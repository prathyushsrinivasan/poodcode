# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 5 — What a tree is.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`.
#
# THE RECURSIVE-TYPE JUMP, AND NOTHING ELSE. The roadmap budgets a whole module
# for `type Expr = NumLit | Binary` where a Binary holds two Exprs, and this is
# that module: no parser, no stdin, no evaluation. Every program is `_plain` —
# trees built by hand, printed. Same discipline as module 1: design the data
# first, write the code that produces it second (module 6).
#
# WHAT IS NOW LEGAL (`_CALC_SCOPE_RULES` at 5): `: Expr`. Nothing else — the
# module is a new idea, not new syntax. Recursion itself needs no new token: a
# function calling itself is a function call.
#
# THE PRINTER IS THE MODULE'S SECOND PAYOFF. `show` writes a tree as an
# S-expression — `(+ 1 (* 2 3))` — which makes precedence something you can SEE.
# Modules 6-8 judge the parser by exactly this output, so it is settled here,
# and `(neg 3)` for unary minus is reserved in the brief for module 8.
#
# `show` IS AN if FOLLOWED BY A FALL-THROUGH: `if num … ; return …binary…`. With
# two kinds that is fine. The day a third kind arrives, the fall-through quietly
# treats it as a binary — the weakness module 10 exists to close. Not said here
# beyond a pitfall; there is nothing to fix yet.
#
# EXPECTED OUTPUTS come from the oracle: the tree for `(1 + 2) * 3` is printed
# as `_calc("(1 + 2) * 3", 8)` — module 8's parser's view of the same source —
# so the hand-built trees are checked against a real parser's.
# ---------------------------------------------------------------------------

import json as _c5json

_C5_OP = 'type Op = "+" | "-" | "*" | "/";\n'

_C5_TYPES = """type NumLit = { kind: "num"; value: number };
type Binary = { kind: "binary"; op: Op; left: Expr; right: Expr };

type Expr = NumLit | Binary;
"""

_C5_FACTORIES = """function num(value: number): NumLit {
  return { kind: "num", value: value };
}

function binary(op: Op, left: Expr, right: Expr): Binary {
  return { kind: "binary", op: op, left: left, right: right };
}
"""

_C5_SHOW = """function show(e: Expr): string {
  if (e.kind === "num") {
    return `${e.value}`;
  }
  return `(${e.op} ${show(e.left)} ${show(e.right)})`;
}
"""

_C5_SIZE = """function size(e: Expr): number {
  if (e.kind === "num") {
    return 1;
  }
  return 1 + size(e.left) + size(e.right);
}
"""


def _c5(*parts):
    return _plain("\n".join(p.rstrip("\n") + "\n" for p in parts))


def _c5_json(src):
    """The JSON a hand-built tree for `src` prints, via the oracle's parser."""
    def conv(e):
        if e[0] == "num":
            return {"kind": "num", "value": int(e[1])}
        return {"kind": "binary", "op": e[1], "left": conv(e[2]), "right": conv(e[3])}
    tree = _CParser(_c_scan(src, 8), 8).expr()
    return _c5json.dumps(conv(tree), separators=(",", ":"))


def _c5_sx(*srcs):
    return "\n".join(_calc(s, 8) for s in srcs)


# --- Step 1: a tree written out as an object literal ------------------------
_C5_S1_MAIN = """const seven: Expr = { kind: "num", value: 7 };
const onePlusTwo: Expr = {
  kind: "binary",
  op: "+",
  left: { kind: "num", value: 1 },
  right: { kind: "num", value: 2 },
};

console.log(JSON.stringify(seven));
console.log(JSON.stringify(onePlusTwo));
"""
_C5_S1_OUT = _c5_json("7") + "\n" + _c5_json("1 + 2")

# --- Step 2: factories, and the two trees `1 + 2 * 3` could be ---------------
_C5_S2_MAIN = """const product = binary("+", num(1), binary("*", num(2), num(3)));
const grouped = binary("*", binary("+", num(1), num(2)), num(3));

console.log(JSON.stringify(product));
console.log(JSON.stringify(grouped));
"""
_C5_S2_OUT = _c5_json("1 + 2 * 3") + "\n" + _c5_json("(1 + 2) * 3")

# --- Step 3: the printer ----------------------------------------------------
_C5_S3_MAIN = """console.log(show(num(7)));
console.log(show(binary("+", num(1), num(2))));
console.log(show(binary("+", num(1), binary("*", num(2), num(3)))));
console.log(show(binary("*", binary("+", num(1), num(2)), num(3))));
console.log(show(binary("-", num(10), num(4))));
console.log(show(binary("/", num(8), binary("-", num(6), num(2)))));
"""
_C5_S3_OUT = _c5_sx("7", "1 + 2", "1 + 2 * 3", "(1 + 2) * 3", "10 - 4", "8 / (6 - 2)")

# --- Step 4 and the build: which way a chain leans --------------------------
_C5_S4_MAIN = """const trees: Expr[] = [
  num(7),
  binary("+", num(1), binary("*", num(2), num(3))),
  binary("-", binary("-", num(10), num(4)), num(3)),
  binary("/", binary("/", num(100), num(10)), num(2)),
  binary("-", num(10), binary("-", num(4), num(3))),
];

for (const t of trees) {
  console.log(`${show(t)} has ${size(t)} nodes`);
}
"""


def _c5_sized(src, n):
    return f"{_calc(src, 8)} has {n} nodes"


_C5_S4_OUT = "\n".join([
    _c5_sized("7", 1),
    _c5_sized("1 + 2 * 3", 5),
    _c5_sized("10 - 4 - 3", 5),
    _c5_sized("100 / 10 / 2", 5),
    _c5_sized("10 - (4 - 3)", 5),
])

_C5_FULL = _c5(_C5_OP, _C5_TYPES, _C5_FACTORIES, _C5_SHOW, _C5_SIZE, _C5_S4_MAIN)


_C5_WHY = (
    "Phase 1 turned text into a list, and a list is the wrong shape for "
    "arithmetic. `1 + 2 * 3` and `1 * 2 + 3` are the same five tokens in a row, "
    "and they mean different things for a reason no list can show: which "
    "operation happens *inside* which. That is a tree. Before any code builds "
    "one, the tree needs a type — and it is the first type in this project that "
    "has to mention itself, because a sum of two things is a thing that can be "
    "summed. This module is only that type, the trees you can build with it by "
    "hand, and the first function that walks one."
)

_C5_BRIEF = """
### The whole module in one line

Write down, as a type, the shape `1 + 2 * 3` really has — and build a few by hand
before any parser exists.

### A list cannot hold precedence

After phase 1, `1 + 2 * 3` is:

```
[num 1] [op +] [num 2] [op *] [num 3] [eof]
```

Everything that matters about it is missing. The `*` happens first — but nothing
in the list says so; you *know* it, from school. A program that only has the
list has to rediscover that rule every time it looks. So the next phase builds
something that has the rule baked into its shape:

```
      +
     / \\
    1   *
       / \\
      2   3
```

An addition whose right-hand side is a multiplication. Nobody has to remember
that `*` binds tighter; the `*` is simply *underneath* the `+`, so it has to be
worked out before the `+` can be.

### The type

```ts
type NumLit = { kind: "num"; value: number };
type Binary = { kind: "binary"; op: Op; left: Expr; right: Expr };

type Expr = NumLit | Binary;
```

Module 1's discriminated union, with one new thing: `Binary` mentions `Expr`, and
`Expr` includes `Binary`. The type refers to itself. That is not a trick — it is
the only honest description of arithmetic, where either side of a `+` can be any
expression at all, including another `+`.

### How you will see a tree

`JSON.stringify` of a tree is correct and unreadable. So this module also writes
`show`, which prints one as an **S-expression** — the operator first, then both
sides, in brackets:

| Source | Tree, printed |
|---|---|
| `7` | `7` |
| `1 + 2 * 3` | `(+ 1 (* 2 3))` |
| `(1 + 2) * 3` | `(* (+ 1 2) 3)` |
| `10 - 4 - 3` | `(- (- 10 4) 3)` |

Read the brackets and precedence is right there on the page. Modules 6 to 8 are
judged by exactly this output — the parser is correct when `show` of its tree
matches — so the format is decided here. (Unary minus will print as `(neg 3)`,
when module 8 adds it, so it can never be mistaken for subtraction.)

### What this module does not do

Read anything. Every program here builds its trees by hand, in code. That is on
purpose: the parser in module 6 has one job — *produce these values* — and it is
much easier to write a function when you already know exactly what it must
return.
"""

_C5_SYNTAX = [
    _syn(
        "type Binary = { kind: \"binary\"; op: Op; left: Expr; right: Expr };",
        "A type that refers to itself. A binary operation holds an operator and two "
        "sub-expressions — and a sub-expression can be anything an `Expr` can be, "
        "including another `Binary`.",
        """
type NumLit = { kind: "num"; value: number };
type Binary = { kind: "binary"; op: Op; left: Expr; right: Expr };
type Expr = NumLit | Binary;
""",
        "Using `Expr` before the line that defines it is fine: type declarations are "
        "not run top to bottom, and the compiler reads all three together. What "
        "stops the recursion from being infinite is `NumLit` — every branch of a "
        "real tree ends in a number.",
    ),
    _syn(
        "type Expr = NumLit | Binary;",
        "The union every tree node belongs to. A function that takes an `Expr` "
        "accepts a single number and an enormous nested sum alike.",
        """
const seven: Expr = { kind: "num", value: 7 };
const sum: Expr = { kind: "binary", op: "+", left: seven, right: seven };
""",
        "Module 1's `Token` was a union of three flat shapes. This is a union of two, "
        "one of which contains the union — the same tool, one step further.",
    ),
    _syn(
        "function show(e: Expr): string { … show(e.left) … }",
        "**Recursion**: a function that calls itself on a smaller piece. A type "
        "that refers to itself is walked by a function that refers to itself.",
        """
function show(e: Expr): string {
  if (e.kind === "num") {
    return `${e.value}`;                                  // a leaf: stop
  }
  return `(${e.op} ${show(e.left)} ${show(e.right)})`;    // a branch: recurse
}
""",
        "Every recursive function needs a case that does not recurse — here, a "
        "number. Because every tree bottoms out in numbers, every call to `show` "
        "eventually reaches one and returns.",
    ),
    _syn(
        "const trees: Expr[] = [ … ];",
        "An array of trees. Each element can be a different shape — a lone number "
        "next to a deep sum — because each is an `Expr`.",
        """
const trees: Expr[] = [num(7), binary("+", num(1), num(2))];
for (const t of trees) {
  console.log(show(t));
}
""",
        "",
    ),
    _syn(
        "if (e.kind === \"num\") { … }",
        "Module 1's narrowing on the tag. Inside, `e.value` exists; after the "
        "`return`, only `Binary` is left, so `e.left` does.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — a type that refers to itself.
# ---------------------------------------------------------------------------

_C5_S1 = _pstep(
    "self", "A type that refers to itself",
    "Two node kinds, one union, and a `Binary` whose sides are themselves `Expr`s.",
    """
A tree has two kinds of node. A **leaf** is a number — nothing below it. A
**branch** is an operation — an operator, and the two things it operates on.

```ts
type NumLit = { kind: "num"; value: number };
type Binary = { kind: "binary"; op: Op; left: Expr; right: Expr };

type Expr = NumLit | Binary;
```

`NumLit` is a number literal: the `7` in `7 + 1`. `Binary` is a binary operation:
the `+`, with whatever is on its left and right. And whatever is on its left and
right is an `Expr` — a number, or another operation. That single word, `Expr`,
inside `Binary`, is what lets a tree be as deep as it needs to be.

### It is not infinite

A type that contains itself sounds like it should go on forever. It does not,
because one member of the union contains *nothing*: a `NumLit` is a dead end.
Every real tree reaches numbers on every branch, the same way every real folder
on a disk eventually contains only files.

### Writing one out in full

```ts
const onePlusTwo: Expr = {
  kind: "binary",
  op: "+",
  left: { kind: "num", value: 1 },
  right: { kind: "num", value: 2 },
};
```

The compiler checks every level. `left` must be an `Expr`, so `{ kind: "num",
value: 1 }` is checked against the union and matches `NumLit`. Put `"one"` in
`value`, or `"%"` in `op`, and it is refused — at whatever depth it is buried.

### Why `num` and not `number`

The token kind was `"number"`. The node kind is `"num"`. They are different
things — a token is a piece of text that was a number; a node is a number in a
tree — and giving them different tags means a `Token` can never be passed where
an `Expr` was wanted by accident. The compiler would refuse `{ kind: "number",
value: 1 }` as an `Expr`.
""",
    """
```
{"kind":"num","value":7}
{"kind":"binary","op":"+","left":{"kind":"num","value":1},"right":{"kind":"num","value":2}}
```

The second line is a tree: an object whose `left` and `right` are objects of the
same union.
""",
    pitfalls=[
        "`left: NumLit; right: NumLit`. Compiles, and describes a language where `1 + 2` is legal and `1 + 2 * 3` is not — a `Binary` could never hold another `Binary`.",
        "`left?: Expr; right?: Expr` on a single node type with an optional `value`. Module 1's optional-field mistake again: it allows a `+` with no sides and a number with an operator.",
        "Reusing the token's `\"number\"` tag for the node. Tokens and nodes are different stages of the pipeline; sharing a tag lets one pass for the other.",
        "Expecting the recursion in the type to need a special keyword. It does not — a type alias can name itself inside an object type.",
    ],
    warmup=[
        _pq("Which of these is a valid `Expr`?",
            ["`{ kind: \"binary\", op: \"*\", left: { kind: \"num\", value: 2 }, right: { kind: \"binary\", op: \"+\", left: { kind: \"num\", value: 1 }, right: { kind: \"num\", value: 1 } } }`",
             "`{ kind: \"binary\", op: \"*\", left: 2, right: 3 }`",
             "`{ kind: \"num\", value: 2, op: \"+\" }`",
             "`{ kind: \"number\", value: 2 }`"],
            0,
            "Both sides of a `Binary` are `Expr`s, and an `Expr` can be another "
            "`Binary`. A bare `2` is a number, not a node; `\"number\"` is the token's "
            "tag."),
    ],
    exercises=[
        _pex("calc-m5-self-1", "The union of nodes",
             "Declare `Expr`: a node is either a number literal or a binary "
             "operation.",
             _c5(_C5_OP, _C5_TYPES, _C5_S1_MAIN),
             "type Expr = NumLit | Binary;",
             [("", _C5_S1_OUT)],
             ["A union of the two node types, joined with `|`.",
              "It is used inside `Binary` before this line — that is allowed.",
              "`type Expr = NumLit | Binary;`"]),
        _pex("calc-m5-self-2", "Both sides are trees",
             "Finish `Binary`: after the operator come the two sides, and each side "
             "can be any expression at all.",
             _c5(_C5_OP, _C5_TYPES, _C5_S1_MAIN),
             "left: Expr; right: Expr",
             [("", _C5_S1_OUT)],
             ["Two fields, `left` and `right`.",
              "Their type is not `NumLit` — a side can be another operation.",
              "`left: Expr; right: Expr`"]),
    ],
    quiz=[
        _pq("What stops `type Expr = NumLit | Binary` from describing only infinite trees?",
            ["`NumLit` contains no `Expr`, so a branch can end — every real tree bottoms out in numbers",
             "TypeScript limits recursion depth to 100",
             "`Binary` is optional",
             "Nothing; it describes infinite trees and that is fine"],
            0,
            "A recursive type needs a member that does not recurse, exactly as a "
            "recursive function needs a case that returns."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — factories, and a tree by hand.
# ---------------------------------------------------------------------------

_C5_S2 = _pstep(
    "build", "Factories, and trees by hand",
    "`num` and `binary`, module 1's factories one level up — and the two trees five tokens could be.",
    """
Writing trees as object literals is correct and exhausting. Module 1 solved the
same problem for tokens with factories, and they work the same way here:

```ts
function num(value: number): NumLit {
  return { kind: "num", value: value };
}

function binary(op: Op, left: Expr, right: Expr): Binary {
  return { kind: "binary", op: op, left: left, right: right };
}
```

Now a tree reads almost like the arithmetic:

```ts
binary("+", num(1), num(2))                         // 1 + 2
```

### Build from the inside out

For `1 + 2 * 3`, ask: *which operation happens last?* That is the top of the tree.
Here, the `+` — it has to wait for `2 * 3`. So the `+` is the outer call, and the
`*` goes inside it, as its right-hand side:

```ts
binary("+", num(1), binary("*", num(2), num(3)))    // 1 + 2 * 3
```

The same five tokens with brackets, `(1 + 2) * 3`, make a different tree, because
now the `*` happens last:

```ts
binary("*", binary("+", num(1), num(2)), num(3))    // (1 + 2) * 3
```

Look at what happened to the brackets: they are **gone**. The second tree has no
node for them. Their whole job was to say "do the `+` first", and in a tree that
is said by putting the `+` underneath. This is why the parser in module 8 will
not need a node kind for parentheses.

### The rule, stated once

> The operation that happens **last** is at the **top**. Whatever must be worked
> out first is further down.

Everything the parser does in modules 6 to 8 is producing trees that obey this.
""",
    """
```
{"kind":"binary","op":"+","left":{"kind":"num","value":1},"right":{"kind":"binary","op":"*",…}}
{"kind":"binary","op":"*","left":{"kind":"binary","op":"+",…},"right":{"kind":"num","value":3}}
```

The same five numbers and operators, two different trees. In the first the `*`
is nested inside; in the second the `+` is.
""",
    pitfalls=[
        "Building left to right as you read: `binary(\"*\", binary(\"+\", num(1), num(2)), num(3))` for `1 + 2 * 3`. That is the tree for `(1 + 2) * 3` — the order of the text is not the order of the operations.",
        "Adding a node kind for parentheses. The tree's shape already says what the brackets said; a `paren` node would be a second way to say it.",
        "Writing `num(\"1\")`. The factory takes a number, because the scanner already turned text into numbers in module 3.",
        "Factories that take the whole object: `binary({ op, left, right })`. It works, and it is the object literal again with more punctuation.",
    ],
    warmup=[
        _pq("Which operation is at the top of the tree for `8 / 2 + 1`?",
            ["The `+` — it happens last, after `8 / 2`",
             "The `/` — it comes first in the text",
             "Both, side by side",
             "Neither; `1` is at the top"],
            0,
            "Last to happen, highest in the tree. `binary(\"+\", binary(\"/\", num(8), "
            "num(2)), num(1))`."),
    ],
    exercises=[
        _pex("calc-m5-build-1", "One plus two times three",
             "Build the tree for `1 + 2 * 3` with the factories: the multiplication "
             "happens first, so it sits underneath the addition.",
             _c5(_C5_OP, _C5_TYPES, _C5_FACTORIES, _C5_S2_MAIN),
             'binary("+", num(1), binary("*", num(2), num(3)))',
             [("", _C5_S2_OUT)],
             ["Which operation happens last? That is the outermost `binary(…)` call.",
              "The `+` has `1` on its left and the whole product on its right.",
              "`binary(\"+\", num(1), binary(\"*\", num(2), num(3)))`"]),
        _pex("calc-m5-build-2", "The factory for a branch",
             "Finish `binary`: return a `Binary` node carrying the operator and "
             "both sides.",
             _c5(_C5_OP, _C5_TYPES, _C5_FACTORIES, _C5_S2_MAIN),
             '  return { kind: "binary", op: op, left: left, right: right };',
             [("", _C5_S2_OUT)],
             ["The same shape as `num`, with more fields.",
              "The tag is `\"binary\"`, and the fields are in the order the type declares them — the JSON output shows it.",
              "`return { kind: \"binary\", op: op, left: left, right: right };`"]),
        _pfix("calc-m5-build-fix1", "Read left to right",
              "`product` is supposed to be the tree for `1 + 2 * 3`. It was built by "
              "reading the source left to right, and it prints the tree for a "
              "different expression.",
              _c5(_C5_OP, _C5_TYPES, _C5_FACTORIES, _C5_S2_MAIN.replace(
                  'binary("+", num(1), binary("*", num(2), num(3)))',
                  'binary("*", binary("+", num(1), num(2)), num(3))', 1)),
              _c5(_C5_OP, _C5_TYPES, _C5_FACTORIES, _C5_S2_MAIN),
              [("", _C5_S2_OUT)],
              ["Compare `product` with `grouped`. Should they be the same tree?",
               "In `1 + 2 * 3`, which operation happens last?",
               "The `+` belongs at the top, with the product as its right side.",
               "`binary(\"+\", num(1), binary(\"*\", num(2), num(3)))`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why does the tree for `(1 + 2) * 3` have no node for the parentheses?",
            ["The brackets only said \"do the `+` first\", and putting the `+` underneath the `*` already says that",
             "Parentheses are removed by the scanner",
             "Because trees cannot hold punctuation",
             "It does; `binary` records them"],
            0,
            "The shape carries the grouping. Module 8's parser will read brackets "
            "and produce no node for them."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — a function that follows the type.
# ---------------------------------------------------------------------------

_C5_S3 = _pstep(
    "show", "A function that follows the type",
    "Recursion: `show` prints a tree by printing its sides — and stops at numbers.",
    """
`JSON.stringify` of `1 + 2 * 3` is 150 characters of braces. The tree deserves a
printer that shows its shape and nothing else:

```ts
function show(e: Expr): string {
  if (e.kind === "num") {
    return `${e.value}`;
  }
  return `(${e.op} ${show(e.left)} ${show(e.right)})`;
}
```

This is **recursion**, and the shape of the function is the shape of the type:

| The type says… | So `show`… |
|---|---|
| an `Expr` is a `NumLit` | prints the number, and stops |
| …or a `Binary` holding two `Expr`s | prints the operator, then **calls `show`** on each side |

`show` does not need to know how deep the tree goes. It handles one node, and
trusts itself to handle the sides. That trust is justified because each call is
on a *smaller* tree, and every tree bottoms out in numbers, where `show` returns
without calling anything.

### Following one call

```
show(+ 1 (* 2 3))
  = "(+ " + show(1) + " " + show(* 2 3) + ")"
  = "(+ " + "1"     + " " + "(* 2 3)"   + ")"
  = "(+ 1 (* 2 3))"
```

`show(* 2 3)` is itself a call with two smaller calls inside it. Recursion is
just that, all the way down.

### Why this format

The operator goes first, then both sides, in brackets — an **S-expression**, the
notation Lisp is written in. It is ideal for checking a parser because it is
completely unambiguous: every operation has its own brackets, so there is only
one way to read `(- (- 10 4) 3)`. From module 6 to module 8, a parser is correct
exactly when `show` of its tree matches.

### Order matters

`show` prints `left` then `right`, and must. `(- 10 4)` is ten minus four;
`(- 4 10)` is not. The tree remembers which side is which, and a printer that
forgets throws that away.
""",
    """
```
7
(+ 1 2)
(+ 1 (* 2 3))
(* (+ 1 2) 3)
(- 10 4)
(/ 8 (- 6 2))
```

The third and fourth lines are the whole of phase 2 in miniature: same numbers,
same operators, different trees — and now you can see it.
""",
    pitfalls=[
        "No base case: calling `show(e.left)` without first checking for a number. It does not compile here (a `NumLit` has no `left`), which is the type doing its job — in a language without it, this is an infinite loop.",
        "Swapping `left` and `right` in the output. Harmless for `+` and `*`, wrong for `-` and `/`, and the trees for `10 - 4` and `4 - 10` print the same.",
        "Printing without brackets: `+ 1 * 2 3`. Readable once you know the trick; the brackets make each operation's extent visible at a glance.",
        "Using `JSON.stringify` inside `show` for the sides. The sides are trees too — they should be printed the same way the whole is.",
    ],
    warmup=[
        _pq("How many times is `show` called, in total, to print `(+ 1 (* 2 3))`?",
            ["5 — once per node: the `+`, the `1`, the `*`, the `2` and the `3`",
             "1",
             "2 — once per operator",
             "3 — once per number"],
            0,
            "Every node is printed by exactly one call. Five nodes, five calls."),
    ],
    exercises=[
        _pex("calc-m5-show-1", "Print the sides the same way",
             "Finish `show` for a binary node: the operator, then the left side and "
             "the right side, each printed by `show` itself, all in brackets.",
             _c5(_C5_OP, _C5_TYPES, _C5_FACTORIES, _C5_SHOW, _C5_S3_MAIN),
             "  return `(${e.op} ${show(e.left)} ${show(e.right)})`;",
             [("", _C5_S3_OUT)],
             ["After the `if`, `e` is a `Binary`: it has `op`, `left` and `right`.",
              "The sides are trees. What prints a tree?",
              "A template literal: `(${…} ${…} ${…})`.",
              "`return `(${e.op} ${show(e.left)} ${show(e.right)})`;`"]),
        _pfix("calc-m5-show-fix1", "Ten minus four is not four minus ten",
              "Every tree prints with its sides the wrong way round. For `+` and `*` "
              "nobody would notice; `(- 4 10)` means something else entirely.",
              _c5(_C5_OP, _C5_TYPES, _C5_FACTORIES,
                  _C5_SHOW.replace("${show(e.left)} ${show(e.right)}",
                                   "${show(e.right)} ${show(e.left)}"),
                  _C5_S3_MAIN),
              _c5(_C5_OP, _C5_TYPES, _C5_FACTORIES, _C5_SHOW, _C5_S3_MAIN),
              [("", _C5_S3_OUT)],
              ["Which side does `(- 10 4)` print first?",
               "The left side of the tree is the left operand of the operator.",
               "`${show(e.left)} ${show(e.right)}`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why does `show` always finish, however deep the tree?",
            ["Each call is on a smaller tree, and every tree ends in numbers, where `show` returns without recursing",
             "TypeScript stops recursion after a fixed depth",
             "Because `show` uses a loop",
             "It does not always finish"],
            0,
            "Smaller each time, with a case that stops: the two things every "
            "recursive function needs."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — which way a chain leans.
# ---------------------------------------------------------------------------

_C5_S4 = _pstep(
    "lean", "Which way a chain leans",
    "`10 - 4 - 3` is `(10 - 4) - 3`: left-leaning trees, and counting nodes recursively.",
    """
Precedence decides between *different* operators. It says nothing about
`10 - 4 - 3`, where both are the same. There are two trees it could be:

```
(- (- 10 4) 3)       (10 - 4) - 3  =  3      ← what arithmetic means
(- 10 (- 4 3))       10 - (4 - 3)  =  9
```

Arithmetic says the first: operators of equal precedence are worked out **left
to right**. So a chain of subtractions builds a tree that leans to the left — the
first subtraction deepest, the last at the top:

```ts
binary("-", binary("-", num(10), num(4)), num(3))
```

This property is called **associativity**, and `+ - * /` are all
*left-associative*. For `+` and `*` it makes no difference to the answer. For `-`
and `/` it is the difference between 3 and 9, and between `100 / 10 / 2 = 5` and
`100 / (10 / 2) = 20`. Module 7's parser has to build the left-leaning tree, and
this is the step that says why.

### Counting nodes

One more recursive function, to get the shape into your hands:

```ts
function size(e: Expr): number {
  if (e.kind === "num") {
    return 1;
  }
  return 1 + size(e.left) + size(e.right);
}
```

A number is one node. A branch is one node — itself — plus everything on both
sides. Same shape as `show`: handle this node, trust the recursion for the rest.
The `1 +` is the part people forget, and it is the node you are standing on.
""",
    """
```
7 has 1 nodes
(+ 1 (* 2 3)) has 5 nodes
(- (- 10 4) 3) has 5 nodes
(/ (/ 100 10) 2) has 5 nodes
(- 10 (- 4 3)) has 5 nodes
```

The third and fifth trees have the same numbers, the same operators and the same
size. They do not have the same meaning. Only the third is `10 - 4 - 3`.
""",
    pitfalls=[
        "Right-leaning chains: `binary(\"-\", num(10), binary(\"-\", num(4), num(3)))` for `10 - 4 - 3`. It is `10 - (4 - 3)`, and evaluates to 9.",
        "Forgetting the `1 +` in `size`: the function then counts only numbers, and says `1 + 2` has two nodes.",
        "Assuming associativity only matters for weird operators. It is the everyday difference between `8 / 4 / 2 = 1` and `8 / (4 / 2) = 4`.",
        "Treating a chain as a special node with a list of operands. It works for `+`, and leaves `-` needing a rule about which operand is which.",
    ],
    warmup=[
        _pq("Which tree is `100 / 10 / 2`?",
            ["`(/ (/ 100 10) 2)` — equal operators work left to right, so the first division is deepest",
             "`(/ 100 (/ 10 2))`",
             "`(/ 100 10 2)`",
             "Either; division is associative"],
            0,
            "Left-associative. The other tree evaluates to 20, not 5."),
    ],
    exercises=[
        _pex("calc-m5-lean-1", "Count every node",
             "Finish `size` for a branch: the branch itself, plus every node on "
             "both sides.",
             _C5_FULL,
             "  return 1 + size(e.left) + size(e.right);",
             [("", _C5_S4_OUT)],
             ["A number is 1. What is a branch?",
              "Count the node you are on, then let `size` count each side.",
              "`return 1 + size(e.left) + size(e.right);`"]),
        _pfix("calc-m5-lean-fix1", "A chain that leans the wrong way",
              "The third tree is meant to be `10 - 4 - 3`, which is 3. It prints as "
              "`(- 10 (- 4 3))`, which is 9.",
              _C5_FULL.replace('binary("-", binary("-", num(10), num(4)), num(3)),',
                               'binary("-", num(10), binary("-", num(4), num(3))),', 1),
              _C5_FULL,
              [("", _C5_S4_OUT)],
              ["Equal operators are worked out left to right. Which subtraction happens first?",
               "The first one happens first, so it is deepest — on the LEFT of the second.",
               "The fifth tree is the right-leaning one on purpose; leave it.",
               "`binary(\"-\", binary(\"-\", num(10), num(4)), num(3))`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does associativity matter for `-` and `/` but not `+` and `*`?",
            ["`(a + b) + c` equals `a + (b + c)`, but `(a - b) - c` does not equal `a - (b - c)`",
             "Because `-` and `/` have higher precedence",
             "It matters for all four equally",
             "Because `+` and `*` are right-associative"],
            0,
            "The tree still leans left for `+` — it simply gives the same answer "
            "either way."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C5_BUILD_BLANK = "\n".join(p.rstrip("\n") + "\n" for p in (_C5_TYPES, _C5_FACTORIES, _C5_SHOW, _C5_SIZE)).rstrip("\n")

_C5_FINAL = _pch(
    "calc-m5-build", "Module 5 build — the tree, as a type", "Easy",
    "Write everything between the operator type and the list of trees.\n\n"
    "* `NumLit`, `Binary` and `Expr` — a `Binary` holds an operator and two "
    "`Expr`s\n"
    "* `num` and `binary` — the factories\n"
    "* `show` — prints a tree as `(op left right)`, a number as itself\n"
    "* `size` — counts every node\n\n"
    "The five trees at the bottom are given. The fifth leans right on purpose.",
    _C5_FULL,
    _C5_BUILD_BLANK,
    [("", _C5_S4_OUT)],
    ["Start with the types. `Binary` mentions `Expr`; that is allowed.",
     "Tags are `\"num\"` and `\"binary\"`; field order matters for nothing printed here, but match the type anyway.",
     "`show` and `size` have the same shape: an `if` for numbers that returns, then the branch case that recurses on both sides.",
     "`size` counts the node it is on: `1 + size(e.left) + size(e.right)`."],
)


_C5_REF_TREE = _C5_TYPES + "\n" + _C5_FACTORIES + "\n" + _C5_SHOW

_CALC_MODULES.append(_pmod(
    key="calc-tree", number=5, phase="parse",
    title="What a tree is",
    what="a type that refers to itself, and the shape `1 + 2 * 3` really has",
    goal="Define `Expr`, build trees by hand, and print them so their shape can be seen.",
    why=_C5_WHY,
    est_minutes=40,
    builds_on=["calc-token", "calc-scan-errors"],
    concepts=["syntax tree", "recursive types", "recursion", "base case",
              "precedence as shape", "associativity", "S-expressions"],
    deliverable="An `Expr` type that can describe any arithmetic expression, "
                "factories to build one, and `show`, which prints `1 + 2 * 3` as "
                "`(+ 1 (* 2 3))` — the output the parser will be judged by.",
    objectives=[
        "Explain why a flat list of tokens cannot hold precedence, and a tree can",
        "Declare a recursive discriminated union, and say what stops it being infinite",
        "Build the tree for an expression by hand, starting from the operation that happens last",
        "Write a recursive function over the tree, with a base case at the leaves",
        "Say why parentheses need no node in the tree",
        "Explain associativity, and build the left-leaning tree for `10 - 4 - 3`",
    ],
    brief=_C5_BRIEF,
    syntax=_C5_SYNTAX,
    steps=[_C5_S1, _C5_S2, _C5_S3, _C5_S4],
    final_build=_C5_FINAL,
    acceptance=[
        "`Expr` is a union of `NumLit` and `Binary`, and `Binary`'s sides are `Expr`s.",
        "`show(binary(\"+\", num(1), binary(\"*\", num(2), num(3))))` prints `(+ 1 (* 2 3))`.",
        "The tree for `(1 + 2) * 3` prints as `(* (+ 1 2) 3)` and contains no node for the brackets.",
        "The tree for `10 - 4 - 3` prints as `(- (- 10 4) 3)`.",
        "`{ kind: \"binary\", op: \"%\", left: num(1), right: num(2) }` does not compile.",
        "`calc.ts` still scans exactly as it did after module 4 — nothing reads a tree yet.",
    ],
    manual_test="""
There is no new command-line behaviour this module — the tree has no producer
yet. Add the types, factories and `show` to `calc.ts` above the main program, and
then, temporarily, at the very bottom:

```ts
console.log(show(binary("+", num(1), binary("*", num(2), num(3)))));
console.log(show(binary("-", binary("-", num(10), num(4)), num(3))));
```

```bash
echo '' | node calc.ts
```

After the `eof` token you should see `(+ 1 (* 2 3))` and `(- (- 10 4) 3)`. Now
break the type on purpose: change `left: Expr` to `left: NumLit` and run
`npx tsc --noEmit --strict calc.ts`. The second tree is refused — its left side
is a subtraction. Put it back, and delete the two test lines.
""",
    reference="""// calc.ts — module 5
//
// Phase 1's scanner, unchanged, plus the TREE the parser will build in module 6.
// Nothing produces an Expr yet: this module designs the data first, exactly as
// module 1 designed Token before any scanner existed.
import { readFileSync } from "node:fs";

""" + _C_TOKENS + """
// A syntax tree. A Binary holds two Exprs, so the type refers to itself; NumLit
// holds none, which is what lets every real tree end. Precedence is SHAPE here:
// in `1 + 2 * 3` the `*` sits underneath the `+`, so it must be worked out first.
// Parentheses have no node — the shape already says what they said.
""" + _C5_REF_TREE + """
type ScanResult = { ok: true; tokens: Token[] } | { ok: false; error: string };

function unexpected(ch: string, i: number): string {
  return `error: unexpected '${ch}' at 1:${i + 1}`;
}

""" + _C4_SCAN + """
const src = readFileSync(0, "utf8").trimEnd();
const result = scan(src);
if (result.ok) {
  for (const t of result.tokens) {
    console.log(JSON.stringify(t));
  }
} else {
  console.log(result.error);
}
""",
    stretch=[
        "Write `depth(e)`: the number of nodes on the longest path from the top to a leaf. What is the depth of `1 + 2 + 3 + 4`, and of `1 + (2 + (3 + 4))`? A parser that gets associativity wrong changes one of them.",
        "Write `infix(e)` — print a tree back as ordinary arithmetic, with brackets around every operation: `((10 - 4) - 3)`. Then try printing only the brackets that are needed. (It is harder than it looks, and it is the stretch module 18 comes back to.)",
        "Draw a tree sideways: `show` with indentation, one node per line, children indented two spaces further than their parent.",
        "Add a `leaves(e)` that returns an array of every number in the tree, left to right. The order it returns them in is the order they appeared in the source — why is that guaranteed?",
    ],
    glossary=[
        _pgloss("syntax tree", "A tree whose shape records how a piece of source is structured — which operation contains which. Also called an AST, an abstract syntax tree."),
        _pgloss("node", "One element of a tree. Here, a `NumLit` (a leaf) or a `Binary` (a branch with two children)."),
        _pgloss("recursive type", "A type that mentions itself, like `Binary`'s `left: Expr`. It needs at least one member that does not, or no value could ever be finished."),
        _pgloss("recursion", "A function calling itself on a smaller piece of the problem, with a base case that stops."),
        _pgloss("base case", "The case a recursive function handles without recursing — for trees, a leaf."),
        _pgloss("associativity", "Which way equal-precedence operators group. `+ - * /` are left-associative: `10 - 4 - 3` is `(10 - 4) - 3`."),
        _pgloss("S-expression", "Operator-first bracketed notation, `(+ 1 (* 2 3))`. Unambiguous, so it is how this project prints trees."),
    ],
    cheatsheet="""
```ts
// a node is a number, or an operator with two sub-trees
type NumLit = { kind: "num"; value: number };
type Binary = { kind: "binary"; op: Op; left: Expr; right: Expr };
type Expr = NumLit | Binary;

function num(value: number): NumLit { return { kind: "num", value: value }; }
function binary(op: Op, left: Expr, right: Expr): Binary {
  return { kind: "binary", op: op, left: left, right: right };
}

// recursion: handle this node, trust the call for the sides
function show(e: Expr): string {
  if (e.kind === "num") { return `${e.value}`; }            // base case
  return `(${e.op} ${show(e.left)} ${show(e.right)})`;
}
```

| Source | Tree |
|---|---|
| `1 + 2 * 3` | `(+ 1 (* 2 3))` — last operation on top |
| `(1 + 2) * 3` | `(* (+ 1 2) 3)` — no node for the brackets |
| `10 - 4 - 3` | `(- (- 10 4) 3)` — equal operators lean left |

| Symptom | Cause |
|---|---|
| `1 + 2 * 3` prints `(* (+ 1 2) 3)` | tree built in reading order, not operation order |
| `(- 4 10)` for ten minus four | `show` prints `right` before `left` |
| `size` says `1 + 2` has 2 nodes | forgot to count the branch itself |
""",
    self_check=[
        "Can you write `Expr` from memory, and say which member stops it being infinite?",
        "Can you build `8 / (6 - 2)` with the factories, starting from the operation that happens last?",
        "Can you explain why the tree for `(1 + 2) * 3` has no parentheses in it?",
        "Can you trace `show` on `(+ 1 (* 2 3))` and count the calls?",
        "Can you give the two trees `10 - 4 - 3` could be, their values, and which one arithmetic means?",
    ],
    review=[
        _pq("Why can't a list of tokens represent precedence?",
            ["`1 + 2 * 3` and `1 * 2 + 3` are the same kind of list; which operation contains which is not recorded anywhere",
             "Lists cannot hold numbers and operators together",
             "It can; the order of the list is the precedence",
             "Because tokens have no `kind`"],
            0,
            "The tree records containment. That is what precedence is."),
        _pq("`type Binary = { kind: \"binary\"; op: Op; left: NumLit; right: NumLit }` — what is wrong?",
            ["A sum could never contain another operation, so `1 + 2 * 3` has no tree",
             "Nothing",
             "`NumLit` is not declared yet",
             "Recursive types need `interface`"],
            0,
            "The sides must be `Expr`s — any expression at all."),
        _pq("Which tree is `(1 + 2) * 3`?",
            ["`binary(\"*\", binary(\"+\", num(1), num(2)), num(3))`",
             "`binary(\"+\", num(1), binary(\"*\", num(2), num(3)))`",
             "`binary(\"paren\", …)`",
             "`binary(\"*\", num(1), num(2), num(3))`"],
            0,
            "The `*` happens last, so it is on top."),
        _pq("Every recursive function over `Expr` in this module starts with `if (e.kind === \"num\")`. Why?",
            ["Numbers are the leaves — the case that returns without recursing, which is what makes the function finish",
             "Because numbers are the most common node",
             "TypeScript requires it",
             "To skip numbers"],
            0,
            "The base case. Without it the function would ask a leaf for its "
            "children — which here does not even compile."),
        _pq("Why is `10 - 4 - 3` built as `(- (- 10 4) 3)`?",
            ["Operators of equal precedence are worked out left to right, so the first subtraction is deepest",
             "Because the scanner reads left to right",
             "Because `-` has higher precedence than `-`",
             "It is built as `(- 10 (- 4 3))`"],
            0,
            "Left associativity. Module 7's parser has to produce exactly this."),
    ],
    milestone="The tree exists — as a type, as values you can build, and as "
              "`(+ 1 (* 2 3))` on your screen. Precedence has stopped being a rule "
              "you remember and become a shape. Module 6 writes the first code "
              "that produces one from tokens.",
))
