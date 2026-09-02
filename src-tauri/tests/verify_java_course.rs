//! Trust harness for the Java course. Every judged exercise (lesson drills,
//! fix-the-bug programs, challenges and each module's capstone) ships a full
//! reference `solution` and its expected `tests`. This proves, through the REAL
//! judge (the same one the app uses), that each reference program actually
//! produces those outputs — and that each starter is genuinely blanked. Mirrors
//! verify_backend_course.rs.
//!
//! The programs are plain Java compiled with `javac` and run as `java Main`,
//! reading stdin with a `Scanner`. If a JDK is missing, the run-through is
//! skipped rather than failing the suite — but `course_structure_is_well_formed`
//! still runs, since it needs no toolchain.
//!
//! The fast authoring loop is tools/verify_java_course.py, which does the same
//! thing without a cargo build. Both must pass.

use std::collections::HashSet;
use std::time::Duration;

use poodcode_lib::judge::{judge_with, JudgeConfig};
use poodcode_lib::models::{Exercise, TestCase, WeeklyCourse};

const COURSE: &str = include_str!("../seeds/java_course.json");
// javac + a JVM start per case is slower than Node, and the naive-Fibonacci
// exercises in module 10 are deliberately expensive — so this is roomier than
// the app's 6s.
const T: Duration = Duration::from_secs(20);

fn load_course() -> WeeklyCourse {
    serde_json::from_str(COURSE).expect("java_course.json parses")
}

/// Every judged exercise in the course (lesson exercises + capstones).
fn all_exercises(course: &WeeklyCourse) -> Vec<(String, &Exercise)> {
    let mut out = Vec::new();
    for m in &course.weeks {
        for l in &m.lessons {
            for ex in &l.exercises {
                out.push((format!("M{}/{}", m.number, l.key), ex));
            }
        }
        if let Some(cap) = &m.capstone {
            for ex in [cap.exercise.as_ref(), cap.stretch.as_ref()].into_iter().flatten() {
                out.push((format!("M{}/capstone", m.number), ex));
            }
        }
    }
    out
}

fn check_quiz(quiz: &[poodcode_lib::models::QuizQuestion], where_: &str) {
    for q in quiz {
        assert!(
            q.answer >= 0 && (q.answer as usize) < q.options.len(),
            "quiz in {where_} has out-of-range answer {}",
            q.answer
        );
        assert!(
            q.options.len() >= 2,
            "quiz in {where_} has fewer than two options"
        );
    }
}

#[test]
fn course_structure_is_well_formed() {
    let course = load_course();
    assert!(!course.weeks.is_empty(), "no Java modules shipped");
    // This course relabels the shared Week/Month model as Module/Part; if the
    // labels went missing the UI would silently call a module a "Week".
    assert_eq!(course.unit_label, "Module", "unit_label lost");
    assert_eq!(course.group_label, "Part", "group_label lost");

    // Modules are numbered 1..=N with no gaps, and every one is authored —
    // this course ships no "coming soon" placeholders.
    for (i, m) in course.weeks.iter().enumerate() {
        assert_eq!(m.number, (i + 1) as i64, "module {} is out of order", m.number);
        assert!(m.authored, "module {} is not authored", m.number);
        assert!(!m.theme.trim().is_empty(), "module {} has no theme", m.number);
        assert!(!m.goal.trim().is_empty(), "module {} has no goal", m.number);
        assert!(!m.lessons.is_empty(), "module {} has no lessons", m.number);
        assert!(
            m.est_minutes > 0,
            "module {} has no study-time estimate",
            m.number
        );
        // Every module carries the polish the UI renders sections for.
        assert!(!m.objectives.is_empty(), "module {} has no objectives", m.number);
        assert!(!m.glossary.is_empty(), "module {} has no glossary", m.number);
        assert!(!m.cheatsheet.trim().is_empty(), "module {} has no cheat sheet", m.number);
        assert!(!m.self_check.is_empty(), "module {} has no self-check", m.number);
        assert!(!m.review.is_empty(), "module {} has no end-of-module review", m.number);
        assert!(
            m.capstone.is_some(),
            "module {} has no capstone project",
            m.number
        );

        let mut lesson_keys: HashSet<&str> = HashSet::new();
        for l in &m.lessons {
            assert!(
                lesson_keys.insert(&l.key),
                "module {}: duplicate lesson key {}",
                m.number,
                l.key
            );
            assert!(!l.title.trim().is_empty(), "{}: lesson with no title", l.key);
            assert!(!l.lesson.trim().is_empty(), "{}: lesson with no prose", l.key);
            assert!(!l.exercises.is_empty(), "{}: lesson with no exercises", l.key);
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
        assert_eq!(ex.language, "java", "{}: not a Java exercise", ex.id);
        // "fix" exercises hand over a complete buggy program (no blank); every
        // other kind must have a ____ blank to fill.
        if ex.kind == "fix" {
            assert!(!ex.starter.contains("____"), "{}: fix starter should have no blank", ex.id);
        } else {
            assert!(ex.starter.contains("____"), "{}: starter has no ____ blank", ex.id);
        }
        assert_ne!(ex.starter, ex.solution, "{}: starter equals solution", ex.id);
        assert!(!ex.tests.is_empty(), "{}: no tests", ex.id);
        // The judge feeds `input` to stdin verbatim. A zero-byte stdin makes
        // `Scanner.nextLine()` throw before the program can print anything, so
        // "the empty input" has to be written as a blank line.
        for t in &ex.tests {
            assert!(
                !t.input.is_empty(),
                "{}: a test case has empty stdin — use \"\\n\" for a blank line",
                ex.id
            );
        }
        total += 1;
    }
    assert!(total > 0, "no Java course exercises shipped");

    for m in &course.weeks {
        check_quiz(&m.review, &format!("M{}/review", m.number));
        for l in &m.lessons {
            check_quiz(&l.warmup, &format!("M{}/{}/warmup", m.number, l.key));
            check_quiz(&l.quiz, &format!("M{}/{}/quiz", m.number, l.key));
        }
    }
    eprintln!(
        "verified {total} well-formed Java exercises across {} modules",
        course.weeks.len()
    );
}

#[test]
fn every_java_solution_passes_its_tests() {
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
            "Java exercise {} ({}) was NOT accepted: {:?}",
            ex.id, where_, report
        );
        checked += 1;
    }
    eprintln!("verified {checked} Java solutions ({skipped} skipped: JDK missing)");
}

/// Every blank has to matter: a starter must not already pass its own tests.
/// A starter that fails to compile counts as failing, which is the normal case
/// for a fill-in-the-blank (`____` is not valid Java).
#[test]
fn every_java_starter_fails() {
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

        let report = judge_with(lang, &ex.starter, &cases, &cfg);
        if report.status == "not_installed" {
            skipped += 1;
            continue;
        }
        assert_ne!(
            report.status, "accepted",
            "Java starter {} ({}) already PASSES — the blank is not load-bearing",
            ex.id, where_
        );
        checked += 1;
    }
    eprintln!("verified {checked} Java starters fail ({skipped} skipped: JDK missing)");
}
