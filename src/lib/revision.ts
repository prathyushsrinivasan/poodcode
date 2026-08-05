// Spaced-repetition scheduling. This mirrors the authoritative Rust logic in
// `src-tauri/src/repo.rs` and is unit-tested (see revision.test.ts).

/** Interval ladder in days. Advancing on recall, resetting on a lapse. */
export const LADDER = [1, 3, 7, 14, 30, 90];

export function clampIndex(i: number): number {
  return Math.max(0, Math.min(i, LADDER.length - 1));
}

/** Days until the next review for a given ladder index. */
export function intervalDays(index: number): number {
  return LADDER[clampIndex(index)];
}

/** The next ladder index after a review. */
export function nextIndex(current: number, remembered: boolean): number {
  return remembered ? clampIndex(current + 1) : 0;
}

/** ISO date (YYYY-MM-DD) `days` from `from` (defaults to today). */
export function addDaysISO(days: number, from: Date = new Date()): string {
  const d = new Date(from);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

/** Due date after grading a review at `current` index. */
export function dueAfterReview(current: number, remembered: boolean, from?: Date): string {
  return addDaysISO(intervalDays(nextIndex(current, remembered)), from);
}

/** Whether an ISO due date is on or before today. */
export function isDue(dueISO: string, today: Date = new Date()): boolean {
  return dueISO <= today.toISOString().slice(0, 10);
}

/**
 * SM-2 scheduling, mirrored from the authoritative Rust `repo::sm2`. `quality`
 * is 0..=3 (Again / Hard / Good / Easy). Returns the next interval (days), the
 * adjusted ease factor, and whether this was a lapse.
 */
export function sm2(
  prevInterval: number,
  ease: number,
  reps: number,
  quality: number
): { interval: number; ease: number; lapse: boolean } {
  const delta = quality === 0 ? -0.3 : quality === 1 ? -0.15 : quality === 3 ? 0.15 : 0;
  const newEase = Math.max(1.3, ease + delta);
  if (quality === 0) {
    return { interval: 1, ease: newEase, lapse: true };
  }
  let interval: number;
  if (reps <= 0) interval = 1;
  else if (reps === 1) interval = quality >= 3 ? 6 : 3;
  else interval = Math.round(Math.max(1, prevInterval) * newEase);
  interval = Math.min(365, Math.max(1, interval));
  return { interval, ease: newEase, lapse: false };
}
