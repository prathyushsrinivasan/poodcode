# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery, Month 6 (weeks 23-26): problem sets, runnable projects,
# extra practice and review cards for the chapters in ts_chapters_m6.py.
#
# Everything runs under strict+indexed. Async problems obey M6-03: output is
# deterministic by construction — week 26's problems run on a *virtual clock*
# (`_VCLOCK` below), so time only advances when the program says so and no
# result depends on how fast the judge's machine is.
# ---------------------------------------------------------------------------

_SI = "strict+indexed"

_HEAP_SRC = r"""
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
""".strip("\n")

# ===========================================================================
# Week 23 — Classes, encapsulation, class design, decorators
# ===========================================================================

TS_PROBLEM_SETS[23] = [
    _tsp(23, "tsm-w23-temperature", "One temperature, three scales", "warm-up",
         "Write a class `Temperature` that stores kelvin in a `#private` field and exposes `celsius`, `fahrenheit` and `kelvin` as get/set accessors; a setter that would go below absolute zero throws a `RangeError`. Each input line is `set <c|f|k> <value>` or `get <c|f|k>`; print the value after each command with two decimals, or `rejected: below absolute zero`. It starts at 0 °C.",
         r"""
class Temperature {
  #kelvin = 273.15;
  get kelvin(): number {
    return this.#kelvin;
  }
  set kelvin(k: number) {
    if (k < 0) throw new RangeError("below absolute zero");
    this.#kelvin = k;
  }
  get celsius(): number {
    return this.#kelvin - 273.15;
  }
  set celsius(c: number) {
    this.kelvin = c + 273.15;
  }
  get fahrenheit(): number {
    return (this.celsius * 9) / 5 + 32;
  }
  set fahrenheit(f: number) {
    this.celsius = ((f - 32) * 5) / 9;
  }
}
const t = new Temperature();
for (const line of input.split("\n")) {
  const [cmd = "", scale = "", value = "0"] = line.trim().split(/\s+/);
  try {
    if (cmd === "set") {
      const v = Number(value);
      if (scale === "c") t.celsius = v;
      else if (scale === "f") t.fahrenheit = v;
      else t.kelvin = v;
    }
    const shown = scale === "c" ? t.celsius : scale === "f" ? t.fahrenheit : t.kelvin;
    console.log(`${scale} = ${shown.toFixed(2)}`);
  } catch (e) {
    console.log(`rejected: ${e instanceof RangeError ? e.message : String(e)}`);
  }
}
""", ["get c\nget f\nset f 212\nget c\nset c -300\nget k\nset k 0\nget f"],
         hints=["Store one unit privately; every accessor converts to and from it.",
                "Let the other setters go through the `kelvin` setter, so the validation lives in one place."]),
    _tsp(23, "tsm-w23-vector", "An immutable 2-D vector", "warm-up",
         "Write a class `Vec` with `readonly x` and `readonly y` and methods `add(v)`, `scale(k)`, `length()`, `equals(v)` and `toString()` (`(x, y)`), each returning a *new* vector where it returns one. Each input line is an expression: `add x1 y1 x2 y2`, `scale x y k`, `length x y` (two decimals) or `equals x1 y1 x2 y2`. Print the result.",
         r"""
class Vec {
  readonly x: number;
  readonly y: number;
  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
  }
  add(v: Vec): Vec {
    return new Vec(this.x + v.x, this.y + v.y);
  }
  scale(k: number): Vec {
    return new Vec(this.x * k, this.y * k);
  }
  length(): number {
    return Math.hypot(this.x, this.y);
  }
  equals(v: Vec): boolean {
    return this.x === v.x && this.y === v.y;
  }
  toString(): string {
    return `(${this.x}, ${this.y})`;
  }
}
for (const line of input.split("\n")) {
  const [op = "", ...rest] = line.trim().split(/\s+/);
  const [a = 0, b = 0, c = 0, d = 0] = rest.map(Number);
  const v = new Vec(a, b);
  if (op === "add") console.log(String(v.add(new Vec(c, d))));
  else if (op === "scale") console.log(String(v.scale(c)));
  else if (op === "length") console.log(v.length().toFixed(2));
  else if (op === "equals") console.log(v.equals(new Vec(c, d)));
}
""", ["add 1 2 3 4\nscale 1 -2 3\nlength 3 4\nequals 1 1 1 1\nequals 1 2 2 1", "length 1 1"],
         hints=["`readonly` fields and methods that return new vectors make every `Vec` immutable."]),
    _tsp(23, "tsm-w23-shapes", "An abstract shape hierarchy", "core",
         "Write an abstract class `Shape` with abstract `name`, `area()` and `perimeter()` and a concrete `describe()` (`<name>: area <a>, perimeter <p>`, two decimals). Subclasses: `Circle(r)`, `Rect(w, h)`, `Triangle(a, b, c)` (area by Heron's formula; sides that can't form a triangle are rejected by a static factory). Each input line is a shape; print the shapes sorted by area, largest first (ties in input order), then `total perimeter <p>`. Bad lines print `bad shape <line>` first, as they are read.",
         r"""
abstract class Shape {
  abstract readonly name: string;
  abstract area(): number;
  abstract perimeter(): number;
  describe(): string {
    return `${this.name}: area ${this.area().toFixed(2)}, perimeter ${this.perimeter().toFixed(2)}`;
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
  perimeter(): number {
    return 2 * Math.PI * this.r;
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
  perimeter(): number {
    return 2 * (this.w + this.h);
  }
}
class Triangle extends Shape {
  readonly name = "triangle";
  readonly sides: readonly [number, number, number];
  private constructor(a: number, b: number, c: number) {
    super();
    this.sides = [a, b, c];
  }
  static of(a: number, b: number, c: number): Triangle | undefined {
    return a + b > c && a + c > b && b + c > a ? new Triangle(a, b, c) : undefined;
  }
  perimeter(): number {
    return this.sides[0] + this.sides[1] + this.sides[2];
  }
  area(): number {
    const s = this.perimeter() / 2;
    return Math.sqrt(s * (s - this.sides[0]) * (s - this.sides[1]) * (s - this.sides[2]));
  }
}
function parse(line: string): Shape | undefined {
  const [kind = "", ...rest] = line.trim().split(/\s+/);
  const n = rest.map(Number);
  if (n.some((x) => !(x > 0))) return undefined;
  const [a = 0, b = 0, c = 0] = n;
  if (kind === "circle" && n.length === 1) return new Circle(a);
  if (kind === "rect" && n.length === 2) return new Rect(a, b);
  if (kind === "triangle" && n.length === 3) return Triangle.of(a, b, c);
  return undefined;
}
const shapes: Shape[] = [];
for (const line of input.split("\n")) {
  const s = parse(line);
  if (s === undefined) console.log(`bad shape ${line.trim()}`);
  else shapes.push(s);
}
for (const s of shapes.toSorted((a, b) => b.area() - a.area())) console.log(s.describe());
console.log(`total perimeter ${shapes.reduce((t, s) => t + s.perimeter(), 0).toFixed(2)}`);
""", ["circle 1\nrect 2 3\ntriangle 3 4 5\ntriangle 1 1 5\nhexagon 2", "rect 1 1\ncircle 0.5"],
         hints=["The base class writes `describe` once; subclasses supply the abstract parts.",
                "A private constructor plus a static factory lets `Triangle` refuse impossible sides."]),
    _tsp(23, "tsm-w23-parking", "A parking lot", "core",
         "A lot has spots of sizes `small`, `medium`, `large`, given on the first line as counts (`small=2 medium=1 large=1`). Vehicles are `bike` (fits any spot), `car` (medium or large) and `van` (large only); each parks in the smallest free spot it fits. Commands: `park <plate> <type>` → `<plate> -> <size>` or `<plate> refused: no space`/`already parked`; `leave <plate>` → `<plate> left <size>` or `<plate> not found`; `status` → `small <free>/<total> medium <free>/<total> large <free>/<total>`. Model it with classes.",
         r"""
type Size = "small" | "medium" | "large";
type Kind = "bike" | "car" | "van";
const SIZES: readonly Size[] = ["small", "medium", "large"];
const FITS: Record<Kind, readonly Size[]> = { bike: SIZES, car: ["medium", "large"], van: ["large"] };
class ParkingLot {
  readonly #total: Record<Size, number>;
  readonly #used: Record<Size, number> = { small: 0, medium: 0, large: 0 };
  readonly #parked = new Map<string, Size>();
  constructor(total: Record<Size, number>) {
    this.#total = total;
  }
  park(plate: string, kind: Kind): string {
    if (this.#parked.has(plate)) return `${plate} refused: already parked`;
    const size = FITS[kind].find((s) => this.#used[s] < this.#total[s]);
    if (size === undefined) return `${plate} refused: no space`;
    this.#used[size]++;
    this.#parked.set(plate, size);
    return `${plate} -> ${size}`;
  }
  leave(plate: string): string {
    const size = this.#parked.get(plate);
    if (size === undefined) return `${plate} not found`;
    this.#used[size]--;
    this.#parked.delete(plate);
    return `${plate} left ${size}`;
  }
  status(): string {
    return SIZES.map((s) => `${s} ${this.#total[s] - this.#used[s]}/${this.#total[s]}`).join(" ");
  }
}
const [first = "", ...commands] = input.split("\n");
const total: Record<Size, number> = { small: 0, medium: 0, large: 0 };
for (const pair of first.trim().split(/\s+/)) {
  const [size = "", n = "0"] = pair.split("=");
  const s = SIZES.find((x) => x === size);
  if (s !== undefined) total[s] = Number(n);
}
const lot = new ParkingLot(total);
const isKind = (s: string): s is Kind => s === "bike" || s === "car" || s === "van";
for (const line of commands) {
  const [cmd = "", plate = "", kind = ""] = line.trim().split(/\s+/);
  if (cmd === "park") console.log(isKind(kind) ? lot.park(plate, kind) : `${plate} refused: unknown type ${kind}`);
  else if (cmd === "leave") console.log(lot.leave(plate));
  else if (cmd === "status") console.log(lot.status());
}
""", ["small=1 medium=1 large=1\npark A1 car\npark B2 bike\npark C3 bike\npark D4 van\npark E5 car\nstatus\nleave A1\npark E5 car\nleave Z9\npark E5 car",
      "small=0 medium=0 large=1\npark V van\npark W van\npark X boat\nstatus"],
         hints=["`FITS[kind].find(…)` over sizes in order picks the smallest spot that is still free.",
                "Keep the counts `#private`, so nothing but `park`/`leave` can change them."]),
    _tsp(23, "tsm-w23-library", "Library checkouts with late fees", "core",
         "Commands: `add <isbn> <title…>` (a book), `join <member>`, `borrow <day> <member> <isbn>`, `return <day> <member> <isbn>`, `report`. A member may hold at most 2 books; a loan is due 14 days after borrowing, and each late day costs 25 cents. Print `ok`, or `refused: <reason>` — `no such member`, `no such book`, `already on loan`, `limit reached`, `not borrowed by <member>` — and a return prints `returned, fee $<x.yy>`. `report` prints each member (sorted) as `<member>: <n> on loan, fees $<total>`.",
         r"""
class Book {
  readonly isbn: string;
  readonly title: string;
  loan: { member: string; day: number } | undefined;
  constructor(isbn: string, title: string) {
    this.isbn = isbn;
    this.title = title;
  }
}
class Member {
  readonly name: string;
  readonly loans = new Set<string>();
  fees = 0;
  constructor(name: string) {
    this.name = name;
  }
}
class Library {
  static readonly LIMIT = 2;
  static readonly DAYS = 14;
  static readonly FEE_CENTS = 25;
  readonly #books = new Map<string, Book>();
  readonly #members = new Map<string, Member>();
  add(isbn: string, title: string): string {
    this.#books.set(isbn, new Book(isbn, title));
    return "ok";
  }
  join(name: string): string {
    if (!this.#members.has(name)) this.#members.set(name, new Member(name));
    return "ok";
  }
  borrow(day: number, name: string, isbn: string): string {
    const m = this.#members.get(name);
    const b = this.#books.get(isbn);
    if (m === undefined) return "refused: no such member";
    if (b === undefined) return "refused: no such book";
    if (b.loan !== undefined) return "refused: already on loan";
    if (m.loans.size >= Library.LIMIT) return "refused: limit reached";
    b.loan = { member: name, day };
    m.loans.add(isbn);
    return "ok";
  }
  giveBack(day: number, name: string, isbn: string): string {
    const m = this.#members.get(name);
    const b = this.#books.get(isbn);
    if (m === undefined) return "refused: no such member";
    if (b === undefined) return "refused: no such book";
    if (b.loan?.member !== name) return `refused: not borrowed by ${name}`;
    const late = Math.max(0, day - b.loan.day - Library.DAYS);
    const fee = late * Library.FEE_CENTS;
    m.fees += fee;
    m.loans.delete(isbn);
    b.loan = undefined;
    return `returned, fee $${(fee / 100).toFixed(2)}`;
  }
  report(): string[] {
    return [...this.#members.values()]
      .sort((a, b) => a.name.localeCompare(b.name))
      .map((m) => `${m.name}: ${m.loans.size} on loan, fees $${(m.fees / 100).toFixed(2)}`);
  }
}
const lib = new Library();
for (const line of input.split("\n")) {
  const [cmd = "", a = "", b = "", ...rest] = line.trim().split(/\s+/);
  if (cmd === "add") console.log(lib.add(a, [b, ...rest].join(" ")));
  else if (cmd === "join") console.log(lib.join(a));
  else if (cmd === "borrow") console.log(lib.borrow(Number(a), b, rest[0] ?? ""));
  else if (cmd === "return") console.log(lib.giveBack(Number(a), b, rest[0] ?? ""));
  else if (cmd === "report") for (const r of lib.report()) console.log(r);
}
""", ["add 111 Dune\nadd 222 Emma\nadd 333 Ulysses\njoin ana\njoin bo\nborrow 1 ana 111\nborrow 2 bo 111\nborrow 2 ana 222\nborrow 3 ana 333\nreturn 20 ana 111\nreturn 21 bo 222\nborrow 21 bo 111\nreport",
      "join cy\nborrow 1 cy 999\nborrow 1 dee 111\nreport"],
         hints=["Static fields hold the rules (`LIMIT`, `DAYS`, `FEE_CENTS`) — shared by every instance.",
                "`b.loan?.member !== name` covers both \"not on loan\" and \"on loan to someone else\"."]),
    _tsp(23, "tsm-w23-observable", "An observable value", "core",
         "Write `class Observable<T>` with `get()`, `set(value)` (notifies only when the value actually changes) and `subscribe(fn)` returning an unsubscribe function; and `computed(source, fn)`, an observable whose value is `fn(source)` and updates when the source changes. Commands: `watch <name>` subscribes a watcher to the price (printing `<name>: <old> -> <new>`), `unwatch <name>`, `set <n>`. A computed `withTax` (price × 1.2, two decimals) is watched from the start. Print `set <n>` echo lines only when nothing is notified.",
         r"""
class Observable<T> {
  #value: T;
  readonly #subs = new Set<(next: T, prev: T) => void>();
  constructor(value: T) {
    this.#value = value;
  }
  get(): T {
    return this.#value;
  }
  set(next: T): boolean {
    const prev = this.#value;
    if (Object.is(prev, next)) return false;
    this.#value = next;
    for (const fn of [...this.#subs]) fn(next, prev);
    return true;
  }
  subscribe(fn: (next: T, prev: T) => void): () => void {
    this.#subs.add(fn);
    return () => {
      this.#subs.delete(fn);
    };
  }
}
function computed<S, R>(source: Observable<S>, fn: (s: S) => R): Observable<R> {
  const out = new Observable(fn(source.get()));
  source.subscribe((s) => out.set(fn(s)));
  return out;
}
const price = new Observable(10);
const withTax = computed(price, (p) => (p * 1.2).toFixed(2));
let notified = 0;
withTax.subscribe((next, prev) => {
  notified++;
  console.log(`withTax: ${prev} -> ${next}`);
});
const watchers = new Map<string, () => void>();
for (const line of input.split("\n")) {
  const [cmd = "", arg = ""] = line.trim().split(/\s+/);
  if (cmd === "watch") {
    watchers.set(arg, price.subscribe((next, prev) => {
      notified++;
      console.log(`${arg}: ${prev} -> ${next}`);
    }));
  } else if (cmd === "unwatch") {
    watchers.get(arg)?.();
    watchers.delete(arg);
  } else if (cmd === "set") {
    const before = notified;
    price.set(Number(arg));
    if (notified === before) console.log(`set ${arg}`);
  }
}
""", ["watch ana\nset 20\nset 20\nwatch bo\nset 5\nunwatch ana\nset 6", "set 10\nset 10.001"],
         hints=["Return a closure from `subscribe` that removes the listener — the caller keeps it to unsubscribe.",
                "`Object.is` compares the old and new values; equal values notify nobody."]),
    _tsp(23, "tsm-w23-elevator", "An elevator, step by step", "stretch",
         "An elevator starts at floor 0, idle. Commands: `call <floor>` adds a request; `step <n>` advances n time steps; each step, if there are requests, it moves one floor toward its target and prints `t=<time> floor <f>`, and when it reaches a requested floor it prints `t=<time> stop <f>` and removes that request. Target choice (SCAN): keep going in the current direction while any request lies ahead; otherwise turn toward the nearest remaining request (the lower one on a tie). Time starts at 0 and counts every step, moving or not.",
         r"""
class Elevator {
  floor = 0;
  time = 0;
  direction: 1 | -1 = 1;
  readonly #requests = new Set<number>();
  call(f: number): void {
    if (f === this.floor) console.log(`t=${this.time} stop ${f}`);
    else this.#requests.add(f);
  }
  step(): void {
    this.time++;
    if (this.#requests.size === 0) return;
    const ahead = [...this.#requests].some((r) => (r - this.floor) * this.direction > 0);
    if (!ahead) {
      const nearest = [...this.#requests].sort((a, b) => Math.abs(a - this.floor) - Math.abs(b - this.floor) || a - b)[0] ?? this.floor;
      this.direction = nearest > this.floor ? 1 : -1;
    }
    this.floor += this.direction;
    console.log(`t=${this.time} floor ${this.floor}`);
    if (this.#requests.delete(this.floor)) console.log(`t=${this.time} stop ${this.floor}`);
  }
}
const e = new Elevator();
for (const line of input.split("\n")) {
  const [cmd = "", arg = "0"] = line.trim().split(/\s+/);
  if (cmd === "call") e.call(Number(arg));
  else if (cmd === "step") for (let i = 0; i < Number(arg); i++) e.step();
}
""", ["call 3\nstep 2\ncall 1\nstep 4\ncall 0\ncall 5\nstep 6", "step 2\ncall 0\ncall -2\ncall 2\nstep 7"],
         hints=["Keep the requests in a `Set`; each step decides the direction, moves one floor, and stops if the new floor was requested."]),
    _tsp_types(23, "tsm-w23-comparable", "An interface for comparable things", "core",
               "Write the `Comparable<T>` interface — one method, `compareTo(other: T): number` — so that `Money` can implement it, and a class that forgets the method is rejected.",
               '''
interface Comparable<T> {
  compareTo(other: T): number;
}
class Money implements Comparable<Money> {
  readonly cents: number;
  constructor(cents: number) {
    this.cents = cents;
  }
  compareTo(other: Money): number {
    return this.cents - other.cents;
  }
}
function max<T extends Comparable<T>>(items: readonly T[]): T | undefined {
  return items.reduce<T | undefined>((best, x) => (best === undefined || x.compareTo(best) > 0 ? x : best), undefined);
}
''', "compareTo(other: T): number;",
               '''
type _1 = Expect<Equal<Parameters<Money["compareTo"]>, [other: Money]>>;
type _2 = Expect<Equal<ReturnType<typeof max<Money>>, Money | undefined>>;
// @ts-expect-error — a Comparable must have compareTo
class Broken implements Comparable<Broken> {}
''', hints=["An interface with a single method signature.", "The parameter has the interface's own type parameter."]),
    _tsp_types(23, "tsm-w23-abstract", "Make the base class abstract", "core",
               "Finish `Shape` so that it can't be instantiated and every subclass must provide an `area()` returning a number.",
               '''
abstract class Shape {
  abstract area(): number;
  describe(): string {
    return "area " + this.area();
  }
}
class Square extends Shape {
  readonly side: number;
  constructor(side: number) {
    super();
    this.side = side;
  }
  area(): number {
    return this.side ** 2;
  }
}
''', "abstract area(): number;",
               '''
type _1 = Expect<Equal<ReturnType<Square["area"]>, number>>;
function _typeTests() {
  // @ts-expect-error — an abstract class can't be constructed
  new Shape();
}
// @ts-expect-error — a subclass must implement area
class NoArea extends Shape {}
''', hints=["The class is already `abstract`; declare the member the same way, with no body."]),
]

TS_PROJECTS[23] = _project(
    23, "account.ts — accounts that protect their invariants",
    "A small bank built from classes whose invariants can't be bypassed: accounts are created only through a validating factory, balances live in `#private` fields, a savings account overrides withdrawal rules, and a transfer either happens completely or not at all.",
    ["`open <kind> <owner> <amount>` creates a `checking` or `savings` account (ids `A1`, `A2`, … in order) through a static factory; bad input prints `refused: <reason>` — `unknown kind`, `owner required`, `amount must be a whole number >= 0`.",
     "`deposit <id> <n>`, `withdraw <id> <n>`: amounts are positive whole numbers. Checking accounts may go down to -100 (an overdraft); savings may not go below 0 and allow at most 3 withdrawals (`refused: withdrawal limit`). Print the new balance, or `refused: insufficient funds`/`refused: no account <id>`/`refused: bad amount`.",
     "`transfer <from> <to> <n>` moves money only if the withdrawal succeeds — then prints `ok <from>=<balance> <to>=<balance>` — otherwise the refusal and no change.",
     "`interest` adds 2% (rounded down) to every savings account with a positive balance and prints `interest paid <total>`; `statement` prints every account as `<id> <kind> <owner> <balance>` in id order.",
     "Use an abstract `Account` with `#balance`, subclasses that override a `canWithdraw` rule, and a private constructor behind `Account.open`."],
    r"""
abstract class Account {
  static #next = 1;
  readonly id: string;
  readonly owner: string;
  #balance: number;
  abstract readonly kind: string;
  protected constructor(owner: string, opening: number) {
    this.id = `A${Account.#next++}`;
    this.owner = owner;
    this.#balance = opening;
  }
  static open(kind: string, owner: string, amount: number): Account | string {
    if (kind !== "checking" && kind !== "savings") return "unknown kind";
    if (owner.trim() === "") return "owner required";
    if (!Number.isInteger(amount) || amount < 0) return "amount must be a whole number >= 0";
    return kind === "checking" ? new Checking(owner, amount) : new Savings(owner, amount);
  }
  get balance(): number {
    return this.#balance;
  }
  protected abstract canWithdraw(amount: number): string | undefined;
  deposit(amount: number): void {
    this.#balance += amount;
  }
  withdraw(amount: number): string | undefined {
    const problem = this.canWithdraw(amount);
    if (problem !== undefined) return problem;
    this.#balance -= amount;
    this.afterWithdraw();
    return undefined;
  }
  protected afterWithdraw(): void {}
}
class Checking extends Account {
  readonly kind = "checking";
  protected canWithdraw(amount: number): string | undefined {
    return this.balance - amount < -100 ? "insufficient funds" : undefined;
  }
}
class Savings extends Account {
  readonly kind = "savings";
  #withdrawals = 0;
  protected canWithdraw(amount: number): string | undefined {
    if (this.#withdrawals >= 3) return "withdrawal limit";
    return this.balance - amount < 0 ? "insufficient funds" : undefined;
  }
  protected override afterWithdraw(): void {
    this.#withdrawals++;
  }
}
const accounts = new Map<string, Account>();
const amountOf = (s: string) => (/^\d+$/.test(s) && Number(s) > 0 ? Number(s) : undefined);
for (const line of input.split("\n")) {
  const [cmd = "", a = "", b = "", c = ""] = line.trim().split(/\s+/);
  if (cmd === "open") {
    const acc = Account.open(a, b, c === "" ? NaN : Number(c));
    if (typeof acc === "string") console.log(`refused: ${acc}`);
    else {
      accounts.set(acc.id, acc);
      console.log(`opened ${acc.id}`);
    }
  } else if (cmd === "deposit" || cmd === "withdraw") {
    const acc = accounts.get(a);
    const n = amountOf(b);
    if (acc === undefined) console.log(`refused: no account ${a}`);
    else if (n === undefined) console.log("refused: bad amount");
    else if (cmd === "deposit") {
      acc.deposit(n);
      console.log(acc.balance);
    } else {
      const problem = acc.withdraw(n);
      console.log(problem === undefined ? acc.balance : `refused: ${problem}`);
    }
  } else if (cmd === "transfer") {
    const from = accounts.get(a);
    const to = accounts.get(b);
    const n = amountOf(c);
    if (from === undefined) console.log(`refused: no account ${a}`);
    else if (to === undefined) console.log(`refused: no account ${b}`);
    else if (n === undefined) console.log("refused: bad amount");
    else {
      const problem = from.withdraw(n);
      if (problem !== undefined) console.log(`refused: ${problem}`);
      else {
        to.deposit(n);
        console.log(`ok ${from.id}=${from.balance} ${to.id}=${to.balance}`);
      }
    }
  } else if (cmd === "interest") {
    let total = 0;
    for (const acc of accounts.values()) {
      if (acc instanceof Savings && acc.balance > 0) {
        const paid = Math.floor(acc.balance * 0.02);
        acc.deposit(paid);
        total += paid;
      }
    }
    console.log(`interest paid ${total}`);
  } else if (cmd === "statement") {
    for (const acc of accounts.values()) console.log(`${acc.id} ${acc.kind} ${acc.owner} ${acc.balance}`);
  }
}
""", ["open checking ana 50\nopen savings bo 1000\nwithdraw A1 120\nwithdraw A1 50\ntransfer A2 A1 200\ninterest\nstatement",
      "open cash cy 5\nopen savings  10\nopen savings dee -5\nopen savings dee 5.5\nopen checking eve 0\ndeposit A9 5\ndeposit A1 x\nstatement",
      "open savings s 100\nwithdraw A1 10\nwithdraw A1 10\nwithdraw A1 10\nwithdraw A1 10\ntransfer A1 A1 5\nstatement",
      "open checking c 0\nopen savings s 0\ntransfer A2 A1 1\ntransfer A1 A2 100\ntransfer A1 A2 1\nstatement\ninterest",
      "open savings rich 9999\ninterest\ninterest\nstatement"],
    stretch=["Add a `history` per account (every successful operation), readable but not writable from outside.",
             "Replace the string refusals with a `Result` type and `Error` subclasses (week 25)."],
)

TS_PRACTICE_MORE[23] = [
    _pr("tsm-w23-p1", "A class instance's type", 'class Point {\n  x = 0;\n  y = 0;\n}\nconst p = new Point();\n', "p", "Point",
        strictness=_SI, hints=["A class declaration also declares a type of the same name."]),
    _dx("tsm-w23-d1", "Constructing an abstract class",
        "error TS2511: Cannot create an instance of an abstract class.",
        'abstract class Shape {\n  abstract area(): number;\n}\nclass Sq extends Shape {\n  area(): number {\n    return 4;\n  }\n}\nconst s: Shape = new Shape();\nconsole.log(s.area());\n',
        'abstract class Shape {\n  abstract area(): number;\n}\nclass Sq extends Shape {\n  area(): number {\n    return 4;\n  }\n}\nconst s: Shape = new Sq();\nconsole.log(s.area());\n',
        [("", "4")], strictness=_SI, hints=["Only concrete subclasses can be constructed.", "Use `Sq`."]),
    _dx("tsm-w23-d2", "An override of nothing",
        "error TS4117: This member cannot have an 'override' modifier because it is not declared in the base class 'Base'. Did you mean 'label'?",
        'class Base {\n  label(): string {\n    return "base";\n  }\n}\nclass Child extends Base {\n  override lable(): string {\n    return "child";\n  }\n}\nconsole.log(new Child().label());\n',
        'class Base {\n  label(): string {\n    return "base";\n  }\n}\nclass Child extends Base {\n  override label(): string {\n    return "child";\n  }\n}\nconsole.log(new Child().label());\n',
        [("", "child")], strictness=_SI, hints=["`override` caught a typo.", "Spell the method like the base class does."]),
    _fx("tsm-w23-f1", "A counter shared by accident",
        "Each counter should count its own clicks. Print both counts after clicking `a` twice and `b` once — they come out the same.",
        'class Counter {\n  static clicks = 0;\n  click(): void {\n    Counter.clicks++;\n  }\n  get count(): number {\n    return Counter.clicks;\n  }\n}\nconst a = new Counter();\nconst b = new Counter();\na.click();\na.click();\nb.click();\nconsole.log(a.count, b.count);\n',
        'class Counter {\n  #clicks = 0;\n  click(): void {\n    this.#clicks++;\n  }\n  get count(): number {\n    return this.#clicks;\n  }\n}\nconst a = new Counter();\nconst b = new Counter();\na.click();\na.click();\nb.click();\nconsole.log(a.count, b.count);\n',
        [("", "2 1")], strictness=_SI, hints=["`static` belongs to the class, not each object.", "Use an instance field."]),
]

TS_CARDS_MORE[23] = [
    ("What does `abstract` on a method require?", "Every concrete subclass implements it (TS2515 otherwise); the abstract class itself can't be constructed (TS2511)."),
    ("What does the `override` keyword protect against?", "Renaming or misspelling: overriding a member the base doesn't have is TS4113."),
    ("How do you stop invalid instances being constructed?", "A `private constructor` behind a `static` factory that validates and returns `undefined` or a `Result`."),
    ("Why not call an overridable method from a base constructor?", "Subclass fields are initialised after the base constructor runs, so the override sees `undefined`."),
    ("What is a standard decorator, in one line?", "A function `(value, context) => replacement?` applied to a class member or class at definition time."),
    ("Why can't this app's runner execute `@decorators`?", "They run code at class definition, so type stripping can't delete them, and Node doesn't implement the syntax yet."),
]

# ===========================================================================
# Week 24 — Iterators, generators, iterator helpers, generic data structures
# ===========================================================================

TS_PROBLEM_SETS[24] = [
    _tsp(24, "tsm-w24-primes", "Lazy primes", "warm-up",
         "Write a generator `primes()` that never ends. Each input line is `first <n>` (the first n primes), `between <a> <b>` (primes with a ≤ p ≤ b) or `nth <n>` (the n-th prime, 1-based). Answer each with iterator helpers over `primes()` — no arrays until the final `toArray()`.",
         r"""
function* primes(): Generator<number> {
  const found: number[] = [];
  for (let n = 2; ; n++) {
    if (found.every((p) => p * p > n || n % p !== 0)) {
      found.push(n);
      yield n;
    }
  }
}
for (const line of input.split("\n")) {
  const [cmd = "", a = "0", b = "0"] = line.trim().split(/\s+/);
  if (cmd === "first") console.log(primes().take(Number(a)).toArray().join(" "));
  else if (cmd === "between") {
    const lo = Number(a);
    const hi = Number(b);
    const inRange: number[] = [];
    for (const p of primes()) {
      if (p > hi) break;
      if (p >= lo) inRange.push(p);
    }
    console.log(inRange.join(" ") || "(none)");
  } else if (cmd === "nth") console.log(primes().drop(Number(a) - 1).take(1).toArray()[0] ?? "?");
}
""", ["first 6\nbetween 20 40\nnth 10\nbetween 24 28", "nth 1\nfirst 1"],
         hints=["An infinite generator is fine as long as every consumer stops: `take`, `break`, or `drop` + `take`."]),
    _tsp(24, "tsm-w24-take-while", "Generators that stop on a condition", "warm-up",
         "Write generators `takeWhile(src, pred)` and `dropWhile(src, pred)` over any `Iterable<T>`. Each input line is a list of integers: print the leading run that is strictly increasing, then the rest after dropping the leading non-negative numbers, as `<run> | <rest>` (`-` for an empty part).",
         r"""
function* takeWhile<T>(src: Iterable<T>, pred: (x: T, prev: T | undefined) => boolean): Generator<T> {
  let prev: T | undefined;
  for (const x of src) {
    if (!pred(x, prev)) return;
    yield x;
    prev = x;
  }
}
function* dropWhile<T>(src: Iterable<T>, pred: (x: T) => boolean): Generator<T> {
  let dropping = true;
  for (const x of src) {
    if (dropping && pred(x)) continue;
    dropping = false;
    yield x;
  }
}
for (const line of input.split("\n")) {
  const xs = line.trim().split(/\s+/).map(Number);
  const run = [...takeWhile(xs, (x, prev) => prev === undefined || x > prev)];
  const rest = [...dropWhile(xs, (x) => x >= 0)];
  console.log(`${run.join(" ") || "-"} | ${rest.join(" ") || "-"}`);
}
""", ["1 3 5 4 -2 7\n9 8 7\n-1 2 3", "4 5 6"],
         hints=["`return` inside a generator ends the sequence.", "`dropWhile` needs one flag: are we still dropping?"]),
    _tsp(24, "tsm-w24-ring", "A ring buffer", "warm-up",
         "Write `class RingBuffer<T>` with a fixed capacity: `push` overwrites the oldest item when full, `toArray()` returns oldest → newest, and the class is iterable. The first input line is the capacity; each later line is `push <x>`, `latest` (the newest item or `empty`) or `dump` (all items, oldest first, or `(empty)`). After every `push` that overwrote something, print `dropped <old>`.",
         r"""
class RingBuffer<T> implements Iterable<T> {
  readonly #items: (T | undefined)[];
  #start = 0;
  #size = 0;
  constructor(capacity: number) {
    this.#items = Array.from({ length: capacity }, () => undefined);
  }
  push(item: T): T | undefined {
    const cap = this.#items.length;
    const index = (this.#start + this.#size) % cap;
    let dropped: T | undefined;
    if (this.#size === cap) {
      dropped = this.#items[this.#start];
      this.#start = (this.#start + 1) % cap;
    } else {
      this.#size++;
    }
    this.#items[index] = item;
    return dropped;
  }
  *[Symbol.iterator](): Generator<T> {
    for (let i = 0; i < this.#size; i++) {
      const item = this.#items[(this.#start + i) % this.#items.length];
      if (item !== undefined) yield item;
    }
  }
  latest(): T | undefined {
    return this.#size === 0 ? undefined : this.#items[(this.#start + this.#size - 1) % this.#items.length];
  }
}
const [capText = "1", ...lines] = input.split("\n");
const ring = new RingBuffer<string>(Number(capText));
for (const line of lines) {
  const [cmd = "", arg = ""] = line.trim().split(/\s+/);
  if (cmd === "push") {
    const dropped = ring.push(arg);
    if (dropped !== undefined) console.log(`dropped ${dropped}`);
  } else if (cmd === "latest") console.log(ring.latest() ?? "empty");
  else if (cmd === "dump") console.log([...ring].join(" ") || "(empty)");
}
""", ["3\ndump\npush a\npush b\npush c\npush d\ndump\nlatest\npush e\npush f\ndump", "1\nlatest\npush x\npush y\ndump"],
         hints=["Track where the oldest item is (`start`) and how many there are (`size`); indexes wrap with `%`."]),
    _tsp(24, "tsm-w24-interleave", "Interleave iterables", "core",
         "Write a generator `interleave<T>(...sources: Iterable<T>[])` that yields one item from each source in turn, skipping sources that have run out, until all are exhausted. Each input line is a list of comma-separated groups (`a b c,1 2,x`); print the interleaved items space-separated. Then print `infinite: ` and the first 7 items of interleaving the input's first line's groups with an infinite `1 2 3 …` counter.",
         r"""
function* interleave<T>(...sources: Iterable<T>[]): Generator<T> {
  const iters = sources.map((s) => s[Symbol.iterator]());
  let active = iters.length;
  const done = new Set<number>();
  while (active > 0) {
    for (const [i, it] of iters.entries()) {
      if (done.has(i)) continue;
      const r = it.next();
      if (r.done === true) {
        done.add(i);
        active--;
      } else {
        yield r.value;
      }
    }
  }
}
function* counter(): Generator<string> {
  for (let n = 1; ; n++) yield String(n);
}
const lines = input.split("\n");
for (const line of lines) {
  const groups = line.split(",").map((g) => g.trim().split(/\s+/).filter((t) => t !== ""));
  console.log([...interleave(...groups)].join(" "));
}
const firstGroups = (lines[0] ?? "").split(",").map((g) => g.trim().split(/\s+/).filter((t) => t !== ""));
console.log("infinite: " + interleave<string>(...firstGroups, counter()).take(7).toArray().join(" "));
""", ["a b c,1 2,x\np q,r s t u", "solo"],
         hints=["Keep one iterator per source; call `next()` on each in turn and remember which are done.",
                "Because the generator is lazy, interleaving with an infinite source is fine as long as the consumer `take`s."]),
    _tsp(24, "tsm-w24-linked-list", "An iterable linked list", "core",
         "Write `class LinkedList<T>` (singly linked, with a tail pointer) supporting `push`, `unshift`, `shift`, `remove(value)` (first occurrence), `reverse()` (in place) and iteration with `for…of`. Commands: `push <x>`, `unshift <x>`, `shift` (prints the removed value or `empty`), `remove <x>` (`removed`/`not found`), `reverse`, `print` (the values or `(empty)`) and `size`.",
         r"""
type ListNode<T> = { value: T; next: ListNode<T> | undefined };
class LinkedList<T> implements Iterable<T> {
  #head: ListNode<T> | undefined;
  #tail: ListNode<T> | undefined;
  #size = 0;
  get size(): number {
    return this.#size;
  }
  push(value: T): void {
    const node: ListNode<T> = { value, next: undefined };
    if (this.#tail === undefined) this.#head = node;
    else this.#tail.next = node;
    this.#tail = node;
    this.#size++;
  }
  unshift(value: T): void {
    this.#head = { value, next: this.#head };
    if (this.#tail === undefined) this.#tail = this.#head;
    this.#size++;
  }
  shift(): T | undefined {
    const h = this.#head;
    if (h === undefined) return undefined;
    this.#head = h.next;
    if (this.#head === undefined) this.#tail = undefined;
    this.#size--;
    return h.value;
  }
  remove(value: T): boolean {
    let prev: ListNode<T> | undefined;
    for (let n = this.#head; n !== undefined; prev = n, n = n.next) {
      if (n.value !== value) continue;
      if (prev === undefined) this.#head = n.next;
      else prev.next = n.next;
      if (this.#tail === n) this.#tail = prev;
      this.#size--;
      return true;
    }
    return false;
  }
  reverse(): void {
    let prev: ListNode<T> | undefined;
    let n = this.#head;
    this.#tail = n;
    while (n !== undefined) {
      const next: ListNode<T> | undefined = n.next;
      n.next = prev;
      prev = n;
      n = next;
    }
    this.#head = prev;
  }
  *[Symbol.iterator](): Generator<T> {
    for (let n = this.#head; n !== undefined; n = n.next) yield n.value;
  }
}
const list = new LinkedList<string>();
for (const line of input.split("\n")) {
  const [cmd = "", arg = ""] = line.trim().split(/\s+/);
  if (cmd === "push") list.push(arg);
  else if (cmd === "unshift") list.unshift(arg);
  else if (cmd === "shift") console.log(list.shift() ?? "empty");
  else if (cmd === "remove") console.log(list.remove(arg) ? "removed" : "not found");
  else if (cmd === "reverse") list.reverse();
  else if (cmd === "print") console.log([...list].join(" ") || "(empty)");
  else if (cmd === "size") console.log(list.size);
}
""", ["push b\npush c\nunshift a\nprint\nremove c\npush d\nreverse\nprint\nshift\nsize\nremove z\nprint",
      "shift\nprint\npush x\nremove x\nprint\npush y\nprint"],
         hints=["Keep `#head`, `#tail` and `#size` consistent in every method — `remove` of the last node must move the tail.",
                "A generator method makes the list work with spread and `for…of`."]),
    _tsp(24, "tsm-w24-bst", "A BST with an in-order iterator", "core",
         "Write `class BST` of numbers with `insert` (ignoring duplicates) and an in-order generator using `yield*` on the subtrees. Commands: `insert <n…>`, `inorder`, `kth <k>` (the k-th smallest, via the iterator — `none` if too few), `range <lo> <hi>` (values in [lo, hi], stopping the iteration as soon as a value exceeds hi) and `height`.",
         r"""
type TreeNode = { value: number; left: TreeNode | undefined; right: TreeNode | undefined };
class BST {
  #root: TreeNode | undefined;
  insert(value: number): void {
    const node: TreeNode = { value, left: undefined, right: undefined };
    if (this.#root === undefined) {
      this.#root = node;
      return;
    }
    let cur = this.#root;
    for (;;) {
      if (value === cur.value) return;
      const side = value < cur.value ? "left" : "right";
      const next = cur[side];
      if (next === undefined) {
        cur[side] = node;
        return;
      }
      cur = next;
    }
  }
  *#walk(n: TreeNode | undefined): Generator<number> {
    if (n === undefined) return;
    yield* this.#walk(n.left);
    yield n.value;
    yield* this.#walk(n.right);
  }
  *[Symbol.iterator](): Generator<number> {
    yield* this.#walk(this.#root);
  }
  height(): number {
    const h = (n: TreeNode | undefined): number => (n === undefined ? 0 : 1 + Math.max(h(n.left), h(n.right)));
    return h(this.#root);
  }
}
const tree = new BST();
for (const line of input.split("\n")) {
  const [cmd = "", ...args] = line.trim().split(/\s+/);
  const nums = args.map(Number);
  if (cmd === "insert") for (const n of nums) tree.insert(n);
  else if (cmd === "inorder") console.log([...tree].join(" ") || "(empty)");
  else if (cmd === "kth") console.log(Iterator.from(tree).drop((nums[0] ?? 1) - 1).take(1).toArray()[0] ?? "none");
  else if (cmd === "range") {
    const [lo = 0, hi = 0] = nums;
    const out: number[] = [];
    for (const v of tree) {
      if (v > hi) break;
      if (v >= lo) out.push(v);
    }
    console.log(out.join(" ") || "(none)");
  } else if (cmd === "height") console.log(tree.height());
}
""", ["insert 50 30 70 20 40 60 80 30\ninorder\nkth 3\nkth 9\nrange 35 65\nheight", "inorder\ninsert 1 2 3 4\nheight\nrange 5 9"],
         hints=["`yield*` delegates to the recursive generator for each subtree.",
                "Because iteration is lazy, `break` stops the walk — a range query touches only what it needs."]),
    _tsp(24, "tsm-w24-meeting-rooms", "Meeting rooms with a heap", "core",
         "Each input line is a meeting `<start>-<end>` (minutes, end exclusive). Assign meetings, in order of start time (then input order), to rooms numbered from 1: reuse the room that frees up earliest if it is free by the start time, otherwise open a new room. Print `<start>-<end> room <r>` in that order, then `rooms <n>`. Use a min-heap of `(end, room)`.",
         _HEAP_SRC + r"""
type Meeting = { start: number; end: number; index: number };
const meetings: Meeting[] = input.split("\n").map((line, index) => {
  const [s = "0", e = "0"] = line.trim().split("-");
  return { start: Number(s), end: Number(e), index };
});
meetings.sort((a, b) => a.start - b.start || a.index - b.index);
const busy = new Heap<{ end: number; room: number }>((a, b) => a.end - b.end || a.room - b.room);
let rooms = 0;
for (const m of meetings) {
  const soonest = busy.peek();
  let room: number;
  if (soonest !== undefined && soonest.end <= m.start) {
    busy.pop();
    room = soonest.room;
  } else {
    room = ++rooms;
  }
  busy.push({ end: m.end, room });
  console.log(`${m.start}-${m.end} room ${room}`);
}
console.log(`rooms ${rooms}`);
""", ["0-30\n5-10\n15-20\n10-40\n30-45", "9-10\n9-10\n10-11"],
         hints=["The heap's top is the room that frees up first — the only one worth checking."]),
    _tsp(24, "tsm-w24-running-median", "A running median", "stretch",
         "The input is a stream of integers. After each one, print the median so far (the average of the two middle values for an even count, with at most one decimal). Keep two heaps — a max-heap of the lower half and a min-heap of the upper half — balanced so their sizes differ by at most one.",
         _HEAP_SRC + r"""
const low = new Heap<number>((a, b) => b - a);
const high = new Heap<number>((a, b) => a - b);
const out: string[] = [];
for (const x of input.split(/\s+/).map(Number)) {
  if (low.size === 0 || x <= (low.peek() ?? x)) low.push(x);
  else high.push(x);
  if (low.size > high.size + 1) high.push(low.pop() ?? 0);
  else if (high.size > low.size) low.push(high.pop() ?? 0);
  const median = low.size > high.size ? (low.peek() ?? 0) : ((low.peek() ?? 0) + (high.peek() ?? 0)) / 2;
  out.push(String(Number(median.toFixed(1))));
}
console.log(out.join(" "));
""", ["5 15 1 3 8 7 9 10", "2", "4 4 4 1"],
         hints=["The lower half's maximum and the upper half's minimum are always at the tops of the heaps.",
                "Rebalance after every insert so the lower half has the same size or one more."]),
    _tsp_types(24, "tsm-w24-iterable", "Make a class iterable, typed", "core",
               "`Bag<T>` stores items in an array. Give it the method that makes it iterable, so spreading a `Bag<string>` gives a `string[]` and `for…of` gives `T`s.",
               '''
class Bag<T> implements Iterable<T> {
  readonly #items: T[] = [];
  add(item: T): this {
    this.#items.push(item);
    return this;
  }
  *[Symbol.iterator](): Generator<T> {
    yield* this.#items;
  }
}
const words = new Bag<string>().add("a").add("b");
const all = [...words];
''', '''*[Symbol.iterator](): Generator<T> {
    yield* this.#items;
  }''',
               '''
type _1 = Expect<Equal<typeof all, string[]>>;
type _2 = Expect<Equal<ReturnType<Bag<number>[typeof Symbol.iterator]>, Generator<number>>>;
''', hints=["A generator method named `[Symbol.iterator]`.", "`yield*` delegates to the array's own iterator."]),
]

TS_PROJECTS[24] = _project(
    24, "lazy.ts — a lazy pipeline over infinite sources",
    "Build pipelines over sequences that never end — natural numbers, Fibonacci, primes — with generators and iterator helpers, so that each pipeline does only the work its `take` asks for. Every step is lazy; nothing is materialised until the end.",
    ["Each input line is a pipeline: `<source> | <step> | <step> …`. Sources: `naturals` (1, 2, 3, …), `fib` (1, 1, 2, 3, 5, …), `primes`, `range <a> <b>` (a ≤ n < b, finite).",
     "Steps: `map square|double|digits` (`digits` = digit sum), `filter even|odd|prime`, `skip <n>`, `take <n>`, `takeWhile below <n>`, `chunk <n>` (groups printed as `[a b]`), `sum` (terminal: prints the total), `count` (terminal).",
     "Without a terminal step print the values space-separated. A pipeline over an infinite source with no `take`, `takeWhile` or finite source before a terminal step or the end prints `refused: infinite`.",
     "Unknown sources or steps print `unknown <word>`.",
     "Use generator functions for the sources and iterator helpers (`map`, `filter`, `drop`, `take`) for the steps; count how many source values were pulled and print `pulled <k>` after each pipeline (except one with an unknown source)."],
    r"""
function* naturals(): Generator<number> {
  for (let n = 1; ; n++) yield n;
}
function* fib(): Generator<number> {
  let [a, b] = [1, 1];
  for (;;) {
    yield a;
    [a, b] = [b, a + b];
  }
}
const isPrime = (n: number): boolean => {
  if (n < 2) return false;
  for (let d = 2; d * d <= n; d++) if (n % d === 0) return false;
  return true;
};
function* range(a: number, b: number): Generator<number> {
  for (let n = a; n < b; n++) yield n;
}
function* counted(src: Iterator<number>, onPull: () => void): Generator<number> {
  for (let r = src.next(); r.done !== true; r = src.next()) {
    onPull();
    yield r.value;
  }
}
function* takeWhileBelow(src: Iterator<number>, limit: number): Generator<number> {
  for (let r = src.next(); r.done !== true && r.value < limit; r = src.next()) yield r.value;
}
const digitSum = (n: number) => [...String(Math.abs(n))].reduce((s, d) => s + Number(d), 0);
for (const line of input.split("\n")) {
  const [sourceText = "", ...stepTexts] = line.split("|").map((s) => s.trim());
  const [sourceName = "", a = "0", b = "0"] = sourceText.split(/\s+/);
  let pulled = 0;
  const base: Iterator<number> | undefined =
    sourceName === "naturals" ? naturals() : sourceName === "fib" ? fib() : sourceName === "primes" ? naturals().filter(isPrime) : sourceName === "range" ? range(Number(a), Number(b)) : undefined;
  if (base === undefined) {
    console.log(`unknown ${sourceName}`);
    continue;
  }
  let it: IteratorObject<number> = counted(base, () => pulled++);
  let finite = sourceName === "range";
  let terminal: string | undefined;
  let chunkSize = 0;
  let error: string | undefined;
  for (const stepText of stepTexts) {
    const [step = "", arg = ""] = stepText.split(/\s+/);
    const n = Number(stepText.split(/\s+/).at(-1));
    if (step === "map" && arg === "square") it = it.map((x) => x * x);
    else if (step === "map" && arg === "double") it = it.map((x) => x * 2);
    else if (step === "map" && arg === "digits") it = it.map(digitSum);
    else if (step === "filter" && arg === "even") it = it.filter((x) => x % 2 === 0);
    else if (step === "filter" && arg === "odd") it = it.filter((x) => x % 2 !== 0);
    else if (step === "filter" && arg === "prime") it = it.filter(isPrime);
    else if (step === "skip") it = it.drop(n);
    else if (step === "take") {
      it = it.take(n);
      finite = true;
    } else if (step === "takeWhile" && arg === "below") {
      it = takeWhileBelow(it, n);
      finite = true;
    } else if (step === "chunk") chunkSize = n;
    else if (step === "sum" || step === "count") terminal = step;
    else {
      error = `unknown ${step}`;
      break;
    }
  }
  if (error !== undefined) console.log(error);
  else if (!finite) console.log("refused: infinite");
  else {
    const values = it.toArray();
    if (terminal === "sum") console.log(values.reduce((s, x) => s + x, 0));
    else if (terminal === "count") console.log(values.length);
    else if (chunkSize > 0) {
      const groups: string[] = [];
      for (let i = 0; i < values.length; i += chunkSize) groups.push(`[${values.slice(i, i + chunkSize).join(" ")}]`);
      console.log(groups.join(" "));
    } else console.log(values.join(" ") || "(empty)");
  }
  console.log(`pulled ${pulled}`);
}
""", ["naturals | filter even | map square | take 5\nfib | takeWhile below 100\nprimes | skip 3 | take 4\nnaturals | map double",
      "range 1 11 | filter odd | sum\nnaturals | take 10 | chunk 3\nfib | take 12 | map digits | count",
      "primes | take 5 | sum\nsquares | take 2\nnaturals | fly | take 1",
      "range 5 5 | take 3\nnaturals | skip 100 | filter prime | take 3",
      "fib | filter even | take 4\nrange 0 20 | filter prime | map square | chunk 2"],
    stretch=["Add `window <n>` (sliding windows) as a lazy generator step.",
             "Make the step table data — `{ name, arity, apply }` — so adding a step is one entry."],
)

TS_PRACTICE_MORE[24] = [
    _pr("tsm-w24-p1", "An iterator helper's type", 'const doubled = [1, 2, 3].values().map((n) => n * 2);\n', "doubled", "IteratorObject<number, undefined, unknown>",
        strictness=_SI, hints=["Iterator helpers return iterator objects, not arrays.", "The element type follows the callback."]),
    _dx("tsm-w24-d1", "Helpers on a plain iterable",
        "error TS2339: Property 'take' does not exist on type 'Iterable<string>'.",
        _STDIN + 'function firstTwo(words: Iterable<string>): string[] {\n  return words.take(2).toArray();\n}\nconsole.log(firstTwo(new Set(input.split(" "))).join(","));\n',
        _STDIN + 'function firstTwo(words: Iterable<string>): string[] {\n  return Iterator.from(words).take(2).toArray();\n}\nconsole.log(firstTwo(new Set(input.split(" "))).join(","));\n',
        [("a b a c", "a,b"), ("x", "x")], strictness=_SI, hints=["`Iterable<T>` only promises `[Symbol.iterator]`.", "Wrap it with `Iterator.from`."]),
    _fx("tsm-w24-f1", "An iterator read twice",
        "Print the count of words and then the words joined by commas. The second line is empty.",
        _STDIN + 'const words = new Set(input.split(" ")).values();\nconsole.log([...words].length);\nconsole.log([...words].join(","));\n',
        _STDIN + 'const words = new Set(input.split(" "));\nconsole.log([...words].length);\nconsole.log([...words].join(","));\n',
        [("a b a", "2\na,b"), ("x", "1\nx")], strictness=_SI,
        hints=["An iterator is used up by the first spread.", "Keep the `Set` (an iterable) and ask it for a new iterator each time."]),
]

TS_CARDS_MORE[24] = [
    ("Lazy or eager: `iter.map(f)` on an iterator?", "Lazy — it returns an iterator and runs `f` only as values are pulled."),
    ("How do iterator helpers make infinite sequences safe?", "`take(n)` (or `find`, `some`, a `break`) stops pulling, so only finitely many values are computed."),
    ("How do you use iterator helpers on an `Iterable<T>`?", "`Iterator.from(iterable).map(…)` — plain iterables don't carry the helpers."),
    ("A binary heap's `push`/`pop` cost?", "O(log n) each; `peek` is O(1)."),
    ("Comparator contract for a heap or `sort`?", "Negative when `a` should come first, positive when `b` should, zero for a tie."),
    ("How do you keep equal priorities in arrival order in a heap?", "Add an insertion counter and compare it when priorities tie."),
]

# ===========================================================================
# Week 25 — Errors, Result, resource management, error causes
# ===========================================================================

_RESULT_SRC = r"""
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
const err = <E>(error: E): Result<never, E> => ({ ok: false, error });
function andThen<T, U, E>(r: Result<T, E>, fn: (value: T) => Result<U, E>): Result<U, E> {
  return r.ok ? fn(r.value) : r;
}
""".strip("\n")

TS_PROBLEM_SETS[25] = [
    _tsp(25, "tsm-w25-result-chain", "A calculation that returns its failures", "warm-up",
         "Each input line is `<a> / <b>` or `sqrt <a>`. Parse, compute and round with functions that return `Result<number, string>` chained with `andThen` — no exceptions. Print the value (at most 4 decimals) or `error: <message>` — `bad number <x>`, `division by zero`, `negative root`, `unknown operation`.",
         _RESULT_SRC + r"""
const num = (text: string): Result<number> => (text.trim() !== "" && Number.isFinite(Number(text)) ? ok(Number(text)) : err(`bad number ${text}`));
const divide = (a: number, b: number): Result<number> => (b === 0 ? err("division by zero") : ok(a / b));
const root = (a: number): Result<number> => (a < 0 ? err("negative root") : ok(Math.sqrt(a)));
function evaluate(line: string): Result<number> {
  const parts = line.trim().split(/\s+/);
  const [x = "", y = "", z = ""] = parts;
  if (x === "sqrt" && parts.length === 2) return andThen(num(y), root);
  if (y === "/" && parts.length === 3) return andThen(num(x), (a) => andThen(num(z), (b) => divide(a, b)));
  return err("unknown operation");
}
for (const line of input.split("\n")) {
  const r = evaluate(line);
  console.log(r.ok ? String(Number(r.value.toFixed(4))) : `error: ${r.error}`);
}
""", ["10 / 4\n1 / 0\nsqrt 2\nsqrt -9\nx / 2\n5 * 3", "7 / 3"],
         hints=["`andThen` runs the next step only when the previous one succeeded, and passes failures straight through.",
                "Every function returns a `Result`, so the failure is part of its type."]),
    _tsp(25, "tsm-w25-safe-json", "Parse JSON without throwing", "warm-up",
         "Write `safeParse(text): Result<unknown, string>` around `JSON.parse`. Each input line should be JSON of the form `{ \"items\": [numbers…] }`. Print `sum <s> of <n>` or `error: <reason>` — `invalid JSON`, `not an object`, `missing items`, `items must be a list of numbers`.",
         _RESULT_SRC + r"""
function safeParse(text: string): Result<unknown> {
  try {
    return ok(JSON.parse(text));
  } catch {
    return err("invalid JSON");
  }
}
function items(data: unknown): Result<number[]> {
  if (typeof data !== "object" || data === null || Array.isArray(data)) return err("not an object");
  if (!("items" in data)) return err("missing items");
  const xs = data.items;
  return Array.isArray(xs) && xs.every((x) => typeof x === "number") ? ok(xs) : err("items must be a list of numbers");
}
for (const line of input.split("\n")) {
  const r = andThen(safeParse(line), items);
  console.log(r.ok ? `sum ${r.value.reduce((a, b) => a + b, 0)} of ${r.value.length}` : `error: ${r.error}`);
}
""", ['{"items":[1,2,3.5]}\n{"items":[]}\n{items}\n[1,2]\n{"list":[1]}\n{"items":[1,"2"]}'],
         hints=["Catch once, at the boundary, and convert the exception into a `Result`."]),
    _tsp(25, "tsm-w25-cause-chain", "Errors that remember why", "warm-up",
         "Three layers import records: `parseAge(text)` throws a `RangeError`; `loadRecord(line)` catches it and throws `Error(\"bad record '<line>'\", { cause })`; `importAll(lines)` catches that and throws `Error(\"import failed at line <n>\", { cause })`. Each input is a list of records `<name>:<age>` (one per line); import them all. Print `imported <k>` on success, or the error chain, one message per line indented two spaces per level.",
         r"""
function parseAge(text: string): number {
  const n = Number(text);
  if (!Number.isInteger(n) || n < 0 || n > 150) throw new RangeError(`age out of range: ${text}`);
  return n;
}
function loadRecord(line: string): { name: string; age: number } {
  const [name = "", age = ""] = line.split(":");
  try {
    return { name, age: parseAge(age) };
  } catch (cause) {
    throw new Error(`bad record '${line}'`, { cause });
  }
}
function importAll(lines: string[]): number {
  lines.forEach((line, i) => {
    try {
      loadRecord(line);
    } catch (cause) {
      throw new Error(`import failed at line ${i + 1}`, { cause });
    }
  });
  return lines.length;
}
try {
  console.log(`imported ${importAll(input.split("\n"))}`);
} catch (e) {
  let depth = 0;
  for (let err: unknown = e; err instanceof Error; err = err.cause) console.log(`${"  ".repeat(depth++)}${err.name}: ${err.message}`);
}
""", ["ana:31\nbo:25", "ana:31\nbo:-4\ncy:200", "x:abc"],
         hints=["Pass the caught value as `{ cause }` when throwing the higher-level error.",
                "Walk `.cause` while it is an `Error`."]),
    _tsp(25, "tsm-w25-fail-fast", "Fail fast, or collect everything", "core",
         "The first input line is `fail-fast` or `collect`; each later line is a record `<name> <age> <email>`. Validate every record (name 2+ letters, age a whole number 0-150, email containing `@`) with a `ValidationError` subclass carrying `line` and `field`. In `fail-fast` mode throw the first error; in `collect` mode throw one `AggregateError` of all of them. Print `all <n> valid`, or `line <l> <field>: <message>` for each error reported, then `<k> error(s)`.",
         r"""
class ValidationError extends Error {
  override readonly name = "ValidationError";
  readonly line: number;
  readonly field: string;
  constructor(line: number, field: string, message: string) {
    super(message);
    this.line = line;
    this.field = field;
  }
}
function check(line: number, record: string): ValidationError[] {
  const [name = "", age = "", email = ""] = record.trim().split(/\s+/);
  const problems: ValidationError[] = [];
  if (!/^[A-Za-z]{2,}$/.test(name)) problems.push(new ValidationError(line, "name", "needs 2+ letters"));
  const n = Number(age);
  if (!/^\d+$/.test(age) || n > 150) problems.push(new ValidationError(line, "age", "must be 0-150"));
  if (!email.includes("@")) problems.push(new ValidationError(line, "email", "must contain @"));
  return problems;
}
function validate(mode: string, records: string[]): number {
  const all: ValidationError[] = [];
  records.forEach((r, i) => {
    const problems = check(i + 1, r);
    const first = problems[0];
    if (mode === "fail-fast" && first !== undefined) throw first;
    all.push(...problems);
  });
  if (all.length > 0) throw new AggregateError(all, `${all.length} problems`);
  return records.length;
}
const [mode = "collect", ...records] = input.split("\n");
try {
  console.log(`all ${validate(mode.trim(), records)} valid`);
} catch (e) {
  const errors = e instanceof AggregateError ? e.errors : [e];
  for (const x of errors) if (x instanceof ValidationError) console.log(`line ${x.line} ${x.field}: ${x.message}`);
  console.log(`${errors.length} error(s)`);
}
""", ["collect\nana 31 ana@x.io\nb 200 bo\ncy 40 cy@z.io\ndee x dee@", "fail-fast\nana 31 ana@x.io\nb 200 bo\ndee x dee@", "fail-fast\nana 1 a@b"],
         hints=["Both modes share one validator; only what is thrown differs.", "`AggregateError.errors` holds the list."]),
    _tsp(25, "tsm-w25-retry", "Retry only what is worth retrying", "core",
         "An operation's outcomes are scripted on the input's first line, one per attempt: `ok:<value>`, `fail:timeout`, `fail:busy` (both retryable) or `fail:auth`, `fail:invalid` (not). The second line is the maximum number of attempts. Model failures as a union `{ kind; retryable }`, return `Result`s, and retry retryable failures only. Print `attempt <n>: <ok value|failed kind>` for each attempt, then `result <value>` or `gave up: <kind> (<reason>)` with reason `not retryable` or `out of attempts`.",
         _RESULT_SRC + r"""
type Failure = { kind: string; retryable: boolean };
const RETRYABLE = new Set(["timeout", "busy"]);
const [script = "", maxText = "1"] = input.split("\n");
const outcomes = script.trim().split(/\s+/);
let calls = 0;
function operation(): Result<string, Failure> {
  const outcome = outcomes[calls++] ?? "fail:invalid";
  const [tag = "", detail = ""] = outcome.split(":");
  return tag === "ok" ? ok(detail) : err({ kind: detail, retryable: RETRYABLE.has(detail) });
}
function retry(max: number): { result: Result<string, Failure>; reason: string } {
  for (let attempt = 1; ; attempt++) {
    const r = operation();
    console.log(`attempt ${attempt}: ${r.ok ? r.value : `failed ${r.error.kind}`}`);
    if (r.ok) return { result: r, reason: "" };
    if (!r.error.retryable) return { result: r, reason: "not retryable" };
    if (attempt >= max) return { result: r, reason: "out of attempts" };
  }
}
const { result, reason } = retry(Number(maxText));
console.log(result.ok ? `result ${result.value}` : `gave up: ${result.error.kind} (${reason})`);
""", ["fail:timeout fail:busy ok:42\n5", "fail:timeout fail:auth ok:1\n5", "fail:busy fail:busy fail:busy\n2", "ok:first\n1"],
         hints=["Put `retryable` on the failure value itself, so the retry loop needs no knowledge of specific kinds."]),
    _tsp(25, "tsm-w25-using-scopes", "Nested scopes with `using`", "core",
         "The input is a little script: `open <name>` acquires a resource in the current block, `{` and `}` open and close a nested block, `log <text>` prints the text, and `fail <message>` throws. Run it with one function per block that declares every resource with `using`, so resources are released in reverse order when their block ends — however it ends. Resources print `open <name>` and `close <name>`; an uncaught failure prints `error: <message>` once everything is closed.",
         r"""
class Resource implements Disposable {
  readonly name: string;
  constructor(name: string) {
    this.name = name;
    console.log(`open ${name}`);
  }
  [Symbol.dispose](): void {
    console.log(`close ${this.name}`);
  }
}
const lines = input.split("\n").map((l) => l.trim());
let pos = 0;
function runBlock(): void {
  using stack = new DisposableStack();
  while (pos < lines.length) {
    const [cmd = "", ...rest] = (lines[pos++] ?? "").split(" ");
    const arg = rest.join(" ");
    if (cmd === "}") return;
    if (cmd === "{") runBlock();
    else if (cmd === "open") stack.use(new Resource(arg));
    else if (cmd === "log") console.log(arg);
    else if (cmd === "fail") throw new Error(arg);
  }
}
try {
  runBlock();
  console.log("finished");
} catch (e) {
  console.log(`error: ${e instanceof Error ? e.message : String(e)}`);
}
""", ["open db\n{\nopen file\nlog working\n}\nopen cache\nlog done", "open a\n{\nopen b\n{\nopen c\nfail disk full\nlog never\n}\n}\nopen z", "log nothing to open"],
         hints=["A `DisposableStack` held by `using` collects every resource opened in its block.",
                "Recursion gives each `{ … }` its own stack, so inner resources close before outer ones."]),
    _tsp(25, "tsm-w25-transfer", "Transfers that roll back", "core",
         "Accounts are given on the first line as `name=balance`. Each later line is a transfer `<from> <to> <amount>` made of three steps — debit the sender, credit the receiver, charge the sender a fee of 1 — any of which can fail (unknown account, insufficient funds, or a `frozen` receiver listed on the second line as `frozen <names…>`). Undo completed steps in reverse order when a later step fails, using a `DisposableStack` whose rollback is disarmed with `move()` on success. Print `ok` or `failed: <reason>` and then all balances in the order given.",
         r"""
const [accountLine = "", frozenLine = "", ...transfers] = input.split("\n");
const balances = new Map<string, number>();
for (const pair of accountLine.trim().split(/\s+/)) {
  const [name = "", amount = "0"] = pair.split("=");
  balances.set(name, Number(amount));
}
const frozen = new Set(frozenLine.trim().split(/\s+/).slice(1));
function adjust(name: string, delta: number): void {
  const current = balances.get(name);
  if (current === undefined) throw new Error(`unknown account ${name}`);
  if (current + delta < 0) throw new Error(`insufficient funds in ${name}`);
  if (delta > 0 && frozen.has(name)) throw new Error(`${name} is frozen`);
  balances.set(name, current + delta);
}
function transfer(from: string, to: string, amount: number): void {
  using undo = new DisposableStack();
  adjust(from, -amount);
  undo.defer(() => balances.set(from, (balances.get(from) ?? 0) + amount));
  adjust(to, amount);
  undo.defer(() => balances.set(to, (balances.get(to) ?? 0) - amount));
  adjust(from, -1);
  undo.move();
}
for (const line of transfers) {
  const [from = "", to = "", amount = "0"] = line.trim().split(/\s+/);
  try {
    transfer(from, to, Number(amount));
    console.log("ok");
  } catch (e) {
    console.log(`failed: ${e instanceof Error ? e.message : String(e)}`);
  }
  console.log([...balances].map(([n, b]) => `${n}=${b}`).join(" "));
}
""", ["ana=100 bo=20 cy=0\nfrozen cy\nana bo 50\nbo ana 20\nana cy 10\nana dee 5\nbo ana 49", "x=10 y=0\nfrozen\nx y 10\nx y 9"],
         hints=["Register each step's undo right after the step succeeds; `move()` at the end means nothing is undone."]),
    _tsp_types(25, "tsm-w25-map-result", "Type `mapResult`", "core",
               "Write the signature of `mapResult`: it takes a `Result<T, E>` and a function from `T` to `U`, and returns a `Result<U, E>` — the error type passes through untouched.",
               '''
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
function mapResult<T, U, E>(r: Result<T, E>, fn: (value: T) => U): Result<U, E> {
  return r.ok ? { ok: true, value: fn(r.value) } : r;
}
declare const parsed: Result<string, "empty" | "too long">;
const lengths = mapResult(parsed, (s) => s.length);
''', "function mapResult<T, U, E>(r: Result<T, E>, fn: (value: T) => U): Result<U, E> {",
               '''
type _1 = Expect<Equal<typeof lengths, Result<number, "empty" | "too long">>>;
''', hints=["Three type parameters: the input value, the output value, and the error.", "The callback turns a `T` into a `U`."]),
    _tsp_types(25, "tsm-w25-error-kinds", "Error kinds from a union", "warm-up",
               "Application errors are a discriminated union. Derive `ErrorKind` — the union of their `kind` tags — from `AppError`, so a new error kind is added in one place.",
               '''
type AppError =
  | { kind: "not-found"; id: string }
  | { kind: "invalid"; field: string }
  | { kind: "timeout"; ms: number };
type ErrorKind = AppError["kind"];
''', 'AppError["kind"]',
               '''
type _1 = Expect<Equal<ErrorKind, "not-found" | "invalid" | "timeout">>;
''', hints=["An indexed access on a union type reads the property from every member."]),
]

TS_PROJECTS[25] = _project(
    25, "parse.ts — a Result-based CSV importer",
    "Parse a CSV file without a single `throw` in the parsing path: every field parser returns a `Result`, every row collects all of its problems with line and column, and the caller decides what to do with the good rows and the bad ones.",
    ["The first line is the header and must be exactly `name,age,email` (otherwise print `bad header` and stop). Each later line is a row; a field may be wrapped in double quotes, in which case it may contain commas (`\"Lee, Ana\",31,ana@x.io`).",
     "Fields: `name` non-empty after trimming; `age` a whole number 0-150; `email` exactly one `@` with text on both sides. A row with the wrong number of fields is `line <n>: expected 3 fields, got <k>`.",
     "For each bad row print `line <n>: <column>: <problem>` for every problem in the row (column order), with problems `required`, `must be a whole number from 0 to 150`, `invalid email`. Line numbers count the header as line 1.",
     "Then print the good rows as `<name> (<age>) <email>` and a summary `imported <good> of <rows> rows`.",
     "Use `Result<T, string>` for every field parser and an unclosed quote as `line <n>: unclosed quote`."],
    _RESULT_SRC + r"""
function splitCsv(line: string): Result<string[]> {
  const fields: string[] = [];
  let cur = "";
  let quoted = false;
  for (let i = 0; i < line.length; i++) {
    const c = line.charAt(i);
    if (quoted) {
      if (c === '"' && line.charAt(i + 1) === '"') {
        cur += '"';
        i++;
      } else if (c === '"') quoted = false;
      else cur += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") {
      fields.push(cur);
      cur = "";
    } else cur += c;
  }
  if (quoted) return err("unclosed quote");
  fields.push(cur);
  return ok(fields);
}
const name = (s: string): Result<string> => (s.trim() === "" ? err("required") : ok(s.trim()));
const age = (s: string): Result<number> => {
  const t = s.trim();
  if (t === "") return err("required");
  return /^\d+$/.test(t) && Number(t) <= 150 ? ok(Number(t)) : err("must be a whole number from 0 to 150");
};
const email = (s: string): Result<string> => {
  const t = s.trim();
  if (t === "") return err("required");
  const parts = t.split("@");
  return parts.length === 2 && parts.every((p) => p !== "") ? ok(t) : err("invalid email");
};
type Row = { name: string; age: number; email: string };
const [header = "", ...rows] = input.split("\n");
if (header.trim() !== "name,age,email") {
  console.log("bad header");
} else {
  const good: Row[] = [];
  rows.forEach((line, i) => {
    const n = i + 2;
    const split = splitCsv(line);
    if (!split.ok) {
      console.log(`line ${n}: ${split.error}`);
      return;
    }
    if (split.value.length !== 3) {
      console.log(`line ${n}: expected 3 fields, got ${split.value.length}`);
      return;
    }
    const [a = "", b = "", c = ""] = split.value;
    const results = [["name", name(a)], ["age", age(b)], ["email", email(c)]] as const;
    const problems = results.flatMap(([col, r]) => (r.ok ? [] : [`line ${n}: ${col}: ${r.error}`]));
    const [, nr] = results[0];
    const [, ar] = results[1];
    const [, er] = results[2];
    if (problems.length > 0 || !nr.ok || !ar.ok || !er.ok) {
      for (const p of problems) console.log(p);
      return;
    }
    good.push({ name: nr.value, age: ar.value, email: er.value });
  });
  for (const r of good) console.log(`${r.name} (${r.age}) ${r.email}`);
  console.log(`imported ${good.length} of ${rows.length} rows`);
}
""", ['name,age,email\nana,31,ana@x.io\n"Lee, Bo",40,bo@y.io\ncy,,cy@z\n,200,nope\ndee,20',
      'name,age,email\n"unclosed,1,a@b\n"say ""hi""",5,q@w.io',
      'name,email,age\nana,31,a@b',
      'name,age,email\nx,0,@b.c\ny,150,a@b@c\nz,151,z@z.z',
      'name,age,email\n  spaced  , 7 , s@p.a '],
    stretch=["Report the column index as well as the name, and suggest a fix for common mistakes (`age: \"31y\"`).",
             "Return all rows as a single `Result<Row[], RowError[]>` and let `main` choose between fail-fast and collect."],
)

TS_PRACTICE_MORE[25] = [
    _pr("tsm-w25-p1", "A catch variable", 'let caught;\ntry {\n  JSON.parse("{");\n} catch (e) {\n  caught = e;\n}\nconst failure = caught;\n', "failure", "unknown",
        strictness=_SI, hints=["Under `strict`, a catch variable is `unknown`.", "`caught` evolves to whatever was assigned."]),
    _dx("tsm-w25-d1", "`using` needs a disposable",
        "error TS2850: The initializer of a 'using' declaration must be either an object with a '[Symbol.dispose]()' method, or be 'null' or 'undefined'.",
        'const file = { name: "log.txt", close: () => console.log("closed") };\nfunction read(): void {\n  using f = file;\n  console.log("reading " + f.name);\n}\nread();\n',
        'const file = { name: "log.txt", [Symbol.dispose]: () => console.log("closed") };\nfunction read(): void {\n  using f = file;\n  console.log("reading " + f.name);\n}\nread();\n',
        [("", "reading log.txt\nclosed")], strictness=_SI,
        hints=["`using` calls `[Symbol.dispose]()`, not `close()`.", "Rename the method to the well-known symbol."], difficulty="Medium"),
    _fx("tsm-w25-f1", "A catch that assumed an Error",
        "Print `failed: <message>` for whatever `risky` throws. It prints `failed: undefined`.",
        _STDIN + 'function risky(): void {\n  throw input;\n}\ntry {\n  risky();\n} catch (e) {\n  console.log("failed: " + (e as Error).message);\n}\n',
        _STDIN + 'function risky(): void {\n  throw input;\n}\ntry {\n  risky();\n} catch (e) {\n  console.log("failed: " + (e instanceof Error ? e.message : String(e)));\n}\n',
        [("disk full", "failed: disk full")], strictness=_SI,
        hints=["Anything can be thrown — here, a string.", "Narrow with `instanceof Error`, else use `String(e)`."]),
]

TS_CARDS_MORE[25] = [
    ("What does `using x = r` guarantee?", "`r[Symbol.dispose]()` runs when the block exits, however it exits — in reverse order for several `using`s."),
    ("`await using` — where is it allowed?", "In async functions and at a module's top level (TS2852 elsewhere)."),
    ("What is `DisposableStack.move()` for?", "Handing the collected cleanups to a new owner, so the current stack won't run them — the \"commit\" of a setup."),
    ("How do you chain a low-level error to a high-level one?", "`throw new Error(\"high-level\", { cause: original })` — walk `.cause` to read the chain."),
    ("What does `AggregateError` hold?", "Several errors in `.errors`, plus its own message — e.g. every validation failure, or every rejection from `Promise.any`."),
    ("When does a `Result` beat an exception?", "For expected failures the caller must handle; throw for failures it can't (bugs, lost connections)."),
]

# ===========================================================================
# Week 26 — Async, event loop, cancellation, async iteration
# ===========================================================================

_VCLOCK = r"""
// A virtual clock: time moves only when every pending microtask has settled
// and the next timer is fired, so output never depends on machine speed.
class VirtualClock {
  now = 0;
  #timers: { at: number; seq: number; fire: () => void }[] = [];
  #seq = 0;
  sleep(ms: number, signal?: AbortSignal): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      if (signal?.aborted === true) {
        reject(signal.reason);
        return;
      }
      const timer = { at: this.now + ms, seq: this.#seq++, fire: () => resolve() };
      this.#timers.push(timer);
      signal?.addEventListener("abort", () => {
        this.#timers = this.#timers.filter((t) => t !== timer);
        reject(signal.reason);
      }, { once: true });
    });
  }
  async run(): Promise<void> {
    for (;;) {
      await new Promise<void>((r) => setTimeout(r, 0));
      this.#timers.sort((a, b) => a.at - b.at || a.seq - b.seq);
      const next = this.#timers.shift();
      if (next === undefined) return;
      this.now = next.at;
      next.fire();
    }
  }
}
const clock = new VirtualClock();
""".strip("\n")

TS_PROBLEM_SETS[26] = [
    _tsp(26, "tsm-w26-throttle", "Throttle a stream of events", "warm-up",
         "The first input line is the throttle interval in ms; the second, event times in ms (ascending). A leading-edge throttle lets an event through if at least `interval` ms have passed since the last event it let through. Print the times let through, then `dropped <k>`. (A pure function over timestamps — no timers needed.)",
         r"""
function throttle(times: readonly number[], interval: number): number[] {
  const out: number[] = [];
  let last = -Infinity;
  for (const t of times) {
    if (t - last >= interval) {
      out.push(t);
      last = t;
    }
  }
  return out;
}
const [intervalText = "0", timesText = ""] = input.split("\n");
const times = timesText.trim().split(/\s+/).map(Number);
const passed = throttle(times, Number(intervalText));
console.log(passed.join(" "));
console.log(`dropped ${times.length - passed.length}`);
""", ["100\n0 20 90 100 150 199 200 350", "50\n5", "10\n0 10 20 30"],
         hints=["Remember the time of the last event let through, not the last event seen."]),
    _tsp(26, "tsm-w26-all-settled", "Settle everything, report in order", "warm-up",
         "Each input line is a task `<name> <ok|fail> <delay> <value>`. Start every task at time 0 on the virtual clock: it sleeps `delay` ms and then resolves with the value or rejects with `Error(value)`. As each settles print `t=<time> <name> <fulfilled|rejected>`; then use `Promise.allSettled` to print a report in input order — `<name>: <value>` or `<name> failed: <message>` — and `finished at t=<time>`.",
         _VCLOCK + r"""
type Task = { name: string; succeed: boolean; delay: number; value: string };
const tasks: Task[] = input.split("\n").map((line) => {
  const [name = "", outcome = "", delay = "0", value = ""] = line.trim().split(/\s+/);
  return { name, succeed: outcome === "ok", delay: Number(delay), value };
});
async function runTask(t: Task): Promise<string> {
  await clock.sleep(t.delay);
  console.log(`t=${clock.now} ${t.name} ${t.succeed ? "fulfilled" : "rejected"}`);
  if (!t.succeed) throw new Error(t.value);
  return t.value;
}
async function main(): Promise<void> {
  const results = await Promise.allSettled(tasks.map(runTask));
  results.forEach((r, i) => {
    const name = tasks[i]?.name ?? "?";
    console.log(r.status === "fulfilled" ? `${name}: ${r.value}` : `${name} failed: ${r.reason instanceof Error ? r.reason.message : String(r.reason)}`);
  });
  console.log(`finished at t=${clock.now}`);
}
const done = main();
await clock.run();
await done;
""", ["a ok 30 alpha\nb fail 10 boom\nc ok 10 gamma\nd fail 50 late", "solo ok 0 x"],
         hints=["`Promise.allSettled` never rejects; each result says `fulfilled` or `rejected`.",
                "Its results are in input order, whatever order the tasks finished in."]),
    _tsp(26, "tsm-w26-pool", "A concurrency-limited pool", "core",
         "The first input line is the concurrency limit; each later line is a job `<name> <duration>`. Run the jobs on the virtual clock with at most that many at once, starting jobs in input order as slots free up. Print `t=<time> start <name>` and `t=<time> end <name>` as they happen, then `all done at t=<time>` and the results in input order (`<name>=<duration>`).",
         _VCLOCK + r"""
async function pool<T, R>(items: readonly T[], limit: number, worker: (item: T) => Promise<R>): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let next = 0;
  async function lane(): Promise<void> {
    while (next < items.length) {
      const i = next++;
      const item = items[i];
      if (item !== undefined) results[i] = await worker(item);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, lane));
  return results;
}
const [limitText = "1", ...lines] = input.split("\n");
const jobs = lines.map((l) => {
  const [name = "", duration = "0"] = l.trim().split(/\s+/);
  return { name, duration: Number(duration) };
});
async function main(): Promise<void> {
  const results = await pool(jobs, Number(limitText), async (job) => {
    console.log(`t=${clock.now} start ${job.name}`);
    await clock.sleep(job.duration);
    console.log(`t=${clock.now} end ${job.name}`);
    return `${job.name}=${job.duration}`;
  });
  console.log(`all done at t=${clock.now}`);
  console.log(results.join(" "));
}
const done = main();
await clock.run();
await done;
""", ["2\na 30\nb 10\nc 10\nd 20\ne 5", "1\nx 5\ny 5", "5\np 7\nq 3"],
         hints=["Start `limit` lanes; each lane repeatedly takes the next unclaimed index until none are left.",
                "Store each result at its own index so the output order is the input order."]),
    _tsp(26, "tsm-w26-timeouts", "Every load, with a timeout", "core",
         "The first input line is the timeout in ms; each later line is `<name> <duration>`. Load all resources concurrently on the virtual clock, racing each load against the timeout; a load that times out is cancelled with an `AbortSignal` so its timer is removed. Print results in input order as `<name>: loaded in <d>ms` or `<name>: timed out after <t>ms`, then `done at t=<time>` — which must be at most the timeout.",
         _VCLOCK + r"""
type Outcome = { ok: true; ms: number } | { ok: false; after: number };
async function load(duration: number, signal: AbortSignal): Promise<number> {
  await clock.sleep(duration, signal);
  return duration;
}
async function withTimeout(duration: number, timeout: number): Promise<Outcome> {
  const controller = new AbortController();
  const timer = new AbortController();
  const timedOut = clock.sleep(timeout, timer.signal).then((): Outcome => {
    controller.abort(new Error("timeout"));
    return { ok: false, after: timeout };
  }, (): Outcome => ({ ok: false, after: timeout }));
  const loaded = load(duration, controller.signal).then((ms): Outcome => {
    timer.abort();
    return { ok: true, ms };
  }, (): Outcome => ({ ok: false, after: timeout }));
  return Promise.race([loaded, timedOut]);
}
const [timeoutText = "0", ...lines] = input.split("\n");
const timeout = Number(timeoutText);
const items = lines.map((l) => {
  const [name = "", d = "0"] = l.trim().split(/\s+/);
  return { name, duration: Number(d) };
});
async function main(): Promise<void> {
  const outcomes = await Promise.all(items.map((it) => withTimeout(it.duration, timeout)));
  outcomes.forEach((o, i) => {
    const name = items[i]?.name ?? "?";
    console.log(o.ok ? `${name}: loaded in ${o.ms}ms` : `${name}: timed out after ${o.after}ms`);
  });
  console.log(`done at t=${clock.now}`);
}
const done = main();
await clock.run();
await done;
""", ["50\nusers 20\nposts 80\nstats 50\nlogo 5", "10\nslow 100"],
         hints=["Race each load against its own timer; whichever wins cancels the other through an `AbortController`.",
                "Because cancelled timers are removed, the clock stops as soon as the last race is decided."]),
    _tsp(26, "tsm-w26-backoff", "Retry with exponential backoff", "core",
         "The first input line is the outcome of each attempt (`ok` or `fail`); the second, the base delay in ms; the third, the maximum number of attempts. On the virtual clock, retry a failed attempt after `base`, then `2·base`, `4·base`, … ms. Print `t=<time> attempt <n>: <ok|fail>` for each, then `succeeded at t=<time>` or `gave up at t=<time>`.",
         _VCLOCK + r"""
const [outcomesText = "", baseText = "100", maxText = "3"] = input.split("\n");
const outcomes = outcomesText.trim().split(/\s+/);
async function withBackoff(max: number, base: number): Promise<boolean> {
  for (let attempt = 1; attempt <= max; attempt++) {
    const success = outcomes[attempt - 1] === "ok";
    console.log(`t=${clock.now} attempt ${attempt}: ${success ? "ok" : "fail"}`);
    if (success) return true;
    if (attempt < max) await clock.sleep(base * 2 ** (attempt - 1));
  }
  return false;
}
async function main(): Promise<void> {
  const success = await withBackoff(Number(maxText), Number(baseText));
  console.log(`${success ? "succeeded" : "gave up"} at t=${clock.now}`);
}
const done = main();
await clock.run();
await done;
""", ["fail fail ok\n100\n5", "fail fail fail fail\n50\n3", "ok\n10\n1"],
         hints=["The n-th wait is `base * 2 ** (n - 1)`.", "No wait after the last attempt."]),
    _tsp(26, "tsm-w26-debounce", "Debounce a search box", "core",
         "The first input line is the debounce wait in ms; each later line is `<time> <character>` — a keystroke typed into a search box. On the virtual clock, deliver each keystroke at its time to a debounced `search` function: it runs only once the user has paused for the wait, with the full text typed so far. Print `t=<time> search \"<text>\"` for each call that actually runs, then `searches: <k>, keystrokes: <n>`.",
         _VCLOCK + r"""
function debounce(fn: (text: string) => void, wait: number): (text: string) => void {
  let pending: AbortController | undefined;
  return (text) => {
    pending?.abort();
    const controller = new AbortController();
    pending = controller;
    clock.sleep(wait, controller.signal).then(() => fn(text), () => {});
  };
}
const [waitText = "0", ...lines] = input.split("\n");
let searches = 0;
const search = debounce((text) => {
  searches++;
  console.log(`t=${clock.now} search "${text}"`);
}, Number(waitText));
let typed = "";
async function main(): Promise<void> {
  for (const line of lines) {
    const [time = "0", ch = ""] = line.trim().split(/\s+/);
    await clock.sleep(Number(time) - clock.now);
    typed += ch;
    search(typed);
  }
}
const done = main();
await clock.run();
await done;
console.log(`searches: ${searches}, keystrokes: ${lines.length}`);
""", ["100\n0 t\n50 y\n120 p\n400 e\n450 s\n700 c", "30\n0 a\n10 b"],
         hints=["Each keystroke cancels the pending timer and starts a new one; only a timer that survives the whole wait fires."]),
    _tsp(26, "tsm-w26-async-queue", "An async queue", "core",
         "Write `class AsyncQueue<T>` with `push(item)`, `async pop(): Promise<T | undefined>` (waits for an item; resolves `undefined` once the queue is closed and empty) and `close()`. Waiting consumers are served in the order they started waiting; items pushed with nobody waiting are buffered. Commands: `consume <name>` (start one `pop` that prints `<name> got <item>` or `<name> got nothing (closed)`), `push <item>`, `close`, `size` (buffered items). Let every microtask settle after each command.",
         r"""
class AsyncQueue<T> {
  readonly #items: T[] = [];
  readonly #waiting: ((item: T | undefined) => void)[] = [];
  #closed = false;
  push(item: T): void {
    const waiter = this.#waiting.shift();
    if (waiter !== undefined) waiter(item);
    else this.#items.push(item);
  }
  pop(): Promise<T | undefined> {
    if (this.#items.length > 0) return Promise.resolve(this.#items.shift());
    if (this.#closed) return Promise.resolve(undefined);
    const { promise, resolve } = Promise.withResolvers<T | undefined>();
    this.#waiting.push(resolve);
    return promise;
  }
  close(): void {
    this.#closed = true;
    for (const waiter of this.#waiting.splice(0)) waiter(undefined);
  }
  get size(): number {
    return this.#items.length;
  }
}
const queue = new AsyncQueue<string>();
const settle = () => new Promise<void>((r) => setTimeout(r, 0));
for (const line of input.split("\n")) {
  const [cmd = "", arg = ""] = line.trim().split(/\s+/);
  if (cmd === "consume") {
    void queue.pop().then((item) => console.log(item === undefined ? `${arg} got nothing (closed)` : `${arg} got ${item}`));
  } else if (cmd === "push") queue.push(arg);
  else if (cmd === "close") queue.close();
  else if (cmd === "size") console.log(`size ${queue.size}`);
  await settle();
}
""", ["consume ana\nconsume bo\npush x\npush y\npush z\nsize\nconsume cy\nconsume dee\nclose\nconsume eve", "push a\nclose\nconsume x\nconsume y"],
         hints=["Keep two queues: buffered items and waiting consumers' `resolve` functions — at most one of them is non-empty.",
                "`Promise.withResolvers` gives you the `resolve` to store for a waiting consumer."]),
    _tsp(26, "tsm-w26-pages", "Paginate with an async generator", "warm-up",
         "A simulated API holds the input's items (first line) and returns pages of the size on the second line, with a `next` cursor (or `null` at the end). Write an async generator `allItems()` that follows the cursors and `yield*`s each page. The third line is how many items to take: print `page <n>` whenever a page is fetched, the items taken (space-separated), and `fetched <k> pages`. Stop fetching as soon as enough items have been taken.",
         r"""
const [itemsLine = "", sizeText = "2", takeText = "0"] = input.split("\n");
const DATA = itemsLine.trim().split(/\s+/);
const size = Number(sizeText);
let fetched = 0;
async function fetchPage(cursor: number): Promise<{ items: string[]; next: number | null }> {
  fetched++;
  console.log(`page ${fetched}`);
  await null;
  const items = DATA.slice(cursor, cursor + size);
  return { items, next: cursor + size < DATA.length ? cursor + size : null };
}
async function* allItems(): AsyncGenerator<string> {
  let cursor: number | null = 0;
  while (cursor !== null) {
    const page: { items: string[]; next: number | null } = await fetchPage(cursor);
    yield* page.items;
    cursor = page.next;
  }
}
const want = Number(takeText);
const taken: string[] = [];
if (want > 0) {
  for await (const item of allItems()) {
    taken.push(item);
    if (taken.length >= want) break;
  }
}
console.log(taken.join(" ") || "(none)");
console.log(`fetched ${fetched} pages`);
""", ["a b c d e f g\n3\n4", "a b c\n2\n10", "x y\n1\n0"],
         hints=["Loop while there is a cursor; `yield*` hands out one page's items one by one.",
                "`break` in the consumer stops the generator, so no further page is fetched."]),
    _tsp(26, "tsm-w26-loader", "Load modules in dependency order", "stretch",
         "Each input line is `<module> <duration> [deps…]`. Load every module on the virtual clock as early as possible: a module starts when all its dependencies have finished, and independent modules load concurrently. Print `t=<time> start <m>` and `t=<time> ready <m>` as they happen, then `all ready at t=<time>`. If the dependencies contain a cycle, print only `cycle: <a> -> <b> -> … -> <a>` (found by a depth-first search visiting modules in input order).",
         _VCLOCK + r"""
type Mod = { name: string; duration: number; deps: string[] };
const mods = new Map<string, Mod>();
for (const line of input.split("\n")) {
  const [name = "", duration = "0", ...deps] = line.trim().split(/\s+/);
  mods.set(name, { name, duration: Number(duration), deps });
}
function findCycle(): string[] | undefined {
  const state = new Map<string, "visiting" | "done">();
  const path: string[] = [];
  const visit = (name: string): string[] | undefined => {
    if (state.get(name) === "done") return undefined;
    if (state.get(name) === "visiting") return [...path.slice(path.indexOf(name)), name];
    state.set(name, "visiting");
    path.push(name);
    for (const d of mods.get(name)?.deps ?? []) {
      const c = visit(d);
      if (c !== undefined) return c;
    }
    path.pop();
    state.set(name, "done");
    return undefined;
  };
  for (const name of mods.keys()) {
    const c = visit(name);
    if (c !== undefined) return c;
  }
  return undefined;
}
const loading = new Map<string, Promise<void>>();
function load(name: string): Promise<void> {
  const existing = loading.get(name);
  if (existing !== undefined) return existing;
  const p = (async () => {
    const m = mods.get(name);
    if (m === undefined) return;
    await Promise.all(m.deps.map(load));
    console.log(`t=${clock.now} start ${name}`);
    await clock.sleep(m.duration);
    console.log(`t=${clock.now} ready ${name}`);
  })();
  loading.set(name, p);
  return p;
}
const cycle = findCycle();
if (cycle !== undefined) {
  console.log(`cycle: ${cycle.join(" -> ")}`);
} else {
  const done = Promise.all([...mods.keys()].map(load)).then(() => console.log(`all ready at t=${clock.now}`));
  await clock.run();
  await done;
}
""", ["app 5 db cache\ndb 10 config\ncache 3 config\nconfig 2\nlog 4", "a 1 b\nb 1 c\nc 1 a", "solo 7"],
         hints=["Memoise one promise per module, so each loads once however many modules depend on it.",
                "`await Promise.all(deps.map(load))` waits for every dependency; independent modules overlap on the clock."]),
    _tsp(26, "tsm-w26-cancel", "A task runner you can cancel", "core",
         "Each input line is either `task <name> <steps> <ms per step>` or `cancel <name> at <time>`. On the virtual clock, run all tasks concurrently from time 0; each step sleeps its ms (with an `AbortSignal`) and then prints `t=<time> <name> step <k>`. A cancellation aborts that task's controller at the given time, which interrupts its current sleep. Print `t=<time> <name> done` or `t=<time> <name> cancelled after <k> steps`, then `summary: <done> done, <cancelled> cancelled`.",
         _VCLOCK + r"""
type TaskSpec = { name: string; steps: number; ms: number; controller: AbortController };
const tasks: TaskSpec[] = [];
const cancels: { name: string; at: number }[] = [];
for (const line of input.split("\n")) {
  const [kind = "", name = "", a = "0", b = "0"] = line.trim().split(/\s+/);
  if (kind === "task") tasks.push({ name, steps: Number(a), ms: Number(b), controller: new AbortController() });
  else if (kind === "cancel") cancels.push({ name, at: Number(b) });
}
let done = 0;
let cancelled = 0;
async function run(t: TaskSpec): Promise<void> {
  let k = 0;
  try {
    for (; k < t.steps; k++) {
      await clock.sleep(t.ms, t.controller.signal);
      console.log(`t=${clock.now} ${t.name} step ${k + 1}`);
    }
    done++;
    console.log(`t=${clock.now} ${t.name} done`);
  } catch {
    cancelled++;
    console.log(`t=${clock.now} ${t.name} cancelled after ${k} steps`);
  }
}
for (const c of cancels) {
  void clock.sleep(c.at).then(() => tasks.find((t) => t.name === c.name)?.controller.abort(new Error("cancelled")));
}
const all = Promise.all(tasks.map(run));
await clock.run();
await all;
console.log(`summary: ${done} done, ${cancelled} cancelled`);
""", ["task a 3 10\ntask b 5 7\ncancel b at 16\ncancel a at 100", "task x 2 5\ncancel x at 0"],
         hints=["Give each task its own `AbortController`; pass its signal to every sleep.",
                "An abort rejects the pending sleep, which lands in the task's `catch`."]),
]

TS_PROJECTS[26] = _project(
    26, "fetchAll.ts — concurrent loads with limits, timeouts and retries",
    "The Month 6 capstone of the async material: load a list of resources with at most two in flight, a per-attempt timeout, and one retry for failures — all on a virtual clock, so every run prints exactly the same thing. Results come back as a `Result` per resource, in input order, however the loads interleave.",
    ["The first input line is `timeout=<ms> retries=<n>`; each later line is `<name> <outcome>:<ms>[,<outcome>:<ms>…]` — the outcome (`ok` or `fail`) and duration of each successive attempt (an attempt beyond the list fails after 1 ms).",
     "Run at most 2 resources at once, starting them in input order. An attempt that hasn't finished by the timeout is cancelled (its timer removed) and counts as a failure `timeout`; a failed attempt is `error`. Failed attempts are retried immediately, up to `retries` extra attempts.",
     "Print `t=<time> <name> attempt <k> <ok|error|timeout>` as each attempt ends.",
     "Then print one line per resource in input order: `<name>: ok after <k> attempt(s)` or `<name>: failed (<last reason>) after <k> attempt(s)`, and finally `done at t=<time>, <ok>/<total> loaded`.",
     "Model each result as `Result<number, string>` and never let the output depend on real time."],
    _VCLOCK + r"""
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
type Attempt = { ok: boolean; ms: number };
const [config = "", ...lines] = input.split("\n");
const settings = new Map(config.trim().split(/\s+/).map((kv) => kv.split("=") as [string, string]));
const TIMEOUT = Number(settings.get("timeout") ?? "100");
const RETRIES = Number(settings.get("retries") ?? "0");
const resources = lines.map((line) => {
  const [name = "", spec = ""] = line.trim().split(/\s+/);
  const attempts: Attempt[] = spec.split(",").map((a) => {
    const [outcome = "fail", ms = "1"] = a.split(":");
    return { ok: outcome === "ok", ms: Number(ms) };
  });
  return { name, attempts };
});
async function attemptOnce(a: Attempt): Promise<"ok" | "error" | "timeout"> {
  const work = new AbortController();
  const timer = new AbortController();
  const finished = clock.sleep(a.ms, work.signal).then(() => {
    timer.abort();
    return a.ok ? ("ok" as const) : ("error" as const);
  }, () => "timeout" as const);
  const timedOut = clock.sleep(TIMEOUT, timer.signal).then(() => {
    work.abort();
    return "timeout" as const;
  }, () => "timeout" as const);
  return Promise.race([finished, timedOut]);
}
async function loadResource(r: { name: string; attempts: Attempt[] }): Promise<{ result: Result<number, string>; tries: number }> {
  let last = "error";
  for (let k = 1; k <= RETRIES + 1; k++) {
    const outcome = await attemptOnce(r.attempts[k - 1] ?? { ok: false, ms: 1 });
    console.log(`t=${clock.now} ${r.name} attempt ${k} ${outcome}`);
    if (outcome === "ok") return { result: { ok: true, value: clock.now }, tries: k };
    last = outcome;
  }
  return { result: { ok: false, error: last }, tries: RETRIES + 1 };
}
async function pool<T, R>(items: readonly T[], limit: number, worker: (item: T) => Promise<R>): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let next = 0;
  const lane = async (): Promise<void> => {
    while (next < items.length) {
      const i = next++;
      const item = items[i];
      if (item !== undefined) results[i] = await worker(item);
    }
  };
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, lane));
  return results;
}
async function main(): Promise<void> {
  const outcomes = await pool(resources, 2, loadResource);
  let loaded = 0;
  outcomes.forEach((o, i) => {
    const name = resources[i]?.name ?? "?";
    const plural = o.tries === 1 ? "attempt" : "attempts";
    if (o.result.ok) loaded++;
    console.log(o.result.ok ? `${name}: ok after ${o.tries} ${plural}` : `${name}: failed (${o.result.error}) after ${o.tries} ${plural}`);
  });
  console.log(`done at t=${clock.now}, ${loaded}/${resources.length} loaded`);
}
const done = main();
await clock.run();
await done;
""", ["timeout=50 retries=1\nusers ok:20\nposts fail:10,ok:30\nstats ok:80,ok:10\nlogo ok:5",
      "timeout=10 retries=0\nslow ok:100\nfast ok:1",
      "timeout=100 retries=2\nflaky fail:5,fail:5,ok:5\ndoomed fail:1,fail:1,fail:1",
      "timeout=30 retries=1\na ok:30\nb ok:29",
      "timeout=20 retries=3\nlonely fail:1"],
    stretch=["Add jitter to retries without losing determinism (a seeded generator, as in the DSA curriculum).",
             "Stream results as they complete with an async generator, while still offering the in-order summary."],
)

TS_PRACTICE_MORE[26] = [
    _pr("tsm-w26-p1", "What an async function returns", 'async function load() {\n  return 42;\n}\nconst pending = load();\n', "pending", "Promise<number>",
        strictness=_SI, hints=["An `async` function always returns a promise.", "Of the returned value's type."]),
    _dx("tsm-w26-d1", "A promise in a condition",
        "error TS2801: This condition will always return true since this 'Promise<boolean>' is always defined.",
        'async function isAdmin(name: string): Promise<boolean> {\n  return name === "ana";\n}\nasync function main(): Promise<void> {\n  if (isAdmin("bo")) console.log("welcome, admin");\n  else console.log("welcome");\n}\nawait main();\n',
        'async function isAdmin(name: string): Promise<boolean> {\n  return name === "ana";\n}\nasync function main(): Promise<void> {\n  if (await isAdmin("bo")) console.log("welcome, admin");\n  else console.log("welcome");\n}\nawait main();\n',
        [("", "welcome")], strictness=_SI, hints=["A promise object is always truthy.", "`await` it to get the boolean."]),
    _fx("tsm-w26-f1", "An async forEach",
        "Print each word doubled, then `done`. `done` comes out first.",
        _STDIN + 'const double = async (w: string) => {\n  await null;\n  return w + w;\n};\nasync function main(): Promise<void> {\n  input.split(" ").forEach(async (w) => console.log(await double(w)));\n  console.log("done");\n}\nawait main();\n',
        _STDIN + 'const double = async (w: string) => {\n  await null;\n  return w + w;\n};\nasync function main(): Promise<void> {\n  for (const w of input.split(" ")) console.log(await double(w));\n  console.log("done");\n}\nawait main();\n',
        [("a b", "aa\nbb\ndone"), ("x", "xx\ndone")], strictness=_SI,
        hints=["`forEach` doesn't wait for promises.", "Use `for…of` with `await`."]),
]

TS_CARDS_MORE[26] = [
    ("Sync code, microtasks, timers — in which order do they run?", "The current synchronous code, then every microtask (promise callbacks, `await` continuations, `queueMicrotask`), then the next timer."),
    ("What does `await` do to the rest of an async function?", "Schedules it as a microtask once the awaited promise settles; code before the first `await` runs synchronously."),
    ("How do you cancel in-flight async work?", "Pass an `AbortSignal` from an `AbortController`; the work checks it (`throwIfAborted`) and listens for `abort`. Cancellation is cooperative."),
    ("`AbortSignal.any([a, AbortSignal.timeout(ms)])`?", "A signal that aborts when either the caller cancels or the time runs out."),
    ("How do you consume an async generator?", "`for await (const x of gen())`, or `await Array.fromAsync(gen())` for a finite one."),
    ("How do you make async output deterministic in tests?", "Order results by input index (`Promise.all`), and drive time with a virtual clock rather than real timers."),
]

# ===========================================================================
# Week 27 (optional) — Capstone & mock interview
# ===========================================================================

TS_PROBLEM_SETS[27] = [
    _tsp(27, "tsm-w27-top-words", "Mock interview 1: the k most frequent words", "core",
         "The first input line is k; the rest is text. Count words case-insensitively (a word is a run of letters or apostrophes) and print the k most frequent as `<word> <count>`, most frequent first, ties alphabetical. If there are fewer than k distinct words, print them all. Say your complexity out loud before you code: this should be O(n log n) or better.",
         r"""
const [kText = "0", ...lines] = input.split("\n");
const k = Number(kText);
const counts = new Map<string, number>();
for (const word of lines.join(" ").toLowerCase().match(/[a-z']+/g) ?? []) counts.set(word, (counts.get(word) ?? 0) + 1);
const ranked = [...counts].sort(([a, x], [b, y]) => y - x || a.localeCompare(b)).slice(0, k);
for (const [word, n] of ranked) console.log(`${word} ${n}`);
""", ["2\nthe cat and the hat\nand the bat", "5\nOne fish, two fish.", "1\nb a"],
         hints=["A `Map<string, number>` of counts, then one sort with a tie-break.",
                "For very large inputs and small k, a size-k heap is O(n log k) — mention it even if you sort."]),
    _tsp(27, "tsm-w27-intervals", "Mock interview 2: insert and merge intervals", "core",
         "The first input line is a list of intervals `a-b` (inclusive, possibly overlapping, unsorted); each later line is a new interval to insert. After each insertion print the merged, sorted list as `a-b a-b …` and `covered <total length>` (the number of integer points covered). Type intervals as readonly tuples `readonly [start: number, end: number]` and never mutate the input list.",
         r"""
type Interval = readonly [start: number, end: number];
const parse = (t: string): Interval => {
  const [a = "0", b = "0"] = t.split("-");
  return [Math.min(Number(a), Number(b)), Math.max(Number(a), Number(b))];
};
function merge(intervals: readonly Interval[]): Interval[] {
  const sorted = intervals.toSorted((x, y) => x[0] - y[0] || x[1] - y[1]);
  const out: Interval[] = [];
  for (const cur of sorted) {
    const last = out.at(-1);
    if (last !== undefined && cur[0] <= last[1] + 1) out[out.length - 1] = [last[0], Math.max(last[1], cur[1])];
    else out.push(cur);
  }
  return out;
}
const [first = "", ...inserts] = input.split("\n");
let current: readonly Interval[] = merge(first.trim().split(/\s+/).map(parse));
for (const line of inserts) {
  current = merge([...current, parse(line.trim())]);
  console.log(current.map(([a, b]) => `${a}-${b}`).join(" "));
  console.log(`covered ${current.reduce((s, [a, b]) => s + b - a + 1, 0)}`);
}
""", ["1-3 8-10 5-6\n4-4\n11-20\n0-100", "5-5\n1-2\n3-4"],
         hints=["Sort by start, then extend the last merged interval while the next one overlaps or touches.",
                "Labelled readonly tuples document the shape and stop accidental mutation."]),
    _tsp(27, "tsm-w27-rate-limiter", "Mock interview 3: a sliding-window rate limiter", "core",
         "Design `class RateLimiter` allowing at most `limit` requests per user in any window of `window` ms (a request at time t counts for the window (t - window, t]). The first input line is `limit window`; each later line is `<time> <user>` in non-decreasing time. Print `<time> <user> allowed` or `<time> <user> limited (retry at <t>)` — the earliest time a request would be allowed. Keep each user's timestamps in their own queue.",
         r"""
class RateLimiter {
  readonly #limit: number;
  readonly #window: number;
  readonly #hits = new Map<string, number[]>();
  constructor(limit: number, windowMs: number) {
    this.#limit = limit;
    this.#window = windowMs;
  }
  request(user: string, t: number): { allowed: true } | { allowed: false; retryAt: number } {
    const hits = this.#hits.get(user) ?? [];
    while (hits.length > 0 && (hits[0] ?? 0) <= t - this.#window) hits.shift();
    this.#hits.set(user, hits);
    if (hits.length < this.#limit) {
      hits.push(t);
      return { allowed: true };
    }
    return { allowed: false, retryAt: (hits[0] ?? t) + this.#window };
  }
}
const [config = "", ...lines] = input.split("\n");
const [limit = 1, windowMs = 1000] = config.trim().split(/\s+/).map(Number);
const limiter = new RateLimiter(limit, windowMs);
for (const line of lines) {
  const [time = "0", user = ""] = line.trim().split(/\s+/);
  const r = limiter.request(user, Number(time));
  console.log(r.allowed ? `${time} ${user} allowed` : `${time} ${user} limited (retry at ${r.retryAt})`);
}
""", ["2 1000\n0 ana\n100 ana\n200 ana\n300 bo\n1000 ana\n1050 ana\n1101 ana", "1 10\n5 x\n5 x\n14 x\n15 x"],
         hints=["A queue of timestamps per user; drop the ones that fell out of the window before deciding.",
                "The earliest retry is when the oldest remaining hit leaves the window."]),
    _tsp(27, "tsm-w27-event-sourcing", "Mock interview 4: rebuild state from events", "stretch",
         "An account's history is a stream of events, one per input line: `<time> opened <owner>`, `<time> deposited <n>`, `<time> withdrew <n>`, `<time> renamed <owner>`, `<time> closed`, then queries `at <time>` (the state after every event up to and including that time). Model events as a discriminated union and state as the result of folding them with a pure `apply(state, event)`; an event that is invalid in the current state (a withdrawal beyond the balance, anything after `closed`, anything before `opened`) is skipped with `skipped <time> <kind>`. Print each query as `at <t>: <owner> <balance> <open|closed>` or `at <t>: no account`.",
         r"""
type Event =
  | { kind: "opened"; t: number; owner: string }
  | { kind: "deposited" | "withdrew"; t: number; amount: number }
  | { kind: "renamed"; t: number; owner: string }
  | { kind: "closed"; t: number };
type State = { readonly owner: string; readonly balance: number; readonly open: boolean } | undefined;
function apply(s: State, e: Event): State | "invalid" {
  if (e.kind === "opened") return s === undefined ? { owner: e.owner, balance: 0, open: true } : "invalid";
  if (s === undefined || !s.open) return "invalid";
  switch (e.kind) {
    case "deposited":
      return { ...s, balance: s.balance + e.amount };
    case "withdrew":
      return e.amount > s.balance ? "invalid" : { ...s, balance: s.balance - e.amount };
    case "renamed":
      return { ...s, owner: e.owner };
    case "closed":
      return { ...s, open: false };
  }
}
const events: Event[] = [];
const queries: number[] = [];
for (const line of input.split("\n")) {
  const [a = "", b = "", c = ""] = line.trim().split(/\s+/);
  if (a === "at") {
    queries.push(Number(b));
    continue;
  }
  const t = Number(a);
  if (b === "opened" || b === "renamed") events.push({ kind: b, t, owner: c });
  else if (b === "deposited" || b === "withdrew") events.push({ kind: b, t, amount: Number(c) });
  else if (b === "closed") events.push({ kind: b, t });
}
const timeline: { t: number; state: State }[] = [];
let state: State = undefined;
for (const e of events) {
  const next = apply(state, e);
  if (next === "invalid") {
    console.log(`skipped ${e.t} ${e.kind}`);
    continue;
  }
  state = next;
  timeline.push({ t: e.t, state });
}
for (const q of queries) {
  const s = timeline.filter((x) => x.t <= q).at(-1)?.state;
  console.log(s === undefined ? `at ${q}: no account` : `at ${q}: ${s.owner} ${s.balance} ${s.open ? "open" : "closed"}`);
}
""", ["1 deposited 5\n2 opened ana\n3 deposited 100\n4 withdrew 150\n5 withdrew 30\n6 renamed ana-lee\n7 closed\n8 deposited 1\nat 0\nat 3\nat 5\nat 6\nat 99",
      "10 opened bo\n10 opened cy\nat 10\nat 9"],
         hints=["A pure `apply` returning the next state (or a marker for invalid) makes replay-to-any-time trivial.",
                "Record the state after each accepted event; a query picks the last one at or before its time."]),
    _tsp_types(27, "tsm-w27-deep-partial", "Mock type puzzle 1: DeepPartial", "core",
               "Write `DeepPartial<T>`: every property at every depth becomes optional; arrays keep their shape but their elements become deep-partial; functions are left alone.",
               '''
type DeepPartial<T> = T extends (...args: never[]) => unknown
  ? T
  : T extends readonly (infer E)[]
    ? DeepPartial<E>[]
    : T extends object
      ? { [K in keyof T]?: DeepPartial<T[K]> }
      : T;
''', '''T extends (...args: never[]) => unknown
  ? T
  : T extends readonly (infer E)[]
    ? DeepPartial<E>[]
    : T extends object
      ? { [K in keyof T]?: DeepPartial<T[K]> }
      : T''',
               '''
type Config = { name: string; db: { host: string; ports: number[] }; tags: { id: number; label: string }[]; onLoad: () => void };
type _1 = Expect<Equal<DeepPartial<Config>, {
  name?: string;
  db?: { host?: string; ports?: number[] };
  tags?: { id?: number; label?: string }[];
  onLoad?: () => void;
}>>;
''', hints=["Four cases, in order: functions, arrays, objects, primitives.", "Arrays: recurse into the element type."]),
    _tsp_types(27, "tsm-w27-path-value", "Mock type puzzle 2: the value at a path", "stretch",
               "Write `PathValue<T, P>`: the type found at the dotted path `P` inside `T` (`never` for a path that doesn't exist).",
               '''
type PathValue<T, P extends string> = P extends `${infer Head}.${infer Rest}`
  ? Head extends keyof T
    ? PathValue<T[Head], Rest>
    : never
  : P extends keyof T
    ? T[P]
    : never;
''', '''P extends `${infer Head}.${infer Rest}`
  ? Head extends keyof T
    ? PathValue<T[Head], Rest>
    : never
  : P extends keyof T
    ? T[P]
    : never''',
               '''
type User = { name: string; address: { city: string; geo: { lat: number } }; tags: string[] };
type _1 = Expect<Equal<PathValue<User, "name">, string>>;
type _2 = Expect<Equal<PathValue<User, "address.geo.lat">, number>>;
type _3 = Expect<Equal<PathValue<User, "address.zip">, never>>;
type _4 = Expect<Equal<PathValue<User, "tags">, string[]>>;
''', hints=["Split off the first segment with a template literal pattern and recurse on the rest.",
            "Each segment must be a `keyof` the current type, or the answer is `never`."]),
    _tsp_types(27, "tsm-w27-required-keys", "Mock type puzzle 3: required keys", "core",
               "Write `RequiredKeys<T>`: the union of `T`'s keys that are *not* optional.",
               '''
type RequiredKeys<T> = { [K in keyof T]-?: {} extends Pick<T, K> ? never : K }[keyof T];
''', "{ [K in keyof T]-?: {} extends Pick<T, K> ? never : K }[keyof T]",
               '''
type _1 = Expect<Equal<RequiredKeys<{ id: number; name?: string; email: string | undefined }>, "id" | "email">>;
type _2 = Expect<Equal<RequiredKeys<{ a?: 1 }>, never>>;
''', hints=["`{}` is assignable to `Pick<T, K>` exactly when `K` is optional.", "Map the optional ones to `never`, and don't forget `-?`."]),
    _tsp_types(27, "tsm-w27-awaited-all", "Mock type puzzle 4: the type of Promise.all", "core",
               "Write `AwaitedAll<T>`: for a tuple of values and promises, the tuple of what each resolves to — the result type of `Promise.all` — as a mutable tuple.",
               '''
type AwaitedAll<T extends readonly unknown[]> = { -readonly [K in keyof T]: Awaited<T[K]> };
''', "{ -readonly [K in keyof T]: Awaited<T[K]> }",
               '''
type _1 = Expect<Equal<AwaitedAll<[Promise<number>, string, Promise<Promise<boolean>>]>, [number, string, boolean]>>;
type _2 = Expect<Equal<AwaitedAll<readonly [Promise<"a">]>, ["a"]>>;
type _3 = Expect<Equal<AwaitedAll<[]>, []>>;
''', hints=["A mapped type over a tuple produces a tuple.", "`Awaited` unwraps nested promises; `-readonly` drops the modifier."]),
]

TS_PROJECTS[27] = _project(
    27, "ledger.ts — the arc's final version",
    "The six-month arc project, finished: a ledger that loads its sources concurrently with a timeout, parses every row into branded types with `Result`s, keeps its state private in a class, streams statements lazily with a generator, and never lets timing decide what it prints.",
    ["The input has three sections separated by `---` lines: config (`timeout=<ms>`), sources (`<name> <delayMs> <row;row;…>` with rows `YYYY-MM-DD,ACC-123,amount`), and commands.",
     "Load every source concurrently on a virtual clock: a source finishes after its delay, or times out at the timeout (a delay equal to the timeout still loads). Parse each loaded row with `Result`s — `bad date`, `bad account` (three capitals, `-`, three digits), `bad amount` (at most two decimals) — recording errors as `<source>#<row>: <problem>`; add good rows to the ledger in source input order.",
     "Commands: `sources` (`<name>: <k> rows` — `row` for one — or `<name>: timed out`, in input order); `balance <acc>`; `statement <acc> [n]` (the first n lines — all by default — of `<date> <signed amount> <running balance>` in date order, produced by a generator); `top <n>` (accounts by balance, highest first, ties by id); `months` (`<YYYY-MM> in <x> out <y>`, sorted); `errors` (in load order, or `no errors`).",
     "Money prints as `$12.00` / `-$3.50`; a bad account id in a command prints `bad account <x>`, and an unknown one `no account <x>`.",
     "Use a branded `AccountId` and `Cents`, a `Ledger` class with `#private` transactions, and `Result<T, string>` for every parser."],
    _VCLOCK + r"""
declare const AccountBrand: unique symbol;
declare const CentsBrand: unique symbol;
type AccountId = string & { readonly [AccountBrand]: true };
type Cents = number & { readonly [CentsBrand]: true };
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
type Tx = { readonly date: string; readonly account: AccountId; readonly amount: Cents };
const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
const err = (error: string): Result<never> => ({ ok: false, error });
const parseAccount = (s: string): Result<AccountId> => (/^[A-Z]{3}-\d{3}$/.test(s) ? ok(s as AccountId) : err("bad account"));
function parseCents(s: string): Result<Cents> {
  const m = /^(-?)(\d+)(?:\.(\d{1,2}))?$/.exec(s);
  if (m === null) return err("bad amount");
  const cents = Number(m[2] ?? "0") * 100 + Number((m[3] ?? "").padEnd(2, "0"));
  return ok((m[1] === "-" ? -cents : cents) as Cents);
}
function parseDate(s: string): Result<string> {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
  if (m === null) return err("bad date");
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const date = new Date(Date.UTC(y, mo - 1, d));
  return date.getUTCMonth() === mo - 1 && date.getUTCDate() === d ? ok(s) : err("bad date");
}
function parseTx(row: string): Result<Tx> {
  const [d = "", a = "", amt = ""] = row.split(",").map((x) => x.trim());
  const date = parseDate(d);
  if (!date.ok) return date;
  const account = parseAccount(a);
  if (!account.ok) return account;
  const amount = parseCents(amt);
  if (!amount.ok) return amount;
  return ok({ date: date.value, account: account.value, amount: amount.value });
}
const money = (c: number) => (c < 0 ? "-" : "") + "$" + (Math.abs(c) / 100).toFixed(2);

class Ledger {
  readonly #txs: Tx[] = [];
  add(tx: Tx): void {
    this.#txs.push(tx);
  }
  has(acc: AccountId): boolean {
    return this.#txs.some((t) => t.account === acc);
  }
  balance(acc: AccountId): number {
    return this.#txs.reduce((s, t) => s + (t.account === acc ? t.amount : 0), 0);
  }
  *statement(acc: AccountId): Generator<string> {
    let running = 0;
    for (const t of this.#txs.filter((x) => x.account === acc).toSorted((a, b) => a.date.localeCompare(b.date))) {
      running += t.amount;
      yield `${t.date} ${t.amount >= 0 ? "+" : ""}${money(t.amount)} ${money(running)}`;
    }
  }
  accounts(): AccountId[] {
    return [...new Set(this.#txs.map((t) => t.account))];
  }
  months(): [string, { in: number; out: number }][] {
    const m = new Map<string, { in: number; out: number }>();
    for (const t of this.#txs) {
      const key = t.date.slice(0, 7);
      const cur = m.get(key) ?? { in: 0, out: 0 };
      m.set(key, t.amount >= 0 ? { ...cur, in: cur.in + t.amount } : { ...cur, out: cur.out - t.amount });
    }
    return [...m].sort(([a], [b]) => a.localeCompare(b));
  }
}

const sections: string[][] = [[]];
for (const line of input.split("\n")) {
  if (line.trim() === "---") sections.push([]);
  else if (line.trim() !== "") sections.at(-1)?.push(line.trim());
}
const [configLines = [], sourceLines = [], commands = []] = sections;
const timeout = Number((configLines[0] ?? "timeout=100").split("=")[1] ?? "100");
const sources = sourceLines.map((line) => {
  const [name = "", delay = "0", rows = ""] = line.split(/\s+/);
  return { name, delay: Number(delay), rows: rows.split(";").filter((r) => r !== "") };
});

async function loadSource(delay: number, rows: string[]): Promise<string[] | undefined> {
  const work = new AbortController();
  const timer = new AbortController();
  const loaded = clock.sleep(delay, work.signal).then(() => {
    timer.abort();
    return rows;
  }, () => undefined);
  const timedOut = clock.sleep(timeout, timer.signal).then(() => {
    work.abort();
    return undefined;
  }, () => undefined);
  return Promise.race([loaded, timedOut]);
}

const ledger = new Ledger();
const errors: string[] = [];
const loaded: (string[] | undefined)[] = [];
const done = Promise.all(sources.map((s) => loadSource(s.delay, s.rows))).then((results) => {
  results.forEach((rows, i) => {
    loaded.push(rows);
    const name = sources[i]?.name ?? "?";
    (rows ?? []).forEach((row, r) => {
      const tx = parseTx(row);
      if (tx.ok) ledger.add(tx.value);
      else errors.push(`${name}#${r + 1}: ${tx.error}`);
    });
  });
});
await clock.run();
await done;

for (const command of commands) {
  const [cmd = "", arg = "", n = ""] = command.split(/\s+/);
  const account = (): AccountId | undefined => {
    const r = parseAccount(arg);
    if (!r.ok) console.log(`bad account ${arg}`);
    else if (!ledger.has(r.value)) console.log(`no account ${arg}`);
    else return r.value;
    return undefined;
  };
  if (cmd === "sources") {
    sources.forEach((s, i) => {
      const rows = loaded[i];
      console.log(rows === undefined ? `${s.name}: timed out` : `${s.name}: ${rows.length} ${rows.length === 1 ? "row" : "rows"}`);
    });
  } else if (cmd === "balance") {
    const acc = account();
    if (acc !== undefined) console.log(`${acc}: ${money(ledger.balance(acc))}`);
  } else if (cmd === "statement") {
    const acc = account();
    if (acc !== undefined) {
      const lines = n === "" ? ledger.statement(acc).toArray() : ledger.statement(acc).take(Number(n)).toArray();
      for (const l of lines) console.log(l);
    }
  } else if (cmd === "top") {
    const ranked = ledger.accounts().sort((a, b) => ledger.balance(b) - ledger.balance(a) || a.localeCompare(b));
    for (const a of ranked.slice(0, Number(arg))) console.log(`${a} ${money(ledger.balance(a))}`);
  } else if (cmd === "months") {
    for (const [m, v] of ledger.months()) console.log(`${m} in ${money(v.in)} out ${money(v.out)}`);
  } else if (cmd === "errors") {
    if (errors.length === 0) console.log("no errors");
    for (const e of errors) console.log(e);
  }
}
""", ["timeout=50\n---\nbank 20 2026-01-05,CHK-001,2500;2026-01-09,CHK-001,-45.50;2026-02-01,SAV-002,500\ncards 40 2026-01-20,CHK-001,-120;2026-01-31,CRD-003,-60.25\nlate 90 2026-03-01,CHK-001,1\n---\nsources\nbalance CHK-001\nstatement CHK-001\ntop 2\nmonths\nerrors",
      "timeout=30\n---\na 30 2026-02-30,ABC-111,5;2026-01-01,abc-111,5;2026-01-02,ABC-111,5.555;2026-01-03,ABC-111,-7\nb 31 2026-01-01,XYZ-999,1\n---\nsources\nerrors\nbalance ABC-111\nbalance XYZ-999\nbalance nope",
      "timeout=100\n---\nonly 0 2026-05-01,ACC-001,10;2026-04-01,ACC-001,-4;2026-06-01,ACC-001,1\n---\nstatement ACC-001 2\nstatement ACC-001\nmonths\ntop 5",
      "timeout=10\n---\nslow 11 2026-01-01,AAA-000,1\n---\nsources\ntop 3\nerrors\nstatement AAA-000",
      "timeout=5\n---\nx 1 2024-02-29,LEP-029,29.02;2023-02-28,LEP-029,-0.02\ny 2 2024-02-29,LEP-030,1\n---\ntop 2\nstatement LEP-029 1\nmonths\nsources"],
    rubric=["Every parser returns a `Result`; nothing in the parsing path throws",
            "Branded `AccountId`/`Cents` are created only by their parsers",
            "The ledger's transactions are `#private`; callers can read, never write",
            "No output depends on real time — only on the virtual clock",
            "No `any` anywhere; every function has a typed signature"],
    stretch=["Split it into modules (`money.ts`, `parse.ts`, `ledger.ts`, `load.ts`, `main.ts`) with `import type` where it applies.",
             "Add `using`-managed resources for the sources and print when each is released."],
)

TS_PRACTICE_MORE[27] = [
    _fx("tsm-w27-f1", "Code review: a sort that edits the caller's data",
        "Print the top score, then the scores in their original order. The original order comes out sorted.",
        _STDIN + 'const scores = input.split(" ").map(Number);\nfunction top(xs: number[]): number {\n  return xs.sort((a, b) => b - a)[0] ?? 0;\n}\nconsole.log(top(scores));\nconsole.log(scores.join(" "));\n',
        _STDIN + 'const scores = input.split(" ").map(Number);\nfunction top(xs: readonly number[]): number {\n  return xs.toSorted((a, b) => b - a)[0] ?? 0;\n}\nconsole.log(top(scores));\nconsole.log(scores.join(" "));\n',
        [("3 9 4", "9\n3 9 4"), ("5", "5\n5")], strictness=_SI,
        hints=["`sort` sorts in place — the review comment is \"this mutates its argument\".", "Take `readonly number[]` and use `toSorted`."]),
    _fx("tsm-w27-f2", "Code review: money in floating point",
        "Print the total of the prices, to two decimals, and whether it equals the expected total on the first line. Totals that should match don't.",
        _STDIN + 'const [expected = "0", ...prices] = input.split(" ");\nconst total = prices.map(Number).reduce((a, b) => a + b, 0);\nconsole.log(total.toFixed(2), total === Number(expected));\n',
        _STDIN + 'const [expected = "0", ...prices] = input.split(" ");\nconst cents = (s: string) => Math.round(Number(s) * 100);\nconst total = prices.map(cents).reduce((a, b) => a + b, 0);\nconsole.log((total / 100).toFixed(2), total === cents(expected));\n',
        [("0.3 0.1 0.2", "0.30 true"), ("1.15 0.5 0.65", "1.15 true")], strictness=_SI,
        hints=["`0.1 + 0.2 !== 0.3` in floating point.", "Compare integer cents."], difficulty="Medium"),
    _fx("tsm-w27-f3", "Code review: `||` where `??` was meant",
        "Print each item's quantity, defaulting to 1 only when no quantity was given (`-`). A quantity of 0 becomes 1.",
        _STDIN + 'const qty = input.split(" ").map((t) => (t === "-" ? undefined : Number(t)));\nconsole.log(qty.map((q) => q || 1).join(" "));\n',
        _STDIN + 'const qty = input.split(" ").map((t) => (t === "-" ? undefined : Number(t)));\nconsole.log(qty.map((q) => q ?? 1).join(" "));\n',
        [("3 - 0", "3 1 0"), ("0", "0")], strictness=_SI,
        hints=["`||` replaces every falsy value, including `0`.", "`??` replaces only `null` and `undefined`."]),
    _dx("tsm-w27-d1", "Code review: an `any` that hid a bug",
        "error TS2339: Property 'toUpperCase' does not exist on type 'string | number'.",
        _STDIN + 'function label(value: string | number): string {\n  return value.toUpperCase();\n}\nconsole.log(input.split(" ").map((t) => label(/^\\d+$/.test(t) ? Number(t) : t)).join(" "));\n',
        _STDIN + 'function label(value: string | number): string {\n  return typeof value === "number" ? `#${value}` : value.toUpperCase();\n}\nconsole.log(input.split(" ").map((t) => label(/^\\d+$/.test(t) ? Number(t) : t)).join(" "));\n',
        [("ab 12 cd", "AB #12 CD"), ("7", "#7")], strictness=_SI,
        ask="Numbers should print as `#<n>`, words upper-cased. (The original code typed `value` as `any`, and this crashed in production.)",
        hints=["Narrow the union before calling a string method.", "`typeof value === \"number\"`."], difficulty="Medium"),
]

TS_CARDS_MORE[27] = [
    ("Mock interview: how do you open a coding question?", "Restate it, confirm the input/output shapes and edge cases, state a brute force and its complexity, then improve."),
    ("Mock interview: `interface` or `type`?", "Interchangeable for object shapes; `interface` merges and extends cheaply, `type` handles unions, mapped and conditional types. Pick one convention and say why."),
    ("Mock interview: how do you type untrusted JSON?", "Parse to `unknown`, validate at the boundary with a guard or schema, and let the inferred type flow inward — never `as T`."),
    ("Mock interview: what is structural typing's biggest surprise?", "Extra properties pass silently (except fresh literals), so types never guarantee a value has *only* what they list."),
    ("Mock interview: how do you make async output testable?", "Inject the clock and the I/O, order results by input index, and never assert on real timing."),
    ("Mock interview: when would you reach for a branded type?", "When two values share a representation but must never be mixed — ids, units, validated strings — at zero runtime cost."),
]
