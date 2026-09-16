import { describe, it, expect } from "vitest";
import { acceptsReading, joinReading, kanaOf, normKana, normRomaji, romajiOf } from "./romaji";

describe("kanaOf / romajiOf", () => {
  it("splits a glossary card's combined reading", () => {
    expect(kanaOf("へんすう (hensū)")).toBe("へんすう");
    expect(romajiOf("へんすう (hensū)")).toBe("hensū");
  });

  it("treats a bare katakana loanword reading as rōmaji only", () => {
    expect(kanaOf("kōdo")).toBe("");
    expect(romajiOf("kōdo")).toBe("kōdo");
  });

  it("rebuilds the combined shape from the vocabulary list's two fields", () => {
    expect(joinReading("へんすう", "hensū")).toBe("へんすう (hensū)");
    expect(joinReading("けいしょう", "")).toBe("けいしょう");
  });
});

describe("normRomaji", () => {
  it("folds macrons and drops spacing and punctuation", () => {
    expect(normRomaji("kata hikisū")).toBe("katahikisu");
    expect(normRomaji("don'yokuhō")).toBe("donyokuho");
  });

  it("collapses the long vowels people type in three different ways", () => {
    expect(normRomaji("keishō")).toBe("keisho");
    expect(normRomaji("keishou")).toBe("keisho");
    expect(normRomaji("keishoo")).toBe("keisho");
    expect(normRomaji("hensuu")).toBe(normRomaji("hensū"));
  });

  it("leaves 'ei' alone — it is two vowels, not a long e", () => {
    expect(normRomaji("seiteki")).toBe("seiteki");
  });
});

describe("normKana", () => {
  it("reads katakana as hiragana and drops the long mark", () => {
    expect(normKana("コード")).toBe("こど");
    expect(normKana("はい れつ")).toBe("はいれつ");
  });
});

describe("acceptsReading", () => {
  const reading = "けいしょう (keishō)";

  it("accepts the rōmaji, however the long vowel is typed", () => {
    expect(acceptsReading("keishō", reading)).toBe(true);
    expect(acceptsReading("keishou", reading)).toBe(true);
    expect(acceptsReading("  KEISHO ", reading)).toBe(true);
  });

  it("accepts the reading typed in kana", () => {
    expect(acceptsReading("けいしょう", reading)).toBe(true);
    expect(acceptsReading("ケイショウ", reading)).toBe(true);
  });

  it("rejects a wrong reading in either script", () => {
    expect(acceptsReading("keisei", reading)).toBe(false);
    expect(acceptsReading("けいせい", reading)).toBe(false);
    expect(acceptsReading("   ", reading)).toBe(false);
  });

  it("grades a katakana loanword against its rōmaji", () => {
    expect(acceptsReading("kodo", "kōdo")).toBe(true);
    expect(acceptsReading("koodo", "kōdo")).toBe(true);
  });
});
