# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 11 — Division, and the arithmetic that can fail.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 10's program.
#
# THE DECISION: a language whose arithmetic leaks `Infinity` and `NaN` is a
# language whose errors surface three steps from their cause. So:
#
#   * `x / 0` is `error: division by zero` — checked BEFORE dividing, so `0 / 0`
#     gets the same honest message rather than a NaN.
#   * any number that is not finite — a result that overflowed, or a literal
#     too long for a double — is `error: number too large`.
#
# `Number.isFinite(` is gated here. The literal case is real: the scanner hands
# `Number("999…9")` (400 digits) to the parser, which produces Infinity, and
# nothing noticed until now.
#
# EVALUATION BECOMES FALLIBLE, so `evaluate` returns an `EvalResult` (the third
# result union, sharing `Failure`) and every recursive call gets module 6's
# pass-it-up line. Graded consequence: operand ORDER now decides which error is
# reported (`calc-m11-fallible-fix1`), where in module 9 it decided nothing.
#
# A SECOND GRADED CONSEQUENCE is the silent one: `${evaluate(...)}` still
# compiles, because a template literal accepts anything — and prints
# `[object Object]`. The compiler protects `.value` but not string conversion;
# the module says so plainly.
# ---------------------------------------------------------------------------

_C11_RESULT = """type EvalResult = { ok: true; value: number } | Failure;

function checked(value: number): EvalResult {
  if (!Number.isFinite(value)) {
    return { ok: false, error: "error: number too large" };
  }
  return { ok: true, value: value };
}
"""

_C11_EVAL = """function evaluate(e: Expr): EvalResult {
  switch (e.kind) {
    case "num":
      return checked(e.value);
    case "neg": {
      const operand = evaluate(e.operand);
      if (!operand.ok) {
        return operand;
      }
      return { ok: true, value: -operand.value };
    }
    case "binary": {
      const left = evaluate(e.left);
      if (!left.ok) {
        return left;
      }
      const right = evaluate(e.right);
      if (!right.ok) {
        return right;
      }
      return arithmetic(e.op, left.value, right.value);
    }
    default: {
      const impossible: never = e;
      return impossible;
    }
  }
}
"""

_C11_ARITH = """function arithmetic(op: Op, left: number, right: number): EvalResult {
  switch (op) {
    case "+":
      return checked(left + right);
    case "-":
      return checked(left - right);
    case "*":
      return checked(left * right);
    case "/":
      if (right === 0) {
        return { ok: false, error: "error: division by zero" };
      }
      return checked(left / right);
    default: {
      const impossible: never = op;
      return impossible;
    }
  }
}
"""

_C11_RUN = """function run(src: string): string {
  const scanned = scan(src);
  if (!scanned.ok) {
    return scanned.error;
  }
  const parsed = parse(scanned.tokens);
  if (!parsed.ok) {
    return parsed.error;
  }
  const result = evaluate(parsed.expr);
  if (!result.ok) {
    return result.error;
  }
  return `${result.value}`;
}

console.log(run(readFileSync(0, "utf8").trimEnd()));
"""


def _c11(result=_C11_RESULT, evaluate=_C11_EVAL, arith=_C11_ARITH, run=_C11_RUN):
    return _stdin(_cjoin(_C8_TOKENS, _C6_RESULTS, _C4_UNEXPECTED, _C8_SCAN, _C9_TREE,
                         _C6_STATE, _C10_DESCRIBE, _C8_PRIMARY, _C8_UNARY, _C8_PRODUCT,
                         _C7_SUM, _C8_PARSE, result, evaluate, arith, run))


_C11_FULL = _c11()

_C11_HUGE = "9" * 400                               # Number() of this is Infinity
_C11_BIG = "1" + "0" * 300                          # 1e300: finite
_C11_INPUTS = ["1 / 0", "0 / 0", "-1 / 0", "7 / (3 - 3)", "1 / 0 - 1 / 0",
               "10 / 4", "(1 - 1) / 5", "1 / 3", "1 + 2 * 3", "(1 + 2) * -3",
               _C11_HUGE, _C11_BIG + " * 10000000000",
               "0 - " + _C11_BIG + " * 10000000000", _C11_BIG + " / 10",
               "1 +", "1 $ 2"]
_C11_TESTS = _ctests(11, _C11_INPUTS)

# --- Step 1's plain program: what `checked` says ---------------------------
_C11_S1_MAIN = """function report(r: EvalResult): string {
  if (r.ok) {
    return `${r.value}`;
  }
  return r.error;
}

console.log(report(checked(7)));
console.log(report(checked(2.5)));
console.log(report(checked(1e308 * 10)));
console.log(report(checked(-1e308 * 10)));
console.log(report(checked(1e308)));
"""
_C11_S1_OUT = "7\n2.5\nerror: number too large\nerror: number too large\n" + _jsnum(1e308)


def _c11_s1(result=_C11_RESULT):
    return _plain(_cjoin("type Failure = { ok: false; error: string };\n", result, _C11_S1_MAIN))


_C11_WHY = (
    "`echo '1 / 0' | node calc.ts` prints `Infinity`, and `0 / 0` prints `NaN`. "
    "Nobody decided that — JavaScript did, and the calculator passed it on. It "
    "matters because those values do not stay put: `Infinity - Infinity` is `NaN`, "
    "`NaN` compared to anything is false, and by the time a user sees the word "
    "`NaN` it is three operations away from the zero that caused it. A language "
    "has to decide what its arithmetic means at the edges, say so, and enforce "
    "it. This module makes that decision — and finds out that evaluation, which "
    "could not fail in module 9, now can."
)

_C11_BRIEF = """
### The whole module in one line

`1 / 0` is `error: division by zero`, and no expression can ever produce
`Infinity` or `NaN` — because evaluation now returns a result that can fail.

### What JavaScript decided for you

| Expression | JavaScript says | Why that is a problem here |
|---|---|---|
| `1 / 0` | `Infinity` | a word for a thing the user did not mean |
| `-1 / 0` | `-Infinity` | the same, with a sign |
| `0 / 0` | `NaN` | "not a number", from a program made of numbers |
| `1e308 * 10` | `Infinity` | too big for a double — silently |
| `Infinity - Infinity` | `NaN` | and now the cause is two steps away |

These are sensible defaults for JavaScript, which is used for a million things.
They are bad defaults for a calculator, whose user would rather be told.

### The decision

1. **Dividing by zero is an error**: `error: division by zero`. Checked *before*
   dividing, so `0 / 0` gets the same message — there is no `NaN` to explain.
2. **A number too big to represent is an error**: `error: number too large`.
   That covers a result that overflowed and a literal with four hundred digits.

The rule underneath both: **every value the evaluator produces is finite.** One
function, `checked`, enforces it, and every arithmetic result goes through it.

### Evaluation can fail now

In module 9 `evaluate` returned a `number`, because nothing could go wrong. Now
something can, so it returns a third result union:

```ts
type EvalResult = { ok: true; value: number } | Failure;
```

and every recursive call passes a failure up — the same line the parser has used
since module 6. It is more code. It is also the reason `1 / 0 + 5` reports the
division, rather than reporting nothing and printing a number.
"""

_C11_SYNTAX = [
    _syn(
        "if (!Number.isFinite(value)) { … }",
        "`Number.isFinite(x)` is true for every ordinary number and false for "
        "`Infinity`, `-Infinity` and `NaN` — all three bad values in one test.",
        """
Number.isFinite(2.5);          // true
Number.isFinite(1 / 0);        // false
Number.isFinite(0 / 0);        // false  (NaN)
Number.isFinite(1e308 * 10);   // false  (overflow)
""",
        "Not the same as the global `isFinite`, which converts its argument first "
        "— `isFinite(\"7\")` is true. `Number.isFinite` never converts.",
    ),
    _syn(
        "type EvalResult = { ok: true; value: number } | Failure;",
        "The evaluator's result: a number, or a reason. The third result union, "
        "sharing module 6's `Failure`.",
        "",
        "Because all three share `Failure`, a parse failure, a scan failure and "
        "an evaluation failure are the same type — `run` returns each one's "
        "`error` the same way.",
    ),
    _syn(
        "case \"neg\": { const operand = evaluate(e.operand); … }",
        "A case body in braces, so it can declare its own `const`s. Needed as "
        "soon as a case does more than one `return`.",
        "",
        "Without braces, a `const` in one case is in scope for the whole switch, "
        "and two cases declaring `left` would clash.",
    ),
    _syn(
        "if (right === 0) { return { ok: false, error: \"error: division by zero\" }; }",
        "Check the divisor before dividing. The check is on the operand, not the "
        "result — so `0 / 0` is caught too.",
        "",
        "`=== 0` is also true for `-0`, which is right: dividing by negative zero "
        "is still dividing by zero.",
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — what JavaScript decided for you.
# ---------------------------------------------------------------------------

_C11_S1 = _pstep(
    "finite", "Every value is finite",
    "`Number.isFinite`, the `EvalResult` union, and one function that guards every number.",
    """
JavaScript numbers are 64-bit floating point. They have three values that are
not ordinary numbers: `Infinity`, `-Infinity` and `NaN`. Arithmetic produces
them instead of failing:

```ts
1 / 0           // Infinity
0 / 0           // NaN
1e308 * 10      // Infinity — too big for 64 bits
```

`Number.isFinite` is false for all three and true for everything else, so one
test catches every bad value:

```ts
function checked(value: number): EvalResult {
  if (!Number.isFinite(value)) {
    return { ok: false, error: "error: number too large" };
  }
  return { ok: true, value: value };
}
```

Every number the evaluator produces — a literal, a sum, a product, a quotient —
goes through `checked`. That is how "every value is finite" becomes a rule rather
than a hope: there is one place it is enforced, and no way around it.

### The third result union

```ts
type EvalResult = { ok: true; value: number } | Failure;
```

Same shape as `ScanResult` and `ParseResult` — a success carrying the answer, or
module 6's `Failure`. Three stages, three results, one failure type.

### Why "too large", and not "infinity"

The user never typed infinity. They typed something whose answer is bigger than
about 1.8 × 10³⁰⁸ — a very long number, or two big ones multiplied. "Number too
large" describes what happened in their terms. (`NaN` will never reach `checked`
from a real program, as step 2 shows; the message only has to describe the
overflow.)
""",
    """
```
7
2.5
error: number too large
error: number too large
1e+308
```

`1e308` is the largest power of ten a double can hold, and it is finite. Ten
times it is not.
""",
    pitfalls=[
        "The global `isFinite` instead of `Number.isFinite`. It converts its argument first; for numbers it agrees, and it is still the wrong habit.",
        "`value === Infinity`. Misses `-Infinity` and `NaN` — and `NaN === NaN` is false, so `value === NaN` never matches anything.",
        "Checking only the final answer in `run`. The rule is that every value is finite; checking at the end reports `1e308 * 10 - 1e308 * 10` as `NaN`-related nonsense rather than the overflow.",
        "Throwing on a bad value. Errors are values until module 17 — and this one has to reach the user as a message, not a stack trace.",
    ],
    warmup=[
        _pq("Which of these does `Number.isFinite` return `true` for?",
            ["`-2.5`",
             "`1 / 0`",
             "`0 / 0`",
             "`-1 / 0`"],
            0,
            "Negative and fractional numbers are finite. The three special values "
            "are not."),
    ],
    exercises=[
        _pex("calc-m11-finite-1", "Guard every number",
             "Finish `checked`: a value that is `Infinity`, `-Infinity` or `NaN` "
             "is a failure.",
             _c11_s1(),
             "  if (!Number.isFinite(value)) {",
             [("", _C11_S1_OUT)],
             ["One test covers all three special values.",
              "It is on `Number`, and it returns true for ordinary numbers.",
              "`if (!Number.isFinite(value)) {`"]),
        _pex("calc-m11-finite-2", "What evaluation returns",
             "Declare `EvalResult`: a number, or a `Failure`.",
             _c11_s1(),
             "type EvalResult = { ok: true; value: number } | Failure;",
             [("", _C11_S1_OUT)],
             ["Same shape as `ParseResult`.",
              "The success carries a `value` of type `number`.",
              "`type EvalResult = { ok: true; value: number } | Failure;`"]),
    ],
    quiz=[
        _pq("Why is `Number.isFinite(x)` the right test rather than `x !== Infinity`?",
            ["It also rejects `-Infinity` and `NaN`, and `NaN` cannot be found with `===` at all",
             "It is faster",
             "`Infinity` is not a number",
             "They are the same"],
            0,
            "One test, three bad values."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — division by zero, decided.
# ---------------------------------------------------------------------------

_C11_S2 = _pstep(
    "divide", "Division by zero, decided",
    "Check the divisor before dividing — so `0 / 0` gets an honest message too.",
    """
With `checked` in place, `1 / 0` is already refused — `Infinity` is not finite.
But the message is wrong:

```
$ echo '1 / 0' | node calc.ts
error: number too large
```

Nothing was too large. The user divided by zero, and the message should say so.
And `0 / 0` is `NaN`, which "number too large" describes even less.

So division checks its divisor **first**:

```ts
case "/":
  if (right === 0) {
    return { ok: false, error: "error: division by zero" };
  }
  return checked(left / right);
```

Check the cause, not the symptom. The symptom — a non-finite result — has several
possible causes, and `checked` cannot tell them apart. The cause — a zero on the
right of a `/` — is exactly one thing, and it has exactly one message.

### Why `0 / 0` never reaches `checked`

Every `NaN` in ordinary arithmetic comes from `0 / 0` or from combining
infinities. The first is caught here, before dividing. The second cannot happen,
because `checked` never lets an infinity out to be combined. So the evaluator
never produces a `NaN` at all — which is why step 1 could give `checked` a
message about size and nothing else.

### The same arithmetic, now fallible

`arithmetic` returns an `EvalResult` now. Every case goes through `checked`, and
division has one check in front of it. The `never` default from module 10 is
still there — this module did not add an operator, so it has nothing to say.
""",
    """
```bash
$ echo '1 / 0' | node calc.ts
error: division by zero
$ echo '0 / 0' | node calc.ts
error: division by zero
$ echo '7 / (3 - 3)' | node calc.ts
error: division by zero
```

The last one divides by a zero that was *computed*. The check is on the value,
so it does not matter where the zero came from.
""",
    pitfalls=[
        "Relying on `checked` alone. Division by zero is reported as `number too large`, which is true of nothing the user typed.",
        "Checking the literal instead of the value: `if (e.right.kind === \"num\" && e.right.value === 0)`. Misses `7 / (3 - 3)`.",
        "Checking `left === 0`. `0 / 5` is a perfectly good zero; `5 / 0` is the problem.",
        "Returning `0` for division by zero. Some languages do; it is the module 10 mistake — an answer to a question nobody asked.",
    ],
    warmup=[
        _pq("Why check `right === 0` before dividing, instead of letting `checked` catch the Infinity?",
            ["`checked` sees only the symptom and would say \"too large\"; the check before dividing names the cause, and also catches `0 / 0`",
             "Because dividing by zero crashes JavaScript",
             "Because `checked` cannot see division",
             "No reason"],
            0,
            "Name the cause, not the symptom."),
    ],
    exercises=[
        _pex("calc-m11-divide-1", "Refuse a zero divisor",
             "In the `/` case, before dividing, fail with `error: division by "
             "zero` if the divisor is zero.",
             _C11_FULL,
             '      if (right === 0) {\n        return { ok: false, error: "error: division by zero" };\n      }',
             _C11_TESTS,
             ["Which operand is the divisor?",
              "Check it before the division happens.",
              "`if (right === 0) { return { ok: false, error: \"error: division by zero\" }; }`"]),
        _pfix("calc-m11-divide-fix1", "Nothing was too large",
              "`1 / 0` says `error: number too large`. So does `0 / 0`. Neither "
              "program has a large number in it — they divide by zero.",
              _c11(arith=_C11_ARITH.replace(
                  '      if (right === 0) {\n        return { ok: false, error: "error: division by zero" };\n      }\n', "")),
              _C11_FULL,
              _C11_TESTS,
              ["Which function is producing the message? What did it actually see?",
               "`checked` only sees the result — an Infinity or a NaN.",
               "Check the divisor in the `/` case before dividing."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("After this module, can the evaluator ever produce `NaN`?",
            ["No — `0 / 0` is caught before dividing, and infinities are never let out to be combined",
             "Yes, from `0 / 0`",
             "Yes, from `Infinity - Infinity`",
             "Only for negative numbers"],
            0,
            "Two rules, and the bad value has nowhere to come from."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — evaluation can fail.
# ---------------------------------------------------------------------------

_C11_S3 = _pstep(
    "fallible", "Evaluation can fail now",
    "`evaluate` returns an `EvalResult`, every child's failure is passed up — and order decides which error wins.",
    """
`arithmetic` can fail, so `evaluate`, which calls it, can fail — and so can
anything that calls `evaluate`, which is `evaluate` itself. The change ripples up
the tree exactly the way the parser's did:

```ts
case "binary": {
  const left = evaluate(e.left);
  if (!left.ok) {
    return left;
  }
  const right = evaluate(e.right);
  if (!right.ok) {
    return right;
  }
  return arithmetic(e.op, left.value, right.value);
}
```

Module 9's version was one line. This one is nine. That is the price of errors
as values, and it is the same price the parser has paid since module 6: one
`if (!x.ok) { return x; }` per call that can fail. What it buys is that a
division by zero anywhere in the tree, however deep, reaches the top as that
exact message — never as a number.

A literal goes through `checked` too — `case "num": return checked(e.value);` —
because the scanner's `Number("999…9")` can already be `Infinity` before any
arithmetic happens.

### Order means something now

In module 9, evaluating left before right changed nothing. Now it decides which
error is reported when both sides fail:

```
1 / 0 + 999…9      ← left fails with division by zero, right with too large
```

Left first, so `division by zero` — the error that is *first in the source*.
That is what users expect from every language they have used, and it is the
same rule the scanner and parser follow: report the first problem, reading left
to right.

### Braces around the cases

`case "binary": { … }` — the braces give each case its own scope, so `neg`'s
`operand` and `binary`'s `left` do not share one. As soon as a case declares
anything, it wants braces.
""",
    """
```bash
$ echo '(1 + 2) * -3' | node calc.ts
-9
$ echo '1 / 0 - 1 / 0' | node calc.ts
error: division by zero
$ echo '999…9  (400 nines)' | node calc.ts
error: number too large
```

In the middle one, the right-hand `1 / 0` is never evaluated: the left side
failed first and the failure went straight up.
""",
    pitfalls=[
        "Evaluating the right side first. Correct answers are unchanged; when both sides fail, the wrong error is reported — the one further along the line.",
        "Forgetting the `num` case. Literals too long for a double come out as `Infinity`, and `99…9 - 99…9` is `NaN`.",
        "`return arithmetic(e.op, left, right)` — passing the results, not their values. It does not compile, which is the result type doing its job.",
        "A `neg` case with no check: `-evaluate(e.operand).value` does not compile either. Every call that can fail has to be looked at.",
    ],
    warmup=[
        _pq("In `1 / 0 - 1 / 0`, how many divisions are actually evaluated?",
            ["One — the left one fails, and its failure is returned before the right side is touched",
             "Two",
             "None",
             "Four"],
            0,
            "Pass-it-up returns immediately. Later work is skipped."),
    ],
    exercises=[
        _pex("calc-m11-fallible-1", "Both sides, in order",
             "Finish the `binary` case: evaluate the left side and pass up a "
             "failure, then the right side, then combine.",
             _C11_FULL,
             "      const left = evaluate(e.left);\n      if (!left.ok) {\n        return left;\n      }\n      const right = evaluate(e.right);\n      if (!right.ok) {\n        return right;\n      }\n      return arithmetic(e.op, left.value, right.value);",
             _C11_TESTS,
             ["Each side is an `EvalResult` now.",
              "Left first, with its own check; then right, with its own.",
              "`arithmetic` takes the two `.value`s."]),
        _pfix("calc-m11-fallible-fix1", "The second error, reported first",
              "`1 / 0 + 99…9` (four hundred nines) reports `error: number too "
              "large`. The division by zero comes first in the source, and should "
              "be the error the user sees. Every correct answer is fine.",
              _c11(evaluate=_C11_EVAL.replace(
                  "      const left = evaluate(e.left);\n      if (!left.ok) {\n        return left;\n      }\n      const right = evaluate(e.right);\n      if (!right.ok) {\n        return right;\n      }\n",
                  "      const right = evaluate(e.right);\n      if (!right.ok) {\n        return right;\n      }\n      const left = evaluate(e.left);\n      if (!left.ok) {\n        return left;\n      }\n")),
              _C11_FULL,
              _C11_TESTS + _ctests(11, ["1 / 0 + " + _C11_HUGE]),
              ["Both sides fail. Which one is evaluated first?",
               "Errors are reported in reading order everywhere else in `calc.ts`.",
               "Evaluate and check `e.left` before `e.right`."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does `case \"num\"` go through `checked` too?",
            ["A literal with hundreds of digits is already `Infinity` when the scanner converts it",
             "Because all cases must call `checked`",
             "To round the number",
             "It should not"],
            0,
            "The bad value can arrive before any arithmetic happens."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the caller, again.
# ---------------------------------------------------------------------------

_C11_S4 = _pstep(
    "caller", "The caller, again",
    "`run` checks the third stage — and the one place the compiler does not stop you forgetting.",
    """
`run` has a third result to check:

```ts
const result = evaluate(parsed.expr);
if (!result.ok) {
  return result.error;
}
return `${result.value}`;
```

Every stage now has the same shape: call, check, pass on the error or carry on.
The first failure in the pipeline ends it, with its own message.

### The mistake that compiles

Module 9's `run` ended with:

```ts
return `${evaluate(parsed.expr)}`;
```

Leave it like that and it **still compiles**. A template literal will turn
anything into text — including an object. So every answer prints:

```
[object Object]
```

Module 4 made a point of the compiler refusing `result.tokens` on an unchecked
result. That protection is about *reading a field*. Converting the whole object
to a string reads no field, so there is nothing to refuse. It is worth knowing
exactly where a guarantee stops: the result type protects you from using a
failure as a success, not from printing it without looking.

### Phase 3 is done

*Text in, a number out* — and now, *no expression evaluates to `Infinity` or
`NaN` by accident*. Every input has one honest answer: a finite number, or a
message naming what went wrong. Phase 4 starts adding the things that make it a
language.
""",
    """
```bash
$ echo '10 / 4' | node calc.ts
2.5
$ echo '1 / 0' | node calc.ts
error: division by zero
$ echo '1 +' | node calc.ts
error: unexpected end of input
```

A value, an evaluation error, a parse error — each from its own stage, all
through one `run`.
""",
    pitfalls=[
        "`${evaluate(parsed.expr)}`. Compiles, and prints `[object Object]` for every input.",
        "Printing `result.value` without the check. That one does not compile — `value` only exists on the success member.",
        "Returning `NaN` or an empty string from `run` on failure. The error message is right there on the failure.",
    ],
    warmup=[
        _pq("`return `${evaluate(parsed.expr)}`;` — does it compile after this module, and what does it print for `1 + 2`?",
            ["It compiles, and prints `[object Object]` — a template literal accepts any value",
             "It does not compile",
             "It compiles and prints `3`",
             "It prints `true`"],
            0,
            "The result type guards its fields, not its string conversion."),
    ],
    exercises=[
        _pfix("calc-m11-caller-fix1", "Every answer is `[object Object]`",
              "It compiles. Every input — `1 + 2`, `1 / 0`, `10 / 4` — prints "
              "`[object Object]`.",
              _c11(run=_C11_RUN.replace(
                  "  const result = evaluate(parsed.expr);\n  if (!result.ok) {\n    return result.error;\n  }\n  return `${result.value}`;",
                  "  return `${evaluate(parsed.expr)}`;")),
              _C11_FULL,
              _C11_TESTS,
              ["What does `evaluate` return now? What does a template literal do with an object?",
               "It is a result, like the other two stages'.",
               "Check `.ok`; return `.error` on failure and `${result.value}` on success."],
              difficulty="Easy"),
        _pch("calc-m11-caller-arith", "Arithmetic with limits", "Medium",
             "Write `arithmetic`: every result goes through `checked`, and "
             "division refuses a zero divisor before dividing.",
             _C11_FULL,
             _C11_ARITH.rstrip("\n"),
             _C11_TESTS,
             ["It returns an `EvalResult` now.",
              "`+ - *`: `return checked(left + right);` and so on.",
              "`/`: check `right === 0` first, then `checked(left / right)`.",
              "Keep the `never` default."]),
    ],
    quiz=[
        _pq("Why doesn't the compiler catch `${evaluate(parsed.expr)}`?",
            ["A template literal converts any value to text, so no field of the result is read — there is nothing to refuse",
             "Because `evaluate` returns a string",
             "It does catch it",
             "Because templates are not type-checked"],
            0,
            "Know where a guarantee stops."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C11_FINAL = _pch(
    "calc-m11-build", "Module 11 build — arithmetic with a decision", "Medium",
    "Write the evaluator with limits, from `EvalResult` to `run`:\n\n"
    "* `EvalResult` and `checked` — every value finite, or `error: number too "
    "large`\n"
    "* `evaluate` — every child's failure passed up, left before right, literals "
    "checked too\n"
    "* `arithmetic` — every result checked, and `error: division by zero` "
    "before dividing\n"
    "* `run` — three stages, three checks\n\n"
    "One test is a literal four hundred digits long.",
    _C11_FULL,
    _cjoin(_C11_RESULT, _C11_EVAL, _C11_ARITH, _C11_RUN.split("\n\nconsole.log")[0]).rstrip("\n"),
    _C11_TESTS + _ctests(11, ["1 / 0 + " + _C11_HUGE]),
    ["`checked` is the one place `Number.isFinite` appears.",
     "`evaluate`: `num` → `checked(e.value)`; `neg` and `binary` pass failures up.",
     "Division: `right === 0` before `left / right`.",
     "`run`: `${result.value}` only after `result.ok` has been checked."],
)


_CALC_MODULES.append(_pmod(
    key="calc-arithmetic", number=11, phase="eval",
    title="Division, and the arithmetic that can fail",
    what="what your language says about `1 / 0`, decided rather than inherited",
    goal="Give division a defined answer for every input, and keep every value finite.",
    why=_C11_WHY,
    est_minutes=40,
    builds_on=["calc-walk", "calc-never"],
    concepts=["language semantics", "Infinity and NaN", "Number.isFinite",
              "checking causes, not symptoms", "fallible evaluation",
              "error order", "where a type guarantee stops"],
    deliverable="`echo '1 / 0' | node calc.ts` prints `error: division by zero`, "
                "and no expression can evaluate to `Infinity` or `NaN`.",
    objectives=[
        "List what JavaScript's arithmetic produces at the edges, and why a language should decide instead",
        "Guard every value with `Number.isFinite` in one function",
        "Check a divisor before dividing, and say why that beats checking the result",
        "Make evaluation return a result, and pass failures up through the recursion",
        "Explain why operand order now decides which error is reported",
        "Say why `${result}` compiles and prints `[object Object]`",
    ],
    brief=_C11_BRIEF,
    syntax=_C11_SYNTAX,
    steps=[_C11_S1, _C11_S2, _C11_S3, _C11_S4],
    final_build=_C11_FINAL,
    acceptance=[
        "`echo '1 / 0' | node calc.ts` prints `error: division by zero`, and so does `0 / 0`.",
        "`echo '7 / (3 - 3)' | node calc.ts` prints `error: division by zero`.",
        "A literal of four hundred nines prints `error: number too large`.",
        "`echo '1 / 0 - 1 / 0' | node calc.ts` prints one error, not `NaN`.",
        "`echo '10 / 4' | node calc.ts` still prints `2.5`.",
        "No input makes `calc.ts` print `Infinity`, `-Infinity` or `NaN`.",
    ],
    manual_test="""
```bash
echo '1 / 0'            | node calc.ts     # error: division by zero
echo '0 / 0'            | node calc.ts     # error: division by zero
echo '7 / (3 - 3)'      | node calc.ts     # error: division by zero
echo '10 / 4'           | node calc.ts     # 2.5
echo '(1 - 1) / 5'      | node calc.ts     # 0
```

For the overflow, build a big number with the shell rather than typing it:

```bash
node -e 'console.log("9".repeat(400))' | node calc.ts                    # number too large
node -e 'console.log("1" + "0".repeat(300) + " * 10000000000")' | node calc.ts
```

Then look back at what you wrote down in module 9 — what you thought `1 / 0`
*should* print. If it was not an error, that is a legitimate design, and some
languages make it. The point of this module is that whichever it is, it was
decided.
""",
    reference="""// calc.ts — module 11
//
// Arithmetic with a decision. Every value the evaluator produces is finite:
//   * x / 0 is `error: division by zero` — checked BEFORE dividing, so 0 / 0 too
//   * anything non-finite (overflow, a 400-digit literal) is `error: number too large`
// Evaluation can fail, so it returns an EvalResult, and every recursive call
// passes a failure up — left before right, so the first error in the source wins.
""" + _C11_FULL,
    stretch=[
        "Add `%` with the same care: what is `5 % 0`? JavaScript says `NaN`. Decide, and enforce it.",
        "Make `0 / 0` a different message from `1 / 0` — `error: zero divided by zero is undefined`. Is it worth a second message? Argue both ways.",
        "Allow decimals in literals (`2.5`) — the scanner accepts one `.` inside a number. Then find out what `Number` does with `\"1.\"` and `\".5\"`, and decide whether your language allows them.",
        "Represent numbers as exact fractions — a numerator and a denominator — so `1 / 3 * 3` is exactly `1`. `Value` becomes an object; follow the change through `arithmetic`.",
    ],
    glossary=[
        _pgloss("semantics", "What a program means — here, what each operator does at every input, including the awkward ones."),
        _pgloss("Infinity / NaN", "JavaScript's non-finite numbers, produced by overflow and by dividing by zero. This language never lets one out."),
        _pgloss("Number.isFinite", "True for ordinary numbers, false for `Infinity`, `-Infinity` and `NaN`. Never converts its argument."),
        _pgloss("overflow", "A result too large for a 64-bit float — above about 1.8 × 10³⁰⁸ — which becomes `Infinity`."),
        _pgloss("fallible", "Able to fail. `evaluate` became fallible in this module, and returns a result to say so."),
    ],
    cheatsheet="""
```ts
type EvalResult = { ok: true; value: number } | Failure;

function checked(value: number): EvalResult {        // the ONE finiteness check
  if (!Number.isFinite(value)) { return { ok: false, error: "error: number too large" }; }
  return { ok: true, value: value };
}

case "/":
  if (right === 0) { return { ok: false, error: "error: division by zero" }; }   // cause first
  return checked(left / right);

case "binary": {                                      // left before right
  const left = evaluate(e.left);   if (!left.ok) { return left; }
  const right = evaluate(e.right); if (!right.ok) { return right; }
  return arithmetic(e.op, left.value, right.value);
}
```

| Input | Output |
|---|---|
| `1 / 0`, `0 / 0`, `7 / (3 - 3)` | `error: division by zero` |
| 400 nines | `error: number too large` |
| `1e300 * 1e10` (as digits) | `error: number too large` |
| `10 / 4` | `2.5` |

| Symptom | Cause |
|---|---|
| `1 / 0` says `number too large` | no divisor check before dividing |
| `[object Object]` | `${evaluate(…)}` — the result printed unchecked |
| the later error is reported | right side evaluated first |
""",
    self_check=[
        "Can you list what JavaScript gives for `1 / 0`, `0 / 0` and a huge product, and say why each is a bad answer here?",
        "Can you explain why the divisor check comes before the division, not after?",
        "Can you say why the evaluator can never produce `NaN` now?",
        "Can you explain why a literal goes through `checked`?",
        "Can you say which error `1 / 0 + 1 / 0 * 0` reports, and why?",
        "Can you explain why `${result}` compiles?",
    ],
    review=[
        _pq("What does `echo '0 / 0' | node calc.ts` print, and why not `NaN`?",
            ["`error: division by zero` — the divisor is checked before dividing, so no `NaN` is ever produced",
             "`NaN`",
             "`error: number too large`",
             "`0`"],
            0,
            "Check the cause and the symptom never appears."),
        _pq("Why does `evaluate` return an `EvalResult` now?",
            ["Evaluation can fail — division by zero, overflow — and a failure has to reach `run` as a message",
             "For symmetry with the parser",
             "Because `switch` requires it",
             "To make it faster"],
            0,
            "Fallible stages return results. Same rule since module 4."),
        _pq("`1 / 0 + 999…9`: which error, and why?",
            ["`division by zero` — the left side is evaluated first and its failure returns immediately",
             "`number too large`",
             "Both",
             "Neither; it prints a number"],
            0,
            "First in the source, first reported."),
        _pq("Which function is the only place `Number.isFinite` is called?",
            ["`checked` — every value goes through it",
             "`arithmetic`",
             "`run`",
             "`scan`"],
            0,
            "One rule, one place."),
        _pq("Why is `1e308` fine and `1e308 * 10` an error?",
            ["The first fits in a 64-bit float; the second overflows to `Infinity`, which is not finite",
             "Because multiplication is not allowed on large numbers",
             "Because `1e308` is a literal",
             "Both are errors"],
            0,
            "The limit is about 1.8 × 10³⁰⁸."),
    ],
    milestone="Phase 3 is done. `calc.ts` is a calculator with a spine: every input "
              "gives a finite number or a message naming the problem, and "
              "`Infinity` and `NaN` have nowhere to come from. Phase 4 turns it into "
              "a language.",
))
