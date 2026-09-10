import { describe, it, expect } from "vitest";
import { collectExerciseIds, plural, solvedLabel, studyTime } from "./trackProgress";

const ex = (id: string) => ({ id }) as never;

describe("studyTime", () => {
  it("keeps short units in minutes", () => {
    expect(studyTime(45)).toBe("~45 min");
    expect(studyTime(89)).toBe("~89 min");
  });

  it("switches to hours at 90 minutes, and drops a pointless decimal", () => {
    expect(studyTime(90)).toBe("~1.5 h");
    expect(studyTime(120)).toBe("~2 h");
    expect(studyTime(300)).toBe("~5 h");
  });

  it("renders an unsized unit as nothing, so it can be dropped into a sentence", () => {
    expect(studyTime(0)).toBe("");
    expect(studyTime(-1)).toBe("");
  });
});

describe("plural", () => {
  it("only pluralises what is not one", () => {
    expect(plural(1, "module")).toBe("1 module");
    expect(plural(2, "module")).toBe("2 modules");
    expect(plural(0, "module")).toBe("0 modules");
  });
});

describe("solvedLabel", () => {
  const solved = new Set(["a", "b"]);

  it("says nothing when there is nothing to solve", () => {
    expect(solvedLabel([], solved)).toBe("");
    expect(solvedLabel(undefined, solved)).toBe("");
    expect(solvedLabel(null, solved)).toBe("");
  });

  it("counts partial progress", () => {
    expect(solvedLabel([ex("a"), ex("c")], solved)).toBe("1/2");
    expect(solvedLabel([ex("c")], solved)).toBe("0/1");
  });

  it("marks a fully solved group done", () => {
    expect(solvedLabel([ex("a"), ex("b")], solved)).toBe("✓ done");
  });
});

describe("collectExerciseIds", () => {
  it("gathers every group's exercises in order", () => {
    const groups = [{ exercises: [ex("a"), ex("b")] }, { exercises: [ex("c")] }];
    expect(collectExerciseIds(groups)).toEqual(["a", "b", "c"]);
  });

  it("appends the closing build, when there is one", () => {
    const groups = [{ exercises: [ex("a")] }];
    expect(collectExerciseIds(groups, ex("final"))).toEqual(["a", "final"]);
  });

  it("skips a missing build rather than emitting a hole", () => {
    const groups = [{ exercises: [ex("a")] }];
    expect(collectExerciseIds(groups, null)).toEqual(["a"]);
    expect(collectExerciseIds(groups, undefined)).toEqual(["a"]);
  });

  it("tolerates missing groups and missing exercise lists", () => {
    expect(collectExerciseIds(null)).toEqual([]);
    expect(collectExerciseIds(undefined)).toEqual([]);
    expect(collectExerciseIds([{}, { exercises: null }])).toEqual([]);
  });
});
