# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery, Month 1 (weeks 1-4): problem sets, runnable projects,
# extra practice and review cards for the chapters added in ts_chapters_m1.py.
#
# Scope rule (TS_MASTERY_ROADMAP X-104): a week's problems need nothing a later
# week teaches. Week 1 is straight-line code — read, convert, compute, print.
# Week 2 adds branching, week 3 loops and numbers, week 4 strings, regex and
# Unicode. Every expected output is computed from the reference solution
# (python tools/gen_ts_outputs.py). Code is in raw strings.
# ---------------------------------------------------------------------------

# ===========================================================================
# Week 1 — Values, types, inference, program I/O (no branches, no loops)
# ===========================================================================

TS_PROBLEM_SETS[1] = [
    _tsp(1, "tsm-w1-clock", "Seconds to a clock", "warm-up",
         "The input is a number of seconds `s` (0 ≤ s < 360000). Print it as `H:MM:SS` — hours unpadded, minutes and seconds always two digits.",
         r"""
const s = Number(input);
const hours = Math.floor(s / 3600);
const minutes = Math.floor((s % 3600) / 60);
const seconds = s % 60;
console.log(`${hours}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`);
""", ["3661", "0", "59", "86399", "359999", "600"],
         hints=["Hours are whole groups of 3600 seconds; `%` gives what is left over.",
                "`String(n).padStart(2, \"0\")` turns `5` into `05`."]),
    _tsp(1, "tsm-w1-kelvin", "Kelvin to everything", "warm-up",
         "The input is a temperature in kelvin. Print it in Celsius and Fahrenheit, each to exactly two decimals, as `C=<c>` and `F=<f>` on two lines. (C = K − 273.15, F = C × 9/5 + 32.)",
         r"""
const kelvin = Number(input);
const celsius = kelvin - 273.15;
const fahrenheit = celsius * 9 / 5 + 32;
console.log(`C=${celsius.toFixed(2)}`);
console.log(`F=${fahrenheit.toFixed(2)}`);
""", ["273.15", "0", "373.15", "300", "233.15"],
         hints=["Convert to Celsius first, then Fahrenheit from Celsius.", "`toFixed(2)` for exactly two decimals."]),
    _tsp(1, "tsm-w1-circle", "Circle stats", "warm-up",
         "The input is a radius. Print the circumference and the area, each to exactly three decimals, on two lines. Use `Math.PI`.",
         r"""
const r = Number(input);
console.log((2 * Math.PI * r).toFixed(3));
console.log((Math.PI * r ** 2).toFixed(3));
""", ["1", "0", "2.5", "10", "0.1"],
         hints=["`2πr` and `πr²`; `**` is the power operator."]),
    _tsp(1, "tsm-w1-mean3", "Average of three", "warm-up",
         "The input is three numbers on one line, separated by any whitespace. Print their mean to exactly two decimals.",
         r"""
const parts = input.split(/\s+/);
const a = Number(parts[0]);
const b = Number(parts[1]);
const c = Number(parts[2]);
console.log(((a + b + c) / 3).toFixed(2));
""", ["1 2 3", "10   20    30", "-1 0 2", "0.5 0.25 0.125", "100 0 0"],
         hints=["Split on `/\\s+/`, convert each token, then add before dividing."]),
    _tsp(1, "tsm-w1-bmi", "Body-mass index", "core",
         "The input is `weightKg heightCm` on one line. Print the BMI — weight divided by the square of the height **in metres** — to one decimal.",
         r"""
const parts = input.split(/\s+/);
const weight = Number(parts[0]);
const heightM = Number(parts[1]) / 100;
console.log((weight / (heightM * heightM)).toFixed(1));
""", ["70 175", "50 160", "90 190", "65.5 170.2", "120 180"],
         hints=["Convert centimetres to metres before squaring."]),
    _tsp(1, "tsm-w1-divmod", "Two kinds of division", "core",
         "The input is two integers `a b` (b ≠ 0). Print `trunc <q> <r>` where q is a/b rounded toward zero and r = a − b·q, then `floor <q> <r>` where q is a/b rounded down and r = a − b·q.",
         r"""
const parts = input.split(/\s+/);
const a = Number(parts[0]);
const b = Number(parts[1]);
const tq = Math.trunc(a / b);
const fq = Math.floor(a / b);
console.log(`trunc ${tq} ${a - b * tq}`);
console.log(`floor ${fq} ${a - b * fq}`);
""", ["7 2", "-7 2", "7 -2", "-7 -2", "6 3", "0 5"],
         hints=["`Math.trunc` rounds toward zero, `Math.floor` toward −∞. They differ only when the signs differ.",
                "Compute each remainder from its own quotient; JavaScript's `%` matches the truncating one."]),
    _tsp(1, "tsm-w1-hours", "Hours to days", "core",
         "The input is a whole number of hours. Print `<d> days <h> hours` — always the words `days` and `hours`, whatever the numbers.",
         r"""
const total = Number(input);
console.log(`${Math.floor(total / 24)} days ${total % 24} hours`);
""", ["100", "24", "5", "0", "1000"],
         hints=["Whole days are `Math.floor(total / 24)`; the rest is `total % 24`."]),
    _tsp(1, "tsm-w1-extremes", "Count, smallest, largest", "core",
         "The input is a line of numbers. Print `count <n>`, `min <x>` and `max <y>` on three lines.",
         r"""
const values = input.split(/\s+/).map(Number);
console.log(`count ${values.length}`);
console.log(`min ${Math.min(...values)}`);
console.log(`max ${Math.max(...values)}`);
""", ["3 1 2", "5", "-4 10 -40 3.5", "7 7 7"],
         hints=["`input.split(/\\s+/).map(Number)` reads a line of numbers.",
                "`Math.min(...values)` spreads the array into arguments."]),
    _tsp(1, "tsm-w1-elapsed", "Time between two clocks", "stretch",
         "The input is two times of the same day on two lines, `HH:MM:SS`, the second not earlier than the first. Print the difference as `H:MM:SS`, then the total number of seconds.",
         r"""
const lines = input.split("\n");
const a = lines[0].trim().split(":").map(Number);
const b = lines[1].trim().split(":").map(Number);
const start = a[0] * 3600 + a[1] * 60 + a[2];
const end = b[0] * 3600 + b[1] * 60 + b[2];
const diff = end - start;
const pad = (n: number) => String(n).padStart(2, "0");
console.log(`${Math.floor(diff / 3600)}:${pad(Math.floor((diff % 3600) / 60))}:${pad(diff % 60)}`);
console.log(diff);
""", ["09:15:00\n17:45:30", "00:00:00\n23:59:59", "12:00:00\n12:00:00", "08:59:59\n09:00:01"],
         hints=["Turn each time into seconds since midnight, subtract, and format back.",
                "A small arrow function `pad` saves repeating `padStart` twice."]),
    _tsp(1, "tsm-w1-unit-price", "Which pack is cheaper per 100 g?", "stretch",
         "The input is `price1 grams1 price2 grams2` on one line. Print each pack's price per 100 g as `A $x.xx` and `B $y.xx`, then `best $z.zz` — the lower of the two — and `save $d.dd`, the difference between them. All to two decimals.",
         r"""
const parts = input.split(/\s+/).map(Number);
const per100A = parts[0] / parts[1] * 100;
const per100B = parts[2] / parts[3] * 100;
console.log(`A $${per100A.toFixed(2)}`);
console.log(`B $${per100B.toFixed(2)}`);
console.log(`best $${Math.min(per100A, per100B).toFixed(2)}`);
console.log(`save $${Math.abs(per100A - per100B).toFixed(2)}`);
""", ["3.50 500 5.00 750", "2 100 2 100", "10 1000 1 90", "4.99 454 6.49 680"],
         hints=["Price per 100 g is price ÷ grams × 100.", "`Math.min` and `Math.abs` avoid needing an `if`."]),
]

TS_PROJECTS[1] = _project(
    1, "units.ts — a temperature converter",
    "Your first complete program: read one value, convert it, and print a small report in an exact format. Nothing in it needs a branch or a loop — what it needs is careful reading of the input and exact printing, which is where most week-1 wrong answers come from.",
    ["The input is one temperature in degrees Celsius, possibly with spaces around it, possibly negative or fractional.",
     "Print `Celsius: <c>`, `Fahrenheit: <f>` and `Kelvin: <k>` on three lines, each value to exactly two decimals (F = C × 9/5 + 32, K = C + 273.15).",
     "Then print `Rounded: <c>C / <f>F`, both rounded to the nearest whole degree with `Math.round`.",
     "Declare every intermediate value with `const`, and annotate only the values whose type you want pinned."],
    r"""
const celsius: number = Number(input);
const fahrenheit = celsius * 9 / 5 + 32;
const kelvin = celsius + 273.15;
console.log(`Celsius: ${celsius.toFixed(2)}`);
console.log(`Fahrenheit: ${fahrenheit.toFixed(2)}`);
console.log(`Kelvin: ${kelvin.toFixed(2)}`);
console.log(`Rounded: ${Math.round(celsius)}C / ${Math.round(fahrenheit)}F`);
""", ["20", "  -40  ", "36.6", "0", "100", "-273.15", "21.5"],
    stretch=["Add Rankine (R = K × 9/5) and Réaumur (Ré = C × 4/5).",
             "Accept the unit as a second token (`20 C`, `68 F`) — you'll have the `if` for it next week."],
)

TS_PRACTICE_MORE[1] = [
    _pr("tsm-w1-p5", "What `Number` gives back", 'const n = Number("42");\n', "n", "number",
        hints=["`Number(...)` always returns a `number` — even when the answer is `NaN`."]),
    _pr("tsm-w1-p6", "Text from stdin", 'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8").trim();\n', "input", "string",
        hints=["With the `\"utf8\"` encoding, `readFileSync` returns text."]),
    _dx("tsm-w1-d4", "Arithmetic on text",
        "error TS2362: The left-hand side of an arithmetic operation must be of type 'any', 'number', 'bigint' or an enum type.",
        _STDIN + "console.log(input * 3);\n",
        _STDIN + "console.log(Number(input) * 3);\n",
        [("4", "12"), ("-2", "-6")], ask="Print three times the number read.",
        hints=["`input` is a `string`.", "Convert it with `Number(...)` first."]),
    _fx("tsm-w1-f3", "The sum that concatenates",
        "The input is two numbers on one line. Print their sum. It prints something else.",
        _STDIN + "const parts = input.split(/\\s+/);\nconsole.log(parts[0] + parts[1]);\n",
        _STDIN + "const parts = input.split(/\\s+/);\nconsole.log(Number(parts[0]) + Number(parts[1]));\n",
        [("2 3", "5"), ("10 -4", "6")], hints=["`\"2\" + \"3\"` is `\"23\"`.", "Convert both tokens."]),
    _fx("tsm-w1-f4", "Two decimals, always",
        "Print the price with exactly two decimals. It drops trailing zeros.",
        _STDIN + "const price = Number(input);\nconsole.log(price);\n",
        _STDIN + "const price = Number(input);\nconsole.log(price.toFixed(2));\n",
        [("2.5", "2.50"), ("10", "10.00"), ("0.125", "0.13")], hints=["`console.log(2.5)` prints `2.5`.", "`toFixed(2)`."]),
]

TS_CARDS_MORE[1] = [
    ("What does `fs.readFileSync(0, \"utf8\")` return?",
     "All of standard input as one string — file descriptor 0 is stdin."),
    ("How do you read a line of numbers?",
     "`input.split(/\\s+/).map(Number)` — split on any run of whitespace, convert each token."),
    ("`split(\" \")` vs `split(/\\s+/)`?",
     "`split(\" \")` leaves empty strings where there are double spaces; `/\\s+/` treats any run of whitespace as one separator."),
    ("What does the judge ignore when comparing output?",
     "`\\r`, trailing spaces at the end of a line, and trailing blank lines. Everything else must match exactly."),
    ("Why does `console.log(2.5)` fail when `2.50` is expected?",
     "A number prints in its shortest form. `toFixed(2)` produces the string with exactly two decimals."),
    ("Why doesn't `const n: number = input` convert the input?",
     "Annotations never convert — they only check. `input` is a `string`, so it's a compile error; convert with `Number(input)`."),
]

# ===========================================================================
# Week 2 — Operators, equality and control flow (branches, no loops)
# ===========================================================================

TS_PROBLEM_SETS[2] = [
    _tsp(2, "tsm-w2-grade", "Letter grade", "warm-up",
         "The input is a score. Print `A` for 90-100, `B` for 80-89, `C` for 70-79, `D` for 60-69 and `F` below 60. Print `invalid` for anything that is not a number from 0 to 100.",
         r"""
const text = input;
const score = Number(text);
if (text === "" || Number.isNaN(score) || score < 0 || score > 100) {
  console.log("invalid");
} else if (score >= 90) {
  console.log("A");
} else if (score >= 80) {
  console.log("B");
} else if (score >= 70) {
  console.log("C");
} else if (score >= 60) {
  console.log("D");
} else {
  console.log("F");
}
""", ["95", "90", "89.5", "60", "59", "0", "100", "101", "abc", "-1"],
         hints=["Check validity first, then test the bands from the top down so each `else if` only sees what is left.",
                "`Number(\"\")` is `0` — check for empty text before converting."]),
    _tsp(2, "tsm-w2-triangle", "What kind of triangle?", "warm-up",
         "The input is three side lengths. Print `invalid` unless every side is positive and each side is shorter than the sum of the other two. Otherwise print `equilateral`, `isosceles` or `scalene`.",
         r"""
const s = input.split(/\s+/).map(Number);
const a = s[0], b = s[1], c = s[2];
if (!(a > 0 && b > 0 && c > 0) || a >= b + c || b >= a + c || c >= a + b) {
  console.log("invalid");
} else if (a === b && b === c) {
  console.log("equilateral");
} else if (a === b || b === c || a === c) {
  console.log("isosceles");
} else {
  console.log("scalene");
}
""", ["3 3 3", "3 4 5", "5 5 8", "1 2 3", "0 1 1", "2 2 3.9", "10 1 1", "-1 2 2"],
         hints=["Rule out the invalid shapes first — including the flat triangle where one side equals the sum of the others."]),
    _tsp(2, "tsm-w2-quadrant", "Where is the point?", "warm-up",
         "The input is `x y`. Print `origin`, `x-axis` or `y-axis` for points on an axis, otherwise `Q1`-`Q4` (Q1 is x>0, y>0, counting anticlockwise).",
         r"""
const p = input.split(/\s+/).map(Number);
const x = p[0], y = p[1];
if (x === 0 && y === 0) console.log("origin");
else if (y === 0) console.log("x-axis");
else if (x === 0) console.log("y-axis");
else if (x > 0) console.log(y > 0 ? "Q1" : "Q4");
else console.log(y > 0 ? "Q2" : "Q3");
""", ["1 1", "-1 1", "-1 -1", "1 -1", "0 0", "5 0", "0 -3", "-0 2"],
         hints=["Handle the axes before the quadrants.", "`-0 === 0` is `true`, which is what you want here."]),
    _tsp(2, "tsm-w2-day", "Name the day", "warm-up",
         "The input is a day number, 1 (Monday) to 7 (Sunday). Print the day's name and, on a second line, `weekend` or `weekday`. For any other input print only `invalid`.",
         r"""
const n = Number(input);
let name = "";
switch (n) {
  case 1: name = "Monday"; break;
  case 2: name = "Tuesday"; break;
  case 3: name = "Wednesday"; break;
  case 4: name = "Thursday"; break;
  case 5: name = "Friday"; break;
  case 6: name = "Saturday"; break;
  case 7: name = "Sunday"; break;
}
if (name === "") {
  console.log("invalid");
} else {
  console.log(name);
  console.log(n >= 6 ? "weekend" : "weekday");
}
""", ["1", "5", "6", "7", "0", "8", "3.5", "x"],
         hints=["A `switch` on the number, with `break` after every case."]),
    _tsp(2, "tsm-w2-shipping", "Shipping cost", "core",
         "The input is `weightKg zone express`, where zone is `domestic` or `international` and express is `yes` or `no`. Bands: up to 1 kg costs 5 (domestic) / 15 (international); up to 5 kg, 10 / 30; up to 20 kg, 20 / 60. Express doubles the price. Print the cost to two decimals, `too heavy` above 20 kg, or `invalid` for a non-positive weight or an unknown zone or express value.",
         r"""
const parts = input.split(/\s+/);
const weight = Number(parts[0]);
const zone = parts[1];
const express = parts[2];
const intl = zone === "international";
if (!(weight > 0) || (zone !== "domestic" && !intl) || (express !== "yes" && express !== "no")) {
  console.log("invalid");
} else if (weight > 20) {
  console.log("too heavy");
} else {
  let cost: number;
  if (weight <= 1) cost = intl ? 15 : 5;
  else if (weight <= 5) cost = intl ? 30 : 10;
  else cost = intl ? 60 : 20;
  if (express === "yes") cost *= 2;
  console.log(cost.toFixed(2));
}
""", ["0.5 domestic no", "1 international yes", "1.01 domestic no", "5 international no", "20 domestic yes", "20.1 domestic no", "0 domestic no", "3 mars no", "3 domestic maybe"],
         hints=["Validate every field before pricing.", "`let cost: number;` with no initialiser is fine — the compiler checks every path assigns it."]),
    _tsp(2, "tsm-w2-versions", "Compare two versions", "core",
         "The input is two versions `major.minor` on one line, e.g. `1.2 1.10`. A missing minor counts as 0. Compare them numerically — `1.10` is newer than `1.2` — and print `<`, `>` or `=`.",
         r"""
const parts = input.split(/\s+/);
const a = parts[0].split(".");
const b = parts[1].split(".");
const aMajor = Number(a[0]), aMinor = Number(a[1] ?? "0");
const bMajor = Number(b[0]), bMinor = Number(b[1] ?? "0");
if (aMajor !== bMajor) console.log(aMajor < bMajor ? "<" : ">");
else if (aMinor !== bMinor) console.log(aMinor < bMinor ? "<" : ">");
else console.log("=");
""", ["1.2 1.10", "2.0 1.99", "3 3.0", "0.1 0.1", "10.4 9.40", "1.10 1.9"],
         hints=["Compare as numbers, not strings: `\"10\" < \"9\"` is `true`.", "Majors first; only if they are equal do minors matter."]),
    _tsp(2, "tsm-w2-water", "Solid, liquid or gas", "core",
         "The input is a temperature and a unit, `C`, `F` or `K`, e.g. `212 F`. At sea level water is `solid` at or below 0 °C, `gas` at or above 100 °C, and `liquid` in between. Print the state, or `invalid unit` for any other unit.",
         r"""
const parts = input.split(/\s+/);
const value = Number(parts[0]);
const unit = parts[1];
let celsius: number | undefined;
if (unit === "C") celsius = value;
else if (unit === "F") celsius = (value - 32) * 5 / 9;
else if (unit === "K") celsius = value - 273.15;
if (celsius === undefined) console.log("invalid unit");
else if (celsius <= 0) console.log("solid");
else if (celsius >= 100) console.log("gas");
else console.log("liquid");
""", ["25 C", "212 F", "32 F", "273.15 K", "373.15 K", "-5 C", "50 X", "99.9 C"],
         hints=["Convert every unit to Celsius first; then there is only one set of thresholds.",
                "`number | undefined` lets the variable say \"no valid unit\"."]),
    _tsp(2, "tsm-w2-clamp", "Clamp a value", "core",
         "The input is `value lo hi`. Print the value clamped into `[lo, hi]`, then `low`, `high` or `inside` depending on where the original was. If `lo > hi`, print `bad range` only.",
         r"""
const p = input.split(/\s+/).map(Number);
const value = p[0], lo = p[1], hi = p[2];
if (lo > hi) {
  console.log("bad range");
} else {
  console.log(Math.min(Math.max(value, lo), hi));
  console.log(value < lo ? "low" : value > hi ? "high" : "inside");
}
""", ["5 1 10", "-3 0 7", "12 0 7", "0 0 0", "4 5 1", "7 7 9"],
         hints=["`Math.min(Math.max(v, lo), hi)` clamps in one line.", "A nested ternary reads fine when each branch is one word."]),
    _tsp(2, "tsm-w2-sign", "Sign of a product, without multiplying", "stretch",
         "The input is three numbers. Print `zero`, `positive` or `negative` for the sign of their product — without computing it (the numbers can be large enough to overflow). `-0` counts as zero.",
         r"""
const n = input.split(/\s+/).map(Number);
const a = n[0], b = n[1], c = n[2];
if (a === 0 || b === 0 || c === 0) {
  console.log("zero");
} else {
  const negatives = (a < 0 ? 1 : 0) + (b < 0 ? 1 : 0) + (c < 0 ? 1 : 0);
  console.log(negatives % 2 === 0 ? "positive" : "negative");
}
""", ["1 2 3", "-1 2 3", "-1 -2 3", "-1 -2 -3", "0 -5 7", "1e200 1e200 -1e200", "-0 4 4"],
         hints=["Any zero makes the product zero.", "Otherwise only the count of negative factors matters."]),
    _tsp(2, "tsm-w2-month-days", "Days in a month", "stretch",
         "The input is `year month`. Print how many days that month has in the Gregorian calendar (February has 29 in a leap year: divisible by 4, except centuries, except every 400 years). Print `invalid` for a month outside 1-12.",
         r"""
const p = input.split(/\s+/).map(Number);
const year = p[0], month = p[1];
const leap = (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
switch (month) {
  case 2:
    console.log(leap ? 29 : 28);
    break;
  case 4: case 6: case 9: case 11:
    console.log(30);
    break;
  case 1: case 3: case 5: case 7: case 8: case 10: case 12:
    console.log(31);
    break;
  default:
    console.log("invalid");
}
""", ["2024 2", "2023 2", "1900 2", "2000 2", "2026 9", "2026 12", "2026 13", "2026 0"],
         hints=["Write the leap-year rule as one boolean with `&&`, `||` and parentheses.",
                "Stacked `case` labels share one body."]),
    _tsp(2, "tsm-w2-rps", "Rock, paper, scissors", "stretch",
         "The input is two moves, e.g. `rock scissors`, case-insensitive. Print `player 1 wins`, `player 2 wins` or `draw`, or `invalid` if either move is not rock, paper or scissors.",
         r"""
const p = input.toLowerCase().split(/\s+/);
const a = p[0], b = p[1];
const valid = (m: string | undefined) => m === "rock" || m === "paper" || m === "scissors";
if (!valid(a) || !valid(b)) {
  console.log("invalid");
} else if (a === b) {
  console.log("draw");
} else if ((a === "rock" && b === "scissors") || (a === "paper" && b === "rock") || (a === "scissors" && b === "paper")) {
  console.log("player 1 wins");
} else {
  console.log("player 2 wins");
}
""", ["rock scissors", "Paper ROCK", "scissors rock", "paper paper", "rock lizard", "rock"],
         hints=["Normalise case once, validate both, then list only player 1's three winning pairs."]),
]

TS_PROJECTS[2] = _project(
    2, "grade.ts — letter grades from a table",
    "Turn a score into a letter grade twice in your head — once as an if-chain, once as a table — and ship the one that is easier to change. The acceptance tests only see the output; the point of the week is which version you would rather extend when the rules change.",
    ["The input is one score. Anything that isn't a number from 0 to 100 prints `invalid` and nothing else.",
     "Print the letter with a modifier: A (90+), B (80+), C (70+), D (60+), F below. Inside A-D, a units digit of 7-9 adds `+` and 0-2 adds `-` (so 87 is `B+`, 81 is `B-`, 85 is `B`); 100 is `A+`; F never has a modifier. Fractional scores are rounded with `Math.round` first.",
     "On a second line print `pass` for a rounded score of 60 or more, otherwise `fail`.",
     "Keep the band boundaries in one place, so adding an `E` band would be a one-line change."],
    r"""
const text = input;
const raw = Number(text);
if (text === "" || Number.isNaN(raw) || raw < 0 || raw > 100) {
  console.log("invalid");
} else {
  const score = Math.round(raw);
  const letter = score >= 90 ? "A" : score >= 80 ? "B" : score >= 70 ? "C" : score >= 60 ? "D" : "F";
  const units = score % 10;
  let modifier = "";
  if (score === 100) modifier = "+";
  else if (letter !== "F" && units >= 7) modifier = "+";
  else if (letter !== "F" && units <= 2) modifier = "-";
  console.log(letter + modifier);
  console.log(score >= 60 ? "pass" : "fail");
}
""", ["87", "81", "85", "100", "90", "59", "59.5", "0", "abc", "101", "72.4"],
    stretch=["Read the band table from the input instead of the code.",
             "Print the distance to the next grade up (`3 points to A-`)."],
)

TS_PRACTICE_MORE[2] = [
    _pr("tsm-w2-p4", "A strict comparison", "const same = 3 === 3;\n", "same", "boolean",
        hints=["A comparison produces a `boolean`."]),
    _pr("tsm-w2-p5", "`??` with a fallback", 'declare const given: string | undefined;\nconst name = given ?? "anon";\n', "name", "string",
        hints=["`??` removes `undefined` from the left side's type, and the fallback is a string too.", "What remains is `string`."]),
    _dx("tsm-w2-d4", "Comparing a number with text",
        "error TS2367: This comparison appears to be unintentional because the types 'number' and 'string' have no overlap.",
        _STDIN + 'const n = Number(input);\nconsole.log(n === "0" ? "zero" : "not zero");\n',
        _STDIN + 'const n = Number(input);\nconsole.log(n === 0 ? "zero" : "not zero");\n',
        [("0", "zero"), ("5", "not zero")], hints=["`n` is a `number`; compare it with a number."]),
    _fx("tsm-w2-f3", "Zero is a real answer",
        "The input may be empty. Print the number typed, or `none` when nothing was typed. A typed `0` comes out as `none`.",
        _STDIN + 'const n = Number(input);\nconsole.log(n || "none");\n',
        _STDIN + 'console.log(input === "" ? "none" : Number(input));\n',
        [("0", "0"), ("", "none"), ("7", "7")], hints=["`0 || \"none\"` is `\"none\"`.", "Decide on the text, not on truthiness."]),
    _fx("tsm-w2-f4", "The missing break",
        "Print `one`, `two` or `many` for 1, 2 and anything else. Input 1 prints the wrong word.",
        _STDIN + 'let word = "";\nswitch (Number(input)) {\n  case 1:\n    word = "one";\n  case 2:\n    word = "two";\n    break;\n  default:\n    word = "many";\n}\nconsole.log(word);\n',
        _STDIN + 'let word = "";\nswitch (Number(input)) {\n  case 1:\n    word = "one";\n    break;\n  case 2:\n    word = "two";\n    break;\n  default:\n    word = "many";\n}\nconsole.log(word);\n',
        [("1", "one"), ("2", "two"), ("9", "many")], hints=["Without `break`, case 1 falls through into case 2."]),
]

TS_CARDS_MORE[2] = [
    ("`\"\" == 0` and `\"\" === 0`?", "`true` and `false` — `==` converts the empty string to 0 first; `===` never converts."),
    ("How do you test for `NaN`?", "`Number.isNaN(x)`. `x === NaN` is always false, even for `NaN` itself."),
    ("What does `Object.is(a, b)` fix compared with `===`?", "`Object.is(NaN, NaN)` is `true` and `Object.is(0, -0)` is `false`; otherwise it's the same as `===`."),
    ("`[1, 2] === [1, 2]`?", "`false` — arrays and objects compare by identity, not contents."),
    ("What does TS2367 mean?", "\"This comparison appears to be unintentional\": the two types can never be equal, e.g. a `number` and a `string`."),
    ("Which is the one accepted use of `==`?", "`x == null`, which is true for both `null` and `undefined` and nothing else."),
]

# ===========================================================================
# Week 3 — Loops & numbers
# ===========================================================================

TS_PROBLEM_SETS[3] = [
    _tsp(3, "tsm-w3-collatz", "Collatz steps", "warm-up",
         "The input is a positive integer n. Repeatedly halve it if even, or replace it with 3n + 1 if odd, until it reaches 1. Print the number of steps, then the largest value reached.",
         r"""
let n = Number(input);
let steps = 0;
let peak = n;
while (n !== 1) {
  n = n % 2 === 0 ? n / 2 : 3 * n + 1;
  if (n > peak) peak = n;
  steps++;
}
console.log(steps);
console.log(peak);
""", ["6", "1", "27", "97", "1000000"],
         hints=["A `while` loop, because you don't know the step count in advance."]),
    _tsp(3, "tsm-w3-droot", "Digital root", "warm-up",
         "The input is a non-negative integer. Repeatedly replace it with the sum of its digits until one digit is left. Print every value along the way, space-separated, starting with the input.",
         r"""
let n = Number(input);
const seen: number[] = [n];
while (n >= 10) {
  let sum = 0;
  let rest = n;
  while (rest > 0) {
    sum += rest % 10;
    rest = Math.floor(rest / 10);
  }
  n = sum;
  seen.push(n);
}
console.log(seen.join(" "));
""", ["9875", "0", "7", "999999999", "10"],
         hints=["Peel digits with `% 10` and `Math.floor(/ 10)` in an inner loop."]),
    _tsp(3, "tsm-w3-gcd", "GCD and LCM", "warm-up",
         "The input is two positive integers. Print their greatest common divisor and least common multiple on two lines. Use Euclid's algorithm.",
         r"""
const p = input.split(/\s+/).map(Number);
let a = p[0], b = p[1];
const product = a * b;
while (b !== 0) {
  const r = a % b;
  a = b;
  b = r;
}
console.log(a);
console.log(product / a);
""", ["12 18", "7 13", "100 10", "1 1", "270 192"],
         hints=["Replace (a, b) with (b, a % b) until b is 0; a is the gcd.", "lcm = a × b ÷ gcd."]),
    _tsp(3, "tsm-w3-multiples", "Multiples of 3 or 5", "warm-up",
         "The input is n. Print the sum of every positive integer below n that is a multiple of 3 or 5, then how many there were.",
         r"""
const n = Number(input);
let sum = 0;
let count = 0;
for (let i = 1; i < n; i++) {
  if (i % 3 === 0 || i % 5 === 0) {
    sum += i;
    count++;
  }
}
console.log(sum);
console.log(count);
""", ["10", "1", "16", "1000", "3"],
         hints=["A `for` loop with a condition; 15 counts once, not twice."]),
    _tsp(3, "tsm-w3-perfect", "Perfect, abundant or deficient", "core",
         "Each input line is a positive integer n. Print `perfect`, `abundant` or `deficient`, comparing n with the sum of its proper divisors (all divisors except n itself). Stop the divisor search at √n.",
         r"""
for (const line of input.split("\n")) {
  const n = Number(line);
  let sum = n > 1 ? 1 : 0;
  for (let d = 2; d * d <= n; d++) {
    if (n % d === 0) {
      sum += d;
      const pair = n / d;
      if (pair !== d) sum += pair;
    }
  }
  console.log(sum === n ? "perfect" : sum > n ? "abundant" : "deficient");
}
""", ["6\n12\n7", "28\n1\n496", "945\n8128\n2"],
         hints=["Divisors come in pairs d and n/d; only search up to √n and add both.", "Don't add the square root twice, and 1 has no proper divisors."]),
    _tsp(3, "tsm-w3-armstrong", "Armstrong numbers", "core",
         "The input is n. An Armstrong number equals the sum of its digits each raised to the power of the number of digits (153 = 1³ + 5³ + 3³). Print every Armstrong number from 1 to n, space-separated.",
         r"""
const n = Number(input);
const found: number[] = [];
for (let i = 1; i <= n; i++) {
  const digits = String(i).length;
  let sum = 0;
  let rest = i;
  while (rest > 0) {
    sum += (rest % 10) ** digits;
    rest = Math.floor(rest / 10);
  }
  if (sum === i) found.push(i);
}
console.log(found.join(" "));
""", ["10", "500", "10000", "1"],
         hints=["For each i, count its digits, then add each digit to that power."]),
    _tsp(3, "tsm-w3-reverse", "Reverse an integer", "core",
         "The input is an integer, possibly negative. Print it with its digits reversed, keeping the sign and dropping leading zeros — using arithmetic, not string methods.",
         r"""
const n = Number(input);
let rest = Math.abs(n);
let reversed = 0;
while (rest > 0) {
  reversed = reversed * 10 + (rest % 10);
  rest = Math.floor(rest / 10);
}
console.log(n < 0 ? -reversed : reversed);
""", ["123", "-456", "1200", "0", "7", "-9000001"],
         hints=["Take the last digit with `% 10` and push it onto the reversed number with `* 10 +`."]),
    _tsp(3, "tsm-w3-primes", "Count the primes", "core",
         "The input is n (up to 1,000,000). Print how many primes are ≤ n, then the largest one (or `none`). Use the sieve of Eratosthenes.",
         r"""
const n = Number(input);
const composite = new Uint8Array(n + 1);
let count = 0;
let largest = 0;
for (let i = 2; i <= n; i++) {
  if (composite[i] === 1) continue;
  count++;
  largest = i;
  for (let j = i * i; j <= n; j += i) composite[j] = 1;
}
console.log(count);
console.log(largest === 0 ? "none" : largest);
""", ["10", "1", "2", "100", "1000000"],
         hints=["Cross off multiples of each prime starting from its square.", "A `Uint8Array` is a compact array of flags."]),
    _tsp(3, "tsm-w3-bigfact", "Big factorial", "stretch",
         "The input is n (0 ≤ n ≤ 200). Compute n! exactly with `bigint`. Print the number of digits, the sum of the digits, and the number of trailing zeros, on three lines.",
         r"""
const n = BigInt(input);
let f = 1n;
for (let i = 2n; i <= n; i++) f *= i;
const digits = f.toString();
let digitSum = 0;
for (const ch of digits) digitSum += Number(ch);
let zeros = 0;
for (let i = digits.length - 1; i >= 0 && digits[i] === "0"; i--) zeros++;
console.log(digits.length);
console.log(digitSum);
console.log(zeros);
""", ["0", "5", "10", "25", "100", "200"],
         hints=["Every operand in the loop must be a `bigint`.", "Then work on its decimal string."]),
    _tsp(3, "tsm-w3-interest", "Compound interest in cents", "stretch",
         "The input is `principal ratePercent years`, e.g. `1000 5 3`. Interest compounds monthly: each month add `round(balance × rate / 12 / 100)` cents to the balance, working in whole cents (round half up with `Math.round`). Print the balance at the end of each year as `year <y>: $<x.xx>`, then `interest $<total>`.",
         r"""
const p = input.split(/\s+/).map(Number);
const startCents = Math.round(p[0] * 100);
const rate = p[1];
const years = p[2];
let cents = startCents;
for (let y = 1; y <= years; y++) {
  for (let m = 0; m < 12; m++) cents += Math.round((cents * rate) / 12 / 100);
  console.log(`year ${y}: $${(cents / 100).toFixed(2)}`);
}
console.log(`interest $${((cents - startCents) / 100).toFixed(2)}`);
""", ["1000 5 3", "100 0 2", "2500.50 3.5 1", "1 100 5", "10000 7.25 4"],
         hints=["Store the balance as integer cents and round each month's interest to a whole cent.", "Two nested `for` loops: years, then months."]),
    _tsp(3, "tsm-w3-words", "Numbers in words", "stretch",
         "Each input line is an integer from 0 to 999. Print it in English words, lowercase, with a hyphen in two-word tens (`forty-two`) and `hundred` without `and` (`one hundred five`).",
         r"""
const ones = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
  "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"];
const tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"];
function below100(n: number): string {
  if (n < 20) return ones[n];
  const t = tens[Math.floor(n / 10)];
  return n % 10 === 0 ? t : `${t}-${ones[n % 10]}`;
}
for (const line of input.split("\n")) {
  const n = Number(line);
  const hundreds = Math.floor(n / 100);
  const rest = n % 100;
  if (hundreds === 0) console.log(below100(rest));
  else if (rest === 0) console.log(`${ones[hundreds]} hundred`);
  else console.log(`${ones[hundreds]} hundred ${below100(rest)}`);
}
""", ["0\n7\n13\n42\n90", "100\n105\n999", "250\n19\n20\n21"],
         hints=["Tables for 0-19 and for the tens make every case short.", "Handle the hundreds, then reuse the under-100 logic for the rest."]),
]

TS_PROJECTS[3] = _project(
    3, "stats.ts — a one-pass statistics report",
    "Read a line of numbers and report on them in a single pass — no `sort`, no `reduce`, no array methods at all: one loop that keeps running totals. That constraint is the lesson: most statistics are just the right accumulators, updated once per value.",
    ["The input is one line of numbers separated by whitespace. An empty line prints `no data` and nothing else.",
     "Print `count`, `sum`, `mean`, `min`, `max` and `range` as `<name> <value>`, one per line, in that order. `mean` has exactly two decimals; the others print as plain numbers.",
     "Then print `above mean <k>` — how many values are strictly greater than the mean. (That needs the mean first, so it is the one place a second pass is allowed.)",
     "Use `for…of` loops and plain variables; don't call `sort`, `reduce`, `Math.min(...xs)` or `Math.max(...xs)`."],
    r"""
if (input === "") {
  console.log("no data");
} else {
  const values = input.split(/\s+/).map(Number);
  let count = 0;
  let sum = 0;
  let min = Infinity;
  let max = -Infinity;
  for (const v of values) {
    count++;
    sum += v;
    if (v < min) min = v;
    if (v > max) max = v;
  }
  const mean = sum / count;
  let above = 0;
  for (const v of values) if (v > mean) above++;
  console.log(`count ${count}`);
  console.log(`sum ${sum}`);
  console.log(`mean ${mean.toFixed(2)}`);
  console.log(`min ${min}`);
  console.log(`max ${max}`);
  console.log(`range ${max - min}`);
  console.log(`above mean ${above}`);
}
""", ["3 1 4 1 5 9 2 6", "", "7", "-5 -1 -10", "2 2 2 2", "0.5 1.5 2.25", "100 -100"],
    stretch=["Add the median — which does need a sorted copy. Why can't it be done in one pass?",
             "Add the standard deviation with Welford's one-pass method."],
)

TS_PRACTICE_MORE[3] = [
    _pr("tsm-w3-p4", "A bigint literal", "const big = 10n;\n", "big", "10n",
        hints=["A `const` keeps the literal type — for `bigint` too."]),
    _pr("tsm-w3-p5", "A widened bigint", "let count = 10n;\n", "count", "bigint",
        hints=["`let` widens the literal to its general type."]),
    _dx("tsm-w3-d4", "Mixing bigint and number",
        "error TS2365: Operator '*' cannot be applied to types 'bigint' and 'number'.",
        _STDIN + "const n = BigInt(input);\nconsole.log((n * 2).toString());\n",
        _STDIN + "const n = BigInt(input);\nconsole.log((n * 2n).toString());\n",
        [("21", "42"), ("9007199254740993", "18014398509481986")], hints=["Both operands must be `bigint`.", "Write `2n`."]),
    _fx("tsm-w3-f3", "Off by one",
        "Print the sum of 1 to n inclusive. It's always short by n.",
        _STDIN + "const n = Number(input);\nlet sum = 0;\nfor (let i = 1; i < n; i++) sum += i;\nconsole.log(sum);\n",
        _STDIN + "const n = Number(input);\nlet sum = 0;\nfor (let i = 1; i <= n; i++) sum += i;\nconsole.log(sum);\n",
        [("4", "10"), ("1", "1"), ("100", "5050")], hints=["\"1 to n inclusive\" — does the loop ever reach n?"]),
    _fx("tsm-w3-f4", "Equal, give or take a float",
        "The input is `a b c`. Print `equal` when a + b equals c, otherwise `not equal`. It says `0.1 0.2 0.3` is not equal.",
        _STDIN + 'const [a = 0, b = 0, c = 0] = input.split(/\\s+/).map(Number);\nconsole.log(a + b === c ? "equal" : "not equal");\n',
        _STDIN + 'const [a = 0, b = 0, c = 0] = input.split(/\\s+/).map(Number);\nconsole.log(Math.abs(a + b - c) < 1e-9 ? "equal" : "not equal");\n',
        [("0.1 0.2 0.3", "equal"), ("1 2 3", "equal"), ("1 2 4", "not equal"), ("0.1 0.2 0.30001", "not equal")],
        hints=["`0.1 + 0.2` is `0.30000000000000004`.", "Compare with a small tolerance."], difficulty="Medium"),
]

TS_CARDS_MORE[3] = [
    ("Why is `(1.005).toFixed(2)` `\"1.00\"`?", "1.005 is stored as 1.00499999…; `toFixed` rounds the stored value, not the decimal you typed."),
    ("How do you print integer cents as dollars?", "`(cents / 100).toFixed(2)` — convert only at the moment of printing, and keep all arithmetic in whole cents."),
    ("`Math.round(-2.5)`?", "`-2` — `Math.round` rounds halves towards +∞."),
    ("How do you write and convert to `bigint`?", "A literal with `n` (`123n`) or `BigInt(\"123\")`. It never mixes with `number` in arithmetic."),
    ("How do you format `1234567.8` as `1,234,567.8` deterministically?", "`new Intl.NumberFormat(\"en-US\").format(n)` — always pass the locale."),
    ("What does `Number.isSafeInteger(x)` check?", "That `x` is an integer between −(2^53 − 1) and 2^53 − 1, where every integer is exactly representable."),
]

# ===========================================================================
# Week 4 — Strings, string methods, regex and Unicode
# ===========================================================================

TS_PROBLEM_SETS[4] = [
    _tsp(4, "tsm-w4-longest", "Longest word", "warm-up",
         "The input is a sentence. Words are runs of letters (ignore punctuation and digits). Print the longest word — the first one if several tie — and its length, as `<word> <n>`, or `none 0` if there are no words.",
         r"""
const words = input.match(/[A-Za-z]+/g) ?? [];
let best = "";
for (const w of words) if (w.length > best.length) best = w;
console.log(best === "" ? "none 0" : `${best} ${best.length}`);
""", ["The quick brown fox jumped!", "a bb cc d", "123 456", "It's well-known."],
         hints=["`match(/[A-Za-z]+/g)` gives every run of letters, or `null`."]),
    _tsp(4, "tsm-w4-acronym", "Acronym", "warm-up",
         "The input is a phrase. Words are separated by spaces or hyphens. Print the uppercase first letter of every word.",
         r"""
const words = input.split(/[\s-]+/).filter((w) => w !== "");
console.log(words.map((w) => w[0].toUpperCase()).join(""));
""", ["portable network graphics", "Complementary metal-oxide semiconductor", "  as   soon as possible ", "a"],
         hints=["Split on a character class of spaces and hyphens.", "Take index 0 of each word and uppercase it."]),
    _tsp(4, "tsm-w4-pangram", "Pangram?", "warm-up",
         "Each input line is a sentence. Print `pangram` if it contains every letter a-z at least once (case-insensitive), otherwise `missing <letters>` with the missing letters in alphabetical order.",
         r"""
for (const line of input.split("\n")) {
  const lower = line.toLowerCase();
  let missing = "";
  for (let code = 97; code <= 122; code++) {
    const ch = String.fromCharCode(code);
    if (!lower.includes(ch)) missing += ch;
  }
  console.log(missing === "" ? "pangram" : `missing ${missing}`);
}
""", ["The quick brown fox jumps over the lazy dog", "Hello world", "Pack my box with five dozen liquor jugs!"],
         hints=["Loop over the character codes 97 (`a`) to 122 (`z`)."]),
    _tsp(4, "tsm-w4-squash", "Squash the spaces", "warm-up",
         "Each input line may have leading, trailing and repeated spaces and tabs. Print it with the ends trimmed and every run of whitespace replaced by one space, followed by ` (<k> removed)` — how many characters were dropped.",
         r"""
for (const line of input.split("\n")) {
  const clean = line.trim().replace(/\s+/g, " ");
  console.log(`${clean} (${line.length - clean.length} removed)`);
}
""", ["  hello    world  ", "a\t\tb", "already clean"],
         hints=["`trim()` then `replace(/\\s+/g, \" \")`."]),
    _tsp(4, "tsm-w4-mask", "Mask a card number", "core",
         "Each input line is a card number that may contain spaces and dashes. Keep only the digits. If there are fewer than 12 or more than 19, print `invalid`. Otherwise replace every digit but the last four with `*` and print them in groups of four from the left, separated by spaces.",
         r"""
for (const line of input.split("\n")) {
  const digits = line.replace(/[\s-]/g, "");
  if (!/^\d{12,19}$/.test(digits)) {
    console.log("invalid");
    continue;
  }
  const masked = "*".repeat(digits.length - 4) + digits.slice(-4);
  console.log(masked.match(/.{1,4}/g)?.join(" ") ?? "");
}
""", ["4111 1111 1111 1111", "5500-0000-0000-0004", "1234", "3782 822463 10005", "4111x1111"],
         hints=["Strip separators, validate with an anchored pattern, then build the masked string.",
                "`/.{1,4}/g` chops a string into groups of four."]),
    _tsp(4, "tsm-w4-snake", "camelCase to snake_case", "core",
         "Each input line is an identifier in camelCase or PascalCase, possibly containing an acronym (`parseHTTPResponse`). Print it in snake_case: lowercase words joined by underscores (`parse_http_response`).",
         r"""
for (const line of input.split("\n")) {
  const snake = line
    .trim()
    .replace(/([a-z0-9])([A-Z])/g, "$1_$2")
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1_$2")
    .toLowerCase();
  console.log(snake);
}
""", ["helloWorld\nparseHTTPResponse\nUserID", "already_snake\nX\nversion2Update"],
         hints=["Put an underscore between a lowercase letter or digit and a capital.",
                "A second pass splits an acronym from the word after it: `HTTPResponse` → `HTTP_Response`."]),
    _tsp(4, "tsm-w4-camel", "snake_case to camelCase", "core",
         "Each input line is a snake_case or kebab-case identifier. Print it in camelCase: first word lowercase, each later word capitalised, underscores and hyphens removed. Repeated separators count as one.",
         r"""
for (const line of input.split("\n")) {
  const words = line.trim().toLowerCase().split(/[_-]+/).filter((w) => w !== "");
  const camel = words.map((w, i) => (i === 0 ? w : w[0].toUpperCase() + w.slice(1))).join("");
  console.log(camel);
}
""", ["hello_world\nparse-http-response", "__private__field\nX_Y_Z", "single"],
         hints=["Split on `/[_-]+/`, drop empty pieces, capitalise every word but the first."]),
    _tsp(4, "tsm-w4-emails", "Extract email addresses", "core",
         "The input is free text. Find every email address — `name@domain.tld`, where name may contain letters, digits, `.`, `_`, `+` and `-`, and the domain is dot-separated labels of letters, digits and hyphens ending in a 2+ letter TLD. Print the distinct addresses lowercased and sorted, one per line, then `<n> found`.",
         r"""
const re = /[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}/g;
const found = new Set<string>();
for (const m of input.matchAll(re)) found.add(m[0].toLowerCase());
const sorted = [...found].sort();
for (const e of sorted) console.log(e);
console.log(`${sorted.length} found`);
""", ["Contact ada@example.com or ADA@Example.com, cc grace.h+work@mail.co.uk.", "no addresses here", "a@b.c and x@y.io, bad@nodot"],
         hints=["`matchAll` with the `g` flag gives every match.", "A `Set` removes duplicates after lowercasing."]),
    _tsp(4, "tsm-w4-roman", "Roman numerals to integers", "stretch",
         "Each input line is a Roman numeral. Print its value, or `invalid` if it is not a canonical numeral from 1 to 3999 (so `IIII`, `VX` and `IC` are invalid). A canonical numeral matches `M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})`.",
         r"""
const canonical = /^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$/;
const value: Record<string, number> = { I: 1, V: 5, X: 10, L: 50, C: 100, D: 500, M: 1000 };
for (const line of input.split("\n")) {
  const s = line.trim().toUpperCase();
  if (s === "" || !canonical.test(s)) {
    console.log("invalid");
    continue;
  }
  let total = 0;
  for (let i = 0; i < s.length; i++) {
    const here = value[s[i]];
    const next = i + 1 < s.length ? value[s[i + 1]] : 0;
    total += here < next ? -here : here;
  }
  console.log(total);
}
""", ["III\nIV\nIX\nLVIII\nMCMXCIV", "MMMCMXCIX\niiii\nVX\nIC", "xlii\n\nM"],
         hints=["Validate with the anchored pattern first.", "A symbol smaller than the one after it is subtracted."]),
    _tsp(4, "tsm-w4-justify", "Justify a line", "stretch",
         "The first line is a width W; the rest is text. Greedily pack words into lines of at most W characters. Justify every line except the last by distributing extra spaces between words, leftmost gaps first; a line with one word is left-aligned. Print each line between `|` bars, padded to W.",
         r"""
const lines = input.split("\n");
const width = Number(lines[0]);
const words = lines.slice(1).join(" ").split(/\s+/).filter((w) => w !== "");
const rows: string[][] = [];
let row: string[] = [];
let len = 0;
for (const w of words) {
  if (row.length > 0 && len + 1 + w.length > width) {
    rows.push(row);
    row = [];
    len = 0;
  }
  len += (row.length > 0 ? 1 : 0) + w.length;
  row.push(w);
}
if (row.length > 0) rows.push(row);
rows.forEach((r, idx) => {
  let text: string;
  if (idx === rows.length - 1 || r.length === 1) {
    text = r.join(" ");
  } else {
    let letters = 0;
    for (const w of r) letters += w.length;
    const gaps = r.length - 1;
    const spaces = width - letters;
    const base = Math.floor(spaces / gaps);
    const extra = spaces % gaps;
    text = r.map((w, i) => (i < gaps ? w + " ".repeat(base + (i < extra ? 1 : 0)) : w)).join("");
  }
  console.log(`|${text.padEnd(width)}|`);
});
""", ["16\nThis is an example of text justification.", "10\nWhat must be done shall be done now", "5\nhi"],
         hints=["First pack greedily, then justify each finished row.",
                "Spaces to share = width − letters; each gap gets `floor(spaces / gaps)`, and the first `spaces % gaps` gaps one more."]),
    _tsp(4, "tsm-w4-title", "Title case in any language", "stretch",
         "Each input line is text in any language. A word is a Unicode letter followed by any letters, combining marks or apostrophes. Lowercase the line, then uppercase the first code point of every word, and print the result followed by ` (<n> words)`.",
         r"""
for (const line of input.split("\n")) {
  let words = 0;
  const titled = line
    .trim()
    .toLowerCase()
    .replace(/\p{L}[\p{L}\p{M}']*/gu, (word) => {
      words++;
      const chars = [...word];
      return chars[0].toUpperCase() + chars.slice(1).join("");
    });
  console.log(`${titled} (${words} words)`);
}
""", ["hello WORLD", "élan vital — ÉCOLE normale", "o'neill's café", "12 monkeys, 3 dogs", "ça va très bien"],
         hints=["`\\p{L}` matches any Unicode letter and `\\p{M}` a combining mark; both need the `u` flag.",
                "A replacement *function* can change each word; spread it into code points before taking the first."]),
]

TS_PROJECTS[4] = _project(
    4, "slug.ts — URL slugs from titles",
    "Every blog, shop and wiki turns titles into URL slugs. It sounds like one `replace`; it is really a small pipeline — case, accents, punctuation, runs of separators, the ends — and each step is one idea from this week.",
    ["Each input line is a title. Print one slug per line.",
     "A slug is lowercase ASCII letters and digits separated by single hyphens, with no hyphen at either end.",
     "Accented Latin letters lose their accents (`Café` → `cafe`): normalise to NFD and remove the combining marks (`\\p{M}` with the `u` flag).",
     "Every run of anything else — spaces, punctuation, emoji — becomes one hyphen.",
     "A title with nothing left prints `untitled`."],
    r"""
for (const line of input.split("\n")) {
  const slug = line
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  console.log(slug === "" ? "untitled" : slug);
}
""", ["Hello, World!", "  Café Crème — 2026 edition  ", "TypeScript's `satisfies` operator", "!!!", "Ünïcödé 😀 slugs", "already-a-slug", "a    b\t\tc"],
    stretch=["Cap slugs at 60 characters without cutting a word in half.",
             "Keep a set of slugs already issued and append `-2`, `-3` … to duplicates."],
)

TS_PRACTICE_MORE[4] = [
    _pr("tsm-w4-p4", "A failed match", 'const m = "abc".match(/\\d+/);\n', "m", "RegExpMatchArray | null",
        hints=["`match` without `g` returns the match details — or `null`."]),
    _pr("tsm-w4-p5", "Every match", 'const all = "a1b2".match(/\\d/g);\n', "all", "RegExpMatchArray | null",
        hints=["With `g` it's still typed as `RegExpMatchArray | null`."]),
    _dx("tsm-w4-d4", "A match that might not happen",
        "error TS18047: 'm' is possibly 'null'.",
        _STDIN + "const m = input.match(/(\\d+)/);\nconsole.log(m[1]);\n",
        _STDIN + 'const m = input.match(/(\\d+)/);\nconsole.log(m === null ? "none" : m[1]);\n',
        [("abc123", "123"), ("xyz", "none")], hints=["`match` returns `null` when nothing matches."]),
    _fx("tsm-w4-f3", "Only the first one",
        "Replace every comma with a semicolon. Only the first changes.",
        _STDIN + 'console.log(input.replace(",", ";"));\n',
        _STDIN + 'console.log(input.replaceAll(",", ";"));\n',
        [("a,b,c", "a;b;c"), ("no commas", "no commas")], hints=["A string pattern replaces one occurrence."]),
    _fx("tsm-w4-f4", "Reversing an emoji",
        "Print the input reversed. Emoji come out as garbage.",
        _STDIN + 'console.log(input.split("").reverse().join(""));\n',
        _STDIN + 'console.log([...input].reverse().join(""));\n',
        [("abc", "cba"), ("a😀b", "b😀a")], hints=["`split(\"\")` splits code units, cutting surrogate pairs.", "Spread iterates by code point."]),
]

TS_CARDS_MORE[4] = [
    ("`/\\d+/.test(s)` vs `/^\\d+$/.test(s)`?", "The first asks \"are there digits anywhere?\"; the anchored one asks \"is the whole string digits?\""),
    ("`match` vs `matchAll`?", "`match` with `g` returns only the matched strings; `matchAll` (needs `g`) yields full matches with groups and indexes."),
    ("Why does reusing a `/…/g` regex with `test` give alternating results?", "A global regex is stateful — `test` continues from `lastIndex`. Don't use `g` for plain testing."),
    ("How do you reference a named group in a replacement?", "`$<name>`; in code, read `m.groups?.name`."),
    ("Three ways to count the \"characters\" in `\"🇯🇵\"`?", "4 code units (`length`), 2 code points (`[...s].length`), 1 grapheme (`Intl.Segmenter`)."),
    ("How do you reverse a string without breaking emoji?", "`[...s].reverse().join(\"\")` — spread iterates by code point."),
    ("Why normalise text before comparing it?", "`é` can be one code point or `e` + a combining accent; they look the same but aren't `===` until both are `normalize(\"NFC\")`-ed."),
    ("How should you sort human-readable words?", "`a.localeCompare(b, \"en\")` — the default sort compares code units, putting uppercase first and accents last."),
    ("What does the `u` flag change?", "The pattern works on code points: `.` matches a whole emoji, and `\\p{L}`-style classes become available."),
    ("What does `isWellFormed()` report?", "Whether a string contains no lone surrogates — e.g. after slicing through the middle of an emoji."),
    ("How do you strip accents from Latin text?", "`s.normalize(\"NFD\").replace(/\\p{M}/gu, \"\")` — decompose, then drop the combining marks."),
    ("`s.replace(\"a\", \"b\")` vs `s.replaceAll(\"a\", \"b\")`?", "`replace` with a string pattern changes only the first occurrence; `replaceAll` changes every one."),
]
