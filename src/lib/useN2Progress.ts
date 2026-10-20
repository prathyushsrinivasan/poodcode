import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { N2_QUESTIONS } from "../data/jlptN2";
import { N2_PROGRESS_KEY, parseN2Progress, recordN2Answer, type N2Progress } from "./jlptN2";

// Serialize snapshots so rapid answers cannot let an older write win. Await
// this queue on remount too, before reading the persisted progress again.
let pendingSave: Promise<void> = Promise.resolve();

export function useN2Progress(key = N2_PROGRESS_KEY, questions: { id: string }[] = N2_QUESTIONS) {
  const [progress, setProgress] = useState<N2Progress | null>(null);
  const latest = useRef<N2Progress>({});
  const [loadError, setLoadError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const mounted = useRef(false);
  useEffect(() => {
    let canceled = false;
    mounted.current = true;
    setLoadError("");
    pendingSave.catch(() => undefined)
      .then(() => api.getSettings())
      .then((settings) => {
        if (canceled) return;
        latest.current = parseN2Progress(settings[key], questions);
        setProgress(latest.current);
      })
      .catch((e) => { if (!canceled) setLoadError(String(e)); });
    return () => { canceled = true; mounted.current = false; };
  }, [attempt, key, questions]);

  function persist(next: N2Progress) {
    pendingSave = pendingSave.catch(() => undefined)
      .then(() => api.setSetting(key, JSON.stringify(next)))
      .then(() => { if (mounted.current) setSaveError(""); })
      .catch((e) => {
        if (mounted.current) setSaveError(String(e));
        // Retain the rejected queue for the next mount/retry to recover from.
        throw e;
      });
    // A failed save is shown inline; this handler prevents an unhandled rejection.
    void pendingSave.catch(() => undefined);
  }
  function record(id: string, correct: boolean) {
    const next = recordN2Answer(latest.current, id, correct);
    latest.current = next;
    setProgress(next);
    persist(next);
  }
  return { progress, record, loadError, saveError,
    retryLoad: () => setAttempt((n) => n + 1), retrySave: () => persist(latest.current) };
}
