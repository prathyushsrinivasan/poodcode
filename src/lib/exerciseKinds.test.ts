import { describe, it, expect } from "vitest";
import { KIND_SECTIONS, bucketFor, groupByKind, kindOf } from "./exerciseKinds";

// The regression these guard: a page that filters exercises into hard-coded
// buckets silently drops any kind it does not know, while the completion count
// still requires it — leaving a lesson stuck at "n-1 of n solved" with nothing
// on the page left to solve.

const ex = (id: string, kind: string) => ({ id, kind });

describe("kindOf", () => {
  it("defaults an empty kind to drill, the way the generators leave it", () => {
    expect(kindOf({ kind: "" })).toBe("drill");
    expect(kindOf({ kind: "fix" })).toBe("fix");
  });
});

describe("bucketFor", () => {
  it("puts each known kind in its own bucket", () => {
    const all = KIND_SECTIONS.map((s) => ex(s.kind, s.kind));
    for (const s of KIND_SECTIONS) {
      expect(bucketFor(all, s.kind).map((e) => e.id)).toEqual([s.kind]);
    }
  });

  it("sweeps an unrecognised kind into the drill bucket instead of dropping it", () => {
    const items = [ex("a", "drill"), ex("b", "sculpt"), ex("c", "challenge")];
    expect(bucketFor(items, "drill").map((e) => e.id)).toEqual(["a", "b"]);
    expect(bucketFor(items, "challenge").map((e) => e.id)).toEqual(["c"]);
  });

  it("treats an empty kind as a drill", () => {
    expect(bucketFor([ex("a", "")], "drill").map((e) => e.id)).toEqual(["a"]);
  });
});

describe("groupByKind", () => {
  it("renders every exercise exactly once, whatever its kind", () => {
    const items = [
      ex("a", "drill"),
      ex("b", "fix"),
      ex("c", "predict"),
      ex("d", "not-a-real-kind"),
      ex("e", ""),
      ex("f", "challenge"),
    ];
    const shown = groupByKind(items).flatMap((g) => g.group.map((e) => e.id));
    expect(shown.sort()).toEqual(["a", "b", "c", "d", "e", "f"]);
    expect(new Set(shown).size).toBe(items.length);
  });

  it("keeps teaching order and drops empty sections", () => {
    const items = [ex("a", "challenge"), ex("b", "predict"), ex("c", "drill")];
    expect(groupByKind(items).map((g) => g.section.kind)).toEqual([
      "predict",
      "drill",
      "challenge",
    ]);
  });

  it("returns nothing for no exercises", () => {
    expect(groupByKind([])).toEqual([]);
  });
});
