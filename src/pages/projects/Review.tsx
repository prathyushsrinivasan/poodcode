// Review — the project's own quiz questions, asked again later and mixed up.
//
// See lib/projectReview.ts for why. The page is a small state machine: choose
// what to draw from, answer a round one question at a time, then see what you
// missed with a link to the step that explains each one. What you get wrong is
// remembered (per viewer, in localStorage) and asked first next time.

import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { Project } from "../../types";
import { QuizItem } from "../../components/exercise";
import {
  collectQuestions,
  pickRound,
  poolSummary,
  recordAnswer,
  type ReviewHistory,
  type ReviewQuestion,
} from "../../lib/projectReview";
import { useToast } from "../../components/Toast";
import { plural } from "../../lib/trackProgress";
import { Badge, Button, Card, Chip, ConfirmDialog, EmptyState, Icon, PageHeader, ProgressBar, Segmented } from "../../components/ui";
import { UnitPart } from "../../components/track/UnitParts";
import { inlineCode } from "../../components/common";
import { useCrumb } from "../../store";

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
  useCrumb(project.title, "Review");
  const all = useMemo(() => collectQuestions(project), [project]);
  const [history, setHistory] = useState<ReviewHistory>(() => readHistory(project.key));
  const finishedCount = new Set(all.filter((q) => doneKeys.has(q.moduleKey)).map((q) => q.moduleKey)).size;

  // "done" draws from finished modules — the default, since reviewing a module
  // you have not reached is previewing, not reviewing. Falls back to every
  // written module when nothing is finished yet.
  const [scope, setScope] = useState<string>(finishedCount > 0 ? "done" : "all");
  const [size, setSize] = useState<number>(10);
  const [stage, setStage] = useState<Stage>({ kind: "setup" });
  const [confirmForget, setConfirmForget] = useState(false);
  const toast = useToast();

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

  /** Undo-able: the answers are handed back to the toast so a misfire costs
   * one click rather than the whole history. */
  function forget() {
    const previous = history;
    setHistory({});
    writeHistory(project.key, {});
    setConfirmForget(false);
    toast("Review answers forgotten.", {
      action: {
        label: "Undo",
        onClick: () => {
          setHistory(previous);
          writeHistory(project.key, previous);
        },
      },
    });
  }

  const stepHref = (q: ReviewQuestion) => `/projects/${project.key}/${q.moduleKey}${q.stepKey ? `?step=${q.stepKey}` : ""}`;

  const header = (
    <PageHeader
      eyebrow={<Link to={`/projects/${project.key}`}>{project.title}</Link>}
      title="Review"
      actions={<Badge icon="help">{plural(all.length, "question")} in the written modules</Badge>}
    />
  );

  if (all.length === 0) {
    return (
      <div className="page">
        {header}
        <EmptyState icon="checklist" title="This project has no quiz questions to review yet." />
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
        <div className="review-bar">
          <ProgressBar value={answered} max={stage.questions.length} label="Questions answered this round" />
          <span className="dim mono cell-small">
            {stage.at + 1}/{stage.questions.length} · {right} right
          </span>
          <Button variant="ghost" size="sm" icon="close" onClick={() => setStage({ kind: "setup" })}>
            Stop
          </Button>
        </div>

        <p className="exercise-note review-source">
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
          <div className="exercise-actions">
            <Button variant="primary" iconRight="forward" onClick={advance} autoFocus>
              {stage.at + 1 < stage.questions.length ? "Next question" : "See how it went"}
            </Button>
            {picked !== q.answer && (
              <Link className="btn ghost" to={stepHref(q)}>
                <Icon name="learn" size={14} /> Read the {q.stepTitle ? "step" : "module"} that covers this
              </Link>
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
        <Card tone={pct === 100 ? "good" : "accent"} className="unit-block">
          <div className="review-score">
            <strong className="review-score-num">
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
          <div className="exercise-actions review-actions">
            {missed.length > 0 && (
              <Button variant="primary" icon="reset" onClick={() => start(missed, missed.length)}>
                {missed.length === 1 ? "Retry the one I missed" : `Retry the ${missed.length} I missed`}
              </Button>
            )}
            <Button variant={missed.length ? "ghost" : "primary"} icon="shuffle" onClick={() => start(pool, size)}>
              Another round
            </Button>
            <Button variant="ghost" icon="sliders" onClick={() => setStage({ kind: "setup" })}>
              Change what to draw from
            </Button>
          </div>
        </Card>

        {missed.length > 0 && (
          <UnitPart title="What you missed" icon="failed">
            {missed.map((q) => (
              <Card key={q.id} tone="bad" className="unit-block">
                <strong>{inlineCode(q.question)}</strong>
                <p className="review-answer">
                  <Icon name="check" size={14} className="is-good" /> {inlineCode(q.options[q.answer] ?? "")}
                </p>
                <p className="section-lead">{q.explanation}</p>
                <Link className="btn ghost btn-sm" to={stepHref(q)}>
                  Module {q.moduleNumber}
                  {q.stepTitle ? ` · ${q.stepTitle}` : ""} <Icon name="forward" size={13} />
                </Link>
              </Card>
            ))}
          </UnitPart>
        )}
      </div>
    );
  }

  // ---- Setup --------------------------------------------------------------
  return (
    <div className="page">
      {header}
      <p className="page-sub">
        The questions {project.title} asks along the way — warm-ups, step checks and module reviews — asked again, out of
        order and mixed together. Each was answered once, right under the explanation; this is where you find out whether
        it stuck. The ones you get wrong come back first next time.
      </p>

      <Card className="unit-block review-setup">
        <div className="io-label">Draw questions from</div>
        <div className="pill-toggle" role="group" aria-label="Draw questions from">
          <Chip
            pressed={scope === "done"}
            onClick={() => setScope("done")}
            disabled={finishedCount === 0}
            count={finishedCount}
            title={finishedCount === 0 ? "Finish a module first" : undefined}
          >
            Modules I've finished
          </Chip>
          <Chip pressed={scope === "all"} onClick={() => setScope("all")}>
            Every written module
          </Chip>
          {phases.map((ph) => (
            <Chip key={ph.key} pressed={scope === ph.key} onClick={() => setScope(ph.key)}>
              {ph.title.replace(/^Phase (\d+) · /, "P$1 · ")}
            </Chip>
          ))}
        </div>

        <div className="io-label">Round length</div>
        <Segmented
          label="Round length"
          value={String(size)}
          onChange={(v) => setSize(Number(v))}
          options={SIZES.map((n) => ({ value: String(n), label: String(n) }))}
        />

        <p className="section-lead">
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

        <div className="exercise-actions">
          <Button variant="primary" iconRight="forward" disabled={pool.length === 0} onClick={() => start(pool, size)}>
            Start a round of {Math.min(size, pool.length)}
          </Button>
          <span className="spacer" />
          {Object.keys(history).length > 0 && (
            <Button variant="ghost" size="sm" icon="delete" onClick={() => setConfirmForget(true)}>
              Forget my answers
            </Button>
          )}
        </div>
      </Card>

      <ConfirmDialog
        open={confirmForget}
        onClose={() => setConfirmForget(false)}
        onConfirm={forget}
        title="Forget your review answers?"
        consequence={
          <>
            This clears which of {project.title}'s {all.length} questions you have got right and wrong, so the next round
            stops asking your weak ones first. Your module progress is not affected.
          </>
        }
        confirmLabel="Forget answers"
      />
    </div>
  );
}
