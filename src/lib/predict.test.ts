import { beforeEach, describe, expect, it } from "vitest";
import { logMismatch, predictionLog, predictionMatches } from "./predict";

describe("predictionMatches", () => {
  it("uses the judge's normalisation", () => {
    expect(predictionMatches("1\n2  \n\n", "1\n2")).toBe(true);
    expect(predictionMatches("1 2", "1\n2")).toBe(false);
  });
});

describe("the mismatch log", () => {
  beforeEach(() => {
    // The test environment is Node, which has no localStorage: a map will do.
    const store = new Map<string, string>();
    (globalThis as { localStorage?: unknown }).localStorage = {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => void store.set(k, v),
      clear: () => store.clear(),
    };
  });
  it("keeps mismatches newest first", () => {
    logMismatch("a", "1", "2", new Date("2026-01-01T00:00:00Z"));
    logMismatch("b", "x", "y", new Date("2026-01-02T00:00:00Z"));
    expect(predictionLog().map((p) => p.id)).toEqual(["b", "a"]);
  });
});
