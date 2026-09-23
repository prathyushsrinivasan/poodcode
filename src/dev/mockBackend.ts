/**
 * A fake Tauri backend, for running the UI in an ordinary browser.
 *
 * Every page reaches the database through `invoke` (see `src/api.ts`), so
 * without Tauri the whole app is error screens — which made design work,
 * screenshots and review impossible outside a full desktop build. This module
 * installs a `window.__TAURI_INTERNALS__` shim that answers those commands from
 * the JSON seeds plus synthesized progress.
 *
 * It is a *fixture*, not an emulator. Judging does not run code, and the
 * progress it reports is invented. What it guarantees is that every screen
 * renders with plausible, **deterministic** content: the fake progress is
 * derived from a hash of each problem's slug, so the same page looks the same
 * on every run and screenshot diffs (UI_ROADMAP L3) mean something.
 *
 * Mutations are real within the session and persist to localStorage, so
 * clicking through a flow behaves — solving a problem moves a counter, and it
 * is still moved after a reload. `resetMockState()` clears it.
 *
 * Enabled only by `VITE_MOCK=1` (see `npm run dev:mock`). `main.tsx` checks
 * that literal, so a production build drops this module and its seed imports.
 */

import type {
  Attempt,
  CardReview,
  CaseResult,
  Contest,
  CountPair,
  Dashboard,
  Goals,
  JudgeReport,
  LangInfo,
  MasteryProgress,
  MasteryTrack,
  Mistake,
  Note,
  Problem,
  ProcOut,
  Solution,
  SolvedStatus,
  TestCase,
  TopicRecommendation,
} from "../types";

/* ------------------------------------------------------------ determinism */

/** FNV-1a. Small, stable across runs, and good enough to scatter slugs. */
function hash(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/** A number in [0,1) derived from a key — the same key always gives the same
 * value, which is what makes the fixture screenshot-stable. */
function rand(key: string): number {
  return hash(key) / 4294967296;
}

const TODAY = new Date();
function isoDay(offset: number): string {
  const d = new Date(TODAY);
  d.setDate(d.getDate() + offset);
  return d.toISOString().slice(0, 10);
}
function isoStamp(offsetDays: number): string {
  const d = new Date(TODAY);
  d.setDate(d.getDate() + offsetDays);
  return d.toISOString().slice(0, 19).replace("T", " ");
}

/* ----------------------------------------------------------------- state */

const STORE_KEY = "poodcode.mock.v1";

interface MockState {
  settings: Record<string, string>;
  /** problem id → status, for problems the user changed this session. */
  solved: Record<number, SolvedStatus>;
  confidence: Record<number, number>;
  favorites: Record<number, boolean>;
  notes: Record<number, string>;
  drafts: Record<string, string>;
  hints: Record<number, number>;
  attempts: Record<number, Attempt[]>;
  solutions: Record<number, Solution[]>;
  mistakes: Record<number, Mistake[]>;
  cards: Record<string, CardReview>;
  chapters: string[];
  exercises: string[];
  mastery: Record<string, MasteryProgress>;
  /** Checkpoint contests started this session, by id. */
  contests: Record<number, Contest>;
  studySeconds: number;
  nextId: number;
}

function blankState(): MockState {
  return {
    settings: {
      onboarded: "1",
      goal_intro: "2",
      goal_easy: "3",
      goal_medium: "2",
      goal_hard: "1",
      goal_reviews: "5",
    },
    solved: {},
    confidence: {},
    favorites: {},
    notes: {},
    drafts: {},
    hints: {},
    attempts: {},
    solutions: {},
    mistakes: {},
    cards: {},
    chapters: [],
    exercises: [],
    mastery: {},
    contests: {},
    studySeconds: 41 * 60,
    nextId: 1000,
  };
}

let state: MockState = blankState();

function load() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) state = { ...blankState(), ...JSON.parse(raw) };
  } catch {
    /* a corrupt fixture is not worth a crash — start fresh */
  }
}

let saveTimer: ReturnType<typeof setTimeout> | undefined;
function save() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(state));
    } catch {
      /* quota or private mode — the session still works, it just won't persist */
    }
  }, 200);
}

/** Wipe the fixture's remembered progress. Exposed as `window.resetMockState()`. */
export function resetMockState() {
  state = blankState();
  try {
    localStorage.removeItem(STORE_KEY);
  } catch {
    /* nothing to clear */
  }
  location.reload();
}

/* ----------------------------------------------------------------- seeds */

/** Seeds are big (17 MB all told), so each is fetched once, on first use. */
const seedCache = new Map<string, Promise<any>>();
function seed(name: string): Promise<any> {
  let p = seedCache.get(name);
  if (!p) {
    p = loadSeed(name);
    seedCache.set(name, p);
  }
  return p;
}

function loadSeed(name: string): Promise<any> {
  switch (name) {
    case "problems":
      return import("../../src-tauri/seeds/problems.json").then((m) => m.default);
    case "concepts":
      return import("../../src-tauri/seeds/concepts.json").then((m) => m.default);
    case "dsa_curriculum":
      return import("../../src-tauri/seeds/dsa_curriculum.json").then((m) => m.default);
    case "ts_course":
      return import("../../src-tauri/seeds/ts_course.json").then((m) => m.default);
    case "java_course":
      return import("../../src-tauri/seeds/java_course.json").then((m) => m.default);
    case "backend_course":
      return import("../../src-tauri/seeds/backend_course.json").then((m) => m.default);
    case "projects":
      return import("../../src-tauri/seeds/projects.json").then((m) => m.default);
    case "mastery":
      return import("../../src-tauri/seeds/mastery.json").then((m) => m.default);
    case "jp_bridge":
      return import("../../src-tauri/seeds/jp_bridge.json").then((m) => m.default);
    case "jp_vocab":
      return import("../../src-tauri/seeds/jp_vocab.json").then((m) => m.default);
    case "sql_datasets":
      return import("../../src-tauri/seeds/sql_datasets.json").then((m) => m.default);
    case "flashcards":
      return import("../../src-tauri/seeds/flashcards.json").then((m) => m.default);
    default:
      return Promise.resolve(null);
  }
}

/* -------------------------------------------------------------- problems */

let problemCache: Problem[] | null = null;

/** The seed carries only the authored fields; the database adds identity and
 * progress. This does the same, inventing the progress. */
async function problems(): Promise<Problem[]> {
  if (problemCache) return problemCache.map(withProgress);
  const raw: any[] = await seed("problems");
  problemCache = raw.map((p, i) => ({
    function_spec: null,
    float_tolerance: 0,
    time_limit_ms: 2000,
    checker: "",
    judge_mode: "stdout",
    editorials: [],
    follow_ups: [],
    patterns: [],
    prerequisites: [],
    hints: [],
    examples: [],
    ...p,
    id: i + 1,
    test_cases: (p.test_cases ?? []).map((c: any, j: number) => ({
      id: i * 100 + j + 1,
      problem_id: i + 1,
      kind: c.kind ?? "example",
      name: c.name ?? `Case ${j + 1}`,
      input: c.input ?? "",
      expected_output: c.expected_output ?? "",
      ordering: j,
    })),
    is_favorite: false,
    solved_status: "unsolved" as SolvedStatus,
    confidence: 0,
    last_solved_at: null,
    time_taken_seconds: 0,
    attempts_count: 0,
    success_count: 0,
    created_at: isoStamp(-120),
    updated_at: isoStamp(-3),
  })) as Problem[];
  return problemCache.map(withProgress);
}

/** Layer the invented (and then the session's real) progress onto a problem.
 *
 * Roughly 45% of problems read as solved and 10% as attempted, weighted so the
 * easy end of the curriculum is further along than the hard end — which is what
 * a half-finished curriculum actually looks like, and exercises both the
 * "done" and "to do" styling on every page. */
function withProgress(p: Problem): Problem {
  const r = rand(p.slug);
  const bias =
    p.difficulty === "Intro" ? 0.3 : p.difficulty === "Easy" ? 0.15 : p.difficulty === "Hard" ? -0.2 : 0;
  let status: SolvedStatus = r < 0.45 + bias ? "solved" : r < 0.55 + bias ? "attempted" : "unsolved";
  if (state.solved[p.id]) status = state.solved[p.id];

  const solvedDaysAgo = Math.floor(rand(p.slug + "d") * 60) + 1;
  return {
    ...p,
    solved_status: status,
    confidence: state.confidence[p.id] ?? (status === "solved" ? 2 + Math.floor(r * 4) : 0),
    is_favorite: state.favorites[p.id] ?? rand(p.slug + "f") < 0.08,
    last_solved_at: status === "solved" ? isoStamp(-solvedDaysAgo) : null,
    attempts_count: status === "unsolved" ? 0 : 1 + Math.floor(rand(p.slug + "a") * 4),
    success_count: status === "solved" ? 1 : 0,
    time_taken_seconds: status === "unsolved" ? 0 : 300 + Math.floor(rand(p.slug + "t") * 1800),
  };
}

/* ------------------------------------------------------------- execution */

/** A believable judge run. Nothing is compiled: the verdict is derived from the
 * code's length and shape so that an empty starter fails and a filled-in
 * attempt passes, which is enough to exercise every results-pane state. */
function fakeJudge(code: string, cases: TestCase[]): JudgeReport {
  const meaningful = code.replace(/\/\/.*|\/\*[\s\S]*?\*\//g, "").trim();
  const looksAttempted = meaningful.length > 120;
  const list = cases.length > 0 ? cases : [];
  const results: CaseResult[] = list.map((c, i) => {
    const passed = looksAttempted && !(i === list.length - 1 && meaningful.length < 200);
    return {
      name: c.name || `Case ${i + 1}`,
      kind: c.kind,
      input: c.input,
      expected: c.expected_output,
      actual: passed ? c.expected_output : "(mock backend: no code was run)",
      stderr: "",
      passed,
      timed_out: false,
      runtime_ms: 8 + ((hash(c.input) % 40) as number),
      memory_kb: 12000 + (hash(c.name) % 6000),
      truncated: false,
      verdict: passed ? "pass" : "wrong",
    };
  });
  const passed = results.filter((r) => r.passed).length;
  return {
    status: results.length > 0 && passed === results.length ? "accepted" : "wrong",
    passed,
    total: results.length,
    runtime_ms: results.reduce((a, r) => a + r.runtime_ms, 0),
    memory_kb: results[0]?.memory_kb ?? 14000,
    compile_error: "",
    not_installed_hint: "",
    results,
  };
}

/* ------------------------------------------------------------- dashboard */

function goalsFromSettings(): Goals {
  const n = (k: string, d: number) => Number(state.settings[k] ?? d) || d;
  return {
    intro: n("goal_intro", 2),
    easy: n("goal_easy", 3),
    medium: n("goal_medium", 2),
    hard: n("goal_hard", 1),
    reviews: n("goal_reviews", 5),
  };
}

async function dashboard(): Promise<Dashboard> {
  const all = await problems();
  const solved = all.filter((p) => p.solved_status === "solved");
  const unsolved = all.filter((p) => p.solved_status !== "solved");
  const byTopic = new Map<string, { total: number; solved: number }>();
  for (const p of all) {
    for (const t of p.topics) {
      const e = byTopic.get(t) ?? { total: 0, solved: 0 };
      e.total++;
      if (p.solved_status === "solved") e.solved++;
      byTopic.set(t, e);
    }
  }
  const weakest = [...byTopic.entries()]
    .filter(([, v]) => v.total >= 5)
    .sort((a, b) => a[1].solved / a[1].total - b[1].solved / b[1].total)[0];

  return {
    solved_today: 2,
    study_seconds_today: state.studySeconds,
    reviews_due: 6,
    current_streak: 9,
    weakest_topic: weakest?.[0] ?? null,
    suggested_problem: unsolved[Math.floor(rand("suggest") * unsolved.length)] ?? null,
    goals: goalsFromSettings(),
    goal_progress: { intro: 1, easy: 2, medium: 1, hard: 0, reviews: 3 },
    total_problems: all.length,
    total_solved: solved.length,
  };
}

async function statistics(): Promise<any> {
  const all = await problems();
  const byDifficulty: Record<string, { total: number; solved: number }> = {};
  const topicMap = new Map<string, { total: number; solved: number; conf: number[] }>();
  for (const p of all) {
    const d = (byDifficulty[p.difficulty] ??= { total: 0, solved: 0 });
    d.total++;
    if (p.solved_status === "solved") d.solved++;
    for (const t of p.topics) {
      const e = topicMap.get(t) ?? { total: 0, solved: 0, conf: [] };
      e.total++;
      if (p.solved_status === "solved") {
        e.solved++;
        e.conf.push(p.confidence);
      }
      topicMap.set(t, e);
    }
  }
  const topics = [...topicMap.entries()].map(([topic, v]) => ({
    topic,
    total: v.total,
    solved: v.solved,
    avg_confidence: v.conf.length ? v.conf.reduce((a, b) => a + b, 0) / v.conf.length : 0,
  }));
  const ranked = [...topics].filter((t) => t.total >= 4).sort((a, b) => a.solved / a.total - b.solved / b.total);

  return {
    total_problems: all.length,
    total_solved: all.filter((p) => p.solved_status === "solved").length,
    by_difficulty: byDifficulty,
    by_topic: topics,
    avg_solve_seconds: 1140,
    acceptance_rate: 0.62,
    current_streak: 9,
    longest_streak: 23,
    language_usage: [
      { label: "java", value: 214 },
      { label: "python", value: 96 },
      { label: "typescript", value: 41 },
    ] as CountPair[],
    heatmap: Array.from({ length: 182 }, (_, i) => {
      const day = isoDay(-181 + i);
      const r = rand(day);
      return { date: day, count: r < 0.28 ? 0 : Math.ceil(r * 7) };
    }),
    weekly_activity: Array.from({ length: 12 }, (_, i) => ({
      label: isoDay(-7 * (11 - i)),
      value: Math.ceil(rand("w" + i) * 14),
    })),
    monthly_activity: Array.from({ length: 6 }, (_, i) => ({
      label: isoDay(-30 * (5 - i)).slice(0, 7),
      value: 20 + Math.floor(rand("m" + i) * 45),
    })),
    weakest_topics: ranked.slice(0, 6),
    strongest_topics: ranked.slice(-6).reverse(),
    first_attempt_rate: 0.41,
    retention_rate: 0.78,
    avg_tries_to_solve: 2.3,
    reviews_total: 148,
    mistake_tally: [
      { label: "missed-edge-case", value: 14 },
      { label: "off-by-one", value: 9 },
      { label: "wrong-data-structure", value: 6 },
      { label: "tle", value: 4 },
    ] as CountPair[],
    topic_behavior: ranked.slice(0, 8).map((t) => ({
      topic: t.topic,
      solved: t.solved,
      first_try_solved: Math.floor(t.solved * 0.4),
      first_try_rate: 0.4,
      avg_hints_used: 0.8,
      mastery: t.total ? t.solved / t.total : 0,
    })),
  };
}

async function recommendations(): Promise<TopicRecommendation[]> {
  const all = await problems();
  const stats = await statistics();
  return stats.weakest_topics.slice(0, 4).map((t: any) => ({
    topic: t.topic,
    solved: t.solved,
    total: t.total,
    avg_confidence: t.avg_confidence,
    concepts: [],
    problems: all
      .filter((p) => p.topics.includes(t.topic) && p.solved_status !== "solved")
      .slice(0, 3)
      .map((p) => ({
        id: p.id,
        title: p.title,
        difficulty: p.difficulty,
        solved_status: p.solved_status,
        confidence: p.confidence,
      })),
  }));
}

/* -------------------------------------------------------------- handlers */

const LANGUAGES: LangInfo[] = [
  { id: "java", label: "Java", monaco: "java", installed: true, install_hint: "" },
  { id: "python", label: "Python", monaco: "python", installed: true, install_hint: "" },
  { id: "typescript", label: "TypeScript", monaco: "typescript", installed: true, install_hint: "" },
  { id: "javascript", label: "JavaScript", monaco: "javascript", installed: true, install_hint: "" },
  {
    id: "cpp",
    label: "C++",
    monaco: "cpp",
    installed: false,
    install_hint: "Install g++ and restart (mock backend: this one is deliberately missing).",
  },
];

/** Progress rows are created on first write, the way an upsert would. */
function masteryRow(trackKey: string, week: number): MasteryProgress {
  const key = `${trackKey}:${week}`;
  let row = state.mastery[key] as MasteryProgress | undefined;
  if (!row) {
    row = {
      track_key: trackKey,
      week,
      best_quiz: -1,
      exam_passed: false,
      exam_code: "",
      project_notes: "",
      project_code: "",
      project_done: false,
      study_seconds: 0,
      started_at: isoStamp(0),
      completed_at: null,
    };
    state.mastery[key] = row;
  }
  return row;
}

type Args = Record<string, any>;

const handlers: Record<string, (a: Args) => any | Promise<any>> = {
  /* ---- content ---- */
  list_problems: () => problems(),
  get_problem: async ({ id }) => (await problems()).find((p) => p.id === id) ?? null,
  random_problem: async ({ difficulty, topic }) => {
    const all = await problems();
    const pool = all.filter(
      (p) =>
        p.solved_status !== "solved" &&
        (!difficulty || p.difficulty === difficulty) &&
        (!topic || p.topics.includes(topic))
    );
    return pool[Math.floor(Math.random() * pool.length)] ?? null;
  },
  distinct_tags: async ({ kind }) => {
    const all = await problems();
    const key = kind === "topic" ? "topics" : kind === "subtopic" ? "subtopics" : "companies";
    return [...new Set(all.flatMap((p) => (p as any)[key] as string[]))].sort();
  },
  concepts: () => seed("concepts"),
  dsa_curriculum: () => seed("dsa_curriculum"),
  ts_course: () => seed("ts_course"),
  java_course: () => seed("java_course"),
  backend_track: () => seed("backend_course"),
  projects_track: () => seed("projects"),
  mastery: () => seed("mastery"),
  jp_bridge: () => seed("jp_bridge"),
  jp_vocab: () => seed("jp_vocab"),
  sql_datasets: () => seed("sql_datasets"),
  list_flashcards: () => seed("flashcards"),
  due_flashcards: async () => ((await seed("flashcards")) ?? []).slice(0, 8),
  list_paths: () => [],
  languages: () => LANGUAGES,
  // The real command drops a process-wide probe cache and re-runs it; with
  // no toolchains to probe, the honest fixture is the same list back.
  redetect_languages: () => LANGUAGES,

  /* ---- per-problem state ---- */
  set_favorite: ({ id, favorite }) => {
    state.favorites[id] = favorite;
    save();
  },
  set_confidence: ({ id, confidence }) => {
    state.confidence[id] = confidence;
    save();
  },
  get_note: ({ problemId }): Note => ({
    problem_id: problemId,
    content: state.notes[problemId] ?? "",
    updated_at: isoStamp(0),
  }),
  save_note: ({ problemId, content }) => {
    state.notes[problemId] = content;
    save();
  },
  get_draft: ({ problemId, language }) => state.drafts[`${problemId}:${language}`] ?? null,
  save_draft: ({ problemId, language, code }) => {
    state.drafts[`${problemId}:${language}`] = code;
    save();
  },
  get_hints_revealed: ({ problemId }) => state.hints[problemId] ?? 0,
  set_hints_revealed: ({ problemId, count }) => {
    state.hints[problemId] = count;
    save();
  },
  known_prereqs: ({ problemId }) => {
    // Deterministic: about half of a problem's prerequisites read as known.
    return (state.settings[`prereq:${problemId}`] ?? "").split(",").filter(Boolean);
  },
  set_prereq_status: ({ problemId, key, known }) => {
    const cur = new Set((state.settings[`prereq:${problemId}`] ?? "").split(",").filter(Boolean));
    known ? cur.add(key) : cur.delete(key);
    state.settings[`prereq:${problemId}`] = [...cur].join(",");
    save();
  },
  list_test_cases: async ({ problemId }) =>
    (await problems()).find((p) => p.id === problemId)?.test_cases ?? [],
  save_test_case: () => state.nextId++,
  delete_test_case: () => {},
  list_solutions: ({ problemId }) => state.solutions[problemId] ?? [],
  save_solution: ({ solution }) => {
    const list = (state.solutions[solution.problem_id] ??= []);
    const id = solution.id || state.nextId++;
    const row = { ...solution, id, created_at: isoStamp(0), updated_at: isoStamp(0) };
    const at = list.findIndex((s) => s.id === id);
    at >= 0 ? (list[at] = row) : list.push(row);
    save();
    return id;
  },
  delete_solution: ({ id }) => {
    for (const k of Object.keys(state.solutions)) {
      state.solutions[+k] = state.solutions[+k].filter((s) => s.id !== id);
    }
    save();
  },
  list_attempts: ({ problemId }) => state.attempts[problemId] ?? [],
  list_mistakes: ({ problemId }) => state.mistakes[problemId] ?? [],
  add_mistake: ({ mistake }) => {
    const id = state.nextId++;
    (state.mistakes[mistake.problem_id] ??= []).unshift({
      ...mistake,
      id,
      created_at: isoStamp(0),
    });
    save();
    return id;
  },
  delete_mistake: ({ id }) => {
    for (const k of Object.keys(state.mistakes)) {
      state.mistakes[+k] = state.mistakes[+k].filter((m) => m.id !== id);
    }
    save();
  },

  /* ---- execution ---- */
  run_tests: ({ code, cases }): JudgeReport => fakeJudge(code, cases ?? []),
  run_scratch: ({ code }): ProcOut => ({
    stdout:
      "(mock backend)\nNo code was executed — this fixture fakes the judge so the\n" +
      "UI can be driven in a browser. Run the Tauri app for real output.\n",
    stderr: "",
    exit_code: 0,
    timed_out: false,
    runtime_ms: 12 + (hash(code) % 30),
    memory_kb: 13400,
    truncated: false,
  }),
  submit: ({ problemId, language, code }): JudgeReport => {
    const report = fakeJudge(code, []);
    const cases = (problemCache?.find((p) => p.id === problemId)?.test_cases ?? []) as TestCase[];
    const real = fakeJudge(code, cases);
    const id = state.nextId++;
    (state.attempts[problemId] ??= []).unshift({
      id,
      problem_id: problemId,
      language,
      code,
      status: real.status === "accepted" ? "accepted" : "wrong",
      runtime_ms: real.runtime_ms,
      memory_kb: real.memory_kb,
      passed: real.passed,
      total: real.total,
      error_text: "",
      duration_seconds: 600,
      created_at: isoStamp(0),
    });
    if (real.status === "accepted") state.solved[problemId] = "solved";
    else if (!state.solved[problemId]) state.solved[problemId] = "attempted";
    save();
    return real.total > 0 ? real : report;
  },

  /* ---- progress across the tracks ---- */
  done_chapters: () => state.chapters,
  set_chapter_done: ({ key, done }) => {
    const s = new Set(state.chapters);
    done ? s.add(key) : s.delete(key);
    state.chapters = [...s];
    save();
  },
  solved_exercises: () => state.exercises,
  set_exercises_solved: ({ ids, solved }) => {
    const s = new Set(state.exercises);
    for (const k of ids ?? []) solved ? s.add(k) : s.delete(k);
    state.exercises = [...s];
    save();
  },
  card_reviews: () => Object.values(state.cards),
  grade_card: ({ cardId, quality }): CardReview => {
    const prev = state.cards[cardId];
    const reps = (prev?.reps ?? 0) + 1;
    const interval = quality >= 3 ? Math.min(90, Math.max(1, (prev?.interval_days ?? 0) * 2 || 1)) : 1;
    const row: CardReview = {
      card_id: cardId,
      ease: prev?.ease ?? 2.5,
      reps,
      lapses: (prev?.lapses ?? 0) + (quality < 3 ? 1 : 0),
      interval_days: interval,
      due_date: isoDay(interval),
      last_quality: quality,
    };
    state.cards[cardId] = row;
    save();
    return row;
  },
  reset_cards: ({ cardIds }) => {
    for (const id of cardIds ?? []) delete state.cards[id];
    save();
  },
  merge_card_reviews: () => 0,
  // Returns every row at once (no arguments) — the page joins them to the
  // curriculum itself.
  mastery_progress: () => Object.values(state.mastery),
  mastery_record_quiz: ({ trackKey, week, percent }) => {
    const row = masteryRow(trackKey, week);
    row.best_quiz = Math.max(row.best_quiz, percent);
    save();
  },
  mastery_record_exam: ({ trackKey, week, passed, code }) => {
    const row = masteryRow(trackKey, week);
    row.exam_passed = row.exam_passed || passed;
    row.exam_code = code;
    save();
  },
  mastery_save_project: ({ trackKey, week, notes, code, done }) => {
    const row = masteryRow(trackKey, week);
    row.project_notes = notes;
    row.project_code = code;
    row.project_done = done;
    save();
  },
  mastery_log_time: ({ trackKey, week, seconds }) => {
    masteryRow(trackKey, week).study_seconds += seconds;
    save();
  },
  mastery_complete_week: ({ trackKey, week }) => {
    const row = masteryRow(trackKey, week);
    const first = !row.completed_at;
    row.completed_at = isoStamp(0);
    save();
    return first;
  },
  // Checkpoints: the same resume-a-running-one rule as the real command.
  mastery_start_contest: async ({ trackKey, week }) => {
    const track = ((await seed("mastery")) as MasteryTrack[]).find((t) => t.key === trackKey);
    const w = track?.weeks.find((x) => x.week === week);
    if (!w?.contest) throw new Error("week checkpoint contest not found");
    const running = Object.values(state.contests).find(
      (c) => c.title === w.contest!.title && c.status === "running"
    );
    if (running) return running.id;
    const slugs = w.contest.slugs?.length ? w.contest.slugs : w.problems.map((p) => p.slug);
    const all = await problems();
    const picked = slugs
      .map((s) => all.find((p) => p.slug === s))
      .filter((p): p is Problem => p !== undefined);
    const id = state.nextId++;
    state.contests[id] = {
      id,
      title: w.contest.title,
      problem_ids: picked.map((p) => p.id),
      duration_seconds: w.contest.duration_seconds,
      status: "running",
      started_at: new Date().toISOString().slice(0, 19).replace("T", " "),
      ended_at: null,
      results: picked.map((p) => ({
        problem_id: p.id,
        title: p.title,
        difficulty: p.difficulty,
        solved: false,
        solved_at: null,
        wrong_tries: 0,
      })),
    };
    save();
    return id;
  },
  contest: ({ id }) => {
    const c = state.contests[id];
    if (!c) throw new Error("contest not found");
    return c;
  },
  record_contest_result: ({ contestId, problemId, solved }) => {
    const r = state.contests[contestId]?.results.find((x) => x.problem_id === problemId);
    if (!r) return;
    if (solved) {
      r.solved = true;
      r.solved_at = r.solved_at ?? new Date().toISOString();
    } else if (!r.solved) {
      r.wrong_tries += 1;
    }
    save();
  },
  finish_contest: ({ id }) => {
    const c = state.contests[id];
    if (c) {
      c.status = "finished";
      c.ended_at = new Date().toISOString();
      save();
    }
  },

  /* ---- aggregates ---- */
  dashboard,
  statistics,
  learning_recommendations: recommendations,
  timeline: () =>
    Array.from({ length: 84 }, (_, i) => {
      const day = isoDay(-83 + i);
      return { label: day, value: rand(day) < 0.3 ? 0 : Math.ceil(rand(day) * 6) };
    }),
  due_reviews: () => [],
  mark_reviewed: () => {},
  grade_review: () => {},
  reschedule_review: () => {},
  log_study_time: ({ seconds }) => {
    state.studySeconds += seconds;
    save();
  },

  /* ---- settings and files ---- */
  get_settings: () => ({ ...state.settings }),
  set_setting: ({ key, value }) => {
    state.settings[key] = value;
    save();
  },
  export_problems: async () => JSON.stringify(await problems(), null, 2),
  import_problems: () => 0,
  read_file: () => "",
  write_file: () => {},
  backup_database: () => {},
  restore_database: () => {},

  /* ---- SQL playground ---- */
  sql_query: () => ({
    columns: ["(mock)"],
    rows: [["The SQL engine only runs in the desktop app."]],
    error: "",
    row_count: 1,
  }),
  sql_tables: () => [],
};

/* ------------------------------------------------------------- the shim */

let warned = false;

async function mockInvoke(cmd: string, args: Args = {}): Promise<any> {
  const fn = handlers[cmd];
  if (!fn) {
    // An unmocked command is a gap in the fixture, not a crash. Say so once per
    // command and answer `null`, which every caller already tolerates.
    console.warn(`[mock] no handler for "${cmd}" — returning null`, args);
    return null;
  }
  if (!warned) {
    warned = true;
    console.info(
      "%c[mock backend]%c Poodcode is running on fixtures, not SQLite. Progress is invented and nothing is executed. Call resetMockState() to clear.",
      "color:#4c8dff;font-weight:700",
      "color:inherit"
    );
  }
  // A small delay makes the loading states real: skeletons, spinners and
  // request races all show up here the way they do against the database.
  await new Promise((r) => setTimeout(r, 40 + Math.random() * 80));
  return fn(args);
}

export function installMockBackend() {
  load();
  (window as any).__TAURI_INTERNALS__ = {
    invoke: mockInvoke,
    transformCallback: (cb: unknown) => cb,
    convertFileSrc: (p: string) => p,
  };
  (window as any).resetMockState = resetMockState;
  document.documentElement.dataset.mockBackend = "1";
}
