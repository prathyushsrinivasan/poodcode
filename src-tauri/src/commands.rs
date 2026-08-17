use std::sync::Mutex;
use std::time::Duration;

use chrono::Local;
use rusqlite::Connection;
use serde::Serialize;
use tauri::State;

use crate::error::{AppError, AppResult};
use crate::exec::{self, LangInfo, ProcOut};
use crate::judge::{self, JudgeReport};
use crate::models::*;
use crate::{repo, stats};

/// Shared application state: a single SQLite connection behind a mutex, plus
/// the on-disk path so backup/restore can operate on the database file.
pub struct AppState {
    pub db: Mutex<Connection>,
    pub db_path: std::path::PathBuf,
}

impl AppState {
    /// Lock the connection, recovering the guard if a previous holder panicked
    /// while holding it. A poisoned lock does not mean the data is corrupt —
    /// SQLite state is consistent — so recovering keeps the app usable rather
    /// than taking the whole backend down.
    fn conn(&self) -> std::sync::MutexGuard<'_, Connection> {
        self.db.lock().unwrap_or_else(|poisoned| poisoned.into_inner())
    }
}

const RUN_TIMEOUT: Duration = Duration::from_secs(6);

/// Bundled concept catalog for the Learn section (authored in tools/gen_seed.py).
const CONCEPTS_JSON: &str = include_str!("../seeds/concepts.json");

#[tauri::command]
pub fn concepts() -> AppResult<Vec<crate::models::Concept>> {
    Ok(serde_json::from_str(CONCEPTS_JSON)?)
}

/// Japanese → Java bridge content (problem statements in Japanese + interview
/// Q&A), authored in tools/japanese_bridge.py.
const JP_BRIDGE_JSON: &str = include_str!("../seeds/jp_bridge.json");

#[tauri::command]
pub fn jp_bridge() -> AppResult<crate::models::JpBridge> {
    Ok(serde_json::from_str(JP_BRIDGE_JSON)?)
}

// ---------------------------------------------------------------------------
// Problems
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn list_problems(state: State<'_, AppState>) -> AppResult<Vec<Problem>> {
    repo::list_problems(&state.conn())
}

#[tauri::command]
pub fn get_problem(state: State<'_, AppState>, id: i64) -> AppResult<Problem> {
    repo::get_problem(&state.conn(), id)
}

#[tauri::command]
pub fn save_problem(state: State<'_, AppState>, problem: Problem) -> AppResult<i64> {
    repo::upsert_problem(&state.conn(), &problem)
}

#[tauri::command]
pub fn delete_problem(state: State<'_, AppState>, id: i64) -> AppResult<()> {
    repo::delete_problem(&state.conn(), id)
}

#[tauri::command]
pub fn set_favorite(state: State<'_, AppState>, id: i64, favorite: bool) -> AppResult<()> {
    repo::set_favorite(&state.conn(), id, favorite)
}

#[tauri::command]
pub fn set_confidence(state: State<'_, AppState>, id: i64, confidence: i64) -> AppResult<()> {
    repo::set_confidence(&state.conn(), id, confidence)
}

#[tauri::command]
pub fn distinct_tags(state: State<'_, AppState>, kind: String) -> AppResult<Vec<String>> {
    repo::distinct_tags(&state.conn(), &kind)
}

// ---------------------------------------------------------------------------
// Import / export
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn import_problems(state: State<'_, AppState>, json: String) -> AppResult<usize> {
    let problems: Vec<Problem> = serde_json::from_str(&json)?;
    let conn = state.conn();
    let mut n = 0;
    for p in &problems {
        repo::upsert_problem(&conn, p)?;
        n += 1;
    }
    Ok(n)
}

/// These commands exist only to move the JSON problem library in and out via the
/// OS file dialog. To keep them from doubling as a general-purpose arbitrary-file
/// primitive on the JS surface, they refuse anything that isn't a `.json` file.
fn guard_json_path(path: &str) -> AppResult<()> {
    let ext = std::path::Path::new(path)
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_ascii_lowercase();
    if ext != "json" {
        return Err(AppError::Other(
            "only .json files can be read or written here".into(),
        ));
    }
    Ok(())
}

/// Read a UTF-8 JSON file (used by the import dialog).
#[tauri::command]
pub fn read_file(path: String) -> AppResult<String> {
    guard_json_path(&path)?;
    Ok(std::fs::read_to_string(path)?)
}

/// Write a UTF-8 JSON file (used by the export dialog).
#[tauri::command]
pub fn write_file(path: String, contents: String) -> AppResult<()> {
    guard_json_path(&path)?;
    std::fs::write(path, contents)?;
    Ok(())
}

#[tauri::command]
pub fn export_problems(state: State<'_, AppState>) -> AppResult<String> {
    let problems = {
        let conn = state.conn();
        let ids: Vec<i64> = repo::list_problems(&conn)?.into_iter().map(|p| p.id).collect();
        ids.into_iter()
            .map(|id| repo::get_problem(&conn, id))
            .collect::<AppResult<Vec<_>>>()?
    };
    Ok(serde_json::to_string_pretty(&problems)?)
}

// ---------------------------------------------------------------------------
// Test cases
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn list_test_cases(state: State<'_, AppState>, problem_id: i64) -> AppResult<Vec<TestCase>> {
    repo::list_test_cases(&state.conn(), problem_id)
}

#[tauri::command]
pub fn save_test_case(state: State<'_, AppState>, test_case: TestCase) -> AppResult<i64> {
    repo::save_test_case(&state.conn(), &test_case)
}

#[tauri::command]
pub fn delete_test_case(state: State<'_, AppState>, id: i64) -> AppResult<()> {
    repo::delete_test_case(&state.conn(), id)
}

// ---------------------------------------------------------------------------
// Prerequisites checklist
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn known_prereqs(state: State<'_, AppState>, problem_id: i64) -> AppResult<Vec<String>> {
    repo::known_prereqs(&state.conn(), problem_id)
}

#[tauri::command]
pub fn set_prereq_status(
    state: State<'_, AppState>,
    problem_id: i64,
    key: String,
    known: bool,
) -> AppResult<()> {
    repo::set_prereq_status(&state.conn(), problem_id, &key, known)
}

// ---------------------------------------------------------------------------
// Notes
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn get_note(state: State<'_, AppState>, problem_id: i64) -> AppResult<Note> {
    repo::get_note(&state.conn(), problem_id)
}

#[tauri::command]
pub fn save_note(state: State<'_, AppState>, problem_id: i64, content: String) -> AppResult<()> {
    repo::save_note(&state.conn(), problem_id, &content)
}

// ---------------------------------------------------------------------------
// Solutions
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn list_solutions(state: State<'_, AppState>, problem_id: i64) -> AppResult<Vec<Solution>> {
    repo::list_solutions(&state.conn(), problem_id)
}

#[tauri::command]
pub fn save_solution(state: State<'_, AppState>, solution: Solution) -> AppResult<i64> {
    repo::save_solution(&state.conn(), &solution)
}

#[tauri::command]
pub fn delete_solution(state: State<'_, AppState>, id: i64) -> AppResult<()> {
    repo::delete_solution(&state.conn(), id)
}

// ---------------------------------------------------------------------------
// Attempts + execution
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn list_attempts(state: State<'_, AppState>, problem_id: i64) -> AppResult<Vec<Attempt>> {
    repo::list_attempts(&state.conn(), problem_id)
}

#[tauri::command]
pub fn languages() -> Vec<LangInfo> {
    exec::languages()
}

/// Build the judging configuration (compare mode, tolerance, harness spec, time
/// limit) for a problem, falling back to plain exact-match defaults.
fn judge_config_for(conn: &Connection, problem_id: Option<i64>) -> judge::JudgeConfig {
    if let Some(id) = problem_id {
        if let Ok(p) = repo::get_problem(conn, id) {
            let timeout = if p.time_limit_ms > 0 {
                Duration::from_millis(p.time_limit_ms as u64)
            } else {
                RUN_TIMEOUT
            };
            return judge::JudgeConfig {
                mode: p.judge_mode,
                tolerance: p.float_tolerance,
                function_spec: p.function_spec,
                checker: if p.checker.is_empty() { None } else { Some(p.checker) },
                timeout,
            };
        }
    }
    judge::JudgeConfig::exact(RUN_TIMEOUT)
}

/// Run the user's code against an explicit set of test cases (the "Run" action).
/// Nothing is persisted. `problem_id` supplies the judge config (harness/mode).
#[tauri::command]
pub fn run_tests(
    state: State<'_, AppState>,
    problem_id: Option<i64>,
    language: String,
    code: String,
    cases: Vec<TestCase>,
) -> AppResult<JudgeReport> {
    let cfg = judge_config_for(&state.conn(), problem_id);
    Ok(judge::judge_with(&language, &code, &cases, &cfg))
}

/// Quick scratch run: execute once against a single stdin blob (editor Run box).
/// For a function-harness problem the user's function is wrapped first.
#[tauri::command]
pub fn run_scratch(
    state: State<'_, AppState>,
    problem_id: Option<i64>,
    language: String,
    code: String,
    stdin: String,
) -> AppResult<ProcOut> {
    let cfg = judge_config_for(&state.conn(), problem_id);
    let effective = match &cfg.function_spec {
        Some(fs) => crate::harness::wrap(&language, &code, fs).map_err(AppError::Other)?,
        None => code,
    };
    let dir = std::env::temp_dir().join(format!("poodcode-{}", uuid::Uuid::new_v4()));
    std::fs::create_dir_all(&dir)?;
    let result = (|| {
        let spec = exec::prepare(&language, &effective, &dir).map_err(|e| match e {
            exec::PrepareError::NotInstalled { hint } => AppError::Other(hint),
            exec::PrepareError::Compile { message } => AppError::Other(message),
            exec::PrepareError::Unknown(id) => AppError::Other(format!("unknown language: {id}")),
            exec::PrepareError::Io(m) => AppError::Other(m),
        })?;
        exec::run_once(&spec, &stdin, cfg.timeout).map_err(AppError::Other)
    })();
    let _ = std::fs::remove_dir_all(&dir);
    result
}

/// Submit: judge against the problem's hidden cases (falling back to examples),
/// persist an attempt, update progress, and seed/advance the review schedule.
#[tauri::command]
pub fn submit(
    state: State<'_, AppState>,
    problem_id: i64,
    language: String,
    code: String,
    duration_seconds: i64,
) -> AppResult<JudgeReport> {
    let (cases, cfg) = {
        let conn = state.conn();
        let all = repo::list_test_cases(&conn, problem_id)?;
        let hidden: Vec<TestCase> = all.iter().filter(|c| c.kind == "hidden").cloned().collect();
        let cases = if hidden.is_empty() {
            all.into_iter().filter(|c| c.kind == "example").collect()
        } else {
            hidden
        };
        (cases, judge_config_for(&conn, Some(problem_id)))
    };

    let report = judge::judge_with(&language, &code, &cases, &cfg);

    // Don't record a "not_installed" outcome as an attempt.
    if report.status != "not_installed" {
        let attempt = Attempt {
            id: 0,
            problem_id,
            language: language.clone(),
            code: code.clone(),
            status: report.status.clone(),
            runtime_ms: Some(report.runtime_ms),
            memory_kb: report.memory_kb,
            passed: report.passed,
            total: report.total,
            error_text: report.compile_error.clone(),
            duration_seconds,
            created_at: String::new(),
        };
        repo::record_attempt(&state.conn(), &attempt)?;
    }
    Ok(report)
}

// ---------------------------------------------------------------------------
// Revision
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn due_reviews(state: State<'_, AppState>) -> AppResult<Vec<ReviewItem>> {
    let today = Local::now().date_naive().format("%Y-%m-%d").to_string();
    repo::due_reviews(&state.conn(), &today)
}

#[tauri::command]
pub fn mark_reviewed(
    state: State<'_, AppState>,
    problem_id: i64,
    remembered: bool,
) -> AppResult<()> {
    repo::mark_reviewed(&state.conn(), problem_id, remembered)
}

/// Grade a review with a 0..=3 quality (Again / Hard / Good / Easy) using SM-2.
#[tauri::command]
pub fn grade_review(
    state: State<'_, AppState>,
    problem_id: i64,
    quality: i64,
) -> AppResult<()> {
    repo::mark_reviewed_quality(&state.conn(), problem_id, quality)
}

// ---------------------------------------------------------------------------
// Mistakes (reflection)
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn add_mistake(state: State<'_, AppState>, mistake: Mistake) -> AppResult<i64> {
    repo::add_mistake(&state.conn(), &mistake)
}

#[tauri::command]
pub fn list_mistakes(state: State<'_, AppState>, problem_id: i64) -> AppResult<Vec<Mistake>> {
    repo::list_mistakes(&state.conn(), problem_id)
}

#[tauri::command]
pub fn delete_mistake(state: State<'_, AppState>, id: i64) -> AppResult<()> {
    repo::delete_mistake(&state.conn(), id)
}

// ---------------------------------------------------------------------------
// Learning paths
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn list_paths(state: State<'_, AppState>) -> AppResult<Vec<Path>> {
    repo::list_paths(&state.conn())
}

// ---------------------------------------------------------------------------
// Contests
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn create_contest(
    state: State<'_, AppState>,
    title: String,
    problem_ids: Vec<i64>,
    duration_seconds: i64,
) -> AppResult<i64> {
    repo::create_contest(&state.conn(), &title, &problem_ids, duration_seconds)
}

#[tauri::command]
pub fn contest(state: State<'_, AppState>, id: i64) -> AppResult<Contest> {
    repo::get_contest(&state.conn(), id)
}

#[tauri::command]
pub fn list_contests(state: State<'_, AppState>) -> AppResult<Vec<Contest>> {
    repo::list_contests(&state.conn())
}

#[tauri::command]
pub fn finish_contest(state: State<'_, AppState>, id: i64) -> AppResult<()> {
    repo::finish_contest(&state.conn(), id)
}

#[tauri::command]
pub fn record_contest_result(
    state: State<'_, AppState>,
    contest_id: i64,
    problem_id: i64,
    solved: bool,
) -> AppResult<()> {
    repo::record_contest_result(&state.conn(), contest_id, problem_id, solved)
}

// ---------------------------------------------------------------------------
// Flashcards
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn list_flashcards(state: State<'_, AppState>) -> AppResult<Vec<Flashcard>> {
    repo::list_flashcards(&state.conn())
}

#[tauri::command]
pub fn due_flashcards(state: State<'_, AppState>) -> AppResult<Vec<Flashcard>> {
    repo::due_flashcards(&state.conn())
}

#[tauri::command]
pub fn add_flashcard(
    state: State<'_, AppState>,
    front: String,
    back: String,
    source: String,
) -> AppResult<i64> {
    repo::add_flashcard(&state.conn(), &front, &back, &source)
}

#[tauri::command]
pub fn grade_flashcard(state: State<'_, AppState>, id: i64, quality: i64) -> AppResult<()> {
    repo::grade_flashcard(&state.conn(), id, quality)
}

#[tauri::command]
pub fn delete_flashcard(state: State<'_, AppState>, id: i64) -> AppResult<()> {
    repo::delete_flashcard(&state.conn(), id)
}

#[tauri::command]
pub fn card_reviews(state: State<'_, AppState>) -> AppResult<Vec<crate::models::CardReview>> {
    repo::card_review_states(&state.conn())
}

#[tauri::command]
pub fn grade_card(
    state: State<'_, AppState>,
    card_id: String,
    quality: i64,
) -> AppResult<crate::models::CardReview> {
    repo::grade_card(&state.conn(), &card_id, quality)
}

#[tauri::command]
pub fn reset_cards(state: State<'_, AppState>, card_ids: Vec<String>) -> AppResult<()> {
    repo::reset_cards(&state.conn(), &card_ids)
}

#[tauri::command]
pub fn reschedule_review(
    state: State<'_, AppState>,
    problem_id: i64,
    due_date: String,
) -> AppResult<()> {
    repo::reschedule_review(&state.conn(), problem_id, &due_date)
}

// ---------------------------------------------------------------------------
// Statistics + dashboard
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn statistics(state: State<'_, AppState>) -> AppResult<stats::Stats> {
    stats::compute(&state.conn())
}

#[derive(Debug, Serialize)]
pub struct Dashboard {
    pub solved_today: i64,
    pub study_seconds_today: i64,
    pub reviews_due: i64,
    pub current_streak: i64,
    pub weakest_topic: Option<String>,
    pub suggested_problem: Option<Problem>,
    pub goals: Goals,
    pub goal_progress: GoalProgress,
    pub total_problems: i64,
    pub total_solved: i64,
}

#[derive(Debug, Serialize)]
pub struct Goals {
    pub intro: i64,
    pub easy: i64,
    pub medium: i64,
    pub hard: i64,
    pub reviews: i64,
}

#[derive(Debug, Serialize)]
pub struct GoalProgress {
    pub intro: i64,
    pub easy: i64,
    pub medium: i64,
    pub hard: i64,
    pub reviews: i64,
}

#[tauri::command]
pub fn dashboard(state: State<'_, AppState>) -> AppResult<Dashboard> {
    let conn = state.conn();
    let today = Local::now().date_naive().format("%Y-%m-%d").to_string();

    let (solved_today, study_seconds_today, reviews_done_today): (i64, i64, i64) = conn
        .query_row(
            "SELECT problems_solved, study_seconds, reviews_done FROM daily_sessions WHERE date = ?1",
            [&today],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .unwrap_or((0, 0, 0));

    let reviews_due: i64 = conn.query_row(
        "SELECT COUNT(*) FROM reviews WHERE due_date <= ?1",
        [&today],
        |r| r.get(0),
    )?;

    // Today's solved counts per difficulty (from accepted attempts today on
    // problems solved today). Approximate via attempts joined to problems.
    let count_today = |diff: &str| -> i64 {
        conn.query_row(
            "SELECT COUNT(DISTINCT a.problem_id) FROM attempts a
             JOIN problems p ON p.id = a.problem_id
             WHERE a.status='accepted' AND p.difficulty=?1 AND date(a.created_at)=?2",
            rusqlite::params![diff, today],
            |r| r.get(0),
        )
        .unwrap_or(0)
    };

    let st = stats::compute(&conn)?;
    let weakest_topic = st.weakest_topics.first().map(|t| t.topic.clone());

    // Suggested next problem: prefer an unsolved problem in the weakest topic,
    // else any unsolved, else a low-confidence solved problem to revisit.
    let suggested_problem = suggest_next(&conn, weakest_topic.as_deref())?;

    let goals = load_goals(&conn);
    let goal_progress = GoalProgress {
        intro: count_today("Intro"),
        easy: count_today("Easy"),
        medium: count_today("Medium"),
        hard: count_today("Hard"),
        reviews: reviews_done_today,
    };

    Ok(Dashboard {
        solved_today,
        study_seconds_today,
        reviews_due,
        current_streak: st.current_streak,
        weakest_topic,
        suggested_problem,
        goals,
        goal_progress,
        total_problems: st.total_problems,
        total_solved: st.total_solved,
    })
}

fn load_goals(conn: &Connection) -> Goals {
    let get = |k: &str, d: i64| -> i64 {
        repo::get_setting(conn, k)
            .ok()
            .flatten()
            .and_then(|v| v.parse().ok())
            .unwrap_or(d)
    };
    Goals {
        intro: get("goal_intro", 3),
        easy: get("goal_easy", 2),
        medium: get("goal_medium", 1),
        hard: get("goal_hard", 0),
        reviews: get("goal_reviews", 3),
    }
}

fn suggest_next(conn: &Connection, weakest_topic: Option<&str>) -> AppResult<Option<Problem>> {
    // 1) Unsolved in weakest topic.
    if let Some(topic) = weakest_topic {
        let id: Option<i64> = conn
            .query_row(
                "SELECT p.id FROM problems p
                 JOIN problem_tags pt ON pt.problem_id = p.id
                 JOIN tags t ON t.id = pt.tag_id
                 WHERE t.kind='topic' AND t.name=?1 AND p.solved_status != 'solved'
                 ORDER BY (p.difficulty='Intro') DESC, (p.difficulty='Easy') DESC, RANDOM() LIMIT 1",
                [topic],
                |r| r.get(0),
            )
            .ok();
        if let Some(id) = id {
            return Ok(Some(repo::get_problem(conn, id)?));
        }
    }
    // 2) Any unsolved.
    let id: Option<i64> = conn
        .query_row(
            "SELECT id FROM problems WHERE solved_status != 'solved'
             ORDER BY (difficulty='Easy') DESC, RANDOM() LIMIT 1",
            [],
            |r| r.get(0),
        )
        .ok();
    if let Some(id) = id {
        return Ok(Some(repo::get_problem(conn, id)?));
    }
    // 3) Lowest-confidence solved problem to revisit.
    let id: Option<i64> = conn
        .query_row(
            "SELECT id FROM problems ORDER BY confidence ASC, RANDOM() LIMIT 1",
            [],
            |r| r.get(0),
        )
        .ok();
    match id {
        Some(id) => Ok(Some(repo::get_problem(conn, id)?)),
        None => Ok(None),
    }
}

// ---------------------------------------------------------------------------
// Settings
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn get_settings(state: State<'_, AppState>) -> AppResult<std::collections::HashMap<String, String>> {
    repo::all_settings(&state.conn())
}

#[tauri::command]
pub fn set_setting(state: State<'_, AppState>, key: String, value: String) -> AppResult<()> {
    repo::set_setting(&state.conn(), &key, &value)
}

// ---------------------------------------------------------------------------
// Drafts + per-problem UI state (persisted in SQLite, captured by backups)
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn get_draft(
    state: State<'_, AppState>,
    problem_id: i64,
    language: String,
) -> AppResult<Option<String>> {
    repo::get_draft(&state.conn(), problem_id, &language)
}

#[tauri::command]
pub fn save_draft(
    state: State<'_, AppState>,
    problem_id: i64,
    language: String,
    code: String,
) -> AppResult<()> {
    repo::save_draft(&state.conn(), problem_id, &language, &code)
}

#[tauri::command]
pub fn get_hints_revealed(state: State<'_, AppState>, problem_id: i64) -> AppResult<i64> {
    repo::get_hints_revealed(&state.conn(), problem_id)
}

#[tauri::command]
pub fn set_hints_revealed(
    state: State<'_, AppState>,
    problem_id: i64,
    count: i64,
) -> AppResult<()> {
    repo::set_hints_revealed(&state.conn(), problem_id, count)
}

// ---------------------------------------------------------------------------
// Full database backup / restore
// ---------------------------------------------------------------------------

/// Write a consistent snapshot of the entire database (every table — problems,
/// notes, attempts, solutions, reviews, drafts, settings…) to `path`. Uses
/// `VACUUM INTO`, which is safe to run while the app is using the database.
#[tauri::command]
pub fn backup_database(state: State<'_, AppState>, path: String) -> AppResult<()> {
    // VACUUM INTO requires the destination not to exist.
    if std::path::Path::new(&path).exists() {
        std::fs::remove_file(&path)?;
    }
    let conn = state.conn();
    conn.execute("VACUUM INTO ?1", rusqlite::params![path])?;
    Ok(())
}

/// Replace the live database with a previously created backup. The current
/// connection is closed, the backup file copied over the database (WAL sidecars
/// removed), and a fresh connection opened. Validates the file looks like a
/// Poodcode database before clobbering anything.
#[tauri::command]
pub fn restore_database(state: State<'_, AppState>, path: String) -> AppResult<()> {
    let src = std::path::PathBuf::from(&path);
    if !src.exists() {
        return Err(AppError::Other("backup file does not exist".into()));
    }
    // Sanity-check the source before we overwrite the real database.
    {
        let probe = Connection::open(&src)?;
        let has_problems: i64 = probe
            .query_row(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='problems'",
                [],
                |r| r.get(0),
            )
            .unwrap_or(0);
        if has_problems == 0 {
            return Err(AppError::Other(
                "that file is not a Poodcode database".into(),
            ));
        }
    }

    let mut guard = state.conn();
    // Close the live connection (checkpointing WAL) by swapping in a throwaway.
    let _old = std::mem::replace(&mut *guard, Connection::open_in_memory()?);
    drop(_old);

    let base = &state.db_path;
    let wal = std::path::PathBuf::from(format!("{}-wal", base.display()));
    let shm = std::path::PathBuf::from(format!("{}-shm", base.display()));
    let _ = std::fs::remove_file(&wal);
    let _ = std::fs::remove_file(&shm);
    std::fs::copy(&src, base)?;

    *guard = crate::db::open(base)?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Learning recommendations (weakness → concepts + practice ladder)
// ---------------------------------------------------------------------------

#[derive(Debug, Serialize)]
pub struct ConceptRef {
    pub key: String,
    pub name: String,
}

#[derive(Debug, Serialize)]
pub struct ProblemRef {
    pub id: i64,
    pub title: String,
    pub difficulty: String,
    pub solved_status: String,
    pub confidence: i64,
}

#[derive(Debug, Serialize)]
pub struct TopicRecommendation {
    pub topic: String,
    pub solved: i64,
    pub total: i64,
    pub avg_confidence: f64,
    pub concepts: Vec<ConceptRef>,
    pub problems: Vec<ProblemRef>,
}

/// For each of the weakest topics, recommend concepts to study (drawn from the
/// prerequisites of that topic's problems) and a short practice ladder (easiest
/// unsolved first, then low-confidence solved problems to revisit).
#[tauri::command]
pub fn learning_recommendations(
    state: State<'_, AppState>,
) -> AppResult<Vec<TopicRecommendation>> {
    let conn = state.conn();
    let st = stats::compute(&conn)?;
    let mut out = Vec::new();
    for t in st.weakest_topics.iter().take(3) {
        out.push(TopicRecommendation {
            topic: t.topic.clone(),
            solved: t.solved,
            total: t.total,
            avg_confidence: t.avg_confidence,
            concepts: topic_concepts(&conn, &t.topic)?,
            problems: topic_practice_ladder(&conn, &t.topic)?,
        });
    }
    Ok(out)
}

/// Distinct prerequisite concepts across the problems tagged with `topic`.
fn topic_concepts(conn: &Connection, topic: &str) -> AppResult<Vec<ConceptRef>> {
    let mut stmt = conn.prepare(
        "SELECT p.prerequisites_json FROM problems p
         JOIN problem_tags pt ON pt.problem_id = p.id
         JOIN tags t ON t.id = pt.tag_id
         WHERE t.kind='topic' AND t.name=?1",
    )?;
    let rows = stmt.query_map([topic], |r| r.get::<_, String>(0))?;
    let mut seen = std::collections::HashSet::new();
    let mut out = Vec::new();
    for row in rows {
        let json = row?;
        let prereqs: Vec<crate::models::Prerequisite> =
            serde_json::from_str(&json).unwrap_or_default();
        for pr in prereqs {
            if pr.key.is_empty() || !seen.insert(pr.key.clone()) {
                continue;
            }
            out.push(ConceptRef {
                key: pr.key,
                name: pr.name,
            });
            if out.len() >= 5 {
                return Ok(out);
            }
        }
    }
    Ok(out)
}

/// A short, ordered set of problems to practice in `topic`: unsolved easiest
/// first, then low-confidence solved problems worth revisiting.
fn topic_practice_ladder(conn: &Connection, topic: &str) -> AppResult<Vec<ProblemRef>> {
    let mut stmt = conn.prepare(
        "SELECT DISTINCT p.id, p.title, p.difficulty, p.solved_status, p.confidence
         FROM problems p
         JOIN problem_tags pt ON pt.problem_id = p.id
         JOIN tags t ON t.id = pt.tag_id
         WHERE t.kind='topic' AND t.name=?1
         ORDER BY (p.solved_status != 'solved') DESC,
                  (p.difficulty='Intro') DESC, (p.difficulty='Easy') DESC,
                  (p.difficulty='Medium') DESC,
                  p.confidence ASC
         LIMIT 4",
    )?;
    let rows = stmt.query_map([topic], |r| {
        Ok(ProblemRef {
            id: r.get(0)?,
            title: r.get(1)?,
            difficulty: r.get(2)?,
            solved_status: r.get(3)?,
            confidence: r.get(4)?,
        })
    })?;
    Ok(rows.filter_map(|r| r.ok()).collect())
}

// ---------------------------------------------------------------------------
// Random practice / weakness search
// ---------------------------------------------------------------------------

/// Random practice honoring simple server-side predicates that are awkward on
/// the client (e.g. "not solved in N days", "failed at least twice").
#[tauri::command]
pub fn random_problem(
    state: State<'_, AppState>,
    difficulty: Option<String>,
    topic: Option<String>,
    predicate: Option<String>,
) -> AppResult<Option<Problem>> {
    let conn = state.conn();
    let mut sql = String::from(
        "SELECT DISTINCT p.id FROM problems p
         LEFT JOIN problem_tags pt ON pt.problem_id = p.id
         LEFT JOIN tags t ON t.id = pt.tag_id AND t.kind='topic'
         WHERE 1=1",
    );
    let mut args: Vec<String> = vec![];
    if let Some(d) = difficulty.filter(|d| !d.is_empty()) {
        args.push(d);
        sql.push_str(&format!(" AND p.difficulty = ?{}", args.len()));
    }
    if let Some(t) = topic.filter(|t| !t.is_empty()) {
        args.push(t);
        sql.push_str(&format!(" AND t.name = ?{}", args.len()));
    }
    match predicate.as_deref() {
        Some("unsolved") => sql.push_str(" AND p.solved_status != 'solved'"),
        Some("weak") => sql.push_str(" AND p.confidence <= 2 AND p.solved_status='solved'"),
        Some("stale60") => {
            sql.push_str(" AND (p.last_solved_at IS NULL OR p.last_solved_at < date('now','-60 day'))")
        }
        Some("failed_twice") => sql
            .push_str(" AND (p.attempts_count - p.success_count) >= 2"),
        Some("never_optimal") => sql.push_str(" AND p.confidence < 4"),
        _ => {}
    }
    sql.push_str(" ORDER BY RANDOM() LIMIT 1");

    let id: Option<i64> = {
        let mut stmt = conn.prepare(&sql)?;
        let params = rusqlite::params_from_iter(args.iter());
        stmt.query_row(params, |r| r.get(0)).ok()
    };
    match id {
        Some(id) => Ok(Some(repo::get_problem(&conn, id)?)),
        None => Ok(None),
    }
}

/// Add extra study time to today's session (used by the solve timer / interview
/// mode so study minutes are captured even without an accepted submission).
#[tauri::command]
pub fn log_study_time(state: State<'_, AppState>, seconds: i64) -> AppResult<()> {
    let conn = state.conn();
    let today = Local::now().date_naive().format("%Y-%m-%d").to_string();
    conn.execute(
        "INSERT INTO daily_sessions(date, study_seconds) VALUES(?1, ?2)
         ON CONFLICT(date) DO UPDATE SET study_seconds = study_seconds + ?2",
        rusqlite::params![today, seconds],
    )?;
    Ok(())
}

/// Small helper exposed for the timeline page: solved counts per month.
#[tauri::command]
pub fn timeline(state: State<'_, AppState>) -> AppResult<Vec<stats::CountPair>> {
    let st = stats::compute(&state.conn())?;
    Ok(st.monthly_activity)
}
