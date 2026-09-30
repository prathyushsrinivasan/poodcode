import { describe, expect, it } from "vitest";
import seed from "../../src-tauri/seeds/new_dsa.json";
import type { NewDsa } from "../types";
import {
  READING_SECTIONS,
  isSectionDone,
  lessonProgress,
  masteryGates,
  nextSection,
  questionId,
  readId,
  sectionItems,
  sectionProgress,
  sittingId,
  sittingScore,
  topicStatus,
} from "./newDsa";

const course = seed as unknown as NewDsa;
const topic = course.topics[0]!;
const none = new Set<string>();

/** Every mark and problem that finishes sections 1-15. */
function allLessonMarks(): { ids: Set<string>; slugs: Set<string> } {
  const ids = new Set<string>();
  const slugs = new Set<string>();
  for (const s of course.sections) {
    const items = sectionItems(topic, s.key);
    items.ids.forEach((i) => ids.add(i));
    items.slugs.forEach((x) => slugs.add(x));
  }
  return { ids, slugs };
}

describe("NEW_DSA progress", () => {
  it("covers the sixteen sections, in the template's order", () => {
    expect(course.sections.map((s) => s.title)).toEqual([
      "Concept",
      "Mental Model",
      "TypeScript Fundamentals",
      "Syntax & Patterns",
      "When to Use It",
      "When NOT to Use It",
      "Step-by-Step Examples",
      "Implementation",
      "Complexity",
      "Common Mistakes",
      "Problem Recognition",
      "Guided Practice",
      "Independent Practice",
      "Variations",
      "Review",
      "Mastery",
    ]);
  });

  it("gives every lesson section something to finish, and mastery nothing", () => {
    for (const s of course.sections) {
      const p = sectionProgress(topic, s.key, none, none);
      if (s.key === "mastery") expect(p.total).toBe(0);
      else expect(p.total, s.key).toBeGreaterThan(0);
    }
  });

  it("finishes a reading section with its read mark", () => {
    for (const key of READING_SECTIONS) {
      const k = key as (typeof course.sections)[number]["key"];
      expect(isSectionDone(sectionProgress(topic, k, none, none))).toBe(false);
      expect(isSectionDone(sectionProgress(topic, k, new Set([readId(topic.key, key)]), none))).toBe(true);
    }
  });

  it("counts linked problems by their solved status", () => {
    const slugs = new Set(topic.independent.problems.slice(0, 2).map((p) => p.slug));
    expect(sectionProgress(topic, "independent", none, slugs)).toEqual({
      done: 2,
      total: topic.independent.problems.length,
    });
  });

  it("keys question marks by section and index", () => {
    expect(sectionItems(topic, "recognition").ids[3]).toBe(questionId(topic.key, "recognition", 3));
    expect(questionId("sliding-window", "complexity", 0)).toBe("ndsa:sliding-window:q:complexity:0");
  });

  it("points Continue at the first unfinished section, then at Mastery", () => {
    expect(nextSection(topic, course.sections, none, none)).toBe("concept");
    const read = new Set([readId(topic.key, "concept"), readId(topic.key, "mental_model")]);
    expect(nextSection(topic, course.sections, read, none)).toBe("ts_fundamentals");
    const all = allLessonMarks();
    expect(nextSection(topic, course.sections, all.ids, all.slugs)).toBe("mastery");
  });
});

describe("NEW_DSA mastery", () => {
  it("has the five abilities, all closed at the start", () => {
    const gates = masteryGates(topic, none, none);
    expect(gates.map((g) => g.ability)).toEqual([
      "understanding",
      "syntax",
      "recognition",
      "implementation",
      "application",
    ]);
    expect(gates.some((g) => g.passed)).toBe(false);
  });

  it("does not master a topic whose lessons are all done", () => {
    const all = allLessonMarks();
    const lessons = lessonProgress(topic, course.sections, all.ids, all.slugs);
    expect(lessons.done).toBe(lessons.total);
    expect(topicStatus(lessons, masteryGates(topic, all.ids, all.slugs))).toBe("lessons-done");
  });

  it("masters a topic only when every gate passes", () => {
    const m = topic.mastery;
    const ids = new Set([
      sittingId(topic.key, "understanding"),
      sittingId(topic.key, "recognition"),
      m.syntax.id,
      m.implementation.id,
    ]);
    const need = m.application.need;
    const short = new Set(m.application.problems.slice(0, need - 1).map((p) => p.slug));
    const enough = new Set(m.application.problems.slice(0, need).map((p) => p.slug));
    const empty = { done: 0, total: 10 };

    expect(topicStatus(empty, masteryGates(topic, ids, short))).toBe("learning");
    expect(topicStatus(empty, masteryGates(topic, ids, enough))).toBe("mastered");
  });

  it("scores a sitting by exact picks", () => {
    expect(sittingScore([0, 2, -1], [0, 1, 3])).toBe(1);
    expect(sittingScore([1, 1], [1, 1])).toBe(2);
  });

  it("says new, then learning", () => {
    expect(topicStatus({ done: 0, total: 5 }, masteryGates(topic, none, none))).toBe("new");
    expect(topicStatus({ done: 1, total: 5 }, masteryGates(topic, none, none))).toBe("learning");
  });
});
