/**
 * Quiz questions, the same everywhere (UI_ROADMAP C4, G8).
 *
 * Learn, the courses, the Backend Lab, Projects and Mastery each drew a
 * question card: a `div.card` whose border went green or red, option buttons
 * coloured with inline styles, a "Correct" / "Not quite" panel. Learn's copy
 * did not shuffle the options, so the right answer — authors write it first —
 * sat on the top button every time. One card now, one option button, one
 * explanation panel.
 */

import { useEffect, useMemo, useState, type ReactNode } from "react";
import type { QuizQuestion } from "../../types";
import { optionOrder } from "../../lib/quizShuffle";
import { Icon } from "../ui/Icon";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Card";
import { VerdictPanel } from "./Verdict";
import { inlineCode } from "../common";

export type OptionState = "idle" | "chosen" | "right" | "wrong" | "missed";

/**
 * One answer button. `missed` is a right answer the learner did not pick in a
 * multi-select question — dashed, so it reads as "this too" rather than as
 * something they chose.
 */
export function QuizOption({
  state,
  onClick,
  disabled,
  mono = false,
  pressed,
  children,
}: {
  state: OptionState;
  onClick: () => void;
  disabled?: boolean;
  /** Program output options, which must keep their spacing. */
  mono?: boolean;
  /** Set for multi-select toggles. */
  pressed?: boolean;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      className={`quiz-option is-${state} ${mono ? "is-mono" : ""}`}
      aria-pressed={pressed}
      onClick={onClick}
      disabled={disabled}
    >
      {(state === "right" || state === "missed") && <Icon name="check" size={14} label="Right answer" />}
      {state === "wrong" && <Icon name="close" size={14} label="Your answer, wrong" />}
      <span className="quiz-option-text">{children}</span>
    </button>
  );
}

/** The frame of a question: number, text, the answer area, and the verdict once revealed. */
export function QuizCard({
  index,
  question,
  revealed,
  right,
  explanation,
  children,
}: {
  index: number;
  question: ReactNode;
  revealed: boolean;
  right: boolean;
  explanation?: ReactNode;
  children: ReactNode;
}) {
  return (
    <article className={`card quiz-card ${revealed ? (right ? "is-right" : "is-wrong") : ""}`}>
      <h4 className="quiz-question">
        <span className="exercise-index">{index}.</span> {question}
      </h4>
      {children}
      {revealed && (
        <VerdictPanel tone={right ? "good" : "bad"} title={right ? "Correct" : "Not quite"}>
          {explanation && <p className="verdict-para">{explanation}</p>}
        </VerdictPanel>
      )}
    </article>
  );
}

/** A single-answer question, answered by clicking an option. Options are
 * shown in a shuffled order (lib/quizShuffle.ts); `picked` holds the AUTHORED
 * index, so grading is unchanged. */
export function QuizItem({
  index,
  question,
  picked,
  onPick,
  salt = "",
}: {
  index: number;
  question: QuizQuestion;
  /** The AUTHORED index of the option chosen, or -1. */
  picked: number;
  onPick: (optionIndex: number) => void;
  /** Varies the display order; the review drill passes its round number. */
  salt?: string;
}) {
  const answered = picked >= 0;
  const isRight = picked === question.answer;
  const order = useMemo(
    () => optionOrder(question.question, question.options.length, salt),
    [question.question, question.options.length, salt]
  );

  return (
    <QuizCard index={index} question={inlineCode(question.question)} revealed={answered} right={isRight} explanation={question.explanation}>
      <div className="quiz-options">
        {order.map((oi) => (
          <QuizOption
            key={oi}
            state={!answered ? "idle" : oi === question.answer ? "right" : oi === picked ? "wrong" : "idle"}
            onClick={() => onPick(oi)}
            disabled={answered}
          >
            {inlineCode(question.options[oi])}
          </QuizOption>
        ))}
      </div>
    </QuizCard>
  );
}

/**
 * A self-check quiz: every question, a running score, and a reset. Graded on
 * the client by comparing the picked option index — no code execution. The
 * first answer to each question is locked in.
 */
export function QuizSection({
  questions,
  onScore,
}: {
  questions: QuizQuestion[];
  /** Reports how many are currently right, so a page can decide whether a
   * chapter has been passed rather than merely read. */
  onScore?: (correct: number) => void;
}) {
  // picked[i] = the option index chosen for question i, or -1 if unanswered.
  const [picked, setPicked] = useState<number[]>(() => questions.map(() => -1));

  const answered = picked.filter((p) => p >= 0).length;
  const correct = picked.filter((p, i) => p === questions[i].answer).length;

  useEffect(() => {
    onScore?.(correct);
  }, [correct, onScore]);

  return (
    <div className="quiz-section">
      {answered > 0 && (
        <div className="quiz-score" role="status">
          <Badge tone={correct === questions.length ? "good" : "accent"}>
            Score {correct}/{questions.length}
          </Badge>
          <span className="exercise-note">
            {answered}/{questions.length} answered
          </span>
          <Button variant="ghost" size="sm" icon="reset" onClick={() => setPicked(questions.map(() => -1))}>
            Reset
          </Button>
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
