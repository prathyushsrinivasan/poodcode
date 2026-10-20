import { READING_PASSAGES, READING_QUESTIONS } from "../data/dokkai";
import type { ReadingPassage, ReadingWord } from "../data/dokkai/types";
import { characterCount, wordKey } from "./dokkaiText";

export const READING_PROGRESS_KEY = "jlpt-n2-reading-v1";
export type ReadingMode = "independent" | "assisted" | "timed";
export interface ReadingResult { attempts: number; correct: number; lastCorrect: boolean; at: number }
export type QuestionHistory = Partial<Record<ReadingMode, ReadingResult>>;
export interface SavedReadingWord extends ReadingWord { source: string; due: number; interval: number; reviews: number }
export interface ReadingProgress {
  results: Record<string, QuestionHistory>;
  bookmarks: string[];
  words: Record<string, SavedReadingWord>;
}
export function emptyReadingProgress(): ReadingProgress { return { results: {}, bookmarks: [], words: {} }; }
const isObject = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);
const natural = (v: unknown): v is number => typeof v === "number" && Number.isSafeInteger(v) && v >= 0;
const MODES: ReadingMode[] = ["independent", "assisted", "timed"];
export function parseReadingProgress(raw?: string): ReadingProgress {
  const out = emptyReadingProgress();
  if (!raw) return out;
  let parsed: unknown;
  try { parsed = JSON.parse(raw); } catch { return out; }
  if (!isObject(parsed)) return out;
  const passageIds = new Set(READING_PASSAGES.map((p) => p.id));
  if (isObject(parsed.results)) for (const q of READING_QUESTIONS) {
    const history = parsed.results[q.id];
    if (!isObject(history)) continue;
    const valid: QuestionHistory = {};
    for (const mode of MODES) {
      const row = history[mode];
      if (isObject(row) && natural(row.attempts) && row.attempts > 0 && natural(row.correct) && row.correct <= row.attempts &&
        typeof row.lastCorrect === "boolean" && natural(row.at) && (!row.lastCorrect || row.correct > 0) &&
        (row.lastCorrect || row.correct < row.attempts)) valid[mode] = row as unknown as ReadingResult;
    }
    if (Object.keys(valid).length) out.results[q.id] = valid;
  }
  if (Array.isArray(parsed.bookmarks)) out.bookmarks = [...new Set(parsed.bookmarks.filter((id): id is string => typeof id === "string" && passageIds.has(id)))];
  if (isObject(parsed.words)) for (const [key, row] of Object.entries(parsed.words)) {
    if (!isObject(row) || typeof row.text !== "string" || !row.text || row.text.length > 100 ||
      typeof row.reading !== "string" || !/^[ぁ-ゖァ-ヺー・\s]+$/u.test(row.reading) ||
      typeof row.meaning !== "string" || !row.meaning || row.meaning.length > 500 ||
      (row.lemma !== undefined && typeof row.lemma !== "string") ||
      typeof row.source !== "string" || !passageIds.has(row.source) || !natural(row.due) || !natural(row.interval) ||
      row.interval > 365 || !natural(row.reviews)) continue;
    const word = row as unknown as SavedReadingWord;
    if (key === wordKey(word)) out.words[key] = word;
  }
  return out;
}
export function latestReadingResult(history?: QuestionHistory): ReadingResult | undefined {
  return Object.values(history ?? {}).sort((a, b) => b.at - a.at)[0];
}
export function recordReadingAnswers(progress: ReadingProgress, answers: { id: string; correct: boolean; mode: ReadingMode }[], now = Date.now()): ReadingProgress {
  const results = { ...progress.results };
  for (const item of answers) {
    const history = results[item.id] ?? {};
    const before = history[item.mode];
    // Monotonic per-question stamps make latest-attempt review deterministic
    // even when multiple modes are recorded during the same millisecond.
    const at = Math.max(now, (latestReadingResult(history)?.at ?? 0) + 1);
    results[item.id] = { ...history, [item.mode]: { attempts: (before?.attempts ?? 0) + 1,
      correct: (before?.correct ?? 0) + Number(item.correct), lastCorrect: item.correct, at } };
  }
  return { ...progress, results };
}
export function readingStats(passages: ReadingPassage[], progress: ReadingProgress, mode?: ReadingMode) {
  const results = passages.flatMap((p) => p.questions).map((q) => mode ? progress.results[q.id]?.[mode] : latestReadingResult(progress.results[q.id]));
  return { total: results.length, attempted: results.filter(Boolean).length,
    correct: results.filter((r) => r?.lastCorrect).length, missed: results.filter((r) => r && !r.lastCorrect).length };
}
export type ReadingStatus = "all" | "unattempted" | "mistakes" | "bookmarks";
export function filterReadings(passages: ReadingPassage[], progress: ReadingProgress, filter: {
  query?: string; topic?: string; skill?: string; level?: string; status?: ReadingStatus; mode?: ReadingMode;
}): ReadingPassage[] {
  const query = (filter.query ?? "").trim().toLocaleLowerCase();
  return passages.filter((p) => (!query || `${p.title} ${p.topic} ${p.texts.map((t) => t.text).join(" ")}`.toLocaleLowerCase().includes(query)) &&
    (!filter.topic || p.topic === filter.topic) && (!filter.skill || p.skill === filter.skill) && (!filter.level || p.level === Number(filter.level)) &&
    (filter.status !== "bookmarks" || progress.bookmarks.includes(p.id)) &&
    (filter.status !== "unattempted" || p.questions.some((q) => !(filter.mode ? progress.results[q.id]?.[filter.mode] : latestReadingResult(progress.results[q.id])))) &&
    (filter.status !== "mistakes" || p.questions.some((q) => { const r = filter.mode ? progress.results[q.id]?.[filter.mode] : latestReadingResult(progress.results[q.id]); return r && !r.lastCorrect; })));
}
export function nextReading(passages: ReadingPassage[], progress: ReadingProgress): ReadingPassage | undefined {
  return passages.find((p) => p.questions.some((q) => !latestReadingResult(progress.results[q.id]))) ??
    passages.find((p) => p.questions.some((q) => latestReadingResult(progress.results[q.id])?.lastCorrect === false)) ?? passages[0];
}
export function readingTimeBudget(passages: ReadingPassage[]): number {
  // Practice guidance, not an official JLPT limit: allow reading plus each question.
  return passages.reduce((seconds, p) => seconds + Math.max(90, Math.ceil(p.texts.reduce((n, t) => n + characterCount(t.text), 0) / 3) + p.questions.length * 45), 0);
}
export function reviewReadingWord(word: SavedReadingWord, remembered: boolean, now = Date.now()): SavedReadingWord {
  const interval = remembered ? Math.min(365, word.interval ? word.interval * 2 : 1) : 0;
  return { ...word, reviews: word.reviews + 1, interval, due: now + (remembered ? interval * 86_400_000 : 600_000) };
}
