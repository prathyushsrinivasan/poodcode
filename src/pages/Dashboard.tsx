/**
 * Today — the page that answers "what now?".
 *
 * It used to be a Dashboard that knew about one part of the app: problem
 * counts, daily difficulty goals, a weakest topic, one suggested problem and
 * four buttons that repeated the sidebar. It said nothing about the
 * curriculum's up-next or its review lane, either course's resume point, the
 * project tracks, or the 日本語 cards falling due — so the page meant to point
 * you at your next action could only do it for a third of the app.
 *
 * Now: a continue card per active track, one merged "due now" list, the goals,
 * the streak with seven-day trends, and a twelve-week activity heatmap.
 *
 * It also used to hang on "Loading…" forever if `api.dashboard()` rejected —
 * the failure went to `console.error` and nothing else. Every section here
 * loads independently, so one failure costs one section and says so.
 */

import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import type { CardReview, Dashboard as Dash, Stats, TopicRecommendation } from "../types";
import { formatDuration } from "../lib/format";
import { DiffBadge } from "../components/common";
import { MasteryCard } from "../components/MasteryCard";
import { TrackCardView, useTrackCards } from "../components/today/TrackCards";
import { useCurriculumData } from "../components/CurriculumData";
import { reviewLane } from "../lib/dsaReview";
import {
  heatSeries,
  mergeDue,
  sparklinePath,
  summariseGoals,
  weekOverWeek,
  type DueGroup,
  type GoalSpec,
} from "../lib/today";

/* --------------------------------------------------------------- pieces */

function Sparkline({ values, label }: { values: number[]; label: string }) {
  const path = sparklinePath(values, 72, 22);
  if (!path) return null;
  return (
    <svg className="spark" viewBox="0 0 72 22" role="img" aria-label={label} focusable="false">
      <path d={path} fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  );
}

/** A headline number with its seven-day shape and a week-over-week comparison. */
function StatTile({
  value,
  label,
  series,
  unit = "",
}: {
  value: React.ReactNode;
  label: string;
  series?: number[];
  unit?: string;
}) {
  const trend = series ? weekOverWeek(series) : null;
  return (
    <div className="card stat-tile">
      <div className="stat-tile-top">
        <div>
          <div className="stat-value">{value}</div>
          <div className="stat-label">{label}</div>
        </div>
        {series && series.length > 1 && (
          <Sparkline values={series} label={`${label}, last ${series.length} days`} />
        )}
      </div>
      {trend && (
        <div className={`stat-trend ${trend.direction}`}>
          {trend.percent === null ? (
            <span className="faint">no earlier week to compare</span>
          ) : (
            <>
              {trend.direction === "up" ? "▲" : trend.direction === "down" ? "▼" : "▬"}{" "}
              {Math.abs(trend.percent)}% vs last week
              <span className="faint">
                {" "}
                ({trend.current}
                {unit} vs {trend.previous}
                {unit})
              </span>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function GoalRow({ goal }: { goal: GoalSpec }) {
  const pct = Math.min(100, (goal.done / goal.target) * 100);
  const complete = goal.done >= goal.target;
  return (
    <div className="goal-row">
      <div className="row">
        <span>
          <span aria-hidden>{complete ? "✅" : "⬜"}</span>{" "}
          <span className="sr-only">{complete ? "Met:" : "Not met:"}</span>
          {goal.label}
        </span>
        <span className="spacer" />
        <span className="dim mono">
          {goal.done}/{goal.target}
        </span>
      </div>
      <div className="progress">
        <span style={{ width: `${pct}%`, background: complete ? "var(--good)" : "var(--accent)" }} />
      </div>
    </div>
  );
}

/** Twelve weeks of activity. The full history lives in the heatmap the
 * statistics command already computes; this is the tail of it. */
function Heatmap({ cells }: { cells: { date: string; count: number }[] }) {
  const recent = cells.slice(-84);
  const max = Math.max(1, ...recent.map((c) => c.count));
  return (
    <div className="heatmap" role="img" aria-label={`Activity over the last ${recent.length} days`}>
      {recent.map((c) => (
        <div
          key={c.date}
          className="heat-cell"
          title={`${c.date}: ${c.count === 0 ? "nothing" : `${c.count} solved`}`}
          style={{
            // Five steps, so a quiet day and a busy one are distinguishable.
            background:
              c.count === 0
                ? "var(--bg-elev-2)"
                : `color-mix(in srgb, var(--good) ${20 + Math.round((c.count / max) * 80)}%, transparent)`,
          }}
        />
      ))}
    </div>
  );
}

function SectionError({ what, error, onRetry }: { what: string; error: string; onRetry: () => void }) {
  return (
    <div className="card error-state">
      <strong>Could not load {what}.</strong>
      <p className="dim error-state-detail">{error}</p>
      <button onClick={onRetry}>Retry</button>
    </div>
  );
}

/* ----------------------------------------------------------------- page */

export default function Today() {
  const [dash, setDash] = useState<Dash | null>(null);
  const [dashError, setDashError] = useState("");
  const [stats, setStats] = useState<Stats | null>(null);
  const [recs, setRecs] = useState<TopicRecommendation[]>([]);
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const [cardsDue, setCardsDue] = useState(0);
  const [reload, setReload] = useState(0);
  const nav = useNavigate();

  const { data: curriculum } = useCurriculumData();
  const trackCards = useTrackCards();

  useEffect(() => {
    setDashError("");
    api
      .dashboard()
      .then(setDash)
      .catch((e) => setDashError(String(e)));
  }, [reload]);

  useEffect(() => {
    // Secondary panels. A failure here costs that panel, not the page, so it
    // leaves the section empty rather than shouting.
    api.statistics().then(setStats).catch(() => setStats(null));
    api.learningRecommendations().then(setRecs).catch(() => setRecs([]));
    api
      .cardReviews()
      .then((rs) => setReviews(new Map(rs.map((r) => [r.card_id, r]))))
      .catch(() => setReviews(new Map()));
    api
      .dueFlashcards()
      .then((cs) => setCardsDue(cs.length))
      .catch(() => setCardsDue(0));
  }, [reload]);

  const lane = useMemo(
    () => (curriculum ? reviewLane(curriculum, reviews) : null),
    [curriculum, reviews]
  );

  const due: DueGroup[] = useMemo(() => {
    const groups: DueGroup[] = [];
    if (lane) {
      groups.push({
        source: "curriculum",
        label: "Curriculum self-checks",
        count: lane.checksDue,
        href: "/library",
        hint: "Questions from units you have cleared, due for another look.",
      });
      groups.push({
        source: "slow",
        label: "Slow solves to re-run",
        count: lane.slowSolves,
        href: "/library",
        hint: "Problems you got right, but not quickly. Worth solving again from memory.",
      });
    }
    groups.push({
      source: "flashcards",
      label: "Flashcards",
      count: cardsDue,
      href: "/flashcards",
      hint: "Cards from finished Mastery weeks, missed quiz questions and your own.",
    });
    return mergeDue(groups);
  }, [lane, cardsDue]);

  const solvedSeries = stats ? heatSeries(stats.heatmap, 14) : [];

  const goals = dash
    ? summariseGoals([
        { key: "intro", label: "Solve Intro", done: dash.goal_progress.intro, target: dash.goals.intro },
        { key: "easy", label: "Solve Easy", done: dash.goal_progress.easy, target: dash.goals.easy },
        { key: "medium", label: "Solve Medium", done: dash.goal_progress.medium, target: dash.goals.medium },
        { key: "hard", label: "Solve Hard", done: dash.goal_progress.hard, target: dash.goals.hard },
        // Was "Review problems", pointing at a queue whose UI had been removed.
        // The curriculum's review lane is the thing that actually exists.
        {
          key: "reviews",
          label: "Curriculum reviews",
          done: Math.max(0, (lane?.checksDue ?? 0) === 0 ? dash.goals.reviews : 0),
          target: dash.goals.reviews,
        },
      ])
    : null;

  const today = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="page today-page">
      <h1 className="page-title">Today</h1>
      <p className="page-sub">
        {today}
        {dash && (
          <>
            {" · "}
            {dash.total_solved}/{dash.total_problems} problems solved overall
          </>
        )}
      </p>

      {dashError ? (
        <SectionError what="your progress" error={dashError} onRetry={() => setReload((n) => n + 1)} />
      ) : !dash ? (
        <div className="grid cols-3 today-stats" aria-hidden>
          {[0, 1, 2].map((i) => (
            <div key={i} className="card stat-tile">
              <div className="skel" style={{ height: 28, width: "40%", marginBottom: 8 }} />
              <div className="skel" style={{ height: 12, width: "60%" }} />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid cols-3 today-stats">
          <StatTile value={dash.solved_today} label="Solved today" series={solvedSeries} />
          <StatTile
            value={formatDuration(dash.study_seconds_today)}
            label="Study time today"
          />
          <StatTile value={`${dash.current_streak}🔥`} label="Current streak" />
        </div>
      )}

      {/* ---- Due now: every review system, merged ---- */}
      {due.length > 0 && (
        <section className="today-section" aria-labelledby="due-now">
          <h2 id="due-now" className="today-h2">
            Due now
          </h2>
          <div className="today-due">
            {due.map((g) => (
              <Link key={g.source} className="today-due-row" to={g.href}>
                <span className="today-due-count">{g.count}</span>
                <span className="today-due-body">
                  <span className="today-due-label">{g.label}</span>
                  <span className="today-due-hint">{g.hint}</span>
                </span>
                <span className="today-due-go" aria-hidden>
                  →
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* ---- Continue: one card per started track ---- */}
      <section className="today-section" aria-labelledby="continue">
        <h2 id="continue" className="today-h2">
          Continue
        </h2>
        <div className="today-cards">
          {curriculum?.next && (
            <div className="today-card">
              <div className="today-card-head">
                <span className="today-card-icon" aria-hidden>
                  📚
                </span>
                <span className="today-card-track">DSA Curriculum</span>
              </div>
              <div className="today-card-position">{curriculum.next.unit.unit.title}</div>
              <div className="progress today-card-progress">
                <span
                  style={{
                    width: `${Math.round((curriculum.solved / Math.max(1, curriculum.total)) * 100)}%`,
                  }}
                />
              </div>
              <div className="today-card-detail">
                {curriculum.solved}/{curriculum.total} problems
              </div>
              <Link
                className="today-card-action"
                to={`/library/unit/${curriculum.next.unit.unit.key}`}
              >
                Open the unit →
              </Link>
            </div>
          )}

          {trackCards?.map((c) => (
            <TrackCardView key={c.key} card={c} />
          ))}

          {trackCards !== null && trackCards.length === 0 && !curriculum?.next && (
            <div className="card empty-state">
              <div className="big" aria-hidden>
                🌱
              </div>
              <p>Nothing started yet. Pick a track and solve one problem.</p>
              <Link className="today-card-action" to="/library">
                Open the DSA Curriculum →
              </Link>
            </div>
          )}
        </div>
      </section>

      <MasteryCard />

      {/* ---- Goals and what to shore up ---- */}
      <div className="grid cols-2 today-lower">
        <div className="card">
          <h3 className="card-title">Today's goals</h3>
          {goals ? (
            goals.rows.length === 0 ? (
              <div className="dim">
                No daily targets set. <Link to="/settings">Set them in Settings</Link>.
              </div>
            ) : (
              <>
                {goals.rows.map((g) => (
                  <GoalRow key={g.key} goal={g} />
                ))}
                <div className="faint today-goal-foot">
                  {goals.met}/{goals.total} met · <Link to="/settings">adjust targets</Link>
                </div>
              </>
            )
          ) : (
            <div className="skel" style={{ height: 80 }} />
          )}
        </div>

        <div className="today-suggest">
          <div className="card">
            <div className="stat-label">Weakest topic</div>
            {dash?.weakest_topic ? (
              <>
                {/* Was an unclickable tile: the one thing you would want to do
                    with a weakest topic is go and work on it. */}
                <Link
                  className="today-weak"
                  to={`/library/browse?topic=${encodeURIComponent(dash.weakest_topic)}&status=unsolved`}
                >
                  {dash.weakest_topic} →
                </Link>
                <div className="faint today-weak-note">Based on solved ratio and confidence.</div>
              </>
            ) : (
              <div className="dim">—</div>
            )}
          </div>

          <div className="card">
            <div className="stat-label">Suggested next problem</div>
            {dash?.suggested_problem ? (
              <>
                <div className="row today-suggest-title">
                  <strong>{dash.suggested_problem.title}</strong>
                  <DiffBadge d={dash.suggested_problem.difficulty} />
                </div>
                <div className="tag-row">
                  {dash.suggested_problem.topics.map((t) => (
                    <span key={t} className="badge tag">
                      {t}
                    </span>
                  ))}
                </div>
                <button
                  className="primary today-suggest-go"
                  onClick={() => nav(`/solve/${dash.suggested_problem!.id}`)}
                >
                  Solve now →
                </button>
              </>
            ) : (
              <div className="dim">All caught up 🎉</div>
            )}
          </div>
        </div>
      </div>

      {/* ---- Activity ---- */}
      {stats && stats.heatmap.length > 0 && (
        <section className="today-section" aria-labelledby="activity">
          <h2 id="activity" className="today-h2">
            Activity
          </h2>
          <div className="card">
            <Heatmap cells={stats.heatmap} />
            <div className="faint today-heat-note">
              The last twelve weeks. Longest streak {stats.longest_streak} days.
            </div>
          </div>
        </section>
      )}

      {/* ---- Recommended focus ---- */}
      {recs.length > 0 && (
        <section className="today-section" aria-labelledby="focus">
          <h2 id="focus" className="today-h2">
            Recommended focus
          </h2>
          <div className="card">
            <p className="faint card-intro">
              Your weakest topics — concepts to shore up and a short practice ladder.
            </p>
            {recs.map((r) => (
              <div key={r.topic} className="rec-row">
                <div className="row">
                  <strong>{r.topic}</strong>
                  <span className="spacer" />
                  <span className="dim">
                    {r.solved}/{r.total} solved · confidence {r.avg_confidence.toFixed(1)}
                  </span>
                </div>
                {r.concepts.length > 0 && (
                  <div className="tag-row rec-tags">
                    <span className="dim rec-tags-label">Study:</span>
                    {/* These were `span`s with onClick, unreachable by keyboard. */}
                    {r.concepts.map((c) => (
                      <Link key={c.key} className="badge tag chip-link" to={`/learn/${c.key}`}>
                        📘 {c.name}
                      </Link>
                    ))}
                  </div>
                )}
                {r.problems.length > 0 && (
                  <div className="tag-row rec-tags">
                    <span className="dim rec-tags-label">Practice:</span>
                    {r.problems.map((p) => (
                      <Link
                        key={p.id}
                        className="badge chip-link"
                        to={`/solve/${p.id}`}
                        title={`${p.difficulty} · ${p.solved_status}`}
                      >
                        {p.solved_status === "solved" ? "✅" : "▶"} {p.title}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
