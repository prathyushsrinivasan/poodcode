import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { CourseLesson, CourseWeek, WeeklyCourse } from "../types";
import { Markdown } from "../components/Markdown";
import { ExerciseCard, QuizSection } from "../components/LearnExercise";
import { ExerciseSections } from "../components/ExerciseSections";
import { ReferenceReveal } from "../components/ReferenceReveal";
import { Section, useCollapse } from "../components/Collapsible";
import { Empty } from "../components/common";
import { useToast } from "../components/Toast";
import {
  loadDoneChapters,
  setChapterDone,
  solvedExercises,
  markExerciseSolved,
} from "../lib/learnProgress";
import { collectExerciseIds, solvedLabel, studyTime } from "../lib/trackProgress";

// This page renders both structured courses. They share a data model, a judge
// and every interaction; they differ only in where the content comes from, how
// the two levels are named (Week/Month vs Module/Part — the course carries its
// own labels), and the namespace their progress is stored under.
type Track = {
  /** Progress-key namespace. Never change it, or existing progress is orphaned. */
  key: string;
  load: () => Promise<WeeklyCourse>;
  /** Route base; detail pages live at `${base}/${unitNumber}`. */
  base: string;
  icon: string;
  emptyText: string;
};

const TS_TRACK: Track = {
  key: "ts",
  load: () => api.tsCourse(),
  base: "/course",
  icon: "📗",
  emptyText: "The TypeScript course isn't built yet.",
};

const JAVA_TRACK: Track = {
  key: "java",
  load: () => api.javaCourse(),
  base: "/java-course",
  icon: "☕",
  emptyText: "The Java course isn't built yet.",
};

// A unit's completion is tracked in the same SQLite-backed chapter-done set as
// the Learn tab, under a namespaced key so it collides with neither a concept
// key nor the other course.
const unitKey = (track: Track, n: number) => `${track.key}-course:w${n}`;

/** Labels default to the TypeScript course's original time-based wording, so a
 * course that omits them renders exactly as it always did. */
function labelsOf(course: WeeklyCourse) {
  return {
    unit: course.unit_label || "Week",
    group: course.group_label || "Month",
    // "3 weeks" / "3 modules" — every label here is a single capitalised word.
    units: (course.unit_label || "Week").toLowerCase() + "s",
  };
}

// Every judged exercise required to complete a unit: all lesson exercises plus
// an auto-graded capstone. The optional "stretch" build is NOT required, which
// is why it is not passed here.
const requiredExerciseIds = (week: CourseWeek) =>
  collectExerciseIds(week.lessons, week.capstone?.exercise);

/** The 8-month TypeScript course (route `/course`). */
export default function Course() {
  return <CourseView track={TS_TRACK} />;
}

/** The topic-laddered Java course (route `/java-course`). */
export function JavaCourse() {
  return <CourseView track={JAVA_TRACK} />;
}

function CourseView({ track }: { track: Track }) {
  const { week } = useParams();
  const [course, setCourse] = useState<WeeklyCourse | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());
  const nav = useNavigate();

  useEffect(() => {
    setCourse(null);
    track.load().then(setCourse).catch(() => setCourse(null));
    loadDoneChapters().then(setDone).catch(() => {});
  }, [track]);

  async function setUnitDone(n: number, value: boolean) {
    const next = await setChapterDone(done, unitKey(track, n), value);
    setDone(next);
  }

  if (!course) return <div className="page">Loading…</div>;
  if (course.weeks.length === 0) {
    return (
      <div className="page">
        <Empty icon={track.icon} text={track.emptyText} />
      </div>
    );
  }

  const labels = labelsOf(course);

  if (week) {
    const n = Number(week);
    const wk = course.weeks.find((w) => w.number === n);
    if (!wk) {
      return (
        <div className="page">
          <Empty icon={track.icon} text={`${labels.unit} not found.`} />
          <button onClick={() => nav(track.base)}>Back to course</button>
        </div>
      );
    }
    // Neighbours for prev/next nav — only among authored units.
    const authored = course.weeks.filter((w) => w.authored).sort((a, b) => a.number - b.number);
    const idx = authored.findIndex((w) => w.number === wk.number);
    return (
      <UnitDetail
        key={wk.number}
        track={track}
        labels={labels}
        week={wk}
        isDone={done.has(unitKey(track, wk.number))}
        onSetDone={(v) => setUnitDone(wk.number, v)}
        prev={idx > 0 ? authored[idx - 1] : null}
        next={idx >= 0 && idx < authored.length - 1 ? authored[idx + 1] : null}
      />
    );
  }

  return <Overview track={track} labels={labels} course={course} done={done} />;
}

type Labels = ReturnType<typeof labelsOf>;

function Overview({
  track,
  labels,
  course,
  done,
}: {
  track: Track;
  labels: Labels;
  course: WeeklyCourse;
  done: Set<string>;
}) {
  const nav = useNavigate();

  const groups = useMemo(() => {
    const map = new Map<number, { title: string; weeks: CourseWeek[] }>();
    for (const w of course.weeks) {
      if (!map.has(w.month)) map.set(w.month, { title: w.month_title, weeks: [] });
      map.get(w.month)!.weeks.push(w);
    }
    return [...map.entries()].sort((a, b) => a[0] - b[0]);
  }, [course.weeks]);

  const authored = course.weeks.filter((w) => w.authored);
  const doneCount = authored.filter((w) => done.has(unitKey(track, w.number))).length;
  const nextUnit = authored.find((w) => !done.has(unitKey(track, w.number))) ?? authored[0];
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
                {doneCount}/{authored.length} {labels.units}
              </span>
            </div>
            <div className="progress">
              <span
                style={{ width: `${pct}%`, background: pct === 100 ? "var(--good)" : "var(--accent)" }}
              />
            </div>
          </div>
          {nextUnit && (
            <button className="primary" onClick={() => nav(`${track.base}/${nextUnit.number}`)}>
              {doneCount === 0
                ? `Start ${labels.unit} ${nextUnit.number} →`
                : `Resume · ${labels.unit} ${nextUnit.number} →`}
            </button>
          )}
        </div>
        <p className="faint" style={{ fontSize: 12, margin: "10px 0 0" }}>
          A {labels.unit.toLowerCase()} auto-completes once you read it through and solve its
          exercises. You'll never be asked to use syntax or ideas a later{" "}
          {labels.unit.toLowerCase()} hasn't taught yet.
        </p>
      </div>

      {groups.map(([m, { title, weeks }]) => (
        <div key={m} style={{ marginBottom: 24 }}>
          <div className="row" style={{ marginBottom: 10 }}>
            <h3 style={{ margin: 0 }}>
              {labels.group} {m} — {title}
            </h3>
            <span className="spacer" />
            <span className="dim" style={{ fontSize: 12 }}>
              {weeks.filter((w) => done.has(unitKey(track, w.number))).length}/
              {weeks.filter((w) => w.authored).length} done
            </span>
          </div>
          <div className="grid cols-2">
            {weeks.map((w) => {
              const isDone = done.has(unitKey(track, w.number));
              const soon = !w.authored;
              const nLessons = w.lessons?.length ?? 0;
              const nEx = requiredExerciseIds(w).length;
              const nPractice = (w.practice ?? []).reduce(
                (sum, f) => sum + (f.exercises?.length ?? 0),
                0
              );
              return (
                <div
                  key={w.number}
                  className="card"
                  style={{
                    cursor: soon ? "default" : "pointer",
                    opacity: soon ? 0.55 : 1,
                    borderColor: isDone ? "var(--good)" : undefined,
                  }}
                  onClick={() => !soon && nav(`${track.base}/${w.number}`)}
                >
                  <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
                    <strong>
                      {isDone && <span style={{ color: "var(--good)" }}>✓ </span>}
                      {labels.unit} {w.number}: {w.theme}
                    </strong>
                    {soon ? (
                      <span className="badge">soon</span>
                    ) : (
                      <span className="row" style={{ gap: 4, flexWrap: "wrap", justifyContent: "flex-end" }}>
                        {nLessons > 0 && <span className="badge">{nLessons} lessons</span>}
                        {nEx > 0 && <span className="badge">{nEx} exercises</span>}
                        {nPractice > 0 && (
                          <span className="badge" title="Extra variation drilling — optional">
                            🏋️ +{nPractice} practice
                          </span>
                        )}
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

function UnitDetail({
  track,
  labels,
  week,
  isDone,
  onSetDone,
  prev,
  next,
}: {
  track: Track;
  labels: Labels;
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
  // Lessons start collapsed: a unit now runs to forty-odd exercises, and each
  // open lesson mounts a Monaco editor per exercise. The contents card below is
  // how you navigate them.
  const sec = useCollapse(`course-sec:${track.key}:w${week.number}`, false);
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

  // Practice is extra drilling, deliberately outside `requiredExerciseIds`: a
  // module completes on its lessons and capstone, so adding 25 more problems
  // never moves the finish line further away.
  const practice = week.practice ?? [];
  const practiceIds = useMemo(
    () => practice.flatMap((f) => (f.exercises ?? []).map((e) => e.id)),
    [practice]
  );
  const practiceCount = practiceIds.length;
  const practiceSolved = practiceIds.filter((id) => solvedEx.has(id)).length;

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
      const head = `🎉 ${labels.unit} ${week.number} complete!`;
      toast(week.milestone ? `${head} ${week.milestone}` : head);
    }
  }, [isDone, scrolledToBottom, allSolved, onSetDone, toast, week.milestone, week.number, labels.unit]);

  const cap = week.capstone;

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4, justifyContent: "space-between" }}>
        <div className="row">
          <button className="ghost" onClick={() => nav(track.base)}>
            ← Course
          </button>
          <span className="badge">
            {labels.unit} {week.number} · {labels.group} {week.month}
          </span>
          {week.est_minutes > 0 && <span className="badge">⏱️ {studyTime(week.est_minutes)}</span>}
        </div>
        <button
          className="ghost"
          style={isDone ? { borderColor: "var(--good)", color: "var(--good)" } : undefined}
          onClick={() => onSetDone(!isDone)}
          title={isDone ? "Marked complete — click to undo" : `Mark this ${labels.unit.toLowerCase()} complete`}
        >
          {isDone ? "✓ Done" : "Mark done"}
        </button>
      </div>

      <h1 className="page-title" style={{ marginTop: 6 }}>
        {week.theme}
      </h1>

      <div className="card" style={{ marginBottom: 14, borderColor: "var(--accent)" }}>
        <div className="io-label" style={{ color: "var(--accent)" }}>
          🎯 This {labels.unit.toLowerCase()}'s goal
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
          <div className="io-label">By the end of this {labels.unit.toLowerCase()} you can…</div>
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
              📚 Lessons in this {labels.unit.toLowerCase()}
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
                {solvedLabel(lesson.exercises, solvedEx)}
              </span>
            }
          >
            <LessonBody lesson={lesson} onSolved={handleSolved} />
          </Section>
        </div>
      ))}

      {practice.length > 0 && (
        <>
          <div className="divider" />
          <h2 style={{ marginBottom: 4 }}>🏋️ Practice</h2>
          <p className="dim" style={{ marginTop: -2 }}>
            {practiceCount} extra problems in {practice.length}{" "}
            {practice.length === 1 ? "family" : "families"}. Each family drills one pattern and
            twists a single thing at a time, so no variant is a cold start. These are{" "}
            <strong>not required</strong> to finish the {labels.unit.toLowerCase()} — come back and
            grind them whenever you want the reps.
            {practiceSolved > 0 && ` You've solved ${practiceSolved} of ${practiceCount}.`}
          </p>
          {practice.map((fam) => {
            const ids = (fam.exercises ?? []).map((e) => e.id);
            const n = ids.filter((id) => solvedEx.has(id)).length;
            return (
              <div key={fam.key} id={`practice-${fam.key}`}>
                <Section
                  title={`🏋️ ${fam.title}`}
                  open={sec.isOpen(`practice:${fam.key}`)}
                  onToggle={() => sec.toggle(`practice:${fam.key}`)}
                  meta={
                    <span className="dim" style={{ fontSize: 12 }}>
                      {n}/{ids.length} solved
                    </span>
                  }
                >
                  {fam.pattern && (
                    <p className="dim" style={{ margin: "0 0 8px", fontSize: 13 }}>
                      {fam.pattern}
                    </p>
                  )}
                  {fam.intro && <Markdown>{fam.intro}</Markdown>}
                  {(fam.exercises ?? []).map((ex, i) => (
                    <ExerciseCard
                      key={ex.id}
                      index={i + 1}
                      exercise={ex}
                      challenge
                      onSolved={handleSolved}
                    />
                  ))}
                </Section>
              </div>
            );
          })}
        </>
      )}

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
                This is a free-build project — write it in the editor of your choice, then mark the{" "}
                {labels.unit.toLowerCase()} done yourself when you're happy with it.
              </p>
            )}
          </div>
          {cap.exercise && (
            <ExerciseCard index={1} exercise={cap.exercise} challenge onSolved={handleSolved} />
          )}
          {/* note="" keeps this reveal exactly as it was before the component
              was shared — the course capstone has never carried the caveat the
              other two tracks show. */}
          {cap.reference && <ReferenceReveal reference={cap.reference} note="" />}
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
          <h3>🔁 End-of-{labels.unit.toLowerCase()} review</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            A quick mixed quiz — some of these reach back to earlier {labels.units}.
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
            ? `This ${labels.unit.toLowerCase()} marks itself ✓ Done once you've read to here and solved its ${gradableIds.length} exercise${gradableIds.length === 1 ? "" : "s"}${allSolved ? " — all solved!" : ` (${solvedCount}/${gradableIds.length} solved)`}.`
            : `This ${labels.unit.toLowerCase()} marks itself ✓ Done once you've read to here.`}
        </p>
      )}

      <div className="row" style={{ marginTop: 20, justifyContent: "space-between" }}>
        {prev ? (
          <button className="ghost" onClick={() => nav(`${track.base}/${prev.number}`)}>
            ← {labels.unit} {prev.number}: {prev.theme}
          </button>
        ) : (
          <span />
        )}
        {next ? (
          <button className="primary" onClick={() => nav(`${track.base}/${next.number}`)}>
            {labels.unit} {next.number}: {next.theme} →
          </button>
        ) : (
          <button className="ghost" onClick={() => nav(track.base)}>
            Back to course overview
          </button>
        )}
      </div>

      {/* Sentinel: intersecting means the unit has been read to the bottom. */}
      <div ref={bottomRef} style={{ height: 1 }} />
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

      <ExerciseSections exercises={exercises} onSolved={onSolved} />

      {quiz.length > 0 && (
        <>
          <h4>❓ Check yourself</h4>
          <QuizSection questions={quiz} />
        </>
      )}
    </div>
  );
}
