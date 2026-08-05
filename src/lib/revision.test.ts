import { describe, expect, it } from "vitest";
import {
  LADDER,
  clampIndex,
  dueAfterReview,
  intervalDays,
  isDue,
  nextIndex,
  sm2,
} from "./revision";

describe("revision ladder", () => {
  it("clamps indices into range", () => {
    expect(clampIndex(-5)).toBe(0);
    expect(clampIndex(99)).toBe(LADDER.length - 1);
    expect(clampIndex(2)).toBe(2);
  });

  it("advances on recall and resets on lapse", () => {
    expect(nextIndex(0, true)).toBe(1);
    expect(nextIndex(2, true)).toBe(3);
    expect(nextIndex(LADDER.length - 1, true)).toBe(LADDER.length - 1);
    expect(nextIndex(4, false)).toBe(0);
  });

  it("maps indices to the correct interval length", () => {
    expect(intervalDays(0)).toBe(1);
    expect(intervalDays(5)).toBe(90);
  });

  it("computes due dates relative to a fixed day", () => {
    const from = new Date("2026-01-01T12:00:00Z");
    // recall from index 0 -> next index 1 -> 3 days
    expect(dueAfterReview(0, true, from)).toBe("2026-01-04");
    // lapse -> index 0 -> 1 day
    expect(dueAfterReview(3, false, from)).toBe("2026-01-02");
  });

  it("detects due items", () => {
    const today = new Date("2026-08-04T00:00:00Z");
    expect(isDue("2026-08-01", today)).toBe(true);
    expect(isDue("2026-08-04", today)).toBe(true);
    expect(isDue("2026-08-10", today)).toBe(false);
  });
});

describe("sm2 (mirrors backend repo::sm2)", () => {
  it("grows the interval across successive Good grades", () => {
    const a = sm2(1, 2.5, 0, 2); // first Good
    expect(a.interval).toBe(1);
    expect(a.lapse).toBe(false);
    const b = sm2(a.interval, a.ease, 1, 2); // second Good
    expect(b.interval).toBe(3);
    const c = sm2(b.interval, 2.5, 2, 2); // third compounds by ease
    expect(c.interval).toBeGreaterThanOrEqual(6);
  });

  it("lapses to 1 day and lowers ease on Again", () => {
    const r = sm2(20, 2.5, 5, 0);
    expect(r.interval).toBe(1);
    expect(r.lapse).toBe(true);
    expect(r.ease).toBeLessThan(2.5);
  });

  it("never drops ease below 1.3", () => {
    let ease = 2.5;
    for (let i = 0; i < 20; i++) ease = sm2(1, ease, 1, 0).ease;
    expect(ease).toBeGreaterThanOrEqual(1.3);
  });
});
