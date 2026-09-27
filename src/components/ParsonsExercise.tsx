// The widgets for the two exercise kinds that are not typed into an editor:
// `order` (Parsons: put shuffled lines back in order) and `spot` (click the
// line that holds the bug). Logic lives in lib/parsons.ts.
import { useState } from "react";
import { api } from "../api";
import type { Exercise, JudgeReport, TestCase } from "../types";
import { recordExerciseRun } from "../lib/learnProgress";
import { fromLines, inPlace, isBugLine, moveLine, toLines } from "../lib/parsons";
import { Markdown } from "./Markdown";
import { ExerciseActions, ExerciseEditor, ExerciseFrame } from "./exercise/Frame";
import { JudgeFeedback, ReferenceCode, VerdictPanel } from "./exercise/Verdict";
import { Badge } from "./ui/Card";
import { Button, IconButton } from "./ui/Button";
import { Icon } from "./ui/Icon";

/** The reorderable list an `order` exercise shows instead of an editor. Drag a
 * line, or use its arrows; the program is `value`, one piece per line. */
export function OrderLines({
  value,
  solution,
  onChange,
  disabled,
}: {
  value: string;
  solution: string;
  onChange: (code: string) => void;
  disabled?: boolean;
}) {
  const lines = toLines(value);
  const [dragging, setDragging] = useState<number | null>(null);
  const [over, setOver] = useState<number | null>(null);
  const move = (from: number, to: number) => onChange(fromLines(moveLine(lines, from, to)));

  return (
    <div className="order-lines" role="list" aria-label="Lines to put in order">
      {lines.map((line, i) => (
        <div
          key={`${i}:${line}`}
          role="listitem"
          className={"order-line" + (dragging === i ? " dragging" : "") + (over === i && dragging !== i ? " over" : "")}
          draggable={!disabled}
          onDragStart={(e) => {
            setDragging(i);
            e.dataTransfer.effectAllowed = "move";
          }}
          onDragOver={(e) => {
            e.preventDefault();
            setOver(i);
          }}
          onDragLeave={() => setOver((o) => (o === i ? null : o))}
          onDrop={(e) => {
            e.preventDefault();
            if (dragging !== null) move(dragging, i);
            setDragging(null);
            setOver(null);
          }}
          onDragEnd={() => {
            setDragging(null);
            setOver(null);
          }}
        >
          <span className="order-grip" aria-hidden>
            <Icon name="more" size={14} />
          </span>
          <code className="order-code">{line}</code>
          <span className="order-arrows">
            <IconButton
              size="sm"
              icon="chevronUp"
              label={`Move line ${i + 1} up`}
              disabled={disabled || i === 0}
              onClick={() => move(i, i - 1)}
            />
            <IconButton
              size="sm"
              icon="chevronDown"
              label={`Move line ${i + 1} down`}
              disabled={disabled || i === lines.length - 1}
              onClick={() => move(i, i + 1)}
            />
          </span>
        </div>
      ))}
      <div className="dim quiz-note order-status">
        {inPlace(lines, solution)}/{lines.length} lines where the worked example has them — any order that
        prints the right thing passes.
      </div>
    </div>
  );
}

/** A "spot the bug" exercise: the program, one clickable line at a time. */
export function SpotCard({
  index,
  exercise,
  onSolved,
}: {
  index: number;
  exercise: Exercise;
  onSolved?: (id: string) => void;
}) {
  const storeKey = `poodcode:learn-spot:${exercise.id}`;
  const lines = toLines(exercise.starter);
  const [solved, setSolved] = useState(() => {
    try {
      return localStorage.getItem(storeKey) === "solved";
    } catch {
      return false;
    }
  });
  const [misses, setMisses] = useState<number[]>([]);
  const [revealed, setRevealed] = useState(false);
  const show = solved || revealed;

  function pick(n: number) {
    if (show) return;
    if (isBugLine(exercise.lines, n)) {
      setSolved(true);
      try {
        localStorage.setItem(storeKey, "solved");
      } catch {
        /* progress still counts for this session */
      }
      recordExerciseRun(exercise.id, true);
      onSolved?.(exercise.id);
    } else if (!misses.includes(n)) {
      setMisses((m) => [...m, n]);
      recordExerciseRun(exercise.id, false);
    }
  }

  return (
    <ExerciseFrame
      index={index}
      title={exercise.title}
      solved={solved}
      emphasis
      prompt={exercise.prompt}
      badges={
        <>
          <Badge tone="bad" icon="search">
            spot the bug
          </Badge>
          <Badge>{exercise.language || "typescript"}</Badge>
        </>
      }
    >
      <div className="spot-lines" role="list" aria-label="Program lines — click the buggy one">
        {lines.map((line, i) => {
          const n = i + 1;
          const bug = isBugLine(exercise.lines, n);
          const state = show && bug ? " bug" : misses.includes(n) ? " miss" : "";
          return (
            <button
              key={n}
              role="listitem"
              className={"spot-line" + state}
              onClick={() => pick(n)}
              disabled={show && !bug}
            >
              <span className="spot-num">{n}</span>
              <code>{line || " "}</code>
            </button>
          );
        })}
      </div>
      {misses.length > 0 && !show && (
        <p className="quiz-note is-bad">
          Not line {misses[misses.length - 1]}. Work back from what goes wrong to the line that makes it
          happen.
        </p>
      )}
      {!show && (
        <ExerciseActions>
          <Button variant="ghost" icon="show" onClick={() => setRevealed(true)}>
            Reveal the answer
          </Button>
        </ExerciseActions>
      )}
      {show && (
        <VerdictPanel tone={solved ? "good" : "info"} title={solved ? "Found it" : "The bug"}>
          {exercise.explanation && <Markdown>{exercise.explanation}</Markdown>}
        </VerdictPanel>
      )}
      {show && <FixStage exercise={exercise} gaveUp={revealed && !solved} />}
    </ExerciseFrame>
  );
}

/** Stage two of a spot-the-bug card (X-11): now repair it. The program is the
 * one just read; the tests are what the corrected program prints, so any fix
 * that behaves right passes — the reference fix stays hidden until asked for. */
function FixStage({ exercise, gaveUp }: { exercise: Exercise; gaveUp: boolean }) {
  const storeKey = `poodcode:learn-spot-fix:${exercise.id}`;
  const [code, setCode] = useState(() => {
    try {
      return localStorage.getItem(storeKey) ?? exercise.starter;
    } catch {
      return exercise.starter;
    }
  });
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState(false);
  const [showFix, setShowFix] = useState(gaveUp);
  const lang = exercise.language || "typescript";

  function update(v: string) {
    setCode(v);
    try {
      localStorage.setItem(storeKey, v);
    } catch {
      /* the draft is a convenience */
    }
  }

  async function check() {
    setRunning(true);
    try {
      const cases: TestCase[] = exercise.tests.map((t, i) => ({
        id: 0,
        problem_id: 0,
        kind: "example",
        name: `Test ${i + 1}`,
        input: t.input,
        expected_output: t.output,
        ordering: i,
      }));
      setReport(await api.runTests(null, lang, code, cases, { strictness: exercise.strictness }));
    } finally {
      setRunning(false);
    }
  }

  const fixed = report?.status === "accepted";
  return (
    <div className="spot-fix">
      <div className="io-label">
        {fixed ? <span className="is-good">✓ Fixed</span> : "Now fix it — the tests are what the corrected program prints"}
      </div>
      <ExerciseEditor
        language={lang}
        value={code}
        onChange={update}
        onRun={check}
        strictness={exercise.strictness}
        lines={toLines(exercise.starter).length}
        maxHeight={360}
      />
      <ExerciseActions>
        <Button variant="primary" icon="check" onClick={check} loading={running} shortcut="Ctrl+Enter">
          {running ? "Checking…" : "Check"}
        </Button>
        <Button variant="ghost" icon="reset" onClick={() => update(exercise.starter)} disabled={running}>
          Reset
        </Button>
        <Button variant="ghost" icon={showFix ? "hide" : "show"} onClick={() => setShowFix((v) => !v)} aria-expanded={showFix}>
          {showFix ? "Hide the fix" : "Show the fix"}
        </Button>
      </ExerciseActions>
      {report && <JudgeFeedback report={report} />}
      {showFix && (
        <>
          <ReferenceCode code={exercise.solution} language="ts" />
          {exercise.tests[0] && (
            <>
              <div className="io-label">Prints</div>
              <pre className="io-block">{exercise.tests[0].output || "(nothing)"}</pre>
            </>
          )}
        </>
      )}
    </div>
  );
}
