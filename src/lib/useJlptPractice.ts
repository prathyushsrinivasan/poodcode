import { useCallback, useEffect, useRef, useState, type SetStateAction } from "react";
import { useLocation } from "react-router-dom";
import { useN2Study } from "./useN2Study";
import { validJlptSessionField } from "./jlptSessionRecovery";

/** Persist only user choices, not temporary UI state such as open panels. */
type PreferenceValue<T> = T extends boolean ? boolean : T extends number ? number : string;
export function useJlptPreference<T extends string | boolean | number>(page: string, key: string, fallback: T): [PreferenceValue<T>, (value: PreferenceValue<T>) => void] {
  const state = useN2Study();
  const value = state.data?.workspace.pagePreferences[page]?.[key];
  return [(typeof value === typeof fallback ? value : fallback) as PreferenceValue<T>, (next) => state.update((p) => ({ ...p, workspace: { ...p.workspace, pagePreferences: { ...p.workspace.pagePreferences, [page]: { ...p.workspace.pagePreferences[page], [key]: next } } } }))];
}
const PREFIX = "jlpt-session:";
function scope() { return `${PREFIX}${window.location.hash.replace(/^#/, "")}`; }
export function clearJlptSession() {
  const prefix = scope();
  for (const key of Object.keys(localStorage)) if (key.startsWith(`${prefix}:`)) localStorage.removeItem(key);
}
/** Synchronous draft journals survive navigation and closure between database
 * writes. Each field is scoped to a native course route; timed deadlines remain
 * absolute timestamps. Course results still use their original progress key. */
export function useJlptSessionState<T>(field: string, initial: T | (() => T)): [T, (next: SetStateAction<T>) => void] {
  const location = useLocation();
  const key = `${PREFIX}${location.pathname}${location.search}:${field}`;
  const recoveryError = useRef("");
  const [value, setValue] = useState<T>(() => {
    const fallback = typeof initial === "function" ? (initial as () => T)() : initial;
    try {
      const raw = localStorage.getItem(key);
      if (raw !== null) {
        const parsed: unknown = JSON.parse(raw);
        if (validJlptSessionField(key, parsed)) return parsed as T;
        recoveryError.current = "A saved draft could not be recovered safely. Its original data has been kept; this field starts fresh.";
        return fallback;
      }
      localStorage.setItem(key, JSON.stringify(fallback));
    } catch { recoveryError.current = "Draft recovery storage could not be read or written. Keep this page open until your answers are submitted."; }
    return fallback;
  });
  const latest = useRef(value);
  useEffect(() => { if (recoveryError.current) window.dispatchEvent(new CustomEvent("jlpt-recovery-error", { detail: recoveryError.current })); }, []);
  const update = useCallback((next: SetStateAction<T>) => {
    const result = typeof next === "function" ? (next as (old: T) => T)(latest.current) : next;
    if (Object.is(result, latest.current)) return;
    latest.current = result;
    try { localStorage.setItem(key, JSON.stringify(result)); }
    catch { window.dispatchEvent(new Event("jlpt-recovery-error")); }
    setValue(result);
  }, [key]);
  return [value, update];
}
