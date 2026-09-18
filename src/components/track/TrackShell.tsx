/**
 * One layout for every track.
 *
 * The TypeScript course, the Java course, the Backend Lab, Projects and the
 * 6-Month Mastery programme each grew their own overview page, their own
 * progress card, their own module list and their own prev/next — five layouts
 * doing one job, none of them quite like the DSA curriculum that works best
 * (UI_ROADMAP G1).
 *
 * This is that job, once. A track describes itself as a `TrackSpec` — units,
 * the groups they fall into, and what a unit is called — and gets the
 * curriculum's structure in return: a hero that says where you are and what to
 * do next, a rail of groups beside one group at a time, and consistent paging.
 *
 * What it deliberately does not do is own a unit's *content*. A course module
 * and a project module have nothing in common below the title, so each track
 * still renders its own detail page inside `UnitPage`'s frame.
 */

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Markdown } from "../Markdown";
import { ClickableRow } from "../common";
import { studyTime } from "../../lib/trackProgress";

export interface TrackUnit {
  /** The route segment under the track's base — a number or a key. */
  slug: string;
  number: number;
  title: string;
  /** One line on what it is for. */
  tagline?: string;
  /** Group key, e.g. a month number or a phase key. */
  group: string;
  done: boolean;
  /** False for a placeholder that is listed but not written yet. */
  authored: boolean;
  estMinutes?: number;
  /** Extra chips — lesson counts, a capstone marker, a stack. */
  badges?: ReactNode;
}

export interface TrackGroup {
  key: string;
  title: string;
}

export interface TrackSpec {
  title: string;
  subtitle: string;
  /** Route prefix, e.g. "/course". A unit lives at `${base}/${slug}`. */
  base: string;
  /** Singular noun for one unit: "Module", "Week", "Project". */
  unitLabel: string;
  /** Singular noun for one group: "Month", "Phase". */
  groupLabel: string;
  groups: TrackGroup[];
  units: TrackUnit[];
  /** Markdown shown once above the rail, if the track has an introduction. */
  intro?: string;
  /** Rendered between the hero and the rail — a track's own extras. */
  children?: ReactNode;
  /**
   * Render a unit yourself instead of as a row that links to `base/slug`.
   *
   * The Mastery programme's weeks expand in place rather than navigating —
   * they are a gated accordion, not a list of pages — so it supplies its own
   * card here and still gets the hero, the phase rail and the grouping.
   */
  renderUnit?: (unit: TrackUnit) => ReactNode;
  /**
   * Replaces the hero's "resume" link, for a track whose next step is not a
   * route (again, Mastery: the next week is already on this page).
   */
  heroAction?: ReactNode;
}

/* ------------------------------------------------------------------ maths */

export interface TrackProgress {
  authored: TrackUnit[];
  doneCount: number;
  percent: number;
  /** The first unwritten-on unit, or the last one when the track is finished. */
  next: TrackUnit | null;
  /** Estimated minutes left across everything not yet done. */
  minutesLeft: number;
  complete: boolean;
}

export function trackProgress(units: TrackUnit[]): TrackProgress {
  const authored = units.filter((u) => u.authored);
  const doneCount = authored.filter((u) => u.done).length;
  const next = authored.find((u) => !u.done) ?? authored[authored.length - 1] ?? null;
  return {
    authored,
    doneCount,
    percent: authored.length ? Math.round((doneCount / authored.length) * 100) : 0,
    next,
    minutesLeft: authored.filter((u) => !u.done).reduce((n, u) => n + (u.estMinutes ?? 0), 0),
    complete: authored.length > 0 && doneCount === authored.length,
  };
}

/* ------------------------------------------------------------------- hero */

/** Where you are, and the one button that continues. */
export function TrackHero({ spec, progress }: { spec: TrackSpec; progress: TrackProgress }) {
  const { doneCount, authored, percent, next, minutesLeft, complete } = progress;
  const unit = spec.unitLabel.toLowerCase();

  return (
    <div className="track-hero">
      <div className="track-hero-main">
        <div className="track-eyebrow">
          {complete ? "Finished" : doneCount === 0 ? "Start here" : "Up next"}
        </div>
        {next && (
          <>
            <div className="track-hero-title">
              {spec.unitLabel} {next.number}
              {next.title ? ` · ${next.title}` : ""}
            </div>
            {next.tagline && <p className="track-hero-tagline">{next.tagline}</p>}
            {spec.heroAction ?? (
              <Link className="track-hero-go" to={`${spec.base}/${next.slug}`}>
                {complete
                  ? `Review ${unit} ${next.number} →`
                  : doneCount === 0
                  ? `Start ${unit} ${next.number} →`
                  : `Resume ${unit} ${next.number} →`}
              </Link>
            )}
          </>
        )}
      </div>

      <div className="track-hero-side">
        <div className="track-big-stat">{percent}%</div>
        <div className="progress">
          <span
            className={complete ? "full" : undefined}
            style={{ width: `${percent}%` }}
          />
        </div>
        <div className="faint track-hero-meta">
          {doneCount} / {authored.length} {unit}s done
          {/* `studyTime` already renders its own "~", so no "about" here. */}
          {minutesLeft > 0 && ` · ${studyTime(minutesLeft)} left`}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------- rail */

/**
 * The groups, as a rail, beside one group's units.
 *
 * Which group is showing lives in `?group=`, so returning from a unit comes
 * back to the part of the track you were reading rather than the top — the same
 * trick the curriculum's stage rail uses.
 */
export function TrackBody({ spec, progress }: { spec: TrackSpec; progress: TrackProgress }) {
  const [params, setParams] = useSearchParams();
  const nav = useNavigate();

  const unitsByGroup = useMemo(() => {
    const map = new Map<string, TrackUnit[]>();
    for (const u of spec.units) {
      if (!map.has(u.group)) map.set(u.group, []);
      map.get(u.group)!.push(u);
    }
    return map;
  }, [spec.units]);

  // Default to the group holding "up next", so the page opens where the work is.
  const currentGroup = progress.next?.group ?? spec.groups[0]?.key;
  const requested = params.get("group");
  const selected =
    requested && spec.groups.some((g) => g.key === requested) ? requested : currentGroup;

  const units = unitsByGroup.get(selected) ?? [];
  const unwritten = spec.units.filter((u) => !u.authored);

  if (spec.groups.length === 0) return null;

  // A track with one group has no rail to offer — the rail would be a single
  // button next to the only thing it could select.
  const showRail = spec.groups.length > 1;

  return (
    <div className={showRail ? "track-layout" : undefined}>
      {showRail && (
        <div className="track-rail">
          <div className="track-rail-label">{spec.groupLabel}s</div>
          {spec.groups.map((g, i) => {
            const groupUnits = unitsByGroup.get(g.key) ?? [];
            const authored = groupUnits.filter((u) => u.authored);
            const done = authored.filter((u) => u.done).length;
            return (
              <button
                key={g.key}
                className={`track-rail-item ${g.key === selected ? "active" : ""}`}
                aria-current={g.key === selected ? "true" : undefined}
                onClick={() => setParams({ group: g.key }, { replace: true })}
              >
                <span className="track-rail-num">{i + 1}</span>
                <span className="track-rail-text">
                  <span className="track-rail-title">{g.title}</span>
                  <span className="track-rail-meta">
                    {authored.length === 0
                      ? "not written yet"
                      : `${done}/${authored.length} done`}
                  </span>
                </span>
              </button>
            );
          })}
        </div>
      )}

      <div className="track-units">
        {showRail && (
          <div className="track-group-head">
            <div className="track-eyebrow">
              {spec.groupLabel} {spec.groups.findIndex((g) => g.key === selected) + 1} of{" "}
              {spec.groups.length}
            </div>
            <h2 className="track-group-title">
              {spec.groups.find((g) => g.key === selected)?.title}
            </h2>
          </div>
        )}

        {units.filter((u) => u.authored).length === 0 ? (
          <div className="card empty-state">
            <p className="dim">Nothing in this {spec.groupLabel.toLowerCase()} is written yet.</p>
          </div>
        ) : (
          <ol className="track-unit-list">
            {units
              .filter((u) => u.authored)
              .map((u) =>
                spec.renderUnit ? (
                  <li key={u.slug} className="track-unit-custom">
                    {spec.renderUnit(u)}
                  </li>
                ) : (
                <li key={u.slug}>
                  <ClickableRow
                    className={`track-unit ${u.done ? "done" : ""}`}
                    onActivate={() => nav(`${spec.base}/${u.slug}`)}
                    title={`Open ${spec.unitLabel.toLowerCase()} ${u.number}`}
                  >
                    <span className="track-unit-num" aria-hidden>
                      {u.done ? "✓" : u.number}
                    </span>
                    <span className="track-unit-body">
                      <span className="track-unit-title">{u.title}</span>
                      {u.tagline && <span className="track-unit-tagline">{u.tagline}</span>}
                      <span className="track-unit-meta">
                        {u.badges}
                        {u.estMinutes ? (
                          <span className="badge">⏱ {studyTime(u.estMinutes)}</span>
                        ) : null}
                      </span>
                    </span>
                  </ClickableRow>
                </li>
                )
              )}
          </ol>
        )}

        {/* The unwritten tail, as one line rather than a grid of things you
            cannot open (UI_ROADMAP G2). */}
        {unwritten.length > 0 && !showRail && (
          <div className="coming-later">
            <span aria-hidden>🚧</span>
            <span>
              Coming later: {spec.unitLabel.toLowerCase()}s{" "}
              {Math.min(...unwritten.map((u) => u.number))}–
              {Math.max(...unwritten.map((u) => u.number))}{" "}
              <span className="faint">({unwritten.length} not written yet)</span>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

/* --------------------------------------------------------------- overview */

/** The whole track overview: heading, hero, the track's own extras, the rail. */
export function TrackOverview({ spec }: { spec: TrackSpec }) {
  const progress = useMemo(() => trackProgress(spec.units), [spec.units]);

  return (
    <div className="page track-page">
      <h1 className="page-title">{spec.title}</h1>
      <p className="page-sub">{spec.subtitle}</p>

      <TrackHero spec={spec} progress={progress} />

      {spec.children}

      {spec.intro && (
        <details className="track-intro">
          <summary>How to work through this</summary>
          <Markdown>{spec.intro}</Markdown>
        </details>
      )}

      <TrackBody spec={spec} progress={progress} />
    </div>
  );
}

/* ------------------------------------------------------------------ pager */

/**
 * Previous / next through a track, with `[` and `]` bound to them.
 *
 * Each track had its own pair of buttons at the bottom of a unit, worded
 * differently and placed differently; this is one of them, and it is the same
 * keys as the curriculum's unit page.
 */
export function UnitPager({
  base,
  unitLabel,
  prev,
  next,
  backTo,
  backLabel,
}: {
  base: string;
  unitLabel: string;
  prev: { slug: string; number: number; title: string } | null;
  next: { slug: string; number: number; title: string } | null;
  backTo: string;
  backLabel: string;
}) {
  const nav = useNavigate();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const el = document.activeElement as HTMLElement | null;
      if (
        el &&
        (el.tagName === "INPUT" ||
          el.tagName === "TEXTAREA" ||
          el.isContentEditable ||
          el.closest(".monaco-editor"))
      ) {
        return;
      }
      if (e.key === "[" && prev) nav(`${base}/${prev.slug}`);
      else if (e.key === "]" && next) nav(`${base}/${next.slug}`);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [base, prev, next, nav]);

  return (
    <nav className="unit-pager" aria-label={`${unitLabel} navigation`}>
      {prev ? (
        <Link className="unit-pager-link" to={`${base}/${prev.slug}`}>
          <span className="unit-pager-dir">← Previous</span>
          <span className="unit-pager-title">
            {prev.number}. {prev.title}
          </span>
        </Link>
      ) : (
        <span />
      )}

      <Link className="unit-pager-back" to={backTo}>
        {backLabel}
      </Link>

      {next ? (
        <Link className="unit-pager-link right" to={`${base}/${next.slug}`}>
          <span className="unit-pager-dir">Next →</span>
          <span className="unit-pager-title">
            {next.number}. {next.title}
          </span>
        </Link>
      ) : (
        <span />
      )}
    </nav>
  );
}

/** Remembers which group of a track was last open, for the Today card. */
export function useTrackGroupMemory(trackKey: string) {
  const [params] = useSearchParams();
  const group = params.get("group");
  const [, setStored] = useState<string | null>(null);
  useEffect(() => {
    if (!group) return;
    try {
      localStorage.setItem(`poodcode:track-group:${trackKey}`, group);
      setStored(group);
    } catch {
      /* a remembered group is a convenience */
    }
  }, [group, trackKey]);
}
