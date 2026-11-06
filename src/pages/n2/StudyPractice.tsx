import { Link, useNavigate, useParams } from "react-router-dom";
import { Button, Card, PageHeader } from "../../components/ui";
import { JLPT_PRACTICE } from "../../data/jlptSections";
import { STUDY_LESSONS, STUDY_LESSON_MAP, STUDY_QUESTIONS } from "../../data/n2Study";
import { beginQuestions, selectRound, startSession } from "../../lib/n2Study";
import { useN2Study, type N2StudyController } from "../../lib/useN2Study";
import { LessonBody, StudyStatus, STUDY_ROOT } from "./StudyShared";
import { useCrumb } from "../../store";
import GrammarReference from "./GrammarReference";
import { useJlptPreference } from "../../lib/useJlptPractice";
import { RoundSize } from "./StudyWorkspace";

export function StudyPracticePage() {
  const { practiceId } = useParams();
  const practice = Object.entries(JLPT_PRACTICE).find(([id]) => id === practiceId)?.[1];
  useCrumb(practice?.title ?? null);
  const state = useN2Study();
  return <div className="page n2-page study-page">
    <Link className="ghost-link" to={STUDY_ROOT}>← JLPT</Link>
    <PageHeader title={practice?.title ?? "Practice not found"} subtitle={practice ? "Practice a short round, then review each answer." : "Choose a practice type from JLPT."} />
    <StudyStatus state={state} />
    {practice && state.data && <PracticeContent key={practiceId} state={state as N2StudyController} title={practice.title} lessonIds={practice.lessonIds} />}
  </div>;
}

function PracticeContent({ state, title, lessonIds }: { state: N2StudyController; title: string; lessonIds: string[] }) {
  const navigate = useNavigate();
  const [timed, setTimed] = useJlptPreference(title, "timed", false);
  const [lessonFilter, setLessonFilter] = useJlptPreference(title, "lesson", "");
  const [topicFilter, setTopicFilter] = useJlptPreference(title, "topic", "");
  const [groupFilter, setGroupFilter] = useJlptPreference(title, "group", "");
  const [exerciseFilter, setExerciseFilter] = useJlptPreference(title, "exercise", "");
  const [kindFilter, setKindFilter] = useJlptPreference(title, "kind", lessonIds.includes("reading-choice") && lessonIds.length > 1 ? "typed" : "");
  const available = STUDY_QUESTIONS.filter((q) => lessonIds.includes(q.lessonId));
  const topics = [...new Set(available.flatMap((q) => q.tags.filter((tag) => tag.startsWith("topic:")).map((tag) => tag.slice(6))))].sort();
  const groups = [...new Set(available.flatMap((q) => q.tags.filter((tag) => tag.startsWith("group:")).map((tag) => tag.slice(6))))].sort();
  const exercises = [...new Set(available.flatMap((q) => q.tags.filter((tag) => tag.startsWith("exercise:")).map((tag) => tag.slice(9))))].sort();
  const pool = available.filter((q) => (!lessonFilter || q.lessonId === lessonFilter) && (!kindFilter || q.kind === kindFilter) && (!topicFilter || q.tags.includes(`topic:${topicFilter}`)) && (!groupFilter || q.tags.includes(`group:${groupFilter}`)) && (!exerciseFilter || q.tags.includes(`exercise:${exerciseFilter}`)));
  const ids = selectRound(state.data, pool, state.data.preferences.roundSize);
  const active = state.data.session && state.data.session.phase !== "summary";
  const lessons = STUDY_LESSONS.filter((lesson) => lessonIds.includes(lesson.id));
  function start() {
    if (!active) state.update((p) => beginQuestions(startSession(p, ids, timed ? "timed" : "learn", title)));
    navigate(`${STUDY_ROOT}/study`);
  }
  return <>
    <Card>
      <p>{active ? "You have a saved round. Finish it before starting another." : `${ids.length} questions this round · ${pool.length} available · Answers and explanations included.`}</p>
      {!active && <label className="dokkai-check"><input type="checkbox" checked={timed} onChange={(e) => setTimed(e.target.checked)} />Timed practice</label>}
      {!active && <details className="jlpt-tips"><summary>Practice options</summary>
        <RoundSize state={state} />
        <label className="study-field">Focus<select aria-label="Focus" value={lessonFilter} onChange={(e) => { setLessonFilter(e.target.value); setKindFilter(""); }}>
          <option value="">All drills</option>{lessons.map((l) => <option key={l.id} value={l.id}>{l.format}</option>)}
        </select></label>
        {topics.length > 0 && <label className="study-field">Topic<select aria-label="Topic" value={topicFilter} onChange={(e) => setTopicFilter(e.target.value)}>
          <option value="">All topics</option>{topics.map((topic) => <option key={topic}>{topic}</option>)}
        </select></label>}
        {groups.length > 0 && <label className="study-field">Meaning group<select aria-label="Meaning group" value={groupFilter} onChange={(e) => setGroupFilter(e.target.value)}>
          <option value="">All groups</option>{groups.map((group) => <option key={group}>{group}</option>)}
        </select></label>}
        {exercises.length > 0 && <label className="study-field">Exercise<select aria-label="Exercise" value={exerciseFilter} onChange={(e) => setExerciseFilter(e.target.value)}>
          <option value="">All exercises</option>{exercises.map((exercise) => <option key={exercise}>{exercise}</option>)}
        </select></label>}
        {STUDY_QUESTIONS.some((q) => lessonIds.includes(q.lessonId) && q.kind === "typed") && <label className="study-field">Answer format<select aria-label="Answer format" value={kindFilter} onChange={(e) => setKindFilter(e.target.value)}>
          <option value="">All formats</option><option value="typed">Type the reading</option><option value="choice">Choose the reading</option>
        </select></label>}
        {!pool.length && <p role="status">No questions match. Choose another focus or answer format.</p>}
      </details>}
      <div className="n2-actions jlpt-start"><Button variant="primary" disabled={!active && !ids.length} onClick={start}>{active ? "Continue saved round" : "Start practice"} →</Button></div>
    </Card>
    {lessonIds.includes("reading-choice") && <p><Link to={`${STUDY_ROOT}/kanji`}>Open Word Builder · 820 words →</Link></p>}
    {lessonIds.includes("assembly-links") && <p><Link to={`${STUDY_ROOT}/sentence-order`}>Full Sentence Order course &amp; strategies →</Link></p>}
    {lessons.some((l) => l.section === "grammar") && <GrammarReference />}
    <details className="card jlpt-tips"><summary>Study tips &amp; examples</summary>
      {lessons.map((lesson) => <section key={lesson.id}><LessonBody lesson={lesson} />
        {lesson.next && <Link to={lesson.next.href}>{lesson.next.label} →</Link>}</section>)}
      {lessonIds.includes("context") && <Link to={`${STUDY_ROOT}/patterns`}>More kanji &amp; vocabulary patterns →</Link>}
    </details>
  </>;
}

/** Keep saved lesson links working without returning to the former tab menus. */
export function StudyLessonPage() {
  const state = useN2Study();
  const { lessonId } = useParams();
  const lesson = STUDY_LESSON_MAP.get(lessonId ?? "");
  useCrumb(lesson?.format ?? null);
  return <div className="page n2-page study-page">
    <Link className="ghost-link" to={STUDY_ROOT}>← JLPT</Link>
    <PageHeader title={lesson?.format ?? "Lesson not found"} />
    <StudyStatus state={state} />
    {lesson && state.data && <PracticeContent key={lesson.id} state={state as N2StudyController} title={lesson.format} lessonIds={[lesson.id]} />}
  </div>;
}
