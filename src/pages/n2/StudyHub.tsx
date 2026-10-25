import { useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { Badge, Button, Card, PageHeader, ProgressBar, TabPanel, Tabs } from "../../components/ui";
import { STUDY_LESSONS, STUDY_LESSON_MAP, STUDY_QUESTION_MAP, STUDY_QUESTIONS, STUDY_SECTIONS, type StudySection } from "../../data/n2Study";
import { dailyStats, daysToExam, localDay, questionSection, reviewQuestions, sectionStats, selectRound, startSession, validExamDate, weakestSection, type ReviewFilter, type StudyMode, type StudyState } from "../../lib/n2Study";
import { useN2Study, type N2StudyController } from "../../lib/useN2Study";
import { AnswerExplanation, formatTime, LessonBody, LibraryLink, QuestionLabel, QuestionTexts, StudyStatus, STUDY_ROOT } from "./StudyShared";

const TABS = [{ key: "today", label: "Today" }, { key: "practice", label: "Learn & practice" }, { key: "review", label: "Review" }, { key: "progress", label: "Progress" }, { key: "plan", label: "Study plan" }];
export default function StudyHub() {
  const state = useN2Study();
  const [params, setParams] = useSearchParams();
  const tab = TABS.some((t) => t.key === params.get("tab")) ? params.get("tab")! : "today";
  return <div className="page n2-page study-page">
    <PageHeader eyebrow="日本語 · A little every day" title="JLPT N2 study space" subtitle="Understand the idea. Try it yourself. Bring back what needs another look." actions={<LibraryLink />} />
    <StudyStatus state={state} />
    {state.data && <>
      <Tabs idBase="n2-study" tabs={TABS} active={tab} onChange={(value) => setParams({ tab: value })} />
      <TabPanel idBase="n2-study" active={tab}>
        <HubContent state={state as N2StudyController} tab={tab} />
      </TabPanel>
    </>}
  </div>;
}
function useStart(state: N2StudyController) {
  const navigate = useNavigate();
  return (ids: string[], mode: StudyMode, title: string) => {
    if (!ids.length) return;
    if (state.data.session && state.data.session.phase !== "summary") { navigate(`${STUDY_ROOT}/study`); return; }
    state.update((p) => startSession(p, ids, mode, title));
    navigate(`${STUDY_ROOT}/study`);
  };
}
function HubContent({ state, tab }: { state: N2StudyController; tab: string }) {
  const start = useStart(state);
  const active = state.data.session && state.data.session.phase !== "summary" ? state.data.session : null;
  return <div className="study-stack">
    {active && <Card className="study-resume" tone="accent"><div><strong>A round is waiting for you</strong><p>{active.title} · question {active.position + 1}/{active.questionIds.length}{active.mode === "timed" ? " · its timer continues" : " · your place is saved"}</p></div>
      <Link className="btn primary" to={`${STUDY_ROOT}/study`}>Continue round →</Link></Card>}
    {tab === "today" && <Today state={state} start={start} />}
    {tab === "practice" && <Practice state={state} start={start} />}
    {tab === "review" && <Review state={state} start={start} />}
    {tab === "progress" && <Progress state={state} />}
    {tab === "plan" && <Plan state={state} />}
    <p className="study-footnote">Original preparation material · {STUDY_QUESTIONS.length} sample questions across six sections · Works offline. Practice percentages are not JLPT scaled scores.</p>
  </div>;
}
type Start = (ids: string[], mode: StudyMode, title: string) => void;
function Today({ state, start }: { state: N2StudyController; start: Start }) {
  const p = state.data; const today = dailyStats(p); const days = daysToExam(p.preferences.examDate);
  const active = p.session && p.session.phase !== "summary";
  const due = reviewQuestions(p, "due"); const weak = weakestSection(p);
  const pool = weak ? STUDY_QUESTIONS.filter((q) => questionSection(q) === weak) : STUDY_QUESTIONS;
  const next = selectRound(p, pool, p.preferences.roundSize);
  const diagnostic = STUDY_SECTIONS.map((s) => selectRound(p, STUDY_QUESTIONS.filter((q) => questionSection(q) === s.id), 1)[0]);
  return <>
    <Card className="study-hero">
      <div><Badge tone="accent">Your next small step</Badge><h2>{due.length ? "Make yesterday's learning stick" : weak ? `A little attention for ${STUDY_SECTIONS.find((s) => s.id === weak)!.title.toLowerCase()}` : "Start with one idea, then try it"}</h2>
        <p>{due.length ? `${due.length} questions are ready for a spaced review. Recall first, then check the explanation.` : "A short lesson, a handful of questions, and a clear explanation for every answer."}</p>
        <div className="n2-actions"><Button variant="primary" onClick={() => start(due.length ? due.slice(0, p.preferences.roundSize).map((q) => q.id) : next, "learn", due.length ? "Today's spaced review" : "Today's focused practice")}>{active ? "Continue your round" : due.length ? `Review ${Math.min(due.length, p.preferences.roundSize)} due questions` : `Start ${next.length}-question practice`} →</Button>
          <Link className="ghost-link" to={`${STUDY_ROOT}?tab=practice`}>Choose a section</Link></div>
      </div><div className="study-hero-date"><strong>{days === null ? "Your pace" : days < 0 ? "Keep going" : `${days}`}</strong><span>{days !== null && days >= 0 ? "days to your exam" : "one day at a time"}</span><Link to={`${STUDY_ROOT}?tab=plan`}>Adjust your plan</Link></div>
    </Card>
    <div className="study-stats"><Stat label="Questions today" value={String(today.unique)} detail={`${today.correct} independent correct attempts`} /><Stat label="Study time today" value={`${Math.floor(today.seconds / 60)} min`} detail={`${p.preferences.dailyMinutes}-minute daily goal`} /><Stat label="Reviews ready" value={String(due.length)} detail="Due from earlier practice" /><Stat label="Current streak" value={`${today.streak} ${today.streak === 1 ? "day" : "days"}`} detail="Based on completed answers" /></div>
    <Card><div className="study-spread"><h2>Today's rhythm</h2><span className="n2-meta">{p.preferences.dailyMinutes} minutes · take breaks as needed</span></div>
      <DailyRhythm minutes={p.preferences.dailyMinutes} />
      <ProgressBar value={Math.floor(today.seconds / 60)} max={p.preferences.dailyMinutes} label="Today's study minutes" />
      <p className="n2-meta">Time counts while answering. Mini lessons and off-app study are extra.</p>
    </Card>
    <div className="study-two-columns"><Card><h2>Get a starting picture</h2><p>A six-question timed sampler touches every section. Use it to spot what needs attention; this small bank cannot predict your exam score.</p>
      <Button onClick={() => start(diagnostic, "timed", "Six-section diagnostic sampler")}>Try the diagnostic sampler</Button></Card>
      <Card><h2>Know what your progress means</h2><p>First recall schedules a review tomorrow, then after three days, then seven. An early repeat does not move you ahead. Misses, help and guesses return to a short interval.</p><Link to={`${STUDY_ROOT}?tab=progress`}>See section progress →</Link></Card></div>
    {p.session?.phase === "summary" && <Link className="ghost-link" to={`${STUDY_ROOT}/study`}>Reopen your latest round recap →</Link>}
  </>;
}
function Stat({ label, value, detail }: { label: string; value: string; detail: string }) { return <div className="card study-stat"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>; }
function DailyRhythm({ minutes }: { minutes: number }) {
  const vocabulary = Math.round(minutes * .2); const grammar = Math.round(minutes * .25); const reading = Math.round(minutes * .35); const review = minutes - vocabulary - grammar - reading;
  return <ol className="study-rhythm">{[[vocabulary, "Kanji & vocabulary", "Recall compounds and useful collocations"], [grammar, "Grammar & assembly", "Learn one contrast, then use it"], [reading, "Reading & text grammar", "Find the evidence behind your answer"], [review, "Review & notes", "Turn one mistake into a useful clue"]].map(([time, title, detail], i) => <li key={title}><span className="study-step-number">{i + 1}</span><div><strong>{title}</strong><small>{detail}</small></div><span>{time} min</span></li>)}</ol>;
}
function Practice({ state, start }: { state: N2StudyController; start: Start }) {
  const [section, setSection] = useState<StudySection | "all">("all");
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<StudyMode>("learn");
  const [size, setSize] = useState(state.data.preferences.roundSize);
  const normalized = query.trim().toLowerCase();
  const lessons = STUDY_LESSONS.filter((l) => (section === "all" || l.section === section) && `${l.title} ${l.format} ${l.takeaway} ${l.examples.map((e) => e.japanese).join(" ")}`.toLowerCase().includes(normalized));
  const pool = STUDY_QUESTIONS.filter((q) => lessons.some((l) => l.id === q.lessonId));
  const ids = selectRound(state.data, pool, size);
  const budget = ids.reduce((sum, id) => sum + STUDY_QUESTION_MAP.get(id)!.targetSeconds, 0);
  return <>
    <div><h2 className="study-section-heading">Build understanding, one format at a time</h2><p className="n2-meta">Choose a mini lesson or mix the matching sample questions into a round.</p></div>
    <div className="study-section-filters" aria-label="Study section"><Button size="sm" aria-pressed={section === "all"} onClick={() => setSection("all")}>All sections</Button>{STUDY_SECTIONS.map((s) => <Button key={s.id} size="sm" aria-pressed={section === s.id} onClick={() => setSection(s.id)}>{s.title}</Button>)}</div>
    <Card className="study-round-setup"><label className="study-field">Find a lesson<input type="search" placeholder="e.g. paraphrases, わけ, paired texts" value={query} onChange={(e) => setQuery(e.target.value)} /></label>
      <label className="study-field">Practice mode<select value={mode} onChange={(e) => setMode(e.target.value as StudyMode)}><option value="learn">Learn & practice · explanations after each answer</option><option value="timed">Timed · explanations after the round</option></select></label>
      <label className="study-field">Round size<select value={size} onChange={(e) => setSize(Number(e.target.value))}>{[3, 5, 10, 20].map((n) => <option key={n} value={n}>{n} questions</option>)}</select></label>
      <div className="n2-actions"><Button variant="primary" disabled={!ids.length} onClick={() => start(ids, mode, section === "all" ? "Mixed section practice" : `${STUDY_SECTIONS.find((s) => s.id === section)!.title} practice`)}>Start {ids.length}-question round</Button><span className="n2-meta">{mode === "timed" ? `${formatTime(budget)} total · fixed deadline` : "No time pressure · hints available"}</span></div>
    </Card>
    {!lessons.length && <Card><h2>No matching lessons</h2><p>Try another term or choose all sections.</p><Button onClick={() => { setQuery(""); setSection("all"); }}>Clear filters</Button></Card>}
    <div className="study-lesson-grid">{lessons.map((l) => {
      const questions = STUDY_QUESTIONS.filter((q) => q.lessonId === l.id); const seen = questions.filter((q) => state.data.reviews[q.id]).length;
      return <Link to={`${STUDY_ROOT}/lesson/${l.id}`} key={l.id} className="card study-lesson-link"><div className="study-spread"><span className="study-japanese" lang="ja">{STUDY_SECTIONS.find((s) => s.id === l.section)!.japanese}</span>{state.data.learned.includes(l.id) && <Badge tone="good">Lesson read</Badge>}</div>
        <h2>{l.title}</h2><p>{l.takeaway}</p><div className="study-lesson-bottom"><span className="n2-meta">{questions.length} sample questions · {seen} practiced</span><strong>Learn &amp; try →</strong></div></Link>;
    })}</div>
  </>;
}
function Review({ state, start }: { state: N2StudyController; start: Start }) {
  const [filter, setFilter] = useState<ReviewFilter>("due"); const [query, setQuery] = useState("");
  const filters: { id: ReviewFilter; label: string; description: string }[] = [
    { id: "due", label: "Due now", description: "Questions whose review interval has arrived." },
    { id: "mistakes", label: "Mistakes & help", description: "Latest attempts that were missed, revealed or completed with help." },
    { id: "confident", label: "Confident misses", description: "You felt sure, but the latest answer was wrong. Check the assumption behind it." },
    { id: "slow", label: "Slow answers", description: "Latest attempts that took longer than the suggested practice target." },
    { id: "saved", label: "Saved", description: "Questions you bookmarked for another look." },
  ];
  const questions = reviewQuestions(state.data, filter).filter((q) => `${q.prompt} ${STUDY_LESSON_MAP.get(q.lessonId)!.title} ${state.data.notes[q.id]?.text ?? ""} ${state.data.notes[q.id]?.reason ?? ""}`.toLowerCase().includes(query.toLowerCase().trim()));
  return <>
    <div><h2 className="study-section-heading">Let mistakes tell you what to learn next</h2><p className="n2-meta">Recall an answer before opening its explanation. Each question keeps one shared review schedule.</p></div>
    <div className="study-section-filters" aria-label="Review queue">{filters.map((f) => <Button key={f.id} size="sm" aria-pressed={filter === f.id} onClick={() => setFilter(f.id)}>{f.label} · {reviewQuestions(state.data, f.id).length}</Button>)}</div>
    <Card className="study-review-toolbar"><div><h2>{filters.find((f) => f.id === filter)!.label}</h2><p>{filters.find((f) => f.id === filter)!.description}</p></div>
      <label className="study-field">Search questions &amp; notes<input type="search" value={query} onChange={(e) => setQuery(e.target.value)} /></label>
      <Button variant="primary" disabled={!questions.length} onClick={() => start(questions.slice(0, state.data.preferences.roundSize).map((q) => q.id), "learn", `${filters.find((f) => f.id === filter)!.label} review`)}>Review {Math.min(questions.length, state.data.preferences.roundSize)} questions</Button></Card>
    {!questions.length && <Card><h2>{filter === "due" ? "Nothing due right now" : "No matching questions yet"}</h2><p>{filter === "due" ? "New reviews appear after practice. You can learn a new format or revisit a saved question in the meantime." : "Try another queue or search. This list will grow as you practice."}</p><Link to={`${STUDY_ROOT}?tab=practice`}>Choose a mini lesson →</Link></Card>}
    <div className="study-stack">{questions.map((q) => {
      const result = [...state.data.attempts].reverse().find((a) => a.questionId === q.id);
      return <details className="card study-recap-item" key={q.id}><summary><QuestionLabel id={q.id} /><Badge>{state.data.notes[q.id]?.reason || "Open review"}</Badge></summary>
        <div className="n2-actions"><Button size="sm" onClick={() => start([q.id], "learn", "Single-question recall")}>Try without looking</Button><Button variant="ghost" size="sm" aria-pressed={state.data.bookmarks.includes(q.id)} onClick={() => state.update((p) => ({ ...p, bookmarks: p.bookmarks.includes(q.id) ? p.bookmarks.filter((id) => id !== q.id) : [...p.bookmarks, q.id] }))}>{state.data.bookmarks.includes(q.id) ? "Remove from saved" : "Save question"}</Button></div>
        {result ? <><QuestionTexts question={q} review /><AnswerExplanation question={q} result={result} state={state} /></> : <p>Saved before your first attempt. Try it to create a review schedule.</p>}
      </details>;
    })}</div>
  </>;
}
function Progress({ state }: { state: N2StudyController }) {
  const p = state.data; const weak = weakestSection(p); const totalSeen = Object.keys(p.reviews).filter((id) => STUDY_QUESTION_MAP.has(id)).length;
  const activity = Array.from({ length: 7 }, (_, i) => { const d = new Date(); d.setDate(d.getDate() - 6 + i); const key = localDay(d.getTime()); return { label: d.toLocaleDateString(undefined, { weekday: "short" }), count: p.attempts.filter((a) => localDay(a.at) === key).length }; });
  return <>
    <Card><h2>Understanding takes more than one correct answer</h2><p>{totalSeen} of {STUDY_QUESTIONS.length} sample questions practiced. “Retained” means three successful, spaced recalls. Assisted answers and guesses never advance retention.</p><ProgressBar value={totalSeen} max={STUDY_QUESTIONS.length} label="Sample question coverage" />
      <p className="n2-meta">{weak ? `Suggested focus: ${STUDY_SECTIONS.find((s) => s.id === weak)!.title}.` : "Complete at least three independent attempts in a section to get a suggested focus."} Accuracy uses up to the latest 3,000 attempts; lifetime review counts stay saved.</p></Card>
    <div className="study-lesson-grid">{STUDY_SECTIONS.map((s) => { const stats = sectionStats(p, s.id); return <Card key={s.id}><div className="study-spread"><h2>{s.title}</h2><Badge>{stats.accuracy === null ? "No attempts" : `${stats.accuracy}% independent`}</Badge></div>
      <p className="n2-meta">{stats.seen}/{stats.total} practiced · {stats.retained} retained · {stats.due} due</p><ProgressBar value={stats.retained} max={stats.total} label={`${s.title}: retained after spaced reviews`} />
      <p>{stats.attempts} independent attempts · {stats.averageSeconds}s average per answer</p></Card>; })}</div>
    <Card><h2>Your last seven days</h2><div className="study-activity">{activity.map((day, i) => <div key={i}><span>{day.label}</span><progress max={Math.max(1, ...activity.map((d) => d.count))} value={day.count} aria-label={`${day.label}: ${day.count} attempts`} /><strong>{day.count}</strong></div>)}</div></Card>
    <Card><h2>Recent practice</h2>{p.attempts.length ? <ol className="study-history">{p.attempts.slice(-12).reverse().map((a) => <li key={a.id}><div><span className="n2-meta">{new Date(a.at).toLocaleString()} · {a.mode === "timed" ? "Timed" : "Guided"}</span><p><QuestionLabel id={a.questionId} /></p></div><Badge tone={a.correct && !a.assisted ? "good" : "warn"}>{a.correct ? a.assisted ? "With help" : "Correct" : "Revisit"}</Badge></li>)}</ol> : <p>Your completed answers will appear here.</p>}</Card>
  </>;
}
function Plan({ state }: { state: N2StudyController }) {
  const [date, setDate] = useState(state.data.preferences.examDate); const [minutes, setMinutes] = useState(state.data.preferences.dailyMinutes); const [size, setSize] = useState(state.data.preferences.roundSize); const [saved, setSaved] = useState(false);
  const days = daysToExam(state.data.preferences.examDate);
  const valid = (date === "" || validExamDate(date)) && Number.isInteger(minutes) && minutes >= 10 && minutes <= 240;
  const phases = [
    { title: "1 · Diagnose & build a routine", range: "30–22 days left", focus: "Sample every format. Identify three recurring errors. Learn one small contrast each day and keep reading daily.", task: "Take a timed sampler and write one concrete clue for every missed answer." },
    { title: "2 · Repair the weak spots", range: "21–15 days left", focus: "Spend extra time on your weakest formats. Pair grammar patterns, practice useful vocabulary combinations, and keep up with due reviews.", task: "Explain why each incorrect option fails before moving on." },
    { title: "3 · Work under time pressure", range: "14–8 days left", focus: "Mix formats and use timed sets. Take a full-length practice paper from a suitable external source; review it on a separate day.", task: "Try a personal split of 35 minutes language knowledge, 65 reading and 5 checking. Adjust it using your results." },
    { title: "4 · Consolidate & arrive rested", range: "7–0 days left", focus: "Revisit confident misses and recurring notes. Take your final mock early in the week. Keep the final two days light.", task: "Prepare a one-page reminder of your own patterns, timing checkpoints and recurring traps." },
  ];
  const phase = days === null || days > 30 ? -1 : days > 21 ? 0 : days > 14 ? 1 : days > 7 ? 2 : days >= 0 ? 3 : -1;
  return <>
    <Card><h2>A plan you can actually repeat</h2><form className="study-plan-form" onSubmit={(e) => { e.preventDefault(); if (valid) { state.update((p) => ({ ...p, preferences: { examDate: date, dailyMinutes: minutes, roundSize: size } })); setSaved(true); } }}>
      <label className="study-field">Exam date<input type="date" value={date} onChange={(e) => { setDate(e.target.value); setSaved(false); }} /></label>
      <label className="study-field">Daily study minutes<input type="number" min={10} max={240} step={5} value={Number.isNaN(minutes) ? "" : minutes} onChange={(e) => { setMinutes(e.target.valueAsNumber); setSaved(false); }} /></label>
      <label className="study-field">Default quick round<select value={size} onChange={(e) => { setSize(Number(e.target.value)); setSaved(false); }}>{[3, 5, 10, 20].map((n) => <option key={n} value={n}>{n} questions</option>)}</select></label>
      <div className="n2-actions"><Button type="submit" variant="primary" disabled={!valid}>Save study plan</Button>{saved && <span role="status">Plan updated</span>}</div>
    </form><p className="n2-meta">The countdown uses your device's local calendar date. You can leave the exam date blank.</p></Card>
    <Card><h2>Your daily rhythm · {state.data.preferences.dailyMinutes} minutes</h2><DailyRhythm minutes={state.data.preferences.dailyMinutes} /></Card>
    <div className="study-plan-phases">{phases.map((p, i) => <Card key={p.title} tone={phase === i ? "accent" : undefined}><div className="study-spread"><Badge>{p.range}</Badge>{phase === i && <Badge tone="accent">Your current phase</Badge>}</div><h2>{p.title}</h2><p>{p.focus}</p><p className="study-callout"><strong>Practical task:</strong> {p.task}</p></Card>)}</div>
    <Card><h2>Practice the real time constraint</h2><p>Language knowledge and reading share 105 minutes. Protect reading time and skip a stubborn question temporarily. In reading, find the evidence; in information search, check every condition and exception.</p>
      <p>This hub offers short practice rounds. Use the existing reading library for longer sets and an official practice workbook for a full paper.</p>
      <a href="https://www.jlpt.jp/e/guideline/testsections.html" target="_blank" rel="noreferrer">Official test formats &amp; timing ↗</a></Card>
  </>;
}
export function StudyLessonPage() {
  const state = useN2Study(); const { lessonId } = useParams();
  return <div className="page n2-page study-page"><Link className="ghost-link" to={`${STUDY_ROOT}?tab=practice`}>← Learn &amp; practice</Link><StudyStatus state={state} />
    {state.data && <LessonPageContent state={state as N2StudyController} lessonId={lessonId ?? ""} />}</div>;
}
function LessonPageContent({ state, lessonId }: { state: N2StudyController; lessonId: string }) {
  const start = useStart(state); const lesson = STUDY_LESSON_MAP.get(lessonId);
  const [mode, setMode] = useState<StudyMode>("learn");
  if (!lesson) return <><PageHeader title="Mini lesson not found" /><Link to={`${STUDY_ROOT}?tab=practice`}>Choose another lesson</Link></>;
  const pool = STUDY_QUESTIONS.filter((q) => q.lessonId === lessonId); const ids = selectRound(state.data, pool, state.data.preferences.roundSize);
  return <><PageHeader eyebrow="One idea · about one minute" title={lesson.format} subtitle="Understand the connection before practicing it." />
    <Card className="study-lesson-card"><LessonBody lesson={lesson} /></Card>
    <Card><h2>Try it without looking</h2><p>{pool.length} sample questions · Your progress will build through later spaced recalls.</p>
      {state.data.session && state.data.session.phase !== "summary" && <p className="study-callout">You already have a round in progress. Continue it before starting another.</p>}
      <label className="study-field">Practice mode<select value={mode} onChange={(e) => setMode(e.target.value as StudyMode)}><option value="learn">Learn & practice · hints and immediate explanations</option><option value="timed">Timed · review after finishing</option></select></label>
      <div className="n2-actions"><Button variant="primary" onClick={() => {
        state.update((p: StudyState) => ({ ...p, learned: [...new Set([...p.learned, lessonId])] }));
        start(ids, mode, lesson.title);
      }}>{state.data.session && state.data.session.phase !== "summary" ? "Continue existing round" : `Practice ${ids.length} questions`} →</Button>
        {lesson.next && <Link className="ghost-link" to={lesson.next.href}>{lesson.next.label} →</Link>}</div>
    </Card></>;
}
