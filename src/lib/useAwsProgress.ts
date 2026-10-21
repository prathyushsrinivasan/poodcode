import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { AWS_PROGRESS_KEY, emptyAwsProgress, parseAwsProgress, type AwsProgress } from "./awsMla";

// Serialize snapshots and wait before remount reads, matching other local courses.
let pending: Promise<void> = Promise.resolve();
export function useAwsProgress() {
  const [progress, setProgress] = useState<AwsProgress | null>(null);
  const latest = useRef(emptyAwsProgress());
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
      latest.current = parseAwsProgress(settings[AWS_PROGRESS_KEY]);
      setProgress(latest.current);
    }).catch((error) => { if (!canceled) setLoadError(String(error)); });
    return () => { canceled = true; mounted.current = false; };
  }, [attempt]);
  function save(next: AwsProgress) {
    pending = pending.catch(() => undefined).then(() => api.setSetting(AWS_PROGRESS_KEY, JSON.stringify(next)))
      .then(() => { if (mounted.current) setSaveError(""); })
      .catch((error) => { if (mounted.current) setSaveError(String(error)); throw error; });
    void pending.catch(() => undefined);
  }
  function update(change: (value: AwsProgress) => AwsProgress) {
    if (!progress) return;
    latest.current = change(latest.current);
    setProgress(latest.current);
    save(latest.current);
  }
  return { progress, update, loadError, saveError, retryLoad: () => setAttempt((n) => n + 1), retrySave: () => save(latest.current) };
}
