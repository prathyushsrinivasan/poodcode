import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Badge, Button, Card, ErrorState, PageHeader, ProgressBar } from "../components/ui";
import { useCrumb } from "../store";
import { N2_ASSEMBLY_LESSONS, N2_ASSEMBLY_QUESTIONS, N2_ASSEMBLY_PROGRESS_KEY,
  assemblyAnswer, type N2AssemblyQuestion } from "../data/jlptN2SentenceOrder";
import { n2ResumeIndex, n2Stats, type N2Progress } from "../lib/jlptN2";
import { useN2Progress } from "../lib/useN2Progress";

const BASE = "/japanese/n2/sentence-order";
const TIPS = [
  ["Read both printed ends first", "The text after the blanks often tells you what must come last: a noun needs a modifier; です needs a noun/adjective phrase; いる may need a て-form. Read the context sentence too."],
  ["Glue fragments into small blocks", "Look for strong links: いくつあるか → わからない; plain clause → と思う; noun + の → ため; さえ → ば; verb stem → かねない. Treat a reliable pair as one block."],
  ["Find the noun behind a long modifier", "In 捨てられずにいる → 古い服が, the whole preceding clause describes the clothes. A particle after the noun belongs to the main sentence; do not make it the subject of the relative clause by accident."],
  ["Use particles to identify jobs", "を usually points to an object, に to a target/time, で to a place/means, and が to a subject. Find the verb that needs each phrase. Particles constrain the order, but do not make every ordering unique by themselves."],
  ["Check endings and tense", "読んだ上で means after reading; 読む上で means in reading/as regards reading. たとたん and て以来 also constrain the preceding form. Never move a printed ending into your answer."],
  ["Test every join, then check the meaning", "Use all four fragments once. Read from the printed beginning through the assembled fragments to the printed ending. Check who did what, the time sequence, and whether the contrast or cause makes sense."],
  ["Report the choice number at ★", "The slot number and the answer number are different. If the full order is 4 → 1 → 3 → 2 and ★ is slot 3, select choice 3. Do not submit the third number in the choice list automatically."],
  ["Use a personal time budget", "Practice accuracy first. Then try a five-question set with your own time target. If stuck, lock a reliable pair, test the remaining positions, mark your best answer and move on. Review the failed connection afterward."],
];

function StrategyGuide() {
  return <Card>
    <h2>How to solve ★ questions</h2>
    <p lang="ja">次の文の ★ に入る最もよいものを、１・２・３・４から一つ選びなさい。</p>
    <p>Arrange all four fragments into one grammatical, meaningful sentence. Submit only the number of the fragment at ★.
      In this course ★ is displayed in the third slot; always count the slots on the actual question.</p>
    <ol className="n2-tips">{TIPS.map(([title, body]) => <li key={title}><strong>{title}.</strong> {body}</li>)}</ol>
    <p className="n2-meta">The general format is listed in the <a href="https://www.jlpt.jp/e/guideline/testsections.html" target="_blank" rel="noreferrer">official JLPT test outline</a>.
      The solving methods here are study advice. The 120 new exercises are original preparation material, with foundation drills before the harder N2 grammar; they are not official exam questions.</p>
  </Card>;
}

export default function JlptN2SentenceOrder() {
  const { lessonId } = useParams();
  const lesson = N2_ASSEMBLY_LESSONS.find((l) => l.id === lessonId);
  const reviewing = lessonId === "review";
  const mixed = lessonId === "mixed";
  useCrumb(lesson?.title ?? null, "Assembly lesson");
  const state = useN2Progress(N2_ASSEMBLY_PROGRESS_KEY, N2_ASSEMBLY_QUESTIONS);
  const [run, setRun] = useState(0);
  const valid = !lessonId || lesson || reviewing || mixed;

  if (!valid) return <div className="page"><PageHeader title="Lesson not found" /><Link to={BASE}>Choose an assembly lesson</Link></div>;
  if (state.loadError) return <div className="page"><PageHeader title="Sentence Assembly ★" />
    <ErrorState title="Your course progress could not be loaded." error={state.loadError} onRetry={state.retryLoad} /></div>;
  if (!state.progress) return <div className="page" role="status">Loading your sentence assembly course…</div>;

  const questions = reviewing
    ? N2_ASSEMBLY_QUESTIONS.filter((q) => state.progress?.[q.id] && !state.progress[q.id].lastCorrect)
    : mixed ? N2_ASSEMBLY_QUESTIONS : lesson?.questions;
  return <div className="page n2-page">
    <Link className="ghost-link" to="/japanese/n2">← JLPT N2 courses</Link>
    {lessonId && <Link className="ghost-link" to={BASE}>← All assembly lessons &amp; tips</Link>}
    <PageHeader eyebrow="JLPT N2 · 文の組み立て"
      title={reviewing ? "Revisit assembly mistakes" : mixed ? "Five-question mixed practice" : lesson?.title ?? "Sentence Assembly ★"}
      subtitle={lessonId ? "Use all four fragments. Choose the number that belongs at ★."
        : `${N2_ASSEMBLY_QUESTIONS.length} questions: your five examples and 120 original exercises in 24 grammar families.`} />
    {state.saveError && <Card tone="warn"><p role="alert">Your latest progress has not been saved. Keep this page open and retry.</p>
      <Button onClick={state.retrySave}>Retry saving progress</Button></Card>}
    {questions ? <AssemblySession key={`${lessonId}-${run}`} questions={questions} progress={state.progress}
      reviewing={reviewing} mixed={mixed} onRecord={state.record} onRestart={() => setRun((n) => n + 1)} />
      : <AssemblyIndex progress={state.progress} />}
    {lessonId && <details><summary>General solving tips</summary><StrategyGuide /></details>}
  </div>;
}

function AssemblyIndex({ progress }: { progress: N2Progress }) {
  const [query, setQuery] = useState("");
  const stats = n2Stats(N2_ASSEMBLY_QUESTIONS, progress);
  const next = N2_ASSEMBLY_LESSONS.find((l) => n2Stats(l.questions, progress).correct < l.questions.length) ?? N2_ASSEMBLY_LESSONS[0];
  const search = query.trim().toLowerCase();
  const lessons = N2_ASSEMBLY_LESSONS.filter((l) => `${l.title} ${l.strategy} ${l.questions.map((q) =>
    `${q.before} ${q.choices.join(" ")} ${q.after} ${q.translation}`).join(" ")}`.toLowerCase().includes(search));
  return <>
    <Card className="n2-overview">
      <strong>{stats.correct} / {stats.total} correct on latest attempt</strong>
      <p>{stats.attempted} practiced · {stats.missed} to revisit. This course saves progress separately from the blank-filling course.</p>
      <ProgressBar value={stats.correct} max={stats.total} label="Assembly questions correct on latest attempt" />
      <div className="n2-actions">
        <Link className="btn primary" to={`${BASE}/${next.id}`}>{stats.attempted ? "Continue course" : "Start with your examples"}</Link>
        <Link className="btn" to={`${BASE}/mixed`}>Try 5 mixed questions</Link>
        {stats.missed > 0 && <Link className="btn" to={`${BASE}/review`}>Review {stats.missed} mistakes</Link>}
      </div>
    </Card>
    <StrategyGuide />
    <label className="n2-search">Find an assembly pattern or sentence
      <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="e.g. わけ, condition, かねない" />
    </label>
    <div className="n2-grid">{lessons.map((l) => {
      const s = n2Stats(l.questions, progress);
      return <Link key={l.id} to={`${BASE}/${l.id}`} className="card n2-lesson">
        <div className="n2-actions"><Badge>{l.id === "examples" ? "Your examples" : Number(l.id.slice(1)) <= 6 ? "Foundation" : "N2 patterns"}</Badge>
          <span className="n2-meta">5 questions</span></div>
        <h2>{l.title}</h2><p>{l.strategy}</p>
        <ProgressBar value={s.correct} max={s.total} label={`${l.title}: correct on latest attempt`} />
        <span className="n2-meta">{s.correct}/5 correct · Open lesson →</span>
      </Link>;
    })}</div>
    {!lessons.length && <p role="status">No lessons match this search.</p>}
  </>;
}

function AssemblySession({ questions, progress, reviewing, mixed, onRecord, onRestart }: {
  questions: N2AssemblyQuestion[]; progress: N2Progress; reviewing: boolean; mixed: boolean;
  onRecord: (id: string, correct: boolean) => void; onRestart: () => void;
}) {
  // Snapshot the round so a corrected review answer never removes the next item.
  const [round] = useState(() => {
    if (mixed) {
      const pool = [...questions];
      for (let i = pool.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pool[i], pool[j]] = [pool[j], pool[i]];
      }
      return pool.slice(0, 5);
    }
    const start = reviewing ? 0 : n2ResumeIndex(questions, progress);
    return [...questions.slice(start), ...questions.slice(0, start)];
  });
  const [position, setPosition] = useState(0);
  const [answer, setAnswer] = useState<number | null>(null);
  const [scratch, setScratch] = useState<number[]>([]);
  const [hint, setHint] = useState(false);
  const [result, setResult] = useState<"correct" | "incorrect" | "revealed" | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const submitted = useRef(false);
  const nextRef = useRef<HTMLButtonElement>(null);
  const firstRef = useRef<HTMLInputElement>(null);
  useEffect(() => { firstRef.current?.focus(); }, [position]);
  useEffect(() => { if (result) nextRef.current?.focus(); }, [result]);
  const q = round[position];
  const lesson = N2_ASSEMBLY_LESSONS.find((l) => l.questions.some((item) => item.id === q?.id));

  if (!round.length) return <Card><h2>No assembly mistakes waiting</h2>
    <p>Missed questions and revealed answers appear here until you solve them.</p><Link to={BASE}>Choose a lesson →</Link></Card>;
  if (!q) return <Card className="n2-finish"><Badge tone="good">Round complete</Badge>
    <h2>{correctCount} / {round.length} correct this round</h2>
    <p>Review the connections that slowed you down, then try again without the explanation.</p>
    <div className="n2-actions"><Button variant="primary" onClick={onRestart}>{mixed ? "Try another 5" : "Practice again"}</Button>
      <Link to={BASE}>Choose another lesson →</Link></div></Card>;

  function submit(reveal = false) {
    if (submitted.current || (!reveal && answer === null)) return;
    submitted.current = true;
    const correct = !reveal && answer === assemblyAnswer(q);
    setResult(reveal ? "revealed" : correct ? "correct" : "incorrect");
    if (correct) setCorrectCount((n) => n + 1);
    onRecord(q.id, correct);
  }
  function next() {
    submitted.current = false;
    setAnswer(null); setScratch([]); setHint(false); setResult(null); setPosition((n) => n + 1);
  }
  function addFragment(n: number) {
    const order = [...scratch, n];
    setScratch(order);
    if (order.length === 4) setAnswer(order[q.starIndex]);
  }
  return <Card className="n2-exercise">
    <div className="n2-actions"><Badge>文の組み立て · ★ slot {q.starIndex + 1}</Badge>
      <span className="n2-meta">Question {position + 1} of {round.length}</span></div>
    <ProgressBar value={position} max={round.length} label="Assembly questions completed in this round" />
    <h2 className="sr-only">Choose the fragment at the star</h2>
    <p className="n2-sentence" lang="ja">{q.before}{[0, 1, 2, 3].map((slot) =>
      <span key={slot} className={`n2-slot ${slot === q.starIndex ? "n2-star" : ""}`}
        aria-label={`Slot ${slot + 1}${slot === q.starIndex ? ", star" : ""}`}>{slot === q.starIndex ? "★" : "____"}</span>)}{q.after}</p>
    {lesson?.id === "examples" && <p className="n2-meta">Your pasted example · ★ assumed to be slot 3 because the blank positions were omitted.</p>}
    <form onSubmit={(e) => { e.preventDefault(); submit(); }}>
      <fieldset className="n2-choice-group" disabled={!!result}>
        <legend>Which fragment belongs at ★?</legend>
        <div className="n2-choices">{q.choices.map((choice, i) => <label key={i} className={`n2-choice ${answer === i + 1 ? "is-selected" : ""}`}>
          <input ref={i === 0 ? firstRef : undefined} type="radio" name={`star-${q.id}`} value={i + 1}
            checked={answer === i + 1} onChange={() => setAnswer(i + 1)} />
          <strong>{i + 1}</strong><span lang="ja">{choice}</span>
        </label>)}</div>
      </fieldset>
      {!result && <>
        <details className="n2-scratch" key={q.id}>
          <summary>Build the full sentence (optional scratchpad)</summary>
          <p>Tap fragments in reading order. Filling all four selects the fragment at ★; you can still change your answer above.</p>
          <p className="n2-scratch-preview" lang="ja">{q.before}{[0, 1, 2, 3].map((slot) => <span key={slot}
            className={slot === q.starIndex ? "n2-star" : ""}>{slot === q.starIndex && "★ "}{scratch[slot] ? q.choices[scratch[slot] - 1] : "____"} </span>)}{q.after}</p>
          <div className="n2-actions">{q.choices.map((choice, i) => <Button key={i} disabled={scratch.includes(i + 1)} onClick={() => addFragment(i + 1)}>
            {i + 1}. <span lang="ja">{choice}</span></Button>)}
            <Button variant="ghost" disabled={!scratch.length} onClick={() => { setScratch([]); setAnswer(null); }}>Clear arrangement</Button></div>
        </details>
        <div className="n2-actions"><Button type="submit" variant="primary" disabled={answer === null}>Check answer</Button>
          <Button variant="ghost" onClick={() => setHint((value) => !value)} aria-expanded={hint}>{hint ? "Hide hint" : "Show pattern hint"}</Button>
          <Button variant="ghost" onClick={() => submit(true)}>Show answer · revisit later</Button></div>
        {hint && <p className="n2-hint"><strong>Connection to look for:</strong> {lesson?.strategy}</p>}
      </>}
    </form>
    {result && <div className="n2-feedback">
      <p role="status"><Badge tone={result === "correct" ? "good" : "warn"}>{result === "correct" ? "Correct ★ answer"
        : result === "revealed" ? "Answer revealed · added to review" : "Not quite · added to review"}</Badge></p>
      <p>{result !== "revealed" && <>Your choice: {answer}. </>}<strong>★ answer: {assemblyAnswer(q)} — <span lang="ja">{q.choices[assemblyAnswer(q) - 1]}</span></strong></p>
      <p><strong>Full order:</strong> {q.order.join(" → ")}. ★ is slot {q.starIndex + 1}.</p>
      <p className="n2-sentence" lang="ja">{q.before}{q.order.map((n, slot) => <span key={slot}
        className={slot === q.starIndex ? "n2-solution" : ""}>{q.choices[n - 1]}</span>)}{q.after}</p>
      <p>{q.translation}</p><h3>Why this order works</h3><p>{q.explanation}</p>
      <p className="n2-meta">Progress checks the fragment at ★, as the question asks. Use the complete solution to check the rest of your arrangement.</p>
      <Button ref={nextRef} variant="primary" onClick={next}>{position + 1 === round.length ? "Finish round" : "Next question →"}</Button>
    </div>}
  </Card>;
}
