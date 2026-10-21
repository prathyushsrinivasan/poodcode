import { AWS_LESSONS } from "../data/awsMla/lessons";
import { AWS_DOMAINS, type AwsQuestion } from "../data/awsMla/syllabus";
import { todayISO } from "./srs";

export const AWS_PROGRESS_KEY = "aws-mla-c02-progress-v1";
export const AWS_DAY = 86_400_000;
const INTERVALS = [1, 3, 7, 14, 30];
export type AwsTarget = 10 | 15 | 25;
export interface AwsLessonProgress {
  attempts: number;
  streak: number;
  interval: number;
  due: number;
  lastStudied: number;
  lastScore: number;
  note: string;
}
export interface AwsProgress {
  version: 1;
  target: AwsTarget;
  lessons: Record<string, AwsLessonProgress>;
  days: Record<string, { minutes: number; lessons: string[] }>;
}

export const emptyAwsProgress = (): AwsProgress => ({ version: 1, target: 15, lessons: {}, days: {} });
const object = (value: unknown): value is Record<string, unknown> => !!value && typeof value === "object" && !Array.isArray(value);
const nonnegative = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value) && value >= 0;
const integer = (value: unknown): value is number => nonnegative(value) && Number.isSafeInteger(value);

/** Reject malformed state without letting one bad row erase other valid rows. */
export function parseAwsProgress(raw?: string): AwsProgress {
  const result = emptyAwsProgress();
  if (!raw) return result;
  let data: unknown;
  try { data = JSON.parse(raw); } catch { return result; }
  if (!object(data) || data.version !== 1) return result;
  if (data.target === 10 || data.target === 15 || data.target === 25) result.target = data.target;
  const ids = new Set(AWS_LESSONS.map((lesson) => lesson.id));
  if (object(data.lessons)) {
    for (const [id, row] of Object.entries(data.lessons)) {
      if (!ids.has(id) || !object(row) || !integer(row.attempts) || !integer(row.streak)
        || !nonnegative(row.interval) || !nonnegative(row.due) || !nonnegative(row.lastStudied)
        || !nonnegative(row.lastScore) || row.lastScore > 1 || typeof row.note !== "string") continue;
      result.lessons[id] = {
        attempts: row.attempts, streak: row.streak, interval: row.interval, due: row.due,
        lastStudied: row.lastStudied, lastScore: row.lastScore, note: row.note.slice(0, 10_000),
      };
    }
  }
  if (object(data.days)) {
    for (const [day, row] of Object.entries(data.days)) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(day) || !object(row) || !nonnegative(row.minutes) || !Array.isArray(row.lessons)) continue;
      result.days[day] = { minutes: row.minutes, lessons: row.lessons.filter((id): id is string => typeof id === "string" && ids.has(id)) };
    }
  }
  return result;
}

export function gradeAwsQuestion(question: AwsQuestion, picked: number[]): boolean {
  const unique = new Set(picked);
  return unique.size === question.answers.length && picked.length === unique.size
    && question.answers.every((answer) => unique.has(answer));
}

export function awsStatus(row: AwsLessonProgress | undefined, now = Date.now()): "new" | "due" | "learning" | "retained" {
  if (!row?.attempts) return "new";
  if (row.due <= now) return "due";
  return row.streak >= 3 && row.lastScore === 1 ? "retained" : "learning";
}

export function recordAwsAttempt(progress: AwsProgress, id: string, picks: number[][], now = Date.now()): AwsProgress {
  const lesson = AWS_LESSONS.find((item) => item.id === id);
  if (!lesson || picks.length !== lesson.questions.length || picks.some((pick) => pick.length === 0)) return progress;
  const previous = progress.lessons[id];
  const score = lesson.questions.filter((q, i) => gradeAwsQuestion(q, picks[i])).length / lesson.questions.length;
  const passed = score === 1;
  const advances = !previous?.attempts || previous.due <= now;
  const streak = passed ? (previous?.streak ?? 0) + (advances ? 1 : 0) : 0;
  const interval = passed ? (advances ? INTERVALS[Math.min(streak - 1, INTERVALS.length - 1)] : previous!.interval) : 0;
  const due = passed ? (advances ? now + interval * AWS_DAY : previous!.due) : now + 10 * 60_000;
  const day = todayISO(new Date(now));
  const activity = progress.days[day] ?? { minutes: 0, lessons: [] };
  return {
    ...progress,
    lessons: { ...progress.lessons, [id]: {
      attempts: (previous?.attempts ?? 0) + 1, streak, interval, due, lastStudied: now, lastScore: score, note: previous?.note ?? "",
    } },
    days: { ...progress.days, [day]: {
      minutes: activity.minutes + (previous?.attempts ? 3 : 6),
      lessons: [...new Set([...activity.lessons, id])],
    } },
  };
}

export function setAwsNote(progress: AwsProgress, id: string, note: string): AwsProgress {
  if (!AWS_LESSONS.some((lesson) => lesson.id === id)) return progress;
  const previous = progress.lessons[id] ?? { attempts: 0, streak: 0, interval: 0, due: 0, lastStudied: 0, lastScore: 0, note: "" };
  return { ...progress, lessons: { ...progress.lessons, [id]: { ...previous, note: note.slice(0, 10_000) } } };
}

/** The session snapshots these IDs: answering must not extend a running session. */
export function planAwsSession(progress: AwsProgress, now = Date.now()): string[] {
  const available = progress.target - (progress.days[todayISO(new Date(now))]?.minutes ?? 0);
  if (available <= 0) return [];
  const priority = (id: string) => {
    const row = progress.lessons[id];
    const lesson = AWS_LESSONS.find((item) => item.id === id)!;
    const weight = AWS_DOMAINS.find((domain) => domain.id === Number(lesson.task[0]))!.weight;
    return (now - row.due) / AWS_DAY + (1 - row.lastScore) * 3 + weight / 100;
  };
  const due = AWS_LESSONS.filter((lesson) => awsStatus(progress.lessons[lesson.id], now) === "due")
    .sort((a, b) => priority(b.id) - priority(a.id));
  const unseen = AWS_LESSONS.filter((lesson) => !progress.lessons[lesson.id]?.attempts);
  const queue: string[] = [];
  let minutes = available;
  for (const lesson of [...due, ...unseen]) {
    const cost = progress.lessons[lesson.id]?.attempts ? 3 : 6;
    if (cost > minutes) continue;
    queue.push(lesson.id);
    minutes -= cost;
  }
  return queue;
}

export function awsStudyStreak(progress: AwsProgress, now = new Date()): number {
  const cursor = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12);
  if (!progress.days[todayISO(cursor)]?.lessons.length) cursor.setDate(cursor.getDate() - 1);
  let streak = 0;
  while (progress.days[todayISO(cursor)]?.lessons.length) {
    streak++;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}
