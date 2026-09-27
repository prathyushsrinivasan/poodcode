/**
 * Insights: how far along every track is, how the review decks are holding,
 * and what the practice numbers say (UI_ROADMAP I1).
 *
 * The old Statistics page charted problems — difficulty and topics — and was
 * deleted with the other unreachable pages. Most of what the app teaches now
 * is courses, units, modules and decks, so this page starts there: one row per
 * track, in that track's own unit, then the decks, then the problems.
 *
 * Only measured things are shown. The app records solving time per problem and
 * study time per Mastery week; it does not record reading time in a lesson,
 * and the page says so instead of estimating it.
 */

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type {
  BackendTrack,
  CardReview,
  Concept,
  MasteryProgress,
  MasteryTrack,
  Problem,
  ProjectTrack,
  Stats,
  WeeklyCourse,
} from "../types";
import { useCurriculumData } from "../components/CurriculumData";
import { Chart } from "../components/Charts";
import { TrackSkeleton } from "../components/Skeleton";
import { Badge, Card, CardHeader, EmptyState, Icon, PageHeader, ProgressBar, StatTile, type IconName } from "../components/ui";
import { loadDoneChapters } from "../lib/learnProgress";
import { loadConcepts, langLabel } from "./learn/learnData";
import { todayISO } from "../lib/srs";
import { formatStudyTime } from "../lib/mastery";
import { loadFailed } from "../lib/failures";
import {
  backendInsight,
  courseInsight,
  curriculumInsight,
  learnInsights,
  masteryInsight,
  orderTracks,
  projectInsights,
  reviewByDeck,
  reviewHealth,
  share,
  solvingSeconds,
  type TrackInsight,
} from "../lib/insights";

const pctText = (x: number) => `${Math.round(x * 100)}%`;

export default function Insights() {
  const { data: curriculum, error: curriculumError } = useCurriculumData();
  const [done, setDone] = useState<Set<string> | null>(null);
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [ts, setTs] = useState<WeeklyCourse | null>(null);
  const [java, setJava] = useState<WeeklyCourse | null>(null);
  const [backend, setBackend] = useState<BackendTrack | null>(null);
  const [projects, setProjects] = useState<ProjectTrack | null>(null);
  const [mastery, setMastery] = useState<MasteryTrack[]>([]);
  const [rows, setRows] = useState<MasteryProgress[]>([]);
  const [cards, setCards] = useState<CardReview[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [problems, setProblems] = useState<Problem[]>([]);

  useEffect(() => {
    loadDoneChapters()
      .then(setDone)
      .catch((e) => {
        setDone(new Set());
        loadFailed("your completed chapters")(e);
      });
    loadConcepts().then(setConcepts).catch(loadFailed("the concept library"));
    api.tsCourse().then(setTs).catch(loadFailed("the TypeScript course"));
    api.javaCourse().then(setJava).catch(loadFailed("the Java course"));
    api.backendTrack().then(setBackend).catch(loadFailed("the Backend Lab"));
    api.projectsTrack().then(setProjects).catch(loadFailed("the Projects track"));
    api.mastery().then(setMastery).catch(loadFailed("the Mastery programmes"));
    api.masteryProgress().then(setRows).catch(loadFailed("your Mastery progress"));
    api.cardReviews().then(setCards).catch(loadFailed("your review schedule"));
    api.statistics().then(setStats).catch(loadFailed("the practice statistics"));
    api.listProblems().then(setProblems).catch(loadFailed("the problem list"));
  }, []);

  const tracks = useMemo<TrackInsight[]>(() => {
    if (!done) return [];
    const out: TrackInsight[] = [];
    if (curriculum) out.push(curriculumInsight(curriculum));
    if (ts) out.push(courseInsight(ts, "ts-course", done, { key: "ts", label: ts.title, icon: "typescript", href: "/course" }));
    if (java) out.push(courseInsight(java, "java-course", done, { key: "java", label: java.title, icon: "java", href: "/java-course" }));
    if (backend) out.push(backendInsight(backend, done));
    if (projects) out.push(...projectInsights(projects, done));
    for (const t of mastery) out.push(masteryInsight(t, rows));
    out.push(
      ...learnInsights(concepts, done, {
        java: langLabel("java"),
        typescript: langLabel("typescript"),
        algorithms: langLabel("algorithms"),
        java_vocab: langLabel("java_vocab"),
        sql: langLabel("sql"),
        japanese: "日本語",
      })
    );
    return orderTracks(out.filter((t) => t.total > 0));
  }, [done, curriculum, ts, java, backend, projects, mastery, rows, concepts]);

  const today = todayISO();
  const health = useMemo(() => reviewHealth(cards, today), [cards, today]);
  const decks = useMemo(() => reviewByDeck(cards, today), [cards, today]);
  const solving = solvingSeconds(problems);
  const masterySeconds = rows.reduce((s, r) => s + r.study_seconds, 0);

  if (!done) return <TrackSkeleton cards={4} />;

  const started = tracks.filter((t) => t.done > 0);
  const finished = tracks.filter((t) => t.done === t.total);

  return (
    <div className="page insights">
      <PageHeader
        title="Insights"
        subtitle="Where every track stands, how well the review decks are holding, and what the practice numbers say."
      />

      <div className="insight-tiles">
        <StatTile value={`${started.length}/${tracks.length}`} label="Tracks started" icon="layers" hint={`${finished.length} finished`} />
        <StatTile value={health.due} label="Cards due today" icon="refresh" hint={`${health.total} scheduled`} />
        <StatTile
          value={stats ? `${stats.total_solved}/${stats.total_problems}` : "…"}
          label="Problems solved"
          icon="done"
          hint={stats ? `${pctText(stats.acceptance_rate)} of submissions accepted` : undefined}
        />
        <StatTile value={formatStudyTime(solving + masterySeconds)} label="Time measured" icon="clock" hint="Solving plus Mastery study" />
      </div>

      <Card as="section" className="unit-block" labelledBy="ins-tracks">
        <CardHeader
          id="ins-tracks"
          level={2}
          icon="map"
          title="Every track"
          subtitle="In progress first. Each counts in its own unit — a curriculum unit, a course week, a project module."
        />
        {curriculumError && <p className="exercise-note is-warn">The curriculum could not be loaded, so it is missing here.</p>}
        {tracks.length === 0 ? (
          <EmptyState compact icon="map" title="No track content is loaded." />
        ) : (
          <ul className="insight-tracks">
            {tracks.map((t) => (
              <li key={t.key}>
                <Link to={t.href} className="insight-track">
                  <Icon name={t.icon as IconName} size={16} className="insight-track-icon" />
                  <span className="insight-track-name">
                    <strong>{t.label}</strong>
                    {t.note && <span className="exercise-note">{t.note}</span>}
                  </span>
                  <ProgressBar
                    className="insight-track-bar"
                    value={t.done}
                    max={t.total}
                    tone={t.done === t.total ? "good" : "accent"}
                    label={`${t.label}: ${t.done} of ${t.total} ${t.unit}s`}
                  />
                  <span className="insight-track-count mono">
                    {t.done}/{t.total} <span className="faint">{t.unit}s</span>
                  </span>
                  <span className="insight-track-pct mono">{pctText(share(t))}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <div className="insight-grid">
        <Card as="section" labelledBy="ins-review">
          <CardHeader
            id="ins-review"
            level={2}
            icon="refresh"
            title="Review decks"
            subtitle="Every spaced-repetition deck: self-checks, flashcards, vocabulary."
          />
          {health.total === 0 ? (
            <EmptyState compact icon="refresh" title="Nothing scheduled yet.">
              Grade a self-check or a flashcard and it starts coming back on a schedule.
            </EmptyState>
          ) : (
            <>
              <dl className="mastery-stats">
                <div>
                  <dt>Mature</dt>
                  <dd>{pctText(health.mature / health.total)}</dd>
                </div>
                <div>
                  <dt>Last answer right</dt>
                  <dd>{pctText(health.lastPass)}</dd>
                </div>
                <div>
                  <dt>Forgotten</dt>
                  <dd>{pctText(health.lapseRate)}</dd>
                </div>
              </dl>
              <p className="exercise-note">
                Mature means the card's interval has reached three weeks. “Forgotten” is the share of all reviews that
                were answered wrong.
              </p>
              <table className="data static insight-table">
                <thead>
                  <tr>
                    <th scope="col">Deck</th>
                    <th scope="col" className="num">
                      Cards
                    </th>
                    <th scope="col" className="num">
                      Due
                    </th>
                    <th scope="col" className="num">
                      Mature
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {decks.map((d) => (
                    <tr key={d.deck}>
                      <td>{d.deck}</td>
                      <td className="num mono">{d.health.total}</td>
                      <td className="num mono">{d.health.due > 0 ? <Badge tone="accent">{d.health.due}</Badge> : 0}</td>
                      <td className="num mono">{d.health.mature}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </Card>

        <Card as="section" labelledBy="ins-practice">
          <CardHeader id="ins-practice" level={2} icon="target" title="Problem practice" subtitle="From every submission you have made." />
          {!stats ? (
            <p className="exercise-note">Loading…</p>
          ) : (
            <>
              <dl className="mastery-stats">
                <div>
                  <dt>First-try solves</dt>
                  <dd>{pctText(stats.first_attempt_rate)}</dd>
                </div>
                <div>
                  <dt>Tries to solve</dt>
                  <dd>{stats.avg_tries_to_solve.toFixed(1)}</dd>
                </div>
                <div>
                  <dt>Still solvable later</dt>
                  <dd>{pctText(stats.retention_rate)}</dd>
                </div>
              </dl>
              <Chart
                height={200}
                option={{
                  tooltip: { trigger: "axis" },
                  legend: { data: ["Solved", "In the bank"], bottom: 0 },
                  xAxis: { type: "category", data: Object.keys(stats.by_difficulty) },
                  yAxis: { type: "value" },
                  series: [
                    { name: "Solved", type: "bar", data: Object.values(stats.by_difficulty).map((d) => d.solved) },
                    { name: "In the bank", type: "bar", data: Object.values(stats.by_difficulty).map((d) => d.total) },
                  ],
                }}
              />
            </>
          )}
        </Card>
      </div>

      {stats && stats.weekly_activity.length > 0 && (
        <Card as="section" className="unit-block" labelledBy="ins-activity">
          <CardHeader id="ins-activity" level={2} icon="trendUp" title="Activity" subtitle="Problems solved per week." />
          <Chart
            height={200}
            option={{
              tooltip: { trigger: "axis" },
              xAxis: { type: "category", data: stats.weekly_activity.map((p) => p.label) },
              yAxis: { type: "value", minInterval: 1 },
              series: [{ type: "bar", data: stats.weekly_activity.map((p) => p.value) }],
            }}
          />
        </Card>
      )}

      <div className="insight-grid">
        {stats && (stats.weakest_topics.length > 0 || stats.strongest_topics.length > 0) && (
          <Card as="section" labelledBy="ins-topics">
            <CardHeader id="ins-topics" level={2} icon="compare" title="Topics" subtitle="By share solved and your confidence." />
            <div className="insight-topics">
              <TopicList title="Weakest" tone="bad" topics={stats.weakest_topics.slice(0, 6)} />
              <TopicList title="Strongest" tone="good" topics={stats.strongest_topics.slice(0, 6)} />
            </div>
          </Card>
        )}

        <Card as="section" labelledBy="ins-time">
          <CardHeader id="ins-time" level={2} icon="clock" title="Time" subtitle="What is measured, and what is not." />
          <dl className="mastery-stats">
            <div>
              <dt>Solving problems</dt>
              <dd>{formatStudyTime(solving)}</dd>
            </div>
            <div>
              <dt>Mastery study</dt>
              <dd>{formatStudyTime(masterySeconds)}</dd>
            </div>
          </dl>
          {rows.some((r) => r.study_seconds > 0) && (
            <Chart
              height={160}
              option={{
                tooltip: { trigger: "axis" },
                xAxis: { type: "category", data: rows.filter((r) => r.study_seconds > 0).map((r) => `W${r.week}`) },
                yAxis: { type: "value", name: "hours" },
                series: [
                  {
                    type: "bar",
                    data: rows.filter((r) => r.study_seconds > 0).map((r) => Math.round((r.study_seconds / 3600) * 10) / 10),
                  },
                ],
              }}
            />
          )}
          <p className="exercise-note">
            Reading time in lessons and course weeks is not recorded, so it is not shown — the counts above are the honest
            measure of those tracks.
          </p>
        </Card>
      </div>
    </div>
  );
}

function TopicList({ title, tone, topics }: { title: string; tone: "good" | "bad"; topics: Stats["weakest_topics"] }) {
  return (
    <div>
      <div className={`io-label ${tone === "good" ? "is-good" : "is-bad"}`}>{title}</div>
      <ul className="insight-topic-list">
        {topics.map((t) => (
          <li key={t.topic}>
            <span className="insight-topic-name">{t.topic}</span>
            <span className="mono faint cell-small">
              {t.solved}/{t.total}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
