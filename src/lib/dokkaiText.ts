import type { ReadingWord } from "../data/dokkai/types";

// Explicit, occurrence-specific glosses: [surface|kana|contextual meaning|lemma].
// The optional dictionary form never replaces the actual surface in the text.
const MARKUP = /\[([^\[\]|]+)\|([^\[\]|]+)\|([^\[\]|]+)(?:\|([^\[\]|]+))?\]/gu;
export interface ReadingSegment { text: string; word?: ReadingWord; evidence: boolean }
export function plainReading(text: string): string { return text.replace(MARKUP, "$1"); }
export function readingWords(text: string): ReadingWord[] {
  return [...text.matchAll(MARKUP)].map((m) => ({ text: m[1], reading: m[2], meaning: m[3], ...(m[4] ? { lemma: m[4] } : {}) }));
}
export function wordKey(word: ReadingWord): string { return `${word.lemma ?? word.text}|${word.reading}|${word.meaning}`; }

/** Explicit markup wins; fallback vocabulary only uses curated, unambiguous
 * surfaces. Split evidence boundaries too, so both plain text and word buttons
 * inside the supporting sentence receive the highlight. */
export function readingSegments(text: string, vocabulary: ReadingWord[] = [], evidence: string[] = []): ReadingSegment[] {
  const plain = plainReading(text);
  const ranges: { start: number; end: number; word: ReadingWord }[] = [];
  let removed = 0;
  for (const m of text.matchAll(MARKUP)) {
    const start = m.index - removed;
    ranges.push({ start, end: start + m[1].length, word: readingWords(m[0])[0] });
    removed += m[0].length - m[1].length;
  }
  const candidates = [...vocabulary].sort((a, b) => b.text.length - a.text.length);
  for (let at = 0; at < plain.length;) {
    const explicit = ranges.find((r) => r.start <= at && r.end > at);
    if (explicit) { at = explicit.end; continue; }
    const word = candidates.find((w) => w.text && plain.startsWith(w.text, at) &&
      !ranges.some((r) => r.start < at + w.text.length && r.end > at));
    if (word) { ranges.push({ start: at, end: at + word.text.length, word }); at += word.text.length; }
    else at++;
  }
  const highlights = evidence.flatMap((quote) => {
    const found: { start: number; end: number }[] = [];
    if (!quote) return found;
    for (let at = plain.indexOf(quote); at >= 0; at = plain.indexOf(quote, at + quote.length)) found.push({ start: at, end: at + quote.length });
    return found;
  });
  const points = [...new Set([0, plain.length, ...ranges.flatMap((r) => [r.start, r.end]), ...highlights.flatMap((r) => [r.start, r.end])])].sort((a, b) => a - b);
  return points.slice(0, -1).map((start, i) => ({ text: plain.slice(start, points[i + 1]),
    word: ranges.find((r) => r.start <= start && r.end >= points[i + 1])?.word,
    evidence: highlights.some((r) => r.start <= start && r.end >= points[i + 1]) }));
}
export function characterCount(text: string): number { return [...plainReading(text).replace(/\s/gu, "")].length; }
