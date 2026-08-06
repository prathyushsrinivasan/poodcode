//! Trust harness for the problem bank. Two guarantees:
//!
//! 1. `all_problems_have_complete_metadata` — every shipped problem is fully
//!    formed (description, examples, hints, editorial, prerequisites, valid
//!    difficulty/judge-mode, Java + Python starters, well-typed function specs
//!    whose test cases have the right number of argument lines).
//!
//! 2. `every_reference_solution_is_accepted` — a KNOWN-CORRECT solution in each
//!    shipped language, run through the REAL judge, is Accepted. This proves the
//!    computed expected outputs and the harness serialization actually agree
//!    with a correct program (a correct answer is never wrongly rejected).

use std::collections::{HashMap, HashSet};
use std::time::Duration;

use poodcode_lib::judge::{judge_with, JudgeConfig};
use poodcode_lib::models::{Problem, TestCase};

const PROBLEMS: &str = include_str!("../seeds/problems.json");
const REFERENCES: &str = include_str!("../seeds/reference_solutions.json");
const T: Duration = Duration::from_secs(10);

fn load_problems() -> Vec<Problem> {
    serde_json::from_str(PROBLEMS).expect("problems.json parses")
}

const SUPPORTED_TYPES: &[&str] = &[
    "int", "long", "double", "bool", "string", "int[]", "long[]", "double[]", "string[]",
];

#[test]
fn all_problems_have_complete_metadata() {
    let problems = load_problems();
    assert!(!problems.is_empty(), "no problems shipped");
    let mut slugs = HashSet::new();

    for p in &problems {
        let s = &p.slug;
        assert!(!s.is_empty(), "empty slug");
        assert!(slugs.insert(s.clone()), "duplicate slug: {s}");
        assert!(!p.title.trim().is_empty(), "{s}: empty title");
        assert!(
            matches!(p.difficulty.as_str(), "Intro" | "Easy" | "Medium" | "Hard"),
            "{s}: bad difficulty {}",
            p.difficulty
        );
        assert!(!p.description.trim().is_empty(), "{s}: empty description");
        assert!(!p.editorial.trim().is_empty(), "{s}: empty editorial");
        assert!(!p.hints.is_empty(), "{s}: no hints");
        assert!(!p.prerequisites.is_empty(), "{s}: no prerequisites");
        assert!(!p.examples.is_empty(), "{s}: no examples");
        assert!(!p.test_cases.is_empty(), "{s}: no test cases");
        assert!(
            matches!(p.judge_mode.as_str(), "exact" | "float" | "unordered" | "checker"),
            "{s}: bad judge_mode {}",
            p.judge_mode
        );
        assert!(p.starter_code.contains_key("java"), "{s}: no Java starter");
        assert!(p.starter_code.contains_key("python"), "{s}: no Python starter");

        // Optimal-complexity fields should be filled in.
        assert!(!p.optimal_time.trim().is_empty(), "{s}: empty optimal_time");

        // Function-harness problems: valid types + correct argument arity.
        if let Some(fs) = &p.function_spec {
            assert!(!fs.name.is_empty(), "{s}: empty function name");
            assert!(
                SUPPORTED_TYPES.contains(&fs.returns.as_str()),
                "{s}: unsupported return type {}",
                fs.returns
            );
            for param in &fs.params {
                assert!(
                    SUPPORTED_TYPES.contains(&param.ty.as_str()),
                    "{s}: unsupported param type {}",
                    param.ty
                );
            }
            if !fs.params.is_empty() {
                for tc in &p.test_cases {
                    let lines = tc.input.trim_end_matches('\n').split('\n').count();
                    assert_eq!(
                        lines,
                        fs.params.len(),
                        "{s}: test '{}' has {lines} input lines but {} params",
                        tc.name,
                        fs.params.len()
                    );
                }
            }
        }
    }
    eprintln!("verified metadata for {} problems", problems.len());
}

#[test]
fn every_reference_solution_is_accepted() {
    let problems = load_problems();
    let by_slug: HashMap<&str, &Problem> = problems.iter().map(|p| (p.slug.as_str(), p)).collect();
    let references: HashMap<String, HashMap<String, String>> =
        serde_json::from_str(REFERENCES).expect("reference_solutions.json parses");

    let mut checked = 0;
    let mut skipped = 0;
    for (slug, langs) in &references {
        let p = by_slug
            .get(slug.as_str())
            .unwrap_or_else(|| panic!("reference for unknown slug: {slug}"));

        // Judge against hidden cases when present, else the examples — exactly
        // what `submit` does.
        let hidden: Vec<TestCase> = p.test_cases.iter().filter(|c| c.kind == "hidden").cloned().collect();
        let cases: Vec<TestCase> = if hidden.is_empty() {
            p.test_cases.iter().filter(|c| c.kind == "example").cloned().collect()
        } else {
            hidden
        };
        assert!(!cases.is_empty(), "{slug}: no cases to judge");

        for (lang, code) in langs {
            let cfg = JudgeConfig {
                mode: p.judge_mode.clone(),
                tolerance: p.float_tolerance,
                function_spec: p.function_spec.clone(),
                checker: if p.checker.is_empty() { None } else { Some(p.checker.clone()) },
                timeout: T,
            };
            let report = judge_with(lang, code, &cases, &cfg);
            if report.status == "not_installed" {
                skipped += 1;
                continue;
            }
            assert_eq!(
                report.status, "accepted",
                "reference {slug}/{lang} was NOT accepted: {:?}",
                report
            );
            checked += 1;
        }
    }
    eprintln!("verified {checked} reference solutions accepted ({skipped} skipped: toolchain missing)");
    assert!(checked > 0, "no reference solutions could run — is any toolchain installed?");
}
