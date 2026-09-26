import { describe, expect, it } from "vitest";
import type { Exercise, MasteryWeek } from "../types";
import { localDay, parseDaily, streak, todaysPuzzle, typeLadder } from "./typeLadder";

const ex = (id: string, difficulty: string, typed = true): Exercise =>
  ({
    id,
    title: id,
    prompt: "",
    hint: "",
    hints: [],
    language: "typescript",
    kind: typed ? "typelevel" : "challenge",
    difficulty,
    strictness: "",
    harness: "",
    judge_mode: typed ? "types" : "",
    forbid: [],
    starter: "",
    solution: "",
    tests: [],
    source_slug: "",
    dataset: "",
  }) as unknown as Exercise;

const wk = (n: number, practice: Exercise[], problemSet: Exercise[] = []): MasteryWeek =>
  ({
    week: n,
    phase: "",
    title: "",
    goal: "",
    concepts: [],
    problems: [],
    project: "",
    quiz: [],
    quiz_sample: 0,
    exam: null,
    contest: null,
    practice,
    problem_set: problemSet,
  }) as MasteryWeek;

describe("typeLadder", () => {
  it("keeps only type-graded work, by week then tier", () => {
    const ladder = typeLadder([
      wk(17, [ex("a-hard", "Hard"), ex("a-easy", "Easy"), ex("runtime", "Easy", false)]),
      wk(18, [ex("b", "Medium")], [ex("a-easy", "Easy")]),
    ]);
    expect(ladder.map((r) => r.exercise.id)).toEqual(["a-easy", "a-hard", "b"]);
  });
});

describe("todaysPuzzle", () => {
  const ladder = typeLadder([wk(17, [ex("a", "Easy"), ex("b", "Medium")]), wk(20, [ex("c", "Easy")])]);

  it("serves the first unsolved rung from a week reached", () => {
    expect(todaysPuzzle(ladder, 18, new Set(["a"]), { pick: null, days: [] }, "2026-09-27")?.exercise.id).toBe("b");
    expect(todaysPuzzle(ladder, 18, new Set(["a", "b"]), { pick: null, days: [] }, "2026-09-27")).toBeNull();
  });

  it("keeps today's pick for the whole day", () => {
    const state = { pick: { day: "2026-09-27", id: "a" }, days: ["2026-09-27"] };
    expect(todaysPuzzle(ladder, 20, new Set(["a"]), state, "2026-09-27")?.exercise.id).toBe("a");
    expect(todaysPuzzle(ladder, 20, new Set(["a"]), state, "2026-09-28")?.exercise.id).toBe("b");
  });
});

describe("streak", () => {
  it("counts back from today, or from yesterday while today is open", () => {
    expect(streak(["2026-09-25", "2026-09-26", "2026-09-27"], "2026-09-27")).toBe(3);
    expect(streak(["2026-09-25", "2026-09-26"], "2026-09-27")).toBe(2);
    expect(streak(["2026-09-24"], "2026-09-27")).toBe(0);
  });

  it("formats local days", () => {
    expect(localDay(new Date(2026, 0, 5, 23, 0))).toBe("2026-01-05");
  });

  it("parses defensively", () => {
    expect(parseDaily("x")).toEqual({ pick: null, days: [] });
  });
});
