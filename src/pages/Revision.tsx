import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { ReviewItem } from "../types";
import { DiffBadge, Empty } from "../components/common";
import { useToast } from "../components/Toast";

// 0..3 → Again / Hard / Good / Easy (SM-2 quality grades).
const GRADES: { q: number; label: string; cls: string; hint: string }[] = [
  { q: 0, label: "Again", cls: "danger", hint: "Blanked — relearn tomorrow" },
  { q: 1, label: "Hard", cls: "", hint: "Got it, but a struggle" },
  { q: 2, label: "Good", cls: "success", hint: "Solid recall" },
  { q: 3, label: "Easy", cls: "primary", hint: "Instant" },
];

export default function Revision({ onChange }: { onChange?: () => void }) {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const nav = useNavigate();
  const toast = useToast();

  const load = () => api.dueReviews().then(setItems);
  useEffect(() => {
    load();
  }, []);

  const grade = async (it: ReviewItem, quality: number) => {
    await api.gradeReview(it.problem_id, quality);
    setItems((xs) => xs.filter((x) => x.problem_id !== it.problem_id));
    onChange?.();
    toast(quality === 0 ? "Reset — due tomorrow" : "Scheduled further out 👍");
  };

  const reschedule = async (it: ReviewItem, days: number) => {
    const d = new Date();
    d.setDate(d.getDate() + days);
    await api.rescheduleReview(it.problem_id, d.toISOString().slice(0, 10));
    setItems((xs) => xs.filter((x) => x.problem_id !== it.problem_id));
    onChange?.();
    toast(`Rescheduled +${days}d`);
  };

  return (
    <div className="page">
      <h1 className="page-title">Revision Queue</h1>
      <p className="page-sub">
        Adaptive spaced repetition (SM-2). Grade honestly — intervals stretch or shrink per card.
        Shakiest cards first. {items.length} due today.
      </p>

      {items.length === 0 ? (
        <Empty icon="🎉" text="Nothing due for review. Great work staying on top of it!" />
      ) : (
        items.map((it) => {
          const r = it.review;
          const leech = r.lapses >= 3;
          return (
            <div key={it.problem_id} className="card" style={{ marginBottom: 12 }}>
              <div className="row">
                <strong style={{ fontSize: 16, cursor: "pointer" }} onClick={() => nav(`/solve/${it.problem_id}`)}>
                  {it.title}
                </strong>
                <DiffBadge d={it.difficulty} />
                {leech && (
                  <span className="badge" style={{ color: "var(--bad)", borderColor: "var(--bad)" }} title="Repeatedly forgotten — re-learn the underlying pattern">
                    🩸 leech · {r.lapses} lapses
                  </span>
                )}
                <span className="spacer" />
                <span className="dim">
                  interval {r.interval_days}d · ease {r.ease.toFixed(2)}
                </span>
              </div>
              <div className="tag-row" style={{ marginTop: 8 }}>
                {it.topics.map((t) => (
                  <span key={t} className="badge tag">
                    {t}
                  </span>
                ))}
              </div>
              <div className="row wrap" style={{ marginTop: 12 }}>
                <button className="ghost" onClick={() => nav(`/solve/${it.problem_id}?mode=interview`)} title="Active recall: actually re-solve it, timed">
                  ▶ Re-solve (recall)
                </button>
                <span className="spacer" />
                {GRADES.map((g) => (
                  <button key={g.q} className={g.cls} title={g.hint} onClick={() => grade(it, g.q)}>
                    {g.label}
                  </button>
                ))}
              </div>
              <div className="row wrap" style={{ marginTop: 8 }}>
                <span className="dim" style={{ fontSize: 12 }}>Snooze:</span>
                <button className="ghost" onClick={() => reschedule(it, 1)}>+1d</button>
                <button className="ghost" onClick={() => reschedule(it, 3)}>+3d</button>
                <button className="ghost" onClick={() => reschedule(it, 7)}>+7d</button>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
