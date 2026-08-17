// Chapter-completion state for the Learn tab. This is a UI convenience (a "I've
// been through this chapter" checkmark), so it lives in localStorage — the same
// place the Learn tab keeps exercise drafts (`poodcode:learn-ex:*`).
//
// Flashcard *mastery* is NOT here: vocabulary cards use real spaced repetition
// persisted in SQLite (see the `card_reviews` table + api.cardReviews/gradeCard).

const DONE_KEY = "poodcode:learn-done"; // JSON array of completed concept keys

function readSet(k: string): Set<string> {
  try {
    const raw = JSON.parse(localStorage.getItem(k) || "[]");
    return new Set(Array.isArray(raw) ? raw : []);
  } catch {
    return new Set();
  }
}

function writeSet(k: string, s: Set<string>) {
  localStorage.setItem(k, JSON.stringify([...s]));
}

export function doneChapters(): Set<string> {
  return readSet(DONE_KEY);
}

export function setChapterDone(key: string, done: boolean): Set<string> {
  const s = readSet(DONE_KEY);
  if (done) s.add(key);
  else s.delete(key);
  writeSet(DONE_KEY, s);
  return s;
}

/** Stable id for a vocabulary card: concept key + the term on its front. */
export function cardId(conceptKey: string, front: string): string {
  return `${conceptKey}#${front}`;
}
