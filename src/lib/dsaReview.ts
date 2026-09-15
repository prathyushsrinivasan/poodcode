import type { CardReview, Difficulty, Problem } from "../types";
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

/** Stable card id for one Big-O drill item, namespaced apart from the checks so
 * the two decks schedule independently. */
export function bigoCardId(unitKey: string, index: number): string {
  return `dsa-bigo:${unitKey}:${index}`;
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

/** Due / started / total over any set of card ids. */
export function cardStats(
  ids: string[],
  reviews: Map<string, CardReview>,
  today: string
): UnitChecks {
  let due = 0;
  let started = 0;
  for (const id of ids) {
    const r = reviews.get(id);
    // `reps` resets to 0 on a lapse, so a card you have failed is still started.
    if (r && (r.reps > 0 || r.lapses > 0)) started++;
    if (isCardDue(r, today)) due++;
  }
  return { due, started, total: ids.length };
}

export function unitChecks(
  u: HydratedUnit,
  reviews: Map<string, CardReview>,
  today: string
): UnitChecks {
  return cardStats(
    u.unit.checks.map((_, i) => checkCardId(u.unit.key, i)),
    reviews,
    today
  );
}

/**
 * How long a solve should take before it stops counting as fluent, per
 * difficulty, in seconds.
 *
 * The curriculum's own thesis is reflex speed — *"your hands start typing a
 * sliding window before you have finished the sentence"* — but `solid` counts
 * correctness alone, so a problem you ground out over forty minutes and one you
 * typed in four are indistinguishable afterwards. They are not the same thing,
 * and the slow one is the one worth doing again.
 *
 * Generous on purpose. These are "you have not internalised this yet" lines,
 * not interview pace: the point is to surface a re-practice candidate, and a
 * threshold that fires on everything surfaces nothing.
 */
export const SLOW_AFTER_SECONDS: Record<Difficulty, number> = {
  Intro: 10 * 60,
  Easy: 20 * 60,
  Medium: 40 * 60,
  Hard: 60 * 60,
};

/** A solved problem that took longer than its difficulty's budget. Unrecorded
 * time (0) is not slow — it means the timer never ran, not that it ran fast. */
export function isSlowSolve(p: Problem): boolean {
  return (
    p.solved_status === "solved" &&
    p.time_taken_seconds > 0 &&
    p.time_taken_seconds > SLOW_AFTER_SECONDS[p.difficulty]
  );
}

/** Solved-but-slow problems in a unit, hardest-won first. */
export function slowSolves(u: HydratedUnit): Problem[] {
  return u.rungs
    .flatMap((r) => r.items)
    .map((i) => i.problem)
    .filter((p): p is Problem => p !== null && isSlowSolve(p))
    .sort((a, b) => b.time_taken_seconds - a.time_taken_seconds);
}

export interface ReviewLaneUnit {
  unit: HydratedUnit;
  checksDue: number;
  /** True when the unit was cleared and its interval has run out. */
  stale: boolean;
  lastPractisedDays: number;
  /** Problems solved correctly but slowly — a re-practice signal on their own. */
  slow: Problem[];
}

export interface ReviewLane {
  checksDue: number;
  /** Cleared units whose practice has gone stale. */
  staleUnits: number;
  /** Problems solved correctly but slowly, across cleared units. */
  slowSolves: number;
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
  let slowCount = 0;

  for (const stage of c.stages) {
    for (const u of stage.units) {
      // A unit marked known is excluded: you told the app you know it, and
      // handing it back as revision would be arguing with you.
      if (u.skipped || !isCleared(u.status)) continue;
      const { due } = unitChecks(u, reviews, today);
      const slow = slowSolves(u);
      checksDue += due;
      slowCount += slow.length;
      if (u.stale) staleUnits++;
      if (due > 0 || u.stale || slow.length > 0) {
        units.push({
          unit: u,
          checksDue: due,
          stale: u.stale,
          lastPractisedDays: u.lastPractisedDays,
          slow,
        });
      }
    }
  }

  units.sort(
    (a, b) =>
      overdueBy(b) - overdueBy(a) ||
      b.checksDue - a.checksDue ||
      b.slow.length - a.slow.length ||
      a.unit.unit.title.localeCompare(b.unit.unit.title)
  );
  return { checksDue, staleUnits, slowSolves: slowCount, units };
}

/** Days past a unit's freshness window; 0 when it is not stale. Finite, so it
 * can be sorted — an unpractised unit would otherwise sort as Infinity. */
function overdueBy(r: ReviewLaneUnit): number {
  if (!r.stale || !Number.isFinite(r.lastPractisedDays)) return 0;
  return r.lastPractisedDays - (r.unit.staleAfterDays ?? 0);
}
