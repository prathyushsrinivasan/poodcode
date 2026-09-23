//! Trust harness for the 6-Month Mastery programme (seeds/mastery.json).
//!
//! Every week ends in a coding final that gates the next week, so a final whose
//! reference solution does not produce its own expected outputs would lock a
//! learner out of the rest of the programme. This proves, through the REAL judge
//! — the same `run_tests` path `ExamPanel` uses, with no problem id and the
//! final's own strictness preset — that each final's `solution` passes all of its
//! `tests`, and that each `starter` is genuinely blank.
//!
//! Before this file existed, tools/mastery_defs.py already claimed the finals
//! were "proven end-to-end by tests/verify_mastery.rs"; they were not proven by
//! anything, and every expected output in the file was typed by hand.
//!
//! The structural test needs no toolchain. The run-throughs skip languages that
//! are not installed rather than failing the suite.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use std::time::Duration;

use poodcode_lib::judge::{judge_with, JudgeConfig};
use poodcode_lib::models::{Exercise, MasteryExam, MasteryTrack, TestCase};

const MASTERY: &str = include_str!("../seeds/mastery.json");
const PROBLEMS: &str = include_str!("../seeds/problems.json");
// javac + a JVM start per case is slow; the finals themselves are all small.
const T: Duration = Duration::from_secs(20);
const WORKERS: usize = 4;

fn load_tracks() -> Vec<MasteryTrack> {
    serde_json::from_str(MASTERY).expect("mastery.json parses")
}

fn cases(exam: &MasteryExam) -> Vec<TestCase> {
    exam.tests
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
        .collect()
}

/// Every final, labelled for failure messages.
fn all_finals(tracks: &[MasteryTrack]) -> Vec<(String, MasteryExam)> {
    tracks
        .iter()
        .flat_map(|t| {
            t.weeks.iter().filter_map(move |w| {
                w.exam
                    .clone()
                    .map(|e| (format!("{} week {} ({})", t.key, w.week, e.title), e))
            })
        })
        .collect()
}

/// Judge every final's `pick`ed program on a small worker pool, collecting
/// (label, status, report) for each.
fn judge_all(
    finals: &[(String, MasteryExam)],
    pick: fn(&MasteryExam) -> &str,
) -> Vec<(String, String, String)> {
    let next = AtomicUsize::new(0);
    let results = Mutex::new(Vec::new());
    std::thread::scope(|s| {
        for _ in 0..WORKERS {
            s.spawn(|| loop {
                let i = next.fetch_add(1, Ordering::SeqCst);
                let Some((label, exam)) = finals.get(i) else { break };
                // The same settings ExamPanel sends: the final's strictness preset.
                let cfg = JudgeConfig { ts_strictness: exam.strictness.clone(), ..JudgeConfig::exact(T) };
                let report = judge_with(&exam.language, pick(exam), &cases(exam), &cfg);
                results
                    .lock()
                    .unwrap()
                    .push((label.clone(), report.status.clone(), format!("{report:?}")));
            });
        }
    });
    results.into_inner().unwrap()
}

/// Every practice exercise and problem-set problem, labelled. Both are judged
/// the same way — by the exercise's own settings, exactly as `ExerciseCard`
/// sends them.
fn all_practice(tracks: &[MasteryTrack]) -> Vec<(String, Exercise)> {
    tracks
        .iter()
        .flat_map(|t| {
            t.weeks.iter().flat_map(move |w| {
                let practice = w
                    .practice
                    .iter()
                    .map(move |ex| (format!("{} week {} practice {}", t.key, w.week, ex.id), ex.clone()));
                let problems = w
                    .problem_set
                    .iter()
                    .map(move |ex| (format!("{} week {} problem {}", t.key, w.week, ex.id), ex.clone()));
                practice.chain(problems)
            })
        })
        .collect()
}

/// Every runnable project, as a final-shaped value so `judge_all` can run it.
fn all_projects(tracks: &[MasteryTrack]) -> Vec<(String, MasteryExam)> {
    tracks
        .iter()
        .flat_map(|t| {
            t.weeks.iter().filter_map(move |w| {
                w.project_spec.as_ref().map(|p| {
                    (
                        format!("{} week {} project ({})", t.key, w.week, p.title),
                        MasteryExam {
                            title: p.title.clone(),
                            prompt: p.goal.clone(),
                            hint: String::new(),
                            language: p.language.clone(),
                            starter: p.starter.clone(),
                            solution: p.solution.clone(),
                            tests: p.tests.clone(),
                            strictness: p.strictness.clone(),
                        },
                    )
                })
            })
        })
        .collect()
}

/// A project's acceptance tests are what "shipped" means, so its reference must
/// pass them and the starter workspace must not.
#[test]
fn every_project_reference_passes_and_every_starter_fails() {
    let tracks = load_tracks();
    let projects = all_projects(&tracks);
    if projects.is_empty() {
        return;
    }
    for (label, p) in &projects {
        assert!(p.tests.len() >= 5, "{label}: a project needs 5+ acceptance tests");
    }
    let solved = judge_all(&projects, |e| &e.solution);
    let failures: Vec<String> = solved
        .iter()
        .filter(|(_, s, _)| s != "accepted" && s != "not_installed")
        .map(|(label, _, report)| format!("{label}: {report}"))
        .collect();
    assert!(failures.is_empty(), "project references that FAIL:\n{}", failures.join("\n\n"));
    let started = judge_all(&projects, |e| &e.starter);
    let passing: Vec<&String> = started.iter().filter(|(_, s, _)| s == "accepted").map(|(l, _, _)| l).collect();
    assert!(passing.is_empty(), "project starters that already PASS: {passing:?}");
    eprintln!("verified {} projects", projects.len());
}

/// The judge settings an exercise carries — exactly what `ExerciseCard` sends.
fn practice_cfg(ex: &Exercise) -> JudgeConfig {
    JudgeConfig {
        harness: ex.harness.clone(),
        typecheck_only: ex.judge_mode == "types",
        ts_strictness: ex.strictness.clone(),
        forbid: ex.forbid.clone(),
        ..JudgeConfig::exact(T)
    }
}

fn exercise_cases(ex: &Exercise) -> Vec<TestCase> {
    ex.tests
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
        .collect()
}

/// One judged practice program.
struct Judged {
    label: String,
    status: String,
    /// The compiler's output; empty when the program compiled (a runtime error
    /// also reports status "error", so this is how the two are told apart).
    compile_error: String,
    report: String,
}

/// Judge every practice exercise's `pick`ed program with its own settings.
fn judge_practice(items: &[(String, Exercise)], pick: fn(&Exercise) -> &str) -> Vec<Judged> {
    let next = AtomicUsize::new(0);
    let results = Mutex::new(Vec::new());
    std::thread::scope(|s| {
        for _ in 0..WORKERS {
            s.spawn(|| loop {
                let i = next.fetch_add(1, Ordering::SeqCst);
                let Some((label, ex)) = items.get(i) else { break };
                let lang = if ex.language.is_empty() { "typescript" } else { &ex.language };
                let report = judge_with(lang, pick(ex), &exercise_cases(ex), &practice_cfg(ex));
                results.lock().unwrap().push(Judged {
                    label: label.clone(),
                    status: report.status.clone(),
                    compile_error: report.compile_error.clone(),
                    report: format!("{report:?}"),
                });
            });
        }
    });
    results.into_inner().unwrap()
}

#[test]
fn every_practice_solution_passes_and_every_starter_fails() {
    let tracks = load_tracks();
    let items = all_practice(&tracks);
    if items.is_empty() {
        return;
    }
    for (label, ex) in &items {
        assert_ne!(ex.starter, ex.solution, "{label}: starter equals solution");
        if ex.judge_mode == "types" {
            assert!(ex.starter.contains("____"), "{label}: a type-graded starter needs a ____ blank");
            assert!(ex.tests.is_empty(), "{label}: a type-graded exercise must not carry tests");
            assert!(ex.harness.contains("Expect<"), "{label}: a type-graded exercise needs claims");
        } else {
            assert!(!ex.tests.is_empty(), "{label}: needs tests");
        }
    }

    let solved = judge_practice(&items, |ex| &ex.solution);
    let skipped = solved.iter().filter(|j| j.status == "not_installed").count();
    let failures: Vec<String> = solved
        .iter()
        .filter(|j| j.status != "accepted" && j.status != "not_installed")
        .map(|j| format!("{}: {}", j.label, j.report))
        .collect();
    assert!(failures.is_empty(), "practice solutions that FAIL:\n{}", failures.join("\n\n"));

    let starters = judge_practice(&items, |ex| &ex.starter);
    let passing: Vec<&String> = starters
        .iter()
        .filter(|j| j.status == "accepted")
        .map(|j| &j.label)
        .collect();
    assert!(passing.is_empty(), "practice starters that already PASS: {passing:?}");

    // A "read the error" exercise quotes a compiler error; its starter must
    // really produce that code, or the prompt is describing a fiction. A "fix
    // the bug" starter must compile — the bug is supposed to be at runtime.
    for (label, ex) in &items {
        let Some(j) = starters.iter().find(|j| &j.label == label) else { continue };
        if j.status == "not_installed" {
            continue;
        }
        match ex.kind.as_str() {
            "diagnose" => {
                let code = ex
                    .prompt
                    .split("TS")
                    .nth(1)
                    .map(|rest| rest.chars().take_while(|c| c.is_ascii_digit()).collect::<String>())
                    .unwrap_or_default();
                assert!(!code.is_empty(), "{label}: a diagnose prompt must quote a TSnnnn code");
                assert!(
                    j.compile_error.contains(&format!("TS{code}")),
                    "{label}: the prompt quotes TS{code}, but the starter reports: {}",
                    j.report
                );
            }
            "fix" => assert!(
                j.compile_error.is_empty(),
                "{label}: a fix starter must compile — its bug belongs at runtime: {}",
                j.compile_error
            ),
            _ => {}
        }
    }
    eprintln!("verified {} practice exercises ({skipped} skipped)", items.len() - skipped);
}

/// The TypeScript track checks finals with `noUncheckedIndexedAccess` from the
/// week that teaches it. Prove the preset reaches the judge: week 14's own
/// solution with its `?? ""` guards removed must be REJECTED — if it passes,
/// the strictness is being dropped between the seed and tsc.
#[test]
fn indexed_strictness_reaches_the_judge() {
    let tracks = load_tracks();
    let ts = tracks.iter().find(|t| t.key == "typescript").expect("typescript track");
    for w in &ts.weeks {
        let exam = w.exam.as_ref().expect("final");
        let want = if w.week >= 14 { "strict+indexed" } else { "" };
        assert_eq!(exam.strictness, want, "typescript week {}: final strictness", w.week);
    }

    let exam = ts.weeks.iter().find(|w| w.week == 14).and_then(|w| w.exam.clone()).unwrap();
    let unguarded = exam.solution.replace(r#"(lines[i] ?? "")"#, "lines[i]");
    assert_ne!(unguarded, exam.solution, "week 14's solution no longer has the guard this test removes");
    let cfg = JudgeConfig { ts_strictness: exam.strictness.clone(), ..JudgeConfig::exact(T) };
    let report = judge_with(&exam.language, &unguarded, &cases(&exam), &cfg);
    eprintln!("unguarded week-14 final under {}: {}", exam.strictness, report.status);
    if report.status == "not_installed" {
        return;
    }
    assert_eq!(report.status, "error", "an unguarded lines[i] must not compile here: {report:?}");
    assert!(report.compile_error.contains("TS2532") || report.compile_error.contains("TS18048"), "{report:?}");
}

#[test]
fn mastery_structure_is_well_formed() {
    let tracks = load_tracks();
    assert!(!tracks.is_empty(), "no mastery tracks shipped");
    let problems: Vec<serde_json::Value> = serde_json::from_str(PROBLEMS).expect("problems.json parses");
    let starters = |slug: &str| -> Vec<String> {
        problems
            .iter()
            .find(|p| p["slug"] == slug)
            .and_then(|p| p["starter_code"].as_object())
            .map(|o| o.keys().cloned().collect())
            .unwrap_or_default()
    };

    for track in &tracks {
        let numbers: Vec<i64> = track.weeks.iter().map(|w| w.week).collect();
        let expected: Vec<i64> = (1..=track.weeks.len() as i64).collect();
        assert_eq!(numbers, expected, "{}: weeks must be 1..N with no gaps", track.key);
        // Optional weeks sit after the programme proper, never inside it: the
        // UI measures totals and pace over the core weeks only.
        let flags: Vec<bool> = track.weeks.iter().map(|w| w.optional).collect();
        let mut ordered = flags.clone();
        ordered.sort();
        assert_eq!(flags, ordered, "{}: optional weeks must come after every core week", track.key);

        for week in &track.weeks {
            let at = format!("{} week {}", track.key, week.week);
            let exam = week.exam.as_ref().unwrap_or_else(|| panic!("{at}: no coding final"));
            assert_eq!(exam.language, track.exam_language, "{at}: final is in the wrong language");
            assert!(exam.starter.contains("____"), "{at}: final starter has no ____ blank");
            assert!(!exam.tests.is_empty(), "{at}: final has no tests");
            for p in &week.problems {
                assert!(!starters(&p.slug).is_empty(), "{at}: unknown problem {}", p.slug);
            }

            // The TypeScript track is held to the stricter rules it was brought
            // up to (tools/mastery_defs.py, _TRACK_RULES). Checked here too so
            // a hand-edited seed cannot slip past the generator's asserts.
            if track.key == "typescript" {
                assert!(exam.tests.len() >= 8, "{at}: final has {} tests, needs 8", exam.tests.len());
                for p in &week.problems {
                    assert!(
                        starters(&p.slug).iter().any(|l| l == "typescript"),
                        "{at}: {} cannot be opened in TypeScript",
                        p.slug
                    );
                }
            }
        }
    }
}

#[test]
fn every_final_solution_passes_its_tests() {
    let tracks = load_tracks();
    let finals = all_finals(&tracks);
    let results = judge_all(&finals, |e| &e.solution);

    let skipped = results.iter().filter(|(_, s, _)| s == "not_installed").count();
    let failures: Vec<String> = results
        .iter()
        .filter(|(_, s, _)| s != "accepted" && s != "not_installed")
        .map(|(label, _, report)| format!("{label}: {report}"))
        .collect();
    assert!(failures.is_empty(), "finals whose reference solution FAILS:\n{}", failures.join("\n\n"));
    eprintln!(
        "verified {} final solutions ({skipped} skipped: toolchain missing)",
        results.len() - skipped
    );
}

/// Every blank must matter: the starter a learner opens must not already pass.
#[test]
fn every_final_starter_fails() {
    let tracks = load_tracks();
    let finals = all_finals(&tracks);
    let results = judge_all(&finals, |e| &e.starter);

    let passing: Vec<&String> = results
        .iter()
        .filter(|(_, s, _)| s == "accepted")
        .map(|(label, _, _)| label)
        .collect();
    assert!(passing.is_empty(), "final starters that already PASS: {passing:?}");
}
