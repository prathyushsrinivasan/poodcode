import { describe, expect, it } from "vitest";
import { applyFilter, emptyFilter } from "./filters";
import type { Problem } from "../types";

function p(over: Partial<Problem>): Problem {
  return {
    id: 1,
    slug: "s",
    title: "Title",
    difficulty: "Easy",
    description: "",
    constraints: "",
    examples: [],
    editorial: "",
    optimal_time: "",
    optimal_space: "",
    optimal_explanation: "",
    starter_code: {},
    topics: [],
    subtopics: [],
    companies: [],
    patterns: [],
    hints: [],
    prerequisites: [],
    test_cases: [],
    function_spec: null,
    judge_mode: "exact",
    float_tolerance: 0,
    time_limit_ms: 0,
    editorials: [],
    follow_ups: [],
    is_favorite: false,
    solved_status: "unsolved",
    confidence: 0,
    last_solved_at: null,
    time_taken_seconds: 0,
    attempts_count: 0,
    success_count: 0,
    created_at: "2026-01-01",
    updated_at: "2026-01-01",
    ...over,
  };
}

describe("applyFilter", () => {
  const data = [
    p({ id: 1, title: "Two Sum", difficulty: "Easy", topics: ["Hashing"], companies: ["Amazon"] }),
    p({ id: 2, title: "Dijkstra", difficulty: "Hard", topics: ["Graphs"], solved_status: "solved", confidence: 1 }),
    p({ id: 3, title: "Edit Distance", difficulty: "Hard", topics: ["Dynamic Programming"], is_favorite: true }),
  ];

  it("passes everything through with the empty filter", () => {
    expect(applyFilter(data, emptyFilter)).toHaveLength(3);
  });

  it("searches title and tags case-insensitively", () => {
    expect(applyFilter(data, { ...emptyFilter, search: "amazon" }).map((x) => x.id)).toEqual([1]);
    expect(applyFilter(data, { ...emptyFilter, search: "graph" }).map((x) => x.id)).toEqual([2]);
  });

  it("filters by difficulty and topic", () => {
    expect(applyFilter(data, { ...emptyFilter, difficulties: ["Hard"] })).toHaveLength(2);
    expect(
      applyFilter(data, { ...emptyFilter, topics: ["Dynamic Programming"] }).map((x) => x.id)
    ).toEqual([3]);
  });

  it("supports favorites and weak-confidence predicates", () => {
    expect(applyFilter(data, { ...emptyFilter, favoritesOnly: true }).map((x) => x.id)).toEqual([3]);
    expect(applyFilter(data, { ...emptyFilter, weakConfidence: true }).map((x) => x.id)).toEqual([2]);
  });

  it("sorts by difficulty then title by default", () => {
    const ids = applyFilter(data, emptyFilter).map((x) => x.id);
    expect(ids[0]).toBe(1); // Easy first
  });

  it("finds problems where cumulative time exceeds 45 minutes", () => {
    const d = [p({ id: 1, time_taken_seconds: 30 * 60 }), p({ id: 2, time_taken_seconds: 50 * 60 })];
    expect(applyFilter(d, { ...emptyFilter, overTime: true }).map((x) => x.id)).toEqual([2]);
  });

  it("finds problems failed at least twice", () => {
    const d = [
      p({ id: 1, attempts_count: 3, success_count: 1 }), // 2 failures
      p({ id: 2, attempts_count: 2, success_count: 2 }), // 0 failures
    ];
    expect(applyFilter(d, { ...emptyFilter, failedTwice: true }).map((x) => x.id)).toEqual([1]);
  });

  it("finds solved-but-never-optimal problems", () => {
    const d = [
      p({ id: 1, solved_status: "solved", confidence: 5 }),
      p({ id: 2, solved_status: "solved", confidence: 2 }),
      p({ id: 3, solved_status: "unsolved", confidence: 0 }),
    ];
    expect(applyFilter(d, { ...emptyFilter, neverOptimal: true }).map((x) => x.id)).toEqual([2]);
  });
});
