import type { Difficulty, Problem, SolvedStatus } from "../types";

export type SortKey =
  | "title"
  | "difficulty"
  | "recently_added"
  | "recently_solved"
  | "attempts"
  | "confidence";

/**
 * Which curriculum unit and stage each problem belongs to.
 *
 * Passed in rather than read from the `Problem`, because a problem does not know
 * — the curriculum owns that relation, and a problem you authored belongs to no
 * unit at all. Browse gained a unit *column* but no way to filter by it, which
 * is the obvious query once the column exists.
 */
export interface UnitLookup {
  unitOf: (slug: string) => string | undefined;
  stageOf: (slug: string) => string | undefined;
}

export interface ProblemFilter {
  search: string;
  difficulties: Difficulty[];
  topics: string[];
  companies: string[];
  /** Unit keys; empty means every unit. */
  units: string[];
  /** Stage keys; empty means every stage. */
  stages: string[];
  status: SolvedStatus | "all";
  favoritesOnly: boolean;
  needsReview: boolean; // last_solved_at older than 14 days, or low confidence
  weakConfidence: boolean; // confidence <= 2
  // Search-by-weakness predicates.
  overTime: boolean; // cumulative time spent > 45 min
  failedTwice: boolean; // at least two non-accepted attempts
  neverOptimal: boolean; // solved but confidence < 4
  sort: SortKey;
}

export const emptyFilter: ProblemFilter = {
  search: "",
  difficulties: [],
  topics: [],
  companies: [],
  units: [],
  stages: [],
  status: "all",
  favoritesOnly: false,
  needsReview: false,
  weakConfidence: false,
  overTime: false,
  failedTwice: false,
  neverOptimal: false,
  sort: "difficulty",
};

const OVER_TIME_SECONDS = 45 * 60;

const DIFF_ORDER: Record<Difficulty, number> = { Intro: 0, Easy: 1, Medium: 2, Hard: 3 };

function daysSince(iso: string | null): number {
  if (!iso) return Infinity;
  const then = new Date(iso.replace(" ", "T")).getTime();
  if (Number.isNaN(then)) return Infinity;
  return (Date.now() - then) / 86_400_000;
}

/** Pure, testable filtering + sorting of the problem list.
 *
 * `units` supplies the curriculum relation; without it the unit and stage
 * filters simply match nothing rather than silently matching everything, because
 * "show me graph-traversal" answered with the whole bank is worse than an empty
 * result you can see is empty. */
export function applyFilter(
  problems: Problem[],
  f: ProblemFilter,
  units?: UnitLookup
): Problem[] {
  const q = f.search.trim().toLowerCase();
  let out = problems.filter((p) => {
    if (q) {
      const hay = (
        p.title +
        " " +
        p.topics.join(" ") +
        " " +
        p.companies.join(" ") +
        " " +
        p.subtopics.join(" ")
      ).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    if (f.difficulties.length && !f.difficulties.includes(p.difficulty)) return false;
    if (f.topics.length && !f.topics.some((t) => p.topics.includes(t))) return false;
    if (f.companies.length && !f.companies.some((c) => p.companies.includes(c)))
      return false;
    if (f.units.length) {
      const k = units?.unitOf(p.slug);
      if (!k || !f.units.includes(k)) return false;
    }
    if (f.stages.length) {
      const k = units?.stageOf(p.slug);
      if (!k || !f.stages.includes(k)) return false;
    }
    if (f.status !== "all" && p.solved_status !== f.status) return false;
    if (f.favoritesOnly && !p.is_favorite) return false;
    if (f.weakConfidence && !(p.confidence <= 2 && p.solved_status === "solved"))
      return false;
    if (
      f.needsReview &&
      !(p.solved_status === "solved" && (p.confidence <= 2 || daysSince(p.last_solved_at) > 14))
    )
      return false;
    if (f.overTime && !(p.time_taken_seconds > OVER_TIME_SECONDS)) return false;
    if (f.failedTwice && !(p.attempts_count - p.success_count >= 2)) return false;
    if (f.neverOptimal && !(p.solved_status === "solved" && p.confidence < 4)) return false;
    return true;
  });

  out = [...out].sort((a, b) => {
    switch (f.sort) {
      case "title":
        return a.title.localeCompare(b.title);
      case "recently_added":
        return b.created_at.localeCompare(a.created_at);
      case "recently_solved":
        return (b.last_solved_at ?? "").localeCompare(a.last_solved_at ?? "");
      case "attempts":
        return b.attempts_count - a.attempts_count;
      case "confidence":
        return a.confidence - b.confidence;
      case "difficulty":
      default:
        // Curated easiest→hardest rank; fall back to tier + title if unset.
        return (
          a.order - b.order ||
          DIFF_ORDER[a.difficulty] - DIFF_ORDER[b.difficulty] ||
          a.title.localeCompare(b.title)
        );
    }
  });
  return out;
}
