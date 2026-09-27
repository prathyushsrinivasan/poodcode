// The widgets for the two exercise kinds that are not typed into an editor:
// `order` (Parsons: put shuffled lines back in order) and `spot` (click the
// line that holds the bug). Logic lives in lib/parsons.ts.
import { useState } from "react";
import { api } from "../api";
import type { Exercise, JudgeReport, TestCase } from "../types";
import { recordExerciseRun } from "../lib/learnProgress";
import { fromLines, inPlace, isBugLine, moveLine, toLines } from "../lib/parsons";
import { Markdown } from "./Markdown";
import { CodeEditor } from "./CodeEditor";
import { FailingCases } from "./OutputCompare";

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
            ⋮⋮
          </span>
          <code className="order-code">{line}</code>
          <span className="order-arrows">
            <button
              className="ghost"
              aria-label={`Move line ${i + 1} up`}
              disabled={disabled || i === 0}
              onClick={() => move(i, i - 1)}
            >
              ↑
            </button>
            <button
              className="ghost"
              aria-label={`Move line ${i + 1} down`}
              disabled={disabled || i === lines.length - 1}
              onClick={() => move(i, i + 1)}
            >
              ↓
            </button>
          </span>
        </div>
      ))}
      <div className="dim quiz-note" style={{ marginTop: 4, fontFamily: "var(--font-sans)" }}>
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
    <div className="card" style={{ marginBottom: 14, borderColor: solved ? "var(--good)" : "var(--accent)" }}>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <strong>
          {index}. {exercise.title} {solved && <span style={{ color: "var(--good)" }}>✓</span>}
        </strong>
        <span className="row" style={{ gap: 6 }}>
          <span className="badge" style={{ borderColor: "var(--bad)", color: "var(--bad)" }}>
            🔎 spot the bug
          </span>
          <span className="badge">{exercise.language || "typescript"}</span>
        </span>
      </div>
      <p style={{ margin: "6px 0 10px", whiteSpace: "pre-wrap" }}>{exercise.prompt}</p>
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
        <p className="quiz-note" style={{ margin: "6px 0 0", color: "var(--bad)" }}>
          Not line {misses[misses.length - 1]}. Work back from what goes wrong to the line that makes it
          happen.
        </p>
      )}
      <div className="row" style={{ marginTop: 10, gap: 8 }}>
        {!show && (
          <button className="ghost" onClick={() => setRevealed(true)}>
            Reveal the answer
          </button>
        )}
      </div>
      {show && (
        <div className="card" style={{ marginTop: 10, marginBottom: 0, background: "var(--accent-dim)" }}>
          <div className="io-label" style={{ color: solved ? "var(--good)" : "var(--accent)" }}>
            {solved ? "Found it" : "The bug"}
          </div>
          {exercise.explanation && <Markdown>{exercise.explanation}</Markdown>}
        </div>
      )}
      {show && <FixStage exercise={exercise} gaveUp={revealed && !solved} />}
    </div>
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
  const failing = report ? report.results.filter((r) => !r.passed) : [];
  return (
    <div style={{ marginTop: 10 }}>
      <div className="io-label">
        {fixed ? <span style={{ color: "var(--good)" }}>✓ Fixed</span> : "Now fix it — the tests are what the corrected program prints"}
      </div>
      <div style={{ height: Math.min(360, toLines(exercise.starter).length * 20 + 30), border: "1px solid var(--border)", borderRadius: 6, overflow: "hidden" }}>
        <CodeEditor language={lang} value={code} onChange={update} onRun={check} tsStrictness={exercise.strictness} />
      </div>
      <div className="row" style={{ marginTop: 8, gap: 8 }}>
        <button onClick={check} disabled={running}>
          {running ? "Checking…" : "Check"}
        </button>
        <button className="ghost" onClick={() => update(exercise.starter)} disabled={running}>
          Reset
        </button>
        <button className="ghost" onClick={() => setShowFix((v) => !v)}>
          {showFix ? "Hide the fix" : "Show the fix"}
        </button>
      </div>
      {report?.compile_error && (
        <pre className="io-block" style={{ marginTop: 8, whiteSpace: "pre-wrap", fontSize: 12, borderColor: "var(--bad)" }}>
          {report.compile_error}
        </pre>
      )}
      {report && !report.compile_error && !fixed && <FailingCases failing={failing} />}
      {showFix && (
        <div style={{ marginTop: 8 }}>
          <Markdown>{"```ts\n" + exercise.solution + "```"}</Markdown>
          {exercise.tests[0] && (
            <>
              <div className="io-label">Prints</div>
              <pre className="io-block" style={{ margin: 0, fontSize: 12 }}>
                {exercise.tests[0].output || "(nothing)"}
              </pre>
            </>
          )}
        </div>
      )}
    </div>
  );
}
