import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { useCrumb } from "../store";
import { Badge, Button, Card, Chip, ErrorState, PageHeader, ProgressBar } from "../components/ui";
import { N2_LESSONS, N2_QUESTIONS, type N2Kind, type N2Question } from "../data/jlptN2";
import { isN2Answer, N2_PROGRESS_KEY, n2LessonFor, n2ResumeIndex, n2ReviewQuestions,
  n2Stats, parseN2Progress, recordN2Answer, type N2Progress } from "../lib/jlptN2";

// Serialize snapshots so rapid answers cannot let an older write win. Await
// this queue on remount too, before reading the persisted progress again.
let pendingSave: Promise<void> = Promise.resolve();

function useN2Progress() {
  const [progress, setProgress] = useState<N2Progress | null>(null);
  const latest = useRef<N2Progress>({});
  const [loadError, setLoadError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const mounted = useRef(false);
  useEffect(() => {
    let canceled = false;
    mounted.current = true;
    setLoadError("");
    pendingSave.catch(() => undefined)
      .then(() => api.getSettings())
      .then((settings) => {
        if (canceled) return;
        latest.current = parseN2Progress(settings[N2_PROGRESS_KEY]);
        setProgress(latest.current);
      })
      .catch((e) => { if (!canceled) setLoadError(String(e)); });
    return () => { canceled = true; mounted.current = false; };
  }, [attempt]);

  function persist(next: N2Progress) {
    pendingSave = pendingSave.catch(() => undefined)
      .then(() => api.setSetting(N2_PROGRESS_KEY, JSON.stringify(next)))
      .then(() => { if (mounted.current) setSaveError(""); })
      .catch((e) => {
        if (mounted.current) setSaveError(String(e));
        // Retain the rejected queue for the next mount/retry to recover from.
        throw e;
      });
    // A failed save is shown inline; this handler prevents an unhandled rejection.
    void pendingSave.catch(() => undefined);
  }
  function record(id: string, correct: boolean) {
    const next = recordN2Answer(latest.current, id, correct);
    latest.current = next;
    setProgress(next);
    persist(next);
  }
  return { progress, record, loadError, saveError,
    retryLoad: () => setAttempt((n) => n + 1), retrySave: () => persist(latest.current) };
}

export default function JlptN2() {
  const { lessonId } = useParams();
  const lesson = N2_LESSONS.find((l) => l.id === lessonId);
  const reviewing = lessonId === "review";
  useCrumb(reviewing ? "Mistake review" : lesson?.title ?? null, "Pattern lesson");
  const state = useN2Progress();
  const [run, setRun] = useState(0);

  if (lessonId && !lesson && !reviewing) return <div className="page">
    <PageHeader title="Lesson not found" subtitle="Choose one of the course's pattern families." />
    <Link to="/japanese/n2">Back to JLPT N2</Link>
  </div>;
  if (state.loadError) return <div className="page">
    <PageHeader title="JLPT N2 patterns" />
    <ErrorState title="Your course progress could not be loaded." error={state.loadError} onRetry={state.retryLoad} />
  </div>;
  if (!state.progress) return <div className="page" role="status">Loading your JLPT N2 course…</div>;

  const questions = reviewing ? n2ReviewQuestions(state.progress) : lesson?.questions;
  return <div className="page n2-page">
    {lessonId && <Link className="ghost-link" to="/japanese/n2">← All pattern families</Link>}
    <PageHeader eyebrow="日本語 · JLPT N2 preparation"
      title={reviewing ? "Revisit your mistakes" : lesson?.title ?? "Learn the pattern. Fill the blank."}
      subtitle={lessonId
        ? "Read the surrounding words, supply only the missing part, then explain your choice."
        : "120 original questions in 24 taught families: 60 one-kanji blanks and 60 vocabulary blanks. Readings, translations and an explanation for every answer."} />
    {state.saveError && <Card tone="warn">
      <p role="alert">Your latest progress has not been saved. Keep this page open and retry.</p>
      <Button onClick={state.retrySave}>Retry saving progress</Button>
    </Card>}
    {questions ? <N2Session key={`${lessonId}-${run}`} questions={questions}
      progress={state.progress} reviewing={reviewing} onRecord={state.record}
      onRestart={() => setRun((n) => n + 1)} />
      : <CourseIndex progress={state.progress} />}
  </div>;
}

function CourseIndex({ progress }: { progress: N2Progress }) {
  const [kind, setKind] = useState<N2Kind | "all">("all");
  const [query, setQuery] = useState("");
  const stats = n2Stats(N2_QUESTIONS, progress);
  const next = N2_LESSONS.find((l) => n2Stats(l.questions, progress).correct < l.questions.length) ?? N2_LESSONS[0];
  const normalized = query.trim().toLowerCase();
  const lessons = N2_LESSONS.filter((l) => (kind === "all" || l.kind === kind) &&
    `${l.title} ${l.rule} ${l.questions.map((q) => `${q.word} ${q.reading} ${q.translation}`).join(" ")}`
      .toLowerCase().includes(normalized));

  return <>
    <Card className="n2-overview">
      <div><strong>{stats.correct} / {stats.total} correct on latest attempt</strong>
        <p>{stats.attempted} practiced · {stats.missed} to revisit. Progress stays in your local app database.</p></div>
      <ProgressBar value={stats.correct} max={stats.total} label="N2 questions correct on latest attempt" />
      <div className="n2-actions">
        <Link className="btn primary" to={`/japanese/n2/${next.id}`}>{stats.attempted ? "Continue course" : "Start course"}</Link>
        {stats.missed > 0 && <Link className="btn" to="/japanese/n2/review">Review {stats.missed} mistakes</Link>}
      </div>
    </Card>
    <Card>
      <h2>How to study a family</h2>
      <p>Learn the shared rule, try five blanks, and read why each answer fits. Then change one clue:
        卵大 → 卵形, 日程を調整する → 音量を調節する, 話がそれる → 話をそらす.</p>
      <p>The real exam provides choices. These open blanks accept listed alternatives, but other natural answers may exist.
        Some easier words establish the patterns; this is preparation material, not an official N2 vocabulary list.</p>
    </Card>
    <div className="n2-filters">
      <div className="n2-actions" aria-label="Question type">
        <Chip pressed={kind === "all"} onClick={() => setKind("all")}>All families · 24</Chip>
        <Chip pressed={kind === "kanji"} onClick={() => setKind("kanji")}>One kanji · 60 questions</Chip>
        <Chip pressed={kind === "vocabulary"} onClick={() => setKind("vocabulary")}>Vocabulary · 60 questions</Chip>
      </div>
      <label className="n2-search">Find a pattern or word
        <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="e.g. 調整, size, せっかく" />
      </label>
    </div>
    <div className="n2-grid">
      {lessons.map((l) => {
        const s = n2Stats(l.questions, progress);
        return <Link key={l.id} to={`/japanese/n2/${l.id}`} className="card n2-lesson">
          <div className="n2-actions"><Badge>{l.kind === "kanji" ? "One kanji" : "Vocabulary"}</Badge>
            <span className="n2-meta">{l.id.toUpperCase()} · 5 questions</span></div>
          <h2>{l.title}</h2><p>{l.rule}</p>
          <ProgressBar value={s.correct} max={s.total} label={`${l.title}: correct on latest attempt`} />
          <span className="n2-meta">{s.correct}/5 correct · {s.attempted ? "Continue practice →" : "Learn this family →"}</span>
        </Link>;
      })}
    </div>
    {lessons.length === 0 && <p role="status">No families match this search. Try a different word or question type.</p>}
  </>;
}

function N2Session({ questions, progress, reviewing, onRecord, onRestart }: {
  questions: N2Question[]; progress: N2Progress; reviewing: boolean;
  onRecord: (id: string, correct: boolean) => void; onRestart: () => void;
}) {
  // Freeze the round, especially during review: correcting an answer must not
  // remove the current item and skip the question that follows it.
  const [round] = useState(() => {
    const start = reviewing ? 0 : n2ResumeIndex(questions, progress);
    return [...questions.slice(start), ...questions.slice(0, start)];
  });
  const [position, setPosition] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [input, setInput] = useState("");
  const [result, setResult] = useState<"correct" | "compare" | "revealed" | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const nextRef = useRef<HTMLButtonElement>(null);
  const submitted = useRef(false);
  const q = round[position];
  useEffect(() => { inputRef.current?.focus(); }, [position]);
  useEffect(() => { if (result) nextRef.current?.focus(); }, [result]);

  if (!round.length) return <Card>
    <h2>No mistakes waiting</h2><p>Try a pattern family. Revealed answers and missed targets will appear here for another attempt.</p>
    <Link to="/japanese/n2">Choose a family →</Link>
  </Card>;
  if (!q) return <Card className="n2-finish">
    <Badge tone="good">Round complete</Badge><h2>{correctCount} / {round.length} correct this round</h2>
    <p>Review an explanation, then try producing the answer again without looking. Only a submitted correct answer counts as correct progress.</p>
    <div className="n2-actions"><Button variant="primary" onClick={onRestart}>Practice again</Button>
      <Link to="/japanese/n2">Choose another family →</Link></div>
  </Card>;

  const lesson = n2LessonFor(q);
  const [before, after] = q.sentence.split("___");
  function submit(reveal = false) {
    if (submitted.current || (!reveal && !input.trim())) return;
    submitted.current = true;
    const correct = !reveal && isN2Answer(q, input);
    setResult(reveal ? "revealed" : correct ? "correct" : "compare");
    if (correct) setCorrectCount((n) => n + 1);
    onRecord(q.id, correct);
  }
  function next() {
    submitted.current = false;
    setInput(""); setResult(null); setPosition((n) => n + 1);
  }
  return <>
    <Card className="n2-rule" tone="accent">
      <h2>The pattern{reviewing ? ` · ${lesson.title}` : ""}</h2>
      <p>{lesson.rule}</p><p><strong>Where the rule stops:</strong> {lesson.boundary}</p>
    </Card>
    <Card className="n2-exercise">
      <div className="n2-actions"><Badge>{lesson.kind === "kanji" ? "Fill exactly one kanji" : "Fill the missing word or form"}</Badge>
        <span className="n2-meta">Question {position + 1} of {round.length}</span></div>
      <ProgressBar value={position} max={round.length} label="Questions completed in this round" />
      <h2 className="sr-only">Complete the sentence</h2>
      <p className="n2-sentence" lang="ja">{before}<span className="n2-blank" aria-label="blank">（　　　）</span>{after}</p>
      {!result ? <form onSubmit={(e) => { e.preventDefault(); submit(); }}>
        <label className="n2-answer">Your answer
          <input ref={inputRef} value={input} lang="ja" autoComplete="off" autoCapitalize="off" spellCheck={false}
            aria-describedby="n2-answer-hint" onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && (e.nativeEvent.isComposing || e.keyCode === 229)) e.preventDefault(); }} />
        </label>
        <p className="n2-meta" id="n2-answer-hint">{lesson.kind === "kanji"
          ? "Type only the missing kanji, not the complete word."
          : "Type only the missing part. Kana spellings are accepted where listed. Keep any printed する or endings outside your answer."}</p>
        <div className="n2-actions"><Button type="submit" variant="primary" disabled={!input.trim()}>Check answer</Button>
          <Button type="button" variant="ghost" onClick={() => submit(true)}>Show answer · revisit later</Button></div>
      </form> : <div className="n2-feedback">
        <p role="status"><Badge tone={result === "correct" ? "good" : "warn"}>
          {result === "correct" ? "Accepted answer" : result === "revealed" ? "Answer revealed · added to review" : "Compare with the teaching target"}
        </Badge></p>
        {result !== "revealed" && <p>Your answer: <strong lang="ja">{input}</strong></p>}
        <p className="n2-sentence" lang="ja">{before}<strong className="n2-solution">{q.answer}</strong>{after}</p>
        <p><strong lang="ja">{q.word}</strong> <span lang="ja">（{q.reading}）</span></p>
        <p>{q.translation}</p>
        <h3>Why this fits</h3><p>{q.explanation}</p>
        {q.accepted.length > 0 && <p className="n2-meta">Also accepted for this blank: <span lang="ja">{q.accepted.join(" · ")}</span></p>}
        {result === "compare" && <p>Other natural answers may exist. This exercise checks the target and listed alternatives; an unmatched answer is not necessarily ungrammatical.</p>}
        <Button ref={nextRef} variant="primary" onClick={next}>{position + 1 === round.length ? "Finish round" : "Next question →"}</Button>
      </div>}
    </Card>
  </>;
}
