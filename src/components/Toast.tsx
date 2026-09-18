/**
 * Stacked, announced, dismissible toasts.
 *
 * The previous provider held exactly one message, replaced it on every call and
 * cleared it after 2.2 seconds, with no severity and no way to dismiss. So
 * "Submit error: <a stack trace>" and "Restore failed: …" — the two messages
 * that most need reading — vanished before they could be read, and a screen
 * reader never heard any of them because the container was a plain `div`.
 *
 * What changed:
 *   - several toasts stack instead of overwriting each other;
 *   - errors persist until dismissed, and carry a "copy details" action;
 *   - hovering pauses the countdown;
 *   - the region is `aria-live`, polite for information and assertive for
 *     errors, so they are announced;
 *   - reversible actions can attach an Undo.
 *
 * The old call style still works: `toast("Saved")` shows an info toast, so the
 * ~90 existing call sites did not all have to change at once.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

export type ToastTone = "info" | "success" | "warning" | "error";

export interface ToastOptions {
  tone?: ToastTone;
  /** Longer body under the message — a stack trace, a path, a reason. */
  detail?: string;
  /** A single action button, e.g. `{ label: "Undo", onClick: revert }`. */
  action?: { label: string; onClick: () => void };
  /** Milliseconds on screen. `0` pins it until dismissed; errors default to 0. */
  duration?: number;
}

interface ToastRow extends ToastOptions {
  id: number;
  message: string;
  tone: ToastTone;
  duration: number;
}

export interface ToastFn {
  (message: string, options?: ToastOptions): void;
  info: (message: string, options?: ToastOptions) => void;
  success: (message: string, options?: ToastOptions) => void;
  warning: (message: string, options?: ToastOptions) => void;
  error: (message: string, options?: ToastOptions) => void;
  dismiss: (id: number) => void;
}

const noop = Object.assign(() => {}, {
  info: () => {},
  success: () => {},
  warning: () => {},
  error: () => {},
  dismiss: () => {},
}) as ToastFn;

const ToastCtx = createContext<ToastFn>(noop);

/** How long each tone stays up. Errors stay until dismissed: they are the ones
 * worth reading, and they were exactly what the 2.2s timer used to eat. */
const DEFAULT_DURATION: Record<ToastTone, number> = {
  info: 4000,
  success: 3500,
  warning: 7000,
  error: 0,
};

const ICON: Record<ToastTone, string> = {
  info: "i",
  success: "✓",
  warning: "!",
  error: "✕",
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [rows, setRows] = useState<ToastRow[]>([]);
  const nextId = useRef(1);

  const dismiss = useCallback((id: number) => {
    setRows((list) => list.filter((r) => r.id !== id));
  }, []);

  const show = useMemo(() => {
    const push = (message: string, options: ToastOptions = {}) => {
      const tone = options.tone ?? "info";
      const row: ToastRow = {
        id: nextId.current++,
        message,
        tone,
        detail: options.detail,
        action: options.action,
        duration: options.duration ?? DEFAULT_DURATION[tone],
      };
      // Keep the stack short enough to read; the oldest falls off the top.
      setRows((list) => [...list, row].slice(-4));
    };

    const fn = ((message: string, options?: ToastOptions) => push(message, options)) as ToastFn;
    fn.info = (m, o) => push(m, { ...o, tone: "info" });
    fn.success = (m, o) => push(m, { ...o, tone: "success" });
    fn.warning = (m, o) => push(m, { ...o, tone: "warning" });
    fn.error = (m, o) => push(m, { ...o, tone: "error" });
    fn.dismiss = dismiss;
    return fn;
  }, [dismiss]);

  return (
    <ToastCtx.Provider value={show}>
      {children}
      {/* Two regions, because politeness is a property of the region, not the
          message: errors interrupt, everything else waits its turn. */}
      <div className="toast-stack" aria-live="polite" aria-atomic="false">
        {rows
          .filter((r) => r.tone !== "error")
          .map((r) => (
            <ToastView key={r.id} row={r} onDismiss={dismiss} />
          ))}
      </div>
      <div className="toast-stack toast-stack-errors" aria-live="assertive" aria-atomic="false">
        {rows
          .filter((r) => r.tone === "error")
          .map((r) => (
            <ToastView key={r.id} row={r} onDismiss={dismiss} />
          ))}
      </div>
    </ToastCtx.Provider>
  );
}

function ToastView({ row, onDismiss }: { row: ToastRow; onDismiss: (id: number) => void }) {
  const [paused, setPaused] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (row.duration <= 0 || paused) return;
    const t = setTimeout(() => onDismiss(row.id), row.duration);
    return () => clearTimeout(t);
  }, [row.duration, row.id, paused, onDismiss]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(`${row.message}\n\n${row.detail ?? ""}`.trim());
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard denied — the text is on screen and selectable anyway */
    }
  };

  return (
    <div
      className={`toast toast-${row.tone}`}
      role={row.tone === "error" ? "alert" : "status"}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <span className="toast-icon" aria-hidden>
        {ICON[row.tone]}
      </span>
      <div className="toast-content">
        <div className="toast-message">{row.message}</div>
        {row.detail && <div className="toast-detail">{row.detail}</div>}
        {(row.action || row.detail) && (
          <div className="toast-actions">
            {row.action && (
              <button
                className="ghost"
                onClick={() => {
                  row.action!.onClick();
                  onDismiss(row.id);
                }}
              >
                {row.action.label}
              </button>
            )}
            {row.detail && (
              <button className="ghost" onClick={copy}>
                {copied ? "Copied" : "Copy details"}
              </button>
            )}
          </div>
        )}
      </div>
      <button className="ghost toast-x" onClick={() => onDismiss(row.id)} aria-label="Dismiss">
        ✕
      </button>
    </div>
  );
}

export function useToast() {
  return useContext(ToastCtx);
}
