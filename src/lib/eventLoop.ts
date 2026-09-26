// A step-by-step model of the JavaScript event loop (TS_MASTERY_ROADMAP
// M6-01): the call stack, the microtask queue, the task (timer) queue and the
// output, for small scenarios.
//
// Each scenario carries the JavaScript it shows AND a structured program the
// simulator runs. The two are kept honest by eventLoop.test.ts, which executes
// the real JavaScript and requires the simulator to print exactly what the
// engine printed — so a scenario cannot teach an order that is not real.

export type Op =
  | { op: "log"; text: string; line: number }
  /** A synchronous call: a frame is pushed, the body runs, the frame pops. */
  | { op: "call"; name: string; line: number; body: Op[] }
  /** setTimeout: a task due `ms` later (Node treats 0 as 1). */
  | { op: "timeout"; ms: number; label: string; line: number; body: Op[] }
  /** A microtask: a `.then` callback, `queueMicrotask`, or the rest of an
   * async function after an `await` (the function returns at the await). */
  | { op: "microtask"; how: "then" | "queueMicrotask" | "await"; label: string; line: number; body: Op[] };

export type Scenario = {
  key: string;
  title: string;
  lesson: string;
  code: string;
  program: Op[];
};

export type Step = {
  stack: string[];
  microtasks: string[];
  tasks: { label: string; due: number }[];
  output: string[];
  /** The line of `code` being executed, if any. */
  line: number | null;
  note: string;
  clock: number;
};

type Queued = { label: string; body: Op[]; line: number };
type Timer = Queued & { due: number; seq: number };

export function simulate(program: Op[]): Step[] {
  const steps: Step[] = [];
  const stack: string[] = [];
  const micro: Queued[] = [];
  const timers: Timer[] = [];
  const output: string[] = [];
  let clock = 0;
  let seq = 0;

  const sortedTimers = () => [...timers].sort((a, b) => a.due - b.due || a.seq - b.seq);
  const record = (line: number | null, note: string) =>
    steps.push({
      stack: [...stack],
      microtasks: micro.map((m) => m.label),
      tasks: sortedTimers().map((t) => ({ label: t.label, due: t.due })),
      output: [...output],
      line,
      note,
      clock,
    });

  const run = (ops: Op[]) => {
    for (const op of ops) {
      switch (op.op) {
        case "log":
          output.push(op.text);
          record(op.line, `console.log prints "${op.text}".`);
          break;
        case "call":
          stack.push(`${op.name}()`);
          record(op.line, `${op.name}() is called — a new frame goes on the call stack.`);
          run(op.body);
          stack.pop();
          record(op.line, `${op.name}() returns and its frame is popped.`);
          break;
        case "timeout": {
          const due = clock + Math.max(1, op.ms);
          timers.push({ label: op.label, body: op.body, line: op.line, due, seq: seq++ });
          record(op.line, `setTimeout(…, ${op.ms}) queues a task, due at ${due} ms. Nothing runs yet.`);
          break;
        }
        case "microtask":
          micro.push({ label: op.label, body: op.body, line: op.line });
          record(
            op.line,
            op.how === "then"
              ? "The promise is settled, so its .then callback is queued as a microtask."
              : op.how === "await"
                ? "await pauses the function; the rest of it is queued as a microtask and the caller continues."
                : "queueMicrotask queues a microtask."
          );
          break;
      }
    }
  };

  stack.push("(script)");
  record(null, "The script starts: its top level runs as the first task.");
  run(program);
  stack.pop();
  record(null, "The script has finished and the call stack is empty.");

  for (;;) {
    if (micro.length > 0) {
      record(null, `The stack is empty, so every microtask runs before any other task (${micro.length} queued).`);
      while (micro.length > 0) {
        const m = micro.shift()!;
        stack.push(m.label);
        record(m.line, `Microtask: ${m.label}.`);
        run(m.body);
        stack.pop();
      }
      record(null, "The microtask queue is empty.");
    }
    const next = sortedTimers()[0];
    if (!next) break;
    timers.splice(timers.indexOf(next), 1);
    clock = Math.max(clock, next.due);
    stack.push(next.label);
    record(next.line, `The event loop takes the next task: ${next.label} (due at ${next.due} ms).`);
    run(next.body);
    stack.pop();
  }
  record(null, "Nothing is left to run — the program exits.");
  return steps;
}

export const SCENARIOS: Scenario[] = [
  {
    key: "basics",
    title: "Sync, then microtasks, then timers",
    lesson:
      "Synchronous code always finishes first. Then every queued microtask runs. Only then does the event loop take a timer — even one set for 0 ms.",
    code: `console.log("script start");
setTimeout(() => console.log("timeout"), 0);
Promise.resolve().then(() => console.log("promise then"));
queueMicrotask(() => console.log("microtask"));
console.log("script end");`,
    program: [
      { op: "log", text: "script start", line: 1 },
      { op: "timeout", ms: 0, label: "timeout callback", line: 2, body: [{ op: "log", text: "timeout", line: 2 }] },
      { op: "microtask", how: "then", label: "then callback", line: 3, body: [{ op: "log", text: "promise then", line: 3 }] },
      { op: "microtask", how: "queueMicrotask", label: "queueMicrotask callback", line: 4, body: [{ op: "log", text: "microtask", line: 4 }] },
      { op: "log", text: "script end", line: 5 },
    ],
  },
  {
    key: "nested",
    title: "Microtasks queued by microtasks",
    lesson:
      "A microtask that queues another microtask does not let the timer in first: the queue drains completely — including what was added while draining — before the next task.",
    code: `setTimeout(() => console.log("timeout"), 0);
Promise.resolve()
  .then(() => {
    console.log("then 1");
    queueMicrotask(() => console.log("nested microtask"));
  })
  .then(() => console.log("then 2"));
console.log("sync");`,
    program: [
      { op: "timeout", ms: 0, label: "timeout callback", line: 1, body: [{ op: "log", text: "timeout", line: 1 }] },
      {
        op: "microtask",
        how: "then",
        label: "then 1 callback",
        line: 3,
        body: [
          { op: "log", text: "then 1", line: 4 },
          { op: "microtask", how: "queueMicrotask", label: "nested microtask", line: 5, body: [{ op: "log", text: "nested microtask", line: 5 }] },
          { op: "microtask", how: "then", label: "then 2 callback", line: 7, body: [{ op: "log", text: "then 2", line: 7 }] },
        ],
      },
      { op: "log", text: "sync", line: 8 },
    ],
  },
  {
    key: "await",
    title: "await splits a function in two",
    lesson:
      "Everything before the first await runs synchronously, inside the caller. At the await the function returns a promise, and its caller carries on; the rest of the function is a microtask.",
    code: `async function load() {
  console.log("load: start");
  await null;
  console.log("load: after await");
}
console.log("before");
load();
console.log("after");`,
    program: [
      { op: "log", text: "before", line: 6 },
      {
        op: "call",
        name: "load",
        line: 7,
        body: [
          { op: "log", text: "load: start", line: 2 },
          { op: "microtask", how: "await", label: "load() resumes after await", line: 3, body: [{ op: "log", text: "load: after await", line: 4 }] },
        ],
      },
      { op: "log", text: "after", line: 8 },
    ],
  },
  {
    key: "timers",
    title: "Timers run by due time",
    lesson:
      "Tasks from setTimeout run in order of when they are due, and timers due at the same moment run in the order they were set. The order they are written in does not matter.",
    code: `setTimeout(() => console.log("30 ms"), 30);
setTimeout(() => console.log("0 ms"), 0);
setTimeout(() => console.log("10 ms"), 10);
setTimeout(() => console.log("0 ms, set later"), 0);`,
    program: [
      { op: "timeout", ms: 30, label: "30 ms callback", line: 1, body: [{ op: "log", text: "30 ms", line: 1 }] },
      { op: "timeout", ms: 0, label: "0 ms callback", line: 2, body: [{ op: "log", text: "0 ms", line: 2 }] },
      { op: "timeout", ms: 10, label: "10 ms callback", line: 3, body: [{ op: "log", text: "10 ms", line: 3 }] },
      { op: "timeout", ms: 0, label: "second 0 ms callback", line: 4, body: [{ op: "log", text: "0 ms, set later", line: 4 }] },
    ],
  },
  {
    key: "between-timers",
    title: "Microtasks run between two timers",
    lesson:
      "After every task — including each timer callback — the microtask queue drains. A promise settled inside the first timer runs before the second timer, even though both timers were due together.",
    code: `setTimeout(() => {
  console.log("timer 1");
  Promise.resolve().then(() => console.log("microtask from timer 1"));
}, 0);
setTimeout(() => console.log("timer 2"), 0);`,
    program: [
      {
        op: "timeout",
        ms: 0,
        label: "timer 1 callback",
        line: 1,
        body: [
          { op: "log", text: "timer 1", line: 2 },
          { op: "microtask", how: "then", label: "then callback (from timer 1)", line: 3, body: [{ op: "log", text: "microtask from timer 1", line: 3 }] },
        ],
      },
      { op: "timeout", ms: 0, label: "timer 2 callback", line: 5, body: [{ op: "log", text: "timer 2", line: 5 }] },
    ],
  },
  {
    key: "foreach",
    title: "An async callback in forEach",
    lesson:
      "forEach calls each callback and ignores the promise it returns. Both callbacks pause at their await, the loop finishes, and the line after it runs before any save completes.",
    code: `async function save(id) {
  await null;
  console.log("saved " + id);
}
[1, 2].forEach(async (id) => {
  await save(id);
});
console.log("all saved?");`,
    program: [
      {
        op: "call",
        name: "forEach",
        line: 5,
        body: [
          {
            op: "call",
            name: "callback(1)",
            line: 5,
            body: [
              {
                op: "call",
                name: "save(1)",
                line: 6,
                body: [
                  {
                    op: "microtask",
                    how: "await",
                    label: "save(1) resumes",
                    line: 2,
                    body: [
                      { op: "log", text: "saved 1", line: 3 },
                      { op: "microtask", how: "then", label: "callback(1) resumes — save(1) settled", line: 6, body: [] },
                    ],
                  },
                ],
              },
            ],
          },
          {
            op: "call",
            name: "callback(2)",
            line: 5,
            body: [
              {
                op: "call",
                name: "save(2)",
                line: 6,
                body: [
                  {
                    op: "microtask",
                    how: "await",
                    label: "save(2) resumes",
                    line: 2,
                    body: [
                      { op: "log", text: "saved 2", line: 3 },
                      { op: "microtask", how: "then", label: "callback(2) resumes — save(2) settled", line: 6, body: [] },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
      { op: "log", text: "all saved?", line: 8 },
    ],
  },
];

// ---------------------------------------------------------------------------
// Promise combinators on a timeline (M6-02)
// ---------------------------------------------------------------------------

export type Combinator = "all" | "allSettled" | "race" | "any";
export type TimedPromise = { label: string; ms: number; ok: boolean };
export type Settlement = {
  /** When the combinator's promise settles; null if it never does. */
  at: number | null;
  outcome: "fulfilled" | "rejected" | "pending";
  /** What it settles with, described. */
  value: string;
};

const result = (p: TimedPromise) => (p.ok ? `"${p.label}"` : `Error(${p.label})`);

export function settle(combinator: Combinator, items: TimedPromise[]): Settlement {
  // Earliest first; ties keep array order (Array.prototype.sort is stable).
  const order = [...items].sort((a, b) => a.ms - b.ms);
  const firstOk = order.find((p) => p.ok);
  const firstFail = order.find((p) => !p.ok);
  const last = order.length ? order[order.length - 1]!.ms : 0;
  switch (combinator) {
    case "all":
      if (firstFail) return { at: firstFail.ms, outcome: "rejected", value: result(firstFail) };
      return { at: last, outcome: "fulfilled", value: `[${items.map(result).join(", ")}]` };
    case "allSettled":
      return {
        at: last,
        outcome: "fulfilled",
        value: `[${items.map((p) => (p.ok ? `fulfilled ${result(p)}` : `rejected ${result(p)}`)).join(", ")}]`,
      };
    case "race": {
      const first = order[0];
      if (!first) return { at: null, outcome: "pending", value: "never settles — nothing to race" };
      return { at: first.ms, outcome: first.ok ? "fulfilled" : "rejected", value: result(first) };
    }
    case "any":
      if (firstOk) return { at: firstOk.ms, outcome: "fulfilled", value: result(firstOk) };
      return { at: last, outcome: "rejected", value: "AggregateError (every promise rejected)" };
  }
}
