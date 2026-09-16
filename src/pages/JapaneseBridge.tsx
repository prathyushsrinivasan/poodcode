import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import type { BridgeProblem, InterviewQA, JpBridge, Problem } from "../types";
import { Empty } from "../components/common";

/** The four stages a Japanese technical interview is actually made of. Every
 * question carries its stage as its first tag — asserted at generation. */
const INTERVIEW_STAGES = [
  { id: "自己紹介", hint: "Introducing yourself, your experience and your questions" },
  { id: "コーディング", hint: "The coding round — complexity, edge cases, testing" },
  { id: "設計", hint: "System design — data, scale, security, trade-offs" },
  { id: "振り返り", hint: "Behavioural — failure, disagreement, handover" },
];

/**
 * Japanese → Java bridge: read a real problem stated in Japanese and open it in
 * the normal solver, plus a bank of Japanese technical-interview Q&A. Content
 * is embedded JSON (seeds/jp_bridge.json) served by the `jp_bridge` command.
 */
export default function JapaneseBridge() {
  const [bridge, setBridge] = useState<JpBridge | null>(null);
  const [problems, setProblems] = useState<Problem[]>([]);
  // term -> vocabulary word id, so a chip can link to the card that teaches it.
  const [wordIds, setWordIds] = useState<Map<string, string>>(new Map());
  const [tab, setTab] = useState<"solve" | "interview">("solve");
  const [stage, setStage] = useState<string>("all");

  useEffect(() => {
    api.jpBridge().then(setBridge).catch(() => setBridge({ problems: [], interview: [] }));
    api.listProblems().then(setProblems).catch(() => {});
    api
      .jpVocab()
      .then((v) => setWordIds(new Map(v.words.map((w) => [w.term, w.id]))))
      .catch(() => {
        /* without the list the chips simply stay plain text */
      });
  }, []);

  const idBySlug = useMemo(() => {
    const m = new Map<string, number>();
    for (const p of problems) m.set(p.slug, p.id);
    return m;
  }, [problems]);

  // Questions are filed by the stage of the interview they belong to, so you
  // can practise the one you're actually about to sit.
  const shownQA = useMemo(() => {
    const all = bridge?.interview ?? [];
    return stage === "all" ? all : all.filter((q) => q.tags[0] === stage);
  }, [bridge, stage]);

  const stageCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const q of bridge?.interview ?? []) {
      const s = q.tags[0] ?? "";
      counts.set(s, (counts.get(s) ?? 0) + 1);
    }
    return counts;
  }, [bridge]);

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
              <BridgeCard
                key={p.slug}
                problem={p}
                problemId={idBySlug.get(p.slug)}
                wordIds={wordIds}
              />
            ))}
          </div>
        )
      ) : bridge.interview.length === 0 ? (
        <Empty icon="🗣" text="No interview questions yet." />
      ) : (
        <>
          <div className="row" style={{ gap: 6, flexWrap: "wrap", marginBottom: 14 }}>
            <button
              className={stage === "all" ? "" : "ghost"}
              style={{ padding: "2px 10px", fontSize: 12 }}
              onClick={() => setStage("all")}
            >
              すべて <span className="dim">{bridge.interview.length}</span>
            </button>
            {INTERVIEW_STAGES.map((s) => (
              <button
                key={s.id}
                className={stage === s.id ? "" : "ghost"}
                style={{ padding: "2px 10px", fontSize: 12 }}
                onClick={() => setStage(s.id)}
                title={s.hint}
              >
                {s.id} <span className="dim">{stageCounts.get(s.id) ?? 0}</span>
              </button>
            ))}
          </div>
          <div className="grid cols-2">
            {shownQA.map((qa, i) => (
              <InterviewCard key={`${stage}-${i}`} qa={qa} wordIds={wordIds} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function BridgeCard({
  problem,
  problemId,
  wordIds,
}: {
  problem: BridgeProblem;
  problemId?: number;
  wordIds: Map<string, string>;
}) {
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
            {problem.vocab.map((v, i) => {
              // The same word is taught as a flashcard next door; when it is,
              // the chip becomes the way in rather than a dead repetition.
              const id = wordIds.get(v[0]);
              return (
                <div key={i} style={{ fontSize: 13 }}>
                  {id ? (
                    <Link to={`/learn?word=${id}`} title={`${v[0]} を単語帳で開く`}>
                      <strong>{v[0]}</strong>
                    </Link>
                  ) : (
                    <strong>{v[0]}</strong>
                  )}{" "}
                  <span className="dim">（{v[1]}）</span> — {v[2]}
                </div>
              );
            })}
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

function InterviewCard({ qa, wordIds }: { qa: InterviewQA; wordIds: Map<string, string> }) {
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

      {qa.terms.length > 0 && (
        <div
          className="row"
          style={{ gap: 5, flexWrap: "wrap", marginTop: "auto", paddingTop: 10, alignItems: "center" }}
        >
          <span className="io-label" style={{ margin: 0 }}>
            語彙
          </span>
          {qa.terms.map((t) => {
            const id = wordIds.get(t);
            return id ? (
              <Link key={t} to={`/learn?word=${id}`} className="badge" title={`${t} を単語帳で開く`}>
                {t}
              </Link>
            ) : (
              <span key={t} className="badge">
                {t}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
