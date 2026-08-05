import type { Difficulty, Problem, SolvedStatus } from "../types";

export type SortKey =
  | "title"
  | "difficulty"
  | "recently_added"
  | "recently_solved"
  | "attempts"
  | "confidence";

export interface ProblemFilter {
  search: string;
  difficulties: Difficulty[];
  topics: string[];
  companies: string[];
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

/** Pure, testable filtering + sorting of the problem list. */
export function applyFilter(problems: Problem[], f: ProblemFilter): Problem[] {
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
