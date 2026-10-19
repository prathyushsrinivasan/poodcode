import { describe, expect, it } from "vitest";
import { N2_LESSONS, N2_QUESTIONS } from "../data/jlptN2";
import { isN2Answer, n2ResumeIndex, n2ReviewQuestions, n2Stats, normalizeN2Answer,
  parseN2Progress, recordN2Answer } from "./jlptN2";

describe("N2 course content", () => {
  it("provides 60 single-kanji and 60 contextual questions in stable families", () => {
    expect(N2_LESSONS).toHaveLength(24);
    expect(N2_QUESTIONS).toHaveLength(120);
    expect(new Set(N2_QUESTIONS.map((q) => q.id)).size).toBe(120);
    for (const kind of ["kanji", "vocabulary"]) {
      expect(N2_LESSONS.filter((l) => l.kind === kind).flatMap((l) => l.questions)).toHaveLength(60);
    }
    for (const lesson of N2_LESSONS) {
      expect(lesson.questions).toHaveLength(5);
      expect(lesson.rule.length).toBeGreaterThan(30);
      expect(lesson.boundary.length).toBeGreaterThan(30);
      for (const q of lesson.questions) {
        expect(q.sentence.split("___")).toHaveLength(2);
        expect(q.explanation.length).toBeGreaterThan(50);
        expect(q.translation.length).toBeGreaterThan(15);
        expect(q.reading).toMatch(/^[ぁ-ゖー]+$/u);
        expect(isN2Answer(q, q.answer)).toBe(true);
        if (lesson.kind === "kanji") {
          for (const answer of [q.answer, ...q.accepted]) expect(answer).toMatch(/^\p{Script=Han}$/u);
        }
      }
    }
  });
  it("covers the user's system, size, decision, former career, scheduling and topic examples", () => {
    expect(N2_QUESTIONS.find((q) => q.sentence.includes("大統領"))?.answer).toBe("制");
    const size = N2_QUESTIONS.find((q) => q.word === "卵大")!;
    expect(isN2Answer(size, "大")).toBe(true);
    expect(isN2Answer(size, "形")).toBe(true);
    expect(isN2Answer(size, "卵大")).toBe(false);
    for (const word of ["判断する", "もともと", "日程の調整", "話がそれる"]) {
      expect(N2_QUESTIONS.some((q) => q.word === word)).toBe(true);
    }
  });
});

describe("N2 answer matching", () => {
  it("accepts explicitly taught alternatives and kana without accepting wrong forms", () => {
    const q = N2_QUESTIONS.find((q) => q.id === "b01-1")!;
    expect(isN2Answer(q, " はんだん　")).toBe(true);
    expect(isN2Answer(q, "決定")).toBe(true);
    expect(isN2Answer(q, "判断する")).toBe(false);
    expect(isN2Answer(q, "")).toBe(false);
    expect(normalizeN2Answer("ｳﾛｳﾛ")).toBe("ウロウロ");
    const stem = N2_QUESTIONS.find((q) => q.id === "b12-4")!;
    expect(isN2Answer(stem, "つけ")).toBe(true);
    expect(isN2Answer(stem, "つける")).toBe(false);
  });
});

describe("N2 progress", () => {
  const questions = N2_LESSONS[0].questions;
  it("keeps mistakes until a later successful attempt and never counts a reveal as a solve", () => {
    const missed = recordN2Answer({}, questions[0].id, false);
    expect(n2Stats(questions, missed)).toEqual({ total: 5, attempted: 1, correct: 0, missed: 1 });
    expect(n2ReviewQuestions(missed).map((q) => q.id)).toEqual([questions[0].id]);
    const corrected = recordN2Answer(missed, questions[0].id, true);
    expect(corrected[questions[0].id]).toEqual({ attempts: 2, correct: 1, lastCorrect: true });
    expect(n2ReviewQuestions(corrected)).toEqual([]);
    expect(missed[questions[0].id].lastCorrect).toBe(false);
  });
  it("resumes unanswered questions before mistakes, then supports replay", () => {
    let p = recordN2Answer({}, questions[0].id, false);
    expect(n2ResumeIndex(questions, p)).toBe(1);
    for (const q of questions.slice(1)) p = recordN2Answer(p, q.id, true);
    expect(n2ResumeIndex(questions, p)).toBe(0);
    p = recordN2Answer(p, questions[0].id, true);
    expect(n2ResumeIndex(questions, p)).toBe(0);
  });
  it("safely loads backups, rejects malformed rows, and round-trips valid history", () => {
    for (const raw of [undefined, "broken", "null", "[]", "42"]) expect(parseN2Progress(raw)).toEqual({});
    const good = recordN2Answer({}, questions[0].id, true);
    expect(parseN2Progress(JSON.stringify(good))).toEqual(good);
    const bad = { attempts: 1, correct: 2, lastCorrect: true };
    expect(parseN2Progress(JSON.stringify({ [questions[0].id]: bad, unknown: good[questions[0].id] }))).toEqual({});
  });
});
