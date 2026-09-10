// Formatting and progress arithmetic shared by every track page — the Backend
// Lab, the two courses and the Projects track.
//
// These were three near-identical copies, one per page, which had already begun
// to drift: two `studyTime`s rendered "~0 min" for an unsized unit where the
// third rendered nothing. The behaviour kept here is the guarded one.

import type { Exercise } from "../types";

/** Units are sized in study hours, not minutes — "~5 h" reads as a plan, where
 * "~300 min" reads as a wall. An unsized unit renders as nothing at all, so a
 * caller can drop it into a sentence without emitting "about 0 min of study". */
export function studyTime(minutes: number): string {
  if (minutes <= 0) return "";
  if (minutes < 90) return `~${minutes} min`;
  const hours = minutes / 60;
  return `~${Number.isInteger(hours) ? hours : hours.toFixed(1)} h`;
}

/** "3 modules", "1 module". */
export const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

/** The progress note on a collapsed section header: "✓ done", "2/5", or
 * nothing at all when there is nothing in there to solve. */
export function solvedLabel(
  exercises: readonly Exercise[] | null | undefined,
  solved: ReadonlySet<string>
): string {
  const ids = (exercises ?? []).map((e) => e.id);
  if (ids.length === 0) return "";
  const n = ids.filter((id) => solved.has(id)).length;
  return n === ids.length ? "✓ done" : `${n}/${ids.length}`;
}

/** Every judged exercise required to complete a unit: the exercises of each of
 * its groups (lessons, or steps), plus any closing build passed as an extra.
 *
 * Optional extras that do not gate completion — a course week's "stretch"
 * build, say — are simply not passed in. */
export function collectExerciseIds(
  groups: readonly { exercises?: Exercise[] | null }[] | null | undefined,
  ...extras: readonly (Exercise | null | undefined)[]
): string[] {
  const ids: string[] = [];
  for (const g of groups ?? []) for (const e of g.exercises ?? []) ids.push(e.id);
  for (const e of extras) if (e) ids.push(e.id);
  return ids;
}
