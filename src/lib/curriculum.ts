import type { CurriculumUnit, DsaCurriculum, Problem } from "../types";

/**
 * Hydrating the DSA curriculum: joining the authored teaching spine
 * (seeds/dsa_curriculum.json — stages, units, rungs of problem *slugs*) to the
 * learner's actual problem rows, and deriving every number the UI shows.
 *
 * There is no curriculum progress table, by design. A unit's state is a
 * function of the solved status the `problems` table already records, so the
 * curriculum can be re-sequenced in a later release without a migration, and a
 * problem solved from anywhere in the app (Browse, Random Practice, a Mastery
 * week) counts here immediately.
 *
 * Everything in this file is pure and framework-free so it can be unit-tested;
 * the page does nothing but render what `hydrate` returns.
 */

/** Fraction of a unit's problems that counts as having learned the technique. */
export const SOLID_RATIO = 0.6;

export type UnitStatus = "new" | "started" | "solid" | "complete";

export interface RungItem {
  slug: string;
  /** Null when the bank does not contain this slug (an older seed version). */
  problem: Problem | null;
  /** The authored "why this problem is on this rung", or "". */
  note: string;
}

export interface HydratedRung {
  title: string;
  purpose: string;
  items: RungItem[];
  solved: number;
  /** Counts only problems that resolved to a real row. */
  total: number;
}

export interface HydratedUnit {
  unit: CurriculumUnit;
  rungs: HydratedRung[];
  solved: number;
  total: number;
  /** Attempted but not solved — what the "in progress" badge counts. */
  attempted: number;
  status: UnitStatus;
  /**
   * Whether every prerequisite is at least `solid`. Advisory, never enforced:
   * an unready unit is still openable, because a learner who already knows
   * heaps should not have to solve their way past the stacks unit to say so.
   */
  ready: boolean;
  /** Titles of the prerequisite units, for saying "builds on Hashing" in the UI. */
  prereqTitles: string[];
  /** First unsolved problem, walking the rungs in order. */
  next: Problem | null;
}

export interface HydratedStage {
  key: string;
  title: string;
  icon: string;
  tagline: string;
  goal: string;
  units: HydratedUnit[];
  solved: number;
  total: number;
}

export interface HydratedCurriculum {
  title: string;
  subtitle: string;
  intro: string;
  stages: HydratedStage[];
  solved: number;
  total: number;
  /** Where the "Continue" button goes: the first unfinished, ready unit. */
  next: { unit: HydratedUnit; problem: Problem | null } | null;
  /** Slug → unit, for showing which unit teaches a problem in Browse. */
  unitBySlug: Map<string, CurriculumUnit>;
  /** Problems in the library that no unit schedules — i.e. ones you added. */
  unplaced: Problem[];
}

function statusOf(solved: number, total: number, attempted: number): UnitStatus {
  if (total === 0) return "new";
  if (solved >= total) return "complete";
  if (solved >= Math.ceil(total * SOLID_RATIO)) return "solid";
  if (solved > 0 || attempted > 0) return "started";
  return "new";
}

/** A unit counts as cleared — for the purpose of unlocking what follows. */
export function isCleared(status: UnitStatus): boolean {
  return status === "solid" || status === "complete";
}

/**
 * Join the curriculum to the learner's problems.
 *
 * Units are processed in curriculum order, which is what makes the single pass
 * enough: the generator guarantees every prerequisite appears before the unit
 * that names it, so a unit's readiness can be decided from units already seen.
 */
export function hydrate(
  curriculum: DsaCurriculum | null,
  problems: Problem[]
): HydratedCurriculum {
  const bySlug = new Map(problems.map((p) => [p.slug, p]));
  const unitBySlug = new Map<string, CurriculumUnit>();
  const statusByUnit = new Map<string, UnitStatus>();
  const titleByUnit = new Map<string, string>();
  const placed = new Set<string>();

  const stages: HydratedStage[] = (curriculum?.stages ?? []).map((stage) => {
    const units: HydratedUnit[] = stage.units.map((unit) => {
      let solved = 0;
      let total = 0;
      let attempted = 0;
      let next: Problem | null = null;

      const rungs: HydratedRung[] = unit.rungs.map((rung) => {
        let rungSolved = 0;
        let rungTotal = 0;
        const items: RungItem[] = rung.slugs.map((slug) => {
          const problem = bySlug.get(slug) ?? null;
          unitBySlug.set(slug, unit);
          placed.add(slug);
          if (problem) {
            rungTotal++;
            if (problem.solved_status === "solved") rungSolved++;
            else {
              if (problem.solved_status === "attempted") attempted++;
              if (!next) next = problem;
            }
          }
          return { slug, problem, note: rung.notes[slug] ?? "" };
        });
        solved += rungSolved;
        total += rungTotal;
        return { title: rung.title, purpose: rung.purpose, items, solved: rungSolved, total: rungTotal };
      });

      const status = statusOf(solved, total, attempted);
      statusByUnit.set(unit.key, status);
      titleByUnit.set(unit.key, unit.title);
      const ready = unit.prereqs.every((k) => {
        const s = statusByUnit.get(k);
        // An unknown prerequisite cannot block: the generator forbids it, and
        // silently locking the whole ladder would be the worse failure.
        return s === undefined || isCleared(s);
      });
      const prereqTitles = unit.prereqs.map((k) => titleByUnit.get(k) ?? k);

      return { unit, rungs, solved, total, attempted, status, ready, prereqTitles, next };
    });

    return {
      key: stage.key,
      title: stage.title,
      icon: stage.icon,
      tagline: stage.tagline,
      goal: stage.goal,
      units,
      solved: units.reduce((n, u) => n + u.solved, 0),
      total: units.reduce((n, u) => n + u.total, 0),
    };
  });

  const all = stages.flatMap((s) => s.units);
  // Prefer the first unfinished unit you are ready for; if every ready unit is
  // finished, fall back to the first unfinished one so "Continue" never dies.
  const unfinished = all.filter((u) => u.status !== "complete");
  const target = unfinished.find((u) => u.ready) ?? unfinished[0] ?? null;

  return {
    title: curriculum?.title ?? "",
    subtitle: curriculum?.subtitle ?? "",
    intro: curriculum?.intro ?? "",
    stages,
    solved: stages.reduce((n, s) => n + s.solved, 0),
    total: stages.reduce((n, s) => n + s.total, 0),
    next: target ? { unit: target, problem: target.next } : null,
    unitBySlug,
    unplaced: problems.filter((p) => !placed.has(p.slug)),
  };
}

/** Find one unit by key across every stage. */
export function findUnit(c: HydratedCurriculum, key: string): HydratedUnit | null {
  for (const stage of c.stages) {
    const hit = stage.units.find((u) => u.unit.key === key);
    if (hit) return hit;
  }
  return null;
}

/** The unit before and after `key` in curriculum order, for unit-page paging. */
export function neighbours(
  c: HydratedCurriculum,
  key: string
): { prev: HydratedUnit | null; next: HydratedUnit | null } {
  const all = c.stages.flatMap((s) => s.units);
  const i = all.findIndex((u) => u.unit.key === key);
  if (i < 0) return { prev: null, next: null };
  return { prev: all[i - 1] ?? null, next: all[i + 1] ?? null };
}

/**
 * Search units by title, tagline, signal wording, pitfall symptom, skeleton
 * name — and the internals prose.
 *
 * Internals is included because it is where the searchable *nouns* live: "ring
 * buffer", "sift down", "sentinel", "load factor". Someone who half-remembers a
 * term is far more likely to type that than the title of the unit that taught
 * it, and matching on it is the difference between finding the page and not.
 */
export function searchUnits(c: HydratedCurriculum, query: string): HydratedUnit[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  return c.stages
    .flatMap((s) => s.units)
    .filter((u) => {
      const hay = [
        u.unit.title,
        u.unit.tagline,
        u.unit.internals,
        ...u.unit.signals.map((s) => `${s.when} ${s.reach_for}`),
        ...u.unit.pitfalls.map((p) => p.symptom),
        ...u.unit.skeletons.map((s) => s.name),
        ...u.unit.traces.map((t) => t.title),
      ]
        .join(" ")
        .toLowerCase();
      return hay.includes(q);
    });
}
