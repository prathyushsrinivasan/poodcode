import { describe, expect, it } from "vitest";
import {
  dueCardCount,
  heatSeries,
  mergeDue,
  sparklinePath,
  summariseGoals,
  weekOverWeek,
  type DueGroup,
} from "./today";
import type { CardReview } from "../types";

const review = (id: string, due: string): CardReview => ({
  card_id: id,
  ease: 2.5,
  reps: 1,
  lapses: 0,
  interval_days: 3,
  due_date: due,
  last_quality: 4,
});

describe("sparklinePath", () => {
  it("is empty for no data", () => {
    expect(sparklinePath([], 60, 20)).toBe("");
  });

  it("draws a flat series through the middle, not along the floor", () => {
    // "nothing happened" and "the minimum happened" must not look the same.
    const path = sparklinePath([4, 4, 4], 60, 20, 1);
    const ys = [...path.matchAll(/,([\d.]+)/g)].map((m) => Number(m[1]));
    expect(new Set(ys).size).toBe(1);
    expect(ys[0]).toBeCloseTo(10, 1);
  });

  it("puts the maximum at the top and the minimum at the bottom", () => {
    const path = sparklinePath([0, 10], 60, 20, 1);
    const ys = [...path.matchAll(/,([\d.]+)/g)].map((m) => Number(m[1]));
    expect(ys[0]).toBeGreaterThan(ys[1]);
  });

  it("spans the full width", () => {
    const path = sparklinePath([1, 2, 3], 60, 20, 1);
    const xs = [...path.matchAll(/[ML]([\d.]+),/g)].map((m) => Number(m[1]));
    expect(xs[0]).toBeCloseTo(1, 1);
    expect(xs[xs.length - 1]).toBeCloseTo(59, 1);
  });
});

describe("weekOverWeek", () => {
  it("compares the last seven days with the seven before", () => {
    const t = weekOverWeek([1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2]);
    expect(t.previous).toBe(7);
    expect(t.current).toBe(14);
    expect(t.percent).toBe(100);
    expect(t.direction).toBe("up");
  });

  it("reports no percentage when there is no earlier week", () => {
    // A first week of use is not "no change" — saying +0% would be a lie.
    const t = weekOverWeek([3, 3, 3]);
    expect(t.percent).toBeNull();
    expect(t.current).toBe(9);
  });

  it("reports no percentage when the earlier week was empty", () => {
    const t = weekOverWeek([0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 5, 5]);
    expect(t.percent).toBeNull();
  });

  it("detects a decline", () => {
    const t = weekOverWeek([2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1]);
    expect(t.percent).toBe(-50);
    expect(t.direction).toBe("down");
  });
});

describe("heatSeries", () => {
  it("takes the most recent days, oldest first", () => {
    const cells = [
      { date: "2026-01-01", count: 1 },
      { date: "2026-01-02", count: 2 },
      { date: "2026-01-03", count: 3 },
    ];
    expect(heatSeries(cells, 2)).toEqual([2, 3]);
  });
});

describe("dueCardCount", () => {
  const today = "2026-09-18";

  it("counts a card that has never been seen as due", () => {
    // The first sitting matters most; hiding it makes a fresh deck look done.
    expect(dueCardCount(["a", "b"], new Map(), today)).toBe(2);
  });

  it("counts a card due today", () => {
    const rs = new Map([["a", review("a", today)]]);
    expect(dueCardCount(["a"], rs, today)).toBe(1);
  });

  it("does not count a card due later", () => {
    const rs = new Map([["a", review("a", "2026-09-30")]]);
    expect(dueCardCount(["a"], rs, today)).toBe(0);
  });

  it("counts an overdue card", () => {
    const rs = new Map([["a", review("a", "2026-09-01")]]);
    expect(dueCardCount(["a"], rs, today)).toBe(1);
  });
});

describe("mergeDue", () => {
  const g = (source: DueGroup["source"], count: number): DueGroup => ({
    source,
    label: source,
    count,
    href: "/",
    hint: "",
  });

  it("drops empty groups and puts the biggest pile first", () => {
    const out = mergeDue([g("curriculum", 2), g("vocab", 0), g("slow", 9)]);
    expect(out.map((x) => x.source)).toEqual(["slow", "curriculum"]);
  });

  it("is empty when nothing is due", () => {
    expect(mergeDue([g("vocab", 0)])).toEqual([]);
  });
});

describe("summariseGoals", () => {
  it("ignores goals with no target", () => {
    const { rows, met, total } = summariseGoals([
      { key: "a", label: "A", done: 1, target: 1 },
      { key: "b", label: "B", done: 0, target: 0 },
      { key: "c", label: "C", done: 0, target: 3 },
    ]);
    expect(rows.map((r) => r.key)).toEqual(["a", "c"]);
    expect(met).toBe(1);
    expect(total).toBe(2);
  });

  it("counts exceeding a target as met", () => {
    const { met } = summariseGoals([{ key: "a", label: "A", done: 5, target: 2 }]);
    expect(met).toBe(1);
  });
});
