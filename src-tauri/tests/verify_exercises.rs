//! Trust harness for the Learn-tab concept exercises. Every "half-coded" drill
//! ships a full reference program (`solution`) and its expected outputs
//! (`tests`). This proves, through the REAL judge, that the reference program
//! actually produces those outputs — the same guarantee verify_seeds.rs gives
//! the problem bank — and that each starter really is blanked out.

use std::collections::{HashMap, HashSet};
use std::time::Duration;

use poodcode_lib::judge::{judge_with, JudgeConfig};
use poodcode_lib::models::{Concept, SqlDataset, TestCase};

const CONCEPTS: &str = include_str!("../seeds/concepts.json");
const SQL_DATASETS: &str = include_str!("../seeds/sql_datasets.json");
const T: Duration = Duration::from_secs(10);

fn load_concepts() -> Vec<Concept> {
    serde_json::from_str(CONCEPTS).expect("concepts.json parses")
}

/// SQL-track datasets keyed by their `key`, so a SQL exercise's shared schema can
/// be prepended to each case's input — exactly as the app does at runtime (see
/// the frontend `setupFor` and `Exercise.dataset`). Without this, SQL exercises
/// run against an empty database and fail with "no such table".
fn load_datasets() -> HashMap<String, String> {
    let sets: Vec<SqlDataset> = serde_json::from_str(SQL_DATASETS).expect("sql_datasets.json parses");
    sets.into_iter().map(|d| (d.key, d.sql)).collect()
}

/// The stdin a case runs against: for SQL exercises, the dataset SQL followed by
/// this case's variation on it; for every other language, the input unchanged.
fn case_input(ex_language: &str, ex_dataset: &str, datasets: &HashMap<String, String>, raw: &str) -> String {
    if ex_language != "sql" {
        return raw.to_string();
    }
    let base = datasets.get(ex_dataset).cloned().unwrap_or_default();
    if raw.trim().is_empty() {
        base
    } else {
        format!("{base}\n{raw}\n")
    }
}

#[test]
fn every_concept_exercise_is_well_formed() {
    let concepts = load_concepts();
    let mut ids = HashSet::new();
    let mut total = 0;

    for c in &concepts {
        for ex in &c.exercises {
            let id = &ex.id;
            assert!(!id.is_empty(), "{}: exercise with empty id", c.key);
            assert!(ids.insert(id.clone()), "duplicate exercise id: {id}");
            assert!(!ex.title.trim().is_empty(), "{id}: empty title");
            assert!(!ex.prompt.trim().is_empty(), "{id}: empty prompt");
            assert!(!ex.solution.trim().is_empty(), "{id}: empty solution");
            assert!(
                ex.starter.contains("____"),
                "{id}: starter has no ____ blank for the learner to fill"
            );
            assert_ne!(ex.starter, ex.solution, "{id}: starter equals solution");
            assert!(!ex.tests.is_empty(), "{id}: no tests");
            total += 1;
        }
    }
    assert!(total > 0, "no concept exercises shipped");
    eprintln!("verified {total} well-formed exercises across {} concepts", concepts.len());
}

#[test]
fn every_exercise_solution_passes_its_tests() {
    let concepts = load_concepts();
    let datasets = load_datasets();
    let cfg = JudgeConfig {
        mode: "exact".into(),
        tolerance: 0.0,
        function_spec: None,
        checker: None,
        ..JudgeConfig::exact(T)
    };

    let mut checked = 0;
    let mut skipped = 0;
    for c in &concepts {
        for ex in &c.exercises {
            let lang = if ex.language.is_empty() { "java" } else { &ex.language };
            let cases: Vec<TestCase> = ex
                .tests
                .iter()
                .enumerate()
                .map(|(i, t)| TestCase {
                    id: 0,
                    problem_id: 0,
                    kind: "hidden".into(),
                    name: format!("case {}", i + 1),
                    input: case_input(lang, &ex.dataset, &datasets, &t.input),
                    expected_output: t.output.clone(),
                    ordering: i as i64,
                })
                .collect();

            let report = judge_with(lang, &ex.solution, &cases, &cfg);
            if report.status == "not_installed" {
                skipped += 1;
                continue;
            }
            assert_eq!(
                report.status, "accepted",
                "exercise {} solution was NOT accepted: {:?}",
                ex.id, report
            );
            checked += 1;
        }
    }
    eprintln!("verified {checked} exercise solutions ({skipped} skipped: toolchain missing)");
    assert!(checked > 0, "no exercise solutions could run — is Java installed?");
}
