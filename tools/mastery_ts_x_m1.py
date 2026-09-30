# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — per-chapter reading kinds, Month 1 (TS_MASTERY_ROADMAP
# X-10, X-11): predict / diagnose / retype / design / fix for the fundamentals
# chapters of weeks 1-4 (program I/O, variables, types, operators, control
# flow, numbers, strings, regex, Unicode), topping each chapter up to its target.
#
# Weeks 1-4 run at `strict` and come before interfaces, try/catch, JSON and
# `as const`, so every program here is a short stdin-to-stdout script built
# from what the chapter itself teaches. Helpers are in
# mastery_ts_chapter_kit.py; exec()'d by gen_seed.py with the other
# tools/mastery_ts_x_m*.py files.
# ---------------------------------------------------------------------------


# ===========================================================================
# Week 1 — ts_program_io
# ===========================================================================

_xpr("ts_program_io", 1, "Tokens from a line", r'''
const line = "3   4";
const parts = line.split(/\s+/);
''', "parts", "string[]",
     hints=["`split` cuts a string into pieces. What are the pieces made of?",
            "Every piece of a string is a string — so the whole result is an array of them."])

_xpr("ts_program_io", 2, "Tokens turned into numbers", r'''
const line = "3 4 10";
const nums = line.split(/\s+/).map(Number);
''', "nums", "number[]",
     hints=["`map` replaces each element with what the function returns.",
            "`Number(...)` returns a `number`, so each string becomes a number."])

_xpr("ts_program_io", 3, "What `toFixed` gives back", r'''
const price = 2.5;
const shown = price.toFixed(2);
''', "shown", "string",
     hints=["`toFixed(2)` produces `\"2.50\"` — with a trailing zero a number could never keep.",
            "It returns text ready to print, not a number."])

_xrt("ts_program_io", 1, "Two tokens, typed", "The program adds the two numbers on the line. Replace the `any` with what `split` really returns.",
     r'''
const parts: any = input.split(/\s+/);
console.log(Number(parts[0]) + Number(parts[1]));
''', r'''
const parts: string[] = input.split(/\s+/);
console.log(Number(parts[0]) + Number(parts[1]));
''', "type _1 = Expect<Equal<typeof parts, string[]>>;", ["2 3", "10    -4", "0 0"],
     hints=["`split` always hands back an array of strings.", "`string[]` — or drop the annotation and let it be inferred."])

_xrt("ts_program_io", 2, "A price and its label", "It reads a price and prints it with a dollar sign and two decimals. Replace each `any` with the type the value really has.",
     r'''
const price: any = parseFloat(input);
const label: any = "$" + price.toFixed(2);
console.log(label);
''', r'''
const price: number = parseFloat(input);
const label: string = "$" + price.toFixed(2);
console.log(label);
''', "type _1 = Expect<Equal<typeof price, number>>;\ntype _2 = Expect<Equal<typeof label, string>>;",
     ["2.5", "10", "0.125"],
     hints=["`parseFloat` reads a number; `toFixed` turns it back into text.",
            "`price` is a `number`, `label` is a `string`."])

_xrt("ts_program_io", 3, "Lines and a count", "The input is several lines; it prints how many and the first one. Replace the `any`s.",
     r'''
const lines: any = input.split("\n");
const count: any = lines.length;
console.log(`${count} line(s), first: ${lines[0].trim()}`);
''', r'''
const lines: string[] = input.split("\n");
const count: number = lines.length;
console.log(`${count} line(s), first: ${lines[0].trim()}`);
''', "type _1 = Expect<Equal<typeof lines, string[]>>;\ntype _2 = Expect<Equal<typeof count, number>>;",
     ["Ada\nGrace\nAlan", "one", "x\ny"],
     hints=["Splitting on `\"\\n\"` gives one string per line.", "`length` is always a `number`."])

_xdz("ts_program_io", 1, "A parsed pair of lines", "The first line is a name and the second an age. Write the `Person` type the parsed input fills in.",
     r'''
type Person = { name: string; age: number };
const lines = input.split("\n");
const person: Person = { name: lines[0].trim(), age: Number(lines[1]) };
console.log(`Hello, ${person.name}. Next year you will be ${person.age + 1}.`);
''', "type Person = { name: string; age: number };",
     "type _1 = Expect<Equal<Person, { name: string; age: number }>>;", ["Ada\n36", "Grace\n85"],
     hints=["Look at what goes into each property: one stays text, one is converted.",
            "`name` is a string; `age` goes through `Number`, and `+ 1` needs a number."])

_xdz("ts_program_io", 2, "A receipt line", "The line holds an item, a quantity and a unit price (`apple 3 0.5`). Write `Order` from how it is filled and printed.",
     r'''
type Order = { item: string; qty: number; price: number };
const parts = input.split(/\s+/);
const order: Order = { item: parts[0], qty: Number(parts[1]), price: Number(parts[2]) };
console.log(`${order.qty} x ${order.item} = $${(order.qty * order.price).toFixed(2)}`);
''', "type Order = { item: string; qty: number; price: number };",
     "type _1 = Expect<Equal<Order, { item: string; qty: number; price: number }>>;",
     ["apple 3 0.5", "pen 10 1.25", "book 1 12"],
     hints=["Three properties; the prompt's example line shows their order.",
            "The two that are multiplied must be numbers."])

_xdz("ts_program_io", 3, "What the reader returns", "`readNumbers` turns a line into its numbers. Write its return type.",
     r'''
function readNumbers(text: string): number[] {
  return text.split(/\s+/).map(Number);
}
const nums = readNumbers(input);
console.log(`count ${nums.length}, first doubled ${nums[0] * 2}`);
''', "number[]",
     "type _1 = Expect<Equal<ReturnType<typeof readNumbers>, number[]>>;", ["3 4 5", "21", "-1 -2"],
     hints=["`split` gives strings; what does `.map(Number)` make of them?", "An array of numbers."])

_xfx("ts_program_io", 1, "An average that counts gaps",
     "It prints the average of the numbers on the line, to two decimals. With more than one space between numbers the average comes out too small.",
     r'''
const tokens = input.split(" ");
let sum = 0;
for (const t of tokens) sum += Number(t);
console.log((sum / tokens.length).toFixed(2));
''', r'''
const tokens = input.split(/\s+/);
let sum = 0;
for (const t of tokens) sum += Number(t);
console.log((sum / tokens.length).toFixed(2));
''', ["2 4 6", "10  20", "5   5   5", "7"],
     hints=["Print `tokens` for `10  20`: how many are there?",
            "`split(\" \")` makes an empty token between two spaces, and `Number(\"\")` is 0. Split on `/\\s+/`."])

_xfx("ts_program_io", 2, "A price that loses its cents",
     "It reads a unit price and a quantity and prints the total to two decimals. `2.5 3` should print `7.50`.",
     r'''
const parts = input.split(/\s+/);
const price = parseInt(parts[0], 10);
const qty = parseInt(parts[1], 10);
console.log((price * qty).toFixed(2));
''', r'''
const parts = input.split(/\s+/);
const price = parseFloat(parts[0]);
const qty = parseInt(parts[1], 10);
console.log((price * qty).toFixed(2));
''', ["2.5 3", "10 2", "0.99 10"],
     hints=["What does `parseInt(\"2.5\", 10)` return?",
            "`parseInt` stops at the decimal point. A price needs `parseFloat` (or `Number`)."])


# ===========================================================================
# Week 1 — ts_variables
# ===========================================================================

_xdx("ts_variables", 1, "A label stuck in its block",
     "TS2304: Cannot find name 'label'.",
     r'''
const n = Number(input);
if (n % 2 === 0) {
  const label = "even";
} else {
  const label = "odd";
}
console.log(`${n} is ${label}`);
''', r'''
const n = Number(input);
let label: string;
if (n % 2 === 0) {
  label = "even";
} else {
  label = "odd";
}
console.log(`${n} is ${label}`);
''', ["4", "7", "0"], ask="Each `const label` lives only inside its own `{ }`. Fix it so the `console.log` can see one.",
     hints=["A `const` or `let` exists only inside the nearest braces.",
            "Declare `label` once, before the `if`, with `let` — then assign it in each branch."])

_xrt("ts_variables", 1, "A running total", "It sums the numbers on the line. Replace the `any` on `total`.",
     r'''
let total: any = 0;
for (const t of input.split(/\s+/)) total += Number(t);
console.log(total);
''', r'''
let total: number = 0;
for (const t of input.split(/\s+/)) total += Number(t);
console.log(total);
''', "type _1 = Expect<Equal<typeof total, number>>;", ["1 2 3", "10", "-5 5"],
     hints=["What does `total` start as, and what is added to it?", "`let total = 0` is already a `number`."])

_xrt("ts_variables", 2, "Swapping two tokens", "It prints the two words on the line in the other order. Replace the `any`s.",
     r'''
const parts = input.split(/\s+/);
let first: any = parts[0];
let second: any = parts[1];
const held = first;
first = second;
second = held;
console.log(first, second);
''', r'''
const parts = input.split(/\s+/);
let first: string = parts[0];
let second: string = parts[1];
const held = first;
first = second;
second = held;
console.log(first, second);
''', "type _1 = Expect<Equal<typeof first, string>>;\ntype _2 = Expect<Equal<typeof second, string>>;\ntype _3 = Expect<Equal<typeof held, string>>;",
     ["left right", "b a", "x x"],
     hints=["They come straight out of `split`, unconverted.",
            "Both are `string` — and once they are, `held` is inferred as `string` too."])

_xrt("ts_variables", 3, "The longest word so far", "It keeps the longest word seen and prints it. Replace the `any`s on the two `let`s.",
     r'''
let longest: any = "";
let seen: any = 0;
for (const w of input.split(/\s+/)) {
  seen = seen + 1;
  if (w.length > longest.length) longest = w;
}
console.log(`${longest} (of ${seen})`);
''', r'''
let longest: string = "";
let seen: number = 0;
for (const w of input.split(/\s+/)) {
  seen = seen + 1;
  if (w.length > longest.length) longest = w;
}
console.log(`${longest} (of ${seen})`);
''', "type _1 = Expect<Equal<typeof longest, string>>;\ntype _2 = Expect<Equal<typeof seen, number>>;",
     ["a bbb cc", "hello", "one two six"],
     hints=["Look at the starting value of each `let`.", "`longest` holds a word; `seen` counts."])

_xdz("ts_variables", 1, "A const that still changes", "`tally` is a `const`, yet its contents change on every line. Write its `Tally` type.",
     r'''
type Tally = { count: number; total: number };
const tally: Tally = { count: 0, total: 0 };
for (const t of input.split(/\s+/)) {
  tally.count += 1;
  tally.total += Number(t);
}
console.log(`${tally.count} numbers, total ${tally.total}`);
''', "type Tally = { count: number; total: number };",
     "type _1 = Expect<Equal<Tally, { count: number; total: number }>>;", ["1 2 3", "10", "-1 1 -1"],
     hints=["`const` fixes which object `tally` names, not what is inside it.",
            "Two numeric properties, both updated with `+=`."])

_xdz("ts_variables", 2, "Declared now, assigned later", "`verdict` is declared without a value and assigned in each branch. Write the `Verdict` type — as narrow as the assignments allow.",
     r'''
type Verdict = "even" | "odd";
const n = Number(input);
let verdict: Verdict;
if (n % 2 === 0) verdict = "even";
else verdict = "odd";
console.log(`${n}: ${verdict}`);
''', 'type Verdict = "even" | "odd";',
     'type _1 = Expect<Equal<Verdict, "even" | "odd">>;', ["4", "9", "0"],
     hints=["A `let` with no initialiser has nothing to infer from, so it needs a type.",
            "Only two strings are ever assigned — the type can list exactly those."])

_xdz("ts_variables", 3, "Replacing the best so far", "`best` is a `let` that is pointed at a new object whenever a longer word turns up. Write `Best`.",
     r'''
type Best = { word: string; size: number };
let best: Best = { word: "", size: 0 };
for (const w of input.split(/\s+/)) {
  if (w.length > best.size) best = { word: w, size: w.length };
}
console.log(`${best.word} has ${best.size} letters`);
''', "type Best = { word: string; size: number };",
     "type _1 = Expect<Equal<Best, { word: string; size: number }>>;", ["cat horse ox", "a", "tie tee"],
     hints=["Read the object literals assigned to `best`.", "`word` is a word; `size` comes from `.length`."])

_xfx("ts_variables", 1, "A swap that loses a value",
     "It should print the two words on the line swapped (`left right` prints `right left`). It prints the same word twice.",
     r'''
const parts = input.split(/\s+/);
let a = parts[0];
let b = parts[1];
a = b;
b = a;
console.log(a, b);
''', r'''
const parts = input.split(/\s+/);
let a = parts[0];
let b = parts[1];
const held = a;
a = b;
b = held;
console.log(a, b);
''', ["left right", "1 2", "same same"],
     hints=["After `a = b`, what is left of `a`'s old value?",
            "Keep the old value in a `const` before overwriting it."])

_xfx("ts_variables", 2, "A maximum that starts at zero",
     "It should print the largest of the numbers on the line. For `-3 -7 -1` it prints `0`.",
     r'''
const nums = input.split(/\s+/).map(Number);
let max = 0;
for (const n of nums) if (n > max) max = n;
console.log(max);
''', r'''
const nums = input.split(/\s+/).map(Number);
let max = nums[0];
for (const n of nums) if (n > max) max = n;
console.log(max);
''', ["3 9 2", "-3 -7 -1", "5"],
     hints=["What if every number is below the starting value?",
            "Start `max` at the first number (or `-Infinity`), not at 0."])


# ===========================================================================
# Week 1 — ts_types
# ===========================================================================

_xpr("ts_types", 1, "A mixed list", r'''
const row = [42, "hi", true];
''', "row", "(string | number | boolean)[]",
     hints=["An array literal gets one element type that covers every element.",
            "Three kinds of primitive — the element type is their union."])

_xpr("ts_types", 2, "A big integer", r'''
let big = 2n ** 64n;
''', "big", "bigint",
     hints=["The `n` suffix makes a different primitive from `number`.",
            "A `let` widens to the general type of that primitive."])

_xdx("ts_types", 1, "A capital-N number",
     "TS2322: Type 'Number' is not assignable to type 'number'.",
     r'''
const n: number = new Number(input);
console.log(n * 2);
''', r'''
const n: number = Number(input);
console.log(n * 2);
''', ["21", "-4", "0.5"],
     hints=["`new Number(...)` builds a wrapper object, not a primitive.",
            "Call `Number(input)` without `new` to convert."])

_xrt("ts_types", 1, "A yes/no answer", "It says whether the age is an adult's. Replace the `any`s.",
     r'''
const age: any = Number(input);
const adult: any = age >= 18;
console.log(adult ? "adult" : "minor");
''', r'''
const age: number = Number(input);
const adult: boolean = age >= 18;
console.log(adult ? "adult" : "minor");
''', "type _1 = Expect<Equal<typeof age, number>>;\ntype _2 = Expect<Equal<typeof adult, boolean>>;",
     ["18", "17", "40"],
     hints=["A comparison is either true or false.", "`age` is a `number`; `adult` is a `boolean`."])

_xrt("ts_types", 2, "Maybe a nickname", "The line is a name and, optionally, a nickname. `nickname` is `null` until one is found. Replace the `any`.",
     r'''
const parts = input.split(/\s+/);
let nickname: any = null;
if (parts.length > 1) nickname = parts[1];
console.log(`${parts[0]} (${nickname ?? "no nickname"})`);
''', r'''
const parts = input.split(/\s+/);
let nickname: string | null = null;
if (parts.length > 1) nickname = parts[1];
console.log(`${parts[0]} (${nickname ?? "no nickname"})`);
''', "type _1 = Expect<Equal<typeof nickname, string | null>>;", ["Margaret Peggy", "Alan", "Ada Countess"],
     hints=["It starts as one thing and may later hold another.",
            "`null` for \"deliberately empty\", or a `string` from the line: `string | null`."])

_xdz("ts_types", 1, "Two units only", "`convert` takes a temperature and its unit, and only two units exist. Write `Unit`.",
     r'''
type Unit = "c" | "f";
function convert(value: number, unit: Unit): string {
  return unit === "c" ? `${(value * 9) / 5 + 32}F` : `${((value - 32) * 5) / 9}C`;
}
const parts = input.split(/\s+/);
const unit = parts[1] === "f" ? "f" : "c";
console.log(convert(Number(parts[0]), unit));
''', 'type Unit = "c" | "f";',
     'type _1 = Expect<Equal<Unit, "c" | "f">>;', ["100 c", "212 f", "-40 c"],
     hints=["A literal type is a promise that the value is one exact string.",
            "Two literals joined with `|`."])

_xdz("ts_types", 2, "A product row", "The line is a name, a price and `yes`/`no` for in stock. Write `Product` from how it is built and printed.",
     r'''
type Product = { name: string; price: number; inStock: boolean };
const parts = input.split(/\s+/);
const p: Product = { name: parts[0], price: Number(parts[1]), inStock: parts[2] === "yes" };
console.log(`${p.name}: $${p.price.toFixed(2)} (${p.inStock ? "in stock" : "sold out"})`);
''', "type Product = { name: string; price: number; inStock: boolean };",
     "type _1 = Expect<Equal<Product, { name: string; price: number; inStock: boolean }>>;",
     ["pen 1.5 yes", "lamp 20 no"],
     hints=["One of each primitive you met first.", "`parts[2] === \"yes\"` is a comparison — what type is that?"])

_xdz("ts_types", 3, "A checked conversion", "`parse` converts text and says whether it worked. Write the `Parsed` type it returns.",
     r'''
type Parsed = { ok: boolean; value: number };
function parse(text: string): Parsed {
  const n = Number(text);
  return { ok: !Number.isNaN(n), value: n };
}
const r = parse(input);
console.log(r.ok ? `doubled: ${r.value * 2}` : "not a number");
''', "type Parsed = { ok: boolean; value: number };",
     "type _1 = Expect<Equal<Parsed, { ok: boolean; value: number }>>;", ["21", "abc", "2.5"],
     hints=["Look at the object `parse` returns.", "`!Number.isNaN(n)` is a boolean; `n` is a number."])


# ===========================================================================
# Week 1 — ts_inference
# ===========================================================================

_xpr("ts_inference", 1, "Inferred through a callback", r'''
const halves = [3, 8].map((n) => n / 2 > 2);
''', "halves", "boolean[]",
     hints=["`n` is typed from the array; what does the arrow return?", "A comparison — so each element is a boolean."])

_xdx("ts_inference", 1, "A `let` that widened",
     "TS2345: Argument of type 'string' is not assignable to parameter of type '\"c\" | \"f\"'.",
     r'''
function convert(value: number, unit: "c" | "f"): string {
  return unit === "c" ? `${value} C` : `${value} F`;
}
const parts = input.split(/\s+/);
let unit = "c";
if (parts[1] === "f") unit = "f";
console.log(convert(Number(parts[0]), unit));
''', r'''
function convert(value: number, unit: "c" | "f"): string {
  return unit === "c" ? `${value} C` : `${value} F`;
}
const parts = input.split(/\s+/);
let unit: "c" | "f" = "c";
if (parts[1] === "f") unit = "f";
console.log(convert(Number(parts[0]), unit));
''', ["20 c", "68 f", "5"], ask="`unit` has to stay a `let` — it is reassigned. Fix the cause without changing that.",
     hints=["What does TypeScript infer for `let unit = \"c\"`?",
            "A `let` widens to `string`. Annotate it with the two values it may hold."])

_xrt("ts_inference", 1, "Typed by the array", "It keeps the numbers above 10. Replace the `any`s — the callback's parameter needs no annotation at all.",
     r'''
const nums: any = input.split(/\s+/).map(Number);
const big: any = nums.filter((n: any) => n > 10);
console.log(big.length === 0 ? "none" : big.join(" "));
''', r'''
const nums = input.split(/\s+/).map(Number);
const big = nums.filter((n) => n > 10);
console.log(big.length === 0 ? "none" : big.join(" "));
''', "type _1 = Expect<Equal<typeof nums, number[]>>;\ntype _2 = Expect<Equal<typeof big, number[]>>;",
     ["5 12 30", "1 2", "11"],
     hints=["Once `nums` has its real type, `n` is inferred from it (contextual typing).",
            "Delete every `: any` — inference gives `number[]` all the way down."])

_xrt("ts_inference", 2, "Min and max from the first", "It prints the smallest and largest number. Replace the `any`s by deleting them — the initialisers say enough.",
     r'''
const nums = input.split(/\s+/).map(Number);
let min: any = nums[0];
let max: any = nums[0];
for (const n of nums) {
  if (n < min) min = n;
  if (n > max) max = n;
}
console.log(`min ${min} max ${max}`);
''', r'''
const nums = input.split(/\s+/).map(Number);
let min = nums[0];
let max = nums[0];
for (const n of nums) {
  if (n < min) min = n;
  if (n > max) max = n;
}
console.log(`min ${min} max ${max}`);
''', "type _1 = Expect<Equal<typeof min, number>>;\ntype _2 = Expect<Equal<typeof max, number>>;",
     ["3 9 -2", "7", "4 4"],
     hints=["An initialiser is all inference needs.", "`nums[0]` is a `number`, so `min` and `max` are too."])

_xrt("ts_inference", 3, "A return type from every path", "`label` is annotated `any`. Delete the annotation so the return type is inferred from its `return`s.",
     r'''
function label(n: number): any {
  if (n > 0) return "positive";
  return "not positive";
}
console.log(label(Number(input)));
''', r'''
function label(n: number) {
  if (n > 0) return "positive";
  return "not positive";
}
console.log(label(Number(input)));
''', 'type _1 = Expect<Equal<ReturnType<typeof label>, "positive" | "not positive">>;', ["5", "0", "-3"],
     hints=["Every `return` contributes to the inferred return type.",
            "Two different string literals: the return type is their union."])

_xdz("ts_inference", 1, "An empty list needs a type", "`long` starts empty, so there is nothing to infer from. Write its annotation.",
     r'''
const long: string[] = [];
for (const w of input.split(/\s+/)) if (w.length > 3) long.push(w);
console.log(long.length === 0 ? "none" : long.join(","));
''', "string[]",
     "type _1 = Expect<Equal<typeof long, string[]>>;", ["tree a house", "a b", "longer"],
     hints=["What is pushed into it?", "Words — so an array of strings."])

_xdz("ts_inference", 2, "Not known yet", "`best` has no value until the loop finds one. Write its type so the `=== undefined` check is honest.",
     r'''
let best: number | undefined;
for (const t of input.split(/\s+/)) {
  const n = Number(t);
  if (best === undefined || n > best) best = n;
}
console.log(`best ${best}`);
''', "number | undefined",
     "type _1 = Expect<Equal<typeof best, number | undefined>>;", ["3 9 2", "-5", "1 1"],
     hints=["Before the first assignment it holds nothing.", "A number once found, `undefined` before."])

_xdz("ts_inference", 3, "Parameters have nothing to infer from", "Write `describe`'s parameter list — each parameter needs its own annotation.",
     r'''
function describe(value: number, unit: string) {
  return `${value.toFixed(1)} ${unit}`;
}
const parts = input.split(/\s+/);
console.log(describe(Number(parts[0]), parts[1]));
''', "value: number, unit: string",
     "type _1 = Expect<Equal<Parameters<typeof describe>, [value: number, unit: string]>>;",
     ["3 km", "2.25 kg", "100 m"],
     hints=["`value` has `.toFixed` called on it.", "One number, one string."])

_xfx("ts_inference", 1, "Zero falls through",
     "It should print `positive`, `negative` or `zero`. For `0` it prints `undefined` — the inferred return type allowed that.",
     r'''
function sign(n: number) {
  if (n > 0) return "positive";
  if (n < 0) return "negative";
}
console.log(sign(Number(input)));
''', r'''
function sign(n: number): string {
  if (n > 0) return "positive";
  if (n < 0) return "negative";
  return "zero";
}
console.log(sign(Number(input)));
''', ["5", "-2", "0"],
     hints=["Hover `sign`: its inferred return type ends in `| undefined`.",
            "Annotate the return type `string` and add the missing `return`."])

_xfx("ts_inference", 2, "An `any` that concatenates",
     "The line is a name and a score; it should print the score plus a 5-point bonus (`Ada 40` prints `Ada 45`). It prints `Ada 405`.",
     r'''
const parts = input.split(/\s+/);
const score: any = parts[1];
console.log(parts[0], score + 5);
''', r'''
const parts = input.split(/\s+/);
const score = Number(parts[1]);
console.log(parts[0], score + 5);
''', ["Ada 40", "Alan 0", "Grace 95"],
     hints=["`any` switched checking off — what is `score` really?",
            "It is still the text `\"40\"`. Convert it with `Number` and let inference type it."])
