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
    est_minutes=300,
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

⏱️ Budget about **five hours**, spread over several sittings.
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
    est_minutes=300,
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

⏱️ Budget about **five hours**.
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
    est_minutes=300,
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

⏱️ Budget about **five hours**.
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
    est_minutes=300,
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

⏱️ Budget about **five hours**.
""",
    objectives=[
        "Declare a function with parameters, a return type, and a return value",
        "Call a function and use what it hands back",
        "Write compact functions as arrow functions",
        "Return early with guard clauses instead of deep nesting",
        "Give parameters defaults and mark them optional",
        "Explain scope, shadowing, and why a pure function is easier to trust",
        "Pass a function to another function as a value",
    ],
    why="Functions are how you stop a program growing into an unreadable sheet of statements. Every abstraction you will ever build — modules, classes, components, APIs — is this idea repeated at a larger scale.",
    est_minutes=300,
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
_WEEKS.append(_week(
    6, 2, _M2,
    "Arrays",
    "Store lists of values and process them with loops and array methods.",
    """
An **array** is an ordered list, reached by index (`nums[0]` is the first). This
week: creating and indexing arrays, iterating them, and `map` / `filter` that
make list-processing concise.

To read a line of numbers into an array:

```ts
const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);
```

`.split(" ")` cuts the text at spaces; `.map(Number)` turns each piece into a number.
""",
    objectives=[
        "Create arrays and read elements by index",
        "Read a line of numbers into an array",
        "Loop over an array to sum or find a max",
        "Transform and filter with map and filter",
    ],
    why="Almost all real data is a list — rows, items, results. Arrays are how you hold and process them.",
    est_minutes=50,
    glossary=[
        _gloss("array", "An ordered list of values."),
        _gloss("index", "A position in an array, starting at 0."),
        _gloss(".split(sep)", "Cuts a string into an array of pieces."),
        _gloss(".map(f)", "Makes a new array by transforming each element."),
        _gloss(".filter(f)", "Keeps only the elements that pass a test."),
        _gloss(".join(sep)", "Glues an array back into a string."),
    ],
    cheatsheet="""
```ts
const a = [3, 5, 7];
a[0]         // 3   (index starts at 0)
a.length     // 3
"1 2 3".split(" ").map(Number)   // [1,2,3]
a.map((x) => x * 2)              // [6,10,14]
a.filter((x) => x > 4)           // [5,7]
a.join(" ")                       // "3 5 7"
```
""",
    self_check=[
        "Can you read numbers into an array and print the first one?",
        "Can you sum an array with a loop?",
        "Can you keep only the even numbers with filter?",
    ],
    review=[
        _q("The first element of an array is at index…", ["1", "0", "-1", "any"], 1,
           "Arrays are zero-indexed."),
        _q('`"3 5".split(" ")` gives…',
           ["35", '["3","5"]', '"3 5"', "error"], 1, "split cuts into pieces."),
        _q("`[1,2,3].filter((x)=>x>1).length` is…", ["1", "2", "3", "0"], 1,
           "Keeps 2 and 3 → length 2."),
    ],
    milestone="Budget Buddy can now crunch a whole month of expenses at once.",
    lessons=[
        _lesson(
            "w6-basics", "Creating & indexing",
            "Arrays and their indexes.",
            """
```ts
const names = ["Ada", "Bo", "Cy"];
names[0]      // Ada  (indexes start at 0)
names.length  // 3
```

> ⚠️ **Common mistakes:** expecting `a[1]` to be the first element (it's the
> *second*), and reading past the end (`a[a.length]` is `undefined`).
""",
            warmup=[
                _q('`const a = [10,20,30]; console.log(a[1]);` prints…',
                   ["10", "20", "30", "1"], 1, "Index 1 is the second element, 20."),
            ],
            exercises=[
                _ex("tscourse-w6-b-1", "First number",
                    "Read the numbers and print the first one.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconsole.log(nums[0]);\n',
                    'nums[0]', [("3 5 7", "3"), ("9", "9")],
                    hints=["The first element is at index 0."]),
                _ex("tscourse-w6-b-2", "How many",
                    "Print how many space-separated words the input has.",
                    _FS + 'const words = fs.readFileSync(0, "utf8").trim().split(" ");\nconsole.log(words.length);\n',
                    'words.length', [("a b c d", "4"), ("hi", "1")],
                    hints=["length gives the number of elements."]),
                _fix("tscourse-w6-b-fix", "Fix the index",
                     "This should print the FIRST number but prints the second. Fix it.",
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconsole.log(nums[1]);\n',
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconsole.log(nums[0]);\n',
                     [("3 5 7", "3")],
                     hints=["Index 1 is the second element.",
                            "The first element is index 0."]),
            ],
        ),
        _lesson(
            "w6-iterate", "Iterating & accumulating",
            "Walk an array with for...of.",
            """
Sum the array [1,2,3,4]:

| step | x | sum after |
|------|---|-----------|
| 1    | 1 | 1         |
| 2    | 2 | 3         |
| 3    | 3 | 6         |
| 4    | 4 | 10        |

```ts
let sum = 0;
for (const x of [1, 2, 3, 4]) sum = sum + x;
console.log(sum);   // 10
```
""",
            warmup=[
                _q("Summing [2,2,2] with a for...of accumulator gives…",
                   ["2", "6", "3", "222"], 1, "2+2+2 = 6."),
            ],
            exercises=[
                _ex("tscourse-w6-it-1", "Sum the list",
                    "Add every number and print the total.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nlet sum = 0;\nfor (const x of nums) {\n  sum = sum + x;\n}\nconsole.log(sum);\n',
                    'sum = sum + x;', [("1 2 3 4", "10"), ("5", "5")],
                    hints=["Add each x to the running sum."]),
                _ex("tscourse-w6-it-2", "Largest",
                    "Track and print the largest number in the list.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nlet best = nums[0];\nfor (const x of nums) {\n  if (x > best) {\n    best = x;\n  }\n}\nconsole.log(best);\n',
                    'x > best', [("3 9 2 7", "9"), ("4", "4")],
                    hints=["Replace best whenever x is bigger."]),
                _fix("tscourse-w6-it-fix", "Fix the sum start",
                     "This sum is always one too big. Fix it so sum(1 2 3)=6.",
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nlet sum = 1;\nfor (const x of nums) {\n  sum = sum + x;\n}\nconsole.log(sum);\n',
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nlet sum = 0;\nfor (const x of nums) {\n  sum = sum + x;\n}\nconsole.log(sum);\n',
                     [("1 2 3", "6")],
                     hints=["A running sum must start at 0, not 1."]),
            ],
        ),
        _lesson(
            "w6-methods", "map & filter",
            "Transform and select.",
            """
- `map` makes a new array by transforming each element.
- `filter` keeps only elements that pass a test.
- `join` glues an array into a string.

```ts
const nums = [1, 2, 3];
nums.map((x) => x * 2).join(" ")     // "2 4 6"
nums.filter((x) => x % 2 === 1).length // 2
```

> ⚠️ **Common mistakes:** forgetting `map`/`filter` return a NEW array (they
> don't change the original), and forgetting to `return`/produce a value in the callback.
""",
            warmup=[
                _q("`[1,2,3,4].filter((x)=>x%2===0)` is…",
                   ["[1,3]", "[2,4]", "[1,2,3,4]", "2"], 1, "Keeps the even numbers."),
            ],
            exercises=[
                _ex("tscourse-w6-m-1", "Count evens",
                    "Keep the even numbers and print how many there are.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconst evens = nums.filter((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                    'x % 2 === 0', [("1 2 3 4 5 6", "3"), ("1 3 5", "0")],
                    hints=["Even means remainder 0 mod 2."]),
                _ex("tscourse-w6-m-2", "Double them",
                    "Double every number and print them space-separated.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconst doubled = nums.map((x) => x * 2);\nconsole.log(doubled.join(" "));\n',
                    'x * 2', [("1 2 3", "2 4 6"), ("10", "20")],
                    hints=["map transforms each x to x * 2."]),
                _fix("tscourse-w6-m-fix", "Fix filter vs map",
                     "This should COUNT the evens, but it doubles instead. Fix it.",
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconst evens = nums.map((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconst evens = nums.filter((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                     [("1 2 3 4 5 6", "3")],
                     hints=["map keeps every element (so length never changes).",
                            "To keep only some elements, use filter."],
                     difficulty="Medium"),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #6 — month stats",
        """
Read a line of expense **amounts** and print three stats:

```
total 14
biggest 5
count 5
```

for input `3 1 4 1 5`.
""",
        _ch("tscourse-w6-capstone", "Budget Buddy #6", "Easy",
            "Compute total and the biggest in one pass, then print the report.",
            _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
            'let total = 0;\nlet biggest = nums[0];\nfor (const x of nums) {\n  total = total + x;\n  if (x > biggest) {\n    biggest = x;\n  }\n}\n'
            'console.log(`total ${total}`);\nconsole.log(`biggest ${biggest}`);\nconsole.log(`count ${nums.length}`);\n',
            'let total = 0;\nlet biggest = nums[0];\nfor (const x of nums) {\n  total = total + x;\n  if (x > biggest) {\n    biggest = x;\n  }\n}\n'
            'console.log(`total ${total}`);\nconsole.log(`biggest ${biggest}`);\nconsole.log(`count ${nums.length}`);',
            [("3 1 4 1 5", "total 14\nbiggest 5\ncount 5"), ("10", "total 10\nbiggest 10\ncount 1")],
            hints=["Start biggest at nums[0].",
                   "Update total and biggest together in one loop.",
                   "count is nums.length."]),
        example_io="total 14\nbiggest 5\ncount 5",
        rubric=["Prints total, biggest and count",
                "Computes total and biggest in a single loop",
                "biggest starts from the first element"],
        stretch=_ch("tscourse-w6-capstone-stretch", "Budget Buddy #6 (stretch)", "Medium",
                    "Also print `average <avg>` where avg = total / count (a decimal is fine).",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                    'let total = 0;\nfor (const x of nums) {\n  total = total + x;\n}\n'
                    'console.log(`total ${total}`);\nconsole.log(`count ${nums.length}`);\nconsole.log(`average ${total / nums.length}`);\n',
                    'let total = 0;\nfor (const x of nums) {\n  total = total + x;\n}\n'
                    'console.log(`total ${total}`);\nconsole.log(`count ${nums.length}`);\nconsole.log(`average ${total / nums.length}`);',
                    [("2 4 6", "total 12\ncount 3\naverage 4"), ("10", "total 10\ncount 1\naverage 10")],
                    hints=["average is total divided by the count.",
                           "Use total / nums.length."]),
    ),
))

# --- Week 7 ---------------------------------------------------------------
_WEEKS.append(_week(
    7, 2, _M2,
    "Objects",
    "Model structured data with objects, and combine them with arrays.",
    """
An **object** groups related values under named keys — perfect for a 'thing'
like an expense or a user. This week: object literals, reading and updating
properties, and arrays of objects (the shape of most real data).

```ts
const user = { name: "Ada", age: 36 };
user.name          // Ada
user.age = user.age + 1;
```
""",
    objectives=[
        "Create objects and read properties with dot access",
        "Update a property on an object",
        "Pass objects into functions",
        "Loop over an array of objects and reach into each one",
    ],
    why="Objects model the real world — a product, a user, an expense — as one tidy bundle of fields.",
    est_minutes=45,
    glossary=[
        _gloss("object", "A bundle of named values (keys) — { name: \"Ada\" }."),
        _gloss("property / key", "A named slot on an object."),
        _gloss("dot access", "Reaching a property: obj.name."),
        _gloss("array of objects", "A list where each item is an object — the shape of most data."),
    ],
    cheatsheet="""
```ts
const p = { name: "Ada", age: 36 };
p.name           // "Ada"
p.age = p.age + 1;  // update
const people = [{ name: "Ada", age: 36 }, { name: "Bo", age: 20 }];
for (const q of people) total = total + q.age;
people.filter((q) => q.age >= 21)
```
""",
    self_check=[
        "Can you read and update a property on an object?",
        "Can you write a function that takes an object and returns a field?",
        "Can you total a field across an array of objects?",
    ],
    review=[
        _q("How do you read the `name` of `user`?",
           ["user[name]", "user->name", "user.name", "name(user)"], 2,
           "Dot notation: user.name."),
        _q("An object is best for…",
           ["an ordered list", "grouping related values under keys",
            "repeating an action", "comparing numbers"], 1,
           "Objects bundle related fields."),
        _q("`[{a:1},{a:2}].filter((o)=>o.a>1).length` is…",
           ["0", "1", "2", "error"], 1, "Only {a:2} passes."),
    ],
    milestone="Budget Buddy now models each expense as a proper record.",
    lessons=[
        _lesson(
            "w7-basics", "Object basics",
            "Keys, values, and dot access.",
            """
```ts
const point = { x: 3, y: 4 };
point.x            // 3
point.y = point.y + 1;   // 5
```

> ⚠️ **Common mistakes:** using `[]` with a bare word (`obj[name]` looks up a
> *variable* name); for a known key, use dot access `obj.name`.
""",
            warmup=[
                _q("`const u = { age: 5 }; console.log(u.age);` prints…",
                   ["age", "5", "u.age", "undefined"], 1, "It reads the property value 5."),
            ],
            exercises=[
                _ex("tscourse-w7-b-1", "Read a property", "Print the user's name.",
                    'const user = { name: "Ada", age: 36 };\nconsole.log(user.name);\n',
                    'user.name', [("", "Ada")],
                    hints=["Access it with user.name."]),
                _ex("tscourse-w7-b-2", "Update a property",
                    "Add 5 to counter.value, then print it.",
                    'const counter = { value: 0 };\ncounter.value = counter.value + 5;\nconsole.log(counter.value);\n',
                    'counter.value + 5', [("", "5")],
                    hints=["Read the current value and add 5."]),
                _fix("tscourse-w7-b-fix", "Fix the property name",
                     "This should print the name but prints undefined. Fix the property.",
                     'const user = { name: "Ada", age: 36 };\nconsole.log(user.username);\n',
                     'const user = { name: "Ada", age: 36 };\nconsole.log(user.name);\n',
                     [("", "Ada")],
                     hints=["There is no `username` key on this object.",
                            "The key is `name`."]),
            ],
        ),
        _lesson(
            "w7-funcs", "Objects & functions",
            "Passing objects around.",
            """
Functions can take and return objects.

```ts
function fullName(p: { first: string; last: string }): string {
  return `${p.first} ${p.last}`;
}
fullName({ first: "Ada", last: "Lovelace" });   // Ada Lovelace
```
""",
            warmup=[
                _q("`fullName({first:\"A\", last:\"B\"})` above returns…",
                   ["A", "B", "A B", "AB"], 2, "Template joins them with a space."),
            ],
            exercises=[
                _ex("tscourse-w7-f-1", "Full name",
                    "Return the first and last name joined by a space.",
                    'function fullName(p: { first: string; last: string }): string {\n  return `${p.first} ${p.last}`;\n}\nconsole.log(fullName({ first: "Ada", last: "Lovelace" }));\n',
                    '`${p.first} ${p.last}`', [("", "Ada Lovelace")],
                    hints=["Template literal with p.first and p.last."]),
                _ex("tscourse-w7-f-2", "Build from input",
                    "Store a greeting on the object, then print it.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\nconst user = { name: name, greeting: `Hi ${name}` };\nconsole.log(user.greeting);\n',
                    '`Hi ${name}`', [("Sam", "Hi Sam"), ("Ada", "Hi Ada")],
                    hints=["The greeting is a template literal using name."]),
                _fix("tscourse-w7-f-fix", "Fix the field access",
                     "This should print the first name but reads the wrong field. Fix it.",
                     'function first(p: { first: string; last: string }): string {\n  return p.last;\n}\nconsole.log(first({ first: "Ada", last: "Lovelace" }));\n',
                     'function first(p: { first: string; last: string }): string {\n  return p.first;\n}\nconsole.log(first({ first: "Ada", last: "Lovelace" }));\n',
                     [("", "Ada")],
                     hints=["It returns p.last but should return the first name.",
                            "Return p.first."]),
            ],
        ),
        _lesson(
            "w7-arrays", "Arrays of objects",
            "The shape of real datasets.",
            """
Most data is a list of records. Loop over it and reach into each one.

```ts
const people = [{ name: "Ada", age: 36 }, { name: "Bo", age: 20 }];
let total = 0;
for (const p of people) total = total + p.age;
console.log(total);   // 56
```
""",
            warmup=[
                _q("Totalling `age` over [{age:1},{age:2},{age:3}] gives…",
                   ["3", "6", "123", "error"], 1, "1+2+3 = 6."),
            ],
            exercises=[
                _ex("tscourse-w7-a-1", "Total ages",
                    "Sum everyone's age and print it.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\nlet total = 0;\nfor (const p of people) {\n  total = total + p.age;\n}\nconsole.log(total);\n',
                    'total + p.age', [("", "56")],
                    hints=["Add each person's age to total."]),
                _ex("tscourse-w7-a-2", "Count adults",
                    "Count people aged 21 or older and print the count.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\nconst adults = people.filter((p) => p.age >= 21);\nconsole.log(adults.length);\n',
                    'p.age >= 21', [("", "1")],
                    hints=["Keep people whose age is at least 21."]),
                _fix("tscourse-w7-a-fix", "Fix the field in the loop",
                     "This should total ages but totals nothing sensible. Fix the field it reads.",
                     'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\nlet total = 0;\nfor (const p of people) {\n  total = total + p.years;\n}\nconsole.log(total);\n',
                     'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\nlet total = 0;\nfor (const p of people) {\n  total = total + p.age;\n}\nconsole.log(total);\n',
                     [("", "56")],
                     hints=["There is no `years` field — it's `age`.",
                            "Read p.age."]),
            ],
        ),
    ],
    capstone=_cap_brief(
        "Budget Buddy #7 — model your expenses (free build)",
        """
A **free-build** project — no auto-grader. In the editor, model Budget Buddy's data:

1. Represent each expense as an object with `desc`, `amount`, and `paid` (a boolean).
2. Put several expenses in an array.
3. Write a function that takes the array and prints a report: the number of
   expenses, the total amount, and the descriptions of the unpaid ones.

Use everything from Weeks 1–7: variables, loops, functions, arrays, objects.
When you're happy with the output, click **Mark done**. A reference solution is
below if you want to compare.
""",
        reference="""
const expenses = [
  { desc: "coffee", amount: 3, paid: true },
  { desc: "book", amount: 12, paid: false },
  { desc: "lunch", amount: 9, paid: false },
];
function report(items) {
  let total = 0;
  for (const e of items) total = total + e.amount;
  console.log(`Expenses: ${items.length}`);
  console.log(`Total: $${total}`);
  const unpaid = items.filter((e) => !e.paid).map((e) => e.desc);
  console.log(`Unpaid: ${unpaid.join(", ")}`);
}
report(expenses);
""",
        rubric=["Each expense is an object with desc, amount, paid",
                "A function takes the array and prints a report",
                "The report includes the count, the total, and the unpaid descriptions"],
    ),
))

# --- Week 8 ---------------------------------------------------------------
_WEEKS.append(_week(
    8, 2, _M2,
    "Types that Describe Your Data",
    "Annotate values and name shapes with type aliases and interfaces.",
    """
You've used TypeScript's types implicitly all along. This week you make them
explicit: **annotations** on values and functions, and naming reusable shapes
with **`interface`** and **`type`**. Well-named types are documentation the
compiler checks for you.

Types are erased before the program runs, so the drills still exercise runtime
logic — the annotations describe it.
""",
    objectives=[
        "Write type annotations on values and functions",
        "Name a shape with interface or type",
        "Annotate an array of records (Item[])",
        "Fold a list to one value with reduce",
    ],
    why="Types catch whole classes of bugs before the program ever runs — the reason TypeScript exists.",
    est_minutes=50,
    glossary=[
        _gloss("annotation", "A written type after a colon: let n: number."),
        _gloss("inference", "TypeScript working out a type for you."),
        _gloss("interface", "A name for the shape of an object type."),
        _gloss("type alias", "Another way to name a type: type User = {...}."),
        _gloss(".reduce(f, start)", "Folds a list into a single accumulated value."),
    ],
    cheatsheet="""
```ts
const price: number = 10;
function repeat(s: string, n: number): string { return s.repeat(n); }
interface Point { x: number; y: number; }
type User = { name: string; admin: boolean };
const items: Item[] = [...];
items.reduce((sum, it) => sum + it.price, 0)   // fold to one number
```
""",
    self_check=[
        "Can you annotate a function's parameters and return type?",
        "Can you name an object shape with interface and use it?",
        "Can you total a field over a typed array with reduce?",
    ],
    review=[
        _q("What happens to type annotations at runtime?",
           ["they slow it down", "they're erased (compile-time only)",
            "they become comments", "they print"], 1,
           "Types guide you and the compiler, then vanish before running."),
        _q("`interface` names…",
           ["a running object", "the shape of an object type", "a loop", "an input"], 1,
           "It names a reusable object shape."),
        _q("`[1,2,3].reduce((s,x)=>s+x, 0)` is…", ["0", "6", "123", "3"], 1,
           "It folds to the sum, 6."),
    ],
    milestone="Budget Buddy is now fully typed — the compiler guards its data. You've finished Month 2!",
    lessons=[
        _lesson(
            "w8-annotations", "Annotations & inference",
            "Writing types on values and functions.",
            """
```ts
const price: number = 10;
function repeat(s: string, n: number): string {
  return s.repeat(n);
}
```

Often you can omit annotations and let TypeScript **infer** them — but writing
them on function parameters and returns is good practice.

> ⚠️ **Common mistakes:** thinking annotations change runtime behaviour — they
> don't; they're checked, then stripped.
""",
            warmup=[
                _q('`"ab".repeat(3)` is…', ["ababab", "ab3", "6", "aaabbb"], 0,
                   "repeat concatenates 3 copies."),
            ],
            exercises=[
                _ex("tscourse-w8-an-1", "Typed total",
                    "Compute price * qty into the annotated total.",
                    'const price: number = 10;\nconst qty: number = 3;\nconst total: number = price * qty;\nconsole.log(total);\n',
                    'price * qty', [("", "30")],
                    hints=["Multiply the two annotated numbers."]),
                _ex("tscourse-w8-an-2", "Typed repeat",
                    "Return the string repeated n times.",
                    'function repeat(s: string, n: number): string {\n  return s.repeat(n);\n}\nconsole.log(repeat("ab", 3));\n',
                    's.repeat(n)', [("", "ababab")],
                    hints=["Strings have a .repeat(n) method."]),
                _fix("tscourse-w8-an-fix", "Fix the annotation mismatch",
                     "This should print 30, but a wrong operator sneaks in. Fix it.",
                     'const price: number = 10;\nconst qty: number = 3;\nconst total: number = price + qty;\nconsole.log(total);\n',
                     'const price: number = 10;\nconst qty: number = 3;\nconst total: number = price * qty;\nconsole.log(total);\n',
                     [("", "30")],
                     hints=["price + qty is 13, not 30.",
                            "A total of items uses multiplication."]),
            ],
        ),
        _lesson(
            "w8-interfaces", "Interfaces & type aliases",
            "Naming the shape of your data.",
            """
Name a shape once, use it everywhere:

```ts
interface Point { x: number; y: number; }
type User = { name: string; admin: boolean };

function dist(p: Point): number {
  return Math.abs(p.x) + Math.abs(p.y);
}
```

`Math.abs(n)` is the distance of n from zero.
""",
            warmup=[
                _q("`Math.abs(-4)` is…", ["-4", "4", "0", "error"], 1,
                   "abs gives the magnitude, 4."),
            ],
            exercises=[
                _ex("tscourse-w8-if-1", "Manhattan distance",
                    "Return |p.x| + |p.y| using Math.abs.",
                    'interface Point {\n  x: number;\n  y: number;\n}\nfunction dist(p: Point): number {\n  return Math.abs(p.x) + Math.abs(p.y);\n}\nconsole.log(dist({ x: 3, y: -4 }));\n',
                    'Math.abs(p.x) + Math.abs(p.y)', [("", "7")],
                    hints=["Add the absolute values of x and y."]),
                _ex("tscourse-w8-if-2", "Labelled user",
                    "Return `<name> (admin)` when admin is true, else just the name.",
                    'type User = { name: string; admin: boolean };\nfunction label(u: User): string {\n  return u.admin ? `${u.name} (admin)` : u.name;\n}\nconsole.log(label({ name: "Ada", admin: true }));\n',
                    'u.admin ? `${u.name} (admin)` : u.name', [("", "Ada (admin)")],
                    hints=["A ternary cond ? a : b picks a when cond is true."]),
                _fix("tscourse-w8-if-fix", "Fix the distance",
                     "Negative coordinates break this. Fix it so dist({x:3,y:-4}) is 7.",
                     'interface Point {\n  x: number;\n  y: number;\n}\nfunction dist(p: Point): number {\n  return p.x + p.y;\n}\nconsole.log(dist({ x: 3, y: -4 }));\n',
                     'interface Point {\n  x: number;\n  y: number;\n}\nfunction dist(p: Point): number {\n  return Math.abs(p.x) + Math.abs(p.y);\n}\nconsole.log(dist({ x: 3, y: -4 }));\n',
                     [("", "7")],
                     hints=["3 + (-4) is -1, not a distance.",
                            "Wrap each coordinate in Math.abs."]),
            ],
        ),
        _lesson(
            "w8-typed-arrays", "Typed arrays & reduce",
            "Interfaces over lists, folded with reduce.",
            """
Annotate an array of records with `Item[]`, and fold it with `reduce`:

```ts
interface Item { name: string; price: number; }
const items: Item[] = [{ name: "A", price: 4 }, { name: "B", price: 6 }];
const total = items.reduce((sum, it) => sum + it.price, 0);   // 10
```

`reduce` carries an accumulator (`sum`, starting at 0) across the list.
""",
            warmup=[
                _q("`[2,3,5].reduce((s,x)=>s+x, 0)` is…", ["0", "10", "235", "3"], 1,
                   "Folds to the sum, 10."),
            ],
            exercises=[
                _ex("tscourse-w8-ta-1", "Total price",
                    "Reduce the items to the sum of their prices.",
                    'interface Item {\n  name: string;\n  price: number;\n}\nconst items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\nconst total = items.reduce((sum, it) => sum + it.price, 0);\nconsole.log(total);\n',
                    'sum + it.price', [("", "10")],
                    hints=["Each step adds it.price to the running sum."]),
                _fix("tscourse-w8-ta-fix", "Fix the reduce start",
                     "The total is one too high — the seed is wrong. Fix it to 10.",
                     'interface Item {\n  name: string;\n  price: number;\n}\nconst items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\nconst total = items.reduce((sum, it) => sum + it.price, 1);\nconsole.log(total);\n',
                     'interface Item {\n  name: string;\n  price: number;\n}\nconst items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\nconst total = items.reduce((sum, it) => sum + it.price, 0);\nconsole.log(total);\n',
                     [("", "10")],
                     hints=["The reduce seed (last argument) starts the sum.",
                            "A sum should seed at 0, not 1."]),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #8 — typed report",
        """
Bring it home: model expenses with an `interface`, then report on them. Given
three expenses, print:

```
Count: 3
Total: $24
Unpaid: book, lunch
```
""",
        _ch("tscourse-w8-capstone", "Budget Buddy #8", "Medium",
            "Use filter, map, join, reduce and .length over a typed array of records.",
            'interface Expense {\n  desc: string;\n  amount: number;\n  paid: boolean;\n}\n'
            'const expenses: Expense[] = [\n  { desc: "coffee", amount: 3, paid: true },\n  { desc: "book", amount: 12, paid: false },\n  { desc: "lunch", amount: 9, paid: false },\n];\n'
            'const total = expenses.reduce((sum, e) => sum + e.amount, 0);\n'
            'const unpaid = expenses.filter((e) => !e.paid).map((e) => e.desc);\n'
            'console.log(`Count: ${expenses.length}`);\nconsole.log(`Total: $${total}`);\nconsole.log(`Unpaid: ${unpaid.join(", ")}`);\n',
            'const total = expenses.reduce((sum, e) => sum + e.amount, 0);\n'
            'const unpaid = expenses.filter((e) => !e.paid).map((e) => e.desc);\n'
            'console.log(`Count: ${expenses.length}`);\nconsole.log(`Total: $${total}`);\nconsole.log(`Unpaid: ${unpaid.join(", ")}`);',
            [("", "Count: 3\nTotal: $24\nUnpaid: book, lunch")],
            hints=["reduce sums the amounts (seed 0).",
                   "Filter to unpaid, then map to descriptions.",
                   'Join the unpaid descriptions with ", ".']),
        example_io="Count: 3\nTotal: $24\nUnpaid: book, lunch",
        rubric=["expenses is typed as Expense[]",
                "Total uses reduce; count uses .length",
                "Unpaid list uses filter + map + join"],
    ),
))

# ===========================================================================
# MONTHS 3-8 — themed skeletons (authored in later batches).
# ===========================================================================
_M3 = "The Type System, Properly"
_WEEKS += [
    _skel(9, 3, _M3, "Unions & Narrowing",
          "Model a value that's 'one of several' and narrow it safely before use."),
    _skel(10, 3, _M3, "Generics",
          "Write functions and types that work over any type without losing safety."),
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
    (".reduce(", 8),                        # reduce
    ("interface ", 8), ("type ", 8),        # named types (annotations OK earlier)
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
        "Each foundation week is around five hours of study across six or seven "
        "lessons, with a goal, warm-ups that make you predict the output, "
        "fill-in-the-blank drills, fix-the-bug programs, hint ladders, a "
        "glossary, a cheat sheet, and a growing capstone project (Budget Buddy). "
        "Nothing ever requires syntax a later week hasn't taught yet."
    ),
    "weeks": _WEEKS,
}
