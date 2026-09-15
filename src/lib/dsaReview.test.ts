import { describe, expect, it } from "vitest";
import { hydrate } from "./curriculum";
import {
  checkCardId,
  isCardDue,
  reviewLane,
  todayISO,
  unitChecks,
} from "./dsaReview";
import type {
  CardReview,
  CurriculumUnit,
  DsaCurriculum,
  Problem,
  Rung,
  SolvedStatus,
  UnitCheck,
} from "../types";

const NOW = new Date("2026-06-01T12:00:00");

function daysAgo(n: number): string {
  const d = new Date(NOW);
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 19).replace("T", " ");
}

function problem(slug: string, status: SolvedStatus = "unsolved", solvedAt: string | null = null): Problem {
  return {
    id: slug.length,
    slug,
    title: slug,
    difficulty: "Easy",
    description: "",
    constraints: "",
    examples: [],
    editorial: "",
    optimal_time: "",
    optimal_space: "",
    optimal_explanation: "",
    starter_code: {},
    topics: [],
    subtopics: [],
    companies: [],
    patterns: [],
    hints: [],
    prerequisites: [],
    test_cases: [],
    function_spec: null,
    judge_mode: "exact",
    float_tolerance: 0,
    checker: "",
    time_limit_ms: 0,
    editorials: [],
    follow_ups: [],
    order: 0,
    is_favorite: false,
    solved_status: status,
    confidence: 0,
    last_solved_at: solvedAt,
    time_taken_seconds: 0,
    attempts_count: 0,
    success_count: 0,
    created_at: "2024-01-01",
    updated_at: "2024-01-01",
  };
}

function rung(title: string, slugs: string[]): Rung {
  return { title, purpose: `do ${title}`, slugs, notes: {}, optional: false };
}

function unit(key: string, rungs: Rung[], checks: UnitCheck[] = []): CurriculumUnit {
  return {
    key,
    title: `Unit ${key}`,
    icon: "🔧",
    stage: "s1",
    tagline: `about ${key}`,
    weight: 2,
    prereqs: [],
    why: "why",
    model: "model",
    internals: "",
    signals: [],
    skeletons: [],
    traces: [],
    costs: [],
    pitfalls: [],
    lessons: [],
    checks,
    bigo: [],
    interview: "",
    rungs,
    build_it: "",
    next_up: "",
  };
}

function curriculum(units: CurriculumUnit[]): DsaCurriculum {
  return {
    key: "dsa",
    title: "DSA Curriculum",
    subtitle: "",
    intro: "",
    stages: [{ key: "s1", title: "Stage 1", icon: "🌱", tagline: "", goal: "", ordering: 0, units }],
  };
}

function review(cardId: string, dueDate: string, reps = 1): CardReview {
  return {
    card_id: cardId,
    ease: 2.5,
    reps,
    lapses: 0,
    interval_days: 7,
    due_date: dueDate,
    last_quality: 2,
  };
}

/** `hydrate` pinned to NOW with nothing marked known — every case here is about
 * decay, not about the skip list. */
function hy(c: DsaCurriculum, problems: Problem[]) {
  return hydrate(c, problems, new Set(), NOW);
}

const CHECKS: UnitCheck[] = [
  { q: "q0", a: "a0" },
  { q: "q1", a: "a1" },
];

describe("checkCardId", () => {
  it("is stable and namespaced, because SQLite rows are keyed by it", () => {
    expect(checkCardId("heaps", 0)).toBe("dsa-check:heaps:0");
    expect(checkCardId("dp-1d", 12)).toBe("dsa-check:dp-1d:12");
  });
});

describe("todayISO", () => {
  it("uses the local date, matching what the backend stores", () => {
    // 2026-06-01T23:30 local is still 2026-06-01 locally even where UTC has
    // rolled over, and comparing against a UTC slice would mark cards due a day
    // early or late depending on the machine's zone.
    expect(todayISO(new Date(2026, 5, 1, 23, 30))).toBe("2026-06-01");
    expect(todayISO(new Date(2026, 0, 9, 0, 5))).toBe("2026-01-09");
  });
});

describe("isCardDue", () => {
  it("treats a never-graded card as due", () => {
    expect(isCardDue(undefined, "2026-06-01")).toBe(true);
  });

  it("is due on the due date, not the day after", () => {
    expect(isCardDue(review("c", "2026-06-01"), "2026-06-01")).toBe(true);
    expect(isCardDue(review("c", "2026-06-02"), "2026-06-01")).toBe(false);
  });
});

describe("unit decay", () => {
  it("does not mark an unfinished unit stale, however old", () => {
    const c = curriculum([unit("u", [rung("Core", ["a", "b", "c"])])]);
    const h = hy(c, [problem("a", "solved", daysAgo(400)), problem("b"), problem("c")]);
    const u = h.stages[0].units[0];
    expect(u.status).toBe("started");
    expect(u.staleAfterDays).toBeNull();
    expect(u.stale).toBe(false);
  });

  it("gives a solid unit 30 days and a complete one 90", () => {
    const solidC = curriculum([unit("u", [rung("Core", ["a", "b", "c"])])]);
    const solid = hy(
      solidC,
      [problem("a", "solved", daysAgo(31)), problem("b", "solved", daysAgo(31)), problem("c")]
    ).stages[0].units[0];
    expect(solid.status).toBe("solid");
    expect(solid.staleAfterDays).toBe(30);
    expect(solid.stale).toBe(true);

    const completeC = curriculum([unit("u", [rung("Core", ["a"])])]);
    const complete = hy(completeC, [problem("a", "solved", daysAgo(31))]).stages[0]
      .units[0];
    expect(complete.status).toBe("complete");
    expect(complete.staleAfterDays).toBe(90);
    expect(complete.stale).toBe(false); // 31 days is well inside 90
  });

  it("measures from the MOST RECENT solve in the unit", () => {
    // One problem solved long ago and one solved yesterday is a unit you are
    // still working on, not one that has gone cold.
    const c = curriculum([unit("u", [rung("Core", ["a", "b", "c"])])]);
    const h = hy(
      c,
      [problem("a", "solved", daysAgo(300)), problem("b", "solved", daysAgo(1)), problem("c")]
    );
    const u = h.stages[0].units[0];
    expect(u.lastPractisedDays).toBe(1);
    expect(u.stale).toBe(false);
  });

  it("refuses to guess when a cleared unit has no solve date", () => {
    const c = curriculum([unit("u", [rung("Core", ["a"])])]);
    const u = hy(c, [problem("a", "solved", null)]).stages[0].units[0];
    expect(u.lastPractisedDays).toBe(Infinity);
    expect(u.stale).toBe(false);
  });
});

describe("unitChecks", () => {
  it("counts ungraded checks as due and graded-but-future as not", () => {
    const c = curriculum([unit("u", [rung("Core", ["a"])], CHECKS)]);
    const h = hy(c, [problem("a", "solved", daysAgo(1))]);
    const reviews = new Map([["dsa-check:u:0", review("dsa-check:u:0", "2026-12-01")]]);

    expect(unitChecks(h.stages[0].units[0], reviews, "2026-06-01")).toEqual({
      due: 1, // index 1 was never graded
      started: 1,
      total: 2,
    });
  });
});

describe("reviewLane", () => {
  it("draws only from cleared units", () => {
    const c = curriculum([
      unit("cleared", [rung("Core", ["a"])], CHECKS),
      unit("untouched", [rung("Core", ["b"])], CHECKS),
    ]);
    const h = hy(c, [problem("a", "solved", daysAgo(1)), problem("b")]);
    const lane = reviewLane(h, new Map(), NOW);

    expect(lane.units.map((r) => r.unit.unit.key)).toEqual(["cleared"]);
    expect(lane.checksDue).toBe(2);
    expect(lane.staleUnits).toBe(0);
  });

  it("orders by how overdue the practice is, then by checks waiting", () => {
    const c = curriculum([
      unit("recent", [rung("Core", ["a"])], CHECKS),
      unit("cold", [rung("Core", ["b", "c", "d"])], CHECKS),
    ]);
    const h = hy(
      c,
      [
        problem("a", "solved", daysAgo(1)),
        // 2 of 3 solved → solid → 30-day window, 200 days ago → 170 overdue
        problem("b", "solved", daysAgo(200)),
        problem("c", "solved", daysAgo(200)),
        problem("d"),
      ]
    );
    const lane = reviewLane(h, new Map(), NOW);

    expect(lane.units.map((r) => r.unit.unit.key)).toEqual(["cold", "recent"]);
    expect(lane.staleUnits).toBe(1);
    expect(lane.units[0].stale).toBe(true);
  });

  it("leaves a cleared unit out once nothing about it is due", () => {
    const c = curriculum([unit("u", [rung("Core", ["a"])], CHECKS)]);
    const h = hy(c, [problem("a", "solved", daysAgo(1))]);
    const reviews = new Map([
      ["dsa-check:u:0", review("dsa-check:u:0", "2026-12-01")],
      ["dsa-check:u:1", review("dsa-check:u:1", "2026-12-01")],
    ]);

    const lane = reviewLane(h, reviews, NOW);
    expect(lane.units).toEqual([]);
    expect(lane.checksDue).toBe(0);
  });

  it("includes a stale unit even when every check is scheduled far out", () => {
    const c = curriculum([unit("u", [rung("Core", ["a"])], CHECKS)]);
    const h = hy(c, [problem("a", "solved", daysAgo(200))]);
    const reviews = new Map([
      ["dsa-check:u:0", review("dsa-check:u:0", "2026-12-01")],
      ["dsa-check:u:1", review("dsa-check:u:1", "2026-12-01")],
    ]);

    const lane = reviewLane(h, reviews, NOW);
    expect(lane.checksDue).toBe(0);
    expect(lane.units.map((r) => r.unit.unit.key)).toEqual(["u"]);
    expect(lane.units[0].stale).toBe(true);
  });
});
