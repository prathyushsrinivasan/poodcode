// Data models mirror the Rust serde structs (snake_case field names).

export type Difficulty = "Intro" | "Easy" | "Medium" | "Hard";
export type SolvedStatus = "unsolved" | "attempted" | "solved";

export interface Example {
  input: string;
  output: string;
  explanation: string;
}

export interface Prerequisite {
  key: string;
  name: string;
  what: string;
  deep: string;
  java: string;
  how: string;
}

export interface Param {
  name: string;
  type: string;
}
export interface FunctionSpec {
  name: string;
  params: Param[];
  returns: string;
}
export interface Editorial {
  title: string;
  body: string;
  time: string;
  space: string;
}
export interface FollowUp {
  slug: string;
  title: string;
  note: string;
}

export interface ExerciseTest {
  input: string;
  output: string;
}
export interface Exercise {
  id: string;
  title: string;
  prompt: string;
  hint: string;
  /** Progressive hint ladder; falls back to `hint` when empty. */
  hints: string[];
  language: string;
  /** "drill" (fill-in-the-blank, default), "challenge" (full coding problem),
   * or "fix" (a complete but buggy program the learner corrects). */
  kind: string;
  /** Suggested difficulty for a challenge: "Intro" | "Easy" | "Medium". */
  difficulty: string;
  starter: string;
  solution: string;
  tests: ExerciseTest[];
  source_slug: string;
  /** SQL track only: key of the {@link SqlDataset} this exercise queries. The
   * dataset's SQL is prepended to each test's `input` (which holds only that
   * case's variation on the data) before the query runs. */
  dataset: string;
}

// --- SQL track (seeds/sql_datasets.json + the in-process SQL engine) --------

/** A ready-made database the SQL exercises are judged against. Replayed into a
 * fresh in-memory SQLite database before every run. */
export interface SqlDataset {
  key: string;
  title: string;
  summary: string;
  /** Markdown: what the tables mean and which quirks were planted in the data. */
  story: string;
  sql: string;
}

/** One result set, structured for the table view. */
export interface SqlGrid {
  columns: string[];
  rows: string[][];
  truncated: boolean;
}

/** The outcome of running SQL against a dataset (the "Run query" button). */
export interface SqlOut {
  grid: SqlGrid | null;
  /** `grid` rendered as the text the judge compares. */
  text: string;
  error: string;
  /** True when the failure was at compile time (syntax, unknown table/column). */
  syntax_error: boolean;
  timed_out: boolean;
  row_count: number;
  statements: number;
  runtime_ms: number;
}

export interface SqlColumn {
  name: string;
  decl_type: string;
  not_null: boolean;
  primary_key: boolean;
}

/** One table of a dataset, as the schema browser shows it. */
export interface SqlTable {
  name: string;
  ddl: string;
  columns: SqlColumn[];
  rows: string[][];
  row_count: number;
  truncated: boolean;
}

export interface Card {
  front: string;
  reading: string;
  meaning: string;
  example_ja: string;
  example_en: string;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  /** 0-based index into `options`. */
  answer: number;
  explanation: string;
}

export interface PracticeRef {
  slug: string;
  note: string;
}

export interface BridgeProblem {
  slug: string;
  title_ja: string;
  statement_ja: string;
  io_ja: string;
  vocab: string[][];
  hint_ja: string;
}

export interface InterviewQA {
  q_ja: string;
  q_en: string;
  a_ja: string;
  a_en: string;
  tags: string[];
}

export interface JpBridge {
  problems: BridgeProblem[];
  interview: InterviewQA[];
}

// --- TypeScript course (8-month structured curriculum) ---------------------
export interface GlossaryItem {
  term: string;
  def: string;
}
export interface Capstone {
  title: string;
  brief: string;
  /** "auto" = judged via `exercise`; "brief" = free build, self-marked. */
  kind: string;
  exercise: Exercise | null;
  example_io: string;
  rubric: string[];
  reference: string;
  stretch: Exercise | null;
}
export interface CourseLesson {
  key: string;
  title: string;
  what: string;
  lesson: string;
  /** "What does this print?" warm-up shown before the drills. */
  warmup: QuizQuestion[];
  exercises: Exercise[];
  quiz: QuizQuestion[];
}
/** Several variants of ONE pattern, drilled back to back. `intro` walks through
 * the base case so each variant is a twist on something already shown. Practice
 * is not counted towards completing a unit — see `requiredExerciseIds`. */
export interface PracticeFamily {
  key: string;
  title: string;
  /** One line naming the motion being drilled. */
  pattern: string;
  /** Markdown walkthrough of the base pattern, shown above the variants. */
  intro: string;
  exercises: Exercise[];
}
export interface CourseWeek {
  number: number;
  month: number;
  month_title: string;
  theme: string;
  goal: string;
  summary: string;
  /** false = skeleton placeholder ("coming soon"). */
  authored: boolean;
  lessons: CourseLesson[];
  capstone: Capstone | null;
  objectives: string[];
  why: string;
  est_minutes: number;
  glossary: GlossaryItem[];
  cheatsheet: string;
  self_check: string[];
  review: QuizQuestion[];
  milestone: string;
  /** Optional bulk variation drilling. Empty for tracks that ship none. */
  practice: PracticeFamily[];
}
/** A structured course: numbered units, each with lessons and a capstone.
 * Two ship and share this shape — the TypeScript course (Weeks inside Months)
 * and the Java course (Modules inside Parts) — so the course itself carries
 * the labels the UI should use. */
export interface WeeklyCourse {
  key: string;
  title: string;
  subtitle: string;
  /** What one unit is called; empty means "Week". */
  unit_label: string;
  /** What a group of units is called; empty means "Month". */
  group_label: string;
  weeks: CourseWeek[];
}

// --- Backend Lab (seeds/backend_course.json) -------------------------------
// A project-based track: every project is a working CRUD HTTP server you build
// from scratch with Node built-ins only. Steps carry the instructions and a
// checkpoint; exercises reuse the same judge as everywhere else.

/** One row of a project's API contract. */
export interface Endpoint {
  method: string;
  path: string;
  purpose: string;
  /** Request body shape, or "" for none. */
  request: string;
  response: string;
  /** Status codes this endpoint can return, e.g. "201 · 400". */
  status: string;
}

export interface BackendStep {
  key: string;
  title: string;
  what: string;
  /** Markdown: what to do in this step. */
  instructions: string;
  /** Markdown: the observable result that proves the step is done. */
  checkpoint: string;
  pitfalls: string[];
  warmup: QuizQuestion[];
  exercises: Exercise[];
  quiz: QuizQuestion[];
}

export interface BackendProject {
  key: string;
  number: number;
  title: string;
  tagline: string;
  /** "Starter" | "Core" | "Advanced". */
  level: string;
  goal: string;
  why: string;
  /** false = planned placeholder ("coming soon"). */
  authored: boolean;
  est_minutes: number;
  /** Keys of the projects this one continues from. */
  builds_on: string[];
  concepts: string[];
  objectives: string[];
  brief: string;
  endpoints: Endpoint[];
  setup: string;
  steps: BackendStep[];
  /** The judged "now build the whole thing" exercise closing the project. */
  final_build: Exercise | null;
  acceptance: string[];
  manual_test: string;
  reference: string;
  stretch: string[];
  glossary: GlossaryItem[];
  cheatsheet: string;
  self_check: string[];
  review: QuizQuestion[];
  milestone: string;
}

export interface BackendTrack {
  key: string;
  title: string;
  subtitle: string;
  intro: string;
  /** The stdin request-script format the judged exercises are driven by. */
  harness_note: string;
  projects: BackendProject[];
}

// --- 6-Month Mastery programme (seeds/mastery.json) ------------------------
// The Learn catalog is a reference library; a mastery track sequences it into
// weeks. Content is read-only — progress lives in localStorage (lib/mastery.ts).

export interface MasteryProblem {
  slug: string;
  note: string;
}

/** The week's coding final, judged exactly like a Learn challenge. */
export interface MasteryExam {
  title: string;
  prompt: string;
  hint: string;
  language: string;
  starter: string;
  solution: string;
  tests: ExerciseTest[];
}

/** An optional timed checkpoint built from the week's problems. */
export interface MasteryContest {
  title: string;
  duration_seconds: number;
}

export interface MasteryWeek {
  /** 1-based; weeks are numbered 1..N with no gaps. */
  week: number;
  /** Month / phase label, used to group the week list. */
  phase: string;
  title: string;
  goal: string;
  /** Concept keys, resolved against the Learn catalog. */
  concepts: string[];
  problems: MasteryProblem[];
  /** Free-text build brief; the learner's notes and code are stored per week. */
  project: string;
  /** The end-of-week question BANK — the UI samples and shuffles from it. */
  quiz: QuizQuestion[];
  /** How many bank questions make one sitting of the exam. */
  quiz_sample: number;
  exam: MasteryExam | null;
  contest: MasteryContest | null;
}

export interface MasteryTrack {
  key: string;
  title: string;
  /** Learn-catalog language whose concepts this track schedules. */
  language: string;
  subtitle: string;
  intro: string;
  /** Percentage of the week's quiz required to unlock the next week. */
  pass_mark: number;
  /** Language the coding finals are written in. */
  exam_language: string;
  weeks: MasteryWeek[];
}

/** Per-week learner state, persisted in SQLite (table `mastery_progress`). */
export interface MasteryProgress {
  track_key: string;
  week: number;
  /** Best multiple-choice percentage; -1 when never attempted. */
  best_quiz: number;
  exam_passed: boolean;
  exam_code: string;
  project_notes: string;
  project_code: string;
  project_done: boolean;
  study_seconds: number;
  started_at: string | null;
  completed_at: string | null;
}

export interface CardReview {
  card_id: string;
  ease: number;
  reps: number;
  lapses: number;
  interval_days: number;
  due_date: string;
  last_quality: number;
}

export interface Concept {
  key: string;
  name: string;
  category: string;
  what: string;
  deep: string;
  java: string;
  language: string;
  lesson: string;
  exercises: Exercise[];
  cards: Card[];
  quiz: QuizQuestion[];
  practice: PracticeRef[];
}

export interface TestCase {
  id: number;
  problem_id: number;
  kind: "hidden" | "user" | "example";
  name: string;
  input: string;
  expected_output: string;
  ordering: number;
}

export interface Problem {
  id: number;
  slug: string;
  title: string;
  difficulty: Difficulty;
  description: string;
  constraints: string;
  examples: Example[];
  editorial: string;
  optimal_time: string;
  optimal_space: string;
  optimal_explanation: string;
  starter_code: Record<string, string>;
  topics: string[];
  subtopics: string[];
  companies: string[];
  patterns: string[];
  hints: string[];
  prerequisites: Prerequisite[];
  test_cases: TestCase[];
  function_spec: FunctionSpec | null;
  judge_mode: string;
  float_tolerance: number;
  checker: string;
  time_limit_ms: number;
  editorials: Editorial[];
  follow_ups: FollowUp[];
  order: number;
  is_favorite: boolean;
  solved_status: SolvedStatus;
  confidence: number;
  last_solved_at: string | null;
  time_taken_seconds: number;
  attempts_count: number;
  success_count: number;
  created_at: string;
  updated_at: string;
}

export interface Note {
  problem_id: number;
  content: string;
  updated_at: string;
}

export interface Solution {
  id: number;
  problem_id: number;
  title: string;
  language: string;
  code: string;
  time_complexity: string;
  space_complexity: string;
  approach_kind: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface Attempt {
  id: number;
  problem_id: number;
  language: string;
  code: string;
  status: "accepted" | "wrong" | "error" | "run";
  runtime_ms: number | null;
  memory_kb: number | null;
  passed: number;
  total: number;
  error_text: string;
  duration_seconds: number;
  created_at: string;
}

export interface Review {
  id: number;
  problem_id: number;
  due_date: string;
  interval_index: number;
  ease: number;
  reps: number;
  lapses: number;
  interval_days: number;
  last_quality: number;
  last_reviewed_at: string | null;
  created_at: string;
}

export interface Mistake {
  id: number;
  problem_id: number;
  attempt_id: number | null;
  category: string;
  note: string;
  created_at: string;
}

export interface PathItem {
  problem_id: number;
  title: string;
  difficulty: Difficulty;
  solved_status: SolvedStatus;
  ordering: number;
}
export interface Path {
  id: number;
  key: string;
  title: string;
  description: string;
  ordering: number;
  items: PathItem[];
}

export interface ContestResult {
  problem_id: number;
  title: string;
  difficulty: Difficulty;
  solved: boolean;
  solved_at: string | null;
  wrong_tries: number;
}
export interface Contest {
  id: number;
  title: string;
  problem_ids: number[];
  duration_seconds: number;
  status: string;
  started_at: string;
  ended_at: string | null;
  results: ContestResult[];
}

export interface Flashcard {
  id: number;
  front: string;
  back: string;
  source: string;
  ease: number;
  reps: number;
  lapses: number;
  interval_days: number;
  due_date: string;
  created_at: string;
}

export interface ReviewItem {
  review: Review;
  problem_id: number;
  title: string;
  difficulty: Difficulty;
  confidence: number;
  topics: string[];
}

export interface LangInfo {
  id: string;
  label: string;
  monaco: string;
  installed: boolean;
  install_hint: string;
}

export interface CaseResult {
  name: string;
  kind: string;
  input: string;
  expected: string;
  actual: string;
  stderr: string;
  passed: boolean;
  timed_out: boolean;
  runtime_ms: number;
  memory_kb: number | null;
  truncated: boolean;
  verdict: string; // "pass" | "wrong" | "tle" | "re" | "trunc"
}

export interface JudgeReport {
  status: "accepted" | "wrong" | "error" | "not_installed" | "tle";
  passed: number;
  total: number;
  runtime_ms: number;
  memory_kb: number | null;
  compile_error: string;
  not_installed_hint: string;
  results: CaseResult[];
}

export interface ProcOut {
  stdout: string;
  stderr: string;
  exit_code: number | null;
  timed_out: boolean;
  runtime_ms: number;
  memory_kb: number | null;
  truncated: boolean;
}

export interface ConceptRef {
  key: string;
  name: string;
}
export interface ProblemRef {
  id: number;
  title: string;
  difficulty: Difficulty;
  solved_status: SolvedStatus;
  confidence: number;
}
export interface TopicRecommendation {
  topic: string;
  solved: number;
  total: number;
  avg_confidence: number;
  concepts: ConceptRef[];
  problems: ProblemRef[];
}

export interface Goals {
  intro: number;
  easy: number;
  medium: number;
  hard: number;
  reviews: number;
}

export interface Dashboard {
  solved_today: number;
  study_seconds_today: number;
  reviews_due: number;
  current_streak: number;
  weakest_topic: string | null;
  suggested_problem: Problem | null;
  goals: Goals;
  goal_progress: Goals;
  total_problems: number;
  total_solved: number;
}

export interface DiffCount {
  total: number;
  solved: number;
}
export interface TopicStat {
  topic: string;
  total: number;
  solved: number;
  avg_confidence: number;
}
export interface CountPair {
  label: string;
  value: number;
}
export interface HeatCell {
  date: string;
  count: number;
}

export interface Stats {
  total_problems: number;
  total_solved: number;
  by_difficulty: Record<string, DiffCount>;
  by_topic: TopicStat[];
  avg_solve_seconds: number;
  acceptance_rate: number;
  current_streak: number;
  longest_streak: number;
  language_usage: CountPair[];
  heatmap: HeatCell[];
  weekly_activity: CountPair[];
  monthly_activity: CountPair[];
  weakest_topics: TopicStat[];
  strongest_topics: TopicStat[];
  first_attempt_rate: number;
  retention_rate: number;
  avg_tries_to_solve: number;
  reviews_total: number;
  mistake_tally: CountPair[];
  topic_behavior: TopicBehavior[];
}

export interface TopicBehavior {
  topic: string;
  solved: number;
  first_try_solved: number;
  first_try_rate: number;
  avg_hints_used: number;
  mastery: number;
}
