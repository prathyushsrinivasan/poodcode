import { describe, expect, it } from "vitest";
import type { MasteryProgress, MasteryTrack, MasteryWeek } from "../types";
import {
  masteryWeekBySlug,
  currentMasteryWeek,
  coreWeeks,
  drawExamPaper,
  formatStudyTime,
  masteryResume,
  MS_PER_WEEK,
  pacing,
  progressByWeek,
  unlockedWeeks,
  weekProgress,
  weekTools,
  effectiveStart,
  togglePause,
  parsePause,
  todayPlan,
  daysLeftInWeek,
  interleavedWarmup,
  weekLinks,
  requeued,
  mostRetried,
  weakChapters,
  progressReport,
  skillProfile,
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

describe("masteryResume", () => {
  it("is null for a track never touched", () => {
    expect(masteryResume(track, [], undefined)).toBeNull();
  });

  it("starts at week 1 once a start date is set", () => {
    const r = masteryResume(track, [], "2026-09-01T00:00:00Z");
    expect(r?.week.week).toBe(1);
    expect(r?.completed).toBe(0);
    expect(r?.finished).toBe(false);
  });

  it("resumes at the first week without a completion stamp", () => {
    const rows = [row({ week: 1, completed_at: "x" }), row({ week: 2, best_quiz: 50 })];
    const r = masteryResume(track, rows, undefined);
    expect(r?.week.week).toBe(2);
    expect(r?.completed).toBe(1);
  });

  it("ignores other tracks' rows", () => {
    const other = { ...row({ week: 1, completed_at: "x" }), track_key: "java" };
    expect(masteryResume(track, [other], undefined)).toBeNull();
  });

  it("reports a finished track on its last week", () => {
    const rows = [1, 2, 3].map((n) => row({ week: n, completed_at: "x" }));
    const r = masteryResume(track, rows, undefined);
    expect(r?.finished).toBe(true);
    expect(r?.week.week).toBe(3);
    expect(r?.completed).toBe(3);
  });

  it("finishes without the optional week after the programme", () => {
    const withCapstone: MasteryTrack = {
      ...track,
      weeks: [...track.weeks, { ...week(4, [], ["p5"]), optional: true }],
    };
    expect(coreWeeks(withCapstone).map((w) => w.week)).toEqual([1, 2, 3]);
    const rows = [1, 2, 3].map((n) => row({ week: n, completed_at: "x" }));
    const r = masteryResume(withCapstone, rows, undefined);
    expect(r?.finished).toBe(true);
    expect(r?.total).toBe(3);
    expect(r?.completed).toBe(3);
  });
});

describe("weekTools", () => {
  it("points each stretch of the TypeScript programme at its tool", () => {
    const labels = (w: number) => weekTools("typescript", w).map((t) => t.label);
    expect(labels(11)).toContain("Narrowing stepper");
    expect(labels(14)).toContain("Strictness switcher");
    expect(labels(20)).toContain("Type expander");
    expect(labels(26)).toEqual(["Event loop", "Promise timeline", "Error glossary"]);
  });
  it("offers nothing on other tracks", () => {
    expect(weekTools("java", 5)).toEqual([]);
  });
});

describe("pauses", () => {
  const day = 24 * 3600 * 1000;
  it("shifts the start by every paused stretch, including one in progress", () => {
    const start = new Date("2026-01-01T00:00:00Z");
    const now = new Date("2026-01-20T00:00:00Z");
    expect(effectiveStart(start, { pausedAt: null, pausedMs: 3 * day }, now).getTime()).toBe(start.getTime() + 3 * day);
    expect(effectiveStart(start, { pausedAt: "2026-01-18T00:00:00Z", pausedMs: day }, now).getTime()).toBe(
      start.getTime() + 3 * day
    );
  });

  it("toggles on and off, banking the time", () => {
    const on = togglePause({ pausedAt: null, pausedMs: 0 }, new Date("2026-01-01T00:00:00Z"));
    expect(on.pausedAt).toBe("2026-01-01T00:00:00.000Z");
    const off = togglePause(on, new Date("2026-01-02T00:00:00Z"));
    expect(off).toEqual({ pausedAt: null, pausedMs: day });
  });

  it("parses defensively", () => {
    expect(parsePause("nope")).toEqual({ pausedAt: null, pausedMs: 0 });
    expect(parsePause(JSON.stringify({ pausedAt: "x", pausedMs: -1 }))).toEqual({ pausedAt: null, pausedMs: 0 });
  });
});

describe("todayPlan", () => {
  const base = {
    chaptersLeft: ["Narrowing", "Type predicates"],
    practiceLeft: 4,
    problemsLeft: 3,
    projectDone: false,
    hasProject: true,
    quizPassed: false,
    examPassed: false,
    daysLeft: 3,
  };

  it("puts the chapters first and spreads the rest over the days left", () => {
    // 2 chapters + 2 practice chunks + 2 problem chunks + project + quiz + final = 9 tasks over 3 days
    expect(todayPlan(base)).toEqual([
      "Read and mark done: Narrowing",
      "Read and mark done: Type predicates",
      "Solve 3 practice exercises",
    ]);
  });

  it("is empty when the week is done", () => {
    expect(
      todayPlan({ ...base, chaptersLeft: [], practiceLeft: 0, problemsLeft: 0, projectDone: true, quizPassed: true, examPassed: true })
    ).toEqual([]);
  });

  it("counts days left in the scheduled week", () => {
    const start = new Date("2026-01-01T00:00:00Z");
    expect(daysLeftInWeek(start, 1, new Date("2026-01-05T00:00:00Z"))).toBe(3);
    expect(daysLeftInWeek(start, 1, new Date("2026-01-20T00:00:00Z"))).toBe(1);
  });
});

describe("interleavedWarmup", () => {
  const weeks = [1, 2, 3, 4, 5, 6, 7].map((w) => ({
    week: w,
    practice: [0, 1, 2, 3].map((i) => ({ id: `w${w}-${i}` })),
  }));

  it("takes two from two weeks back and one from five weeks back", () => {
    const picks = interleavedWarmup(weeks, 7).map((e) => e.id);
    expect(picks).toHaveLength(3);
    expect(picks.filter((id) => id.startsWith("w5-"))).toHaveLength(2);
    expect(picks.filter((id) => id.startsWith("w2-"))).toHaveLength(1);
  });

  it("is empty at the start of the programme", () => {
    expect(interleavedWarmup(weeks, 1)).toEqual([]);
  });
});

describe("weekLinks", () => {
  it("links TypeScript weeks to course weeks and DSA units", () => {
    expect(weekLinks("typescript", 9)).toEqual({ course: [19], dsa: ["hashing"], projects: [] });
    expect(weekLinks("typescript", 26).projects.map((p) => p.to)).toEqual(["/backend", "/projects"]);
    expect(weekLinks("java", 9).course).toEqual([]);
  });

  it("covers every core week", () => {
    for (let w = 1; w <= 26; w++) expect(weekLinks("typescript", w).course.length).toBeGreaterThan(0);
  });
});

describe("using failed runs", () => {
  const ex = (id: string) => ({ id, title: id.toUpperCase() });
  const weeks = [
    { week: 1, practice: [ex("a"), ex("b")], problem_set: [ex("c")] },
    { week: 2, practice: [ex("d")] },
    { week: 3, practice: [ex("e")] },
  ];

  it("re-queues earlier exercises failed twice and still unsolved, worst first", () => {
    const failures = { a: 2, b: 5, c: 1, d: 3, e: 9 };
    expect(requeued(weeks, 3, failures, new Set(["d"])).map((e) => e.id)).toEqual(["b", "a"]);
  });

  it("finds the most retried exercise", () => {
    expect(mostRetried([ex("a"), ex("b")], { a: 1, b: 4 })).toEqual({ title: "B", count: 4 });
    expect(mostRetried([ex("a")], {})).toBeNull();
  });

  it("flags chapters with a low first-try rate", () => {
    const chapters = [
      { key: "k1", name: "Easy", exercises: [{ id: "x1" }, { id: "x2" }] },
      { key: "k2", name: "Hard", exercises: [{ id: "y1" }, { id: "y2" }, { id: "y3" }] },
      { key: "k3", name: "Untouched", exercises: [{ id: "z1" }] },
    ];
    const solved = new Set(["x1", "x2", "y1", "y2"]);
    const failures = { y1: 2, y2: 1, y3: 1 };
    expect(weakChapters(chapters, failures, solved)).toEqual([{ key: "k2", name: "Hard", attempted: 3, firstTry: 0 }]);
  });
});

describe("progressReport", () => {
  it("reports every week as JSON and as a Markdown table", () => {
    const t: MasteryTrack = { ...track, weeks: [week(1, ["a"], []), week(2, ["b"], [])] };
    const per = t.weeks.map((w) => weekProgress(w, t, new Set(["a"]), new Set(), new Map()));
    const { json, markdown } = progressReport(t, per, new Map(), new Date("2026-09-27T00:00:00Z"));
    const parsed = JSON.parse(json);
    expect(parsed.weeks).toHaveLength(2);
    expect(parsed.weeks[0].chapters).toBe("1/1");
    expect(markdown).toContain("| Week | Title |");
    expect(markdown).toContain("Exported 2026-09-27");
  });
});

describe("skillProfile", () => {
  it("counts each kind of work solved, and finals as programs", () => {
    const t: MasteryTrack = {
      ...track,
      weeks: [
        {
          ...week(1, [], []),
          practice: [
            { id: "p1", kind: "predict" },
            { id: "d1", kind: "diagnose" },
            { id: "t1", kind: "typelevel" },
          ] as never,
        },
      ],
    };
    const per = t.weeks.map((w) => weekProgress(w, t, new Set(), new Set(), new Map()));
    const skills = skillProfile(t, new Set(["p1", "t1"]), per);
    const by = Object.fromEntries(skills.map((s) => [s.label, `${s.done}/${s.total}`]));
    expect(by["Reading types"]).toBe("1/1");
    expect(by["Reading errors"]).toBe("0/1");
    expect(by["Writing types"]).toBe("1/1");
    expect(by["Writing programs"]).toBe("0/1");
  });
});

describe("masteryWeekBySlug / currentMasteryWeek", () => {
  const track = {
    key: "typescript",
    weeks: [
      { week: 2, problems: [{ slug: "b", note: "" }, { slug: "a", note: "Review" }] },
      { week: 1, problems: [{ slug: "a", note: "" }] },
    ],
  };
  it("maps each slug to the earliest week that curates it", () => {
    const m = masteryWeekBySlug(track as never);
    expect(m.get("a")).toBe(1);
    expect(m.get("b")).toBe(2);
    expect(m.has("c")).toBe(false);
  });
  it("puts an untouched learner on week 1", () => {
    const t = { key: "typescript", weeks: [{ week: 1 }, { week: 2 }] };
    expect(currentMasteryWeek(t as never, [])).toBe(1);
    const rows = [{ track_key: "typescript", week: 1, completed_at: "2026-09-01" }];
    expect(currentMasteryWeek(t as never, rows as never)).toBe(2);
  });
});
