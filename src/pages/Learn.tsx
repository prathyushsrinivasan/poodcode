import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { Concept, Problem } from "../types";
import { Markdown } from "../components/Markdown";
import { DiffBadge, Empty } from "../components/common";

const CATEGORY_ORDER = [
  "Foundations",
  "Arrays",
  "Strings",
  "Data Structures",
  "Searching & Sorting",
  "Recursion & DP",
  "Graphs",
  "Math",
  "General",
];

export default function Learn() {
  const { key } = useParams();
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [problems, setProblems] = useState<Problem[]>([]);
  const nav = useNavigate();

  useEffect(() => {
    api.concepts().then(setConcepts).catch(() => {});
    api.listProblems().then(setProblems).catch(() => {});
  }, []);

  const byCategory = useMemo(() => {
    const map = new Map<string, Concept[]>();
    for (const c of concepts) {
      if (!map.has(c.category)) map.set(c.category, []);
      map.get(c.category)!.push(c);
    }
    return [...map.entries()].sort(
      (a, b) => CATEGORY_ORDER.indexOf(a[0]) - CATEGORY_ORDER.indexOf(b[0])
    );
  }, [concepts]);

  if (key) {
    const concept = concepts.find((c) => c.key === key);
    if (concepts.length === 0) return <div className="page">Loading…</div>;
    if (!concept) {
      return (
        <div className="page">
          <Empty icon="📘" text="Concept not found." />
          <button onClick={() => nav("/learn")}>Back to Learn</button>
        </div>
      );
    }
    const related = problems.filter((p) => p.prerequisites?.some((pr) => pr.key === key));
    return <ConceptDetail concept={concept} related={related} />;
  }

  return (
    <div className="page">
      <h1 className="page-title">Learn</h1>
      <p className="page-sub">
        {concepts.length} concepts, each with a worked example, Java code, and pitfalls. New to
        Java? Start with <strong>Foundations</strong>.
      </p>

      {byCategory.map(([cat, items]) => (
        <div key={cat} style={{ marginBottom: 22 }}>
          <h3 style={{ marginBottom: 10 }}>{cat}</h3>
          <div className="grid cols-3">
            {items.map((c) => (
              <div
                key={c.key}
                className="card"
                style={{ cursor: "pointer" }}
                onClick={() => nav(`/learn/${c.key}`)}
              >
                <strong>{c.name}</strong>
                <p className="dim" style={{ margin: "6px 0 0", fontSize: 13 }}>
                  {c.what}
                </p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function ConceptDetail({ concept, related }: { concept: Concept; related: Problem[] }) {
  const nav = useNavigate();
  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4 }}>
        <button className="ghost" onClick={() => nav("/learn")}>
          ← Learn
        </button>
        <span className="badge">{concept.category}</span>
      </div>
      <h1 className="page-title" style={{ marginTop: 6 }}>
        {concept.name}
      </h1>
      <p className="page-sub">{concept.what}</p>

      <div className="card" style={{ marginBottom: 14 }}>
        <div className="io-label">The idea</div>
        <p style={{ marginBottom: 0 }}>{concept.deep}</p>
      </div>

      <div className="card" style={{ marginBottom: 14, borderColor: "var(--accent)" }}>
        <div className="io-label" style={{ color: "var(--accent)" }}>In Java</div>
        <p style={{ marginBottom: 0 }}>{concept.java}</p>
      </div>

      <Markdown>{concept.lesson}</Markdown>

      <div className="divider" />
      <h3>Practice this concept</h3>
      {related.length === 0 ? (
        <div className="dim">No problems tagged with this concept yet.</div>
      ) : (
        <div className="grid cols-2">
          {related.map((p) => (
            <div key={p.id} className="card" style={{ cursor: "pointer" }} onClick={() => nav(`/solve/${p.id}`)}>
              <div className="row">
                <strong>{p.title}</strong>
                <DiffBadge d={p.difficulty} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
