/** What the Projects pages share (UI_ROADMAP G7). */

import type { ProjectModule } from "../../types";
import { collectExerciseIds } from "../../lib/trackProgress";

// Module completion is tracked in the same SQLite-backed chapter-done set as
// the Learn tab, the courses and the Backend Lab, under a namespaced key so it
// can never collide with a concept key, a course week or a backend project.
export const moduleKey = (projectKey: string, key: string) => `project:${projectKey}:${key}`;

/** Every judged exercise required to complete a module. */
export const requiredExerciseIds = (m: ProjectModule) => collectExerciseIds(m.steps, m.final_build);

/** The project-level pages that are not a module. Each has a static route in
 * App.tsx, so none can be shadowed by a module that one day takes the key. */
export type ProjectView = "reference" | "history" | "workbench" | "review";
