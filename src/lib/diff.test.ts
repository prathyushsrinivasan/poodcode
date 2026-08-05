import { describe, expect, it } from "vitest";
import { diffStats, lineDiff } from "./diff";

describe("lineDiff", () => {
  it("marks unchanged lines as same", () => {
    const ops = lineDiff("a\nb\nc", "a\nb\nc");
    expect(ops.every((o) => o.type === "same")).toBe(true);
    expect(ops.length).toBe(3);
  });

  it("detects an added line", () => {
    const ops = lineDiff("a\nc", "a\nb\nc");
    expect(diffStats(ops)).toEqual({ added: 1, removed: 0 });
    expect(ops.find((o) => o.type === "add")?.text).toBe("b");
  });

  it("detects a removed line", () => {
    const ops = lineDiff("a\nb\nc", "a\nc");
    expect(diffStats(ops)).toEqual({ added: 0, removed: 1 });
    expect(ops.find((o) => o.type === "del")?.text).toBe("b");
  });

  it("represents a changed line as a delete + add", () => {
    const ops = lineDiff("x = 1", "x = 2");
    expect(diffStats(ops)).toEqual({ added: 1, removed: 1 });
  });
});
