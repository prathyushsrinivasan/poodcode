import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Problem } from "../types";
import { DiffBadge, Empty } from "../components/common";

export default function Companies() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [sel, setSel] = useState<string | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    api.listProblems().then(setProblems);
  }, []);

  const byCompany = useMemo(() => {
    const map = new Map<string, Problem[]>();
    for (const p of problems) {
      for (const c of p.companies) {
        if (!map.has(c)) map.set(c, []);
        map.get(c)!.push(p);
      }
    }
    return [...map.entries()].sort((a, b) => b[1].length - a[1].length);
  }, [problems]);

  if (byCompany.length === 0) {
    return (
      <div className="page">
        <h1 className="page-title">Company Prep</h1>
        <Empty icon="🏢" text="No company tags yet. Add company tags when authoring or editing problems." />
      </div>
    );
  }

  const selected = sel ? byCompany.find(([c]) => c === sel) : byCompany[0];

  return (
    <div className="page page-wide">
      <h1 className="page-title">Company Prep</h1>
      <p className="page-sub">Grouped problem lists by company tag.</p>

      <div className="row wrap" style={{ marginBottom: 16 }}>
        {byCompany.map(([c, list]) => {
          const solved = list.filter((p) => p.solved_status === "solved").length;
          return (
            <div
              key={c}
              className={`pill ${(selected && selected[0] === c) ? "on" : ""}`}
              onClick={() => setSel(c)}
              style={{ padding: "8px 14px" }}
            >
              {c} · {solved}/{list.length}
            </div>
          );
        })}
      </div>

      {selected && (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="data">
            <thead>
              <tr>
                <th>Title</th>
                <th style={{ width: 90 }}>Difficulty</th>
                <th>Topics</th>
                <th style={{ width: 90 }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {selected[1].map((p) => (
                <tr key={p.id} onClick={() => nav(`/solve/${p.id}`)}>
                  <td><strong>{p.title}</strong></td>
                  <td><DiffBadge d={p.difficulty} /></td>
                  <td>
                    <div className="tag-row">
                      {p.topics.slice(0, 3).map((t) => (
                        <span key={t} className="badge tag">{t}</span>
                      ))}
                    </div>
                  </td>
                  <td className={p.solved_status === "solved" ? "" : "dim"}>
                    {p.solved_status === "solved" ? "✅ Solved" : p.solved_status}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
