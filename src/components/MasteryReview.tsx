// Review for weeks behind you (TS_MASTERY_ROADMAP X-55, X-54) and the
// monthly checkpoint quizzes (X-35): short mixed sittings drawn from several
// weeks' question banks. Nothing here gates anything.

import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { MasteryWeek } from "../types";
import { inlineCode } from "./common";
import { QuizChoices } from "./QuizChoices";
import { QuizCard } from "./exercise/Quiz";
import { answerText, questionText } from "../lib/quizKinds";
import { drawFinalPaper } from "../lib/finalExam";
import { WEEK_BUDGET_HOURS, type ChapterStat, type WeekProgress } from "../lib/mastery";
import { useToast } from "./Toast";
import { recordSitting } from "../lib/quizStats";

/** A fresh mixed paper on demand: `size` questions drawn round-robin from the
 * banks of `weeks`, marked on submit, misses savable as flashcards. */
export function MixedQuiz({
  weeks,
  size,
  source,
  startLabel,
  passMark = 80,
}: {
  weeks: MasteryWeek[];
  size: number;
  /** Where saved flashcards say they came from. */
  source: string;
  startLabel: string;
  /** Percentage shown as a pass (nothing is gated on it). */
  passMark?: number;
}) {
  const toast = useToast();
  const [seed, setSeed] = useState<number | null>(null);
  const [picked, setPicked] = useState<number[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const [saved, setSaved] = useState(false);
  const paper = useMemo(() => (seed === null ? [] : drawFinalPaper(weeks, size, seed)), [seed, weeks, size]);

  const correct = paper.filter((q, i) => picked[i] === q.answer).length;
  const missed = submitted ? paper.filter((q, i) => picked[i] !== q.answer) : [];
  const percent = paper.length ? Math.round((correct / paper.length) * 100) : 0;

  function start() {
    const s = (Date.now() ^ Math.floor(Math.random() * 0x7fffffff)) >>> 0;
    setSeed(s);
    setPicked(Array.from({ length: size }, () => -1));
    setSubmitted(false);
    setSaved(false);
  }

  async function saveMisses() {
    try {
      const existing = new Set((await api.listFlashcards()).map((c) => c.front));
      let added = 0;
      for (const q of missed) {
        if (existing.has(questionText(q))) continue;
        await api.addFlashcard(questionText(q), `${answerText(q)}\n\n${q.explanation}`, source);
        added++;
      }
      setSaved(true);
      toast(added ? `Added ${added} card${added === 1 ? "" : "s"} to Flashcards` : "Already in your Flashcards");
    } catch {
      toast("Could not save those flashcards — try again");
    }
  }

  if (seed === null) return <button onClick={start}>{startLabel}</button>;

  return (
    <>
      {paper.map((q, i) => {
        const right = picked[i] === q.answer;
        return (
          <QuizCard
            key={i}
            index={i + 1}
            question={inlineCode(q.question)}
            revealed={submitted}
            right={right}
            explanation={q.explanation}
          >
            <QuizChoices
              question={q}
              picked={picked[i] ?? -1}
              revealed={submitted}
              onPick={(v) => setPicked((prev) => prev.map((p, k) => (k === i ? v : p)))}
            />
          </QuizCard>
        );
      })}
      <div className="row" style={{ gap: 8, alignItems: "center" }}>
        {!submitted ? (
          <>
            <button
              onClick={() => {
                setSubmitted(true);
                recordSitting(paper.map((q, i) => ({ question: q.question, right: picked[i] === q.answer })));
              }}
              disabled={picked.some((p) => p < 0)}
            >
              Check my answers
            </button>
            <span className="dim quiz-note">
              {picked.filter((p) => p >= 0).length}/{paper.length} answered
            </span>
          </>
        ) : (
          <>
            <strong style={{ color: percent >= passMark ? "var(--good)" : "var(--bad)" }}>
              {correct}/{paper.length} ({percent}%)
            </strong>
            <button className="ghost" onClick={start}>
              Another sitting
            </button>
            {missed.length > 0 && !saved && (
              <button className="ghost" onClick={saveMisses}>
                Save {missed.length} miss{missed.length === 1 ? "" : "es"} as flashcards
              </button>
            )}
          </>
        )}
      </div>
    </>
  );
}

export function ReviewSession({
  trackTitle,
  weeks,
  perWeek,
  onOpenWeek,
  weakChapters = [],
}: {
  trackTitle: string;
  /** Core weeks, in order. */
  weeks: MasteryWeek[];
  perWeek: WeekProgress[];
  onOpenWeek: (week: number) => void;
  /** Chapters with a low first-try rate (X-54). */
  weakChapters?: ChapterStat[];
}) {
  const completed = useMemo(() => weeks.filter((_, i) => perWeek[i]?.complete), [weeks, perWeek]);

  // The weeks you found hardest — a low best quiz score, or twice the budget.
  const revisit = weeks
    .map((w, i) => ({ w, p: perWeek[i] }))
    .filter(
      (x): x is { w: MasteryWeek; p: WeekProgress } =>
        !!x.p && x.p.complete && ((x.p.score ?? 100) < 85 || x.p.studySeconds > 2 * WEEK_BUDGET_HOURS * 3600)
    )
    .sort((a, b) => (a.p.score ?? 0) - (b.p.score ?? 0))
    .slice(0, 4);

  if (completed.length < 2) return null;

  return (
    <details className="card mastery-practice" style={{ marginBottom: 18 }}>
      <summary>
        <strong>🔁 Review the weeks behind you</strong>{" "}
        <span className="dim quiz-note">
          a 10-question mixed sitting from {completed.length} finished weeks
          {revisit.length + weakChapters.length > 0 && ` · ${revisit.length + weakChapters.length} worth revisiting`}
        </span>
      </summary>

      {revisit.length > 0 && (
        <p className="quiz-note" style={{ marginBottom: 6 }}>
          Worth revisiting:{" "}
          {revisit.map((x, i) => (
            <span key={x.w.week}>
              {i > 0 && " · "}
              <button className="linklike" onClick={() => onOpenWeek(x.w.week)}>
                Week {x.w.week} ({x.w.title})
              </button>{" "}
              <span className="dim">best quiz {x.p.score ?? 0}%</span>
            </span>
          ))}
        </p>
      )}

      {weakChapters.length > 0 && (
        <p className="quiz-note" style={{ marginBottom: 6 }}>
          Chapters where most exercises needed more than one try:{" "}
          {weakChapters.slice(0, 5).map((c, i) => (
            <span key={c.key}>
              {i > 0 && " · "}
              <Link to={`/learn/${c.key}`}>{c.name}</Link>{" "}
              <span className="dim">
                {c.firstTry}/{c.attempted} first try
              </span>
            </span>
          ))}
        </p>
      )}

      <MixedQuiz weeks={completed} size={10} source={`${trackTitle} · review`} startLabel="Start a review sitting" />
    </details>
  );
}
