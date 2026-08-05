import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Problem } from "../types";
import { DiffBadge, Empty } from "../components/common";
import { Markdown } from "../components/Markdown";

/** Pattern-recognition drill: read a problem, name the pattern before solving.
 * Retrieval practice for the single most useful interview skill — mapping a
 * novel problem to a known technique. */
export default function Drill() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [idx, setIdx] = useState(0);
  const [picked, setPicked] = useState<string | null>(null);
  const [score, setScore] = useState({ right: 0, total: 0 });
  const nav = useNavigate();

  useEffect(() => {
    api.listProblems().then((all) => {
      // Only problems that actually declare patterns can be drilled.
      const withPatterns = all.filter((p) => p.patterns.length > 0);
      setProblems(shuffle(withPatterns));
    });
  }, []);

  const allPatterns = useMemo(() => {
    const s = new Set<string>();
    problems.forEach((p) => p.patterns.forEach((x) => s.add(x)));
    return [...s];
  }, [problems]);

  const current = problems[idx];

  // Build 4 options: the correct pattern + 3 distractors.
  const options = useMemo(() => {
    if (!current) return [];
    const correct = current.patterns[0];
    const distractors = shuffle(allPatterns.filter((p) => !current.patterns.includes(p))).slice(0, 3);
    return shuffle([correct, ...distractors]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current]);

  if (problems.length === 0) {
    return (
      <div className="page">
        <h1 className="page-title">Pattern Drill</h1>
        <Empty icon="🧩" text="No pattern-tagged problems available to drill." />
      </div>
    );
  }

  const answered = picked !== null;
  const isCorrect = (opt: string) => current.patterns.includes(opt);

  const choose = (opt: string) => {
    if (answered) return;
    setPicked(opt);
    setScore((s) => ({ right: s.right + (isCorrect(opt) ? 1 : 0), total: s.total + 1 }));
  };

  const next = () => {
    setPicked(null);
    setIdx((i) => (i + 1) % problems.length);
  };

  return (
    <div className="page">
      <div className="row">
        <h1 className="page-title">Pattern Drill</h1>
        <span className="spacer" />
        <span className="badge">
          Score {score.right}/{score.total}
        </span>
      </div>
      <p className="page-sub">Read the problem and name the underlying pattern — before writing any code.</p>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row" style={{ marginBottom: 8 }}>
          <strong style={{ fontSize: 16 }}>{current.title}</strong>
          <DiffBadge d={current.difficulty} />
        </div>
        <Markdown>{current.description.split("\n### Input")[0]}</Markdown>
      </div>

      <div className="grid cols-2" style={{ marginBottom: 12 }}>
        {options.map((opt) => {
          let cls = "";
          if (answered) {
            if (isCorrect(opt)) cls = "success";
            else if (opt === picked) cls = "danger";
          }
          return (
            <button key={opt} className={cls} style={{ padding: "14px" }} onClick={() => choose(opt)} disabled={answered}>
              {opt}
            </button>
          );
        })}
      </div>

      {answered && (
        <div className="card" style={{ marginBottom: 12, borderColor: isCorrect(picked!) ? "var(--good)" : "var(--bad)" }}>
          <strong style={{ color: isCorrect(picked!) ? "var(--good)" : "var(--bad)" }}>
            {isCorrect(picked!) ? "Correct!" : `It's ${current.patterns.join(" / ")}.`}
          </strong>{" "}
          <span className="dim">Topics: {current.topics.join(", ")}.</span>
          <div className="row" style={{ marginTop: 10 }}>
            <button className="primary" onClick={next}>Next →</button>
            <button className="ghost" onClick={() => nav(`/solve/${current.id}`)}>Solve this one</button>
          </div>
        </div>
      )}
    </div>
  );
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
