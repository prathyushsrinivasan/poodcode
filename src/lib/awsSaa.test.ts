import { describe, expect, it } from "vitest";
import { SAA_BY_ID, SAA_QUESTIONS } from "../data/awsSaa/questions";
import { SAA_DOMAINS, SAA_TOPICS } from "../data/awsSaa/schema";
import { emptySaaProgress, gradeSaa, parseSaaProgress, planSaaDaily, recordSaaAnswer, saaMistakes, saaStreak, startSaaDaily, validSaaSelection } from "./awsSaa";
import { optionOrder } from "./quizShuffle";

describe("SAA question bank", () => {
  it("contains 100 original complete scenarios across ten topics and four domains", () => {
    expect(SAA_QUESTIONS).toHaveLength(100);
    expect(SAA_BY_ID.size).toBe(100);
    expect(new Set(SAA_QUESTIONS.map((question) => question.prompt)).size).toBe(100);
    expect(new Set(SAA_QUESTIONS.map((question) => question.domain))).toEqual(new Set(Object.keys(SAA_DOMAINS)));
    for (const topic of SAA_TOPICS) expect(SAA_QUESTIONS.filter((question) => question.topic === topic.id)).toHaveLength(10);
    expect(SAA_QUESTIONS.filter((question) => question.correct.length > 1).length).toBeGreaterThanOrEqual(15);
    for (const question of SAA_QUESTIONS) {
      expect(question.prompt.length).toBeGreaterThan(100);
      expect(question.takeaway.length).toBeGreaterThan(40);
      expect(question.options).toHaveLength(question.correct.length === 1 ? 4 : 5);
      expect(new Set(question.options.map((option) => option.text)).size).toBe(question.options.length);
      for (const option of question.options) expect(option.explanation.length).toBeGreaterThan(35);
      expect(gradeSaa(question, question.correct)).toBe(true);
      const displayed = optionOrder(question.id, question.options.length, "2026-10-21");
      expect(new Set(displayed).size).toBe(question.options.length);
    }
    const firstPositions = new Set(SAA_QUESTIONS.map((question) => optionOrder(question.id, question.options.length, "2026-10-21").indexOf(question.correct[0])));
    expect(firstPositions.size).toBeGreaterThanOrEqual(4);
  });
});

describe("SAA exact-set grading", () => {
  const multiple = SAA_QUESTIONS.find((question) => question.correct.length > 1)!;
  it("requires all correct options and rejects extra, duplicate and invalid selections", () => {
    expect(gradeSaa(multiple, [...multiple.correct].reverse())).toBe(true);
    expect(gradeSaa(multiple, [multiple.correct[0]])).toBe(false);
    expect(gradeSaa(multiple, [...multiple.correct, 4])).toBe(false);
    expect(gradeSaa(multiple, [0, 0])).toBe(false);
    expect(validSaaSelection(multiple, [0, -1])).toBe(false);
    expect(validSaaSelection(multiple, [0, 0.5])).toBe(false);
    expect(validSaaSelection(multiple, [0, 50])).toBe(false);
    expect(validSaaSelection(multiple, [0, 2])).toBe(true);
    expect(gradeSaa(multiple, [0, 2])).toBe(false);
  });
});

describe("SAA daily planning and results", () => {
  it("chooses five distinct topics deterministically and rotates unseen items across days", () => {
    const progress = emptySaaProgress();
    const ids = planSaaDaily(progress, "2026-10-21");
    expect(ids).toHaveLength(5);
    expect(new Set(ids.map((id) => SAA_BY_ID.get(id)!.topic)).size).toBe(5);
    expect(planSaaDaily(progress, "2026-10-21")).toEqual(ids);
    expect(planSaaDaily(progress, "2026-10-22")).not.toEqual(ids);
  });
  it("prioritizes a previous mistake and freezes today's set despite unrelated practice", () => {
    const id = SAA_QUESTIONS[0].id;
    const wrong = recordSaaAnswer(emptySaaProgress(), id, [1], 10);
    expect(planSaaDaily(wrong, "2026-10-21")[0]).toBe(id);
    const started = startSaaDaily(wrong, "2026-10-21");
    const practiced = recordSaaAnswer(started, id, [0], 20);
    expect(saaMistakes(practiced)).not.toContain(id);
    expect(planSaaDaily(practiced, "2026-10-21")).toEqual(started.days["2026-10-21"].ids);
    expect(startSaaDaily(practiced, "2026-10-21")).toBe(practiced);
  });
  it("counts daily questions once and keeps topic practice separate from daily completion", () => {
    const day = "2026-10-21";
    const started = startSaaDaily(emptySaaProgress(), day);
    const id = started.days[day].ids[0];
    const question = SAA_BY_ID.get(id)!;
    const practiced = recordSaaAnswer(started, id, question.correct, 10);
    expect(Object.keys(practiced.days[day].answers)).toHaveLength(0);
    const daily = recordSaaAnswer(practiced, id, question.correct, 20, day);
    expect(daily.questions[id].attempts).toBe(2);
    expect(Object.keys(daily.days[day].answers)).toHaveLength(1);
    expect(recordSaaAnswer(daily, id, question.correct, 30, day)).toBe(daily);
    const outside = SAA_QUESTIONS.find((item) => !daily.days[day].ids.includes(item.id))!;
    expect(recordSaaAnswer(daily, outside.id, outside.correct, 30, day)).toBe(daily);
    expect(recordSaaAnswer(daily, id, [], 40)).toBe(daily);
    expect(recordSaaAnswer(daily, "missing", [0], 40)).toBe(daily);
  });
  it("preserves daily answers and resumes the remaining questions after a storage round trip", () => {
    const day = "2026-10-21";
    let progress = startSaaDaily(emptySaaProgress(), day);
    const id = progress.days[day].ids[0];
    progress = recordSaaAnswer(progress, id, SAA_BY_ID.get(id)!.correct, 1, day);
    const restored = parseSaaProgress(JSON.stringify(progress));
    expect(restored).toEqual(progress);
    expect(restored.days[day].ids.filter((item) => !restored.days[day].answers[item])).toHaveLength(4);
  });
  it("keeps a completed daily score unchanged when a mistake is corrected in practice", () => {
    const day = "2026-10-21";
    let progress = startSaaDaily(emptySaaProgress(), day);
    const id = progress.days[day].ids[0];
    const question = SAA_BY_ID.get(id)!;
    const wrong = question.correct.length === 1 ? [1] : [0, 2];
    progress = recordSaaAnswer(progress, id, wrong, 1, day);
    progress = recordSaaAnswer(progress, id, question.correct, 2);
    expect(progress.days[day].answers[id].correct).toBe(false);
    expect(progress.questions[id].lastCorrect).toBe(true);
  });
});

describe("SAA storage and calendar streaks", () => {
  it("ignores malformed rows, rejects unsupported versions and recomputes answer correctness", () => {
    expect(parseSaaProgress("bad JSON")).toEqual(emptySaaProgress());
    expect(parseSaaProgress('{"version":2}')).toEqual(emptySaaProgress());
    const day = "2026-10-21";
    const progress = startSaaDaily(emptySaaProgress(), day);
    const id = progress.days[day].ids[0];
    const serialized = { ...progress, questions: { [id]: { attempts: -1, correct: 10, lastCorrect: true, lastAt: 1 } },
      days: { ...progress.days, broken: { ids: [id] }, [day]: { ...progress.days[day], answers: {
        [id]: { selected: SAA_BY_ID.get(id)!.correct, correct: false },
      } } } };
    const parsed = parseSaaProgress(JSON.stringify(serialized));
    expect(parsed.questions).toEqual({});
    expect(parsed.days.broken).toBeUndefined();
    expect(parsed.days[day].answers[id].correct).toBe(true);
  });
  it("counts consecutive completed local days, allowing today to be unfinished", () => {
    let progress = emptySaaProgress();
    for (const day of ["2026-10-19", "2026-10-20"]) {
      progress = startSaaDaily(progress, day);
      for (const id of progress.days[day].ids) progress = recordSaaAnswer(progress, id, SAA_BY_ID.get(id)!.correct, 1, day);
    }
    expect(saaStreak(progress, new Date(2026, 9, 21, 1))).toBe(2);
    expect(saaStreak(progress, new Date(2026, 9, 22, 1))).toBe(0);
    expect(saaStreak(progress, new Date(2026, 9, 20, 23))).toBe(2);
  });
});
