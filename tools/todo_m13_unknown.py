# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 13 — `unknown` at the boundary.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses modules 10-12's program pieces.
#
# THE PIVOT OF THE TRACK. Every module since 9 has trusted `JSON.parse`, and
# said so. This is the module that stops. The roadmap's worry was that it could
# not be taught as "spot the error", because `any` is silent — and module 11 set
# up the answer: `changesFrom(data: any)` names the hole in its signature, and
# changing that one word to `unknown` turns every line that trusted the body
# into a compile error. Those errors are a MAP of everywhere the API assumed the
# client told the truth.
#
# TYPES HERE, VALUES IN 14. This module checks the *shape* of what was parsed —
# an object, a string title, a boolean done. It does not check what the values
# SAY: `{"title":""}` is a string, so it is still accepted, and module 14 is where
# an empty title is refused and the error names the field. The split is the
# design: "is it the right kind of thing?" is a question the type system can
# help with; "is it an acceptable one?" is a rule of this application.
#
# A BARE 400 ARRIVES HERE, not in 14. When narrowing fails the compiler insists
# on an answer, and a body of the wrong shape is the client's fault, so it is a
# 4xx: `400 {"error":"invalid_body"}`. Module 14 replaces the bare 400 with one
# that names the field. Module 9's status table was corrected to say 13.
#
# `not json` IS STILL A 500. `JSON.parse` throws on text that is not JSON, and
# no amount of checking the RESULT helps, because there is no result. Catching
# needs `try`/`catch`, gated at 16. The module says so plainly.
#
# THE GRADABLE BUGS split cleanly: the whole point of `unknown` is that most
# mistakes are now COMPILE errors, so one `fix` is deliberately compile-time (a
# property read without an `in` check — the verifier lists it, as intended);
# the runtime ones are the checks `unknown` cannot make for you — `typeof null`
# being "object", an array being an object, and the old trusting route itself.
# ---------------------------------------------------------------------------

_M13_OBJECT = """function objectFrom(data: unknown): object | undefined {
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    return undefined;
  }
  return data;
}
"""

_M13_TITLE = """function titleFrom(data: unknown): string | undefined {
  const obj = objectFrom(data);
  if (obj === undefined || !("title" in obj) || typeof obj.title !== "string") {
    return undefined;
  }
  return obj.title;
}
"""

_M13_CHANGES = """function changesFrom(data: unknown): Partial<Todo> | undefined {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return undefined;
  }
  const changes: Partial<Todo> = {};
  if ("title" in obj) {
    if (typeof obj.title !== "string") {
      return undefined;
    }
    changes.title = obj.title;
  }
  if ("done" in obj) {
    if (typeof obj.done !== "boolean") {
      return undefined;
    }
    changes.done = obj.done;
  }
  return changes;
}
"""

_M13_POST_OLD = """    const body = await readBody(req);
    const data = JSON.parse(body);
    const todo = addTodo(data.title);
    send(res, 201, todo);"""

_M13_POST_NEW = """    const body = await readBody(req);
    const data: unknown = JSON.parse(body);
    const title = titleFrom(data);
    if (title === undefined) {
      send(res, 400, { error: "invalid_body" });
      return;
    }
    const todo = addTodo(title);
    send(res, 201, todo);"""

_M13_PATCH_OLD = """    const body = await readBody(req);
    const data = JSON.parse(body);
    const updated = updateTodo(todo, changesFrom(data));
    send(res, 200, updated);"""

_M13_PATCH_NEW = """    const body = await readBody(req);
    const data: unknown = JSON.parse(body);
    const changes = changesFrom(data);
    if (changes === undefined) {
      send(res, 400, { error: "invalid_body" });
      return;
    }
    const updated = updateTodo(todo, changes);
    send(res, 200, updated);"""

assert _M12_HANDLER.count(_M13_POST_OLD) == 1 and _M12_HANDLER.count(_M13_PATCH_OLD) == 1
_M13_HANDLER = _M12_HANDLER.replace(_M13_POST_OLD, _M13_POST_NEW).replace(_M13_PATCH_OLD, _M13_PATCH_NEW)


def _m13(handler=_M13_HANDLER, obj=_M13_OBJECT, title=_M13_TITLE, changes=_M13_CHANGES):
    """A module-13 server program: module 12's, with the body checked at the door."""
    return _server("\n\n".join(p.rstrip("\n") for p in
                               (_M10_STORE, _M10_SEND, _M10_READBODY,
                                _M10_IDTEXT, _M10_PARSEID, _M10_TODOID,
                                _M11_UPDATE, _M12_DELETE, _M12_SENDEMPTY,
                                obj, title, changes, handler)))


_M13_FULL = _m13()

# --- Step 1's plain program: the six things JSON can be ---------------------
_M13_KIND = """function kindOf(value: unknown): string {
  if (value === null) {
    return "null";
  }
  if (Array.isArray(value)) {
    return "array";
  }
  return typeof value;
}
"""

_M13_S1_PRINTS = """
console.log(kindOf(JSON.parse('"Buy milk"')));
console.log(kindOf(JSON.parse("42")));
console.log(kindOf(JSON.parse("true")));
console.log(kindOf(JSON.parse("null")));
console.log(kindOf(JSON.parse('["Buy milk"]')));
console.log(kindOf(JSON.parse('{"title":"Buy milk"}')));
"""
_M13_S1_OUT = "string\nnumber\nboolean\nnull\narray\nobject"


def _m13_s1(kind=_M13_KIND):
    return _plain(kind.rstrip("\n") + "\n" + _M13_S1_PRINTS)


# --- Step 2's plain program: what titleFrom accepts --------------------------
_M13_S2_PRINTS = """
console.log(JSON.stringify(titleFrom(JSON.parse('{"title":"Buy milk"}'))));
console.log(JSON.stringify(titleFrom(JSON.parse('{"title":""}'))));
console.log(JSON.stringify(titleFrom(JSON.parse('{}'))));
console.log(JSON.stringify(titleFrom(JSON.parse('{"title":5}'))));
console.log(JSON.stringify(titleFrom(JSON.parse('{"title":null}'))));
console.log(JSON.stringify(titleFrom(JSON.parse("null"))));
console.log(JSON.stringify(titleFrom(JSON.parse('["Buy milk"]'))));
console.log(JSON.stringify(titleFrom(JSON.parse('"Buy milk"'))));
"""
_M13_S2_OUT = '"Buy milk"\n""\n' + "\n".join(["undefined"] * 6)


def _m13_s2(title=_M13_TITLE, obj=_M13_OBJECT):
    return _plain(obj.rstrip("\n") + "\n\n" + title.rstrip("\n") + "\n" + _M13_S2_PRINTS)


_BAD = '400 {"error":"invalid_body"}'
_TODO_E2 = '{"id":2,"title":"","done":false}'

_M13_WHY = (
    "The API accepts three things it should not, and module 9 named all three: "
    "`{}` makes a todo with no title, `{\"title\":5}` makes one whose title is a "
    "number, and `{\"done\":\"yes\"}` makes `done` a string. Not one of them "
    "produces an error, because `JSON.parse` hands back `any` and `any` means "
    "stop checking. Every guarantee the type system has given you for twelve "
    "modules ends at that line. This module moves the line: nothing gets past "
    "the boundary with a type it has not been checked for."
)

_M13_BRIEF = """
### The whole module in one line

Type what `JSON.parse` returns as `unknown`, check its shape before you use it,
and answer `400` when the shape is wrong.

### The one-word change

```ts
const data = JSON.parse(body);            // any      — everything allowed
const data: unknown = JSON.parse(body);   // unknown  — nothing allowed until checked
```

`any` and `unknown` both mean *this could be anything*. They differ in what they
let you do next:

| | `data.title` | `data.a.b.c` | `addTodo(data)` |
|---|---|---|---|
| `any` | fine | fine | fine |
| `unknown` | **error** | **error** | **error** |

`any` assumes the best and stops checking. `unknown` assumes nothing and makes
you prove it. Make the one-word change in your own `server.ts` and count the red
lines: every one is a place the API was trusting a client. That list is this
module's to-do list.

### Checking, not casting

```ts
const title = data as string;    // compiles. Proves nothing. The same hole with a different shape.
```

`as` tells the compiler to believe you. The whole point is that you do not know
yet. Instead, you **narrow** — ask real questions at runtime, and let the
compiler follow along:

```ts
typeof x === "string"            // is it a string?
Array.isArray(x)                 // is it an array?
"title" in obj                   // does this object have a title?
```

### Shape here, values in module 14

This module checks that the body is *the right kind of thing* — an object, with
a string `title`, with a boolean `done`. It does not check what the values say:
`{"title":""}` is a string, so it still gets through. Module 14 refuses it, and
also replaces today's bare `{"error":"invalid_body"}` with an error that names
the field.

### And `not json` is still a 500

`JSON.parse` throws on text that is not JSON, so there is no result to check.
Catching that needs `try`/`catch`, which is module 16's.
"""

_M13_SYNTAX = [
    _syn(
        "const data: unknown = JSON.parse(body);",
        "`unknown`: \"this could be anything, **and you must check before you use "
        "it**.\" The safe opposite of `any`.",
        """
const data: unknown = JSON.parse('{"title":"Buy milk"}');
data.title;         // error: 'data' is of type 'unknown'
""",
        "Assigning `any` to an `unknown` needs no conversion, so this one "
        "annotation is the whole change at the boundary. Everything after it has "
        "to earn its type.",
    ),
    _syn(
        'typeof value === "string"',
        "Ask what kind of value this is at runtime. Inside the `if`, the compiler "
        "narrows `value` to `string`.",
        """
const value: unknown = JSON.parse("42");
if (typeof value === "number") {
  console.log(value + 1);    // 43 — value is a number here
}
""",
        "`typeof` answers one of a few words: `\"string\"`, `\"number\"`, "
        "`\"boolean\"`, `\"object\"`, `\"undefined\"` … and **`typeof null` is "
        "`\"object\"`**. So is `typeof` of an array. Two of JSON's six kinds "
        "hide behind `\"object\"`.",
    ),
    _syn(
        "Array.isArray(value)",
        "`true` only for an array. The check `typeof` cannot make, since it says "
        "`\"object\"` for arrays too.",
        """
Array.isArray([1, 2]);            // true
Array.isArray({ title: "x" });    // false
typeof [1, 2];                    // "object" (!)
""",
        "A JSON array is a perfectly valid body to `JSON.parse`, and it has no "
        "fields — so a check that only asked for an object would wave `[]` "
        "through to a route that reads fields off it.",
    ),
    _syn(
        '"title" in obj',
        "Does this object have a property called `title`? Inside the `if`, the "
        "compiler knows it does — and types `obj.title` as `unknown`.",
        """
const obj: object = { title: "Buy milk" };
if ("title" in obj) {
  console.log(obj.title);       // fine — but obj.title is unknown
}
""",
        "Being there is not the same as being the right type. After `in`, "
        "`obj.title` is `unknown`, and it still needs a `typeof` check before it "
        "is a string.",
    ),
    _syn(
        "function objectFrom(data: unknown): object | undefined { … }",
        "The body as an object, or `undefined` if it is not one. `null`, arrays, "
        "strings and numbers are all valid JSON and all rejected here.",
        """
if (typeof data !== "object" || data === null || Array.isArray(data)) {
  return undefined;
}
return data;               // object
""",
        "All three checks are needed. `typeof` alone lets `null` and arrays "
        "through, because it calls both of them `\"object\"`.",
    ),
    _syn(
        'send(res, 400, { error: "invalid_body" });',
        "**400 Bad Request** — your request was wrong. The first 4xx in this "
        "project that blames the *body*, rather than the address.",
        "",
        "Deliberately bare for now: it says *that* the body was wrong, not *which "
        "part*. Module 14 makes it name the field.",
    ),
    _syn(
        "function changesFrom(data: any): Partial<Todo> { … }",
        "Module 11's patch builder — the function whose `data: any` this module "
        "changes to `unknown`.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — what JSON can be.
# ---------------------------------------------------------------------------

_M13_S1 = _pstep(
    "unknown", "Six things JSON can be",
    "`unknown` versus `any`, `typeof`, and the two kinds `typeof` hides behind \"object\".",
    """
Before you can check a body, you need to know what it might be. `JSON.parse` can
hand back exactly six kinds of value:

```
"Buy milk"          a string
42                  a number
true                a boolean
null                null
["Buy milk"]        an array
{"title":"x"}       an object
```

All six are valid bodies. A client can send any of them, and today your API
reads `.title` off whichever arrives.

### `any` versus `unknown`

```ts
const data: any = JSON.parse(body);
data.title            // fine. And wrong, if the body was 42.

const data: unknown = JSON.parse(body);
data.title            // error: 'data' is of type 'unknown'.
```

Both types mean *could be anything*. `any` responds to that by checking nothing;
`unknown` responds by allowing nothing until you have checked. `JSON.parse` is
declared to return `any` for historical reasons. You change that with one
annotation, and `any` converts to `unknown` without complaint.

### Asking what it is: `typeof`

```ts
typeof "Buy milk"     // "string"
typeof 42             // "number"
typeof true           // "boolean"
typeof null           // "object"    ← !
typeof ["Buy milk"]   // "object"    ← !
typeof {}             // "object"
```

`typeof` is a question you ask at runtime, and TypeScript narrows on the answer:
inside `if (typeof x === "string")`, `x` is a `string`.

But look at the last three. `typeof` has one word for three of JSON's six kinds.
`null` answers `"object"` — a famous mistake in JavaScript's design, kept forever
for compatibility — and so does every array. So telling the six apart takes two
more checks:

```ts
function kindOf(value: unknown): string {
  if (value === null) {
    return "null";
  }
  if (Array.isArray(value)) {
    return "array";
  }
  return typeof value;
}
```

Compare with `null` by name, ask `Array.isArray` about arrays, and only then is
`typeof` telling the truth.
""",
    """
Your `kindOf` names all six:

```
"Buy milk"          string
42                  number
true                boolean
null                null
["Buy milk"]        array
{"title":…}         object
```

If `null` or the array comes out as `object`, a check is missing — and it is the
same check `objectFrom` will need in step 2.
""",
    pitfalls=[
        "`typeof null === \"object\"`. It is true, and it is why a body of `null` gets past a check that only asks for an object — and then crashes the first time you read a field off it.",
        "`typeof [] === \"object\"` too. An array is a valid body with no fields, and `typeof` cannot tell it from `{}`. `Array.isArray` can.",
        "Reaching for `as`: `const title = data as string;`. It compiles and checks nothing — the same hole as `any`, written in a way that looks deliberate.",
        "`typeof x === \"array\"`. There is no such answer; `typeof` never says `\"array\"`. TypeScript refuses the comparison for that reason.",
        "Thinking `unknown` is a restriction to work around. Every error it produces is a place the code was assuming something about a client. Read them as a list.",
    ],
    warmup=[
        _pq("`typeof null` — what is it?",
            ["`\"object\"` — a long-standing quirk of JavaScript, and why `null` gets past a bare object check",
             "`\"null\"`",
             "`\"undefined\"`",
             "It throws"],
            0,
            "Which is why every object check in this module compares with `null` "
            "by name."),
        _pq("`const data: unknown = JSON.parse(body);` — what does `data.title` do?",
            ["Fails to compile — nothing may be done with an `unknown` until it has been checked",
             "Compiles, and is `unknown`",
             "Compiles, and is `any`",
             "Compiles, and is `undefined` at runtime"],
            0,
            "That refusal is the feature. `any` would have said yes to anything."),
    ],
    exercises=[
        _pex("todo-m13-unknown-1", "Name null by name",
             "`typeof` calls `null` an `\"object\"`. Catch it first, by comparing "
             "with it directly.",
             _m13_s1(),
             "value === null",
             [("", _M13_S1_OUT)],
             ["`null` is a single value, so compare with it.",
              "Strict equality, like every comparison in this project.",
              "`value === null`"]),
        _pfix("todo-m13-unknown-fix1", "An object called null",
              "`kindOf(JSON.parse(\"null\"))` answers `object`. Every other kind "
              "comes out right.",
              _m13_s1(_M13_KIND.replace("""  if (value === null) {
    return "null";
  }
""", "")),
              _m13_s1(),
              [("", _M13_S1_OUT)],
              ["What does `typeof null` answer?",
               "`typeof` cannot tell `null` from an object. A direct comparison can.",
               "Before the other checks: `if (value === null) { return \"null\"; }`"],
              difficulty="Intro"),
        _pfix("todo-m13-unknown-fix2", "An object called array",
              "`kindOf(JSON.parse('[\"Buy milk\"]'))` answers `object`.",
              _m13_s1(_M13_KIND.replace("""  if (Array.isArray(value)) {
    return "array";
  }
""", "")),
              _m13_s1(),
              [("", _M13_S1_OUT)],
              ["What does `typeof` say about an array?",
               "There is a function on `Array` that answers exactly this question.",
               "`if (Array.isArray(value)) { return \"array\"; }` before the `typeof`."],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("What is the difference between `any` and `unknown`?",
            ["Both could be anything; `any` then allows everything unchecked, `unknown` allows nothing until checked",
             "`unknown` is for values that might be `undefined`",
             "`any` is faster at runtime",
             "There is none — they are aliases"],
            0,
            "One trusts, one verifies. The value at runtime is identical; only what "
            "the compiler lets you do with it differs."),
        _pq("Which of JSON's six kinds does `typeof` call `\"object\"`?",
            ["Objects, arrays and `null`",
             "Only objects",
             "Objects and strings",
             "Objects and numbers"],
            0,
            "Three kinds, one word. `=== null` and `Array.isArray` tell the other "
            "two apart."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — reaching into an object.
# ---------------------------------------------------------------------------

_M13_S2_FIXIN = _M13_TITLE.replace(
    '  if (obj === undefined || !("title" in obj) || typeof obj.title !== "string") {',
    '  if (obj === undefined || typeof obj.title !== "string") {')

_M13_S2 = _pstep(
    "fields", "Reaching into an object",
    "`objectFrom`, the `in` operator, and a title that has to earn being a string.",
    """
The create route needs one thing from the body: a string called `title`. Getting
there from `unknown` takes three questions, each answered by a check the compiler
follows:

```ts
function objectFrom(data: unknown): object | undefined {
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    return undefined;
  }
  return data;
}
```

**Is it an object at all?** — `typeof` for the broad question, then `null` and
arrays by name, because step 1 showed `typeof` lets both through. What comes out
is typed `object`: something with properties, though the compiler has no idea
which.

### `in`: does it have this property?

```ts
const obj: object = …;
obj.title                  // error: Property 'title' does not exist on type 'object'
if ("title" in obj) {
  obj.title                // fine — and its type is unknown
}
```

`"title" in obj` is true when the object has a property with that name. Inside
the `if`, the compiler knows the property is there — and knows *nothing else*
about it, so `obj.title` is `unknown`. Being there is not the same as being a
string.

### And is it the right type?

```ts
function titleFrom(data: unknown): string | undefined {
  const obj = objectFrom(data);
  if (obj === undefined || !("title" in obj) || typeof obj.title !== "string") {
    return undefined;
  }
  return obj.title;          // string
}
```

Three questions in one condition, each only asked when the one before it passed
— `||` stops at the first `true` — so the compiler narrows as it reads: `obj` is
an object by the second question, has a `title` by the third, and after the `if`,
`obj.title` is a `string`.

### What gets through, and what does not

| Body | `titleFrom` | Why |
|---|---|---|
| `{"title":"Buy milk"}` | `"Buy milk"` | |
| `{"title":""}` | `""` | a string — module 14 decides empty is not allowed |
| `{}` | `undefined` | no title |
| `{"title":5}` | `undefined` | not a string |
| `{"title":null}` | `undefined` | `typeof null` is not `"string"` |
| `null` · `["Buy milk"]` · `"Buy milk"` | `undefined` | not an object |

Every one of those `undefined`s was a 201 yesterday.
""",
    """
Your `titleFrom` answers these eight bodies:

```
{"title":"Buy milk"}   "Buy milk"
{"title":""}           ""
{}                     undefined
{"title":5}            undefined
{"title":null}         undefined
null                   undefined
["Buy milk"]           undefined
"Buy milk"             undefined
```

Two strings out, six refusals — and the second string is the one module 14 will
refuse too.
""",
    pitfalls=[
        "Reading `obj.title` without `\"title\" in obj` first. An `object` has no known properties, so it does not compile — `Property 'title' does not exist on type 'object'`.",
        "Stopping after `in`. The property exists, but `obj.title` is still `unknown`; returning it as a `string` does not compile either. `typeof` finishes the job.",
        "Leaving `null` out of `objectFrom`. `typeof null` is `\"object\"`, so `null` passes, and `\"title\" in null` throws a `TypeError` at runtime — a 500.",
        "Checking `data.title !== undefined` the module-11 way. On `unknown` it does not compile, and on `any` it let `5` and `null` through.",
        "Treating `{\"title\":\"\"}` as a type error. It is a string — the right *type*. Whether an empty title is allowed is a rule about values, and that is module 14.",
    ],
    warmup=[
        _pq("`const obj: object = …; if (\"title\" in obj) { … }` — inside the `if`, what is the type of `obj.title`?",
            ["`unknown` — the property exists, but nothing is known about it yet",
             "`string`",
             "`any`",
             "`string | undefined`"],
            0,
            "`in` proves presence, not type. `typeof` is the second question."),
    ],
    exercises=[
        _pex("todo-m13-fields-1", "Does it have a title?",
             "`obj` is an object. Before its `title` can be read, check that it "
             "has one.",
             _m13_s2(),
             '"title" in obj',
             [("", _M13_S2_OUT)],
             ["The operator that asks whether an object has a named property.",
              "The property name goes first, as a string.",
              "It sits inside a `!( … )` — the `if` is looking for bodies to refuse.",
              '`"title" in obj`']),
        _pfix("todo-m13-fields-fix1", "A property the object never promised",
              "This does not compile:\n\n"
              "    Property 'title' does not exist on type 'object'.\n\n"
              "`objectFrom` has proved the body is an object — but not what is in "
              "it. Add the one check that lets the compiler, and you, read "
              "`obj.title`.",
              _m13_s2(_M13_S2_FIXIN),
              _m13_s2(),
              [("", _M13_S2_OUT)],
              ["An `object` has no properties the compiler knows about.",
               "Ask whether the property is there before asking what type it is.",
               "The check goes between `obj === undefined` and the `typeof`, joined with `||`.",
               '`!("title" in obj) ||`'],
              difficulty="Easy"),
        _pex("todo-m13-fields-2", "Is the title a string?",
             "`obj` has a `title`, and its type is `unknown`. Refuse the body "
             "unless it is a string.",
             _m13_s2(),
             'typeof obj.title !== "string"',
             [("", _M13_S2_OUT)],
             ["`typeof` answers with a word.",
              "The `if` refuses, so the condition is \"not a string\".",
              '`typeof obj.title !== "string"`']),
    ],
    quiz=[
        _pq("Why does `objectFrom` check `data === null` when it has already checked `typeof data === \"object\"`?",
            ["`typeof null` is `\"object\"`, so without it `null` passes — and `\"title\" in null` throws",
             "For readability only",
             "Because `typeof` cannot run on `unknown`",
             "Because `null` is an array"],
            0,
            "A 500 hidden in a check that looked complete. Three checks, because "
            "`typeof` has one word for three things."),
        _pq("Which body does `titleFrom` accept that the finished API must refuse?",
            ["`{\"title\":\"\"}` — it is a string, so the type is right; refusing an empty one is module 14's rule",
             "`{\"title\":5}`",
             "`{}`",
             "`null`"],
            0,
            "Types say what kind of thing it is. Rules say whether it is acceptable. "
            "This module is the first; the next is the second."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — the create route.
# ---------------------------------------------------------------------------

_M13_POST_ROUTE = """  if (req.method === "POST" && url.pathname === "/todos") {
""" + _M13_POST_NEW + """
    return;
  }"""

_M13_S3 = _pstep(
    "create", "Create: check, then store",
    "`unknown` at the parse, `titleFrom` before `addTodo`, and the first 400.",
    """
Here is the create route as it has been since module 9:

```ts
const body = await readBody(req);
const data = JSON.parse(body);            // any
const todo = addTodo(data.title);         // whatever data.title happens to be
send(res, 201, todo);
```

Annotate the parse and the third line stops compiling — `'data' is of type
'unknown'`. Good: that line was the hole. It becomes a check and a branch:

```ts
const body = await readBody(req);
const data: unknown = JSON.parse(body);
const title = titleFrom(data);
if (title === undefined) {
  send(res, 400, { error: "invalid_body" });
  return;
}
const todo = addTodo(title);              // title is a string. Proven, not assumed.
send(res, 201, todo);
```

After the `if`, `title` is a `string`, and `addTodo` gets exactly what its
signature asks for — which, since module 2, it has never actually been
guaranteed.

### 400 Bad Request

`400` means *your request was wrong* — the client's fault, not the server's.
Every failure so far has been about the address (404) or the server itself (500).
This is the first that is about **what the client sent**.

The body `{"error":"invalid_body"}` is honest and not very helpful: it says the
body was wrong, not what was wrong with it. That is a deliberate stopping point.
Module 14 turns it into

```json
{"error":"validation","fields":[{"field":"title","message":"must be a string"}]}
```

— and doing that well is a whole module.

### What the route no longer accepts

```
POST /todos {}                → 400    was 201, with no title
POST /todos {"title":5}       → 400    was 201, with a number for a title
POST /todos ["Buy milk"]      → 400    was 201, with no title
POST /todos null              → 400    was a 500 — reading .title off null throws
```

Look at the last one. Yesterday a body of `null` crashed the route, and the
replayer's boundary answered 500. Today it is refused before anything touches it.
Checking the shape did not only fix the quiet wrong answers — it removed a crash.
""",
    """
```bash
$ curl -s -i -X POST localhost:3000/todos -d '{"title":5}'
HTTP/1.1 400 Bad Request
{"error":"invalid_body"}

$ curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
{"id":1,"title":"Buy milk","done":false}
```

A refused body uses no id: the next good create still gets id 1.
""",
    pitfalls=[
        "`const data = JSON.parse(body) as unknown` and then `as any` further down to make an error go away. Every `as` is a place you stopped checking; the errors were the point.",
        "Calling `addTodo` before the check. A refused body must not reach the store — or the counter: a 400 that burned an id leaves a gap in every id after it.",
        "Answering 422 or 404. 404 is about the address, and this one is fine. 400 is the status for \"the request you sent is wrong\".",
        "Expecting `not json` to become a 400. `JSON.parse` throws before there is anything to check; that needs `try`/`catch`, which is module 16's.",
        "Forgetting the `return` after the 400. `title` is still `undefined` below it — and `addTodo(title)` then refuses to compile, which is the compiler catching this for you.",
    ],
    warmup=[
        _pq("Yesterday, `POST /todos null` answered 500. What happens today, and why?",
            ["400 — `objectFrom` refuses `null` before anything reads a property off it",
             "Still 500 — `null` is not valid JSON",
             "201 with no title",
             "404"],
            0,
            "Reading `.title` off `null` throws. Checking the shape first means "
            "nothing ever tries."),
    ],
    exercises=[
        _pex("todo-m13-create-1", "Refuse a body without a title",
             "`titleFrom` has answered. If it found no string title, answer 400 "
             "and stop — before anything reaches the store.",
             _M13_FULL,
             """    const title = titleFrom(data);
    if (title === undefined) {
      send(res, 400, { error: "invalid_body" });
      return;
    }
    const todo = addTodo(title);""",
             [("\n".join(['POST /todos {"title":5}', "POST /todos {}", _POST_A, "GET /todos"]),
               "\n".join([_BAD, _BAD, "201 " + _TODO_A, "200 [" + _TODO_A + "]"]))],
             ["Ask `titleFrom` for the title and keep the answer.",
              "`undefined` means the body did not have one: 400, `{ error: \"invalid_body\" }`, `return`.",
              "After the `if`, `title` is a `string` — pass it to `addTodo`.",
              "The third request must get id 1: the refused ones never touched the counter."]),
        _pfix("todo-m13-create-fix1", "A todo whose title is a number",
              "`POST /todos {\"title\":5}` answers `201` with "
              "`{\"id\":1,\"title\":5,\"done\":false}`. `POST /todos {}` answers `201` "
              "with no title at all. It compiles, it runs, and it returns nonsense "
              "— which is exactly what `any` is for.\n\n"
              "`titleFrom` is already written above. The route never calls it.",
              _m13(_M13_HANDLER.replace(_M13_POST_NEW, _M13_POST_OLD)),
              _M13_FULL,
              [("\n".join(['POST /todos {"title":5}', "POST /todos {}", _POST_A]),
                "\n".join([_BAD, _BAD, "201 " + _TODO_A]))],
              ["What type does `data` have in the create route?",
               "Annotate the parse as `unknown` and see which line the compiler objects to.",
               "That line is the hole. Replace `data.title` with `titleFrom(data)`, and answer 400 when it is `undefined`.",
               "`const data: unknown = JSON.parse(body); const title = titleFrom(data); if (title === undefined) { send(res, 400, { error: \"invalid_body\" }); return; }`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("A client posts `{\"title\":5}`. Who is at fault, and what status says so?",
            ["The client — 400, *your request was wrong*",
             "The server — 500",
             "Nobody — 201, since the title can be converted",
             "The address — 404"],
            0,
            "Status codes are a contract about whose problem this is. 4xx is "
            "yours; 5xx is mine."),
        _pq("Why must `addTodo` not run before the check?",
            ["A refused body must leave the store untouched — including the id counter, or every later id has a gap",
             "Because `addTodo` throws on bad input",
             "It can; the todo is deleted afterwards",
             "Because 400 responses cannot follow a store write"],
            0,
            "Check, then commit. The same order module 11 set up for updates."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the patch route.
# ---------------------------------------------------------------------------

_M13_S4 = _pstep(
    "patch", "Patch: the function that stops compiling",
    "`changesFrom(data: unknown)`, a field that is present but wrong, and the array that is not a body.",
    """
Module 11 wrote this, and said this module would change one word of it:

```ts
function changesFrom(data: any): Partial<Todo> {
  const changes: Partial<Todo> = {};
  if (data.title !== undefined) {
    changes.title = data.title;
  }
  if (data.done !== undefined) {
    changes.done = data.done;
  }
  return changes;
}
```

Change `any` to `unknown`, and all four uses of `data` are errors. Each one was a
place the patch trusted the client. Here is the function that replaces them:

```ts
function changesFrom(data: unknown): Partial<Todo> | undefined {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return undefined;
  }
  const changes: Partial<Todo> = {};
  if ("title" in obj) {
    if (typeof obj.title !== "string") {
      return undefined;
    }
    changes.title = obj.title;
  }
  if ("done" in obj) {
    if (typeof obj.done !== "boolean") {
      return undefined;
    }
    changes.done = obj.done;
  }
  return changes;
}
```

### Absent is fine. Present and wrong is not.

A patch may leave a field out — that is what makes it a patch. So a missing
`title` is not an error; `"title" in obj` is simply false and nothing is copied.
But a `title` that **is** there and is not a string is a mistake the client made,
and the whole patch is refused:

| Body | Result |
|---|---|
| `{"done":true}` | `{ done: true }` |
| `{}` | `{}` — an empty patch, still valid |
| `{"done":"yes"}` | `undefined` → 400 |
| `{"title":null,"done":true}` | `undefined` → 400 — one bad field refuses the lot |
| `[]` | `undefined` → 400 — not an object |

Refusing the whole patch for one bad field is deliberate: a client that sent two
changes expects both or neither, and applying half is worse than applying none.

### The return type gained a `| undefined`

`Partial<Todo> | undefined` means the caller now has to handle "this body was
not a patch at all" — which is exactly the case module 11's version quietly
turned into "a patch that changes nothing". The route:

```ts
const data: unknown = JSON.parse(body);
const changes = changesFrom(data);
if (changes === undefined) {
  send(res, 400, { error: "invalid_body" });
  return;
}
const updated = updateTodo(todo, changes);
```

Still lookup first: `PATCH /todos/9 {"done":"yes"}` is a 404, because there is
nothing at that address for the body to be wrong about.
""",
    """
```bash
$ curl -s -i -X PATCH localhost:3000/todos/1 -d '{"done":"yes"}'
HTTP/1.1 400 Bad Request
{"error":"invalid_body"}

$ curl -s -i -X PATCH localhost:3000/todos/1 -d '[]'
HTTP/1.1 400 Bad Request

$ curl -s localhost:3000/todos/1
{"id":1,"title":"Buy milk","done":false}
```

Both refused, and the todo untouched by either.
""",
    pitfalls=[
        "Refusing a patch because a field is *missing*. Absence is what makes it a patch; only a field that is present and the wrong type is a mistake.",
        "Skipping a bad field and applying the rest. `{\"title\":null,\"done\":true}` would tick the todo off and silently ignore the title — half a request is worse than none.",
        "Leaving `Array.isArray` out of `objectFrom`. `[]` has no `title` and no `done`, so it becomes an empty patch — a 200 for a body that was never an object.",
        "Checking `obj.done === true || obj.done === false` instead of `typeof`. It works, and it is two comparisons doing the job of one question.",
        "Parsing before the lookup, again. A bad body sent to a missing todo is a 404 — there is nothing for it to be wrong about.",
    ],
    warmup=[
        _pq("`PATCH /todos/1 {\"title\":null,\"done\":true}`. What should happen?",
            ["400 — the title is present and not a string, so the whole patch is refused and nothing changes",
             "200, ticking the todo off and ignoring the null title",
             "200, setting the title to null",
             "404"],
            0,
            "All or nothing. A client that sent two changes did not ask for one "
            "of them."),
    ],
    exercises=[
        _pex("todo-m13-patch-1", "Is done a boolean?",
             "`obj` has a `done`. Refuse the whole patch unless it is `true` or "
             "`false`.",
             _M13_FULL,
             'typeof obj.done !== "boolean"',
             [("\n".join([_POST_A, 'PATCH /todos/1 {"done":"yes"}', 'PATCH /todos/1 {"done":1}',
                          'PATCH /todos/1 {"done":true}']),
               "\n".join(["201 " + _TODO_A, _BAD, _BAD, "200 " + _TODO_A_DONE]))],
             ["The same question the title check asks, with a different answer.",
              "`typeof true` is `\"boolean\"`.",
              '`typeof obj.done !== "boolean"`']),
        _pfix("todo-m13-patch-fix1", "An array is not a patch",
              "`PATCH /todos/1 []` answers `200` with the todo unchanged — as if "
              "the client had sent an empty patch. It sent an array.",
              _m13(obj=_M13_OBJECT.replace(" || Array.isArray(data)", "")),
              _M13_FULL,
              [("\n".join([_POST_A, "PATCH /todos/1 []", 'PATCH /todos/1 ["done"]', "PATCH /todos/1 {}"]),
                "\n".join(["201 " + _TODO_A, _BAD, _BAD, "200 " + _TODO_A]))],
              ["What does `typeof []` answer?",
               "`objectFrom` lets through everything `typeof` calls an object.",
               "`|| Array.isArray(data)` in `objectFrom`'s condition."],
              difficulty="Easy"),
        _pch("todo-m13-patch-build", "Write changesFrom", "Medium",
             "Write `changesFrom(data: unknown)`.\n\n"
             "* not an object → `undefined`\n"
             "* a `title` that is present and not a string → `undefined`\n"
             "* a `done` that is present and not a boolean → `undefined`\n"
             "* otherwise the `Partial<Todo>` holding whichever of the two were sent\n\n"
             "`objectFrom` is written above it.",
             _M13_FULL,
             _M13_CHANGES.rstrip("\n"),
             [("\n".join([_POST_A, 'PATCH /todos/1 {"title":"Buy oat milk"}',
                          'PATCH /todos/1 {"title":null,"done":true}', "PATCH /todos/1 {}",
                          'PATCH /todos/1 {"done":true,"id":7}', "GET /todos"]),
               "\n".join(["201 " + _TODO_A, "200 " + _TODO_A_OAT, _BAD, "200 " + _TODO_A_OAT,
                          "200 " + _TODO_A_OAT_DONE, "200 [" + _TODO_A_OAT_DONE + "]"]))],
             ["Start with `const obj = objectFrom(data);` and return `undefined` if it is.",
              "`const changes: Partial<Todo> = {};`",
              "For each field: `if (\"title\" in obj) { … }` — inside, refuse unless `typeof` is right, then copy.",
              "The third request has one bad field and one good one. Nothing may change.",
              "`id` is still never copied: there is no `if` for it."]),
    ],
    quiz=[
        _pq("Why does a *missing* `title` not refuse a patch, when a `null` one does?",
            ["A patch may leave fields out — that is what it is; a field that is present and the wrong type is a mistake",
             "Because `null` is not valid JSON",
             "It should refuse both",
             "Because missing fields default to their old value in JSON"],
            0,
            "Absent means \"leave it alone\". Present-and-wrong means the client "
            "asked for something impossible."),
        _pq("Module 11's `changesFrom` returned `Partial<Todo>`. Why does this one return `Partial<Todo> | undefined`?",
            ["\"This body is not a patch at all\" is a real answer, and the type makes the route handle it",
             "Because `Partial` can be `undefined` anyway",
             "For symmetry with `titleFrom`",
             "Because `unknown` requires it"],
            0,
            "The old version turned a bad body into an empty patch — a 200 that "
            "hid the mistake. The `| undefined` is where the 400 comes from."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M13_BUILD_BLANK = "\n\n".join(p.rstrip("\n") for p in (_M13_OBJECT, _M13_TITLE, _M13_CHANGES))

_M13_FINAL = _pch(
    "todo-m13-build", "Module 13 build — nothing unchecked gets in", "Medium",
    "Write the three boundary functions.\n\n"
    "* `objectFrom(data)` — the body as an `object`, or `undefined` for `null`, "
    "arrays and every non-object\n"
    "* `titleFrom(data)` — a string `title`, or `undefined`\n"
    "* `changesFrom(data)` — a `Partial<Todo>` of the fields sent, or `undefined` "
    "if any field sent has the wrong type\n\n"
    "The handler below them already parses to `unknown` and answers 400 when they "
    "say `undefined`. The script throws every wrong shape at both write routes — "
    "and ends with `{\"title\":\"\"}`, which is a string and is still accepted. "
    "Module 14 refuses that one.",
    _M13_FULL,
    _M13_BUILD_BLANK,
    [("\n".join([_POST_A,
                 'POST /todos {"title":5}', "POST /todos {}", 'POST /todos ["Buy milk"]',
                 'POST /todos "Buy milk"', "POST /todos null",
                 'PATCH /todos/1 {"done":"yes"}', 'PATCH /todos/1 {"done":true,"title":null}',
                 "PATCH /todos/1 []", 'PATCH /todos/9 {"done":"yes"}',
                 'PATCH /todos/1 {"done":true}',
                 'POST /todos {"title":""}', "GET /todos"]),
      "\n".join(["201 " + _TODO_A,
                 _BAD, _BAD, _BAD, _BAD, _BAD,
                 _BAD, _BAD, _BAD, _NF,
                 "200 " + _TODO_A_DONE,
                 "201 " + _TODO_E2, "200 [" + _TODO_A_DONE + "," + _TODO_E2 + "]"]))],
    ["`objectFrom`: refuse unless `typeof data === \"object\"`, and it is not `null`, and not an array.",
     "`titleFrom`: `objectFrom`, then `\"title\" in obj`, then `typeof obj.title === \"string\"` — in that order, so each check can narrow for the next.",
     "`changesFrom`: an absent field is skipped; a present field of the wrong type refuses the whole patch.",
     "`PATCH /todos/9 {\"done\":\"yes\"}` is a 404 — the handler looks up before it reads.",
     "Five refused creates and no ids used: the empty-title todo gets id 2."],
)


_TODO_MODULES.append(_pmod(
    key="todo-unknown", number=13, phase="trust",
    title="`unknown` at the boundary",
    what="JSON.parse hands back `any` — the one place types stop protecting you",
    goal="Type parsed input honestly as `unknown`, narrow it before use, and answer 400 when its shape is wrong.",
    why=_M13_WHY,
    est_minutes=55,
    builds_on=["todo-create", "todo-update"],
    concepts=["unknown vs any", "typeof", "typeof null", "Array.isArray", "the in operator",
              "narrowing", "400 Bad Request", "shape vs value"],
    deliverable="An API where nothing parsed from a request is used before its shape "
                "has been checked — and a wrong shape is the client's 400, not a "
                "quiet 201 or a crash.",
    objectives=[
        "Explain the difference between `any` and `unknown`, and change `JSON.parse`'s result from one to the other",
        "Read the compile errors that change produces as a list of everywhere the code trusted a client",
        "Name JSON's six kinds of value, and the three that `typeof` calls `\"object\"`",
        "Check that a value is a plain object, excluding `null` and arrays, and say what goes wrong without each check",
        "Reach a property of an `object` with `in`, and say why its type is still `unknown` afterwards",
        "Answer a body of the wrong shape with 400, and say why a body that is not JSON is still a 500",
        "Refuse a patch with one wrong-typed field entirely, and say why applying the rest would be worse",
    ],
    endpoints=[
        _pep("POST", "/todos", "Create a todo from the body's title",
             '{"title":"Buy milk"}', "Todo, with the id you assigned",
             "201 · 400 · 500 on bad JSON"),
        _pep("PATCH", "/todos/:id", "Change title and/or done", '{"done":true}',
             "Todo, as it now is", "200 · 400 · 404 · 500 on bad JSON"),
        _pep("*", "anything else", "Fall through", "", '{"error":"not_found"}', "404"),
    ],
    brief=_M13_BRIEF,
    syntax=_M13_SYNTAX,
    steps=[_M13_S1, _M13_S2, _M13_S3, _M13_S4],
    final_build=_M13_FINAL,
    acceptance=[
        "`JSON.parse` is only ever assigned to a variable typed `unknown`; the words `any` and `as` appear nowhere in the body-handling code.",
        "`curl -s -i -X POST localhost:3000/todos -d '{\"title\":5}'` returns 400 and `{\"error\":\"invalid_body\"}`.",
        "`curl -s -i -X POST localhost:3000/todos -d '{}'` returns 400 — a todo with no title is never created.",
        "`curl -s -i -X POST localhost:3000/todos -d 'null'` returns 400, not 500.",
        "`curl -s -i -X PATCH localhost:3000/todos/1 -d '{\"done\":\"yes\"}'` returns 400, and the todo is unchanged afterwards.",
        "`curl -s -i -X PATCH localhost:3000/todos/1 -d '[]'` returns 400.",
        "A refused create uses no id: the next good create gets the next number.",
        "`curl -s -X POST localhost:3000/todos -d '{\"title\":\"\"}'` is still accepted — and you can say which module refuses it, and why it is not this one.",
    ],
    manual_test="""
Before anything else, make the one-word change in your own `server.ts` and let
the compiler talk:

```ts
const data: unknown = JSON.parse(body);     // in both write routes
function changesFrom(data: unknown) …       // and here
```

```bash
npx tsc --noEmit --strict --noUncheckedIndexedAccess server.ts
```

Count the errors, and read each one as a sentence: *here, the API believed the
client.* Then fix them with this module's three functions, restart, and throw the
wrong shapes at it:

```bash
for b in '{"title":5}' '{}' '["Buy milk"]' '"Buy milk"' 'null' '{"title":null}'; do
  printf '%-18s ' "$b"
  curl -s -o /dev/null -w '%{http_code}\\n' -X POST localhost:3000/todos -d "$b"
done
```

Every line should say 400. Then the patch route:

```bash
curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
curl -s -i -X PATCH localhost:3000/todos/1 -d '{"done":"yes"}'              # 400
curl -s -i -X PATCH localhost:3000/todos/1 -d '{"title":null,"done":true}'  # 400
curl -s localhost:3000/todos/1                                              # unchanged
```

And the two this module leaves alone, on purpose:

```bash
curl -s -X POST localhost:3000/todos -d '{"title":""}'   # 201 — right type, wrong value. Module 14.
curl -s -i -X POST localhost:3000/todos -d 'not json'    # 500 — never became a value. Module 16.
```
""",
    reference="""// server.ts — module 13
//
// Nothing parsed from a request is used before its shape has been checked.
// JSON.parse's result is `unknown` — "could be anything, prove it before you use
// it" — and three small functions do the proving. A body of the wrong shape is a
// 400: the client's mistake, said so.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

// addTodo's `title: string` has been a promise since module 2. As of this
// module, every caller can actually keep it.
function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };
  const i = todos.indexOf(todo);
  todos[i] = updated;
  return updated;
}

function deleteTodo(id: number): boolean {
  const i = todos.findIndex((t) => t.id === id);
  if (i === -1) {
    return false;
  }
  todos.splice(i, 1);
  return true;
}

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function sendEmpty(res: ServerResponse, status: number): void {
  res.writeHead(status);
  res.end();
}

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise<string>((resolve) => {
    req.setEncoding("utf8");
    let body = "";
    req.on("data", (chunk: string) => {
      body = body + chunk;
    });
    req.on("end", () => {
      resolve(body);
    });
  });
}

function idText(pathname: string): string | undefined {
  const parts = pathname.split("/");
  if (parts.length !== 3 || parts[1] !== "todos") {
    return undefined;
  }
  return parts[2];
}

function parseId(text: string): number | undefined {
  const id = Number(text);
  if (!Number.isInteger(id) || id < 1) {
    return undefined;
  }
  return id;
}

function todoId(pathname: string): number | undefined {
  const text = idText(pathname);
  if (text === undefined) {
    return undefined;
  }
  return parseId(text);
}

// ---- the boundary ----------------------------------------------------------
// Everything below this line and above the handler exists because a client can
// send any JSON at all: a string, a number, a boolean, null, an array, or an
// object. Only the last is a body.

// typeof says "object" for null AND for arrays, so both are named explicitly.
// Without the null check, `"title" in null` would throw — a 500.
function objectFrom(data: unknown): object | undefined {
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    return undefined;
  }
  return data;
}

// Three questions, each asked only if the last passed (|| stops at the first
// true), so the compiler narrows as it reads: an object, with a title, which is
// a string. After the `if`, obj.title is a `string` — proven, not assumed.
function titleFrom(data: unknown): string | undefined {
  const obj = objectFrom(data);
  if (obj === undefined || !("title" in obj) || typeof obj.title !== "string") {
    return undefined;
  }
  return obj.title;
}

// Module 11's patch builder, with `any` changed to `unknown` — which made every
// line of the old version a compile error. Absent fields are fine (that is what a
// patch is); a field that is PRESENT and the wrong type refuses the whole patch,
// because applying half of what a client asked for is worse than applying none.
//
// Shape only. `{"title":""}` is a string and gets through; whether an empty
// title is ALLOWED is a rule about values, and that is module 14.
function changesFrom(data: unknown): Partial<Todo> | undefined {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return undefined;
  }
  const changes: Partial<Todo> = {};
  if ("title" in obj) {
    if (typeof obj.title !== "string") {
      return undefined;
    }
    changes.title = obj.title;
  }
  if ("done" in obj) {
    if (typeof obj.done !== "boolean") {
      return undefined;
    }
    changes.done = obj.done;
  }
  return changes;
}

async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const id = todoId(url.pathname);

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    // `not json` still throws here and becomes the replayer's 500: there is no
    // value to check. Catching it is module 16's.
    const data: unknown = JSON.parse(body);
    const title = titleFrom(data);
    if (title === undefined) {
      // Bare on purpose. Module 14 says WHICH field and WHY.
      send(res, 400, { error: "invalid_body" });
      return;
    }
    // Checked before anything touches the store — a refused body never uses an id.
    const todo = addTodo(title);
    send(res, 201, todo);
    return;
  }

  if (req.method === "GET" && id !== undefined) {
    const todo = findTodo(id);
    if (todo === undefined) {
      send(res, 404, { error: "not_found" });
      return;
    }
    send(res, 200, todo);
    return;
  }

  if (req.method === "PATCH" && id !== undefined) {
    const todo = findTodo(id);                 // look up first: a bad body to a
    if (todo === undefined) {                  // missing todo is still a 404
      send(res, 404, { error: "not_found" });
      return;
    }
    const body = await readBody(req);
    const data: unknown = JSON.parse(body);
    const changes = changesFrom(data);
    if (changes === undefined) {
      send(res, 400, { error: "invalid_body" });
      return;
    }
    const updated = updateTodo(todo, changes);
    send(res, 200, updated);
    return;
  }

  if (req.method === "DELETE" && id !== undefined) {
    const removed = deleteTodo(id);
    if (!removed) {
      send(res, 404, { error: "not_found" });
      return;
    }
    sendEmpty(res, 204);
    return;
  }

  send(res, 404, { error: "not_found" });
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Search your file for `any` and for ` as `. Every hit in code that handles a request is a hole this module closes; get the count to zero.",
        "Write `function isTodo(value: unknown): value is Todo` — a *type predicate*, where the return type tells the compiler what a `true` means. Use it to check a whole todo at once, and notice module 19 will want exactly this when it loads todos from a file.",
        "Refuse unknown fields: make `PATCH {\"done\":true,\"colour\":\"red\"}` a 400 instead of ignoring `colour`. Then argue with yourself about whether ignoring was better — clients evolve, and a strict server breaks every client that sends a field it does not know yet.",
        "Accept `\"done\":\"true\"` as `true`. Write it, then list three strings a client might reasonably send and decide what each means. The list is the argument for refusing instead.",
        "Put a size limit on the body before `JSON.parse` — say 10 KB — and answer 413 above it. Where does the check go, and why can it not go after the parse?",
    ],
    glossary=[
        _pgloss("unknown", "\"Could be anything — check before use.\" Nothing may be done with an `unknown` value until it has been narrowed. The safe opposite of `any`."),
        _pgloss("typeof", "A runtime question answered with a word — `\"string\"`, `\"number\"`, `\"boolean\"`, `\"object\"` … TypeScript narrows on the answer."),
        _pgloss("typeof null", "`\"object\"` — a quirk kept for compatibility, and the reason object checks compare with `null` by name."),
        _pgloss("Array.isArray", "`true` only for arrays, which `typeof` also calls `\"object\"`."),
        _pgloss("in operator", "`\"title\" in obj` — whether an object has a property with that name. Narrows `obj` so the property can be read, as `unknown`."),
        _pgloss("400 Bad Request", "Your request was wrong: the client's fault. Here, a body whose shape is not what the route accepts."),
        _pgloss("shape vs value", "Whether data is the right *kind* of thing (a string title) versus whether it is *acceptable* (a non-empty title). Module 13 checks the first, module 14 the second."),
        _pgloss("type assertion", "`x as T` — telling the compiler to believe you. Checks nothing at runtime, which is why this module never uses one."),
    ],
    cheatsheet="""
```ts
const data: unknown = JSON.parse(body);        // the one-word change

// an object — not null, not an array (typeof calls all three "object")
function objectFrom(data: unknown): object | undefined {
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    return undefined;
  }
  return data;
}

// object → has a title → title is a string. Each check narrows for the next.
function titleFrom(data: unknown): string | undefined {
  const obj = objectFrom(data);
  if (obj === undefined || !("title" in obj) || typeof obj.title !== "string") {
    return undefined;
  }
  return obj.title;
}

// in the route: check, THEN commit
const title = titleFrom(data);
if (title === undefined) {
  send(res, 400, { error: "invalid_body" });
  return;
}
const todo = addTodo(title);
```

| `typeof …` | Answer |
|---|---|
| `"x"` · `5` · `true` | `"string"` · `"number"` · `"boolean"` |
| `{}` · `[]` · `null` | `"object"` · `"object"` · `"object"` ← three kinds, one word |

| Body | POST | PATCH |
|---|---|---|
| `{"title":"x"}` | 201 | 200 |
| `{}` | 400 — no title | 200 — empty patch |
| `{"title":5}` · `{"title":null}` | 400 | 400 |
| `{"done":"yes"}` | 400 — no title | 400 |
| `[]` · `null` · `"x"` | 400 | 400 |
| `{"title":""}` | ⚠️ 201 — module 14 | ⚠️ 200 — module 14 |
| `not json` | ⚠️ 500 — module 16 | ⚠️ 500 — module 16 |

| Compiler says | Missing |
|---|---|
| `'data' is of type 'unknown'` | a check before using `data` |
| `Property 'title' does not exist on type 'object'` | `"title" in obj` |
| `Type 'unknown' is not assignable to type 'string'` | `typeof obj.title === "string"` |
""",
    self_check=[
        "Can you say what `any` allows that `unknown` does not, and why that makes `unknown` the right type for a parsed body?",
        "Can you name JSON's six kinds, and which three `typeof` calls `\"object\"`?",
        "Can you say what happens to a body of `null` without the `=== null` check — and what status the client sees?",
        "Can you explain why `obj.title` is still `unknown` after `\"title\" in obj`?",
        "Can you say why a missing `title` is fine in a patch and a `null` one is not?",
        "Can you explain why `{\"title\":\"\"}` gets through this module, and `not json` is still a 500?",
    ],
    review=[
        _pq("You change `const data = JSON.parse(body)` to `const data: unknown = JSON.parse(body)`. What happens?",
            ["Every line that reads from `data` without checking stops compiling — a list of every place the code trusted the client",
             "Nothing; `unknown` and `any` behave the same",
             "`JSON.parse` stops throwing",
             "The route answers 400 automatically"],
            0,
            "The errors are the lesson. `any` was silent about all of them."),
        _pq("Why does `objectFrom` need `Array.isArray` as well as `typeof data === \"object\"`?",
            ["`typeof` calls arrays `\"object\"` — without it `[]` is treated as a body with no fields",
             "Arrays cannot be parsed from JSON",
             "`typeof` throws on arrays",
             "It does not; the `in` check catches arrays"],
            0,
            "For `titleFrom` the `in` check would catch it. For `changesFrom`, an "
            "array becomes an empty patch and a 200 — which is the graded bug."),
        _pq("A client sends `POST /todos not json`. What does it get today, and why?",
            ["500 — `JSON.parse` throws before there is any value to check; catching it is module 16's",
             "400 — `titleFrom` refuses it",
             "201 with no title",
             "404"],
            0,
            "Checking the shape of a value needs a value. Text that is not JSON "
            "never becomes one."),
        _pq("`PATCH /todos/1 {\"title\":null,\"done\":true}`. Why refuse the whole patch rather than apply `done`?",
            ["The client asked for both; applying half is a result it never requested — all or nothing",
             "Because `done` depends on `title`",
             "Because the compiler cannot narrow two fields",
             "It should apply `done`"],
            0,
            "The same all-or-nothing module 11 built into `updateTodo`, now at the "
            "boundary."),
        _pq("Which is the difference between this module's checks and module 14's?",
            ["13 checks the *shape* — right kind of value; 14 checks the *value* — acceptable, and says which field failed",
             "13 checks POST, 14 checks PATCH",
             "13 is compile-time only, 14 is runtime",
             "There is none; 14 repeats 13"],
            0,
            "\"Is it a string?\" is a question the types can help with. \"Is it an "
            "acceptable title?\" is a rule this application makes up."),
        _pq("Why is `const title = data.title as string` not a fix?",
            ["`as` tells the compiler to believe you and checks nothing at runtime — `{\"title\":5}` still gets through",
             "It is a fix, just a verbose one",
             "It does not compile on `unknown`",
             "It throws on numbers"],
            0,
            "An assertion is `any` wearing a tie. Narrowing is the only thing that "
            "proves anything."),
    ],
    milestone="Nothing gets past the boundary unchecked. A parsed body is `unknown` "
              "until it has proved its shape, a wrong shape is the client's 400, "
              "and `addTodo`'s `title: string` is — for the first time since module "
              "2 — a promise every caller actually keeps.",
))
