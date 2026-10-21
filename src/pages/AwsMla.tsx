import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Markdown } from "../components/Markdown";
import { Badge, PageHeader } from "../components/ui";
import { AWS_LESSONS } from "../data/awsMla/lessons";
import { AWS_DOMAINS, AWS_GUIDE, AWS_SKILLS, AWS_TASKS, AWS_VERIFIED, type AwsLesson } from "../data/awsMla/syllabus";
import { awsStatus, awsStudyStreak, gradeAwsQuestion, planAwsSession, recordAwsAttempt, setAwsNote, type AwsProgress, type AwsTarget } from "../lib/awsMla";
import { optionOrder } from "../lib/quizShuffle";
import { todayISO } from "../lib/srs";
import { useAwsProgress } from "../lib/useAwsProgress";
import { useCrumb } from "../store";
import roadmap from "../../AWS_MLA_C02_ROADMAP.md?raw";

type State = ReturnType<typeof useAwsProgress> & { progress: AwsProgress };
const statusLabels = { new: "New", due: "Review due", learning: "Learning", retained: "Retained" };

function nextReview(due: number, now: number): string {
  if (due <= now) return "now";
  if (due - now < 3_600_000) return `in ${Math.ceil((due - now) / 60_000)} min`;
  return new Date(due).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function AwsMla({ daily = false }: { daily?: boolean }) {
  const state = useAwsProgress();
  const { lessonId } = useParams();
  const lesson = AWS_LESSONS.find((item) => item.id === lessonId);
  useCrumb(lesson?.title);
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 30_000);
    return () => window.clearInterval(timer);
  }, []);
  if (state.loadError) return <div className="page aws-page"><h1>AWS MLA-C02</h1>
    <p role="alert">Could not load your study progress: {state.loadError}</p><button onClick={state.retryLoad}>Retry loading</button></div>;
  if (!state.progress) return <div className="page" role="status">Loading AWS study progress…</div>;
  const ready = { ...state, progress: state.progress };
  return <div className="page aws-page">
    {state.saveError && <div className="card" role="alert"><p>Your latest study changes have not been saved: {state.saveError}</p>
      <button onClick={state.retrySave}>Retry saving</button></div>}
    {daily ? <DailySession state={ready} now={now} /> : lessonId ? lesson
      ? <><Link className="ghost-link" to="/aws-mla">← AWS MLA-C02</Link><Lesson key={lesson.id} lesson={lesson} state={ready} now={now} /></>
      : <><h1>Lesson not found</h1><Link to="/aws-mla">Open the AWS course</Link></>
      : <CourseHome state={ready} now={now} />}
  </div>;
}

function CourseHome({ state, now }: { state: State; now: number }) {
  const { progress, update } = state;
  const [view, setView] = useState<"today" | "lessons" | "blueprint">("today");
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("all");
  const [filter, setFilter] = useState("all");
  const plan = planAwsSession(progress, now);
  const day = progress.days[todayISO(new Date(now))];
  const studied = AWS_LESSONS.filter((lesson) => progress.lessons[lesson.id]?.attempts);
  const retained = AWS_LESSONS.filter((lesson) => awsStatus(progress.lessons[lesson.id], now) === "retained");
  const due = AWS_LESSONS.filter((lesson) => awsStatus(progress.lessons[lesson.id], now) === "due");
  const matches = AWS_LESSONS.filter((lesson) => (domain === "all" || lesson.task[0] === domain)
    && (filter === "all" || awsStatus(progress.lessons[lesson.id], now) === filter)
    && `${lesson.title} ${lesson.task} ${lesson.model} ${lesson.rules.join(" ")} ${lesson.skills.map((id) => `${id} ${AWS_SKILLS.find((s) => s.id === id)?.title}`).join(" ")}`.toLowerCase().includes(query.toLowerCase()));
  return <>
    <PageHeader eyebrow="AWS certification · daily practice" title="AWS MLA-C02"
      subtitle="Build the decision skills. Recall the idea, solve a scenario, and revisit it before it fades." />
    <div className="aws-summary" aria-label="Course progress">
      <div><strong>{studied.length}<small> / {AWS_LESSONS.length}</small></strong><span>lessons practiced</span></div>
      <div><strong>{retained.length}</strong><span>retained through spaced checks</span></div>
      <div><strong>{due.length}</strong><span>reviews due</span></div>
      <div><strong>{awsStudyStreak(progress, new Date(now))}</strong><span>day study streak</span></div>
    </div>
    <div className="aws-switcher" aria-label="Course views">
      {([ ["today", "Today"], ["lessons", "All lessons"], ["blueprint", "Exam map · 107 skills"] ] as const).map(([key, label]) =>
        <button key={key} aria-pressed={view === key} onClick={() => setView(key)}>{label}</button>)}
    </div>
    {view === "today" && <>
      <section className="card aws-daily">
        <div><Badge>Small daily steps</Badge><h2>Your next study session</h2>
          <p>Review what is due, then learn the next idea. Reviews prioritize overdue and weak material; new lessons follow the course order.</p>
          <p><strong>{day?.minutes ?? 0} / {progress.target} estimated minutes today</strong> · {day?.lessons.length ?? 0} lessons practiced</p></div>
        <div className="aws-daily-action">
          <label htmlFor="aws-target">Daily target</label>
          <select id="aws-target" value={progress.target} onChange={(event) => update((p) => ({ ...p, target: Number(event.target.value) as AwsTarget }))}>
            <option value={10}>10 minutes</option><option value={15}>15 minutes</option><option value={25}>25 minutes</option>
          </select>
          {plan.length > 0 ? <Link className="btn primary" to="/aws-mla/daily">Start {plan.length}-lesson session →</Link>
            : <p role="status">{(day?.minutes ?? 0) >= progress.target ? "Daily target reached. Come back tomorrow, or browse another lesson." : "No lessons fit the remaining target. Browse a lesson or return for your next review."}</p>}
          <span className="faint">New lesson ≈ 6 min · review ≈ 3 min</span>
        </div>
      </section>
      {plan.length > 0 && <section className="aws-stack"><h2>Up next</h2>{plan.map((id, index) => {
        const lesson = AWS_LESSONS.find((item) => item.id === id)!;
        return <Link className="card aws-up-next" key={id} to={`/aws-mla/${id}`}><span className="faint">{index + 1}</span>
          <div><strong>{lesson.title}</strong><span>Task {lesson.task} · {statusLabels[awsStatus(progress.lessons[id], now)]}</span></div><span aria-hidden>→</span></Link>;
      })}</section>}
      <section className="aws-stack"><h2>Coverage by exam domain</h2><div className="aws-domains">
        {AWS_DOMAINS.map((item) => {
          const lessons = AWS_LESSONS.filter((lesson) => Number(lesson.task[0]) === item.id);
          const count = lessons.filter((lesson) => progress.lessons[lesson.id]?.attempts).reduce((sum, lesson) => sum + lesson.skills.length, 0);
          const total = lessons.reduce((sum, lesson) => sum + lesson.skills.length, 0);
          return <div className="card" key={item.id}><Badge>{item.weight}% of exam</Badge><h3>{item.title}</h3>
            <progress value={count} max={total} aria-label={`${item.title}: ${count} of ${total} skills introduced`} />
            <p className="faint">{count} / {total} skills introduced</p></div>;
        })}
      </div></section>
      <div className="card aws-explainer"><h2>Make it stick</h2><p>Try the recall prompt before opening the notes. A perfect first submission moves a due lesson along the 1, 3, 7, 14, 30 day review ladder. A miss comes back in 10 minutes. Early repeat passes keep the current review date.</p>
        <p>Retained means three successful spaced checks with a current correct result. This small question bank is a study signal; use hands-on work and official practice resources to assess exam readiness.</p></div>
    </>}
    {view === "lessons" && <section className="aws-stack">
      <h2>Learn the complete published blueprint</h2>
      <div className="aws-filters">
        <label>Search topic, service, or skill ID<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="e.g. RAG, IAM, 3.2.9" /></label>
        <label>Domain<select value={domain} onChange={(event) => setDomain(event.target.value)}><option value="all">All domains</option>
          {AWS_DOMAINS.map((item) => <option key={item.id} value={item.id}>{item.id}. {item.title}</option>)}</select></label>
        <label>Progress<select value={filter} onChange={(event) => setFilter(event.target.value)}><option value="all">All progress</option>
          {Object.entries(statusLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
      </div>
      <p className="faint" role="status">{matches.length} lessons · {matches.reduce((sum, lesson) => sum + lesson.skills.length, 0)} mapped skills</p>
      <div className="aws-lesson-grid">{matches.map((lesson) => <Link className="card aws-lesson-card" key={lesson.id} to={`/aws-mla/${lesson.id}`}>
        <div className="aws-card-meta"><Badge>Task {lesson.task}</Badge><span>{statusLabels[awsStatus(progress.lessons[lesson.id], now)]}</span></div>
        <h3>{lesson.title}</h3><p>{lesson.model}</p><span className="faint">{lesson.skills.length} skills · 2 scenarios · ≈ 6 min</span>
      </Link>)}</div>
      {!matches.length && <p>No matching lessons. Try another service or clear the filters.</p>}
    </section>}
    {view === "blueprint" && <section className="aws-stack"><h2>Every published task and skill</h2>
      <p>Verified {AWS_VERIFIED}. Short study labels map to AWS skill IDs. The official blueprint is non-exhaustive, and lessons provide introductory coverage.</p>
      <a href={`data:text/markdown;charset=utf-8,${encodeURIComponent(roadmap)}`} download="AWS_MLA_C02_ROADMAP.md">Download the full Markdown roadmap</a>
      {AWS_TASKS.map((task) => <details className="card aws-task" key={task.id}><summary>{task.id} · {task.title} <span className="faint">({task.labels.length} skills)</span></summary>
        <ul>{AWS_SKILLS.filter((skill) => skill.task === task.id).map((skill) => {
          const lesson = AWS_LESSONS.find((item) => item.skills.includes(skill.id))!;
          return <li key={skill.id}><Link to={`/aws-mla/${lesson.id}`}><code>{skill.id}</code> {skill.title}</Link>
            <span className="faint"> · {statusLabels[awsStatus(progress.lessons[lesson.id], now)]}</span></li>;
        })}</ul></details>)}
      <details className="card aws-task"><summary>Read the full roadmap, service list, and practical milestones</summary><Markdown>{roadmap}</Markdown></details>
    </section>}
    <footer className="aws-footer"><a href={AWS_GUIDE} target="_blank" rel="noreferrer">Official MLA-C02 guide ↗</a>
      <a href="https://aws.amazon.com/certification/certified-machine-learning-engineer-associate/" target="_blank" rel="noreferrer">Exam format & beta status ↗</a>
      <span>Content verified {AWS_VERIFIED} · Works offline · Progress saved locally</span></footer>
  </>;
}

function DailySession({ state, now }: { state: State; now: number }) {
  const [queue] = useState(() => planAwsSession(state.progress, now));
  const [index, setIndex] = useState(0);
  const lesson = AWS_LESSONS.find((item) => item.id === queue[index]);
  if (!lesson) return <><PageHeader eyebrow="AWS MLA-C02" title={queue.length ? "Session complete" : "You're up to date for this session"}
    subtitle={queue.length ? `You practiced ${queue.length} lessons. Your progress and next review dates are saved locally.` : "Browse a lesson, adjust your target, or return when a review is due."} />
    <Link className="btn primary" to="/aws-mla">Back to your course →</Link></>;
  return <><div className="aws-session-bar"><Link to="/aws-mla">← Back to course</Link><strong>Daily session · {index + 1} / {queue.length}</strong></div>
    <Lesson key={`${index}-${lesson.id}`} lesson={lesson} state={state} now={now} onNext={() => { setIndex((value) => value + 1); document.getElementById("main")?.scrollTo(0, 0); }} />
  </>;
}

function Lesson({ lesson, state, now, onNext }: { lesson: AwsLesson; state: State; now: number; onNext?: () => void }) {
  const [revealed, setRevealed] = useState(false);
  const [recall, setRecall] = useState("");
  const [exercise, setExercise] = useState("");
  const [showExercise, setShowExercise] = useState(false);
  const [picks, setPicks] = useState<number[][]>(() => lesson.questions.map(() => []));
  const [submitted, setSubmitted] = useState(false);
  const [optionSalt] = useState(() => String(state.progress.lessons[lesson.id]?.attempts ?? 0));
  const [note, setNote] = useState(state.progress.lessons[lesson.id]?.note ?? "");
  const row = state.progress.lessons[lesson.id];
  const score = lesson.questions.filter((question, index) => gradeAwsQuestion(question, picks[index])).length;
  const next = AWS_LESSONS[AWS_LESSONS.indexOf(lesson) + 1];
  function choose(questionIndex: number, optionIndex: number) {
    if (submitted) return;
    setPicks((previous) => previous.map((selected, index) => index !== questionIndex ? selected
      : lesson.questions[index].answers.length === 1 ? [optionIndex]
        : selected.includes(optionIndex) ? selected.filter((item) => item !== optionIndex) : [...selected, optionIndex]));
  }
  return <article className="aws-study">
    <PageHeader eyebrow={`AWS MLA-C02 · Task ${lesson.task} · ${row?.attempts ? "Review ≈ 3 min" : "Lesson ≈ 6 min"}`}
      title={lesson.title} subtitle={lesson.skills.map((id) => `${id}: ${AWS_SKILLS.find((skill) => skill.id === id)?.title}`).join(" · ")} />
    <section className="card aws-recall"><Badge>1 · Recall first</Badge><h2>Try before looking</h2><p>{lesson.recall}</p>
      <label htmlFor="aws-recall">Your explanation in a few words<textarea id="aws-recall" value={recall} onChange={(event) => setRecall(event.target.value)} placeholder="Explain it as if teaching a teammate…" rows={3} /></label>
      <button className="primary" aria-expanded={revealed} aria-controls="aws-lesson-notes" onClick={() => setRevealed((value) => !value)}>{revealed ? "Hide lesson notes" : "Reveal lesson notes"}</button>
    </section>
    {revealed && <section className="card aws-notes" id="aws-lesson-notes"><h2>The mental model</h2><p className="aws-model">{lesson.model}</p>
      <ul>{lesson.rules.map((rule) => <li key={rule}>{rule}</li>)}</ul><div className="aws-trap"><strong>Common trap</strong><p>{lesson.trap}</p></div>
      <p className="faint">Go deeper: {lesson.references.map((reference, index) => <span key={reference.url}>{index > 0 && " · "}<a href={reference.url} target="_blank" rel="noreferrer">{reference.title} ↗</a></span>)}</p>
    </section>}
    <section className="card aws-exercise"><Badge>2 · Apply the idea</Badge><h2>A small design exercise</h2><p>{lesson.exercise}</p>
      <label htmlFor="aws-exercise">Your approach<textarea id="aws-exercise" value={exercise} onChange={(event) => setExercise(event.target.value)} rows={3} /></label>
      <button aria-expanded={showExercise} onClick={() => setShowExercise((value) => !value)}>{showExercise ? "Hide suggested approach" : "Compare with a suggested approach"}</button>
      {showExercise && <p className="aws-exercise-answer">{lesson.exerciseAnswer}</p>}
    </section>
    <section className="card aws-quiz"><Badge>3 · Check your decision skills</Badge><h2>Scenario checks</h2>
      <p className="faint">Submit once to record this check. Select-all questions require every correct option. These are original study questions.</p>
      <form onSubmit={(event) => {
        event.preventDefault();
        if (submitted || picks.some((picked) => !picked.length)) return;
        setSubmitted(true);
        state.update((progress) => recordAwsAttempt(progress, lesson.id, picks));
      }}>
        {lesson.questions.map((question, questionIndex) => <fieldset key={question.id} disabled={submitted}>
          <legend>{questionIndex + 1}. {question.prompt} {question.answers.length > 1 && <strong>(Select {question.answers.length})</strong>}</legend>
          {optionOrder(question.id, question.options.length, optionSalt).map((optionIndex) => {
            const option = question.options[optionIndex];
            const selected = picks[questionIndex].includes(optionIndex);
            const correct = question.answers.includes(optionIndex);
            return <label className={`aws-option ${submitted ? correct ? "aws-correct" : selected ? "aws-incorrect" : "" : ""}`} key={optionIndex}>
              <span className="aws-option-choice"><input type={question.answers.length > 1 ? "checkbox" : "radio"} name={question.id} checked={selected} onChange={() => choose(questionIndex, optionIndex)} /><span>{option.text}</span></span>
              {submitted && <span className="aws-option-reason"><strong>{correct ? "Correct option. " : selected ? "Your selection was incorrect. " : "Other option. "}</strong>{option.why}</span>}
            </label>;
          })}
          {submitted && <p><strong>{gradeAwsQuestion(question, picks[questionIndex]) ? "Correct" : "Review this decision"}</strong></p>}
        </fieldset>)}
        {!submitted && <button type="submit" className="primary" disabled={picks.some((picked) => !picked.length)}>Check answers & schedule review</button>}
      </form>
      {submitted && <div className="aws-result" role="status"><h3>{score} / {lesson.questions.length} correct</h3>
        <p>{score === lesson.questions.length ? "Good recall. " : "Read the explanations and revisit the mental model. "}Next review: {row ? nextReview(row.due, now) : "scheduled"}.</p>
        {onNext ? <button className="primary" onClick={onNext}>Continue session →</button> : <div className="aws-switcher">
          {next && <Link className="btn primary" to={`/aws-mla/${next.id}`}>Next lesson →</Link>}
          <Link to="/aws-mla">Back to course</Link>
        </div>}
      </div>}
    </section>
    <section className="card aws-personal-note"><h2>Your takeaway</h2><label htmlFor="aws-note">Save a rule you want to remember<textarea id="aws-note" rows={3} maxLength={10_000} value={note} onChange={(event) => setNote(event.target.value)}
      onBlur={() => { if (note !== (row?.note ?? "")) state.update((progress) => setAwsNote(progress, lesson.id, note)); }} /></label>
      <button onClick={() => state.update((progress) => setAwsNote(progress, lesson.id, note))}>Save takeaway</button><span className="faint">{note === (row?.note ?? "") ? " Saved locally" : " Unsaved changes"}</span>
    </section>
  </article>;
}
