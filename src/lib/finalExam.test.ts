import { describe, expect, it } from "vitest";
import type { MasteryFinalExam, MasteryWeek, QuizQuestion } from "../types";
import {
  drawFinalPaper,
  headlineAttempt,
  parseFinalExamState,
  scoreSitting,
  type FinalAttempt,
} from "./finalExam";

function q(text: string): QuizQuestion {
  return { question: text, options: ["right", "w1", "w2", "w3"], answer: 0, explanation: "" };
}

function week(n: number, count: number): MasteryWeek {
  return {
    week: n,
    phase: "",
    title: `W${n}`,
    goal: "",
    concepts: [],
    problems: [],
    project: "",
    quiz: Array.from({ length: count }, (_, i) => q(`w${n}q${i}`)),
    quiz_sample: 4,
    exam: null,
    contest: null,
  };
}

describe("drawFinalPaper", () => {
  const weeks = [week(1, 5), week(2, 5), week(3, 1)];

  it("represents every week before any week gives a second question", () => {
    const paper = drawFinalPaper(weeks, 3, 42);
    const fromWeek = paper.map((p) => p.question.slice(0, 2)).sort();
    expect(fromWeek).toEqual(["w1", "w2", "w3"]);
  });

  it("is deterministic for a seed and keeps the right answer marked", () => {
    const a = drawFinalPaper(weeks, 8, 7);
    const b = drawFinalPaper(weeks, 8, 7);
    expect(a).toEqual(b);
    for (const p of a) expect(p.options[p.answer]).toBe("right");
  });

  it("stops when the banks run out", () => {
    expect(drawFinalPaper(weeks, 100, 1)).toHaveLength(11);
  });
});

describe("scoreSitting", () => {
  const exam = {
    pass_mark: 70,
    min_problems: 1,
    min_types: 1,
    problems: [{ id: "p1" }, { id: "p2" }],
    type_section: [{ id: "t1" }],
  } as unknown as MasteryFinalExam;
  const paper = drawFinalPaper([week(1, 4)], 4, 3);
  const allRight = paper.map((p) => p.answer);

  it("passes with enough of each part", () => {
    const s = scoreSitting(exam, paper, { seed: 3, startedAt: "", picked: allRight, solved: ["p2", "t1"] });
    expect(s).toEqual({ quizPercent: 100, problems: 1, types: 1, passed: true });
  });

  it("fails when one part is short", () => {
    const s = scoreSitting(exam, paper, { seed: 3, startedAt: "", picked: allRight, solved: ["p1", "p2"] });
    expect(s.passed).toBe(false);
    expect(s.types).toBe(0);
  });

  it("counts unanswered questions as wrong", () => {
    const s = scoreSitting(exam, paper, { seed: 3, startedAt: "", picked: [-1, -1, -1, -1], solved: [] });
    expect(s.quizPercent).toBe(0);
  });
});

describe("parseFinalExamState", () => {
  it("defaults on missing or bad input", () => {
    expect(parseFinalExamState(undefined)).toEqual({ sitting: null, attempts: [] });
    expect(parseFinalExamState("nope")).toEqual({ sitting: null, attempts: [] });
  });

  it("round-trips a sitting and attempts", () => {
    const state = {
      sitting: { seed: 9, startedAt: "2026-09-27T10:00:00Z", picked: [0, -1], solved: ["p1"] },
      attempts: [{ date: "d", seconds: 60, quizPercent: 80, problems: 3, types: 4, passed: true }],
    };
    expect(parseFinalExamState(JSON.stringify(state))).toEqual(state);
  });
});

describe("headlineAttempt", () => {
  const a = (quizPercent: number, problems: number, passed: boolean): FinalAttempt => ({
    date: "",
    seconds: 0,
    quizPercent,
    problems,
    types: 0,
    passed,
  });

  it("prefers the first pass", () => {
    expect(headlineAttempt([a(50, 1, false), a(71, 3, true), a(99, 5, true)])?.quizPercent).toBe(71);
  });

  it("otherwise the best try, and null before any", () => {
    expect(headlineAttempt([a(50, 1, false), a(60, 2, false)])?.quizPercent).toBe(60);
    expect(headlineAttempt([])).toBeNull();
  });
});
