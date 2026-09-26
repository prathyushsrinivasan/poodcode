# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The original Month 6 TypeScript chapters, brought up to the lesson template
# (TS_MASTERY_ROADMAP.md F-12, X-02/X-03) with `_deepen`:
#
#   ts_classes  ts_this_accessors          (week 23)
#   ts_iterators  ts_ds_generics           (week 24)
#   ts_errors  ts_error_types              (week 25)
#   ts_async  ts_async_patterns            (week 26)
#
# Every output and message is computed (gen_ts_outputs.py). The async programs
# follow M6-03: their output depends on due times alone, never on how quickly
# the machine runs them.
# ---------------------------------------------------------------------------

_deepen(
    "ts_classes",
    why=r"""
Some data has rules. A bank balance may not go below zero; a queue's head may
not pass its tail. With a plain object anyone can write any field, so the rule
has to be re-checked everywhere the object is touched. A class puts the data
and the only operations allowed to change it in one place, and hides the rest —
the rule is enforced once, in the methods, and callers can't break it.

A class is also two things in TypeScript at once: a runtime value you call with
`new`, and a type describing its instances. `implements` checks it against an
interface, `extends` builds on another class, and `#private` fields are
enforced by the JavaScript engine itself, not just by the compiler.
""",
    examples=[
        ("An invariant only the class can change",
         r"""
class Account {
  readonly owner: string;
  #balance = 0;
  constructor(owner: string) {
    this.owner = owner;
  }
  deposit(amount: number): this {
    if (amount <= 0) throw new RangeError("deposit must be positive");
    this.#balance += amount;
    return this;
  }
  withdraw(amount: number): boolean {
    if (amount > this.#balance) return false;
    this.#balance -= amount;
    return true;
  }
  get balance(): number {
    return this.#balance;
  }
}
const acct = new Account("ana").deposit(50).deposit(20);
console.log(acct.withdraw(100), acct.withdraw(30), acct.balance);
""", [""],
         "Nothing outside the class can write `#balance`, so \"never negative\" holds by construction. Returning `this` from `deposit` allows chaining."),
        ("`implements` checks a class against an interface",
         r"""
interface Shape {
  readonly name: string;
  area(): number;
}
class Circle implements Shape {
  readonly name = "circle";
  readonly r: number;
  constructor(r: number) {
    this.r = r;
  }
  area(): number {
    return Math.PI * this.r ** 2;
  }
}
class Square implements Shape {
  readonly name = "square";
  readonly side: number;
  constructor(side: number) {
    this.side = side;
  }
  area(): number {
    return this.side ** 2;
  }
}
const shapes: Shape[] = [new Circle(1), new Square(3)];
for (const s of shapes) console.log(s.name + ": " + s.area().toFixed(2));
""", [""],
         "`implements` adds no code — it only asks the compiler to check the class has everything `Shape` requires. Callers depend on the interface, not the classes."),
        ("An abstract base with one step left open",
         r"""
abstract class Report {
  abstract title(): string;
  abstract rows(): string[];
  render(): string {
    const lines = this.rows();
    return [this.title() + " (" + lines.length + ")", ...lines.map((l) => "- " + l)].join("\n");
  }
}
class TodoReport extends Report {
  readonly items: string[];
  constructor(items: string[]) {
    super();
    this.items = items;
  }
  override title(): string {
    return "Todo";
  }
  override rows(): string[] {
    return this.items.filter((i) => i.length > 0);
  }
}
console.log(new TodoReport(["write", "", "test"]).render());
""", [""],
         "The base class fixes the shape of `render` and subclasses fill in the parts. `abstract` and `override` are type-only, so they erase cleanly; `new Report()` would not compile."),
    ],
    errors=[
        (2564, r"""
class Counter {
  count: number;
  constructor(start?: number) {
    if (start !== undefined) this.count = start;
  }
}
""", "Under `strict`, every declared field must be assigned on every path through the constructor. Give it a default (`count = 0`) or assign it unconditionally."),
        (17009, r"""
class Animal {
  readonly name: string;
  constructor(name: string) {
    this.name = name;
  }
}
class Dog extends Animal {
  readonly tricks: string[];
  constructor(name: string) {
    this.tricks = [];
    super(name);
  }
}
"""  , "A subclass's `this` doesn't exist until the parent constructor has run. Call `super(...)` first."),
        (2420, r"""
interface Shape {
  area(): number;
}
class Square implements Shape {
  readonly side: number;
  constructor(side: number) {
    this.side = side;
  }
  perimeter(): number {
    return this.side * 4;
  }
}
""", "`implements` is a promise the compiler holds you to — the class is missing `area`."),
    ],
    pitfalls=[
        ("A base constructor calling an overridden method",
         r"""
class Base {
  readonly label: string;
  constructor() {
    this.label = this.describe();
  }
  describe(): string {
    return "base";
  }
}
class Tagged extends Base {
  tag = "v2";
  override describe(): string {
    return "tagged " + this.tag;
  }
}
console.log(new Tagged().label);
""",
         r"""
class Base {
  get label(): string {
    return this.describe();
  }
  describe(): string {
    return "base";
  }
}
class Tagged extends Base {
  tag = "v2";
  override describe(): string {
    return "tagged " + this.tag;
  }
}
console.log(new Tagged().label);
""",
         "The parent constructor runs *before* the subclass's field initialisers, so the override saw `tag` still unset. Compute it lazily (a getter) instead of in the base constructor."),
        ("`private` is only a compile-time fence",
         r"""
class Vault {
  private secret = "k-123";
  open(key: string): boolean {
    return key === this.secret;
  }
}
const v = new Vault();
console.log(Object.keys(v), JSON.stringify(v));
""",
         r"""
class Vault {
  #secret = "k-123";
  open(key: string): boolean {
    return key === this.#secret;
  }
}
const v = new Vault();
console.log(Object.keys(v), JSON.stringify(v));
""",
         "`private` is erased with the other types — at runtime it's an ordinary property that `Object.keys` and `JSON.stringify` see. A `#` field is private to the engine."),
        ("An object literal that fits the type is not an instance",
         r"""
class Point {
  readonly x: number;
  readonly y: number;
  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
  }
}
function describe(p: Point): string {
  return p instanceof Point ? `point ${p.x},${p.y}` : "not a point";
}
console.log(describe({ x: 1, y: 2 }));
""",
         r"""
class Point {
  readonly x: number;
  readonly y: number;
  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
  }
}
function describe(p: Point): string {
  return `point ${p.x},${p.y}`;
}
console.log(describe({ x: 1, y: 2 }));
""",
         "Class types are structural: `{ x: 1, y: 2 }` has the right shape, so it type-checks, but `instanceof` asks about the prototype. Don't branch on `instanceof` for a type that plain objects satisfy — rely on the shape, or add a `#brand` field."),
    ],
    later=[
        "**Week 23 — this, getters and setters.** Methods detached from their object.",
        "**Week 23 — Class design.** Composition over inheritance, and when a class is the wrong tool.",
        "**Week 24 — Generic data structures.** Stacks, queues and lists as classes over `T`.",
        "**Week 25 — Typed errors.** Error hierarchies are classes that extend `Error`.",
    ],
)


_deepen(
    "ts_this_accessors",
    why=r"""
`this` is not fixed where a function is written; it's decided each time the
function is *called*, by what's to the left of the dot. That's what lets one
method serve every instance — and it's also why a method handed to `forEach`,
`setTimeout` or an event emitter can arrive with no object at all.

Getters and setters solve a different problem: a class wants to change how it
stores something (or check every write) without changing how callers use it.
`r.area` reads like a field but runs code; `t.celsius = -300` looks like an
assignment but can refuse. Callers never need to know which properties are
stored and which are computed.
""",
    examples=[
        ("A setter that validates, a getter that converts",
         r"""
class Temperature {
  #celsius = 0;
  get celsius(): number {
    return this.#celsius;
  }
  set celsius(value: number) {
    if (value < -273.15) throw new RangeError(`below absolute zero: ${value}`);
    this.#celsius = value;
  }
  get fahrenheit(): number {
    return this.#celsius * 9 / 5 + 32;
  }
  set fahrenheit(value: number) {
    this.celsius = (value - 32) * 5 / 9;
  }
}
const t = new Temperature();
t.fahrenheit = 212;
console.log(t.celsius, t.fahrenheit);
try {
  t.celsius = -300;
} catch (e) {
  console.log(e instanceof Error ? e.message : String(e));
}
console.log(t.celsius);
""", [""],
         "Only `#celsius` is stored. The Fahrenheit setter goes through the Celsius setter, so the range check can't be bypassed, and the failed write left the old value intact."),
        ("One function, three `this` values",
         r"""
type Named = { name: string; greet(): string };
const ana: Named = {
  name: "ana",
  greet() {
    return "hi from " + this.name;
  },
};
const ben: Named = { name: "ben", greet: ana.greet };
const bound = ana.greet.bind(ben);
console.log(ana.greet(), "|", ben.greet(), "|", bound());
""", [""],
         "The same function object runs three times. Called as `ben.greet()`, `this` is `ben` — it doesn't matter that the function was written inside `ana`. `bind` fixes `this` once and for all."),
        ("Keeping `this` when a method becomes a callback",
         r"""
class Clicker {
  count = 0;
  inc(): void {
    this.count++;
  }
  incArrow = (): void => {
    this.count++;
  };
}
const c = new Clicker();
const handlers: (() => void)[] = [c.incArrow, c.inc.bind(c), () => c.inc()];
for (const h of handlers) h();
console.log(c.count);
""", [""],
         "Three safe ways to hand over a method: an arrow-function field (captures `this` when the instance is built), `bind`, or a small arrow that calls the method on its object."),
    ],
    errors=[
        (2684, r"""
class Counter {
  count = 0;
  inc(this: Counter): void {
    this.count++;
  }
}
const c = new Counter();
const inc = c.inc;
inc();
""", "A `this` parameter (erased at runtime) declares what a method must be called on, which turns the lost-`this` bug into a compile error."),
        (2540, r"""
class Rect {
  readonly w: number;
  readonly h: number;
  constructor(w: number, h: number) {
    this.w = w;
    this.h = h;
  }
  get area(): number {
    return this.w * this.h;
  }
}
const r = new Rect(3, 4);
r.area = 20;
""", "A getter without a setter is a read-only property."),
        (6234, r"""
class Rect {
  readonly w = 3;
  readonly h = 4;
  get area(): number {
    return this.w * this.h;
  }
}
console.log(new Rect().area());
""", "A getter is read like a field. `area()` tries to call the number it returned, and the compiler recognises the mistake."),
    ],
    pitfalls=[
        ("Passing a method as a callback",
         r"""
class Tally {
  total = 0;
  add(n: number): void {
    this.total += n;
  }
}
const t = new Tally();
try {
  [1, 2, 3].forEach(t.add);
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
console.log(t.total);
""",
         r"""
class Tally {
  total = 0;
  add(n: number): void {
    this.total += n;
  }
}
const t = new Tally();
[1, 2, 3].forEach((n) => t.add(n));
console.log(t.total);
""",
         "`forEach(t.add)` passes the function alone; it's called with `this` undefined. The compiler doesn't catch it unless the method declares a `this` parameter."),
        ("A setter that assigns to itself",
         r"""
class User {
  set name(value: string) {
    this.name = value.trim();
  }
  get name(): string {
    return this.name;
  }
}
try {
  const u = new User();
  u.name = "  ana ";
  console.log(u.name);
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
class User {
  #name = "";
  set name(value: string) {
    this.#name = value.trim();
  }
  get name(): string {
    return this.#name;
  }
}
const u = new User();
u.name = "  ana ";
console.log(u.name);
""",
         "Inside the setter, `this.name = …` calls the setter again, forever. An accessor needs a separate backing field."),
        ("An arrow function as an object-literal method",
         (r"""
const counter = {
  count: 0,
  inc: () => {
    this.count++;
  },
};
counter.inc();
console.log(counter.count);
""", 2532),
         r"""
const counter = {
  count: 0,
  inc() {
    this.count++;
  },
};
counter.inc();
console.log(counter.count);
""",
         "Arrow functions don't get their own `this` — they use the one around them. At the top of a module that's `undefined`, and the compiler knows it. Method shorthand gets the object."),
    ],
    later=[
        "**Week 23 — Class design.** Accessors as a stable public surface over changing internals.",
        "**Week 24 — Generic data structures.** `size` and `isEmpty` as getters.",
        "**Week 26 — Promises.** Methods passed to `setTimeout` and `.then` lose `this` the same way.",
    ],
)


_deepen(
    "ts_iterators",
    why=r"""
`for…of`, spread, array destructuring, `Array.from`, `new Map(…)` and
`Promise.all` all consume values the same way: they ask for an iterator and
call `next()` until it says `done`. Anything that implements that one method —
arrays, strings, maps, sets, or your own class — works with all of them.

Generators are the easy way to implement it. A `function*` can pause at each
`yield` and resume where it left off, so a tree walk or an infinite sequence is
written as an ordinary loop, and only the values someone actually asks for are
ever computed.
""",
    examples=[
        ("A generator that walks a tree",
         r"""
type Tree = { value: number; children: Tree[] };
function* walk(t: Tree, depth = 0): Generator<string> {
  yield "  ".repeat(depth) + t.value;
  for (const child of t.children) yield* walk(child, depth + 1);
}
const tree: Tree = {
  value: 1,
  children: [
    { value: 2, children: [{ value: 4, children: [] }] },
    { value: 3, children: [] },
  ],
};
console.log([...walk(tree)].join("\n"));
""", [""],
         "`yield*` forwards every value of the recursive call, so the depth-first order falls out of the code's shape — no explicit stack, no result array passed around."),
        ("Only what's asked for is computed",
         r"""
let computed = 0;
function* squares(): Generator<number> {
  for (let i = 1; ; i++) {
    computed++;
    yield i * i;
  }
}
function* filter<T>(source: Iterable<T>, keep: (x: T) => boolean): Generator<T> {
  for (const x of source) if (keep(x)) yield x;
}
function* take<T>(source: Iterable<T>, n: number): Generator<T> {
  if (n <= 0) return;
  for (const x of source) {
    yield x;
    if (--n === 0) return;
  }
}
const odd = [...take(filter(squares(), (x) => x % 2 === 1), 3)];
console.log(odd.join(","), "computed " + computed);
""", [""],
         "An infinite source, a filter and a limit, chained. Five squares were computed to find three odd ones; nothing else ran."),
        ("Everything that consumes iterables",
         r"""
function* fib(): Generator<number> {
  let [a, b] = [0, 1];
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}
const [f0, f1, , f3] = fib();
function* pairs(): Generator<[string, number]> {
  yield ["x", 1];
  yield ["y", 2];
}
const m = new Map(pairs());
console.log(f0, f1, f3, m.get("y"), Math.max(...new Set([3, 9, 4, 9])));
""", [""],
         "Destructuring pulled four values from an infinite generator and stopped. `Map` accepted a generator of pairs; spread accepted a `Set`."),
    ],
    errors=[
        (2488, r"""
const scores = { ana: 3, ben: 5 };
for (const [name, score] of scores) {
  console.log(name, score);
}
""", "Plain objects aren't iterable. Iterate `Object.entries(scores)`, or use a `Map`."),
        (2322, r"""
function* ids(): Generator<number> {
  yield 1;
  yield "2";
}
""", "The declared `Generator<number>` checks every `yield`."),
    ],
    pitfalls=[
        ("Iterating a generator twice",
         r"""
function* evens(limit: number): Generator<number> {
  for (let i = 0; i < limit; i += 2) yield i;
}
const upToSix = evens(6);
console.log([...upToSix].length, [...upToSix].length);
""",
         r"""
function* evens(limit: number): Generator<number> {
  for (let i = 0; i < limit; i += 2) yield i;
}
const upToSix: Iterable<number> = { [Symbol.iterator]: () => evens(6) };
console.log([...upToSix].length, [...upToSix].length);
""",
         "A generator object is its own iterator and is used up after one pass. An iterable whose `[Symbol.iterator]` makes a fresh generator can be walked any number of times."),
        ("Removing items while iterating",
         r"""
const nums = [2, 4, 5, 6];
for (const n of nums) {
  if (n % 2 === 0) nums.splice(nums.indexOf(n), 1);
}
console.log(nums.join(","));
""",
         r"""
const nums = [2, 4, 5, 6];
const odd = nums.filter((n) => n % 2 !== 0);
console.log(odd.join(","));
""",
         "An array's iterator is just an index. Removing the current element shifts the next one into its slot, and the loop skips it. Build a new array instead."),
        ("A generator's body doesn't run until the first `next()`",
         r"""
function* checked(xs: number[]): Generator<number> {
  if (xs.length === 0) throw new Error("empty input");
  yield* xs;
}
try {
  const gen = checked([]);
  console.log("created without error:", typeof gen);
} catch {
  console.log("caught at call");
}
""",
         r"""
function checked(xs: number[]): Generator<number> {
  if (xs.length === 0) throw new Error("empty input");
  return (function* () {
    yield* xs;
  })();
}
try {
  const gen = checked([]);
  console.log("created without error:", typeof gen);
} catch {
  console.log("caught at call");
}
""",
         "Calling a generator function only creates the generator — the validation ran later, far from the bad call. Validate in an ordinary function that then returns the generator."),
    ],
    later=[
        "**Week 24 — Iterator helpers.** `map`, `filter` and `take` built into iterators.",
        "**Week 24 — Generic data structures.** Making your own collections iterable.",
        "**Week 26 — Async iteration.** `for await`, and generators that `await`.",
    ],
)


_deepen(
    "ts_ds_generics",
    why=r"""
A stack of numbers and a stack of tasks differ only in what they hold. Written
once with a type parameter, the structure is correct for every element type,
and the compiler still knows that `pop()` on a `Stack<Task>` gives a `Task`.

Two rules carry the rest of the chapter. First, the structure's invariants —
the heap order, the queue's head, the list's size — belong behind `#private`
fields, or any caller can break them. Second, `T` is erased at runtime, so
anything that depends on the element type (how to order, how to compare) has
to be passed in as a function.
""",
    examples=[
        ("A queue with O(1) dequeue",
         r"""
class Queue<T> {
  #items: (T | undefined)[] = [];
  #head = 0;
  enqueue(item: T): void {
    this.#items.push(item);
  }
  dequeue(): T | undefined {
    if (this.#head === this.#items.length) return undefined;
    const item = this.#items[this.#head];
    this.#items[this.#head++] = undefined;
    if (this.#head > 32 && this.#head * 2 > this.#items.length) {
      this.#items = this.#items.slice(this.#head);
      this.#head = 0;
    }
    return item;
  }
  get size(): number {
    return this.#items.length - this.#head;
  }
}
const q = new Queue<string>();
for (const job of ["build", "test", "ship"]) q.enqueue(job);
console.log(q.dequeue(), q.dequeue(), q.size);
const big = new Queue<number>();
for (let i = 0; i < 100000; i++) big.enqueue(i);
let drained = 0;
while (big.dequeue() !== undefined) drained++;
console.log(drained, big.size);
""", [""],
         "A head index instead of `shift()` makes each dequeue constant time; the array is compacted once the dead prefix is more than half of it."),
        ("A linked list that is iterable",
         r"""
type ListNode<T> = { value: T; next: ListNode<T> | null };
class LinkedList<T> implements Iterable<T> {
  #head: ListNode<T> | null = null;
  #size = 0;
  prepend(value: T): this {
    this.#head = { value, next: this.#head };
    this.#size++;
    return this;
  }
  reverse(): this {
    let prev: ListNode<T> | null = null;
    let cur = this.#head;
    while (cur) {
      const next: ListNode<T> | null = cur.next;
      cur.next = prev;
      prev = cur;
      cur = next;
    }
    this.#head = prev;
    return this;
  }
  *[Symbol.iterator](): Generator<T> {
    for (let n = this.#head; n; n = n.next) yield n.value;
  }
  get size(): number {
    return this.#size;
  }
}
const list = new LinkedList<number>().prepend(3).prepend(2).prepend(1);
console.log([...list].join(" -> "), "| reversed:", [...list.reverse()].join(" -> "), "| size", list.size);
""", [""],
         "`implements Iterable<T>` makes the compiler check the `[Symbol.iterator]` method, and from then on the list works with spread and `for…of` like a built-in."),
        ("A generic LRU cache on top of `Map`",
         r"""
class LruCache<K, V> {
  readonly #limit: number;
  #map = new Map<K, V>();
  constructor(limit: number) {
    this.#limit = limit;
  }
  get(key: K): V | undefined {
    if (!this.#map.has(key)) return undefined;
    const value = this.#map.get(key) as V;
    this.#map.delete(key);
    this.#map.set(key, value);
    return value;
  }
  set(key: K, value: V): void {
    this.#map.delete(key);
    this.#map.set(key, value);
    if (this.#map.size > this.#limit) {
      const oldest = this.#map.keys().next();
      if (!oldest.done) this.#map.delete(oldest.value);
    }
  }
  keys(): K[] {
    return [...this.#map.keys()];
  }
}
const cache = new LruCache<string, number>(2);
cache.set("a", 1);
cache.set("b", 2);
cache.get("a");
cache.set("c", 3);
console.log(cache.keys().join(","), cache.get("b"));
""", [""],
         "A `Map` remembers insertion order, so re-inserting on every read keeps the least recently used key first. Reading `a` saved it; `b` was evicted."),
    ],
    errors=[
        (2345, r"""
class Stack<T> {
  #items: T[] = [];
  push(item: T): void {
    this.#items.push(item);
  }
}
const s = new Stack<number>();
s.push("3");
""", "The element type chosen at construction is checked on every call."),
        (18013, r"""
class Stack<T> {
  #items: T[] = [];
  push(item: T): void {
    this.#items.push(item);
  }
}
const s = new Stack<number>();
s.#items.length = 0;
""", "Outside the class body a `#` field doesn't exist, for the compiler or for the engine."),
        (2532, r"""
class Stack<T> {
  #items: T[] = [];
  push(item: T): void {
    this.#items.push(item);
  }
  pop(): T | undefined {
    return this.#items.pop();
  }
}
const s = new Stack<number>();
s.push(4);
console.log(s.pop().toFixed(1));
""", "`pop` admits it can come back empty, so the caller has to handle `undefined` — with `?.`, `??`, or a size check."),
    ],
    pitfalls=[
        ("`Stack<any>` to make an error go away",
         r"""
class Stack<T> {
  #items: T[] = [];
  push(item: T): void {
    this.#items.push(item);
  }
  pop(): T | undefined {
    return this.#items.pop();
  }
}
const s = new Stack<any>();
s.push(5);
try {
  console.log(s.pop().toUpperCase());
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         (r"""
class Stack<T> {
  #items: T[] = [];
  push(item: T): void {
    this.#items.push(item);
  }
  pop(): T | undefined {
    return this.#items.pop();
  }
}
const s = new Stack<number>();
s.push(5);
console.log(s.pop()?.toUpperCase());
""", 2339),
         "With `any` the mistake reached runtime. With the real element type, the compiler rejects it before it runs."),
        ("The default sort compares strings",
         r"""
class SortedList<T> {
  #items: T[] = [];
  add(item: T): this {
    this.#items.push(item);
    this.#items.sort();
    return this;
  }
  toString(): string {
    return this.#items.join(",");
  }
}
console.log(String(new SortedList<number>().add(10).add(2).add(33)));
""",
         r"""
class SortedList<T> {
  #items: T[] = [];
  readonly #compare: (a: T, b: T) => number;
  constructor(compare: (a: T, b: T) => number) {
    this.#compare = compare;
  }
  add(item: T): this {
    this.#items.push(item);
    this.#items.sort(this.#compare);
    return this;
  }
  toString(): string {
    return this.#items.join(",");
  }
}
console.log(String(new SortedList<number>((a, b) => a - b).add(10).add(2).add(33)));
""",
         "`sort()` with no comparator turns elements into strings, and `\"10\" < \"2\"`. The class can't know how to order an arbitrary `T`, so the caller must say."),
        ("Handing out the internal array",
         r"""
class SortedList {
  #items: number[] = [];
  add(n: number): this {
    this.#items.push(n);
    this.#items.sort((a, b) => a - b);
    return this;
  }
  get items(): number[] {
    return this.#items;
  }
}
const list = new SortedList().add(9).add(5);
list.items.push(1);
console.log(list.items.join(","));
""",
         r"""
class SortedList {
  #items: number[] = [];
  add(n: number): this {
    this.#items.push(n);
    this.#items.sort((a, b) => a - b);
    return this;
  }
  get items(): number[] {
    return [...this.#items];
  }
}
const list = new SortedList().add(9).add(5);
list.items.push(1);
console.log(list.items.join(","));
""",
         "`#items` was private, but the getter gave away the array itself, and the caller broke \"always sorted\". Return a copy (or a `readonly number[]` view)."),
    ],
    later=[
        "**Week 24 — Heaps and priority queues.** A comparator-driven binary heap over `T`.",
        "**Week 24 — Iterator helpers.** Lazy pipelines over your own iterable collections.",
        "**Week 27 — Capstone.** Choosing and composing these structures in one program.",
    ],
)


_deepen(
    "ts_errors",
    why=r"""
A function can't always do what it was asked: the input is malformed, the file
is missing, the number is out of range. Returning a special value (`-1`, `null`)
works until a caller forgets to check it. Throwing stops the function
immediately and unwinds through every caller until one of them has a `catch` —
so the code in between can be written for the success path only.

TypeScript adds one important rule: a function's type doesn't say what it can
throw, and JavaScript can throw *anything*, so a caught value is `unknown`. And
`finally` guarantees cleanup runs whichever way the block is left.
""",
    examples=[
        ("`finally` runs on every path",
         r"""
const log: string[] = [];
function load(raw: string): number {
  log.push("open");
  try {
    const n = JSON.parse(raw) as number;
    log.push("parsed");
    return n;
  } catch {
    log.push("bad input");
    return -1;
  } finally {
    log.push("close");
  }
}
console.log(load("42"), load("{"), log.join(" > "));
""", [""],
         "Both calls ran `close` — after a `return` from `try` and after one from `catch`. (A `catch` that doesn't need the error may omit the binding.)"),
        ("An error unwinds through its callers",
         r"""
function level3(): number {
  throw new Error("disk full");
}
function level2(): number {
  const v = level3();
  console.log("level2 continues");
  return v;
}
function level1(): string {
  try {
    return "ok " + level2();
  } catch (e) {
    return "level1 caught: " + (e instanceof Error ? e.message : String(e));
  }
}
console.log(level1());
""", [""],
         "`level2` has no `catch`, so the rest of it never ran. The nearest handler up the call stack took the error."),
        ("Anything can be thrown",
         r"""
function describe(e: unknown): string {
  if (e instanceof Error) return `${e.name}: ${e.message}`;
  if (typeof e === "string") return "a string: " + e;
  if (typeof e === "object" && e !== null && "code" in e) return "an object with code " + String(e.code);
  return "something else: " + String(e);
}
const throwers: (() => void)[] = [
  () => { throw new TypeError("wrong type"); },
  () => { throw "oops"; },
  () => { throw { code: 7 }; },
  () => { throw 42; },
];
for (const f of throwers) {
  try {
    f();
  } catch (e) {
    console.log(describe(e));
  }
}
""", [""],
         "This is why `e` is `unknown`: a library may throw a string or a plain object. Narrow with `instanceof`, `typeof` and `in`, exactly as with any other `unknown`."),
    ],
    errors=[
        (18046, r"""
try {
  JSON.parse("{");
} catch (e) {
  console.log(e.message);
}
""", "Under `strict` (`useUnknownInCatchVariables`) the caught value is `unknown`. Narrow with `e instanceof Error` first."),
        (1196, r"""
try {
  JSON.parse("{");
} catch (e: Error) {
  console.log(e.message);
}
""", "You can't annotate what was thrown — nothing guarantees it. Only `unknown` (or `any`) is allowed."),
        (2366, r"""
function parse(s: string): number {
  try {
    return JSON.parse(s) as number;
  } catch (e) {
    console.log("bad input");
  }
}
""", "The `catch` path falls off the end without a value. Return one, or rethrow."),
    ],
    pitfalls=[
        ("A `return` in `finally` swallows the error",
         r"""
function risky(): string {
  try {
    throw new Error("lost");
  } finally {
    return "finally wins";
  }
}
try {
  console.log(risky());
} catch (e) {
  console.log("caught: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
function risky(): string {
  try {
    throw new Error("lost");
  } finally {
    console.log("cleanup");
  }
}
try {
  console.log(risky());
} catch (e) {
  console.log("caught: " + (e instanceof Error ? e.message : String(e)));
}
""",
         "Leaving `finally` with `return` replaces whatever was in flight, error included. Use `finally` for cleanup only."),
        ("A `catch` that hides a bug",
         r"""
function total(json: string): number {
  try {
    const items = JSON.parse(json) as { price: number }[];
    return items.reduce((sum, i) => sum + i.price, 0);
  } catch {
    return 0;
  }
}
console.log(total('[{"price": 2}, {"price": 3}]'), total("not json"), total('{"price": 5}'));
""",
         r"""
function total(json: string): number {
  let items: { price: number }[];
  try {
    items = JSON.parse(json) as { price: number }[];
  } catch (e) {
    if (e instanceof SyntaxError) return 0;
    throw e;
  }
  return items.reduce((sum, i) => sum + i.price, 0);
}
for (const input of ['[{"price": 2}, {"price": 3}]', "not json", '{"price": 5}']) {
  try {
    console.log(total(input));
  } catch (e) {
    console.log("error: " + (e instanceof Error ? e.message : String(e)));
  }
}
""",
         "The catch-all meant to handle bad JSON also swallowed a `TypeError` — the input was an object, not an array. Keep the `try` around the one call that can fail, and catch only the error you expect."),
        ("Throwing a string loses the stack",
         r"""
function config(): string {
  throw "config missing";
}
try {
  config();
} catch (e) {
  console.log(e instanceof Error, typeof (e as { stack?: unknown }).stack);
}
""",
         r"""
function config(): string {
  throw new Error("config missing");
}
try {
  config();
} catch (e) {
  console.log(e instanceof Error, typeof (e as { stack?: unknown }).stack);
}
""",
         "Only `Error` objects record where they were thrown. A string gives the handler a message and nothing else."),
    ],
    later=[
        "**Week 25 — Result types and typed errors.** Making failure part of a function's type.",
        "**Week 25 — Error cause.** Wrapping a low-level error without losing it.",
        "**Week 25 — Resource management.** `using` as a `finally` you can't forget.",
        "**Week 26 — Promises.** A rejected promise is thrown at the `await`.",
    ],
)


_deepen(
    "ts_error_types",
    why=r"""
`function parsePort(raw: string): number` says nothing about what happens on
`"abc"`. If it throws, the caller has to know that from documentation — the
compiler will happily let them forget. Returning a `Result` puts the failure in
the return type, and because it's a discriminated union, the value can't even be
read until the caller has checked which case it got.

Exceptions still have a place — bugs and truly unrecoverable states — and for
those, error *classes* give each failure a name, extra fields and an
`instanceof` test, so a handler can tell a "not found" from a "forbidden".
""",
    examples=[
        ("Collecting every validation error with `Result`",
         r"""
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
type Person = { name: string; age: number };
function parsePerson(line: string): Result<Person> {
  const [name = "", ageText = ""] = line.split(",");
  if (!name.trim()) return { ok: false, error: "missing name" };
  const age = Number(ageText);
  if (!Number.isInteger(age) || age < 0) return { ok: false, error: `bad age "${ageText}"` };
  return { ok: true, value: { name: name.trim(), age } };
}
const lines = ["ana,31", ",20", "ben,x", "cy,7"];
const results = lines.map(parsePerson);
const people = results.flatMap((r) => (r.ok ? [r.value] : []));
const problems = results.flatMap((r, i) => (r.ok ? [] : [`line ${i + 1}: ${r.error}`]));
console.log(people.map((p) => p.name).join(","), "|", problems.join("; "));
""", [""],
         "An exception would have stopped at line 2. Results are ordinary values, so every line is checked and every problem reported."),
        ("A hierarchy of error classes",
         r"""
class AppError extends Error {
  constructor(message: string) {
    super(message);
    this.name = new.target.name;
  }
}
class NotFound extends AppError {
  readonly id: string;
  constructor(id: string) {
    super(`no record ${id}`);
    this.id = id;
  }
}
class Forbidden extends AppError {}
function status(e: unknown): string {
  if (e instanceof NotFound) return `404 (${e.id})`;
  if (e instanceof Forbidden) return "403";
  if (e instanceof AppError) return "400";
  return "500";
}
const failures: unknown[] = [new NotFound("u7"), new Forbidden("admins only"), new AppError("bad request"), new RangeError("bug")];
for (const e of failures) console.log(status(e), String(e));
""", [""],
         "`new.target.name` names each error after the class actually constructed, so `String(e)` says `NotFound: …` without every subclass repeating it. Check the most specific class first."),
        ("A union of error codes, handled exhaustively",
         r"""
type NameError = { kind: "empty" } | { kind: "tooLong"; max: number } | { kind: "badChar"; char: string };
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
function checkName(s: string): Result<string, NameError> {
  if (s.length === 0) return { ok: false, error: { kind: "empty" } };
  if (s.length > 8) return { ok: false, error: { kind: "tooLong", max: 8 } };
  const bad = [...s].find((c) => !/[a-z]/.test(c));
  if (bad !== undefined) return { ok: false, error: { kind: "badChar", char: bad } };
  return { ok: true, value: s };
}
function message(e: NameError): string {
  switch (e.kind) {
    case "empty": return "name is required";
    case "tooLong": return `at most ${e.max} letters`;
    case "badChar": return `"${e.char}" is not allowed`;
    default: {
      const unreachable: never = e;
      return unreachable;
    }
  }
}
for (const s of ["ana", "", "bartholomew", "jo3"]) {
  const r = checkName(s);
  console.log(r.ok ? "ok: " + r.value : "error: " + message(r.error));
}
""", [""],
         "Each error carries exactly the data its message needs. The `never` check means adding a fourth kind is a compile error here until it has a message."),
    ],
    errors=[
        (2339, r"""
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
declare function parsePort(raw: string): Result<number>;
const r = parsePort("8080");
console.log(r.value + 1);
""", "`value` only exists on the `ok: true` case. Check `r.ok` first and the compiler narrows `r`."),
        (2322, r"""
type LoadError = { kind: "missing" } | { kind: "timeout"; ms: number };
function message(e: LoadError): string {
  switch (e.kind) {
    case "missing":
      return "not found";
    default: {
      const unreachable: never = e;
      return unreachable;
    }
  }
}
""", "The `timeout` case isn't handled, so `e` is not `never` in the default branch. This is the error that makes adding a case safe."),
    ],
    pitfalls=[
        ("An error class without a `name`",
         r"""
class ParseError extends Error {
  readonly line: number;
  constructor(line: number, message: string) {
    super(message);
    this.line = line;
  }
}
console.log(String(new ParseError(3, "unexpected ','")));
""",
         r"""
class ParseError extends Error {
  readonly line: number;
  constructor(line: number, message: string) {
    super(message);
    this.name = "ParseError";
    this.line = line;
  }
}
console.log(String(new ParseError(3, "unexpected ','")));
""",
         "`name` is inherited from `Error.prototype`, so logs and stack traces say plain `Error`. Set it in the constructor."),
        ("Ignoring a returned `Result`",
         r"""
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
function save(amount: number): Result<number> {
  return amount < 0 ? { ok: false, error: "negative amount" } : { ok: true, value: amount };
}
save(-5);
console.log("saved");
""",
         r"""
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
function save(amount: number): Result<number> {
  return amount < 0 ? { ok: false, error: "negative amount" } : { ok: true, value: amount };
}
const r = save(-5);
console.log(r.ok ? "saved " + r.value : "not saved: " + r.error);
""",
         "A `Result` only helps if someone looks at it; unlike an exception, dropping it is silent. Keep it in a variable, and the union forces the check before the value can be used."),
        ("Mixing `throw` and `Result` at one boundary",
         r"""
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
function readConfig(json: string): Result<{ port: number }> {
  const raw = JSON.parse(json) as { port?: unknown };
  if (typeof raw.port !== "number") return { ok: false, error: "port missing" };
  return { ok: true, value: { port: raw.port } };
}
for (const text of ['{"port": 80}', "{}", "{port"]) {
  try {
    const r = readConfig(text);
    console.log(r.ok ? "port " + r.value.port : "error: " + r.error);
  } catch (e) {
    console.log("escaped: " + (e instanceof Error ? e.name : String(e)));
  }
}
""",
         r"""
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
function readConfig(json: string): Result<{ port: number }> {
  let raw: { port?: unknown };
  try {
    raw = JSON.parse(json) as { port?: unknown };
  } catch {
    return { ok: false, error: "not JSON" };
  }
  if (typeof raw.port !== "number") return { ok: false, error: "port missing" };
  return { ok: true, value: { port: raw.port } };
}
for (const text of ['{"port": 80}', "{}", "{port"]) {
  const r = readConfig(text);
  console.log(r.ok ? "port " + r.value.port : "error: " + r.error);
}
""",
         "The signature promised a `Result`, but `JSON.parse` still threw through it. A function that returns `Result` must convert every expected failure inside, or callers need both a check and a `try`."),
    ],
    later=[
        "**Week 25 — Error cause.** Wrapping errors across layers with `{ cause }`.",
        "**Week 25 — Resource management.** Cleanup that runs whichever way a block exits.",
        "**Week 26 — Promise combinators.** `allSettled` is a list of results, one per task.",
    ],
)


_deepen(
    "ts_async",
    why=r"""
Reading a file, querying a database or waiting for a timer takes time, and
JavaScript runs your code on a single thread. If that thread stopped to wait,
nothing else could happen — no other requests, no UI. Instead, a slow operation
returns a *promise* straight away: a placeholder for a value that will arrive
(or fail) later, while the thread goes on to other work.

`async`/`await` lets that code read top to bottom anyway. `await` suspends only
the current async function, and failures surface as ordinary exceptions at the
`await`. TypeScript tracks the difference between a `Promise<number>` and a
`number`, which is what catches the most common async bug — forgetting the
`await`.
""",
    examples=[
        ("Sequential and concurrent, by their order",
         r"""
const log: string[] = [];
function task(name: string, ms: number): Promise<string> {
  log.push("start " + name);
  return new Promise<string>((resolve) =>
    setTimeout(() => {
      log.push("end " + name);
      resolve(name);
    }, ms));
}
async function sequential(): Promise<void> {
  await task("a", 20);
  await task("b", 10);
}
async function concurrent(): Promise<void> {
  await Promise.all([task("c", 20), task("d", 10)]);
}
await sequential();
log.push("|");
await concurrent();
console.log(log.join(" "));
""", [""],
         "`b` didn't start until `a` ended. `c` and `d` started together, and the shorter one finished first — concurrent total time is the longest task, not the sum."),
        ("An `async` function always returns a promise",
         r"""
async function double(n: number): Promise<number> {
  return n * 2;
}
const p = double(21);
console.log(p instanceof Promise, await p);
async function fails(): Promise<number> {
  throw new Error("nope");
}
const outcome = await fails().then(
  (v) => "value " + v,
  (e: unknown) => "rejected: " + (e instanceof Error ? e.message : String(e)),
);
console.log(outcome);
""", [""],
         "`return n * 2` became a fulfilled promise; `throw` became a rejected one. Nothing escaped synchronously from `fails()`."),
        ("Wrapping a callback API in a promise",
         r"""
function readSetting(key: string, done: (err: Error | null, value?: string) => void): void {
  const store: Record<string, string> = { theme: "dark" };
  setTimeout(() => (key in store ? done(null, store[key]) : done(new Error("no setting " + key))), 5);
}
function readSettingAsync(key: string): Promise<string> {
  return new Promise((resolve, reject) => {
    readSetting(key, (err, value) => (err ? reject(err) : resolve(value ?? "")));
  });
}
for (const key of ["theme", "font"]) {
  try {
    const value = await readSettingAsync(key);
    console.log(key + " = " + value);
  } catch (e) {
    console.log(e instanceof Error ? e.message : String(e));
  }
}
""", [""],
         "Older APIs report through a callback. `new Promise` turns \"call `done` later\" into a value you can `await`, and the callback's error into a rejection."),
    ],
    errors=[
        (1308, r"""
function main(): void {
  const n = await Promise.resolve(1);
  console.log(n);
}
""", "`await` needs an `async` function around it (or the top level of a module)."),
        (2322, r"""
async function count(): Promise<number> {
  return 3;
}
const total: number = count();
""", "Without `await` you hold the promise, not the number."),
        (1064, r"""
async function count(): number {
  return 3;
}
""", "An `async` function always returns a promise, so its declared return type must be `Promise<…>`."),
    ],
    pitfalls=[
        ("A promise in an `if`",
         (r"""
async function isAllowed(user: string): Promise<boolean> {
  return user === "admin";
}
async function open(user: string): Promise<string> {
  if (isAllowed(user)) return "opened for " + user;
  return "denied";
}
console.log(await open("guest"));
""", 2801),
         r"""
async function isAllowed(user: string): Promise<boolean> {
  return user === "admin";
}
async function open(user: string): Promise<string> {
  if (await isAllowed(user)) return "opened for " + user;
  return "denied";
}
console.log(await open("guest"));
""",
         "A promise object is always truthy, so without `await` every user would be allowed. The compiler recognises this exact mistake."),
        ("`forEach` with an async callback",
         r"""
const log: string[] = [];
async function save(id: number): Promise<void> {
  await new Promise<void>((resolve) => setTimeout(resolve, 5));
  log.push("saved " + id);
}
async function saveAll(ids: number[]): Promise<void> {
  ids.forEach(async (id) => {
    await save(id);
  });
}
await saveAll([1, 2]);
console.log("done after: [" + log.join(", ") + "]");
""",
         r"""
const log: string[] = [];
async function save(id: number): Promise<void> {
  await new Promise<void>((resolve) => setTimeout(resolve, 5));
  log.push("saved " + id);
}
async function saveAll(ids: number[]): Promise<void> {
  for (const id of ids) await save(id);
}
await saveAll([1, 2]);
console.log("done after: [" + log.join(", ") + "]");
""",
         "`forEach` ignores what its callback returns, so the promises were dropped and `saveAll` finished at once. Use `for…of` with `await` (or `Promise.all` over `map`)."),
        ("`return` without `await` inside `try`",
         r"""
async function load(): Promise<string> {
  throw new Error("offline");
}
async function main(): Promise<string> {
  try {
    return load();
  } catch {
    return "fallback";
  }
}
console.log(await main().catch((e: unknown) => "escaped: " + (e instanceof Error ? e.message : String(e))));
""",
         r"""
async function load(): Promise<string> {
  throw new Error("offline");
}
async function main(): Promise<string> {
  try {
    return await load();
  } catch {
    return "fallback";
  }
}
console.log(await main().catch((e: unknown) => "escaped: " + (e instanceof Error ? e.message : String(e))));
""",
         "`return load()` hands the promise out of the `try` before it has rejected, so the `catch` never sees the failure. `return await` keeps it inside."),
    ],
    later=[
        "**Week 26 — Promise combinators.** `all`, `allSettled`, `race`, `any` and limiting concurrency.",
        "**Week 26 — The event loop.** Why `.then` callbacks run before timers.",
        "**Week 26 — Cancellation.** Stopping work with `AbortSignal`.",
        "**Week 26 — Async iteration.** `for await` over streams of results.",
    ],
)


_deepen(
    "ts_async_patterns",
    why=r"""
Real programs rarely wait for one thing. A page loads a user *and* their orders;
a sync job fetches a thousand records; a request has to give up after two
seconds. The combinators are how you say what should happen when several
promises are in flight — and each one is really a choice of *failure
semantics*: stop at the first error (`all`), report every outcome
(`allSettled`), take whichever settles first (`race`), or the first success
(`any`).

TypeScript types each of them precisely — `Promise.all` over a tuple keeps each
position's type, and `allSettled` gives a discriminated union you narrow on
`status` — so the choice shows up in the code that uses the results.
""",
    examples=[
        ("`allSettled` reports every outcome, `all` stops at the first failure",
         r"""
function fetchPrice(sku: string): Promise<number> {
  const prices: Record<string, number> = { pen: 2, cup: 5 };
  return new Promise((resolve, reject) =>
    setTimeout(() => (sku in prices ? resolve(prices[sku]) : reject(new Error("unknown sku " + sku))), 5));
}
const skus = ["pen", "hat", "cup"];
const settled = await Promise.allSettled(skus.map(fetchPrice));
settled.forEach((r, i) => {
  const shown = r.status === "fulfilled" ? String(r.value) : "failed (" + (r.reason instanceof Error ? r.reason.message : String(r.reason)) + ")";
  console.log(skus[i] + ": " + shown);
});
try {
  const all = await Promise.all(skus.map(fetchPrice));
  console.log("all: " + all.join(","));
} catch (e) {
  console.log("all: " + (e instanceof Error ? e.message : String(e)));
}
""", [""],
         "Same three requests, two answers: `allSettled` kept both prices and the failure; `all` gave up with the one error and discarded the rest."),
        ("A timeout with `race`",
         r"""
function after<T>(ms: number, value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}
function timeout(ms: number): Promise<never> {
  return new Promise((_, reject) => setTimeout(() => reject(new Error(`timed out after ${ms} ms`)), ms));
}
function withTimeout<T>(work: Promise<T>, ms: number): Promise<T> {
  return Promise.race([work, timeout(ms)]);
}
for (const [label, ms] of [["fast", 10], ["slow", 60]] as const) {
  try {
    console.log(await withTimeout(after(ms, label + " reply"), 30));
  } catch (e) {
    console.log(label + ": " + (e instanceof Error ? e.message : String(e)));
  }
}
""", [""],
         "`timeout` returns `Promise<never>` — it can only reject — so racing it against `Promise<T>` is still a `Promise<T>`."),
        ("At most N at a time",
         r"""
async function mapPool<T, U>(items: T[], limit: number, f: (item: T) => Promise<U>): Promise<U[]> {
  const results: U[] = new Array(items.length);
  let next = 0;
  async function worker(): Promise<void> {
    while (next < items.length) {
      const i = next++;
      results[i] = await f(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return results;
}
let active = 0;
let peak = 0;
const out = await mapPool([30, 10, 20, 10, 5], 2, async (ms) => {
  active++;
  peak = Math.max(peak, active);
  await new Promise<void>((resolve) => setTimeout(resolve, ms));
  active--;
  return ms * 2;
});
console.log(out.join(","), "| peak in flight: " + peak);
""", [""],
         "`Promise.all(items.map(f))` would start all five at once. Two workers pull the next index whenever they finish, so no more than two run, and results still land in input order."),
    ],
    errors=[
        (2339, r"""
async function main(): Promise<void> {
  const settled = await Promise.allSettled([Promise.resolve(1)]);
  for (const r of settled) console.log(r.value);
}
""", "A settled result might be the rejected kind, which has `reason` and no `value`. Narrow on `r.status === \"fulfilled\"`."),
        (2322, r"""
declare function count(): Promise<number>;
declare function label(): Promise<string>;
async function main(): Promise<void> {
  const [n, s]: [string, number] = await Promise.all([count(), label()]);
  console.log(n, s);
}
""", "`Promise.all` over a tuple keeps each position's type — here `[number, string]` — so swapped annotations are caught."),
    ],
    pitfalls=[
        ("Expecting `map(async …)` to run one at a time",
         r"""
const log: string[] = [];
async function upload(id: number): Promise<void> {
  log.push("start " + id);
  await new Promise<void>((resolve) => setTimeout(resolve, 10));
  log.push("end " + id);
}
await Promise.all([1, 2, 3].map(async (id) => await upload(id)));
console.log(log.join(", "));
""",
         r"""
const log: string[] = [];
async function upload(id: number): Promise<void> {
  log.push("start " + id);
  await new Promise<void>((resolve) => setTimeout(resolve, 10));
  log.push("end " + id);
}
for (const id of [1, 2, 3]) await upload(id);
console.log(log.join(", "));
""",
         "`map` calls every callback immediately; the `await` inside each only pauses that one callback. When order matters (or the server can't take the load), loop with `await`."),
        ("`race` doesn't stop the loser",
         r"""
const log: string[] = [];
const work = new Promise<string>((resolve) =>
  setTimeout(() => {
    log.push("work ran to the end");
    resolve("data");
  }, 40));
const timer = new Promise<string>((resolve) => setTimeout(() => resolve("timeout"), 10));
console.log(await Promise.race([work, timer]));
await new Promise<void>((resolve) => setTimeout(resolve, 60));
console.log(log.join("; ") || "(no side effects)");
""",
         r"""
const log: string[] = [];
const controller = new AbortController();
const work = new Promise<string>((resolve) =>
  setTimeout(() => {
    if (controller.signal.aborted) {
      log.push("work skipped: aborted");
      return;
    }
    log.push("work ran to the end");
    resolve("data");
  }, 40));
const timer = new Promise<string>((resolve) => setTimeout(() => resolve("timeout"), 10));
const winner = await Promise.race([work, timer]);
if (winner === "timeout") controller.abort();
console.log(winner);
await new Promise<void>((resolve) => setTimeout(resolve, 60));
console.log(log.join("; ") || "(no side effects)");
""",
         "A promise has no \"cancel\". `race` only stops *waiting*; the losing work still runs and still has side effects. Pass it a signal it checks."),
        ("`allSettled` never rejects",
         r"""
try {
  const results = await Promise.allSettled([Promise.reject(new Error("db down")), Promise.resolve(1)]);
  console.log("success? " + results.length + " results");
} catch {
  console.log("caught a failure");
}
""",
         r"""
const results = await Promise.allSettled([Promise.reject(new Error("db down")), Promise.resolve(1)]);
const failed = results.filter((r) => r.status === "rejected");
console.log(failed.length > 0 ? failed.length + " of " + results.length + " failed" : "all ok");
""",
         "Every failure is folded into the result array, so a surrounding `catch` never fires. Inspect `status` yourself."),
    ],
    later=[
        "**Week 26 — The event loop.** When promise callbacks and timers actually run.",
        "**Week 26 — Cancellation.** `AbortSignal.timeout` and `AbortSignal.any`.",
        "**Week 26 — Project.** `fetchAll.ts`: a pool with timeouts and retries on a virtual clock.",
    ],
)
