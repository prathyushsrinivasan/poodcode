import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type {
  Concept,
  Exercise,
  JudgeReport,
  Problem,
  QuizQuestion,
  SqlDataset,
  SqlOut,
  TestCase,
} from "../types";
import { Markdown } from "../components/Markdown";
import { CodeEditor } from "../components/CodeEditor";
import { CardStudy } from "../components/CardStudy";
import { DiffBadge, Empty } from "../components/common";
import { Section, useCollapse } from "../components/Collapsible";
import {
  DatasetBrowser,
  ResultGrid,
  TextGrid,
  differingRows,
} from "../components/SqlGrid";
import {
  loadDoneChapters,
  setChapterDone,
  solvedExercises,
  markExerciseSolved,
} from "../lib/learnProgress";

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
  // Mastery-track TypeScript categories (tools/typescript_mastery.py)
  "TS: Type System",
  "TS: Generics & Type-Level",
  "TS: Runtime & Architecture",
  // Japanese coding-vocabulary categories (shown under the 日本語 toggle)
  "JP: Coding Basics",
  "JP: Java Language",
  "JP: Control Flow",
  "JP: Data Structures",
  "JP: Errors & Debugging",
  "JP: Dev Tools & Git",
  "JP: Interview & Workplace",
  // Japanese × TypeScript foundations
  "JP: TypeScript Basics",
  "JP: TS Types",
  "JP: TS Functions",
  "JP: TS Objects & Tooling",
  "JP: Web & Frontend",
  // Language-agnostic Algorithms track (shown under the 🧠 Algorithms toggle)
  "Algo: Foundations",
  "Algo: Searching & Scanning",
  "Algo: Sorting",
  "Algo: Recursion",
  // Java vocabulary track (shown under the 📖 Java Vocab toggle)
  "JV: Language Core",
  "JV: OOP",
  "JV: Modifiers",
  "JV: Types",
  "JV: Collections",
  "JV: Generics",
  "JV: Exceptions",
  "JV: Concurrency",
  "JV: Functional",
  "JV: JVM & Memory",
  "JV: Strings",
  "JV: I/O",
  "JV: Tooling",
  "JV: Modern Java",
  // SQL track (shown under the 🗄 SQL toggle) — joins first, then everything
  // that builds on them. Must stay in sync with SQL_CATEGORY_ORDER in
  // tools/sql_defs.py, which refuses to generate a chapter filed anywhere else.
  "SQL: Join Foundations",
  "SQL: Aggregation",
  "SQL: Subqueries & CTEs",
  "SQL: Window Functions",
  "SQL: Sets & NULLs",
  "SQL: Performance",
];

// A concept with no explicit language is legacy Java content.
const conceptLang = (c: Concept) => c.language || "java";

const LANG_TABS: { id: string; label: string }[] = [
  { id: "java", label: "Java" },
  { id: "typescript", label: "TypeScript" },
  { id: "japanese", label: "日本語" },
  { id: "algorithms", label: "🧠 Algorithms" },
  { id: "java_vocab", label: "📖 Java Vocab" },
  { id: "sql", label: "🗄 SQL" },
];

// Human-readable name for a Learn language, used in headings and card labels.
const LANG_LABEL: Record<string, string> = {
  java: "Java",
  typescript: "TypeScript",
  japanese: "Japanese",
  algorithms: "Algorithms",
  java_vocab: "Java Vocab",
  sql: "SQL",
};
const langLabel = (id: string) => LANG_LABEL[id] || "Java";
const LANG_STORE_KEY = "poodcode:learn-lang";

export default function Learn() {
  const { key } = useParams();
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [problems, setProblems] = useState<Problem[]>([]);
  // The SQL track's databases, keyed for lookup by an exercise's `dataset`.
  // Loaded once here rather than per exercise card, since one dataset is shared
  // by a whole chapter (and often by several).
  const [datasets, setDatasets] = useState<Map<string, SqlDataset>>(new Map());
  const [lang, setLang] = useState<string>(
    () => localStorage.getItem(LANG_STORE_KEY) || "java"
  );
  const [done, setDone] = useState<Set<string>>(new Set());
  // Category sections fold independently per language track, so collapsing
  // "Arrays" under Java doesn't also fold it under another tab.
  const cats = useCollapse(`learn-cat:${lang}`);
  const nav = useNavigate();

  async function setDoneState(key: string, value: boolean) {
    setDone(await setChapterDone(done, key, value));
  }

  useEffect(() => {
    api.concepts().then(setConcepts).catch(() => {});
    api.listProblems().then(setProblems).catch(() => {});
    api
      .sqlDatasets()
      .then((ds) => setDatasets(new Map(ds.map((d) => [d.key, d]))))
      .catch(() => {});
    // Chapter completion lives in SQLite now (so backups cover it), which makes
    // it an async load rather than a synchronous localStorage read.
    loadDoneChapters().then(setDone).catch(() => {});
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
    return (
      <ConceptDetail
        concept={concept}
        related={related}
        problems={problems}
        datasets={datasets}
        isDone={done.has(concept.key)}
        onSetDone={(v) => setDoneState(concept.key, v)}
      />
    );
  }

  const isTs = lang === "typescript";
  const isJp = lang === "japanese";
  const isAlg = lang === "algorithms";
  const isVocab = lang === "java_vocab";
  const isSql = lang === "sql";

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
        {isSql ? (
          <>
            {shownCount} SQL chapters, starting at <strong>joins</strong> and building up
            through aggregation, subqueries, CTEs and window functions. Every drill and
            challenge runs <strong>real SQL against a real database</strong> — five small
            ones you can read end to end — and is checked against the exact result set.
            New here? Start with <strong>SQL: Join Foundations → How a Join Actually
            Works</strong>, and read <strong>Choosing the Right Join</strong> when you can
            do all four but never know which to reach for.
          </>
        ) : isVocab ? (
          <>
            {shownCount} Java vocabulary chapters — <strong>266 terms</strong>, each with a
            crisp <strong>textbook definition</strong> and a{" "}
            <strong>plain-English</strong> "what it actually means" line, plus a tiny example.
            Skim the glossary, drill it with <strong>🎴 spaced-repetition flashcards</strong>,
            and <strong>❓ quiz yourself</strong>. New here? Start with{" "}
            <strong>JV: Language Core → Keywords &amp; Syntax</strong>.
          </>
        ) : isAlg ? (
          <>
            {shownCount} <strong>language-agnostic</strong> algorithm lessons — the idea,
            pseudocode, worked traces, and cost of each technique, with{" "}
            <strong>multiple-choice quizzes</strong> to test yourself and curated{" "}
            <strong>practice problems</strong> to apply it in any language. New here? Start with{" "}
            <strong>Algo: Foundations → What Is an Algorithm?</strong>
          </>
        ) : isJp ? (
          <>
            {shownCount} Japanese coding-vocabulary sets — the words, readings, and{" "}
            <strong>example sentences</strong> you'll meet writing Java and doing technical
            interviews in Japanese. Tap a set to see the full glossary. New here? Start with{" "}
            <strong>JP: Coding Basics</strong>.
          </>
        ) : (
          <>
            {shownCount} {langLabel(lang)} concepts. Each teaches the syntax, then hands
            you short <strong>fill-in-the-blank drills</strong> and{" "}
            <strong>full-length problems</strong> — run them right here and check instantly.{" "}
            {isTs ? (
              <>
                New to TypeScript? Start with <strong>TS: Language Basics</strong> — then
                keep going through the type-system and type-level chapters.
              </>
            ) : (
              <>
                New to Java? Start with <strong>Foundations</strong>.
              </>
            )}
          </>
        )}
      </p>

      {isJp && (
        <div
          className="card"
          style={{ cursor: "pointer", borderColor: "var(--accent)", marginBottom: 22 }}
          onClick={() => nav("/jp-bridge")}
        >
          <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <strong>🈁 日本語 → Java — put the vocabulary to work</strong>
              <p className="dim" style={{ margin: "4px 0 0", fontSize: 13 }}>
                Read real coding problems stated in Japanese and solve them in Java, plus Japanese
                technical-interview practice.
              </p>
            </div>
            <span className="badge">Open →</span>
          </div>
        </div>
      )}

      {isTs && (
        <div
          className="card"
          style={{ cursor: "pointer", borderColor: "var(--accent)", marginBottom: 12 }}
          onClick={() => nav("/course")}
        >
          <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <strong>📗 New: the 8-month TypeScript course — from zero</strong>
              <p className="dim" style={{ margin: "4px 0 0", fontSize: 13 }}>
                A guided, week-by-week path from your first line of code to interview-ready. Each
                week has a goal, lessons that never outrun what you've learned, and a capstone
                project. The chapters below are your free-form reference.
              </p>
            </div>
            <span className="badge">Start →</span>
          </div>
        </div>
      )}

      {isTs && (
        <div
          className="card"
          style={{ cursor: "pointer", borderColor: "var(--accent)", marginBottom: 22 }}
          onClick={() => nav("/mastery")}
        >
          <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <strong>🎓 6-Month Mastery — these chapters, in order</strong>
              <p className="dim" style={{ margin: "4px 0 0", fontSize: 13 }}>
                Prefer a syllabus to a library? The mastery programme sequences every chapter
                below into 26 weeks, each with curated problems, a build project and an exam
                that unlocks the next week.
              </p>
            </div>
            <span className="badge">Open →</span>
          </div>
        </div>
      )}

      {byCategory.length > 1 && (
        <div className="row" style={{ gap: 6, marginBottom: 12 }}>
          <button
            className="ghost"
            style={{ padding: "2px 10px", fontSize: 12 }}
            onClick={() => cats.setAll(byCategory.map(([c]) => c), true)}
          >
            Expand all
          </button>
          <button
            className="ghost"
            style={{ padding: "2px 10px", fontSize: 12 }}
            onClick={() => cats.setAll(byCategory.map(([c]) => c), false)}
          >
            Collapse all
          </button>
        </div>
      )}

      {byCategory.map(([cat, items]) => {
        const doneN = items.filter((c) => done.has(c.key)).length;
        return (
          <Section
            key={cat}
            title={cat}
            open={cats.isOpen(cat)}
            onToggle={() => cats.toggle(cat)}
            meta={
              <span
                className="dim"
                style={{ fontSize: 12, color: doneN === items.length ? "var(--good)" : undefined }}
              >
                {doneN}/{items.length} done
              </span>
            }
          >
            <div className="grid cols-3">
              {items.map((c) => {
                const isDone = done.has(c.key);
                const exs = c.exercises ?? [];
                const drillN = exs.filter((e) => (e.kind || "drill") !== "challenge").length;
                const challengeN = exs.filter((e) => e.kind === "challenge").length;
                const quizN = c.quiz?.length ?? 0;
                return (
                  <div
                    key={c.key}
                    className="card"
                    style={{
                      cursor: "pointer",
                      borderColor: isDone ? "var(--good)" : undefined,
                    }}
                    onClick={() => nav(`/learn/${c.key}`)}
                  >
                    <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
                      <strong>
                        {isDone && <span style={{ color: "var(--good)" }}>✓ </span>}
                        {c.name}
                      </strong>
                      <span className="row" style={{ gap: 4, flexWrap: "wrap", justifyContent: "flex-end" }}>
                        {c.cards?.length > 0 ? (
                          <span className="badge" title="Vocabulary flashcards">
                            {c.cards.length} cards
                          </span>
                        ) : (
                          <>
                            {drillN > 0 && (
                              <span className="badge" title="Fill-in-the-blank drills">
                                {drillN} drills
                              </span>
                            )}
                            {challengeN > 0 && (
                              <span
                                className="badge"
                                title="Coding challenge"
                                style={{ borderColor: "var(--accent)", color: "var(--accent)" }}
                              >
                                🏆 challenge
                              </span>
                            )}
                          </>
                        )}
                        {quizN > 0 && (
                          <span
                            className="badge"
                            title="Multiple-choice self-check quiz"
                            style={{ borderColor: "var(--accent)", color: "var(--accent)" }}
                          >
                            ❓ {quizN} quiz
                          </span>
                        )}
                      </span>
                    </div>
                    <p className="dim" style={{ margin: "6px 0 0", fontSize: 13 }}>
                      {c.what}
                    </p>
                  </div>
                );
              })}
            </div>
          </Section>
        );
      })}
    </div>
  );
}

function ConceptDetail({
  concept,
  related,
  problems,
  datasets,
  isDone,
  onSetDone,
}: {
  concept: Concept;
  related: Problem[];
  problems: Problem[];
  datasets: Map<string, SqlDataset>;
  isDone: boolean;
  onSetDone: (done: boolean) => void;
}) {
  const nav = useNavigate();
  const bySlug = useMemo(() => {
    const m = new Map<string, Problem>();
    for (const p of problems) m.set(p.slug, p);
    return m;
  }, [problems]);

  const exercises = concept.exercises ?? [];
  const drills = exercises.filter((e) => (e.kind || "drill") !== "challenge");
  const challenges = exercises.filter((e) => e.kind === "challenge");

  // --- Auto-complete: mark this chapter done once the learner has scrolled to
  // the bottom AND solved all of its exercises (a chapter with no exercises just
  // needs to be read through). The manual Done toggle still works.
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const [scrolledToBottom, setScrolledToBottom] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const gradableIds = exercises.map((e) => e.id);
  const allSolved = gradableIds.every((id) => solvedEx.has(id));
  const onSolved = (id: string) => setSolvedEx(new Set(markExerciseSolved(id)));

  useEffect(() => {
    const el = bottomRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) setScrolledToBottom(true);
      },
      { threshold: 0.01 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [concept.key]);

  useEffect(() => {
    if (!isDone && scrolledToBottom && allSolved) onSetDone(true);
  }, [isDone, scrolledToBottom, allSolved, onSetDone]);
  const cards = concept.cards ?? [];
  const quiz = concept.quiz ?? [];
  const practiceRefs = (concept.practice ?? [])
    .map((pr) => ({ note: pr.note, problem: bySlug.get(pr.slug) }))
    .filter((x): x is { note: string; problem: Problem } => !!x.problem);
  const [mode, setMode] = useState<"lesson" | "cards">("lesson");
  // The datasets this chapter's exercises actually query, in first-use order.
  // Shown once at the top rather than repeated on every card: joins are
  // unlearnable without being able to see the rows you are joining.
  const usedDatasets = useMemo(() => {
    const keys: string[] = [];
    for (const ex of exercises) {
      if (ex.dataset && !keys.includes(ex.dataset)) keys.push(ex.dataset);
    }
    return keys.map((k) => datasets.get(k)).filter((d): d is SqlDataset => !!d);
  }, [exercises, datasets]);
  const [activeDataset, setActiveDataset] = useState(0);
  // Sections fold per concept, so a long chapter can be narrowed down to just
  // the drills (or just the lesson) and stay that way when you come back.
  const sec = useCollapse(`learn-sec:${concept.key}`);
  const secKeys = [
    "idea",
    "lesson",
    "dataset",
    "quiz",
    "practice",
    "drills",
    "challenges",
    "library",
  ];

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4, justifyContent: "space-between" }}>
        <div className="row">
          <button className="ghost" onClick={() => nav("/learn")}>
            ← Learn
          </button>
          <span className="badge">{concept.category}</span>
        </div>
        <button
          className="ghost"
          style={isDone ? { borderColor: "var(--good)", color: "var(--good)" } : undefined}
          onClick={() => onSetDone(!isDone)}
          title={isDone ? "Marked complete — click to undo" : "Mark this chapter as complete"}
        >
          {isDone ? "✓ Done" : "Mark done"}
        </button>
      </div>
      <h1 className="page-title" style={{ marginTop: 6 }}>
        {concept.name}
      </h1>
      <p className="page-sub">{concept.what}</p>

      <div className="row" style={{ gap: 6, marginBottom: 10 }}>
        <button
          className="ghost"
          style={{ padding: "2px 10px", fontSize: 12 }}
          onClick={() => sec.setAll(secKeys, true)}
        >
          Expand all
        </button>
        <button
          className="ghost"
          style={{ padding: "2px 10px", fontSize: 12 }}
          onClick={() => sec.setAll(secKeys, false)}
        >
          Collapse all
        </button>
      </div>

      <Section
        title="💡 The idea"
        open={sec.isOpen("idea")}
        onToggle={() => sec.toggle("idea")}
      >
        <div className="card" style={{ marginBottom: 14 }}>
          <p style={{ margin: 0 }}>{concept.deep}</p>
        </div>

        <div className="card" style={{ marginBottom: 0, borderColor: "var(--accent)" }}>
          <div className="io-label" style={{ color: "var(--accent)" }}>
            {conceptLang(concept) === "japanese"
              ? "How to read this"
              : conceptLang(concept) === "algorithms"
              ? "At a glance"
              : conceptLang(concept) === "java_vocab"
              ? "How to use this set"
              : `In ${langLabel(conceptLang(concept))}`}
          </div>
          <Markdown>{concept.java}</Markdown>
        </div>
      </Section>

      <Section
        title={cards.length > 0 ? "📖 Reference" : "📖 Lesson"}
        open={sec.isOpen("lesson")}
        onToggle={() => sec.toggle("lesson")}
      >
        {cards.length > 0 && (
          <div className="row" style={{ gap: 6, marginBottom: 14 }}>
            <button className={mode === "lesson" ? "" : "ghost"} onClick={() => setMode("lesson")}>
              📖 Glossary
            </button>
            <button className={mode === "cards" ? "" : "ghost"} onClick={() => setMode("cards")}>
              🎴 Study cards
            </button>
          </div>
        )}

        {cards.length > 0 && mode === "cards" ? (
          <CardStudy
            conceptKey={concept.key}
            cards={cards}
            variant={conceptLang(concept) === "japanese" ? "japanese" : "vocab"}
          />
        ) : (
          <Markdown>{concept.lesson}</Markdown>
        )}
      </Section>

      {usedDatasets.length > 0 && (
        <Section
          title="🗄 The dataset"
          open={sec.isOpen("dataset")}
          onToggle={() => sec.toggle("dataset")}
          meta={
            <span className="badge">
              {usedDatasets.length === 1
                ? usedDatasets[0].key
                : `${usedDatasets.length} databases`}
            </span>
          }
        >
          <p className="dim" style={{ marginTop: -4 }}>
            Every exercise below runs against a <strong>fresh copy</strong> of one of these,
            rebuilt from scratch each time — so nothing you run can break anything. Read the
            rows before you write the query.
          </p>
          {usedDatasets.length > 1 && (
            <div className="row" style={{ gap: 6, marginBottom: 12, flexWrap: "wrap" }}>
              {usedDatasets.map((d, i) => (
                <button
                  key={d.key}
                  className={i === activeDataset ? "" : "ghost"}
                  onClick={() => setActiveDataset(i)}
                >
                  {d.title}
                </button>
              ))}
            </div>
          )}
          <DatasetBrowser
            dataset={usedDatasets[Math.min(activeDataset, usedDatasets.length - 1)]}
          />
        </Section>
      )}

      {quiz.length > 0 && (
        <Section
          title="❓ Check yourself"
          open={sec.isOpen("quiz")}
          onToggle={() => sec.toggle("quiz")}
          meta={<span className="badge">{quiz.length} questions</span>}
        >
          <p className="dim" style={{ marginTop: -4 }}>
            {quiz.length} quick questions. Pick an answer to see whether it&rsquo;s right and{" "}
            <strong>why</strong>. No code to run — just recall.
          </p>
          <QuizSection questions={quiz} />
        </Section>
      )}

      {practiceRefs.length > 0 && (
        <Section
          title="🎯 Practice this technique"
          open={sec.isOpen("practice")}
          onToggle={() => sec.toggle("practice")}
          meta={<span className="badge">{practiceRefs.length} problems</span>}
        >
          <p className="dim" style={{ marginTop: -4 }}>
            Real problems from the Library where this idea is the key. Solve them in whatever
            language you like.
          </p>
          <div className="grid cols-2">
            {practiceRefs.map(({ note, problem }) => (
              <div
                key={problem.id}
                className="card"
                style={{ cursor: "pointer" }}
                onClick={() => nav(`/solve/${problem.id}`)}
              >
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <strong>{problem.title}</strong>
                  <DiffBadge d={problem.difficulty} />
                </div>
                {note && (
                  <p className="dim" style={{ margin: "6px 0 0", fontSize: 13 }}>
                    {note}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {drills.length > 0 && (
        <Section
          title="🧩 Warm-up drills — fill in the blank"
          open={sec.isOpen("drills")}
          onToggle={() => sec.toggle("drills")}
          meta={<span className="badge">{drills.length} drills</span>}
        >
          <p className="dim" style={{ marginTop: -4 }}>
            Everything is written except the one piece this lesson teaches. Replace{" "}
            <code>____</code>, then press <strong>Check</strong>.
          </p>
          {drills.map((ex, i) => (
            <ExerciseCard
              key={ex.id}
              index={i + 1}
              exercise={ex}
              dataset={ex.dataset ? datasets.get(ex.dataset) : undefined}
              source={ex.source_slug ? bySlug.get(ex.source_slug) : undefined}
              onSolved={onSolved}
            />
          ))}
        </Section>
      )}

      {challenges.length > 0 && (
        <Section
          title={challenges.length > 1 ? "🏆 Coding challenges" : "🏆 Coding challenge"}
          open={sec.isOpen("challenges")}
          onToggle={() => sec.toggle("challenges")}
          accent="var(--accent)"
          meta={
            <span className="badge" style={{ borderColor: "var(--accent)", color: "var(--accent)" }}>
              {challenges.length} challenge{challenges.length > 1 ? "s" : ""}
            </span>
          }
        >
          <p className="dim" style={{ marginTop: -4 }}>
            Now put it together. This is a complete little problem using only what
            you&rsquo;ve learned so far — write the whole solution where you see{" "}
            <code>____</code>, then <strong>Check</strong>. Stuck? Reveal the solution.
          </p>
          {challenges.map((ex, i) => (
            <ExerciseCard
              key={ex.id}
              index={i + 1}
              exercise={ex}
              challenge
              dataset={ex.dataset ? datasets.get(ex.dataset) : undefined}
              source={ex.source_slug ? bySlug.get(ex.source_slug) : undefined}
              onSolved={onSolved}
            />
          ))}
        </Section>
      )}

      {conceptLang(concept) !== "japanese" && related.length > 0 && (
        <Section
          title="Practice more in the Library"
          open={sec.isOpen("library")}
          onToggle={() => sec.toggle("library")}
          meta={<span className="badge">{related.length}</span>}
        >
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
        </Section>
      )}

      {!isDone && (
        <p className="faint" style={{ fontSize: 12, marginTop: 20, textAlign: "center" }}>
          {gradableIds.length > 0
            ? `This chapter marks itself ✓ Done once you've read to here and solved its ${gradableIds.length} exercise${gradableIds.length === 1 ? "" : "s"}${allSolved ? " — all solved!" : ` (${gradableIds.filter((id) => solvedEx.has(id)).length}/${gradableIds.length} solved)`}.`
            : "This chapter marks itself ✓ Done once you've read to here."}
        </p>
      )}

      {/* Sentinel: intersecting means the lesson has been read to the bottom. */}
      <div ref={bottomRef} style={{ height: 1 }} />
    </div>
  );
}

function ExerciseCard({
  index,
  exercise,
  source,
  dataset,
  challenge = false,
  onSolved,
}: {
  index: number;
  exercise: Exercise;
  source?: Problem;
  /** SQL track: the database this exercise queries. */
  dataset?: SqlDataset;
  challenge?: boolean;
  onSolved?: (id: string) => void;
}) {
  const nav = useNavigate();
  const storeKey = `poodcode:learn-ex:${exercise.id}`;
  const lang = exercise.language || "java";
  const isSql = lang === "sql";
  const [code, setCode] = useState<string>(
    () => localStorage.getItem(storeKey) ?? exercise.starter
  );
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState("");
  const [showHint, setShowHint] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  // The SQL track's scratch run: the learner's query against the base dataset,
  // showing whatever it returns rather than a pass/fail. Looking at the wrong
  // answer is most of how you get to the right one.
  const [preview, setPreview] = useState<SqlOut | null>(null);

  // Challenges are written from scratch, so give them a roomier editor than a
  // short fill-in-the-blank drill (whose starter already sizes it well).
  const height = Math.min(
    Math.max(exercise.starter.split("\n").length * 20 + 24, challenge ? 260 : 150),
    challenge ? 560 : 480
  );

  function update(v: string) {
    setCode(v);
    localStorage.setItem(storeKey, v);
  }

  function reset() {
    update(exercise.starter);
    setReport(null);
    setPreview(null);
    setErr("");
    setShowSolution(false);
  }

  /** The SQL a case runs against: the dataset, then that case's variation on it.
   * Keeping the shared schema out of the individual tests is what stops a 4 KB
   * CREATE/INSERT batch from being repeated inside all 161 exercises — see
   * `Exercise.dataset` and tools/sql_defs.py. */
  function setupFor(caseInput: string): string {
    if (!isSql) return caseInput;
    const base = dataset?.sql ?? "";
    return caseInput.trim() ? `${base}\n${caseInput}\n` : base;
  }

  async function check() {
    setRunning(true);
    setErr("");
    setReport(null);
    const cases: TestCase[] = exercise.tests.map((t, i) => ({
      id: 0,
      problem_id: 0,
      kind: "example",
      name: isSql && t.input.trim() ? `Test ${i + 1} (changed data)` : `Test ${i + 1}`,
      input: setupFor(t.input),
      expected_output: t.output,
      ordering: i,
    }));
    try {
      const r = await api.runTests(null, lang, code, cases);
      setReport(r);
      if (r.status === "accepted") onSolved?.(exercise.id);
    } catch (e) {
      setErr(String(e));
    } finally {
      setRunning(false);
    }
  }

  /** Run the query against the base dataset and just show what comes back. */
  async function runQuery() {
    if (!dataset) return;
    setRunning(true);
    setErr("");
    setReport(null);
    try {
      setPreview(await api.sqlQuery(dataset.sql, code));
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
      style={{
        marginBottom: 14,
        borderColor: solved
          ? "var(--good)"
          : challenge
          ? "var(--accent)"
          : undefined,
      }}
    >
      <div className="row" style={{ justifyContent: "space-between" }}>
        <strong>
          {index}. {exercise.title} {solved && <span style={{ color: "var(--good)" }}>✓</span>}
        </strong>
        <span className="row" style={{ gap: 6 }}>
          {challenge && exercise.difficulty && (
            <span className={`badge diff ${exercise.difficulty}`}>{exercise.difficulty}</span>
          )}
          {isSql && exercise.tests.length > 1 && (
            <span
              className="badge"
              title={`Checked against ${exercise.tests.length} datasets — the same schema with the data changed, so a hard-coded answer fails`}
            >
              {exercise.tests.length} datasets
            </span>
          )}
          {isSql && dataset && (
            <span className="badge" title={dataset.summary}>
              🗄 {dataset.key}
            </span>
          )}
          <span className="badge">{lang}</span>
        </span>
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
        {isSql && dataset && (
          <button
            className="ghost"
            onClick={runQuery}
            disabled={running}
            title="Run this SQL against the dataset and just show the result — no pass/fail"
          >
            ▶ Run query
          </button>
        )}
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

      {isSql && (
        <p className="dim" style={{ margin: "8px 0 0", fontSize: 12 }}>
          Tip: put <code>EXPLAIN QUERY PLAN</code> in front of your query and press{" "}
          <strong>Run query</strong> to see how SQLite intends to execute it.
        </p>
      )}

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

      {preview && <SqlPreview out={preview} />}

      {report && <Feedback report={report} isSql={isSql} />}

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

/** A language-agnostic multiple-choice self-check quiz. Graded entirely on the
 * client by comparing the picked option index — no code execution. Tracks a
 * running score across the concept's questions. */
function QuizSection({ questions }: { questions: QuizQuestion[] }) {
  // picked[i] = the option index the user chose for question i, or -1 if unanswered.
  const [picked, setPicked] = useState<number[]>(() => questions.map(() => -1));

  const answered = picked.filter((p) => p >= 0).length;
  const correct = picked.filter((p, i) => p === questions[i].answer).length;

  return (
    <div>
      {answered > 0 && (
        <div className="row" style={{ marginBottom: 10, gap: 8, alignItems: "center" }}>
          <span
            className="badge"
            style={{
              borderColor: correct === questions.length ? "var(--good)" : "var(--accent)",
              color: correct === questions.length ? "var(--good)" : "var(--accent)",
            }}
          >
            Score {correct}/{questions.length}
          </span>
          <span className="dim" style={{ fontSize: 12 }}>
            {answered}/{questions.length} answered
          </span>
          {answered > 0 && (
            <button
              className="ghost"
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => setPicked(questions.map(() => -1))}
            >
              Reset
            </button>
          )}
        </div>
      )}
      {questions.map((q, qi) => (
        <QuizItem
          key={qi}
          index={qi + 1}
          question={q}
          picked={picked[qi]}
          onPick={(oi) =>
            setPicked((prev) => {
              if (prev[qi] >= 0) return prev; // lock the first answer
              const next = [...prev];
              next[qi] = oi;
              return next;
            })
          }
        />
      ))}
    </div>
  );
}

function QuizItem({
  index,
  question,
  picked,
  onPick,
}: {
  index: number;
  question: QuizQuestion;
  picked: number;
  onPick: (optionIndex: number) => void;
}) {
  const answered = picked >= 0;
  const isRight = picked === question.answer;

  return (
    <div
      className="card"
      style={{
        marginBottom: 12,
        borderColor: answered ? (isRight ? "var(--good)" : "var(--bad)") : undefined,
      }}
    >
      <strong>
        {index}. {question.question}
      </strong>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 10 }}>
        {question.options.map((opt, oi) => {
          let border: string | undefined;
          let color: string | undefined;
          if (answered) {
            if (oi === question.answer) {
              border = "var(--good)";
              color = "var(--good)";
            } else if (oi === picked) {
              border = "var(--bad)";
              color = "var(--bad)";
            }
          }
          return (
            <button
              key={oi}
              className="ghost"
              style={{ textAlign: "left", borderColor: border, color, padding: "8px 12px" }}
              onClick={() => onPick(oi)}
              disabled={answered}
            >
              {answered && oi === question.answer && "✓ "}
              {answered && oi === picked && oi !== question.answer && "✗ "}
              {opt}
            </button>
          );
        })}
      </div>
      {answered && (
        <div
          className="card"
          style={{
            marginTop: 10,
            marginBottom: 0,
            background: "var(--accent-dim)",
            borderColor: isRight ? "var(--good)" : "var(--bad)",
          }}
        >
          <div
            className="io-label"
            style={{ color: isRight ? "var(--good)" : "var(--bad)" }}
          >
            {isRight ? "Correct" : "Not quite"}
          </div>
          <p style={{ margin: 0 }}>{question.explanation}</p>
        </div>
      )}
    </div>
  );
}

/** The result of a scratch "Run query", shown as a table rather than as text. */
function SqlPreview({ out }: { out: SqlOut }) {
  if (out.error) {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
        <div className="io-label" style={{ color: "var(--bad)" }}>
          {out.timed_out
            ? "Query timed out"
            : out.syntax_error
            ? "SQL error — the query would not compile"
            : "SQL error"}
        </div>
        <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 12 }}>{out.error}</pre>
        {out.timed_out && (
          <p className="dim" style={{ margin: "6px 0 0", fontSize: 12 }}>
            An accidental cross join is the usual cause — check that every table after the
            first has an <code>ON</code> clause.
          </p>
        )}
      </div>
    );
  }
  return (
    <div className="card" style={{ marginTop: 10, marginBottom: 0 }}>
      <div className="io-label">
        Query result — {out.row_count} row{out.row_count === 1 ? "" : "s"} in{" "}
        {out.runtime_ms} ms
      </div>
      {out.grid && (
        <ResultGrid
          columns={out.grid.columns}
          rows={out.grid.rows}
          truncated={out.grid.truncated}
        />
      )}
      <p className="dim" style={{ margin: "6px 0 0", fontSize: 12 }}>
        This is just what your SQL returns — press <strong>Check</strong> to compare it
        against the expected answer.
      </p>
    </div>
  );
}

/** The failing case, as two aligned tables with the differing rows tinted. */
function SqlCaseDiff({
  name,
  variation,
  expected,
  actual,
  stderr,
  timedOut,
}: {
  name: string;
  variation: boolean;
  expected: string;
  actual: string;
  stderr: string;
  timedOut: boolean;
}) {
  const diff = differingRows(expected, actual);
  return (
    <div style={{ marginTop: 10 }}>
      <div className="dim" style={{ fontSize: 12, marginBottom: 4 }}>
        {name}
        {variation && " — the same schema with the data changed, so a hard-coded answer fails here"}
      </div>
      {stderr ? (
        <pre
          style={{
            margin: 0,
            whiteSpace: "pre-wrap",
            fontSize: 12,
            color: "var(--bad)",
          }}
        >
          {timedOut ? "Query timed out. " : ""}
          {stderr}
        </pre>
      ) : (
        <div className="sql-compare">
          <div>
            <div className="io-label" style={{ color: "var(--good)" }}>
              Expected
            </div>
            <TextGrid text={expected} highlightRows={diff} />
          </div>
          <div>
            <div className="io-label" style={{ color: "var(--bad)" }}>
              Your query returned
            </div>
            <TextGrid text={actual} highlightRows={diff} />
          </div>
        </div>
      )}
    </div>
  );
}

function Feedback({ report, isSql = false }: { report: JudgeReport; isSql?: boolean }) {
  if (report.status === "not_installed") {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
        <div className="io-label" style={{ color: "var(--bad)" }}>Toolchain not available</div>
        <p style={{ margin: 0 }}>
          {report.not_installed_hint || "Install the language's toolchain to run these drills."}
        </p>
      </div>
    );
  }

  if (report.compile_error) {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
        <div className="io-label" style={{ color: "var(--bad)" }}>
          {isSql ? "SQL error — the query would not compile" : "Compile error"}
        </div>
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
        isSql &&
        failing.slice(0, 2).map((r, i) => (
          <SqlCaseDiff
            key={i}
            name={r.name}
            variation={r.name.includes("changed data")}
            expected={r.expected}
            actual={r.actual}
            stderr={r.stderr}
            timedOut={r.timed_out}
          />
        ))}
      {!ok &&
        !isSql &&
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
