//! Trust harness for the Learn-tab concept exercises. Every "half-coded" drill
//! ships a full reference program (`solution`) and its expected outputs
//! (`tests`). This proves, through the REAL judge, that the reference program
//! actually produces those outputs — the same guarantee verify_seeds.rs gives
//! the problem bank — and that each starter really is blanked out.

use std::collections::HashSet;
use std::time::Duration;

use poodcode_lib::judge::{judge_with, JudgeConfig};
use poodcode_lib::models::{Concept, TestCase};

const CONCEPTS: &str = include_str!("../seeds/concepts.json");
const T: Duration = Duration::from_secs(10);

fn load_concepts() -> Vec<Concept> {
    serde_json::from_str(CONCEPTS).expect("concepts.json parses")
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
    let cfg = JudgeConfig {
        mode: "exact".into(),
        tolerance: 0.0,
        function_spec: None,
        checker: None,
        timeout: T,
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
                    input: t.input.clone(),
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
