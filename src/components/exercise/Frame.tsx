/**
 * The frame every exercise card shares: header (number, title, solved mark,
 * badges), prompt, body, action row. `ExerciseCard` fills it with an editor;
 * spot-the-bug fills it with clickable lines; quiz cards use the same
 * header and verdict slot. Keeping it separate from `ExerciseCard` is what lets
 * those other cards use it without an import cycle.
 */

import type { ReactNode } from "react";
import { CodeEditor } from "../CodeEditor";
import { Icon } from "../ui/Icon";
import { H } from "../ui/Heading";

export function ExerciseFrame({
  index,
  title,
  solved = false,
  emphasis = false,
  badges,
  prompt,
  children,
  className = "",
}: {
  index?: number;
  title: ReactNode;
  solved?: boolean;
  /** A challenge, or a kind that hands over a whole program: the accent frame. */
  emphasis?: boolean;
  badges?: ReactNode;
  /** The statement. A string keeps its authored line breaks. */
  prompt?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <article
      className={`card exercise ${solved ? "is-solved" : ""} ${emphasis ? "is-emphasis" : ""} ${className}`.trim()}
    >
      <header className="exercise-head">
        <H className="exercise-title">
          {index !== undefined && <span className="exercise-index">{index}.</span>} {title}
          {solved && (
            <span className="exercise-solved">
              <Icon name="done" size={15} label="Solved" />
            </span>
          )}
        </H>
        {badges && <div className="exercise-badges">{badges}</div>}
      </header>
      {prompt !== undefined && prompt !== null && prompt !== "" && (
        <div className={`exercise-prompt ${typeof prompt === "string" ? "is-text" : ""}`}>{prompt}</div>
      )}
      {children}
    </article>
  );
}

/** The row of buttons under the editor. */
export function ExerciseActions({ children }: { children: ReactNode }) {
  return <div className="exercise-actions">{children}</div>;
}

/** An editor whose height follows its starter, within limits. */
export function ExerciseEditor({
  language,
  value,
  onChange,
  onRun,
  strictness,
  lines,
  roomy = false,
  maxHeight,
}: {
  language: string;
  value: string;
  onChange: (v: string) => void;
  onRun?: () => void;
  strictness?: string;
  /** Line count of the starter, which sizes the editor. */
  lines: number;
  /** A whole program rather than a line with a blank: a taller minimum. */
  roomy?: boolean;
  maxHeight?: number;
}) {
  const height = Math.min(Math.max(lines * 20 + 24, roomy ? 260 : 150), maxHeight ?? (roomy ? 560 : 480));
  return (
    // The height is data (the starter's length), so it stays inline.
    <div className="exercise-editor" style={{ height }}>
      <CodeEditor language={language} value={value} onChange={onChange} onRun={onRun} tsStrictness={strictness} />
    </div>
  );
}

