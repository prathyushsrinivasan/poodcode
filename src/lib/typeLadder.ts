// The type-challenge ladder as a daily rep (TS_MASTERY_ROADMAP M5-02): every
// type-graded exercise in the programme, easiest first, served one a day from
// the weeks you have reached, with a streak.

import type { Exercise, MasteryWeek } from "../types";

export type Rung = { week: number; exercise: Exercise };

const TIER: Record<string, number> = { Easy: 0, "": 1, Medium: 1, Hard: 2 };

// Type challenges only — "predict the type" drills are type-graded too, but
// they practise reading an inference, not writing a type.
const isTypeGraded = (e: Exercise) => e.kind === "typelevel";

/** Every type-graded exercise, by week and then by tier; ids are unique. */
export function typeLadder(weeks: MasteryWeek[]): Rung[] {
  const seen = new Set<string>();
  const rungs: Rung[] = [];
  for (const w of weeks) {
    const pool = [
      ...(w.practice ?? []),
      ...(w.problem_set ?? []),
      ...(w.exam?.types ? [w.exam.types] : []),
    ].filter(isTypeGraded);
    pool.sort((a, b) => (TIER[a.difficulty] ?? 1) - (TIER[b.difficulty] ?? 1));
    for (const e of pool) {
      if (seen.has(e.id)) continue;
      seen.add(e.id);
      rungs.push({ week: w.week, exercise: e });
    }
  }
  return rungs;
}

export type DailyState = {
  /** Today's pick, kept for the day so it does not change on reload. */
  pick: { day: string; id: string } | null;
  /** Local days (YYYY-MM-DD) on which the daily puzzle was solved. */
  days: string[];
};

export const dailyKey = (trackKey: string) => `mastery-type-daily:${trackKey}`;

/** A local calendar day as YYYY-MM-DD. */
export function localDay(d: Date = new Date()): string {
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${m}-${day}`;
}

export function parseDaily(raw: string | undefined): DailyState {
  try {
    const v = JSON.parse(raw ?? "") as Partial<DailyState>;
    const pick =
      v.pick && typeof v.pick.day === "string" && typeof v.pick.id === "string" ? v.pick : null;
    const days = Array.isArray(v.days) ? v.days.filter((d): d is string => typeof d === "string") : [];
    return { pick, days };
  } catch {
    return { pick: null, days: [] };
  }
}

/** Today's puzzle: yesterday's pick carries over only if it was never solved;
 * otherwise the first unsolved rung from a week you have reached. */
export function todaysPuzzle(
  ladder: Rung[],
  reachedWeek: number,
  solved: Set<string>,
  state: DailyState,
  today: string
): Rung | null {
  if (state.pick?.day === today) {
    const kept = ladder.find((r) => r.exercise.id === state.pick!.id);
    if (kept) return kept;
  }
  return ladder.find((r) => r.week <= reachedWeek && !solved.has(r.exercise.id)) ?? null;
}

/** Consecutive days solved, ending today — or yesterday, if today is still open. */
export function streak(days: string[], today: string): number {
  const set = new Set(days);
  const d = new Date(`${today}T12:00:00`);
  if (!set.has(today)) d.setDate(d.getDate() - 1);
  let n = 0;
  while (set.has(localDay(d))) {
    n++;
    d.setDate(d.getDate() - 1);
  }
  return n;
}
