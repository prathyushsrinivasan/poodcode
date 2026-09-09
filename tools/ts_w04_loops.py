# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 4 — loops.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

# --- Week 4 ---------------------------------------------------------------
_WEEKS.append(_week(
    4, 1, _M1,
    "Loops",
    "Repeat work with while, for and for...of; accumulate results; steer with break and continue; and nest loops for grids.",
    """
Computers are unremarkable at any single instruction and extraordinary at doing
one a million times. This week you learn to say "again".

Four ideas, and the third is the one that matters most:

1. **`while`** — repeat while a condition holds.
2. **`for`** — the same thing, packaged for counting.
3. **The accumulator** — a variable that survives across iterations and builds
   the answer: a running total, a counter, a best-so-far, a growing string.
   Nearly every loop you will ever write is an accumulator loop.
4. **`for...of`** — hand me each item in turn, no counter needed.

Then `break`/`continue` for steering, and nested loops for anything
two-dimensional.

Loops are also where you'll meet your first *hang*: a loop whose condition never
becomes false runs forever. That's normal, it happens to everyone, and lesson 1
shows you exactly what causes it.

⏱️ Budget about **seven hours**, spread over several sittings.
""",
    objectives=[
        "Write a while loop and trace its variables by hand",
        "Recognise and repair an infinite loop",
        "Write a for loop and get its boundary right",
        "Build a running total, counter, best-so-far, and string with an accumulator",
        "Walk a string character by character with for...of",
        "Steer a loop with break and continue",
        "Take a number apart digit by digit with % and Math.floor",
        "Nest loops to produce rows and columns",
    ],
    why="A loop is how you turn one calculation into a report, one comparison into a search, one character into a parser. Everything from summing a column to rendering a frame is this.",
    est_minutes=440,
    glossary=[
        _gloss("loop", "Code that repeats while a condition holds."),
        _gloss("iteration", "One pass through the loop body."),
        _gloss("condition", "The test checked before each iteration."),
        _gloss("body", "The block that repeats."),
        _gloss("accumulator", "A variable declared OUTSIDE the loop that builds a result across iterations."),
        _gloss("counter", "An accumulator that counts occurrences."),
        _gloss("initialisation", "Setting the loop variable's starting value."),
        _gloss("update / step", "The change that moves the loop toward finishing."),
        _gloss("infinite loop", "A loop whose condition never becomes false."),
        _gloss("off-by-one", "Running one time too many or too few — usually < versus <=."),
        _gloss("for...of", "A loop that hands you each item of a sequence directly."),
        _gloss("break", "Leave the loop immediately."),
        _gloss("continue", "Skip the rest of this iteration and start the next."),
        _gloss("nested loop", "A loop inside another loop's body."),
        _gloss("sentinel", "A starting value chosen so the first comparison always updates it."),
        _gloss("trace", "Walking through a loop by hand, writing down each variable each pass."),
    ],
    cheatsheet="""
```ts
// ---- while ----------------------------------------------------------
let i = 1;
while (i <= n) {
  // ... work ...
  i = i + 1;          // ⚠️ without this it never ends
}

// ---- for: setup ; condition ; step ----------------------------------
for (let i = 1; i <= n; i = i + 1) { ... }   // 1..n inclusive
for (let i = 0; i < n; i = i + 1) { ... }    // n times, 0..n-1
for (let i = n; i >= 1; i = i - 1) { ... }   // countdown
i++            // shorthand for i = i + 1
sum += x       // shorthand for sum = sum + x

// ---- accumulators (declared BEFORE the loop) ------------------------
let sum = 0;          // running total       ->  sum += x
let count = 0;        // counter             ->  count++
let best = -Infinity; // maximum so far      ->  if (x > best) best = x;
let out = "";         // built-up string     ->  out += ch

// ---- for...of: each character ---------------------------------------
for (const ch of s) { ... }

// ---- steering --------------------------------------------------------
if (found) break;      // leave the loop entirely
if (skip) continue;    // jump to the next iteration

// ---- digits ----------------------------------------------------------
n % 10                 // last digit
Math.floor(n / 10)     // drop the last digit

// ---- nesting ---------------------------------------------------------
for (let r = 1; r <= rows; r++) {
  let line = "";
  for (let c = 1; c <= cols; c++) { line += "*"; }
  console.log(line);
}
```
""",
    self_check=[
        "Can you sum the numbers 1..n with both a while and a for loop?",
        "Can you say, for a loop that hangs, exactly which line is missing?",
        "Can you count how often a character appears in a string?",
        "Can you find the largest of a stream of values without an array?",
        "Can you explain the difference between break and continue?",
        "Can you extract the digits of 4207 one at a time?",
        "Can you print a 3x4 rectangle of stars?",
    ],
    review=[
        _q("What is an accumulator?",
           ["A loop keyword", "A variable declared outside the loop that builds a result",
            "A comparison", "The loop condition"], 1,
           "Declared before the loop so it survives every iteration."),
        _q("A while loop whose condition never becomes false…",
           ["runs once", "never runs", "runs forever", "errors"], 2,
           "That is an infinite loop — the update is missing or wrong."),
        _q("`for (let i = 0; i < 3; i++)` runs the body how many times?",
           ["2", "3", "4", "forever"], 1, "i takes the values 0, 1, 2."),
        _q("`for (let i = 1; i <= 3; i++)` runs the body how many times?",
           ["2", "3", "4", "forever"], 1, "i takes 1, 2, 3."),
        _q('`for (const ch of "hi")` runs the body…',
           ["once", "twice", "three times", "never"], 1, "Once per character: h, i."),
        _q("`break` does what?",
           ["Skips one iteration", "Leaves the loop entirely", "Restarts the loop",
            "Ends the program"], 1,
           "It exits the loop immediately; continue is the one that skips."),
        _q("`continue` does what?",
           ["Leaves the loop", "Skips the rest of this iteration", "Repeats the iteration",
            "Nothing"], 1,
           "Control jumps to the loop's update and next test."),
        _q("`4207 % 10` and `Math.floor(4207 / 10)` give…",
           ["7 and 420", "4 and 207", "7 and 4207", "0 and 420"], 0,
           "Remainder peels off the last digit; the floored division drops it."),
        _q("Why start a maximum search at -Infinity?",
           ["It is faster", "So the first real value always beats it",
            "It is required", "To avoid zero"], 1,
           "A sentinel guarantees the first comparison updates the best-so-far."),
        _q("Two nested loops of 3 and 4 iterations run the inner body…",
           ["7 times", "12 times", "3 times", "4 times"], 1,
           "The inner loop runs fully for every pass of the outer: 3 * 4."),
    ],
    milestone="Budget Buddy can now project a savings schedule day by day and summarise it — its first program that produces a whole report rather than a single line.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w4-while", "while loops",
            "Repeat while a condition holds — and make sure it stops.",
            """
A `while` loop runs its body over and over, checking its condition **before**
each pass:

```ts
let i = 1;
let sum = 0;
while (i <= 3) {
  sum = sum + i;
  i = i + 1;
}
console.log(sum);   // 6
```

Every while loop has three parts, and forgetting any of them breaks it:

1. **Initialise** something before the loop (`let i = 1`).
2. **Test** it in the condition (`i <= 3`).
3. **Update** it inside the body (`i = i + 1`).

**Trace it by hand.** This is the single most useful habit in this whole week —
write out the variables at every step:

| pass | i | `i <= 3` | sum after |
|------|---|--------|-----------|
| start | 1 | — | 0 |
| 1 | 1 | true | 1 |
| 2 | 2 | true | 3 |
| 3 | 3 | true | 6 |
| end | 4 | false | 6 |

Notice the loop *does* leave `i` at 4 — one past the last value used. That's
normal, and worth expecting.

**Infinite loops.** Drop the update and the condition never changes:

```ts
let i = 1;
while (i <= 3) {
  console.log(i);   // 1, 1, 1, 1, ... forever
}
```

Nothing errors; the program simply never finishes (here, the judge will stop it
and report a timeout). When a program hangs, look first for a loop whose
variable isn't moving.

**When to prefer `while`:** when you don't know in advance how many passes you
need — "keep halving until it's below 1", "keep reading until the end". When
you're counting a known number of times, the `for` loop in the next lesson says
it better.

> ⚠️ **Common mistakes:** forgetting the update; updating the wrong variable;
> and putting a `;` right after the condition (`while (i < 3);`), which makes an
> empty body and hangs immediately.
""",
            warmup=[
                _q("`let i=0; while(i<2){ i = i+1; } console.log(i);` prints…",
                   ["0", "1", "2", "forever"], 2, "i climbs to 2, at which point i<2 is false."),
                _q("`let i=0; while(i<0){ i = i+1; } console.log(i);` prints…",
                   ["0", "1", "-1", "forever"], 0,
                   "The condition is false straight away, so the body never runs."),
                _q("Which line, if deleted, makes a counting while loop hang?",
                   ["the declaration", "the condition", "the update inside the body",
                    "the console.log"], 2,
                   "Without the update the condition can never become false."),
            ],
            exercises=[
                _ex("tscourse-w4-while-1", "Sum 1..n",
                    "Loop while i has not passed n, adding each i to sum. Print the total.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let sum = 0;\nlet i = 1;\nwhile (i <= n) {\n  sum = sum + i;\n  i = i + 1;\n}\nconsole.log(sum);\n',
                    'i <= n',
                    [("5", "15"), ("1", "1"), ("10", "55")],
                    hints=["Keep going while i has not gone past n.", "The condition is i <= n."]),
                _ex("tscourse-w4-while-2", "Countdown",
                    "Print n, n-1, … down to 1, one per line.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let i = n;\nwhile (i >= 1) {\n  console.log(i);\n  i = i - 1;\n}\n',
                    'i = i - 1;',
                    [("3", "3\n2\n1"), ("1", "1")],
                    hints=["Counting down means the update subtracts.",
                           "Write i = i - 1;"]),
                _ex("tscourse-w4-while-3", "Halve until small",
                    "Keep halving n (rounding down) until it reaches 0, counting the steps. Print the count.",
                    _FS + 'let n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let steps = 0;\nwhile (n > 0) {\n  n = Math.floor(n / 2);\n  steps = steps + 1;\n}\nconsole.log(steps);\n',
                    'n = Math.floor(n / 2);',
                    [("8", "4"), ("1", "1"), ("5", "3")],
                    hints=["Each pass replaces n with half of it, rounded down.",
                           "Write n = Math.floor(n / 2);"],
                    difficulty="Medium"),
                _ex("tscourse-w4-while-4", "Powers of two",
                    "Print every power of two that is 1 or more and no greater than n, one per line.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let p = 1;\nwhile (p <= n) {\n  console.log(p);\n  p = p * 2;\n}\n',
                    'p = p * 2;',
                    [("10", "1\n2\n4\n8"), ("1", "1"), ("16", "1\n2\n4\n8\n16")],
                    hints=["The step is not +1 here — it doubles.",
                           "Write p = p * 2;"]),
                _ex("tscourse-w4-while-5", "First multiple over a limit",
                    "Starting at 7 and adding 7 each time, print the first multiple of 7 that is strictly greater than n.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let m = 7;\nwhile (m <= n) {\n  m = m + 7;\n}\nconsole.log(m);\n',
                    'while (m <= n) {',
                    [("20", "21"), ("21", "28"), ("0", "7")],
                    hints=["Keep advancing while m has NOT yet passed n.",
                           "The condition is m <= n."],
                    difficulty="Medium"),
                _fix("tscourse-w4-while-fix1", "Fix the infinite loop",
                     "This loop never ends because i never changes. Fix it so it prints 1 2 3.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let i = 1;\nwhile (i <= n) {\n  console.log(i);\n}\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let i = 1;\nwhile (i <= n) {\n  console.log(i);\n  i = i + 1;\n}\n',
                     [("3", "1\n2\n3")],
                     hints=["Nothing advances i, so i <= n stays true forever.",
                            "Add i = i + 1; inside the body."],
                     difficulty="Medium"),
                _fix("tscourse-w4-while-fix2", "Fix the wrong direction",
                     "This should count down from n to 1 but hangs. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let i = n;\nwhile (i >= 1) {\n  console.log(i);\n  i = i + 1;\n}\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let i = n;\nwhile (i >= 1) {\n  console.log(i);\n  i = i - 1;\n}\n',
                     [("3", "3\n2\n1")],
                     hints=["The update moves i AWAY from the finish line.",
                            "Counting down subtracts: i = i - 1;"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A while loop checks its condition…",
                   ["after each pass", "before each pass", "only once", "never"], 1,
                   "Which is why a false condition means the body never runs at all."),
                _q("Your program hangs. The first thing to look for is…",
                   ["a typo in a string", "a loop variable that never changes",
                    "a missing semicolon", "too much printing"], 1,
                   "An unchanging loop variable is the overwhelmingly common cause."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w4-for", "for loops",
            "The counting loop, with all three parts on one line.",
            """
A `for` loop puts the initialisation, condition and update where you can see
them together:

```ts
for (let i = 1; i <= n; i = i + 1) {
  console.log(i);
}
```

```
     ┌ initialise once   ┌ test before every pass   ┌ update after every pass
for (let i = 1;          i <= n;                    i = i + 1) { ... }
```

It is exactly the `while` from lesson 1, rearranged so nothing can go missing.
Reach for `for` whenever you're counting a known number of times.

**The two standard shapes** — learn both by heart:

```ts
for (let i = 0; i < n; i++)    // n passes, i is 0 .. n-1   ← positions/indices
for (let i = 1; i <= n; i++)   // n passes, i is 1 .. n     ← counting things
```

`i++` is shorthand for `i = i + 1`. Similarly `sum += x` means
`sum = sum + x`, and `i--` counts down. They're everywhere in real code.

**Off-by-one.** `<` and `<=` differ by exactly one pass, and picking the wrong
one is the most common loop bug there is:

```ts
for (let i = 1; i < 5; i++)     // 1,2,3,4   — four passes
for (let i = 1; i <= 5; i++)    // 1,2,3,4,5 — five passes
```

The reliable check: ask "what is the **first** value, and what is the **last**?"
If you can answer both without hesitating, the boundary is right.

**Counting down:**

```ts
for (let i = n; i >= 1; i--) { ... }
```

**The loop variable is local.** `let i` inside the `for` header exists only
inside the loop. If you need the value afterwards, declare it outside — or, far
better, keep an accumulator (next lesson).

> ⚠️ **Common mistakes:** `<` where you wanted `<=`; separating the three parts
> with commas instead of semicolons; and a stray `;` after the header, which
> gives the loop an empty body.
""",
            warmup=[
                _q("`for (let i=0; i<3; i++) console.log(i);` prints…",
                   ["0 1 2 3", "0 1 2", "1 2 3", "3"], 1, "i < 3 covers 0, 1, 2."),
                _q("`for (let i=1; i<=3; i++)` runs the body how many times?",
                   ["2", "3", "4", "forever"], 1, "i is 1, 2, 3."),
                _q("`i++` is shorthand for…",
                   ["i = i - 1", "i = i + 1", "i = i * 2", "i = 1"], 1, "Increment by one."),
                _q("`sum += 5` means…",
                   ["sum = 5", "sum = sum + 5", "sum = sum * 5", "sum > 5"], 1,
                   "Add to the existing value and store it back."),
            ],
            exercises=[
                _ex("tscourse-w4-for-1", "Count to n",
                    "Print 1 up to n, one per line.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let i = 1; i <= n; i++) {\n  console.log(i);\n}\n',
                    'i <= n',
                    [("3", "1\n2\n3"), ("1", "1")],
                    hints=["n itself must print, so the boundary is inclusive.",
                           "The condition is i <= n."]),
                _ex("tscourse-w4-for-2", "Factorial",
                    "Multiply 1*2*...*n into product, then print it.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let product = 1;\nfor (let i = 1; i <= n; i++) {\n  product = product * i;\n}\nconsole.log(product);\n',
                    'product = product * i;',
                    [("5", "120"), ("1", "1"), ("4", "24")],
                    hints=["Each pass multiplies the running product by i.",
                           "Write product = product * i;"]),
                _ex("tscourse-w4-for-3", "Count the evens",
                    "Count how many numbers from 1..n are even, and print the count.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let count = 0;\nfor (let i = 1; i <= n; i++) {\n  if (i % 2 === 0) {\n    count++;\n  }\n}\nconsole.log(count);\n',
                    'i % 2 === 0',
                    [("10", "5"), ("1", "0"), ("2", "1"), ("7", "3")],
                    hints=["Even means remainder 0 when divided by 2.",
                           "Test i % 2 === 0."]),
                _ex("tscourse-w4-for-4", "Countdown with for",
                    "Print n down to 1, one per line, using a for loop.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let i = n; i >= 1; i--) {\n  console.log(i);\n}\n',
                    'let i = n; i >= 1; i--',
                    [("3", "3\n2\n1"), ("1", "1")],
                    hints=["Start high, stop at 1, and step downwards.",
                           "Write let i = n; i >= 1; i--"]),
                _ex("tscourse-w4-for-5", "Times table",
                    "Print n's times table from 1 to 5, as lines like `3 x 2 = 6`.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let i = 1; i <= 5; i++) {\n  console.log(`${n} x ${i} = ${n * i}`);\n}\n',
                    '`${n} x ${i} = ${n * i}`',
                    [("3", "3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n3 x 4 = 12\n3 x 5 = 15"),
                     ("1", "1 x 1 = 1\n1 x 2 = 2\n1 x 3 = 3\n1 x 4 = 4\n1 x 5 = 5")],
                    hints=["Three holes: the number, the multiplier, and the product.",
                           "Write `${n} x ${i} = ${n * i}`."]),
                _ex("tscourse-w4-for-6", "Sum of squares",
                    "Print 1² + 2² + ... + n².",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let sum = 0;\nfor (let i = 1; i <= n; i++) {\n  sum += i * i;\n}\nconsole.log(sum);\n',
                    'sum += i * i;',
                    [("3", "14"), ("1", "1"), ("4", "30")],
                    hints=["Add the square of i each pass.",
                           "Write sum += i * i;"]),
                _fix("tscourse-w4-for-fix1", "Fix the off-by-one",
                     "This should sum 1..n but leaves n out — sum(1..3) comes to 3 instead of 6. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let sum = 0;\nfor (let i = 1; i < n; i++) {\n  sum += i;\n}\nconsole.log(sum);\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let sum = 0;\nfor (let i = 1; i <= n; i++) {\n  sum += i;\n}\nconsole.log(sum);\n',
                     [("3", "6"), ("5", "15"), ("1", "1")],
                     hints=["`i < n` stops one short and never adds n itself.",
                            "Use i <= n."]),
                _fix("tscourse-w4-for-fix2", "Fix the empty body",
                     "For n=3 this prints a single line, `4`, instead of counting 1 2 3. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let i = 1;\nfor (i = 1; i <= n; i++);\n{\n  console.log(i);\n}\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let i = 1;\nfor (i = 1; i <= n; i++) {\n  console.log(i);\n}\n',
                     [("3", "1\n2\n3"), ("1", "1")],
                     hints=["The semicolon right after the header IS the loop's entire body, so the braces below run just once, after the loop.",
                            "Delete the semicolon so the block becomes the body."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`for (let i = 0; i < n; i++)` runs how many times?",
                   ["n - 1", "n", "n + 1", "forever"], 1,
                   "n passes, with i from 0 to n-1."),
                _q("The three parts of a for header are separated by…",
                   ["commas", "semicolons", "colons", "spaces"], 1,
                   "setup ; condition ; update."),
                _q("Where does `let i` declared in a for header exist?",
                   ["Everywhere", "Only inside the loop", "Only after the loop",
                    "Only in the condition"], 1,
                   "It is scoped to the loop."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w4-accumulate", "The accumulator pattern",
            "The one loop shape that covers most real problems.",
            """
Almost every useful loop looks like this:

```ts
let result = <starting value>;      // BEFORE the loop
for (...) {
  result = <result combined with this item>;
}
console.log(result);                // AFTER the loop
```

The variable is called an **accumulator**, and the crucial detail is *where it
lives*: **outside** the loop. Declare it inside and it's created fresh every
pass, losing everything — the single most common accumulator bug.

Four shapes cover an enormous amount of real code:

**1. Running total** — start at 0, add:

```ts
let sum = 0;
for (let i = 1; i <= n; i++) { sum += i; }
```

**2. Counter** — start at 0, add 1 when a condition holds:

```ts
let evens = 0;
for (let i = 1; i <= n; i++) { if (i % 2 === 0) evens++; }
```

**3. Best-so-far** — start at a **sentinel** that anything beats, then replace:

```ts
let best = -Infinity;
for (...) { if (x > best) { best = x; } }
```

Why `-Infinity` and not `0`? Because with `0` a stream of negative numbers would
report `0` as the maximum — a value that was never in the data. A sentinel that
loses to everything is the safe start. (For a minimum, start at `Infinity`.)

**4. Built-up string** — start empty, append:

```ts
let out = "";
for (const ch of s) { out = ch + out; }   // reversed!
```

Note the difference between `out + ch` (append — keeps the order) and
`ch + out` (prepend — reverses it). Same characters, opposite result.

**Choosing the starting value** is the whole art. Ask: *what should the answer
be if the loop runs zero times?* Sum of nothing is `0`. Product of nothing is
`1`. Text built from nothing is `""`. Maximum of nothing has no answer — which
is exactly why it needs a sentinel.

> ⚠️ **Common mistakes:** declaring the accumulator inside the loop; starting a
> product at 0 (everything stays 0); starting a maximum at 0; and printing
> inside the loop when you meant to print the final answer after it.
""",
            warmup=[
                _q("Where must the accumulator be declared?",
                   ["Inside the loop body", "Before the loop", "After the loop",
                    "In the condition"], 1,
                   "Inside, it would be recreated every pass and lose its value."),
                _q("What should a product accumulator start at?",
                   ["0", "1", "-1", "Infinity"], 1,
                   "0 would make every product 0. The product of nothing is 1."),
                _q("Starting a maximum search at 0 breaks when…",
                   ["all values are positive", "all values are negative",
                    "there is one value", "never"], 1,
                   "It would report 0, a value that never appeared in the data."),
                _q('`let out = ""; for (const ch of "abc") { out = out + ch; }` leaves out as…',
                   ['"abc"', '"cba"', '"c"', '""'], 0,
                   "Appending preserves the order; prepending would reverse it."),
            ],
            exercises=[
                _ex("tscourse-w4-acc-1", "Running total",
                    "Sum every number from 1 to n. Declare the accumulator in the right place.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let sum = 0;\nfor (let i = 1; i <= n; i++) {\n  sum += i;\n}\nconsole.log(sum);\n',
                    'let sum = 0;',
                    [("5", "15"), ("1", "1")],
                    hints=["It has to survive every pass, so it goes before the loop.",
                           "Write let sum = 0; above the for."]),
                _ex("tscourse-w4-acc-2", "Count the multiples",
                    "Count how many numbers from 1..n are multiples of 3.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let count = 0;\nfor (let i = 1; i <= n; i++) {\n  if (i % 3 === 0) {\n    count++;\n  }\n}\nconsole.log(count);\n',
                    'count++;',
                    [("10", "3"), ("3", "1"), ("2", "0")],
                    hints=["Add one to the counter when the test passes.",
                           "Write count++;"]),
                _ex("tscourse-w4-acc-3", "Largest digit",
                    "The input is a string of digits. Print the largest one, as a number.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'let best = -Infinity;\nfor (const ch of s) {\n  const d = Number(ch);\n  if (d > best) {\n    best = d;\n  }\n}\nconsole.log(best);\n',
                    'let best = -Infinity;',
                    [("4207", "7"), ("9", "9"), ("111", "1")],
                    hints=["Start from a value that every digit beats.",
                           "Write let best = -Infinity;"],
                    difficulty="Medium"),
                _ex("tscourse-w4-acc-4", "Smallest digit",
                    "Print the smallest digit in the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'let best = Infinity;\nfor (const ch of s) {\n  const d = Number(ch);\n  if (d < best) {\n    best = d;\n  }\n}\nconsole.log(best);\n',
                    'd < best',
                    [("4207", "0"), ("9", "9"), ("531", "1")],
                    hints=["Mirror the maximum: start at Infinity and keep anything smaller.",
                           "The test is d < best."],
                    difficulty="Medium"),
                _ex("tscourse-w4-acc-5", "Build a bar",
                    "Print a bar of `#` n characters long, built one character at a time in a loop.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let bar = "";\nfor (let i = 1; i <= n; i++) {\n  bar += "#";\n}\nconsole.log(bar);\n',
                    'bar += "#";',
                    [("3", "###"), ("1", "#")],
                    hints=["Append one character each pass.",
                           'Write bar += "#";']),
                _ex("tscourse-w4-acc-6", "Average of 1..n",
                    "Print the average of the numbers 1..n, to two decimal places.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let sum = 0;\nfor (let i = 1; i <= n; i++) {\n  sum += i;\n}\nconsole.log((sum / n).toFixed(2));\n',
                    '(sum / n).toFixed(2)',
                    [("4", "2.50"), ("1", "1.00"), ("5", "3.00")],
                    hints=["Total first, then divide — after the loop.",
                           "Write (sum / n).toFixed(2)."],
                    difficulty="Medium"),
                _fix("tscourse-w4-acc-fix1", "Fix the reset accumulator",
                     "This should print one number — the total, 15 for n=5 — but prints every number instead. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'for (let i = 1; i <= n; i++) {\n  let sum = 0;\n  sum += i;\n  console.log(sum);\n}\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let sum = 0;\nfor (let i = 1; i <= n; i++) {\n  sum += i;\n}\nconsole.log(sum);\n',
                     [("5", "15"), ("3", "6")],
                     hints=["The accumulator is created fresh every pass, so it never accumulates anything.",
                            "Move `let sum = 0;` above the loop and the console.log below it."],
                     difficulty="Medium"),
                _fix("tscourse-w4-acc-fix2", "Fix the product's start",
                     "This should print 120 for n=5 but prints 0. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let product = 0;\nfor (let i = 1; i <= n; i++) {\n  product = product * i;\n}\nconsole.log(product);\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let product = 1;\nfor (let i = 1; i <= n; i++) {\n  product = product * i;\n}\nconsole.log(product);\n',
                     [("5", "120"), ("1", "1")],
                     hints=["Anything multiplied by 0 is 0, forever.",
                            "A product accumulator starts at 1."]),
            ],
            quiz=[
                _q("The starting value of an accumulator should be…",
                   ["always 0", "the answer when the loop runs zero times", "always 1",
                    "the first item"], 1,
                   "Sum of nothing is 0; product of nothing is 1; text from nothing is \"\"."),
                _q("`out = ch + out` inside a loop over a string produces…",
                   ["the same string", "the reversed string", "the last character",
                    "an empty string"], 1,
                   "Each new character goes in front, so the result comes out backwards."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w4-forof", "for...of: walking a string",
            "When you want each item, not each position.",
            """
When you need every character and don't care about positions, `for...of` says it
directly:

```ts
for (const ch of "hello") {
  console.log(ch);      // h, e, l, l, o
}
```

Compare it with the indexed form, which does the same job with more moving
parts:

```ts
for (let i = 0; i < s.length; i++) {
  const ch = s[i];
  ...
}
```

**Use `for...of` when** you only need the values. **Use the indexed `for` when**
you need the position — to compare a character with its neighbour, to print
"character 3 is…", or to walk backwards.

Note `const ch` — it's a fresh binding each pass, so `const` is correct even
though the value differs every time.

**The counting pattern** with `for...of`:

```ts
let vowels = 0;
for (const ch of s) {
  if (ch === "a" || ch === "e" || ch === "i" || ch === "o" || ch === "u") {
    vowels++;
  }
}
```

**`for...of` vs `for...in`.** There is a similar-looking `for...in` that gives
you *keys*, not values — for a string that means `"0"`, `"1"`, `"2"`… as
strings. It is almost never what you want. Reach for `for...of`.

> ⚠️ **Common mistakes:** using `for...in` by accident; trying to reach the
> previous character without an index; and forgetting that `for...of` gives you
> a one-character *string*, so `Number(ch)` is needed before arithmetic.
""",
            warmup=[
                _q('How many times does `for (const c of "aba")` run its body?',
                   ["1", "2", "3", "0"], 2, "Once per character."),
                _q('In `for (const ch of "42")`, what is `ch` on the first pass?',
                   ["4", '"4"', "42", "0"], 1,
                   'A one-character string — you would need Number(ch) to do maths with it.'),
                _q("You need to compare each character with the one before it. Which loop?",
                   ["for...of", "an indexed for", "while(true)", "for...in"], 1,
                   "Neighbour comparisons need positions."),
            ],
            exercises=[
                _ex("tscourse-w4-of-1", "Count a letter",
                    "Count how many times the letter `a` appears in the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'let count = 0;\nfor (const ch of s) {\n  if (ch === "a") {\n    count++;\n  }\n}\nconsole.log(count);\n',
                    'ch === "a"',
                    [("banana", "3"), ("xyz", "0"), ("aaa", "3")],
                    hints=['Compare each character to "a".']),
                _ex("tscourse-w4-of-2", "Reverse a string",
                    "Build the input backwards by putting each new character in front.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'let out = "";\nfor (const ch of s) {\n  out = ch + out;\n}\nconsole.log(out);\n',
                    'ch + out',
                    [("abc", "cba"), ("hello", "olleh"), ("a", "a")],
                    hints=["Prepend rather than append.", "Write ch + out."]),
                _ex("tscourse-w4-of-3", "Count the vowels",
                    "Count the vowels (a, e, i, o, u) in the lowercased input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim().toLowerCase();\n'
                    'let v = 0;\nfor (const ch of s) {\n  if ("aeiou".includes(ch)) {\n    v++;\n  }\n}\nconsole.log(v);\n',
                    '"aeiou".includes(ch)',
                    [("banana", "3"), ("rhythm", "0"), ("AEIOU", "5")],
                    hints=["Rather than five comparisons, ask whether a vowel string contains the character.",
                           'Write "aeiou".includes(ch).'],
                    difficulty="Medium"),
                _ex("tscourse-w4-of-4", "Sum the digits",
                    "The input is a string of digits. Print their sum.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'let sum = 0;\nfor (const ch of s) {\n  sum += Number(ch);\n}\nconsole.log(sum);\n',
                    'sum += Number(ch);',
                    [("4207", "13"), ("9", "9"), ("111", "3")],
                    hints=["Each ch is a one-character string, so convert before adding.",
                           "Write sum += Number(ch);"]),
                _ex("tscourse-w4-of-5", "Strip the spaces",
                    "Print the input with every space removed, using a loop.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'let out = "";\nfor (const ch of s) {\n  if (ch !== " ") {\n    out += ch;\n  }\n}\nconsole.log(out);\n',
                    'ch !== " "',
                    [("a b c", "abc"), ("hello there", "hellothere"), ("x", "x")],
                    hints=["Append every character that is not a space.",
                           'The test is ch !== " ".']),
                _ex("tscourse-w4-of-6", "Positions with an indexed loop",
                    "Print each character with its position, as `0:h` lines.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'for (let i = 0; i < s.length; i++) {\n  console.log(`${i}:${s[i]}`);\n}\n',
                    'i < s.length',
                    [("hi", "0:h\n1:i"), ("a", "0:a")],
                    hints=["Positions run from 0 up to length - 1.",
                           "The condition is i < s.length."],
                    difficulty="Medium"),
                _fix("tscourse-w4-of-fix1", "Fix the reversal",
                     "This should reverse the string but returns it unchanged. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'let out = "";\nfor (const ch of s) {\n  out = out + ch;\n}\nconsole.log(out);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'let out = "";\nfor (const ch of s) {\n  out = ch + out;\n}\nconsole.log(out);\n',
                     [("abc", "cba"), ("hello", "olleh")],
                     hints=["out + ch appends, which keeps the original order.",
                            "Prepend instead: ch + out."]),
                _fix("tscourse-w4-of-fix2", "Fix the digit sum",
                     "This should print 13 for `4207` but prints `04207`. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'let sum = 0;\nfor (const ch of s) {\n  sum = sum + ch;\n}\nconsole.log(sum);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'let sum = 0;\nfor (const ch of s) {\n  sum = sum + Number(ch);\n}\nconsole.log(sum);\n',
                     [("4207", "13"), ("111", "3")],
                     hints=["ch is a string, so + is joining rather than adding.",
                            "Convert it: sum = sum + Number(ch);"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`for...of` gives you…", ["positions", "values", "keys", "nothing"], 1,
                   "The items themselves. for...in would give keys."),
                _q("Which loop do you need to compare s[i] with s[i - 1]?",
                   ["for...of", "an indexed for", "while(true)", "either"], 1,
                   "Neighbour access needs the index."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w4-control", "break & continue",
            "Leaving early, and skipping a pass.",
            """
Two statements steer a loop from inside it.

**`break` leaves the loop immediately.** The classic use is a search — once
you've found the answer, there's no reason to keep looking:

```ts
let firstDigit = "";
for (const ch of s) {
  if (ch >= "0" && ch <= "9") {
    firstDigit = ch;
    break;                 // stop at the FIRST one
  }
}
```

Without the `break`, the loop keeps going and `firstDigit` ends up holding the
*last* digit instead. One word, opposite meaning.

**`continue` skips the rest of this pass** and goes straight to the next:

```ts
for (let i = 1; i <= n; i++) {
  if (i % 3 !== 0) continue;   // not a multiple of 3? next.
  console.log(i);
}
```

That's the same as wrapping the body in an `if`. `continue` earns its keep when
there are several skip conditions and the real work is long — the skips read as
a list of exclusions at the top, and the body stays unindented.

**Both affect only the innermost loop.** Inside nested loops, `break` leaves the
inner one and the outer one carries on.

**The "found" flag.** After a `break`, you often want to know *whether* you
found anything:

```ts
let found = false;
for (const ch of s) {
  if (ch === target) { found = true; break; }
}
console.log(found ? "yes" : "no");
```

⚠️ With `continue` in a `while` loop, be careful: `continue` jumps to the
condition, skipping anything after it in the body — including your update. That
hangs. In a `for` loop the update lives in the header, so it still runs; this is
one reason `for` is safer for counting.

> ⚠️ **Common mistakes:** forgetting the `break` in a first-match search;
> `continue` in a `while` loop skipping the increment; and using `break` where a
> better-chosen loop condition would have been clearer.
""",
            warmup=[
                _q("`break` does what?",
                   ["Skips one pass", "Leaves the loop", "Restarts the loop", "Ends the program"], 1,
                   "It exits the loop entirely."),
                _q("`continue` does what?",
                   ["Leaves the loop", "Skips the rest of this pass", "Repeats the pass",
                    "Nothing"], 1,
                   "Control moves on to the next iteration."),
                _q("A search loop with no `break` ends up holding…",
                   ["the first match", "the last match", "nothing", "an error"], 1,
                   "It keeps overwriting, so the last match wins."),
            ],
            exercises=[
                _ex("tscourse-w4-ctl-1", "First vowel",
                    "Print the first vowel in the input, then stop looking. Print nothing if there is none.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'for (const ch of s) {\n  if ("aeiou".includes(ch)) {\n    console.log(ch);\n    break;\n  }\n}\n',
                    'break;',
                    [("hello", "e"), ("banana", "a"), ("rhythm", "")],
                    hints=["Once printed, there is no reason to keep going.",
                           "Add break; after the console.log."]),
                _ex("tscourse-w4-ctl-2", "Skip the multiples",
                    "Print 1..n, but skip every multiple of 3.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let i = 1; i <= n; i++) {\n  if (i % 3 === 0) {\n    continue;\n  }\n  console.log(i);\n}\n',
                    'continue;',
                    [("5", "1\n2\n4\n5"), ("3", "1\n2")],
                    hints=["Skip the rest of the pass when the test matches.",
                           "Write continue;"]),
                _ex("tscourse-w4-ctl-3", "Stop at the limit",
                    "Add 1, 2, 3, … to a total and print how many numbers you added before the total passed n.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let total = 0;\nlet count = 0;\n'
                    'for (let i = 1; i <= 1000; i++) {\n  total += i;\n  if (total > n) {\n    break;\n  }\n  count++;\n}\nconsole.log(count);\n',
                    'total > n',
                    [("10", "4"), ("1", "1"), ("0", "0")],
                    hints=["Stop as soon as the running total exceeds n.",
                           "The test is total > n."],
                    difficulty="Medium"),
                _ex("tscourse-w4-ctl-4", "Found or not",
                    "Print `yes` when the input contains a digit, `no` otherwise — using a flag and a break.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'let found = false;\nfor (const ch of s) {\n  if (ch >= "0" && ch <= "9") {\n    found = true;\n    break;\n  }\n}\nconsole.log(found ? "yes" : "no");\n',
                    'found = true;',
                    [("ab3", "yes"), ("abc", "no"), ("7", "yes")],
                    hints=["Record the discovery in the flag before leaving.",
                           "Write found = true;"],
                    difficulty="Medium"),
                _ex("tscourse-w4-ctl-5", "Skip several cases",
                    "Print 1..n, skipping anything divisible by 2 or by 5.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let i = 1; i <= n; i++) {\n  if (i % 2 === 0) continue;\n  if (i % 5 === 0) continue;\n  console.log(i);\n}\n',
                    'if (i % 5 === 0) continue;',
                    [("10", "1\n3\n7\n9"), ("5", "1\n3")],
                    hints=["A second guard, in the same shape as the first.",
                           "Write if (i % 5 === 0) continue;"]),
                _fix("tscourse-w4-ctl-fix1", "Fix the missing break",
                     "This should print the FIRST vowel but prints the last one. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'let out = "";\nfor (const ch of s) {\n  if ("aeiou".includes(ch)) {\n    out = ch;\n  }\n}\nconsole.log(out);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'let out = "";\nfor (const ch of s) {\n  if ("aeiou".includes(ch)) {\n    out = ch;\n    break;\n  }\n}\nconsole.log(out);\n',
                     [("audio", "a"), ("hello", "e")],
                     hints=["Every later vowel overwrites the earlier one.",
                            "Stop after the first: add break;"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Inside nested loops, `break` leaves…",
                   ["both loops", "the innermost loop only", "the program", "nothing"], 1,
                   "Only the loop it sits directly inside."),
                _q("Why can `continue` hang a while loop?",
                   ["It always does", "It can skip the update statement at the bottom of the body",
                    "It leaves the loop", "It resets the condition"], 1,
                   "In a for loop the update is in the header, so it still runs."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w4-digits", "Looping over a number",
            "Taking a number apart with % and Math.floor.",
            """
You can walk the digits of a number without ever turning it into text. Two
operations do all the work:

```ts
n % 10                 // the LAST digit
Math.floor(n / 10)     // n with the last digit removed
```

Put them in a loop and the digits come off one at a time, right to left:

```ts
let n = 4207;
while (n > 0) {
  const digit = n % 10;
  console.log(digit);        // 7, 0, 2, 4
  n = Math.floor(n / 10);
}
```

Trace it:

| pass | n | `n % 10` | n after |
|---|---|---|---|
| 1 | 4207 | 7 | 420 |
| 2 | 420 | 0 | 42 |
| 3 | 42 | 2 | 4 |
| 4 | 4 | 4 | 0 |

The loop ends when `n` reaches 0 — which is also why this pattern prints nothing
for an input of `0`, a boundary worth handling deliberately.

Combined with an accumulator you get digit sums, digit counts, and reversals:

```ts
let sum = 0;
while (n > 0) {
  sum += n % 10;
  n = Math.floor(n / 10);
}
```

**FizzBuzz.** The classic first interview question is just a loop plus the
remainder operator. For 1..n print `Fizz` for multiples of 3, `Buzz` for
multiples of 5, `FizzBuzz` for both, otherwise the number:

```ts
for (let i = 1; i <= n; i++) {
  if (i % 15 === 0) {
    console.log("FizzBuzz");
  } else if (i % 3 === 0) {
    console.log("Fizz");
  } else if (i % 5 === 0) {
    console.log("Buzz");
  } else {
    console.log(i);
  }
}
```

Note the order: the `15` test must come first, because 15 is also a multiple of
3 and would otherwise be caught by the earlier branch. That's lesson 3 of last
week, showing up in real code.

> ⚠️ **Common mistakes:** forgetting `Math.floor` (so `n` becomes a decimal and
> the loop never reaches 0); using `n >= 0` (an infinite loop, since 0 stays 0);
> and getting the FizzBuzz branch order wrong.
""",
            warmup=[
                _q("`4207 % 10` is…", ["4", "7", "420", "0"], 1, "The remainder is the last digit."),
                _q("`Math.floor(4207 / 10)` is…", ["420", "420.7", "421", "7"], 0,
                   "Divide by ten and drop the fraction."),
                _q("`while (n > 0) { n = Math.floor(n / 10); }` with n = 42 runs…",
                   ["once", "twice", "three times", "forever"], 1, "42 -> 4 -> 0."),
                _q("Why must the FizzBuzz `% 15` test come first?",
                   ["It is faster", "15 is also a multiple of 3, so an earlier branch would catch it",
                    "It is required syntax", "It doesn't matter"], 1,
                   "First match wins in a chain."),
            ],
            exercises=[
                _ex("tscourse-w4-dig-1", "Last digit",
                    "Print the last digit of the input number.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(n % 10);\n',
                    'n % 10',
                    [("4207", "7"), ("9", "9"), ("40", "0")],
                    hints=["The remainder after dividing by 10.", "Write n % 10."]),
                _ex("tscourse-w4-dig-2", "Digit sum",
                    "Add up the digits of the number and print the total.",
                    _FS + 'let n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let sum = 0;\nwhile (n > 0) {\n  sum += n % 10;\n  n = Math.floor(n / 10);\n}\nconsole.log(sum);\n',
                    'n = Math.floor(n / 10);',
                    [("4207", "13"), ("9", "9"), ("111", "3")],
                    hints=["After taking the last digit, drop it.",
                           "Write n = Math.floor(n / 10);"]),
                _ex("tscourse-w4-dig-3", "Count the digits",
                    "Print how many digits the number has. (The input is always 1 or more.)",
                    _FS + 'let n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let count = 0;\nwhile (n > 0) {\n  count++;\n  n = Math.floor(n / 10);\n}\nconsole.log(count);\n',
                    'while (n > 0) {',
                    [("4207", "4"), ("9", "1"), ("100", "3")],
                    hints=["Keep peeling until nothing is left.",
                           "The condition is n > 0."]),
                _ex("tscourse-w4-dig-4", "Reverse the number",
                    "Print the digits of the number in reverse order, as a number.",
                    _FS + 'let n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let out = 0;\nwhile (n > 0) {\n  out = out * 10 + (n % 10);\n  n = Math.floor(n / 10);\n}\nconsole.log(out);\n',
                    'out * 10 + (n % 10)',
                    [("123", "321"), ("9", "9"), ("4207", "7024")],
                    hints=["Shift what you have one place left, then add the new digit.",
                           "Write out * 10 + (n % 10)."],
                    difficulty="Medium"),
                _ex("tscourse-w4-dig-5", "FizzBuzz",
                    "For 1..n print Fizz (multiples of 3), Buzz (multiples of 5), FizzBuzz (both), else the number.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let i = 1; i <= n; i++) {\n  if (i % 15 === 0) {\n    console.log("FizzBuzz");\n'
                    '  } else if (i % 3 === 0) {\n    console.log("Fizz");\n'
                    '  } else if (i % 5 === 0) {\n    console.log("Buzz");\n'
                    '  } else {\n    console.log(i);\n  }\n}\n',
                    'i % 15 === 0',
                    [("5", "1\n2\nFizz\n4\nBuzz"),
                     ("15", "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz")],
                    hints=["The narrowest case is 'divisible by both', which means divisible by 15.",
                           "The first test is i % 15 === 0."],
                    difficulty="Medium"),
                _fix("tscourse-w4-dig-fix1", "Fix the decimal drift",
                     "This should print the digit sum but hangs or gives nonsense. Fix it.",
                     _FS + 'let n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let sum = 0;\nwhile (n > 0) {\n  sum += n % 10;\n  n = n / 10;\n}\nconsole.log(sum);\n',
                     _FS + 'let n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let sum = 0;\nwhile (n > 0) {\n  sum += n % 10;\n  n = Math.floor(n / 10);\n}\nconsole.log(sum);\n',
                     [("4207", "13"), ("9", "9")],
                     hints=["Plain division leaves a fraction, which never reaches 0.",
                            "Round it down: Math.floor(n / 10)."],
                     difficulty="Medium"),
                _fix("tscourse-w4-dig-fix2", "Fix the FizzBuzz order",
                     "15 prints `Fizz` instead of `FizzBuzz`. Fix the branch order.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'for (let i = 1; i <= n; i++) {\n  if (i % 3 === 0) {\n    console.log("Fizz");\n'
                     '  } else if (i % 5 === 0) {\n    console.log("Buzz");\n'
                     '  } else if (i % 15 === 0) {\n    console.log("FizzBuzz");\n'
                     '  } else {\n    console.log(i);\n  }\n}\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'for (let i = 1; i <= n; i++) {\n  if (i % 15 === 0) {\n    console.log("FizzBuzz");\n'
                     '  } else if (i % 3 === 0) {\n    console.log("Fizz");\n'
                     '  } else if (i % 5 === 0) {\n    console.log("Buzz");\n'
                     '  } else {\n    console.log(i);\n  }\n}\n',
                     [("15", "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz")],
                     hints=["The %3 branch catches 15 before the %15 branch is ever reached.",
                            "Move the %15 test to the front."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Which pair peels digits off a number?",
                   ["/ and *", "% 10 and Math.floor(/ 10)", "+ and -", "slice and length"], 1,
                   "Remainder gives the last digit; floored division removes it."),
                _q("`while (n >= 0)` in a digit loop…",
                   ["works fine", "never ends, because 0 stays 0", "runs once",
                    "skips the last digit"], 1,
                   "Once n is 0 it stops changing, so the condition stays true."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w4-nested", "Nested loops",
            "A loop inside a loop, for anything with rows and columns.",
            """
Put a loop inside another loop's body and the inner one runs **completely** for
every single pass of the outer one:

```ts
for (let r = 1; r <= 2; r++) {
  for (let c = 1; c <= 3; c++) {
    console.log(`${r},${c}`);
  }
}
```

```
1,1  1,2  1,3  2,1  2,2  2,3      ← six passes: 2 x 3
```

**The cost multiplies.** Two nested loops of n passes each run the inner body
n × n times. For n = 10 that's 100; for n = 1000 it's a million. You'll put a
name to this in Month 6 ("O(n²)"); for now just notice that nesting is where
programs start to get slow.

**Building a row, then printing it.** Printing inside the inner loop puts every
character on its own line. To get a *row*, accumulate a string in the inner loop
and print it in the outer one:

```ts
for (let r = 1; r <= rows; r++) {
  let line = "";
  for (let c = 1; c <= cols; c++) {
    line += "*";
  }
  console.log(line);
}
```

Notice where `line` is declared: **inside the outer loop, outside the inner
one**. It must reset for each row and survive across the columns. Getting that
placement right is the whole exercise.

**Triangles** come from making the inner bound depend on the outer variable:

```ts
for (let r = 1; r <= n; r++) {
  console.log("*".repeat(r));      // *, **, ***, ...
}
```

**Name your variables meaningfully.** `i` and `j` are traditional and become
unreadable the moment the loops are more than three lines long. `row`/`col`,
`i`/`digit`, `outer`/`inner` — anything that says what's being counted.

> ⚠️ **Common mistakes:** declaring the row accumulator in the wrong place (all
> rows join into one, or every row comes out empty); reusing the same variable
> name for both loops; and printing inside the inner loop when you wanted rows.
""",
            warmup=[
                _q("Two nested loops of 3 and 4 passes run the inner body…",
                   ["7 times", "12 times", "3 times", "4 times"], 1, "3 × 4."),
                _q("Where should a per-row accumulator be declared?",
                   ["Before both loops", "Inside the outer loop, before the inner one",
                    "Inside the inner loop", "After both loops"], 1,
                   "It must reset each row but survive the columns."),
                _q('`for (let r=1; r<=3; r++) console.log("*".repeat(r));` prints…',
                   ["three identical lines", "*, **, ***", "***", "nothing"], 1,
                   "The width grows with the row number."),
            ],
            exercises=[
                _ex("tscourse-w4-nest-1", "A rectangle",
                    "Print n rows of 4 stars each.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let r = 1; r <= n; r++) {\n  let line = "";\n  for (let c = 1; c <= 4; c++) {\n    line += "*";\n  }\n  console.log(line);\n}\n',
                    'let line = "";',
                    [("2", "****\n****"), ("1", "****")],
                    hints=["The row accumulator resets each row, so it belongs inside the outer loop.",
                           'Write let line = ""; as the first statement of the outer body.'],
                    difficulty="Medium"),
                _ex("tscourse-w4-nest-2", "A triangle",
                    "Print a left-aligned triangle: row r has r stars.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let r = 1; r <= n; r++) {\n  let line = "";\n  for (let c = 1; c <= r; c++) {\n    line += "*";\n  }\n  console.log(line);\n}\n',
                    'c <= r',
                    [("3", "*\n**\n***"), ("1", "*")],
                    hints=["The inner loop's bound depends on the current row.",
                           "The inner condition is c <= r."],
                    difficulty="Medium"),
                _ex("tscourse-w4-nest-3", "Coordinate grid",
                    "For n rows and n columns print `r,c` on each line.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let r = 1; r <= n; r++) {\n  for (let c = 1; c <= n; c++) {\n    console.log(`${r},${c}`);\n  }\n}\n',
                    '`${r},${c}`',
                    [("2", "1,1\n1,2\n2,1\n2,2")],
                    hints=["Two holes, joined by a comma.",
                           "Write `${r},${c}`."]),
                _ex("tscourse-w4-nest-4", "Multiplication table",
                    "Print an n-by-n multiplication table, values on a row separated by a space.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'for (let r = 1; r <= n; r++) {\n  let line = "";\n  for (let c = 1; c <= n; c++) {\n    line += `${r * c} `;\n  }\n  console.log(line.trim());\n}\n',
                    'line += `${r * c} `;',
                    [("3", "1 2 3\n2 4 6\n3 6 9"), ("1", "1")],
                    hints=["Append the product and a space, then trim the row before printing.",
                           "Write line += `${r * c} `;"],
                    difficulty="Medium"),
                _ex("tscourse-w4-nest-5", "Count the pairs",
                    "Count how many pairs (a, b) with 1 <= a < b <= n exist, and print the count.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let count = 0;\nfor (let a = 1; a <= n; a++) {\n  for (let b = a + 1; b <= n; b++) {\n    count++;\n  }\n}\nconsole.log(count);\n',
                    'let b = a + 1;',
                    [("4", "6"), ("2", "1"), ("1", "0")],
                    hints=["b must be strictly greater than a, so start it one past a.",
                           "Write let b = a + 1;"],
                    difficulty="Medium"),
                _fix("tscourse-w4-nest-fix1", "Fix the runaway row",
                     "This should print n rows of 4 stars but prints one long line at the end. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let line = "";\nfor (let r = 1; r <= n; r++) {\n  for (let c = 1; c <= 4; c++) {\n    line += "*";\n  }\n}\nconsole.log(line);\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'for (let r = 1; r <= n; r++) {\n  let line = "";\n  for (let c = 1; c <= 4; c++) {\n    line += "*";\n  }\n  console.log(line);\n}\n',
                     [("2", "****\n****"), ("1", "****")],
                     hints=["The accumulator is declared before both loops, so every row joins onto the last.",
                            "Move it inside the outer loop and print at the end of each row."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Nesting two n-pass loops runs the inner body…",
                   ["2n times", "n² times", "n times", "n + 2 times"], 1,
                   "Which is why nesting is where performance problems begin."),
                _q("`break` inside the inner of two nested loops…",
                   ["exits both", "exits the inner only", "exits the outer only",
                    "restarts the outer"], 1,
                   "It only affects the loop it is directly inside."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #4 — the savings projection",
        """
Budget Buddy's first real **report**. Read a number of days and print a savings
schedule that adds **$5** every day, then a summary.

For an input of `4`:

```
Day  1: $5
Day  2: $10
Day  3: $15
Day  4: $20
--------------------
Days saved:  4
Total saved: $20
Best day:    $20
```

Details that matter:

- The day number is right-aligned in a **2-character** column (`Day  1`,
  `Day 10`).
- The rule is exactly **20 dashes**.
- `Best day` is the largest single running total — track it with a best-so-far
  accumulator rather than assuming it's the last one.
""",
        _ch("tscourse-w4-capstone", "Budget Buddy #4", "Medium",
            "Loop over the days, keep a running total and a best-so-far, then print the summary.",
            _FS + 'const days = Number(fs.readFileSync(0, "utf8").trim());\n'
            'let total = 0;\n'
            'let best = -Infinity;\n'
            'for (let d = 1; d <= days; d++) {\n'
            '  total += 5;\n'
            '  if (total > best) {\n    best = total;\n  }\n'
            '  console.log(`Day ${String(d).padStart(2)}: $${total}`);\n'
            '}\n'
            'console.log("-".repeat(20));\n'
            'console.log(`Days saved:  ${days}`);\n'
            'console.log(`Total saved: $${total}`);\n'
            'console.log(`Best day:    $${best}`);\n',
            'let total = 0;\n'
            'let best = -Infinity;\n'
            'for (let d = 1; d <= days; d++) {\n'
            '  total += 5;\n'
            '  if (total > best) {\n    best = total;\n  }\n'
            '  console.log(`Day ${String(d).padStart(2)}: $${total}`);\n'
            '}\n'
            'console.log("-".repeat(20));\n'
            'console.log(`Days saved:  ${days}`);\n'
            'console.log(`Total saved: $${total}`);\n'
            'console.log(`Best day:    $${best}`);',
            [("4", "Day  1: $5\nDay  2: $10\nDay  3: $15\nDay  4: $20\n--------------------\nDays saved:  4\nTotal saved: $20\nBest day:    $20"),
             ("1", "Day  1: $5\n--------------------\nDays saved:  1\nTotal saved: $5\nBest day:    $5")],
            hints=["Three accumulators live outside the loop: total, best, and the day counter the for header already gives you.",
                   "Right-align the day with String(d).padStart(2).",
                   'The rule is "-".repeat(20).',
                   "Update best inside the loop, right after total changes: if (total > best) best = total;"]),
        example_io="Day  1: $5\nDay  2: $10\nDay  3: $15\nDay  4: $20\n--------------------\nDays saved:  4\nTotal saved: $20\nBest day:    $20",
        rubric=["One line per day, with the day number right-aligned in two characters",
                "A running total that grows by $5 each day",
                "A 20-dash rule between the schedule and the summary",
                "A best-so-far accumulator, not an assumption about which day is biggest"],
        stretch=_ch("tscourse-w4-capstone-stretch", "Budget Buddy #4 (stretch)", "Medium",
                    "Add a bar chart: after each day's amount, print a `#` for every $5 saved so far. Day 3's line becomes `Day  3: $15 ###`.",
                    _FS + 'const days = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let total = 0;\n'
                    'let best = -Infinity;\n'
                    'for (let d = 1; d <= days; d++) {\n'
                    '  total += 5;\n'
                    '  if (total > best) {\n    best = total;\n  }\n'
                    '  let bar = "";\n'
                    '  for (let b = 1; b <= total / 5; b++) {\n    bar += "#";\n  }\n'
                    '  console.log(`Day ${String(d).padStart(2)}: $${total} ${bar}`);\n'
                    '}\n'
                    'console.log("-".repeat(20));\n'
                    'console.log(`Days saved:  ${days}`);\n'
                    'console.log(`Total saved: $${total}`);\n'
                    'console.log(`Best day:    $${best}`);\n',
                    'let bar = "";\n'
                    '  for (let b = 1; b <= total / 5; b++) {\n    bar += "#";\n  }\n'
                    '  console.log(`Day ${String(d).padStart(2)}: $${total} ${bar}`);',
                    [("3", "Day  1: $5 #\nDay  2: $10 ##\nDay  3: $15 ###\n--------------------\nDays saved:  3\nTotal saved: $15\nBest day:    $15")],
                    hints=["Build the bar with an inner loop — the bar accumulator resets each day.",
                           "The number of hashes is total / 5.",
                           "Append the bar to the day's line with one space before it."]),
    ),
))
