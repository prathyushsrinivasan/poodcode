//! Trust harness for the 8-month TypeScript course. Every judged exercise
//! (lesson drills/challenges + auto-graded capstones) ships a full reference
//! `solution` and its expected `tests`. This proves, through the REAL judge
//! (the same one the app uses), that each reference program actually produces
//! those outputs — and that each starter is genuinely blanked. Mirrors
//! verify_exercises.rs. TypeScript runs via Node type-stripping; if Node is
//! missing the run-through is skipped rather than failing the suite.

use std::collections::HashSet;
use std::time::Duration;

use poodcode_lib::judge::{judge_with, JudgeConfig};
use poodcode_lib::models::{Exercise, TestCase, TsCourse};

const COURSE: &str = include_str!("../seeds/ts_course.json");
const T: Duration = Duration::from_secs(10);

fn load_course() -> TsCourse {
    serde_json::from_str(COURSE).expect("ts_course.json parses")
}

/// Every judged exercise in the course (lesson exercises + auto capstone).
fn all_exercises(course: &TsCourse) -> Vec<(String, &Exercise)> {
    let mut out = Vec::new();
    for w in &course.weeks {
        for l in &w.lessons {
            for ex in &l.exercises {
                out.push((format!("W{}/{}", w.number, l.key), ex));
            }
        }
        if let Some(cap) = &w.capstone {
            if let Some(ex) = &cap.exercise {
                out.push((format!("W{}/capstone", w.number), ex));
            }
        }
    }
    out
}

#[test]
fn course_structure_is_well_formed() {
    let course = load_course();
    assert_eq!(course.weeks.len(), 32, "expected a 32-week (8-month) course");

    // Weeks are numbered 1..=32 exactly once, each tagged to a month.
    let mut seen: HashSet<i64> = HashSet::new();
    for w in &course.weeks {
        assert!((1..=32).contains(&w.number), "week number out of range: {}", w.number);
        assert!(seen.insert(w.number), "duplicate week number: {}", w.number);
        assert!((1..=8).contains(&w.month), "week {} has bad month {}", w.number, w.month);
        assert!(!w.theme.trim().is_empty(), "week {} has no theme", w.number);
        assert!(!w.goal.trim().is_empty(), "week {} has no goal", w.number);
        if w.authored {
            assert!(!w.lessons.is_empty(), "authored week {} has no lessons", w.number);
        }
    }

    let mut ids = HashSet::new();
    let mut total = 0;
    for (where_, ex) in all_exercises(&course) {
        assert!(!ex.id.is_empty(), "{where_}: exercise with empty id");
        assert!(ids.insert(ex.id.clone()), "duplicate exercise id: {}", ex.id);
        assert!(!ex.title.trim().is_empty(), "{}: empty title", ex.id);
        assert!(!ex.prompt.trim().is_empty(), "{}: empty prompt", ex.id);
        assert!(!ex.solution.trim().is_empty(), "{}: empty solution", ex.id);
        assert!(ex.starter.contains("____"), "{}: starter has no ____ blank", ex.id);
        assert_ne!(ex.starter, ex.solution, "{}: starter equals solution", ex.id);
        assert!(!ex.tests.is_empty(), "{}: no tests", ex.id);
        total += 1;
    }
    assert!(total > 0, "no course exercises shipped");

    // Every quiz answer index is in range.
    for w in &course.weeks {
        for l in &w.lessons {
            for q in &l.quiz {
                assert!(
                    q.answer >= 0 && (q.answer as usize) < q.options.len(),
                    "quiz in {} has out-of-range answer {}",
                    l.key,
                    q.answer
                );
            }
        }
    }
    eprintln!("verified {total} well-formed course exercises across 32 weeks");
}

#[test]
fn every_course_solution_passes_its_tests() {
    let course = load_course();
    let cfg = JudgeConfig {
        mode: "exact".into(),
        tolerance: 0.0,
        function_spec: None,
        checker: None,
        timeout: T,
    };

    let mut checked = 0;
    let mut skipped = 0;
    for (where_, ex) in all_exercises(&course) {
        let lang = if ex.language.is_empty() { "typescript" } else { &ex.language };
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
            "course exercise {} ({}) was NOT accepted: {:?}",
            ex.id, where_, report
        );
        checked += 1;
    }
    eprintln!("verified {checked} course solutions ({skipped} skipped: Node missing)");
}
