//! Unit tests for critical backend business logic: the spaced-repetition
//! scheduler and progress bookkeeping.

use crate::db;
use crate::models::*;
use crate::repo;

fn conn() -> rusqlite::Connection {
    db::open_memory().expect("memory db")
}

fn sample_problem(slug: &str) -> Problem {
    Problem {
        id: 0,
        slug: slug.into(),
        title: "T".into(),
        difficulty: "Easy".into(),
        description: String::new(),
        constraints: String::new(),
        examples: vec![],
        editorial: String::new(),
        optimal_time: String::new(),
        optimal_space: String::new(),
        optimal_explanation: String::new(),
        starter_code: Default::default(),
        topics: vec!["Arrays".into()],
        subtopics: vec![],
        companies: vec![],
        hints: vec![],
        prerequisites: vec![],
        patterns: vec![],
        function_spec: None,
        judge_mode: "exact".into(),
        float_tolerance: 0.0,
        checker: String::new(),
        time_limit_ms: 0,
        editorials: vec![],
        follow_ups: vec![],
        order: 0,
        test_cases: vec![TestCase {
            id: 0,
            problem_id: 0,
            kind: "hidden".into(),
            name: String::new(),
            input: "1\n".into(),
            expected_output: "1\n".into(),
            ordering: 0,
        }],
        is_favorite: false,
        solved_status: "unsolved".into(),
        confidence: 0,
        last_solved_at: None,
        time_taken_seconds: 0,
        attempts_count: 0,
        success_count: 0,
        created_at: String::new(),
        updated_at: String::new(),
    }
}

#[test]
fn upsert_is_idempotent_by_slug() {
    let c = conn();
    let id1 = repo::upsert_problem(&c, &sample_problem("p1")).unwrap();
    let id2 = repo::upsert_problem(&c, &sample_problem("p1")).unwrap();
    assert_eq!(id1, id2);
    assert_eq!(repo::list_problems(&c).unwrap().len(), 1);
}

#[test]
fn accepted_attempt_marks_solved_and_seeds_review() {
    let c = conn();
    let id = repo::upsert_problem(&c, &sample_problem("p1")).unwrap();
    let attempt = Attempt {
        id: 0,
        problem_id: id,
        language: "python".into(),
        code: "print(1)".into(),
        status: "accepted".into(),
        runtime_ms: Some(5),
        memory_kb: None,
        passed: 1,
        total: 1,
        error_text: String::new(),
        duration_seconds: 120,
        created_at: String::new(),
    };
    repo::record_attempt(&c, &attempt).unwrap();

    let p = repo::get_problem(&c, id).unwrap();
    assert_eq!(p.solved_status, "solved");
    assert_eq!(p.success_count, 1);
    assert_eq!(p.attempts_count, 1);

    // A review should now be due today (ladder index 0 => +1 day, but it is
    // created; due_reviews with a far-future date should include it).
    let far = "2999-01-01";
    let due = repo::due_reviews(&c, far).unwrap();
    assert_eq!(due.len(), 1);
    assert_eq!(due[0].review.interval_index, 0);
}

#[test]
fn review_ladder_advances_and_resets() {
    let c = conn();
    let id = repo::upsert_problem(&c, &sample_problem("p1")).unwrap();
    repo::schedule_after_solve(&c, id).unwrap();

    repo::mark_reviewed(&c, id, true).unwrap(); // Good
    let due = repo::due_reviews(&c, "2999-01-01").unwrap();
    assert_eq!(due[0].review.reps, 1);

    repo::mark_reviewed(&c, id, true).unwrap(); // Good
    let due = repo::due_reviews(&c, "2999-01-01").unwrap();
    assert_eq!(due[0].review.reps, 2);

    // Forgetting (Again) resets reps and records a lapse.
    repo::mark_reviewed(&c, id, false).unwrap();
    let due = repo::due_reviews(&c, "2999-01-01").unwrap();
    assert_eq!(due[0].review.reps, 0);
    assert_eq!(due[0].review.lapses, 1);
}

#[test]
fn sm2_grows_interval_on_good_and_lapses_on_again() {
    // Fresh card, graded Good repeatedly: interval should grow past the first steps.
    let (i1, e1, lapse1) = repo::sm2(1, 2.5, 0, 2);
    assert_eq!(i1, 1);
    assert!(!lapse1);
    let (i2, _e2, _) = repo::sm2(i1, e1, 1, 2); // second good
    assert_eq!(i2, 3);
    let (i3, e3, _) = repo::sm2(i2, 2.5, 2, 2); // third good multiplies by ease
    assert!(i3 >= 6, "interval should compound, got {i3}");
    // Again → lapse, interval resets to 1, ease drops.
    let (i4, e4, lapse4) = repo::sm2(i3, e3, 3, 0);
    assert_eq!(i4, 1);
    assert!(lapse4);
    assert!(e4 < e3, "ease should drop on a lapse");
}

#[test]
fn review_grading_persists_sm2_state() {
    let c = conn();
    let id = repo::upsert_problem(&c, &sample_problem("p1")).unwrap();
    repo::schedule_after_solve(&c, id).unwrap();
    repo::mark_reviewed_quality(&c, id, 3).unwrap(); // Easy
    repo::mark_reviewed_quality(&c, id, 2).unwrap(); // Good
    let due = repo::due_reviews(&c, "2999-01-01").unwrap();
    assert_eq!(due.len(), 1);
    assert!(due[0].review.reps >= 2);
    assert!(due[0].review.interval_days >= 3);
    assert_eq!(due[0].review.last_quality, 2);
}

#[test]
fn confidence_is_clamped() {
    let c = conn();
    let id = repo::upsert_problem(&c, &sample_problem("p1")).unwrap();
    repo::set_confidence(&c, id, 99).unwrap();
    assert_eq!(repo::get_problem(&c, id).unwrap().confidence, 5);
    repo::set_confidence(&c, id, -3).unwrap();
    assert_eq!(repo::get_problem(&c, id).unwrap().confidence, 0);
}


// ---------------------------------------------------------------------------
// Learn chapter completion + mastery progress
//
// These moved out of localStorage specifically so they'd be covered by
// backup/restore, which makes their persistence behaviour worth pinning down.
// ---------------------------------------------------------------------------

#[test]
fn chapter_progress_round_trips_and_is_idempotent() {
    let c = conn();
    assert!(repo::done_chapters(&c).unwrap().is_empty());

    repo::set_chapter_done(&c, "ts_generics", true).unwrap();
    // Marking the same chapter twice must not error or duplicate the row.
    repo::set_chapter_done(&c, "ts_generics", true).unwrap();
    repo::set_chapter_done(&c, "bfs", true).unwrap();
    assert_eq!(repo::done_chapters(&c).unwrap(), vec!["bfs", "ts_generics"]);

    repo::set_chapter_done(&c, "bfs", false).unwrap();
    assert_eq!(repo::done_chapters(&c).unwrap(), vec!["ts_generics"]);

    // Un-marking something never marked is a no-op, not an error.
    repo::set_chapter_done(&c, "never_seen", false).unwrap();
    assert_eq!(repo::done_chapters(&c).unwrap(), vec!["ts_generics"]);
}

fn week_row(c: &rusqlite::Connection, track: &str, week: i64) -> MasteryProgress {
    repo::mastery_progress(c)
        .unwrap()
        .into_iter()
        .find(|r| r.track_key == track && r.week == week)
        .expect("row exists")
}

#[test]
fn mastery_quiz_keeps_only_the_best_score() {
    let c = conn();
    repo::mastery_record_quiz(&c, "ts", 1, 40).unwrap();
    assert_eq!(week_row(&c, "ts", 1).best_quiz, 40);

    repo::mastery_record_quiz(&c, "ts", 1, 100).unwrap();
    assert_eq!(week_row(&c, "ts", 1).best_quiz, 100);

    // A worse retake must not take back a week the learner already unlocked.
    repo::mastery_record_quiz(&c, "ts", 1, 25).unwrap();
    assert_eq!(week_row(&c, "ts", 1).best_quiz, 100);
}

#[test]
fn mastery_exam_pass_is_sticky_but_code_is_not() {
    let c = conn();
    repo::mastery_record_exam(&c, "ts", 3, false, "first try").unwrap();
    let row = week_row(&c, "ts", 3);
    assert!(!row.exam_passed);
    assert_eq!(row.exam_code, "first try");

    repo::mastery_record_exam(&c, "ts", 3, true, "working").unwrap();
    assert!(week_row(&c, "ts", 3).exam_passed);

    // Saving a broken draft afterwards keeps the code but not the failure —
    // otherwise editing a solved week would re-lock everything after it.
    repo::mastery_record_exam(&c, "ts", 3, false, "broken again").unwrap();
    let row = week_row(&c, "ts", 3);
    assert!(row.exam_passed);
    assert_eq!(row.exam_code, "broken again");
}

#[test]
fn mastery_rows_are_scoped_per_track() {
    let c = conn();
    repo::mastery_record_quiz(&c, "ts", 1, 80).unwrap();
    repo::mastery_record_quiz(&c, "java", 1, 55).unwrap();
    assert_eq!(week_row(&c, "ts", 1).best_quiz, 80);
    assert_eq!(week_row(&c, "java", 1).best_quiz, 55);
    assert_eq!(repo::mastery_progress(&c).unwrap().len(), 2);
}

#[test]
fn mastery_project_and_time_accumulate() {
    let c = conn();
    repo::mastery_save_project(&c, "ts", 2, "notes", "code", false).unwrap();
    let row = week_row(&c, "ts", 2);
    assert_eq!(row.project_notes, "notes");
    assert_eq!(row.project_code, "code");
    assert!(!row.project_done);

    repo::mastery_save_project(&c, "ts", 2, "notes v2", "code v2", true).unwrap();
    assert!(week_row(&c, "ts", 2).project_done);

    // Study time adds up rather than overwriting, and ignores nonsense values.
    repo::mastery_log_time(&c, "ts", 2, 60).unwrap();
    repo::mastery_log_time(&c, "ts", 2, 90).unwrap();
    repo::mastery_log_time(&c, "ts", 2, -5).unwrap();
    assert_eq!(week_row(&c, "ts", 2).study_seconds, 150);
}

#[test]
fn mastery_week_completes_exactly_once() {
    let c = conn();
    // The first call stamps it; later calls report false so the caller knows
    // not to seed the week's flashcards and reviews a second time.
    assert!(repo::mastery_mark_complete(&c, "ts", 4).unwrap());
    assert!(!repo::mastery_mark_complete(&c, "ts", 4).unwrap());
    assert!(week_row(&c, "ts", 4).completed_at.is_some());
}

#[test]
fn mastery_touching_a_week_stamps_when_it_started() {
    let c = conn();
    repo::mastery_log_time(&c, "ts", 7, 30).unwrap();
    assert!(week_row(&c, "ts", 7).started_at.is_some());
}
