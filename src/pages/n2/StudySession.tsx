import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Badge, Button, Card, ConfirmDialog, PageHeader, ProgressBar } from "../../components/ui";
import { STUDY_LESSON_MAP, STUDY_QUESTION_MAP, type StudyQuestion } from "../../data/n2Study";
import { beginQuestions, blankDraft, checkAnswer, finishSession, moveQuestion, pauseSession, startSession, updateDraft, type Confidence, type StudySession as Session } from "../../lib/n2Study";
import { useN2Study, type N2StudyController } from "../../lib/useN2Study";
import { AnswerExplanation, formatTime, LessonBody, QuestionLabel, QuestionTexts, StudyStatus, STUDY_ROOT } from "./StudyShared";

export default function StudySession() {
  const state = useN2Study();
  return <div className="page n2-page study-page"><StudyStatus state={state} />
    {state.data && <SessionRouter state={state as N2StudyController} />}
  </div>;
}
function SessionRouter({ state }: { state: N2StudyController }) {
  const session = state.data.session;
  if (!session) return <><PageHeader title="Ready for a short round?" subtitle="Choose a section or today's mixed practice to begin." /><Link className="btn primary" to={STUDY_ROOT}>Open your study space</Link></>;
  return <SessionView key={session.id} state={state} session={session} />;
}
function SessionView({ state, session: s }: { state: N2StudyController; session: Session }) {
  const navigate = useNavigate();
  const [now, setNow] = useState(Date.now());
  const [confirmFinish, setConfirmFinish] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const nextButton = useRef<HTMLButtonElement>(null);
  const mountGeneration = useRef(0);
  const update = state.update;
  const q = STUDY_QUESTION_MAP.get(s.questionIds[s.position])!;
  const lesson = STUDY_LESSON_MAP.get(q.lessonId)!;
  const result = s.results[q.id];
  const d = s.drafts[q.id] ?? blankDraft();
  useEffect(() => {
    const tick = () => {
      const at = Date.now(); setNow(at);
      update((p) => p.session?.id === s.id && p.session.phase !== "summary" && p.session.deadline !== null && at >= p.session.deadline ? finishSession(p, at) : p);
    };
    tick();
    const interval = window.setInterval(tick, 500);
    return () => window.clearInterval(interval);
  }, [s.id, update]);
  useEffect(() => {
    // Guided rounds pause when navigating away; timed deadlines always continue.
    // A StrictMode effect replay is not navigation: cancel its deferred cleanup.
    const generation = ++mountGeneration.current;
    const pause = () => update((p) => p.session?.id === s.id ? pauseSession(p, true) : p);
    window.addEventListener("pagehide", pause);
    return () => {
      window.removeEventListener("pagehide", pause);
      queueMicrotask(() => { if (mountGeneration.current === generation) pause(); });
    };
  }, [s.id, update]);
  useEffect(() => { heading.current?.focus(); }, [s.position, s.phase, s.paused]);
  useEffect(() => { if (result && s.phase !== "summary") nextButton.current?.focus(); }, [result, s.phase]);
  function back() { update((p) => pauseSession(p, true)); navigate(STUDY_ROOT); }
  const remaining = s.deadline === null ? null : Math.max(0, (s.deadline - now) / 1000);
  const elapsed = d.elapsedMs / 1000 + (!s.paused && s.phase === "question" && !result ? Math.max(0, now - s.questionStartedAt) / 1000 : 0);
  if (s.phase === "summary") {
    const results = Object.values(s.results);
    const independent = results.filter((r) => r.correct && !r.assisted).length;
    const assisted = results.filter((r) => r.assisted).length;
    const retry = results.filter((r) => !r.correct || r.assisted || r.confidence === "guess").map((r) => r.questionId);
    const seconds = results.reduce((n, r) => n + r.elapsedMs, 0) / 1000;
    return <>
      <PageHeader eyebrow={s.mode === "timed" ? "Timed practice complete" : "Learn & practice complete"} title="A little clearer than before"
        subtitle={s.expired ? "Time expired. Submitted answers were graded; unanswered questions are included as missed." : "Your results and next reviews are saved. Take one useful clue into your next round."} />
      <Card className="study-summary"><div className="study-score">{independent}<span> / {results.length}</span></div><p>correct without help · {assisted} assisted · {formatTime(seconds)} answering time</p>
        <p className="n2-meta">Practice results are not an official JLPT scaled score. A correct guess stays on a short review interval.</p>
        <div className="n2-actions">{retry.length > 0 && <Button variant="primary" onClick={() => update((p) => startSession({ ...p, session: null }, retry, "learn", "Revisit this round"))}>Retry {retry.length} to revisit</Button>}
          <Button onClick={back}>Back to study space</Button></div>
      </Card>
      <section aria-label="Round review" className="study-stack">{s.questionIds.map((id, i) => {
        const item = STUDY_QUESTION_MAP.get(id)!; const r = s.results[id];
        return <details className="card study-recap-item" key={id}><summary><span>{i + 1}. <QuestionLabel id={id} /></span><Badge tone={r.correct && !r.assisted ? "good" : "warn"}>{r.correct ? r.assisted ? "With help" : "Correct" : "Revisit"}</Badge></summary>
          <QuestionTexts question={item} review /><AnswerExplanation question={item} result={r} state={state} /></details>;
      })}</section>
    </>;
  }
  if (s.paused) return <><PageHeader title="Your place is saved" subtitle={`${s.title} · Question ${s.position + 1} of ${s.questionIds.length}`} />
    <Card><h2>Pick up where you left off</h2><p>Your answers, hints, confidence and notes are kept. The guided timer is paused.</p>
      <Button variant="primary" onClick={() => update((p) => pauseSession(p, false))}>Resume round</Button></Card><Link to={STUDY_ROOT}>Back to study space</Link></>;
  return <>
    <div className="study-session-toolbar"><Button variant="ghost" onClick={back}>← Save &amp; return</Button>
      <span className="n2-meta">{s.mode === "timed" ? "Timed · timer continues when you leave" : "Learn & practice · pause anytime"}</span>
      {remaining !== null && <span className={`study-timer ${remaining < 30 ? "study-low-time" : ""}`} role="timer" aria-label="Time remaining">{formatTime(remaining)} left</span>}</div>
    <PageHeader eyebrow={s.title} title={lesson.format} subtitle={`Question ${s.position + 1} of ${s.questionIds.length}`} />
    <ProgressBar value={s.mode === "timed" ? Object.values(s.drafts).filter((v) => v.answer).length : Object.keys(s.results).length} max={s.questionIds.length} label="Questions answered" />
    {s.phase === "lesson" ? <Card className="study-lesson-card"><Badge>Learn · about one minute</Badge><LessonBody lesson={lesson} />
      <Button variant="primary" onClick={() => update(beginQuestions)}>Try the questions →</Button></Card> : <>
      <div className="study-question-layout">
        <Card className="study-question-card">
          <div className="study-question-meta"><Badge>{q.kind === "typed" ? "Type the hiragana" : q.kind === "assembly" ? "Build the full sentence" : "Choose one answer"}</Badge>
            <span className="n2-meta">{s.mode === "timed" ? "" : `${formatTime(elapsed)} · `}suggested {formatTime(q.targetSeconds)}</span>
            <Button size="sm" variant="ghost" aria-pressed={state.data.bookmarks.includes(q.id)} onClick={() => update((p) => ({ ...p, bookmarks: p.bookmarks.includes(q.id) ? p.bookmarks.filter((id) => id !== q.id) : [...p.bookmarks, q.id] }))}>{state.data.bookmarks.includes(q.id) ? "Saved ★" : "Save for later"}</Button>
          </div>
          <QuestionTexts question={q} review={!!result} />
          <h2 ref={heading} tabIndex={-1} className="study-question-prompt" lang={q.kind === "choice" || q.kind === "typed" ? "ja" : "en"}>{q.prompt}</h2>
          {q.kind === "typed" && <p className="study-word" lang="ja">{q.word}</p>}
          <form onSubmit={(e) => { e.preventDefault(); if (s.mode === "learn") update((p) => checkAnswer(p)); }}>
            <AnswerInput key={q.id} question={q} answer={d.answer} disabled={!!result} onChange={(answer) => update((p) => updateDraft(p, { answer }))} />
            {!result && <fieldset className="study-confidence"><legend>How sure are you?</legend>
              {(["guess", "unsure", "sure"] as Confidence[]).map((c) => <label key={c}><input type="radio" name="confidence" value={c} checked={d.confidence === c} onChange={() => update((p) => updateDraft(p, { confidence: c }))} />{c === "guess" ? "Guessing" : c === "sure" ? "Confident" : "Unsure"}</label>)}
            </fieldset>}
            {!result && s.mode === "learn" && <div className="n2-actions"><Button variant="primary" type="submit" disabled={!d.answer || (q.kind === "assembly" && d.answer.split(",").length !== 4)}>Check answer</Button>
              <Button variant="ghost" onClick={() => update((p) => checkAnswer(p, Date.now(), true))}>Reveal &amp; revisit</Button></div>}
          </form>
          {result && <AnswerExplanation question={q} result={result} state={state} />}
        </Card>
        {s.mode === "learn" && !result && <aside className="study-coach"><Card><h2>Need a small nudge?</h2><p>You can try independently, or use a hint. Using help is recorded separately.</p>
          {!d.assisted ? <Button onClick={() => update((p) => updateDraft(p, { assisted: true }))}>Show a hint</Button> : <p className="study-callout">{q.hint}</p>}
          <details onToggle={(e) => { if (e.currentTarget.open) update((p) => updateDraft(p, { assisted: true })); }}><summary>Review the mini lesson</summary><LessonBody lesson={lesson} /></details></Card></aside>}
      </div>
      <div className="study-session-footer">
        {s.mode === "timed" ? <><div className="study-question-nav" aria-label="Jump to question">{s.questionIds.map((id, i) => <Button key={id} size="sm" aria-label={`Question ${i + 1}${s.drafts[id]?.answer ? ", answered" : ", unanswered"}`} aria-current={i === s.position ? "step" : undefined} onClick={() => update((p) => moveQuestion(p, i))}>{i + 1}{s.drafts[id]?.answer ? " ✓" : ""}</Button>)}</div>
          <div className="n2-actions"><Button disabled={s.position === 0} onClick={() => update((p) => moveQuestion(p, s.position - 1))}>Previous</Button>
            {s.position < s.questionIds.length - 1 && <Button variant="primary" onClick={() => update((p) => moveQuestion(p, s.position + 1))}>Next question →</Button>}
            <Button onClick={() => setConfirmFinish(true)}>Finish timed round</Button></div></>
          : <div className="n2-actions">{result && <Button ref={nextButton} variant="primary" onClick={() => update((p) => s.position + 1 === s.questionIds.length ? finishSession(p) : moveQuestion(p, s.position + 1))}>{s.position + 1 === s.questionIds.length ? "See round recap" : "Next question →"}</Button>}
            <Button variant="ghost" onClick={() => setConfirmFinish(true)}>Finish early</Button></div>}
      </div>
    </>}
    <ConfirmDialog open={confirmFinish} title="Finish this round?" confirmLabel="Finish & review" cancelLabel="Keep practicing" onClose={() => setConfirmFinish(false)}
      consequence={s.mode === "timed" ? "Your current answers will be graded. Unanswered questions count as missed and will be scheduled for review. You can retry them from the recap." : "Your submitted results will be kept and any current answer will be graded. Questions you have not tried will stay unattempted."}
      onConfirm={() => { update((p) => finishSession(p)); setConfirmFinish(false); }} />
  </>;
}
function AnswerInput({ question: q, answer, disabled, onChange }: { question: StudyQuestion; answer: string; disabled: boolean; onChange: (answer: string) => void }) {
  if (q.kind === "typed") return <label className="study-field">Reading in hiragana<input aria-label="Reading in hiragana" value={answer} disabled={disabled} autoComplete="off" autoCapitalize="off" spellCheck={false} lang="ja"
    onChange={(e) => onChange(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && (e.nativeEvent.isComposing || e.keyCode === 229)) e.preventDefault(); }} /></label>;
  if (q.kind === "choice") return <fieldset className="study-answer-options" disabled={disabled}><legend className="sr-only">Choose your answer</legend>{q.choices.map((c, i) => <label key={i} className={answer === String(i) ? "study-option is-selected" : "study-option"}>
    <input type="radio" name={`answer-${q.id}`} value={i} checked={answer === String(i)} onChange={() => onChange(String(i))} /><span className="study-option-number" aria-hidden="true">{i + 1}</span><span lang="ja">{c.text}</span>
  </label>)}</fieldset>;
  const order = answer ? answer.split(",").map(Number) : [];
  return <div className="study-assembly"><p className="n2-sentence" lang="ja">{q.before}<span className="study-slots">{[0, 1, 2, 3].map((i) => <span key={i} className={i === q.starIndex ? "study-slot is-star" : "study-slot"}>{i === q.starIndex && <span className="study-slot-star">★</span>}{order[i] === undefined ? "＿＿" : q.fragments[order[i]]}</span>)}</span>{q.after}</p>
    <p className="n2-meta">Select fragments in sentence order. Undo to change the last fragment.</p>
    <div className="study-fragments">{q.fragments.map((text, i) => <Button key={i} disabled={disabled || order.includes(i)} onClick={() => onChange([...order, i].join(","))}><span lang="ja">{text}</span></Button>)}</div>
    <div className="n2-actions"><Button size="sm" disabled={disabled || !order.length} onClick={() => onChange(order.slice(0, -1).join(","))}>Undo last</Button><Button size="sm" variant="ghost" disabled={disabled || !order.length} onClick={() => onChange("")}>Clear order</Button></div>
  </div>;
}
