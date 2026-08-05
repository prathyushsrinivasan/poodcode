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
    /// Full Markdown lesson (worked example, code, pitfalls).
    #[serde(default)]
    pub lesson: String,
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
