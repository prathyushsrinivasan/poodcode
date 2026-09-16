import type { CardReview } from "../types";

/**
 * Shared spaced-repetition primitives.
 *
 * Three decks schedule through the one `card_reviews` table — the Learn tab's
 * glossary cards (`CardStudy`), the DSA curriculum's self-checks (`dsaReview`)
 * and the 日本語 vocabulary list (`jpVocab`). Each had grown its own copy of
 * "what is today" and "is this card due", which is how two decks start
 * disagreeing about the same date. One copy lives here.
 *
 * Scheduling itself stays in the Rust `grade_card` (SM-2) — this module only
 * answers questions *about* a stored review, it never writes one.
 */

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
