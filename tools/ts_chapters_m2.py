# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# New TypeScript chapters for Mastery Month 2 — Functions & data.
#
#   week 5  ts_overloads          overload signatures vs the implementation
#   week 5  ts_closures_scope     lexical scope, closures, the loop-closure bug
#   week 6  ts_recursion          base cases, the call stack, memoisation
#   week 7  ts_tuples             fixed-length, labelled, optional and rest tuples
#   week 7  ts_array_modern       at, toSorted, with, Object.groupBy, structuredClone
#   week 8  ts_interfaces_types   interface vs type, extends vs &, merging
#   week 8  ts_index_signatures   index signatures, Record, optional vs undefined
#
# Built with ts_chapter_kit.py's `_chapter`; every printed output and compiler
# message is computed (python tools/gen_ts_outputs.py).
# ---------------------------------------------------------------------------

_chapter(
    "ts_overloads", "TS: Functions & Types",
    "Overloads & Flexible Signatures",
    "Several call signatures for one function: overload lists, the implementation signature behind them, and when a union parameter is the better tool.",
    "Some functions genuinely return different things depending on what you pass: a `parse` that turns a string into a number and an array of strings into an array of numbers. One signature with unions loses that link — the caller gets `number | number[]` either way. Overloads list each call shape separately, so the compiler picks the right return type at every call site. They are also easy to overuse, and the implementation behind them is checked far more loosely than the overloads suggest.",
    "Java overloading picks one of several *method bodies* by argument types at compile time. TypeScript overloads are several *signatures* for one body: there is exactly one implementation, which must handle every overload at runtime by inspecting its arguments.",
    why=r"""
A function with a union parameter answers a union: `parse(input: string |
string[]): number | number[]`. Every caller, even one that obviously passed a
single string, gets back `number | number[]` and has to narrow it again. The
information "string in, number out" was in your head, not in the type.

Overloads put it in the type. They are how the standard library types
`Array.prototype.reduce`, `document.createElement("canvas")` and friends. The
catch is that the compiler checks *calls* against the overloads, but checks the
*implementation* only against its own, looser signature — so an overload can
promise something the body doesn't do.
""",
    idea=r"""
**The shape.** One or more overload signatures, with no body, followed by the
implementation:

```ts
function parse(input: string): number;
function parse(input: string[]): number[];
function parse(input: string | string[]): number | number[] {
  return typeof input === "string" ? Number(input) : input.map(Number);
}
```

- **Callers only see the overloads.** The implementation signature
  (`string | string[]`) is hidden; you cannot call `parse` with a union unless
  an overload accepts one.
- **Resolution is top-down.** The compiler tries each overload in order and
  uses the first that fits — so put the most specific first.
- **The implementation must be compatible with every overload**, and must
  handle each case at runtime by checking its arguments. The compiler does not
  verify that the `string` branch really returns a `number`.

**Prefer a union when the output doesn't depend on the input.** If every call
returns the same type, one signature with a union parameter (or an optional
parameter) is simpler and composes better:

```ts
function describe(value: string | number): string   // not two overloads
```

**Optional parameters and defaults** cover most "call it with more or fewer
arguments" cases without overloads at all. Reach for overloads when the *return
type* genuinely depends on the arguments.
""",
    examples=[
        ("String in, number out; array in, array out",
         r"""
function parse(input: string): number;
function parse(input: string[]): number[];
function parse(input: string | string[]): number | number[] {
  return typeof input === "string" ? Number(input) : input.map(Number);
}

const one = parse("42");
const many = parse(["1", "2", "3"]);
console.log(one.toFixed(1));
console.log(many.reduce((a, b) => a + b, 0));
""", [""],
         "`one` is a `number` and `many` a `number[]` — so `toFixed` and `reduce` need no narrowing. With a single union signature both would be `number | number[]`."),
        ("Different arities, one implementation",
         r"""
function makeTime(seconds: number): string;
function makeTime(hours: number, minutes: number, seconds?: number): string;
function makeTime(a: number, b?: number, c?: number): string {
  const total = b === undefined ? a : a * 3600 + b * 60 + (c ?? 0);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  return `${h}h ${m}m ${s}s`;
}

console.log(makeTime(3725));
console.log(makeTime(1, 2));
console.log(makeTime(1, 2, 5));
""", [""],
         "The overloads document the two meaningful ways to call it — and `makeTime(1, 2, 3, 4)` or a call with a string are rejected at the call site."),
        ("When a union is simply better",
         r"""
function label(value: string | number | boolean): string {
  return `${typeof value}: ${String(value)}`;
}

const inputs: (string | number | boolean)[] = ["hi", 3, true];
for (const v of inputs) console.log(label(v));
""", [""],
         "Every call returns a `string`, whatever it was given, so overloads would add nothing — and a union parameter accepts a `string | number | boolean` variable, which a set of overloads would not."),
    ],
    errors=[
        (2769, r"""
function parse(input: string): number;
function parse(input: string[]): number[];
function parse(input: string | string[]): number | number[] {
  return typeof input === "string" ? Number(input) : input.map(Number);
}
const raw: string | string[] = Math.random() > 2 ? "1" : ["1"];
console.log(parse(raw));
""", "Callers see only the overloads, and neither accepts `string | string[]`. The implementation would handle it, but its signature is invisible. Add a third overload for the union — or reconsider whether overloads are needed."),
        (2394, r"""
function size(value: string): number;
function size(value: number[]): number;
function size(value: string): number {
  return value.length;
}
console.log(size("abc"));
""", "Every overload must be compatible with the implementation signature. This implementation only accepts a `string`, so the `number[]` overload promises a call the body cannot take."),
    ],
    pitfalls=[
        ("The body doesn't have to keep the overloads' promises",
         r"""
function describe(n: number): string;
function describe(n: number, unit: string): string;
function describe(n: number, unit?: string): string {
  return n + " " + unit;
}
console.log(describe(5, "kg"));
console.log(describe(5));
""",
         r"""
function describe(n: number): string;
function describe(n: number, unit: string): string;
function describe(n: number, unit?: string): string {
  return unit === undefined ? String(n) : n + " " + unit;
}
console.log(describe(5, "kg"));
console.log(describe(5));
""",
         "The one-argument overload promises a sensible string; the implementation, checked only against its own `unit?: string` signature, happily prints `5 undefined`. Test every overload's case at runtime."),
        ("Most general first swallows the specific ones",
         (r"""
function toNumber(value: unknown): number | null;
function toNumber(value: string): number;
function toNumber(value: unknown): number | null {
  return typeof value === "string" ? Number(value) : null;
}
console.log(toNumber("5").toFixed(2));
""", 2531),
         r"""
function toNumber(value: string): number;
function toNumber(value: unknown): number | null;
function toNumber(value: unknown): number | null {
  return typeof value === "string" ? Number(value) : null;
}
console.log(toNumber("5").toFixed(2));
""",
         "Overloads are tried top-down, and `unknown` matches everything — so the `string` overload is never reached and the call gets `number | null`. Order them from most specific to most general."),
        ("A union variable can't reach an overload",
         (r"""
function wrap(x: string): string[];
function wrap(x: number): number[];
function wrap(x: string | number): (string | number)[] {
  return [x];
}
const values: (string | number)[] = ["a", 1];
for (const v of values) console.log(wrap(v).length);
""", 2769),
         r"""
function wrap(x: string): string[];
function wrap(x: number): number[];
function wrap(x: string | number): (string | number)[];
function wrap(x: string | number): (string | number)[] {
  return [x];
}
const values: (string | number)[] = ["a", 1];
for (const v of values) console.log(wrap(v).length);
""",
         "Inside the loop `v` is `string | number`, and no overload takes that. A final overload for the union case — or no overloads at all — fixes it."),
    ],
    later=[
        "**Week 13 — Function types in depth.** Overloads inside a function *type*, and assignability between them.",
        "**Week 18 — Generics.** Many overload sets collapse into one generic signature: `first<T>(xs: T[]): T | undefined`.",
        "**Week 21 — Conditional types.** A return type that *computes* from the argument type — the heavy-duty alternative to overloads.",
    ],
    exercises=[
        _drill("ts_overloads-parse", "Handle both overloads",
               "`parse` promises a `number` for a string and a `number[]` for an array. Replace `____` with the implementation's return expression that handles both at runtime.",
               r"""
import * as fs from "fs";
function parse(input: string): number;
function parse(input: string[]): number[];
function parse(input: string | string[]): number | number[] {
  return typeof input === "string" ? Number(input) : input.map(Number);
}
const lines = fs.readFileSync(0, "utf8").trim().split("\n");
const first = parse(lines[0]);
const rest = parse(lines.slice(1));
console.log(first * 2);
console.log(rest.length);
""", ['typeof input === "string" ? Number(input) : input.map(Number)'],
               ["21\n1\n2\n3", "5", "0\n10"],
               hint="Check `typeof input` and return the matching shape."),
        _drill("ts_overloads-time", "Two ways to call it",
               "`duration` takes either total seconds, or minutes and seconds. Replace `____` so the implementation computes the total seconds in both cases.",
               r"""
import * as fs from "fs";
function duration(seconds: number): string;
function duration(minutes: number, seconds: number): string;
function duration(a: number, b?: number): string {
  const total = b === undefined ? a : a * 60 + b;
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const nums = line.trim().split(/\s+/).map(Number);
  console.log(nums.length === 1 ? duration(nums[0]) : duration(nums[0], nums[1]));
}
""", ["b === undefined ? a : a * 60 + b"], ["125\n2 5", "59\n0 59", "3600\n60 0"],
               hint="When `b` is missing, `a` already *is* the total."),
        _chal("ts_overloads-fmt", "One formatter, three call shapes", "Medium",
              "Write `fmt` with three overloads: `fmt(n: number)` gives `n` with two decimals; `fmt(n: number, currency: string)` gives `<currency> <n to 2 dp>`; `fmt(values: number[])` gives the values each to two decimals joined by `, `. Each input line is `n`, `n CUR`, or `list a b c…`; print `fmt` of it.",
              r"""
function fmt(n: number): string;
function fmt(n: number, currency: string): string;
function fmt(values: number[]): string;
function fmt(a: number | number[], currency?: string): string {
  if (Array.isArray(a)) return a.map((v) => v.toFixed(2)).join(", ");
  return currency === undefined ? a.toFixed(2) : `${currency} ${a.toFixed(2)}`;
}
for (const line of input.split("\n")) {
  const parts = line.trim().split(/\s+/);
  if (parts[0] === "list") console.log(fmt(parts.slice(1).map(Number)));
  else if (parts.length === 2) console.log(fmt(Number(parts[0]), parts[1]));
  else console.log(fmt(Number(parts[0])));
}
""", ["3.14159\n5 EUR\nlist 1 2.5 3", "0\nlist 7", "12.345 USD\n-1"],
              hint="Branch on `Array.isArray(a)` first; then on whether `currency` was given."),
    ],
    quiz=[
        _cq("What do callers of an overloaded function see?", "Only the overload signatures — never the implementation signature",
            ["Only the implementation signature", "Both", "Whichever is more general"],
            "That's why a call with a union can fail even when the implementation would accept it."),
        _cq("In what order are overloads tried?", "Top to bottom; the first that fits wins",
            ["Most specific first, automatically", "Bottom to top", "All at once, merging the results"],
            "So the most specific overload must be written first."),
        _cq("What does the compiler check about the implementation?", "Its body against its own signature, and each overload's compatibility with that signature",
            ["That each branch returns what the matching overload promises", "Nothing", "Only the number of parameters"],
            "It cannot tell which branch serves which overload, so the promises are yours to keep."),
        _cq("When is a union parameter better than overloads?", "When the return type does not depend on which argument type was passed",
            ["Never", "When there are more than two types", "When the function is async"],
            "Overloads earn their keep only by linking input types to output types."),
        _cq("A variable is `string | number`. The overloads accept `string` and `number` separately. Can you call it?",
            "No — add an overload that accepts the union", ["Yes, the compiler splits the call", "Only with `as any`", "Yes, if the implementation accepts the union"],
            "Overload resolution needs one signature that accepts the whole argument type."),
    ],
    interview=[
        ("When would you use function overloads?",
         "When the return type depends on the argument types — string in gives number out, array in gives array out — and a caller shouldn't have to narrow the result. If the output type is the same for all inputs, a union parameter or optional parameters are simpler."),
        ("What's the implementation signature, and why can't callers use it?",
         "It's the signature on the body, usually a union of all the overloads' parameters. It's deliberately hidden so callers only see the precise overloads; if you want the union callable, add it as an overload."),
        ("What's the risk with overloads?",
         "The body is only checked against the implementation signature, so it can break an overload's promise — returning the wrong shape for one case — and the compiler won't notice. Each overload's case needs its own test."),
    ],
)


_chapter(
    "ts_closures_scope", "TS: Functions & Types",
    "Scope & Closures",
    "Where a name is visible — block, function and module scope — and closures: functions that keep the variables they were created with.",
    "A function in TypeScript remembers the variables that were in scope where it was *written*, not where it is called. That is a closure, and it is how a counter keeps its count between calls, how a module keeps private state without a class, and how an event handler knows which item it belongs to. The same rule explains the classic bug where every callback created in a `var` loop sees the last value.",
    "A Java lambda can only capture effectively-final locals. A JavaScript closure captures the *variable itself* — later assignments are visible to it — and there is no final requirement. Private state that Java puts in fields often lives in a closure here.",
    why=r"""
Many problems need a function that remembers something: how many times it has
been called, a cache of earlier answers, a configuration fixed at creation. You
could keep that in a global variable — until two users of the function trample
each other's state.

A closure keeps state private to one function value. `makeCounter()` returns a
function with its *own* count; call `makeCounter()` again and you get a second,
independent one. Understanding what a closure captures — the variable, not a
snapshot of its value — is also what makes the famous loop bug obvious instead
of mysterious.
""",
    idea=r"""
**Scopes.** A name declared with `let` or `const` is visible only inside the
`{ }` block that declares it — an `if`, a loop body, a function. Inner blocks
see outer names; outer blocks never see inner ones. Each file is also a
**module**, with its own top-level scope. (`var` is function-scoped and
hoisted; don't use it — it's here only to explain old code.)

**Closures.** A function can use the variables of every scope around the place
it was written:

```ts
function makeCounter(start = 0) {
  let count = start;          // lives as long as some function still uses it
  return () => ++count;       // the returned function closes over `count`
}
const a = makeCounter();
const b = makeCounter(100);
a(); a(); b();                // a's count is 2, b's is 101 — separate variables
```

Every call to `makeCounter` creates a fresh `count`, and the returned function
keeps it alive after `makeCounter` has returned.

**Captured variables, not values.** A closure sees the variable's *current*
value when it runs, not the value when it was created. That's what makes
closures useful for state — and what the loop pitfall below is about.

**Each loop iteration of `let` is a new variable.** `for (let i = 0; …)`
creates a fresh `i` per iteration, so closures created in the loop each get
their own. With `var` there is one `i` for the whole loop.

**The temporal dead zone.** A `let`/`const` exists from the start of its block
but can't be read until its declaration line runs — reading it earlier throws.
TypeScript reports most such uses at compile time.
""",
    examples=[
        ("Independent counters",
         r"""
function makeCounter(start = 0, step = 1) {
  let count = start;
  return () => {
    count += step;
    return count;
  };
}

const byOne = makeCounter();
const byTen = makeCounter(100, 10);
console.log(byOne(), byOne(), byOne());
console.log(byTen(), byTen());
console.log(byOne());
""", [""],
         "Two calls to `makeCounter`, two separate `count` variables. Nothing outside can read or reset them — the closure is the only way in."),
        ("Private state without a class",
         r"""
import * as fs from "fs";
function makeBank(opening: number) {
  let balance = opening;
  const history: string[] = [];
  return {
    deposit(amount: number) {
      balance += amount;
      history.push(`+${amount}`);
    },
    withdraw(amount: number) {
      if (amount > balance) {
        history.push(`refused ${amount}`);
        return;
      }
      balance -= amount;
      history.push(`-${amount}`);
    },
    report: () => `${balance} after ${history.join(" ")}`,
  };
}

const account = makeBank(50);
for (const op of fs.readFileSync(0, "utf8").trim().split(/\s+/)) {
  const n = Number(op.slice(1));
  if (op.startsWith("+")) account.deposit(n);
  else account.withdraw(n);
}
console.log(account.report());
""", ["+20 -30 -100 +5", "-50 -1"],
         "`balance` and `history` are reachable only through the three methods — the object literal closes over them. This is the module pattern, and a lightweight alternative to a class with private fields."),
        ("A cache that outlives each call",
         r"""
function makeSlowSquare() {
  const cache = new Map<number, number>();
  let computed = 0;
  const square = (n: number): number => {
    const hit = cache.get(n);
    if (hit !== undefined) return hit;
    computed++;
    const result = n * n;
    cache.set(n, result);
    return result;
  };
  return { square, stats: () => `${computed} computed, ${cache.size} cached` };
}

const { square, stats } = makeSlowSquare();
console.log([3, 4, 3, 3, 5, 4].map(square).join(" "));
console.log(stats());
""", [""],
         "Six calls, three computations: the `Map` lives in the closure between calls. Memoisation is just a closure over a cache."),
    ],
    errors=[
        (2304, r"""
for (let i = 0; i < 3; i++) {
  const doubled = i * 2;
}
console.log(doubled);
""", "`doubled` was declared inside the loop body, so outside it the name doesn't exist. Declare it in the outer scope if you need it there."),
        (2448, r"""
console.log(total);
const total = 10;
""", "Using a `const` before its declaration line would throw at runtime (the temporal dead zone), so the compiler rejects it."),
    ],
    pitfalls=[
        ("`var` in a loop: one variable for every closure",
         r"""
const printers: (() => string)[] = [];
for (var i = 0; i < 3; i++) {
  printers.push(() => `item ${i}`);
}
console.log(printers.map((p) => p()).join(", "));
""",
         r"""
const printers: (() => string)[] = [];
for (let i = 0; i < 3; i++) {
  printers.push(() => `item ${i}`);
}
console.log(printers.map((p) => p()).join(", "));
""",
         "`var i` is one variable shared by all three closures, and by the time they run the loop has left it at 3. `let` makes a new `i` for each iteration."),
        ("State in the wrong scope is shared",
         r"""
let count = 0;
function makeCounter() {
  return () => ++count;
}
const a = makeCounter();
const b = makeCounter();
a();
a();
console.log(`a=${a()} b=${b()}`);
""",
         r"""
function makeCounter() {
  let count = 0;
  return () => ++count;
}
const a = makeCounter();
const b = makeCounter();
a();
a();
console.log(`a=${a()} b=${b()}`);
""",
         "With `count` at module level, every counter closes over the same variable. Declare it inside the factory so each call gets its own."),
        ("A closure sees later changes",
         r"""
let rate = 0.1;
const withTax = (price: number) => price * (1 + rate);
rate = 0.2;
console.log(withTax(100).toFixed(2));
""",
         r"""
let rate = 0.1;
const makeWithTax = (r: number) => (price: number) => price * (1 + r);
const withTax = makeWithTax(rate);
rate = 0.2;
console.log(withTax(100).toFixed(2));
""",
         "The closure reads `rate` when it *runs*, so changing `rate` afterwards changes its result. To freeze a value, pass it in as a parameter when the function is created."),
    ],
    later=[
        "**Week 6 — Higher-order functions.** `once`, `memoize`, `debounce`: all closures over a little state.",
        "**Week 23 — Classes.** `#private` fields — the class-based way to get what a closure gives you here.",
        "**Week 26 — Async.** Callbacks that run later close over variables that may have changed by then.",
    ],
    exercises=[
        _drill("ts_closures_scope-counter", "A counter that remembers",
               "Replace `____` with the body of the returned function: add `step` to `count` and return the new value.",
               r"""
import * as fs from "fs";
function makeCounter(start: number, step: number) {
  let count = start;
  return () => {
    count += step;
    return count;
  };
}
const [start = "0", step = "1", calls = "1"] = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const next = makeCounter(Number(start), Number(step));
const seen: number[] = [];
for (let i = 0; i < Number(calls); i++) seen.push(next());
console.log(seen.join(" "));
""", ["count += step;\n    return count;"], ["0 1 3", "100 -5 4", "7 0 2"],
               hint="The returned arrow closes over `count`; update it, then return it."),
        _drill("ts_closures_scope-loop", "One variable per iteration",
               "Each printer should print its own index. Replace `____` with the loop header that gives every iteration its own `i`.",
               r"""
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
const printers: (() => number)[] = [];
for (let i = 0; i < n; i++) {
  printers.push(() => i * i);
}
console.log(printers.map((p) => p()).join(" "));
""", ["for (let i = 0; i < n; i++)"], ["3", "5", "1"],
               hint="`let` in a `for` header creates a fresh binding each iteration."),
        _chal("ts_closures_scope-once", "Only the first call counts", "Medium",
              "Write `once(fn)`: it returns a function that calls `fn` the first time and returns its result, and on every later call returns that same first result without calling `fn` again. Each input line is a list of numbers; for each line create `const first = once((x: number) => …)` whose function squares its argument and counts real calls, call `first` with each number, and print the results then `calls=<k>`.",
              r"""
function once(fn: (x: number) => number): (x: number) => number {
  let done = false;
  let result = 0;
  return (x: number) => {
    if (!done) {
      result = fn(x);
      done = true;
    }
    return result;
  };
}
for (const line of input.split("\n")) {
  let calls = 0;
  const first = once((x: number) => {
    calls++;
    return x * x;
  });
  const results = line.trim().split(/\s+/).map(Number).map((x) => first(x));
  console.log(`${results.join(" ")} calls=${calls}`);
}
""", ["3 4 5", "7\n-2 9", "0 0 1"],
              hint="Keep a `done` flag and the saved `result` in the closure."),
    ],
    quiz=[
        _cq("What does a closure capture?", "The variables themselves — later changes are visible to it",
            ["A snapshot of the values at creation", "Only `const` variables", "Nothing; it copies its arguments"],
            "That's what lets a counter keep counting, and what causes the `var` loop bug."),
        _cq("Why do closures made in `for (var i…)` all see the same `i`?", "`var` is one function-scoped variable for the whole loop",
            ["Closures can't capture loop variables", "Because of the event loop", "They don't; each sees its own"],
            "`let` in the loop header creates a new binding for each iteration."),
        _cq("`const a = makeCounter(); const b = makeCounter();` — do they share a count?", "No — each call creates a fresh variable",
            ["Yes, always", "Only if they're called in the same tick", "Only if `count` is `const`"],
            "Unless the state lives outside the factory, in which case they do."),
        _cq("Where is a `let` declared inside an `if` block visible?", "Only inside that block",
            ["Anywhere in the function", "Anywhere in the file", "From the start of the function, as `undefined`"],
            "`let`/`const` are block-scoped."),
        _cq("What is the temporal dead zone?", "The part of a block before a `let`/`const` declaration, where reading it throws",
            ["A block with no variables", "The time between two awaits", "Code after a `return`"],
            "TypeScript catches most such reads at compile time (TS2448)."),
    ],
    interview=[
        ("What is a closure?",
         "A function together with the variables of the scope it was defined in. It keeps those variables alive and sees their current values, which is how a factory like `makeCounter()` gives each returned function its own private state."),
        ("Explain the classic `var` loop bug.",
         "Callbacks created in `for (var i…)` all close over one function-scoped `i`, so when they run they all see its final value. `let` creates a fresh binding per iteration; in old code people used an IIFE to capture each value."),
        ("Closure or class for private state?",
         "A closure is lighter for one or two functions and state that's truly hidden. A class with `#private` fields reads better when there are many methods, needs `instanceof`, or benefits from methods shared on a prototype."),
    ],
)


_chapter(
    "ts_recursion", "TS: Functions & Types",
    "Recursion",
    "Functions that call themselves: base cases, the call stack and its depth limit, recursion versus loops, and memoisation for overlapping calls.",
    "Some problems are defined in terms of smaller versions of themselves — a nested list is a list of items that may be nested lists; the sum of a number's digits is its last digit plus the sum of the rest. A recursive function mirrors that definition directly. It needs two things: a base case that stops, and a step that makes the problem strictly smaller. Every call waits on the call stack, which in Node holds about ten thousand frames — so depth matters, and so does not recomputing the same subproblem twice.",
    "Recursion works exactly as in Java, including a stack depth limit (a `RangeError: Maximum call stack size exceeded` instead of a `StackOverflowError`). As in Java, there is no guaranteed tail-call optimisation, so deep linear recursion should become a loop.",
    why=r"""
Loops are perfect for "do this for each item". They are awkward for data whose
depth you don't know in advance: a folder that contains folders, a JSON value
that contains arrays of objects, an expression like `(1 + (2 * 3))`. Recursive
data is most naturally handled by recursive code — each call handles one level
and hands the rest to itself.

Recursion is also how you enumerate: every ordering of a list, every way to make
change, every path through a maze. The trade-offs — stack depth, repeated work
— are predictable once you can see the call tree.
""",
    idea=r"""
**Two parts, always.**

```ts
function sumDigits(n: number): number {
  if (n < 10) return n;                          // base case: small enough to answer directly
  return (n % 10) + sumDigits(Math.floor(n / 10)); // step: a strictly smaller problem
}
```

If the step does not make the input smaller, or some input never reaches the
base case, the recursion never ends.

**The call stack.** Each call gets a frame holding its arguments and locals,
waiting for the call it made to return. `sumDigits(4321)` is four frames deep.
Node allows roughly ten thousand frames; exceed it and you get
`RangeError: Maximum call stack size exceeded`. Recursion over a 100,000-item
linked list therefore needs a loop instead.

**Annotate the return type.** A recursive function's return type depends on
itself, so TypeScript may not infer it (TS7023). Writing `: number` is both the
fix and good documentation.

**Overlapping subproblems.** Naive `fib(n) = fib(n - 1) + fib(n - 2)` recomputes
the same values exponentially often — `fib(40)` makes over 300 million calls.
Remember each answer the first time (*memoise*) and the calls drop to `n`.

**Recursion versus a loop.** Linear recursion (one call per level, like
`sumDigits`) converts to a loop mechanically. Tree-shaped recursion (two or
more calls per level — nested data, enumeration) is where recursion earns its
keep.
""",
    examples=[
        ("Recursing on nested data",
         r"""
import * as fs from "fs";
type Nested = number | Nested[];

function total(value: Nested): number {
  if (typeof value === "number") return value;
  let sum = 0;
  for (const item of value) sum += total(item);
  return sum;
}

function depth(value: Nested): number {
  if (typeof value === "number") return 0;
  let deepest = 0;
  for (const item of value) deepest = Math.max(deepest, depth(item));
  return 1 + deepest;
}

const data = JSON.parse(fs.readFileSync(0, "utf8").trim()) as Nested;
console.log(`total ${total(data)}, depth ${depth(data)}`);
""", ["[1, [2, 3], [[4]]]", "7", "[[], [[], [5]]]"],
         "The type `Nested` is recursive, and so are the functions: a number is the base case, an array hands each item back to the same function."),
        ("Enumerating every ordering",
         r"""
import * as fs from "fs";
function permutations(items: string[]): string[][] {
  if (items.length <= 1) return [items];
  const out: string[][] = [];
  items.forEach((first, i) => {
    const rest = [...items.slice(0, i), ...items.slice(i + 1)];
    for (const perm of permutations(rest)) out.push([first, ...perm]);
  });
  return out;
}

const letters = fs.readFileSync(0, "utf8").trim().split("");
const all = permutations(letters);
console.log(all.map((p) => p.join("")).join(" "));
console.log(`${all.length} orderings`);
""", ["abc", "xy", "z"],
         "Each call fixes one first letter and recurses on the rest. The call tree has n! leaves — recursion is the natural way to walk it."),
        ("Memoisation turns exponential into linear",
         r"""
let calls = 0;
function slowFib(n: number): number {
  calls++;
  return n < 2 ? n : slowFib(n - 1) + slowFib(n - 2);
}

const memo = new Map<number, number>();
let memoCalls = 0;
function fastFib(n: number): number {
  memoCalls++;
  const known = memo.get(n);
  if (known !== undefined) return known;
  const value = n < 2 ? n : fastFib(n - 1) + fastFib(n - 2);
  memo.set(n, value);
  return value;
}

console.log(slowFib(25), `${calls} calls`);
console.log(fastFib(25), `${memoCalls} calls`);
""", [""],
         "Same answer; 242,785 calls against 49. The memo is consulted before any work is done."),
        ("When the stack runs out",
         r"""
function countDown(n: number): number {
  return n === 0 ? 0 : 1 + countDown(n - 1);
}

function countDownLoop(n: number): number {
  let steps = 0;
  while (n > 0) {
    n--;
    steps++;
  }
  return steps;
}

try {
  console.log(countDown(1_000_000));
} catch (e) {
  console.log(e instanceof RangeError ? "RangeError: stack exhausted" : "other error");
}
console.log(countDownLoop(1_000_000));
""", [""],
         "A million nested calls exceed Node's stack. The linear recursion converts to a loop with no depth limit at all."),
    ],
    errors=[
        (7023, r"""
function depth(tree: { children: unknown[] }) {
  return tree.children.length === 0
    ? 1
    : 1 + Math.max(...tree.children.map((c) => depth(c as { children: unknown[] })));
}
console.log(depth({ children: [] }));
""", "The return type of `depth` depends on the result of `depth`, so inference goes in a circle. Annotate it: `function depth(...): number`."),
        (2366, r"""
function power(base: number, exp: number): number {
  if (exp === 0) return 1;
  if (exp > 0) return base * power(base, exp - 1);
}
console.log(power(2, 10));
""", "Some path — here, a negative exponent — falls off the end and returns `undefined`, which isn't a `number`. Every path needs a return: handle `exp < 0`, or throw."),
    ],
    pitfalls=[
        ("A base case that negative input never reaches",
         r"""
function sumTo(n: number): number {
  if (n === 0) return 0;
  return n + sumTo(n - 1);
}
try {
  console.log(sumTo(4), sumTo(-1));
} catch (e) {
  console.log(e instanceof RangeError ? "stack overflow" : "other error");
}
""",
         r"""
function sumTo(n: number): number {
  if (n <= 0) return 0;
  return n + sumTo(n - 1);
}
console.log(sumTo(4), sumTo(-1));
""",
         "`n === 0` is never reached from `-1`, which only gets further away. Make the base case cover every input that can't shrink further — here, `n <= 0`."),
        ("Recomputing the same subproblem",
         r"""
let calls = 0;
function ways(n: number): number {
  calls++;
  if (n <= 1) return 1;
  return ways(n - 1) + ways(n - 2);
}
console.log(ways(20), `calls=${calls}`);
""",
         r"""
let calls = 0;
const memo = new Map<number, number>();
function ways(n: number): number {
  calls++;
  if (n <= 1) return 1;
  const known = memo.get(n);
  if (known !== undefined) return known;
  const result = ways(n - 1) + ways(n - 2);
  memo.set(n, result);
  return result;
}
console.log(ways(20), `calls=${calls}`);
""",
         "Counting the ways to climb 20 stairs one or two at a time makes 21,891 calls naively, because `ways(10)` alone is computed 89 times. With a memo it makes 39."),
        ("Mutating a shared array while recursing",
         r"""
function subsets(items: number[], from = 0, current: number[] = [], out: number[][] = []): number[][] {
  out.push(current);
  for (let i = from; i < items.length; i++) {
    current.push(items[i]);
    subsets(items, i + 1, current, out);
    current.pop();
  }
  return out;
}
console.log(subsets([1, 2]).map((s) => `[${s.join(",")}]`).join(" "));
""",
         r"""
function subsets(items: number[], from = 0, current: number[] = [], out: number[][] = []): number[][] {
  out.push([...current]);
  for (let i = from; i < items.length; i++) {
    current.push(items[i]);
    subsets(items, i + 1, current, out);
    current.pop();
  }
  return out;
}
console.log(subsets([1, 2]).map((s) => `[${s.join(",")}]`).join(" "));
""",
         "Every entry pushed into `out` is the *same* `current` array, which ends empty after backtracking — so all four subsets print as `[]`. Push a copy."),
    ],
    later=[
        "**Week 12 — Discriminated unions.** Evaluating an expression tree: recursion over a recursive union type.",
        "**Week 22 — Recursive types.** The same idea at the type level: `Json`, `Paths<T>`, `DeepReadonly<T>`.",
        "**Week 24 — Generators.** `yield*` for recursive traversal that produces values lazily.",
    ],
    exercises=[
        _drill("ts_recursion-digits", "Sum the digits",
               "Replace `____` with the recursive step: the last digit plus the digit sum of the rest.",
               r"""
import * as fs from "fs";
function sumDigits(n: number): number {
  if (n < 10) return n;
  return (n % 10) + sumDigits(Math.floor(n / 10));
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) console.log(sumDigits(Number(line)));
""", ["return (n % 10) + sumDigits(Math.floor(n / 10));"], ["4321\n7\n0", "999999", "10\n1000000001"],
               hint="`n % 10` is the last digit; `Math.floor(n / 10)` is the rest."),
        _drill("ts_recursion-power", "Fast power",
               "`power` computes `base ** exp` for a non-negative integer `exp` in O(log exp) calls. Replace `____` so an even exponent squares the result for half the exponent.",
               r"""
import * as fs from "fs";
let calls = 0;
function power(base: number, exp: number): number {
  calls++;
  if (exp === 0) return 1;
  if (exp % 2 === 0) {
    const half = power(base, exp / 2);
    return half * half;
  }
  return base * power(base, exp - 1);
}
const [b = "0", e = "0"] = fs.readFileSync(0, "utf8").trim().split(/\s+/);
console.log(power(Number(b), Number(e)), `calls=${calls}`);
""", ["const half = power(base, exp / 2);\n    return half * half;"], ["2 10", "3 0", "2 30", "10 5"],
               hint="Compute the half power ONCE and multiply it by itself — calling `power` twice would undo the saving."),
        _chal("ts_recursion-flatten", "Flatten with depth", "Medium",
              "Each input line is a JSON array whose items are numbers or nested arrays. Print its numbers flattened in order, space-separated (or `(empty)`), then `max depth <d>`, where a flat array has depth 1 and each level of nesting adds one.",
              r"""
type Nested = number | Nested[];
function flatten(value: Nested, out: number[]): number[] {
  if (typeof value === "number") {
    out.push(value);
    return out;
  }
  for (const item of value) flatten(item, out);
  return out;
}
function depth(value: Nested): number {
  if (typeof value === "number") return 0;
  let deepest = 0;
  for (const item of value) deepest = Math.max(deepest, depth(item));
  return deepest + 1;
}
for (const line of input.split("\n")) {
  const data = JSON.parse(line) as Nested;
  const flat = flatten(data, []);
  console.log(flat.join(" ") || "(empty)");
  console.log(`max depth ${depth(data)}`);
}
""", ["[1,[2,[3,4]],5]", "[]\n[[[]]]", "[[1],[2],[[3]]]\n[7]"],
              hint="Two recursive functions: one collects numbers into an output array, one returns 1 + the deepest child."),
    ],
    quiz=[
        _cq("What two things does every recursive function need?", "A base case that stops, and a step that makes the input strictly smaller",
            ["A loop and a counter", "A global variable and a return", "Two recursive calls"],
            "Without either, the recursion never ends."),
        _cq("What happens when recursion goes about ten thousand calls deep in Node?", "`RangeError: Maximum call stack size exceeded`",
            ["It silently returns `undefined`", "Node grows the stack forever", "A compile error"],
            "Deep linear recursion should become a loop."),
        _cq("Why does naive `fib(40)` take so long?", "It recomputes the same values exponentially many times",
            ["Numbers get too big", "Recursion is slow in JavaScript", "The stack limit makes it retry"],
            "Memoising each result makes it linear."),
        _cq("Why annotate a recursive function's return type?", "Inference can go circular (TS7023), and the annotation documents the contract",
            ["It's required for every function", "It makes recursion faster", "It raises the stack limit"],
            "The return type depends on itself, so TypeScript may give up."),
        _cq("When is recursion clearly better than a loop?", "For tree-shaped work — nested data, enumerating combinations",
            ["For summing an array", "Always", "Never — loops are always better"],
            "Linear recursion converts to a loop mechanically; branching recursion doesn't."),
    ],
    interview=[
        ("How do you avoid a stack overflow with recursion?",
         "Make sure depth is bounded — recursion depth equals the height of the data, so it's fine for balanced trees but not for a 100k-long list. For deep linear cases, convert to a loop or use an explicit stack; JavaScript engines don't reliably do tail-call optimisation."),
        ("What is memoisation?",
         "Caching a pure function's result by its arguments so repeated calls return instantly. It turns recursion with overlapping subproblems — Fibonacci, counting paths — from exponential to polynomial; it's top-down dynamic programming."),
        ("How would you flatten an arbitrarily nested array?",
         "Recursively: a number goes to the output, an array recurses on each item — or `arr.flat(Infinity)` in production. I'd type it with a recursive type like `type Nested = number | Nested[]`."),
    ],
)


_chapter(
    "ts_tuples", "TS: Data Structures",
    "Tuples",
    "Fixed-length arrays where each position has its own type: labelled, optional and rest elements, `readonly` tuples, and returning several values at once.",
    "An array says \"any number of these\". A tuple says \"exactly this, then exactly that\": `[string, number]` is a name and a score, in that order. Tuples are how a function returns two values without inventing an object type, how `Object.entries` describes its pairs, and how a variadic function types its arguments. They look like arrays at runtime — which is also where their one big hole is.",
    "Java has no tuples; you'd return a small record or `Map.Entry`. A TypeScript tuple is an ordinary array whose type fixes its length and each element's type, so destructuring it (`const [min, max] = minMax(xs)`) is typed precisely.",
    why=r"""
Returning two things from a function is common — a minimum and a maximum, a
quotient and a remainder, a parsed value and the rest of the input. An object
works but needs a name for the type; an array of `number[]` loses the fact
that there are exactly two.

A tuple states it: `[min: number, max: number]`. Destructuring gets the right
type at each position, and the compiler stops you reading a third element that
doesn't exist. Tuples also appear everywhere in the standard library — every
`Map` entry is a `[K, V]` — so reading them is as important as writing them.
""",
    idea=r"""
**Writing a tuple type.**

```ts
type Pair = [string, number];                          // exactly two
type Range = [start: number, end: number];             // labelled — the labels are documentation
type Point = [x: number, y: number, z?: number];      // an optional last element
type Row = [id: string, ...scores: number[]];          // a fixed head, then a rest element
```

**Inference makes arrays, not tuples.** `const p = [1, "a"]` is
`(string | number)[]` — an array that could have any length. To get a tuple,
annotate it, annotate the function's return type, or use `as const` (which
also makes it `readonly` with literal types).

**Reading positions.** Each index has its own type: in `[string, number]`,
`t[0]` is a `string` and `t[1]` a `number`. Reading `t[2]` is a compile error
(TS2493). Destructuring is the usual way in: `const [name, score] = pair`.

**`readonly` tuples** — `readonly [number, number]` — forbid `push`, index
assignment and every other mutation, which matters because…

**…the hole.** A (non-readonly) tuple is still an array at runtime, and
`push` is allowed on it. `pair.push(3)` compiles, and the type still claims two
elements. Prefer `readonly` tuples for values you return, and never grow a
tuple.

**Tuples you already use.** `Object.entries(obj)` gives `[string, V][]`;
`map.entries()` gives `[K, V]` pairs; `Promise.all([a, b])` returns a tuple of
the two results.
""",
    examples=[
        ("Returning two values",
         r"""
import * as fs from "fs";
function minMax(values: number[]): [min: number, max: number] {
  let min = Infinity;
  let max = -Infinity;
  for (const v of values) {
    if (v < min) min = v;
    if (v > max) max = v;
  }
  return [min, max];
}

const values = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const [low, high] = minMax(values);
console.log(`low ${low}, high ${high}, spread ${high - low}`);
""", ["3 9 -2 7", "5"],
         "The return annotation is what makes `[min, max]` a tuple; destructuring then gives two `number`s with names chosen by the caller."),
        ("A fixed head and a rest",
         r"""
import * as fs from "fs";
type Row = [name: string, ...scores: number[]];

function parseRow(line: string): Row {
  const [name = "", ...rest] = line.trim().split(/\s+/);
  return [name, ...rest.map(Number)];
}

for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [name, ...scores] = parseRow(line);
  const best = scores.length === 0 ? "none" : String(Math.max(...scores));
  console.log(`${name}: ${scores.length} scores, best ${best}`);
}
""", ["ada 90 85 99\ngrace 70\nlinus"],
         "A rest element types \"one string, then any number of numbers\" — exactly the shape of a CSV-ish row."),
        ("Entries are tuples",
         r"""
const stock: Record<string, number> = { apples: 3, pears: 0, figs: 12 };
const entries = Object.entries(stock);
const sorted = [...entries].sort((a, b) => b[1] - a[1]);
for (const [fruit, count] of sorted) console.log(`${fruit.padEnd(6)} ${count}`);
const counts = new Map<string, number>(entries);
console.log(counts.get("figs"));
""", [""],
         "`Object.entries` returns `[string, number][]`, the `sort` comparator reads position 1, and a `Map` is built straight from the pairs."),
    ],
    errors=[
        (2493, r"""
const pair: [string, number] = ["ada", 36];
console.log(pair[2]);
""", "A tuple's length is part of its type. Position 2 doesn't exist, so reading it is an error instead of a silent `undefined`."),
        (2322, r"""
function range(): [number, number] {
  const values = [1, 10];
  return values;
}
console.log(range());
""", "`values` was inferred as `number[]` — any length — so it can't be promised as exactly two numbers. Return the literal `[1, 10]` directly, or annotate `values`."),
    ],
    pitfalls=[
        ("An array literal is not a tuple",
         (r"""
function swap(pair: [string, number]): [number, string] {
  return [pair[1], pair[0]];
}
const item = ["pen", 3];
console.log(swap(item));
""", 2345),
         r"""
function swap(pair: [string, number]): [number, string] {
  return [pair[1], pair[0]];
}
const item: [string, number] = ["pen", 3];
console.log(swap(item).join(" "));
""",
         "`[\"pen\", 3]` stored in a plain `const` is inferred as `(string | number)[]`. Annotate the variable (or write the literal directly in the call) so it is a tuple."),
        ("`push` compiles on a tuple",
         r"""
function point(): [number, number] {
  return [3, 4];
}
const p = point();
p.push(5);
const [x, y] = p;
console.log(x, y, p.length);
""",
         r"""
function point(): readonly [number, number] {
  return [3, 4];
}
const p = point();
const moved = [...p, 5];
const [x, y] = p;
console.log(x, y, p.length, moved.length);
""",
         "A mutable tuple is still an array, so `push` type-checks and the length quietly becomes 3 while the type still says 2. Returning a `readonly` tuple makes `push` a compile error; build a new array instead."),
        ("Optional elements are `T | undefined`",
         r"""
type Point = [x: number, y: number, z?: number];
const flat: Point = [1, 2];
const deep: Point = [1, 2, 3];
console.log(deep[2]! + 1, flat[2]! + 1);
""",
         r"""
type Point = [x: number, y: number, z?: number];
const flat: Point = [1, 2];
const deep: Point = [1, 2, 3];
console.log((deep[2] ?? 0) + 1, (flat[2] ?? 0) + 1);
""",
         "The `!` silences the compiler's correct warning that `z` may be missing, and `undefined + 1` prints `NaN`. Give the optional element a default instead."),
    ],
    later=[
        "**Week 13 — Function types.** Rest parameters typed as tuples: `(...args: [name: string, age: number]) => void`.",
        "**Week 18 — Generics.** `const` type parameters that keep a literal tuple's exact types.",
        "**Week 22 — Recursive types.** Type-level programs over tuples: `Length<T>`, `Reverse<T>`, `Last<T>`.",
    ],
    exercises=[
        _drill("ts_tuples-minmax", "Two values back",
               "Replace `____` with the return statement that gives back the smallest and largest value as a tuple.",
               r"""
import * as fs from "fs";
function minMax(values: number[]): [number, number] {
  let min = Infinity;
  let max = -Infinity;
  for (const v of values) {
    if (v < min) min = v;
    if (v > max) max = v;
  }
  return [min, max];
}
const [lo, hi] = minMax(fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number));
console.log(lo, hi);
""", ["return [min, max];"], ["3 1 2", "-5 5", "7"],
               hint="A tuple is written like an array literal."),
        _drill("ts_tuples-swap", "Swap with destructuring",
               "Replace `____` so the two variables exchange values in one statement.",
               r"""
import * as fs from "fs";
let [a = "", b = ""] = fs.readFileSync(0, "utf8").trim().split(/\s+/);
[a, b] = [b, a];
console.log(a, b);
""", ["[a, b] = [b, a];"], ["left right", "1 2", "x y"],
               hint="Assign a tuple of the two values, reversed, back into both."),
        _chal("ts_tuples-divmod", "Quotient and remainder, for every pair", "Easy",
              "Write `divmod(a, b): [quotient: number, remainder: number]` using floor division (the remainder takes the divisor's sign). Each input line is `a b`; print `a = b*q + r` for it, using the tuple.",
              r"""
function divmod(a: number, b: number): [quotient: number, remainder: number] {
  const q = Math.floor(a / b);
  return [q, a - b * q];
}
for (const line of input.split("\n")) {
  const [a = 0, b = 1] = line.trim().split(/\s+/).map(Number);
  const [q, r] = divmod(a, b);
  console.log(`${a} = ${b}*${q} + ${r}`);
}
""", ["7 2\n-7 2", "7 -2\n0 3", "100 7"],
              hint="Return `[q, a - b * q]`, and destructure it at the call site."),
    ],
    quiz=[
        _cq("What type does `const p = [1, \"a\"]` get?", "`(string | number)[]`",
            ["`[number, string]`", "`readonly [1, \"a\"]`", "`any[]`"],
            "Array literals infer arrays. Annotate, or use `as const`, to get a tuple."),
        _cq("What is `pair[2]` for `pair: [string, number]`?", "A compile error (TS2493)",
            ["`undefined`", "`string | number`", "`never`, with no error"],
            "The length is part of a tuple's type."),
        _cq("Why prefer `readonly [number, number]` for a return type?", "A mutable tuple still allows `push`, which breaks the length the type promises",
            ["It's faster", "Only readonly tuples can be destructured", "Mutable tuples can't be returned"],
            "`readonly` removes every mutating method from the type."),
        _cq("What does `[name: string, ...scores: number[]]` describe?", "A string followed by any number of numbers",
            ["Exactly two elements", "An object with `name` and `scores`", "An array of strings and numbers in any order"],
            "A rest element can follow fixed elements."),
        _cq("What is each element of `Object.entries({ a: 1 })`?", "A `[string, number]` tuple",
            ["A `{ key, value }` object", "A `string`", "A `Map` entry object"],
            "Entries are key/value pairs as two-element tuples."),
    ],
    interview=[
        ("When would you use a tuple instead of an object?",
         "For small, positional, short-lived groupings where the positions are obvious — `[min, max]`, `[key, value]`, the result of `useState`. As soon as there are more than two or three fields, or the meaning isn't obvious from order, an object with named properties reads better."),
        ("How do you make an array literal a tuple?",
         "Annotate it or the function's return type, or use `as const`, which gives a `readonly` tuple of literal types. Plain inference always produces an array type."),
        ("What's unsound about tuples?",
         "They're arrays at runtime, so mutating methods like `push` type-check on a non-readonly tuple and break its declared length. Returning `readonly` tuples avoids it."),
    ],
)


_chapter(
    "ts_array_modern", "TS: Data Structures",
    "Modern Array Methods",
    "The newer, safer array toolkit: `at`, the copying methods `toSorted`/`toReversed`/`toSpliced`/`with`, `findLast`, `flatMap`, `Array.from({ length })`, `Object.groupBy` and `structuredClone`.",
    "The classic array methods have two long-standing traps: `sort`, `reverse` and `splice` change the array you call them on, and reading `xs[xs.length - 1]` for the last element is clumsy. ES2023 added copying versions of every mutating method, ES2022 added `at`, and ES2024 added `Object.groupBy`. All run on the installed Node and are part of the judge's `lib`. This chapter is the modern default for working with arrays without surprising anyone who holds a reference to them.",
    "Java's `List.sort` mutates too; its streams give you copies. Here the copying methods sit on the array itself: `xs.toSorted()` is `xs.stream().sorted().toList()` without the ceremony. `Object.groupBy` is `Collectors.groupingBy`.",
    why=r"""
A function receives an array, sorts it to find the median, and returns. The
caller's array is now sorted too — because `sort` works in place — and a bug
appears somewhere far away. The same goes for `reverse` and `splice`.

The copying methods make "give me a changed version, leave the original alone"
the one-word default. Together with `at(-1)`, `findLast`, `Object.groupBy` and
`structuredClone`, they remove most of the reasons old code mutated arrays or
wrote index arithmetic by hand.
""",
    idea=r"""
**Copying versions of the mutating methods** (ES2023):

| mutates | returns a new array instead |
|---|---|
| `xs.sort(cmp)` | `xs.toSorted(cmp)` |
| `xs.reverse()` | `xs.toReversed()` |
| `xs.splice(i, n, ...items)` | `xs.toSpliced(i, n, ...items)` |
| `xs[i] = v` | `xs.with(i, v)` |

They also work on `readonly` arrays, where the mutating versions don't exist.

**Reading from the end.** `xs.at(-1)` is the last element, `xs.at(-2)` the one
before. It returns `T | undefined` — the array may be too short.
`findLast(pred)` and `findLastIndex(pred)` search from the end.

**Building arrays.** `Array.from({ length: n }, (_, i) => i * i)` makes an
array of `n` computed values. (`new Array(n).map(...)` does *not* work — the
slots are holes that `map` skips.) `flatMap(f)` maps and flattens one level,
perfect for "each item produces zero or more results".

**Grouping.** `Object.groupBy(xs, keyFn)` returns an object from each key to
the items that produced it; `Map.groupBy` returns a `Map` (use it when keys
aren't strings). Every group's value is typed as possibly `undefined`, because
the compiler can't know which keys occur.

**Deep copies.** Spread (`[...xs]`, `{ ...o }`) copies one level.
`structuredClone(value)` copies all the way down — arrays, objects, `Map`s,
`Set`s, `Date`s — and so nested edits to the copy never reach the original.
""",
    examples=[
        ("Sort a copy, keep the original",
         r"""
import * as fs from "fs";
const scores = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const ranked = scores.toSorted((a, b) => b - a);
const median = scores.toSorted((a, b) => a - b)[Math.floor(scores.length / 2)];
console.log("input order:", scores.join(" "));
console.log("ranked:     ", ranked.join(" "));
console.log("median:", median, "last:", scores.at(-1));
""", ["7 3 9 1 5", "2 2 1"],
         "The input order is still intact after two sorts — neither touched `scores`."),
        ("Grouping and flat-mapping",
         r"""
import * as fs from "fs";
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const byLength = Object.groupBy(words, (w) => String(w.length));
for (const [len, group] of Object.entries(byLength)) {
  console.log(`${len}: ${(group ?? []).join(", ")}`);
}
const letters = words.flatMap((w) => [...w.toLowerCase()]);
console.log(`${letters.length} letters, ${new Set(letters).size} distinct`);
""", ["the cat sat on a mat", "Aa Bb Cc"],
         "`Object.groupBy` builds the buckets in one call; `flatMap` turns each word into its letters and flattens them into one array."),
        ("Copies that go all the way down",
         r"""
const original = { name: "cart", items: [{ sku: "a1", qty: 1 }] };
const shallow = { ...original, items: [...original.items] };
const deep = structuredClone(original);
shallow.items[0].qty = 5;
deep.items[0].qty = 99;
console.log(original.items[0].qty, shallow.items[0].qty, deep.items[0].qty);
const squares = Array.from({ length: 5 }, (_, i) => i * i);
console.log(squares.with(0, -1).join(" "), "|", squares.join(" "));
""", [""],
         "Copying the `items` array still shared its objects, so the shallow edit reached `original`. `structuredClone` copied the objects too. `with` returned a changed copy and left `squares` alone."),
    ],
    errors=[
        (2532, r"""
const xs = [3, 1, 2];
console.log(xs.at(-1).toFixed(1));
""", "`at` returns `T | undefined` — the array might be too short for the index — so you must handle the missing case (`xs.at(-1) ?? 0`) before using it."),
        (2339, r"""
const fixed: readonly number[] = [3, 1, 2];
fixed.sort();
console.log(fixed);
""", "A `readonly` array has no mutating methods at all. `fixed.toSorted()` returns a sorted copy, which is what you wanted anyway."),
    ],
    pitfalls=[
        ("`sort` changes the caller's array",
         r"""
function median(values: number[]): number {
  const sorted = values.sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}
const readings = [9, 1, 5];
console.log(median(readings), readings.join(" "));
""",
         r"""
function median(values: number[]): number {
  const sorted = values.toSorted((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}
const readings = [9, 1, 5];
console.log(median(readings), readings.join(" "));
""",
         "`sort` sorts in place and returns the same array, so `median` rearranged the caller's readings. `toSorted` works on a copy."),
        ("`new Array(n).map` does nothing",
         r"""
const squares = new Array(4).map((_, i) => i * i);
console.log(squares.length, squares.join(","));
""",
         r"""
const squares = Array.from({ length: 4 }, (_, i) => i * i);
console.log(squares.length, squares.join(","));
""",
         "`new Array(4)` has four *holes*, not four `undefined`s, and `map` skips holes — you get four holes back. `Array.from({ length })` calls the function for every index."),
        ("Default `sort` compares as strings",
         r"""
console.log([10, 9, 1, 100].toSorted().join(" "));
""",
         r"""
console.log([10, 9, 1, 100].toSorted((a, b) => a - b).join(" "));
""",
         "With no comparator, sorting converts every element to a string and compares those — so `100` comes before `9`. Numbers always need `(a, b) => a - b`."),
    ],
    later=[
        "**Week 16 — Immutability.** `readonly` arrays and the copying methods together: data that can't change underneath you.",
        "**Week 17 — Utility types.** `Object.groupBy`'s `Partial<Record<K, T[]>>` return type, explained.",
        "**Week 24 — Iterators.** Iterator helpers — `map`, `filter`, `take` — that work lazily on any iterable, not just arrays.",
    ],
    exercises=[
        _drill("ts_array_modern-last", "The last one, safely",
               "Replace `____` with an expression for the last element of `values`, or `0` when the line is empty.",
               r"""
import * as fs from "fs";
const text = fs.readFileSync(0, "utf8").trim();
const values = text === "" ? [] : text.split(/\s+/).map(Number);
const last = values.at(-1) ?? 0;
console.log(last * 2);
""", ["values.at(-1) ?? 0"], ["1 2 3", "", "-4"],
               hint="`at(-1)` reads from the end and may be `undefined`."),
        _drill("ts_array_modern-copy", "Rank without reordering",
               "Replace `____` with a sorted copy of `scores`, highest first, so the original order can still be printed.",
               r"""
import * as fs from "fs";
const scores = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const ranked = scores.toSorted((a, b) => b - a);
console.log(ranked.join(" "));
console.log(scores.join(" "));
""", ["scores.toSorted((a, b) => b - a)"], ["3 1 2", "10 9 100", "5"],
               hint="The copying sort takes the same comparator as `sort`."),
        _chal("ts_array_modern-group", "Group by first letter", "Medium",
              "The input is a line of words. Group them by their lowercase first letter with `Object.groupBy`. Print one line per group in alphabetical order of the letter: `<letter>: <words>` with the words in input order, then the letter of the largest group (the alphabetically first on a tie).",
              r"""
const words = input.split(/\s+/);
const groups = Object.groupBy(words, (w) => w[0].toLowerCase());
const letters = Object.keys(groups).toSorted();
let best = "";
let bestSize = 0;
for (const letter of letters) {
  const group = groups[letter] ?? [];
  console.log(`${letter}: ${group.join(" ")}`);
  if (group.length > bestSize) {
    best = letter;
    bestSize = group.length;
  }
}
console.log(best);
""", ["apple Banana avocado cherry blueberry", "x", "one two three Three"],
              hint="`Object.groupBy(words, keyFn)`, then walk `Object.keys(groups).toSorted()`. Each group may be `undefined` to the compiler."),
    ],
    quiz=[
        _cq("What does `xs.toSorted()` do that `xs.sort()` doesn't?", "Returns a new sorted array and leaves `xs` unchanged",
            ["Sorts numbers correctly by default", "Sorts faster", "Sorts in place and returns nothing"],
            "It's the copying counterpart; numbers still need a comparator."),
        _cq("What is `[1, 2, 3].at(-1)` typed as?", "`number | undefined`", ["`number`", "`3`", "`any`"],
            "An index from the end may be out of range."),
        _cq("Why does `new Array(3).map((_, i) => i)` not give `[0, 1, 2]`?", "The array has holes, and `map` skips holes",
            ["`map` can't use the index", "It gives `[0, 1, 2]`", "Arrays can't be created with `new`"],
            "`Array.from({ length: 3 }, (_, i) => i)` visits every index."),
        _cq("What does `Object.groupBy(xs, f)` return?", "An object from each key to the items that produced it",
            ["A `Map`", "An array of arrays", "A count per key"],
            "`Map.groupBy` is the version that returns a `Map`."),
        _cq("How is `structuredClone(o)` different from `{ ...o }`?", "It copies nested objects too, not just the top level",
            ["It's the same", "It only copies arrays", "It freezes the copy"],
            "Spread is shallow; nested objects stay shared."),
    ],
    interview=[
        ("What's the difference between `sort` and `toSorted`?",
         "`sort` sorts in place and returns the same array, which surprises any other code holding it; `toSorted` returns a sorted copy. The same pairing exists for `reverse`/`toReversed`, `splice`/`toSpliced`, and index assignment/`with`. Both still sort as strings without a comparator."),
        ("How do you deep-copy an object?",
         "`structuredClone` — it handles nested objects, arrays, `Map`, `Set`, `Date` and cycles. It can't copy functions or class prototypes, and `JSON.parse(JSON.stringify(x))` is the older, lossier approach."),
        ("How would you group an array by a key?",
         "`Object.groupBy(items, item => key)` in modern runtimes, or `Map.groupBy` for non-string keys. Before that: a `reduce` into an object or a loop filling a `Map`."),
    ],
)


_chapter(
    "ts_interfaces_types", "TS: Data Structures",
    "Interfaces & Type Aliases",
    "`interface` versus `type`: `extends` versus `&`, declaration merging, what only one of them can do, and how to choose.",
    "Two keywords can name an object shape: `interface User { … }` and `type User = { … }`. For plain object shapes they are almost interchangeable, which is why codebases argue about them. The real differences are few and concrete: only a `type` can name a union, a tuple or a mapped type; only an `interface` can be reopened and merged; and `extends` reports conflicts where `&` quietly produces `never`. Knowing those three is enough to choose deliberately.",
    "A Java `interface` is a contract a class implements. A TypeScript interface is just a named object shape — any value with the right members satisfies it, whether or not anything says `implements`. Classes can still `implements` an interface (or a type alias) to have the compiler check them.",
    why=r"""
Every non-trivial program names its data shapes: a `User`, an `Order`, a
`Config`. You'll write hundreds of these, and read hundreds more in library
type definitions — which lean heavily on interfaces, because users of a library
can extend them.

The choice between `interface` and `type` rarely matters for correctness, but
the edge cases do: an intersection that silently becomes `never`, an
interface you reopened by accident, a union you tried to write as an interface.
This chapter covers the differences that actually change what compiles.
""",
    idea=r"""
**Both name an object shape.**

```ts
interface Point { x: number; y: number }
type Point2 = { x: number; y: number };
```

Values of either are checked structurally — the same object satisfies both.

**Extending.** An interface `extends` one or more others; a type alias
combines with `&` (intersection):

```ts
interface Named { name: string }
interface Employee extends Named { salary: number }
type Employee2 = Named & { salary: number };
```

The difference shows on conflict: if `Employee` redeclares `name` with an
incompatible type, `extends` is an **error at the declaration**. An
intersection instead produces a property of type `never` — and the error only
appears later, wherever someone tries to build a value.

**Only `type` can do these:** unions (`type Id = string | number`), tuples,
primitives, function types written as aliases, mapped and conditional types.

**Only `interface` can do this — declaration merging:** two `interface`
declarations with the same name merge into one. That is how libraries let you
add a field to their types (module augmentation, week 14). Two `type`
declarations with the same name are an error (TS2300).

**Choosing.** A common, defensible rule: `interface` for object shapes that
others may extend, `type` for everything else — unions, tuples, computed
types. Whatever you pick, pick one per codebase.

**`implements`** asks the compiler to check that a class has the shape; it
works with interfaces and object type aliases alike. It adds nothing at
runtime.
""",
    examples=[
        ("The same shape, two spellings",
         r"""
interface Point {
  x: number;
  y: number;
}
type Size = { width: number; height: number };
type Rect = Point & Size;

const r: Rect = { x: 1, y: 2, width: 10, height: 4 };
const p: Point = r;
console.log(`at (${p.x}, ${p.y}), area ${r.width * r.height}`);
""", [""],
         "A `Rect` is also a `Point` — structural typing — so it can be assigned without a cast. The intersection combines an interface and a type alias freely."),
        ("Extending, and what only a type can say",
         r"""
interface Animal {
  name: string;
}
interface Dog extends Animal {
  breed: string;
}
type Pet = Dog | { kind: "fish"; name: string };

function describe(pet: Pet): string {
  return "breed" in pet ? `${pet.name} the ${pet.breed}` : `${pet.name} the fish`;
}

console.log(describe({ name: "Rex", breed: "collie" }));
console.log(describe({ kind: "fish", name: "Bubbles" }));
""", [""],
         "`Pet` is a union — only a type alias can name that. `\"breed\" in pet` narrows it to `Dog`."),
        ("Declaration merging",
         r"""
interface Settings {
  theme: string;
}
interface Settings {
  fontSize: number;
}

const s: Settings = { theme: "dark", fontSize: 14 };
console.log(Object.keys(s).join(", "));
""", [""],
         "The two declarations merge into one `Settings` with both fields. Libraries rely on this so you can add fields to their interfaces; in your own code it usually means a name was reused by accident."),
    ],
    errors=[
        (2430, r"""
interface Base {
  id: number;
}
interface Record2 extends Base {
  id: string;
}
const r: Record2 = { id: "a" };
console.log(r.id);
""", "`extends` checks the new interface against the old one at the declaration: `id` can't become a `string`."),
        (2300, r"""
type User = { name: string };
type User = { age: number };
const u: User = { name: "ada" };
console.log(u);
""", "Type aliases can't be reopened. If you meant to add fields, use an intersection with a new name — or an interface, which merges."),
    ],
    pitfalls=[
        ("An intersection with a conflict becomes `never`",
         (r"""
type Base = { id: number };
type Tagged = Base & { id: string };
const item: Tagged = { id: "a1" };
console.log(item.id);
""", 2322),
         r"""
type Base = { id: number };
type Tagged = Omit<Base, "id"> & { id: string };
const item: Tagged = { id: "a1" };
console.log(item.id);
""",
         "`number & string` is `never`, so no value can ever be a `Tagged` — but the error only appears when you try to build one. Replace the property explicitly: omit it first, then add the new type."),
        ("Excess-property checks only apply to fresh literals",
         r"""
interface PublicUser {
  id: number;
  name: string;
}
const row = { id: 1, name: "ada", passwordHash: "x9f" };
const shown: PublicUser = row;
console.log(JSON.stringify(shown));
""",
         r"""
interface PublicUser {
  id: number;
  name: string;
}
const row = { id: 1, name: "ada", passwordHash: "x9f" };
const shown: PublicUser = { id: row.id, name: row.name };
console.log(JSON.stringify(shown));
""",
         "Assigning a *variable* with extra properties is allowed (it's still a valid `PublicUser`), and the extra field travels along at runtime — straight into the JSON. Types describe a minimum, not an exact shape; copy the fields you mean to expose."),
        ("Merging an interface you didn't mean to",
         r"""
interface Options {
  retries: number;
}
const defaults: Options = { retries: 3 };
interface Options {
  verbose?: boolean;
}
console.log(Object.keys(defaults).length, defaults.verbose ?? "unset");
""",
         r"""
interface Options {
  retries: number;
}
const defaults: Options = { retries: 3 };
interface LoggingOptions extends Options {
  verbose?: boolean;
}
const logging: LoggingOptions = { ...defaults, verbose: true };
console.log(Object.keys(logging).length, logging.verbose ?? "unset");
""",
         "Reusing the name `Options` silently merged a second declaration into the first. It compiles because the new field is optional — which is exactly how an unrelated shape leaks into every `Options`. Give the extension its own name."),
    ],
    later=[
        "**Week 10 — Unions & aliases.** Literal unions as types — something only `type` can name.",
        "**Week 14 — Declarations.** Module augmentation: deliberately merging into a library's interface.",
        "**Week 15 — Structural typing.** Why a value with extra properties still satisfies an interface, and where that's unsound.",
    ],
    exercises=[
        _drill("ts_interfaces_types-extend", "Extend a shape",
               "`Employee` should have everything a `Person` has, plus `salary`. Replace `____` with the interface header that says so.",
               r"""
import * as fs from "fs";
interface Person {
  name: string;
}
interface Employee extends Person {
  salary: number;
}
function describe(e: Employee): string {
  return `${e.name} earns ${e.salary}`;
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [name = "", salary = "0"] = line.trim().split(/\s+/);
  console.log(describe({ name, salary: Number(salary) }));
}
""", ["interface Employee extends Person"], ["ada 100\ngrace 120", "linus 1"],
               hint="`interface New extends Old { … }`."),
        _drill("ts_interfaces_types-union", "A union needs a type alias",
               "Replace `____` with a type alias for an id that may be a number or a string.",
               r"""
import * as fs from "fs";
type Id = number | string;
function normalise(id: Id): string {
  return typeof id === "number" ? `#${id}` : id.toUpperCase();
}
for (const token of fs.readFileSync(0, "utf8").trim().split(/\s+/)) {
  const id: Id = /^\d+$/.test(token) ? Number(token) : token;
  console.log(normalise(id));
}
""", ["type Id = number | string;"], ["42 abc 7", "x"],
               hint="Interfaces can't name unions."),
        _chal("ts_interfaces_types-public", "Expose only the public fields", "Medium",
              "Each input line is a JSON user record, which may contain extra fields. Define `interface PublicUser { id: number; name: string; email?: string }` and a function `toPublic` that copies exactly those fields (leaving out `email` when absent). Print `JSON.stringify(toPublic(record))` per line.",
              r"""
interface PublicUser {
  id: number;
  name: string;
  email?: string;
}
function toPublic(record: { id: number; name: string; email?: string }): PublicUser {
  const out: PublicUser = { id: record.id, name: record.name };
  if (record.email !== undefined) out.email = record.email;
  return out;
}
for (const line of input.split("\n")) {
  const record = JSON.parse(line) as { id: number; name: string; email?: string };
  console.log(JSON.stringify(toPublic(record)));
}
""", ['{"id":1,"name":"ada","passwordHash":"x"}\n{"id":2,"name":"bo","email":"b@x.io","admin":true}', '{"id":3,"name":"cy","email":"c@y.io"}'],
              hint="Build a new object from the fields you want — assigning the record itself would carry its extra fields along."),
    ],
    quiz=[
        _cq("Which can name a union type?", "Only a `type` alias", ["Only an `interface`", "Both", "Neither — unions can't be named"],
            "`type Id = string | number`. Interfaces describe object shapes only."),
        _cq("Two `interface Settings` declarations in one scope…", "merge into one interface with both sets of members",
            ["are an error", "the second replaces the first", "create two unrelated types"],
            "Declaration merging — deliberate in library augmentation, accidental elsewhere."),
        _cq("`type T = { id: number } & { id: string }` — what is `T[\"id\"]`?", "`never`",
            ["`number | string`", "`string`", "A compile error at the declaration"],
            "Intersections intersect property types; the conflict only surfaces when a value is built."),
        _cq("What does `class A implements Shape` do at runtime?", "Nothing — it only asks the compiler to check the class",
            ["Copies `Shape`'s methods onto `A`", "Registers `A` as a `Shape`", "Makes `instanceof Shape` work"],
            "Interfaces and `implements` are erased."),
        _cq("Assigning a variable with extra properties to an interface type…", "is allowed; the extra properties stay on the object",
            ["is always an error", "strips the extra properties", "is allowed only with `as`"],
            "Excess-property errors are only for fresh object literals."),
    ],
    interview=[
        ("`interface` or `type`?",
         "For object shapes they're nearly equivalent. `interface` supports declaration merging and gives clearer errors with `extends`; `type` can also name unions, tuples, primitives and mapped or conditional types. I use `interface` for extensible object shapes and `type` for everything else — and follow the codebase's existing convention."),
        ("What's the difference between `extends` and `&`?",
         "`extends` checks compatibility at the declaration and errors on conflicting members. `&` intersects silently, so a conflicting property becomes `never` and the error appears only when you construct a value."),
        ("What is declaration merging?",
         "Two interface declarations with the same name combine into one. Libraries use it (with module augmentation) so users can add fields — e.g. to Express's `Request`. Type aliases can't merge."),
    ],
)


_chapter(
    "ts_index_signatures", "TS: Data Structures",
    "Index Signatures & Records",
    "Objects used as dictionaries: `{ [key: string]: T }`, `Record<K, V>`, why a missing key is `undefined`, optional properties versus `| undefined`, and the prototype keys lurking in `{}`.",
    "Sometimes an object's keys aren't known in advance — word counts, settings by name, scores by player. An index signature types that: `{ [word: string]: number }` means \"any string key, number values\". `Record<K, V>` says the same thing more briefly, and with a union for `K` it becomes exhaustive: `Record<\"red\" | \"green\", string>` must have both keys. The catch is that the type promises a value for *every* key while the object has only some — which is why reading a missing one is a classic bug.",
    "This is `Map<String, Integer>` built from a plain object. Unlike a Java map, a plain object inherits keys from `Object.prototype` (`toString`, `constructor`…), and TypeScript's index signature pretends every key is present unless you turn on `noUncheckedIndexedAccess`.",
    why=r"""
Counting things is the first thing most programs do with objects-as-maps:
`counts[word] = (counts[word] ?? 0) + 1`. It is also where the first subtle
bugs appear: a missing key reads as `undefined`, `undefined + 1` is `NaN`, and
the word `"constructor"` finds a function where you expected a count.

Index signatures and `Record` are how you type these dictionaries; knowing what
the type *doesn't* promise — that a key exists — is what makes them safe. From
week 14 on, the judge turns on the flag that makes the compiler say so too.
""",
    idea=r"""
**Index signatures.** `{ [key: string]: number }` accepts any string key and
promises a `number` value. The key's name is documentation only.

```ts
const counts: { [word: string]: number } = {};
counts["ts"] = 1;
```

**`Record<K, V>`** is the same idea as a utility type. With `K = string` it's
an open dictionary; with a union of literals it's a closed, exhaustive table:

```ts
const colors: Record<"red" | "green", string> = { red: "#f00", green: "#0f0" };
```

Leave a key out and it's a compile error (TS2741); add an unknown one and
that's an error too (TS2353, for a fresh literal).

**What the type does not promise.** `counts["nope"]` type-checks as `number`,
but it's `undefined` at runtime. Always supply a default when reading:
`counts[word] ?? 0`. Under `noUncheckedIndexedAccess` (on in this programme
from week 14) the type becomes `number | undefined` and the compiler insists.

**Optional properties versus `| undefined`.** `{ nickname?: string }` means
the key may be *absent*. `{ nickname: string | undefined }` means the key is
*present* and may hold `undefined`. Under `exactOptionalPropertyTypes` those
are different; without it, TypeScript treats them loosely alike.

**Indexing a known shape with a string.** A variable `key: string` can't index
`{ a: number; b: number }` — the object has no index signature (TS7053).
Narrow the key to `keyof typeof obj` first, or give the object a `Record` type.

**The prototype problem.** `{}` inherits `toString`, `constructor` and friends.
`"constructor" in {}` is `true`. For dictionaries fed by user input, check
`Object.hasOwn(obj, key)`, create the object with `Object.create(null)`, or use
a `Map` (week 9).
""",
    examples=[
        ("Counting with an index signature",
         r"""
import * as fs from "fs";
const words = fs.readFileSync(0, "utf8").trim().toLowerCase().split(/\s+/);
const counts: { [word: string]: number } = {};
for (const w of words) counts[w] = (counts[w] ?? 0) + 1;
const top = Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
for (const [word, n] of top.slice(0, 3)) console.log(`${word} ${n}`);
""", ["the cat and the hat and the bat", "a b c"],
         "`counts[w] ?? 0` is the whole trick: a word seen for the first time reads as `undefined`, and the default turns it into 0."),
        ("An exhaustive table",
         r"""
import * as fs from "fs";
type Level = "debug" | "info" | "warn" | "error";
const prefix: Record<Level, string> = {
  debug: "[.]",
  info: "[i]",
  warn: "[!]",
  error: "[x]",
};
const levels: Level[] = ["debug", "info", "warn", "error"];
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [first = "", ...rest] = line.split(" ");
  const level = levels.find((l) => l === first);
  console.log(level === undefined ? `[?] ${line}` : `${prefix[level]} ${rest.join(" ")}`);
}
""", ["info started\nwarn disk at 91%\nverbose ignored\nerror stopped"],
         "`Record<Level, string>` must list all four levels — add a fifth to `Level` and this object stops compiling until it gets a prefix too."),
        ("Absent versus present-but-undefined",
         r"""
type Profile = { name: string; nickname?: string };
const a: Profile = { name: "Ada" };
const b: Profile = { name: "Bo", nickname: undefined };
for (const p of [a, b]) {
  console.log(p.name, "nickname" in p, Object.hasOwn(p, "nickname"), p.nickname ?? "(none)");
}
""", [""],
         "Both read `undefined` for `nickname`, but only `b` *has* the key. Code that iterates keys or serialises objects can tell the difference, which is what `exactOptionalPropertyTypes` makes the type system track."),
    ],
    errors=[
        (7053, r"""
const limits = { small: 10, large: 100 };
const size: string = "small";
console.log(limits[size]);
""", "`limits` has exactly two known keys and no index signature, so an arbitrary `string` can't index it. Narrow `size` to `keyof typeof limits`, or type `limits` as a `Record<string, number>`."),
        (2741, r"""
type Level = "info" | "warn" | "error";
const colour: Record<Level, string> = { info: "blue", warn: "yellow" };
console.log(colour.info);
""", "`Record` over a union is exhaustive: every member needs an entry, and `error` is missing."),
        (2353, r"""
const settings: Record<"theme" | "lang", string> = { theme: "dark", lang: "en", fontSize: "14" };
console.log(settings.theme);
""", "A fresh object literal may not add keys the type doesn't know. It's usually a typo — or a sign the type needs the key."),
    ],
    pitfalls=[
        ("Incrementing a key that isn't there",
         r"""
const counts: { [k: string]: number } = {};
for (const w of ["a", "b", "a"]) counts[w]++;
console.log(JSON.stringify(counts));
""",
         r"""
const counts: { [k: string]: number } = {};
for (const w of ["a", "b", "a"]) counts[w] = (counts[w] ?? 0) + 1;
console.log(JSON.stringify(counts));
""",
         "The type says every key holds a `number`, so `counts[w]++` compiles — but the first time a word appears its value is `undefined`, and `undefined + 1` is `NaN` (which JSON prints as `null`). Always default a missing count to 0."),
        ("Words that are also prototype keys",
         r"""
const counts: { [k: string]: number } = {};
for (const w of ["toString", "constructor", "ok"]) counts[w] = (counts[w] ?? 0) + 1;
console.log(typeof counts.toString, typeof counts.constructor, counts.ok);
""",
         r"""
const counts: { [k: string]: number } = Object.create(null);
for (const w of ["toString", "constructor", "ok"]) counts[w] = (counts[w] ?? 0) + 1;
console.log(typeof counts.toString, typeof counts.constructor, counts.ok);
""",
         "A plain `{}` inherits `toString` and `constructor`, so `counts[w] ?? 0` finds a *function*, and `function + 1` builds a string. An object with no prototype (or a `Map`) has only the keys you put in."),
        ("Integer-like keys don't keep insertion order",
         r"""
const byCode: Record<string, string> = {};
byCode["b"] = "second";
byCode["10"] = "ten";
byCode["2"] = "two";
byCode["a"] = "first";
console.log(Object.keys(byCode).join(" "));
""",
         r"""
const byCode = new Map<string, string>();
byCode.set("b", "second");
byCode.set("10", "ten");
byCode.set("2", "two");
byCode.set("a", "first");
console.log([...byCode.keys()].join(" "));
""",
         "Object property order puts integer-like keys first, in numeric order, then the rest in insertion order. A `Map` keeps pure insertion order."),
    ],
    later=[
        "**Week 9 — Maps & Sets.** `Map` as the dictionary with no prototype keys and any key type.",
        "**Week 14 — `noUncheckedIndexedAccess`.** Every `record[key]` read becomes `V | undefined`, for real.",
        "**Week 20 — Mapped types.** `Record` rebuilt by hand: `{ [K in Keys]: V }`.",
    ],
    exercises=[
        _drill("ts_index_signatures-count", "Count safely",
               "Replace `____` so each word's count starts at 0 the first time it is seen.",
               r"""
import * as fs from "fs";
const counts: { [word: string]: number } = Object.create(null);
for (const w of fs.readFileSync(0, "utf8").trim().split(/\s+/)) {
  counts[w] = (counts[w] ?? 0) + 1;
}
console.log(Object.keys(counts).sort().map((w) => `${w}=${counts[w]}`).join(" "));
""", ["counts[w] = (counts[w] ?? 0) + 1;"], ["a b a", "x", "toString toString ok"],
               hint="Read with a default, then write the incremented value back."),
        _drill("ts_index_signatures-table", "Every level needs a colour",
               "Replace `____` with the type of `colour`: exactly one string for each `Level`.",
               r"""
import * as fs from "fs";
type Level = "low" | "mid" | "high";
const colour: Record<Level, string> = { low: "green", mid: "amber", high: "red" };
function level(n: number): Level {
  return n < 30 ? "low" : n < 70 ? "mid" : "high";
}
for (const t of fs.readFileSync(0, "utf8").trim().split(/\s+/)) console.log(colour[level(Number(t))]);
""", ["Record<Level, string>"], ["10 50 90", "30 70"],
               hint="A utility type from a union of keys to a value type."),
        _chal("ts_index_signatures-inventory", "An inventory ledger", "Medium",
              "Each input line is `+ item n` or `- item n`. Keep a dictionary from item to quantity (an object with no prototype, so any item name is safe). A removal that would take an item below zero prints `short <item>` and changes nothing. At the end print every item with a positive quantity as `item=n`, sorted by name, space-separated (or `(empty)`).",
              r"""
const stock: { [item: string]: number } = Object.create(null);
for (const line of input.split("\n")) {
  const [op = "", item = "", amount = "0"] = line.trim().split(/\s+/);
  const n = Number(amount);
  const have = stock[item] ?? 0;
  if (op === "+") stock[item] = have + n;
  else if (have < n) console.log(`short ${item}`);
  else stock[item] = have - n;
}
const lines = Object.keys(stock)
  .filter((k) => (stock[k] ?? 0) > 0)
  .sort()
  .map((k) => `${k}=${stock[k]}`);
console.log(lines.join(" ") || "(empty)");
""", ["+ apples 5\n- apples 2\n+ pears 1\n- figs 1", "+ constructor 1\n+ toString 2\n- toString 2", "- x 1"],
              hint="`Object.create(null)` gives a dictionary without inherited keys; read each quantity with `?? 0`."),
    ],
    quiz=[
        _cq("What does `{ [key: string]: number }` promise about `obj[\"missing\"]`?", "It types it as `number`, although at runtime it's `undefined`",
            ["That it's `number | undefined`", "That the key exists", "Nothing — it's `any`"],
            "Only `noUncheckedIndexedAccess` makes the read honest."),
        _cq("What does `Record<\"a\" | \"b\", number>` require?", "Exactly the keys `a` and `b`, each a number",
            ["At least one of the keys", "Any string keys", "Keys `a` or `b`, optionally"],
            "A union of literal keys makes the record exhaustive."),
        _cq("`{ x?: number }` vs `{ x: number | undefined }`?", "The first may omit the key; the second must have it, possibly holding `undefined`",
            ["They're identical in every mode", "The second may omit the key", "The first can't be `undefined`"],
            "`exactOptionalPropertyTypes` makes the distinction strict."),
        _cq("Why can `\"constructor\" in {}` be `true`?", "Plain objects inherit properties from `Object.prototype`",
            ["It's a TypeScript bug", "Because of `strict` mode", "It can't"],
            "Use `Object.hasOwn`, `Object.create(null)` or a `Map`."),
        _cq("What does TS7053 usually mean?", "You indexed an object that has no index signature with an arbitrary `string`",
            ["The key is misspelled", "The object is `readonly`", "The value is `any`"],
            "Narrow the key to `keyof typeof obj`, or type the object as a `Record`."),
    ],
    interview=[
        ("Index signature, `Record`, or `Map`?",
         "An index signature or `Record<string, V>` for simple JSON-like dictionaries with string keys; `Record<Union, V>` for an exhaustive table the compiler checks; a `Map` for non-string keys, frequent additions and deletions, insertion order, or untrusted keys where prototype collisions matter."),
        ("What does `noUncheckedIndexedAccess` change for records?",
         "Every `record[key]` read is typed `V | undefined`, which matches reality — the key may not be there. It forces defaults (`?? 0`) or checks, and catches the \"increment a missing counter\" class of bug at compile time."),
        ("Optional property versus `| undefined`?",
         "`x?: T` means the key can be absent; `x: T | undefined` means it's present but may be `undefined`. With `exactOptionalPropertyTypes` the first no longer accepts an explicit `undefined`, which matters for code that distinguishes missing from unset — like PATCH updates."),
    ],
)
