import React, { useState } from "react";
import type { Exercise } from "../types";
import { ExerciseCard } from "./exercise";
import { inlineCode } from "./common";
import { groupByKind, type KindSection } from "../lib/exerciseKinds";

/** Every exercise, grouped into its sections and rendered in teaching order.
 *
 * The grouping — including the rule that an unrecognised kind is never dropped
 * — lives in lib/exerciseKinds.ts. This is only how it looks.
 *
 * `overrides` retunes a section's wording for one track without forking the
 * list: the Projects track calls its challenge section "Build it", because
 * there the challenge *is* the next piece of the application.
 *
 * `collapsible` folds each section behind its heading and count, the first one
 * open. A Mastery week's practice runs to forty exercises in ten kinds, and
 * every card owns an editor: folded sections mount theirs only when opened. */
export function ExerciseSections({
  exercises,
  onSolved,
  overrides = {},
  predictFirst = false,
  collapsible = false,
  solved,
}: {
  exercises: Exercise[];
  onSolved: (id: string) => void;
  overrides?: Record<string, Partial<Omit<KindSection, "kind">>>;
  /** Ask for a prediction before each run (M1-03). */
  predictFirst?: boolean;
  collapsible?: boolean;
  /** Solved exercise ids, for the per-section count when collapsible. */
  solved?: Set<string>;
}) {
  return (
    <>
      {groupByKind(exercises).map(({ section, group }, sectionIndex) => {
        const { heading, blurb } = { ...section, ...overrides[section.kind] };
        const cards = group.map((ex, i) => (
          <ExerciseCard
            key={ex.id}
            index={i + 1}
            exercise={ex}
            challenge={section.kind === "challenge"}
            onSolved={onSolved}
            predictFirst={predictFirst}
          />
        ));
        if (collapsible) {
          const done = solved ? group.filter((ex) => solved.has(ex.id)).length : null;
          return (
            <FoldedSection
              key={section.kind}
              heading={heading}
              blurb={blurb}
              count={done === null ? `${group.length}` : `${done}/${group.length}`}
              defaultOpen={sectionIndex === 0}
            >
              {cards}
            </FoldedSection>
          );
        }
        return (
          <React.Fragment key={section.kind}>
            <h4>{heading}</h4>
            {blurb && (
              <p className="dim" style={{ marginTop: -4 }}>
                {inlineCode(blurb)}
              </p>
            )}
            {cards}
          </React.Fragment>
        );
      })}
    </>
  );
}

/** One section behind a disclosure; its cards (and their editors) mount only
 * once it has been opened, and stay mounted so drafts are not lost. */
function FoldedSection({
  heading,
  blurb,
  count,
  defaultOpen,
  children,
}: {
  heading: string;
  blurb?: string;
  count: string;
  defaultOpen: boolean;
  children: React.ReactNode;
}) {
  const [opened, setOpened] = useState(defaultOpen);
  return (
    <details
      className="exercise-fold"
      open={defaultOpen}
      onToggle={(e) => {
        if ((e.currentTarget as HTMLDetailsElement).open) setOpened(true);
      }}
    >
      <summary>
        <strong>{heading}</strong> <span className="dim quiz-note">{count}</span>
      </summary>
      {blurb && (
        <p className="dim" style={{ marginTop: 4 }}>
          {inlineCode(blurb)}
        </p>
      )}
      {opened && children}
    </details>
  );
}
