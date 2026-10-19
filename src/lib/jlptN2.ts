import { N2_LESSONS, N2_QUESTIONS, type N2Question } from "../data/jlptN2";

export const N2_PROGRESS_KEY = "jlpt-n2-progress-v1";
export interface N2Result {
  attempts: number;
  correct: number;
  lastCorrect: boolean;
}
export type N2Progress = Record<string, N2Result>;

/** Normalize keyboard width and accidental spacing, without accepting a whole
 * word when the exercise asks for just one missing character. */
export function normalizeN2Answer(value: string): string {
  return value.normalize("NFKC").replace(/\s/gu, "");
}

export function isN2Answer(question: N2Question, input: string): boolean {
  const normalized = normalizeN2Answer(input);
  return normalized.length > 0 && [question.answer, ...question.accepted]
    .some((answer) => normalizeN2Answer(answer) === normalized);
}

/** Settings can be imported from older backups. Ignore unknown/malformed rows
 * rather than allowing them to inflate progress or break a lesson. */
export function parseN2Progress(raw?: string): N2Progress {
  if (!raw) return {};
  let parsed: unknown;
  try { parsed = JSON.parse(raw); } catch { return {}; }
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return {};
  const out: N2Progress = {};
  for (const q of N2_QUESTIONS) {
    const row = (parsed as Record<string, unknown>)[q.id];
    if (!row || typeof row !== "object") continue;
    const r = row as N2Result;
    if (Number.isSafeInteger(r.attempts) && r.attempts > 0 &&
        Number.isSafeInteger(r.correct) && r.correct >= 0 && r.correct <= r.attempts &&
        typeof r.lastCorrect === "boolean" && (!r.lastCorrect || r.correct > 0)) {
      out[q.id] = { attempts: r.attempts, correct: r.correct, lastCorrect: r.lastCorrect };
    }
  }
  return out;
}

export function recordN2Answer(progress: N2Progress, id: string, correct: boolean): N2Progress {
  const old = progress[id];
  return { ...progress, [id]: {
    attempts: (old?.attempts ?? 0) + 1,
    correct: (old?.correct ?? 0) + Number(correct),
    lastCorrect: correct,
  } };
}

export function n2Stats(questions: N2Question[], progress: N2Progress) {
  return {
    total: questions.length,
    attempted: questions.filter((q) => progress[q.id]).length,
    correct: questions.filter((q) => progress[q.id]?.lastCorrect).length,
    missed: questions.filter((q) => progress[q.id] && !progress[q.id].lastCorrect).length,
  };
}

export function n2ReviewQuestions(progress: N2Progress): N2Question[] {
  return N2_QUESTIONS.filter((q) => progress[q.id] && !progress[q.id].lastCorrect);
}

/** Resume the first unanswered question, then the first mistake. A completely
 * correct lesson opens at the beginning for another practice session. */
export function n2ResumeIndex(questions: N2Question[], progress: N2Progress): number {
  const unanswered = questions.findIndex((q) => !progress[q.id]);
  if (unanswered >= 0) return unanswered;
  const missed = questions.findIndex((q) => !progress[q.id]?.lastCorrect);
  return missed >= 0 ? missed : 0;
}

export function n2LessonFor(question: N2Question) {
  return N2_LESSONS.find((l) => l.questions.some((q) => q.id === question.id))!;
}
