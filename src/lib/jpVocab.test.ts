import { describe, it, expect } from "vitest";
import { filterVocab, matchesQuery, splitOnTerm, tagCounts, wrapIndex } from "./jpVocab";
import type { JpVocabWord } from "../types";

const word = (over: Partial<JpVocabWord>): JpVocabWord => ({
  id: "x",
  term: "",
  reading: "",
  romaji: "",
  tag: "java",
  meaning: "",
  desc_en: "",
  desc_ja: "",
  example_ja: "",
  example_en: "",
  ...over,
});

const inherit = word({ id: "keisho", term: "継承", reading: "けいしょう", romaji: "keishō", tag: "java", meaning: "inheritance" });
const typeArg = word({ id: "kata-hikisu", term: "型引数", reading: "かたひきすう", romaji: "kata hikisū", tag: "typescript", meaning: "type argument" });
const array = word({ id: "hairetsu", term: "配列", reading: "はいれつ", romaji: "hairetsu", tag: "problems", meaning: "array" });
const all = [inherit, typeArg, array];

describe("matchesQuery", () => {
  it("matches on the term, the reading and the English meaning", () => {
    expect(matchesQuery(inherit, "継承")).toBe(true);
    expect(matchesQuery(inherit, "けいしょう")).toBe(true);
    expect(matchesQuery(inherit, "INHERIT")).toBe(true);
  });

  it("finds rōmaji typed without macrons or spaces", () => {
    expect(matchesQuery(typeArg, "hikisu")).toBe(true);
    expect(matchesQuery(typeArg, "katahikisu")).toBe(true);
    expect(matchesQuery(typeArg, "kata hikisū")).toBe(true);
  });

  it("treats a blank query as matching everything", () => {
    expect(matchesQuery(array, "   ")).toBe(true);
  });
});

describe("filterVocab", () => {
  it("narrows by tag and keeps seed order", () => {
    expect(filterVocab(all, "all", "").map((w) => w.id)).toEqual(["keisho", "kata-hikisu", "hairetsu"]);
    expect(filterVocab(all, "problems", "").map((w) => w.id)).toEqual(["hairetsu"]);
  });

  it("applies the tag and the search together", () => {
    expect(filterVocab(all, "java", "array")).toEqual([]);
    expect(filterVocab(all, "typescript", "type").map((w) => w.id)).toEqual(["kata-hikisu"]);
  });
});

describe("tagCounts", () => {
  it("counts each tag and the total", () => {
    expect(tagCounts(all)).toEqual({ all: 3, java: 1, typescript: 1, problems: 1 });
  });
});

describe("splitOnTerm", () => {
  it("marks the term inside a sentence", () => {
    expect(splitOnTerm("DogはAnimalを継承しています。", "継承")).toEqual([
      { text: "DogはAnimalを", hit: false },
      { text: "継承", hit: true },
      { text: "しています。", hit: false },
    ]);
  });

  it("handles the term at the edges and more than once", () => {
    expect(splitOnTerm("木と木", "木")).toEqual([
      { text: "木", hit: true },
      { text: "と", hit: false },
      { text: "木", hit: true },
    ]);
  });
});

describe("wrapIndex", () => {
  it("wraps forwards and backwards", () => {
    expect(wrapIndex(2, 1, 3)).toBe(0);
    expect(wrapIndex(0, -1, 3)).toBe(2);
    expect(wrapIndex(1, 1, 3)).toBe(2);
  });

  it("has no neighbour in an empty list", () => {
    expect(wrapIndex(0, 1, 0)).toBe(-1);
  });
});
