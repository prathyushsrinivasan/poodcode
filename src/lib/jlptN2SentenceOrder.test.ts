import { describe, expect, it } from "vitest";
import { N2_ASSEMBLY_LESSONS, N2_ASSEMBLY_QUESTIONS, N2_ASSEMBLY_PROGRESS_KEY,
  assemblyAnswer, assemblySentence } from "../data/jlptN2SentenceOrder";
import { N2_PROGRESS_KEY, n2ResumeIndex, n2Stats, parseN2Progress, recordN2Answer } from "./jlptN2";

describe("N2 sentence assembly content", () => {
  it("provides the five supplied examples and 120 distinct original questions with complete solutions", () => {
    expect(N2_ASSEMBLY_LESSONS).toHaveLength(25);
    expect(N2_ASSEMBLY_QUESTIONS).toHaveLength(125);
    expect(new Set(N2_ASSEMBLY_QUESTIONS.map((q) => q.id)).size).toBe(125);
    expect(new Set(N2_ASSEMBLY_QUESTIONS.map(assemblySentence)).size).toBe(125);
    for (const lesson of N2_ASSEMBLY_LESSONS) {
      expect(lesson.questions).toHaveLength(5);
      expect(lesson.strategy.length).toBeGreaterThan(60);
      for (const q of lesson.questions) {
        expect(q.choices).toHaveLength(4);
        expect(new Set(q.choices).size).toBe(4);
        expect([...q.order].sort()).toEqual([1, 2, 3, 4]);
        expect(q.starIndex).toBeGreaterThanOrEqual(0);
        expect(q.starIndex).toBeLessThan(4);
        expect(q.before.length).toBeGreaterThan(0);
        expect(q.after.length).toBeGreaterThan(0);
        expect(q.translation.length).toBeGreaterThan(25);
        expect(q.explanation.length).toBeGreaterThan(100);
        expect(assemblySentence(q)).not.toMatch(/___|undefined|�/u);
        expect(q.choices.every((c) => c.trim().length > 0)).toBe(true);
      }
    }
    // Every choice number appears at the star; never train a fixed answer number.
    const answers = N2_ASSEMBLY_QUESTIONS.slice(5).map(assemblyAnswer);
    for (const n of [1, 2, 3, 4]) expect(answers.filter((answer) => answer === n)).toHaveLength(30);
  });

  it("preserves the user's choice numbering and reconstructs the five examples", () => {
    const examples = N2_ASSEMBLY_LESSONS[0].questions;
    expect(examples.map(assemblyAnswer)).toEqual([2, 3, 2, 1, 4]);
    expect(examples.map((q) => q.order)).toEqual([[1, 3, 2, 4], [4, 1, 3, 2], [1, 4, 2, 3], [3, 4, 1, 2], [2, 1, 4, 3]]);
    expect(assemblySentence(examples[0])).toContain("汗をかくと体温が下がるのもその性質によるものです。");
    expect(assemblySentence(examples[2])).toContain("会議室に入っていったきり一度も出てこないまま2時間がたとうとしている。");
    expect(assemblySentence(examples[4])).toContain("着るかもしれないと思って捨てられずにいる古い服が");
  });
});

describe("separate assembly progress", () => {
  it("round-trips assembly answers without mixing old blank-course history", () => {
    expect(N2_ASSEMBLY_PROGRESS_KEY).not.toBe(N2_PROGRESS_KEY);
    let p = recordN2Answer({}, "examples-13", false);
    p = recordN2Answer(p, "a01-1", true);
    const loaded = parseN2Progress(JSON.stringify(p), N2_ASSEMBLY_QUESTIONS);
    expect(Object.keys(loaded)).toEqual(["examples-13"]);
    expect(Object.keys(parseN2Progress(JSON.stringify(p)))).toEqual(["a01-1"]);
    expect(n2Stats(N2_ASSEMBLY_QUESTIONS, loaded)).toEqual({ total: 125, attempted: 1, correct: 0, missed: 1 });
    const corrected = recordN2Answer(loaded, "examples-13", true);
    expect(corrected["examples-13"]).toEqual({ attempts: 2, correct: 1, lastCorrect: true });
    expect(n2ResumeIndex(N2_ASSEMBLY_LESSONS[0].questions, corrected)).toBe(1);
  });
});
