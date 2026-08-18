# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Learn track — expansion pass.
#
# exec()'d inside gen_seed.py AFTER typescript_defs.py (so `tsx`, `tsc`, `_P`
# and the CONCEPTS/CATEGORY/LESSONS/EXERCISES dicts already exist). It does two
# things:
#
#   1. Adds ONE self-contained *coding challenge* (kind="challenge") to every
#      foundational TypeScript concept, so each lesson pairs its short
#      fill-in-the-blank drills with a fuller problem. Each challenge is scoped
#      to what the syllabus has taught up to that point, and tagged with a
#      difficulty (Intro -> Easy -> Medium as the track progresses).
#
#   2. Adds two new foundational concepts — Numbers & Math, String Methods —
#      that a beginner curriculum needs, each with drills + a challenge.
#
# EXECUTION MODEL (same constraints as typescript_defs.py): drills/challenges
# run through the real stdin/stdout judge via `node --experimental-strip-types`.
# Types are erased at runtime, so every graded blank targets runtime code.
# Every `solution` here is proven end-to-end by tests/verify_exercises.rs.
# ---------------------------------------------------------------------------

# Standard scaffold: read all of stdin (trimmed) into `input`. The challenge
# body does its own parsing from `input` (one line, or split on "\n").
_SCAF = 'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8").trim();\n'


def _chal(eid, title, diff, prompt, body, tests, hint=""):
    """Build a coding challenge whose starter is the scaffold + a single `____`
    where the learner writes the whole solution `body`."""
    body = body.strip("\n")
    full = _P(_SCAF + body)
    return tsc(eid, title, diff, prompt, full, body, tests, hint)


def _add_challenge(concept_key, challenge):
    """Append a challenge to a concept's exercise list (after its drills)."""
    EXERCISES.setdefault(concept_key, []).append(challenge)


# ===========================================================================
# 1) CODING CHALLENGES — one per existing foundational concept.
#    Ordered to mirror the syllabus so "what is taught so far" holds.
# ===========================================================================

# -- TS: Language Basics (Intro) -------------------------------------------
_add_challenge("ts_variables", _chal(
    "ts_variables-challenge", "Two-number report", "Intro",
    "The input is two numbers `a b` on one line. Using `const`/`let` and arithmetic, print three lines: their sum, their difference (`a - b`), and their product.",
    r'''
const [a, b] = input.split(/\s+/).map(Number);
const sum = a + b;
const diff = a - b;
const product = a * b;
console.log(sum);
console.log(diff);
console.log(product);
''',
    [("3 4", "7\n-1\n12"), ("10 5", "15\n5\n50"),
     ("-2 -3", "-5\n1\n6"), ("0 0", "0\n0\n0")],
    hint="Read the two numbers, then compute and log each result on its own line.",
))

_add_challenge("ts_types", _chal(
    "ts_types-challenge", "Coin counter", "Intro",
    "The input is four counts `quarters dimes nickels pennies`. Compute the total value in cents (25/10/5/1), then in dollars (cents / 100). Print the cents on line 1 and the dollars on line 2.",
    r'''
const [q, d, n, p] = input.split(/\s+/).map(Number);
const cents: number = q * 25 + d * 10 + n * 5 + p;
const dollars: number = cents / 100;
console.log(cents);
console.log(dollars);
''',
    [("1 0 0 0", "25\n0.25"), ("0 0 0 0", "0\n0"),
     ("3 2 1 4", "104\n1.04"), ("4 0 0 0", "100\n1")],
    hint="cents is an integer; dividing by 100 gives a decimal `number` like 0.25.",
))

_add_challenge("ts_inference", _chal(
    "ts_inference-challenge", "Min, max, range", "Intro",
    "The input is a line of numbers. Let TypeScript infer the types. Print the smallest on line 1, the largest on line 2, and the range (largest − smallest) on line 3.",
    r'''
const nums = input.split(/\s+/).map(Number);
const lo = Math.min(...nums);
const hi = Math.max(...nums);
console.log(lo);
console.log(hi);
console.log(hi - lo);
''',
    [("3 1 4 1 5", "1\n5\n4"), ("7", "7\n7\n0"),
     ("-2 -5 -1", "-5\n-1\n4"), ("10 10", "10\n10\n0")],
    hint="Math.min(...nums) and Math.max(...nums) spread the array as arguments.",
))

_add_challenge("ts_strings", _chal(
    "ts_strings-challenge", "Initials", "Intro",
    "The input is a name of one or more words. Print the uppercase initials joined together — `grace hopper` → `GH`.",
    r'''
const words = input.split(/\s+/);
const initials = words.map(w => w[0].toUpperCase()).join("");
console.log(initials);
''',
    [("grace hopper", "GH"), ("ada", "A"),
     ("the quick brown fox", "TQBF"), ("john von neumann", "JVN")],
    hint="Split on spaces, take w[0] of each word, uppercase it, then join with \"\".",
))

_add_challenge("ts_operators", _chal(
    "ts_operators-challenge", "Operator trio", "Intro",
    "The input is two numbers `a b`. Print three lines: the remainder `a % b`, whether `a === b` (a boolean), and whether `a > b` (a boolean).",
    r'''
const [a, b] = input.split(/\s+/).map(Number);
console.log(a % b);
console.log(a === b);
console.log(a > b);
''',
    [("7 2", "1\nfalse\ntrue"), ("4 4", "0\ntrue\nfalse"),
     ("3 10", "3\nfalse\nfalse"), ("9 3", "0\nfalse\ntrue")],
    hint="A comparison like a === b evaluates to true or false — log it directly.",
))

_add_challenge("ts_conditionals", _chal(
    "ts_conditionals-challenge", "Letter grade", "Intro",
    "The input is a single score (0–100). Print its letter grade with an if/else ladder: 90+ → A, 80+ → B, 70+ → C, 60+ → D, otherwise F.",
    r'''
const score = Number(input);
let grade: string;
if (score >= 90) grade = "A";
else if (score >= 80) grade = "B";
else if (score >= 70) grade = "C";
else if (score >= 60) grade = "D";
else grade = "F";
console.log(grade);
''',
    [("95", "A"), ("82", "B"), ("70", "C"), ("60", "D"), ("40", "F")],
    hint="Check the highest threshold first; each `else if` handles the next band down.",
))

_add_challenge("ts_loops", _chal(
    "ts_loops-challenge", "FizzBuzz", "Intro",
    "The input is a number `n`. Print the numbers 1..n one per line, but print `Fizz` for multiples of 3, `Buzz` for multiples of 5, and `FizzBuzz` for multiples of both.",
    r'''
const n = Number(input);
for (let i = 1; i <= n; i++) {
  if (i % 15 === 0) console.log("FizzBuzz");
  else if (i % 3 === 0) console.log("Fizz");
  else if (i % 5 === 0) console.log("Buzz");
  else console.log(i);
}
''',
    [("5", "1\n2\nFizz\n4\nBuzz"), ("3", "1\n2\nFizz"), ("1", "1"),
     ("15", "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz")],
    hint="Test the both-case (i % 15 === 0) first, or 15 prints Fizz instead of FizzBuzz.",
))

_add_challenge("ts_destructuring", _chal(
    "ts_destructuring-challenge", "Path length", "Easy",
    "The input is a flat list of coordinates `x1 y1 x2 y2 …` describing a path. Walk consecutive points and sum the Manhattan distance (|dx| + |dy|) of each step. Print the total path length.",
    r'''
const nums = input.split(/\s+/).map(Number);
let total = 0;
for (let i = 2; i < nums.length; i += 2) {
  const [px, py, x, y] = [nums[i - 2], nums[i - 1], nums[i], nums[i + 1]];
  total += Math.abs(x - px) + Math.abs(y - py);
}
console.log(total);
''',
    [("0 0 3 4", "7"), ("0 0 1 0 1 1", "2"),
     ("0 0 0 0", "0"), ("0 0 -3 0 -3 -4", "7")],
    hint="Destructure each pair of points, add |x−px| + |y−py| to a running total.",
))

# -- TS: Functions & Types (Easy) ------------------------------------------
_add_challenge("ts_functions", _chal(
    "ts_functions-challenge", "Count primes", "Easy",
    "The input is a number `n`. Write an `isPrime` helper function, then count how many integers in 2..n are prime and print the count.",
    r'''
const n = Number(input);
function isPrime(x: number): boolean {
  if (x < 2) return false;
  for (let d = 2; d * d <= x; d++) if (x % d === 0) return false;
  return true;
}
let count = 0;
for (let i = 2; i <= n; i++) if (isPrime(i)) count++;
console.log(count);
''',
    [("10", "4"), ("1", "0"), ("2", "1"), ("20", "8"), ("0", "0")],
    hint="isPrime(x): false below 2, otherwise no divisor d with d*d <= x divides it.",
))

_add_challenge("ts_params", _chal(
    "ts_params-challenge", "Clamp to a range", "Easy",
    "The input is a line of numbers. Write a `clamp(x, lo = 0, hi = 100)` using default parameters, apply it to every number, and print the clamped values space-separated.",
    r'''
const nums = input.split(/\s+/).map(Number);
function clamp(x: number, lo: number = 0, hi: number = 100): number {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}
console.log(nums.map(x => clamp(x)).join(" "));
''',
    [("50 -5 150 100", "50 0 100 100"), ("0", "0"),
     ("-1 -2 -3", "0 0 0"), ("200 99", "100 99")],
    hint="Call clamp(x) with just one argument — the defaults supply lo and hi.",
))

_add_challenge("ts_unions", _chal(
    "ts_unions-challenge", "Robot walk", "Easy",
    "The input is a string of moves drawn from the union `\"N\" | \"S\" | \"E\" | \"W\"`. Start at (0, 0); N/S change y by +1/−1 and E/W change x by +1/−1. Print the final position as `x y`.",
    r'''
type Dir = "N" | "S" | "E" | "W";
function delta(d: Dir): [number, number] {
  if (d === "N") return [0, 1];
  if (d === "S") return [0, -1];
  if (d === "E") return [1, 0];
  return [-1, 0];
}
let x = 0, y = 0;
for (const ch of input.split("")) {
  const [dx, dy] = delta(ch as Dir);
  x += dx;
  y += dy;
}
console.log(x + " " + y);
''',
    [("N", "0 1"), ("NNEE", "2 2"), ("NSEW", "0 0"), ("EEESSS", "3 -3")],
    hint="Map each direction letter to a (dx, dy) step, then accumulate x and y.",
))

_add_challenge("ts_aliases", _chal(
    "ts_aliases-challenge", "Rectangle areas", "Easy",
    "Each input line is `w h` for one rectangle. Define an interface `Rect`, build a typed array of them, print each area on its own line, then a final line `total <sum-of-areas>`.",
    r'''
interface Rect { w: number; h: number; }
const rects: Rect[] = input.split("\n").map(line => {
  const [w, h] = line.trim().split(/\s+/).map(Number);
  return { w, h };
});
let total = 0;
for (const r of rects) {
  const area = r.w * r.h;
  total += area;
  console.log(area);
}
console.log("total " + total);
''',
    [("3 4", "12\ntotal 12"), ("2 2\n5 5", "4\n25\ntotal 29"),
     ("1 1\n1 1\n1 1", "1\n1\n1\ntotal 3"), ("10 2", "20\ntotal 20")],
    hint="Parse each line into a { w, h } object, then loop to print areas and sum them.",
))

_add_challenge("ts_narrowing", _chal(
    "ts_narrowing-challenge", "Numbers vs words", "Easy",
    "The input is a line of space-separated tokens, mixing numbers and words. Sum the tokens that are numeric and count the ones that are not. Print `<sum> <wordCount>`.",
    r'''
const tokens = input.split(/\s+/);
let sum = 0;
let words = 0;
for (const t of tokens) {
  if (t === "") continue;
  const n = Number(t);
  if (!Number.isNaN(n)) sum += n;
  else words++;
}
console.log(sum + " " + words);
''',
    [("1 cat 2 dog 3", "6 2"), ("hello world", "0 2"),
     ("10 20 30", "60 0"), ("5 5 5 x", "15 1")],
    hint="Number(t) is NaN for a non-numeric token — that check narrows it to a word.",
))

# -- TS: Data Structures (Easy) --------------------------------------------
_add_challenge("ts_arrays", _chal(
    "ts_arrays-challenge", "Rotate right by k", "Easy",
    "Line 1 is a list of numbers; line 2 is `k`. Rotate the array right by k positions (wrap around) and print it space-separated. `1 2 3 4 5` with k=2 → `4 5 1 2 3`.",
    r'''
const lines = input.split("\n");
const arr = lines[0].trim().split(/\s+/).map(Number);
const k = Number(lines[1]) % arr.length;
const rotated = [...arr.slice(arr.length - k), ...arr.slice(0, arr.length - k)];
console.log(rotated.join(" "));
''',
    [("1 2 3 4 5\n2", "4 5 1 2 3"), ("1 2 3\n0", "1 2 3"),
     ("1 2 3\n3", "1 2 3"), ("1 2\n1", "2 1")],
    hint="Take the last k with slice(len-k), then the rest, and spread them into one array.",
))

_add_challenge("ts_array_methods", _chal(
    "ts_array_methods-challenge", "Number stats", "Easy",
    "The input is a line of numbers. Using array methods (no manual index loops), print the sum on line 1, the count of even numbers on line 2, and the maximum on line 3.",
    r'''
const nums = input.split(/\s+/).map(Number);
const sum = nums.reduce((a, x) => a + x, 0);
const evens = nums.filter(x => x % 2 === 0).length;
const max = nums.reduce((m, x) => (x > m ? x : m), nums[0]);
console.log(sum);
console.log(evens);
console.log(max);
''',
    [("1 2 3 4 5", "15\n2\n5"), ("2 4 6", "12\n3\n6"),
     ("-1 -2 -3", "-6\n1\n-1"), ("7", "7\n0\n7")],
    hint="reduce folds to the sum/max; filter(...).length counts the evens.",
))

_add_challenge("ts_objects", _chal(
    "ts_objects-challenge", "Most common word", "Easy",
    "The input is a line of words. Count them using an object with an index signature, then print the most frequent word and its count as `<word> <count>` (on a tie, the word that reached the top count first).",
    r'''
const words = input.split(/\s+/).filter(w => w !== "");
const counts: { [w: string]: number } = {};
for (const w of words) counts[w] = (counts[w] ?? 0) + 1;
let best = words[0];
let bestCount = 0;
for (const w of words) {
  if (counts[w] > bestCount) {
    best = w;
    bestCount = counts[w];
  }
}
console.log(best + " " + bestCount);
''',
    [("a b a c a", "a 3"), ("x y y", "y 2"),
     ("one", "one 1"), ("cat dog cat dog", "cat 2")],
    hint="Tally into counts[w], then scan the words keeping the first that beats the max.",
))

_add_challenge("ts_maps_sets", _chal(
    "ts_maps_sets-challenge", "First unique number", "Easy",
    "The input is a line of numbers. Using a Map to count occurrences, print the first number that appears exactly once. If every number repeats, print `none`.",
    r'''
const nums = input.split(/\s+/).map(Number);
const freq = new Map<number, number>();
for (const n of nums) freq.set(n, (freq.get(n) ?? 0) + 1);
let ans = "none";
for (const n of nums) {
  if (freq.get(n) === 1) {
    ans = String(n);
    break;
  }
}
console.log(ans);
''',
    [("1 2 2 3 3", "1"), ("4 4 5", "5"), ("1 1 2 2", "none"), ("9", "9")],
    hint="Count first, then scan in original order for the first value with count === 1.",
))

_add_challenge("ts_enums", _chal(
    "ts_enums-challenge", "Compass turns", "Easy",
    "Start facing `N`. The input is a string of turns: `R` turns clockwise (N→E→S→W), `L` turns counter-clockwise. Print the final direction. Model directions with a literal-union array.",
    r'''
type Dir = "N" | "E" | "S" | "W";
const order: Dir[] = ["N", "E", "S", "W"];
let idx = 0;
for (const t of input.split("")) {
  if (t === "R") idx = (idx + 1) % 4;
  else if (t === "L") idx = (idx + 3) % 4;
}
console.log(order[idx]);
''',
    [("R", "E"), ("RR", "S"), ("L", "W"), ("RRRR", "N"), ("RRL", "E")],
    hint="Index into [\"N\",\"E\",\"S\",\"W\"]; R is +1 mod 4, L is +3 mod 4 (same as −1).",
))

# -- TS: Composition & Reuse (Medium) --------------------------------------
_add_challenge("ts_generics", _chal(
    "ts_generics-challenge", "Generic de-duplicate", "Medium",
    "Write a generic `unique<T>(arr: T[]): T[]` that keeps the first occurrence of each value in order. Apply it to the input tokens; print the unique tokens space-separated on line 1 and how many there are on line 2.",
    r'''
function unique<T>(arr: T[]): T[] {
  const out: T[] = [];
  const seen = new Set<T>();
  for (const x of arr) {
    if (!seen.has(x)) {
      seen.add(x);
      out.push(x);
    }
  }
  return out;
}
const toks = input.split(/\s+/).filter(t => t !== "");
const u = unique(toks);
console.log(u.join(" "));
console.log(u.length);
''',
    [("a b a c b", "a b c\n3"), ("1 1 1", "1\n1"),
     ("x y z", "x y z\n3"), ("dog cat dog", "dog cat\n2")],
    hint="Track seen values in a Set<T>; push only the first time you see each one.",
))

_add_challenge("ts_classes", _chal(
    "ts_classes-challenge", "Bank account", "Medium",
    "Line 1 is a starting balance. Each later line is `deposit <n>` or `withdraw <n>`. Model an `Account` class; a withdrawal larger than the balance is rejected (counted, not applied). Print `<finalBalance> <rejectedCount>`.",
    r'''
class Account {
  private balance: number;
  private rejected: number;
  constructor(start: number) {
    this.balance = start;
    this.rejected = 0;
  }
  deposit(amount: number): void { this.balance += amount; }
  withdraw(amount: number): void {
    if (amount > this.balance) this.rejected++;
    else this.balance -= amount;
  }
  report(): string { return this.balance + " " + this.rejected; }
}
const lines = input.split("\n");
const acc = new Account(Number(lines[0]));
for (let i = 1; i < lines.length; i++) {
  const [op, amt] = lines[i].trim().split(/\s+/);
  if (op === "deposit") acc.deposit(Number(amt));
  else if (op === "withdraw") acc.withdraw(Number(amt));
}
console.log(acc.report());
''',
    [("100\ndeposit 50\nwithdraw 30", "120 0"), ("100\nwithdraw 200", "100 1"),
     ("0\ndeposit 10\nwithdraw 5\nwithdraw 100", "5 1"), ("50", "50 0")],
    hint="Keep balance and a rejected counter as private fields; guard withdraw before subtracting.",
))

_add_challenge("ts_this_accessors", _chal(
    "ts_this_accessors-challenge", "Celsius to Fahrenheit", "Medium",
    "The input is a line of Celsius temperatures. Build a `Temp` class with a `fahrenheit` getter (c × 9 / 5 + 32) and print each temperature's Fahrenheit value space-separated.",
    r'''
class Temp {
  celsius: number;
  constructor(c: number) { this.celsius = c; }
  get fahrenheit(): number { return this.celsius * 9 / 5 + 32; }
}
const out = input.split(/\s+/).map(s => {
  const t = new Temp(Number(s));
  return t.fahrenheit;
});
console.log(out.join(" "));
''',
    [("0", "32"), ("100", "212"), ("37", "98.6"), ("-40", "-40")],
    hint="A getter is read like a property: t.fahrenheit (no parentheses).",
))

_add_challenge("ts_modules", _chal(
    "ts_modules-challenge", "Exported geometry helpers", "Easy",
    "The input is `w h`. Declare and `export` two functions — `area(w, h)` and `perimeter(w, h)` — then use them to print the rectangle's area on line 1 and perimeter on line 2.",
    r'''
export function area(w: number, h: number): number { return w * h; }
export function perimeter(w: number, h: number): number { return 2 * (w + h); }
const [w, h] = input.split(/\s+/).map(Number);
console.log(area(w, h));
console.log(perimeter(w, h));
''',
    [("3 4", "12\n14"), ("5 5", "25\n20"), ("1 1", "1\n4"), ("10 2", "20\n24")],
    hint="`export function` publishes a function; here you both export and call them in one file.",
))

# -- TS: Robustness (Medium) -----------------------------------------------
_add_challenge("ts_nullish", _chal(
    "ts_nullish-challenge", "Resolve config", "Medium",
    "Each input line is `key value` for one of `host`, `port`, `mode` (any may be missing). Read them into a Map, then print `<host> <port> <mode>`, supplying defaults `localhost` / `8080` / `prod` with `??` when a key is absent.",
    r'''
const map = new Map<string, string>();
for (const line of input.split("\n")) {
  const [k, v] = line.trim().split(/\s+/);
  if (k) map.set(k, v);
}
const host = map.get("host") ?? "localhost";
const port = map.get("port") ?? "8080";
const mode = map.get("mode") ?? "prod";
console.log(host + " " + port + " " + mode);
''',
    [("host example.com", "example.com 8080 prod"),
     ("port 3000\nmode dev", "localhost 3000 dev"),
     ("", "localhost 8080 prod"),
     ("host a\nport 1\nmode b", "a 1 b")],
    hint="map.get(k) is undefined when the key is missing — `?? default` fills it in.",
))

_add_challenge("ts_errors", _chal(
    "ts_errors-challenge", "Safe sum", "Medium",
    "The input is a line of tokens. Write a `toNumber` that throws on a non-numeric token. In a try/catch, sum the valid numbers and count the failures. Print `<sum> <failures>`.",
    r'''
function toNumber(s: string): number {
  const n = Number(s);
  if (Number.isNaN(n)) throw new Error("bad number: " + s);
  return n;
}
let sum = 0;
let failures = 0;
for (const t of input.split(/\s+/)) {
  if (t === "") continue;
  try {
    sum += toNumber(t);
  } catch (e) {
    failures++;
  }
}
console.log(sum + " " + failures);
''',
    [("1 2 x 3", "6 1"), ("a b c", "0 3"), ("10 20", "30 0"), ("5 ? 5 !", "10 2")],
    hint="Wrap each toNumber call in try/catch; the catch branch just increments failures.",
))

_add_challenge("ts_utility_types", _chal(
    "ts_utility_types-challenge", "Apply patches", "Medium",
    "Line 1 is a base user `name age`. Each later line is a patch `name <value>` or `age <value>`. Apply them in order using a `Partial<User>` and spread, then print the final `name age`.",
    r'''
interface User { name: string; age: number; }
const lines = input.split("\n");
const [name0, age0] = lines[0].trim().split(/\s+/);
let user: User = { name: name0, age: Number(age0) };
for (let i = 1; i < lines.length; i++) {
  const [field, value] = lines[i].trim().split(/\s+/);
  const patch: Partial<User> = field === "age"
    ? { age: Number(value) }
    : { name: value };
  user = { ...user, ...patch };
}
console.log(user.name + " " + user.age);
''',
    [("Ada 36", "Ada 36"), ("Ada 36\nage 40", "Ada 40"),
     ("Ada 36\nname Bob\nage 41", "Bob 41"), ("X 1\nname Y", "Y 1")],
    hint="Each patch is a Partial<User>; `{ ...user, ...patch }` overrides just its field.",
))

_add_challenge("ts_async", _chal(
    "ts_async-challenge", "Async square-sum", "Medium",
    "The input is a line of numbers. Write a `square(n)` that returns a `Promise<number>`, then in an `async` function `await` each square and print the total sum.",
    r'''
function square(n: number): Promise<number> {
  return new Promise(resolve => resolve(n * n));
}
async function main(): Promise<void> {
  const nums = input.split(/\s+/).map(Number);
  let total = 0;
  for (const n of nums) {
    total += await square(n);
  }
  console.log(total);
}
await main();
''',
    [("1 2 3", "14"), ("0", "0"), ("2 2 2", "12"), ("-3 4", "25")],
    hint="await square(n) inside the loop unwraps the Promise to a plain number to add up.",
))

_add_challenge("ts_assertions", _chal(
    "ts_assertions-challenge", "First adult", "Medium",
    "The input is a JSON array of people like `[{\"name\":\"Ada\",\"age\":36}]`. Parse it and assert the shape with `as`, then print the name of the first person aged 18 or older, or `none` if there is none.",
    r'''
interface Person { name: string; age: number; }
const people = JSON.parse(input) as Person[];
const adult = people.find(p => p.age >= 18);
if (adult) {
  console.log(adult.name);
} else {
  console.log("none");
}
''',
    [('[{"name":"Kid","age":10},{"name":"Ada","age":36}]', "Ada"),
     ('[{"name":"A","age":18}]', "A"),
     ('[{"name":"B","age":5}]', "none"),
     ('[]', "none")],
    hint="`JSON.parse(input) as Person[]` tells TypeScript the parsed value's shape.",
))

_add_challenge("ts_compose", _chal(
    "ts_compose-challenge", "Labeled point", "Medium",
    "The input is `label x y`. Using an intersection type `Point & Labeled`, build one object holding all three, then print `<label>: (<x>, <y>)` on line 1 and `|x| + |y|` on line 2.",
    r'''
type Point = { x: number; y: number };
type Labeled = { label: string };
type LabeledPoint = Point & Labeled;
const [label, xs, ys] = input.split(/\s+/);
const lp: LabeledPoint = { label, x: Number(xs), y: Number(ys) };
console.log(lp.label + ": (" + lp.x + ", " + lp.y + ")");
console.log(Math.abs(lp.x) + Math.abs(lp.y));
''',
    [("origin 0 0", "origin: (0, 0)\n0"), ("A 3 4", "A: (3, 4)\n7"),
     ("p -1 -2", "p: (-1, -2)\n3"), ("home 5 5", "home: (5, 5)\n10")],
    hint="Point & Labeled requires x, y, AND label together in one object.",
))

_add_challenge("ts_json", _chal(
    "ts_json-challenge", "Inventory total", "Easy",
    "The input is a JSON array of items like `[{\"name\":\"a\",\"qty\":2,\"price\":3}]`. Parse it and print the total value — the sum of `qty × price` across all items.",
    r'''
interface Item { name: string; qty: number; price: number; }
const items = JSON.parse(input) as Item[];
const total = items.reduce((sum, it) => sum + it.qty * it.price, 0);
console.log(total);
''',
    [('[{"name":"a","qty":2,"price":3}]', "6"),
     ('[]', "0"),
     ('[{"name":"x","qty":1,"price":10},{"name":"y","qty":3,"price":2}]', "16"),
     ('[{"name":"z","qty":0,"price":99}]', "0")],
    hint="JSON.parse gives you the array; reduce over qty * price starting from 0.",
))

_add_challenge("ts_immutability", _chal(
    "ts_immutability-challenge", "Immutable ledger", "Medium",
    "Line 1 is a starting balance; each later line is a delta. Build a NEW state object for every step (never mutate the old one) using spread, keeping a history array. Print `<finalBalance> <numberOfStates>`.",
    r'''
interface State { balance: number; steps: number; }
const lines = input.split("\n");
let state: State = { balance: Number(lines[0]), steps: 0 };
const history: State[] = [state];
for (let i = 1; i < lines.length; i++) {
  const delta = Number(lines[i]);
  state = { ...state, balance: state.balance + delta, steps: state.steps + 1 };
  history.push(state);
}
console.log(state.balance + " " + history.length);
''',
    [("100\n10\n-20", "90 3"), ("0", "0 1"),
     ("5\n5\n5\n5", "20 4"), ("50\n-50", "0 2")],
    hint="`state = { ...state, balance: ... }` makes a fresh object; push each new state to history.",
))


# ===========================================================================
# 2) NEW FOUNDATIONAL CONCEPTS — Numbers & Math, String Methods.
#    Each gets a lesson, two drills, and a challenge.
# ===========================================================================
CONCEPTS.update({
    "ts_number_math": {
        "name": "Numbers & Math",
        "what": "Rounding, integer division, absolute value, and the Math toolbox — plus NaN and Infinity.",
        "deep": "There is one `number` type for ints and floats, so `7 / 2` is `3.5`. When you need a whole number you round explicitly: `Math.floor`, `Math.round`, `Math.ceil`, or `Math.trunc`. The `Math` object also gives you `abs`, `min`, `max`, `pow`, and `sqrt`. Watch for `NaN` (from a failed `Number(...)`) and `Infinity` (from dividing by zero).",
        "java": "`/` never truncates — `7 / 2` is `3.5`, not `3`. Use `Math.floor(a / b)` for Java-style integer division. `Math.floor/round/ceil` match Java's Math; `x % 0` is `NaN` (not an exception) and `x / 0` is `Infinity`. Check a parse with `Number.isNaN(n)`, never `n === NaN` (which is always false).",
        "language": "typescript",
    },
    "ts_string_methods": {
        "name": "String Methods",
        "what": "The everyday string toolbox: slice, indexOf/includes, replace/replaceAll, padStart, repeat, and split/join.",
        "deep": "Strings are immutable, so every method returns a NEW string. `slice(start, end)` cuts a substring, `indexOf`/`includes` search, `replaceAll` swaps text, `padStart`/`padEnd` align, `repeat` duplicates, and `split`/`join` convert to and from arrays. Chaining them is how you clean and reshape text.",
        "java": "Methods are camelCase and mostly match Java's `String` (`indexOf`, `replace`, `split`). `slice` allows negative indices (from the end) — handier than `substring`. `padStart(5, \"0\")` replaces `String.format(\"%05d\", n)`, and `\"ab\".repeat(3)` replaces a manual loop.",
        "language": "typescript",
    },
})

CATEGORY.update({
    "ts_number_math": "TS: Language Basics",
    "ts_string_methods": "TS: Language Basics",
})

LESSONS.update({
    "ts_number_math": """### Worked example
One `number` type means division keeps the fraction:
```ts
7 / 2;             // 3.5   (NOT 3)
Math.floor(7 / 2); // 3     integer division
Math.trunc(-7 / 2);// -3    toward zero
-7 % 3;            // -1    remainder keeps the sign of the left operand
```

### Rounding
```ts
Math.floor(3.7);  // 3   down
Math.ceil(3.2);   // 4   up
Math.round(3.5);  // 4   nearest (.5 rounds up)
Math.trunc(3.9);  // 3   drop the fraction
```

### The Math toolbox
```ts
Math.abs(-5);        // 5
Math.min(3, 9, 1);   // 1
Math.max(3, 9, 1);   // 9
Math.pow(2, 10);     // 1024   (or 2 ** 10)
Math.sqrt(144);      // 12
```
Spread an array into `min`/`max`: `Math.max(...nums)`.

### NaN and Infinity
```ts
Number("oops");      // NaN   — a failed conversion
Number.isNaN(Number("oops")); // true  — the safe test
1 / 0;               // Infinity
```

### Watch out for
- `Math.round(-2.5)` is `-2` (rounds toward +∞), not `-3`.
- `n === NaN` is **always false**. Use `Number.isNaN(n)`.
- For big whole numbers beyond ~9 quadrillion, reach for `bigint`.
""",
    "ts_string_methods": """### Worked example
Every method returns a new string — the original is untouched:
```ts
const s = "Poodcode";
s.slice(0, 4);        // "Pood"    (start, end-exclusive)
s.slice(-4);          // "code"    negative counts from the end
s.indexOf("code");    // 4         (-1 if not found)
s.includes("ood");    // true
s.toUpperCase();      // "POODCODE"
```

### Reshaping text
```ts
"a-b-c".split("-");            // ["a","b","c"]
["a","b","c"].join("/");      // "a/b/c"
"  hi  ".trim();               // "hi"
"5".padStart(3, "0");          // "005"
"ab".repeat(3);                // "ababab"
"cat cat".replaceAll("cat", "dog"); // "dog dog"
```

### Chaining
```ts
const clean = "  Hello, World  "
  .trim()                 // "Hello, World"
  .toLowerCase()          // "hello, world"
  .replaceAll(",", "");   // "hello world"
```

### Counting occurrences
A quick trick: `text.split(needle).length - 1` counts how many times `needle` appears.

### Watch out for
- `replace` swaps only the FIRST match; use `replaceAll` for every match.
- `slice` and `substring` differ on negative indices — prefer `slice`.
- Indexing past the end (`s[99]`) gives `undefined`, not an error.
""",
})

EXERCISES.update({
    "ts_number_math": [
        tsx(
            "ts_number_math-intdiv", "Integer division",
            "The input is two numbers `a b`. Replace `____` to print the integer part of `a / b` (round down with `Math.floor`).",
            _P(r'''
import * as fs from "fs";
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
console.log(Math.floor(a / b));
'''),
            [r'Math.floor(a / b)'],
            [("7 2", "3"), ("10 3", "3"), ("9 3", "3"), ("1 2", "0")],
            hint="Plain a / b keeps the fraction; Math.floor rounds it down to an integer.",
        ),
        tsx(
            "ts_number_math-round", "Round three ways",
            "The input is one decimal number. Replace `____` to print its `Math.round`, then `Math.floor`, then `Math.ceil`, each on its own line.",
            _P(r'''
import * as fs from "fs";
const x = Number(fs.readFileSync(0, "utf8").trim());
console.log(Math.round(x));
console.log(Math.floor(x));
console.log(Math.ceil(x));
'''),
            [r'''console.log(Math.round(x));
console.log(Math.floor(x));
console.log(Math.ceil(x));'''],
            [("3.5", "4\n3\n4"), ("2.1", "2\n2\n3"), ("7", "7\n7\n7")],
            hint="round = nearest, floor = down, ceil = up.",
        ),
    ],
    "ts_string_methods": [
        tsx(
            "ts_string_methods-pad", "Zero-pad a number",
            "The input is a number. Replace `____` to print it as a string padded on the left with `0` to a width of 5 — `42` → `00042`.",
            _P(r'''
import * as fs from "fs";
const n = fs.readFileSync(0, "utf8").trim();
console.log(n.padStart(5, "0"));
'''),
            [r'n.padStart(5, "0")'],
            [("42", "00042"), ("7", "00007"), ("12345", "12345")],
            hint='padStart(5, "0") adds leading zeros until the string is 5 characters wide.',
        ),
        tsx(
            "ts_string_methods-count", "Count a character",
            "The input is a word then a single character, like `banana a`. Replace `____` to print how many times the character appears in the word (use the split-length trick).",
            _P(r'''
import * as fs from "fs";
const [word, ch] = fs.readFileSync(0, "utf8").trim().split(/\s+/);
console.log(word.split(ch).length - 1);
'''),
            [r'word.split(ch).length - 1'],
            [("banana a", "3"), ("hello l", "2"), ("abc z", "0")],
            hint="Splitting on the character yields one more piece than there are occurrences.",
        ),
    ],
})

_add_challenge("ts_number_math", _chal(
    "ts_number_math-challenge", "Digit sum", "Intro",
    "The input is one integer (possibly negative). Print two numbers separated by a space: the sum of its digits and how many digits it has. Use `% 10` and `Math.floor(n / 10)`.",
    r'''
let n = Math.abs(Number(input));
let sum = 0;
let digits = 0;
if (n === 0) digits = 1;
while (n > 0) {
  sum += n % 10;
  n = Math.floor(n / 10);
  digits++;
}
console.log(sum + " " + digits);
''',
    [("123", "6 3"), ("0", "0 1"), ("-45", "9 2"), ("1000", "1 4")],
    hint="Peel the last digit with n % 10, then drop it with Math.floor(n / 10) until n is 0.",
))

_add_challenge("ts_string_methods", _chal(
    "ts_string_methods-challenge", "Censor a word", "Easy",
    "Line 1 is a sentence; line 2 is a word to censor. Replace every occurrence of the word with a run of `*` the same length, and print the result. Use `repeat` and `split`/`join` (or `replaceAll`).",
    r'''
const lines = input.split("\n");
const text = lines[0];
const word = lines[1].trim();
const stars = "*".repeat(word.length);
console.log(text.split(word).join(stars));
''',
    [("the cat sat\ncat", "the *** sat"), ("aaa\na", "***"),
     ("hello world\nworld", "hello *****"), ("no match here\nxyz", "no match here")],
    hint='"*".repeat(word.length) builds the mask; split(word).join(mask) swaps every occurrence.',
))
