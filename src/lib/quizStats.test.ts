import { beforeEach, describe, expect, it } from "vitest";
import { flaggedQuestions, quizStats, recordSitting } from "./quizStats";

beforeEach(() => {
  const store = new Map<string, string>();
  (globalThis as { localStorage?: unknown }).localStorage = {
    getItem: (k: string) => store.get(k) ?? null,
    setItem: (k: string, v: string) => void store.set(k, v),
  };
});

describe("quiz stats", () => {
  it("accumulates sittings and flags both ends", () => {
    for (let i = 0; i < 3; i++) recordSitting([{ question: "easy", right: true }, { question: "hard", right: false }]);
    recordSitting([{ question: "hard", right: true }]);
    expect(quizStats()["hard"]).toEqual({ right: 1, wrong: 3 });
    const f = flaggedQuestions(quizStats());
    expect(f.missed.map((r) => r.question)).toEqual(["hard"]);
    expect(f.tooEasy.map((r) => r.question)).toEqual(["easy"]);
  });
});
