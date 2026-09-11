import { describe, it, expect } from "vitest";
import type { Project, ProjectModule, QuizQuestion } from "../types";
import {
  collectQuestions,
  pickRound,
  poolSummary,
  priority,
  recordAnswer,
  type ReviewHistory,
} from "./projectReview";
import { hashString, optionOrder, seededRandom, shuffleWith } from "./quizShuffle";

const q = (question: string, options = ["right", "wrong 1", "wrong 2", "wrong 3"]): QuizQuestion => ({
  question,
  options,
  answer: 0,
  explanation: "",
});

const mod = (
  number: number,
  key: string,
  steps: { key: string; title: string; warmup?: QuizQuestion[]; quiz?: QuizQuestion[] }[],
  review: QuizQuestion[] = [],
  authored = true
) =>
  ({ number, key, title: `Module ${number}`, phase: "crud", authored, steps, review }) as unknown as ProjectModule;

const proj = (modules: ProjectModule[]) => ({ key: "todo-api", modules }) as unknown as Project;

describe("optionOrder", () => {
  it("is a permutation of every option", () => {
    const order = optionOrder("Why 201 rather than 200?", 4);
    expect([...order].sort()).toEqual([0, 1, 2, 3]);
  });

  it("is stable for the same question, so a page does not reshuffle under you", () => {
    expect(optionOrder("What does JSON.parse return?", 4)).toEqual(
      optionOrder("What does JSON.parse return?", 4)
    );
  });

  it("spreads an always-first answer across every position", () => {
    // The whole reason this exists: authored answers are all index 0. Over a
    // realistic number of questions the answer should land everywhere.
    const where = new Set<number>();
    for (let i = 0; i < 40; i++) where.add(optionOrder(`question ${i}`, 4).indexOf(0));
    expect([...where].sort()).toEqual([0, 1, 2, 3]);
  });

  it("gives a different order under a different salt", () => {
    const orders = new Set(
      ["", "a", "b", "c", "d", "e"].map((salt) => optionOrder("same question", 4, salt).join())
    );
    expect(orders.size).toBeGreaterThan(1);
  });
});

describe("seeded shuffling", () => {
  it("is reproducible from a seed", () => {
    const a = shuffleWith([1, 2, 3, 4, 5, 6], seededRandom(42));
    const b = shuffleWith([1, 2, 3, 4, 5, 6], seededRandom(42));
    expect(a).toEqual(b);
    expect([...a].sort()).toEqual([1, 2, 3, 4, 5, 6]);
  });

  it("hashes strings to unsigned 32-bit integers", () => {
    const h = hashString("todo-api");
    expect(Number.isInteger(h)).toBe(true);
    expect(h).toBeGreaterThanOrEqual(0);
    expect(h).toBeLessThan(2 ** 32);
  });
});

describe("collectQuestions", () => {
  it("gathers warm-ups, step checks and module reviews in the order they are asked", () => {
    const p = proj([
      mod(1, "m1", [{ key: "s1", title: "Step one", warmup: [q("w1")], quiz: [q("c1")] }], [q("r1")]),
      mod(2, "m2", [{ key: "s1", title: "Step one", quiz: [q("c2")] }]),
    ]);
    const got = collectQuestions(p);
    expect(got.map((x) => `${x.question}/${x.source}`)).toEqual([
      "w1/warm-up",
      "c1/check",
      "r1/module review",
      "c2/check",
    ]);
    expect(got[0]).toMatchObject({ moduleKey: "m1", moduleNumber: 1, stepKey: "s1", stepTitle: "Step one" });
    expect(got[2]).toMatchObject({ stepKey: "", stepTitle: "" });
  });

  it("skips modules that are not written yet", () => {
    const p = proj([mod(1, "m1", [{ key: "s", title: "S", quiz: [q("a")] }], [], false)]);
    expect(collectQuestions(p)).toEqual([]);
  });

  it("keeps a word-for-word repeat once, and ids stay stable", () => {
    const p = proj([
      mod(1, "m1", [{ key: "s", title: "S", quiz: [q("same")] }]),
      mod(2, "m2", [], [q("same")]),
    ]);
    const got = collectQuestions(p);
    expect(got).toHaveLength(1);
    expect(got[0]!.moduleKey).toBe("m1");
    expect(collectQuestions(p)[0]!.id).toBe(got[0]!.id);
  });
});

describe("priority and pickRound", () => {
  const pool = collectQuestions(
    proj([mod(1, "m1", [{ key: "s", title: "S", quiz: ["a", "b", "c", "d", "e", "f"].map((t) => q(t)) }])])
  );
  const id = (text: string) => pool.find((x) => x.question === text)!.id;

  it("ranks last-missed, then unseen, then shaky, then solid", () => {
    let h: ReviewHistory = {};
    h = recordAnswer(h, "missed", false);
    h = recordAnswer(h, "shaky", false);
    h = recordAnswer(h, "shaky", true);
    h = recordAnswer(h, "solid", true);
    expect(priority(h["missed"])).toBe(0);
    expect(priority(h["never"])).toBe(1);
    expect(priority(h["shaky"])).toBe(2);
    expect(priority(h["solid"])).toBe(3);
    expect(h["shaky"]).toEqual({ seen: 2, missed: 1, lastRight: true });
  });

  it("always includes what you got wrong last time", () => {
    let h: ReviewHistory = {};
    for (const x of pool) h = recordAnswer(h, x.id, true);
    h = recordAnswer(h, id("e"), false);
    for (let seed = 1; seed < 20; seed++) {
      expect(pickRound(pool, h, 2, seed).map((x) => x.question)).toContain("e");
    }
  });

  it("returns at most the round size, and never more than the pool", () => {
    expect(pickRound(pool, {}, 3, 7)).toHaveLength(3);
    expect(pickRound(pool, {}, 50, 7)).toHaveLength(pool.length);
    expect(new Set(pickRound(pool, {}, 50, 7).map((x) => x.id)).size).toBe(pool.length);
  });

  it("summarises the pool by bucket", () => {
    let h: ReviewHistory = {};
    h = recordAnswer(h, id("a"), false);
    h = recordAnswer(h, id("b"), true);
    expect(poolSummary(pool, h)).toEqual({ missed: 1, fresh: 4, shaky: 0, solid: 1 });
  });
});
