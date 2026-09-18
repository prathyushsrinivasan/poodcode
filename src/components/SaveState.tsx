/**
 * "Saved · just now", and what to say when it does not save.
 *
 * Solve debounces draft writes to SQLite and Settings writes a preference on
 * every keystroke — both entirely silently. So the two questions an editor
 * raises, *did that save?* and *did that fail?*, had no answer anywhere on
 * screen, and a failed write looked exactly like a successful one.
 */

import { useEffect, useState } from "react";

export type SaveStatus = "idle" | "saving" | "saved" | "error";

/** Tracks a save and how long ago it landed. */
export function useSaveState() {
  const [status, setStatus] = useState<SaveStatus>("idle");
  const [at, setAt] = useState<number | null>(null);
  const [error, setError] = useState("");

  /** Wrap the write: marks saving, then saved or error. */
  const track = async (write: () => Promise<unknown>) => {
    setStatus("saving");
    try {
      await write();
      setAt(Date.now());
      setStatus("saved");
      setError("");
    } catch (e) {
      setError(String(e));
      setStatus("error");
    }
  };

  return { status, at, error, track };
}

/** How long ago, in words. Re-renders itself so "just now" becomes "2m ago". */
function useAgo(at: number | null) {
  const [, tick] = useState(0);
  useEffect(() => {
    if (at === null) return;
    const t = setInterval(() => tick((n) => n + 1), 20_000);
    return () => clearInterval(t);
  }, [at]);

  if (at === null) return "";
  const seconds = Math.floor((Date.now() - at) / 1000);
  if (seconds < 45) return "just now";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  return `${Math.round(minutes / 60)}h ago`;
}

export function SaveIndicator({
  status,
  at,
  error,
  onRetry,
}: {
  status: SaveStatus;
  at: number | null;
  error?: string;
  onRetry?: () => void;
}) {
  const ago = useAgo(at);

  if (status === "idle") return null;

  if (status === "error") {
    return (
      <span className="save-state error" role="status">
        <span aria-hidden>⚠</span> Not saved
        {error && <span className="faint save-state-detail">{error}</span>}
        {onRetry && (
          <button className="ghost link-button" onClick={onRetry}>
            Retry
          </button>
        )}
      </span>
    );
  }

  return (
    <span className="save-state" role="status">
      {status === "saving" ? (
        <>
          <span className="save-dot" aria-hidden /> Saving…
        </>
      ) : (
        <>
          <span aria-hidden>✓</span> Saved{ago && ` · ${ago}`}
        </>
      )}
    </span>
  );
}
