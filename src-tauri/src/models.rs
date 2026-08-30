use serde::{Deserialize, Serialize};

/// A teachable concept for the Learn section. Shipped as a bundled catalog
/// (seeds/concepts.json) and surfaced independently of any single problem.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Concept {
    pub key: String,
    pub name: String,
    #[serde(default)]
    pub category: String,
    #[serde(default)]
    pub what: String,
    #[serde(default)]
    pub deep: String,
    #[serde(default)]
    pub java: String,
    /// Which language this concept teaches ("java" | "typescript"). Drives the
    /// Learn-tab language toggle. Empty is treated as "java" by the frontend.
    #[serde(default)]
    pub language: String,
    /// Full Markdown lesson (worked example, code, pitfalls).
    #[serde(default)]
    pub lesson: String,
    /// Half-coded fill-in-the-blank drills for this concept (Learn tab).
    #[serde(default)]
    pub exercises: Vec<Exercise>,
    /// Structured vocabulary cards for flashcard study (Japanese track). Empty
    /// for code concepts, which teach via `lesson` + `exercises` instead.
    #[serde(default)]
    pub cards: Vec<Card>,
    /// Multiple-choice self-check questions (language-agnostic Algorithms
    /// track). Graded client-side by option index — no code execution. Empty
    /// for concepts that teach through code drills instead.
    #[serde(default)]
    pub quiz: Vec<QuizQuestion>,
    /// Curated real Library problems to practice this concept on. Resolved to a
    /// problem by `slug` in the frontend, so the lesson can hand the learner
    /// straight into the solver. Empty when there is nothing linked.
    #[serde(default)]
    pub practice: Vec<PracticeRef>,
}

/// One multiple-choice question for a concept's self-check quiz. `answer` is the
/// 0-based index into `options`; `explanation` is shown after the learner picks.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuizQuestion {
    pub question: String,
    #[serde(default)]
    pub options: Vec<String>,
    #[serde(default)]
    pub answer: i64,
    #[serde(default)]
    pub explanation: String,
}

/// A pointer from a concept to a real Library problem to practice it on.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PracticeRef {
    pub slug: String,
    #[serde(default)]
    pub note: String,
}

/// One vocabulary flashcard: a term on the front, its reading / meaning /
/// example on the back. Populated only for reference concepts (Japanese track).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Card {
    pub front: String,
    #[serde(default)]
    pub reading: String,
    #[serde(default)]
    pub meaning: String,
    #[serde(default)]
    pub example_ja: String,
    #[serde(default)]
    pub example_en: String,
}

/// A single stdin/stdout check for a concept exercise.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExerciseTest {
    pub input: String,
    pub output: String,
}

/// A "half-coded" drill: the learner is shown `starter` (a full Java program
/// with a `____` blank) and types back the one piece the lesson teaches. The
/// completed program is judged against `tests`; `solution` is the reveal-able
/// correct answer and the reference proven by tests/verify_exercises.rs.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Exercise {
    pub id: String,
    pub title: String,
    pub prompt: String,
    #[serde(default)]
    pub hint: String,
    /// Progressive hint ladder (nudge → strategy → near-answer). When present the
    /// UI reveals one at a time; falls back to the single `hint` when empty.
    #[serde(default)]
    pub hints: Vec<String>,
    #[serde(default)]
    pub language: String,
    /// "drill" (short fill-in-the-blank, the default) or "challenge" (a fuller,
    /// self-contained coding problem scoped to the syllabus so far). Empty is
    /// treated as "drill" by the frontend.
    #[serde(default)]
    pub kind: String,
    /// Suggested difficulty for a challenge ("Intro" | "Easy" | "Medium").
    /// Empty for plain drills.
    #[serde(default)]
    pub difficulty: String,
    pub starter: String,
    pub solution: String,
    pub tests: Vec<ExerciseTest>,
    /// Optional Library problem slug this drill leads into (advanced concepts).
    #[serde(default)]
    pub source_slug: String,
    /// SQL track only: the key of the [`SqlDataset`] this exercise queries. The
    /// dataset's DDL + rows are prepended to each test's `input` (which then
    /// holds only that case's *variation* on the data), so a schema shared by a
    /// whole chapter is stored once instead of once per exercise.
    #[serde(default)]
    pub dataset: String,
}

/// A ready-made database for the SQL track: schema plus rows, as one batch of
/// SQL that `sqlexec` replays into a fresh in-memory database before every run.
///
/// Datasets are shared across chapters on purpose. Re-meeting the same customers
/// and orders in the joins chapter, the window-functions chapter and the
/// performance chapter means the learner spends their attention on the technique
/// rather than on re-reading a new schema each time.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SqlDataset {
    pub key: String,
    pub title: String,
    /// One line describing what is in here, shown on the dataset chip.
    #[serde(default)]
    pub summary: String,
    /// Markdown: what the tables mean and which quirks were planted in the data
    /// (orphan rows, NULLs, ties) so the exercises have something to bite on.
    #[serde(default)]
    pub story: String,
    /// The full `CREATE TABLE` + `INSERT` batch.
    pub sql: String,
}

/// A coding problem. `topics`, `subtopics` and `companies` are denormalized on
/// read for the frontend; they are stored normalized via the `tags` tables.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Problem {
    #[serde(default)]
    pub id: i64,
    pub slug: String,
    pub title: String,
    pub difficulty: String, // "Easy" | "Medium" | "Hard"
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub constraints: String,
    /// Worked examples shown in the statement (input/output/explanation).
    #[serde(default)]
    pub examples: Vec<Example>,
    #[serde(default)]
    pub editorial: String,
    #[serde(default)]
    pub optimal_time: String,
    #[serde(default)]
    pub optimal_space: String,
    #[serde(default)]
    pub optimal_explanation: String,
    #[serde(default)]
    pub starter_code: std::collections::HashMap<String, String>,
    #[serde(default)]
    pub topics: Vec<String>,
    #[serde(default)]
    pub subtopics: Vec<String>,
    #[serde(default)]
    pub companies: Vec<String>,
    #[serde(default)]
    pub hints: Vec<String>,
    #[serde(default)]
    pub prerequisites: Vec<Prerequisite>,
    #[serde(default)]
    pub test_cases: Vec<TestCase>,
    // Rich judging + curriculum (all optional, back-compatible)
    #[serde(default)]
    pub patterns: Vec<String>,
    #[serde(default)]
    pub function_spec: Option<FunctionSpec>,
    #[serde(default = "default_judge_mode")]
    pub judge_mode: String, // "exact" | "float" | "unordered"
    #[serde(default)]
    pub float_tolerance: f64,
    /// Special-judge checker (Python `def check(input, output) -> bool`); empty = exact/mode.
    #[serde(default)]
    pub checker: String,
    #[serde(default)]
    pub time_limit_ms: i64, // 0 = global default
    #[serde(default)]
    pub editorials: Vec<Editorial>,
    #[serde(default)]
    pub follow_ups: Vec<FollowUp>,
    /// Curated global rank for easiest→hardest ordering in the library.
    #[serde(default)]
    pub order: i64,
    // Progress / metadata
    #[serde(default)]
    pub is_favorite: bool,
    #[serde(default = "default_status")]
    pub solved_status: String, // "unsolved" | "attempted" | "solved"
    #[serde(default)]
    pub confidence: i64, // 0..=5 (0 = none)
    #[serde(default)]
    pub last_solved_at: Option<String>,
    #[serde(default)]
    pub time_taken_seconds: i64,
    #[serde(default)]
    pub attempts_count: i64,
    #[serde(default)]
    pub success_count: i64,
    #[serde(default)]
    pub created_at: String,
    #[serde(default)]
    pub updated_at: String,
}

fn default_status() -> String {
    "unsolved".to_string()
}

fn default_judge_mode() -> String {
    "exact".to_string()
}

/// A function-harness signature. When present, the app wraps the user's function
/// with generated I/O glue: the test-case `input` holds the arguments (one JSON
/// value per line) and `expected_output` holds the serialized return value.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FunctionSpec {
    pub name: String,
    #[serde(default)]
    pub params: Vec<Param>,
    #[serde(default)]
    pub returns: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Param {
    pub name: String,
    #[serde(rename = "type")]
    pub ty: String,
}

/// One authored approach to a problem (brute force → optimal), with its cost.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Editorial {
    pub title: String,
    #[serde(default)]
    pub body: String,
    #[serde(default)]
    pub time: String,
    #[serde(default)]
    pub space: String,
}

/// A linked follow-up / variant problem.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FollowUp {
    #[serde(default)]
    pub slug: String,
    pub title: String,
    #[serde(default)]
    pub note: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Example {
    #[serde(default)]
    pub input: String,
    #[serde(default)]
    pub output: String,
    #[serde(default)]
    pub explanation: String,
}

/// A concept the solver should understand before attempting the problem.
/// `what` explains the concept in general; `how` explains why it matters for
/// *this specific* problem. `key` is a stable slug used to remember whether the
/// user has checked it off (per problem).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Prerequisite {
    #[serde(default)]
    pub key: String,
    pub name: String,
    /// One-sentence gist of the concept.
    #[serde(default)]
    pub what: String,
    /// Deeper explanation: mechanics, complexity, when to reach for it, pitfalls.
    #[serde(default)]
    pub deep: String,
    /// Java-specific guidance: the concrete classes/APIs and idioms to use.
    #[serde(default)]
    pub java: String,
    /// How this concept specifically helps solve *this* problem.
    #[serde(default)]
    pub how: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestCase {
    #[serde(default)]
    pub id: i64,
    #[serde(default)]
    pub problem_id: i64,
    /// "hidden" | "user" | "example"
    #[serde(default = "default_kind")]
    pub kind: String,
    #[serde(default)]
    pub name: String,
    pub input: String,
    pub expected_output: String,
    #[serde(default)]
    pub ordering: i64,
}

fn default_kind() -> String {
    "user".to_string()
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Note {
    #[serde(default)]
    pub problem_id: i64,
    #[serde(default)]
    pub content: String,
    #[serde(default)]
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Solution {
    #[serde(default)]
    pub id: i64,
    pub problem_id: i64,
    pub title: String,
    pub language: String,
    pub code: String,
    #[serde(default)]
    pub time_complexity: String,
    #[serde(default)]
    pub space_complexity: String,
    #[serde(default)]
    pub approach_kind: String, // e.g. "Brute Force" | "Optimized" | ...
    #[serde(default)]
    pub notes: String,
    #[serde(default)]
    pub created_at: String,
    #[serde(default)]
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Attempt {
    #[serde(default)]
    pub id: i64,
    pub problem_id: i64,
    pub language: String,
    pub code: String,
    /// "accepted" | "wrong" | "error" | "run"
    pub status: String,
    #[serde(default)]
    pub runtime_ms: Option<i64>,
    #[serde(default)]
    pub memory_kb: Option<i64>,
    #[serde(default)]
    pub passed: i64,
    #[serde(default)]
    pub total: i64,
    #[serde(default)]
    pub error_text: String,
    #[serde(default)]
    pub duration_seconds: i64,
    #[serde(default)]
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Review {
    #[serde(default)]
    pub id: i64,
    pub problem_id: i64,
    pub due_date: String,       // ISO date (YYYY-MM-DD)
    pub interval_index: i64,    // legacy ladder index (kept for compatibility)
    #[serde(default = "default_ease")]
    pub ease: f64,
    #[serde(default)]
    pub reps: i64,
    #[serde(default)]
    pub lapses: i64,
    #[serde(default)]
    pub interval_days: i64,
    #[serde(default)]
    pub last_quality: i64,
    #[serde(default)]
    pub last_reviewed_at: Option<String>,
    #[serde(default)]
    pub created_at: String,
}

fn default_ease() -> f64 {
    2.5
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Mistake {
    #[serde(default)]
    pub id: i64,
    pub problem_id: i64,
    #[serde(default)]
    pub attempt_id: Option<i64>,
    pub category: String,
    #[serde(default)]
    pub note: String,
    #[serde(default)]
    pub created_at: String,
}

/// A curated learning path with its ordered problems (hydrated for the UI).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Path {
    #[serde(default)]
    pub id: i64,
    pub key: String,
    pub title: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub ordering: i64,
    #[serde(default)]
    pub items: Vec<PathItem>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PathItem {
    pub problem_id: i64,
    pub title: String,
    pub difficulty: String,
    pub solved_status: String,
    #[serde(default)]
    pub ordering: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Contest {
    #[serde(default)]
    pub id: i64,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub problem_ids: Vec<i64>,
    #[serde(default)]
    pub duration_seconds: i64,
    #[serde(default)]
    pub status: String,
    #[serde(default)]
    pub started_at: String,
    #[serde(default)]
    pub ended_at: Option<String>,
    #[serde(default)]
    pub results: Vec<ContestResult>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContestResult {
    pub problem_id: i64,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub difficulty: String,
    #[serde(default)]
    pub solved: bool,
    #[serde(default)]
    pub solved_at: Option<String>,
    #[serde(default)]
    pub wrong_tries: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Flashcard {
    #[serde(default)]
    pub id: i64,
    pub front: String,
    pub back: String,
    #[serde(default)]
    pub source: String,
    #[serde(default = "default_ease")]
    pub ease: f64,
    #[serde(default)]
    pub reps: i64,
    #[serde(default)]
    pub lapses: i64,
    #[serde(default)]
    pub interval_days: i64,
    #[serde(default)]
    pub due_date: String,
    #[serde(default)]
    pub created_at: String,
}

/// SM-2 scheduling state for a single vocabulary card (Japanese track). Card
/// content lives in concepts.json; this is only the per-card review state,
/// keyed by a stable id ("<conceptKey>#<term>").
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CardReview {
    pub card_id: String,
    #[serde(default = "default_ease")]
    pub ease: f64,
    #[serde(default)]
    pub reps: i64,
    #[serde(default)]
    pub lapses: i64,
    #[serde(default)]
    pub interval_days: i64,
    #[serde(default)]
    pub due_date: String,
    /// Last grade given (0=Again..3=Easy), -1 if never graded.
    #[serde(default)]
    pub last_quality: i64,
}

/// One problem restated in Japanese, linked (by `slug`) to a real problem in
/// the bank so the UI can open it in the solver. Part of the Japanese track.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BridgeProblem {
    pub slug: String,
    pub title_ja: String,
    pub statement_ja: String,
    #[serde(default)]
    pub io_ja: String,
    /// [term, reading, english] triples for the words used in the statement.
    #[serde(default)]
    pub vocab: Vec<Vec<String>>,
    #[serde(default)]
    pub hint_ja: String,
}

/// A Japanese technical-interview question with a model answer (JP + EN).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InterviewQA {
    pub q_ja: String,
    #[serde(default)]
    pub q_en: String,
    pub a_ja: String,
    #[serde(default)]
    pub a_en: String,
    #[serde(default)]
    pub tags: Vec<String>,
}

/// The whole Japanese → Java bridge catalog (embedded seeds/jp_bridge.json).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JpBridge {
    #[serde(default)]
    pub problems: Vec<BridgeProblem>,
    #[serde(default)]
    pub interview: Vec<InterviewQA>,
}

// ---------------------------------------------------------------------------
// TypeScript course — an 8-month, week-by-week structured curriculum. Content
// lives in the embedded seeds/ts_course.json; served by the `ts_course`
// command. Lessons reuse the same `Exercise` + `QuizQuestion` model (and the
// same stdin/stdout judge) as the Learn concepts.
// ---------------------------------------------------------------------------

/// The whole TypeScript course (embedded seeds/ts_course.json).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TsCourse {
    #[serde(default)]
    pub key: String,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub subtitle: String,
    #[serde(default)]
    pub weeks: Vec<CourseWeek>,
}

/// One themed week of the course: a goal, a set of lessons, and a capstone.
/// `authored=false` marks a skeleton placeholder shown as "coming soon".
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CourseWeek {
    pub number: i64,
    #[serde(default)]
    pub month: i64,
    #[serde(default)]
    pub month_title: String,
    #[serde(default)]
    pub theme: String,
    #[serde(default)]
    pub goal: String,
    #[serde(default)]
    pub summary: String,
    #[serde(default)]
    pub authored: bool,
    #[serde(default)]
    pub lessons: Vec<CourseLesson>,
    #[serde(default)]
    pub capstone: Option<Capstone>,
    // --- Polish fields (all optional; empty = section hidden) --------------
    /// "By the end of this week you can…" bullet list.
    #[serde(default)]
    pub objectives: Vec<String>,
    /// One-line real-world "why this matters" hook.
    #[serde(default)]
    pub why: String,
    /// Estimated time to complete the week, in minutes.
    #[serde(default)]
    pub est_minutes: i64,
    /// Term → plain-English definition for the week's new vocabulary.
    #[serde(default)]
    pub glossary: Vec<GlossaryItem>,
    /// A short Markdown syntax cheat-sheet for everything introduced this week.
    #[serde(default)]
    pub cheatsheet: String,
    /// "Can you…?" self-check prompts shown at the end.
    #[serde(default)]
    pub self_check: Vec<String>,
    /// End-of-week mixed-review quiz (may pull from earlier weeks).
    #[serde(default)]
    pub review: Vec<QuizQuestion>,
    /// "You can now build…" milestone celebrated on completion.
    #[serde(default)]
    pub milestone: String,
}

/// One term and its plain-English definition (week glossary).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GlossaryItem {
    pub term: String,
    #[serde(default)]
    pub def: String,
}

/// One lesson within a week: prose (`lesson`, Markdown) plus judged exercises,
/// an optional "predict the output" warm-up, and a self-check quiz — all scoped
/// to what's been taught so far.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CourseLesson {
    pub key: String,
    pub title: String,
    #[serde(default)]
    pub what: String,
    #[serde(default)]
    pub lesson: String,
    /// "What does this print?" multiple-choice warm-up shown before the drills.
    #[serde(default)]
    pub warmup: Vec<QuizQuestion>,
    #[serde(default)]
    pub exercises: Vec<Exercise>,
    #[serde(default)]
    pub quiz: Vec<QuizQuestion>,
}

/// A week's capstone mini-project. `kind = "auto"` carries a judged `exercise`
/// (a fuller build with hidden tests); `kind = "brief"` is a written spec the
/// learner builds freely and self-marks (some projects don't fit console I/O).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Capstone {
    pub title: String,
    #[serde(default)]
    pub brief: String,
    #[serde(default)]
    pub kind: String,
    #[serde(default)]
    pub exercise: Option<Exercise>,
    /// Exact expected console output for the core build (shown in the spec).
    #[serde(default)]
    pub example_io: String,
    /// A "did I do it?" checklist for the learner.
    #[serde(default)]
    pub rubric: Vec<String>,
    /// A reference solution revealed after a brief (free-build) capstone.
    #[serde(default)]
    pub reference: String,
    /// An optional harder "stretch" build for fast learners.
    #[serde(default)]
    pub stretch: Option<Exercise>,
}

// ---------------------------------------------------------------------------
// 6-Month Mastery programme (seeds/mastery.json, authored in
// tools/mastery_defs.py). The Learn catalog is a reference library you can read
// in any order; a mastery track sequences it into weeks with problems, a build
// project and a gating end-of-week exam. Progress lives client-side, so these
// models are read-only content.
// ---------------------------------------------------------------------------

/// A curated Library problem for one week, with the reason it was chosen.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MasteryProblem {
    pub slug: String,
    #[serde(default)]
    pub note: String,
}

/// The week's coding final — a full problem run through the same judge as the
/// Learn challenges (`run_tests` with a null problem id). Answering multiple
/// choice is not enough to unlock the next week; this has to be accepted too.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MasteryExam {
    pub title: String,
    pub prompt: String,
    #[serde(default)]
    pub hint: String,
    pub language: String,
    pub starter: String,
    /// Reference solution, revealable after a pass (and proven by the seed tests).
    pub solution: String,
    #[serde(default)]
    pub tests: Vec<ExerciseTest>,
}

/// An optional timed checkpoint contest attached to a week, built from that
/// week's problems through the existing Contest machinery.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MasteryContest {
    pub title: String,
    pub duration_seconds: i64,
}

/// One week of a mastery track.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MasteryWeek {
    /// 1-based week number; weeks are numbered 1..N with no gaps.
    pub week: i64,
    /// Which month/phase this week belongs to, for grouping in the UI.
    #[serde(default)]
    pub phase: String,
    pub title: String,
    #[serde(default)]
    pub goal: String,
    /// Concept keys to study, resolved against the Learn catalog.
    #[serde(default)]
    pub concepts: Vec<String>,
    #[serde(default)]
    pub problems: Vec<MasteryProblem>,
    /// A build-it-yourself brief. Not graded, but the learner's notes and code
    /// for it are stored against the week.
    #[serde(default)]
    pub project: String,
    /// The end-of-week question BANK. The UI samples `quiz_sample` of these and
    /// shuffles both the questions and each question's options, so a retake is
    /// not a memory test for answer positions.
    #[serde(default)]
    pub quiz: Vec<QuizQuestion>,
    /// How many bank questions make up one sitting of the exam.
    #[serde(default)]
    pub quiz_sample: i64,
    /// The week's coding final.
    pub exam: Option<MasteryExam>,
    /// A timed checkpoint contest, on consolidation weeks.
    pub contest: Option<MasteryContest>,
}

/// The learner's state for one week of one track (table `mastery_progress`).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MasteryProgress {
    pub track_key: String,
    pub week: i64,
    /// Best multiple-choice percentage; -1 when never attempted.
    pub best_quiz: i64,
    pub exam_passed: bool,
    pub exam_code: String,
    pub project_notes: String,
    pub project_code: String,
    pub project_done: bool,
    pub study_seconds: i64,
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
}

/// A full programme — currently one track (TypeScript), built to hold more.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MasteryTrack {
    pub key: String,
    pub title: String,
    /// Learn-catalog language whose concepts this track schedules.
    #[serde(default)]
    pub language: String,
    #[serde(default)]
    pub subtitle: String,
    #[serde(default)]
    pub intro: String,
    /// Percentage of the end-of-week quiz required to unlock the next week.
    #[serde(default)]
    pub pass_mark: i64,
    /// Language the coding finals are written in.
    #[serde(default)]
    pub exam_language: String,
    #[serde(default)]
    pub weeks: Vec<MasteryWeek>,
}

/// A review item joined with its problem for the review queue UI.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReviewItem {
    pub review: Review,
    pub problem_id: i64,
    pub title: String,
    pub difficulty: String,
    pub confidence: i64,
    pub topics: Vec<String>,
}
