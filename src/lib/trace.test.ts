import { describe, expect, it } from "vitest";
import { parseTrace } from "./trace";

describe("parseTrace", () => {
  it("ignores non-trace lines", () => {
    expect(parseTrace("hello\nworld\n")).toEqual([]);
  });

  it("parses ints and arrays", () => {
    const steps = parseTrace("#T arr=[1, 2, 3] i=0 lo=2\nnoise\n#T i=1\n");
    expect(steps).toHaveLength(2);
    expect(steps[0].vars).toEqual({ arr: [1, 2, 3], i: 0, lo: 2 });
    expect(steps[1].vars).toEqual({ i: 1 });
  });

  it("handles empty arrays and negative numbers", () => {
    const s = parseTrace("#T a=[] n=-5");
    expect(s[0].vars).toEqual({ a: [], n: -5 });
  });

  it("keeps non-numeric tokens as strings", () => {
    const s = parseTrace('#T state="done" x=3');
    expect(s[0].vars).toEqual({ state: "done", x: 3 });
  });

  it("parses space- or comma-separated arrays", () => {
    expect(parseTrace("#T a=[1 2 3]")[0].vars.a).toEqual([1, 2, 3]);
    expect(parseTrace("#T a=[1,2,3]")[0].vars.a).toEqual([1, 2, 3]);
  });
});
