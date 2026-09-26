// Pure state helpers for the capstone week's mock interviews and code reviews
// (components/MasteryCapstone.tsx). Both are stored as JSON in the settings
// table; anything unreadable falls back to a fresh state rather than throwing.

export type MockAttempt = { date: string; seconds: number; scores: number[] };
export type MockState = { startedAt: string | null; attempts: MockAttempt[] };
export type ReviewState = { text: string; compared: boolean; caught: number[] };

function parseObject(raw: string | undefined): Record<string, unknown> | null {
  if (!raw) return null;
  try {
    const v: unknown = JSON.parse(raw);
    return typeof v === "object" && v !== null && !Array.isArray(v) ? (v as Record<string, unknown>) : null;
  } catch {
    return null;
  }
}

const isNumberArray = (v: unknown): v is number[] =>
  Array.isArray(v) && v.every((x) => typeof x === "number" && Number.isFinite(x));

export function parseMockState(raw: string | undefined): MockState {
  const o = parseObject(raw);
  if (!o) return { startedAt: null, attempts: [] };
  const startedAt =
    typeof o.startedAt === "string" && !Number.isNaN(Date.parse(o.startedAt)) ? o.startedAt : null;
  const attempts = Array.isArray(o.attempts)
    ? o.attempts.filter(
        (a): a is MockAttempt =>
          typeof a === "object" &&
          a !== null &&
          typeof (a as MockAttempt).date === "string" &&
          typeof (a as MockAttempt).seconds === "number" &&
          isNumberArray((a as MockAttempt).scores)
      )
    : [];
  return { startedAt, attempts };
}

export function parseReviewState(raw: string | undefined): ReviewState {
  const o = parseObject(raw);
  if (!o) return { text: "", compared: false, caught: [] };
  return {
    text: typeof o.text === "string" ? o.text : "",
    compared: o.compared === true,
    caught: isNumberArray(o.caught) ? o.caught : [],
  };
}

/** Totals for the attempts at one mock session, or null before the first. Each
 * rubric line is scored 1–4, so the maximum is 4 × lines. */
export function mockAttemptSummary(
  attempts: MockAttempt[],
  rubricLines: number
): { count: number; best: number; last: number; max: number } | null {
  if (attempts.length === 0) return null;
  const totals = attempts.map((a) => a.scores.reduce((s, x) => s + x, 0));
  return {
    count: attempts.length,
    best: Math.max(...totals),
    last: totals[totals.length - 1],
    max: rubricLines * 4,
  };
}
