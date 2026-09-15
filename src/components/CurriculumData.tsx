import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { DsaCurriculum } from "../types";
import {
  hydrate,
  parseSkipped,
  serialiseSkipped,
  SKIPPED_SETTING,
  type HydratedCurriculum,
  type UnitStatus,
} from "../lib/curriculum";

/**
 * The curriculum seed, fetched once per session.
 *
 * The seed is embedded in the binary and cannot change while the app is running,
 * so re-fetching and re-parsing 480 KB of JSON on every mount of every Library
 * page was work with no possible benefit. The learner's *problems* are a
 * different matter and are still re-fetched every time — that is what keeps a
 * solve recorded elsewhere from showing stale progress here.
 *
 * A module-level promise rather than a store: there is nothing to invalidate, no
 * subscribers to notify, and a failed fetch should be retried rather than
 * cached, which is why the promise is cleared on rejection.
 */
let curriculumPromise: Promise<DsaCurriculum | null> | null = null;

export function loadCurriculumSeed(): Promise<DsaCurriculum | null> {
  if (!curriculumPromise) {
    curriculumPromise = api.dsaCurriculum().catch((e) => {
      curriculumPromise = null; // a transient failure must not be permanent
      throw e;
    });
  }
  return curriculumPromise;
}

/** Loads the curriculum, the learner's problems and the skipped-unit list, and
 * joins them.
 *
 * All three Library pages need exactly this trio, and the join is cheap (one
 * pass over 271 problems). The curriculum comes from the session-wide cache; the
 * problems and settings are re-fetched, because those do change.
 *
 * `setSkipped` writes the settings row and re-joins in place, so marking a unit
 * known updates every badge and the "up next" target immediately. */
export function useCurriculumData() {
  const [data, setData] = useState<HydratedCurriculum | null>(null);
  const [error, setError] = useState<string>("");

  const load = useCallback(() => {
    Promise.all([
      loadCurriculumSeed().catch(() => null),
      api.listProblems(),
      api.getSettings().catch(() => ({}) as Record<string, string>),
    ])
      .then(([c, problems, settings]) =>
        setData(hydrate(c, problems, parseSkipped(settings[SKIPPED_SETTING])))
      )
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(load, [load]);

  const setSkipped = useCallback(
    async (unitKeys: Iterable<string>, known: boolean) => {
      const wanted = [...unitKeys];
      const settings = await api.getSettings().catch(() => ({}) as Record<string, string>);
      const next = parseSkipped(settings[SKIPPED_SETTING]);
      for (const k of wanted) {
        if (known) next.add(k);
        else next.delete(k);
      }
      await api.setSetting(SKIPPED_SETTING, serialiseSkipped(next));
      load();
    },
    [load]
  );

  return { data, error, reload: load, setSkipped };
}

const STATUS_META: Record<UnitStatus, { label: string; colour: string; icon: string }> = {
  new: { label: "Not started", colour: "var(--text-faint)", icon: "○" },
  started: { label: "In progress", colour: "var(--accent)", icon: "◐" },
  solid: { label: "Solid", colour: "var(--medium)", icon: "◕" },
  complete: { label: "Complete", colour: "var(--good)", icon: "●" },
};

/** A unit's state, as a badge. "Solid" deliberately arrives before every
 * problem is solved — the bar for moving on is knowing the technique, not
 * clearing the list.
 *
 * `stale` mutes a cleared unit whose practice has aged out of its interval. It
 * is not a fourth status: the unit *was* cleared, and that is still true. What
 * has expired is the evidence, so the badge keeps its label and loses its
 * colour, which is exactly the claim being made. */
export function StatusBadge({
  status,
  stale = false,
  skipped = false,
}: {
  status: UnitStatus;
  stale?: boolean;
  /** Marked "I already know this" — deliberately not styled as earned green. */
  skipped?: boolean;
}) {
  if (skipped) {
    return (
      <span
        className="badge"
        style={{ color: "var(--medium)", borderColor: "var(--medium)", borderStyle: "dashed" }}
        title="You marked this known. It counts as cleared, but the app is not claiming you solved it here."
      >
        ✓ Known
      </span>
    );
  }
  const m = STATUS_META[status];
  const colour = stale ? "var(--text-faint)" : m.colour;
  return (
    <span
      className="badge"
      style={{ color: colour, borderColor: colour }}
      title={stale ? `${m.label}, but not practised recently` : m.label}
    >
      {m.icon} {m.label}
      {stale && " · stale"}
    </span>
  );
}

/**
 * Slug → the unit that teaches it, built once and kept.
 *
 * `TaughtIn` used to fetch the whole seed and run a full `hydrate()` — building
 * all 33 units, every rung, every trace — to render one badge, on every Solve
 * page open. The badge needs four strings, so the index holds four strings:
 * walking the rungs directly skips the hydration entirely, and the seed itself
 * now comes from the session cache.
 */
export interface TaughtInUnit {
  key: string;
  title: string;
  icon: string;
  tagline: string;
}

export interface SlugPlacement {
  unit: TaughtInUnit;
  rungTitle: string;
  /** Every slug on that rung, in ladder order, so "next in this rung" is a walk. */
  rungSlugs: string[];
}

let unitIndexPromise: Promise<Map<string, SlugPlacement>> | null = null;

export function loadUnitIndex(): Promise<Map<string, SlugPlacement>> {
  if (!unitIndexPromise) {
    unitIndexPromise = loadCurriculumSeed()
      .then((c) => {
        const index = new Map<string, SlugPlacement>();
        for (const stage of c?.stages ?? []) {
          for (const u of stage.units) {
            const unit = { key: u.key, title: u.title, icon: u.icon, tagline: u.tagline };
            for (const rung of u.rungs) {
              const entry = { unit, rungTitle: rung.title, rungSlugs: rung.slugs };
              for (const slug of rung.slugs) index.set(slug, entry);
            }
          }
        }
        return index;
      })
      .catch((e) => {
        unitIndexPromise = null;
        throw e;
      });
  }
  return unitIndexPromise;
}

/** "Taught in <unit>" — the way back from a problem to the technique.
 *
 * Rendered on the Solve page, where you may well have arrived from the review
 * queue or a random pick with no idea which pattern the problem is drilling.
 *
 * Renders nothing for a problem you authored, which belongs to no unit. */
export function TaughtIn({ slug }: { slug: string }) {
  const [where, setWhere] = useState<SlugPlacement | null>(null);

  useEffect(() => {
    let live = true;
    loadUnitIndex()
      .then((index) => {
        if (live) setWhere(index.get(slug) ?? null);
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [slug]);

  if (!where) return null;
  return (
    <span className="badge" title={`${where.unit.tagline} · ${where.rungTitle}`}>
      Taught in{" "}
      <Link to={`/library/unit/${where.unit.key}`}>
        {where.unit.icon} {where.unit.title}
      </Link>
    </span>
  );
}

/**
 * "Next in this rung →", on the Solve page.
 *
 * After a solve you were left on the Solve page, whose only route onward was
 * `TaughtIn` → the unit page → re-scanning the rungs for the next unsolved row.
 * A rung is explicitly "a group of problems drilling the same twist", so the
 * next one on it is almost always what you wanted; making you navigate two pages
 * to find it is how a drill loses its momentum.
 *
 * Walks the rung in ladder order for the first problem after this one that is
 * not solved. Falls back to the first unsolved *anywhere* on the rung, so
 * arriving at the last row still moves you forward rather than dead-ending.
 */
export function NextInRung({ slug }: { slug: string }) {
  const [next, setNext] = useState<{ id: number; title: string; rung: string } | null>(null);

  useEffect(() => {
    let live = true;
    Promise.all([loadUnitIndex(), api.listProblems()])
      .then(([index, problems]) => {
        if (!live) return;
        const where = index.get(slug);
        if (!where) return setNext(null);
        const bySlug = new Map(problems.map((p) => [p.slug, p]));
        const unsolved = (s: string) => {
          const p = bySlug.get(s);
          return p && p.solved_status !== "solved" && s !== slug ? p : null;
        };
        const at = where.rungSlugs.indexOf(slug);
        const after = where.rungSlugs.slice(at + 1).map(unsolved).find(Boolean);
        const anywhere = where.rungSlugs.map(unsolved).find(Boolean);
        const pick = after ?? anywhere ?? null;
        setNext(pick ? { id: pick.id, title: pick.title, rung: where.rungTitle } : null);
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [slug]);

  if (!next) return null;
  return (
    <Link
      to={`/solve/${next.id}`}
      className="badge"
      title={`The next unsolved problem on the "${next.rung}" rung`}
      style={{ borderColor: "var(--accent)", color: "var(--accent)" }}
    >
      Next in {next.rung} → {next.title}
    </Link>
  );
}

export function UnitProgress({
  solved,
  total,
  stale = false,
}: {
  solved: number;
  total: number;
  /** Mute the bar for a cleared unit whose practice has aged out. */
  stale?: boolean;
}) {
  const pct = total ? (solved / total) * 100 : 0;
  return (
    <div
      className="progress-track"
      title={stale ? `${solved} of ${total} solved, but not recently` : `${solved} of ${total} solved`}
    >
      <span
        className="progress-fill"
        style={{
          display: "block",
          width: `${pct}%`,
          background: stale
            ? "var(--text-faint)"
            : pct === 100
              ? "var(--good)"
              : "var(--accent)",
        }}
      />
    </div>
  );
}
