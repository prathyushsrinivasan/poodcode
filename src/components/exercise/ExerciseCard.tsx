/**
 * One exercise card for every track (UI_ROADMAP C4).
 *
 * `ExerciseCard` was implemented twice — once in `pages/Learn.tsx` (SQL-aware)
 * and once in `components/LearnExercise.tsx` (the courses, the Backend Lab and
 * Projects) — and the two had drifted: different badges, a prediction box in
 * one and a query preview in the other, and their own copies of the feedback
 * panel. This is the merge. It grades the same way everywhere, via
 * `api.runTests(null, lang, code, cases)`, with two modes chosen by
 * `exercise.judge_mode`:
 *
 *   ""/"stdout" — run the program and compare stdout against `tests`, using
 *                 the exact whitespace-normalized judge.
 *   "types"     — never run it: the program plus the exercise's hidden harness
 *                 only has to type-check. This is the only way to grade a
 *                 type, which has no runtime value to print.
 *
 * Either mode may carry `exercise.harness`: TypeScript appended to the
 * learner's code before compiling, which lets an exercise ask for a *function*
 * and grade what it returns instead of what it printed.
 *
 * SQL exercises pass `dataset`: every case runs against that database first,
 * and a "Run query" button shows what the query returns without grading it.
 *
 * The frame (`./Frame.tsx`) is separate so a card that is not
 * code — spot-the-bug, a quiz question — can have the same header, prompt,
 * action row and verdict slot.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api";
import type { Exercise, JudgeReport, Problem, SqlDataset, SqlOut, TestCase } from "../../types";
import { recordExerciseRun } from "../../lib/learnProgress";
import { logMismatch, predictionMatches } from "../../lib/predict";
import { Markdown } from "../Markdown";
import { OrderLines, SpotCard } from "../ParsonsExercise";
import type { IconName } from "../ui/Icon";
import { ExerciseFrame, ExerciseActions, ExerciseEditor } from "./Frame";
import { Button } from "../ui/Button";
import { Badge, type Tone } from "../ui/Card";
import {
  HintButton,
  HintPanel,
  JudgeFeedback,
  ReferenceCode,
  RunError,
  SqlPreview,
  VerdictPanel,
  useHintLadder,
} from "./Verdict";

// ---- Kinds ------------------------------------------------------------------

/**
 * Per-kind presentation. `whole` marks the kinds that hand over a complete
 * program rather than a line with a blank in it, which want the roomier editor
 * and the accent frame a challenge gets. Kinds absent from this table (notably
 * "drill" and "challenge") fall through to the plain treatment, so an
 * unrecognised kind renders rather than breaking.
 */
const KIND_STYLE: Record<string, { label: string; icon: IconName; tone: Tone; whole: boolean }> = {
  fix: { label: "fix the bug", icon: "tools", tone: "bad", whole: true },
  diagnose: { label: "read the error", icon: "terminal", tone: "bad", whole: true },
  retype: { label: "retype the any", icon: "edit", tone: "warn", whole: true },
  predict: { label: "predict the type", icon: "sparkles", tone: "accent", whole: false },
  design: { label: "types first", icon: "braces", tone: "accent", whole: true },
  order: { label: "put it in order", icon: "layers", tone: "accent", whole: false },
  refactor: { label: "refactor", icon: "build", tone: "warn", whole: true },
};

// ---- The card -----------------------------------------------------------------

export type ExerciseCardProps = {
  index: number;
  exercise: Exercise;
  /** A full problem this drill leads into. */
  source?: Problem;
  challenge?: boolean;
  onSolved?: (id: string) => void;
  /** Ask for a prediction of the first test's output before a run (M1-03). */
  predictFirst?: boolean;
  /** SQL track: the database this exercise queries. */
  dataset?: SqlDataset;
};

/** One exercise, whatever its kind. "Spot the bug" is answered by clicking a
 * line, not by running code, so it has a card of its own. */
export function ExerciseCard(props: ExerciseCardProps) {
  if (props.exercise.kind === "spot") {
    return <SpotCard index={props.index} exercise={props.exercise} onSolved={props.onSolved} />;
  }
  return <CodeExerciseCard {...props} />;
}

function readDraft(key: string, fallback: string): string {
  try {
    return localStorage.getItem(key) ?? fallback;
  } catch {
    return fallback;
  }
}

function CodeExerciseCard({
  index,
  exercise,
  source,
  challenge = false,
  onSolved,
  predictFirst = false,
  dataset,
}: ExerciseCardProps) {
  const nav = useNavigate();
  const storeKey = `poodcode:learn-ex:${exercise.id}`;
  const lang = exercise.language || "java";
  const isSql = lang === "sql";
  const [code, setCode] = useState<string>(() => readDraft(storeKey, exercise.starter));
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState("");
  const [showSolution, setShowSolution] = useState(false);
  const [showChecks, setShowChecks] = useState(false);
  const [prediction, setPrediction] = useState("");
  const [verdict, setVerdict] = useState<null | { match: boolean; actual: string }>(null);
  // The SQL track's scratch run: the learner's query against the base dataset,
  // showing whatever it returns rather than a pass/fail. Looking at the wrong
  // answer is most of how you get to the right one.
  const [preview, setPreview] = useState<SqlOut | null>(null);
  const hints = useHintLadder(exercise.hints, exercise.hint);

  const kind = KIND_STYLE[exercise.kind];
  const big = challenge || !!kind?.whole;
  const hasBlank = exercise.starter.includes("____");
  // A type-level exercise is never run: it passes when the compiler accepts the
  // assertions in its harness. There are no test cases and no output to show.
  const isTypes = exercise.judge_mode === "types";
  // A Parsons problem is reordered, not typed; its prompt already shows the output.
  const isOrder = exercise.kind === "order";
  const predicting = predictFirst && !isTypes && !isOrder && exercise.tests.length > 0;

  function update(v: string) {
    setCode(v);
    try {
      localStorage.setItem(storeKey, v);
    } catch {
      /* the draft is a convenience; the editor still holds the code */
    }
  }

  function reset() {
    update(exercise.starter);
    setReport(null);
    setPreview(null);
    setErr("");
    setShowSolution(false);
  }

  /** The SQL a case runs against: the dataset, then that case's variation on it.
   * Keeping the shared schema out of the individual tests is what stops a 4 KB
   * CREATE/INSERT batch from being repeated inside every exercise — see
   * `Exercise.dataset` and tools/sql_defs.py. */
  function setupFor(caseInput: string): string {
    if (!isSql) return caseInput;
    const base = dataset?.sql ?? "";
    return caseInput.trim() ? `${base}\n${caseInput}\n` : base;
  }

  async function check() {
    setRunning(true);
    setErr("");
    setReport(null);
    setPreview(null);
    const cases: TestCase[] = exercise.tests.map((t, i) => ({
      id: 0,
      problem_id: 0,
      kind: "example",
      name: isSql && t.input.trim() ? `Test ${i + 1} (changed data)` : `Test ${i + 1}`,
      input: setupFor(t.input),
      expected_output: t.output,
      ordering: i,
    }));
    try {
      const r = await api.runTests(null, lang, code, cases, {
        strictness: exercise.strictness,
        harness: exercise.harness,
        judgeMode: exercise.judge_mode,
        forbid: exercise.forbid,
      });
      setReport(r);
      recordExerciseRun(exercise.id, r.status === "accepted");
      const first = r.results[0];
      if (predicting && first && !r.compile_error) {
        const match = predictionMatches(prediction, first.actual);
        setVerdict({ match, actual: first.actual });
        if (!match) logMismatch(exercise.id, prediction, first.actual);
      }
      if (r.status === "accepted") onSolved?.(exercise.id);
    } catch (e) {
      setErr(String(e));
    } finally {
      setRunning(false);
    }
  }

  /** Run the query against the base dataset and just show what comes back. */
  async function runQuery() {
    if (!dataset) return;
    setRunning(true);
    setErr("");
    setReport(null);
    try {
      setPreview(await api.sqlQuery(dataset.sql, code));
    } catch (e) {
      setErr(String(e));
    } finally {
      setRunning(false);
    }
  }

  const untouched = hasBlank && (code === exercise.starter || code.includes("____"));
  const solved = report?.status === "accepted";
  const needsPrediction = predicting && prediction.trim() === "";

  const badges = (
    <>
      {kind && (
        <Badge tone={kind.tone} icon={kind.icon}>
          {kind.label}
        </Badge>
      )}
      {isTypes && (
        <Badge tone="accent" icon="braces">
          type-level
        </Badge>
      )}
      {exercise.difficulty && <span className={`badge diff ${exercise.difficulty}`}>{exercise.difficulty}</span>}
      {isSql && exercise.tests.length > 1 && (
        <Badge
          title={`Checked against ${exercise.tests.length} datasets — the same schema with the data changed, so a hard-coded answer fails`}
        >
          {exercise.tests.length} datasets
        </Badge>
      )}
      {isSql && dataset && (
        <Badge icon="database" title={dataset.summary}>
          {dataset.key}
        </Badge>
      )}
      <Badge>{lang}</Badge>
    </>
  );

  return (
    // pre-wrap on a string prompt keeps an authored line break. A "read the
    // error" prompt quotes the compiler's message on its own indented line, and
    // collapsing that into the running text is exactly the thing being taught.
    <ExerciseFrame index={index} title={exercise.title} solved={solved} emphasis={big} badges={badges} prompt={exercise.prompt}>
      {/* Say the ban up front. Finding out only on submission that `typeof` was
          never going to be accepted reads as a broken exercise, not as a rule. */}
      {exercise.forbid && exercise.forbid.length > 0 && (
        <p className="exercise-note exercise-forbid">
          Not allowed here:{" "}
          {exercise.forbid.map((f, i) => (
            <span key={f}>
              {i > 0 && ", "}
              <code>{f}</code>
            </span>
          ))}
        </p>
      )}

      {isOrder ? (
        <OrderLines value={code} solution={exercise.solution} onChange={update} disabled={running} />
      ) : (
        <ExerciseEditor
          language={lang}
          value={code}
          onChange={update}
          onRun={check}
          strictness={exercise.strictness}
          lines={exercise.starter.split("\n").length}
          roomy={big}
        />
      )}

      {predicting && (
        <div className="predict-box">
          <label className="io-label" htmlFor={`predict-${exercise.id}`}>
            Predict first — for this input, your code will print:
          </label>
          <pre className="io-block predict-input">{exercise.tests[0]!.input || "(no input)"}</pre>
          <textarea
            id={`predict-${exercise.id}`}
            className="predict-text"
            value={prediction}
            onChange={(e) => {
              setPrediction(e.target.value);
              setVerdict(null);
            }}
            placeholder="Write the output you expect, line by line — then run."
          />
          {verdict && (
            <p className={`quiz-note predict-verdict ${verdict.match ? "is-good" : "is-bad"}`}>
              {verdict.match
                ? "✓ Exactly what it printed — you read your own code right."
                : `✗ It printed ${JSON.stringify(verdict.actual.trim())} — a learning moment, logged for review.`}
            </p>
          )}
        </div>
      )}

      <ExerciseActions>
        <Button
          variant="primary"
          icon={isTypes ? "braces" : "check"}
          onClick={check}
          loading={running}
          disabled={needsPrediction}
          title={needsPrediction ? "Write your prediction first." : undefined}
          shortcut="Ctrl+Enter"
        >
          {running ? "Checking…" : isTypes ? "Type-check" : "Check"}
        </Button>
        {isSql && dataset && (
          <Button
            variant="ghost"
            icon="run"
            onClick={runQuery}
            disabled={running}
            title="Run this SQL against the dataset and just show the result — no pass/fail"
          >
            Run query
          </Button>
        )}
        <Button variant="ghost" icon="reset" onClick={reset} disabled={running}>
          Reset
        </Button>
        <HintButton ladder={hints} />
        <Button
          variant="ghost"
          icon={showSolution ? "hide" : "show"}
          onClick={() => setShowSolution((s) => !s)}
          aria-expanded={showSolution}
        >
          {showSolution ? "Hide solution" : "Reveal solution"}
        </Button>
        {/* A type-level exercise's assertions are worth reading — they say
            precisely what the type has to do, and unlike hidden stdout tests
            there is nothing to game: you cannot satisfy `Expect<Equal<…>>`
            without actually writing the type. */}
        {isTypes && exercise.harness && (
          <Button variant="ghost" icon="checklist" onClick={() => setShowChecks((s) => !s)} aria-expanded={showChecks}>
            {showChecks ? "Hide checks" : "What's being checked?"}
          </Button>
        )}
        {untouched && !running && (
          <span className="exercise-note">
            Replace the <code>____</code> before checking.
          </span>
        )}
      </ExerciseActions>

      {isSql && (
        <p className="exercise-note">
          Tip: put <code>EXPLAIN QUERY PLAN</code> in front of your query and press <strong>Run query</strong> to see
          how SQLite intends to execute it.
        </p>
      )}

      <HintPanel ladder={hints} />

      {showChecks && exercise.harness && (
        <div className="exercise-checks">
          <div className="io-label">These must compile against your code</div>
          <Markdown>{"```ts\n" + exercise.harness.trim() + "\n```"}</Markdown>
        </div>
      )}

      <RunError error={err} />
      {preview && <SqlPreview out={preview} />}
      {report && (
        <JudgeFeedback
          report={report}
          isSql={isSql}
          check={isTypes ? { harness: exercise.harness ?? "", code } : undefined}
        />
      )}

      {/* Why the answer is the answer — a repair's pitfall, or a "three ways"
          comparison. Kept until solved: it would give the fix away. */}
      {solved && exercise.explanation && (
        <VerdictPanel tone="info" icon="sparkles" title="Why this works">
          <Markdown>{exercise.explanation}</Markdown>
        </VerdictPanel>
      )}

      {showSolution && <ReferenceCode code={exercise.solution} language={lang} />}

      {source && (
        <p className="exercise-next">
          Ready for the whole thing?{" "}
          <button type="button" className="link-button" onClick={() => nav(`/solve/${source.id}`)}>
            Open “{source.title}” →
          </button>
        </p>
      )}
    </ExerciseFrame>
  );
}
