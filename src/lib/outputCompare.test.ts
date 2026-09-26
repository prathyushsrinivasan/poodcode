import { describe, expect, it } from "vitest";
import { describeDifference, firstDifference, normalizeOutput, visibleWhitespace } from "./outputCompare";

describe("normalizeOutput", () => {
  it("matches the judge: CR, trailing spaces and trailing blank lines ignored", () => {
    expect(normalizeOutput("a  \r\nb\n\n\n")).toBe("a\nb");
  });
});

describe("firstDifference", () => {
  it("is same after normalisation", () => {
    expect(firstDifference("1\n2\n", "1  \n2")).toEqual({ kind: "same" });
  });

  it("finds a character difference", () => {
    expect(firstDifference("x=4\ny=5", "x=4\ny=5.0")).toEqual({
      kind: "char",
      line: 2,
      column: 4,
      expected: "y=5",
      actual: "y=5.0",
    });
  });

  it("finds missing and extra lines", () => {
    expect(firstDifference("a\nb", "a")).toEqual({ kind: "missing", line: 2, expected: "b" });
    expect(firstDifference("a", "a\nb")).toEqual({ kind: "extra", line: 2, actual: "b" });
    expect(firstDifference("a", "")).toEqual({ kind: "missing", line: 1, expected: "a" });
  });
});

describe("describeDifference", () => {
  it("names case-only and spacing-only differences", () => {
    expect(describeDifference(firstDifference("Hello", "hello"))).toMatch(/upper\/lower case/);
    expect(describeDifference(firstDifference("a b", "a  b"))).toMatch(/spacing/);
  });

  it("says when a line ends early or runs on", () => {
    expect(describeDifference(firstDifference("total 12", "total"))).toMatch(/ends early/);
    expect(describeDifference(firstDifference("total", "total 12"))).toMatch(/runs on/);
  });

  it("quotes the diverging text", () => {
    expect(describeDifference(firstDifference("x=4", "x=5"))).toBe(
      "Line 1 differs at column 3: expected `4`, you printed `5`."
    );
  });
});

describe("visibleWhitespace", () => {
  it("shows spaces and tabs", () => {
    expect(visibleWhitespace("a b\tc")).toBe("a·b→c");
  });
});
