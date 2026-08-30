import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { CourseLesson, CourseWeek, TsCourse } from "../types";
import { Markdown } from "../components/Markdown";
import { ExerciseCard, QuizSection } from "../components/LearnExercise";
import { Empty } from "../components/common";
import {
  loadDoneChapters,
  setChapterDone,
  solvedExercises,
  markExerciseSolved,
} from "../lib/learnProgress";

// A course week's completion is tracked in the same SQLite-backed chapter-done
// set as the Learn tab, under a namespaced key so it never collides with a
// concept key.
const weekKey = (n: number) => `ts-course:w${n}`;

export default function Course() {
  const { week } = useParams();
  const [course, setCourse] = useState<TsCourse | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());
  const nav = useNavigate();

  useEffect(() => {
    api.tsCourse().then(setCourse).catch(() => setCourse(null));
    loadDoneChapters().then(setDone).catch(() => {});
  }, []);

  async function setWeekDone(n: number, value: boolean) {
    const next = await setChapterDone(done, weekKey(n), value);
    setDone(next);
  }

  if (!course) return <div className="page">Loading…</div>;
  if (course.weeks.length === 0) {
    return (
      <div className="page">
        <Empty icon="📗" text="The TypeScript course isn't built yet." />
      </div>
    );
  }

  if (week) {
    const n = Number(week);
    const wk = course.weeks.find((w) => w.number === n);
    if (!wk) {
      return (
        <div className="page">
          <Empty icon="📗" text="Week not found." />
          <button onClick={() => nav("/course")}>Back to course</button>
        </div>
      );
    }
    return (
      <WeekDetail
        week={wk}
        isDone={done.has(weekKey(wk.number))}
        onSetDone={(v) => setWeekDone(wk.number, v)}
      />
    );
  }

  return <Overview course={course} done={done} />;
}

function Overview({ course, done }: { course: TsCourse; done: Set<string> }) {
  const nav = useNavigate();

  // Group weeks into months, preserving order.
  const months = useMemo(() => {
    const map = new Map<number, { title: string; weeks: CourseWeek[] }>();
    for (const w of course.weeks) {
      if (!map.has(w.month)) map.set(w.month, { title: w.month_title, weeks: [] });
      map.get(w.month)!.weeks.push(w);
    }
    return [...map.entries()].sort((a, b) => a[0] - b[0]);
  }, [course.weeks]);

  const authored = course.weeks.filter((w) => w.authored);
  const doneCount = authored.filter((w) => done.has(weekKey(w.number))).length;
  const nextWeek = authored.find((w) => !done.has(weekKey(w.number))) ?? authored[0];
  const pct = authored.length ? Math.round((doneCount / authored.length) * 100) : 0;

  return (
    <div className="page">
      <h1 className="page-title">{course.title}</h1>
      <p className="page-sub">{course.subtitle}</p>

      <div className="card" style={{ marginBottom: 18 }}>
        <div className="row" style={{ alignItems: "center", gap: 12 }}>
          <div style={{ flex: 1 }}>
            <div className="row" style={{ marginBottom: 6 }}>
              <strong>Your progress</strong>
              <span className="spacer" />
              <span className="dim mono">
                {doneCount}/{authored.length} weeks
              </span>
            </div>
            <div className="progress">
              <span
                style={{ width: `${pct}%`, background: pct === 100 ? "var(--good)" : "var(--accent)" }}
              />
            </div>
          </div>
          {nextWeek && (
            <button className="primary" onClick={() => nav(`/course/${nextWeek.number}`)}>
              {doneCount === 0 ? "Start Week 1 →" : `Continue · Week ${nextWeek.number} →`}
            </button>
          )}
        </div>
        <p className="faint" style={{ fontSize: 12, margin: "10px 0 0" }}>
          A week auto-completes once you read it through and solve its exercises. You'll never be
          asked to use syntax or ideas a later week hasn't taught yet.
        </p>
      </div>

      {months.map(([m, { title, weeks }]) => (
        <div key={m} style={{ marginBottom: 24 }}>
          <div className="row" style={{ marginBottom: 10 }}>
            <h3 style={{ margin: 0 }}>
              Month {m} — {title}
            </h3>
            <span className="spacer" />
            <span className="dim" style={{ fontSize: 12 }}>
              {weeks.filter((w) => done.has(weekKey(w.number))).length}/
              {weeks.filter((w) => w.authored).length} done
            </span>
          </div>
          <div className="grid cols-2">
            {weeks.map((w) => {
              const isDone = done.has(weekKey(w.number));
              const soon = !w.authored;
              const nLessons = w.lessons?.length ?? 0;
              return (
                <div
                  key={w.number}
                  className="card"
                  style={{
                    cursor: soon ? "default" : "pointer",
                    opacity: soon ? 0.55 : 1,
                    borderColor: isDone ? "var(--good)" : undefined,
                  }}
                  onClick={() => !soon && nav(`/course/${w.number}`)}
                >
                  <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
                    <strong>
                      {isDone && <span style={{ color: "var(--good)" }}>✓ </span>}
                      Week {w.number}: {w.theme}
                    </strong>
                    {soon ? (
                      <span className="badge">soon</span>
                    ) : (
                      <span className="row" style={{ gap: 4 }}>
                        {nLessons > 0 && <span className="badge">{nLessons} lessons</span>}
                        {w.capstone && (
                          <span
                            className="badge"
                            style={{ borderColor: "var(--accent)", color: "var(--accent)" }}
                            title={w.capstone.title}
                          >
                            🏆 project
                          </span>
                        )}
                      </span>
                    )}
                  </div>
                  <p className="dim" style={{ margin: "6px 0 0", fontSize: 13 }}>
                    🎯 {w.goal}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function WeekDetail({
  week,
  isDone,
  onSetDone,
}: {
  week: CourseWeek;
  isDone: boolean;
  onSetDone: (done: boolean) => void;
}) {
  const nav = useNavigate();
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const [scrolledToBottom, setScrolledToBottom] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // Every judged exercise across the week's lessons + an auto-graded capstone.
  const gradableIds = useMemo(() => {
    const ids: string[] = [];
    for (const l of week.lessons ?? []) for (const e of l.exercises ?? []) ids.push(e.id);
    if (week.capstone?.exercise) ids.push(week.capstone.exercise.id);
    return ids;
  }, [week]);
  const allSolved = gradableIds.every((id) => solvedEx.has(id));
  const solvedCount = gradableIds.filter((id) => solvedEx.has(id)).length;

  function handleSolved(id: string) {
    setSolvedEx(new Set(markExerciseSolved(id)));
  }

  useEffect(() => {
    const el = bottomRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) setScrolledToBottom(true);
      },
      { threshold: 0.01 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [week.number]);

  useEffect(() => {
    if (!isDone && scrolledToBottom && allSolved) onSetDone(true);
  }, [isDone, scrolledToBottom, allSolved, onSetDone]);

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4, justifyContent: "space-between" }}>
        <div className="row">
          <button className="ghost" onClick={() => nav("/course")}>
            ← Course
          </button>
          <span className="badge">
            Week {week.number} · Month {week.month}
          </span>
        </div>
        <button
          className="ghost"
          style={isDone ? { borderColor: "var(--good)", color: "var(--good)" } : undefined}
          onClick={() => onSetDone(!isDone)}
          title={isDone ? "Marked complete — click to undo" : "Mark this week complete"}
        >
          {isDone ? "✓ Done" : "Mark done"}
        </button>
      </div>

      <h1 className="page-title" style={{ marginTop: 6 }}>
        {week.theme}
      </h1>

      <div className="card" style={{ marginBottom: 14, borderColor: "var(--accent)" }}>
        <div className="io-label" style={{ color: "var(--accent)" }}>
          🎯 This week's goal
        </div>
        <p style={{ marginBottom: 0 }}>{week.goal}</p>
      </div>

      {week.summary && <Markdown>{week.summary}</Markdown>}

      {(week.lessons ?? []).map((lesson, li) => (
        <LessonBlock key={lesson.key} index={li + 1} lesson={lesson} onSolved={handleSolved} />
      ))}

      {week.capstone && (
        <>
          <div className="divider" />
          <h2 style={{ marginBottom: 4 }}>🏆 Capstone project</h2>
          <div className="card" style={{ marginBottom: 14, borderColor: "var(--accent)" }}>
            <strong style={{ fontSize: 16 }}>{week.capstone.title}</strong>
            <div style={{ marginTop: 8 }}>
              <Markdown>{week.capstone.brief}</Markdown>
            </div>
            {week.capstone.kind === "brief" && (
              <p className="faint" style={{ fontSize: 12, margin: "8px 0 0" }}>
                This is a free-build project — write it in the editor of your choice, then mark the
                week done yourself when you're happy with it.
              </p>
            )}
          </div>
          {week.capstone.exercise && (
            <ExerciseCard index={1} exercise={week.capstone.exercise} challenge onSolved={handleSolved} />
          )}
        </>
      )}

      {!isDone && (
        <p className="faint" style={{ fontSize: 12, marginTop: 24, textAlign: "center" }}>
          {gradableIds.length > 0
            ? `This week marks itself ✓ Done once you've read to here and solved its ${gradableIds.length} exercise${gradableIds.length === 1 ? "" : "s"}${allSolved ? " — all solved!" : ` (${solvedCount}/${gradableIds.length} solved)`}.`
            : "This week marks itself ✓ Done once you've read to here."}
        </p>
      )}

      <div ref={bottomRef} style={{ height: 1 }} />
    </div>
  );
}

function LessonBlock({
  index,
  lesson,
  onSolved,
}: {
  index: number;
  lesson: CourseLesson;
  onSolved: (id: string) => void;
}) {
  const exercises = lesson.exercises ?? [];
  const drills = exercises.filter((e) => (e.kind || "drill") !== "challenge");
  const challenges = exercises.filter((e) => e.kind === "challenge");
  const quiz = lesson.quiz ?? [];

  return (
    <div style={{ marginTop: 18 }}>
      <h2 style={{ marginBottom: 2 }}>
        {index}. {lesson.title}
      </h2>
      {lesson.what && (
        <p className="dim" style={{ marginTop: 0 }}>
          {lesson.what}
        </p>
      )}
      <Markdown>{lesson.lesson}</Markdown>

      {quiz.length > 0 && (
        <>
          <h4>❓ Check yourself</h4>
          <QuizSection questions={quiz} />
        </>
      )}

      {drills.length > 0 && (
        <>
          <h4>🧩 Practice — fill in the blank</h4>
          {drills.map((ex, i) => (
            <ExerciseCard key={ex.id} index={i + 1} exercise={ex} onSolved={onSolved} />
          ))}
        </>
      )}

      {challenges.length > 0 && (
        <>
          <h4>🏆 Coding challenge</h4>
          {challenges.map((ex, i) => (
            <ExerciseCard key={ex.id} index={i + 1} exercise={ex} challenge onSolved={onSolved} />
          ))}
        </>
      )}
    </div>
  );
}
