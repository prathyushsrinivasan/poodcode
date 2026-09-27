/**
 * Browse's remembered state: filter presets and visible columns
 * (UI_ROADMAP H1).
 *
 * A preset is a whole filter with a name — "unsolved Mediums in my weakest
 * topic" — so a question you ask the problem bank every week is one click
 * instead of seven. Presets and columns are per-viewer conveniences, so they
 * live in localStorage, with every read tolerant of a stored shape from an
 * older version.
 */

import { emptyFilter, type ProblemFilter } from "./filters";

export interface BrowseState {
  filter: ProblemFilter;
  /** Only problems that are not on the curriculum (your own). */
  mineOnly: boolean;
  /** Only problems TypeScript Mastery has reached. */
  solvableNow: boolean;
}

export interface Preset extends BrowseState {
  id: string;
  name: string;
  /** Built-in presets cannot be deleted. */
  builtin?: boolean;
}

export const BUILTIN_PRESETS: Preset[] = [
  {
    id: "builtin:unsolved-medium",
    name: "Unsolved Mediums",
    builtin: true,
    filter: { ...emptyFilter, difficulties: ["Medium"], status: "unsolved" },
    mineOnly: false,
    solvableNow: false,
  },
  {
    id: "builtin:weak",
    name: "Solved but shaky",
    builtin: true,
    filter: { ...emptyFilter, status: "solved", weakConfidence: true, sort: "confidence" },
    mineOnly: false,
    solvableNow: false,
  },
  {
    id: "builtin:struggled",
    name: "Failed twice or more",
    builtin: true,
    filter: { ...emptyFilter, failedTwice: true },
    mineOnly: false,
    solvableNow: false,
  },
  {
    id: "builtin:favorites",
    name: "Favorites",
    builtin: true,
    filter: { ...emptyFilter, favoritesOnly: true },
    mineOnly: false,
    solvableNow: false,
  },
];

/** Merge a stored filter onto the empty one, so a missing field is never undefined. */
export function normaliseFilter(raw: unknown): ProblemFilter {
  if (!raw || typeof raw !== "object") return emptyFilter;
  return { ...emptyFilter, ...(raw as Partial<ProblemFilter>) };
}

export function parsePresets(raw: string | null): Preset[] {
  if (!raw) return [];
  try {
    const v: unknown = JSON.parse(raw);
    if (!Array.isArray(v)) return [];
    return v
      .filter((p): p is Record<string, unknown> => !!p && typeof p === "object")
      .filter((p) => typeof p.id === "string" && typeof p.name === "string")
      .map((p) => ({
        id: p.id as string,
        name: p.name as string,
        filter: normaliseFilter(p.filter),
        mineOnly: p.mineOnly === true,
        solvableNow: p.solvableNow === true,
      }));
  } catch {
    return [];
  }
}

/** Add a preset, replacing one with the same name (case-insensitive). */
export function savePreset(list: Preset[], name: string, state: BrowseState, now = Date.now()): Preset[] {
  const trimmed = name.trim();
  if (!trimmed) return list;
  const rest = list.filter((p) => p.name.toLowerCase() !== trimmed.toLowerCase());
  return [...rest, { id: `user:${now}`, name: trimmed, ...state }];
}

export function deletePreset(list: Preset[], id: string): Preset[] {
  return list.filter((p) => p.id !== id);
}

/** Whether the current state is exactly a preset — its chip then shows as on. */
export function matchesPreset(p: BrowseState, state: BrowseState): boolean {
  return (
    p.mineOnly === state.mineOnly &&
    p.solvableNow === state.solvableNow &&
    JSON.stringify(normaliseFilter(p.filter)) === JSON.stringify(normaliseFilter(state.filter))
  );
}

/** How many filters are set, for the "Clear n filters" affordance. */
export function activeFilterCount(state: BrowseState): number {
  const f = state.filter;
  let n = 0;
  if (f.search.trim()) n++;
  n += f.difficulties.length + f.topics.length + f.companies.length + f.stages.length + f.units.length;
  if (f.status !== "all") n++;
  for (const flag of [f.favoritesOnly, f.needsReview, f.weakConfidence, f.overTime, f.failedTwice, f.neverOptimal]) {
    if (flag) n++;
  }
  if (state.mineOnly) n++;
  if (state.solvableNow) n++;
  return n;
}

// ---- Columns ----------------------------------------------------------------

export const COLUMNS = [
  { key: "favorite", label: "Favorite" },
  { key: "difficulty", label: "Difficulty" },
  { key: "unit", label: "Taught in" },
  { key: "topics", label: "Topics" },
  { key: "status", label: "Status" },
  { key: "attempts", label: "Attempts" },
  { key: "confidence", label: "Confidence" },
  { key: "solved", label: "Last solved" },
] as const;

export type ColumnKey = (typeof COLUMNS)[number]["key"];

export const DEFAULT_COLUMNS: ColumnKey[] = ["favorite", "difficulty", "unit", "status", "confidence", "solved"];

export function parseColumns(raw: string | null): ColumnKey[] {
  if (!raw) return DEFAULT_COLUMNS;
  try {
    const v: unknown = JSON.parse(raw);
    if (!Array.isArray(v)) return DEFAULT_COLUMNS;
    const known = new Set<string>(COLUMNS.map((c) => c.key));
    const keys = v.filter((k): k is ColumnKey => typeof k === "string" && known.has(k));
    // Keep table order stable whatever order they were stored in.
    return COLUMNS.map((c) => c.key).filter((k) => keys.includes(k));
  } catch {
    return DEFAULT_COLUMNS;
  }
}

export function toggleColumn(cols: ColumnKey[], key: ColumnKey): ColumnKey[] {
  const next = cols.includes(key) ? cols.filter((k) => k !== key) : [...cols, key];
  return COLUMNS.map((c) => c.key).filter((k) => next.includes(k));
}

// ---- Keyboard row navigation --------------------------------------------------

/** The row index a key moves to, or null when the key is not a row key. */
export function nextRow(key: string, at: number, count: number, page = 10): number | null {
  if (count === 0) return null;
  switch (key) {
    case "ArrowDown":
      return Math.min(count - 1, at + 1);
    case "ArrowUp":
      return Math.max(0, at - 1);
    case "PageDown":
      return Math.min(count - 1, at + page);
    case "PageUp":
      return Math.max(0, at - page);
    case "Home":
      return 0;
    case "End":
      return count - 1;
    default:
      return null;
  }
}
