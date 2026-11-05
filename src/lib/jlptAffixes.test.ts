import { describe, expect, it } from "vitest";
import { AFFIX_LESSONS, AFFIX_PROGRESS_KEY, AFFIX_QUESTIONS } from "../data/jlptAffixes";
import { drawAffixRound, filterAffixQuestions, type AffixFilters } from "./jlptAffixes";
import { N2_PROGRESS_KEY, n2Stats, parseN2Progress, recordN2Answer } from "./jlptN2";
import { optionOrder } from "./quizShuffle";
import { breadcrumb } from "./breadcrumb";

const all: AffixFilters = { level: "all", kind: "all", affix: "", query: "" };

describe("affix content integrity", () => {
  it("provides 300 distinct contextual problems, balanced across levels and word positions", () => {
    expect(AFFIX_LESSONS).toHaveLength(30);
    expect(AFFIX_QUESTIONS).toHaveLength(300);
    expect(new Set(AFFIX_LESSONS.map((l) => l.id)).size).toBe(30);
    expect(new Set(AFFIX_QUESTIONS.map((q) => q.id)).size).toBe(300);
    expect(new Set(AFFIX_QUESTIONS.map((q) => q.sentence)).size).toBe(300);
    for (const level of ["N3", "N2", "N1"] as const) {
      expect(filterAffixQuestions({ ...all, level })).toHaveLength(100);
      for (const kind of ["prefix", "suffix"] as const) {
        expect(filterAffixQuestions({ ...all, level, kind })).toHaveLength(50);
      }
    }
    for (const lesson of AFFIX_LESSONS) {
      expect(lesson.questions).toHaveLength(10);
      for (const q of lesson.questions) {
        expect(q.sentence.split("___"), q.id).toHaveLength(2);
        expect(q.sentence.replace("___", q.answer), q.id).toContain(q.word);
        expect(q.choices, q.id).toHaveLength(4);
        expect(new Set(q.choices).size, q.id).toBe(4);
        expect(q.choices.filter((a) => a === q.answer), q.id).toHaveLength(1);
        expect(q.reading, q.id).toMatch(/^[ぁ-ゖー]+$/u);
        expect(q.translation.trim(), q.id).not.toBe("");
        expect(q.explanation.trim(), q.id).not.toBe("");
        expect(q.lessonId).toBe(lesson.id);
        if (q.kind === "prefix") expect(q.word.startsWith(q.answer), q.id).toBe(true);
        else expect(q.word.endsWith(q.answer), q.id).toBe(true);
      }
    }
  });

  it("includes the exact requested athlete example and keeps grading independent of option position", () => {
    const q = AFFIX_QUESTIONS.find((q) => q.word === "名選手")!;
    expect(q.sentence).toBe("中村選手は日本を代表する___選手だ。");
    expect(q.choices).toEqual(["高", "優", "名", "真"]);
    expect(q.answer).toBe("名");
    const positions = new Set<number>();
    for (let seed = 0; seed < 20; seed++) {
      const choices = optionOrder(q.id, 4, String(seed)).map((i) => q.choices[i]);
      expect(choices.filter((c) => c === q.answer)).toHaveLength(1);
      positions.add(choices.indexOf(q.answer));
    }
    expect(positions.size).toBe(4);
  });
});

describe("affix selection and rounds", () => {
  it("combines level, position, affix, kana and English searches", () => {
    const selected = filterAffixQuestions({ ...all, level: "N1", kind: "prefix", affix: "非" });
    expect(selected.map((q) => q.word)).toEqual(["非公開", "非営利"]);
    expect(filterAffixQuestions({ ...all, query: "めいせんしゅ" }).map((q) => q.word)).toEqual(["名選手"]);
    expect(filterAffixQuestions({ ...all, query: "　ATHLETE　" }).some((q) => q.word === "名選手")).toBe(true);
    expect(filterAffixQuestions({ ...all, query: "nonexistent-word-xyz" })).toEqual([]);
  });

  it("draws a reproducible mixed round without duplicates, respecting the supplied filters", () => {
    const selected = filterAffixQuestions({ ...all, level: "N2", kind: "suffix" });
    const round = drawAffixRound(selected, {}, "mixed", 20, 1234);
    expect(round).toHaveLength(20);
    expect(new Set(round.map((q) => q.id)).size).toBe(20);
    expect(round.every((q) => q.level === "N2" && q.kind === "suffix")).toBe(true);
    expect(drawAffixRound(selected, {}, "mixed", 20, 1234)).toEqual(round);
    expect(drawAffixRound(selected, {}, "mixed", 20, 5678)).not.toEqual(round);
    expect(drawAffixRound(selected.slice(0, 3), {}, "mixed", 50, 1)).toHaveLength(3);
  });

  it("saves reveals as mistakes, resumes unanswered items, and keeps an active review stable", () => {
    const questions = AFFIX_LESSONS[0].questions;
    let progress = recordN2Answer({}, questions[0].id, false);
    progress = recordN2Answer(progress, questions[1].id, false);
    expect(AFFIX_PROGRESS_KEY).not.toBe(N2_PROGRESS_KEY);
    expect(parseN2Progress(JSON.stringify(progress), AFFIX_QUESTIONS)).toEqual(progress);
    expect(drawAffixRound(questions, progress, "lesson", 10, 1)[0]).toBe(questions[2]);
    const review = drawAffixRound(questions, progress, "review", 10, 1);
    progress = recordN2Answer(progress, questions[0].id, true);
    expect(review.map((q) => q.id)).toEqual([questions[0].id, questions[1].id]);
    expect(drawAffixRound(questions, progress, "review", 10, 1)).toEqual([questions[1]]);
    expect(n2Stats(questions, progress)).toEqual({ total: 10, attempted: 2, correct: 1, missed: 1 });
    expect(drawAffixRound([], {}, "mixed", 10, 1)).toEqual([]);
  });

  it("provides course, lesson and review breadcrumbs", () => {
    expect(breadcrumb("/japanese/n2/affixes/n3-praise").map((c) => c.label).slice(-2))
      .toEqual(["Prefixes & Suffixes", "Affix lesson"]);
    expect(breadcrumb("/japanese/n2/affixes/review").slice(-1)[0].label).toBe("Mistake review");
  });
});
