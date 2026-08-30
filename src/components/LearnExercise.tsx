// Shared, judge-backed exercise + quiz widgets for the Learn tab and the
// TypeScript course. Both surfaces render half-coded drills / coding challenges
// and grade them the *same* way — via `api.runTests(null, lang, code, cases)`,
// which uses the exact whitespace-normalized stdin/stdout judge (no harness).
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
  const [showHint, setShowHint] = useState(false);
  const [showSolution, setShowSolution] = useState(false);

  // Challenges are written from scratch, so give them a roomier editor than a
  // short fill-in-the-blank drill (whose starter already sizes it well).
  const height = Math.min(
    Math.max(exercise.starter.split("\n").length * 20 + 24, challenge ? 260 : 150),
    challenge ? 560 : 480
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
      const r = await api.runTests(null, lang, code, cases);
      setReport(r);
      if (r.status === "accepted") onSolved?.(exercise.id);
    } catch (e) {
      setErr(String(e));
    } finally {
      setRunning(false);
    }
  }

  const untouched = code === exercise.starter || code.includes("____");
  const solved = report?.status === "accepted";

  return (
    <div
      className="card"
      style={{
        marginBottom: 14,
        borderColor: solved
          ? "var(--good)"
          : challenge
          ? "var(--accent)"
          : undefined,
      }}
    >
      <div className="row" style={{ justifyContent: "space-between" }}>
        <strong>
          {index}. {exercise.title} {solved && <span style={{ color: "var(--good)" }}>✓</span>}
        </strong>
        <span className="row" style={{ gap: 6 }}>
          {challenge && exercise.difficulty && (
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
          {running ? "Checking…" : "Check"}
        </button>
        <button className="ghost" onClick={reset} disabled={running}>
          Reset
        </button>
        {exercise.hint && (
          <button className="ghost" onClick={() => setShowHint((s) => !s)}>
            {showHint ? "Hide hint" : "Hint"}
          </button>
        )}
        <button className="ghost" onClick={() => setShowSolution((s) => !s)}>
          {showSolution ? "Hide solution" : "Reveal solution"}
        </button>
        {untouched && !running && (
          <span className="dim" style={{ fontSize: 12, alignSelf: "center" }}>
            Replace the <code>____</code> before checking.
          </span>
        )}
      </div>

      {showHint && exercise.hint && (
        <div
          className="card"
          style={{ marginTop: 10, marginBottom: 0, background: "var(--accent-dim)" }}
        >
          <div className="io-label" style={{ color: "var(--accent)" }}>Hint</div>
          <p style={{ margin: 0 }}>{exercise.hint}</p>
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
