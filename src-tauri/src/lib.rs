mod commands;
mod db;
mod error;
pub mod exec;
pub mod harness;
pub mod judge;
pub mod models;
mod repo;
mod stats;

#[cfg(test)]
mod tests;

use std::sync::Mutex;

use rusqlite::Connection;
use tauri::Manager;

use commands::AppState;
use models::Problem;

/// Bump when the bundled seed problems change so existing installs pick up new
/// content on next launch (existing user progress is preserved via upsert).
const SEED_VERSION: i64 = 7;

/// Original starter problems, authored for this app (no third-party content).
const SEED_PROBLEMS: &str = include_str!("../seeds/problems.json");

fn seed_if_needed(conn: &Connection) {
    if db::seed_version(conn) >= SEED_VERSION {
        return;
    }
    match serde_json::from_str::<Vec<Problem>>(SEED_PROBLEMS) {
        Ok(problems) => {
            for p in &problems {
                if let Err(e) = repo::upsert_problem(conn, p) {
                    eprintln!("[seed] failed to import {}: {e}", p.slug);
                }
            }
            let _ = db::set_seed_version(conn, SEED_VERSION);
            eprintln!("[seed] imported {} starter problems", problems.len());
        }
        Err(e) => eprintln!("[seed] could not parse seed problems: {e}"),
    }
}

/// Curated learning paths (curriculum tracks). Re-applied on every launch so new
/// installs and updated definitions both take effect; `upsert_path` is idempotent.
fn seed_paths(conn: &Connection) {
    let paths: &[(&str, &str, &str, &[&str])] = &[
        (
            "foundations",
            "Programming Foundations",
            "Get comfortable reading input, doing arithmetic, branching, and looping.",
            &[
                "print-greeting", "echo-line", "add-two-numbers", "rectangle-area",
                "even-or-odd", "is-even", "larger-of-two", "max-of-three",
                "sum-to-n", "countdown", "absolute-value", "square-number",
                "sum-of-digits", "factorial",
            ],
        ),
        (
            "arrays-hashing",
            "Arrays & Hashing",
            "The bread and butter: scanning arrays and using hash maps for O(1) lookups.",
            &[
                "array-sum", "array-minimum", "count-evens", "running-sum",
                "contains-duplicate", "two-sum-exists", "two-sum-indices",
                "move-zeroes", "second-largest", "product-except-self",
                "rotate-array", "rotate-array-right", "group-anagrams-count",
            ],
        ),
        (
            "hashing-patterns",
            "Hashing Patterns",
            "Turn 'search' into O(1) lookups: complements, counts, sets, and prefix sums.",
            &[
                "valid-anagram", "first-unique-char", "majority-element",
                "single-number", "subarray-sum-k", "longest-consecutive",
            ],
        ),
        (
            "bit-manipulation",
            "Bit Manipulation",
            "Think in bits: XOR tricks and popcount.",
            &["number-of-1-bits", "single-number"],
        ),
        (
            "greedy",
            "Greedy",
            "Make the locally-best choice and prove it stays globally optimal.",
            &["best-time-buy-sell", "jump-game", "container-most-water"],
        ),
        (
            "stack-monotonic",
            "Stacks & Monotonic Stacks",
            "Matching brackets and 'next greater' style problems.",
            &["valid-parentheses", "daily-temperatures", "next-greater-element"],
        ),
        (
            "two-pointers-sliding",
            "Two Pointers & Sliding Window",
            "Shrinking/expanding windows and converging pointers.",
            &["reverse-string", "longest-unique-substring", "trapping-rain-water"],
        ),
        (
            "binary-search",
            "Binary Search",
            "Halving the search space — on arrays and on answers.",
            &["binary-search-first", "search-insert-position", "integer-sqrt", "longest-increasing-subsequence"],
        ),
        (
            "dp-ladder",
            "Dynamic Programming Ladder",
            "Build DP intuition from 1-D recurrences up to 2-D tables.",
            &[
                "nth-fibonacci", "climbing-stairs", "min-cost-climbing-stairs",
                "house-robber", "maximum-subarray", "max-subarray-fn",
                "coin-change", "coin-change-ways", "edit-distance",
                "longest-increasing-subsequence",
            ],
        ),
        (
            "dp-advanced",
            "Dynamic Programming II (Hard)",
            "Tougher recurrences: strings, subsets, and products.",
            &[
                "word-break", "decode-ways", "maximum-product-subarray",
                "partition-equal-subset-sum", "longest-palindrome-length", "edit-distance",
            ],
        ),
        (
            "math",
            "Math & Number Theory",
            "Primes, digits, and integer arithmetic.",
            &["gcd", "palindrome-number", "is-prime", "count-primes", "integer-sqrt"],
        ),
        (
            "graphs",
            "Graph Fundamentals",
            "Traversal, ordering, and shortest paths.",
            &["number-of-islands", "course-schedule", "dijkstra-shortest-path"],
        ),
        (
            "stacks-strings",
            "Stacks & Strings",
            "Matching, counting, and canonical forms.",
            &["valid-parentheses", "count-vowels", "group-anagrams-count"],
        ),
    ];
    for (i, (key, title, desc, slugs)) in paths.iter().enumerate() {
        let owned: Vec<String> = slugs.iter().map(|s| s.to_string()).collect();
        if let Err(e) = repo::upsert_path(conn, key, title, desc, i as i64, &owned) {
            eprintln!("[paths] failed to seed {key}: {e}");
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let dir = app
                .path()
                .app_data_dir()
                .expect("failed to resolve app data dir");
            std::fs::create_dir_all(&dir).ok();
            let db_path = dir.join("poodcode.sqlite");
            let conn = db::open(&db_path).expect("failed to open database");
            seed_if_needed(&conn);
            seed_paths(&conn);
            app.manage(AppState {
                db: Mutex::new(conn),
                db_path,
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::list_problems,
            commands::get_problem,
            commands::save_problem,
            commands::delete_problem,
            commands::set_favorite,
            commands::set_confidence,
            commands::distinct_tags,
            commands::import_problems,
            commands::export_problems,
            commands::read_file,
            commands::write_file,
            commands::list_test_cases,
            commands::save_test_case,
            commands::delete_test_case,
            commands::get_note,
            commands::save_note,
            commands::known_prereqs,
            commands::set_prereq_status,
            commands::list_solutions,
            commands::save_solution,
            commands::delete_solution,
            commands::list_attempts,
            commands::languages,
            commands::concepts,
            commands::run_tests,
            commands::run_scratch,
            commands::submit,
            commands::due_reviews,
            commands::mark_reviewed,
            commands::grade_review,
            commands::reschedule_review,
            commands::add_mistake,
            commands::list_mistakes,
            commands::delete_mistake,
            commands::list_paths,
            commands::create_contest,
            commands::contest,
            commands::list_contests,
            commands::finish_contest,
            commands::record_contest_result,
            commands::list_flashcards,
            commands::due_flashcards,
            commands::add_flashcard,
            commands::grade_flashcard,
            commands::delete_flashcard,
            commands::statistics,
            commands::dashboard,
            commands::get_settings,
            commands::set_setting,
            commands::get_draft,
            commands::save_draft,
            commands::get_hints_revealed,
            commands::set_hints_revealed,
            commands::backup_database,
            commands::restore_database,
            commands::learning_recommendations,
            commands::random_problem,
            commands::log_study_time,
            commands::timeline,
        ])
        .run(tauri::generate_context!())
        .expect("error while running Poodcode");
}
