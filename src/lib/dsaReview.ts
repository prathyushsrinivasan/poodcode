import type { CardReview } from "../types";
import { isCleared, type HydratedCurriculum, type HydratedUnit } from "./curriculum";

/**
 * Retention for the DSA curriculum: spacing the self-checks, and deciding what
 * is due.
 *
 * The curriculum shipped ~150 authored self-check questions across 33 units,
 * all of them reveal-the-answer-only — no grading, no scheduling. They are
 * already the ideal deck and they were inert. This module keys them into the
 * card-review table the Learn tab's `CardStudy` already uses, so nothing new is
 * stored: a check is a card, and its SM-2 state lives in `card_reviews`
 * alongside every other card.
 *
 * Scheduling is deliberately left to the Rust `grade_card` (SM-2) rather than
 * re-implemented from `revision.LADDER` here. Two schedulers for one table is
 * how due dates start disagreeing. `revision.LADDER` still decides *unit* decay
 * (see `curriculum.ts`), which is a different question — "when should I
 * re-practise this technique" rather than "when should I see this card again".
 *
 * Everything here is pure so it can be unit-tested; the pages render what it
 * returns.
 */

/** Stable card id for one unit's self-check. Never change the shape — the
 * review rows in SQLite are keyed by it. */
export function checkCardId(unitKey: string, index: number): string {
  return `dsa-check:${unitKey}:${index}`;
}

/** Today as `YYYY-MM-DD` in the *local* zone, matching what the backend stores. */
export function todayISO(now: Date = new Date()): string {
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

/** A never-graded card is due; a graded one is due on or after its due date. */
export function isCardDue(review: CardReview | undefined, today: string): boolean {
  return !review || review.due_date <= today;
}

export interface UnitChecks {
  /** Checks never graded or due today or earlier. */
  due: number;
  /** Checks graded at least once. */
  started: number;
  total: number;
}

export function unitChecks(
  u: HydratedUnit,
  reviews: Map<string, CardReview>,
  today: string
): UnitChecks {
  let due = 0;
  let started = 0;
  u.unit.checks.forEach((_, i) => {
    const r = reviews.get(checkCardId(u.unit.key, i));
    if (r && r.reps > 0) started++;
    if (isCardDue(r, today)) due++;
  });
  return { due, started, total: u.unit.checks.length };
}

export interface ReviewLaneUnit {
  unit: HydratedUnit;
  checksDue: number;
  /** True when the unit was cleared and its interval has run out. */
  stale: boolean;
  lastPractisedDays: number;
}

export interface ReviewLane {
  checksDue: number;
  /** Cleared units whose practice has gone stale. */
  staleUnits: number;
  /**
   * Units with something to do, most-overdue first. Only *cleared* units
   * appear: revision is for what you have learned, and putting a unit you have
   * never opened in the review queue would make the queue meaningless.
   */
  units: ReviewLaneUnit[];
}

/**
 * What is due today, across the units you have cleared.
 *
 * A unit qualifies when it has due self-checks or has gone stale. Sorted by how
 * overdue the *practice* is, then by how many checks are waiting, so the lane's
 * first entry is the one whose memory is furthest gone rather than the one that
 * happens to come first in the curriculum.
 */
export function reviewLane(
  c: HydratedCurriculum,
  reviews: Map<string, CardReview>,
  now: Date = new Date()
): ReviewLane {
  const today = todayISO(now);
  const units: ReviewLaneUnit[] = [];
  let checksDue = 0;
  let staleUnits = 0;

  for (const stage of c.stages) {
    for (const u of stage.units) {
      if (!isCleared(u.status)) continue;
      const { due } = unitChecks(u, reviews, today);
      checksDue += due;
      if (u.stale) staleUnits++;
      if (due > 0 || u.stale) {
        units.push({
          unit: u,
          checksDue: due,
          stale: u.stale,
          lastPractisedDays: u.lastPractisedDays,
        });
      }
    }
  }

  units.sort(
    (a, b) =>
      overdueBy(b) - overdueBy(a) ||
      b.checksDue - a.checksDue ||
      a.unit.unit.title.localeCompare(b.unit.unit.title)
  );
  return { checksDue, staleUnits, units };
}

/** Days past a unit's freshness window; 0 when it is not stale. Finite, so it
 * can be sorted — an unpractised unit would otherwise sort as Infinity. */
function overdueBy(r: ReviewLaneUnit): number {
  if (!r.stale || !Number.isFinite(r.lastPractisedDays)) return 0;
  return r.lastPractisedDays - (r.unit.staleAfterDays ?? 0);
}
