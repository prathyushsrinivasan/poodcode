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

/// Judge an exercise exactly as the app does.
///
/// The ONE place that maps an `Exercise` onto a `JudgeConfig`, so the mapping
/// cannot be right in one test and wrong in another. It matters most for
/// `ts_strictness`: `JudgeConfig::exact` leaves it empty, and an empty preset
/// silently checks every week at plain `strict`.
fn cfg_for(ex: &Exercise) -> JudgeConfig {
    JudgeConfig {
        harness: ex.harness.clone(),
        typecheck_only: ex.judge_mode == "types",
        ts_strictness: ex.strictness.clone(),
        ..JudgeConfig::exact(T)
    }
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

/// Guard against the hole this file used to have.
///
/// `JudgeConfig::exact` leaves `ts_strictness` empty, so a harness that forgets
/// to set it checks all 32 weeks at plain `strict`. That is not a loud failure —
/// it is a silent one: the suite goes green while happily accepting content the
/// app itself rejects, which is exactly how 42 broken exercises shipped past it.
///
/// This proves two things cheaply: the course really does ship exercises at the
/// tighter preset, and the preset really is load-bearing *through the judge*
/// (not merely inside `tscheck`, which has its own unit test for the same).
#[test]
fn the_judge_actually_applies_the_strictness_ladder() {
    let course = load_course();
    let all = all_exercises(&course);
    let indexed: Vec<_> = all
        .iter()
        .filter(|(_, ex)| ex.strictness == "strict+indexed")
        .collect();
    assert!(!indexed.is_empty(), "no exercise ships at strict+indexed — is the ladder wired up?");

    // The mapping the other test relies on must carry the preset through. This
    // is the exact line that was wrong: the config was built without it.
    for (_, ex) in &all {
        assert_eq!(
            cfg_for(ex).ts_strictness,
            ex.strictness,
            "{}: cfg_for dropped the exercise's strictness",
            ex.id
        );
    }

    // Passes `strict`; rejected by `noUncheckedIndexedAccess`, which types a[0]
    // as `number | undefined`.
    let src = "const a: number[] = [1, 2, 3];\nconst first: number = a[0];\nconsole.log(first);\n";
    let cases = vec![TestCase {
        id: 0,
        problem_id: 0,
        kind: "hidden".into(),
        name: "case 1".into(),
        input: String::new(),
        expected_output: "1".into(),
        ordering: 0,
    }];

    let lax = judge_with("typescript", src, &cases, &JudgeConfig::exact(T));
    if lax.status == "not_installed" {
        eprintln!("Node missing; skipping");
        return;
    }
    assert_eq!(lax.status, "accepted", "the baseline preset must accept this: {lax:?}");

    let tight = judge_with(
        "typescript",
        src,
        &cases,
        &JudgeConfig { ts_strictness: "strict+indexed".into(), ..JudgeConfig::exact(T) },
    );
    assert_eq!(
        tight.status, "error",
        "strict+indexed must REJECT a[0] assigned to number — if this passes, the \
         strictness field is being dropped somewhere between here and tsc: {tight:?}"
    );
}

#[test]
fn every_course_solution_passes_its_tests() {
    let course = load_course();

    let mut checked = 0;
    let mut typed = 0;
    let mut skipped = 0;
    for (where_, ex) in all_exercises(&course) {
        let lang = if ex.language.is_empty() { "typescript" } else { &ex.language };
        let cfg = cfg_for(ex);
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
