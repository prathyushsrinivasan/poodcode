// "Predict first" (TS_MASTERY_ROADMAP M1-03): before running, write down what
// you think your program prints for the first test's input. After the run the
// prediction is compared with what it actually printed — with the judge's own
// normalisation — and every mismatch is kept as a learning moment.

import { normalizeOutput } from "./outputCompare";

export type Prediction = { id: string; at: string; predicted: string; actual: string };

const LOG_KEY = "poodcode:predict-log";

export function predictionMatches(predicted: string, actual: string): boolean {
  return normalizeOutput(predicted) === normalizeOutput(actual);
}

export function predictionLog(): Prediction[] {
  try {
    const v: unknown = JSON.parse(localStorage.getItem(LOG_KEY) || "[]");
    return Array.isArray(v)
      ? v.filter(
          (p): p is Prediction =>
            typeof p === "object" &&
            p !== null &&
            typeof (p as Prediction).id === "string" &&
            typeof (p as Prediction).predicted === "string" &&
            typeof (p as Prediction).actual === "string"
        )
      : [];
  } catch {
    return [];
  }
}

/** Keep a mismatch (the last 200). Matches are not worth storing. */
export function logMismatch(id: string, predicted: string, actual: string, now: Date = new Date()): void {
  try {
    const next = [{ id, at: now.toISOString(), predicted, actual }, ...predictionLog()].slice(0, 200);
    localStorage.setItem(LOG_KEY, JSON.stringify(next));
  } catch {
    /* private mode — the comparison on screen is what matters */
  }
}
