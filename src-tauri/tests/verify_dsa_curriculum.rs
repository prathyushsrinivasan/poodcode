//! Trust harness for the DSA Curriculum — the Problem Library, taught.
//!
//! `tools/dsa_curriculum.py` asserts these same invariants while authoring, but
//! that only proves the generator was happy on the machine that ran it. This
//! re-asserts them against the **committed seed** the app actually ships, so a
//! hand-edited JSON, a stale regeneration, or a problem renamed in
//! problems.json without touching the curriculum fails `cargo test` rather than
//! showing up as a dead link in the UI.
//!
//! The invariants, in the order the curriculum depends on them:
//!
//! 1. Every problem slug and concept key a unit references really exists.
//! 2. Every problem is placed in **exactly one** unit — so the curriculum and
//!    the library are the same set, and "what is next?" is never ambiguous.
//! 3. Prerequisites point backwards, so the ladder can be walked top to bottom —
//!    and past the foundations stage they are a graph rather than a chain.
//! 4. Rungs climb: within a unit, difficulty never decreases.
//! 5. Every substantial unit opens below its ceiling — a unit of more than four
//!    problems starts on an Intro or an Easy, so "Warm up" is a description
//!    rather than a label.
//! 6. Every unit is actually taught — a why, a model, a ladder and self-checks.

use std::collections::{HashMap, HashSet};

use poodcode_lib::models::{Concept, DsaCurriculum, Problem};

const CURRICULUM: &str = include_str!("../seeds/dsa_curriculum.json");
const PROBLEMS: &str = include_str!("../seeds/problems.json");
const CONCEPTS: &str = include_str!("../seeds/concepts.json");

/// Mirrors `_MAX_CHAIN_RUN` in tools/dsa_curriculum.py.
const MAX_CHAIN_RUN: usize = 2;

/// Mirrors `_ONRAMP_MIN_UNIT` in tools/dsa_curriculum.py — a unit this short is
/// exempt from needing an on-ramp, being over before it can wall anyone off.
const ONRAMP_MIN_UNIT: usize = 4;

fn rank(difficulty: &str) -> i32 {
    match difficulty {
        "Intro" => 0,
        "Easy" => 1,
        "Medium" => 2,
        "Hard" => 3,
        other => panic!("unknown difficulty {other}"),
    }
}

#[test]
fn curriculum_teaches_every_problem_exactly_once() {
    let curriculum: DsaCurriculum =
        serde_json::from_str(CURRICULUM).expect("dsa_curriculum.json parses");
    let problems: Vec<Problem> = serde_json::from_str(PROBLEMS).expect("problems.json parses");
    let concepts: Vec<Concept> = serde_json::from_str(CONCEPTS).expect("concepts.json parses");

    let by_slug: HashMap<&str, &Problem> =
        problems.iter().map(|p| (p.slug.as_str(), p)).collect();
    let concept_keys: HashSet<&str> = concepts.iter().map(|c| c.key.as_str()).collect();

    let mut seen_units: HashSet<&str> = HashSet::new();
    let mut owner: HashMap<&str, &str> = HashMap::new();
    let mut order: Vec<&str> = Vec::new();
    let mut chain_run = 0usize;

    assert!(!curriculum.stages.is_empty(), "no stages shipped");

    for (si, stage) in curriculum.stages.iter().enumerate() {
        assert!(!stage.units.is_empty(), "stage {}: no units", stage.key);

        for unit in &stage.units {
            let k = unit.key.as_str();
            assert!(seen_units.insert(k), "duplicate unit {k}");
            order.push(k);

            // 6 — the unit is actually taught, not just a list of links.
            assert!(!unit.title.trim().is_empty(), "{k}: no title");
            assert!(
                (1..=3).contains(&unit.weight),
                "{k}: weight is {} — interview yield is 1, 2 or 3",
                unit.weight
            );
            assert!(!unit.why.trim().is_empty(), "{k}: no 'why this exists'");
            assert!(!unit.model.trim().is_empty(), "{k}: no mental model");
            assert!(!unit.rungs.is_empty(), "{k}: no problem ladder");
            assert!(!unit.checks.is_empty(), "{k}: no self-check questions");

            // 3 — prerequisites point backwards…
            for p in &unit.prereqs {
                assert!(
                    seen_units.contains(p.as_str()),
                    "{k}: prerequisite {p} is not an earlier unit"
                );
            }

            // …and, past foundations, are not merely the chain. A run of units
            // whose only prereq is the one textually before them is the absence
            // of a dependency graph rather than a shallow one, and it makes the
            // "builds on …" banner assert something false. Counted as a run
            // because one chain link is often the true answer.
            let chained = order.len() >= 2
                && unit.prereqs.len() == 1
                && unit.prereqs[0] == order[order.len() - 2];
            if si > 0 && chained {
                chain_run += 1;
                assert!(
                    chain_run <= MAX_CHAIN_RUN,
                    "{k}: {chain_run} units in a row list only the unit before them as a \
                     prerequisite — that is a chain, not a dependency graph"
                );
            } else {
                chain_run = 0;
            }

            // 1 — concept links resolve.
            for lesson in &unit.lessons {
                assert!(
                    concept_keys.contains(lesson.as_str()),
                    "{k}: unknown concept key {lesson}"
                );
            }

            let mut last_rank = -1;
            let mut first_rung_floor: Option<i32> = None;
            let mut unit_n = 0usize;
            let mut seen_optional = false;
            for rung in &unit.rungs {
                assert!(!rung.slugs.is_empty(), "{k}/{}: empty rung", rung.title);
                assert!(!rung.purpose.trim().is_empty(), "{k}/{}: no purpose", rung.title);

                let mut hardest = -1;
                let mut easiest = i32::MAX;
                let optional = rung.optional;
                for slug in &rung.slugs {
                    // 1 — problem links resolve.
                    let problem = by_slug
                        .get(slug.as_str())
                        .unwrap_or_else(|| panic!("{k}/{}: unknown slug {slug}", rung.title));
                    // 2 — placed exactly once.
                    if let Some(prev) = owner.insert(slug.as_str(), k) {
                        panic!("{slug} is in both {prev} and {k}");
                    }
                    hardest = hardest.max(rank(&problem.difficulty));
                    easiest = easiest.min(rank(&problem.difficulty));
                }
                unit_n += rung.slugs.len();
                for noted in rung.notes.keys() {
                    assert!(
                        rung.slugs.contains(noted),
                        "{k}/{}: note for {noted}, which is not in the rung",
                        rung.title
                    );
                }

                // An optional rung is off the ladder: it holds a unit's surplus,
                // so neither the climb rule nor the on-ramp floor applies to it,
                // and it must come after everything the unit does ask for — or
                // "work down the page" stops being true.
                if optional {
                    seen_optional = true;
                    continue;
                }
                assert!(
                    !seen_optional,
                    "{k}: required rung {} follows an optional one — optional rungs go last",
                    rung.title
                );
                if first_rung_floor.is_none() {
                    first_rung_floor = Some(easiest);
                }

                // 4 — rungs climb (compared on each rung's hardest problem, so a
                // rung may still open with a warm-up of its own).
                assert!(
                    hardest >= last_rank,
                    "{k}: rung {} is easier than the rung before it",
                    rung.title
                );
                last_rank = hardest;
            }
            assert!(
                first_rung_floor.is_some(),
                "{k}: every rung is optional, so the unit asks nothing"
            );

            // 5 — a substantial unit opens below its ceiling. Rule 4 compares
            // each rung's *hardest* problem, so a unit that is ten Mediums and
            // two Hards satisfies it while opening at its own maximum. Stated
            // as "opens on an Intro or an Easy" because that is the property a
            // learner meeting the technique for the first time needs.
            if unit_n > ONRAMP_MIN_UNIT {
                let floor = first_rung_floor.unwrap_or(0);
                assert!(
                    floor <= rank("Easy"),
                    "{k}: {unit_n} problems and the first rung ({}) opens at {} — a first \
                     rung at the unit's ceiling is a wall with a warm-up's label on it",
                    unit.rungs[0].title,
                    if floor == 2 { "Medium" } else { "Hard" }
                );
            }
        }
    }

    // 2, the other half — no problem is unreachable from the curriculum.
    let unplaced: Vec<&str> = problems
        .iter()
        .map(|p| p.slug.as_str())
        .filter(|s| !owner.contains_key(s))
        .collect();
    assert!(
        unplaced.is_empty(),
        "{} problem(s) belong to no unit: {:?}",
        unplaced.len(),
        &unplaced[..unplaced.len().min(12)]
    );
}

/// The teaching surface is what makes this a curriculum rather than a playlist,
/// so it is asserted rather than left to the author's discretion: every unit
/// routes (signals), shows the code (skeletons), prices it (costs) and names
/// what goes wrong (pitfalls).
#[test]
fn every_unit_carries_its_teaching_surface() {
    let curriculum: DsaCurriculum =
        serde_json::from_str(CURRICULUM).expect("dsa_curriculum.json parses");

    for stage in &curriculum.stages {
        for u in &stage.units {
            let k = &u.key;
            assert!(!u.signals.is_empty(), "{k}: no signal → technique rows");
            assert!(!u.skeletons.is_empty(), "{k}: no code skeletons");
            assert!(!u.costs.is_empty(), "{k}: no cost table");
            assert!(!u.pitfalls.is_empty(), "{k}: no pitfalls");
            assert!(!u.interview.trim().is_empty(), "{k}: no interview note");

            for s in &u.skeletons {
                assert!(!s.code.trim().is_empty(), "{k}: skeleton {} has no code", s.name);
            }
            for p in &u.pitfalls {
                assert!(!p.symptom.trim().is_empty(), "{k}: a pitfall has no symptom");
                assert!(!p.fix.trim().is_empty(), "{k}: pitfall '{}' has no fix", p.symptom);
            }
            for c in &u.checks {
                assert!(!c.a.trim().is_empty(), "{k}: check '{}' has no answer", c.q);
            }
        }
    }
}

/// Traces are optional depth, but a ragged one renders as a broken table, so
/// wherever a unit carries them they must be well-formed: every row the same
/// width as the header, and at least two rows — a trace of one step shows
/// nothing changing, which is the only thing a trace is for.
#[test]
fn every_trace_is_a_well_formed_table() {
    let curriculum: DsaCurriculum =
        serde_json::from_str(CURRICULUM).expect("dsa_curriculum.json parses");

    for stage in &curriculum.stages {
        for u in &stage.units {
            for t in &u.traces {
                let k = &u.key;
                assert!(!t.headers.is_empty(), "{k}: trace '{}' has no headers", t.title);
                assert!(
                    t.rows.len() >= 2,
                    "{k}: trace '{}' needs at least two steps to show change",
                    t.title
                );
                assert!(
                    !t.takeaway.trim().is_empty(),
                    "{k}: trace '{}' has no takeaway — the table is not the point, the \
                     sentence it makes obvious is",
                    t.title
                );
                for (i, row) in t.rows.iter().enumerate() {
                    assert_eq!(
                        row.len(),
                        t.headers.len(),
                        "{k}: trace '{}' row {i} has {} cells, expected {}",
                        t.title,
                        row.len(),
                        t.headers.len()
                    );
                }
            }
        }
    }
}

/// The data-structure stage carries depth the technique stages do not need, and
/// it is asserted rather than left to the author's discretion: a unit about a
/// *structure* must explain the layout its costs come from, show the state
/// changing, and ask you to build the thing once.
#[test]
fn structure_units_explain_their_internals() {
    let curriculum: DsaCurriculum =
        serde_json::from_str(CURRICULUM).expect("dsa_curriculum.json parses");

    let stage = curriculum
        .stages
        .iter()
        .find(|s| s.key == "structures")
        .expect("the linear-structures stage exists");

    for u in &stage.units {
        let k = &u.key;
        assert!(!u.internals.trim().is_empty(), "{k}: no internals — what are its costs made of?");
        assert!(!u.build_it.trim().is_empty(), "{k}: no build-it-yourself exercise");
        assert!(!u.traces.is_empty(), "{k}: no worked trace");
    }
}
