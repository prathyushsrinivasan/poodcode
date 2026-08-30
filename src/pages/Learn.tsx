import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { Concept, Problem } from "../types";
import { Markdown } from "../components/Markdown";
import { CardStudy } from "../components/CardStudy";
import { ExerciseCard, QuizSection } from "../components/LearnExercise";
import { DiffBadge, Empty } from "../components/common";
import {
  doneChapters,
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
];

// A concept with no explicit language is legacy Java content.
const conceptLang = (c: Concept) => c.language || "java";

const LANG_TABS: { id: string; label: string }[] = [
  { id: "java", label: "Java" },
  { id: "typescript", label: "TypeScript" },
  { id: "japanese", label: "日本語" },
  { id: "algorithms", label: "🧠 Algorithms" },
  { id: "java_vocab", label: "📖 Java Vocab" },
];

// Human-readable name for a Learn language, used in headings and card labels.
const LANG_LABEL: Record<string, string> = {
  java: "Java",
  typescript: "TypeScript",
  japanese: "Japanese",
  algorithms: "Algorithms",
  java_vocab: "Java Vocab",
};
const langLabel = (id: string) => LANG_LABEL[id] || "Java";
const LANG_STORE_KEY = "poodcode:learn-lang";

export default function Learn() {
  const { key } = useParams();
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [lang, setLang] = useState<string>(
    () => localStorage.getItem(LANG_STORE_KEY) || "java"
  );
  const [done, setDone] = useState<Set<string>>(() => doneChapters());
  const nav = useNavigate();

  function setDoneState(key: string, value: boolean) {
    setDone(new Set(setChapterDone(key, value)));
  }

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
    return (
      <ConceptDetail
        concept={concept}
        related={related}
        problems={problems}
        isDone={done.has(concept.key)}
        onSetDone={(v) => setDoneState(concept.key, v)}
      />
    );
  }

  const isTs = lang === "typescript";
  const isJp = lang === "japanese";
  const isAlg = lang === "algorithms";
  const isVocab = lang === "java_vocab";

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
        {isVocab ? (
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
                New to TypeScript? Start with <strong>TS: Language Basics</strong>.
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
          style={{ cursor: "pointer", borderColor: "var(--accent)", marginBottom: 22 }}
          onClick={() => nav("/course")}
        >
          <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <strong>📗 New: the 8-month TypeScript course</strong>
              <p className="dim" style={{ margin: "4px 0 0", fontSize: 13 }}>
                A guided, week-by-week path from absolute beginner to interview-ready — each week has
                a goal, lessons that never outrun what you've learned, and a capstone project. The
                concepts below are your free-form reference.
              </p>
            </div>
            <span className="badge">Start →</span>
          </div>
        </div>
      )}

      {byCategory.map(([cat, items]) => {
        const doneN = items.filter((c) => done.has(c.key)).length;
        return (
          <div key={cat} style={{ marginBottom: 22 }}>
            <div className="row" style={{ justifyContent: "space-between", marginBottom: 10 }}>
              <h3 style={{ margin: 0 }}>{cat}</h3>
              <span
                className="dim"
                style={{ fontSize: 12, color: doneN === items.length ? "var(--good)" : undefined }}
              >
                {doneN}/{items.length} done
              </span>
            </div>
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
          </div>
        );
      })}
    </div>
  );
}

function ConceptDetail({
  concept,
  related,
  problems,
  isDone,
  onSetDone,
}: {
  concept: Concept;
  related: Problem[];
  problems: Problem[];
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
  const cards = concept.cards ?? [];
  const quiz = concept.quiz ?? [];
  const practiceRefs = (concept.practice ?? [])
    .map((pr) => ({ note: pr.note, problem: bySlug.get(pr.slug) }))
    .filter((x): x is { note: string; problem: Problem } => !!x.problem);
  const [mode, setMode] = useState<"lesson" | "cards">("lesson");

  // --- Auto-complete: mark this chapter done once the learner has scrolled to
  // the bottom AND solved all of its exercises. Manual toggle still works.
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const [scrolledToBottom, setScrolledToBottom] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // Every judged exercise (drills + challenges) is a "given problem" to solve.
  // A chapter with no exercises just needs to be read to the bottom.
  const gradableIds = exercises.map((e) => e.id);
  const allSolved = gradableIds.every((id) => solvedEx.has(id));

  function handleExerciseSolved(id: string) {
    setSolvedEx(new Set(markExerciseSolved(id)));
  }

  // Watch a sentinel at the very bottom of the page: when it scrolls into view
  // (or the page is short enough that it's already visible), the lesson has been
  // read through. Works regardless of which ancestor is the scroll container.
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

      <div className="card" style={{ marginBottom: 14 }}>
        <div className="io-label">The idea</div>
        <p style={{ marginBottom: 0 }}>{concept.deep}</p>
      </div>

      <div className="card" style={{ marginBottom: 14, borderColor: "var(--accent)" }}>
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

      {quiz.length > 0 && (
        <>
          <div className="divider" />
          <h3>❓ Check yourself</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            {quiz.length} quick questions. Pick an answer to see whether it&rsquo;s right and{" "}
            <strong>why</strong>. No code to run — just recall.
          </p>
          <QuizSection questions={quiz} />
        </>
      )}

      {practiceRefs.length > 0 && (
        <>
          <div className="divider" />
          <h3>🎯 Practice this technique</h3>
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
        </>
      )}

      {drills.length > 0 && (
        <>
          <div className="divider" />
          <h3>🧩 Warm-up drills — fill in the blank</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            Everything is written except the one piece this lesson teaches. Replace{" "}
            <code>____</code>, then press <strong>Check</strong>.
          </p>
          {drills.map((ex, i) => (
            <ExerciseCard
              key={ex.id}
              index={i + 1}
              exercise={ex}
              source={ex.source_slug ? bySlug.get(ex.source_slug) : undefined}
              onSolved={handleExerciseSolved}
            />
          ))}
        </>
      )}

      {challenges.length > 0 && (
        <>
          <div className="divider" />
          <h3>🏆 Coding challenge</h3>
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
              source={ex.source_slug ? bySlug.get(ex.source_slug) : undefined}
              onSolved={handleExerciseSolved}
            />
          ))}
        </>
      )}

      {conceptLang(concept) !== "japanese" && related.length > 0 && (
        <>
          <div className="divider" />
          <h3>Practice more in the Library</h3>
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
        </>
      )}

      {!isDone && (
        <p className="faint" style={{ fontSize: 12, marginTop: 24, textAlign: "center" }}>
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

