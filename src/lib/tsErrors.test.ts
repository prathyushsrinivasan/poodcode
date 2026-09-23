import { describe, expect, it } from "vitest";
import { TS_ERRORS, codesIn, entriesIn, errorEntry, searchErrors } from "./tsErrors";

describe("the glossary data", () => {
  it("has unique codes, each with an example pair and a teaching week", () => {
    const codes = TS_ERRORS.map((e) => e.code);
    expect(new Set(codes).size).toBe(codes.length);
    for (const e of TS_ERRORS) {
      expect(e.bad.trim().length).toBeGreaterThan(0);
      expect(e.good.trim().length).toBeGreaterThan(0);
      expect(e.week).toBeGreaterThanOrEqual(1);
      expect(e.week).toBeLessThanOrEqual(26);
    }
  });

  it("covers the errors every learner meets first", () => {
    for (const code of [2322, 2345, 2339, 7006, 18048, 2532]) {
      expect(errorEntry(code), `TS${code}`).toBeDefined();
    }
  });
});

describe("codesIn", () => {
  it("finds every distinct code in tsc output, in order", () => {
    const out = [
      "main.ts(3,7): error TS2322: Type 'string' is not assignable to type 'number'.",
      "main.ts(5,1): error TS7006: Parameter 'x' implicitly has an 'any' type.",
      "main.ts(9,7): error TS2322: Type 'boolean' is not assignable to type 'number'.",
    ].join("\n");
    expect(codesIn(out)).toEqual([2322, 7006]);
  });

  it("ignores things that merely look numeric", () => {
    expect(codesIn("exit code 2322, line TS12 and ATS2322x")).toEqual([]);
  });
});

describe("entriesIn", () => {
  it("returns glossary entries only for codes the glossary covers", () => {
    const out = "error TS2322: … error TS9999: …";
    expect(entriesIn(out).map((e) => e.code)).toEqual([2322]);
  });
});

describe("searchErrors", () => {
  it("matches by code, with or without the TS prefix", () => {
    expect(searchErrors("2322").map((e) => e.code)).toContain(2322);
    expect(searchErrors("ts2322").map((e) => e.code)).toContain(2322);
  });

  it("requires every word to match", () => {
    const hits = searchErrors("possibly undefined");
    expect(hits.length).toBeGreaterThan(0);
    for (const e of hits) {
      const hay = `${e.title} ${e.meaning} ${e.cause}`.toLowerCase();
      expect(hay).toContain("possibly");
      expect(hay).toContain("undefined");
    }
  });

  it("returns everything for an empty query", () => {
    expect(searchErrors("  ")).toHaveLength(TS_ERRORS.length);
  });
});
