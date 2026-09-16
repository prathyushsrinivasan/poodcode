import { describe, it, expect } from "vitest";
import {
  BLANK,
  clozePrompt,
  distractors,
  filterVocab,
  matchesQuery,
  readyWords,
  shuffleWith,
  splitOnTerm,
  stateCounts,
  tagCounts,
  vocabCardId,
  wordState,
  wrapIndex,
} from "./jpVocab";
import type { CardReview, JpVocabWord } from "../types";

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

describe("clozePrompt", () => {
  it("blanks every occurrence of the term", () => {
    expect(clozePrompt("DogはAnimalを継承しています。", "継承")).toBe(
      `DogはAnimalを${BLANK}しています。`
    );
    expect(clozePrompt("木と木", "木")).toBe(`${BLANK}と${BLANK}`);
  });
});

describe("shuffleWith", () => {
  it("keeps every item and leaves the input alone", () => {
    const xs = [1, 2, 3, 4];
    // rand() === 0 sends every swap to index 0 — a fixed, checkable permutation.
    expect(shuffleWith(xs, () => 0).sort()).toEqual([1, 2, 3, 4]);
    expect(xs).toEqual([1, 2, 3, 4]);
  });
});

describe("distractors", () => {
  it("never offers the answer as a wrong option", () => {
    const picked = distractors(all, "hairetsu", 3, () => 0);
    expect(picked.map((w) => w.id)).not.toContain("hairetsu");
    expect(picked).toHaveLength(2); // only two other words exist
  });
});

const review = (wordId: string, dueDate: string, reps = 1): CardReview => ({
  card_id: vocabCardId(wordId),
  ease: 2.5,
  reps,
  lapses: 0,
  interval_days: 3,
  due_date: dueDate,
  last_quality: 2,
});

const reviewMap = (...rs: CardReview[]) => new Map(rs.map((r) => [r.card_id, r]));

describe("wordState", () => {
  it("calls a word never graded new, even if a row exists with no reps", () => {
    expect(wordState(undefined, "2026-06-01")).toBe("new");
    expect(wordState(review("keisho", "2026-06-01", 0), "2026-06-01")).toBe("new");
  });

  it("splits graded words on their due date", () => {
    expect(wordState(review("keisho", "2026-06-01"), "2026-06-01")).toBe("due");
    expect(wordState(review("keisho", "2026-05-20"), "2026-06-01")).toBe("due");
    expect(wordState(review("keisho", "2026-06-02"), "2026-06-01")).toBe("learning");
  });
});

describe("readyWords", () => {
  it("keeps the new and the overdue, and drops what is scheduled ahead", () => {
    const reviews = reviewMap(
      review("keisho", "2026-06-02"), // learning
      review("hairetsu", "2026-05-30") // due
    );
    // kata-hikisu has no review at all, so it is new — and studiable.
    expect(readyWords(all, reviews, "2026-06-01").map((w) => w.id)).toEqual([
      "kata-hikisu",
      "hairetsu",
    ]);
  });
});

describe("stateCounts", () => {
  it("counts each state, with ready spanning new and due", () => {
    const reviews = reviewMap(review("keisho", "2026-06-02"), review("hairetsu", "2026-05-30"));
    expect(stateCounts(all, reviews, "2026-06-01")).toEqual({
      new: 1,
      due: 1,
      learning: 1,
      ready: 2,
    });
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
