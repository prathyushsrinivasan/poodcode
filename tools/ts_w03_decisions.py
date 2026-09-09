# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 3 — making decisions.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

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
                # The buggy half must CRASH on empty input, not merely be in the
                # wrong order: `s[0] === "a"` on an empty string is a harmless
                # `undefined === "a"`, so both orders printed false and there was
                # nothing to fix. Calling a method on the missing character is
                # what makes the guard load-bearing.
                _fix("tscourse-w3-log-fix2", "Fix the unguarded index",
                     "Empty input should print false, but this crashes: it calls a method on a character that isn't there. Reorder the test so the length check protects it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s[0].toUpperCase() === "A" && s.length > 0);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length > 0 && s[0].toUpperCase() === "A");\n',
                     [("apple", "true"), ("", "false"), ("bat", "false")],
                     hints=["&& evaluates left to right and stops at the first false.",
                            "On empty input the left side runs first and there is no s[0] to uppercase.",
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
