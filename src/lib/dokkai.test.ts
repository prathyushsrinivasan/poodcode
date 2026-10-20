import { describe, expect, it } from "vitest";
import { READING_PASSAGES, READING_QUESTIONS, READING_SECTIONS } from "../data/dokkai";
import { COMMON_READING_WORDS } from "../data/dokkai/vocabulary";
import { characterCount, plainReading, readingSegments, readingWords, wordKey } from "./dokkaiText";
import { emptyReadingProgress, filterReadings, latestReadingResult, nextReading, parseReadingProgress, readingStats,
  recordReadingAnswers, reviewReadingWord, readingTimeBudget } from "./dokkai";

describe("authored reading library", () => {
  it("has 100 short and 100 medium passages with stable legacy IDs in all five formats", () => {
    expect(READING_PASSAGES.filter((p) => p.kind === "short")).toHaveLength(100);
    const medium = READING_PASSAGES.filter((p) => p.kind === "medium");
    expect(medium.map((p) => p.id)).toEqual(Array.from({ length: 100 }, (_, i) => `medium-${String(i + 1).padStart(3, "0")}`));
    expect(medium.flatMap((p) => p.questions)).toHaveLength(200);
    expect(READING_PASSAGES).toHaveLength(208);
    expect(READING_QUESTIONS).toHaveLength(318);
    for (const p of medium) expect(p.questions.map((q) => q.id)).toEqual([`${p.id}-q1`, `${p.id}-q2`]);
    expect(new Set(READING_PASSAGES.map((p) => p.id)).size).toBe(READING_PASSAGES.length);
    expect(new Set(READING_PASSAGES.flatMap((p) => p.texts.map((t) => plainReading(t.text)))).size)
      .toBe(READING_PASSAGES.reduce((n, p) => n + p.texts.length, 0));
    for (const s of READING_SECTIONS) expect(READING_PASSAGES.some((p) => p.kind === s.id)).toBe(true);
    expect(new Set(READING_QUESTIONS.map((q) => q.id)).size).toBe(READING_QUESTIONS.length);
  });
  it("keeps all 95 additions within 450–550 plain characters in three translated paragraphs", () => {
    const added = READING_PASSAGES.filter((p) => p.kind === "medium").slice(5);
    expect(added).toHaveLength(95);
    for (const p of added) {
      expect(p.questions.length, p.id).toBeGreaterThanOrEqual(2);
      expect(p.questions.length, p.id).toBeLessThanOrEqual(3);
      expect(p.texts, p.id).toHaveLength(1);
      const text = p.texts[0];
      expect(characterCount(text.text), p.id).toBeGreaterThanOrEqual(450);
      expect(characterCount(text.text), p.id).toBeLessThanOrEqual(550);
      expect(plainReading(text.text).split(/\n\s*\n/), p.id).toHaveLength(3);
      expect(text.translation.match(/\b[A-Za-z]+\b/g)?.length, p.id).toBeGreaterThan(100);
      expect(readingWords(text.text).length, p.id).toBeGreaterThanOrEqual(3);
      expect(readingSegments(text.text, COMMON_READING_WORDS).filter((s) => s.word).length, p.id).toBeGreaterThanOrEqual(30);
      for (const raw of [text.text, ...p.questions.flatMap((q) => [q.prompt, ...q.choices.map((c) => c.text)])]) {
        expect(plainReading(raw), p.id).not.toMatch(/[\[\]|]/u);
        expect(raw, p.id).not.toMatch(/\ufffd/u);
        const segments = readingSegments(raw, COMMON_READING_WORDS);
        expect(segments.map((s) => s.text).join(""), p.id).toBe(plainReading(raw));
        expect(segments.some((s) => s.word), `${p.id}: ${plainReading(raw)}`).toBe(true);
      }
      for (const q of p.questions) for (const quote of q.evidence) {
        expect(quote, q.id).not.toMatch(/[\[\]|]/u);
        expect(readingSegments(text.text, COMMON_READING_WORDS, [quote]).filter((s) => s.evidence).map((s) => s.text).join(""), q.id).toBe(quote);
      }
    }
    expect(new Set(added.map((p) => p.topic)).size).toBeGreaterThanOrEqual(8);
    expect(new Set(added.map((p) => p.skill)).size).toBeGreaterThanOrEqual(6);
    expect(new Set(added.map((p) => p.level))).toEqual(new Set([1, 2, 3]));
  });
  it("rejects reused passage templates by comparing normalized four-character sequences", () => {
    const passages = READING_PASSAGES.filter((p) => p.kind === "medium");
    const grams = passages.map((p) => {
      const text = [...plainReading(p.texts[0].text).replace(/\s/gu, "")];
      return new Set(text.slice(0, -3).map((_, i) => text.slice(i, i + 4).join("")));
    });
    // A substantial shared skeleton fails even if a few names have changed.
    for (let a = 0; a < grams.length; a++) for (let b = a + 1; b < grams.length; b++) {
      const shared = [...grams[a]].filter((s) => grams[b].has(s)).length;
      expect(shared / Math.min(grams[a].size, grams[b].size), `${passages[a].id} / ${passages[b].id}`).toBeLessThan(0.35);
    }
  });
  it("validates readings, meanings and dictionary forms in shared and explicit annotations", () => {
    const raw = READING_PASSAGES.flatMap((p) => [...p.texts.map((t) => t.text), ...p.questions.flatMap((q) => [q.prompt, ...q.choices.map((c) => c.text)])]);
    for (const word of [...COMMON_READING_WORDS, ...raw.flatMap(readingWords)]) {
      expect(word.text.trim()).not.toBe("");
      expect(word.reading, word.text).toMatch(/^[ぁ-ゖァ-ヺー・\s]+$/u);
      expect(word.meaning, word.text).toMatch(/[a-zA-Z]/u);
      if (word.lemma) expect(word.lemma.trim(), word.text).not.toBe("");
    }
  });
  it("keeps passages near their stated character lengths, counting Japanese text rather than markup", () => {
    const limits = { short: [180, 250], medium: [420, 600], ab: [270, 350], long: [900, 1200], information: [600, 800] };
    const outliers = READING_PASSAGES.flatMap((p) => p.texts.map((t) => ({ id: p.id, count: characterCount(t.text), kind: p.kind })))
      .filter((p) => p.count < limits[p.kind][0] || p.count > limits[p.kind][1]);
    expect(outliers).toEqual([]);
  });
  it("provides four explained options, an exact supporting quote and an English translation for every question", () => {
    for (const p of READING_PASSAGES) {
      expect(p.questions.length).toBeGreaterThan(0);
      if (p.kind === "ab") expect(p.texts.map((t) => t.label)).toEqual(["A", "B"]);
      if (p.kind === "short") expect(p.questions).toHaveLength(1);
      for (const text of p.texts) {
        expect(text.translation.length, p.id).toBeGreaterThan(100);
        expect(plainReading(text.text), p.id).not.toMatch(/[\[\]|]/u);
        expect(readingSegments(text.text, COMMON_READING_WORDS).some((s) => s.word), p.id).toBe(true);
      }
      for (const q of p.questions) {
        expect(q.choices, q.id).toHaveLength(4);
        expect(new Set(q.choices.map((c) => c.text)).size, q.id).toBe(4);
        expect(q.answer, q.id).toBeGreaterThanOrEqual(0);
        expect(q.answer, q.id).toBeLessThan(4);
        expect(q.explanation.length, q.id).toBeGreaterThan(30);
        for (const choice of q.choices) expect(choice.explanation.length, q.id).toBeGreaterThan(20);
        expect(q.evidence.length, q.id).toBeGreaterThan(0);
        for (const quote of q.evidence) expect(p.texts.some((t) => plainReading(t.text).includes(quote)), `${q.id}: ${quote}`).toBe(true);
      }
    }
    expect(new Set(READING_QUESTIONS.map((q) => q.answer)).size).toBe(4);
  });
});

describe("reading annotations", () => {
  it("preserves occurrence-specific readings even for identical spellings", () => {
    const text = "[生物|なまもの|perishable food]と[生物|せいぶつ|living things]。";
    const segments = readingSegments(text, [{ text: "生物", reading: "せいぶつ", meaning: "organism" }]);
    expect(segments.filter((s) => s.word).map((s) => s.word?.reading)).toEqual(["なまもの", "せいぶつ"]);
    expect(segments.map((s) => s.text).join("")).toBe("生物と生物。");
    expect(characterCount(text)).toBe(6);
  });
  it("highlights evidence across clickable and plain text without revealing annotation syntax", () => {
    const text = "今日は[延期した|えんきした|postponed|延期する]。明日話す。";
    const segments = readingSegments(text, [], ["今日は延期した。"]);
    expect(segments.filter((s) => s.evidence).map((s) => s.text).join("")).toBe("今日は延期した。");
    expect(readingWords(text)[0].lemma).toBe("延期する");
    expect(segments.map((s) => s.text).join("")).toBe(plainReading(text));
  });
});

describe("separate study and timed progress", () => {
  const p = READING_PASSAGES[0];
  const id = p.questions[0].id;
  it("round-trips new medium results, bookmarks and context-specific saved vocabulary", () => {
    const passage = READING_PASSAGES.find((p) => p.id === "medium-100")!;
    const question = passage.questions[0];
    const word = readingWords(passage.texts[0].text).find((w) => w.lemma)!;
    expect(word).toBeDefined();
    let state = emptyReadingProgress();
    for (const mode of ["independent", "assisted", "timed"] as const) {
      state = recordReadingAnswers(state, [{ id: question.id, correct: mode !== "timed", mode }], 100);
    }
    state.bookmarks.push(passage.id);
    state.words[wordKey(word)] = { ...word, source: passage.id, due: 100, interval: 0, reviews: 0 };
    const restored = parseReadingProgress(JSON.stringify(state));
    expect(restored).toEqual(state);
    expect(filterReadings(READING_PASSAGES, restored, { status: "mistakes", mode: "timed", query: passage.title })).toEqual([passage]);
    expect(filterReadings(READING_PASSAGES, restored, { status: "mistakes", mode: "independent", query: passage.title })).toEqual([]);
    expect(readingTimeBudget([passage])).toBeGreaterThan(180);
  });
  it("keeps assistance separate, and latest-attempt mistakes clear only after a correct attempt", () => {
    let state = recordReadingAnswers(emptyReadingProgress(), [{ id, correct: false, mode: "timed" }], 100);
    state = recordReadingAnswers(state, [{ id, correct: true, mode: "assisted" }], 100);
    expect(readingStats([p], state, "timed").missed).toBe(1);
    expect(readingStats([p], state, "assisted").correct).toBe(1);
    expect(readingStats([p], state, "independent").attempted).toBe(0);
    expect(latestReadingResult(state.results[id])?.lastCorrect).toBe(true);
    expect(filterReadings([p], state, { status: "mistakes" })).toHaveLength(0);
    expect(filterReadings([p], state, { status: "mistakes", mode: "timed" })).toHaveLength(1);
    state = recordReadingAnswers(state, [{ id, correct: false, mode: "independent" }], 101);
    expect(filterReadings([p], state, { status: "mistakes" })).toHaveLength(1);
    expect(parseReadingProgress(JSON.stringify(state))).toEqual(state);
  });
  it("continues at unattempted passages and combines bookmarks with topic and skill filters", () => {
    const passages = READING_PASSAGES.slice(0, 3);
    const state = recordReadingAnswers(emptyReadingProgress(), [{ id, correct: false, mode: "independent" }]);
    state.bookmarks.push(p.id);
    expect(nextReading(passages, state)?.id).toBe(passages[1].id);
    expect(filterReadings(passages, state, { status: "bookmarks", topic: p.topic, skill: p.skill }).map((x) => x.id)).toEqual([p.id]);
    expect(filterReadings(passages, state, { status: "unattempted" }).map((x) => x.id)).not.toContain(p.id);
  });
  it("recovers from malformed backups without counting invalid attempts or unknown passages", () => {
    for (const raw of ["bad", "null", "[]", "42"]) expect(parseReadingProgress(raw)).toEqual(emptyReadingProgress());
    const result = { attempts: 1, correct: 2, lastCorrect: true, at: 0 };
    expect(parseReadingProgress(JSON.stringify({ results: { [id]: { timed: result }, unknown: { timed: result } },
      bookmarks: [p.id, p.id, "unknown", 42], words: { bad: { text: "bad" } } })))
      .toEqual({ ...emptyReadingProgress(), bookmarks: [p.id] });
  });
  it("schedules forgotten vocabulary sooner while increasing remembered intervals", () => {
    const word = { text: "延期", reading: "えんき", meaning: "postponement", source: p.id, due: 0, interval: 0, reviews: 0 };
    const first = reviewReadingWord(word, true, 1000);
    const second = reviewReadingWord(first, true, 1000);
    const again = reviewReadingWord(second, false, 1000);
    expect(first.interval).toBe(1); expect(second.interval).toBe(2);
    expect(again.due).toBe(601000); expect(again.reviews).toBe(3);
    const progress = { ...emptyReadingProgress(), words: { [wordKey(first)]: first } };
    expect(parseReadingProgress(JSON.stringify(progress))).toEqual(progress);
  });
});
