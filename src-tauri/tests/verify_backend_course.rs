//! Trust harness for the Backend Lab. Every judged exercise (step drills,
//! fix-the-bug programs and each project's final build) ships a full reference
//! `solution` and its expected `tests`. This proves, through the REAL judge (the
//! same one the app uses), that each reference program actually produces those
//! outputs — and that each starter is genuinely blanked. Mirrors
//! verify_ts_course.rs.
//!
//! The programs are plain JavaScript run by Node: most of them boot a real
//! `node:http` server on port 0 and replay a request script read from stdin. If
//! Node is missing, the run-through is skipped rather than failing the suite.

use std::collections::HashSet;
use std::time::Duration;

use poodcode_lib::judge::{judge_with, JudgeConfig};
use poodcode_lib::models::{BackendTrack, Exercise, TestCase};

const TRACK: &str = include_str!("../seeds/backend_course.json");
// Booting a server and replaying a handful of requests is fast, but scrypt in
// the auth project is deliberately slow — so this is roomier than the app's 6s.
const T: Duration = Duration::from_secs(20);

fn load_track() -> BackendTrack {
    serde_json::from_str(TRACK).expect("backend_course.json parses")
}

/// Every judged exercise in the track (step exercises + each final build).
fn all_exercises(track: &BackendTrack) -> Vec<(String, &Exercise)> {
    let mut out = Vec::new();
    for p in &track.projects {
        for s in &p.steps {
            for ex in &s.exercises {
                out.push((format!("P{}/{}", p.number, s.key), ex));
            }
        }
        if let Some(ex) = &p.final_build {
            out.push((format!("P{}/final", p.number), ex));
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
    }
}

#[test]
fn track_structure_is_well_formed() {
    let track = load_track();
    assert!(!track.projects.is_empty(), "no backend projects shipped");

    // Projects are numbered 1..=N with no gaps and no duplicate keys, and each
    // `builds_on` points at an EARLIER project (the build ladder must be acyclic
    // and forward-only, or "continue from the last one" is a lie).
    let mut keys: HashSet<&str> = HashSet::new();
    for (i, p) in track.projects.iter().enumerate() {
        assert_eq!(p.number, (i + 1) as i64, "project {} is out of order", p.key);
        assert!(keys.insert(&p.key), "duplicate project key: {}", p.key);
        assert!(!p.title.trim().is_empty(), "project {} has no title", p.key);
        assert!(!p.goal.trim().is_empty(), "project {} has no goal", p.key);
        for dep in &p.builds_on {
            assert!(
                keys.contains(dep.as_str()),
                "project {} builds_on {:?}, which is not an earlier project",
                p.key,
                dep
            );
        }
        if p.authored {
            assert!(!p.steps.is_empty(), "authored project {} has no steps", p.key);
            assert!(!p.brief.trim().is_empty(), "project {} has no brief", p.key);
            let mut step_keys: HashSet<&str> = HashSet::new();
            for s in &p.steps {
                assert!(step_keys.insert(&s.key), "{}: duplicate step key {}", p.key, s.key);
                // The whole point of this track: every step says what to do and
                // how to know it worked.
                assert!(
                    !s.instructions.trim().is_empty(),
                    "{}/{}: no instructions",
                    p.key,
                    s.key
                );
                assert!(
                    !s.checkpoint.trim().is_empty(),
                    "{}/{}: no checkpoint",
                    p.key,
                    s.key
                );
            }
            assert!(
                !p.acceptance.is_empty(),
                "authored project {} has no acceptance checklist",
                p.key
            );
        }
    }

    let mut ids = HashSet::new();
    let mut total = 0;
    for (where_, ex) in all_exercises(&track) {
        assert!(!ex.id.is_empty(), "{where_}: exercise with empty id");
        assert!(ids.insert(ex.id.clone()), "duplicate exercise id: {}", ex.id);
        assert!(!ex.title.trim().is_empty(), "{}: empty title", ex.id);
        assert!(!ex.prompt.trim().is_empty(), "{}: empty prompt", ex.id);
        assert!(!ex.solution.trim().is_empty(), "{}: empty solution", ex.id);
        // "fix" exercises hand over a complete buggy program (no blank); every
        // other kind must have a ____ blank to fill.
        if ex.kind == "fix" {
            assert!(!ex.starter.contains("____"), "{}: fix starter should have no blank", ex.id);
        } else {
            assert!(ex.starter.contains("____"), "{}: starter has no ____ blank", ex.id);
        }
        assert_ne!(ex.starter, ex.solution, "{}: starter equals solution", ex.id);
        assert!(!ex.tests.is_empty(), "{}: no tests", ex.id);
        total += 1;
    }
    assert!(total > 0, "no backend exercises shipped");

    for p in &track.projects {
        check_quiz(&p.review, &format!("P{}/review", p.number));
        for s in &p.steps {
            check_quiz(&s.warmup, &format!("P{}/{}/warmup", p.number, s.key));
            check_quiz(&s.quiz, &format!("P{}/{}/quiz", p.number, s.key));
        }
    }
    eprintln!(
        "verified {total} well-formed backend exercises across {} projects",
        track.projects.len()
    );
}

#[test]
fn every_backend_solution_passes_its_tests() {
    let track = load_track();
    let cfg = JudgeConfig {
        mode: "exact".into(),
        tolerance: 0.0,
        function_spec: None,
        checker: None,
        timeout: T,
    };

    let mut checked = 0;
    let mut skipped = 0;
    for (where_, ex) in all_exercises(&track) {
        let lang = if ex.language.is_empty() { "javascript" } else { &ex.language };
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
            "backend exercise {} ({}) was NOT accepted: {:?}",
            ex.id, where_, report
        );
        checked += 1;
    }
    eprintln!("verified {checked} backend solutions ({skipped} skipped: Node missing)");
}
