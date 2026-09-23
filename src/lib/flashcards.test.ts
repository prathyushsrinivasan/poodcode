import { describe, expect, it } from "vitest";
import { groupBySource, sourceLabel } from "./flashcards";
import type { Flashcard } from "../types";

function card(id: number, source: string): Flashcard {
  return {
    id,
    front: `f${id}`,
    back: `b${id}`,
    source,
    ease: 2.5,
    reps: 0,
    lapses: 0,
    interval_days: 0,
    due_date: "2026-01-01",
    created_at: "2026-01-01",
  };
}

describe("sourceLabel", () => {
  it("names the mastery week a seeded card came from", () => {
    expect(sourceLabel("mastery:typescript:w3")).toBe("TypeScript Mastery · Week 3");
    expect(sourceLabel("mastery:java:w12")).toBe("Java Mastery · Week 12");
  });

  it("falls back to the raw key for an unknown track rather than hiding it", () => {
    expect(sourceLabel("mastery:rust:w1")).toBe("rust Mastery · Week 1");
  });

  it("labels generator-seeded and hand-made cards", () => {
    expect(sourceLabel("seed:tree_traversal")).toBe("Pattern card");
    expect(sourceLabel("manual")).toBe("Your card");
    expect(sourceLabel("")).toBe("Your card");
  });

  it("passes an already human-readable source through", () => {
    expect(sourceLabel("TypeScript Mastery · Week 1 quiz")).toBe("TypeScript Mastery · Week 1 quiz");
  });
});

describe("groupBySource", () => {
  it("groups by label, largest group first, ties alphabetical", () => {
    const groups = groupBySource([
      card(1, "manual"),
      card(2, "mastery:typescript:w1"),
      card(3, "mastery:typescript:w1"),
      card(4, "seed:x"),
      card(5, "seed:y"),
    ]);
    expect(groups.map(([label, cs]) => [label, cs.map((c) => c.id)])).toEqual([
      ["Pattern card", [4, 5]],
      ["TypeScript Mastery · Week 1", [2, 3]],
      ["Your card", [1]],
    ]);
  });
});
