// Pure helpers for the flashcard deck (table `flashcards`, SM-2 scheduled in
// src-tauri/src/repo.rs). The page decides nothing on its own; these do, so
// they can be tested without a backend.

import type { Flashcard } from "../types";

/** SM-2 recall grades, in the order the buttons show them. `quality` is what
 * `grade_flashcard` takes (0..3, the same scale as problem reviews). */
export const GRADES = [
  { quality: 0, label: "Again", key: "1" },
  { quality: 1, label: "Hard", key: "2" },
  { quality: 2, label: "Good", key: "3" },
  { quality: 3, label: "Easy", key: "4" },
] as const;

const TRACK_TITLES: Record<string, string> = {
  typescript: "TypeScript Mastery",
  java: "Java Mastery",
};

/** Where a card came from, in words. Sources are machine keys for the cards the
 * app seeds (`mastery:<track>:w<n>`, `seed:<topic>`, `manual`) and already
 * human-readable for the ones a page writes directly, which pass through. */
export function sourceLabel(source: string): string {
  const mastery = /^mastery:([^:]+):w(\d+)$/.exec(source);
  if (mastery) {
    const track = TRACK_TITLES[mastery[1]] ?? `${mastery[1]} Mastery`;
    return `${track} · Week ${mastery[2]}`;
  }
  if (source.startsWith("seed:")) return "Pattern card";
  if (source === "manual" || source === "") return "Your card";
  return source;
}

/** Cards grouped by where they came from, largest group first — for the
 * "all cards" list, where 300 cards in one undivided column is unreadable. */
export function groupBySource(cards: Flashcard[]): [string, Flashcard[]][] {
  const groups = new Map<string, Flashcard[]>();
  for (const c of cards) {
    const label = sourceLabel(c.source);
    const list = groups.get(label);
    if (list) list.push(c);
    else groups.set(label, [c]);
  }
  return [...groups.entries()].sort((a, b) => b[1].length - a[1].length || a[0].localeCompare(b[0]));
}
