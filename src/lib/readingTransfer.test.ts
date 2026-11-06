import { describe, expect, it } from "vitest";
import type { ReadingPassage, ReadingWord } from "../data/dokkai/types";
import { readingTransferExamples } from "./readingTransfer";

const passage = (id: string, text: string): ReadingPassage => ({ id, kind: "short", title: id, topic: "Test", skill: "Reference", level: 1, texts: [{ text, translation: "Test" }], questions: [] });
describe("saved-word transfer", () => {
  const word: ReadingWord = { text: "生物", reading: "せいぶつ", meaning: "living organisms" };
  it("uses another authored passage while preserving the exact reading and sense", () => {
    const bank = [passage("source", "[生物|せいぶつ|living organisms]を調べる。"),
      passage("food", "[生物|なまもの|perishable food]を冷蔵する。"),
      passage("other", "海の[生物|せいぶつ|living organisms]を研究する。")];
    const examples = readingTransferExamples(word, "source", bank, []);
    expect(examples).toHaveLength(1);
    expect(examples[0]).toMatchObject({ passageId: "other", sentence: "海の生物を研究する。", at: 2 });
    expect(examples[0].sentence.slice(examples[0].at, examples[0].at + examples[0].wordText.length)).toBe("生物");
  });
  it("does not mistake an occurrence-specific override for the shared word's meaning", () => {
    const bank = [passage("different", "[生物|なまもの|perishable food]を買った。"), passage("same", "海の生物を調べた。")];
    expect(readingTransferExamples(word, "source", bank, [word]).map((e) => e.passageId)).toEqual(["same"]);
  });
  it("deduplicates contexts, limits results and returns no fabricated example when none matches", () => {
    const bank = [passage("a", "生物を研究する。"), passage("b", "生物を研究する。"), passage("c", "生物を観察する。")];
    expect(readingTransferExamples(word, "source", bank, [word], 3)).toHaveLength(2);
    expect(readingTransferExamples(word, "source", bank, [word], 1)).toHaveLength(1);
    expect(readingTransferExamples(word, "source", bank, [], 3)).toEqual([]);
  });
});
