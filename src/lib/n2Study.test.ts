import { describe, expect, it } from "vitest";
import { STUDY_LESSONS, STUDY_QUESTION_MAP, STUDY_QUESTIONS, STUDY_SECTIONS } from "../data/n2Study";
import { answerCorrect, beginQuestions, checkAnswer, dailyStats, DAY, daysToExam, emptyStudy, finishSession, moveQuestion, parseStudy, pauseSession, questionSection, reviewQuestions, sectionStats, selectRound, startSession, updateDraft, validExamDate, type Confidence, type StudyState } from "./n2Study";

const at = new Date(2026, 9, 25, 12).getTime();
const typed = STUDY_QUESTIONS.find((q) => q.kind === "typed")!;
const choice = STUDY_QUESTIONS.find((q) => q.kind === "choice")!;
function correct(id: string) {
  const q = STUDY_QUESTION_MAP.get(id)!;
  return q.kind === "typed" ? q.answers[0] : q.kind === "choice" ? String(q.answer) : q.order.join(",");
}
function round(state = emptyStudy(), ids = [typed.id], now = at, mode: "learn" | "timed" = "learn", id = `s-${now}`) {
  return beginQuestions(startSession({ ...state, session: null }, ids, mode, "Test round", now, id), now);
}
function recall(state: StudyState, now: number, answer = correct(typed.id), confidence: Confidence = "sure", assisted = false) {
  return checkAnswer(updateDraft(round(state, [typed.id], now), { answer, confidence, assisted }, now + 1000), now + 2000);
}
describe("N2 sample bank integrity", () => {
  it("covers all six sections and all vocabulary and reading formats", () => {
    for (const section of STUDY_SECTIONS) expect(STUDY_QUESTIONS.some((q) => questionSection(q) === section.id)).toBe(true);
    for (const id of ["word-formation", "context", "paraphrase", "usage", "reading-short", "reading-medium", "reading-ab", "reading-long", "reading-information"]) expect(STUDY_QUESTIONS.some((q) => q.lessonId === id)).toBe(true);
  });
  it("has unique stable IDs, valid connections, and no explanation or evidence gaps", () => {
    expect(new Set(STUDY_LESSONS.map((l) => l.id)).size).toBe(STUDY_LESSONS.length);
    expect(new Set(STUDY_QUESTIONS.map((q) => q.id)).size).toBe(STUDY_QUESTIONS.length);
    for (const q of STUDY_QUESTIONS) {
      expect(STUDY_LESSONS.some((l) => l.id === q.lessonId)).toBe(true);
      expect(q.explanation.length).toBeGreaterThan(25); expect(q.hint.length).toBeGreaterThan(10);
      expect(q.targetSeconds).toBeGreaterThan(0);
      expect(answerCorrect(q, correct(q.id))).toBe(true);
      for (const quote of q.evidence ?? []) expect(q.texts?.some((t) => t.text.includes(quote))).toBe(true);
      if (q.kind === "choice") {
        expect(q.choices).toHaveLength(4); expect(new Set(q.choices.map((c) => c.text)).size).toBe(4);
        expect(q.answer).toBeGreaterThanOrEqual(0); expect(q.answer).toBeLessThan(4);
        for (const option of q.choices) expect(option.why.length).toBeGreaterThan(12);
      } else if (q.kind === "assembly") {
        expect([...q.order].sort()).toEqual([0, 1, 2, 3]); expect(q.starIndex).toBeLessThan(4);
        for (const order of q.acceptedOrders ?? []) { expect([...order].sort()).toEqual([0, 1, 2, 3]); expect(answerCorrect(q, order.join(","))).toBe(true); }
      } else for (const answer of q.answers) expect(answer).toMatch(/^[\p{Script=Hiragana}ー]+$/u);
    }
  });
  it("normalizes typing without accepting romaji, katakana or missing long vowels", () => {
    expect(answerCorrect(typed, ` ${correct(typed.id)} `)).toBe(true);
    expect(answerCorrect(typed, "seisan")).toBe(false); expect(answerCorrect(typed, "セイサン")).toBe(false);
    expect(answerCorrect(typed, "せさん")).toBe(false);
    expect(answerCorrect(choice, "")).toBe(false);
  });
  it("accepts explicitly authored alternative assembly orders, but not arbitrary permutations", () => {
    const q = STUDY_QUESTIONS.find((item) => item.kind === "assembly" && item.acceptedOrders?.length)!;
    if (q.kind !== "assembly") throw new Error("Missing alternate-order sample");
    expect(answerCorrect(q, q.acceptedOrders![0].join(","))).toBe(true);
    expect(answerCorrect(q, "0,0,0,0")).toBe(false);
    expect(answerCorrect(q, [...q.order].reverse().join(","))).toBe(false);
  });
});
describe("learning, grading and spaced recall", () => {
  it("does not count lesson reading or a draft as a completed answer", () => {
    const p = updateDraft(round(), { answer: correct(typed.id) }, at + 1000);
    expect(p.attempts).toHaveLength(0); expect(p.learned).toContain(typed.lessonId);
  });
  it("atomically records one attempt, result and tomorrow's review, despite repeated submission", () => {
    const p = recall(emptyStudy(), at);
    expect(p.attempts).toHaveLength(1); expect(p.session!.results[typed.id].correct).toBe(true);
    expect(p.reviews[typed.id]).toMatchObject({ attempts: 1, correct: 1, stage: 1, due: at + 2000 + DAY });
    expect(checkAnswer(p, at + 3000)).toBe(p);
  });
  it("advances spaced recalls through 1, 3 and 7 days; early repeats do not inflate retention", () => {
    let p = recall(emptyStudy(), at); const due = p.reviews[typed.id].due;
    p = recall(p, at + 10_000); expect(p.reviews[typed.id].stage).toBe(1); expect(p.reviews[typed.id].due).toBe(due);
    p = recall(p, due); expect(p.reviews[typed.id].stage).toBe(2); expect(p.reviews[typed.id].due).toBe(due + 2000 + 3 * DAY);
    const due2 = p.reviews[typed.id].due; p = recall(p, due2);
    expect(p.reviews[typed.id]).toMatchObject({ stage: 3, due: due2 + 2000 + 7 * DAY });
    expect(sectionStats(p, "kanji").retained).toBe(1);
  });
  it.each(["guess", "assisted", "miss"])("returns %s to a short interval", (condition) => {
    let p = recall(emptyStudy(), at); const due = p.reviews[typed.id].due;
    p = recall(p, due, condition === "miss" ? "wrong" : correct(typed.id), condition === "guess" ? "guess" : "sure", condition === "assisted");
    expect(p.reviews[typed.id].stage).toBe(0); expect(p.reviews[typed.id].due).toBe(due + 2000 + DAY);
  });
  it("revealed and assisted answers appear in mistake review and do not count as independent correct", () => {
    let p = updateDraft(round(), { answer: correct(typed.id), assisted: true }, at + 1000);
    p = checkAnswer(p, at + 2000); expect(p.reviews[typed.id].correct).toBe(0);
    expect(reviewQuestions(p, "mistakes").map((q) => q.id)).toContain(typed.id);
    p = checkAnswer(round(), at + 1000, true);
    expect(p.attempts[0]).toMatchObject({ correct: false, revealed: true, assisted: true });
  });
  it("does not allow a revealed hint to be undone", () => {
    const p = updateDraft(updateDraft(round(), { assisted: true }, at), { assisted: false }, at + 1000);
    expect(p.session!.drafts[typed.id].assisted).toBe(true);
  });
  it("tracks confident misses and slow answers separately", () => {
    let p = updateDraft(round(), { answer: "wrong", confidence: "sure" }, at + 1000);
    p = checkAnswer(p, at + (typed.targetSeconds + 1) * 1000);
    expect(reviewQuestions(p, "confident").map((q) => q.id)).toEqual([typed.id]);
    expect(reviewQuestions(p, "slow").map((q) => q.id)).toEqual([typed.id]);
    expect(reviewQuestions(p, "due", at)).toHaveLength(0);
    expect(reviewQuestions(p, "due", p.reviews[typed.id].due)).toHaveLength(1);
  });
  it("pauses guided time without charging the break to the next answer", () => {
    let p = pauseSession(round(), true, at + 2000);
    p = pauseSession(p, false, at + DAY);
    p = updateDraft(p, { answer: correct(typed.id) }, at + DAY + 1000);
    p = checkAnswer(p, at + DAY + 2000);
    expect(p.attempts[0].elapsedMs).toBe(4000);
  });
  it("keeps the round frozen after a mistake is corrected", () => {
    let p = round(emptyStudy(), [typed.id, choice.id]);
    p = checkAnswer(updateDraft(p, { answer: correct(typed.id) }, at), at + 1000);
    p = moveQuestion(p, 1, at + 2000);
    expect(p.session!.questionIds).toEqual([typed.id, choice.id]); expect(p.session!.position).toBe(1);
  });
  it("does not replace an unfinished round", () => {
    const p = round(); expect(startSession(p, [choice.id], "timed", "Other", at)).toBe(p);
  });
  it("finishes guided practice without manufacturing mistakes for unseen questions", () => {
    let p = round(emptyStudy(), [typed.id, choice.id]);
    p = checkAnswer(updateDraft(p, { answer: correct(typed.id) }, at), at + 1000);
    p = finishSession(p, at + 2000);
    expect(p.attempts).toHaveLength(1); expect(p.reviews[choice.id]).toBeUndefined();
    expect(p.session!.questionIds).toEqual([typed.id]); expect(parseStudy(JSON.stringify(p))).toEqual(p);
    expect(finishSession(round(), at + 1000).session).toBeNull();
  });
});
describe("timed rounds and restart recovery", () => {
  it("allows changing and skipping answers, then grades once at the end", () => {
    let p = round(emptyStudy(), [typed.id, choice.id], at, "timed");
    p = updateDraft(p, { answer: "wrong" }, at + 1000); p = updateDraft(p, { answer: correct(typed.id) }, at + 2000);
    p = moveQuestion(p, 1, at + 3000); expect(p.attempts).toHaveLength(0);
    p = finishSession(p, at + 4000); expect(p.attempts).toHaveLength(2);
    expect(p.attempts.map((a) => a.correct)).toEqual([true, false]); expect(p.session!.phase).toBe("summary");
    expect(finishSession(p, at + 5000)).toBe(p);
  });
  it("preserves a fixed deadline across saves, reloads and navigation; refuses late edits", () => {
    let p = round(emptyStudy(), [typed.id, choice.id], at, "timed");
    const deadline = p.session!.deadline!;
    p = updateDraft(p, { answer: correct(typed.id) }, deadline - 1000);
    p = parseStudy(JSON.stringify(p)); expect(p.session!.deadline).toBe(deadline);
    expect(pauseSession(p, true)).toBe(p); expect(updateDraft(p, { answer: "late" }, deadline)).toBe(p);
    p = moveQuestion(p, 1, deadline + 1000);
    expect(p.session!.expired).toBe(true); expect(p.attempts).toHaveLength(2);
    expect(p.attempts[0].elapsedMs).toBe(deadline - at);
  });
  it("never reveals a timed answer through the guided grading action", () => {
    const p = round(emptyStudy(), [typed.id], at, "timed"); expect(checkAnswer(p, at + 1000, true)).toBe(p);
  });
  it("round-trips notes, confidence, results and learned lessons", () => {
    const p = recall(emptyStudy(), at); p.notes[typed.id] = { text: "Watch the long vowel", reason: "Unknown word" }; p.bookmarks = [typed.id];
    expect(parseStudy(JSON.stringify(p))).toEqual(p);
  });
  it.each(["{", '{"version":99}', '{"version":1}', '[]'])("rejects unreadable snapshots instead of silently resetting: %s", (raw) => expect(() => parseStudy(raw)).toThrow());
  it("rejects broken counters, invalid session positions and damaged drafts", () => {
    const p = recall(emptyStudy(), at);
    expect(() => parseStudy(JSON.stringify({ ...p, reviews: { [typed.id]: { ...p.reviews[typed.id], stage: 5 } } }))).toThrow();
    expect(() => parseStudy(JSON.stringify({ ...p, session: { ...p.session, position: 99 } }))).toThrow();
    expect(() => parseStudy(JSON.stringify({ ...p, session: { ...p.session, drafts: { [typed.id]: { answer: "x" } } } }))).toThrow();
  });
});
describe("selection, calendar and honest progress", () => {
  it("uses local calendar days for countdowns and rejects impossible dates", () => {
    expect(daysToExam("2026-12-06", at)).toBe(42); expect(daysToExam("", at)).toBeNull();
    expect(validExamDate("2026-02-30")).toBe(false); expect(validExamDate("2028-02-29")).toBe(true);
  });
  it("prioritizes due items and interleaves sections without duplicates", () => {
    const p = recall(emptyStudy(), at);
    const ids = selectRound(p, STUDY_QUESTIONS, 10, p.reviews[typed.id].due);
    expect(ids[0]).toBe(typed.id); expect(new Set(ids).size).toBe(10);
    expect(questionSection(STUDY_QUESTION_MAP.get(ids[0])!)).not.toBe(questionSection(STUDY_QUESTION_MAP.get(ids[1])!));
  });
  it("counts unique daily questions separately from attempts", () => {
    let p = recall(emptyStudy(), at); p = recall(p, at + 10_000);
    expect(dailyStats(p, at)).toMatchObject({ unique: 1, attempts: 2, streak: 1 });
  });
  it("gives every section a turn before repeating one in an unseen mixed round", () => {
    const ids = selectRound(emptyStudy(), STUDY_QUESTIONS, 6, at);
    expect(new Set(ids.map((id) => questionSection(STUDY_QUESTION_MAP.get(id)!))).size).toBe(6);
    const vocabulary = STUDY_QUESTIONS.filter((q) => questionSection(q) === "vocabulary");
    const formats = selectRound(emptyStudy(), vocabulary, 4, at).map((id) => STUDY_QUESTION_MAP.get(id)!.lessonId);
    expect(new Set(formats).size).toBe(4);
  });
});
