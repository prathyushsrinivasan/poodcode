import { afterEach, describe, expect, it, vi } from "vitest";
import { clearFailures, failureMessage, ignore, loadFailed, recentFailures, saveFailed } from "./failures";

afterEach(() => {
  clearFailures();
  vi.restoreAllMocks();
});

describe("failure handlers", () => {
  it("records an ignored failure with its reason and returns undefined", () => {
    vi.spyOn(console, "debug").mockImplementation(() => {});
    expect(ignore("a badge")(new Error("boom"))).toBeUndefined();
    const [f] = recentFailures();
    expect(f.kind).toBe("ignored");
    expect(f.what).toBe("a badge");
    expect(f.detail).toBe("boom");
  });

  it("words load and save failures for the toast", () => {
    vi.spyOn(console, "warn").mockImplementation(() => {});
    loadFailed("your progress")("x");
    saveFailed("your draft")("y");
    const [save, load] = recentFailures();
    expect(failureMessage(save)).toBe("Couldn't save your draft.");
    expect(failureMessage(load)).toBe("Couldn't load your progress.");
  });

  it("keeps the newest fifty", () => {
    vi.spyOn(console, "debug").mockImplementation(() => {});
    for (let i = 0; i < 60; i++) ignore(`n${i}`)("e");
    expect(recentFailures()).toHaveLength(50);
    expect(recentFailures()[0].what).toBe("n59");
  });

  it("stringifies non-Error rejections", () => {
    vi.spyOn(console, "warn").mockImplementation(() => {});
    saveFailed("x")({ code: 5 });
    expect(recentFailures()[0].detail).toBe('{"code":5}');
  });
});
