use chrono::{Duration, Local, NaiveDate};
use rusqlite::{params, Connection, OptionalExtension};
use std::collections::HashMap;

use crate::error::{AppError, AppResult};
use crate::models::*;

/// Spaced-repetition interval ladder, in days. Mirrored in the frontend
/// (`src/lib/revision.ts`) which carries the unit tests for this logic.
pub const LADDER: [i64; 6] = [1, 3, 7, 14, 30, 90];

fn today() -> NaiveDate {
    Local::now().date_naive()
}

fn now_iso() -> String {
    Local::now().format("%Y-%m-%d %H:%M:%S").to_string()
}

// ---------------------------------------------------------------------------
// Tags
// ---------------------------------------------------------------------------

fn upsert_tag(conn: &Connection, name: &str, kind: &str) -> AppResult<i64> {
    let name = name.trim();
    if name.is_empty() {
        return Err(AppError::Other("empty tag".into()));
    }
    conn.execute(
        "INSERT OR IGNORE INTO tags(name, kind) VALUES(?1, ?2)",
        params![name, kind],
    )?;
    let id = conn.query_row(
        "SELECT id FROM tags WHERE name = ?1 AND kind = ?2",
        params![name, kind],
        |r| r.get(0),
    )?;
    Ok(id)
}

fn tags_for(conn: &Connection, problem_id: i64, kind: &str) -> AppResult<Vec<String>> {
    let mut stmt = conn.prepare(
        "SELECT t.name FROM tags t
         JOIN problem_tags pt ON pt.tag_id = t.id
         WHERE pt.problem_id = ?1 AND t.kind = ?2
         ORDER BY t.name",
    )?;
    let rows = stmt.query_map(params![problem_id, kind], |r| r.get::<_, String>(0))?;
    Ok(rows.filter_map(|r| r.ok()).collect())
}

fn set_tags(conn: &Connection, problem_id: i64, names: &[String], kind: &str) -> AppResult<()> {
    // Remove existing links of this kind, then re-link.
    conn.execute(
        "DELETE FROM problem_tags WHERE problem_id = ?1 AND tag_id IN
           (SELECT id FROM tags WHERE kind = ?2)",
        params![problem_id, kind],
    )?;
    for name in names {
        let tag_id = upsert_tag(conn, name, kind)?;
        conn.execute(
            "INSERT OR IGNORE INTO problem_tags(problem_id, tag_id) VALUES(?1, ?2)",
            params![problem_id, tag_id],
        )?;
    }
    Ok(())
}

/// Distinct tag names of a given kind across the whole library (for filters).
pub fn distinct_tags(conn: &Connection, kind: &str) -> AppResult<Vec<String>> {
    let mut stmt =
        conn.prepare("SELECT DISTINCT name FROM tags WHERE kind = ?1 ORDER BY name")?;
    let rows = stmt.query_map(params![kind], |r| r.get::<_, String>(0))?;
    Ok(rows.filter_map(|r| r.ok()).collect())
}

// ---------------------------------------------------------------------------
// Problems
// ---------------------------------------------------------------------------

fn hydrate_problem(conn: &Connection, id: i64, include_heavy: bool) -> AppResult<Problem> {
    let mut p = conn
        .query_row(
            "SELECT id, slug, title, difficulty, description, constraints, examples_json,
                    editorial, optimal_time, optimal_space, optimal_explanation, starter_json,
                    hints_json, is_favorite, solved_status, confidence, last_solved_at,
                    time_taken_seconds, attempts_count, success_count, created_at, updated_at,
                    prerequisites_json, function_spec_json, judge_mode, float_tolerance,
                    time_limit_ms, editorials_json, follow_ups_json
             FROM problems WHERE id = ?1",
            params![id],
            |r| {
                let examples_json: String = r.get(6)?;
                let starter_json: String = r.get(11)?;
                let hints_json: String = r.get(12)?;
                let prerequisites_json: String = r.get(22)?;
                let function_spec_json: String = r.get(23)?;
                let editorials_json: String = r.get(27)?;
                let follow_ups_json: String = r.get(28)?;
                Ok(Problem {
                    id: r.get(0)?,
                    slug: r.get(1)?,
                    title: r.get(2)?,
                    difficulty: r.get(3)?,
                    description: if include_heavy { r.get(4)? } else { String::new() },
                    constraints: r.get(5)?,
                    examples: serde_json::from_str(&examples_json).unwrap_or_default(),
                    editorial: if include_heavy { r.get(7)? } else { String::new() },
                    optimal_time: r.get(8)?,
                    optimal_space: r.get(9)?,
                    optimal_explanation: if include_heavy { r.get(10)? } else { String::new() },
                    starter_code: serde_json::from_str(&starter_json).unwrap_or_default(),
                    hints: if include_heavy {
                        serde_json::from_str(&hints_json).unwrap_or_default()
                    } else {
                        Vec::new()
                    },
                    prerequisites: if include_heavy {
                        serde_json::from_str(&prerequisites_json).unwrap_or_default()
                    } else {
                        Vec::new()
                    },
                    function_spec: if function_spec_json.trim().is_empty() {
                        None
                    } else {
                        serde_json::from_str(&function_spec_json).ok()
                    },
                    judge_mode: r.get(24)?,
                    float_tolerance: r.get(25)?,
                    time_limit_ms: r.get(26)?,
                    editorials: if include_heavy {
                        serde_json::from_str(&editorials_json).unwrap_or_default()
                    } else {
                        Vec::new()
                    },
                    follow_ups: if include_heavy {
                        serde_json::from_str(&follow_ups_json).unwrap_or_default()
                    } else {
                        Vec::new()
                    },
                    patterns: Vec::new(),
                    topics: Vec::new(),
                    subtopics: Vec::new(),
                    companies: Vec::new(),
                    test_cases: Vec::new(),
                    is_favorite: r.get::<_, i64>(13)? != 0,
                    solved_status: r.get(14)?,
                    confidence: r.get(15)?,
                    last_solved_at: r.get(16)?,
                    time_taken_seconds: r.get(17)?,
                    attempts_count: r.get(18)?,
                    success_count: r.get(19)?,
                    created_at: r.get(20)?,
                    updated_at: r.get(21)?,
                })
            },
        )
        .optional()?
        .ok_or_else(|| AppError::NotFound(format!("problem {id}")))?;

    p.topics = tags_for(conn, id, "topic")?;
    p.subtopics = tags_for(conn, id, "subtopic")?;
    p.companies = tags_for(conn, id, "company")?;
    p.patterns = tags_for(conn, id, "pattern")?;
    if include_heavy {
        p.test_cases = list_test_cases(conn, id)?;
    }
    Ok(p)
}

pub fn get_problem(conn: &Connection, id: i64) -> AppResult<Problem> {
    hydrate_problem(conn, id, true)
}

pub fn list_problems(conn: &Connection) -> AppResult<Vec<Problem>> {
    let ids: Vec<i64> = {
        let mut stmt = conn.prepare("SELECT id FROM problems ORDER BY id")?;
        let rows = stmt.query_map([], |r| r.get::<_, i64>(0))?;
        rows.filter_map(|r| r.ok()).collect()
    };
    let mut out = Vec::with_capacity(ids.len());
    for id in ids {
        out.push(hydrate_problem(conn, id, false)?);
    }
    Ok(out)
}

/// Insert or update a problem by slug. Returns the problem id. Progress fields
/// are preserved on update (only static content + tags + tests are replaced).
pub fn upsert_problem(conn: &Connection, p: &Problem) -> AppResult<i64> {
    let examples_json = serde_json::to_string(&p.examples)?;
    let starter_json = serde_json::to_string(&p.starter_code)?;
    let hints_json = serde_json::to_string(&p.hints)?;
    let prerequisites_json = serde_json::to_string(&p.prerequisites)?;
    let function_spec_json = match &p.function_spec {
        Some(fs) => serde_json::to_string(fs)?,
        None => String::new(),
    };
    let editorials_json = serde_json::to_string(&p.editorials)?;
    let follow_ups_json = serde_json::to_string(&p.follow_ups)?;

    let existing: Option<i64> = conn
        .query_row(
            "SELECT id FROM problems WHERE slug = ?1",
            params![p.slug],
            |r| r.get(0),
        )
        .optional()?;

    let id = if let Some(id) = existing {
        conn.execute(
            "UPDATE problems SET title=?2, difficulty=?3, description=?4, constraints=?5,
                examples_json=?6, editorial=?7, optimal_time=?8, optimal_space=?9,
                optimal_explanation=?10, starter_json=?11, hints_json=?12, updated_at=?13,
                prerequisites_json=?14, function_spec_json=?15, judge_mode=?16,
                float_tolerance=?17, time_limit_ms=?18, editorials_json=?19, follow_ups_json=?20
             WHERE id=?1",
            params![
                id, p.title, p.difficulty, p.description, p.constraints, examples_json,
                p.editorial, p.optimal_time, p.optimal_space, p.optimal_explanation,
                starter_json, hints_json, now_iso(), prerequisites_json, function_spec_json,
                p.judge_mode, p.float_tolerance, p.time_limit_ms, editorials_json, follow_ups_json
            ],
        )?;
        id
    } else {
        conn.execute(
            "INSERT INTO problems(slug, title, difficulty, description, constraints,
                examples_json, editorial, optimal_time, optimal_space, optimal_explanation,
                starter_json, hints_json, prerequisites_json, function_spec_json, judge_mode,
                float_tolerance, time_limit_ms, editorials_json, follow_ups_json)
             VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17,?18,?19)",
            params![
                p.slug, p.title, p.difficulty, p.description, p.constraints, examples_json,
                p.editorial, p.optimal_time, p.optimal_space, p.optimal_explanation,
                starter_json, hints_json, prerequisites_json, function_spec_json, p.judge_mode,
                p.float_tolerance, p.time_limit_ms, editorials_json, follow_ups_json
            ],
        )?;
        conn.last_insert_rowid()
    };

    set_tags(conn, id, &p.topics, "topic")?;
    set_tags(conn, id, &p.subtopics, "subtopic")?;
    set_tags(conn, id, &p.companies, "company")?;
    set_tags(conn, id, &p.patterns, "pattern")?;

    // Replace hidden/example test cases; keep user-authored ones on re-import.
    conn.execute(
        "DELETE FROM test_cases WHERE problem_id = ?1 AND kind IN ('hidden','example')",
        params![id],
    )?;
    for (i, tc) in p.test_cases.iter().enumerate() {
        if tc.kind == "user" {
            continue; // never overwrite user cases via import
        }
        conn.execute(
            "INSERT INTO test_cases(problem_id, kind, name, input, expected_output, ordering)
             VALUES(?1,?2,?3,?4,?5,?6)",
            params![id, tc.kind, tc.name, tc.input, tc.expected_output, i as i64],
        )?;
    }
    Ok(id)
}

pub fn delete_problem(conn: &Connection, id: i64) -> AppResult<()> {
    conn.execute("DELETE FROM problems WHERE id = ?1", params![id])?;
    Ok(())
}

pub fn set_favorite(conn: &Connection, id: i64, fav: bool) -> AppResult<()> {
    conn.execute(
        "UPDATE problems SET is_favorite = ?2, updated_at = ?3 WHERE id = ?1",
        params![id, fav as i64, now_iso()],
    )?;
    Ok(())
}

pub fn set_confidence(conn: &Connection, id: i64, confidence: i64) -> AppResult<()> {
    conn.execute(
        "UPDATE problems SET confidence = ?2, updated_at = ?3 WHERE id = ?1",
        params![id, confidence.clamp(0, 5), now_iso()],
    )?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Test cases
// ---------------------------------------------------------------------------

pub fn list_test_cases(conn: &Connection, problem_id: i64) -> AppResult<Vec<TestCase>> {
    let mut stmt = conn.prepare(
        "SELECT id, problem_id, kind, name, input, expected_output, ordering
         FROM test_cases WHERE problem_id = ?1 ORDER BY ordering, id",
    )?;
    let rows = stmt.query_map(params![problem_id], |r| {
        Ok(TestCase {
            id: r.get(0)?,
            problem_id: r.get(1)?,
            kind: r.get(2)?,
            name: r.get(3)?,
            input: r.get(4)?,
            expected_output: r.get(5)?,
            ordering: r.get(6)?,
        })
    })?;
    Ok(rows.filter_map(|r| r.ok()).collect())
}

pub fn save_test_case(conn: &Connection, tc: &TestCase) -> AppResult<i64> {
    if tc.id > 0 {
        conn.execute(
            "UPDATE test_cases SET kind=?2, name=?3, input=?4, expected_output=?5, ordering=?6
             WHERE id=?1",
            params![tc.id, tc.kind, tc.name, tc.input, tc.expected_output, tc.ordering],
        )?;
        Ok(tc.id)
    } else {
        conn.execute(
            "INSERT INTO test_cases(problem_id, kind, name, input, expected_output, ordering)
             VALUES(?1,?2,?3,?4,?5,?6)",
            params![tc.problem_id, tc.kind, tc.name, tc.input, tc.expected_output, tc.ordering],
        )?;
        Ok(conn.last_insert_rowid())
    }
}

pub fn delete_test_case(conn: &Connection, id: i64) -> AppResult<()> {
    conn.execute("DELETE FROM test_cases WHERE id = ?1", params![id])?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Prerequisite checklist status (per problem)
// ---------------------------------------------------------------------------

/// Concept keys the user has marked as "known" for this problem.
pub fn known_prereqs(conn: &Connection, problem_id: i64) -> AppResult<Vec<String>> {
    let mut stmt =
        conn.prepare("SELECT key FROM prereq_status WHERE problem_id = ?1 AND known = 1")?;
    let rows = stmt.query_map(params![problem_id], |r| r.get::<_, String>(0))?;
    Ok(rows.filter_map(|r| r.ok()).collect())
}

pub fn set_prereq_status(
    conn: &Connection,
    problem_id: i64,
    key: &str,
    known: bool,
) -> AppResult<()> {
    conn.execute(
        "INSERT INTO prereq_status(problem_id, key, known, updated_at) VALUES(?1, ?2, ?3, ?4)
         ON CONFLICT(problem_id, key) DO UPDATE SET known = excluded.known, updated_at = excluded.updated_at",
        params![problem_id, key, known as i64, now_iso()],
    )?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Notes
// ---------------------------------------------------------------------------

pub fn get_note(conn: &Connection, problem_id: i64) -> AppResult<Note> {
    let note = conn
        .query_row(
            "SELECT problem_id, content, updated_at FROM notes WHERE problem_id = ?1",
            params![problem_id],
            |r| {
                Ok(Note {
                    problem_id: r.get(0)?,
                    content: r.get(1)?,
                    updated_at: r.get(2)?,
                })
            },
        )
        .optional()?
        .unwrap_or(Note {
            problem_id,
            content: String::new(),
            updated_at: String::new(),
        });
    Ok(note)
}

pub fn save_note(conn: &Connection, problem_id: i64, content: &str) -> AppResult<()> {
    conn.execute(
        "INSERT INTO notes(problem_id, content, updated_at) VALUES(?1, ?2, ?3)
         ON CONFLICT(problem_id) DO UPDATE SET content=excluded.content, updated_at=excluded.updated_at",
        params![problem_id, content, now_iso()],
    )?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Solutions
// ---------------------------------------------------------------------------

pub fn list_solutions(conn: &Connection, problem_id: i64) -> AppResult<Vec<Solution>> {
    let mut stmt = conn.prepare(
        "SELECT id, problem_id, title, language, code, time_complexity, space_complexity,
                approach_kind, notes, created_at, updated_at
         FROM solutions WHERE problem_id = ?1 ORDER BY id",
    )?;
    let rows = stmt.query_map(params![problem_id], |r| {
        Ok(Solution {
            id: r.get(0)?,
            problem_id: r.get(1)?,
            title: r.get(2)?,
            language: r.get(3)?,
            code: r.get(4)?,
            time_complexity: r.get(5)?,
            space_complexity: r.get(6)?,
            approach_kind: r.get(7)?,
            notes: r.get(8)?,
            created_at: r.get(9)?,
            updated_at: r.get(10)?,
        })
    })?;
    Ok(rows.filter_map(|r| r.ok()).collect())
}

pub fn save_solution(conn: &Connection, s: &Solution) -> AppResult<i64> {
    if s.id > 0 {
        conn.execute(
            "UPDATE solutions SET title=?2, language=?3, code=?4, time_complexity=?5,
                space_complexity=?6, approach_kind=?7, notes=?8, updated_at=?9 WHERE id=?1",
            params![
                s.id, s.title, s.language, s.code, s.time_complexity, s.space_complexity,
                s.approach_kind, s.notes, now_iso()
            ],
        )?;
        Ok(s.id)
    } else {
        conn.execute(
            "INSERT INTO solutions(problem_id, title, language, code, time_complexity,
                space_complexity, approach_kind, notes)
             VALUES(?1,?2,?3,?4,?5,?6,?7,?8)",
            params![
                s.problem_id, s.title, s.language, s.code, s.time_complexity,
                s.space_complexity, s.approach_kind, s.notes
            ],
        )?;
        Ok(conn.last_insert_rowid())
    }
}

pub fn delete_solution(conn: &Connection, id: i64) -> AppResult<()> {
    conn.execute("DELETE FROM solutions WHERE id = ?1", params![id])?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Attempts + progress
// ---------------------------------------------------------------------------

pub fn record_attempt(conn: &Connection, a: &Attempt) -> AppResult<i64> {
    conn.execute(
        "INSERT INTO attempts(problem_id, language, code, status, runtime_ms, memory_kb,
            passed, total, error_text, duration_seconds)
         VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,?10)",
        params![
            a.problem_id, a.language, a.code, a.status, a.runtime_ms, a.memory_kb,
            a.passed, a.total, a.error_text, a.duration_seconds
        ],
    )?;
    let id = conn.last_insert_rowid();

    // Update problem aggregate progress.
    let accepted = a.status == "accepted";
    conn.execute(
        "UPDATE problems SET attempts_count = attempts_count + 1,
            success_count = success_count + ?2,
            time_taken_seconds = time_taken_seconds + ?3,
            solved_status = CASE WHEN ?4 THEN 'solved'
                                 WHEN solved_status = 'solved' THEN 'solved'
                                 ELSE 'attempted' END,
            last_solved_at = CASE WHEN ?4 THEN ?5 ELSE last_solved_at END,
            updated_at = ?5
         WHERE id = ?1",
        params![
            a.problem_id,
            accepted as i64,
            a.duration_seconds,
            accepted,
            now_iso()
        ],
    )?;

    if accepted {
        bump_daily(conn, true, a.duration_seconds)?;
        schedule_after_solve(conn, a.problem_id)?;
    } else {
        bump_daily(conn, false, a.duration_seconds)?;
    }
    Ok(id)
}

pub fn list_attempts(conn: &Connection, problem_id: i64) -> AppResult<Vec<Attempt>> {
    let mut stmt = conn.prepare(
        "SELECT id, problem_id, language, code, status, runtime_ms, memory_kb, passed, total,
                error_text, duration_seconds, created_at
         FROM attempts WHERE problem_id = ?1 ORDER BY id DESC",
    )?;
    let rows = stmt.query_map(params![problem_id], |r| {
        Ok(Attempt {
            id: r.get(0)?,
            problem_id: r.get(1)?,
            language: r.get(2)?,
            code: r.get(3)?,
            status: r.get(4)?,
            runtime_ms: r.get(5)?,
            memory_kb: r.get(6)?,
            passed: r.get(7)?,
            total: r.get(8)?,
            error_text: r.get(9)?,
            duration_seconds: r.get(10)?,
            created_at: r.get(11)?,
        })
    })?;
    Ok(rows.filter_map(|r| r.ok()).collect())
}

// ---------------------------------------------------------------------------
// Daily sessions
// ---------------------------------------------------------------------------

fn bump_daily(conn: &Connection, solved: bool, seconds: i64) -> AppResult<()> {
    let date = today().format("%Y-%m-%d").to_string();
    conn.execute(
        "INSERT INTO daily_sessions(date, problems_solved, study_seconds)
         VALUES(?1, ?2, ?3)
         ON CONFLICT(date) DO UPDATE SET
            problems_solved = problems_solved + ?2,
            study_seconds = study_seconds + ?3",
        params![date, solved as i64, seconds],
    )?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Revision (spaced repetition)
// ---------------------------------------------------------------------------

fn due_from(index: usize) -> String {
    let idx = index.min(LADDER.len() - 1);
    (today() + Duration::days(LADDER[idx]))
        .format("%Y-%m-%d")
        .to_string()
}

/// SM-2 next-interval computation. `quality` is 0..=3 mapping to
/// Again / Hard / Good / Easy. Returns `(interval_days, new_ease, is_lapse)`.
/// Mirrored in the frontend `revision.ts::sm2`.
pub fn sm2(prev_interval: i64, ease: f64, reps: i64, quality: i64) -> (i64, f64, bool) {
    // Ease adjustment on a 0..=3 scale (Again lowers a lot, Easy raises).
    let delta = match quality {
        0 => -0.30,
        1 => -0.15,
        2 => 0.0,
        3 => 0.15,
        _ => 0.0,
    };
    let new_ease = (ease + delta).max(1.3);
    if quality == 0 {
        // Lapse: relearn tomorrow, keep a softened ease.
        return (1, new_ease, true);
    }
    let interval = if reps <= 0 {
        1
    } else if reps == 1 {
        if quality >= 3 {
            6
        } else {
            3
        }
    } else {
        ((prev_interval.max(1) as f64) * new_ease).round() as i64
    };
    (interval.clamp(1, 365), new_ease, false)
}

/// When a problem is first solved, seed a review due tomorrow. If a review
/// already exists it is left untouched (progression happens via mark_reviewed).
pub fn schedule_after_solve(conn: &Connection, problem_id: i64) -> AppResult<()> {
    let exists: bool = conn
        .query_row(
            "SELECT 1 FROM reviews WHERE problem_id = ?1",
            params![problem_id],
            |_| Ok(true),
        )
        .optional()?
        .unwrap_or(false);
    if !exists {
        conn.execute(
            "INSERT INTO reviews(problem_id, due_date, interval_index, interval_days, reps)
             VALUES(?1, ?2, 0, 1, 0)",
            params![problem_id, due_from(0)],
        )?;
    }
    Ok(())
}

/// Grade a review with a 0..=3 quality (Again/Hard/Good/Easy) using SM-2.
/// `remembered` false is treated as quality 0 for backward compatibility.
pub fn mark_reviewed_quality(conn: &Connection, problem_id: i64, quality: i64) -> AppResult<()> {
    let (interval, ease, reps, lapses): (i64, f64, i64, i64) = conn
        .query_row(
            "SELECT interval_days, ease, reps, lapses FROM reviews WHERE problem_id = ?1",
            params![problem_id],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?)),
        )
        .optional()?
        .unwrap_or((1, 2.5, 0, 0));

    let (new_interval, new_ease, is_lapse) = sm2(interval, ease, reps, quality);
    let new_reps = if is_lapse { 0 } else { reps + 1 };
    let new_lapses = lapses + if is_lapse { 1 } else { 0 };
    let due = (today() + Duration::days(new_interval)).format("%Y-%m-%d").to_string();

    conn.execute(
        "INSERT INTO reviews(problem_id, due_date, interval_index, ease, reps, lapses,
            interval_days, last_quality, last_reviewed_at)
         VALUES(?1, ?2, 0, ?3, ?4, ?5, ?6, ?7, ?8)
         ON CONFLICT(problem_id) DO UPDATE SET
            due_date = excluded.due_date,
            ease = excluded.ease,
            reps = excluded.reps,
            lapses = excluded.lapses,
            interval_days = excluded.interval_days,
            last_quality = excluded.last_quality,
            last_reviewed_at = excluded.last_reviewed_at",
        params![problem_id, due, new_ease, new_reps, new_lapses, new_interval, quality, now_iso()],
    )?;

    let date = today().format("%Y-%m-%d").to_string();
    conn.execute(
        "INSERT INTO daily_sessions(date, reviews_done) VALUES(?1, 1)
         ON CONFLICT(date) DO UPDATE SET reviews_done = reviews_done + 1",
        params![date],
    )?;
    Ok(())
}

/// Backward-compatible binary grading (remembered → Good, forgot → Again).
pub fn mark_reviewed(conn: &Connection, problem_id: i64, remembered: bool) -> AppResult<()> {
    mark_reviewed_quality(conn, problem_id, if remembered { 2 } else { 0 })
}

/// Set an explicit due date (manual adjustment).
pub fn reschedule_review(conn: &Connection, problem_id: i64, due_date: &str) -> AppResult<()> {
    conn.execute(
        "INSERT INTO reviews(problem_id, due_date, interval_index) VALUES(?1, ?2, 0)
         ON CONFLICT(problem_id) DO UPDATE SET due_date = excluded.due_date",
        params![problem_id, due_date],
    )?;
    Ok(())
}

pub fn due_reviews(conn: &Connection, on_or_before: &str) -> AppResult<Vec<ReviewItem>> {
    // Order by due date, then shakiest first (lowest ease / most lapses) so the
    // hardest recalls surface at the top of the queue.
    let mut stmt = conn.prepare(
        "SELECT r.id, r.problem_id, r.due_date, r.interval_index, r.ease, r.reps, r.lapses,
                r.interval_days, r.last_quality, r.last_reviewed_at, r.created_at,
                p.title, p.difficulty, p.confidence
         FROM reviews r JOIN problems p ON p.id = r.problem_id
         WHERE r.due_date <= ?1
         ORDER BY r.due_date, r.lapses DESC, r.ease ASC",
    )?;
    let rows = stmt.query_map(params![on_or_before], |r| {
        Ok((
            Review {
                id: r.get(0)?,
                problem_id: r.get(1)?,
                due_date: r.get(2)?,
                interval_index: r.get(3)?,
                ease: r.get(4)?,
                reps: r.get(5)?,
                lapses: r.get(6)?,
                interval_days: r.get(7)?,
                last_quality: r.get(8)?,
                last_reviewed_at: r.get(9)?,
                created_at: r.get(10)?,
            },
            r.get::<_, String>(11)?,
            r.get::<_, String>(12)?,
            r.get::<_, i64>(13)?,
        ))
    })?;
    let mut out = Vec::new();
    for row in rows {
        let (review, title, difficulty, confidence) = row?;
        let pid = review.problem_id;
        out.push(ReviewItem {
            review,
            problem_id: pid,
            title,
            difficulty,
            confidence,
            topics: tags_for(conn, pid, "topic")?,
        });
    }
    Ok(out)
}

// ---------------------------------------------------------------------------
// Settings
// ---------------------------------------------------------------------------

pub fn get_setting(conn: &Connection, key: &str) -> AppResult<Option<String>> {
    let v = conn
        .query_row(
            "SELECT value FROM settings WHERE key = ?1",
            params![key],
            |r| r.get::<_, String>(0),
        )
        .optional()?;
    Ok(v)
}

pub fn set_setting(conn: &Connection, key: &str, value: &str) -> AppResult<()> {
    conn.execute(
        "INSERT INTO settings(key, value) VALUES(?1, ?2)
         ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        params![key, value],
    )?;
    Ok(())
}

pub fn all_settings(conn: &Connection) -> AppResult<HashMap<String, String>> {
    let mut stmt = conn.prepare("SELECT key, value FROM settings")?;
    let rows = stmt.query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)))?;
    let mut map = HashMap::new();
    for row in rows {
        let (k, v) = row?;
        map.insert(k, v);
    }
    Ok(map)
}

// ---------------------------------------------------------------------------
// Drafts (in-progress editor buffers) + per-problem UI state
// ---------------------------------------------------------------------------

/// The saved draft for a (problem, language), or `None` if none exists yet.
pub fn get_draft(conn: &Connection, problem_id: i64, language: &str) -> AppResult<Option<String>> {
    let v = conn
        .query_row(
            "SELECT code FROM drafts WHERE problem_id = ?1 AND language = ?2",
            params![problem_id, language],
            |r| r.get::<_, String>(0),
        )
        .optional()?;
    Ok(v)
}

pub fn save_draft(conn: &Connection, problem_id: i64, language: &str, code: &str) -> AppResult<()> {
    conn.execute(
        "INSERT INTO drafts(problem_id, language, code, updated_at) VALUES(?1, ?2, ?3, ?4)
         ON CONFLICT(problem_id, language) DO UPDATE SET code = excluded.code, updated_at = excluded.updated_at",
        params![problem_id, language, code, now_iso()],
    )?;
    Ok(())
}

/// Number of hints the user has revealed for a problem (persisted).
pub fn get_hints_revealed(conn: &Connection, problem_id: i64) -> AppResult<i64> {
    let v = conn
        .query_row(
            "SELECT hints_revealed FROM problem_ui WHERE problem_id = ?1",
            params![problem_id],
            |r| r.get::<_, i64>(0),
        )
        .optional()?
        .unwrap_or(0);
    Ok(v)
}

pub fn set_hints_revealed(conn: &Connection, problem_id: i64, count: i64) -> AppResult<()> {
    conn.execute(
        "INSERT INTO problem_ui(problem_id, hints_revealed, updated_at) VALUES(?1, ?2, ?3)
         ON CONFLICT(problem_id) DO UPDATE SET hints_revealed = excluded.hints_revealed, updated_at = excluded.updated_at",
        params![problem_id, count.max(0), now_iso()],
    )?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Mistakes (reflection)
// ---------------------------------------------------------------------------

pub fn add_mistake(conn: &Connection, m: &Mistake) -> AppResult<i64> {
    conn.execute(
        "INSERT INTO mistakes(problem_id, attempt_id, category, note) VALUES(?1,?2,?3,?4)",
        params![m.problem_id, m.attempt_id, m.category, m.note],
    )?;
    Ok(conn.last_insert_rowid())
}

pub fn list_mistakes(conn: &Connection, problem_id: i64) -> AppResult<Vec<Mistake>> {
    let mut stmt = conn.prepare(
        "SELECT id, problem_id, attempt_id, category, note, created_at
         FROM mistakes WHERE problem_id = ?1 ORDER BY id DESC",
    )?;
    let rows = stmt.query_map(params![problem_id], |r| {
        Ok(Mistake {
            id: r.get(0)?,
            problem_id: r.get(1)?,
            attempt_id: r.get(2)?,
            category: r.get(3)?,
            note: r.get(4)?,
            created_at: r.get(5)?,
        })
    })?;
    Ok(rows.filter_map(|r| r.ok()).collect())
}

pub fn delete_mistake(conn: &Connection, id: i64) -> AppResult<()> {
    conn.execute("DELETE FROM mistakes WHERE id = ?1", params![id])?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Learning paths (curriculum)
// ---------------------------------------------------------------------------

/// Insert or update a path by key, replacing its ordered items.
pub fn upsert_path(
    conn: &Connection,
    key: &str,
    title: &str,
    description: &str,
    ordering: i64,
    problem_slugs: &[String],
) -> AppResult<i64> {
    conn.execute(
        "INSERT INTO paths(key, title, description, ordering) VALUES(?1,?2,?3,?4)
         ON CONFLICT(key) DO UPDATE SET title=excluded.title, description=excluded.description, ordering=excluded.ordering",
        params![key, title, description, ordering],
    )?;
    let id: i64 = conn.query_row("SELECT id FROM paths WHERE key = ?1", params![key], |r| r.get(0))?;
    conn.execute("DELETE FROM path_items WHERE path_id = ?1", params![id])?;
    for (i, slug) in problem_slugs.iter().enumerate() {
        if let Some(pid) = conn
            .query_row("SELECT id FROM problems WHERE slug = ?1", params![slug], |r| {
                r.get::<_, i64>(0)
            })
            .optional()?
        {
            conn.execute(
                "INSERT OR IGNORE INTO path_items(path_id, problem_id, ordering) VALUES(?1,?2,?3)",
                params![id, pid, i as i64],
            )?;
        }
    }
    Ok(id)
}

pub fn list_paths(conn: &Connection) -> AppResult<Vec<Path>> {
    let ids: Vec<(i64, String, String, String, i64)> = {
        let mut stmt =
            conn.prepare("SELECT id, key, title, description, ordering FROM paths ORDER BY ordering, id")?;
        let rows = stmt.query_map([], |r| {
            Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?, r.get(4)?))
        })?;
        rows.filter_map(|r| r.ok()).collect()
    };
    let mut out = Vec::new();
    for (id, key, title, description, ordering) in ids {
        let mut stmt = conn.prepare(
            "SELECT pi.problem_id, p.title, p.difficulty, p.solved_status, pi.ordering
             FROM path_items pi JOIN problems p ON p.id = pi.problem_id
             WHERE pi.path_id = ?1 ORDER BY pi.ordering",
        )?;
        let items = stmt
            .query_map(params![id], |r| {
                Ok(PathItem {
                    problem_id: r.get(0)?,
                    title: r.get(1)?,
                    difficulty: r.get(2)?,
                    solved_status: r.get(3)?,
                    ordering: r.get(4)?,
                })
            })?
            .filter_map(|r| r.ok())
            .collect();
        out.push(Path { id, key, title, description, ordering, items });
    }
    Ok(out)
}

// ---------------------------------------------------------------------------
// Contests
// ---------------------------------------------------------------------------

pub fn create_contest(
    conn: &Connection,
    title: &str,
    problem_ids: &[i64],
    duration_seconds: i64,
) -> AppResult<i64> {
    let ids_json = serde_json::to_string(problem_ids)?;
    conn.execute(
        "INSERT INTO contests(title, problem_ids_json, duration_seconds, status) VALUES(?1,?2,?3,'running')",
        params![title, ids_json, duration_seconds],
    )?;
    let cid = conn.last_insert_rowid();
    for pid in problem_ids {
        conn.execute(
            "INSERT OR IGNORE INTO contest_results(contest_id, problem_id) VALUES(?1,?2)",
            params![cid, pid],
        )?;
    }
    Ok(cid)
}

pub fn record_contest_result(
    conn: &Connection,
    contest_id: i64,
    problem_id: i64,
    solved: bool,
) -> AppResult<()> {
    if solved {
        conn.execute(
            "UPDATE contest_results SET solved = 1, solved_at = COALESCE(solved_at, ?3)
             WHERE contest_id = ?1 AND problem_id = ?2",
            params![contest_id, problem_id, now_iso()],
        )?;
    } else {
        conn.execute(
            "UPDATE contest_results SET wrong_tries = wrong_tries + 1
             WHERE contest_id = ?1 AND problem_id = ?2 AND solved = 0",
            params![contest_id, problem_id],
        )?;
    }
    Ok(())
}

pub fn finish_contest(conn: &Connection, contest_id: i64) -> AppResult<()> {
    conn.execute(
        "UPDATE contests SET status='finished', ended_at=?2 WHERE id=?1",
        params![contest_id, now_iso()],
    )?;
    Ok(())
}

fn hydrate_contest(conn: &Connection, id: i64) -> AppResult<Contest> {
    let (title, ids_json, duration, status, started, ended): (
        String,
        String,
        i64,
        String,
        String,
        Option<String>,
    ) = conn.query_row(
        "SELECT title, problem_ids_json, duration_seconds, status, started_at, ended_at
         FROM contests WHERE id = ?1",
        params![id],
        |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?, r.get(4)?, r.get(5)?)),
    )?;
    let problem_ids: Vec<i64> = serde_json::from_str(&ids_json).unwrap_or_default();
    let mut stmt = conn.prepare(
        "SELECT cr.problem_id, p.title, p.difficulty, cr.solved, cr.solved_at, cr.wrong_tries
         FROM contest_results cr JOIN problems p ON p.id = cr.problem_id
         WHERE cr.contest_id = ?1",
    )?;
    let results = stmt
        .query_map(params![id], |r| {
            Ok(ContestResult {
                problem_id: r.get(0)?,
                title: r.get(1)?,
                difficulty: r.get(2)?,
                solved: r.get::<_, i64>(3)? != 0,
                solved_at: r.get(4)?,
                wrong_tries: r.get(5)?,
            })
        })?
        .filter_map(|r| r.ok())
        .collect();
    Ok(Contest {
        id,
        title,
        problem_ids,
        duration_seconds: duration,
        status,
        started_at: started,
        ended_at: ended,
        results,
    })
}

pub fn get_contest(conn: &Connection, id: i64) -> AppResult<Contest> {
    hydrate_contest(conn, id)
}

pub fn list_contests(conn: &Connection) -> AppResult<Vec<Contest>> {
    let ids: Vec<i64> = {
        let mut stmt = conn.prepare("SELECT id FROM contests ORDER BY id DESC")?;
        let rows = stmt.query_map([], |r| r.get::<_, i64>(0))?;
        rows.filter_map(|r| r.ok()).collect()
    };
    ids.into_iter().map(|id| hydrate_contest(conn, id)).collect()
}

// ---------------------------------------------------------------------------
// Flashcards (spaced repetition for concepts/notes)
// ---------------------------------------------------------------------------

pub fn add_flashcard(conn: &Connection, front: &str, back: &str, source: &str) -> AppResult<i64> {
    let due = today().format("%Y-%m-%d").to_string();
    conn.execute(
        "INSERT INTO flashcards(front, back, source, due_date, interval_days) VALUES(?1,?2,?3,?4,0)",
        params![front, back, source, due],
    )?;
    Ok(conn.last_insert_rowid())
}

pub fn list_flashcards(conn: &Connection) -> AppResult<Vec<Flashcard>> {
    let mut stmt = conn.prepare(
        "SELECT id, front, back, source, ease, reps, lapses, interval_days, due_date, created_at
         FROM flashcards ORDER BY id DESC",
    )?;
    let rows = stmt.query_map([], |r| {
        Ok(Flashcard {
            id: r.get(0)?,
            front: r.get(1)?,
            back: r.get(2)?,
            source: r.get(3)?,
            ease: r.get(4)?,
            reps: r.get(5)?,
            lapses: r.get(6)?,
            interval_days: r.get(7)?,
            due_date: r.get(8)?,
            created_at: r.get(9)?,
        })
    })?;
    Ok(rows.filter_map(|r| r.ok()).collect())
}

pub fn due_flashcards(conn: &Connection) -> AppResult<Vec<Flashcard>> {
    let today = today().format("%Y-%m-%d").to_string();
    Ok(list_flashcards(conn)?
        .into_iter()
        .filter(|c| c.due_date <= today)
        .collect())
}

pub fn grade_flashcard(conn: &Connection, id: i64, quality: i64) -> AppResult<()> {
    let (interval, ease, reps, lapses): (i64, f64, i64, i64) = conn
        .query_row(
            "SELECT interval_days, ease, reps, lapses FROM flashcards WHERE id = ?1",
            params![id],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?)),
        )
        .optional()?
        .unwrap_or((0, 2.5, 0, 0));
    let (new_interval, new_ease, is_lapse) = sm2(interval, ease, reps, quality);
    let new_reps = if is_lapse { 0 } else { reps + 1 };
    let new_lapses = lapses + if is_lapse { 1 } else { 0 };
    let due = (today() + Duration::days(new_interval)).format("%Y-%m-%d").to_string();
    conn.execute(
        "UPDATE flashcards SET ease=?2, reps=?3, lapses=?4, interval_days=?5, due_date=?6 WHERE id=?1",
        params![id, new_ease, new_reps, new_lapses, new_interval, due],
    )?;
    Ok(())
}

pub fn delete_flashcard(conn: &Connection, id: i64) -> AppResult<()> {
    conn.execute("DELETE FROM flashcards WHERE id = ?1", params![id])?;
    Ok(())
}
