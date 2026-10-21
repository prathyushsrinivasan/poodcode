import { describe, expect, it } from "vitest";
import { KANJI_GROUPS, KANJI_WORDS, KANJI_WORD_BY_ID, wordsForKanji } from "../data/kanjiWords";
import { emptyKanjiProgress, gradeKanjiMeaning, gradeKanjiReading, isHiragana, kanjiStats, kanjiWordComplete,
  kanjiWordNeedsReview, parseKanjiProgress, planKanjiRound, recordKanjiResult, validKanjiMeaningSelection } from "./kanjiWords";
import { optionOrder } from "./quizShuffle";

const find = (written: string, reading?: string) => KANJI_WORDS.find((word) => word.written === written && (!reading || word.readings.includes(reading)))!;

describe("kanji vocabulary content", () => {
  it("ships twenty substantial kanji families and over seven hundred unique verified entries", () => {
    expect(KANJI_GROUPS).toHaveLength(20);
    expect(new Set(KANJI_GROUPS.map((group) => group.kanji)).size).toBe(20);
    expect(KANJI_WORDS.length).toBeGreaterThanOrEqual(700);
    expect(KANJI_WORD_BY_ID.size).toBe(KANJI_WORDS.length);
    expect(new Set(KANJI_WORDS.map((word) => `${word.written}|${word.readings[0]}`)).size).toBe(KANJI_WORDS.length);
    for (const group of KANJI_GROUPS) expect(wordsForKanji(group.kanji).length).toBeGreaterThanOrEqual(25);
    expect(KANJI_WORDS.filter((word) => word.meanings.length > 1).length).toBeGreaterThanOrEqual(70);
  });
  it("has hiragana readings, complete feedback and consistent shuffled answers for every entry", () => {
    const positions = new Set<number>();
    for (const word of KANJI_WORDS) {
      expect(KANJI_GROUPS.some((group) => word.written.includes(group.kanji))).toBe(true);
      expect(word.dictionaryIds.length).toBeGreaterThan(0);
      expect(word.dictionaryIds.every((id) => /^\d+$/.test(id))).toBe(true);
      expect(word.readings.length).toBeGreaterThan(0);
      expect(new Set(word.readings).size).toBe(word.readings.length);
      for (const reading of word.readings) {
        expect(isHiragana(reading)).toBe(true);
        expect(gradeKanjiReading(word, reading)).toBe(true);
      }
      expect(word.levels.every((level) => ["N3", "N2", "N1"].includes(level))).toBe(true);
      expect(word.options).toHaveLength(word.meanings.length + 3);
      expect(new Set(word.options.map((option) => option.text)).size).toBe(word.options.length);
      expect(word.options.every((option) => option.text.trim().length > 0 && option.explanation.length > 20)).toBe(true);
      const correct = word.options.flatMap((option, index) => option.correct ? [index] : []);
      expect(correct).toHaveLength(word.meanings.length);
      expect(gradeKanjiMeaning(word, correct)).toBe(true);
      expect(gradeKanjiMeaning(word, [...correct.slice(1), word.options.length - 1])).toBe(false);
      positions.add(optionOrder(word.id, word.options.length, "test").indexOf(correct[0]));
    }
    expect(positions.size).toBeGreaterThanOrEqual(4);
  });
  it("gives context to every homograph with a distinct reading and meaning", () => {
    for (const word of KANJI_WORDS) {
      if (KANJI_WORDS.some((other) => other.id !== word.id && other.written === word.written)) expect(word.cue.length).toBeGreaterThan(0);
    }
    expect(find("人気", "にんき").id).not.toBe(find("人気", "ひとけ").id);
    expect(find("分別", "ぶんべつ").cue).toContain("ごみ");
    expect(find("表", "おもて").meanings).not.toEqual(find("表", "ひょう").meanings);
  });
});

describe("typed hiragana", () => {
  it("normalizes spacing and combining marks while preserving kana distinctions", () => {
    const word = find("学会");
    expect(gradeKanjiReading(word, " がっかい　")).toBe(true);
    expect(gradeKanjiReading(word, "か\u3099っかい")).toBe(true);
    expect(gradeKanjiReading(word, "がつかい")).toBe(false);
    expect(gradeKanjiReading(word, "ガッカイ")).toBe(false);
    expect(gradeKanjiReading(word, "gakkai")).toBe(false);
    expect(gradeKanjiReading(word, "学会")).toBe(false);
    expect(gradeKanjiReading(word, "")).toBe(false);
    expect(gradeKanjiReading(find("心強い"), "こころずよい")).toBe(false);
    expect(gradeKanjiReading(find("心強い"), "こころづよい")).toBe(true);
  });
  it("accepts reviewed alternate readings without mixing up homograph senses", () => {
    expect(gradeKanjiReading(find("行き"), "いき")).toBe(true);
    expect(gradeKanjiReading(find("行き"), "ゆき")).toBe(true);
    expect(gradeKanjiReading(find("出生"), "しゅっしょう")).toBe(true);
    expect(gradeKanjiReading(find("人気", "にんき"), "ひとけ")).toBe(false);
    expect(gradeKanjiReading(find("分別", "ぶんべつ"), "ふんべつ")).toBe(false);
  });
});

describe("meaning selection", () => {
  it("requires the exact set, rejecting missing, extra, duplicate and invalid indices", () => {
    const word = find("生地", "きじ");
    expect(word.meanings).toHaveLength(2);
    expect(gradeKanjiMeaning(word, [1, 0])).toBe(true);
    for (const selected of [[], [0], [0, 1, 2], [0, 0], [0, -1], [0, 0.5], [0, 99]]) {
      expect(validKanjiMeaningSelection(word, selected)).toBe(false);
      expect(gradeKanjiMeaning(word, selected)).toBe(false);
    }
    expect(validKanjiMeaningSelection(word, [0, 2])).toBe(true);
    expect(gradeKanjiMeaning(word, [0, 2])).toBe(false);
  });
});

describe("kanji study progress", () => {
  it("tracks reading and meaning independently, and counts shared words once", () => {
    const word = find("生産性");
    let progress = recordKanjiResult(emptyKanjiProgress(), word.id, "reading", true);
    expect(kanjiWordComplete(progress.words[word.id])).toBe(false);
    progress = recordKanjiResult(progress, word.id, "meaning", false);
    expect(kanjiWordNeedsReview(progress.words[word.id])).toBe(true);
    progress = recordKanjiResult(progress, word.id, "meaning", true);
    expect(progress.words[word.id].reading?.attempts).toBe(1);
    expect(progress.words[word.id].meaning).toEqual({ attempts: 2, correct: 1, lastCorrect: true });
    expect(kanjiWordComplete(progress.words[word.id])).toBe(true);
    expect(kanjiWordNeedsReview(progress.words[word.id])).toBe(false);
    expect(kanjiStats(KANJI_WORDS, progress).complete).toBe(1);
    expect(kanjiStats(wordsForKanji("生"), progress).complete).toBe(1);
    expect(kanjiStats(wordsForKanji("性"), progress).complete).toBe(1);
    expect(recordKanjiResult(progress, "unknown", "reading", true)).toBe(progress);
  });
  it("round-trips partial progress and rejects corrupt counters without discarding valid skills", () => {
    const word = KANJI_WORDS[0];
    const partial = recordKanjiResult(emptyKanjiProgress(), word.id, "reading", true);
    expect(parseKanjiProgress(JSON.stringify(partial))).toEqual(partial);
    expect(parseKanjiProgress("broken JSON")).toEqual(emptyKanjiProgress());
    expect(parseKanjiProgress('{"version":2,"words":{}}')).toEqual(emptyKanjiProgress());
    const corrupt = { ...partial, words: { ...partial.words, [word.id]: { ...partial.words[word.id],
      meaning: { attempts: 1, correct: 0, lastCorrect: true } }, unknown: { reading: { attempts: 10, correct: 10, lastCorrect: true } } } };
    expect(parseKanjiProgress(JSON.stringify(corrupt))).toEqual(partial);
  });
  it("plans distinct words with mistakes first and keeps a captured round stable as review results change", () => {
    const word = KANJI_WORDS[0];
    let progress = recordKanjiResult(emptyKanjiProgress(), word.id, "reading", false);
    const ids = planKanjiRound(KANJI_WORDS, progress, 10, "round");
    expect(ids).toHaveLength(10);
    expect(new Set(ids).size).toBe(10);
    expect(ids[0]).toBe(word.id);
    expect(planKanjiRound(KANJI_WORDS, progress, 10, "round")).toEqual(ids);
    progress = recordKanjiResult(progress, word.id, "reading", true);
    expect(ids[0]).toBe(word.id);
    expect(planKanjiRound([], progress, 10, "round")).toEqual([]);
    expect(planKanjiRound([word], progress, 10, "round")).toEqual([word.id]);
  });
});
