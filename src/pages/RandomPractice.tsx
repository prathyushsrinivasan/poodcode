import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Difficulty, Problem } from "../types";
import { DiffBadge } from "../components/common";

const PREDICATES = [
  { id: "", label: "Any" },
  { id: "unsolved", label: "Unsolved" },
  { id: "weak", label: "Weak confidence" },
  { id: "stale60", label: "Not solved in 60 days" },
  { id: "failed_twice", label: "Failed ≥ 2 times" },
  { id: "never_optimal", label: "Never solved optimally" },
];

export default function RandomPractice() {
  const [topics, setTopics] = useState<string[]>([]);
  const [difficulty, setDifficulty] = useState<Difficulty | "">("");
  const [topic, setTopic] = useState("");
  const [predicate, setPredicate] = useState("unsolved");
  const [pick, setPick] = useState<Problem | null>(null);
  const [empty, setEmpty] = useState(false);
  const nav = useNavigate();

  useEffect(() => {
    api.distinctTags("topic").then(setTopics);
  }, []);

  const roll = async () => {
    setEmpty(false);
    const p = await api.randomProblem(difficulty || undefined, topic || undefined, predicate || undefined);
    if (p) setPick(p);
    else {
      setPick(null);
      setEmpty(true);
    }
  };

  return (
    <div className="page">
      <h1 className="page-title">Random Practice</h1>
      <p className="page-sub">Spin up a problem matching your filters.</p>

      <div className="card">
        <div className="row wrap" style={{ gap: 18 }}>
          <div>
            <div className="io-label">Difficulty</div>
            <div className="pill-toggle">
              {(["", "Intro", "Easy", "Medium", "Hard"] as const).map((d) => (
                <span key={d} className={`pill ${difficulty === d ? "on" : ""}`} onClick={() => setDifficulty(d)}>
                  {d || "Any"}
                </span>
              ))}
            </div>
          </div>
          <div>
            <div className="io-label">Topic</div>
            <select value={topic} onChange={(e) => setTopic(e.target.value)}>
              <option value="">Any topic</option>
              {topics.map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <div className="io-label">Condition</div>
            <select value={predicate} onChange={(e) => setPredicate(e.target.value)}>
              {PREDICATES.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <button className="primary" style={{ marginTop: 16 }} onClick={roll}>
          🎲 Pick a problem
        </button>
      </div>

      {empty && <div className="empty"><div className="big">🤷</div>No problems match those filters.</div>}

      {pick && (
        <div className="card" style={{ marginTop: 16 }}>
          <div className="row">
            <strong style={{ fontSize: 18 }}>{pick.title}</strong>
            <DiffBadge d={pick.difficulty} />
          </div>
          <div className="tag-row" style={{ marginTop: 8 }}>
            {pick.topics.map((t) => (
              <span key={t} className="badge tag">{t}</span>
            ))}
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <button className="primary" onClick={() => nav(`/solve/${pick.id}`)}>Solve →</button>
            <button onClick={roll}>Reroll</button>
          </div>
        </div>
      )}
    </div>
  );
}
