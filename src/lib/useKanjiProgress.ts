import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api";
import { KANJI_PROGRESS_KEY } from "../data/kanjiWords";
import { emptyKanjiProgress, parseKanjiProgress, recordKanjiResult, type KanjiProgress, type KanjiSkill } from "./kanjiWords";
import { clearJlptJournal, readJlptJournal, writeJlptJournal } from "./jlptPersistence";

let pending: Promise<void> = Promise.resolve();
export const flushKanjiProgress = () => pending;
export function useKanjiProgress() {
  const [progress, setProgress] = useState<KanjiProgress | null>(null);
  const latest = useRef(emptyKanjiProgress());
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
      latest.current = parseKanjiProgress(readJlptJournal(KANJI_PROGRESS_KEY, settings[KANJI_PROGRESS_KEY]));
      setProgress(latest.current);
    }).catch((error) => { if (!canceled) setLoadError(String(error)); });
    return () => { canceled = true; mounted.current = false; };
  }, [attempt]);
  const save = useCallback((next: KanjiProgress) => {
    const raw = JSON.stringify(next);
    try { writeJlptJournal(KANJI_PROGRESS_KEY, raw); } catch { setSaveError("Recovery storage is unavailable. Keep this page open until saving succeeds."); }
    pending = pending.catch(() => undefined).then(() => api.setSetting(KANJI_PROGRESS_KEY, JSON.stringify(next)))
      .then(() => { clearJlptJournal(KANJI_PROGRESS_KEY, raw); if (mounted.current) setSaveError(""); })
      .catch((error) => { if (mounted.current) setSaveError(String(error)); throw error; });
    void pending.catch(() => undefined);
  }, []);
  const record = useCallback((id: string, skill: KanjiSkill, correct: boolean) => {
    const next = recordKanjiResult(latest.current, id, skill, correct);
    if (next === latest.current) return;
    latest.current = next;
    setProgress(next);
    save(next);
  }, [save]);
  return { progress, record, loadError, saveError, retryLoad: () => setAttempt((n) => n + 1), retrySave: () => save(latest.current) };
}
