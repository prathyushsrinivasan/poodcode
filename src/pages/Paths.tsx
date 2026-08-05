import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Path } from "../types";
import { DiffBadge } from "../components/common";

export default function Paths() {
  const [paths, setPaths] = useState<Path[]>([]);
  const nav = useNavigate();

  useEffect(() => {
    api.listPaths().then(setPaths);
  }, []);

  return (
    <div className="page page-wide">
      <h1 className="page-title">Learning Paths</h1>
      <p className="page-sub">
        Curated, ordered tracks. Work top to bottom — each builds on the last.
      </p>

      {paths.length === 0 && <div className="dim">No paths yet.</div>}

      <div className="grid cols-2">
        {paths.map((p) => {
          const solved = p.items.filter((i) => i.solved_status === "solved").length;
          const pct = p.items.length ? (solved / p.items.length) * 100 : 0;
          // First unsolved item is the "current" step.
          const next = p.items.find((i) => i.solved_status !== "solved");
          return (
            <div key={p.id} className="card" style={{ marginBottom: 16 }}>
              <div className="row">
                <strong style={{ fontSize: 16 }}>{p.title}</strong>
                <span className="spacer" />
                <span className="dim mono">
                  {solved}/{p.items.length}
                </span>
              </div>
              <p className="dim" style={{ marginTop: 4 }}>
                {p.description}
              </p>
              <div className="progress" style={{ marginBottom: 10 }}>
                <span style={{ width: `${pct}%`, background: pct === 100 ? "var(--good)" : "var(--accent)" }} />
              </div>
              <div>
                {p.items.map((it, idx) => {
                  const done = it.solved_status === "solved";
                  const isNext = next && it.problem_id === next.problem_id;
                  return (
                    <div
                      key={it.problem_id}
                      className="row"
                      style={{
                        padding: "6px 8px",
                        borderRadius: 6,
                        cursor: "pointer",
                        background: isNext ? "color-mix(in srgb, var(--accent) 12%, transparent)" : "transparent",
                      }}
                      onClick={() => nav(`/solve/${it.problem_id}`)}
                    >
                      <span style={{ width: 22 }}>{done ? "✅" : isNext ? "▶" : `${idx + 1}.`}</span>
                      <span className={done ? "dim" : ""}>{it.title}</span>
                      <span className="spacer" />
                      <DiffBadge d={it.difficulty} />
                    </div>
                  );
                })}
              </div>
              {next && (
                <button className="primary" style={{ marginTop: 10 }} onClick={() => nav(`/solve/${next.problem_id}`)}>
                  Continue → {next.title}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
