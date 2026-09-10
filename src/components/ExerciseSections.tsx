import React from "react";
import type { Exercise } from "../types";
import { ExerciseCard } from "./LearnExercise";
import { groupByKind, type KindSection } from "../lib/exerciseKinds";

/** Every exercise, grouped into its sections and rendered in teaching order.
 *
 * The grouping — including the rule that an unrecognised kind is never dropped
 * — lives in lib/exerciseKinds.ts. This is only how it looks.
 *
 * `overrides` retunes a section's wording for one track without forking the
 * list: the Projects track calls its challenge section "Build it", because
 * there the challenge *is* the next piece of the application. */
export function ExerciseSections({
  exercises,
  onSolved,
  overrides = {},
}: {
  exercises: Exercise[];
  onSolved: (id: string) => void;
  overrides?: Record<string, Partial<Omit<KindSection, "kind">>>;
}) {
  return (
    <>
      {groupByKind(exercises).map(({ section, group }) => {
        const { heading, blurb } = { ...section, ...overrides[section.kind] };
        return (
          <React.Fragment key={section.kind}>
            <h4>{heading}</h4>
            {blurb && (
              <p className="dim" style={{ marginTop: -4 }}>
                {blurb}
              </p>
            )}
            {group.map((ex, i) => (
              <ExerciseCard
                key={ex.id}
                index={i + 1}
                exercise={ex}
                challenge={section.kind === "challenge"}
                onSolved={onSolved}
              />
            ))}
          </React.Fragment>
        );
      })}
    </>
  );
}
