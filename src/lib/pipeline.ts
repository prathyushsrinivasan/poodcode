// The array-method pipeline viewer (TS_MASTERY_ROADMAP M2-03): run a chain
// like `.filter(…).map(…).reduce(…)` one call at a time and keep what each
// step produced. The steps are the learner's own JavaScript, evaluated in the
// page — the same code they would write, just with every intermediate shown.

export const PIPE_METHODS = [
  "filter",
  "map",
  "flatMap",
  "reduce",
  "toSorted",
  "sort",
  "toReversed",
  "slice",
  "find",
  "some",
  "every",
] as const;
export type PipeMethod = (typeof PIPE_METHODS)[number];

export type PipeStep = { method: PipeMethod; arg: string };
export type PipeResult = { value: unknown; error?: string; mutatedInput?: boolean };

/** Run each step on the previous step's result. A step that throws, or that is
 * called on something without that method, stops the chain there. */
export function runPipeline(input: unknown, steps: PipeStep[]): PipeResult[] {
  const out: PipeResult[] = [];
  let current: unknown = input;
  for (const step of steps) {
    if (!Array.isArray(current)) {
      out.push({ value: undefined, error: `.${step.method}() needs an array, but the previous step gave ${describe(current)}.` });
      break;
    }
    const before = JSON.stringify(current);
    try {
      // eslint-disable-next-line @typescript-eslint/no-implied-eval
      const fn = new Function("xs", `"use strict"; return xs.${step.method}(${step.arg});`) as (xs: unknown[]) => unknown;
      const arr = current;
      const value = fn(arr);
      out.push({ value, mutatedInput: JSON.stringify(arr) !== before });
      current = value;
    } catch (e) {
      out.push({ value: undefined, error: e instanceof Error ? `${e.name}: ${e.message}` : String(e) });
      break;
    }
  }
  return out;
}

export function describe(v: unknown): string {
  if (v === undefined) return "undefined";
  try {
    return JSON.stringify(v) ?? String(v);
  } catch {
    return String(v);
  }
}

export type PipePreset = { title: string; lesson: string; input: string; steps: PipeStep[] };

export const PIPE_PRESETS: PipePreset[] = [
  {
    title: "Evens, squared, summed",
    lesson: "filter keeps some elements, map transforms each, reduce folds the array into one value.",
    input: "[3, 8, 1, 6, 5, 4]",
    steps: [
      { method: "filter", arg: "(x) => x % 2 === 0" },
      { method: "map", arg: "(x) => x * x" },
      { method: "reduce", arg: "(sum, x) => sum + x, 0" },
    ],
  },
  {
    title: "Words to a slug",
    lesson: "flatMap maps and flattens in one step; every step returns a new array, so the chain reads top to bottom.",
    input: '["Hello World", "from TypeScript"]',
    steps: [
      { method: "flatMap", arg: '(s) => s.split(" ")' },
      { method: "map", arg: "(w) => w.toLowerCase()" },
      { method: "filter", arg: "(w) => w.length > 2" },
    ],
  },
  {
    title: "The sort surprise",
    lesson: "With no comparator, sort compares as strings — and it sorts the array in place. toSorted with a comparator does neither.",
    input: "[10, 9, 1, 100]",
    steps: [
      { method: "toSorted", arg: "" },
      { method: "toSorted", arg: "(a, b) => a - b" },
    ],
  },
  {
    title: "map(parseInt)",
    lesson: "map passes (value, index) — so parseInt receives the index as its radix. A wrapper that takes one argument fixes it.",
    input: '["1", "2", "3", "10"]',
    steps: [
      { method: "map", arg: "parseInt" },
    ],
  },
];
