import type { JpVocabWord } from "../types";

// Pure helpers for the 日本語 vocabulary section: the menu's tag + text filter,
// per-tag counts, and splitting an example sentence around the term so the
// flashcard can highlight it. Framework-free so it can be unit-tested.

/** "all", or one of the tag ids from seeds/jp_vocab.json. */
export type VocabTagFilter = string;

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

/** Index of the neighbour `step` places away, wrapping at both ends. */
export function wrapIndex(i: number, step: number, length: number): number {
  if (length <= 0) return -1;
  return (((i + step) % length) + length) % length;
}
