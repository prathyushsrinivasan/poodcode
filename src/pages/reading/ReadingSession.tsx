import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Badge, Button, Card, ProgressBar } from "../../components/ui";
import { passageVocabulary, ReadingText, ReadingWordDialog, useWordPopup } from "../../components/ReadingText";
import { READING_PASSAGES, READING_TIPS } from "../../data/dokkai";
import type { ReadingPassage, ReadingWord } from "../../data/dokkai/types";
import { nextReading, readingTimeBudget, type ReadingMode } from "../../lib/dokkai";
import { plainReading } from "../../lib/dokkaiText";
import { shuffleWith } from "../../lib/jpVocab";
import type { ReadingState } from "../../lib/useReadingProgress";

export default function ReadingSession({ passages, state, timed, mixed, minutes, onRestart }: {
  passages: ReadingPassage[]; state: ReadingState; timed: boolean; mixed: boolean; minutes: string | null; onRestart: () => void;
}) {
  // A round is immutable: answering correctly in mistake review cannot remove
  // a passage or move the next question while the learner is reading.
  const [round] = useState(() => mixed ? shuffleWith(passages).slice(0, 5) : [...passages]);
  const [duration] = useState(() => minutes && Number.isFinite(Number(minutes)) && Number(minutes) >= 1 && Number(minutes) <= 120
    ? Math.round(Number(minutes) * 60) : readingTimeBudget(round));
  const [phase, setPhase] = useState<"ready" | "answer" | "review" | "finish">(timed ? "ready" : "answer");
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const answerRef = useRef(answers);
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const checkedRef = useRef(new Set<string>());
  const [aids, setAids] = useState<Record<string, boolean>>({});
  const [revealed, setRevealed] = useState<Record<string, boolean>>({});
  const [recordedModes, setRecordedModes] = useState<Record<string, ReadingMode>>({});
  const [ruby, setRuby] = useState(false);
  const [hint, setHint] = useState(false);
  const [deadline, setDeadline] = useState<number | null>(null);
  const [remaining, setRemaining] = useState(duration);
  const [expired, setExpired] = useState(false);
  const timedRecorded = useRef(false);
  const nextRef = useRef<HTMLButtonElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const popup = useWordPopup();
  const p = round[index];
  const review = phase === "review" || !!checked[p?.id];
  const enabled = !timed || phase === "review";
  const vocabulary = p ? passageVocabulary(p.texts) : [];
  const finalizeRef = useRef<(timeout: boolean) => void>(() => undefined);
  finalizeRef.current = (timeout) => {
    if (timedRecorded.current) return;
    timedRecorded.current = true;
    state.record(round.flatMap((item) => item.questions.map((q) => ({ id: q.id,
      correct: answerRef.current[q.id] === q.answer, mode: "timed" as const }))));
    setExpired(timeout); setPhase("review"); setIndex(0); setDeadline(null); setHint(false);
  };
  useEffect(() => {
    if (!deadline || phase !== "answer") return;
    const tick = () => {
      const left = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
      setRemaining(left);
      if (!left) finalizeRef.current(true);
    };
    tick();
    const timer = window.setInterval(tick, 250);
    return () => window.clearInterval(timer);
  }, [deadline, phase]);
  useEffect(() => { headingRef.current?.focus(); }, [index, phase]);
  useEffect(() => { if (checked[p?.id]) nextRef.current?.focus(); }, [checked, p?.id]);

  if (!round.length) return <Card><h2>No passages in this round</h2><p>Choose some passages from the library to begin.</p><Link to="/japanese/n2/reading">Choose a section →</Link></Card>;
  if (phase === "ready") return <Card className="n2-overview"><h2>Ready for timed practice?</h2>
    <p>{round.length} passages · {round.reduce((n, item) => n + item.questions.length, 0)} questions · {Math.ceil(duration / 60)} minutes</p>
    <p>You can move back and change answers until you finish. Lookups, furigana, translations and explanations open after the round. When time runs out, unanswered questions count as missed.</p>
    <p className="n2-meta">The timer continues while this tab is in the background. Your chosen answers are saved as results when the round ends; finish before leaving this page.</p>
    <Button variant="primary" onClick={() => { setDeadline(Date.now() + duration * 1000); setPhase("answer"); }}>Begin timed practice</Button></Card>;
  const total = round.reduce((n, item) => n + item.questions.length, 0);
  const score = round.reduce((n, item) => n + item.questions.filter((q) => !revealed[item.id] && answers[q.id] === q.answer).length, 0);
  const continueWith = nextReading(READING_PASSAGES.filter((item) => item.kind === round[0].kind), state.progress);
  if (phase === "finish") return <Card className="n2-overview"><Badge tone="good">Round complete</Badge><h2>{score} / {total} correct this round</h2>
    <p>{timed ? "Timed results saved separately from study." : "Study results saved. Answers using vocabulary, furigana or tips are recorded as assisted."} Missed and revealed questions are available in mistake review.</p>
    <div className="n2-actions">{round.length === 1 && continueWith && continueWith.id !== round[0].id && <Link className="btn primary" to={`/japanese/n2/reading/${continueWith.kind}/${continueWith.id}${timed ? "?mode=timed" : ""}`}>Continue to next passage →</Link>}
      <Button onClick={onRestart}>Practice again</Button><Link to={`/japanese/n2/reading/${round[0].kind}`}>Return to passage library →</Link></div></Card>;

  function assist() { if (!timed && !review) setAids((before) => ({ ...before, [p.id]: true })); }
  function openWord(word: ReadingWord) { assist(); popup.open(word); }
  function check(reveal = false) {
    if (checkedRef.current.has(p.id) || timed) return;
    if (!reveal && p.questions.some((q) => answers[q.id] === undefined)) return;
    checkedRef.current.add(p.id);
    const mode: ReadingMode = reveal || aids[p.id] || ruby ? "assisted" : "independent";
    setRecordedModes((before) => ({ ...before, [p.id]: mode }));
    state.record(p.questions.map((q) => ({ id: q.id, correct: !reveal && answers[q.id] === q.answer, mode })));
    if (reveal) setRevealed((before) => ({ ...before, [p.id]: true }));
    setChecked((before) => ({ ...before, [p.id]: true }));
  }
  function next() {
    popup.close(); setHint(false);
    if (index + 1 === round.length) {
      if (timed && phase === "answer") finalizeRef.current(false);
      else setPhase("finish");
    } else setIndex((n) => n + 1);
  }
  const answered = Object.keys(answers).length;
  const bookmark = state.progress.bookmarks.includes(p.id);
  return <>
    <Card className="dokkai-session-bar"><div className="n2-actions dokkai-spread"><strong>Passage {index + 1} of {round.length} · {timed ? phase === "review" ? "Timed review" : "Timed practice" : "Study"}</strong>
      {timed && phase === "answer" && <span className={remaining <= 30 ? "dokkai-countdown is-low" : "dokkai-countdown"} role="timer" aria-label="Time remaining">{Math.floor(remaining / 60)}:{String(remaining % 60).padStart(2, "0")}</span>}</div>
      <ProgressBar value={timed && phase === "answer" ? answered : index} max={timed && phase === "answer" ? total : round.length} label={timed && phase === "answer" ? "Questions answered in this round" : "Passages reviewed in this round"} />
      {phase === "review" && <p role="status">{expired ? "Time is up. " : "Round submitted. "}{score}/{total} correct. Review every passage below.</p>}
    </Card>
    <Card className="dokkai-reader"><div className="n2-actions dokkai-spread"><Badge>{p.skill} · {p.topic}</Badge>
      <Button aria-pressed={bookmark} onClick={() => state.bookmark(p.id)}>{bookmark ? "Bookmarked" : "Bookmark passage"}</Button></div>
      <h2 ref={headingRef} tabIndex={-1} lang="ja">{p.title}</h2>
      {enabled && <div className="n2-actions"><label className="dokkai-check"><input type="checkbox" checked={ruby} onChange={(e) => { assist(); setRuby(e.target.checked); }} /> Show kana above annotated words</label>
        <span className="n2-meta">Click underlined words for meaning and kana.</span></div>}
      <div className={p.kind === "ab" ? "dokkai-texts dokkai-paired" : "dokkai-texts"}>{p.texts.map((text, i) => <section key={i} className={p.kind === "information" ? "dokkai-notice" : "dokkai-text-block"}>
        {text.label && <h3>Text {text.label}</h3>}
        <div className="dokkai-passage" lang="ja"><ReadingText text={text.text} vocabulary={vocabulary} enabled={enabled} ruby={ruby && enabled}
          evidence={review ? p.questions.flatMap((q) => q.evidence) : []} onWord={openWord} /></div>
      </section>)}</div>
      {review && <p className="n2-meta">Highlighted text supports the answers below.</p>}
    </Card>
    <Card><form onSubmit={(e) => { e.preventDefault(); if (!timed) check(); else next(); }}>
      {p.questions.map((q, qi) => <fieldset key={q.id} className="n2-choice-group">
        <legend><strong>Question {qi + 1}. </strong><span lang="ja"><ReadingText text={q.prompt} vocabulary={vocabulary} enabled={enabled} onWord={openWord} /></span></legend>
        <div className="dokkai-choices">{q.choices.map((choice, ci) => <label key={ci} className={`n2-choice ${answers[q.id] === ci ? "is-selected" : ""} ${review && q.answer === ci ? "dokkai-correct" : ""}`}>
          <input type="radio" name={q.id} value={ci} checked={answers[q.id] === ci} disabled={review} onChange={() => {
            const value = { ...answerRef.current, [q.id]: ci }; answerRef.current = value; setAnswers(value);
          }} /><strong>{ci + 1}.</strong><span lang="ja"><ReadingText text={choice.text} vocabulary={vocabulary} enabled={enabled} onWord={openWord} /></span>
        </label>)}</div>
        {review && <div className="n2-feedback"><p role="status"><Badge tone={!revealed[p.id] && answers[q.id] === q.answer ? "good" : "warn"}>
          {revealed[p.id] ? "Answer revealed · revisit later" : answers[q.id] === q.answer ? "Correct" : answers[q.id] === undefined ? "Unanswered · revisit later" : "Incorrect · revisit later"}</Badge></p>
          <p>Your choice: {answers[q.id] === undefined ? "None" : answers[q.id] + 1}. <strong>Correct answer: {q.answer + 1}</strong></p>
          <p>{q.explanation}</p><p><strong>Evidence:</strong></p>{q.evidence.map((quote, i) => <blockquote key={i} lang="ja">{quote}</blockquote>)}
          <details><summary>Why each option is right or wrong</summary><ol>{q.choices.map((choice, i) => <li key={i}><strong lang="ja">{plainReading(choice.text)}</strong><p>{choice.explanation}</p></li>)}</ol></details>
        </div>}
      </fieldset>)}
      {!review && !timed && <div className="n2-actions"><Button type="submit" variant="primary" disabled={p.questions.some((q) => answers[q.id] === undefined)}>Check answers</Button>
        <Button variant="ghost" onClick={() => { assist(); setHint((value) => !value); }} aria-expanded={hint}>{hint ? "Hide tip" : "Show solving tip"}</Button>
        <Button variant="ghost" onClick={() => check(true)}>Reveal answers · revisit later</Button></div>}
      {hint && <p className="n2-hint">{READING_TIPS[p.skill]}</p>}
      {(review || timed) && <div className="n2-actions">
        {index > 0 && timed && <Button onClick={() => { popup.close(); setHint(false); setIndex((n) => n - 1); }}>Previous passage</Button>}
        <Button ref={nextRef} variant="primary" onClick={next}>{index + 1 < round.length ? "Next passage →" : timed && phase === "answer" ? "Finish and review answers" : "Finish round"}</Button>
        {timed && phase === "answer" && index + 1 < round.length && <Button onClick={() => finalizeRef.current(false)}>Submit round now · {answered}/{total} answered</Button>}
      </div>}
    </form></Card>
    {review && <Card><h2>Learn from this passage</h2><p><strong>{p.skill}:</strong> {READING_TIPS[p.skill]}</p>
      <details key={p.id}><summary>English translation</summary>{p.texts.map((text, i) => <div key={i}>{text.label && <h3>Text {text.label}</h3>}<p>{text.translation}</p></div>)}</details>
      {!timed && <p className="n2-meta">Recorded as {recordedModes[p.id] === "assisted" ? "study with help" : "independent study"}.</p>}
    </Card>}
    <ReadingWordDialog word={popup.word} source={p.id} state={state} onClose={popup.close} />
  </>;
}
