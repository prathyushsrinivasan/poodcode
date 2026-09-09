# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 1 practice — values, variables & output.
#
# exec()'d by tools/typescript_course.py; fills `_PRACTICE[1]`.
#
# Three families, five variants each. A family drills ONE motion and twists a
# single dimension at a time, so the second variant is never a cold start — it
# is the first one with one thing moved. That is the whole design: not fifteen
# unrelated puzzles, but three motions you stop having to think about.
#
# WEEK 1 SCOPE — deliberately tiny, and the scope linter only catches the tokens
# it knows about, so this list is the real guard. Available: `const`/`let`,
# annotations, arithmetic, template literals, string concatenation, escapes,
# `Number()`, `String()`, `typeof`, `.toFixed()`, `Math.floor()`, `.repeat()`.
# NOT available: stdin (week 2), any other string method (week 2), `if` (week
# 3), loops (week 4), functions (week 5), arrays (week 6), objects (week 7).
#
# Every variant therefore hard-codes its inputs and prints — exactly like the
# lesson exercises for this week, whose tests all take empty stdin.
# ---------------------------------------------------------------------------


def _p1(eid, title, prompt, full, blank, out, hints, difficulty="Intro"):
    """One week-1 practice variant. Input is always empty; `out` is the whole
    expected stdout."""
    return _ch(eid, title, difficulty, prompt, full, blank, [("", out)], hints)


# --- Family A — compute one value, report one line -------------------------

_P1_A = _fam(
    "p1-report", "Compute, then report",
    "Name the inputs, compute one value, print one templated line.",
    """
This is the shape of nearly every small program you will write this month, and
of the week's capstone:

```ts
const price = 3;          // 1. name the inputs
const qty = 4;
const total = price * qty;   // 2. compute the one value you care about
console.log(`Total: ${total}`);   // 3. report it
```

Naming the computed value on its own line is the habit worth building. You
*could* write `${price * qty}` directly inside the template, and for one value
that is fine — but the moment there are two, the named version is the one you
can still read.

Each variant below changes exactly one thing: the arithmetic, then how the
number is formatted, then how many inputs feed it.
""",
    [
        _p1("tsp-w1-a1", "Quantity times price",
            "Print `4 x 3 = 12` — the quantity, the price, and their product.",
            'const price = 3;\nconst qty = 4;\n'
            'console.log(`${qty} x ${price} = ${price * qty}`);\n',
            '`${qty} x ${price} = ${price * qty}`', "4 x 3 = 12",
            ["A template literal goes in backticks, with `${...}` around each value.",
             "The last slot holds the arithmetic itself."]),
        _p1("tsp-w1-a2", "Add the tax",
            "A subtotal of 10 with tax at 0.1 comes to 11. Print `Total: 11.00`.",
            'const subtotal = 10;\nconst rate = 0.1;\n'
            'const total = subtotal + subtotal * rate;\n'
            'console.log(`Total: ${total.toFixed(2)}`);\n',
            'subtotal + subtotal * rate', "Total: 11.00",
            ["The tax is a fraction OF the subtotal, so multiply first and add.",
             "`*` happens before `+`, so no brackets are needed.",
             "Write subtotal + subtotal * rate."],
            difficulty="Easy"),
        _p1("tsp-w1-a3", "Change from a note",
            "Spend 12.50 out of a 20 budget. Print `Change: 7.50`.",
            'const budget = 20;\nconst spent = 12.5;\n'
            'const change = budget - spent;\n'
            'console.log(`Change: ${change.toFixed(2)}`);\n',
            'budget - spent', "Change: 7.50",
            ["Subtraction, in the order that leaves a positive number.",
             "Write budget - spent."]),
        _p1("tsp-w1-a4", "The average of two",
            "Average 7 and 10, printed to two decimals: `Average: 8.50`.",
            'const first = 7;\nconst second = 10;\n'
            'const average = (first + second) / 2;\n'
            'console.log(`Average: ${average.toFixed(2)}`);\n',
            '(first + second) / 2', "Average: 8.50",
            ["Add them, then halve — and the brackets matter.",
             "Without brackets, `first + second / 2` halves only the second.",
             "Write (first + second) / 2."],
            difficulty="Easy"),
        _p1("tsp-w1-a5", "As a percentage",
            "18 marks out of 24 is 75%. Print `Score: 75%`.",
            'const got = 18;\nconst outOf = 24;\n'
            'const percent = (got / outOf) * 100;\n'
            'console.log(`Score: ${percent}%`);\n',
            '(got / outOf) * 100', "Score: 75%",
            ["A fraction of the total, scaled up to a hundred.",
             "Divide first, then multiply by 100.",
             "Write (got / outOf) * 100."],
            difficulty="Easy"),
    ],
)


# --- Family B — money, to the penny ----------------------------------------

_P1_B = _fam(
    "p1-money", "Money, to the penny",
    "`.toFixed(2)` — and the reason it is not optional.",
    """
`.toFixed(2)` turns a number into a **string** with exactly two decimals:

```ts
const price = 3.5;
console.log(price.toFixed(2));   // 3.50   <- a string, not a number
```

You need it because money and binary fractions disagree. A computer stores
`0.1` the way you'd store `1/3` in decimal — close, but not exact — so sums
that look obvious come out slightly wrong:

```ts
console.log(0.1 + 0.2);              // 0.30000000000000004
console.log((0.1 + 0.2).toFixed(2)); // 0.30
```

That is not a bug in TypeScript; every language using binary floating point
does it. The habit is simply: **compute in numbers, print through `toFixed`.**

Note the brackets in the second line. `0.1 + 0.2.toFixed(2)` would apply the
method to `0.2` alone, because a method binds tighter than `+`.
""",
    [
        _p1("tsp-w1-b1", "A third of a pound",
            "Print one third, to two decimals: `0.33`.",
            'const share = 1 / 3;\nconsole.log(share.toFixed(2));\n',
            'share.toFixed(2)', "0.33",
            ["Call the method on the number you want formatted.",
             "Write share.toFixed(2)."]),
        _p1("tsp-w1-b2", "Round up to the pound",
            "A price of 19.999 should print as `20.00`.",
            'const price = 19.999;\nconsole.log(price.toFixed(2));\n',
            'price.toFixed(2)', "20.00",
            ["toFixed rounds; it does not merely chop.",
             "Write price.toFixed(2)."]),
        _p1("tsp-w1-b3", "The classic floating-point sum",
            "`0.1 + 0.2` does not print what you expect. Print it as `0.30`.",
            'const a = 0.1;\nconst b = 0.2;\n'
            'console.log((a + b).toFixed(2));\n',
            '(a + b).toFixed(2)', "0.30",
            ["Add first, format second — so the addition needs brackets.",
             "Without them the method would apply to `b` alone.",
             "Write (a + b).toFixed(2)."],
            difficulty="Easy"),
        _p1("tsp-w1-b4", "Price per item",
            "13 split across 4 items is 3.25 each. Print `Each: 3.25`.",
            'const total = 13;\nconst qty = 4;\n'
            'const each = total / qty;\n'
            'console.log(`Each: ${each.toFixed(2)}`);\n',
            'total / qty', "Each: 3.25",
            ["The total shared between the items.",
             "Write total / qty."]),
        _p1("tsp-w1-b5", "A two-line receipt",
            "Print the subtotal and the total after a 2.00 delivery fee:\n"
            "`Subtotal: 8.50` then `Total:    10.50`.",
            'const subtotal = 8.5;\nconst fee = 2;\n'
            'console.log(`Subtotal: ${subtotal.toFixed(2)}`);\n'
            'console.log(`Total:    ${(subtotal + fee).toFixed(2)}`);\n',
            'console.log(`Total:    ${(subtotal + fee).toFixed(2)}`);',
            "Subtotal: 8.50\nTotal:    10.50",
            ["A second console.log prints a second line.",
             "The alignment is just spaces typed inside the backticks.",
             "Add the fee inside brackets, then format the result."],
            difficulty="Easy"),
    ],
)


# --- Family C — convert on purpose -----------------------------------------

_P1_C = _fam(
    "p1-convert", "Convert on purpose",
    "`Number(...)` and `String(...)`, and choosing which one you meant.",
    """
`+` has two jobs, and it picks by looking at its operands:

```ts
console.log(3 + 4);       // 7    two numbers  -> addition
console.log("3" + 4);     // 34   a string     -> joining
```

So text that *looks* numeric will silently join instead of adding. The fix is
never to hope — it is to convert on purpose, **before** the operator runs:

```ts
Number("3") + 4     // 7     say "treat this as a number"
String(3) + "4"     // "34"  say "treat this as text"
```

`Number(...)` on something that isn't a number gives `NaN` ("not a number") —
which is itself of type `number`, a wrinkle week 2 comes back to.

Each variant asks which conversion you meant. Getting it backwards is the most
common beginner bug in the language, so it is worth the reps.
""",
    [
        _p1("tsp-w1-c1", "Add, don't join",
            "`raw` holds the text `12`. Print the sum with 8 — that is 20, not 128.",
            'const raw = "12";\nconsole.log(Number(raw) + 8);\n',
            'Number(raw) + 8', "20",
            ["As it stands, + would join the two into text.",
             "Convert raw first: Number(raw) + 8."]),
        _p1("tsp-w1-c2", "Join, don't add",
            "`n` holds the number 7. Print `7!`.",
            'const n = 7;\nconsole.log(String(n) + "!");\n',
            'String(n) + "!"', "7!",
            ["String(...) turns a number into text.",
             'Write String(n) + "!".']),
        _p1("tsp-w1-c3", "Convert, then double",
            "`raw` holds the text `3.5`. Print it doubled: `7`.",
            'const raw = "3.5";\nconsole.log(Number(raw) * 2);\n',
            'Number(raw) * 2', "7",
            ["Number() handles decimals, not just whole numbers.",
             "Write Number(raw) * 2."]),
        _p1("tsp-w1-c4", "Name the type",
            "Print the type of `v`, which holds the text `42`. It should print `string`.",
            'const v = "42";\nconsole.log(typeof v);\n',
            'typeof v', "string",
            ["typeof reports a value's type as a word.",
             "The quotes are what make it text, however numeric it looks."]),
        _p1("tsp-w1-c5", "Two texts, one sum",
            "Both values arrived as text. Print their sum: `15`.",
            'const a = "10";\nconst b = "5";\n'
            'console.log(Number(a) + Number(b));\n',
            'Number(a) + Number(b)', "15",
            ["Either side being text is enough to make + join instead of add.",
             'Leaving one unconverted would print "105".',
             "Convert both: Number(a) + Number(b)."],
            difficulty="Easy"),
    ],
)


_PRACTICE[1] = [_P1_A, _P1_B, _P1_C]
