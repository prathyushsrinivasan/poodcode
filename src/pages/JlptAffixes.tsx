import { useEffect, useRef, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { Badge, Button, Card, ErrorState, PageHeader, ProgressBar } from "../components/ui";
import { useCrumb } from "../store";
import { AFFIX_LESSONS, AFFIX_PROGRESS_KEY, AFFIX_QUESTIONS, type AffixQuestion } from "../data/jlptAffixes";
import { drawAffixRound, filterAffixQuestions, type AffixFilters } from "../lib/jlptAffixes";
import { n2Stats, type N2Progress } from "../lib/jlptN2";
import { optionOrder } from "../lib/quizShuffle";
import { useN2Progress } from "../lib/useN2Progress";

const BASE = "/japanese/n2/affixes";
const AFFIXES = [...new Set(AFFIX_QUESTIONS.map((q) => q.answer))].sort((a, b) => a.localeCompare(b, "ja"));

export default function JlptAffixes() {
  const { lessonId } = useParams();
  const [params, setParams] = useSearchParams();
  const lesson = AFFIX_LESSONS.find((l) => l.id === lessonId);
  const mode = lessonId === "mixed" ? "mixed" : lessonId === "review" ? "review" : "lesson";
  const level = params.get("level"), kind = params.get("kind");
  const filters: AffixFilters = {
    level: level === "N3" || level === "N2" || level === "N1" ? level : "all",
    kind: kind === "prefix" || kind === "suffix" ? kind : "all",
    affix: AFFIXES.includes(params.get("affix") ?? "") ? params.get("affix")! : "",
    query: params.get("q") ?? "",
  };
  const size = [10, 20, 50].includes(Number(params.get("size"))) ? Number(params.get("size")) : 10;
  const search = params.size ? `?${params}` : "";
  const state = useN2Progress(AFFIX_PROGRESS_KEY, AFFIX_QUESTIONS);
  const [run, setRun] = useState(0);
  useCrumb(lesson?.title ?? null, "Affix lesson");

  if (lessonId && !lesson && mode === "lesson") return <div className="page"><PageHeader title="Lesson not found" />
    <Link to={BASE}>Choose a prefix or suffix lesson</Link></div>;
  if (state.loadError) return <div className="page"><PageHeader title="Prefixes & Suffixes" />
    <ErrorState title="Your affix progress could not be loaded." error={state.loadError} onRetry={state.retryLoad} /></div>;
  if (!state.progress) return <div className="page" role="status">Loading your prefix and suffix practice…</div>;

  const pool = filterAffixQuestions(filters, lesson?.questions ?? AFFIX_QUESTIONS);
  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(params);
    if (value && value !== "all") next.set(key, value); else next.delete(key);
    setParams(next, { replace: true });
  }
  return <div className="page n2-page">
    <div className="n2-actions"><Link className="ghost-link" to="/japanese/n2/library">← JLPT course library</Link>
      {lessonId && <Link className="ghost-link" to={`${BASE}${search}`}>← Prefix &amp; suffix library</Link>}</div>
    <PageHeader eyebrow="JLPT N3–N1 practice · 語形成 · 接頭辞・接尾辞"
      title={mode === "review" ? "Review affix mistakes" : mode === "mixed" ? "Mixed affix practice" : lesson?.title ?? "Prefixes & Suffixes"}
      subtitle={lessonId ? "Choose the one prefix or suffix that completes the word in context."
        : `${AFFIX_QUESTIONS.length} four-choice problems · 100 per level · ${AFFIX_LESSONS.length} pattern families`} />
    {state.saveError && <Card tone="warn"><p role="alert">Your latest progress has not been saved. Keep this page open and retry.</p>
      <Button onClick={state.retrySave}>Retry saving progress</Button></Card>}
    {lessonId ? <AffixSession key={`${lessonId}-${search}-${run}`} questions={pool} progress={state.progress} mode={mode}
      size={size} onRecord={state.record} onRestart={() => setRun((n) => n + 1)} back={`${BASE}${search}`} />
      : <AffixIndex questions={pool} progress={state.progress} filters={filters} size={size} search={search} onFilter={updateFilter} />}
  </div>;
}

function AffixIndex({ questions, progress, filters, size, search, onFilter }: {
  questions: AffixQuestion[]; progress: N2Progress; filters: AffixFilters; size: number; search: string;
  onFilter: (key: string, value: string) => void;
}) {
  const stats = n2Stats(questions, progress);
  const lessons = AFFIX_LESSONS.map((lesson) => ({ lesson,
    questions: questions.filter((q) => q.lessonId === lesson.id) })).filter((row) => row.questions.length);
  const next = lessons.find((l) => n2Stats(l.questions, progress).correct < l.questions.length) ?? lessons[0];
  return <>
    <Card className="n2-overview">
      <strong>{stats.correct} / {stats.total} correct on latest attempt</strong>
      <p>{stats.attempted} practiced · {stats.missed} to revisit in the current selection. Progress is saved for each question.</p>
      <ProgressBar value={stats.correct} max={stats.total || 1} label="Selected affix questions correct on latest attempt" />
      <div className="n2-actions">
        {next && <Link className="btn primary" to={`${BASE}/${next.lesson.id}${search}`}>{stats.attempted ? "Continue practice" : "Start practice"}</Link>}
        {!!questions.length && <Link className="btn" to={`${BASE}/mixed${search}`}>Try {Math.min(size, questions.length)} mixed questions</Link>}
        {!!stats.missed && <Link className="btn" to={`${BASE}/review${search}`}>Review {stats.missed} mistakes</Link>}
      </div>
    </Card>
    <details><summary>How to solve word-formation questions</summary>
      <Card><p lang="ja">（　）に入れるのに最もよいものを、１・２・３・４から一つ選びなさい。</p>
        <ol className="n2-tips">
          <li>Read the full sentence. Decide whether the missing part comes before a base word (接頭辞) or after it (接尾辞).</li>
          <li>Check the meaning: absence, repetition, status, degree, a person, a quality, or a tendency.</li>
          <li>Join each choice to the base. Choose an established word that fits the grammar and the context.</li>
          <li>After checking, read the completed sentence, full-word reading, translation, and explanation. Mix families to practice without a pattern hint.</li>
        </ol>
        <p className="n2-meta">These are original preparation exercises. N3, N2 and N1 are study estimates. The dedicated 語形成 question type is listed at N2 in the
          {" "}<a href="https://www.jlpt.jp/e/guideline/testsections.html" target="_blank" rel="noreferrer">official JLPT test outline</a>.
          Practice here also includes verb endings and time expressions to build word-formation skills across levels.</p>
      </Card>
    </details>
    <div className="affix-filters">
      <label className="n2-search">Study level<select value={filters.level} onChange={(e) => onFilter("level", e.target.value)}>
        <option value="all">All levels · 300</option>{(["N3", "N2", "N1"] as const).map((l) => <option key={l} value={l}>{l} · 100</option>)}
      </select></label>
      <label className="n2-search">Word position<select value={filters.kind} onChange={(e) => onFilter("kind", e.target.value)}>
        <option value="all">Prefixes &amp; suffixes</option><option value="prefix">Prefixes · 接頭辞</option><option value="suffix">Suffixes &amp; endings · 接尾辞</option>
      </select></label>
      <label className="n2-search">Target affix<select value={filters.affix} onChange={(e) => onFilter("affix", e.target.value)}>
        <option value="">All affixes</option>{AFFIXES.map((a) => <option key={a} value={a}>{a}</option>)}
      </select></label>
      <label className="n2-search">Mixed round size<select value={size} onChange={(e) => onFilter("size", e.target.value)}>
        {[10, 20, 50].map((n) => <option key={n} value={n}>{n} questions</option>)}
      </select></label>
    </div>
    <label className="n2-search">Find an affix, word, reading or meaning
      <input type="search" value={filters.query} onChange={(e) => onFilter("q", e.target.value)} placeholder="e.g. 名選手, せんしゅ, absence, だらけ" />
    </label>
    <div className="n2-actions"><p className="n2-meta" role="status">{questions.length} matching {questions.length === 1 ? "question" : "questions"} · {lessons.length} {lessons.length === 1 ? "family" : "families"}</p>
      {(filters.level !== "all" || filters.kind !== "all" || filters.affix || filters.query) && <Link to={BASE}>Clear filters</Link>}</div>
    <div className="n2-grid">{lessons.map(({ lesson, questions: matching }) => {
      const s = n2Stats(matching, progress);
      return <Link key={lesson.id} className="card n2-lesson" to={`${BASE}/${lesson.id}${search}`}>
        <div className="n2-actions"><Badge>{lesson.level} · {lesson.kind === "prefix" ? "Prefix" : "Suffix / ending"}</Badge>
          <span className="n2-meta">{matching.length} questions</span></div>
        <h2>{lesson.title}</h2><p>{lesson.rule}</p>
        <ProgressBar value={s.correct} max={s.total} label={`${lesson.title}: correct on latest attempt`} />
        <span className="n2-meta">{s.correct}/{s.total} correct · Open family →</span>
      </Link>;
    })}</div>
    {!lessons.length && <Card><h2>No questions match these filters</h2><p>Try another level, affix, or search term.</p><Link to={BASE}>Show all 300 questions</Link></Card>}
  </>;
}

function AffixSession({ questions, progress, mode, size, onRecord, onRestart, back }: {
  questions: AffixQuestion[]; progress: N2Progress; mode: "lesson" | "mixed" | "review"; size: number;
  onRecord: (id: string, correct: boolean) => void; onRestart: () => void; back: string;
}) {
  const [seed] = useState(() => Math.floor(Math.random() * 0x100000000));
  const [round] = useState(() => drawAffixRound(questions, progress, mode, size, seed));
  const [position, setPosition] = useState(0);
  const [answer, setAnswer] = useState<string | null>(null);
  const [result, setResult] = useState<"correct" | "incorrect" | "revealed" | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [hint, setHint] = useState(false);
  const submitted = useRef(false);
  const firstRef = useRef<HTMLInputElement>(null);
  const nextRef = useRef<HTMLButtonElement>(null);
  useEffect(() => { firstRef.current?.focus(); }, [position]);
  useEffect(() => { if (result) nextRef.current?.focus(); }, [result]);
  const q = round[position];
  if (!round.length) return <Card><h2>{mode === "review" ? "No affix mistakes waiting" : "No questions in this selection"}</h2>
    <p>{mode === "review" ? "Missed and revealed questions appear here until you solve them correctly." : "Change your filters to find more questions."}</p>
    <Link to={back}>Back to the affix library →</Link></Card>;
  if (!q) return <Card className="n2-finish"><Badge tone="good">Round complete</Badge>
    <h2>{correctCount} / {round.length} correct this round</h2>
    <p>Missed and revealed answers stay in mistake review until a correct attempt.</p>
    <div className="n2-actions"><Button variant="primary" onClick={onRestart}>{mode === "mixed" ? "Try another mixed round" : "Practice again"}</Button>
      <Link to={back}>Back to the affix library →</Link></div></Card>;
  const lesson = AFFIX_LESSONS.find((l) => l.id === q.lessonId)!;
  const choices = optionOrder(q.id, q.choices.length, String(seed)).map((i) => q.choices[i]);
  const [before, after] = q.sentence.split("___");
  function submit(reveal = false) {
    if (submitted.current || (!reveal && answer === null)) return;
    submitted.current = true;
    const correct = !reveal && answer === q.answer;
    setResult(reveal ? "revealed" : correct ? "correct" : "incorrect");
    if (correct) setCorrectCount((n) => n + 1);
    onRecord(q.id, correct);
  }
  function next() {
    submitted.current = false;
    setAnswer(null); setResult(null); setHint(false); setPosition((n) => n + 1);
  }
  return <Card className="n2-exercise">
    <div className="n2-actions"><Badge>{q.level} · {q.kind === "prefix" ? "接頭辞 · Prefix" : "接尾辞 · Suffix / ending"}</Badge>
      <span className="n2-meta">Question {position + 1} of {round.length}</span></div>
    <ProgressBar value={position} max={round.length} label="Affix questions completed this round" />
    <h2 className="sr-only">Choose the missing prefix or suffix</h2>
    <p className="n2-sentence" lang="ja">{before}<span className="n2-blank">（　　）</span>{after}</p>
    <form onSubmit={(e) => { e.preventDefault(); submit(); }}>
      <fieldset className="n2-choice-group" disabled={!!result}><legend>Which choice completes the word?</legend>
        <div className="n2-choices">{choices.map((choice, i) => <label key={`${q.id}-${choice}`} className={`n2-choice ${answer === choice ? "is-selected" : ""}`}>
          <input ref={i === 0 ? firstRef : undefined} type="radio" name={`affix-${q.id}`} value={choice}
            checked={answer === choice} onChange={() => setAnswer(choice)} /><strong>{i + 1}</strong><span lang="ja">{choice}</span>
        </label>)}</div>
      </fieldset>
      {!result && <div className="n2-actions"><Button type="submit" variant="primary" disabled={answer === null}>Check answer</Button>
        <Button variant="ghost" onClick={() => setHint((v) => !v)} aria-expanded={hint}>{hint ? "Hide hint" : "Show pattern hint"}</Button>
        <Button variant="ghost" onClick={() => submit(true)}>Show answer · revisit later</Button></div>}
      {hint && !result && <p className="n2-hint">{lesson.rule}</p>}
    </form>
    {result && <div className="n2-feedback">
      <p role="status"><Badge tone={result === "correct" ? "good" : "warn"}>{result === "correct" ? "Correct answer"
        : result === "revealed" ? "Answer revealed · added to review" : "Not quite · added to review"}</Badge></p>
      {result !== "revealed" && <p>Your choice: {choices.indexOf(answer!) + 1} — <span lang="ja">{answer}</span></p>}
      <p><strong>Answer: {choices.indexOf(q.answer) + 1} — <span lang="ja">{q.answer}</span></strong></p>
      <p className="n2-sentence" lang="ja">{before}<span className="n2-solution">{q.answer}</span>{after}</p>
      <p lang="ja"><strong>{q.word}</strong> · {q.reading}</p><p>{q.translation}</p>
      <h3>Why this fits</h3><p>{q.explanation}</p><p className="n2-meta">{lesson.rule}</p>
      <Button ref={nextRef} variant="primary" onClick={next}>{position + 1 === round.length ? "Finish round" : "Next question →"}</Button>
    </div>}
  </Card>;
}
