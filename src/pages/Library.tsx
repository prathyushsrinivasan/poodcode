import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Markdown } from "../components/Markdown";
import { Section, useCollapse } from "../components/Collapsible";
import { ClickableRow, Empty } from "../components/common";
import { StatusBadge, UnitProgress, useCurriculumData } from "../components/CurriculumData";
import { searchUnits, type HydratedUnit } from "../lib/curriculum";

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
  const nav = useNavigate();
  const stageKeys = useMemo(() => (data?.stages ?? []).map((s) => s.key), [data]);
  const { isOpen, toggle } = useCollapse("dsa-stage", true);

  const hits = useMemo(() => (data ? searchUnits(data, query) : []), [data, query]);

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
        <StatusBadge status={u.status} />
      </div>
      <p className="dim" style={{ margin: "6px 0 0" }}>
        {u.unit.tagline}
      </p>
      <UnitProgress solved={u.solved} total={u.total} />
      <div className="row" style={{ marginTop: 8 }}>
        <span className="faint" style={{ fontSize: 12 }}>
          {u.solved}/{u.total} problems
          {u.attempted > 0 && ` · ${u.attempted} attempted`}
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
