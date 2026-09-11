// Review — the project's own quiz questions, asked again later and mixed up.
//
// See lib/projectReview.ts for why. The page is a small state machine: choose
// what to draw from, answer a round one question at a time, then see what you
// missed with a link to the step that explains each one. What you get wrong is
// remembered (per viewer, in localStorage) and asked first next time.

import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Project } from "../types";
import { QuizItem } from "../components/LearnExercise";
import { Empty } from "../components/common";
import {
  collectQuestions,
  pickRound,
  poolSummary,
  recordAnswer,
  type ReviewHistory,
  type ReviewQuestion,
} from "../lib/projectReview";
import { plural } from "../lib/trackProgress";

const historyKey = (projectKey: string) => `poodcode:project-review:${projectKey}`;

function readHistory(projectKey: string): ReviewHistory {
  try {
    const raw = localStorage.getItem(historyKey(projectKey));
    const v: unknown = raw ? JSON.parse(raw) : {};
    return v && typeof v === "object" && !Array.isArray(v) ? (v as ReviewHistory) : {};
  } catch {
    return {};
  }
}

function writeHistory(projectKey: string, h: ReviewHistory) {
  try {
    localStorage.setItem(historyKey(projectKey), JSON.stringify(h));
  } catch {
    // Storage blocked: the round still works, it just is not remembered.
  }
}

const SIZES = [5, 10, 20] as const;

type Stage =
  | { kind: "setup" }
  | { kind: "round"; questions: ReviewQuestion[]; at: number; picked: number[]; round: number }
  | { kind: "done"; questions: ReviewQuestion[]; picked: number[]; round: number };

export default function ProjectReview({
  project,
  doneKeys,
}: {
  project: Project;
  /** Keys of the modules this viewer has completed. */
  doneKeys: Set<string>;
}) {
  const nav = useNavigate();
  const all = useMemo(() => collectQuestions(project), [project]);
  const [history, setHistory] = useState<ReviewHistory>(() => readHistory(project.key));
  const finishedCount = new Set(all.filter((q) => doneKeys.has(q.moduleKey)).map((q) => q.moduleKey)).size;

  // "done" draws from finished modules — the default, since reviewing a module
  // you have not reached is previewing, not reviewing. Falls back to every
  // written module when nothing is finished yet.
  const [scope, setScope] = useState<string>(finishedCount > 0 ? "done" : "all");
  const [size, setSize] = useState<number>(10);
  const [stage, setStage] = useState<Stage>({ kind: "setup" });

  const pool = useMemo(
    () =>
      all.filter((q) =>
        scope === "all" ? true : scope === "done" ? doneKeys.has(q.moduleKey) : q.phase === scope
      ),
    [all, scope, doneKeys]
  );
  const summary = poolSummary(pool, history);
  const phases = project.roadmap.filter((ph) => all.some((q) => q.phase === ph.key));

  function start(from: readonly ReviewQuestion[], n: number) {
    const round = Date.now();
    const questions = pickRound(from, history, n, round % 2147483647);
    if (questions.length === 0) return;
    setStage({ kind: "round", questions, at: 0, picked: questions.map(() => -1), round });
  }

  function answer(optionIndex: number) {
    if (stage.kind !== "round") return;
    const q = stage.questions[stage.at]!;
    if (stage.picked[stage.at]! >= 0) return;
    const picked = [...stage.picked];
    picked[stage.at] = optionIndex;
    const next = recordAnswer(history, q.id, optionIndex === q.answer);
    setHistory(next);
    writeHistory(project.key, next);
    setStage({ ...stage, picked });
  }

  function advance() {
    if (stage.kind !== "round") return;
    if (stage.at + 1 < stage.questions.length) setStage({ ...stage, at: stage.at + 1 });
    else setStage({ kind: "done", questions: stage.questions, picked: stage.picked, round: stage.round });
  }

  function forget() {
    if (!window.confirm("Forget which questions you have got right and wrong in this project's review?")) return;
    setHistory({});
    writeHistory(project.key, {});
  }

  const openStep = (q: ReviewQuestion) =>
    nav(`/projects/${project.key}/${q.moduleKey}${q.stepKey ? `?step=${q.stepKey}` : ""}`);

  const header = (
    <>
      <div className="row" style={{ marginBottom: 4 }}>
        <button className="ghost" onClick={() => nav(`/projects/${project.key}`)}>
          ← {project.title}
        </button>
        <span className="badge">{plural(all.length, "question")} in the written modules</span>
      </div>
      <h1 className="page-title" style={{ marginTop: 6 }}>
        Review
      </h1>
    </>
  );

  if (all.length === 0) {
    return (
      <div className="page">
        {header}
        <Empty icon="🔁" text="This project has no quiz questions to review yet." />
      </div>
    );
  }

  // ---- A round in progress ----------------------------------------------
  if (stage.kind === "round") {
    const q = stage.questions[stage.at]!;
    const picked = stage.picked[stage.at]!;
    const right = stage.picked.filter((p, i) => p >= 0 && p === stage.questions[i]!.answer).length;
    const answered = stage.picked.filter((p) => p >= 0).length;
    return (
      <div className="page">
        {header}
        <div className="row" style={{ alignItems: "center", gap: 10, margin: "4px 0 14px" }}>
          <div className="progress" style={{ flex: 1 }}>
            <span style={{ width: `${Math.round((answered / stage.questions.length) * 100)}%` }} />
          </div>
          <span className="dim mono" style={{ fontSize: 12 }}>
            {stage.at + 1}/{stage.questions.length} · {right} right
          </span>
          <button className="ghost" style={{ padding: "2px 8px", fontSize: 12 }} onClick={() => setStage({ kind: "setup" })}>
            Stop
          </button>
        </div>

        <p className="faint" style={{ fontSize: 12, margin: "0 0 6px" }}>
          Module {q.moduleNumber} · {q.moduleTitle}
          {q.stepTitle && ` · ${q.stepTitle}`} · {q.source}
        </p>
        <QuizItem
          key={`${stage.round}:${stage.at}`}
          index={stage.at + 1}
          question={q}
          picked={picked}
          onPick={answer}
          salt={String(stage.round)}
        />
        {picked >= 0 && (
          <div className="row" style={{ gap: 8 }}>
            <button className="primary" onClick={advance} autoFocus>
              {stage.at + 1 < stage.questions.length ? "Next question →" : "See how it went →"}
            </button>
            {picked !== q.answer && (
              <button className="ghost" onClick={() => openStep(q)}>
                Read the {q.stepTitle ? "step" : "module"} that covers this
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  // ---- The end of a round -------------------------------------------------
  if (stage.kind === "done") {
    const missed = stage.questions.filter((q, i) => stage.picked[i] !== q.answer);
    const score = stage.questions.length - missed.length;
    const pct = Math.round((score / stage.questions.length) * 100);
    return (
      <div className="page">
        {header}
        <div
          className="card"
          style={{ marginBottom: 14, borderColor: pct === 100 ? "var(--good)" : "var(--accent)" }}
        >
          <div className="row" style={{ alignItems: "baseline", gap: 10 }}>
            <strong style={{ fontSize: 22 }}>
              {score}/{stage.questions.length}
            </strong>
            <span className="dim">
              {pct === 100
                ? "Every one. These modules have stuck."
                : pct >= 70
                  ? "Solid — the misses below are the ones worth a second look."
                  : "Worth going back over the steps below before moving on."}
            </span>
          </div>
          <div className="row" style={{ gap: 8, marginTop: 12, flexWrap: "wrap" }}>
            {missed.length > 0 && (
              <button className="primary" onClick={() => start(missed, missed.length)}>
                {missed.length === 1 ? "Retry the one I missed" : `Retry the ${missed.length} I missed`}
              </button>
            )}
            <button className={missed.length ? "ghost" : "primary"} onClick={() => start(pool, size)}>
              Another round
            </button>
            <button className="ghost" onClick={() => setStage({ kind: "setup" })}>
              Change what to draw from
            </button>
          </div>
        </div>

        {missed.length > 0 && (
          <>
            <h3 style={{ marginBottom: 6 }}>What you missed</h3>
            {missed.map((q) => (
              <div key={q.id} className="card" style={{ marginBottom: 10, borderColor: "var(--bad)" }}>
                <strong>{q.question}</strong>
                <p style={{ margin: "8px 0 4px" }}>
                  <span style={{ color: "var(--good)" }}>✓ </span>
                  {q.options[q.answer]}
                </p>
                <p className="dim" style={{ margin: "0 0 8px", fontSize: 13 }}>
                  {q.explanation}
                </p>
                <button className="ghost" style={{ padding: "2px 8px", fontSize: 12 }} onClick={() => openStep(q)}>
                  Module {q.moduleNumber}
                  {q.stepTitle ? ` · ${q.stepTitle}` : ""} →
                </button>
              </div>
            ))}
          </>
        )}
      </div>
    );
  }

  // ---- Setup --------------------------------------------------------------
  return (
    <div className="page">
      {header}
      <p className="page-sub">
        The questions {project.title} asks along the way — warm-ups, step checks and module reviews
        — asked again, out of order and mixed together. Each was answered once, right under the
        explanation; this is where you find out whether it stuck. The ones you get wrong come back
        first next time.
      </p>

      <div className="card" style={{ marginBottom: 14 }}>
        <div className="io-label">Draw questions from</div>
        <div className="row" style={{ gap: 8, flexWrap: "wrap", marginTop: 6 }}>
          <button
            className={scope === "done" ? "primary" : "ghost"}
            onClick={() => setScope("done")}
            disabled={finishedCount === 0}
            title={finishedCount === 0 ? "Finish a module first" : undefined}
          >
            Modules I've finished · {finishedCount}
          </button>
          <button className={scope === "all" ? "primary" : "ghost"} onClick={() => setScope("all")}>
            Every written module
          </button>
          {phases.map((ph) => (
            <button
              key={ph.key}
              className={scope === ph.key ? "primary" : "ghost"}
              onClick={() => setScope(ph.key)}
            >
              {ph.title.replace(/^Phase (\d+) · /, "P$1 · ")}
            </button>
          ))}
        </div>

        <div className="io-label" style={{ marginTop: 14 }}>
          Round length
        </div>
        <div className="row" style={{ gap: 8, marginTop: 6 }}>
          {SIZES.map((n) => (
            <button key={n} className={size === n ? "primary" : "ghost"} onClick={() => setSize(n)}>
              {n}
            </button>
          ))}
        </div>

        <p className="dim" style={{ fontSize: 13, margin: "14px 0 0" }}>
          {pool.length === 0
            ? "Nothing to draw from here yet."
            : `${plural(pool.length, "question")} to draw from: ` +
              [
                summary.missed && `${summary.missed} you got wrong last time`,
                summary.fresh && `${summary.fresh} not yet reviewed`,
                summary.shaky && `${summary.shaky} you have missed before`,
                summary.solid && `${summary.solid} always right`,
              ]
                .filter(Boolean)
                .join(" · ") +
              "."}
        </p>

        <div className="row" style={{ gap: 8, marginTop: 14 }}>
          <button className="primary" disabled={pool.length === 0} onClick={() => start(pool, size)}>
            Start a round of {Math.min(size, pool.length)} →
          </button>
          <span className="spacer" />
          {Object.keys(history).length > 0 && (
            <button className="ghost" style={{ fontSize: 12 }} onClick={forget}>
              Forget my answers
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
