# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Practice families (TS_MASTERY_ROADMAP.md X-19): five variations of one
# problem, each twisting a single dimension — the input's shape, the output's
# format, an edge case, a rule, a generalisation — so the pattern is learnt
# rather than the one answer. Optional practice, outside the gate; outputs
# computed from the references. exec()'d by gen_seed.py before
# mastery_ts_attach.py.
# ---------------------------------------------------------------------------


def _family(week, fid, title, variants):
    """`variants`: five (twist, prompt, body, inputs); `body` follows the
    stdin scaffold, exactly like a problem-set problem."""
    assert len(variants) == 5, f"{fid}: a family has five variations"
    strictness = _week_strictness(week)
    for n, (twist, prompt, body, inputs) in enumerate(variants, start=1):
        eid = f"tsm-w{week}-fam-{fid}-{n}"
        solution = _TS_SCAFFOLD + body.strip("\n") + "\n"
        lead = "The base problem." if n == 1 else f"Twist {n - 1}: {twist}."
        TS_PRACTICE_MORE.setdefault(week, []).append({
            "id": eid, "title": f"{title} ({n}/5){'' if n == 1 else ' — ' + twist}",
            "prompt": f"{lead} {prompt}",
            "hint": "", "hints": [],
            "language": "typescript", "kind": "challenge", "difficulty": "Easy" if n <= 2 else "Medium",
            "strictness": strictness, "harness": "", "judge_mode": "", "forbid": [],
            "starter": _TS_SCAFFOLD + "____\n", "solution": solution,
            "tests": _computed(eid, solution, inputs, strictness),
            "source_slug": "", "dataset": "",
        })


_family(1, "temps", "Temperature table", [
    ("", "The input is a temperature in Celsius. Print it in Fahrenheit with one decimal (`F = C × 9/5 + 32`).",
     r'''
const c = Number(input);
console.log(((c * 9) / 5 + 32).toFixed(1));
''', ["100", "0", "-40", "36.6"]),
    ("many values", "The input is several Celsius values on one line. Print each in Fahrenheit, one decimal, one per line.",
     r'''
for (const t of input.split(/\s+/)) console.log(((Number(t) * 9) / 5 + 32).toFixed(1));
''', ["0 100 -40", "21.5"]),
    ("labelled output", "Several Celsius values again; print each as `<C>C -> <F>F`, both with one decimal.",
     r'''
for (const t of input.split(/\s+/)) {
  const c = Number(t);
  console.log(`${c.toFixed(1)}C -> ${((c * 9) / 5 + 32).toFixed(1)}F`);
}
''', ["0 37.5", "-10"]),
    ("either unit", "Each value now carries its unit: `100C` or `212F`. Convert each to the other unit, one decimal, printed with the new unit's letter.",
     r'''
for (const t of input.split(/\s+/)) {
  const unit = t.slice(-1);
  const v = Number(t.slice(0, -1));
  console.log(unit === "C" ? `${((v * 9) / 5 + 32).toFixed(1)}F` : `${(((v - 32) * 5) / 9).toFixed(1)}C`);
}
''', ["100C 212F -40C 98.6F", "0F"]),
    ("summary", "Several Celsius values; print only the lowest and highest in Fahrenheit: `min <F> max <F>`, one decimal each.",
     r'''
const fs2 = input.split(/\s+/).map((t) => (Number(t) * 9) / 5 + 32);
console.log(`min ${Math.min(...fs2).toFixed(1)} max ${Math.max(...fs2).toFixed(1)}`);
''', ["0 100 -40 20", "5"]),
])

_family(2, "grades", "Grade bands", [
    ("", "The input is a score from 0 to 100. Print its letter: `A` for 90+, `B` for 80+, `C` for 70+, `D` for 60+, otherwise `F`.",
     r'''
const s = Number(input);
console.log(s >= 90 ? "A" : s >= 80 ? "B" : s >= 70 ? "C" : s >= 60 ? "D" : "F");
''', ["95", "80", "79", "59", "100"]),
    ("bad input", "Now a score may be out of range: print `invalid` for anything below 0 or above 100.",
     r'''
const s = Number(input);
if (s < 0 || s > 100) console.log("invalid");
else console.log(s >= 90 ? "A" : s >= 80 ? "B" : s >= 70 ? "C" : s >= 60 ? "D" : "F");
''', ["101", "-5", "70", "0"]),
    ("many scores", "The input is several scores on one line. Print their letters on one line, separated by spaces.",
     r'''
const letter = (s: number) => (s >= 90 ? "A" : s >= 80 ? "B" : s >= 70 ? "C" : s >= 60 ? "D" : "F");
console.log(input.split(/\s+/).map((t) => letter(Number(t))).join(" "));
''', ["90 85 60 12", "71"]),
    ("a tally", "Several scores; print how many got each letter, as `A:<n> B:<n> C:<n> D:<n> F:<n>`.",
     r'''
const letter = (s: number) => (s >= 90 ? "A" : s >= 80 ? "B" : s >= 70 ? "C" : s >= 60 ? "D" : "F");
const counts: Record<string, number> = { A: 0, B: 0, C: 0, D: 0, F: 0 };
for (const t of input.split(/\s+/)) counts[letter(Number(t))] = (counts[letter(Number(t))] ?? 0) + 1;
console.log(Object.entries(counts).map(([k, n]) => `${k}:${n}`).join(" "));
''', ["90 85 60 12 99 70", "100"]),
    ("plus and minus", "Several scores; now a letter (except `F`) gets `+` when the last digit is 7 or more and `-` when it is 2 or less. 100 is `A+`.",
     r'''
const letter = (s: number) => (s >= 90 ? "A" : s >= 80 ? "B" : s >= 70 ? "C" : s >= 60 ? "D" : "F");
const graded = (s: number): string => {
  const base = letter(s);
  if (base === "F") return base;
  if (s === 100) return "A+";
  const d = s % 10;
  return base + (d >= 7 ? "+" : d <= 2 ? "-" : "");
};
console.log(input.split(/\s+/).map((t) => graded(Number(t))).join(" "));
''', ["97 91 88 72 60 55 100 83", "65"]),
])

_family(3, "digits", "Digit work", [
    ("", "The input is a non-negative integer. Print the sum of its digits.",
     r'''
let n = Number(input);
let sum = 0;
do {
  sum += n % 10;
  n = Math.floor(n / 10);
} while (n > 0);
console.log(sum);
''', ["12345", "0", "9999"]),
    ("a different fold", "Print the product of the non-zero digits instead (a number with no non-zero digits gives 1).",
     r'''
let n = Number(input);
let product = 1;
while (n > 0) {
  const d = n % 10;
  if (d !== 0) product *= d;
  n = Math.floor(n / 10);
}
console.log(product);
''', ["105", "7", "0"]),
    ("repeat until done", "Sum the digits again and again until one digit is left, printing every step: `38 -> 11 -> 2`. A single digit prints just itself.",
     r'''
let n = Number(input);
const steps = [n];
while (n >= 10) {
  let sum = 0;
  for (let m = n; m > 0; m = Math.floor(m / 10)) sum += m % 10;
  n = sum;
  steps.push(n);
}
console.log(steps.join(" -> "));
''', ["38", "5", "9875"]),
    ("another base", "The input is `n b`: sum the digits of `n` written in base `b` (2 to 16).",
     r'''
const [nText, bText] = input.split(/\s+/);
let n = Number(nText);
const b = Number(bText);
let sum = 0;
while (n > 0) {
  sum += n % b;
  n = Math.floor(n / b);
}
console.log(sum);
''', ["10 2", "255 16", "0 7"]),
    ("pick the winner", "The input is several numbers; print the one with the largest digit sum (the first, on a tie).",
     r'''
const digitSum = (n: number): number => {
  let sum = 0;
  for (let m = n; m > 0; m = Math.floor(m / 10)) sum += m % 10;
  return sum;
};
let best = -1;
let bestSum = -1;
for (const t of input.split(/\s+/)) {
  const n = Number(t);
  if (digitSum(n) > bestSum) {
    best = n;
    bestSum = digitSum(n);
  }
}
console.log(best);
''', ["19 91 28 1000", "7"]),
])

_family(4, "cases", "Word styles", [
    ("", "The input is words separated by single spaces. Print them in Title Case (each word's first letter upper-case, the rest lower-case).",
     r'''
console.log(input.split(" ").map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" "));
''', ["the quick brown fox", "hELLO wORLD"]),
    ("snake to camel", "The input is a `snake_case` name. Print it in `camelCase`.",
     r'''
console.log(input.replace(/_([a-z])/g, (_m, c: string) => c.toUpperCase()));
''', ["user_first_name", "a_b", "single"]),
    ("camel to kebab", "The input is a `camelCase` name. Print it in `kebab-case`.",
     r'''
console.log(input.replace(/[A-Z]/g, (c) => "-" + c.toLowerCase()));
''', ["userFirstName", "x", "parseHTTPBody"]),
    ("inside out", "Reverse the letters of each word but keep the words in their order.",
     r'''
console.log(input.split(" ").map((w) => [...w].reverse().join("")).join(" "));
''', ["hello world ab", "racecar"]),
    ("acronym", "Print the acronym: the first letter of each word, upper-cased — skipping the words `and`, `of` and `the`.",
     r'''
const SKIP = new Set(["and", "of", "the"]);
console.log(
  input
    .split(" ")
    .filter((w) => !SKIP.has(w.toLowerCase()))
    .map((w) => w.charAt(0).toUpperCase())
    .join(""),
);
''', ["bank of the west", "portable network graphics", "salt and pepper"]),
])

_family(5, "tips", "Tip calculator", [
    ("", "The input is `bill percent`. Print `tip <tip> total <total>`, both with two decimals.",
     r'''
const [bill, pct] = input.split(/\s+/).map(Number);
const tip = (bill * pct) / 100;
console.log(`tip ${tip.toFixed(2)} total ${(bill + tip).toFixed(2)}`);
''', ["50 20", "19.99 15"]),
    ("a default", "The percentage may now be left out: it defaults to 15. Write a function with a default parameter.",
     r'''
function tipFor(bill: number, pct = 15): { tip: number; total: number } {
  const tip = (bill * pct) / 100;
  return { tip, total: bill + tip };
}
const [billText, pctText] = input.split(/\s+/);
const { tip, total } = pctText === undefined ? tipFor(Number(billText)) : tipFor(Number(billText), Number(pctText));
console.log(`tip ${tip.toFixed(2)} total ${total.toFixed(2)}`);
''', ["80", "80 10"]),
    ("splitting it", "An optional third number is how many people share the bill. Also print `each <amount>` (two decimals) when it is given.",
     r'''
function tipFor(bill: number, pct = 15, people?: number): string {
  const tip = (bill * pct) / 100;
  const total = bill + tip;
  const base = `tip ${tip.toFixed(2)} total ${total.toFixed(2)}`;
  return people === undefined ? base : `${base} each ${(total / people).toFixed(2)}`;
}
const [b, p, n] = input.split(/\s+/).map(Number);
console.log(tipFor(b, p, n));
''', ["100 18 4", "60 15"]),
    ("round it up", "`bill percent` again, but the total is rounded up to a whole number; print `total <n> tip <effective %>` with the effective percentage to one decimal.",
     r'''
const [bill, pct] = input.split(/\s+/).map(Number);
const total = Math.ceil(bill + (bill * pct) / 100);
console.log(`total ${total} tip ${(((total - bill) / bill) * 100).toFixed(1)}%`);
''', ["47.5 15", "100 10"]),
    ("any number of bills", "The first number is the percentage; the rest are separate bills. Print each bill's tip (two decimals, space-separated), then `sum <all tips>`. Use a rest parameter.",
     r'''
function tips(pct: number, ...bills: number[]): number[] {
  return bills.map((b) => (b * pct) / 100);
}
const [pct, ...bills] = input.split(/\s+/).map(Number);
const each = tips(pct, ...bills);
console.log(`${each.map((t) => t.toFixed(2)).join(" ")} sum ${each.reduce((a, b) => a + b, 0).toFixed(2)}`);
''', ["15 10 20 30.5", "20 5"]),
])

_family(7, "positions", "Array positions", [
    ("", "The input is a list of numbers. Print the index of the largest (the first, if it repeats).",
     r'''
const xs = input.split(/\s+/).map(Number);
console.log(xs.indexOf(Math.max(...xs)));
''', ["3 9 2 9", "5", "-1 -7"]),
    ("every match", "Print every index where the largest value appears, space-separated.",
     r'''
const xs = input.split(/\s+/).map(Number);
const max = Math.max(...xs);
console.log(xs.flatMap((x, i) => (x === max ? [i] : [])).join(" "));
''', ["3 9 2 9", "5"]),
    ("the runner-up", "Print the second largest *distinct* value, or `none` if there is only one distinct value.",
     r'''
const distinct = [...new Set(input.split(/\s+/).map(Number))].toSorted((a, b) => b - a);
console.log(distinct.length > 1 ? distinct[1] : "none");
''', ["3 9 2 9", "4 4", "1 2"]),
    ("rotation", "The first number is `k`; rotate the rest left by `k` places (`k` may be larger than the list) and print them.",
     r'''
const [k, ...xs] = input.split(/\s+/).map(Number);
const s = xs.length === 0 ? 0 : k % xs.length;
console.log([...xs.slice(s), ...xs.slice(0, s)].join(" "));
''', ["2 1 2 3 4 5", "7 1 2 3", "0 9"]),
    ("differences", "Print the difference between each number and the next (`next - current`), space-separated; a single number prints nothing.",
     r'''
const xs = input.split(/\s+/).map(Number);
console.log(xs.slice(1).map((x, i) => x - xs[i]).join(" "));
''', ["1 4 9 16", "5", "10 7 7"]),
])

_TW_STAFF = '[{"name":"ana","dept":"eng","salary":120},{"name":"bo","dept":"ops","salary":90},{"name":"cy","dept":"eng","salary":150},{"name":"di","dept":"ops","salary":95},{"name":"ed","dept":"hr","salary":70}]'
_TW_STAFF2 = '[{"name":"fay","dept":"eng","salary":100},{"name":"gus","dept":"eng"},{"name":"hal","dept":"hr"}]'

_family(8, "staff", "Staff records", [
    ("", "The input is a JSON array of `{ name, dept, salary }`. Print the total salary.",
     r'''
type Person = { name: string; dept: string; salary: number };
const staff: Person[] = JSON.parse(input);
console.log(staff.reduce((sum, p) => sum + p.salary, 0));
''', [_TW_STAFF]),
    ("grouped", "Print the total per department, one `dept: total` line each, departments in alphabetical order.",
     r'''
type Person = { name: string; dept: string; salary: number };
const staff: Person[] = JSON.parse(input);
const totals: Record<string, number> = {};
for (const p of staff) totals[p.dept] = (totals[p.dept] ?? 0) + p.salary;
for (const dept of Object.keys(totals).sort()) console.log(`${dept}: ${totals[dept]}`);
''', [_TW_STAFF]),
    ("the top of each group", "Print the best-paid person per department, `dept: name`, departments in alphabetical order.",
     r'''
type Person = { name: string; dept: string; salary: number };
const staff: Person[] = JSON.parse(input);
const best: Record<string, Person> = {};
for (const p of staff) {
  const cur = best[p.dept];
  if (cur === undefined || p.salary > cur.salary) best[p.dept] = p;
}
for (const dept of Object.keys(best).sort()) console.log(`${dept}: ${best[dept]?.name}`);
''', [_TW_STAFF]),
    ("JSON out", "Print a JSON object mapping each department to its head count, keys in alphabetical order (no spaces).",
     r'''
type Person = { name: string; dept: string; salary: number };
const staff: Person[] = JSON.parse(input);
const counts: Record<string, number> = {};
for (const dept of staff.map((p) => p.dept).sort()) counts[dept] = (counts[dept] ?? 0) + 1;
console.log(JSON.stringify(counts));
''', [_TW_STAFF]),
    ("missing fields", "Some records have no `salary`. Count it as 0 in the total, print `total <n>`, then `missing: <names>` (comma-separated, input order) or `missing: none`.",
     r'''
type Person = { name: string; dept: string; salary?: number };
const staff: Person[] = JSON.parse(input);
const total = staff.reduce((sum, p) => sum + (p.salary ?? 0), 0);
const missing = staff.filter((p) => p.salary === undefined).map((p) => p.name);
console.log(`total ${total}`);
console.log(`missing: ${missing.length ? missing.join(",") : "none"}`);
''', [_TW_STAFF2, _TW_STAFF]),
])

_family(9, "sets", "Set talk", [
    ("", "Two lines of words. Print the words that appear in both, in alphabetical order, space-separated (or `none`).",
     r'''
const [a = "", b = ""] = input.split("\n");
const second = new Set(b.split(/\s+/));
const both = [...new Set(a.split(/\s+/))].filter((w) => second.has(w)).sort();
console.log(both.length ? both.join(" ") : "none");
''', ["red green blue\nblue yellow red", "a b\nc d"]),
    ("one side only", "Print the words in the first line that are not in the second, alphabetical (or `none`).",
     r'''
const [a = "", b = ""] = input.split("\n");
const second = new Set(b.split(/\s+/));
const only = [...new Set(a.split(/\s+/))].filter((w) => !second.has(w)).sort();
console.log(only.length ? only.join(" ") : "none");
''', ["red green blue\nblue yellow red", "a b\na b"]),
    ("either but not both", "Print the words in exactly one of the two lines, alphabetical (or `none`).",
     r'''
const [a = "", b = ""] = input.split("\n");
const x = new Set(a.split(/\s+/));
const y = new Set(b.split(/\s+/));
const out = [...x].filter((w) => !y.has(w)).concat([...y].filter((w) => !x.has(w))).sort();
console.log(out.length ? out.join(" ") : "none");
''', ["red green blue\nblue yellow red", "a b\nb a"]),
    ("a score", "Print the Jaccard similarity of the two word sets — shared words divided by all distinct words — with two decimals.",
     r'''
const [a = "", b = ""] = input.split("\n");
const x = new Set(a.split(/\s+/));
const y = new Set(b.split(/\s+/));
const shared = [...x].filter((w) => y.has(w)).length;
const all = new Set([...x, ...y]).size;
console.log((shared / all).toFixed(2));
''', ["red green blue\nblue yellow red", "a b\nc d", "same\nsame"]),
    ("many lines", "Any number of lines now. For each distinct word, print `word <number of lines containing it>`, words in alphabetical order.",
     r'''
const counts = new Map<string, number>();
for (const line of input.split("\n")) {
  for (const w of new Set(line.split(/\s+/))) counts.set(w, (counts.get(w) ?? 0) + 1);
}
for (const w of [...counts.keys()].sort()) console.log(`${w} ${counts.get(w)}`);
''', ["red green\ngreen blue red\nred", "x"]),
])


def _type_family(week, fid, title, variants, prelude=""):
    """Five type-level variations: (twist, prompt, full, blank, checks). The
    hidden `prelude` (e.g. a `Flat<T>` helper) goes before every check."""
    assert len(variants) == 5, f"{fid}: a family has five variations"
    for n, (twist, prompt, full, blank, checks) in enumerate(variants, start=1):
        ex = _tsp_types(week, f"tsm-w{week}-fam-{fid}-{n}", "", "warm-up" if n <= 2 else "core",
                        prompt, full, blank, prelude + checks)
        lead = "The base problem." if n == 1 else f"Twist {n - 1}: {twist}."
        ex["title"] = f"{title} ({n}/5){'' if n == 1 else ' — ' + twist}"
        ex["prompt"] = f"{lead} {prompt}"
        TS_PRACTICE_MORE.setdefault(week, []).append(ex)


_FAM_SETTINGS = r'''
const settings = new Map<string, string>();
for (const line of input.split("\n")) {
  const [k = "", v = ""] = line.split("=");
  if (k.trim()) settings.set(k.trim(), v.trim());
}
'''

_FAM_SOURCES = r'''
const parse = (line: string | undefined): Map<string, string> => {
  const m = new Map<string, string>();
  for (const pair of (line ?? "").split(",")) {
    const [k = "", v = ""] = pair.split("=");
    if (k.trim()) m.set(k.trim(), v.trim());
  }
  return m;
};
const [fileLine, envLine] = input.split("\n");
const file = parse(fileLine);
const env = parse(envLine);
'''

_family(11, "settings", "Optional settings", [
    ("", "Each input line is `key=value`. Print `port <value>` — or `port 3000` when no `port` line is given.",
     _FAM_SETTINGS + r'''
console.log(`port ${settings.get("port") ?? "3000"}`);
''', ["port=8080\nhost=x", "host=x"]),
    ("check it", "Now the port must be a whole number from 1 to 65535: print `invalid port <raw text>` otherwise (still `port 3000` when absent).",
     _FAM_SETTINGS + r'''
const raw = settings.get("port");
if (raw === undefined) console.log("port 3000");
else {
  const n = Number(raw);
  console.log(Number.isInteger(n) && n >= 1 && n <= 65535 ? `port ${n}` : `invalid port ${raw}`);
}
''', ["port=8080", "port=99999", "port=eighty", "host=x"]),
    ("zero is a value", "Print `retries <n>` from a `retries` line, defaulting to 3 — and `retries=0` means zero retries, not the default.",
     _FAM_SETTINGS + r'''
const r = settings.get("retries");
console.log(`retries ${r === undefined ? 3 : Number(r)}`);
''', ["retries=0", "retries=5", "port=80"]),
    ("two sources", "Line 1 holds the file's settings and line 2 (possibly absent) the environment's, each as comma-separated `key=value`. The environment overrides the file, which overrides the defaults `host=localhost` and `port=3000`. Print `host:port`.",
     _FAM_SOURCES + r'''
const pick = (k: string, fallback: string) => env.get(k) ?? file.get(k) ?? fallback;
console.log(`${pick("host", "localhost")}:${pick("port", "3000")}`);
''', ["host=db.local,port=5432\nport=6543", "port=80", "host=x\nhost=y,port=1"]),
    ("say where it came from", "Same two sources; print `host=<v> (<source>)` and `port=<v> (<source>)`, where the source is `env`, `file` or `default`.",
     _FAM_SOURCES + r'''
const DEFAULTS = [["host", "localhost"], ["port", "3000"]] as const;
for (const [k, fallback] of DEFAULTS) {
  const source = env.has(k) ? "env" : file.has(k) ? "file" : "default";
  console.log(`${k}=${env.get(k) ?? file.get(k) ?? fallback} (${source})`);
}
''', ["host=db.local,port=5432\nport=6543", "port=80", "x=1"]),
])

_FAM_SHAPE = r'''
type Shape = { kind: "circle"; r: number } | { kind: "rect"; w: number; h: number };
const parse = (line: string): Shape => {
  const [k, a = "0", b = "0"] = line.trim().split(/\s+/);
  return k === "circle" ? { kind: "circle", r: Number(a) } : { kind: "rect", w: Number(a), h: Number(b) };
};
const area = (s: Shape): number => {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.r ** 2;
    case "rect":
      return s.w * s.h;
  }
};
'''

_family(12, "shapes", "Shapes", [
    ("", "Each line is `circle r` or `rect w h`. Model them as a discriminated union and print each area with two decimals.",
     _FAM_SHAPE + r'''
for (const line of input.split("\n")) console.log(area(parse(line)).toFixed(2));
''', ["circle 1\nrect 2 3", "rect 1.5 2\ncircle 0.5"]),
    ("another measure", "Print each perimeter instead (circle `2πr`, rectangle `2(w + h)`), two decimals.",
     _FAM_SHAPE + r'''
const perimeter = (s: Shape): number => {
  switch (s.kind) {
    case "circle":
      return 2 * Math.PI * s.r;
    case "rect":
      return 2 * (s.w + s.h);
  }
};
for (const line of input.split("\n")) console.log(perimeter(parse(line)).toFixed(2));
''', ["circle 1\nrect 2 3", "rect 1.5 2"]),
    ("the biggest", "Print only the largest shape's kind and area: `rect 6.00` (the first, on a tie).",
     _FAM_SHAPE + r'''
let best: Shape | undefined;
for (const line of input.split("\n")) {
  const s = parse(line);
  if (best === undefined || area(s) > area(best)) best = s;
}
if (best) console.log(`${best.kind} ${area(best).toFixed(2)}`);
''', ["circle 1\nrect 2 3", "circle 2\nrect 3 4"]),
    ("a new kind", "Add `tri a b c` — a triangle by its sides, area by Heron's formula — and print every area with two decimals. The compiler should point you at every `switch` to update.",
     r'''
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "rect"; w: number; h: number }
  | { kind: "tri"; a: number; b: number; c: number };
const parse = (line: string): Shape => {
  const [k, x = "0", y = "0", z = "0"] = line.trim().split(/\s+/);
  if (k === "circle") return { kind: "circle", r: Number(x) };
  if (k === "tri") return { kind: "tri", a: Number(x), b: Number(y), c: Number(z) };
  return { kind: "rect", w: Number(x), h: Number(y) };
};
const area = (s: Shape): number => {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.r ** 2;
    case "rect":
      return s.w * s.h;
    case "tri": {
      const p = (s.a + s.b + s.c) / 2;
      return Math.sqrt(p * (p - s.a) * (p - s.b) * (p - s.c));
    }
  }
};
for (const line of input.split("\n")) console.log(area(parse(line)).toFixed(2));
''', ["tri 3 4 5\ncircle 1\nrect 2 2", "tri 2 2 2"]),
    ("bad lines", "Lines may be wrong now: an unknown kind, the wrong number of values, or a value that is not positive. Print `skip` for those and the area (two decimals) for the rest. Let the parser return `Shape | null`.",
     r'''
type Shape = { kind: "circle"; r: number } | { kind: "rect"; w: number; h: number };
const parse = (line: string): Shape | null => {
  const [k, ...rest] = line.trim().split(/\s+/);
  const nums = rest.map(Number);
  if (nums.some((n) => !(n > 0))) return null;
  if (k === "circle" && nums.length === 1) return { kind: "circle", r: nums[0] };
  if (k === "rect" && nums.length === 2) return { kind: "rect", w: nums[0], h: nums[1] };
  return null;
};
const area = (s: Shape): number => (s.kind === "circle" ? Math.PI * s.r ** 2 : s.w * s.h);
for (const line of input.split("\n")) {
  const s = parse(line);
  console.log(s === null ? "skip" : area(s).toFixed(2));
}
''', ["circle 1\nhex 2\nrect 2\nrect -1 2\nrect 2 3", "circle x"]),
])

_FLAT = "type Flat<T> = { [P in keyof T]: T[P] };\ntype User = { id: number; name: string; email: string; age?: number };\n"

_type_family(17, "keys", "Change some keys", [
    ("", "Write `Optional<T, K extends keyof T>`: `T` with the keys in `K` made optional and every other key unchanged — built from utility types.",
     "type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;", "Omit<T, K> & Partial<Pick<T, K>>",
     'type _1 = Expect<Equal<Flat<Optional<User, "email">>, { id: number; name: string; email?: string; age?: number }>>;\n'
     'type _2 = Expect<Equal<Flat<Optional<User, "id" | "name">>, { id?: number; name?: string; email: string; age?: number }>>;\n'),
    ("the other way", "Write `RequiredKeys<T, K extends keyof T>`: the keys in `K` become required.",
     "type RequiredKeys<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;", "Omit<T, K> & Required<Pick<T, K>>",
     'type _1 = Expect<Equal<Flat<RequiredKeys<User, "age">>, { id: number; name: string; email: string; age: number }>>;\n'),
    ("lock them", "Write `ReadonlyKeys<T, K extends keyof T>`: the keys in `K` become `readonly`, the rest stay writable.",
     "type ReadonlyKeys<T, K extends keyof T> = Omit<T, K> & Readonly<Pick<T, K>>;", "Omit<T, K> & Readonly<Pick<T, K>>",
     'type _1 = Expect<Equal<Flat<ReadonlyKeys<User, "id">>, { readonly id: number; name: string; email: string; age?: number }>>;\n'),
    ("one key stays", "Write `Patch<T extends { id: unknown }>`: `id` required, every other key optional — the shape of an update request.",
     'type Patch<T extends { id: unknown }> = Pick<T, "id"> & Partial<Omit<T, "id">>;', 'Pick<T, "id"> & Partial<Omit<T, "id">>',
     'type _1 = Expect<Equal<Flat<Patch<User>>, { id: number; name?: string; email?: string; age?: number }>>;\n'),
    ("keys that may not exist", "Write `Summary<T>`: only `T`'s `id` and `name` keys — whichever of them `T` has.",
     'type Summary<T> = Pick<T, Extract<keyof T, "id" | "name">>;', 'Pick<T, Extract<keyof T, "id" | "name">>',
     'type _1 = Expect<Equal<Flat<Summary<User>>, { id: number; name: string }>>;\n'
     'type _2 = Expect<Equal<Flat<Summary<{ id: string; x: 1 }>>, { id: string }>>;\n'),
], prelude=_FLAT)

_EVENTS = "type Events = { click: { x: number; y: number }; key: { code: string } };\n"

_type_family(20, "handlers", "Typed handlers", [
    ("", "Write `Handlers<E>`: for each event name in `E`, a function taking that event's payload and returning `void`.",
     "type Handlers<E> = { [K in keyof E]: (event: E[K]) => void };", "{ [K in keyof E]: (event: E[K]) => void }",
     'type _1 = Expect<Equal<Handlers<Events>, { click: (event: { x: number; y: number }) => void; key: (event: { code: string }) => void }>>;\n'),
    ("all optional", "Write `MaybeHandlers<E>`: the same, but every handler optional.",
     "type MaybeHandlers<E> = { [K in keyof E]?: (event: E[K]) => void };", "{ [K in keyof E]?: (event: E[K]) => void }",
     'type _1 = Expect<Equal<MaybeHandlers<Events>, { click?: (event: { x: number; y: number }) => void; key?: (event: { code: string }) => void }>>;\n'),
    ("renamed", "Write `OnHandlers<E>`: the keys become `onClick`, `onKey`… — remap them with `as` and `Capitalize`.",
     "type OnHandlers<E> = { [K in keyof E & string as `on${Capitalize<K>}`]: (event: E[K]) => void };",
     "{ [K in keyof E & string as `on${Capitalize<K>}`]: (event: E[K]) => void }",
     'type _1 = Expect<Equal<OnHandlers<Events>, { onClick: (event: { x: number; y: number }) => void; onKey: (event: { code: string }) => void }>>;\n'),
    ("did it handle it?", "Write `Checkers<E>`: each handler now returns `boolean` — whether it handled the event.",
     "type Checkers<E> = { [K in keyof E]: (event: E[K]) => boolean };", "{ [K in keyof E]: (event: E[K]) => boolean }",
     'type _1 = Expect<Equal<Checkers<Events>["key"], (event: { code: string }) => boolean>>;\n'),
    ("the other direction", "Write `Creators<E>`: for each event, a function taking its payload and returning `{ type: K; payload: E[K] }` — an action creator.",
     "type Creators<E> = { [K in keyof E]: (payload: E[K]) => { type: K; payload: E[K] } };",
     "{ [K in keyof E]: (payload: E[K]) => { type: K; payload: E[K] } }",
     'type _1 = Expect<Equal<ReturnType<Creators<Events>["click"]>, { type: "click"; payload: { x: number; y: number } }>>;\n'),
], prelude=_EVENTS)

_family(23, "counter", "A counter class", [
    ("", "Write `class Counter` with a private `#count`, an `inc()` method and a `value` getter. The input is a line of `inc` words; print the final value.",
     r'''
class Counter {
  #count = 0;
  inc(): void {
    this.#count++;
  }
  get value(): number {
    return this.#count;
  }
}
const c = new Counter();
for (const op of input.split(/\s+/)) if (op === "inc") c.inc();
console.log(c.value);
''', ["inc inc inc", "inc"]),
    ("a step", "The first token is a step size given to the constructor; each `inc` adds the step.",
     r'''
class Counter {
  #count = 0;
  readonly #step: number;
  constructor(step: number) {
    this.#step = step;
  }
  inc(): void {
    this.#count += this.#step;
  }
  get value(): number {
    return this.#count;
  }
}
const [step = "1", ...ops] = input.split(/\s+/);
const c = new Counter(Number(step));
for (const op of ops) if (op === "inc") c.inc();
console.log(c.value);
''', ["5 inc inc", "2 inc"]),
    ("more operations", "Ops are now `inc`, `dec` and `reset`; the count never goes below zero.",
     r'''
class Counter {
  #count = 0;
  inc(): void {
    this.#count++;
  }
  dec(): void {
    this.#count = Math.max(0, this.#count - 1);
  }
  reset(): void {
    this.#count = 0;
  }
  get value(): number {
    return this.#count;
  }
}
const c = new Counter();
for (const op of input.split(/\s+/)) {
  if (op === "inc") c.inc();
  else if (op === "dec") c.dec();
  else if (op === "reset") c.reset();
}
console.log(c.value);
''', ["inc inc dec dec dec inc", "inc reset inc"]),
    ("a history", "Also keep the value after every operation, exposed as a `readonly number[]`; print the history space-separated.",
     r'''
class Counter {
  #count = 0;
  readonly #history: number[] = [];
  #record(): void {
    this.#history.push(this.#count);
  }
  inc(): void {
    this.#count++;
    this.#record();
  }
  dec(): void {
    this.#count = Math.max(0, this.#count - 1);
    this.#record();
  }
  get history(): readonly number[] {
    return this.#history;
  }
}
const c = new Counter();
for (const op of input.split(/\s+/)) {
  if (op === "inc") c.inc();
  else if (op === "dec") c.dec();
}
console.log(c.history.join(" "));
''', ["inc inc dec dec dec inc", "inc"]),
    ("a limit", "Write `class BoundedCounter extends Counter` whose constructor takes a maximum; `inc()` past it stays at the maximum (override it and call `super.inc()`). The first token is the maximum.",
     r'''
class Counter {
  #count = 0;
  inc(): void {
    this.#count++;
  }
  get value(): number {
    return this.#count;
  }
}
class BoundedCounter extends Counter {
  readonly #max: number;
  constructor(max: number) {
    super();
    this.#max = max;
  }
  override inc(): void {
    if (this.value < this.#max) super.inc();
  }
}
const [max = "0", ...ops] = input.split(/\s+/);
const c = new BoundedCounter(Number(max));
for (const op of ops) if (op === "inc") c.inc();
console.log(c.value);
''', ["2 inc inc inc inc", "5 inc"]),
])

_family(26, "fetch", "Asynchronous lookups", [
    ("", "`fetchUser(id)` is an async function resolving to `user<id>`. For each id on the input line, await it in turn and print the result.",
     r'''
async function fetchUser(id: number): Promise<string> {
  return `user${id}`;
}
async function main(): Promise<void> {
  for (const t of input.split(/\s+/)) console.log(await fetchUser(Number(t)));
}
main();
''', ["1 2 3", "7"]),
    ("all at once", "Start every lookup at once and print the results joined by commas.",
     r'''
async function fetchUser(id: number): Promise<string> {
  return `user${id}`;
}
async function main(): Promise<void> {
  const users = await Promise.all(input.split(/\s+/).map((t) => fetchUser(Number(t))));
  console.log(users.join(","));
}
main();
''', ["1 2 3", "7"]),
    ("some fail", "A negative id now rejects with `Error(\"bad id <id>\")`. Print `ok <user>` or `failed <message>` for every id, in input order.",
     r'''
async function fetchUser(id: number): Promise<string> {
  if (id < 0) throw new Error(`bad id ${id}`);
  return `user${id}`;
}
async function main(): Promise<void> {
  const results = await Promise.allSettled(input.split(/\s+/).map((t) => fetchUser(Number(t))));
  for (const r of results) {
    console.log(r.status === "fulfilled" ? `ok ${r.value}` : `failed ${r.reason instanceof Error ? r.reason.message : String(r.reason)}`);
  }
}
main();
''', ["1 -2 3", "-1"]),
    ("first success", "Print the first lookup to succeed — or `none` if every one fails.",
     r'''
async function fetchUser(id: number): Promise<string> {
  if (id < 0) throw new Error(`bad id ${id}`);
  return `user${id}`;
}
async function main(): Promise<void> {
  try {
    console.log(await Promise.any(input.split(/\s+/).map((t) => fetchUser(Number(t)))));
  } catch {
    console.log("none");
  }
}
main();
''', ["-1 4 5", "-1 -2"]),
    ("two at a time", "Look the ids up with at most two in flight, and print the results in input order, comma-separated.",
     r'''
async function fetchUser(id: number): Promise<string> {
  return `user${id}`;
}
async function mapLimit<T, R>(items: readonly T[], limit: number, fn: (x: T) => Promise<R>): Promise<R[]> {
  const out: R[] = [];
  let next = 0;
  const worker = async (): Promise<void> => {
    while (next < items.length) {
      const i = next++;
      const item = items[i];
      if (item !== undefined) out[i] = await fn(item);
    }
  };
  await Promise.all([worker(), worker()].slice(0, Math.min(limit, items.length)));
  return out;
}
async function main(): Promise<void> {
  const ids = input.split(/\s+/).map(Number);
  console.log((await mapLimit(ids, 2, fetchUser)).join(","));
}
main();
''', ["1 2 3 4 5", "9"]),
])


_family(6, "ops", "A chain of operations", [
    ("", "Line 1 is a number, line 2 a list of operation names (`double`, `inc`, `square`). Apply them left to right and print the result. Keep the operations in a table of functions.",
     r'''
const OPS: Record<string, (n: number) => number> = { double: (n) => n * 2, inc: (n) => n + 1, square: (n) => n * n };
const [start = "0", names = ""] = input.split("\n");
console.log(names.split(/\s+/).reduce((acc, name) => OPS[name](acc), Number(start)));
''', ["3\ndouble inc square", "5\ninc"]),
    ("show the steps", "Print every intermediate value: `3 -> 6 -> 7 -> 49`.",
     r'''
const OPS: Record<string, (n: number) => number> = { double: (n) => n * 2, inc: (n) => n + 1, square: (n) => n * n };
const [start = "0", names = ""] = input.split("\n");
const steps = [Number(start)];
for (const name of names.split(/\s+/)) steps.push(OPS[name](steps[steps.length - 1]));
console.log(steps.join(" -> "));
''', ["3\ndouble inc square", "5\ninc"]),
    ("operations with arguments", "Operations now carry an argument: `add:5`, `mul:2`, `pow:3`. Build each function from its argument (a function returning a function).",
     r'''
const MAKERS: Record<string, (arg: number) => (n: number) => number> = {
  add: (a) => (n) => n + a,
  mul: (a) => (n) => n * a,
  pow: (a) => (n) => n ** a,
};
const [start = "0", specs = ""] = input.split("\n");
const fns = specs.split(/\s+/).map((spec) => {
  const [name, arg] = spec.split(":");
  return MAKERS[name](Number(arg));
});
console.log(fns.reduce((acc, f) => f(acc), Number(start)));
''', ["3\nadd:5 mul:2 add:-1", "2\npow:10"]),
    ("the other order", "Back to named operations, but apply them right to left — the order of mathematical composition (`f ∘ g` runs `g` first).",
     r'''
const OPS: Record<string, (n: number) => number> = { double: (n) => n * 2, inc: (n) => n + 1, square: (n) => n * n };
const [start = "0", names = ""] = input.split("\n");
console.log(names.split(/\s+/).reduceRight((acc, name) => OPS[name](acc), Number(start)));
''', ["3\ndouble inc square", "5\ninc"]),
    ("without a loop", "Left to right again, written as a recursive function `run(x, ops)` — no loop and no `reduce`.",
     r'''
const OPS: Record<string, (n: number) => number> = { double: (n) => n * 2, inc: (n) => n + 1, square: (n) => n * n };
const run = (x: number, ops: string[]): number => (ops.length === 0 ? x : run(OPS[ops[0]](x), ops.slice(1)));
const [start = "0", names = ""] = input.split("\n");
console.log(run(Number(start), names.split(/\s+/)));
''', ["3\ndouble inc square", "5\ninc"]),
])

_FAM_STATUS = r'''
const STATUSES = ["draft", "paid", "shipped", "delivered"] as const;
type Status = (typeof STATUSES)[number];
const toStatus = (s: string): Status | undefined => STATUSES.find((x) => x === s);
'''

_family(10, "status", "Order status", [
    ("", "The input is one status: `draft`, `paid`, `shipped` or `delivered`. Print its label from a `Record<Status, string>` — `Draft`, `Paid`, `On its way`, `Delivered` — or `unknown status`.",
     _FAM_STATUS + r'''
const LABEL: Record<Status, string> = { draft: "Draft", paid: "Paid", shipped: "On its way", delivered: "Delivered" };
const s = toStatus(input);
console.log(s === undefined ? "unknown status" : LABEL[s]);
''', ["shipped", "draft", "lost"]),
    ("what comes next", "Print the status that follows (or `final` after `delivered`, `unknown status` for anything else).",
     _FAM_STATUS + r'''
const s = toStatus(input);
if (s === undefined) console.log("unknown status");
else console.log(STATUSES[STATUSES.indexOf(s) + 1] ?? "final");
''', ["draft", "delivered", "x"]),
    ("allowed moves", "The input is `from to`. Print `ok` if `to` is the next status after `from`, otherwise `not allowed`.",
     _FAM_STATUS + r'''
const [from = "", to = ""] = input.split(/\s+/);
const a = toStatus(from);
const b = toStatus(to);
console.log(a !== undefined && b !== undefined && STATUSES.indexOf(b) === STATUSES.indexOf(a) + 1 ? "ok" : "not allowed");
''', ["paid shipped", "draft shipped", "delivered draft"]),
    ("a tally", "The input is a list of statuses; print the count of each, in the declared order: `draft:1 paid:0 shipped:2 delivered:0`. Ignore unknown words.",
     _FAM_STATUS + r'''
const counts = new Map<Status, number>(STATUSES.map((s) => [s, 0]));
for (const w of input.split(/\s+/)) {
  const s = toStatus(w);
  if (s !== undefined) counts.set(s, (counts.get(s) ?? 0) + 1);
}
console.log(STATUSES.map((s) => `${s}:${counts.get(s) ?? 0}`).join(" "));
''', ["shipped draft shipped oops", "paid"]),
    ("a new status", "Add `cancelled`: it can follow `draft` or `paid` only, and nothing follows it. The input is `from to`; print `ok` or `not allowed`. Keep the rules in a table keyed by status.",
     r'''
const STATUSES = ["draft", "paid", "shipped", "delivered", "cancelled"] as const;
type Status = (typeof STATUSES)[number];
const toStatus = (s: string): Status | undefined => STATUSES.find((x) => x === s);
const NEXT: Record<Status, readonly Status[]> = {
  draft: ["paid", "cancelled"],
  paid: ["shipped", "cancelled"],
  shipped: ["delivered"],
  delivered: [],
  cancelled: [],
};
const [from = "", to = ""] = input.split(/\s+/);
const a = toStatus(from);
const b = toStatus(to);
console.log(a !== undefined && b !== undefined && NEXT[a].includes(b) ? "ok" : "not allowed");
''', ["paid cancelled", "shipped cancelled", "cancelled draft", "draft paid"]),
])

_family(13, "checks", "Validators as functions", [
    ("", "A check is a function `(s: string) => string | null` — an error message or `null`. Apply `nonEmpty`, `noSpaces` and `maxLen10` to each input line and print `ok` or the first error.",
     r'''
type Check = (s: string) => string | null;
const nonEmpty: Check = (s) => (s.length === 0 ? "empty" : null);
const noSpaces: Check = (s) => (s.includes(" ") ? "has spaces" : null);
const maxLen10: Check = (s) => (s.length > 10 ? "too long" : null);
const CHECKS: Check[] = [nonEmpty, noSpaces, maxLen10];
for (const line of input.split("\n")) {
  let error: string | null = null;
  for (const check of CHECKS) {
    error = check(line);
    if (error !== null) break;
  }
  console.log(error ?? "ok");
}
''', ["alice\nhas space\nwaytoolongname", "bob"]),
    ("every error", "Print all the errors for a line, joined by `; ` (or `ok`).",
     r'''
type Check = (s: string) => string | null;
const CHECKS: Check[] = [
  (s) => (s.length === 0 ? "empty" : null),
  (s) => (s.includes(" ") ? "has spaces" : null),
  (s) => (s.length > 10 ? "too long" : null),
];
for (const line of input.split("\n")) {
  const errors = CHECKS.map((c) => c(line)).filter((e): e is string => e !== null);
  console.log(errors.length ? errors.join("; ") : "ok");
}
''', ["alice\nhas a very long space\nwaytoolongname", "bob"]),
    ("checks from settings", "Line 1 is `min=<n> max=<n>`; build `minLen(n)` and `maxLen(n)` checks with functions that return functions, then check each following line.",
     r'''
type Check = (s: string) => string | null;
const minLen = (n: number): Check => (s) => (s.length < n ? `shorter than ${n}` : null);
const maxLen = (n: number): Check => (s) => (s.length > n ? `longer than ${n}` : null);
const [header = "", ...words] = input.split("\n");
const opts = new Map(header.split(" ").map((kv) => kv.split("=")).map(([k, v]) => [k, Number(v)] as const));
const checks: Check[] = [minLen(opts.get("min") ?? 0), maxLen(opts.get("max") ?? Infinity)];
for (const w of words) {
  const error = checks.map((c) => c(w)).find((e) => e !== null);
  console.log(error ?? "ok");
}
''', ["min=3 max=8\nab\nabcdef\nabcdefghij", "min=1 max=1\nx"]),
    ("combine them", "Write `firstError(...checks: Check[]): Check` — one check made of several — and use it on each line.",
     r'''
type Check = (s: string) => string | null;
const firstError =
  (...checks: Check[]): Check =>
  (s) => {
    for (const c of checks) {
      const e = c(s);
      if (e !== null) return e;
    }
    return null;
  };
const username = firstError(
  (s) => (s.length === 0 ? "empty" : null),
  (s) => (/^[a-z]/.test(s) ? null : "must start with a letter"),
  (s) => (s.length > 10 ? "too long" : null),
);
for (const line of input.split("\n")) console.log(username(line) ?? "ok");
''', ["alice\n9lives\nwaytoolongname", "Bob"]),
    ("count the calls", "Wrap each check so a closure counts how often it runs. Check each line with the first-error rule, then print `calls: <name>=<n> …` — later checks run less often.",
     r'''
type Check = (s: string) => string | null;
const calls = new Map<string, number>();
const counted = (name: string, check: Check): Check => (s) => {
  calls.set(name, (calls.get(name) ?? 0) + 1);
  return check(s);
};
const CHECKS: Check[] = [
  counted("nonEmpty", (s) => (s.length === 0 ? "empty" : null)),
  counted("noSpaces", (s) => (s.includes(" ") ? "has spaces" : null)),
  counted("maxLen", (s) => (s.length > 10 ? "too long" : null)),
];
for (const line of input.split("\n")) {
  const error = CHECKS.reduce<string | null>((e, c) => e ?? c(line), null);
  console.log(error ?? "ok");
}
console.log(`calls: ${[...calls].map(([k, n]) => `${k}=${n}`).join(" ")}`);
''', ["alice\nhas space\nbob", "x"]),
])

_family(14, "flags", "Command-line flags", [
    ("", "The input is command-line arguments, e.g. `--port 8080 --verbose`. Print `port <n>` (default 3000) and `verbose <true|false>`.",
     r'''
const args = input.split(/\s+/);
const i = args.indexOf("--port");
console.log(`port ${i >= 0 ? (args[i + 1] ?? "3000") : "3000"}`);
console.log(`verbose ${args.includes("--verbose")}`);
''', ["--port 8080 --verbose", "--verbose", "--port 1"]),
    ("equals form", "Flags may also be written `--port=8080`. Support both forms.",
     r'''
const args = input.split(/\s+/);
let port = "3000";
let verbose = false;
for (let i = 0; i < args.length; i++) {
  const arg = args[i] ?? "";
  if (arg === "--verbose") verbose = true;
  else if (arg === "--port") port = args[++i] ?? port;
  else if (arg.startsWith("--port=")) port = arg.slice("--port=".length);
}
console.log(`port ${port}`);
console.log(`verbose ${verbose}`);
''', ["--port=8080 --verbose", "--port 1", "--verbose"]),
    ("unknown flags", "Any other flag is an error: print `unknown flag <flag>` and nothing else.",
     r'''
const args = input.split(/\s+/);
let port = "3000";
let verbose = false;
let error = "";
for (let i = 0; i < args.length && !error; i++) {
  const arg = args[i] ?? "";
  if (arg === "--verbose") verbose = true;
  else if (arg === "--port") port = args[++i] ?? port;
  else if (arg.startsWith("--port=")) port = arg.slice("--port=".length);
  else error = `unknown flag ${arg}`;
}
if (error) console.log(error);
else {
  console.log(`port ${port}`);
  console.log(`verbose ${verbose}`);
}
''', ["--port 1 --colour red", "--verbose"]),
    ("repeated flags", "Add `--tag <name>`, which may repeat. Print the port, then `tags <a,b>` (or `tags none`).",
     r'''
const args = input.split(/\s+/);
let port = "3000";
const tags: string[] = [];
for (let i = 0; i < args.length; i++) {
  const arg = args[i] ?? "";
  if (arg === "--port") port = args[++i] ?? port;
  else if (arg === "--tag") {
    const t = args[++i];
    if (t !== undefined) tags.push(t);
  }
}
console.log(`port ${port}`);
console.log(`tags ${tags.length ? tags.join(",") : "none"}`);
''', ["--tag a --port 80 --tag b", "--port 1"]),
    ("a typed result", "Parse into a typed object `{ port: number; verbose: boolean; tags: string[] }` and print it with `JSON.stringify`.",
     r'''
type Options = { port: number; verbose: boolean; tags: string[] };
function parseArgs(args: readonly string[]): Options {
  const opts: Options = { port: 3000, verbose: false, tags: [] };
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--verbose") opts.verbose = true;
    else if (arg === "--port") opts.port = Number(args[++i] ?? opts.port);
    else if (arg === "--tag") {
      const t = args[++i];
      if (t !== undefined) opts.tags.push(t);
    }
  }
  return opts;
}
console.log(JSON.stringify(parseArgs(input.split(/\s+/))));
''', ["--tag a --port 80 --verbose", "--tag x"]),
])

_FAM_PALETTE = r'''
type Rgb = { r: number; g: number; b: number };
const PALETTE = {
  red: { r: 255, g: 0, b: 0 },
  teal: { r: 0, g: 128, b: 128 },
  navy: { r: 0, g: 0, b: 128 },
  gold: { r: 255, g: 215, b: 0 },
} satisfies Record<string, Rgb>;
const hex = (c: Rgb): string => "#" + [c.r, c.g, c.b].map((n) => n.toString(16).padStart(2, "0")).join("");
'''

_family(15, "colours", "A colour palette", [
    ("", "The palette is checked with `satisfies Record<string, Rgb>`. For each colour name on the input line, print its hex code, or `unknown <name>`.",
     _FAM_PALETTE + r'''
const names: Record<string, Rgb> = PALETTE;
for (const name of input.split(/\s+/)) {
  const c = names[name];
  console.log(c === undefined ? `unknown ${name}` : hex(c));
}
''', ["red teal pink", "gold"]),
    ("from numbers", "Each input line is `r,g,b`; print the hex code.",
     _FAM_PALETTE + r'''
for (const line of input.split("\n")) {
  const [r = 0, g = 0, b = 0] = line.split(",").map(Number);
  console.log(hex({ r, g, b }));
}
''', ["255,0,0\n0,128,128", "1,2,3"]),
    ("the other way", "Each input line is a hex code `#rrggbb`; print `r,g,b`.",
     r'''
for (const line of input.split("\n")) {
  const n = Number.parseInt(line.slice(1), 16);
  console.log(`${(n >> 16) & 255},${(n >> 8) & 255},${n & 255}`);
}
''', ["#ff0000\n#008080", "#010203"]),
    ("mixing", "The input is two palette names; print the hex of their average (each channel rounded).",
     _FAM_PALETTE + r'''
const names: Record<string, Rgb> = PALETTE;
const [a = "", b = ""] = input.split(/\s+/);
const x = names[a];
const y = names[b];
if (x === undefined || y === undefined) console.log("unknown colour");
else console.log(hex({ r: Math.round((x.r + y.r) / 2), g: Math.round((x.g + y.g) / 2), b: Math.round((x.b + y.b) / 2) }));
''', ["red gold", "teal navy", "red pink"]),
    ("nearest", "The input is `r,g,b`; print the palette name nearest to it (smallest squared distance).",
     _FAM_PALETTE + r'''
const [r = 0, g = 0, b = 0] = input.split(",").map(Number);
const dist = (c: Rgb) => (c.r - r) ** 2 + (c.g - g) ** 2 + (c.b - b) ** 2;
const nearest = Object.entries(PALETTE).reduce((best, cur) => (dist(cur[1]) < dist(best[1]) ? cur : best));
console.log(nearest[0]);
''', ["250,10,10", "0,100,150", "200,200,0"]),
])

_family(16, "stock", "Immutable stock", [
    ("", "Line 1 is the stock, `apple:3,pear:2`; each further line is `sell <item> <n>` or `restock <item> <n>`. Apply them without mutating — each step returns a new `ReadonlyMap` — and print the final stock as `item:n` pairs sorted by name.",
     r'''
type Stock = ReadonlyMap<string, number>;
const parseStock = (line: string): Stock =>
  new Map(line.split(",").map((pair) => {
    const [item = "", n = "0"] = pair.split(":");
    return [item, Number(n)];
  }));
const apply = (stock: Stock, op: string): Stock => {
  const [verb, item = "", n = "0"] = op.split(" ");
  const have = stock.get(item) ?? 0;
  const next = new Map(stock);
  next.set(item, verb === "sell" ? have - Number(n) : have + Number(n));
  return next;
};
const show = (s: Stock) => [...s].toSorted(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${k}:${v}`).join(",");
const [first = "", ...ops] = input.split("\n");
console.log(show(ops.reduce(apply, parseStock(first))));
''', ["apple:3,pear:2\nsell apple 1\nrestock pear 5", "fig:1"]),
    ("no overselling", "Selling more than is in stock prints `cannot sell <item>` and leaves the stock unchanged.",
     r'''
type Stock = ReadonlyMap<string, number>;
const parseStock = (line: string): Stock =>
  new Map(line.split(",").map((pair) => {
    const [item = "", n = "0"] = pair.split(":");
    return [item, Number(n)];
  }));
const apply = (stock: Stock, op: string): Stock => {
  const [verb, item = "", n = "0"] = op.split(" ");
  const have = stock.get(item) ?? 0;
  if (verb === "sell" && Number(n) > have) {
    console.log(`cannot sell ${item}`);
    return stock;
  }
  return new Map(stock).set(item, verb === "sell" ? have - Number(n) : have + Number(n));
};
const show = (s: Stock) => [...s].toSorted(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${k}:${v}`).join(",");
const [first = "", ...ops] = input.split("\n");
console.log(show(ops.reduce(apply, parseStock(first))));
''', ["apple:3,pear:2\nsell apple 5\nsell pear 2", "fig:1\nsell fig 1"]),
    ("keep every version", "Keep the whole history as a `readonly` array of stocks. Print how many versions there are, then the first and last.",
     r'''
type Stock = ReadonlyMap<string, number>;
const parseStock = (line: string): Stock =>
  new Map(line.split(",").map((pair) => {
    const [item = "", n = "0"] = pair.split(":");
    return [item, Number(n)];
  }));
const apply = (stock: Stock, op: string): Stock => {
  const [verb, item = "", n = "0"] = op.split(" ");
  const have = stock.get(item) ?? 0;
  return new Map(stock).set(item, verb === "sell" ? have - Number(n) : have + Number(n));
};
const show = (s: Stock | undefined) =>
  s === undefined ? "" : [...s].toSorted(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${k}:${v}`).join(",");
const [first = "", ...ops] = input.split("\n");
const history: readonly Stock[] = ops.reduce<readonly Stock[]>(
  (h, op) => [...h, apply(h[h.length - 1] ?? new Map(), op)],
  [parseStock(first)],
);
console.log(history.length);
console.log(show(history[0]));
console.log(show(history.at(-1)));
''', ["apple:3,pear:2\nsell apple 1\nrestock pear 5", "fig:1"]),
    ("undo", "An `undo` line returns to the previous version (no effect at the start). Print the final stock.",
     r'''
type Stock = ReadonlyMap<string, number>;
const parseStock = (line: string): Stock =>
  new Map(line.split(",").map((pair) => {
    const [item = "", n = "0"] = pair.split(":");
    return [item, Number(n)];
  }));
const apply = (stock: Stock, op: string): Stock => {
  const [verb, item = "", n = "0"] = op.split(" ");
  const have = stock.get(item) ?? 0;
  return new Map(stock).set(item, verb === "sell" ? have - Number(n) : have + Number(n));
};
const show = (s: Stock | undefined) =>
  s === undefined ? "" : [...s].toSorted(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${k}:${v}`).join(",");
const [first = "", ...ops] = input.split("\n");
let history: readonly Stock[] = [parseStock(first)];
for (const op of ops) {
  if (op === "undo") history = history.length > 1 ? history.slice(0, -1) : history;
  else history = [...history, apply(history[history.length - 1] ?? new Map(), op)];
}
console.log(show(history.at(-1)));
''', ["apple:3,pear:2\nsell apple 1\nundo\nrestock pear 5\nundo\nundo", "fig:1\nundo"]),
    ("parse, don't trust", "Lines may be malformed. Parse each into `{ verb: \"sell\" | \"restock\"; item: string; n: number } | { error: string }` first; print `bad line: <text>` for errors and apply the rest.",
     r'''
type Stock = ReadonlyMap<string, number>;
type Op = { verb: "sell" | "restock"; item: string; n: number } | { error: string };
const parseOp = (line: string): Op => {
  const [verb, item, n] = line.split(" ");
  const qty = Number(n);
  if ((verb !== "sell" && verb !== "restock") || !item || !Number.isInteger(qty) || qty <= 0) return { error: line };
  return { verb, item, n: qty };
};
const parseStock = (line: string): Stock =>
  new Map(line.split(",").map((pair) => {
    const [item = "", n = "0"] = pair.split(":");
    return [item, Number(n)];
  }));
const show = (s: Stock) => [...s].toSorted(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${k}:${v}`).join(",");
const [first = "", ...lines] = input.split("\n");
let stock = parseStock(first);
for (const line of lines) {
  const op = parseOp(line);
  if ("error" in op) {
    console.log(`bad line: ${op.error}`);
    continue;
  }
  const have = stock.get(op.item) ?? 0;
  stock = new Map(stock).set(op.item, op.verb === "sell" ? have - op.n : have + op.n);
}
console.log(show(stock));
''', ["apple:3\nsell apple 1\nsteal apple 2\nsell apple -1\nrestock kiwi 4", "fig:1"]),
])

_family(18, "generic", "Small generic helpers", [
    ("", "Write `firstWhere<T>(xs: readonly T[], test: (x: T) => boolean): T | undefined`. Use it to print the first even number on the input line, or `none`.",
     r'''
function firstWhere<T>(xs: readonly T[], test: (x: T) => boolean): T | undefined {
  for (const x of xs) if (test(x)) return x;
  return undefined;
}
console.log(firstWhere(input.split(/\s+/).map(Number), (n) => n % 2 === 0) ?? "none");
''', ["3 7 8 10", "1 3"]),
    ("grouping", "Write `groupBy<T, K extends string | number>(xs, key)` returning a `Map<K, T[]>`; group the input words by length and print `len: words` lines, shortest first.",
     r'''
function groupBy<T, K extends string | number>(xs: readonly T[], key: (x: T) => K): Map<K, T[]> {
  const out = new Map<K, T[]>();
  for (const x of xs) {
    const k = key(x);
    out.set(k, [...(out.get(k) ?? []), x]);
  }
  return out;
}
const groups = groupBy(input.split(/\s+/), (w) => w.length);
for (const [len, words] of [...groups].toSorted((a, b) => a[0] - b[0])) console.log(`${len}: ${words.join(",")}`);
''', ["cat horse dog ox mouse", "a"]),
    ("pairs", "Write `zip<A, B>(as: readonly A[], bs: readonly B[]): [A, B][]` (as long as the shorter list). Line 1 is names, line 2 scores; print `name score` lines.",
     r'''
function zip<A, B>(as: readonly A[], bs: readonly B[]): [A, B][] {
  const out: [A, B][] = [];
  for (let i = 0; i < Math.min(as.length, bs.length); i++) {
    const a = as[i];
    const b = bs[i];
    if (a !== undefined && b !== undefined) out.push([a, b]);
  }
  return out;
}
const [names = "", scores = ""] = input.split("\n");
for (const [n, s] of zip(names.split(/\s+/), scores.split(/\s+/).map(Number))) console.log(`${n} ${s}`);
''', ["ana bo cy\n3 5 8", "x y\n1"]),
    ("the best one", "Write `maxBy<T>(xs: readonly T[], score: (x: T) => number): T | undefined` and print the longest input word (the first, on a tie).",
     r'''
function maxBy<T>(xs: readonly T[], score: (x: T) => number): T | undefined {
  let best: T | undefined;
  let bestScore = -Infinity;
  for (const x of xs) {
    if (score(x) > bestScore) {
      best = x;
      bestScore = score(x);
    }
  }
  return best;
}
console.log(maxBy(input.split(/\s+/), (w) => w.length) ?? "");
''', ["cat horse dog mouse", "a"]),
    ("chunks", "Write `chunk<T>(xs: readonly T[], size: number): T[][]` and print the input words in chunks of 3, one chunk per line, comma-separated.",
     r'''
function chunk<T>(xs: readonly T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < xs.length; i += size) out.push(xs.slice(i, i + size));
  return out;
}
for (const c of chunk(input.split(/\s+/), 3)) console.log(c.join(","));
''', ["a b c d e f g", "x"]),
])

_CFG = "const config = { server: { host: \"localhost\", port: 8080 }, flags: [\"a\", \"b\"] as const, debug: false };\ntype Config = typeof config;\n"

_type_family(19, "lookups", "Looking types up", [
    ("", "Write `ValueOf<T>`: the union of `T`'s property types.",
     "type ValueOf<T> = T[keyof T];", "T[keyof T]",
     'type _1 = Expect<Equal<ValueOf<{ a: 1; b: "x" }>, 1 | "x">>;\ntype _2 = Expect<Equal<ValueOf<{ n: number }>, number>>;\n'),
    ("one property", "Write `PropType<T, K extends keyof T>`: the type of one property.",
     "type PropType<T, K extends keyof T> = T[K];", "T[K]",
     'type _1 = Expect<Equal<PropType<Config, "debug">, boolean>>;\ntype _2 = Expect<Equal<PropType<Config, "server">, { host: string; port: number }>>;\n'),
    ("an element", "Write `ElementType<A extends readonly unknown[]>`: the type of the array's elements.",
     "type ElementType<A extends readonly unknown[]> = A[number];", "A[number]",
     'type _1 = Expect<Equal<ElementType<Config["flags"]>, "a" | "b">>;\ntype _2 = Expect<Equal<ElementType<string[]>, string>>;\n'),
    ("two levels down", "Write `PathValue<T, A extends keyof T, B extends keyof T[A]>`: the type at `T[A][B]`.",
     "type PathValue<T, A extends keyof T, B extends keyof T[A]> = T[A][B];", "T[A][B]",
     'type _1 = Expect<Equal<PathValue<Config, "server", "port">, number>>;\n'),
    ("a function's argument", "Write `FirstArg<F extends (arg: never) => unknown>`: the type of the function's first parameter.",
     "type FirstArg<F extends (arg: never) => unknown> = Parameters<F>[0];", "Parameters<F>[0]",
     'type _1 = Expect<Equal<FirstArg<(s: string) => void>, string>>;\ntype _2 = Expect<Equal<FirstArg<(n: { id: number }) => boolean>, { id: number }>>;\n'),
], prelude=_CFG)

_type_family(21, "conditionals", "Conditional types", [
    ("", "Write `IsString<T>`: `true` when `T` is a string type, otherwise `false`.",
     "type IsString<T> = T extends string ? true : false;", "T extends string ? true : false",
     'type _1 = Expect<Equal<IsString<"a">, true>>;\ntype _2 = Expect<Equal<IsString<3>, false>>;\n'),
    ("pull out a part", "Write `ElementOr<T>`: an array's element type, or `T` itself when it is not an array.",
     "type ElementOr<T> = T extends readonly (infer E)[] ? E : T;", "T extends readonly (infer E)[] ? E : T",
     'type _1 = Expect<Equal<ElementOr<number[]>, number>>;\ntype _2 = Expect<Equal<ElementOr<string>, string>>;\n'),
    ("unwrap once", "Write `UnwrapPromise<T>`: the value a promise resolves to, one level only; anything else unchanged.",
     "type UnwrapPromise<T> = T extends Promise<infer V> ? V : T;", "T extends Promise<infer V> ? V : T",
     'type _1 = Expect<Equal<UnwrapPromise<Promise<number>>, number>>;\ntype _2 = Expect<Equal<UnwrapPromise<Promise<Promise<1>>>, Promise<1>>>;\ntype _3 = Expect<Equal<UnwrapPromise<"x">, "x">>;\n'),
    ("unwrap all the way", "Write `DeepUnwrap<T>`: keep unwrapping until it is not a promise.",
     "type DeepUnwrap<T> = T extends Promise<infer V> ? DeepUnwrap<V> : T;", "T extends Promise<infer V> ? DeepUnwrap<V> : T",
     'type _1 = Expect<Equal<DeepUnwrap<Promise<Promise<1>>>, 1>>;\ntype _2 = Expect<Equal<DeepUnwrap<string>, string>>;\n'),
    ("the whole parameter list", "Write `Args<F>`: a function type's parameter list as a tuple (`never` for non-functions).",
     "type Args<F> = F extends (...args: infer A) => unknown ? A : never;", "F extends (...args: infer A) => unknown ? A : never",
     'type _1 = Expect<Equal<Args<(a: string, b: number) => void>, [a: string, b: number]>>;\ntype _2 = Expect<Equal<Args<42>, never>>;\n'),
])

_type_family(22, "templates", "Template literal types", [
    ("", "Write `EventName<T extends string>`: `\"click\"` becomes `\"onClick\"`.",
     "type EventName<T extends string> = `on${Capitalize<T>}`;", "`on${Capitalize<T>}`",
     'type _1 = Expect<Equal<EventName<"click">, "onClick">>;\ntype _2 = Expect<Equal<EventName<"a" | "b">, "onA" | "onB">>;\n'),
    ("a prefix", "Write `CssVar<T extends string>`: `\"gap\"` becomes `\"--gap\"`.",
     "type CssVar<T extends string> = `--${T}`;", "`--${T}`",
     'type _1 = Expect<Equal<CssVar<"gap">, "--gap">>;\n'),
    ("taking apart", "Write `Split<S extends string, D extends string>`: split a string type into a tuple at every `D`.",
     "type Split<S extends string, D extends string> = S extends `${infer H}${D}${infer T}` ? [H, ...Split<T, D>] : [S];",
     "S extends `${infer H}${D}${infer T}` ? [H, ...Split<T, D>] : [S]",
     'type _1 = Expect<Equal<Split<"a.b.c", ".">, ["a", "b", "c"]>>;\ntype _2 = Expect<Equal<Split<"x", ".">, ["x"]>>;\n'),
    ("putting together", "Write `Join<T extends string[], D extends string>`: the reverse of `Split`.",
     "type Join<T extends string[], D extends string> = T extends [infer H extends string, ...infer R extends string[]] ? R extends [] ? H : `${H}${D}${Join<R, D>}` : \"\";",
     "T extends [infer H extends string, ...infer R extends string[]] ? R extends [] ? H : `${H}${D}${Join<R, D>}` : \"\"",
     'type _1 = Expect<Equal<Join<["a", "b", "c"], "-">, "a-b-c">>;\ntype _2 = Expect<Equal<Join<[], "-">, "">>;\n'),
    ("trimming", "Write `TrimLeft<S extends string>`: remove leading spaces.",
     "type TrimLeft<S extends string> = S extends ` ${infer R}` ? TrimLeft<R> : S;", "S extends ` ${infer R}` ? TrimLeft<R> : S",
     'type _1 = Expect<Equal<TrimLeft<"   hi ">, "hi ">>;\ntype _2 = Expect<Equal<TrimLeft<"x">, "x">>;\n'),
])

_family(24, "gen", "Generators", [
    ("", "Write `function* range(n: number)` yielding 0 … n-1. The input is `n`; print the sum of the squares of the range.",
     r'''
function* range(n: number): Generator<number> {
  for (let i = 0; i < n; i++) yield i;
}
let sum = 0;
for (const i of range(Number(input))) sum += i * i;
console.log(sum);
''', ["4", "1", "10"]),
    ("infinite, taken", "Write an endless `naturals()` generator and `take(it, k)`; print the first `k` naturals (from 1), space-separated.",
     r'''
function* naturals(): Generator<number> {
  for (let n = 1; ; n++) yield n;
}
function* take<T>(it: Iterable<T>, k: number): Generator<T> {
  if (k <= 0) return;
  let i = 0;
  for (const x of it) {
    yield x;
    if (++i >= k) return;
  }
}
console.log([...take(naturals(), Number(input))].join(" "));
''', ["5", "1"]),
    ("filtered", "Add a generator `filter(it, test)`; print the first `k` even naturals.",
     r'''
function* naturals(): Generator<number> {
  for (let n = 1; ; n++) yield n;
}
function* filter<T>(it: Iterable<T>, test: (x: T) => boolean): Generator<T> {
  for (const x of it) if (test(x)) yield x;
}
function* take<T>(it: Iterable<T>, k: number): Generator<T> {
  if (k <= 0) return;
  let i = 0;
  for (const x of it) {
    yield x;
    if (++i >= k) return;
  }
}
console.log([...take(filter(naturals(), (n) => n % 2 === 0), Number(input))].join(" "));
''', ["5", "1"]),
    ("with iterator helpers", "Do the same — the first `k` squares of odd naturals — with iterator helpers (`filter`, `map`, `take`, `toArray`) instead of hand-written generators.",
     r'''
function* naturals(): Generator<number> {
  for (let n = 1; ; n++) yield n;
}
console.log(
  naturals()
    .filter((n) => n % 2 === 1)
    .map((n) => n * n)
    .take(Number(input))
    .toArray()
    .join(" "),
);
''', ["4", "1"]),
    ("your own iterable", "Write `class Countdown` implementing `[Symbol.iterator]` so `for…of` counts down from `n` to 1; print the values.",
     r'''
class Countdown implements Iterable<number> {
  readonly #from: number;
  constructor(from: number) {
    this.#from = from;
  }
  *[Symbol.iterator](): Generator<number> {
    for (let n = this.#from; n >= 1; n--) yield n;
  }
}
console.log([...new Countdown(Number(input))].join(" "));
''', ["5", "1"]),
])

_family(25, "errors", "Handling bad input", [
    ("", "Each line should be an integer. Parse them with a function that throws on a bad line; catch it and print `line <n>: bad number <text>` — and print `sum <total>` if every line was good.",
     r'''
function parseLine(text: string, n: number): number {
  const v = Number(text);
  if (text.trim() === "" || !Number.isInteger(v)) throw new Error(`line ${n}: bad number ${text}`);
  return v;
}
try {
  const nums = input.split("\n").map((t, i) => parseLine(t, i + 1));
  console.log(`sum ${nums.reduce((a, b) => a + b, 0)}`);
} catch (e) {
  console.log(e instanceof Error ? e.message : String(e));
}
''', ["1\n2\n3", "1\nx\n3", "4.5"]),
    ("every problem", "Report every bad line, not just the first; then print `<k> bad` or the sum.",
     r'''
const errors: string[] = [];
let sum = 0;
input.split("\n").forEach((text, i) => {
  const v = Number(text);
  if (text.trim() === "" || !Number.isInteger(v)) errors.push(`line ${i + 1}: bad number ${text}`);
  else sum += v;
});
for (const e of errors) console.log(e);
console.log(errors.length ? `${errors.length} bad` : `sum ${sum}`);
''', ["1\nx\n3\ny", "1\n2"]),
    ("no exceptions", "Return a `Result<number>` — `{ ok: true; value } | { ok: false; error }` — from the parser instead of throwing, and print the same report as before.",
     r'''
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
const parseLine = (text: string, n: number): Result<number> => {
  const v = Number(text);
  return text.trim() === "" || !Number.isInteger(v) ? { ok: false, error: `line ${n}: bad number ${text}` } : { ok: true, value: v };
};
const results = input.split("\n").map((t, i) => parseLine(t, i + 1));
let sum = 0;
let bad = 0;
for (const r of results) {
  if (r.ok) sum += r.value;
  else {
    console.log(r.error);
    bad++;
  }
}
console.log(bad ? `${bad} bad` : `sum ${sum}`);
''', ["1\nx\n3\ny", "1\n2"]),
    ("with a cause", "Stop at the first bad line, but wrap the parser's error with context: throw `new Error(\"could not total the input\", { cause })` and print the message, then `because: <cause message>`.",
     r'''
function parseLine(text: string, n: number): number {
  const v = Number(text);
  if (text.trim() === "" || !Number.isInteger(v)) throw new Error(`line ${n}: bad number ${text}`);
  return v;
}
function total(lines: readonly string[]): number {
  try {
    return lines.map((t, i) => parseLine(t, i + 1)).reduce((a, b) => a + b, 0);
  } catch (cause) {
    throw new Error("could not total the input", { cause });
  }
}
try {
  console.log(`sum ${total(input.split("\n"))}`);
} catch (e) {
  if (e instanceof Error) {
    console.log(e.message);
    if (e.cause instanceof Error) console.log(`because: ${e.cause.message}`);
  }
}
''', ["1\nx\n3", "5\n6"]),
    ("clean up anyway", "A `Log` resource prints `open` when created and `close` when disposed. Hold it with `using` around the work, so `close` prints even when a bad line throws.",
     r'''
class Log implements Disposable {
  constructor() {
    console.log("open");
  }
  [Symbol.dispose](): void {
    console.log("close");
  }
}
function run(lines: readonly string[]): void {
  using _log = new Log();
  let sum = 0;
  for (const [i, t] of lines.entries()) {
    const v = Number(t);
    if (!Number.isInteger(v)) throw new Error(`line ${i + 1}: bad number ${t}`);
    sum += v;
  }
  console.log(`sum ${sum}`);
}
try {
  run(input.split("\n"));
} catch (e) {
  console.log(e instanceof Error ? e.message : String(e));
}
''', ["1\n2", "1\nx"]),
])
