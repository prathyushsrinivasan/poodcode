/**
 * Headings that know how deep they are (UI_ROADMAP D9).
 *
 * The structure audit found pages jumping from h1 to h3 or h4: the collapsible
 * Section always rendered an h3, exercise and quiz cards an h4, whatever they
 * sat inside. A screen reader's heading list is the page's table of contents,
 * and skipped levels read as missing sections.
 *
 * A context carries the current level. The page's h1 is level 1, so content
 * starts at 2; anything that opens a section (`Section`, `UnitPart`,
 * `ExerciseSections`) renders its heading at the current level and gives its
 * body `Deeper`. `H` renders at the current level, capped at 6. Visual size
 * comes from classes, never from the tag.
 */

import { createContext, useContext, type ReactNode } from "react";

const LevelCtx = createContext(2);

export function useHeadingLevel(): number {
  return useContext(LevelCtx);
}

/** Everything inside is one heading level deeper. */
export function Deeper({ children, by = 1 }: { children: ReactNode; by?: number }) {
  const level = useContext(LevelCtx);
  return <LevelCtx.Provider value={Math.min(6, level + by)}>{children}</LevelCtx.Provider>;
}

/** Start a subtree at a given level (a page that renders its own h2s). */
export function AtLevel({ level, children }: { level: number; children: ReactNode }) {
  return <LevelCtx.Provider value={Math.max(1, Math.min(6, level))}>{children}</LevelCtx.Provider>;
}

/** A heading at the current level. */
export function H({ children, className, id }: { children: ReactNode; className?: string; id?: string }) {
  const level = Math.min(6, useContext(LevelCtx));
  const Tag = `h${level}` as "h2";
  return (
    <Tag className={className} id={id}>
      {children}
    </Tag>
  );
}
