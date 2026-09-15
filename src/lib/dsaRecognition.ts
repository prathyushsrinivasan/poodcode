import type { Problem } from "../types";
import { isCleared, type HydratedCurriculum, type HydratedUnit } from "./curriculum";

/**
 * Recognition: prompt → technique routing, tested the only way it can be —
 * unlabelled.
 *
 * All the practice in the curriculum is **blocked**: you solve a sliding-window
 * problem on the page titled Sliding Window, having just read the Sliding
 * Window signals table. The Signals tables exist precisely to train prompt →
 * technique routing, and nothing ever tested that routing. It is also the skill
 * that actually fails under interview pressure, because in an interview nobody
 * tells you which chapter the question came from.
 *
 * So: a mixed set per stage, drawn from that stage and every earlier one, with
 * the unit names hidden. Before the editor opens, one question — *which
 * technique does this prompt want?* — with distractors taken from sibling
 * units' own `signals[].reach_for`, so a wrong answer is a plausible wrong
 * answer rather than an obvious one.
 *
 * Recognition and implementation are scored separately because they are
 * different failures. "I knew it was a heap and could not write one" and "I can
 * write a heap and never saw that it was one" want different practice, and a
 * single percentage hides which one you have.
 *
 * Nothing here is authored in the seed: every question is derived from content
 * the units already carry. That is deliberate — a routing question authored by
 * hand would drift from the signals table it is meant to test.
 */

/** Deterministic PRNG, so "today's mixed set" is stable within a session and
 * reproducible in tests. mulberry32. */
export function rng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function shuffled<T>(xs: readonly T[], rand: () => number): T[] {
  const a = [...xs];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/**
 * A unit's answer in a routing question: its **title**.
 *
 * The roadmap proposed drawing option labels from sibling units'
 * `signals[].reach_for`, on the reasoning that the signals table is what trained
 * the routing. Against the real content that produces unusable options — the
 * cells are written to sit in a table row next to their `when`, so they come out
 * as `` `long` ``, "Two passes", "O(n²) is fine", "Heap over per-user lists" —
 * and, fatally, they collide: both `graph-traversal` and `shortest-paths` would
 * answer "BFS", making the question unanswerable.
 *
 * Unit titles are the technique names ("Sliding Window", "Union-Find", "Heaps &
 * Priority Queues") and are unique by construction — the generator lints for it.
 * The signals table still does its job, via `RoutingQuestion.signalHint`: it is
 * shown *after* the answer, as the giveaway you should have spotted, which is
 * the loop the drill exists to close.
 */
export function techniqueLabel(u: HydratedUnit): string {
  return u.unit.title;
}

export interface RoutingQuestion {
  /** The problem whose statement is the prompt. */
  problem: Problem;
  /** Key of the unit that really teaches it. */
  answerUnit: string;
  /** Option labels, shuffled; exactly one matches `answerLabel`. */
  options: string[];
  answerLabel: string;
  /**
   * One row of the answer unit's signals table, revealed after answering —
   * "when the prompt says X, reach for Y". This is what makes the drill teach
   * rather than merely score: a missed routing question should send you back to
   * the wording you failed to notice.
   */
  signalHint: { when: string; reachFor: string } | null;
}

/** Stable card id for a unit's routing score, graded like a self-check.
 *
 * Kept in the same `card_reviews` table as the checks so recognition decays on
 * its own schedule — knowing that "contiguous subarray" means sliding window is
 * a memory like any other, and it is the first one to go. */
export function routeCardId(unitKey: string): string {
  return `dsa-route:${unitKey}`;
}

/**
 * Build one routing question for `target`, with distractors from `pool`.
 *
 * Distractors are drawn from *sibling* units — units the learner has already
 * met — so the question tests discrimination between things they know, not
 * recall of a name they have never seen. Returns null when there is no problem
 * to ask about or fewer than two plausible distractors, because a two-option
 * routing question is a coin toss.
 */
export function routingQuestion(
  target: HydratedUnit,
  pool: HydratedUnit[],
  rand: () => number,
  /** Restrict to problems the learner has not solved, when any remain. */
  preferUnsolved = true
): RoutingQuestion | null {
  const items = target.rungs.flatMap((r) => r.items).filter((i) => i.problem);
  if (items.length === 0) return null;
  const unsolved = items.filter((i) => i.problem!.solved_status !== "solved");
  const from = preferUnsolved && unsolved.length > 0 ? unsolved : items;
  const problem = from[Math.floor(rand() * from.length)].problem!;

  const answerLabel = techniqueLabel(target);
  const distractors: string[] = [];
  for (const u of shuffled(pool, rand)) {
    if (u.unit.key === target.unit.key) continue;
    const label = techniqueLabel(u);
    if (label === answerLabel || distractors.includes(label)) continue;
    distractors.push(label);
    if (distractors.length === 3) break;
  }
  if (distractors.length < 2) return null;

  const signals = target.unit.signals.filter((s) => s.when.trim() && s.reach_for.trim());
  const sig = signals.length > 0 ? signals[Math.floor(rand() * signals.length)] : null;

  return {
    problem,
    answerUnit: target.unit.key,
    answerLabel,
    options: shuffled([answerLabel, ...distractors], rand),
    signalHint: sig ? { when: sig.when, reachFor: sig.reach_for } : null,
  };
}

/**
 * The mixed set for a stage: unlabelled problems from this stage and every
 * earlier one.
 *
 * Earlier stages are included on purpose. A set drawn from one stage still
 * tells you which five techniques are in play, which is most of the routing
 * answer given away for free — and interleaving across everything learned so
 * far is the whole reason the set exists.
 */
export function mixedSet(
  c: HydratedCurriculum,
  stageKey: string,
  seed: number,
  size = 6
): RoutingQuestion[] {
  const stageIndex = c.stages.findIndex((s) => s.key === stageKey);
  if (stageIndex < 0) return [];
  const pool = c.stages
    .slice(0, stageIndex + 1)
    .flatMap((s) => s.units)
    // A unit with no rungs resolved to real problems cannot contribute a prompt.
    .filter((u) => u.total > 0 || u.rungs.some((r) => r.items.some((i) => i.problem)));
  if (pool.length === 0) return [];

  const rand = rng(seed);
  const out: RoutingQuestion[] = [];
  const used = new Set<string>();
  for (const u of shuffled(pool, rand)) {
    if (out.length >= size) break;
    const q = routingQuestion(u, pool, rand);
    if (!q || used.has(q.problem.slug)) continue;
    used.add(q.problem.slug);
    out.push(q);
  }
  return out;
}

export interface PlacementStage {
  stageKey: string;
  stageTitle: string;
  stageIcon: string;
  /** One routing question — can you name the technique? */
  question: RoutingQuestion | null;
  /** One representative problem — can you write it? */
  problem: Problem | null;
  /** Every unit the stage would mark known if you clear it. */
  unitKeys: string[];
  /** Already cleared (earned or marked known), so there is nothing to place. */
  alreadyCleared: boolean;
}

/**
 * The placement diagnostic, per stage.
 *
 * The course starts at `System.out.println` for everyone, which is right as a
 * default and wrong as the only option: units open regardless of readiness, but
 * there was no honest way to *skip*. Clearing a stage's diagnostic marks its
 * units known (the B4 mechanism), so an experienced learner lands in `heaps`
 * rather than scrolling past four Intro units.
 *
 * One routing question and one representative problem, because those are the
 * two failures worth ruling out. The representative problem is the hardest one
 * on the stage's last unit's core rungs — passing a warm-up proves nothing.
 */
export function placement(c: HydratedCurriculum, seed: number): PlacementStage[] {
  const rand = rng(seed);
  // Distractors come from the WHOLE curriculum here, unlike the mixed set.
  // Someone taking placement is claiming prior knowledge, so restricting the
  // options to techniques the *course* has reached would both be unfair (they
  // may well know all of them) and less discriminating — and for stage 1 it
  // leaves too few siblings to build a question from at all.
  const everything = c.stages.flatMap((s) => s.units);
  return c.stages.map((stage) => {
    const units = stage.units;
    const last = units[units.length - 1];
    const q = last ? routingQuestion(last, everything, rand, false) : null;

    const candidates = units
      .flatMap((u) => u.rungs.filter((r) => !r.optional).flatMap((r) => r.items))
      .map((i) => i.problem)
      .filter((p): p is Problem => p !== null);
    const rank: Record<string, number> = { Intro: 0, Easy: 1, Medium: 2, Hard: 3 };
    // Hardest, but not the Hard outlier: a stage's stretch problem is not what
    // "you can skip this stage" should hinge on.
    const sorted = [...candidates].sort((a, b) => rank[a.difficulty] - rank[b.difficulty]);
    const representative =
      sorted.filter((p) => p.difficulty !== "Hard").slice(-1)[0] ?? sorted.slice(-1)[0] ?? null;

    return {
      stageKey: stage.key,
      stageTitle: stage.title,
      stageIcon: stage.icon,
      question: q,
      problem: representative,
      unitKeys: units.map((u) => u.unit.key),
      alreadyCleared: units.every((u) => u.skipped || isCleared(u.status)),
    };
  });
}
