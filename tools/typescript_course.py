# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The 8-month structured TypeScript course (POLISHED build).
#
# exec()'d inside gen_seed.py's namespace AFTER the other TypeScript files, so it
# can reuse `_P` (program normalizer). Defines a single global `TS_COURSE` (dict)
# which gen_seed writes to src-tauri/seeds/ts_course.json (served by `ts_course`).
#
# HARD DESIGN RULE (the user's core ask): a week may only require syntax/concepts
# introduced in that week or earlier. A gen-time `_lint_scope` check at the end
# enforces this by scanning every program for constructs that appear before the
# week that teaches them (loops<W4, functions<W5, array methods<W6, reduce<W8,
# object literals<W7). If you add content that violates the ladder, generation
# FAILS loudly.
#
# EXECUTION MODEL: exercises run through the same stdin/stdout judge as every
# Learn drill (Node type-stripping). Every blank targets RUNTIME code; programs
# read stdin with `fs.readFileSync(0,"utf8")`; output is matched exactly (after
# whitespace normalization). Each `solution` is verified end-to-end by
# tests/verify_ts_course.rs and a Node verifier.
#
# EXERCISE KINDS: "drill" (fill one ____ blank), "challenge"/"capstone" (write a
# whole solution where you see ____), "fix" (a complete but buggy program the
# learner corrects — no blank; starter=buggy, solution=fixed).
# ---------------------------------------------------------------------------


def _prog(src):
    return _P(src)


def _q(question, options, answer, explanation):
    return {"question": question, "options": options, "answer": answer,
            "explanation": explanation}


def _gloss(term, definition):
    return {"term": term, "def": definition}


def _tests(pairs):
    return [{"input": i, "output": o} for (i, o) in pairs]


def _mk(eid, title, prompt, full, tests, hints, difficulty, kind, starter=None,
        blank=None):
    """Build a course Exercise dict. Either `blank` (a unique substring of `full`
    replaced by ____ to form the starter) OR an explicit `starter` (for "fix")."""
    full = _prog(full)
    if starter is None:
        assert blank is not None, f"{eid}: need blank or starter"
        assert blank in full, f"{eid}: blank not found in solution: {blank!r}"
        starter = full.replace(blank, "____", 1)
        assert starter != full, f"{eid}: no blank applied"
    else:
        starter = _prog(starter)
        assert starter != full, f"{eid}: starter equals solution"
    assert tests, f"{eid}: needs at least one test"
    hints = list(hints or [])
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "",
        "hints": hints, "language": "typescript",
        "kind": kind, "difficulty": difficulty,
        "starter": starter, "solution": full, "tests": _tests(tests),
        "source_slug": "", "dataset": "",
    }


def _ex(eid, title, prompt, full, blank, tests, hints=(), difficulty="Intro"):
    return _mk(eid, title, prompt, full, tests, hints, difficulty, "drill", blank=blank)


def _ch(eid, title, difficulty, prompt, full, blank, tests, hints=()):
    return _mk(eid, title, prompt, full, tests, hints, difficulty, "challenge", blank=blank)


def _fix(eid, title, prompt, buggy, fixed, tests, hints=(), difficulty="Easy"):
    return _mk(eid, title, prompt, fixed, tests, hints, difficulty, "fix", starter=buggy)


def _lesson(key, title, what, lesson_md, exercises, warmup=None, quiz=None):
    return {"key": key, "title": title, "what": what,
            "lesson": _prog(lesson_md) if lesson_md else "",
            "warmup": warmup or [], "exercises": exercises, "quiz": quiz or []}


def _cap_auto(title, brief, exercise, example_io="", rubric=None, stretch=None):
    return {"title": title, "brief": _prog(brief), "kind": "auto",
            "exercise": exercise, "example_io": example_io,
            "rubric": rubric or [], "reference": "", "stretch": stretch}


def _cap_brief(title, brief, reference="", rubric=None, stretch=None):
    return {"title": title, "brief": _prog(brief), "kind": "brief",
            "exercise": None, "example_io": "",
            "rubric": rubric or [], "reference": _prog(reference) if reference else "",
            "stretch": stretch}


def _week(number, month, month_title, theme, goal, summary, lessons, capstone=None,
          objectives=None, why="", est_minutes=40, glossary=None, cheatsheet="",
          self_check=None, review=None, milestone="", authored=True):
    return {
        "number": number, "month": month, "month_title": month_title,
        "theme": theme, "goal": goal, "summary": _prog(summary) if summary else "",
        "authored": authored, "lessons": lessons, "capstone": capstone,
        "objectives": objectives or [], "why": why, "est_minutes": est_minutes,
        "glossary": glossary or [], "cheatsheet": _prog(cheatsheet) if cheatsheet else "",
        "self_check": self_check or [], "review": review or [], "milestone": milestone,
    }


def _skel(number, month, month_title, theme, goal, summary=""):
    return _week(number, month, month_title, theme, goal, summary, [], None,
                 authored=False)


_FS = 'import * as fs from "fs";\n'
_WEEKS = []

# ===========================================================================
# MONTH 1 — Absolute basics: output, values, decisions, loops
# ===========================================================================
_M1 = "First Steps: Values, Logic & Loops"

# --- Week 1 ---------------------------------------------------------------
_WEEKS.append(_week(
    1, 1, _M1,
    "Values, Variables & Output",
    "Write programs that hold values in named variables, compute with them, and print exactly the text you intend.",
    """
Welcome — this is the very beginning, and it assumes **nothing**. By the end of
this week you'll have written a few dozen small programs that print things,
remember things, and do arithmetic. That sounds modest, but it genuinely is
what most code does: take some values, combine them, show a result.

**How to work through a week.** Each lesson has four parts:

1. **Read** the explanation — short, with a worked example.
2. **Predict the output** — guess before you run. Guessing wrong is the single
   fastest way to fix a wrong mental model, so answer honestly.
3. **Practice** — fill in the `____` and press **Check**. Your code really runs.
4. **Fix the bug** — a complete program that looks right but isn't.

Plan on roughly **five hours** for the week. Nobody does that in one sitting —
one lesson per session is a perfectly good pace, and the page remembers what
you've solved.
""",
    objectives=[
        "Print exact text, numbers, and several values at once with console.log",
        "Store values in const and let, and know which to reach for",
        "Compute with + - * / % and control the order with parentheses",
        "Round and truncate numbers with Math.round, Math.floor and toFixed",
        "Join text with + and with template literals",
        "Name the type of a value, annotate a variable, and convert between text and numbers",
    ],
    why="Every program you will ever write holds values and shows results. Everything later — decisions, loops, functions, whole applications — is built on this floor.",
    est_minutes=280,
    glossary=[
        _gloss("statement", "One instruction. Statements run top to bottom, usually one per line, ending in a semicolon."),
        _gloss("expression", "Anything that produces a value: 2 + 3, \"hi\", price * qty."),
        _gloss("string", "Text. Written inside quotes: \"hello\"."),
        _gloss("number", "TypeScript's one numeric type — it covers 7 and 7.5 alike."),
        _gloss("boolean", "A value that is either true or false."),
        _gloss("variable", "A named box holding a value."),
        _gloss("const", "Declares a name whose value is never reassigned. Your default."),
        _gloss("let", "Declares a name you intend to reassign later."),
        _gloss("declaration", "The first mention, with let/const. You declare a name once."),
        _gloss("assignment", "Putting a value into an already-declared name: count = 5."),
        _gloss("operator", "A symbol combining values: + - * / %."),
        _gloss("operand", "A value an operator works on. In a * b, a and b are the operands."),
        _gloss("precedence", "Which operator binds tighter. * and / happen before + and -."),
        _gloss("concatenation", "Joining strings with +."),
        _gloss("escape sequence", "A backslash code inside a string: \\n newline, \\\" a quote, \\\\ a backslash."),
        _gloss("template literal", "A backtick string with ${...} holes: `Hi ${name}`."),
        _gloss("annotation", "The `: number` in `const n: number = 5` — a note to the compiler about the type."),
        _gloss("typeof", "An operator reporting a value's type as a string: typeof 5 is \"number\"."),
        _gloss("comment", "Text the computer ignores: // to end of line, or /* ... */."),
    ],
    cheatsheet="""
```ts
// ---- printing -------------------------------------------------------
console.log("hi");            // prints: hi
console.log("Total:", 42);    // prints: Total: 42   (a space between args)
console.log(6 * 7);           // prints: 42
// this line is a comment — ignored

// ---- variables ------------------------------------------------------
const name = "Ada";           // never reassigned  <- your default
let count = 0;                // will be reassigned
count = count + 1;            // assignment (no second `let`)

// ---- annotations ----------------------------------------------------
const price: number = 3;
const label: string = "Coffee";
const paid: boolean = true;

// ---- arithmetic -----------------------------------------------------
6 * 7                         // 42
17 % 5                        // 2      remainder
10 / 4                        // 2.5    always a decimal
2 + 3 * 4                     // 14     * before +
(2 + 3) * 4                   // 20     parentheses win

Math.floor(7 / 2)             // 3      chop toward zero-ish (down)
Math.round(2.6)               // 3
Math.max(3, 9)                // 9
(0.1 + 0.2).toFixed(2)        // "0.30" fixed decimal places (a string!)

// ---- text -----------------------------------------------------------
"a" + "b"                     // "ab"
"Line 1\\nLine 2"              // \\n is a newline inside one string
`Hi ${name}, you owe $${total}`   // template literal

// ---- types & conversion ---------------------------------------------
typeof 5                      // "number"
typeof "5"                    // "string"
"5" + 3                       // "53"   <- + joined them!
Number("5") + 3               // 8      convert first
String(42) + "!"              // "42!"
```
""",
    self_check=[
        "Can you print an exact line of text, including punctuation and spacing?",
        "Can you explain, in your own words, when to use const and when to use let?",
        "Can you predict what 2 + 3 * 4 gives, and how to make it 20 instead?",
        "Can you say why \"5\" + 3 is \"53\" and how to get 8?",
        "Can you write the same output line twice — once with + and once with a template literal?",
        "Can you compute a total from a price and a quantity and print it with two decimal places?",
    ],
    review=[
        _q("Which declares a value that is never reassigned?",
           ["let x = 1", "const x = 1", "x = 1", "number x = 1"], 1,
           "const fixes the binding. Reach for it first; switch to let only when you actually reassign."),
        _q("What does `17 % 5` evaluate to?", ["3", "2", "3.4", "12"], 1,
           "% is the remainder: 17 = 3*5 + 2, so 2."),
        _q('What does `console.log("5" + 3)` print?', ["8", "53", "\"53\"", "an error"], 1,
           'The left side is a string, so + joins rather than adds: "53".'),
        _q("What does `2 + 3 * 4` evaluate to?", ["20", "14", "24", "9"], 1,
           "* binds tighter than +, so it's 2 + 12 = 14."),
        _q("What does `console.log(\"Total:\", 7)` print?",
           ["Total:7", "Total: 7", "Total: , 7", "Total:"], 1,
           "console.log separates its arguments with a single space."),
        _q("Which is TRUE of `const total = 10 / 4;`?",
           ["total is 2", "total is 2.5", "total is 3", "it is an error"], 1,
           "There is no integer division in TypeScript — / keeps the decimal."),
        _q("What is `typeof true`?", ['"true"', '"boolean"', '"number"', "true"], 1,
           "typeof reports the type name as a string: \"boolean\"."),
        _q("`(2.345).toFixed(1)` produces…", ["2.3", '"2.3"', "2", '"2.35"'], 1,
           "toFixed returns a STRING with that many decimal places."),
        _q("You wrote `let n = 1;` then want n to be 5. Which line is right?",
           ["let n = 5;", "n = 5;", "const n = 5;", "n == 5;"], 1,
           "The name is already declared — reassignment is just `n = 5;`."),
        _q("What does `console.log(`${2 + 3} apples`)` print?",
           ["${2 + 3} apples", "5 apples", "2 + 3 apples", "23 apples"], 1,
           "Any expression inside ${ } is evaluated first."),
    ],
    milestone="You can write a program that prints a formatted, computed receipt. That is real, working code — the same shape as the billing line in a real checkout.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w1-hello", "Your first program",
            "Statements, console.log, and comments.",
            """
A **program** is a list of **statements** run strictly top to bottom. The
statement you'll use most is `console.log(...)`, which prints its argument and
then moves to a new line.

```ts
console.log("Hello, world!");
```

Three things are happening there:

| piece | name | meaning |
|---|---|---|
| `console.log` | the thing being called | "print this" |
| `( ... )` | parentheses | what to print goes inside |
| `"Hello, world!"` | a **string** | text; the quotes mark where it starts and ends |

The quotes are *not* printed — they only tell TypeScript "the text starts
here and ends here".

**Several values at once.** Separate them with commas and `console.log` joins
them with a single space:

```ts
console.log("Total:", 42);   // Total: 42
console.log("a", "b", "c");  // a b c
```

**Arithmetic prints its result, not the sum you typed:**

```ts
console.log(2 + 3);     // 5     — no quotes, so it's a calculation
console.log("2 + 3");   // 2 + 3 — quotes, so it's just text
```

That difference — *value* versus *text that looks like a value* — is the single
most important idea this week.

**Comments** are notes for humans; the computer skips them entirely:

```ts
// everything after two slashes on this line is ignored
console.log("run"); // ...including a note after a statement
```

> ⚠️ **Common mistakes:** forgetting the quotes around text (TypeScript then
> thinks you're naming a variable that doesn't exist); forgetting the
> parentheses — it is `console.log("hi")`, never `console.log "hi"`; and
> expecting `console.log` to print quotes it never prints.
""",
            warmup=[
                _q('What does `console.log("Hi")` print?',
                   ['"Hi"', "Hi", "Hi (with quotes)", "nothing"], 1,
                   "The quotes delimit the string; they are not part of it."),
                _q("What does `console.log(2 + 3)` print?",
                   ["2 + 3", "23", "5", '"5"'], 2,
                   "No quotes, so it is arithmetic: 5."),
                _q('What does `console.log("2 + 3")` print?',
                   ["5", "2 + 3", "23", "error"], 1,
                   "Inside quotes it is plain text, printed as written."),
                _q('What does `console.log("Score:", 10)` print?',
                   ["Score:10", "Score: 10", "Score:, 10", "Score: \"10\""], 1,
                   "Arguments are separated by exactly one space."),
            ],
            exercises=[
                _ex("tscourse-w1-hello-1", "Print a greeting",
                    "Make the program print exactly: Hello, world!",
                    'console.log("Hello, world!");\n',
                    '"Hello, world!"', [("", "Hello, world!")],
                    hints=["A string is text between double quotes.",
                           'Put "Hello, world!" inside the parentheses.']),
                _ex("tscourse-w1-hello-2", "Print two lines",
                    "Print `Line one` then `Line two`, each on its own line.",
                    'console.log("Line one");\nconsole.log("Line two");\n',
                    'console.log("Line two");', [("", "Line one\nLine two")],
                    hints=["Each console.log ends with a newline of its own.",
                           'The second statement is console.log("Line two");']),
                _ex("tscourse-w1-hello-3", "A label and a value",
                    "Print `Total: 42` using ONE console.log with two arguments.",
                    'console.log("Total:", 42);\n',
                    '"Total:", 42', [("", "Total: 42")],
                    hints=["Two arguments separated by a comma get one space between them.",
                           'Write "Total:", 42 inside the parentheses.']),
                _ex("tscourse-w1-hello-4", "Print a calculation",
                    "Print the result of 12 times 12 (not the text `12 * 12`).",
                    'console.log(12 * 12);\n',
                    '12 * 12', [("", "144")],
                    hints=["No quotes — you want the value, not the text.",
                           "Write 12 * 12 with no quotes around it."]),
                _ex("tscourse-w1-hello-5", "A blank line between",
                    "Print `top`, then an empty line, then `bottom`.",
                    'console.log("top");\nconsole.log("");\nconsole.log("bottom");\n',
                    'console.log("");', [("", "top\n\nbottom")],
                    hints=["An empty string is just two quotes with nothing between.",
                           'The middle statement is console.log("");']),
                _fix("tscourse-w1-hello-fix1", "Fix the greeting",
                     "This is supposed to print `Hello!` but prints something else. Fix it.",
                     'console.log("Goodbye!");\n',
                     'console.log("Hello!");\n',
                     [("", "Hello!")],
                     hints=["Only the text inside the quotes is wrong.",
                            'Change "Goodbye!" to "Hello!".']),
                _fix("tscourse-w1-hello-fix2", "Fix the quoted sum",
                     "This should print the number 9, but prints the text `4 + 5` instead. Fix it.",
                     'console.log("4 + 5");\n',
                     'console.log(4 + 5);\n',
                     [("", "9")],
                     hints=["Quotes turn a calculation into plain text.",
                            "Remove the quotes so 4 + 5 is actually computed."]),
            ],
            quiz=[
                _q("Statements in a program run…",
                   ["in a random order", "top to bottom", "bottom to top",
                    "only if you ask"], 1,
                   "Top to bottom, one after another."),
                _q("What is printed by `console.log(\"3\", 3);`?",
                   ["3 3", "33", "6", '"3" 3'], 0,
                   'Both print as 3, separated by a space — the string "3" and the number 3 look identical when printed.'),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w1-variables", "Naming values: const and let",
            "Storing a value so you can use it more than once.",
            """
A **variable** is a name attached to a value. You **declare** it once — with
`const` or `let` — and use the name everywhere after.

```ts
const name = "Ada";
console.log(name);          // Ada
console.log("Hi, " + name); // Hi, Ada
```

**Declaration vs assignment.** The first mention creates the name; later
mentions just put a new value in it. You never repeat `let`:

```ts
let count = 1;     // declaration  (creates `count`)
count = 2;         // assignment   (no `let`!)
count = count + 1; // reads 2, adds 1, stores 3
```

That last line reads strangely if you think `=` means "equals". It doesn't —
`=` means **"put the value on the right into the name on the left."** The right
side is worked out first.

**const vs let.** `const` means *this name will never be reassigned*:

```ts
const rate = 0.08;
rate = 0.09;   // ❌ error: cannot assign to a constant
```

**Reach for `const` by default.** Use `let` only when you genuinely need the
value to change. A `const` is a promise to your future self that this name
means one thing throughout — which makes code far easier to read.

**Naming.** Names use letters, digits, `_` and `$`, and can't start with a
digit. The convention is `camelCase`: `lineTotal`, `taxRate`, `userName`.
Choose names that say what the value *means*: `qty` beats `q`, `n2` means
nothing to anyone.

> ⚠️ **Common mistakes:** writing `let` a second time when reassigning (that's
> a redeclaration error); trying to reassign a `const`; and using a name before
> the line that declares it.
""",
            warmup=[
                _q("After `let n = 1; n = n + 4;`, what is `n`?",
                   ["1", "5", "14", "4"], 1, "n + 4 is 5, and that is stored back into n."),
                _q("After `let a = 2; let b = a; a = 9;`, what is `b`?",
                   ["9", "2", "11", "error"], 1,
                   "b copied the VALUE 2 at that moment; changing a afterwards doesn't touch b."),
                _q("Which line is an error?",
                   ["let x = 1;", "const y = 2;", "let x = 1; let x = 3;", "let z = 1; z = 3;"], 2,
                   "You may only declare a given name once in the same scope."),
            ],
            exercises=[
                _ex("tscourse-w1-var-1", "Name a value",
                    "Store `Ada` in `name` so the program prints `Hello, Ada`.",
                    'const name = "Ada";\nconsole.log("Hello, " + name);\n',
                    '"Ada"', [("", "Hello, Ada")],
                    hints=["The value is a string, so it needs quotes.",
                           'Set name to "Ada".']),
                _ex("tscourse-w1-var-2", "Reassign with let",
                    "Reassign `count` to 2 so the program prints 2.",
                    'let count = 1;\ncount = 2;\nconsole.log(count);\n',
                    'count = 2;', [("", "2")],
                    hints=["Reassignment does not repeat `let`.",
                           "The line is exactly `count = 2;`."]),
                _ex("tscourse-w1-var-3", "Use a name twice",
                    "Print the item name on both lines, using the variable each time.",
                    'const item = "Coffee";\nconsole.log("Item: " + item);\nconsole.log("Thanks for buying " + item);\n',
                    '"Thanks for buying " + item',
                    [("", "Item: Coffee\nThanks for buying Coffee")],
                    hints=["Join the fixed text and the variable with +.",
                           'Write "Thanks for buying " + item — mind the trailing space inside the quotes.']),
                _ex("tscourse-w1-var-4", "Grow a running count",
                    "Add 3 to `score`, then add 4, so the program prints 7.",
                    'let score = 0;\nscore = score + 3;\nscore = score + 4;\nconsole.log(score);\n',
                    'score = score + 4;', [("", "7")],
                    hints=["Read the current value, add to it, store it back.",
                           "The second line is `score = score + 4;`."]),
                _ex("tscourse-w1-var-5", "Swap in a helper name",
                    "Introduce `total` so the printed line stays `Total: 30`.",
                    'const price = 10;\nconst qty = 3;\nconst total = price * qty;\nconsole.log("Total: " + total);\n',
                    'const total = price * qty;', [("", "Total: 30")],
                    hints=["Naming the intermediate result makes the last line readable.",
                           "Declare `const total = price * qty;`."]),
                _fix("tscourse-w1-var-fix1", "Fix the redeclaration",
                     "This should print 10 but crashes. Fix it so it prints 10.",
                     'let total = 4;\nlet total = 10;\nconsole.log(total);\n',
                     'let total = 4;\ntotal = 10;\nconsole.log(total);\n',
                     [("", "10")],
                     hints=["A name may only be declared once.",
                            "The second line should reassign, not redeclare — drop the `let`."]),
                _fix("tscourse-w1-var-fix2", "Fix the const",
                     "This should print 20, but assigning to a const is an error. Change the declaration so the program works.",
                     'const budget = 10;\nbudget = 20;\nconsole.log(budget);\n',
                     'let budget = 10;\nbudget = 20;\nconsole.log(budget);\n',
                     [("", "20")],
                     hints=["The value here really does need to change.",
                            "Declare it with `let` instead of `const`."]),
            ],
            quiz=[
                _q("What does `=` mean in `total = price * qty;`?",
                   ["is equal to", "put the right-hand value into the left-hand name",
                    "compare the two sides", "declare a constant"], 1,
                   "`=` is assignment. Comparison comes later, and uses `===`."),
                _q("Which should you reach for by default?",
                   ["let", "const", "whichever", "neither — skip the declaration"], 1,
                   "const first; switch to let only when you actually reassign."),
                _q("Which is the best name for a coffee's price?",
                   ["p", "x2", "coffeePrice", "COFFEE_price_value_number"], 2,
                   "Say what it means, in camelCase, without padding."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w1-numbers", "Numbers & arithmetic",
            "One number type, five operators, and the order they happen in.",
            """
TypeScript has **one** numeric type, `number`, covering `7` and `7.5` alike.
There is no separate integer type — and, importantly, **no integer division**:

```ts
10 / 4      // 2.5   (not 2)
```

The five operators:

| operator | name | example | result |
|---|---|---|---|
| `+` | add | `4 + 5` | `9` |
| `-` | subtract | `9 - 4` | `5` |
| `*` | multiply | `6 * 7` | `42` |
| `/` | divide | `10 / 4` | `2.5` |
| `%` | remainder | `17 % 5` | `2` |

**Remainder (`%`)** is what's left after dividing as many whole times as
possible: 17 ÷ 5 is 3 with 2 left over, so `17 % 5` is `2`. It's how you test
"is this even?" (`n % 2` is 0) or "what's the last digit?" (`n % 10`).

**Precedence.** `*`, `/` and `%` happen before `+` and `-`, exactly as in school
maths. Parentheses override that:

```ts
2 + 3 * 4      // 14   (3*4 first)
(2 + 3) * 4    // 20   (parentheses first)
```

When in doubt, add parentheses. They cost nothing and they document intent.

**Rounding.** `Math` holds a toolbox of number helpers:

```ts
Math.floor(2.9)   // 2    always down
Math.ceil(2.1)    // 3    always up
Math.round(2.5)   // 3    to nearest, .5 goes up
Math.abs(-4)      // 4    distance from zero
Math.max(3, 9)    // 9
Math.min(3, 9)    // 3
```

`Math.floor(a / b)` is how you get "whole divisions only": `Math.floor(17 / 5)`
is `3`.

**Decimals lie a little.** Computers store decimals in binary, and some
fractions don't fit exactly:

```ts
console.log(0.1 + 0.2);   // 0.30000000000000004
```

That is not a bug in your code — it's how binary fractions work everywhere.
When you're *displaying* money, fix the decimal places:

```ts
console.log((0.1 + 0.2).toFixed(2));   // 0.30
```

Note `toFixed` hands back a **string**, ready for printing.

> ⚠️ **Common mistakes:** expecting `10 / 3` to be a whole number; mixing up `/`
> with `%`; and forgetting parentheses in a formula like `(a + b) / 2`, which
> without them means `a + (b / 2)`.
""",
            warmup=[
                _q("What does `console.log(10 / 4)` print?",
                   ["2", "2.5", "3", "2.4"], 1, "Division keeps the decimal part."),
                _q("What does `console.log(9 % 2)` print?",
                   ["4.5", "0", "1", "4"], 2, "9 = 4*2 + 1, so the remainder is 1."),
                _q("What does `console.log(2 + 3 * 4)` print?",
                   ["20", "14", "24", "9"], 1, "* binds tighter: 2 + 12."),
                _q("What does `console.log(Math.floor(7 / 2))` print?",
                   ["3.5", "4", "3", "3.0"], 2, "7/2 is 3.5; floor rounds down to 3."),
            ],
            exercises=[
                _ex("tscourse-w1-num-1", "Multiply",
                    "Print the product of `a` and `b` (it should be 42).",
                    'const a = 6;\nconst b = 7;\nconsole.log(a * b);\n',
                    'a * b', [("", "42")],
                    hints=["Use the * operator.", "Write `a * b`."]),
                _ex("tscourse-w1-num-2", "Remainder",
                    "Print the remainder when `total` is divided by 5.",
                    'const total = 17;\nconsole.log(total % 5);\n',
                    'total % 5', [("", "2")],
                    hints=["`%` gives what is left over.", "Write `total % 5`."]),
                _ex("tscourse-w1-num-3", "Average of two",
                    "Print the average of `a` and `b`. Mind the parentheses!",
                    'const a = 4;\nconst b = 9;\nconsole.log((a + b) / 2);\n',
                    '(a + b) / 2', [("", "6.5")],
                    hints=["Add first, then halve.",
                           "Without parentheses you would get a + (b / 2). Write (a + b) / 2."]),
                _ex("tscourse-w1-num-4", "Whole divisions only",
                    "How many whole 5s fit in 17? Print 3, using Math.floor.",
                    'const total = 17;\nconsole.log(Math.floor(total / 5));\n',
                    'Math.floor(total / 5)', [("", "3")],
                    hints=["17 / 5 is 3.4; you want it rounded down.",
                           "Wrap the division: Math.floor(total / 5)."]),
                _ex("tscourse-w1-num-5", "Money to two decimals",
                    "Print the total to exactly two decimal places: 21.75",
                    'const price = 7.25;\nconst qty = 3;\nconsole.log((price * qty).toFixed(2));\n',
                    '(price * qty).toFixed(2)', [("", "21.75")],
                    hints=["Compute first, then fix the decimals.",
                           "Write (price * qty).toFixed(2)."]),
                _ex("tscourse-w1-num-6", "Last digit",
                    "Print the last digit of `code` (should be 7).",
                    'const code = 40127;\nconsole.log(code % 10);\n',
                    'code % 10', [("", "7")],
                    hints=["The remainder after dividing by 10 is the last digit.",
                           "Write code % 10."]),
                _fix("tscourse-w1-num-fix1", "Fix the total",
                     "This should print the SUM of a and b (8) but prints something else.",
                     'const a = 5;\nconst b = 3;\nconsole.log(a - b);\n',
                     'const a = 5;\nconst b = 3;\nconsole.log(a + b);\n',
                     [("", "8")],
                     hints=["Look closely at the operator between a and b.",
                            "A sum uses + , not - ."]),
                _fix("tscourse-w1-num-fix2", "Fix the precedence bug",
                     "This should print the average of 4 and 10 (7) but prints 9. Fix it.",
                     'const a = 4;\nconst b = 10;\nconsole.log(a + b / 2);\n',
                     'const a = 4;\nconst b = 10;\nconsole.log((a + b) / 2);\n',
                     [("", "7")],
                     hints=["/ happens before +, so right now it computes 4 + 5.",
                            "Parenthesise the addition: (a + b) / 2."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("How do you test whether `n` is even?",
                   ["n / 2 === 0", "n % 2 === 0", "Math.floor(n) === n", "n * 2 === n"], 1,
                   "An even number leaves remainder 0 when divided by 2."),
                _q("`(2.5).toFixed(0)` gives you…",
                   ["the number 3", 'the string "3"', "the number 2", "an error"], 1,
                   "toFixed always returns a string — handy for printing, not for further maths."),
                _q("Why does `0.1 + 0.2` print 0.30000000000000004?",
                   ["A TypeScript bug", "Binary can't represent some decimal fractions exactly",
                    "console.log is broken", "0.1 isn't a number"], 1,
                   "It's how binary floating point works — true in nearly every language."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w1-strings", "Strings: quotes, joining & escapes",
            "Building exact text out of pieces.",
            """
A **string** is text. Double quotes and single quotes both work — pick one and
stay consistent (this course uses double):

```ts
const a = "hello";
const b = 'hello';   // identical
```

**Joining (concatenation)** uses `+`:

```ts
const name = "Ada";
console.log("Hello, " + name + "!");   // Hello, Ada!
```

Spacing is *literal*. `"Hello," + name` produces `Hello,Ada` — the space has to
be inside the quotes: `"Hello, "`. Nearly every wrong-output moment this week
will be a missing or extra space.

**Mixing text and numbers.** When either side of `+` is a string, `+` joins
instead of adding:

```ts
console.log("Total: " + 42);   // Total: 42
```

That's convenient here, and a trap later (lesson 6).

**Escape sequences** put otherwise-impossible characters inside a string. A
backslash starts one:

| escape | meaning |
|---|---|
| `\\n` | newline |
| `\\t` | tab |
| `\\"` | a literal double quote |
| `\\\\` | a literal backslash |

```ts
console.log("Line 1\\nLine 2");     // prints TWO lines from ONE call
console.log("She said \\"hi\\"");     // She said "hi"
```

**Handy for output:** `"-".repeat(20)` builds a 20-character rule, which is how
you draw a separator line without typing twenty dashes.

> ⚠️ **Common mistakes:** forgetting the space inside the quotes; putting a
> `"` inside a `"`-quoted string without escaping it; and writing `\\n` outside
> a string, where it means nothing.
""",
            warmup=[
                _q('What does `console.log("a" + "b")` print?',
                   ["a b", "ab", "a+b", '"ab"'], 1, "Concatenation glues them with nothing between."),
                _q('What does `console.log("Hi," + "Bo")` print?',
                   ["Hi, Bo", "Hi,Bo", "HiBo", "Hi, + Bo"], 1,
                   "There is no space in either string, so none appears."),
                _q('How many lines does `console.log("a\\nb")` print?',
                   ["1", "2", "3", "0"], 1, "\\n is a newline inside the one string."),
            ],
            exercises=[
                _ex("tscourse-w1-str-1", "Join with a space",
                    "Print `Hello, Ada!` — mind the space after the comma.",
                    'const name = "Ada";\nconsole.log("Hello, " + name + "!");\n',
                    '"Hello, " + name + "!"', [("", "Hello, Ada!")],
                    hints=["The space has to live inside the quotes.",
                           'Write "Hello, " + name + "!".']),
                _ex("tscourse-w1-str-2", "Two lines from one call",
                    "Using ONE console.log, print `top` then `bottom` on separate lines.",
                    'console.log("top\\nbottom");\n',
                    '"top\\nbottom"', [("", "top\nbottom")],
                    hints=["\\n inside a string is a newline.",
                           'Write "top\\nbottom".']),
                _ex("tscourse-w1-str-3", "Quote inside a quote",
                    'Print exactly: She said "hi"',
                    'console.log("She said \\"hi\\"");\n',
                    '"She said \\"hi\\""', [("", 'She said "hi"')],
                    hints=['A " inside a "-string must be escaped as \\".',
                           'Write "She said \\"hi\\"".']),
                _ex("tscourse-w1-str-4", "Draw a rule",
                    "Print a line of exactly 10 dashes, using repeat.",
                    'console.log("-".repeat(10));\n',
                    '"-".repeat(10)', [("", "----------")],
                    hints=["repeat makes n copies of a string.",
                           'Write "-".repeat(10).']),
                _ex("tscourse-w1-str-5", "Label a number",
                    "Print `Items: 3` by joining text and a number with +.",
                    'const count = 3;\nconsole.log("Items: " + count);\n',
                    '"Items: " + count', [("", "Items: 3")],
                    hints=["When one side of + is text, the other is converted for you.",
                           'Write "Items: " + count.']),
                _fix("tscourse-w1-str-fix1", "Fix the missing space",
                     "This prints `Hello,Ada` but should print `Hello, Ada`. Fix it.",
                     'const name = "Ada";\nconsole.log("Hello," + name);\n',
                     'const name = "Ada";\nconsole.log("Hello, " + name);\n',
                     [("", "Hello, Ada")],
                     hints=["Nothing adds a space for you.",
                            'Put the space inside the quotes: "Hello, ".']),
                _fix("tscourse-w1-str-fix2", "Fix the escape",
                     "This was meant to print a real newline between the words, but prints the backslash-n. Fix it.",
                     'console.log("top" + "\\\\n" + "bottom");\n',
                     'console.log("top" + "\\n" + "bottom");\n',
                     [("", "top\nbottom")],
                     hints=["\\\\ is an escaped backslash — it prints a literal \\.",
                            'A newline is a single backslash then n: "\\n".']),
            ],
            quiz=[
                _q('What is the length of the printed output of `console.log("a\\tb")`?',
                   ["it prints a, a tab, then b", "it prints a\\tb literally",
                    "it prints ab", "it errors"], 0,
                   "\\t is a tab character."),
                _q('`"ab".repeat(3)` is…', ['"ababab"', '"ab3"', '"aaabbb"', "an error"], 0,
                   "repeat concatenates that many copies."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w1-templates", "Template literals",
            "The readable way to build a line of text.",
            """
Building a line with `+` gets noisy fast:

```ts
console.log("Item: " + item + " x" + qty + " = $" + total);
```

A **template literal** uses **backticks** (`` ` ``, the key left of `1` on most
keyboards) and drops values straight into the text with `${ }`:

```ts
console.log(`Item: ${item} x${qty} = $${total}`);
```

Same output, and you can *see* the shape of the line. Notice `$${total}`: the
first `$` is a literal dollar sign you want printed, the `${total}` is the hole.

**Anything that produces a value can go in a hole:**

```ts
const a = 3, b = 4;
console.log(`${a} + ${b} = ${a + b}`);        // 3 + 4 = 7
console.log(`Half: ${(a + b) / 2}`);           // Half: 3.5
console.log(`Price: $${(9.5).toFixed(2)}`);    // Price: $9.50
```

**Templates can span multiple lines** — the line breaks are part of the string:

```ts
console.log(`Name: Ada
Role: Engineer`);
```

prints two lines.

> ⚠️ **Common mistakes:** using `"` or `'` instead of a backtick — then
> `${name}` prints literally, character for character; and forgetting the `$`
> before the `{ }`.
""",
            warmup=[
                _q("With `const n = 3;`, what does `` `n = ${n}` `` produce?",
                   ["n = ${n}", "n = 3", "n = n", "3"], 1, "${n} is replaced by the value."),
                _q("With `const n = 3;`, what does `'n = ${n}'` (single quotes) produce?",
                   ["n = 3", "n = ${n}", "an error", "n = n"], 1,
                   "Only backticks interpolate. In ordinary quotes it is literal text."),
                _q("What does `` `${2 * 5} apples` `` produce?",
                   ["${2 * 5} apples", "10 apples", "2 * 5 apples", "25 apples"], 1,
                   "The expression inside the hole is evaluated first."),
            ],
            exercises=[
                _ex("tscourse-w1-tmpl-1", "Welcome message",
                    "Use a template literal to print `Hi Ada, welcome!`.",
                    'const name = "Ada";\nconsole.log(`Hi ${name}, welcome!`);\n',
                    '`Hi ${name}, welcome!`', [("", "Hi Ada, welcome!")],
                    hints=["Backticks, not quotes.",
                           "Put ${name} where the name belongs."]),
                _ex("tscourse-w1-tmpl-2", "Inline arithmetic",
                    "Print `3 + 4 = 7` using a single template literal.",
                    'const a = 3;\nconst b = 4;\nconsole.log(`${a} + ${b} = ${a + b}`);\n',
                    '`${a} + ${b} = ${a + b}`', [("", "3 + 4 = 7")],
                    hints=["A hole can contain an expression like a + b.",
                           "The template is `${a} + ${b} = ${a + b}`."]),
                _ex("tscourse-w1-tmpl-3", "A dollar sign and a hole",
                    "Print `Total: $36` — a literal $ followed by the computed total.",
                    'const price = 12;\nconst qty = 3;\nconsole.log(`Total: $${price * qty}`);\n',
                    '`Total: $${price * qty}`', [("", "Total: $36")],
                    hints=["You need two dollar signs: one printed, one starting the hole.",
                           "Write `Total: $${price * qty}`."]),
                _ex("tscourse-w1-tmpl-4", "Money, fixed",
                    "Print `Price: $9.50` from the number 9.5.",
                    'const price = 9.5;\nconsole.log(`Price: $${price.toFixed(2)}`);\n',
                    'price.toFixed(2)', [("", "Price: $9.50")],
                    hints=["toFixed(2) gives exactly two decimal places.",
                           "Put price.toFixed(2) inside the hole."]),
                _ex("tscourse-w1-tmpl-5", "Two lines, one template",
                    "Using ONE console.log and a multi-line template, print `Name: Ada` then `Role: Engineer`.",
                    'const name = "Ada";\nconsole.log(`Name: ${name}\nRole: Engineer`);\n',
                    'Role: Engineer', [("", "Name: Ada\nRole: Engineer")],
                    hints=["A real line break inside backticks becomes a newline.",
                           "The second line of the template is `Role: Engineer`."]),
                _fix("tscourse-w1-tmpl-fix1", "Fix the quotes",
                     "This was meant to greet by name but prints the hole literally. Fix it.",
                     'const name = "Ada";\nconsole.log(\'Hi ${name}!\');\n',
                     'const name = "Ada";\nconsole.log(`Hi ${name}!`);\n',
                     [("", "Hi Ada!")],
                     hints=["${...} only means anything inside backticks.",
                            "Swap the single quotes for backticks."]),
                _fix("tscourse-w1-tmpl-fix2", "Fix the missing dollar",
                     "This prints `{name} is here` instead of `Ada is here`. Fix it.",
                     'const name = "Ada";\nconsole.log(`{name} is here`);\n',
                     'const name = "Ada";\nconsole.log(`${name} is here`);\n',
                     [("", "Ada is here")],
                     hints=["A hole is $ followed by braces.",
                            "Add the missing $ before {name}."]),
            ],
            quiz=[
                _q("Which character opens a template literal?",
                   ['"', "'", "`", "$"], 2, "The backtick, usually left of the 1 key."),
                _q("`` `a${1 + 1}c` `` produces…", ["a1 + 1c", "a2c", "a${2}c", "ac"], 1,
                   "The hole evaluates to 2."),
                _q("Which is easier to get wrong by one space?",
                   ['"Hi, " + name + "!"', "`Hi, ${name}!`", "they are equally risky",
                    "neither can go wrong"], 0,
                   "With + the spaces are scattered across several quoted pieces; a template shows the whole line at once."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w1-types", "Types, annotations & conversion",
            "What the 'Type' in TypeScript buys you.",
            """
Every value has a **type**. This week you've met three:

| type | example values |
|---|---|
| `number` | `42`, `-1`, `3.5` |
| `string` | `"hi"`, `""`, `"42"` |
| `boolean` | `true`, `false` |

`typeof` reports the type as a string:

```ts
console.log(typeof 42);      // number
console.log(typeof "42");    // string
console.log(typeof true);    // boolean
```

Notice `42` and `"42"` are *different values*. They print identically, which is
exactly why the difference bites.

**The classic trap.** `+` means "add" for two numbers and "join" for anything
involving a string:

```ts
console.log(3 + 4);       // 7    two numbers  -> addition
console.log("3" + 4);     // 34   a string     -> concatenation
console.log("3" - 1);     // 2    - has no string meaning, so it converts
```

That inconsistency is inherited from JavaScript. The cure is to **convert on
purpose**:

```ts
Number("3") + 4     // 7
String(3) + "4"     // "34"
```

**Annotations** are how you tell TypeScript what you mean, so it can catch the
mistake before the program ever runs:

```ts
const price: number = 3;
const label: string = "Coffee";
const paid: boolean = true;
```

Read `: number` as "…and this is a number". You don't need it everywhere —
TypeScript can usually work it out from the value — but writing one costs a
second and turns a silent wrong answer into a red squiggle.

The annotations are **erased before the program runs**. They are a checking
tool, not part of the running code; at runtime it is all just values.

> ⚠️ **Common mistakes:** assuming `"5" + 3` adds; annotating something as
> `number` and then assigning text to it; and reaching for `Number(...)` after
> the concatenation has already happened, e.g. `Number("5" + 3)` is 53, not 8.
""",
            warmup=[
                _q('What does `console.log(typeof "42")` print?',
                   ["42", "number", "string", "text"], 2, 'The quotes make it a string.'),
                _q('What does `console.log("5" + 3)` print?', ["8", "53", "15", "error"], 1,
                   "A string on the left makes + concatenate."),
                _q('What does `console.log("5" - 3)` print?', ["53", "2", "8", "error"], 1,
                   'The - operator has no string meaning, so "5" is converted to 5 first.'),
                _q('What does `console.log(Number("5") + 3)` print?',
                   ["53", "8", '"8"', "error"], 1, "Convert first, then add."),
            ],
            exercises=[
                _ex("tscourse-w1-typ-1", "Report a type",
                    "Print the type of the value in `v` (it should print `string`).",
                    'const v = "42";\nconsole.log(typeof v);\n',
                    'typeof v', [("", "string")],
                    hints=["typeof reports the type name.", "Write typeof v."]),
                _ex("tscourse-w1-typ-2", "Add, don't join",
                    "`raw` holds text. Print 8 — the sum, not `53`.",
                    'const raw = "5";\nconsole.log(Number(raw) + 3);\n',
                    'Number(raw) + 3', [("", "8")],
                    hints=["Convert the text to a number before adding.",
                           "Write Number(raw) + 3."]),
                _ex("tscourse-w1-typ-3", "Join, don't add",
                    "`n` holds the number 42. Print `42!`.",
                    'const n = 42;\nconsole.log(String(n) + "!");\n',
                    'String(n) + "!"', [("", "42!")],
                    hints=["String(...) turns a number into text.",
                           'Write String(n) + "!".']),
                _ex("tscourse-w1-typ-4", "Annotate it",
                    "Fill in the annotation so `rate` is declared as a number.",
                    'const rate: number = 0.08;\nconsole.log(rate);\n',
                    'number', [("", "0.08")],
                    hints=["The annotation names the kind of value: number, string or boolean.",
                           "0.08 is a number, so write `const rate: number = 0.08;`."]),
                _ex("tscourse-w1-typ-5", "A boolean value",
                    "Store `true` in `paid` and print it.",
                    'const paid: boolean = true;\nconsole.log(paid);\n',
                    'true', [("", "true")],
                    hints=["true is a value, written without quotes.",
                           "Assign the bare word true."]),
                _fix("tscourse-w1-typ-fix1", "Fix the accidental join",
                     "This should print the total 15 but prints 105. Fix it.",
                     'const a = "10";\nconst b = 5;\nconsole.log(a + b);\n',
                     'const a = "10";\nconst b = 5;\nconsole.log(Number(a) + b);\n',
                     [("", "15")],
                     hints=['a is the string "10", so + joins: "10" + 5 is "105".',
                            "Convert a first: Number(a) + b."],
                     difficulty="Medium"),
                _fix("tscourse-w1-typ-fix2", "Fix the late conversion",
                     "Someone tried to convert, but in the wrong place: this prints 53 instead of 8. Fix it.",
                     'const raw = "5";\nconsole.log(Number(raw + 3));\n',
                     'const raw = "5";\nconsole.log(Number(raw) + 3);\n',
                     [("", "8")],
                     hints=['The join happens inside the parentheses first, giving "53".',
                            "Convert raw alone, then add: Number(raw) + 3."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What are annotations like `: number` for?",
                   ["Speed", "Catching mistakes before the program runs",
                    "They change the value", "They are required"], 1,
                   "They're checked while you write, then erased before running."),
                _q('`Number("abc")` gives…', ["0", "NaN", '"abc"', "an error that stops the program"], 1,
                   "NaN — 'not a number'. You'll learn to check for it in week 2."),
                _q("Which pair holds DIFFERENT values?",
                   ["42 and 42", '"42" and 42', "true and true", '"a" and "a"'], 1,
                   "One is text, one is a number — they only look alike when printed."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #1 — the receipt line",
        """
Meet **Budget Buddy**, the little expense tool you'll grow all the way through
this course. Each week it gains exactly the powers you just learned.

**This week.** Using only variables, arithmetic and text-building, print a
four-line receipt for **4 coffees at $3.25 each** against a **$20** budget:

```
Coffee x4
Each:      $3.25
Subtotal:  $13.00
Remaining: $7.00
```

Every number must be **computed**, not typed in — change `qty` to 5 and the
receipt should still be right. Money is shown to two decimal places.
""",
        _ch("tscourse-w1-capstone", "Budget Buddy #1", "Easy",
            "Compute the subtotal and the remaining budget, then print the four lines exactly.",
            'const item = "Coffee";\n'
            'const price = 3.25;\n'
            'const qty = 4;\n'
            'const budget = 20;\n'
            'const subtotal = price * qty;\n'
            'const remaining = budget - subtotal;\n'
            'console.log(`${item} x${qty}`);\n'
            'console.log(`Each:      $${price.toFixed(2)}`);\n'
            'console.log(`Subtotal:  $${subtotal.toFixed(2)}`);\n'
            'console.log(`Remaining: $${remaining.toFixed(2)}`);\n',
            'const subtotal = price * qty;\n'
            'const remaining = budget - subtotal;\n'
            'console.log(`${item} x${qty}`);\n'
            'console.log(`Each:      $${price.toFixed(2)}`);\n'
            'console.log(`Subtotal:  $${subtotal.toFixed(2)}`);\n'
            'console.log(`Remaining: $${remaining.toFixed(2)}`);',
            [("", "Coffee x4\nEach:      $3.25\nSubtotal:  $13.00\nRemaining: $7.00")],
            hints=["Start by naming the two computed values: subtotal and remaining.",
                   "subtotal is price * qty; remaining is budget - subtotal.",
                   "Each money line is a template literal ending in .toFixed(2), e.g. `Subtotal:  $${subtotal.toFixed(2)}`.",
                   "Match the label padding exactly: `Each:` has six spaces after it, `Subtotal:` two, `Remaining:` one."]),
        example_io="Coffee x4\nEach:      $3.25\nSubtotal:  $13.00\nRemaining: $7.00",
        rubric=["Line 1 shows the item and quantity",
                "The unit price, subtotal and remaining budget each appear on their own line",
                "Every money figure has exactly two decimal places",
                "Nothing is hard-coded — the numbers come from price, qty and budget"],
        stretch=_ch("tscourse-w1-capstone-stretch", "Budget Buddy #1 (stretch)", "Medium",
                    "Add a dashed rule under the header and a final line showing how many MORE coffees the remaining budget affords (whole coffees only).",
                    'const item = "Coffee";\n'
                    'const price = 3.25;\n'
                    'const qty = 4;\n'
                    'const budget = 20;\n'
                    'const subtotal = price * qty;\n'
                    'const remaining = budget - subtotal;\n'
                    'console.log(`${item} x${qty}`);\n'
                    'console.log("-".repeat(20));\n'
                    'console.log(`Each:      $${price.toFixed(2)}`);\n'
                    'console.log(`Subtotal:  $${subtotal.toFixed(2)}`);\n'
                    'console.log(`Remaining: $${remaining.toFixed(2)}`);\n'
                    'console.log(`Affords:   ${Math.floor(remaining / price)} more`);\n',
                    'const subtotal = price * qty;\n'
                    'const remaining = budget - subtotal;\n'
                    'console.log(`${item} x${qty}`);\n'
                    'console.log("-".repeat(20));\n'
                    'console.log(`Each:      $${price.toFixed(2)}`);\n'
                    'console.log(`Subtotal:  $${subtotal.toFixed(2)}`);\n'
                    'console.log(`Remaining: $${remaining.toFixed(2)}`);\n'
                    'console.log(`Affords:   ${Math.floor(remaining / price)} more`);',
                    [("", "Coffee x4\n--------------------\nEach:      $3.25\nSubtotal:  $13.00\nRemaining: $7.00\nAffords:   2 more")],
                    hints=['A 20-dash rule is "-".repeat(20).',
                           "Whole coffees only means Math.floor(remaining / price).",
                           "$7.00 buys 2 more coffees at $3.25 (2.15 rounded down)."]),
    ),
))

# --- Week 2 ---------------------------------------------------------------
_WEEKS.append(_week(
    2, 1, _M1,
    "Text & Input",
    "Read what the user types and reshape it: measure it, search it, slice it, pad it, and turn it into a number.",
    """
Last week your programs always printed the same thing. This week they **react**.
Almost every program from here on starts the same way:

```ts
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
```

That reads everything the user typed as one string, and `.trim()` shaves off the
newline they pressed at the end.

The rest of the week is the **string toolbox** — the handful of operations you'll
use for the rest of your life: measuring, indexing, changing case, searching,
slicing, padding, replacing, and converting text to numbers. None of them is
hard on its own. The skill is knowing which one to reach for, which comes from
using each of them a dozen times. That's what this week is.

⏱️ Budget about **six hours**, spread over several sittings.
""",
    objectives=[
        "Read a line of input and trim it",
        "Measure a string with .length and reach individual characters with s[i]",
        "Normalise case with toUpperCase / toLowerCase and compare case-insensitively",
        "Search text with includes, startsWith, endsWith and indexOf",
        "Extract parts with slice, including from the end with negative indices",
        "Pad, repeat and replace text to produce neatly aligned output",
        "Convert text to numbers with Number and parseInt, and spot NaN",
    ],
    why="Every real program has an edge where text comes in — a form field, a filename, a command, a CSV cell. Cleaning and interrogating that text is a daily job, not a beginner exercise.",
    est_minutes=350,
    glossary=[
        _gloss("standard input", "The stream of text a program reads — here, whatever the user types."),
        _gloss("fs.readFileSync(0, \"utf8\")", "Reads all of standard input as one string. The 0 means 'the input stream'."),
        _gloss(".trim()", "Returns a copy with whitespace removed from both ends."),
        _gloss("property", "A value attached to a value, read without parentheses: s.length."),
        _gloss("method", "A function attached to a value, called with parentheses: s.toUpperCase()."),
        _gloss("index", "A character's position, counting from 0. In \"cat\", 'c' is index 0."),
        _gloss("zero-based", "Counting starts at 0, so the last index is length - 1."),
        _gloss("immutable", "Strings never change in place. Every string method returns a NEW string."),
        _gloss(".includes(x)", "true when x appears anywhere inside."),
        _gloss(".indexOf(x)", "The index where x starts, or -1 when it is absent."),
        _gloss(".slice(a, b)", "The characters from index a up to but NOT including b."),
        _gloss(".padStart(n, c)", "Pads the front with c until the string is n characters long."),
        _gloss(".replaceAll(a, b)", "Every occurrence of a swapped for b."),
        _gloss("Number(x)", "Converts a whole string to a number, or NaN if it isn't one."),
        _gloss("parseInt(x)", "Reads a leading whole number, ignoring trailing text: parseInt(\"12kg\") is 12."),
        _gloss("NaN", "'Not a Number' — the result of a failed numeric conversion. It equals nothing, not even itself."),
    ],
    cheatsheet="""
```ts
import * as fs from "fs";
const s = fs.readFileSync(0, "utf8").trim();   // read + clean input

// ---- measure & index ------------------------------------------------
s.length              // 5 for "hello"   (a property: no parentheses)
s[0]                  // "h"   first character
s[s.length - 1]       // "o"   last character
s.at(-1)              // "o"   same thing, counting from the end

// ---- case -----------------------------------------------------------
s.toUpperCase()       // "HELLO"
s.toLowerCase()       // "hello"
a.toLowerCase() === b.toLowerCase()    // case-insensitive comparison

// ---- search ---------------------------------------------------------
s.includes("ell")     // true
s.startsWith("he")    // true
s.endsWith("lo")      // true
s.indexOf("l")        // 2    first position, or -1 if absent
s.lastIndexOf("l")    // 3

// ---- extract --------------------------------------------------------
s.slice(0, 3)         // "hel"   from 0 up to (not including) 3
s.slice(2)            // "llo"   from 2 to the end
s.slice(-2)           // "lo"    last two characters

// ---- reshape --------------------------------------------------------
s.trim()              // both ends
"7".padStart(3, "0")  // "007"
"ab".padEnd(5, ".")   // "ab..."
"-".repeat(10)        // "----------"
"a-b-c".replaceAll("-", " ")   // "a b c"

// ---- text -> number -------------------------------------------------
Number("42")          // 42
Number("4.5")         // 4.5
Number("abc")         // NaN
parseInt("12kg", 10)  // 12
Number.isNaN(v)       // the safe way to test for NaN
```
""",
    self_check=[
        "Can you read a line of input and print it back unchanged?",
        "Can you print the first and last character of whatever is typed?",
        "Can you compare two words ignoring their case?",
        "Can you explain why s.slice(0, 3) gives three characters, not four?",
        "Can you right-align a number in a 6-character column?",
        "Can you turn \"42\" into 42, and say what happens with \"forty-two\"?",
    ],
    review=[
        _q("Why call `.trim()` on the input?",
           ["To uppercase it", "To remove the trailing newline and stray spaces",
            "To convert it to a number", "It is optional and pointless"], 1,
           "The user pressed Enter, so the raw input ends in a newline."),
        _q("`\"hello\".length` is…", ["a method call", "5", '"5"', "an error"], 1,
           "length is a property whose value is the number 5."),
        _q('What is `"cat"[1]`?', ['"c"', '"a"', '"t"', "1"], 1,
           "Indexing is zero-based, so index 1 is the second character."),
        _q('What is `"hello".slice(1, 3)`?', ['"ell"', '"el"', '"he"', '"hel"'], 1,
           "From index 1 up to but not including 3: characters 1 and 2."),
        _q('What does `"Hello".indexOf("z")` return?', ["0", "-1", "undefined", "an error"], 1,
           "-1 is the 'not found' answer — remember it, it catches everyone once."),
        _q('`"7".padStart(3, "0")` gives…', ['"700"', '"007"', '"7  "', '"7"'], 1,
           "padStart adds to the FRONT until the target length is reached."),
        _q('`Number("12kg")` gives…', ["12", "NaN", '"12"', "0"], 1,
           'Number needs the WHOLE string to be numeric. parseInt("12kg", 10) gives 12.'),
        _q("Which correctly tests that `v` failed to convert?",
           ["v === NaN", "v == NaN", "Number.isNaN(v)", "v === \"NaN\""], 2,
           "NaN is not equal to anything, including itself — always use Number.isNaN."),
        _q('After `const t = s.toUpperCase();`, what has happened to `s`?',
           ["It is now uppercase", "It is unchanged", "It is empty", "It is a number"], 1,
           "Strings are immutable; methods return a new string and leave the original alone."),
        _q("How do you compare two names ignoring case?",
           ["a === b", "a.toLowerCase() === b.toLowerCase()", "a.includes(b)",
            "a.length === b.length"], 1,
           "Normalise both sides to the same case first."),
    ],
    milestone="Budget Buddy can now take a messy, hand-typed expense line and print a clean, aligned entry from it.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w2-input", "Reading input",
            "Getting whatever the user types into a variable.",
            """
Your programs get their input from **standard input** — the text piped into them
when they run. Two lines do the job:

```ts
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
console.log(input);
```

Reading it piece by piece:

| piece | meaning |
|---|---|
| `import * as fs from "fs"` | bring in the file-system toolbox |
| `readFileSync(0, "utf8")` | read stream number 0 — standard input — as text |
| `.trim()` | drop whitespace from both ends |

**Why `.trim()` matters.** The user pressed Enter, so the raw input is
`"hello\\n"`. Without trimming, `input.length` would be 6, not 5, and comparing
it to `"hello"` would fail — for a reason you cannot see on screen. Trimming
first removes a whole class of baffling bugs.

**`.trim()` returns a new string.** Strings are **immutable** — nothing you call
on a string ever modifies it. `s.trim()` hands you a cleaned copy; `s` is
untouched unless you assign the result somewhere.

The `import` line goes at the very top, once. From here on, exercises that need
input already have it.

> ⚠️ **Common mistakes:** forgetting `.trim()`, so your output has a stray blank
> line or your comparison mysteriously fails; forgetting the `import` line; and
> writing `readFileSync("0")` — the 0 is a number, not text.
""",
            warmup=[
                _q("If the user types `cat` and the program does `console.log(input)`, the output is…",
                   ["cat", '"cat"', "input", "3"], 0, "It echoes the text."),
                _q('Without .trim(), what is the length of the input when the user types `hi` and presses Enter?',
                   ["1", "2", "3", "0"], 2, 'It is "hi\\n" — two letters plus the newline.'),
                _q("After `const t = s.trim();`, what is `s`?",
                   ["Trimmed", "Unchanged", "Empty", "undefined"], 1,
                   "trim returns a copy; the original is untouched."),
            ],
            exercises=[
                _ex("tscourse-w2-input-1", "Echo the input",
                    "Read the whole input, trimmed, and print it back.",
                    _FS + 'const input = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(input);\n',
                    'fs.readFileSync(0, "utf8").trim()',
                    [("hello\n", "hello"), ("  spaced  ", "spaced")],
                    hints=['readFileSync(0, "utf8") reads standard input.',
                           "Chain .trim() onto it to drop surrounding whitespace."]),
                _ex("tscourse-w2-input-2", "Greet the input",
                    "Read a name and print `Hello, <name>!` using a template literal.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`Hello, ${name}!`);\n',
                    '`Hello, ${name}!`',
                    [("Ada", "Hello, Ada!"), ("Bo", "Hello, Bo!")],
                    hints=["Backticks and one hole.",
                           "Write `Hello, ${name}!`."]),
                _ex("tscourse-w2-input-3", "Say it twice",
                    "Print the input twice on one line, separated by a single space.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`${s} ${s}`);\n',
                    '`${s} ${s}`',
                    [("hi", "hi hi"), ("ok", "ok ok")],
                    hints=["One template literal with two holes.",
                           "Write `${s} ${s}` — the space between them is literal."]),
                _ex("tscourse-w2-input-4", "Quote the input",
                    'Print the input wrapped in square brackets, e.g. `[hi]`.',
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`[${s}]`);\n',
                    '`[${s}]`',
                    [("hi", "[hi]"), ("  pad  ", "[pad]")],
                    hints=["Brackets are ordinary characters in a template.",
                           "Write `[${s}]` — the trim already removed the padding."]),
                _fix("tscourse-w2-input-fix1", "Fix the echo",
                     "This should echo what the user typed, but it prints a fixed word. Fix it.",
                     _FS + 'const input = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log("input");\n',
                     _FS + 'const input = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(input);\n',
                     [("hello", "hello"), ("bo", "bo")],
                     hints=['It prints the literal word "input" rather than the value.',
                            "Log the variable — no quotes."]),
                _fix("tscourse-w2-input-fix2", "Fix the untrimmed length",
                     "This should print the number of characters typed, but the newline is being counted. Fix it so `hi` prints 2.",
                     _FS + 'const s = fs.readFileSync(0, "utf8");\n'
                     'console.log(s.length);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length);\n',
                     [("hi\n", "2"), ("hello\n", "5")],
                     hints=["The trailing newline is a character too.",
                            "Add .trim() when reading."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What does the 0 in readFileSync(0, \"utf8\") mean?",
                   ["Read zero bytes", "Standard input", "The first file", "An error code"], 1,
                   "0 is the standard-input stream."),
                _q("Strings in TypeScript are…",
                   ["mutable — methods change them in place",
                    "immutable — methods return new strings", "numbers", "always uppercase"], 1,
                   "Immutable. This is why you must assign the result of s.trim()."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w2-inspect", "Measuring & indexing",
            "How long is it, and what is the character at position i?",
            """
**Length** is a *property* — no parentheses:

```ts
"hello".length     // 5
"".length          // 0
```

**Indexing** reaches one character. Positions start at **0**:

```
 "h"  "e"  "l"  "l"  "o"
  0    1    2    3    4
```

```ts
const s = "hello";
s[0]                // "h"   first
s[4]                // "o"   fifth
s[s.length - 1]     // "o"   LAST — length is 5, last index is 4
s[99]               // undefined  (no error, just nothing)
```

That `length - 1` is worth burning in: a 5-character string has indices 0 to 4.
Reaching for `s[s.length]` gets you `undefined`, which then quietly poisons
everything downstream. This is the famous **off-by-one**, and you will meet it
again in loops next week.

`.at()` is a friendlier way to count from the end:

```ts
s.at(-1)    // "o"   last
s.at(-2)    // "l"   second from last
```

A single character is itself a string of length 1 — there's no separate
character type, so everything you know about strings applies to it.

> ⚠️ **Common mistakes:** writing `s.length()` (it's a property, so no
> parentheses); using `s[s.length]` instead of `s[s.length - 1]`; and forgetting
> that an empty input makes every index `undefined`.
""",
            warmup=[
                _q('What is `"cat".length`?', ["cat", "2", "3", '"3"'], 2, "Three characters."),
                _q('What is `"cat"[0]`?', ['"c"', '"a"', "0", "undefined"], 0, "Index 0 is the first."),
                _q('What is `"cat"[3]`?', ['"t"', '""', "undefined", "an error"], 2,
                   "The valid indices are 0, 1, 2. Index 3 is past the end."),
                _q('Which reliably gives the LAST character of `s`?',
                   ["s[s.length]", "s[s.length - 1]", "s[-1]", "s.last()"], 1,
                   "s[-1] is undefined in TypeScript — use s[s.length - 1] or s.at(-1)."),
            ],
            exercises=[
                _ex("tscourse-w2-idx-1", "Count the characters",
                    "Print how many characters the input has.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.length);\n',
                    's.length',
                    [("hello", "5"), ("hi", "2")],
                    hints=["length is a property — no parentheses."]),
                _ex("tscourse-w2-idx-2", "First character",
                    "Print the first character of the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s[0]);\n',
                    's[0]',
                    [("hello", "h"), ("Ada", "A")],
                    hints=["Positions start at 0.", "Write s[0]."]),
                _ex("tscourse-w2-idx-3", "Last character",
                    "Print the last character of the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s[s.length - 1]);\n',
                    's[s.length - 1]',
                    [("hello", "o"), ("Ada", "a"), ("x", "x")],
                    hints=["The last index is one less than the length.",
                           "Write s[s.length - 1]."]),
                _ex("tscourse-w2-idx-4", "First and last, together",
                    "Print the first and last character joined, e.g. `hello` → `ho`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`${s[0]}${s.at(-1)}`);\n',
                    '`${s[0]}${s.at(-1)}`',
                    [("hello", "ho"), ("ab", "ab")],
                    hints=["Two holes, no separator between them.",
                           "Write `${s[0]}${s.at(-1)}` — or use s[s.length - 1] for the last."]),
                _ex("tscourse-w2-idx-5", "Middle character",
                    "The input always has an odd length. Print its middle character.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s[Math.floor(s.length / 2)]);\n',
                    'Math.floor(s.length / 2)',
                    [("abc", "b"), ("hello", "l"), ("x", "x")],
                    hints=['For "abc" the middle index is 1, and 3 / 2 is 1.5.',
                           "Round the halved length down: Math.floor(s.length / 2)."],
                    difficulty="Medium"),
                _fix("tscourse-w2-idx-fix1", "Fix the length call",
                     "This should print the length but crashes. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length());\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length);\n',
                     [("hello", "5")],
                     hints=["length is a property, not a method.",
                            "Remove the parentheses after length."]),
                _fix("tscourse-w2-idx-fix2", "Fix the off-by-one",
                     "This should print the last character but prints nothing (undefined). Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s[s.length]);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s[s.length - 1]);\n',
                     [("hello", "o"), ("ab", "b")],
                     hints=["A 5-character string has indices 0 to 4, not 0 to 5.",
                            "Subtract one: s[s.length - 1]."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("For a string of length n, the valid indices are…",
                   ["1 to n", "0 to n", "0 to n - 1", "0 to n + 1"], 2,
                   "Zero-based: 0 up to n - 1."),
                _q("`\"abc\"[5]` evaluates to…",
                   ["an error that stops the program", "undefined", '""', "c"], 1,
                   "Out-of-range indexing is silent — which is exactly what makes it dangerous."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w2-case", "Changing case",
            "Normalising text so comparisons behave.",
            """
Two methods, both returning a **new** string:

```ts
"Hello".toUpperCase()    // "HELLO"
"Hello".toLowerCase()    // "hello"
```

The real use isn't shouting — it's **normalising before you compare**. To a
computer `"YES"`, `"Yes"` and `"yes"` are three different strings. Users type
all three. So you flatten both sides first:

```ts
const answer = "YeS";
console.log(answer.toLowerCase() === "yes");   // true
```

That pattern — *normalise, then compare* — turns up constantly: matching
commands, checking a filename's extension, deduplicating names.

**Capitalising a word** combines case with indexing and slicing (slicing gets
its own lesson shortly, but here's the shape):

```ts
const w = "ada";
console.log(w[0].toUpperCase() + w.slice(1));   // "Ada"
```

Take the first character, uppercase it, and glue on everything from index 1
onward.

> ⚠️ **Common mistakes:** calling `s.toUpperCase()` and expecting `s` itself to
> change; normalising only one side of a comparison; and forgetting the
> parentheses — `s.toUpperCase` without them is the method itself, not its
> result.
""",
            warmup=[
                _q('What is `"hi".toUpperCase()`?', ["hi", "HI", "Hi", '"HI"'], 1, "Both letters uppercased."),
                _q('After `const t = s.toUpperCase();` with `s = "hi"`, what is `s`?',
                   ['"HI"', '"hi"', '""', "undefined"], 1, "Unchanged — strings are immutable."),
                _q('Is `"YES" === "yes"`?', ["true", "false"], 1,
                   "String comparison is case-sensitive; normalise first."),
            ],
            exercises=[
                _ex("tscourse-w2-case-1", "Shout it",
                    "Print the input in UPPERCASE.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.toUpperCase());\n',
                    's.toUpperCase()',
                    [("hello", "HELLO"), ("Bo", "BO")],
                    hints=["Call .toUpperCase() on the string."]),
                _ex("tscourse-w2-case-2", "Whisper it",
                    "Print the input in lowercase.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.toLowerCase());\n',
                    's.toLowerCase()',
                    [("HELLO", "hello"), ("MiXeD", "mixed")],
                    hints=["The mirror image of toUpperCase."]),
                _ex("tscourse-w2-case-3", "Case-insensitive yes",
                    "Print `true` when the input is any capitalisation of `yes`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.toLowerCase() === "yes");\n',
                    's.toLowerCase() === "yes"',
                    [("YES", "true"), ("Yes", "true"), ("yes", "true"), ("no", "false")],
                    hints=["Flatten the input, then compare to the lowercase word.",
                           'Write s.toLowerCase() === "yes".']),
                _ex("tscourse-w2-case-4", "Capitalise a word",
                    "Print the input with only its first letter capitalised: `ada` → `Ada`.",
                    _FS + 'const w = fs.readFileSync(0, "utf8").trim().toLowerCase();\n'
                    'console.log(w[0].toUpperCase() + w.slice(1));\n',
                    'w[0].toUpperCase() + w.slice(1)',
                    [("ada", "Ada"), ("BOB", "Bob"), ("x", "X")],
                    hints=["Uppercase the first character, then append the rest.",
                           "The rest of the word is w.slice(1)."],
                    difficulty="Medium"),
                _fix("tscourse-w2-case-fix1", "Fix the one-sided compare",
                     "This should accept `YES` in any case, but only `yes` works. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s === "yes");\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.toLowerCase() === "yes");\n',
                     [("YES", "true"), ("Yes", "true"), ("no", "false")],
                     hints=["Only one side has been normalised — actually, neither has.",
                            "Lowercase the input before comparing."]),
                _fix("tscourse-w2-case-fix2", "Fix the ignored result",
                     "This should print the input uppercased, but prints it unchanged. Fix it.",
                     _FS + 'let s = fs.readFileSync(0, "utf8").trim();\n'
                     's.toUpperCase();\nconsole.log(s);\n',
                     _FS + 'let s = fs.readFileSync(0, "utf8").trim();\n'
                     's = s.toUpperCase();\nconsole.log(s);\n',
                     [("hi", "HI"), ("ada", "ADA")],
                     hints=["The call happens, but its result is thrown away.",
                            "Assign it back: s = s.toUpperCase();"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why normalise case before comparing?",
                   ["It is faster", "Because users type the same word many ways",
                    "It saves memory", "It is required by TypeScript"], 1,
                   "Yes / YES / yes are three different strings to a computer."),
                _q('`"ada"[0].toUpperCase()` gives…', ['"ADA"', '"A"', '"a"', "an error"], 1,
                   'Indexing first gives the one-character string "a", which uppercases to "A".'),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w2-search", "Searching inside text",
            "Does it contain, start with, end with — and where?",
            """
Four everyday questions, four methods:

```ts
const s = "budget-report.csv";

s.includes("report")     // true   — anywhere?
s.startsWith("budget")   // true   — at the front?
s.endsWith(".csv")       // true   — at the back?
s.indexOf("report")      // 7      — WHERE? (or -1)
```

The first three answer `true`/`false`. `indexOf` answers **where**, and when the
text isn't there it returns **`-1`** — not `0`, not `undefined`. `-1` is the
sentinel you have to remember, because `0` is a perfectly good answer meaning
"right at the start".

```ts
"hello".indexOf("h")    // 0   found, at the front
"hello".indexOf("z")    // -1  not found
```

`lastIndexOf` searches from the right, which is how you find a file extension:

```ts
const name = "my.report.csv";
name.lastIndexOf(".")   // 9   the final dot
```

**`indexOf` vs `includes`.** `includes` is just a friendlier way of asking
`indexOf(x) !== -1`. Prefer `includes` when you only care *whether*; use
`indexOf` when you need the position for slicing.

`startsWith` and `endsWith` also take a second argument in some forms, but the
plain version covers nearly everything: prefixes (`"http"`), suffixes
(`".csv"`), and command matching.

> ⚠️ **Common mistakes:** treating `indexOf` as truthy — `if (s.indexOf("a"))`
> is wrong, because a match at position 0 is falsy; and forgetting that all four
> are case-sensitive, so normalise first when that matters.
""",
            warmup=[
                _q('What is `"hello".includes("ell")`?', ["true", "false"], 0,
                   "It appears starting at index 1."),
                _q('What is `"hello".indexOf("l")`?', ["1", "2", "3", "-1"], 1,
                   "The FIRST l is at index 2."),
                _q('What is `"hello".indexOf("z")`?', ["0", "-1", "undefined", "5"], 1,
                   "-1 means not found."),
                _q('What is `"report.csv".endsWith(".csv")`?', ["true", "false"], 0,
                   "The string does end with that suffix."),
            ],
            exercises=[
                _ex("tscourse-w2-find-1", "Contains a word",
                    "Print whether the input contains `cat`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.includes("cat"));\n',
                    's.includes("cat")',
                    [("concatenate", "true"), ("dog", "false"), ("cat", "true")],
                    hints=["includes answers true or false.",
                           'Write s.includes("cat").']),
                _ex("tscourse-w2-find-2", "Is it a CSV?",
                    "Print whether the input filename ends with `.csv`.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(name.endsWith(".csv"));\n',
                    'name.endsWith(".csv")',
                    [("report.csv", "true"), ("report.txt", "false"), ("csv", "false")],
                    hints=["endsWith checks a suffix.",
                           'Write name.endsWith(".csv").']),
                _ex("tscourse-w2-find-3", "Where is it?",
                    "Print the index where `-` first appears (or -1 if it doesn't).",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.indexOf("-"));\n',
                    's.indexOf("-")',
                    [("a-b", "1"), ("-x", "0"), ("abc", "-1")],
                    hints=["indexOf gives the position, or -1.",
                           'Write s.indexOf("-").']),
                _ex("tscourse-w2-find-4", "Explicit not-found test",
                    "Print `true` when the input does NOT contain `x`, using indexOf.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.indexOf("x") === -1);\n',
                    's.indexOf("x") === -1',
                    [("abc", "true"), ("axc", "false"), ("x", "false")],
                    hints=["Not found is exactly -1.",
                           'Compare s.indexOf("x") to -1.']),
                _ex("tscourse-w2-find-5", "The final dot",
                    "Print the index of the LAST `.` in the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.lastIndexOf("."));\n',
                    's.lastIndexOf(".")',
                    [("my.report.csv", "9"), ("a.b", "1"), ("plain", "-1")],
                    hints=["Search from the right-hand end.",
                           'Write s.lastIndexOf(".").']),
                _fix("tscourse-w2-find-fix1", "Fix the case-sensitive search",
                     "This should find `cat` however it is capitalised, but misses `CAT`. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.includes("cat"));\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.toLowerCase().includes("cat"));\n',
                     [("CAT", "true"), ("A Cat here", "true"), ("dog", "false")],
                     hints=["Searching is case-sensitive.",
                            "Lowercase the haystack before searching."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`s.includes(x)` is equivalent to…",
                   ["s.indexOf(x) === 0", "s.indexOf(x) !== -1", "s.indexOf(x) > 0",
                    "s.length > 0"], 1,
                   "Found means the index is anything other than -1."),
                _q("Why is `if (s.indexOf(\"a\"))` a bug?",
                   ["indexOf doesn't exist", "A match at index 0 is falsy, so it reads as 'not found'",
                    "It is too slow", "indexOf returns a string"], 1,
                   "Position 0 is a real match but behaves as false. Compare to -1 explicitly."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w2-slice", "Slicing out a piece",
            "Taking a substring by position.",
            """
`slice(start, end)` returns the characters from `start` **up to but not
including** `end`:

```
 "h"  "e"  "l"  "l"  "o"
  0    1    2    3    4    5   <- boundaries
```

```ts
const s = "hello";
s.slice(0, 3)    // "hel"   indices 0,1,2
s.slice(1, 3)    // "el"
s.slice(2)       // "llo"   from 2 to the end
s.slice(0, 0)    // ""      empty
```

**Why exclude the end?** Because then the length of the result is simply
`end - start`. `slice(0, 3)` gives exactly 3 characters. Once you internalise
that, the arithmetic stops being fiddly.

**Negative indices count from the end**, which is enormously convenient:

```ts
s.slice(-1)      // "o"    last character
s.slice(-3)      // "llo"  last three
s.slice(0, -1)   // "hell" everything except the last
```

**Slicing at a found position** is the classic combination — find, then cut:

```ts
const file = "report.csv";
const dot = file.lastIndexOf(".");
console.log(file.slice(0, dot));   // "report"
console.log(file.slice(dot + 1));  // "csv"
```

`substring` does something very similar but treats negatives as 0. Prefer
`slice`; there is no reason to carry two.

> ⚠️ **Common mistakes:** expecting `slice(0, 3)` to include index 3; forgetting
> the `+ 1` when slicing after a found separator (you'd keep the separator); and
> using `substring` with a negative number and wondering why nothing happened.
""",
            warmup=[
                _q('What is `"hello".slice(0, 2)`?', ['"he"', '"hel"', '"h"', '"llo"'], 0,
                   "Indices 0 and 1 — the end is excluded."),
                _q('What is `"hello".slice(2)`?', ['"he"', '"llo"', '"l"', '"hello"'], 1,
                   "With no end, it runs to the end of the string."),
                _q('How many characters does `s.slice(2, 6)` return (for a long enough s)?',
                   ["3", "4", "5", "6"], 1, "end - start = 6 - 2 = 4."),
                _q('What is `"hello".slice(-2)`?', ['"he"', '"lo"', '"llo"', '""'], 1,
                   "Negative counts back from the end: the last two characters."),
            ],
            exercises=[
                _ex("tscourse-w2-slice-1", "First three",
                    "Print the first three characters of the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.slice(0, 3));\n',
                    's.slice(0, 3)',
                    [("hello", "hel"), ("abcdef", "abc")],
                    hints=["The end index is excluded, so 0 to 3 gives three characters.",
                           "Write s.slice(0, 3)."]),
                _ex("tscourse-w2-slice-2", "Drop the first character",
                    "Print everything except the first character.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.slice(1));\n',
                    's.slice(1)',
                    [("hello", "ello"), ("ab", "b")],
                    hints=["Start at index 1 and run to the end.",
                           "Write s.slice(1)."]),
                _ex("tscourse-w2-slice-3", "Last two characters",
                    "Print the last two characters, using a negative index.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.slice(-2));\n',
                    's.slice(-2)',
                    [("hello", "lo"), ("ab", "ab")],
                    hints=["Negative means 'this many from the end'.",
                           "Write s.slice(-2)."]),
                _ex("tscourse-w2-slice-4", "Drop the last character",
                    "Print everything except the final character.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.slice(0, -1));\n',
                    's.slice(0, -1)',
                    [("hello!", "hello"), ("ab", "a")],
                    hints=["A negative END means 'stop that far from the end'.",
                           "Write s.slice(0, -1)."]),
                _ex("tscourse-w2-slice-5", "The file extension",
                    "Print the extension of a filename, without the dot: `report.csv` → `csv`.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'const dot = name.lastIndexOf(".");\n'
                    'console.log(name.slice(dot + 1));\n',
                    'name.slice(dot + 1)',
                    [("report.csv", "csv"), ("my.data.json", "json"), ("a.b", "b")],
                    hints=["Start one past the dot, or you keep the dot.",
                           "Write name.slice(dot + 1)."],
                    difficulty="Medium"),
                _ex("tscourse-w2-slice-6", "The base name",
                    "Print the filename WITHOUT its extension: `report.csv` → `report`.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'const dot = name.lastIndexOf(".");\n'
                    'console.log(name.slice(0, dot));\n',
                    'name.slice(0, dot)',
                    [("report.csv", "report"), ("my.data.json", "my.data")],
                    hints=["Cut from the start up to (not including) the dot.",
                           "Write name.slice(0, dot)."],
                    difficulty="Medium"),
                _fix("tscourse-w2-slice-fix1", "Fix the retained dot",
                     "This should print the extension `csv` but prints `.csv`. Fix it.",
                     _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                     'const dot = name.lastIndexOf(".");\n'
                     'console.log(name.slice(dot));\n',
                     _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                     'const dot = name.lastIndexOf(".");\n'
                     'console.log(name.slice(dot + 1));\n',
                     [("report.csv", "csv"), ("a.b", "b")],
                     hints=["Slicing FROM the dot includes the dot itself.",
                            "Start one character later: dot + 1."]),
            ],
            quiz=[
                _q("`s.slice(a, b)` returns how many characters?",
                   ["b", "b - a", "b - a + 1", "a + b"], 1,
                   "Excluding the end makes the length exactly b - a."),
                _q("Which gives everything but the last character?",
                   ["s.slice(1)", "s.slice(0, -1)", "s.slice(-1)", "s.slice(0, s.length)"], 1,
                   "A negative end stops that many characters from the end."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w2-shape", "Padding, repeating & replacing",
            "Making output line up, and swapping text out.",
            """
**Padding** grows a string to a target width, which is how columns line up:

```ts
"7".padStart(3, "0")      // "007"    pad the FRONT
"7".padStart(4)           // "   7"   spaces by default
"Name".padEnd(10, ".")    // "Name......"
```

Right-align numbers with `padStart`, left-align labels with `padEnd`. Two
`padEnd`s and everything in a report suddenly reads as a table:

```ts
console.log("Coffee".padEnd(12) + "$13.00".padStart(8));
console.log("Rent".padEnd(12) + "$900.00".padStart(8));
```

```
Coffee        $13.00
Rent         $900.00
```

**Repeating** builds rules and bars:

```ts
"-".repeat(20)     // a 20-character rule
"█".repeat(3)      // a tiny bar chart
```

**Replacing** swaps text out. `replace` changes only the first match;
`replaceAll` changes every one:

```ts
"a-b-c".replace("-", " ")      // "a b-c"    first only
"a-b-c".replaceAll("-", " ")   // "a b c"    all of them
"  x  ".trim()                 // "x"
```

Remember: every one of these returns a **new** string. `s.replaceAll(...)` on
its own does nothing useful — you must use or store the result.

> ⚠️ **Common mistakes:** using `replace` when you meant `replaceAll` and only
> fixing the first occurrence; padding to a width shorter than the string (it's
> left alone, never truncated); and forgetting that padding a *number* requires
> `String(n)` or a template hole first.
""",
            warmup=[
                _q('`"5".padStart(3, "0")` is…', ['"500"', '"005"', '"5  "', '"5"'], 1,
                   "The front is padded until the length is 3."),
                _q('`"hello".padStart(3, "0")` is…', ['"hel"', '"hello"', '"000hello"', '""'], 1,
                   "Already longer than 3, so it is returned unchanged — padding never truncates."),
                _q('`"a-b-c".replace("-", "+")` is…', ['"a+b+c"', '"a+b-c"', '"a-b-c"', '"abc"'], 1,
                   "replace changes only the first occurrence."),
                _q('`"ab".repeat(3)` is…', ['"ababab"', '"aaabbb"', '"ab3"', '"ab"'], 0,
                   "Three copies, joined."),
            ],
            exercises=[
                _ex("tscourse-w2-shape-1", "Zero-pad an ID",
                    "Print the input padded with leading zeros to 5 characters: `42` → `00042`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.padStart(5, "0"));\n',
                    's.padStart(5, "0")',
                    [("42", "00042"), ("7", "00007"), ("12345", "12345")],
                    hints=["padStart adds to the front until the length is reached.",
                           'Write s.padStart(5, "0").']),
                _ex("tscourse-w2-shape-2", "Left-align a label",
                    "Print the input padded with dots to 10 characters: `Rent` → `Rent......`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.padEnd(10, "."));\n',
                    's.padEnd(10, ".")',
                    [("Rent", "Rent......"), ("Groceries", "Groceries.")],
                    hints=["padEnd adds to the back.",
                           'Write s.padEnd(10, ".").']),
                _ex("tscourse-w2-shape-3", "A rule as wide as the text",
                    "Print the input, then a line of `=` exactly as long as it.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s);\nconsole.log("=".repeat(s.length));\n',
                    '"=".repeat(s.length)',
                    [("Report", "Report\n======"), ("Hi", "Hi\n==")],
                    hints=["repeat takes the number of copies.",
                           'The count is s.length: "=".repeat(s.length).']),
                _ex("tscourse-w2-shape-4", "Swap every separator",
                    "Print the input with EVERY `-` replaced by a space.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.replaceAll("-", " "));\n',
                    's.replaceAll("-", " ")',
                    [("a-b-c", "a b c"), ("one-two", "one two"), ("plain", "plain")],
                    hints=["replace stops after the first match.",
                           'Use replaceAll("-", " ").']),
                _ex("tscourse-w2-shape-5", "A tiny bar",
                    "The input is a small number. Print that many `#` characters.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log("#".repeat(n));\n',
                    '"#".repeat(n)',
                    [("3", "###"), ("1", "#"), ("6", "######")],
                    hints=["repeat takes a number, and n already is one.",
                           'Write "#".repeat(n).']),
                _ex("tscourse-w2-shape-6", "An aligned row",
                    "Print `Coffee` padded to 12 characters, then `$13.00` right-aligned in 8.",
                    _FS + 'const label = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(label.padEnd(12) + "$13.00".padStart(8));\n',
                    'label.padEnd(12) + "$13.00".padStart(8)',
                    [("Coffee", "Coffee        $13.00"), ("Rent", "Rent          $13.00")],
                    hints=["padEnd for the label on the left, padStart for the amount on the right.",
                           'Join them with +: label.padEnd(12) + "$13.00".padStart(8).'],
                    difficulty="Medium"),
                _fix("tscourse-w2-shape-fix1", "Fix the partial replace",
                     "This should replace every `-` but only replaces the first. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.replace("-", " "));\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.replaceAll("-", " "));\n',
                     [("a-b-c", "a b c"), ("x-y", "x y")],
                     hints=["replace handles one occurrence only.",
                            "Use replaceAll."]),
            ],
            quiz=[
                _q("`\"abc\".padStart(2, \"0\")` gives…", ['"ab"', '"abc"', '"0abc"', '""'], 1,
                   "Padding never shortens a string."),
                _q("To right-align an amount in a report column you use…",
                   ["padEnd", "padStart", "repeat", "trim"], 1,
                   "padStart pushes the text to the right by filling the front."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w2-tonumber", "Text to numbers",
            "Converting input into something you can compute with.",
            """
Input always arrives as **text**, even when it looks like a number. `"12"` is
not `12`, and `"12" + 1` is `"121"`. Convert deliberately:

```ts
Number("42")       // 42
Number("4.5")      // 4.5
Number("  7  ")    // 7      surrounding whitespace is fine
Number("")         // 0      ⚠️ an empty string becomes zero
Number("abc")      // NaN
Number("12kg")     // NaN    the WHOLE string must be numeric
```

`parseInt` is more forgiving — it reads a leading number and stops:

```ts
parseInt("12kg", 10)    // 12
parseInt("abc", 10)     // NaN
parseFloat("3.5cm")     // 3.5
```

The `10` is the number base; always pass it, so `"08"` can never be misread.

**NaN** — "Not a Number" — is what a failed conversion produces. It is
contagious (`NaN + 1` is `NaN`) and, famously, **not equal to itself**:

```ts
const v = Number("abc");
console.log(v === NaN);          // false  ⚠️ always false, for everything
console.log(Number.isNaN(v));    // true   ✅ the correct test
```

So the rule is: **test with `Number.isNaN(x)`**, never with `===`.

**Round-tripping.** Going back the other way, `toFixed` gives you a string with
a set number of decimals, and `String(n)` gives the plain text:

```ts
const total = 13;
console.log(total.toFixed(2));   // "13.00"
console.log(String(total));      // "13"
```

> ⚠️ **Common mistakes:** forgetting to convert, so `+` silently concatenates;
> comparing to `NaN` with `===`; and being surprised that `Number("")` is `0`,
> which makes empty input look like a legitimate zero.
""",
            warmup=[
                _q('What is `Number("12") + 1`?', ['"121"', "13", "12", "NaN"], 1,
                   "Converted first, so it's real addition."),
                _q('What is `"12" + 1`?', ['"121"', "13", "12", "NaN"], 0,
                   "A string on the left means concatenation."),
                _q('What is `Number("12kg")`?', ["12", "NaN", '"12"', "0"], 1,
                   "Number requires the entire string to be numeric."),
                _q('What is `parseInt("12kg", 10)`?', ["12", "NaN", '"12"', "0"], 0,
                   "parseInt reads the leading digits and stops."),
                _q("What does `Number.isNaN(Number(\"abc\"))` give?", ["true", "false"], 0,
                   "The conversion failed, so the result is NaN."),
            ],
            exercises=[
                _ex("tscourse-w2-num-1", "Double the input",
                    "Read a number and print it doubled.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(n * 2);\n',
                    'Number(fs.readFileSync(0, "utf8").trim())',
                    [("21", "42"), ("0", "0"), ("2.5", "5")],
                    hints=["Convert the text before doing arithmetic.",
                           "Wrap the read in Number(...)."]),
                _ex("tscourse-w2-num-2", "Money, formatted",
                    "Read an amount and print it with exactly two decimals: `7.5` → `7.50`.",
                    _FS + 'const amt = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(amt.toFixed(2));\n',
                    'amt.toFixed(2)',
                    [("7.5", "7.50"), ("13", "13.00"), ("0.1", "0.10")],
                    hints=["toFixed sets the number of decimal places.",
                           "Write amt.toFixed(2)."]),
                _ex("tscourse-w2-num-3", "A number with a unit",
                    "The input looks like `12kg`. Print just the number, 12.",
                    _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(parseInt(raw, 10));\n',
                    'parseInt(raw, 10)',
                    [("12kg", "12"), ("7lbs", "7"), ("100m", "100")],
                    hints=["Number() would give NaN here — you need the forgiving one.",
                           "Write parseInt(raw, 10)."]),
                _ex("tscourse-w2-num-4", "Is it a number at all?",
                    "Print `true` when the input is NOT a valid number.",
                    _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(Number.isNaN(Number(raw)));\n',
                    'Number.isNaN(Number(raw))',
                    [("abc", "true"), ("42", "false"), ("4.5", "false")],
                    hints=["Convert, then test the result properly.",
                           "Write Number.isNaN(Number(raw))."],
                    difficulty="Medium"),
                _ex("tscourse-w2-num-5", "Percent of a total",
                    "Read an amount and print 8% of it, to two decimals: `50` → `4.00`.",
                    _FS + 'const amt = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log((amt * 0.08).toFixed(2));\n',
                    '(amt * 0.08).toFixed(2)',
                    [("50", "4.00"), ("100", "8.00"), ("12.5", "1.00")],
                    hints=["8% is a multiplication by 0.08.",
                           "Compute first, then format: (amt * 0.08).toFixed(2)."]),
                _fix("tscourse-w2-num-fix1", "Fix the accidental concatenation",
                     "This should add 10 to the input, but `5` gives `510`. Fix it.",
                     _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(raw + 10);\n',
                     _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(Number(raw) + 10);\n',
                     [("5", "15"), ("0", "10")],
                     hints=["raw is text, so + joins instead of adding.",
                            "Convert it: Number(raw) + 10."],
                     difficulty="Medium"),
                _fix("tscourse-w2-num-fix2", "Fix the NaN test",
                     "This should print `true` for `abc`, but always prints `false`. Fix it.",
                     _FS + 'const v = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(v === NaN);\n',
                     _FS + 'const v = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(Number.isNaN(v));\n',
                     [("abc", "true"), ("42", "false")],
                     hints=["NaN is not equal to anything, not even another NaN.",
                            "Use Number.isNaN(v)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q('Why pass 10 to parseInt?',
                   ["It's the maximum value", "It fixes the number base to decimal",
                    "It's the number of digits", "It is optional and pointless"], 1,
                   "Being explicit about base 10 removes any ambiguity."),
                _q('`Number("")` is…', ["NaN", "0", '""', "undefined"], 1,
                   "Empty text converts to zero — a real source of quiet bugs with blank input."),
                _q("`total.toFixed(2)` returns…",
                   ["a number", "a string", "a boolean", "nothing"], 1,
                   "A string, ready to print — don't do further maths on it."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #2 — the entry cleaner",
        """
Real expense lines are typed by hand and arrive messy: stray spaces, random
capitalisation, a unit stuck to the amount. This week Budget Buddy **cleans one
up and files it**.

The input is a single line like:

```
  coffee-and-cake:12kg
```

Print a four-line record:

```
Label:  Coffee and cake
Code:   COF
Amount: 12
Row:    Coffee and cake....... 12
```

Rules:

- **Label** — trimmed, `-` swapped for spaces, first letter capitalised, rest lowercase.
- **Code** — the first three letters of the label, uppercased.
- **Amount** — the digits after the `:`, read with `parseInt`.
- **Row** — the label padded with `.` to 22 characters, a space, then the amount.
""",
        _ch("tscourse-w2-capstone", "Budget Buddy #2", "Medium",
            "Clean the raw entry and print the four lines exactly.",
            _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
            'const colon = raw.indexOf(":");\n'
            'const words = raw.slice(0, colon).replaceAll("-", " ").toLowerCase();\n'
            'const label = words[0].toUpperCase() + words.slice(1);\n'
            'const code = label.slice(0, 3).toUpperCase();\n'
            'const amount = parseInt(raw.slice(colon + 1), 10);\n'
            'console.log(`Label:  ${label}`);\n'
            'console.log(`Code:   ${code}`);\n'
            'console.log(`Amount: ${amount}`);\n'
            'console.log(`Row:    ${label.padEnd(22, ".")} ${amount}`);\n',
            'const colon = raw.indexOf(":");\n'
            'const words = raw.slice(0, colon).replaceAll("-", " ").toLowerCase();\n'
            'const label = words[0].toUpperCase() + words.slice(1);\n'
            'const code = label.slice(0, 3).toUpperCase();\n'
            'const amount = parseInt(raw.slice(colon + 1), 10);\n'
            'console.log(`Label:  ${label}`);\n'
            'console.log(`Code:   ${code}`);\n'
            'console.log(`Amount: ${amount}`);\n'
            'console.log(`Row:    ${label.padEnd(22, ".")} ${amount}`);',
            [("  coffee-and-cake:12kg",
              "Label:  Coffee and cake\nCode:   COF\nAmount: 12\nRow:    Coffee and cake....... 12"),
             ("RENT:900",
              "Label:  Rent\nCode:   REN\nAmount: 900\nRow:    Rent.................. 900")],
            hints=["Find the colon first — everything before it is the label, everything after is the amount.",
                   'Build the label in steps: slice off the front, replaceAll("-", " "), then toLowerCase().',
                   "Capitalise with words[0].toUpperCase() + words.slice(1).",
                   'The amount needs parseInt(raw.slice(colon + 1), 10) because of the trailing unit.',
                   'The row is label.padEnd(22, ".") then a space then the amount.']),
        example_io="Label:  Coffee and cake\nCode:   COF\nAmount: 12\nRow:    Coffee and cake....... 12",
        rubric=["The label is trimmed, de-hyphenated, and capitalised like a sentence",
                "The code is three uppercase letters taken from the label",
                "The amount survives a trailing unit like `kg`",
                "The row is padded to a fixed width so many rows would line up"],
        stretch=_ch("tscourse-w2-capstone-stretch", "Budget Buddy #2 (stretch)", "Medium",
                    "Add a fifth line flagging big expenses: `Over:   true` when the amount is 100 or more, `Over:   false` otherwise. You have not met if/else yet — you don't need it, because a comparison is itself a value you can print.",
                    _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'const colon = raw.indexOf(":");\n'
                    'const words = raw.slice(0, colon).replaceAll("-", " ").toLowerCase();\n'
                    'const label = words[0].toUpperCase() + words.slice(1);\n'
                    'const code = label.slice(0, 3).toUpperCase();\n'
                    'const amount = parseInt(raw.slice(colon + 1), 10);\n'
                    'console.log(`Label:  ${label}`);\n'
                    'console.log(`Code:   ${code}`);\n'
                    'console.log(`Amount: ${amount}`);\n'
                    'console.log(`Row:    ${label.padEnd(22, ".")} ${amount}`);\n'
                    'console.log(`Over:   ${amount >= 100}`);\n',
                    'console.log(`Over:   ${amount >= 100}`);',
                    [("  coffee-and-cake:12kg",
                      "Label:  Coffee and cake\nCode:   COF\nAmount: 12\nRow:    Coffee and cake....... 12\nOver:   false"),
                     ("RENT:900",
                      "Label:  Rent\nCode:   REN\nAmount: 900\nRow:    Rent.................. 900\nOver:   true")],
                    hints=["A comparison like amount >= 100 is itself a value — true or false.",
                           "Drop it straight into a template hole: `Over:   ${amount >= 100}`."]),
    ),
))

# --- Week 3 ---------------------------------------------------------------
_WEEKS.append(_week(
    3, 1, _M1,
    "Making Decisions",
    "Branch on conditions with if/else, combine tests with boolean logic, and pick a value with a conditional expression or switch.",
    """
So far your programs run every line, every time. This week they start to
**choose**. That single ability — do this *or* that, depending — is what turns
a calculator into software.

Four things to get solid:

1. **Comparisons** produce a `true`/`false` value you can store and print.
2. **`if` / `else if` / `else`** picks one block of statements to run.
3. **`&&`, `||`, `!`** combine conditions.
4. **The conditional expression `a ? b : c`** and **`switch`** pick a *value*
   rather than a block, which often reads far better.

Most bugs in real code hide in decisions: a `>` that should be `>=`, branches in
the wrong order, an `||` that should be `&&`. So this week leans hard on the
"fix the bug" drills — the ordering trap in lesson 3 in particular is one you
will meet in production code for the rest of your career.

⏱️ Budget about **seven hours**, spread over several sittings.
""",
    objectives=[
        "Produce and print booleans with === , !== , < , > , <= , >=",
        "Branch with if, if/else, and if/else if/else chains",
        "Order branches correctly so no branch is unreachable",
        "Combine conditions with && , || and ! , and read short-circuiting",
        "Choose a value inline with the conditional (ternary) expression",
        "Know which values are truthy, and why === beats ==",
        "Dispatch on a fixed set of options with switch, including fall-through",
    ],
    why="Access control, pricing tiers, validation, routing, retries — every branch point in every application you will ever work on is one of these constructs. Getting the boundaries right is most of what correctness means.",
    est_minutes=410,
    glossary=[
        _gloss("boolean", "A value that is either true or false."),
        _gloss("condition", "An expression evaluated for its truth, e.g. n > 10."),
        _gloss("===", "Strict equality: same type AND same value. Your default."),
        _gloss("!==", "Strict inequality."),
        _gloss("==", "Loose equality — converts types first. Avoid it."),
        _gloss("if / else", "Runs one block of statements or another."),
        _gloss("else if", "Chains another test; only the FIRST match runs."),
        _gloss("block", "Statements grouped in { }."),
        _gloss("&&", "Logical AND — true only when both sides are true."),
        _gloss("||", "Logical OR — true when either side is true."),
        _gloss("!", "Logical NOT — flips a boolean."),
        _gloss("short-circuit", "&& and || stop evaluating as soon as the answer is settled."),
        _gloss("ternary", "The conditional expression cond ? whenTrue : whenFalse."),
        _gloss("truthy / falsy", "Non-boolean values behave as true or false in a condition. Falsy: false, 0, \"\", null, undefined, NaN."),
        _gloss("switch", "Dispatch on one value against several fixed cases."),
        _gloss("fall-through", "A switch case without break continues into the next case."),
        _gloss("guard", "An early test that rejects bad input before the real work."),
        _gloss("boundary", "The exact edge of a condition — where >= and > differ."),
    ],
    cheatsheet="""
```ts
// ---- comparisons produce booleans -----------------------------------
5 > 3            // true
a === b          // strict equality  (use this)
a !== b          // strict inequality
n >= 0           // note: >= includes the boundary itself

// ---- branching ------------------------------------------------------
if (n < 0) {
  console.log("negative");
} else if (n === 0) {
  console.log("zero");
} else {
  console.log("positive");
}
// Only the FIRST matching branch runs. Order narrow tests before broad ones.

// ---- logic ----------------------------------------------------------
n >= 1 && n <= 5              // both
s === "y" || s === "yes"      // either
!done                          // not
!(a && b) === (!a || !b)       // De Morgan

// ---- choose a VALUE, not a block ------------------------------------
const label = n < 0 ? "negative" : "non-negative";
console.log(`Status: ${n > 100 ? "over" : "ok"}`);

// ---- truthiness ------------------------------------------------------
// falsy: false  0  ""  null  undefined  NaN      everything else is truthy
if (name) { ... }              // "is name a non-empty string?"

// ---- switch ----------------------------------------------------------
switch (cmd) {
  case "add":
  case "plus":                 // deliberate fall-through: both do the same
    console.log("adding");
    break;
  case "del":
    console.log("deleting");
    break;
  default:
    console.log("unknown");
}
```
""",
    self_check=[
        "Can you print whether a number lies between 1 and 5 inclusive?",
        "Can you write an if/else if/else chain and explain why order matters?",
        "Can you say what happens if a broad condition is tested first?",
        "Can you rewrite a small if/else as a ternary, and say when you would not?",
        "Can you list the falsy values from memory?",
        "Can you say why `===` is safer than `==`?",
        "Can you write a switch with a deliberate fall-through and a default?",
    ],
    review=[
        _q("Which operator is strict equality?", ["=", "==", "===", "=>"], 2,
           "=== compares without type conversion; = is assignment."),
        _q("`(n >= 1 && n <= 5)` is true when…",
           ["n is 1 to 5 inclusive", "n is any number", "n is 0 only", "never"], 0,
           "Both halves must hold."),
        _q("In `if (a) {...} else if (b) {...} else {...}`, how many blocks run?",
           ["All that match", "Exactly one", "At most one", "None"], 1,
           "Exactly one — the else guarantees a fallback."),
        _q("Why is `if (age >= 0) ... else if (age < 18) ...` broken?",
           ["age can't be negative", "The first test is true for everyone, so the second is unreachable",
            "You cannot use else if", "< 18 is wrong"], 1,
           "A broad test placed first swallows every narrower one after it."),
        _q("Which values are falsy?",
           ['0, "", null, undefined, NaN, false', "only false", "only 0 and false",
            '"false" and 0'], 0,
           "Those six. Everything else — including \"0\" and \"false\" — is truthy."),
        _q('`"0" == 0` is…', ["true", "false"], 0,
           'Loose equality converts, so it is true. With === it is false. This is why we avoid ==.'),
        _q("`const t = n > 5 ? \"big\" : \"small\";` — what is t when n is 5?",
           ['"big"', '"small"', "5", "undefined"], 1,
           "5 > 5 is false, so the else branch value is chosen."),
        _q("A switch case with no `break`…",
           ["errors", "falls through into the next case", "skips the case", "returns"], 1,
           "Fall-through is occasionally useful and usually a bug."),
        _q("`!(a && b)` is the same as…",
           ["!a && !b", "!a || !b", "a || b", "!a && b"], 1,
           "De Morgan's law: negating an AND gives an OR of the negations."),
        _q("`false || \"hello\"` evaluates to…",
           ["true", "false", '"hello"', "an error"], 2,
           "|| returns the first truthy operand itself, not a boolean."),
    ],
    milestone="Budget Buddy can now validate an amount, reject nonsense input, band it by size, and label it — a real decision pipeline.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w3-booleans", "Booleans & comparison",
            "Values that are true or false, and the operators that produce them.",
            """
A **boolean** is a value with exactly two possibilities: `true` and `false`.
They're written without quotes — `"true"` is a *string*, a different thing.

Comparisons produce booleans:

| operator | meaning | example | result |
|---|---|---|---|
| `===` | equal (strict) | `3 === 3` | `true` |
| `!==` | not equal | `3 !== 4` | `true` |
| `<` | less than | `3 < 3` | `false` |
| `<=` | less than or equal | `3 <= 3` | `true` |
| `>` | greater than | `4 > 3` | `true` |
| `>=` | greater or equal | `3 >= 4` | `false` |

A boolean is a value like any other: you can store it, print it, name it.

```ts
const isAdult = age >= 18;
console.log(isAdult);          // true or false
```

Naming a condition is a genuinely good habit. `if (isAdult)` explains itself;
`if (age >= 18)` makes the reader do the work every time.

**Use `===`, not `==`.** Loose equality (`==`) converts types before comparing,
producing results nobody wants:

```ts
"5" == 5     // true   ⚠️
"5" === 5    // false  ✅ different types, so not equal
```

**Boundaries are where bugs live.** `>` and `>=` differ at exactly one value,
and that value is nearly always the one your tests forget. When you write a
comparison, say the boundary out loud: "is 18 itself an adult? Then it's `>=`."

**Strings compare too**, alphabetically by character codes — useful for equality,
occasionally surprising for ordering (`"Z" < "a"` is `true`, because uppercase
letters come first).

> ⚠️ **Common mistakes:** writing `=` (assignment) where you meant `===`;
> comparing input text to a number without `Number(...)`, so `"10" === 10` is
> false; and getting the boundary wrong by one.
""",
            warmup=[
                _q("What does `console.log(4 > 9)` print?", ["true", "false", "4", "9"], 1,
                   "4 is not greater than 9."),
                _q('What does `console.log("a" === "a")` print?', ["a", "true", "false", "1"], 1,
                   "Identical strings are strictly equal."),
                _q('What does `console.log("5" === 5)` print?', ["true", "false"], 1,
                   "Different types, so strict equality says false."),
                _q("What does `console.log(3 >= 3)` print?", ["true", "false"], 0,
                   ">= includes the boundary value itself."),
            ],
            exercises=[
                _ex("tscourse-w3-cmp-1", "Greater than ten",
                    "Print whether the number is strictly greater than 10.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(n > 10);\n',
                    'n > 10',
                    [("15", "true"), ("3", "false"), ("10", "false")],
                    hints=["'Strictly' means 10 itself does not count.",
                           "Use > , not >=."]),
                _ex("tscourse-w3-cmp-2", "Exact match",
                    "Print whether the input equals the word `yes`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s === "yes");\n',
                    's === "yes"',
                    [("yes", "true"), ("no", "false"), ("YES", "false")],
                    hints=["Use === for a strict comparison.",
                           'Compare s to "yes".']),
                _ex("tscourse-w3-cmp-3", "Old enough",
                    "Print whether the age qualifies as adult — 18 counts.",
                    _FS + 'const age = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(age >= 18);\n',
                    'age >= 18',
                    [("18", "true"), ("17", "false"), ("40", "true")],
                    hints=["18 itself must be true, so the boundary is included.",
                           "Use >= 18."]),
                _ex("tscourse-w3-cmp-4", "Name the condition",
                    "Store the test in `isEmpty`, then print it.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'const isEmpty = s.length === 0;\n'
                    'console.log(isEmpty);\n',
                    's.length === 0',
                    [("", "true"), ("hi", "false")],
                    hints=["An empty string has length 0.",
                           "Write s.length === 0."]),
                _ex("tscourse-w3-cmp-5", "Different from",
                    "Print whether the input is anything OTHER than `stop`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s !== "stop");\n',
                    's !== "stop"',
                    [("stop", "false"), ("go", "true")],
                    hints=["There is an operator for 'not equal'.",
                           'Write s !== "stop".']),
                _fix("tscourse-w3-cmp-fix1", "Fix the threshold",
                     "This should be true only when STRICTLY greater than 10, but 10 itself prints true. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(n >= 10);\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(n > 10);\n',
                     [("15", "true"), ("10", "false"), ("3", "false")],
                     hints=[">= includes 10 itself.", "Use > for strictly greater."]),
                _fix("tscourse-w3-cmp-fix2", "Fix the type mismatch",
                     "This should say true when the user types 10, but always says false. Fix it.",
                     _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(raw === 10);\n',
                     _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(Number(raw) === 10);\n',
                     [("10", "true"), ("11", "false")],
                     hints=['raw is the string "10", and a string is never strictly equal to a number.',
                            "Convert before comparing: Number(raw) === 10."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why prefer `===` over `==`?",
                   ["It is faster", "It compares without surprising type conversions",
                    "== is deprecated", "There is no difference"], 1,
                   "== converts first, which produces results like \"\" == 0 being true."),
                _q("`const ok = score >= 50;` — what type is `ok`?",
                   ["number", "string", "boolean", "undefined"], 2,
                   "A comparison always produces a boolean."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w3-if", "if and else",
            "Running one block of statements, or another.",
            """
`if` runs a block when its condition is true:

```ts
if (temperature > 30) {
  console.log("Hot");
}
```

`else` supplies the alternative — it runs when, and only when, the condition
was false:

```ts
if (n >= 0) {
  console.log("non-negative");
} else {
  console.log("negative");
}
```

Exactly one of those two lines prints. Always.

**The braces.** TypeScript allows a single statement without braces, but
**always write the braces**. This is the single most famous small bug in
programming:

```ts
if (x) console.log("a");
       console.log("b");   // ⚠️ runs ALWAYS — the indentation lies
```

Braces cost two characters and remove the ambiguity permanently.

**Nesting.** A block can contain another `if`. Useful, but keep it shallow —
three levels of nesting is a sign the logic wants restructuring, usually into
the `else if` chain you'll meet next.

```ts
if (loggedIn) {
  if (isAdmin) {
    console.log("admin");
  } else {
    console.log("user");
  }
}
```

**The condition is just an expression.** Anything producing a boolean works —
a comparison, a stored boolean, a method call like `s.startsWith("a")`.

> ⚠️ **Common mistakes:** putting a semicolon straight after the condition —
> `if (x);` — which silently gives the `if` an empty body; omitting braces; and
> writing `if (x = 5)` (assignment) instead of `if (x === 5)`.
""",
            warmup=[
                _q("`if (false) { console.log(\"a\"); } else { console.log(\"b\"); }` prints…",
                   ["a", "b", "both", "nothing"], 1, "The condition is false, so the else runs."),
                _q("How many of the two blocks in an if/else can run?",
                   ["Both", "Exactly one", "At most one, sometimes none", "None"], 1,
                   "An if/else always runs exactly one of its two blocks."),
                _q('With `s = "apple"`, `if (s.startsWith("a")) { console.log("yes"); }` prints…',
                   ["yes", "nothing", "a", "true"], 0,
                   "The method returns true, so the block runs."),
            ],
            exercises=[
                _ex("tscourse-w3-if-1", "Sign of a number",
                    "Print `non-negative` when n >= 0, otherwise `negative`.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'if (n >= 0) {\n  console.log("non-negative");\n} else {\n  console.log("negative");\n}\n',
                    'n >= 0',
                    [("5", "non-negative"), ("-2", "negative"), ("0", "non-negative")],
                    hints=["Zero counts as non-negative.", "Use >= 0."]),
                _ex("tscourse-w3-if-2", "The else branch",
                    "Fill in what happens when the password is wrong.",
                    _FS + 'const pw = fs.readFileSync(0, "utf8").trim();\n'
                    'if (pw === "hunter2") {\n  console.log("welcome");\n} else {\n  console.log("denied");\n}\n',
                    'console.log("denied");',
                    [("hunter2", "welcome"), ("wrong", "denied")],
                    hints=["The else block runs when the condition was false.",
                           'Print "denied" there.']),
                _ex("tscourse-w3-if-3", "Only when needed",
                    "Print `Warning: empty` ONLY when the input is empty. Print nothing otherwise.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'if (s.length === 0) {\n  console.log("Warning: empty");\n}\n',
                    's.length === 0',
                    [("", "Warning: empty"), ("hi", "")],
                    hints=["An if with no else simply does nothing when false.",
                           "Test s.length === 0."]),
                _ex("tscourse-w3-if-4", "Nested check",
                    "Print `admin` when the input is `admin`, `user` for any other non-empty input, and `nobody` when it is empty.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'if (name.length === 0) {\n  console.log("nobody");\n} else {\n'
                    '  if (name === "admin") {\n    console.log("admin");\n  } else {\n    console.log("user");\n  }\n}\n',
                    'if (name === "admin") {\n    console.log("admin");\n  } else {\n    console.log("user");\n  }',
                    [("", "nobody"), ("admin", "admin"), ("bo", "user")],
                    hints=["Inside the else, ask a second question.",
                           'Nest an if/else comparing name to "admin".'],
                    difficulty="Medium"),
                _ex("tscourse-w3-if-5", "Two independent checks",
                    "Print `long` when the input has more than 5 characters, and (separately) `shouty` when it is all uppercase. Both can print.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'if (s.length > 5) {\n  console.log("long");\n}\n'
                    'if (s === s.toUpperCase()) {\n  console.log("shouty");\n}\n',
                    's === s.toUpperCase()',
                    [("HELLOTHERE", "long\nshouty"), ("hello!!", "long"), ("HI", "shouty"), ("hi", "")],
                    hints=["A string is all-uppercase when uppercasing it changes nothing.",
                           "Compare s to s.toUpperCase()."],
                    difficulty="Medium"),
                _fix("tscourse-w3-if-fix1", "Fix the stray semicolon",
                     "This prints `hot` for every input. Fix it so only 31 and above do.",
                     _FS + 'const t = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (t > 30);\n{\n  console.log("hot");\n}\n',
                     _FS + 'const t = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (t > 30) {\n  console.log("hot");\n}\n',
                     [("35", "hot"), ("10", "")],
                     hints=["The semicolon right after the condition IS the if's whole body.",
                            "Delete it so the braces become the body."],
                     difficulty="Medium"),
                _fix("tscourse-w3-if-fix2", "Fix the missing braces",
                     "`ok` is meant to print only for `y`, but it always prints. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'if (s === "y")\n  console.log("checking");\n  console.log("ok");\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'if (s === "y") {\n  console.log("checking");\n  console.log("ok");\n}\n',
                     [("y", "checking\nok"), ("n", "")],
                     hints=["Without braces the if governs only the FIRST statement.",
                            "Wrap both statements in { }."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why always use braces on an if?",
                   ["TypeScript requires them", "So adding a second statement later can't silently escape the branch",
                    "They are faster", "They are optional and pointless"], 1,
                   "Indentation is not what decides — braces are."),
                _q("`if (x = 5) {}` does what?",
                   ["Tests whether x is 5", "Assigns 5 to x and then treats 5 as truthy",
                    "Nothing", "Errors always"], 1,
                   "= is assignment. This is why some codebases ban it inside conditions."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w3-chain", "else if chains & ordering",
            "Picking one of several bands — and getting the order right.",
            """
When there are more than two outcomes, chain the tests:

```ts
if (score >= 90) {
  console.log("A");
} else if (score >= 80) {
  console.log("B");
} else if (score >= 70) {
  console.log("C");
} else {
  console.log("F");
}
```

Read it as a **waterfall**. Each test is tried in turn, and the **first** one
that's true wins — everything below it is skipped entirely. That's why the
second test can be a bare `score >= 80`: if we reached it at all, we already
know `score` is under 90.

**Order is the whole game.** Flip two lines and the logic quietly breaks:

```ts
if (score >= 70) {          // ⚠️ broad test first
  console.log("C");
} else if (score >= 90) {   // unreachable — 95 already matched above
  console.log("A");
}
```

A score of 95 prints `C`. Nothing errors. Nothing warns you. The rule:
**order from the narrowest condition to the broadest**, which for numeric
bands means starting at one end and walking steadily to the other.

**The `else` is your safety net.** Without a final `else`, an input that matches
nothing produces *no output at all* — usually a bug, and one that looks like the
program silently did nothing.

**Testing bands.** Every band has two edges. For "80 to 89 is a B", test 79, 80,
89 and 90. Two of those four are the ones that catch a `>` that should be `>=`.

> ⚠️ **Common mistakes:** putting the broad test first; forgetting the final
> `else`; and writing overlapping conditions like `>= 80` after `>= 70` and
> expecting the later one to somehow win.
""",
            warmup=[
                _q("With score = 85, which prints from the A/B/C chain above?",
                   ["A", "B", "C", "all three"], 1, "85 fails >= 90 but passes >= 80."),
                _q("If the FIRST test in a chain is `score >= 0`, how many later branches can ever run?",
                   ["All of them", "None — for any non-negative score the first always wins",
                    "Only the last", "Only the else"], 1,
                   "A test that is true for everything makes the rest unreachable."),
                _q("A chain with no final `else`, given an input matching nothing, prints…",
                   ["an error", "nothing at all", "the last branch", "the first branch"], 1,
                   "Silence — which is why a default branch is usually worth having."),
            ],
            exercises=[
                _ex("tscourse-w3-chain-1", "Letter grade",
                    "Fill in the middle test so 95→A, 85→B, 70→C.",
                    _FS + 'const score = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'if (score >= 90) {\n  console.log("A");\n} else if (score >= 80) {\n  console.log("B");\n} else {\n  console.log("C");\n}\n',
                    'score >= 80',
                    [("95", "A"), ("85", "B"), ("70", "C"), ("80", "B"), ("89", "B")],
                    hints=["The B band starts at 80.", "Write score >= 80."]),
                _ex("tscourse-w3-chain-2", "Expense bands",
                    "Print `small` under 10, `medium` for 10 to 49, `large` for 50 and up.",
                    _FS + 'const amt = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'if (amt < 10) {\n  console.log("small");\n} else if (amt < 50) {\n  console.log("medium");\n} else {\n  console.log("large");\n}\n',
                    'amt < 50',
                    [("4", "small"), ("25", "medium"), ("50", "large"), ("49", "medium"), ("9", "small")],
                    hints=["Having already failed `< 10`, the medium band only needs its upper edge.",
                           "Write amt < 50."]),
                _ex("tscourse-w3-chain-3", "Add the safety net",
                    "Complete the chain so an unrecognised command prints `unknown`.",
                    _FS + 'const cmd = fs.readFileSync(0, "utf8").trim();\n'
                    'if (cmd === "add") {\n  console.log("adding");\n} else if (cmd === "del") {\n  console.log("deleting");\n} else {\n  console.log("unknown");\n}\n',
                    'console.log("unknown");',
                    [("add", "adding"), ("del", "deleting"), ("wat", "unknown")],
                    hints=["The final else catches everything that matched nothing.",
                           'Print "unknown" there.']),
                _ex("tscourse-w3-chain-4", "Three-way compare",
                    "Print `negative`, `zero` or `positive`.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'if (n < 0) {\n  console.log("negative");\n} else if (n === 0) {\n  console.log("zero");\n} else {\n  console.log("positive");\n}\n',
                    'n === 0',
                    [("-3", "negative"), ("0", "zero"), ("7", "positive")],
                    hints=["Having ruled out negative, zero is an exact test.",
                           "Write n === 0."]),
                _ex("tscourse-w3-chain-5", "Shipping tiers",
                    "Free over 100, $5 for 50 to 100, $10 below 50. Print just the number: `0`, `5` or `10`.",
                    _FS + 'const total = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'if (total > 100) {\n  console.log(0);\n} else if (total >= 50) {\n  console.log(5);\n} else {\n  console.log(10);\n}\n',
                    'total >= 50',
                    [("150", "0"), ("100", "5"), ("50", "5"), ("49", "10"), ("0", "10")],
                    hints=["100 itself is NOT free — it pays $5, so the first test is strict.",
                           "The middle band includes 50, so use >= 50."],
                    difficulty="Medium"),
                _fix("tscourse-w3-chain-fix1", "Fix the branch order",
                     "Every non-negative age prints `adult`, even 10. Fix the logic.",
                     _FS + 'const age = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (age >= 0) {\n  console.log("adult");\n} else if (age < 18) {\n  console.log("minor");\n} else {\n  console.log("adult");\n}\n',
                     _FS + 'const age = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (age < 18) {\n  console.log("minor");\n} else {\n  console.log("adult");\n}\n',
                     [("10", "minor"), ("40", "adult"), ("18", "adult")],
                     hints=["`age >= 0` is true for everybody, so it always wins.",
                            "Drop it and test the minor case first."],
                     difficulty="Medium"),
                _fix("tscourse-w3-chain-fix2", "Fix the upside-down bands",
                     "This grades backwards: 95 prints `C`. Reorder the chain so 95→A, 85→B, 70→C.",
                     _FS + 'const score = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (score >= 70) {\n  console.log("C");\n} else if (score >= 80) {\n  console.log("B");\n} else if (score >= 90) {\n  console.log("A");\n} else {\n  console.log("F");\n}\n',
                     _FS + 'const score = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (score >= 90) {\n  console.log("A");\n} else if (score >= 80) {\n  console.log("B");\n} else if (score >= 70) {\n  console.log("C");\n} else {\n  console.log("F");\n}\n',
                     [("95", "A"), ("85", "B"), ("70", "C"), ("50", "F")],
                     hints=["The broadest test is running first and swallowing the rest.",
                            "Start from the highest band and work down."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("In an else-if chain, how many branches run?",
                   ["Every one that matches", "The first that matches", "The last that matches",
                    "All of them"], 1,
                   "First match wins; the rest are skipped."),
                _q("For numeric bands you should order tests…",
                   ["alphabetically", "from one end of the range steadily to the other",
                    "broadest first", "it doesn't matter"], 1,
                   "Highest-to-lowest (or lowest-to-highest) guarantees no branch is unreachable."),
                _q("Which inputs best test the boundary of `score >= 80`?",
                   ["0 and 100", "79 and 80", "85 and 86", "80 only"], 1,
                   "The two values either side of the edge are where >= and > differ."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w3-logic", "Combining conditions",
            "&& , || and ! — and the fact that they stop early.",
            """
Three operators combine booleans:

| operator | reads as | true when |
|---|---|---|
| `a && b` | AND | **both** are true |
| `a \\|\\| b` | OR | **either** is true |
| `!a` | NOT | `a` is false |

```ts
n >= 1 && n <= 5              // in the range 1..5
s === "y" || s === "yes"      // either spelling
!done                          // not finished
```

**Ranges need `&&`.** The maths notation `1 <= n <= 5` looks reasonable and is
wrong — it evaluates left to right and compares a *boolean* to 5. Always spell
it out: `n >= 1 && n <= 5`.

**Precedence:** `!` binds tightest, then `&&`, then `||`. So
`a || b && c` means `a || (b && c)`. When mixing them, add parentheses — nobody
should have to remember this table while reading your code.

**Short-circuiting.** `&&` stops the moment it sees a false; `||` stops the
moment it sees a true:

```ts
s.length > 0 && s[0] === "a"     // safe: the second half only runs if there IS a s[0]
```

That's not just an optimisation — it's how you guard a check that would
otherwise be nonsense. Put the cheap, protective test first.

**De Morgan's laws** let you push a `!` inside:

```
!(a && b)   ===   !a || !b
!(a || b)   ===   !a && !b
```

Useful when a negated condition reads awkwardly. `!(age >= 18 && hasId)` says
"not (adult with ID)", which is usually clearer as "under 18, or missing ID".

> ⚠️ **Common mistakes:** writing `1 <= n <= 5`; using `||` where you meant
> `&&` (far too permissive) or the reverse (too strict); and mixing `&&` with
> `||` without parentheses.
""",
            warmup=[
                _q("`true && false` is…", ["true", "false"], 1, "AND needs both."),
                _q("`false || true` is…", ["true", "false"], 0, "OR needs just one."),
                _q("`!(3 > 5)` is…", ["true", "false"], 0, "3 > 5 is false; NOT flips it."),
                _q("With n = 9, what is `n >= 1 || n <= 5`?", ["true", "false"], 0,
                   "9 >= 1 is true, and OR only needs one side — this is the classic too-loose bug."),
            ],
            exercises=[
                _ex("tscourse-w3-log-1", "In range",
                    "Print whether n is between 1 and 5 inclusive.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(n >= 1 && n <= 5);\n',
                    'n >= 1 && n <= 5',
                    [("3", "true"), ("9", "false"), ("1", "true"), ("5", "true"), ("0", "false")],
                    hints=["Both edges must hold at once.", "Join the two tests with &&."]),
                _ex("tscourse-w3-log-2", "Either spelling",
                    "Print true when the input is `y` or `yes`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s === "y" || s === "yes");\n',
                    's === "y" || s === "yes"',
                    [("yes", "true"), ("y", "true"), ("n", "false")],
                    hints=["Either one is acceptable.", "Join the two tests with ||."]),
                _ex("tscourse-w3-log-3", "Not empty",
                    "Print true when the input is NOT empty, using the ! operator.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(!(s.length === 0));\n',
                    '!(s.length === 0)',
                    [("hi", "true"), ("", "false")],
                    hints=["Write the 'is empty' test, then negate the whole thing.",
                           "Write !(s.length === 0)."]),
                _ex("tscourse-w3-log-4", "A guarded check",
                    "Print true only when the input is non-empty AND starts with `a`. Empty input must not crash.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.length > 0 && s[0] === "a");\n',
                    's.length > 0 && s[0] === "a"',
                    [("apple", "true"), ("bat", "false"), ("", "false")],
                    hints=["Put the protective test first so the second never sees an empty string.",
                           'Write s.length > 0 && s[0] === "a".'],
                    difficulty="Medium"),
                _ex("tscourse-w3-log-5", "Weekend or holiday",
                    "Print `off` when the input is `sat`, `sun` or `holiday`; otherwise `work`.",
                    _FS + 'const d = fs.readFileSync(0, "utf8").trim();\n'
                    'if (d === "sat" || d === "sun" || d === "holiday") {\n  console.log("off");\n} else {\n  console.log("work");\n}\n',
                    'd === "sat" || d === "sun" || d === "holiday"',
                    [("sat", "off"), ("sun", "off"), ("holiday", "off"), ("mon", "work")],
                    hints=["You can chain as many || as you need.",
                           'Three comparisons joined by ||.']),
                _ex("tscourse-w3-log-6", "Outside the range",
                    "Print true when n is OUTSIDE 1..5, written as a negated range.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(!(n >= 1 && n <= 5));\n',
                    '!(n >= 1 && n <= 5)',
                    [("0", "true"), ("3", "false"), ("6", "true"), ("5", "false")],
                    hints=["Write the inside-the-range test, then negate it.",
                           "By De Morgan this is the same as n < 1 || n > 5."],
                    difficulty="Medium"),
                _fix("tscourse-w3-log-fix1", "Fix the too-loose range",
                     "This should be true only for 1..5, but 9 also prints true. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(n >= 1 || n <= 5);\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(n >= 1 && n <= 5);\n',
                     [("3", "true"), ("9", "false"), ("0", "false")],
                     hints=["|| is true when EITHER side holds — every number satisfies one of these.",
                            "Both must hold, so use &&."]),
                _fix("tscourse-w3-log-fix2", "Fix the unguarded index",
                     "Empty input should print false, but this reads a character that isn't there. Reorder the test so the length check protects it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s[0] === "a" && s.length > 0);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length > 0 && s[0] === "a");\n',
                     [("apple", "true"), ("", "false"), ("bat", "false")],
                     hints=["&& evaluates left to right and stops at the first false.",
                            "Put the cheap protective test on the left."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`1 <= n <= 5` is wrong because…",
                   ["it is a syntax error", "it compares a boolean to 5",
                    "it only checks the first half", "<= cannot be chained in any language"], 1,
                   "1 <= n produces true/false, which is then compared to 5 — always true."),
                _q("Which stops evaluating as soon as it hits a `true`?",
                   ["&&", "||", "!", "==="], 1,
                   "|| short-circuits on the first truthy operand."),
                _q("`!(a || b)` is the same as…",
                   ["!a || !b", "!a && !b", "a && b", "!a"], 1,
                   "De Morgan: negating an OR gives an AND of the negations."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w3-ternary", "Choosing a value inline",
            "The conditional expression: cond ? a : b.",
            """
`if` picks a **block of statements**. Often what you actually want is to pick a
**value**. That's the conditional expression, universally called the *ternary*
(it's the only operator with three operands):

```ts
const label = n < 0 ? "negative" : "non-negative";
```

Read it as a question: *"is n < 0? then `"negative"`, otherwise
`"non-negative"`."*

Compare the two ways of writing the same thing:

```ts
// with if — five lines, and `label` must be `let`
let label;
if (n < 0) {
  label = "negative";
} else {
  label = "non-negative";
}

// with a ternary — one line, and `label` can be const
const label = n < 0 ? "negative" : "non-negative";
```

Because it's an expression, it fits anywhere a value fits — most usefully inside
a template hole:

```ts
console.log(`You have ${n} item${n === 1 ? "" : "s"}`);
console.log(`Status: ${total > 100 ? "over budget" : "ok"}`);
```

That pluralisation trick alone will earn its keep.

**When *not* to use it.** Ternaries nest legally and read horribly:

```ts
const g = s >= 90 ? "A" : s >= 80 ? "B" : s >= 70 ? "C" : "F";   // 😬
```

Two levels is the sane ceiling. Beyond that, use an `else if` chain — the
computer doesn't care, and the next reader is you in six months.

> ⚠️ **Common mistakes:** using a ternary for side effects (`x ? console.log(1) :
> console.log(2)` — just use `if`); forgetting the `:` branch (it's mandatory);
> and nesting three deep.
""",
            warmup=[
                _q('With n = 5, `n > 3 ? "big" : "small"` is…', ['"big"', '"small"', "true", "5"], 0,
                   "The condition holds, so the first value is chosen."),
                _q('With n = 3, `n > 3 ? "big" : "small"` is…', ['"big"', '"small"', "false", "3"], 1,
                   "3 > 3 is false, so the second value."),
                _q('What does `` `${1 === 1 ? "y" : "n"}` `` produce?', ['"y"', '"n"', "true", "1"], 0,
                   "A ternary works inside a template hole like any other expression."),
            ],
            exercises=[
                _ex("tscourse-w3-tern-1", "Pass or fail",
                    "Print `pass` when the score is 50 or more, else `fail` — using a ternary.",
                    _FS + 'const score = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(score >= 50 ? "pass" : "fail");\n',
                    'score >= 50 ? "pass" : "fail"',
                    [("50", "pass"), ("49", "fail"), ("90", "pass")],
                    hints=["condition ? valueIfTrue : valueIfFalse.",
                           'Write score >= 50 ? "pass" : "fail".']),
                _ex("tscourse-w3-tern-2", "Name a chosen value",
                    "Store the right word in `label`, then print it.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'const label = n % 2 === 0 ? "even" : "odd";\n'
                    'console.log(label);\n',
                    'n % 2 === 0 ? "even" : "odd"',
                    [("4", "even"), ("7", "odd"), ("0", "even")],
                    hints=["Even means remainder 0 when divided by 2.",
                           'Write n % 2 === 0 ? "even" : "odd".']),
                _ex("tscourse-w3-tern-3", "Pluralise",
                    "Print `1 item` or `3 items` — the `s` appears only when n is not 1.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(`${n} item${n === 1 ? "" : "s"}`);\n',
                    'n === 1 ? "" : "s"',
                    [("1", "1 item"), ("3", "3 items"), ("0", "0 items")],
                    hints=["The ternary chooses between an empty string and \"s\".",
                           'Write n === 1 ? "" : "s" inside the hole.'],
                    difficulty="Medium"),
                _ex("tscourse-w3-tern-4", "Inline status",
                    "Print `Total: 120 (over budget)` when over 100, `Total: 40 (ok)` otherwise.",
                    _FS + 'const total = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(`Total: ${total} (${total > 100 ? "over budget" : "ok"})`);\n',
                    'total > 100 ? "over budget" : "ok"',
                    [("120", "Total: 120 (over budget)"), ("40", "Total: 40 (ok)"), ("100", "Total: 100 (ok)")],
                    hints=["The whole ternary goes inside the second template hole.",
                           '100 itself is NOT over, so the test is > 100.'],
                    difficulty="Medium"),
                _ex("tscourse-w3-tern-5", "Absolute value",
                    "Print the input's distance from zero, without using Math.abs.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(n < 0 ? -n : n);\n',
                    'n < 0 ? -n : n',
                    [("-5", "5"), ("7", "7"), ("0", "0")],
                    hints=["When it is negative, flip the sign.",
                           "Write n < 0 ? -n : n."]),
                _fix("tscourse-w3-tern-fix1", "Fix the swapped branches",
                     "This prints `fail` for a score of 90. Fix it.",
                     _FS + 'const score = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(score >= 50 ? "fail" : "pass");\n',
                     _FS + 'const score = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(score >= 50 ? "pass" : "fail");\n',
                     [("90", "pass"), ("10", "fail")],
                     hints=["The value after ? is the one used when the condition is TRUE.",
                            "Swap the two results."]),
                _fix("tscourse-w3-tern-fix2", "Fix the pluralisation",
                     "This prints `1 items`. Fix it so 1 gets no `s` and other counts do.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(`${n} item${n === 1 ? "s" : ""}`);\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(`${n} item${n === 1 ? "" : "s"}`);\n',
                     [("1", "1 item"), ("2", "2 items")],
                     hints=["When n IS 1 you want nothing added.",
                            "Swap the two branches of the ternary."]),
            ],
            quiz=[
                _q("A ternary produces…", ["a block", "a value", "nothing", "a boolean only"], 1,
                   "It's an expression: it evaluates to one of its two values."),
                _q("When should you reach for if/else instead of a ternary?",
                   ["Never", "When each branch runs statements, or when it would nest three deep",
                    "When the condition is long", "When using strings"], 1,
                   "Ternaries are for choosing values; deep nesting destroys readability."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w3-truthy", "Truthiness & equality traps",
            "What a condition does with a value that isn't a boolean.",
            """
An `if` doesn't require a boolean. Any value is converted to one, and there is a
short, memorisable list of values that count as **false**:

```
false    0    ""    null    undefined    NaN
```

**Everything else is truthy** — including `"0"`, `"false"`, `-1`, and empty
containers. Those six are worth committing to memory; there is no seventh.

```ts
if (name) { ... }   // "name is a non-empty string"
if (count) { ... }  // ⚠️ "count is not 0" — often NOT what you meant
```

That second one is a real trap: a legitimate count of `0` is skipped. When zero
is a meaningful value, test explicitly: `if (count > 0)` or
`if (count !== undefined)`.

**`==` vs `===`.** Loose equality converts before comparing, and its rules are
genuinely surprising:

```ts
0 == ""        // true   😐
0 == "0"       // true   😐
"" == "0"      // false  😱  (so == isn't even transitive)
null == undefined   // true
```

Strict equality has none of that:

```ts
0 === ""       // false
0 === "0"      // false
```

**The rule: always `===`.** The single accepted exception is `x == null`, which
neatly catches both `null` and `undefined` — and even that is clearer written
out.

**NaN** deserves its own warning: it is not equal to itself, so `x === NaN` is
always false. Test with `Number.isNaN(x)`.

**Guard clauses.** Truthiness is at its best rejecting bad input up front:

```ts
if (!raw) {
  console.log("no input");
} else if (Number.isNaN(Number(raw))) {
  console.log("not a number");
} else {
  console.log(Number(raw) * 2);
}
```

Handle the bad cases first, then the real work happens with everything already
known to be sound.

> ⚠️ **Common mistakes:** `if (count)` when 0 is legitimate; using `==`;
> comparing to `NaN` with `===`; and assuming `"false"` is falsy (it's a
> non-empty string, so it's truthy).
""",
            warmup=[
                _q('Is `""` truthy or falsy?', ["truthy", "falsy"], 1, "An empty string is falsy."),
                _q('Is `"0"` truthy or falsy?', ["truthy", "falsy"], 0,
                   "It is a non-empty string, so truthy — even though it looks like zero."),
                _q("`0 == \"\"` is…", ["true", "false"], 0,
                   "Loose equality converts both to 0. With === it would be false."),
                _q("`NaN === NaN` is…", ["true", "false"], 1,
                   "NaN is equal to nothing, including itself."),
            ],
            exercises=[
                _ex("tscourse-w3-truth-1", "Reject empty input",
                    "Print `empty` when nothing was typed, otherwise print the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'if (!s) {\n  console.log("empty");\n} else {\n  console.log(s);\n}\n',
                    '!s',
                    [("", "empty"), ("hi", "hi")],
                    hints=["An empty string is falsy, so ! flips it to true.",
                           "The condition is just !s."]),
                _ex("tscourse-w3-truth-2", "Zero is a real value",
                    "Print `none` only when the count is exactly 0, and the count otherwise. Do NOT use truthiness.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'if (n === 0) {\n  console.log("none");\n} else {\n  console.log(n);\n}\n',
                    'n === 0',
                    [("0", "none"), ("3", "3"), ("-1", "-1")],
                    hints=["Be explicit rather than relying on 0 being falsy.",
                           "Write n === 0."]),
                _ex("tscourse-w3-truth-3", "Validate a number",
                    "Print `not a number` when the input doesn't convert, otherwise print it doubled.",
                    _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'if (Number.isNaN(Number(raw))) {\n  console.log("not a number");\n} else {\n  console.log(Number(raw) * 2);\n}\n',
                    'Number.isNaN(Number(raw))',
                    [("abc", "not a number"), ("21", "42")],
                    hints=["Convert, then test the result with the proper function.",
                           "Write Number.isNaN(Number(raw))."],
                    difficulty="Medium"),
                _ex("tscourse-w3-truth-4", "A guard ladder",
                    "Print `no input` for empty, `not a number` for nonsense, else the value doubled.",
                    _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'if (!raw) {\n  console.log("no input");\n} else if (Number.isNaN(Number(raw))) {\n  console.log("not a number");\n} else {\n  console.log(Number(raw) * 2);\n}\n',
                    'console.log("not a number");',
                    [("", "no input"), ("abc", "not a number"), ("5", "10")],
                    hints=["Each guard rejects one bad case before the real work.",
                           'The middle branch prints "not a number".'],
                    difficulty="Medium"),
                _ex("tscourse-w3-truth-5", "Strictly equal",
                    "Print whether the input is strictly the string `0` — `0` should be true but an empty input false.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s === "0");\n',
                    's === "0"',
                    [("0", "true"), ("", "false"), ("00", "false")],
                    hints=['With == , the empty string would wrongly match.',
                           'Use === against the string "0".']),
                _fix("tscourse-w3-truth-fix1", "Fix the swallowed zero",
                     "A count of 0 should print `0`, but this prints `none`. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (!n) {\n  console.log("none");\n} else {\n  console.log(n);\n}\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (Number.isNaN(n)) {\n  console.log("none");\n} else {\n  console.log(n);\n}\n',
                     [("0", "0"), ("3", "3"), ("abc", "none")],
                     hints=["0 is falsy, so !n is true for a perfectly good count.",
                            "Test for the real failure case instead: Number.isNaN(n)."],
                     difficulty="Medium"),
                _fix("tscourse-w3-truth-fix2", "Fix the loose equality",
                     "This wrongly says an empty input equals 0. Make it strict.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s == 0);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(Number(s) === 0 && s.length > 0);\n',
                     [("0", "true"), ("", "false"), ("5", "false")],
                     hints=['== converts "" to 0, so empty input matches.',
                            "Convert deliberately and also require the input to be non-empty."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("How many falsy values are there?",
                   ["3", "6", "12", "infinitely many"], 1,
                   'false, 0, "", null, undefined, NaN.'),
                _q("`if (items)` where items is the number 0 does what?",
                   ["Runs the block", "Skips the block", "Errors", "Depends"], 1,
                   "0 is falsy — which is a bug whenever 0 is a legitimate count."),
                _q("The one defensible use of `==` is…",
                   ["comparing numbers", "x == null, to catch null and undefined together",
                    "comparing strings", "there are none at all"], 1,
                   "And even that is clearer written as x === null || x === undefined."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w3-switch", "switch",
            "Dispatching on one value against a fixed set of options.",
            """
When you're comparing **one value** against **several fixed options**, a
`switch` says so more clearly than a chain of `===` tests:

```ts
switch (cmd) {
  case "add":
    console.log("adding");
    break;
  case "del":
    console.log("deleting");
    break;
  default:
    console.log("unknown");
}
```

Three rules:

1. Cases are matched with **strict equality** (`===`). No ranges, no
   conditions — exact values only.
2. **`break` ends the case.** Without it, execution *falls through* into the
   next case and keeps going.
3. **`default`** catches everything unmatched. Put it last, and include it —
   a switch without one silently does nothing for unexpected input.

**Deliberate fall-through** is the one genuinely nice thing about `switch`:
stack the labels to give several values the same handling.

```ts
switch (day) {
  case "sat":
  case "sun":
    console.log("weekend");
    break;
  default:
    console.log("weekday");
}
```

Both `"sat"` and `"sun"` reach the same statement. Written as an `if`, that's
`day === "sat" || day === "sun"` — fine too, but the switch scales better as
the list grows.

**When to prefer if/else:** whenever the tests are *ranges* or *conditions*
rather than exact values. A `switch` can't express `score >= 90`.

> ⚠️ **Common mistakes:** forgetting `break` and falling through by accident;
> expecting `case n > 5:` to work; and omitting `default`, so bad input produces
> silence.
""",
            warmup=[
                _q("What ends a case?", ["a semicolon", "break", "the next case label", "return only"], 1,
                   "Without break, execution continues into the following case."),
                _q("A switch matches cases with…", ["==", "===", "<", "includes"], 1,
                   "Strict equality — exact values only."),
                _q('Given `case "sat": case "sun": console.log("weekend"); break;` and day = "sat", what prints?',
                   ["nothing", "weekend", "sat", "an error"], 1,
                   'The "sat" label falls straight through to the shared statement.'),
            ],
            exercises=[
                _ex("tscourse-w3-sw-1", "Dispatch a command",
                    "Complete the case so `del` prints `deleting`.",
                    _FS + 'const cmd = fs.readFileSync(0, "utf8").trim();\n'
                    'switch (cmd) {\n  case "add":\n    console.log("adding");\n    break;\n'
                    '  case "del":\n    console.log("deleting");\n    break;\n'
                    '  default:\n    console.log("unknown");\n}\n',
                    'case "del":',
                    [("add", "adding"), ("del", "deleting"), ("wat", "unknown")],
                    hints=["A case label is the word `case`, the exact value, then a colon.",
                           'Write case "del": .']),
                _ex("tscourse-w3-sw-2", "Add the default",
                    "Make any unrecognised colour print `unknown`.",
                    _FS + 'const c = fs.readFileSync(0, "utf8").trim();\n'
                    'switch (c) {\n  case "red":\n    console.log("stop");\n    break;\n'
                    '  case "green":\n    console.log("go");\n    break;\n'
                    '  default:\n    console.log("unknown");\n}\n',
                    'default:\n    console.log("unknown");',
                    [("red", "stop"), ("green", "go"), ("blue", "unknown")],
                    hints=["default has no value — just the word and a colon.",
                           'Write default: then console.log("unknown");']),
                _ex("tscourse-w3-sw-3", "Shared handling",
                    "Make both `sat` and `sun` print `weekend`, using stacked case labels.",
                    _FS + 'const d = fs.readFileSync(0, "utf8").trim();\n'
                    'switch (d) {\n  case "sat":\n  case "sun":\n    console.log("weekend");\n    break;\n'
                    '  default:\n    console.log("weekday");\n}\n',
                    'case "sat":\n  case "sun":',
                    [("sat", "weekend"), ("sun", "weekend"), ("mon", "weekday")],
                    hints=["Two labels in a row, with no statements between them.",
                           'Write case "sat": on one line and case "sun": on the next.'],
                    difficulty="Medium"),
                _ex("tscourse-w3-sw-4", "Days in a month",
                    "Complete the case so `feb` prints 28.",
                    _FS + 'const m = fs.readFileSync(0, "utf8").trim();\n'
                    'switch (m) {\n  case "feb":\n    console.log(28);\n    break;\n'
                    '  case "apr":\n  case "jun":\n    console.log(30);\n    break;\n'
                    '  default:\n    console.log(31);\n}\n',
                    'console.log(28);',
                    [("feb", "28"), ("apr", "30"), ("jun", "30"), ("jan", "31")],
                    hints=["February is the short one.", "Print 28."]),
                _ex("tscourse-w3-sw-5", "Normalise first",
                    "Make the switch case-insensitive by lowercasing the input before switching.",
                    _FS + 'const cmd = fs.readFileSync(0, "utf8").trim().toLowerCase();\n'
                    'switch (cmd) {\n  case "yes":\n    console.log("ok");\n    break;\n'
                    '  default:\n    console.log("no");\n}\n',
                    '.toLowerCase()',
                    [("YES", "ok"), ("Yes", "ok"), ("no", "no")],
                    hints=["A switch compares strictly, so normalise before it.",
                           "Chain .toLowerCase() onto the read."]),
                _fix("tscourse-w3-sw-fix1", "Fix the missing break",
                     "`add` prints both `adding` and `deleting`. Fix it.",
                     _FS + 'const cmd = fs.readFileSync(0, "utf8").trim();\n'
                     'switch (cmd) {\n  case "add":\n    console.log("adding");\n'
                     '  case "del":\n    console.log("deleting");\n    break;\n'
                     '  default:\n    console.log("unknown");\n}\n',
                     _FS + 'const cmd = fs.readFileSync(0, "utf8").trim();\n'
                     'switch (cmd) {\n  case "add":\n    console.log("adding");\n    break;\n'
                     '  case "del":\n    console.log("deleting");\n    break;\n'
                     '  default:\n    console.log("unknown");\n}\n',
                     [("add", "adding"), ("del", "deleting"), ("wat", "unknown")],
                     hints=["Without break, execution runs on into the next case.",
                            'Add a break; at the end of the "add" case.'],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A switch is a poor fit when…",
                   ["there are many options", "the tests are ranges or conditions",
                    "the value is a string", "you need a default"], 1,
                   "Cases are exact values; ranges need if/else."),
                _q("Omitting `default` means unmatched input…",
                   ["errors", "produces no output", "matches the first case",
                    "matches the last case"], 1,
                   "Silence — which usually reads as a mysterious no-op."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #3 — validate & classify",
        """
Budget Buddy now has to cope with whatever gets typed at it. Read one raw
amount and print **exactly two lines**: a verdict and a band.

Rules, in order:

1. **Empty input** → print `Invalid: no amount` and `Band:    -`
2. **Not a number** → print `Invalid: not a number` and `Band:    -`
3. **Negative** → print `Invalid: negative` and `Band:    -`
4. Otherwise print `Amount:  <the number, 2dp>` and a band:
   - under 10 → `Band:    small`
   - 10 to 49.99 → `Band:    medium`
   - 50 and over → `Band:    large`

Examples:

```
(input "25")     ->  Amount:  25.00
                     Band:    medium

(input "abc")    ->  Invalid: not a number
                     Band:    -
```

Order your guards carefully: each one may assume the earlier ones already
passed.
""",
        _ch("tscourse-w3-capstone", "Budget Buddy #3", "Medium",
            "Validate the input with a guard ladder, then band it.",
            _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
            'const n = Number(raw);\n'
            'if (!raw) {\n'
            '  console.log("Invalid: no amount");\n  console.log("Band:    -");\n'
            '} else if (Number.isNaN(n)) {\n'
            '  console.log("Invalid: not a number");\n  console.log("Band:    -");\n'
            '} else if (n < 0) {\n'
            '  console.log("Invalid: negative");\n  console.log("Band:    -");\n'
            '} else {\n'
            '  console.log(`Amount:  ${n.toFixed(2)}`);\n'
            '  console.log(`Band:    ${n < 10 ? "small" : n < 50 ? "medium" : "large"}`);\n'
            '}\n',
            'if (!raw) {\n'
            '  console.log("Invalid: no amount");\n  console.log("Band:    -");\n'
            '} else if (Number.isNaN(n)) {\n'
            '  console.log("Invalid: not a number");\n  console.log("Band:    -");\n'
            '} else if (n < 0) {\n'
            '  console.log("Invalid: negative");\n  console.log("Band:    -");\n'
            '} else {\n'
            '  console.log(`Amount:  ${n.toFixed(2)}`);\n'
            '  console.log(`Band:    ${n < 10 ? "small" : n < 50 ? "medium" : "large"}`);\n'
            '}',
            [("", "Invalid: no amount\nBand:    -"),
             ("abc", "Invalid: not a number\nBand:    -"),
             ("-5", "Invalid: negative\nBand:    -"),
             ("4", "Amount:  4.00\nBand:    small"),
             ("25", "Amount:  25.00\nBand:    medium"),
             ("50", "Amount:  50.00\nBand:    large"),
             ("9.99", "Amount:  9.99\nBand:    small")],
            hints=["Convert once at the top: const n = Number(raw); then every guard can use it.",
                   "Guard order matters — empty first (Number(\"\") is 0, which would sneak through), then NaN, then negative.",
                   "Each invalid branch prints TWO lines, the second always `Band:    -`.",
                   'The band itself is a two-level ternary: n < 10 ? "small" : n < 50 ? "medium" : "large".']),
        example_io="Amount:  25.00\nBand:    medium",
        rubric=["Empty, non-numeric and negative input each get their own message",
                "The guards are ordered so no valid input is wrongly rejected",
                "Valid amounts print with exactly two decimal places",
                "The three bands split at 10 and 50, with 50 itself counting as large"],
        stretch=_ch("tscourse-w3-capstone-stretch", "Budget Buddy #3 (stretch)", "Medium",
                    "Add a third line for valid amounts: `Note:    over budget` when the amount exceeds 100, `Note:    fine` otherwise. Invalid input still prints only its two lines.",
                    _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'const n = Number(raw);\n'
                    'if (!raw) {\n'
                    '  console.log("Invalid: no amount");\n  console.log("Band:    -");\n'
                    '} else if (Number.isNaN(n)) {\n'
                    '  console.log("Invalid: not a number");\n  console.log("Band:    -");\n'
                    '} else if (n < 0) {\n'
                    '  console.log("Invalid: negative");\n  console.log("Band:    -");\n'
                    '} else {\n'
                    '  console.log(`Amount:  ${n.toFixed(2)}`);\n'
                    '  console.log(`Band:    ${n < 10 ? "small" : n < 50 ? "medium" : "large"}`);\n'
                    '  console.log(`Note:    ${n > 100 ? "over budget" : "fine"}`);\n'
                    '}\n',
                    'console.log(`Note:    ${n > 100 ? "over budget" : "fine"}`);',
                    [("25", "Amount:  25.00\nBand:    medium\nNote:    fine"),
                     ("150", "Amount:  150.00\nBand:    large\nNote:    over budget"),
                     ("abc", "Invalid: not a number\nBand:    -")],
                    hints=["The new line belongs inside the final else, so invalid input never reaches it.",
                           'Use a ternary in the hole: ${n > 100 ? "over budget" : "fine"}.']),
    ),
))

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

# ===========================================================================
# MONTH 2 — Data & functions
# ===========================================================================
_M2 = "Data & Functions"

# --- Week 5 ---------------------------------------------------------------
_WEEKS.append(_week(
    5, 2, _M2,
    "Functions",
    "Package logic into named, reusable functions with parameters, return values, guards, defaults and predictable behaviour.",
    """
Everything you've written so far has been one long script. This week you learn
to **name a piece of logic** so you can use it again, test it on its own, and
read it without re-deriving it.

A **function** takes inputs (**parameters**), does something, and hands back a
**return value**. That's it. But the consequences are large:

- You write the tricky bit **once** and fix bugs in one place.
- The name becomes documentation: `withTax(amount)` explains itself.
- Each piece can be reasoned about alone, which is the only way anything big
  stays understandable.

You'll also meet **annotations on the boundary** — `(x: number): number` — which
is where TypeScript really starts to earn its name. The compiler checks every
call site against that signature, so a wrong argument is caught while you type
rather than at 3am.

⏱️ Budget about **nine hours**, spread over several sittings.
""",
    objectives=[
        "Declare a function with parameters, a return type, and a return value",
        "Call a function and use what it hands back",
        "Write compact functions as arrow functions",
        "Return early with guard clauses instead of deep nesting",
        "Give parameters defaults and mark them optional",
        "Explain scope, shadowing, and why a pure function is easier to trust",
        "Pass a function to another function as a value",
        "Return a function from a function, and explain what a closure captures",
        "Write a function's contract — name, inputs, output, preconditions — before its body",
        "Trace a nested call by substituting each return value, and extract a helper on the third repetition",
    ],
    why="Functions are how you stop a program growing into an unreadable sheet of statements. Every abstraction you will ever build — modules, classes, components, APIs — is this idea repeated at a larger scale.",
    est_minutes=540,
    glossary=[
        _gloss("function", "Named, reusable logic that takes inputs and returns a value."),
        _gloss("parameter", "A named input, written in the declaration."),
        _gloss("argument", "The actual value you pass at the call site."),
        _gloss("signature", "The parameter types and return type together: (x: number) => number."),
        _gloss("return", "Hands a value back to the caller AND ends the function immediately."),
        _gloss("call site", "The place where a function is invoked."),
        _gloss("arrow function", "A compact form: const f = (x: number): number => x * 2."),
        _gloss("guard clause", "An early return that rejects a case up front, keeping the body flat."),
        _gloss("default parameter", "A value used when the argument is omitted: (rate = 0.08)."),
        _gloss("optional parameter", "A parameter marked with ? that may be undefined."),
        _gloss("void", "The return type of a function that returns nothing useful."),
        _gloss("scope", "The region where a name is visible."),
        _gloss("shadowing", "An inner name hiding an outer one of the same name."),
        _gloss("pure function", "Same inputs, same output, no side effects."),
        _gloss("side effect", "Anything a function does beyond returning — printing, changing an outer variable."),
        _gloss("composition", "Feeding one function's result into another: whole(withTax(x))."),
        _gloss("higher-order function", "A function that takes or returns another function."),
        _gloss("hoisting", "Function declarations are usable before the line that defines them; const arrow functions are not."),
        _gloss("closure", "A function together with the variables it captured from the scope around it."),
        _gloss("factory", "A function whose job is to build and return another function."),
        _gloss("contract", "The name, inputs, output and preconditions a function promises to honour."),
        _gloss("stub", "A function body that returns a placeholder so the rest of the program can already call it."),
        _gloss("tracing", "Working out a result by hand: replace each call with the value it returned."),
        _gloss("extraction", "Turning a repeated line into a function whose parameter is the part that varied."),
    ],
    cheatsheet="""
```ts
// ---- declaration -----------------------------------------------------
function square(x: number): number {
  return x * x;
}
console.log(square(5));            // 25

// ---- several parameters ----------------------------------------------
function lineTotal(price: number, qty: number): number {
  return price * qty;
}
lineTotal(3.25, 4)                 // 13   — order matters

// ---- arrow function ---------------------------------------------------
const cube = (x: number): number => x * x * x;       // auto-returns
const cube2 = (x: number): number => { return x * x * x; };   // needs return

// ---- guard clause ------------------------------------------------------
function describe(n: number): string {
  if (Number.isNaN(n)) return "not a number";        // reject early
  if (n < 0) return "negative";
  return "ok";                                        // the happy path, flat
}

// ---- defaults & optionals ----------------------------------------------
function withTax(amount: number, rate: number = 0.08): number {
  return amount * (1 + rate);
}
withTax(100)         // 108   — rate defaulted
withTax(100, 0.2)    // 120

function greet(name: string, title?: string): string {
  return title === undefined ? `Hi ${name}` : `Hi ${title} ${name}`;
}

// ---- returns nothing ---------------------------------------------------
function banner(text: string): void {
  console.log("-".repeat(text.length));
}

// ---- a function as a value ---------------------------------------------
function applyTwice(f: (x: number) => number, x: number): number {
  return f(f(x));
}
applyTwice(cube, 2)   // 512
```
""",
    self_check=[
        "Can you write a function that takes two numbers and returns a result?",
        "Can you explain the difference between console.log and return?",
        "Can you rewrite a two-line function as an arrow function?",
        "Can you replace a nested if/else with guard clauses?",
        "Can you give a parameter a default and say when the default is used?",
        "Can you say why a pure function is easier to test than one that prints?",
        "Can you pass one function into another as an argument?",
        "Can you write a function that returns a configured function, and say what it remembers?",
        "Can you state a function's contract before writing a line of its body?",
        "Can you trace inc(twice(5)) on paper, and say which guard order a grade() needs?",
    ],
    review=[
        _q("What does `return` do?",
           ["Prints a value", "Hands a value back to the caller and ends the function",
            "Declares a variable", "Starts a loop"], 1,
           "It produces the function's result and stops it there and then."),
        _q("In `function f(x: number)`, `x` is a…",
           ["return value", "parameter", "global", "argument"], 1,
           "A parameter. The value you pass at the call site is the argument."),
        _q("`const d = (x: number): number => x * 2; d(4)` is…",
           ["4", "8", "24", "an error"], 1, "It doubles: 8."),
        _q("A function with no `return` statement returns…",
           ["0", "null", "undefined", "an error"], 2,
           "undefined — which is why a forgotten return prints as `undefined`."),
        _q("`const f = (x: number): number => { x * 2; };` returns…",
           ["2x", "undefined", "an error", "x"], 1,
           "With braces you must write return yourself."),
        _q("A guard clause is…",
           ["a try/catch", "an early return that handles a case and leaves",
            "a loop condition", "a type annotation"], 1,
           "It keeps the main path flat and unindented."),
        _q("`function f(a: number, b: number = 2)` — what is `f(5)`'s b?",
           ["undefined", "0", "2", "an error"], 2,
           "The default fills in for the omitted argument."),
        _q("A pure function…",
           ["prints its result", "returns the same output for the same input and changes nothing else",
            "has no parameters", "is always short"], 1,
           "Which is exactly what makes it trivially testable."),
        _q("Which can you call on the line ABOVE where it is written?",
           ["const f = () => ...", "function f() { ... }", "both", "neither"], 1,
           "Function declarations are hoisted; const arrow functions are not."),
        _q("`applyTwice(cube, 2)` passes `cube`…",
           ["as a string", "as a value — the function itself, not its result",
            "by calling it first", "as a number"], 1,
           "Note there are no parentheses after cube — that is the whole point."),
        _q("What is a function's contract?",
           ["its length", "its name, inputs, output and preconditions", "its call sites", "its return statement"], 1,
           "Decide it first and the body usually writes itself."),
        _q("Tracing `inc(twice(5))`, you first replace…",
           ["inc with its body", "twice(5) with 10", "5 with 10", "nothing"], 1,
           "Innermost call first — substitute the value it returned."),
        _q("Copying a line and changing one number in it is a sign that…",
           ["the code is fine", "that number wants to be a parameter",
            "you need a loop", "the function is pure"], 1,
           "The part that varies between copies is exactly the input."),
    ],
    milestone="Budget Buddy is now built from named helpers instead of one long script — the first version you could hand to somebody else and have them understand.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w5-declare", "Declaring a function",
            "function name(params): type { return ... }",
            """
```ts
function square(x: number): number {
  return x * x;
}

console.log(square(5));    // 25
console.log(square(3));    // 9
```

Every part earns its place:

| piece | name | meaning |
|---|---|---|
| `function` | keyword | "here comes a named piece of logic" |
| `square` | name | how you'll call it |
| `(x: number)` | parameter list | one input, annotated as a number |
| `: number` | return type | what it hands back |
| `{ ... }` | body | what it does |
| `return x * x` | return statement | the result |

**`return` is not `console.log`.** This is the single most common confusion at
this stage:

- `console.log(v)` **shows** `v` on screen. The value is gone afterwards.
- `return v` **hands `v` back** to whoever called the function, so they can use
  it, store it, or combine it.

```ts
function bad(x: number): void { console.log(x * 2); }   // shows it
function good(x: number): number { return x * 2; }      // gives it back

const t = good(5) + good(5);   // 20   — you can do this
```

You can't add up things that were only printed.

**`return` ends the function immediately.** Anything after it never runs:

```ts
function f(): number {
  return 1;
  console.log("never");   // unreachable
}
```

**A function with no return** hands back `undefined`. That's the cause of the
classic "why does it print undefined?" — a body that computes the answer and
then forgets to give it back.

**Hoisting.** A `function` declaration can be called from a line above where
it's written. That's why helper functions are often placed at the bottom of a
file, with the main flow readable at the top.

> ⚠️ **Common mistakes:** forgetting `return`; printing instead of returning;
> and putting statements after `return` and wondering why they never run.
""",
            warmup=[
                _q("`function f(x){ return x + 1; } console.log(f(4));` prints…",
                   ["4", "5", "x + 1", "undefined"], 1, "f(4) returns 5."),
                _q("`function f(x){ x + 1; } console.log(f(4));` prints…",
                   ["4", "5", "undefined", "an error"], 2,
                   "It computes and discards; with no return the result is undefined."),
                _q("`function f(){ return 1; console.log(2); } f();` prints…",
                   ["1", "2", "nothing", "1 then 2"], 2,
                   "return ends the function, so the log is unreachable."),
            ],
            exercises=[
                _ex("tscourse-w5-dec-1", "Square", "Return x multiplied by itself.",
                    'function square(x: number): number {\n  return x * x;\n}\nconsole.log(square(5));\n',
                    'return x * x;', [("", "25")],
                    hints=["Hand the result back rather than printing it.",
                           "Write return x * x;"]),
                _ex("tscourse-w5-dec-2", "Greet", "Return a greeting string for the given name.",
                    'function greet(name: string): string {\n  return `Hello, ${name}!`;\n}\nconsole.log(greet("Ada"));\n',
                    '`Hello, ${name}!`', [("", "Hello, Ada!")],
                    hints=["Return a template literal that uses the parameter."]),
                _ex("tscourse-w5-dec-3", "Name the return type",
                    "Fill in the return type annotation. This function hands back text.",
                    'function describe(n: number): string {\n  return `n is ${n}`;\n}\nconsole.log(describe(7));\n',
                    'string', [("", "n is 7")],
                    hints=["The return type goes after the parameter list, before the body.",
                           "It hands back text, so the annotation is string."]),
                _ex("tscourse-w5-dec-4", "Use the result twice",
                    "Print double(5) added to double(10) — the function must return, not print.",
                    'function double(x: number): number {\n  return x * 2;\n}\nconsole.log(double(5) + double(10));\n',
                    'double(5) + double(10)', [("", "30")],
                    hints=["Because it returns, you can combine the two calls in one expression.",
                           "Write double(5) + double(10)."]),
                _ex("tscourse-w5-dec-5", "Call it on input",
                    "Read a number and print its square, using the function.",
                    _FS + 'function square(x: number): number {\n  return x * x;\n}\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(square(n));\n',
                    'square(n)', [("5", "25"), ("9", "81")],
                    hints=["Pass the input as the argument.", "Write square(n)."]),
                _fix("tscourse-w5-dec-fix1", "Fix the missing return",
                     "This should print 25 but prints undefined. Fix it.",
                     'function square(x: number): number {\n  x * x;\n}\nconsole.log(square(5));\n',
                     'function square(x: number): number {\n  return x * x;\n}\nconsole.log(square(5));\n',
                     [("", "25")],
                     hints=["The function computes x*x but never hands it back.",
                            "Add return before x * x."]),
                _fix("tscourse-w5-dec-fix2", "Fix print-versus-return",
                     "This prints 10 then `undefined` — the function logs instead of returning. Make it print just 10.",
                     'function double(x: number) {\n  console.log(x * 2);\n}\nconsole.log(double(5));\n',
                     'function double(x: number): number {\n  return x * 2;\n}\nconsole.log(double(5));\n',
                     [("", "10")],
                     hints=["The inner log shows the value; the outer log then shows what was returned — nothing.",
                            "Return the value instead of logging it inside."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What is the difference between return and console.log?",
                   ["None", "return hands the value back to the caller; console.log only displays it",
                    "console.log is faster", "return prints too"], 1,
                   "Only a returned value can be used in further computation."),
                _q("A function whose body never reaches a return gives back…",
                   ["0", "undefined", '""', "an error"], 1,
                   "undefined — the source of countless 'why undefined?' moments."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w5-params", "Parameters & arguments",
            "Several inputs, in a fixed order.",
            """
Functions can take any number of inputs, separated by commas:

```ts
function lineTotal(price: number, qty: number): number {
  return price * qty;
}
console.log(lineTotal(3.25, 4));   // 13
```

**Parameter vs argument** — worth keeping straight:

- **Parameter**: the name in the declaration (`price`, `qty`).
- **Argument**: the value at the call site (`3.25`, `4`).

**Order is everything.** Arguments are matched by position, not by name:

```ts
function divide(a: number, b: number): number { return a / b; }
divide(10, 2)   // 5
divide(2, 10)   // 0.2   — no error, just wrong
```

TypeScript catches a wrong *type* here but cannot catch a wrong *order* when
both are numbers. Two defences: name parameters so the call reads sensibly, and
keep the count small. More than three or four arguments is a signal that the
inputs want grouping into an object (week 7).

**Composition.** Because a function returns a value, one call can be the
argument to another:

```ts
function withTax(amount: number): number { return amount * 1.08; }
function whole(amount: number): number { return Math.floor(amount); }

console.log(whole(withTax(50)));   // 54
```

Read those inside-out: `withTax(50)` produces 54, which `whole` then floors.
Chaining small, well-named functions like this is most of what "good structure"
means in practice.

**Parameters are local copies.** Reassigning one inside the function has no
effect on the caller's variable:

```ts
function f(x: number): number { x = 99; return x; }
const a = 1;
f(a);            // 99
console.log(a);  // still 1
```

> ⚠️ **Common mistakes:** swapping arguments; forgetting to *call* the function
> (writing `double` instead of `double(21)`); and passing the wrong count —
> TypeScript will tell you, so read the error.
""",
            warmup=[
                _q("`function add(a, b){ return a - b; } add(5, 3)` returns…",
                   ["8", "2", "15", "an error"], 1, "This (deliberately misnamed) function subtracts."),
                _q("`function sub(a, b){ return a - b; } sub(3, 5)` returns…",
                   ["2", "-2", "8", "an error"], 1, "Order matters: 3 - 5."),
                _q("In `greet(\"Ada\")`, `\"Ada\"` is the…",
                   ["parameter", "argument", "return value", "signature"], 1,
                   "The value at the call site is the argument."),
                _q("`whole(withTax(50))` evaluates which first?",
                   ["whole", "withTax", "neither", "both at once"], 1,
                   "Inner calls are evaluated before the outer one can use their result."),
            ],
            exercises=[
                _ex("tscourse-w5-par-1", "Two parameters",
                    "Return the line total for a price and a quantity.",
                    'function lineTotal(price: number, qty: number): number {\n  return price * qty;\n}\n'
                    'console.log(lineTotal(3.25, 4));\n',
                    'price * qty', [("", "13")],
                    hints=["Multiply the two parameters.", "Write price * qty."]),
                _ex("tscourse-w5-par-2", "Double the input",
                    "Return x doubled; the program prints double(n) for the input n.",
                    _FS + 'function double(x: number): number {\n  return x * 2;\n}\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(double(n));\n',
                    'x * 2', [("21", "42"), ("0", "0")],
                    hints=["Multiply the parameter by 2."]),
                _ex("tscourse-w5-par-3", "Three inputs",
                    "Return the total for a price, a quantity and a flat delivery fee.",
                    'function orderTotal(price: number, qty: number, delivery: number): number {\n'
                    '  return price * qty + delivery;\n}\n'
                    'console.log(orderTotal(3, 4, 5));\n',
                    'price * qty + delivery', [("", "17")],
                    hints=["Multiply, then add the fee.",
                           "Write price * qty + delivery."]),
                _ex("tscourse-w5-par-4", "Compose two functions",
                    "Print the taxed amount floored to a whole number, by calling one function inside the other.",
                    'function withTax(amount: number): number {\n  return amount * 1.08;\n}\n'
                    'function whole(amount: number): number {\n  return Math.floor(amount);\n}\n'
                    'console.log(whole(withTax(50)));\n',
                    'whole(withTax(50))', [("", "54")],
                    hints=["The inner call runs first and its result becomes the outer argument.",
                           "Write whole(withTax(50))."],
                    difficulty="Medium"),
                _ex("tscourse-w5-par-5", "Percentage of",
                    "Return what percent `part` is of `total`, to one decimal place, as a string like `25.0`.",
                    _FS + 'function percentOf(part: number, total: number): string {\n'
                    '  return ((part / total) * 100).toFixed(1);\n}\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(percentOf(n, 200));\n',
                    '((part / total) * 100).toFixed(1)',
                    [("50", "25.0"), ("200", "100.0"), ("0", "0.0")],
                    hints=["Divide, scale by 100, then fix the decimals.",
                           "Write ((part / total) * 100).toFixed(1)."],
                    difficulty="Medium"),
                _fix("tscourse-w5-par-fix1", "Fix the missing call",
                     "This should print 42 but prints the function itself. Fix the call.",
                     _FS + 'function double(x: number): number {\n  return x * 2;\n}\n'
                     'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(double);\n',
                     _FS + 'function double(x: number): number {\n  return x * 2;\n}\n'
                     'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(double(n));\n',
                     [("21", "42")],
                     hints=["`double` names the function; it does not run it.",
                            "Add the parentheses and the argument: double(n)."]),
                _fix("tscourse-w5-par-fix2", "Fix the argument order",
                     "This should print 5 for `divide(10, 2)` but prints 0.2. Fix it.",
                     'function divide(a: number, b: number): number {\n  return b / a;\n}\n'
                     'console.log(divide(10, 2));\n',
                     'function divide(a: number, b: number): number {\n  return a / b;\n}\n'
                     'console.log(divide(10, 2));\n',
                     [("", "5")],
                     hints=["The body divides the second parameter by the first.",
                            "Swap them: return a / b;"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Arguments are matched to parameters by…",
                   ["name", "position", "type", "alphabetical order"], 1,
                   "Which is why swapping two same-typed arguments is invisible to the compiler."),
                _q("Reassigning a parameter inside a function…",
                   ["changes the caller's variable", "affects only the local copy",
                    "is an error", "returns it"], 1,
                   "For numbers and strings the caller is untouched."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w5-arrow", "Arrow functions",
            "A compact form for small functions.",
            """
For short functions there's a lighter syntax:

```ts
const cube = (x: number): number => x * x * x;
console.log(cube(3));    // 27
```

Compare the two forms side by side:

```ts
function cube(x: number): number {
  return x * x * x;
}

const cube = (x: number): number => x * x * x;
```

**The implicit return.** When the body is a single expression with no braces,
its value is returned automatically — no `return` keyword. Add braces and you're
back to writing it yourself:

```ts
const a = (x: number): number => x * 2;              // returns 2x
const b = (x: number): number => { return x * 2; };  // returns 2x
const c = (x: number): number => { x * 2; };         // ⚠️ returns undefined
```

That third one is the classic arrow mistake. Braces mean "here is a block of
statements", and a block returns nothing unless told to.

**Several parameters** need the parentheses; a body over one expression needs
the braces:

```ts
const add = (a: number, b: number): number => a + b;
```

**Declaration vs arrow — which to use?**

| | `function` | arrow |
|---|---|---|
| hoisted (callable above) | yes | no |
| best for | named, standalone logic | short helpers, and functions passed as values |

They behave differently in one deeper way too (around a keyword called `this`),
which you'll meet with objects. For everything this week, pick whichever reads
better — and reach for arrows when the function is small or is being handed to
another function (lesson 7).

> ⚠️ **Common mistakes:** braces without `return`; calling a `const` arrow above
> the line that defines it (it isn't hoisted); and forgetting that
> `const f = ...` is a variable declaration, so it ends with a semicolon.
""",
            warmup=[
                _q("`const f = (x: number) => x + 10; f(5)` is…",
                   ["5", "10", "15", "an error"], 2, "5 + 10."),
                _q("`const f = (x: number) => { x + 10; }; f(5)` is…",
                   ["15", "undefined", "5", "an error"], 1,
                   "With braces you must write return."),
                _q("Which can be called on the line above its definition?",
                   ["const f = () => 1;", "function f() { return 1; }", "both", "neither"], 1,
                   "Only function declarations are hoisted."),
            ],
            exercises=[
                _ex("tscourse-w5-arr-1", "Cube (arrow)", "Return x cubed, using the implicit return.",
                    'const cube = (x: number): number => x * x * x;\nconsole.log(cube(3));\n',
                    'x * x * x', [("", "27")],
                    hints=["No braces, no return — just the expression.",
                           "Write x * x * x."]),
                _ex("tscourse-w5-arr-2", "Triple (arrow)",
                    "Return x * 3; the program prints triple(n) for the input.",
                    _FS + 'const triple = (x: number): number => x * 3;\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(triple(n));\n',
                    'x * 3', [("5", "15"), ("10", "30")],
                    hints=["Multiply x by 3."]),
                _ex("tscourse-w5-arr-3", "Two parameters, arrow style",
                    "Write the arrow that adds its two parameters.",
                    'const add = (a: number, b: number): number => a + b;\nconsole.log(add(2, 40));\n',
                    'a + b', [("", "42")],
                    hints=["The body is a single expression.", "Write a + b."]),
                _ex("tscourse-w5-arr-4", "Arrow returning text",
                    "Return an initial-plus-dot for a name: `Ada` → `A.`",
                    _FS + 'const initial = (name: string): string => `${name[0].toUpperCase()}.`;\n'
                    'const s = fs.readFileSync(0, "utf8").trim();\nconsole.log(initial(s));\n',
                    '`${name[0].toUpperCase()}.`',
                    [("Ada", "A."), ("bo", "B.")],
                    hints=["Take the first character, uppercase it, and append a dot.",
                           "Write `${name[0].toUpperCase()}.`"],
                    difficulty="Medium"),
                _ex("tscourse-w5-arr-5", "Explicit return in a block",
                    "This arrow needs a block because it has two statements. Add the return.",
                    'const doubleThenAddOne = (x: number): number => {\n'
                    '  const d = x * 2;\n  return d + 1;\n};\n'
                    'console.log(doubleThenAddOne(5));\n',
                    'return d + 1;', [("", "11")],
                    hints=["Inside braces nothing is returned automatically.",
                           "Write return d + 1;"]),
                _fix("tscourse-w5-arr-fix1", "Fix the arrow body",
                     "This prints undefined instead of 8. Fix it so cube(2) is 8.",
                     'const cube = (x: number): number => { x * x * x; };\nconsole.log(cube(2));\n',
                     'const cube = (x: number): number => x * x * x;\nconsole.log(cube(2));\n',
                     [("", "8")],
                     hints=["With braces you must return explicitly.",
                            "Either add return, or drop the braces for the implicit return."]),
                _fix("tscourse-w5-arr-fix2", "Fix the too-early call",
                     "This crashes because the arrow is used before it exists. Fix it by moving the call.",
                     'console.log(half(10));\nconst half = (x: number): number => x / 2;\n',
                     'const half = (x: number): number => x / 2;\nconsole.log(half(10));\n',
                     [("", "5")],
                     hints=["Arrow functions stored in a const are not hoisted.",
                            "Define it first, then call it."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`(x) => x * 2` returns…",
                   ["undefined", "2x", "a block", "an error"], 1,
                   "A braceless body returns its expression."),
                _q("`(x) => { x * 2 }` returns…",
                   ["2x", "undefined", "a block", "an error"], 1,
                   "A block returns nothing unless you write return."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w5-guards", "Guard clauses & early return",
            "Handling the awkward cases first, and keeping the main path flat.",
            """
`return` ends the function *immediately*. That's not just a way to produce a
value — it's a structural tool.

Compare. Nested:

```ts
function describe(n: number): string {
  if (!Number.isNaN(n)) {
    if (n >= 0) {
      if (n <= 100) {
        return "in range";
      } else {
        return "too big";
      }
    } else {
      return "negative";
    }
  } else {
    return "not a number";
  }
}
```

Guarded:

```ts
function describe(n: number): string {
  if (Number.isNaN(n)) return "not a number";
  if (n < 0) return "negative";
  if (n > 100) return "too big";
  return "in range";
}
```

Same behaviour. The second version reads top to bottom as a list of rejections
followed by the answer, never indents past one level, and lets you add a rule by
adding a line.

**The pattern:** deal with every exceptional case first, each with its own early
`return`. By the time you reach the last line, everything awkward has already
left the building — so the **happy path** sits at the end, unindented, with no
conditions attached.

**Order still matters**, exactly as in an `else if` chain. Each guard may assume
all the earlier ones passed, which is precisely what makes them short.

**Multiple returns are fine.** Some people are taught "one return per function".
For guard clauses, that advice makes code worse: it forces a mutable result
variable and deeper nesting. Prefer several early returns.

> ⚠️ **Common mistakes:** guards in the wrong order (a broad one first makes the
> rest unreachable); forgetting a final return, so some path yields `undefined`;
> and writing `if (cond) return;` in a function that's supposed to return a
> value.
""",
            warmup=[
                _q("What does an early `return` do to the rest of the body?",
                   ["Runs it anyway", "Skips it entirely", "Runs it later", "Errors"], 1,
                   "The function ends there and then."),
                _q("A guard clause's main benefit is…",
                   ["speed", "keeping the main path flat and unindented",
                    "fewer characters", "type safety"], 1,
                   "Readability: exceptions first, answer last."),
                _q("If a function's last guard is missing and no path returns, the result is…",
                   ["0", "undefined", "an error", "the last value computed"], 1,
                   "undefined — and TypeScript will usually warn you."),
            ],
            exercises=[
                _ex("tscourse-w5-grd-1", "Reject the bad case first",
                    "Return `not a number` for NaN input, otherwise the doubled value as a string.",
                    _FS + 'function describe(n: number): string {\n'
                    '  if (Number.isNaN(n)) return "not a number";\n'
                    '  return String(n * 2);\n}\n'
                    'console.log(describe(Number(fs.readFileSync(0, "utf8").trim())));\n',
                    'if (Number.isNaN(n)) return "not a number";',
                    [("abc", "not a number"), ("21", "42")],
                    hints=["One line: test the bad case and return immediately.",
                           'Write if (Number.isNaN(n)) return "not a number";']),
                _ex("tscourse-w5-grd-2", "A ladder of guards",
                    "Return `negative`, `too big` (over 100) or `in range`.",
                    _FS + 'function describe(n: number): string {\n'
                    '  if (n < 0) return "negative";\n'
                    '  if (n > 100) return "too big";\n'
                    '  return "in range";\n}\n'
                    'console.log(describe(Number(fs.readFileSync(0, "utf8").trim())));\n',
                    'if (n > 100) return "too big";',
                    [("-1", "negative"), ("150", "too big"), ("50", "in range"), ("100", "in range")],
                    hints=["The second guard only sees non-negative numbers.",
                           'Write if (n > 100) return "too big";']),
                _ex("tscourse-w5-grd-3", "Empty first",
                    "Return `(empty)` for an empty string, otherwise the string uppercased.",
                    _FS + 'function label(s: string): string {\n'
                    '  if (!s) return "(empty)";\n'
                    '  return s.toUpperCase();\n}\n'
                    'console.log(label(fs.readFileSync(0, "utf8").trim()));\n',
                    '!s',
                    [("", "(empty)"), ("hi", "HI")],
                    hints=["An empty string is falsy.", "The guard condition is !s."]),
                _ex("tscourse-w5-grd-4", "The happy path last",
                    "Complete the function so a valid, non-negative amount returns its formatted value.",
                    _FS + 'function money(n: number): string {\n'
                    '  if (Number.isNaN(n)) return "invalid";\n'
                    '  if (n < 0) return "negative";\n'
                    '  return `$${n.toFixed(2)}`;\n}\n'
                    'console.log(money(Number(fs.readFileSync(0, "utf8").trim())));\n',
                    'return `$${n.toFixed(2)}`;',
                    [("abc", "invalid"), ("-2", "negative"), ("7.5", "$7.50")],
                    hints=["By this line the value is known to be a valid non-negative number.",
                           "Return `$${n.toFixed(2)}`."],
                    difficulty="Medium"),
                _ex("tscourse-w5-grd-5", "Guard inside a loop-free check",
                    "Return `too short` when the input is under 3 characters, `too long` over 10, else `ok`.",
                    _FS + 'function check(s: string): string {\n'
                    '  if (s.length < 3) return "too short";\n'
                    '  if (s.length > 10) return "too long";\n'
                    '  return "ok";\n}\n'
                    'console.log(check(fs.readFileSync(0, "utf8").trim()));\n',
                    's.length < 3',
                    [("ab", "too short"), ("abcdefghijk", "too long"), ("hello", "ok"), ("abc", "ok")],
                    hints=["3 itself is acceptable, so the rejection is strictly under 3.",
                           "Write s.length < 3."]),
                _fix("tscourse-w5-grd-fix1", "Fix the guard order",
                     "Every input returns `in range`, even -5. Fix the order.",
                     _FS + 'function describe(n: number): string {\n'
                     '  if (n <= 100) return "in range";\n'
                     '  if (n < 0) return "negative";\n'
                     '  return "too big";\n}\n'
                     'console.log(describe(Number(fs.readFileSync(0, "utf8").trim())));\n',
                     _FS + 'function describe(n: number): string {\n'
                     '  if (n < 0) return "negative";\n'
                     '  if (n > 100) return "too big";\n'
                     '  return "in range";\n}\n'
                     'console.log(describe(Number(fs.readFileSync(0, "utf8").trim())));\n',
                     [("-5", "negative"), ("150", "too big"), ("50", "in range")],
                     hints=["`n <= 100` is true for every negative number too, so it fires first.",
                            "Reject the negative case before testing the range."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Guard clauses replace…",
                   ["loops", "deep if/else nesting", "type annotations", "return values"], 1,
                   "They flatten the structure by leaving early."),
                _q("'One return per function' applied to guard clauses tends to…",
                   ["improve them", "force a mutable result variable and more nesting",
                    "make them faster", "have no effect"], 1,
                   "Which is why the rule is not followed in modern code."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w5-defaults", "Defaults, optionals & void",
            "Parameters that don't always have to be supplied.",
            """
**Default parameters** supply a value when the argument is omitted:

```ts
function withTax(amount: number, rate: number = 0.08): number {
  return amount * (1 + rate);
}

withTax(100)        // 108   — rate defaulted to 0.08
withTax(100, 0.2)   // 120
```

The default is evaluated **only when the argument is missing** (or explicitly
`undefined`). Passing `0` is a real value and overrides it — passing `0` and
getting the default anyway is the bug people expect here and don't get. Good.

**Defaults must come last.** Otherwise you'd have no way to skip them:

```ts
function bad(rate: number = 0.08, amount: number): number { ... }  // ⚠️ awkward
```

**Optional parameters** use `?` and may simply be absent, arriving as
`undefined`:

```ts
function greet(name: string, title?: string): string {
  if (title === undefined) return `Hi ${name}`;
  return `Hi ${title} ${name}`;
}

greet("Ada")            // Hi Ada
greet("Ada", "Dr")      // Hi Dr Ada
```

Use a **default** when there's a sensible fallback value; use **optional** when
absence itself means something different.

**`void`** is the return type of a function that returns nothing useful —
typically because its whole job is a side effect like printing:

```ts
function banner(text: string): void {
  console.log(text);
  console.log("-".repeat(text.length));
}
```

Annotating `void` is a promise to the reader: *don't expect a value back from
this*.

> ⚠️ **Common mistakes:** putting a defaulted parameter before a required one;
> assuming a default fires for `0` or `""` (it doesn't — only for `undefined`);
> and forgetting to handle the `undefined` case of an optional parameter.
""",
            warmup=[
                _q("`function f(a: number, b: number = 2){ return a + b; } f(5)` is…",
                   ["5", "7", "undefined", "an error"], 1, "b defaults to 2."),
                _q("`function f(a: number, b: number = 2){ return a + b; } f(5, 0)` is…",
                   ["7", "5", "2", "undefined"], 1,
                   "0 is a real argument, so the default is not used."),
                _q("An optional parameter that is not passed arrives as…",
                   ["0", "null", "undefined", '""'], 2, "undefined."),
                _q("A function annotated `: void`…",
                   ["returns 0", "returns nothing useful", "cannot be called",
                    "returns a string"], 1,
                   "It exists for its side effect."),
            ],
            exercises=[
                _ex("tscourse-w5-def-1", "Give the rate a default",
                    "Default the tax rate to 0.08 so withTax(100) prints 108.00.",
                    'function withTax(amount: number, rate: number = 0.08): number {\n'
                    '  return amount * (1 + rate);\n}\n'
                    'console.log(withTax(100).toFixed(2));\n',
                    'rate: number = 0.08', [("", "108.00")],
                    hints=["A default is written with = in the parameter list.",
                           "Write rate: number = 0.08."]),
                _ex("tscourse-w5-def-2", "Override the default",
                    "Call withTax with an explicit 20% rate so it prints 120.",
                    'function withTax(amount: number, rate: number = 0.08): number {\n'
                    '  return amount * (1 + rate);\n}\n'
                    'console.log(withTax(100, 0.2));\n',
                    'withTax(100, 0.2)', [("", "120")],
                    hints=["Pass the rate as a second argument.",
                           "Write withTax(100, 0.2)."]),
                _ex("tscourse-w5-def-3", "A default separator",
                    "Default the separator to `, ` so join2(\"a\", \"b\") is `a, b`.",
                    'function join2(a: string, b: string, sep: string = ", "): string {\n'
                    '  return a + sep + b;\n}\n'
                    'console.log(join2("a", "b"));\n',
                    'sep: string = ", "', [("", "a, b")],
                    hints=["The default goes in the parameter list.",
                           'Write sep: string = ", ".']),
                _ex("tscourse-w5-def-4", "Handle the optional",
                    "Return `Hi Ada` when no title is given, `Hi Dr Ada` when one is.",
                    'function greet(name: string, title?: string): string {\n'
                    '  if (title === undefined) return `Hi ${name}`;\n'
                    '  return `Hi ${title} ${name}`;\n}\n'
                    'console.log(greet("Ada"));\nconsole.log(greet("Ada", "Dr"));\n',
                    'title === undefined',
                    [("", "Hi Ada\nHi Dr Ada")],
                    hints=["An omitted optional parameter is undefined.",
                           "Test title === undefined."],
                    difficulty="Medium"),
                _ex("tscourse-w5-def-5", "A void helper",
                    "Complete the banner function's return type — it only prints, so it hands nothing back.",
                    'function banner(text: string): void {\n'
                    '  console.log(text);\n  console.log("-".repeat(text.length));\n}\n'
                    'banner("Report");\n',
                    'void', [("", "Report\n------")],
                    hints=["There is a return type reserved for functions that return nothing useful.",
                           "The annotation is void."]),
                _fix("tscourse-w5-def-fix1", "Fix the parameter order",
                     "A defaulted parameter sits before a required one, which forces every caller to pass both. Reorder them so `charge(100)` works and prints 108.00.",
                     'function charge(rate: number = 0.08, amount: number): number {\n'
                     '  return amount * (1 + rate);\n}\n'
                     'console.log(charge(0.08, 100).toFixed(2));\n',
                     'function charge(amount: number, rate: number = 0.08): number {\n'
                     '  return amount * (1 + rate);\n}\n'
                     'console.log(charge(100).toFixed(2));\n',
                     [("", "108.00")],
                     hints=["Optional and defaulted parameters belong at the end.",
                            "Put amount first, then rate with its default, and simplify the call."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A default parameter fires when the argument is…",
                   ["0", '""', "undefined or omitted", "null"], 2,
                   "Only undefined (or absent) triggers it."),
                _q("Defaulted and optional parameters must be…",
                   ["first", "last", "alphabetical", "annotated as any"], 1,
                   "Otherwise callers could not skip them."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w5-scope", "Scope, shadowing & purity",
            "Where names live, and why some functions are easier to trust.",
            """
**Scope** is the region of code where a name is visible. `let` and `const` are
**block-scoped**: they exist inside the nearest `{ }` and nowhere else.

```ts
function f(): void {
  const inner = 1;
  console.log(inner);      // fine
}
console.log(inner);        // ❌ not defined out here
```

A function can *read* names from the scope around it, but the outside can't see
in. That asymmetry is the point: a function's internals are its own business.

**Shadowing** happens when an inner name reuses an outer one:

```ts
const n = 1;
function f(): number {
  const n = 2;      // shadows the outer n inside this function
  return n;         // 2
}
console.log(f(), n);   // 2 1
```

Legal, occasionally useful, and a frequent source of confusion — if you find
yourself shadowing by accident, rename.

**Side effects and purity.** A function has a **side effect** if it does
anything beyond computing its return value: printing, modifying an outer
variable, writing a file.

```ts
let total = 0;

function addImpure(x: number): void {
  total += x;                       // side effect: changes the outside
}

function addPure(a: number, b: number): number {
  return a + b;                     // pure: same inputs, same output, no effects
}
```

A **pure** function is easier to trust because:

- You can test it by calling it — nothing needs to be set up first.
- Reading the call site tells you everything that happens.
- Calling it twice with the same input can never differ.

You can't make everything pure — programs have to print things and save
things eventually. The useful discipline is to **keep the calculation pure and
push the side effects to the edges**: compute the report with pure helpers, then
print it once at the end.

> ⚠️ **Common mistakes:** relying on an outer `let` that another part of the
> program also changes; shadowing a name by accident; and mixing computing with
> printing inside one function, which makes it impossible to reuse.
""",
            warmup=[
                _q("A `const` declared inside a function is visible…",
                   ["everywhere", "only inside that function", "only after it",
                    "only in the parameter list"], 1,
                   "Block scope: it exists inside those braces only."),
                _q("`const n = 1; function f(){ const n = 2; return n; } f()` returns…",
                   ["1", "2", "3", "an error"], 1, "The inner n shadows the outer one."),
                _q("Which is pure?",
                   ["one that prints its result", "one that returns a value and changes nothing else",
                    "one with no parameters", "one that reads input"], 1,
                   "No side effects, and the same output for the same input."),
            ],
            exercises=[
                _ex("tscourse-w5-scope-1", "Keep it local",
                    "Complete the function so the calculation happens with a local name.",
                    'function area(w: number, h: number): number {\n'
                    '  const result = w * h;\n  return result;\n}\n'
                    'console.log(area(3, 4));\n',
                    'const result = w * h;', [("", "12")],
                    hints=["Name the intermediate value inside the function.",
                           "Write const result = w * h;"]),
                _ex("tscourse-w5-scope-2", "Return, don't print",
                    "Make the function pure — it must return the label so the caller can print it.",
                    'function label(n: number): string {\n'
                    '  return `Total: ${n}`;\n}\n'
                    'console.log(label(42));\n',
                    'return `Total: ${n}`;', [("", "Total: 42")],
                    hints=["A pure function hands the text back rather than logging it.",
                           "Write return `Total: ${n}`;"]),
                _ex("tscourse-w5-scope-3", "Shadowing on purpose",
                    "Inside the function, declare a local `n` of 2 so it returns 2 while the outer n stays 1.",
                    'const n = 1;\nfunction f(): number {\n  const n = 2;\n  return n;\n}\n'
                    'console.log(f());\nconsole.log(n);\n',
                    'const n = 2;', [("", "2\n1")],
                    hints=["A same-named const inside the function shadows the outer one.",
                           "Write const n = 2; inside f."],
                    difficulty="Medium"),
                _ex("tscourse-w5-scope-4", "Pure calculation, printed once",
                    "Compute the whole report string in a pure helper, then print it in one place.",
                    _FS + 'function report(name: string, amount: number): string {\n'
                    '  return `${name}: $${amount.toFixed(2)}`;\n}\n'
                    'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(report(s, 12.5));\n',
                    'console.log(report(s, 12.5));',
                    [("Coffee", "Coffee: $12.50"), ("Rent", "Rent: $12.50")],
                    hints=["The helper builds the text; the caller does the printing.",
                           "Write console.log(report(s, 12.5));"]),
                _ex("tscourse-w5-scope-5", "Read from the enclosing scope",
                    "The tax rate lives outside the function. Use it inside.",
                    'const RATE = 0.1;\nfunction withTax(amount: number): number {\n'
                    '  return amount * (1 + RATE);\n}\n'
                    'console.log(withTax(100).toFixed(2));\n',
                    'amount * (1 + RATE)', [("", "110.00")],
                    hints=["A function can read names from the scope around it.",
                           "Write amount * (1 + RATE)."]),
                _fix("tscourse-w5-scope-fix1", "Fix the leaky helper",
                     "This should total 5 but prints 3 — the side effect overwrites instead of accumulating. Fix it.",
                     'let total = 0;\nfunction add(x: number): void {\n  total = x;\n}\n'
                     'add(2);\nadd(3);\nconsole.log(total);\n',
                     'let total = 0;\nfunction add(x: number): void {\n  total += x;\n}\n'
                     'add(2);\nadd(3);\nconsole.log(total);\n',
                     [("", "5")],
                     hints=["Each call replaces the shared variable, so only the last one survives.",
                            "It should add to what is already there: total += x;",
                            "Worth noticing: this bug is only possible because the function reaches outside itself. A pure `add(a, b)` returning a + b could not go wrong this way."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why is a pure function easier to test?",
                   ["It is shorter", "Calling it with inputs is the entire test — no setup, no cleanup",
                    "It cannot fail", "It has no parameters"], 1,
                   "Nothing outside it has to be arranged or inspected."),
                _q("The practical discipline with side effects is…",
                   ["never use them", "keep calculation pure and push effects to the edges",
                    "put them everywhere", "use only global variables"], 1,
                   "Compute with pure helpers, print or save once at the boundary."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w5-values", "Functions as values",
            "Passing behaviour around, not just data.",
            """
A function is a **value**. You can store it in a variable, and you can pass it
to another function — which is exactly what `const cube = ...` has been doing
all along.

```ts
const cube = (x: number): number => x * x * x;
const f = cube;         // no parentheses — the function itself
console.log(f(2));      // 8
```

**The parentheses are the difference.** `cube` is the function; `cube(2)` is the
result of running it. Passing `cube(2)` where a function was expected is the
mistake to watch for.

**A function that takes a function:**

```ts
function applyTwice(f: (x: number) => number, x: number): number {
  return f(f(x));
}

console.log(applyTwice(cube, 2));   // cube(cube(2)) = cube(8) = 512
```

Read the parameter's annotation `(x: number) => number` as *"a function taking a
number and returning a number"*. That's the **signature**, and TypeScript checks
that whatever you pass matches it.

A function that takes or returns another function is called a **higher-order
function**. They let you write the *shape* of an operation once and supply the
varying part at the call site:

```ts
function twice(f: (s: string) => string, s: string): string {
  return f(f(s));
}
const excite = (s: string): string => s + "!";
console.log(twice(excite, "wow"));   // wow!!
```

**Why this matters next week.** Arrays come with built-in higher-order methods —
`map`, `filter`, `reduce` — each of which takes exactly this: a small function
describing what to do with one item. Everything in week 6 rests on being
comfortable with the idea that a function can be an argument.

**Inline arrows.** You'll usually define the little function right at the call
site rather than naming it:

```ts
console.log(applyTwice((x: number): number => x + 3, 10));   // 16
```

> ⚠️ **Common mistakes:** passing `f(x)` (the result) where `f` (the function)
> was wanted; annotating a function parameter as `number` instead of a signature;
> and forgetting that the inner function's parameter name is entirely its own.
""",
            warmup=[
                _q("`const g = cube;` stores…",
                   ["the result of cube", "the function itself", "a string", "undefined"], 1,
                   "No parentheses means no call."),
                _q("`applyTwice(cube, 2)` computes…",
                   ["cube(2)", "cube(cube(2))", "2 * cube", "an error"], 1,
                   "The function is applied to its own result."),
                _q("`(x: number) => number` as a parameter type means…",
                   ["a number", "a function from number to number", "an arrow", "a string"], 1,
                   "It is the signature of the function you must pass."),
            ],
            exercises=[
                _ex("tscourse-w5-val-1", "Store a function",
                    "Point `f` at the `cube` function (do not call it), then use it.",
                    'const cube = (x: number): number => x * x * x;\n'
                    'const f = cube;\nconsole.log(f(2));\n',
                    'const f = cube;', [("", "8")],
                    hints=["No parentheses — you want the function, not its result.",
                           "Write const f = cube;"]),
                _ex("tscourse-w5-val-2", "Apply it twice",
                    "Complete applyTwice so it feeds its own result back in.",
                    'const cube = (x: number): number => x * x * x;\n'
                    'function applyTwice(f: (x: number) => number, x: number): number {\n'
                    '  return f(f(x));\n}\n'
                    'console.log(applyTwice(cube, 2));\n',
                    'return f(f(x));', [("", "512")],
                    hints=["Call f on x, then call f on that.",
                           "Write return f(f(x));"],
                    difficulty="Medium"),
                _ex("tscourse-w5-val-3", "Annotate the parameter",
                    "Fill in the signature for a parameter that takes a number and returns a number.",
                    'function applyOnce(f: (x: number) => number, x: number): number {\n'
                    '  return f(x);\n}\n'
                    'console.log(applyOnce((n: number): number => n + 1, 41));\n',
                    '(x: number) => number', [("", "42")],
                    hints=["The type of a function is written like an arrow function without a body.",
                           "Write (x: number) => number."],
                    difficulty="Medium"),
                _ex("tscourse-w5-val-4", "Pass an inline arrow",
                    "Pass a function that adds 3, so the result is 16.",
                    'function applyTwice(f: (x: number) => number, x: number): number {\n'
                    '  return f(f(x));\n}\n'
                    'console.log(applyTwice((x: number): number => x + 3, 10));\n',
                    '(x: number): number => x + 3',
                    [("", "16")],
                    hints=["Define the little function right at the call site.",
                           "Write (x: number): number => x + 3."],
                    difficulty="Medium"),
                _ex("tscourse-w5-val-5", "A string transformer",
                    "Pass a function that appends an exclamation mark, so `wow` becomes `wow!!`.",
                    _FS + 'function twice(f: (s: string) => string, s: string): string {\n'
                    '  return f(f(s));\n}\n'
                    'const input = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(twice((s: string): string => s + "!", input));\n',
                    '(s: string): string => s + "!"',
                    [("wow", "wow!!"), ("hi", "hi!!")],
                    hints=["Each application adds one character.",
                           'Write (s: string): string => s + "!".'],
                    difficulty="Medium"),
                _fix("tscourse-w5-val-fix1", "Fix the accidental call",
                     "This passes the RESULT of cube instead of the function, and crashes. Fix it.",
                     'const cube = (x: number): number => x * x * x;\n'
                     'function applyTwice(f: (x: number) => number, x: number): number {\n'
                     '  return f(f(x));\n}\n'
                     'console.log(applyTwice(cube(2), 2));\n',
                     'const cube = (x: number): number => x * x * x;\n'
                     'function applyTwice(f: (x: number) => number, x: number): number {\n'
                     '  return f(f(x));\n}\n'
                     'console.log(applyTwice(cube, 2));\n',
                     [("", "512")],
                     hints=["cube(2) is the number 8; applyTwice wants something it can call.",
                            "Drop the parentheses: pass cube."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`f` versus `f(x)` — the difference is…",
                   ["none", "f is the function; f(x) is the result of running it",
                    "f is faster", "f(x) is the function"], 1,
                   "Parentheses mean 'run it now'."),
                _q("A higher-order function is one that…",
                   ["is very long", "takes or returns another function",
                    "has many parameters", "returns void"], 1,
                   "map, filter and reduce — next week — are all higher-order."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w5-closures", "Functions that build functions",
            "Returning a function, and the variables it remembers.",
            """
A function can **return** a function, just as it can return a number. That
sounds like a curiosity; it's actually one of the most useful tools you have.

```ts
function multiplier(factor: number): (x: number) => number {
  return (x: number): number => x * factor;
}

const double = multiplier(2);
const triple = multiplier(3);
console.log(double(10));   // 20
console.log(triple(10));   // 30
```

Read the return type `(x: number) => number` as *"…and it hands back a function
from number to number."*

**The remembering part.** `multiplier(2)` finishes and returns. Yet the little
function it produced still knows that `factor` was 2 — forever. A function
bundled together with the variables it captured from the scope around it is
called a **closure**.

```ts
function counter(): () => number {
  let n = 0;                       // lives on, privately
  return (): number => {
    n = n + 1;
    return n;
  };
}

const next = counter();
console.log(next());   // 1
console.log(next());   // 2
console.log(next());   // 3
```

`n` is not a global and nothing outside can touch it, but it survives between
calls because the returned function still holds a reference to it. That's a
**private variable** — genuinely private, enforced by scope rather than
convention.

**Each call makes a fresh one.** `counter()` twice gives two independent
counters with two separate `n`s. This is why closures are how you make
*configured* behaviour:

```ts
const withRate = multiplier(1.08);    // a tax function, configured once
```

**Where you'll meet this next.** A closure is what makes `filter` calls like
this work:

```ts
const limit = 10;
items.filter((x) => x > limit);       // the arrow captured `limit`
```

The little function you hand to `filter` reaches out and remembers `limit` from
the surrounding scope. You've been relying on closures without naming them.

> ⚠️ **Common mistakes:** calling the outer function every time
> (`multiplier(2)(10)` works but throws away the configured function); expecting
> two calls to the factory to share state (they don't); and returning the
> *result* rather than the function — `return x * factor;` in the outer body is
> a different program entirely.
""",
            warmup=[
                _q("`const double = multiplier(2); double(10)` gives…",
                   ["2", "10", "20", "a function"], 2, "factor is 2, so 10 * 2."),
                _q("After `const a = counter(); const b = counter(); a(); a(); b();` what did the last call print?",
                   ["3", "2", "1", "0"], 2,
                   "b has its own independent n, so its first call is 1."),
                _q("A closure is…",
                   ["a loop that closes", "a function plus the variables it captured",
                    "a type annotation", "a return statement"], 1,
                   "The function keeps its surrounding variables alive."),
            ],
            exercises=[
                _ex("tscourse-w5-clo-1", "Return a function",
                    "Complete multiplier so it hands back a function that multiplies by factor.",
                    'function multiplier(factor: number): (x: number) => number {\n'
                    '  return (x: number): number => x * factor;\n}\n'
                    'const double = multiplier(2);\nconsole.log(double(10));\n',
                    'return (x: number): number => x * factor;', [("", "20")],
                    hints=["The outer function returns a function, not a number.",
                           "Write return (x: number): number => x * factor;"],
                    difficulty="Medium"),
                _ex("tscourse-w5-clo-2", "Configure it once",
                    "Build a tripling function from the factory, then use it.",
                    _FS + 'function multiplier(factor: number): (x: number) => number {\n'
                    '  return (x: number): number => x * factor;\n}\n'
                    'const triple = multiplier(3);\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(triple(n));\n',
                    'multiplier(3)', [("5", "15"), ("10", "30")],
                    hints=["Call the factory once with the factor you want.",
                           "Write multiplier(3)."]),
                _ex("tscourse-w5-clo-3", "A private counter",
                    "Complete the returned function so each call gives the next number.",
                    'function counter(): () => number {\n  let n = 0;\n'
                    '  return (): number => {\n    n = n + 1;\n    return n;\n  };\n}\n'
                    'const next = counter();\nconsole.log(next());\nconsole.log(next());\nconsole.log(next());\n',
                    'n = n + 1;\n    return n;', [("", "1\n2\n3")],
                    hints=["Advance the captured variable, then hand it back.",
                           "Write n = n + 1; then return n;"],
                    difficulty="Medium"),
                _ex("tscourse-w5-clo-4", "A configured greeter",
                    "Return a function that greets a name with the captured greeting word.",
                    _FS + 'function greeterFor(word: string): (name: string) => string {\n'
                    '  return (name: string): string => `${word}, ${name}!`;\n}\n'
                    'const hello = greeterFor("Hello");\n'
                    'const who = fs.readFileSync(0, "utf8").trim();\nconsole.log(hello(who));\n',
                    '`${word}, ${name}!`', [("Ada", "Hello, Ada!"), ("Bo", "Hello, Bo!")],
                    hints=["The inner function sees both its own parameter and the captured word.",
                           "Write `${word}, ${name}!`."],
                    difficulty="Medium"),
                _ex("tscourse-w5-clo-5", "Two independent counters",
                    "Show that each factory call gets its own state: print a's first two, then b's first.",
                    'function counter(): () => number {\n  let n = 0;\n'
                    '  return (): number => {\n    n = n + 1;\n    return n;\n  };\n}\n'
                    'const a = counter();\nconst b = counter();\n'
                    'console.log(a());\nconsole.log(a());\nconsole.log(b());\n',
                    'const b = counter();', [("", "1\n2\n1")],
                    hints=["b must come from its own call to the factory.",
                           "Write const b = counter();"],
                    difficulty="Medium"),
                _fix("tscourse-w5-clo-fix1", "Fix the factory that forgot to be one",
                     "This should print 20, but the factory returns a number instead of a function. Fix it.",
                     'function multiplier(factor: number): (x: number) => number {\n'
                     '  return factor;\n}\n'
                     'const double = multiplier(2);\nconsole.log(double(10));\n',
                     'function multiplier(factor: number): (x: number) => number {\n'
                     '  return (x: number): number => x * factor;\n}\n'
                     'const double = multiplier(2);\nconsole.log(double(10));\n',
                     [("", "20")],
                     hints=["`double` is supposed to be callable, but it was handed the number 2.",
                            "Return a function: (x: number): number => x * factor."],
                     difficulty="Medium"),
                _fix("tscourse-w5-clo-fix2", "Fix the shared state",
                     "These two counters should be independent — expected 1, 2, 1 — but the second one continues the first. Fix it.",
                     'function counter(): () => number {\n  let n = 0;\n'
                     '  return (): number => {\n    n = n + 1;\n    return n;\n  };\n}\n'
                     'const a = counter();\nconst b = a;\n'
                     'console.log(a());\nconsole.log(a());\nconsole.log(b());\n',
                     'function counter(): () => number {\n  let n = 0;\n'
                     '  return (): number => {\n    n = n + 1;\n    return n;\n  };\n}\n'
                     'const a = counter();\nconst b = counter();\n'
                     'console.log(a());\nconsole.log(a());\nconsole.log(b());\n',
                     [("", "1\n2\n1")],
                     hints=["`const b = a;` points b at the SAME function, so it shares a's captured n.",
                            "Call the factory again to get a fresh one: const b = counter();"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What keeps `factor` alive after `multiplier` has returned?",
                   ["a global variable", "the closure — the returned function captured it",
                    "nothing, it is copied", "the type annotation"], 1,
                   "The returned function holds a reference to the scope it was created in."),
                _q("`(x: number) => number` written as a RETURN type means…",
                   ["the function returns a number", "the function returns another function",
                    "the parameter is a function", "it is a syntax error"], 1,
                   "The whole arrow notation is the type of the returned value."),
                _q("Why is the `n` inside `counter` effectively private?",
                   ["it is const", "nothing outside the closure has a reference to it",
                    "it is annotated private", "it is a global"], 1,
                   "Scope, not convention, enforces it."),
            ],
        ),
        # ---- Lesson 9 --------------------------------------------------
        _lesson(
            "w5-design", "Designing a function",
            "Contract first, trace by hand, extract the duplication.",
            """
You can now *write* functions. This lesson is about *deciding* which functions
to write — the judgement that separates code you can live with from code you
can't.

**1. Write the contract before the body.** A contract is four short answers:

| question | for `shipping` |
|---|---|
| What is it called? | `shipping` |
| What goes in? | `weight: number` — kilograms, never negative |
| What comes out? | `number` — the cost in dollars |
| What must be true? | the caller passes kilograms, not grams |

Write the signature first and the body almost writes itself:

```ts
function shipping(weight: number): number {
  return 0;   // stub — fill this in once the shape is agreed
}
```

A stub that compiles is a real milestone: the rest of the program can already
call it while you work out the arithmetic.

**2. Trace a call by hand.** When something is wrong, don't guess — substitute.

```ts
function twice(x: number): number { return x * 2; }
function inc(x: number): number { return x + 1; }
console.log(inc(twice(5)));
```

```
inc(twice(5))
inc(10)          // twice(5) returned 10 — the call is REPLACED by its value
11
```

Innermost call first, replace it with what it returned, repeat. Nearly every
debugging session you will ever have is this, done patiently.

**3. Extract on the third repetition.** Two similar lines are a coincidence;
three are a pattern. When you copy a line and edit one number, that number is a
parameter and the line is a function:

```ts
console.log((10 * 1.2).toFixed(2));    // copy…
console.log((25 * 1.2).toFixed(2));    // …paste…
console.log((99 * 1.2).toFixed(2));    // …paste again  ← stop.

function withVat(amount: number): string {
  return (amount * 1.2).toFixed(2);    // the rate now lives in ONE place
}
```

**4. One function, one job.** If the name needs an "and" — `validateAndSave` —
it is two functions wearing one coat. Small named pieces compose; big ones
don't.

**5. Order guards from most specific to least.** Guards are checked top to
bottom and the first match wins, so a broad condition placed first swallows the
narrow ones underneath it. This is the most common logic bug in guarded code.

**6. Choose test cases deliberately.** Before running anything, pick a typical
value, a boundary value (exactly the limit), and a hostile value (zero,
negative, empty). A function that survives those three usually survives the
rest.

> ⚠️ **Common mistakes:** writing the body before deciding what it returns;
> ordering guards widest-first; and a helper that both computes *and* prints,
> which makes it unusable anywhere that has to stay quiet.
""",
            warmup=[
                _q("Trace `inc(twice(5))` where `twice` doubles and `inc` adds 1:",
                   ["11", "12", "10", "6"], 0,
                   "twice(5) is 10; that call is replaced by 10; inc(10) is 11."),
                _q("You copy a line and change one number in it. That number should become…",
                   ["a global", "a parameter", "a comment", "a string"], 1,
                   "The thing that varies between the copies is exactly the input."),
                _q("With `if (s >= 50) return 'pass';` placed ABOVE `if (s >= 80) return 'distinction';`, `grade(90)` is…",
                   ["distinction", "pass", "fail", "undefined"], 1,
                   "The broad guard matched first and returned, so the narrow one never ran."),
                _q("A helper that both computes a total and prints it is hard to…",
                   ["name", "reuse anywhere that must not print", "annotate", "call twice"], 1,
                   "Printing is a side effect, and it decides for every caller."),
            ],
            exercises=[
                _ex("tscourse-w5-des-1", "Fill in the contract",
                    "The body is written. Declare the two parameters it needs: an amount and a rate, both numbers.",
                    'function feeFor(amount: number, rate: number): number {\n'
                    '  return amount * rate;\n}\n'
                    'console.log(feeFor(200, 0.015).toFixed(2));\n',
                    'amount: number, rate: number', [("", "3.00")],
                    hints=["Read the body: which names does it use?",
                           "Two parameters, comma-separated, each annotated : number."]),
                _ex("tscourse-w5-des-2", "Extract the repeated line",
                    "Three lines each multiplied by 1.2 and formatted became one helper. Fill in its body.",
                    'function withVat(amount: number): string {\n'
                    '  return (amount * 1.2).toFixed(2);\n}\n'
                    'console.log(withVat(10));\n'
                    'console.log(withVat(25));\n'
                    'console.log(withVat(99));\n',
                    'return (amount * 1.2).toFixed(2);',
                    [("", "12.00\n30.00\n118.80")],
                    hints=["The part that never changed was `* 1.2` followed by `.toFixed(2)`.",
                           "The part that did change is now the parameter `amount`."]),
                _ex("tscourse-w5-des-3", "Guard the upper bound",
                    "`clamp` pulls any value back inside low..high. The low guard is written; add the high one.",
                    'function clamp(value: number, low: number, high: number): number {\n'
                    '  if (value < low) return low;\n'
                    '  if (value > high) return high;\n'
                    '  return value;\n}\n'
                    'console.log(clamp(15, 0, 10));\n'
                    'console.log(clamp(-4, 0, 10));\n'
                    'console.log(clamp(7, 0, 10));\n',
                    'if (value > high) return high;', [("", "10\n0\n7")],
                    hints=["Mirror the line above it, flipping the comparison.",
                           "Write if (value > high) return high;"],
                    difficulty="Easy"),
                _ex("tscourse-w5-des-4", "Guards in the right order",
                    "Shipping is free at zero weight, a flat $3 below 1 kg, and $3 plus $2 for every whole extra kilogram beyond that. Fill in the last case.",
                    _FS +
                    'function shipping(weight: number): number {\n'
                    '  if (weight <= 0) return 0;\n'
                    '  if (weight < 1) return 3;\n'
                    '  return 3 + Math.ceil(weight - 1) * 2;\n}\n'
                    'const w = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(shipping(w));\n',
                    'return 3 + Math.ceil(weight - 1) * 2;',
                    [("0", "0"), ("0.5", "3"), ("1", "3"), ("2.5", "7"), ("4", "9")],
                    hints=["Anything from 1 kg up pays the base 3 plus 2 per rounded-up extra kilo.",
                           "Math.ceil(weight - 1) counts those extra kilos.",
                           "Write return 3 + Math.ceil(weight - 1) * 2;"],
                    difficulty="Medium"),
                _ex("tscourse-w5-des-5", "One job each",
                    "`badge` should not know how initials are built — it should call the helper. Fill in that call.",
                    'function initials(first: string, last: string): string {\n'
                    '  return `${first[0]}.${last[0]}.`;\n}\n'
                    'function badge(first: string, last: string, role: string): string {\n'
                    '  return `${initials(first, last)} ${role}`;\n}\n'
                    'console.log(badge("Ada", "Lovelace", "engineer"));\n'
                    'console.log(badge("Grace", "Hopper", "admiral"));\n',
                    'initials(first, last)',
                    [("", "A.L. engineer\nG.H. admiral")],
                    hints=["Pass badge's own two name parameters straight through.",
                           "Write initials(first, last) inside the template literal."]),
                _fix("tscourse-w5-des-fix1", "Fix the guard order",
                     "This should print distinction, pass, fail — but the broad guard is swallowing the narrow one. Reorder it.",
                     'function grade(score: number): string {\n'
                     '  if (score >= 50) return "pass";\n'
                     '  if (score >= 80) return "distinction";\n'
                     '  return "fail";\n}\n'
                     'console.log(grade(90));\n'
                     'console.log(grade(60));\n'
                     'console.log(grade(20));\n',
                     'function grade(score: number): string {\n'
                     '  if (score >= 80) return "distinction";\n'
                     '  if (score >= 50) return "pass";\n'
                     '  return "fail";\n}\n'
                     'console.log(grade(90));\n'
                     'console.log(grade(60));\n'
                     'console.log(grade(20));\n',
                     [("", "distinction\npass\nfail")],
                     hints=["90 is also >= 50, so the first guard returns before the second is ever read.",
                            "Put the most specific test first."],
                     difficulty="Medium"),
                _fix("tscourse-w5-des-fix2", "Fix the leaky helper",
                     "`withFee` adds a flat $2 fee, so both lines should print 12. The second is wrong because the helper accumulates into an outer variable. Make it pure.",
                     'let running = 0;\n'
                     'function withFee(amount: number): number {\n'
                     '  running = running + amount;\n'
                     '  return running + 2;\n}\n'
                     'console.log(withFee(10));\n'
                     'console.log(withFee(10));\n',
                     'function withFee(amount: number): number {\n'
                     '  return amount + 2;\n}\n'
                     'console.log(withFee(10));\n'
                     'console.log(withFee(10));\n',
                     [("", "12\n12")],
                     hints=["The second call remembers the first one — that is a side effect.",
                            "A pure version needs no outer variable at all: return amount + 2."],
                     difficulty="Medium"),
                _fix("tscourse-w5-des-fix3", "Fix the helper that prints",
                     "`describe` logs instead of returning, so the caller cannot build a sentence from it. It should print `Rating: warm`.",
                     'function describe(temp: number): void {\n'
                     '  if (temp > 25) console.log("hot");\n'
                     '  else if (temp > 15) console.log("warm");\n'
                     '  else console.log("cold");\n}\n'
                     'console.log(`Rating: ${describe(20)}`);\n',
                     'function describe(temp: number): string {\n'
                     '  if (temp > 25) return "hot";\n'
                     '  if (temp > 15) return "warm";\n'
                     '  return "cold";\n}\n'
                     'console.log(`Rating: ${describe(20)}`);\n',
                     [("", "Rating: warm")],
                     hints=["A void helper hands back undefined, which is what the template ends up showing.",
                            "Return each word instead of logging it, and change the return type to string.",
                            "With returns you no longer need else — each return already leaves the function."],
                     difficulty="Medium"),
                _ch("tscourse-w5-des-ch1", "Build a three-piece toolkit", "Medium",
                    "Write three helpers. `pct(part, whole)` returns the percentage and 0 when whole is 0; `round1(x)` returns it as a string with one decimal; `bar(value)` returns one `#` per full 10 percent, rounded.",
                    _FS +
                    'function pct(part: number, whole: number): number {\n'
                    '  if (whole === 0) return 0;\n'
                    '  return (part / whole) * 100;\n}\n'
                    'function round1(x: number): string {\n'
                    '  return x.toFixed(1);\n}\n'
                    'function bar(value: number): string {\n'
                    '  return "#".repeat(Math.round(value / 10));\n}\n'
                    'const done = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'const total = 40;\n'
                    'const p = pct(done, total);\n'
                    'console.log(`${round1(p)}%`);\n'
                    'console.log(bar(p));\n',
                    'function pct(part: number, whole: number): number {\n'
                    '  if (whole === 0) return 0;\n'
                    '  return (part / whole) * 100;\n}\n'
                    'function round1(x: number): string {\n'
                    '  return x.toFixed(1);\n}\n'
                    'function bar(value: number): string {\n'
                    '  return "#".repeat(Math.round(value / 10));\n}',
                    [("10", "25.0%\n###"), ("20", "50.0%\n#####"), ("40", "100.0%\n##########")],
                    hints=["Write the three signatures first, each returning a stub, then fill the bodies one at a time.",
                           "pct needs a guard: reject whole === 0 before dividing.",
                           "round1 is a one-liner over toFixed(1).",
                           'bar uses "#".repeat(n) where n is Math.round(value / 10).']),
            ],
            quiz=[
                _q("What should you decide before writing a function's body?",
                   ["its length", "its name, inputs, output and preconditions",
                    "which file it lives in", "whether it is an arrow function"], 1,
                   "That is the contract — everything else follows from it."),
                _q("Tracing `inc(twice(5))`, the first step is to…",
                   ["run inc", "replace twice(5) with 10", "print both", "read right to left"], 1,
                   "Innermost call first: substitute its return value, then continue."),
                _q("Guards should be ordered…",
                   ["alphabetically", "most specific first", "widest first", "any order works"], 1,
                   "The first matching guard returns, so a wide one placed first hides the rest."),
                _q("A name like `validateAndSave` hints that…",
                   ["it is too short", "it is doing two jobs and wants splitting",
                    "it needs a return type", "it should be an arrow function"], 1,
                   "The 'and' is the seam where the function wants to be cut in two."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #5 — refactored into helpers",
        """
Budget Buddy has grown into a script. This week you **rebuild it out of named
functions** — which is what a working codebase actually looks like.

Read a **quantity** and print a receipt for coffees at **$3.25** each, with 8%
tax, and a budget of $20:

```
Coffee x4
Subtotal:  $13.00
Tax (8%):  $1.04
Total:     $14.04
Remaining: $5.96
Verdict:   within budget
```

Build it from four helpers — no free-floating arithmetic in the printing code:

- `subtotal(price, qty)` → the pre-tax amount
- `tax(amount, rate = 0.08)` → just the tax portion, with a default rate
- `money(amount)` → a string like `$13.00`
- `verdict(remaining)` → `within budget` when remaining is 0 or more,
  `OVER BUDGET` otherwise

Each helper is **pure** — it returns a value and prints nothing. All the
`console.log` calls live at the bottom.
""",
        _ch("tscourse-w5-capstone", "Budget Buddy #5", "Medium",
            "Write the four helpers, then print the six lines using them.",
            _FS + 'function subtotal(price: number, qty: number): number {\n'
            '  return price * qty;\n}\n'
            'function tax(amount: number, rate: number = 0.08): number {\n'
            '  return amount * rate;\n}\n'
            'function money(amount: number): string {\n'
            '  return `$${amount.toFixed(2)}`;\n}\n'
            'function verdict(remaining: number): string {\n'
            '  if (remaining < 0) return "OVER BUDGET";\n'
            '  return "within budget";\n}\n'
            'const qty = Number(fs.readFileSync(0, "utf8").trim());\n'
            'const price = 3.25;\n'
            'const budget = 20;\n'
            'const sub = subtotal(price, qty);\n'
            'const t = tax(sub);\n'
            'const total = sub + t;\n'
            'console.log(`Coffee x${qty}`);\n'
            'console.log(`Subtotal:  ${money(sub)}`);\n'
            'console.log(`Tax (8%):  ${money(t)}`);\n'
            'console.log(`Total:     ${money(total)}`);\n'
            'console.log(`Remaining: ${money(budget - total)}`);\n'
            'console.log(`Verdict:   ${verdict(budget - total)}`);\n',
            'function subtotal(price: number, qty: number): number {\n'
            '  return price * qty;\n}\n'
            'function tax(amount: number, rate: number = 0.08): number {\n'
            '  return amount * rate;\n}\n'
            'function money(amount: number): string {\n'
            '  return `$${amount.toFixed(2)}`;\n}\n'
            'function verdict(remaining: number): string {\n'
            '  if (remaining < 0) return "OVER BUDGET";\n'
            '  return "within budget";\n}',
            [("4", "Coffee x4\nSubtotal:  $13.00\nTax (8%):  $1.04\nTotal:     $14.04\nRemaining: $5.96\nVerdict:   within budget"),
             ("10", "Coffee x10\nSubtotal:  $32.50\nTax (8%):  $2.60\nTotal:     $35.10\nRemaining: $-15.10\nVerdict:   OVER BUDGET"),
             ("1", "Coffee x1\nSubtotal:  $3.25\nTax (8%):  $0.26\nTotal:     $3.51\nRemaining: $16.49\nVerdict:   within budget")],
            hints=["Write the four helpers first; the printing code at the bottom already calls them.",
                   "tax returns only the tax portion — amount * rate — not the taxed total.",
                   "money returns a string: `$${amount.toFixed(2)}`.",
                   "verdict is a guard clause: reject the negative case, then return the happy answer.",
                   "Give tax's rate parameter a default of 0.08 so the call site can omit it."]),
        example_io="Coffee x4\nSubtotal:  $13.00\nTax (8%):  $1.04\nTotal:     $14.04\nRemaining: $5.96\nVerdict:   within budget",
        rubric=["Four named helpers, each doing one thing",
                "Every helper returns a value; none of them prints",
                "tax has a defaulted rate parameter",
                "verdict uses a guard clause rather than nested if/else",
                "All printing happens in one place at the bottom"],
        stretch=_ch("tscourse-w5-capstone-stretch", "Budget Buddy #5 (stretch)", "Medium",
                    "Add a `line(label, value)` helper that formats any row as a label padded to 11 characters followed by the value, and use it for all four money rows — so changing the column width means editing one function.",
                    _FS + 'function subtotal(price: number, qty: number): number {\n'
                    '  return price * qty;\n}\n'
                    'function tax(amount: number, rate: number = 0.08): number {\n'
                    '  return amount * rate;\n}\n'
                    'function money(amount: number): string {\n'
                    '  return `$${amount.toFixed(2)}`;\n}\n'
                    'function verdict(remaining: number): string {\n'
                    '  if (remaining < 0) return "OVER BUDGET";\n'
                    '  return "within budget";\n}\n'
                    'function line(label: string, value: string): string {\n'
                    '  return label.padEnd(11) + value;\n}\n'
                    'const qty = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'const price = 3.25;\n'
                    'const budget = 20;\n'
                    'const sub = subtotal(price, qty);\n'
                    'const t = tax(sub);\n'
                    'const total = sub + t;\n'
                    'console.log(`Coffee x${qty}`);\n'
                    'console.log(line("Subtotal:", money(sub)));\n'
                    'console.log(line("Tax (8%):", money(t)));\n'
                    'console.log(line("Total:", money(total)));\n'
                    'console.log(line("Remaining:", money(budget - total)));\n'
                    'console.log(line("Verdict:", verdict(budget - total)));\n',
                    'function line(label: string, value: string): string {\n'
                    '  return label.padEnd(11) + value;\n}',
                    [("4", "Coffee x4\nSubtotal:  $13.00\nTax (8%):  $1.04\nTotal:     $14.04\nRemaining: $5.96\nVerdict:   within budget")],
                    hints=["padEnd(11) makes every label occupy the same width.",
                           "Write return label.padEnd(11) + value;"]),
    ),
))

# --- Week 6 ---------------------------------------------------------------
_NUMS = _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
_WORDS = _FS + 'const words = fs.readFileSync(0, "utf8").trim().split(" ");\n'

_WEEKS.append(_week(
    6, 2, _M2,
    "Arrays",
    "Hold lists of values, walk them, reshape them with map/filter/find, and sort them correctly.",
    """
A variable holds one value. An **array** holds an ordered list of them, reached
by position. Nearly all real data is a list — rows in a report, items in a
basket, results from a search — so this is the week your programs start looking
like real programs.

Two halves to it:

1. **The manual half** — creating, indexing, looping, accumulating. This is last
   week's accumulator pattern applied to lists, and it never stops being useful.
2. **The method half** — `map`, `filter`, `find`, `some`, `every`, `sort`. Each
   takes a small function (exactly what you learned to pass in week 5) and
   describes an operation on the *whole* list in one line.

The methods are not just shorthand. `nums.filter((x) => x > 10)` says *what you
want*; the loop that does the same thing says *how to get it*, and you have to
read all five lines to find out. Learn both — you need the loop when the
operation doesn't fit a method, and the method every other time.

⏱️ Budget about **eight and a half hours**, spread over several sittings.
""",
    objectives=[
        "Create arrays, index them, and reach the last element safely",
        "Turn a line of input into an array with split, and back with join",
        "Walk an array with for...of and an indexed for, accumulating a result",
        "Add and remove elements, and tell mutation apart from making a new array",
        "Transform every element with map",
        "Select elements with filter, find, findIndex, some and every",
        "Sort numbers and strings correctly with a comparator, without wrecking the original",
        "Chain split, map, filter, sort, slice and join into one readable pipeline",
        "Choose the order of a chain, and copy an array before sorting it",
    ],
    why="Every list you will ever process — search results, table rows, log lines, basket items — is an array. The methods in this week are the vocabulary of day-to-day data work.",
    est_minutes=510,
    glossary=[
        _gloss("array", "An ordered list of values: [3, 5, 7]."),
        _gloss("element", "One value inside an array."),
        _gloss("index", "An element's position, from 0."),
        _gloss(".length", "How many elements the array holds."),
        _gloss(".split(sep)", "Cuts a string into an array of pieces."),
        _gloss(".join(sep)", "Glues an array into one string, with sep between."),
        _gloss(".push(x)", "Adds x to the END, changing the array in place."),
        _gloss(".pop()", "Removes and returns the LAST element."),
        _gloss(".shift() / .unshift(x)", "Remove from / add to the FRONT."),
        _gloss("mutation", "Changing an array in place, so every reference to it sees the change."),
        _gloss("spread (...)", "Copies elements out: [...a] is a fresh copy of a."),
        _gloss(".map(f)", "A NEW array with f applied to every element. Same length."),
        _gloss(".filter(f)", "A NEW array of only the elements passing f. Same or shorter."),
        _gloss(".find(f)", "The FIRST element passing f, or undefined."),
        _gloss(".findIndex(f)", "The index of the first element passing f, or -1."),
        _gloss(".some(f) / .every(f)", "Does any / does every element pass f?"),
        _gloss("callback", "The small function you hand to map, filter, sort…"),
        _gloss("predicate", "A callback returning true/false, used to test elements."),
        _gloss("comparator", "The (a, b) function sort uses to order two elements."),
        _gloss("chain", "Calling one array method on the result of the last, because each returns a new array."),
        _gloss("pipeline", "A chain read top to bottom, each stage transforming the whole list once."),
        _gloss("slice", "Takes a section of an array — and with no arguments, copies the whole thing."),
        _gloss("in-place", "A method that rearranges the array it was called on. sort and reverse are the two."),
    ],
    cheatsheet="""
```ts
// ---- create & index --------------------------------------------------
const a = [3, 5, 7];
a[0]                 // 3      first
a.length             // 3
a[a.length - 1]      // 7      last
a.at(-1)             // 7      last, more readably
a[99]                // undefined  (no error)

// ---- input & output --------------------------------------------------
"1 2 3".split(" ")            // ["1","2","3"]   (strings!)
"1 2 3".split(" ").map(Number) // [1,2,3]
"abc".split("")               // ["a","b","c"]
a.join(" ")                   // "3 5 7"
a.join(", ")                  // "3, 5, 7"

// ---- walk -------------------------------------------------------------
for (const x of a) { ... }              // values
for (let i = 0; i < a.length; i++) { }  // positions

// ---- change in place (MUTATES) ---------------------------------------
a.push(9);      // add to end        a is now [3,5,7,9]
a.pop();        // remove from end   returns 9
a.unshift(1);   // add to front
a.shift();      // remove from front
a.includes(5)   // true
a.indexOf(5)    // 1   (or -1)

// ---- make a NEW array (leaves the original alone) --------------------
[...a]                       // a copy
a.slice(1, 3)                // elements 1 and 2
a.map((x) => x * 2)          // [6,10,14]
a.filter((x) => x > 4)       // [5,7]
a.concat([8, 9])             // a with more on the end

// ---- search ------------------------------------------------------------
a.find((x) => x > 4)         // 5      the element
a.findIndex((x) => x > 4)    // 1      the position
a.some((x) => x > 6)         // true   any?
a.every((x) => x > 0)        // true   all?

// ---- sort (MUTATES — copy first if you care) --------------------------
[...a].sort((x, y) => x - y)   // ascending numbers
[...a].sort((x, y) => y - x)   // descending numbers
[...names].sort()               // strings, alphabetical
[10, 9, 1].sort()               // ⚠️ [1, 10, 9] — sorts as TEXT
```
""",
    self_check=[
        "Can you read a line of numbers into an array and print the last one?",
        "Can you sum an array with a loop, and say why the accumulator sits outside it?",
        "Can you say what map returns when the array has 5 elements?",
        "Can you pick the right one of find, filter, some and includes for a given question?",
        "Can you sort numbers descending, without changing the original array?",
        "Can you explain why [10, 9, 1].sort() gives [1, 10, 9]?",
        "Can you turn a line of raw input into a ranked report in one chain?",
        "Can you say why sort needs a slice() in front of it, and when filter should come before map?",
    ],
    review=[
        _q("The first element of an array is at index…", ["1", "0", "-1", "any"], 1,
           "Arrays are zero-indexed, so the last is at length - 1."),
        _q('`"3 5".split(" ")` gives…',
           ["35", '["3","5"]', '[3,5]', "an error"], 1,
           'split always produces STRINGS — hence the .map(Number) that usually follows.'),
        _q("`[1,2,3].map((x) => x * 2)` has how many elements?",
           ["1", "2", "3", "6"], 2, "map never changes the length — one output per input."),
        _q("`[1,2,3].filter((x) => x > 1).length` is…", ["1", "2", "3", "0"], 1,
           "It keeps 2 and 3."),
        _q("Which returns the ELEMENT rather than a list?",
           ["filter", "map", "find", "some"], 2,
           "find gives the first match itself, or undefined."),
        _q("`[1,2,3].some((x) => x > 2)` is…", ["true", "false", "3", "[3]"], 0,
           "At least one element passes."),
        _q("`a.push(4)` does what to `a`?",
           ["returns a new array", "changes a in place", "nothing", "sorts it"], 1,
           "push mutates. map/filter/slice are the ones that return new arrays."),
        _q("`[10, 9, 1].sort()` gives…",
           ["[1, 9, 10]", "[1, 10, 9]", "[10, 9, 1]", "an error"], 1,
           'With no comparator, sort compares as text: "1" < "10" < "9".'),
        _q("Sorting numbers ascending needs the comparator…",
           ["(a, b) => a > b", "(a, b) => a - b", "(a, b) => b - a", "none"], 1,
           "A negative result means a comes first."),
        _q("To sort without disturbing the original you…",
           ["cannot", "copy first: [...a].sort(...)", "use map", "use filter"], 1,
           "sort mutates the array it is called on."),
        _q("Array methods can be chained because…",
           ["they mutate in place", "each hands back a new array", "TypeScript rewrites them", "they are lazy"], 1,
           "map, filter and slice all return fresh arrays."),
        _q("`nums.filter((n) => n > 0);` on a line of its own changes `nums`…",
           ["to the positives", "not at all — the result was discarded", "to an empty array", "to a copy"], 1,
           "You must keep what a non-mutating method returns."),
        _q("Which pair of methods rearranges the original array?",
           ["map and filter", "sort and reverse", "slice and join", "split and map"], 1,
           "Copy with slice() first if anyone else is holding that array."),
    ],
    milestone="Budget Buddy can now crunch a whole month of expenses at once — totals, extremes, averages and a ranked list.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w6-basics", "Creating & indexing",
            "Making an array and reaching into it.",
            """
Write an array as a comma-separated list in square brackets:

```ts
const names = ["Ada", "Bo", "Cy"];
const nums = [3, 5, 7];
const empty: number[] = [];
```

That `number[]` annotation reads as *"an array of numbers"*. You need it on an
empty array, because there is nothing there for TypeScript to infer from.

**Indexing** works exactly like string indexing — positions start at **0**:

```
 "Ada"  "Bo"  "Cy"
   0      1     2
```

```ts
names[0]                 // "Ada"
names.length             // 3
names[names.length - 1]  // "Cy"   the last one
names.at(-1)             // "Cy"   the same, said better
names[99]                // undefined  — no error, just nothing
```

The `length - 1` for the last element is the same off-by-one you met in week 2,
and it catches people just as often here.

**Out of range is silent.** `names[99]` doesn't throw; it hands back
`undefined`, which then flows onward and breaks something far away. When an
index might be out of range, check it.

**Arrays can hold anything**, including other arrays:

```ts
const grid = [[1, 2], [3, 4]];
grid[1][0]     // 3   — row 1, then column 0
```

Read `grid[1][0]` left to right: take element 1 (`[3, 4]`), then element 0 of
that (`3`).

> ⚠️ **Common mistakes:** thinking `a[1]` is the first element; using
> `a[a.length]` for the last; and calling `a.length()` — like strings, it is a
> property, with no parentheses.
""",
            warmup=[
                _q("`const a = [10,20,30]; console.log(a[1]);` prints…",
                   ["10", "20", "30", "1"], 1, "Index 1 is the second element."),
                _q("`[10,20,30].length` is…", ["2", "3", "30", "undefined"], 1,
                   "Three elements."),
                _q("`[10,20,30][3]` is…", ["30", "0", "undefined", "an error"], 2,
                   "Valid indices are 0, 1, 2."),
                _q("`[[1,2],[3,4]][0][1]` is…", ["1", "2", "3", "4"], 1,
                   "Row 0 is [1,2]; its element 1 is 2."),
            ],
            exercises=[
                _ex("tscourse-w6-b-1", "First element",
                    "Print the first name in the list.",
                    'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[0]);\n',
                    'names[0]', [("", "Ada")],
                    hints=["Positions start at 0."]),
                _ex("tscourse-w6-b-2", "How many",
                    "Print how many names there are.",
                    'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names.length);\n',
                    'names.length', [("", "3")],
                    hints=["length is a property — no parentheses."]),
                _ex("tscourse-w6-b-3", "Last element",
                    "Print the last name, computed from the length (not typed as 2).",
                    'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[names.length - 1]);\n',
                    'names[names.length - 1]', [("", "Cy")],
                    hints=["The last index is one less than the length.",
                           "Write names[names.length - 1]."]),
                _ex("tscourse-w6-b-4", "An annotated empty array",
                    "Annotate the empty array as an array of numbers.",
                    'const scores: number[] = [];\nconsole.log(scores.length);\n',
                    'number[]', [("", "0")],
                    hints=["An array of numbers is written number[].",
                           "Write const scores: number[] = [];"]),
                _ex("tscourse-w6-b-5", "Into the grid",
                    "Print the value in row 1, column 0 (it should be 3).",
                    'const grid = [[1, 2], [3, 4]];\nconsole.log(grid[1][0]);\n',
                    'grid[1][0]', [("", "3")],
                    hints=["Index the row first, then the column.",
                           "Write grid[1][0]."]),
                _fix("tscourse-w6-b-fix1", "Fix the index",
                     "This should print the FIRST name but prints the second. Fix it.",
                     'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[1]);\n',
                     'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[0]);\n',
                     [("", "Ada")],
                     hints=["Index 1 is the second element.",
                            "The first is index 0."]),
                _fix("tscourse-w6-b-fix2", "Fix the off-by-one",
                     "This should print the last name but prints nothing. Fix it.",
                     'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[names.length]);\n',
                     'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[names.length - 1]);\n',
                     [("", "Cy")],
                     hints=["A 3-element array has indices 0, 1, 2 — never 3.",
                            "Subtract one from the length."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("For an array of length n, the valid indices are…",
                   ["1..n", "0..n", "0..n-1", "0..n+1"], 2, "Zero-based."),
                _q("Why annotate `const xs: number[] = []`?",
                   ["It is required", "There is nothing in it to infer a type from",
                    "It makes it faster", "To make it readonly"], 1,
                   "An empty literal gives the compiler no evidence."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w6-input", "split & join",
            "Turning a line of text into an array, and back again.",
            """
Input arrives as one string. `split` cuts it into an array:

```ts
"1 2 3".split(" ")        // ["1", "2", "3"]
"a,b,c".split(",")        // ["a", "b", "c"]
"abc".split("")           // ["a", "b", "c"]   — every character
```

**Everything split produces is a string**, even when it looks like a number.
`["1","2","3"]` is three strings. To compute with them, convert:

```ts
"1 2 3".split(" ").map(Number)     // [1, 2, 3]
```

`.map(Number)` runs `Number` on each piece. You'll meet `map` properly in
lesson 5 — for now, take this as the standard opening line for a numeric
program:

```ts
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);
```

Read it right to left: read the input, trim it, cut at spaces, convert each
piece.

**`join` is the mirror image**, gluing an array into one string:

```ts
[3, 5, 7].join(" ")      // "3 5 7"
[3, 5, 7].join(", ")     // "3, 5, 7"
[3, 5, 7].join("")       // "357"
["a"].join(", ")         // "a"        — no trailing separator
[].join(", ")            // ""
```

`join` is how you print a list on one line, and it never leaves a dangling
separator at the end — which a loop building `out += x + ", "` always does.

**Why trim first.** Without `.trim()`, `"1 2 3\\n".split(" ")` gives
`["1", "2", "3\\n"]`, and that last entry converts to a number just fine but
prints with a stray newline. Trim, then split.

> ⚠️ **Common mistakes:** forgetting `.map(Number)` and then adding strings
> (`"1" + "2"` is `"12"`); splitting on `""` when you meant `" "`; and building
> output with `+=` and a separator instead of using `join`.
""",
            warmup=[
                _q('`"a b".split(" ")` gives…',
                   ['"ab"', '["a","b"]', '["a b"]', '["a"," ","b"]'], 1,
                   "Two pieces, with the separator removed."),
                _q('`"1 2".split(" ")[0] + 1` gives…',
                   ["2", '"11"', "11", "an error"], 1,
                   'The piece is the STRING "1", so + joins.'),
                _q('`[1,2,3].join("-")` gives…',
                   ['"1-2-3"', '"123"', "[1,2,3]", '"1-2-3-"'], 0,
                   "Separators go between, never at the end."),
                _q('`"abc".split("")` gives…',
                   ['["abc"]', '["a","b","c"]', '"abc"', "[]"], 1,
                   "An empty separator splits between every character."),
            ],
            exercises=[
                _ex("tscourse-w6-in-1", "Read the numbers",
                    "Read the space-separated numbers into an array and print the first one.",
                    _NUMS + 'console.log(nums[0]);\n',
                    '.split(" ").map(Number)',
                    [("3 5 7", "3"), ("9 1", "9")],
                    hints=["Cut at spaces, then convert each piece.",
                           'Chain .split(" ").map(Number).']),
                _ex("tscourse-w6-in-2", "How many words",
                    "Print how many space-separated words the input has.",
                    _WORDS + 'console.log(words.length);\n',
                    'words.length', [("a b c d", "4"), ("hi", "1")],
                    hints=["Split first, then take the length."]),
                _ex("tscourse-w6-in-3", "Join with commas",
                    "Print the words joined by `, `.",
                    _WORDS + 'console.log(words.join(", "));\n',
                    'words.join(", ")', [("a b c", "a, b, c"), ("solo", "solo")],
                    hints=["join puts the separator between elements only.",
                           'Write words.join(", ").']),
                _ex("tscourse-w6-in-4", "Sum two numbers from input",
                    "The input is two numbers. Print their sum.",
                    _NUMS + 'console.log(nums[0] + nums[1]);\n',
                    'nums[0] + nums[1]',
                    [("3 4", "7"), ("10 -2", "8")],
                    hints=["They are already numbers thanks to map(Number).",
                           "Write nums[0] + nums[1]."]),
                _ex("tscourse-w6-in-5", "Letters of a word",
                    "Split the input into individual characters and print them space-separated.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.split("").join(" "));\n',
                    's.split("").join(" ")',
                    [("abc", "a b c"), ("hi", "h i")],
                    hints=["An empty separator splits every character apart.",
                           'Write s.split("").join(" ").'],
                    difficulty="Medium"),
                _fix("tscourse-w6-in-fix1", "Fix the missing conversion",
                     "This should print the sum 7 for `3 4`, but prints `34`. Fix it.",
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                     'console.log(nums[0] + nums[1]);\n',
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                     'console.log(nums[0] + nums[1]);\n',
                     [("3 4", "7"), ("10 5", "15")],
                     hints=["split gives strings, so + is joining them.",
                            "Add .map(Number) after the split."],
                     difficulty="Medium"),
                _fix("tscourse-w6-in-fix2", "Fix the trailing separator",
                     "This builds the line by hand and leaves a trailing `, `. Rewrite it using join.",
                     _WORDS + 'let out = "";\nfor (const w of words) {\n  out += w + ", ";\n}\nconsole.log(out);\n',
                     _WORDS + 'console.log(words.join(", "));\n',
                     [("a b c", "a, b, c"), ("solo", "solo")],
                     hints=["Every pass appends a separator, including after the last word.",
                            'join solves this exactly: words.join(", ").'],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What type are the pieces from `.split(\" \")`?",
                   ["numbers", "strings", "booleans", "it depends on the input"], 1,
                   "Always strings — convert explicitly."),
                _q("Why is join better than += with a separator?",
                   ["It is faster", "It never leaves a separator dangling at the end",
                    "It sorts", "It removes duplicates"], 1,
                   "Separators go strictly between elements."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w6-loop", "Walking an array",
            "Loops and accumulators over lists.",
            """
Everything you learned about loops in week 4 applies directly. `for...of` hands
you each element:

```ts
let sum = 0;
for (const x of [1, 2, 3, 4]) {
  sum += x;
}
console.log(sum);   // 10
```

| pass | x | sum after |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2 | 3 |
| 3 | 3 | 6 |
| 4 | 4 | 10 |

The accumulator lives **outside** the loop — same rule as always.

**When you need positions**, use the indexed form:

```ts
for (let i = 0; i < nums.length; i++) {
  console.log(`${i}: ${nums[i]}`);
}
```

Use it when you need the index in the output, when you want to compare an
element with its neighbour (`nums[i - 1]`), or when you're walking backwards.

**The four accumulator shapes**, now over arrays:

```ts
let sum = 0;                        for (const x of a) sum += x;
let count = 0;                      for (const x of a) if (x > 10) count++;
let best = a[0];                    for (const x of a) if (x > best) best = x;
let out = "";                       for (const x of a) out += x;
```

**A note on the maximum.** Over an array you can seed `best` with `a[0]` rather
than `-Infinity`, because a real element is right there. That's better: the
answer is guaranteed to be a value that actually appeared. It does assume the
array is non-empty — so if it might be, check first.

**Neighbour comparisons** need indices, and start at 1:

```ts
let rises = 0;
for (let i = 1; i < a.length; i++) {
  if (a[i] > a[i - 1]) rises++;
}
```

Starting at `i = 1` is deliberate: element 0 has no predecessor.

> ⚠️ **Common mistakes:** declaring the accumulator inside the loop; seeding a
> maximum with 0 when the data can be negative; and looking at `a[i - 1]` from
> `i = 0`, which is `a[-1]` — `undefined`.
""",
            warmup=[
                _q("Summing [2,2,2] with a for...of accumulator gives…",
                   ["2", "6", "3", "222"], 1, "2+2+2."),
                _q("Why does a neighbour-comparison loop start at i = 1?",
                   ["style", "element 0 has no previous element", "to skip the first value",
                    "arrays start at 1"], 1,
                   "a[-1] would be undefined."),
                _q("Seeding `best = a[0]` rather than 0 protects against…",
                   ["empty arrays", "all-negative data", "strings", "nothing"], 1,
                   "With 0 as the seed, all-negative data would wrongly report 0."),
            ],
            exercises=[
                _ex("tscourse-w6-lp-1", "Sum the list",
                    "Add every number and print the total.",
                    _NUMS + 'let sum = 0;\nfor (const x of nums) {\n  sum += x;\n}\nconsole.log(sum);\n',
                    'sum += x;', [("1 2 3 4", "10"), ("5", "5")],
                    hints=["Add each element to the running total."]),
                _ex("tscourse-w6-lp-2", "Largest",
                    "Print the largest number, seeding from the first element.",
                    _NUMS + 'let best = nums[0];\nfor (const x of nums) {\n  if (x > best) {\n    best = x;\n  }\n}\nconsole.log(best);\n',
                    'let best = nums[0];',
                    [("3 9 2 7", "9"), ("4", "4"), ("-5 -2 -9", "-2")],
                    hints=["Seed from a value that is actually in the list.",
                           "Write let best = nums[0];"]),
                _ex("tscourse-w6-lp-3", "Count the big ones",
                    "Count how many numbers are greater than 10.",
                    _NUMS + 'let count = 0;\nfor (const x of nums) {\n  if (x > 10) {\n    count++;\n  }\n}\nconsole.log(count);\n',
                    'x > 10', [("5 20 30 1", "2"), ("1 2", "0")],
                    hints=["Strictly greater, so 10 itself does not count."]),
                _ex("tscourse-w6-lp-4", "Numbered list",
                    "Print each element on its own line as `1. value`, numbering from 1.",
                    _WORDS + 'for (let i = 0; i < words.length; i++) {\n  console.log(`${i + 1}. ${words[i]}`);\n}\n',
                    '`${i + 1}. ${words[i]}`',
                    [("a b c", "1. a\n2. b\n3. c"), ("solo", "1. solo")],
                    hints=["The index starts at 0 but the display starts at 1.",
                           "Write `${i + 1}. ${words[i]}`."],
                    difficulty="Medium"),
                _ex("tscourse-w6-lp-5", "Count the rises",
                    "Count how many times a number is greater than the one before it.",
                    _NUMS + 'let rises = 0;\nfor (let i = 1; i < nums.length; i++) {\n  if (nums[i] > nums[i - 1]) {\n    rises++;\n  }\n}\nconsole.log(rises);\n',
                    'nums[i] > nums[i - 1]',
                    [("1 3 2 5", "2"), ("5 4 3", "0"), ("1 2 3", "2")],
                    hints=["Compare each element with its predecessor.",
                           "Write nums[i] > nums[i - 1]."],
                    difficulty="Medium"),
                _ex("tscourse-w6-lp-6", "Average",
                    "Print the average of the numbers to two decimal places.",
                    _NUMS + 'let sum = 0;\nfor (const x of nums) {\n  sum += x;\n}\nconsole.log((sum / nums.length).toFixed(2));\n',
                    '(sum / nums.length).toFixed(2)',
                    [("2 4 6", "4.00"), ("1 2", "1.50")],
                    hints=["Total first, then divide by the count — after the loop.",
                           "Write (sum / nums.length).toFixed(2)."]),
                _fix("tscourse-w6-lp-fix1", "Fix the sum seed",
                     "This total is always one too big. Fix it so `1 2 3` gives 6.",
                     _NUMS + 'let sum = 1;\nfor (const x of nums) {\n  sum += x;\n}\nconsole.log(sum);\n',
                     _NUMS + 'let sum = 0;\nfor (const x of nums) {\n  sum += x;\n}\nconsole.log(sum);\n',
                     [("1 2 3", "6"), ("5", "5")],
                     hints=["What should the sum of an empty list be?",
                            "A running total starts at 0."]),
                _fix("tscourse-w6-lp-fix2", "Fix the maximum seed",
                     "With all-negative input this wrongly prints 0. Fix it so `-5 -2 -9` gives -2.",
                     _NUMS + 'let best = 0;\nfor (const x of nums) {\n  if (x > best) {\n    best = x;\n  }\n}\nconsole.log(best);\n',
                     _NUMS + 'let best = nums[0];\nfor (const x of nums) {\n  if (x > best) {\n    best = x;\n  }\n}\nconsole.log(best);\n',
                     [("-5 -2 -9", "-2"), ("3 9 2", "9")],
                     hints=["0 beats every negative number, so it is never replaced.",
                            "Seed from an element that is actually in the array: nums[0]."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Which loop do you need to print `3: value`?",
                   ["for...of", "an indexed for", "either", "while(true)"], 1,
                   "Only the indexed form gives you the position."),
                _q("An accumulator declared inside the loop body…",
                   ["works fine", "is reset every pass", "is an error", "is faster"], 1,
                   "It never accumulates anything."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w6-mutate", "Growing, shrinking & copying",
            "Changing an array in place — and when not to.",
            """
Four methods change an array **in place**:

```ts
const a = [1, 2, 3];
a.push(4);      // [1,2,3,4]   add to the end
a.pop();        // [1,2,3]     remove from the end, returns 4
a.unshift(0);   // [0,1,2,3]   add to the front
a.shift();      // [1,2,3]     remove from the front, returns 0
```

**`push` is how you build a list in a loop** — the array equivalent of `+=`:

```ts
const doubled: number[] = [];
for (const x of nums) {
  doubled.push(x * 2);
}
```

**`const` does not mean frozen.** This surprises everyone once:

```ts
const a = [1, 2];
a.push(3);      // ✅ fine — the array's CONTENTS changed
a = [9];        // ❌ error — the NAME cannot be repointed
```

`const` fixes what the name points at, not what lives inside it.

**Mutation is shared.** Assigning an array to another name does not copy it —
both names point at the same array:

```ts
const a = [1, 2];
const b = a;
b.push(3);
console.log(a);   // [1, 2, 3]   ⚠️ a changed too
```

That's the single most surprising thing in this lesson, and the cause of bugs
that look like action at a distance. To get a genuine copy, spread it:

```ts
const b = [...a];      // a fresh array with the same elements
b.push(3);             // a is untouched
```

**Searching:**

```ts
a.includes(2)     // true / false
a.indexOf(2)      // 1, or -1 when absent
```

**`slice` takes a piece without mutating** (unlike its confusable neighbour
`splice`, which does mutate):

```ts
a.slice(1, 3)     // elements 1 and 2, as a new array
a.slice(-2)       // the last two
```

Same rules as string `slice` — the end is excluded, negatives count from the
end.

> ⚠️ **Common mistakes:** expecting `const b = a` to copy; expecting `push` to
> return the new array (it returns the new *length*); and mixing up `slice`
> (copies) with `splice` (mutates).
""",
            warmup=[
                _q("`const a = [1,2]; a.push(3);` is…",
                   ["an error, a is const", "fine — contents may change", "a no-op",
                    "a copy"], 1,
                   "const fixes the binding, not the contents."),
                _q("`const a=[1,2]; const b=a; b.push(3); a.length` is…",
                   ["2", "3", "0", "an error"], 1,
                   "b is the same array, so a sees the change too."),
                _q("`[1,2,3].pop()` returns…", ["[1,2]", "3", "1", "3 elements"], 1,
                   "The removed element."),
                _q("Which makes a genuine copy?",
                   ["const b = a", "const b = [...a]", "const b = a.length",
                    "const b = a.push()"], 1,
                   "Spreading builds a fresh array."),
            ],
            exercises=[
                _ex("tscourse-w6-mu-1", "Build with push",
                    "Collect the doubled numbers into a new array, then print them space-separated.",
                    _NUMS + 'const doubled: number[] = [];\nfor (const x of nums) {\n  doubled.push(x * 2);\n}\nconsole.log(doubled.join(" "));\n',
                    'doubled.push(x * 2);',
                    [("1 2 3", "2 4 6"), ("5", "10")],
                    hints=["push adds to the end of the array.",
                           "Write doubled.push(x * 2);"]),
                _ex("tscourse-w6-mu-2", "Add to the end",
                    "Append 99 to the list, then print it.",
                    'const a = [1, 2, 3];\na.push(99);\nconsole.log(a.join(" "));\n',
                    'a.push(99);', [("", "1 2 3 99")],
                    hints=["push puts it at the end."]),
                _ex("tscourse-w6-mu-3", "Copy before changing",
                    "Make `b` a genuine copy so pushing to it leaves `a` alone.",
                    'const a = [1, 2];\nconst b = [...a];\nb.push(3);\nconsole.log(a.length);\nconsole.log(b.length);\n',
                    'const b = [...a];', [("", "2\n3")],
                    hints=["Assignment shares; spreading copies.",
                           "Write const b = [...a];"],
                    difficulty="Medium"),
                _ex("tscourse-w6-mu-4", "Is it in there?",
                    "Print whether the list of words contains `cat`.",
                    _WORDS + 'console.log(words.includes("cat"));\n',
                    'words.includes("cat")',
                    [("dog cat bird", "true"), ("dog bird", "false")],
                    hints=["includes answers true or false.",
                           'Write words.includes("cat").']),
                _ex("tscourse-w6-mu-5", "Drop the first",
                    "Print every element except the first, space-separated, without mutating.",
                    _NUMS + 'console.log(nums.slice(1).join(" "));\n',
                    'nums.slice(1)',
                    [("1 2 3", "2 3"), ("9 8", "8")],
                    hints=["slice from index 1 to the end.",
                           "Write nums.slice(1)."]),
                _ex("tscourse-w6-mu-6", "The last two",
                    "Print the last two elements, space-separated.",
                    _NUMS + 'console.log(nums.slice(-2).join(" "));\n',
                    'nums.slice(-2)',
                    [("1 2 3 4", "3 4"), ("7 8", "7 8")],
                    hints=["A negative start counts from the end.",
                           "Write nums.slice(-2)."]),
                _fix("tscourse-w6-mu-fix1", "Fix the accidental sharing",
                     "This should print `2` then `3`, but prints `3` then `3` — the copy is not a copy. Fix it.",
                     'const a = [1, 2];\nconst b = a;\nb.push(3);\nconsole.log(a.length);\nconsole.log(b.length);\n',
                     'const a = [1, 2];\nconst b = [...a];\nb.push(3);\nconsole.log(a.length);\nconsole.log(b.length);\n',
                     [("", "2\n3")],
                     hints=["`const b = a;` gives the same array a second name.",
                            "Spread to build a fresh one: [...a]."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`const` applied to an array prevents…",
                   ["adding elements", "reassigning the name", "reading elements",
                    "sorting"], 1,
                   "Contents stay mutable."),
                _q("`slice` and `splice` differ in that…",
                   ["nothing", "slice copies, splice mutates", "splice copies, slice mutates",
                    "slice is for strings only"], 1,
                   "A one-letter difference with opposite consequences."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w6-map", "map — transform every element",
            "One output for every input.",
            """
`map` builds a **new** array by running a function on each element:

```ts
const nums = [1, 2, 3];
nums.map((x) => x * 2);          // [2, 4, 6]
nums.map((x) => `#${x}`);        // ["#1", "#2", "#3"]
```

Compare with the loop it replaces:

```ts
const doubled: number[] = [];
for (const x of nums) {
  doubled.push(x * 2);
}
```

Five lines become one, and — more importantly — the one-liner *cannot* get the
bookkeeping wrong. There is no accumulator to seed and no push to forget.

**Three facts about map, in order of how often they matter:**

1. **The length never changes.** Three in, three out, always. If you want fewer,
   you want `filter`.
2. **A new array comes back.** The original is untouched. Ignore the return
   value and you've done nothing.
3. **The callback must return something.** An arrow with braces and no `return`
   gives you an array of `undefined` — the arrow trap from week 5, in its
   natural habitat.

**The index is available** as a second parameter:

```ts
["a", "b"].map((x, i) => `${i}: ${x}`);   // ["0: a", "1: b"]
```

**Chaining** is where it gets pleasant, because each step hands an array to the
next:

```ts
"1 2 3".split(" ").map(Number).map((x) => x * 10).join(", ");   // "10, 20, 30"
```

`.map(Number)` deserves a note: you're passing the `Number` function itself
rather than calling it — exactly the "functions as values" idea from week 5.

> ⚠️ **Common mistakes:** using `map` when you meant `filter` (the length gives
> it away); forgetting `return` inside a braced callback; and discarding the
> result — `nums.map(...)` on its own line changes nothing.
""",
            warmup=[
                _q("`[1,2,3].map((x) => x * 2)` is…",
                   ["[2,4,6]", "[1,2,3]", "12", "6"], 0, "Each element doubled."),
                _q("`[1,2,3].map((x) => x > 1)` has length…",
                   ["1", "2", "3", "0"], 2, "map always preserves the length."),
                _q("`[1,2].map((x) => { x * 2; })` gives…",
                   ["[2,4]", "[undefined, undefined]", "[]", "an error"], 1,
                   "A braced callback needs an explicit return."),
                _q('`["a","b"].map((x, i) => `${i}${x}`)` is…',
                   ['["0a","1b"]', '["a0","b1"]', '["ab"]', '["1a","2b"]'], 0,
                   "The second parameter is the index, counting from 0."),
            ],
            exercises=[
                _ex("tscourse-w6-mp-1", "Double them",
                    "Double every number and print them space-separated.",
                    _NUMS + 'console.log(nums.map((x) => x * 2).join(" "));\n',
                    'nums.map((x) => x * 2)',
                    [("1 2 3", "2 4 6"), ("10", "20")],
                    hints=["map transforms each element.",
                           "Write nums.map((x) => x * 2)."]),
                _ex("tscourse-w6-mp-2", "Shout the words",
                    "Uppercase every word and print them space-separated.",
                    _WORDS + 'console.log(words.map((w) => w.toUpperCase()).join(" "));\n',
                    'w.toUpperCase()',
                    [("a bc", "A BC"), ("hi there", "HI THERE")],
                    hints=["The callback receives one word at a time.",
                           "Return w.toUpperCase()."]),
                _ex("tscourse-w6-mp-3", "Number the words",
                    "Print each word prefixed by its 1-based position, comma-separated: `1:a, 2:b`.",
                    _WORDS + 'console.log(words.map((w, i) => `${i + 1}:${w}`).join(", "));\n',
                    '`${i + 1}:${w}`',
                    [("a b", "1:a, 2:b"), ("solo", "1:solo")],
                    hints=["The second callback parameter is the index, from 0.",
                           "Write `${i + 1}:${w}`."],
                    difficulty="Medium"),
                _ex("tscourse-w6-mp-4", "Lengths",
                    "Print the length of each word, space-separated.",
                    _WORDS + 'console.log(words.map((w) => w.length).join(" "));\n',
                    'w.length',
                    [("a bb ccc", "1 2 3"), ("hello", "5")],
                    hints=["Return each word's length.", "Write w.length."]),
                _ex("tscourse-w6-mp-5", "Chain two steps",
                    "Multiply every number by 10, then print them comma-separated.",
                    _NUMS + 'console.log(nums.map((x) => x * 10).join(", "));\n',
                    '.map((x) => x * 10).join(", ")',
                    [("1 2 3", "10, 20, 30"), ("7", "70")],
                    hints=["map produces an array, which join then turns into text.",
                           'Chain .map((x) => x * 10).join(", ").']),
                _fix("tscourse-w6-mp-fix1", "Fix the missing return",
                     "This should double the numbers but prints a row of `undefined`. Fix it.",
                     _NUMS + 'console.log(nums.map((x) => { x * 2; }).join(" "));\n',
                     _NUMS + 'console.log(nums.map((x) => x * 2).join(" "));\n',
                     [("1 2 3", "2 4 6")],
                     hints=["A braced arrow body returns nothing unless you say so.",
                            "Drop the braces, or add return."],
                     difficulty="Medium"),
                _fix("tscourse-w6-mp-fix2", "Fix the discarded result",
                     "This should print the doubled numbers but prints the originals. Fix it.",
                     _NUMS + 'nums.map((x) => x * 2);\nconsole.log(nums.join(" "));\n',
                     _NUMS + 'const doubled = nums.map((x) => x * 2);\nconsole.log(doubled.join(" "));\n',
                     [("1 2 3", "2 4 6"), ("5", "10")],
                     hints=["map does not change nums — it returns a new array that is being thrown away.",
                            "Store the result and print that."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`a.map(f)` where a has 5 elements returns an array of length…",
                   ["0..5", "exactly 5", "1", "it depends on f"], 1,
                   "map is one-for-one; only filter can shorten."),
                _q("`nums.map(Number)` passes…",
                   ["the result of Number", "the Number function itself", "a string",
                    "nothing"], 1,
                   "No parentheses — a function as a value, as in week 5."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w6-filter", "filter, find & friends",
            "Selecting elements, and asking questions about them.",
            """
`filter` keeps the elements whose callback returns `true`:

```ts
const nums = [1, 2, 3, 4, 5, 6];
nums.filter((x) => x % 2 === 0);    // [2, 4, 6]
nums.filter((x) => x > 100);        // []          — empty, not undefined
```

A callback that returns true/false is called a **predicate**. Everything in this
lesson takes one; they differ only in what they hand back:

| method | question | answer |
|---|---|---|
| `filter` | which ones? | a new **array** (possibly empty) |
| `find` | the first one? | the **element**, or `undefined` |
| `findIndex` | where is the first one? | the **index**, or `-1` |
| `some` | any at all? | `true` / `false` |
| `every` | all of them? | `true` / `false` |

```ts
nums.find((x) => x > 3);        // 4        the element itself
nums.findIndex((x) => x > 3);   // 3        its position
nums.some((x) => x > 5);        // true
nums.every((x) => x > 0);       // true
```

**Choose by what you actually need.** Reaching for `filter(...)[0]` when you
want one element works but scans the whole array and allocates one you throw
away; `find` says what you mean. `filter(...).length > 0` is `some`.

**Two edge cases worth knowing:**

- `find` returns `undefined` when nothing matches — check for it before using
  the result.
- `every` on an **empty** array is `true`. ("Every element passes" is vacuously
  true when there are no elements.) It's a real source of surprise when a filter
  upstream emptied the list.

**Chaining filter and map** is the everyday pattern — narrow, then reshape:

```ts
words.filter((w) => w.length > 3).map((w) => w.toUpperCase()).join(", ")
```

Filter first when you can: there's less left to transform.

> ⚠️ **Common mistakes:** using `map` when you meant `filter`; forgetting `find`
> can be `undefined`; and testing `findIndex(...)` for truthiness, when index 0
> is a real match (the `indexOf` trap from week 2, again).
""",
            warmup=[
                _q("`[1,2,3,4].filter((x) => x % 2 === 0)` is…",
                   ["[1,3]", "[2,4]", "[1,2,3,4]", "2"], 1, "The even ones."),
                _q("`[1,2,3].find((x) => x > 1)` is…", ["[2,3]", "2", "1", "true"], 1,
                   "The first matching element itself."),
                _q("`[1,2,3].find((x) => x > 9)` is…", ["[]", "-1", "undefined", "0"], 2,
                   "find has nothing to return."),
                _q("`[].every((x) => x > 5)` is…", ["true", "false", "undefined", "an error"], 0,
                   "Vacuously true — there is no element that fails."),
            ],
            exercises=[
                _ex("tscourse-w6-fl-1", "Keep the evens",
                    "Print the even numbers, space-separated.",
                    _NUMS + 'console.log(nums.filter((x) => x % 2 === 0).join(" "));\n',
                    'x % 2 === 0',
                    [("1 2 3 4 5 6", "2 4 6"), ("1 3", "")],
                    hints=["Even means remainder 0 mod 2."]),
                _ex("tscourse-w6-fl-2", "Count the big ones",
                    "Print how many numbers are greater than 10.",
                    _NUMS + 'console.log(nums.filter((x) => x > 10).length);\n',
                    'nums.filter((x) => x > 10).length',
                    [("5 20 30 1", "2"), ("1 2", "0")],
                    hints=["Filter first, then take the length.",
                           "Write nums.filter((x) => x > 10).length."]),
                _ex("tscourse-w6-fl-3", "First over ten",
                    "Print the first number greater than 10, or `none` if there isn't one.",
                    _NUMS + 'const hit = nums.find((x) => x > 10);\n'
                    'console.log(hit === undefined ? "none" : hit);\n',
                    'nums.find((x) => x > 10)',
                    [("5 20 30", "20"), ("1 2", "none")],
                    hints=["find gives the element or undefined.",
                           "Write nums.find((x) => x > 10)."],
                    difficulty="Medium"),
                _ex("tscourse-w6-fl-4", "Any negatives?",
                    "Print whether any number is negative.",
                    _NUMS + 'console.log(nums.some((x) => x < 0));\n',
                    'nums.some((x) => x < 0)',
                    [("1 -2 3", "true"), ("1 2", "false")],
                    hints=["'Any at all' is exactly what some answers.",
                           "Write nums.some((x) => x < 0)."]),
                _ex("tscourse-w6-fl-5", "All positive?",
                    "Print whether every number is greater than 0.",
                    _NUMS + 'console.log(nums.every((x) => x > 0));\n',
                    'nums.every((x) => x > 0)',
                    [("1 2 3", "true"), ("1 -2", "false")],
                    hints=["every requires all of them to pass.",
                           "Write nums.every((x) => x > 0)."]),
                _ex("tscourse-w6-fl-6", "Narrow then reshape",
                    "Keep the words longer than 3 characters, uppercase them, and join with `, `.",
                    _WORDS + 'console.log(words.filter((w) => w.length > 3).map((w) => w.toUpperCase()).join(", "));\n',
                    '.filter((w) => w.length > 3).map((w) => w.toUpperCase())',
                    [("hi there you all", "THERE"), ("abcd efgh", "ABCD, EFGH")],
                    hints=["Filter first so there is less to transform.",
                           "Chain .filter(...) then .map(...)."],
                    difficulty="Medium"),
                _fix("tscourse-w6-fl-fix1", "Fix filter vs map",
                     "This should COUNT the evens (3 of them) but always prints 6. Fix it.",
                     _NUMS + 'const evens = nums.map((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                     _NUMS + 'const evens = nums.filter((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                     [("1 2 3 4 5 6", "3"), ("1 3 5", "0")],
                     hints=["map keeps every element, so its length never changes.",
                            "To keep only some, use filter."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("You need the first matching element. Best choice?",
                   ["filter(...)[0]", "find(...)", "some(...)", "map(...)"], 1,
                   "find says what you mean and stops at the first match."),
                _q("`arr.filter(p).length > 0` can be written as…",
                   ["arr.every(p)", "arr.some(p)", "arr.find(p)", "arr.map(p)"], 1,
                   "some asks exactly that question."),
                _q("`findIndex` returns what when nothing matches?",
                   ["undefined", "-1", "0", "null"], 1,
                   "Same sentinel as indexOf — and the same truthiness trap."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w6-sort", "Sorting",
            "Ordering a list — and the trap that catches everyone.",
            """
Start with the trap, because you will hit it:

```ts
[10, 9, 1].sort();      // [1, 10, 9]   ⚠️ not what you wanted
```

With no argument, `sort` converts every element to a **string** and orders them
alphabetically. As text, `"10"` really does come before `"9"`, because `1` comes
before `9`. This is not a bug; it's a default that suits words and ruins
numbers.

**Numbers need a comparator** — a function of two elements that returns a
number:

```ts
[10, 9, 1].sort((a, b) => a - b);    // [1, 9, 10]    ascending
[10, 9, 1].sort((a, b) => b - a);    // [10, 9, 1]    descending
```

The contract is:

| `compare(a, b)` returns | meaning |
|---|---|
| negative | `a` comes first |
| positive | `b` comes first |
| `0` | leave their order alone |

So `a - b` is negative exactly when `a` is smaller — ascending. Swap to `b - a`
for descending. You do not need to memorise more than that.

**Strings sort sensibly by default:**

```ts
["Cy", "Ada", "Bo"].sort();     // ["Ada", "Bo", "Cy"]
```

Though capitals sort before lowercase (`"Z" < "a"`), so normalise the case first
if that matters.

**`sort` mutates.** It reorders the array you called it on and returns that same
array — it does not hand you a sorted copy:

```ts
const a = [3, 1, 2];
const b = a.sort((x, y) => x - y);
console.log(a);          // [1,2,3]  ⚠️ a was reordered
console.log(b === a);    // true     — the same array
```

If the original matters, **copy first** — the idiom is worth memorising:

```ts
const sorted = [...a].sort((x, y) => x - y);
```

**`reverse` also mutates**, so the same rule applies: `[...a].reverse()`.

**Sorting by a field** is the everyday case, and it's the same comparator with
the field named:

```ts
[...people].sort((p, q) => p.age - q.age);
```

You'll use exactly this next week, on arrays of objects.

> ⚠️ **Common mistakes:** sorting numbers without a comparator; forgetting that
> `sort` mutates and then wondering why an earlier printout changed; and writing
> `(a, b) => a > b`, which returns a boolean where a number is required.
""",
            warmup=[
                _q("`[10, 9, 1].sort()` gives…",
                   ["[1,9,10]", "[1,10,9]", "[10,9,1]", "an error"], 1,
                   "Default sort compares as text."),
                _q("`[10, 9, 1].sort((a,b) => a - b)` gives…",
                   ["[1,9,10]", "[1,10,9]", "[10,9,1]", "[]"], 0, "Ascending numeric."),
                _q("`(a, b) => b - a` sorts…", ["ascending", "descending", "randomly",
                                                "alphabetically"], 1,
                   "The sign is flipped, so bigger comes first."),
                _q("After `a.sort(...)`, the array `a` is…",
                   ["unchanged", "reordered in place", "emptied", "copied"], 1,
                   "sort mutates — copy first if you need the original."),
            ],
            exercises=[
                _ex("tscourse-w6-so-1", "Sort ascending",
                    "Print the numbers in ascending order, space-separated.",
                    _NUMS + 'console.log([...nums].sort((a, b) => a - b).join(" "));\n',
                    '(a, b) => a - b',
                    [("10 9 1", "1 9 10"), ("3 1 2", "1 2 3")],
                    hints=["Numbers need a comparator, or they sort as text.",
                           "Write (a, b) => a - b."]),
                _ex("tscourse-w6-so-2", "Sort descending",
                    "Print the numbers largest first, space-separated.",
                    _NUMS + 'console.log([...nums].sort((a, b) => b - a).join(" "));\n',
                    '(a, b) => b - a',
                    [("1 9 10", "10 9 1"), ("3 1 2", "3 2 1")],
                    hints=["Flip the subtraction to reverse the order.",
                           "Write (a, b) => b - a."]),
                _ex("tscourse-w6-so-3", "Alphabetical",
                    "Print the words in alphabetical order, space-separated.",
                    _WORDS + 'console.log([...words].sort().join(" "));\n',
                    '[...words].sort()',
                    [("cy ada bo", "ada bo cy"), ("b a", "a b")],
                    hints=["Strings sort sensibly with no comparator at all.",
                           "Write [...words].sort()."]),
                _ex("tscourse-w6-so-4", "Keep the original",
                    "Print the sorted list, then the ORIGINAL list unchanged.",
                    _NUMS + 'const sorted = [...nums].sort((a, b) => a - b);\n'
                    'console.log(sorted.join(" "));\nconsole.log(nums.join(" "));\n',
                    'const sorted = [...nums].sort((a, b) => a - b);',
                    [("3 1 2", "1 2 3\n3 1 2"), ("2 1", "1 2\n2 1")],
                    hints=["sort mutates, so sort a copy.",
                           "Write const sorted = [...nums].sort((a, b) => a - b);"],
                    difficulty="Medium"),
                _ex("tscourse-w6-so-5", "The three smallest",
                    "Print the three smallest numbers in ascending order, space-separated.",
                    _NUMS + 'console.log([...nums].sort((a, b) => a - b).slice(0, 3).join(" "));\n',
                    '.slice(0, 3)',
                    [("5 3 9 1 7", "1 3 5"), ("2 1 4", "1 2 4")],
                    hints=["Sort ascending, then take the front of the list.",
                           "Chain .slice(0, 3)."],
                    difficulty="Medium"),
                _ex("tscourse-w6-so-6", "Second largest",
                    "Print the second largest number.",
                    _NUMS + 'console.log([...nums].sort((a, b) => b - a)[1]);\n',
                    '[...nums].sort((a, b) => b - a)[1]',
                    [("5 3 9 1", "5"), ("2 7", "2")],
                    hints=["Sort descending, then take index 1.",
                           "Write [...nums].sort((a, b) => b - a)[1]."],
                    difficulty="Medium"),
                _fix("tscourse-w6-so-fix1", "Fix the text sort",
                     "This should sort numbers ascending but gives `1 10 9`. Fix it.",
                     _NUMS + 'console.log([...nums].sort().join(" "));\n',
                     _NUMS + 'console.log([...nums].sort((a, b) => a - b).join(" "));\n',
                     [("10 9 1", "1 9 10"), ("100 20 3", "3 20 100")],
                     hints=["With no comparator, sort compares string forms.",
                            "Supply (a, b) => a - b."],
                     difficulty="Medium"),
                _fix("tscourse-w6-so-fix2", "Fix the clobbered original",
                     "The second line should print the ORIGINAL order but prints the sorted one. Fix it.",
                     _NUMS + 'const sorted = nums.sort((a, b) => a - b);\n'
                     'console.log(sorted.join(" "));\nconsole.log(nums.join(" "));\n',
                     _NUMS + 'const sorted = [...nums].sort((a, b) => a - b);\n'
                     'console.log(sorted.join(" "));\nconsole.log(nums.join(" "));\n',
                     [("3 1 2", "1 2 3\n3 1 2")],
                     hints=["sort reordered nums itself, and returned that same array.",
                            "Sort a copy: [...nums].sort(...)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A comparator returning a negative number means…",
                   ["a comes first", "b comes first", "they are equal", "an error"], 0,
                   "Negative keeps a ahead of b."),
                _q("`(a, b) => a > b` as a comparator is wrong because…",
                   ["it is too slow", "it returns a boolean where a number is needed",
                    "it sorts descending", "it mutates"], 1,
                   "true/false convert to 1/0, so 'a comes first' can never be expressed."),
                _q("`[...a].sort()` rather than `a.sort()` because…",
                   ["it is faster", "sort mutates, and the copy protects the original",
                    "sort needs an array", "no reason"], 1,
                   "The spread makes a fresh array for sort to reorder."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w6-pipeline", "Chaining: building a pipeline",
            "split → filter → map → sort → slice → join, as one readable flow.",
            """
You have met `split`, `map`, `filter`, `sort` and `join` one at a time. Real
programs use them **together**, in a chain, because every one of them *returns a
new array* — so the next one can start where the last finished.

```ts
const raw = "5, 12, -3, 8, 20";

const top = raw
  .split(",")                     // ["5", " 12", " -3", " 8", " 20"]
  .map((s) => Number(s.trim()))   // [5, 12, -3, 8, 20]
  .filter((n) => n > 0)           // [5, 12, 8, 20]
  .sort((a, b) => b - a)          // [20, 12, 8, 5]
  .slice(0, 3);                   // [20, 12, 8]

console.log(top.join(" "));       // 20 12 8
```

Read a chain **top to bottom**: each line is one small, total transformation of
the whole list. That is much easier to hold in your head than one loop doing
five things at once.

**Order changes the answer.** These two are not the same program:

```ts
words.filter((w) => w.length > 3).map((w) => w.toUpperCase())   // test the raw value
words.map((w) => w.toUpperCase()).filter((w) => w.length > 3)   // test the mapped value
```

The rule of thumb: **filter first when the test works on the original value** —
you then do the expensive `map` on fewer items. Map first only when the test
needs the transformed value.

**`slice` is your "take" and your "copy".** `xs.slice(0, 3)` takes the first
three; a bare `xs.slice()` copies the whole array. That copy matters because
`sort` and `reverse` are the odd ones out — they **mutate in place** and return
the *same* array:

```ts
const scores = [88, 92, 79];
const ranked = scores.slice().sort((a, b) => b - a);   // copy first, then sort
console.log(scores.join(","));   // 88,92,79 — untouched
```

**`map` hands you the index too.** The callback's second parameter is the
position, which is how you number a list:

```ts
const names = ["ada", "alan"];
console.log(names.map((n, i) => `${i + 1}. ${n}`).join("\\n"));
// 1. ada
// 2. alan
```

**Name the middle when the chain gets long.** A chain of three is a sentence; a
chain of eight is a paragraph with no full stops. Break it:

```ts
const cleaned = lines.map((l) => l.trim()).filter((l) => l.length > 0);
const parsed = cleaned.map((l) => l.split(","));
```

Named steps also give you somewhere to put a `console.log` when the answer comes
out wrong — inspect `cleaned`, then `parsed`, and the broken stage announces
itself.

> ⚠️ **Common mistakes:** calling `filter` and throwing the result away (these
> methods never change the original — you must keep what they return); writing
> `(n) => { n > 0; }` with braces but no `return`, so every test is `undefined`
> and the result is empty; and sorting a shared array without copying it first.
""",
            warmup=[
                _q("`[1,2,3,4].filter((n) => n % 2 === 0).map((n) => n * 10)` gives…",
                   ["[10,20,30,40]", "[20,40]", "[2,4]", "[]"], 1,
                   "Filter keeps 2 and 4; map then multiplies each by 10."),
                _q("`nums.filter((n) => n > 0);` on its own line, then printing `nums`, shows…",
                   ["only the positives", "the original array unchanged", "an empty array", "an error"], 1,
                   "filter returns a NEW array; ignoring it changes nothing."),
                _q("`[1,2,3].map((n, i) => n * i)` gives…",
                   ["[1,2,3]", "[0,2,6]", "[0,1,2]", "[1,4,9]"], 1,
                   "The second parameter is the index: 1*0, 2*1, 3*2."),
                _q("Which method changes the array it is called on?",
                   ["map", "filter", "slice", "sort"], 3,
                   "sort (and reverse) mutate in place — copy with slice() first."),
            ],
            exercises=[
                _ex("tscourse-w6-pipe-1", "Filter, then map",
                    "Keep the even numbers, then multiply each by 10. Fill in the filtering stage.",
                    'const nums = [1, 2, 3, 4, 5, 6];\n'
                    'const result = nums.filter((n) => n % 2 === 0).map((n) => n * 10);\n'
                    'console.log(result.join(","));\n',
                    'filter((n) => n % 2 === 0)', [("", "20,40,60")],
                    hints=["A number is even when the remainder after dividing by 2 is 0.",
                           "Write filter((n) => n % 2 === 0)."]),
                _ex("tscourse-w6-pipe-2", "Map, then filter",
                    "The test needs the mapped value — the lengths — so map runs first. Add the filter that keeps lengths above 2.",
                    'const words = ["hi", "there", "ok", "friend"];\n'
                    'const lens = words.map((w) => w.length).filter((n) => n > 2);\n'
                    'console.log(lens.join(" "));\n',
                    '.filter((n) => n > 2)', [("", "5 6")],
                    hints=["After map you have [2, 5, 2, 6].",
                           "Chain .filter((n) => n > 2) onto the map."]),
                _ex("tscourse-w6-pipe-3", "Sort inside a chain",
                    "Read a comma-separated list, keep the positives, and print the three largest, biggest first. Add the sorting stage.",
                    _FS +
                    'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'const top = raw\n'
                    '  .split(",")\n'
                    '  .map((s) => Number(s.trim()))\n'
                    '  .filter((n) => n > 0)\n'
                    '  .sort((a, b) => b - a)\n'
                    '  .slice(0, 3);\n'
                    'console.log(top.join(" "));\n',
                    '.sort((a, b) => b - a)',
                    [("5, 12, -3, 8, 20, 1", "20 12 8"), ("3,1,2", "3 2 1"), ("-4, 7", "7")],
                    hints=["Descending order means the comparator subtracts the other way round.",
                           "Write .sort((a, b) => b - a)."],
                    difficulty="Easy"),
                _ex("tscourse-w6-pipe-4", "Name the middle",
                    "Lines are cleaned into `names`; now build `shouted` from it by upper-casing every name.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const names = lines.map((l) => l.trim()).filter((l) => l.length > 0);\n'
                    'const shouted = names.map((n) => n.toUpperCase());\n'
                    'console.log(shouted.join(", "));\n',
                    'names.map((n) => n.toUpperCase())',
                    [("ada\n  grace \n\nalan", "ADA, GRACE, ALAN"), ("solo", "SOLO")],
                    hints=["Start from the array the previous line named, not from `lines`.",
                           "Write names.map((n) => n.toUpperCase())."],
                    difficulty="Easy"),
                _ex("tscourse-w6-pipe-5", "Copy before you sort",
                    "Print the scores sorted ascending, then prove the original is untouched. Fill in the copy.",
                    'const scores = [88, 92, 79, 95, 61];\n'
                    'const sorted = scores.slice().sort((a, b) => a - b);\n'
                    'console.log(sorted.join(","));\n'
                    'console.log(scores.join(","));\n',
                    'scores.slice()', [("", "61,79,88,92,95\n88,92,79,95,61")],
                    hints=["sort rearranges the array it is given, so hand it a copy.",
                           "A bare slice() with no arguments copies the whole array."],
                    difficulty="Easy"),
                _ex("tscourse-w6-pipe-6", "Number the list",
                    "Print each name on its own line, numbered from 1. Use map's index parameter.",
                    'const names = ["ada", "alan", "grace"];\n'
                    'const numbered = names.map((n, i) => `${i + 1}. ${n}`);\n'
                    'console.log(numbered.join("\\n"));\n',
                    '(n, i) => `${i + 1}. ${n}`',
                    [("", "1. ada\n2. alan\n3. grace")],
                    hints=["The callback can take a second parameter: the index, counting from 0.",
                           "Add 1 to the index so the list starts at 1."],
                    difficulty="Medium"),
                _fix("tscourse-w6-pipe-fix1", "Fix the discarded result",
                     "This should print only the positive numbers, but prints all of them. The filtered array is being thrown away.",
                     'const nums = [3, -1, 4, -5, 9];\n'
                     'nums.filter((n) => n > 0);\n'
                     'console.log(nums.join(","));\n',
                     'const nums = [3, -1, 4, -5, 9];\n'
                     'const positive = nums.filter((n) => n > 0);\n'
                     'console.log(positive.join(","));\n',
                     [("", "3,4,9")],
                     hints=["filter never edits the array it is called on — it hands back a new one.",
                            "Store the returned array in a const and print that instead."]),
                _fix("tscourse-w6-pipe-fix2", "Fix the silent predicate",
                     "This should print 3 (the count of even numbers) but prints 0. The callback has braces but never returns.",
                     'const nums = [1, 2, 3, 4, 5, 6];\n'
                     'const evens = nums.filter((n) => { n % 2 === 0; });\n'
                     'console.log(evens.length);\n',
                     'const nums = [1, 2, 3, 4, 5, 6];\n'
                     'const evens = nums.filter((n) => n % 2 === 0);\n'
                     'console.log(evens.length);\n',
                     [("", "3")],
                     hints=["A braced arrow body needs an explicit return; without one every test is undefined.",
                            "Drop the braces so the expression is returned automatically."],
                     difficulty="Medium"),
                _fix("tscourse-w6-pipe-fix3", "Fix the mutated original",
                     "This should print the top score and then the original order, but sorting rearranged the array everyone shares.",
                     'const scores = [88, 92, 79];\n'
                     'const ranked = scores.sort((a, b) => b - a);\n'
                     'console.log(`Top: ${ranked[0]}`);\n'
                     'console.log(`Original: ${scores.join(",")}`);\n',
                     'const scores = [88, 92, 79];\n'
                     'const ranked = scores.slice().sort((a, b) => b - a);\n'
                     'console.log(`Top: ${ranked[0]}`);\n'
                     'console.log(`Original: ${scores.join(",")}`);\n',
                     [("", "Top: 92\nOriginal: 88,92,79")],
                     hints=["sort is one of the two array methods that change the array in place.",
                            "Insert a .slice() before the .sort(...) so it sorts a copy."],
                     difficulty="Medium"),
                _ch("tscourse-w6-pipe-ch1", "Leaderboard", "Medium",
                    "Each input line is `name,score`, and blank lines may appear. Build the pipeline: clean the lines, split each into fields, rank by score highest first, keep the top three, and number them as `1. name (score)`.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const rows = lines\n'
                    '  .map((l) => l.trim())\n'
                    '  .filter((l) => l.length > 0)\n'
                    '  .map((l) => l.split(","));\n'
                    'const ranked = rows.sort((a, b) => Number(b[1]) - Number(a[1])).slice(0, 3);\n'
                    'const out = ranked.map((r, i) => `${i + 1}. ${r[0]} (${r[1]})`);\n'
                    'console.log(out.join("\\n"));\n',
                    'const rows = lines\n'
                    '  .map((l) => l.trim())\n'
                    '  .filter((l) => l.length > 0)\n'
                    '  .map((l) => l.split(","));\n'
                    'const ranked = rows.sort((a, b) => Number(b[1]) - Number(a[1])).slice(0, 3);\n'
                    'const out = ranked.map((r, i) => `${i + 1}. ${r[0]} (${r[1]})`);',
                    [("ada,91\ngrace,88\n\nalan,95\nedsger,70",
                      "1. alan (95)\n2. ada (91)\n3. grace (88)"),
                     ("bob,10\nsue,20", "1. sue (20)\n2. bob (10)")],
                    hints=["Four stages: trim each line, drop the empty ones, split each on the comma, then rank.",
                           "After the last map, each row is a two-element array: [name, score].",
                           "The score is text, so compare Number(b[1]) - Number(a[1]) for descending order.",
                           "slice(0, 3) takes the top three, and map's index gives you the numbering."]),
            ],
            quiz=[
                _q("Why can array methods be chained?",
                   ["they mutate in place", "each returns a new array for the next one to work on",
                    "TypeScript rewrites them", "they are asynchronous"], 1,
                   "map/filter/slice each hand back a fresh array."),
                _q("`filter` before `map` is usually preferred because…",
                   ["it reads better", "the map then runs on fewer items",
                    "map cannot come first", "filter is faster than map"], 1,
                   "Unless the test needs the mapped value, shrink the list first."),
                _q("`xs.slice()` with no arguments…",
                   ["empties the array", "copies the whole array", "sorts it", "is an error"], 1,
                   "Which is exactly how you protect an array from an in-place sort."),
                _q("A long chain is worth breaking into named steps because…",
                   ["it runs faster", "you get somewhere to inspect the middle when it goes wrong",
                    "chains are limited to three calls", "TypeScript requires it"], 1,
                   "Named stages turn debugging into reading."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #6 — the month in numbers",
        """
Budget Buddy finally sees a whole month at once. The input is a line of
expense amounts:

```
12 3 45 7 3 20
```

Print a six-line summary:

```
Count:    6
Total:    $90.00
Average:  $15.00
Largest:  $45.00
Smallest: $3.00
Top 3:    45, 20, 12
```

Rules:

- Money is shown to two decimal places.
- `Top 3` is the three largest amounts, largest first, joined with `, `. If
  there are fewer than three, show all of them.
- The input array must be left **unsorted** — sort copies, not the original.
""",
        _ch("tscourse-w6-capstone", "Budget Buddy #6", "Medium",
            "Compute the six statistics and print them.",
            _NUMS +
            'let total = 0;\n'
            'for (const x of nums) {\n  total += x;\n}\n'
            'const desc = [...nums].sort((a, b) => b - a);\n'
            'console.log(`Count:    ${nums.length}`);\n'
            'console.log(`Total:    $${total.toFixed(2)}`);\n'
            'console.log(`Average:  $${(total / nums.length).toFixed(2)}`);\n'
            'console.log(`Largest:  $${desc[0].toFixed(2)}`);\n'
            'console.log(`Smallest: $${desc[desc.length - 1].toFixed(2)}`);\n'
            'console.log(`Top 3:    ${desc.slice(0, 3).join(", ")}`);\n',
            'let total = 0;\n'
            'for (const x of nums) {\n  total += x;\n}\n'
            'const desc = [...nums].sort((a, b) => b - a);\n'
            'console.log(`Count:    ${nums.length}`);\n'
            'console.log(`Total:    $${total.toFixed(2)}`);\n'
            'console.log(`Average:  $${(total / nums.length).toFixed(2)}`);\n'
            'console.log(`Largest:  $${desc[0].toFixed(2)}`);\n'
            'console.log(`Smallest: $${desc[desc.length - 1].toFixed(2)}`);\n'
            'console.log(`Top 3:    ${desc.slice(0, 3).join(", ")}`);',
            [("12 3 45 7 3 20",
              "Count:    6\nTotal:    $90.00\nAverage:  $15.00\nLargest:  $45.00\nSmallest: $3.00\nTop 3:    45, 20, 12"),
             ("10", "Count:    1\nTotal:    $10.00\nAverage:  $10.00\nLargest:  $10.00\nSmallest: $10.00\nTop 3:    10"),
             ("5 1", "Count:    2\nTotal:    $6.00\nAverage:  $3.00\nLargest:  $5.00\nSmallest: $1.00\nTop 3:    5, 1")],
            hints=["Total needs a loop and an accumulator — reduce arrives in week 8.",
                   "Sort a COPY descending once, and read largest, smallest and the top three off it.",
                   "The smallest is the last element of the descending copy: desc[desc.length - 1].",
                   'Top 3 is desc.slice(0, 3).join(", ") — slice happily returns fewer if there are fewer.']),
        example_io="Count:    6\nTotal:    $90.00\nAverage:  $15.00\nLargest:  $45.00\nSmallest: $3.00\nTop 3:    45, 20, 12",
        rubric=["Count, total, average, largest and smallest are all computed from the array",
                "Money values carry two decimal places",
                "Top 3 is sorted descending and joined with a comma and a space",
                "The original array is never mutated — sorting happens on a copy"],
        stretch=_ch("tscourse-w6-capstone-stretch", "Budget Buddy #6 (stretch)", "Medium",
                    "Add a seventh line, `Over avg: <n>`, counting how many amounts are strictly above the average.",
                    _NUMS +
                    'let total = 0;\n'
                    'for (const x of nums) {\n  total += x;\n}\n'
                    'const avg = total / nums.length;\n'
                    'const desc = [...nums].sort((a, b) => b - a);\n'
                    'console.log(`Count:    ${nums.length}`);\n'
                    'console.log(`Total:    $${total.toFixed(2)}`);\n'
                    'console.log(`Average:  $${avg.toFixed(2)}`);\n'
                    'console.log(`Largest:  $${desc[0].toFixed(2)}`);\n'
                    'console.log(`Smallest: $${desc[desc.length - 1].toFixed(2)}`);\n'
                    'console.log(`Top 3:    ${desc.slice(0, 3).join(", ")}`);\n'
                    'console.log(`Over avg: ${nums.filter((x) => x > avg).length}`);\n',
                    'console.log(`Over avg: ${nums.filter((x) => x > avg).length}`);',
                    [("12 3 45 7 3 20",
                      "Count:    6\nTotal:    $90.00\nAverage:  $15.00\nLargest:  $45.00\nSmallest: $3.00\nTop 3:    45, 20, 12\nOver avg: 2"),
                     ("5 1", "Count:    2\nTotal:    $6.00\nAverage:  $3.00\nLargest:  $5.00\nSmallest: $1.00\nTop 3:    5, 1\nOver avg: 1")],
                    hints=["Name the average once so both the printout and the count can use it.",
                           "Counting matches is filter then .length.",
                           "Write nums.filter((x) => x > avg).length."]),
    ),
))

# --- Week 7 ---------------------------------------------------------------
_WEEKS.append(_week(
    7, 2, _M2,
    "Objects",
    "Model a 'thing' as a bundle of named fields, reach into it safely, and process arrays of records.",
    """
An array holds many values in a row. An **object** holds a few values *by name*:

```ts
const expense = { desc: "coffee", amount: 3.25, paid: true };
```

Arrays answer "which one?" with a number. Objects answer "which one?" with a
word — and words are what real data is made of. An expense has a description,
an amount and a paid flag; calling them `e[0]`, `e[1]`, `e[2]` would be
technically possible and humanly hopeless.

Put the two together and you get **an array of objects** — the shape of very
nearly every dataset you will ever touch:

```ts
const expenses = [
  { desc: "coffee", amount: 3.25, paid: true },
  { desc: "book",   amount: 12,   paid: false },
];
```

This week: building objects, reaching into them (including when a field might
not be there), passing them around, processing lists of them, the sharing
behaviour that catches everyone out, and using an object as a **lookup table** —
which is the single most useful trick in the whole course.

⏱️ Budget about **nine hours**, spread over several sittings.
""",
    objectives=[
        "Create objects, read fields with dot access, and update or add fields",
        "Reach a field whose name is decided at runtime, with bracket access",
        "Handle missing fields with in, optional chaining and ??",
        "Navigate nested objects and arrays inside objects",
        "Take objects as parameters and return them, with destructuring",
        "Filter, map and sort an array of records by a field",
        "Tell sharing from copying, and make a copy with spread",
        "Count and group with an object used as a lookup table",
        "Group records into buckets keyed by any field, in a single pass",
        "Summarise each bucket and print the report in a stable, sorted order",
    ],
    why="Objects are how a program talks about the real world — a user, an order, a row, a config. Once you can model data as records and process a list of them, you can write actual applications.",
    est_minutes=550,
    glossary=[
        _gloss("object", "A bundle of named values: { name: \"Ada\" }."),
        _gloss("property / field / key", "One named slot on an object."),
        _gloss("value", "What is stored in a slot."),
        _gloss("dot access", "Reaching a known field: obj.name."),
        _gloss("bracket access", "Reaching a field by a name computed at runtime: obj[k]."),
        _gloss("shorthand", "{ name } is short for { name: name }."),
        _gloss("in", "Tests whether a key exists: \"paid\" in obj."),
        _gloss("optional chaining (?.)", "Reads a field only if the thing exists, else undefined."),
        _gloss("?? (nullish coalescing)", "A fallback used only for null/undefined, not for 0 or \"\"."),
        _gloss("destructuring", "Pulling fields into names: const { desc, amount } = e;"),
        _gloss("record", "An object used as one row of data."),
        _gloss("reference", "A name pointing at an object. Two names can point at the same one."),
        _gloss("aliasing", "Two names sharing one object, so a change through either is seen by both."),
        _gloss("shallow copy", "{ ...o } — a new top-level object, but nested objects are still shared."),
        _gloss("lookup table", "An object used as a name-to-value map."),
        _gloss("Object.keys / values / entries", "Turn an object into an array of its keys, values, or [key, value] pairs."),
        _gloss("grouping", "Bucketing records under a key so each bucket holds every matching item."),
        _gloss("bucket", "The array (or running total) stored under one key of a lookup table."),
        _gloss("accumulator table", "A lookup whose values are running totals rather than arrays."),
        _gloss("deterministic output", "Output that is identical for identical input — here, by sorting the keys."),
    ],
    cheatsheet="""
```ts
// ---- create & read ---------------------------------------------------
const e = { desc: "coffee", amount: 3.25, paid: true };
e.desc                    // "coffee"
e.missing                 // undefined  (no error)
e.amount = 4;             // update
e.tag = "food";           // add (needs a `let`-style shape or an annotation)

const desc = "tea";
const f = { desc };       // shorthand for { desc: desc }

// ---- dynamic keys -----------------------------------------------------
const k = "amount";
e[k]                      // 3.25   bracket access
"paid" in e               // true
Object.keys(e)            // ["desc","amount","paid"]
Object.values(e)          // ["coffee",3.25,true]
Object.entries(e)         // [["desc","coffee"], ...]

// ---- possibly missing --------------------------------------------------
user?.address?.city       // undefined instead of a crash
e.note ?? "(none)"        // fallback ONLY for null/undefined
e.count ?? 0              // 0 stays 0; ||  would replace it

// ---- nested ------------------------------------------------------------
const u = { name: "Ada", address: { city: "London" }, tags: ["a","b"] };
u.address.city            // "London"
u.tags[0]                 // "a"

// ---- functions ---------------------------------------------------------
function total(e: { amount: number; qty: number }): number {
  return e.amount * e.qty;
}
function label({ desc, amount }: { desc: string; amount: number }): string {
  return `${desc}: ${amount}`;      // destructured parameter
}

// ---- arrays of records --------------------------------------------------
const rows = [{ n: "a", v: 2 }, { n: "b", v: 9 }];
rows.filter((r) => r.v > 5)
rows.map((r) => r.n)
[...rows].sort((p, q) => p.v - q.v)

// ---- sharing vs copying --------------------------------------------------
const b = a;              // ⚠️ same object
const c = { ...a };       // a fresh shallow copy
const d = { ...a, v: 9 }; // copy with one field replaced

// ---- lookup table / tally -------------------------------------------------
const counts: { [key: string]: number } = {};
for (const w of words) {
  counts[w] = (counts[w] ?? 0) + 1;
}
```
""",
    self_check=[
        "Can you read and update a field on an object?",
        "Can you say what `obj.nope` gives you, and why that is dangerous?",
        "Can you reach a field whose name is in a variable?",
        "Can you total one field across an array of records?",
        "Can you sort records by a field without mutating the original array?",
        "Can you explain why `const b = a` then `b.x = 1` changes `a` too?",
        "Can you count word frequencies with an object?",
        "Can you group an array of records by one of their fields without knowing the categories in advance?",
        "Can you say when to bucket into arrays and when to accumulate straight into numbers?",
    ],
    review=[
        _q("How do you read the `name` of `user`?",
           ["user[name]", "user->name", "user.name", "name(user)"], 2,
           "Dot access for a key you know at write time."),
        _q("`({a: 1}).b` evaluates to…", ["null", "0", "undefined", "an error"], 2,
           "Missing fields are undefined, silently."),
        _q("`const k = \"a\"; ({a: 1})[k]` is…", ["undefined", "1", '"a"', "an error"], 1,
           "Bracket access uses the VALUE of k as the key."),
        _q("`obj?.x` when obj is undefined gives…",
           ["a crash", "undefined", "null", "0"], 1,
           "Optional chaining short-circuits instead of throwing."),
        _q("`0 ?? 5` is…", ["5", "0", "undefined", "an error"], 1,
           "?? only falls back for null/undefined — 0 is a real value. `0 || 5` would give 5."),
        _q("`const b = a; b.x = 9;` — what is `a.x`?",
           ["unchanged", "9", "undefined", "an error"], 1,
           "Both names point at the same object."),
        _q("`{ ...a }` gives you…",
           ["the same object", "a shallow copy", "a deep copy", "an array"], 1,
           "Top level is fresh; nested objects are still shared."),
        _q("`Object.keys({a:1, b:2})` is…",
           ["[1,2]", '["a","b"]', "2", '[["a",1],["b",2]]'], 1,
           "The key names, as an array of strings."),
        _q("Sorting records by a numeric field uses the comparator…",
           ["(p, q) => p.v > q.v", "(p, q) => p.v - q.v", "(p, q) => p - q", "none"], 1,
           "Same rule as week 6 — subtract, don't compare."),
        _q("`counts[w] = (counts[w] ?? 0) + 1;` — why the `?? 0`?",
           ["style", "the first time a word appears, counts[w] is undefined",
            "to reset the count", "it is optional"], 1,
           "undefined + 1 is NaN, so the first occurrence needs a starting value."),
        _q("The two lines at the heart of grouping are…",
           ["sort then join", "create the bucket if missing, then push",
            "keys then values", "filter then map"], 1,
           "Everything else is choosing what the key should be."),
        _q("`tally[k] = tally[k] + 1` for a brand-new key gives…",
           ["1", "0", "NaN", "an error"], 2,
           "undefined + 1 is NaN — start from (tally[k] ?? 0)."),
        _q("Sorting `Object.keys(groups)` before printing gives you…",
           ["faster lookup", "a report that is identical for identical input",
            "sorted buckets", "fewer keys"], 1,
           "Stable output is what makes a report testable."),
    ],
    milestone="Budget Buddy now models each expense as a proper record and reports over the whole list — the data shape real applications use.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w7-basics", "Object basics",
            "Keys, values and dot access.",
            """
An **object literal** is a comma-separated list of `key: value` pairs in braces:

```ts
const point = { x: 3, y: 4 };
const user = { name: "Ada", age: 36, admin: true };
```

Keys are names; values can be anything — numbers, strings, booleans, arrays,
even other objects.

**Reading** uses a dot:

```ts
point.x        // 3
user.name      // "Ada"
```

**Updating** assigns through the same dot:

```ts
point.y = point.y + 1;    // 5
user.age += 1;            // 37
```

**`const` doesn't freeze it** — same as arrays last week. `const` fixes the
name, not the contents:

```ts
const p = { x: 1 };
p.x = 2;        // ✅ fine
p = { x: 3 };   // ❌ error — cannot repoint the name
```

**A missing key gives `undefined`**, quietly:

```ts
user.email     // undefined — no error, no warning at runtime
```

This is the object equivalent of reading past the end of an array, and it's why
a typo like `user.nmae` produces a mystery `undefined` three functions later
rather than an error at the scene. TypeScript catches this one for you when the
object's shape is known — one of the clearest wins the language offers.

**Shorthand.** When a variable already has the name you want for the key, say
it once:

```ts
const desc = "coffee";
const e = { desc };          // same as { desc: desc }
```

> ⚠️ **Common mistakes:** separating pairs with `;` instead of `,` inside the
> braces; misspelling a key on read (silent `undefined`) or on write (you
> quietly create a *new* field); and expecting `const` to prevent field updates.
""",
            warmup=[
                _q("`const u = { age: 5 }; console.log(u.age);` prints…",
                   ["age", "5", "u.age", "undefined"], 1, "It reads the value."),
                _q("`const u = { age: 5 }; console.log(u.name);` prints…",
                   ["null", "undefined", "an error", '""'], 1,
                   "Missing keys read as undefined."),
                _q("`const p = { x: 1 }; p.x = 2;` is…",
                   ["an error, p is const", "fine", "a no-op", "a copy"], 1,
                   "const fixes the binding, not the contents."),
                _q("`const n = 'a'; const o = { n };` gives o the key…",
                   ['"n"', '"a"', "both", "none"], 0,
                   'Shorthand uses the VARIABLE NAME as the key: { n: "a" }.'),
            ],
            exercises=[
                _ex("tscourse-w7-b-1", "Read a field", "Print the user's name.",
                    'const user = { name: "Ada", age: 36 };\nconsole.log(user.name);\n',
                    'user.name', [("", "Ada")],
                    hints=["Reach it with a dot."]),
                _ex("tscourse-w7-b-2", "Update a field",
                    "Add 5 to counter.value, then print it.",
                    'const counter = { value: 0 };\ncounter.value = counter.value + 5;\nconsole.log(counter.value);\n',
                    'counter.value + 5', [("", "5")],
                    hints=["Read the current value and add to it."]),
                _ex("tscourse-w7-b-3", "Build an object",
                    "Build an expense with desc `coffee` and amount 3, then print the amount.",
                    'const e = { desc: "coffee", amount: 3 };\nconsole.log(e.amount);\n',
                    '{ desc: "coffee", amount: 3 }', [("", "3")],
                    hints=["Pairs are key: value, separated by commas.",
                           'Write { desc: "coffee", amount: 3 }.']),
                _ex("tscourse-w7-b-4", "Two fields in a sentence",
                    "Print `Ada is 36`.",
                    'const user = { name: "Ada", age: 36 };\nconsole.log(`${user.name} is ${user.age}`);\n',
                    '`${user.name} is ${user.age}`', [("", "Ada is 36")],
                    hints=["Two holes, each a dot access.",
                           "Write `${user.name} is ${user.age}`."]),
                _ex("tscourse-w7-b-5", "Shorthand",
                    "Build the object using shorthand so its key is `desc`.",
                    _FS + 'const desc = fs.readFileSync(0, "utf8").trim();\n'
                    'const e = { desc };\nconsole.log(e.desc);\n',
                    '{ desc }', [("coffee", "coffee"), ("rent", "rent")],
                    hints=["When the variable is already named right, say it once.",
                           "Write { desc }."]),
                _fix("tscourse-w7-b-fix1", "Fix the field name",
                     "This should print the name but prints undefined. Fix it.",
                     'const user = { name: "Ada", age: 36 };\nconsole.log(user.username);\n',
                     'const user = { name: "Ada", age: 36 };\nconsole.log(user.name);\n',
                     [("", "Ada")],
                     hints=["There is no `username` key on this object.",
                            "The key is `name`."]),
                _fix("tscourse-w7-b-fix2", "Fix the typo'd write",
                     "This should print 5, but the update lands on the wrong field and it prints 0. Fix it.",
                     'const counter = { value: 0 };\ncounter.valeu = 5;\nconsole.log(counter.value);\n',
                     'const counter = { value: 0 };\ncounter.value = 5;\nconsole.log(counter.value);\n',
                     [("", "5")],
                     hints=["Writing a misspelled key silently creates a brand-new field.",
                            "The key is `value`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Reading a key that does not exist gives…",
                   ["an error", "null", "undefined", "0"], 2,
                   "Silently — which is exactly why annotating shapes is worth it."),
                _q("Objects answer 'which one?' with…",
                   ["a number", "a name", "an index", "a type"], 1,
                   "Arrays use positions; objects use names."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w7-access", "Dynamic keys & missing fields",
            "Bracket access, in, ?. and ??.",
            """
Dot access needs the key spelled out when you write the code. When the key is
only known at **runtime**, use brackets:

```ts
const e = { desc: "coffee", amount: 3 };
const k = "amount";

e.k        // ⚠️ undefined — looks for a key literally called "k"
e[k]       // 3            — uses the VALUE of k
```

That distinction is the whole lesson: `e.k` is the key `"k"`; `e[k]` is the key
whose name `k` holds.

**Does the key exist?** `in` asks directly:

```ts
"amount" in e     // true
"paid" in e       // false
```

Why not just check `e.paid === undefined`? Because a key *can* exist and hold
`undefined`. `in` distinguishes "absent" from "present but empty".

**Optional chaining `?.`** reads through something that might not be there:

```ts
const u = { name: "Ada" };
u.address.city      // 💥 crashes — cannot read city of undefined
u.address?.city     // undefined — stops safely
```

Read `a?.b` as *"if `a` is null or undefined, the whole thing is `undefined`;
otherwise carry on"*. It short-circuits the rest of the chain, so
`u?.address?.city` is safe at every step.

**Nullish coalescing `??`** supplies a fallback:

```ts
e.note ?? "(none)"      // "(none)" when note is missing
```

`??` falls back **only** for `null` and `undefined`. Its older cousin `||` falls
back for every falsy value, which quietly destroys legitimate data:

```ts
const count = 0;
count || 10     // 10  ⚠️ a real zero was thrown away
count ?? 10     // 0   ✅
```

When the fallback is for *missing*, use `??`. Reserve `||` for genuine
true/false logic.

> ⚠️ **Common mistakes:** writing `e.k` when you meant `e[k]`; using `||` where
> `??` was needed and losing zeros and empty strings; and reaching for `?.`
> everywhere, which hides bugs — use it where a value is *genuinely* optional.
""",
            warmup=[
                _q('`const k = "a"; const o = { a: 1 }; o[k]` is…',
                   ["undefined", "1", '"a"', "an error"], 1, "Bracket access uses k's value."),
                _q('`const k = "a"; const o = { a: 1 }; o.k` is…',
                   ["1", "undefined", '"a"', "an error"], 1,
                   'Dot access looks for a key literally named "k".'),
                _q("`undefined?.x` is…", ["a crash", "undefined", "null", "0"], 1,
                   "Optional chaining stops safely."),
                _q("`0 || 5` and `0 ?? 5` are…", ["5 and 5", "0 and 0", "5 and 0", "0 and 5"], 2,
                   "|| treats 0 as falsy; ?? only replaces null/undefined."),
            ],
            exercises=[
                _ex("tscourse-w7-ac-1", "Key from a variable",
                    "Print the value of the field named by `k`.",
                    'const e = { desc: "coffee", amount: 3 };\nconst k = "amount";\nconsole.log(e[k]);\n',
                    'e[k]', [("", "3")],
                    hints=["Brackets use the value held in k.", "Write e[k]."]),
                _ex("tscourse-w7-ac-2", "Key from input",
                    "Read a field name from input and print that field's value.",
                    _FS + 'const e = { desc: "coffee", amount: 3 };\n'
                    'const k = fs.readFileSync(0, "utf8").trim();\nconsole.log(e[k]);\n',
                    'e[k]', [("desc", "coffee"), ("amount", "3")],
                    hints=["The key is only known when the program runs.",
                           "Write e[k]."]),
                _ex("tscourse-w7-ac-3", "Does it have one?",
                    "Print whether the object has a `paid` key.",
                    'const e = { desc: "coffee", amount: 3 };\nconsole.log("paid" in e);\n',
                    '"paid" in e', [("", "false")],
                    hints=["`in` tests for the key's presence.",
                           'Write "paid" in e.']),
                _ex("tscourse-w7-ac-4", "Safe deep read",
                    "Print the city, or `undefined` if there is no address — without crashing.",
                    'const u: { name: string; address?: { city: string } } = { name: "Ada" };\n'
                    'console.log(u.address?.city);\n',
                    'u.address?.city', [("", "undefined")],
                    hints=["Reading .city off a missing address would crash.",
                           "Write u.address?.city."],
                    difficulty="Medium"),
                _ex("tscourse-w7-ac-5", "A sensible fallback",
                    "Print the note, or `(none)` when there isn't one.",
                    'const e: { desc: string; note?: string } = { desc: "coffee" };\n'
                    'console.log(e.note ?? "(none)");\n',
                    'e.note ?? "(none)"', [("", "(none)")],
                    hints=["?? supplies a value only when the left side is null/undefined.",
                           'Write e.note ?? "(none)".']),
                _ex("tscourse-w7-ac-6", "Keep a real zero",
                    "Print the count, defaulting to 10 only when it is genuinely missing. Here it is 0, so 0 must print.",
                    'const e: { count?: number } = { count: 0 };\nconsole.log(e.count ?? 10);\n',
                    'e.count ?? 10', [("", "0")],
                    hints=["|| would throw the zero away.",
                           "Write e.count ?? 10."],
                    difficulty="Medium"),
                _fix("tscourse-w7-ac-fix1", "Fix the dot-versus-bracket",
                     "This should print 3 but prints undefined. Fix it.",
                     'const e = { desc: "coffee", amount: 3 };\nconst k = "amount";\nconsole.log(e.k);\n',
                     'const e = { desc: "coffee", amount: 3 };\nconst k = "amount";\nconsole.log(e[k]);\n',
                     [("", "3")],
                     hints=['e.k looks for a key spelled "k", which does not exist.',
                            "Use brackets so the VALUE of k is the key."],
                     difficulty="Medium"),
                _fix("tscourse-w7-ac-fix2", "Fix the swallowed zero",
                     "A count of 0 is real data, but this prints 10. Fix it.",
                     'const e: { count?: number } = { count: 0 };\nconsole.log(e.count || 10);\n',
                     'const e: { count?: number } = { count: 0 };\nconsole.log(e.count ?? 10);\n',
                     [("", "0")],
                     hints=["0 is falsy, so || replaces it.",
                            "?? only falls back for null and undefined."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`obj[k]` uses as the key…",
                   ['the letter "k"', "the value stored in k", "index k", "nothing"], 1,
                   "That is the whole point of bracket access."),
                _q("Prefer `??` over `||` when…",
                   ["always", "the fallback is for a MISSING value and 0 or \"\" are legitimate",
                    "never", "comparing booleans"], 1,
                   "Otherwise real zeros and empty strings get replaced."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w7-nested", "Nested data",
            "Objects inside objects, arrays inside objects.",
            """
A field's value can be another object, or an array. Real data nests:

```ts
const user = {
  name: "Ada",
  address: { city: "London", postcode: "E1" },
  tags: ["engineer", "founder"],
};
```

Read it by chaining, left to right:

```ts
user.address.city     // "London"
user.tags[0]          // "engineer"
user.tags.length      // 2
```

`user.address.city` means: take `user`, take its `address` (an object), take
that object's `city`. Each step must actually exist — if `address` were missing,
the second step crashes, which is exactly what `?.` is for.

**Arrays of objects, with objects inside them**, are entirely normal:

```ts
const orders = [
  { id: 1, customer: { name: "Ada" }, items: ["pen", "ink"] },
  { id: 2, customer: { name: "Bo" },  items: ["pad"] },
];

orders[0].customer.name     // "Ada"
orders[1].items.length      // 1
```

**Building nested data from input** is the everyday task. Given a line per
record:

```
coffee 3
book 12
```

split into lines, then split each line:

```ts
const rows = fs.readFileSync(0, "utf8").trim().split("\\n");
const items = rows.map((line) => {
  const parts = line.trim().split(" ");
  return { desc: parts[0], amount: Number(parts[1]) };
});
```

That callback has braces, so it needs an explicit `return` — the arrow trap
again. (An alternative is to wrap the object in parentheses:
`(line) => ({ desc: ... })`, which tells TypeScript the braces are an *object*
and not a function body. Both work; the explicit `return` is easier to read.)

**Depth is a cost.** `a.b.c.d.e` is fragile: five things must exist, and one
rename anywhere breaks it. Pull intermediate values into named variables when a
chain gets long.

> ⚠️ **Common mistakes:** reading through a missing level and crashing;
> forgetting `return` in a braced `map` callback that builds an object; and
> forgetting that a nested array still needs `[i]`, not `.i`.
""",
            warmup=[
                _q('`{a: {b: 2}}.a.b` is…', ["undefined", "2", "{b: 2}", "an error"], 1,
                   "Chain left to right."),
                _q('`{tags: ["x","y"]}.tags[1]` is…', ['"x"', '"y"', "1", "undefined"], 1,
                   "Index the array after reaching it."),
                _q('`{a: 1}.b.c` does what?',
                   ["gives undefined", "crashes", "gives null", "gives 1"], 1,
                   "`.b` is undefined, and reading `.c` off undefined throws."),
                _q("`(line) => { desc: line }` returns…",
                   ["an object", "undefined", "a string", "an error"], 1,
                   "The braces read as a function body, not an object literal."),
            ],
            exercises=[
                _ex("tscourse-w7-ne-1", "Reach into a nested object",
                    "Print the user's city.",
                    'const user = { name: "Ada", address: { city: "London" } };\n'
                    'console.log(user.address.city);\n',
                    'user.address.city', [("", "London")],
                    hints=["Chain the dots left to right."]),
                _ex("tscourse-w7-ne-2", "An array inside an object",
                    "Print how many tags the user has.",
                    'const user = { name: "Ada", tags: ["engineer", "founder"] };\n'
                    'console.log(user.tags.length);\n',
                    'user.tags.length', [("", "2")],
                    hints=["Reach the array, then take its length."]),
                _ex("tscourse-w7-ne-3", "Into a list of records",
                    "Print the name of the customer on the SECOND order.",
                    'const orders = [\n'
                    '  { id: 1, customer: { name: "Ada" } },\n'
                    '  { id: 2, customer: { name: "Bo" } },\n'
                    '];\n'
                    'console.log(orders[1].customer.name);\n',
                    'orders[1].customer.name', [("", "Bo")],
                    hints=["Index the array first, then chain the dots.",
                           "Write orders[1].customer.name."],
                    difficulty="Medium"),
                _ex("tscourse-w7-ne-4", "Records from input",
                    "Each input line is `desc amount`. Build the records and print the first description.",
                    _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const items = rows.map((line) => {\n'
                    '  const parts = line.trim().split(" ");\n'
                    '  return { desc: parts[0], amount: Number(parts[1]) };\n'
                    '});\n'
                    'console.log(items[0].desc);\n',
                    'return { desc: parts[0], amount: Number(parts[1]) };',
                    [("coffee 3\nbook 12", "coffee"), ("rent 900", "rent")],
                    hints=["The callback has braces, so it needs an explicit return.",
                           "Return { desc: parts[0], amount: Number(parts[1]) };"],
                    difficulty="Medium"),
                _ex("tscourse-w7-ne-5", "Total from built records",
                    "Each line is `desc amount`. Print the total of the amounts.",
                    _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const items = rows.map((line) => {\n'
                    '  const parts = line.trim().split(" ");\n'
                    '  return { desc: parts[0], amount: Number(parts[1]) };\n'
                    '});\n'
                    'let total = 0;\nfor (const it of items) {\n  total += it.amount;\n}\n'
                    'console.log(total);\n',
                    'total += it.amount;',
                    [("coffee 3\nbook 12", "15"), ("rent 900", "900")],
                    hints=["Accumulate the amount field across the records.",
                           "Write total += it.amount;"],
                    difficulty="Medium"),
                _fix("tscourse-w7-ne-fix1", "Fix the object-literal callback",
                     "This should print `coffee` but prints `undefined` — the callback returns nothing. Fix it.",
                     _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                     'const items = rows.map((line) => {\n'
                     '  const parts = line.trim().split(" ");\n'
                     '  ({ desc: parts[0], amount: Number(parts[1]) });\n'
                     '});\n'
                     'console.log(items[0]?.desc);\n',
                     _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                     'const items = rows.map((line) => {\n'
                     '  const parts = line.trim().split(" ");\n'
                     '  return { desc: parts[0], amount: Number(parts[1]) };\n'
                     '});\n'
                     'console.log(items[0]?.desc);\n',
                     [("coffee 3", "coffee"), ("book 12\nrent 900", "book")],
                     hints=["The object is built and then thrown away.",
                            "Add return in front of it."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`a.b.c` crashes when…",
                   ["c is missing", "b is missing", "a is missing", "b is missing or a is missing"], 3,
                   "You can read a missing FINAL field safely; reading THROUGH a missing one throws."),
                _q("To return an object from a braceless arrow you write…",
                   ["(x) => { a: x }", "(x) => ({ a: x })", "(x) => a: x", "impossible"], 1,
                   "The parentheses tell TypeScript the braces are an object literal."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w7-funcs", "Objects & functions",
            "Passing records in, handing records back, destructuring.",
            """
Functions take and return objects like any other value. The parameter's type is
written as the shape itself:

```ts
function lineTotal(e: { amount: number; qty: number }): number {
  return e.amount * e.qty;
}
lineTotal({ amount: 3, qty: 4 });   // 12
```

Note the shape uses `;` between fields (a semicolon inside a *type*, a comma
inside a *value* — an inconsistency worth simply memorising).

**Returning an object** lets a function hand back several values at once:

```ts
function stats(a: number[]): { count: number; total: number } {
  let total = 0;
  for (const x of a) total += x;
  return { count: a.length, total };
}
const s = stats([1, 2, 3]);
console.log(s.total);    // 6
```

That's the answer to "how do I return two things?" — return one object with two
fields.

**Destructuring** pulls fields out into local names:

```ts
const e = { desc: "coffee", amount: 3 };
const { desc, amount } = e;
console.log(desc, amount);      // coffee 3
```

It works on **parameters** too, which is where it earns its keep — the function
signature then lists exactly what it uses:

```ts
function label({ desc, amount }: { desc: string; amount: number }): string {
  return `${desc}: $${amount}`;
}
```

Compare with `e.desc` and `e.amount` repeated through a long body. Destructuring
names them once.

You can rename and default while destructuring:

```ts
const { desc: name, note = "(none)" } = e;
```

**Objects are passed by reference.** A function receives the *same* object, so
changing a field inside is visible to the caller:

```ts
function bump(o: { n: number }): void { o.n += 1; }
const p = { n: 1 };
bump(p);
console.log(p.n);    // 2  ⚠️
```

That's a side effect of exactly the kind week 5 warned about. Prefer returning a
**new** object:

```ts
function bumped(o: { n: number }): { n: number } { return { ...o, n: o.n + 1 }; }
```

> ⚠️ **Common mistakes:** using `,` instead of `;` in an inline shape type;
> mutating a parameter object and surprising the caller; and forgetting that
> destructuring copies the *value* — for a nested object, that value is still a
> shared reference.
""",
            warmup=[
                _q("`function f(e: { a: number }): number { return e.a; } f({a: 7})` is…",
                   ["7", "undefined", "{a:7}", "an error"], 0, "It reads the field."),
                _q("`const { a } = { a: 1, b: 2 };` leaves `a` as…",
                   ["1", "2", "{a:1}", "undefined"], 0, "Destructuring pulls out the field."),
                _q("A function that mutates its object parameter…",
                   ["cannot", "changes the caller's object too", "makes a copy",
                    "returns it"], 1,
                   "Objects are handed over by reference."),
                _q("How do you return two values from a function?",
                   ["you cannot", "return an object with two fields", "return twice",
                    "use a global"], 1,
                   "One object, several fields."),
            ],
            exercises=[
                _ex("tscourse-w7-fu-1", "Take an object",
                    "Return the line total from the record's amount and qty.",
                    'function lineTotal(e: { amount: number; qty: number }): number {\n'
                    '  return e.amount * e.qty;\n}\n'
                    'console.log(lineTotal({ amount: 3, qty: 4 }));\n',
                    'e.amount * e.qty', [("", "12")],
                    hints=["Multiply the two fields."]),
                _ex("tscourse-w7-fu-2", "Return an object",
                    "Return a record holding the count and the total.",
                    'function stats(a: number[]): { count: number; total: number } {\n'
                    '  let total = 0;\n  for (const x of a) {\n    total += x;\n  }\n'
                    '  return { count: a.length, total };\n}\n'
                    'const s = stats([1, 2, 3]);\nconsole.log(`${s.count} ${s.total}`);\n',
                    'return { count: a.length, total };', [("", "3 6")],
                    hints=["Bundle both answers into one object; `total` can use shorthand.",
                           "Write return { count: a.length, total };"],
                    difficulty="Medium"),
                _ex("tscourse-w7-fu-3", "Destructure a record",
                    "Pull `desc` and `amount` out of the record in one line, then print them.",
                    'const e = { desc: "coffee", amount: 3 };\n'
                    'const { desc, amount } = e;\n'
                    'console.log(`${desc} ${amount}`);\n',
                    'const { desc, amount } = e;', [("", "coffee 3")],
                    hints=["Braces on the LEFT of = destructure.",
                           "Write const { desc, amount } = e;"]),
                _ex("tscourse-w7-fu-4", "Destructure a parameter",
                    "Destructure the parameter so the body can use `desc` and `amount` directly.",
                    'function label({ desc, amount }: { desc: string; amount: number }): string {\n'
                    '  return `${desc}: $${amount}`;\n}\n'
                    'console.log(label({ desc: "coffee", amount: 3 }));\n',
                    '{ desc, amount }', [("", "coffee: $3")],
                    hints=["The destructuring pattern goes where the parameter name would.",
                           "Write { desc, amount } before the type annotation."],
                    difficulty="Medium"),
                _ex("tscourse-w7-fu-5", "Return a changed copy",
                    "Return a NEW record with n increased by one, leaving the original alone.",
                    'function bumped(o: { n: number }): { n: number } {\n'
                    '  return { ...o, n: o.n + 1 };\n}\n'
                    'const p = { n: 1 };\nconst q = bumped(p);\nconsole.log(`${p.n} ${q.n}`);\n',
                    'return { ...o, n: o.n + 1 };', [("", "1 2")],
                    hints=["Spread the old fields, then override the one that changes.",
                           "Write return { ...o, n: o.n + 1 };"],
                    difficulty="Medium"),
                _fix("tscourse-w7-fu-fix1", "Fix the field access",
                     "This should print the first name but reads the wrong field. Fix it.",
                     'function first(p: { first: string; last: string }): string {\n  return p.last;\n}\n'
                     'console.log(first({ first: "Ada", last: "Lovelace" }));\n',
                     'function first(p: { first: string; last: string }): string {\n  return p.first;\n}\n'
                     'console.log(first({ first: "Ada", last: "Lovelace" }));\n',
                     [("", "Ada")],
                     hints=["It returns p.last.", "Return p.first."]),
                _fix("tscourse-w7-fu-fix2", "Fix the surprise mutation",
                     "The caller's object should be untouched — expected `1 2` — but this prints `2 2`. Fix it.",
                     'function bumped(o: { n: number }): { n: number } {\n  o.n = o.n + 1;\n  return o;\n}\n'
                     'const p = { n: 1 };\nconst q = bumped(p);\nconsole.log(`${p.n} ${q.n}`);\n',
                     'function bumped(o: { n: number }): { n: number } {\n  return { ...o, n: o.n + 1 };\n}\n'
                     'const p = { n: 1 };\nconst q = bumped(p);\nconsole.log(`${p.n} ${q.n}`);\n',
                     [("", "1 2")],
                     hints=["The function is handed the caller's own object and edits it.",
                            "Build and return a new one instead: { ...o, n: o.n + 1 }."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Inside an inline shape type, fields are separated by…",
                   [",", ";", ":", "nothing"], 1,
                   "Semicolons in a type, commas in a value."),
                _q("Destructuring a parameter mainly buys you…",
                   ["speed", "a signature that names exactly what the function uses",
                    "type safety", "immutability"], 1,
                   "It documents the function's real dependencies."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w7-records", "Arrays of records",
            "The shape of real datasets.",
            """
Put last week's array methods together with this week's objects and you can
answer real questions about real data:

```ts
const people = [
  { name: "Ada", age: 36 },
  { name: "Bo",  age: 20 },
  { name: "Cy",  age: 47 },
];
```

**Total a field** — a loop and an accumulator:

```ts
let total = 0;
for (const p of people) total += p.age;
```

**Select rows** — `filter` with a predicate on a field:

```ts
people.filter((p) => p.age >= 21);      // Ada and Cy
```

**Pull out one column** — `map` to a field:

```ts
people.map((p) => p.name);              // ["Ada","Bo","Cy"]
people.map((p) => p.name).join(", ");   // "Ada, Bo, Cy"
```

**Find one row:**

```ts
people.find((p) => p.name === "Bo");        // the record, or undefined
people.some((p) => p.age > 40);             // true
```

**Sort by a field** — the week 6 comparator, reading a field from each side:

```ts
[...people].sort((p, q) => p.age - q.age);            // youngest first
[...people].sort((p, q) => q.age - p.age);            // oldest first
[...people].sort((p, q) => p.name.localeCompare(q.name));  // by name
```

`localeCompare` returns a negative/zero/positive number comparing two strings —
exactly the comparator contract. And the copy (`[...people]`) matters just as
much here: sorting in place reorders the array everyone else is holding.

**Chaining reads like a sentence** once you're used to it:

```ts
people
  .filter((p) => p.age >= 21)
  .map((p) => p.name)
  .join(", ");                    // "Ada, Cy"
```

Filter, then map, then join: narrow the rows, pick the column, print it.

> ⚠️ **Common mistakes:** reading a field that doesn't exist and totalling
> `NaN`; sorting in place and corrupting the source array; and mapping before
> filtering, which does more work than necessary.
""",
            warmup=[
                _q("Totalling `age` over [{age:1},{age:2},{age:3}] gives…",
                   ["3", "6", "123", "an error"], 1, "1+2+3."),
                _q("`[{a:1},{a:2}].filter((o) => o.a > 1).length` is…",
                   ["0", "1", "2", "an error"], 1, "Only {a:2} passes."),
                _q("`[{n:\"x\"},{n:\"y\"}].map((o) => o.n).join(\"-\")` is…",
                   ['"x-y"', '"xy"', '["x","y"]', '"x, y"'], 0,
                   "Pull the column, then glue it."),
                _q("Totalling a MISSPELLED field over records gives…",
                   ["0", "NaN", "undefined", "an error"], 1,
                   "undefined + a number is NaN, and NaN spreads."),
            ],
            exercises=[
                _ex("tscourse-w7-re-1", "Total a column",
                    "Sum everyone's age and print it.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                    'let total = 0;\nfor (const p of people) {\n  total += p.age;\n}\nconsole.log(total);\n',
                    'total += p.age;', [("", "56")],
                    hints=["Accumulate the age field."]),
                _ex("tscourse-w7-re-2", "Count matching rows",
                    "Count people aged 21 or older.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n  { name: "Cy", age: 47 },\n];\n'
                    'console.log(people.filter((p) => p.age >= 21).length);\n',
                    'p.age >= 21', [("", "2")],
                    hints=["21 itself counts, so the test is >=."]),
                _ex("tscourse-w7-re-3", "Pull a column",
                    "Print everyone's name, comma-separated.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                    'console.log(people.map((p) => p.name).join(", "));\n',
                    'people.map((p) => p.name)', [("", "Ada, Bo")],
                    hints=["map to the field, then join.",
                           "Write people.map((p) => p.name)."]),
                _ex("tscourse-w7-re-4", "Find a row",
                    "Print Bo's age, found by name.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                    'const bo = people.find((p) => p.name === "Bo");\nconsole.log(bo?.age);\n',
                    'people.find((p) => p.name === "Bo")', [("", "20")],
                    hints=["find returns the record itself, or undefined.",
                           'Write people.find((p) => p.name === "Bo").'],
                    difficulty="Medium"),
                _ex("tscourse-w7-re-5", "Sort by a field",
                    "Print the names youngest first, comma-separated.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n  { name: "Cy", age: 47 },\n];\n'
                    'console.log([...people].sort((p, q) => p.age - q.age).map((p) => p.name).join(", "));\n',
                    '(p, q) => p.age - q.age', [("", "Bo, Ada, Cy")],
                    hints=["Same comparator rule as week 6, reading a field from each side.",
                           "Write (p, q) => p.age - q.age."],
                    difficulty="Medium"),
                _ex("tscourse-w7-re-6", "Filter then map",
                    "Print the names of everyone 21 or older, comma-separated.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n  { name: "Cy", age: 47 },\n];\n'
                    'console.log(people.filter((p) => p.age >= 21).map((p) => p.name).join(", "));\n',
                    '.filter((p) => p.age >= 21).map((p) => p.name)',
                    [("", "Ada, Cy")],
                    hints=["Narrow the rows first, then pick the column.",
                           "Chain .filter(...) then .map(...)."],
                    difficulty="Medium"),
                _fix("tscourse-w7-re-fix1", "Fix the wrong field",
                     "This should total ages (56) but prints NaN. Fix it.",
                     'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                     'let total = 0;\nfor (const p of people) {\n  total += p.years;\n}\nconsole.log(total);\n',
                     'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                     'let total = 0;\nfor (const p of people) {\n  total += p.age;\n}\nconsole.log(total);\n',
                     [("", "56")],
                     hints=["There is no `years` field, so each read is undefined — and 0 + undefined is NaN.",
                            "The field is `age`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Which order does less work?",
                   ["map then filter", "filter then map", "identical", "neither works"], 1,
                   "Filtering first leaves fewer elements to transform."),
                _q("`[...rows].sort(...)` rather than `rows.sort(...)` because…",
                   ["it is faster", "sort mutates, and other code may be holding rows",
                    "sort needs a copy", "no reason"], 1,
                   "The same rule as week 6."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w7-copy", "Sharing, copying & spread",
            "Why changing one object changed another.",
            """
An object variable does not hold the object. It holds a **reference** — the
address of one. Assigning copies the address, not the object:

```ts
const a = { n: 1 };
const b = a;        // b points at THE SAME object
b.n = 9;
console.log(a.n);   // 9   ⚠️
```

Both names sit in front of one object. This is called **aliasing**, and it is
behind a whole family of bugs that feel like magic: a value changes and nothing
nearby touched it.

**Comparison follows the same rule.** `===` on objects asks "the same object?",
not "the same contents?":

```ts
{ n: 1 } === { n: 1 }     // false — two different objects
const a = { n: 1 }; a === a   // true
```

**Copying** uses spread:

```ts
const c = { ...a };            // a fresh object with the same fields
const d = { ...a, n: 9 };      // copy, with n replaced
```

`{ ...a, n: 9 }` is the everyday "change one field without mutating" move —
later fields win, so the override goes last. It's how you'll update state in
almost any modern framework.

**The copy is shallow.** Spread copies each field's *value* — and for a nested
object, that value is another reference:

```ts
const u = { name: "Ada", address: { city: "London" } };
const v = { ...u };
v.address.city = "Paris";
console.log(u.address.city);    // "Paris"  ⚠️ still shared
```

The top level is fresh; anything nested is not. To copy a level down, spread
that level too:

```ts
const v = { ...u, address: { ...u.address } };
```

For deeply nested data, `structuredClone(u)` copies the whole tree.

**The same is true of arrays of objects.** `[...rows]` gives you a new array
holding the *same* record objects — reordering it is safe, editing a record
through it is not.

> ⚠️ **Common mistakes:** expecting `=` to copy; comparing objects with `===`
> and expecting contents to be compared; and trusting a shallow copy to protect
> nested data.
""",
            warmup=[
                _q("`const a={n:1}; const b=a; b.n=9; a.n` is…", ["1", "9", "undefined", "an error"], 1,
                   "One object, two names."),
                _q("`({n:1}) === ({n:1})` is…", ["true", "false"], 1,
                   "Different objects, so not identical — contents are not compared."),
                _q("`{ ...a, n: 9 }` produces…",
                   ["a mutated a", "a copy with n replaced", "an error", "just {n:9}"], 1,
                   "Later fields override earlier ones."),
                _q("After `const v = { ...u }`, changing `v.address.city` affects `u` because…",
                   ["spread is broken", "the copy is shallow — nested objects are still shared",
                    "address is const", "it does not"], 1,
                   "Only the top level was duplicated."),
            ],
            exercises=[
                _ex("tscourse-w7-cp-1", "Make a real copy",
                    "Copy the object so changing the copy leaves the original at 1.",
                    'const a = { n: 1 };\nconst b = { ...a };\nb.n = 9;\nconsole.log(`${a.n} ${b.n}`);\n',
                    'const b = { ...a };', [("", "1 9")],
                    hints=["Assignment shares; spread copies.",
                           "Write const b = { ...a };"]),
                _ex("tscourse-w7-cp-2", "Copy with an override",
                    "Build a new record with the same fields but amount 9.",
                    'const e = { desc: "coffee", amount: 3 };\n'
                    'const f = { ...e, amount: 9 };\n'
                    'console.log(`${f.desc} ${f.amount} ${e.amount}`);\n',
                    '{ ...e, amount: 9 }', [("", "coffee 9 3")],
                    hints=["Spread first, then name the field you want different.",
                           "Write { ...e, amount: 9 }."],
                    difficulty="Medium"),
                _ex("tscourse-w7-cp-3", "Compare identity",
                    "Print whether the two separately-built objects are the same object.",
                    'const a = { n: 1 };\nconst b = { n: 1 };\nconsole.log(a === b);\n',
                    'a === b', [("", "false")],
                    hints=["=== on objects asks about identity, not contents."]),
                _ex("tscourse-w7-cp-4", "Copy one level down",
                    "Copy the user so changing the copy's city leaves the original as London.",
                    'const u = { name: "Ada", address: { city: "London" } };\n'
                    'const v = { ...u, address: { ...u.address } };\n'
                    'v.address.city = "Paris";\n'
                    'console.log(`${u.address.city} ${v.address.city}`);\n',
                    '{ ...u, address: { ...u.address } }',
                    [("", "London Paris")],
                    hints=["A plain spread leaves address shared.",
                           "Spread the nested object too: { ...u, address: { ...u.address } }."],
                    difficulty="Medium"),
                _ex("tscourse-w7-cp-5", "Copy an array of records",
                    "Sort a copy by amount so the original order survives.",
                    'const rows = [{ n: "a", v: 2 }, { n: "b", v: 1 }];\n'
                    'const sorted = [...rows].sort((p, q) => p.v - q.v);\n'
                    'console.log(sorted.map((r) => r.n).join(""));\n'
                    'console.log(rows.map((r) => r.n).join(""));\n',
                    '[...rows].sort((p, q) => p.v - q.v)', [("", "ba\nab")],
                    hints=["Spread the array before sorting it.",
                           "Write [...rows].sort((p, q) => p.v - q.v)."],
                    difficulty="Medium"),
                _fix("tscourse-w7-cp-fix1", "Fix the shared object",
                     "This should print `1 9` but prints `9 9`. Fix it.",
                     'const a = { n: 1 };\nconst b = a;\nb.n = 9;\nconsole.log(`${a.n} ${b.n}`);\n',
                     'const a = { n: 1 };\nconst b = { ...a };\nb.n = 9;\nconsole.log(`${a.n} ${b.n}`);\n',
                     [("", "1 9")],
                     hints=["`const b = a;` gives the same object a second name.",
                            "Spread to build a fresh one."],
                     difficulty="Medium"),
                _fix("tscourse-w7-cp-fix2", "Fix the shallow copy",
                     "This should print `London Paris` but prints `Paris Paris`. Fix it.",
                     'const u = { name: "Ada", address: { city: "London" } };\n'
                     'const v = { ...u };\nv.address.city = "Paris";\n'
                     'console.log(`${u.address.city} ${v.address.city}`);\n',
                     'const u = { name: "Ada", address: { city: "London" } };\n'
                     'const v = { ...u, address: { ...u.address } };\nv.address.city = "Paris";\n'
                     'console.log(`${u.address.city} ${v.address.city}`);\n',
                     [("", "London Paris")],
                     hints=["Spread copies only the top level; address is still the same object.",
                            "Spread the nested object as well."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("An object variable holds…",
                   ["the object", "a reference to the object", "a copy", "a name"], 1,
                   "Which is why assignment shares rather than copies."),
                _q("`{ ...a, x: 1 }` versus `{ x: 1, ...a }` — the difference is…",
                   ["none", "which one wins: the LAST mention of a field",
                    "the first is invalid", "the second is faster"], 1,
                   "In the second, a's own x would override the 1."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w7-tally", "Objects as lookup tables",
            "Counting, grouping, and looking things up by name.",
            """
So far objects have modelled *one thing* with a fixed set of fields. They have a
second life: as a **lookup table** from arbitrary names to values.

```ts
const prices: { [key: string]: number } = {
  coffee: 3.25,
  book: 12,
};
prices["coffee"];    // 3.25
```

That annotation — `{ [key: string]: number }` — is an **index signature**. It
says *"any string key, and every value is a number"*. Use it when the keys are
data rather than a fixed schema.

**Counting** is the classic use, and worth knowing cold:

```ts
const counts: { [key: string]: number } = {};
for (const w of words) {
  counts[w] = (counts[w] ?? 0) + 1;
}
```

The `?? 0` carries the whole idea. The first time a word appears, `counts[w]` is
`undefined`, and `undefined + 1` is `NaN`. The fallback supplies the starting
value. (`|| 0` happens to work here too, since a count of 0 never survives, but
`??` states the intent: *only* when missing.)

**Why an object rather than searching an array?** Looking a key up in an object
is effectively instant no matter how many keys there are, where scanning an
array to find a match takes longer as it grows. Counting a million words with an
array of pairs would be unusably slow; with an object it's immediate. You'll
give this a name — O(1) versus O(n) — in Month 6.

**Reading a table back out:**

```ts
Object.keys(counts)      // ["a", "b"]
Object.values(counts)    // [2, 1]
Object.entries(counts)   // [["a", 2], ["b", 1]]
```

`entries` gives an array of `[key, value]` pairs, which you can then sort or map
like any array:

```ts
Object.entries(counts)
  .sort((p, q) => q[1] - p[1])          // by count, descending
  .map((p) => `${p[0]}:${p[1]}`)
  .join(", ");
```

`p[0]` is the key and `p[1]` the value. You can destructure the pair instead,
which reads better: `.map(([k, v]) => `${k}:${v}`)`.

**Grouping** is the same move with arrays as the values:

```ts
const byTag: { [key: string]: string[] } = {};
for (const e of expenses) {
  if (byTag[e.tag] === undefined) byTag[e.tag] = [];
  byTag[e.tag].push(e.desc);
}
```

Make sure the bucket exists, then push into it. (`Map` — a purpose-built
alternative — arrives in week 18.)

> ⚠️ **Common mistakes:** forgetting `?? 0` and getting `NaN`; forgetting to
> create the empty array before pushing; and assuming key order is meaningful
> (it mostly follows insertion order for string keys, but don't rely on it —
> sort explicitly).
""",
            warmup=[
                _q("`counts[w] = counts[w] + 1;` on a brand-new word gives…",
                   ["1", "0", "NaN", "an error"], 2,
                   "undefined + 1 is NaN — hence the ?? 0."),
                _q("`Object.keys({a:1,b:2})` is…",
                   ['["a","b"]', "[1,2]", "2", '[["a",1],["b",2]]'], 0, "The key names."),
                _q("`Object.entries({a:1})` is…",
                   ['["a",1]', '[["a",1]]', '{a:1}', '["a"]'], 1,
                   "An array of [key, value] pairs — one pair here."),
                _q("Looking a key up in an object versus scanning an array…",
                   ["the array is faster", "the object stays fast as it grows",
                    "identical", "objects cannot be searched"], 1,
                   "Key lookup does not get slower with size."),
            ],
            exercises=[
                _ex("tscourse-w7-ta-1", "A price table",
                    "Look up the price of the word given on input.",
                    _FS + 'const prices: { [key: string]: number } = { coffee: 3.25, book: 12 };\n'
                    'const k = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(prices[k]);\n',
                    'prices[k]', [("coffee", "3.25"), ("book", "12")],
                    hints=["Bracket access with the runtime key."]),
                _ex("tscourse-w7-ta-2", "Count the words",
                    "Count how many times each word appears, then print the count for `a`.",
                    _WORDS + 'const counts: { [key: string]: number } = {};\n'
                    'for (const w of words) {\n  counts[w] = (counts[w] ?? 0) + 1;\n}\n'
                    'console.log(counts["a"] ?? 0);\n',
                    'counts[w] = (counts[w] ?? 0) + 1;',
                    [("a b a c a", "3"), ("b c", "0")],
                    hints=["The first sighting of a word has no existing count.",
                           "Write counts[w] = (counts[w] ?? 0) + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w7-ta-3", "How many distinct",
                    "Print how many DISTINCT words the input contains.",
                    _WORDS + 'const seen: { [key: string]: boolean } = {};\n'
                    'for (const w of words) {\n  seen[w] = true;\n}\n'
                    'console.log(Object.keys(seen).length);\n',
                    'Object.keys(seen).length',
                    [("a b a c a", "3"), ("x", "1")],
                    hints=["Each distinct word becomes one key.",
                           "Count the keys: Object.keys(seen).length."],
                    difficulty="Medium"),
                _ex("tscourse-w7-ta-4", "Read the table out",
                    "Print each word and its count as `a:3` lines, sorted alphabetically by word.",
                    _WORDS + 'const counts: { [key: string]: number } = {};\n'
                    'for (const w of words) {\n  counts[w] = (counts[w] ?? 0) + 1;\n}\n'
                    'for (const k of Object.keys(counts).sort()) {\n  console.log(`${k}:${counts[k]}`);\n}\n',
                    'Object.keys(counts).sort()',
                    [("b a a", "a:2\nb:1"), ("x", "x:1")],
                    hints=["Key order is not guaranteed, so sort the keys explicitly.",
                           "Write Object.keys(counts).sort()."],
                    difficulty="Medium"),
                _ex("tscourse-w7-ta-5", "The most common word",
                    "Print the most frequent word. On a tie, the alphabetically first wins.",
                    _WORDS + 'const counts: { [key: string]: number } = {};\n'
                    'for (const w of words) {\n  counts[w] = (counts[w] ?? 0) + 1;\n}\n'
                    'const best = Object.keys(counts).sort().sort((p, q) => counts[q] - counts[p])[0];\n'
                    'console.log(best);\n',
                    '(p, q) => counts[q] - counts[p]',
                    [("a b a c a", "a"), ("b b c c", "b"), ("z", "z")],
                    hints=["Sort alphabetically first, then re-sort by count descending — sort is stable, so ties keep the alphabetical order.",
                           "The count comparator is (p, q) => counts[q] - counts[p]."],
                    difficulty="Medium"),
                _fix("tscourse-w7-ta-fix1", "Fix the NaN count",
                     "This should print 3 for `a b a c a` but prints NaN. Fix it.",
                     _WORDS + 'const counts: { [key: string]: number } = {};\n'
                     'for (const w of words) {\n  counts[w] = counts[w] + 1;\n}\n'
                     'console.log(counts["a"]);\n',
                     _WORDS + 'const counts: { [key: string]: number } = {};\n'
                     'for (const w of words) {\n  counts[w] = (counts[w] ?? 0) + 1;\n}\n'
                     'console.log(counts["a"]);\n',
                     [("a b a c a", "3"), ("a", "1")],
                     hints=["The first time a word is seen, its count is undefined.",
                            "Supply a starting value: (counts[w] ?? 0) + 1."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`{ [key: string]: number }` describes…",
                   ["one field called key", "any string key, with number values",
                    "an array", "a function"], 1,
                   "An index signature, for tables whose keys are data."),
                _q("Why `?? 0` in a tally?",
                   ["style", "the first occurrence has no existing count",
                    "to reset", "for speed"], 1,
                   "Otherwise undefined + 1 is NaN."),
                _q("To group values under a key you must first…",
                   ["sort", "make sure the bucket array exists", "count them",
                    "use an array"], 1,
                   "Pushing onto undefined throws."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w7-group", "Grouping & summarising",
            "Bucket records by a key, then report each bucket.",
            """
A tally answers *how many of each*. **Grouping** answers the bigger question:
*which ones, in each bucket* — and once you have the buckets you can summarise
them any way you like. It is the single most common shape of real reporting
code, and it is three lines of pattern.

**The bucket pattern.** The table's values are arrays instead of numbers:

```ts
const byLetter: { [key: string]: string[] } = {};

for (const w of ["ant", "bee", "ape", "bat"]) {
  const key = w[0];
  if (!(key in byLetter)) byLetter[key] = [];   // create the bucket once
  byLetter[key].push(w);                        // then always push
}
// { a: ["ant", "ape"], b: ["bee", "bat"] }
```

Those two lines never change. The only decision you make is **what the key is** —
`w[0]` here, `expense.category` in Budget Buddy, `user.country` at work.

The same idea with the `??` fallback from the previous lesson:

```ts
byLetter[key] = byLetter[key] ?? [];
byLetter[key].push(w);
```

Both are fine. Pick one and use it everywhere.

**Then walk the buckets.** `Object.keys` gives you the keys, and `.sort()` makes
the report **deterministic** — the same input always prints in the same order,
which is what makes output testable:

```ts
for (const key of Object.keys(byLetter).sort()) {
  const bucket = byLetter[key];
  console.log(`${key}: ${bucket.length} — ${bucket.join(", ")}`);
}
```

**Summarising a bucket** is ordinary array work on `byLetter[key]`: count with
`.length`, total with a running sum, best with a running maximum.

```ts
const totals: { [key: string]: number } = {};
for (const s of sales) {
  totals[s.region] = (totals[s.region] ?? 0) + s.amount;   // sum straight in
}
```

Notice the choice: bucket into **arrays** when you still need the individual
items later, and accumulate into **numbers** when you only ever want the total.
Grouping keeps your options open; accumulating is cheaper.

**Grouping is one pass.** Resist the urge to loop once per category — you'd have
to know the categories in advance, and you'd read the data as many times as
there are keys. One pass over the records builds every bucket at once, whatever
the categories turn out to be.

> ⚠️ **Common mistakes:** pushing into a bucket that was never created (a crash
> on `undefined.push`); *assigning* `groups[key] = [item]` instead of pushing, so
> each bucket only ever holds the last item; and adding to a missing numeric
> bucket, where `undefined + 1` quietly gives you `NaN`.
""",
            warmup=[
                _q("After bucketing `[\"ant\",\"ape\"]` by first letter, `groups[\"a\"]` is…",
                   ['"ape"', '["ant", "ape"]', '2', 'undefined'], 1,
                   "The value is an array holding every item that matched the key."),
                _q("`groups[key].push(w)` without creating the bucket first…",
                   ["works fine", "crashes, because groups[key] is undefined",
                    "creates the bucket automatically", "returns NaN"], 1,
                   "You cannot call .push on undefined."),
                _q("`totals[k] = totals[k] + 1` on a key seen for the first time gives…",
                   ["1", "0", "NaN", "undefined"], 2,
                   "undefined + 1 is NaN — supply a starting value with ?? 0."),
                _q("Why `.sort()` the keys before printing?",
                   ["it is faster", "so the report comes out in the same order every time",
                    "objects cannot be read otherwise", "it removes duplicates"], 1,
                   "Deterministic output is what makes a report testable."),
            ],
            exercises=[
                _ex("tscourse-w7-grp-1", "Create the bucket",
                    "Group the words by their first letter. Add the line that creates a bucket the first time a letter is seen.",
                    'const words = ["ant", "bee", "ape", "bat"];\n'
                    'const groups: { [key: string]: string[] } = {};\n'
                    'for (const w of words) {\n'
                    '  const key = w[0];\n'
                    '  if (!(key in groups)) groups[key] = [];\n'
                    '  groups[key].push(w);\n'
                    '}\n'
                    'console.log(Object.keys(groups).sort().join(","));\n'
                    'console.log(groups["a"].join(" "));\n',
                    'if (!(key in groups)) groups[key] = [];',
                    [("", "a,b\nant ape")],
                    hints=["Use the `in` operator to ask whether the key exists yet.",
                           "Write if (!(key in groups)) groups[key] = [];"]),
                _ex("tscourse-w7-grp-2", "Push into the bucket",
                    "The buckets are created; now add each expense's name to the bucket for its category.",
                    'const expenses = [\n'
                    '  { name: "coffee", category: "food" },\n'
                    '  { name: "novel", category: "books" },\n'
                    '  { name: "bread", category: "food" },\n'
                    '];\n'
                    'const groups: { [key: string]: string[] } = {};\n'
                    'for (const e of expenses) {\n'
                    '  groups[e.category] = groups[e.category] ?? [];\n'
                    '  groups[e.category].push(e.name);\n'
                    '}\n'
                    'console.log(groups["food"].join(" + "));\n',
                    'groups[e.category].push(e.name);',
                    [("", "coffee + bread")],
                    hints=["The bucket for this record is groups[e.category].",
                           "Push the name onto it: groups[e.category].push(e.name);"]),
                _ex("tscourse-w7-grp-3", "Walk the buckets in order",
                    "Print one line per category, alphabetically. Fill in how the keys are obtained and ordered.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const groups: { [key: string]: string[] } = {};\n'
                    'for (const line of lines) {\n'
                    '  const parts = line.trim().split(",");\n'
                    '  const cat = parts[0];\n'
                    '  groups[cat] = groups[cat] ?? [];\n'
                    '  groups[cat].push(parts[1]);\n'
                    '}\n'
                    'for (const cat of Object.keys(groups).sort()) {\n'
                    '  console.log(`${cat}: ${groups[cat].join(", ")}`);\n'
                    '}\n',
                    'Object.keys(groups).sort()',
                    [("fruit,apple\nveg,leek\nfruit,fig", "fruit: apple, fig\nveg: leek"),
                     ("b,two\na,one", "a: one\nb: two")],
                    hints=["Object.keys gives you the bucket names as an array.",
                           "Sorting that array makes the report order stable."],
                    difficulty="Easy"),
                _ex("tscourse-w7-grp-4", "Accumulate instead of bucketing",
                    "You only need the totals here, so add straight into a numeric table. Fill in the accumulating line.",
                    'const sales = [\n'
                    '  { region: "north", amount: 30 },\n'
                    '  { region: "south", amount: 20 },\n'
                    '  { region: "north", amount: 12 },\n'
                    '];\n'
                    'const totals: { [key: string]: number } = {};\n'
                    'for (const s of sales) {\n'
                    '  totals[s.region] = (totals[s.region] ?? 0) + s.amount;\n'
                    '}\n'
                    'for (const r of Object.keys(totals).sort()) {\n'
                    '  console.log(`${r} ${totals[r]}`);\n'
                    '}\n',
                    'totals[s.region] = (totals[s.region] ?? 0) + s.amount;',
                    [("", "north 42\nsouth 20")],
                    hints=["The first time a region appears there is no running total yet.",
                           "Fall back to 0 with ?? before adding the amount."],
                    difficulty="Easy"),
                _ex("tscourse-w7-grp-5", "Find the biggest bucket",
                    "Report which category holds the most items. Fill in the comparison.",
                    'const groups: { [key: string]: string[] } = {\n'
                    '  fruit: ["apple", "fig"],\n'
                    '  veg: ["leek"],\n'
                    '  drink: ["tea", "coffee", "cocoa"],\n'
                    '};\n'
                    'let best = "";\n'
                    'for (const k of Object.keys(groups).sort()) {\n'
                    '  if (best === "" || groups[k].length > groups[best].length) best = k;\n'
                    '}\n'
                    'console.log(`${best} (${groups[best].length})`);\n',
                    'groups[k].length > groups[best].length',
                    [("", "drink (3)")],
                    hints=["Compare this bucket's length against the best one found so far.",
                           "Write groups[k].length > groups[best].length."],
                    difficulty="Medium"),
                _fix("tscourse-w7-grp-fix1", "Fix the missing bucket",
                     "This should print `ant ape` but crashes on the first word, because nothing ever creates the bucket.",
                     'const words = ["ant", "bee", "ape"];\n'
                     'const groups: { [key: string]: string[] } = {};\n'
                     'for (const w of words) {\n'
                     '  groups[w[0]].push(w);\n'
                     '}\n'
                     'console.log(groups["a"].join(" "));\n',
                     'const words = ["ant", "bee", "ape"];\n'
                     'const groups: { [key: string]: string[] } = {};\n'
                     'for (const w of words) {\n'
                     '  groups[w[0]] = groups[w[0]] ?? [];\n'
                     '  groups[w[0]].push(w);\n'
                     '}\n'
                     'console.log(groups["a"].join(" "));\n',
                     [("", "ant ape")],
                     hints=["The very first time a letter appears, groups[letter] is undefined.",
                            "Create an empty array for it before pushing."]),
                _fix("tscourse-w7-grp-fix2", "Fix the overwritten bucket",
                     "This should print `ant ape` but prints only `ape`. Each record is replacing the bucket instead of joining it.",
                     'const groups: { [key: string]: string[] } = {};\n'
                     'const words = ["ant", "ape", "bee"];\n'
                     'for (const w of words) {\n'
                     '  if (!(w[0] in groups)) groups[w[0]] = [];\n'
                     '  groups[w[0]] = [w];\n'
                     '}\n'
                     'console.log(groups["a"].join(" "));\n',
                     'const groups: { [key: string]: string[] } = {};\n'
                     'const words = ["ant", "ape", "bee"];\n'
                     'for (const w of words) {\n'
                     '  if (!(w[0] in groups)) groups[w[0]] = [];\n'
                     '  groups[w[0]].push(w);\n'
                     '}\n'
                     'console.log(groups["a"].join(" "));\n',
                     [("", "ant ape")],
                     hints=["Assigning a fresh one-element array throws away everything already in the bucket.",
                            "Add to the existing bucket with .push(w) instead."],
                     difficulty="Medium"),
                _fix("tscourse-w7-grp-fix3", "Fix the NaN tally",
                     "This should print `2 1` but prints `NaN NaN`. The first addition has nothing to add to.",
                     'const tally: { [key: string]: number } = {};\n'
                     'for (const c of ["a", "b", "a"]) {\n'
                     '  tally[c] = tally[c] + 1;\n'
                     '}\n'
                     'console.log(`${tally["a"]} ${tally["b"]}`);\n',
                     'const tally: { [key: string]: number } = {};\n'
                     'for (const c of ["a", "b", "a"]) {\n'
                     '  tally[c] = (tally[c] ?? 0) + 1;\n'
                     '}\n'
                     'console.log(`${tally["a"]} ${tally["b"]}`);\n',
                     [("", "2 1")],
                     hints=["A key that has never been seen reads back as undefined.",
                            "undefined + 1 is NaN — supply 0 with ?? before adding."]),
                _ch("tscourse-w7-grp-ch1", "Grouped spending report", "Medium",
                    "Each input line is `category,item,price`. Group the prices by category, then print one line per category in alphabetical order: `category: N item(s), total $X.XX`, singular when the category holds exactly one item.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const groups: { [key: string]: number[] } = {};\n'
                    'for (const line of lines) {\n'
                    '  const parts = line.trim().split(",");\n'
                    '  const cat = parts[0];\n'
                    '  groups[cat] = groups[cat] ?? [];\n'
                    '  groups[cat].push(Number(parts[2]));\n'
                    '}\n'
                    'for (const cat of Object.keys(groups).sort()) {\n'
                    '  const prices = groups[cat];\n'
                    '  let total = 0;\n'
                    '  for (const p of prices) total = total + p;\n'
                    '  const label = prices.length === 1 ? "item" : "items";\n'
                    '  console.log(`${cat}: ${prices.length} ${label}, total $${total.toFixed(2)}`);\n'
                    '}\n',
                    'const groups: { [key: string]: number[] } = {};\n'
                    'for (const line of lines) {\n'
                    '  const parts = line.trim().split(",");\n'
                    '  const cat = parts[0];\n'
                    '  groups[cat] = groups[cat] ?? [];\n'
                    '  groups[cat].push(Number(parts[2]));\n'
                    '}\n'
                    'for (const cat of Object.keys(groups).sort()) {\n'
                    '  const prices = groups[cat];\n'
                    '  let total = 0;\n'
                    '  for (const p of prices) total = total + p;\n'
                    '  const label = prices.length === 1 ? "item" : "items";\n'
                    '  console.log(`${cat}: ${prices.length} ${label}, total $${total.toFixed(2)}`);\n'
                    '}',
                    [("food,apple,1.50\nbooks,novel,29.99\nfood,bread,2.25",
                      "books: 1 item, total $29.99\nfood: 2 items, total $3.75"),
                     ("a,x,1\na,y,2\na,z,3", "a: 3 items, total $6.00")],
                    hints=["One pass builds the buckets; a second pass over the sorted keys prints the report.",
                           "The bucket here holds numbers, so its annotation is { [key: string]: number[] }.",
                           "Sum a bucket with a running total in a for..of loop.",
                           'Pick the word with a ternary: prices.length === 1 ? "item" : "items".']),
            ],
            quiz=[
                _q("The two lines at the heart of grouping are…",
                   ["sort then join", "create the bucket if missing, then push",
                    "filter then map", "keys then values"], 1,
                   "Everything else is deciding what the key should be."),
                _q("Bucket into arrays rather than accumulating numbers when…",
                   ["there are many keys", "you still need the individual items later",
                    "the values are strings", "the input is sorted"], 1,
                   "Grouping keeps the members; accumulating keeps only the answer."),
                _q("`Object.keys(groups).sort()` is used so that…",
                   ["the buckets are sorted", "the report prints in a stable, testable order",
                    "duplicate keys are removed", "lookup gets faster"], 1,
                   "The keys are ordered; the buckets themselves are untouched."),
                _q("How many passes over the records does grouping take?",
                   ["one per category", "one, whatever the categories turn out to be",
                    "two per category", "one per record squared"], 1,
                   "That is exactly why you group rather than loop per category."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #7 — the expense ledger",
        """
Budget Buddy grows up: expenses become **records**, and the report is built
from them.

Input is one expense per line — `desc amount paid` — where `paid` is `y` or
`n`:

```
coffee 3.25 y
book 12 n
lunch 9.50 n
rent 900 y
```

Print:

```
Entries:  4
Total:    $924.75
Unpaid:   $21.50 (book, lunch)
Biggest:  rent ($900.00)
```

Rules:

- Build an array of records with `desc` (string), `amount` (number) and `paid`
  (boolean — `true` when the third field is `y`).
- `Unpaid` shows the unpaid total, then the unpaid descriptions in **input
  order**, joined with `, `.
- `Biggest` is the single largest expense, paid or not.
- Money always carries two decimal places.
""",
        _ch("tscourse-w7-capstone", "Budget Buddy #7", "Medium",
            "Parse the lines into records, then report on them.",
            _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
            'const items = rows.map((line) => {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0], amount: Number(p[1]), paid: p[2] === "y" };\n'
            '});\n'
            'let total = 0;\n'
            'for (const it of items) {\n  total += it.amount;\n}\n'
            'const unpaid = items.filter((it) => !it.paid);\n'
            'let unpaidTotal = 0;\n'
            'for (const it of unpaid) {\n  unpaidTotal += it.amount;\n}\n'
            'const biggest = [...items].sort((p, q) => q.amount - p.amount)[0];\n'
            'console.log(`Entries:  ${items.length}`);\n'
            'console.log(`Total:    $${total.toFixed(2)}`);\n'
            'console.log(`Unpaid:   $${unpaidTotal.toFixed(2)} (${unpaid.map((it) => it.desc).join(", ")})`);\n'
            'console.log(`Biggest:  ${biggest.desc} ($${biggest.amount.toFixed(2)})`);\n',
            'const items = rows.map((line) => {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0], amount: Number(p[1]), paid: p[2] === "y" };\n'
            '});\n'
            'let total = 0;\n'
            'for (const it of items) {\n  total += it.amount;\n}\n'
            'const unpaid = items.filter((it) => !it.paid);\n'
            'let unpaidTotal = 0;\n'
            'for (const it of unpaid) {\n  unpaidTotal += it.amount;\n}\n'
            'const biggest = [...items].sort((p, q) => q.amount - p.amount)[0];\n'
            'console.log(`Entries:  ${items.length}`);\n'
            'console.log(`Total:    $${total.toFixed(2)}`);\n'
            'console.log(`Unpaid:   $${unpaidTotal.toFixed(2)} (${unpaid.map((it) => it.desc).join(", ")})`);\n'
            'console.log(`Biggest:  ${biggest.desc} ($${biggest.amount.toFixed(2)})`);',
            [("coffee 3.25 y\nbook 12 n\nlunch 9.50 n\nrent 900 y",
              "Entries:  4\nTotal:    $924.75\nUnpaid:   $21.50 (book, lunch)\nBiggest:  rent ($900.00)"),
             ("tea 2 n",
              "Entries:  1\nTotal:    $2.00\nUnpaid:   $2.00 (tea)\nBiggest:  tea ($2.00)"),
             ("a 5 y\nb 5 y",
              "Entries:  2\nTotal:    $10.00\nUnpaid:   $0.00 ()\nBiggest:  a ($5.00)")],
            hints=["Parse first: split into lines, then split each line into three parts.",
                   'paid is a boolean, so convert it: p[2] === "y".',
                   "Filter to the unpaid records ONCE and reuse that array for both the total and the names — it keeps input order automatically.",
                   "Biggest comes from sorting a copy descending by amount and taking element 0.",
                   "Every money figure ends in .toFixed(2)."]),
        example_io="Entries:  4\nTotal:    $924.75\nUnpaid:   $21.50 (book, lunch)\nBiggest:  rent ($900.00)",
        rubric=["Each line becomes a record with desc, amount and a boolean paid",
                "The unpaid list preserves input order",
                "Biggest is found without mutating the items array",
                "All money is formatted to two decimal places"],
        stretch=_ch("tscourse-w7-capstone-stretch", "Budget Buddy #7 (stretch)", "Medium",
                    "Add a `By tag:` line. Each line now ends with a tag (`coffee 3.25 y food`); total the amounts per tag and print them sorted alphabetically as `food=$12.75; rent=$900.00`.",
                    _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const items = rows.map((line) => {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0], amount: Number(p[1]), paid: p[2] === "y", tag: p[3] };\n'
                    '});\n'
                    'const byTag: { [key: string]: number } = {};\n'
                    'for (const it of items) {\n  byTag[it.tag] = (byTag[it.tag] ?? 0) + it.amount;\n}\n'
                    'const parts = Object.keys(byTag).sort().map((t) => `${t}=$${byTag[t].toFixed(2)}`);\n'
                    'console.log(`By tag: ${parts.join("; ")}`);\n',
                    'const byTag: { [key: string]: number } = {};\n'
                    'for (const it of items) {\n  byTag[it.tag] = (byTag[it.tag] ?? 0) + it.amount;\n}\n'
                    'const parts = Object.keys(byTag).sort().map((t) => `${t}=$${byTag[t].toFixed(2)}`);\n'
                    'console.log(`By tag: ${parts.join("; ")}`);',
                    [("coffee 3.25 y food\nlunch 9.50 n food\nrent 900 y home",
                      "By tag: food=$12.75; home=$900.00"),
                     ("tea 2 n drink", "By tag: drink=$2.00")],
                    hints=["This is the tally pattern, accumulating an amount rather than a count.",
                           "byTag[it.tag] = (byTag[it.tag] ?? 0) + it.amount;",
                           "Sort the keys before mapping so the output is deterministic."]),
    ),
))

# --- Week 8 ---------------------------------------------------------------
_WEEKS.append(_week(
    8, 2, _M2,
    "Types that Describe Your Data",
    "Name the shapes your program works with, let inference do the rest, and fold a list to one value with reduce.",
    """
You have been using types since week 1 — TypeScript worked most of them out
silently. This week you take the wheel: **naming** the shapes your data has, so
the compiler can check every place they're used.

The payoff is not decoration. Once `Expense` is a named type, a misspelled
`e.amont`, a forgotten field, a string where a number belongs — each becomes a
red squiggle as you type instead of a wrong number in a report. That is the
entire reason TypeScript exists.

Two things to keep straight all week:

- **Types are erased before the program runs.** Nothing you write here changes
  behaviour at runtime. The drills therefore still exercise real logic; the
  types describe it.
- **Annotate boundaries, infer the middle.** Function parameters and returns,
  and empty containers, are worth annotating. Local variables with an obvious
  initialiser are not — `const n = 5` is already a `number`.

The week closes with **`reduce`**, the last of the big array methods and the one
that generalises all the others.

⏱️ Budget about **nine hours**, spread over several sittings.
""",
    objectives=[
        "Annotate values and functions, and know when inference is enough",
        "Name a shape with a type alias or an interface, and say which to reach for",
        "Type arrays of records, and use a tuple for a fixed-length pair",
        "Mark properties optional, and understand structural typing and excess-property checks",
        "Write a function type, and type a callback parameter",
        "Fold a list to a number, a string or an object with reduce",
        "Design a type for real-world data and process it end to end",
        "Explain that annotations are erased at runtime, and validate data where it enters",
        "Write a boundary function that turns untrusted text into a typed, checked record",
    ],
    why="A named type is documentation the compiler enforces. It is the cheapest bug prevention available, and it is what makes a codebase survive being edited six months later by someone who has forgotten it.",
    est_minutes=550,
    glossary=[
        _gloss("annotation", "A written type after a colon: let n: number."),
        _gloss("inference", "TypeScript working the type out from the value."),
        _gloss("type alias", "A name for any type: type ID = string."),
        _gloss("interface", "A name for the shape of an object type."),
        _gloss("structural typing", "Compatibility by SHAPE, not by name — if it has the right fields, it fits."),
        _gloss("excess property check", "TypeScript rejects unknown fields on an object literal assigned straight to a typed slot."),
        _gloss("optional property", "A field marked `?` that may be absent."),
        _gloss("readonly", "A property that cannot be reassigned after creation."),
        _gloss("union", "A type that is one of several: string | number."),
        _gloss("literal type", "A type that is one exact value: \"paid\"."),
        _gloss("tuple", "A fixed-length array with a type per position: [string, number]."),
        _gloss("Array<T>", "The long form of T[] — the same type."),
        _gloss("function type", "(a: number) => string — the shape of a function."),
        _gloss("void", "The return type of a function that returns nothing useful."),
        _gloss("any", "Opts out of checking entirely. Almost always the wrong answer."),
        _gloss("unknown", "Like any, but you must narrow it before use. The safe version."),
        _gloss(".reduce(f, seed)", "Folds a list into a single accumulated value."),
        _gloss("accumulator (reduce)", "The value carried from one step to the next."),
        _gloss("boundary", "The one place where outside data is validated and turned into your types."),
        _gloss("erasure", "Annotations exist only while compiling; nothing of them survives into the running code."),
        _gloss("any", "Switches type checking off for a value. Every any is a small debt."),
        _gloss("assertion (as)", "A promise to the compiler about a type. Checked never, believed always."),
        _gloss("NaN", "The number you get from a failed conversion. Test for it with Number.isNaN."),
    ],
    cheatsheet="""
```ts
// ---- annotate & infer -------------------------------------------------
const price: number = 10;      // annotation (often unnecessary)
const qty = 3;                 // inferred as number — fine
let names: string[] = [];      // needed: nothing to infer from
function f(s: string, n: number): string { return s.repeat(n); }

// ---- name a shape ------------------------------------------------------
interface Point { x: number; y: number }
type User = { name: string; admin: boolean };
type ID = string;                       // alias for any type, not just objects
type Status = "paid" | "unpaid";        // a union of literal types

// ---- arrays & tuples ---------------------------------------------------
const xs: number[] = [1, 2, 3];
const ys: Array<number> = [1, 2, 3];    // identical
const rows: User[] = [];
const pair: [string, number] = ["a", 1];   // fixed length, typed per slot

// ---- optional & readonly ------------------------------------------------
interface Expense {
  desc: string;
  amount: number;
  note?: string;              // may be absent -> string | undefined
  readonly id: string;        // set at creation, never reassigned
}

// ---- function types ------------------------------------------------------
type Mapper = (x: number) => number;
const double: Mapper = (x) => x * 2;        // parameter type inferred from Mapper
function apply(f: (x: number) => number, x: number): number { return f(x); }

// ---- reduce ---------------------------------------------------------------
[1, 2, 3].reduce((sum, x) => sum + x, 0)          // 6      fold to a number
words.reduce((acc, w) => acc + w[0], "")          // fold to a string
items.reduce((acc, it) => {                        // fold to an object
  acc[it.tag] = (acc[it.tag] ?? 0) + 1;
  return acc;
}, {} as { [key: string]: number })
```
""",
    self_check=[
        "Can you say which annotations are worth writing and which are noise?",
        "Can you name an object shape and use it on a function parameter?",
        "Can you explain what 'structural typing' means in one sentence?",
        "Can you say what `note?: string` does to the type of `e.note`?",
        "Can you write the type of a function that takes a string and returns a number?",
        "Can you total a field with reduce, and say what the seed is for?",
        "Can you say why `any` is worse than `unknown`?",
        "Can you say what happens to your annotations when the program runs?",
        "Can you write a parse function that rejects malformed input instead of crashing on it?",
    ],
    review=[
        _q("What happens to type annotations at runtime?",
           ["They slow it down", "They are erased before the program runs",
            "They become comments", "They are printed"], 1,
           "Checked while you write, then stripped."),
        _q("`interface` names…",
           ["a running object", "the shape of an object type", "a loop", "a value"], 1,
           "A reusable object shape."),
        _q("Which is TRUE of `type` versus `interface`?",
           ["type only works for objects", "interface only works for objects",
            "they are completely identical", "type cannot be exported"], 1,
           "A type alias can name ANY type — unions, functions, primitives — while an interface names object shapes."),
        _q("TypeScript decides two types are compatible based on…",
           ["their names", "their shape", "declaration order", "the file they are in"], 1,
           "Structural typing: the right fields is enough."),
        _q("`note?: string` means `e.note` has type…",
           ["string", "string | undefined", "undefined", "any"], 1,
           "Optional adds undefined to the type."),
        _q("`[string, number]` describes…",
           ["an array of strings and numbers", "a fixed-length pair, typed per position",
            "a union", "an object"], 1,
           "A tuple."),
        _q("`[1,2,3].reduce((s, x) => s + x, 0)` is…", ["0", "6", "123", "3"], 1,
           "It folds to the sum."),
        _q("The seed (second argument) of reduce is…",
           ["the first element", "the starting accumulator", "the length", "optional and pointless"], 1,
           "It is what the accumulator begins as — and the answer for an empty array."),
        _q("Why prefer `unknown` to `any`?",
           ["it is faster", "unknown forces you to narrow before use", "any is deprecated",
            "no difference"], 1,
           "any switches checking off entirely; unknown keeps you honest."),
        _q("Which annotation is genuinely needed?",
           ["const n: number = 5", "const s: string = \"a\"", "const xs: string[] = []",
            "const b: boolean = true"], 2,
           "An empty array gives inference nothing to work from."),
        _q("At runtime, annotations are…",
           ["checked on assignment", "erased", "stored with the value", "converted to guards"], 1,
           "Which is exactly why boundaries need real checks."),
        _q("`Number(\"oops\")` gives…",
           ["a type error", "NaN, whose type is number", "0", "undefined"], 1,
           "The annotation is satisfied and the value is still wrong."),
        _q("`value as Config` at runtime…",
           ["validates the shape", "does nothing", "copies the object", "throws on mismatch"], 1,
           "An assertion silences the compiler; it checks nothing."),
    ],
    milestone="Budget Buddy is now fully typed — the compiler guards its data, and reduce folds a whole ledger into a summary. That's Month 2 complete.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w8-annotations", "Annotations & inference",
            "Writing types — and knowing when not to.",
            """
An **annotation** is a type written after a colon:

```ts
const price: number = 10;
const label: string = "Coffee";
let names: string[] = [];
function repeat(s: string, n: number): string {
  return s.repeat(n);
}
```

**Inference** is TypeScript working it out for you:

```ts
const price = 10;            // inferred: number
const label = "Coffee";      // inferred: string
const xs = [1, 2, 3];        // inferred: number[]
```

Both are equally type-safe. `const price: number = 10` adds nothing the compiler
didn't already know — it's just more to read and more to keep in sync.

**The rule of thumb: annotate the boundaries, infer the middle.**

| annotate | because |
|---|---|
| function parameters | there is no value to infer from |
| function return types | it pins your intent, and catches a wrong branch |
| empty arrays/objects | `[]` could be an array of anything |
| a value that should be narrower than its literal | `let s: string` when you'll reassign |

| don't annotate | because |
|---|---|
| `const n = 5` | obviously a number |
| `const xs = [1, 2]` | obviously `number[]` |
| a local computed from typed things | inference follows the chain |

**Why annotate a return type** when TypeScript can infer it? Because inference
reports what your code *does*; an annotation states what it's *meant* to do. If
a branch accidentally returns a string, an annotated function errors at the
mistake. An unannotated one silently widens its return type and the error
surfaces somewhere else entirely.

**`any` turns checking off:**

```ts
let x: any = 5;
x.foo.bar();     // no complaint — and a crash at runtime
```

Every `any` is a hole in the net. `unknown` is the honest alternative: it
accepts anything but makes you check before you use it (week 9's narrowing is
exactly that skill).

> ⚠️ **Common mistakes:** annotating everything and drowning the code in noise;
> reaching for `any` to silence an error rather than understanding it; and
> forgetting that annotations vanish at runtime — they never validate real input.
""",
            warmup=[
                _q("`const n = 5;` — what type does TypeScript infer?",
                   ["any", "number", "5", "unknown"], 1, "From the value."),
                _q("Which annotation is genuinely required?",
                   ["const a = 1", "const b: number = 1", "const c: string[] = []",
                    "const d = \"x\""], 2,
                   "An empty array has nothing to infer from."),
                _q("`let x: any = 5; x.foo();` at compile time…",
                   ["errors", "is accepted", "warns", "is impossible"], 1,
                   "any accepts anything — and then it crashes when it runs."),
                _q("Annotations at runtime…",
                   ["validate input", "are erased", "slow things down", "become comments"], 1,
                   "They never check real data — that is your job."),
            ],
            exercises=[
                _ex("tscourse-w8-an-1", "Typed total",
                    "Compute price * qty into the annotated total.",
                    'const price: number = 10;\nconst qty: number = 3;\n'
                    'const total: number = price * qty;\nconsole.log(total);\n',
                    'price * qty', [("", "30")],
                    hints=["Multiply the two annotated numbers."]),
                _ex("tscourse-w8-an-2", "Typed repeat",
                    "Return the string repeated n times.",
                    'function repeat(s: string, n: number): string {\n  return s.repeat(n);\n}\n'
                    'console.log(repeat("ab", 3));\n',
                    's.repeat(n)', [("", "ababab")],
                    hints=["Strings have a .repeat(n) method."]),
                _ex("tscourse-w8-an-3", "An annotated empty array",
                    "Collect the doubled numbers into the annotated array and print them.",
                    _NUMS + 'const out: number[] = [];\n'
                    'for (const x of nums) {\n  out.push(x * 2);\n}\n'
                    'console.log(out.join(" "));\n',
                    'out.push(x * 2);', [("1 2 3", "2 4 6"), ("5", "10")],
                    hints=["The array is already annotated — just fill it.",
                           "Write out.push(x * 2);"]),
                _ex("tscourse-w8-an-4", "Annotate the parameters",
                    "Fill in the parameter list: a string and a number.",
                    'function tag(name: string, n: number): string {\n'
                    '  return `${name}-${n}`;\n}\n'
                    'console.log(tag("row", 3));\n',
                    'name: string, n: number', [("", "row-3")],
                    hints=["Each parameter gets its own annotation, separated by a comma.",
                           "Write name: string, n: number."]),
                _ex("tscourse-w8-an-5", "A narrower let",
                    "Annotate `status` so it can later hold any string, then print it.",
                    'let status: string = "new";\nstatus = "done";\nconsole.log(status);\n',
                    ': string = "new"', [("", "done")],
                    hints=['Without the annotation this would still infer string — but stating it documents the intent.',
                           'Write : string = "new".']),
                _fix("tscourse-w8-an-fix1", "Fix the operator",
                     "This should print 30 but a wrong operator sneaks in. Fix it.",
                     'const price: number = 10;\nconst qty: number = 3;\n'
                     'const total: number = price + qty;\nconsole.log(total);\n',
                     'const price: number = 10;\nconst qty: number = 3;\n'
                     'const total: number = price * qty;\nconsole.log(total);\n',
                     [("", "30")],
                     hints=["price + qty is 13.", "A line total multiplies."]),
                _fix("tscourse-w8-an-fix2", "Fix the any-shaped hole",
                     "`any` let a string through where a number was meant, so this prints `102` instead of 12. Give the value a real type and convert the input.",
                     _FS + 'const raw: any = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(raw + 2);\n',
                     _FS + 'const raw: number = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(raw + 2);\n',
                     [("10", "12"), ("5", "7")],
                     hints=["any silenced the check; the value really is a string, so + joined.",
                            "Annotate it as number and convert with Number(...)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("'Annotate the boundaries, infer the middle' means…",
                   ["annotate everything", "annotate parameters, returns and empty containers",
                    "never annotate", "annotate only locals"], 1,
                   "Those are the places inference has nothing to work from, or where intent matters."),
                _q("An annotated return type helps because…",
                   ["it is faster", "an accidental wrong return errors at the function, not far away",
                    "it is required", "it changes the value"], 1,
                   "Inference reports what the code does; the annotation states what it should do."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w8-aliases", "Naming shapes: type & interface",
            "One name, used everywhere.",
            """
Writing the same inline shape three times is how it drifts:

```ts
function total(e: { desc: string; amount: number }): number { ... }
function label(e: { desc: string; amount: number }): string { ... }
```

Name it once instead. Two ways, both fine:

```ts
interface Expense {
  desc: string;
  amount: number;
}

type Expense = {
  desc: string;
  amount: number;
};
```

Then use the name:

```ts
function total(e: Expense): number { return e.amount; }
const rows: Expense[] = [];
```

**`type` versus `interface`.** For object shapes they are nearly
interchangeable. The real difference:

- **`type` can name *any* type**, not just objects:

```ts
type ID = string;
type Status = "paid" | "unpaid";              // a union
type Mapper = (x: number) => number;          // a function
type Pair = [string, number];                 // a tuple
```

- **`interface` is only for object shapes**, but it can be *reopened* — declare
  it twice and the members merge. That's occasionally essential for extending
  library types, and occasionally a surprise.

A workable convention: **`interface` for object shapes you might extend,
`type` for everything else.** Pick one and be consistent; a codebase that mixes
them arbitrarily is just noise.

**Extending:**

```ts
interface Timestamped { created: string }
interface Expense extends Timestamped { desc: string; amount: number }

type Expense2 = Timestamped & { desc: string; amount: number };   // & = intersection
```

**Structural typing** is the deep idea underneath all of this. TypeScript does
not care what a type is *called* — only what shape it has:

```ts
interface Point { x: number; y: number }
const thing = { x: 1, y: 2, z: 3 };
const p: Point = thing;    // ✅ fine — it has x and y
```

A value fits if it has the required members. This is why you'll sometimes see a
function parameter typed with an inline shape listing only the two fields it
actually needs — anything with those fields can be passed.

> ⚠️ **Common mistakes:** using `,` instead of `;` between interface members
> (both are actually allowed, but be consistent); expecting an interface to
> reject extra fields on a variable (it doesn't — see the next lesson); and
> agonising over `type` versus `interface` when it rarely matters.
""",
            warmup=[
                _q("Which can name a union like `\"a\" | \"b\"`?",
                   ["interface", "type", "both", "neither"], 1,
                   "A type alias names any type; an interface names object shapes."),
                _q("TypeScript decides compatibility by…",
                   ["the type's name", "the shape", "the file", "declaration order"], 1,
                   "Structural typing."),
                _q("`interface A extends B` means A…",
                   ["replaces B", "has B's members plus its own", "is unrelated to B",
                    "is a copy of B"], 1,
                   "Extension adds to the inherited members."),
                _q("An object with EXTRA fields assigned to a variable of a narrower interface is…",
                   ["always rejected", "accepted when it comes from a variable",
                    "an error at runtime", "converted"], 1,
                   "Structural typing accepts it; only fresh object literals get the excess-property check."),
            ],
            exercises=[
                _ex("tscourse-w8-al-1", "Use a named shape",
                    "Return the Manhattan distance of the point from the origin.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'function dist(p: Point): number {\n  return Math.abs(p.x) + Math.abs(p.y);\n}\n'
                    'console.log(dist({ x: 3, y: -4 }));\n',
                    'Math.abs(p.x) + Math.abs(p.y)', [("", "7")],
                    hints=["Add the absolute values of the two coordinates."]),
                _ex("tscourse-w8-al-2", "A type alias for a record",
                    "Return `<name> (admin)` when admin is true, otherwise just the name.",
                    'type User = { name: string; admin: boolean };\n'
                    'function label(u: User): string {\n'
                    '  return u.admin ? `${u.name} (admin)` : u.name;\n}\n'
                    'console.log(label({ name: "Ada", admin: true }));\n'
                    'console.log(label({ name: "Bo", admin: false }));\n',
                    'u.admin ? `${u.name} (admin)` : u.name',
                    [("", "Ada (admin)\nBo")],
                    hints=["A ternary picks between the two strings."]),
                _ex("tscourse-w8-al-3", "Name a non-object type",
                    "Alias `Status` to the two allowed strings, then print the given status.",
                    _FS + 'type Status = "paid" | "unpaid";\n'
                    'const s: Status = fs.readFileSync(0, "utf8").trim() === "paid" ? "paid" : "unpaid";\n'
                    'console.log(s);\n',
                    '"paid" | "unpaid"', [("paid", "paid"), ("no", "unpaid")],
                    hints=["A type alias can name a union of exact string values.",
                           'Write "paid" | "unpaid".'],
                    difficulty="Medium"),
                _ex("tscourse-w8-al-4", "Extend an interface",
                    "Total the amount across the extended records.",
                    'interface Timestamped {\n  created: string;\n}\n'
                    'interface Expense extends Timestamped {\n  desc: string;\n  amount: number;\n}\n'
                    'const rows: Expense[] = [\n'
                    '  { created: "mon", desc: "coffee", amount: 3 },\n'
                    '  { created: "tue", desc: "book", amount: 12 },\n'
                    '];\n'
                    'let total = 0;\nfor (const r of rows) {\n  total += r.amount;\n}\n'
                    'console.log(total);\n',
                    'total += r.amount;', [("", "15")],
                    hints=["The extended interface has both its own fields and the inherited one.",
                           "Accumulate r.amount."]),
                _ex("tscourse-w8-al-5", "Structural fit",
                    "The value has an extra field, but it still fits Point. Print its distance.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'const thing = { x: 1, y: 2, z: 3 };\n'
                    'const p: Point = thing;\n'
                    'console.log(p.x + p.y);\n',
                    'const p: Point = thing;', [("", "3")],
                    hints=["Assigning from a VARIABLE skips the excess-property check.",
                           "Write const p: Point = thing;"],
                    difficulty="Medium"),
                _fix("tscourse-w8-al-fix1", "Fix the distance",
                     "Negative coordinates break this — dist({x:3,y:-4}) should be 7. Fix it.",
                     'interface Point {\n  x: number;\n  y: number;\n}\n'
                     'function dist(p: Point): number {\n  return p.x + p.y;\n}\n'
                     'console.log(dist({ x: 3, y: -4 }));\n',
                     'interface Point {\n  x: number;\n  y: number;\n}\n'
                     'function dist(p: Point): number {\n  return Math.abs(p.x) + Math.abs(p.y);\n}\n'
                     'console.log(dist({ x: 3, y: -4 }));\n',
                     [("", "7")],
                     hints=["3 + (-4) is -1, which is not a distance.",
                            "Wrap each coordinate in Math.abs."]),
                _fix("tscourse-w8-ali-fix2", "Fix the shape that was only promised",
                     "This should print `ada <ada@example.com>` but the email comes out undefined. An assertion was used to force an incomplete object into the shape.",
                     'interface User {\n  name: string;\n  email: string;\n}\n'
                     'function line(u: User): string {\n'
                     '  return `${u.name} <${u.email}>`;\n}\n'
                     'const u = { name: "ada" } as User;\n'
                     'console.log(line(u));\n',
                     'interface User {\n  name: string;\n  email: string;\n}\n'
                     'function line(u: User): string {\n'
                     '  return `${u.name} <${u.email}>`;\n}\n'
                     'const u: User = { name: "ada", email: "ada@example.com" };\n'
                     'console.log(line(u));\n',
                     [("", "ada <ada@example.com>")],
                     hints=["`as User` promised a field that was never supplied.",
                            "Annotate the variable instead of asserting it, and give it every required field."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Which CANNOT be expressed with `interface`?",
                   ["an object shape", "extending another shape",
                    "a union of two string literals", "a method signature"], 2,
                   "Unions need a type alias."),
                _q("Structural typing means a value fits a type when…",
                   ["it was declared with that type", "it has the required members",
                    "it is in the same file", "it is a class"], 1,
                   "Names are irrelevant; shape is everything."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w8-collections", "Typed arrays & tuples",
            "Describing lists and fixed-length pairs.",
            """
An array's type says what's inside it:

```ts
const xs: number[] = [1, 2, 3];
const names: string[] = ["Ada"];
const rows: Expense[] = [];
```

`Array<number>` is the identical type written the long way:

```ts
const ys: Array<number> = [1, 2, 3];   // same as number[]
```

Use whichever your codebase uses. `T[]` is shorter; `Array<T>` occasionally
reads better for complicated element types.

**Arrays of arrays:**

```ts
const grid: number[][] = [[1, 2], [3, 4]];
```

Read `number[][]` from the inside out: an array of (arrays of number).

**An array of a union** versus **a union of arrays** are different, and the
distinction bites:

```ts
const a: (string | number)[] = ["x", 1];   // each element is either
const b: string[] | number[] = ["x", "y"]; // the whole array is one or the other
```

**Tuples** are fixed-length arrays with a type per position:

```ts
const pair: [string, number] = ["coffee", 3];
pair[0].toUpperCase();     // TypeScript knows this one is a string
pair[1].toFixed(2);        // ...and this one is a number
```

This is exactly what `Object.entries` gives you — `[key, value]` pairs — which
is why destructuring them works so neatly:

```ts
for (const [k, v] of Object.entries(counts)) {
  console.log(`${k}=${v}`);
}
```

A tuple is the right tool when a pair genuinely has a fixed shape and order.
When there are more than two or three slots, or the order isn't obvious, an
object with names is kinder to read.

**`readonly`** stops reassignment:

```ts
const xs: readonly number[] = [1, 2, 3];
xs.push(4);       // ❌ compile error
```

It's a compile-time promise, not a runtime freeze — but as a signal in a
function signature ("I will not modify your array") it is genuinely valuable.

> ⚠️ **Common mistakes:** writing `number[]` when you meant a tuple and losing
> the per-position types; forgetting that an empty array literal needs an
> annotation; and expecting `readonly` to protect the array at runtime.
""",
            warmup=[
                _q("`Array<string>` and `string[]` are…",
                   ["different", "the same type", "only for classes", "invalid"], 1,
                   "Two spellings of one type."),
                _q("`number[][]` describes…",
                   ["two numbers", "an array of arrays of number", "a tuple",
                    "a union"], 1, "Read it inside out."),
                _q("`const p: [string, number] = [\"a\", 1];` — what is `p.length`?",
                   ["any", "exactly 2", "1", "unknown"], 1, "Tuples are fixed length."),
                _q("`Object.entries(o)` gives you an array of…",
                   ["keys", "values", "[key, value] tuples", "objects"], 2,
                   "Which is why `for (const [k, v] of ...)` works."),
            ],
            exercises=[
                _ex("tscourse-w8-co-1", "A typed list of records",
                    "Total the amounts across the typed array.",
                    'interface Item {\n  name: string;\n  price: number;\n}\n'
                    'const items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\n'
                    'let total = 0;\nfor (const it of items) {\n  total += it.price;\n}\n'
                    'console.log(total);\n',
                    'total += it.price;', [("", "10")],
                    hints=["Accumulate the price field."]),
                _ex("tscourse-w8-co-2", "Array of arrays",
                    "Print the value at row 1, column 0 of the typed grid.",
                    'const grid: number[][] = [[1, 2], [3, 4]];\nconsole.log(grid[1][0]);\n',
                    'grid[1][0]', [("", "3")],
                    hints=["Index the row, then the column."]),
                _ex("tscourse-w8-co-3", "A tuple",
                    "Print the pair as `COFFEE costs 3.00`, using both slots.",
                    'const pair: [string, number] = ["coffee", 3];\n'
                    'console.log(`${pair[0].toUpperCase()} costs ${pair[1].toFixed(2)}`);\n',
                    '${pair[0].toUpperCase()} costs ${pair[1].toFixed(2)}',
                    [("", "COFFEE costs 3.00")],
                    hints=["Slot 0 is a string and slot 1 is a number, so each has its own methods.",
                           "Use pair[0].toUpperCase() and pair[1].toFixed(2)."],
                    difficulty="Medium"),
                _ex("tscourse-w8-co-4", "Destructure entries",
                    "Print each key and value as `k=v` lines, sorted by key.",
                    'const counts: { [key: string]: number } = { b: 1, a: 2 };\n'
                    'for (const [k, v] of Object.entries(counts).sort()) {\n'
                    '  console.log(`${k}=${v}`);\n}\n',
                    'const [k, v] of', [("", "a=2\nb=1")],
                    hints=["Each entry is a [key, value] tuple, so destructure it in the loop header.",
                           "Write const [k, v] of."],
                    difficulty="Medium"),
                _ex("tscourse-w8-co-5", "An array of a union",
                    "The list holds numbers and strings. Print only the numbers, space-separated.",
                    'const mixed: (string | number)[] = [1, "a", 2, "b", 3];\n'
                    'const nums = mixed.filter((x) => typeof x === "number");\n'
                    'console.log(nums.join(" "));\n',
                    'typeof x === "number"', [("", "1 2 3")],
                    hints=["typeof reports the runtime type as a string.",
                           'Write typeof x === "number".'],
                    difficulty="Medium"),
                _fix("tscourse-w8-co-fix1", "Fix the grid index",
                     "This should print 3 (row 1, column 0) but prints 2. Fix it.",
                     'const grid: number[][] = [[1, 2], [3, 4]];\nconsole.log(grid[0][1]);\n',
                     'const grid: number[][] = [[1, 2], [3, 4]];\nconsole.log(grid[1][0]);\n',
                     [("", "3")],
                     hints=["The row index comes first, then the column.",
                            "Write grid[1][0]."]),
                _fix("tscourse-w8-col-fix2", "Fix the tuple order",
                     "Each pair is [name, quantity], so this should print `2 x apple`. The destructuring reads the slots the wrong way round.",
                     'type Pair = [string, number];\n'
                     'const items: Pair[] = [["apple", 2], ["fig", 5]];\n'
                     'for (const [qty, name] of items) console.log(`${qty} x ${name}`);\n',
                     'type Pair = [string, number];\n'
                     'const items: Pair[] = [["apple", 2], ["fig", 5]];\n'
                     'for (const [name, qty] of items) console.log(`${qty} x ${name}`);\n',
                     [("", "2 x apple\n5 x fig")],
                     hints=["A tuple's meaning is positional: slot 0 is the name, slot 1 is the quantity.",
                            "Name the destructured slots in the order the tuple declares them."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A tuple differs from an array in that…",
                   ["it is faster", "it has a fixed length with a type per position",
                    "it cannot hold objects", "it is immutable"], 1,
                   "Per-position types are the point."),
                _q("`(string | number)[]` versus `string[] | number[]`:",
                   ["identical", "the first allows mixed elements; the second is all-one-or-all-the-other",
                    "the second allows mixing", "both are invalid"], 1,
                   "Where the union sits changes everything."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w8-optional", "Optional fields & excess properties",
            "Describing data that isn't always complete.",
            """
Real records have holes. Mark a field with `?` when it may be absent:

```ts
interface Expense {
  desc: string;
  amount: number;
  note?: string;        // may be missing
}
```

`note?: string` means `e.note` has type `string | undefined`. TypeScript then
**makes you deal with it** before using it as a string:

```ts
e.note.toUpperCase();          // ❌ 'e.note' is possibly undefined
e.note?.toUpperCase();         // ✅ undefined when absent
(e.note ?? "").toUpperCase();  // ✅ a real fallback
```

That error is the feature. Week 7 taught you `?.` and `??` as runtime tools;
here the compiler tells you exactly where they are needed.

**Optional versus "present but undefined".** `note?: string` allows the field to
be missing entirely. `note: string | undefined` requires you to *write* it, even
if the value is `undefined`. Most of the time you want `?`.

**Default it once** rather than defending everywhere:

```ts
function describe(e: Expense): string {
  const note = e.note ?? "(no note)";
  return `${e.desc}: ${note}`;
}
```

**Excess property checks.** TypeScript is structural — extra fields are usually
fine. But a **fresh object literal** assigned straight to a typed slot gets an
extra check:

```ts
interface Point { x: number; y: number }

const p: Point = { x: 1, y: 2, z: 3 };   // ❌ 'z' does not exist in type 'Point'

const t = { x: 1, y: 2, z: 3 };
const q: Point = t;                       // ✅ fine — not a fresh literal
```

That inconsistency looks arbitrary and isn't: a literal written *right there*
with an unknown field is almost always a typo or a misunderstanding, so it's
worth flagging. A value that came from somewhere else may legitimately carry
more than this particular function needs.

**`readonly` on a property** prevents reassignment after construction:

```ts
interface Expense { readonly id: string; amount: number }
e.id = "x";        // ❌
e.amount = 5;      // ✅
```

Again: compile-time only. It documents and enforces intent while you write.

> ⚠️ **Common mistakes:** reading an optional field without handling
> `undefined`; using `||` instead of `??` and losing legitimate `0`/`""`; and
> being baffled by the excess-property check when a variable works but the same
> literal doesn't.
""",
            warmup=[
                _q("`note?: string` gives `e.note` the type…",
                   ["string", "string | undefined", "undefined", "any"], 1,
                   "Optional adds undefined."),
                _q("`const p: Point = { x:1, y:2, z:3 };` where Point has x and y…",
                   ["is fine", "errors — excess property on a fresh literal",
                    "drops z silently", "errors at runtime"], 1,
                   "Fresh literals get the extra check."),
                _q("`readonly id: string` prevents…",
                   ["reading id", "reassigning id after creation", "id being a string",
                    "nothing"], 1,
                   "Compile-time protection against reassignment."),
                _q("Which safely uppercases a possibly-missing note?",
                   ["e.note.toUpperCase()", "(e.note ?? \"\").toUpperCase()",
                    "e.note!.toUpperCase()", "String(e.note).toUpperCase()"], 1,
                   "Supply a real fallback before calling the method."),
            ],
            exercises=[
                _ex("tscourse-w8-op-1", "Handle the missing note",
                    "Print `coffee: (no note)` when the note is absent.",
                    'interface Expense {\n  desc: string;\n  amount: number;\n  note?: string;\n}\n'
                    'const e: Expense = { desc: "coffee", amount: 3 };\n'
                    'console.log(`${e.desc}: ${e.note ?? "(no note)"}`);\n',
                    'e.note ?? "(no note)"', [("", "coffee: (no note)")],
                    hints=["?? supplies a value only when the left side is missing.",
                           'Write e.note ?? "(no note)".']),
                _ex("tscourse-w8-op-2", "Safely call a method",
                    "Print the note uppercased, or an empty line when there is none.",
                    _FS + 'interface Expense {\n  desc: string;\n  note?: string;\n}\n'
                    'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'const e: Expense = raw ? { desc: "x", note: raw } : { desc: "x" };\n'
                    'console.log((e.note ?? "").toUpperCase());\n',
                    '(e.note ?? "").toUpperCase()',
                    [("hi", "HI"), ("", "")],
                    hints=["Give it a real string first, then call the method.",
                           'Write (e.note ?? "").toUpperCase().'],
                    difficulty="Medium"),
                _ex("tscourse-w8-op-3", "Count the complete records",
                    "Count how many records actually have a note.",
                    'interface Expense {\n  desc: string;\n  note?: string;\n}\n'
                    'const rows: Expense[] = [\n'
                    '  { desc: "a", note: "x" },\n  { desc: "b" },\n  { desc: "c", note: "y" },\n];\n'
                    'console.log(rows.filter((r) => r.note !== undefined).length);\n',
                    'r.note !== undefined', [("", "2")],
                    hints=["An absent optional field reads as undefined.",
                           "Write r.note !== undefined."]),
                _ex("tscourse-w8-op-4", "Default it once",
                    "Pull the note out with a fallback at the top of the function.",
                    'interface Expense {\n  desc: string;\n  note?: string;\n}\n'
                    'function describe(e: Expense): string {\n'
                    '  const note = e.note ?? "(no note)";\n'
                    '  return `${e.desc}: ${note}`;\n}\n'
                    'console.log(describe({ desc: "coffee" }));\n'
                    'console.log(describe({ desc: "book", note: "gift" }));\n',
                    'const note = e.note ?? "(no note)";',
                    [("", "coffee: (no note)\nbook: gift")],
                    hints=["Handle the absence once, then the rest of the body is simple.",
                           'Write const note = e.note ?? "(no note)";'],
                    difficulty="Medium"),
                _ex("tscourse-w8-op-5", "Avoid the excess-property check",
                    "Assign the wider value through a variable so it satisfies Point.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'const t = { x: 1, y: 2, z: 3 };\nconst p: Point = t;\n'
                    'console.log(p.x + p.y);\n',
                    'const p: Point = t;', [("", "3")],
                    hints=["A fresh literal with an unknown field would be rejected; a variable is not.",
                           "Write const p: Point = t;"],
                    difficulty="Medium"),
                _fix("tscourse-w8-op-fix1", "Fix the lost zero",
                     "A discount of 0 is real, but this prints 5. Fix it.",
                     'interface Row {\n  discount?: number;\n}\n'
                     'const r: Row = { discount: 0 };\nconsole.log(r.discount || 5);\n',
                     'interface Row {\n  discount?: number;\n}\n'
                     'const r: Row = { discount: 0 };\nconsole.log(r.discount ?? 5);\n',
                     [("", "0")],
                     hints=["0 is falsy, so || replaces it.",
                            "For 'only when missing', use ??."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why does TypeScript flag `z` in a fresh literal but not via a variable?",
                   ["a bug", "a literal with an unknown field is almost always a typo",
                    "variables are special", "it does not"], 1,
                   "The check targets the case where the mistake is most likely."),
                _q("`readonly` protects a field…",
                   ["at runtime", "at compile time only", "always", "never"], 1,
                   "Like every type feature, it is erased before running."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w8-fntypes", "Typing functions",
            "The shape of a function, as a type.",
            """
A function's type is written like an arrow function with no body:

```ts
(x: number) => number          // takes a number, returns a number
(s: string) => void            // takes a string, returns nothing useful
() => string                   // takes nothing, returns a string
```

You met this in week 5 as a *parameter* annotation. Now name it:

```ts
type Mapper = (x: number) => number;

const double: Mapper = (x) => x * 2;
const square: Mapper = (x) => x * x;
```

Notice `(x)` with **no annotation** in those arrows. Because the variable is
already typed as `Mapper`, TypeScript infers `x: number` from the target type.
This is called **contextual typing**, and it's why callbacks passed to `map` and
`filter` rarely need annotations:

```ts
nums.map((x) => x * 2);        // x is known to be number
```

**Typing a higher-order function:**

```ts
function applyTwice(f: (x: number) => number, x: number): number {
  return f(f(x));
}
```

**Returning a function** — the closure from week 5, now typed:

```ts
function multiplier(factor: number): (x: number) => number {
  return (x) => x * factor;
}
```

**`void` deserves care.** It means "the caller should not rely on a return
value". A function typed `() => void` may actually return something; the type
just says nobody should use it. That's deliberate, and it's why
`items.forEach((x) => list.push(x))` type-checks even though `push` returns a
number.

**Optional and default parameters** appear in the type too:

```ts
type Fmt = (n: number, digits?: number) => string;
const fmt: Fmt = (n, digits = 2) => n.toFixed(digits);
```

The default lives in the implementation, not the type — a type describes what
callers may do, and callers may omit it either way.

> ⚠️ **Common mistakes:** writing `Function` as a type (it accepts anything and
> tells you nothing); annotating callback parameters that contextual typing
> already knows; and confusing a function's *type* `(x: number) => number` with
> a function *value* `(x) => x * 2`.
""",
            warmup=[
                _q("`(s: string) => number` describes…",
                   ["a string", "a function taking a string and returning a number",
                    "a number", "an object"], 1,
                   "It is the shape of a function."),
                _q("In `const f: Mapper = (x) => x * 2;` the type of `x` is…",
                   ["any", "inferred from Mapper", "unknown", "an error"], 1,
                   "Contextual typing supplies it."),
                _q("Why do `map` callbacks rarely need annotations?",
                   ["they are any", "the element type is known, so the parameter is inferred",
                    "annotations are banned", "map is special"], 1,
                   "Contextual typing again."),
                _q("A `() => void` function…",
                   ["must return undefined", "may return something, but callers should ignore it",
                    "cannot be called", "returns null"], 1,
                   "void is about what the caller may rely on."),
            ],
            exercises=[
                _ex("tscourse-w8-fn-1", "Name a function type",
                    "Alias `Mapper` to a function from number to number, then use it.",
                    'type Mapper = (x: number) => number;\n'
                    'const double: Mapper = (x) => x * 2;\n'
                    'console.log(double(21));\n',
                    '(x: number) => number', [("", "42")],
                    hints=["Write it like an arrow function with no body.",
                           "Write (x: number) => number."]),
                _ex("tscourse-w8-fn-2", "Rely on contextual typing",
                    "Fill in the squaring arrow. Its parameter needs no annotation.",
                    'type Mapper = (x: number) => number;\n'
                    'const square: Mapper = (x) => x * x;\n'
                    'console.log(square(7));\n',
                    '(x) => x * x', [("", "49")],
                    hints=["Mapper already says x is a number.",
                           "Write (x) => x * x."]),
                _ex("tscourse-w8-fn-3", "A typed higher-order function",
                    "Apply the function to its own result.",
                    'function applyTwice(f: (x: number) => number, x: number): number {\n'
                    '  return f(f(x));\n}\n'
                    'console.log(applyTwice((n) => n + 3, 10));\n',
                    'return f(f(x));', [("", "16")],
                    hints=["Call f on x, then call f on that.",
                           "Write return f(f(x));"],
                    difficulty="Medium"),
                _ex("tscourse-w8-fn-4", "A typed factory",
                    "Return a function that multiplies by the captured factor.",
                    _FS + 'function multiplier(factor: number): (x: number) => number {\n'
                    '  return (x) => x * factor;\n}\n'
                    'const triple = multiplier(3);\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(triple(n));\n',
                    'return (x) => x * factor;', [("5", "15"), ("10", "30")],
                    hints=["The return type already says what shape to hand back.",
                           "Write return (x) => x * factor;"],
                    difficulty="Medium"),
                _ex("tscourse-w8-fn-5", "Optional parameter in a type",
                    "Implement the formatter with a default of 2 digits.",
                    'type Fmt = (n: number, digits?: number) => string;\n'
                    'const fmt: Fmt = (n, digits = 2) => n.toFixed(digits);\n'
                    'console.log(fmt(3.14159));\nconsole.log(fmt(3.14159, 3));\n',
                    '(n, digits = 2) => n.toFixed(digits)',
                    [("", "3.14\n3.142")],
                    hints=["The default belongs in the implementation, not the type.",
                           "Write (n, digits = 2) => n.toFixed(digits)."],
                    difficulty="Medium"),
                _fix("tscourse-w8-fn-fix1", "Fix the passed-in call",
                     "This passes the RESULT where a function was expected, and crashes. Fix it.",
                     'function applyTwice(f: (x: number) => number, x: number): number {\n'
                     '  return f(f(x));\n}\n'
                     'const double = (x: number): number => x * 2;\n'
                     'console.log(applyTwice(double(2), 5));\n',
                     'function applyTwice(f: (x: number) => number, x: number): number {\n'
                     '  return f(f(x));\n}\n'
                     'const double = (x: number): number => x * 2;\n'
                     'console.log(applyTwice(double, 5));\n',
                     [("", "20")],
                     hints=["double(2) is the number 4; applyTwice needs something callable.",
                            "Pass the function itself: double."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`Function` as a type annotation is discouraged because…",
                   ["it is slow", "it accepts any function and describes nothing",
                    "it is deprecated", "it cannot be called"], 1,
                   "Write the actual signature instead."),
                _q("Contextual typing is…",
                   ["a runtime feature", "TypeScript inferring a parameter's type from where the function is used",
                    "an annotation", "a union"], 1,
                   "It is why callbacks stay clean."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w8-reduce", "reduce — fold a list to one value",
            "The most general array method.",
            """
`map` gives one output per input. `filter` gives some of the inputs. **`reduce`
gives one value for the whole list** — a total, a maximum, a joined string, a
whole object.

```ts
[1, 2, 3].reduce((sum, x) => sum + x, 0);    // 6
```

Two arguments:

1. a **callback** `(accumulator, element) => newAccumulator`
2. a **seed** — what the accumulator starts as

It walks the list, feeding each result into the next step:

| step | acc in | x | acc out |
|---|---|---|---|
| start | — | — | 0 |
| 1 | 0 | 1 | 1 |
| 2 | 1 | 2 | 3 |
| 3 | 3 | 3 | 6 |

That's the accumulator pattern from week 4, with the bookkeeping done for you.
The loop version is identical in meaning:

```ts
let sum = 0;
for (const x of a) sum = sum + x;
```

**The seed matters, and it is not optional in practice.** It sets both the
starting value *and* the accumulator's type, and it is the answer for an empty
array. Leave it out and `reduce` uses the first element instead — which throws
on an empty array. **Always pass a seed.**

**The accumulator doesn't have to be a number.** This is what makes `reduce`
general:

```ts
// to a string
words.reduce((acc, w) => acc + w[0], "");            // initials

// to a maximum
nums.reduce((best, x) => (x > best ? x : best), -Infinity);

// to an object — a tally
items.reduce((acc, it) => {
  acc[it.tag] = (acc[it.tag] ?? 0) + 1;
  return acc;
}, {} as { [key: string]: number });
```

That last one is week 7's tally, folded. Note the `return acc;` — a braced
callback must hand the accumulator back, and forgetting it is *the* classic
reduce bug: the next step receives `undefined`.

**When not to use it.** `reduce` can express `map` and `filter`, but doing so is
strictly worse — less clear and no faster. Reach for `reduce` when you're
genuinely collapsing a list to one value; use the specific method when one fits.
A `reduce` whose body is ten lines usually wants to be a plain loop.

> ⚠️ **Common mistakes:** omitting the seed; forgetting `return acc` in a braced
> callback; and mutating the seed object across calls (fine here, but a trap when
> the seed is shared).
""",
            warmup=[
                _q("`[2,3,5].reduce((s, x) => s + x, 0)` is…", ["0", "10", "235", "3"], 1,
                   "Folds to the sum."),
                _q("`[].reduce((s, x) => s + x, 0)` is…", ["0", "undefined", "an error", "NaN"], 0,
                   "The seed is the answer for an empty list."),
                _q("`[].reduce((s, x) => s + x)` — no seed — does what?",
                   ["gives 0", "gives undefined", "throws", "gives NaN"], 2,
                   "With no seed and no elements there is nothing to start from."),
                _q("A braced reduce callback that forgets `return acc` gives…",
                   ["the seed", "undefined into the next step", "an error", "the last element"], 1,
                   "The callback's value IS the next accumulator."),
            ],
            exercises=[
                _ex("tscourse-w8-rd-1", "Total with reduce",
                    "Fold the numbers to their sum.",
                    _NUMS + 'console.log(nums.reduce((sum, x) => sum + x, 0));\n',
                    'nums.reduce((sum, x) => sum + x, 0)',
                    [("1 2 3 4", "10"), ("5", "5")],
                    hints=["Callback first, then the seed.",
                           "Write nums.reduce((sum, x) => sum + x, 0)."]),
                _ex("tscourse-w8-rd-2", "Total a field",
                    "Fold the typed records to the sum of their prices.",
                    'interface Item {\n  name: string;\n  price: number;\n}\n'
                    'const items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\n'
                    'console.log(items.reduce((sum, it) => sum + it.price, 0));\n',
                    'sum + it.price', [("", "10")],
                    hints=["Each step adds one record's price to the running total."]),
                _ex("tscourse-w8-rd-3", "Fold to a string",
                    "Build the initials of the words: `ada bo cy` → `abc`.",
                    _WORDS + 'console.log(words.reduce((acc, w) => acc + w[0], ""));\n',
                    'acc + w[0]', [("ada bo cy", "abc"), ("x", "x")],
                    hints=["The accumulator is a string, seeded empty.",
                           "Write acc + w[0]."],
                    difficulty="Medium"),
                _ex("tscourse-w8-rd-4", "Fold to a maximum",
                    "Find the largest number with reduce.",
                    _NUMS + 'console.log(nums.reduce((best, x) => (x > best ? x : best), -Infinity));\n',
                    '(x > best ? x : best)',
                    [("3 9 2", "9"), ("-5 -2", "-2"), ("7", "7")],
                    hints=["Keep whichever of the two is bigger.",
                           "Write (x > best ? x : best)."],
                    difficulty="Medium"),
                _ex("tscourse-w8-rd-5", "Fold to an object",
                    "Tally the words with reduce, then print the count for `a`.",
                    _WORDS + 'const counts = words.reduce((acc, w) => {\n'
                    '  acc[w] = (acc[w] ?? 0) + 1;\n  return acc;\n'
                    '}, {} as { [key: string]: number });\n'
                    'console.log(counts["a"] ?? 0);\n',
                    'acc[w] = (acc[w] ?? 0) + 1;\n  return acc;',
                    [("a b a c a", "3"), ("b c", "0")],
                    hints=["Update the accumulator, then hand it back for the next step.",
                           "Write acc[w] = (acc[w] ?? 0) + 1; then return acc;"],
                    difficulty="Medium"),
                _fix("tscourse-w8-rd-fix1", "Fix the reduce seed",
                     "The total is one too high — the seed is wrong. Fix it to 10.",
                     'interface Item {\n  name: string;\n  price: number;\n}\n'
                     'const items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\n'
                     'console.log(items.reduce((sum, it) => sum + it.price, 1));\n',
                     'interface Item {\n  name: string;\n  price: number;\n}\n'
                     'const items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\n'
                     'console.log(items.reduce((sum, it) => sum + it.price, 0));\n',
                     [("", "10")],
                     hints=["The last argument is the starting accumulator.",
                            "A sum seeds at 0."]),
                _fix("tscourse-w8-rd-fix2", "Fix the missing return",
                     "This tally should print 3 for `a b a c a` but crashes — the callback returns nothing. Fix it.",
                     _WORDS + 'const counts = words.reduce((acc, w) => {\n'
                     '  acc[w] = (acc[w] ?? 0) + 1;\n'
                     '}, {} as { [key: string]: number });\n'
                     'console.log(counts["a"] ?? 0);\n',
                     _WORDS + 'const counts = words.reduce((acc, w) => {\n'
                     '  acc[w] = (acc[w] ?? 0) + 1;\n  return acc;\n'
                     '}, {} as { [key: string]: number });\n'
                     'console.log(counts["a"] ?? 0);\n',
                     [("a b a c a", "3"), ("a", "1")],
                     hints=["Whatever the callback returns becomes the next accumulator — here that is undefined.",
                            "Add return acc; at the end of the callback."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The seed of a reduce sets…",
                   ["only the starting value", "the starting value, the accumulator's type, and the empty-list answer",
                    "the length", "nothing"], 1,
                   "All three — which is why you always pass one."),
                _q("When should you NOT use reduce?",
                   ["for sums", "when map or filter already says what you mean",
                    "for objects", "for strings"], 1,
                   "Expressing map via reduce is less clear and no faster."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w8-modelling", "Modelling real data",
            "Choosing types that make wrong states hard to write.",
            """
Types are a design tool, not paperwork. The question is always: **what shapes
should be possible?**

Take a payment record. A first attempt:

```ts
interface Payment {
  amount: number;
  status: string;        // "paid" or "pending" or "failed"
}
```

`status: string` allows `"pain"`, `"PAID"`, `""` and `"banana"`. Narrow it to
exactly the values you mean:

```ts
type Status = "paid" | "pending" | "failed";

interface Payment {
  amount: number;
  status: Status;
}
```

Now a typo is a compile error, and your editor autocompletes the three options.
This — **a union of literal types** — is the single highest-value modelling
trick in TypeScript, and week 9 is built on it.

**Make illegal states unrepresentable.** Compare:

```ts
interface Job { done: boolean; result?: string; error?: string }
```

That permits `{ done: false, result: "x", error: "y" }` — finished and failed
and unfinished at once. Nothing in the type says those fields travel together.
Week 9's discriminated unions fix this properly; for now, notice the smell:
**optional fields that are only meaningful in combination.**

**A practical checklist for a new type:**

1. What are the fields, and which are genuinely optional?
2. Which fields are a **fixed set of values** rather than free text?
3. Which fields must never change after creation? (`readonly`)
4. Are any of these fields only valid together?

**A typed pipeline** is what this all pays for. Parse into a named type once, at
the edge, and everything downstream is checked:

```ts
interface Row { desc: string; amount: number }

function parse(line: string): Row {
  const p = line.trim().split(" ");
  return { desc: p[0], amount: Number(p[1]) };
}

const rows: Row[] = lines.map(parse);
const total = rows.reduce((s, r) => s + r.amount, 0);
```

`parse` is the boundary. Above it is untrusted text; below it, every field has a
known type. Getting the boundary right is most of what makes a program feel
solid — and note that the *type* does no validation. `Number("abc")` is `NaN`,
and the annotation says `number` regardless. Types describe intent; **runtime
checks enforce it**, and you need both.

> ⚠️ **Common mistakes:** typing a fixed set of values as `string`; scattering
> optional fields that are only valid in combination; and assuming an annotation
> validates real input — it never does.
""",
            warmup=[
                _q("`status: string` versus `status: \"paid\" | \"pending\"` — the union…",
                   ["is slower", "makes typos a compile error and enables autocomplete",
                    "is the same", "is runtime-checked"], 1,
                   "Narrow types catch narrow mistakes."),
                _q("`{ done: boolean; result?: string; error?: string }` allows…",
                   ["only valid states", "done and error together, nonsensically",
                    "nothing", "only done: true"], 1,
                   "Optionals that only make sense in combination are a design smell."),
                _q("Does `const n: number = Number(\"abc\")` error?",
                   ["yes, at compile time", "no — the type is number, the value is NaN",
                    "yes, at runtime", "it returns 0"], 1,
                   "NaN is a number. Types do not validate input."),
                _q("Parsing at the boundary means…",
                   ["parsing everywhere", "converting untrusted text into a named type once, at the edge",
                    "never parsing", "parsing at the end"], 1,
                   "Everything downstream then works with known types."),
            ],
            exercises=[
                _ex("tscourse-w8-md-1", "Narrow the status",
                    "Alias Status to exactly the three allowed values, then print the payment's status.",
                    'type Status = "paid" | "pending" | "failed";\n'
                    'interface Payment {\n  amount: number;\n  status: Status;\n}\n'
                    'const p: Payment = { amount: 10, status: "paid" };\n'
                    'console.log(p.status);\n',
                    '"paid" | "pending" | "failed"', [("", "paid")],
                    hints=["A union of exact string values, separated by |.",
                           'Write "paid" | "pending" | "failed".']),
                _ex("tscourse-w8-md-2", "A parse boundary",
                    "Complete parse so it turns a `desc amount` line into a Row.",
                    _FS + 'interface Row {\n  desc: string;\n  amount: number;\n}\n'
                    'function parse(line: string): Row {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0], amount: Number(p[1]) };\n}\n'
                    'const rows: Row[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'console.log(rows[0].amount);\n',
                    'return { desc: p[0], amount: Number(p[1]) };',
                    [("coffee 3", "3"), ("book 12\nrent 900", "12")],
                    hints=["Build the record, converting the numeric field.",
                           "Write return { desc: p[0], amount: Number(p[1]) };"],
                    difficulty="Medium"),
                _ex("tscourse-w8-md-3", "A typed pipeline",
                    "Parse the lines, then fold them to a total with reduce.",
                    _FS + 'interface Row {\n  desc: string;\n  amount: number;\n}\n'
                    'function parse(line: string): Row {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0], amount: Number(p[1]) };\n}\n'
                    'const rows: Row[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'console.log(rows.reduce((s, r) => s + r.amount, 0));\n',
                    'rows.reduce((s, r) => s + r.amount, 0)',
                    [("coffee 3\nbook 12", "15"), ("rent 900", "900")],
                    hints=["Fold the parsed records to one number.",
                           "Write rows.reduce((s, r) => s + r.amount, 0)."],
                    difficulty="Medium"),
                _ex("tscourse-w8-md-4", "Validate at runtime",
                    "The type says number, but the data may be nonsense. Print `invalid` when the amount does not parse.",
                    _FS + 'interface Row {\n  desc: string;\n  amount: number;\n}\n'
                    'const p = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                    'const row: Row = { desc: p[0], amount: Number(p[1]) };\n'
                    'console.log(Number.isNaN(row.amount) ? "invalid" : row.amount);\n',
                    'Number.isNaN(row.amount) ? "invalid" : row.amount',
                    [("coffee abc", "invalid"), ("coffee 3", "3")],
                    hints=["Annotations never check real input — you must.",
                           'Write Number.isNaN(row.amount) ? "invalid" : row.amount.'],
                    difficulty="Medium"),
                _ex("tscourse-w8-md-5", "readonly identity",
                    "Mark the id as readonly, then print the record's label.",
                    'interface Expense {\n  readonly id: string;\n  desc: string;\n}\n'
                    'const e: Expense = { id: "e1", desc: "coffee" };\n'
                    'console.log(`${e.id}: ${e.desc}`);\n',
                    'readonly id: string;', [("", "e1: coffee")],
                    hints=["readonly goes before the field name.",
                           "Write readonly id: string;"]),
                _fix("tscourse-w8-md-fix1", "Fix the unvalidated boundary",
                     "For `coffee abc` this should print `invalid` but prints `NaN`. Fix it.",
                     _FS + 'const p = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                     'const amount: number = Number(p[1]);\n'
                     'console.log(amount);\n',
                     _FS + 'const p = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                     'const amount: number = Number(p[1]);\n'
                     'console.log(Number.isNaN(amount) ? "invalid" : amount);\n',
                     [("coffee abc", "invalid"), ("coffee 3", "3")],
                     hints=["NaN IS a number as far as the type system is concerned.",
                            "Check it at runtime with Number.isNaN."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The highest-value modelling move in TypeScript is…",
                   ["annotating every local", "replacing `string` with a union of the literal values you mean",
                    "using any", "adding readonly everywhere"], 1,
                   "It turns typos into compile errors and drives autocomplete."),
                _q("'Make illegal states unrepresentable' means…",
                   ["validate everything at runtime", "choose types that cannot describe a nonsensical combination",
                    "use readonly", "avoid optional fields"], 1,
                   "Design the type so the bad case cannot be written."),
                _q("Types validate real input…",
                   ["always", "never — they are erased; runtime checks are still required",
                    "only for numbers", "only with interfaces"], 1,
                   "You need both: types for intent, checks for reality."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w8-boundary", "Types at the boundary",
            "Where untrusted text becomes values your types can vouch for.",
            """
Here is the fact that reframes everything you learned this week:

> **Types are erased before the program runs.** Not one annotation survives into
> the running code.

`const n: number = ...` is a promise *you* make to the compiler, checked while
you write. It is not a guard rail at runtime. So the moment data arrives from
outside — stdin, a file, a network call, a form — your annotations describe what
you *hope* is there, and something has to actually check.

```ts
const raw = fs.readFileSync(0, "utf8").trim();
const amount: number = Number(raw);   // annotation satisfied…
console.log(amount + 1);              // …and if raw was "oops", this is NaN
```

`Number("oops")` is `NaN`, whose type is `number`. The annotation is honest; the
value is garbage. That is why real programs have a **boundary**.

**The boundary function.** One place converts text into your shape, validating
as it goes, and everything downstream can then trust its types:

```ts
interface Entry {
  name: string;
  amount: number;
  ok: boolean;       // did this line survive validation?
}

function parseEntry(line: string): Entry {
  const parts = line.split(",");
  if (parts.length !== 2) return { name: line.trim(), amount: 0, ok: false };
  const amount = Number(parts[1].trim());
  if (Number.isNaN(amount)) return { name: parts[0].trim(), amount: 0, ok: false };
  return { name: parts[0].trim(), amount, ok: true };
}
```

Two things to notice. Validation is **guard clauses** again — reject, reject,
then the happy path. And a rejected line does not crash the program; it comes
back marked `ok: false` and the caller decides. (Month 4 gives this the name it
has in the wild: the **Result** pattern.)

**Check the things that actually go wrong.** In practice that is a short list:
the field count is wrong, a number didn't parse (`Number.isNaN`), a required
string is empty, or a value is out of range (a negative price).

**`any` switches the compiler off.** It is not "some type" — it is "stop
checking":

```ts
const data: any = { amount: "3.25" };   // a STRING, though nobody said so
console.log(data.amount + 1);           // "3.251" — no error, wrong answer
```

Every bug `any` lets through is a bug you were paying TypeScript to catch. Treat
each `any` as a small debt.

**`as` is a promise, not a check.** An assertion tells the compiler you know
better. Nothing is verified at runtime:

```ts
const cfg = fromElsewhere as Config;   // if it isn't a Config, nothing complains
```

Use it only right after a check you performed yourself, and never as a way to
silence an error you don't understand.

> ⚠️ **Common mistakes:** believing an annotation validates runtime data;
> forgetting the `Number.isNaN` guard, so one bad row poisons every total with
> `NaN`; reaching for `any` to make an error go away; and reading fields out of
> a split line in the wrong order — the types all still line up, and the output
> is nonsense.
""",
            warmup=[
                _q("`const n: number = Number(\"oops\");` — does this compile?",
                   ["No, it is a type error", "Yes, and n is NaN", "Yes, and n is 0", "It throws"], 1,
                   "NaN is a number as far as the type system is concerned."),
                _q("At runtime, your type annotations are…",
                   ["checked on every assignment", "erased — they existed only while compiling",
                    "converted to if-statements", "stored alongside the value"], 1,
                   "Which is exactly why boundaries need real validation code."),
                _q("`const data: any = { amount: \"3.25\" }; data.amount + 1` gives…",
                   ["4.25", '"3.251"', "a type error", "NaN"], 1,
                   "any turns checking off, so string concatenation happens silently."),
                _q("`value as Config` does what at runtime?",
                   ["validates the shape", "nothing at all — it only silences the compiler",
                    "copies the object", "throws if the shape is wrong"], 1,
                   "An assertion is a promise you make, not a check you get."),
            ],
            exercises=[
                _ex("tscourse-w8-bnd-1", "Annotate the boundary",
                    "Give the parsing function the return annotation that says what it hands back.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'function parsePoint(text: string): Point {\n'
                    '  const parts = text.split(",");\n'
                    '  return { x: Number(parts[0]), y: Number(parts[1]) };\n}\n'
                    'const p = parsePoint("3,4");\n'
                    'console.log(p.x + p.y);\n',
                    'Point {\n'
                    '  const parts = text.split(",");',
                    [("", "7")],
                    hints=["The function builds an object with x and y — there is already a name for that shape.",
                           "Annotate the return as Point."]),
                _ex("tscourse-w8-bnd-2", "Guard the parse",
                    "One unparseable value should become 0 rather than poisoning everything. Add the guard.",
                    _FS +
                    'function toAmount(text: string): number {\n'
                    '  const n = Number(text.trim());\n'
                    '  if (Number.isNaN(n)) return 0;\n'
                    '  return n;\n}\n'
                    'const raw = fs.readFileSync(0, "utf8").trim().split(",");\n'
                    'const amounts: number[] = raw.map(toAmount);\n'
                    'console.log(amounts.join(" "));\n',
                    'if (Number.isNaN(n)) return 0;',
                    [("3, abc, 5", "3 0 5"), ("1,2", "1 2")],
                    hints=["Number() hands back NaN when the text isn't a number.",
                           "NaN === NaN is false, so you must test with Number.isNaN.",
                           "Write if (Number.isNaN(n)) return 0;"],
                    difficulty="Easy"),
                _ex("tscourse-w8-bnd-3", "Reject the wrong field count",
                    "A line must have exactly two fields. Fill in the rejecting guard so a malformed line comes back marked not-ok.",
                    'interface Parsed {\n  ok: boolean;\n  name: string;\n  amount: number;\n}\n'
                    'function parseLine(line: string): Parsed {\n'
                    '  const parts = line.split(",");\n'
                    '  if (parts.length !== 2) return { ok: false, name: "", amount: 0 };\n'
                    '  const amount = Number(parts[1]);\n'
                    '  if (Number.isNaN(amount)) return { ok: false, name: "", amount: 0 };\n'
                    '  return { ok: true, name: parts[0].trim(), amount };\n}\n'
                    'console.log(parseLine("coffee, 3.25").ok);\n'
                    'console.log(parseLine("coffee").ok);\n'
                    'console.log(parseLine("coffee, abc").ok);\n',
                    'if (parts.length !== 2) return { ok: false, name: "", amount: 0 };',
                    [("", "true\nfalse\nfalse")],
                    hints=["Splitting on the comma should give exactly two pieces.",
                           'Return { ok: false, name: "", amount: 0 } when it does not.'],
                    difficulty="Medium"),
                _ex("tscourse-w8-bnd-4", "The escape hatch",
                    "Value from elsewhere, shape you are willing to vouch for. Fill in the assertion.",
                    'interface Config {\n  retries: number;\n  verbose: boolean;\n}\n'
                    'const fromElsewhere: any = { retries: 3, verbose: true };\n'
                    'const cfg = fromElsewhere as Config;\n'
                    'console.log(`${cfg.retries} ${cfg.verbose}`);\n',
                    'fromElsewhere as Config',
                    [("", "3 true")],
                    hints=["The `as` keyword asserts a type — remember it checks nothing at runtime.",
                           "Write fromElsewhere as Config."],
                    difficulty="Easy"),
                _ex("tscourse-w8-bnd-5", "Trust only what passed",
                    "Total up the rows that survived validation, ignoring the rest. Fill in the fold.",
                    'interface Row {\n  name: string;\n  amount: number;\n  ok: boolean;\n}\n'
                    'const rows: Row[] = [\n'
                    '  { name: "a", amount: 3, ok: true },\n'
                    '  { name: "b", amount: 99, ok: false },\n'
                    '  { name: "c", amount: 4, ok: true },\n'
                    '];\n'
                    'const total = rows.filter((r) => r.ok).reduce((sum, r) => sum + r.amount, 0);\n'
                    'console.log(total);\n',
                    '.reduce((sum, r) => sum + r.amount, 0)',
                    [("", "7")],
                    hints=["Filter first so the fold only ever sees good rows.",
                           "Start the accumulator at 0 and add each row's amount."],
                    difficulty="Medium"),
                _fix("tscourse-w8-bnd-fix1", "Fix the any that hid a bug",
                     "This should print `Total: 4.25`, but `any` let a string through where a number was meant. Type the shape honestly and convert at the boundary.",
                     'const raw: any = { name: "coffee", amount: "3.25" };\n'
                     'console.log(`Total: ${raw.amount + 1}`);\n',
                     'interface RawEntry {\n  name: string;\n  amount: string;\n}\n'
                     'const raw: RawEntry = { name: "coffee", amount: "3.25" };\n'
                     'console.log(`Total: ${Number(raw.amount) + 1}`);\n',
                     [("", "Total: 4.25")],
                     hints=["`amount` really is text — say so in an interface instead of hiding it under any.",
                            "Then convert it with Number(...) where you actually do arithmetic."],
                     difficulty="Medium"),
                _fix("tscourse-w8-bnd-fix2", "Fix the poisoned total",
                     "One unparseable value turns the whole total into NaN. It should print 15.00.",
                     'function toAmount(text: string): number {\n'
                     '  return Number(text);\n}\n'
                     'const values = ["10", "oops", "5"];\n'
                     'let total = 0;\n'
                     'for (const v of values) total = total + toAmount(v);\n'
                     'console.log(total.toFixed(2));\n',
                     'function toAmount(text: string): number {\n'
                     '  const n = Number(text);\n'
                     '  if (Number.isNaN(n)) return 0;\n'
                     '  return n;\n}\n'
                     'const values = ["10", "oops", "5"];\n'
                     'let total = 0;\n'
                     'for (const v of values) total = total + toAmount(v);\n'
                     'console.log(total.toFixed(2));\n',
                     [("", "15.00")],
                     hints=["Anything added to NaN is NaN, so one bad value ruins every later sum.",
                            "Guard inside toAmount with Number.isNaN and fall back to 0."]),
                _fix("tscourse-w8-bnd-fix3", "Fix the swapped fields",
                     "The types all line up, yet this prints `12 costs NaN`. The fields are being read out of the split line in the wrong order.",
                     'interface Item {\n  name: string;\n  price: number;\n}\n'
                     'function toItem(line: string): Item {\n'
                     '  const parts = line.split(",");\n'
                     '  return { name: parts[1], price: Number(parts[0]) };\n}\n'
                     'const it = toItem("book,12");\n'
                     'console.log(`${it.name} costs ${it.price}`);\n',
                     'interface Item {\n  name: string;\n  price: number;\n}\n'
                     'function toItem(line: string): Item {\n'
                     '  const parts = line.split(",");\n'
                     '  return { name: parts[0], price: Number(parts[1]) };\n}\n'
                     'const it = toItem("book,12");\n'
                     'console.log(`${it.name} costs ${it.price}`);\n',
                     [("", "book costs 12")],
                     hints=["parts[0] is the text before the comma; parts[1] is after it.",
                            "The compiler cannot catch this — both fields still receive the right kind of value."],
                     difficulty="Medium"),
                _ch("tscourse-w8-bnd-ch1", "A validating boundary", "Hard",
                    "Each line is `name,amount`. Write the `Entry` shape and `parseEntry`: reject a line that hasn't got exactly two fields, whose amount doesn't parse, or whose amount is negative — marking it `ok: false` with an amount of 0 — and accept everything else with the name trimmed.",
                    _FS +
                    'interface Entry {\n  name: string;\n  amount: number;\n  ok: boolean;\n}\n'
                    'function parseEntry(line: string): Entry {\n'
                    '  const parts = line.split(",");\n'
                    '  if (parts.length !== 2) return { name: line.trim(), amount: 0, ok: false };\n'
                    '  const amount = Number(parts[1].trim());\n'
                    '  if (Number.isNaN(amount) || amount < 0) {\n'
                    '    return { name: parts[0].trim(), amount: 0, ok: false };\n'
                    '  }\n'
                    '  return { name: parts[0].trim(), amount, ok: true };\n}\n'
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n")\n'
                    '  .filter((l) => l.trim().length > 0);\n'
                    'const entries: Entry[] = lines.map((l) => parseEntry(l));\n'
                    'const good = entries.filter((e) => e.ok);\n'
                    'const total = good.reduce((sum, e) => sum + e.amount, 0);\n'
                    'for (const e of good) console.log(`${e.name}: $${e.amount.toFixed(2)}`);\n'
                    'console.log(`Accepted ${good.length}, rejected ${entries.length - good.length}, total $${total.toFixed(2)}`);\n',
                    'interface Entry {\n  name: string;\n  amount: number;\n  ok: boolean;\n}\n'
                    'function parseEntry(line: string): Entry {\n'
                    '  const parts = line.split(",");\n'
                    '  if (parts.length !== 2) return { name: line.trim(), amount: 0, ok: false };\n'
                    '  const amount = Number(parts[1].trim());\n'
                    '  if (Number.isNaN(amount) || amount < 0) {\n'
                    '    return { name: parts[0].trim(), amount: 0, ok: false };\n'
                    '  }\n'
                    '  return { name: parts[0].trim(), amount, ok: true };\n}',
                    [("coffee, 3.25\nbroken\nbook, 12\nbad, -4",
                      "coffee: $3.25\nbook: $12.00\nAccepted 2, rejected 2, total $15.25"),
                     ("a,1\nb,2", "a: $1.00\nb: $2.00\nAccepted 2, rejected 0, total $3.00"),
                     ("nope", "Accepted 0, rejected 1, total $0.00")],
                    hints=["Entry needs three fields: the name, the amount, and whether the line survived.",
                           "Write the rejections as guard clauses, one per thing that can go wrong.",
                           "Number.isNaN(amount) catches unparseable text; amount < 0 catches the impossible price.",
                           "The happy path returns at the end with ok: true and the trimmed name."]),
            ],
            quiz=[
                _q("What survives into the running program?",
                   ["the annotations", "only the values and the code — annotations are erased",
                    "interfaces but not type aliases", "everything"], 1,
                   "Which is why runtime data needs runtime checks."),
                _q("`Number(\"oops\")` produces…",
                   ["a type error", "NaN, whose type is number", "0", "undefined"], 1,
                   "The annotation is satisfied and the value is still wrong."),
                _q("The point of a single boundary function is that…",
                   ["it is faster", "everything downstream can trust its types",
                    "it avoids interfaces", "it removes the need for guards"], 1,
                   "Validate once, at the edge; trust everywhere inside."),
                _q("`as` should be used…",
                   ["whenever the compiler complains", "sparingly, right after a check you performed yourself",
                    "instead of interfaces", "to convert strings to numbers"], 1,
                   "It silences the compiler without checking anything."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #8 — the typed ledger",
        """
Month 2's finale. Everything gets a name, and the report is folded with
`reduce`.

Input is one expense per line — `desc amount status` — where status is `paid`
or `unpaid`:

```
coffee 3.25 paid
book 12 unpaid
lunch 9.50 unpaid
rent 900 paid
```

Print:

```
Count:   4
Total:   $924.75
Paid:    $903.25
Unpaid:  $21.50
Largest: rent
```

Requirements:

- A `type Status = "paid" | "unpaid"` and an `interface Expense` with `desc`,
  `amount` and `status`.
- A `parse(line: string): Expense` boundary function.
- Every total computed with **`reduce`**, not a loop.
- `Largest` is the description of the biggest expense.
""",
        _ch("tscourse-w8-capstone", "Budget Buddy #8", "Medium",
            "Model the data, parse it at the boundary, then fold it three ways.",
            _FS + 'type Status = "paid" | "unpaid";\n'
            'interface Expense {\n  desc: string;\n  amount: number;\n  status: Status;\n}\n'
            'function parse(line: string): Expense {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0], amount: Number(p[1]), status: p[2] === "paid" ? "paid" : "unpaid" };\n'
            '}\n'
            'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const total = rows.reduce((s, r) => s + r.amount, 0);\n'
            'const paid = rows.filter((r) => r.status === "paid").reduce((s, r) => s + r.amount, 0);\n'
            'const largest = rows.reduce((best, r) => (r.amount > best.amount ? r : best), rows[0]);\n'
            'console.log(`Count:   ${rows.length}`);\n'
            'console.log(`Total:   $${total.toFixed(2)}`);\n'
            'console.log(`Paid:    $${paid.toFixed(2)}`);\n'
            'console.log(`Unpaid:  $${(total - paid).toFixed(2)}`);\n'
            'console.log(`Largest: ${largest.desc}`);\n',
            'function parse(line: string): Expense {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0], amount: Number(p[1]), status: p[2] === "paid" ? "paid" : "unpaid" };\n'
            '}\n'
            'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const total = rows.reduce((s, r) => s + r.amount, 0);\n'
            'const paid = rows.filter((r) => r.status === "paid").reduce((s, r) => s + r.amount, 0);\n'
            'const largest = rows.reduce((best, r) => (r.amount > best.amount ? r : best), rows[0]);\n'
            'console.log(`Count:   ${rows.length}`);\n'
            'console.log(`Total:   $${total.toFixed(2)}`);\n'
            'console.log(`Paid:    $${paid.toFixed(2)}`);\n'
            'console.log(`Unpaid:  $${(total - paid).toFixed(2)}`);\n'
            'console.log(`Largest: ${largest.desc}`);',
            [("coffee 3.25 paid\nbook 12 unpaid\nlunch 9.50 unpaid\nrent 900 paid",
              "Count:   4\nTotal:   $924.75\nPaid:    $903.25\nUnpaid:  $21.50\nLargest: rent"),
             ("tea 2 unpaid",
              "Count:   1\nTotal:   $2.00\nPaid:    $0.00\nUnpaid:  $2.00\nLargest: tea"),
             ("a 5 paid\nb 5 paid",
              "Count:   2\nTotal:   $10.00\nPaid:    $10.00\nUnpaid:  $0.00\nLargest: a")],
            hints=["parse is the boundary: split the line and build one Expense, converting the amount and narrowing the status.",
                   'The status field is a union, so derive it: p[2] === "paid" ? "paid" : "unpaid".',
                   "Total is rows.reduce((s, r) => s + r.amount, 0) — always pass the seed.",
                   "Paid is a filter followed by the same reduce; unpaid is then just total - paid.",
                   "Largest folds to a RECORD, not a number: seed with rows[0] and keep whichever has the bigger amount."]),
        example_io="Count:   4\nTotal:   $924.75\nPaid:    $903.25\nUnpaid:  $21.50\nLargest: rent",
        rubric=["Status is a union of literal types, not string",
                "A single parse function converts a line into a typed Expense",
                "Every total uses reduce with an explicit seed",
                "Largest folds to a record and reads its desc"],
        stretch=_ch("tscourse-w8-capstone-stretch", "Budget Buddy #8 (stretch)", "Medium",
                    "Add a `By status:` line built with a single reduce that folds to an object: `paid=2, unpaid=2` (counts, keys sorted alphabetically).",
                    _FS + 'type Status = "paid" | "unpaid";\n'
                    'interface Expense {\n  desc: string;\n  amount: number;\n  status: Status;\n}\n'
                    'function parse(line: string): Expense {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0], amount: Number(p[1]), status: p[2] === "paid" ? "paid" : "unpaid" };\n'
                    '}\n'
                    'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'const byStatus = rows.reduce((acc, r) => {\n'
                    '  acc[r.status] = (acc[r.status] ?? 0) + 1;\n  return acc;\n'
                    '}, {} as { [key: string]: number });\n'
                    'const parts = Object.keys(byStatus).sort().map((k) => `${k}=${byStatus[k]}`);\n'
                    'console.log(`By status: ${parts.join(", ")}`);\n',
                    'const byStatus = rows.reduce((acc, r) => {\n'
                    '  acc[r.status] = (acc[r.status] ?? 0) + 1;\n  return acc;\n'
                    '}, {} as { [key: string]: number });\n'
                    'const parts = Object.keys(byStatus).sort().map((k) => `${k}=${byStatus[k]}`);\n'
                    'console.log(`By status: ${parts.join(", ")}`);',
                    [("coffee 3.25 paid\nbook 12 unpaid\nlunch 9.50 unpaid\nrent 900 paid",
                      "By status: paid=2, unpaid=2"),
                     ("tea 2 unpaid", "By status: unpaid=1")],
                    hints=["This is the tally fold: seed with an empty object and return the accumulator each step.",
                           "acc[r.status] = (acc[r.status] ?? 0) + 1; then return acc;",
                           "Sort the keys before mapping so the output is deterministic."]),
    ),
))

# ===========================================================================
# MONTH 3 — The type system, properly
# ===========================================================================
_M3 = "The Type System, Properly"

# --- Week 9 ---------------------------------------------------------------
_LINE = _FS + 'const line = fs.readFileSync(0, "utf8").trim();\n'

_WEEKS.append(_week(
    9, 3, _M3,
    "Unions & Narrowing",
    "Model a value that is 'one of several things', then prove to the compiler which one it is before using it.",
    """
Month 2 taught you to describe data that has **one** shape. Month 3 starts with
the far more common case: data that is **one of several** shapes.

- A parsed field is a `number` **or** the string `"n/a"`.
- A status is `"paid"` **or** `"pending"` **or** `"failed"`.
- An API result is a success **or** an error.

That's a **union type**, written with `|`:

```ts
type Result = number | string;
```

And immediately you hit the central problem. Given a `number | string`, you
cannot call `.toFixed(2)` — it might be a string. You cannot call
`.toUpperCase()` — it might be a number. On a union you may only use what **all**
the members have in common.

The way out is **narrowing**: writing an ordinary runtime check that TypeScript
understands, after which it knows which member you have:

```ts
function show(v: number | string): string {
  if (typeof v === "number") {
    return v.toFixed(2);      // here, v is a number
  }
  return v.toUpperCase();     // here, it can only be a string
}
```

That is the whole week, and it is the moment TypeScript stops feeling like
annotation and starts feeling like a proof assistant. The checks are all
JavaScript you already know — `typeof`, `===`, `in`, `Array.isArray`,
truthiness. What's new is that the *type* changes as you check.

⏱️ Budget about **ten hours**, spread over several sittings.
""",
    objectives=[
        "Write union types and say what you may do with an un-narrowed union",
        "Model a fixed set of options as a union of literal types",
        "Narrow with typeof, and know exactly what typeof reports",
        "Narrow with equality and with switch on a literal union",
        "Narrow with truthiness, in, Array.isArray and instanceof",
        "Design and consume a discriminated union",
        "Prove a switch is exhaustive with never, and combine types with &",
        "Write a custom type guard whose return annotation narrows its argument",
        "Use a predicate with filter to narrow a whole array's element type",
    ],
    why="Almost every interesting value in a real program is 'one of several things' — loaded or loading or failed, guest or member, found or missing. Unions plus narrowing are how TypeScript makes those cases impossible to forget.",
    est_minutes=590,
    glossary=[
        _gloss("union", "A type that is one of several: number | string."),
        _gloss("member (of a union)", "One of the alternatives in a union."),
        _gloss("literal type", "A type that is one exact value: \"paid\", 42, true."),
        _gloss("narrowing", "Using a runtime check so the compiler knows which member you have."),
        _gloss("type guard", "An expression that narrows: typeof x === \"string\"."),
        _gloss("control-flow analysis", "TypeScript tracking the narrowed type along each branch."),
        _gloss("typeof", "Reports a value's runtime type as a string."),
        _gloss("in", "Tests whether a key exists on an object — and narrows by it."),
        _gloss("Array.isArray(x)", "The reliable array test; typeof an array is \"object\"."),
        _gloss("instanceof", "Tests against a class or constructor, e.g. Error."),
        _gloss("discriminated union", "A union of objects sharing a literal 'tag' field that identifies each case."),
        _gloss("discriminant / tag", "The shared literal field (kind, type, status) that tells the cases apart."),
        _gloss("exhaustive", "Every case of a union is handled."),
        _gloss("never", "The type with no values — what remains when every case is handled."),
        _gloss("intersection (&)", "A type having ALL the members of both: A & B."),
        _gloss("narrowing by assignment", "Assigning a value narrows the variable's type from then on."),
        _gloss("type predicate", "A return annotation of the form `v is T` that tells the compiler what true means."),
        _gloss("custom type guard", "A function you wrote whose result narrows the value you passed it."),
        _gloss("assertion function", "`asserts v is T` — narrows from the call site onward, or stops the program."),
        _gloss("filter narrowing", "Passing a predicate to filter, so the result comes back as the narrower array."),
    ],
    cheatsheet="""
```ts
// ---- declaring unions --------------------------------------------------
type Score = number | "n/a";
type Status = "paid" | "pending" | "failed";
type Maybe = string | undefined;

// On an un-narrowed union you may only use what ALL members share:
function f(v: number | string) {
  v.toString();      // ✅ both have it
  v.toFixed(2);      // ❌ string does not
}

// ---- typeof narrowing ---------------------------------------------------
if (typeof v === "number") { /* v: number */ }
else                       { /* v: string */ }

typeof 1          // "number"      typeof "a"        // "string"
typeof true       // "boolean"     typeof undefined  // "undefined"
typeof {}         // "object"      typeof []         // "object"  ⚠️
typeof null       // "object"      ⚠️ the famous bug
typeof (() => 1)  // "function"

// ---- equality & switch ---------------------------------------------------
if (s === "paid") { /* s: "paid" */ }
switch (s) {
  case "paid":    ...; break;
  case "pending": ...; break;
  default:        ...;
}

// ---- other guards ---------------------------------------------------------
if (x)                    { /* removes null/undefined/""/0 */ }
if (x !== undefined)      { /* keeps a legitimate 0 or "" */ }
if (Array.isArray(x))     { /* x: something[] */ }
if ("radius" in shape)    { /* shape: the member with radius */ }
if (e instanceof Error)   { /* e: Error */ }

// ---- discriminated union ---------------------------------------------------
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return 3.14 * s.r * s.r;
    case "square": return s.side * s.side;
  }
}

// ---- exhaustiveness --------------------------------------------------------
default: {
  const _exhaustive: never = s;    // errors if a case was forgotten
  return _exhaustive;
}

// ---- intersection -----------------------------------------------------------
type Timestamped = { created: string };
type Row = Timestamped & { desc: string };   // has BOTH members
```
""",
    self_check=[
        "Can you say why `v.toFixed(2)` is rejected on a `number | string`?",
        "Can you narrow a union with typeof and use the member's own methods?",
        "Can you list what typeof reports for an array and for null?",
        "Can you narrow a literal union with a switch?",
        "Can you say when to use `in` rather than `typeof`?",
        "Can you design a discriminated union for two shapes and write a function over it?",
        "Can you explain how the `never` trick catches a forgotten case?",
        "Can you say why a helper annotated `: boolean` fails to narrow, and fix it?",
        "Can you filter a mixed array into a narrower one using a predicate you wrote?",
    ],
    review=[
        _q("On an un-narrowed `number | string` you may use…",
           ["everything on number", "everything on string",
            "only what BOTH have", "nothing at all"], 2,
           "The union's usable surface is the intersection of its members' members."),
        _q("`typeof []` is…", ['"array"', '"object"', '"list"', "undefined"], 1,
           "Arrays are objects — use Array.isArray."),
        _q("`typeof null` is…", ['"null"', '"object"', '"undefined"', "an error"], 1,
           "A famous, permanent JavaScript wart."),
        _q("After `if (typeof v === \"string\")`, inside the block `v` is…",
           ["still the union", "string", "any", "unknown"], 1,
           "TypeScript narrows along the branch."),
        _q("A discriminated union needs…",
           ["an interface", "a shared literal field distinguishing the cases",
            "a class", "an array"], 1,
           "The discriminant is what makes switch-narrowing work."),
        _q("`type Shape = {kind:\"a\"} | {kind:\"b\"}` — after `case \"a\":` the value is…",
           ["Shape", '{kind:"a"}', "never", "any"], 1,
           "The tag narrows it to exactly one member."),
        _q("`const _x: never = s;` in a default branch errors when…",
           ["always", "a union case was not handled", "never", "s is a string"], 1,
           "If any case remains, s is not never — so it fails to compile."),
        _q("`A & B` gives you…",
           ["either A or B", "the members of both", "neither", "an array"], 1,
           "Intersection combines; union chooses."),
        _q("Which safely narrows away a legitimate `0`?",
           ["if (x)", "if (x !== undefined)", "if (!x)", "if (x == null)"], 1,
           "Truthiness would discard the 0 as well."),
        _q("`\"r\" in shape` is useful when…",
           ["the members share a tag", "the members have no tag but different fields",
            "shape is a number", "never"], 1,
           "It distinguishes object shapes by the presence of a key."),
        _q("A helper annotated `: boolean` used in an `if` narrows the argument to…",
           ["the matching member", "nothing", "never", "unknown"], 1,
           "A plain boolean carries no information about which member matched."),
        _q("The name on the left of `is` in a predicate must be…",
           ["any identifier", "one of the function's parameters", "a type", "the return value"], 1,
           "The predicate narrows that particular parameter."),
        _q("A predicate whose body is wrong is…",
           ["rejected by the compiler", "believed anyway, which is worse than no guard",
            "ignored at runtime", "converted to boolean"], 1,
           "Keep the body an obvious restatement of the type."),
    ],
    milestone="Budget Buddy can now hold values that are 'a number or not applicable', and expense events that are one of several kinds — with the compiler refusing to let you forget a case.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w9-unions", "Union types",
            "One value, several possible types.",
            """
A **union** says a value is one of several types:

```ts
type Score = number | "n/a";
let s: Score = 42;
s = "n/a";        // also fine
s = "banana";     // ❌ not a member
```

The `|` reads as "or". Members can be any types: primitives, object shapes,
literal values, arrays, other unions.

**The rule that governs everything else:** on an un-narrowed union you may only
use what **every** member supports.

```ts
function f(v: number | string) {
  v.toString();     // ✅ both numbers and strings have toString
  v.toFixed(2);     // ❌ Property 'toFixed' does not exist on type 'string'
  v.length;         // ❌ numbers have no length
}
```

This feels restrictive for about a day, and then you realise it is the *point*.
The compiler is telling you that you haven't decided what to do about the string
case. `v.toFixed(2)` on a `number | string` isn't unfairly rejected — it is a
crash waiting to happen, caught early.

**Unions are everywhere in real code**, usually with `undefined` or `null`:

```ts
type Maybe = string | undefined;      // what `find` returns
type Id = string | number;            // an API that accepts either
```

Anything optional is secretly a union: `note?: string` gives `e.note` the type
`string | undefined`, which is exactly why last week's compiler errors happened.

**A union of object shapes** is legal and useful, though awkward without a tag
(lesson 6 fixes that):

```ts
type Contact = { email: string } | { phone: string };
```

**Where unions come from in practice:** parsing (`Number(x)` may be `NaN`),
lookups (found or not), external input (any of several shapes), and state
(loading, loaded, failed).

> ⚠️ **Common mistakes:** trying to use a member-specific method without
> narrowing; reaching for `any` to silence the error (throwing away the very
> information you need); and writing `number | any`, which collapses to `any`.
""",
            warmup=[
                _q("`type T = number | string;` — which is allowed on an un-narrowed T?",
                   ["t.toFixed(2)", "t.toUpperCase()", "t.toString()", "t.length"], 2,
                   "Only what both members share."),
                _q("`note?: string` gives the field the type…",
                   ["string", "string | undefined", "undefined", "any"], 1,
                   "Optional is a union in disguise."),
                _q("`let s: \"a\" | \"b\" = \"c\";` is…",
                   ["fine", "a compile error", "a runtime error", "undefined"], 1,
                   '"c" is not a member of the union.'),
                _q("`number | any` collapses to…",
                   ["number", "any", "unknown", "never"], 1,
                   "any absorbs everything — which is why it destroys unions."),
            ],
            exercises=[
                _ex("tscourse-w9-un-1", "Declare a union",
                    "Alias Score so it is either a number or the exact string `n/a`, then print the value.",
                    'type Score = number | "n/a";\nconst s: Score = "n/a";\nconsole.log(s);\n',
                    'number | "n/a"', [("", "n/a")],
                    hints=["Members are separated by |.",
                           'Write number | "n/a".']),
                _ex("tscourse-w9-un-2", "Use only the shared surface",
                    "Print the value using a method BOTH members have.",
                    'const v: number | string = 42;\nconsole.log(v.toString());\n',
                    'v.toString()', [("", "42")],
                    hints=["toFixed and toUpperCase each belong to only one member.",
                           "Both have toString()."]),
                _ex("tscourse-w9-un-3", "A union with undefined",
                    "Print the found element, or `none` when there is none.",
                    _NUMS + 'const hit: number | undefined = nums.find((x) => x > 10);\n'
                    'console.log(hit === undefined ? "none" : hit);\n',
                    'hit === undefined ? "none" : hit',
                    [("5 20 3", "20"), ("1 2", "none")],
                    hints=["find's return type is a union with undefined.",
                           'Write hit === undefined ? "none" : hit.']),
                _ex("tscourse-w9-un-4", "A union of exact values",
                    "Alias Status to the three allowed strings and print the chosen one.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(s);\n',
                    '"paid" | "pending" | "failed"',
                    [("paid", "paid"), ("pending", "pending"), ("zzz", "failed")],
                    hints=["Three exact string values, joined by |.",
                           'Write "paid" | "pending" | "failed".']),
                _ex("tscourse-w9-un-5", "Union in an array",
                    "The list holds numbers and strings. Print how many entries are strings.",
                    'const mixed: (string | number)[] = [1, "a", 2, "b", "c"];\n'
                    'console.log(mixed.filter((x) => typeof x === "string").length);\n',
                    'typeof x === "string"', [("", "3")],
                    hints=["typeof reports the runtime type as a string.",
                           'Write typeof x === "string".'],
                    difficulty="Medium"),
                _fix("tscourse-w9-un-fix1", "Fix the un-narrowed call",
                     "This crashes when the value is a string. Print the number formatted to 2 decimals, or the string uppercased.",
                     'const v: number | string = "abc";\nconsole.log((v as number).toFixed(2));\n',
                     'const v: number | string = "abc";\n'
                     'console.log(typeof v === "number" ? v.toFixed(2) : v.toUpperCase());\n',
                     [("", "ABC")],
                     hints=["The `as number` cast lies to the compiler; at runtime it is still a string.",
                            "Check with typeof and handle both branches."],
                     difficulty="Medium"),
                _fix("tscourse-w9-uni-fix2", "Fix the half-handled union",
                     "This should print `#AB` then `#7`, but it crashes on the number: the code assumed one member and asserted its way past the other.",
                     'type Id = string | number;\n'
                     'function show(id: Id): string {\n'
                     '  return `#${(id as string).toUpperCase()}`;\n}\n'
                     'console.log(show("ab"));\n'
                     'console.log(show(7));\n',
                     'type Id = string | number;\n'
                     'function show(id: Id): string {\n'
                     '  if (typeof id === "string") return `#${id.toUpperCase()}`;\n'
                     '  return `#${id}`;\n}\n'
                     'console.log(show("ab"));\n'
                     'console.log(show(7));\n',
                     [("", "#AB\n#7")],
                     hints=["A union means you must handle every member, not assert the awkward one away.",
                            "Narrow with typeof, then handle the number case on its own line."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The usable methods on a union are…",
                   ["the union of all members' methods", "the ones common to every member",
                    "none", "all of the first member's"], 1,
                   "Anything else would be unsound."),
                _q("Casting with `as` to silence a union error…",
                   ["is the right fix", "lies to the compiler and can crash at runtime",
                    "narrows properly", "is required"], 1,
                   "A cast asserts; it does not check."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w9-literals", "Literal types",
            "A type that is one exact value.",
            """
A **literal type** is a type whose only value is one specific value:

```ts
let a: "paid" = "paid";
a = "pending";     // ❌ not assignable
```

On its own that's a curiosity. In a union it is the most useful modelling tool
in the language:

```ts
type Status = "paid" | "pending" | "failed";
type Dice = 1 | 2 | 3 | 4 | 5 | 6;
type Flag = true | false;              // (this is just `boolean`)
```

Compare `status: string` with `status: Status`:

| | `string` | `Status` |
|---|---|---|
| `"paid"` | ✅ | ✅ |
| `"Paid"` | ✅ 😬 | ❌ caught |
| `"pian"` | ✅ 😬 | ❌ caught |
| autocomplete | nothing | the three options |
| exhaustive switch | impossible | possible (lesson 7) |

**Inference and widening.** TypeScript decides how specific to be based on
mutability:

```ts
const a = "paid";      // type is "paid"   — it can never change
let b = "paid";        // type is string   — it might be reassigned
```

`const` gets the narrow literal type; `let` gets the **widened** type. That's
why this fails:

```ts
let s = "paid";               // s: string
const st: Status = s;         // ❌ string is not assignable to Status
```

Three fixes, in ascending order of quality:

```ts
const s = "paid";             // ✅ keep it const — it is a literal again
let s: Status = "paid";       // ✅ annotate the variable
const s = "paid" as const;    // ✅ assert the literal type explicitly
```

**Literal unions from input** need a runtime check, because input is `string`
and the compiler cannot know it's one of your three values:

```ts
const raw = readInput();                 // string
const s: Status = raw === "paid" ? "paid" : "pending";
```

That ternary is doing real work: it is the **validation** that justifies the
narrow type. Types describe intent; the check earns it.

**Numeric and boolean literals** work the same way, and are handy for
constrained numbers (`type Digit = 0 | 1 | ... | 9`) — though beyond a handful
of values a runtime range check is usually kinder.

> ⚠️ **Common mistakes:** typing a fixed set of options as `string`; being
> puzzled that a `let` won't fit a literal union (widening); and assuming the
> annotation validates input from outside the program.
""",
            warmup=[
                _q('`const a = "paid";` — the inferred type is…',
                   ["string", '"paid"', "any", "never"], 1,
                   "const cannot be reassigned, so the literal type survives."),
                _q('`let b = "paid";` — the inferred type is…',
                   ["string", '"paid"', "any", "never"], 0,
                   "let widens, because it might be reassigned."),
                _q('`type S = "a" | "b"; let x = "a"; const y: S = x;` is…',
                   ["fine", "an error — x widened to string", "a runtime error", "never"], 1,
                   "Widening is why `as const` and annotations exist."),
                _q("`type Flag = true | false` is the same as…",
                   ["string", "boolean", "never", "any"], 1,
                   "That union IS boolean."),
            ],
            exercises=[
                _ex("tscourse-w9-li-1", "A literal union",
                    "Alias Status to the three exact values and print the one chosen.",
                    'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = "pending";\nconsole.log(s);\n',
                    '"paid" | "pending" | "failed"', [("", "pending")],
                    hints=["Exact string values joined by |."]),
                _ex("tscourse-w9-li-2", "Validate then narrow",
                    "Turn the raw input into a Status: `paid` stays paid, anything else becomes `failed`.",
                    _LINE + 'type Status = "paid" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : "failed";\n'
                    'console.log(s);\n',
                    'line === "paid" ? "paid" : "failed"',
                    [("paid", "paid"), ("nonsense", "failed")],
                    hints=["A runtime check is what makes the narrow type honest.",
                           'Write line === "paid" ? "paid" : "failed".']),
                _ex("tscourse-w9-li-3", "Keep the literal with as const",
                    "Use `as const` so the value keeps its literal type, then print it.",
                    'type Status = "paid" | "failed";\n'
                    'const raw = "paid" as const;\nconst s: Status = raw;\nconsole.log(s);\n',
                    '"paid" as const', [("", "paid")],
                    hints=["`as const` pins the value's literal type.",
                           'Write "paid" as const.'],
                    difficulty="Medium"),
                _ex("tscourse-w9-li-4", "Numeric literals",
                    "Alias Dice to the six faces, then print the chosen face.",
                    _LINE + 'type Dice = 1 | 2 | 3 | 4 | 5 | 6;\n'
                    'const n = Number(line);\n'
                    'const d: Dice = n >= 1 && n <= 6 ? (n as Dice) : 1;\n'
                    'console.log(d);\n',
                    '1 | 2 | 3 | 4 | 5 | 6', [("4", "4"), ("9", "1")],
                    hints=["Numeric literal types are written the same way as string ones.",
                           "Write 1 | 2 | 3 | 4 | 5 | 6."],
                    difficulty="Medium"),
                _ex("tscourse-w9-li-5", "Map a literal to a label",
                    "Print `PAID` for paid, `PENDING` for pending, `FAILED` otherwise.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(s.toUpperCase());\n',
                    's.toUpperCase()',
                    [("paid", "PAID"), ("pending", "PENDING"), ("x", "FAILED")],
                    hints=["Every member of the union is a string, so string methods are available.",
                           "Write s.toUpperCase()."]),
                _fix("tscourse-w9-li-fix1", "Fix the widened let",
                     "This should print `paid`, but the value was declared in a way that loses its literal type. Fix the declaration.",
                     'type Status = "paid" | "failed";\n'
                     'let raw = "paid";\nconst s: Status = raw as Status;\nconsole.log(s);\n',
                     'type Status = "paid" | "failed";\n'
                     'const raw = "paid";\nconst s: Status = raw;\nconsole.log(s);\n',
                     [("", "paid")],
                     hints=["`let` widened the type to string, forcing a cast to paper over it.",
                            "Declare it with const and the cast becomes unnecessary."],
                     difficulty="Medium"),
                _fix("tscourse-w9-lit-fix2", "Fix the literal typo",
                     "Both lines come back unticked. The comparison is against a spelling that is not in the union at all — exactly the mistake literal types exist to catch.",
                     'type Status = "todo" | "done";\n'
                     'function icon(s: Status): string {\n'
                     '  if (s === ("Done" as Status)) return "[x]";\n'
                     '  return "[ ]";\n}\n'
                     'console.log(icon("done"));\n'
                     'console.log(icon("todo"));\n',
                     'type Status = "todo" | "done";\n'
                     'function icon(s: Status): string {\n'
                     '  if (s === "done") return "[x]";\n'
                     '  return "[ ]";\n}\n'
                     'console.log(icon("done"));\n'
                     'console.log(icon("todo"));\n',
                     [("", "[x]\n[ ]")],
                     hints=["The union has no member spelled with a capital letter.",
                            "Remove the assertion and compare against the exact literal \"done\"."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why does `const` infer a literal type but `let` does not?",
                   ["a bug", "a let might be reassigned, so the type must allow that",
                    "const is faster", "they behave identically"], 1,
                   "Widening follows mutability."),
                _q("`as const` is used to…",
                   ["convert at runtime", "keep the narrow literal type", "cast to string",
                    "make it readonly at runtime"], 1,
                   "It is a compile-time assertion about specificity."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w9-typeof", "Narrowing with typeof",
            "The workhorse guard for primitive unions.",
            """
`typeof` reports a value's runtime type as a string — and TypeScript
**understands** it, narrowing the type inside the branch:

```ts
function show(v: number | string): string {
  if (typeof v === "number") {
    return v.toFixed(2);      // v: number   ✅ toFixed allowed
  }
  return v.toUpperCase();     // v: string   ✅ the only remaining member
}
```

Notice the second `return` needs no check. Having ruled out `number`, only
`string` remains, and TypeScript knows it. This is **control-flow analysis**:
the type of `v` differs on each path through the function.

**What typeof actually reports** — memorise this table, including the two
warts:

| value | `typeof` |
|---|---|
| `42` | `"number"` |
| `"a"` | `"string"` |
| `true` | `"boolean"` |
| `undefined` | `"undefined"` |
| `() => 1` | `"function"` |
| `{}` | `"object"` |
| `[1,2]` | `"object"` ⚠️ |
| `null` | `"object"` ⚠️ |

The last two are the traps. **Arrays are objects** — use `Array.isArray(x)`.
**`null` is an object** — a bug from 1995 that can never be fixed without
breaking the web. So this is wrong:

```ts
if (typeof x === "object") {
  x.name;      // 💥 x might be null
}
```

and the fix is to test for null first:

```ts
if (x !== null && typeof x === "object") { ... }
```

**Narrowing works with early returns too**, which pairs perfectly with week 5's
guard clauses:

```ts
function len(v: string | number[]): number {
  if (typeof v === "string") return v.length;
  return v.length;              // v: number[] — also has length, but a different one
}
```

**It narrows variables, not arbitrary expressions.** `typeof obj.v === "string"`
does narrow `obj.v` for a `const` object, but if anything could reassign it in
between, TypeScript gives the narrowing up. Pull the value into a local `const`
first when a check seems mysteriously not to stick.

> ⚠️ **Common mistakes:** using `typeof x === "array"` (there is no such thing);
> forgetting `null` passes an `"object"` check; and comparing to a misspelled
> string like `"nunber"` — the comparison is just a string comparison, so it
> silently never matches. (TypeScript does catch this one for you.)
""",
            warmup=[
                _q('`typeof [1,2]` is…', ['"array"', '"object"', '"list"', '"number"'], 1,
                   "Arrays are objects at runtime."),
                _q('`typeof null` is…', ['"null"', '"object"', '"undefined"', '"boolean"'], 1,
                   "A permanent JavaScript wart."),
                _q('After `if (typeof v === "number")` with `v: number | string`, the ELSE branch has v as…',
                   ["number | string", "string", "any", "never"], 1,
                   "Ruling out one member leaves the other."),
                _q('`typeof (() => 1)` is…', ['"object"', '"function"', '"arrow"', '"number"'], 1,
                   "Functions get their own typeof result."),
            ],
            exercises=[
                _ex("tscourse-w9-tf-1", "Narrow a number",
                    "Format the value with 2 decimals when it is a number, otherwise uppercase it.",
                    _LINE + 'const v: number | string = line === "x" ? "abc" : 3.14159;\n'
                    'if (typeof v === "number") {\n  console.log(v.toFixed(2));\n} else {\n  console.log(v.toUpperCase());\n}\n',
                    'typeof v === "number"',
                    [("n", "3.14"), ("x", "ABC")],
                    hints=["Compare typeof against the type name as a string.",
                           'Write typeof v === "number".']),
                _ex("tscourse-w9-tf-2", "Guard-clause style",
                    "Return early for the string case, then handle the number.",
                    _LINE + 'function show(v: number | string): string {\n'
                    '  if (typeof v === "string") return v.toUpperCase();\n'
                    '  return v.toFixed(2);\n}\n'
                    'console.log(show(line === "x" ? "abc" : 3.14159));\n',
                    'if (typeof v === "string") return v.toUpperCase();',
                    [("x", "ABC"), ("n", "3.14")],
                    hints=["Reject one member up front, and the rest of the body is the other.",
                           'Write if (typeof v === "string") return v.toUpperCase();'],
                    difficulty="Medium"),
                _ex("tscourse-w9-tf-3", "Label it by member",
                    "Print `chars: 5` for a string and `items: 3` for an array.",
                    _LINE + 'const v: string | number[] = line === "a" ? [1, 2, 3] : "hello";\n'
                    'console.log(typeof v === "string" ? `chars: ${v.length}` : `items: ${v.length}`);\n',
                    'typeof v === "string" ? `chars: ${v.length}` : `items: ${v.length}`',
                    [("a", "items: 3"), ("b", "chars: 5")],
                    hints=["Both members have a length, but they mean different things — so the branch decides the wording.",
                           "Write typeof v === \"string\" ? `chars: ${v.length}` : `items: ${v.length}`."],
                    difficulty="Medium"),
                _ex("tscourse-w9-tf-4", "Count by runtime type",
                    "Print how many entries in the mixed list are numbers.",
                    'const mixed: (string | number)[] = [1, "a", 2, "b", 3];\n'
                    'console.log(mixed.filter((x) => typeof x === "number").length);\n',
                    'typeof x === "number"', [("", "3")],
                    hints=["Filter by the runtime type of each element."]),
                _ex("tscourse-w9-tf-5", "Null-safe object check",
                    "Print `object` only for a real object, `null` for null, `other` otherwise.",
                    _LINE + 'const v: object | null | string = line === "o" ? {} : line === "z" ? null : "s";\n'
                    'if (v === null) {\n  console.log("null");\n} else if (typeof v === "object") {\n  console.log("object");\n} else {\n  console.log("other");\n}\n',
                    'v === null',
                    [("o", "object"), ("z", "null"), ("q", "other")],
                    hints=["typeof null is \"object\", so null must be ruled out first.",
                           "Test v === null before the typeof check."],
                    difficulty="Medium"),
                _fix("tscourse-w9-tf-fix1", "Fix the array check",
                     "There is no `\"array\"` typeof, so this always prints `not`. Fix it so an array prints `array`.",
                     'const v: string | number[] = [1, 2, 3];\n'
                     'console.log(typeof v === "array" ? "array" : "not");\n',
                     'const v: string | number[] = [1, 2, 3];\n'
                     'console.log(Array.isArray(v) ? "array" : "not");\n',
                     [("", "array")],
                     hints=['typeof an array is "object", never "array".',
                            "Use Array.isArray(v)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Control-flow analysis means…",
                   ["the code runs faster", "the type of a variable differs along different branches",
                    "types are checked at runtime", "loops are unrolled"], 1,
                   "TypeScript tracks what each check has proved."),
                _q("`if (typeof x === \"object\") x.name;` is unsafe because…",
                   ["objects have no name", "null also passes that check", "typeof is slow",
                    "it is fine"], 1,
                   "Rule out null explicitly."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w9-equality", "Narrowing by equality & switch",
            "Comparing against literals, and dispatching on them.",
            """
For a union of **literal types**, `typeof` is useless — every member is a
string. Compare against the values instead:

```ts
type Status = "paid" | "pending" | "failed";

function label(s: Status): string {
  if (s === "paid") {
    return "Settled";       // s: "paid"
  }
  return "Outstanding";     // s: "pending" | "failed"
}
```

Notice the else branch: TypeScript has removed only the member you ruled out.
The remaining type is still a union — a smaller one.

**`switch` narrows the same way**, and reads much better with three or more
cases:

```ts
switch (s) {
  case "paid":    return "Settled";      // s: "paid"
  case "pending": return "Waiting";      // s: "pending"
  case "failed":  return "Rejected";     // s: "failed"
}
```

Each `case` narrows to exactly one member inside its arm. And because every
member is covered, TypeScript can see the function always returns — no `default`
needed, and no "not all code paths return a value" error. That's a small miracle
that only works because the type is a finite union.

**Narrowing by equality between two unions** also works, and is occasionally
handy:

```ts
function f(a: string | number, b: string | boolean) {
  if (a === b) {
    // both must be string — the only overlap
  }
}
```

**`!==` narrows the negative side**, which is how you strip `undefined`:

```ts
function g(v: string | undefined): string {
  if (v === undefined) return "(none)";
  return v.toUpperCase();      // v: string
}
```

**Narrowing survives assignment.** Assigning a value to a union-typed variable
narrows it from that point on:

```ts
let v: string | number;
v = "hi";
v.toUpperCase();      // ✅ TypeScript knows it is a string right now
```

> ⚠️ **Common mistakes:** using `==` and getting unexpected coercion; assuming
> the else branch narrows to a single member when the union had three; and
> adding a `default` that returns something bogus, which silently disables the
> exhaustiveness benefit you'll meet in lesson 7.
""",
            warmup=[
                _q('With `s: "a"|"b"|"c"`, after `if (s === "a")` the ELSE branch is…',
                   ['"a"', '"b" | "c"', "string", "never"], 1,
                   "Only the tested member is removed."),
                _q("A switch covering every member of a literal union…",
                   ["still needs a default to compile", "can omit default and still be seen to always return",
                    "cannot narrow", "is an error"], 1,
                   "Exhaustiveness is visible to the compiler."),
                _q("`if (v === undefined) return; ` then `v` is…",
                   ["still the union", "the union minus undefined", "any", "never"], 1,
                   "The negative branch is narrowed too."),
                _q("`let v: string | number; v = 5; v.toFixed(2)` is…",
                   ["an error", "fine — assignment narrowed it", "a runtime error", "undefined"], 1,
                   "Narrowing by assignment."),
            ],
            exercises=[
                _ex("tscourse-w9-eq-1", "Compare to a literal",
                    "Return `Settled` for paid and `Outstanding` for anything else.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(s === "paid" ? "Settled" : "Outstanding");\n',
                    's === "paid" ? "Settled" : "Outstanding"',
                    [("paid", "Settled"), ("pending", "Outstanding"), ("x", "Outstanding")],
                    hints=["Compare the value against the literal member.",
                           'Write s === "paid" ? "Settled" : "Outstanding".']),
                _ex("tscourse-w9-eq-2", "Switch on a union",
                    "Complete the pending case so it prints `Waiting`.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'switch (s) {\n'
                    '  case "paid":\n    console.log("Settled");\n    break;\n'
                    '  case "pending":\n    console.log("Waiting");\n    break;\n'
                    '  case "failed":\n    console.log("Rejected");\n    break;\n'
                    '}\n',
                    'case "pending":\n    console.log("Waiting");\n    break;',
                    [("paid", "Settled"), ("pending", "Waiting"), ("x", "Rejected")],
                    hints=["A case label, the statement, then break.",
                           'Write case "pending": console.log("Waiting"); break;'],
                    difficulty="Medium"),
                _ex("tscourse-w9-eq-3", "Strip the undefined",
                    "Return `(none)` when the value is missing, else the value uppercased.",
                    _LINE + 'function g(v: string | undefined): string {\n'
                    '  if (v === undefined) return "(none)";\n'
                    '  return v.toUpperCase();\n}\n'
                    'console.log(g(line === "z" ? undefined : line));\n',
                    'if (v === undefined) return "(none)";',
                    [("z", "(none)"), ("hi", "HI")],
                    hints=["Reject the undefined case first, and the rest is a plain string.",
                           'Write if (v === undefined) return "(none)";'],
                    difficulty="Medium"),
                _ex("tscourse-w9-eq-4", "Two of three",
                    "Print `open` for pending or failed, `closed` for paid.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(s === "pending" || s === "failed" ? "open" : "closed");\n',
                    's === "pending" || s === "failed"',
                    [("pending", "open"), ("x", "open"), ("paid", "closed")],
                    hints=["Two members share an outcome, so test for either.",
                           'Write s === "pending" || s === "failed".']),
                _ex("tscourse-w9-eq-5", "Narrow by assignment",
                    "Assign a string, then use a string method with no further checking.",
                    'let v: string | number;\nv = "hi";\nconsole.log(v.toUpperCase());\n',
                    'v = "hi";', [("", "HI")],
                    hints=["Assigning a value narrows the variable from that point on.",
                           'Write v = "hi";']),
                _fix("tscourse-w9-eq-fix1", "Fix the missing break",
                     "For `paid` this prints two lines. Fix it so each status prints exactly one.",
                     _LINE + 'type Status = "paid" | "pending";\n'
                     'const s: Status = line === "paid" ? "paid" : "pending";\n'
                     'switch (s) {\n'
                     '  case "paid":\n    console.log("Settled");\n'
                     '  case "pending":\n    console.log("Waiting");\n    break;\n'
                     '}\n',
                     _LINE + 'type Status = "paid" | "pending";\n'
                     'const s: Status = line === "paid" ? "paid" : "pending";\n'
                     'switch (s) {\n'
                     '  case "paid":\n    console.log("Settled");\n    break;\n'
                     '  case "pending":\n    console.log("Waiting");\n    break;\n'
                     '}\n',
                     [("paid", "Settled"), ("pending", "Waiting")],
                     hints=["Without break, execution falls into the next case.",
                            "Add break; to the paid case."],
                     difficulty="Medium"),
                _fix("tscourse-w9-eq-fix2", "Fix the fallthrough",
                     "This should print `1 2 3`. One case forgets to break, so it runs on into the next one and overwrites its own answer.",
                     'type Level = "low" | "mid" | "high";\n'
                     'function score(l: Level): number {\n'
                     '  let n = 0;\n'
                     '  switch (l) {\n'
                     '    case "low":\n'
                     '      n = 1;\n'
                     '    case "mid":\n'
                     '      n = 2;\n'
                     '      break;\n'
                     '    case "high":\n'
                     '      n = 3;\n'
                     '      break;\n'
                     '  }\n'
                     '  return n;\n}\n'
                     'console.log(`${score("low")} ${score("mid")} ${score("high")}`);\n',
                     'type Level = "low" | "mid" | "high";\n'
                     'function score(l: Level): number {\n'
                     '  let n = 0;\n'
                     '  switch (l) {\n'
                     '    case "low":\n'
                     '      n = 1;\n'
                     '      break;\n'
                     '    case "mid":\n'
                     '      n = 2;\n'
                     '      break;\n'
                     '    case "high":\n'
                     '      n = 3;\n'
                     '      break;\n'
                     '  }\n'
                     '  return n;\n}\n'
                     'console.log(`${score("low")} ${score("mid")} ${score("high")}`);\n',
                     [("", "1 2 3")],
                     hints=["A case without break keeps running into the case below it.",
                            "This is why a switch of returns is safer than a switch of assignments."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why does typeof not help with `\"a\" | \"b\"`?",
                   ["typeof is broken", "every member is a string, so typeof cannot tell them apart",
                    "literals have no typeof", "it does help"], 1,
                   "Compare against the values instead."),
                _q("A `default` branch that returns a placeholder…",
                   ["is best practice", "hides a forgotten case from the exhaustiveness check",
                    "is required", "narrows better"], 1,
                   "It makes the compiler stop warning you."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w9-guards", "The other guards",
            "Truthiness, in, Array.isArray and instanceof.",
            """
Four more ways to narrow, each for a situation the previous two don't cover.

**Truthiness** removes every falsy member at once:

```ts
function f(v: string | undefined | null) {
  if (v) {
    v.toUpperCase();     // v: string
  }
}
```

Convenient — and it also removes `""`, which may be a legitimate value. When
the empty string or `0` matters, be explicit:

```ts
if (v !== undefined && v !== null) { ... }
if (v != null) { ... }        // the one accepted use of != : catches both
```

**`Array.isArray`** is the correct array test, because `typeof` says
`"object"`:

```ts
function count(v: string | string[]): number {
  if (Array.isArray(v)) return v.length;    // v: string[]
  return 1;                                  // v: string
}
```

**`in`** distinguishes object shapes by the presence of a key — the tool for a
union of objects with **no** shared tag:

```ts
type Contact = { email: string } | { phone: string };

function reach(c: Contact): string {
  if ("email" in c) {
    return c.email;      // c: { email: string }
  }
  return c.phone;        // c: { phone: string }
}
```

**`instanceof`** narrows against a class or constructor. The everyday case is
error handling:

```ts
try {
  risky();
} catch (e) {
  if (e instanceof Error) {
    console.log(e.message);    // e: Error
  }
}
```

(A caught `e` is `unknown` in modern TypeScript, precisely so you're forced to
check.)

**Choosing a guard:**

| the union is… | use |
|---|---|
| primitives (`number \\| string`) | `typeof` |
| literal values (`"a" \\| "b"`) | `===` or `switch` |
| maybe-missing (`T \\| undefined`) | `=== undefined`, or truthiness if safe |
| array or not | `Array.isArray` |
| object shapes without a tag | `in` |
| class instances | `instanceof` |
| object shapes **with** a tag | `switch` on the tag ← next lesson, and the best option |

> ⚠️ **Common mistakes:** using truthiness on a union containing `0` or `""`;
> using `typeof x === "object"` for arrays; and using `in` with a variable key
> (`k in obj` narrows nothing useful — it needs a literal).
""",
            warmup=[
                _q("`if (v)` on `string | undefined` also removes…",
                   ["nothing else", "the empty string", "numbers", "null only"], 1,
                   '"" is falsy, so a legitimate empty string is excluded too.'),
                _q("The correct array test is…",
                   ['typeof x === "array"', "Array.isArray(x)", "x instanceof Array only",
                    "x.length !== undefined"], 1,
                   "typeof can never say \"array\"."),
                _q('`"email" in c` narrows a union of object shapes by…',
                   ["their names", "the presence of that key", "their length", "typeof"], 1,
                   "Useful when there is no shared tag."),
                _q("In modern TypeScript a caught `e` in `catch (e)` has type…",
                   ["Error", "any", "unknown", "string"], 2,
                   "Which forces you to narrow before using it."),
            ],
            exercises=[
                _ex("tscourse-w9-gu-1", "Truthiness guard",
                    "Print the value uppercased, or `(none)` when it is missing or empty.",
                    _LINE + 'const v: string | undefined = line === "z" ? undefined : line;\n'
                    'console.log(v ? v.toUpperCase() : "(none)");\n',
                    'v ? v.toUpperCase() : "(none)"',
                    [("hi", "HI"), ("z", "(none)")],
                    hints=["A truthiness test removes undefined (and empty strings).",
                           'Write v ? v.toUpperCase() : "(none)".']),
                _ex("tscourse-w9-gu-2", "Keep a legitimate zero",
                    "Print the number, treating only a genuinely missing value as `(none)`.",
                    _LINE + 'const v: number | undefined = line === "z" ? undefined : Number(line);\n'
                    'console.log(v !== undefined ? v : "(none)");\n',
                    'v !== undefined ? v : "(none)"',
                    [("0", "0"), ("z", "(none)"), ("7", "7")],
                    hints=["Truthiness would discard the 0.",
                           'Write v !== undefined ? v : "(none)".'],
                    difficulty="Medium"),
                _ex("tscourse-w9-gu-3", "Array or single",
                    "Return the number of items: the array's length, or 1 for a lone string.",
                    _LINE + 'function count(v: string | string[]): number {\n'
                    '  if (Array.isArray(v)) return v.length;\n'
                    '  return 1;\n}\n'
                    'console.log(count(line === "a" ? ["x", "y", "z"] : "solo"));\n',
                    'if (Array.isArray(v)) return v.length;',
                    [("a", "3"), ("b", "1")],
                    hints=["typeof cannot tell an array from an object.",
                           "Write if (Array.isArray(v)) return v.length;"],
                    difficulty="Medium"),
                _ex("tscourse-w9-gu-4", "Narrow with in",
                    "Return the email when present, otherwise the phone.",
                    _LINE + 'type Contact = { email: string } | { phone: string };\n'
                    'function reach(c: Contact): string {\n'
                    '  if ("email" in c) return c.email;\n'
                    '  return c.phone;\n}\n'
                    'console.log(reach(line === "e" ? { email: "a@b.c" } : { phone: "123" }));\n',
                    'if ("email" in c) return c.email;',
                    [("e", "a@b.c"), ("p", "123")],
                    hints=["These shapes share no tag, so test for a key.",
                           'Write if ("email" in c) return c.email;'],
                    difficulty="Medium"),
                _ex("tscourse-w9-gu-5", "Narrow a caught error",
                    "Print the error's message when it is a real Error, otherwise `unknown error`.",
                    'function risky(): void {\n  throw new Error("boom");\n}\n'
                    'try {\n  risky();\n} catch (e) {\n'
                    '  console.log(e instanceof Error ? e.message : "unknown error");\n}\n',
                    'e instanceof Error ? e.message : "unknown error"',
                    [("", "boom")],
                    hints=["A caught value is unknown until you check it.",
                           'Write e instanceof Error ? e.message : "unknown error".'],
                    difficulty="Medium"),
                _fix("tscourse-w9-gu-fix1", "Fix the discarded zero",
                     "A value of 0 is real data, but this prints `(none)`. Fix it.",
                     _LINE + 'const v: number | undefined = line === "z" ? undefined : Number(line);\n'
                     'console.log(v ? v : "(none)");\n',
                     _LINE + 'const v: number | undefined = line === "z" ? undefined : Number(line);\n'
                     'console.log(v !== undefined ? v : "(none)");\n',
                     [("0", "0"), ("z", "(none)"), ("7", "7")],
                     hints=["0 is falsy, so the truthiness guard rejects it.",
                            "Test explicitly against undefined."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`if (v != null)` catches…",
                   ["only null", "only undefined", "both null and undefined",
                    "every falsy value"], 2,
                   "The single defensible use of loose inequality."),
                _q("You have a union of object shapes with no shared field name. Use…",
                   ["typeof", "in", "Array.isArray", "==="], 1,
                   "`in` distinguishes by key presence."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w9-discriminated", "Discriminated unions",
            "The pattern that makes 'one of several shapes' pleasant.",
            """
This is the most important idea in the week, and one of the most important in
TypeScript.

A **discriminated union** is a union of object types that all carry a **literal
field in common** — the *discriminant*, or *tag*:

```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number }
  | { kind: "rect"; w: number; h: number };
```

Every member has `kind`, and each `kind` is a different literal. Switch on it
and TypeScript narrows to exactly one member per arm:

```ts
function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return 3.14159 * s.r * s.r;    // s.r exists here
    case "square": return s.side * s.side;         // s.side exists here
    case "rect":   return s.w * s.h;
  }
}
```

Inside `case "circle"` you may read `s.r` and **may not** read `s.side` — the
compiler knows which member you have. No casts, no optional fields, no
defensive checks.

**Why this beats optional fields.** The alternative people reach for first:

```ts
interface Shape { kind: string; r?: number; side?: number; w?: number; h?: number }
```

That type permits `{ kind: "circle", side: 3 }` and `{ kind: "banana" }`, and
every read needs a `?? 0`. The discriminated union makes those states
**unrepresentable** — the phrase from week 8, now with teeth.

**The canonical use: results that might fail.**

```ts
type Result =
  | { ok: true; value: number }
  | { ok: false; error: string };

function show(r: Result): string {
  if (r.ok) {
    return `= ${r.value}`;     // value exists only on the success member
  }
  return `! ${r.error}`;
}
```

Note the discriminant here is a **boolean literal** (`true` / `false`), and a
plain `if (r.ok)` narrows it. The tag doesn't have to be a string.

**Naming the tag.** `kind`, `type`, `status`, `ok` — anything, as long as it is
consistent and its values are literal types. `type` is common in the wider
ecosystem; `kind` avoids clashing with the keyword in your own reading.

**Modelling state** is the other everyday use, and it kills a whole class of
bug:

```ts
type Load =
  | { kind: "loading" }
  | { kind: "loaded"; items: string[] }
  | { kind: "failed"; error: string };
```

There is now no way to be loading *and* have items, or failed *and* have no
error.

> ⚠️ **Common mistakes:** giving the tag a non-literal type (`kind: string`),
> which disables all narrowing; forgetting the tag on one member; and using a
> different field name for the tag in different members.
""",
            warmup=[
                _q("A discriminated union's tag must be…",
                   ["a string", "a literal type", "optional", "a number"], 1,
                   "`kind: string` would narrow nothing."),
                _q('In `case "circle":` of a switch on `s.kind`, `s` is…',
                   ["the whole union", "just the circle member", "any", "never"], 1,
                   "That is the whole payoff."),
                _q("`type R = {ok: true; value: number} | {ok: false; error: string}` — after `if (r.ok)`, `r.error` is…",
                   ["available", "a compile error", "undefined", "any"], 1,
                   "The success member has no error field."),
                _q("Compared with optional fields, a discriminated union…",
                   ["is longer to write only", "makes invalid combinations unrepresentable",
                    "is slower", "needs classes"], 1,
                   "The type itself rules out nonsense."),
            ],
            exercises=[
                _ex("tscourse-w9-di-1", "Switch on the tag",
                    "Complete the square case so it returns side squared.",
                    _LINE + 'type Shape =\n'
                    '  | { kind: "circle"; r: number }\n'
                    '  | { kind: "square"; side: number };\n'
                    'function area(s: Shape): number {\n'
                    '  switch (s.kind) {\n'
                    '    case "circle":\n      return 3 * s.r * s.r;\n'
                    '    case "square":\n      return s.side * s.side;\n'
                    '  }\n}\n'
                    'console.log(area(line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 }));\n',
                    'return s.side * s.side;', [("c", "12"), ("s", "16")],
                    hints=["Inside this case the compiler knows the member has `side`.",
                           "Write return s.side * s.side;"],
                    difficulty="Medium"),
                _ex("tscourse-w9-di-2", "Build a valid member",
                    "Construct the circle member — it needs the tag AND that member's own field.",
                    _LINE + 'type Shape =\n'
                    '  | { kind: "circle"; r: number }\n'
                    '  | { kind: "square"; side: number };\n'
                    'const s: Shape = line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 };\n'
                    'console.log(s.kind);\n',
                    '{ kind: "circle", r: 2 }',
                    [("c", "circle"), ("s", "square")],
                    hints=["A member must carry its literal tag and exactly the fields that member declares.",
                           'Write { kind: "circle", r: 2 }.'],
                    difficulty="Medium"),
                _ex("tscourse-w9-di-3", "A Result type",
                    "Print `= <value>` on success and `! <error>` on failure.",
                    _LINE + 'type Result =\n'
                    '  | { ok: true; value: number }\n'
                    '  | { ok: false; error: string };\n'
                    'const n = Number(line);\n'
                    'const r: Result = Number.isNaN(n) ? { ok: false, error: "not a number" } : { ok: true, value: n };\n'
                    'console.log(r.ok ? `= ${r.value}` : `! ${r.error}`);\n',
                    'r.ok ? `= ${r.value}` : `! ${r.error}`',
                    [("42", "= 42"), ("abc", "! not a number")],
                    hints=["A boolean tag narrows with a plain truthiness test.",
                           "Write r.ok ? `= ${r.value}` : `! ${r.error}`."],
                    difficulty="Medium"),
                _ex("tscourse-w9-di-4", "Build the failure case",
                    "Return the failing Result when the input does not parse.",
                    _LINE + 'type Result =\n'
                    '  | { ok: true; value: number }\n'
                    '  | { ok: false; error: string };\n'
                    'function parse(s: string): Result {\n'
                    '  const n = Number(s);\n'
                    '  if (Number.isNaN(n)) return { ok: false, error: "bad" };\n'
                    '  return { ok: true, value: n };\n}\n'
                    'const r = parse(line);\nconsole.log(r.ok ? r.value : r.error);\n',
                    'return { ok: false, error: "bad" };',
                    [("7", "7"), ("zz", "bad")],
                    hints=["The failure member carries the tag AND the error field.",
                           'Write return { ok: false, error: "bad" };'],
                    difficulty="Medium"),
                _ex("tscourse-w9-di-5", "Model a loading state",
                    "Print `loading`, `n items`, or `error: <msg>` for each state.",
                    _LINE + 'type Load =\n'
                    '  | { kind: "loading" }\n'
                    '  | { kind: "loaded"; items: string[] }\n'
                    '  | { kind: "failed"; error: string };\n'
                    'const st: Load =\n'
                    '  line === "l" ? { kind: "loading" }\n'
                    '  : line === "d" ? { kind: "loaded", items: ["a", "b"] }\n'
                    '  : { kind: "failed", error: "oops" };\n'
                    'switch (st.kind) {\n'
                    '  case "loading":\n    console.log("loading");\n    break;\n'
                    '  case "loaded":\n    console.log(`${st.items.length} items`);\n    break;\n'
                    '  case "failed":\n    console.log(`error: ${st.error}`);\n    break;\n'
                    '}\n',
                    'console.log(`${st.items.length} items`);',
                    [("l", "loading"), ("d", "2 items"), ("f", "error: oops")],
                    hints=["Only the loaded member has items, and only inside its case.",
                           "Write console.log(`${st.items.length} items`);"],
                    difficulty="Medium"),
                _fix("tscourse-w9-di-fix1", "Fix the untagged union",
                     "The tag was typed as `string`, so narrowing is impossible and this reads the wrong field. Give each member a literal tag and read the right one.",
                     _LINE + 'type Shape =\n'
                     '  | { kind: string; r: number }\n'
                     '  | { kind: string; side: number };\n'
                     'const s: Shape = line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 };\n'
                     'console.log(s.kind === "circle" ? 12 : 12);\n',
                     _LINE + 'type Shape =\n'
                     '  | { kind: "circle"; r: number }\n'
                     '  | { kind: "square"; side: number };\n'
                     'const s: Shape = line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 };\n'
                     'console.log(s.kind === "circle" ? 3 * s.r * s.r : s.side * s.side);\n',
                     [("c", "12"), ("s", "16")],
                     hints=["`kind: string` is not a literal type, so no narrowing happens and the areas had to be hard-coded.",
                            'Change the tags to the literals "circle" and "square", then compute each area from the member\'s own field.'],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The discriminant of a union must be…",
                   ["named kind", "a literal-typed field present on every member", "a string",
                    "optional"], 1,
                   "The name is free; being a literal on every member is not."),
                _q("A Result union beats returning `number | null` because…",
                   ["it is shorter", "the failure can carry an explanation, and success cannot be confused with it",
                    "it is faster", "null is banned"], 1,
                   "You get the reason, not just the absence."),
                _q("`{ kind: \"circle\", side: 3 }` against a proper Shape union is…",
                   ["allowed", "a compile error", "allowed but undefined", "a runtime error"], 1,
                   "The tag and the fields must agree — that is the whole point."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w9-exhaustive", "Exhaustiveness & intersections",
            "Making the compiler catch the case you forgot.",
            """
Discriminated unions give you one more thing, and it is the reason experienced
people reach for them: **the compiler can prove you handled every case.**

Start with a `never` refresher. `never` is the type with **no values** — the
type of a situation that cannot happen. If you've handled every member of a
union, the value that reaches the `default` branch has type `never`, because
nothing is left.

```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return 3.14159 * s.r * s.r;
    case "square": return s.side * s.side;
    default: {
      const _exhaustive: never = s;      // ✅ compiles: s is never here
      return _exhaustive;
    }
  }
}
```

Now **add a third member** to `Shape` and forget to handle it. `s` in the
`default` is no longer `never` — it's the new member — so
`const _exhaustive: never = s;` **fails to compile**, pointing straight at the
function you forgot to update.

That is a genuinely powerful property: adding a case to a type produces a list
of every place that must change. It's why "make the illegal states
unrepresentable" pays off — the compiler becomes a to-do list.

**Without the trick**, a forgotten case falls through the `default` and returns
something plausible-but-wrong at runtime. With it, the code doesn't build.

**A note on returns.** If every case returns and you *don't* write a `default`,
TypeScript already knows the switch is exhaustive and won't complain about a
missing return. Adding the `never` check makes that guarantee explicit and
survives someone later adding a member.

---

**Intersections** are the other half of the type algebra. Where `A | B` is
"either", `A & B` is **both**:

```ts
type Timestamped = { created: string };
type Named = { name: string };

type Entry = Timestamped & Named;      // has created AND name

const e: Entry = { created: "mon", name: "coffee" };   // both required
```

Use them to bolt a common set of fields onto several types:

```ts
type WithId<T> = T & { id: string };    // (generics arrive next week)
```

**Union and intersection pull in opposite directions.** A union has *fewer*
usable members (only the shared ones); an intersection has *more* (all of them).
Beginners routinely expect the opposite, because "union" sounds bigger. The
rule: a union is a bigger set of **values**, and therefore a smaller set of
**guaranteed members**.

Intersecting incompatible primitives gives `never` — no value can be both:

```ts
type Impossible = string & number;      // never
```

> ⚠️ **Common mistakes:** adding a `default` that returns a fallback, which
> silently defeats exhaustiveness; expecting `A | B` to give you the members of
> both; and forgetting that the `never` check must actually *assign* the value
> to a `never`-typed name.
""",
            warmup=[
                _q("`never` is the type of…",
                   ["null", "a value that cannot exist", "undefined", "any value"], 1,
                   "It has no values at all."),
                _q("In an exhaustive switch's default, the value has type…",
                   ["the union", "never", "any", "unknown"], 1,
                   "Every member was removed by a case."),
                _q("Adding a member to the union and forgetting a case makes the never check…",
                   ["still compile", "fail to compile, pointing at the switch", "throw at runtime",
                    "warn only"], 1,
                   "Which is exactly the point."),
                _q("`A & B` gives a value with…",
                   ["either A's or B's members", "all of A's and B's members", "no members",
                    "only shared members"], 1,
                   "Intersection combines; union restricts."),
            ],
            exercises=[
                _ex("tscourse-w9-ex-1", "Add the exhaustiveness check",
                    "Complete the default branch so a forgotten case would fail to compile.",
                    _LINE + 'type Shape =\n'
                    '  | { kind: "circle"; r: number }\n'
                    '  | { kind: "square"; side: number };\n'
                    'function area(s: Shape): number {\n'
                    '  switch (s.kind) {\n'
                    '    case "circle":\n      return 3 * s.r * s.r;\n'
                    '    case "square":\n      return s.side * s.side;\n'
                    '    default: {\n'
                    '      const _exhaustive: never = s;\n'
                    '      return _exhaustive;\n'
                    '    }\n'
                    '  }\n}\n'
                    'console.log(area(line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 }));\n',
                    'const _exhaustive: never = s;', [("c", "12"), ("s", "16")],
                    hints=["Assign the leftover value to a name annotated as never.",
                           "Write const _exhaustive: never = s;"],
                    difficulty="Medium"),
                _ex("tscourse-w9-ex-2", "Handle the new case",
                    "A third shape was added. Handle it so the switch stays exhaustive.",
                    _LINE + 'type Shape =\n'
                    '  | { kind: "circle"; r: number }\n'
                    '  | { kind: "square"; side: number }\n'
                    '  | { kind: "rect"; w: number; h: number };\n'
                    'function area(s: Shape): number {\n'
                    '  switch (s.kind) {\n'
                    '    case "circle":\n      return 3 * s.r * s.r;\n'
                    '    case "square":\n      return s.side * s.side;\n'
                    '    case "rect":\n      return s.w * s.h;\n'
                    '    default: {\n'
                    '      const _exhaustive: never = s;\n'
                    '      return _exhaustive;\n'
                    '    }\n'
                    '  }\n}\n'
                    'console.log(area(line === "r" ? { kind: "rect", w: 2, h: 5 } : { kind: "square", side: 4 }));\n',
                    'case "rect":\n      return s.w * s.h;', [("r", "10"), ("s", "16")],
                    hints=["The new member has w and h.",
                           'Write case "rect": return s.w * s.h;'],
                    difficulty="Medium"),
                _ex("tscourse-w9-ex-3", "An intersection",
                    "Combine the two shapes with & so the value must have both fields.",
                    'type Timestamped = { created: string };\n'
                    'type Named = { name: string };\n'
                    'type Entry = Timestamped & Named;\n'
                    'const e: Entry = { created: "mon", name: "coffee" };\n'
                    'console.log(`${e.created} ${e.name}`);\n',
                    'Timestamped & Named', [("", "mon coffee")],
                    hints=["& means 'has all the members of both'.",
                           "Write Timestamped & Named."]),
                _ex("tscourse-w9-ex-4", "Extend records with a shared field",
                    "Total the amounts across records that carry both an id and an amount.",
                    'type WithId = { id: string };\n'
                    'type Amounted = { amount: number };\n'
                    'const rows: (WithId & Amounted)[] = [\n'
                    '  { id: "a", amount: 3 },\n  { id: "b", amount: 12 },\n];\n'
                    'console.log(rows.reduce((s, r) => s + r.amount, 0));\n',
                    '(WithId & Amounted)[]', [("", "15")],
                    hints=["Each element has all the members of both types.",
                           "Write (WithId & Amounted)[]."],
                    difficulty="Medium"),
                _ex("tscourse-w9-ex-5", "Exhaustive over a status",
                    "Complete the failed case so every Status is handled.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'function label(s: Status): string {\n'
                    '  switch (s) {\n'
                    '    case "paid":\n      return "Settled";\n'
                    '    case "pending":\n      return "Waiting";\n'
                    '    case "failed":\n      return "Rejected";\n'
                    '    default: {\n'
                    '      const _exhaustive: never = s;\n      return _exhaustive;\n'
                    '    }\n'
                    '  }\n}\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(label(s));\n',
                    'case "failed":\n      return "Rejected";',
                    [("paid", "Settled"), ("pending", "Waiting"), ("x", "Rejected")],
                    hints=["Without this case the never check would not compile.",
                           'Write case "failed": return "Rejected";'],
                    difficulty="Medium"),
                _fix("tscourse-w9-ex-fix1", "Fix the defeated exhaustiveness",
                     "The default returns a bogus 0, hiding the unhandled `rect` case — so a rect prints 0 instead of 10. Handle rect properly.",
                     _LINE + 'type Shape =\n'
                     '  | { kind: "circle"; r: number }\n'
                     '  | { kind: "square"; side: number }\n'
                     '  | { kind: "rect"; w: number; h: number };\n'
                     'function area(s: Shape): number {\n'
                     '  switch (s.kind) {\n'
                     '    case "circle":\n      return 3 * s.r * s.r;\n'
                     '    case "square":\n      return s.side * s.side;\n'
                     '    default:\n      return 0;\n'
                     '  }\n}\n'
                     'console.log(area(line === "r" ? { kind: "rect", w: 2, h: 5 } : { kind: "square", side: 4 }));\n',
                     _LINE + 'type Shape =\n'
                     '  | { kind: "circle"; r: number }\n'
                     '  | { kind: "square"; side: number }\n'
                     '  | { kind: "rect"; w: number; h: number };\n'
                     'function area(s: Shape): number {\n'
                     '  switch (s.kind) {\n'
                     '    case "circle":\n      return 3 * s.r * s.r;\n'
                     '    case "square":\n      return s.side * s.side;\n'
                     '    case "rect":\n      return s.w * s.h;\n'
                     '    default: {\n'
                     '      const _exhaustive: never = s;\n      return _exhaustive;\n'
                     '    }\n'
                     '  }\n}\n'
                     'console.log(area(line === "r" ? { kind: "rect", w: 2, h: 5 } : { kind: "square", side: 4 }));\n',
                     [("r", "10"), ("s", "16")],
                     hints=["A plausible fallback in default is what let the missing case through silently.",
                            "Handle rect, and replace the fallback with the never check so the next omission is caught."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The never trick works because…",
                   ["never is a runtime check", "an unhandled member is not assignable to never",
                    "it throws", "default always runs"], 1,
                   "The assignment fails to compile precisely when a case remains."),
                _q("A union has ____ guaranteed members than any single member.",
                   ["more", "fewer or equal", "the same", "infinitely many"], 1,
                   "Only what all members share is usable."),
                _q("`string & number` is…",
                   ["string", "number", "never", "any"], 2,
                   "No value can be both, so the type is empty."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w9-predicates", "Custom type guards",
            "Teach the compiler to narrow through a function you wrote yourself.",
            """
Every narrowing you have done so far happened **inline** — `typeof`, `===`, `in`,
a `switch` on `kind`. The moment you move that test into a helper, the narrowing
evaporates:

```ts
function isCircle(s: Shape): boolean {
  return s.kind === "circle";
}

if (isCircle(s)) {
  console.log(s.r);    // ✗ Property 'r' does not exist on type 'Shape'
}
```

TypeScript sees a function returning `boolean`. It has no idea *what* that
boolean means. You have to say so — in the return position:

```ts
function isCircle(s: Shape): s is Circle {   // ← a type predicate
  return s.kind === "circle";
}

if (isCircle(s)) {
  console.log(s.r);    // ✓ narrowed to Circle
}
```

`s is Circle` reads: *"when this returns true, the argument named `s` is a
`Circle`"*. The parameter name on the left must be one of the function's own
parameters.

**The payoff is `filter`.** This is the moment custom guards stop being a
curiosity:

```ts
const values = ["gold", "wood", "silver"];
const coins: Coin[] = values.filter(isCoin);   // string[] → Coin[]
```

Without the predicate, `filter` hands back `string[]` and you are stuck casting.
With it, the narrowed element type flows out of the filter for free — every
later line knows it is holding coins.

**You are responsible for the truth of it.** A predicate is an *assertion*, in
the same family as `as`: the compiler believes the signature and never checks the
body. A guard whose body is wrong is worse than no guard, because now everything
downstream is confidently wrong.

```ts
function isCoin(v: string): v is Coin {
  return v.length > 0;      // ← compiles. Also completely untrue.
}
```

Keep the body a direct, obvious restatement of the type — one comparison per
member, nothing clever.

**Assertion functions** are the other half. Instead of returning a boolean they
narrow the caller's variable from that line on, and stop the program if the check
fails:

```ts
function assertNumber(v: unknown): asserts v is number {
  if (typeof v !== "number") throw new Error("not a number");
}

assertNumber(raw);
console.log(raw + 1);   // raw is a number from here down
```

(`throw` gets a proper treatment in Month 4 — for now read it as *"stop, this
should never have happened"*.) Use `asserts` for conditions that are genuinely
impossible if the program is correct, and a plain predicate for conditions you
expect to encounter and handle.

> ⚠️ **Common mistakes:** annotating the helper `: boolean` and wondering why
> narrowing is lost; naming a different variable on the left of `is`; writing a
> body that doesn't really establish the type; and reaching for `as` after the
> guard, which is a sign the predicate should have been written properly.
""",
            warmup=[
                _q("`function isCircle(s: Shape): boolean` used in an `if` narrows `s` to…",
                   ["Circle", "nothing — it stays Shape", "unknown", "never"], 1,
                   "A plain boolean carries no information about which member matched."),
                _q("The correct return annotation for a custom guard is…",
                   ["boolean", "s is Circle", "Circle", "asserts Circle"], 1,
                   "The predicate names a parameter and the type it establishes."),
                _q("`values.filter(isCoin)` where `isCoin` is a predicate returns…",
                   ["string[]", "Coin[]", "boolean[]", "unknown[]"], 1,
                   "The narrowed element type flows out of filter."),
                _q("If a predicate's body is wrong, TypeScript…",
                   ["reports an error", "believes it anyway", "falls back to boolean", "throws at runtime"], 1,
                   "It is an assertion — the signature is taken on trust."),
            ],
            exercises=[
                _ex("tscourse-w9-pred-1", "Write the predicate",
                    "Give `isCoin` a return annotation that narrows a string to a Coin.",
                    'type Coin = "gold" | "silver";\n'
                    'function isCoin(v: string): v is Coin {\n'
                    '  return v === "gold" || v === "silver";\n}\n'
                    'const values = ["gold", "wood", "silver"];\n'
                    'const coins: Coin[] = values.filter(isCoin);\n'
                    'console.log(coins.join(","));\n',
                    'v is Coin', [("", "gold,silver")],
                    hints=["Name the parameter, then `is`, then the type it establishes.",
                           "Write v is Coin."]),
                _ex("tscourse-w9-pred-2", "Narrow in an if",
                    "Fill in the body of the guard so each shape takes the right branch.",
                    'interface Circle {\n  kind: "circle";\n  r: number;\n}\n'
                    'interface Square {\n  kind: "square";\n  side: number;\n}\n'
                    'type Shape = Circle | Square;\n'
                    'function isCircle(s: Shape): s is Circle {\n'
                    '  return s.kind === "circle";\n}\n'
                    'const shapes: Shape[] = [{ kind: "circle", r: 2 }, { kind: "square", side: 3 }];\n'
                    'for (const s of shapes) {\n'
                    '  if (isCircle(s)) console.log(`circle area ${(Math.PI * s.r * s.r).toFixed(2)}`);\n'
                    '  else console.log(`square area ${s.side * s.side}`);\n'
                    '}\n',
                    'return s.kind === "circle";',
                    [("", "circle area 12.57\nsquare area 9")],
                    hints=["The body is the same discriminant check you would write inline.",
                           'Write return s.kind === "circle";'],
                    difficulty="Easy"),
                _ex("tscourse-w9-pred-3", "Guard, then trust",
                    "`label` should reject anything that isn't a Status before using it. Add the rejecting guard.",
                    'type Status = "todo" | "doing" | "done";\n'
                    'function isStatus(v: string): v is Status {\n'
                    '  return v === "todo" || v === "doing" || v === "done";\n}\n'
                    'function label(v: string): string {\n'
                    '  if (!isStatus(v)) return `unknown(${v})`;\n'
                    '  return v.toUpperCase();\n}\n'
                    'console.log(label("done"));\n'
                    'console.log(label("wat"));\n',
                    'if (!isStatus(v)) return `unknown(${v})`;',
                    [("", "DONE\nunknown(wat)")],
                    hints=["A guard clause: reject the bad case first, then the happy path runs narrowed.",
                           "Negate the predicate and return early."],
                    difficulty="Easy"),
                _ex("tscourse-w9-pred-4", "Filter into a narrower array",
                    "Keep only the published posts, then total their views. Fill in the filtering step.",
                    'interface Draft {\n  kind: "draft";\n  title: string;\n}\n'
                    'interface Published {\n  kind: "published";\n  title: string;\n  views: number;\n}\n'
                    'type Post = Draft | Published;\n'
                    'function isPublished(p: Post): p is Published {\n'
                    '  return p.kind === "published";\n}\n'
                    'const posts: Post[] = [\n'
                    '  { kind: "draft", title: "a" },\n'
                    '  { kind: "published", title: "b", views: 10 },\n'
                    '  { kind: "published", title: "c", views: 5 },\n'
                    '];\n'
                    'const live = posts.filter(isPublished);\n'
                    'const total = live.reduce((sum, p) => sum + p.views, 0);\n'
                    'console.log(`${live.length} live, ${total} views`);\n',
                    'posts.filter(isPublished)',
                    [("", "2 live, 15 views")],
                    hints=["Pass the predicate itself to filter — no arrow function needed.",
                           "Because it is a predicate, `live` comes out as Published[], so `.views` is available."],
                    difficulty="Medium"),
                _ex("tscourse-w9-pred-5", "An assertion function",
                    "Fill in the annotation that makes this narrow its argument from the call site onwards.",
                    'function assertNumber(v: unknown): asserts v is number {\n'
                    '  if (typeof v !== "number") throw new Error("not a number");\n}\n'
                    'const raw: unknown = 42;\n'
                    'assertNumber(raw);\n'
                    'console.log(raw + 1);\n',
                    'asserts v is number', [("", "43")],
                    hints=["An assertion function's return annotation starts with the word asserts.",
                           "Write asserts v is number."],
                    difficulty="Medium"),
                _fix("tscourse-w9-pred-fix1", "Fix the lying predicate",
                     "This should keep only `gold,silver`, but the guard's body doesn't actually establish the type — it accepts anything non-empty.",
                     'type Coin = "gold" | "silver";\n'
                     'function isCoin(v: string): v is Coin {\n'
                     '  return v.length > 0;\n}\n'
                     'const values = ["gold", "wood", "silver"];\n'
                     'console.log(values.filter(isCoin).join(","));\n',
                     'type Coin = "gold" | "silver";\n'
                     'function isCoin(v: string): v is Coin {\n'
                     '  return v === "gold" || v === "silver";\n}\n'
                     'const values = ["gold", "wood", "silver"];\n'
                     'console.log(values.filter(isCoin).join(","));\n',
                     [("", "gold,silver")],
                     hints=["The compiler believed the signature and never looked at the body.",
                            "Test the value against each member of the union."],
                     difficulty="Medium"),
                _fix("tscourse-w9-pred-fix2", "Fix the impossible condition",
                     "Every label comes back as unknown. The guard asks for a value that is two things at once.",
                     'type Status = "todo" | "done";\n'
                     'function isStatus(v: string): v is Status {\n'
                     '  return v === "todo" && v === "done";\n}\n'
                     'function label(v: string): string {\n'
                     '  if (!isStatus(v)) return `unknown(${v})`;\n'
                     '  return v.toUpperCase();\n}\n'
                     'console.log(label("done"));\n'
                     'console.log(label("todo"));\n'
                     'console.log(label("wat"));\n',
                     'type Status = "todo" | "done";\n'
                     'function isStatus(v: string): v is Status {\n'
                     '  return v === "todo" || v === "done";\n}\n'
                     'function label(v: string): string {\n'
                     '  if (!isStatus(v)) return `unknown(${v})`;\n'
                     '  return v.toUpperCase();\n}\n'
                     'console.log(label("done"));\n'
                     'console.log(label("todo"));\n'
                     'console.log(label("wat"));\n',
                     [("", "DONE\nTODO\nunknown(wat)")],
                     hints=["No single string can equal both members.",
                            "Membership of a union is an OR, not an AND."]),
                _fix("tscourse-w9-pred-fix3", "Fix the wrong field",
                     "This should report `2 live` but reports 0 — the guard is comparing the wrong property against the tag.",
                     'interface Draft {\n  kind: "draft";\n  title: string;\n}\n'
                     'interface Published {\n  kind: "published";\n  title: string;\n  views: number;\n}\n'
                     'type Post = Draft | Published;\n'
                     'function isPublished(p: Post): p is Published {\n'
                     '  return p.title === "published";\n}\n'
                     'const posts: Post[] = [\n'
                     '  { kind: "draft", title: "a" },\n'
                     '  { kind: "published", title: "b", views: 10 },\n'
                     '  { kind: "published", title: "c", views: 5 },\n'
                     '];\n'
                     'console.log(`${posts.filter(isPublished).length} live`);\n',
                     'interface Draft {\n  kind: "draft";\n  title: string;\n}\n'
                     'interface Published {\n  kind: "published";\n  title: string;\n  views: number;\n}\n'
                     'type Post = Draft | Published;\n'
                     'function isPublished(p: Post): p is Published {\n'
                     '  return p.kind === "published";\n}\n'
                     'const posts: Post[] = [\n'
                     '  { kind: "draft", title: "a" },\n'
                     '  { kind: "published", title: "b", views: 10 },\n'
                     '  { kind: "published", title: "c", views: 5 },\n'
                     '];\n'
                     'console.log(`${posts.filter(isPublished).length} live`);\n',
                     [("", "2 live")],
                     hints=["The discriminant is the `kind` field, not the title.",
                            "Both fields are strings, so the compiler had no way to object."],
                     difficulty="Medium"),
                _ch("tscourse-w9-pred-ch1", "Split a stream with guards", "Hard",
                    "Events arrive as `add,<number>` or `note,<text>`. Write the two predicates `isAdd` and `isNote`, then use them to build the total of every add and the list of every note.",
                    _FS +
                    'interface Add {\n  kind: "add";\n  amount: number;\n}\n'
                    'interface Note {\n  kind: "note";\n  text: string;\n}\n'
                    'type Event = Add | Note;\n'
                    'function toEvent(line: string): Event {\n'
                    '  const parts = line.split(",");\n'
                    '  if (parts[0].trim() === "add") return { kind: "add", amount: Number(parts[1]) };\n'
                    '  return { kind: "note", text: parts[1].trim() };\n}\n'
                    'function isAdd(e: Event): e is Add {\n'
                    '  return e.kind === "add";\n}\n'
                    'function isNote(e: Event): e is Note {\n'
                    '  return e.kind === "note";\n}\n'
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n")\n'
                    '  .filter((l) => l.trim().length > 0);\n'
                    'const events: Event[] = lines.map(toEvent);\n'
                    'const total = events.filter(isAdd).reduce((sum, e) => sum + e.amount, 0);\n'
                    'const notes = events.filter(isNote).map((e) => e.text);\n'
                    'console.log(`Total: ${total}`);\n'
                    'console.log(`Notes: ${notes.join(" | ")}`);\n',
                    'function isAdd(e: Event): e is Add {\n'
                    '  return e.kind === "add";\n}\n'
                    'function isNote(e: Event): e is Note {\n'
                    '  return e.kind === "note";\n}\n'
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n")\n'
                    '  .filter((l) => l.trim().length > 0);\n'
                    'const events: Event[] = lines.map(toEvent);\n'
                    'const total = events.filter(isAdd).reduce((sum, e) => sum + e.amount, 0);\n'
                    'const notes = events.filter(isNote).map((e) => e.text);',
                    [("add,10\nnote,hello\nadd,5\nnote,bye", "Total: 15\nNotes: hello | bye"),
                     ("note,x\nnote,y", "Total: 0\nNotes: x | y"),
                     ("add,7", "Total: 7\nNotes:")],
                    hints=["Each predicate is one line: compare the `kind` tag to its literal.",
                           "Filtering with a predicate gives you an Add[] and a Note[], so .amount and .text are both safe.",
                           "reduce over the adds with a starting accumulator of 0.",
                           "map the notes to their text before joining them."]),
            ],
            quiz=[
                _q("`function isCoin(v: string): v is Coin` differs from `: boolean` because…",
                   ["it is faster", "it tells the compiler what a true result means",
                    "it validates at runtime", "it cannot be used in filter"], 1,
                   "That is the entire content of a type predicate."),
                _q("The name on the left of `is` must be…",
                   ["any identifier", "one of the function's own parameters", "the return value", "a type"], 1,
                   "The predicate narrows that specific parameter."),
                _q("Passing a predicate to `filter` gives you…",
                   ["a boolean array", "an array of the narrowed type",
                    "the original array", "an error"], 1,
                   "Which is why predicates are worth writing at all."),
                _q("An `asserts v is number` function…",
                   ["returns a boolean", "narrows v from the call site on, and stops the program otherwise",
                    "converts v to a number", "is checked by the compiler"], 1,
                   "Use it for conditions that should be impossible."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #9 — the event log",
        """
Budget Buddy stops storing rows and starts storing **events**. Each line of
input is one event, and events come in three kinds:

```
add coffee 3.25
remove coffee
note reviewed the month
```

Model them as a **discriminated union**:

```ts
type Event =
  | { kind: "add"; desc: string; amount: number }
  | { kind: "remove"; desc: string }
  | { kind: "note"; text: string };
```

Process the log in order and print:

```
Events:  3
Added:   1 ($3.25)
Removed: 1 (coffee)
Notes:   1
Balance: $0.00
```

Rules:

- `Balance` is the total of every `add` minus the amount of every `remove` whose
  description was previously added. (Removing something never added changes
  nothing.)
- `Removed` lists the descriptions of removals, in order, joined with `, `.
- A `note` event's text is everything after the word `note`.
- Handle every kind with a `switch` on the tag — no optional fields.
""",
        _ch("tscourse-w9-capstone", "Budget Buddy #9", "Medium",
            "Parse each line into a tagged event, then fold the log.",
            _FS + 'type Event =\n'
            '  | { kind: "add"; desc: string; amount: number }\n'
            '  | { kind: "remove"; desc: string }\n'
            '  | { kind: "note"; text: string };\n'
            'function parse(line: string): Event {\n'
            '  const p = line.trim().split(" ");\n'
            '  if (p[0] === "add") return { kind: "add", desc: p[1], amount: Number(p[2]) };\n'
            '  if (p[0] === "remove") return { kind: "remove", desc: p[1] };\n'
            '  return { kind: "note", text: p.slice(1).join(" ") };\n'
            '}\n'
            'const events: Event[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const prices: { [key: string]: number } = {};\n'
            'let added = 0;\nlet notes = 0;\nlet balance = 0;\n'
            'const removed: string[] = [];\n'
            'for (const e of events) {\n'
            '  switch (e.kind) {\n'
            '    case "add":\n'
            '      added++;\n      balance += e.amount;\n      prices[e.desc] = e.amount;\n      break;\n'
            '    case "remove":\n'
            '      removed.push(e.desc);\n      balance -= prices[e.desc] ?? 0;\n      break;\n'
            '    case "note":\n'
            '      notes++;\n      break;\n'
            '  }\n'
            '}\n'
            'let addedTotal = 0;\n'
            'for (const e of events) {\n  if (e.kind === "add") addedTotal += e.amount;\n}\n'
            'console.log(`Events:  ${events.length}`);\n'
            'console.log(`Added:   ${added} ($${addedTotal.toFixed(2)})`);\n'
            'console.log(`Removed: ${removed.length} (${removed.join(", ")})`);\n'
            'console.log(`Notes:   ${notes}`);\n'
            'console.log(`Balance: $${balance.toFixed(2)}`);\n',
            'function parse(line: string): Event {\n'
            '  const p = line.trim().split(" ");\n'
            '  if (p[0] === "add") return { kind: "add", desc: p[1], amount: Number(p[2]) };\n'
            '  if (p[0] === "remove") return { kind: "remove", desc: p[1] };\n'
            '  return { kind: "note", text: p.slice(1).join(" ") };\n'
            '}\n'
            'const events: Event[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const prices: { [key: string]: number } = {};\n'
            'let added = 0;\nlet notes = 0;\nlet balance = 0;\n'
            'const removed: string[] = [];\n'
            'for (const e of events) {\n'
            '  switch (e.kind) {\n'
            '    case "add":\n'
            '      added++;\n      balance += e.amount;\n      prices[e.desc] = e.amount;\n      break;\n'
            '    case "remove":\n'
            '      removed.push(e.desc);\n      balance -= prices[e.desc] ?? 0;\n      break;\n'
            '    case "note":\n'
            '      notes++;\n      break;\n'
            '  }\n'
            '}\n'
            'let addedTotal = 0;\n'
            'for (const e of events) {\n  if (e.kind === "add") addedTotal += e.amount;\n}\n'
            'console.log(`Events:  ${events.length}`);\n'
            'console.log(`Added:   ${added} ($${addedTotal.toFixed(2)})`);\n'
            'console.log(`Removed: ${removed.length} (${removed.join(", ")})`);\n'
            'console.log(`Notes:   ${notes}`);\n'
            'console.log(`Balance: $${balance.toFixed(2)}`);',
            [("add coffee 3.25\nremove coffee\nnote reviewed the month",
              "Events:  3\nAdded:   1 ($3.25)\nRemoved: 1 (coffee)\nNotes:   1\nBalance: $0.00"),
             ("add book 12\nadd tea 2",
              "Events:  2\nAdded:   2 ($14.00)\nRemoved: 0 ()\nNotes:   0\nBalance: $14.00"),
             ("remove ghost\nnote nothing here",
              "Events:  2\nAdded:   0 ($0.00)\nRemoved: 1 (ghost)\nNotes:   1\nBalance: $0.00")],
            hints=["parse decides the tag from the first word, and builds a DIFFERENT shape for each kind.",
                   'A note\'s text is the rest of the line: p.slice(1).join(" ").',
                   "Remember what each amount was: a lookup table from desc to amount, filled on every add.",
                   "Removing something never added must not change the balance — `prices[e.desc] ?? 0` handles that.",
                   "Switch on e.kind so each arm can read only its own member's fields."]),
        example_io="Events:  3\nAdded:   1 ($3.25)\nRemoved: 1 (coffee)\nNotes:   1\nBalance: $0.00",
        rubric=["Event is a discriminated union with a literal `kind` on every member",
                "parse builds a different shape per kind — no optional fields",
                "A switch on the tag handles all three kinds",
                "Removing a description that was never added leaves the balance unchanged"],
        stretch=_ch("tscourse-w9-capstone-stretch", "Budget Buddy #9 (stretch)", "Medium",
                    "Add an exhaustiveness guard: a `default` branch whose `const _exhaustive: never = e;` would stop the build if a fourth event kind were added and left unhandled. Also print the last note's text as `Last note: <text>` (or `Last note: -` when there are none).",
                    _FS + 'type Event =\n'
                    '  | { kind: "add"; desc: string; amount: number }\n'
                    '  | { kind: "remove"; desc: string }\n'
                    '  | { kind: "note"; text: string };\n'
                    'function parse(line: string): Event {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  if (p[0] === "add") return { kind: "add", desc: p[1], amount: Number(p[2]) };\n'
                    '  if (p[0] === "remove") return { kind: "remove", desc: p[1] };\n'
                    '  return { kind: "note", text: p.slice(1).join(" ") };\n'
                    '}\n'
                    'const events: Event[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'let lastNote = "-";\n'
                    'for (const e of events) {\n'
                    '  switch (e.kind) {\n'
                    '    case "add":\n      break;\n'
                    '    case "remove":\n      break;\n'
                    '    case "note":\n      lastNote = e.text;\n      break;\n'
                    '    default: {\n'
                    '      const _exhaustive: never = e;\n      throw new Error(_exhaustive);\n'
                    '    }\n'
                    '  }\n'
                    '}\n'
                    'console.log(`Last note: ${lastNote}`);\n',
                    'default: {\n'
                    '      const _exhaustive: never = e;\n      throw new Error(_exhaustive);\n'
                    '    }',
                    [("add coffee 3.25\nnote reviewed the month", "Last note: reviewed the month"),
                     ("add book 12", "Last note: -"),
                     ("note first\nnote second", "Last note: second")],
                    hints=["The default branch receives whatever the cases did not cover.",
                           "Assign it to a name annotated never — that is the whole check.",
                           "Write default: { const _exhaustive: never = e; throw new Error(_exhaustive); }"]),
    ),
))

# --- Week 10 --------------------------------------------------------------
_WEEKS.append(_week(
    10, 3, _M3,
    "Generics",
    "Write one function or type that works over any type — without losing what the compiler knows about it.",
    """
Here is the problem generics exist to solve. You write a helper that returns the
first element of an array:

```ts
function firstNumber(a: number[]): number { return a[0]; }
```

Then you need it for strings. And for records. You have three choices:

1. **Copy it** for every element type — three functions that differ by one word.
2. **Use `any`** — one function, and every caller loses all type information.
3. **Make the type a parameter.**

The third is a **generic**:

```ts
function first<T>(a: T[]): T {
  return a[0];
}

first([1, 2, 3]);        // T is number   -> returns number
first(["a", "b"]);       // T is string   -> returns string
```

`<T>` declares a **type parameter** — a placeholder filled in at each call site,
usually inferred so you never write it. One implementation, and the compiler
still knows that `first(["a"])` gives you a `string` with `.toUpperCase()` on it.

The mental model that makes generics click: **`T` is a variable whose value is a
type.** Everything else — constraints, `keyof`, generic interfaces — is that one
idea applied more sharply.

The runtime code in this week's drills is deliberately simple; the difficulty
lives in the signatures. Read them slowly, and lean on the quizzes.

⏱️ Budget about **ten hours**, spread over several sittings.
""",
    objectives=[
        "Say what problem generics solve, and why `any` is not the answer",
        "Write a generic function and let TypeScript infer its type argument",
        "Write generic helpers over arrays that preserve the element type",
        "Constrain a type parameter with extends so you can use its members",
        "Use keyof and indexed access to type a field-plucking helper",
        "Declare generic type aliases and interfaces, including a Result type",
        "Give a type parameter a default, and recognise when a generic is overkill",
        "Write a generic helper that takes a callback and changes the type on the way through",
        "Decide when a second type parameter earns its place — and when it does not",
    ],
    why="Every array method, every Promise, every collection and every well-typed utility in the ecosystem is generic. Reading them fluently — and writing your own when a helper would otherwise need `any` — is the difference between using TypeScript and fighting it.",
    est_minutes=580,
    glossary=[
        _gloss("generic", "A function, type or interface parameterised by a type."),
        _gloss("type parameter", "The placeholder declared in angle brackets: <T>."),
        _gloss("type argument", "The concrete type supplied at a call site: first<string>(...)."),
        _gloss("inference (of type arguments)", "TypeScript working out T from the values you passed."),
        _gloss("T", "The conventional name for a type parameter. K, V, E, R are also common."),
        _gloss("constraint", "extends limits what a type parameter may be: <T extends { id: string }>."),
        _gloss("keyof T", "The union of T's key names as literal types."),
        _gloss("indexed access (T[K])", "The type of the property K on T."),
        _gloss("generic interface", "An interface with its own type parameters: interface Box<T>."),
        _gloss("default type parameter", "A fallback type argument: <T = string>."),
        _gloss("Array<T>", "The generic type behind T[]."),
        _gloss("Promise<T>", "A value of type T that arrives later (week 16)."),
        _gloss("Record<K, V>", "A built-in generic object type (week 12)."),
        _gloss("any", "Turns checking off. A generic keeps the information instead."),
        _gloss("unknown", "Accepts anything but must be narrowed. Safe, but loses the caller's type."),
        _gloss("higher-order generic", "A generic function that takes a function, letting the callback decide the output type."),
        _gloss("U", "By convention the second type parameter — usually what a callback returns."),
        _gloss("pinned parameter", "A callback return type fixed to string or number because the helper indexes or compares with it."),
        _gloss("Array<T>", "The same type as T[], written in the generic form."),
    ],
    cheatsheet="""
```ts
// ---- the basic shape --------------------------------------------------
function first<T>(a: T[]): T { return a[0]; }
first([1, 2]);            // T inferred as number
first<string>(["a"]);     // T given explicitly (rarely needed)

function identity<T>(x: T): T { return x; }

// ---- several parameters -------------------------------------------------
function pair<A, B>(a: A, b: B): [A, B] { return [a, b]; }
function swap<A, B>(p: [A, B]): [B, A] { return [p[1], p[0]]; }

// ---- constraints ---------------------------------------------------------
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;      // .length is now allowed
}
longest("abc", "de");        // ✅ strings have length
longest([1], [2, 3]);        // ✅ arrays do too
longest(1, 2);               // ❌ numbers do not

// ---- keyof & indexed access ------------------------------------------------
type User = { id: string; age: number };
type K = keyof User;              // "id" | "age"
type A = User["age"];             // number

function pluck<T, K extends keyof T>(o: T, k: K): T[K] {
  return o[k];
}
pluck({ id: "u1", age: 3 }, "age");   // returns number, not any

// ---- generic types ----------------------------------------------------------
interface Box<T> { value: T }
type Pair<A, B> = { left: A; right: B };
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

// ---- defaults ----------------------------------------------------------------
interface Options<T = string> { items: T[] }
const o: Options = { items: ["a"] };      // T defaults to string
```
""",
    self_check=[
        "Can you explain why `any` is a bad substitute for a generic?",
        "Can you write a function that returns the last element of an array of any type?",
        "Can you say what TypeScript infers T to be in `first([1, 2])`?",
        "Can you constrain a type parameter so you may read `.length` off it?",
        "Can you say what `keyof User` is, for a User with id and age?",
        "Can you declare a generic interface and use it at two different types?",
        "Can you name a case where a generic would be pointless?",
        "Can you write mapAll, groupBy and maxBy from scratch, with the right type parameters?",
        "Can you say where each type parameter is inferred from at a call site?",
    ],
    review=[
        _q("`<T>` in a function signature declares…",
           ["a value parameter", "a type parameter", "an array", "a constraint"], 1,
           "A placeholder for a type, filled at the call site."),
        _q("In `first([1, 2, 3])` where `first<T>(a: T[]): T`, T is…",
           ["any", "number", "number[]", "unknown"], 1,
           "Inferred from the argument's element type."),
        _q("Why not just use `any` instead of a generic?",
           ["any is slower", "any discards the caller's type, so the RESULT is unchecked too",
            "any is deprecated", "no difference"], 1,
           "The generic remembers what came in and hands the same type back."),
        _q("`function f<T extends { length: number }>(x: T)` lets you…",
           ["pass anything", "read x.length inside f", "return a number", "skip inference"], 1,
           "A constraint is what makes a member usable."),
        _q("`keyof { id: string; age: number }` is…",
           ["string", '"id" | "age"', "[string, number]", "never"], 1,
           "A union of the key names as literal types."),
        _q("`User[\"age\"]` where age is a number is…",
           ['"age"', "number", "string", "never"], 1,
           "Indexed access gives the property's TYPE."),
        _q("`interface Box<T> { value: T }` used as `Box<string>` has value of type…",
           ["T", "string", "any", "unknown"], 1,
           "The argument replaces the parameter."),
        _q("`<T = string>` means…",
           ["T must be string", "T defaults to string when not supplied", "T is a value",
            "T is constrained"], 1,
           "A default type argument."),
        _q("A generic with a type parameter used exactly ONCE in the signature is usually…",
           ["ideal", "a sign it should just be a plain parameter type", "faster",
            "required"], 1,
           "A parameter that relates nothing to nothing buys you nothing."),
        _q("`function f<T>(x: T): T` called as `f(\"a\")` returns a value of type…",
           ["string", '"a"', "any", "unknown"], 0,
           "Inference widens the literal to string here."),
        _q("In `mapAll<T, U>(xs: T[], f: (x: T) => U): U[]`, `U` is inferred from…",
           ["the array", "what the callback returns", "the call site only", "the return statement"], 1,
           "The callback decides the output element type."),
        _q("`groupBy<T>(xs: T[], key: (x: T) => string)` pins the callback's return to string because…",
           ["strings are faster", "the helper uses it as an object key", "T must be a string", "generics demand it"], 1,
           "Object keys are strings, so that position cannot stay open."),
        _q("A type parameter that appears in exactly one position…",
           ["is required", "relates nothing, and can usually be a concrete type",
            "must be constrained", "is inferred last"], 1,
           "A type parameter earns its keep by tying two positions together."),
    ],
    milestone="Budget Buddy's helpers now work over any record type at all, and its parser hands back a typed Result — the same shapes real libraries expose. Month 3 is half done.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w10-why", "Why generics exist",
            "The gap between duplication and any.",
            """
Three ways to write "give me the first element".

**Duplicate per type** — correct, and unmaintainable:

```ts
function firstNumber(a: number[]): number { return a[0]; }
function firstString(a: string[]): string { return a[0]; }
function firstUser(a: User[]): User { return a[0]; }
```

**Use `any`** — one function, and the type information is destroyed:

```ts
function first(a: any[]): any { return a[0]; }

const s = first(["a", "b"]);
s.toUpperCase();     // no error... and no checking either
s.toFixed(2);        // also no error — and a crash at runtime
```

`any` doesn't just lose information at the boundary; it *poisons everything
downstream*. The caller got a value the compiler will never question again.

**Make the type a parameter:**

```ts
function first<T>(a: T[]): T {
  return a[0];
}

const s = first(["a", "b"]);   // s: string
s.toUpperCase();               // ✅
s.toFixed(2);                  // ❌ caught
```

One implementation, full checking at every call site.

**What `<T>` means.** Read `function first<T>(a: T[]): T` as: *"for any type T,
this takes an array of T and returns a T."* The signature states a
**relationship** — the output type is tied to the input type — and that
relationship is exactly what `any` throws away.

**`unknown` is safer than `any` but still wrong here:**

```ts
function first(a: unknown[]): unknown { return a[0]; }
const s = first(["a"]);
s.toUpperCase();      // ❌ must narrow first — but you already KNEW it was a string
```

`unknown` is honest, and it still makes the caller re-establish something the
function could have preserved. Use `unknown` for values whose type you genuinely
don't know (parsed JSON, caught errors). Use a generic when the type is *known
to the caller* and you're just passing it through.

**The test for whether you need a generic:** does a type appear in **more than
one place** in the signature — two parameters, or a parameter and the return? If
yes, a generic ties them together. If a type parameter appears only once, it is
doing nothing.

> ⚠️ **Common mistakes:** reaching for `any` when a generic was two characters
> away; adding type parameters that appear only once; and thinking `<T>` has a
> runtime cost — it is erased like every other type.
""",
            warmup=[
                _q("`function first(a: any[]): any` — what does the caller get?",
                   ["a checked value", "a value the compiler will never question again",
                    "an error", "unknown"], 1,
                   "any propagates outward."),
                _q("`function first<T>(a: T[]): T` called with `[\"a\"]` returns…",
                   ["any", "string", "unknown", "T"], 1, "T is inferred as string."),
                _q("The point of `<T>` in a signature is to…",
                   ["speed things up", "tie the output type to the input type",
                    "allow any value", "avoid annotations"], 1,
                   "It states a relationship."),
                _q("A type parameter that appears only ONCE in the signature is…",
                   ["ideal", "pointless — it relates nothing", "required", "faster"], 1,
                   "Generics exist to connect two places."),
            ],
            exercises=[
                _ex("tscourse-w10-wh-1", "The identity function",
                    "Return the argument unchanged.",
                    'function identity<T>(x: T): T {\n  return x;\n}\n'
                    'console.log(identity("hello"));\nconsole.log(identity(42));\n',
                    'return x;', [("", "hello\n42")],
                    hints=["The simplest generic there is — hand back what you were given."]),
                _ex("tscourse-w10-wh-2", "First element, generically",
                    "Return the first element of the array.",
                    'function first<T>(a: T[]): T {\n  return a[0];\n}\n'
                    'console.log(first([1, 2, 3]));\nconsole.log(first(["a", "b"]));\n',
                    'return a[0];', [("", "1\na")],
                    hints=["Index 0, whatever the element type is."]),
                _ex("tscourse-w10-wh-3", "Declare the parameter",
                    "Add the type parameter so this works for any element type.",
                    'function last<T>(a: T[]): T {\n  return a[a.length - 1];\n}\n'
                    'console.log(last([1, 2, 3]));\nconsole.log(last(["a", "b"]));\n',
                    '<T>', [("", "3\nb")],
                    hints=["Angle brackets go right after the function name.",
                           "Write <T>."]),
                _ex("tscourse-w10-wh-4", "Use the preserved type",
                    "The result is a string, so its own methods are available. Uppercase it.",
                    'function first<T>(a: T[]): T {\n  return a[0];\n}\n'
                    'const s = first(["hello", "there"]);\nconsole.log(s.toUpperCase());\n',
                    's.toUpperCase()', [("", "HELLO")],
                    hints=["Because T was inferred as string, string methods are allowed.",
                           "Write s.toUpperCase()."]),
                _ex("tscourse-w10-wh-5", "Generic over records",
                    "The same helper works on an array of objects. Print the first record's desc.",
                    'function first<T>(a: T[]): T {\n  return a[0];\n}\n'
                    'const rows = [{ desc: "coffee" }, { desc: "book" }];\n'
                    'console.log(first(rows).desc);\n',
                    'first(rows).desc', [("", "coffee")],
                    hints=["T is inferred as the record type, so .desc is available.",
                           "Write first(rows).desc."],
                    difficulty="Medium"),
                _fix("tscourse-w10-wh-fix1", "Fix the any-shaped helper",
                     "This uses `any`, so a genuine mistake goes unnoticed and it crashes at runtime. Make it generic and call the right method.",
                     'function first(a: any[]): any {\n  return a[0];\n}\n'
                     'const s = first(["hello"]);\nconsole.log(s.toFixed(2));\n',
                     'function first<T>(a: T[]): T {\n  return a[0];\n}\n'
                     'const s = first(["hello"]);\nconsole.log(s.toUpperCase());\n',
                     [("", "HELLO")],
                     hints=["With any, calling toFixed on a string raised no complaint at all.",
                            "Parameterise the type, then call a method the value actually has."],
                     difficulty="Medium"),
                _fix("tscourse-w10-why-fix2", "Fix the off-by-one helper",
                     "The generic signature is right, but `first` hands back the second element. It should print 10 then a.",
                     'function first<T>(xs: T[]): T {\n'
                     '  return xs[1];\n}\n'
                     'console.log(first([10, 20, 30]));\n'
                     'console.log(first(["a", "b"]));\n',
                     'function first<T>(xs: T[]): T {\n'
                     '  return xs[0];\n}\n'
                     'console.log(first([10, 20, 30]));\n'
                     'console.log(first(["a", "b"]));\n',
                     [("", "10\na")],
                     hints=["Generics make the types line up; they cannot make the logic correct.",
                            "Array positions start at 0."]),
            ],
            quiz=[
                _q("`unknown[]` instead of a generic means the caller must…",
                   ["nothing extra", "narrow a type it already knew", "cast to any",
                    "use a loop"], 1,
                   "Safe, but it discards information the function could have preserved."),
                _q("Generics at runtime…",
                   ["add a lookup", "are erased like all types", "create classes",
                    "slow calls down"], 1,
                   "There is no runtime representation of T at all."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w10-functions", "Generic functions & inference",
            "Declaring type parameters, and letting them be worked out.",
            """
The type parameter list goes between the name and the value parameters:

```ts
function wrap<T>(x: T): T[] {
  return [x];
}
```

**You almost never write the type argument.** TypeScript infers it from what you
pass:

```ts
wrap("a");        // T = string   -> string[]
wrap(3);          // T = number   -> number[]
wrap<boolean>(true);   // explicit — legal, but usually noise
```

Supply it explicitly only when inference can't help — typically when the type
appears nowhere in the arguments:

```ts
function makeEmpty<T>(): T[] { return []; }
const xs = makeEmpty<string>();     // nothing to infer from, so say it
```

**Several type parameters** are independent:

```ts
function pair<A, B>(a: A, b: B): [A, B] {
  return [a, b];
}
pair("x", 1);      // [string, number]
```

Conventional names: `T` for a single one; `A`/`B` or `T`/`U` for two; `K` for a
key, `V` for a value, `E` for an error, `R` for a result. Use a descriptive name
when it helps (`<TRow>`), but short names are the norm and nobody minds.

**Inference follows the values, and widens literals:**

```ts
function id<T>(x: T): T { return x; }
const a = id("hello");        // string, not "hello"
const b = id({ n: 1 });       // { n: number }
```

**Generic arrow functions** exist too, and are used constantly for callbacks:

```ts
const wrap = <T>(x: T): T[] => [x];
```

(In `.tsx` files that clashes with JSX and needs `<T,>`; in a plain `.ts` file
it's fine.)

**A generic can call another generic**, passing its own parameter through:

```ts
function firstOrEmpty<T>(a: T[]): T[] {
  return a.length > 0 ? wrap(first(a)) : [];
}
```

That's the payoff: the relationships compose, and the compiler tracks them all
the way down.

> ⚠️ **Common mistakes:** writing explicit type arguments everywhere (let
> inference work); declaring `<T>` and then never using it; and expecting `T` to
> be available at runtime — you cannot write `if (T === string)`.
""",
            warmup=[
                _q("`function wrap<T>(x: T): T[]` called as `wrap(3)` returns type…",
                   ["number", "number[]", "T[]", "any[]"], 1, "T is number, so T[] is number[]."),
                _q("When must you write the type argument explicitly?",
                   ["always", "when nothing in the arguments determines it", "never",
                    "for strings"], 1,
                   "e.g. a function taking no parameters."),
                _q("`const a = id(\"hello\")` where `id<T>(x: T): T` gives a…",
                   ['"hello"', "string", "any", "never"], 1, "Inference widens the literal."),
                _q("Can you test `T` at runtime?",
                   ["yes, with typeof T", "no — type parameters are erased", "yes, with instanceof",
                    "only for classes"], 1,
                   "There is nothing left of T when the program runs."),
            ],
            exercises=[
                _ex("tscourse-w10-fn-1", "Wrap a value",
                    "Return a one-element array holding the argument.",
                    'function wrap<T>(x: T): T[] {\n  return [x];\n}\n'
                    'console.log(wrap("a").length);\nconsole.log(wrap(3)[0]);\n',
                    'return [x];', [("", "1\n3")],
                    hints=["An array literal containing just the parameter."]),
                _ex("tscourse-w10-fn-2", "Two type parameters",
                    "Return the two arguments as a tuple.",
                    'function pair<A, B>(a: A, b: B): [A, B] {\n  return [a, b];\n}\n'
                    'const p = pair("x", 1);\nconsole.log(`${p[0]}${p[1]}`);\n',
                    'return [a, b];', [("", "x1")],
                    hints=["The tuple holds them in order."]),
                _ex("tscourse-w10-fn-3", "Declare two parameters",
                    "Add the type parameter list so both arguments keep their own types.",
                    'function swap<A, B>(a: A, b: B): [B, A] {\n  return [b, a];\n}\n'
                    'const s = swap("x", 1);\nconsole.log(`${s[0]}${s[1]}`);\n',
                    '<A, B>', [("", "1x")],
                    hints=["Two names, separated by a comma, in angle brackets.",
                           "Write <A, B>."],
                    difficulty="Medium"),
                _ex("tscourse-w10-fn-4", "Swap the tuple",
                    "Return the pair with its two slots exchanged.",
                    'function swap<A, B>(p: [A, B]): [B, A] {\n  return [p[1], p[0]];\n}\n'
                    'const s = swap(["x", 1]);\nconsole.log(`${s[0]}${s[1]}`);\n',
                    'return [p[1], p[0]];', [("", "1x")],
                    hints=["Slot 1 first, then slot 0."],
                    difficulty="Medium"),
                _ex("tscourse-w10-fn-5", "Compose two generics",
                    "Return a one-element array holding the first element, or an empty array.",
                    'function first<T>(a: T[]): T {\n  return a[0];\n}\n'
                    'function wrap<T>(x: T): T[] {\n  return [x];\n}\n'
                    'function firstOrEmpty<T>(a: T[]): T[] {\n'
                    '  return a.length > 0 ? wrap(first(a)) : [];\n}\n'
                    'console.log(firstOrEmpty([5, 6]).length);\nconsole.log(firstOrEmpty([]).length);\n',
                    'a.length > 0 ? wrap(first(a)) : []',
                    [("", "1\n0")],
                    hints=["Guard the empty case, then pass T straight through both helpers.",
                           "Write a.length > 0 ? wrap(first(a)) : []."],
                    difficulty="Medium"),
                _fix("tscourse-w10-fn-fix1", "Fix the unused parameter",
                     "The helper declares a type parameter it never uses, and hard-codes a string. Make it actually generic so the number is returned unchanged.",
                     'function identity<T>(x: string): string {\n  return x;\n}\n'
                     'console.log(identity("a"));\n',
                     'function identity<T>(x: T): T {\n  return x;\n}\n'
                     'console.log(identity("a"));\nconsole.log(identity(42));\n',
                     [("", "a\n42")],
                     hints=["<T> is declared but the signature still says string everywhere.",
                            "Use T for the parameter and the return, then it works for numbers too."],
                     difficulty="Medium"),
                _fix("tscourse-w10-fn-fix2", "Fix the swap that doesn't swap",
                     "`swap` promises `[B, A]` but hands the pair back untouched — and a double assertion hid it. It should print `1,a`.",
                     'function swap<A, B>(pair: [A, B]): [B, A] {\n'
                     '  return [pair[0], pair[1]] as unknown as [B, A];\n}\n'
                     'console.log(swap(["a", 1]).join(","));\n',
                     'function swap<A, B>(pair: [A, B]): [B, A] {\n'
                     '  return [pair[1], pair[0]];\n}\n'
                     'console.log(swap(["a", 1]).join(","));\n',
                     [("", "1,a")],
                     hints=["Without the assertion, the compiler would have rejected this immediately.",
                            "Return the second slot first: [pair[1], pair[0]]."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Explicit type arguments are…",
                   ["always required", "usually unnecessary — inference handles it",
                    "never allowed", "faster"], 1,
                   "Write them only when inference has nothing to go on."),
                _q("`<A, B>` declares…",
                   ["one parameter", "two independent type parameters", "a constraint",
                    "a tuple"], 1,
                   "Each is inferred separately."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w10-arrays", "Generic helpers over arrays",
            "Where generics earn their keep day to day.",
            """
Array helpers are the natural home of generics, because the element type must
survive the trip.

```ts
function last<T>(a: T[]): T            { return a[a.length - 1]; }
function head<T>(a: T[], n: number): T[] { return a.slice(0, n); }
function reversed<T>(a: T[]): T[]      { return [...a].reverse(); }
```

Each says something the compiler can use: `last` of a `string[]` is a `string`;
`reversed` of a `User[]` is a `User[]`.

**Returning "maybe nothing"** needs a union — and this is why the built-in
`find` returns `T | undefined`:

```ts
function firstOr<T>(a: T[], fallback: T): T {
  return a.length > 0 ? a[0] : fallback;
}
```

Note the `fallback: T`. That's the whole idea again: the fallback must be the
*same* type as the elements, and the signature enforces it.
`firstOr([1, 2], "none")` is a compile error, which is what you want.

**Combining two arrays:**

```ts
function concat<T>(a: T[], b: T[]): T[] {
  return [...a, ...b];
}
```

Both parameters use the *same* `T`, so mixing element types is rejected. If you
genuinely want to allow that, say so — `concat<A, B>(a: A[], b: B[]): (A | B)[]`.
The signature is the design decision.

**Deduplicating:**

```ts
function unique<T>(a: T[]): T[] {
  const out: T[] = [];
  for (const x of a) {
    if (!out.includes(x)) out.push(x);
  }
  return out;
}
```

`out: T[]` needs its annotation for the reason you learned in week 8 — an empty
literal has nothing to infer from.

**Reading the built-ins.** Everything you used in week 6 is generic. Hover over
`map` and you'll see roughly:

```ts
map<U>(fn: (value: T, index: number) => U): U[]
```

`T` is the array's element type; `U` is whatever the callback returns. That is
why `[1,2,3].map((x) => String(x))` is `string[]` and not `number[]` — the
signature *derives* the result type from your callback. Once generics read
easily, the standard library stops being magic.

> ⚠️ **Common mistakes:** forgetting the annotation on an accumulator array;
> using one `T` where you meant two independent ones (or the reverse); and
> writing a helper that returns `T` when it can return `undefined` for an empty
> array.
""",
            warmup=[
                _q("`function last<T>(a: T[]): T` on a `string[]` returns…",
                   ["T", "string", "any", "string[]"], 1, "T is inferred as string."),
                _q("`function concat<T>(a: T[], b: T[]): T[]` called with a number[] and a string[]…",
                   ["works, giving (number|string)[]", "is a compile error", "returns any[]",
                    "throws"], 1,
                   "Both parameters share one T, so they must agree."),
                _q("In `map<U>(fn: (v: T) => U): U[]`, U is…",
                   ["the element type", "whatever the callback returns", "always string",
                    "the index"], 1,
                   "Which is why map can change the array's type."),
                _q("`const out: T[] = [];` needs its annotation because…",
                   ["T is special", "an empty literal gives inference nothing", "it is const",
                    "it does not"], 1,
                   "Same rule as week 8."),
            ],
            exercises=[
                _ex("tscourse-w10-ar-1", "Last element",
                    "Return the final element, whatever the element type.",
                    'function last<T>(a: T[]): T {\n  return a[a.length - 1];\n}\n'
                    'console.log(last([1, 2, 3]));\nconsole.log(last(["a", "b"]));\n',
                    'return a[a.length - 1];', [("", "3\nb")],
                    hints=["The last index is one less than the length."]),
                _ex("tscourse-w10-ar-2", "Reverse a copy",
                    "Return a reversed copy, leaving the original alone.",
                    'function reversed<T>(a: T[]): T[] {\n  return [...a].reverse();\n}\n'
                    'const xs = [1, 2, 3];\nconsole.log(reversed(xs).join(""));\nconsole.log(xs.join(""));\n',
                    'return [...a].reverse();', [("", "321\n123")],
                    hints=["reverse mutates, so spread into a copy first.",
                           "Write return [...a].reverse();"],
                    difficulty="Medium"),
                _ex("tscourse-w10-ar-3", "A typed fallback",
                    "Return the first element, or the fallback when the array is empty.",
                    'function firstOr<T>(a: T[], fallback: T): T {\n'
                    '  return a.length > 0 ? a[0] : fallback;\n}\n'
                    'console.log(firstOr([5, 6], 0));\nconsole.log(firstOr<number>([], 0));\n',
                    'a.length > 0 ? a[0] : fallback', [("", "5\n0")],
                    hints=["Guard the empty case and hand back the fallback.",
                           "Write a.length > 0 ? a[0] : fallback."],
                    difficulty="Medium"),
                _ex("tscourse-w10-ar-4", "Concatenate",
                    "Return the two arrays joined into one.",
                    'function concat<T>(a: T[], b: T[]): T[] {\n  return [...a, ...b];\n}\n'
                    'console.log(concat([1, 2], [3]).join(""));\n',
                    'return [...a, ...b];', [("", "123")],
                    hints=["Spread both into a single new array."]),
                _ex("tscourse-w10-ar-5", "Deduplicate",
                    "Keep only the first occurrence of each element.",
                    _WORDS + 'function unique<T>(a: T[]): T[] {\n'
                    '  const out: T[] = [];\n'
                    '  for (const x of a) {\n    if (!out.includes(x)) {\n      out.push(x);\n    }\n  }\n'
                    '  return out;\n}\n'
                    'console.log(unique(words).join(" "));\n',
                    'if (!out.includes(x)) {\n      out.push(x);\n    }',
                    [("a b a c a", "a b c"), ("x y", "x y")],
                    hints=["Add an element only when it is not already collected.",
                           "Write if (!out.includes(x)) { out.push(x); }"],
                    difficulty="Medium"),
                _ex("tscourse-w10-ar-6", "Generic over records",
                    "The same unique helper works on records compared by reference. Print how many distinct objects remain.",
                    'function unique<T>(a: T[]): T[] {\n'
                    '  const out: T[] = [];\n'
                    '  for (const x of a) {\n    if (!out.includes(x)) {\n      out.push(x);\n    }\n  }\n'
                    '  return out;\n}\n'
                    'const r = { id: 1 };\nconsole.log(unique([r, r, { id: 1 }]).length);\n',
                    'unique([r, r, { id: 1 }]).length', [("", "2")],
                    hints=["includes compares objects by identity, so the two separate literals are different.",
                           "Write unique([r, r, { id: 1 }]).length."],
                    difficulty="Medium"),
                _fix("tscourse-w10-ar-fix1", "Fix the mutating reverse",
                     "The original array should stay `123` but comes back reversed. Fix it.",
                     'function reversed<T>(a: T[]): T[] {\n  return a.reverse();\n}\n'
                     'const xs = [1, 2, 3];\nconsole.log(reversed(xs).join(""));\nconsole.log(xs.join(""));\n',
                     'function reversed<T>(a: T[]): T[] {\n  return [...a].reverse();\n}\n'
                     'const xs = [1, 2, 3];\nconsole.log(reversed(xs).join(""));\nconsole.log(xs.join(""));\n',
                     [("", "321\n123")],
                     hints=["reverse reorders the caller's own array.",
                            "Copy it first with a spread."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Using the same `T` for two parameters means…",
                   ["they may differ", "they must be the same type", "one is inferred",
                    "nothing"], 1,
                   "Sharing a parameter is how you require agreement."),
                _q("Why does `[1,2].map((x) => String(x))` give `string[]`?",
                   ["map always returns strings", "map's signature derives the result type from the callback",
                    "a cast", "coincidence"], 1,
                   "The U in map<U> comes from your callback's return type."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w10-constraints", "Constraints with extends",
            "Requiring a type parameter to have something.",
            """
An unconstrained `T` could be *anything*, so you may not touch it:

```ts
function longest<T>(a: T, b: T): T {
  return a.length >= b.length ? a : b;   // ❌ Property 'length' does not exist on type 'T'
}
```

The compiler is right: `T` might be `number`. **Constrain it** with `extends`:

```ts
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;   // ✅
}

longest("abc", "de");        // ✅ strings have length
longest([1], [2, 3]);        // ✅ arrays too
longest(1, 2);               // ❌ numbers do not
```

Read `T extends { length: number }` as *"T, whatever it is, must at least have a
numeric length"*. Inside the function you may use exactly what the constraint
guarantees, and nothing more.

**`extends` here means "is assignable to", not inheritance.** Any type with the
required shape qualifies — structural typing, from week 8.

**Why not just take `{ length: number }` as the parameter type?**

```ts
function longestBad(a: { length: number }, b: { length: number }): { length: number }
```

That works, but the return type has been flattened — the caller gets back
something with only `length`, having passed in strings. The generic **preserves
the actual type**:

```ts
longest("abc", "de").toUpperCase();      // ✅ still a string
longestBad("abc", "de").toUpperCase();   // ❌ information lost
```

This is the clearest demonstration of what generics buy you over a plain
supertype parameter.

**Common constraints:**

```ts
<T extends string>                      // some kind of string
<T extends { id: string }>              // anything with an id
<T extends unknown[]>                   // any array
<T extends object>                      // any non-primitive
```

**Constraints compose with defaults and with `keyof`** (next lesson), and they
are what make a generic *usable* rather than merely general.

> ⚠️ **Common mistakes:** reading `extends` as class inheritance; constraining
> more tightly than the body needs (which rejects valid callers); and forgetting
> that inside the function you get only what the constraint promised, never the
> caller's extra fields.
""",
            warmup=[
                _q("`function f<T>(x: T) { return x.length; }` is…",
                   ["fine", "an error — T might not have length", "an error at runtime",
                    "inferred"], 1,
                   "An unconstrained T guarantees nothing."),
                _q("`<T extends { length: number }>` allows you to pass…",
                   ["only strings", "anything with a numeric length", "only arrays", "numbers"], 1,
                   "Structural, not nominal."),
                _q("`extends` in a constraint means…",
                   ["class inheritance", "is assignable to", "equals", "implements"], 1,
                   "Any type with the required shape qualifies."),
                _q("Taking `{length: number}` directly instead of a constrained generic loses…",
                   ["nothing", "the caller's actual type in the return", "speed",
                    "the constraint"], 1,
                   "The return type would be flattened."),
            ],
            exercises=[
                _ex("tscourse-w10-cn-1", "Constrain to length",
                    "Add the constraint so `.length` may be read inside the function.",
                    'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                    '  return a.length >= b.length ? a : b;\n}\n'
                    'console.log(longest("abc", "de"));\n',
                    'extends { length: number }', [("", "abc")],
                    hints=["State the minimum shape T must have.",
                           "Write extends { length: number }."],
                    difficulty="Medium"),
                _ex("tscourse-w10-cn-2", "Use the preserved type",
                    "The result is still a string, so uppercase it.",
                    'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                    '  return a.length >= b.length ? a : b;\n}\n'
                    'console.log(longest("abc", "de").toUpperCase());\n',
                    'longest("abc", "de").toUpperCase()', [("", "ABC")],
                    hints=["A generic hands back the caller's own type, not the constraint.",
                           'Write longest("abc", "de").toUpperCase().'],
                    difficulty="Medium"),
                _ex("tscourse-w10-cn-3", "Anything with an id",
                    "Return the record's id.",
                    'function idOf<T extends { id: string }>(x: T): string {\n'
                    '  return x.id;\n}\n'
                    'console.log(idOf({ id: "u1", age: 3 }));\n',
                    'return x.id;', [("", "u1")],
                    hints=["The constraint guarantees the id field exists."]),
                _ex("tscourse-w10-cn-4", "Constrain to arrays",
                    "Return how many elements the array-like argument holds.",
                    'function count<T extends unknown[]>(a: T): number {\n'
                    '  return a.length;\n}\n'
                    'console.log(count([1, 2, 3]));\nconsole.log(count(["a"]));\n',
                    'extends unknown[]', [("", "3\n1")],
                    hints=["Any array at all satisfies this.",
                           "Write extends unknown[]."],
                    difficulty="Medium"),
                _ex("tscourse-w10-cn-5", "Longest of records",
                    "The constraint is structural, so a record with a length field qualifies. Print the winner's name.",
                    'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                    '  return a.length >= b.length ? a : b;\n}\n'
                    'const big = { name: "big", length: 10 };\n'
                    'const small = { name: "small", length: 2 };\n'
                    'console.log(longest(big, small).name);\n',
                    'longest(big, small).name', [("", "big")],
                    hints=["The generic preserved the record type, so .name survives.",
                           "Write longest(big, small).name."],
                    difficulty="Medium"),
                _fix("tscourse-w10-cn-fix1", "Fix the flattened return",
                     "Taking the constraint directly as the parameter type loses the string, so `.toUpperCase()` is unavailable and this prints the wrong thing. Make it generic.",
                     'function longest(a: { length: number }, b: { length: number }): { length: number } {\n'
                     '  return a.length >= b.length ? a : b;\n}\n'
                     'console.log(longest("abc", "de").length);\n',
                     'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                     '  return a.length >= b.length ? a : b;\n}\n'
                     'console.log(longest("abc", "de").toUpperCase());\n',
                     [("", "ABC")],
                     hints=["The caller passed strings but got back something with only a length.",
                            "Parameterise with T constrained by the shape, then the string survives."],
                     difficulty="Medium"),
                _fix("tscourse-w10-con-fix2", "Fix the reversed comparison",
                     "`longest` is constrained to things that have a length, but it keeps returning the shorter one. It should print `there` then 3.",
                     'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                     '  return a.length < b.length ? a : b;\n}\n'
                     'console.log(longest("hi", "there"));\n'
                     'console.log(longest([1, 2, 3], [1]).length);\n',
                     'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                     '  return a.length > b.length ? a : b;\n}\n'
                     'console.log(longest("hi", "there"));\n'
                     'console.log(longest([1, 2, 3], [1]).length);\n',
                     [("", "there\n3")],
                     hints=["The constraint guarantees `.length` exists; it says nothing about which way you compare.",
                            "Keep a when its length is greater."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Inside a constrained generic you may use…",
                   ["everything the caller passed", "exactly what the constraint guarantees",
                    "nothing", "only length"], 1,
                   "The body is checked against the constraint, not against any particular caller."),
                _q("A constraint that is tighter than the body needs…",
                   ["is safer", "rejects valid callers for no reason", "is faster",
                    "is required"], 1,
                   "Ask for the minimum you actually use."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w10-keyof", "keyof & indexed access",
            "Types computed from other types.",
            """
`keyof T` is the union of `T`'s key names, as literal types:

```ts
type User = { id: string; age: number };
type K = keyof User;        // "id" | "age"
```

**Indexed access** `T[K]` is the *type of that property*:

```ts
type A = User["age"];              // number
type Either = User[keyof User];    // string | number
```

Note `User["age"]` uses a **type** in the brackets, not a value — it looks like
property access but happens entirely at compile time.

Together they type the single most useful generic helper there is:

```ts
function pluck<T, K extends keyof T>(o: T, k: K): T[K] {
  return o[k];
}

const u = { id: "u1", age: 3 };
pluck(u, "age");      // number   ✅
pluck(u, "id");       // string   ✅
pluck(u, "nope");     // ❌ not assignable to "id" | "age"
```

Read the signature slowly, because it is the pattern:

- `T` — the object's type.
- `K extends keyof T` — the key must be one of `T`'s actual keys.
- `T[K]` — the return is the type of *that specific* property.

So a single function returns a `string` for one key and a `number` for another,
and typos are compile errors. Without generics this would be `any`.

**Sorting by a key** is the everyday application:

```ts
function sortBy<T, K extends keyof T>(rows: T[], key: K): T[] {
  return [...rows].sort((a, b) => (a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0));
}
sortBy(people, "age");      // ✅
sortBy(people, "aeg");      // ❌ caught
```

**`keyof` on an index signature** behaves as you'd expect:

```ts
type Table = { [k: string]: number };
type TK = keyof Table;      // string | number
```

**Where you'll see this:** `Pick`, `Omit` and `Record` (week 12) are all built
from `keyof` and indexed access. Learning to read it now makes that week easy.

> ⚠️ **Common mistakes:** writing `keyof T` where you meant `T[keyof T]` (keys
> versus value types); forgetting the `extends keyof T` constraint, which makes
> `o[k]` an error; and expecting `keyof` to work at runtime — use
> `Object.keys(o)` for that, which returns `string[]`.
""",
            warmup=[
                _q('`keyof { id: string; age: number }` is…',
                   ["string", '"id" | "age"', "string | number", "never"], 1,
                   "The key NAMES as literal types."),
                _q('`{ id: string; age: number }["age"]` is…',
                   ['"age"', "number", "string", "never"], 1,
                   "Indexed access gives the property's type."),
                _q("In `pluck<T, K extends keyof T>(o: T, k: K): T[K]`, the return type is…",
                   ["always any", "the type of the specific property named by k", "T", "K"], 1,
                   "Which is why it returns string for one key and number for another."),
                _q("Does `keyof` exist at runtime?",
                   ["yes", "no — use Object.keys for that", "only for classes",
                    "only for arrays"], 1,
                   "It is a compile-time operator."),
            ],
            exercises=[
                _ex("tscourse-w10-ke-1", "Pluck a field",
                    "Return the property named by the key.",
                    'function pluck<T, K extends keyof T>(o: T, k: K): T[K] {\n'
                    '  return o[k];\n}\n'
                    'const u = { id: "u1", age: 3 };\n'
                    'console.log(pluck(u, "id"));\nconsole.log(pluck(u, "age"));\n',
                    'return o[k];', [("", "u1\n3")],
                    hints=["Bracket access with the key parameter."]),
                _ex("tscourse-w10-ke-2", "Constrain the key",
                    "Add the constraint so only real keys of T are accepted.",
                    'function pluck<T, K extends keyof T>(o: T, k: K): T[K] {\n'
                    '  return o[k];\n}\n'
                    'console.log(pluck({ id: "u1", age: 3 }, "age"));\n',
                    'K extends keyof T', [("", "3")],
                    hints=["The key parameter must be one of T's own key names.",
                           "Write K extends keyof T."],
                    difficulty="Medium"),
                _ex("tscourse-w10-ke-3", "Use the specific return type",
                    "The plucked id is a string, so uppercase it.",
                    'function pluck<T, K extends keyof T>(o: T, k: K): T[K] {\n'
                    '  return o[k];\n}\n'
                    'const u = { id: "u1", age: 3 };\n'
                    'console.log(pluck(u, "id").toUpperCase());\n',
                    'pluck(u, "id").toUpperCase()', [("", "U1")],
                    hints=["T[K] resolved to string for this key.",
                           'Write pluck(u, "id").toUpperCase().'],
                    difficulty="Medium"),
                _ex("tscourse-w10-ke-4", "Sort by a key",
                    "Complete the comparator so the rows sort by the chosen key.",
                    'function sortBy<T, K extends keyof T>(rows: T[], key: K): T[] {\n'
                    '  return [...rows].sort((a, b) => (a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0));\n}\n'
                    'const people = [\n  { name: "Cy", age: 47 },\n  { name: "Bo", age: 20 },\n];\n'
                    'console.log(sortBy(people, "age").map((p) => p.name).join(","));\n',
                    'a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0',
                    [("", "Bo,Cy")],
                    hints=["Return a negative, positive or zero number, comparing the two keyed values.",
                           "Write a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0."],
                    difficulty="Medium"),
                _ex("tscourse-w10-ke-5", "Pluck across a list",
                    "Pull one column out of the records by key.",
                    'function pluckAll<T, K extends keyof T>(rows: T[], k: K): T[K][] {\n'
                    '  return rows.map((r) => r[k]);\n}\n'
                    'const people = [{ name: "Ada", age: 36 }, { name: "Bo", age: 20 }];\n'
                    'console.log(pluckAll(people, "name").join(","));\n',
                    'rows.map((r) => r[k])', [("", "Ada,Bo")],
                    hints=["map each record to the keyed property.",
                           "Write rows.map((r) => r[k])."],
                    difficulty="Medium"),
                _fix("tscourse-w10-ke-fix1", "Fix the any-typed pluck",
                     "This returns `any`, so the mistyped method call was not caught and it crashes. Type it with keyof and call the right method.",
                     'function pluck(o: any, k: string): any {\n  return o[k];\n}\n'
                     'const u = { id: "u1", age: 3 };\nconsole.log(pluck(u, "id").toFixed(2));\n',
                     'function pluck<T, K extends keyof T>(o: T, k: K): T[K] {\n  return o[k];\n}\n'
                     'const u = { id: "u1", age: 3 };\nconsole.log(pluck(u, "id").toUpperCase());\n',
                     [("", "U1")],
                     hints=["With any, calling toFixed on a string raised no complaint.",
                            "Parameterise T and K so the return type is the property's real type."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`T[keyof T]` gives you…",
                   ["the key names", "the union of the property TYPES", "an array", "never"], 1,
                   "keyof gives names; indexing by them gives value types."),
                _q("Omitting `extends keyof T` from the key parameter means…",
                   ["it still works", "o[k] becomes an error, since k might not be a key",
                    "faster inference", "nothing"], 1,
                   "The constraint is what licenses the lookup."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w10-types", "Generic types & interfaces",
            "Parameterising a shape, not just a function.",
            """
Types take parameters too:

```ts
interface Box<T> {
  value: T;
}

const a: Box<string> = { value: "hi" };
const b: Box<number> = { value: 42 };
```

`Box<string>` is a *different type* from `Box<number>`, produced from one
declaration. Type aliases work the same way:

```ts
type Pair<A, B> = { left: A; right: B };
type List<T> = T[];
type Lookup<V> = { [key: string]: V };
```

**The Result type** is the pattern you'll actually reach for, combining week 9's
discriminated union with a type parameter:

```ts
type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

function parseNum(s: string): Result<number> {
  const n = Number(s);
  if (Number.isNaN(n)) return { ok: false, error: `bad number: ${s}` };
  return { ok: true, value: n };
}

const r = parseNum("42");
if (r.ok) {
  r.value.toFixed(2);      // r.value: number
}
```

One `Result<T>` serves every operation that can fail, and the success type
changes per use: `Result<number>`, `Result<User>`, `Result<string[]>`. This is
how serious codebases handle failure without exceptions — and it is the shape
behind Rust's `Result` and many TypeScript libraries.

**Generic types can be constrained** exactly like generic functions:

```ts
type Table<T extends { id: string }> = { [id: string]: T };
```

**Nesting works and reads fine once you're used to it:**

```ts
Result<Box<string>>
Pair<string, number[]>
```

**Recursive generic types** are legal, and are how tree shapes are described:

```ts
type Tree<T> = { value: T; children: Tree<T>[] };
```

**The naming convention** for a generic type's parameter mirrors functions: `T`
for the payload, `K`/`V` for key and value, `E` for an error type. `Result<T, E>`
with a parameterised error is common in larger codebases.

> ⚠️ **Common mistakes:** writing `Box` without its argument (it needs one
> unless there's a default); assuming `Box<string>` is assignable to
> `Box<number>` (it is not); and reaching for a generic type when a plain union
> would say it more clearly.
""",
            warmup=[
                _q("`interface Box<T> { value: T }` — `Box<string>`'s value has type…",
                   ["T", "string", "any", "unknown"], 1, "The argument replaces the parameter."),
                _q("Is `Box<string>` assignable to `Box<number>`?",
                   ["yes", "no", "only if empty", "only with a cast"], 1,
                   "They are unrelated types."),
                _q("`type Result<T> = {ok:true; value:T} | {ok:false; error:string}` — after `if (r.ok)`, `r.value` is…",
                   ["T | undefined", "T", "string", "never"], 1,
                   "The discriminant narrowed it to the success member."),
                _q("Writing `Box` with no type argument is…",
                   ["fine", "an error unless T has a default", "inferred", "any"], 1,
                   "A generic type needs its arguments."),
            ],
            exercises=[
                _ex("tscourse-w10-ty-1", "A generic interface",
                    "Declare Box with a type parameter, then print both boxed values.",
                    'interface Box<T> {\n  value: T;\n}\n'
                    'const a: Box<string> = { value: "hi" };\n'
                    'const b: Box<number> = { value: 42 };\n'
                    'console.log(`${a.value} ${b.value}`);\n',
                    'Box<T>', [("", "hi 42")],
                    hints=["The parameter list goes right after the interface name.",
                           "Write Box<T>."]),
                _ex("tscourse-w10-ty-2", "A generic alias",
                    "Print both sides of the pair.",
                    'type Pair<A, B> = { left: A; right: B };\n'
                    'const p: Pair<string, number> = { left: "x", right: 1 };\n'
                    'console.log(`${p.left}${p.right}`);\n',
                    '${p.left}${p.right}', [("", "x1")],
                    hints=["Two holes, no separator.",
                           "Write ${p.left}${p.right}."]),
                _ex("tscourse-w10-ty-3", "A Result type",
                    "Return the failing Result when the input does not parse.",
                    _LINE + 'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'function parseNum(s: string): Result<number> {\n'
                    '  const n = Number(s);\n'
                    '  if (Number.isNaN(n)) return { ok: false, error: `bad number: ${s}` };\n'
                    '  return { ok: true, value: n };\n}\n'
                    'const r = parseNum(line);\n'
                    'console.log(r.ok ? r.value.toFixed(2) : r.error);\n',
                    'return { ok: false, error: `bad number: ${s}` };',
                    [("42", "42.00"), ("abc", "bad number: abc")],
                    hints=["The failure member carries the tag and the message.",
                           "Write return { ok: false, error: `bad number: ${s}` };"],
                    difficulty="Medium"),
                _ex("tscourse-w10-ty-4", "Consume a Result",
                    "Print the value to 2 decimals on success, or the error message.",
                    _LINE + 'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'function parseNum(s: string): Result<number> {\n'
                    '  const n = Number(s);\n'
                    '  if (Number.isNaN(n)) return { ok: false, error: "bad" };\n'
                    '  return { ok: true, value: n };\n}\n'
                    'const r = parseNum(line);\n'
                    'console.log(r.ok ? r.value.toFixed(2) : r.error);\n',
                    'r.ok ? r.value.toFixed(2) : r.error',
                    [("7", "7.00"), ("zz", "bad")],
                    hints=["The tag narrows, so value and error are each available in one branch only.",
                           "Write r.ok ? r.value.toFixed(2) : r.error."],
                    difficulty="Medium"),
                _ex("tscourse-w10-ty-5", "A generic lookup",
                    "Declare a lookup whose values are numbers, then print one.",
                    'type Lookup<V> = { [key: string]: V };\n'
                    'const prices: Lookup<number> = { coffee: 3.25, book: 12 };\n'
                    'console.log(prices["coffee"].toFixed(2));\n',
                    'Lookup<number>', [("", "3.25")],
                    hints=["Supply the value type as the argument.",
                           "Write Lookup<number>."],
                    difficulty="Medium"),
                _fix("tscourse-w10-ty-fix1", "Fix the missing type argument",
                     "`Box` was used without its argument, so the value was left untyped and the wrong method was called. Supply the argument and call the right one.",
                     'interface Box<T> {\n  value: T;\n}\n'
                     'const a: Box<any> = { value: "hi" };\n'
                     'console.log(a.value.toFixed(2));\n',
                     'interface Box<T> {\n  value: T;\n}\n'
                     'const a: Box<string> = { value: "hi" };\n'
                     'console.log(a.value.toUpperCase());\n',
                     [("", "HI")],
                     hints=["Box<any> silenced the check; the value really is a string.",
                            "Use Box<string> and call a string method."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`Result<T>` is useful because…",
                   ["it is shorter", "one failure-handling shape serves every success type",
                    "it avoids unions", "it is built in"], 1,
                   "The success payload varies; the machinery does not."),
                _q("`type Tree<T> = { value: T; children: Tree<T>[] }` is…",
                   ["illegal", "a legal recursive generic type", "an interface", "a union"], 1,
                   "Recursion in type definitions is fine."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w10-defaults", "Defaults & knowing when to stop",
            "Default type arguments, and generics that aren't worth it.",
            """
A type parameter can have a **default**, used when the caller doesn't supply
one:

```ts
interface Options<T = string> {
  items: T[];
}

const a: Options = { items: ["x"] };            // T defaults to string
const b: Options<number> = { items: [1, 2] };
```

Defaults make a generic type usable in the common case without ceremony. They
follow the same rule as default parameters in week 5: **defaults come last.**

```ts
type Result<T, E = string> =
  | { ok: true; value: T }
  | { ok: false; error: E };

Result<number>              // error is string
Result<number, Error>       // error is an Error
```

**Constraints and defaults combine**, in that order:

```ts
interface Table<T extends { id: string } = { id: string }> { rows: T[] }
```

---

**Now the more valuable half of this lesson: when *not* to reach for a generic.**

Generics have a real cost — every reader has to hold another variable in their
head. Three signs you don't need one:

**1. The parameter appears only once.**

```ts
function log<T>(x: T): void { console.log(x); }     // 🚩
function log(x: unknown): void { console.log(x); }  // ✅ says the same thing
```

If `T` doesn't connect two places, it is decoration.

**2. You immediately constrain it to exactly one thing.**

```ts
function f<T extends string>(x: T): void { ... }    // 🚩 unless you return T
function f(x: string): void { ... }                 // ✅
```

The exception is when you *return* `T` — then the constraint preserves literal
types, which is genuinely useful.

**3. You end up casting inside.** If the body needs `as` to do its work, the
signature is promising something the implementation can't honour. Rethink the
types rather than papering over them.

**And the counter-test — when you *do* want one:** a type appears in two or
more positions and callers would otherwise lose information. `first`, `pluck`,
`sortBy`, `Result` all pass. `log` does not.

**Reading generics you didn't write** is most of the benefit here. When a
library signature looks frightening, name the parts:

```ts
function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] }
```

*"For any row type T, and any key K of T, take rows and a key, and give back a
lookup from key values to arrays of rows."* Once you can do that narration, the
ecosystem opens up.

> ⚠️ **Common mistakes:** adding type parameters for symmetry; putting a
> defaulted parameter before a required one; and treating a scary-looking
> signature as unknowable rather than reading it left to right.
""",
            warmup=[
                _q("`interface Options<T = string>` used as plain `Options` gives T as…",
                   ["any", "string", "unknown", "an error"], 1, "The default fills in."),
                _q("Defaulted type parameters must come…",
                   ["first", "last", "anywhere", "alone"], 1,
                   "Same rule as default value parameters."),
                _q("`function log<T>(x: T): void` — is the generic earning its place?",
                   ["yes", "no — T appears only once", "yes, for speed", "only for arrays"], 1,
                   "Nothing is connected, so `unknown` says it better."),
                _q("Needing `as` inside a generic's body usually means…",
                   ["you are done", "the signature promises more than the body can honour",
                    "it is optimised", "T is wrong"], 1,
                   "A cast there is a design smell."),
            ],
            exercises=[
                _ex("tscourse-w10-df-1", "A default type argument",
                    "Give T a default of string, then use Options with no argument.",
                    'interface Options<T = string> {\n  items: T[];\n}\n'
                    'const a: Options = { items: ["x", "y"] };\n'
                    'console.log(a.items.join(","));\n',
                    'T = string', [("", "x,y")],
                    hints=["The default is written with = after the parameter name.",
                           "Write T = string."]),
                _ex("tscourse-w10-df-2", "Override the default",
                    "Use Options at number, then total the items.",
                    'interface Options<T = string> {\n  items: T[];\n}\n'
                    'const b: Options<number> = { items: [1, 2, 3] };\n'
                    'console.log(b.items.reduce((s, x) => s + x, 0));\n',
                    'Options<number>', [("", "6")],
                    hints=["Supply the argument explicitly to override the default.",
                           "Write Options<number>."]),
                _ex("tscourse-w10-df-3", "Result with a defaulted error",
                    "Print the value on success, or the error message.",
                    _LINE + 'type Result<T, E = string> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: E };\n'
                    'function parseNum(s: string): Result<number> {\n'
                    '  const n = Number(s);\n'
                    '  if (Number.isNaN(n)) return { ok: false, error: "bad" };\n'
                    '  return { ok: true, value: n };\n}\n'
                    'const r = parseNum(line);\nconsole.log(r.ok ? r.value : r.error);\n',
                    'T, E = string', [("5", "5"), ("zz", "bad")],
                    hints=["The payload type is required; the error type defaults.",
                           "Write T, E = string."],
                    difficulty="Medium"),
                _ex("tscourse-w10-df-4", "Prefer unknown to a pointless generic",
                    "This helper only prints, so it needs no type parameter. Give it the right one.",
                    'function show(x: unknown): void {\n  console.log(x);\n}\n'
                    'show("a");\nshow(1);\n',
                    'x: unknown', [("", "a\n1")],
                    hints=["Nothing is returned, so no type needs preserving.",
                           "Write x: unknown."]),
                _ex("tscourse-w10-df-5", "Group rows by a key",
                    "Complete the grouping so each key value collects its rows.",
                    'function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] } {\n'
                    '  const out: { [k: string]: T[] } = {};\n'
                    '  for (const r of rows) {\n'
                    '    const k = String(r[key]);\n'
                    '    if (out[k] === undefined) {\n      out[k] = [];\n    }\n'
                    '    out[k].push(r);\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'const rows = [\n  { tag: "food", n: 1 },\n  { tag: "home", n: 2 },\n  { tag: "food", n: 3 },\n];\n'
                    'const g = groupBy(rows, "tag");\n'
                    'console.log(Object.keys(g).sort().map((k) => `${k}=${g[k].length}`).join(","));\n',
                    'if (out[k] === undefined) {\n      out[k] = [];\n    }\n'
                    '    out[k].push(r);',
                    [("", "food=2,home=1")],
                    hints=["Create the bucket before pushing into it — week 7's grouping pattern.",
                           "Write if (out[k] === undefined) { out[k] = []; } then out[k].push(r);"],
                    difficulty="Medium"),
                _fix("tscourse-w10-df-fix1", "Fix the default's position",
                     "A defaulted type parameter sits before a required one, so `Pair<number>` cannot work. Reorder them.",
                     'type Pair<A = string, B> = { left: A; right: B };\n'
                     'const p: Pair<string, number> = { left: "x", right: 1 };\n'
                     'console.log(`${p.left}${p.right}`);\n',
                     'type Pair<A, B = string> = { left: A; right: B };\n'
                     'const p: Pair<number, string> = { left: 1, right: "x" };\n'
                     'console.log(`${p.left}${p.right}`);\n',
                     [("", "1x")],
                     hints=["Defaults must come last, or callers could never skip them.",
                            "Move the default onto B, and swap the arguments at the use site."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Which signature genuinely needs a generic?",
                   ["log<T>(x: T): void", "pluck<T, K extends keyof T>(o: T, k: K): T[K]",
                    "print<T>(x: T): void", "warn<T>(x: T): void"], 1,
                   "Its type parameters connect the arguments to the return type."),
                _q("The best way to read an intimidating generic signature is…",
                   ["skip it", "narrate it left to right, naming each parameter",
                    "look at the body", "assume any"], 1,
                   "'For any T, and any key K of T, …'"),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w10-hof", "Generics that take functions",
            "Two type parameters, with a callback carrying you from one to the other.",
            """
Every generic helper you have written so far kept the same type all the way
through: `T` in, `T` out. The helpers you actually use every day are more
interesting than that — they **change** the type on the way through, and the
callback is what decides the new one.

Look at `map`, written out longhand:

```ts
function mapAll<T, U>(xs: T[], f: (x: T) => U): U[] {
  const out: U[] = [];
  for (const x of xs) out.push(f(x));
  return out;
}

mapAll([1, 2, 3], (n) => n * 2);        // T = number, U = number  → number[]
mapAll(["a", "bb"], (s) => s.length);   // T = string, U = number  → number[]
```

Two parameters, two different jobs:

| parameter | where it comes from |
|---|---|
| `T` | inferred from the array you pass |
| `U` | inferred from **what the callback returns** |

Neither is written at the call site. You describe the *relationship* — "give me
an array of whatever this function hands back" — and inference fills in the rest.
This is the whole idea of generics arriving at its most useful form.

**The shape recurs everywhere.** Once you can read `<T, U>` you can write the
standard toolkit:

```ts
function groupBy<T>(xs: T[], key: (x: T) => string): { [k: string]: T[] } { … }
function uniqueBy<T>(xs: T[], key: (x: T) => string): T[] { … }
function maxBy<T>(xs: T[], score: (x: T) => number): T { … }
function zip<A, B>(as: A[], bs: B[]): Array<[A, B]> { … }
```

Note the pattern in the first three: the callback's *return* type is fixed
(`string`, `number`) because the helper needs to compare or index with it, while
`T` stays free. That combination — one parameter open, one pinned — is what makes
them usable on any record shape you invent later.

**`zip` needs two open parameters** because it genuinely relates two independent
things, and the tuple `[A, B]` records that relationship in the result. `T[]` and
`Array<T>` are the same notation, by the way; `Array<[A, B]>` is just easier to
read than `[A, B][]`.

**Naming.** `T` and `U` are fine for a helper that truly works on anything.
`K`/`V` are conventional for a key and value. Once a parameter means something
specific to your domain, spell it out — `<Row>` reads far better than `<T>` in a
function that only makes sense over table rows.

**When inference has nothing to work from, say it yourself:**

```ts
const nums = emptyOf<number>();   // no argument, so nothing to infer from
```

Explicit type arguments are the exception, not the rule — needing them on a call
that *does* pass data usually means the signature is describing the wrong
relationship.

> ⚠️ **Common mistakes:** pushing the original item instead of the callback's
> result, so `U` is a lie; forgetting the callback's parameter type is `T` and
> annotating it `any`; and giving a helper two type parameters when the second
> one only ever appears once — if `U` shows up in exactly one place, it isn't
> relating anything and can be a concrete type.
""",
            warmup=[
                _q("In `mapAll<T, U>(xs: T[], f: (x: T) => U): U[]`, where does `U` come from?",
                   ["the array", "the callback's return type", "the call site, always", "the return statement"], 1,
                   "Inference reads it off what the callback hands back."),
                _q("`mapAll([\"a\", \"bb\"], (s) => s.length)` has type…",
                   ["string[]", "number[]", "unknown[]", "(string | number)[]"], 1,
                   "T is string, U is number, so the result is number[]."),
                _q("`Array<[A, B]>` and `[A, B][]` are…",
                   ["different types", "the same type written two ways", "only valid for tuples", "an error"], 1,
                   "Pick whichever reads better in context."),
                _q("A helper whose second type parameter appears only once…",
                   ["is optimal", "probably doesn't need to be generic there",
                    "cannot compile", "must be constrained"], 1,
                   "A type parameter earns its keep by relating two positions."),
            ],
            exercises=[
                _ex("tscourse-w10-hof-1", "Type the callback",
                    "Fill in the callback's parameter, so `mapAll` takes a `T` and produces a `U`.",
                    'function mapAll<T, U>(xs: T[], f: (x: T) => U): U[] {\n'
                    '  const out: U[] = [];\n'
                    '  for (const x of xs) out.push(f(x));\n'
                    '  return out;\n}\n'
                    'console.log(mapAll([1, 2, 3], (n) => n * 2).join(","));\n'
                    'console.log(mapAll(["a", "bb"], (s) => s.length).join(","));\n',
                    'f: (x: T) => U', [("", "2,4,6\n1,2")],
                    hints=["The callback receives an element of the input array and returns an element of the output.",
                           "Write f: (x: T) => U."]),
                _ex("tscourse-w10-hof-2", "Generic groupBy",
                    "Finish the bucket step so any array can be grouped by any key function.",
                    'function groupBy<T>(xs: T[], key: (x: T) => string): { [k: string]: T[] } {\n'
                    '  const out: { [k: string]: T[] } = {};\n'
                    '  for (const x of xs) {\n'
                    '    const k = key(x);\n'
                    '    out[k] = out[k] ?? [];\n'
                    '    out[k].push(x);\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'const words = ["ant", "bee", "ape"];\n'
                    'const byLetter = groupBy(words, (w) => w[0]);\n'
                    'console.log(Object.keys(byLetter).sort().join(","));\n'
                    'console.log(byLetter["a"].join(" "));\n',
                    'out[k].push(x);', [("", "a,b\nant ape")],
                    hints=["The bucket already exists by this line — add the item to it.",
                           "Push the item itself, not the key."],
                    difficulty="Easy"),
                _ex("tscourse-w10-hof-3", "Two open parameters",
                    "`zip` pairs two independent arrays. Fill in its return annotation.",
                    'function zip<A, B>(as: A[], bs: B[]): Array<[A, B]> {\n'
                    '  const out: Array<[A, B]> = [];\n'
                    '  const n = Math.min(as.length, bs.length);\n'
                    '  for (let i = 0; i < n; i++) out.push([as[i], bs[i]]);\n'
                    '  return out;\n}\n'
                    'const pairs = zip(["a", "b", "c"], [1, 2]);\n'
                    'console.log(pairs.map((p) => `${p[0]}=${p[1]}`).join(","));\n',
                    'Array<[A, B]> {', [("", "a=1,b=2")],
                    hints=["Each element pairs one A with one B — that is a two-element tuple.",
                           "The result is an array of those tuples: Array<[A, B]>."],
                    difficulty="Medium"),
                _ex("tscourse-w10-hof-4", "Generic uniqueBy",
                    "Keep the first record for each key and skip the rest. Add the skipping check.",
                    'function uniqueBy<T>(xs: T[], key: (x: T) => string): T[] {\n'
                    '  const seen: { [k: string]: boolean } = {};\n'
                    '  const out: T[] = [];\n'
                    '  for (const x of xs) {\n'
                    '    const k = key(x);\n'
                    '    if (seen[k]) continue;\n'
                    '    seen[k] = true;\n'
                    '    out.push(x);\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'const people = [\n'
                    '  { name: "ada", city: "london" },\n'
                    '  { name: "alan", city: "london" },\n'
                    '  { name: "grace", city: "ny" },\n'
                    '];\n'
                    'console.log(uniqueBy(people, (p) => p.city).map((p) => p.name).join(","));\n',
                    'if (seen[k]) continue;', [("", "ada,grace")],
                    hints=["If this key has been recorded already, move on to the next item.",
                           "Write if (seen[k]) continue;"],
                    difficulty="Medium"),
                _ex("tscourse-w10-hof-5", "Say it when nothing can be inferred",
                    "There is no argument to infer from here, so supply the type argument yourself.",
                    'function emptyOf<T>(): T[] {\n'
                    '  return [];\n}\n'
                    'const nums = emptyOf<number>();\n'
                    'nums.push(1);\n'
                    'nums.push(2);\n'
                    'console.log(nums.join(","));\n',
                    'emptyOf<number>()', [("", "1,2")],
                    hints=["Type arguments go in angle brackets between the name and the parentheses.",
                           "Write emptyOf<number>()."],
                    difficulty="Easy"),
                _fix("tscourse-w10-hof-fix1", "Fix the ignored callback",
                     "This should print `2,4,6` but prints the originals — the callback's result is being thrown away.",
                     'function mapAll<T, U>(xs: T[], f: (x: T) => U): U[] {\n'
                     '  const out: U[] = [];\n'
                     '  for (const x of xs) out.push(x as unknown as U);\n'
                     '  return out;\n}\n'
                     'console.log(mapAll([1, 2, 3], (n) => n * 2).join(","));\n',
                     'function mapAll<T, U>(xs: T[], f: (x: T) => U): U[] {\n'
                     '  const out: U[] = [];\n'
                     '  for (const x of xs) out.push(f(x));\n'
                     '  return out;\n}\n'
                     'console.log(mapAll([1, 2, 3], (n) => n * 2).join(","));\n',
                     [("", "2,4,6")],
                     hints=["The double assertion was silencing the very error that would have caught this.",
                            "Push what the callback returns: out.push(f(x))."],
                     difficulty="Medium"),
                _fix("tscourse-w10-hof-fix2", "Fix the overrun",
                     "Zipping a three-element array with a two-element one should give two pairs, but a third appears with an undefined half.",
                     'function zip<A, B>(as: A[], bs: B[]): Array<[A, B]> {\n'
                     '  const out: Array<[A, B]> = [];\n'
                     '  const n = as.length;\n'
                     '  for (let i = 0; i < n; i++) out.push([as[i], bs[i]]);\n'
                     '  return out;\n}\n'
                     'const pairs = zip(["a", "b", "c"], [1, 2]);\n'
                     'console.log(pairs.map((p) => `${p[0]}=${p[1]}`).join(","));\n',
                     'function zip<A, B>(as: A[], bs: B[]): Array<[A, B]> {\n'
                     '  const out: Array<[A, B]> = [];\n'
                     '  const n = Math.min(as.length, bs.length);\n'
                     '  for (let i = 0; i < n; i++) out.push([as[i], bs[i]]);\n'
                     '  return out;\n}\n'
                     'const pairs = zip(["a", "b", "c"], [1, 2]);\n'
                     'console.log(pairs.map((p) => `${p[0]}=${p[1]}`).join(","));\n',
                     [("", "a=1,b=2")],
                     hints=["Reading past the end of the shorter array gives undefined.",
                            "Stop at Math.min(as.length, bs.length)."]),
                _fix("tscourse-w10-hof-fix3", "Fix the forgetful set",
                     "This should print `ada,grace` but keeps every record — nothing is ever recorded as seen.",
                     'function uniqueBy<T>(xs: T[], key: (x: T) => string): T[] {\n'
                     '  const seen: { [k: string]: boolean } = {};\n'
                     '  const out: T[] = [];\n'
                     '  for (const x of xs) {\n'
                     '    const k = key(x);\n'
                     '    if (seen[k]) continue;\n'
                     '    out.push(x);\n'
                     '  }\n'
                     '  return out;\n}\n'
                     'const people = [\n'
                     '  { name: "ada", city: "london" },\n'
                     '  { name: "alan", city: "london" },\n'
                     '  { name: "grace", city: "ny" },\n'
                     '];\n'
                     'console.log(uniqueBy(people, (p) => p.city).map((p) => p.name).join(","));\n',
                     'function uniqueBy<T>(xs: T[], key: (x: T) => string): T[] {\n'
                     '  const seen: { [k: string]: boolean } = {};\n'
                     '  const out: T[] = [];\n'
                     '  for (const x of xs) {\n'
                     '    const k = key(x);\n'
                     '    if (seen[k]) continue;\n'
                     '    seen[k] = true;\n'
                     '    out.push(x);\n'
                     '  }\n'
                     '  return out;\n}\n'
                     'const people = [\n'
                     '  { name: "ada", city: "london" },\n'
                     '  { name: "alan", city: "london" },\n'
                     '  { name: "grace", city: "ny" },\n'
                     '];\n'
                     'console.log(uniqueBy(people, (p) => p.city).map((p) => p.name).join(","));\n',
                     [("", "ada,grace")],
                     hints=["The check reads `seen`, but nothing ever writes to it.",
                            "Mark the key before pushing: seen[k] = true;"],
                     difficulty="Medium"),
                _ch("tscourse-w10-hof-ch1", "A generic reporting toolkit", "Hard",
                    "Write two helpers that work on any record type. `countBy(xs, key)` counts items per key; `maxBy(xs, score)` returns the item with the highest score. The program then reports sales per region and the single biggest sale.",
                    _FS +
                    'interface Sale {\n  region: string;\n  amount: number;\n}\n'
                    'function countBy<T>(xs: T[], key: (x: T) => string): { [k: string]: number } {\n'
                    '  const out: { [k: string]: number } = {};\n'
                    '  for (const x of xs) {\n'
                    '    const k = key(x);\n'
                    '    out[k] = (out[k] ?? 0) + 1;\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'function maxBy<T>(xs: T[], score: (x: T) => number): T {\n'
                    '  let best = xs[0];\n'
                    '  for (const x of xs) {\n'
                    '    if (score(x) > score(best)) best = x;\n'
                    '  }\n'
                    '  return best;\n}\n'
                    'const sales: Sale[] = fs.readFileSync(0, "utf8").trim().split("\\n")\n'
                    '  .filter((l) => l.trim().length > 0)\n'
                    '  .map((l) => {\n'
                    '    const parts = l.split(",");\n'
                    '    return { region: parts[0].trim(), amount: Number(parts[1]) };\n'
                    '  });\n'
                    'const counts = countBy(sales, (s) => s.region);\n'
                    'for (const r of Object.keys(counts).sort()) console.log(`${r}: ${counts[r]}`);\n'
                    'const top = maxBy(sales, (s) => s.amount);\n'
                    'console.log(`Top: ${top.region} ${top.amount}`);\n',
                    'function countBy<T>(xs: T[], key: (x: T) => string): { [k: string]: number } {\n'
                    '  const out: { [k: string]: number } = {};\n'
                    '  for (const x of xs) {\n'
                    '    const k = key(x);\n'
                    '    out[k] = (out[k] ?? 0) + 1;\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'function maxBy<T>(xs: T[], score: (x: T) => number): T {\n'
                    '  let best = xs[0];\n'
                    '  for (const x of xs) {\n'
                    '    if (score(x) > score(best)) best = x;\n'
                    '  }\n'
                    '  return best;\n}',
                    [("north,30\nsouth,20\nnorth,12", "north: 2\nsouth: 1\nTop: north 30"),
                     ("a,5\nb,9", "a: 1\nb: 1\nTop: b 9"),
                     ("solo,7", "solo: 1\nTop: solo 7")],
                    hints=["Both helpers keep T open and pin the callback's return type — string for a key, number for a score.",
                           "countBy is the tally pattern with (out[k] ?? 0) + 1.",
                           "maxBy tracks a running best, starting from the first element.",
                           "Neither helper mentions Sale anywhere — that is the point of writing them generically."]),
            ],
            quiz=[
                _q("In `mapAll<T, U>`, `U` is determined by…",
                   ["the input array", "what the callback returns", "the call site only", "the return statement's variable"], 1,
                   "Inference reads U off the callback's result type."),
                _q("`groupBy<T>(xs: T[], key: (x: T) => string)` pins the callback's return to `string` because…",
                   ["strings are faster", "the helper uses it as an object key",
                    "T must be a string", "generics require it"], 1,
                   "Object keys are strings, so that position cannot stay open."),
                _q("`zip` needs two type parameters because…",
                   ["it takes two arguments", "it relates two independent element types in the result",
                    "tuples require it", "inference fails otherwise"], 1,
                   "The tuple [A, B] carries both through to the output."),
                _q("You should write explicit type arguments…",
                   ["always", "rarely — mainly when there is no argument to infer from",
                    "never", "whenever there are two parameters"], 1,
                   "Needing them on a call that does pass data is usually a signature smell."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #10 — a generic toolkit",
        """
Budget Buddy's helpers stop being about expenses and start being about
**records** — reusable over any row type at all.

Build three generics and use them on an expense ledger. Input is one row per
line, `desc amount tag`:

```
coffee 3.25 food
rent 900 home
lunch 9.50 food
book 12 fun
```

Print:

```
Rows:     4
By tag:   food=2, fun=1, home=1
Dearest:  rent
Cheapest: coffee
```

Required signatures — implement these exactly:

```ts
function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] }
function maxBy<T, K extends keyof T>(rows: T[], key: K): T
function minBy<T, K extends keyof T>(rows: T[], key: K): T
```

Rules:

- `By tag` lists each tag and its row count, keys sorted alphabetically, joined
  with `, `.
- `Dearest` and `Cheapest` are the descriptions of the rows with the largest and
  smallest amounts. On a tie the **first** such row wins.
- The helpers must not mention `Expense` anywhere — they work for any record.
""",
        _ch("tscourse-w10-capstone", "Budget Buddy #10", "Medium",
            "Write the three generic helpers, then apply them to the parsed rows.",
            _FS + 'interface Expense {\n  desc: string;\n  amount: number;\n  tag: string;\n}\n'
            'function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] } {\n'
            '  const out: { [k: string]: T[] } = {};\n'
            '  for (const r of rows) {\n'
            '    const k = String(r[key]);\n'
            '    if (out[k] === undefined) {\n      out[k] = [];\n    }\n'
            '    out[k].push(r);\n'
            '  }\n'
            '  return out;\n}\n'
            'function maxBy<T, K extends keyof T>(rows: T[], key: K): T {\n'
            '  let best = rows[0];\n'
            '  for (const r of rows) {\n    if (r[key] > best[key]) {\n      best = r;\n    }\n  }\n'
            '  return best;\n}\n'
            'function minBy<T, K extends keyof T>(rows: T[], key: K): T {\n'
            '  let best = rows[0];\n'
            '  for (const r of rows) {\n    if (r[key] < best[key]) {\n      best = r;\n    }\n  }\n'
            '  return best;\n}\n'
            'function parse(line: string): Expense {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0], amount: Number(p[1]), tag: p[2] };\n}\n'
            'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const groups = groupBy(rows, "tag");\n'
            'const tagParts = Object.keys(groups).sort().map((k) => `${k}=${groups[k].length}`);\n'
            'console.log(`Rows:     ${rows.length}`);\n'
            'console.log(`By tag:   ${tagParts.join(", ")}`);\n'
            'console.log(`Dearest:  ${maxBy(rows, "amount").desc}`);\n'
            'console.log(`Cheapest: ${minBy(rows, "amount").desc}`);\n',
            'function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] } {\n'
            '  const out: { [k: string]: T[] } = {};\n'
            '  for (const r of rows) {\n'
            '    const k = String(r[key]);\n'
            '    if (out[k] === undefined) {\n      out[k] = [];\n    }\n'
            '    out[k].push(r);\n'
            '  }\n'
            '  return out;\n}\n'
            'function maxBy<T, K extends keyof T>(rows: T[], key: K): T {\n'
            '  let best = rows[0];\n'
            '  for (const r of rows) {\n    if (r[key] > best[key]) {\n      best = r;\n    }\n  }\n'
            '  return best;\n}\n'
            'function minBy<T, K extends keyof T>(rows: T[], key: K): T {\n'
            '  let best = rows[0];\n'
            '  for (const r of rows) {\n    if (r[key] < best[key]) {\n      best = r;\n    }\n  }\n'
            '  return best;\n}',
            [("coffee 3.25 food\nrent 900 home\nlunch 9.50 food\nbook 12 fun",
              "Rows:     4\nBy tag:   food=2, fun=1, home=1\nDearest:  rent\nCheapest: coffee"),
             ("tea 2 drink",
              "Rows:     1\nBy tag:   drink=1\nDearest:  tea\nCheapest: tea"),
             ("a 5 x\nb 5 x",
              "Rows:     2\nBy tag:   x=2\nDearest:  a\nCheapest: a")],
            hints=["All three helpers take `rows: T[]` and `key: K extends keyof T` — they must never mention Expense.",
                   "groupBy is week 7's grouping pattern: String(r[key]) for the bucket name, create the array before pushing.",
                   "maxBy and minBy are the best-so-far accumulator, seeded with rows[0] so the answer is always a real row.",
                   "Use a strict comparison (> and <) so a tie keeps the FIRST row.",
                   'Call them as maxBy(rows, "amount").desc — the return type is T, so .desc is available.']),
        example_io="Rows:     4\nBy tag:   food=2, fun=1, home=1\nDearest:  rent\nCheapest: coffee",
        rubric=["The three helpers are generic over the row type and its keys",
                "None of them mentions the Expense type",
                "groupBy creates each bucket before pushing into it",
                "maxBy and minBy seed from rows[0] and keep the first row on a tie"],
        stretch=_ch("tscourse-w10-capstone-stretch", "Budget Buddy #10 (stretch)", "Medium",
                    "Add a generic `sumBy<T, K extends keyof T>(rows: T[], key: K): number` and print `Total:    $924.75` from it. Since T[K] could be anything, convert each value with Number(...) before adding.",
                    _FS + 'interface Expense {\n  desc: string;\n  amount: number;\n  tag: string;\n}\n'
                    'function sumBy<T, K extends keyof T>(rows: T[], key: K): number {\n'
                    '  return rows.reduce((s, r) => s + Number(r[key]), 0);\n}\n'
                    'function parse(line: string): Expense {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0], amount: Number(p[1]), tag: p[2] };\n}\n'
                    'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'console.log(`Total:    $${sumBy(rows, "amount").toFixed(2)}`);\n',
                    'function sumBy<T, K extends keyof T>(rows: T[], key: K): number {\n'
                    '  return rows.reduce((s, r) => s + Number(r[key]), 0);\n}',
                    [("coffee 3.25 food\nrent 900 home\nlunch 9.50 food\nbook 12 fun",
                      "Total:    $924.75"),
                     ("tea 2 drink", "Total:    $2.00")],
                    hints=["The key could name a non-numeric field, so the compiler will not let you add T[K] directly.",
                           "Convert at the point of use: Number(r[key]).",
                           "Fold with reduce and an explicit seed of 0."]),
    ),
))

# ===========================================================================
# MONTHS 3-8 — themed skeletons (authored in later batches).
# ===========================================================================
_WEEKS += [
    _skel(11, 3, _M3, "Immutability & readonly",
          "Lock data down with readonly, as const, and pure (copy-don't-mutate) updates."),
    _skel(12, 3, _M3, "Utility Types",
          "Reshape existing types with Partial, Pick, Omit, and Record."),
]
_M4 = "Robust, Real-World Programs"
_WEEKS += [
    _skel(13, 4, _M4, "Optionals & Null-Safety",
          "Handle possibly-missing values with ?., ??, and strict null checks."),
    _skel(14, 4, _M4, "Error Handling",
          "Fail loudly and recover gracefully with try/catch and the Result pattern."),
    _skel(15, 4, _M4, "Modules & Organization",
          "Split a program across files with import/export and clear boundaries."),
    _skel(16, 4, _M4, "Async & Promises",
          "Work with promises and async/await for tasks that take time."),
]
_M5 = "Data Structures in TypeScript"
_WEEKS += [
    _skel(17, 5, _M5, "Stacks & Queues",
          "Build and use LIFO/FIFO structures and know when each fits."),
    _skel(18, 5, _M5, "Maps & Sets",
          "Reach for hash maps and sets to get O(1) lookup and de-duplication."),
    _skel(19, 5, _M5, "Recursion",
          "Solve problems whose definition refers to themselves."),
    _skel(20, 5, _M5, "Linked Lists & Trees",
          "Model data as nodes that point to other nodes."),
]
_M6 = "Algorithmic Thinking"
_WEEKS += [
    _skel(21, 6, _M6, "Big-O & Complexity",
          "Reason about the time and space cost of your code."),
    _skel(22, 6, _M6, "Searching & Two Pointers",
          "Binary search a sorted array and sweep it with two pointers."),
    _skel(23, 6, _M6, "Sliding Window & Prefix Sums",
          "Answer range and subarray questions in linear time."),
    _skel(24, 6, _M6, "Sorting",
          "Understand the common sorts and use sorting as a problem-solving tool."),
]
_M7 = "DSA Interview Core"
_WEEKS += [
    _skel(25, 7, _M7, "Recursion & Backtracking",
          "Generate and search combinatorial spaces (subsets, permutations)."),
    _skel(26, 7, _M7, "Dynamic Programming",
          "Turn overlapping recursion into fast, memoized DP."),
    _skel(27, 7, _M7, "Graphs: BFS & DFS",
          "Traverse graphs and grids to answer reachability and shortest-path questions."),
    _skel(28, 7, _M7, "Heaps & Intervals",
          "Use priority queues and interval techniques on classic problems."),
]
_M8 = "Advanced Types & Interview Polish"
_WEEKS += [
    _skel(29, 8, _M8, "Conditional & Mapped Types",
          "Compute new types from existing ones with conditional and mapped types."),
    _skel(30, 8, _M8, "Inference & Template Literal Types",
          "Bend the inference engine and build types from string patterns."),
    _skel(31, 8, _M8, "Type-Level Challenges",
          "Solve 'type gymnastics' puzzles the way interviewers pose them."),
    _skel(32, 8, _M8, "Mock Interview Week",
          "Put it together under time: DSA solved in TypeScript plus type challenges."),
]


# ===========================================================================
# CONCEPT-SCOPE LINT — enforce "never require concepts beyond this week".
# For each authored week, scan every program (drills/fixes/challenges/capstone/
# stretch) for tokens that belong to a LATER week. Fails generation if violated.
# ===========================================================================
def _all_programs(week):
    out = []
    for l in week["lessons"]:
        for ex in l["exercises"]:
            out.append((ex["id"], ex["solution"]))
            out.append((ex["id"] + ":starter", ex["starter"]))
    cap = week.get("capstone")
    if cap:
        for ex in (cap.get("exercise"), cap.get("stretch")):
            if ex:
                out.append((ex["id"], ex["solution"]))
        if cap.get("reference"):
            out.append((cap["title"] + ":ref", cap["reference"]))
    return out


# (token substring, first week it's allowed). A program in a week EARLIER than
# the listed week must not contain the token.
_SCOPE_RULES = [
    ("while (", 4), ("for (", 4),          # loops
    ("=> ", 5), ("function ", 5),          # functions
    (".map(", 6), (".filter(", 6),
    (".split(", 6), (".join(", 6),         # array methods
    (".push(", 6), (".sort(", 6), (".find(", 6),   # array mutation/search
    ("?.", 7), ("Object.keys(", 7),         # optional chaining, object reflection
    (".reduce(", 8),                        # reduce
    ("interface ", 8), ("type ", 8),        # named types (annotations OK earlier)
    ("keyof ", 10),                         # keyof / indexed access
]


def _lint_scope(weeks):
    problems = []
    for w in weeks:
        if not w.get("authored"):
            continue
        wn = w["number"]
        for pid, prog in _all_programs(w):
            for token, allowed_from in _SCOPE_RULES:
                if wn < allowed_from and token in prog:
                    problems.append(
                        f"Week {wn} program {pid} uses {token!r} (not introduced until week {allowed_from})"
                    )
    if problems:
        raise AssertionError("TS course scope violations:\n  " + "\n  ".join(problems))


_lint_scope(_WEEKS)


TS_COURSE = {
    "key": "typescript",
    "title": "TypeScript: Zero to Interview",
    "subtitle": (
        "An 8-month, week-by-week course from your very first line of code to "
        "interview-ready — DSA solved in TypeScript and deep type-system mastery. "
        "Each authored week is five to ten hours of study across seven to nine "
        "lessons, with a goal, warm-ups that make you predict the output, "
        "fill-in-the-blank drills, fix-the-bug programs, an integrative "
        "challenge, hint ladders, a glossary, a cheat sheet, and a growing "
        "capstone project (Budget Buddy). "
        "Nothing ever requires syntax a later week hasn't taught yet."
    ),
    "weeks": _WEEKS,
}
