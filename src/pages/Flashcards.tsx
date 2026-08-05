import { useEffect, useState } from "react";
import { api } from "../api";
import type { Flashcard } from "../types";
import { Empty } from "../components/common";
import { useToast } from "../components/Toast";

const GRADES = [
  { q: 0, label: "Again", cls: "danger" },
  { q: 1, label: "Hard", cls: "" },
  { q: 2, label: "Good", cls: "success" },
  { q: 3, label: "Easy", cls: "primary" },
];

export default function Flashcards() {
  const [due, setDue] = useState<Flashcard[]>([]);
  const [all, setAll] = useState<Flashcard[]>([]);
  const [flipped, setFlipped] = useState(false);
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");
  const toast = useToast();

  const load = () => {
    api.dueFlashcards().then(setDue);
    api.listFlashcards().then(setAll);
  };
  useEffect(load, []);

  const current = due[0];

  const grade = async (q: number) => {
    if (!current) return;
    await api.gradeFlashcard(current.id, q);
    setFlipped(false);
    setDue((xs) => xs.slice(1));
    api.listFlashcards().then(setAll);
  };

  const add = async () => {
    if (!front.trim() || !back.trim()) return;
    await api.addFlashcard(front, back, "manual");
    setFront("");
    setBack("");
    toast("Card added");
    load();
  };

  const del = async (id: number) => {
    await api.deleteFlashcard(id);
    load();
  };

  return (
    <div className="page">
      <h1 className="page-title">Flashcards</h1>
      <p className="page-sub">
        Concept recall on the same SM-2 engine as problem reviews. {due.length} due.
      </p>

      {current ? (
        <div className="card" style={{ marginBottom: 16, minHeight: 160 }}>
          <div className="io-label">Front</div>
          <div style={{ fontSize: 18, margin: "6px 0 12px" }}>{current.front}</div>
          {flipped ? (
            <>
              <div className="io-label">Back</div>
              <div style={{ fontSize: 16, margin: "6px 0 12px" }}>{current.back}</div>
              <div className="row wrap">
                <span className="dim" style={{ fontSize: 12 }}>How well did you recall it?</span>
                <span className="spacer" />
                {GRADES.map((g) => (
                  <button key={g.q} className={g.cls} onClick={() => grade(g.q)}>
                    {g.label}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <button className="primary" onClick={() => setFlipped(true)}>
              Show answer
            </button>
          )}
        </div>
      ) : (
        <Empty icon="🃏" text="No cards due. Add some below or come back later." />
      )}

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>New card</h3>
        <input
          style={{ width: "100%", marginBottom: 8 }}
          placeholder="Front (question / prompt)"
          value={front}
          onChange={(e) => setFront(e.target.value)}
        />
        <textarea
          style={{ width: "100%" }}
          rows={2}
          placeholder="Back (answer)"
          value={back}
          onChange={(e) => setBack(e.target.value)}
        />
        <button className="primary" style={{ marginTop: 8 }} onClick={add}>
          + Add card
        </button>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>All cards ({all.length})</h3>
        {all.length === 0 && <div className="dim">No cards yet.</div>}
        {all.map((c) => (
          <div key={c.id} className="row" style={{ padding: "6px 0", borderBottom: "1px solid var(--border)" }}>
            <span>{c.front}</span>
            <span className="spacer" />
            <span className="dim" style={{ fontSize: 12 }}>due {c.due_date} · {c.interval_days}d</span>
            <button className="ghost danger" onClick={() => del(c.id)}>
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
