/**
 * The interactive pieces of a NEW_DSA topic page (src/pages/NewDsaTopic.tsx):
 * a question that can be retried, a graded sitting, the window stepper, the
 * four-layer hint ladder and the guided-practice walk.
 *
 * Questions reuse `QuizChoices` (every quiz kind, including multi-select) and
 * `lib/quizShuffle` — the seed lists the right option first, and without the
 * shuffle it would sit on the top button every time.
 */

import { useEffect, useMemo, useState, type ReactNode } from "react";
import type { Exercise, NdEdgeTest, NdGuided, NdHint, NdStepper, QuizQuestion } from "../../types";
import { Markdown, InlineMarkdown } from "../Markdown";
import { QuizChoices } from "../QuizChoices";
import { ExerciseCard } from "../exercise";
import { VerdictPanel } from "../exercise/Verdict";
import { Button, Badge, Icon, ScrollX } from "../ui";
import { optionOrder } from "../../lib/quizShuffle";
import { expectedPick, quizKind, reorderOptions } from "../../lib/quizKinds";
import { sittingScore } from "../../lib/newDsa";

export function Code({ code, lang = "ts" }: { code: string; lang?: string }) {
  return <Markdown>{"```" + lang + "\n" + code.trimEnd() + "\n```"}</Markdown>;
}

/** A question with its options in a stable shuffled order. */
function useShuffled(q: QuizQuestion, salt = ""): QuizQuestion {
  return useMemo(() => {
    const order = optionOrder(q.question, q.options.length, salt);
    return reorderOptions(q, order.map((i) => q.options[i]!));
  }, [q, salt]);
}

// ---- One question -----------------------------------------------------------

/**
 * A learning question: answer, see why, and try again if it was wrong. A
 * single-choice question is marked on the click; a multi-select one on
 * "Check". `onCorrect` fires on a right answer, which the page records.
 */
export function QuestionCard({
  index,
  question,
  done = false,
  onCorrect,
  onAnswered,
}: {
  index: number | string;
  question: QuizQuestion;
  /** Already answered right in an earlier visit. */
  done?: boolean;
  onCorrect?: () => void;
  /** Any answer at all — the guided walk moves on either way. */
  onAnswered?: (right: boolean) => void;
}) {
  const [attempt, setAttempt] = useState(0);
  const q = useShuffled(question, attempt ? String(attempt) : "");
  const [picked, setPicked] = useState(-1);
  const [revealed, setRevealed] = useState(false);
  const multi = quizKind(q) === "multi";
  const right = picked === expectedPick(q);

  function reveal(value: number) {
    setRevealed(true);
    const ok = value === expectedPick(q);
    if (ok) onCorrect?.();
    onAnswered?.(ok);
  }

  function pick(value: number) {
    if (revealed) return;
    setPicked(value);
    if (!multi && value >= 0) reveal(value);
  }

  function retry() {
    setAttempt((a) => a + 1);
    setPicked(-1);
    setRevealed(false);
  }

  return (
    <article className={`card quiz-card ndsa-question ${revealed ? (right ? "is-right" : "is-wrong") : ""}`}>
      <div className="quiz-question ndsa-question-head">
        <span className="exercise-index">{index}.</span>
        <span className="ndsa-question-text">
          <InlineMarkdown>{q.question}</InlineMarkdown>
        </span>
        {done && !revealed && (
          <Badge tone="good" icon="check">
            answered
          </Badge>
        )}
      </div>
      <QuizChoices question={q} picked={picked} revealed={revealed} onPick={pick} />
      {multi && !revealed && (
        <div className="cur-actions mt-2">
          <Button variant="primary" icon="check" onClick={() => reveal(picked)} disabled={picked < 0}>
            Check
          </Button>
        </div>
      )}
      {revealed && (
        <VerdictPanel tone={right ? "good" : "bad"} title={right ? "Correct" : "Not quite"}>
          <Markdown>{q.explanation}</Markdown>
          {!right && (
            <Button variant="ghost" icon="reset" onClick={retry}>
              Try again
            </Button>
          )}
        </VerdictPanel>
      )}
    </article>
  );
}

// ---- A graded sitting ---------------------------------------------------------

/**
 * A test rather than a lesson: answer every question, then submit. The right
 * answers are shown only once you pass. A failed sitting says which questions
 * were wrong, never what the right option was, so a retake is still a test.
 */
export function Sitting({
  title,
  questions,
  pass,
  passed,
  onPass,
}: {
  title: string;
  questions: QuizQuestion[];
  pass: number;
  passed: boolean;
  onPass: () => void;
}) {
  const [round, setRound] = useState(0);
  const shuffled = useMemo(
    () =>
      questions.map((q) => {
        const order = optionOrder(q.question, q.options.length, `sitting-${round}`);
        return reorderOptions(q, order.map((i) => q.options[i]!));
      }),
    [questions, round]
  );
  const [picks, setPicks] = useState<number[]>(() => questions.map(() => -1));
  const [submitted, setSubmitted] = useState(false);
  const expected = shuffled.map(expectedPick);
  const score = sittingScore(picks, expected);
  const ok = submitted && score >= pass;
  const answered = picks.every((p) => p >= 0);

  function submit() {
    setSubmitted(true);
    if (sittingScore(picks, expected) >= pass) onPass();
  }

  function retake() {
    setRound((r) => r + 1);
    setPicks(questions.map(() => -1));
    setSubmitted(false);
  }

  return (
    <div className="ndsa-sitting">
      <div className="row items-baseline">
        <strong>{title}</strong>
        <span className="spacer" />
        {passed && !submitted ? (
          <Badge tone="good" icon="check">
            passed
          </Badge>
        ) : (
          <span className="dim text-xs">
            Pass mark: {pass} of {questions.length}
          </span>
        )}
      </div>
      {shuffled.map((q, i) => {
        const wrong = submitted && picks[i] !== expected[i];
        return (
          <article
            key={q.question}
            className={`card quiz-card ndsa-question ${submitted ? (ok ? (wrong ? "is-wrong" : "is-right") : wrong ? "is-wrong" : "") : ""}`}
          >
            <div className="quiz-question ndsa-question-head">
              <span className="exercise-index">{i + 1}.</span>
              <span className="ndsa-question-text">
                <InlineMarkdown>{q.question}</InlineMarkdown>
              </span>
              {submitted && !ok && (
                <Badge tone={wrong ? "bad" : "good"} icon={wrong ? "close" : "check"}>
                  {wrong ? "wrong" : "right"}
                </Badge>
              )}
            </div>
            <QuizChoices
              question={q}
              picked={picks[i]!}
              revealed={ok}
              onPick={(v) => {
                if (submitted) return;
                setPicks((ps) => ps.map((p, j) => (j === i ? v : p)));
              }}
            />
            {ok && (
              <div className="ndsa-sitting-why">
                <Markdown>{q.explanation}</Markdown>
              </div>
            )}
          </article>
        );
      })}
      {!submitted ? (
        <div className="cur-actions">
          <Button variant="primary" icon="submit" onClick={submit} disabled={!answered}>
            Submit
          </Button>
          {!answered && <span className="dim text-xs">Answer every question to submit.</span>}
        </div>
      ) : ok ? (
        <VerdictPanel tone="good" title={`Passed: ${score} / ${questions.length}`}>
          <p className="verdict-para">The answers and explanations are shown above.</p>
        </VerdictPanel>
      ) : (
        <VerdictPanel tone="bad" title={`${score} / ${questions.length}: below the pass mark of ${pass}`}>
          <p className="verdict-para">
            The questions marked wrong are flagged, but not their answers. Go back over the sections they come from, then
            retake it. The options will be in a new order.
          </p>
          <Button icon="reset" onClick={retake}>
            Retake
          </Button>
        </VerdictPanel>
      )}
    </div>
  );
}

// ---- The window stepper --------------------------------------------------------

const ACTION_TONE: Record<string, "accent" | "good" | "bad" | "warn" | "neutral"> = {
  absorb: "accent",
  release: "warn",
  measure: "good",
  done: "good",
};

/** Step through a window run frame by frame: where lo and hi are, what the
 * summary holds, and the sentence explaining the move. */
export function WindowStepper({ stepper }: { stepper: NdStepper }) {
  const [i, setI] = useState(0);
  const last = stepper.frames.length - 1;
  const f = stepper.frames[Math.min(i, last)]!;
  const go = (n: number) => setI(Math.max(0, Math.min(last, n)));

  return (
    <div
      className="ndsa-stepper"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "ArrowRight") go(i + 1);
        if (e.key === "ArrowLeft") go(i - 1);
      }}
      aria-label={`${stepper.title}. Use the left and right arrow keys to step.`}
    >
      <div className="row items-baseline">
        <strong>{stepper.title}</strong>
        <span className="spacer" />
        <code>{stepper.input_label}</code>
      </div>
      <div className="ndsa-cells" role="img" aria-label={`Window from ${f.lo} to ${f.hi}`}>
        {stepper.cells.map((c, idx) => {
          const inside = f.hi >= 0 && idx >= f.lo && idx <= f.hi;
          return (
            <div key={idx} className={`ndsa-cell ${inside ? "in" : ""} ${idx === f.hi ? "is-hi" : ""}`}>
              <span className="ndsa-cell-val">{c}</span>
              <span className="ndsa-cell-idx">{idx}</span>
              <span className="ndsa-cell-ptr">
                {idx === f.lo && f.hi >= f.lo ? "lo" : ""}
                {idx === f.lo && idx === f.hi ? " " : ""}
                {idx === f.hi ? "hi" : ""}
              </span>
            </div>
          );
        })}
      </div>
      <div className="ndsa-stepper-state">
        <Badge tone={ACTION_TONE[f.action] ?? "neutral"}>{f.action}</Badge>
        <span>
          {stepper.state_label}: <code>{f.state}</code>
        </span>
        <span>
          best: <strong>{f.best}</strong>
        </span>
      </div>
      <p className="ndsa-stepper-note">{f.note}</p>
      <div className="cur-actions">
        <Button size="sm" icon="chevronLeft" onClick={() => go(i - 1)} disabled={i === 0}>
          Back
        </Button>
        <Button size="sm" variant="primary" iconRight="chevronRight" onClick={() => go(i + 1)} disabled={i === last}>
          Step
        </Button>
        <Button size="sm" variant="ghost" icon="reset" onClick={() => go(0)} disabled={i === 0}>
          Restart
        </Button>
        <input
          type="range"
          min={0}
          max={last}
          value={i}
          onChange={(e) => go(Number(e.target.value))}
          aria-label="Frame"
          className="ndsa-stepper-range"
        />
        <span className="dim text-xs">
          {i + 1} / {last + 1}
        </span>
      </div>
    </div>
  );
}

// ---- Layered hints -------------------------------------------------------------

/** Nudge → Approach → Steps → Code, one at a time, each only on request. */
export function LayeredHints({ hints }: { hints: NdHint[] }) {
  const [shown, setShown] = useState(0);
  const next = hints[shown];
  return (
    <div className="ndsa-hints">
      {hints.slice(0, shown).map((h, i) => (
        <div key={h.label} className="ndsa-hint">
          <span className="ndsa-hint-label">
            Hint {i + 1} · {h.label}
          </span>
          <InlineMarkdown>{h.text}</InlineMarkdown>
        </div>
      ))}
      {next && (
        <Button variant="ghost" size="sm" icon="hint" onClick={() => setShown((n) => n + 1)}>
          Show hint {shown + 1}: {next.label.toLowerCase()}
        </Button>
      )}
    </div>
  );
}

// ---- Guided practice ------------------------------------------------------------

const GUIDED_STEPS = ["Understand", "Identify", "Choose an approach", "Pseudocode", "Implement", "Test"] as const;

function readReached(key: string): number {
  try {
    return Number(localStorage.getItem(key) ?? "0") || 0;
  } catch {
    return 0;
  }
}

/**
 * One guided problem, walked in the template's order: understand the I/O →
 * identify the concept → choose the approach → pseudocode → implement → test.
 * Each step opens when the one before it has been answered, and how far you
 * got is remembered on this device. A solved problem opens every step.
 */
export function GuidedFlow({
  topicKey,
  guided,
  index,
  solved,
  onSolved,
}: {
  topicKey: string;
  guided: NdGuided;
  index: number;
  solved: boolean;
  onSolved: (id: string) => void;
}) {
  const storeKey = `poodcode:ndsa-guided:${topicKey}:${guided.key}`;
  const [reached, setReached] = useState(() => (solved ? GUIDED_STEPS.length - 1 : readReached(storeKey)));
  const [draft, setDraft] = useState(() => {
    try {
      return localStorage.getItem(`${storeKey}:pseudo`) ?? "";
    } catch {
      return "";
    }
  });
  const [showModel, setShowModel] = useState(false);

  useEffect(() => {
    try {
      localStorage.setItem(storeKey, String(reached));
    } catch {
      /* a convenience only */
    }
  }, [storeKey, reached]);

  const open = (step: number) => setReached((r) => Math.max(r, step));
  const at = solved ? GUIDED_STEPS.length - 1 : reached;

  const step = (n: number, body: ReactNode) =>
    n <= at && (
      <section className="ndsa-guided-step" key={n}>
        <div className="ndsa-guided-step-head">
          <span className={`cur-num ${n < at ? "complete" : "started"}`}>{n < at ? <Icon name="check" size={14} /> : n + 1}</span>
          <strong>{GUIDED_STEPS[n]}</strong>
        </div>
        <div className="ndsa-guided-step-body">{body}</div>
      </section>
    );

  return (
    <div className="cur-panel ndsa-guided">
      <div className="row items-baseline">
        <h3 className="ndsa-h3">
          Problem {index}: {guided.title}
        </h3>
        <span className="spacer" />
        {solved && (
          <Badge tone="good" icon="check">
            solved
          </Badge>
        )}
      </div>
      <Markdown>{guided.problem}</Markdown>

      {step(
        0,
        <>
          <ExamplesTable examples={guided.examples} />
          <QuestionCard index="Check" question={guided.understand} onAnswered={() => open(1)} />
        </>
      )}
      {step(1, <QuestionCard index="?" question={guided.identify} onAnswered={() => open(2)} />)}
      {step(2, <QuestionCard index="?" question={guided.approach} onAnswered={() => open(3)} />)}
      {step(
        3,
        <>
          <p className="dim mt-0">
            Write the steps in your own words first: plain English is fine. Then compare with the model.
          </p>
          <textarea
            className="ndsa-pseudo"
            value={draft}
            placeholder={"for each position…\n    …"}
            onChange={(e) => {
              setDraft(e.target.value);
              try {
                localStorage.setItem(`${storeKey}:pseudo`, e.target.value);
              } catch {
                /* the draft is a convenience */
              }
            }}
            aria-label="Your pseudocode"
          />
          <div className="cur-actions">
            <Button
              icon={showModel ? "hide" : "compare"}
              onClick={() => {
                setShowModel((s) => !s);
                open(4);
              }}
            >
              {showModel ? "Hide the model pseudocode" : "Compare with the model pseudocode"}
            </Button>
          </div>
          {showModel && <Code code={guided.pseudocode} lang="text" />}
        </>
      )}
      {step(
        4,
        <>
          <LayeredHints hints={guided.hints} />
          <ExerciseCard
            index={index}
            exercise={guided.exercise}
            challenge
            onSolved={(id) => {
              onSolved(id);
              open(5);
            }}
          />
          {!solved && at === 4 && (
            <Button variant="ghost" size="sm" onClick={() => open(5)}>
              Show the edge cases to test →
            </Button>
          )}
        </>
      )}
      {step(5, <EdgeTests tests={guided.tests} />)}
    </div>
  );
}

function ExamplesTable({ examples }: { examples: NdGuided["examples"] }) {
  return (
    <ScrollX label="Examples">
      <table className="ndsa-table">
        <thead>
          <tr>
            <th>Input</th>
            <th>Output</th>
            <th>Why</th>
          </tr>
        </thead>
        <tbody>
          {examples.map((e) => (
            <tr key={e.input}>
              <td>
                <code>{e.input}</code>
              </td>
              <td>
                <code>{e.output}</code>
              </td>
              <td className="dim">{e.note}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ScrollX>
  );
}

function EdgeTests({ tests }: { tests: NdEdgeTest[] }) {
  return (
    <>
      <p className="dim mt-0">
        Before trusting a solution, run these in your head against your code. All of them are among the hidden checks.
      </p>
      <ScrollX label="Edge cases">
        <table className="ndsa-table">
          <thead>
            <tr>
              <th>Case</th>
              <th>Input</th>
              <th>Expected</th>
              <th>What it catches</th>
            </tr>
          </thead>
          <tbody>
            {tests.map((t) => (
              <tr key={t.case}>
                <td>{t.case}</td>
                <td>
                  <code>{t.input}</code>
                </td>
                <td>
                  <code>{t.expected}</code>
                </td>
                <td>
                  <InlineMarkdown>{t.why}</InlineMarkdown>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </ScrollX>
    </>
  );
}

/** An exercise card that reports the solve to the page. */
export function TrackedExercise({
  index,
  exercise,
  onSolved,
  challenge = false,
}: {
  index: number;
  exercise: Exercise;
  onSolved: (id: string) => void;
  challenge?: boolean;
}) {
  return <ExerciseCard index={index} exercise={exercise} onSolved={onSolved} challenge={challenge} />;
}
