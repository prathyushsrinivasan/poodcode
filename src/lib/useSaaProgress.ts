import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api";
import { emptySaaProgress, parseSaaProgress, SAA_PROGRESS_KEY, type SaaProgress } from "./awsSaa";

// Preserve write order, and wait for outstanding writes before a route remount reads.
let pending: Promise<void> = Promise.resolve();
export function useSaaProgress() {
  const [progress, setProgress] = useState<SaaProgress | null>(null);
  const latest = useRef(emptySaaProgress());
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
      latest.current = parseSaaProgress(settings[SAA_PROGRESS_KEY]);
      setProgress(latest.current);
    }).catch((error) => { if (!canceled) setLoadError(String(error)); });
    return () => { canceled = true; mounted.current = false; };
  }, [attempt]);
  const save = useCallback((next: SaaProgress) => {
    pending = pending.catch(() => undefined).then(() => api.setSetting(SAA_PROGRESS_KEY, JSON.stringify(next)))
      .then(() => { if (mounted.current) setSaveError(""); })
      .catch((error) => { if (mounted.current) setSaveError(String(error)); throw error; });
    void pending.catch(() => undefined);
  }, []);
  const update = useCallback((change: (value: SaaProgress) => SaaProgress) => {
    const next = change(latest.current);
    if (next === latest.current) return;
    latest.current = next;
    setProgress(next);
    save(next);
  }, [save]);
  return { progress, update, loadError, saveError, retryLoad: () => setAttempt((n) => n + 1), retrySave: () => save(latest.current) };
}
