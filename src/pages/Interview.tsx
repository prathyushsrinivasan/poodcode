import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Difficulty, Problem } from "../types";
import { DiffBadge } from "../components/common";

export default function Interview() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [difficulty, setDifficulty] = useState<Difficulty | "">("");
  const nav = useNavigate();

  useEffect(() => {
    api.listProblems().then(setProblems);
  }, []);

  const start = (id: number) => nav(`/solve/${id}?mode=interview`);

  const startRandom = async () => {
    const p = await api.randomProblem(difficulty || undefined, undefined, "unsolved");
    let chosen = p;
    if (!chosen) {
      // Fallback: prefer an unsolved problem in the chosen difficulty; only fall
      // back to any problem if everything matching is already solved.
      const pool = difficulty ? problems.filter((x) => x.difficulty === difficulty) : problems;
      const unsolved = pool.filter((x) => x.solved_status !== "solved");
      const from = unsolved.length ? unsolved : pool;
      chosen = from[Math.floor(Math.random() * from.length)] ?? null;
    }
    if (chosen) start(chosen.id);
  };

  const filtered = difficulty ? problems.filter((p) => p.difficulty === difficulty) : problems;

  return (
    <div className="page">
      <h1 className="page-title">Interview Mode</h1>
      <p className="page-sub">Simulate a timed technical interview.</p>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row wrap">
          <div>
            <strong>Rules</strong>
            <ul className="dim" style={{ marginTop: 6 }}>
              <li>45-minute countdown timer</li>
              <li>No hints and no editorial</li>
              <li>Autocomplete &amp; editor suggestions disabled</li>
              <li>Editor locks when time expires</li>
            </ul>
          </div>
          <span className="spacer" />
          <div>
            <div className="io-label">Difficulty</div>
            <div className="pill-toggle">
              {(["", "Intro", "Easy", "Medium", "Hard"] as const).map((d) => (
                <span key={d} className={`pill ${difficulty === d ? "on" : ""}`} onClick={() => setDifficulty(d)}>
                  {d || "Any"}
                </span>
              ))}
            </div>
            <button className="primary" style={{ marginTop: 12 }} onClick={startRandom}>
              ⏱️ Start random interview
            </button>
          </div>
        </div>
      </div>

      <h3>Or pick a specific problem</h3>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="data">
          <tbody>
            {filtered.map((p) => (
              <tr key={p.id} onClick={() => start(p.id)}>
                <td><strong>{p.title}</strong></td>
                <td style={{ width: 90 }}><DiffBadge d={p.difficulty} /></td>
                <td>
                  <div className="tag-row">
                    {p.topics.slice(0, 3).map((t) => (
                      <span key={t} className="badge tag">{t}</span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
