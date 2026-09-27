/**
 * What happens when a background call fails (UI_ROADMAP E2).
 *
 * The app had ~60 calls ending in `.catch(() => {})`. Some really were
 * best-effort — a nav badge, the palette's search index — but none of them
 * told anyone anything, so a settings write or a progress mark that never
 * landed looked exactly like one that did. Every such call now picks one of
 * three handlers, and the choice is visible at the call site:
 *
 *   `ignore(reason)`     — genuinely optional (decoration, a prefetch). Stays
 *                          quiet, but the reason is written down and the
 *                          failure is logged and kept for Settings → About.
 *   `loadFailed(what)`   — something the page shows is missing or stale. A
 *                          warning toast says what.
 *   `saveFailed(what)`   — a write did not land. A warning toast says what
 *                          was not saved.
 *
 * Handlers work outside React (lib code has no toast hook): they dispatch a
 * window event that the ToastProvider turns into a toast, collapsing repeats
 * of the same message so a periodic write that keeps failing is one toast,
 * not one a minute.
 */

export type FailureKind = "ignored" | "load" | "save";

export interface Failure {
  kind: FailureKind;
  /** What failed, in words: "your progress", "the study-time log". */
  what: string;
  detail: string;
  at: number;
}

export const FAILURE_EVENT = "poodcode:failure";

const MAX_KEPT = 50;
const kept: Failure[] = [];

function detailOf(e: unknown): string {
  if (e instanceof Error) return e.message;
  if (typeof e === "string") return e;
  try {
    return JSON.stringify(e);
  } catch {
    return String(e);
  }
}

function record(kind: FailureKind, what: string, e: unknown): Failure {
  const f: Failure = { kind, what, detail: detailOf(e), at: Date.now() };
  kept.unshift(f);
  if (kept.length > MAX_KEPT) kept.length = MAX_KEPT;
  return f;
}

/** Failures this session, newest first — Settings → About shows them. */
export function recentFailures(): readonly Failure[] {
  return kept;
}

/** Test hook. */
export function clearFailures(): void {
  kept.length = 0;
}

function announce(f: Failure) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<Failure>(FAILURE_EVENT, { detail: f }));
}

/**
 * A failure that does not matter to the learner. `reason` says why it is
 * allowed to be silent — it is documentation as much as an argument.
 */
export function ignore(reason: string) {
  return (e: unknown): undefined => {
    const f = record("ignored", reason, e);
    console.debug(`[ignored] ${reason}:`, f.detail);
    return undefined;
  };
}

/** A read whose result the page shows. The page keeps working without it; the toast says what is missing. */
export function loadFailed(what: string) {
  return (e: unknown): undefined => {
    const f = record("load", what, e);
    console.warn(`[load failed] ${what}:`, f.detail);
    announce(f);
    return undefined;
  };
}

/** A write that did not land. */
export function saveFailed(what: string) {
  return (e: unknown): undefined => {
    const f = record("save", what, e);
    console.warn(`[save failed] ${what}:`, f.detail);
    announce(f);
    return undefined;
  };
}

/** The toast wording for a failure, shared so tests and the provider agree. */
export function failureMessage(f: Failure): string {
  return f.kind === "save" ? `Couldn't save ${f.what}.` : `Couldn't load ${f.what}.`;
}
