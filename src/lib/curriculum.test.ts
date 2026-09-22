import { describe, expect, it } from "vitest";
import {
  findUnit,
  hydrate,
  isCleared,
  neighbours,
  parseSkipped,
  searchUnits,
  serialiseSkipped,
} from "./curriculum";
import type { CurriculumUnit, DsaCurriculum, Problem, Rung, SolvedStatus } from "../types";

function problem(slug: string, status: SolvedStatus = "unsolved"): Problem {
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
    last_solved_at: null,
    time_taken_seconds: 0,
    attempts_count: 0,
    success_count: 0,
    created_at: "2024-01-01",
    updated_at: "2024-01-01",
  };
}

function rung(title: string, slugs: string[], notes: Record<string, string> = {}): Rung {
  return { title, purpose: `do ${title}`, slugs, notes, optional: false };
}

function extra(title: string, slugs: string[]): Rung {
  return { title, purpose: `do ${title}`, slugs, notes: {}, optional: true };
}

function unit(key: string, rungs: Rung[], prereqs: string[] = []): CurriculumUnit {
  return {
    key,
    title: `Unit ${key}`,
    icon: "🔧",
    stage: "s1",
    tagline: `about ${key}`,
    weight: 2,
    prereqs,
    why: "why",
    model: "model",
    internals: "",
    signals: [],
    skeletons: [],
    traces: [],
    costs: [],
    pitfalls: [],
    lessons: [],
    checks: [],
    bigo: [],
    interview: "",
    rungs,
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

function curriculum(units: CurriculumUnit[][]): DsaCurriculum {
  return {
    key: "dsa",
    title: "DSA Curriculum",
    subtitle: "sub",
    intro: "intro",
    stages: units.map((us, i) => ({
      key: `s${i + 1}`,
      title: `Stage ${i + 1}`,
      icon: "🌱",
      tagline: "",
      goal: "",
      ordering: i,
      router: [],
      units: us,
    })),
  };
}

describe("hydrate", () => {
  it("joins slugs to problems and counts only the ones that resolve", () => {
    const c = curriculum([[unit("a", [rung("Core", ["x", "y", "ghost"])])]]);
    const h = hydrate(c, [problem("x", "solved"), problem("y")]);

    const u = h.stages[0].units[0];
    expect(u.total).toBe(2); // "ghost" is not in the bank and is not counted
    expect(u.solved).toBe(1);
    expect(u.rungs[0].items.map((i) => i.slug)).toEqual(["x", "y", "ghost"]);
    expect(u.rungs[0].items[2].problem).toBeNull();
  });

  it("carries the authored per-problem note through to the rung item", () => {
    const c = curriculum([[unit("a", [rung("Core", ["x"], { x: "start here" })])]]);
    const h = hydrate(c, [problem("x")]);
    expect(h.stages[0].units[0].rungs[0].items[0].note).toBe("start here");
    expect(h.stages[0].units[0].rungs[0].items[0]).toMatchObject({ slug: "x" });
  });

  it("derives unit status from solved counts", () => {
    const slugs = ["a", "b", "c", "d", "e"];
    const c = curriculum([[unit("u", [rung("Core", slugs)])]]);

    const status = (solvedCount: number) =>
      hydrate(
        c,
        slugs.map((s, i) => problem(s, i < solvedCount ? "solved" : "unsolved"))
      ).stages[0].units[0].status;

    expect(status(0)).toBe("new");
    expect(status(1)).toBe("started");
    expect(status(2)).toBe("started"); // below the 60% bar
    expect(status(3)).toBe("solid"); // ceil(5 * 0.6) === 3
    expect(status(5)).toBe("complete");
  });

  it("treats an attempted-but-unsolved problem as having started the unit", () => {
    const c = curriculum([[unit("u", [rung("Core", ["a", "b"])])]]);
    const h = hydrate(c, [problem("a", "attempted"), problem("b")]);
    expect(h.stages[0].units[0].status).toBe("started");
    expect(h.stages[0].units[0].attempted).toBe(1);
    expect(h.stages[0].units[0].solved).toBe(0);
  });

  it("picks the next problem by walking the rungs in order", () => {
    const c = curriculum([
      [unit("u", [rung("Warm up", ["a"]), rung("Core", ["b", "c"])])],
    ]);
    const h = hydrate(c, [problem("a", "solved"), problem("b"), problem("c")]);
    expect(h.stages[0].units[0].next?.slug).toBe("b");
  });

  it("prefers an attempted problem over an earlier untouched one", () => {
    // A problem you fought with yesterday and one you have never opened are not
    // interchangeable: the attempted one still has your context loaded.
    const c = curriculum([[unit("u", [rung("Core", ["a", "b", "c"])])]]);
    const h = hydrate(c, [problem("a"), problem("b", "attempted"), problem("c")]);
    expect(h.stages[0].units[0].next?.slug).toBe("b");
  });

  it("falls back to the first untouched problem when nothing is attempted", () => {
    const c = curriculum([[unit("u", [rung("Core", ["a", "b"])])]]);
    const h = hydrate(c, [problem("a"), problem("b")]);
    expect(h.stages[0].units[0].next?.slug).toBe("a");
  });

  it("reports the difficulty mix and a rough time, over required rungs only", () => {
    const c = curriculum([
      [unit("u", [rung("Core", ["easy", "med"]), extra("Extra practice", ["hard"])])],
    ]);
    const h = hydrate(c, [
      { ...problem("easy"), difficulty: "Easy" as const },
      { ...problem("med"), difficulty: "Medium" as const },
      { ...problem("hard"), difficulty: "Hard" as const },
    ]);
    const u = h.stages[0].units[0];

    expect(u.mix).toEqual({ Intro: 0, Easy: 1, Medium: 1, Hard: 0 });
    expect(u.estimatedMinutes).toBe(32); // 10 + 22; the optional Hard is not asked
  });

  it("counts an optional rung into the mix once it is started", () => {
    const c = curriculum([
      [unit("u", [rung("Core", ["easy"]), extra("Extra practice", ["hard"])])],
    ]);
    const h = hydrate(c, [
      { ...problem("easy"), difficulty: "Easy" as const },
      { ...problem("hard", "solved"), difficulty: "Hard" as const },
    ]);
    expect(h.stages[0].units[0].mix).toEqual({ Intro: 0, Easy: 1, Medium: 0, Hard: 1 });
  });

  it("marks a unit ready only once every prerequisite is cleared", () => {
    const c = curriculum([
      [unit("basics", [rung("Core", ["a", "b"])]), unit("next", [rung("Core", ["c"])], ["basics"])],
    ]);

    const unready = hydrate(c, [problem("a"), problem("b"), problem("c")]);
    expect(findUnit(unready, "next")!.ready).toBe(false);

    const ready = hydrate(c, [problem("a", "solved"), problem("b", "solved"), problem("c")]);
    expect(findUnit(ready, "next")!.ready).toBe(true);
  });

  it("leaves an untouched optional rung out of the unit's totals", () => {
    const c = curriculum([[unit("u", [rung("Core", ["a", "b"]), extra("Extra practice", ["c", "d"])])]]);
    const h = hydrate(c, [problem("a", "solved"), problem("b"), problem("c"), problem("d")]);
    const u = h.stages[0].units[0];

    expect(u.total).toBe(2); // the optional rung is not asked of you
    expect(u.solved).toBe(1);
    expect(u.rungs[1].counted).toBe(false);
    expect(u.rungs[1].total).toBe(2); // the rung still reports its own size
  });

  it("counts an optional rung once you have started it", () => {
    const c = curriculum([[unit("u", [rung("Core", ["a", "b"]), extra("Extra practice", ["c", "d"])])]]);
    const h = hydrate(c, [
      problem("a", "solved"),
      problem("b", "solved"),
      problem("c", "solved"),
      problem("d"),
    ]);
    const u = h.stages[0].units[0];

    expect(u.rungs[1].counted).toBe(true);
    expect(u.total).toBe(4);
    expect(u.solved).toBe(3);
  });

  it("never points `next` at an optional rung you have not started", () => {
    const c = curriculum([[unit("u", [rung("Core", ["a"]), extra("Extra practice", ["b"])])]]);
    const solvedCore = hydrate(c, [problem("a", "solved"), problem("b")]);
    expect(solvedCore.stages[0].units[0].next).toBeNull();
    // …and the unit reads as complete, because the optional rung is not asked.
    expect(solvedCore.stages[0].units[0].status).toBe("complete");
  });

  it("names only the prerequisites that are actually unmet", () => {
    // Prereqs are a graph, not a chain, so a unit can name two and have
    // cleared one. Saying "builds on A, B, which you have not finished" would
    // then be false about A — the banner reads `unmetPrereqTitles`.
    const c = curriculum([
      [
        unit("hashing", [rung("Core", ["a"])]),
        unit("trees", [rung("Core", ["b"])]),
        unit("tries", [rung("Core", ["c"])], ["hashing", "trees"]),
      ],
    ]);
    const h = hydrate(c, [problem("a", "solved"), problem("b"), problem("c")]);
    const tries = findUnit(h, "tries")!;

    expect(tries.ready).toBe(false);
    expect(tries.prereqTitles).toEqual(["Unit hashing", "Unit trees"]);
    expect(tries.unmetPrereqTitles).toEqual(["Unit trees"]);
  });

  it("reports no unmet prerequisites once every one is cleared", () => {
    const c = curriculum([
      [
        unit("hashing", [rung("Core", ["a"])]),
        unit("trees", [rung("Core", ["b"])]),
        unit("tries", [rung("Core", ["c"])], ["hashing", "trees"]),
      ],
    ]);
    const h = hydrate(c, [problem("a", "solved"), problem("b", "solved"), problem("c")]);
    expect(findUnit(h, "tries")!.unmetPrereqTitles).toEqual([]);
    expect(findUnit(h, "tries")!.ready).toBe(true);
  });

  it("continues at the first unfinished unit whose prerequisites are met", () => {
    const c = curriculum([
      [
        unit("one", [rung("Core", ["a"])]),
        unit("two", [rung("Core", ["b"])], ["one"]),
        unit("three", [rung("Core", ["c"])], ["two"]),
      ],
    ]);
    const h = hydrate(c, [problem("a", "solved"), problem("b"), problem("c")]);
    expect(h.next?.unit.unit.key).toBe("two");
    expect(h.next?.problem?.slug).toBe("b");
  });

  it("falls back to an unready unit rather than losing the Continue target", () => {
    // "two" is unfinished but not ready, and nothing else is left to do.
    const c = curriculum([
      [unit("one", [rung("Core", ["a"])]), unit("two", [rung("Core", ["b"])], ["one"])],
    ]);
    const h = hydrate(c, [problem("a"), problem("b")]);
    expect(h.next?.unit.unit.key).toBe("one");
  });

  it("returns no Continue target once everything is solved", () => {
    const c = curriculum([[unit("one", [rung("Core", ["a"])])]]);
    expect(hydrate(c, [problem("a", "solved")]).next).toBeNull();
  });

  it("reports problems that no unit schedules, so Browse can surface them", () => {
    const c = curriculum([[unit("one", [rung("Core", ["a"])])]]);
    const h = hydrate(c, [problem("a"), problem("mine")]);
    expect(h.unplaced.map((p) => p.slug)).toEqual(["mine"]);
    expect(h.unitBySlug.get("a")?.key).toBe("one");
    expect(h.unitBySlug.has("mine")).toBe(false);
  });

  it("totals a stage and the whole curriculum from its units", () => {
    const c = curriculum([
      [unit("one", [rung("Core", ["a", "b"])])],
      [unit("two", [rung("Core", ["c"])])],
    ]);
    const h = hydrate(c, [problem("a", "solved"), problem("b"), problem("c", "solved")]);
    expect(h.stages[0]).toMatchObject({ solved: 1, total: 2 });
    expect(h.stages[1]).toMatchObject({ solved: 1, total: 1 });
    expect(h).toMatchObject({ solved: 2, total: 3 });
  });

  it("leaves an optional stage out of the overall progress", () => {
    const c = curriculum([
      [unit("one", [rung("Core", ["a", "b"])])],
      [unit("extra", [rung("Core", ["c", "d"])])],
    ]);
    c.stages[1].optional = true;
    const h = hydrate(c, [problem("a", "solved"), problem("b"), problem("c", "solved"), problem("d")]);
    expect(h.stages[1]).toMatchObject({ optional: true, solved: 1, total: 2 });
    expect(h).toMatchObject({ solved: 1, total: 2 });
  });

  it("does not send Continue into an optional stage while core work remains", () => {
    // The optional unit is ready and the core one is not — core still wins.
    const c = curriculum([
      [unit("one", [rung("Core", ["a"])]), unit("two", [rung("Core", ["b"])], ["one"])],
      [unit("extra", [rung("Core", ["c"])])],
    ]);
    c.stages[1].optional = true;
    const h = hydrate(c, [problem("a", "solved"), problem("b"), problem("c")]);
    expect(h.next?.unit.unit.key).toBe("two");
    expect(h.coreComplete).toBe(false);
  });

  it("offers the optional stage once the core is complete", () => {
    const c = curriculum([
      [unit("one", [rung("Core", ["a"])])],
      [unit("extra", [rung("Core", ["c"])])],
    ]);
    c.stages[1].optional = true;
    const h = hydrate(c, [problem("a", "solved"), problem("c")]);
    expect(h.coreComplete).toBe(true);
    expect(h.next?.unit.unit.key).toBe("extra");
    expect(hydrate(c, [problem("a", "solved"), problem("c", "solved")]).next).toBeNull();
  });

  it("survives a missing curriculum", () => {
    const h = hydrate(null, [problem("a")]);
    expect(h.stages).toEqual([]);
    expect(h.next).toBeNull();
    expect(h.unplaced).toHaveLength(1);
  });
});

describe("marking a unit known", () => {
  const twoUnits = () =>
    curriculum([
      [unit("heaps", [rung("Core", ["a", "b", "c"])]), unit("later", [rung("Core", ["d"])], ["heaps"])],
    ]);
  const unsolved = () => [problem("a"), problem("b"), problem("c"), problem("d")];

  it("unblocks what depends on it without claiming the problems were solved", () => {
    const h = hydrate(twoUnits(), unsolved(), new Set(["heaps"]));
    const heaps = findUnit(h, "heaps")!;
    const later = findUnit(h, "later")!;

    expect(heaps.skipped).toBe(true);
    expect(heaps.solved).toBe(0); // no progress is invented
    expect(heaps.status).toBe("new");
    expect(later.ready).toBe(true); // …but the prerequisite is satisfied
    expect(later.unmetPrereqTitles).toEqual([]);
  });

  it("is never the Continue target", () => {
    const h = hydrate(twoUnits(), unsolved(), new Set(["heaps"]));
    expect(h.next?.unit.unit.key).toBe("later");
  });

  it("blocks again once un-skipped", () => {
    const h = hydrate(twoUnits(), unsolved(), new Set());
    expect(findUnit(h, "later")!.ready).toBe(false);
    expect(h.next?.unit.unit.key).toBe("heaps");
  });

  it("round-trips through the settings string, sorted and de-duplicated", () => {
    expect(serialiseSkipped(["tries", "heaps", "heaps"])).toBe("heaps,tries");
    expect([...parseSkipped("heaps, tries ,,")]).toEqual(["heaps", "tries"]);
    expect([...parseSkipped(undefined)]).toEqual([]);
    expect([...parseSkipped("")]).toEqual([]);
  });

  it("ignores a skipped key that no longer names a unit", () => {
    const h = hydrate(twoUnits(), unsolved(), new Set(["a-unit-that-was-deleted"]));
    expect(findUnit(h, "later")!.ready).toBe(false);
    expect(h.stages[0].units.every((u) => !u.skipped)).toBe(true);
  });
});

describe("isCleared", () => {
  it("counts solid and complete, and nothing else", () => {
    expect(isCleared("solid")).toBe(true);
    expect(isCleared("complete")).toBe(true);
    expect(isCleared("started")).toBe(false);
    expect(isCleared("new")).toBe(false);
  });
});

describe("neighbours", () => {
  it("pages across stage boundaries", () => {
    const c = curriculum([
      [unit("one", [rung("Core", ["a"])]), unit("two", [rung("Core", ["b"])])],
      [unit("three", [rung("Core", ["c"])])],
    ]);
    const h = hydrate(c, [problem("a"), problem("b"), problem("c")]);

    expect(neighbours(h, "two").prev?.unit.key).toBe("one");
    expect(neighbours(h, "two").next?.unit.key).toBe("three");
    expect(neighbours(h, "one").prev).toBeNull();
    expect(neighbours(h, "three").next).toBeNull();
    expect(neighbours(h, "nope")).toEqual({ prev: null, next: null });
  });
});

describe("searchUnits", () => {
  const withSignals = (): CurriculumUnit => ({
    ...unit("hashing", [rung("Core", ["a"])]),
    internals: "A bucket array; a long chain becomes a tree at load factor 0.75.",
    signals: [{ when: "two numbers that sum to target", reach_for: "complement map", why: "" }],
    pitfalls: [{ symptom: "returns the same index twice", cause: "", fix: "" }],
    skeletons: [{ name: "Seen-set", when: "", code: "", note: "" }],
    traces: [
      { title: "Complement lookup on [2, 7, 11]", intro: "", headers: ["i"], rows: [["0"], ["1"]], takeaway: "" },
    ],
  });

  it("matches on titles, signal wording, pitfall symptoms and skeleton names", () => {
    const h = hydrate(curriculum([[withSignals()]]), [problem("a")]);
    expect(searchUnits(h, "sum to target")).toHaveLength(1);
    expect(searchUnits(h, "same index twice")).toHaveLength(1);
    expect(searchUnits(h, "seen-set")).toHaveLength(1);
    expect(searchUnits(h, "Unit hashing")).toHaveLength(1);
    expect(searchUnits(h, "dijkstra")).toHaveLength(0);
  });

  it("matches on internals prose and trace titles, which is where the nouns are", () => {
    // "load factor" appears nowhere but the internals, and someone who
    // half-remembers the term will type that rather than the unit's title.
    const h = hydrate(curriculum([[withSignals()]]), [problem("a")]);
    expect(searchUnits(h, "load factor")).toHaveLength(1);
    expect(searchUnits(h, "complement lookup on")).toHaveLength(1);
  });

  it("treats a blank query as no search rather than as matching everything", () => {
    const h = hydrate(curriculum([[withSignals()]]), [problem("a")]);
    expect(searchUnits(h, "   ")).toEqual([]);
  });

  it("ranks a title match above an incidental prose match", () => {
    // Searching "stack" used to put the unit that mentions a stack in passing
    // above the unit *called* Stacks, because every field was one haystack and
    // the result order was `filter` order.
    const mentions: CurriculumUnit = {
      ...unit("recursion", [rung("Core", ["b"])]),
      model: "Every recursive call pushes a frame onto the call stack.",
    };
    const named: CurriculumUnit = { ...unit("stacks", [rung("Core", ["a"])]) };
    named.title = "Stacks";

    const h = hydrate(curriculum([[mentions, named]]), [problem("a"), problem("b")]);
    const hits = searchUnits(h, "stack");

    expect(hits.map((m) => m.unit.unit.key)).toEqual(["stacks", "recursion"]);
    expect(hits[0].field).toBe("title");
    expect(hits[1].field).toBe("prose");
  });

  it("reports which field matched, and the line that did", () => {
    const h = hydrate(curriculum([[withSignals()]]), [problem("a")]);
    const [hit] = searchUnits(h, "same index twice");

    expect(hit.field).toBe("pitfall");
    expect(hit.label).toBe("pitfall");
    expect(hit.snippet).toContain("returns the same index twice");
  });

  it("searches the fields that were previously invisible", () => {
    // "load factor" lives in internals, "amortised" in the cost table and
    // "identity element" in a self-check — none of the last two were searchable.
    const u: CurriculumUnit = {
      ...unit("hashing", [rung("Core", ["a"], { a: "the complement trick, twice" })]),
      costs: [{ op: "insert", time: "O(1) amortised", space: "O(n)", note: "" }],
      checks: [{ q: "Why initialise a product to 1?", a: "It is the identity element." }],
      build_it: "Write the bucket array yourself.",
    };
    const h = hydrate(curriculum([[u]]), [problem("a")]);

    expect(searchUnits(h, "amortised")[0].field).toBe("cost");
    expect(searchUnits(h, "identity element")[0].field).toBe("check");
    expect(searchUnits(h, "bucket array")[0].field).toBe("prose");
    expect(searchUnits(h, "complement trick")[0].field).toBe("problem");
  });

  it("reports each unit once, by its most meaningful match", () => {
    const u: CurriculumUnit = {
      ...unit("maps", [rung("Core", ["a"])]),
      // Two pitfalls and the prose all mention it; only the best field is
      // reported, so the result list has one row per unit rather than per hit.
      pitfalls: [
        { symptom: "hash collision", cause: "", fix: "" },
        { symptom: "hash mismatch", cause: "", fix: "" },
      ],
      model: "A hash is a number.",
    };
    const h = hydrate(curriculum([[u]]), [problem("a")]);
    const hits = searchUnits(h, "hash");
    expect(hits).toHaveLength(1);
    expect(hits[0].field).toBe("pitfall");
  });
});
