/**
 * A real tab bar: `role="tablist"`, roving tabindex, and ←/→/Home/End.
 *
 * The app had exactly one `role="tab"` in 48 files. Solve's seven tabs and the
 * curriculum's own were `div`s with `onClick`, which meant a keyboard could not
 * reach them at all and a screen reader announced nothing about what was
 * selected or how many there were.
 *
 * Counts are part of the contract rather than something each caller appends to
 * its label: an empty tab is worth not clicking, and saying so in the tab is
 * the cheapest way to communicate it (UI_ROADMAP F3).
 */

import { useRef, type ReactNode } from "react";

export interface TabSpec<K extends string> {
  key: K;
  label: ReactNode;
  /** Shown as a pill after the label. `0` renders muted, `undefined` omits it. */
  count?: number;
  disabled?: boolean;
}

export function Tabs<K extends string>({
  tabs,
  active,
  onChange,
  /** Ties the bar to its panel; the panel should carry `id={`${idBase}-panel`}`. */
  idBase,
  className = "",
  children,
}: {
  tabs: TabSpec<K>[];
  active: K;
  onChange: (key: K) => void;
  idBase: string;
  className?: string;
  /** Rendered at the right-hand end of the bar (shortcut hints, actions). */
  children?: ReactNode;
}) {
  const refs = useRef(new Map<K, HTMLButtonElement | null>());

  const move = (from: K, delta: number | "home" | "end") => {
    const usable = tabs.filter((t) => !t.disabled);
    if (usable.length === 0) return;
    let next: TabSpec<K>;
    if (delta === "home") next = usable[0];
    else if (delta === "end") next = usable[usable.length - 1];
    else {
      const i = usable.findIndex((t) => t.key === from);
      next = usable[(i + delta + usable.length) % usable.length];
    }
    onChange(next.key);
    refs.current.get(next.key)?.focus();
  };

  return (
    <div className={`tabs ${className}`} role="tablist">
      {tabs.map((t) => {
        const selected = t.key === active;
        return (
          <button
            key={t.key}
            ref={(el) => {
              refs.current.set(t.key, el);
            }}
            type="button"
            role="tab"
            id={`${idBase}-tab-${t.key}`}
            aria-selected={selected}
            aria-controls={`${idBase}-panel`}
            // Roving tabindex: one stop for the whole bar, arrows move within it.
            tabIndex={selected ? 0 : -1}
            disabled={t.disabled}
            className={`tab ${selected ? "active" : ""}`}
            onClick={() => onChange(t.key)}
            onKeyDown={(e) => {
              const k = e.key;
              if (k === "ArrowRight" || k === "ArrowDown") {
                e.preventDefault();
                move(t.key, 1);
              } else if (k === "ArrowLeft" || k === "ArrowUp") {
                e.preventDefault();
                move(t.key, -1);
              } else if (k === "Home") {
                e.preventDefault();
                move(t.key, "home");
              } else if (k === "End") {
                e.preventDefault();
                move(t.key, "end");
              }
            }}
          >
            {t.label}
            {t.count !== undefined && (
              <span className={`tab-count ${t.count === 0 ? "zero" : ""}`}>{t.count}</span>
            )}
          </button>
        );
      })}
      {children}
    </div>
  );
}

/** The panel a `Tabs` bar controls. Focusable so that tabbing off the bar
 * lands in the content it just revealed. */
export function TabPanel({
  idBase,
  active,
  children,
}: {
  idBase: string;
  active: string;
  children: ReactNode;
}) {
  return (
    <div
      id={`${idBase}-panel`}
      role="tabpanel"
      aria-labelledby={`${idBase}-tab-${active}`}
      tabIndex={0}
      className="tab-panel"
    >
      {children}
    </div>
  );
}
