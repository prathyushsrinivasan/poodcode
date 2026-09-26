// The programme final exam (TS_MASTERY_ROADMAP X-36): the paper, the score and
// the saved state. Pure, so it is tested directly; rendered by
// components/MasteryFinalExam.tsx.
//
// A sitting stores only a seed, so the paper — which questions, in which order,
// with which option order — is re-derived identically after a restart instead
// of being copied into settings.

import type { MasteryFinalExam, MasteryWeek } from "../types";
import type { ExamQuestion } from "./mastery";
import { seededRandom, shuffleWith } from "./quizShuffle";
import { reorderOptions } from "./quizKinds";

export type FinalSitting = {
  seed: number;
  startedAt: string;
  /** Picked option per paper question; -1 = unanswered. */
  picked: number[];
  /** Problem and puzzle ids accepted during this sitting. */
  solved: string[];
};

export type FinalAttempt = {
  date: string;
  seconds: number;
  quizPercent: number;
  problems: number;
  types: number;
  passed: boolean;
};

export type FinalExamState = { sitting: FinalSitting | null; attempts: FinalAttempt[] };

export const finalExamKey = (trackKey: string) => `mastery-final-exam:${trackKey}`;

/** Draw the paper: round-robin across the weeks so every week is represented
 * before any week gives a second question, each week's bank shuffled, each
 * question's options shuffled. Deterministic for a given seed. */
export function drawFinalPaper(weeks: MasteryWeek[], size: number, seed: number): ExamQuestion[] {
  const rand = seededRandom(seed);
  const banks = shuffleWith(
    weeks.filter((w) => w.quiz.length > 0).map((w) => shuffleWith(w.quiz, rand)),
    rand
  );
  const out: ExamQuestion[] = [];
  const seen = new Set<string>();
  for (let round = 0; out.length < size; round++) {
    let drewAny = false;
    for (const bank of banks) {
      if (out.length >= size) break;
      const q = bank[round];
      if (!q) continue;
      drewAny = true;
      if (seen.has(q.question)) continue;
      seen.add(q.question);
      out.push(reorderOptions(q, shuffleWith(q.options, rand)));
    }
    if (!drewAny) break;
  }
  return out;
}

export type FinalScore = {
  quizPercent: number;
  problems: number;
  types: number;
  passed: boolean;
};

export function scoreSitting(
  exam: MasteryFinalExam,
  paper: ExamQuestion[],
  sitting: FinalSitting
): FinalScore {
  const correct = paper.filter((q, i) => sitting.picked[i] === q.answer).length;
  const quizPercent = paper.length === 0 ? 0 : Math.round((correct / paper.length) * 100);
  const solved = new Set(sitting.solved);
  const problems = exam.problems.filter((p) => solved.has(p.id)).length;
  const types = exam.type_section.filter((p) => solved.has(p.id)).length;
  return {
    quizPercent,
    problems,
    types,
    passed:
      quizPercent >= exam.pass_mark && problems >= exam.min_problems && types >= exam.min_types,
  };
}

function isNumberArray(v: unknown): v is number[] {
  return Array.isArray(v) && v.every((x) => typeof x === "number");
}

export function parseFinalExamState(raw: string | undefined): FinalExamState {
  const empty: FinalExamState = { sitting: null, attempts: [] };
  if (!raw) return empty;
  let v: unknown;
  try {
    v = JSON.parse(raw);
  } catch {
    return empty;
  }
  if (typeof v !== "object" || v === null) return empty;
  const o = v as Record<string, unknown>;
  let sitting: FinalSitting | null = null;
  const s = o.sitting as Record<string, unknown> | null | undefined;
  if (
    s &&
    typeof s.seed === "number" &&
    typeof s.startedAt === "string" &&
    isNumberArray(s.picked) &&
    Array.isArray(s.solved) &&
    s.solved.every((x) => typeof x === "string")
  ) {
    sitting = {
      seed: s.seed,
      startedAt: s.startedAt,
      picked: s.picked,
      solved: s.solved as string[],
    };
  }
  const attempts = Array.isArray(o.attempts)
    ? (o.attempts as unknown[]).filter((a): a is FinalAttempt => {
        if (typeof a !== "object" || a === null) return false;
        const r = a as Record<string, unknown>;
        return (
          typeof r.date === "string" &&
          typeof r.seconds === "number" &&
          typeof r.quizPercent === "number" &&
          typeof r.problems === "number" &&
          typeof r.types === "number" &&
          typeof r.passed === "boolean"
        );
      })
    : [];
  return { sitting, attempts };
}

/** The attempt to show on the completion summary: the first pass, else the best try. */
export function headlineAttempt(attempts: FinalAttempt[]): FinalAttempt | null {
  const pass = attempts.find((a) => a.passed);
  if (pass) return pass;
  let best: FinalAttempt | null = null;
  for (const a of attempts) {
    const score = a.quizPercent + a.problems * 10 + a.types * 10;
    const bestScore = best ? best.quizPercent + best.problems * 10 + best.types * 10 : -1;
    if (score > bestScore) best = a;
  }
  return best;
}
