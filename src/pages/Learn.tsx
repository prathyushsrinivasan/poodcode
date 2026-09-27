import { LessonMarkdown } from "../components/LessonMarkdown";
import { ChapterCheatSheet } from "../components/ChapterCheatSheet";
import { ExerciseCard, QuizSection } from "../components/exercise";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api";
import type {
  Card,
  Concept,
  JpVocab,
  Problem,
  SqlDataset,
} from "../types";
import { Markdown } from "../components/Markdown";
import { CardStudy, type StudyVariant } from "../components/CardStudy";
import { JpVocabCard, JpVocabMenu, useVocabReviews } from "../components/JpVocab";
import { vocabCardId } from "../lib/jpVocab";
import { joinReading } from "../lib/romaji";
import { DiffBadge } from "../components/common";
import { Section, useCollapse } from "../components/Collapsible";
import {
  DatasetBrowser,
} from "../components/SqlGrid";
import { TrackSkeleton } from "../components/Skeleton";
import {
  loadDoneChapters,
  migrateVocabCardIds,
  setChapterDone,
  solvedExercises,
  loadSolvedExercises,
  markExerciseSolved,
} from "../lib/learnProgress";
import { EmptyState } from "../components/ui";
import { ignore, loadFailed } from "../lib/failures";

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
  "JP: カタカナ Loanwords",
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

/** Which study layout a concept's cards want. The katakana set drops the
 * Type-the-reading mode: a loanword is its own reading, so typing it back would
 * test transliteration rather than Japanese. */
const studyVariant = (c: Concept): StudyVariant =>
  c.key === "jp_katakana" ? "loanword" : conceptLang(c) === "japanese" ? "japanese" : "vocab";

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
  // 日本語 core vocabulary. The open flashcard lives in the URL (?word=<id>) so
  // it can be linked to and Back closes it; `vocabList` is the filtered list it
  // was opened from, which prev/next walk.
  const [vocab, setVocab] = useState<JpVocab | null>(null);
  const [vocabList, setVocabList] = useState<string[]>([]);
  // Review state is shared by the menu (which shows the counts) and the card
  // (which does the grading), so it is owned here rather than by either.
  const vocabReviews = useVocabReviews();
  const [params, setParams] = useSearchParams();
  const openWord = params.get("word");

  async function setDoneState(key: string, value: boolean) {
    setDone(await setChapterDone(done, key, value));
  }

  useEffect(() => {
    api
      .concepts()
      .then((cs) => {
        setConcepts(cs);
        // Fold any pre-existing glossary review rows onto the vocabulary card
        // ids that replaced them. Guarded internally, so this runs once.
        migrateVocabCardIds(cs).catch(ignore("vocabulary id migration; it is retried next launch"));
      })
      .catch(loadFailed("the concept library"));
    api.jpVocab().then(setVocab).catch(loadFailed("the vocabulary deck"));
    api.listProblems().then(setProblems).catch(loadFailed("the problem list"));
    api
      .sqlDatasets()
      .then((ds) => setDatasets(new Map(ds.map((d) => [d.key, d]))))
      .catch(loadFailed("the SQL datasets"));
    // Chapter completion lives in SQLite now (so backups cover it), which makes
    // it an async load rather than a synchronous localStorage read.
    loadDoneChapters().then(setDone).catch(loadFailed("your completed chapters"));
  }, []);

  function openVocab(id: string, list: string[]) {
    setVocabList(list);
    setParams({ word: id });
  }

  const navigateVocab = useCallback(
    (id: string) => setParams({ word: id }, { replace: true }),
    [setParams]
  );

  const closeVocab = useCallback(() => {
    const next = new URLSearchParams(params);
    next.delete("word");
    setParams(next, { replace: true });
  }, [params, setParams]);

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

  /**
   * One deck for the whole 日本語 tab: the vocabulary list plus every glossary
   * set, de-duplicated by card id.
   *
   * The two used to schedule separately, so "what should I review today?" had
   * fourteen different answers and no way to ask it once. Step 4b gave the words
   * that exist in both places a single id, which is what makes merging them here
   * honest: 配列 is one card in this deck, not one from each source.
   */
  const reviewDeck = useMemo<Card[]>(() => {
    const out: Card[] = [];
    const seen = new Set<string>();
    const push = (card: Card, id: string) => {
      if (seen.has(id)) return;
      seen.add(id);
      out.push(card);
    };
    for (const w of vocab?.words ?? []) {
      const id = vocabCardId(w.id);
      push(
        {
          front: w.term,
          card_id: id,
          reading: joinReading(w.reading, w.romaji),
          meaning: w.meaning,
          example_ja: w.example_ja,
          example_en: w.example_en,
        },
        id
      );
    }
    for (const c of concepts) {
      if (conceptLang(c) !== "japanese") continue;
      for (const card of c.cards ?? []) {
        push(card, card.card_id || `${c.key}#${card.front}`);
      }
    }
    return out;
  }, [vocab, concepts]);

  if (key) {
    const concept = concepts.find((c) => c.key === key);
    if (concepts.length === 0) return <TrackSkeleton cards={6} />;
    if (!concept) {
      return (
        <div className="page">
          <EmptyState
            icon="learn"
            title="Concept not found."
            action={{ label: "Back to Learn", icon: "back", onClick: () => nav("/learn") }}
          />
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
            Start with <strong>Vocabulary</strong>: {vocab?.words.length || 100} core
            non-katakana words for Java, coding problems and TypeScript. Filter them by tag,
            then tap one for a <strong>flashcard</strong> with its reading, a description in
            English and Japanese, and an <strong>example sentence</strong>. Below it are{" "}
            {shownCount} vocabulary sets with full glossaries, starting with{" "}
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

      {isJp && reviewDeck.length > 0 && (
        <Section
          title="🎴 日本語 review — まとめて復習"
          open={cats.isOpen("jp-review")}
          onToggle={() => cats.toggle("jp-review")}
          meta={
            <span className="dim" style={{ fontSize: 12 }}>
              {reviewDeck.length} cards
            </span>
          }
        >
          <p className="dim" style={{ margin: "0 0 12px", fontSize: 13 }}>
            The vocabulary list and every glossary set in <strong>one session</strong> —
            whatever is due today, wherever it happens to live. A word that appears in
            both is one card here, not two.
          </p>
          <CardStudy conceptKey="jp-review" cards={reviewDeck} variant="japanese" />
        </Section>
      )}

      {isJp && vocab && vocab.words.length > 0 && (
        <Section
          title="📝 Vocabulary — 語彙"
          open={cats.isOpen("jp-vocab")}
          onToggle={() => cats.toggle("jp-vocab")}
          meta={
            <span className="dim" style={{ fontSize: 12 }}>
              {vocab.words.length} words
            </span>
          }
        >
          <JpVocabMenu vocab={vocab} reviews={vocabReviews} onOpen={openVocab} />
        </Section>
      )}

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

      {openWord && vocab && (
        <JpVocabCard
          vocab={vocab}
          id={openWord}
          list={vocabList}
          reviews={vocabReviews}
          onNavigate={navigateVocab}
          onClose={closeVocab}
        />
      )}
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

  // Hydrate the solved set from SQLite. The initialiser above reads a
  // module-level cache — warm after the first load of the session — and this
  // is what fills it on a cold start.
  useEffect(() => {
    loadSolvedExercises().then(setSolvedEx).catch(loadFailed("your solved exercises"));
  }, []);

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

  const cards = concept.cards ?? [];
  const quiz = concept.quiz ?? [];
  // A chapter with a self-check has to be *passed*, not merely scrolled past.
  // The glossary sets have no exercises, so `allSolved` is vacuously true for
  // them and reaching the bottom used to be the whole bar.
  const [quizCorrect, setQuizCorrect] = useState(0);
  const quizPassed = quiz.length === 0 || quizCorrect === quiz.length;

  useEffect(() => {
    if (!isDone && scrolledToBottom && allSolved && quizPassed) onSetDone(true);
  }, [isDone, scrolledToBottom, allSolved, quizPassed, onSetDone]);
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
            variant={studyVariant(concept)}
          />
        ) : (
          <LessonMarkdown>{concept.lesson}</LessonMarkdown>
        )}
      </Section>

      {conceptLang(concept) === "typescript" && (
        <Section
          title="📄 Cheat sheet"
          // Folded by default: useCollapse opens sections unless toggled, so
          // this one reads the inverse of its own key.
          open={!sec.isOpen("cheatsheet")}
          onToggle={() => sec.toggle("cheatsheet")}
        >
          <ChapterCheatSheet name={concept.name} what={concept.what} lesson={concept.lesson} />
        </Section>
      )}

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
          <QuizSection questions={quiz} onScore={setQuizCorrect} />
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
