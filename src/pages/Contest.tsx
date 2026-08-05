import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Contest as ContestT, Problem } from "../types";
import { DiffBadge, Empty } from "../components/common";
import { formatClock } from "../lib/format";
import { useToast } from "../components/Toast";

export default function Contest() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [history, setHistory] = useState<ContestT[]>([]);
  const [active, setActive] = useState<ContestT | null>(null);
  const [count, setCount] = useState(3);
  const [minutes, setMinutes] = useState(60);
  const [difficulty, setDifficulty] = useState<string>("");
  const [now, setNow] = useState(Date.now());
  const startRef = useRef(0);
  const nav = useNavigate();
  const toast = useToast();

  const load = () => {
    api.listProblems().then(setProblems);
    api.listContests().then(setHistory);
  };
  useEffect(load, []);

  // Tick while a contest is active.
  useEffect(() => {
    if (!active || active.status !== "running") return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [active]);

  const elapsed = active ? Math.floor((now - startRef.current) / 1000) : 0;
  const remaining = active ? active.duration_seconds - elapsed : 0;

  // Auto-finish on timeout.
  useEffect(() => {
    if (active && active.status === "running" && remaining <= 0) {
      finish();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [remaining, active]);

  const pool = useMemo(
    () => (difficulty ? problems.filter((p) => p.difficulty === difficulty) : problems),
    [problems, difficulty]
  );

  const start = async () => {
    const shuffled = [...pool].sort(() => Math.random() - 0.5).slice(0, count);
    if (shuffled.length === 0) {
      toast("No problems match.");
      return;
    }
    const id = await api.createContest(
      `Contest ${new Date().toLocaleString()}`,
      shuffled.map((p) => p.id),
      minutes * 60
    );
    const c = await api.contest(id);
    startRef.current = Date.now();
    setNow(Date.now());
    setActive(c);
  };

  const refreshActive = async () => {
    if (active) setActive(await api.contest(active.id));
  };

  const finish = async () => {
    if (!active) return;
    await api.finishContest(active.id);
    setActive(await api.contest(active.id));
    api.listContests().then(setHistory);
    toast("Contest finished.");
  };

  if (active) {
    const solved = active.results.filter((r) => r.solved).length;
    const running = active.status === "running";
    return (
      <div className="page">
        <div className="row">
          <h1 className="page-title">{running ? "Contest in progress" : "Contest results"}</h1>
          <span className="spacer" />
          {running ? (
            <span className={`timer ${remaining < 300 ? "warn" : ""}`}>⏱ {formatClock(Math.max(0, remaining))}</span>
          ) : (
            <span className="badge" style={{ color: "var(--good)", borderColor: "var(--good)" }}>
              {solved}/{active.results.length} solved
            </span>
          )}
        </div>
        <p className="page-sub">Solve as many as you can. Submissions update your score automatically.</p>

        <div className="card" style={{ padding: 0, overflow: "hidden", marginBottom: 16 }}>
          <table className="data">
            <thead>
              <tr>
                <th style={{ width: 40 }}></th>
                <th>Problem</th>
                <th style={{ width: 90 }}>Difficulty</th>
                <th style={{ width: 90 }}>Wrong</th>
                <th style={{ width: 120 }}></th>
              </tr>
            </thead>
            <tbody>
              {active.results.map((r) => (
                <tr key={r.problem_id}>
                  <td>{r.solved ? "✅" : "⬜"}</td>
                  <td><strong>{r.title}</strong></td>
                  <td><DiffBadge d={r.difficulty} /></td>
                  <td className="dim">{r.wrong_tries}</td>
                  <td>
                    {running && (
                      <button onClick={() => nav(`/solve/${r.problem_id}?contest=${active.id}`)}>
                        Solve →
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="row">
          {running && (
            <>
              <button onClick={refreshActive}>↻ Refresh scores</button>
              <button className="danger" onClick={finish}>End contest</button>
            </>
          )}
          <button className="ghost" onClick={() => { setActive(null); load(); }}>
            Back to setup
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1 className="page-title">Contest Mode</h1>
      <p className="page-sub">Timed multi-problem sets — simulate interview-day pressure.</p>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row wrap" style={{ gap: 18 }}>
          <div>
            <div className="io-label">Problems</div>
            <input type="number" min={1} max={10} style={{ width: 70 }} value={count} onChange={(e) => setCount(Math.max(1, Math.min(10, Number(e.target.value))))} />
          </div>
          <div>
            <div className="io-label">Minutes</div>
            <input type="number" min={5} max={240} style={{ width: 80 }} value={minutes} onChange={(e) => setMinutes(Math.max(5, Number(e.target.value)))} />
          </div>
          <div>
            <div className="io-label">Difficulty</div>
            <div className="pill-toggle">
              {["", "Intro", "Easy", "Medium", "Hard"].map((d) => (
                <span key={d} className={`pill ${difficulty === d ? "on" : ""}`} onClick={() => setDifficulty(d)}>
                  {d || "Any"}
                </span>
              ))}
            </div>
          </div>
        </div>
        <button className="primary" style={{ marginTop: 16 }} onClick={start}>
          🏁 Start contest
        </button>
      </div>

      <h3>History</h3>
      {history.length === 0 ? (
        <Empty icon="🏁" text="No contests yet." />
      ) : (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="data">
            <thead>
              <tr>
                <th>Started</th>
                <th style={{ width: 90 }}>Score</th>
                <th style={{ width: 90 }}>Status</th>
                <th style={{ width: 100 }}></th>
              </tr>
            </thead>
            <tbody>
              {history.map((c) => {
                const solved = c.results.filter((r) => r.solved).length;
                return (
                  <tr key={c.id}>
                    <td>{new Date(c.started_at.replace(" ", "T")).toLocaleString()}</td>
                    <td className="dim">{solved}/{c.results.length}</td>
                    <td className={c.status === "finished" ? "dim" : ""}>{c.status}</td>
                    <td>
                      <button className="ghost" onClick={async () => { startRef.current = Date.now() - 999999; setActive(await api.contest(c.id)); }}>
                        View
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
