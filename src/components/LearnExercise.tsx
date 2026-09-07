// Shared, judge-backed exercise + quiz widgets for the Learn tab and the
// TypeScript course. Both surfaces render half-coded drills / coding challenges
// and grade them the *same* way — via `api.runTests(null, lang, code, cases)`.
//
// Two grading modes, chosen by `exercise.judge_mode`:
//
//   ""/"stdout" — run the program and compare stdout against `tests`, using the
//                 exact whitespace-normalized judge.
//   "types"     — never run it: the program plus the exercise's hidden harness
//                 only has to type-check. This is the only way to grade a type,
//                 which has no runtime value to print.
//
// Either mode may carry `exercise.harness`: TypeScript appended to the
// learner's code before compiling, which lets an exercise ask for a *function*
// and grade what it returns instead of what it printed.
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Exercise, JudgeReport, Problem, QuizQuestion, TestCase } from "../types";
import { Markdown } from "./Markdown";
import { CodeEditor } from "./CodeEditor";

export function ExerciseCard({
  index,
  exercise,
  source,
  challenge = false,
  onSolved,
}: {
  index: number;
  exercise: Exercise;
  source?: Problem;
  challenge?: boolean;
  onSolved?: (id: string) => void;
}) {
  const nav = useNavigate();
  const storeKey = `poodcode:learn-ex:${exercise.id}`;
  const lang = exercise.language || "java";
  const [code, setCode] = useState<string>(
    () => localStorage.getItem(storeKey) ?? exercise.starter
  );
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState("");
  const [hintsShown, setHintsShown] = useState(0);
  const [showSolution, setShowSolution] = useState(false);
  const [showChecks, setShowChecks] = useState(false);

  // Progressive hint ladder (nudge → strategy → near-answer); fall back to the
  // single legacy `hint` when no ladder is authored.
  const hintLadder =
    exercise.hints && exercise.hints.length > 0
      ? exercise.hints
      : exercise.hint
      ? [exercise.hint]
      : [];

  // "fix" = a complete but buggy program to correct; like a challenge, it's a
  // full program (no ____ blank) so it wants a roomier editor and accent frame.
  const isFix = exercise.kind === "fix";
  const big = challenge || isFix;
  const hasBlank = exercise.starter.includes("____");
  // A type-level exercise is never run: it passes when the compiler accepts the
  // assertions in its harness. There are no test cases and no output to show.
  const isTypes = exercise.judge_mode === "types";

  const height = Math.min(
    Math.max(exercise.starter.split("\n").length * 20 + 24, big ? 260 : 150),
    big ? 560 : 480
  );

  function update(v: string) {
    setCode(v);
    localStorage.setItem(storeKey, v);
  }

  function reset() {
    update(exercise.starter);
    setReport(null);
    setErr("");
    setShowSolution(false);
  }

  async function check() {
    setRunning(true);
    setErr("");
    setReport(null);
    const cases: TestCase[] = exercise.tests.map((t, i) => ({
      id: 0,
      problem_id: 0,
      kind: "example",
      name: `Test ${i + 1}`,
      input: t.input,
      expected_output: t.output,
      ordering: i,
    }));
    try {
      const r = await api.runTests(null, lang, code, cases, {
        strictness: exercise.strictness,
        harness: exercise.harness,
        judgeMode: exercise.judge_mode,
      });
      setReport(r);
      if (r.status === "accepted") onSolved?.(exercise.id);
    } catch (e) {
      setErr(String(e));
    } finally {
      setRunning(false);
    }
  }

  const untouched = hasBlank && (code === exercise.starter || code.includes("____"));
  const solved = report?.status === "accepted";

  return (
    <div
      className="card"
      style={{
        marginBottom: 14,
        borderColor: solved
          ? "var(--good)"
          : big
          ? "var(--accent)"
          : undefined,
      }}
    >
      <div className="row" style={{ justifyContent: "space-between" }}>
        <strong>
          {index}. {exercise.title} {solved && <span style={{ color: "var(--good)" }}>✓</span>}
        </strong>
        <span className="row" style={{ gap: 6 }}>
          {isFix && (
            <span className="badge" style={{ borderColor: "var(--bad)", color: "var(--bad)" }}>
              🐞 fix the bug
            </span>
          )}
          {isTypes && (
            <span className="badge" style={{ borderColor: "var(--accent)", color: "var(--accent)" }}>
              🧬 type-level
            </span>
          )}
          {exercise.difficulty && (
            <span className={`badge diff ${exercise.difficulty}`}>{exercise.difficulty}</span>
          )}
          <span className="badge">{lang}</span>
        </span>
      </div>
      <p style={{ margin: "6px 0 10px" }}>{exercise.prompt}</p>

      <div
        style={{
          height,
          border: "1px solid var(--border)",
          borderRadius: 6,
          overflow: "hidden",
        }}
      >
        <CodeEditor language={lang} value={code} onChange={update} onRun={check} />
      </div>

      <div className="row" style={{ marginTop: 10, flexWrap: "wrap", gap: 8 }}>
        <button onClick={check} disabled={running}>
          {running ? "Checking…" : isTypes ? "Type-check" : "Check"}
        </button>
        <button className="ghost" onClick={reset} disabled={running}>
          Reset
        </button>
        {hintsShown < hintLadder.length && (
          <button className="ghost" onClick={() => setHintsShown((n) => n + 1)}>
            {hintsShown === 0
              ? hintLadder.length > 1
                ? `Hint (${hintLadder.length})`
                : "Hint"
              : `Next hint (${hintsShown}/${hintLadder.length})`}
          </button>
        )}
        <button className="ghost" onClick={() => setShowSolution((s) => !s)}>
          {showSolution ? "Hide solution" : "Reveal solution"}
        </button>
        {/* A type-level exercise's assertions are worth reading — they say
            precisely what the type has to do, and unlike hidden stdout tests
            there is nothing to game: you cannot satisfy `Expect<Equal<…>>`
            without actually writing the type. */}
        {isTypes && exercise.harness && (
          <button className="ghost" onClick={() => setShowChecks((s) => !s)}>
            {showChecks ? "Hide checks" : "What's being checked?"}
          </button>
        )}
        {untouched && !running && (
          <span className="dim" style={{ fontSize: 12, alignSelf: "center" }}>
            Replace the <code>____</code> before checking.
          </span>
        )}
      </div>

      {hintsShown > 0 && (
        <div
          className="card"
          style={{ marginTop: 10, marginBottom: 0, background: "var(--accent-dim)" }}
        >
          <div className="io-label" style={{ color: "var(--accent)" }}>
            {hintLadder.length > 1 ? `Hints (${hintsShown}/${hintLadder.length})` : "Hint"}
          </div>
          {hintLadder.slice(0, hintsShown).map((h, i) => (
            <p key={i} style={{ margin: i === 0 ? 0 : "6px 0 0" }}>
              {hintLadder.length > 1 && <strong>{i + 1}. </strong>}
              {h}
            </p>
          ))}
        </div>
      )}

      {showChecks && exercise.harness && (
        <div style={{ marginTop: 10 }}>
          <div className="io-label">These must compile against your code</div>
          <Markdown>{"```ts\n" + exercise.harness.trim() + "\n```"}</Markdown>
        </div>
      )}

      {err && (
        <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
          <div className="io-label" style={{ color: "var(--bad)" }}>Couldn’t run</div>
          <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 12 }}>{err}</pre>
        </div>
      )}

      {report && <Feedback report={report} />}

      {showSolution && (
        <div style={{ marginTop: 10 }}>
          <Markdown>{"```" + lang + "\n" + exercise.solution + "\n```"}</Markdown>
        </div>
      )}

      {source && (
        <div className="dim" style={{ marginTop: 8, fontSize: 13 }}>
          Ready for the whole thing?{" "}
          <a
            style={{ cursor: "pointer", color: "var(--accent)" }}
            onClick={() => nav(`/solve/${source.id}`)}
          >
            Open “{source.title}” →
          </a>
        </div>
      )}
    </div>
  );
}

/** A language-agnostic multiple-choice self-check quiz. Graded entirely on the
 * client by comparing the picked option index — no code execution. Tracks a
 * running score across the concept's questions. */
export function QuizSection({ questions }: { questions: QuizQuestion[] }) {
  // picked[i] = the option index the user chose for question i, or -1 if unanswered.
  const [picked, setPicked] = useState<number[]>(() => questions.map(() => -1));

  const answered = picked.filter((p) => p >= 0).length;
  const correct = picked.filter((p, i) => p === questions[i].answer).length;

  return (
    <div>
      {answered > 0 && (
        <div className="row" style={{ marginBottom: 10, gap: 8, alignItems: "center" }}>
          <span
            className="badge"
            style={{
              borderColor: correct === questions.length ? "var(--good)" : "var(--accent)",
              color: correct === questions.length ? "var(--good)" : "var(--accent)",
            }}
          >
            Score {correct}/{questions.length}
          </span>
          <span className="dim" style={{ fontSize: 12 }}>
            {answered}/{questions.length} answered
          </span>
          {answered > 0 && (
            <button
              className="ghost"
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => setPicked(questions.map(() => -1))}
            >
              Reset
            </button>
          )}
        </div>
      )}
      {questions.map((q, qi) => (
        <QuizItem
          key={qi}
          index={qi + 1}
          question={q}
          picked={picked[qi]}
          onPick={(oi) =>
            setPicked((prev) => {
              if (prev[qi] >= 0) return prev; // lock the first answer
              const next = [...prev];
              next[qi] = oi;
              return next;
            })
          }
        />
      ))}
    </div>
  );
}

function QuizItem({
  index,
  question,
  picked,
  onPick,
}: {
  index: number;
  question: QuizQuestion;
  picked: number;
  onPick: (optionIndex: number) => void;
}) {
  const answered = picked >= 0;
  const isRight = picked === question.answer;

  return (
    <div
      className="card"
      style={{
        marginBottom: 12,
        borderColor: answered ? (isRight ? "var(--good)" : "var(--bad)") : undefined,
      }}
    >
      <strong>
        {index}. {question.question}
      </strong>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 10 }}>
        {question.options.map((opt, oi) => {
          let border: string | undefined;
          let color: string | undefined;
          if (answered) {
            if (oi === question.answer) {
              border = "var(--good)";
              color = "var(--good)";
            } else if (oi === picked) {
              border = "var(--bad)";
              color = "var(--bad)";
            }
          }
          return (
            <button
              key={oi}
              className="ghost"
              style={{ textAlign: "left", borderColor: border, color, padding: "8px 12px" }}
              onClick={() => onPick(oi)}
              disabled={answered}
            >
              {answered && oi === question.answer && "✓ "}
              {answered && oi === picked && oi !== question.answer && "✗ "}
              {opt}
            </button>
          );
        })}
      </div>
      {answered && (
        <div
          className="card"
          style={{
            marginTop: 10,
            marginBottom: 0,
            background: "var(--accent-dim)",
            borderColor: isRight ? "var(--good)" : "var(--bad)",
          }}
        >
          <div
            className="io-label"
            style={{ color: isRight ? "var(--good)" : "var(--bad)" }}
          >
            {isRight ? "Correct" : "Not quite"}
          </div>
          <p style={{ margin: 0 }}>{question.explanation}</p>
        </div>
      )}
    </div>
  );
}

export function Feedback({ report }: { report: JudgeReport }) {
  if (report.status === "not_installed") {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
        <div className="io-label" style={{ color: "var(--bad)" }}>Runtime not available</div>
        <p style={{ margin: 0 }}>
          {report.not_installed_hint || "The toolchain for this language isn't installed."}
        </p>
      </div>
    );
  }

  if (report.compile_error) {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
        <div className="io-label" style={{ color: "var(--bad)" }}>Compile error</div>
        <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 12 }}>
          {report.compile_error}
        </pre>
      </div>
    );
  }

  // A type-level exercise has no cases: the backend reports one synthetic
  // `typecheck` result, and a failure has already been rendered above as a
  // compile error. "1/1 tests passed" would be a lie about what happened.
  if (report.results.length === 1 && report.results[0].kind === "typecheck") {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--good)" }}>
        <div className="io-label" style={{ color: "var(--good)" }}>
          Types check out — every assertion compiled 🎉
        </div>
      </div>
    );
  }

  const ok = report.status === "accepted";
  const failing = report.results.filter((r) => !r.passed);

  return (
    <div
      className="card"
      style={{ marginTop: 10, marginBottom: 0, borderColor: ok ? "var(--good)" : "var(--bad)" }}
    >
      <div className="io-label" style={{ color: ok ? "var(--good)" : "var(--bad)" }}>
        {ok
          ? `All ${report.total} tests passed 🎉`
          : `${report.passed} / ${report.total} tests passed`}
      </div>
      {!ok &&
        failing.slice(0, 3).map((r, i) => (
          <div key={i} style={{ marginTop: 6, fontSize: 12 }}>
            <div className="dim">{r.name}</div>
            <div style={{ fontFamily: "var(--font-mono)" }}>
              <div>
                input: <code>{r.input.replace(/\n/g, " ⏎ ") || "(none)"}</code>
              </div>
              <div>
                expected: <code>{r.expected}</code>
              </div>
              <div style={{ color: "var(--bad)" }}>
                got: <code>{r.timed_out ? "(timed out)" : r.actual || "(nothing)"}</code>
              </div>
              {r.stderr && (
                <pre style={{ margin: "4px 0 0", whiteSpace: "pre-wrap" }}>{r.stderr}</pre>
              )}
            </div>
          </div>
        ))}
    </div>
  );
}
