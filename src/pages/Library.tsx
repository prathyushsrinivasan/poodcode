import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { open as openDialog, save as saveDialog } from "@tauri-apps/plugin-dialog";
import { api } from "../api";
import type { Difficulty, Problem, SolvedStatus } from "../types";
import { applyFilter, emptyFilter, type ProblemFilter, type SortKey } from "../lib/filters";
import { Confidence, DiffBadge, Empty } from "../components/common";
import { relativeDate } from "../lib/format";
import { useToast } from "../components/Toast";

const STATUS_LABEL: Record<SolvedStatus, string> = {
  unsolved: "—",
  attempted: "Attempted",
  solved: "Solved",
};

export default function Library() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [topics, setTopics] = useState<string[]>([]);
  const [companies, setCompanies] = useState<string[]>([]);
  const [f, setF] = useState<ProblemFilter>(emptyFilter);
  const nav = useNavigate();
  const toast = useToast();

  const load = () => {
    api.listProblems().then(setProblems);
    api.distinctTags("topic").then(setTopics);
    api.distinctTags("company").then(setCompanies);
  };
  useEffect(load, []);

  const filtered = useMemo(() => applyFilter(problems, f), [problems, f]);

  const toggleIn = <T,>(arr: T[], v: T): T[] =>
    arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v];

  const toggleFav = async (p: Problem) => {
    await api.setFavorite(p.id, !p.is_favorite);
    setProblems((ps) => ps.map((x) => (x.id === p.id ? { ...x, is_favorite: !x.is_favorite } : x)));
  };

  const setConf = async (p: Problem, v: number) => {
    await api.setConfidence(p.id, v);
    setProblems((ps) => ps.map((x) => (x.id === p.id ? { ...x, confidence: v } : x)));
  };

  const doImport = async () => {
    const path = await openDialog({ filters: [{ name: "JSON", extensions: ["json"] }] });
    if (typeof path !== "string") return;
    try {
      const text = await api.readFile(path);
      const n = await api.importProblems(text);
      toast(`Imported ${n} problems`);
      load();
    } catch (e) {
      toast(`Import failed: ${e}`);
    }
  };

  const doExport = async () => {
    const path = await saveDialog({
      defaultPath: "poodcode-problems.json",
      filters: [{ name: "JSON", extensions: ["json"] }],
    });
    if (!path) return;
    const json = await api.exportProblems();
    await api.writeFile(path, json);
    toast("Exported problem library");
  };

  return (
    <div className="page page-wide">
      <div className="row">
        <h1 className="page-title">Problem Library</h1>
        <span className="spacer" />
        <button onClick={doImport}>⬆ Import</button>
        <button onClick={doExport}>⬇ Export</button>
        <button className="primary" onClick={() => nav("/problem/new")}>
          + New Problem
        </button>
      </div>
      <p className="page-sub">
        {filtered.length} of {problems.length} problems
      </p>

      {/* Filters */}
      <div className="card" style={{ marginBottom: 16 }}>
        <input
          style={{ width: "100%", marginBottom: 12 }}
          placeholder="Search by title, topic, subtopic, or company…"
          value={f.search}
          onChange={(e) => setF({ ...f, search: e.target.value })}
        />
        <div className="row wrap" style={{ gap: 16 }}>
          <div>
            <div className="io-label">Difficulty</div>
            <div className="pill-toggle">
              {(["Intro", "Easy", "Medium", "Hard"] as Difficulty[]).map((d) => (
                <span
                  key={d}
                  className={`pill ${f.difficulties.includes(d) ? "on" : ""}`}
                  onClick={() => setF({ ...f, difficulties: toggleIn(f.difficulties, d) })}
                >
                  {d}
                </span>
              ))}
            </div>
          </div>
          <div>
            <div className="io-label">Status</div>
            <div className="pill-toggle">
              {(["all", "unsolved", "attempted", "solved"] as const).map((s) => (
                <span
                  key={s}
                  className={`pill ${f.status === s ? "on" : ""}`}
                  onClick={() => setF({ ...f, status: s })}
                >
                  {s === "all" ? "All" : STATUS_LABEL[s]}
                </span>
              ))}
            </div>
          </div>
          <div>
            <div className="io-label">Quick · search by weakness</div>
            <div className="pill-toggle">
              <span className={`pill ${f.favoritesOnly ? "on" : ""}`} onClick={() => setF({ ...f, favoritesOnly: !f.favoritesOnly })}>
                ★ Favorites
              </span>
              <span className={`pill ${f.needsReview ? "on" : ""}`} onClick={() => setF({ ...f, needsReview: !f.needsReview })}>
                Needs Review
              </span>
              <span className={`pill ${f.weakConfidence ? "on" : ""}`} onClick={() => setF({ ...f, weakConfidence: !f.weakConfidence })}>
                Weak Confidence
              </span>
              <span className={`pill ${f.overTime ? "on" : ""}`} onClick={() => setF({ ...f, overTime: !f.overTime })} title="Cumulative time spent over 45 minutes">
                Over 45 min
              </span>
              <span className={`pill ${f.failedTwice ? "on" : ""}`} onClick={() => setF({ ...f, failedTwice: !f.failedTwice })} title="Two or more non-accepted attempts">
                Failed ≥ 2
              </span>
              <span className={`pill ${f.neverOptimal ? "on" : ""}`} onClick={() => setF({ ...f, neverOptimal: !f.neverOptimal })} title="Solved, but confidence below 4">
                Never optimal
              </span>
            </div>
          </div>
          <div>
            <div className="io-label">Sort</div>
            <select value={f.sort} onChange={(e) => setF({ ...f, sort: e.target.value as SortKey })}>
              <option value="difficulty">Difficulty (easy → hard)</option>
              <option value="title">Title</option>
              <option value="recently_added">Recently Added</option>
              <option value="recently_solved">Recently Solved</option>
              <option value="attempts">Most Attempts</option>
              <option value="confidence">Lowest Confidence</option>
            </select>
          </div>
        </div>
        {(topics.length > 0 || companies.length > 0) && (
          <>
            <div className="io-label" style={{ marginTop: 12 }}>Topics</div>
            <div className="pill-toggle">
              {topics.map((t) => (
                <span key={t} className={`pill ${f.topics.includes(t) ? "on" : ""}`} onClick={() => setF({ ...f, topics: toggleIn(f.topics, t) })}>
                  {t}
                </span>
              ))}
            </div>
            {companies.length > 0 && (
              <>
                <div className="io-label" style={{ marginTop: 10 }}>Companies</div>
                <div className="pill-toggle">
                  {companies.map((c) => (
                    <span key={c} className={`pill ${f.companies.includes(c) ? "on" : ""}`} onClick={() => setF({ ...f, companies: toggleIn(f.companies, c) })}>
                      {c}
                    </span>
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </div>

      {filtered.length === 0 ? (
        <Empty icon="🔍" text="No problems match these filters." />
      ) : (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="data">
            <thead>
              <tr>
                <th style={{ width: 30 }}></th>
                <th>Title</th>
                <th style={{ width: 90 }}>Difficulty</th>
                <th>Topics</th>
                <th style={{ width: 90 }}>Status</th>
                <th style={{ width: 110 }}>Confidence</th>
                <th style={{ width: 90 }}>Last solved</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p) => (
                <tr key={p.id} onClick={() => nav(`/solve/${p.id}`)}>
                  <td>
                    <span
                      className={`star ${p.is_favorite ? "on" : ""}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleFav(p);
                      }}
                    >
                      {p.is_favorite ? "★" : "☆"}
                    </span>
                  </td>
                  <td>
                    <strong>{p.title}</strong>
                  </td>
                  <td>
                    <DiffBadge d={p.difficulty} />
                  </td>
                  <td>
                    <div className="tag-row">
                      {p.topics.slice(0, 3).map((t) => (
                        <span key={t} className="badge tag">
                          {t}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <span className={p.solved_status === "solved" ? "" : "dim"}>
                      {p.solved_status === "solved" ? "✅ Solved" : STATUS_LABEL[p.solved_status]}
                    </span>
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <Confidence value={p.confidence} onChange={(v) => setConf(p, v)} />
                  </td>
                  <td className="dim">{relativeDate(p.last_solved_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
