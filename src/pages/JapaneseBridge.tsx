import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { BridgeProblem, InterviewQA, JpBridge, Problem } from "../types";
import { Empty } from "../components/common";

/**
 * Japanese → Java bridge: read a real problem stated in Japanese and open it in
 * the normal solver, plus a bank of Japanese technical-interview Q&A. Content
 * is embedded JSON (seeds/jp_bridge.json) served by the `jp_bridge` command.
 */
export default function JapaneseBridge() {
  const [bridge, setBridge] = useState<JpBridge | null>(null);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [tab, setTab] = useState<"solve" | "interview">("solve");

  useEffect(() => {
    api.jpBridge().then(setBridge).catch(() => setBridge({ problems: [], interview: [] }));
    api.listProblems().then(setProblems).catch(() => {});
  }, []);

  const idBySlug = useMemo(() => {
    const m = new Map<string, number>();
    for (const p of problems) m.set(p.slug, p.id);
    return m;
  }, [problems]);

  if (!bridge) return <div className="page">Loading…</div>;

  return (
    <div className="page">
      <h1 className="page-title">日本語で解く · Japanese → Java</h1>
      <p className="page-sub">
        Read a real coding problem <strong>in Japanese</strong>, then solve it in Java in the normal
        editor — plus a bank of Japanese <strong>technical-interview</strong> questions with model
        answers. This is where the vocabulary becomes real engineering practice.
      </p>

      <div className="row" style={{ gap: 6, marginBottom: 16 }}>
        <button className={tab === "solve" ? "" : "ghost"} onClick={() => setTab("solve")}>
          🈁 Solve in Japanese ({bridge.problems.length})
        </button>
        <button className={tab === "interview" ? "" : "ghost"} onClick={() => setTab("interview")}>
          🗣 Interview practice ({bridge.interview.length})
        </button>
      </div>

      {tab === "solve" ? (
        bridge.problems.length === 0 ? (
          <Empty icon="🈁" text="No bridge problems yet." />
        ) : (
          <div className="grid cols-2">
            {bridge.problems.map((p) => (
              <BridgeCard key={p.slug} problem={p} problemId={idBySlug.get(p.slug)} />
            ))}
          </div>
        )
      ) : bridge.interview.length === 0 ? (
        <Empty icon="🗣" text="No interview questions yet." />
      ) : (
        <div className="grid cols-2">
          {bridge.interview.map((qa, i) => (
            <InterviewCard key={i} qa={qa} />
          ))}
        </div>
      )}
    </div>
  );
}

function BridgeCard({ problem, problemId }: { problem: BridgeProblem; problemId?: number }) {
  const nav = useNavigate();
  const [showHint, setShowHint] = useState(false);

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column" }}>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
        <strong style={{ fontSize: 16 }}>{problem.title_ja}</strong>
        <span className="badge">{problem.slug}</span>
      </div>

      <p style={{ margin: "8px 0 10px", lineHeight: 1.8 }}>{problem.statement_ja}</p>

      {problem.io_ja && (
        <pre
          style={{
            background: "var(--bg-elev-2)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            padding: "8px 10px",
            fontSize: 12.5,
            margin: "0 0 10px",
            whiteSpace: "pre-wrap",
          }}
        >
          {problem.io_ja}
        </pre>
      )}

      {problem.vocab.length > 0 && (
        <div style={{ marginBottom: 10 }}>
          <div className="io-label">語彙 · Vocabulary</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {problem.vocab.map((v, i) => (
              <div key={i} style={{ fontSize: 13 }}>
                <strong>{v[0]}</strong>{" "}
                <span className="dim">（{v[1]}）</span> — {v[2]}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="row" style={{ marginTop: "auto", gap: 8, flexWrap: "wrap" }}>
        {problemId != null ? (
          <button onClick={() => nav(`/solve/${problemId}`)}>この問題を解く →</button>
        ) : (
          <span className="dim" style={{ fontSize: 12 }}>
            (problem not available)
          </span>
        )}
        {problem.hint_ja && (
          <button className="ghost" onClick={() => setShowHint((s) => !s)}>
            {showHint ? "ヒントを隠す" : "ヒント"}
          </button>
        )}
      </div>

      {showHint && problem.hint_ja && (
        <div
          className="card"
          style={{ marginTop: 10, marginBottom: 0, background: "var(--accent-dim)" }}
        >
          <div className="io-label" style={{ color: "var(--accent)" }}>
            ヒント
          </div>
          <p style={{ margin: 0 }}>{problem.hint_ja}</p>
        </div>
      )}
    </div>
  );
}

function InterviewCard({ qa }: { qa: InterviewQA }) {
  const [show, setShow] = useState(false);
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column" }}>
      <div className="row" style={{ gap: 6, flexWrap: "wrap", marginBottom: 6 }}>
        {qa.tags.map((t) => (
          <span key={t} className="badge">
            {t}
          </span>
        ))}
      </div>
      <strong style={{ fontSize: 15, lineHeight: 1.7 }}>{qa.q_ja}</strong>
      {qa.q_en && (
        <span className="dim" style={{ fontSize: 12.5, marginTop: 2 }}>
          {qa.q_en}
        </span>
      )}

      {show ? (
        <div
          style={{
            marginTop: 10,
            borderTop: "1px solid var(--border)",
            paddingTop: 10,
            lineHeight: 1.8,
          }}
        >
          <div style={{ color: "var(--accent)" }}>{qa.a_ja}</div>
          {qa.a_en && (
            <div className="dim" style={{ fontStyle: "italic", fontSize: 13, marginTop: 4 }}>
              {qa.a_en}
            </div>
          )}
        </div>
      ) : (
        <button className="ghost" style={{ marginTop: 10, alignSelf: "flex-start" }} onClick={() => setShow(true)}>
          模範解答を見る
        </button>
      )}
    </div>
  );
}
