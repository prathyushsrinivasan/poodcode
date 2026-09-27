import { useCallback, useId, useState } from "react";
import { Icon } from "./ui/Icon";
import { Deeper, H } from "./ui/Heading";

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

  /** Force one section open regardless of the remembered state. Used when a URL
   * hash names a section: arriving at `#pitfalls` and finding it collapsed
   * because you closed it last week is the link failing to work. */
  const open = useCallback(
    (k: string) => {
      setOverrides((prev) => {
        // The persisted set holds *deviations* from the default, so "open" means
        // removing the id when the default is open and adding it when it is not.
        const wanted = defaultOpen ? false : true;
        if (prev.has(id(k)) === wanted) return prev;
        const next = new Set(prev);
        if (wanted) next.add(id(k));
        else next.delete(id(k));
        writeCollapsed(next);
        return next;
      });
    },
    [id, defaultOpen]
  );

  return { isOpen, toggle, setAll, open };
}

/** Leading emoji or symbols in a title, which the outline does not want. */
function plainTitle(title: React.ReactNode): string | undefined {
  if (typeof title !== "string") return undefined;
  return title.replace(/^[^\p{L}\p{N}]+/u, "").trim() || title;
}

/** A section with a disclosure header that shows/hides its body.
 *
 * `meta` renders on the right of the header (counts, progress) and stays
 * visible when collapsed, so a folded section still tells you what's inside.
 *
 * The header is a real `<button aria-expanded>` inside the heading — the
 * disclosure pattern — rather than a `div role="button"` wrapping the heading,
 * which hid the heading from anyone navigating by headings (UI_ROADMAP D9).
 * The section also names itself for the page outline (G4): `outline` if
 * given, else a string title without its leading emoji. */
export function Section({
  title,
  open,
  onToggle,
  meta,
  level = "h3",
  accent,
  id,
  outline,
  children,
}: {
  title: React.ReactNode;
  open: boolean;
  onToggle: () => void;
  meta?: React.ReactNode;
  /** Visual weight of the header — "h3" for page sections, "h4" for nested.
   * The heading *tag* comes from the heading-level context, not from this. */
  level?: "h3" | "h4";
  /** Tint the header with the accent (the challenge section). */
  accent?: string;
  /**
   * DOM id, so the section can be linked to (`#pitfalls`) and scrolled to.
   * The pitfalls table is the thing you want to reach mid-debug, from outside
   * the app, in one click — which needs an anchor to aim at.
   */
  id?: string;
  /** Its name in the page outline; `false` leaves it out. */
  outline?: string | false;
  children: React.ReactNode;
}) {
  const bodyId = useId();
  const outlineText = outline === false ? undefined : outline ?? plainTitle(title);
  return (
    <section className="collapsible" id={id} data-outline={outlineText}>
      <div className="collapsible-row">
        <H className={`collapsible-heading ${level === "h4" ? "sub" : ""} ${accent ? "accent" : ""}`}>
          <button
            type="button"
            className="collapsible-head"
            aria-expanded={open}
            aria-controls={bodyId}
            onClick={onToggle}
          >
            <Icon name="chevronRight" size={14} className={`caret ${open ? "open" : ""}`} />
            <span className="collapsible-title">{title}</span>
          </button>
        </H>
        {meta && <div className="collapsible-meta">{meta}</div>}
      </div>
      {open && (
        <div className="collapsible-body" id={bodyId}>
          <Deeper>{children}</Deeper>
        </div>
      )}
    </section>
  );
}
