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

// Per-exercise "solved once" marks. Like the exercise DRAFTS above, this is a
// lightweight UI convenience (used to decide when a lesson/week has had all its
// problems solved so it can auto-complete), so it stays in localStorage.
const SOLVED_EX_KEY = "poodcode:learn-ex-solved";

function readSolved(): Set<string> {
  try {
    const raw = JSON.parse(localStorage.getItem(SOLVED_EX_KEY) || "[]");
    return new Set(Array.isArray(raw) ? raw : []);
  } catch {
    return new Set();
  }
}

/** Exercise ids the learner has solved (judged Accepted) at least once. */
export function solvedExercises(): Set<string> {
  return readSolved();
}

export function markExerciseSolved(id: string): Set<string> {
  const s = readSolved();
  if (!s.has(id)) {
    s.add(id);
    localStorage.setItem(SOLVED_EX_KEY, JSON.stringify([...s]));
  }
  return s;
}

/** Forget that a set of exercises was ever solved, so a unit can be worked
 * again from scratch. Only the solved marks go — the learner's own drafts
 * (`poodcode:learn-ex:*`) are their writing, not progress, and are left alone
 * so a reset never destroys work they might still want to read. */
export function unmarkExercisesSolved(ids: string[]): Set<string> {
  const s = readSolved();
  let changed = false;
  for (const id of ids) changed = s.delete(id) || changed;
  if (changed) localStorage.setItem(SOLVED_EX_KEY, JSON.stringify([...s]));
  return s;
}
