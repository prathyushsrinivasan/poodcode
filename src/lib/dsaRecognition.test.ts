import { describe, expect, it } from "vitest";
import { hydrate } from "./curriculum";
import {
  mixedSet,
  placement,
  rng,
  routeCardId,
  routingQuestion,
  shuffled,
  techniqueLabel,
  variantCardId,
  variantQuestions,
} from "./dsaRecognition";
import type {
  CurriculumUnit,
  Difficulty,
  DsaCurriculum,
  Problem,
  Rung,
  Signal,
  SolvedStatus,
  StageRoute,
  Variant,
} from "../types";

function problem(
  slug: string,
  difficulty: Difficulty = "Medium",
  status: SolvedStatus = "unsolved"
): Problem {
  return {
    id: slug.length,
    slug,
    title: slug,
    difficulty,
    description: `Statement for ${slug}.\n\nA second paragraph nobody should see in the prompt.`,
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
    last_solved_at: null,
    time_taken_seconds: 0,
    attempts_count: 0,
    success_count: 0,
    created_at: "2024-01-01",
    updated_at: "2024-01-01",
  };
}

function sig(reach: string): Signal {
  return { when: "when the prompt says something", reach_for: reach, why: "" };
}

function rung(title: string, slugs: string[], optional = false): Rung {
  return { title, purpose: `do ${title}`, slugs, notes: {}, optional };
}

function unit(key: string, title: string, slugs: string[], signals: Signal[] = []): CurriculumUnit {
  return {
    key,
    title,
    icon: "🔧",
    stage: "s1",
    tagline: "",
    weight: 2,
    prereqs: [],
    why: "why",
    model: "model",
    internals: "",
    signals,
    skeletons: [],
    traces: [],
    costs: [],
    pitfalls: [],
    lessons: [],
    checks: [],
    bigo: [],
    interview: "",
    rungs: [rung("Core", slugs)],
    build_it: "",
    next_up: "",
    invariant: null,
    variants: [],
    rewrites: [],
    quizzes: [],
    lab: null,
    drills: [],
    stuck: [],
    edge_cases: [],
    walkthrough: null,
  };
}

function curriculum(
  stages: { key: string; units: CurriculumUnit[]; router?: StageRoute[] }[]
): DsaCurriculum {
  return {
    key: "dsa",
    title: "DSA Curriculum",
    subtitle: "",
    intro: "",
    stages: stages.map((s, i) => ({
      key: s.key,
      title: `Stage ${i + 1}`,
      icon: "🌱",
      tagline: "",
      goal: "",
      ordering: i,
      router: s.router ?? [],
      units: s.units,
    })),
  };
}

const FOUR = curriculum([
  {
    key: "s1",
    units: [
      unit("hashing", "Hashing", ["h1", "h2"], [sig("a complement map")]),
      unit("two-pointers", "Two Pointers", ["t1"], [sig("two converging pointers")]),
    ],
  },
  {
    key: "s2",
    units: [
      unit("heaps", "Heaps & Priority Queues", ["p1"], [sig("a min-heap")]),
      unit("stacks", "Stacks", ["s1"], [sig("a monotonic stack")]),
    ],
  },
]);

const PROBLEMS = ["h1", "h2", "t1", "p1", "s1"].map((s) => problem(s));

describe("rng / shuffled", () => {
  it("is deterministic for a seed, so today's set does not reshuffle on reload", () => {
    const a = shuffled([1, 2, 3, 4, 5, 6, 7, 8], rng(42));
    const b = shuffled([1, 2, 3, 4, 5, 6, 7, 8], rng(42));
    expect(a).toEqual(b);
    expect(shuffled([1, 2, 3, 4, 5, 6, 7, 8], rng(43))).not.toEqual(a);
    expect([...a].sort((x, y) => x - y)).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
  });
});

describe("techniqueLabel", () => {
  it("is the unit's title, which identifies a unit on its own", () => {
    // Signal `reach_for` cells are written to sit next to their `when` in a
    // table, so as standalone options they read as "Two passes" or "`long`" —
    // and worse, they collide (graph-traversal and shortest-paths both say
    // "BFS"), which would make the question unanswerable.
    const h = hydrate(FOUR, PROBLEMS);
    expect(techniqueLabel(h.stages[0].units[0])).toBe("Hashing");
    expect(techniqueLabel(h.stages[1].units[0])).toBe("Heaps & Priority Queues");
  });

  it("is unique across the real curriculum's units", () => {
    const labels = FOUR.stages.flatMap((s) => s.units).map((u) => u.title);
    expect(new Set(labels).size).toBe(labels.length);
  });
});

describe("routingQuestion", () => {
  it("offers the right answer plus distractors from sibling units", () => {
    const h = hydrate(FOUR, PROBLEMS);
    const pool = h.stages.flatMap((s) => s.units);
    const q = routingQuestion(pool[0], pool, rng(7))!;

    expect(q.answerUnit).toBe("hashing");
    expect(q.answerLabel).toBe("Hashing");
    expect(q.options).toContain("Hashing");
    expect(q.options).toHaveLength(4);
    expect(new Set(q.options).size).toBe(4); // no duplicate labels
    expect(["h1", "h2"]).toContain(q.problem.slug);
  });

  it("carries a signal row so a miss sends you back to the wording", () => {
    const h = hydrate(FOUR, PROBLEMS);
    const pool = h.stages.flatMap((s) => s.units);
    const q = routingQuestion(pool[0], pool, rng(7))!;
    expect(q.signalHint).toEqual({
      when: "when the prompt says something",
      reachFor: "a complement map",
    });
  });

  it("has no signal hint for a unit with no signals table", () => {
    const c = curriculum([
      {
        key: "s1",
        units: [
          unit("a", "A", ["h1"]),
          unit("b", "B", ["h2"], [sig("b")]),
          unit("c", "C", ["t1"], [sig("c")]),
        ],
      },
    ]);
    const h = hydrate(c, [problem("h1"), problem("h2"), problem("t1")]);
    const pool = h.stages.flatMap((s) => s.units);
    expect(routingQuestion(pool[0], pool, rng(2))!.signalHint).toBeNull();
  });

  it("refuses rather than asking a two-option coin toss", () => {
    const c = curriculum([
      { key: "s1", units: [unit("a", "A", ["h1"], [sig("technique a")])] },
    ]);
    const h = hydrate(c, [problem("h1")]);
    const pool = h.stages.flatMap((s) => s.units);
    expect(routingQuestion(pool[0], pool, rng(1))).toBeNull();
  });

  it("prefers an unsolved problem, but uses a solved one rather than nothing", () => {
    const allSolved = PROBLEMS.map((p) => ({ ...p, solved_status: "solved" as SolvedStatus }));
    const h = hydrate(FOUR, allSolved);
    const pool = h.stages.flatMap((s) => s.units);
    const q = routingQuestion(pool[0], pool, rng(3))!;
    expect(["h1", "h2"]).toContain(q.problem.slug);

    const mixed = PROBLEMS.map((p) =>
      p.slug === "h1" ? { ...p, solved_status: "solved" as SolvedStatus } : p
    );
    const h2 = hydrate(FOUR, mixed);
    const pool2 = h2.stages.flatMap((s) => s.units);
    // "h2" is the only unsolved problem in hashing, so it must be the one asked.
    expect(routingQuestion(pool2[0], pool2, rng(3))!.problem.slug).toBe("h2");
  });
});

describe("mixedSet", () => {
  it("draws from this stage and every earlier one", () => {
    const h = hydrate(FOUR, PROBLEMS);
    const set = mixedSet(h, "s2", 11, 6);
    const units = new Set(set.map((q) => q.answerUnit));
    // Stage 2's own units plus stage 1's are all eligible.
    expect(units.size).toBeGreaterThan(2);
    expect([...units].some((k) => k === "hashing" || k === "two-pointers")).toBe(true);
  });

  it("never asks about the same problem twice", () => {
    const h = hydrate(FOUR, PROBLEMS);
    const set = mixedSet(h, "s2", 5, 10);
    const slugs = set.map((q) => q.problem.slug);
    expect(new Set(slugs).size).toBe(slugs.length);
  });

  it("is stable for a seed and empty for an unknown stage", () => {
    const h = hydrate(FOUR, PROBLEMS);
    expect(mixedSet(h, "s2", 9).map((q) => q.problem.slug)).toEqual(
      mixedSet(h, "s2", 9).map((q) => q.problem.slug)
    );
    expect(mixedSet(h, "nope", 9)).toEqual([]);
  });
});

describe("placement", () => {
  it("offers one routing question and one representative problem per stage", () => {
    const h = hydrate(FOUR, PROBLEMS);
    const stages = placement(h, 4);
    expect(stages).toHaveLength(2);
    for (const s of stages) {
      expect(s.question).not.toBeNull();
      expect(s.problem).not.toBeNull();
      expect(s.unitKeys.length).toBeGreaterThan(0);
      expect(s.alreadyCleared).toBe(false);
    }
  });

  it("names every unit the stage would mark known", () => {
    const h = hydrate(FOUR, PROBLEMS);
    expect(placement(h, 4)[0].unitKeys).toEqual(["hashing", "two-pointers"]);
  });

  it("prefers the hardest non-Hard problem as representative", () => {
    // A stage's stretch problem is not what "you can skip this stage" should
    // hinge on.
    const c = curriculum([
      { key: "s1", units: [unit("u", "U", ["easy", "med", "hard"], [sig("a")])] },
    ]);
    const h = hydrate(c, [
      problem("easy", "Easy"),
      problem("med", "Medium"),
      problem("hard", "Hard"),
    ]);
    expect(placement(h, 1)[0].problem?.slug).toBe("med");
  });

  it("reports a stage as already cleared when every unit is", () => {
    const solved = PROBLEMS.map((p) => ({ ...p, solved_status: "solved" as SolvedStatus }));
    const h = hydrate(FOUR, solved);
    expect(placement(h, 4).every((s) => s.alreadyCleared)).toBe(true);
  });

  it("skips an optional stage — there is nothing to place into", () => {
    const c: DsaCurriculum = { ...FOUR, stages: FOUR.stages.map((s, i) => ({ ...s, optional: i === 1 })) };
    const stages = placement(hydrate(c, PROBLEMS), 4);
    expect(stages.map((s) => s.stageKey)).toEqual([FOUR.stages[0].key]);
  });

  it("counts a unit marked known toward the stage being cleared", () => {
    const h = hydrate(FOUR, PROBLEMS, new Set(["hashing", "two-pointers"]));
    expect(placement(h, 4)[0].alreadyCleared).toBe(true);
    expect(placement(h, 4)[1].alreadyCleared).toBe(false);
  });
});

describe("routeCardId", () => {
  it("is namespaced apart from the self-check cards", () => {
    expect(routeCardId("heaps")).toBe("dsa-route:heaps");
    expect(routeCardId("heaps")).not.toBe("dsa-check:heaps:0");
  });
});

function variant(name: string, when: string): Variant {
  return { name, change: `change for ${name}`, when, cost: "O(n)", gotcha: `watch ${name}` };
}

/** A hydrated unit carrying a family table, with no problems needed — the
 * family drill is derived from authored variants alone. */
function unitWithVariants(key: string, variants: Variant[]) {
  const u = unit(key, `Unit ${key}`, ["p1"]);
  const c = hydrate(curriculum([{ key: "s1", units: [{ ...u, variants }] }]), [
    problem("p1", "Easy"),
  ]);
  return c.stages[0].units[0];
}

describe("variantQuestions", () => {
  it("asks one question per variant, prompting with its `when`", () => {
    const hu = unitWithVariants("sw", [
      variant("Fixed width", "every window of size k"),
      variant("Longest valid", "longest substring with at most k distinct"),
      variant("Shortest valid", "smallest subarray with sum at least target"),
      variant("Exactly k", "count subarrays with exactly k distinct"),
    ]);
    const qs = variantQuestions(hu);
    expect(qs).toHaveLength(4);
    expect(qs.map((q) => q.prompt)).toEqual([
      "every window of size k",
      "longest substring with at most k distinct",
      "smallest subarray with sum at least target",
      "count subarrays with exactly k distinct",
    ]);
    expect(qs.map((q) => q.answerLabel)).toEqual([
      "Fixed width",
      "Longest valid",
      "Shortest valid",
      "Exactly k",
    ]);
  });

  it("draws every distractor from the SAME unit, so each is plausible", () => {
    const names = ["Fixed width", "Longest valid", "Shortest valid", "Exactly k"];
    const hu = unitWithVariants("sw", names.map((n, i) => variant(n, `prompt ${i}`)));
    for (const q of variantQuestions(hu)) {
      expect(q.options).toContain(q.answerLabel);
      for (const o of q.options) expect(names).toContain(o);
      // No duplicate options — a repeated label makes the question unanswerable.
      expect(new Set(q.options).size).toBe(q.options.length);
    }
  });

  it("carries the edit and the caveat, so a wrong answer teaches", () => {
    const hu = unitWithVariants("sw", [
      variant("A", "prompt a"),
      variant("B", "prompt b"),
      variant("C", "prompt c"),
    ]);
    const q = variantQuestions(hu)[0];
    expect(q.change).toBe("change for A");
    expect(q.gotcha).toBe("watch A");
    expect(q.unitKey).toBe("sw");
  });

  it("returns nothing below three variants — two options is a coin toss", () => {
    expect(variantQuestions(unitWithVariants("x", []))).toEqual([]);
    expect(variantQuestions(unitWithVariants("x", [variant("A", "a")]))).toEqual([]);
    expect(
      variantQuestions(unitWithVariants("x", [variant("A", "a"), variant("B", "b")]))
    ).toEqual([]);
  });

  it("skips variants with no prompt to ask about", () => {
    const hu = unitWithVariants("x", [
      variant("A", "a"),
      variant("B", "b"),
      variant("C", "c"),
      { name: "D", change: "d", when: "   ", cost: "O(1)", gotcha: "" },
    ]);
    const qs = variantQuestions(hu);
    expect(qs.map((q) => q.answerLabel)).toEqual(["A", "B", "C"]);
  });

  it("is stable for a given seed, so a card id keeps meaning the same question", () => {
    const hu = unitWithVariants("x", [
      variant("A", "a"),
      variant("B", "b"),
      variant("C", "c"),
      variant("D", "d"),
    ]);
    expect(variantQuestions(hu, 7)).toEqual(variantQuestions(hu, 7));
  });
});

describe("variantCardId", () => {
  it("is unique per unit and index", () => {
    expect(variantCardId("sliding-window", 0)).toBe("dsa-variant:sliding-window:0");
    expect(variantCardId("sliding-window", 1)).not.toBe(variantCardId("sliding-window", 0));
    expect(variantCardId("two-pointers", 0)).not.toBe(variantCardId("sliding-window", 0));
  });
});

function route(unit: string, when: string, notWhen = ""): StageRoute {
  return { when, unit, why: `why ${unit}`, not_when: notWhen };
}

describe("routeHint", () => {
  it("is null when the stage has no routing table", () => {
    // Three units, because a routing question needs at least two distractors.
    const c = hydrate(
      curriculum([
        {
          key: "s1",
          units: [unit("a", "Alpha", ["p1"]), unit("b", "Beta", ["p2"]), unit("c", "Gamma", ["p3"])],
        },
      ]),
      [problem("p1"), problem("p2"), problem("p3")]
    );
    const q = routingQuestion(c.stages[0].units[0], c.stages[0].units, rng(1));
    expect(q).not.toBeNull();
    expect(q!.routeHint).toBeNull();
  });

  it("carries the stage's rule for the answer unit", () => {
    const c = hydrate(
      curriculum([
        {
          key: "s1",
          units: [unit("a", "Alpha", ["p1"]), unit("b", "Beta", ["p2"]), unit("c", "Gamma", ["p3"])],
          router: [route("b", "when the prompt says beta", "not when it says gamma")],
        },
      ]),
      [problem("p1"), problem("p2"), problem("p3")]
    );
    const qs = mixedSet(c, "s1", 5, 6);
    const beta = qs.find((q) => q.answerUnit === "b");
    expect(beta?.routeHint).toEqual({
      when: "when the prompt says beta",
      why: "why b",
      notWhen: "not when it says gamma",
    });
    // A unit the table says nothing about gets no rule rather than someone else's.
    expect(qs.find((q) => q.answerUnit === "a")?.routeHint).toBeNull();
  });

  it("prefers a row that names a near miss", () => {
    const c = hydrate(
      curriculum([
        {
          key: "s1",
          units: [unit("a", "Alpha", ["p1"]), unit("b", "Beta", ["p2"]), unit("c", "Gamma", ["p3"])],
          router: [
            route("b", "plain rule with no near miss"),
            route("b", "rule that names one", "the confusable phrasing"),
          ],
        },
      ]),
      [problem("p1"), problem("p2"), problem("p3")]
    );
    const beta = mixedSet(c, "s1", 5, 6).find((q) => q.answerUnit === "b");
    expect(beta?.routeHint?.when).toBe("rule that names one");
  });

  it("looks the rule up in the stage that owns the unit, not the one being drilled", () => {
    // A mixed set for stage 2 draws from stage 1 as well; a stage-1 question
    // must still get stage 1's rule.
    const c = hydrate(
      curriculum([
        {
          key: "s1",
          units: [unit("a", "Alpha", ["p1"])],
          router: [route("a", "stage one rule")],
        },
        {
          key: "s2",
          units: [unit("b", "Beta", ["p2"]), unit("c", "Gamma", ["p3"])],
          router: [route("b", "stage two rule")],
        },
      ]),
      [problem("p1"), problem("p2"), problem("p3")]
    );
    const qs = mixedSet(c, "s2", 3, 6);
    expect(qs.find((q) => q.answerUnit === "a")?.routeHint?.when).toBe("stage one rule");
    expect(qs.find((q) => q.answerUnit === "b")?.routeHint?.when).toBe("stage two rule");
  });
});
