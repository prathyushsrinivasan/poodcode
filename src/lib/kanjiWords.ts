import { KANJI_WORD_BY_ID, type KanjiWord } from "../data/kanjiWords";
import { optionOrder } from "./quizShuffle";

export type KanjiSkill = "reading" | "meaning";
export interface KanjiResult { attempts: number; correct: number; lastCorrect: boolean }
export type KanjiWordProgress = Partial<Record<KanjiSkill, KanjiResult>>;
export interface KanjiProgress { version: 1; words: Record<string, KanjiWordProgress> }
export const emptyKanjiProgress = (): KanjiProgress => ({ version: 1, words: {} });
export const normalizeHiragana = (value: string) => value.normalize("NFKC").replace(/\s/gu, "");
export const isHiragana = (value: string) => /^[ぁ-ゖー]+$/u.test(normalizeHiragana(value));
export function gradeKanjiReading(word: KanjiWord, value: string): boolean {
  const reading = normalizeHiragana(value);
  return isHiragana(reading) && word.readings.includes(reading);
}
export function validKanjiMeaningSelection(word: KanjiWord, selected: number[]): boolean {
  return selected.length === word.meanings.length && new Set(selected).size === selected.length
    && selected.every((index) => Number.isSafeInteger(index) && index >= 0 && index < word.options.length);
}
export function gradeKanjiMeaning(word: KanjiWord, selected: number[]): boolean {
  return validKanjiMeaningSelection(word, selected) && selected.every((index) => word.options[index].correct);
}
const object = (value: unknown): value is Record<string, unknown> => !!value && typeof value === "object" && !Array.isArray(value);
export function parseKanjiProgress(raw?: string): KanjiProgress {
  const result = emptyKanjiProgress();
  if (!raw) return result;
  let data: unknown;
  try { data = JSON.parse(raw); } catch { return result; }
  if (!object(data) || data.version !== 1 || !object(data.words)) return result;
  for (const [id, word] of Object.entries(data.words)) {
    if (!KANJI_WORD_BY_ID.has(id) || !object(word)) continue;
    const row: KanjiWordProgress = {};
    for (const skill of ["reading", "meaning"] as const) {
      const r = word[skill];
      if (!object(r) || typeof r.attempts !== "number" || !Number.isSafeInteger(r.attempts) || r.attempts < 1
        || typeof r.correct !== "number" || !Number.isSafeInteger(r.correct) || r.correct < 0 || r.correct > r.attempts
        || typeof r.lastCorrect !== "boolean" || (r.lastCorrect && r.correct === 0)) continue;
      row[skill] = { attempts: r.attempts, correct: r.correct, lastCorrect: r.lastCorrect };
    }
    if (Object.keys(row).length) result.words[id] = row;
  }
  return result;
}
export function recordKanjiResult(progress: KanjiProgress, id: string, skill: KanjiSkill, correct: boolean): KanjiProgress {
  if (!KANJI_WORD_BY_ID.has(id)) return progress;
  const old = progress.words[id]?.[skill];
  return { ...progress, words: { ...progress.words, [id]: { ...progress.words[id], [skill]: {
    attempts: (old?.attempts ?? 0) + 1, correct: (old?.correct ?? 0) + Number(correct), lastCorrect: correct,
  } } } };
}
export const kanjiWordComplete = (row?: KanjiWordProgress) => !!row?.reading?.lastCorrect && !!row.meaning?.lastCorrect;
export const kanjiWordNeedsReview = (row?: KanjiWordProgress) => row?.reading?.lastCorrect === false || row?.meaning?.lastCorrect === false;
export function kanjiStats(words: KanjiWord[], progress: KanjiProgress) {
  return {
    total: words.length,
    practiced: words.filter((word) => progress.words[word.id]).length,
    readings: words.filter((word) => progress.words[word.id]?.reading?.lastCorrect).length,
    meanings: words.filter((word) => progress.words[word.id]?.meaning?.lastCorrect).length,
    complete: words.filter((word) => kanjiWordComplete(progress.words[word.id])).length,
    mistakes: words.filter((word) => kanjiWordNeedsReview(progress.words[word.id])).length,
  };
}
/** Snapshot this list in the view; correcting a mistake must not shift the round. */
export function planKanjiRound(words: KanjiWord[], progress: KanjiProgress, size: number, salt: string): string[] {
  const priority = (word: KanjiWord) => kanjiWordNeedsReview(progress.words[word.id]) ? 0
    : !kanjiWordComplete(progress.words[word.id]) ? 1 : 2;
  const shuffled = optionOrder("kanji-word-round", words.length, salt).map((index) => words[index]);
  return shuffled.sort((a, b) => priority(a) - priority(b)).slice(0, size).map((word) => word.id);
}
