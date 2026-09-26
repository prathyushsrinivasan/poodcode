// A step-by-step view of the call stack for recursion and closures
// (TS_MASTERY_ROADMAP M2-02).
//
// Each scenario shows plain JavaScript and carries an instrumented twin that
// reports every call, assignment, print and return to a tracer. The tracer
// turns those into steps — the frames on the stack with their locals, and the
// output so far. callStack.test.ts runs the plain code for real and requires
// the twin to print the same thing, so the two cannot drift apart.

export type Frame = { name: string; locals: [string, string][] };

export type StackStep = {
  frames: Frame[];
  output: string[];
  line: number | null;
  note: string;
  /** Values captured by closures that outlive their frames. */
  captured: [string, string][];
};

export class Tracer {
  steps: StackStep[] = [];
  private frames: Frame[] = [];
  private output: string[] = [];
  private captured = new Map<string, string>();

  private record(line: number | null, note: string) {
    this.steps.push({
      frames: this.frames.map((f) => ({ name: f.name, locals: f.locals.map(([k, v]) => [k, v] as [string, string]) })),
      output: [...this.output],
      line,
      note,
      captured: [...this.captured.entries()],
    });
  }

  start(note = "The program starts.") {
    this.frames.push({ name: "(script)", locals: [] });
    this.record(null, note);
  }

  call(name: string, args: [string, unknown][], line: number) {
    this.frames.push({ name, locals: args.map(([k, v]) => [k, show(v)]) });
    this.record(line, `${name} is called — a new frame with ${args.length ? args.map(([k, v]) => `${k} = ${show(v)}`).join(", ") : "no arguments"}.`);
  }

  set(name: string, value: unknown, line: number, note?: string) {
    const top = this.frames[this.frames.length - 1]!;
    const i = top.locals.findIndex(([k]) => k === name);
    if (i >= 0) top.locals[i] = [name, show(value)];
    else top.locals.push([name, show(value)]);
    this.record(line, note ?? `${name} = ${show(value)}.`);
  }

  capture(name: string, value: unknown, line: number, note: string) {
    this.captured.set(name, show(value));
    this.record(line, note);
  }

  log(text: string, line: number) {
    this.output.push(text);
    this.record(line, `console.log prints "${text}".`);
  }

  ret<T>(value: T, line: number, note?: string): T {
    const f = this.frames.pop()!;
    this.record(line, note ?? `${f.name} returns ${show(value)} and its frame is popped.`);
    return value;
  }

  end() {
    this.frames.pop();
    this.record(null, "The program is done — the stack is empty.");
  }
}

function show(v: unknown): string {
  if (typeof v === "string") return JSON.stringify(v);
  if (typeof v === "function") return "ƒ";
  if (Array.isArray(v)) return `[${v.map(show).join(", ")}]`;
  return String(v);
}

export type StackScenario = {
  key: string;
  title: string;
  lesson: string;
  code: string;
  run: (t: Tracer) => void;
};

export const STACK_SCENARIOS: StackScenario[] = [
  {
    key: "factorial",
    title: "Recursion: factorial",
    lesson:
      "Each call waits on the stack for the one it made. The base case is the first to return; then the frames unwind, each finishing its multiplication.",
    code: `function factorial(n) {
  if (n <= 1) return 1;
  const rest = factorial(n - 1);
  return n * rest;
}
console.log(factorial(4));`,
    run: (t) => {
      t.start();
      const factorial = (n: number): number => {
        t.call(`factorial(${n})`, [["n", n]], 1);
        if (n <= 1) return t.ret(1, 2, `n <= 1 — the base case returns 1 without another call.`);
        const rest = factorial(n - 1);
        t.set("rest", rest, 3, `factorial(${n - 1}) came back with ${rest}.`);
        return t.ret(n * rest, 4, `factorial(${n}) returns ${n} × ${rest} = ${n * rest}.`);
      };
      const result = factorial(4);
      t.log(String(result), 6);
      t.end();
    },
  },
  {
    key: "sum-digits",
    title: "Recursion: sum of digits",
    lesson:
      "The recursive call works on a smaller number each time — the last digit is split off with % 10 and the rest with Math.floor(n / 10) — until one digit is left.",
    code: `function sumDigits(n) {
  if (n < 10) return n;
  return (n % 10) + sumDigits(Math.floor(n / 10));
}
console.log(sumDigits(4817));`,
    run: (t) => {
      t.start();
      const sumDigits = (n: number): number => {
        t.call(`sumDigits(${n})`, [["n", n]], 1);
        if (n < 10) return t.ret(n, 2, `One digit left — return ${n}.`);
        t.set("n % 10", n % 10, 3, `Split off the last digit, ${n % 10}, and recurse on ${Math.floor(n / 10)}.`);
        const inner = sumDigits(Math.floor(n / 10));
        return t.ret((n % 10) + inner, 3, `${n % 10} + ${inner} = ${(n % 10) + inner}.`);
      };
      t.log(String(sumDigits(4817)), 5);
      t.end();
    },
  },
  {
    key: "fib",
    title: "Recursion that branches: fib",
    lesson:
      "fib(n) makes two calls, so the same values are computed again and again — fib(2) appears twice below. That repetition is what memoisation removes.",
    code: `function fib(n) {
  if (n < 2) return n;
  return fib(n - 1) + fib(n - 2);
}
console.log(fib(4));`,
    run: (t) => {
      t.start();
      const fib = (n: number): number => {
        t.call(`fib(${n})`, [["n", n]], 1);
        if (n < 2) return t.ret(n, 2, `Base case: fib(${n}) = ${n}.`);
        const a = fib(n - 1);
        t.set("fib(n - 1)", a, 3, `fib(${n - 1}) = ${a}; now the second call, fib(${n - 2}).`);
        const b = fib(n - 2);
        return t.ret(a + b, 3, `fib(${n}) = ${a} + ${b} = ${a + b}.`);
      };
      t.log(String(fib(4)), 5);
      t.end();
    },
  },
  {
    key: "closure",
    title: "Closures: a counter factory",
    lesson:
      "makeCounter's frame is gone once it returns — but the function it returned still sees count. The variable lives on in the closure, and each counter has its own.",
    code: `function makeCounter() {
  let count = 0;
  return () => {
    count += 1;
    return count;
  };
}
const a = makeCounter();
const b = makeCounter();
console.log(a(), a(), b());`,
    run: (t) => {
      t.start();
      let counters = 0;
      const makeCounter = () => {
        const id = counters === 0 ? "a" : "b";
        counters++;
        t.call("makeCounter()", [], 1);
        let count = 0;
        t.set("count", count, 2);
        const inc = () => {
          t.call(`${id}()`, [], 3);
          count += 1;
          t.capture(`${id}'s count`, count, 4, `count += 1 — this changes the captured count of counter ${id}, now ${count}.`);
          return t.ret(count, 5);
        };
        t.capture(`${id}'s count`, count, 3, `The arrow function closes over count. It will outlive this frame.`);
        return t.ret(inc, 3, "makeCounter returns the arrow function; its frame is popped, but count survives in the closure.");
      };
      const a = makeCounter();
      const b = makeCounter();
      const out = [a(), a(), b()];
      t.log(out.join(" "), 10);
      t.end();
    },
  },
];

/** Run a scenario's tracer and return its steps. */
export function traceScenario(s: StackScenario): StackStep[] {
  const t = new Tracer();
  s.run(t);
  return t.steps;
}
