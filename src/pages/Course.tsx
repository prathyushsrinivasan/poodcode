import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { CourseLesson, CourseWeek, WeeklyCourse } from "../types";
import { Markdown } from "../components/Markdown";
import { ExerciseCard, QuizSection, ReferenceReveal } from "../components/exercise";
import { ExerciseSections } from "../components/ExerciseSections";
import { Section, useCollapse } from "../components/Collapsible";
import {
  TrackOverview,
  UnitPager,
  type TrackGroup,
  type TrackSpec,
} from "../components/track/TrackShell";
import { useToast } from "../components/Toast";
import {
  loadDoneChapters,
  setChapterDone,
  solvedExercises,
  loadSolvedExercises,
  markExerciseSolved,
} from "../lib/learnProgress";
import { collectExerciseIds, solvedLabel, studyTime } from "../lib/trackProgress";
import { TrackSkeleton } from "../components/Skeleton";
import { Badge, Card, CardHeader, EmptyState, Icon, PageHeader } from "../components/ui";
import { Glossary, Milestone, SubHeading, UnitContents, UnitGoal, UnitList, UnitPart, scrollToPart } from "../components/track/UnitParts";
import { ReaderLayout, ReadStatus, useSeenBottom } from "../components/reader/Reader";
import { useCrumb } from "../store";
import { inlineCode } from "../components/common";
import { loadFailed } from "../lib/failures";

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
    loadDoneChapters().then(setDone).catch(loadFailed("your completed chapters"));
  }, [track]);

  async function setUnitDone(n: number, value: boolean) {
    const next = await setChapterDone(done, unitKey(track, n), value);
    setDone(next);
  }

  if (!course) return <TrackSkeleton cards={6} />;
  if (course.weeks.length === 0) {
    return (
      <div className="page">
        <EmptyState icon={track.key === "java" ? "java" : "typescript"} title={track.emptyText} />
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
          <EmptyState
            icon={track.key === "java" ? "java" : "typescript"}
            title={`${labels.unit} not found.`}
            action={{ label: "Back to the course", icon: "back", onClick: () => nav(track.base) }}
          />
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

/**
 * The course overview, on the shared track template.
 *
 * This used to be a bespoke progress card above a stack of month headings, each
 * with a two-column grid of week cards — so a 31-module course was one very long
 * page and the month you were working in was wherever you had scrolled to. The
 * template gives it the curriculum's hero and a rail of months beside one month
 * at a time (UI_ROADMAP G1).
 */
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
  const spec = useMemo<TrackSpec>(() => {
    const groups: TrackGroup[] = [];
    const seen = new Set<number>();
    for (const w of course.weeks) {
      if (!w.authored || seen.has(w.month)) continue;
      seen.add(w.month);
      groups.push({ key: String(w.month), title: w.month_title || `${labels.group} ${w.month}` });
    }
    groups.sort((a, b) => Number(a.key) - Number(b.key));

    return {
      title: course.title,
      subtitle: course.subtitle,
      base: track.base,
      unitLabel: labels.unit,
      groupLabel: labels.group,
      groups,
      units: course.weeks.map((w) => {
        const nLessons = w.lessons?.length ?? 0;
        const nEx = requiredExerciseIds(w).length;
        const nPractice = (w.practice ?? []).reduce(
          (sum, f) => sum + (f.exercises?.length ?? 0),
          0
        );
        return {
          slug: String(w.number),
          number: w.number,
          title: w.theme,
          tagline: w.goal,
          group: String(w.month),
          done: done.has(unitKey(track, w.number)),
          authored: w.authored,
          estMinutes: w.est_minutes,
          badges: (
            <>
              {nLessons > 0 && <span className="badge">{nLessons} lessons</span>}
              {nEx > 0 && <span className="badge">{nEx} exercises</span>}
              {nPractice > 0 && (
                <span className="badge" title="Extra variation drilling — optional">
                  🏋️ +{nPractice} practice
                </span>
              )}
              {w.capstone && (
                <span className="badge accent" title={w.capstone.title}>
                  🏆 project
                </span>
              )}
            </>
          ),
        };
      }),
    };
  }, [course, track, labels, done]);

  return <TrackOverview spec={spec} />;
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
  const toast = useToast();
  useCrumb(week.theme, `${labels.unit} ${week.number}`);
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const [bottomRef, seenBottom] = useSeenBottom(week.number);
  const celebrated = useRef(false);
  // Lessons start collapsed: a unit now runs to forty-odd exercises, and each
  // open lesson mounts a Monaco editor per exercise. The contents list below
  // and the outline rail are how you navigate them.
  const sec = useCollapse(`course-sec:${track.key}:w${week.number}`, false);
  const lessons = week.lessons ?? [];
  const lessonKeys = useMemo(() => lessons.map((l) => l.key), [lessons]);
  const unit = labels.unit.toLowerCase();

  function openLesson(key: string) {
    if (!sec.isOpen(key)) sec.toggle(key);
    scrollToPart(`lesson-${key}`);
  }

  const gradableIds = useMemo(() => requiredExerciseIds(week), [week]);
  const allSolved = gradableIds.every((id) => solvedEx.has(id));
  const solvedCount = gradableIds.filter((id) => solvedEx.has(id)).length;

  // Practice is extra drilling, deliberately outside `requiredExerciseIds`: a
  // module completes on its lessons and capstone, so adding 25 more problems
  // never moves the finish line further away.
  const practice = week.practice ?? [];
  const practiceIds = useMemo(() => practice.flatMap((f) => (f.exercises ?? []).map((e) => e.id)), [practice]);
  const practiceCount = practiceIds.length;
  const practiceSolved = practiceIds.filter((id) => solvedEx.has(id)).length;

  function handleSolved(id: string) {
    setSolvedEx(new Set(markExerciseSolved(id)));
  }

  // Hydrate the solved set from SQLite. The initialiser above reads a
  // module-level cache — warm after the first load of the session — and this
  // is what fills it on a cold start.
  useEffect(() => {
    loadSolvedExercises().then(setSolvedEx).catch(loadFailed("your solved exercises"));
  }, []);

  useEffect(() => {
    if (!isDone && seenBottom && allSolved && !celebrated.current) {
      celebrated.current = true;
      onSetDone(true);
      const head = `${labels.unit} ${week.number} complete!`;
      toast.success(week.milestone ? `${head} ${week.milestone}` : head);
    }
  }, [isDone, seenBottom, allSolved, onSetDone, toast, week.milestone, week.number, labels.unit]);

  const steps = [
    { label: "Read to the end", met: seenBottom || isDone },
    ...(gradableIds.length > 0
      ? [{ label: `Solve the exercises (${solvedCount}/${gradableIds.length})`, met: allSolved }]
      : []),
  ];

  const cap = week.capstone;

  return (
    <div className="page course-unit">
      <ReaderLayout aside={<ReadStatus steps={steps} complete={isDone} onToggle={() => onSetDone(!isDone)} />}>
        <PageHeader
          eyebrow={
            <>
              {labels.unit} {week.number} · {labels.group} {week.month}
              {week.est_minutes > 0 && (
                <>
                  {" "}
                  · <Icon name="clock" size={12} /> {studyTime(week.est_minutes)}
                </>
              )}
            </>
          }
          title={week.theme}
        />

        <UnitGoal label={`This ${unit}'s goal`} goal={week.goal} why={week.why} />
        <UnitList label={`By the end of this ${unit} you can…`} items={week.objectives} />
        {week.summary && <Markdown>{week.summary}</Markdown>}

        <UnitContents
          title={`Lessons in this ${unit}`}
          rows={lessons.map((l) => {
            const ids = (l.exercises ?? []).map((e) => e.id);
            return { key: l.key, title: l.title, what: l.what, solved: ids.filter((id) => solvedEx.has(id)).length, total: ids.length };
          })}
          onOpen={openLesson}
          onExpandAll={() => sec.setAll(lessonKeys, true)}
          onCollapseAll={() => sec.setAll(lessonKeys, false)}
        />

        {lessons.map((lesson, li) => (
          <div key={lesson.key} id={`lesson-${lesson.key}`}>
            <Section
              title={`${li + 1}. ${lesson.title}`}
              outline={lesson.title}
              open={sec.isOpen(lesson.key)}
              onToggle={() => sec.toggle(lesson.key)}
              meta={<span className="learn-cat-count">{solvedLabel(lesson.exercises, solvedEx)}</span>}
            >
              <LessonBody lesson={lesson} onSolved={handleSolved} />
            </Section>
          </div>
        ))}

        {practice.length > 0 && (
          <UnitPart
            title="Practice"
            icon="target"
            lead={
              <>
                {practiceCount} extra problems in {practice.length} {practice.length === 1 ? "family" : "families"}.
                Each family drills one pattern and twists a single thing at a time, so no variant is a cold start. They
                are <strong>not required</strong> to finish the {unit} — come back for the reps whenever you want them.
                {practiceSolved > 0 && ` You've solved ${practiceSolved} of ${practiceCount}.`}
              </>
            }
          >
            {practice.map((fam) => {
              const ids = (fam.exercises ?? []).map((e) => e.id);
              const n = ids.filter((id) => solvedEx.has(id)).length;
              return (
                <div key={fam.key} id={`practice-${fam.key}`}>
                  <Section
                    title={fam.title}
                    outline={false}
                    level="h4"
                    open={sec.isOpen(`practice:${fam.key}`)}
                    onToggle={() => sec.toggle(`practice:${fam.key}`)}
                    meta={
                      <span className="learn-cat-count">
                        {n}/{ids.length} solved
                      </span>
                    }
                  >
                    {fam.pattern && <p className="section-lead">{fam.pattern}</p>}
                    {fam.intro && <Markdown>{fam.intro}</Markdown>}
                    {(fam.exercises ?? []).map((ex, i) => (
                      <ExerciseCard key={ex.id} index={i + 1} exercise={ex} challenge onSolved={handleSolved} />
                    ))}
                  </Section>
                </div>
              );
            })}
          </UnitPart>
        )}

        {cap && (
          <UnitPart title="Capstone project" icon="trophy">
            <Card tone="accent" className="unit-block">
              <CardHeader level={3} title={cap.title} />
              <Markdown>{cap.brief}</Markdown>
              {cap.example_io && (
                <>
                  <div className="io-label">Expected output</div>
                  <Markdown>{"```\n" + cap.example_io + "\n```"}</Markdown>
                </>
              )}
              {cap.rubric.length > 0 && (
                <>
                  <div className="io-label">Checklist</div>
                  <ul className="unit-list">
                    {cap.rubric.map((r, i) => (
                      <li key={i}>{inlineCode(r)}</li>
                    ))}
                  </ul>
                </>
              )}
              {cap.kind === "brief" && (
                <p className="exercise-note">
                  A free-build project — write it in the editor of your choice, then mark the {unit} done yourself when
                  you're happy with it.
                </p>
              )}
            </Card>
            {cap.exercise && <ExerciseCard index={1} exercise={cap.exercise} challenge onSolved={handleSolved} />}
            {/* note="" keeps this reveal as it was before the component was
                shared — the course capstone never carried the caveat. */}
            {cap.reference && <ReferenceReveal reference={cap.reference} note="" />}
            {cap.stretch && (
              <>
                <SubHeading icon="sparkles">Stretch goal (optional)</SubHeading>
                <ExerciseCard index={1} exercise={cap.stretch} challenge onSolved={handleSolved} />
              </>
            )}
          </UnitPart>
        )}

        {week.self_check.length > 0 && (
          <UnitPart
            title="Self-check"
            icon="checklist"
            lead="Before you move on, make sure you can honestly say yes to each of these:"
          >
            <UnitList items={week.self_check} />
          </UnitPart>
        )}

        {week.review.length > 0 && (
          <UnitPart
            title={`End-of-${unit} review`}
            outline="Review"
            icon="refresh"
            lead={`A quick mixed quiz — some of these reach back to earlier ${labels.units}.`}
          >
            <QuizSection questions={week.review} />
          </UnitPart>
        )}

        {week.glossary.length > 0 && (
          <Section
            title="Glossary"
            open={sec.isOpen("glossary")}
            onToggle={() => sec.toggle("glossary")}
            meta={<Badge>{week.glossary.length} terms</Badge>}
          >
            <Glossary terms={week.glossary} />
          </Section>
        )}

        {week.cheatsheet && (
          <Section title="Cheat sheet" open={sec.isOpen("cheatsheet")} onToggle={() => sec.toggle("cheatsheet")}>
            <Markdown>{week.cheatsheet}</Markdown>
          </Section>
        )}

        {week.milestone && <Milestone text={week.milestone} />}

        <div className="concept-end">
          <ReadStatus steps={steps} complete={isDone} compact />
        </div>

        <UnitPager
          base={track.base}
          unitLabel={labels.unit}
          prev={prev ? { slug: String(prev.number), number: prev.number, title: prev.theme } : null}
          next={next ? { slug: String(next.number), number: next.number, title: next.theme } : null}
          backTo={track.base}
          backLabel={`All ${labels.group.toLowerCase()}s`}
        />

        {/* Sentinel: intersecting means the unit has been read to the bottom. */}
        <div ref={bottomRef} className="read-sentinel" />
      </ReaderLayout>
    </div>
  );
}

function LessonBody({ lesson, onSolved }: { lesson: CourseLesson; onSolved: (id: string) => void }) {
  const exercises = lesson.exercises ?? [];
  const warmup = lesson.warmup ?? [];
  const quiz = lesson.quiz ?? [];

  return (
    <div className="lesson-body">
      {lesson.what && <p className="section-lead">{lesson.what}</p>}
      <Markdown>{lesson.lesson}</Markdown>

      {warmup.length > 0 && (
        <>
          <SubHeading icon="sparkles">Predict the output</SubHeading>
          <p className="section-lead">Read the code and guess what it prints — then check.</p>
          <QuizSection questions={warmup} />
        </>
      )}

      <ExerciseSections exercises={exercises} onSolved={onSolved} />

      {quiz.length > 0 && (
        <>
          <SubHeading icon="help">Check yourself</SubHeading>
          <QuizSection questions={quiz} />
        </>
      )}
    </div>
  );
}
