import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { Concept, Exercise, JudgeReport, Problem, TestCase } from "../types";
import { Markdown } from "../components/Markdown";
import { CodeEditor } from "../components/CodeEditor";
import { DiffBadge, Empty } from "../components/common";

const CATEGORY_ORDER = [
  "Foundations",
  "Arrays",
  "Strings",
  "Data Structures",
  "Linked Lists",
  "Trees",
  "Searching & Sorting",
  "Recursion & DP",
  "Graphs",
  "Math",
  "General",
  // TypeScript track categories (shown when the TS toggle is active)
  "TS: Language Basics",
  "TS: Functions & Types",
  "TS: Data Structures",
  "TS: Composition & Reuse",
  "TS: Robustness",
];

// A concept with no explicit language is legacy Java content.
const conceptLang = (c: Concept) => c.language || "java";

const LANG_TABS: { id: string; label: string }[] = [
  { id: "java", label: "Java" },
  { id: "typescript", label: "TypeScript" },
];
const LANG_STORE_KEY = "poodcode:learn-lang";

export default function Learn() {
  const { key } = useParams();
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [lang, setLang] = useState<string>(
    () => localStorage.getItem(LANG_STORE_KEY) || "java"
  );
  const nav = useNavigate();

  useEffect(() => {
    api.concepts().then(setConcepts).catch(() => {});
    api.listProblems().then(setProblems).catch(() => {});
  }, []);

  function pickLang(id: string) {
    setLang(id);
    localStorage.setItem(LANG_STORE_KEY, id);
  }

  // Which languages actually have concepts, so the toggle only offers real tabs.
  const availableLangs = useMemo(() => {
    const present = new Set(concepts.map(conceptLang));
    return LANG_TABS.filter((t) => present.has(t.id));
  }, [concepts]);

  const byCategory = useMemo(() => {
    const map = new Map<string, Concept[]>();
    for (const c of concepts) {
      if (conceptLang(c) !== lang) continue;
      if (!map.has(c.category)) map.set(c.category, []);
      map.get(c.category)!.push(c);
    }
    return [...map.entries()].sort(
      (a, b) => CATEGORY_ORDER.indexOf(a[0]) - CATEGORY_ORDER.indexOf(b[0])
    );
  }, [concepts, lang]);

  const shownCount = useMemo(
    () => concepts.filter((c) => conceptLang(c) === lang).length,
    [concepts, lang]
  );

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
    return <ConceptDetail concept={concept} related={related} problems={problems} />;
  }

  const isTs = lang === "typescript";

  return (
    <div className="page">
      <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
        <h1 className="page-title">Learn</h1>
        {availableLangs.length > 1 && (
          <div className="row" style={{ gap: 6 }}>
            {availableLangs.map((t) => (
              <button
                key={t.id}
                className={t.id === lang ? "" : "ghost"}
                onClick={() => pickLang(t.id)}
              >
                {t.label}
              </button>
            ))}
          </div>
        )}
      </div>
      <p className="page-sub">
        {shownCount} {isTs ? "TypeScript" : "Java"} concepts. Each teaches the syntax, then hands
        you short <strong>fill-in-the-blank drills</strong> and{" "}
        <strong>full-length problems</strong> — run them right here and check instantly.{" "}
        {isTs ? (
          <>
            New to TypeScript? Start with <strong>TS: Language Basics</strong>.
          </>
        ) : (
          <>
            New to Java? Start with <strong>Foundations</strong>.
          </>
        )}
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
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <strong>{c.name}</strong>
                  {c.exercises?.length > 0 && (
                    <span className="badge" title="Fill-in-the-blank drills">
                      {c.exercises.length} drills
                    </span>
                  )}
                </div>
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

function ConceptDetail({
  concept,
  related,
  problems,
}: {
  concept: Concept;
  related: Problem[];
  problems: Problem[];
}) {
  const nav = useNavigate();
  const bySlug = useMemo(() => {
    const m = new Map<string, Problem>();
    for (const p of problems) m.set(p.slug, p);
    return m;
  }, [problems]);

  const exercises = concept.exercises ?? [];

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
        <div className="io-label" style={{ color: "var(--accent)" }}>
          In {conceptLang(concept) === "typescript" ? "TypeScript" : "Java"}
        </div>
        <p style={{ marginBottom: 0 }}>{concept.java}</p>
      </div>

      <Markdown>{concept.lesson}</Markdown>

      {exercises.length > 0 && (
        <>
          <div className="divider" />
          <h3>Try it — fill in the blank</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            Everything is written except the one piece this lesson teaches. Replace{" "}
            <code>____</code>, then press <strong>Check</strong>.
          </p>
          {exercises.map((ex, i) => (
            <ExerciseCard
              key={ex.id}
              index={i + 1}
              exercise={ex}
              source={ex.source_slug ? bySlug.get(ex.source_slug) : undefined}
            />
          ))}
        </>
      )}

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

function ExerciseCard({
  index,
  exercise,
  source,
}: {
  index: number;
  exercise: Exercise;
  source?: Problem;
}) {
  const nav = useNavigate();
  const storeKey = `poodcode:learn-ex:${exercise.id}`;
  const lang = exercise.language || "java";
  const [code, setCode] = useState<string>(
    () => localStorage.getItem(storeKey) ?? exercise.starter
  );
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState("");
  const [showHint, setShowHint] = useState(false);
  const [showSolution, setShowSolution] = useState(false);

  const height = Math.min(
    Math.max(exercise.starter.split("\n").length * 20 + 24, 150),
    480
  );

  function update(v: string) {
    setCode(v);
    localStorage.setItem(storeKey, v);
  }

  function reset() {
    update(exercise.starter);
    setReport(null);
    setErr("");
    setShowSolution(false);
  }

  async function check() {
    setRunning(true);
    setErr("");
    setReport(null);
    const cases: TestCase[] = exercise.tests.map((t, i) => ({
      id: 0,
      problem_id: 0,
      kind: "example",
      name: `Test ${i + 1}`,
      input: t.input,
      expected_output: t.output,
      ordering: i,
    }));
    try {
      const r = await api.runTests(null, lang, code, cases);
      setReport(r);
    } catch (e) {
      setErr(String(e));
    } finally {
      setRunning(false);
    }
  }

  const untouched = code === exercise.starter || code.includes("____");
  const solved = report?.status === "accepted";

  return (
    <div
      className="card"
      style={{ marginBottom: 14, borderColor: solved ? "var(--good)" : undefined }}
    >
      <div className="row" style={{ justifyContent: "space-between" }}>
        <strong>
          {index}. {exercise.title} {solved && <span style={{ color: "var(--good)" }}>✓</span>}
        </strong>
        <span className="badge">{lang}</span>
      </div>
      <p style={{ margin: "6px 0 10px" }}>{exercise.prompt}</p>

      <div
        style={{
          height,
          border: "1px solid var(--border)",
          borderRadius: 6,
          overflow: "hidden",
        }}
      >
        <CodeEditor language={lang} value={code} onChange={update} onRun={check} />
      </div>

      <div className="row" style={{ marginTop: 10, flexWrap: "wrap", gap: 8 }}>
        <button onClick={check} disabled={running}>
          {running ? "Checking…" : "Check"}
        </button>
        <button className="ghost" onClick={reset} disabled={running}>
          Reset
        </button>
        {exercise.hint && (
          <button className="ghost" onClick={() => setShowHint((s) => !s)}>
            {showHint ? "Hide hint" : "Hint"}
          </button>
        )}
        <button className="ghost" onClick={() => setShowSolution((s) => !s)}>
          {showSolution ? "Hide solution" : "Reveal solution"}
        </button>
        {untouched && !running && (
          <span className="dim" style={{ fontSize: 12, alignSelf: "center" }}>
            Replace the <code>____</code> before checking.
          </span>
        )}
      </div>

      {showHint && exercise.hint && (
        <div
          className="card"
          style={{ marginTop: 10, marginBottom: 0, background: "var(--accent-dim)" }}
        >
          <div className="io-label" style={{ color: "var(--accent)" }}>Hint</div>
          <p style={{ margin: 0 }}>{exercise.hint}</p>
        </div>
      )}

      {err && (
        <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
          <div className="io-label" style={{ color: "var(--bad)" }}>Couldn’t run</div>
          <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 12 }}>{err}</pre>
        </div>
      )}

      {report && <Feedback report={report} />}

      {showSolution && (
        <div style={{ marginTop: 10 }}>
          <Markdown>{"```" + lang + "\n" + exercise.solution + "\n```"}</Markdown>
        </div>
      )}

      {source && (
        <div className="dim" style={{ marginTop: 8, fontSize: 13 }}>
          Ready for the whole thing?{" "}
          <a
            style={{ cursor: "pointer", color: "var(--accent)" }}
            onClick={() => nav(`/solve/${source.id}`)}
          >
            Open “{source.title}” →
          </a>
        </div>
      )}
    </div>
  );
}

function Feedback({ report }: { report: JudgeReport }) {
  if (report.status === "not_installed") {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
        <div className="io-label" style={{ color: "var(--bad)" }}>Java not available</div>
        <p style={{ margin: 0 }}>
          {report.not_installed_hint || "Install a JDK to run these drills."}
        </p>
      </div>
    );
  }

  if (report.compile_error) {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
        <div className="io-label" style={{ color: "var(--bad)" }}>Compile error</div>
        <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 12 }}>
          {report.compile_error}
        </pre>
      </div>
    );
  }

  const ok = report.status === "accepted";
  const failing = report.results.filter((r) => !r.passed);

  return (
    <div
      className="card"
      style={{ marginTop: 10, marginBottom: 0, borderColor: ok ? "var(--good)" : "var(--bad)" }}
    >
      <div className="io-label" style={{ color: ok ? "var(--good)" : "var(--bad)" }}>
        {ok
          ? `All ${report.total} tests passed 🎉`
          : `${report.passed} / ${report.total} tests passed`}
      </div>
      {!ok &&
        failing.slice(0, 3).map((r, i) => (
          <div key={i} style={{ marginTop: 6, fontSize: 12 }}>
            <div className="dim">{r.name}</div>
            <div style={{ fontFamily: "var(--font-mono)" }}>
              <div>
                input: <code>{r.input.replace(/\n/g, " ⏎ ") || "(none)"}</code>
              </div>
              <div>
                expected: <code>{r.expected}</code>
              </div>
              <div style={{ color: "var(--bad)" }}>
                got: <code>{r.timed_out ? "(timed out)" : r.actual || "(nothing)"}</code>
              </div>
              {r.stderr && (
                <pre style={{ margin: "4px 0 0", whiteSpace: "pre-wrap" }}>{r.stderr}</pre>
              )}
            </div>
          </div>
        ))}
    </div>
  );
}
