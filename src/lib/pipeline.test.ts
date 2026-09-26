import { describe, expect, it } from "vitest";
import { PIPE_PRESETS, runPipeline } from "./pipeline";

describe("runPipeline", () => {
  it("keeps every intermediate", () => {
    const r = runPipeline([3, 8, 1, 6], PIPE_PRESETS[0]!.steps);
    expect(r.map((x) => x.value)).toEqual([[8, 6], [64, 36], 100]);
  });

  it("stops when a step gets something that is not an array", () => {
    const r = runPipeline([1, 2], [
      { method: "reduce", arg: "(a, b) => a + b, 0" },
      { method: "map", arg: "(x) => x" },
    ]);
    expect(r).toHaveLength(2);
    expect(r[1]!.error).toMatch(/needs an array/);
  });

  it("reports a thrown error", () => {
    const r = runPipeline([], [{ method: "reduce", arg: "(a, b) => a + b" }]);
    expect(r[0]!.error).toMatch(/TypeError/);
  });

  it("notices a mutating step", () => {
    const r = runPipeline([3, 1, 2], [{ method: "sort", arg: "" }]);
    expect(r[0]!.mutatedInput).toBe(true);
    expect(runPipeline([3, 1, 2], [{ method: "toSorted", arg: "" }])[0]!.mutatedInput).toBe(false);
  });

  it("shows the classic surprises", () => {
    expect(runPipeline([10, 9, 1, 100], PIPE_PRESETS[2]!.steps)[0]!.value).toEqual([1, 10, 100, 9]);
    expect(runPipeline(["1", "2", "3", "10"], PIPE_PRESETS[3]!.steps)[0]!.value).toEqual([1, NaN, NaN, 3]);
  });
});
