// Chapter-completion state for the Learn tab.
//
// This used to live in localStorage, which meant `backupDatabase` (a SQLite
// VACUUM INTO) never captured it and clearing site data silently wiped months
// of progress. It now lives in the `chapter_progress` table alongside every
// other kind of progress, with a one-time migration for anyone upgrading.
//
// Exercise DRAFTS (`poodcode:learn-ex:*`) deliberately stay in localStorage —
// they are scratch text, not progress, and are rewritten on every keystroke.
//
// Flashcard mastery is elsewhere again: vocabulary cards use real spaced
// repetition in SQLite (the `card_reviews` table + api.cardReviews/gradeCard).

import { api } from "../api";
import type { Concept } from "../types";

const LEGACY_DONE_KEY = "poodcode:learn-done"; // pre-migration JSON array
const MIGRATED_KEY = "poodcode:learn-done-migrated";

/** Push any pre-existing localStorage completions into SQLite, once. Failures
 * are swallowed and retried next launch — losing a checkmark is not worth
 * blocking the page over. */
async function migrateLegacyChapters(): Promise<void> {
  if (localStorage.getItem(MIGRATED_KEY) === "1") return;
  let keys: string[] = [];
  try {
    const raw = JSON.parse(localStorage.getItem(LEGACY_DONE_KEY) || "[]");
    keys = Array.isArray(raw) ? raw.filter((k) => typeof k === "string") : [];
  } catch {
    keys = [];
  }
  for (const key of keys) {
    await api.setChapterDone(key, true);
  }
  localStorage.setItem(MIGRATED_KEY, "1");
}

/** Concept keys the learner has marked complete. */
export async function loadDoneChapters(): Promise<Set<string>> {
  try {
    await migrateLegacyChapters();
  } catch {
    // Migration is best-effort; fall through to whatever the server has.
  }
  return new Set(await api.doneChapters());
}

/** Toggle a chapter and return the updated set. The caller passes its current
 * set so the UI can update without a round trip for the whole list. */
export async function setChapterDone(
  current: Set<string>,
  key: string,
  done: boolean
): Promise<Set<string>> {
  await api.setChapterDone(key, done);
  const next = new Set(current);
  if (done) next.add(key);
  else next.delete(key);
  return next;
}

/** Stable id for a vocabulary card: concept key + the term on its front. */
export function cardId(conceptKey: string, front: string): string {
  return `${conceptKey}#${front}`;
}

const VOCAB_IDS_MIGRATED_KEY = "poodcode:jp-vocab-ids-migrated";

/**
 * One-off: a glossary card for a term that is also a 日本語 vocabulary word used
 * to schedule under `<concept>#<term>`. It now carries the vocabulary word's id
 * so the two are one card rather than two schedules for one word — which means
 * the old rows would otherwise be orphaned and the learner's history would
 * silently reset.
 *
 * Several old ids can land on the same new one (継承 was a card in two sets), so
 * the backend merges rather than renames. The flag is set only after the call
 * succeeds, so a failed run is simply retried on the next launch.
 */
export async function migrateVocabCardIds(concepts: Concept[]): Promise<void> {
  if (localStorage.getItem(VOCAB_IDS_MIGRATED_KEY) === "1") return;
  const moves: [string, string][] = [];
  for (const c of concepts) {
    for (const card of c.cards ?? []) {
      if (card.card_id) moves.push([cardId(c.key, card.front), card.card_id]);
    }
  }
  if (moves.length > 0) await api.mergeCardReviews(moves);
  localStorage.setItem(VOCAB_IDS_MIGRATED_KEY, "1");
}

// Per-exercise "solved once" marks, for every track that judges exercises.
//
// These lived in localStorage on the theory that they were a UI convenience.
// That was true when only the Learn tab used them; it stopped being true when
// the Projects track arrived, where they ARE the progress — a module's bar is
// solved/required, "Resume" jumps to the first unsolved exercise, and a module
// auto-completes when the last one lands. Clearing site data zeroed all of it
// while leaving the SQLite chapter ✓ marks standing.
//
// So they now live in `exercise_progress`, covered by backup/restore like the
// chapter marks above. DRAFTS (`poodcode:learn-ex:*`) stay in localStorage —
// those are scratch text, rewritten on every keystroke, and genuinely are a
// convenience.
//
// READS STAY SYNCHRONOUS. Call sites read this set while rendering (a module
// page asks "is this exercise solved?" once per card), so the ids are held in
// a module-level cache that `loadSolvedExercises` hydrates and every write
// updates. `solvedExercises()` reads that cache; it is warm for the rest of
// the session after the first load, so navigating between modules never
// flashes an empty set.

const SOLVED_EX_KEY = "poodcode:learn-ex-solved"; // pre-migration JSON array
const SOLVED_MIGRATED_KEY = "poodcode:learn-ex-solved-migrated";

/** Hydrated by `loadSolvedExercises`, then kept in step by the writers below. */
let solvedCache = new Set<string>();

function readLegacySolved(): string[] {
  try {
    const raw = JSON.parse(localStorage.getItem(SOLVED_EX_KEY) || "[]");
    return Array.isArray(raw) ? raw.filter((id) => typeof id === "string") : [];
  } catch {
    return [];
  }
}

/** Push any pre-existing localStorage marks into SQLite, once. The legacy key
 * is left in place: it costs nothing, and a failed migration that has already
 * flipped the flag would otherwise have thrown the marks away. */
async function migrateLegacySolved(): Promise<void> {
  if (localStorage.getItem(SOLVED_MIGRATED_KEY) === "1") return;
  const ids = readLegacySolved();
  if (ids.length > 0) await api.setExercisesSolved(ids, true);
  localStorage.setItem(SOLVED_MIGRATED_KEY, "1");
}

/** Load the solved set from SQLite into the cache. Call once per page mount,
 * alongside `loadDoneChapters`. */
export async function loadSolvedExercises(): Promise<Set<string>> {
  try {
    await migrateLegacySolved();
  } catch {
    // Best-effort, retried next launch — same as the chapter migration.
  }
  solvedCache = new Set(await api.solvedExercises());
  return new Set(solvedCache);
}

/** Exercise ids the learner has solved (judged Accepted) at least once. */
export function solvedExercises(): Set<string> {
  return new Set(solvedCache);
}

/** Record a solve. The cache updates immediately so the caller can re-render
 * from the returned set; the SQLite write follows and is best-effort, since
 * blocking an Accepted verdict on a disk write would be worse than losing a
 * mark that the next solve re-adds. */
export function markExerciseSolved(id: string): Set<string> {
  if (!solvedCache.has(id)) {
    solvedCache.add(id);
    void api.setExercisesSolved([id], true).catch(() => {});
  }
  return new Set(solvedCache);
}

/** Forget that a set of exercises was ever solved, so a unit can be worked
 * again from scratch. Only the solved marks go — the learner's own drafts
 * (`poodcode:learn-ex:*`) are their writing, not progress, and are left alone
 * so a reset never destroys work they might still want to read. */
export function unmarkExercisesSolved(ids: string[]): Set<string> {
  const gone = ids.filter((id) => solvedCache.delete(id));
  if (gone.length > 0) void api.setExercisesSolved(gone, false).catch(() => {});
  return new Set(solvedCache);
}
