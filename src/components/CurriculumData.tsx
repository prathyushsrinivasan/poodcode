import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { CurriculumUnit } from "../types";
import { hydrate, type HydratedCurriculum, type UnitStatus } from "../lib/curriculum";

/** Loads the curriculum and the learner's problems, and joins them.
 *
 * All three Library pages need exactly this pair, and the join is cheap (one
 * pass over 271 problems), so each page loads for itself rather than sharing a
 * store. That keeps a solve recorded on another page from showing stale
 * progress here: coming back re-fetches. */
export function useCurriculumData() {
  const [data, setData] = useState<HydratedCurriculum | null>(null);
  const [error, setError] = useState<string>("");

  const load = useCallback(() => {
    Promise.all([api.dsaCurriculum().catch(() => null), api.listProblems()])
      .then(([c, problems]) => setData(hydrate(c, problems)))
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(load, [load]);
  return { data, error, reload: load };
}

const STATUS_META: Record<UnitStatus, { label: string; colour: string; icon: string }> = {
  new: { label: "Not started", colour: "var(--text-faint)", icon: "○" },
  started: { label: "In progress", colour: "var(--accent)", icon: "◐" },
  solid: { label: "Solid", colour: "var(--medium)", icon: "◕" },
  complete: { label: "Complete", colour: "var(--good)", icon: "●" },
};

/** A unit's state, as a badge. "Solid" deliberately arrives before every
 * problem is solved — the bar for moving on is knowing the technique, not
 * clearing the list. */
export function StatusBadge({ status }: { status: UnitStatus }) {
  const m = STATUS_META[status];
  return (
    <span className="badge" style={{ color: m.colour, borderColor: m.colour }}>
      {m.icon} {m.label}
    </span>
  );
}

/** "Taught in <unit>" — the way back from a problem to the technique.
 *
 * Rendered on the Solve page, where you may well have arrived from the review
 * queue or a random pick with no idea which pattern the problem is drilling.
 * Hydrating against an empty problem list is deliberate: the slug → unit map is
 * built from the curriculum alone, so this costs one read and no join.
 *
 * Renders nothing for a problem you authored, which belongs to no unit. */
export function TaughtIn({ slug }: { slug: string }) {
  const [unit, setUnit] = useState<CurriculumUnit | null>(null);

  useEffect(() => {
    let live = true;
    api
      .dsaCurriculum()
      .then((c) => {
        if (live) setUnit(hydrate(c, []).unitBySlug.get(slug) ?? null);
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [slug]);

  if (!unit) return null;
  return (
    <span className="badge" title={unit.tagline}>
      Taught in{" "}
      <Link to={`/library/unit/${unit.key}`}>
        {unit.icon} {unit.title}
      </Link>
    </span>
  );
}

export function UnitProgress({ solved, total }: { solved: number; total: number }) {
  const pct = total ? (solved / total) * 100 : 0;
  return (
    <div className="progress-track" title={`${solved} of ${total} solved`}>
      <span
        className="progress-fill"
        style={{
          display: "block",
          width: `${pct}%`,
          background: pct === 100 ? "var(--good)" : "var(--accent)",
        }}
      />
    </div>
  );
}
