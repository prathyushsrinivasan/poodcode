# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 1 — What a token is.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`.
#
# THE CONSTRAINT THAT SHAPES THIS MODULE: it is first, so it may assume
# nothing. Every token in `_CALC_SCOPE_RULES` is off-limits except the three
# introduced here (`type `, `JSON.stringify(` and `.kind`), plus the ungated
# basics the primer covers — `const`, `function`, `return`, `if`, `===`,
# template literals and `console.log`.
#
# In particular there are NO arrays yet (module 2), no stdin (module 2), no
# `.slice`/`Number` (module 3), no `switch` (module 9) and no `never` (module
# 10). So the module cannot scan anything, and does not try to: it prints
# individual tokens that were built by hand. That is the right shape anyway —
# module 1 is where the token type is DESIGNED, and a scanner written before the
# token type is decided is a scanner you rewrite in module 3.
#
# A TRAP WORTH REMEMBERING: `_lint_scope` scans program TEXT, comments
# included. So no program in this file may contain the words `never` or `case `,
# or the strings `for (`, `[]`, `.length` — even inside a comment. Where the
# teaching text needs an ellipsis it uses the Unicode `…`, exactly as the Todo
# API's early modules do.
#
# WHY OPERATORS ARE ONE KIND WITH A PAYLOAD rather than one kind each: see step
# 2. It is the module's one real design argument and it is settled here because
# module 7 (precedence) is built on top of the answer.
# ---------------------------------------------------------------------------

_C1_WHY = (
    "A language processor is three transformations — text to tokens, tokens to "
    "a tree, tree to a value — and every one of them is written in terms of "
    "what a token is. Choose the token type badly and the damage is not local: "
    "the scanner gets an extra field nobody fills in, the parser grows an `if` "
    "for a case that cannot happen, and module 10's exhaustiveness check has "
    "nothing to check. Ten minutes of design here is the cheapest ten minutes "
    "in the project."
)

_C1_BRIEF = """
### The whole module in one line

Decide what a token is, write it down as a type the compiler will hold you to,
and print one as exactly the JSON the rest of the project passes around.

### Why start here and not with the scanner

The instinct is to start scanning, because a loop over characters feels like
real progress and a type declaration does not. Resist it for one module.

A scanner is twenty lines and you will write it next. But a scanner *produces*
tokens, so it cannot be written until you know what one is — and if you decide
that while writing the loop, you will decide it badly, because you will be
thinking about characters rather than about what the parser needs. The parser is
the customer here. Design for the customer.

### What a token has to answer

Take the smallest interesting input this project handles:

```
1 + 2
```

Five characters, and the scanner will turn them into four tokens: the number 1,
the operator `+`, the number 2, and a marker meaning *that was the end*. Look at
what those four have in common and what they do not.

| Token | What kind is it? | What does it carry? |
|---|---|---|
| `1` | a number | the value `1` |
| `+` | an operator | which operator, `+` |
| `2` | a number | the value `2` |
| — | end of input | nothing at all |

Every token answers the first question. **Only some answer the second, and they
answer it with different types** — a number carries a `number`, an operator
carries one of four symbols, and the end marker carries nothing. That asymmetry
is the entire design problem, and TypeScript has exactly the right tool for it.

### Why there is an end-of-input token

It looks like bookkeeping and it is not. Module 6's parser will repeatedly ask
"what is the next token?", and without a real token meaning *the end*, every one
of those questions has two answers — a token, or nothing — and every place that
asks has to handle both. One extra token kind now removes a `| undefined` from
roughly thirty lines of parser later.

This is the same trade the whole project keeps making: put the awkward case in
the data, not in the code that reads it.

### Why `type` and not `interface`

TypeScript will let you write either for a plain shape. This track uses `type`
everywhere and never mentions `interface` again, for two reasons: `type` also
describes things `interface` cannot — unions, which this module needs in about
four paragraphs' time — so there is one keyword to learn rather than two; and
`interface` silently allows *declaration merging*, where declaring it twice
combines the two instead of erroring. That is a feature for library authors and
a trap for everyone else.
"""

_C1_SYNTAX = [
    _syn(
        'type TokenKind = "number" | "op" | "eof";',
        "A union of **string literal types**. `TokenKind` now means \"one of "
        "exactly these three strings\" — not \"a string\".",
        """
type TokenKind = "number" | "op" | "eof";

const k: TokenKind = "op";
console.log(k);
""",
        "The `|` is read \"or\". Widening this to `string` would compile just as "
        "happily and would catch none of the typos this type exists to catch — "
        "which is the argument of step 1.",
    ),
    _syn(
        'type NumberToken = { kind: "number"; value: number };',
        "An object type where one field's type is a **single literal**. `kind` "
        "here is not \"some string\" — it is the string `\"number\"` and nothing "
        "else. That is what makes the union below discriminated.",
        """
type NumberToken = { kind: "number"; value: number };

const one: NumberToken = { kind: "number", value: 1 };
console.log(one.value);
""",
        "`{ kind: \"number\", value: 1 }` is a *value*; `{ kind: \"number\"; value: "
        "number }` is a *type*. They look almost identical on the page, which is "
        "the single most common source of confusion in this module. Types use "
        "`;` and name other types; values use `,` and hold data.",
    ),
    _syn(
        "type Token = NumberToken | OpToken | EofToken;",
        "A **union of object types**. A `Token` is any one of the three — and "
        "until you check which, you may only touch the fields all three have.",
        """
type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: "+" | "-" };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

const t: Token = { kind: "op", op: "+" };
console.log(t.kind);
""",
        "`t.kind` is fine on a bare `Token` because all three members have it. "
        "`t.value` is a compile error, because two of the three do not — and that "
        "error is the type doing its job, not getting in your way.",
    ),
    _syn(
        'if (t.kind === "number") { … }',
        "**Narrowing.** Compare the discriminant and TypeScript works out which "
        "member of the union you must be holding. Inside the braces, `t` is a "
        "`NumberToken` and `t.value` is available.",
        """
function describe(t: Token): string {
  if (t.kind === "number") {
    return `number ${t.value}`;
  }
  return "something else";
}
""",
        "This only works because every member has a `kind` field with a *literal* "
        "type. Declare `kind: string` instead and the comparison compiles, "
        "narrows nothing, and `t.value` stays an error — the design and the "
        "narrowing are the same decision.",
    ),
    _syn(
        "function numberToken(value: number): NumberToken { … }",
        "A factory: typed parameters, a declared return type, and one place that "
        "knows how a token of this kind is built.",
        """
function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

console.log(numberToken(12).value);
""",
        "Writing `: NumberToken` is optional — TypeScript would infer it — and "
        "you should write it anyway. An inferred return type reports a mistake "
        "at every *call site*; a declared one reports it once, on the line that "
        "is actually wrong.",
    ),
    _syn(
        "JSON.stringify(t)",
        "Turn a token into text. Every module from 2 onwards prints tokens this "
        "way, so it is worth seeing the exact output now.",
        """
const one: NumberToken = { kind: "number", value: 1 };
console.log(JSON.stringify(one));
// {"kind":"number","value":1}
""",
        "Keys come out in **insertion order**, not alphabetically — so `kind` "
        "first in the object literal means `kind` first in the output. That makes "
        "field order part of what these exercises compare, rather than a style "
        "choice.",
    ),
    _syn(
        "console.log(value)",
        "Print one line to stdout. This is the whole output mechanism for the "
        "project, and from module 2 the whole input mechanism is stdin.",
        """
console.log("number 1");
console.log(JSON.stringify({ kind: "eof" }));
""",
        "`console.log` on an object prints Node's debugging view — `{ kind: 'eof' "
        "}`, with single quotes and spaces — which is not JSON. Stringify "
        "whenever the output is meant to be data.",
    ),
]

_C1_S1 = _pstep(
    "kinds", "Name the kinds",
    "Read the language off the examples, and write the kinds down as literal types.",
    """
Open a new file, `calc.ts`. It will not read anything for another module; name
it that anyway so you are not renaming things later.

Before you type, list the kinds. The way to do that is to look at the inputs the
finished project has to handle and ask, for each character: *is this a new kind
of thing, or more of the previous thing?*

```
1 + 2 * 3
(1 + 2) * -3
let x = 4; x * x > 10
```

Phase 1 only needs the first line. Walking it: `1` is a number, `+` is an
operator, `2` is a number, `*` is an operator, `3` is a number, and then the
input runs out. So — three kinds:

```ts
type TokenKind = "number" | "op" | "eof";
```

Three, genuinely. The temptation is to add `"lparen"`, `"rparen"`, `"let"`,
`"identifier"` and `"semicolon"` now, while the project's full grammar is in
front of you. Do not. A kind you add today is a kind the scanner does not
produce, the parser does not consume, and every `if` you write between now and
module 8 has to skip. **Add a kind in the module that needs it** — parens in 8,
names and `let` in 12, `;` in 13.

### Why literal strings and not just `string`

This compiles too:

```ts
type TokenKind = string;
```

and it is worth understanding exactly what it costs you, because the difference
is the reason this project is written in TypeScript at all.

```ts
const k: TokenKind = "opp";      // with `string`: fine. Ships. Breaks in module 6.
```

With the literal union, that line is refused before the program runs, with an
error naming the three strings that were allowed. The typo is caught by the same
mechanism that will, in module 10, catch a whole missing branch of your
evaluator. It is the same idea at two sizes.
""",
    """
`calc.ts` declares `type TokenKind` with exactly three members, and this runs:

```ts
const k: TokenKind = "op";
console.log(k);
```

Now try `const bad: TokenKind = "operator";` and read the error before deleting
it. It should name all three allowed strings. If it does not complain at all,
you have written `string` somewhere.
""",
    pitfalls=[
        "Adding kinds for parentheses, `let` and identifiers now, because the project brief shows them. Every one of them is dead weight until the module that produces it — and a kind with no producer is a branch you write, test and maintain for nothing.",
        "Declaring `kind: string`. It compiles, it looks like a type, and it turns off both the typo check here and the narrowing in step 3. This is the single most consequential wrong turn available in module 1.",
        "Using one kind per operator (`\"plus\"`, `\"minus\"`, `\"star\"`, `\"slash\"`). Not wrong, but step 2 argues against it, and switching later means touching the scanner and the parser at once.",
    ],
    warmup=[
        _pq("The finished project handles `(1 + 2) * -3`, so parentheses are "
            "definitely a kind of token eventually. Why not add `\"lparen\"` and "
            "`\"rparen\"` to `TokenKind` right now?",
            ["Nothing produces or consumes them until module 8, so they would be branches that cannot happen",
             "A union may only have three members",
             "Parentheses are not tokens — the parser reads them straight from the text",
             "They would make `JSON.stringify` output non-deterministic"],
            0,
            "A kind that no scanner emits is a case every reader of a token still "
            "has to consider, forever, for nothing. The project adds parens in "
            "module 8 — in the same module that teaches the parser what to do with "
            "them, which is when the branch starts earning its keep."),
    ],
    exercises=[
        _pex("calc-m1-kind-1", "Complete the kinds",
             "The program uses all three token kinds, but `TokenKind` is one member "
             "short. Add the missing one — the marker that means the input ran out.",
             _plain("""
type TokenKind = "number" | "op" | "eof";

const a: TokenKind = "number";
const b: TokenKind = "op";
const c: TokenKind = "eof";

console.log(a);
console.log(b);
console.log(c);
"""),
             ' | "eof"',
             [("", "number\nop\neof")],
             ["Look at which of the three `const` lines has no matching member in "
              "the union.",
              "The third kind marks the end of the input, and the project spells it "
              "the way compilers usually do — three letters.",
              '`type TokenKind = "number" | "op" | "eof";`']),
        _pfix("calc-m1-kind-fix1", "The type that protected nothing",
              "This program compiles and prints `kind is opp`. It should print `kind "
              "is op`. The typo is the symptom — fix the cause, so that a typo like it "
              "is refused before the program runs.",
              _plain("""
type TokenKind = string;

const k: TokenKind = "opp";
console.log(`kind is ${k}`);
"""),
              _plain("""
type TokenKind = "number" | "op" | "eof";

const k: TokenKind = "op";
console.log(`kind is ${k}`);
"""),
              [("", "kind is op")],
              ["Correcting `\"opp\"` to `\"op\"` makes the output right and leaves the "
               "real problem in place — the next typo is just as welcome.",
               "`TokenKind` is declared as `string`, which allows every string there "
               "has ever been.",
               "Declare it as the union of the three literal strings, then fix the "
               "value: `type TokenKind = \"number\" | \"op\" | \"eof\";`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("What does `type TokenKind = \"number\" | \"op\" | \"eof\"` allow that "
            "`type TokenKind = string` does not?",
            ["Nothing — the literal union allows strictly less, which is the point",
             "It allows any string plus those three",
             "It allows the strings to be compared with `===`",
             "It allows `TokenKind` to be used as a field type"],
            0,
            "Types are about what you *forbid*. `string` permits every string ever "
            "typed, so it can reject nothing; the union permits three, so it rejects "
            "everything else — including `\"opp\"`, `\"Number\"`, and the empty string. "
            "A type that allows more is not more powerful, it is less useful."),
    ],
)

_C1_S2 = _pstep(
    "union", "One type per kind, joined into one union",
    "The payload problem, and the tool TypeScript has for exactly it.",
    """
`TokenKind` says what a token *is*. It says nothing about what a token *carries*
— and that is where the real design decision lives, because the three kinds
carry three different things:

| Kind | Carries |
|---|---|
| `number` | a `number` — the value |
| `op` | one of `+ - * /` |
| `eof` | nothing |

### The design that looks obvious and is wrong

One type, with the payloads optional:

```ts
type Token = {
  kind: TokenKind;
  value?: number;
  op?: string;
};
```

It compiles, it is short, and it makes every line of the next seventeen modules
slightly worse. Here is the whole problem in one line:

```ts
const nonsense: Token = { kind: "eof", value: 3, op: "+" };
```

That is an end-of-input token that is also the number 3 and also a plus sign.
Your type says it is fine. And on the other side of the same coin, when the
parser holds a token it knows is a number, `t.value` is still `number |
undefined` — so it has to check for a case the scanner can never produce, at
every single use.

**A type that permits states your program cannot produce is a type that makes
you handle them anyway.**

### The design that is right

Declare one type per kind, each with exactly the fields that kind has, and join
them with `|`:

```ts
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;
```

Now `{ kind: "eof", value: 3 }` is a compile error. `value` on a `NumberToken`
is `number`, not `number | undefined`. And — the part that matters most, and
which step 3 is entirely about — checking `kind` tells the compiler which member
you are holding.

This shape has a name: a **discriminated union**. The field they all share, with
a different literal type in each member, is the **discriminant**. It is the most
useful modelling tool TypeScript has, and this project is built out of four of
them.

### Why `op` is one kind carrying a symbol

The alternative is one kind per operator — `"plus"`, `"minus"`, `"star"`,
`"slash"` — which is what many hand-written scanners do. Both work. This project
groups them, for a reason that is entirely about module 7:

Precedence is a property of the *operator symbol*. Module 7 will ask "does this
operator bind tighter than that one?", and with a grouped kind that question is
one comparison against `t.op`. With four kinds it is a four-branch `if` in two
different functions, repeated every time the language gains an operator.

The rule generalises: **split kinds when the code that reads them differs, group
them when it does not.** Numbers and operators are read by completely different
code, so they are different kinds. `+` and `*` are read by the same code with a
different constant, so they are one kind and a payload.
""",
    """
`calc.ts` declares `Op`, three token types and the `Token` union, and all three
of these compile:

```ts
const one: Token = { kind: "number", value: 1 };
const star: Token = { kind: "op", op: "*" };
const end: Token = { kind: "eof" };
```

While all three of these are refused:

```ts
const bad1: Token = { kind: "eof", value: 3 };     // eof carries nothing
const bad2: Token = { kind: "number" };            // where is the value?
const bad3: Token = { kind: "op", op: "%" };       // not one of the four
```

Read `bad3`'s error in particular. It should name the four operators — which is
the same protection step 1 bought for `kind`, now applied to the payload.
""",
    pitfalls=[
        "Writing the union as one type with optional fields. It is shorter today and it costs you a `| undefined` check at every use, plus the ability to narrow at all. This is the decision the whole step exists to make.",
        "Typing `op` as `string` rather than `Op`. Then `{ kind: \"op\", op: \"%\" }` is a valid token, and the first thing that notices is module 7's precedence table quietly returning the wrong answer.",
        "Mixing up type syntax and value syntax. `{ kind: \"number\"; value: number }` describes a shape; `{ kind: \"number\", value: 1 }` is one. Semicolons and type names in the first, commas and data in the second.",
    ],
    warmup=[
        _pq("With `type Token = { kind: TokenKind; value?: number; op?: string }`, "
            "you are holding a `t` you have just checked is `t.kind === \"number\"`. "
            "What type is `t.value`?",
            ["`number | undefined` — the check on `kind` tells the compiler nothing about `value`",
             "`number` — checking the kind narrows the whole object",
             "`undefined` — optional fields are always undefined until assigned",
             "It is a compile error to read `value` at all"],
            0,
            "This is the cost of the optional-field design in one question. `kind` "
            "and `value` are unrelated as far as the type is concerned, so you get to "
            "write `t.value ?? 0` forever — handling a case your own scanner cannot "
            "produce. The union makes the two fields related, which is the whole "
            "trick."),
    ],
    exercises=[
        _pex("calc-m1-union-1", "Type the operator payload",
             "`OpToken` carries which operator it is, but the field has no type yet. "
             "Give it the one that allows exactly the four the language has.",
             _plain("""
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

const plus: OpToken = { kind: "op", op: "+" };

console.log(plus.kind);
console.log(plus.op);
"""),
             "op: Op",
             [("", "op\n+")],
             ["The type you want is already declared on the first line of the program.",
              "The field is named `op`, and its type is named `Op`.",
              '`type OpToken = { kind: "op"; op: Op };`']),
        _pex("calc-m1-union-2", "Join them into one type",
             "Three token types are declared. Join them into the single `Token` type "
             "the rest of the project will use.",
             _plain("""
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

const one: Token = { kind: "number", value: 1 };
const star: Token = { kind: "op", op: "*" };
const end: Token = { kind: "eof" };

console.log(one.kind);
console.log(star.kind);
console.log(end.kind);
"""),
             "NumberToken | OpToken | EofToken;",
             [("", "number\nop\neof")],
             ["A `Token` is any one of the three types above it.",
              "The `|` between two types means \"either of these\".",
              "`type Token = NumberToken | OpToken | EofToken;`"]),
        _pfix("calc-m1-union-fix1", "A token that carries the wrong thing",
              "This program is refused before it runs. One of the three tokens claims "
              "a kind whose type does not have the field it is trying to set. Read the "
              "error, then fix the value — not the types.",
              _plain("""
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

const one: Token = { kind: "number", value: 1 };
const star: Token = { kind: "op", value: 2 };
const end: Token = { kind: "eof" };

console.log(one.kind);
console.log(star.kind);
console.log(end.kind);
"""),
              _plain("""
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

const one: Token = { kind: "number", value: 1 };
const star: Token = { kind: "op", op: "*" };
const end: Token = { kind: "eof" };

console.log(one.kind);
console.log(star.kind);
console.log(end.kind);
"""),
              [("", "number\nop\neof")],
              ["The error is on the `star` line, and it mentions a field that "
               "`OpToken` does not declare.",
               "An operator token carries *which operator it is*, not a numeric value.",
               '`const star: Token = { kind: "op", op: "*" };`'],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("What makes a union of object types *discriminated*?",
            ["Every member has a field of the same name whose type is a different literal",
             "Every member has a different number of fields",
             "It was declared with `type` rather than `interface`",
             "The members are listed in alphabetical order"],
            0,
            "The shared field with per-member literal types is the discriminant, and "
            "it is what lets `t.kind === \"number\"` tell the compiler which member "
            "you hold. Without it — say `kind: string` in every member — you have a "
            "union, but comparing the field narrows nothing."),
        _pq("Why does this project use one `op` kind carrying a symbol rather than "
            "four kinds, one per operator?",
            ["Precedence is a property of the symbol, so module 7 compares one field instead of branching four ways",
             "Four kinds would exceed the number of members a union may have",
             "`JSON.stringify` cannot represent four kinds",
             "Four kinds would make the scanner slower to run"],
            0,
            "Split kinds when different code reads them; group them when the same "
            "code reads them with a different constant. `+` and `*` go through "
            "identical parser and evaluator paths with one value changed, so they are "
            "one kind — while numbers and operators are read by entirely different "
            "code, so they are not."),
    ],
)

_C1_S3 = _pstep(
    "narrow", "Ask a token what it is",
    "Checking `kind` is not just an `if` — it changes the type of the thing you are holding.",
    """
Here is the payoff. Write a function that turns any token into a description:

```ts
function describe(t: Token): string {
  if (t.kind === "number") {
    return `number ${t.value}`;
  }
  if (t.kind === "op") {
    return `operator ${t.op}`;
  }
  return "end of input";
}
```

Read what happened to `t` on the way down.

**On the first line of the body**, `t` is a `Token` — one of three things. Try
`t.value` here and it is a compile error: two of the three members have no such
field, and the compiler will not guess.

**Inside the first `if`**, `t` is a `NumberToken`. Not "probably" — the compiler
has worked it out from the comparison, and `t.value` is a plain `number` with no
`undefined` in sight. This is **narrowing**, and it is the entire reason step 2
insisted on the discriminated union.

**Inside the second `if`**, `t` is an `OpToken`, so `t.op` is available and
`t.value` is not.

**On the last line**, `t` is an `EofToken` — the only member left. You did not
tell the compiler that; it subtracted the two you handled from the three that
existed. Hover it in your editor and confirm, because that subtraction is the
mechanism module 10 turns into a permanent guarantee.

### The thing to actually notice

Nothing above is a runtime check that the compiler happens to tolerate. The
`if` and the type are the same statement, read twice: once by Node, which
compares two strings, and once by the compiler, which uses the comparison to
decide what `t` is on each branch. When people say TypeScript "understands your
control flow", this is the thing they mean, and it is worth more than every
other feature in the language put together.

### What breaks it

Narrowing on `kind` works because of three decisions, and losing any one of them
loses the narrowing:

- every member has the field (so the comparison is legal at all);
- the field's type is a **literal** in each member (so the comparison is
  informative);
- the literals are **different** (so the comparison is decisive).

Declare `kind: string` in the members and all three go. The `if` still compiles.
It just tells the compiler nothing, and `t.value` stays an error inside it —
which is a confusing five minutes if you do not know why.
""",
    """
`node calc.ts` runs and prints:

```
number 12
operator *
end of input
```

Then try adding `console.log(t.value)` as the first line of `describe`'s body,
before any `if`. It must be refused, with an error saying `value` does not exist
on `OpToken`. If it compiles, `t` is not the union you think it is.
""",
    pitfalls=[
        "Reading a payload before narrowing. `t.value` at the top of the function is an error, and it is the *correct* error — the token might be an `eof`. Move the read inside the branch that proved which kind it is.",
        "Reaching for `as NumberToken` to make that error go away. An assertion switches off the check rather than satisfying it, and the first token it lies about is a crash in module 9 with no clue where it came from.",
        "Comparing against a string that is not one of the kinds — `t.kind === \"operator\"`. TypeScript flags this as a comparison that can never be true, which is a small gift you only get because `kind` has literal types.",
        "Describing an operator with `t.kind` instead of `t.op`. It compiles, because both are strings — and it prints `operator op` for every operator in the language.",
    ],
    warmup=[
        _pq("Inside `if (t.kind === \"number\") { … }`, what type does the compiler "
            "give `t`?",
            ["`NumberToken`", "`Token`", "`TokenKind`", "`NumberToken | undefined`"],
            0,
            "The comparison rules out the two members whose `kind` cannot be "
            "`\"number\"`, leaving exactly one. That is why `t.value` is a plain "
            "`number` inside the braces and an error outside them."),
    ],
    exercises=[
        _pex("calc-m1-narrow-1", "Check the discriminant",
             "`describe` is missing the comparison that tells the compiler it is "
             "holding a number token. Fill it in.",
             _plain("""
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

function describe(t: Token): string {
  if (t.kind === "number") {
    return `number ${t.value}`;
  }
  if (t.kind === "op") {
    return `operator ${t.op}`;
  }
  return "end of input";
}

console.log(describe({ kind: "number", value: 12 }));
console.log(describe({ kind: "op", op: "*" }));
console.log(describe({ kind: "eof" }));
"""),
             't.kind === "number"',
             [("", "number 12\noperator *\nend of input")],
             ["The next line reads `t.value`, so this branch has to have proved `t` "
              "is a `NumberToken`.",
              "Compare the shared field against one of the three literal strings, "
              "with `===`.",
              '`if (t.kind === "number") {`']),
        _pex("calc-m1-narrow-2", "Read the payload",
             "The operator branch has narrowed `t` to an `OpToken`, so the field "
             "saying *which* operator it is can be read. Print it.",
             _plain("""
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

function describe(t: Token): string {
  if (t.kind === "number") {
    return `number ${t.value}`;
  }
  if (t.kind === "op") {
    return `operator ${t.op}`;
  }
  return "end of input";
}

console.log(describe({ kind: "op", op: "+" }));
console.log(describe({ kind: "number", value: 7 }));
"""),
             "${t.op}",
             [("", "operator +\nnumber 7")],
             ["Inside this `if`, `t` is an `OpToken` — look at what field that type "
              "declares.",
              "It is not `t.kind`, which would print the word `op` for every "
              "operator.",
              "`` return `operator ${t.op}`; ``"]),
        _pfix("calc-m1-narrow-fix1", "Every operator describes itself as `op`",
              "This program compiles cleanly and prints the wrong thing: every "
              "operator comes out as `operator op`. Expected output is `operator *`, "
              "`operator +`, `number 3`. Fix it.",
              _plain("""
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

function describe(t: Token): string {
  if (t.kind === "number") {
    return `number ${t.value}`;
  }
  if (t.kind === "op") {
    return `operator ${t.kind}`;
  }
  return "end of input";
}

console.log(describe({ kind: "op", op: "*" }));
console.log(describe({ kind: "op", op: "+" }));
console.log(describe({ kind: "number", value: 3 }));
"""),
              _plain("""
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

function describe(t: Token): string {
  if (t.kind === "number") {
    return `number ${t.value}`;
  }
  if (t.kind === "op") {
    return `operator ${t.op}`;
  }
  return "end of input";
}

console.log(describe({ kind: "op", op: "*" }));
console.log(describe({ kind: "op", op: "+" }));
console.log(describe({ kind: "number", value: 3 }));
"""),
              [("", "operator *\noperator +\nnumber 3")],
              ["Both `t.kind` and `t.op` are strings, so the compiler is happy with "
               "either. Only one of them says which operator this is.",
               "`t.kind` is the same value — `\"op\"` — for every operator token in "
               "the language. That is what is being printed.",
               "`` return `operator ${t.op}`; ``"]),
    ],
    quiz=[
        _pq("Why is `t.value` a compile error at the top of `describe`, before any "
            "`if`?",
            ["`t` is the whole union, and two of its three members have no `value` field",
             "`value` is optional, so it must be checked against `undefined` first",
             "Fields may only be read inside an `if` in TypeScript",
             "It is not an error — `t.value` is `number | undefined` there"],
            0,
            "On a union you may only touch what every member has. `kind` qualifies; "
            "`value` does not, because an `eof` token genuinely does not have one. "
            "The fix is to narrow — not to make the field optional, which would put "
            "the `undefined` back everywhere."),
        _pq("You change every member to declare `kind: string` instead of a literal. "
            "What happens to `if (t.kind === \"number\") { return t.value; }`?",
            ["It still compiles as a comparison, narrows nothing, and `t.value` becomes an error",
             "Nothing changes — the comparison narrows either way",
             "The comparison itself becomes a compile error",
             "`t.value` becomes `number | undefined`"],
            0,
            "Narrowing needs the discriminant's type to be a literal, so that ruling "
            "out `\"number\"` rules out a member. With `string` in every member, the "
            "comparison is just a string comparison — true at runtime, meaningless to "
            "the compiler, and the payload stays out of reach."),
    ],
)

_C1_S4 = _pstep(
    "json", "Build them in one place, print them the way the scanner will",
    "Factories, and the exact output text every module after this one produces.",
    """
Two small things close the module out.

### Factories

You are about to write a scanner that produces hundreds of these. Typing the
object literal at each site is how `kind: "numbrer"` gets in, and how one token
ends up built slightly differently from the rest. Put each one in a function:

```ts
function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

function opToken(op: Op): OpToken {
  return { kind: "op", op: op };
}

function eofToken(): EofToken {
  return { kind: "eof" };
}
```

Three things to notice.

**The parameters are typed.** `opToken("%")` is now a compile error rather than
a token the parser meets in module 7 and has no branch for.

**The return types are declared.** Optional — TypeScript would infer them — and
worth writing anyway. A mistake inside the function is then reported *there*,
instead of at each of the fifty places module 3 calls it from.

**`eofToken()` takes nothing and looks pointless.** Call it anyway. When module
16 gives every token a line and column, this function grows two parameters, and
the fifty call sites that went through it get the change for free.

> **On `{ kind: "number", value: value }`.** TypeScript has a shorthand —
> `{ kind: "number", value }` — and it is what you would normally write. This
> project spells it out for now, because the longhand makes it obvious that the
> *field* `value` and the *parameter* `value` are two different things that
> happen to share a name. Once that is second nature, use the shorthand.

### The output text

Every module from here prints tokens with `JSON.stringify`, and the exercises
compare that text exactly:

```ts
console.log(JSON.stringify(numberToken(1)));   // {"kind":"number","value":1}
console.log(JSON.stringify(opToken("+")));     // {"kind":"op","op":"+"}
console.log(JSON.stringify(eofToken()));       // {"kind":"eof"}
```

`kind` comes first because you wrote it first. `JSON.stringify` emits keys in
**insertion order**, not alphabetically, so these two are the same value and
different text:

```ts
{ kind: "number", value: 1 }   // {"kind":"number","value":1}
{ value: 1, kind: "number" }   // {"value":1,"kind":"number"}
```

Both are valid `NumberToken`s and both type-check. One matches what every
exercise in this project expects and one does not. Build the literal with `kind`
first — inside the factory, once — and the question never comes up again.
""",
    """
`node calc.ts` prints exactly these four lines — the token list for `1 + 2`,
which is precisely what module 2's scanner will produce from the text:

```
{"kind":"number","value":1}
{"kind":"op","op":"+"}
{"kind":"number","value":2}
{"kind":"eof"}
```

Character for character: no spaces after the colons, `kind` first in every
object. If yours differs, you are either printing the object rather than the
JSON, or a factory builds its literal in a different order.
""",
    pitfalls=[
        "`console.log(t)` instead of `console.log(JSON.stringify(t))`. The first prints `{ kind: 'number', value: 1 }` — close enough to JSON to be mistaken for it at a glance, and different in every character that matters.",
        "Building the literal with the payload first. It type-checks, and the output text no longer matches what every later module expects.",
        "Skipping `eofToken()` because a function with no parameters that returns a constant looks like ceremony. Module 16 adds a position to every token, and that is the module where the fifty inline `{ kind: \"eof\" }` literals become an afternoon.",
        "Leaving the return types off the factories. It compiles, and it moves every future error away from the line that caused it.",
    ],
    warmup=[
        _pq("`const t: NumberToken = { value: 1, kind: \"number\" };` — what does "
            "`JSON.stringify(t)` print?",
            ['{"value":1,"kind":"number"}',
             '{"kind":"number","value":1}',
             "{ value: 1, kind: 'number' }",
             "The order is unspecified and may vary between runs"],
            0,
            "Insertion order, exactly as written. The annotation `: NumberToken` says "
            "which fields must be present; it says nothing about the order you wrote "
            "them in, and `stringify` follows the object rather than the type."),
    ],
    exercises=[
        _pex("calc-m1-json-1", "Declare what the factory returns",
             "`numberToken` builds the right object but does not say what it hands "
             "back. Add the return type annotation.",
             _plain("""
type NumberToken = { kind: "number"; value: number };

function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

console.log(JSON.stringify(numberToken(1)));
console.log(JSON.stringify(numberToken(42)));
"""),
             ": NumberToken",
             [("", '{"kind":"number","value":1}\n{"kind":"number","value":42}')],
             ["The return type goes after the parameter list's closing bracket.",
              "A colon, then the name of the type the function hands back.",
              "`function numberToken(value: number): NumberToken {`"]),
        _pex("calc-m1-json-2", "Print it as data",
             "The program prints Node's debugging view of each token. Print the JSON "
             "the rest of the project passes around instead.",
             _plain("""
type Op = "+" | "-" | "*" | "/";

type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

function opToken(op: Op): OpToken {
  return { kind: "op", op: op };
}

function eofToken(): EofToken {
  return { kind: "eof" };
}

console.log(JSON.stringify(opToken("*")));
console.log(JSON.stringify(eofToken()));
"""),
             "JSON.stringify(opToken(\"*\"))",
             [("", '{"kind":"op","op":"*"}\n{"kind":"eof"}')],
             ["`console.log(opToken(\"*\"))` prints Node's view of the object, quotes "
              "and all — but not JSON.",
              "There is a built-in that turns a value into JSON text, and the second "
              "line already uses it.",
              '`console.log(JSON.stringify(opToken("*")));`']),
        _pfix("calc-m1-json-fix1", "The token comes out back to front",
              "This program compiles and every token it builds is a perfectly valid "
              "`NumberToken`. The output text is still wrong: this project puts `kind` "
              "first in every token. Fix it.",
              _plain("""
type NumberToken = { kind: "number"; value: number };

function numberToken(value: number): NumberToken {
  return { value: value, kind: "number" };
}

console.log(JSON.stringify(numberToken(1)));
console.log(JSON.stringify(numberToken(2)));
"""),
              _plain("""
type NumberToken = { kind: "number"; value: number };

function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

console.log(JSON.stringify(numberToken(1)));
console.log(JSON.stringify(numberToken(2)));
"""),
              [("", '{"kind":"number","value":1}\n{"kind":"number","value":2}')],
              ["The type is fine and the values are fine. Look only at the output "
               "text.",
               "`JSON.stringify` follows the order the fields were inserted, not the "
               "order the type declares them in.",
               '`return { kind: "number", value: value };`']),
    ],
    quiz=[
        _pq("Why declare `: NumberToken` as `numberToken`'s return type when "
            "TypeScript can infer it?",
            ["A mistake inside the function is then reported there, instead of at every place that calls it",
             "Without it the function returns `any`",
             "Inference does not work on object literals",
             "It is required for `JSON.stringify` to emit the fields in order"],
            0,
            "Inference is accurate but it propagates: get the body wrong and the "
            "inferred type quietly changes, so the errors surface wherever the result "
            "is *used* — which, by module 3, is fifty places. A declared return type "
            "pins the contract at the definition."),
    ],
)

_C1_FINAL = _pch(
    "calc-m1-build", "Module 1 build — the token", "Easy",
    "Put the module together. Declare `Op`, the three token types and the `Token` "
    "union; write the three factories `numberToken`, `opToken` and `eofToken`; and "
    "write `describe(t)` returning `number <value>`, `operator <op>` or `end of "
    "input`.\n\n"
    "Everything below the blank is already written for you — it prints the token "
    "list for `1 + 2`, first described and then as JSON. That is exactly what "
    "module 2's scanner will produce from the text.",
    _plain("""
type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

function opToken(op: Op): OpToken {
  return { kind: "op", op: op };
}

function eofToken(): EofToken {
  return { kind: "eof" };
}

function describe(t: Token): string {
  if (t.kind === "number") {
    return `number ${t.value}`;
  }
  if (t.kind === "op") {
    return `operator ${t.op}`;
  }
  return "end of input";
}

console.log(describe(numberToken(1)));
console.log(describe(opToken("+")));
console.log(describe(numberToken(2)));
console.log(describe(eofToken()));
console.log(JSON.stringify(numberToken(1)));
console.log(JSON.stringify(opToken("+")));
console.log(JSON.stringify(eofToken()));
"""),
    """type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

function opToken(op: Op): OpToken {
  return { kind: "op", op: op };
}

function eofToken(): EofToken {
  return { kind: "eof" };
}

function describe(t: Token): string {
  if (t.kind === "number") {
    return `number ${t.value}`;
  }
  if (t.kind === "op") {
    return `operator ${t.op}`;
  }
  return "end of input";
}""",
    [("", "number 1\noperator +\nnumber 2\nend of input\n"
          '{"kind":"number","value":1}\n{"kind":"op","op":"+"}\n{"kind":"eof"}')],
    ["Four things go in the blank: `Op`, the three token types plus the `Token` "
     "union, the three factories, and `describe`.",
     "Each token type pins `kind` to a single literal string — that is what makes "
     "`describe`'s `if`s narrow.",
     "`describe` checks `t.kind` twice and returns `\"end of input\"` on the way "
     "out, because `EofToken` is the only member left by then.",
     "Field order inside each factory decides the JSON: build `kind` first."],
)

_CALC_MODULES.append(_pmod(
    key="calc-token", number=1, phase="scan",
    title="What a token is",
    what="the token union, and why a `kind` field beats an optional payload",
    goal="Define the `Token` type as a discriminated union, and produce tokens as "
         "exactly the JSON the rest of the project passes around.",
    why=_C1_WHY,
    est_minutes=40,
    builds_on=[],
    concepts=["string literal types", "discriminated union", "narrowing",
              "factory functions", "JSON.stringify", "insertion order"],
    objectives=[
        "Derive a set of token kinds from the inputs a language has to handle",
        "Explain what a union of string literals forbids that `string` does not",
        "Model per-kind payloads as a discriminated union rather than optional fields",
        "Narrow a union by comparing its discriminant, and say why that works",
        "Decide when to split a kind and when to group it behind a payload",
        "Write factory functions with typed parameters and declared return types",
        "Predict the exact JSON text a token produces, including key order",
    ],
    deliverable="A `Token` type the compiler enforces, three factories that build "
                "one of each kind, and a `describe` that reads each one's payload "
                "safely.",
    brief=_C1_BRIEF,
    syntax=_C1_SYNTAX,
    steps=[_C1_S1, _C1_S2, _C1_S3, _C1_S4],
    final_build=_C1_FINAL,
    acceptance=[
        "`calc.ts` declares `Token` as a union of three types, each pinning `kind` "
        "to a single literal string.",
        "`{ kind: \"eof\", value: 3 }` is refused before the program runs.",
        "`opToken(\"%\")` is refused before the program runs.",
        "Inside `if (t.kind === \"number\")`, `t.value` is a `number` — with no "
        "`undefined` and no `as`.",
        "`JSON.stringify(numberToken(1))` gives `{\"kind\":\"number\",\"value\":1}` — "
        "that exact text, `kind` first.",
    ],
    reference="""// calc.ts — module 1
//
// The token type, designed before the scanner that produces it. Three kinds,
// because `1 + 2` needs three and nothing more: a number, an operator, and a
// marker meaning the input ran out. Parens arrive in module 8, names and `let`
// in module 12 — each in the module that also teaches the parser to read them.

type Op = "+" | "-" | "*" | "/";

// One type per kind, each carrying exactly what that kind carries. `kind` is a
// LITERAL type in each of them, not `string` — that is what makes the union
// below discriminated, and what makes `describe` able to narrow.
type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

// Factories rather than inline literals: one place that decides field order
// (which is output order — see step 4), and one place to change in module 16
// when every token grows a line and column.
function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

function opToken(op: Op): OpToken {
  return { kind: "op", op: op };
}

// Takes nothing today. Takes a position in module 16, and every site that calls
// it gets that change without being touched.
function eofToken(): EofToken {
  return { kind: "eof" };
}

// Narrowing: after the two comparisons the compiler knows `t` must be an
// EofToken, so the final return needs no check of its own. Module 10 turns that
// subtraction into a guarantee the compiler enforces forever.
function describe(t: Token): string {
  if (t.kind === "number") {
    return `number ${t.value}`;
  }
  if (t.kind === "op") {
    return `operator ${t.op}`;
  }
  return "end of input";
}

// The token list for `1 + 2`, built by hand. Module 2 produces this same list
// from the text itself.
console.log(describe(numberToken(1)));
console.log(describe(opToken("+")));
console.log(describe(numberToken(2)));
console.log(describe(eofToken()));
console.log(JSON.stringify(numberToken(1)));
console.log(JSON.stringify(opToken("+")));
console.log(JSON.stringify(eofToken()));
""",
    stretch=[
        "Add `\"lparen\"` and `\"rparen\"` kinds, then try to justify them from anything module 1 through 7 does. Delete them again — module 8 is where they earn their place.",
        "Rewrite the union with four operator kinds instead of one `op` kind, and write the function that answers \"does this bind tighter than that?\" both ways. The comparison is the argument in step 2, made concrete.",
        "Try `type Token = { kind: TokenKind; value?: number; op?: Op }` and rewrite `describe` against it. Count the `undefined` checks you now need for cases no scanner could ever produce.",
        "Declare `interface Token` twice in one file with different fields, and watch them merge silently rather than error. That is the trap the brief mentioned.",
    ],
    glossary=[
        _pgloss("token", "The smallest meaningful piece of a program's text — a number, an operator, a name. What a scanner produces."),
        _pgloss("string literal type", "A type whose only value is one specific string. `\"number\"` as a type allows exactly the string `\"number\"`."),
        _pgloss("union", "`A | B` — a type whose values are those of either member. On a bare union you may only touch what every member has."),
        _pgloss("discriminated union", "A union whose members share a field with a different literal type in each, so comparing that field identifies the member."),
        _pgloss("discriminant", "That shared field. Here it is `kind`."),
        _pgloss("narrowing", "The compiler reducing a value's type on a branch, from what a check on that branch proved. `t.kind === \"op\"` narrows `Token` to `OpToken`."),
        _pgloss("payload", "The per-kind data a token carries beyond its kind — `value` on a number, `op` on an operator, nothing on an eof."),
        _pgloss("eof", "End of input. A real token rather than an absence, so the parser never has to ask whether a token exists."),
        _pgloss("insertion order", "The order keys were added to an object, which is the order `JSON.stringify` writes them out in."),
    ],
    cheatsheet="""
```ts
// Kinds as literal strings — allows exactly these three, nothing else
type Op = "+" | "-" | "*" | "/";

// One type per kind, each carrying what that kind carries
type NumberToken = { kind: "number"; value: number };
type OpToken     = { kind: "op"; op: Op };
type EofToken    = { kind: "eof" };

// The discriminated union
type Token = NumberToken | OpToken | EofToken;

// Narrowing: check the discriminant, get the payload
if (t.kind === "number") {
  t.value;        // number   — no `undefined`, no `as`
}

// Factories: typed in, declared out, field order decided once
function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

// The output text these exercises compare
JSON.stringify(numberToken(1));   // {"kind":"number","value":1}
JSON.stringify(opToken("+"));     // {"kind":"op","op":"+"}
JSON.stringify(eofToken());       // {"kind":"eof"}
```

| Want | Write | Not |
|---|---|---|
| A fixed set of kinds | `type K = "a" \\| "b"` | `type K = string` |
| Per-kind data | a union of object types | one type with `value?`, `op?` |
| The payload | narrow first, then read | `(t as NumberToken).value` |
| JSON text | `JSON.stringify(t)` | `console.log(t)` |
| `kind` first in the output | build the literal `kind` first | rely on the type's field order |
""",
    self_check=[
        "Can you name the three token kinds and the part of `1 + 2` that produces each?",
        "Can you say what `string` allows that `\"number\" | \"op\" | \"eof\"` does not, and why allowing less is the point?",
        "Can you give the concrete cost of modelling payloads as optional fields, in the parser you have not written yet?",
        "Can you state the three properties a discriminant needs for narrowing to work?",
        "Can you explain why `+` and `*` share a kind while a number and an operator do not?",
        "Can you predict the exact JSON text for each of the three token kinds, key order included?",
    ],
    review=[
        _pq("Which is the strongest reason not to add a `\"lparen\"` kind in module 1?",
            ["No module before 8 produces or consumes one, so it would be a branch every reader has to skip",
             "Parentheses are handled by the scanner without becoming tokens",
             "A union may not have more than three members",
             "It would change the JSON output of the other kinds"],
            0,
            "The rule the whole track runs on: add the thing in the module that needs "
            "it. A kind with no producer still has to be considered by everything that "
            "reads a token — and it will be half-supported until module 8 arrives to "
            "finish the job properly."),
        _pq("`const t: Token = { kind: \"eof\", value: 3 };` — why is this refused?",
            ["`EofToken` declares no `value` field, and `kind: \"eof\"` picks that member",
             "`value` must be optional to appear on any token",
             "`Token` is a union, and unions reject all object literals",
             "It is not refused — `value` is simply ignored"],
            0,
            "The literal `\"eof\"` selects `EofToken` as the member being built, and "
            "that member has exactly one field. This is the payoff of the union over "
            "optional fields: a state your scanner can never produce is one your type "
            "will not let you write down."),
        _pq("`describe` handles `\"number\"` and `\"op\"`, then returns `\"end of "
            "input\"` with no check. What is `t`'s type on that last line?",
            ["`EofToken` — the compiler subtracted the two members already handled",
             "`Token` — narrowing only applies inside the `if` bodies",
             "`unknown` — the compiler cannot tell outside a check",
             "`EofToken | undefined`"],
            0,
            "Each `if` that returns removes a member from what can still be flowing "
            "past it, so by the last line exactly one is left. Module 10 makes the "
            "compiler *prove* that leftover is empty when it should be — which is how "
            "adding a token kind becomes a compile error rather than a bug report."),
    ],
    milestone="You have the type every other module in this project is written in "
              "terms of — and the modelling tool, the discriminated union, that "
              "the tree in module 5 and the values in module 14 are both built "
              "out of.",
))
