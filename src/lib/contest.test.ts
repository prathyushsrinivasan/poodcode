import { describe, expect, it } from "vitest";
import { contestScore, contestStartMs, secondsLeft } from "./contest";

describe("contestStartMs", () => {
  it("reads SQLite's zone-less datetime('now') as UTC, not local time", () => {
    expect(contestStartMs("2026-09-24 10:00:00")).toBe(Date.UTC(2026, 8, 24, 10, 0, 0));
  });

  it("leaves a string that already carries a zone alone", () => {
    expect(contestStartMs("2026-09-24T10:00:00Z")).toBe(Date.UTC(2026, 8, 24, 10, 0, 0));
    expect(contestStartMs("2026-09-24T12:00:00+02:00")).toBe(Date.UTC(2026, 8, 24, 10, 0, 0));
  });

  it("is NaN for an empty value", () => {
    expect(contestStartMs("")).toBeNaN();
  });
});

describe("secondsLeft", () => {
  const start = "2026-09-24 10:00:00";
  const t0 = Date.UTC(2026, 8, 24, 10, 0, 0);

  it("counts down from the duration", () => {
    expect(secondsLeft({ started_at: start, duration_seconds: 3600 }, t0)).toBe(3600);
    expect(secondsLeft({ started_at: start, duration_seconds: 3600 }, t0 + 90_500)).toBe(3510);
  });

  it("never goes negative, and ignores a clock that is behind the start", () => {
    expect(secondsLeft({ started_at: start, duration_seconds: 60 }, t0 + 3_600_000)).toBe(0);
    expect(secondsLeft({ started_at: start, duration_seconds: 60 }, t0 - 5_000)).toBe(60);
  });

  it("falls back to the full duration when the start is unreadable", () => {
    expect(secondsLeft({ started_at: "", duration_seconds: 900 }, t0)).toBe(900);
  });
});

describe("contestScore", () => {
  it("counts solved problems and wrong tries", () => {
    const score = contestScore({
      results: [
        { problem_id: 1, title: "a", difficulty: "Easy", solved: true, solved_at: "x", wrong_tries: 2 },
        { problem_id: 2, title: "b", difficulty: "Easy", solved: false, solved_at: null, wrong_tries: 1 },
      ],
    });
    expect(score).toEqual({ solved: 1, total: 2, wrongTries: 3 });
  });
});
