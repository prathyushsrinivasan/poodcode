import { describe, expect, it } from "vitest";
import { evidenceSentences, compareEvidence } from "./readingEvidence";

describe("reader evidence selection", () => {
  const texts = [{ text: "[図書館|としょかん|library]は月曜に休む。火曜は開いている。\n利用には登録が必要だ。" }];
  it("splits plain sentences without exposing annotation syntax or losing source positions", () => {
    const sentences = evidenceSentences(texts);
    expect(sentences.map((s) => s.text)).toEqual(["図書館は月曜に休む。", "火曜は開いている。", "利用には登録が必要だ。"]);
    expect(new Set(sentences.map((s) => s.id)).size).toBe(3);
    expect(sentences[1].start).toBe(sentences[0].end);
  });
  it("requires coverage of each quote and distinguishes extra irrelevant sentences", () => {
    const [first, second, third] = evidenceSentences(texts);
    const quotes = ["月曜に休む", "登録が必要"];
    expect(compareEvidence(texts, quotes, [first.id]).coversAll).toBe(false);
    expect(compareEvidence(texts, quotes, [first.id, third.id])).toMatchObject({ coversAll: true });
    const extra = compareEvidence(texts, quotes, [first.id, second.id, third.id]);
    expect(extra.selected).toHaveLength(3); expect(extra.matching).toHaveLength(2);
    expect(compareEvidence(texts, quotes, []).coversAll).toBe(false);
  });
  it("keeps paired texts distinct and recognizes repeated quotes without forcing every occurrence", () => {
    const pair = [{ text: "費用は無料だ。" }, { text: "費用は無料だ。時間は短い。" }];
    const sentences = evidenceSentences(pair);
    expect(sentences[0].id).not.toBe(sentences[1].id);
    expect(compareEvidence(pair, ["費用は無料"], [sentences[1].id]).coversAll).toBe(true);
  });
  it("keeps quoted punctuation inside the surrounding sentence", () => {
    const source = [{ text: "担当者は「来週は『休館です。』と伝えてください。」と話した。次の文です。" }];
    expect(evidenceSentences(source).map((s) => s.text)).toEqual(["担当者は「来週は『休館です。』と伝えてください。」と話した。", "次の文です。"]);
  });
});
