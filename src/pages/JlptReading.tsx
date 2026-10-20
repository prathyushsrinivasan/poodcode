import { useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { Badge, Button, Card, ErrorState, PageHeader, ProgressBar } from "../components/ui";
import { READING_PASSAGES, READING_SECTIONS, READING_TIPS } from "../data/dokkai";
import { filterReadings, nextReading, readingStats, type ReadingMode, type ReadingStatus } from "../lib/dokkai";
import { characterCount } from "../lib/dokkaiText";
import { useReadingProgress, type ReadingState } from "../lib/useReadingProgress";
import { useCrumb } from "../store";
import ReadingSession from "./reading/ReadingSession";
import ReadingVocabulary from "./reading/ReadingVocabulary";

export const READING_BASE = "/japanese/n2/reading";
export default function JlptReading() {
  const { section, passageId } = useParams();
  const [params] = useSearchParams();
  const current = READING_SECTIONS.find((s) => s.id === section);
  const passage = READING_PASSAGES.find((p) => p.id === passageId && p.kind === section);
  const loading = useReadingProgress();
  const [run, setRun] = useState(0);
  useCrumb(passage?.title ?? (passageId === "practice" ? "Practice" : current?.name) ?? (section === "vocabulary" ? "Reading vocabulary" : null), "Reading section", passageId && current ? [current.name] : []);
  const valid = !section || section === "vocabulary" && !passageId || current && (!passageId || passage || passageId === "practice");
  if (!valid) return <div className="page n2-page"><PageHeader title="Reading section not found" /><Link to={READING_BASE}>Choose a reading section</Link></div>;
  if (loading.loadError) return <div className="page"><PageHeader title="読解 · Reading" /><ErrorState title="Reading progress could not be loaded" error={loading.loadError} onRetry={loading.retryLoad} /></div>;
  if (!loading.progress) return <div className="page" role="status">Loading your reading practice…</div>;
  const state: ReadingState = { ...loading, progress: loading.progress };
  const pool = current ? READING_PASSAGES.filter((p) => p.kind === current.id) : READING_PASSAGES;
  const ids = params.get("ids")?.split(",");
  const practicePool = ids ? pool.filter((p) => ids.includes(p.id)) : pool;
  return <div className="page n2-page dokkai-page">
    <div className="n2-actions"><Link className="ghost-link" to="/japanese/n2">← JLPT N2 courses</Link>
      {section && <Link className="ghost-link" to={READING_BASE}>← All reading sections</Link>}
      {passageId && <Link className="ghost-link" to={`${READING_BASE}/${section}`}>← Passage library</Link>}</div>
    <PageHeader eyebrow="JLPT N2 · 読解（どっかい）" title={section === "vocabulary" ? "Reading vocabulary" : passage?.title ?? (passageId === "practice" ? `${current?.name} · Practice` : current ? `${current.name} · ${current.english}` : "読解 · Reading")}
      subtitle={passageId ? "Read the passage, choose the best answer, then review the evidence."
        : "Original practice material. Study with clickable vocabulary or test yourself under a time limit."} />
    {state.saveError && <Card tone="warn"><p role="alert">Your latest changes have not been saved. Keep this page open and retry.</p><Button onClick={state.retrySave}>Retry saving</Button></Card>}
    {section === "vocabulary" ? <ReadingVocabulary state={state} /> : passageId ? <ReadingSession key={`${section}-${passageId}-${params.toString()}-${run}`}
      passages={passage ? [passage] : practicePool} state={state} timed={params.get("mode") === "timed"}
      mixed={!passage && params.get("round") !== "set"} minutes={params.get("minutes")} onRestart={() => setRun((n) => n + 1)} />
      : current ? <ReadingLibrary key={section} passages={pool} state={state} section={current.id} /> : <ReadingOverview state={state} />}
  </div>;
}

function ReadingOverview({ state }: { state: ReadingState }) {
  const stats = readingStats(READING_PASSAGES, state.progress);
  return <>
    <Card className="n2-overview"><h2>Read, understand, explain</h2>
      <p>{READING_PASSAGES.length} passages · {stats.total} questions · {stats.attempted} attempted · {stats.missed} to revisit</p>
      <ProgressBar value={stats.correct} max={stats.total} label="Reading questions correct on the latest attempt" />
      <div className="n2-actions"><Link className="btn primary" to={`${READING_BASE}/short`}>Practice 短文</Link>
        <Link className="btn" to={`${READING_BASE}/vocabulary`}>Reading vocabulary · {Object.keys(state.progress.words).length} saved</Link></div>
      <p className="n2-meta">Click underlined words for kana and meaning. Study results distinguish independent attempts from attempts using help. Timed answers and explanations are revealed at the end.</p>
    </Card>
    <div className="n2-grid">{READING_SECTIONS.map((s) => {
      const passages = READING_PASSAGES.filter((p) => p.kind === s.id);
      const results = readingStats(passages, state.progress);
      return <Link key={s.id} className="card n2-lesson" to={`${READING_BASE}/${s.id}`}>
        <Badge>{s.length}</Badge><h2 lang="ja">{s.name}</h2><strong>{s.english}</strong><p>{s.description}</p>
        <ProgressBar value={results.correct} max={results.total} label={`${s.name}: latest answers correct`} />
        <span className="n2-meta">{passages.length} passages · {results.total} questions · Open section →</span>
      </Link>;
    })}</div>
  </>;
}

function ReadingLibrary({ passages, state, section }: { passages: typeof READING_PASSAGES; state: ReadingState; section: string }) {
  const [query, setQuery] = useState("");
  const [topic, setTopic] = useState("");
  const [skill, setSkill] = useState("");
  const [level, setLevel] = useState("");
  const [status, setStatus] = useState<ReadingStatus>("all");
  const [resultMode, setResultMode] = useState<ReadingMode | "">("");
  const [page, setPage] = useState(0);
  const [timed, setTimed] = useState(false);
  const [minutes, setMinutes] = useState("");
  const filtered = filterReadings(passages, state.progress, { query, topic, skill, level, status, mode: resultMode || undefined });
  const totalPages = Math.ceil(filtered.length / 10);
  const currentPage = Math.min(page, Math.max(0, totalPages - 1));
  const shown = filtered.slice(currentPage * 10, currentPage * 10 + 10);
  const stats = readingStats(passages, state.progress);
  const next = nextReading(filtered, state.progress);
  const modeParams = new URLSearchParams();
  if (timed) { modeParams.set("mode", "timed"); if (minutes) modeParams.set("minutes", minutes); }
  const practiceLink = (set?: boolean) => {
    const p = new URLSearchParams(modeParams);
    p.set("ids", (set ? shown : filtered).map((item) => item.id).join(","));
    if (set) p.set("round", "set");
    return `${READING_BASE}/${section}/practice?${p.toString()}`;
  };
  function reset() { setPage(0); }
  return <>
    <Card className="n2-overview"><h2>{stats.correct} / {stats.total} latest answers correct</h2>
      <p>{stats.attempted} attempted · {stats.missed} mistakes · {passages.length} passages</p>
      <div className="dokkai-mode-stats">{(["independent", "assisted", "timed"] as const).map((mode) => {
        const s = readingStats(passages, state.progress, mode);
        return <div key={mode}><strong>{mode === "independent" ? "Study · independent" : mode === "assisted" ? "Study · with help" : "Timed practice"}</strong><br />
          <span>{s.correct} / {s.attempted} correct on latest attempts{!s.attempted ? " · No attempts yet" : ""}</span></div>;
      })}</div>
      <Link to={`${READING_BASE}/vocabulary`}>Open saved vocabulary →</Link>
    </Card>
    <Card><h2>Choose your practice</h2>
      <div className="n2-actions"><label className="dokkai-check"><input type="checkbox" checked={timed} onChange={(e) => setTimed(e.target.checked)} /> Timed practice</label>
        {timed && <label className="n2-search">Time limit in minutes (optional)<input type="number" min="1" max="120" value={minutes}
          onChange={(e) => setMinutes(e.target.value)} placeholder="Suggested automatically" /></label>}</div>
      <p className="n2-meta">{timed ? "Vocabulary, furigana, tips and answers stay hidden until the round ends. The suggested budget is practice guidance, not an official test limit." : "Lookups, furigana and tips are available. Using any of these marks that passage's answers as assisted."}</p>
      <div className="n2-actions">{next && <Link className="btn primary" to={`${READING_BASE}/${section}/${next.id}?${modeParams}`}>Continue{status === "mistakes" ? " mistake review" : " practice"}</Link>}
        {!!filtered.length && <><Link className="btn" to={practiceLink()}>Random {Math.min(5, filtered.length)} passages</Link>
          <Link className="btn" to={practiceLink(true)}>Practice this set · {shown.length} passages</Link></>}
        <Button onClick={() => { setStatus("mistakes"); reset(); }}>Review mistakes</Button>
      </div>
    </Card>
    <div className="dokkai-filters">
      <label className="n2-search">Search passages<input type="search" value={query} onChange={(e) => { setQuery(e.target.value); reset(); }} placeholder="Title, topic or Japanese text" /></label>
      <label className="n2-search">Topic<select value={topic} onChange={(e) => { setTopic(e.target.value); reset(); }}><option value="">All topics</option>{[...new Set(passages.map((p) => p.topic))].map((t) => <option key={t}>{t}</option>)}</select></label>
      <label className="n2-search">Reading skill<select value={skill} onChange={(e) => { setSkill(e.target.value); reset(); }}><option value="">All skills</option>{[...new Set(passages.map((p) => p.skill))].map((s) => <option key={s}>{s}</option>)}</select></label>
      <label className="n2-search">Challenge<select value={level} onChange={(e) => { setLevel(e.target.value); reset(); }}><option value="">All challenges</option><option value="1">Foundation</option><option value="2">Standard</option><option value="3">Stretch</option></select></label>
      <label className="n2-search">Show<select value={status} onChange={(e) => { setStatus(e.target.value as ReadingStatus); reset(); }}><option value="all">All passages</option><option value="unattempted">Unattempted questions</option><option value="mistakes">Mistakes</option><option value="bookmarks">Bookmarks</option></select></label>
      <label className="n2-search">Result history<select value={resultMode} onChange={(e) => { setResultMode(e.target.value as ReadingMode | ""); reset(); }}><option value="">Latest across all modes</option><option value="independent">Independent study</option><option value="assisted">Study with help</option><option value="timed">Timed practice</option></select></label>
    </div>
    <div className="n2-actions dokkai-spread"><p role="status">{filtered.length} passages match{totalPages ? ` · Set ${currentPage + 1} of ${totalPages}` : ""}</p>
      <div className="n2-actions"><Button disabled={!currentPage} onClick={() => setPage(currentPage - 1)}>Previous set</Button><Button disabled={currentPage + 1 >= totalPages} onClick={() => setPage(currentPage + 1)}>Next set</Button></div></div>
    {!shown.length && <Card><h2>No matching passages</h2><p>Try another filter, or practice some passages to build a mistake list.</p><Button onClick={() => { setQuery(""); setTopic(""); setSkill(""); setLevel(""); setStatus("all"); setResultMode(""); reset(); }}>Clear filters</Button></Card>}
    <div className="n2-grid">{shown.map((p, i) => {
      const s = readingStats([p], state.progress, resultMode || undefined);
      const saved = state.progress.bookmarks.includes(p.id);
      return <Card key={p.id} className="dokkai-library-card"><div className="n2-actions dokkai-spread"><Badge>{p.skill}</Badge><Button size="sm" aria-pressed={saved} onClick={() => state.bookmark(p.id)}>{saved ? "Bookmarked" : "Bookmark"}</Button></div>
        <h2><Link to={`${READING_BASE}/${section}/${p.id}?${modeParams}`} lang="ja">{currentPage * 10 + i + 1}. {p.title}</Link></h2>
        <p className="n2-meta">{p.topic} · {p.level === 1 ? "Foundation" : p.level === 2 ? "Standard" : "Stretch"} · {p.texts.map((t) => characterCount(t.text)).join(" + ")} characters · {p.questions.length} question{p.questions.length === 1 ? "" : "s"}</p>
        <p className="n2-meta">{s.attempted ? `${s.correct}/${s.total} correct on latest attempt · ${s.missed} to revisit` : "Not practiced yet"}</p>
      </Card>;
    })}</div>
    <details><summary>Reading strategies</summary>{[...new Set(passages.map((p) => p.skill))].map((s) => <p key={s}><strong>{s}:</strong> {READING_TIPS[s]}</p>)}</details>
  </>;
}
