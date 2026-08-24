import { describe, expect, it } from "vitest";
import type { MasteryProgress, MasteryTrack, MasteryWeek } from "../types";
import {
  drawExamPaper,
  formatStudyTime,
  MS_PER_WEEK,
  pacing,
  progressByWeek,
  unlockedWeeks,
  weekProgress,
  type ProgressMap,
} from "./mastery";

function week(n: number, concepts: string[], slugs: string[]): MasteryWeek {
  return {
    week: n,
    phase: "Month 1",
    title: `Week ${n}`,
    goal: "",
    concepts,
    problems: slugs.map((slug) => ({ slug, note: "" })),
    project: "Build something",
    quiz: [
      { question: "q1", options: ["a", "b"], answer: 0, explanation: "e1" },
      { question: "q2", options: ["a", "b"], answer: 1, explanation: "e2" },
      { question: "q3", options: ["a", "b", "c"], answer: 2, explanation: "e3" },
      { question: "q4", options: ["a", "b"], answer: 0, explanation: "e4" },
      { question: "q5", options: ["a", "b"], answer: 1, explanation: "e5" },
      { question: "q6", options: ["a", "b"], answer: 0, explanation: "e6" },
    ],
    quiz_sample: 4,
    exam: {
      title: "Final",
      prompt: "Do the thing",
      hint: "",
      language: "typescript",
      starter: "____",
      solution: "console.log(1);",
      tests: [{ input: "", output: "1" }],
    },
    contest: null,
  };
}

const track: MasteryTrack = {
  key: "ts",
  title: "Test track",
  language: "typescript",
  subtitle: "",
  intro: "",
  pass_mark: 75,
  exam_language: "typescript",
  weeks: [
    week(1, ["c1", "c2"], ["p1", "p2"]),
    week(2, ["c3"], ["p3"]),
    week(3, ["c4"], ["p4"]),
  ],
};

function row(overrides: Partial<MasteryProgress> & { week: number }): MasteryProgress {
  return {
    track_key: "ts",
    best_quiz: -1,
    exam_passed: false,
    exam_code: "",
    project_notes: "",
    project_code: "",
    project_done: false,
    study_seconds: 0,
    started_at: null,
    completed_at: null,
    ...overrides,
  };
}

/** Progress map from a list of partial rows. */
function progress(...rows: (Partial<MasteryProgress> & { week: number })[]): ProgressMap {
  return progressByWeek(rows.map(row), "ts");
}

const NONE: ProgressMap = new Map();

describe("progressByWeek", () => {
  it("keeps only the requested track's rows", () => {
    const rows = [row({ week: 1 }), { ...row({ week: 2 }), track_key: "java" }];
    const map = progressByWeek(rows, "ts");
    expect([...map.keys()]).toEqual([1]);
  });
});

describe("week progress", () => {
  it("counts chapters and problems independently", () => {
    const p = weekProgress(track.weeks[0], track, new Set(["c1"]), new Set(["p1", "p2"]), NONE);
    expect(p.conceptsDone).toBe(1);
    expect(p.conceptsTotal).toBe(2);
    expect(p.problemsSolved).toBe(2);
    expect(p.quizPassed).toBe(false);
    expect(p.examPassed).toBe(false);
    expect(p.complete).toBe(false);
  });

  it("requires chapters, the quiz AND the coding final", () => {
    const all = new Set(["c1", "c2"]);
    // Quiz passed, final passed, a chapter still unread.
    expect(
      weekProgress(track.weeks[0], track, new Set(["c1"]), new Set(),
        progress({ week: 1, best_quiz: 100, exam_passed: true })).complete
    ).toBe(false);
    // Chapters read and final passed, but the quiz was never taken.
    expect(
      weekProgress(track.weeks[0], track, all, new Set(),
        progress({ week: 1, exam_passed: true })).complete
    ).toBe(false);
    // Chapters read, quiz passed, final NOT accepted — multiple choice alone
    // must never be enough to unlock the next week.
    expect(
      weekProgress(track.weeks[0], track, all, new Set(),
        progress({ week: 1, best_quiz: 100 })).complete
    ).toBe(false);
    // Quiz below the pass mark.
    expect(
      weekProgress(track.weeks[0], track, all, new Set(),
        progress({ week: 1, best_quiz: 50, exam_passed: true })).complete
    ).toBe(false);
    // All three.
    expect(
      weekProgress(track.weeks[0], track, all, new Set(),
        progress({ week: 1, best_quiz: 75, exam_passed: true })).complete
    ).toBe(true);
  });

  it("does not require the curated problems or the project to unlock", () => {
    const p = weekProgress(track.weeks[0], track, new Set(["c1", "c2"]), new Set(),
      progress({ week: 1, best_quiz: 80, exam_passed: true }));
    expect(p.problemsSolved).toBe(0);
    expect(p.projectDone).toBe(false);
    expect(p.complete).toBe(true);
    // …but both still hold the progress bar below 100%.
    expect(p.percent).toBeLessThan(100);
  });

  it("treats a consolidation week with no chapters as study-complete", () => {
    const consolidation = week(1, [], ["p1"]);
    const p = weekProgress(consolidation, track, new Set(), new Set(),
      progress({ week: 1, best_quiz: 100, exam_passed: true }));
    expect(p.complete).toBe(true);
  });

  it("reports a null score for a week never attempted", () => {
    expect(weekProgress(track.weeks[0], track, new Set(), new Set(), NONE).score).toBeNull();
    expect(
      weekProgress(track.weeks[0], track, new Set(), new Set(),
        progress({ week: 1, best_quiz: 0 })).score
    ).toBe(0);
  });
});

describe("unlocking", () => {
  it("opens only week 1 on a fresh start", () => {
    expect([...unlockedWeeks(track, new Set(), new Set(), NONE)]).toEqual([1]);
  });

  it("opens the next week once the previous one is complete", () => {
    const done = new Set(["c1", "c2"]);
    const open = unlockedWeeks(track, done, new Set(),
      progress({ week: 1, best_quiz: 90, exam_passed: true }));
    expect([...open].sort()).toEqual([1, 2]);
  });

  it("stops at the first incomplete week rather than skipping ahead", () => {
    // Week 3's requirements are met, but week 2's are not — so 3 stays sealed.
    const done = new Set(["c1", "c2", "c4"]);
    const open = unlockedWeeks(track, done, new Set(),
      progress(
        { week: 1, best_quiz: 90, exam_passed: true },
        { week: 3, best_quiz: 100, exam_passed: true },
      ));
    expect([...open].sort()).toEqual([1, 2]);
  });

  it("keeps earlier weeks open after later ones unlock", () => {
    const done = new Set(["c1", "c2", "c3"]);
    const open = unlockedWeeks(track, done, new Set(),
      progress(
        { week: 1, best_quiz: 90, exam_passed: true },
        { week: 2, best_quiz: 80, exam_passed: true },
      ));
    expect([...open].sort()).toEqual([1, 2, 3]);
  });
});

describe("pacing", () => {
  const start = new Date("2026-01-01T00:00:00Z");

  it("puts you on week 1 on day one", () => {
    const p = pacing(start, 1, 26, start);
    expect(p.scheduledWeek).toBe(1);
    expect(p.weeksBehind).toBe(0);
  });

  it("reports being behind when the calendar has moved on", () => {
    const now = new Date(start.getTime() + 5 * MS_PER_WEEK);
    const p = pacing(start, 3, 26, now);
    expect(p.scheduledWeek).toBe(6);
    expect(p.weeksBehind).toBe(3);
  });

  it("reports being ahead when you outpace the schedule", () => {
    const now = new Date(start.getTime() + 2 * MS_PER_WEEK);
    const p = pacing(start, 6, 26, now);
    expect(p.scheduledWeek).toBe(3);
    expect(p.weeksBehind).toBe(-3);
  });

  it("never schedules past the final week", () => {
    const now = new Date(start.getTime() + 99 * MS_PER_WEEK);
    expect(pacing(start, 26, 26, now).scheduledWeek).toBe(26);
  });

  it("projects an earlier finish for a faster pace", () => {
    const now = new Date(start.getTime() + 4 * MS_PER_WEEK);
    const fast = pacing(start, 9, 26, now).projectedFinish; // 8 weeks in 4
    const slow = pacing(start, 3, 26, now).projectedFinish; // 2 weeks in 4
    expect(fast.getTime()).toBeLessThan(slow.getTime());
  });
});

describe("exam papers", () => {
  it("samples the configured number of questions from the bank", () => {
    const paper = drawExamPaper(track.weeks[0]);
    expect(paper).toHaveLength(4);
    expect(track.weeks[0].quiz).toHaveLength(6);
  });

  it("keeps the answer index pointing at the correct option after shuffling", () => {
    for (let i = 0; i < 50; i++) {
      for (const q of drawExamPaper(track.weeks[0])) {
        const source = track.weeks[0].quiz.find((s) => s.question === q.question)!;
        expect(q.options[q.answer]).toBe(source.options[source.answer]);
        expect([...q.options].sort()).toEqual([...source.options].sort());
      }
    }
  });

  it("draws different papers across retakes", () => {
    const seen = new Set<string>();
    for (let i = 0; i < 40; i++) {
      seen.add(drawExamPaper(track.weeks[0]).map((q) => q.question).join(","));
    }
    expect(seen.size).toBeGreaterThan(1);
  });

  it("never asks for more questions than the bank holds", () => {
    const small: MasteryWeek = { ...week(1, [], []), quiz_sample: 99 };
    expect(drawExamPaper(small)).toHaveLength(small.quiz.length);
  });
});

describe("formatStudyTime", () => {
  it("scales the unit to the magnitude", () => {
    expect(formatStudyTime(45)).toBe("45s");
    expect(formatStudyTime(600)).toBe("10m");
    expect(formatStudyTime(3600)).toBe("1h 0m");
    expect(formatStudyTime(5400)).toBe("1h 30m");
  });
});
