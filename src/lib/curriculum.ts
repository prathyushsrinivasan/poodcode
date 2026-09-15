import type { CurriculumUnit, DsaCurriculum, Problem } from "../types";
import { intervalDays } from "./revision";

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

/**
 * How long a cleared unit stays trustworthy before it should be re-practised,
 * as indices into `revision.LADDER` (= [1, 3, 7, 14, 30, 90] days).
 *
 * Without this, a unit reaches `solid` at 60% and is green forever, so at month
 * three a green unit and a *remembered* unit look identical — which is the one
 * thing a progress display exists to distinguish. Clearing a unit buys 30 days;
 * finishing every problem in it buys 90, because having solved all of them is
 * evidence of a stronger memory and not merely more of it.
 *
 * Deliberately long. A unit that greys out a fortnight after you cleared it
 * would be noise, and noise is how a staleness signal gets ignored.
 */
const STALE_LADDER_INDEX: Record<"solid" | "complete", number> = {
  solid: 4,     // 30 days
  complete: 5,  // 90 days
};

/** Whole days between an ISO timestamp and `now`; `Infinity` for null/unparseable. */
export function daysSince(iso: string | null, now: Date = new Date()): number {
  if (!iso) return Infinity;
  const then = new Date(iso.replace(" ", "T")).getTime();
  if (Number.isNaN(then)) return Infinity;
  return Math.floor((now.getTime() - then) / 86_400_000);
}

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
  /** Surplus the unit does not ask of you. See `counted`. */
  optional: boolean;
  /**
   * Whether this rung's problems are folded into the unit's `solved`/`total`.
   *
   * Required rungs always are. An optional rung is counted only once you have
   * *started* it — touched at least one of its problems — so that ignoring it
   * costs nothing and working it is still credited. Counting it unconditionally
   * would make a unit's percentage punish you for skipping what it told you to
   * skip; excluding it unconditionally would throw away real work.
   */
  counted: boolean;
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
  /**
   * Titles of the prerequisites that are *not* yet cleared.
   *
   * Separate from `prereqTitles` because prereqs are a graph rather than a
   * chain: a unit can name two and have cleared one, and "builds on Trees,
   * Binary Search, which you have not finished" would then be a false
   * statement about Trees. The banner names only what is actually missing.
   */
  unmetPrereqTitles: string[];
  /** First unsolved problem, walking the rungs in order. */
  next: Problem | null;
  /**
   * Days since the most recent solve anywhere in this unit, or `Infinity` if
   * nothing here has ever been solved.
   */
  lastPractisedDays: number;
  /** Days a cleared unit stays fresh, or null when it is not cleared. */
  staleAfterDays: number | null;
  /**
   * A unit that was cleared and has not been touched since its interval ran
   * out. Derived, like everything else here — there is still no progress table,
   * so this survives a re-sequencing of the curriculum with no migration.
   */
  stale: boolean;
  /**
   * Marked "I already know this". Counts as cleared for readiness and for
   * choosing what is next, and renders distinctly from earned green: someone
   * who learned heaps elsewhere should not have to re-solve eleven problems or
   * watch the Library sit at 20% forever, but the display must not claim they
   * did the work either.
   */
  skipped: boolean;
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
 * The settings key holding the units marked "I already know this".
 *
 * A single comma-separated row in the existing key-value settings table rather
 * than a curriculum progress table: the no-progress-table property is what lets
 * the curriculum be re-sequenced without a migration, and one string does not
 * cost it. A key that no longer names a unit is simply ignored, so deleting a
 * unit needs no cleanup.
 */
export const SKIPPED_SETTING = "dsa.skipped";

export function parseSkipped(raw: string | undefined): Set<string> {
  return new Set((raw ?? "").split(",").map((s) => s.trim()).filter(Boolean));
}

export function serialiseSkipped(keys: Iterable<string>): string {
  return [...new Set(keys)].sort().join(",");
}

/**
 * The last unit you opened, so the curriculum page can offer to resume it.
 *
 * `data.next` — the first unfinished *ready* unit — is a reasonable default and
 * is not the same question. If you spent yesterday evening on Backtracking, "up
 * next" may well point at Trees, and the thing you actually want is the page you
 * closed. Both are offered; neither is guessed at.
 *
 * localStorage rather than settings: this is a per-device UI convenience like the
 * collapse state, not progress, and it should not travel in a backup.
 */
const LAST_UNIT_KEY = "poodcode:dsa:last-unit";

export function rememberLastUnit(unitKey: string): void {
  try {
    localStorage.setItem(LAST_UNIT_KEY, unitKey);
  } catch {
    /* a private window with storage blocked loses the convenience, nothing more */
  }
}

export function readLastUnit(): string | null {
  try {
    return localStorage.getItem(LAST_UNIT_KEY);
  } catch {
    return null;
  }
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
  problems: Problem[],
  /** Units marked "I already know this" (see `SKIPPED_SETTING`). */
  skipped: Set<string> = new Set(),
  /** Injectable so decay is testable; the app never passes it. */
  now: Date = new Date()
): HydratedCurriculum {
  const bySlug = new Map(problems.map((p) => [p.slug, p]));
  const unitBySlug = new Map<string, CurriculumUnit>();
  const clearedByUnit = new Map<string, boolean>();
  const titleByUnit = new Map<string, string>();
  const placed = new Set<string>();

  const stages: HydratedStage[] = (curriculum?.stages ?? []).map((stage) => {
    const units: HydratedUnit[] = stage.units.map((unit) => {
      let solved = 0;
      let total = 0;
      let attempted = 0;
      let next: Problem | null = null;
      let lastPractisedDays = Infinity;

      const rungs: HydratedRung[] = unit.rungs.map((rung) => {
        let rungSolved = 0;
        let rungTotal = 0;
        let rungTouched = 0;
        let rungAttempted = 0;
        let rungNext: Problem | null = null;
        const items: RungItem[] = rung.slugs.map((slug) => {
          const problem = bySlug.get(slug) ?? null;
          unitBySlug.set(slug, unit);
          placed.add(slug);
          if (problem) {
            rungTotal++;
            if (problem.solved_status === "solved") {
              rungSolved++;
              rungTouched++;
              // The *most recent* solve, because staleness asks "when did I last
              // touch this technique", not "when did I start it".
              lastPractisedDays = Math.min(
                lastPractisedDays,
                daysSince(problem.last_solved_at, now)
              );
            } else {
              if (problem.solved_status === "attempted") {
                rungAttempted++;
                rungTouched++;
              }
              if (!rungNext) rungNext = problem;
            }
          }
          return { slug, problem, note: rung.notes[slug] ?? "" };
        });

        const counted = !rung.optional || rungTouched > 0;
        if (counted) {
          solved += rungSolved;
          total += rungTotal;
          attempted += rungAttempted;
        }
        // `next` skips an untouched optional rung too: "what should I do now?"
        // must never point at work the unit has told you to skip. Once you have
        // started the rung it is ordinary work again and rejoins the walk.
        if (counted && !next && rungNext) next = rungNext;

        return {
          title: rung.title,
          purpose: rung.purpose,
          items,
          solved: rungSolved,
          total: rungTotal,
          optional: rung.optional,
          counted,
        };
      });

      const status = statusOf(solved, total, attempted);
      const isSkipped = skipped.has(unit.key);
      clearedByUnit.set(unit.key, isCleared(status) || isSkipped);
      titleByUnit.set(unit.key, unit.title);
      const unmet = unit.prereqs.filter((k) => {
        const cleared = clearedByUnit.get(k);
        // An unknown prerequisite cannot block: the generator forbids it, and
        // silently locking the whole ladder would be the worse failure.
        return cleared === false;
      });
      const ready = unmet.length === 0;
      const prereqTitles = unit.prereqs.map((k) => titleByUnit.get(k) ?? k);
      const unmetPrereqTitles = unmet.map((k) => titleByUnit.get(k) ?? k);

      const staleAfterDays =
        status === "solid" || status === "complete"
          ? intervalDays(STALE_LADDER_INDEX[status])
          : null;
      // `lastPractisedDays === Infinity` cannot coexist with a cleared status —
      // clearing requires solves — but a seed whose problems carry no
      // `last_solved_at` would produce it, and calling that unit stale would be
      // a guess. Require a real date.
      const stale =
        staleAfterDays !== null &&
        Number.isFinite(lastPractisedDays) &&
        lastPractisedDays > staleAfterDays;

      return {
        unit,
        rungs,
        solved,
        total,
        attempted,
        status,
        ready,
        prereqTitles,
        unmetPrereqTitles,
        next,
        lastPractisedDays,
        staleAfterDays,
        stale,
        skipped: isSkipped,
      };
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
  // A skipped unit is never the target — the whole point of saying "I know this"
  // is not to be sent back to it.
  const unfinished = all.filter((u) => u.status !== "complete" && !u.skipped);
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
 * Which part of a unit a search matched, ranked by how much it means.
 *
 * A title match is almost always the unit you wanted; an incidental hit in the
 * internals prose almost never is. The old search concatenated every field into
 * one haystack and returned `filter` order, so "stack" ranked the unit that
 * mentions a stack in passing above **Stacks**, and the result card never showed
 * *why* it matched — searching `"infinite loop"` returned unit cards with no hint
 * that the hit was a pitfall symptom, which is the one line you actually wanted.
 */
export type MatchField =
  | "title"
  | "tagline"
  | "signal"
  | "pitfall"
  | "skeleton"
  | "check"
  | "cost"
  | "trace"
  | "problem"
  | "prose";

const FIELD_RANK: Record<MatchField, number> = {
  title: 0,
  tagline: 1,
  signal: 2,
  pitfall: 3,
  skeleton: 4,
  check: 5,
  cost: 6,
  trace: 7,
  problem: 8,
  prose: 9,
};

const FIELD_LABEL: Record<MatchField, string> = {
  title: "title",
  tagline: "tagline",
  signal: "signal",
  pitfall: "pitfall",
  skeleton: "playbook",
  check: "self-check",
  cost: "costs",
  trace: "trace",
  problem: "problem",
  prose: "notes",
};

export interface UnitMatch {
  unit: HydratedUnit;
  field: MatchField;
  /** Human name for the field, for the result card. */
  label: string;
  /** The matching text, trimmed to a readable window around the hit. */
  snippet: string;
}

/** A window of `text` around the first occurrence of `q`, with ellipses. */
function snippetAround(text: string, q: string, width = 130): string {
  const flat = text.replace(/\s+/g, " ").trim();
  const at = flat.toLowerCase().indexOf(q);
  if (at < 0) return flat.slice(0, width);
  const start = Math.max(0, at - Math.floor((width - q.length) / 2));
  const end = Math.min(flat.length, start + width);
  return (start > 0 ? "…" : "") + flat.slice(start, end).trim() + (end < flat.length ? "…" : "");
}

/**
 * Search units, ranked, with the reason each one matched.
 *
 * The haystack is wider than it was: it now covers `why`, `model`, `build_it`,
 * the self-check questions, the cost-table operations and the rungs' problem
 * titles and notes. "Amortised" and "load factor" live in `costs` and `checks`
 * and were not searchable at all before — which is exactly the kind of
 * half-remembered term someone types.
 */
export function searchUnits(c: HydratedCurriculum, query: string): UnitMatch[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];

  const out: UnitMatch[] = [];
  for (const u of c.stages.flatMap((s) => s.units)) {
    // Ordered best-field-first; the first hit wins, so a unit is reported by the
    // most meaningful place it matched rather than all of them.
    const fields: [MatchField, string][] = [
      ["title", u.unit.title],
      ["tagline", u.unit.tagline],
      ...u.unit.signals.map(
        (s) => ["signal", `${s.when} → ${s.reach_for}. ${s.why}`] as [MatchField, string]
      ),
      ...u.unit.pitfalls.map(
        (p) => ["pitfall", `${p.symptom} — ${p.cause} Fix: ${p.fix}`] as [MatchField, string]
      ),
      ...u.unit.skeletons.map(
        (s) => ["skeleton", `${s.name} — ${s.when} ${s.note}`] as [MatchField, string]
      ),
      ...u.unit.checks.map((k) => ["check", `${k.q} ${k.a}`] as [MatchField, string]),
      ...u.unit.costs.map(
        (k) => ["cost", `${k.op}: ${k.time} / ${k.space}. ${k.note}`] as [MatchField, string]
      ),
      ...u.unit.traces.map((t) => ["trace", `${t.title} ${t.takeaway}`] as [MatchField, string]),
      ...u.rungs.flatMap((r) =>
        r.items.map(
          (i) =>
            [
              "problem",
              `${i.problem?.title ?? i.slug}${i.note ? ` — ${i.note}` : ""}`,
            ] as [MatchField, string]
        )
      ),
      ["prose", `${u.unit.why} ${u.unit.model} ${u.unit.internals} ${u.unit.build_it}`],
    ];

    for (const [field, text] of fields) {
      if (text.toLowerCase().includes(q)) {
        out.push({ unit: u, field, label: FIELD_LABEL[field], snippet: snippetAround(text, q) });
        break;
      }
    }
  }

  // Within a field, curriculum order — which is also difficulty order, so the
  // unit you are likelier to be ready for comes first.
  return out.sort((a, b) => FIELD_RANK[a.field] - FIELD_RANK[b.field]);
}
