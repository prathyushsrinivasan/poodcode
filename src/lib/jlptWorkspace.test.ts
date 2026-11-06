import { describe, expect, it } from "vitest";
import { AFFIX_PROGRESS_KEY, AFFIX_QUESTIONS } from "../data/jlptAffixes";
import { KANJI_PROGRESS_KEY, KANJI_WORDS } from "../data/kanjiWords";
import { N2_ASSEMBLY_PROGRESS_KEY, N2_ASSEMBLY_QUESTIONS } from "../data/jlptN2SentenceOrder";
import { READING_PASSAGES } from "../data/dokkai";
import { STUDY_QUESTION_MAP, STUDY_QUESTIONS } from "../data/n2Study";
import { emptyReadingProgress, READING_PROGRESS_KEY, recordReadingAnswers } from "./dokkai";
import { conceptProgress, filterReview, JLPT_BACKUP_KEYS, JLPT_CATALOG, newExamples, parseJlptBackup, planPractice, resultsBreakdown, reviewInventory, startPlannedPractice, toggleFlag, type JlptBackup, type MockConfig } from "./jlptWorkspace";
import { emptyStudy, finishSession, parseStudy, questionSection, STUDY_KEY, updateDraft, type StudyReview, type StudyState } from "./n2Study";
import { validJlptSessionField } from "./jlptSessionRecovery";

const at = 1_800_000_000_000;
const q = STUDY_QUESTIONS.find((q) => q.kind === "choice")!;
const review = (patch: Partial<StudyReview> = {}): StudyReview => ({ attempts: 3, correct: 0, stage: 0, due: at - 1, lastAt: at - 1000, lastCorrect: false, lastAssisted: false, lastSlow: true, lastConfidentWrong: true, ...patch });
const config: MockConfig = { vocabulary: 4, grammar: 3, reading: 3, minutes: 15, fresh: true };
function backup(state = emptyStudy()): JlptBackup { return { format: "poodcode-jlpt", version: 1, exportedAt: new Date(at).toISOString(), settings: { [STUDY_KEY]: JSON.stringify(state) }, recovery: {} }; }

describe("additive JLPT state and aggregate review", () => {
  it("loads old study snapshots without changing their revision, reviews or preferences", () => {
    const old = { ...emptyStudy(), revision: 42, reviews: { [q.id]: review() } } as Partial<StudyState>;
    delete old.workspace;
    const loaded = parseStudy(JSON.stringify(old));
    expect(loaded.revision).toBe(42); expect(loaded.reviews).toEqual(old.reviews);
    expect(loaded.workspace).toEqual({ pagePreferences: {}, lists: [], support: { readings: false, translations: false } });
  });
  it("aggregates legacy mistakes and schedules without writing or summing course history", () => {
    const state = emptyStudy(); state.reviews[q.id] = review();
    const settings = { [KANJI_PROGRESS_KEY]: JSON.stringify({ version: 1, words: { [KANJI_WORDS[0].id]: { reading: { attempts: 2, correct: 0, lastCorrect: false }, meaning: { attempts: 1, correct: 1, lastCorrect: true } } } }), [AFFIX_PROGRESS_KEY]: JSON.stringify({ [AFFIX_QUESTIONS[0].id]: { attempts: 1, correct: 0, lastCorrect: false } }) };
    const before = JSON.stringify({ state, settings });
    const due = filterReview(reviewInventory(state, settings, at), "due");
    expect(due.map((i) => i.source)).toEqual(expect.arrayContaining(["Guided", "Word Builder", "Affixes"]));
    expect(due).toHaveLength(3);
    expect(JSON.stringify({ state, settings })).toBe(before);
  });
  it("counts an assembly exercise once when both course stores contain it", () => {
    const id = N2_ASSEMBLY_QUESTIONS[0].id;
    const state = emptyStudy(); state.reviews[`assembly-${id}`] = review(); state.bookmarks = [`order:${id}`];
    const items = reviewInventory(state, { [N2_ASSEMBLY_PROGRESS_KEY]: JSON.stringify({ [id]: { attempts: 8, correct: 5, lastCorrect: false } }) }, at);
    expect(items.filter((i) => i.id === `assembly-${id}`)).toHaveLength(1);
    expect(items.some((i) => i.id === `order:${id}`)).toBe(false);
    expect(items.find((i) => i.id === `assembly-${id}`)).toMatchObject({ due: true, saved: true, nativePending: true, mistakes: 3 });
  });
  it("keeps a newer native mistake actionable when the guided copy is correct", () => {
    const p = READING_PASSAGES[0]; const native = p.questions[0];
    const state = emptyStudy(); state.reviews[`study-${native.id}`] = review({ lastCorrect: true, lastSlow: false, due: at + 100_000 });
    const reading = recordReadingAnswers(emptyReadingProgress(), [{ id: native.id, correct: false, mode: "independent" }], at);
    const item = reviewInventory(state, { [READING_PROGRESS_KEY]: JSON.stringify(reading) }, at).find((i) => i.id === `study-${native.id}`);
    expect(item).toMatchObject({ due: true, nativePending: true, href: `/japanese/n2/reading/${p.kind}/${p.id}` });
  });
  it("filters the notebook by reason, confident misses, slow answers and persistent trouble", () => {
    const state = emptyStudy(); state.reviews[q.id] = review(); state.bookmarks = [q.id]; state.notes[q.id] = { text: "Check the clause", reason: "Grammar connection" };
    state.attempts = Array.from({ length: 3 }, (_, i) => ({ id: `miss-${i}`, questionId: q.id, at, correct: false, answer: "", confidence: "sure", assisted: false, elapsedMs: 100_000, mode: "learn", revealed: false }));
    const items = reviewInventory(state, {}, at);
    for (const filter of ["saved", "reason", "confident", "slow", "trouble"] as const) expect(filterReview(items, filter, "Grammar connection").map((i) => i.id)).toContain(q.id);
    expect(filterReview(items, "reason", "Careless slip")).toHaveLength(0);
    state.reviews[q.id] = review({ lastCorrect: true, lastAssisted: false });
    expect(filterReview(reviewInventory(state, {}, at), "trouble")).toHaveLength(0);
  });
  it("preserves personal lists and rejects malformed workspace data", () => {
    const state = emptyStudy(); state.workspace.lists = [{ id: "work", name: "Workplace", items: [q.id, q.id] }];
    expect(parseStudy(JSON.stringify(state)).workspace.lists[0].items).toEqual([q.id]);
    expect(() => parseStudy(JSON.stringify({ ...state, workspace: { ...state.workspace, support: { readings: "yes" } } }))).toThrow();
  });
});
describe("daily rounds, diagnostic and written mocks", () => {
  it("samples all six skill sections in a short diagnostic and daily mix", () => {
    const state = emptyStudy();
    const diagnostic = planPractice(state, "diagnostic", config, new Set(), 1);
    expect(diagnostic).toHaveLength(12); expect(new Set(diagnostic).size).toBe(12);
    expect(new Set(diagnostic.map((id) => questionSection(STUDY_QUESTION_MAP.get(id)!))).size).toBe(6);
    state.preferences.roundSize = 10;
    const daily = planPractice(state, "daily", config, new Set(), 1);
    expect(daily).toHaveLength(10); expect(new Set(daily.map((id) => questionSection(STUDY_QUESTION_MAP.get(id)!))).size).toBe(6);
  });
  it("selects new examples of missed concepts without repeating the missed question", () => {
    const state = emptyStudy(); state.reviews[q.id] = review();
    const ids = newExamples(state, [q.id], 5);
    expect(ids.length).toBeGreaterThan(0); expect(ids).not.toContain(q.id);
    for (const id of ids) expect(STUDY_QUESTION_MAP.get(id)?.lessonId).toBe(q.lessonId);
    expect(planPractice(emptyStudy(), "weak", config)).toEqual([]);
    expect(planPractice(state, "weak", config, new Set(), 2).every((id) => STUDY_QUESTION_MAP.get(id)!.lessonId === q.lessonId)).toBe(true);
  });
  it("uses only written choice and assembly questions, honoring fresh history in both stores", () => {
    const state = emptyStudy();
    const first = planPractice(state, "mini", config, new Set(), 42);
    expect(first).toHaveLength(10); expect(new Set(first).size).toBe(10);
    expect(first.every((id) => STUDY_QUESTION_MAP.get(id)!.kind !== "typed")).toBe(true);
    const fresh = planPractice(state, "mini", config, new Set(first), 42);
    expect(fresh.every((id) => !first.includes(id))).toBe(true);
    expect(planPractice(state, "mini", { ...config, fresh: false }, new Set(first), 42)).toEqual(first);
  });
  it("runs a configurable mock longer than a short round with a persisted custom deadline", () => {
    const ids = planPractice(emptyStudy(), "written", { ...config, vocabulary: 25, grammar: 25, reading: 20 });
    const state = startPlannedPractice(emptyStudy(), ids, "written", 105, at);
    expect(state.session!.questionIds).toHaveLength(70); expect(state.session!.deadline).toBe(at + 105 * 60_000);
    const flagged = toggleFlag(state, ids[1]);
    expect(parseStudy(JSON.stringify(flagged)).session?.flags).toEqual([ids[1]]);
    expect(toggleFlag(flagged, ids[1]).session?.flags).toEqual([]);
    expect(startPlannedPractice(flagged, [q.id], "daily", 5, at)).toBe(flagged);
    expect(() => parseStudy(JSON.stringify({ ...state, session: { ...state.session, flags: ["unknown"] } }))).toThrow();
  });
  it("retains confidence and pacing data while grading an expired mock once", () => {
    const ids = planPractice(emptyStudy(), "mini", config, new Set(), 2);
    let state = startPlannedPractice(emptyStudy(), ids, "mini", 15, at);
    const first = STUDY_QUESTION_MAP.get(ids[0])!;
    state = updateDraft(state, { answer: first.kind === "choice" ? String((first.answer + 1) % 4) : "0,1,2,3", confidence: "sure" }, at + 200_000);
    state = finishSession(state, at + 15 * 60_000);
    expect(state.session?.expired).toBe(true); expect(state.attempts).toHaveLength(ids.length);
    const rows = resultsBreakdown(state.session!);
    expect(rows.reduce((n, r) => n + r.total - r.answered, 0)).toBe(9);
    expect(rows.reduce((n, r) => n + r.confidentWrong, 0)).toBe(1);
    expect(rows.reduce((n, r) => n + r.slow, 0)).toBe(1);
    expect(finishSession(state, at + 20 * 60_000)).toBe(state);
    expect(conceptProgress(state).reduce((n, c) => n + c.attempts, 0)).toBe(10);
  });
});
describe("JLPT backup and recovery validation", () => {
  it("round-trips all course stores and preserves unrelated settings outside the backup", () => {
    const p = backup();
    for (const key of JLPT_BACKUP_KEYS) if (key !== STUDY_KEY) p.settings[key] = JSON.stringify(key === KANJI_PROGRESS_KEY ? { version: 1, words: {} } : key === READING_PROGRESS_KEY ? emptyReadingProgress() : {});
    expect(parseJlptBackup(JSON.stringify(p))).toEqual(p);
    expect(() => parseJlptBackup(JSON.stringify({ ...p, settings: { ...p.settings, theme: "light" } }))).toThrow("Unexpected backup setting");
  });
  it("rejects future snapshots and damaged legacy data before importing anything", () => {
    const p = backup(); p.settings[AFFIX_PROGRESS_KEY] = '{"unknown":{"attempts":5,"correct":99,"lastCorrect":true}}';
    expect(() => parseJlptBackup(JSON.stringify(p))).toThrow("Invalid or unavailable");
    delete p.settings[AFFIX_PROGRESS_KEY]; p.settings[STUDY_KEY] = '{"version":99}';
    expect(() => parseJlptBackup(JSON.stringify(p))).toThrow();
  });
  it("accepts native drafts but rejects altered exercises in a recovery backup", () => {
    const p = backup();
    const key = "jlpt-session:/japanese/n2/affixes/mixed:round";
    p.recovery[key] = JSON.stringify([AFFIX_QUESTIONS[0]]);
    p.recovery["jlpt-session:/japanese/n2/affixes/mixed:result"] = JSON.stringify("incorrect");
    expect(parseJlptBackup(JSON.stringify(p))).toEqual(p);
    p.recovery[key] = JSON.stringify([{ ...AFFIX_QUESTIONS[0], answer: "tampered" }]);
    expect(() => parseJlptBackup(JSON.stringify(p))).toThrow("Invalid session recovery");
    expect(validJlptSessionField("jlpt-session:/japanese/n2/reading/short/test?mode=timed:deadline", at)).toBe(true);
    expect(validJlptSessionField("jlpt-session:/japanese/n2/reading/short/test:index", -1)).toBe(false);
  });
  it("keeps stable catalog IDs unique across courses", () => {
    expect(new Set(JLPT_CATALOG.map((i) => i.id)).size).toBe(JLPT_CATALOG.length);
    expect(JLPT_CATALOG.every((i) => i.href.startsWith("/japanese/n2/"))).toBe(true);
  });
});
