/**
 * Wayfinding for long lessons (UI_ROADMAP G4).
 *
 * Lessons are long Markdown with exercises after them, and a page gave no
 * sense of where you were in one: no table of contents, no progress, and the
 * "scroll to the bottom and it marks itself done" rule was invisible until it
 * fired. Four pages (Learn, the courses, the Backend Lab, Projects) each had
 * their own copy of the bottom sentinel.
 *
 *   `ReaderLayout`   the page body beside a sticky "On this page" rail; below
 *                    a width it folds into a disclosure above the content.
 *   `PageOutline`    built from the DOM — every `[data-outline]` section and
 *                    every `h2` in a lesson body — so it follows whatever the
 *                    page rendered, and highlights the section in view.
 *   `ReadingBar`     a thin progress bar pinned to the top of the page.
 *   `useSeenBottom`  the shared sentinel: true once the end has been reached.
 *   `ReadStatus`     the completion rule, spelled out as a checklist, so it is
 *                    visible *before* it fires.
 */

import { useCallback, useEffect, useRef, useState, type ReactNode, type RefObject } from "react";
import { Icon } from "../ui/Icon";

/** The element the app scrolls in (the window never scrolls; `.main` does). */
function scroller(): HTMLElement | null {
  return document.getElementById("main");
}

export function slugify(text: string): string {
  return (
    text
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[^\p{L}\p{N}]+/gu, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 60) || "section"
  );
}

// ---- Reading progress ---------------------------------------------------------

/**
 * How far through `ref` the reader has scrolled, 0..1. 0 when its top is at the
 * top of the viewport, 1 when its bottom has come into view.
 */
export function useReadingProgress(ref: RefObject<HTMLElement>): number {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const main = scroller();
    const el = ref.current;
    if (!main || !el) return;
    let frame = 0;
    const measure = () => {
      frame = 0;
      const box = el.getBoundingClientRect();
      const view = main.getBoundingClientRect();
      const travel = box.height - view.height;
      const p = travel <= 0 ? 1 : (view.top - box.top) / travel;
      setProgress(Math.max(0, Math.min(1, p)));
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(measure);
    };
    measure();
    main.addEventListener("scroll", onScroll, { passive: true });
    const ro = new ResizeObserver(onScroll);
    ro.observe(el);
    return () => {
      main.removeEventListener("scroll", onScroll);
      ro.disconnect();
      if (frame) cancelAnimationFrame(frame);
    };
  }, [ref]);
  return progress;
}

export function ReadingBar({ progress, done }: { progress: number; done?: boolean }) {
  return (
    <div
      className={`reading-bar ${done ? "done" : ""}`}
      role="progressbar"
      aria-label="Reading progress"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(progress * 100)}
    >
      {/* The width is the measured scroll position — genuinely data. */}
      <span style={{ width: `${progress * 100}%` }} />
    </div>
  );
}

/**
 * The shared bottom sentinel: returns a ref for an element at the end of the
 * page and whether it has been scrolled into view. `resetKey` starts over
 * (a new chapter on the same component).
 */
export function useSeenBottom(resetKey: unknown): [RefObject<HTMLDivElement>, boolean] {
  const ref = useRef<HTMLDivElement>(null);
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    setSeen(false);
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) setSeen(true);
      },
      { threshold: 0.01 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [resetKey]);
  return [ref, seen];
}

// ---- Outline --------------------------------------------------------------------

interface OutlineItem {
  id: string;
  text: string;
  level: 1 | 2;
}

/** Collect the outline from the rendered page. */
function collect(root: HTMLElement): OutlineItem[] {
  const items: OutlineItem[] = [];
  const used = new Set<string>();
  // A lesson's own headings nest under its section. Lessons are written with
  // `##` or `###` as their top level; use whichever the lesson actually has.
  const headingSel = root.querySelector(".lesson-body .md h2") ? ".lesson-body .md h2" : ".lesson-body .md h3";
  const nodes = root.querySelectorAll<HTMLElement>(`[data-outline], ${headingSel}`);
  nodes.forEach((node) => {
    const isSection = node.hasAttribute("data-outline");
    const text = (isSection ? node.getAttribute("data-outline") : node.textContent)?.trim() ?? "";
    if (!text) return;
    if (!node.id) {
      let id = `${isSection ? "sec" : "h"}-${slugify(text)}`;
      let n = 2;
      while (used.has(id) || document.getElementById(id)) id = `${id}-${n++}`;
      node.id = id;
    }
    used.add(node.id);
    items.push({ id: node.id, text, level: isSection ? 1 : 2 });
  });
  return items;
}

/**
 * "On this page": the sections and lesson headings of `rootRef`, with the one
 * currently in view highlighted. Rebuilt whenever the page's DOM changes, since
 * sections open and close and lessons render late.
 */
export function PageOutline({ rootRef, title = "On this page" }: { rootRef: RefObject<HTMLElement>; title?: string }) {
  const [items, setItems] = useState<OutlineItem[]>([]);
  const [active, setActive] = useState<string>("");

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    let frame = 0;
    const rebuild = () => {
      frame = 0;
      const next = collect(root);
      setItems((prev) =>
        prev.length === next.length && prev.every((p, i) => p.id === next[i].id && p.text === next[i].text) ? prev : next
      );
    };
    rebuild();
    const mo = new MutationObserver(() => {
      if (!frame) frame = requestAnimationFrame(rebuild);
    });
    mo.observe(root, { childList: true, subtree: true });
    return () => {
      mo.disconnect();
      if (frame) cancelAnimationFrame(frame);
    };
  }, [rootRef]);

  // Scrollspy: the last heading whose top has passed a line near the top.
  useEffect(() => {
    const main = scroller();
    if (!main || items.length === 0) return;
    let frame = 0;
    const spy = () => {
      frame = 0;
      const line = main.getBoundingClientRect().top + 96;
      let current = items[0].id;
      for (const it of items) {
        const el = document.getElementById(it.id);
        if (el && el.getBoundingClientRect().top <= line) current = it.id;
      }
      setActive(current);
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(spy);
    };
    spy();
    main.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      main.removeEventListener("scroll", onScroll);
      if (frame) cancelAnimationFrame(frame);
    };
  }, [items]);

  const go = useCallback((id: string) => {
    const el = document.getElementById(id);
    if (!el) return;
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    // Move focus with the view, for keyboard and screen-reader users; the
    // target is made focusable just for this.
    if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
    el.focus({ preventScroll: true });
    setActive(id);
  }, []);

  if (items.length < 2) return null;

  return (
    <nav className="outline" aria-label={title}>
      <div className="outline-title">{title}</div>
      <ol>
        {items.map((it) => (
          <li key={it.id} className={`outline-l${it.level}`}>
            <a
              href={`#${it.id}`}
              className={active === it.id ? "active" : undefined}
              aria-current={active === it.id ? "location" : undefined}
              onClick={(e) => {
                // HashRouter owns the hash; an in-page anchor must not become a route.
                e.preventDefault();
                go(it.id);
              }}
            >
              {it.text}
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}

/**
 * A page with an outline rail. `aside` sits above the outline (a progress
 * summary, a done toggle); the rail is sticky, and folds into a disclosure
 * above the content when the page is narrow (a container query, so it
 * follows the sidebar being open or collapsed, not the window).
 */
export function ReaderLayout({
  children,
  aside,
  outlineTitle,
}: {
  children: ReactNode;
  aside?: ReactNode;
  outlineTitle?: string;
}) {
  const bodyRef = useRef<HTMLDivElement>(null);
  const progress = useReadingProgress(bodyRef);
  return (
    <div className="reader">
      <ReadingBar progress={progress} done={progress >= 0.999} />
      <div className="reader-layout">
        <div className="reader-body" ref={bodyRef}>
          {children}
        </div>
        <aside className="reader-rail" aria-label="Page navigation">
          {aside}
          <PageOutline rootRef={bodyRef} title={outlineTitle} />
          {/* The same outline, folded, for a compact window (CSS picks one). */}
          <details className="reader-outline-fold">
            <summary>{outlineTitle ?? "On this page"}</summary>
            <PageOutline rootRef={bodyRef} title={outlineTitle} />
          </details>
        </aside>
      </div>
    </div>
  );
}

// ---- Completion -------------------------------------------------------------------

export interface ReadStep {
  label: ReactNode;
  met: boolean;
}

/**
 * The completion rule, as a checklist that ticks itself: "read to the end",
 * "solve 3/5 exercises", "pass the self-check". It used to be a faint sentence
 * at the very bottom, visible only once you were already there.
 */
export function ReadStatus({
  steps,
  complete,
  onToggle,
  compact = false,
}: {
  steps: ReadStep[];
  complete: boolean;
  /** Manual override: mark done / undo. */
  onToggle?: () => void;
  compact?: boolean;
}) {
  return (
    <div className={`read-status ${complete ? "complete" : ""} ${compact ? "compact" : ""}`} role="status">
      <div className="read-status-head">
        <Icon name={complete ? "done" : "partial"} size={16} />
        <strong>{complete ? "Complete" : "To complete this page"}</strong>
      </div>
      {!complete && (
        <ul className="read-steps">
          {steps.map((s, i) => (
            <li key={i} className={s.met ? "met" : undefined}>
              <Icon name={s.met ? "check" : "todo"} size={13} label={s.met ? "Done" : "Not yet"} />
              <span>{s.label}</span>
            </li>
          ))}
        </ul>
      )}
      {onToggle && (
        <button type="button" className="link-button read-status-toggle" onClick={onToggle}>
          {complete ? "Mark as not done" : "Mark done now"}
        </button>
      )}
    </div>
  );
}
