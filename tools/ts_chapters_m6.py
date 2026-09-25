# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# New TypeScript chapters for Mastery Month 6 — Runtime & architecture.
#
#   week 23  ts_class_design         abstract classes, `implements`, `override`,
#                                    `protected`, static factories, composition
#   week 23  ts_decorators           TC39 standard decorators — what they are and
#                                    what they desugar to (the runner can't run
#                                    `@` syntax, so the examples run the desugared
#                                    form; the compiler checks the real syntax)
#   week 24  ts_iterator_helpers     ES2025 iterator helpers and `Iterator.from`
#   week 24  ts_heap_pq              a generic binary heap / priority queue
#   week 25  ts_resource_management  `using`, `await using`, `Symbol.dispose`,
#                                    `DisposableStack`
#   week 25  ts_error_cause          Error subclasses, `cause`, `AggregateError`
#   week 26  ts_event_loop           the call stack, microtasks and tasks
#   week 26  ts_cancellation         `AbortController`, `AbortSignal`,
#                                    `Promise.withResolvers`, `Promise.try`
#   week 26  ts_async_iteration      `for await`, async generators, `Array.fromAsync`
#
# Built with ts_chapter_kit.py's `_chapter`; every printed output and compiler
# message is computed (python tools/gen_ts_outputs.py). Async examples are
# deterministic by construction (M6-03): ordering comes from the event loop's
# rules — microtasks before timers, timers in order of delay — never from how
# long something happened to take.
# ---------------------------------------------------------------------------

_chapter(
    "ts_class_design", "TS: Runtime & Architecture",
    "Designing with Classes",
    "Abstract classes, `implements`, `override`, `protected` and static factories — and when a class, a closure or plain composition is the better design.",
    "Classes give you a runtime constructor *and* a type, `private`/`protected` members, and inheritance. Used well — an abstract base that fixes an algorithm's shape, a private constructor behind a validating `static` factory, an interface implemented by several classes — they make invariants impossible to bypass. Used as a default, they produce fragile hierarchies. This chapter is the toolkit and the judgement.",
    "Much is familiar from Java: `abstract`, `implements`, `protected`, `static`. The differences matter: classes are structurally typed (two classes with the same shape are interchangeable unless one has a `private` member), `private` is compile-time only while `#private` is enforced at runtime, `override` is checked but optional, and plain objects and closures are first-class alternatives rather than workarounds.",
    why=r"""
The Classes chapter taught the mechanics: fields, constructors, methods,
`#private`, accessors. Design is the next question. When a `Shape` needs an
`area`, should it be an abstract class or a discriminated union? When an
`Account` must never go negative, how do you make *constructing* a bad one
impossible? When two classes share code, should one extend the other?

Those choices are what interviews probe and what codebases live with for years.
The tools are small — `abstract`, `implements`, `override`, `protected`, a
`private constructor` — but each exists to make one kind of mistake impossible.
""",
    idea=r"""
**`abstract` fixes the shape, leaves the details.** An abstract class can't be
instantiated; its `abstract` members must be implemented by every concrete
subclass. It's the right tool when the *algorithm* is shared and a step varies
(a `describe()` that calls an abstract `area()`).

**`implements` checks a class against an interface** without inheriting
anything. Use it for capabilities (`Comparable`, `Serializable`) that unrelated
classes share.

**`override` says "this replaces a base member".** If the base member is
renamed or removed, `override` turns the silent new method into a compile error
(and `--noImplicitOverride` makes the keyword mandatory).

**`protected`** is visible to subclasses but not to callers — the subclass
extension points of a base class. Like `private`, it's compile-time only.

**Private constructor + static factory** is the class form of a smart
constructor (week 16):

```ts
class Account {
  #balance: number;
  private constructor(opening: number) { this.#balance = opening; }
  static open(opening: number): Account | undefined {
    return opening >= 0 ? new Account(opening) : undefined;
  }
}
```

Nothing outside the class can call `new Account(-5)`.

**Composition over inheritance.** Inheritance couples a subclass to its base's
internals; changing the base can break every subclass (the "fragile base
class"). Prefer small objects passed in — a `Logger`, a `Clock`, a `Store` — and
reserve `extends` for real "is-a" relationships with a stable base.

**Class, closure or union?** A discriminated union (week 12) suits data with a
fixed set of variants handled by `switch`. A class suits an object with an
identity and invariants that its methods protect. A closure returning an object
of functions gives true privacy with no `this` at all.
""",
    examples=[
        ("An abstract base that fixes the algorithm",
         r"""
abstract class Shape {
  abstract readonly name: string;
  abstract area(): number;
  describe(): string {
    return `${this.name} with area ${this.area().toFixed(1)}`;
  }
}
class Circle extends Shape {
  readonly name = "circle";
  readonly r: number;
  constructor(r: number) {
    super();
    this.r = r;
  }
  area(): number {
    return Math.PI * this.r ** 2;
  }
}
class Rect extends Shape {
  readonly name = "rect";
  readonly w: number;
  readonly h: number;
  constructor(w: number, h: number) {
    super();
    this.w = w;
    this.h = h;
  }
  area(): number {
    return this.w * this.h;
  }
}
const shapes: Shape[] = [new Circle(1), new Rect(2, 3)];
for (const s of shapes) console.log(s.describe());
""", [""],
         "`describe` is written once, in the base; each subclass supplies `name` and `area`. Forgetting either in a subclass is a compile error (TS2515)."),
        ("A private constructor behind a factory",
         r"""
class Account {
  #balance: number;
  readonly owner: string;
  private constructor(owner: string, opening: number) {
    this.owner = owner;
    this.#balance = opening;
  }
  static open(owner: string, opening: number): Account | string {
    if (owner.trim() === "") return "owner required";
    if (!Number.isInteger(opening) || opening < 0) return "opening balance must be a whole number >= 0";
    return new Account(owner.trim(), opening);
  }
  withdraw(amount: number): string {
    if (amount > this.#balance) return `refused: ${this.owner} has ${this.#balance}`;
    this.#balance -= amount;
    return `ok: ${this.owner} has ${this.#balance}`;
  }
}
for (const [owner, opening] of [["ana", 100], ["", 5], ["bo", -3]] as const) {
  const acc = Account.open(owner, opening);
  console.log(typeof acc === "string" ? acc : acc.withdraw(30));
}
""", [""],
         "The only way to get an `Account` is `open`, which validates. `#balance` is private at runtime too, so no caller can write to it — the invariant lives in one place."),
        ("Composition: behaviour passed in",
         r"""
interface Clock {
  now(): number;
}
interface Log {
  write(line: string): void;
}
class RateLimiter {
  readonly #clock: Clock;
  readonly #log: Log;
  readonly #hits: number[] = [];
  readonly #limit: number;
  constructor(clock: Clock, log: Log, limit: number) {
    this.#clock = clock;
    this.#log = log;
    this.#limit = limit;
  }
  allow(user: string): boolean {
    const t = this.#clock.now();
    while (this.#hits.length > 0 && (this.#hits[0] ?? 0) <= t - 1000) this.#hits.shift();
    const ok = this.#hits.length < this.#limit;
    if (ok) this.#hits.push(t);
    this.#log.write(`${t}ms ${user} ${ok ? "allowed" : "limited"}`);
    return ok;
  }
}
let fake = 0;
const lines: string[] = [];
const limiter = new RateLimiter({ now: () => fake }, { write: (l) => lines.push(l) }, 2);
for (const t of [0, 100, 200, 1150, 1200]) {
  fake = t;
  limiter.allow("ana");
}
console.log(lines.join("\n"));
""", [""],
         "The limiter doesn't *extend* a clock or a logger — it receives them. A fake clock makes the output deterministic; in production you'd pass `{ now: () => Date.now() }`."),
    ],
    errors=[
        (2511, r"""
abstract class Shape {
  abstract area(): number;
}
const s = new Shape();
""", "An abstract class is a template, not a thing: only its concrete subclasses can be constructed."),
        (2515, r"""
abstract class Shape {
  abstract area(): number;
  abstract readonly name: string;
}
class Square extends Shape {
  readonly name = "square";
}
""", "Every abstract member must be implemented; `Square` forgot `area`. This is how an abstract base enforces its contract."),
        (4113, r"""
class Base {
  greet(): string {
    return "hi";
  }
}
class Loud extends Base {
  override greeting(): string {
    return "HI";
  }
}
""", "`override` claims a base member is being replaced, and `Base` has no `greeting` — a typo that would otherwise silently add a new method."),
        (2673, r"""
class Account {
  private constructor(readonly owner: string) {}
  static open(owner: string) {
    return new Account(owner);
  }
}
const a = new Account("ana");
""", "The constructor is private, so `open` is the only door. (Parameter properties like `readonly owner` are fine for the type checker; this app's runner can't strip them, which is why the runnable examples write fields out.)"),
    ],
    pitfalls=[
        ("A base constructor calling an overridable method",
         r"""
class Widget {
  constructor() {
    console.log("rendering " + this.render());
  }
  render(): string {
    return "widget";
  }
}
class Label extends Widget {
  text = "hello";
  override render(): string {
    return "label: " + this.text;
  }
}
new Label();
""",
         r"""
class Widget {
  render(): string {
    return "widget";
  }
  mount(): void {
    console.log("rendering " + this.render());
  }
}
class Label extends Widget {
  text = "hello";
  override render(): string {
    return "label: " + this.text;
  }
}
new Label().mount();
""",
         "The base constructor runs *before* the subclass's field initialisers, so `this.text` is still `undefined` when the overridden `render` runs. Don't call overridable methods from a constructor; do the work in a separate step."),
        ("A constructor that allows invalid objects",
         r"""
class Temperature {
  readonly celsius: number;
  constructor(celsius: number) {
    this.celsius = celsius;
  }
}
const readings = [21, -300, 15].map((c) => new Temperature(c));
console.log(readings.map((t) => t.celsius).join(" "));
""",
         r"""
class Temperature {
  readonly celsius: number;
  private constructor(celsius: number) {
    this.celsius = celsius;
  }
  static of(celsius: number): Temperature | undefined {
    return celsius >= -273.15 ? new Temperature(celsius) : undefined;
  }
}
const readings = [21, -300, 15].map((c) => Temperature.of(c)).filter((t) => t !== undefined);
console.log(readings.map((t) => t.celsius).join(" "));
""",
         "A public constructor can't refuse. A private one behind a factory that returns `undefined` (or a `Result`) makes \"below absolute zero\" unconstructable."),
        ("Static state shared by every instance",
         r"""
class Cart {
  static items: string[] = [];
  add(item: string): number {
    Cart.items.push(item);
    return Cart.items.length;
  }
}
const a = new Cart();
const b = new Cart();
a.add("pen");
console.log("items in b: " + b.add("cup"));
""",
         r"""
class Cart {
  readonly items: string[] = [];
  add(item: string): number {
    this.items.push(item);
    return this.items.length;
  }
}
const a = new Cart();
const b = new Cart();
a.add("pen");
console.log("items in b: " + b.add("cup"));
""",
         "`static` belongs to the class, so every cart shared one list. Per-object state is an instance field."),
    ],
    later=[
        "**Week 23 — Decorators.** Standard decorators wrap methods, fields and classes.",
        "**Week 24 — Generic data structures.** `Stack<T>`, `Heap<T>` and iterable classes.",
        "**Week 25 — Errors.** `Error` subclasses, and a `Result` returned by static factories.",
    ],
    exercises=[
        _drill("ts_class_design-factory", "A factory that refuses",
               "`Percent` has a private constructor. Replace `____` with the condition under which `Percent.of` creates one: a number from 0 to 100 inclusive.",
               r"""
import * as fs from "fs";
class Percent {
  readonly value: number;
  private constructor(value: number) {
    this.value = value;
  }
  static of(value: number): Percent | undefined {
    return value >= 0 && value <= 100 ? new Percent(value) : undefined;
  }
  of(amount: number): number {
    return (amount * this.value) / 100;
  }
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [p = "", amount = "0"] = line.trim().split(/\s+/);
  const pct = Percent.of(Number(p));
  console.log(pct === undefined ? `bad percent ${p}` : `${p}% of ${amount} = ${pct.of(Number(amount))}`);
}
""", ["value >= 0 && value <= 100"],
               ["50 80\n150 10\n0 99", "100 7\n-1 5"],
               hint="Both bounds are allowed."),
        _drill("ts_class_design-abstract", "Implement the abstract step",
               "`Report` fixes the format; each subclass supplies `rows()`. Replace `____` with `Totals`' implementation: one `<name>: <total>` row per person, in input order.",
               r"""
import * as fs from "fs";
abstract class Report {
  abstract readonly title: string;
  abstract rows(): string[];
  render(): string {
    return [`== ${this.title} ==`, ...this.rows(), `(${this.rows().length} rows)`].join("\n");
  }
}
class Totals extends Report {
  readonly title = "Totals";
  readonly data: [string, number[]][];
  constructor(data: [string, number[]][]) {
    super();
    this.data = data;
  }
  rows(): string[] {
    return this.data.map(([name, xs]) => `${name}: ${xs.reduce((a, b) => a + b, 0)}`);
  }
}
const data: [string, number[]][] = fs.readFileSync(0, "utf8").trim().split("\n").map((line) => {
  const [name = "", ...xs] = line.trim().split(/\s+/);
  return [name, xs.map(Number)];
});
console.log(new Totals(data).render());
""", ["return this.data.map(([name, xs]) => `${name}: ${xs.reduce((a, b) => a + b, 0)}`);"],
               ["ana 1 2 3\nbo 10", "cy 0"],
               hint="Map each `[name, numbers]` pair to one row string."),
        _chal("ts_class_design-inventory", "An inventory that protects its invariant", "Medium",
              "Write a class `Inventory` whose stock can never go negative: a private `Map` of counts, `add(item, n)`, `remove(item, n)` returning `true`/`false` (refused if there isn't enough), and `count(item)`. Each input line is `add <item> <n>`, `remove <item> <n>` or `count <item>`. Print `ok`/`refused` for changes and the number for counts, then every item with a positive count, sorted, as `<item>=<n>`.",
              r"""
class Inventory {
  readonly #stock = new Map<string, number>();
  add(item: string, n: number): void {
    this.#stock.set(item, this.count(item) + n);
  }
  remove(item: string, n: number): boolean {
    const have = this.count(item);
    if (n > have) return false;
    this.#stock.set(item, have - n);
    return true;
  }
  count(item: string): number {
    return this.#stock.get(item) ?? 0;
  }
  entries(): [string, number][] {
    return [...this.#stock].filter(([, n]) => n > 0).sort(([a], [b]) => a.localeCompare(b));
  }
}
const inv = new Inventory();
for (const line of input.split("\n")) {
  const [cmd = "", item = "", n = "0"] = line.trim().split(/\s+/);
  if (cmd === "add") {
    inv.add(item, Number(n));
    console.log("ok");
  } else if (cmd === "remove") {
    console.log(inv.remove(item, Number(n)) ? "ok" : "refused");
  } else if (cmd === "count") {
    console.log(inv.count(item));
  }
}
console.log(inv.entries().map(([k, v]) => `${k}=${v}`).join(" ") || "(empty)");
""", ["add pen 5\nremove pen 3\nremove pen 3\ncount pen\nadd cup 1\nremove cup 1", "remove ink 1\ncount ink"],
              hint="Keep the map `#private` so nothing outside the class can make a count negative."),
    ],
    quiz=[
        _cq("What does `abstract area(): number` in a base class require?",
            "Every concrete subclass must implement `area`", ["Callers must pass an `area`", "`area` returns 0 by default", "The class must be exported"],
            "Missing it is TS2515; the base class itself can't be instantiated (TS2511)."),
        _cq("What does the `override` keyword catch?",
            "A method meant to replace a base member when no such member exists (e.g. a typo)",
            ["Calls to `super`", "Missing constructors", "Private members"], "TS4113. `--noImplicitOverride` makes the keyword required."),
        _cq("How do you stop callers from constructing invalid instances?",
            "A `private constructor` plus a `static` factory that validates",
            ["Throw in every method", "Use `readonly` fields", "Make the class `abstract`"], "The factory is the only door, and it can refuse."),
        _cq("Why is calling an overridable method from a constructor risky?",
            "Subclass fields aren't initialised yet when the base constructor runs",
            ["It is a syntax error", "Methods can't be called before `super()`", "It always throws"], "The override sees `undefined` fields."),
        _cq("`private` vs `#private`?",
            "`private` is checked only by the compiler; `#private` is enforced at runtime",
            ["They are identical", "`#private` is compile-time only", "`private` fields are faster"], "`#` fields are part of JavaScript."),
        _cq("When is composition better than inheritance?",
            "When you want to reuse behaviour without coupling to a base class's internals",
            ["Never", "Only for interfaces", "Only for static methods"], "Pass collaborators in; keep `extends` for stable is-a relationships."),
    ],
    interview=[
        ("Abstract class or interface?",
         "An interface describes a capability with no implementation and can be implemented by unrelated classes — or by plain objects. An abstract class shares implementation: a template method that calls abstract steps. If there's no shared code, I use an interface."),
        ("How do you enforce an invariant in a class?",
         "Make the state `#private`, validate in every method that changes it, and don't let construction bypass the rules: a private constructor behind a static factory that returns `undefined` or a `Result` for bad input."),
        ("Why prefer composition over inheritance?",
         "Inheritance couples subclasses to the base class's internals and call order — the fragile base class problem — and a class can only extend one base. Composition passes small collaborators in, which is easier to test (fake clocks, fake loggers) and to change."),
    ],
)


_chapter(
    "ts_decorators", "TS: Runtime & Architecture",
    "Decorators",
    "TC39 standard decorators: functions that wrap a class, method, accessor or field at definition time — how they're typed, what they desugar to, and why this app's runner can't execute the `@` syntax yet.",
    "A decorator is a function applied with `@name` above a class or member. It receives the original value and a `context` object (kind, name, `addInitializer`) and may return a replacement. TypeScript 5.0+ implements the standard (TC39 stage 3) decorators by default; the older `--experimentalDecorators` form has a different signature. Decorators are not erasable — they call functions at class definition — so type stripping can't run them; this chapter runs their desugared form and lets the compiler check the real syntax.",
    "Java annotations are metadata read by a framework; a TypeScript decorator is *code* that runs when the class is defined and can replace what it decorates. The closest Java analogue is an annotation processor combined with a proxy — TypeScript's is one function.",
    why=r"""
Frameworks love decorators: `@Component`, `@Injectable`, `@Get("/users")`,
`@observable`. They let a library add behaviour — logging, caching, validation,
registration — by writing one line above a member instead of editing its body.

For years TypeScript shipped an experimental version that differed from where
the JavaScript standard ended up. TypeScript 5.0 implemented the standard, which
changes the signatures you'll see in modern code. And because decorators *run*
— they aren't just types — they are one of the features type stripping can't
handle (week 14). Knowing what a decorator desugars to is how you understand
all of this without magic.
""",
    idea=r"""
**A method decorator is a function from a method to a method:**

```ts
function logged<This, Args extends unknown[], R>(
  target: (this: This, ...args: Args) => R,
  context: ClassMethodDecoratorContext<This, (this: This, ...args: Args) => R>,
) {
  return function (this: This, ...args: Args): R {
    console.log(`→ ${String(context.name)}(${args.join(", ")})`);
    return target.call(this, ...args);
  };
}

class Calc {
  @logged
  add(a: number, b: number) { return a + b; }
}
```

**What it desugars to.** Roughly: after the class body is evaluated,
`Calc.prototype.add = logged(Calc.prototype.add, { kind: "method", name: "add", … })`.
That's the whole idea — a function applied to the original, whose result
replaces it. Decorators on one member apply bottom-up (the one nearest the
member first).

**Kinds and contexts.** Each kind gets a matching context type:
`ClassDecoratorContext`, `ClassMethodDecoratorContext`,
`ClassGetterDecoratorContext`, `ClassFieldDecoratorContext`,
`ClassAccessorDecoratorContext` (for the new `accessor` keyword). A field
decorator returns an *initializer* transformer rather than a replacement.
`context.addInitializer(fn)` runs code when an instance (or the class) is set up
— useful for binding methods or registering the class.

**Decorator factories** take configuration and return a decorator:
`@retry(3)` is `retry(3)` evaluated first, then applied.

**Standard vs experimental.** With `--experimentalDecorators` a method decorator
was `(target, propertyKey, descriptor) => …` and parameter decorators existed.
Standard decorators have the `(value, context)` signature and no parameter
decorators. Mixing the two is a common source of confusing errors.

**Why they can't run here.** Decorators execute code at class definition, so a
stripper can't delete them, and Node doesn't implement the syntax natively yet.
Every runnable example below applies the decorator function by hand — which is
exactly what the `@` line means.
""",
    examples=[
        ("A logging decorator, applied by hand",
         r"""
function logged<This, Args extends unknown[], R>(target: (this: This, ...args: Args) => R, name: string) {
  return function (this: This, ...args: Args): R {
    const result = target.call(this, ...args);
    console.log(`${name}(${args.join(", ")}) = ${String(result)}`);
    return result;
  };
}

class Calc {
  add(a: number, b: number): number {
    return a + b;
  }
  scale(x: number, k: number): number {
    return x * k;
  }
}
// What `@logged` above each method would do:
Calc.prototype.add = logged(Calc.prototype.add, "add");
Calc.prototype.scale = logged(Calc.prototype.scale, "scale");

const c = new Calc();
c.scale(c.add(2, 3), 4);
""", [""],
         "A decorator is just this: a function that takes the original method and returns a wrapper. The `@logged` syntax only changes *where* you write the call — above the member instead of after the class."),
        ("A decorator factory with configuration",
         r"""
function retry(times: number) {
  return function <Args extends unknown[], R>(target: (...args: Args) => R, name: string) {
    return (...args: Args): R => {
      for (let attempt = 1; ; attempt++) {
        try {
          return target(...args);
        } catch (e) {
          console.log(`${name} attempt ${attempt} failed: ${e instanceof Error ? e.message : String(e)}`);
          if (attempt >= times) throw e;
        }
      }
    };
  };
}

let calls = 0;
function flaky(x: number): number {
  calls++;
  if (calls < 3) throw new Error("busy");
  return x * 2;
}
// @retry(3) applied to `flaky`:
const safe = retry(3)(flaky, "flaky");
console.log("result " + safe(21));
""", [""],
         "`@retry(3)` evaluates `retry(3)` first — a decorator factory — and applies the decorator it returns. Configuration goes in the outer call."),
        ("Order: nearest to the member first",
         r"""
type Fn = (s: string) => string;
const trim = (f: Fn): Fn => (s) => f(s.trim());
const upper = (f: Fn): Fn => (s) => f(s.toUpperCase());
const exclaim = (f: Fn): Fn => (s) => f(s + "!");

const base: Fn = (s) => `[${s}]`;
// @trim
// @upper
// @exclaim
// greet(s) { ... }   — applied bottom-up: exclaim first, then upper, then trim
const decorated = trim(upper(exclaim(base)));
console.log(decorated("  hello "));
""", [""],
         "Stacked decorators are applied from the bottom up, so the *top* decorator's wrapper runs first when the method is called: `trim`, then `upper`, then `exclaim`, then the original."),
    ],
    errors=[
        (1206, r"""
function logged(target: unknown, context: unknown) {
  return target;
}
@logged
function greet() {
  return "hi";
}
""", "Decorators apply to classes and class members only — a plain function declaration can't be decorated. Wrap it by hand instead: `const greet = logged(…)`."),
        (1241, r"""
function legacy(target: object, key: string, descriptor: PropertyDescriptor) {
  return descriptor;
}
class Calc {
  @legacy
  add(a: number, b: number) {
    return a + b;
  }
}
""", "This is an `--experimentalDecorators` signature (`target, key, descriptor`). Standard decorators receive `(value, context)`, so the compiler can't resolve this call."),
    ],
    pitfalls=[
        ("A wrapper that loses `this`",
         r"""
function logged<Args extends unknown[], R>(target: (...args: Args) => R) {
  return (...args: Args): R => {
    console.log("call");
    return target(...args);
  };
}
class Counter {
  count = 0;
  inc(): number {
    return ++this.count;
  }
}
Counter.prototype.inc = logged(Counter.prototype.inc);
try {
  console.log(new Counter().inc());
} catch (e) {
  console.log("crashed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
function logged<This, Args extends unknown[], R>(target: (this: This, ...args: Args) => R) {
  return function (this: This, ...args: Args): R {
    console.log("call");
    return target.call(this, ...args);
  };
}
class Counter {
  count = 0;
  inc(): number {
    return ++this.count;
  }
}
Counter.prototype.inc = logged(Counter.prototype.inc);
console.log(new Counter().inc());
""",
         "The wrapper called the original method as a plain function, so `this` was `undefined`. A method decorator must forward `this` — a `function` wrapper (not an arrow) and `target.call(this, …)`."),
        ("Decorating a plain function",
         (r"""
function logged(target: unknown, context: unknown) {
  return target;
}
@logged
function greet(): string {
  return "hi";
}
console.log(greet());
""", 1206),
         r"""
function logged<R>(target: () => R, name: string): () => R {
  return () => {
    console.log("calling " + name);
    return target();
  };
}
const greet = logged(() => "hi", "greet");
console.log(greet());
""",
         "Only classes and class members take `@` decorators. For a function, apply the wrapper directly — it's the same idea without the syntax."),
        ("A legacy decorator signature",
         (r"""
function legacy(target: object, key: string, descriptor: PropertyDescriptor) {
  return descriptor;
}
class Calc {
  @legacy
  add(a: number, b: number) {
    return a + b;
  }
}
console.log(new Calc().add(1, 2));
""", 1241),
         r"""
class Calc {
  add(a: number, b: number) {
    return a + b;
  }
}
function standard<This, Args extends unknown[], R>(target: (this: This, ...args: Args) => R, name: string) {
  return function (this: This, ...args: Args): R {
    console.log("standard decorator on " + name);
    return target.call(this, ...args);
  };
}
Calc.prototype.add = standard(Calc.prototype.add, "add");
console.log(new Calc().add(1, 2));
""",
         "Code copied from an older codebase often uses the experimental `(target, key, descriptor)` form. With standard decorators (TypeScript 5.0's default) the signature is `(value, context)`."),
    ],
    later=[
        "**Week 23 — Class design.** What decorators usually decorate: methods, accessors and classes.",
        "**Week 14 — Erasable syntax.** Why the runner can't execute decorators, alongside `enum` and parameter properties.",
    ],
    exercises=[
        _drill("ts_decorators-timed", "A counting decorator",
               "`counted` wraps a method and counts its calls, the way a `@counted` decorator would. Replace `____` so the wrapper forwards `this` and the arguments to the original method.",
               r"""
import * as fs from "fs";
const counts = new Map<string, number>();
function counted<This, Args extends unknown[], R>(target: (this: This, ...args: Args) => R, name: string) {
  return function (this: This, ...args: Args): R {
    counts.set(name, (counts.get(name) ?? 0) + 1);
    return target.call(this, ...args);
  };
}
class Greeter {
  prefix = "hello";
  greet(name: string): string {
    return `${this.prefix} ${name}`;
  }
}
Greeter.prototype.greet = counted(Greeter.prototype.greet, "greet");
const g = new Greeter();
for (const name of fs.readFileSync(0, "utf8").trim().split(/\s+/)) console.log(g.greet(name));
console.log(`greet called ${counts.get("greet") ?? 0} times`);
""", ["return target.call(this, ...args);"],
               ["ana bo", "cy", "a b c d"],
               hint="Call the original with `.call`, passing `this` first."),
        _drill("ts_decorators-memo", "A memoising wrapper",
               "Replace `____` so `memo` returns the cached result when it has seen the argument before, and otherwise computes, stores and returns it.",
               r"""
import * as fs from "fs";
let computed = 0;
function memo<R>(target: (n: number) => R) {
  const cache = new Map<number, R>();
  return (n: number): R => {
    const hit = cache.get(n);
    if (hit !== undefined) return hit;
    const value = target(n);
    cache.set(n, value);
    return value;
  };
}
const square = memo((n: number) => {
  computed++;
  return n * n;
});
const inputs = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
console.log(inputs.map(square).join(" "));
console.log(`computed ${computed} of ${inputs.length}`);
""", ["const hit = cache.get(n);\n    if (hit !== undefined) return hit;"],
               ["2 3 2 2 4", "7", "1 1 1"],
               hint="Look up first; return early on a hit."),
        _chal("ts_decorators-validate", "A validating wrapper", "Medium",
              "Write `validated(check, target, name)` — what a `@validated(check)` decorator would do — returning a function that throws `Error(\"<name>: bad input <x>\")` when `check(x)` is false and otherwise calls `target(x)`. Wrap `sqrt` with a non-negative check and `reciprocal` with a non-zero check. Each input line is `<fn> <x>`; print the result to 3 decimals, or the error message, or `unknown fn <f>`.",
              r"""
function validated(check: (x: number) => boolean, target: (x: number) => number, name: string): (x: number) => number {
  return (x) => {
    if (!check(x)) throw new Error(`${name}: bad input ${x}`);
    return target(x);
  };
}
const fns: Record<string, (x: number) => number> = {
  sqrt: validated((x) => x >= 0, Math.sqrt, "sqrt"),
  reciprocal: validated((x) => x !== 0, (x) => 1 / x, "reciprocal"),
};
for (const line of input.split("\n")) {
  const [name = "", x = "0"] = line.trim().split(/\s+/);
  const fn = Object.hasOwn(fns, name) ? fns[name] : undefined;
  if (fn === undefined) {
    console.log(`unknown fn ${name}`);
    continue;
  }
  try {
    console.log(fn(Number(x)).toFixed(3));
  } catch (e) {
    console.log(e instanceof Error ? e.message : String(e));
  }
}
""", ["sqrt 2\nsqrt -4\nreciprocal 4\nreciprocal 0\ncube 3", "sqrt 0"],
              hint="The wrapper checks, then either throws or delegates."),
    ],
    quiz=[
        _cq("What does a standard method decorator receive?",
            "The original method and a context object", ["`target, key, descriptor`", "Only the class", "Only the method name"],
            "`(value, context)` — `context` has `kind`, `name`, `static`, `private` and `addInitializer`."),
        _cq("`@a @b method() {}` — which decorator is applied first?",
            "`@b` (the one nearest the member)", ["`@a`", "Both at once", "It is undefined"], "Decorators are applied bottom-up; the top one's wrapper runs outermost."),
        _cq("What is `@retry(3)`?",
            "A decorator factory: `retry(3)` returns the decorator that is applied", ["Three decorators", "A type annotation", "A comment"],
            "The outer call takes configuration."),
        _cq("Why can't type stripping run decorators?",
            "They execute code at class definition, so deleting them would delete behaviour",
            ["They're only types", "Node forbids classes", "They require `enum`"], "Like `enum` and parameter properties, they aren't erasable."),
        _cq("Which is the experimental (legacy) method decorator signature?",
            "`(target, propertyKey, descriptor)`", ["`(value, context)`", "`(context)`", "`(this, ...args)`"], "Enabled by `--experimentalDecorators`; different from the standard."),
        _cq("How must a method-decorator wrapper call the original?",
            "With the same `this` — e.g. `target.call(this, ...args)` in a `function` wrapper",
            ["As a plain function", "With `new`", "Through `super`"], "An arrow wrapper can't receive the instance as `this`."),
    ],
    interview=[
        ("What is a decorator in TypeScript?",
         "A function applied with `@` to a class or class member at definition time. It receives the original and a context object and can return a replacement — wrapping a method with logging or caching, transforming a field's initial value, or registering a class. TypeScript 5.0 implements the standard TC39 decorators; the older `experimentalDecorators` form has a different signature."),
        ("How would you write a method decorator?",
         "A generic function `(target: (this: This, ...args: Args) => R, context: ClassMethodDecoratorContext<This, …>)` that returns a `function (this: This, ...args: Args): R` wrapper, calling `target.call(this, ...args)`. The generics keep the method's exact signature, and the `function` wrapper preserves `this`."),
        ("Standard vs experimental decorators?",
         "Experimental decorators receive `(target, key, descriptor)`, support parameter decorators and emit metadata with a flag — Angular and NestJS were built on them. Standard decorators receive `(value, context)`, have no parameter decorators, and follow the JavaScript proposal. New code should use the standard form unless a framework requires the legacy one."),
    ],
)


_chapter(
    "ts_iterator_helpers", "TS: Runtime & Architecture",
    "Iterator Helpers",
    "ES2025's lazy iterator methods — `map`, `filter`, `take`, `drop`, `flatMap`, `reduce`, `toArray` and friends on every iterator — plus `Iterator.from` and making your own classes iterable.",
    "Arrays have had `map` and `filter` forever, but they're eager: each step builds a whole new array. ES2025 adds the same methods to *iterators* — the thing `Map.keys()`, `Set.values()`, generators and `array.values()` return — and they are lazy: nothing runs until you ask for values, and `take(n)` stops the pipeline early. That makes infinite sequences, large files and early exits cheap, with the vocabulary you already know.",
    "Java streams are the closest thing: lazy, chained, with terminal operations. The difference is that JavaScript iterator helpers are methods on the iterators you already have — no `.stream()` call — and an iterator, like a Java stream, can be consumed only once.",
    why=r"""
You have a `Map` of 100,000 users and want the first five admins' names. The
familiar way — `[...users.values()].filter(isAdmin).map(u => u.name).slice(0, 5)`
— copies all 100,000 into an array, filters all of them, maps every admin, and
only then throws most of it away.

Iterator helpers do the same thing lazily:
`users.values().filter(isAdmin).map(u => u.name).take(5).toArray()` looks at
users one at a time and stops as soon as it has five. Same vocabulary, a
fraction of the work — and it works on infinite sources, which arrays never can.
""",
    idea=r"""
**Where they live.** Every built-in iterator — from `array.values()`,
`map.entries()`, `set.keys()`, `string[Symbol.iterator]()`, a generator — has
these methods (Node 22+, `lib: es2025` from TypeScript 6.0; `esnext.iterator`
before that):

| lazy (return an iterator) | eager (consume it) |
|---|---|
| `map`, `filter`, `take(n)`, `drop(n)`, `flatMap` | `toArray`, `reduce`, `forEach`, `some`, `every`, `find` |

**Lazy means pull-based.** Each value flows through the whole chain before the
next is read. Nothing happens until an eager method (or `for…of`) pulls.

**`Iterator.from(x)`** wraps anything iterable (or an iterator-like object) so
the helpers are available on it — handy for your own iterables.

**Single use.** An iterator is a cursor. Once `toArray()` has consumed it, it's
empty; call the source again for a fresh one.

**Your own classes.** Implement `[Symbol.iterator]()` — often as a generator
method `*[Symbol.iterator]()` — and the class works with `for…of`, spread, and
(through `Iterator.from` or by returning a built-in iterator) the helpers:

```ts
class Range implements Iterable<number> {
  constructor(readonly from: number, readonly to: number) {}
  *[Symbol.iterator]() { for (let i = this.from; i < this.to; i++) yield i; }
}
Iterator.from(new Range(0, 1_000_000)).filter(isPrime).take(3).toArray();
```

**Types.** The helpers are typed on `IteratorObject<T>` (what built-in
iterators are); a plain `Iterable<T>` doesn't have them — convert with
`Iterator.from`. `take` and `drop` return iterators of the same `T`; `map`
changes it.
""",
    examples=[
        ("Lazy: only as much work as needed",
         r"""
const users = new Map([
  [1, { name: "ana", admin: true }],
  [2, { name: "bo", admin: false }],
  [3, { name: "cy", admin: true }],
  [4, { name: "dee", admin: true }],
]);
let checked = 0;
const firstTwoAdmins = users
  .values()
  .filter((u) => {
    checked++;
    return u.admin;
  })
  .map((u) => u.name.toUpperCase())
  .take(2)
  .toArray();
console.log(firstTwoAdmins.join(", "));
console.log(`checked ${checked} of ${users.size}`);
""", [""],
         "The pipeline stopped after the third user: `take(2)` had what it needed, so `dee` was never looked at. An array chain would have filtered all four."),
        ("An infinite source, safely",
         r"""
function* naturals(): Generator<number> {
  for (let n = 1; ; n++) yield n;
}
const isPrime = (n: number) => {
  if (n < 2) return false;
  for (let d = 2; d * d <= n; d++) if (n % d === 0) return false;
  return true;
};
console.log(naturals().filter(isPrime).take(8).toArray().join(" "));
console.log(naturals().drop(10).map((n) => n * n).take(3).toArray().join(" "));
console.log(naturals().take(100).reduce((a, b) => a + b, 0));
""", [""],
         "`naturals()` never ends, but every pipeline has a `take`, so each pulls a finite number of values. `[...naturals()]` would hang."),
        ("An iterable class, with the helpers",
         r"""
class Countdown implements Iterable<number> {
  readonly from: number;
  constructor(from: number) {
    this.from = from;
  }
  *[Symbol.iterator](): Generator<number> {
    for (let i = this.from; i > 0; i--) yield i;
  }
}
const c = new Countdown(5);
console.log([...c].join(","));
for (const n of c) if (n % 2 === 0) console.log("even " + n);
console.log(Iterator.from(c).map((n) => n * 10).toArray().join(","));
""", [""],
         "A generator method makes the class iterable — each `for…of` or spread gets a fresh iterator. `Iterator.from` gives access to the helpers."),
        ("An iterator is used up",
         r"""
const words = ["alpha", "beta", "gamma"];
const upper = words.values().map((w) => w.toUpperCase());
console.log(upper.toArray().join(" "));
console.log(`again: [${upper.toArray().join(" ")}]`);
const fresh = () => words.values().map((w) => w.toUpperCase());
console.log(fresh().toArray().length, fresh().toArray().length);
""", [""],
         "The second `toArray()` on the same iterator finds it empty. When you need to iterate twice, keep a function (or the array) that creates a new iterator each time."),
    ],
    errors=[
        (2339, r"""
function firstTwo(items: Iterable<number>): number[] {
  return items.take(2).toArray();
}
""", "A plain `Iterable<T>` only promises `[Symbol.iterator]()`; the helpers live on iterator objects. Wrap it: `Iterator.from(items).take(2).toArray()`."),
        (2488, r"""
const point = { x: 1, y: 2 };
for (const v of point) console.log(v);
""", "An ordinary object isn't iterable. Iterate `Object.values(point)` — or give a class a `[Symbol.iterator]` method."),
    ],
    pitfalls=[
        ("Side effects run lazily",
         r"""
const logged: string[] = [];
const names = ["ana", "bo", "cy", "dee"];
const firstTwo = names.map((n) => {
  logged.push(n);
  return n.toUpperCase();
}).slice(0, 2);
console.log(firstTwo.join(" "), "| processed:", logged.join(","));
""",
         r"""
const logged: string[] = [];
const names = ["ana", "bo", "cy", "dee"];
const firstTwo = names.values().map((n) => {
  logged.push(n);
  return n.toUpperCase();
}).take(2).toArray();
console.log(firstTwo.join(" "), "| processed:", logged.join(","));
""",
         "Not a bug either way — but a real difference. The array `map` processed every name before `slice` threw two away; the iterator pipeline processed exactly two. If the callback has side effects (logging, I/O, counting), lazy and eager chains behave differently."),
        ("Reusing a consumed iterator",
         r"""
const scores = new Map([["ana", 90], ["bo", 70]]);
const values = scores.values();
const max = Math.max(...values);
const total = values.reduce((a, b) => a + b, 0);
console.log(`max ${max}, total ${total}`);
""",
         r"""
const scores = new Map([["ana", 90], ["bo", 70]]);
const max = Math.max(...scores.values());
const total = scores.values().reduce((a, b) => a + b, 0);
console.log(`max ${max}, total ${total}`);
""",
         "The spread consumed `values`, so `reduce` saw nothing and returned its initial `0`. Ask the `Map` for a fresh iterator each time."),
        ("Helpers on a plain iterable",
         (r"""
function evens(items: Iterable<number>): number[] {
  return items.filter((n) => n % 2 === 0).toArray();
}
console.log(evens(new Set([1, 2, 3, 4])).join(","));
""", 2339),
         r"""
function evens(items: Iterable<number>): number[] {
  return Iterator.from(items).filter((n) => n % 2 === 0).toArray();
}
console.log(evens(new Set([1, 2, 3, 4])).join(","));
""",
         "`Iterable<number>` could be anything with `[Symbol.iterator]`; `Iterator.from` turns it into an iterator object with the helpers."),
    ],
    later=[
        "**Week 24 — Generic data structures.** Iterable `LinkedList<T>` and tree iterators with `yield*`.",
        "**Week 26 — Async iteration.** The same ideas for values that arrive over time: `for await`, async generators.",
    ],
    exercises=[
        _drill("ts_iterator_helpers-first", "The first matches, lazily",
               "The input is a list of words. Replace `____` with a lazy pipeline over `words.values()` that keeps words longer than 3 letters, upper-cases them, and stops after 3.",
               r"""
import * as fs from "fs";
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const picked = words.values().filter((w) => w.length > 3).map((w) => w.toUpperCase()).take(3).toArray();
console.log(picked.join(" ") || "(none)");
console.log(picked.length);
""", ["words.values().filter((w) => w.length > 3).map((w) => w.toUpperCase()).take(3).toArray()"],
               ["the quick brown foxes jumped over lazy dogs", "a bb ccc", "longer words here"],
               hint="`values()` gives an iterator; chain `filter`, `map`, `take`, then `toArray()`."),
        _drill("ts_iterator_helpers-range", "Make a class iterable",
               "Replace `____` with the generator method that makes `Range` iterable, yielding `from`, `from + step`, … while below `to`.",
               r"""
import * as fs from "fs";
class Range implements Iterable<number> {
  readonly from: number;
  readonly to: number;
  readonly step: number;
  constructor(from: number, to: number, step: number) {
    this.from = from;
    this.to = to;
    this.step = step;
  }
  *[Symbol.iterator](): Generator<number> {
    for (let i = this.from; i < this.to; i += this.step) yield i;
  }
}
const [from = 0, to = 0, step = 1] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const r = new Range(from, to, step);
console.log([...r].join(" ") || "(empty)");
console.log(Iterator.from(r).reduce((a, b) => a + b, 0));
""", ["*[Symbol.iterator](): Generator<number> {\n    for (let i = this.from; i < this.to; i += this.step) yield i;\n  }"],
               ["0 10 3", "5 5 1", "1 4 1"],
               hint="A generator method named `[Symbol.iterator]`, with a `for` loop that `yield`s."),
        _chal("ts_iterator_helpers-log", "Scan a log lazily", "Medium",
              "Each input line is a log entry `<level> <message…>`. Using iterator helpers over `lines.values()` (no intermediate arrays until the end), print the first 2 `ERROR` messages, then `warnings: <n>` (with `reduce`), then `has fatal: <bool>` (with `some`), then the 3rd line after skipping the first 2 (`drop`) or `none`.",
              r"""
const lines = input.split("\n").map((l) => l.trim());
const level = (l: string) => l.split(" ")[0] ?? "";
const message = (l: string) => l.slice(l.indexOf(" ") + 1);
const errors = lines.values().filter((l) => level(l) === "ERROR").map(message).take(2).toArray();
for (const e of errors) console.log(e);
console.log(`warnings: ${lines.values().reduce((n, l) => n + (level(l) === "WARN" ? 1 : 0), 0)}`);
console.log(`has fatal: ${lines.values().some((l) => level(l) === "FATAL")}`);
console.log(lines.values().drop(2).take(1).toArray()[0] ?? "none");
""", ["INFO boot\nWARN slow disk\nERROR db down\nINFO retry\nERROR db down again\nERROR third\nWARN hot", "FATAL all bad", "INFO a\nINFO b"],
              hint="Each question gets a fresh `lines.values()` — an iterator is consumed by the first pipeline that reads it."),
    ],
    quiz=[
        _cq("Which of these is lazy?",
            "`it.map(f)` on an iterator", ["`arr.map(f)` on an array", "`it.toArray()`", "`it.reduce(f, 0)`"],
            "Iterator `map` returns a new iterator and runs nothing until pulled."),
        _cq("What does `take(n)` do to the pipeline?",
            "Stops pulling from the source after `n` values", ["Skips `n` values", "Sorts and takes the top `n`", "Copies `n` values into an array"],
            "It's what makes infinite sources safe."),
        _cq("You call `toArray()` twice on the same iterator. The second result?",
            "An empty array — the iterator was consumed", ["The same values again", "An error", "`undefined`"],
            "Iterators are single-use cursors."),
        _cq("How do you use the helpers on a value typed `Iterable<T>`?",
            "`Iterator.from(value)`", ["`[...value]`", "`value.iterator()`", "They're already there"],
            "`Iterable<T>` only promises `[Symbol.iterator]`."),
        _cq("How do you make a class work with `for…of`?",
            "Implement `[Symbol.iterator]()`, often as a generator method", ["Extend `Array`", "Add a `forEach` method", "Mark it `iterable`"],
            "`*[Symbol.iterator]() { … yield … }`."),
        _cq("Which call hangs?",
            "`[...naturals()]` for an infinite generator", ["`naturals().take(5).toArray()`", "`naturals().drop(5).take(1).toArray()`", "`naturals().find((n) => n > 5)`"],
            "Spreading tries to collect everything."),
    ],
    interview=[
        ("What are iterator helpers and why do they matter?",
         "ES2025 added `map`, `filter`, `take`, `drop`, `flatMap`, `reduce`, `toArray` and similar methods to iterator objects. Unlike array methods they're lazy — values are pulled one at a time through the chain, and `take` stops early — so you can process large or infinite sequences, or `Map`/`Set` views, without building intermediate arrays."),
        ("What's the difference between an iterable and an iterator?",
         "An iterable has a `[Symbol.iterator]()` method that returns an iterator; an iterator has `next()` and is a single-use cursor. Arrays, maps and strings are iterables — each loop asks for a fresh iterator. Generators are both, which is why a generator object can only be consumed once."),
        ("How would you make a custom collection iterable?",
         "Add a generator method `*[Symbol.iterator]()` that yields the elements. That gives `for…of`, spread and destructuring for free, and `Iterator.from(collection)` gives the lazy helpers."),
    ],
)


_M6_HEAP = r"""
class Heap<T> {
  readonly #items: T[] = [];
  readonly #compare: (a: T, b: T) => number;
  constructor(compare: (a: T, b: T) => number) {
    this.#compare = compare;
  }
  get size(): number {
    return this.#items.length;
  }
  peek(): T | undefined {
    return this.#items[0];
  }
  push(item: T): void {
    const a = this.#items;
    a.push(item);
    let i = a.length - 1;
    while (i > 0) {
      const parent = (i - 1) >> 1;
      const child = a[i] as T;
      const up = a[parent] as T;
      if (this.#compare(child, up) >= 0) break;
      a[i] = up;
      a[parent] = child;
      i = parent;
    }
  }
  pop(): T | undefined {
    const a = this.#items;
    const top = a[0];
    const last = a.pop();
    if (a.length > 0 && last !== undefined) {
      a[0] = last;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1;
        const r = l + 1;
        let m = i;
        if (l < a.length && this.#compare(a[l] as T, a[m] as T) < 0) m = l;
        if (r < a.length && this.#compare(a[r] as T, a[m] as T) < 0) m = r;
        if (m === i) break;
        const tmp = a[i] as T;
        a[i] = a[m] as T;
        a[m] = tmp;
        i = m;
      }
    }
    return top;
  }
}
"""

_chapter(
    "ts_heap_pq", "TS: Data Structures",
    "Heaps & Priority Queues",
    "A generic binary heap with a comparator: `push` and `pop` in O(log n), always handing out the smallest item — the structure behind priority queues, k-smallest, merging sorted lists and schedulers.",
    "JavaScript has no built-in priority queue, so interviews and real schedulers need one written by hand. A binary heap keeps an array in *heap order* — every parent no larger than its children — so the minimum is always at index 0; `push` bubbles a new item up and `pop` sifts the last item down, each touching only O(log n) slots. Made generic over `T` with a comparator `(a, b) => number` (the same contract as `sort`), one class serves numbers, tasks, events and anything else.",
    "Java ships `PriorityQueue<E>` with a `Comparator<E>`; this chapter builds the same thing, because JavaScript doesn't have one. The comparator contract is identical: negative means `a` comes first.",
    why=r"""
Many problems need "the smallest thing so far" over and over while things are
added: the next task to run, the nearest unvisited city, the next line to merge
from k sorted files, the running median. Re-sorting an array after every insert
costs O(n log n) each time; scanning for the minimum costs O(n). A heap does both
operations in O(log n).

Interviewers ask for heaps constantly — top-k, merge k lists, task scheduling,
meeting rooms — and TypeScript gives you nothing to import. Writing a small,
generic, well-typed heap once, and knowing its comparator contract cold, is one
of the most reusable pieces of interview code you can own.
""",
    idea=r"""
**Heap order in an array.** Store a complete binary tree level by level: the
children of index `i` are `2i + 1` and `2i + 2`, its parent is `(i - 1) >> 1`.
The *heap property* — every parent compares ≤ its children — puts the minimum at
`items[0]`.

- **push:** append at the end, then swap it with its parent while it's smaller
  ("bubble up"). O(log n).
- **pop:** take `items[0]`, move the last item to the root, then swap it with
  its smaller child while a child is smaller ("sift down"). O(log n).
- **peek:** `items[0]`, O(1). Under `noUncheckedIndexedAccess` both `peek` and
  `pop` honestly return `T | undefined`.

**Generic with a comparator.** `class Heap<T>` takes
`compare: (a: T, b: T) => number` — negative if `a` should come out first —
exactly `Array.prototype.sort`'s contract. A max-heap is the same class with the
comparator reversed: `(a, b) => b - a`.

**Common patterns.**

| problem | heap |
|---|---|
| k smallest of n | max-heap of size k: push, and pop whenever it exceeds k |
| merge k sorted lists | min-heap of the current head of each list |
| scheduler | min-heap of `(time, seq, task)`, seq breaking ties |
| running median | a max-heap of the low half, a min-heap of the high half |

**Heaps aren't stable.** Equal items can come out in any order. When order
among equals matters (first-come-first-served), add an insertion counter to the
comparison.
""",
    examples=[
        ("Heap sort, from the generic class",
         _M6_HEAP + r"""
const h = new Heap<number>((a, b) => a - b);
for (const n of [5, 1, 8, 3, 9, 2]) h.push(n);
const out: number[] = [];
for (let x = h.pop(); x !== undefined; x = h.pop()) out.push(x);
console.log(out.join(" "));

const words = new Heap<string>((a, b) => b.length - a.length || a.localeCompare(b));
for (const w of ["pear", "fig", "banana", "kiwi"]) words.push(w);
console.log(words.pop(), words.pop(), words.size);
""", [""],
         "The same class, two element types, two orders: ascending numbers, and words longest-first (alphabetical on ties). The comparator is the only thing that changes."),
        ("k smallest with a bounded max-heap",
         _M6_HEAP + r"""
function kSmallest(xs: readonly number[], k: number): number[] {
  const worstFirst = new Heap<number>((a, b) => b - a);
  for (const x of xs) {
    worstFirst.push(x);
    if (worstFirst.size > k) worstFirst.pop();
  }
  const out: number[] = [];
  for (let x = worstFirst.pop(); x !== undefined; x = worstFirst.pop()) out.push(x);
  return out.reverse();
}
console.log(kSmallest([9, 4, 7, 1, 8, 2, 6], 3).join(" "));
console.log(kSmallest([5], 3).join(" "));
""", [""],
         "The heap never holds more than k items, so this is O(n log k) — much better than sorting everything when k is small. Its top is the largest of the k smallest, the one to evict."),
        ("A scheduler with stable ties",
         _M6_HEAP + r"""
type Job = { name: string; priority: number; seq: number };
const queue = new Heap<Job>((a, b) => a.priority - b.priority || a.seq - b.seq);
let seq = 0;
for (const [name, priority] of [["backup", 2], ["email", 1], ["report", 2], ["alert", 0], ["cleanup", 2]] as const) {
  queue.push({ name, priority, seq: seq++ });
}
const order: string[] = [];
for (let j = queue.pop(); j !== undefined; j = queue.pop()) order.push(`${j.name}(${j.priority})`);
console.log(order.join(" "));
""", [""],
         "Priority 2 has three jobs; the `seq` tie-break makes them run in arrival order. Without it a heap may hand them out in any order."),
        ("Merge k sorted lists",
         _M6_HEAP + r"""
function mergeSorted(lists: readonly (readonly number[])[]): number[] {
  const heads = new Heap<{ value: number; list: number; index: number }>((a, b) => a.value - b.value);
  lists.forEach((l, list) => {
    const first = l[0];
    if (first !== undefined) heads.push({ value: first, list, index: 0 });
  });
  const out: number[] = [];
  for (let h = heads.pop(); h !== undefined; h = heads.pop()) {
    out.push(h.value);
    const next = lists[h.list]?.[h.index + 1];
    if (next !== undefined) heads.push({ value: next, list: h.list, index: h.index + 1 });
  }
  return out;
}
console.log(mergeSorted([[1, 4, 9], [2, 3, 10], [], [5]]).join(" "));
""", [""],
         "The heap holds one candidate per list — at most k items — so merging n values costs O(n log k)."),
    ],
    errors=[
        (2322, r"""
declare class Heap<T> {
  constructor(compare: (a: T, b: T) => number);
  push(item: T): void;
  pop(): T | undefined;
}
const h = new Heap<number>((a, b) => a - b);
h.push(3);
const smallest: number = h.pop();
""", "`pop` on an empty heap has nothing to return, so its type says `number | undefined`. Handle the empty case (`?? …`, or loop `while (x !== undefined)`)."),
        (2345, r"""
declare class Heap<T> {
  constructor(compare: (a: T, b: T) => number);
}
const byLength = (a: string, b: string) => a.length - b.length;
const h = new Heap<number>(byLength);
""", "The comparator must compare the heap's element type. A `Heap<number>` needs `(a: number, b: number) => number`."),
    ],
    pitfalls=[
        ("A comparator with the sign reversed",
         _M6_HEAP + r"""
const tasks = new Heap<number>((a, b) => b - a);
for (const due of [30, 10, 20]) tasks.push(due);
console.log("next due: " + tasks.pop());
""",
         _M6_HEAP + r"""
const tasks = new Heap<number>((a, b) => a - b);
for (const due of [30, 10, 20]) tasks.push(due);
console.log("next due: " + tasks.pop());
""",
         "`(a, b) => b - a` is a *max*-heap. The contract is `sort`'s: negative when `a` should come out first. Say it out loud before writing the comparator."),
        ("Ties in arbitrary order",
         _M6_HEAP + r"""
const q = new Heap<{ name: string; p: number }>((a, b) => a.p - b.p);
for (const name of ["a", "b", "c", "d", "e"]) q.push({ name, p: 1 });
const out: string[] = [];
for (let j = q.pop(); j !== undefined; j = q.pop()) out.push(j.name);
console.log(out.join(""));
""",
         _M6_HEAP + r"""
const q = new Heap<{ name: string; p: number; seq: number }>((a, b) => a.p - b.p || a.seq - b.seq);
["a", "b", "c", "d", "e"].forEach((name, seq) => q.push({ name, p: 1, seq }));
const out: string[] = [];
for (let j = q.pop(); j !== undefined; j = q.pop()) out.push(j.name);
console.log(out.join(""));
""",
         "All five have the same priority, and a heap isn't stable: they came out shuffled. Add an insertion counter to the comparison when equal items must keep their order."),
        ("A boolean comparator",
         (r"""
const xs = [3, 1, 2];
xs.sort((a, b) => a > b);
console.log(xs.join(","));
""", 2345),
         r"""
const xs = [3, 1, 2];
xs.sort((a, b) => a - b);
console.log(xs.join(","));
""",
         "A comparator returns a *number* (negative, zero, positive). `a > b` returns a boolean, which JavaScript would silently turn into 0 or 1 — an inconsistent order. TypeScript refuses it."),
    ],
    later=[
        "**Week 24 — Problem set.** Running median with two heaps, meeting rooms, a task scheduler.",
        "**DSA curriculum, stage 5.** Heaps and the problems built on them (`/library`).",
        "**Week 26 — Async.** A scheduler over a simulated clock is a heap keyed by time.",
    ],
    exercises=[
        _drill("ts_heap_pq-max", "A max-heap from the same class",
               "`Heap<T>` is a min-heap by its comparator. Replace `____` with the comparator that makes `top` hand out the largest number first.",
               _M6_HEAP + r"""
import * as fs from "fs";
const top = new Heap<number>((a, b) => b - a);
for (const n of fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number)) top.push(n);
const firstThree = [top.pop(), top.pop(), top.pop()].filter((x) => x !== undefined);
console.log(firstThree.join(" "));
console.log(`left ${top.size}`);
""", ["(a, b) => b - a"],
               ["5 1 9 3 7", "2 2", "10 20 30 40"],
               hint="Negative when `a` should come out first — so when `a` is *larger*."),
        _drill("ts_heap_pq-kth", "The k-th largest",
               "Keep a min-heap of the k largest values seen so far. Replace `____` with the step that keeps it at k items.",
               _M6_HEAP + r"""
import * as fs from "fs";
const [kText = "1", line = ""] = fs.readFileSync(0, "utf8").trim().split("\n");
const k = Number(kText);
const best = new Heap<number>((a, b) => a - b);
for (const x of line.trim().split(/\s+/).map(Number)) {
  best.push(x);
  if (best.size > k) best.pop();
}
console.log(best.size < k ? "not enough values" : `k-th largest: ${best.peek()}`);
""", ["if (best.size > k) best.pop();"],
               ["3\n4 9 1 7 3 8", "1\n5 2", "4\n1 2"],
               hint="When the heap grows past k, remove its smallest."),
        _chal("ts_heap_pq-scheduler", "Run jobs by priority, then arrival", "Medium",
              "Each input line is `add <name> <priority>` (lower runs first) or `run <n>` (run up to n jobs). For each job run print `run <name>`; if the queue empties early print `idle`. Equal priorities run in the order they were added. Finish with `pending <names by the order they'd run>` or `pending none`. Write (or reuse) a generic heap with a comparator.",
              _M6_HEAP.strip("\n") + r"""
type Job = { name: string; priority: number; seq: number };
const queue = new Heap<Job>((a, b) => a.priority - b.priority || a.seq - b.seq);
let seq = 0;
for (const line of input.split("\n")) {
  const [cmd = "", a = "", b = "0"] = line.trim().split(/\s+/);
  if (cmd === "add") queue.push({ name: a, priority: Number(b), seq: seq++ });
  else if (cmd === "run") {
    for (let i = 0; i < Number(a); i++) {
      const job = queue.pop();
      if (job === undefined) {
        console.log("idle");
        break;
      }
      console.log(`run ${job.name}`);
    }
  }
}
const pending: string[] = [];
for (let j = queue.pop(); j !== undefined; j = queue.pop()) pending.push(j.name);
console.log(`pending ${pending.join(" ") || "none"}`);
""", ["add backup 2\nadd email 1\nadd report 2\nrun 2\nadd alert 0\nrun 5\nadd late 3", "run 1\nadd x 5\nadd y 5"],
              hint="Compare by priority, then by an arrival counter."),
    ],
    quiz=[
        _cq("Where is the smallest item in a min-heap stored in an array?",
            "At index 0", ["At the last index", "In the middle", "Anywhere"], "The heap property puts the minimum at the root."),
        _cq("What are the children of index `i`?",
            "`2i + 1` and `2i + 2`", ["`i + 1` and `i + 2`", "`2i` and `2i + 1`", "`i / 2`"], "Its parent is `(i - 1) >> 1`."),
        _cq("Cost of `push` and `pop`?",
            "O(log n) each", ["O(1) each", "O(n) each", "O(n log n) each"], "Each walks one root-to-leaf path."),
        _cq("How do you get the k smallest of n values in O(n log k)?",
            "A max-heap capped at k items, popping when it exceeds k", ["Sort, then slice", "A min-heap of all n", "A `Set`"],
            "Its top is the largest kept value — the one to evict."),
        _cq("Are heaps stable for equal priorities?",
            "No — add an insertion counter to the comparison if order matters", ["Yes, always", "Only for numbers", "Only when k = 1"],
            "Swaps reorder equal items."),
        _cq("What does the comparator `(a, b) => b - a` produce?",
            "A max-heap", ["A min-heap", "A random order", "An error"], "Negative when `a` is larger, so larger items come out first."),
    ],
    interview=[
        ("How would you implement a priority queue in TypeScript?",
         "A generic `Heap<T>` over an array with a comparator `(a, b) => number`: push appends and bubbles up, pop moves the last element to the root and sifts down, both O(log n); peek reads index 0. `pop` and `peek` return `T | undefined`. A max-heap is the same class with the comparator flipped."),
        ("Find the k largest elements in a stream.",
         "Keep a min-heap of size k: push each element and pop whenever the size exceeds k. The heap then holds the k largest, with the k-th largest at the top. O(n log k) time, O(k) space — better than sorting when k is small, and it works on an unbounded stream."),
        ("How do you merge k sorted lists?",
         "Push the head of each list into a min-heap keyed by value (remembering which list it came from); repeatedly pop the smallest, append it, and push the next element from the same list. O(n log k) for n total elements."),
    ],
)


_chapter(
    "ts_resource_management", "TS: Robustness",
    "Resource Management with `using`",
    "`using` and `await using` declarations, `Symbol.dispose` and `Symbol.asyncDispose`, and `DisposableStack` — deterministic cleanup that runs however a block exits.",
    "A resource — a file handle, a lock, a transaction, a timer — must be released exactly once, even when the code using it returns early or throws. `try`/`finally` does that but scatters cleanup and gets the order wrong as resources multiply. `using x = acquire()` (TypeScript 5.2, Node 24) calls `x[Symbol.dispose]()` when the enclosing block exits, in reverse order of acquisition; `await using` does the same for async cleanup; `DisposableStack` collects cleanups that don't fit one variable.",
    "This is Java's try-with-resources and `AutoCloseable`, and C#'s `using`: the resource declares how to close itself, and the language guarantees the call. JavaScript's version is a declaration rather than a block, so several resources in one scope close in reverse order automatically.",
    why=r"""
Cleanup bugs are quiet. A function opens a connection, something throws, and the
connection stays open; a lock is taken and an early `return` skips the release;
three resources are closed by hand in the wrong order. None of these fail a
simple test — they leak slowly in production.

`try`/`finally` fixes each case, one hand-written block at a time. The `using`
declaration moves the knowledge of *how* to release a resource into the
resource itself, and the guarantee of *when* into the language: at the end of the
block, in reverse order, whatever happened.
""",
    idea=r"""
**Disposable.** An object is disposable if it has a `[Symbol.dispose]()`
method (the `Disposable` interface). Async-disposable objects have
`[Symbol.asyncDispose](): Promise<void>` (`AsyncDisposable`).

**`using`.**

```ts
{
  using conn = openConnection();   // conn[Symbol.dispose]() runs at block end
  using tx = conn.begin();         // tx is disposed first, then conn
  tx.write("…");
}                                  // …even if write threw, or we returned early
```

- Disposal happens when the block exits — normally, by `return`, `break` or
  exception.
- Several `using` declarations dispose in **reverse** order: last acquired,
  first released.
- `null` and `undefined` are allowed and skipped (an optional resource).
- If the block threw *and* a dispose throws, you get a `SuppressedError` whose
  `.error` is the dispose error and `.suppressed` is the original.

**`await using`** awaits `[Symbol.asyncDispose]()` at block exit; it's only
allowed in async functions and at a module's top level.

**`DisposableStack`** is a disposable that holds other cleanups:
`stack.use(resource)`, `stack.defer(() => …)`, `stack.adopt(value, release)`.
Disposing the stack runs them in reverse. `stack.move()` transfers ownership
to a new stack — how a constructor that acquires several resources hands them to
the object only if all acquisitions succeeded.

**Availability.** TypeScript 5.2+ with the `esnext.disposable` library (in this
app's checker), and natively in Node 24 — which is what runs these examples.
""",
    examples=[
        ("Acquired in order, released in reverse",
         r"""
class Resource implements Disposable {
  readonly name: string;
  constructor(name: string) {
    this.name = name;
    console.log("open " + name);
  }
  [Symbol.dispose](): void {
    console.log("close " + this.name);
  }
}
function work(): string {
  using db = new Resource("db");
  using file = new Resource("file");
  console.log(`using ${db.name} and ${file.name}`);
  return "done";
}
console.log(work());
""", [""],
         "`file` was acquired last, so it's released first; both are released before `work`'s return value reaches the caller."),
        ("Cleanup on every exit path",
         r"""
class Lock implements Disposable {
  static held = 0;
  constructor() {
    Lock.held++;
  }
  [Symbol.dispose](): void {
    Lock.held--;
  }
}
function transfer(amount: number): string {
  using lock = new Lock();
  if (amount <= 0) return "rejected";
  if (amount > 100) throw new Error("limit exceeded");
  return `moved ${amount} while holding ${Lock.held} lock`;
}
for (const amount of [50, -1, 500]) {
  try {
    console.log(transfer(amount));
  } catch (e) {
    console.log("error: " + (e instanceof Error ? e.message : String(e)));
  }
  console.log(`locks held afterwards: ${Lock.held}`);
}
""", [""],
         "An early `return` and a `throw` both release the lock — there is no path out of the block that skips `[Symbol.dispose]`."),
        ("A stack of cleanups",
         r"""
function setup(fail: boolean): DisposableStack {
  using stack = new DisposableStack();
  stack.defer(() => console.log("  undo: stop server"));
  console.log("  start server");
  stack.defer(() => console.log("  undo: close cache"));
  console.log("  open cache");
  if (fail) throw new Error("config missing");
  return stack.move();
}
for (const fail of [true, false]) {
  console.log(fail ? "setup that fails:" : "setup that succeeds:");
  try {
    using app = setup(fail);
    console.log("  running");
  } catch (e) {
    console.log("  failed: " + (e instanceof Error ? e.message : String(e)));
  }
}
""", [""],
         "On failure the local `stack` undoes everything done so far. On success, `move()` hands the cleanups to the caller's `app`, which releases them when *its* block ends."),
        ("Async cleanup with `await using`",
         r"""
class Connection implements AsyncDisposable {
  readonly id: number;
  constructor(id: number) {
    this.id = id;
  }
  async query(sql: string): Promise<string> {
    return `#${this.id}: ${sql.toUpperCase()}`;
  }
  async [Symbol.asyncDispose](): Promise<void> {
    await Promise.resolve();
    console.log(`connection ${this.id} closed`);
  }
}
async function report(): Promise<void> {
  await using conn = new Connection(7);
  console.log(await conn.query("select 1"));
}
await report();
console.log("after report");
""", [""],
         "`await using` waits for the async close to finish before `report` completes, so \"closed\" always prints before \"after report\"."),
    ],
    errors=[
        (2850, r"""
const handle = { close() {} };
function read() {
  using h = handle;
}
""", "`using` needs an object with `[Symbol.dispose]()`. An object with a `close()` method isn't disposable until it says how — wrap it: `using h = { [Symbol.dispose]: () => handle.close() }`."),
        (2852, r"""
function read(conn: AsyncDisposable) {
  await using c = conn;
}
""", "`await using` waits for async cleanup, so it's only allowed where `await` is: in async functions and at a module's top level."),
    ],
    pitfalls=[
        ("Cleanup skipped by an exception",
         r"""
const log: string[] = [];
function risky(fail: boolean): void {
  log.push("open");
  if (fail) throw new Error("boom");
  log.push("close");
}
try {
  risky(true);
} catch {
  log.push("caught");
}
console.log(log.join(", "));
""",
         r"""
const log: string[] = [];
function risky(fail: boolean): void {
  using _handle = { [Symbol.dispose]: () => log.push("close") };
  log.push("open");
  if (fail) throw new Error("boom");
}
try {
  risky(true);
} catch {
  log.push("caught");
}
console.log(log.join(", "));
""",
         "The close sat after the code that threw, so it never ran. With `using`, the release happens on the way out — before the caller's `catch` even runs."),
        ("Returning a resource you `using`-ed",
         r"""
class File implements Disposable {
  open = true;
  read(): string {
    return this.open ? "contents" : "(read after close)";
  }
  [Symbol.dispose](): void {
    this.open = false;
  }
}
function openFile(): File {
  using f = new File();
  return f;
}
const f = openFile();
console.log(f.read());
""",
         r"""
class File implements Disposable {
  open = true;
  read(): string {
    return this.open ? "contents" : "(read after close)";
  }
  [Symbol.dispose](): void {
    this.open = false;
  }
}
function openFile(): File {
  return new File();
}
{
  using f = openFile();
  console.log(f.read());
}
""",
         "`using` ties the resource's lifetime to the block, so returning it hands back a closed file. The function that *creates* a resource returns it plainly; the caller that *uses* it declares `using`."),
        ("`using` on an async-only resource",
         (r"""
const conn: AsyncDisposable = { async [Symbol.asyncDispose]() { console.log("closed"); } };
async function run(): Promise<void> {
  using c = conn;
  console.log("working");
}
await run();
""", 2850),
         r"""
const conn: AsyncDisposable = { async [Symbol.asyncDispose]() { console.log("closed"); } };
async function run(): Promise<void> {
  await using c = conn;
  console.log("working");
}
await run();
""",
         "An object with only `[Symbol.asyncDispose]` can't be released synchronously; the compiler insists on `await using`."),
    ],
    later=[
        "**Week 25 — Errors.** `SuppressedError`, and why cleanup must not hide the original failure.",
        "**Week 26 — Cancellation.** Removing listeners and clearing timers when an operation is aborted — natural disposables.",
    ],
    exercises=[
        _drill("ts_resource_management-dispose", "Make it disposable",
               "`Timer` should report its elapsed ticks when released. Replace `____` with the method name that `using` calls.",
               r"""
import * as fs from "fs";
class Timer implements Disposable {
  readonly label: string;
  ticks = 0;
  constructor(label: string) {
    this.label = label;
  }
  tick(): void {
    this.ticks++;
  }
  [Symbol.dispose](): void {
    console.log(`${this.label}: ${this.ticks} ticks`);
  }
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [label = "", n = "0"] = line.trim().split(/\s+/);
  using t = new Timer(label);
  for (let i = 0; i < Number(n); i++) t.tick();
}
console.log("all timers released");
""", ["[Symbol.dispose]"],
               ["a 3\nb 0", "solo 5"],
               hint="The well-known symbol `Symbol.dispose`, as a computed method name."),
        _drill("ts_resource_management-stack", "Undo on failure",
               "Replace `____` with the call that registers the rollback for each step on the stack, so a failing step undoes every earlier step in reverse.",
               r"""
import * as fs from "fs";
function migrate(steps: string[]): string {
  using stack = new DisposableStack();
  for (const step of steps) {
    if (step.startsWith("!")) return `failed at ${step.slice(1)}`;
    console.log("apply " + step);
    stack.defer(() => console.log("rollback " + step));
  }
  stack.move();
  return "committed";
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) console.log(migrate(line.trim().split(/\s+/)));
""", ['stack.defer(() => console.log("rollback " + step));'],
               ["users posts !index", "a b"],
               hint="`stack.defer(fn)` registers a cleanup; `move()` at the end keeps them from running on success."),
        _chal("ts_resource_management-pool", "A connection pool that always gets its connections back", "Medium",
              "A pool has 2 connections. Each input line is a job: a list of words; the job borrows a connection with `using`, prints `job <n> on conn <id>: <words upper-cased>`, and — if a word is `crash` — throws before finishing (print `job <n> failed`). Borrowing when none are free prints `job <n> waiting` (and the job is skipped). After each job print `free <k>`. A borrowed connection must be returned on every path.",
              r"""
class Pool {
  readonly #free: number[] = [1, 2];
  borrow(): (Disposable & { id: number }) | undefined {
    const id = this.#free.shift();
    if (id === undefined) return undefined;
    return { id, [Symbol.dispose]: () => void this.#free.push(id) };
  }
  get free(): number {
    return this.#free.length;
  }
}
const pool = new Pool();
function run(n: number, words: string[]): void {
  using conn = pool.borrow();
  if (conn === undefined) {
    console.log(`job ${n} waiting`);
    return;
  }
  if (words.includes("crash")) throw new Error("crash");
  console.log(`job ${n} on conn ${conn.id}: ${words.join(" ").toUpperCase()}`);
}
input.split("\n").forEach((line, i) => {
  try {
    run(i + 1, line.trim().split(/\s+/));
  } catch {
    console.log(`job ${i + 1} failed`);
  }
  console.log(`free ${pool.free}`);
});
""", ["hello world\ncrash now\nlast one", "a\nb\nc"],
              hint="`using` accepts `undefined`, so an unavailable connection needs no special case in the cleanup."),
    ],
    quiz=[
        _cq("When is `x[Symbol.dispose]()` called for `using x = …`?",
            "When the enclosing block exits — normally, by return, or by exception", ["Immediately", "At program exit", "When `x` is garbage collected"],
            "Deterministic, like `finally`."),
        _cq("Two `using` declarations in one block are disposed in which order?",
            "Reverse order of declaration", ["Declaration order", "Alphabetical", "Unspecified"], "Last acquired, first released."),
        _cq("What does `using x = undefined` do?",
            "Nothing at block exit — `null` and `undefined` are allowed and skipped", ["Throws", "Is a compile error", "Disposes the enclosing object"],
            "Handy for optional resources."),
        _cq("Where is `await using` allowed?",
            "In async functions and at a module's top level", ["Anywhere", "Only in classes", "Only in generators"], "Wherever `await` is."),
        _cq("What is `DisposableStack.prototype.move()` for?",
            "Transferring the collected cleanups to a new stack so the current one won't run them",
            ["Reordering cleanups", "Disposing twice", "Moving a resource between threads"],
            "Used when setup succeeds and ownership passes to the caller."),
        _cq("A block throws and then a dispose also throws. What propagates?",
            "A `SuppressedError` holding both", ["Only the first error", "Only the dispose error", "Nothing"], "`.error` is the dispose error, `.suppressed` the original."),
    ],
    interview=[
        ("What problem does `using` solve?",
         "Deterministic cleanup. `using x = acquire()` guarantees `x[Symbol.dispose]()` runs when the block exits — on return, break or exception — and several resources are released in reverse order. It replaces nested `try`/`finally` blocks, like Java's try-with-resources."),
        ("How do you make a class usable with `using`?",
         "Implement `Disposable`: a `[Symbol.dispose]()` method that releases the resource (idempotently, ideally). For async cleanup implement `[Symbol.asyncDispose]()` returning a promise and use `await using`."),
        ("How do you clean up partially completed setup?",
         "Collect each step's undo in a `DisposableStack` held by `using`; if a later step throws, the stack undoes the earlier ones in reverse. On success, `stack.move()` transfers the cleanups to the object or caller that now owns the resources."),
    ],
)


_chapter(
    "ts_error_cause", "TS: Robustness",
    "Error Types, Causes & Aggregates",
    "`Error` subclasses with their own fields, the `cause` option that chains a low-level failure to the high-level one it caused, `AggregateError` for many failures at once, and catching `unknown` safely.",
    "An error message says what went wrong; its *type* says what kind of wrong, and its *cause* says why. Subclass `Error` (and set `name`) so callers can `instanceof` it and read typed fields; wrap a lower-level error with `new ConfigError(\"…\", { cause: e })` instead of losing it; throw an `AggregateError` when several independent things failed. Under `useUnknownInCatchVariables` every `catch` receives `unknown`, so narrowing is part of the design, not an afterthought.",
    "Java has checked exceptions, typed `catch` clauses and `getCause()`. TypeScript has none of the first two: a `catch` catches everything, as `unknown`. You get the same expressiveness from `instanceof` narrowing on your own subclasses — and `cause` is the direct equivalent of Java's exception chaining.",
    why=r"""
"Something went wrong" is not an error handling strategy. The code that catches
an error needs to decide: retry? show the user? give up? That decision depends
on *which* error it is — and a bare `Error` with a message string gives it
nothing reliable to decide on.

The other half of the problem appears when errors travel up through layers. The
database driver fails with "ECONNRESET", the repository turns that into "could
not load user", the handler turns *that* into "500 Internal Error". If each layer
throws a new error and drops the old one, whoever reads the log sees only the
top message. `cause` keeps the chain.
""",
    idea=r"""
**Subclass `Error` for kinds of failure.**

```ts
class ValidationError extends Error {
  override readonly name = "ValidationError";
  readonly field: string;
  constructor(field: string, message: string, options?: ErrorOptions) {
    super(message, options);
    this.field = field;
  }
}
```

- Set `name`: it's what `String(e)` and stack traces print.
- Add typed fields (`field`, `status`, `retryable`) — callers read them after
  `e instanceof ValidationError`.
- Pass `options` through to `super` so callers can attach a `cause`.

**Chain with `cause`.** `new LoadError("could not load user 7", { cause: e })`
keeps the original. Walk the chain with `while (err instanceof Error) { …; err =
err.cause; }`. Log the chain; show the user the top.

**`AggregateError`** carries many errors: `new AggregateError(errors,
"3 fields invalid")`, read back with `.errors`. `Promise.any` rejects with one
when every promise fails.

**Catch `unknown`.** Anything can be thrown — strings, numbers, objects — so a
`catch (e)` variable is `unknown` under `strict`. Narrow before use:
`e instanceof ValidationError` → typed fields; `e instanceof Error` → `message`;
otherwise `String(e)`. Rethrow what you don't handle.

**Throw, or return a `Result`?** Throw for failures the immediate caller can't
reasonably handle (bugs, lost connections). Return a `Result` (week 12's
discriminated union) for *expected* failures that the caller must handle (bad
input, not found) — the compiler then makes them deal with it. The week's
problem set has both.
""",
    examples=[
        ("A subclass callers can recognise",
         r"""
class ValidationError extends Error {
  override readonly name = "ValidationError";
  readonly field: string;
  constructor(field: string, message: string) {
    super(message);
    this.field = field;
  }
}
function parseAge(text: string): number {
  const n = Number(text);
  if (!Number.isInteger(n)) throw new ValidationError("age", `not a whole number: ${text}`);
  if (n < 0 || n > 150) throw new ValidationError("age", `out of range: ${n}`);
  return n;
}
for (const t of ["42", "4.5", "-3", "x"]) {
  try {
    console.log("age " + parseAge(t));
  } catch (e) {
    if (e instanceof ValidationError) console.log(`${e.name} on ${e.field}: ${e.message}`);
    else throw e;
  }
}
""", [""],
         "`instanceof ValidationError` narrows `e` from `unknown` to the subclass, so `e.field` is typed. Anything else is rethrown — this `catch` only handles what it understands."),
        ("A chain of causes",
         r"""
class ConfigError extends Error {
  override readonly name = "ConfigError";
}
class StartupError extends Error {
  override readonly name = "StartupError";
}
function readConfig(text: string): { port: number } {
  try {
    return JSON.parse(text) as { port: number };
  } catch (e) {
    throw new ConfigError("config is not valid JSON", { cause: e });
  }
}
function start(text: string): string {
  try {
    return `listening on ${readConfig(text).port}`;
  } catch (e) {
    throw new StartupError("server could not start", { cause: e });
  }
}
try {
  console.log(start('{"port": 80'));
} catch (e) {
  let err: unknown = e;
  for (let depth = 0; err instanceof Error; depth++) {
    console.log(`${"  ".repeat(depth)}${err.name}: ${err.message.split("\n")[0]?.split(" (")[0]}`);
    err = err.cause;
  }
}
""", [""],
         "Each layer adds what *it* knows and keeps the rest via `cause`. The top of the chain is for the user; the whole chain is for whoever debugs it."),
        ("Many failures at once",
         r"""
function validate(user: { name: string; email: string; age: number }): void {
  const errors: Error[] = [];
  if (user.name.trim() === "") errors.push(new Error("name is required"));
  if (!user.email.includes("@")) errors.push(new Error("email is invalid"));
  if (user.age < 13) errors.push(new Error("age must be at least 13"));
  if (errors.length > 0) throw new AggregateError(errors, `${errors.length} problems`);
}
for (const user of [{ name: "ana", email: "ana@x.io", age: 30 }, { name: "", email: "nope", age: 9 }]) {
  try {
    validate(user);
    console.log("ok");
  } catch (e) {
    if (!(e instanceof AggregateError)) throw e;
    console.log(e.message);
    for (const inner of e.errors) console.log(" - " + (inner instanceof Error ? inner.message : String(inner)));
  }
}
""", [""],
         "Reporting every problem at once — as the week 17 validators did — with a standard error type that carries the list."),
    ],
    errors=[
        (18046, r"""
try {
  JSON.parse("{");
} catch (e) {
  console.log(e.message);
}
""", "`e` is `unknown` under `strict`: JavaScript can throw anything. Narrow with `instanceof Error` first."),
        (2339, r"""
class HttpError extends Error {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}
function report(e: Error): number {
  return e.status;
}
""", "Only `HttpError` has `status`. Narrow first — `e instanceof HttpError ? e.status : 500` — or take an `HttpError` parameter."),
    ],
    pitfalls=[
        ("Throwing a string",
         r"""
function load(id: number): string {
  if (id < 0) throw `bad id ${id}`;
  return "user " + id;
}
try {
  load(-1);
} catch (e) {
  console.log("failed: " + (e as Error).message);
}
""",
         r"""
function load(id: number): string {
  if (id < 0) throw new RangeError(`bad id ${id}`);
  return "user " + id;
}
try {
  load(-1);
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         "A thrown string has no `message` (and no stack trace), and `as Error` hid that from the compiler. Throw `Error` objects, and narrow instead of asserting in `catch`."),
        ("A subclass that forgot its name",
         r"""
class NotFoundError extends Error {}
try {
  throw new NotFoundError("user 7");
} catch (e) {
  console.log(String(e));
}
""",
         r"""
class NotFoundError extends Error {
  override readonly name = "NotFoundError";
}
try {
  throw new NotFoundError("user 7");
} catch (e) {
  console.log(String(e));
}
""",
         "Without `name`, a subclass prints as a plain `Error` in logs and stack traces. `instanceof` still works — but the humans reading the log can't tell."),
        ("Rethrowing without the cause",
         r"""
function fetchUser(): never {
  throw new Error("ECONNRESET");
}
try {
  try {
    fetchUser();
  } catch {
    throw new Error("could not load user");
  }
} catch (e) {
  const cause = e instanceof Error && e.cause instanceof Error ? e.cause.message : "(none)";
  console.log(`${e instanceof Error ? e.message : e} — cause: ${cause}`);
}
""",
         r"""
function fetchUser(): never {
  throw new Error("ECONNRESET");
}
try {
  try {
    fetchUser();
  } catch (inner) {
    throw new Error("could not load user", { cause: inner });
  }
} catch (e) {
  const cause = e instanceof Error && e.cause instanceof Error ? e.cause.message : "(none)";
  console.log(`${e instanceof Error ? e.message : e} — cause: ${cause}`);
}
""",
         "Wrapping is right — the caller shouldn't see `ECONNRESET` as *its* error — but dropping the original makes the real failure invisible. `{ cause }` keeps it."),
    ],
    later=[
        "**Week 25 — `Result`.** Returning expected failures as values instead of throwing them.",
        "**Week 25 — Resource management.** `SuppressedError` when cleanup fails during an error.",
        "**Week 26 — Async.** `Promise.allSettled` and `Promise.any`'s `AggregateError`.",
    ],
    exercises=[
        _drill("ts_error_cause-narrow", "Handle only what you understand",
               "Replace `____` with the condition that recognises a `ParseError`, so its `line` field can be read; any other error is rethrown.",
               r"""
import * as fs from "fs";
class ParseError extends Error {
  override readonly name = "ParseError";
  readonly line: number;
  constructor(line: number, message: string) {
    super(message);
    this.line = line;
  }
}
function parse(lines: string[]): number {
  let total = 0;
  lines.forEach((l, i) => {
    const n = Number(l);
    if (!Number.isFinite(n)) throw new ParseError(i + 1, `not a number: ${l}`);
    total += n;
  });
  return total;
}
try {
  console.log("total " + parse(fs.readFileSync(0, "utf8").trim().split("\n")));
} catch (e) {
  if (e instanceof ParseError) console.log(`line ${e.line}: ${e.message}`);
  else throw e;
}
""", ["e instanceof ParseError"],
               ["1\n2\n3", "4\nfive\n6", "x"],
               hint="`instanceof` narrows `unknown` to the subclass."),
        _drill("ts_error_cause-chain", "Keep the cause",
               "Replace `____` so the high-level error keeps the low-level one as its cause; the program prints the whole chain.",
               r"""
import * as fs from "fs";
function readNumber(text: string): number {
  const n = Number(text);
  if (!Number.isFinite(n)) throw new Error(`"${text}" is not a number`);
  return n;
}
function loadPrice(text: string): number {
  try {
    return readNumber(text);
  } catch (e) {
    throw new Error("could not load price", { cause: e });
  }
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  try {
    console.log(`price ${loadPrice(line.trim())}`);
  } catch (e) {
    const parts: string[] = [];
    for (let err: unknown = e; err instanceof Error; err = err.cause) parts.push(err.message);
    console.log(parts.join(" <- "));
  }
}
""", ['throw new Error("could not load price", { cause: e });'],
               ["12.5\nabc", "-3"],
               hint="The second argument to `Error` is an options object with `cause`."),
        _chal("ts_error_cause-http", "Map errors to responses", "Medium",
              "Define `NotFoundError` and `ValidationError` (with a `field`), both with names. Each input line is a request `get <id>`: ids must be positive integers (`ValidationError` on field `id`), and only ids 1-3 exist (`NotFoundError`); id 7 simulates a bug by throwing a plain `Error(\"db exploded\")`. Handle each request and print `200 user <id>`, `400 <field>: <message>`, `404 <message>`, or — for anything unrecognised — `500 internal error (<name>: <message>)`.",
              r"""
class NotFoundError extends Error {
  override readonly name = "NotFoundError";
}
class ValidationError extends Error {
  override readonly name = "ValidationError";
  readonly field: string;
  constructor(field: string, message: string) {
    super(message);
    this.field = field;
  }
}
function getUser(idText: string): string {
  const id = Number(idText);
  if (!Number.isInteger(id) || id <= 0) throw new ValidationError("id", `must be a positive integer, got ${idText}`);
  if (id === 7) throw new Error("db exploded");
  if (id > 3) throw new NotFoundError(`no user ${id}`);
  return `user ${id}`;
}
for (const line of input.split("\n")) {
  const id = line.trim().split(/\s+/)[1] ?? "";
  try {
    console.log(`200 ${getUser(id)}`);
  } catch (e) {
    if (e instanceof ValidationError) console.log(`400 ${e.field}: ${e.message}`);
    else if (e instanceof NotFoundError) console.log(`404 ${e.message}`);
    else console.log(`500 internal error (${e instanceof Error ? `${e.name}: ${e.message}` : String(e)})`);
  }
}
""", ["get 2\nget 9\nget x\nget 7\nget 0", "get 3"],
              hint="Check the most specific classes first; everything else is a 500."),
    ],
    quiz=[
        _cq("Why set `name` on an `Error` subclass?",
            "It's what `String(e)` and stack traces print", ["`instanceof` needs it", "It makes the error serialisable", "`super` requires it"],
            "`instanceof` works without it; people reading logs don't."),
        _cq("How do you keep the original error when wrapping it?",
            "`new Error(\"high-level message\", { cause: original })`", ["Concatenate the messages", "Throw both", "`original.wrap()`"],
            "`cause` is part of the standard `Error` constructor (ES2022)."),
        _cq("What type is `e` in `catch (e)` under `strict`?",
            "`unknown`", ["`Error`", "`any`", "`never`"], "`useUnknownInCatchVariables` — anything can be thrown."),
        _cq("What does `AggregateError` hold?",
            "A list of errors in `.errors`, plus its own message", ["The first error only", "A stack of causes", "Only strings"],
            "`Promise.any` throws one when every promise rejects."),
        _cq("A `catch` block receives an error it doesn't understand. What should it do?",
            "Rethrow it", ["Log and ignore it", "Return `undefined`", "Convert it to a string"], "Handle what you can; let the rest propagate."),
        _cq("When is returning a `Result` better than throwing?",
            "For expected failures the caller must handle, like invalid input",
            ["Never", "For programming bugs", "For lost connections"], "The compiler then forces the caller to deal with the failure case."),
    ],
    interview=[
        ("How do you design errors in a TypeScript codebase?",
         "Subclass `Error` for each kind a caller might handle differently, set `name`, add typed fields (`status`, `field`, `retryable`), and pass `ErrorOptions` through so callers can attach a `cause`. Catch as `unknown`, narrow with `instanceof`, handle what you understand, rethrow the rest. Expected failures that callers must handle are often better as a returned `Result`."),
        ("What is `error.cause` for?",
         "Chaining: when a layer catches a low-level error and throws its own, it passes the original as `{ cause }`. Logs can then show the whole chain — \"server could not start ← config is not valid JSON ← Unexpected end of JSON input\" — while the user only sees the top."),
        ("Why is the catch variable `unknown`?",
         "Because JavaScript can throw any value — a string, `undefined`, an object. Typing it as `Error` (the old `any` behaviour) was a lie that crashed on `e.message`. `useUnknownInCatchVariables` (part of `strict`) makes you narrow first."),
    ],
)


_chapter(
    "ts_event_loop", "TS: Runtime & Architecture",
    "The Event Loop",
    "How JavaScript runs asynchronous code on one thread: the call stack, the microtask queue (promise callbacks, `await` continuations, `queueMicrotask`) and the task queue (timers) — and how to predict the order things print.",
    "JavaScript runs one piece of code at a time. When the current synchronous code finishes, the runtime drains the **microtask** queue completely — every `.then` callback, every resumed `await`, every `queueMicrotask` — and only then takes the next **task**, such as a `setTimeout` callback. That single rule predicts almost every async ordering question, explains why `await` gives other code a turn, and explains why a busy loop freezes timers.",
    "Java runs async work on thread pools, with real parallelism and locks. A JavaScript program has one thread for your code: there are no data races between callbacks, but there is an order — and a long synchronous computation blocks everything else, including timers.",
    why=r"""
"What does this print?" is the most common async interview question, and the
most common async bug is the same question asked by accident: a log line appears
before the data it describes, a `forEach` finishes before its async callbacks, a
timer fires later than expected because a loop never yielded.

None of it is random. The runtime follows a small, fixed set of rules about
*when* each callback runs. Learn them once and you can read async code the way
the engine runs it — and write code whose output doesn't depend on timing at all.
""",
    idea=r"""
**One call stack.** Synchronous code runs to completion; nothing interrupts it.

**Two queues.**

- **Microtasks:** promise reactions (`.then`/`.catch`/`.finally` callbacks),
  the continuation after each `await`, and `queueMicrotask(fn)`.
- **Tasks (macrotasks):** timers (`setTimeout`), I/O callbacks, events.

**The loop.** Run the current task to completion → run **all** microtasks,
including any queued while draining → take the next task → repeat. So:

```ts
console.log("A");
setTimeout(() => console.log("E"), 0);
Promise.resolve().then(() => console.log("C"));
queueMicrotask(() => console.log("D"));
console.log("B");
// A B C D E
```

**`await` splits a function.** Everything before the first `await` runs
synchronously, as part of the caller. The rest is scheduled as a microtask when
the awaited promise settles — which is why two `async` calls interleave at their
`await`s.

**Timers are ordered by delay, then by when they were set.** A `setTimeout(f, 0)`
still waits for the current code *and* every microtask. Delays are minimums, not
promises: a long synchronous loop delays every timer.

**Writing deterministic async code** (this programme's rule, M6-03): make order
depend on these rules — microtasks before tasks, timers by delay — or on explicit
sequencing (`await`, index-ordered results), never on how long something took.
""",
    examples=[
        ("Sync, then microtasks, then timers",
         r"""
console.log("1 sync");
setTimeout(() => console.log("6 timer"), 0);
Promise.resolve().then(() => console.log("3 promise"));
queueMicrotask(() => console.log("4 queueMicrotask"));
Promise.resolve().then(() => {
  console.log("5 promise, queued from a microtask:");
  queueMicrotask(() => console.log("5b still before the timer"));
});
console.log("2 sync");
""", [""],
         "The whole microtask queue — including microtasks added while it drains — runs before the first timer."),
        ("`await` hands over control",
         r"""
async function task(name: string): Promise<void> {
  console.log(`${name}: start`);
  await null;
  console.log(`${name}: after first await`);
  await null;
  console.log(`${name}: done`);
}
const a = task("a");
const b = task("b");
console.log("both started");
await Promise.all([a, b]);
console.log("all finished");
""", [""],
         "Each `task` runs synchronously up to its first `await`, then returns a pending promise. The continuations are microtasks, so `a` and `b` take turns."),
        ("Timers by delay",
         r"""
const order: string[] = [];
setTimeout(() => order.push("30ms"), 30);
setTimeout(() => order.push("10ms"), 10);
setTimeout(() => order.push("0ms"), 0);
setTimeout(() => order.push("10ms, set later"), 10);
setTimeout(() => console.log(order.join(" -> ")), 50);
""", [""],
         "Timers fire by delay; equal delays fire in the order they were set. None of this depends on how fast the machine is."),
        ("Sequential vs concurrent, made visible",
         r"""
const events: string[] = [];
const fakeRequest = (name: string) =>
  new Promise<string>((resolve) => {
    events.push(`start ${name}`);
    setTimeout(() => {
      events.push(`end ${name}`);
      resolve(name.toUpperCase());
    }, 10);
  });

for (const n of ["a", "b"]) await fakeRequest(n);
console.log("sequential: " + events.join(", "));

events.length = 0;
const results = await Promise.all(["a", "b"].map(fakeRequest));
console.log("concurrent: " + events.join(", "));
console.log(results.join(","));
""", [""],
         "Awaiting inside the loop starts each request after the previous one ends. Mapping to promises first starts them all, and `Promise.all` returns results in input order however they finish."),
    ],
    errors=[
        (1308, r"""
function load(): string {
  const text = await Promise.resolve("data");
  return text;
}
""", "`await` is only allowed inside an `async` function (or at a module's top level). Mark the function `async` — its return type becomes `Promise<string>`."),
        (2801, r"""
async function isReady(): Promise<boolean> {
  return false;
}
if (isReady()) console.log("ready!");
""", "A `Promise` object is always truthy, whatever it will resolve to. The compiler catches the missing `await`."),
    ],
    pitfalls=[
        ("`forEach` with an async callback",
         r"""
const saved: string[] = [];
const save = async (x: string) => {
  await null;
  saved.push(x);
};
async function saveAll(items: string[]): Promise<void> {
  items.forEach(async (x) => {
    await save(x);
  });
  console.log(`saved ${saved.length} of ${items.length}`);
}
await saveAll(["a", "b", "c"]);
""",
         r"""
const saved: string[] = [];
const save = async (x: string) => {
  await null;
  saved.push(x);
};
async function saveAll(items: string[]): Promise<void> {
  for (const x of items) await save(x);
  console.log(`saved ${saved.length} of ${items.length}`);
}
await saveAll(["a", "b", "c"]);
""",
         "`forEach` ignores the promises its callback returns, so `saveAll` reported before any save finished. Use `for…of` with `await` (in order) or `await Promise.all(items.map(save))` (concurrently)."),
        ("A promise nobody awaited",
         r"""
let status = "idle";
async function sync(): Promise<void> {
  await null;
  status = "synced";
}
async function main(): Promise<void> {
  sync();
  console.log("status: " + status);
}
await main();
""",
         r"""
let status = "idle";
async function sync(): Promise<void> {
  await null;
  status = "synced";
}
async function main(): Promise<void> {
  await sync();
  console.log("status: " + status);
}
await main();
""",
         "A floating promise runs on its own schedule: `main` read `status` before `sync` resumed. (Lint rules like `no-floating-promises` catch this; the compiler only catches it in conditions.)"),
        ("A timer that waits for microtasks",
         r"""
const log: string[] = [];
setTimeout(() => log.push("timer"), 0);
let n = 0;
const spin = (): void => {
  if (n++ < 3) {
    log.push(`microtask ${n}`);
    queueMicrotask(spin);
  }
};
queueMicrotask(spin);
setTimeout(() => console.log(log.join(", ")), 5);
""",
         r"""
const log: string[] = [];
setTimeout(() => log.push("timer"), 0);
let n = 0;
const spin = (): void => {
  if (n++ < 3) {
    log.push(`step ${n}`);
    setTimeout(spin, 0);
  } else {
    console.log(log.join(", "));
  }
};
setTimeout(spin, 0);
""",
         "Microtasks that keep queueing microtasks all run before the timer — the timer is *starved* until the chain ends. Scheduling each step as a task lets other tasks take turns."),
    ],
    later=[
        "**Week 26 — Cancellation.** Stopping async work that's already been started.",
        "**Week 26 — Async iteration.** Consuming values that arrive over time with `for await`.",
    ],
    exercises=[
        _drill("ts_event_loop-order", "Queue it for after the sync code",
               "The program should print the input words in order, then `-- microtasks --`, then each word reversed. Replace `____` so each reversal is printed from a microtask.",
               r"""
import * as fs from "fs";
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
for (const w of words) {
  queueMicrotask(() => console.log([...w].reverse().join("")));
  console.log(w);
}
console.log("-- microtasks --");
""", ['queueMicrotask(() => console.log([...w].reverse().join("")));'],
               ["abc def", "x"],
               hint="`queueMicrotask(fn)` runs `fn` after the current synchronous code."),
        _drill("ts_event_loop-all", "Start them together",
               "`double` is async. Replace `____` so all the calls start at once and the results arrive in input order.",
               r"""
import * as fs from "fs";
const log: string[] = [];
async function double(n: number): Promise<number> {
  log.push(`start ${n}`);
  await null;
  return n * 2;
}
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const results = await Promise.all(nums.map(double));
console.log(log.join(", "));
console.log(results.join(" "));
""", ["await Promise.all(nums.map(double))"],
               ["1 2 3", "10"],
               hint="Map to promises first, then await them all with `Promise.all`."),
        _chal("ts_event_loop-simulate", "Predict the order", "Hard",
              "Each input line is an operation for a tiny event-loop simulator: `log <x>` (synchronous), `micro <x>` (queue a microtask that logs x), `timer <ms> <x>` (a timer that logs x). Simulate the rules — run every `log` in order, then all microtasks in order, then timers by delay (ties in the order they were set) — and print the order as `x -> y -> …`. Then check your simulator against the real runtime: schedule the same operations with `queueMicrotask`/`setTimeout` and print the real order too, as `real: …`, then `match: true|false`.",
              r"""
type Op = { kind: "log" | "micro"; label: string } | { kind: "timer"; ms: number; label: string };
const ops: Op[] = input.split("\n").map((line) => {
  const [kind = "", a = "", b = ""] = line.trim().split(/\s+/);
  return kind === "timer" ? { kind: "timer", ms: Number(a), label: b } : { kind: kind === "micro" ? "micro" : "log", label: a };
});
const predicted = [
  ...ops.filter((o) => o.kind === "log").map((o) => o.label),
  ...ops.filter((o) => o.kind === "micro").map((o) => o.label),
  ...ops.flatMap((o, i) => (o.kind === "timer" ? [{ ms: o.ms, i, label: o.label }] : []))
    .sort((a, b) => a.ms - b.ms || a.i - b.i)
    .map((t) => t.label),
];
console.log(predicted.join(" -> "));
const real: string[] = [];
for (const o of ops) {
  if (o.kind === "timer") setTimeout(() => real.push(o.label), o.ms);
  else if (o.kind === "log") real.push(o.label);
  else queueMicrotask(() => real.push(o.label));
}
const longest = Math.max(0, ...ops.map((o) => (o.kind === "timer" ? o.ms : 0)));
setTimeout(() => {
  console.log("real: " + real.join(" -> "));
  console.log(`match: ${real.join() === predicted.join()}`);
}, longest + 20);
""", ["log a\ntimer 0 t1\nmicro m1\nlog b\ntimer 5 t2\nmicro m2\ntimer 0 t3", "timer 10 late\nlog only"],
              hint="Three buckets: synchronous logs, microtasks, timers sorted by delay then by position."),
    ],
    quiz=[
        _cq("`setTimeout(f, 0)` and `Promise.resolve().then(g)` are scheduled in that order. Which runs first?",
            "`g` — microtasks run before the next timer", ["`f` — it was scheduled first", "They run together", "It depends on the machine"],
            "The whole microtask queue drains before any task."),
        _cq("What runs synchronously when you call an `async` function?",
            "Its body up to the first `await`", ["Nothing — it all runs later", "The whole body", "Only the return statement"],
            "The rest is resumed as a microtask."),
        _cq("Which of these is a microtask?",
            "The continuation after an `await`", ["A `setTimeout` callback", "An I/O callback", "A click event"], "Also `.then` callbacks and `queueMicrotask`."),
        _cq("Why does `items.forEach(async (x) => await save(x))` not wait?",
            "`forEach` ignores the promises its callback returns", ["`forEach` is synchronous only for arrays of numbers", "`await` doesn't work in arrow functions", "It does wait"],
            "Use `for…of` with `await`, or `Promise.all(items.map(…))`."),
        _cq("A synchronous loop runs for two seconds. What happens to a `setTimeout(f, 10)` set before it?",
            "It runs after the loop — about two seconds late", ["It interrupts the loop", "It runs on another thread", "It's cancelled"],
            "Nothing interrupts running code; a delay is a minimum."),
        _cq("`Promise.all([slow(), fast()])` — what order are the results in?",
            "Input order, regardless of which finished first", ["Completion order", "Random", "Reverse"], "That's what makes it deterministic to print."),
    ],
    interview=[
        ("Explain the event loop.",
         "JavaScript runs one task at a time on a single thread. After the current task (say, the script, or a timer callback) finishes, the runtime drains the microtask queue — promise callbacks, `await` continuations, `queueMicrotask` — completely, then takes the next task from the task queue: timers, I/O, events. So synchronous code runs first, then microtasks, then timers, which is how you predict print order."),
        ("What does `await` actually do?",
         "It suspends the async function and returns control to the caller; when the awaited promise settles, the rest of the function is queued as a microtask. Code before the first `await` runs synchronously. Two async functions called one after the other therefore interleave at their `await` points."),
        ("How do you run async operations in parallel and keep results in order?",
         "Start them all first — `items.map(fn)` creates the promises — then `await Promise.all(promises)`, whose results are in input order. For a bounded number at a time, use a small pool that starts the next item as each finishes."),
    ],
)


_chapter(
    "ts_cancellation", "TS: Runtime & Architecture",
    "Cancellation: AbortController & Friends",
    "Stopping async work that has already started: `AbortController` and `AbortSignal`, timeouts and combined signals, and the promise helpers `Promise.withResolvers` and `Promise.try`.",
    "A promise can't be cancelled — once work has started, only the work itself can decide to stop. The web-standard way to ask it to is an `AbortSignal`: the caller keeps an `AbortController`, passes `controller.signal` down, and calls `abort(reason)`; the work checks `signal.aborted` (or calls `signal.throwIfAborted()`) between steps and listens for the `abort` event to stop timers. `AbortSignal.timeout(ms)` and `AbortSignal.any([...])` build signals for timeouts and \"whichever comes first\".",
    "Java cancels a `Future` or interrupts a thread; the task must still check `isInterrupted()`. JavaScript's `AbortSignal` is the same cooperative idea, standardised across `fetch`, Node streams, timers and event listeners — so one signal can cancel a whole tree of operations.",
    why=r"""
The user closes the page, types another letter into the search box, or gives up
waiting. The request you started is still running, and it will finish and update
the screen with a stale result — or keep a connection busy for nothing.

`Promise.race(work, timeout)` looks like a fix and isn't: the loser keeps
running. Real cancellation is a conversation: the caller signals, and the work
stops at the next safe point and cleans up. `AbortController` is the standard
shape of that conversation, and it's what `fetch`, Node's APIs and most
libraries accept.
""",
    idea=r"""
**The pair.**

```ts
const controller = new AbortController();
startWork(controller.signal);        // pass the signal down
controller.abort(new Error("user cancelled"));   // later
```

`signal.aborted` becomes `true`, `signal.reason` holds the reason (a
`DOMException` named `AbortError` if you gave none), and an `abort` event fires
once.

**Inside the work.** Check between steps — `signal.throwIfAborted()` throws the
reason — and, for anything that waits (a timer, a listener), subscribe with
`signal.addEventListener("abort", …, { once: true })` so the wait ends
immediately. Always remove listeners and clear timers when the work finishes
normally too.

**Composing signals.** `AbortSignal.timeout(ms)` aborts itself after `ms` with a
`TimeoutError`. `AbortSignal.any([userSignal, AbortSignal.timeout(5000)])`
aborts when *either* does — "cancel, or give up after 5 s" in one signal.

**Promise helpers.** `Promise.withResolvers<T>()` returns
`{ promise, resolve, reject }`, so code that isn't inside a `new Promise`
executor can settle it — the natural way to build a cancellable wait.
`Promise.try(fn)` runs `fn` and always returns a promise, turning a synchronous
`throw` into a rejection.

**Contracts to keep.** An aborted operation should reject (typically with the
signal's reason) rather than resolve with a partial result; callers tell a
cancellation from a failure with `signal.aborted` or the error's `name`.
""",
    examples=[
        ("Cooperative cancellation between steps",
         r"""
async function process(items: string[], signal: AbortSignal): Promise<string[]> {
  const done: string[] = [];
  for (const item of items) {
    signal.throwIfAborted();
    await null;
    done.push(item.toUpperCase());
    console.log("processed " + item);
  }
  return done;
}
const controller = new AbortController();
const work = process(["a", "b", "c", "d"], controller.signal);
queueMicrotask(() => queueMicrotask(() => controller.abort(new Error("user cancelled"))));
try {
  console.log("result " + (await work).join(","));
} catch (e) {
  console.log("stopped: " + (e instanceof Error ? e.message : String(e)));
}
""", [""],
         "The work checks the signal before each step, so it stops at the first safe point after `abort` — here after the third item — and rejects with the reason instead of returning a partial result."),
        ("A cancellable sleep with `Promise.withResolvers`",
         r"""
function sleep(ms: number, signal: AbortSignal): Promise<void> {
  const { promise, resolve, reject } = Promise.withResolvers<void>();
  const onAbort = () => {
    clearTimeout(timer);
    reject(signal.reason);
  };
  const timer = setTimeout(() => {
    signal.removeEventListener("abort", onAbort);
    resolve();
  }, ms);
  signal.addEventListener("abort", onAbort, { once: true });
  return promise;
}
const c = new AbortController();
setTimeout(() => c.abort(new Error("gave up")), 20);
for (const ms of [5, 100]) {
  try {
    await sleep(ms, c.signal);
    console.log(`slept ${ms}ms`);
  } catch (e) {
    console.log(`sleep ${ms}ms interrupted: ${e instanceof Error ? e.message : String(e)}`);
  }
}
""", [""],
         "`withResolvers` hands `resolve` and `reject` to the timer and the abort listener. Whichever happens first wins, and it tidies up after the other so nothing fires later."),
        ("Cancel or time out, whichever comes first",
         r"""
async function slowTask(signal: AbortSignal): Promise<string> {
  for (let step = 1; step <= 5; step++) {
    await new Promise<void>((r) => setTimeout(r, 20));
    signal.throwIfAborted();
  }
  return "finished";
}
const user = new AbortController();
const signal = AbortSignal.any([user.signal, AbortSignal.timeout(50)]);
try {
  console.log(await slowTask(signal));
} catch (e) {
  const name = e instanceof Error ? e.name : "unknown";
  console.log(name === "TimeoutError" ? "gave up: took longer than 50ms" : "cancelled by the user");
}
""", [""],
         "`AbortSignal.any` combines the user's signal with a timeout. The task needs ~100ms and the timeout fires at 50ms, so the result is always the timeout — decided by fixed delays, not by machine speed."),
        ("`Promise.try` turns a throw into a rejection",
         r"""
function parse(text: string): number {
  const n = Number(text);
  if (!Number.isFinite(n)) throw new Error(`not a number: ${text}`);
  return n;
}
for (const t of ["42", "x"]) {
  const result = await Promise.try(() => parse(t)).then(
    (n) => `ok ${n}`,
    (e: unknown) => `rejected: ${e instanceof Error ? e.message : String(e)}`,
  );
  console.log(result);
}
""", [""],
         "A synchronous `throw` inside `Promise.try` becomes a rejected promise, so one `.then(ok, fail)` handles both the sync and async failure paths."),
    ],
    errors=[
        (2540, r"""
const controller = new AbortController();
controller.signal.aborted = true;
""", "A signal is read-only for everyone but its controller: call `controller.abort(reason)`. That also sets the reason and fires the `abort` event, which assigning a flag never could."),
        (2345, r"""
const { promise, resolve } = Promise.withResolvers<string>();
resolve(42);
""", "`withResolvers<string>()` gives a `resolve` that only accepts strings — the same type the `promise` will produce."),
    ],
    pitfalls=[
        ("Work that ignores its signal",
         r"""
async function download(parts: number, signal: AbortSignal): Promise<number> {
  let got = 0;
  for (let i = 1; i <= parts; i++) {
    await null;
    got++;
  }
  return got;
}
const c = new AbortController();
const job = download(5, c.signal);
c.abort();
const got = await job;
console.log(`parts downloaded after abort: ${got}`);
""",
         r"""
async function download(parts: number, signal: AbortSignal): Promise<number> {
  let got = 0;
  for (let i = 1; i <= parts; i++) {
    if (signal.aborted) break;
    await null;
    got++;
  }
  return got;
}
const c = new AbortController();
const job = download(5, c.signal);
c.abort();
const got = await job;
console.log(`parts downloaded after abort: ${got}`);
""",
         "Accepting a signal isn't the same as honouring it: cancellation is cooperative. Check it at every step (the first `got++` ran before the check in the second version only because the loop body had already started)."),
        ("`Promise.race` doesn't stop the loser",
         r"""
const log: string[] = [];
async function work(): Promise<string> {
  for (let i = 1; i <= 4; i++) {
    await new Promise<void>((r) => setTimeout(r, 30));
    log.push(`step ${i}`);
  }
  return "done";
}
const timeout = new Promise<string>((r) => setTimeout(() => r("timed out"), 45));
console.log(await Promise.race([work(), timeout]));
await new Promise<void>((r) => setTimeout(r, 150));
console.log(log.join(", "));
""",
         r"""
const log: string[] = [];
async function work(signal: AbortSignal): Promise<string> {
  for (let i = 1; i <= 4; i++) {
    await new Promise<void>((r) => setTimeout(r, 30));
    if (signal.aborted) return "cancelled";
    log.push(`step ${i}`);
  }
  return "done";
}
const c = new AbortController();
const timeout = new Promise<string>((r) => setTimeout(() => { c.abort(); r("timed out"); }, 45));
console.log(await Promise.race([work(c.signal), timeout]));
await new Promise<void>((r) => setTimeout(r, 150));
console.log(log.join(", "));
""",
         "The race resolved at 25ms, but the first `work` kept going to step 4. Racing only decides which result you *read*; stopping the work needs a signal the work checks."),
        ("Treating cancellation as a failure",
         r"""
async function fetchData(signal: AbortSignal): Promise<string> {
  await null;
  signal.throwIfAborted();
  return "data";
}
const c = new AbortController();
c.abort();
try {
  await fetchData(c.signal);
} catch (e) {
  console.log("ERROR: fetch failed — alerting on-call");
}
""",
         r"""
async function fetchData(signal: AbortSignal): Promise<string> {
  await null;
  signal.throwIfAborted();
  return "data";
}
const c = new AbortController();
c.abort();
try {
  await fetchData(c.signal);
} catch (e) {
  if (c.signal.aborted) console.log("cancelled (" + (e instanceof Error ? e.name : "?") + ") — nothing to report");
  else console.log("ERROR: fetch failed — alerting on-call");
}
""",
         "An abort rejects the promise, so it arrives in the same `catch` as real failures. Check `signal.aborted` (or the error's `name`) before treating it as an error."),
    ],
    later=[
        "**Week 26 — Problem set.** A cancellable task runner, retries that stop when aborted, debouncing on a simulated clock.",
        "**Week 25 — Resource management.** Removing listeners and clearing timers are cleanups — `using` fits them.",
    ],
    exercises=[
        _drill("ts_cancellation-check", "Honour the signal",
               "`sum` adds numbers one per microtask. Replace `____` so it stops — rejecting with the signal's reason — as soon as the signal is aborted.",
               r"""
import * as fs from "fs";
async function sum(nums: number[], signal: AbortSignal): Promise<number> {
  let total = 0;
  for (const n of nums) {
    signal.throwIfAborted();
    await null;
    total += n;
  }
  return total;
}
const [limit = 0, ...nums] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const c = new AbortController();
let ticks = 0;
const tick = () => {
  if (++ticks >= limit) c.abort(new Error(`aborted after ${limit} ticks`));
  else queueMicrotask(tick);
};
if (limit > 0) queueMicrotask(tick);
try {
  console.log("total " + (await sum(nums, c.signal)));
} catch (e) {
  console.log(e instanceof Error ? e.message : String(e));
}
""", ["signal.throwIfAborted();"],
               ["0 1 2 3", "2 5 5 5 5 5", "1 7"],
               hint="One call on the signal throws its reason if it has been aborted."),
        _drill("ts_cancellation-resolvers", "A gate you open from outside",
               "Replace `____` with the call that creates a promise together with its `resolve` function, so the `open` command can release everyone waiting.",
               r"""
import * as fs from "fs";
const { promise: gate, resolve: open } = Promise.withResolvers<string>();
const waiting: Promise<void>[] = [];
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [cmd = "", arg = ""] = line.trim().split(/\s+/);
  if (cmd === "wait") waiting.push(gate.then((msg) => console.log(`${arg} released: ${msg}`)));
  else if (cmd === "open") open(arg);
  console.log("handled " + cmd);
}
await Promise.all(waiting);
""", ["Promise.withResolvers<string>()"],
               ["wait ana\nwait bo\nopen go", "open now\nwait late"],
               hint="`Promise.withResolvers<T>()` returns `{ promise, resolve, reject }`."),
        _chal("ts_cancellation-retry", "Retries that stop when cancelled", "Hard",
              "Write `retry(task, attempts, signal)` that calls an async task up to `attempts` times, stopping early if the signal is aborted (rejecting with its reason) and rethrowing the last failure otherwise. The input's first line is how many attempts; the second is the outcome of each call to the task (`fail`, `ok`); the third, `cancel <n>` or `none`, aborts the signal right after the task has been called n times. Print `attempt <k>` for each call, then `result <value>`, `failed: <message>` or `cancelled: <reason>`.",
              r"""
async function retry<T>(task: () => Promise<T>, attempts: number, signal: AbortSignal): Promise<T> {
  let last: unknown = new Error("no attempts");
  for (let i = 1; i <= attempts; i++) {
    signal.throwIfAborted();
    try {
      return await task();
    } catch (e) {
      last = e;
    }
  }
  throw last;
}
const [attemptsText = "1", outcomesText = "", cancelText = "none"] = input.split("\n");
const outcomes = outcomesText.trim().split(/\s+/);
const cancelAfter = cancelText.startsWith("cancel") ? Number(cancelText.split(" ")[1]) : Infinity;
const c = new AbortController();
let calls = 0;
const task = async (): Promise<string> => {
  calls++;
  console.log(`attempt ${calls}`);
  if (calls >= cancelAfter) c.abort(new Error("user pressed stop"));
  await null;
  if (outcomes[calls - 1] === "ok") return `ok on attempt ${calls}`;
  throw new Error(`attempt ${calls} failed`);
};
try {
  console.log("result " + (await retry(task, Number(attemptsText), c.signal)));
} catch (e) {
  const message = e instanceof Error ? e.message : String(e);
  console.log(c.signal.aborted ? `cancelled: ${message}` : `failed: ${message}`);
}
""", ["3\nfail fail ok\nnone", "2\nfail fail fail\nnone", "5\nfail fail fail ok\ncancel 2"],
              hint="Check the signal before every attempt; keep the last error to rethrow when attempts run out."),
    ],
    quiz=[
        _cq("Can you cancel a promise?",
            "No — you ask the work to stop via a signal, and it cooperates", ["Yes, with `promise.cancel()`", "Yes, by rejecting it from outside", "Only with `Promise.race`"],
            "Cancellation is cooperative in JavaScript."),
        _cq("What does `signal.throwIfAborted()` do?",
            "Throws the signal's reason if it has been aborted; otherwise nothing", ["Aborts the signal", "Waits until it's aborted", "Returns a boolean"],
            "The one-line check between steps."),
        _cq("`AbortSignal.any([a, b])` aborts when?",
            "When either `a` or `b` aborts", ["When both abort", "Never", "Immediately"], "Cancel-or-timeout in one signal."),
        _cq("What does `Promise.withResolvers<T>()` return?",
            "`{ promise, resolve, reject }`", ["A resolved promise", "An `AbortController`", "An array of promises"], "Settle the promise from outside an executor."),
        _cq("After `Promise.race([work(), timeout])` resolves with the timeout, what is `work()` doing?",
            "Still running, unless it was given a signal and checks it", ["It was cancelled", "It was paused", "It threw"], "Racing chooses a result; it doesn't stop anything."),
        _cq("`controller.abort()` with no argument — what is `signal.reason`?",
            "A `DOMException` named `AbortError`", ["`undefined`", "`null`", "`\"aborted\"`"], "Pass your own reason for a clearer message."),
    ],
    interview=[
        ("How do you cancel an in-flight async operation?",
         "Create an `AbortController`, pass its `signal` into the operation, and call `abort(reason)`. The operation checks `signal.aborted` or calls `signal.throwIfAborted()` between steps and listens for the `abort` event to stop timers or requests; `fetch` and most Node APIs accept the signal directly. It's cooperative — the work has to honour it."),
        ("How would you implement a timeout for an async function?",
         "Combine signals: `AbortSignal.any([callerSignal, AbortSignal.timeout(ms)])` and pass that down. That stops the work when the timeout fires, unlike `Promise.race`, which only stops you waiting while the work keeps running."),
        ("What are `Promise.withResolvers` and `Promise.try` for?",
         "`withResolvers` gives you a promise plus its `resolve`/`reject` so you can settle it from event handlers or timers without nesting code in an executor — useful for cancellable waits and gates. `Promise.try(fn)` runs `fn` and always returns a promise, converting a synchronous throw into a rejection so one error path handles both."),
    ],
)


_chapter(
    "ts_async_iteration", "TS: Runtime & Architecture",
    "Async Iteration",
    "Values that arrive over time: `for await…of`, async generators (`async function*`), `Symbol.asyncIterator`, `Array.fromAsync` — pagination, streams and pipelines that pull one item at a time.",
    "A regular iterator hands out values synchronously; an async iterator hands out *promises* of values, and `for await (const x of source)` waits for each one before running the loop body. An async generator — `async function*` — can `await` and `yield`, which makes paginated APIs, line-by-line readers and polling loops look like ordinary loops. Consumers pull at their own pace, so a slow consumer naturally slows the producer (backpressure).",
    "Java's closest analogues are reactive streams (`Flow.Publisher`) or blocking iterators on a thread. JavaScript's async iterators are *pull*-based and built into the language: `for await` works on any object with `[Symbol.asyncIterator]`, including Node streams.",
    why=r"""
Many sources don't give you everything at once: an API returns results a page at
a time, a file arrives in chunks, a queue delivers messages as they come. The
naive version fetches everything into an array first — slow to start, and
impossible for sources that never end.

Async iteration lets you write the consumer as a plain loop — "for each user, do
this" — while the producer fetches the next page only when the loop asks for
more. Stop the loop early and the producer stops too. The pattern is everywhere
in modern Node code, from `readline` to streams to database cursors.
""",
    idea=r"""
**The protocol.** An async iterable has `[Symbol.asyncIterator]()` returning an
object whose `next()` returns a `Promise<IteratorResult<T>>`.

**`for await…of`** pulls values one at a time, awaiting each:

```ts
for await (const user of fetchAllUsers()) {
  if (user.banned) break;      // stops the producer too
  console.log(user.name);
}
```

It also accepts ordinary iterables of promises (`for await (const x of
[p1, p2])`), awaiting each in order. Like `await`, it's only allowed in async
functions and at a module's top level.

**Async generators** are the easy way to write a source:

```ts
async function* pages(): AsyncGenerator<User[]> {
  for (let page = 1; ; page++) {
    const batch = await fetchPage(page);
    if (batch.length === 0) return;
    yield batch;
  }
}
async function* users() {
  for await (const batch of pages()) yield* batch;   // flatten pages into users
}
```

- `yield*` delegates to another (async) iterable.
- `break`, `return` or an exception in the consumer calls the generator's
  `return()`, so its `finally` blocks run — clean up connections there.
- Like sync generators, an async generator object is single-use.

**Collecting.** `Array.fromAsync(source)` awaits every value into an array
(ES2024). Use it when you really need them all; iterate when you don't.

**Sequential by nature.** `for await` handles one item at a time. For bounded
concurrency, pull a few items and process them with `Promise.all`, or use a pool
(week 26's problem set).
""",
    examples=[
        ("Paginating a simulated API",
         r"""
const DB = ["ana", "bo", "cy", "dee", "eve", "fay", "gus"];
let requests = 0;
async function fetchPage(page: number, size: number): Promise<string[]> {
  requests++;
  await null;
  return DB.slice((page - 1) * size, page * size);
}
async function* allUsers(size: number): AsyncGenerator<string> {
  for (let page = 1; ; page++) {
    const batch = await fetchPage(page, size);
    if (batch.length === 0) return;
    yield* batch;
  }
}
for await (const name of allUsers(3)) {
  console.log(name);
  if (name === "dee") break;
}
console.log(`requests made: ${requests}`);
""", [""],
         "The consumer stopped at `dee`, on the second page, so the third page was never requested. The generator fetches only as fast as the loop pulls."),
        ("Collecting with `Array.fromAsync`",
         r"""
async function* countdown(from: number): AsyncGenerator<number> {
  for (let i = from; i > 0; i--) {
    await null;
    yield i;
  }
}
const all = await Array.fromAsync(countdown(4));
console.log(all.join(" "));
const squares = await Array.fromAsync(countdown(3), (n) => n * n);
console.log(squares.join(" "));
""", [""],
         "`Array.fromAsync` is `Array.from` for async sources — including an optional mapping function. It waits for the source to end, so never use it on an infinite one."),
        ("Cleanup when the consumer stops early",
         r"""
async function* lines(text: string): AsyncGenerator<string> {
  console.log("open");
  try {
    for (const line of text.split("\n")) {
      await null;
      yield line;
    }
  } finally {
    console.log("close");
  }
}
for await (const line of lines("one\ntwo\nSTOP\nfour")) {
  if (line === "STOP") break;
  console.log("read " + line);
}
console.log("after loop");
""", [""],
         "`break` calls the generator's `return()`, which runs its `finally` — the reader is closed before the loop statement finishes, exactly as `using` would guarantee."),
        ("An async pipeline of generators",
         r"""
async function* numbers(): AsyncGenerator<number> {
  for (let i = 1; i <= 10; i++) {
    await null;
    yield i;
  }
}
async function* filterAsync<T>(source: AsyncIterable<T>, keep: (x: T) => boolean): AsyncGenerator<T> {
  for await (const x of source) if (keep(x)) yield x;
}
async function* mapAsync<T, U>(source: AsyncIterable<T>, fn: (x: T) => U): AsyncGenerator<U> {
  for await (const x of source) yield fn(x);
}
const pipeline = mapAsync(filterAsync(numbers(), (n) => n % 3 === 0), (n) => `#${n}`);
console.log((await Array.fromAsync(pipeline)).join(" "));
""", [""],
         "Each stage is a small async generator that pulls from the previous one — the async version of iterator helpers. Values flow through one at a time."),
    ],
    errors=[
        (2488, r"""
async function* ticks(): AsyncGenerator<number> {
  yield 1;
}
for (const t of ticks()) console.log(t);
""", "An async generator produces promises, so it's an *async* iterable: consume it with `for await`."),
        (1103, r"""
async function* ticks(): AsyncGenerator<number> {
  yield 1;
}
function show(): void {
  for await (const t of ticks()) console.log(t);
}
""", "`for await` waits, so — like `await` — it's only allowed in async functions and at a module's top level."),
    ],
    pitfalls=[
        ("A sync loop over an async source",
         (r"""
async function* words(): AsyncGenerator<string> {
  yield "a";
  yield "b";
}
for (const w of words()) console.log(w);
""", 2488),
         r"""
async function* words(): AsyncGenerator<string> {
  yield "a";
  yield "b";
}
for await (const w of words()) console.log(w);
""",
         "Values from an async generator arrive as promises; `for await` waits for each."),
        ("Iterating the same generator twice",
         r"""
async function* ids(): AsyncGenerator<number> {
  yield 1;
  yield 2;
}
const source = ids();
console.log("first: " + (await Array.fromAsync(source)).join(","));
console.log("second: " + ((await Array.fromAsync(source)).join(",") || "(nothing)"));
""",
         r"""
async function* ids(): AsyncGenerator<number> {
  yield 1;
  yield 2;
}
console.log("first: " + (await Array.fromAsync(ids())).join(","));
console.log("second: " + ((await Array.fromAsync(ids())).join(",") || "(nothing)"));
""",
         "A generator object is a single-use cursor. Call the generator function again for a fresh one."),
        ("`Array.from` on an async source",
         (r"""
async function* ids(): AsyncGenerator<number> {
  yield 1;
  yield 2;
}
const all = Array.from(ids());
console.log(all.length);
""", 2769),
         r"""
async function* ids(): AsyncGenerator<number> {
  yield 1;
  yield 2;
}
const all = await Array.fromAsync(ids());
console.log(all.length);
""",
         "`Array.from` needs a synchronous iterable. `Array.fromAsync` awaits each value — and returns a promise, so `await` it."),
    ],
    later=[
        "**Week 26 — Problem set.** Paginated loading, an async queue, and a concurrency-limited pool.",
        "**Week 24 — Iterator helpers.** The synchronous version of these pipelines.",
    ],
    exercises=[
        _drill("ts_async_iteration-gen", "An async generator of pages",
               "Replace `____` so `pages` yields the input's items in pages of `size`, awaiting a (simulated) fetch for each page.",
               r"""
import * as fs from "fs";
const [sizeText = "2", ...items] = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const size = Number(sizeText);
async function fetchPage(page: number): Promise<string[]> {
  await null;
  return items.slice(page * size, (page + 1) * size);
}
async function* pages(): AsyncGenerator<string[]> {
  for (let page = 0; ; page++) {
    const batch = await fetchPage(page);
    if (batch.length === 0) return;
    yield batch;
  }
}
let n = 0;
for await (const batch of pages()) console.log(`page ${++n}: ${batch.join(" ")}`);
console.log(`${n} pages`);
""", ["for (let page = 0; ; page++) {\n    const batch = await fetchPage(page);\n    if (batch.length === 0) return;\n    yield batch;\n  }"],
               ["2 a b c d e", "3 x y z", "5 solo"],
               hint="Loop over page numbers; stop (`return`) at the first empty page; `yield` each batch."),
        _drill("ts_async_iteration-for-await", "Consume it with `for await`",
               "Replace `____` with the loop header that consumes `readings()` one value at a time, so the running average is printed after each reading.",
               r"""
import * as fs from "fs";
const values = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
async function* readings(): AsyncGenerator<number> {
  for (const v of values) {
    await null;
    yield v;
  }
}
let count = 0;
let total = 0;
for await (const r of readings()) {
  count++;
  total += r;
  console.log(`after ${count}: average ${(total / count).toFixed(2)}`);
}
""", ["for await (const r of readings())"],
               ["10 20 30", "5", "1 2"],
               hint="`for await (const x of source)`."),
        _chal("ts_async_iteration-merge", "Merge two sorted async streams", "Hard",
              "The input has two lines of sorted numbers. Turn each into an async generator (one `await null` per value), then write `merge(a, b)` — an async generator that yields all values in sorted order by pulling from whichever stream has the smaller current value (`a` on ties). Print the merged values, then `pulled <k>` — how many values were pulled from the two sources in total — when the consumer stops after the first value greater than 50 (print the values up to and including it).",
              r"""
async function* fromList(xs: number[], counter: { pulled: number }): AsyncGenerator<number> {
  for (const x of xs) {
    await null;
    counter.pulled++;
    yield x;
  }
}
async function* merge(a: AsyncIterator<number>, b: AsyncIterator<number>): AsyncGenerator<number> {
  let x = await a.next();
  let y = await b.next();
  while (!x.done || !y.done) {
    if (!x.done && (y.done || x.value <= y.value)) {
      yield x.value;
      x = await a.next();
    } else if (!y.done) {
      yield y.value;
      y = await b.next();
    }
  }
}
const [first = "", second = ""] = input.split("\n");
const parse = (s: string) => s.trim().split(/\s+/).filter((t) => t !== "").map(Number);
const counter = { pulled: 0 };
const out: number[] = [];
for await (const v of merge(fromList(parse(first), counter), fromList(parse(second), counter))) {
  out.push(v);
  if (v > 50) break;
}
console.log(out.join(" "));
console.log(`pulled ${counter.pulled}`);
""", ["1 4 9 60 70\n2 3 55 80", "5 10\n7", "100\n1 2"],
              hint="Keep the current `next()` result of each source; yield the smaller and advance that source only."),
    ],
    quiz=[
        _cq("What does `for await (const x of source)` do each iteration?",
            "Awaits the next value before running the body", ["Runs all iterations in parallel", "Awaits only the first value", "Nothing different from `for…of`"],
            "Values are pulled one at a time."),
        _cq("What does an `async function*` return?",
            "An async generator — an async iterable of its yielded values", ["A promise of an array", "A regular generator", "A single promise"],
            "Consume it with `for await` or `Array.fromAsync`."),
        _cq("A consumer `break`s out of `for await` early. What happens to the generator?",
            "Its `return()` is called, so its `finally` blocks run", ["It keeps running in the background", "It throws", "Nothing"],
            "Put cleanup in `finally`."),
        _cq("How do you collect an async iterable into an array?",
            "`await Array.fromAsync(source)`", ["`Array.from(source)`", "`[...source]`", "`source.toArray()`"],
            "ES2024; also takes a mapping function."),
        _cq("Can you iterate the same async generator object twice?",
            "No — it's single-use; call the generator function again", ["Yes", "Only with `for await`", "Only if it's finite"], "Same as sync generators."),
        _cq("Why is async iteration good for paginated APIs?",
            "The next page is fetched only when the consumer asks for more", ["It fetches all pages in parallel", "It caches every page", "It avoids promises"],
            "Stopping early saves the remaining requests."),
    ],
    interview=[
        ("What's an async iterator?",
         "An object whose `next()` returns a promise of `{ value, done }`, reachable through `[Symbol.asyncIterator]`. `for await…of` consumes it one value at a time. Async generators (`async function*`) are the easy way to produce one — they can `await` between `yield`s."),
        ("How would you consume a paginated API?",
         "Wrap it in an async generator that fetches page by page and `yield*`s each batch, so callers write `for await (const item of all())`. Pages are fetched lazily, the consumer can stop early (which ends the generator and runs its `finally`), and memory holds one page at a time."),
        ("`for await` vs `Promise.all`?",
         "`for await` is sequential — one value at a time, good for streams and backpressure. `Promise.all` runs already-started promises concurrently and gives all results at once. For large workloads you often want something in between: a concurrency-limited pool."),
    ],
)
