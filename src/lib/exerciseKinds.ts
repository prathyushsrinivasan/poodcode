// How a lesson's or a step's exercises are grouped on the page, shared by every
// track that renders judged exercises (the TypeScript course, the Java course,
// the Projects track). Rendering lives in components/ExerciseSections.tsx; the
// grouping is here, with no React in it, so it can be tested directly.
//
// It is shared because of the failure it prevents. Each page used to filter into
// its own hard-coded buckets — `drill`/`fix`/`challenge` — which meant an
// exercise whose kind was not one of those three rendered nowhere at all while
// still counting towards the completion total. The result was a lesson stuck at
// "3/4 solved" with no fourth exercise on the page and no way to finish it.
// Adding a kind to a generator must never be able to do that again, so there is
// exactly one list, and anything missing from it falls through to the drill
// bucket rather than disappearing.

import type { Exercise } from "../types";

export type KindSection = {
  kind: string;
  heading: string;
  blurb?: string;
};

/** The sections, in the order they are worked. The order is the teaching order:
 * read code before writing it (predict, diagnose), fill in a blank, repair a
 * whole program (fix, retype), design from a spec, then solve end to end. */
export const KIND_SECTIONS: KindSection[] = [
  {
    kind: "predict",
    // Not 🔮 — that belongs to the "Predict the output" warm-up directly above,
    // and the two sit adjacent in every lesson that has both.
    heading: "🧠 Predict the type",
    blurb:
      "Before you write anything: say what TypeScript infers here. Write the type out in full — the point is to read the inference, not to ask for it.",
  },
  {
    kind: "diagnose",
    heading: "🩺 Read the error",
    blurb:
      "Here is a real compiler error and the code that produced it. Work out what it is telling you, then fix the cause.",
  },
  { kind: "drill", heading: "🧩 Practice — fill in the blank" },
  {
    kind: "fix",
    heading: "🐞 Fix the bug",
    blurb:
      "This program looks right but doesn't work. Find and fix the bug so the tests pass.",
  },
  {
    kind: "retype",
    heading: "🚫 Retype the any",
    blurb:
      "This program runs, and its types say nothing. Replace every `any` with a type that describes what is actually there — the hidden checks accept nothing vaguer.",
  },
  {
    kind: "design",
    heading: "📐 Design the type first",
    blurb:
      "Write the types before the code. Get the shape right and the implementation nearly falls out of it.",
  },
  { kind: "challenge", heading: "🏆 Coding challenge" },
];

/** The bucket unrecognised kinds fall into. */
const FALLBACK_KIND = "drill";

const KNOWN_KINDS = new Set(KIND_SECTIONS.map((s) => s.kind));

/** An exercise's kind, defaulted — the generators leave it empty for drills. */
export const kindOf = (e: Pick<Exercise, "kind">) => e.kind || FALLBACK_KIND;

/** The exercises belonging to one section. Unrecognised kinds are swept into
 * the fallback bucket rather than dropped — see the note at the top. */
export function bucketFor<T extends Pick<Exercise, "kind">>(exercises: T[], kind: string): T[] {
  return exercises.filter((e) =>
    kind === FALLBACK_KIND
      ? kindOf(e) === FALLBACK_KIND || !KNOWN_KINDS.has(kindOf(e))
      : kindOf(e) === kind
  );
}

/** Every exercise, grouped into its sections in teaching order, empty sections
 * dropped. Every input exercise appears in exactly one group. */
export function groupByKind<T extends Pick<Exercise, "kind">>(
  exercises: T[]
): { section: KindSection; group: T[] }[] {
  return KIND_SECTIONS.map((section) => ({
    section,
    group: bucketFor(exercises, section.kind),
  })).filter((g) => g.group.length > 0);
}
