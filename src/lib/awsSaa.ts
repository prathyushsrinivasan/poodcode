import { SAA_BY_ID, SAA_QUESTIONS } from "../data/awsSaa/questions";
import type { SaaQuestion } from "../data/awsSaa/schema";
import { hashString } from "./quizShuffle";
import { todayISO } from "./srs";

export const SAA_PROGRESS_KEY = "aws-saa-c03-quizzes-v1";
export const SAA_DAILY_SIZE = 5;
export interface SaaAnswer { selected: number[]; correct: boolean }
export interface SaaDaily { ids: string[]; answers: Record<string, SaaAnswer> }
export interface SaaProgress {
  version: 1;
  questions: Record<string, { attempts: number; correct: number; lastCorrect: boolean; lastAt: number }>;
  days: Record<string, SaaDaily>;
}
export const emptySaaProgress = (): SaaProgress => ({ version: 1, questions: {}, days: {} });
const object = (value: unknown): value is Record<string, unknown> => !!value && typeof value === "object" && !Array.isArray(value);
const integer = (value: unknown): value is number => typeof value === "number" && Number.isSafeInteger(value) && value >= 0;

export function validSaaSelection(question: SaaQuestion, selected: number[]): boolean {
  return selected.length === question.correct.length && new Set(selected).size === selected.length
    && selected.every((index) => integer(index) && index < question.options.length);
}
export function gradeSaa(question: SaaQuestion, selected: number[]): boolean {
  return validSaaSelection(question, selected) && selected.every((index) => question.correct.includes(index));
}
export function parseSaaProgress(raw?: string): SaaProgress {
  const result = emptySaaProgress();
  if (!raw) return result;
  let data: unknown;
  try { data = JSON.parse(raw); } catch { return result; }
  if (!object(data) || data.version !== 1) return result;
  if (object(data.questions)) for (const [id, row] of Object.entries(data.questions)) {
    if (!SAA_BY_ID.has(id) || !object(row) || !integer(row.attempts) || row.attempts < 1
      || !integer(row.correct) || row.correct > row.attempts || typeof row.lastCorrect !== "boolean"
      || !integer(row.lastAt)) continue;
    result.questions[id] = { attempts: row.attempts, correct: row.correct, lastCorrect: row.lastCorrect, lastAt: row.lastAt };
  }
  if (object(data.days)) for (const [day, row] of Object.entries(data.days)) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(day) || !object(row) || !Array.isArray(row.ids) || !object(row.answers)) continue;
    const ids = row.ids.filter((id): id is string => typeof id === "string" && SAA_BY_ID.has(id));
    if (ids.length !== SAA_DAILY_SIZE || new Set(ids).size !== ids.length) continue;
    const answers: SaaDaily["answers"] = {};
    for (const id of ids) {
      const answer = row.answers[id];
      const question = SAA_BY_ID.get(id)!;
      if (!object(answer) || !Array.isArray(answer.selected) || !answer.selected.every(integer)
        || !validSaaSelection(question, answer.selected)) continue;
      answers[id] = { selected: [...answer.selected], correct: gradeSaa(question, answer.selected) };
    }
    result.days[day] = { ids, answers };
  }
  return result;
}

/** Prefer mistakes, then unseen items; diversify topics and freeze the result on first opening. */
export function planSaaDaily(progress: SaaProgress, day: string): string[] {
  if (progress.days[day]) return [...progress.days[day].ids];
  const rank = (id: string) => {
    const row = progress.questions[id];
    return row ? row.lastCorrect ? 2 : 0 : 1;
  };
  const sorted = [...SAA_QUESTIONS].sort((a, b) => rank(a.id) - rank(b.id)
    || (progress.questions[a.id]?.attempts ?? 0) - (progress.questions[b.id]?.attempts ?? 0)
    || (progress.questions[a.id]?.lastAt ?? 0) - (progress.questions[b.id]?.lastAt ?? 0)
    || hashString(`${day}:${a.id}`) - hashString(`${day}:${b.id}`));
  const topics = new Set<string>();
  return sorted.filter((question) => {
    if (topics.has(question.topic)) return false;
    topics.add(question.topic);
    return true;
  }).slice(0, SAA_DAILY_SIZE).map((question) => question.id);
}
export function startSaaDaily(progress: SaaProgress, day: string): SaaProgress {
  if (progress.days[day]) return progress;
  return { ...progress, days: { ...progress.days, [day]: { ids: planSaaDaily(progress, day), answers: {} } } };
}
export function recordSaaAnswer(progress: SaaProgress, id: string, selected: number[], now: number, day?: string): SaaProgress {
  const question = SAA_BY_ID.get(id);
  if (!question || !validSaaSelection(question, selected)) return progress;
  const daily = day ? progress.days[day] : undefined;
  if (day && (!daily || !daily.ids.includes(id) || daily.answers[id])) return progress;
  const correct = gradeSaa(question, selected);
  const previous = progress.questions[id];
  const answer = { selected: [...selected], correct };
  return {
    ...progress,
    questions: { ...progress.questions, [id]: {
      attempts: (previous?.attempts ?? 0) + 1, correct: (previous?.correct ?? 0) + Number(correct), lastCorrect: correct, lastAt: now,
    } },
    days: day && daily ? { ...progress.days, [day]: { ...daily, answers: { ...daily.answers, [id]: answer } } } : progress.days,
  };
}
export function saaMistakes(progress: SaaProgress): string[] {
  return SAA_QUESTIONS.filter((question) => progress.questions[question.id]?.lastCorrect === false).map((question) => question.id);
}
export function saaStreak(progress: SaaProgress, now = new Date()): number {
  const cursor = new Date(now);
  cursor.setHours(12, 0, 0, 0);
  const completed = (day: string) => {
    const daily = progress.days[day];
    return !!daily && daily.ids.every((id) => !!daily.answers[id]);
  };
  if (!completed(todayISO(cursor))) cursor.setDate(cursor.getDate() - 1);
  let count = 0;
  while (completed(todayISO(cursor))) { count++; cursor.setDate(cursor.getDate() - 1); }
  return count;
}
