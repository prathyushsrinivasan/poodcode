import { useCallback, useState } from "react";

// Collapse state for Learn-tab sections. This is pure UI convenience, so it
// lives in localStorage next to the chapter-done checkmarks and exercise
// drafts. Keys are namespaced by the caller (e.g. "cat:Arrays", "sec:drills").
const KEY = "poodcode:collapsed";

function readCollapsed(): Set<string> {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || "[]");
    return new Set(Array.isArray(raw) ? raw : []);
  } catch {
    return new Set();
  }
}

function writeCollapsed(s: Set<string>) {
  localStorage.setItem(KEY, JSON.stringify([...s]));
}

/** Remembered open/closed state for a set of sections sharing a namespace.
 *
 * The persisted set holds the ids that differ from `defaultOpen`, so a
 * default-open namespace stores its collapsed sections and a default-closed one
 * stores its expanded sections. Default-closed matters where a section body is
 * expensive — a course lesson mounts a Monaco editor per exercise, and a week
 * has dozens, so opening them all at once would stall the page. */
export function useCollapse(namespace: string, defaultOpen = true) {
  const [overrides, setOverrides] = useState<Set<string>>(readCollapsed);

  const id = useCallback((k: string) => `${namespace}:${k}`, [namespace]);

  const isOpen = useCallback(
    (k: string) => (overrides.has(id(k)) ? !defaultOpen : defaultOpen),
    [overrides, id, defaultOpen]
  );

  const toggle = useCallback(
    (k: string) => {
      setOverrides((prev) => {
        const next = new Set(prev);
        if (next.has(id(k))) next.delete(id(k));
        else next.add(id(k));
        writeCollapsed(next);
        return next;
      });
    },
    [id]
  );

  /** Collapse or expand every section in this namespace at once. */
  const setAll = useCallback(
    (keys: string[], open: boolean) => {
      setOverrides((prev) => {
        const next = new Set(prev);
        for (const k of keys) {
          if (open === defaultOpen) next.delete(id(k));
          else next.add(id(k));
        }
        writeCollapsed(next);
        return next;
      });
    },
    [id, defaultOpen]
  );

  return { isOpen, toggle, setAll };
}

/** A section with a clickable header that shows/hides its body.
 *
 * `meta` renders on the right of the header (counts, progress) and stays
 * visible when collapsed, so a folded section still tells you what's inside. */
export function Section({
  title,
  open,
  onToggle,
  meta,
  level = "h3",
  accent,
  children,
}: {
  title: React.ReactNode;
  open: boolean;
  onToggle: () => void;
  meta?: React.ReactNode;
  /** Visual weight of the header — "h3" for page sections, "h4" for nested. */
  level?: "h3" | "h4";
  /** Tint the header text (e.g. "var(--accent)" for the challenge section). */
  accent?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="collapsible">
      <div
        className="collapsible-head"
        role="button"
        tabIndex={0}
        aria-expanded={open}
        onClick={onToggle}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onToggle();
          }
        }}
      >
        <span className={`caret ${open ? "open" : ""}`} aria-hidden>
          ▸
        </span>
        {level === "h3" ? (
          <h3 style={{ margin: 0, color: accent }}>{title}</h3>
        ) : (
          <h4 style={{ margin: 0, color: accent }}>{title}</h4>
        )}
        <span className="spacer" />
        {meta}
      </div>
      {open && <div className="collapsible-body">{children}</div>}
    </div>
  );
}
