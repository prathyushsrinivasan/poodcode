import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { CardReview } from "../types";
import { Markdown } from "../components/Markdown";
import { Section, useCollapse } from "../components/Collapsible";
import { ClickableRow, Empty } from "../components/common";
import { StatusBadge, UnitProgress, useCurriculumData } from "../components/CurriculumData";
import { searchUnits, type HydratedUnit } from "../lib/curriculum";
import { reviewLane, type ReviewLane } from "../lib/dsaReview";

/**
 * The Problem Library, as a curriculum.
 *
 * The old page was a filterable table of every problem — perfect for "find the
 * one I mean", useless for "what should I learn next". That table has not gone
 * anywhere (it is `/library/browse`); this page is the answer to the second
 * question: six stages, thirty-two units, every problem in the bank placed on
 * exactly one teaching ladder, from `System.out.println` to tries and Dijkstra.
 *
 * Nothing here is locked. A unit whose prerequisites are unfinished is marked
 * "builds on …" and is still openable, because someone who already knows heaps
 * should not have to solve their way past stacks to prove it.
 */
export default function Library() {
  const { data, error } = useCurriculumData();
  const [query, setQuery] = useState("");
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const nav = useNavigate();
  const stageKeys = useMemo(() => (data?.stages ?? []).map((s) => s.key), [data]);
  const { isOpen, toggle } = useCollapse("dsa-stage", true);

  useEffect(() => {
    api
      .cardReviews()
      .then((rs) => setReviews(new Map(rs.map((r) => [r.card_id, r]))))
      .catch(() => {});
  }, []);

  const hits = useMemo(() => (data ? searchUnits(data, query) : []), [data, query]);
  const lane = useMemo(() => (data ? reviewLane(data, reviews) : null), [data, reviews]);

  if (error) {
    return (
      <div className="page page-wide">
        <h1 className="page-title">Problem Library</h1>
        <Empty icon="⚠️" text={`Could not load the curriculum: ${error}`} />
      </div>
    );
  }
  if (!data) return <div className="empty" style={{ paddingTop: "20vh" }}>Loading…</div>;

  const pct = data.total ? Math.round((data.solved / data.total) * 100) : 0;

  return (
    <div className="page page-wide">
      <div className="row">
        <h1 className="page-title">{data.title || "DSA Curriculum"}</h1>
        <span className="spacer" />
        <button onClick={() => nav("/library/browse")}>🔎 Browse all problems</button>
      </div>
      <p className="page-sub">{data.subtitle}</p>

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
              {hits.map((u) => (
                <UnitCard key={u.unit.key} u={u} onOpen={() => nav(`/library/unit/${u.unit.key}`)} />
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

function UnitCard({ u, onOpen }: { u: HydratedUnit; onOpen: () => void }) {
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
      <UnitProgress solved={u.solved} total={u.total} stale={u.stale} />
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
