import { useState } from "react";
import { Link } from "react-router-dom";
import { Badge, Button, Card } from "../../components/ui";
import { READING_PASSAGES } from "../../data/dokkai";
import type { ReadingState } from "../../lib/useReadingProgress";

function dueLabel(due: number, now: number): string {
  const minutes = Math.ceil((due - now) / 60_000);
  if (minutes <= 0) return "Due now";
  if (minutes < 60) return `Review in ${minutes} minute${minutes === 1 ? "" : "s"}`;
  const hours = Math.ceil(minutes / 60);
  if (hours < 24) return `Review in ${hours} hour${hours === 1 ? "" : "s"}`;
  const days = Math.ceil(hours / 24);
  return `Review in ${days} day${days === 1 ? "" : "s"}`;
}

export default function ReadingVocabulary({ state }: { state: ReadingState }) {
  const [now, setNow] = useState(Date.now);
  const [reviewing, setReviewing] = useState(false);
  const [round, setRound] = useState<string[]>([]);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [query, setQuery] = useState("");
  const words = Object.entries(state.progress.words);
  const due = words.filter(([, word]) => word.due <= now);
  const word = state.progress.words[round[index]];
  const filtered = words.filter(([, w]) => `${w.text} ${w.reading} ${w.meaning}`.toLowerCase().includes(query.toLowerCase()));
  function grade(remembered: boolean) {
    state.gradeWord(round[index], remembered);
    setFlipped(false); setIndex((n) => n + 1); setNow(Date.now());
  }
  return <>
    <Card className="n2-overview"><h2>{words.length} saved words · {due.length} due</h2>
      <p>Saved from reading passages with their kana, contextual meanings and source. Reveal an answer, then rate your recall. Remembered words return after 1, 2, 4 days and longer; difficult words return in ten minutes.</p>
      <div className="n2-actions"><Button variant="primary" disabled={!due.length} onClick={() => { setRound(due.map(([key]) => key)); setIndex(0); setFlipped(false); setReviewing(true); }}>Review due words</Button>
        <Button onClick={() => setNow(Date.now())}>Refresh due list</Button></div></Card>
    {reviewing && <Card className="n2-overview">{word ? <>
      <Badge>Word {index + 1} of {round.length}</Badge><h2 lang="ja">{word.text}</h2>
      {flipped ? <><p className="dokkai-kana" lang="ja">{word.reading}</p><p>{word.meaning}</p>
        {word.lemma && word.lemma !== word.text && <p>Dictionary form: <span lang="ja">{word.lemma}</span></p>}
        <div className="n2-actions"><Button onClick={() => grade(false)}>Again · 10 minutes</Button><Button variant="primary" onClick={() => grade(true)}>Remembered</Button></div></>
        : <Button variant="primary" onClick={() => setFlipped(true)}>Reveal reading and meaning</Button>}
    </> : <><h2>Vocabulary round complete</h2><p>Your next review times have been saved.</p></>}
      <Button variant="ghost" onClick={() => setReviewing(false)}>Close review</Button></Card>}
    <label className="n2-search">Find a saved word<input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Japanese, kana or meaning" /></label>
    {!filtered.length && <Card><p>{words.length ? "No words match your search." : "Hover over an underlined word in a reading passage, then choose Save for vocabulary review."}</p><Link to="/japanese/n2/reading/short">Open short passages →</Link></Card>}
    <div className="n2-grid">{filtered.map(([key, w]) => {
      const source = READING_PASSAGES.find((p) => p.id === w.source);
      return <Card key={key}><h2 lang="ja">{w.text} <span className="n2-meta">{w.reading}</span></h2><p>{w.meaning}</p>
        <p className="n2-meta">{dueLabel(w.due, now)} · {w.reviews} reviews</p>
        <div className="n2-actions">{source && <Link to={`/japanese/n2/reading/${source.kind}/${source.id}`}>Source: {source.title}</Link>}
          <Button variant="ghost" disabled={reviewing} onClick={() => state.removeWord(key)}>Remove saved word</Button></div></Card>;
    })}</div>
  </>;
}
