//! Trust harness for NEW_DSA (seeds/new_dsa.json, authored in tools/new_dsa.py).
//!
//! `tools/verify_new_dsa.py` is the fast authoring loop; this proves the same
//! through the REAL judge the app uses, at the app's own per-case timeout — so
//! the large generated case in the window-maxima variation is shown to fit the
//! budget an accepted solution actually gets. Also checks that the seed parses
//! into the Rust model and that every topic carries the template's sixteen
//! sections, in order. TypeScript runs via Node type-stripping; if Node is
//! missing the run-through is skipped rather than failing the suite.

use std::collections::HashSet;
use std::time::Duration;

use poodcode_lib::judge::{judge_with, JudgeConfig};
use poodcode_lib::models::{Exercise, NdTopic, NewDsa, QuizQuestion, TestCase};

const SEED: &str = include_str!("../seeds/new_dsa.json");
/// The app's `RUN_TIMEOUT` for exercises (src/commands.rs).
const T: Duration = Duration::from_secs(6);

const SECTIONS: [&str; 16] = [
    "concept",
    "mental_model",
    "ts_fundamentals",
    "patterns",
    "when_to_use",
    "when_not",
    "examples",
    "implementation",
    "complexity",
    "mistakes",
    "recognition",
    "guided",
    "independent",
    "variations",
    "review",
    "mastery",
];

fn load() -> NewDsa {
    serde_json::from_str(SEED).expect("new_dsa.json parses into models::NewDsa")
}

fn exercises(t: &NdTopic) -> Vec<(&'static str, &Exercise)> {
    let mut out: Vec<(&'static str, &Exercise)> = Vec::new();
    for ex in &t.ts_fundamentals.drills {
        out.push(("ts_fundamentals", ex));
    }
    out.push(("implementation", &t.implementation.complete));
    out.push(("implementation", &t.implementation.pseudocode.exercise));
    out.push(("implementation", &t.implementation.scratch));
    for g in &t.guided {
        out.push(("guided", &g.exercise));
    }
    for v in &t.variations {
        if let Some(ex) = &v.exercise {
            out.push(("variations", ex));
        }
    }
    out.push(("mastery", &t.mastery.syntax));
    out.push(("mastery", &t.mastery.implementation));
    out
}

fn questions(t: &NdTopic) -> Vec<&QuizQuestion> {
    let mut out: Vec<&QuizQuestion> = Vec::new();
    out.extend(t.examples.iter().filter_map(|e| e.question.as_ref()));
    out.extend(&t.complexity.questions);
    out.extend(&t.recognition.questions);
    for g in &t.guided {
        out.extend([&g.understand, &g.identify, &g.approach]);
    }
    out.extend(&t.mastery.understanding.questions);
    out.extend(&t.mastery.recognition.questions);
    out
}

#[test]
fn every_topic_follows_the_template() {
    let course = load();
    let keys: Vec<&str> = course.sections.iter().map(|s| s.key.as_str()).collect();
    assert_eq!(keys, SECTIONS, "the course's section list must be the template, in order");
    assert!(!course.topics.is_empty(), "no topics shipped");

    // Key order inside each topic object is irrelevant; presence is not.
    let raw: serde_json::Value = serde_json::from_str(SEED).unwrap();
    for t in raw["topics"].as_array().unwrap() {
        for s in SECTIONS {
            let v = &t[s];
            let empty = v.is_null()
                || v.as_array().is_some_and(|a| a.is_empty())
                || v.as_object().is_some_and(|o| o.is_empty());
            assert!(!empty, "topic {} is missing section {s}", t["key"]);
        }
    }

    let mut ids = HashSet::new();
    for t in &course.topics {
        for (section, ex) in exercises(t) {
            assert!(ids.insert(ex.id.clone()), "duplicate exercise id {}", ex.id);
            assert!(ex.id.starts_with(&format!("ndsa:{}:", t.key)), "{}: not namespaced", ex.id);
            assert_eq!(ex.language, "typescript", "{} ({section}) must be TypeScript", ex.id);
            assert!(!ex.tests.is_empty(), "{} ({section}) has no tests", ex.id);
            assert!(!ex.harness.trim().is_empty(), "{} ({section}) has no checker harness", ex.id);
            assert_ne!(ex.starter, ex.solution, "{}: starter equals solution", ex.id);
        }
        for q in questions(t) {
            assert!(
                q.answer >= 0 && (q.answer as usize) < q.options.len(),
                "{}: answer out of range in {:?}",
                t.key,
                q.question
            );
            assert!(q.answers.iter().all(|&a| a >= 0 && (a as usize) < q.options.len()));
        }
        for g in &t.guided {
            let labels: Vec<&str> = g.hints.iter().map(|h| h.label.as_str()).collect();
            assert_eq!(labels, ["Nudge", "Approach", "Steps", "Code"], "{}/{}", t.key, g.key);
        }
        let m = &t.mastery;
        assert!(m.understanding.pass > 0 && m.understanding.pass as usize <= m.understanding.questions.len());
        assert!(m.recognition.pass > 0 && m.recognition.pass as usize <= m.recognition.questions.len());
        assert!(m.application.need > 0 && m.application.need as usize <= m.application.problems.len());
    }
}

#[test]
fn every_solution_is_accepted_by_the_real_judge() {
    let course = load();
    let mut checked = 0;
    for t in &course.topics {
        for (section, ex) in exercises(t) {
            let cases: Vec<TestCase> = ex
                .tests
                .iter()
                .enumerate()
                .map(|(i, c)| TestCase {
                    id: 0,
                    problem_id: 0,
                    kind: "hidden".into(),
                    name: format!("case {}", i + 1),
                    input: c.input.clone(),
                    expected_output: c.output.clone(),
                    ordering: i as i64,
                })
                .collect();
            let cfg = JudgeConfig { harness: ex.harness.clone(), ..JudgeConfig::exact(T) };
            let report = judge_with("typescript", &ex.solution, &cases, &cfg);
            if report.status == "not_installed" {
                eprintln!("Node missing; skipping");
                return;
            }
            assert_eq!(report.status, "accepted", "{} ({section}) was NOT accepted: {report:?}", ex.id);

            // And the starter is not: a blank or stub that already passes is decorative.
            let starter = judge_with("typescript", &ex.starter, &cases, &cfg);
            assert_ne!(starter.status, "accepted", "{} ({section}): the starter already passes", ex.id);
            checked += 1;
        }
    }
    eprintln!("verified {checked} NEW_DSA solutions (and their starters) through the judge");
}
