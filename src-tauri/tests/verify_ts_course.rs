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
use poodcode_lib::models::{Exercise, TestCase, WeeklyCourse};

const COURSE: &str = include_str!("../seeds/ts_course.json");
const T: Duration = Duration::from_secs(10);

fn load_course() -> WeeklyCourse {
    serde_json::from_str(COURSE).expect("ts_course.json parses")
}

/// Every judged exercise in the course (lesson exercises + capstone + stretch).
fn all_exercises(course: &WeeklyCourse) -> Vec<(String, &Exercise)> {
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
            if let Some(ex) = &cap.stretch {
                out.push((format!("W{}/stretch", w.number), ex));
            }
        }
    }
    out
}

/// Validate a quiz's answer indices are all in range.
fn check_quiz(quiz: &[poodcode_lib::models::QuizQuestion], where_: &str) {
    for q in quiz {
        assert!(
            q.answer >= 0 && (q.answer as usize) < q.options.len(),
            "quiz in {where_} has out-of-range answer {}",
            q.answer
        );
    }
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
        // "fix" exercises hand the learner a complete buggy program (no blank);
        // every other kind must have a ____ blank to fill.
        if ex.kind == "fix" {
            assert!(!ex.starter.contains("____"), "{}: fix starter should have no blank", ex.id);
        } else {
            assert!(ex.starter.contains("____"), "{}: starter has no ____ blank", ex.id);
        }
        assert_ne!(ex.starter, ex.solution, "{}: starter equals solution", ex.id);
        // A type-level exercise is graded by the compiler: its harness carries
        // the assertions, and there is nothing to run or compare. Every other
        // exercise still has to ship cases.
        if ex.judge_mode == "types" {
            assert!(
                ex.tests.is_empty(),
                "{}: a type-level exercise is never run, so its tests can never fire",
                ex.id
            );
            assert!(
                ex.harness.contains("Expect<"),
                "{}: a type-level exercise needs Expect<> assertions in its harness",
                ex.id
            );
        } else {
            assert!(
                ex.judge_mode.is_empty() || ex.judge_mode == "stdout",
                "{}: unknown judge_mode {:?}",
                ex.id,
                ex.judge_mode
            );
            assert!(!ex.tests.is_empty(), "{}: no tests", ex.id);
        }
        total += 1;
    }
    assert!(total > 0, "no course exercises shipped");

    // Every quiz answer index is in range — lesson warm-ups, lesson quizzes,
    // and the end-of-week review.
    for w in &course.weeks {
        check_quiz(&w.review, &format!("W{}/review", w.number));
        for l in &w.lessons {
            check_quiz(&l.warmup, &format!("W{}/{}/warmup", w.number, l.key));
            check_quiz(&l.quiz, &format!("W{}/{}/quiz", w.number, l.key));
        }
    }
    eprintln!("verified {total} well-formed course exercises across 32 weeks");
}

#[test]
fn every_course_solution_passes_its_tests() {
    let course = load_course();

    let mut checked = 0;
    let mut typed = 0;
    let mut skipped = 0;
    for (where_, ex) in all_exercises(&course) {
        let lang = if ex.language.is_empty() { "typescript" } else { &ex.language };
        // Judge each exercise exactly as the app does: its own hidden harness,
        // its own grading mode. Anything else and this harness stops proving
        // that what ships actually works.
        let cfg = JudgeConfig {
            harness: ex.harness.clone(),
            typecheck_only: ex.judge_mode == "types",
            ..JudgeConfig::exact(T)
        };
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
        if ex.judge_mode == "types" {
            typed += 1;
        }
    }
    eprintln!(
        "verified {checked} course solutions ({typed} graded by type-check alone, \
         {skipped} skipped: Node missing)"
    );
}
