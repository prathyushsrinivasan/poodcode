# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — per-chapter reading kinds, Month 6 (TS_MASTERY_ROADMAP
# X-10, X-11): predict / diagnose / retype / design / fix for the runtime and
# architecture chapters of weeks 23-26 (classes, iterators and data
# structures, errors and resources, async), topping each chapter up to its
# target.
#
# Weeks 23-26 run at strict+indexed. Decorators and constructor parameter
# properties are not erasable, so exercises that use them are type-only (no
# inputs). The async programs of week 26 are ordered by construction — await
# chains, microtasks before macrotasks, Promise.all's result order — never by
# racing timers of different lengths. Helpers are in
# mastery_ts_chapter_kit.py; exec()'d by gen_seed.py with the other
# tools/mastery_ts_x_m*.py files.
# ---------------------------------------------------------------------------


# ---- Week 23: classes -------------------------------------------------------

_xpr("ts_classes", 1, "A readonly field's literal", r'''
class Circle {
  readonly name = "circle";
  readonly r: number;
  constructor(r: number) {
    this.r = r;
  }
}
const c = new Circle(2);
''', "c.name", '"circle"',
     hints=["A `readonly` field can never be reassigned, so its initialiser is not widened.",
            "The type is the literal itself."])

_xpr("ts_classes", 2, "A method that returns this", r'''
class Builder {
  parts: string[] = [];
  add(p: string): this {
    this.parts.push(p);
    return this;
  }
}
class HtmlBuilder extends Builder {
  wrap(): string {
    return "<" + this.parts.join("") + ">";
  }
}
const b = new HtmlBuilder().add("p");
''', "b", "HtmlBuilder",
     hints=["`this` as a return type means \"whatever class the method was called on\".",
            "It was called on an `HtmlBuilder`, not a `Builder`."])

_xpr("ts_classes", 3, "An array of two classes", r'''
class Circle {
  readonly r: number;
  constructor(r: number) {
    this.r = r;
  }
}
class Square {
  readonly side: number;
  constructor(side: number) {
    this.side = side;
  }
}
const shapes = [new Circle(1), new Square(2), new Circle(3)];
''', "shapes", "(Circle | Square)[]",
     hints=["A class name is also the type of its instances.",
            "The elements are of two different shapes, so the array's element type is a union."])

_xrt("ts_classes", 1, "A tally with honest fields", "Replace each `any` with the type the class really stores and returns.",
     r'''
class Tally {
  #counts: any = new Map();
  add(word: string): void {
    this.#counts.set(word, (this.#counts.get(word) ?? 0) + 1);
  }
  count(word: string): any {
    return this.#counts.get(word) ?? 0;
  }
  get distinct(): any {
    return this.#counts.size;
  }
}
const t = new Tally();
for (const w of input.split(/\s+/)) t.add(w);
console.log(t.distinct, t.count("a"));
''', r'''
class Tally {
  #counts: Map<string, number> = new Map();
  add(word: string): void {
    this.#counts.set(word, (this.#counts.get(word) ?? 0) + 1);
  }
  count(word: string): number {
    return this.#counts.get(word) ?? 0;
  }
  get distinct(): number {
    return this.#counts.size;
  }
}
const t = new Tally();
for (const w of input.split(/\s+/)) t.add(w);
console.log(t.distinct, t.count("a"));
''', "type _1 = Expect<Equal<ReturnType<Tally[\"count\"]>, number>>;\n"
     "type _2 = Expect<Equal<Tally[\"distinct\"], number>>;",
     ["a b a c a", "x y", "a"],
     hints=["The private field maps each word to how many times it was seen.",
            "`#counts: Map<string, number>`; `count` and `distinct` both return a number."])

_xrt("ts_classes", 2, "Money that only adds money", "Type the constructor and `plus` so only amounts in cents and other `Money` values get in.",
     r'''
class Money {
  readonly cents: number;
  constructor(cents: any) {
    this.cents = cents;
  }
  plus(other: any): Money {
    return new Money(this.cents + other.cents);
  }
  format(): string {
    return (this.cents / 100).toFixed(2);
  }
}
let total = new Money(0);
for (const t of input.split(/\s+/)) total = total.plus(new Money(Number(t)));
console.log(total.format());
''', r'''
class Money {
  readonly cents: number;
  constructor(cents: number) {
    this.cents = cents;
  }
  plus(other: Money): Money {
    return new Money(this.cents + other.cents);
  }
  format(): string {
    return (this.cents / 100).toFixed(2);
  }
}
let total = new Money(0);
for (const t of input.split(/\s+/)) total = total.plus(new Money(Number(t)));
console.log(total.format());
''', "type _1 = Expect<Equal<ConstructorParameters<typeof Money>[0], number>>;\n"
     "type _2 = Expect<Equal<Parameters<Money[\"plus\"]>[0], Money>>;",
     ["150 275", "99", "0 5 -5"],
     hints=["What does `this.cents = cents` need `cents` to be?",
            "A class name is a type: `plus(other: Money)`."])

_xrt("ts_classes", 3, "Largest by the interface", "Type `largest` against the `Shape` interface rather than `any`.",
     r'''
interface Shape {
  readonly name: string;
  area(): number;
}
class Rect implements Shape {
  readonly name = "rect";
  readonly w: number;
  readonly h: number;
  constructor(w: number, h: number) {
    this.w = w;
    this.h = h;
  }
  area(): number {
    return this.w * this.h;
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
function largest(shapes: any): any {
  let best: any = undefined;
  for (const s of shapes) if (best === undefined || s.area() > best.area()) best = s;
  return best;
}
const [a = 0, b = 0, c = 0] = input.split(/\s+/).map(Number);
const big = largest([new Rect(a, b), new Square(c)]);
console.log(big === undefined ? "none" : big.name + " " + big.area());
''', r'''
interface Shape {
  readonly name: string;
  area(): number;
}
class Rect implements Shape {
  readonly name = "rect";
  readonly w: number;
  readonly h: number;
  constructor(w: number, h: number) {
    this.w = w;
    this.h = h;
  }
  area(): number {
    return this.w * this.h;
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
function largest(shapes: Shape[]): Shape | undefined {
  let best: Shape | undefined = undefined;
  for (const s of shapes) if (best === undefined || s.area() > best.area()) best = s;
  return best;
}
const [a = 0, b = 0, c = 0] = input.split(/\s+/).map(Number);
const big = largest([new Rect(a, b), new Square(c)]);
console.log(big === undefined ? "none" : big.name + " " + big.area());
''', "type _1 = Expect<Equal<Parameters<typeof largest>[0], Shape[]>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof largest>, Shape | undefined>>;",
     ["2 3 2", "1 1 5", "4 4 4"],
     hints=["Both classes `implements Shape`, so the function can ask for the interface.",
            "An empty list has no largest: the result is `Shape | undefined`."])

_xdz("ts_classes", 1, "What a queue promises", "Write the `Queue` interface that `ArrayQueue` implements, from how the class and its callers use it.",
     r'''
interface Queue {
  enqueue(x: number): void;
  dequeue(): number | undefined;
  readonly size: number;
}
class ArrayQueue implements Queue {
  #items: number[] = [];
  enqueue(x: number): void {
    this.#items.push(x);
  }
  dequeue(): number | undefined {
    return this.#items.shift();
  }
  get size(): number {
    return this.#items.length;
  }
}
const q: Queue = new ArrayQueue();
for (const t of input.split(/\s+/)) q.enqueue(Number(t));
const first = q.dequeue();
console.log(first, q.size);
''', r'''interface Queue {
  enqueue(x: number): void;
  dequeue(): number | undefined;
  readonly size: number;
}''', "type _1 = Expect<Equal<keyof Queue, \"enqueue\" | \"dequeue\" | \"size\">>;\n"
      "type _2 = Expect<Equal<ReturnType<Queue[\"dequeue\"]>, number | undefined>>;\n"
      "type _3 = Expect<Equal<Pick<Queue, \"size\">, { readonly size: number }>>;",
     ["3 1 2", "7"],
     hints=["Callers only see what the interface lists: they enqueue, dequeue and read `size`.",
            "`size` is a getter with no setter — in an interface that is a `readonly` property."])

_xdz("ts_classes", 2, "Comparable versions", "Write the generic `Comparable` interface that `Version` implements.",
     r'''
interface Comparable<T> {
  compareTo(other: T): number;
}
class Version implements Comparable<Version> {
  readonly major: number;
  readonly minor: number;
  constructor(text: string) {
    const [a = 0, b = 0] = text.split(".").map(Number);
    this.major = a;
    this.minor = b;
  }
  compareTo(other: Version): number {
    return this.major - other.major || this.minor - other.minor;
  }
  toString(): string {
    return this.major + "." + this.minor;
  }
}
const vs = input.split(/\s+/).map((t) => new Version(t));
vs.sort((a, b) => a.compareTo(b));
console.log(vs.join(" "));
''', r'''interface Comparable<T> {
  compareTo(other: T): number;
}''', "type _1 = Expect<Equal<Parameters<Comparable<Version>[\"compareTo\"]>[0], Version>>;\n"
      "type _2 = Expect<Equal<ReturnType<Comparable<string>[\"compareTo\"]>, number>>;\n"
      "type _3 = Expect<Equal<keyof Comparable<number>, \"compareTo\">>;",
     ["1.10 1.2 0.9", "2.0", "3.1 3.1 1.0"],
     hints=["`implements Comparable<Version>` — the interface takes the type to compare against.",
            "One method: it takes a `T` and returns a number, negative/zero/positive."])

_xfx("ts_classes", 1, "An override that forgot its parent",
     "`CappedCounter` should count words like `WordCounter` but stop at 3 of any one word. It counts nothing at all.",
     r'''
class WordCounter {
  counts = new Map<string, number>();
  add(w: string): void {
    this.counts.set(w, (this.counts.get(w) ?? 0) + 1);
  }
}
class CappedCounter extends WordCounter {
  override add(w: string): void {
    if ((this.counts.get(w) ?? 0) >= 3) return;
  }
}
const c = new CappedCounter();
for (const w of input.split(/\s+/)) c.add(w);
console.log([...c.counts].map(([w, n]) => w + "=" + n).join(" ") || "empty");
''', r'''
class WordCounter {
  counts = new Map<string, number>();
  add(w: string): void {
    this.counts.set(w, (this.counts.get(w) ?? 0) + 1);
  }
}
class CappedCounter extends WordCounter {
  override add(w: string): void {
    if ((this.counts.get(w) ?? 0) >= 3) return;
    super.add(w);
  }
}
const c = new CappedCounter();
for (const w of input.split(/\s+/)) c.add(w);
console.log([...c.counts].map(([w, n]) => w + "=" + n).join(" ") || "empty");
''', ["a a a a b", "x", "b a b"],
     hints=["An override replaces the parent's method entirely.",
            "After the cap check, hand the real work to `super.add(w)`."])

_xfx("ts_classes", 2, "Two equal points, two entries",
     "It should print how many DIFFERENT points the input lists (pairs of numbers). Repeated points are counted twice.",
     r'''
class Point {
  readonly x: number;
  readonly y: number;
  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
  }
}
const nums = input.split(/\s+/).map(Number);
const seen = new Set<Point>();
for (let i = 0; i + 1 < nums.length; i += 2) seen.add(new Point(nums[i] ?? 0, nums[i + 1] ?? 0));
console.log(seen.size);
''', r'''
class Point {
  readonly x: number;
  readonly y: number;
  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
  }
  get key(): string {
    return this.x + "," + this.y;
  }
}
const nums = input.split(/\s+/).map(Number);
const seen = new Set<string>();
for (let i = 0; i + 1 < nums.length; i += 2) seen.add(new Point(nums[i] ?? 0, nums[i + 1] ?? 0).key);
console.log(seen.size);
''', ["1 2 1 2 3 4", "0 0", "5 5 5 5 5 5"],
     hints=["Every `new Point(...)` is a new object, and a `Set` compares objects by identity.",
            "Store a value that compares by content — a string key like `\"x,y\"`."])


# ---- Week 23: this, getters and setters -------------------------------------

_xpr("ts_this_accessors", 1, "A getter's inferred type", r'''
class Level {
  n = 0;
  get label() {
    return this.n > 0 ? "up" : "down";
  }
}
const lv = new Level();
const shown = lv.label;
''', "shown", '"up" | "down"',
     hints=["The getter has no return annotation, so its type is inferred from the `return` expression.",
            "Each branch of the conditional is a string literal, and the inferred type keeps both."])

_xpr("ts_this_accessors", 2, "A method pulled off its object", r'''
class Counter {
  count = 0;
  inc(this: Counter): void {
    this.count++;
  }
}
const inc = new Counter().inc;
''', "inc", "(this: Counter) => void",
     hints=["Taking a method off an instance gives you the bare function.",
            "The declared `this` parameter is part of the function's type."])

_xrt("ts_this_accessors", 1, "Say what `this` must be", "Replace the `any` on the `this` parameter with the shape the function really reads.",
     r'''
function sumItems(this: any): number {
  return this.items.reduce((s: number, n: number) => s + n, 0);
}
const cart = { items: input.split(/\s+/).map(Number), sum: sumItems };
console.log(cart.sum());
''', r'''
function sumItems(this: { items: number[] }): number {
  return this.items.reduce((s, n) => s + n, 0);
}
const cart = { items: input.split(/\s+/).map(Number), sum: sumItems };
console.log(cart.sum());
''', "type _1 = Expect<Equal<ThisParameterType<typeof sumItems>, { items: number[] }>>;",
     ["1 2 3", "10", "-4 4"],
     hints=["A `this` parameter is erased at runtime, but it types every use of `this` inside.",
            "The function reads `this.items` and adds them up: `this: { items: number[] }`."])

_xrt("ts_this_accessors", 2, "An accessor pair with a real type", "Type the Celsius accessor pair; it stores and returns degrees.",
     r'''
class Temperature {
  #celsius = 0;
  get celsius(): any {
    return this.#celsius;
  }
  set celsius(value: any) {
    this.#celsius = value;
  }
  set fahrenheit(value: number) {
    this.celsius = (value - 32) * 5 / 9;
  }
}
const t = new Temperature();
for (const f of input.split(/\s+/)) {
  t.fahrenheit = Number(f);
  console.log(t.celsius.toFixed(1));
}
''', r'''
class Temperature {
  #celsius = 0;
  get celsius(): number {
    return this.#celsius;
  }
  set celsius(value: number) {
    this.#celsius = value;
  }
  set fahrenheit(value: number) {
    this.celsius = (value - 32) * 5 / 9;
  }
}
const t = new Temperature();
for (const f of input.split(/\s+/)) {
  t.fahrenheit = Number(f);
  console.log(t.celsius.toFixed(1));
}
''', "type _1 = Expect<Equal<Temperature[\"celsius\"], number>>;",
     ["212 32", "-40", "98.6"],
     hints=["Reading `t.celsius` has the getter's return type.",
            "Both halves of the pair are numbers of degrees."])

_xrt("ts_this_accessors", 3, "A callback that keeps its object", "Type the arrow-function field that is handed to `forEach`.",
     r'''
class Collector {
  seen: string[] = [];
  onItem: any = (s: string): void => {
    if (!this.seen.includes(s)) this.seen.push(s);
  };
}
const c = new Collector();
input.split(",").forEach(c.onItem);
console.log(c.seen.join("|"));
''', r'''
class Collector {
  seen: string[] = [];
  onItem = (s: string): void => {
    if (!this.seen.includes(s)) this.seen.push(s);
  };
}
const c = new Collector();
input.split(",").forEach(c.onItem);
console.log(c.seen.join("|"));
''', "type _1 = Expect<Equal<Collector[\"onItem\"], (s: string) => void>>;",
     ["a,b,a", "x", "c,c,c,d"],
     hints=["The field holds a function; its type can simply be inferred from the arrow.",
            "An arrow field captured `this` when the instance was built, so it survives `forEach`."])

_xdz("ts_this_accessors", 1, "A method that demands its object", "Write `Clickable` so that `click` may only be called on a `Clickable`.",
     r'''
type Clickable = { clicks: number; click(this: Clickable): number };
const button: Clickable = {
  clicks: 0,
  click() {
    this.clicks++;
    return this.clicks;
  },
};
let last = 0;
for (let i = 0; i < Number(input); i++) last = button.click();
console.log(last, button.clicks);
''', "type Clickable = { clicks: number; click(this: Clickable): number };",
     "type _1 = Expect<Equal<ThisParameterType<Clickable[\"click\"]>, Clickable>>;\n"
     "type _2 = Expect<Equal<ReturnType<Clickable[\"click\"]>, number>>;\n"
     "type _3 = Expect<Equal<Clickable[\"clicks\"], number>>;",
     ["3", "0", "1"],
     hints=["A method can declare what `this` must be with a first, erased parameter.",
            "`click(this: Clickable): number`."])

_xdz("ts_this_accessors", 2, "A read-only measurement", "Write the `Measured` interface: callers may read `area` but never assign it, and may `scale`.",
     r'''
interface Measured {
  readonly area: number;
  scale(k: number): void;
}
class Rect implements Measured {
  w: number;
  h: number;
  constructor(w: number, h: number) {
    this.w = w;
    this.h = h;
  }
  get area(): number {
    return this.w * this.h;
  }
  scale(k: number): void {
    this.w *= k;
    this.h *= k;
  }
}
const [w = 1, h = 1, k = 1] = input.split(/\s+/).map(Number);
const m: Measured = new Rect(w, h);
m.scale(k);
console.log(m.area);
''', r'''interface Measured {
  readonly area: number;
  scale(k: number): void;
}''', "type _1 = Expect<Equal<Pick<Measured, \"area\">, { readonly area: number }>>;\n"
      "type _2 = Expect<Equal<Parameters<Measured[\"scale\"]>[0], number>>;\n"
      "type _3 = Expect<Equal<keyof Measured, \"area\" | \"scale\">>;",
     ["2 3 2", "1 1 5", "4 5 1"],
     hints=["A getter with no setter is, from outside, a property you may only read.",
            "`readonly area: number` and a `scale(k: number): void` method."])
