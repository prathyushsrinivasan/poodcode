import { useEffect, useRef, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { Badge, Button, Card, ErrorState, PageHeader, ProgressBar } from "../components/ui";
import { KANJI_GROUPS, KANJI_WORDS, KANJI_WORD_BY_ID, wordsForKanji, type KanjiWord } from "../data/kanjiWords";
import { gradeKanjiMeaning, gradeKanjiReading, isHiragana, kanjiStats, kanjiWordComplete, kanjiWordNeedsReview,
  planKanjiRound, validKanjiMeaningSelection, type KanjiProgress, type KanjiSkill } from "../lib/kanjiWords";
import { optionOrder } from "../lib/quizShuffle";
import { useKanjiProgress } from "../lib/useKanjiProgress";
import { useCrumb } from "../store";
import referenceLicense from "../data/kanjiWords/JLPT-LICENSE.txt?raw";
import dictionaryLicense from "../data/kanjiWords/CC-BY-SA-4.0.txt?raw";

const BASE = "/japanese/n2/kanji";
type Mode = "library" | "practice" | "mixed" | "review" | "word";
const matchesWord = (word: KanjiWord, query: string, level: string) => (level === "all" || word.levels.includes(level))
  && `${word.written} ${word.aliases.join(" ")} ${word.readings.join(" ")} ${word.meanings.join(" ")}`.toLowerCase().includes(query.trim().toLowerCase());
const matchesProgress = (word: KanjiWord, progress: KanjiProgress, status: string) => status === "all"
  || (status === "new" && !progress.words[word.id]) || (status === "review" && kanjiWordNeedsReview(progress.words[word.id]))
  || (status === "complete" && kanjiWordComplete(progress.words[word.id]));

export default function JlptKanjiWords({ mode = "library" }: { mode?: Mode }) {
  const { groupId, wordId } = useParams();
  const [params] = useSearchParams();
  const group = KANJI_GROUPS.find((item) => item.id === groupId);
  const word = wordId ? KANJI_WORD_BY_ID.get(wordId) : undefined;
  useCrumb(word?.written ?? group?.kanji ?? null);
  const state = useKanjiProgress();
  const [run, setRun] = useState(0);
  if ((groupId && !group) || (mode === "word" && !word)) return <div className="page n2-page"><h1>Kanji or word not found</h1><Link to={BASE}>Browse the kanji library</Link></div>;
  if (state.loadError) return <div className="page n2-page"><PageHeader title="Kanji Word Builder" />
    <ErrorState title="Your kanji progress could not be loaded." error={state.loadError} onRetry={state.retryLoad} /></div>;
  if (!state.progress) return <div className="page" role="status">Loading kanji practice…</div>;
  const progress = state.progress;
  const pool = mode === "word" ? [word!] : mode === "review" ? KANJI_WORDS.filter((entry) => kanjiWordNeedsReview(progress.words[entry.id]))
    : (group ? wordsForKanji(group.kanji) : KANJI_WORDS).filter((entry) => matchesWord(entry, params.get("q") ?? "", params.get("level") ?? "all")
      && matchesProgress(entry, progress, params.get("status") ?? "all"));
  const title = mode === "word" ? word!.written : mode === "review" ? "Review kanji vocabulary mistakes" : mode === "mixed" ? "Mixed kanji word practice"
    : group ? `${group.kanji} · ${group.gloss}` : "Kanji Word Builder";
  const size = mode === "mixed" ? 5 : params.get("size") === "all" || mode === "review" || mode === "word" ? pool.length : 10;
  return <div className="page n2-page kw-page">
    <div className="n2-actions"><Link className="ghost-link" to="/japanese/n2">← JLPT N2 courses</Link>
      {(group || mode !== "library") && <Link className="ghost-link" to={BASE}>← All 20 kanji</Link>}
      {mode === "practice" && group && <Link className="ghost-link" to={`${BASE}/${group.id}`}>← Word list for {group.kanji}</Link>}</div>
    <PageHeader eyebrow="JLPT N2 preparation · N3–N1 vocabulary" title={title}
      subtitle={mode === "library" ? group ? `Explore every word in this bank containing ${group.kanji}. Practice its reading and meanings together.`
        : `${KANJI_GROUPS.length} kanji · ${KANJI_WORDS.length} vocabulary entries. Type the hiragana, then choose the English meaning or meanings.`
        : "Two steps for each word: recall its hiragana reading, then identify its English meanings."} />
    {state.saveError && <Card tone="warn"><p role="alert">Your latest results have not been saved. Keep this page open and retry.</p>
      <Button onClick={state.retrySave}>Retry saving progress</Button></Card>}
    {mode === "library" ? <Library key={groupId ?? "index"} kanji={group?.kanji} groupId={group?.id} progress={progress} />
      : <Round key={`${mode}:${groupId ?? wordId ?? ""}:${params.toString()}:${run}`} words={pool} size={size} progress={progress}
        onRecord={state.record} onRestart={() => setRun((value) => value + 1)} />}
    <footer className="kw-sources"><p>Vocabulary and estimated levels adapted from <a href="https://github.com/jamsinclair/open-anki-jlpt-decks" target="_blank" rel="noreferrer">Open Anki JLPT</a>,
      with editorial additions. Readings checked against <a href="https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project" target="_blank" rel="noreferrer">JMdict</a> © James William Breen and EDRDG.
      Dictionary-derived data: <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">CC BY-SA 4.0</a>.</p>
      <p>Levels are study estimates, not official JLPT assignments. This is a broad starter bank, rather than an exhaustive dictionary. Synonyms share one option; distinct study senses use separate options.</p>
      <details><summary>Data licenses · available offline</summary><h2>Open Anki JLPT · MIT</h2><pre className="kw-license-text">{referenceLicense}</pre>
        <h2>JMdict and adapted vocabulary · CC BY-SA 4.0</h2><pre className="kw-license-text">{dictionaryLicense}</pre></details></footer>
  </div>;
}

function Library({ kanji, groupId, progress }: { kanji?: string; groupId?: string; progress: KanjiProgress }) {
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("all");
  const [status, setStatus] = useState("all");
  const [showAnswers, setShowAnswers] = useState(false);
  const allWords = kanji ? wordsForKanji(kanji) : KANJI_WORDS;
  const stats = kanjiStats(allWords, progress);
  const filtered = allWords.filter((word) => matchesWord(word, query, level) && matchesProgress(word, progress, status));
  const filters = new URLSearchParams({ q: query, level, status });
  const showWords = !!kanji || query.trim().length > 0 || status !== "all" || level !== "all";
  const groups = KANJI_GROUPS.filter((group) => !query.trim() || `${group.kanji} ${group.gloss}`.toLowerCase().includes(query.trim().toLowerCase())
    || wordsForKanji(group.kanji).some((word) => matchesWord(word, query, level)));
  return <>
    <Card className="n2-overview"><div className="kw-stat-row"><div><strong>{stats.complete} / {stats.total}</strong><span>reading + meaning correct</span></div>
      <div><strong>{stats.readings}</strong><span>readings correct</span></div><div><strong>{stats.meanings}</strong><span>meanings correct</span></div>
      <div><strong>{stats.mistakes}</strong><span>words to revisit</span></div></div>
      <ProgressBar value={stats.complete} max={stats.total} label="Words with reading and meaning correct on latest attempts" />
      <div className="n2-actions">{groupId ? <>
        <Link className={`btn primary ${filtered.length ? "" : "kw-disabled-link"}`} aria-disabled={!filtered.length} tabIndex={filtered.length ? undefined : -1}
          onClick={(event) => { if (!filtered.length) event.preventDefault(); }} to={`${BASE}/${groupId}/practice?${filters}`}>Practice up to 10 words</Link>
        <Link className="btn" to={`${BASE}/${groupId}/practice?${filters}&size=all`}>Practice all {filtered.length} matching words</Link>
      </> : <Link className="btn primary" to={`${BASE}/mixed`}>Practice 5 mixed words</Link>}
        <Link className="btn" to={`${BASE}/review`}>Review mistakes · {kanjiStats(KANJI_WORDS, progress).mistakes}</Link></div>
      <p className="n2-meta">Submitted readings and meanings are saved separately. Words shared by several kanji share one progress record.</p>
    </Card>
    <div className="kw-filters"><label>Find a kanji or word<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="生, せい, life, productivity…" /></label>
      <label>Estimated level<select aria-label="Estimated level" value={level} onChange={(event) => setLevel(event.target.value)}><option value="all">All N3–N1</option><option>N3</option><option>N2</option><option>N1</option></select></label>
      <label>Progress<select aria-label="Progress filter" value={status} onChange={(event) => setStatus(event.target.value)}><option value="all">All words</option><option value="new">Unseen words</option>
        <option value="review">Mistakes</option><option value="complete">Both correct</option></select></label></div>
    {!kanji && <div className="kw-kanji-grid">{groups.map((group) => {
      const words = wordsForKanji(group.kanji);
      const s = kanjiStats(words, progress);
      return <Link className="card kw-kanji-card" to={`${BASE}/${group.id}`} key={group.id}>
        <span lang="ja" className="kw-glyph">{group.kanji}</span><div><h2>{group.gloss}</h2><p>{words.length} words · {s.complete} both correct</p>
          <ProgressBar value={s.complete} max={s.total} label={`${group.kanji}: words with both skills correct`} /></div></Link>;
    })}</div>}
    {showWords && <section className="kw-word-library" aria-labelledby="kw-list-title"><div className="kw-list-heading"><h2 id="kw-list-title">{filtered.length} matching words</h2>
      <label className="kw-check"><input type="checkbox" checked={showAnswers} onChange={(event) => setShowAnswers(event.target.checked)} />Show readings &amp; meanings</label></div>
      <div className="kw-word-grid">{filtered.map((word) => {
        const row = progress.words[word.id];
        return <article key={word.id} className="card kw-word-card"><div className="kw-word-heading"><h3 lang="ja">{word.written}</h3><Badge>{word.levels.join(" / ")} · est.</Badge></div>
          {word.cue && <p lang="ja" className="kw-cue">{word.cue}</p>}
          {showAnswers && <div className="kw-library-answer"><p lang="ja">{word.readings.join(" / ")}</p><ul>{word.meanings.map((meaning) => <li key={meaning}>{meaning}</li>)}</ul></div>}
          <p className="n2-meta">Reading: {row?.reading ? row.reading.lastCorrect ? "correct" : "revisit" : "new"} · Meaning: {row?.meaning ? row.meaning.lastCorrect ? "correct" : "revisit" : "new"}</p>
          <Link className="btn" to={`${BASE}/word/${word.id}`}>Practice {word.written}</Link></article>;
      })}</div>
      {!filtered.length && <p role="status">No words match these filters. Try another search or reset the level and progress filters.</p>}
    </section>}
    {!kanji && !groups.length && <p role="status">No kanji match this search.</p>}
  </>;
}

type RecordResult = (id: string, skill: KanjiSkill, correct: boolean) => void;
function Round({ words, size, progress, onRecord, onRestart }: {
  words: KanjiWord[]; size: number; progress: KanjiProgress; onRecord: RecordResult; onRestart: () => void;
}) {
  const [seed] = useState(() => String(Date.now()));
  const [ids, setIds] = useState(() => planKanjiRound(words, progress, size, seed));
  const [position, setPosition] = useState(0);
  const [results, setResults] = useState<{ id: string; reading: boolean; meaning: boolean }[]>([]);
  const word = KANJI_WORD_BY_ID.get(ids[position]);
  if (!ids.length) return <Card><h2>No matching words to practice</h2><p>There are no mistakes waiting, or your filters match no words.</p><Link to={BASE}>Choose a kanji →</Link></Card>;
  if (!word) {
    const missed = results.filter((row) => !row.reading || !row.meaning).map((row) => row.id);
    return <Card className="n2-finish"><Badge>Round complete</Badge><h2>{results.length - missed.length} / {results.length} words correct in both steps</h2>
      <p>{results.filter((row) => row.reading).length} readings correct · {results.filter((row) => row.meaning).length} meaning quizzes correct. All submitted results are saved.</p>
      <div className="n2-actions"><Button variant="primary" onClick={onRestart}>Practice another round</Button>
        {missed.length > 0 && <Button onClick={() => { setIds(missed); setPosition(0); setResults([]); }}>Retry {missed.length} missed words</Button>}</div>
      <ul className="kw-recap">{results.map((row) => <li key={row.id}><Link to={`${BASE}/word/${row.id}`} lang="ja">{KANJI_WORD_BY_ID.get(row.id)!.written}</Link>
        <span>Reading: {row.reading ? "correct" : "revisit"} · Meaning: {row.meaning ? "correct" : "revisit"}</span></li>)}</ul></Card>;
  }
  return <>
    <div className="kw-round-status"><strong>Word {position + 1} of {ids.length}</strong><span className="n2-meta">Mistakes first, then unfinished words</span></div>
    <ProgressBar value={position} max={ids.length} label="Words completed in this round" />
    <WordExercise key={`${word.id}:${results.length}`} word={word} seed={seed} onRecord={onRecord} onNext={(result) => {
      setResults((value) => [...value, { id: word.id, ...result }]); setPosition((value) => value + 1);
    }} />
    <p className="n2-meta">Submitted results survive navigation and restart. Unsubmitted input and your current round are not saved.</p>
  </>;
}

function WordExercise({ word, seed, onRecord, onNext }: { word: KanjiWord; seed: string; onRecord: RecordResult;
  onNext: (result: { reading: boolean; meaning: boolean }) => void }) {
  const [stage, setStage] = useState<"reading" | "meaning">("reading");
  const [input, setInput] = useState("");
  const [readingResult, setReadingResult] = useState<{ correct: boolean; revealed: boolean } | null>(null);
  const [selected, setSelected] = useState<number[]>([]);
  const [meaningResult, setMeaningResult] = useState<{ correct: boolean; revealed: boolean } | null>(null);
  const composition = useRef(false);
  const submitted = useRef({ reading: false, meaning: false, next: false });
  const readingInput = useRef<HTMLInputElement>(null);
  const advanceButton = useRef<HTMLButtonElement>(null);
  const firstOption = useRef<HTMLInputElement>(null);
  useEffect(() => { readingInput.current?.focus(); }, [word.id]);
  useEffect(() => { if (readingResult || meaningResult) advanceButton.current?.focus(); }, [readingResult, meaningResult]);
  useEffect(() => { if (stage === "meaning") firstOption.current?.focus(); }, [stage]);
  const multiple = word.meanings.length > 1;
  function checkReading(reveal = false) {
    if (submitted.current.reading || composition.current || (!reveal && !isHiragana(input))) return;
    submitted.current.reading = true;
    const correct = !reveal && gradeKanjiReading(word, input);
    setReadingResult({ correct, revealed: reveal });
    onRecord(word.id, "reading", correct);
  }
  function checkMeaning(reveal = false) {
    if (submitted.current.meaning || (!reveal && !validKanjiMeaningSelection(word, selected))) return;
    submitted.current.meaning = true;
    const correct = !reveal && gradeKanjiMeaning(word, selected);
    setMeaningResult({ correct, revealed: reveal });
    onRecord(word.id, "meaning", correct);
  }
  return <Card className="kw-exercise">
    <div className="kw-round-status"><Badge>{stage === "reading" ? "Step 1 of 2 · Hiragana" : "Step 2 of 2 · Meaning"}</Badge><span className="n2-meta">{word.levels.join(" / ")} · estimated</span></div>
    <h2 lang="ja" className="kw-prompt">{stage === "reading" ? word.written : <ruby>{word.written}<rt>{word.readings[0]}</rt></ruby>}</h2>
    {word.cue && <p className="kw-cue" lang="ja">{word.cue}</p>}
    {stage === "reading" ? <>
      <form onSubmit={(event) => { event.preventDefault(); checkReading(); }}>
        <label className="n2-answer" htmlFor="kw-reading">Type the full word in hiragana
          <input id="kw-reading" ref={readingInput} value={input} onChange={(event) => setInput(event.target.value)} lang="ja" type="text" inputMode="text"
            autoComplete="off" autoCapitalize="none" spellCheck={false} disabled={!!readingResult} aria-describedby="kw-reading-help"
            onCompositionStart={() => { composition.current = true; }} onCompositionEnd={() => { composition.current = false; }}
            onKeyDown={(event) => { if (event.key === "Enter" && (event.nativeEvent.isComposing || event.nativeEvent.keyCode === 229 || composition.current)) event.preventDefault(); }} />
        </label><p id="kw-reading-help" className="n2-meta">Use your Japanese IME. Small kana and long vowels count; romaji and katakana are not accepted.</p>
        {!readingResult && <div className="n2-actions"><Button variant="primary" type="submit" disabled={!isHiragana(input)}>Check reading</Button>
          <Button type="button" onClick={() => checkReading(true)}>Reveal reading</Button></div>}
      </form>
      {readingResult && <div className="n2-feedback" role="status"><h3>{readingResult.revealed ? "Reading revealed" : readingResult.correct ? "Reading correct" : "Check the reading"}</h3>
        <p lang="ja" className="kw-reading-result">{word.readings.join(" / ")}</p>
        {!readingResult.correct && <p>{readingResult.revealed ? "This reading is marked for review." : <>Your answer: <span lang="ja">{input}</span>. This reading is marked for review.</>}</p>}
        <Button ref={advanceButton} variant="primary" onClick={() => setStage("meaning")}>Continue to meaning</Button></div>}
    </> : <>
      <form onSubmit={(event) => { event.preventDefault(); checkMeaning(); }}>
        <fieldset className="n2-choice-group" disabled={!!meaningResult}><legend>{multiple ? `Choose all ${word.meanings.length} study meanings` : "Choose the English meaning"}</legend>
          <p className="n2-meta">Meanings apply to this word and reading, beyond the example sentence. Synonyms are grouped into one option.</p>
          <div className="kw-meaning-options">{optionOrder(word.id, word.options.length, seed).map((index, position) => {
            const option = word.options[index];
            return <label key={index} className={`n2-choice ${meaningResult ? option.correct ? "kw-correct" : selected.includes(index) ? "kw-incorrect" : "" : selected.includes(index) ? "is-selected" : ""}`}>
              <span className="kw-choice-line"><input ref={position === 0 ? firstOption : undefined} type={multiple ? "checkbox" : "radio"} name="kw-meaning" value={index}
                checked={selected.includes(index)} onChange={() => setSelected((value) => multiple ? value.includes(index) ? value.filter((item) => item !== index) : [...value, index] : [index])} />
                <span>{option.text}</span></span>
              {meaningResult && <span className="kw-option-reason"><strong>{option.correct ? "Correct" : selected.includes(index) ? "Your answer · Incorrect" : "Incorrect option"}:</strong> {option.explanation}</span>}
            </label>;
          })}</div>
        </fieldset>
        {!meaningResult && <div className="n2-actions"><Button variant="primary" type="submit" disabled={!validKanjiMeaningSelection(word, selected)}>Check meaning</Button>
          <Button type="button" onClick={() => checkMeaning(true)}>Reveal meanings</Button><span className="n2-meta">{selected.length} / {word.meanings.length} selected</span></div>}
      </form>
      {meaningResult && <div className="n2-feedback" role="status"><h3>{meaningResult.revealed ? "Meanings revealed" : meaningResult.correct ? "Meaning correct" : "Review the meanings"}</h3>
        {!meaningResult.correct && <p>All correct meanings must be selected, with no incorrect options. This meaning is marked for review.</p>}
        <p><strong lang="ja">{word.written} · {word.readings.join(" / ")}</strong></p><ul>{word.meanings.map((meaning) => <li key={meaning}>{meaning}</li>)}</ul>
        {word.note && <p className="kw-note">{word.note}</p>}
        <Button ref={advanceButton} variant="primary" onClick={() => { if (submitted.current.next) return; submitted.current.next = true; onNext({ reading: !!readingResult?.correct, meaning: meaningResult.correct }); }}>Next word / results</Button>
      </div>}
    </>}
  </Card>;
}
