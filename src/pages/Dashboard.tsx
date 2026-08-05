import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Dashboard as Dash, TopicRecommendation } from "../types";
import { formatDuration } from "../lib/format";
import { DiffBadge, Stat } from "../components/common";

function GoalRow({ label, done, target }: { label: string; done: number; target: number }) {
  if (target <= 0) return null;
  const pct = Math.min(100, (done / target) * 100);
  const complete = done >= target;
  return (
    <div style={{ marginBottom: 12 }}>
      <div className="row" style={{ marginBottom: 5 }}>
        <span>{complete ? "✅" : "⬜"} {label}</span>
        <span className="spacer" />
        <span className="dim mono">
          {done}/{target}
        </span>
      </div>
      <div className="progress">
        <span style={{ width: `${pct}%`, background: complete ? "var(--good)" : "var(--accent)" }} />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [d, setD] = useState<Dash | null>(null);
  const [recs, setRecs] = useState<TopicRecommendation[]>([]);
  const nav = useNavigate();

  useEffect(() => {
    api.dashboard().then(setD).catch((e) => console.error(e));
    api.learningRecommendations().then(setRecs).catch(() => setRecs([]));
  }, []);

  if (!d) return <div className="page">Loading…</div>;

  const g = d.goals;
  const gp = d.goal_progress;

  return (
    <div className="page">
      <h1 className="page-title">Dashboard</h1>
      <p className="page-sub">
        {new Date().toLocaleDateString(undefined, {
          weekday: "long",
          month: "long",
          day: "numeric",
        })}
        {" · "}
        {d.total_solved}/{d.total_problems} problems solved overall
      </p>

      <div className="grid cols-4" style={{ marginBottom: 18 }}>
        <Stat value={d.solved_today} label="Solved today" />
        <Stat value={formatDuration(d.study_seconds_today)} label="Study time today" />
        <Stat value={`${d.current_streak}🔥`} label="Current streak" />
        <Stat value={d.reviews_due} label="Reviews due" />
      </div>

      <div className="grid cols-2">
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Today's Goals</h3>
          <GoalRow label="Solve Intro" done={gp.intro} target={g.intro} />
          <GoalRow label="Solve Easy" done={gp.easy} target={g.easy} />
          <GoalRow label="Solve Medium" done={gp.medium} target={g.medium} />
          <GoalRow label="Solve Hard" done={gp.hard} target={g.hard} />
          <GoalRow label="Review problems" done={gp.reviews} target={g.reviews} />
          <div className="faint" style={{ fontSize: 12, marginTop: 6 }}>
            Adjust targets in Settings.
          </div>
        </div>

        <div className="grid" style={{ gridTemplateRows: "auto 1fr" }}>
          <div className="card">
            <div className="stat-label">Weakest topic</div>
            <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>
              {d.weakest_topic ?? "—"}
            </div>
            <div className="faint" style={{ fontSize: 12 }}>
              Based on solved ratio and confidence.
            </div>
          </div>

          <div className="card">
            <div className="stat-label">Suggested next problem</div>
            {d.suggested_problem ? (
              <>
                <div className="row" style={{ marginTop: 8 }}>
                  <strong style={{ fontSize: 16 }}>{d.suggested_problem.title}</strong>
                  <DiffBadge d={d.suggested_problem.difficulty} />
                </div>
                <div className="tag-row" style={{ marginTop: 8 }}>
                  {d.suggested_problem.topics.map((t) => (
                    <span key={t} className="badge tag">
                      {t}
                    </span>
                  ))}
                </div>
                <button
                  className="primary"
                  style={{ marginTop: 12 }}
                  onClick={() => nav(`/solve/${d.suggested_problem!.id}`)}
                >
                  Solve now →
                </button>
              </>
            ) : (
              <div className="dim" style={{ marginTop: 8 }}>
                All caught up! 🎉
              </div>
            )}
          </div>
        </div>
      </div>

      {recs.length > 0 && (
        <div className="card" style={{ marginTop: 18 }}>
          <h3 style={{ marginTop: 0 }}>Recommended focus</h3>
          <p className="faint" style={{ fontSize: 12, marginTop: 0 }}>
            Based on your weakest topics — concepts to shore up and a short practice ladder.
          </p>
          {recs.map((r) => (
            <div key={r.topic} style={{ marginBottom: 14 }}>
              <div className="row">
                <strong>{r.topic}</strong>
                <span className="spacer" />
                <span className="dim">
                  {r.solved}/{r.total} solved · confidence {r.avg_confidence.toFixed(1)}
                </span>
              </div>
              {r.concepts.length > 0 && (
                <div className="tag-row" style={{ marginTop: 6 }}>
                  <span className="dim" style={{ fontSize: 12 }}>Study:</span>
                  {r.concepts.map((c) => (
                    <span
                      key={c.key}
                      className="badge tag"
                      style={{ cursor: "pointer" }}
                      onClick={() => nav(`/learn/${c.key}`)}
                      title={`Open lesson: ${c.name}`}
                    >
                      📘 {c.name}
                    </span>
                  ))}
                </div>
              )}
              {r.problems.length > 0 && (
                <div className="tag-row" style={{ marginTop: 6 }}>
                  <span className="dim" style={{ fontSize: 12 }}>Practice:</span>
                  {r.problems.map((p) => (
                    <span
                      key={p.id}
                      className="badge"
                      style={{ cursor: "pointer" }}
                      onClick={() => nav(`/solve/${p.id}`)}
                      title={`${p.difficulty} · ${p.solved_status}`}
                    >
                      {p.solved_status === "solved" ? "✅" : "▶"} {p.title}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="row" style={{ marginTop: 18 }}>
        <button onClick={() => nav("/library")}>Browse Library</button>
        <button onClick={() => nav("/revision")}>Start Reviews ({d.reviews_due})</button>
        <button onClick={() => nav("/random")}>Random Problem</button>
        <button onClick={() => nav("/interview")}>Interview Mode</button>
      </div>
    </div>
  );
}
