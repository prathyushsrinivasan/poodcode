//! Trust harness for the Projects track. Every judged exercise (step drills,
//! fix-the-bug programs and each module's build) ships a full reference
//! `solution` and its expected `tests`. This proves, through the REAL judge (the
//! same one the app uses), that each reference program actually produces those
//! outputs — and that each starter is genuinely blanked. Mirrors
//! verify_backend_course.rs and verify_ts_course.rs.
//!
//! The programs are TypeScript, so the judge type-checks them at the exercise's
//! strictness preset BEFORE running them — which is why this test is worth
//! having next to `tools/verify_projects.py`: the Python verifier reimplements
//! that pipeline, and this one is the pipeline. If Node is missing, the
//! run-through is skipped rather than failing the suite.
//!
//! Two structural claims are checked here that no other track needs, because
//! they are what the Projects track promises:
//!
//!   * Every authored module carries the full development process — a `why`, a
//!     `deliverable`, a syntax primer, and steps that each say what to do AND
//!     how to know it worked.
//!   * Every authored module has a revealable `reference`, since "reveal
//!     solution" is a headline feature and an empty reveal is worse than none.

use std::collections::HashSet;
use std::time::Duration;

use poodcode_lib::judge::{judge_with, JudgeConfig};
use poodcode_lib::models::{Exercise, ProjectTrack, TestCase};

const TRACK: &str = include_str!("../seeds/projects.json");
// Type-checking a program costs a `tsc` spawn on top of booting a server, so
// this is roomier than the app's 6s per case.
const T: Duration = Duration::from_secs(30);

fn load_track() -> ProjectTrack {
    serde_json::from_str(TRACK).expect("projects.json parses")
}

/// Every judged exercise in the track (step exercises + each module build).
fn all_exercises(track: &ProjectTrack) -> Vec<(String, &Exercise)> {
    let mut out = Vec::new();
    for p in &track.projects {
        for m in &p.modules {
            for s in &m.steps {
                for ex in &s.exercises {
                    out.push((format!("M{}/{}", m.number, s.key), ex));
                }
            }
            if let Some(ex) = &m.final_build {
                out.push((format!("M{}/final", m.number), ex));
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
    }
}

#[test]
fn track_structure_is_well_formed() {
    let track = load_track();
    assert!(!track.projects.is_empty(), "no projects shipped");

    let mut total = 0;
    let mut ids: HashSet<String> = HashSet::new();

    for p in &track.projects {
        assert!(!p.title.trim().is_empty(), "project {} has no title", p.key);
        assert!(!p.goal.trim().is_empty(), "project {} has no goal", p.key);
        assert!(
            !p.roadmap.is_empty(),
            "project {} has no roadmap — the module list has nothing to group by",
            p.key
        );

        let phases: HashSet<&str> = p.roadmap.iter().map(|r| r.key.as_str()).collect();
        for phase in &p.roadmap {
            assert!(
                !phase.outcome.trim().is_empty(),
                "phase {} has no outcome — a phase that delivers nothing demonstrable is \
                 an arbitrary grouping",
                phase.key
            );
        }

        // Modules are numbered 1..=N with no gaps and no duplicate keys, and each
        // `builds_on` points at an EARLIER module (the ladder must be forward-only,
        // or "continues from the last one" is a lie).
        let mut keys: HashSet<&str> = HashSet::new();
        for (i, m) in p.modules.iter().enumerate() {
            assert_eq!(m.number, (i + 1) as i64, "module {} is out of order", m.key);
            assert!(keys.insert(&m.key), "duplicate module key: {}", m.key);
            assert!(!m.title.trim().is_empty(), "module {} has no title", m.key);
            assert!(
                phases.contains(m.phase.as_str()),
                "module {} names phase {:?}, which is not in the roadmap",
                m.key,
                m.phase
            );
            for dep in &m.builds_on {
                assert!(
                    keys.contains(dep.as_str()),
                    "module {} builds_on {:?}, which is not an earlier module",
                    m.key,
                    dep
                );
            }

            if !m.authored {
                continue;
            }

            // The five things a module promises. Each of these is a headline
            // claim of the track, so an authored module without one is a bug.
            assert!(!m.why.trim().is_empty(), "authored module {} has no `why`", m.key);
            assert!(
                !m.deliverable.trim().is_empty(),
                "authored module {} has no `deliverable` — nothing states what the app \
                 can do at the end of it that it could not at the start",
                m.key
            );
            assert!(
                !m.syntax.is_empty(),
                "authored module {} has no syntax primer — the track's promise is that \
                 nothing is used before it is taught",
                m.key
            );
            assert!(!m.steps.is_empty(), "authored module {} has no steps", m.key);
            assert!(
                m.reference.trim().len() > 200,
                "authored module {} has no revealable reference (or it is a stub)",
                m.key
            );
            assert!(
                !m.acceptance.is_empty(),
                "authored module {} has no acceptance checklist",
                m.key
            );

            for s in &m.syntax {
                assert!(!s.form.trim().is_empty(), "{}: syntax entry with no form", m.key);
                assert!(
                    !s.means.trim().is_empty() || s.recap,
                    "{}: syntax entry {:?} explains nothing",
                    m.key,
                    s.form
                );
            }

            let mut step_keys: HashSet<&str> = HashSet::new();
            for s in &m.steps {
                assert!(step_keys.insert(&s.key), "{}: duplicate step key {}", m.key, s.key);
                // The whole point of the track: every step says what to do and
                // how to know it worked.
                assert!(
                    !s.instructions.trim().is_empty(),
                    "{}/{}: no instructions",
                    m.key,
                    s.key
                );
                assert!(
                    !s.checkpoint.trim().is_empty(),
                    "{}/{}: no checkpoint",
                    m.key,
                    s.key
                );
            }
        }

        for m in &p.modules {
            check_quiz(&m.review, &format!("M{}/review", m.number));
            for s in &m.steps {
                check_quiz(&s.warmup, &format!("M{}/{}/warmup", m.number, s.key));
                check_quiz(&s.quiz, &format!("M{}/{}/quiz", m.number, s.key));
            }
        }
    }

    for (where_, ex) in all_exercises(&track) {
        assert!(!ex.id.is_empty(), "{where_}: exercise with empty id");
        assert!(ids.insert(ex.id.clone()), "duplicate exercise id: {}", ex.id);
        assert!(!ex.title.trim().is_empty(), "{}: empty title", ex.id);
        assert!(!ex.prompt.trim().is_empty(), "{}: empty prompt", ex.id);
        assert!(!ex.solution.trim().is_empty(), "{}: empty solution", ex.id);
        assert_eq!(
            ex.language, "typescript",
            "{}: the Projects track is TypeScript only for now",
            ex.id
        );
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
    assert!(total > 0, "no project exercises shipped");

    let authored: usize = track
        .projects
        .iter()
        .map(|p| p.modules.iter().filter(|m| m.authored).count())
        .sum();
    eprintln!(
        "verified {total} well-formed exercises across {authored} authored modules \
         in {} project(s)",
        track.projects.len()
    );
}

#[test]
fn every_project_solution_passes_its_tests() {
    let track = load_track();

    let mut checked = 0;
    let mut skipped = 0;
    for (where_, ex) in all_exercises(&track) {
        let lang = if ex.language.is_empty() { "typescript" } else { &ex.language };
        // The strictness preset is part of the exercise, and the judge has to be
        // handed it — a program authored under `strict+indexed` may legitimately
        // fail to compile under a different one.
        let cfg = JudgeConfig {
            ts_strictness: ex.strictness.clone(),
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
            "project exercise {} ({}) was NOT accepted: {:?}",
            ex.id, where_, report
        );
        checked += 1;
    }
    eprintln!("verified {checked} project solutions ({skipped} skipped: Node missing)");
}

#[test]
fn every_project_starter_fails() {
    let track = load_track();

    let mut checked = 0;
    let mut skipped = 0;
    for (where_, ex) in all_exercises(&track) {
        let lang = if ex.language.is_empty() { "typescript" } else { &ex.language };
        let cfg = JudgeConfig {
            ts_strictness: ex.strictness.clone(),
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

        let report = judge_with(lang, &ex.starter, &cases, &cfg);
        if report.status == "not_installed" {
            skipped += 1;
            continue;
        }
        // If a starter is accepted there is nothing for the learner to do, and
        // the blank is decorative.
        assert_ne!(
            report.status, "accepted",
            "project starter {} ({}) already PASSES — nothing to solve",
            ex.id, where_
        );
        checked += 1;
    }
    eprintln!("verified {checked} project starters fail ({skipped} skipped: Node missing)");
}
