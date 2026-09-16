import type { CardReview, JpVocabWord } from "../types";
import { isCardDue } from "./srs";

// Pure helpers for the 日本語 vocabulary section: the menu's tag + text filter,
// per-tag counts, splitting an example sentence around the term so the
// flashcard can highlight it, and where each word sits in its review schedule.
// Framework-free so it can be unit-tested.

/** "all", or one of the tag ids from seeds/jp_vocab.json. */
export type VocabTagFilter = string;

/** The deck every vocabulary review is filed under. Never change it — the
 * `card_reviews` rows in SQLite are keyed by the id it builds. */
export const VOCAB_DECK = "jp-vocab";

/** `jp-vocab#hairetsu` — the same `<deck>#<front>` shape `learnProgress.cardId`
 * builds for glossary cards, kept here so this module stays dependency-free. */
export function vocabCardId(wordId: string): string {
  return `${VOCAB_DECK}#${wordId}`;
}

/** Lowercase and fold rōmaji long-vowel marks, so "hensu" finds "hensū". */
export function foldLatin(s: string): string {
  return s
    .toLowerCase()
    .replace(/[āáàâ]/g, "a")
    .replace(/[īíìî]/g, "i")
    .replace(/[ūúùû]/g, "u")
    .replace(/[ēéèê]/g, "e")
    .replace(/[ōóòô]/g, "o");
}

/** Does a word match free-text search? Checks the term, its hiragana reading,
 * its rōmaji (with or without macrons and spaces) and the English meaning. */
export function matchesQuery(w: JpVocabWord, query: string): boolean {
  const q = foldLatin(query.trim());
  if (!q) return true;
  const squash = (s: string) => s.replace(/[\s'-]/g, "");
  return (
    w.term.includes(q) ||
    w.reading.includes(q) ||
    squash(foldLatin(w.romaji)).includes(squash(q)) ||
    foldLatin(w.meaning).includes(q)
  );
}

/** The words the menu shows for a tag filter and a search string, in seed order. */
export function filterVocab(
  words: JpVocabWord[],
  tag: VocabTagFilter,
  query: string
): JpVocabWord[] {
  return words.filter((w) => (tag === "all" || w.tag === tag) && matchesQuery(w, query));
}

/** How many words carry each tag, plus an "all" total. */
export function tagCounts(words: JpVocabWord[]): Record<string, number> {
  const out: Record<string, number> = { all: words.length };
  for (const w of words) out[w.tag] = (out[w.tag] ?? 0) + 1;
  return out;
}

/** Split a sentence around every occurrence of `term`, marking which pieces are
 * the term. The generator guarantees the term appears at least once. */
export function splitOnTerm(sentence: string, term: string): { text: string; hit: boolean }[] {
  if (!term) return [{ text: sentence, hit: false }];
  const parts: { text: string; hit: boolean }[] = [];
  const pieces = sentence.split(term);
  pieces.forEach((p, i) => {
    if (p) parts.push({ text: p, hit: false });
    if (i < pieces.length - 1) parts.push({ text: term, hit: true });
  });
  return parts;
}

/* ------------------------------------------------------------ study modes */

/** What a cloze prompt puts where the term was. */
export const BLANK = "＿＿＿";

/** The example sentence with every occurrence of the term blanked out. The
 * generator guarantees the term appears in it, so every word supports cloze. */
export function clozePrompt(sentence: string, term: string): string {
  return splitOnTerm(sentence, term)
    .map((p) => (p.hit ? BLANK : p.text))
    .join("");
}

/** Fisher-Yates with an injectable source of randomness, so the UI can shuffle
 * and a test can assert. */
export function shuffleWith<T>(xs: T[], rand: () => number = Math.random): T[] {
  const a = [...xs];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/** Up to `n` other words, to sit beside the answer as the wrong options. */
export function distractors(
  words: JpVocabWord[],
  answerId: string,
  n: number,
  rand: () => number = Math.random
): JpVocabWord[] {
  return shuffleWith(
    words.filter((w) => w.id !== answerId),
    rand
  ).slice(0, n);
}

/** Index of the neighbour `step` places away, wrapping at both ends. */
export function wrapIndex(i: number, step: number, length: number): number {
  if (length <= 0) return -1;
  return (((i + step) % length) + length) % length;
}

/* ------------------------------------------------------- review scheduling */

/** Where a word sits in its cycle: never graded, graded and ready again, or
 * graded and scheduled for a later day. */
export type VocabState = "new" | "due" | "learning";

export function wordState(review: CardReview | undefined, today: string): VocabState {
  if (!review || review.reps <= 0) return "new";
  return isCardDue(review, today) ? "due" : "learning";
}

/** The words that can be studied right now — never seen, or scheduled for today
 * or earlier. The same pool `CardStudy` draws from for the glossary sets. */
export function readyWords(
  words: JpVocabWord[],
  reviews: Map<string, CardReview>,
  today: string
): JpVocabWord[] {
  return words.filter((w) => isCardDue(reviews.get(vocabCardId(w.id)), today));
}

/** How many words sit in each state, plus `ready` (new + due) for the Due chip. */
export function stateCounts(
  words: JpVocabWord[],
  reviews: Map<string, CardReview>,
  today: string
): Record<VocabState, number> & { ready: number } {
  const out = { new: 0, due: 0, learning: 0, ready: 0 };
  for (const w of words) {
    const s = wordState(reviews.get(vocabCardId(w.id)), today);
    out[s]++;
    if (s !== "learning") out.ready++;
  }
  return out;
}
