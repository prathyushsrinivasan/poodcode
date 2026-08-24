import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type {
  Concept,
  JudgeReport,
  MasteryExam,
  MasteryProgress,
  MasteryTrack,
  MasteryWeek,
  Problem,
  TestCase,
} from "../types";
import { Markdown } from "../components/Markdown";
import { CodeEditor } from "../components/CodeEditor";
import { DiffBadge, Empty } from "../components/common";
import { Section, useCollapse } from "../components/Collapsible";
import { loadDoneChapters, setChapterDone } from "../lib/learnProgress";
import { useToast } from "../components/Toast";
import {
  drawExamPaper,
  formatStudyTime,
  migrateLegacyQuizScores,
  pacing,
  progressByWeek,
  startDateKey,
  unlockedWeeks,
  weekProgress,
  type ExamQuestion,
  type ProgressMap,
  type WeekProgress,
} from "../lib/mastery";

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
  const toast = useToast();

  const refreshProgress = useCallback(async () => {
    setRows(await api.masteryProgress());
  }, []);

  useEffect(() => {
    // Exam scores used to live in localStorage; fold any leftovers into SQLite
    // before the first read so nothing looks lost on upgrade.
    migrateLegacyQuizScores()
      .catch(() => {})
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
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const track = useMemo(
    () => tracks.find((t) => t.key === trackKey) ?? tracks[0],
    [tracks, trackKey]
  );

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

  const phaseFold = useCollapse(`mastery-phase:${track?.key ?? ""}`);

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
          toast(`Week ${w.week} complete — its chapters are now in your review queue`);
        }
      }
      await refreshProgress();
    })().catch(() => {});
  }, [track, perWeek, progress, refreshProgress, toast]);

  if (loading) return <div className="page">Loading…</div>;
  if (!track) {
    return (
      <div className="page">
        <Empty icon="🎓" text="No mastery track is bundled." />
      </div>
    );
  }

  const completedWeeks = perWeek.filter((p) => p.complete).length;
  const currentWeek =
    track.weeks.find((w) => unlocked.has(w.week) && !perWeek[w.week - 1].complete)?.week ??
    track.weeks.length;
  const totalStudy = perWeek.reduce((sum, p) => sum + p.studySeconds, 0);
  const startedRaw = settings[startDateKey(track.key)];
  const pace = startedRaw
    ? pacing(new Date(startedRaw), currentWeek, track.weeks.length)
    : null;
  const finished = completedWeeks === track.weeks.length;

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
      <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
        <h1 className="page-title">🎓 {track.title}</h1>
        {tracks.length > 1 && (
          <div className="row" style={{ gap: 6 }}>
            {tracks.map((t) => (
              <button
                key={t.key}
                className={t.key === track.key ? "" : "ghost"}
                onClick={() => pickTrack(t.key)}
              >
                {t.title}
              </button>
            ))}
          </div>
        )}
      </div>
      <p className="page-sub">{track.subtitle}</p>

      <div className="card" style={{ marginBottom: 18 }}>
        <p style={{ marginTop: 0 }}>{track.intro}</p>
        <div className="row" style={{ gap: 22, flexWrap: "wrap", marginTop: 12 }}>
          <span>
            <strong style={{ fontSize: 22 }}>{completedWeeks}</strong>
            <span className="dim"> / {track.weeks.length} weeks done</span>
          </span>
          <span>
            <strong style={{ fontSize: 22 }}>{currentWeek}</strong>
            <span className="dim"> current week</span>
          </span>
          <span>
            <strong style={{ fontSize: 22 }}>{formatStudyTime(totalStudy)}</strong>
            <span className="dim"> studied here</span>
          </span>
          <span>
            <strong style={{ fontSize: 22 }}>{track.pass_mark}%</strong>
            <span className="dim"> pass mark</span>
          </span>
        </div>
        <Bar percent={Math.round((completedWeeks / track.weeks.length) * 100)} />

        {pace ? (
          <p className="dim" style={{ margin: "12px 0 0", fontSize: 13 }}>
            Started {new Date(startedRaw!).toLocaleDateString()} · the calendar says{" "}
            <strong>Week {pace.scheduledWeek}</strong> ·{" "}
            {pace.weeksBehind > 0 ? (
              <span style={{ color: "var(--bad)" }}>
                {pace.weeksBehind} week{pace.weeksBehind > 1 ? "s" : ""} behind
              </span>
            ) : pace.weeksBehind < 0 ? (
              <span style={{ color: "var(--good)" }}>
                {-pace.weeksBehind} week{pace.weeksBehind < -1 ? "s" : ""} ahead
              </span>
            ) : (
              <span style={{ color: "var(--good)" }}>on track</span>
            )}
            {!finished && (
              <> · at this pace you finish {pace.projectedFinish.toLocaleDateString()}</>
            )}
          </p>
        ) : (
          <div className="row" style={{ marginTop: 12, gap: 10, alignItems: "center" }}>
            <button onClick={beginTrack}>Start the programme</button>
            <span className="dim" style={{ fontSize: 12 }}>
              Sets today as week 1 so pacing and a finish date can be tracked.
            </span>
          </div>
        )}
      </div>

      {finished && <CompletionSummary track={track} perWeek={perWeek} totalStudy={totalStudy} />}

      {phases.map(([phase, weeks]) => {
        const doneHere = weeks.filter((w) => perWeek[w.week - 1].complete).length;
        return (
          <Section
            key={phase}
            title={phase}
            open={phaseFold.isOpen(phase)}
            onToggle={() => phaseFold.toggle(phase)}
            meta={
              <span
                className="dim"
                style={{ fontSize: 12, color: doneHere === weeks.length ? "var(--good)" : undefined }}
              >
                {doneHere}/{weeks.length} weeks
              </span>
            }
          >
            {weeks.map((w) => (
              <WeekCard
                key={w.week}
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
              />
            ))}
          </Section>
        );
      })}
    </div>
  );
}

function Bar({ percent }: { percent: number }) {
  return (
    <div className="progress-track" title={`${percent}%`}>
      <div
        className="progress-fill"
        style={{
          width: `${percent}%`,
          background: percent === 100 ? "var(--good)" : "var(--accent)",
        }}
      />
    </div>
  );
}

function CompletionSummary({
  track,
  perWeek,
  totalStudy,
}: {
  track: MasteryTrack;
  perWeek: WeekProgress[];
  totalStudy: number;
}) {
  const scores = perWeek.map((p) => p.score ?? 0);
  const avg = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  const problems = perWeek.reduce((s, p) => s + p.problemsSolved, 0);
  const projects = perWeek.filter((p) => p.projectDone).length;
  return (
    <div className="card" style={{ marginBottom: 18, borderColor: "var(--good)" }}>
      <div className="io-label" style={{ color: "var(--good)" }}>
        🏁 Programme complete
      </div>
      <p style={{ marginTop: 0 }}>
        Every week of <strong>{track.title}</strong> is finished — all{" "}
        {track.weeks.length} chapters sets studied, both exams passed each week.
      </p>
      <div className="grid cols-4">
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="stat-value">{track.weeks.length}</div>
          <div className="stat-label">weeks completed</div>
        </div>
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="stat-value">{avg}%</div>
          <div className="stat-label">average exam score</div>
        </div>
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="stat-value">{problems}</div>
          <div className="stat-label">curated problems solved</div>
        </div>
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="stat-value">{formatStudyTime(totalStudy)}</div>
          <div className="stat-label">time invested · {projects} projects shipped</div>
        </div>
      </div>
    </div>
  );
}

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
}) {
  const nav = useNavigate();
  const toast = useToast();
  const [open, setOpen] = useState(!locked && !progress.complete);

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
      if (seconds > 0) api.masteryLogTime(track.key, week.week, seconds).catch(() => {});
    };
    const timer = setInterval(flush, TIME_FLUSH_MS);
    return () => {
      clearInterval(timer);
      flush();
      opened.current = null;
    };
  }, [locked, open, track.key, week.week]);

  if (locked) {
    return (
      <div className="card week-card locked">
        <div className="row" style={{ alignItems: "center", gap: 10 }}>
          <span className="week-num">🔒</span>
          <div>
            <strong className="dim">Week {week.week} — locked</strong>
            <p className="dim" style={{ margin: "4px 0 0", fontSize: 13 }}>
              Finish Week {week.week - 1} — every chapter marked done, the quiz passed at{" "}
              {track.pass_mark}%, and its coding final accepted — to open this one.
            </p>
          </div>
        </div>
      </div>
    );
  }

  async function startContest() {
    try {
      const id = await api.masteryStartContest(track.key, week.week);
      toast(`Checkpoint contest ready (#${id}) — open it from Contests`);
    } catch (e) {
      toast(String(e));
    }
  }

  return (
    <div
      className="card week-card"
      style={{ borderColor: progress.complete ? "var(--good)" : undefined }}
    >
      <div
        className="row"
        style={{ alignItems: "center", gap: 10, cursor: "pointer" }}
        onClick={() => setOpen((o) => !o)}
      >
        <span
          className="week-num"
          style={
            progress.complete
              ? { background: "var(--good)", borderColor: "var(--good)", color: "#fff" }
              : undefined
          }
        >
          {progress.complete ? "✓" : week.week}
        </span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <strong>
            Week {week.week} — {week.title}
          </strong>
          <p className="dim" style={{ margin: "3px 0 0", fontSize: 13 }}>
            {week.goal}
          </p>
        </div>
        <span className="row" style={{ gap: 6, flexWrap: "wrap", justifyContent: "flex-end" }}>
          {progress.conceptsTotal > 0 && (
            <span className="badge">
              {progress.conceptsDone}/{progress.conceptsTotal} chapters
            </span>
          )}
          <span className="badge">
            {progress.problemsSolved}/{progress.problemsTotal} problems
          </span>
          <span
            className="badge"
            style={
              progress.quizPassed
                ? { borderColor: "var(--good)", color: "var(--good)" }
                : { borderColor: "var(--accent)", color: "var(--accent)" }
            }
          >
            {progress.score === null ? "quiz —" : `quiz ${progress.score}%`}
          </span>
          <span
            className="badge"
            style={
              progress.examPassed
                ? { borderColor: "var(--good)", color: "var(--good)" }
                : { borderColor: "var(--accent)", color: "var(--accent)" }
            }
          >
            {progress.examPassed ? "final ✓" : "final —"}
          </span>
          <span className={`caret ${open ? "open" : ""}`} aria-hidden>
            ▸
          </span>
        </span>
      </div>

      <Bar percent={progress.percent} />

      {open && (
        <div style={{ marginTop: 14 }}>
          {progress.studySeconds > 0 && (
            <p className="dim" style={{ marginTop: 0, fontSize: 12 }}>
              {formatStudyTime(progress.studySeconds)} spent on this week so far.
            </p>
          )}

          {week.concepts.length > 0 && (
            <>
              <div className="io-label">📘 Chapters to study</div>
              <div className="grid cols-2" style={{ marginBottom: 14 }}>
                {week.concepts.map((key) => {
                  const c = conceptByKey.get(key);
                  const isDone = done.has(key);
                  return (
                    <div
                      key={key}
                      className="card"
                      style={{
                        marginBottom: 0,
                        cursor: "pointer",
                        borderColor: isDone ? "var(--good)" : undefined,
                      }}
                      onClick={() => nav(`/learn/${key}`)}
                    >
                      <div className="row" style={{ justifyContent: "space-between", gap: 8 }}>
                        <strong>
                          {isDone && <span style={{ color: "var(--good)" }}>✓ </span>}
                          {c?.name ?? key}
                        </strong>
                        <button
                          className="ghost"
                          style={{
                            padding: "2px 8px",
                            fontSize: 11,
                            borderColor: isDone ? "var(--good)" : undefined,
                            color: isDone ? "var(--good)" : undefined,
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            onToggleChapter(key);
                          }}
                        >
                          {isDone ? "Done" : "Mark done"}
                        </button>
                      </div>
                      {c?.what && (
                        <p className="dim" style={{ margin: "6px 0 0", fontSize: 12 }}>
                          {c.what}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {week.problems.length > 0 && (
            <>
              <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
                <div className="io-label">🎯 Problems to solve</div>
                {week.contest && (
                  <button
                    className="ghost"
                    style={{ padding: "2px 10px", fontSize: 12 }}
                    onClick={startContest}
                  >
                    ⏱ Run as a timed checkpoint
                  </button>
                )}
              </div>
              <div className="grid cols-2" style={{ marginBottom: 14 }}>
                {week.problems.map((ref) => {
                  const p = problemBySlug.get(ref.slug);
                  if (!p) return null;
                  const solved = p.solved_status === "solved";
                  return (
                    <div
                      key={ref.slug}
                      className="card"
                      style={{
                        marginBottom: 0,
                        cursor: "pointer",
                        borderColor: solved ? "var(--good)" : undefined,
                      }}
                      onClick={() => nav(`/solve/${p.id}`)}
                    >
                      <div className="row" style={{ justifyContent: "space-between", gap: 8 }}>
                        <strong>
                          {solved && <span style={{ color: "var(--good)" }}>✓ </span>}
                          {p.title}
                        </strong>
                        <DiffBadge d={p.difficulty} />
                      </div>
                      {ref.note && (
                        <p className="dim" style={{ margin: "6px 0 0", fontSize: 12 }}>
                          {ref.note}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {week.project && (
            <ProjectPanel
              brief={week.project}
              row={row}
              language={track.exam_language}
              onSave={(notes, code, done) =>
                api
                  .masterySaveProject(track.key, week.week, notes, code, done)
                  .then(onChanged)
              }
            />
          )}

          <QuizPanel
            week={week}
            track={track}
            best={progress.score}
            onSubmit={(percent) =>
              api.masteryRecordQuiz(track.key, week.week, percent).then(onChanged)
            }
          />

          {week.exam && (
            <ExamPanel
              exam={week.exam}
              weekNumber={week.week}
              passed={progress.examPassed}
              savedCode={row?.exam_code ?? ""}
              onResult={(passed, code) =>
                api.masteryRecordExam(track.key, week.week, passed, code).then(onChanged)
              }
            />
          )}
        </div>
      )}
    </div>
  );
}

/** The week's build brief, plus somewhere to actually record having done it. */
function ProjectPanel({
  brief,
  row,
  language,
  onSave,
}: {
  brief: string;
  row: MasteryProgress | undefined;
  language: string;
  onSave: (notes: string, code: string, done: boolean) => Promise<void>;
}) {
  const [notes, setNotes] = useState(row?.project_notes ?? "");
  const [code, setCode] = useState(row?.project_code ?? "");
  const [shipped, setShipped] = useState(row?.project_done ?? false);
  const [saving, setSaving] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const toast = useToast();

  async function save(nextShipped = shipped) {
    setSaving(true);
    try {
      await onSave(notes, code, nextShipped);
      setShipped(nextShipped);
      toast("Project saved");
    } finally {
      setSaving(false);
    }
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
      <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
        <div className="io-label" style={{ color: shipped ? "var(--good)" : "var(--accent)" }}>
          🔨 Build it yourself {shipped && "— shipped"}
        </div>
        <button
          className="ghost"
          style={{ padding: "2px 10px", fontSize: 12 }}
          onClick={() => setExpanded((e) => !e)}
        >
          {expanded ? "Hide workspace" : "Open workspace"}
        </button>
      </div>
      <p style={{ margin: "0 0 10px" }}>{brief}</p>

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
              height: 260,
              border: "1px solid var(--border)",
              borderRadius: 6,
              overflow: "hidden",
              marginBottom: 10,
            }}
          >
            <CodeEditor language={language} value={code} onChange={setCode} />
          </div>
          <div className="row" style={{ gap: 8, flexWrap: "wrap" }}>
            <button onClick={() => save()} disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </button>
            <button
              className="ghost"
              style={shipped ? { borderColor: "var(--good)", color: "var(--good)" } : undefined}
              onClick={() => save(!shipped)}
              disabled={saving}
            >
              {shipped ? "✓ Shipped — undo" : "Mark shipped"}
            </button>
          </div>
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

  const answered = picked.filter((p) => p >= 0).length;
  const correct = picked.filter((p, i) => p === paper[i].answer).length;
  const percent = Math.round((correct / paper.length) * 100);
  const passedNow = submitted && percent >= track.pass_mark;

  function submit() {
    setSubmitted(true);
    onSubmit(percent).catch(() => {});
  }

  function retake() {
    const next = drawExamPaper(week);
    setPaper(next);
    setPicked(next.map(() => -1));
    setSubmitted(false);
  }

  return (
    <div className="card" style={{ marginBottom: 14 }}>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <div className="io-label" style={{ margin: 0 }}>
          📝 End-of-week quiz
        </div>
        <span className="dim" style={{ fontSize: 12 }}>
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
        <div className="row" style={{ gap: 10, alignItems: "center", marginTop: 10 }}>
          <button onClick={submit} disabled={answered < paper.length}>
            Submit quiz
          </button>
          <span className="dim" style={{ fontSize: 12 }}>
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
          <button className="ghost" onClick={retake}>
            Draw a new paper
          </button>
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
  const isRight = picked === question.answer;
  return (
    <div
      className="card"
      style={{
        marginTop: 12,
        marginBottom: 0,
        borderColor: revealed ? (isRight ? "var(--good)" : "var(--bad)") : undefined,
      }}
    >
      <strong>
        {index}. {question.question}
      </strong>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 10 }}>
        {question.options.map((opt, oi) => {
          let border: string | undefined;
          let color: string | undefined;
          if (revealed) {
            if (oi === question.answer) {
              border = "var(--good)";
              color = "var(--good)";
            } else if (oi === picked) {
              border = "var(--bad)";
              color = "var(--bad)";
            }
          } else if (oi === picked) {
            border = "var(--accent)";
            color = "var(--accent)";
          }
          return (
            <button
              key={oi}
              className="ghost"
              style={{ textAlign: "left", borderColor: border, color, padding: "8px 12px" }}
              onClick={() => onPick(oi)}
              disabled={revealed}
            >
              {revealed && oi === question.answer && "✓ "}
              {revealed && oi === picked && oi !== question.answer && "✗ "}
              {opt}
            </button>
          );
        })}
      </div>
      {revealed && (
        <div
          className="card"
          style={{
            marginTop: 10,
            marginBottom: 0,
            background: "var(--accent-dim)",
            borderColor: isRight ? "var(--good)" : "var(--bad)",
          }}
        >
          <div className="io-label" style={{ color: isRight ? "var(--good)" : "var(--bad)" }}>
            {isRight ? "Correct" : "Not quite"}
          </div>
          <p style={{ margin: 0 }}>{question.explanation}</p>
        </div>
      )}
    </div>
  );
}

/** The week's coding final — the half of the gate a quiz cannot test. Judged by
 * the same runner as the Learn challenges. */
function ExamPanel({
  exam,
  weekNumber,
  passed,
  savedCode,
  onResult,
}: {
  exam: MasteryExam;
  weekNumber: number;
  passed: boolean;
  savedCode: string;
  onResult: (passed: boolean, code: string) => Promise<void>;
}) {
  const [code, setCode] = useState(savedCode || exam.starter);
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState("");
  const [showHint, setShowHint] = useState(false);
  const [showSolution, setShowSolution] = useState(false);

  async function submit() {
    setRunning(true);
    setErr("");
    setReport(null);
    const cases: TestCase[] = exam.tests.map((t, i) => ({
      id: 0,
      problem_id: 0,
      kind: "hidden",
      name: `Test ${i + 1}`,
      input: t.input,
      expected_output: t.output,
      ordering: i,
    }));
    try {
      const r = await api.runTests(null, exam.language, code, cases);
      setReport(r);
      await onResult(r.status === "accepted", code);
    } catch (e) {
      setErr(String(e));
    } finally {
      setRunning(false);
    }
  }

  const accepted = report?.status === "accepted";
  const untouched = code.includes("____");

  return (
    <div
      className="card"
      style={{ marginBottom: 0, borderColor: passed ? "var(--good)" : "var(--accent)" }}
    >
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <div className="io-label" style={{ margin: 0, color: passed ? "var(--good)" : "var(--accent)" }}>
          🧪 Coding final — {exam.title} {passed && "✓"}
        </div>
        <span className="badge">{exam.language}</span>
      </div>
      <p style={{ margin: "6px 0 10px" }}>{exam.prompt}</p>

      <div
        style={{
          height: 340,
          border: "1px solid var(--border)",
          borderRadius: 6,
          overflow: "hidden",
        }}
      >
        <CodeEditor language={exam.language} value={code} onChange={setCode} onRun={submit} />
      </div>

      <div className="row" style={{ marginTop: 10, flexWrap: "wrap", gap: 8 }}>
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
        {untouched && !running && (
          <span className="dim" style={{ fontSize: 12, alignSelf: "center" }}>
            Replace the <code>____</code> before submitting.
          </span>
        )}
      </div>

      {showHint && exam.hint && (
        <div className="card" style={{ marginTop: 10, marginBottom: 0, background: "var(--accent-dim)" }}>
          <div className="io-label" style={{ color: "var(--accent)" }}>Hint</div>
          <p style={{ margin: 0 }}>{exam.hint}</p>
        </div>
      )}

      {err && (
        <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
          <div className="io-label" style={{ color: "var(--bad)" }}>Couldn&rsquo;t run</div>
          <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 12 }}>{err}</pre>
        </div>
      )}

      {report && <ExamFeedback report={report} weekNumber={weekNumber} accepted={accepted} />}

      {showSolution && passed && (
        <div style={{ marginTop: 10 }}>
          <Markdown>{"```" + exam.language + "\n" + exam.solution + "\n```"}</Markdown>
        </div>
      )}
    </div>
  );
}

function ExamFeedback({
  report,
  weekNumber,
  accepted,
}: {
  report: JudgeReport;
  weekNumber: number;
  accepted: boolean;
}) {
  if (report.status === "not_installed") {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
        <div className="io-label" style={{ color: "var(--bad)" }}>Toolchain missing</div>
        <p style={{ margin: 0 }}>
          {report.not_installed_hint || "Install the language toolchain to run this final."}
        </p>
      </div>
    );
  }

  if (report.compile_error) {
    return (
      <div className="card" style={{ marginTop: 10, marginBottom: 0, borderColor: "var(--bad)" }}>
        <div className="io-label" style={{ color: "var(--bad)" }}>Compile error</div>
        <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 12 }}>{report.compile_error}</pre>
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
        <p style={{ margin: 0 }}>
          Week {weekNumber}&rsquo;s coding final is done. With the quiz passed and every
          chapter marked, the next week unlocks.
        </p>
      ) : (
        failing.slice(0, 3).map((r, i) => (
          <div key={i} style={{ marginTop: 6, fontSize: 12 }}>
            <div className="dim">{r.name}</div>
            <div style={{ fontFamily: "var(--font-mono)" }}>
              <div>
                input: <code>{r.input.replace(/\n/g, " ⏎ ") || "(none)"}</code>
              </div>
              <div>
                expected: <code>{r.expected}</code>
              </div>
              <div style={{ color: "var(--bad)" }}>
                got: <code>{r.timed_out ? "(timed out)" : r.actual || "(nothing)"}</code>
              </div>
              {r.stderr && <pre style={{ margin: "4px 0 0", whiteSpace: "pre-wrap" }}>{r.stderr}</pre>}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
