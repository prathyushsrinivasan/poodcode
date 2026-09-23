// Timing for checkpoint contests (table `contests`). Pure, so it is testable
// without a clock: `now` is always passed in.

import type { Contest } from "../types";

/** When a contest started, as epoch milliseconds.
 *
 * `started_at` comes from SQLite's `datetime('now')`: UTC, written as
 * "YYYY-MM-DD HH:MM:SS" with no zone marker. `new Date()` reads that form as
 * LOCAL time, which would skew every timer by the machine's UTC offset — so it
 * is normalised to ISO with an explicit `Z` first. Strings that already carry a
 * zone (ISO from elsewhere) are left alone. */
export function contestStartMs(startedAt: string): number {
  const s = startedAt.trim();
  if (!s) return NaN;
  const hasZone = /[zZ]$|[+-]\d\d:?\d\d$/.test(s);
  return Date.parse(hasZone ? s : `${s.replace(" ", "T")}Z`);
}

/** Seconds left on the clock (never negative). */
export function secondsLeft(contest: Pick<Contest, "started_at" | "duration_seconds">, now: number): number {
  const start = contestStartMs(contest.started_at);
  if (Number.isNaN(start)) return contest.duration_seconds;
  const elapsed = Math.floor((now - start) / 1000);
  return Math.max(0, contest.duration_seconds - Math.max(0, elapsed));
}

export interface ContestScore {
  solved: number;
  total: number;
  wrongTries: number;
}

export function contestScore(contest: Pick<Contest, "results">): ContestScore {
  return {
    solved: contest.results.filter((r) => r.solved).length,
    total: contest.results.length,
    wrongTries: contest.results.reduce((sum, r) => sum + (r.wrong_tries ?? 0), 0),
  };
}
