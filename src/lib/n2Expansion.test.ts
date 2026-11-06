import { describe, expect, it } from "vitest";
import { JLPT_PRACTICE, JLPT_SECTIONS } from "../data/jlptSections";
import { STUDY_LESSONS, STUDY_QUESTIONS } from "../data/n2Study";
import { SPELLING_LESSONS } from "../data/n2Study/spelling";
import { READING_DRILL_LESSONS } from "../data/n2Study/readings";
import { VOCABULARY_LESSONS, VOCABULARY_TOPICS } from "../data/n2Study/vocabulary";
import { GRAMMAR_POINTS } from "../data/n2Study/grammar";
import { N2_ASSEMBLY_LESSONS } from "../data/jlptN2SentenceOrder";
import { READING_SKILL_LESSONS } from "../data/n2Study/readingSkills";
import { answerCorrect, beginQuestions, emptyStudy, finishSession, parseStudy, selectRound, startSession, updateDraft } from "./n2Study";

describe("expanded JLPT practice", () => {
  it("leaves only listening unavailable and connects each practice format to content", () => {
    for (const section of JLPT_SECTIONS.filter((s) => s.id !== "listening")) for (const item of section.items) expect(item.to).toBeTruthy();
    for (const practice of Object.values(JLPT_PRACTICE)) for (const id of practice.lessonIds) {
      expect(STUDY_LESSONS.some((l) => l.id === id)).toBe(true);
      expect(STUDY_QUESTIONS.some((q) => q.lessonId === id)).toBe(true);
    }
  });
  it("has substantive spelling and reading drills with literal underlined targets", () => {
    for (const lesson of [...SPELLING_LESSONS, ...READING_DRILL_LESSONS]) expect(STUDY_QUESTIONS.filter((q) => q.lessonId === lesson.id).length).toBeGreaterThanOrEqual(8);
    for (const q of STUDY_QUESTIONS.filter((q) => q.focus)) expect(q.prompt).toContain(q.focus);
  });
  it("accepts both dictionary-supported readings of a physical marketplace without using one as a wrong choice", () => {
    const typed = STUDY_QUESTIONS.find((q) => q.id === "context-readings-marketplace")!;
    expect(answerCorrect(typed, "いちば")).toBe(true);
    expect(answerCorrect(typed, "しじょう")).toBe(true);
    const choice = STUDY_QUESTIONS.find((q) => q.id === "reading-choice-marketplace")!;
    if (choice.kind !== "choice") throw new Error("Expected reading choices");
    expect(choice.choices.filter((_, i) => i !== choice.answer).some((c) => ["いちば", "しじょう"].includes(c.text))).toBe(false);
  });
  it("expands vocabulary formats with specialist practice and coverage across all eight topics", () => {
    for (const lesson of VOCABULARY_LESSONS) expect(STUDY_QUESTIONS.filter((q) => q.lessonId === lesson.id).length).toBeGreaterThanOrEqual(6);
    expect(STUDY_QUESTIONS.filter((q) => q.lessonId === "context").length).toBeGreaterThanOrEqual(30);
    expect(STUDY_QUESTIONS.filter((q) => q.lessonId === "paraphrase").length).toBeGreaterThanOrEqual(12);
    expect(STUDY_QUESTIONS.filter((q) => q.lessonId === "usage").length).toBeGreaterThanOrEqual(8);
    for (const topic of VOCABULARY_TOPICS) expect(STUDY_QUESTIONS.filter((q) => q.tags.includes(`topic:${topic}`)).length).toBeGreaterThanOrEqual(4);
  });
  it("connects grammar references, formation/contrast/correction/register practice and passage grammar", () => {
    expect(GRAMMAR_POINTS.length).toBeGreaterThanOrEqual(12);
    for (const point of GRAMMAR_POINTS) {
      const lessonId = `grammar-${point.id}`;
      expect(JLPT_PRACTICE.grammar.lessonIds).toContain(lessonId);
      expect(STUDY_QUESTIONS.filter((q) => q.lessonId === lessonId).length).toBeGreaterThanOrEqual(2);
      expect(point.examples).toHaveLength(2);
      expect(point.formation.length).toBeGreaterThan(20);
      expect(point.register.length).toBeGreaterThan(20);
    }
    for (const exercise of ["Formation", "Comparison", "Correction", "Register"]) expect(STUDY_QUESTIONS.filter((q) => q.tags.includes(`exercise:${exercise}`)).length).toBeGreaterThanOrEqual(6);
    const passageQuestions = STUDY_QUESTIONS.filter((q) => q.id.startsWith("text-passage-"));
    expect(passageQuestions).toHaveLength(12);
    for (const q of passageQuestions) {
      expect(q.texts![0].text.split("\n\n")).toHaveLength(3);
      for (const slot of [1, 2, 3]) expect(q.texts![0].text).toContain(`【${slot}】`);
    }
  });
  it("shares the full assembly bank while preserving previously practised question IDs and alternatives", () => {
    const assembly = STUDY_QUESTIONS.filter((q) => q.kind === "assembly");
    expect(assembly).toHaveLength(N2_ASSEMBLY_LESSONS.reduce((n, l) => n + l.questions.length, 0));
    for (const id of ["s01-1", "s02-1", "s03-1", "s04-1"]) expect(assembly.some((q) => q.id === `assembly-${id}`)).toBe(true);
  });
  it("offers all seven reading skills, reviewed clause breakdowns and rectangular information tables", () => {
    for (const lesson of READING_SKILL_LESSONS) expect(STUDY_QUESTIONS.filter((q) => q.lessonId === lesson.id).length).toBeGreaterThanOrEqual(4);
    const structures = STUDY_QUESTIONS.filter((q) => q.lessonId === "reading-structure");
    for (const q of structures) {
      expect(q.breakdown?.modifiers.length).toBeGreaterThan(0);
      expect(q.texts![0].text).toContain(q.breakdown!.sentence);
    }
    const tables = STUDY_QUESTIONS.filter((q) => q.lessonId === "reading-tables");
    expect(tables).toHaveLength(9);
    for (const q of tables) {
      const table = q.texts![0].table!;
      expect(table.caption.length).toBeGreaterThan(0);
      expect(table.rows.length).toBeGreaterThanOrEqual(3);
      for (const row of table.rows) expect(row).toHaveLength(table.columns.length);
    }
  });
  it("grades spelling through timed rounds and saved-state recovery", () => {
    const pool = STUDY_QUESTIONS.filter((q) => JLPT_PRACTICE["kanji-spelling"].lessonIds.includes(q.lessonId));
    const ids = selectRound(emptyStudy(), pool, 5, 1000);
    let state = beginQuestions(startSession(emptyStudy(), ids, "timed", "Spelling", 1000, "spelling-round"), 1000);
    const q = pool.find((q) => q.id === ids[0])!;
    if (q.kind !== "choice") throw new Error("Expected spelling choices");
    state = updateDraft(state, { answer: String(q.answer), confidence: "sure" }, 2000);
    state = finishSession(parseStudy(JSON.stringify(state)), 3000);
    expect(state.attempts).toHaveLength(5);
    expect(state.session!.results[q.id].correct).toBe(true);
    expect(state.attempts.filter((a) => !a.correct)).toHaveLength(4);
  });
});
