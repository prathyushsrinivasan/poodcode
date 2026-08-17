// `Stats` is built field-by-field after `default()` for readability.
#![allow(clippy::field_reassign_with_default)]

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
const SEED_VERSION: i64 = 10;

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
        // ---- Syllabus expansion tracks (SEED_VERSION 10) ----
        (
            "trees",
            "Binary Trees",
            "Traversals, depth, and the recursion that powers every tree problem.",
            &[
                "max-depth-tree", "min-depth-tree", "invert-binary-tree", "same-tree",
                "level-order-traversal", "right-side-view", "path-sum-exists",
                "balanced-tree", "diameter-of-tree", "lca-binary-tree", "max-path-sum",
            ],
        ),
        (
            "bst",
            "Binary Search Trees",
            "Exploit the left < node < right invariant for search, order, and validation.",
            &["bst-search", "bst-insert", "kth-smallest-bst", "lca-bst", "validate-bst"],
        ),
        (
            "linked-lists",
            "Linked Lists",
            "Pointer surgery: reversal, fast/slow pointers, and cycle detection.",
            &[
                "list-length", "reverse-linked-list", "middle-of-list",
                "remove-duplicates-sorted-list", "merge-two-sorted-lists",
                "remove-nth-from-end", "palindrome-linked-list", "has-cycle",
                "reorder-list", "reverse-k-group",
            ],
        ),
        (
            "backtracking",
            "Backtracking",
            "Choose / explore / un-choose over subsets, permutations, and constraint puzzles.",
            &[
                "subset-sum-count", "combination-sum-count", "generate-subsets",
                "generate-permutations", "generate-parentheses", "word-search",
                "palindrome-partition-count", "n-queens-count",
            ],
        ),
        (
            "heaps",
            "Heaps & Priority Queues",
            "Top-K, two-heap medians, and greedy-with-a-heap scheduling.",
            &[
                "last-stone-weight", "kth-largest-in-array", "k-closest-distances",
                "top-k-frequent-words", "task-scheduler", "reorganize-string",
                "merge-k-sorted", "median-from-stream",
            ],
        ),
        (
            "intervals",
            "Intervals",
            "Sort by start or end, merge, and sweep for concurrency.",
            &[
                "can-attend-meetings", "merge-intervals", "insert-interval",
                "min-meeting-rooms", "non-overlapping-remove", "min-arrows-balloons",
                "interval-intersections", "employee-free-time",
            ],
        ),
        (
            "design-ds",
            "Design & Data Structures",
            "Compose primitives into caches, stacks-from-queues, and streaming structures.",
            &[
                "min-stack", "implement-queue-stacks", "design-hashmap",
                "design-circular-queue", "lru-cache", "time-based-kv",
                "stock-spanner", "lfu-cache",
            ],
        ),
        (
            "union-find",
            "Union-Find (DSU)",
            "Connectivity, components, cycle detection, and Kruskal's MST.",
            &[
                "count-components", "number-of-provinces", "graph-valid-tree",
                "redundant-connection", "largest-component-size",
                "make-network-connected", "earliest-full-connect",
            ],
        ),
        (
            "advanced-graphs",
            "Advanced Graphs",
            "Dijkstra, Bellman-Ford, MST, topological order, and cycle detection.",
            &[
                "network-delay-time", "cheapest-flights-k-stops", "mst-total-weight",
                "min-cost-connect-points", "detect-cycle-directed", "course-schedule-possible",
                "bipartite-check", "word-ladder-length", "alien-dictionary-order",
            ],
        ),
        (
            "tries",
            "Tries (Prefix Trees)",
            "Prefix-indexed lookups: dictionaries, autocomplete, wildcards, and bit-tries.",
            &[
                "longest-common-prefix-strs", "word-in-dictionary", "prefix-counts",
                "replace-words-roots", "implement-trie-ops", "word-dictionary-wildcard",
                "max-xor-pair",
            ],
        ),
    ];
    for (i, (key, title, desc, slugs)) in paths.iter().enumerate() {
        let owned: Vec<String> = slugs.iter().map(|s| s.to_string()).collect();
        if let Err(e) = repo::upsert_path(conn, key, title, desc, i as i64, &owned) {
            eprintln!("[paths] failed to seed {key}: {e}");
        }
    }
}

/// Concept flashcards (signal → technique), authored in the generator and
/// seeded idempotently so review progress survives relaunches.
const SEED_FLASHCARDS: &str = include_str!("../seeds/flashcards.json");

#[derive(serde::Deserialize)]
struct SeedCard {
    front: String,
    back: String,
    source: String,
}

fn seed_flashcards(conn: &Connection) {
    match serde_json::from_str::<Vec<SeedCard>>(SEED_FLASHCARDS) {
        Ok(cards) => {
            for c in &cards {
                if let Err(e) = repo::seed_flashcard_if_absent(conn, &c.front, &c.back, &c.source) {
                    eprintln!("[flashcards] failed to seed: {e}");
                }
            }
        }
        Err(e) => eprintln!("[flashcards] could not parse seed flashcards: {e}"),
    }
}

/// One timed practice contest per syllabus domain, created once (idempotent by
/// title) so users have a ready-made mock-interview set to launch.
fn seed_contests(conn: &Connection) {
    let contests: &[(&str, i64, &[&str])] = &[
        ("Tree Traversal Gauntlet", 3600, &["max-depth-tree", "level-order-traversal", "validate-bst", "diameter-of-tree", "lca-binary-tree"]),
        ("Linked List Sprint", 3600, &["reverse-linked-list", "middle-of-list", "merge-two-sorted-lists", "has-cycle", "reorder-list"]),
        ("Backtracking Dash", 3600, &["generate-subsets", "generate-permutations", "combination-sum-count", "word-search", "n-queens-count"]),
        ("Heap Time Trial", 3600, &["kth-largest-in-array", "top-k-frequent-words", "task-scheduler", "merge-k-sorted", "median-from-stream"]),
        ("Interval Sprint", 3600, &["merge-intervals", "insert-interval", "min-meeting-rooms", "non-overlapping-remove", "interval-intersections"]),
        ("Design Bracket", 3600, &["min-stack", "implement-queue-stacks", "lru-cache", "time-based-kv", "stock-spanner"]),
        ("Union-Find Round", 3600, &["count-components", "graph-valid-tree", "redundant-connection", "make-network-connected", "largest-component-size"]),
        ("Graph Showdown", 3600, &["network-delay-time", "cheapest-flights-k-stops", "mst-total-weight", "course-schedule-possible", "word-ladder-length"]),
        ("Trie Power Hour", 3600, &["word-in-dictionary", "prefix-counts", "replace-words-roots", "implement-trie-ops", "word-dictionary-wildcard"]),
    ];
    for (title, dur, slugs) in contests {
        if let Err(e) = repo::create_contest_if_absent(conn, title, slugs, *dur) {
            eprintln!("[contests] failed to seed {title}: {e}");
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
            seed_flashcards(&conn);
            seed_contests(&conn);
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
            commands::card_reviews,
            commands::grade_card,
            commands::reset_cards,
            commands::jp_bridge,
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
