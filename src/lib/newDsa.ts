import type { NdSection, NdTopic, Problem } from "../types";

/**
 * NEW_DSA progress and mastery (NEW_DSA.md, sections 1-16).
 *
 * Nothing new is stored. Every mark is an id in the `solved_exercises` table
 * the courses already use, namespaced `ndsa:<topic>:…`:
 *
 *   ndsa:<topic>:<section>:<name>   a judged exercise (its own `id`)
 *   ndsa:<topic>:q:<section>:<i>    a question answered correctly
 *   ndsa:<topic>:read:<section>     a reading section finished
 *   ndsa:<topic>:mastery:<gate>     a mastery sitting passed
 *
 * and linked problems count through the solved status the `problems` table
 * already holds. Never change these shapes: the rows in SQLite are keyed by
 * them.
 *
 * The one rule the template insists on is kept here: **finishing the lessons
 * does not master a topic**. Lessons (sections 1-15) and mastery (section 16)
 * are measured separately, and only the five mastery gates decide "mastered".
 */

export type SectionKey = NdSection["key"];

export const readId = (topic: string, section: string) => `ndsa:${topic}:read:${section}`;
export const questionId = (topic: string, section: string, i: number | string) => `ndsa:${topic}:q:${section}:${i}`;
export const sittingId = (topic: string, gate: "understanding" | "recognition") => `ndsa:${topic}:mastery:${gate}`;

/** What finishing a section means: marks to hold and problems to have solved. */
export interface SectionItems {
  ids: string[];
  slugs: string[];
}

/** Sections that are read rather than answered. Finishing one is a mark
 * written when the learner moves on from it. */
export const READING_SECTIONS: ReadonlySet<string> = new Set([
  "concept",
  "mental_model",
  "patterns",
  "when_to_use",
  "when_not",
  "mistakes",
  "review",
]);

export function sectionItems(t: NdTopic, key: SectionKey): SectionItems {
  const k = t.key;
  const none: SectionItems = { ids: [], slugs: [] };
  if (READING_SECTIONS.has(key)) return { ids: [readId(k, key)], slugs: [] };
  switch (key) {
    case "ts_fundamentals":
      return { ids: t.ts_fundamentals.drills.map((d) => d.id), slugs: [] };
    case "examples":
      return {
        ids: t.examples.flatMap((e, i) => (e.question ? [questionId(k, "examples", i)] : [])),
        slugs: [],
      };
    case "implementation": {
      const im = t.implementation;
      return { ids: [im.complete.id, im.pseudocode.exercise.id, im.scratch.id], slugs: [] };
    }
    case "complexity":
      return { ids: t.complexity.questions.map((_, i) => questionId(k, "complexity", i)), slugs: [] };
    case "recognition":
      return { ids: t.recognition.questions.map((_, i) => questionId(k, "recognition", i)), slugs: [] };
    case "guided":
      return { ids: t.guided.map((g) => g.exercise.id), slugs: [] };
    case "independent":
      return { ids: [], slugs: t.independent.problems.map((p) => p.slug) };
    case "variations":
      return {
        ids: t.variations.flatMap((v) => (v.exercise ? [v.exercise.id] : [])),
        slugs: t.variations.flatMap((v) => (v.slug ? [v.slug] : [])),
      };
    case "mastery":
      return none; // measured by `masteryGates`, never as a lesson
    default:
      return none;
  }
}

export interface Tally {
  done: number;
  total: number;
}

export function sectionProgress(
  t: NdTopic,
  key: SectionKey,
  solved: ReadonlySet<string>,
  solvedSlugs: ReadonlySet<string>
): Tally {
  const { ids, slugs } = sectionItems(t, key);
  return {
    done: ids.filter((i) => solved.has(i)).length + slugs.filter((s) => solvedSlugs.has(s)).length,
    total: ids.length + slugs.length,
  };
}

export function isSectionDone(p: Tally): boolean {
  return p.total > 0 && p.done >= p.total;
}

/** Sections 1-15, item by item. Mastery is deliberately not in here. */
export function lessonProgress(
  t: NdTopic,
  sections: NdSection[],
  solved: ReadonlySet<string>,
  solvedSlugs: ReadonlySet<string>
): Tally {
  return sections
    .filter((s) => s.key !== "mastery")
    .map((s) => sectionProgress(t, s.key, solved, solvedSlugs))
    .reduce((a, b) => ({ done: a.done + b.done, total: a.total + b.total }), { done: 0, total: 0 });
}

export type Ability = "understanding" | "syntax" | "recognition" | "implementation" | "application";

export interface Gate {
  ability: Ability;
  label: string;
  /** What the gate asks, in one line. */
  test: string;
  passed: boolean;
  /** Progress towards it, where that means something ("1 / 2 solved"). */
  detail: string;
}

export function masteryGates(t: NdTopic, solved: ReadonlySet<string>, solvedSlugs: ReadonlySet<string>): Gate[] {
  const m = t.mastery;
  const app = m.application.problems.filter((p) => solvedSlugs.has(p.slug)).length;
  return [
    {
      ability: "understanding",
      label: "Understanding",
      test: "Explain what the technique does and why it works",
      passed: solved.has(sittingId(t.key, "understanding")),
      detail: `pass mark ${m.understanding.pass} / ${m.understanding.questions.length}`,
    },
    {
      ability: "syntax",
      label: "Syntax",
      test: "Complete a TypeScript implementation",
      passed: solved.has(m.syntax.id),
      detail: "",
    },
    {
      ability: "recognition",
      label: "Recognition",
      test: "Identify the technique from a problem",
      passed: solved.has(sittingId(t.key, "recognition")),
      detail: `pass mark ${m.recognition.pass} / ${m.recognition.questions.length}`,
    },
    {
      ability: "implementation",
      label: "Implementation",
      test: "Implement it from scratch",
      passed: solved.has(m.implementation.id),
      detail: "",
    },
    {
      ability: "application",
      label: "Application",
      test: "Solve unfamiliar problems",
      passed: app >= m.application.need,
      detail: `${Math.min(app, m.application.need)} / ${m.application.need} solved`,
    },
  ];
}

export type TopicStatus = "new" | "learning" | "lessons-done" | "mastered";

export function topicStatus(lessons: Tally, gates: Gate[]): TopicStatus {
  if (gates.length > 0 && gates.every((g) => g.passed)) return "mastered";
  if (lessons.total > 0 && lessons.done >= lessons.total) return "lessons-done";
  if (lessons.done > 0 || gates.some((g) => g.passed)) return "learning";
  return "new";
}

/** Slugs of problems the learner has solved, from the problem bank. */
export function solvedSlugSet(problems: Problem[]): Set<string> {
  return new Set(problems.filter((p) => p.solved_status === "solved").map((p) => p.slug));
}

/** Right answers in a sitting. `picks[i]` must equal `expected[i]`. */
export function sittingScore(picks: number[], expected: number[]): number {
  return expected.filter((e, i) => picks[i] === e).length;
}

/** The first section, in template order, that is not finished yet — where
 * "Continue" goes. Mastery once every lesson is done. */
export function nextSection(
  t: NdTopic,
  sections: NdSection[],
  solved: ReadonlySet<string>,
  solvedSlugs: ReadonlySet<string>
): SectionKey {
  const open = sections.find(
    (s) => s.key !== "mastery" && !isSectionDone(sectionProgress(t, s.key, solved, solvedSlugs))
  );
  return (open ?? sections[sections.length - 1]!).key;
}
