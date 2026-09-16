import { describe, it, expect } from "vitest";
import { hasJapaneseVoice, isJapaneseVoice, pickJapaneseVoice, type VoiceLike } from "./speech";

const voice = (lang: string, name: string, dflt = false): VoiceLike => ({
  lang,
  name,
  default: dflt,
});

describe("isJapaneseVoice", () => {
  it("accepts the spellings platforms actually report", () => {
    expect(isJapaneseVoice(voice("ja-JP", "Kyoko"))).toBe(true);
    expect(isJapaneseVoice(voice("ja", "Generic"))).toBe(true);
    expect(isJapaneseVoice(voice("ja_JP", "Underscored"))).toBe(true);
  });

  it("rejects other languages, including ones merely starting with j", () => {
    expect(isJapaneseVoice(voice("en-US", "Alex"))).toBe(false);
    expect(isJapaneseVoice(voice("jv-ID", "Javanese"))).toBe(false);
  });
});

describe("pickJapaneseVoice", () => {
  it("returns undefined when nothing Japanese is installed", () => {
    expect(pickJapaneseVoice([voice("en-US", "Alex"), voice("de-DE", "Anna")])).toBeUndefined();
  });

  it("prefers an exact ja-JP over a bare ja", () => {
    const picked = pickJapaneseVoice([voice("ja", "Bare"), voice("ja-JP", "Kyoko")]);
    expect(picked?.name).toBe("Kyoko");
  });

  it("prefers the platform default among equally good voices", () => {
    const picked = pickJapaneseVoice([
      voice("ja-JP", "First"),
      voice("ja-JP", "Preferred", true),
    ]);
    expect(picked?.name).toBe("Preferred");
  });

  it("ignores non-Japanese voices even when they are the default", () => {
    const picked = pickJapaneseVoice([voice("en-US", "Alex", true), voice("ja-JP", "Kyoko")]);
    expect(picked?.name).toBe("Kyoko");
  });
});

describe("hasJapaneseVoice", () => {
  it("reports whether the list contains one at all", () => {
    expect(hasJapaneseVoice([voice("ja-JP", "Kyoko")])).toBe(true);
    expect(hasJapaneseVoice([voice("en-US", "Alex")])).toBe(false);
    expect(hasJapaneseVoice([])).toBe(false);
  });
});
