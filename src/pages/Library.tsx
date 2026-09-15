import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { CardReview, Difficulty } from "../types";
import { Markdown } from "../components/Markdown";
import { Section, useCollapse } from "../components/Collapsible";
import { ClickableRow, Empty } from "../components/common";
import { LibrarySkeleton } from "../components/Skeleton";
import { StatusBadge, UnitProgress, useCurriculumData } from "../components/CurriculumData";
import {
  findUnit,
  readLastUnit,
  searchUnits,
  type HydratedUnit,
  type UnitMatch,
} from "../lib/curriculum";
import { reviewLane, type ReviewLane } from "../lib/dsaReview";

/**
 * The Problem Library, as a curriculum.
 *
 * The old page was a filterable table of every problem — perfect for "find the
 * one I mean", useless for "what should I learn next". That table has not gone
 * anywhere (it is `/library/browse`); this page is the answer to the second
 * question: every problem in the bank placed on exactly one teaching ladder, in
 * stages, from `System.out.println` to tries and Dijkstra. The stage and unit
 * counts are rendered from the seed rather than stated here — the previous
 * version of this comment said "thirty-two units" while shipping 33.
 *
 * Nothing here is locked. A unit whose prerequisites are unfinished is marked
 * "builds on …" and is still openable, because someone who already knows heaps
 * should not have to solve their way past stacks to prove it. A unit can also be
 * marked known outright, which reads as cleared without claiming it was earned.
 */
export default function Library() {
  const { data, error } = useCurriculumData();
  const [query, setQuery] = useState("");
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const nav = useNavigate();
  const stageKeys = useMemo(() => (data?.stages ?? []).map((s) => s.key), [data]);
  // Default-closed, with the stage you are working in opened below. Every stage
  // open on first paint rendered all 33 unit cards in a two-column grid, so the
  // page opened several screens tall and the unit you wanted was rarely visible.
  const { isOpen, toggle, open: openStage } = useCollapse("dsa-stage", false);

  useEffect(() => {
    api
      .cardReviews()
      .then((rs) => setReviews(new Map(rs.map((r) => [r.card_id, r]))))
      .catch(() => {});
  }, []);

  const hits = useMemo(() => (data ? searchUnits(data, query) : []), [data, query]);
  const lane = useMemo(() => (data ? reviewLane(data, reviews) : null), [data, reviews]);

  /**
   * The stage holding "up next" — the one you are working in.
   *
   * Opened once, the first time this page is seen in a session, rather than on
   * every render: after that the remembered collapse state wins, because a page
   * that re-opens a section you deliberately closed is arguing with you.
   */
  const currentStage = useMemo(
    () =>
      data?.next
        ? data.stages.find((s) =>
            s.units.some((u) => u.unit.key === data.next!.unit.unit.key)
          )?.key ?? null
        : null,
    [data]
  );
  const opened = useRef(false);
  useEffect(() => {
    if (!currentStage || opened.current) return;
    opened.current = true;
    openStage(currentStage);
  }, [currentStage, openStage]);

  if (error) {
    return (
      <div className="page page-wide">
        <h1 className="page-title">Problem Library</h1>
        <Empty icon="⚠️" text={`Could not load the curriculum: ${error}`} />
      </div>
    );
  }
  if (!data) return <LibrarySkeleton />;

  const pct = data.total ? Math.round((data.solved / data.total) * 100) : 0;
  // Derived, not stated: the comment this replaced claimed thirty-two.
  const unitCount = data.stages.reduce((n, s) => n + s.units.length, 0);
  // "Where was I?" and "what is next?" are different questions. Offer the
  // remembered unit only when it is neither finished nor already the target.
  const lastKey = readLastUnit();
  const lastUnit = lastKey ? findUnit(data, lastKey) : null;
  const resume =
    lastUnit && lastUnit.status !== "complete" && lastUnit.unit.key !== data.next?.unit.unit.key
      ? lastUnit
      : null;

  return (
    <div className="page page-wide">
      <div className="row">
        <h1 className="page-title">{data.title || "DSA Curriculum"}</h1>
        <span className="spacer" />
        <button onClick={() => nav("/library/browse")}>🔎 Browse all problems</button>
      </div>
      <p className="page-sub">
        {data.subtitle}
        {data.stages.length > 0 && (
          <>
            {" "}
            <span className="faint">
              — {data.stages.length} stages, {unitCount} units, {data.total} problems.
            </span>
          </>
        )}
      </p>

      {/* Overall progress + where to go next. */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row">
          <strong>
            {data.solved} of {data.total} problems solved
          </strong>
          <span className="spacer" />
          <span className="dim mono">{pct}%</span>
        </div>
        <UnitProgress solved={data.solved} total={data.total} />

        {data.next ? (
          <div className="row" style={{ marginTop: 14, gap: 10 }}>
            <div>
              <div className="io-label">Up next</div>
              <strong>
                {data.next.unit.unit.icon} {data.next.unit.unit.title}
              </strong>
              <span className="dim"> — {data.next.unit.unit.tagline}</span>
            </div>
            <span className="spacer" />
            {resume && (
              <button
                onClick={() => nav(`/library/unit/${resume.unit.key}`)}
                title="The last unit you had open — not necessarily the next one"
              >
                Resume {resume.unit.title}
              </button>
            )}
            <button className="primary" onClick={() => nav(`/library/unit/${data.next!.unit.unit.key}`)}>
              Open the unit →
            </button>
            {data.next.problem && (
              <button onClick={() => nav(`/solve/${data.next!.problem!.id}`)}>
                Straight to {data.next.problem.title}
              </button>
            )}
          </div>
        ) : (
          <p className="dim" style={{ marginTop: 12, marginBottom: 0 }}>
            🎉 Every problem in the curriculum is solved. The work from here is
            revision — the review queue, and re-solving the stretch rungs from
            memory rather than from notes.
          </p>
        )}
      </div>

      {lane && lane.units.length > 0 && <ReviewLaneCard lane={lane} nav={nav} />}

      <input
        style={{ width: "100%", marginBottom: 16 }}
        placeholder="Search the units — by technique, by a phrase in a prompt (“contiguous subarray”), or by a symptom (“infinite loop”)…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      {query.trim() ? (
        <div style={{ marginBottom: 20 }}>
          <p className="page-sub">
            {hits.length} unit{hits.length === 1 ? "" : "s"} match “{query.trim()}”
          </p>
          {hits.length === 0 ? (
            <Empty icon="🔍" text="No unit mentions that. Try the problem search in Browse." />
          ) : (
            <div className="grid cols-2">
              {hits.map((m) => (
                <UnitCard
                  key={m.unit.unit.key}
                  u={m.unit}
                  match={m}
                  onOpen={() => nav(`/library/unit/${m.unit.unit.key}`)}
                />
              ))}
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            <Markdown>{data.intro}</Markdown>
          </div>

          {/* Placement sits above the stage list because that is where someone
              who does not need stage 1 will look for permission to leave it. */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="row">
              <div>
                <strong>🎯 Already know some of this?</strong>
                <span className="dim">
                  {" "}
                  — one routing question and one problem per stage. Clear both and its
                  units are marked known.
                </span>
              </div>
              <span className="spacer" />
              <button onClick={() => nav("/library/placement")}>Take the placement →</button>
            </div>
          </div>

          {data.stages.map((stage, i) => (
            <Section
              key={stage.key}
              title={`${stage.icon} Stage ${i + 1} · ${stage.title}`}
              open={isOpen(stage.key)}
              onToggle={() => toggle(stage.key)}
              meta={
                <span className="dim mono">
                  {stage.solved}/{stage.total}
                </span>
              }
            >
              <p className="dim" style={{ marginTop: 0 }}>
                {stage.tagline}
              </p>
              <Markdown>{stage.goal}</Markdown>
              <div className="grid cols-2" style={{ marginTop: 12 }}>
                {stage.units.map((u) => (
                  <UnitCard
                    key={u.unit.key}
                    u={u}
                    onOpen={() => nav(`/library/unit/${u.unit.key}`)}
                  />
                ))}
              </div>
              <div className="row" style={{ marginTop: 12 }}>
                <span className="dim" style={{ fontSize: 13 }}>
                  Finished the stage? The mixed set draws from it and every earlier one,
                  unlabelled — which is the only way prompt → technique routing gets tested.
                </span>
                <span className="spacer" />
                <button className="ghost" onClick={() => nav(`/library/mixed/${stage.key}`)}>
                  🎲 Mixed set
                </button>
              </div>
            </Section>
          ))}
          {stageKeys.length === 0 && <Empty icon="📚" text="No curriculum content." />}

          {data.unplaced.length > 0 && (
            <p className="faint" style={{ fontSize: 12, marginTop: 16 }}>
              {data.unplaced.length} problem{data.unplaced.length === 1 ? "" : "s"} in your
              library {data.unplaced.length === 1 ? "is" : "are"} not on the curriculum — your
              own additions and imports.{" "}
              <a href="#" onClick={(e) => { e.preventDefault(); nav("/library/browse"); }}>
                Find them in Browse
              </a>
              .
            </p>
          )}
        </>
      )}
    </div>
  );
}

/** What is due today, from the units you have already cleared.
 *
 * Only cleared units appear. A review queue that offered you units you have
 * never opened would be a second copy of the curriculum, and would stop meaning
 * "this is slipping away". */
function ReviewLaneCard({ lane, nav }: { lane: ReviewLane; nav: (to: string) => void }) {
  const first = lane.units[0];
  const parts: string[] = [];
  if (lane.checksDue > 0) {
    parts.push(`${lane.checksDue} self-check${lane.checksDue === 1 ? "" : "s"}`);
  }
  if (lane.staleUnits > 0) {
    parts.push(`${lane.staleUnits} unit${lane.staleUnits === 1 ? "" : "s"} gone stale`);
  }
  if (lane.slowSolves > 0) {
    parts.push(`${lane.slowSolves} solved slowly`);
  }

  return (
    <div className="card" style={{ marginBottom: 16, borderColor: "var(--accent)" }}>
      <div className="row">
        <div>
          <div className="io-label">Due today</div>
          <strong>{parts.join(" · ")}</strong>
          <span className="dim">
            {" "}
            — from the {lane.units.length} unit{lane.units.length === 1 ? "" : "s"} you have
            cleared
          </span>
        </div>
        <span className="spacer" />
        <button className="primary" onClick={() => nav(`/library/unit/${first.unit.unit.key}`)}>
          Start with {first.unit.unit.title} →
        </button>
      </div>
      <div className="row wrap" style={{ marginTop: 10, gap: 6 }}>
        {lane.units.slice(0, 8).map((r) => (
          <span
            key={r.unit.unit.key}
            className="badge"
            style={{
              cursor: "pointer",
              color: r.stale ? "var(--text-faint)" : "var(--accent)",
              borderColor: r.stale ? "var(--text-faint)" : "var(--accent)",
            }}
            title={
              [
                r.stale ? `Last practised ${r.lastPractisedDays} days ago` : "",
                r.checksDue > 0
                  ? `${r.checksDue} self-check${r.checksDue === 1 ? "" : "s"} due`
                  : "",
                r.slow.length > 0
                  ? `${r.slow.length} solved slowly (${r.slow[0].title} took ${Math.round(
                      r.slow[0].time_taken_seconds / 60
                    )} min)`
                  : "",
              ]
                .filter(Boolean)
                .join(" · ")
            }
            onClick={() => nav(`/library/unit/${r.unit.unit.key}`)}
          >
            {r.unit.unit.icon} {r.unit.unit.title}
            {r.checksDue > 0 && ` · ${r.checksDue}`}
            {r.stale && " · stale"}
            {r.slow.length > 0 && " · 🐢"}
          </span>
        ))}
        {lane.units.length > 8 && (
          <span className="faint" style={{ fontSize: 12, alignSelf: "center" }}>
            +{lane.units.length - 8} more
          </span>
        )}
      </div>
    </div>
  );
}

const DIFF_COLOUR: Record<Difficulty, string> = {
  Intro: "var(--text-faint)",
  Easy: "var(--good)",
  Medium: "var(--medium)",
  Hard: "var(--bad)",
};

/** The difficulty mix as a stacked bar plus `E2 · M6 · H3`, and a rough time.
 *
 * The bar is for scanning a two-column grid of cards; the letters are for
 * knowing what it actually says. Neither alone does both jobs. */
function DifficultyMix({
  mix,
  minutes,
}: {
  mix: Record<Difficulty, number>;
  minutes: number;
}) {
  const order: Difficulty[] = ["Intro", "Easy", "Medium", "Hard"];
  const total = order.reduce((n, d) => n + mix[d], 0);
  if (total === 0) return null;
  const hours = minutes >= 90 ? `~${Math.round(minutes / 60)}h` : `~${minutes}m`;

  return (
    <div style={{ marginTop: 8 }}>
      <div
        style={{ display: "flex", height: 4, borderRadius: 2, overflow: "hidden" }}
        title={order.filter((d) => mix[d]).map((d) => `${mix[d]} ${d}`).join(" · ")}
      >
        {order
          .filter((d) => mix[d] > 0)
          .map((d) => (
            <span
              key={d}
              style={{ width: `${(mix[d] / total) * 100}%`, background: DIFF_COLOUR[d] }}
            />
          ))}
      </div>
      <div className="faint mono" style={{ fontSize: 11, marginTop: 4 }}>
        {order
          .filter((d) => mix[d] > 0)
          .map((d) => `${d[0]}${mix[d]}`)
          .join(" · ")}{" "}
        <span title="Rough time at fluent pace, not a first encounter">· {hours}</span>
      </div>
    </div>
  );
}

function UnitCard({
  u,
  onOpen,
  match,
}: {
  u: HydratedUnit;
  onOpen: () => void;
  /** Present in search results: why this unit matched, and the line that did. */
  match?: UnitMatch;
}) {
  return (
    <ClickableRow
      onActivate={onOpen}
      className="card week-card"
      title={`Open ${u.unit.title}`}
      style={{ marginBottom: 0 }}
    >
      <div className="row">
        <span style={{ fontSize: 20 }}>{u.unit.icon}</span>
        <strong>{u.unit.title}</strong>
        <span className="spacer" />
        <StatusBadge status={u.status} stale={u.stale} skipped={u.skipped} />
      </div>
      <p className="dim" style={{ margin: "6px 0 0" }}>
        {u.unit.tagline}
      </p>
      {/* Why it matched, and the line that did — searching "infinite loop" used
          to return bare unit cards with no hint that the hit was a pitfall. */}
      {match && match.field !== "title" && match.field !== "tagline" && (
        <div className="hint" style={{ margin: "8px 0 0", fontSize: 12 }}>
          <div className="hint-label">matched in {match.label}</div>
          <div className="dim">{match.snippet}</div>
        </div>
      )}
      <UnitProgress solved={u.solved} total={u.total} stale={u.stale} />
      {/* "11 problems" reads the same for 11 Intros and for 10 Medium + 2 Hard.
          The mix is what tells you which unit is an evening and which is a week. */}
      <DifficultyMix mix={u.mix} minutes={u.estimatedMinutes} />
      <div className="row" style={{ marginTop: 8 }}>
        <span className="faint" style={{ fontSize: 12 }}>
          {u.solved}/{u.total} problems
          {u.attempted > 0 && ` · ${u.attempted} attempted`}
          {u.stale && ` · last practised ${u.lastPractisedDays}d ago`}
        </span>
        <span className="spacer" />
        {u.unmetPrereqTitles.length > 0 && (
          <span className="faint" style={{ fontSize: 12 }} title="Advisory only — the unit is still open">
            builds on {u.unmetPrereqTitles.join(", ")}
          </span>
        )}
      </div>
    </ClickableRow>
  );
}
