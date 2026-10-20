import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { ReadingWord } from "../data/dokkai/types";
import { emptyReadingProgress, parseReadingProgress, READING_PROGRESS_KEY, recordReadingAnswers,
  reviewReadingWord, type ReadingMode, type ReadingProgress } from "./dokkai";
import { wordKey } from "./dokkaiText";

let pending: Promise<void> = Promise.resolve();
export function useReadingProgress() {
  const [progress, setProgress] = useState<ReadingProgress | null>(null);
  const latest = useRef(emptyReadingProgress());
  const mounted = useRef(false);
  const [loadError, setLoadError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let canceled = false;
    mounted.current = true;
    setLoadError("");
    pending.catch(() => undefined).then(() => api.getSettings()).then((settings) => {
      if (canceled) return;
      latest.current = parseReadingProgress(settings[READING_PROGRESS_KEY]);
      setProgress(latest.current);
    }).catch((error) => { if (!canceled) setLoadError(String(error)); });
    return () => { canceled = true; mounted.current = false; };
  }, [attempt]);
  function save(next: ReadingProgress) {
    pending = pending.catch(() => undefined).then(() => api.setSetting(READING_PROGRESS_KEY, JSON.stringify(next)))
      .then(() => { if (mounted.current) setSaveError(""); })
      .catch((error) => { if (mounted.current) setSaveError(String(error)); throw error; });
    void pending.catch(() => undefined);
  }
  function change(update: (p: ReadingProgress) => ReadingProgress) {
    if (!progress) return;
    latest.current = update(latest.current);
    setProgress(latest.current);
    save(latest.current);
  }
  return { progress, loadError, saveError, retryLoad: () => setAttempt((n) => n + 1), retrySave: () => save(latest.current),
    record: (answers: { id: string; correct: boolean; mode: ReadingMode }[]) => change((p) => recordReadingAnswers(p, answers)),
    bookmark: (id: string) => change((p) => ({ ...p, bookmarks: p.bookmarks.includes(id) ? p.bookmarks.filter((x) => x !== id) : [...p.bookmarks, id] })),
    saveWord: (word: ReadingWord, source: string) => change((p) => ({ ...p, words: { ...p.words,
      [wordKey(word)]: p.words[wordKey(word)] ?? { ...word, source, due: Date.now(), interval: 0, reviews: 0 } } })),
    removeWord: (key: string) => change((p) => ({ ...p, words: Object.fromEntries(Object.entries(p.words).filter(([id]) => id !== key)) })),
    gradeWord: (key: string, remembered: boolean) => change((p) => {
      const word = p.words[key];
      return word ? { ...p, words: { ...p.words, [key]: reviewReadingWord(word, remembered) } } : p;
    }),
  };
}
export type ReadingState = ReturnType<typeof useReadingProgress> & { progress: ReadingProgress };
