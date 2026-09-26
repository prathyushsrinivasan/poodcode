import { describe, expect, it } from "vitest";
import {
  expandableTypes,
  lineOf,
  maskNonCode,
  occurrences,
  probeSource,
  probeType,
} from "./tsAnalysis";

describe("maskNonCode", () => {
  it("blanks strings and comments but keeps length and newlines", () => {
    const src = 'const a = "x y"; // note\n/* b */ const c = 1;';
    const masked = maskNonCode(src);
    expect(masked.length).toBe(src.length);
    expect(masked).toBe('const a = "   ";        \n        const c = 1;');
  });

  it("keeps template holes as code", () => {
    const masked = maskNonCode("const s = `n=${n} ok`;");
    expect(masked).toBe("const s = `  ${n}   `;");
  });
});

describe("occurrences", () => {
  const src = 'function f(x: string | null) {\n  if (x === null) return "x";\n  return x.length; // x\n}\n';

  it("finds code uses only", () => {
    const hits = occurrences(src, "x");
    expect(hits.map((o) => lineOf(src, o))).toEqual([1, 2, 3]);
  });

  it("ignores property accesses and longer names", () => {
    expect(occurrences("const xs = [1]; o.x = xs.length;", "x")).toEqual([]);
  });

  it("rejects non-identifiers", () => {
    expect(occurrences("a+b", "a+b")).toEqual([]);
  });
});

describe("expandableTypes", () => {
  it("lists non-generic aliases and interfaces", () => {
    const src = "type A = { a: 1 };\ninterface B { b: 2 }\ntype G<T> = T[];\nexport type C = A & B;\n// type D = 1\n";
    expect(expandableTypes(src)).toEqual(["A", "B", "C"]);
  });
});

describe("probeSource", () => {
  it("appends one probe per name and points at each probe's name", () => {
    const { text, offsets } = probeSource("type A = 1;\n", ["A"]);
    expect(text.slice(offsets[0], offsets[0]! + 6)).toBe("__pg_0");
    expect(text).toContain("declare const __pg_0: __PgExpand<A>;");
  });
  it("reads the type out of a quick-info string", () => {
    expect(probeType("const __pg_0: { a: number; }")).toBe("{ a: number; }");
  });
});
