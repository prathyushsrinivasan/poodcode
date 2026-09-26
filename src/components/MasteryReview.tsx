// Review for weeks behind you (TS_MASTERY_ROADMAP X-55, X-54): a short mixed
// sitting drawn from every completed week's question bank, and the weeks most
// worth revisiting. Nothing here gates anything.

import { useMemo, useState } from "react";
import { api } from "../api";
import type { MasteryWeek } from "../types";
import { inlineCode } from "./common";
import { drawFinalPaper } from "../lib/finalExam";
import { WEEK_BUDGET_HOURS, type WeekProgress } from "../lib/mastery";
import { useToast } from "./Toast";

const SIZE = 10;

export function ReviewSession({
  trackTitle,
  weeks,
  perWeek,
  onOpenWeek,
}: {
  trackTitle: string;
  /** Core weeks, in order. */
  weeks: MasteryWeek[];
  perWeek: WeekProgress[];
  onOpenWeek: (week: number) => void;
}) {
  const toast = useToast();
  const completed = weeks.filter((_, i) => perWeek[i]?.complete);
  const [seed, setSeed] = useState<number | null>(null);
  const [picked, setPicked] = useState<number[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const [saved, setSaved] = useState(false);
  const paper = useMemo(() => (seed === null ? [] : drawFinalPaper(completed, SIZE, seed)), [seed, completed]);

  // X-54: the weeks you found hardest — a low best quiz score, or twice the
  // time budget.
  const revisit = weeks
    .map((w, i) => ({ w, p: perWeek[i] }))
    .filter(
      (x): x is { w: MasteryWeek; p: WeekProgress } =>
        !!x.p && x.p.complete && ((x.p.score ?? 100) < 85 || x.p.studySeconds > 2 * WEEK_BUDGET_HOURS * 3600)
    )
    .sort((a, b) => (a.p.score ?? 0) - (b.p.score ?? 0))
    .slice(0, 4);

  if (completed.length < 2) return null;

  const correct = paper.filter((q, i) => picked[i] === q.answer).length;
  const missed = submitted ? paper.filter((q, i) => picked[i] !== q.answer) : [];

  function start() {
    const s = (Date.now() ^ Math.floor(Math.random() * 0x7fffffff)) >>> 0;
    setSeed(s);
    setPicked(Array.from({ length: SIZE }, () => -1));
    setSubmitted(false);
    setSaved(false);
  }

  async function saveMisses() {
    try {
      const existing = new Set((await api.listFlashcards()).map((c) => c.front));
      let added = 0;
      for (const q of missed) {
        if (existing.has(q.question)) continue;
        await api.addFlashcard(q.question, `${q.options[q.answer]}\n\n${q.explanation}`, `${trackTitle} · review`);
        added++;
      }
      setSaved(true);
      toast(added ? `Added ${added} card${added === 1 ? "" : "s"} to Flashcards` : "Already in your Flashcards");
    } catch {
      toast("Could not save those flashcards — try again");
    }
  }

  return (
    <details className="card mastery-practice" style={{ marginBottom: 18 }}>
      <summary>
        <strong>🔁 Review the weeks behind you</strong>{" "}
        <span className="dim quiz-note">
          a {SIZE}-question mixed sitting from {completed.length} finished weeks
          {revisit.length > 0 && ` · ${revisit.length} worth revisiting`}
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

      {seed === null ? (
        <button onClick={start}>Start a review sitting</button>
      ) : (
        <>
          {paper.map((q, i) => {
            const right = picked[i] === q.answer;
            return (
              <div
                key={i}
                className="card"
                style={{
                  marginBottom: 8,
                  borderColor: submitted ? (right ? "var(--good)" : "var(--bad)") : undefined,
                }}
              >
                <strong>
                  {i + 1}. {inlineCode(q.question)}
                </strong>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 8 }}>
                  {q.options.map((opt, oi) => {
                    const chosen = picked[i] === oi;
                    const color = submitted
                      ? oi === q.answer
                        ? "var(--good)"
                        : chosen
                          ? "var(--bad)"
                          : undefined
                      : chosen
                        ? "var(--accent)"
                        : undefined;
                    return (
                      <button
                        key={oi}
                        className="ghost"
                        disabled={submitted}
                        style={{ textAlign: "left", padding: "6px 12px", borderColor: color, color }}
                        onClick={() => setPicked(picked.map((p, k) => (k === i ? oi : p)))}
                      >
                        {inlineCode(opt)}
                      </button>
                    );
                  })}
                </div>
                {submitted && <p className="dim quiz-note" style={{ marginBottom: 0 }}>{q.explanation}</p>}
              </div>
            );
          })}
          <div className="row" style={{ gap: 8, alignItems: "center" }}>
            {!submitted ? (
              <button onClick={() => setSubmitted(true)} disabled={picked.some((p) => p < 0)}>
                Check my answers
              </button>
            ) : (
              <>
                <strong style={{ color: correct >= paper.length * 0.8 ? "var(--good)" : "var(--bad)" }}>
                  {correct}/{paper.length}
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
      )}
    </details>
  );
}
