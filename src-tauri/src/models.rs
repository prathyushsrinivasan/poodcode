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
    /// TypeScript only: the strictness preset this exercise is type-checked at
    /// ("" = `strict`, or `strict+indexed`). The TypeScript course tightens the
    /// compiler as the syllabus advances, so a week-6 array drill is checked
    /// under `noUncheckedIndexedAccess` while a week-2 one is not.
    #[serde(default)]
    pub strictness: String,
    /// TypeScript only: hidden source appended to the learner's program before
    /// it is type-checked and run. It never appears in the editor, so it cannot
    /// be read around or deleted.
    ///
    /// Two uses, told apart by [`Exercise::judge_mode`]:
    ///
    /// - **stdout** — a *driver*. It reads the case's stdin, calls the function
    ///   the exercise asked for, and prints the result in a canonical form. This
    ///   is what lets an exercise say "implement `twoSum(nums, target)`" and
    ///   grade the value it returns, instead of forcing every solution to
    ///   hand-roll `console.log` scaffolding around the real work.
    /// - **types** — *assertions*. `Expect<Equal<…>>` lines that only have to
    ///   compile.
    ///
    /// Unrelated to the [`crate::harness`] module, which generates I/O glue from
    /// a [`FunctionSpec`] for the Python/Java problem bank. This one is authored
    /// text carried in the seed, so the judge and `tools/verify_ts_course.py`
    /// grade against the same bytes and cannot drift apart.
    #[serde(default)]
    pub harness: String,
    /// How this exercise is graded. `""` / `"stdout"` (the default) runs the
    /// program and compares stdout against `tests`.
    ///
    /// `"types"` never runs it: the program only has to type-check, and `tests`
    /// is empty. That is the only way to grade a type — `Pick<T, K>` has no
    /// runtime value to print, so the assertion has to fail at *compile* time.
    #[serde(default)]
    pub judge_mode: String,
    /// Substrings the learner's own source may not contain. Checked before the
    /// program is compiled, so a violation reads as a rejection rather than as a
    /// confusing pass.
    ///
    /// This exists because some exercises are gradeable but trivially dodgeable.
    /// A "predict the type" drill asks the learner to annotate `check` with the
    /// type the compiler infers for `x`, and its assertion is
    /// `Equal<typeof check, typeof x>`; that assertion is honest — and worth
    /// revealing under "What's being checked?" — but `const check: typeof x = x`
    /// satisfies it without predicting anything. Banning `typeof` is what makes
    /// the question real.
    ///
    /// The judge only reports *which* substring was used; the exercise's prompt
    /// is where the reason belongs.
    #[serde(default)]
    pub forbid: Vec<String>,
    pub starter: String,
    pub solution: String,
    #[serde(default)]
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
// Structured courses — a sequence of numbered units, each with lessons and a
// capstone. Two of them ship, sharing this model, the `Exercise` +
// `QuizQuestion` types and the same stdin/stdout judge as the Learn concepts:
//
//   * seeds/ts_course.json   — TypeScript, an 8-month WEEK-by-week curriculum
//                              (`ts_course` command, tools/typescript_course.py)
//   * seeds/java_course.json — Java after the basics, ten topic MODULES
//                              (`java_course` command, tools/java_course.py)
//
// The two levels are called Week/Month in one and Module/Part in the other, so
// the course itself carries the labels the UI should use — see `unit_label`.
// ---------------------------------------------------------------------------

/// A whole structured course (embedded seeds/ts_course.json or
/// seeds/java_course.json).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WeeklyCourse {
    #[serde(default)]
    pub key: String,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub subtitle: String,
    /// What one unit is called — "Week" (default) or "Module".
    #[serde(default)]
    pub unit_label: String,
    /// What a group of units is called — "Month" (default) or "Part".
    #[serde(default)]
    pub group_label: String,
    #[serde(default)]
    pub weeks: Vec<CourseWeek>,
}

/// One themed unit of a course: a goal, a set of lessons, and a capstone.
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
    /// Optional bulk practice: families of variations on this module's patterns.
    /// Empty for tracks that ship none, so older seeds keep deserialising.
    #[serde(default)]
    pub practice: Vec<PracticeFamily>,
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

/// A family of practice problems: several variants of ONE pattern, drilled back
/// to back. `intro` is a short worked walkthrough of the base case, so each
/// variant is a twist on something already shown rather than a cold start.
///
/// Practice is deliberately NOT counted towards completing a module (see
/// `requiredExerciseIds` in Course.tsx) — it is a drilling ground to come back
/// to, not a gate that has to be cleared.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PracticeFamily {
    pub key: String,
    pub title: String,
    /// One line naming the motion being drilled.
    #[serde(default)]
    pub pattern: String,
    /// Markdown walkthrough of the base pattern, shown above the variants.
    #[serde(default)]
    pub intro: String,
    #[serde(default)]
    pub exercises: Vec<Exercise>,
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
// Backend Lab — a project-based track that builds CRUD HTTP APIs from scratch.
// Content lives in the embedded seeds/backend_course.json (authored in
// tools/backend_course.py); served by the `backend_track` command.
//
// Where the TypeScript course is a *time* ladder (weeks), this one is a *build*
// ladder: each project is a working server you finish and can run, and each
// project reopens the previous one's code to add the next layer. Steps carry the
// instructions ("do this, then this") plus a checkpoint that tells you how to
// know it worked — the thing a beginner is usually missing.
//
// Exercises reuse the same `Exercise` model and the same stdin/stdout judge as
// everything else: each program boots a real `node:http` server on port 0 and
// replays a request script read from stdin, so a route bug shows up as a wrong
// status code rather than as a mystery.
// ---------------------------------------------------------------------------

/// The whole Backend Lab track (embedded seeds/backend_course.json).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackendTrack {
    #[serde(default)]
    pub key: String,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub subtitle: String,
    /// Markdown shown once on the overview: how to work through the track.
    #[serde(default)]
    pub intro: String,
    /// The stdin request-script format every judged exercise is driven by,
    /// explained once (Markdown) rather than repeated in every prompt.
    #[serde(default)]
    pub harness_note: String,
    #[serde(default)]
    pub projects: Vec<BackendProject>,
}

/// One buildable project: a spec, ordered steps, and a finished reference.
/// `authored=false` marks a planned project shown as "coming soon".
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackendProject {
    pub key: String,
    pub number: i64,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub tagline: String,
    /// "Starter" | "Core" | "Advanced" — sizing, not gating.
    #[serde(default)]
    pub level: String,
    #[serde(default)]
    pub goal: String,
    /// One-line "why a real backend needs this".
    #[serde(default)]
    pub why: String,
    #[serde(default)]
    pub authored: bool,
    #[serde(default)]
    pub est_minutes: i64,
    /// Keys of the projects this one continues from.
    #[serde(default)]
    pub builds_on: Vec<String>,
    /// Short concept tags shown as badges ("status codes", "routing", …).
    #[serde(default)]
    pub concepts: Vec<String>,
    #[serde(default)]
    pub objectives: Vec<String>,
    /// Markdown: what you are building and the shape of the finished thing.
    #[serde(default)]
    pub brief: String,
    /// The API contract as a table — the spec you build against.
    #[serde(default)]
    pub endpoints: Vec<Endpoint>,
    /// Markdown: files to create and the exact command that runs the server.
    #[serde(default)]
    pub setup: String,
    #[serde(default)]
    pub steps: Vec<BackendStep>,
    /// The judged "now build the whole thing" exercise closing the project.
    #[serde(default)]
    pub final_build: Option<Exercise>,
    /// "Did I actually do it?" checklist for the finished server.
    #[serde(default)]
    pub acceptance: Vec<String>,
    /// Markdown: curl / fetch commands to try against your own running server.
    #[serde(default)]
    pub manual_test: String,
    /// A complete reference implementation, revealed on request.
    #[serde(default)]
    pub reference: String,
    /// Optional extensions for when the project is done.
    #[serde(default)]
    pub stretch: Vec<String>,
    #[serde(default)]
    pub glossary: Vec<GlossaryItem>,
    #[serde(default)]
    pub cheatsheet: String,
    #[serde(default)]
    pub self_check: Vec<String>,
    #[serde(default)]
    pub review: Vec<QuizQuestion>,
    #[serde(default)]
    pub milestone: String,
}

/// One row of a project's API contract.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Endpoint {
    pub method: String,
    pub path: String,
    #[serde(default)]
    pub purpose: String,
    /// Request body shape, or "" for none.
    #[serde(default)]
    pub request: String,
    /// Success response body shape.
    #[serde(default)]
    pub response: String,
    /// Status codes this endpoint can return, e.g. "201 · 400".
    #[serde(default)]
    pub status: String,
}

/// One step of a project: what to do, how to check it worked, and drills.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackendStep {
    pub key: String,
    pub title: String,
    #[serde(default)]
    pub what: String,
    /// Markdown: the actual instructions for this step.
    #[serde(default)]
    pub instructions: String,
    /// Markdown: the observable result that proves the step is done.
    #[serde(default)]
    pub checkpoint: String,
    /// Mistakes that cost beginners an hour, named up front.
    #[serde(default)]
    pub pitfalls: Vec<String>,
    /// "What does this request return?" multiple-choice warm-up.
    #[serde(default)]
    pub warmup: Vec<QuizQuestion>,
    #[serde(default)]
    pub exercises: Vec<Exercise>,
    #[serde(default)]
    pub quiz: Vec<QuizQuestion>,
}

// ---------------------------------------------------------------------------
// Projects — build one real application, in TypeScript, broken all the way
// down. Content lives in the embedded seeds/projects.json (authored in
// tools/projects_track.py plus one file per module); served by the
// `projects_track` command.
//
// HOW THIS DIFFERS FROM THE BACKEND LAB, which is also project-shaped:
//
//   * Backend Lab is JavaScript and two levels deep (Project → Step). Its unit
//     is a whole server you finish in an evening.
//   * Projects is TypeScript and three levels deep (Project → Module → Step).
//     Its unit is a MODULE: one 30-60 minute slice that adds exactly one
//     capability to an application you keep building. A module is small enough
//     to carry the full development process end to end — why it exists, where
//     it sits on the roadmap, the syntax it needs, ordered steps with a
//     checkpoint each, exercises you actually write, and a revealable
//     reference — which is the whole point of breaking it down this far.
//
// Both reuse `BackendStep`, `Endpoint`, `Exercise` and the same stdin/stdout
// judge, so a module's drills are graded exactly like everything else in the
// app: boot a real server on port 0, replay a request script, compare stdout.
// ---------------------------------------------------------------------------

/// The whole Projects track (embedded seeds/projects.json).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectTrack {
    #[serde(default)]
    pub key: String,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub subtitle: String,
    /// Markdown shown once on the overview: how to work through a project.
    #[serde(default)]
    pub intro: String,
    /// The stdin request-script format every judged exercise is driven by,
    /// explained once rather than repeated in every prompt.
    #[serde(default)]
    pub harness_note: String,
    #[serde(default)]
    pub projects: Vec<Project>,
}

/// One application built across many modules. `authored=false` marks a planned
/// project shown as "coming soon".
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub key: String,
    pub number: i64,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub tagline: String,
    /// Language the whole project is written in ("typescript").
    #[serde(default)]
    pub language: String,
    #[serde(default)]
    pub goal: String,
    /// One-line "why anyone builds this".
    #[serde(default)]
    pub why: String,
    #[serde(default)]
    pub authored: bool,
    #[serde(default)]
    pub est_minutes: i64,
    /// What it is built out of, shown as badges ("TypeScript", "node:http",
    /// "zero dependencies").
    #[serde(default)]
    pub stack: Vec<String>,
    /// What finishing the modules does and does not mean, shown under the
    /// progress bar. Project-specific on purpose: ticking every module off is
    /// never the real deliverable, but what the real deliverable *is* differs
    /// per project — for the Todo API it is a server running on your own
    /// machine, and the next project's will be something else entirely.
    #[serde(default)]
    pub completion_note: String,
    /// Markdown: what the finished application is.
    #[serde(default)]
    pub brief: String,
    /// The finished application's full API contract — the spec every module
    /// chips away at, shown up front so the destination is never a mystery.
    #[serde(default)]
    pub endpoints: Vec<Endpoint>,
    /// Markdown: files to create and the exact command that runs it.
    #[serde(default)]
    pub setup: String,
    /// The module map, grouped into phases. This is the "roadmap" the learner
    /// navigates by; every module names the phase it belongs to.
    #[serde(default)]
    pub roadmap: Vec<RoadmapPhase>,
    #[serde(default)]
    pub modules: Vec<ProjectModule>,
    /// "Did I actually build it?" checklist for the finished application.
    #[serde(default)]
    pub acceptance: Vec<String>,
    /// Markdown: curl commands to try against your own running server.
    #[serde(default)]
    pub manual_test: String,
    /// The complete finished source, revealed on request.
    #[serde(default)]
    pub reference: String,
    #[serde(default)]
    pub stretch: Vec<String>,
    #[serde(default)]
    pub milestone: String,
}

/// One phase of a project's roadmap: a run of consecutive modules that together
/// deliver something demonstrable.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoadmapPhase {
    pub key: String,
    pub title: String,
    /// What the application can do once this phase is finished.
    #[serde(default)]
    pub outcome: String,
    #[serde(default)]
    pub summary: String,
}

/// One module: the smallest unit that still runs the whole development
/// process. Adds exactly one capability to the application.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectModule {
    pub key: String,
    pub number: i64,
    /// Key of the [`RoadmapPhase`] this module belongs to.
    #[serde(default)]
    pub phase: String,
    #[serde(default)]
    pub title: String,
    /// One line, shown in the module list.
    #[serde(default)]
    pub what: String,
    #[serde(default)]
    pub goal: String,
    /// Why this module exists — the problem the previous module left behind.
    /// Written to be readable *before* the learner knows the solution.
    #[serde(default)]
    pub why: String,
    #[serde(default)]
    pub authored: bool,
    #[serde(default)]
    pub est_minutes: i64,
    /// Keys of the modules this one continues from.
    #[serde(default)]
    pub builds_on: Vec<String>,
    /// Short concept badges ("discriminated union", "status codes").
    #[serde(default)]
    pub concepts: Vec<String>,
    #[serde(default)]
    pub objectives: Vec<String>,
    /// The one sentence naming what the app can do at the end of this module
    /// that it could not at the start. The module's reason to exist.
    #[serde(default)]
    pub deliverable: String,
    /// Markdown: the design discussion — what we are about to build and why
    /// this shape rather than another.
    #[serde(default)]
    pub brief: String,
    /// Every piece of TypeScript syntax this module needs, taught before it is
    /// used. A module may only rely on syntax it or an earlier module declared
    /// here — enforced at generation time — so the track never assumes an
    /// import from the TypeScript course.
    #[serde(default)]
    pub syntax: Vec<SyntaxItem>,
    /// The rows of the project's contract this module implements.
    #[serde(default)]
    pub endpoints: Vec<Endpoint>,
    #[serde(default)]
    pub steps: Vec<BackendStep>,
    /// The judged "now put it together" exercise closing the module.
    #[serde(default)]
    pub final_build: Option<Exercise>,
    #[serde(default)]
    pub acceptance: Vec<String>,
    /// Markdown: curl commands proving this module's slice works.
    #[serde(default)]
    pub manual_test: String,
    /// The module's finished source, revealed on request — the "reveal
    /// solution" for the whole module rather than for one exercise.
    #[serde(default)]
    pub reference: String,
    #[serde(default)]
    pub stretch: Vec<String>,
    #[serde(default)]
    pub glossary: Vec<GlossaryItem>,
    #[serde(default)]
    pub cheatsheet: String,
    #[serde(default)]
    pub self_check: Vec<String>,
    #[serde(default)]
    pub review: Vec<QuizQuestion>,
    #[serde(default)]
    pub milestone: String,
}

/// One piece of syntax a module needs, taught in the module that first needs
/// it. Four fields because the form alone teaches nobody anything: what it
/// means in words, the smallest example that shows it working, and the thing
/// that catches people out.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyntaxItem {
    /// The syntax itself, e.g. `type Todo = { id: number }`.
    pub form: String,
    /// What it means, in one plain sentence.
    #[serde(default)]
    pub means: String,
    /// The smallest complete example that shows it working.
    #[serde(default)]
    pub example: String,
    /// The mistake people make with it.
    #[serde(default)]
    pub note: String,
    /// True when an earlier module already taught this and the module is only
    /// reminding the reader. Rendered dimmer, and exempt from "new syntax".
    #[serde(default)]
    pub recap: bool,
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
