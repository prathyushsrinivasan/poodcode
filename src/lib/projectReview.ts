// A project's quiz questions, gathered for retrieval practice across modules.
//
// WHY. Every Projects-track module carries three kinds of multiple-choice
// question — a warm-up before each step, a check after it, and a mixed review at
// the end of the module — about 125 of them in the Todo API by module 9. Each is
// answered once, in the module that asked it, and never seen again. That is the
// weakest possible way to use a question: the one moment it is asked is the one
// moment the answer is already on the screen above it.
//
// Asked again a week later, mixed in with questions from other modules, the same
// question is a genuine test of whether the idea stuck. That is all this is: the
// questions the track already wrote, drawn from the modules you have finished,
// with the ones you have got wrong before asked first.

import type { Project, QuizQuestion } from "../types";
import { hashString, seededRandom, shuffleWith } from "./quizShuffle";

export type QuestionSource = "warm-up" | "check" | "module review";

export interface ReviewQuestion extends QuizQuestion {
  /** Stable across seed regenerations as long as the question text is. */
  id: string;
  moduleKey: string;
  moduleNumber: number;
  moduleTitle: string;
  phase: string;
  /** The step the question was asked in; empty for a module review question. */
  stepKey: string;
  stepTitle: string;
  source: QuestionSource;
}

/** Every quiz question in a project's written modules, in the order the
 * project asks them. A question repeated word for word is kept once. */
export function collectQuestions(project: Project): ReviewQuestion[] {
  const out: ReviewQuestion[] = [];
  const seen = new Set<string>();
  const modules = (project.modules ?? [])
    .filter((m) => m.authored)
    .sort((a, b) => a.number - b.number);

  for (const m of modules) {
    const base = {
      moduleKey: m.key,
      moduleNumber: m.number,
      moduleTitle: m.title,
      phase: m.phase,
    };
    const add = (q: QuizQuestion, source: QuestionSource, stepKey = "", stepTitle = "") => {
      const text = q.question.trim();
      if (!text || seen.has(text) || q.options.length < 2) return;
      seen.add(text);
      out.push({
        ...q,
        ...base,
        id: `${project.key}:${hashString(text).toString(36)}`,
        stepKey,
        stepTitle,
        source,
      });
    };
    for (const s of m.steps ?? []) {
      for (const q of s.warmup ?? []) add(q, "warm-up", s.key, s.title);
      for (const q of s.quiz ?? []) add(q, "check", s.key, s.title);
    }
    for (const q of m.review ?? []) add(q, "module review");
  }
  return out;
}

/** What the drill remembers about one question, per viewer. */
export interface QuestionHistory {
  /** Times answered. */
  seen: number;
  /** Times answered wrongly. */
  missed: number;
  /** Whether the most recent answer was right. */
  lastRight: boolean;
}

export type ReviewHistory = Record<string, QuestionHistory>;

/** Record one answer, returning a new history object. */
export function recordAnswer(history: ReviewHistory, id: string, right: boolean): ReviewHistory {
  const prev = history[id] ?? { seen: 0, missed: 0, lastRight: true };
  return {
    ...history,
    [id]: {
      seen: prev.seen + 1,
      missed: prev.missed + (right ? 0 : 1),
      lastRight: right,
    },
  };
}

/**
 * How urgently a question should come up again. Lower is sooner.
 *
 *   0  last answered wrongly — the whole point of a drill is to go back to these
 *   1  never answered
 *   2  answered, right last time, but missed at some point before
 *   3  answered, and never missed
 *
 * Deliberately coarse. A spaced-repetition schedule wants dates and intervals,
 * and this is a practice round you start by choice, not a queue that nags. Four
 * buckets are enough to make a round lead with what you are shaky on.
 */
export function priority(h: QuestionHistory | undefined): number {
  if (!h || h.seen === 0) return 1;
  if (!h.lastRight) return 0;
  return h.missed > 0 ? 2 : 3;
}

/**
 * Choose a round of `size` questions from `pool`: most urgent bucket first,
 * shuffled within each bucket by `seed`, then shuffled again as a round so the
 * missed questions are not always the first few on screen.
 */
export function pickRound(
  pool: readonly ReviewQuestion[],
  history: ReviewHistory,
  size: number,
  seed: number
): ReviewQuestion[] {
  const rand = seededRandom(seed);
  const buckets = new Map<number, ReviewQuestion[]>();
  for (const q of pool) {
    const p = priority(history[q.id]);
    const b = buckets.get(p);
    if (b) b.push(q);
    else buckets.set(p, [q]);
  }
  const ordered = [...buckets.keys()]
    .sort((a, b) => a - b)
    .flatMap((p) => shuffleWith(buckets.get(p)!, rand));
  return shuffleWith(ordered.slice(0, Math.max(0, size)), rand);
}

/** A per-bucket count, for telling the viewer what a round will draw on. */
export function poolSummary(pool: readonly ReviewQuestion[], history: ReviewHistory) {
  let missed = 0;
  let fresh = 0;
  let shaky = 0;
  let solid = 0;
  for (const q of pool) {
    const p = priority(history[q.id]);
    if (p === 0) missed++;
    else if (p === 1) fresh++;
    else if (p === 2) shaky++;
    else solid++;
  }
  return { missed, fresh, shaky, solid };
}
