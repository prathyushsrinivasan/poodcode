use rusqlite::Connection;
use std::path::Path;

use crate::error::AppResult;

/// Normalized SQLite schema. Designed to be future-proof: tags cover
/// topics/subtopics/companies uniformly; execution/progress data is separated
/// from static problem content so problems can be re-imported without loss.
pub const SCHEMA: &str = r#"
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS problems (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  slug                TEXT UNIQUE NOT NULL,
  title               TEXT NOT NULL,
  difficulty          TEXT NOT NULL DEFAULT 'Medium',
  description         TEXT NOT NULL DEFAULT '',
  constraints         TEXT NOT NULL DEFAULT '',
  examples_json       TEXT NOT NULL DEFAULT '[]',
  editorial           TEXT NOT NULL DEFAULT '',
  optimal_time        TEXT NOT NULL DEFAULT '',
  optimal_space       TEXT NOT NULL DEFAULT '',
  optimal_explanation TEXT NOT NULL DEFAULT '',
  starter_json        TEXT NOT NULL DEFAULT '{}',
  hints_json          TEXT NOT NULL DEFAULT '[]',
  prerequisites_json  TEXT NOT NULL DEFAULT '[]',
  -- Richer judging + curriculum metadata (all optional / back-compatible).
  function_spec_json  TEXT NOT NULL DEFAULT '',    -- function-harness signature, empty = raw stdin mode
  judge_mode          TEXT NOT NULL DEFAULT 'exact', -- 'exact' | 'float' | 'unordered'
  float_tolerance     REAL NOT NULL DEFAULT 0,
  time_limit_ms       INTEGER NOT NULL DEFAULT 0,   -- 0 = use the global default
  editorials_json     TEXT NOT NULL DEFAULT '[]',   -- multiple approaches (brute→optimal)
  follow_ups_json     TEXT NOT NULL DEFAULT '[]',   -- linked variant problems
  is_favorite         INTEGER NOT NULL DEFAULT 0,
  solved_status       TEXT NOT NULL DEFAULT 'unsolved',
  confidence          INTEGER NOT NULL DEFAULT 0,
  last_solved_at      TEXT,
  time_taken_seconds  INTEGER NOT NULL DEFAULT 0,
  attempts_count      INTEGER NOT NULL DEFAULT 0,
  success_count       INTEGER NOT NULL DEFAULT 0,
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tags (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  name  TEXT NOT NULL,
  kind  TEXT NOT NULL, -- 'topic' | 'subtopic' | 'company'
  UNIQUE(name, kind)
);

CREATE TABLE IF NOT EXISTS problem_tags (
  problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  tag_id     INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (problem_id, tag_id)
);

CREATE TABLE IF NOT EXISTS test_cases (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  problem_id      INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  kind            TEXT NOT NULL DEFAULT 'user', -- 'hidden' | 'user' | 'example'
  name            TEXT NOT NULL DEFAULT '',
  input           TEXT NOT NULL DEFAULT '',
  expected_output TEXT NOT NULL DEFAULT '',
  ordering        INTEGER NOT NULL DEFAULT 0
);

-- Per-problem prerequisite checklist state (has the user checked a concept off).
CREATE TABLE IF NOT EXISTS prereq_status (
  problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  key        TEXT NOT NULL,
  known      INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (problem_id, key)
);

CREATE TABLE IF NOT EXISTS notes (
  problem_id INTEGER PRIMARY KEY REFERENCES problems(id) ON DELETE CASCADE,
  content    TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS solutions (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  problem_id       INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  title            TEXT NOT NULL DEFAULT '',
  language         TEXT NOT NULL DEFAULT '',
  code             TEXT NOT NULL DEFAULT '',
  time_complexity  TEXT NOT NULL DEFAULT '',
  space_complexity TEXT NOT NULL DEFAULT '',
  approach_kind    TEXT NOT NULL DEFAULT '',
  notes            TEXT NOT NULL DEFAULT '',
  created_at       TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS attempts (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  problem_id       INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  language         TEXT NOT NULL DEFAULT '',
  code             TEXT NOT NULL DEFAULT '',
  status           TEXT NOT NULL DEFAULT 'run',
  runtime_ms       INTEGER,
  memory_kb        INTEGER,
  passed           INTEGER NOT NULL DEFAULT 0,
  total            INTEGER NOT NULL DEFAULT 0,
  error_text       TEXT NOT NULL DEFAULT '',
  duration_seconds INTEGER NOT NULL DEFAULT 0,
  created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reviews (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  problem_id       INTEGER NOT NULL UNIQUE REFERENCES problems(id) ON DELETE CASCADE,
  due_date         TEXT NOT NULL,
  interval_index   INTEGER NOT NULL DEFAULT 0,
  -- SM-2 adaptive scheduling fields.
  ease             REAL NOT NULL DEFAULT 2.5,
  reps             INTEGER NOT NULL DEFAULT 0,
  lapses           INTEGER NOT NULL DEFAULT 0,
  interval_days    INTEGER NOT NULL DEFAULT 0,
  last_quality     INTEGER NOT NULL DEFAULT 0,
  last_reviewed_at TEXT,
  created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS daily_sessions (
  date            TEXT PRIMARY KEY,        -- YYYY-MM-DD
  problems_solved INTEGER NOT NULL DEFAULT 0,
  study_seconds   INTEGER NOT NULL DEFAULT 0,
  reviews_done    INTEGER NOT NULL DEFAULT 0,
  editorials_read INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- In-progress editor buffers, per problem and language. Persisted in SQLite (not
-- webview localStorage) so drafts survive cache clears and are captured by backups.
CREATE TABLE IF NOT EXISTS drafts (
  problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  language   TEXT NOT NULL,
  code       TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (problem_id, language)
);

-- Per-problem UI state that must persist (e.g. how many hints were revealed).
CREATE TABLE IF NOT EXISTS problem_ui (
  problem_id     INTEGER PRIMARY KEY REFERENCES problems(id) ON DELETE CASCADE,
  hints_revealed INTEGER NOT NULL DEFAULT 0,
  updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Reflection: tagged mistakes logged against a problem/attempt for aggregation.
CREATE TABLE IF NOT EXISTS mistakes (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  attempt_id INTEGER,
  category   TEXT NOT NULL,      -- e.g. 'off-by-one', 'wrong-ds', 'missed-edge-case', 'tle', 'misread'
  note       TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Learning paths: ordered curated problem sequences (curriculum tracks).
CREATE TABLE IF NOT EXISTS paths (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  key         TEXT UNIQUE NOT NULL,
  title       TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  ordering    INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS path_items (
  path_id    INTEGER NOT NULL REFERENCES paths(id) ON DELETE CASCADE,
  problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  ordering   INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (path_id, problem_id)
);

-- Contest mode: timed multi-problem sets with per-problem results + history.
CREATE TABLE IF NOT EXISTS contests (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  title            TEXT NOT NULL DEFAULT '',
  problem_ids_json TEXT NOT NULL DEFAULT '[]',
  duration_seconds INTEGER NOT NULL DEFAULT 3600,
  status           TEXT NOT NULL DEFAULT 'running', -- 'running' | 'finished'
  started_at       TEXT NOT NULL DEFAULT (datetime('now')),
  ended_at         TEXT
);
CREATE TABLE IF NOT EXISTS contest_results (
  contest_id   INTEGER NOT NULL REFERENCES contests(id) ON DELETE CASCADE,
  problem_id   INTEGER NOT NULL,
  solved       INTEGER NOT NULL DEFAULT 0,
  solved_at    TEXT,
  wrong_tries  INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (contest_id, problem_id)
);

-- Flashcards: spaced-repetition cards extracted from notes/concepts.
CREATE TABLE IF NOT EXISTS flashcards (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  front          TEXT NOT NULL,
  back           TEXT NOT NULL,
  source         TEXT NOT NULL DEFAULT '', -- e.g. 'problem:12' or 'concept:bfs'
  ease           REAL NOT NULL DEFAULT 2.5,
  reps           INTEGER NOT NULL DEFAULT 0,
  lapses         INTEGER NOT NULL DEFAULT 0,
  interval_days  INTEGER NOT NULL DEFAULT 0,
  due_date       TEXT NOT NULL,
  created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems(difficulty);
CREATE INDEX IF NOT EXISTS idx_problems_status ON problems(solved_status);
CREATE INDEX IF NOT EXISTS idx_test_cases_problem ON test_cases(problem_id);
CREATE INDEX IF NOT EXISTS idx_attempts_problem ON attempts(problem_id);
CREATE INDEX IF NOT EXISTS idx_solutions_problem ON solutions(problem_id);
CREATE INDEX IF NOT EXISTS idx_problem_tags_tag ON problem_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_reviews_due ON reviews(due_date);
CREATE INDEX IF NOT EXISTS idx_mistakes_problem ON mistakes(problem_id);
CREATE INDEX IF NOT EXISTS idx_path_items_path ON path_items(path_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_due ON flashcards(due_date);
"#;

/// Open (creating if needed) the database at `path`, applying the schema.
pub fn open(path: &Path) -> AppResult<Connection> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let conn = Connection::open(path)?;
    conn.execute_batch("PRAGMA journal_mode = WAL; PRAGMA synchronous = NORMAL;")?;
    conn.execute_batch(SCHEMA)?;
    migrate(&conn)?;
    Ok(conn)
}

/// Additive migrations for databases created by an earlier version. New tables
/// are handled by `CREATE TABLE IF NOT EXISTS`; new columns need an ALTER.
fn migrate(conn: &Connection) -> AppResult<()> {
    if !column_exists(conn, "problems", "prerequisites_json")? {
        conn.execute(
            "ALTER TABLE problems ADD COLUMN prerequisites_json TEXT NOT NULL DEFAULT '[]'",
            [],
        )?;
    }
    // New problem columns (rich judging + curriculum). Each guarded so existing
    // databases upgrade in place without data loss.
    let add_col = |table: &str, col: &str, decl: &str| -> AppResult<()> {
        if !column_exists(conn, table, col)? {
            conn.execute(&format!("ALTER TABLE {table} ADD COLUMN {col} {decl}"), [])?;
        }
        Ok(())
    };
    add_col("problems", "function_spec_json", "TEXT NOT NULL DEFAULT ''")?;
    add_col("problems", "judge_mode", "TEXT NOT NULL DEFAULT 'exact'")?;
    add_col("problems", "float_tolerance", "REAL NOT NULL DEFAULT 0")?;
    add_col("problems", "time_limit_ms", "INTEGER NOT NULL DEFAULT 0")?;
    add_col("problems", "editorials_json", "TEXT NOT NULL DEFAULT '[]'")?;
    add_col("problems", "follow_ups_json", "TEXT NOT NULL DEFAULT '[]'")?;
    // New review columns (SM-2 adaptive scheduling).
    add_col("reviews", "ease", "REAL NOT NULL DEFAULT 2.5")?;
    add_col("reviews", "reps", "INTEGER NOT NULL DEFAULT 0")?;
    add_col("reviews", "lapses", "INTEGER NOT NULL DEFAULT 0")?;
    add_col("reviews", "interval_days", "INTEGER NOT NULL DEFAULT 0")?;
    add_col("reviews", "last_quality", "INTEGER NOT NULL DEFAULT 0")?;
    Ok(())
}

fn column_exists(conn: &Connection, table: &str, column: &str) -> AppResult<bool> {
    let mut stmt = conn.prepare(&format!("PRAGMA table_info({table})"))?;
    let mut rows = stmt.query([])?;
    while let Some(row) = rows.next()? {
        let name: String = row.get(1)?;
        if name == column {
            return Ok(true);
        }
    }
    Ok(false)
}

/// Open an in-memory database (used for tests).
#[cfg(test)]
pub fn open_memory() -> AppResult<Connection> {
    let conn = Connection::open_in_memory()?;
    conn.execute_batch(SCHEMA)?;
    Ok(conn)
}

/// Returns the stored schema/seed version, or 0 if unset.
pub fn seed_version(conn: &Connection) -> i64 {
    conn.query_row(
        "SELECT value FROM meta WHERE key = 'seed_version'",
        [],
        |r| r.get::<_, String>(0),
    )
    .ok()
    .and_then(|s| s.parse::<i64>().ok())
    .unwrap_or(0)
}

pub fn set_seed_version(conn: &Connection, v: i64) -> AppResult<()> {
    conn.execute(
        "INSERT INTO meta(key, value) VALUES('seed_version', ?1)
         ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        [v.to_string()],
    )?;
    Ok(())
}
