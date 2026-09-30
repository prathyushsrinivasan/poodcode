# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — per-chapter reading kinds, Month 4 (TS_MASTERY_ROADMAP
# X-10, X-11): predict / diagnose / retype / design / fix for the tooling and
# type-design chapters of weeks 14-17, topping each chapter up to its target.
#
# Weeks 14-17 run at strict+indexed. The judge compiles ONE file under a fixed
# tsconfig, so the tooling chapters (tsconfig, modules, declaration files,
# erasable syntax, versions) practise what a single file can show: what the
# strict flags reject, `declare` and ambient shapes, `export` / `import type`
# syntax, erasable alternatives to enum / namespace / parameter properties, and
# library features by version. Enum, namespace and parameter properties appear
# only in type-only exercises (no inputs), since Node strips types to run.
# Helpers are in mastery_ts_chapter_kit.py; exec()'d by gen_seed.py with the
# other tools/mastery_ts_x_m*.py files.
# ---------------------------------------------------------------------------

# ── ts_tsconfig ──────────────────────────────────────────────────────────────

_xpr("ts_tsconfig", 1, "Destructuring reads an index too",
     "const scores = [90, 72];\nconst [head] = scores;\n", "head", "number | undefined",
     hints=["`const [head] = scores` is `scores[0]` in disguise.",
            "Under `noUncheckedIndexedAccess` an array read may miss: `number | undefined`."])

_xpr("ts_tsconfig", 2, "A tuple knows its length",
     'const pair: [string, number] = ["ana", 3];\nconst count = pair[1];\n', "count", "number",
     hints=["The flag widens reads whose position the type cannot vouch for.",
            "A tuple type fixes its length, so `pair[1]` is certainly there: `number`."])

_xpr("ts_tsconfig", 3, "A default closes the gap",
     'const names = ["ana", "bo"];\nconst shown = names[0] ?? "nobody";\n', "shown", "string",
     hints=["`names[0]` is `string | undefined` under the flag.",
            "`??` replaces the `undefined` with a string, leaving `string`."])

_xdx("ts_tsconfig", 1, "A name that may be null",
     "TS18047: 'name' is possibly 'null'.",
     r'''
function initial(name: string | null): string {
  return name.charAt(0).toUpperCase();
}
const name = input === "-" ? null : input;
console.log(initial(name));
''', r'''
function initial(name: string | null): string {
  return name === null ? "?" : name.charAt(0).toUpperCase();
}
const name = input === "-" ? null : input;
console.log(initial(name));
''', ["ann", "-", "bo"],
     ask="A `-` means no name was given; print `?` for it. Fix the cause.",
     hints=["`strictNullChecks` keeps `null` out of `string`, so the parameter's type says it can be absent.",
            "Check `name === null` before calling a method on it."])

_xrt("ts_tsconfig", 1, "The largest, if there is one",
     "It prints the largest number, or `empty` for no numbers. Replace every `any` with what is really there — including the case the list is empty.",
     r'''
function largest(xs: any): any {
  let best: any = undefined;
  for (const x of xs) if (best === undefined || x > best) best = x;
  return best;
}
const nums = input.split(",").filter((t) => t !== "").map(Number);
const top = largest(nums);
console.log(top === undefined ? "empty" : top.toFixed(1));
''', r'''
function largest(xs: readonly number[]): number | undefined {
  let best: number | undefined = undefined;
  for (const x of xs) if (best === undefined || x > best) best = x;
  return best;
}
const nums = input.split(",").filter((t) => t !== "").map(Number);
const top = largest(nums);
console.log(top === undefined ? "empty" : top.toFixed(1));
''', "type _1 = Expect<Equal<ReturnType<typeof largest>, number | undefined>>;\n"
     "type _2 = Expect<Equal<typeof top, number | undefined>>;",
     ["3,9,4", "-2,-7", ",", "5"],
     hints=["An empty list has no largest — the return type should admit it.",
            "`number | undefined`, and the caller's check then narrows `top`."])

_xrt("ts_tsconfig", 2, "A nickname, if given",
     "Each `;`-separated entry is `name` or `name:nick`. Replace the `any`s with a type that says the nickname is optional.",
     r'''
function label(p: any): any {
  return p.nickname !== undefined ? `${p.name} (${p.nickname})` : p.name;
}
for (const entry of input.split(";")) {
  const [name = "", nickname] = entry.split(":");
  console.log(label(nickname === undefined ? { name } : { name, nickname }));
}
''', r'''
type Person = { name: string; nickname?: string };
function label(p: Person): string {
  return p.nickname !== undefined ? `${p.name} (${p.nickname})` : p.name;
}
for (const entry of input.split(";")) {
  const [name = "", nickname] = entry.split(":");
  console.log(label(nickname === undefined ? { name } : { name, nickname }));
}
''', "type _1 = Expect<Equal<Parameters<typeof label>[0], { name: string; nickname?: string }>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof label>, string>>;",
     ["ana:annie;bo", "cy", "di:dee"],
     hints=["Some entries have a nickname and some don't: an optional property.",
            "`{ name: string; nickname?: string }`, returning `string`."])

_xdz("ts_tsconfig", 1, "A reading that may be missing",
     "Each token is `sensor=value`, or `sensor=` when the sensor gave no reading. Write `Reading` from how it is used.",
     r'''
type Reading = { sensor: string; value: number | null };
const readings: Reading[] = input.split(" ").map((t) => {
  const [sensor = "?", raw = ""] = t.split("=");
  return { sensor, value: raw === "" ? null : Number(raw) };
});
for (const r of readings) {
  console.log(r.value === null ? `${r.sensor}: no reading` : `${r.sensor}: ${r.value.toFixed(1)}`);
}
''', "type Reading = { sensor: string; value: number | null };",
     "type _1 = Expect<Equal<Reading, { sensor: string; value: number | null }>>;",
     ["t1=21.5 t2= t3=19", "a=", "x=0"],
     hints=["The value is either a number or `null` — the program checks `=== null`.",
            "With `strictNullChecks`, `null` must be in the type: `number | null`."])

_xdz("ts_tsconfig", 2, "A tally the flag keeps honest",
     "Input is `text|queries`. It counts each word of the text, then prints the count for each query. Write `Tally`.",
     r'''
type Tally = { [word: string]: number };
const [text = "", query = ""] = input.split("|");
const tally: Tally = {};
for (const w of text.split(" ")) tally[w] = (tally[w] ?? 0) + 1;
for (const q of query.split(" ")) console.log(`${q}: ${tally[q] ?? 0}`);
''', "type Tally = { [word: string]: number };",
     "type _1 = Expect<Equal<Tally, { [word: string]: number }>>;",
     ["a b a c|a c z", "x|x y", "the cat the|the"],
     hints=["Any word can be a key, and each maps to a count.",
            "An index signature, `{ [word: string]: number }` — the flag adds `undefined` to every read, which is why `?? 0` is there."])

# ── ts_modules ───────────────────────────────────────────────────────────────

_xpr("ts_modules", 1, "Typed by the module's declaration",
     'import * as fs from "fs";\nconst text = fs.readFileSync(0, "utf8");\n', "text", "string",
     hints=["The declaration of `fs` says what `readFileSync` returns for each way of calling it.",
            "With an encoding it returns text: `string`."])

_xpr("ts_modules", 2, "An exported constant",
     "export const PORT = 8080;\nexport let retries = 3;\n", "PORT", "8080",
     hints=["`export` does not change inference: it is still a `const`.",
            "A `const` keeps its literal type: `8080`."])

_xdx("ts_modules", 1, "Patching an import",
     "TS2540: Cannot assign to 'readFileSync' because it is a read-only property.",
     r'''
function wordCount(): number {
  return fs.readFileSync(0, "utf8").trim().split(/\s+/).length;
}
fs.readFileSync = () => input;
console.log(wordCount());
''', r'''
function wordCount(read: () => string): number {
  return read().split(/\s+/).length;
}
console.log(wordCount(() => input));
''', ["a b c", "one", "x  y"],
     ask="The idea was to make `wordCount` count the text already read. Fix the cause.",
     hints=["A module namespace (`import * as fs`) is read-only — you cannot swap one of its exports.",
            "Pass the reading function in as a parameter instead."])

_xrt("ts_modules", 1, "An exported parser",
     "Each `;`-separated entry is `key=value`. Replace the `any`s — the module exports its result type as well as the function.",
     r'''
export type Pair = { key: string; value: string };
export function parsePair(text: any): any {
  const [key = "", value = ""] = text.split("=");
  return { key, value };
}
for (const entry of input.split(";")) {
  const p = parsePair(entry);
  console.log(`${p.key} -> ${p.value === "" ? "(empty)" : p.value}`);
}
''', r'''
export type Pair = { key: string; value: string };
export function parsePair(text: string): Pair {
  const [key = "", value = ""] = text.split("=");
  return { key, value };
}
for (const entry of input.split(";")) {
  const p = parsePair(entry);
  console.log(`${p.key} -> ${p.value === "" ? "(empty)" : p.value}`);
}
''', "type _1 = Expect<Equal<ReturnType<typeof parsePair>, { key: string; value: string }>>;\n"
     "type _2 = Expect<Equal<Parameters<typeof parsePair>, [text: string]>>;",
     ["a=1;b=2", "name=", "x=y=z"],
     hints=["The file already exports the result's shape.",
            "Take a `string`, return a `Pair`."])

_xrt("ts_modules", 2, "Pass the reader in",
     "Rather than calling `fs` itself, `summary` is handed a function that returns the text. Replace the `any`s.",
     r'''
function summary(read: any): any {
  const lines = read().split("\n");
  return `${lines.length} line(s), first: ${lines[0] ?? ""}`;
}
console.log(summary(() => input));
''', r'''
function summary(read: () => string): string {
  const lines = read().split("\n");
  return `${lines.length} line(s), first: ${lines[0] ?? ""}`;
}
console.log(summary(() => input));
''', "type _1 = Expect<Equal<Parameters<typeof summary>[0], () => string>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof summary>, string>>;",
     ["alpha\nbeta\ngamma", "solo", "a\nb"],
     hints=["`read` is called with no arguments and its result is split.",
            "`() => string` — a stand-in for the module's reader, easy to substitute in a test."])

_xrt("ts_modules", 3, "A default export",
     "The file's default export averages some numbers. Replace the `any`s.",
     r'''
export default function average(xs: any): any {
  return xs.length === 0 ? 0 : xs.reduce((s: any, x: any) => s + x, 0) / xs.length;
}
const nums = input.split(" ").filter((t) => t !== "").map(Number);
console.log(average(nums).toFixed(2));
''', r'''
export default function average(xs: readonly number[]): number {
  return xs.length === 0 ? 0 : xs.reduce((s, x) => s + x, 0) / xs.length;
}
const nums = input.split(" ").filter((t) => t !== "").map(Number);
console.log(average(nums).toFixed(2));
''', "type _1 = Expect<Equal<ReturnType<typeof average>, number>>;\n"
     "type _2 = Expect<Equal<Parameters<typeof average>[0] extends readonly number[] ? true : false, true>>;\n"
     "type _3 = Expect<Equal<IsAny<Parameters<typeof average>[0]>, false>>;",
     ["2 4 9", "5", "1 2"],
     hints=["A default export is typed exactly like any other function.",
            "It takes a list of numbers (`readonly number[]` or `number[]`) and returns a `number`."])

_xdz("ts_modules", 1, "An exported money type",
     "Each `;`-separated entry is `amount currency`. Write the exported `Money` type from how the exported functions use it.",
     r'''
export type Money = { amount: number; currency: string };
export function parseMoney(text: string): Money {
  const [amount = "0", currency = "?"] = text.trim().split(" ");
  return { amount: Number(amount), currency };
}
export function show(m: Money): string {
  return `${m.amount.toFixed(2)} ${m.currency}`;
}
console.log(input.split(";").map(parseMoney).map(show).join(" | "));
''', "export type Money = { amount: number; currency: string };",
     "type _1 = Expect<Equal<Money, { amount: number; currency: string }>>;",
     ["12.5 EUR;3 USD", "7 JPY", "0.1 GBP; 2 GBP"],
     hints=["`amount` goes through `Number` and `.toFixed`; `currency` is a word.",
            "`export type Money = { amount: number; currency: string };`"])

_xdz("ts_modules", 2, "The unit a module accepts",
     "Input is `value unit` with unit `c` or `f`; it converts to the OTHER unit. Write the exported `Unit`.",
     r'''
export type Unit = "c" | "f";
export function convert(value: number, to: Unit): number {
  return to === "f" ? (value * 9) / 5 + 32 : ((value - 32) * 5) / 9;
}
const [raw = "0", from = "c"] = input.split(" ");
const to: Unit = from === "c" ? "f" : "c";
console.log(`${convert(Number(raw), to).toFixed(1)}${to}`);
''', 'export type Unit = "c" | "f";',
     "type _1 = Expect<Equal<Unit, \"c\" | \"f\">>;",
     ["20 c", "68 f", "-40 c"],
     hints=["Exactly two units, compared with `===`.",
            "A union of two string literals."])

_xdz("ts_modules", 3, "What the namespace holds",
     "`math` stands in for a namespace import (`import * as math from \"./math\"`). Write `MathModule`, the type of what that module exports.",
     r'''
type MathModule = { add(a: number, b: number): number; readonly PI: number };
const math: MathModule = { add: (a, b) => a + b, PI: 3.14159 };
const [a = 0, b = 0] = input.split(" ").map(Number);
console.log(math.add(a, b), (math.PI * a).toFixed(2));
''', "type MathModule = { add(a: number, b: number): number; readonly PI: number };",
     "type _1 = Expect<Equal<MathModule, { add(a: number, b: number): number; readonly PI: number }>>;",
     ["2 3", "1 0", "10 -4"],
     hints=["One function export and one constant export; a namespace's properties are read-only.",
            "`{ add(a: number, b: number): number; readonly PI: number }`."])

_xfx("ts_modules", 1, "State that outlives the call",
     "Each `;`-separated line should print its words with repeats removed. From the second line on, words are missing.",
     r'''
const seen = new Set<string>();
export function unique(words: string[]): string[] {
  return words.filter((w) => {
    if (seen.has(w)) return false;
    seen.add(w);
    return true;
  });
}
for (const line of input.split(";")) console.log(unique(line.split(" ")).join(" "));
''', r'''
export function unique(words: string[]): string[] {
  const seen = new Set<string>();
  return words.filter((w) => {
    if (seen.has(w)) return false;
    seen.add(w);
    return true;
  });
}
for (const line of input.split(";")) console.log(unique(line.split(" ")).join(" "));
''', ["a b a;b c b", "x x", "p q;q p;r"],
     hints=["Module-level variables are created once and shared by every call.",
            "Make `seen` local to `unique`."])

_xfx("ts_modules", 2, "An exported default, changed by a caller",
     "Each `;`-separated line is words, optionally prefixed with `!` to shout that line only. After one `!` line, every later line shouts too.",
     r'''
export const DEFAULTS = { sep: ",", upper: false };
function format(words: string[], opts: { sep: string; upper: boolean }): string {
  const out = words.join(opts.sep);
  return opts.upper ? out.toUpperCase() : out;
}
for (const line of input.split(";")) {
  const opts = DEFAULTS;
  if (line.startsWith("!")) opts.upper = true;
  console.log(format(line.replace("!", "").split(" "), opts));
}
''', r'''
export const DEFAULTS = { sep: ",", upper: false };
function format(words: string[], opts: { sep: string; upper: boolean }): string {
  const out = words.join(opts.sep);
  return opts.upper ? out.toUpperCase() : out;
}
for (const line of input.split(";")) {
  const opts = { ...DEFAULTS };
  if (line.startsWith("!")) opts.upper = true;
  console.log(format(line.replace("!", "").split(" "), opts));
}
''', ["a b;!c d;e f", "x y", "!p;q"],
     hints=["`const opts = DEFAULTS` does not copy — it is the exported object itself.",
            "Copy it (`{ ...DEFAULTS }`) before changing it."])

# ── ts_declaration_files ─────────────────────────────────────────────────────
