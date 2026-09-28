# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 10 — Exhaustiveness with `never`.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 9's program.
#
# THE MODULE THE PROJECT HAS BEEN WALKING TOWARDS. Module 9 showed that a switch
# with every case and no default is ALREADY checked — TS2366, "Function lacks
# ending return statement". This module is honest about that, and then shows the
# three places the accidental check goes quiet:
#
#   1. code after the switch (a `let` filled in by cases, returned at the end)
#   2. a `default:` — any default — which the check can no longer see past
#   3. the message itself, which names the function, not the missing member
#
# `const impossible: never = x;` in the default fixes all three: it fires
# wherever the switch is, it IS the default, and the error names the member
# ("Type 'Neg' is not assignable to type 'never'").
#
# WHAT IS NOW LEGAL: `never`. Also taught (ungated): `default:`, `break`, and a
# block `{ }` around a case body so a `const` can live in it.
#
# DONE BEFORE PHASE 4 ON PURPOSE (the roadmap is explicit): modules 12, 14 and 15
# each add a node kind, and the check is worth most on the module that would
# otherwise have broken silently. From here on every switch over a union in the
# project ends in a `never` default, and module 15's opening exercise is the
# compiler listing exactly the places the new `if` node must be handled.
#
# The graded compile-time `fix` (`calc-m10-every-fix1`) is deliberate, like
# module 4's: the lesson is the compile error.
# ---------------------------------------------------------------------------

def _c10_never(var, indent="    "):
    return (f"{indent}default: {{\n"
            f"{indent}  const impossible: never = {var};\n"
            f"{indent}  return impossible;\n"
            f"{indent}}}\n")


def _c10_close(src, var):
    """Add a `never` default before the switch's closing brace."""
    marker = "\n  }\n}\n"
    assert src.count(marker) == 1, src
    return src.replace(marker, "\n" + _c10_never(var).rstrip("\n") + "\n  }\n}\n", 1)


_C10_DESCRIBE_FN = _C9_DESCRIBE.split("\n\nfunction unexpectedToken")[0] + "\n"
_C10_DESCRIBE = _c10_close(_C10_DESCRIBE_FN, "t") + "\n" + \
    "function unexpectedToken" + _C9_DESCRIBE.split("\n\nfunction unexpectedToken")[1]
_C10_EVAL = _c10_close(_C9_EVAL, "e")
_C10_ARITH = _c10_close(_C9_ARITH, "op")


def _c10(describe=_C10_DESCRIBE, evaluate=_C10_EVAL, arith=_C10_ARITH):
    return _c9(describe=describe, evaluate=evaluate, arith=arith)


_C10_FULL = _c10()
_C10_TESTS = _ctests(10, _C9_INPUTS)

# --- Step 1's plain program: a switch the compiler cannot check -------------
_C10_LABEL_QUIET = """function label(e: Expr): string {
  let text = "?";
  switch (e.kind) {
    case "num":
      text = "number";
      break;
    case "binary":
      text = "operation";
      break;
  }
  return text;
}
"""

_C10_LABEL = """function label(e: Expr): string {
  let text = "?";
  switch (e.kind) {
    case "num":
      text = "number";
      break;
    case "neg":
      text = "negation";
      break;
    case "binary":
      text = "operation";
      break;
    default: {
      const impossible: never = e;
      return impossible;
    }
  }
  return text;
}
"""

_C10_S1_MAIN = """const nodes: Expr[] = [num(7), neg(num(3)), binary("+", num(1), num(2))];
for (const n of nodes) {
  console.log(label(n));
}
"""
_C10_S1_OUT = "number\nnegation\noperation"


def _c10_s1(label=_C10_LABEL):
    return _plain(_cjoin('type Op = "+" | "-" | "*" | "/";\n', _C9_TREE, label, _C10_S1_MAIN))


# --- Step 3: a default that returns a "safe" value --------------------------
_C10_EVAL_DEFAULT0 = """function evaluate(e: Expr): number {
  switch (e.kind) {
    case "num":
      return e.value;
    case "binary":
      return arithmetic(e.op, evaluate(e.left), evaluate(e.right));
    default:
      return 0;
  }
}
"""

_C10_WHY = (
    "The language is about to grow: variables in module 12, booleans in 14, "
    "`if` in 15 — three new kinds of node, each of which every function over the "
    "tree must handle. Module 8 already showed how that goes wrong: brackets were "
    "added, `describe` was not updated, and a `)` was reported as the end of the "
    "input without a word from the compiler. Module 9's switches catch some of "
    "that by accident. This module makes the catching deliberate — one line, in "
    "the default branch of every switch, that fails to compile if any member of "
    "the union has been forgotten, and names the one it was."
)

_C10_BRIEF = """
### The whole module in one line

`const impossible: never = e;` in the `default` of every switch — so adding a
kind to a union is a compile error at every place that has not handled it yet.

### The check you already have, and where it stops

Delete a case from module 9's `evaluate` and the compiler complains:

```
TS2366: Function lacks ending return statement and return type does not include 'undefined'.
```

That is exhaustiveness checking — by accident. It exists because `evaluate`
promises a `number`, and a missing case means it might not return one. It stops
working in three everyday situations:

| Situation | Why the check goes quiet |
|---|---|
| The switch sets a variable and the function returns it afterwards | there is always a `return` at the end |
| The switch has a `default:` of any kind | the function can always return |
| The function returns nothing | there is nothing to be missing |

And when it does fire, it points at the function's signature, not at the case
you forgot.

### `never`: the type with no values

`never` is the type of something that cannot exist. No value has it. So:

```ts
switch (e.kind) {
  case "num":    …
  case "neg":    …
  case "binary": …
  default: {
    const impossible: never = e;    // e has been narrowed to… nothing
    return impossible;
  }
}
```

After three cases, every member of `Expr` has been handled, and in the `default`
the compiler has narrowed `e` to `never` — there is nothing left it could be.
Assigning it to a `never` variable is fine.

Now add a member to `Expr` and forget a case. In the `default`, `e` is that
forgotten member — and it is not assignable to `never`:

```
Type 'Neg' is not assignable to type 'never'.
```

On the line of the switch that forgot it. Naming the member. In every function
that switches on `Expr`, whether or not it returns anything.

### What changes in `calc.ts`

Three switches — `describe`, `evaluate`, `arithmetic` — each gain four lines.
Nothing changes at runtime; the `default` can never run. What changes is that the
next three modules cannot break the evaluator silently. The compiler will hand
you a list.
"""

_C10_SYNTAX = [
    _syn(
        "const impossible: never = e;",
        "Assert, in a way the compiler checks, that every case has been handled. "
        "It compiles only if `e` has been narrowed to nothing at all.",
        """
default: {
  const impossible: never = e;
  return impossible;
}
""",
        "`never` is the type with no values. After cases for every member of a "
        "union, the narrowed type of the switched value is `never` — so the "
        "assignment works. Miss a member, and the error names it.",
    ),
    _syn(
        "default: { … }",
        "The branch a switch takes when no `case` matched. Braces make it a block, "
        "so a `const` declared inside belongs to it alone.",
        "",
        "A `default` that returns a real value — `default: return 0;` — hides "
        "every future missing case. The only honest thing to put in one is the "
        "`never` check.",
    ),
    _syn(
        "return impossible;",
        "Return the `never`. A value of type `never` is assignable to every type, "
        "so it satisfies whatever the function promised to return.",
        "",
        "It never runs. It is there so the function's code paths all end in a "
        "`return`, which keeps module 9's check happy as well.",
    ),
    _syn(
        "case \"num\": text = \"number\"; break;",
        "`break` leaves the switch without leaving the function. Used when the "
        "cases set something and the code after the switch carries on.",
        """
switch (e.kind) {
  case "num":
    text = "number";
    break;          // jump to after the switch
  case "neg":
    text = "negation";
    break;
}
return text;
""",
        "A case with neither `return` nor `break` runs on into the next case. In "
        "a switch like this one, every case needs its `break`.",
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — where the compiler goes quiet.
# ---------------------------------------------------------------------------

_C10_S1 = _pstep(
    "quiet", "Where the compiler goes quiet",
    "A switch that sets a variable, a missing case, and no error at all.",
    """
Module 9's switches returned from every case, and the compiler caught a missing
one. Here is a function over the same tree that does not:

```ts
function label(e: Expr): string {
  let text = "?";
  switch (e.kind) {
    case "num":
      text = "number";
      break;
    case "binary":
      text = "operation";
      break;
  }
  return text;
}
```

There is no case for `neg`. It compiles without a murmur. `label(neg(num(3)))`
returns `"?"`.

Why is this one silent when `evaluate` was not? Module 9's error was *"Function
lacks ending return statement"* — it fired because a missing case meant the end
of the function could be reached with nothing returned. Here the end of the
function **always** returns `text`. From the compiler's point of view there is
nothing wrong: every path returns a string. Whether it is the *right* string is
not its business.

This shape — cases fill in a variable, one `return` at the bottom — is extremely
common. So is a switch followed by more code, and so is a function that returns
nothing and just *does* something per kind. The accidental check covers none of
them.

### `break`

Each case here ends in `break`, which jumps to the line after the switch. Leave
one out and the case runs straight on into the next one's code — so `num` would
be labelled `"operation"`. When cases `return`, as in `evaluate`, `break` is not
needed; when they do not, it is.
""",
    """
```
number
negation
operation
```

Once the `neg` case exists. Without it, the middle line is `?` — and the compiler
has no opinion.
""",
    pitfalls=[
        "Trusting a clean compile after adding a node kind. The accidental check only covers switches that are the last thing in a value-returning function.",
        "A placeholder like `let text = \"?\"`. It is what makes the missing case compile: there is always something to return.",
        "Forgetting `break`, so one case falls into the next. `return` in every case avoids it; this function cannot, so it needs `break`.",
    ],
    warmup=[
        _pq("`label` has no `neg` case but compiles. Why doesn't module 9's error appear?",
            ["The function always reaches `return text` — the missing case changes which string, not whether one is returned",
             "Because `label` is not called",
             "Because `break` disables checking",
             "Because `neg` is not in `Expr`"],
            0,
            "TS2366 is about return paths. It knows nothing about intent."),
    ],
    exercises=[
        _pfix("calc-m10-quiet-fix1", "A negation labelled `?`",
              "`label(neg(num(3)))` prints `?`. The switch has no case for "
              "negation, and nothing warned anyone. Add the case — and make sure "
              "the next kind someone adds cannot go unnoticed the same way.",
              _c10_s1(_C10_LABEL_QUIET),
              _c10_s1(),
              [("", _C10_S1_OUT)],
              ["Which kind of `Expr` has no case?",
               "Add `case \"neg\": text = \"negation\"; break;`.",
               "Then a `default` that only compiles when every kind is handled: `const impossible: never = e;`.",
               "`default: { const impossible: never = e; return impossible; }`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Which of these switches does the ACCIDENTAL check (TS2366) protect?",
            ["A switch whose every case returns, at the end of a function that returns a value",
             "A switch that sets a variable returned afterwards",
             "A switch with `default: return 0;`",
             "A switch in a function that returns nothing"],
            0,
            "Only the first. The other three are the everyday cases."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — the type with no values.
# ---------------------------------------------------------------------------

_C10_S2 = _pstep(
    "never", "The type with no values",
    "`never`, narrowing all the way down, and the one line that turns a forgotten case into a named error.",
    """
Narrowing removes members from a union as cases handle them. Follow `e` through
`evaluate`'s switch:

| Where | Type of `e` |
|---|---|
| before the switch | `NumLit \\| Neg \\| Binary` |
| in `case "num":` | `NumLit` |
| after `num` is handled | `Neg \\| Binary` |
| after `neg` is handled | `Binary` |
| after `binary` is handled — the `default` | **`never`** |

When every member has been handled, what is left is nothing. TypeScript has a
name for the type of nothing: `never`. No value has type `never`; a variable of
that type can only ever be given something that is *also* `never`.

So this line:

```ts
default: {
  const impossible: never = e;
  return impossible;
}
```

compiles exactly when `e` is `never` at that point — when every case has been
handled. Remove the `neg` case and, in the `default`, `e` is `Neg`:

```
error TS2322: Type 'Neg' is not assignable to type 'never'.
```

Compare that with module 9's message. This one is on the `default` line of the
switch that is missing a case, and it names the member it is missing. With three
node kinds that is convenient; with fifteen it is the difference between a
two-minute fix and an afternoon.

### `return impossible;`

The `default` never runs — there is no value it could run for. The `return`
makes every path through the function end in a `return`, and `never` is
assignable to every type, so it satisfies `number` here and `string` in
`describe`. It costs nothing and keeps both checks working.

### Why a block

`default: { … }` — the braces give the `const` its own scope. Without them, a
`const` declared in one case is visible (though unusable) in the others, and two
cases declaring `impossible` would clash.
""",
    """
```bash
$ echo '1 + 2 * 3' | node calc.ts
7
```

Nothing changes at runtime — the check is entirely at compile time. Delete a case
and `tsc` now names the member that lost it.
""",
    pitfalls=[
        "`const impossible: never = e.kind;` — the kind is a string, and after all cases it is also `never`, so it works… but the error message then names a string literal, not the member type. Assign the whole value.",
        "Omitting `return impossible;`. The compiler then sees a path through the `default` that falls out of the function without returning.",
        "Using `any` somewhere upstream. If `e` is `any`, narrowing does nothing and `any` is assignable to `never` — the check passes whatever you forget.",
        "Believing the `default` handles something at runtime. It is unreachable; it exists only to be type-checked.",
    ],
    warmup=[
        _pq("In the `default` of a switch that handles `num` and `binary` but not `neg`, what is the type of `e`?",
            ["`Neg` — the only member no case removed",
             "`never`",
             "`Expr`",
             "`undefined`"],
            0,
            "And `Neg` is not assignable to `never`, which is the error you want."),
    ],
    exercises=[
        _pex("calc-m10-never-1", "Nothing left",
             "In `evaluate`'s default, assert that `e` has been narrowed to "
             "nothing — so that a forgotten kind of node is a compile error "
             "naming it.",
             _C10_FULL,
             "      const impossible: never = e;\n      return impossible;\n    }\n  }\n}\n\nfunction arithmetic",
             _C10_TESTS,
             ["Declare a `const` of the type with no values.",
              "Assign it the thing the switch was on.",
              "Return it, so every path ends in a `return`.",
              "`const impossible: never = e; return impossible;`"]),
        _pex("calc-m10-never-2", "Every operator",
             "`arithmetic` switches on an `Op`. Give it the same guarantee: its "
             "default only compiles if every operator has a case.",
             _C10_FULL,
             "      const impossible: never = op;",
             _C10_TESTS,
             ["The switch is on `op`, not on a node.",
              "Same line as in `evaluate`, with the right variable.",
              "`const impossible: never = op;`"]),
    ],
    quiz=[
        _pq("Why does `const impossible: never = e;` compile only when every case is handled?",
            ["Each case narrows a member away; only when none is left is `e` itself `never`, and nothing else is assignable to `never`",
             "Because `default` only runs when all cases fail",
             "Because `never` means optional",
             "It always compiles"],
            0,
            "Narrowing to nothing, and a type nothing else fits into."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — a default that lies.
# ---------------------------------------------------------------------------

_C10_S3 = _pstep(
    "lies", "A default that lies",
    "`default: return 0;` compiles, runs, and quietly evaluates every forgotten node to zero.",
    """
The instinct, faced with a switch that might not cover everything, is to add a
safety net:

```ts
function evaluate(e: Expr): number {
  switch (e.kind) {
    case "num":
      return e.value;
    case "binary":
      return arithmetic(e.op, evaluate(e.left), evaluate(e.right));
    default:
      return 0;
  }
}
```

This compiles. Module 9's check is gone — the function can always return. And
this version was written before negation existed, so:

```
$ echo '-3' | node calc.ts
0
$ echo '(1 + 2) * -3' | node calc.ts
0
```

A default that returns a real value is not a safety net. It is a way of
answering questions nobody asked with an answer nobody checked. Zero looks like a
number, flows into arithmetic like a number, and ends up in the output — the
worst kind of wrong, because nothing about it looks broken.

### What a default is for

There are exactly two honest things to do with a `default` when switching on a
union:

1. **Nothing can reach it** — every member has a case. Say so, with `never`, so
   the compiler keeps it true.
2. **Something can reach it and that is an error** — say so, with a failure the
   caller has to handle.

`return 0` is neither. Neither is `return ""`, `return undefined`, or "print a
warning and carry on".
""",
    """
```bash
$ echo '-3' | node calc.ts
-3
$ echo '(1 + 2) * -3' | node calc.ts
-9
```

With the `neg` case back and the `default` replaced by the `never` check.
""",
    pitfalls=[
        "`default: return 0;` — or any plausible value. It disables every check the compiler had and turns a missing case into a wrong answer.",
        "`default: console.log(\"unknown node\"); return 0;`. A message on the side does not stop the wrong number going to the output.",
        "Keeping the safe default AND adding the `never` line after it. The `default` already returned; there is no \"after\".",
    ],
    warmup=[
        _pq("`evaluate` has `default: return 0;` and no `neg` case. What does `2 * -3` print?",
            ["`0` — the negation evaluates to 0, and `2 * 0` is 0, with no error anywhere",
             "`-6`",
             "A compile error",
             "An error message"],
            0,
            "A default that returns a value is a silent wrong answer waiting to "
            "happen."),
    ],
    exercises=[
        _pfix("calc-m10-lies-fix1", "Minus three is zero",
              "`-3` prints `0`, and so does `(1 + 2) * -3`. Every other test "
              "passes. The evaluator has a `default` that answers any node it "
              "does not recognise with a zero.",
              _c10(evaluate=_C10_EVAL_DEFAULT0),
              _C10_FULL,
              _C10_TESTS + _ctests(10, ["-3"]),
              ["Which kind of node has no case?",
               "The `default` is answering for it — with a number that looks real.",
               "Add `case \"neg\": return -evaluate(e.operand);`.",
               "Replace the default's `return 0` with the `never` check, so this cannot happen again."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("What are the only two honest uses of `default` in a switch over a union?",
            ["Proving nothing reaches it (the `never` check), or reporting that reaching it is an error",
             "Returning 0 or returning an empty string",
             "Logging and continuing",
             "There are none; never write a default"],
            0,
            "Anything else answers a question nobody asked."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — every switch, both unions.
# ---------------------------------------------------------------------------

_C10_S4 = _pstep(
    "every", "Every switch, both unions",
    "`describe` over `Token`, `evaluate` over `Expr`, `arithmetic` over `Op` — and the list the compiler will hand you.",
    """
The check belongs on **every** switch over a union, not just the ones that look
risky. In `calc.ts` that is three:

| Function | Switches on | Grows in |
|---|---|---|
| `describe` | `Token` — five kinds | module 12 (names), 13 (`let`, `=`, `;`), 14, 15 |
| `evaluate` | `Expr` — three kinds | module 12 (variables), 14 (booleans), 15 (`if`) |
| `arithmetic` | `Op` — four operators | module 14 (`<`, `>`, `==`) |

Every one of them is going to grow. Module 8 was the preview: brackets were added
to `Token`, `describe` was not updated, and the only way to find out was to read.

With the check on all three, adding a member to any union produces a list:

```
calc.ts:74:13 - error TS2322: Type 'RParenToken' is not assignable to type 'never'.
calc.ts:141:13 - error TS2322: Type 'Var' is not assignable to type 'never'.
```

one line per switch that needs a new case. That list is a to-do list the compiler
writes for you. Work through it and the language grows without a single forgotten
branch.

### The same four lines, three times

```ts
default: {
  const impossible: never = t;     // or e, or op
  return impossible;
}
```

It is boilerplate, and it is worth it. The stretch list shows how to name it as a
function — module 17, where `throw` arrives, is the natural place to do that for
real.
""",
    """
```bash
$ npx tsc --noEmit --strict calc.ts
$ echo '(1 + 2) * -3' | node calc.ts
-9
```

A clean compile, and behaviour identical to module 9's. The difference is what
happens next time a union grows.
""",
    pitfalls=[
        "Adding the check only to `evaluate`. `describe` is the switch that has already been caught out once.",
        "Assigning the wrong variable: `const impossible: never = e;` inside `describe`, where the token is `t`. It does not compile — `e` does not exist there.",
        "Treating the compile errors after growing a union as noise to silence. Each one is a place that genuinely needs a new case.",
    ],
    warmup=[
        _pq("A new token kind is added and `describe` has the `never` check. What happens?",
            ["A compile error in `describe`'s default, naming the new token type",
             "The new token is described as `end of input`",
             "A runtime error",
             "Nothing"],
            0,
            "Module 8's silent bug becomes a compile error with a name in it."),
    ],
    exercises=[
        _pfix("calc-m10-every-fix1", "The compiler hands you a name",
              "This does not compile:\n\n"
              "    Type 'RParenToken' is not assignable to type 'never'.\n\n"
              "Someone rewrote `describe` and lost a case. The error says which.",
              _c10(describe=_C10_DESCRIBE.replace('    case "rparen":\n      return "\')\'";\n', "")),
              _C10_FULL,
              _C10_TESTS,
              ["The error names the member with no case.",
               "Add it back, before the default.",
               "`case \"rparen\": return \"')'\";`"],
              difficulty="Intro"),
        _pex("calc-m10-every-1", "Guard the token switch",
             "Finish `describe`'s default: it only compiles when every kind of "
             "token has a case.",
             _C10_FULL,
             "      const impossible: never = t;",
             _C10_TESTS,
             ["`describe` switches on the token `t`.",
              "Same line as in `evaluate`, with the right variable.",
              "`const impossible: never = t;`"]),
    ],
    quiz=[
        _pq("Why put the `never` check on every switch over a union, not just the important ones?",
            ["Every one of them grows when the union grows, and a forgotten case in an 'unimportant' one is still a wrong answer",
             "Because the compiler requires it",
             "Because it makes the program faster",
             "Only `evaluate` needs it"],
            0,
            "`describe` was the unimportant one, and it was the one that broke."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C10_FINAL = _pch(
    "calc-m10-build", "Module 10 build — exhaustive by construction", "Medium",
    "Write the evaluator again, this time with a guarantee:\n\n"
    "* `evaluate` — three cases and a `never` default\n"
    "* `arithmetic` — four cases and a `never` default\n"
    "* `run` — scan, parse, evaluate\n\n"
    "`describe` already has its check. The tests are module 9's — nothing changes "
    "at runtime. What you are building is the compile error the next module "
    "will get.",
    _C10_FULL,
    _cjoin(_C10_EVAL, _C10_ARITH, _C9_RUN.split("\n\nconsole.log")[0]).rstrip("\n"),
    _C10_TESTS,
    ["Each switch: one case per member, then `default: { const impossible: never = …; return impossible; }`.",
     "In `evaluate` the switched value is `e`; in `arithmetic` it is `op`.",
     "No default may return a real value."],
)


_CALC_MODULES.append(_pmod(
    key="calc-never", number=10, phase="eval",
    title="Exhaustiveness with `never`",
    what="the compiler proving you handled every node, forever",
    goal="Make a new node kind a compile error everywhere it is not handled.",
    why=_C10_WHY,
    est_minutes=35,
    builds_on=["calc-parens", "calc-walk"],
    concepts=["exhaustiveness checking", "the never type", "narrowing to nothing",
              "honest defaults", "break", "growing a union safely"],
    deliverable="Every switch in `calc.ts` ends in a `never` check, so adding a "
                "member to `Token`, `Expr` or `Op` is a compile error naming every "
                "place that must handle it.",
    objectives=[
        "Say when the compiler's accidental exhaustiveness check fires, and name three situations where it does not",
        "Explain what `never` is and why a switch's default narrows to it",
        "Write the `never` check and read the error it produces for a missing case",
        "Explain why `default: return 0;` is worse than no default at all",
        "Put the check on every switch over a union, and say which unions will grow next",
    ],
    brief=_C10_BRIEF,
    syntax=_C10_SYNTAX,
    steps=[_C10_S1, _C10_S2, _C10_S3, _C10_S4],
    final_build=_C10_FINAL,
    acceptance=[
        "`describe`, `evaluate` and `arithmetic` each end their switch with `default: { const impossible: never = …; return impossible; }`.",
        "Deleting any case from any of the three produces `Type '…' is not assignable to type 'never'`, naming the member.",
        "No switch in `calc.ts` has a `default` that returns a real value.",
        "`echo '(1 + 2) * -3' | node calc.ts` still prints `-9` — nothing changes at runtime.",
    ],
    manual_test="""
Nothing new to type at the shell. The test for this module is the compiler.

1. Add a fourth member to `Expr` — say `type Abs = { kind: "abs"; operand: Expr };`
   and `| Abs` in the union.
2. Run `npx tsc --noEmit --strict calc.ts`.

You should get exactly one error, in `evaluate`, naming `Abs`. Now add a token
kind the same way — `type CommaToken = { kind: "comma" };` — and you get one in
`describe`. Add `"%"` to `Op`: one in `arithmetic`. (The scanner will also
complain about `"%"`, if you try to push one — follow that too.)

Delete all three additions. Then try the same experiment on your module 9 file,
if you kept it: `Abs` produces a `TS2366` pointing at `evaluate`'s return type,
and the token and operator additions produce nothing at all.
""",
    reference="""// calc.ts — module 10
//
// Same behaviour as module 9. Every switch over a union now ends in
//
//   default: { const impossible: never = x; return impossible; }
//
// which compiles only when every member has a case. Add a member to Token, Expr
// or Op and the compiler lists each switch that needs one — by name.
""" + _C10_FULL,
    stretch=[
        "Name the check: `function assertNever(x: never): never { … }`. What can its body be, with no `throw` yet? (Module 17 has the real answer.) Then replace the three defaults with `return assertNever(e);`.",
        "Write a `void` function over `Expr` — `countKinds(e, counts)` that increments a counter per kind — and confirm that without the `never` check, deleting a case produces no error at all.",
        "Add `\"%\"` to `Op` for real: the scanner, `arithmetic`, and nothing else. Let the compiler tell you when you are done.",
        "Find out what `satisfies never` does, and whether `e satisfies never` could replace the two-line check.",
    ],
    glossary=[
        _pgloss("exhaustiveness", "Every member of a union handled. Checked here by the compiler, not by reading."),
        _pgloss("never", "The type with no values. What a union narrows to once every member has been handled."),
        _pgloss("exhaustiveness check", "`const impossible: never = x;` in a default — compiles only if nothing is left unhandled, and names what is."),
        _pgloss("default", "The branch a switch takes when no case matched. Honest only as a `never` check or an error."),
        _pgloss("break", "Leave a switch without leaving the function."),
    ],
    cheatsheet="""
```ts
switch (e.kind) {
  case "num":    return e.value;
  case "neg":    return -evaluate(e.operand);
  case "binary": return arithmetic(e.op, evaluate(e.left), evaluate(e.right));
  default: {
    const impossible: never = e;     // e is `never` only if every kind has a case
    return impossible;
  }
}
```

| Switch | On | Variable |
|---|---|---|
| `describe` | `Token` | `t` |
| `evaluate` | `Expr` | `e` |
| `arithmetic` | `Op` | `op` |

| You see | It means |
|---|---|
| `Type 'Neg' is not assignable to type 'never'` | this switch has no case for `Neg` |
| `TS2366: Function lacks ending return statement` | the accidental check — a case is missing somewhere |
| a wrong answer and no error | a `default` that returns a real value |
""",
    self_check=[
        "Can you name three situations where a missing case compiles cleanly without the `never` check?",
        "Can you narrow `Expr` case by case and say what is left in the default?",
        "Can you write the check from memory, and say why it returns?",
        "Can you explain why `default: return 0;` is worse than no default?",
        "Can you list the three switches in `calc.ts` and the modules that will grow each union?",
    ],
    review=[
        _pq("What is `never`?",
            ["The type with no values — what a union narrows to after every member is handled",
             "A type meaning optional",
             "A keyword that stops a function",
             "Another name for `void`"],
            0,
            "Nothing is assignable to it except another `never`."),
        _pq("`evaluate` has no `neg` case and ends with the `never` check. What is the error?",
            ["`Type 'Neg' is not assignable to type 'never'`, on the default's line",
             "`Function lacks ending return statement`",
             "No error",
             "A runtime error for negative numbers"],
            0,
            "It names the member and the switch."),
        _pq("Why does module 9's accidental check miss a switch whose cases set a variable returned afterwards?",
            ["There is always a `return` at the end, so no path lacks one — the check is about return paths, not cases",
             "Because variables cannot be narrowed",
             "Because `break` turns checking off",
             "It does not miss it"],
            0,
            "And that shape is everywhere."),
        _pq("Why is this module placed before phase 4?",
            ["Phase 4 adds three node kinds; the check is worth most on the modules that would otherwise break silently",
             "Because `never` is needed for booleans",
             "Because phase 4 uses `switch` for the first time",
             "No reason"],
            0,
            "Install the smoke alarm before the fire."),
        _pq("What should replace `default: return 0;` in a switch over `Expr`?",
            ["`default: { const impossible: never = e; return impossible; }`",
             "`default: return -1;`",
             "`default: return NaN;`",
             "Nothing — remove the switch"],
            0,
            "A default that proves it cannot run, instead of one that runs "
            "wrongly."),
    ],
    milestone="Growing the language can no longer silently break it. Every switch "
              "over a union ends in a check the compiler enforces, and adding a "
              "kind of token, node or operator produces a list — by name — of every "
              "place that must learn about it.",
))
