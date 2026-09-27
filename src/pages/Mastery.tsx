import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import type {
  Concept,
  JudgeReport,
  MasteryExam,
  MasteryProgress,
  MasteryProjectSpec,
  MasteryTrack,
  MasteryWeek,
  Problem,
  TestCase,
} from "../types";
import { Markdown } from "../components/Markdown";
import { CodeEditor } from "../components/CodeEditor";
import { WorkspaceEditor } from "../components/WorkspaceEditor";
import { DiffView } from "../components/DiffView";
import { FailingCases } from "../components/OutputCompare";
import { TsErrorLinks } from "../components/TsErrorLinks";
import { DiffBadge, inlineCode } from "../components/common";
import { QuizChoices } from "../components/QuizChoices";
import { QuizCard } from "../components/exercise";
import { H } from "../components/ui/Heading";
import { Badge, Button, Card, EmptyState, ErrorState, Icon, PageHeader, ProgressBar, Segmented, type IconName } from "../components/ui";
import { answerText, questionText } from "../lib/quizKinds";
import {
  loadDoneChapters,
  loadSolvedExercises,
  markMasterySolved,
  exerciseFailures,
  setChapterDone,
  solvedExercises,
} from "../lib/learnProgress";
import { ExerciseSections } from "../components/ExerciseSections";
import { CapstonePractice } from "../components/MasteryCapstone";
import { MixedQuiz, ReviewSession } from "../components/MasteryReview";
import { DailyTypePuzzle, WeekZero } from "../components/MasteryDaily";
import { typeLadder } from "../lib/typeLadder";
import { predictionLog } from "../lib/predict";
import { flaggedQuestions, quizStats, recordSitting } from "../lib/quizStats";
import { SkillRadar } from "../components/SkillRadar";
import {
  FinalExamPanel,
  ProgrammeSummary,
  useFinalExamState,
} from "../components/MasteryFinalExam";
import { useToast } from "../components/Toast";
import { TrackSkeleton } from "../components/Skeleton";
import {
  TrackBody,
  trackProgress,
  type TrackGroup,
  type TrackSpec,
} from "../components/track/TrackShell";
import {
  drawExamPaper,
  formatStudyTime,
  migrateLegacyQuizScores,
  pacing,
  coreWeeks,
  progressByWeek,
  startDateKey,
  unlockedWeeks,
  weekProgress,
  weekTools,
  budgetNote,
  daysLeftInWeek,
  effectiveStart,
  interleavedWarmup,
  parsePause,
  pauseKey,
  todayPlan,
  togglePause,
  weekLinks,
  requeued,
  mostRetried,
  weakChapters,
  progressReport,
  skillProfile,
  type ExamQuestion,
  type ProgressMap,
  type WeekProgress,
} from "../lib/mastery";
import { ignore, loadFailed, saveFailed } from "../lib/failures";

const TRACK_STORE_KEY = "poodcode:mastery-track";
/** How often accumulated study time is flushed to the backend. */
const TIME_FLUSH_MS = 60_000;
/** Cap on a single flush. A background tab has its timers throttled, and a week
 * left expanded overnight would otherwise log the whole night as study time. */
const MAX_FLUSH_SECONDS = (TIME_FLUSH_MS / 1000) * 2;

export default function Mastery() {
  const [tracks, setTracks] = useState<MasteryTrack[]>([]);
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [done, setDone] = useState<Set<string>>(new Set());
  const [rows, setRows] = useState<MasteryProgress[]>([]);
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [trackKey, setTrackKey] = useState<string>(
    () => localStorage.getItem(TRACK_STORE_KEY) || ""
  );
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const [focusWeek, setFocusWeek] = useState<number | null>(null);
  const [query, setQuery] = useState("");
  const [solvedAll, setSolvedAll] = useState<Set<string>>(() => solvedExercises());
  const [, setParams] = useSearchParams();
  const toast = useToast();

  const saveSetting = useCallback((key: string, value: string) => {
    setSettings((s) => ({ ...s, [key]: value }));
    api.setSetting(key, value).catch(saveFailed("a Mastery setting"));
  }, []);

  const refreshProgress = useCallback(async () => {
    setRows(await api.masteryProgress());
  }, []);

  useEffect(() => {
    setLoadError("");
    // Exam scores used to live in localStorage; fold any leftovers into SQLite
    // before the first read so nothing looks lost on upgrade.
    migrateLegacyQuizScores()
      .catch(ignore("legacy quiz-score migration; it is retried next launch"))
      .then(() =>
        Promise.all([
          api.mastery(),
          api.concepts(),
          api.listProblems(),
          api.masteryProgress(),
          loadDoneChapters(),
          api.getSettings(),
        ])
      )
      .then(([t, c, p, pr, d, s]) => {
        setTracks(t);
        setConcepts(c);
        setProblems(p);
        setRows(pr);
        setDone(d);
        setSettings(s);
      })
      .then(() => loadSolvedExercises().then(setSolvedAll))
      // Was a silent catch, after which the page said "No mastery track is
      // bundled" — a load failure reported as missing content (E2).
      .catch((e) => setLoadError(String(e)))
      .finally(() => setLoading(false));
  }, [attempt]);

  const track = useMemo(
    () => tracks.find((t) => t.key === trackKey) ?? tracks[0],
    [tracks, trackKey]
  );

  const [finalState, saveFinalState] = useFinalExamState(track?.key ?? "");

  const conceptByKey = useMemo(() => {
    const m = new Map<string, Concept>();
    for (const c of concepts) m.set(c.key, c);
    return m;
  }, [concepts]);

  const problemBySlug = useMemo(() => {
    const m = new Map<string, Problem>();
    for (const p of problems) m.set(p.slug, p);
    return m;
  }, [problems]);

  const solvedSlugs = useMemo(
    () => new Set(problems.filter((p) => p.solved_status === "solved").map((p) => p.slug)),
    [problems]
  );

  const progress: ProgressMap = useMemo(
    () => progressByWeek(rows, track?.key ?? ""),
    [rows, track]
  );

  const perWeek = useMemo(
    () =>
      track
        ? track.weeks.map((w) => weekProgress(w, track, done, solvedSlugs, progress))
        : [],
    [track, done, solvedSlugs, progress]
  );

  const unlocked = useMemo(
    () => (track ? unlockedWeeks(track, done, solvedSlugs, progress) : new Set<number>()),
    [track, done, solvedSlugs, progress]
  );

  const phases = useMemo(() => {
    if (!track) return [] as [string, MasteryWeek[]][];
    const map = new Map<string, MasteryWeek[]>();
    for (const w of track.weeks) {
      if (!map.has(w.phase)) map.set(w.phase, []);
      map.get(w.phase)!.push(w);
    }
    return [...map.entries()];
  }, [track]);


  // A week that has just become complete gets stamped server-side, which is
  // also what seeds its flashcards and review entries — once.
  useEffect(() => {
    if (!track) return;
    const newly = track.weeks.filter(
      (w, i) => perWeek[i]?.complete && !progress.get(w.week)?.completed_at
    );
    if (newly.length === 0) return;
    (async () => {
      for (const w of newly) {
        const first = await api.masteryCompleteWeek(track.key, w.week);
        if (first) {
          toast(`Week ${w.week} complete — its review cards are now in Flashcards`);
        }
      }
      await refreshProgress();
    })().catch(saveFailed("the week's completion"));
  }, [track, perWeek, progress, refreshProgress, toast]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key !== "j" && e.key !== "k" && e.key !== "n" && e.key !== "h") return;
      const t = e.target as HTMLElement | null;
      if (t && (t.closest("input, textarea, select, [contenteditable=true], .monaco-editor") !== null)) return;
      if (e.key === "h") {
        // The next hint of the first exercise on screen.
        const hint = [...document.querySelectorAll<HTMLElement>("[data-hint-next]")].find((b) => {
          const r = b.getBoundingClientRect();
          return r.top >= 0 && r.bottom <= window.innerHeight;
        });
        if (hint) {
          e.preventDefault();
          hint.click();
        }
        return;
      }
      const sections = [...document.querySelectorAll<HTMLElement>("[data-spine-section]")];
      if (sections.length === 0) return;
      const tops = sections.map((el) => el.getBoundingClientRect().top);
      const current = Math.max(0, tops.findIndex((top) => top > 90) - 1);
      let target: HTMLElement | undefined;
      if (e.key === "j") target = sections[Math.min(sections.length - 1, tops.findIndex((top) => top > 90))];
      else if (e.key === "k") target = sections[Math.max(0, current - (tops[current]! > 60 ? 1 : 0))];
      else target = sections.slice(current + 1).find((el) => el.dataset.done === "false") ?? sections.find((el) => el.dataset.done === "false");
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  if (loading) return <TrackSkeleton cards={6} />;
  if (loadError) {
    return (
      <div className="page">
        <ErrorState
          title="The Mastery programme could not be loaded."
          error={loadError}
          onRetry={() => {
            setLoading(true);
            setAttempt((n) => n + 1);
          }}
        />
      </div>
    );
  }
  if (!track) {
    return (
      <div className="page">
        <EmptyState icon="mastery" title="No mastery track is bundled." />
      </div>
    );
  }

  // Totals, pace and "finished" count the programme proper; an optional week
  // after it (the capstone) is extra credit.
  const core = coreWeeks(track);
  const corePerWeek = core.map((w) => perWeek[w.week - 1]);
  const completedWeeks = corePerWeek.filter((p) => p.complete).length;
  const currentWeek =
    core.find((w) => unlocked.has(w.week) && !perWeek[w.week - 1].complete)?.week ??
    core.length;
  const totalStudy = perWeek.reduce((sum, p) => sum + p.studySeconds, 0);
  const startedRaw = settings[startDateKey(track.key)];
  const pause = parsePause(settings[pauseKey(track.key)]);
  const effStart = startedRaw ? effectiveStart(new Date(startedRaw), pause) : null;
  const pace = effStart ? pacing(effStart, currentWeek, core.length) : null;
  const finished = completedWeeks === core.length;

  // X-61: today's share of the current week.
  const current = track.weeks.find((w) => w.week === currentWeek);
  const currentProgress = current ? perWeek[current.week - 1] : undefined;
  const plan =
    current && currentProgress && !finished
      ? todayPlan({
          chaptersLeft: current.concepts.filter((k) => !done.has(k)).map((k) => conceptByKey.get(k)?.name ?? k),
          practiceLeft: (current.practice ?? []).filter((e) => !solvedAll.has(e.id)).length,
          problemsLeft:
            currentProgress.problemsTotal -
            currentProgress.problemsSolved +
            (current.problem_set ?? []).filter((e) => !solvedAll.has(e.id)).length,
          projectDone: currentProgress.projectDone,
          hasProject: !!current.project,
          quizPassed: currentProgress.quizPassed,
          examPassed: currentProgress.examPassed,
          daysLeft: effStart ? daysLeftInWeek(effStart, currentWeek) : 7,
        })
      : [];

  // X-73: search the programme — week titles and goals, chapter names and keys.
  const q = query.trim().toLowerCase();
  const hits =
    q.length < 2
      ? []
      : track.weeks.filter((w) =>
          [w.title, w.goal, w.project, ...w.concepts, ...w.concepts.map((k) => conceptByKey.get(k)?.name ?? "")]
            .join(" ")
            .toLowerCase()
            .includes(q)
        );

  function openWeek(n: number) {
    const w = track.weeks.find((x) => x.week === n);
    if (!w) return;
    setParams({ group: w.phase }, { replace: true });
    setFocusWeek(null);
    setTimeout(() => setFocusWeek(n), 0);
  }

  async function exportJson() {
    const { json } = progressReport(track, perWeek, progress);
    try {
      const { save } = await import("@tauri-apps/plugin-dialog");
      const path = await save({
        defaultPath: `poodcode-${track.key}-progress.json`,
        filters: [{ name: "JSON", extensions: ["json"] }],
      });
      if (!path) return;
      await api.writeFile(path, json);
      toast("Progress exported");
    } catch (e) {
      toast(`Could not export: ${e}`);
    }
  }

  async function copyMarkdown() {
    try {
      await navigator.clipboard.writeText(progressReport(track, perWeek, progress).markdown);
      toast("Progress copied as a Markdown table");
    } catch {
      toast("The clipboard is not available here");
    }
  }

  function flipPause() {
    const next = togglePause(pause);
    saveSetting(pauseKey(track.key), JSON.stringify(next));
    toast(next.pausedAt ? "Pacing paused — the calendar stops until you resume" : "Pacing resumed");
  }

  /* The programme as a track: phases are the rail, weeks are the units. They
     expand in place rather than navigating, so `renderUnit` supplies the card
     and `base` is never used for a link (UI_ROADMAP G1). */
  const spec: TrackSpec = {
    title: track.title,
    subtitle: track.subtitle,
    base: "/mastery",
    unitLabel: "Week",
    groupLabel: "Phase",
    groups: phases.map<TrackGroup>(([phase]) => ({
      key: phase,
      title: phase,
      goal: track.phase_goals?.[phase],
    })),
    progressRings: true,
    units: track.weeks.map((w) => ({
      slug: String(w.week),
      number: w.week,
      title: w.title,
      group: w.phase,
      done: perWeek[w.week - 1].complete,
      authored: true,
    })),
    renderUnit: (u) => {
      const w = track.weeks.find((x) => x.week === u.number);
      if (!w) return null;
      return (
        <WeekCard
          week={w}
          track={track}
          row={progress.get(w.week)}
          progress={perWeek[w.week - 1]}
          locked={!unlocked.has(w.week)}
          conceptByKey={conceptByKey}
          problemBySlug={problemBySlug}
          done={done}
          onToggleChapter={toggleChapter}
          onChanged={refreshProgress}
          settings={settings}
          saveSetting={saveSetting}
          focused={focusWeek === w.week}
        />
      );
    },
  };

  async function pickTrack(key: string) {
    setTrackKey(key);
    localStorage.setItem(TRACK_STORE_KEY, key);
  }

  async function beginTrack() {
    const iso = new Date().toISOString();
    await api.setSetting(startDateKey(track.key), iso);
    setSettings((s) => ({ ...s, [startDateKey(track.key)]: iso }));
    toast("Programme started — pacing is now tracked against today");
  }

  async function toggleChapter(key: string) {
    setDone(await setChapterDone(done, key, !done.has(key)));
  }

  return (
    <div className="page">
      <PageHeader
        title={track.title}
        subtitle={track.subtitle}
        actions={
          tracks.length > 1 && (
            <Segmented
              label="Programme"
              value={track.key}
              onChange={pickTrack}
              options={tracks.map((t) => ({ value: t.key, label: t.title }))}
            />
          )
        }
      />

      <Card className="unit-block mastery-summary">
        <p className="mastery-intro">{track.intro}</p>
        <dl className="mastery-stats">
          <div>
            <dt>Weeks done</dt>
            <dd>
              {completedWeeks}
              <span className="dim"> / {core.length}</span>
            </dd>
          </div>
          <div>
            <dt>Current week</dt>
            <dd>{currentWeek}</dd>
          </div>
          <div>
            <dt>Studied here</dt>
            <dd>{formatStudyTime(totalStudy)}</dd>
          </div>
          <div>
            <dt>Pass mark</dt>
            <dd>{track.pass_mark}%</dd>
          </div>
        </dl>
        <ProgressBar
          value={completedWeeks}
          max={core.length}
          tone={completedWeeks === core.length ? "good" : "accent"}
          label="Weeks of the programme done"
        />
        <details className="mastery-skills">
          <summary className="dim quiz-note">Skills — what kinds of work you have done</summary>
          <SkillRadar skills={skillProfile(track, solvedAll, perWeek)} />
        </details>
        <div className="mastery-summary-actions">
          <Button variant="ghost" size="sm" icon="download" onClick={exportJson} title="Save every week's progress as JSON — for a portfolio or a mentor.">
            Export progress
          </Button>
          <Button variant="ghost" size="sm" icon="copy" onClick={copyMarkdown} title="Copy a progress table you can paste anywhere.">
            Copy as Markdown
          </Button>
        </div>

        {pace ? (
          <p className="section-lead mastery-pace">
            Started {new Date(startedRaw!).toLocaleDateString()} · the calendar says{" "}
            <strong>Week {pace.scheduledWeek}</strong> ·{" "}
            {pace.weeksBehind > 0 ? (
              <span className="is-bad">
                {pace.weeksBehind} week{pace.weeksBehind > 1 ? "s" : ""} behind
              </span>
            ) : pace.weeksBehind < 0 ? (
              <span className="is-good">
                {-pace.weeksBehind} week{pace.weeksBehind < -1 ? "s" : ""} ahead
              </span>
            ) : (
              <span className="is-good">on track</span>
            )}
            {!finished && (
              <> · at this pace you finish {pace.projectedFinish.toLocaleDateString()}</>
            )}
            {!finished && (
              <>
                {" · "}
                <button className="linklike" onClick={flipPause} title="A holiday stops the calendar: paused days never count against your pace.">
                  {pause.pausedAt
                    ? `resume (paused since ${new Date(pause.pausedAt).toLocaleDateString()})`
                    : "pause for a holiday"}
                </button>
              </>
            )}
          </p>
        ) : (
          <div className="exercise-actions mastery-pace">
            <Button variant="primary" icon="run" onClick={beginTrack}>
              Start the programme
            </Button>
            <span className="exercise-note">Sets today as week 1 so pacing and a finish date can be tracked.</span>
          </div>
        )}
      </Card>

      {plan.length > 0 && current && (
        <div className="card card-accent mastery-today unit-block">
          <div className="io-label is-accent">
            <Icon name="target" size={13} /> Today, at your pace — Week {current.week}: {current.title}
          </div>
          <ol className="unit-list">
            {plan.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
          <div className="exercise-actions">
            <Button variant="ghost" iconRight="forward" onClick={() => openWeek(current.week)}>
              Open Week {current.week}
            </Button>
            <span className="dim quiz-note">
              {effStart
                ? `What is left of this week, spread over the ${daysLeftInWeek(effStart, currentWeek)} day(s) left in it.`
                : "Start the programme to spread this over the days of the week."}
            </span>
          </div>
        </div>
      )}

      <div className="learn-filters" role="search">
        <label className="learn-search">
          <Icon name="search" size={15} />
          <span className="sr-only">Search the programme</span>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search the programme — a topic, a chapter, a keyword"
          />
        </label>
        {hits.length > 0 && (
          <span className="exercise-note" role="status">
            {hits.length} week{hits.length === 1 ? "" : "s"}
          </span>
        )}
      </div>
      {hits.length > 0 && (
        <Card className="unit-block">
          <ul className="mastery-hits">
            {hits.slice(0, 12).map((w) => (
              <li key={w.week}>
                <button type="button" className="link-button" onClick={() => openWeek(w.week)}>
                  Week {w.week} — {w.title}
                </button>
                <span className="exercise-note">{w.phase}</span>
                {!unlocked.has(w.week) && <Icon name="locked" size={12} label="Locked" />}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {completedWeeks === 0 && (
        <WeekZero
          track={track}
          exercise={track.week_zero ?? null}
          settings={settings}
          saveSetting={saveSetting}
          onOpenWeek={openWeek}
        />
      )}

      <DailyTypePuzzle
        track={track}
        reachedWeek={Math.max(0, ...[...unlocked])}
        settings={settings}
        saveSetting={saveSetting}
      />

      <ReviewSession
        trackTitle={track.title}
        weeks={core}
        perWeek={corePerWeek}
        onOpenWeek={openWeek}
        weakChapters={weakChapters(
          core
            .filter((_, i) => corePerWeek[i]?.complete)
            .flatMap((w) => w.concepts)
            .map((k) => conceptByKey.get(k))
            .filter((c): c is Concept => !!c),
          exerciseFailures(),
          solvedAll
        )}
      />

      {finished && (
        <ProgrammeSummary
          track={track}
          weeks={core}
          perWeek={corePerWeek}
          totalStudy={totalStudy}
          exam={track.final_exam ?? null}
          attempts={finalState?.attempts ?? []}
        />
      )}
      {track.final_exam && finalState && (
        <FinalExamPanel
          exam={track.final_exam}
          weeks={core}
          finished={finished}
          remaining={core.length - completedWeeks}
          state={finalState}
          onChange={saveFinalState}
        />
      )}

      <TrackBody spec={spec} progress={trackProgress(spec.units)} />

      <QuestionStats />
    </div>
  );
}

/** X-38: questions you keep missing and questions you never miss, from every
 * marked sitting on this device. */
function QuestionStats() {
  const [open, setOpen] = useState(false);
  const flagged = open ? flaggedQuestions(quizStats()) : null;
  return (
    <details className="card mastery-practice mastery-stats-panel" onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
      <summary>
        <strong>Question stats</strong>{" "}
        <span className="dim quiz-note">which questions you keep missing, and which you never miss</span>
      </summary>
      {flagged && (
        <>
          <div className="io-label">Missed most — a real gap, or an ambiguous question</div>
          {flagged.missed.length === 0 && <p className="dim quiz-note">Nothing yet — a question needs two sittings.</p>}
          {flagged.missed.slice(0, 15).map((r) => (
            <div key={r.question} className="quiz-note mastery-stat-row">
              <Badge tone="bad">
                {r.right}/{r.attempts}
              </Badge>{" "}
              {inlineCode(r.question)}
            </div>
          ))}
          <div className="io-label">Never missed — maybe too easy</div>
          {flagged.tooEasy.length === 0 && <p className="dim quiz-note">Nothing yet — a question needs three sittings.</p>}
          {flagged.tooEasy.slice(0, 15).map((r) => (
            <div key={r.question} className="quiz-note mastery-stat-row">
              <Badge tone="good">
                {r.right}/{r.attempts}
              </Badge>{" "}
              {inlineCode(r.question)}
            </div>
          ))}
        </>
      )}
    </details>
  );
}

function Bar({ percent, label }: { percent: number; label: string }) {
  return (
    <ProgressBar
      className="week-bar"
      value={percent}
      max={100}
      tone={percent === 100 ? "good" : "accent"}
      label={label}
      size="sm"
    />
  );
}

type SpineItem = {
  id: string;
  icon: IconName;
  label: string;
  detail: string;
  done: boolean;
  /** Part of the week's gate (chapters, quiz, final). */
  gate?: boolean;
};

const prettyKey = (key: string) => key.replace(/-/g, " ").replace(/^./, (c) => c.toUpperCase());

function WeekCard({
  week,
  track,
  row,
  progress,
  locked,
  conceptByKey,
  problemBySlug,
  done,
  onToggleChapter,
  onChanged,
  settings,
  saveSetting,
  focused,
}: {
  week: MasteryWeek;
  track: MasteryTrack;
  row: MasteryProgress | undefined;
  progress: WeekProgress;
  locked: boolean;
  conceptByKey: Map<string, Concept>;
  problemBySlug: Map<string, Problem>;
  done: Set<string>;
  onToggleChapter: (key: string) => void;
  onChanged: () => Promise<void>;
  settings: Record<string, string>;
  saveSetting: (key: string, value: string) => void;
  /** Set when search picked this week: open it and scroll to it. */
  focused: boolean;
}) {
  const nav = useNavigate();
  const toast = useToast();
  const [open, setOpen] = useState(!locked && !progress.complete);
  const practice = week.practice ?? [];
  const problemSet = week.problem_set ?? [];
  // The warm-up: interleaved review (X-53) plus anything failed twice in an
  // earlier week and still unsolved (X-52). Fixed when the week opens, so an
  // item solved here does not vanish from under the learner.
  const warmup = useMemo(() => {
    const base = interleavedWarmup(track.weeks, week.week);
    const again = requeued(track.weeks, week.week, exerciseFailures(), solvedExercises()).filter(
      (e) => !base.some((b) => b.id === e.id)
    );
    return [...base, ...again];
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [track.weeks, week.week, open]);
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const practiceSolved = practice.filter((ex) => solvedEx.has(ex.id)).length;
  const setSolved = problemSet.filter((ex) => solvedEx.has(ex.id)).length;
  const warmupSolved = warmup.filter((ex) => solvedEx.has(ex.id)).length;
  const notesKey = `mastery-notes:${track.key}:${week.week}`;
  const [notes, setNotes] = useState(settings[notesKey] ?? "");
  const cardRef = useRef<HTMLDivElement | null>(null);
  const anchor = (id: string) => `w${week.week}-${id}`;

  useEffect(() => {
    if (!focused || locked) return;
    setOpen(true);
    const t = setTimeout(() => cardRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
    return () => clearTimeout(t);
  }, [focused, locked]);

  // Practice solved-state lives in SQLite; the initialiser reads the warm
  // session cache and this fills it on a cold start.
  useEffect(() => {
    if (practice.length === 0 && problemSet.length === 0 && warmup.length === 0) return;
    loadSolvedExercises().then(setSolvedEx).catch(loadFailed("your solved exercises"));
  }, [practice.length, problemSet.length, warmup.length]);

  // Study time is accumulated only while this week is expanded, then flushed
  // periodically and on collapse. It also lands in daily_sessions, so mastery
  // work counts toward the heatmap and streak like everything else.
  const opened = useRef<number | null>(null);
  useEffect(() => {
    if (locked || !open) return;
    opened.current = Date.now();
    const flush = () => {
      if (opened.current === null) return;
      const elapsed = Math.round((Date.now() - opened.current) / 1000);
      opened.current = Date.now();
      const seconds = Math.min(elapsed, MAX_FLUSH_SECONDS);
      if (seconds > 0) api.masteryLogTime(track.key, week.week, seconds).catch(saveFailed("study time"));
    };
    const timer = setInterval(flush, TIME_FLUSH_MS);
    return () => {
      clearInterval(timer);
      flush();
      opened.current = null;
    };
  }, [locked, open, track.key, week.week]);

  if (locked) {
    // X-75: a sealed week still shows where the programme goes.
    return (
      <div className="card week-card locked" id={`week-${week.week}`} ref={cardRef}>
        <div className="week-head is-locked">
          <span className="week-num">
            <Icon name="locked" size={14} label="Locked" />
          </span>
          <div className="week-head-text">
            <strong className="dim">
              Week {week.week} — {week.title}
            </strong>
            <p className="week-goal">{week.goal}</p>
            {week.concepts.length > 0 && (
              <p className="exercise-note">Chapters: {week.concepts.map((k) => conceptByKey.get(k)?.name ?? k).join(" · ")}</p>
            )}
            <p className="exercise-note">
              Opens when Week {week.week - 1} is finished — every chapter marked done, the quiz passed at{" "}
              {track.pass_mark}%, and its coding final accepted.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const links = weekLinks(track.key, week.week);
  // X-44: the arc project's progress lives in settings (one row per week holds
  // the weekly project).
  const arcKey = `mastery-arc:${track.key}:${week.week}`;
  const arc = parseArc(settings[arcKey]);
  // M1-03: predict-first, a per-learner switch for months 1-2.
  const predictKey = `mastery-predict-first:${track.key}`;
  const predictFirst = week.week <= 8 && settings[predictKey] === "1";
  // M3-04: the week the strictness ladder steps up says so.
  const previous = track.weeks.find((w) => w.week === week.week - 1);
  const strictStep =
    week.exam?.strictness === "strict+indexed" && previous?.exam?.strictness !== "strict+indexed";
  // X-35: a checkpoint draws on its whole month; type-level months add puzzles.
  const monthWeeks = track.weeks.filter((w) => w.phase === week.phase && !w.optional && w.week <= week.week);
  const monthPuzzles = week.contest
    ? (() => {
        const ladder = typeLadder(monthWeeks);
        if (ladder.length < 5) return [];
        const step = Math.max(1, Math.floor(ladder.length / 10));
        return ladder.filter((_, i) => i % step === 0).slice(0, 10).map((r) => r.exercise);
      })()
    : [];
  // X-82: what slowed you down — the item with the most failed runs.
  const retried = mostRetried(
    [...practice, ...problemSet, ...(week.exam?.types ? [week.exam.types] : [])],
    exerciseFailures()
  );
  const budget = budgetNote(progress.studySeconds);
  const spine: SpineItem[] = [];
  if (week.concepts.length > 0) {
    spine.push({
      id: "read",
      icon: "learn",
      label: "Read",
      detail: `${progress.conceptsDone}/${progress.conceptsTotal}`,
      done: progress.conceptsDone === progress.conceptsTotal,
      gate: true,
    });
  }
  if (practice.length + warmup.length > 0) {
    spine.push({
      id: "practice",
      icon: "edit",
      label: "Practise",
      detail: `${practiceSolved + warmupSolved}/${practice.length + warmup.length}`,
      done: practiceSolved + warmupSolved === practice.length + warmup.length,
    });
  }
  if (week.problems.length + problemSet.length > 0) {
    spine.push({
      id: "problems",
      icon: "target",
      label: "Problems",
      detail: `${progress.problemsSolved + setSolved}/${week.problems.length + problemSet.length}`,
      done: progress.problemsSolved + setSolved === week.problems.length + problemSet.length,
    });
  }
  if (week.project) {
    spine.push({ id: "project", icon: "build", label: "Project", detail: progress.projectDone ? "shipped" : "open", done: progress.projectDone });
  }
  spine.push({
    id: "quiz",
    icon: "checklist",
    label: "Quiz",
    detail: progress.score === null ? "—" : `${progress.score}%`,
    done: progress.quizPassed,
    gate: true,
  });
  if (week.exam) {
    spine.push({ id: "final", icon: "playground", label: "Final", detail: progress.examPassed ? "passed" : "—", done: progress.examPassed, gate: true });
  }
  spine.push({ id: "notes", icon: "notes", label: "Notes", detail: notes.trim() ? "✎" : "", done: true });

  const go = (id: string) =>
    document.getElementById(anchor(id))?.scrollIntoView({ behavior: "smooth", block: "start" });
  const section = (id: string) => ({
    id: anchor(id),
    "data-spine-section": id,
    "data-done": String(spine.find((s) => s.id === id)?.done ?? true),
  });

  return (
    <div className={`card week-card ${progress.complete ? "is-complete" : ""}`} id={`week-${week.week}`} ref={cardRef}>
      {/* The whole header toggles the week — a button, so Tab and Enter do too (D3). */}
      <button type="button" className="week-head" aria-expanded={open} onClick={() => setOpen((o) => !o)}>
        <span className={`week-num ${progress.complete ? "complete" : ""}`}>
          {progress.complete ? <Icon name="check" size={14} label="Complete" /> : week.week}
        </span>
        <span className="week-head-text">
          <strong>
            Week {week.week} — {week.title}
          </strong>
          {week.optional && (
            <Badge className="week-optional" title="After the programme proper — it never counts toward your total or pace.">
              optional
            </Badge>
          )}
          <span className="week-goal">{week.goal}</span>
        </span>
        <span className="week-badges">
          {progress.conceptsTotal > 0 && (
            <Badge>
              {progress.conceptsDone}/{progress.conceptsTotal} chapters
            </Badge>
          )}
          <Badge>
            {progress.problemsSolved}/{progress.problemsTotal} problems
          </Badge>
          <Badge tone={progress.quizPassed ? "good" : "accent"}>
            {progress.score === null ? "quiz —" : `quiz ${progress.score}%`}
          </Badge>
          <Badge tone={progress.examPassed ? "good" : "accent"}>{progress.examPassed ? "final ✓" : "final —"}</Badge>
          <Icon name="chevronRight" size={14} className={`caret ${open ? "open" : ""}`} />
        </span>
      </button>

      <Bar percent={progress.percent} label={`Week ${week.week} progress`} />

      {open && (
        <div className="week-body">
          {/* X-60: the week as a checklist, in the order it is worked. */}
          <nav className="week-spine" aria-label={`Week ${week.week} checklist`}>
            {spine.map((s) => (
              <button
                key={s.id}
                className={`week-spine-item ${s.done ? "done" : ""}`}
                onClick={() => go(s.id)}
                title={s.gate ? "Part of the week's gate" : "Optional"}
              >
                <Icon name={s.done && s.id !== "notes" ? "check" : s.icon} size={14} />
                <span className="week-spine-label">{s.label}</span>
                <span className="week-spine-detail">{s.detail}</span>
                {s.gate && !s.done && <span className="week-spine-gate">gate</span>}
              </button>
            ))}
            <p className="dim week-spine-keys">
              <kbd>j</kbd>/<kbd>k</kbd> move · <kbd>n</kbd> next unfinished · <kbd>h</kbd> hint
            </p>
          </nav>

          <div className="week-content">
            {week.week <= 8 && track.key === "typescript" && (
              <label className="dim quiz-note mastery-toggle-row">
                <input
                  type="checkbox"
                  checked={predictFirst}
                  onChange={(e) => saveSetting(predictKey, e.target.checked ? "1" : "0")}
                />
                Predict first — before each run of a practice exercise or problem, write what it will print
                {predictionLog().length > 0 && ` (${predictionLog().length} learning moments logged)`}
              </label>
            )}
            <p className={`dim quiz-note mastery-line ${budget.over ? "is-bad" : ""}`}>
              <Icon name="clock" size={12} /> {budget.text}
              {budget.over && " — more than twice the plan. Worth asking what slowed you down."}
              {retried && (
                <span className="dim">
                  {" "}
                  · most retried: <strong>{retried.title}</strong> ({retried.count} failed run
                  {retried.count === 1 ? "" : "s"})
                </span>
              )}
            </p>

            {weekTools(track.key, week.week).length > 0 && (
              <p className="dim quiz-note mastery-line">
                <Icon name="tools" size={12} /> Tools for this week:{" "}
                {weekTools(track.key, week.week).map((t, k) => (
                  <span key={t.label}>
                    {k > 0 && " · "}
                    <Link to={t.to} title={t.why}>
                      {t.label}
                    </Link>
                  </span>
                ))}
              </p>
            )}

            {(links.course.length > 0 || links.dsa.length > 0 || links.projects.length > 0) && (
              <p className="dim quiz-note mastery-line">
                <Icon name="external" size={12} /> Elsewhere in the app:{" "}
                {links.course.map((n, k) => (
                  <span key={`c${n}`}>
                    {k > 0 && " · "}
                    <Link to={`/course/${n}`}>
                      TypeScript course week {n}
                      {done.has(`ts-course:w${n}`) ? " ✓" : ""}
                    </Link>
                  </span>
                ))}
                {links.dsa.map((key) => (
                  <span key={`d${key}`}>
                    {" · "}
                    <Link to={`/library/unit/${key}`}>DSA: {prettyKey(key)}</Link>
                  </span>
                ))}
                {links.projects.map((p) => (
                  <span key={p.to}>
                    {" · "}
                    <Link to={p.to}>{p.label}</Link>
                  </span>
                ))}
              </p>
            )}

            {strictStep && (
              <div className="card strict-step">
                <strong>From this week on, the compiler is stricter.</strong> Every final, project and exercise is
                checked with <code>noUncheckedIndexedAccess</code>: reading <code>xs[i]</code> or{" "}
                <code>record[key]</code> gives <code>T | undefined</code> until you deal with the missing case.{" "}
                <Link to="/playground/ts">Try the flag in the playground</Link>.
              </div>
            )}

            {week.concepts.length > 0 && (
              <section {...section("read")}>
                <div className="io-label">
                  <Icon name="learn" size={13} /> Chapters to study
                </div>
                <ul className="mastery-items">
                  {week.concepts.map((key) => {
                    const c = conceptByKey.get(key);
                    const isDone = done.has(key);
                    return (
                      <li key={key} className={`card mastery-item ${isDone ? "is-done" : ""}`}>
                        <span className="mastery-item-head">
                          {/* Stretched over the card: the whole card opens the
                              chapter, and it is still one real link (D3). */}
                          <Link className="stretched-link" to={`/learn/${key}`}>
                            {isDone && <Icon name="done" size={14} label="Done" className="is-good" />}
                            <strong>{c?.name ?? key}</strong>
                          </Link>
                          <Button
                            variant="ghost"
                            size="sm"
                            className={`above-stretch ${isDone ? "is-good" : ""}`}
                            aria-pressed={isDone}
                            onClick={() => onToggleChapter(key)}
                          >
                            {isDone ? "Done" : "Mark done"}
                          </Button>
                        </span>
                        {c?.what && <span className="mastery-item-what">{c.what}</span>}
                      </li>
                    );
                  })}
                </ul>
              </section>
            )}

            {practice.length + warmup.length > 0 && (
              <section {...section("practice")}>
                {warmup.length > 0 && (
                  <details className="card mastery-practice">
                    <summary>
                      <strong>Warm-up from earlier weeks</strong>{" "}
                      <span className="dim quiz-note">
                        {warmupSolved}/{warmup.length} solved · from earlier weeks, plus anything you failed
                        twice and have not solved yet — interleaving is what makes it stick
                      </span>
                    </summary>
                    <ExerciseSections
                      exercises={warmup}
                      onSolved={(id) => setSolvedEx(new Set(markMasterySolved(id)))}
                    />
                  </details>
                )}
                {practice.length > 0 && (
                  <details className="card mastery-practice">
                    <summary>
                      <strong>Practice</strong>{" "}
                      <span className="dim quiz-note">
                        {practiceSolved}/{practice.length} solved · optional — not part of the week's gate
                      </span>
                    </summary>
                    <p className="dim quiz-note">
                      Short, judged exercises on this week's ideas — reading an inference, reading a real
                      compiler error, repairing code that runs wrong, and on the type-level weeks, writing types
                      the compiler checks.
                    </p>
                    <ExerciseSections
                      exercises={practice}
                      onSolved={(id) => setSolvedEx(new Set(markMasterySolved(id)))}
                      predictFirst={predictFirst}
                      collapsible
                      solved={solvedEx}
                    />
                  </details>
                )}
              </section>
            )}

            {week.problems.length + problemSet.length > 0 && (
              <section {...section("problems")}>
                {week.problems.length > 0 && (
                  <>
                    <div className="io-label">
                      <Icon name="target" size={13} /> Problems to solve
                    </div>
                    <ul className="mastery-items">
                      {week.problems.map((ref) => {
                        const p = problemBySlug.get(ref.slug);
                        if (!p) return null;
                        const solved = p.solved_status === "solved";
                        return (
                          <li key={ref.slug} className={`card mastery-item ${solved ? "is-done" : ""}`}>
                            <span className="mastery-item-head">
                              <Link className="stretched-link" to={`/solve/${p.id}`}>
                                {solved && <Icon name="done" size={14} label="Solved" className="is-good" />}
                                <strong>{p.title}</strong>
                              </Link>
                              <DiffBadge d={p.difficulty} />
                            </span>
                            {ref.note && <span className="mastery-item-what">{ref.note}</span>}
                          </li>
                        );
                      })}
                    </ul>
                  </>
                )}

                {problemSet.length > 0 && (
                  <details className="card mastery-practice">
                    <summary>
                      <strong>Problem set</strong>{" "}
                      <span className="dim quiz-note">
                        {setSolved}/{problemSet.length} solved · warm-up, core and stretch · optional —
                        not part of the week's gate
                      </span>
                    </summary>
                    <p className="dim quiz-note">
                      Original problems on exactly this week&rsquo;s ideas, written for TypeScript and
                      judged at this week&rsquo;s strictness. Easy is a warm-up, Medium is the core of
                      the week, Hard is a stretch.
                    </p>
                    <ExerciseSections
                      exercises={problemSet}
                      onSolved={(id) => setSolvedEx(new Set(markMasterySolved(id)))}
                      overrides={{ challenge: { heading: "Problems" } }}
                      collapsible
                      solved={solvedEx}
                      predictFirst={predictFirst}
                    />
                  </details>
                )}
              </section>
            )}

            {(week.project || week.contest || week.arc_project) && (
              <section {...section("project")}>
                {week.project && (
                  <ProjectPanel
                    workspaceId={`${track.key}-w${week.week}`}
                    brief={week.project}
                    spec={week.project_spec ?? null}
                    row={row}
                    language={track.exam_language}
                    onSave={(notes, code, done) =>
                      api
                        .masterySaveProject(track.key, week.week, notes, code, done)
                        .then(onChanged)
                    }
                    onRubric={(ticked) => api.masterySaveRubric(track.key, week.week, ticked)}
                  />
                )}

                {week.arc_project && (
                  <>
                    <div className="io-label">
                      <Icon name="layers" size={13} /> The arc project — one ledger that grows all programme
                    </div>
                    <ProjectPanel
                      workspaceId={`${track.key}-w${week.week}-arc`}
                      brief={week.arc_project.goal}
                      spec={week.arc_project}
                      row={arcRow(row, track.key, week.week, arc)}
                      language={track.exam_language}
                      onSave={async (notes, code, shipped) =>
                        saveSetting(arcKey, JSON.stringify({ ...arc, notes, code, done: shipped }))
                      }
                      onRubric={async (ticked) => saveSetting(arcKey, JSON.stringify({ ...arc, rubric: ticked }))}
                    />
                  </>
                )}

                {week.contest && (
                  <div className="card mastery-checkpoint">
                    <div className="row wrap">
                      <div>
                        <strong>
                          <Icon name="timer" size={14} /> {week.contest.title}
                        </strong>
                        <div className="dim quiz-note">
                          {Math.round(week.contest.duration_seconds / 60)} minutes ·{" "}
                          {(week.contest.slugs?.length ?? 0) > 0
                            ? `${week.contest.slugs!.length} problems from across the month`
                            : `this week's ${week.problems.length} problems`}{" "}
                          · optional, timed, and retakeable
                        </div>
                      </div>
                      <span className="spacer" />
                      <Button
                        variant="primary"
                        icon="timer"
                        onClick={async () => {
                          try {
                            const id = await api.masteryStartContest(track.key, week.week);
                            nav(`/contest/${id}`);
                          } catch (e) {
                            toast.error("Could not start the checkpoint", { detail: String(e) });
                          }
                        }}
                      >
                        Start the checkpoint
                      </Button>
                    </div>
                    <details className="mastery-sub">
                      <summary className="quiz-note">The checkpoint quiz — 20 questions from the whole month</summary>
                      <MixedQuiz
                        weeks={monthWeeks}
                        size={20}
                        source={`${track.title} · ${week.contest.title}`}
                        startLabel="Draw a 20-question paper"
                      />
                    </details>
                    {monthPuzzles.length > 0 && (
                      <details className="mastery-sub">
                        <summary className="quiz-note">
                          The type-challenge section — {monthPuzzles.length} puzzles from the month
                        </summary>
                        <ExerciseSections
                          exercises={monthPuzzles}
                          onSolved={(id) => setSolvedEx(new Set(markMasterySolved(id)))}
                        />
                      </details>
                    )}
                  </div>
                )}
              </section>
            )}

            <CapstonePractice week={week} trackKey={track.key} />

            {(week.flashcards?.length ?? 0) > 0 && (
              <p className="dim quiz-note mastery-line">
                <Icon name="layers" size={12} />{" "}
                {progress.complete ? (
                  <>
                    This week's {week.flashcards!.length} review cards are in{" "}
                    <Link to="/flashcards">Flashcards</Link>.
                  </>
                ) : (
                  <>{week.flashcards!.length} review cards join your Flashcards when you finish this week.</>
                )}
              </p>
            )}

            <section {...section("quiz")}>
              <QuizPanel
                week={week}
                track={track}
                best={progress.score}
                onSubmit={(percent) =>
                  api.masteryRecordQuiz(track.key, week.week, percent).then(onChanged)
                }
              />
            </section>

            {week.exam && (
              <section {...section("final")}>
                <ExamPanel
                  versions={[week.exam, ...(week.exam_alternates ?? [])]}
                  variantKey={`mastery-final-variant:${track.key}:${week.week}`}
                  weekNumber={week.week}
                  passed={progress.examPassed}
                  savedCode={row?.exam_code ?? ""}
                  typesSolved={!!week.exam.types && solvedEx.has(week.exam.types.id)}
                  onTypesSolved={(id) => setSolvedEx(new Set(markMasterySolved(id)))}
                  onResult={(passed, code) =>
                    api.masteryRecordExam(track.key, week.week, passed, code).then(onChanged)
                  }
                />
              </section>
            )}

            <section {...section("notes")} className="mastery-notes">
              <label className="io-label" htmlFor={`notes-${week.week}`}>
                <Icon name="notes" size={13} /> Your notes for this week
              </label>
              <textarea
                id={`notes-${week.week}`}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                onBlur={() => {
                  if (notes !== (settings[notesKey] ?? "")) saveSetting(notesKey, notes);
                }}
                placeholder="What clicked, what didn't, what to revisit. Saved with your backups."
                className="mastery-notes-text"
              />
            </section>
          </div>
        </div>
      )}
    </div>
  );
}

type ArcState = { notes: string; code: string; done: boolean; rubric: number[] };

function parseArc(raw: string | undefined): ArcState {
  try {
    const v = JSON.parse(raw || "{}") as Partial<ArcState>;
    return {
      notes: typeof v.notes === "string" ? v.notes : "",
      code: typeof v.code === "string" ? v.code : "",
      done: v.done === true,
      rubric: Array.isArray(v.rubric) ? v.rubric.filter((x): x is number => typeof x === "number") : [],
    };
  } catch {
    return { notes: "", code: "", done: false, rubric: [] };
  }
}

/** The arc project's state, shaped like a progress row for ProjectPanel. */
function arcRow(row: MasteryProgress | undefined, trackKey: string, week: number, arc: ArcState): MasteryProgress {
  return {
    track_key: trackKey,
    week,
    best_quiz: row?.best_quiz ?? -1,
    exam_passed: row?.exam_passed ?? false,
    exam_code: "",
    project_notes: arc.notes,
    project_code: arc.code,
    project_done: arc.done,
    study_seconds: 0,
    started_at: null,
    completed_at: null,
    project_rubric: JSON.stringify(arc.rubric),
  };
}

type ProjectVersion = { at: string; code: string };

function parseHistory(raw: string | undefined): ProjectVersion[] {
  try {
    const v: unknown = JSON.parse(raw || "[]");
    return Array.isArray(v)
      ? v.filter(
          (x): x is ProjectVersion =>
            typeof x === "object" && x !== null && typeof (x as ProjectVersion).at === "string" && typeof (x as ProjectVersion).code === "string"
        )
      : [];
  } catch {
    return [];
  }
}

/** Rubric ticks are stored as a JSON array of item indices. */
function parseTicks(raw: string | undefined): Set<number> {
  try {
    const v: unknown = JSON.parse(raw || "[]");
    return new Set(Array.isArray(v) ? v.filter((x): x is number => typeof x === "number") : []);
  } catch {
    return new Set();
  }
}

/** The week's build project. With a `spec` it is a structured brief whose
 * acceptance tests run through the judge, and "shipped" needs them green; the
 * reference implementation opens only after shipping (TS_MASTERY_ROADMAP
 * X-40 to X-43). Without one it is the older free-form brief. */
function ProjectPanel({
  workspaceId,
  brief,
  spec,
  row,
  language,
  onSave,
  onRubric,
}: {
  workspaceId: string;
  brief: string;
  spec: MasteryProjectSpec | null;
  row: MasteryProgress | undefined;
  language: string;
  onSave: (notes: string, code: string, done: boolean) => Promise<void>;
  onRubric: (ticked: number[]) => Promise<void>;
}) {
  const [notes, setNotes] = useState(row?.project_notes ?? "");
  const [code, setCode] = useState(row?.project_code || spec?.starter || "");
  const [shipped, setShipped] = useState(row?.project_done ?? false);
  const [saving, setSaving] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState(false);
  const [runErr, setRunErr] = useState("");
  const [showReference, setShowReference] = useState(false);
  const [ticked, setTicked] = useState<Set<number>>(() => parseTicks(row?.project_rubric));
  const toast = useToast();
  const green = report?.status === "accepted";
  // With acceptance tests, shipping means they pass. Un-shipping is always allowed.
  const canShip = shipped || !spec || green;

  // X-46: every save keeps a version (up to 20), in settings, so it is backed up.
  const historyKey = `mastery-project-history:${workspaceId}`;
  const [history, setHistory] = useState<ProjectVersion[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [diffWith, setDiffWith] = useState<number | null>(null);
  useEffect(() => {
    api
      .getSettings()
      .then((s) => setHistory(parseHistory(s[historyKey])))
      .catch(loadFailed("your saved versions"));
  }, [historyKey]);

  function keepVersion(text: string) {
    if (!text.trim() || history[0]?.code === text) return;
    const next = [{ at: new Date().toISOString(), code: text }, ...history].slice(0, 20);
    setHistory(next);
    api.setSetting(historyKey, JSON.stringify(next)).catch(saveFailed("the version history"));
  }

  async function save(nextShipped = shipped) {
    setSaving(true);
    try {
      await onSave(notes, code, nextShipped);
      keepVersion(code);
      setShipped(nextShipped);
      toast(nextShipped && !shipped ? "Project shipped" : "Project saved");
    } finally {
      setSaving(false);
    }
  }

  async function runTests() {
    if (!spec) return;
    setRunning(true);
    setRunErr("");
    setReport(null);
    const cases: TestCase[] = spec.tests.map((t, i) => ({
      id: 0,
      problem_id: 0,
      kind: "hidden",
      name: `Acceptance test ${i + 1}`,
      input: t.input,
      expected_output: t.output,
      ordering: i,
    }));
    try {
      const r = await api.runTests(null, spec.language, code, cases, {
        strictness: spec.strictness,
      });
      setReport(r);
      await onSave(notes, code, shipped);
    } catch (e) {
      setRunErr(String(e));
    } finally {
      setRunning(false);
    }
  }

  function toggleTick(i: number) {
    const next = new Set(ticked);
    if (next.has(i)) next.delete(i);
    else next.add(i);
    setTicked(next);
    onRubric([...next].sort((a, b) => a - b)).catch(() => toast("Could not save the checklist"));
  }

  return (
    <div
      className="card"
      style={{
        marginBottom: 14,
        background: "var(--accent-dim)",
        borderColor: shipped ? "var(--good)" : "var(--accent)",
      }}
    >
      <div className="row justify-between items-start">
        <div className="io-label" style={{ color: shipped ? "var(--good)" : "var(--accent)" }}>
          <Icon name="build" size={14} /> {spec ? `Build it: ${spec.title}` : "Build it yourself"} {shipped && "— shipped"}
        </div>
        <button
          className="ghost"
          style={{ padding: "2px 10px", fontSize: 12 }}
          onClick={() => setExpanded((e) => !e)}
        >
          {expanded ? "Hide workspace" : "Open workspace"}
        </button>
      </div>
      {spec ? (
        <>
          <Markdown>{spec.goal}</Markdown>
          <div className="io-label">Requirements</div>
          <ol className="mt-0">
            {spec.requirements.map((r, i) => (
              <li key={i}>
                <Markdown>{r}</Markdown>
              </li>
            ))}
          </ol>
          {spec.stretch.length > 0 && (
            <>
              <div className="io-label">Stretch (not tested)</div>
              <ul className="mt-0">
                {spec.stretch.map((r, i) => (
                  <li key={i}>
                    <Markdown>{r}</Markdown>
                  </li>
                ))}
              </ul>
            </>
          )}
          <p className="dim quiz-note mt-0">
            Done when all {spec.tests.length} acceptance tests pass — then mark it shipped.
          </p>
        </>
      ) : (
        <p style={{ margin: "0 0 10px" }}>{brief}</p>
      )}

      {expanded && (
        <>
          <div className="io-label">Notes</div>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="What you built, what surprised you, what you would do differently."
            style={{ width: "100%", minHeight: 90, marginBottom: 10 }}
          />
          <div className="io-label">Code</div>
          <div
            style={{
              height: spec ? 420 : 260,
              border: "1px solid var(--border)",
              borderRadius: 6,
              overflow: "hidden",
              marginBottom: 10,
            }}
          >
            <WorkspaceEditor
              workspaceId={workspaceId}
              language={language}
              value={code}
              onChange={setCode}
              onRun={spec ? runTests : undefined}
              tsStrictness={spec?.strictness}
            />
          </div>
          <div className="row gap-2 flex-wrap">
            {spec && (
              <button onClick={runTests} disabled={running}>
                {running ? "Running…" : `Run ${spec.tests.length} acceptance tests`}
              </button>
            )}
            <button className={spec ? "ghost" : undefined} onClick={() => save()} disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </button>
            <button
              className="ghost"
              style={shipped ? { borderColor: "var(--good)", color: "var(--good)" } : undefined}
              onClick={() => save(!shipped)}
              disabled={saving || !canShip}
              title={canShip ? undefined : "Run the acceptance tests — shipping needs them all green."}
            >
              {shipped ? "✓ Shipped — undo" : "Mark shipped"}
            </button>
            {spec && shipped && (
              <button className="ghost" onClick={() => setShowReference((s) => !s)}>
                {showReference ? "Hide reference" : "Reference implementation"}
              </button>
            )}
            {history.length > 0 && (
              <button className="ghost" onClick={() => setShowHistory((h) => !h)}>
                {showHistory ? "Hide history" : `History (${history.length})`}
              </button>
            )}
            {spec?.strictness === "strict+indexed" && (
              <span className="dim quiz-note">
                Checked with <code>noUncheckedIndexedAccess</code>
              </span>
            )}
          </div>

          {runErr && (
            <div className="card mt-2 mb-0 border-bad">
              <div className="io-label c-bad">Couldn&rsquo;t run</div>
              <pre className="m-0 pre-wrap text-xs">{runErr}</pre>
            </div>
          )}
          {report && (
            <ExamFeedback
              report={report}
              accepted={green}
              acceptedNote={
                shipped
                  ? "Still green."
                  : "Every acceptance test passes. Tick the self-review below, then mark it shipped."
              }
            />
          )}

          {spec && spec.rubric.length > 0 && (
            <div className="mt-3">
              <div className="io-label">Self-review</div>
              {spec.rubric.map((item, i) => (
                <label
                  key={i}
                  style={{ display: "flex", gap: 8, alignItems: "baseline", fontSize: 13, margin: "4px 0" }}
                >
                  <input type="checkbox" checked={ticked.has(i)} onChange={() => toggleTick(i)} />
                  <span>{inlineCode(item)}</span>
                </label>
              ))}
            </div>
          )}

          {showHistory && history.length > 0 && (
            <div className="card mt-2">
              <div className="io-label">Saved versions — newest first</div>
              {history.map((v, i) => (
                <div key={v.at} className="row" style={{ gap: 8, alignItems: "center", margin: "4px 0" }}>
                  <span className="quiz-note">{new Date(v.at).toLocaleString()}</span>
                  <span className="dim quiz-note">{v.code.split("\n").length} lines</span>
                  <button className="ghost" onClick={() => setDiffWith(diffWith === i ? null : i)}>
                    {diffWith === i ? "Hide diff" : "Diff with now"}
                  </button>
                  <button
                    className="ghost"
                    onClick={() => {
                      // Undo rather than a confirm: the code being replaced is
                      // kept for one click (E5).
                      const current = code;
                      setCode(v.code);
                      toast("Restored the saved version.", {
                        action: { label: "Undo", onClick: () => setCode(current) },
                      });
                    }}
                  >
                    Restore
                  </button>
                </div>
              ))}
              {diffWith !== null && history[diffWith] && (
                <DiffView before={history[diffWith]!.code} after={code} maxHeight={380} />
              )}
            </div>
          )}

          {showReference && spec && shipped && (
            <div className="mt-2">
              <p className="dim quiz-note">
                One way to meet the brief — compare it with yours rather than copying it. The diff shows what the
                reference does differently: <span className="c-bad">−</span> yours,{" "}
                <span className="c-good">+</span> the reference.
              </p>
              <DiffView before={code} after={spec.solution} maxHeight={420} />
              <details className="mt-2">
                <summary className="dim quiz-note">The reference on its own</summary>
                <Markdown>{"```" + spec.language + "\n" + spec.solution + "\n```"}</Markdown>
              </details>
            </div>
          )}
        </>
      )}
    </div>
  );
}


/** The multiple-choice half of the week's exam. Each sitting is a fresh draw
 * from the week's bank with the options shuffled. */
function QuizPanel({
  week,
  track,
  best,
  onSubmit,
}: {
  week: MasteryWeek;
  track: MasteryTrack;
  best: number | null;
  onSubmit: (percent: number) => Promise<void>;
}) {
  const [paper, setPaper] = useState<ExamQuestion[]>(() => drawExamPaper(week));
  const [picked, setPicked] = useState<number[]>(() => paper.map(() => -1));
  const [submitted, setSubmitted] = useState(false);
  /** How many misses were turned into flashcards this sitting, once saved. */
  const [savedMisses, setSavedMisses] = useState<number | null>(null);
  const [savingMisses, setSavingMisses] = useState(false);
  const toast = useToast();

  const answered = picked.filter((p) => p >= 0).length;
  const correct = picked.filter((p, i) => p === paper[i].answer).length;
  const percent = Math.round((correct / paper.length) * 100);
  const passedNow = submitted && percent >= track.pass_mark;
  const missed = submitted ? paper.filter((q, i) => picked[i] !== q.answer) : [];

  function submit() {
    setSubmitted(true);
    recordSitting(paper.map((q, i) => ({ question: q.question, right: picked[i] === q.answer })));
    onSubmit(percent).catch(saveFailed("your quiz score"));
  }

  function retake() {
    const next = drawExamPaper(week);
    setPaper(next);
    setPicked(next.map(() => -1));
    setSubmitted(false);
    setSavedMisses(null);
  }

  /** A wrong answer is the most useful card there is: it is exactly what you
   * do not know yet. Each miss becomes a card — question on the front, the
   * right answer and its explanation on the back — skipping any question
   * already in the deck, so a retake does not pile up duplicates. */
  async function saveMisses() {
    setSavingMisses(true);
    try {
      const existing = new Set((await api.listFlashcards()).map((c) => c.front));
      const source = `${track.title} · Week ${week.week} quiz`;
      let added = 0;
      for (const q of missed) {
        if (existing.has(questionText(q))) continue;
        await api.addFlashcard(questionText(q), `${answerText(q)}\n\n${q.explanation}`, source);
        existing.add(questionText(q));
        added++;
      }
      setSavedMisses(added);
    } catch {
      toast("Could not save those flashcards — try again");
    } finally {
      setSavingMisses(false);
    }
  }

  return (
    <div className="card mb-3">
      <div className="row justify-between items-center">
        <div className="io-label m-0">
          <Icon name="checklist" size={14} /> End-of-week quiz
        </div>
        <span className="dim text-xs">
          {paper.length} of {week.quiz.length} in the bank · {track.pass_mark}% to pass
          {best !== null && ` · best ${best}%`}
        </span>
      </div>

      {paper.map((q, qi) => (
        <QuizQuestionCard
          key={`${q.question}-${qi}`}
          index={qi + 1}
          question={q}
          picked={picked[qi]}
          revealed={submitted}
          onPick={(oi) =>
            setPicked((prev) => {
              if (submitted) return prev;
              const next = [...prev];
              next[qi] = oi;
              return next;
            })
          }
        />
      ))}

      {!submitted ? (
        <div className="row gap-2 items-center mt-2">
          <button onClick={submit} disabled={answered < paper.length}>
            Submit quiz
          </button>
          <span className="dim text-xs">
            {answered}/{paper.length} answered
            {answered < paper.length && " — answer every question first"}
          </span>
        </div>
      ) : (
        <div
          className="card"
          style={{
            marginTop: 10,
            marginBottom: 0,
            borderColor: passedNow ? "var(--good)" : "var(--bad)",
          }}
        >
          <div className="io-label" style={{ color: passedNow ? "var(--good)" : "var(--bad)" }}>
            {passedNow
              ? `Passed — ${correct}/${paper.length} (${percent}%)`
              : `Not yet — ${correct}/${paper.length} (${percent}%), ${track.pass_mark}% needed`}
          </div>
          <p style={{ margin: "0 0 10px" }}>
            {passedNow
              ? "Now clear the coding final below to unlock the next week."
              : "Read the explanations, revisit the chapters, and take a fresh paper — only your best score counts."}
          </p>
          <div className="row quiz-actions">
            <button className="ghost" onClick={retake}>
              Draw a new paper
            </button>
            {missed.length > 0 && savedMisses === null && (
              <button className="ghost" onClick={saveMisses} disabled={savingMisses}>
                {savingMisses
                  ? "Saving…"
                  : `Save ${missed.length} missed ${missed.length === 1 ? "question" : "questions"} as flashcards`}
              </button>
            )}
            {savedMisses !== null && (
              <span className="dim quiz-note">
                {savedMisses === 0
                  ? "Those questions are already in your flashcards."
                  : `Added ${savedMisses} ${savedMisses === 1 ? "card" : "cards"} to your review queue.`}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function QuizQuestionCard({
  index,
  question,
  picked,
  revealed,
  onPick,
}: {
  index: number;
  question: ExamQuestion;
  picked: number;
  revealed: boolean;
  onPick: (optionIndex: number) => void;
}) {
  return (
    <QuizCard
      index={index}
      question={inlineCode(question.question)}
      revealed={revealed}
      right={picked === question.answer}
      explanation={question.explanation}
    >
      <QuizChoices question={question} picked={picked} revealed={revealed} onPick={onPick} />
    </QuizCard>
  );
}

/** The week's coding final — the half of the gate a quiz cannot test. Judged by
 * the same runner as the Learn challenges.
 *
 * Weeks 15-22 have two-part finals (X-34): a type-graded half that must be
 * solved as well as the runtime tests. Tests past `visible_tests` are a hidden
 * set (X-32). After a failed attempt the learner can switch to an alternate
 * version of the final (X-33); the choice is remembered in settings, and
 * passing any version passes the week. */
function ExamPanel({
  versions,
  variantKey,
  weekNumber,
  passed,
  savedCode,
  typesSolved,
  onTypesSolved,
  onResult,
}: {
  versions: MasteryExam[];
  variantKey: string;
  weekNumber: number;
  passed: boolean;
  savedCode: string;
  typesSolved: boolean;
  onTypesSolved: (id: string) => void;
  onResult: (passed: boolean, code: string) => Promise<void>;
}) {
  const [variant, setVariant] = useState(0);
  const exam = versions[Math.min(variant, versions.length - 1)];
  const [code, setCode] = useState(savedCode || exam.starter);
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState("");
  const [showHint, setShowHint] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  const [failedOnce, setFailedOnce] = useState(false);
  const types = versions[0].types ?? null;
  // X-71: focus mode hides the app's chrome and runs a clock; a pass in focus
  // mode records how long it took.
  const [focusStart, setFocusStart] = useState<number | null>(null);
  const [, setTick] = useState(0);
  const [focusResult, setFocusResult] = useState<string>("");

  useEffect(() => {
    if (focusStart === null) return;
    document.body.classList.add("focus-mode");
    const t = setInterval(() => setTick((n) => n + 1), 1000);
    return () => {
      clearInterval(t);
      document.body.classList.remove("focus-mode");
    };
  }, [focusStart]);
  const focusSeconds = focusStart === null ? 0 : Math.floor((Date.now() - focusStart) / 1000);

  // Which version is in use survives a restart; an unknown value means the main one.
  useEffect(() => {
    if (versions.length < 2) return;
    api
      .getSettings()
      .then((s) => {
        const v = Number(s[variantKey] ?? "0");
        if (Number.isInteger(v) && v > 0 && v < versions.length) {
          setVariant(v);
          if (!savedCode) setCode(versions[v].starter);
        }
      })
      .catch(loadFailed("your exam version"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [variantKey, versions.length]);

  function switchVersion() {
    const next = (variant + 1) % versions.length;
    setVariant(next);
    setCode(versions[next].starter);
    setReport(null);
    setShowHint(false);
    setFailedOnce(false);
    api.setSetting(variantKey, String(next)).catch(saveFailed("your exam version"));
  }

  async function submit() {
    setRunning(true);
    setErr("");
    setReport(null);
    const visible = exam.visible_tests || exam.tests.length;
    const cases: TestCase[] = exam.tests.map((t, i) => ({
      id: 0,
      problem_id: 0,
      kind: "hidden",
      name: i < visible ? `Test ${i + 1}` : `Hidden test ${i + 1 - visible}`,
      input: t.input,
      expected_output: t.output,
      ordering: i,
    }));
    try {
      const r = await api.runTests(null, exam.language, code, cases, {
        strictness: exam.strictness,
      });
      setReport(r);
      const green = r.status === "accepted";
      if (!green) setFailedOnce(true);
      if (green && focusStart !== null) {
        const secs = Math.round((Date.now() - focusStart) / 1000);
        const text = `${Math.floor(secs / 60)}m ${String(secs % 60).padStart(2, "0")}s`;
        setFocusResult(text);
        api.setSetting(`${variantKey}:focus-time`, String(secs)).catch(saveFailed("focus time"));
        setFocusStart(null);
      }
      await onResult(green && (!types || typesSolved), code);
    } catch (e) {
      setErr(String(e));
    } finally {
      setRunning(false);
    }
  }

  const accepted = report?.status === "accepted";
  const untouched = code.includes("____");

  // Solving the type half after the runtime half is already green completes
  // the final there and then.
  function typesDone(id: string) {
    onTypesSolved(id);
    if (accepted) onResult(true, code).catch(saveFailed("your exam result"));
  }

  return (
    <div
      className="card"
      style={{ marginBottom: 0, borderColor: passed ? "var(--good)" : "var(--accent)" }}
    >
      <div className="row justify-between items-center">
        <div className="io-label" style={{ margin: 0, color: passed ? "var(--good)" : "var(--accent)" }}>
          <Icon name="playground" size={14} /> Coding final — {exam.title} {passed && "✓"}
        </div>
        <span className="row gap-1">
          {versions.length > 1 && (
            <span className="badge" title="Alternate versions are offered after a failed attempt.">
              version {variant + 1} of {versions.length}
            </span>
          )}
          <span className="badge">{exam.language}</span>
        </span>
      </div>

      {types && (
        <>
          <p className="dim quiz-note" style={{ margin: "6px 0 0" }}>
            A two-part final: the type half and the runtime half must both pass.{" "}
            {typesSolved ? "✓ Part 1 is done." : "Part 1 is still open."}
          </p>
          <ExerciseSections
            exercises={[types]}
            onSolved={typesDone}
            overrides={{
              typelevel: {
                heading: "Part 1 — types",
                blurb:
                  "Nothing runs: hidden `Expect<Equal<…>>` claims about your type must all compile.",
              },
            }}
          />
          <H className="unit-subtitle">Part 2 — runtime</H>
        </>
      )}
      <p style={{ margin: "6px 0 10px" }}>{exam.prompt}</p>

      <div
        style={{
          height: 340,
          border: "1px solid var(--border)",
          borderRadius: 6,
          overflow: "hidden",
        }}
      >
        <CodeEditor
          language={exam.language}
          value={code}
          onChange={setCode}
          onRun={submit}
          tsStrictness={exam.strictness}
        />
      </div>

      <div className="row mt-2 flex-wrap gap-2">
        <button onClick={submit} disabled={running}>
          {running ? "Judging…" : "Submit final"}
        </button>
        <button className="ghost" onClick={() => setCode(exam.starter)} disabled={running}>
          Reset
        </button>
        {exam.hint && (
          <button className="ghost" onClick={() => setShowHint((s) => !s)}>
            {showHint ? "Hide hint" : "Hint"}
          </button>
        )}
        {passed && (
          <button className="ghost" onClick={() => setShowSolution((s) => !s)}>
            {showSolution ? "Hide reference solution" : "Reference solution"}
          </button>
        )}
        <button
          className="ghost"
          onClick={() => setFocusStart((f) => (f === null ? Date.now() : null))}
          title="Hide the sidebar and top bar, and time yourself. Nothing is gated on the time."
        >
          {focusStart === null
            ? "Focus mode"
            : `${Math.floor(focusSeconds / 60)}:${String(focusSeconds % 60).padStart(2, "0")} · leave focus`}
        </button>
        {focusResult && <span className="dim quiz-note">Passed in focus mode in {focusResult}.</span>}
        {versions.length > 1 && !passed && failedOnce && (
          <button
            className="ghost"
            onClick={switchVersion}
            title="A different problem on the same ideas — so a retake tests the ideas, not your memory of the tests."
          >
            Retake with a different version
          </button>
        )}
        {untouched && !running && (
          <span className="dim" style={{ fontSize: 12, alignSelf: "center" }}>
            Replace the <code>____</code> before submitting.
          </span>
        )}
        {exam.strictness === "strict+indexed" && (
          <span className="dim quiz-note" title="Every a[i] and record[key] read is typed T | undefined until you handle the missing case.">
            Checked with <code>noUncheckedIndexedAccess</code>
          </span>
        )}
      </div>

      {showHint && exam.hint && (
        <div className="card mt-2 mb-0 bg-accent-dim">
          <div className="io-label c-accent">Hint</div>
          <p className="m-0">{exam.hint}</p>
        </div>
      )}

      {err && (
        <div className="card mt-2 mb-0 border-bad">
          <div className="io-label c-bad">Couldn&rsquo;t run</div>
          <pre className="m-0 pre-wrap text-xs">{err}</pre>
        </div>
      )}

      {report && (
        <ExamFeedback
          report={report}
          weekNumber={weekNumber}
          accepted={accepted}
          acceptedNote={
            types && !typesSolved
              ? "Every runtime test passes. Solve Part 1 — the type half — to finish the final."
              : undefined
          }
        />
      )}

      {showSolution && passed && (
        <div className="mt-2">
          <Markdown>{"```" + exam.language + "\n" + exam.solution + "\n```"}</Markdown>
          {types && <Markdown>{"```ts\n" + types.solution + "```"}</Markdown>}
        </div>
      )}
    </div>
  );
}

/** A judge report for the coding final — or, with `acceptedNote`, for a
 * project's acceptance tests, which say something different on a pass. */
function ExamFeedback({
  report,
  weekNumber = 0,
  accepted,
  acceptedNote,
}: {
  report: JudgeReport;
  weekNumber?: number;
  accepted: boolean;
  acceptedNote?: string;
}) {
  if (report.status === "not_installed") {
    return (
      <div className="card mt-2 mb-0 border-bad">
        <div className="io-label c-bad">Toolchain missing</div>
        <p className="m-0">
          {report.not_installed_hint || "Install the language toolchain to run this final."}
        </p>
      </div>
    );
  }

  if (report.compile_error) {
    return (
      <div className="card mt-2 mb-0 border-bad">
        <div className="io-label c-bad">Compile error</div>
        <pre className="m-0 pre-wrap text-xs">{report.compile_error}</pre>
        <TsErrorLinks text={report.compile_error} />
      </div>
    );
  }

  const failing = report.results.filter((r) => !r.passed);
  return (
    <div
      className="card"
      style={{ marginTop: 10, marginBottom: 0, borderColor: accepted ? "var(--good)" : "var(--bad)" }}
    >
      <div className="io-label" style={{ color: accepted ? "var(--good)" : "var(--bad)" }}>
        {accepted
          ? `Accepted — all ${report.total} tests passed 🎉`
          : `${report.passed} / ${report.total} tests passed`}
      </div>
      {accepted ? (
        <p className="m-0">
          {acceptedNote ?? (
            <>
              Week {weekNumber}&rsquo;s coding final is done. With the quiz passed and every
              chapter marked, the next week unlocks.
            </>
          )}
        </p>
      ) : (
        <FailingCases failing={failing} />
      )}
    </div>
  );
}
