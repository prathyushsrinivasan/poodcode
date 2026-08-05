import { describe, expect, it } from "vitest";
import { hasMutablePayload, mulberry32, mutateInput } from "./testgen";

describe("mutateInput", () => {
  it("keeps the count line fixed and preserves token/line structure", () => {
    const out = mutateInput("3\n1 2 3\n", "perturb", mulberry32(1));
    const lines = out.replace(/\n$/, "").split("\n");
    expect(lines[0]).toBe("3"); // structural count is frozen
    expect(lines[1].trim().split(/\s+/).length).toBe(3); // still three payload ints
    expect(out.endsWith("\n")).toBe(true); // trailing newline preserved
  });

  it("leaves non-integer tokens untouched", () => {
    expect(mutateInput("hello world\n", "perturb", mulberry32(2))).toBe("hello world\n");
  });

  it("min mode drives non-negative payload to zero", () => {
    const out = mutateInput("2\n5 8\n", "min", mulberry32(3));
    expect(out.replace(/\n$/, "").split("\n")[1]).toBe("0 0");
  });

  it("freezes both dimensions of a 'rows cols' grid line", () => {
    const grid = "2 3\nabc\ndef\n";
    const out = mutateInput(grid, "large", mulberry32(4));
    expect(out.split("\n")[0]).toBe("2 3"); // dimensions frozen -> grid stays valid
  });

  it("is deterministic for a fixed seed", () => {
    const a = mutateInput("1\n4 5 6\n", "perturb", mulberry32(7));
    const b = mutateInput("1\n4 5 6\n", "perturb", mulberry32(7));
    expect(a).toBe(b);
  });
});

describe("hasMutablePayload", () => {
  it("is true when there are payload integers", () => {
    expect(hasMutablePayload("2\n5 8\n")).toBe(true);
  });
  it("is false for input with no mutable integers", () => {
    expect(hasMutablePayload("hello world\n")).toBe(false);
  });
});
