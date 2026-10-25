import { Link } from "react-router-dom";
import { Badge, Button, Card, ErrorState } from "../../components/ui";
import { STUDY_LESSON_MAP, STUDY_QUESTION_MAP, type StudyLesson, type StudyQuestion } from "../../data/n2Study";
import { displayAnswer, targetAnswer, MISTAKE_REASONS, type StudyAttempt } from "../../lib/n2Study";
import { useN2Study, type N2StudyController } from "../../lib/useN2Study";

export const STUDY_ROOT = "/japanese/n2";
export function formatTime(seconds: number): string {
  const s = Math.max(0, Math.ceil(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
export function StudyStatus({ state }: { state: ReturnType<typeof useN2Study> }) {
  if (state.loadError) return <ErrorState title="Your study progress could not be loaded" error={state.loadError} onRetry={state.retryLoad} />;
  if (!state.data) return <p role="status">Loading your study space…</p>;
  if (state.saveError) return <Card tone="warn"><p role="alert">{state.saveError}</p><Button onClick={state.retrySave}>Retry saving</Button></Card>;
  return <p className="study-save-status" role="status">{state.saving ? "Saving…" : "Saved on this device"}</p>;
}
export function LessonBody({ lesson }: { lesson: StudyLesson }) {
  return <div className="study-lesson-body">
    <Badge>{lesson.format}</Badge><h2>{lesson.title}</h2>
    <p className="study-takeaway">{lesson.takeaway}</p>
    <ol className="study-steps">{lesson.steps.map((step) => <li key={step}>{step}</li>)}</ol>
    <div className="study-example">{lesson.examples.map((e) => <div key={e.japanese}><p lang="ja">{e.japanese}</p><p className="n2-meta">{e.english}</p></div>)}</div>
    <p className="study-callout"><strong>Watch for this:</strong> {lesson.trap}</p>
  </div>;
}
export function EvidenceText({ text, evidence = [] }: { text: string; evidence?: string[] }) {
  // Exact quotes are highlighted only after an attempt. Never inject HTML.
  const ranges = evidence.flatMap((quote) => {
    const at = text.indexOf(quote);
    return at >= 0 && quote ? [{ at, end: at + quote.length }] : [];
  }).sort((a, b) => a.at - b.at);
  const parts = []; let cursor = 0;
  for (const r of ranges) {
    if (r.at < cursor) continue;
    parts.push(text.slice(cursor, r.at), <mark className="dokkai-evidence" key={`${r.at}-${r.end}`}>{text.slice(r.at, r.end)}</mark>);
    cursor = r.end;
  }
  parts.push(text.slice(cursor));
  return <>{parts}</>;
}
export function QuestionTexts({ question, review = false }: { question: StudyQuestion; review?: boolean }) {
  if (!question.texts) return null;
  return <div className={`study-texts ${question.texts.length > 1 ? "study-texts-paired" : ""}`}>
    {question.texts.map((t, i) => <section key={i} className="study-passage">
      <h3>{t.label ?? (question.texts!.length > 1 ? `Text ${i + 1}` : "Passage")}</h3>
      <p lang="ja"><EvidenceText text={t.text} evidence={review ? question.evidence : []} /></p>
    </section>)}
  </div>;
}
export function AnswerExplanation({ question: q, result, state }: { question: StudyQuestion; result: StudyAttempt; state: N2StudyController }) {
  const note = state.data.notes[q.id] ?? { text: "", reason: "" };
  const review = state.data.reviews[q.id];
  return <div className="study-explanation">
    <div className="n2-actions"><Badge tone={result.correct && !result.assisted ? "good" : "warn"}>{result.revealed ? "Revealed · scheduled for review" : result.correct ? result.assisted ? "Correct with help" : "Correct" : "Let's work through it"}</Badge>
      <span className="n2-meta">{formatTime(result.elapsedMs / 1000)} · {result.confidence === "sure" ? "Confident" : result.confidence === "guess" ? "Guessed" : "Unsure"}</span></div>
    <p>Your answer: <strong lang="ja">{displayAnswer(q, result.answer)}</strong></p>
    <div className="study-example"><span className="n2-meta">Target answer</span><p lang="ja">{targetAnswer(q)}</p>
      {q.kind === "typed" && <p>{q.word} — {q.meaning}</p>}
      {q.kind === "assembly" && <p>★ is slot {q.starIndex + 1}: <strong lang="ja">{q.fragments[q.order[q.starIndex]]}</strong></p>}</div>
    {q.kind === "assembly" && !!q.acceptedOrders?.length && <details><summary>Other accepted sentence orders</summary>{q.acceptedOrders.map((order) => <p key={order.join(",")} lang="ja">{q.before}{order.map((i) => q.fragments[i]).join("")}{q.after}</p>)}</details>}
    <h3>Why it fits</h3><p>{q.explanation}</p>
    {q.evidence && <div className="study-callout"><strong>Evidence from the text</strong>{q.evidence.map((quote) => <blockquote key={quote} lang="ja">{quote}</blockquote>)}</div>}
    {q.kind === "choice" && <details open={!result.correct}><summary>Understand every option</summary><div className="study-option-explanations">{q.choices.map((c, i) => <div key={i} className={i === q.answer ? "study-correct-option" : ""}>
      <div className="n2-actions"><strong lang="ja">{i + 1}. {c.text}</strong><Badge tone={i === q.answer ? "good" : "neutral"}>{i === q.answer ? "Correct" : c.trap ?? "Doesn't fit"}</Badge></div><p>{c.why}</p>
    </div>)}</div></details>}
    <details><summary>English translation</summary>{q.texts ? q.texts.map((t, i) => <p key={i}>{t.translation}</p>) : <p>{q.translation}</p>}</details>
    <details><summary>Your mistake note &amp; takeaway</summary>
      <label className="study-field">What tripped you up?<select value={note.reason} onChange={(e) => state.update((p) => ({ ...p, notes: { ...p.notes, [q.id]: { ...note, reason: e.target.value } } }))}>
        <option value="">Choose a reason</option>{MISTAKE_REASONS.map((r) => <option key={r}>{r}</option>)}
      </select></label>
      <label className="study-field">A clue to remember next time<textarea maxLength={4000} rows={3} value={note.text} placeholder="e.g. Check whether the speaker limits a claim or rejects it completely."
        onChange={(e) => state.update((p) => ({ ...p, notes: { ...p.notes, [q.id]: { ...note, text: e.target.value } } }))} /></label>
    </details>
    {review && <p className="n2-meta">Next review: {new Date(review.due).toLocaleDateString()} · {review.stage >= 3 ? "Retained across spaced reviews" : `Review step ${review.stage} of 3`}. Early repeats don't advance the spacing.</p>}
  </div>;
}
export function QuestionLabel({ id }: { id: string }) {
  const q = STUDY_QUESTION_MAP.get(id);
  if (!q) return <>Previously practiced question</>;
  return <>{STUDY_LESSON_MAP.get(q.lessonId)!.format} · <span lang="ja">{q.kind === "typed" ? q.word : q.kind === "assembly" ? q.before || "Sentence assembly ★" : q.prompt}</span></>;
}
export function LibraryLink() { return <Link className="ghost-link" to={`${STUDY_ROOT}/library`}>Full course library →</Link>; }
