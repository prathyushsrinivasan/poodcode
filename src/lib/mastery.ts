// Progress, gating and pacing for the 6-Month Mastery programme.
//
// The curriculum is read-only content from seeds/mastery.json. Progress lives
// in SQLite (`mastery_progress`), so it survives backup/restore — see
// api.masteryProgress and friends. This module holds the pure logic that
// decides what is unlocked and how far behind schedule you are, which is what
// mastery.test.ts covers.
//
// Unlock rule: week 1 is always open; week N opens once week N-1 is complete.
// A week is complete when every one of its chapters is marked done, its
// multiple-choice exam has been passed at the track's pass mark, AND its coding
// final has been accepted by the judge. Multiple choice alone is far too weak a
// gate for a programming curriculum.

import { api } from "../api";
import type { MasteryProgress, MasteryTrack, MasteryWeek } from "../types";

/** Progress rows keyed by week number, for one track. */
export type ProgressMap = Map<number, MasteryProgress>;

const LEGACY_QUIZ_KEY = "poodcode:mastery-quiz"; // pre-SQLite { "track:week": pct }
const QUIZ_MIGRATED_KEY = "poodcode:mastery-quiz-migrated";

/** Move any exam scores left in localStorage into SQLite, once. Best-effort:
 * the backend keeps only the better of the two, so re-running is harmless. */
export async function migrateLegacyQuizScores(): Promise<void> {
  if (localStorage.getItem(QUIZ_MIGRATED_KEY) === "1") return;
  let entries: [string, unknown][] = [];
  try {
    const raw = JSON.parse(localStorage.getItem(LEGACY_QUIZ_KEY) || "{}");
    entries = raw && typeof raw === "object" ? Object.entries(raw) : [];
  } catch {
    entries = [];
  }
  for (const [key, percent] of entries) {
    const sep = key.lastIndexOf(":");
    const trackKey = key.slice(0, sep);
    const week = Number(key.slice(sep + 1));
    if (!trackKey || !Number.isInteger(week) || typeof percent !== "number") continue;
    await api.masteryRecordQuiz(trackKey, week, percent);
  }
  localStorage.setItem(QUIZ_MIGRATED_KEY, "1");
}

export function progressByWeek(
  rows: MasteryProgress[],
  trackKey: string
): ProgressMap {
  const map: ProgressMap = new Map();
  for (const row of rows) {
    if (row.track_key === trackKey) map.set(row.week, row);
  }
  return map;
}

export interface WeekProgress {
  /** Chapters marked done in the Learn tab, out of the week's total. */
  conceptsDone: number;
  conceptsTotal: number;
  /** Curated problems already solved. Encouraged, but not part of the gate —
   * you may legitimately have solved them in another language or track. */
  problemsSolved: number;
  problemsTotal: number;
  /** Best multiple-choice score so far, or null if never attempted. */
  score: number | null;
  quizPassed: boolean;
  /** Whether the judge has accepted the week's coding final. */
  examPassed: boolean;
  projectDone: boolean;
  studySeconds: number;
  /** Chapters + quiz + coding final. This is what gates the next week. */
  complete: boolean;
  /** 0–100 across every strand, for the progress bar. */
  percent: number;
}

export function weekProgress(
  week: MasteryWeek,
  track: MasteryTrack,
  doneChapters: Set<string>,
  solvedSlugs: Set<string>,
  progress: ProgressMap
): WeekProgress {
  const row = progress.get(week.week);
  const conceptsTotal = week.concepts.length;
  const conceptsDone = week.concepts.filter((k) => doneChapters.has(k)).length;
  const problemsTotal = week.problems.length;
  const problemsSolved = week.problems.filter((p) => solvedSlugs.has(p.slug)).length;

  const best = row?.best_quiz ?? -1;
  const score = best < 0 ? null : best;
  const quizPassed = score !== null && score >= track.pass_mark;
  const examPassed = row?.exam_passed ?? false;
  const projectDone = row?.project_done ?? false;

  // A consolidation week schedules no new chapters, so "all chapters done" is
  // vacuously true there and the two exams alone carry it.
  const complete = conceptsDone === conceptsTotal && quizPassed && examPassed;

  // Equally-weighted strands, skipping any this week does not have. The project
  // counts toward the bar but never toward the gate — it is unverifiable.
  const strands: number[] = [];
  if (conceptsTotal > 0) strands.push(conceptsDone / conceptsTotal);
  if (problemsTotal > 0) strands.push(problemsSolved / problemsTotal);
  strands.push(quizPassed ? 1 : 0);
  if (week.exam) strands.push(examPassed ? 1 : 0);
  if (week.project) strands.push(projectDone ? 1 : 0);
  const percent = Math.round(
    (strands.reduce((a, b) => a + b, 0) / strands.length) * 100
  );

  return {
    conceptsDone,
    conceptsTotal,
    problemsSolved,
    problemsTotal,
    score,
    quizPassed,
    examPassed,
    projectDone,
    studySeconds: row?.study_seconds ?? 0,
    complete,
    percent,
  };
}

/** Which weeks are readable. Week 1 always is; each later week opens when its
 * predecessor is complete. Returns a set of week numbers. */
export function unlockedWeeks(
  track: MasteryTrack,
  doneChapters: Set<string>,
  solvedSlugs: Set<string>,
  progress: ProgressMap
): Set<number> {
  const open = new Set<number>();
  for (const week of track.weeks) {
    if (week.week === 1) {
      open.add(week.week);
      continue;
    }
    const previous = track.weeks.find((w) => w.week === week.week - 1);
    if (!previous) break;
    const prev = weekProgress(previous, track, doneChapters, solvedSlugs, progress);
    if (!prev.complete) break;
    open.add(week.week);
  }
  return open;
}

// ---------------------------------------------------------------------------
// Pacing — "6 months" only means something against a start date.
// ---------------------------------------------------------------------------

export const MS_PER_WEEK = 7 * 24 * 60 * 60 * 1000;

export interface Pacing {
  /** Whole weeks elapsed since the start date, 1-based (week 1 on day 0). */
  scheduledWeek: number;
  /** The week the learner has actually reached. */
  currentWeek: number;
  /** Positive = behind schedule, negative = ahead, 0 = on track. */
  weeksBehind: number;
  /** Projected finish if the current pace holds. */
  projectedFinish: Date;
}

/** Work out where the calendar says you should be. `now` is injectable so the
 * tests are not clock-dependent. */
export function pacing(
  startedAt: Date,
  currentWeek: number,
  totalWeeks: number,
  now: Date = new Date()
): Pacing {
  const elapsedWeeks = Math.floor((now.getTime() - startedAt.getTime()) / MS_PER_WEEK);
  const scheduledWeek = Math.min(totalWeeks, Math.max(1, elapsedWeeks + 1));
  const weeksBehind = scheduledWeek - currentWeek;

  // Project from the pace actually achieved. Before a week is finished there is
  // no pace to measure, so fall back to the nominal one-week-per-week.
  const completed = Math.max(0, currentWeek - 1);
  const weeksPerWeek = completed > 0 && elapsedWeeks > 0 ? completed / elapsedWeeks : 1;
  const remaining = totalWeeks - completed;
  const projectedFinish = new Date(
    now.getTime() + (remaining / Math.max(weeksPerWeek, 0.05)) * MS_PER_WEEK
  );

  return { scheduledWeek, currentWeek, weeksBehind, projectedFinish };
}

/** Settings key holding a track's ISO start date. */
export function startDateKey(trackKey: string): string {
  return `mastery:${trackKey}:started`;
}

// ---------------------------------------------------------------------------
// Exam paper assembly
// ---------------------------------------------------------------------------

export interface ExamQuestion {
  question: string;
  options: string[];
  /** Index into the SHUFFLED options. */
  answer: number;
  explanation: string;
}

function shuffle<T>(items: T[], rand: () => number): T[] {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/** Draw one sitting of a week's exam: sample from the bank, then shuffle both
 * the questions and each question's options, so a retake is a fresh paper
 * rather than a memory test for answer positions. */
export function drawExamPaper(week: MasteryWeek, rand: () => number = Math.random): ExamQuestion[] {
  const sample = Math.min(week.quiz_sample || week.quiz.length, week.quiz.length);
  return shuffle(week.quiz, rand)
    .slice(0, sample)
    .map((q) => {
      const correct = q.options[q.answer];
      const options = shuffle(q.options, rand);
      return {
        question: q.question,
        options,
        answer: options.indexOf(correct),
        explanation: q.explanation,
      };
    });
}

/** Format a study-time total for the UI. */
export function formatStudyTime(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}
