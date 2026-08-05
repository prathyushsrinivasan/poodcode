use chrono::{Duration, Local, NaiveDate};
use rusqlite::Connection;
use serde::Serialize;
use std::collections::BTreeMap;

use crate::error::AppResult;

#[derive(Debug, Default, Serialize)]
pub struct Stats {
    pub total_problems: i64,
    pub total_solved: i64,
    pub by_difficulty: BTreeMap<String, DiffCount>,
    pub by_topic: Vec<TopicStat>,
    pub avg_solve_seconds: i64,
    pub acceptance_rate: f64,
    pub current_streak: i64,
    pub longest_streak: i64,
    pub language_usage: Vec<CountPair>,
    pub heatmap: Vec<HeatCell>,       // last 182 days
    pub weekly_activity: Vec<CountPair>,  // last 12 ISO weeks
    pub monthly_activity: Vec<CountPair>, // last 12 months
    pub weakest_topics: Vec<TopicStat>,
    pub strongest_topics: Vec<TopicStat>,
    // Behavioral / learning-outcome signals.
    pub first_attempt_rate: f64,   // fraction of solved problems solved on the first submission
    pub retention_rate: f64,       // fraction of reviews graded Good/Easy
    pub avg_tries_to_solve: f64,   // mean submissions before the first AC (solved problems)
    pub reviews_total: i64,
    pub mistake_tally: Vec<CountPair>,
    pub topic_behavior: Vec<TopicBehavior>,
}

/// Behavioral mastery per topic, derived from what actually happened rather than
/// self-reported confidence: first-attempt accuracy and hint dependence.
#[derive(Debug, Clone, Serialize)]
pub struct TopicBehavior {
    pub topic: String,
    pub solved: i64,
    pub first_try_solved: i64,
    pub first_try_rate: f64,
    pub avg_hints_used: f64,
    pub mastery: f64, // 0..1 blended behavioral score
}

#[derive(Debug, Default, Serialize)]
pub struct DiffCount {
    pub total: i64,
    pub solved: i64,
}

#[derive(Debug, Clone, Serialize)]
pub struct TopicStat {
    pub topic: String,
    pub total: i64,
    pub solved: i64,
    pub avg_confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct CountPair {
    pub label: String,
    pub value: i64,
}

#[derive(Debug, Serialize)]
pub struct HeatCell {
    pub date: String,
    pub count: i64,
}

fn today() -> NaiveDate {
    Local::now().date_naive()
}

pub fn compute(conn: &Connection) -> AppResult<Stats> {
    let mut s = Stats::default();

    s.total_problems =
        conn.query_row("SELECT COUNT(*) FROM problems", [], |r| r.get(0))?;
    s.total_solved = conn.query_row(
        "SELECT COUNT(*) FROM problems WHERE solved_status = 'solved'",
        [],
        |r| r.get(0),
    )?;

    // By difficulty
    for diff in ["Intro", "Easy", "Medium", "Hard"] {
        let total: i64 = conn.query_row(
            "SELECT COUNT(*) FROM problems WHERE difficulty = ?1",
            [diff],
            |r| r.get(0),
        )?;
        let solved: i64 = conn.query_row(
            "SELECT COUNT(*) FROM problems WHERE difficulty = ?1 AND solved_status = 'solved'",
            [diff],
            |r| r.get(0),
        )?;
        s.by_difficulty
            .insert(diff.to_string(), DiffCount { total, solved });
    }

    // Average solve time over accepted attempts.
    s.avg_solve_seconds = conn
        .query_row(
            "SELECT COALESCE(AVG(duration_seconds),0) FROM attempts
             WHERE status = 'accepted' AND duration_seconds > 0",
            [],
            |r| r.get::<_, f64>(0),
        )
        .unwrap_or(0.0) as i64;

    // Acceptance rate over "submit" attempts (accepted / (accepted+wrong+error)).
    let submits: i64 = conn.query_row(
        "SELECT COUNT(*) FROM attempts WHERE status IN ('accepted','wrong','error')",
        [],
        |r| r.get(0),
    )?;
    let accepted: i64 = conn.query_row(
        "SELECT COUNT(*) FROM attempts WHERE status = 'accepted'",
        [],
        |r| r.get(0),
    )?;
    s.acceptance_rate = if submits > 0 {
        accepted as f64 / submits as f64
    } else {
        0.0
    };

    // Language usage.
    {
        let mut stmt = conn.prepare(
            "SELECT language, COUNT(*) c FROM attempts WHERE language != ''
             GROUP BY language ORDER BY c DESC",
        )?;
        let rows = stmt.query_map([], |r| {
            Ok(CountPair {
                label: r.get(0)?,
                value: r.get(1)?,
            })
        })?;
        s.language_usage = rows.filter_map(|r| r.ok()).collect();
    }

    // Topic stats.
    {
        let mut stmt = conn.prepare(
            "SELECT t.name,
                    COUNT(pt.problem_id) AS total,
                    SUM(CASE WHEN p.solved_status='solved' THEN 1 ELSE 0 END) AS solved,
                    AVG(p.confidence) AS avgc
             FROM tags t
             JOIN problem_tags pt ON pt.tag_id = t.id
             JOIN problems p ON p.id = pt.problem_id
             WHERE t.kind = 'topic'
             GROUP BY t.name ORDER BY t.name",
        )?;
        let rows = stmt.query_map([], |r| {
            Ok(TopicStat {
                topic: r.get(0)?,
                total: r.get(1)?,
                solved: r.get(2)?,
                avg_confidence: r.get::<_, Option<f64>>(3)?.unwrap_or(0.0),
            })
        })?;
        s.by_topic = rows.filter_map(|r| r.ok()).collect();
    }

    // Weakest / strongest: rank topics that have at least one problem by a
    // "mastery" score = solved ratio * (avg confidence / 5).
    let mut ranked: Vec<TopicStat> = s
        .by_topic
        .iter()
        .filter(|t| t.total > 0)
        .cloned()
        .collect();
    ranked.sort_by(|a, b| {
        let ma = mastery(a);
        let mb = mastery(b);
        ma.partial_cmp(&mb).unwrap_or(std::cmp::Ordering::Equal)
    });
    s.weakest_topics = ranked.iter().take(5).cloned().collect();
    s.strongest_topics = ranked.iter().rev().take(5).cloned().collect();

    // Heatmap: solved problems per day (last 182 days).
    let start = today() - Duration::days(181);
    let mut per_day: BTreeMap<String, i64> = BTreeMap::new();
    {
        let mut stmt = conn.prepare(
            "SELECT date, problems_solved FROM daily_sessions WHERE date >= ?1",
        )?;
        let rows = stmt.query_map([start.format("%Y-%m-%d").to_string()], |r| {
            Ok((r.get::<_, String>(0)?, r.get::<_, i64>(1)?))
        })?;
        for row in rows {
            let (d, c) = row?;
            per_day.insert(d, c);
        }
    }
    for i in 0..182 {
        let d = (start + Duration::days(i)).format("%Y-%m-%d").to_string();
        let count = per_day.get(&d).copied().unwrap_or(0);
        s.heatmap.push(HeatCell { date: d, count });
    }

    // Current & longest streak (consecutive days with >=1 solved).
    let (cur, longest) = streaks(&per_day);
    s.current_streak = cur;
    s.longest_streak = longest;

    // Weekly activity (last 12 weeks) and monthly (last 12 months).
    s.weekly_activity = bucketize(&per_day, Bucket::Week);
    s.monthly_activity = bucketize(&per_day, Bucket::Month);

    // Behavioral signals.
    behavioral(conn, &mut s)?;

    Ok(s)
}

/// Derive learning-outcome metrics from attempts, reviews, and mistakes.
fn behavioral(conn: &Connection, s: &mut Stats) -> AppResult<()> {
    // First-attempt rate: of solved problems, how many were AC on their very
    // first submission (no prior wrong/error attempt).
    let solved_ids: Vec<i64> = {
        let mut stmt =
            conn.prepare("SELECT id FROM problems WHERE solved_status = 'solved'")?;
        let rows = stmt.query_map([], |r| r.get::<_, i64>(0))?;
        rows.filter_map(|r| r.ok()).collect()
    };
    let mut first_try = 0i64;
    let mut total_tries_sum = 0i64;
    for pid in &solved_ids {
        // Order attempts oldest-first; count submissions up to and including first AC.
        let mut stmt = conn.prepare(
            "SELECT status FROM attempts WHERE problem_id = ?1
             AND status IN ('accepted','wrong','error','tle') ORDER BY id",
        )?;
        let statuses: Vec<String> = stmt
            .query_map([pid], |r| r.get::<_, String>(0))?
            .filter_map(|r| r.ok())
            .collect();
        let mut tries = 0i64;
        for st in &statuses {
            tries += 1;
            if st == "accepted" {
                break;
            }
        }
        if tries == 0 {
            continue;
        }
        total_tries_sum += tries;
        if statuses.first().map(|x| x == "accepted").unwrap_or(false) {
            first_try += 1;
        }
    }
    let n_solved = solved_ids.len().max(1) as f64;
    s.first_attempt_rate = first_try as f64 / n_solved;
    s.avg_tries_to_solve = total_tries_sum as f64 / n_solved;

    // Retention: fraction of graded reviews that were Good/Easy (quality >= 2).
    s.reviews_total = conn
        .query_row("SELECT COUNT(*) FROM reviews WHERE reps > 0 OR last_quality > 0", [], |r| r.get(0))
        .unwrap_or(0);
    let good: i64 = conn
        .query_row("SELECT COUNT(*) FROM reviews WHERE last_quality >= 2", [], |r| r.get(0))
        .unwrap_or(0);
    s.retention_rate = if s.reviews_total > 0 {
        good as f64 / s.reviews_total as f64
    } else {
        0.0
    };

    // Mistake tally by category.
    {
        let mut stmt =
            conn.prepare("SELECT category, COUNT(*) c FROM mistakes GROUP BY category ORDER BY c DESC")?;
        let rows = stmt.query_map([], |r| {
            Ok(CountPair { label: r.get(0)?, value: r.get(1)? })
        })?;
        s.mistake_tally = rows.filter_map(|r| r.ok()).collect();
    }

    // Per-topic behavioral mastery: first-try rate blended with hint dependence.
    {
        let mut stmt = conn.prepare(
            "SELECT t.name, p.id, p.solved_status,
                    COALESCE(ui.hints_revealed, 0)
             FROM tags t
             JOIN problem_tags pt ON pt.tag_id = t.id
             JOIN problems p ON p.id = pt.problem_id
             LEFT JOIN problem_ui ui ON ui.problem_id = p.id
             WHERE t.kind = 'topic'",
        )?;
        struct Acc {
            solved: i64,
            first_try: i64,
            hints: i64,
        }
        let mut map: BTreeMap<String, Acc> = BTreeMap::new();
        let rows = stmt.query_map([], |r| {
            Ok((
                r.get::<_, String>(0)?,
                r.get::<_, i64>(1)?,
                r.get::<_, String>(2)?,
                r.get::<_, i64>(3)?,
            ))
        })?;
        for row in rows {
            let (topic, pid, status, hints) = row?;
            let entry = map.entry(topic).or_insert(Acc { solved: 0, first_try: 0, hints: 0 });
            if status == "solved" {
                entry.solved += 1;
                entry.hints += hints;
                // First-try lookup.
                let ft: bool = conn
                    .query_row(
                        "SELECT status FROM attempts WHERE problem_id=?1
                         AND status IN ('accepted','wrong','error','tle') ORDER BY id LIMIT 1",
                        [pid],
                        |r| r.get::<_, String>(0),
                    )
                    .map(|x| x == "accepted")
                    .unwrap_or(false);
                if ft {
                    entry.first_try += 1;
                }
            }
        }
        let mut tb: Vec<TopicBehavior> = map
            .into_iter()
            .filter(|(_, a)| a.solved > 0)
            .map(|(topic, a)| {
                let first_try_rate = a.first_try as f64 / a.solved as f64;
                let avg_hints = a.hints as f64 / a.solved as f64;
                // Mastery: reward first-try solves, penalize heavy hint use.
                let mastery = (first_try_rate * (1.0 - (avg_hints / 4.0).min(0.5))).clamp(0.0, 1.0);
                TopicBehavior {
                    topic,
                    solved: a.solved,
                    first_try_solved: a.first_try,
                    first_try_rate,
                    avg_hints_used: avg_hints,
                    mastery,
                }
            })
            .collect();
        tb.sort_by(|a, b| a.mastery.partial_cmp(&b.mastery).unwrap_or(std::cmp::Ordering::Equal));
        s.topic_behavior = tb;
    }

    Ok(())
}

fn mastery(t: &TopicStat) -> f64 {
    let ratio = if t.total > 0 {
        t.solved as f64 / t.total as f64
    } else {
        0.0
    };
    ratio * (t.avg_confidence / 5.0)
}

fn streaks(per_day: &BTreeMap<String, i64>) -> (i64, i64) {
    let solved_days: std::collections::BTreeSet<NaiveDate> = per_day
        .iter()
        .filter(|(_, &c)| c > 0)
        .filter_map(|(d, _)| NaiveDate::parse_from_str(d, "%Y-%m-%d").ok())
        .collect();

    // Current streak: walk back from today.
    let mut current = 0;
    let mut day = today();
    // Allow the streak to be "alive" if today has no solve yet but yesterday did.
    if !solved_days.contains(&day) {
        day -= Duration::days(1);
    }
    while solved_days.contains(&day) {
        current += 1;
        day -= Duration::days(1);
    }

    // Longest streak across the window.
    let mut longest = 0;
    let mut run = 0;
    let mut prev: Option<NaiveDate> = None;
    for d in &solved_days {
        run = match prev {
            Some(p) if *d == p + Duration::days(1) => run + 1,
            _ => 1,
        };
        longest = longest.max(run);
        prev = Some(*d);
    }
    (current, longest)
}

enum Bucket {
    Week,
    Month,
}

fn bucketize(per_day: &BTreeMap<String, i64>, bucket: Bucket) -> Vec<CountPair> {
    let mut agg: BTreeMap<String, i64> = BTreeMap::new();
    for (d, c) in per_day {
        if let Ok(date) = NaiveDate::parse_from_str(d, "%Y-%m-%d") {
            let key = match bucket {
                Bucket::Week => {
                    let iso = date.iso_week();
                    format!("{}-W{:02}", iso.year(), iso.week())
                }
                Bucket::Month => date.format("%Y-%m").to_string(),
            };
            *agg.entry(key).or_insert(0) += c;
        }
    }
    let take = match bucket {
        Bucket::Week => 12,
        Bucket::Month => 12,
    };
    let mut pairs: Vec<CountPair> = agg
        .into_iter()
        .map(|(label, value)| CountPair { label, value })
        .collect();
    let len = pairs.len();
    if len > take {
        pairs = pairs.split_off(len - take);
    }
    pairs
}

use chrono::Datelike;
