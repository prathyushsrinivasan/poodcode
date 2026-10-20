import { useEffect, useRef, useState } from "react";
import type { ReadingWord } from "../data/dokkai/types";
import { COMMON_READING_WORDS } from "../data/dokkai/vocabulary";
import { readingSegments, readingWords, wordKey } from "../lib/dokkaiText";
import type { ReadingState } from "../lib/useReadingProgress";
import { Button } from "./ui";

export function ReadingText({ text, vocabulary = [], ruby = false, enabled = true, evidence = [], onWord }: {
  text: string; vocabulary?: ReadingWord[]; ruby?: boolean; enabled?: boolean; evidence?: string[]; onWord: (word: ReadingWord) => void;
}) {
  const segments = readingSegments(text, [...vocabulary, ...COMMON_READING_WORDS], evidence);
  return <>{segments.map((segment, i) => <span key={i} className={segment.evidence ? "dokkai-evidence" : undefined}>
    {enabled && segment.word ? <button type="button" className="dokkai-word" aria-label={`Look up ${segment.word.text}`}
      onClick={() => onWord(segment.word!)}>{ruby ? <ruby>{segment.text}<rt>{segment.word.reading}</rt></ruby> : segment.text}</button>
      : segment.text}
  </span>)}</>;
}

export function useWordPopup() {
  const [word, setWord] = useState<ReadingWord | null>(null);
  const opener = useRef<HTMLElement | null>(null);
  return { word, open: (value: ReadingWord) => { opener.current = document.activeElement as HTMLElement; setWord(value); },
    close: () => { setWord(null); opener.current?.focus(); } };
}
export function ReadingWordDialog({ word, source, state, onClose }: { word: ReadingWord | null; source: string; state: ReadingState; onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    if (word && !dialog.current?.open) dialog.current?.showModal();
    else if (!word) dialog.current?.close();
  }, [word]);
  const saved = word ? !!state.progress.words[wordKey(word)] : false;
  return <dialog ref={dialog} className="dokkai-dialog" aria-labelledby="reading-word-title" onCancel={(e) => { e.preventDefault(); onClose(); }}>
    {word && <>
      <div className="n2-actions dokkai-spread"><h2 id="reading-word-title" lang="ja">{word.text}</h2><Button onClick={onClose} aria-label="Close vocabulary">Close</Button></div>
      <p className="dokkai-kana" lang="ja">{word.reading}</p><p>{word.meaning}</p>
      {word.lemma && word.lemma !== word.text && <p>Dictionary form: <span lang="ja">{word.lemma}</span></p>}
      <Button variant="primary" disabled={saved} onClick={() => state.saveWord(word, source)}>{saved ? "Saved to vocabulary review" : "Save for vocabulary review"}</Button>
      <p className="n2-meta" role="status">{saved ? "This word is available in Reading vocabulary, with its source passage." : "Meaning and reading apply to this occurrence."}</p>
    </>}
  </dialog>;
}
export function passageVocabulary(texts: { text: string }[]): ReadingWord[] { return texts.flatMap((t) => readingWords(t.text)); }
