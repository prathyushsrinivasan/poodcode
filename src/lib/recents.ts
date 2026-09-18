/**
 * What you opened recently, for the command palette.
 *
 * With nothing typed, the palette listed the same eleven pages every time and
 * then 650 problems in seed order — which is a directory, not a shortcut. The
 * thing you actually want at that moment is almost always something you had
 * open a minute ago.
 *
 * Stored per viewer in localStorage: it is a convenience, it is specific to
 * this machine, and losing it costs nothing.
 */

const KEY = "poodcode:recents";
const LIMIT = 12;

export interface Recent {
  /** Route to open. Doubles as the identity, so revisiting moves it up. */
  to: string;
  label: string;
  hint?: string;
  at: number;
}

export function readRecents(): Recent[] {
  try {
    const raw = localStorage.getItem(KEY);
    const list: unknown = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(list)) return [];
    return list
      .filter((r): r is Recent => !!r && typeof r.to === "string" && typeof r.label === "string")
      .sort((a, b) => b.at - a.at)
      .slice(0, LIMIT);
  } catch {
    return [];
  }
}

/** Record a visit. Most recent first, one entry per route. */
export function pushRecent(entry: Omit<Recent, "at">): void {
  try {
    const next = [{ ...entry, at: Date.now() }, ...readRecents().filter((r) => r.to !== entry.to)];
    localStorage.setItem(KEY, JSON.stringify(next.slice(0, LIMIT)));
  } catch {
    /* a private window, or full storage — the palette just has no history */
  }
}

export function clearRecents(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* nothing to clear */
  }
}
