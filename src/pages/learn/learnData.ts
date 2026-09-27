/**
 * Learn's data and vocabulary, shared by the library, a chapter and the
 * 日本語 page (UI_ROADMAP G6).
 *
 * Learn was one 1,501-line page doing four jobs — a concept library, a
 * language switcher, the SQL track and the 日本語 vocabulary — and it loaded
 * everything for all four on every visit. The seeds (concepts, SQL datasets,
 * the vocabulary deck) are embedded in the binary and cannot change while the
 * app runs, so they are fetched once per session here, like the curriculum;
 * the learner's own progress is re-read on every mount, because that does
 * change.
 */

import { useCallback, useEffect, useState } from "react";
import { api } from "../../api";
import type { Concept, JpVocab, Problem, SqlDataset } from "../../types";
import type { StudyVariant } from "../../components/CardStudy";
import { loadDoneChapters, migrateVocabCardIds, setChapterDone } from "../../lib/learnProgress";
import { ignore, loadFailed } from "../../lib/failures";

export const CATEGORY_ORDER = [
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
  // TypeScript track categories
  "TS: Language Basics",
  "TS: Functions & Types",
  "TS: Data Structures",
  "TS: Composition & Reuse",
  "TS: Robustness",
  // Mastery-track TypeScript categories (tools/typescript_mastery.py)
  "TS: Type System",
  "TS: Generics & Type-Level",
  "TS: Runtime & Architecture",
  // Japanese coding-vocabulary categories
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
  // Language-agnostic Algorithms track
  "Algo: Foundations",
  "Algo: Searching & Scanning",
  "Algo: Sorting",
  "Algo: Recursion",
  // Java vocabulary track
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
  // SQL track — joins first, then everything that builds on them. Must stay in
  // sync with SQL_CATEGORY_ORDER in tools/sql_defs.py, which refuses to
  // generate a chapter filed anywhere else.
  "SQL: Join Foundations",
  "SQL: Aggregation",
  "SQL: Subqueries & CTEs",
  "SQL: Window Functions",
  "SQL: Sets & NULLs",
  "SQL: Performance",
];

/** Where a category sorts; unknown categories go last rather than first. */
export function categoryRank(cat: string): number {
  const i = CATEGORY_ORDER.indexOf(cat);
  return i < 0 ? CATEGORY_ORDER.length : i;
}

/** A concept with no explicit language is legacy Java content. */
export const conceptLang = (c: Concept) => c.language || "java";

/** Which study layout a concept's cards want. The katakana set drops the
 * Type-the-reading mode: a loanword is its own reading, so typing it back would
 * test transliteration rather than Japanese. */
export const studyVariant = (c: Concept): StudyVariant =>
  c.key === "jp_katakana" ? "loanword" : conceptLang(c) === "japanese" ? "japanese" : "vocab";

export const TRACKS: { id: string; label: string }[] = [
  { id: "java", label: "Java" },
  { id: "typescript", label: "TypeScript" },
  { id: "algorithms", label: "Algorithms" },
  { id: "java_vocab", label: "Java vocabulary" },
  { id: "sql", label: "SQL" },
  { id: "japanese", label: "日本語" },
];

const TRACK_LABEL: Record<string, string> = {
  java: "Java",
  typescript: "TypeScript",
  japanese: "Japanese",
  algorithms: "Algorithms",
  java_vocab: "Java Vocab",
  sql: "SQL",
};
export const langLabel = (id: string) => TRACK_LABEL[id] || "Java";

export const TRACK_STORE_KEY = "poodcode:learn-lang";

/** The concept's category with its track prefix ("TS: ", "SQL: ") removed, for display. */
export function shortCategory(cat: string): string {
  return cat.replace(/^(TS|JP|Algo|JV|SQL): /, "");
}

// ---- Session caches for the embedded seeds ------------------------------------

let conceptsPromise: Promise<Concept[]> | null = null;
let datasetsPromise: Promise<Map<string, SqlDataset>> | null = null;
let vocabPromise: Promise<JpVocab> | null = null;

function cached<T>(get: () => Promise<T> | null, set: (p: Promise<T> | null) => void, load: () => Promise<T>): Promise<T> {
  let p = get();
  if (!p) {
    p = load().catch((e) => {
      set(null); // a transient failure must not be permanent
      throw e;
    });
    set(p);
  }
  return p;
}

export function loadConcepts(): Promise<Concept[]> {
  return cached(
    () => conceptsPromise,
    (p) => (conceptsPromise = p),
    () =>
      api.concepts().then((cs) => {
        // Fold any pre-existing glossary review rows onto the vocabulary card
        // ids that replaced them. Guarded internally, so this runs once.
        migrateVocabCardIds(cs).catch(ignore("vocabulary id migration; it is retried next launch"));
        return cs;
      })
  );
}

export function loadDatasets(): Promise<Map<string, SqlDataset>> {
  return cached(
    () => datasetsPromise,
    (p) => (datasetsPromise = p),
    () => api.sqlDatasets().then((ds) => new Map(ds.map((d) => [d.key, d])))
  );
}

export function loadVocab(): Promise<JpVocab> {
  return cached(
    () => vocabPromise,
    (p) => (vocabPromise = p),
    () => api.jpVocab()
  );
}

/**
 * Everything a Learn page shows: the concepts (the one thing it cannot do
 * without — its failure is the page's error state), plus the problems, SQL
 * datasets and chapter progress (each optional: a failure is a toast and the
 * page carries on without it).
 */
export function useLearnData() {
  const [concepts, setConcepts] = useState<Concept[] | null>(null);
  const [error, setError] = useState("");
  const [problems, setProblems] = useState<Problem[]>([]);
  const [datasets, setDatasets] = useState<Map<string, SqlDataset>>(new Map());
  const [done, setDone] = useState<Set<string>>(new Set());

  const load = useCallback(() => {
    setError("");
    loadConcepts()
      .then(setConcepts)
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    load();
    api.listProblems().then(setProblems).catch(loadFailed("the problem list"));
    loadDatasets().then(setDatasets).catch(loadFailed("the SQL datasets"));
    // Chapter completion lives in SQLite (so backups cover it).
    loadDoneChapters().then(setDone).catch(loadFailed("your completed chapters"));
  }, [load]);

  const markDone = useCallback(
    async (key: string, value: boolean) => {
      setDone(await setChapterDone(done, key, value));
    },
    [done]
  );

  return { concepts, error, reload: load, problems, datasets, done, markDone };
}
