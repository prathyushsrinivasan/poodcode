import { Fragment, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import type { CardReview, Difficulty } from "../types";
import { Markdown, InlineMarkdown } from "../components/Markdown";
import { useCollapse } from "../components/Collapsible";
import { ClickableRow } from "../components/common";
import { LibrarySkeleton } from "../components/Skeleton";
import { StatusBadge, UnitProgress, useCurriculumData } from "../components/CurriculumData";
import {
  findUnit,
  isCleared,
  readLastUnit,
  searchUnits,
  type HydratedStage,
  type HydratedUnit,
  type UnitMatch,
} from "../lib/curriculum";
import { reviewLane, type ReviewLane } from "../lib/dsaReview";
import { EmptyState, ErrorState, Icon, IconButton, Button, ScrollX } from "../components/ui";
import { loadFailed } from "../lib/failures";

/**
 * The Problem Library, as a curriculum.
 *
 * The old page was a filterable table of every problem — perfect for "find the
 * one I mean", useless for "what should I learn next". That table has not gone
 * anywhere (it is `/library/browse`); this page is the answer to the second
 * question: every problem in the bank placed on exactly one teaching ladder, in
 * stages, from `System.out.println` to tries and Dijkstra. The stage and unit
 * counts are rendered from the seed rather than stated here.
 *
 * The page shows **one stage at a time**. It used to stack a progress card, the
 * review lane, the search box, the intro and the placement pitch above six
 * collapsible stages of two-column cards, so the curriculum itself started
 * below the fold and opening a stage meant scrolling past the others. Now the
 * stages are a rail on the left, the selected one fills the right as a numbered
 * path, and the selection lives in `?stage=` so coming back from a unit returns
 * you to the stage you were browsing.
 *
 * Nothing here is locked. A unit whose prerequisites are unfinished is marked
 * "builds on …" and is still openable, because someone who already knows heaps
 * should not have to solve their way past stacks to prove it. A unit can also be
 * marked known outright, which reads as cleared without claiming it was earned.
 */
export default function Library() {
  const { data, error, reload } = useCurriculumData();
  const [query, setQuery] = useState("");
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const [params, setParams] = useSearchParams();
  const nav = useNavigate();
  // The intro and each stage's goal are reference text: worth one read, then in
  // the way. Closed by default, remembered once opened.
  const fold = useCollapse("dsa-overview", false);
  // Default-closed namespace, so "open" here means the rail is folded.
  const railCompact = fold.isOpen("rail");

  useEffect(() => {
    api
      .cardReviews()
      .then((rs) => setReviews(new Map(rs.map((r) => [r.card_id, r]))))
      .catch(loadFailed("your review schedule"));
  }, []);

  const hits = useMemo(() => (data ? searchUnits(data, query) : []), [data, query]);
  const lane = useMemo(() => (data ? reviewLane(data, reviews) : null), [data, reviews]);

  if (error) {
    return (
      <div className="page cur-page">
        <h1 className="page-title">DSA Curriculum</h1>
        <ErrorState title="Could not load the curriculum." error={error} onRetry={reload} />
      </div>
    );
  }
  if (!data) return <LibrarySkeleton />;
  if (data.stages.length === 0) {
    return (
      <div className="page cur-page">
        <h1 className="page-title">{data.title || "DSA Curriculum"}</h1>
        <EmptyState icon="curriculum" title="No curriculum content." />
      </div>
    );
  }

  const coreStages = data.stages.filter((s) => !s.optional);
  const optionalStages = data.stages.length - coreStages.length;
  const unitCount = coreStages.reduce((n, s) => n + s.units.length, 0);
  const nextKey = data.next?.unit.unit.key ?? null;
  // The stage holding "up next" is the one you are working in, and the default
  // selection when the URL does not name one.
  const currentIndex = Math.max(
    0,
    data.stages.findIndex((s) => s.units.some((u) => u.unit.key === nextKey))
  );
  const requested = data.stages.findIndex((s) => s.key === params.get("stage"));
  const selectedIndex = requested >= 0 ? requested : currentIndex;
  const stage = data.stages[selectedIndex];
  // `replace`, so flicking through stages does not fill the back stack.
  const selectStage = (key: string) => setParams({ stage: key }, { replace: true });
  const openUnit = (key: string) => nav(`/library/unit/${key}`);

  // "Where was I?" and "what is next?" are different questions. Offer the
  // remembered unit only when it is neither finished nor already the target.
  const lastKey = readLastUnit();
  const lastUnit = lastKey ? findUnit(data, lastKey) : null;
  const resume =
    lastUnit && lastUnit.status !== "complete" && lastUnit.unit.key !== nextKey ? lastUnit : null;

  const searching = query.trim().length > 0;

  return (
    <div className="page cur-page">
      <div className="cur-head">
        <div>
          <h1 className="page-title">{data.title || "DSA Curriculum"}</h1>
          <p className="page-sub">
            {data.subtitle}{" "}
            <span className="faint">
              {coreStages.length} stages · {unitCount} units · {data.total} problems
              {optionalStages > 0 &&
                ` · plus ${optionalStages === 1 ? "an optional stage" : `${optionalStages} optional stages`}`}
            </span>
          </p>
        </div>
        <div className="cur-head-actions">
          <button
            className={fold.isOpen("intro") ? "" : "ghost"}
            onClick={() => fold.toggle("intro")}
            aria-expanded={fold.isOpen("intro")}
          >
            ℹ️ How it works
          </button>
          <button
            onClick={() => nav("/library/placement")}
            title="One routing question and one problem per stage. Clear both and its units are marked known."
          >
            Placement test
          </button>
          <Button icon="browse" onClick={() => nav("/library/browse")}>
            Browse all problems
          </Button>
          <Button
            icon="sparkles"
            onClick={() => nav("/library/topic/sliding-window")}
            title="The first topic in the NEW_DSA format: sixteen sections, in TypeScript, from the concept to mastery"
          >
            NEW DSA: Sliding Window
          </Button>
        </div>
      </div>

      {fold.isOpen("intro") && (
        <div className="cur-panel mb-4">
          <div className="row">
            <span className="cur-eyebrow">How this curriculum works</span>
            <span className="spacer" />
            <button className="ghost" onClick={() => fold.toggle("intro")}>
              Close
            </button>
          </div>
          <Markdown>{data.intro}</Markdown>
          <p className="dim mb-0">
            <strong>Already know some of this?</strong> The placement test asks one routing
            question and one problem per stage; clear both and that stage's units are marked
            known.
          </p>
        </div>
      )}

      <ContinuePanel
        data={data}
        lane={lane}
        resume={resume}
        onOpenUnit={openUnit}
        onSolve={(id) => nav(`/solve/${id}`)}
        onShowIntro={fold.isOpen("intro") ? null : () => fold.toggle("intro")}
      />

      <input
        style={{ width: "100%", marginBottom: 24, padding: "10px 14px", fontSize: 14 }}
        placeholder="Search every unit — a technique, a phrase from a prompt (“contiguous subarray”), or a symptom (“infinite loop”)"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      {searching ? (
        <SearchResults
          query={query.trim()}
          hits={hits}
          stages={data.stages}
          nextKey={nextKey}
          onOpen={openUnit}
          onClear={() => setQuery("")}
        />
      ) : (
        <div className={`cur-layout ${railCompact ? "rail-compact" : ""}`}>
          <nav className="cur-stages" aria-label="Stages">
            <div className="cur-stages-head">
              <span className="cur-eyebrow cur-stages-label">Stages</span>
              {/* The rail folds to its numbers: on a narrow window, or when
                  the stage itself is what you want the width for (H4). */}
              <IconButton
                size="sm"
                icon={railCompact ? "sidebarOpen" : "sidebarClose"}
                label={railCompact ? "Show stage names" : "Fold the stage rail to numbers"}
                aria-expanded={!railCompact}
                onClick={() => fold.toggle("rail")}
              />
            </div>
            {data.stages.map((s, i) => (
              <Fragment key={s.key}>
                {/* The optional stage is past the finish line; say so where it sits. */}
                {s.optional && (i === 0 || !data.stages[i - 1]!.optional) && (
                  <div className="cur-optional-rule" role="presentation">
                    <span>Optional</span>
                  </div>
                )}
                <StageButton
                  stage={s}
                  number={i + 1}
                  active={i === selectedIndex}
                  current={i === currentIndex && !!data.next}
                  compact={railCompact}
                  onSelect={() => selectStage(s.key)}
                />
              </Fragment>
            ))}
            {data.unplaced.length > 0 && (
              <div className="cur-stage-foot">
                {data.unplaced.length} problem{data.unplaced.length === 1 ? " is" : "s are"} your
                own additions and not on the curriculum —{" "}
                <a
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    nav("/library/browse");
                  }}
                >
                  find them in Browse
                </a>
                .
              </div>
            )}
          </nav>

          <StagePanel
            stage={stage}
            number={selectedIndex + 1}
            count={coreStages.length}
            nextKey={nextKey}
            goalOpen={fold.isOpen(`goal:${stage.key}`)}
            onToggleGoal={() => fold.toggle(`goal:${stage.key}`)}
            routerOpen={fold.isOpen(`router:${stage.key}`)}
            onToggleRouter={() => fold.toggle(`router:${stage.key}`)}
            prev={data.stages[selectedIndex - 1] ?? null}
            next={data.stages[selectedIndex + 1] ?? null}
            onSelectStage={selectStage}
            onOpenUnit={openUnit}
            onMixed={() => nav(`/library/mixed/${stage.key}`)}
          />
        </div>
      )}
    </div>
  );
}

/** Up next, overall progress and what is due — the whole "what do I do now"
 * answer in one panel instead of three stacked cards. */
function ContinuePanel({
  data,
  lane,
  resume,
  onOpenUnit,
  onSolve,
  onShowIntro,
}: {
  data: NonNullable<ReturnType<typeof useCurriculumData>["data"]>;
  lane: ReviewLane | null;
  resume: HydratedUnit | null;
  onOpenUnit: (key: string) => void;
  onSolve: (id: number) => void;
  /** Null when the intro is already open. */
  onShowIntro: (() => void) | null;
}) {
  const pct = data.total ? Math.round((data.solved / data.total) * 100) : 0;
  // Core units only, to match `data.solved / data.total`: an optional stage is
  // not part of finishing the course.
  const all = data.stages.filter((s) => !s.optional).flatMap((s) => s.units);
  const cleared = all.filter((u) => isCleared(u.status) || u.skipped).length;
  const next = data.next;

  return (
    <div className="cur-hero">
      <div className="cur-hero-main">
        {next ? (
          <>
            <div className="cur-eyebrow" style={{ color: data.coreComplete ? "var(--good)" : "var(--accent)" }}>
              {data.coreComplete ? "🎉 Core complete · optional next" : "Up next"}
            </div>
            <div className="cur-hero-title">
              <span>{next.unit.unit.icon}</span>
              <span>{next.unit.unit.title}</span>
              <StatusBadge status={next.unit.status} stale={next.unit.stale} />
            </div>
            <p className="cur-hero-tagline">{next.unit.unit.tagline}</p>
            <div className="cur-actions">
              <button className="primary" onClick={() => onOpenUnit(next.unit.unit.key)}>
                Open the unit →
              </button>
              {next.problem && (
                <button onClick={() => onSolve(next.problem!.id)}>
                  Straight to {next.problem.title}
                </button>
              )}
              {resume && (
                <button
                  className="ghost"
                  onClick={() => onOpenUnit(resume.unit.key)}
                  title="The last unit you had open — not necessarily the next one"
                >
                  ↩ Resume {resume.unit.title}
                </button>
              )}
            </div>
            {data.solved === 0 && onShowIntro && (
              <p className="faint" style={{ margin: "14px 0 0", fontSize: 12 }}>
                New here?{" "}
                <button className="cur-link-btn text-xs" onClick={onShowIntro}>
                  Read how the curriculum works
                </button>{" "}
                — two minutes, and it explains what "done" means.
              </p>
            )}
          </>
        ) : (
          <>
            <div className="cur-eyebrow c-good">
              🎉 Curriculum complete
            </div>
            <p className="mb-0">
              Every unit in the curriculum is done, the optional stage included. The work from
              here is revision — the mixed sets, and re-solving the stretch rungs from memory
              rather than from notes.
            </p>
          </>
        )}
      </div>

      <div className="cur-hero-side">
        <div>
          <div className="row items-baseline">
            <span className="cur-big-stat">{pct}%</span>
            <span className="spacer" />
            <span className="dim text-xs">
              {data.solved} / {data.total} problems · {cleared} / {all.length} units
            </span>
          </div>
          <UnitProgress solved={data.solved} total={data.total} />
        </div>
        <DueToday lane={lane} onOpenUnit={onOpenUnit} />
      </div>
    </div>
  );
}

/** What is due today, from the units you have already cleared.
 *
 * Only cleared units appear. A review queue that offered you units you have
 * never opened would be a second copy of the curriculum, and would stop meaning
 * "this is slipping away". */
function DueToday({
  lane,
  onOpenUnit,
}: {
  lane: ReviewLane | null;
  onOpenUnit: (key: string) => void;
}) {
  if (!lane || lane.units.length === 0) {
    return (
      <div>
        <div className="cur-eyebrow">Due today</div>
        <p className="faint" style={{ margin: "4px 0 0", fontSize: 12 }}>
          Nothing due. Units you clear come back here when their self-checks are due or they
          go stale.
        </p>
      </div>
    );
  }

  const parts: string[] = [];
  if (lane.checksDue > 0) parts.push(`${lane.checksDue} self-check${lane.checksDue === 1 ? "" : "s"}`);
  if (lane.staleUnits > 0) parts.push(`${lane.staleUnits} stale unit${lane.staleUnits === 1 ? "" : "s"}`);
  if (lane.slowSolves > 0) parts.push(`${lane.slowSolves} slow solve${lane.slowSolves === 1 ? "" : "s"}`);
  const shown = lane.units.slice(0, 4);

  return (
    <div>
      <div className="row">
        <div>
          <div className="cur-eyebrow">Due today</div>
          <strong>{parts.join(" · ")}</strong>
        </div>
        <span className="spacer" />
        <button
          onClick={() => onOpenUnit(lane.units[0].unit.unit.key)}
          title={`Start with ${lane.units[0].unit.unit.title}`}
        >
          Review →
        </button>
      </div>
      <div className="cur-chips mt-2">
        {shown.map((r) => (
          <span
            key={r.unit.unit.key}
            className="badge cur-chip"
            role="button"
            tabIndex={0}
            title={[
              r.stale ? `Last practised ${r.lastPractisedDays} days ago` : "",
              r.checksDue > 0 ? `${r.checksDue} self-check${r.checksDue === 1 ? "" : "s"} due` : "",
              r.slow.length > 0
                ? `${r.slow.length} solved slowly (${r.slow[0].title} took ${Math.round(
                    r.slow[0].time_taken_seconds / 60
                  )} min)`
                : "",
            ]
              .filter(Boolean)
              .join(" · ")}
            onClick={() => onOpenUnit(r.unit.unit.key)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onOpenUnit(r.unit.unit.key);
              }
            }}
          >
            {r.unit.unit.icon} {r.unit.unit.title}
            {r.checksDue > 0 && ` · ${r.checksDue}`}
            {r.stale && " · stale"}
            {r.slow.length > 0 && " · slow"}
          </span>
        ))}
        {lane.units.length > shown.length && (
          <span className="faint" style={{ fontSize: 12, alignSelf: "center" }}>
            +{lane.units.length - shown.length} more
          </span>
        )}
      </div>
    </div>
  );
}

function StageButton({
  stage,
  number,
  active,
  current,
  compact = false,
  onSelect,
}: {
  stage: HydratedStage;
  number: number;
  active: boolean;
  /** Holds the "up next" unit. */
  current: boolean;
  /** The folded rail: the number only, the rest in the tooltip. */
  compact?: boolean;
  onSelect: () => void;
}) {
  const clearedUnits = stage.units.filter((u) => isCleared(u.status) || u.skipped).length;
  const done = stage.units.length > 0 && clearedUnits === stage.units.length;
  const started = stage.units.some((u) => u.status !== "new" || u.skipped);
  const pct = stage.total ? (stage.solved / stage.total) * 100 : 0;

  return (
    <button
      className={`cur-stage-btn ${active ? "active" : ""} ${stage.optional ? "optional" : ""} ${compact ? "compact" : ""}`}
      onClick={onSelect}
      aria-current={active ? "true" : undefined}
      aria-label={compact ? `${stage.optional ? "Optional stage" : `Stage ${number}`}: ${stage.title}, ${clearedUnits} of ${stage.units.length} units` : undefined}
      title={compact ? `${stage.title} — ${clearedUnits}/${stage.units.length} units` : undefined}
    >
      <span className={`cur-num ${done ? "complete" : started ? "started" : ""} ${stage.optional ? "optional" : ""}`}>
        {done ? <Icon name="check" size={14} /> : stage.optional ? <Icon name="sparkles" size={14} /> : number}
      </span>
      <span className="cur-stage-text">
        <span className="cur-stage-name">
          {stage.icon} {stage.title}
        </span>
        <span className="cur-stage-meta">
          <span>
            {clearedUnits}/{stage.units.length} units
          </span>
          {stage.optional && <span>· optional</span>}
          {current && <span className="cur-here">· you are here</span>}
        </span>
        <span className="cur-minibar">
          <span style={{ width: `${pct}%`, background: done ? "var(--good)" : undefined }} />
        </span>
      </span>
    </button>
  );
}

/**
 * The stage's routing table: which of its units a given prompt belongs to.
 *
 * A unit's `signals` answer "does THIS technique apply?" — a question you can
 * only ask once you have already guessed the technique. On a stage whose six
 * units all take an array and return a number, guessing *is* the difficulty,
 * and nothing else in the curriculum addresses it.
 *
 * `not_when` is rendered as prominently as `why`, because the confusable pairs
 * are where the time goes: "longest substring with at most k distinct" is a
 * window and "count substrings with exactly k distinct" is two windows
 * subtracted, and a routing rule that does not say what it excludes is half a
 * rule.
 *
 * Collapsed by default and remembered, like the stage goal — it is reference
 * text, useful before the stage and again after, and in the way during.
 */
function StageRouter({
  stage,
  open,
  onToggle,
  onOpenUnit,
}: {
  stage: HydratedStage;
  open: boolean;
  onToggle: () => void;
  onOpenUnit: (key: string) => void;
}) {
  const titleOf = (key: string) =>
    stage.units.find((u) => u.unit.key === key)?.unit.title ?? key;
  const iconOf = (key: string) => stage.units.find((u) => u.unit.key === key)?.unit.icon ?? "";

  return (
    <>
      <button className="cur-link-btn" onClick={onToggle} aria-expanded={open}>
        {open ? "▾ Hide the routing table" : "▸ Which unit is this prompt?"}
      </button>
      {open && (
        <div className="cur-router">
          <p className="dim mt-0">
            Every unit in this stage takes an array and returns a number, so telling them apart
            from the prompt is the real skill. Read this before the stage, and again after.
          </p>
          <ScrollX label="Telling the units apart" className="card p-0">
            <table className="data">
              <thead>
                <tr>
                  <th>When the prompt says…</th>
                  <th style={{ width: 200 }}>Go to</th>
                  <th>Why, and what it is not</th>
                </tr>
              </thead>
              <tbody>
                {stage.router.map((r, i) => (
                  <tr className="cursor-default" key={i}>
                    <td>
                      <InlineMarkdown>{r.when}</InlineMarkdown>
                    </td>
                    <td>
                      <button
                        className="cur-link-btn ws-nowrap"
                        onClick={() => onOpenUnit(r.unit)}
                      >
                        {iconOf(r.unit)} {titleOf(r.unit)}
                      </button>
                    </td>
                    <td className="dim">
                      <InlineMarkdown>{r.why}</InlineMarkdown>
                      {r.not_when && (
                        <div className="cur-router-not">
                          <span className="cur-router-not-tag">not</span>{" "}
                          <InlineMarkdown>{r.not_when}</InlineMarkdown>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </ScrollX>
        </div>
      )}
    </>
  );
}

function StagePanel({
  stage,
  number,
  count,
  nextKey,
  goalOpen,
  onToggleGoal,
  routerOpen,
  onToggleRouter,
  prev,
  next,
  onSelectStage,
  onOpenUnit,
  onMixed,
}: {
  stage: HydratedStage;
  number: number;
  count: number;
  nextKey: string | null;
  goalOpen: boolean;
  onToggleGoal: () => void;
  routerOpen: boolean;
  onToggleRouter: () => void;
  prev: HydratedStage | null;
  next: HydratedStage | null;
  onSelectStage: (key: string) => void;
  onOpenUnit: (key: string) => void;
  onMixed: () => void;
}) {
  const minutes = stage.units.reduce((n, u) => n + u.estimatedMinutes, 0);
  // Per visit rather than remembered: the sheet is something you open to look
  // one thing up, not a panel you live with.
  const [sheetOpen, setSheetOpen] = useState(false);

  return (
    <section className="min-w-0" aria-label={`Stage ${number}: ${stage.title}`}>
      <div className="cur-eyebrow">
        {stage.optional ? "Optional stage" : `Stage ${number} of ${count}`} · {stage.units.length}{" "}
        units · {stage.solved}/{stage.total} problems · {formatMinutes(minutes)}
      </div>
      <h2 className="cur-stage-title">
        <span>{stage.icon}</span>
        <span>{stage.title}</span>
      </h2>
      <p className="cur-stage-tagline">{stage.tagline}</p>
      {stage.goal && (
        <>
          <button className="cur-link-btn" onClick={onToggleGoal} aria-expanded={goalOpen}>
            {goalOpen ? "▾ Hide what this stage builds" : "▸ What this stage builds"}
          </button>
          {goalOpen && (
            <div className="cur-goal">
              <Markdown>{stage.goal}</Markdown>
            </div>
          )}
        </>
      )}

      {stage.router.length > 0 && (
        <StageRouter
          stage={stage}
          open={routerOpen}
          onToggle={onToggleRouter}
          onOpenUnit={onOpenUnit}
        />
      )}

      {stage.cheatsheet && (
        <>
          <button
            className="cur-link-btn"
            onClick={() => setSheetOpen((v) => !v)}
            aria-expanded={sheetOpen}
          >
            {sheetOpen ? "▾ Hide the cheat sheet" : "▸ The whole stage on one page"}
          </button>
          {sheetOpen && (
            <div className="cur-goal">
              <Markdown>{stage.cheatsheet}</Markdown>
            </div>
          )}
        </>
      )}

      <div className="cur-path">
        {stage.units.map((u, i) => (
          <div key={u.unit.key} className="cur-step">
            <div className="cur-step-rail">
              <span className={`cur-num ${numClass(u)}`}>
                {u.status === "complete" && !u.stale ? "✓" : i + 1}
              </span>
              <span className="cur-step-line" />
            </div>
            <UnitCard u={u} isNext={u.unit.key === nextKey} onOpen={() => onOpenUnit(u.unit.key)} />
          </div>
        ))}
      </div>

      <div className="cur-stage-end" data-stage-end>
        <Icon name="shuffle" size={24} />
        <div style={{ flex: 1, minWidth: 220 }}>
          <strong>Finished the stage? Try the mixed set.</strong>
          <div className="dim text-sm">
            Problems from this stage and every earlier one, unlabelled. It is the only way to
            test whether you can pick the technique from the prompt.
          </div>
        </div>
        <button onClick={onMixed}>Start the mixed set</button>
      </div>

      <div className="cur-stage-nav">
        {prev ? (
          <button className="ghost" onClick={() => onSelectStage(prev.key)}>
            ← {prev.icon} {prev.title}
          </button>
        ) : (
          <span />
        )}
        {next && (
          <button className="ghost" onClick={() => onSelectStage(next.key)}>
            {next.icon} {next.title} →
          </button>
        )}
      </div>
    </section>
  );
}

function SearchResults({
  query,
  hits,
  stages,
  nextKey,
  onOpen,
  onClear,
}: {
  query: string;
  hits: UnitMatch[];
  stages: HydratedStage[];
  nextKey: string | null;
  onOpen: (key: string) => void;
  onClear: () => void;
}) {
  const stageOf = (key: string) => {
    const i = stages.findIndex((s) => s.units.some((u) => u.unit.key === key));
    if (i < 0) return "";
    return stages[i].optional ? `Optional · ${stages[i].title}` : `Stage ${i + 1} · ${stages[i].title}`;
  };

  return (
    <div style={{ maxWidth: 900 }}>
      <div className="row mb-3">
        <span className="dim">
          {hits.length} unit{hits.length === 1 ? "" : "s"} match “{query}”
        </span>
        <span className="spacer" />
        <button className="ghost" onClick={onClear}>
          Clear search
        </button>
      </div>
      {hits.length === 0 ? (
        <EmptyState
          icon="search"
          title="No unit mentions that."
          action={{ label: "Clear search", icon: "close", onClick: onClear }}
        >
          The problem search in Browse covers every problem, not just unit titles.
        </EmptyState>
      ) : (
        hits.map((m) => (
          <UnitCard
            key={m.unit.unit.key}
            u={m.unit}
            match={m}
            stageLabel={stageOf(m.unit.unit.key)}
            isNext={m.unit.unit.key === nextKey}
            onOpen={() => onOpen(m.unit.unit.key)}
          />
        ))
      )}
    </div>
  );
}

function numClass(u: HydratedUnit): string {
  if (u.skipped) return "known";
  if (u.stale) return "stale";
  return u.status === "new" ? "" : u.status;
}

function formatMinutes(minutes: number): string {
  return minutes >= 90 ? `~${Math.round(minutes / 60)}h` : `~${minutes}m`;
}

const DIFF_COLOUR: Record<Difficulty, string> = {
  Intro: "var(--intro)",
  Easy: "var(--easy)",
  Medium: "var(--medium)",
  Hard: "var(--hard)",
};

/** `E2 M6 H3`, coloured. "11 problems" reads the same for 11 Intros and for
 * 10 Medium + 2 Hard; the mix is what tells you which unit is an evening and
 * which is a week. */
function DifficultyMix({ mix }: { mix: Record<Difficulty, number> }) {
  const order: Difficulty[] = ["Intro", "Easy", "Medium", "Hard"];
  const present = order.filter((d) => mix[d] > 0);
  if (present.length === 0) return null;
  return (
    <span className="cur-mix" title={present.map((d) => `${mix[d]} ${d}`).join(" · ")}>
      {present.map((d) => (
        <span key={d} style={{ color: DIFF_COLOUR[d] }}>
          {d[0]}
          {mix[d]}
        </span>
      ))}
    </span>
  );
}

function UnitCard({
  u,
  onOpen,
  isNext,
  match,
  stageLabel,
}: {
  u: HydratedUnit;
  onOpen: () => void;
  isNext: boolean;
  /** Present in search results: why this unit matched, and the line that did. */
  match?: UnitMatch;
  stageLabel?: string;
}) {
  const pct = u.total ? (u.solved / u.total) * 100 : 0;
  return (
    <ClickableRow
      onActivate={onOpen}
      className={`cur-unit ${isNext ? "is-next" : ""}`}
      title={`Open ${u.unit.title}`}
    >
      {stageLabel && (
        <div className="cur-eyebrow mb-1">
          {stageLabel}
        </div>
      )}
      <div className="cur-unit-top">
        <span className="cur-unit-icon">{u.unit.icon}</span>
        <span className="cur-unit-title">{u.unit.title}</span>
        {isNext && <span className="cur-pill-next">Up next</span>}
        <span className="spacer" />
        <StatusBadge status={u.status} stale={u.stale} skipped={u.skipped} />
      </div>
      <p className="cur-unit-tagline">{u.unit.tagline}</p>
      {/* Why it matched, and the line that did — searching "infinite loop" used
          to return bare unit cards with no hint that the hit was a pitfall. */}
      {match && match.field !== "title" && match.field !== "tagline" && (
        <div className="hint" style={{ margin: "10px 0 0", fontSize: 12 }}>
          <div className="hint-label">matched in {match.label}</div>
          <div className="dim">{match.snippet}</div>
        </div>
      )}
      <div className="cur-unit-meta">
        <span className="row gap-2">
          <span className="cur-minibar">
            <span
              style={{
                width: `${pct}%`,
                background: u.stale ? "var(--text-faint)" : pct === 100 ? "var(--good)" : undefined,
              }}
            />
          </span>
          <span>
            {u.solved}/{u.total} solved
          </span>
        </span>
        <DifficultyMix mix={u.mix} />
        <span title="Rough time at fluent pace, not a first encounter">
          <Icon name="clock" size={12} /> {formatMinutes(u.estimatedMinutes)}
        </span>
        {u.attempted > 0 && <span>{u.attempted} attempted</span>}
        {u.stale && <span>last practised {u.lastPractisedDays}d ago</span>}
        {u.unmetPrereqTitles.length > 0 && (
          <span title="Advisory only — the unit is still open">
            builds on {u.unmetPrereqTitles.join(", ")}
          </span>
        )}
      </div>
    </ClickableRow>
  );
}
