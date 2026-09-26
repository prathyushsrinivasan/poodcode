import { describe, expect, it } from "vitest";
import { mockAttemptSummary, parseMockState, parseReviewState } from "./capstone";

describe("parseMockState", () => {
  it("defaults when missing or unreadable", () => {
    expect(parseMockState(undefined)).toEqual({ startedAt: null, attempts: [] });
    expect(parseMockState("{nope")).toEqual({ startedAt: null, attempts: [] });
    expect(parseMockState("[1,2]")).toEqual({ startedAt: null, attempts: [] });
  });

  it("keeps valid attempts and drops malformed ones", () => {
    const raw = JSON.stringify({
      startedAt: "2026-09-27T10:00:00.000Z",
      attempts: [
        { date: "2026-09-26T10:00:00.000Z", seconds: 2400, scores: [3, 2, 4, 3] },
        { date: "x", seconds: "long", scores: [1] },
      ],
    });
    const st = parseMockState(raw);
    expect(st.startedAt).toBe("2026-09-27T10:00:00.000Z");
    expect(st.attempts).toHaveLength(1);
  });

  it("drops a start time that is not a date", () => {
    expect(parseMockState(JSON.stringify({ startedAt: "soon", attempts: [] })).startedAt).toBeNull();
  });
});

describe("parseReviewState", () => {
  it("reads text, compared and caught", () => {
    const st = parseReviewState(JSON.stringify({ text: "cast hides a bug", compared: true, caught: [0, 2] }));
    expect(st).toEqual({ text: "cast hides a bug", compared: true, caught: [0, 2] });
  });

  it("defaults bad fields", () => {
    expect(parseReviewState(JSON.stringify({ text: 3, compared: "yes", caught: ["a"] }))).toEqual({
      text: "",
      compared: false,
      caught: [],
    });
  });
});

describe("mockAttemptSummary", () => {
  it("is null before the first attempt", () => {
    expect(mockAttemptSummary([], 4)).toBeNull();
  });

  it("reports best, last and the maximum", () => {
    const s = mockAttemptSummary(
      [
        { date: "a", seconds: 1, scores: [4, 4, 3, 3] },
        { date: "b", seconds: 1, scores: [2, 2, 2, 2] },
      ],
      4
    );
    expect(s).toEqual({ count: 2, best: 14, last: 8, max: 16 });
  });
});
