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
import type { MasteryProgress, MasteryTrack, MasteryWeek, QuizQuestion } from "../types";
import { reorderOptions } from "./quizKinds";

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
// Resume point — what the Today page shows for a track in progress.
// ---------------------------------------------------------------------------

export interface MasteryResume {
  /** The first week without a completion stamp (the last week once finished). */
  week: MasteryWeek;
  completed: number;
  total: number;
  finished: boolean;
}

/** Where a learner is in a track, from the completion stamps the backend writes
 * (`mastery_complete_week`). Cheap on purpose — Today shouldn't need the whole
 * problem bank to say "you're on week 7". Returns null for a track that hasn't
 * been touched: no progress rows and no start date. */
export function masteryResume(
  track: MasteryTrack,
  rows: MasteryProgress[],
  startedAt: string | undefined
): MasteryResume | null {
  const core = coreWeeks(track);
  if (core.length === 0) return null;
  const mine = rows.filter((r) => r.track_key === track.key);
  if (mine.length === 0 && !startedAt) return null;
  const done = new Set(mine.filter((r) => r.completed_at).map((r) => r.week));
  const next = core.find((w) => !done.has(w.week));
  return {
    week: next ?? core[core.length - 1],
    completed: core.filter((w) => done.has(w.week)).length,
    total: core.length,
    finished: next === undefined,
  };
}

/** The programme proper: every week except the optional ones after it. Totals,
 * pacing and "finished" are measured against these. */
export function coreWeeks(track: MasteryTrack): MasteryWeek[] {
  return track.weeks.filter((w) => !w.optional);
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

/** A drawn question: options shuffled, `answer` (and a multi-select's
 * `answers`) pointing into the SHUFFLED options — see lib/quizKinds.ts. */
export type ExamQuestion = QuizQuestion;

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
    .map((q) => reorderOptions(q, shuffle(q.options, rand)));
}

/** Format a study-time total for the UI. */
export function formatStudyTime(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

// ---------------------------------------------------------------------------
// Teaching tools per week — the pages built for a stretch of the programme.
// ---------------------------------------------------------------------------

export interface WeekTool {
  label: string;
  to: string;
  why: string;
}

/** The interactive tools that teach a TypeScript week's subject. */
export function weekTools(trackKey: string, week: number): WeekTool[] {
  if (trackKey !== "typescript") return [];
  const tools: WeekTool[] = [];
  if (week <= 8) {
    tools.push({ label: "Playground", to: "/playground/ts", why: "see what every declaration infers (Types tab)" });
  }
  if (week === 5 || week === 6) {
    tools.push({ label: "Call stack", to: "/visualise/async?tab=stack", why: "recursion and closures, frame by frame" });
  }
  if (week === 6 || week === 7) {
    tools.push({ label: "Array pipeline", to: "/visualise/async?tab=pipeline", why: "every intermediate array of a method chain" });
  }
  if (week >= 10 && week <= 13) {
    tools.push({ label: "Narrowing stepper", to: "/playground/ts", why: "a variable's type at every line (Narrowing tab)" });
  }
  if (week === 10 || week === 12) {
    tools.push({ label: "State machines", to: "/playground/ts", why: "a union of states and its moves, drawn (Machines tab)" });
  }
  if (week === 14 || week === 15 || week === 16) {
    tools.push({ label: "Strictness switcher", to: "/playground/ts", why: "flip compiler flags and watch errors appear (Compiler tab)" });
  }
  if (week >= 17 && week <= 22) {
    tools.push({ label: "Type expander", to: "/playground/ts", why: "every type alias fully expanded (Types tab)" });
  }
  if (week >= 20 && week <= 22) {
    tools.push({ label: "Type stepper", to: "/playground/ts", why: "a conditional type evaluated member by member (Step tab)" });
  }
  if (week === 26) {
    tools.push({ label: "Event loop", to: "/visualise/async?tab=loop", why: "step through the stack and the queues" });
    tools.push({ label: "Promise timeline", to: "/visualise/async?tab=combinators", why: "when all / allSettled / race / any settle" });
  }
  tools.push({ label: "Error glossary", to: "/ts-errors", why: "every TSnnnn code, explained" });
  return tools;
}

// ---------------------------------------------------------------------------
// Pacing that understands pauses (X-81). A pause shifts the start date: the
// weeks you were on holiday do not count against you.
// ---------------------------------------------------------------------------

export type PauseState = { pausedAt: string | null; pausedMs: number };

export function pauseKey(trackKey: string): string {
  return `mastery:${trackKey}:pause`;
}

export function parsePause(raw: string | undefined): PauseState {
  try {
    const v: unknown = JSON.parse(raw ?? "");
    if (typeof v === "object" && v !== null) {
      const o = v as Record<string, unknown>;
      const pausedAt =
        typeof o.pausedAt === "string" && !Number.isNaN(Date.parse(o.pausedAt)) ? o.pausedAt : null;
      const pausedMs = typeof o.pausedMs === "number" && o.pausedMs > 0 ? o.pausedMs : 0;
      return { pausedAt, pausedMs };
    }
  } catch {
    /* fall through */
  }
  return { pausedAt: null, pausedMs: 0 };
}

/** The start date with every paused stretch (including one in progress) added. */
export function effectiveStart(started: Date, pause: PauseState, now: Date = new Date()): Date {
  const ongoing = pause.pausedAt ? Math.max(0, now.getTime() - Date.parse(pause.pausedAt)) : 0;
  return new Date(started.getTime() + pause.pausedMs + ongoing);
}

export function togglePause(pause: PauseState, now: Date = new Date()): PauseState {
  if (pause.pausedAt) {
    return { pausedAt: null, pausedMs: pause.pausedMs + Math.max(0, now.getTime() - Date.parse(pause.pausedAt)) };
  }
  return { pausedAt: now.toISOString(), pausedMs: pause.pausedMs };
}

// ---------------------------------------------------------------------------
// Time budget (X-80)
// ---------------------------------------------------------------------------

/** Hours a week of the programme is planned to take. */
export const WEEK_BUDGET_HOURS = 9;

export function budgetNote(studySeconds: number): { text: string; over: boolean } {
  const budget = WEEK_BUDGET_HOURS * 3600;
  return {
    text: `${formatStudyTime(studySeconds)} of a ~${WEEK_BUDGET_HOURS}h week`,
    over: studySeconds > 2 * budget,
  };
}

// ---------------------------------------------------------------------------
// Today's share of the current week (X-61)
// ---------------------------------------------------------------------------

export interface PlanInput {
  chaptersLeft: string[];
  practiceLeft: number;
  problemsLeft: number;
  projectDone: boolean;
  hasProject: boolean;
  quizPassed: boolean;
  examPassed: boolean;
  /** Days left in this week at your pace (1..7). */
  daysLeft: number;
}

/** Split what is left of a week into today's share: the gate first (chapters),
 * then practice, problems and the project, then the quiz and the final. */
export function todayPlan(p: PlanInput): string[] {
  const tasks: string[] = [];
  for (const c of p.chaptersLeft) tasks.push(`Read and mark done: ${c}`);
  for (let i = 0; i < p.practiceLeft; i += 3) {
    const n = Math.min(3, p.practiceLeft - i);
    tasks.push(`Solve ${n} practice exercise${n === 1 ? "" : "s"}`);
  }
  for (let i = 0; i < p.problemsLeft; i += 2) {
    const n = Math.min(2, p.problemsLeft - i);
    tasks.push(`Solve ${n} problem${n === 1 ? "" : "s"}`);
  }
  if (p.hasProject && !p.projectDone) tasks.push("Work on the build project");
  if (!p.quizPassed) tasks.push("Take the end-of-week quiz");
  if (!p.examPassed) tasks.push("Submit the coding final");
  if (tasks.length === 0) return [];
  const perDay = Math.ceil(tasks.length / Math.max(1, Math.min(7, p.daysLeft)));
  return tasks.slice(0, perDay);
}

/** Days left in the scheduled week, from the (pause-adjusted) start date. */
export function daysLeftInWeek(start: Date, week: number, now: Date = new Date()): number {
  const weekEnd = start.getTime() + week * MS_PER_WEEK;
  const days = Math.ceil((weekEnd - now.getTime()) / (24 * 3600 * 1000));
  return Math.max(1, Math.min(7, days));
}

// ---------------------------------------------------------------------------
// Interleaved warm-up (X-53): three exercises from two and five weeks back.
// ---------------------------------------------------------------------------

export function interleavedWarmup<E extends { id: string }>(
  weeks: { week: number; practice?: E[] }[],
  week: number
): E[] {
  const from = (n: number) => weeks.find((w) => w.week === n)?.practice ?? [];
  const pick = (xs: E[], k: number, salt: number) =>
    xs.length === 0
      ? []
      : Array.from({ length: Math.min(k, xs.length) }, (_, i) => xs[(week * 7 + salt + i * 3) % xs.length]!);
  const out = [...pick(from(week - 2), 2, 1), ...pick(from(week - 5), 1, 2)];
  return out.filter((e, i) => out.findIndex((x) => x.id === e.id) === i);
}

// ---------------------------------------------------------------------------
// Links to the rest of the app (X-90, X-91, X-92)
// ---------------------------------------------------------------------------

export interface WeekLinks {
  /** TypeScript course week numbers covering the same ground. */
  course: number[];
  /** DSA curriculum unit keys that use the same structures. */
  dsa: string[];
  /** Next steps in the Projects track / Backend Lab. */
  projects: { label: string; to: string }[];
}

const TS_WEEK_LINKS: Record<number, [number[], string[]]> = {
  1: [[1, 2], ["io-and-arithmetic"]],
  2: [[3], ["branching"]],
  3: [[4], ["loops-and-digits"]],
  4: [[2], ["strings"]],
  5: [[5], []],
  6: [[5], ["recursion"]],
  7: [[6], ["arrays-first-pass"]],
  8: [[7], []],
  9: [[19], ["hashing"]],
  10: [[8, 9], []],
  11: [[9, 15], []],
  12: [[9], []],
  13: [[8], []],
  14: [[16], []],
  15: [[12], []],
  16: [[13], []],
  17: [[14], ["intervals"]],
  18: [[10], []],
  19: [[14, 29], []],
  20: [[29], []],
  21: [[29, 30], []],
  22: [[30, 31], ["tries"]],
  23: [[11], ["design"]],
  24: [[18, 20], ["stacks", "queues-and-deques", "linked-lists", "heaps"]],
  25: [[15], []],
  26: [[17], []],
  27: [[32], ["design"]],
};

export function weekLinks(trackKey: string, week: number): WeekLinks {
  if (trackKey !== "typescript") return { course: [], dsa: [], projects: [] };
  const [course, dsa] = TS_WEEK_LINKS[week] ?? [[], []];
  const projects =
    week >= 25
      ? [
          { label: "Backend Lab", to: "/backend" },
          { label: "Projects track", to: "/projects" },
        ]
      : [];
  return { course, dsa, projects };
}

// ---------------------------------------------------------------------------
// Using failed runs (X-52, X-54, X-82)
// ---------------------------------------------------------------------------

type Attemptable = { id: string; title: string };

/** Exercises from earlier weeks failed twice or more and still unsolved —
 * they come back in a later week's warm-up until they are solved (X-52). */
export function requeued<E extends Attemptable>(
  weeks: { week: number; practice?: E[]; problem_set?: E[] }[],
  week: number,
  failures: Record<string, number>,
  solved: Set<string>,
  max = 2
): E[] {
  return weeks
    .filter((w) => w.week < week)
    .flatMap((w) => [...(w.practice ?? []), ...(w.problem_set ?? [])])
    .filter((e) => (failures[e.id] ?? 0) >= 2 && !solved.has(e.id))
    .sort((a, b) => (failures[b.id] ?? 0) - (failures[a.id] ?? 0))
    .slice(0, max);
}

/** The exercise with the most failed runs among `items` (X-82). */
export function mostRetried<E extends Attemptable>(
  items: E[],
  failures: Record<string, number>
): { title: string; count: number } | null {
  let best: { title: string; count: number } | null = null;
  for (const e of items) {
    const n = failures[e.id] ?? 0;
    if (n > 0 && (!best || n > best.count)) best = { title: e.title, count: n };
  }
  return best;
}

export interface ChapterStat {
  key: string;
  name: string;
  attempted: number;
  firstTry: number;
}

/** Chapters with a low first-try rate: of the exercises you have solved or
 * failed, how many were accepted with no failed run first (X-54). A chapter
 * needs two attempted exercises to be judged, and is weak below 50%. */
export function weakChapters(
  chapters: { key: string; name: string; exercises?: { id: string }[] }[],
  failures: Record<string, number>,
  solved: Set<string>
): ChapterStat[] {
  const out: ChapterStat[] = [];
  for (const c of chapters) {
    const ids = (c.exercises ?? []).map((e) => e.id);
    const attempted = ids.filter((id) => solved.has(id) || (failures[id] ?? 0) > 0);
    if (attempted.length < 2) continue;
    const firstTry = attempted.filter((id) => solved.has(id) && !(failures[id] ?? 0)).length;
    if (firstTry / attempted.length < 0.5) out.push({ key: c.key, name: c.name, attempted: attempted.length, firstTry });
  }
  return out.sort((a, b) => a.firstTry / a.attempted - b.firstTry / b.attempted);
}

// ---------------------------------------------------------------------------
// Progress export (X-83) — for a portfolio or a mentor.
// ---------------------------------------------------------------------------

export interface ProgressReportRow {
  week: number;
  title: string;
  phase: string;
  complete: boolean;
  bestQuiz: number | null;
  finalPassed: boolean;
  projectShipped: boolean;
  chapters: string;
  problems: string;
  studyMinutes: number;
  completedAt: string | null;
}

export function progressReport(
  track: MasteryTrack,
  perWeek: WeekProgress[],
  progress: ProgressMap,
  exportedAt: Date = new Date()
): { json: string; markdown: string } {
  const rows: ProgressReportRow[] = track.weeks.map((w, i) => {
    const p = perWeek[i]!;
    return {
      week: w.week,
      title: w.title,
      phase: w.phase,
      complete: p.complete,
      bestQuiz: p.score,
      finalPassed: p.examPassed,
      projectShipped: p.projectDone,
      chapters: `${p.conceptsDone}/${p.conceptsTotal}`,
      problems: `${p.problemsSolved}/${p.problemsTotal}`,
      studyMinutes: Math.round(p.studySeconds / 60),
      completedAt: progress.get(w.week)?.completed_at ?? null,
    };
  });
  const core = coreWeeks(track).length;
  const done = rows.filter((r, i) => r.complete && !track.weeks[i]!.optional).length;
  const json = JSON.stringify(
    { track: track.key, title: track.title, exportedAt: exportedAt.toISOString(), weeksComplete: done, weeksTotal: core, weeks: rows },
    null,
    2
  );
  const tick = (b: boolean) => (b ? "✓" : "—");
  const md = [
    `# ${track.title} — progress`,
    "",
    `Exported ${exportedAt.toISOString().slice(0, 10)} · ${done}/${core} weeks complete · ${formatStudyTime(
      rows.reduce((s, r) => s + r.studyMinutes * 60, 0)
    )} of study`,
    "",
    "| Week | Title | Chapters | Problems | Best quiz | Final | Project | Time |",
    "|---|---|---|---|---|---|---|---|",
    ...rows.map(
      (r) =>
        `| ${r.week}${r.complete ? " ✓" : ""} | ${r.title} | ${r.chapters} | ${r.problems} | ${
          r.bestQuiz === null ? "—" : `${r.bestQuiz}%`
        } | ${tick(r.finalPassed)} | ${tick(r.projectShipped)} | ${formatStudyTime(r.studyMinutes * 60)} |`
    ),
    "",
  ].join("\n");
  return { json, markdown: md };
}

// ---------------------------------------------------------------------------
// Skill profile (X-69): what kinds of work you have done, as fractions.
// ---------------------------------------------------------------------------

export interface Skill {
  label: string;
  done: number;
  total: number;
}

/** Six skills, each the share of that kind of work solved so far:
 * reading inferred types (predict), reading errors (diagnose), repairing code
 * (fix), writing types (type challenges), writing programs (problems and
 * finals), and the runtime month (weeks 23-26). */
export function skillProfile(
  track: MasteryTrack,
  solved: Set<string>,
  perWeek: WeekProgress[]
): Skill[] {
  const all = track.weeks.flatMap((w) =>
    [...(w.practice ?? []), ...(w.problem_set ?? []), ...(w.exam?.types ? [w.exam.types] : [])].map((e) => ({
      e,
      week: w.week,
    }))
  );
  const count = (pick: (x: { e: { kind: string; id: string }; week: number }) => boolean): [number, number] => {
    const xs = all.filter(pick);
    return [xs.filter((x) => solved.has(x.e.id)).length, xs.length];
  };
  const finals = track.weeks.filter((w) => w.exam && !w.optional);
  const finalsPassed = finals.filter((w) => perWeek[w.week - 1]?.examPassed).length;
  const [predictDone, predictTotal] = count((x) => x.e.kind === "predict");
  const [diagDone, diagTotal] = count((x) => x.e.kind === "diagnose");
  const [fixDone, fixTotal] = count((x) => x.e.kind === "fix");
  const [typesDone, typesTotal] = count((x) => x.e.kind === "typelevel");
  const [codeDone, codeTotal] = count((x) => x.e.kind === "challenge");
  const [runDone, runTotal] = count((x) => x.week >= 23 && x.week <= 26);
  return [
    { label: "Reading types", done: predictDone, total: predictTotal },
    { label: "Reading errors", done: diagDone, total: diagTotal },
    { label: "Repairing code", done: fixDone, total: fixTotal },
    { label: "Writing types", done: typesDone, total: typesTotal },
    { label: "Writing programs", done: codeDone + finalsPassed, total: codeTotal + finals.length },
    { label: "Runtime & async", done: runDone, total: runTotal },
  ];
}
