// The answer area of one quiz question, for every kind in lib/quizKinds.ts:
// the question's program (if any), then option buttons, multi-select toggles or
// a typed-type box. The weekly quiz, the mixed review sitting and the final
// exam all render through this, so a new kind lands in all three at once.
import { useState } from "react";
import { api } from "../api";
import type { QuizQuestion } from "../types";
import { Markdown } from "./Markdown";
import { inlineCode } from "./common";
import {
  isSelected,
  quizKind,
  toggleMulti,
  typeAnswerProgram,
  bannedIn,
} from "../lib/quizKinds";

export function QuizChoices({
  question,
  picked,
  revealed,
  onPick,
}: {
  question: QuizQuestion;
  /** -1, an option index, a multi-select pick or a type verdict — see quizKinds. */
  picked: number;
  /** Marked: show what was right and lock the answer. */
  revealed: boolean;
  onPick: (value: number) => void;
}) {
  const kind = quizKind(question);
  return (
    <>
      {question.code && <Markdown>{"```ts\n" + question.code.trimEnd() + "\n```"}</Markdown>}
      {kind === "type" ? (
        <TypeAnswer question={question} picked={picked} revealed={revealed} onPick={onPick} />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 10 }}>
          {kind === "multi" && !revealed && (
            <div className="dim quiz-note">Select every answer that is right — there is more than one.</div>
          )}
          {question.options.map((opt, oi) => {
            const chosen = kind === "multi" ? isSelected(picked, oi) : picked === oi;
            const right = kind === "multi" ? (question.answers ?? []).includes(oi) : oi === question.answer;
            let border: string | undefined;
            let color: string | undefined;
            if (revealed) {
              if (right) {
                border = "var(--good)";
                color = "var(--good)";
              } else if (chosen) {
                border = "var(--bad)";
                color = "var(--bad)";
              }
            } else if (chosen) {
              border = "var(--accent)";
              color = "var(--accent)";
            }
            return (
              <button
                key={oi}
                className="ghost"
                aria-pressed={kind === "multi" ? chosen : undefined}
                style={{
                  textAlign: "left",
                  borderColor: border,
                  borderStyle: revealed && right && !chosen && kind === "multi" ? "dashed" : undefined,
                  color,
                  padding: "8px 12px",
                  whiteSpace: "pre-wrap",
                  fontFamily: kind === "output" ? "var(--font-mono)" : undefined,
                  fontSize: kind === "output" ? 12.5 : undefined,
                }}
                onClick={() => onPick(kind === "multi" ? toggleMulti(picked, oi) : oi)}
                disabled={revealed}
              >
                {kind === "multi" && !revealed && (chosen ? "☑ " : "☐ ")}
                {revealed && right && "✓ "}
                {revealed && chosen && !right && "✗ "}
                {kind === "output" ? opt : inlineCode(opt)}
              </button>
            );
          })}
          {revealed && <WhyNot question={question} picked={picked} />}
        </div>
      )}
    </>
  );
}

/** X-37: why the options you chose are wrong, when the question says. */
function WhyNot({ question, picked }: { question: QuizQuestion; picked: number }) {
  const why = question.why_not ?? [];
  const chosen =
    quizKind(question) === "multi"
      ? question.options.map((_, i) => i).filter((i) => isSelected(picked, i) && !(question.answers ?? []).includes(i))
      : picked >= 0 && picked !== question.answer
        ? [picked]
        : [];
  const notes = chosen.filter((i) => why[i]).map((i) => ({ i, text: why[i]! }));
  if (notes.length === 0) return null;
  return (
    <div className="quiz-note" style={{ marginTop: 4 }}>
      {notes.map((n) => (
        <p key={n.i} style={{ margin: "2px 0", color: "var(--bad)" }}>
          Why not “{question.options[n.i]!.split("\n")[0]}”: <span style={{ color: "var(--text)" }}>{n.text}</span>
        </p>
      ))}
    </div>
  );
}

/** A typed answer, checked by the real type-checker against hidden claims. */
function TypeAnswer({
  question,
  picked,
  revealed,
  onPick,
}: {
  question: QuizQuestion;
  picked: number;
  revealed: boolean;
  onPick: (value: number) => void;
}) {
  const [typed, setTyped] = useState("");
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");

  async function check() {
    // The ban is on the answer, not the question's code (which may well use
    // `typeof` itself), so it is checked here rather than by the judge.
    const banned = bannedIn(typed);
    if (banned) {
      onPick(1);
      setError(`spell the type out — ${banned} is not allowed in the answer`);
      return;
    }
    setChecking(true);
    setError("");
    try {
      const r = await api.runTests(null, "typescript", typeAnswerProgram(question, typed), [], {
        judgeMode: "types",
        harness: question.harness ?? "",
        strictness: question.strictness || "strict",
      });
      onPick(r.status === "accepted" ? 0 : 1);
      if (r.status !== "accepted") setError(r.compile_error || r.status);
    } catch (e) {
      setError(String(e));
    } finally {
      setChecking(false);
    }
  }

  return (
    <div style={{ marginTop: 10 }}>
      <div className="row" style={{ gap: 8, alignItems: "center", flexWrap: "wrap" }}>
        <code style={{ whiteSpace: "nowrap" }}>type Answer =</code>
        <input
          value={typed}
          onChange={(e) => {
            setTyped(e.target.value);
            if (picked >= 0 && !revealed) onPick(-1);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && typed.trim() && !revealed) void check();
          }}
          disabled={revealed}
          placeholder="write the type out in full"
          spellCheck={false}
          style={{ flex: "1 1 180px", minWidth: 0, fontFamily: "var(--font-mono)" }}
          aria-label="Your answer, as a type"
        />
        <button
          className="ghost"
          style={{ whiteSpace: "nowrap" }}
          onClick={check}
          disabled={revealed || checking || !typed.trim()}
        >
          {checking ? "Checking…" : "Check type"}
        </button>
      </div>
      {picked === 0 && !revealed && (
        <p className="quiz-note" style={{ margin: "6px 0 0", color: "var(--good)" }}>
          ✓ The checker agrees.
        </p>
      )}
      {picked === 1 && !revealed && (
        <p className="quiz-note" style={{ margin: "6px 0 0", color: "var(--bad)" }}>
          ✗ Not that type — you can change it and check again before you submit.
          {error && <span className="dim"> ({error.split("\n")[0]})</span>}
        </p>
      )}
      {revealed && (
        <p className="quiz-note" style={{ margin: "6px 0 0" }}>
          Model answer: <code>{question.type_answer}</code>
        </p>
      )}
    </div>
  );
}
