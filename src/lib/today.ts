/**
 * The arithmetic behind the Today page.
 *
 * The Dashboard used to know about one part of the app: problem counts, daily
 * difficulty goals, one weakest topic and one suggested problem. It said
 * nothing about the curriculum's up-next, either course's resume point, the
 * project tracks, or the 日本語 cards falling due — so the page that is
 * supposed to answer "what now?" could only answer it for a third of the app.
 *
 * Everything here is pure so it can be tested without a backend: the page
 * fetches, these functions decide.
 */

import type { CardReview, CountPair, HeatCell } from "../types";

/* ------------------------------------------------------------- sparklines */

/** An SVG path through `values`, normalised into a `width` × `height` box.
 *
 * A flat series still draws a line through the middle rather than along the
 * floor, because "nothing happened" and "the minimum happened" look identical
 * at the bottom of a box and mean different things. */
export function sparklinePath(values: number[], width: number, height: number, pad = 1): string {
  if (values.length === 0) return "";
  const max = Math.max(...values);
  const min = Math.min(...values);
  const span = max - min;
  const innerH = height - pad * 2;
  const step = values.length > 1 ? (width - pad * 2) / (values.length - 1) : 0;

  return values
    .map((v, i) => {
      const x = pad + i * step;
      const t = span === 0 ? 0.5 : (v - min) / span;
      const y = pad + innerH * (1 - t);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

export interface Trend {
  /** Sum of the most recent 7 entries. */
  current: number;
  /** Sum of the 7 before those. */
  previous: number;
  /** Whole-percent change, or null when there is no earlier period to compare. */
  percent: number | null;
  direction: "up" | "down" | "flat";
}

/** Compare the last 7 days against the 7 before them.
 *
 * Returns `percent: null` rather than a fake 0% when the earlier week has no
 * data at all — a first week of use is not "no change". */
export function weekOverWeek(values: number[]): Trend {
  const current = values.slice(-7).reduce((a, b) => a + b, 0);
  const earlier = values.slice(-14, -7);
  const previous = earlier.reduce((a, b) => a + b, 0);
  if (earlier.length === 0 || previous === 0) {
    return { current, previous, percent: null, direction: current > 0 ? "up" : "flat" };
  }
  const percent = Math.round(((current - previous) / previous) * 100);
  return {
    current,
    previous,
    percent,
    direction: percent > 0 ? "up" : percent < 0 ? "down" : "flat",
  };
}

/** Pull a plain number series out of the heatmap the statistics command
 * returns, oldest first, for the last `days` days. */
export function heatSeries(heatmap: HeatCell[], days: number): number[] {
  return heatmap.slice(-days).map((c) => c.count);
}

/** The same, for the label/value pairs `timeline` returns. */
export function pairSeries(pairs: CountPair[], days: number): number[] {
  return pairs.slice(-days).map((p) => p.value);
}

/* --------------------------------------------------------------- due now */

export type DueSource = "curriculum" | "vocab" | "slow" | "flashcards";

export interface DueGroup {
  source: DueSource;
  label: string;
  count: number;
  /** Where the "review these" button goes. */
  href: string;
  hint: string;
}

/** How many cards in `deck` are due on or before `today`.
 *
 * A card with no review row has never been seen; that counts as due, because
 * the first sitting is the one that matters most and hiding it would make a
 * fresh deck look finished. */
export function dueCardCount(
  cardIds: readonly string[],
  reviews: Map<string, CardReview>,
  today: string
): number {
  let n = 0;
  for (const id of cardIds) {
    const r = reviews.get(id);
    if (!r || r.due_date <= today) n++;
  }
  return n;
}

/** Merge every review system into one list, dropping the empty ones.
 *
 * Sorted by how much is waiting, so the biggest pile is the first thing
 * offered rather than whichever track happens to be listed first. */
export function mergeDue(groups: DueGroup[]): DueGroup[] {
  return groups.filter((g) => g.count > 0).sort((a, b) => b.count - a.count);
}

/* ----------------------------------------------------------------- goals */

export interface GoalSpec {
  key: string;
  label: string;
  done: number;
  target: number;
}

/** Drop goals with no target, and report how many are met.
 *
 * "Review problems" used to be one of these, pointing at a queue whose UI had
 * been removed — a goal you could not act on. Callers now pass curriculum
 * reviews instead (UI_ROADMAP B2). */
export function summariseGoals(goals: GoalSpec[]): {
  rows: GoalSpec[];
  met: number;
  total: number;
} {
  const rows = goals.filter((g) => g.target > 0);
  return {
    rows,
    met: rows.filter((g) => g.done >= g.target).length,
    total: rows.length,
  };
}
