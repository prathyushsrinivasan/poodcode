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
  language: string;
  starter: string;
  solution: string;
  tests: ExerciseTest[];
  source_slug: string;
}

export interface Card {
  front: string;
  reading: string;
  meaning: string;
  example_ja: string;
  example_en: string;
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
