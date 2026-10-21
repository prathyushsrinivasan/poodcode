import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import type { ReadingWord } from "../data/dokkai/types";
import { COMMON_READING_WORDS } from "../data/dokkai/vocabulary";
import { readingSegments, readingWords, wordKey } from "../lib/dokkaiText";
import type { ReadingState } from "../lib/useReadingProgress";
import { Button } from "./ui";

export function ReadingText({ text, vocabulary = [], ruby = false, enabled = true, evidence = [], onWord }: {
  text: string; vocabulary?: ReadingWord[]; ruby?: boolean; enabled?: boolean; evidence?: string[]; onWord: (word: ReadingWord, anchor: HTMLElement) => void;
}) {
  const segments = readingSegments(text, [...vocabulary, ...COMMON_READING_WORDS], evidence);
  return <>{segments.map((segment, i) => <span key={i} className={segment.evidence ? "dokkai-evidence" : undefined}>
    {enabled && segment.word ? <button type="button" className="dokkai-word" aria-label={`Look up ${segment.word.text}`}
      aria-haspopup="dialog" aria-controls="reading-word-popup"
      onPointerEnter={(e) => { if (e.pointerType !== "touch") onWord(segment.word!, e.currentTarget); }}
      onFocus={(e) => onWord(segment.word!, e.currentTarget)}
      onKeyDown={(e) => { if (e.key === "ArrowDown") { e.preventDefault(); document.querySelector<HTMLButtonElement>("#reading-word-popup button")?.focus(); } }}
      onClick={(e) => { e.preventDefault(); e.stopPropagation(); onWord(segment.word!, e.currentTarget); }}>{ruby ? <ruby>{segment.text}<rt>{segment.word.reading}</rt></ruby> : segment.text}</button>
      : segment.text}
  </span>)}</>;
}

export function useWordPopup() {
  const [selection, setSelection] = useState<{ word: ReadingWord; anchor: HTMLElement } | null>(null);
  useEffect(() => {
    if (!selection) return;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const inside = (target: EventTarget | null) => target instanceof Node &&
      (selection.anchor.contains(target) || document.getElementById("reading-word-popup")?.contains(target));
    const move = (event: PointerEvent) => {
      clearTimeout(timer);
      if (!inside(event.target)) timer = setTimeout(() => setSelection(null), 180);
    };
    const leave = () => { timer = setTimeout(() => setSelection(null), 180); };
    const dismiss = (event: Event) => { if (!inside(event.target)) setSelection(null); };
    const key = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.preventDefault();
      if (document.getElementById("reading-word-popup")?.contains(document.activeElement)) selection.anchor.focus();
      setSelection(null);
    };
    const close = (event: Event) => {
      if (!(event.target instanceof Node && document.getElementById("reading-word-popup")?.contains(event.target))) setSelection(null);
    };
    document.addEventListener("pointermove", move);
    document.documentElement.addEventListener("pointerleave", leave);
    document.addEventListener("pointerdown", dismiss);
    document.addEventListener("focusin", dismiss);
    document.addEventListener("keydown", key);
    window.addEventListener("resize", close);
    window.addEventListener("scroll", close, true);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("pointermove", move);
      document.documentElement.removeEventListener("pointerleave", leave);
      document.removeEventListener("pointerdown", dismiss);
      document.removeEventListener("focusin", dismiss);
      document.removeEventListener("keydown", key);
      window.removeEventListener("resize", close);
      window.removeEventListener("scroll", close, true);
    };
  }, [selection]);
  return { word: selection?.word ?? null, anchor: selection?.anchor ?? null,
    open: (word: ReadingWord, anchor: HTMLElement) => setSelection((before) => before?.anchor === anchor ? before : { word, anchor }),
    close: () => setSelection(null) };
}
export function ReadingWordPopup({ word, anchor, source, state, onClose }: { word: ReadingWord | null; anchor: HTMLElement | null; source: string; state: ReadingState; onClose: () => void }) {
  const dialog = useRef<HTMLDivElement>(null);
  const saved = word ? !!state.progress.words[wordKey(word)] : false;
  useLayoutEffect(() => {
    if (!word || !anchor || !dialog.current) return;
    const rect = anchor.getBoundingClientRect();
    const popup = dialog.current;
    const left = Math.max(8, Math.min(rect.left, window.innerWidth - popup.offsetWidth - 8));
    const top = rect.bottom + popup.offsetHeight + 8 <= window.innerHeight
      ? rect.bottom + 8 : Math.max(8, rect.top - popup.offsetHeight - 8);
    popup.style.left = `${left}px`;
    popup.style.top = `${top}px`;
  }, [word, anchor, saved]);
  if (!word) return null;
  return createPortal(<div ref={dialog} id="reading-word-popup" role="dialog" aria-modal="false" className="dokkai-dialog" aria-labelledby="reading-word-title">
      <div className="n2-actions dokkai-spread"><h2 id="reading-word-title" lang="ja">{word.text}</h2><Button onClick={() => { anchor?.focus(); onClose(); }} aria-label="Close vocabulary">Close</Button></div>
      <p className="dokkai-kana" lang="ja">{word.reading}</p><p>{word.meaning}</p>
      {word.lemma && word.lemma !== word.text && <p>Dictionary form: <span lang="ja">{word.lemma}</span></p>}
      <Button variant="primary" disabled={saved} onClick={() => state.saveWord(word, source)}>{saved ? "Saved to vocabulary review" : "Save for vocabulary review"}</Button>
      <p className="n2-meta" role="status">{saved ? "This word is available in Reading vocabulary, with its source passage." : "Meaning and reading apply to this occurrence."}</p>
  </div>, document.body);
}
export function passageVocabulary(texts: { text: string }[]): ReadingWord[] { return texts.flatMap((t) => readingWords(t.text)); }
