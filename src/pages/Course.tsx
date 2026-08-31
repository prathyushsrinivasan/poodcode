import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { CourseLesson, CourseWeek, Exercise, TsCourse } from "../types";
import { Markdown } from "../components/Markdown";
import { ExerciseCard, QuizSection } from "../components/LearnExercise";
import { Section, useCollapse } from "../components/Collapsible";
import { Empty } from "../components/common";
import { useToast } from "../components/Toast";
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

// Every judged exercise required to complete a week: all lesson exercises plus
// an auto-graded capstone. The optional "stretch" build is NOT required.
function requiredExerciseIds(week: CourseWeek): string[] {
  const ids: string[] = [];
  for (const l of week.lessons ?? []) for (const e of l.exercises ?? []) ids.push(e.id);
  if (week.capstone?.exercise) ids.push(week.capstone.exercise.id);
  return ids;
}

// Weeks are sized in study hours, not minutes — "~5 h" reads as a plan, where
// "~300 min" reads as a wall.
function studyTime(minutes: number): string {
  if (minutes < 90) return `~${minutes} min`;
  const hours = minutes / 60;
  return `~${Number.isInteger(hours) ? hours : hours.toFixed(1)} h`;
}

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
    // Neighbours for prev/next nav — only among authored weeks.
    const authored = course.weeks.filter((w) => w.authored).sort((a, b) => a.number - b.number);
    const idx = authored.findIndex((w) => w.number === wk.number);
    return (
      <WeekDetail
        key={wk.number}
        week={wk}
        isDone={done.has(weekKey(wk.number))}
        onSetDone={(v) => setWeekDone(wk.number, v)}
        prev={idx > 0 ? authored[idx - 1] : null}
        next={idx >= 0 && idx < authored.length - 1 ? authored[idx + 1] : null}
      />
    );
  }

  return <Overview course={course} done={done} />;
}

function Overview({ course, done }: { course: TsCourse; done: Set<string> }) {
  const nav = useNavigate();

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
              {doneCount === 0 ? "Start Week 1 →" : `Resume · Week ${nextWeek.number} →`}
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
              const nEx = requiredExerciseIds(w).length;
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
                      <span className="row" style={{ gap: 4, flexWrap: "wrap", justifyContent: "flex-end" }}>
                        {nLessons > 0 && <span className="badge">{nLessons} lessons</span>}
                        {nEx > 0 && <span className="badge">{nEx} exercises</span>}
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
                  {!soon && w.est_minutes > 0 && (
                    <p className="faint" style={{ margin: "6px 0 0", fontSize: 12 }}>
                      ⏱️ about {studyTime(w.est_minutes)} of study
                    </p>
                  )}
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
  prev,
  next,
}: {
  week: CourseWeek;
  isDone: boolean;
  onSetDone: (done: boolean) => void;
  prev: CourseWeek | null;
  next: CourseWeek | null;
}) {
  const nav = useNavigate();
  const toast = useToast();
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const [scrolledToBottom, setScrolledToBottom] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const celebrated = useRef(false);
  // Lessons start collapsed: a week now runs to forty-odd exercises, and each
  // open lesson mounts a Monaco editor per exercise. The contents card below is
  // how you navigate them.
  const sec = useCollapse(`course-sec:w${week.number}`, false);
  const lessons = week.lessons ?? [];
  const lessonKeys = useMemo(() => lessons.map((l) => l.key), [lessons]);

  function openLesson(key: string) {
    if (!sec.isOpen(key)) sec.toggle(key);
    // Let the body mount before scrolling to it.
    requestAnimationFrame(() =>
      document.getElementById(`lesson-${key}`)?.scrollIntoView({ behavior: "smooth", block: "start" })
    );
  }

  const gradableIds = useMemo(() => requiredExerciseIds(week), [week]);
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
    if (!isDone && scrolledToBottom && allSolved && !celebrated.current) {
      celebrated.current = true;
      onSetDone(true);
      toast(week.milestone ? `🎉 Week ${week.number} complete! ${week.milestone}` : `🎉 Week ${week.number} complete!`);
    }
  }, [isDone, scrolledToBottom, allSolved, onSetDone, toast, week.milestone, week.number]);

  const cap = week.capstone;

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
          {week.est_minutes > 0 && <span className="badge">⏱️ {studyTime(week.est_minutes)}</span>}
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
        <p style={{ marginBottom: week.why ? 8 : 0 }}>{week.goal}</p>
        {week.why && (
          <p className="dim" style={{ margin: 0, fontSize: 13 }}>
            💡 Why it matters: {week.why}
          </p>
        )}
      </div>

      {week.objectives.length > 0 && (
        <div className="card" style={{ marginBottom: 14 }}>
          <div className="io-label">By the end of this week you can…</div>
          <ul style={{ margin: "6px 0 0", paddingLeft: 20 }}>
            {week.objectives.map((o, i) => (
              <li key={i} style={{ marginBottom: 2 }}>{o}</li>
            ))}
          </ul>
        </div>
      )}

      {week.summary && <Markdown>{week.summary}</Markdown>}

      {lessons.length > 0 && (
        <div className="card" style={{ marginBottom: 14 }}>
          <div className="row" style={{ marginBottom: 8 }}>
            <div className="io-label" style={{ margin: 0 }}>
              📚 Lessons in this week
            </div>
            <span className="spacer" />
            <button
              className="ghost"
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => sec.setAll(lessonKeys, true)}
            >
              Expand all
            </button>
            <button
              className="ghost"
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => sec.setAll(lessonKeys, false)}
            >
              Collapse all
            </button>
          </div>
          {lessons.map((lesson, li) => {
            const ids = (lesson.exercises ?? []).map((e) => e.id);
            const n = ids.filter((id) => solvedEx.has(id)).length;
            const complete = ids.length > 0 && n === ids.length;
            return (
              <div
                key={lesson.key}
                className="row"
                style={{
                  cursor: "pointer",
                  gap: 8,
                  padding: "5px 0",
                  borderBottom: li < lessons.length - 1 ? "1px solid var(--border)" : undefined,
                }}
                onClick={() => openLesson(lesson.key)}
              >
                <span style={{ color: complete ? "var(--good)" : "var(--accent)", width: 18 }}>
                  {complete ? "✓" : li + 1}
                </span>
                <span style={{ flex: 1 }}>
                  {lesson.title}
                  {lesson.what && (
                    <span className="faint" style={{ fontSize: 12 }}>
                      {" "}
                      — {lesson.what}
                    </span>
                  )}
                </span>
                {ids.length > 0 && (
                  <span className="dim mono" style={{ fontSize: 12 }}>
                    {n}/{ids.length}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}

      {lessons.map((lesson, li) => (
        <div key={lesson.key} id={`lesson-${lesson.key}`}>
          <Section
            title={`${li + 1}. ${lesson.title}`}
            open={sec.isOpen(lesson.key)}
            onToggle={() => sec.toggle(lesson.key)}
            meta={
              <span className="dim" style={{ fontSize: 12 }}>
                {lessonSolvedLabel(lesson, solvedEx)}
              </span>
            }
          >
            <LessonBody lesson={lesson} onSolved={handleSolved} />
          </Section>
        </div>
      ))}

      {cap && (
        <>
          <div className="divider" />
          <h2 style={{ marginBottom: 4 }}>🏆 Capstone project</h2>
          <div className="card" style={{ marginBottom: 14, borderColor: "var(--accent)" }}>
            <strong style={{ fontSize: 16 }}>{cap.title}</strong>
            <div style={{ marginTop: 8 }}>
              <Markdown>{cap.brief}</Markdown>
            </div>
            {cap.example_io && (
              <>
                <div className="io-label" style={{ marginTop: 6 }}>Expected output</div>
                <Markdown>{"```\n" + cap.example_io + "\n```"}</Markdown>
              </>
            )}
            {cap.rubric.length > 0 && (
              <>
                <div className="io-label" style={{ marginTop: 6 }}>Checklist</div>
                <ul style={{ margin: "4px 0 0", paddingLeft: 20 }}>
                  {cap.rubric.map((r, i) => (
                    <li key={i} style={{ marginBottom: 2 }}>{r}</li>
                  ))}
                </ul>
              </>
            )}
            {cap.kind === "brief" && (
              <p className="faint" style={{ fontSize: 12, margin: "8px 0 0" }}>
                This is a free-build project — write it in the editor of your choice, then mark the
                week done yourself when you're happy with it.
              </p>
            )}
          </div>
          {cap.exercise && (
            <ExerciseCard index={1} exercise={cap.exercise} challenge onSolved={handleSolved} />
          )}
          {cap.reference && <ReferenceReveal reference={cap.reference} />}
          {cap.stretch && (
            <>
              <h4 style={{ margin: "14px 0 4px" }}>🚀 Stretch goal (optional)</h4>
              <ExerciseCard index={1} exercise={cap.stretch} challenge onSolved={handleSolved} />
            </>
          )}
        </>
      )}

      {week.self_check.length > 0 && (
        <>
          <div className="divider" />
          <h3>✅ Self-check</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            Before you move on, make sure you can honestly say yes to each of these:
          </p>
          <div className="card">
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {week.self_check.map((s, i) => (
                <li key={i} style={{ marginBottom: 4 }}>{s}</li>
              ))}
            </ul>
          </div>
        </>
      )}

      {week.review.length > 0 && (
        <>
          <div className="divider" />
          <h3>🔁 End-of-week review</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            A quick mixed quiz — some of these reach back to earlier weeks.
          </p>
          <QuizSection questions={week.review} />
        </>
      )}

      {week.glossary.length > 0 && (
        <Section
          title="📖 Glossary"
          open={sec.isOpen("glossary")}
          onToggle={() => sec.toggle("glossary")}
          meta={<span className="badge">{week.glossary.length} terms</span>}
        >
          <div className="card" style={{ marginTop: 0 }}>
            {week.glossary.map((g, i) => (
              <div key={i} style={{ padding: "5px 0", borderBottom: i < week.glossary.length - 1 ? "1px solid var(--border)" : undefined }}>
                <code style={{ color: "var(--accent)" }}>{g.term}</code> — {g.def}
              </div>
            ))}
          </div>
        </Section>
      )}

      {week.cheatsheet && (
        <Section
          title="🧾 Cheat sheet"
          open={sec.isOpen("cheatsheet")}
          onToggle={() => sec.toggle("cheatsheet")}
        >
          <Markdown>{week.cheatsheet}</Markdown>
        </Section>
      )}

      {week.milestone && (
        <div className="card" style={{ marginTop: 16, borderColor: "var(--good)" }}>
          <div className="io-label" style={{ color: "var(--good)" }}>🎉 Milestone</div>
          <p style={{ margin: 0 }}>{week.milestone}</p>
        </div>
      )}

      {!isDone && (
        <p className="faint" style={{ fontSize: 12, marginTop: 24, textAlign: "center" }}>
          {gradableIds.length > 0
            ? `This week marks itself ✓ Done once you've read to here and solved its ${gradableIds.length} exercise${gradableIds.length === 1 ? "" : "s"}${allSolved ? " — all solved!" : ` (${solvedCount}/${gradableIds.length} solved)`}.`
            : "This week marks itself ✓ Done once you've read to here."}
        </p>
      )}

      <div className="row" style={{ marginTop: 20, justifyContent: "space-between" }}>
        {prev ? (
          <button className="ghost" onClick={() => nav(`/course/${prev.number}`)}>
            ← Week {prev.number}: {prev.theme}
          </button>
        ) : (
          <span />
        )}
        {next ? (
          <button className="primary" onClick={() => nav(`/course/${next.number}`)}>
            Week {next.number}: {next.theme} →
          </button>
        ) : (
          <button className="ghost" onClick={() => nav("/course")}>
            Back to course overview
          </button>
        )}
      </div>

      {/* Sentinel: intersecting means the week has been read to the bottom. */}
      <div ref={bottomRef} style={{ height: 1 }} />
    </div>
  );
}

function lessonSolvedLabel(lesson: CourseLesson, solvedEx: Set<string>): string {
  const ids = (lesson.exercises ?? []).map((e) => e.id);
  if (ids.length === 0) return "";
  const n = ids.filter((id) => solvedEx.has(id)).length;
  return n === ids.length ? "✓ done" : `${n}/${ids.length}`;
}

function ReferenceReveal({ reference }: { reference: string }) {
  const [show, setShow] = useState(false);
  return (
    <div style={{ marginTop: 10 }}>
      <button className="ghost" onClick={() => setShow((s) => !s)}>
        {show ? "Hide reference solution" : "Reveal a reference solution"}
      </button>
      {show && (
        <div style={{ marginTop: 10 }}>
          <Markdown>{"```ts\n" + reference + "\n```"}</Markdown>
        </div>
      )}
    </div>
  );
}

function LessonBody({
  lesson,
  onSolved,
}: {
  lesson: CourseLesson;
  onSolved: (id: string) => void;
}) {
  const exercises = lesson.exercises ?? [];
  const kindOf = (e: Exercise) => e.kind || "drill";
  const drills = exercises.filter((e) => kindOf(e) === "drill");
  const fixes = exercises.filter((e) => kindOf(e) === "fix");
  const challenges = exercises.filter((e) => kindOf(e) === "challenge");
  const warmup = lesson.warmup ?? [];
  const quiz = lesson.quiz ?? [];

  return (
    <div>
      {lesson.what && (
        <p className="dim" style={{ marginTop: 0 }}>
          {lesson.what}
        </p>
      )}
      <Markdown>{lesson.lesson}</Markdown>

      {warmup.length > 0 && (
        <>
          <h4>🔮 Predict the output</h4>
          <p className="dim" style={{ marginTop: -4 }}>
            Read the code and guess what it prints — then check.
          </p>
          <QuizSection questions={warmup} />
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

      {fixes.length > 0 && (
        <>
          <h4>🐞 Fix the bug</h4>
          <p className="dim" style={{ marginTop: -4 }}>
            This program looks right but doesn't work. Find and fix the bug so the tests pass.
          </p>
          {fixes.map((ex, i) => (
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

      {quiz.length > 0 && (
        <>
          <h4>❓ Check yourself</h4>
          <QuizSection questions={quiz} />
        </>
      )}
    </div>
  );
}
