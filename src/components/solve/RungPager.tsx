/**
 * Previous / next within the rung this problem belongs to.
 *
 * Solve showed "Taught in <unit>" and a "next unsolved in the rung" link, but
 * there was no way to step backwards, and no sense of position — you could not
 * tell whether you were on the second of nine or the last one. A rung is a
 * deliberate ordering, so walking it should be one keystroke.
 */

import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../api";
import { loadUnitIndex } from "../CurriculumData";

interface Neighbour {
  id: number;
  title: string;
}

interface RungPosition {
  rungTitle: string;
  unitTitle: string;
  unitKey: string;
  at: number;
  total: number;
  prev: Neighbour | null;
  next: Neighbour | null;
}

export function useRungPosition(slug: string | undefined) {
  const [pos, setPos] = useState<RungPosition | null>(null);

  useEffect(() => {
    if (!slug) return;
    let live = true;
    Promise.all([loadUnitIndex(), api.listProblems()])
      .then(([index, problems]) => {
        if (!live) return;
        const where = index.get(slug);
        if (!where) return setPos(null);
        const bySlug = new Map(problems.map((p) => [p.slug, p]));
        const at = where.rungSlugs.indexOf(slug);
        const pick = (i: number): Neighbour | null => {
          const p = i >= 0 && i < where.rungSlugs.length ? bySlug.get(where.rungSlugs[i]) : undefined;
          return p ? { id: p.id, title: p.title } : null;
        };
        setPos({
          rungTitle: where.rungTitle,
          unitTitle: where.unit.title,
          unitKey: where.unit.key,
          at,
          total: where.rungSlugs.length,
          prev: pick(at - 1),
          next: pick(at + 1),
        });
      })
      .catch(() => {
        /* placement is context, not content — its absence costs nothing */
      });
    return () => {
      live = false;
    };
  }, [slug]);

  return pos;
}

export function RungPager({ pos }: { pos: RungPosition | null }) {
  const nav = useNavigate();

  // Alt+N / Alt+P walk the rung. Alt, because Ctrl+N and Ctrl+P are taken by
  // the editor and the OS.
  useEffect(() => {
    if (!pos) return;
    const onKey = (e: KeyboardEvent) => {
      if (!e.altKey) return;
      const k = e.key.toLowerCase();
      if (k === "n" && pos.next) {
        e.preventDefault();
        nav(`/solve/${pos.next.id}`);
      } else if (k === "p" && pos.prev) {
        e.preventDefault();
        nav(`/solve/${pos.prev.id}`);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [pos, nav]);

  if (!pos) return null;

  return (
    <div className="rung-pager">
      <Link className="rung-unit" to={`/library/unit/${pos.unitKey}`}>
        {pos.unitTitle}
      </Link>
      <span className="rung-name faint">{pos.rungTitle}</span>
      <span className="rung-pos mono">
        {pos.at + 1}/{pos.total}
      </span>
      <button
        className="ghost"
        disabled={!pos.prev}
        title={pos.prev ? `Previous: ${pos.prev.title} (Alt+P)` : "First in this rung"}
        aria-label="Previous problem in this rung"
        onClick={() => pos.prev && nav(`/solve/${pos.prev.id}`)}
      >
        ‹
      </button>
      <button
        className="ghost"
        disabled={!pos.next}
        title={pos.next ? `Next: ${pos.next.title} (Alt+N)` : "Last in this rung"}
        aria-label="Next problem in this rung"
        onClick={() => pos.next && nav(`/solve/${pos.next.id}`)}
      >
        ›
      </button>
    </div>
  );
}
