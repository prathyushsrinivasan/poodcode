//! In-process SQL execution for the SQL learning track.
//!
//! Every other language in Poodcode runs as a **subprocess** over stdin/stdout
//! (see `exec.rs`). SQL cannot: there is no "SQL toolchain" to detect on PATH,
//! and shelling out to a `sqlite3` binary would make the whole track depend on
//! something that isn't installed on most machines. Instead SQL runs *inside the
//! app*, against a throwaway in-memory SQLite database built fresh for every
//! test case — the same SQLite (3.46, bundled by `rusqlite`) that stores the
//! learner's own progress.
//!
//! The judging contract mirrors the stdin/stdout one exactly, which is what lets
//! `judge.rs` treat SQL as just another language:
//!
//! | stdin/stdout languages     | SQL                                    |
//! |----------------------------|----------------------------------------|
//! | test case `input` -> stdin | test case `input` -> setup SQL (DDL + data) |
//! | program prints to stdout   | last result-returning statement -> a text grid |
//! | expected_output compared   | expected_output compared to that grid  |
//!
//! ## The rendered grid
//!
//! A result set renders as one header line of column names followed by one line
//! per row, cells joined by `" | "`. That format is deliberately both
//! machine-comparable and readable, so a failing case shows a diff a human can
//! actually read. Value rendering is defined precisely in [`render_value`] so
//! that the Python authoring tool (`tools/sql_defs.py`) can compute expected
//! outputs that agree byte-for-byte with this engine.
//!
//! ## Safety and limits
//!
//! The database is `:memory:`, discarded when the call returns, so a query can
//! neither see nor damage the learner's real data. On top of that:
//!
//! - a **progress handler** interrupts a query that outruns its wall clock (an
//!   accidental cartesian product is the single most common way a join exercise
//!   goes wrong, and it must not hang the UI);
//! - an **authorizer** refuses `ATTACH`/`DETACH`, the only SQL-level way an
//!   in-memory database could reach the filesystem;
//! - result sets are capped at [`MAX_ROWS`] rows and [`MAX_COLS`] columns.

use rusqlite::hooks::{AuthAction, Authorization};
use rusqlite::types::ValueRef;
use rusqlite::{Batch, Connection};
use serde::Serialize;
use std::time::{Duration, Instant};

/// Rows kept from one result set. Exercise answers are small; anything larger is
/// a runaway query, and truncating keeps both the comparison and the UI bounded.
pub const MAX_ROWS: usize = 500;
/// Columns kept from one result set (`SELECT *` on a wide join, mostly).
pub const MAX_COLS: usize = 64;
/// Rows shown per table in the dataset browser.
pub const MAX_PREVIEW_ROWS: usize = 200;
/// Virtual-machine steps between wall-clock checks. Small enough that a runaway
/// join is interrupted promptly, large enough that the callback is not hot.
const PROGRESS_OPS: i32 = 1000;

/// One result set, both as structured data (for the UI's table view) and as the
/// rendered text the judge compares.
#[derive(Debug, Clone, Serialize, Default)]
pub struct SqlGrid {
    pub columns: Vec<String>,
    pub rows: Vec<Vec<String>>,
    /// True if the result set hit [`MAX_ROWS`] or [`MAX_COLS`].
    pub truncated: bool,
}

/// The outcome of running one batch of learner SQL against one dataset.
#[derive(Debug, Clone, Serialize)]
pub struct SqlOut {
    /// The last result set produced, if any statement returned one.
    pub grid: Option<SqlGrid>,
    /// `grid` rendered for comparison; empty when there was no result set.
    pub text: String,
    /// SQLite's message, or ours, when the batch could not complete.
    pub error: String,
    /// True when the failure happened while *compiling* SQL (a syntax error, an
    /// unknown table or column) rather than while running it. `judge.rs` surfaces
    /// this the way it surfaces a compile error for Java.
    pub syntax_error: bool,
    pub timed_out: bool,
    pub row_count: i64,
    /// How many statements in the batch ran to completion.
    pub statements: i64,
    pub runtime_ms: i64,
}

impl SqlOut {
    fn failure(error: String, syntax_error: bool, timed_out: bool, runtime_ms: i64) -> Self {
        SqlOut {
            grid: None,
            text: String::new(),
            error,
            syntax_error,
            timed_out,
            row_count: 0,
            statements: 0,
            runtime_ms,
        }
    }

    pub fn ok(&self) -> bool {
        self.error.is_empty()
    }
}

/// One column of a table, as the dataset browser shows it.
#[derive(Debug, Clone, Serialize)]
pub struct SqlColumn {
    pub name: String,
    /// Declared type (`INTEGER`, `TEXT`, ...), empty when the column has none.
    pub decl_type: String,
    pub not_null: bool,
    pub primary_key: bool,
}

/// One table of a dataset: its shape, its `CREATE TABLE` text, and its rows.
#[derive(Debug, Clone, Serialize)]
pub struct SqlTable {
    pub name: String,
    pub ddl: String,
    pub columns: Vec<SqlColumn>,
    pub rows: Vec<Vec<String>>,
    pub row_count: i64,
    /// True if more rows exist than the [`MAX_PREVIEW_ROWS`] shown.
    pub truncated: bool,
}

/// Render one SQLite value as the exact text the judge compares.
///
/// The rules are fixed here and mirrored in `tools/sql_defs.py::render_value`,
/// because that tool *computes* every expected output by running the reference
/// query through Python's SQLite. Any divergence between the two renderers would
/// make correct answers fail, so `tests/verify_sql.rs` re-runs every authored
/// solution through *this* engine and asserts the outputs still match.
///
/// - `NULL` renders as the four characters `NULL` (distinct from an empty
///   string, which renders as nothing at all — the difference matters when
///   teaching outer joins).
/// - Integers render in decimal.
/// - Reals always carry a decimal point, so `3.0` never collapses to `3` and
///   silently compares equal to the integer `3`.
/// - Text renders verbatim, with newlines escaped so one row stays one line.
/// - Blobs render as `X'<uppercase hex>'`, matching SQLite's own literal syntax.
pub fn render_value(v: ValueRef<'_>) -> String {
    match v {
        ValueRef::Null => "NULL".to_string(),
        ValueRef::Integer(i) => i.to_string(),
        ValueRef::Real(f) => render_real(f),
        ValueRef::Text(bytes) => escape_cell(&String::from_utf8_lossy(bytes)),
        ValueRef::Blob(bytes) => {
            let mut s = String::with_capacity(bytes.len() * 2 + 3);
            s.push_str("X'");
            for b in bytes {
                s.push_str(&format!("{b:02X}"));
            }
            s.push('\'');
            s
        }
    }
}

/// Format a REAL so that it always reads as a float. Rust's `{}` prints `3` for
/// `3.0f64` while Python's `repr` prints `3.0`; appending the missing `.0` makes
/// the two agree. Both sides otherwise emit the shortest round-tripping decimal.
fn render_real(f: f64) -> String {
    if f.is_nan() {
        return "NaN".to_string();
    }
    if f.is_infinite() {
        return if f > 0.0 { "Inf".to_string() } else { "-Inf".to_string() };
    }
    let s = format!("{f}");
    if s.contains('.') || s.contains('e') || s.contains('E') {
        s
    } else {
        format!("{s}.0")
    }
}

/// Keep one cell on one line: a row is a line, so embedded newlines would break
/// the grid's line-per-row contract.
fn escape_cell(s: &str) -> String {
    s.replace('\r', "").replace('\n', "\\n")
}

impl SqlGrid {
    /// The comparison text: header line, then one line per row.
    pub fn render(&self) -> String {
        let mut out = self.columns.join(" | ");
        for row in &self.rows {
            out.push('\n');
            out.push_str(&row.join(" | "));
        }
        out
    }
}

/// Open a fresh in-memory database and apply the (trusted, authored) dataset SQL.
fn open_with(setup: &str) -> Result<Connection, String> {
    let conn = Connection::open_in_memory().map_err(|e| e.to_string())?;
    // Foreign keys are off by default in SQLite; the datasets declare them and
    // the lessons talk about them, so enforce them.
    conn.execute_batch("PRAGMA foreign_keys = ON;")
        .map_err(|e| e.to_string())?;
    if !setup.trim().is_empty() {
        conn.execute_batch(setup)
            .map_err(|e| format!("dataset setup failed: {e}"))?;
    }
    Ok(conn)
}

/// Refuse the only SQL-level escapes from an in-memory database to the disk.
fn lock_down(conn: &Connection) {
    conn.authorizer(Some(|ctx: rusqlite::hooks::AuthContext<'_>| match ctx.action {
        AuthAction::Attach { .. } | AuthAction::Detach { .. } => Authorization::Deny,
        _ => Authorization::Allow,
    }));
}

/// Interrupt anything still running after `deadline`.
fn arm_timeout(conn: &Connection, deadline: Instant) {
    conn.progress_handler(PROGRESS_OPS, Some(move || Instant::now() >= deadline));
}

/// True when this error is SQLite reporting that the progress handler stopped it.
fn is_interrupt(e: &rusqlite::Error) -> bool {
    matches!(
        e,
        rusqlite::Error::SqliteFailure(err, _)
            if err.code == rusqlite::ErrorCode::OperationInterrupted
    )
}

/// Build a dataset, then run the learner's SQL batch against it.
///
/// Every statement in `sql` executes in order; the **last one that returns rows**
/// becomes the output. That allows a `CREATE INDEX` (or a `WITH RECURSIVE` setup,
/// or an `UPDATE` followed by a verifying `SELECT`) before the answer query,
/// while keeping "what gets compared" unambiguous.
pub fn run(setup: &str, sql: &str, timeout: Duration) -> SqlOut {
    let start = Instant::now();
    let conn = match open_with(setup) {
        Ok(c) => c,
        Err(e) => return SqlOut::failure(e, false, false, start.elapsed().as_millis() as i64),
    };
    lock_down(&conn);
    arm_timeout(&conn, start + timeout);

    if sql.trim().is_empty() {
        return SqlOut::failure(
            "no SQL to run — write a query first".into(),
            true,
            false,
            start.elapsed().as_millis() as i64,
        );
    }

    let mut grid: Option<SqlGrid> = None;
    let mut statements = 0i64;
    let mut batch = Batch::new(&conn, sql);

    loop {
        // `Batch::next` compiles the next statement; a failure here is a
        // compile-time problem (bad syntax, unknown table/column).
        let mut stmt = match batch.next() {
            Ok(Some(s)) => s,
            Ok(None) => break,
            Err(e) => {
                let ms = start.elapsed().as_millis() as i64;
                let timed_out = is_interrupt(&e);
                let msg = if timed_out {
                    format!("query timed out after {} ms", timeout.as_millis())
                } else {
                    e.to_string()
                };
                return SqlOut::failure(msg, !timed_out, timed_out, ms);
            }
        };

        let ncol = stmt.column_count();
        let mut columns: Vec<String> = stmt
            .column_names()
            .iter()
            .take(MAX_COLS)
            .map(|s| s.to_string())
            .collect();
        let mut truncated = ncol > MAX_COLS;
        let keep = columns.len();

        let mut rows_out: Vec<Vec<String>> = Vec::new();
        let mut rows = stmt.raw_query();
        loop {
            match rows.next() {
                // A statement with no columns (INSERT, CREATE, UPDATE) runs to
                // completion here and yields nothing; that is how it executes.
                Ok(Some(row)) => {
                    if keep == 0 {
                        continue;
                    }
                    if rows_out.len() >= MAX_ROWS {
                        truncated = true;
                        break;
                    }
                    let mut cells = Vec::with_capacity(keep);
                    for i in 0..keep {
                        match row.get_ref(i) {
                            Ok(v) => cells.push(render_value(v)),
                            Err(e) => {
                                return SqlOut::failure(
                                    e.to_string(),
                                    false,
                                    false,
                                    start.elapsed().as_millis() as i64,
                                )
                            }
                        }
                    }
                    rows_out.push(cells);
                }
                Ok(None) => break,
                Err(e) => {
                    let ms = start.elapsed().as_millis() as i64;
                    let timed_out = is_interrupt(&e);
                    let msg = if timed_out {
                        format!("query timed out after {} ms", timeout.as_millis())
                    } else {
                        e.to_string()
                    };
                    return SqlOut::failure(msg, false, timed_out, ms);
                }
            }
        }
        statements += 1;
        if keep > 0 {
            columns.truncate(keep);
            grid = Some(SqlGrid { columns, rows: rows_out, truncated });
        }
    }

    let runtime_ms = start.elapsed().as_millis() as i64;
    match grid {
        Some(g) => {
            let text = g.render();
            let row_count = g.rows.len() as i64;
            SqlOut {
                grid: Some(g),
                text,
                error: String::new(),
                syntax_error: false,
                timed_out: false,
                row_count,
                statements,
                runtime_ms,
            }
        }
        None => SqlOut::failure(
            "that SQL ran but returned no result set — the last statement has to be a SELECT"
                .into(),
            false,
            false,
            runtime_ms,
        ),
    }
}

/// Introspect a dataset for the UI's schema/data browser: every user table with
/// its `CREATE TABLE` text, column metadata, and rows.
pub fn dataset_tables(setup: &str) -> Result<Vec<SqlTable>, String> {
    let conn = open_with(setup)?;
    lock_down(&conn);

    let names: Vec<(String, String)> = {
        let mut stmt = conn
            .prepare(
                "SELECT name, COALESCE(sql, '') FROM sqlite_schema \
                 WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
            )
            .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)))
            .map_err(|e| e.to_string())?;
        rows.collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())?
    };

    let mut tables = Vec::with_capacity(names.len());
    for (name, ddl) in names {
        // `PRAGMA table_info` is not parameterizable, and the name comes from
        // sqlite_schema rather than from user input; quote it defensively anyway.
        let quoted = format!("\"{}\"", name.replace('"', "\"\""));
        let columns: Vec<SqlColumn> = {
            let mut stmt = conn
                .prepare(&format!("PRAGMA table_info({quoted})"))
                .map_err(|e| e.to_string())?;
            let rows = stmt
                .query_map([], |r| {
                    Ok(SqlColumn {
                        name: r.get::<_, String>(1)?,
                        decl_type: r.get::<_, String>(2)?,
                        not_null: r.get::<_, i64>(3)? != 0,
                        primary_key: r.get::<_, i64>(5)? != 0,
                    })
                })
                .map_err(|e| e.to_string())?;
            rows.collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())?
        };

        let row_count: i64 = conn
            .query_row(&format!("SELECT COUNT(*) FROM {quoted}"), [], |r| r.get(0))
            .map_err(|e| e.to_string())?;

        let mut data: Vec<Vec<String>> = Vec::new();
        {
            let mut stmt = conn
                .prepare(&format!("SELECT * FROM {quoted} LIMIT {}", MAX_PREVIEW_ROWS))
                .map_err(|e| e.to_string())?;
            let ncol = stmt.column_count();
            let mut rows = stmt.raw_query();
            while let Some(row) = rows.next().map_err(|e| e.to_string())? {
                let mut cells = Vec::with_capacity(ncol);
                for i in 0..ncol {
                    cells.push(render_value(row.get_ref(i).map_err(|e| e.to_string())?));
                }
                data.push(cells);
            }
        }

        let truncated = row_count > data.len() as i64;
        tables.push(SqlTable { name, ddl, columns, rows: data, row_count, truncated });
    }
    Ok(tables)
}

#[cfg(test)]
mod tests {
    use super::*;

    const SETUP: &str = "CREATE TABLE t(id INTEGER PRIMARY KEY, name TEXT, score REAL);\
        INSERT INTO t VALUES (1,'a',3.0),(2,'b',2.5),(3,NULL,NULL);";
    const T: Duration = Duration::from_secs(5);

    #[test]
    fn renders_header_and_rows() {
        let out = run(SETUP, "SELECT id, name FROM t ORDER BY id;", T);
        assert!(out.ok(), "{}", out.error);
        assert_eq!(out.text, "id | name\n1 | a\n2 | b\n3 | NULL");
        assert_eq!(out.row_count, 3);
    }

    #[test]
    fn empty_result_still_has_a_header() {
        let out = run(SETUP, "SELECT id FROM t WHERE id > 99;", T);
        assert!(out.ok(), "{}", out.error);
        assert_eq!(out.text, "id");
        assert_eq!(out.row_count, 0);
    }

    #[test]
    fn reals_keep_their_decimal_point() {
        let out = run(SETUP, "SELECT score FROM t WHERE id = 1;", T);
        assert_eq!(out.text, "score\n3.0");
    }

    #[test]
    fn null_is_distinct_from_empty_text() {
        let out = run(SETUP, "SELECT NULL AS a, '' AS b;", T);
        assert_eq!(out.text, "a | b\nNULL | ");
    }

    #[test]
    fn last_result_set_wins_over_earlier_statements() {
        let out = run(
            SETUP,
            "CREATE INDEX ix ON t(name); SELECT COUNT(*) AS n FROM t;",
            T,
        );
        assert!(out.ok(), "{}", out.error);
        assert_eq!(out.text, "n\n3");
        assert_eq!(out.statements, 2);
    }

    #[test]
    fn syntax_errors_are_flagged_as_compile_time() {
        let out = run(SETUP, "SELEKT * FROM t;", T);
        assert!(!out.ok());
        assert!(out.syntax_error, "{}", out.error);
    }

    #[test]
    fn unknown_column_is_a_compile_time_error() {
        let out = run(SETUP, "SELECT nope FROM t;", T);
        assert!(out.syntax_error, "{}", out.error);
        assert!(out.error.contains("nope"), "{}", out.error);
    }

    #[test]
    fn a_batch_with_no_query_is_an_error() {
        let out = run(SETUP, "UPDATE t SET name = 'z' WHERE id = 1;", T);
        assert!(!out.ok());
        assert!(out.error.contains("SELECT"), "{}", out.error);
    }

    #[test]
    fn a_runaway_join_is_interrupted_not_hung() {
        // Five-way cross product over a recursive 400-row table: ~10^13 rows.
        let sql = "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n WHERE x < 400) \
                   SELECT COUNT(*) AS c FROM n a, n b, n c, n d, n e;";
        let out = run(SETUP, sql, Duration::from_millis(300));
        assert!(out.timed_out, "expected a timeout, got: {out:?}");
        assert!(!out.syntax_error);
    }

    #[test]
    fn attaching_a_file_is_refused() {
        let out = run(SETUP, "ATTACH DATABASE 'evil.db' AS evil; SELECT 1 AS x;", T);
        assert!(!out.ok());
        assert!(
            out.error.to_lowercase().contains("not authorized"),
            "{}",
            out.error
        );
    }

    #[test]
    fn the_database_does_not_persist_between_runs() {
        let a = run(SETUP, "CREATE TABLE scratch(x); INSERT INTO scratch VALUES (1); SELECT COUNT(*) AS n FROM scratch;", T);
        assert!(a.ok(), "{}", a.error);
        let b = run(SETUP, "SELECT COUNT(*) AS n FROM scratch;", T);
        assert!(b.syntax_error, "second run still saw the table: {b:?}");
    }

    #[test]
    fn dataset_browser_reports_shape_and_rows() {
        let tables = dataset_tables(SETUP).expect("introspection works");
        assert_eq!(tables.len(), 1);
        let t = &tables[0];
        assert_eq!(t.name, "t");
        assert_eq!(t.row_count, 3);
        assert_eq!(t.columns.len(), 3);
        assert!(t.columns[0].primary_key);
        assert_eq!(t.columns[2].decl_type, "REAL");
        assert_eq!(t.rows[2], vec!["3", "NULL", "NULL"]);
    }

    #[test]
    fn foreign_keys_are_enforced() {
        let setup = "CREATE TABLE p(id INTEGER PRIMARY KEY); \
                     CREATE TABLE c(id INTEGER PRIMARY KEY, p_id INTEGER REFERENCES p(id)); \
                     INSERT INTO p VALUES (1);";
        let out = run(setup, "INSERT INTO c VALUES (1, 99); SELECT 1 AS x;", T);
        assert!(!out.ok());
        assert!(out.error.to_lowercase().contains("foreign key"), "{}", out.error);
    }
}
