import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Badge, PageHeader } from "../components/ui";
import { SAA_BY_ID, SAA_QUESTIONS } from "../data/awsSaa/questions";
import { SAA_DOMAINS, SAA_GUIDE, SAA_TOPICS, SAA_VERIFIED, type SaaQuestion } from "../data/awsSaa/schema";
import { gradeSaa, recordSaaAnswer, saaMistakes, saaStreak, startSaaDaily, validSaaSelection, type SaaAnswer, type SaaProgress } from "../lib/awsSaa";
import { optionOrder } from "../lib/quizShuffle";
import { todayISO } from "../lib/srs";
import { useSaaProgress } from "../lib/useSaaProgress";
import { useCrumb } from "../store";

type Mode = "home" | "daily" | "topic" | "mixed" | "review";
type State = ReturnType<typeof useSaaProgress> & { progress: SaaProgress };

export default function AwsSaa({ mode = "home" }: { mode?: Mode }) {
  const state = useSaaProgress();
  const { topicId } = useParams();
  const topic = SAA_TOPICS.find((item) => item.id === topicId);
  useCrumb(topic?.title);
  const [day, setDay] = useState(() => todayISO());
  useEffect(() => {
    const timer = window.setInterval(() => setDay(todayISO()), 15_000);
    return () => window.clearInterval(timer);
  }, []);
  const { progress, update } = state;
  useEffect(() => {
    if (mode === "daily" && progress && !progress.days[day]) update((value) => startSaaDaily(value, day));
  }, [mode, progress, day, update]);
  if (state.loadError) return <div className="page aws-page saa-page"><h1>AWS SAA quizzes</h1>
    <p role="alert">Could not load quiz progress: {state.loadError}</p><button onClick={state.retryLoad}>Retry loading</button></div>;
  if (!progress) return <div className="page" role="status">Loading SAA quiz progress…</div>;
  const ready = { ...state, progress };
  return <div className="page aws-page saa-page">
    {state.saveError && <div className="card saa-save-error" role="alert"><p>Your latest quiz changes have not been saved: {state.saveError}</p>
      <button onClick={state.retrySave}>Retry saving</button></div>}
    {mode === "home" ? <Home state={ready} day={day} /> : mode === "topic" && !topic
      ? <><h1>Topic not found</h1><Link to="/aws-saa">Browse SAA topics</Link></>
      : mode === "daily" && !progress.days[day] ? <p role="status">Preparing your daily five…</p>
      : <Quiz key={`${mode}:${topicId ?? ""}:${day}`} mode={mode} topicId={topicId} state={ready} day={day} />}
  </div>;
}

function Home({ state: { progress }, day }: { state: State; day: string }) {
  const [query, setQuery] = useState("");
  const rows = Object.values(progress.questions);
  const attempts = rows.reduce((sum, row) => sum + row.attempts, 0);
  const correct = rows.reduce((sum, row) => sum + row.correct, 0);
  const mistakes = saaMistakes(progress);
  const daily = progress.days[day];
  const done = daily ? Object.keys(daily.answers).length : 0;
  const matches = SAA_TOPICS.filter((topic) => `${topic.title} ${topic.description}`.toLowerCase().includes(query.toLowerCase()));
  return <>
    <PageHeader eyebrow="AWS certification · Quiz practice" title="AWS SAA-C03"
      subtitle="Build your architecture judgment, five questions at a time. 100 original scenarios with single-answer and multiple-answer questions." />
    <section className="card aws-daily">
      <div><Badge>Daily five · {day}</Badge><h2>A little practice, every day</h2>
        <p>Five questions from different topics. Mistakes come first, then unseen questions. Your set stays fixed once you open it.</p>
        <p><strong>{done} / 5 answered today</strong>{done === 5 && ` · ${Object.values(daily.answers).filter((answer) => answer.correct).length} / 5 correct`}</p>
        <progress className="saa-progress" value={done} max={5} aria-label="Daily questions answered" />
      </div>
      <div className="aws-daily-action"><Link className="btn primary" to="/aws-saa/daily">{done === 5 ? "Review today's five" : done ? "Continue daily five" : "Start daily five"}</Link>
        <span className="faint">Resumes after you leave. A fresh set each local calendar day.</span></div>
    </section>
    <div className="aws-summary" aria-label="SAA progress">
      <div><strong>{rows.length}<small> / 100</small></strong><span>questions practiced</span></div>
      <div><strong>{attempts ? `${Math.round(correct / attempts * 100)}%` : "—"}</strong><span>accuracy across all attempts</span></div>
      <div><strong>{mistakes.length}</strong><span>questions to revisit</span></div>
      <div><strong>{saaStreak(progress)}</strong><span>day daily-five streak</span></div>
    </div>
    <div className="saa-practice-actions"><Link className="btn" to="/aws-saa/practice">Mixed practice · 10 questions</Link>
      <Link className="btn" to="/aws-saa/review">Review mistakes · {mistakes.length}</Link></div>
    <section aria-labelledby="saa-topics-title" className="saa-topics">
      <div className="saa-topics-heading"><div><h2 id="saa-topics-title">Practice by topic</h2><p className="faint">10 topics · 10 questions each · No written answers</p></div>
        <label>Find a topic<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Try VPC, Aurora, SQS…" /></label></div>
      <div className="aws-lesson-grid">{matches.map((topic) => {
        const questions = SAA_QUESTIONS.filter((question) => question.topic === topic.id);
        const answered = questions.filter((question) => progress.questions[question.id]).length;
        const right = questions.filter((question) => progress.questions[question.id]?.lastCorrect).length;
        return <Link to={`/aws-saa/topic/${topic.id}`} className="card aws-lesson-card" key={topic.id}>
          <div className="aws-card-meta"><span>{String(SAA_TOPICS.indexOf(topic) + 1).padStart(2, "0")}</span><Badge>10 questions</Badge></div>
          <h3>{topic.title}</h3><p>{topic.description}</p>
          <progress className="saa-progress" value={answered} max={questions.length} aria-label={`${topic.title} questions practiced`} />
          <span className="faint">{answered} practiced · {right} latest answers correct</span>
        </Link>;
      })}</div>
      {!matches.length && <p role="status">No topics match. Try another service or clear the search.</p>}
    </section>
    <footer className="aws-footer"><span>Original practice questions, not official exam questions. Practice accuracy is not an AWS scaled score.</span>
      <a href={SAA_GUIDE} target="_blank" rel="noreferrer">Official SAA-C03 exam guide</a><span>Content reviewed {SAA_VERIFIED}</span></footer>
  </>;
}

function Quiz({ mode, topicId, state, day }: { mode: Mode; topicId?: string; state: State; day: string }) {
  const { progress, update } = state;
  const topic = SAA_TOPICS.find((item) => item.id === topicId);
  const initialIds = () => mode === "daily" ? progress.days[day].ids : mode === "topic"
    ? SAA_QUESTIONS.filter((question) => question.topic === topicId).map((question) => question.id)
    : mode === "review" ? saaMistakes(progress)
    : optionOrder("saa-mixed", SAA_QUESTIONS.length, String(Date.now())).slice(0, 10).map((index) => SAA_QUESTIONS[index].id);
  const [ids, setIds] = useState(initialIds);
  const [localAnswers, setLocalAnswers] = useState<Record<string, SaaAnswer>>({});
  const answers = mode === "daily" ? progress.days[day].answers : localAnswers;
  const [index, setIndex] = useState(() => Math.max(0, ids.findIndex((id) => !answers[id])));
  const [finished, setFinished] = useState(() => ids.length > 0 && ids.every((id) => !!answers[id]));
  const title = mode === "daily" ? "Daily five" : mode === "topic" ? topic!.title : mode === "review" ? "Mistake review" : "Mixed practice";
  const answered = ids.filter((id) => answers[id]);
  const correct = answered.filter((id) => answers[id].correct).length;
  const missed = answered.filter((id) => !answers[id].correct);
  const submit = (selected: number[]) => {
    const id = ids[index];
    if (answers[id]) return;
    update((value) => recordSaaAnswer(value, id, selected, Date.now(), mode === "daily" ? day : undefined));
    if (mode !== "daily") setLocalAnswers((value) => ({ ...value, [id]: { selected: [...selected], correct: gradeSaa(SAA_BY_ID.get(id)!, selected) } }));
  };
  const restart = (next: string[]) => { setIds(next); setLocalAnswers({}); setIndex(0); setFinished(false); };
  return <div className="aws-study saa-session">
    <Link className="ghost-link" to="/aws-saa">← All SAA quizzes</Link>
    <PageHeader eyebrow={`AWS SAA-C03 · ${mode === "daily" ? day : "Quiz practice"}`} title={title}
      subtitle={mode === "daily" ? "Your first submitted answers count toward today's five. Explanations remain available afterward." : "Choose your answer, then check the reasoning. Multiple-answer questions require every correct selection."} />
    {!ids.length ? <section className="card"><h2>No mistakes waiting</h2><p>Questions whose latest answer is incorrect appear here. Try a topic or a mixed set to keep practicing.</p>
      <Link className="btn primary" to="/aws-saa/practice">Start mixed practice</Link></section> : finished ? <section className="card saa-results" aria-labelledby="saa-result-title">
      <Badge>Session complete</Badge><h2 id="saa-result-title">{correct} / {ids.length} correct</h2>
      <p>{mode === "daily" ? "Daily five complete. Come back tomorrow for a fresh set, or keep practicing by topic." : "Your progress is saved. Review the explanations or retry the questions you missed."}</p>
      <p className="faint">Practice result only. Multiple-answer items receive credit only when all selections match.</p>
      <div className="saa-practice-actions"><button onClick={() => { setIndex(0); setFinished(false); }}>Review explanations</button>
        {mode !== "daily" && missed.length > 0 && <button className="primary" onClick={() => restart(missed)}>Retry {missed.length} missed</button>}
        {mode !== "daily" && <button onClick={() => restart(initialIds())}>Practice again</button>}
        {mode === "daily" && <Link className="btn" to="/aws-saa/practice">Keep practicing</Link>}</div>
      <ol className="saa-result-list">{ids.map((id, position) => <li key={id}><button onClick={() => { setIndex(position); setFinished(false); }}>
        <span>{answers[id]?.correct ? "Correct" : "Incorrect"}</span> · {SAA_BY_ID.get(id)!.prompt}</button></li>)}</ol>
    </section> : <>
      <div className="aws-session-bar"><strong>Question {index + 1} of {ids.length}</strong><span className="faint">{answered.length} answered · {correct} correct</span></div>
      <progress className="saa-progress" value={answered.length} max={ids.length} aria-label="Session questions answered" />
      <Question key={ids[index]} question={SAA_BY_ID.get(ids[index])!} answer={answers[ids[index]]} onSubmit={submit} day={day} />
      <div className="saa-practice-actions"><button disabled={index === 0} onClick={() => setIndex((value) => value - 1)}>Previous</button>
        <button className="primary" disabled={!answers[ids[index]]} onClick={() => index === ids.length - 1 ? setFinished(true) : setIndex((value) => value + 1)}>
          {index === ids.length - 1 ? "View results" : "Next question"}</button></div>
      {mode !== "daily" && <p className="faint">Submitted results are saved. Leaving this practice set starts a new set when you return.</p>}
    </>}
  </div>;
}

function Question({ question, answer, onSubmit, day }: { question: SaaQuestion; answer?: SaaAnswer; onSubmit: (selected: number[]) => void; day: string }) {
  const [selected, setSelected] = useState<number[]>(answer?.selected ?? []);
  const selection = answer?.selected ?? selected;
  const topic = SAA_TOPICS.find((item) => item.id === question.topic)!;
  const multiple = question.correct.length > 1;
  const feedback = useRef<HTMLDivElement>(null);
  const submittedHere = useRef(false);
  useEffect(() => { if (answer && submittedHere.current) feedback.current?.focus(); }, [answer]);
  return <section className="card aws-quiz saa-question">
    <div className="aws-card-meta"><Badge>{topic.title}</Badge><span className="faint">{SAA_DOMAINS[question.domain]}</span></div>
    <form onSubmit={(event) => { event.preventDefault(); if (!answer && validSaaSelection(question, selected)) { submittedHere.current = true; onSubmit(selected); } }}>
      <fieldset><legend className="saa-prompt">{question.prompt}</legend>
        <p id={`${question.id}-instruction`} className="saa-instruction">{multiple ? `Choose ${question.correct.length} answers.` : "Choose one answer."} {multiple && !answer && `${selection.length} / ${question.correct.length} selected.`}</p>
        {optionOrder(question.id, question.options.length, day).map((optionIndex, position) => {
          const option = question.options[optionIndex];
          const isCorrect = question.correct.includes(optionIndex);
          const checked = selection.includes(optionIndex);
          return <label className={`aws-option ${answer ? isCorrect ? "aws-correct" : checked ? "aws-incorrect" : "" : ""}`} key={optionIndex}>
            <span className="aws-option-choice"><input type={multiple ? "checkbox" : "radio"} name={question.id} value={optionIndex} checked={checked} disabled={!!answer}
              aria-describedby={`${question.id}-instruction`} onChange={() => setSelected((value) => multiple ? value.includes(optionIndex) ? value.filter((item) => item !== optionIndex) : [...value, optionIndex] : [optionIndex])} />
              <span><strong>{String.fromCharCode(65 + position)}.</strong> {option.text}</span></span>
            {answer && <span className="aws-option-reason"><strong>{isCorrect ? "Correct answer" : checked ? "Your answer · Incorrect" : "Incorrect option"}:</strong> {option.explanation}</span>}
          </label>;
        })}
      </fieldset>
      {!answer && <button type="submit" className="primary" disabled={!validSaaSelection(question, selected)}>Check answer</button>}
    </form>
    {answer && <div className="aws-result" role="status" tabIndex={-1} ref={feedback}>
      <h2>{answer.correct ? "Correct" : "Not quite"}</h2>
      {!answer.correct && <p>{multiple ? "All correct options must be selected, with no incorrect options." : "The correct option is marked above."}</p>}
      <p><strong>Takeaway:</strong> {question.takeaway}</p>
      <a href={topic.source} target="_blank" rel="noreferrer">AWS documentation · {topic.title}</a>
    </div>}
  </section>;
}
