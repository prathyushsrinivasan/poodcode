import { describe, expect, it } from "vitest";
import { fromLines, inPlace, isBugLine, moveLine, toLines } from "./parsons";

describe("parsons", () => {
  it("round-trips a program through its pieces", () => {
    const code = "const a = 1;\nconsole.log(a);\n";
    expect(toLines(code)).toEqual(["const a = 1;", "console.log(a);"]);
    expect(fromLines(toLines(code))).toBe(code);
  });

  it("keeps indentation and repeated lines as separate pieces", () => {
    expect(toLines("if (x) {\n  f();\n}\n}\n")).toEqual(["if (x) {", "  f();", "}", "}"]);
  });

  it("moves a piece up, down and to the ends", () => {
    const l = ["a", "b", "c", "d"];
    expect(moveLine(l, 2, 1)).toEqual(["a", "c", "b", "d"]);
    expect(moveLine(l, 0, 3)).toEqual(["b", "c", "d", "a"]);
    expect(moveLine(l, 3, 0)).toEqual(["d", "a", "b", "c"]);
    expect(l).toEqual(["a", "b", "c", "d"]);
  });

  it("ignores moves off the list", () => {
    const l = ["a", "b"];
    expect(moveLine(l, 0, -1)).toBe(l);
    expect(moveLine(l, 1, 2)).toBe(l);
    expect(moveLine(l, 1, 1)).toBe(l);
  });

  it("counts pieces already in place", () => {
    expect(inPlace(["b", "a", "c"], "a\nb\nc\n")).toBe(1);
    expect(inPlace(["a", "b", "c"], "a\nb\nc\n")).toBe(3);
  });

  it("accepts any of the bug lines", () => {
    expect(isBugLine([3, 4], 4)).toBe(true);
    expect(isBugLine([3, 4], 2)).toBe(false);
    expect(isBugLine(undefined, 1)).toBe(false);
  });
});
