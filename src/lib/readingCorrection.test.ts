import { describe, expect, it } from "vitest";
import { readingCorrection } from "./readingCorrection";

describe("reading corrections", () => {
  it("marks a missing long-vowel kana without marking the rest of the reading", () => {
    const diff = readingCorrection("せさん", ["せいさん"]);
    expect(diff.distance).toBe(1);
    expect(diff.correct.filter((p) => p.changed).map((p) => p.text)).toEqual(["い"]);
    expect(diff.given.every((p) => !p.changed)).toBe(true);
  });
  it("locates small-kana and voiced-sound substitutions", () => {
    expect(readingCorrection("しゆっちょう", ["しゅっちょう"]).correct.filter((p) => p.changed).map((p) => p.text)).toEqual(["ゅ"]);
    expect(readingCorrection("てかみ", ["てがみ"]).given.filter((p) => p.changed).map((p) => p.text)).toEqual(["か"]);
  });
  it("handles extra kana, normalized marks and the nearest accepted alternative", () => {
    expect(readingCorrection("はっぴょうう", ["はっぴょう"]).given.filter((p) => p.changed)).toHaveLength(1);
    expect(readingCorrection(" てか\u3099み ", ["てがみ"]).distance).toBe(0);
    expect(readingCorrection("ゆきづま", ["いきづまる", "ゆきづまる"]).target).toBe("ゆきづまる");
    expect(readingCorrection("", ["せいさん"]).correct.every((p) => p.changed)).toBe(true);
  });
});
