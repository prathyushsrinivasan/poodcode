import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { Flashcard } from "../types";
import { Empty } from "../components/common";
import { Markdown } from "../components/Markdown";
import { useToast } from "../components/Toast";
import { GRADES, groupBySource, sourceLabel } from "../lib/flashcards";

/**
 * The flashcard deck — SM-2 scheduled in the backend (`grade_flashcard`), the
 * same engine as problem reviews.
 *
 * This page was removed in the UI overhaul, but the deck was not: completing a
 * Mastery week kept seeding cards into it, and the Mastery page kept promising
 * they were "in your review queue". Nothing showed them. This is that queue.
 *
 * Keyboard: Space / Enter shows the answer; 1–4 grade it.
 */
export default function Flashcards() {
  const [due, setDue] = useState<Flashcard[]>([]);
  const [all, setAll] = useState<Flashcard[]>([]);
  const [flipped, setFlipped] = useState(false);
  const [reviewed, setReviewed] = useState(0);
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");
  const [showAll, setShowAll] = useState(false);
  const toast = useToast();

  const load = useCallback(() => {
    api.dueFlashcards().then(setDue).catch(() => setDue([]));
    api.listFlashcards().then(setAll).catch(() => setAll([]));
  }, []);
  useEffect(load, [load]);

  const current = due[0];

  const grade = useCallback(
    async (quality: number) => {
      if (!current) return;
      try {
        await api.gradeFlashcard(current.id, quality);
      } catch {
        toast("Could not save that grade — try again");
        return;
      }
      setFlipped(false);
      setReviewed((n) => n + 1);
      // "Again" means the card is not learned yet: see it again this session.
      setDue((xs) => (quality === 0 ? [...xs.slice(1), xs[0]] : xs.slice(1)));
    },
    [current, toast]
  );

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA")) return;
      if (!current) return;
      if (!flipped && (e.key === " " || e.key === "Enter")) {
        e.preventDefault();
        setFlipped(true);
        return;
      }
      const g = flipped ? GRADES.find((x) => x.key === e.key) : undefined;
      if (g) {
        e.preventDefault();
        void grade(g.quality);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [current, flipped, grade]);

  const add = async () => {
    if (!front.trim() || !back.trim()) return;
    await api.addFlashcard(front.trim(), back.trim(), "manual");
    setFront("");
    setBack("");
    toast("Card added — it is due today");
    load();
  };

  const remove = async (id: number) => {
    await api.deleteFlashcard(id);
    load();
  };

  const groups = useMemo(() => groupBySource(all), [all]);

  return (
    <div className="page">
      <h1 className="page-title">Flashcards</h1>
      <p className="page-sub">
        {due.length === 0
          ? `Nothing due${reviewed ? ` — ${reviewed} reviewed this session` : ""}.`
          : `${due.length} due${reviewed ? ` · ${reviewed} reviewed this session` : ""}.`}{" "}
        Cards from finished Mastery weeks, quiz questions you missed, and your own — on the same
        spaced-repetition schedule as problem reviews.
      </p>

      {current ? (
        <div className="card flash-card">
          <div className="row flash-meta dim">
            <span>{sourceLabel(current.source)}</span>
            <span>
              {!current.reps ? "new" : `seen ${current.reps}×`}
              {current.lapses > 0 && ` · forgotten ${current.lapses}×`}
            </span>
          </div>
          <div className="flash-front">
            <Markdown>{current.front}</Markdown>
          </div>
          {flipped ? (
            <>
              <div className="flash-back">
                <Markdown>{current.back}</Markdown>
              </div>
              <div className="row flash-grades">
                <span className="dim">How well did you recall it?</span>
                <span className="spacer" />
                {GRADES.map((g) => (
                  <button
                    key={g.quality}
                    className={g.quality === 0 ? "danger" : g.quality === 2 ? "primary" : ""}
                    onClick={() => grade(g.quality)}
                  >
                    {g.label}
                    <kbd>{g.key}</kbd>
                  </button>
                ))}
              </div>
            </>
          ) : (
            <button className="primary" onClick={() => setFlipped(true)}>
              Show answer <kbd>Space</kbd>
            </button>
          )}
        </div>
      ) : (
        <Empty
          icon="🃏"
          text={
            all.length === 0
              ? "No cards yet. Finish a Mastery week, save the questions you miss on a quiz, or add your own below."
              : "Nothing due right now. Come back tomorrow — or add a card below."
          }
        />
      )}

      <div className="card flash-new">
        <h3>New card</h3>
        <input
          placeholder="Front — a question or prompt"
          value={front}
          onChange={(e) => setFront(e.target.value)}
        />
        <textarea
          rows={3}
          placeholder="Back — the answer (Markdown and `code` work)"
          value={back}
          onChange={(e) => setBack(e.target.value)}
        />
        <button className="primary" onClick={add} disabled={!front.trim() || !back.trim()}>
          + Add card
        </button>
      </div>

      <div className="card">
        <div className="row">
          <h3>All cards ({all.length})</h3>
          <span className="spacer" />
          {all.length > 0 && (
            <button className="ghost" onClick={() => setShowAll((v) => !v)}>
              {showAll ? "Hide" : "Show"}
            </button>
          )}
        </div>
        {showAll &&
          groups.map(([label, cards]) => (
            <details key={label}>
              <summary>
                {label} <span className="dim">({cards.length})</span>
              </summary>
              {cards.map((c) => (
                <div key={c.id} className="row flash-list-row">
                  <span>{c.front}</span>
                  <span className="spacer" />
                  <span className="dim flash-due">
                    due {c.due_date} · every {c.interval_days}d
                  </span>
                  <button className="ghost danger" onClick={() => remove(c.id)} aria-label="Delete card">
                    ✕
                  </button>
                </div>
              ))}
            </details>
          ))}
      </div>
    </div>
  );
}
