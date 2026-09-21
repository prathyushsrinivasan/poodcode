import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { CardReview, Problem } from "../types";
import { InlineMarkdown, Markdown } from "../components/Markdown";
import { DiffBadge, Empty } from "../components/common";
import { LibrarySkeleton } from "../components/Skeleton";
import { useCurriculumData } from "../components/CurriculumData";
import { findUnit } from "../lib/curriculum";
import {
  mixedSet,
  placement,
  routeCardId,
  type PlacementStage,
  type RoutingQuestion,
} from "../lib/dsaRecognition";

/**
 * Recognition drills: the stage-end mixed set, and the placement diagnostic.
 *
 * Both exist because every other page in the curriculum practises *blocked* —
 * you solve a sliding-window problem on the page titled Sliding Window, having
 * just read its signals table. Routing a prompt to a technique is the skill the
 * Signals tables were built to train and the one that fails under interview
 * pressure, and nothing tested it.
 *
 * Two scores, never one. "I knew it was a heap and could not write one" and "I
 * can write a heap and never saw it was one" are different failures wanting
 * different practice, and a single percentage hides which one you have.
 */

/** A stable-per-day seed, so reloading the page does not reshuffle the set
 * under you but tomorrow's is different. */
function todaySeed(extra: string): number {
  const d = new Date();
  const base = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  let h = base;
  for (let i = 0; i < extra.length; i++) h = (h * 31 + extra.charCodeAt(i)) | 0;
  return Math.abs(h);
}

export default function CurriculumDrill({ view }: { view: "mixed" | "placement" }) {
  const { stage = "" } = useParams();
  const { data, error, setSkipped } = useCurriculumData();
  const nav = useNavigate();

  if (error) {
    return (
      <div className="page page-wide">
        <h1 className="page-title">Recognition</h1>
        <Empty icon="⚠️" text={`Could not load the curriculum: ${error}`} />
        <button onClick={() => nav("/library")}>Back to the curriculum</button>
      </div>
    );
  }
  if (!data) return <LibrarySkeleton />;

  return view === "placement" ? (
    <Placement data={data} nav={nav} setSkipped={setSkipped} />
  ) : (
    <MixedSet data={data} stageKey={stage} nav={nav} />
  );
}

/* ------------------------------------------------------------------ mixed */

function MixedSet({
  data,
  stageKey,
  nav,
}: {
  data: ReturnType<typeof useCurriculumData>["data"] & object;
  stageKey: string;
  nav: (to: string) => void;
}) {
  const stage = data.stages.find((s) => s.key === stageKey);
  const questions = useMemo(
    () => mixedSet(data, stageKey, todaySeed(stageKey)),
    [data, stageKey]
  );
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());

  useEffect(() => {
    api
      .cardReviews()
      .then((rs) => setReviews(new Map(rs.map((r) => [r.card_id, r]))))
      .catch(() => {});
  }, []);

  const gradeRoute = useCallback(async (unitKey: string, right: boolean) => {
    const id = routeCardId(unitKey);
    try {
      const r = await api.gradeCard(id, right ? 2 : 0);
      setReviews((m) => new Map(m).set(id, r));
    } catch {
      /* the drill is worth more than the bookkeeping */
    }
  }, []);

  if (!stage) {
    return (
      <div className="page page-wide">
        <Empty icon="🤔" text="No such stage." />
        <button onClick={() => nav("/library")}>Back to the curriculum</button>
      </div>
    );
  }

  const index = data.stages.findIndex((s) => s.key === stageKey);

  return (
    <div className="page page-wide">
      <div className="row" style={{ marginBottom: 4 }}>
        <button className="ghost" onClick={() => nav("/library")}>
          ← Curriculum
        </button>
      </div>
      <h1 className="page-title" style={{ marginBottom: 0 }}>
        🎲 Mixed set · {stage.title}
      </h1>
      <p className="page-sub">
        Unlabelled problems from this stage and every earlier one. Name the technique
        before you open the editor.
      </p>

      <div className="card" style={{ marginBottom: 16 }}>
        <Markdown>{`Everywhere else in the curriculum you are told which
technique a problem wants — you are reading it on the page named after that
technique. Here you are not, and that is the whole exercise: **reading a prompt
and landing on the technique without deriving it** is most of what separates
fast solvers from slow ones.

Answer the routing question first. Whether you then *solve* it is a separate
question with a separate answer, which is why the two are scored apart.

${index > 0 ? `Drawn from stages 1–${index + 1}, not just this one — a set from a single stage tells you which five techniques are in play, which gives away most of the routing answer for free.` : ""}`}</Markdown>
      </div>

      {questions.length === 0 ? (
        <Empty icon="🎲" text="Not enough units with problems yet to build a mixed set." />
      ) : (
        questions.map((q) => (
          <RoutingCard
            key={q.problem.slug}
            q={q}
            review={reviews.get(routeCardId(q.answerUnit))}
            unitTitle={findUnit(data, q.answerUnit)?.unit.title ?? q.answerUnit}
            onGrade={(right) => gradeRoute(q.answerUnit, right)}
            onSolve={() => nav(`/solve/${q.problem.id}`)}
            onOpenUnit={() => nav(`/library/unit/${q.answerUnit}`)}
          />
        ))
      )}
    </div>
  );
}

/** One prompt, four techniques, then the editor. The answer is only revealed
 * after a choice: a routing question you can see the answer to is a reading
 * exercise. */
function RoutingCard({
  q,
  review,
  unitTitle,
  onGrade,
  onSolve,
  onOpenUnit,
}: {
  q: RoutingQuestion;
  review: CardReview | undefined;
  unitTitle: string;
  onGrade: (right: boolean) => void;
  onSolve: () => void;
  onOpenUnit: () => void;
}) {
  const [picked, setPicked] = useState<string | null>(null);
  const right = picked === q.answerLabel;

  return (
    <div className="card" style={{ marginBottom: 14 }}>
      <div className="row">
        <strong>{q.problem.title}</strong>
        <DiffBadge d={q.problem.difficulty} />
        <span className="spacer" />
        {review && review.reps > 0 && (
          <span className="faint" style={{ fontSize: 12 }}>
            routed right {review.reps}× in a row
            {review.lapses > 0 && ` · ${review.lapses} miss${review.lapses === 1 ? "" : "es"}`}
          </span>
        )}
      </div>
      <div className="dim" style={{ margin: "6px 0 12px" }}>
        <Markdown>{promptOf(q.problem)}</Markdown>
      </div>

      <div className="io-label">Which technique does this prompt want?</div>
      <div className="grid cols-2" style={{ marginTop: 8 }}>
        {q.options.map((opt) => {
          let border: string | undefined;
          if (picked !== null) {
            if (opt === q.answerLabel) border = "var(--good)";
            else if (opt === picked) border = "var(--bad)";
          }
          return (
            <button
              key={opt}
              className="ghost"
              style={{ textAlign: "left", borderColor: border, color: border, padding: "10px 12px" }}
              disabled={picked !== null}
              onClick={() => {
                setPicked(opt);
                onGrade(opt === q.answerLabel);
              }}
            >
              {opt}
            </button>
          );
        })}
      </div>

      {picked !== null && (
        <>
          <div className="row" style={{ marginTop: 12, gap: 8 }}>
            <span style={{ color: right ? "var(--good)" : "var(--bad)", fontWeight: 600 }}>
              {right ? "Routed correctly." : "Not this one."}
            </span>
            <span className="dim">
              Taught in{" "}
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  onOpenUnit();
                }}
              >
                {unitTitle}
              </a>
              .
            </span>
            <span className="spacer" />
            <button className="primary" onClick={onSolve}>
              Now solve it →
            </button>
          </div>
          {/* The giveaway, from the unit's own signals table. A missed routing
              question should send you back to the wording you did not notice —
              scoring it without saying why would teach nothing. */}
          {q.signalHint && (
            <div className="hint" style={{ marginTop: 10 }}>
              <div className="hint-label">The signal</div>
              <div>
                When the prompt says <InlineMarkdown>{q.signalHint.when}</InlineMarkdown> → reach
                for <strong><InlineMarkdown>{q.signalHint.reachFor}</InlineMarkdown></strong>
              </div>
            </div>
          )}
          {/* The signal above says "this technique applies when…", which is the
              question you ask *after* choosing — and someone who chose wrongly
              never got that far. The stage's routing rule is what would have
              sent them here in the first place, and `not` names the near miss
              they most likely confused it with. */}
          {q.routeHint && (
            <div className="hint" style={{ marginTop: 10 }}>
              <div className="hint-label">The routing rule</div>
              <div>
                <InlineMarkdown>{q.routeHint.when}</InlineMarkdown> →{" "}
                <strong>{q.answerLabel}</strong>.{" "}
                <span className="dim"><InlineMarkdown>{q.routeHint.why}</InlineMarkdown></span>
              </div>
              {q.routeHint.notWhen && (
                <div className="cur-router-not" style={{ marginTop: 6 }}>
                  <span className="cur-router-not-tag">not</span>{" "}
                  <InlineMarkdown>{q.routeHint.notWhen}</InlineMarkdown>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

/** The first paragraph of a statement — enough to route from, short enough to
 * read six of. The full statement is on the Solve page. */
function promptOf(p: Problem): string {
  const first = p.description.split(/\n\s*\n/)[0] ?? p.description;
  return first.length > 420 ? `${first.slice(0, 420).trimEnd()}…` : first;
}

/* -------------------------------------------------------------- placement */

function Placement({
  data,
  nav,
  setSkipped,
}: {
  data: ReturnType<typeof useCurriculumData>["data"] & object;
  nav: (to: string) => void;
  setSkipped: (keys: Iterable<string>, known: boolean) => Promise<void>;
}) {
  const stages = useMemo(() => placement(data, todaySeed("placement")), [data]);

  return (
    <div className="page page-wide">
      <div className="row" style={{ marginBottom: 4 }}>
        <button className="ghost" onClick={() => nav("/library")}>
          ← Curriculum
        </button>
      </div>
      <h1 className="page-title" style={{ marginBottom: 0 }}>
        🎯 Placement
      </h1>
      <p className="page-sub">Skip what you already know, honestly.</p>

      <div className="card" style={{ marginBottom: 16 }}>
        <Markdown>{`The course starts at \`System.out.println\` for everyone.
That is the right default and a bad only-option: units open regardless of
readiness, which is correct, but there was no honest way to **skip**.

Per stage, two questions — *can you name the technique?* and *can you write
it?* — because those are the two failures worth ruling out. Clear both and the
stage's units are marked **known**: they count as cleared for what unlocks
next, and they still render as known rather than as earned green. Nothing is
deleted and nothing is locked; you can un-skip any unit from its own page.

Solving the representative problem happens on the normal Solve page, against
the normal judge. There is no separate grading here to game.`}</Markdown>
      </div>

      {stages.map((s) => (
        <PlacementCard
          key={s.stageKey}
          stage={s}
          data={data}
          nav={nav}
          onClear={() => setSkipped(s.unitKeys, true)}
          onUndo={() => setSkipped(s.unitKeys, false)}
        />
      ))}
    </div>
  );
}

function PlacementCard({
  stage,
  data,
  nav,
  onClear,
  onUndo,
}: {
  stage: PlacementStage;
  data: ReturnType<typeof useCurriculumData>["data"] & object;
  nav: (to: string) => void;
  onClear: () => void;
  onUndo: () => void;
}) {
  const [picked, setPicked] = useState<string | null>(null);
  const q = stage.question;
  const routed = q !== null && picked === q.answerLabel;
  const solved = stage.problem?.solved_status === "solved";
  const skipped = stage.unitKeys.every((k) => findUnit(data, k)?.skipped);

  return (
    <div className="card" style={{ marginBottom: 14 }}>
      <div className="row">
        <span style={{ fontSize: 20 }}>{stage.stageIcon}</span>
        <strong>{stage.stageTitle}</strong>
        <span className="spacer" />
        {skipped ? (
          <span className="badge" style={{ color: "var(--medium)", borderColor: "var(--medium)" }}>
            ✓ Marked known
          </span>
        ) : stage.alreadyCleared ? (
          <span className="badge" style={{ color: "var(--good)", borderColor: "var(--good)" }}>
            ● Already cleared
          </span>
        ) : null}
      </div>

      {skipped ? (
        <div className="row" style={{ marginTop: 10 }}>
          <span className="dim">
            {stage.unitKeys.length} unit{stage.unitKeys.length === 1 ? "" : "s"} marked known.
          </span>
          <span className="spacer" />
          <button className="ghost" onClick={onUndo}>
            Put them back
          </button>
        </div>
      ) : stage.alreadyCleared ? (
        <p className="dim" style={{ marginTop: 8, marginBottom: 0 }}>
          You have already cleared every unit here by solving. Nothing to place.
        </p>
      ) : (
        <>
          {q ? (
            <>
              <div className="dim" style={{ margin: "8px 0 10px" }}>
                <Markdown>{promptOf(q.problem)}</Markdown>
              </div>
              <div className="io-label">Which technique does this prompt want?</div>
              <div className="grid cols-2" style={{ marginTop: 8 }}>
                {q.options.map((opt) => {
                  let border: string | undefined;
                  if (picked !== null) {
                    if (opt === q.answerLabel) border = "var(--good)";
                    else if (opt === picked) border = "var(--bad)";
                  }
                  return (
                    <button
                      key={opt}
                      className="ghost"
                      style={{
                        textAlign: "left",
                        borderColor: border,
                        color: border,
                        padding: "10px 12px",
                      }}
                      disabled={picked !== null}
                      onClick={() => setPicked(opt)}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            </>
          ) : (
            <p className="faint" style={{ marginTop: 8 }}>
              Not enough sibling techniques to build a routing question for this stage.
            </p>
          )}

          <div className="row" style={{ marginTop: 12, gap: 10, flexWrap: "wrap" }}>
            <span className={routed ? "" : "dim"} style={{ fontSize: 13 }}>
              {picked === null ? "○" : routed ? "✅" : "❌"} Recognition
            </span>
            <span className={solved ? "" : "dim"} style={{ fontSize: 13 }}>
              {solved ? "✅" : "○"} Implementation
              {stage.problem && (
                <>
                  {" — "}
                  <a
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      nav(`/solve/${stage.problem!.id}`);
                    }}
                  >
                    {stage.problem.title}
                  </a>
                </>
              )}
            </span>
            <span className="spacer" />
            <button className="primary" disabled={!routed || !solved} onClick={onClear}>
              Mark this stage known
            </button>
          </div>
          {picked !== null && !routed && (
            <p className="faint" style={{ fontSize: 12, marginTop: 8, marginBottom: 0 }}>
              Missing the routing question is the signal this stage is worth working, not a
              reason to be locked out of it — every unit is still open from the curriculum.
            </p>
          )}
        </>
      )}
    </div>
  );
}
