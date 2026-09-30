# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 14 — Validation, and a 400 that names the field.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses modules 10-13's program pieces.
#
# VALUES HERE, SHAPE IN 13. Module 13 checked that a body was the right KIND of
# thing and answered a bare `{"error":"invalid_body"}` when it was not. This
# module adds the rules about what the values SAY — a title must not be empty or
# blank, and must be at most 100 characters — and replaces the bare 400 with one
# that names every field that was wrong:
#
#   {"error":"validation","fields":[{"field":"title","message":"must not be empty"}]}
#
# THE SHAPE WAS DECIDED WITH MODULE 15 IN MIND, as the roadmap asked. A field
# error is `{ field, message }` and a validation failure is a LIST of them, so
# module 15's `ApiError` union can carry `fields: FieldError[]` unchanged; only
# the line that sends it moves.
#
# THE RETURN TYPES CHANGE AGAIN, and the module says so. A validator now answers
# "the value, or what was wrong with it": `titleFrom` returns
# `string | FieldError`, `changesFrom` returns `Partial<Todo> | FieldError[]`.
# The two halves have different shapes, so a check module 13 already taught
# tells them apart — `typeof` for the single field, `Array.isArray` for the
# list. Module 15 then points out that this worked because the shapes HAPPENED
# to differ, and gives failures a tag of their own.
#
# COLLECTED, NOT FIRST-FAIL. Module 13's `changesFrom` returned at the first bad
# field. A patch of `{"title":"","done":"yes"}` has two mistakes, and a client
# fixing them one round-trip at a time is the thing a field-level error exists
# to prevent. Both gradable bugs in step 3 are about this: returning at the
# first error, and an off-by-one in the "any errors?" check that applies half a
# patch.
#
# `titleFrom` NOW TAKES THE FIELD, NOT THE BODY — and because its parameter is
# `unknown`, passing it the whole body still compiles. That is step 2's graded
# fix, and it is the lesson that `unknown` in a parameter accepts anything,
# including the wrong thing.
#
# NO `.map(`, NO `try`, NO `.filter(` anywhere in these programs, comments
# included: modules 16 and 17 own them.
# ---------------------------------------------------------------------------

_M14_FIELDERROR = """type FieldError = {
  field: string;
  message: string;
};
"""

_M14_TITLE = """function titleFrom(value: unknown): string | FieldError {
  if (typeof value !== "string") {
    return { field: "title", message: "must be a string" };
  }
  if (value.trim() === "") {
    return { field: "title", message: "must not be empty" };
  }
  if (value.length > 100) {
    return { field: "title", message: "must be at most 100 characters" };
  }
  return value;
}
"""

_M14_DONE = """function doneFrom(value: unknown): boolean | FieldError {
  if (typeof value !== "boolean") {
    return { field: "done", message: "must be true or false" };
  }
  return value;
}
"""

_M14_CREATE = """function createFrom(data: unknown): string | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];
  }
  if (!("title" in obj)) {
    return [{ field: "title", message: "is required" }];
  }
  const title = titleFrom(obj.title);
  if (typeof title !== "string") {
    return [title];
  }
  return title;
}
"""

_M14_CHANGES = """function changesFrom(data: unknown): Partial<Todo> | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];
  }
  const changes: Partial<Todo> = {};
  const errors: FieldError[] = [];
  if ("title" in obj) {
    const title = titleFrom(obj.title);
    if (typeof title === "string") {
      changes.title = title;
    } else {
      errors.push(title);
    }
  }
  if ("done" in obj) {
    const done = doneFrom(obj.done);
    if (typeof done === "boolean") {
      changes.done = done;
    } else {
      errors.push(done);
    }
  }
  if (errors.length > 0) {
    return errors;
  }
  return changes;
}
"""

_M14_POST_NEW = """    const body = await readBody(req);
    const data: unknown = JSON.parse(body);
    const checked = createFrom(data);
    if (Array.isArray(checked)) {
      send(res, 400, { error: "validation", fields: checked });
      return;
    }
    const todo = addTodo(checked);
    send(res, 201, todo);"""

_M14_PATCH_NEW = """    const body = await readBody(req);
    const data: unknown = JSON.parse(body);
    const checked = changesFrom(data);
    if (Array.isArray(checked)) {
      send(res, 400, { error: "validation", fields: checked });
      return;
    }
    const updated = updateTodo(todo, checked);
    send(res, 200, updated);"""

assert _M13_HANDLER.count(_M13_POST_NEW) == 1 and _M13_HANDLER.count(_M13_PATCH_NEW) == 1
_M14_HANDLER = _M13_HANDLER.replace(_M13_POST_NEW, _M14_POST_NEW).replace(_M13_PATCH_NEW, _M14_PATCH_NEW)


def _m14(handler=_M14_HANDLER, title=_M14_TITLE, done=_M14_DONE,
         create=_M14_CREATE, changes=_M14_CHANGES):
    """A module-14 server program: module 13's, with values checked and every
    refusal naming its field."""
    return _server("\n\n".join(p.rstrip("\n") for p in
                               (_M10_STORE, _M10_SEND, _M10_READBODY,
                                _M10_IDTEXT, _M10_PARSEID, _M10_TODOID,
                                _M11_UPDATE, _M12_DELETE, _M12_SENDEMPTY,
                                _M13_OBJECT, _M14_FIELDERROR, title, done,
                                create, changes, handler)))


_M14_FULL = _m14()

# --- Step 1's plain program: what titleFrom makes of eight values -----------
_A100 = "a" * 100
_A101 = "a" * 101

_M14_S1_PRINTS = """
function show(value: unknown): void {
  const result = titleFrom(value);
  if (typeof result === "string") {
    console.log("accepted (" + result.length + " characters)");
  } else {
    console.log(result.field + ": " + result.message);
  }
}

show("Buy milk");
show("");
show("   ");
show(5);
show(null);
show(true);
show("A100");
show("A101");
""".replace('"A100"', '"' + _A100 + '"').replace('"A101"', '"' + _A101 + '"')

_M14_S1_OUT = "\n".join([
    "accepted (8 characters)",
    "title: must not be empty",
    "title: must not be empty",
    "title: must be a string",
    "title: must be a string",
    "title: must be a string",
    "accepted (100 characters)",
    "title: must be at most 100 characters",
])


def _m14_s1(title=_M14_TITLE):
    return _plain("\n\n".join(p.rstrip("\n") for p in (_M14_FIELDERROR, title))
                  + "\n" + _M14_S1_PRINTS)


def _fe(field, message):
    return '{"field":"%s","message":"%s"}' % (field, message)


def _v(*errors):
    """The status line of a validation 400 naming these field errors."""
    return '400 {"error":"validation","fields":[' + ",".join(errors) + "]}"


_FE_EMPTY = _fe("title", "must not be empty")
_FE_STRING = _fe("title", "must be a string")
_FE_LONG = _fe("title", "must be at most 100 characters")
_FE_REQUIRED = _fe("title", "is required")
_FE_DONE = _fe("done", "must be true or false")
_FE_BODY = _fe("body", "must be a JSON object")

_M14_WHY = (
    "Module 13 made the API refuse the wrong *kind* of body — and it still "
    "accepts `{\"title\":\"\"}`, a todo with nothing to do, because an empty "
    "string is a string. Worse, every refusal it does make is the same bare "
    "`{\"error\":\"invalid_body\"}`. A client that sent `{\"title\":\"\","
    "\"done\":\"yes\"}` gets told *something* was wrong and has to guess which "
    "field, fix one, send again, and find the other. An error response is only "
    "useful if a client can act on it without reading your source code."
)

_M14_BRIEF = """
### The whole module in one line

Refuse values the application does not allow, and say **which field** was wrong
and **why** — every field, in one response.

### What changes on the wire

```
POST /todos {"title":""}
400 {"error":"invalid_body"}                                              ← module 13
400 {"error":"validation","fields":[{"field":"title","message":"must not be empty"}]}   ← now
```

The new body is a contract, not a courtesy. A form can put `must not be empty`
under the title box because `field` says which box. Two fields wrong means two
entries, in one response.

### Shape was module 13. Values are this one.

| Question | Answered by | Module |
|---|---|---|
| Is `title` a string? | the type system can help — `typeof` | 13 |
| Is it an *acceptable* title? | a rule this application made up | **14** |

The rules, decided before writing a line:

* `title` must not be empty — and a title of only spaces counts as empty
* `title` must be at most **100** characters
* `done` must be `true` or `false` (a shape rule, now with a message)

### Validators answer with the value *or* the reason

```ts
function titleFrom(value: unknown): string | FieldError
```

Either you get a title you can use, or you get a `FieldError` saying what was
wrong with it. `typeof result === "string"` tells you which — a check module 13
already taught you. For a whole body the failure is a *list*, and
`Array.isArray` tells the two apart.
"""

_M14_SYNTAX = [
    _syn(
        "type FieldError = { field: string; message: string };",
        "One thing wrong with one field of a request. A validation failure is a "
        "**list** of these.",
        """
const e: FieldError = { field: "title", message: "must not be empty" };
""",
        "`field` is the name the *client* used, so a form can put the message "
        "next to the right box. `message` is written for a person.",
    ),
    _syn(
        "value.trim()",
        "The same string with the spaces (and tabs and newlines) removed from "
        "both ends. The string itself is not changed; you get a new one.",
        """
"  Buy milk ".trim();    // "Buy milk"
"   ".trim();            // ""
""",
        "`value === \"\"` lets `\"   \"` through — a title nobody can see. "
        "Comparing the *trimmed* value with `\"\"` catches both.",
    ),
    _syn(
        "function titleFrom(value: unknown): string | FieldError { … }",
        "A validator: the value if it passes every rule, otherwise the first "
        "rule it broke, as a `FieldError`.",
        """
const result = titleFrom("");
if (typeof result === "string") {
  // a title you can store
} else {
  // result is a FieldError
}
""",
        "Takes the *field's* value, not the whole body. Its parameter is "
        "`unknown`, so passing it the body by mistake still compiles — step 2 "
        "grades exactly that.",
    ),
    _syn(
        "const errors: FieldError[] = [];",
        "Somewhere to **collect** every problem before answering, rather than "
        "returning at the first.",
        """
const errors: FieldError[] = [];
errors.push({ field: "done", message: "must be true or false" });
errors.length;    // 1
""",
        "A patch can be wrong in two places. One response naming both saves the "
        "client a round trip per mistake.",
    ),
    _syn(
        "Partial<Todo> | FieldError[]",
        "\"The changes, or the list of what was wrong.\" Told apart with "
        "`Array.isArray`, since only one of them is an array.",
        """
const checked = changesFrom(data);
if (Array.isArray(checked)) {
  // FieldError[]
} else {
  // Partial<Todo>
}
""",
        "This works because the two halves *happen* to have different shapes. "
        "Module 15 gives failures a tag of their own so it never depends on luck.",
    ),
    _syn(
        'send(res, 400, { error: "validation", fields: checked });',
        "The field-level 400. Replaces module 13's bare `{\"error\":\"invalid_body\"}`.",
        "",
        "`error` stays a short fixed code a program can compare; `fields` says "
        "what to show a person.",
    ),
    _syn(
        "function objectFrom(data: unknown): object | undefined { … }",
        "Module 13's check that the body is a plain object — not `null`, not an "
        "array, not a string.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — rules about values.
# ---------------------------------------------------------------------------

_M14_S1 = _pstep(
    "rules", "Rules about values",
    "`FieldError`, `.trim()`, and a validator that answers with the value or the reason.",
    """
Module 13's `titleFrom` answered one question — *is there a string title?* —
with `string | undefined`. `undefined` says "no" and nothing else. This module
needs the reason, so the "no" has to carry one:

```ts
type FieldError = {
  field: string;
  message: string;
};
```

And the validator answers with the value when it passes, or a `FieldError` when
it does not:

```ts
function titleFrom(value: unknown): string | FieldError {
  if (typeof value !== "string") {
    return { field: "title", message: "must be a string" };
  }
  if (value.trim() === "") {
    return { field: "title", message: "must not be empty" };
  }
  if (value.length > 100) {
    return { field: "title", message: "must be at most 100 characters" };
  }
  return value;
}
```

Notice what changed besides the return type: it takes the **field's value**, not
the whole body. Finding the field inside the body is a separate job — the next
step's — and keeping them apart is what lets `titleFrom` serve both create and
patch.

### The order of the rules is the order of the questions

The `typeof` check comes first because the other two cannot be asked of
something that is not a string — `.trim()` on `5` does not compile. After it,
`value` is a `string`, and the value rules can use it.

### Empty, and empty-looking

```ts
"".trim()        // ""
"   ".trim()     // ""
" Buy milk ".trim()   // "Buy milk"
```

`value === ""` would refuse the first and accept the second — a title of three
spaces, which shows up in a list as nothing at all. Trimming before comparing
refuses both. (The title is stored as it was sent; only the *check* trims.)

### Where the limit sits

*At most* 100 characters means 100 is allowed and 101 is not: `> 100`, not
`>= 100`. A boundary rule is two tests, not one — the last value allowed and the
first refused.

### Telling the answer apart

```ts
const result = titleFrom(value);
if (typeof result === "string") {
  // result: string
} else {
  // result: FieldError
}
```

The two possible answers have different `typeof`s, so the same check module 13
taught narrows them.
""",
    """
Your `titleFrom` answers these eight values:

```
"Buy milk"        accepted (8 characters)
""                title: must not be empty
"   "             title: must not be empty
5                 title: must be a string
null              title: must be a string
true              title: must be a string
100 × "a"         accepted (100 characters)
101 × "a"         title: must be at most 100 characters
```

If `"   "` is accepted, the check is comparing the untrimmed value. If the
100-character title is refused, the limit is off by one.
""",
    pitfalls=[
        "A title of spaces is accepted — `value === \"\"` compares the raw string. Compare `value.trim()` instead.",
        "A 100-character title is refused — the check is `>= 100`. \"At most 100\" allows 100; test the last value allowed as well as the first refused.",
        "`.trim()` does not compile — `Property 'trim' does not exist on type 'unknown'`. The `typeof` check has to come first; after it, `value` is a string.",
        "Storing the trimmed title without meaning to. The rule *checks* the trimmed value; what you store is a separate decision, and changing what a client sent is not this module's.",
        "Writing messages for a program to parse. `message` is for a person; `field` and the top-level `error` code are what a program compares.",
    ],
    warmup=[
        _pq("`\"   \".trim()` — what is it?",
            ["`\"\"` — trimming removes spaces from both ends, and there is nothing else",
             "`\"   \"` — trim only removes newlines",
             "`\" \"` — one space is kept",
             "`undefined`"],
            0,
            "Which is why the emptiness check trims first: three spaces is an "
            "empty title in every way a person can see."),
    ],
    exercises=[
        _pex("todo-m14-rules-1", "Empty, however many spaces",
             "Refuse a title that is empty — including one made only of spaces.",
             _m14_s1(),
             'value.trim() === ""',
             [("", _M14_S1_OUT)],
             ["Remove the spaces from both ends, then compare.",
              "`.trim()` returns a new string without them.",
              '`value.trim() === ""`']),
        _pfix("todo-m14-rules-fix1", "A title nobody can see",
              "`titleFrom(\"   \")` is accepted — a todo whose title is three "
              "spaces. The truly empty title is refused correctly.",
              _m14_s1(_M14_TITLE.replace('value.trim() === ""', 'value === ""')),
              _m14_s1(),
              [("", _M14_S1_OUT)],
              ["What does the emptiness check compare?",
               "`\"   \"` is not `\"\"`. What is `\"   \".trim()`?",
               '`value.trim() === ""`'],
              difficulty="Intro"),
        _pfix("todo-m14-rules-fix2", "One character too strict",
              "A title of exactly 100 characters is refused. The rule is *at "
              "most* 100.",
              _m14_s1(_M14_TITLE.replace("value.length > 100", "value.length >= 100")),
              _m14_s1(),
              [("", _M14_S1_OUT)],
              ["Is 100 allowed by \"at most 100\"?",
               "`>=` refuses 100 itself.",
               "`value.length > 100`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why does `titleFrom` check `typeof value !== \"string\"` before `value.trim()`?",
            ["`.trim()` only exists on strings — until the `typeof` check, `value` is `unknown` and the call does not compile",
             "For speed",
             "Because `trim` throws on empty strings",
             "The order does not matter"],
            0,
            "Shape first, then values. The shape check is what makes the value "
            "checks expressible at all."),
        _pq("A rule says *at most 100 characters*. Which two titles are worth testing?",
            ["100 characters (allowed) and 101 (refused) — the two sides of the boundary",
             "0 and 1000",
             "Only 101",
             "50 and 150"],
            0,
            "Off-by-one bugs live exactly at the boundary. Test the last value "
            "allowed and the first refused."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — the create route.
# ---------------------------------------------------------------------------

_M14_S2_SCRIPT = "\n".join([
    'POST /todos {"title":""}', 'POST /todos {"title":"   "}', "POST /todos {}",
    'POST /todos {"title":5}', "POST /todos []", _POST_A, "GET /todos"])
_M14_S2_OUT = "\n".join([
    _v(_FE_EMPTY), _v(_FE_EMPTY), _v(_FE_REQUIRED), _v(_FE_STRING), _v(_FE_BODY),
    "201 " + _TODO_A, "200 [" + _TODO_A + "]"])

_M14_S2 = _pstep(
    "create", "Create: the body, then the field",
    "`createFrom`, *required* versus *wrong*, and the first field-level 400.",
    """
`titleFrom` checks a title. The create route has a *body*, and three different
things can be wrong with it before `titleFrom` is even asked:

| Body | What is wrong | Field error |
|---|---|---|
| `[]` · `null` · `"Buy milk"` | not an object at all | `body: must be a JSON object` |
| `{}` | no title | `title: is required` |
| `{"title":5}` | a title of the wrong kind | `title: must be a string` |
| `{"title":""}` | a title of the right kind that breaks a rule | `title: must not be empty` |

`createFrom` asks those questions in that order, and for the last two it hands
over to `titleFrom`:

```ts
function createFrom(data: unknown): string | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];
  }
  if (!("title" in obj)) {
    return [{ field: "title", message: "is required" }];
  }
  const title = titleFrom(obj.title);
  if (typeof title !== "string") {
    return [title];
  }
  return title;
}
```

It returns a **list** even though create can only ever find one problem — there
is only one field. That is so both write routes fail in the same shape, and a
client needs to read one format, not two.

### Required is not the same as wrong

`{}` and `{"title":5}` are different mistakes and deserve different messages. On
create, a title is **required**: there is no todo without one. (On a patch, as
module 13 said, a missing field is fine — that asymmetry is next step's.)

### The route

```ts
const data: unknown = JSON.parse(body);
const checked = createFrom(data);
if (Array.isArray(checked)) {
  send(res, 400, { error: "validation", fields: checked });
  return;
}
const todo = addTodo(checked);       // checked: string
send(res, 201, todo);
```

`Array.isArray` is the question module 13 taught for telling an array from an
object. Here it tells the failure (a list) from the success (a string), and after
the `if`, the compiler knows `checked` is the title.
""",
    """
```bash
$ curl -s -X POST localhost:3000/todos -d '{"title":"   "}'
{"error":"validation","fields":[{"field":"title","message":"must not be empty"}]}

$ curl -s -X POST localhost:3000/todos -d '{}'
{"error":"validation","fields":[{"field":"title","message":"is required"}]}

$ curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
{"id":1,"title":"Buy milk","done":false}
```

Five refusals, and the good create still gets id 1.
""",
    pitfalls=[
        "Every create answers `title: must be a string`, even `{\"title\":\"Buy milk\"}`. `titleFrom` was handed the whole body — `titleFrom(obj)` — and an object is not a string. Its parameter is `unknown`, so the mistake compiles. Pass `obj.title`.",
        "`{}` answers `must be a string` instead of `is required`. Different mistakes, different messages: check `\"title\" in obj` before asking what type the title is.",
        "Returning a single `FieldError` from `createFrom` instead of a list. Then the create 400 and the patch 400 have different shapes, and every client has to handle both.",
        "Answering the validation 400 with `error: \"invalid_body\"` out of habit. The code a client compares is part of the contract; `validation` is the new one.",
        "Calling `addTodo` before the check. A refused create must not use an id — the next good one still gets the next number.",
    ],
    warmup=[
        _pq("`POST /todos {}`. Which field error is right?",
            ["`title: is required` — there is no title at all, which is a different mistake from a title of the wrong kind",
             "`title: must be a string`",
             "`body: must be a JSON object`",
             "None — `{}` is a valid create"],
            0,
            "`{}` *is* a JSON object, so the body is fine. What it lacks is the "
            "one field create cannot do without."),
    ],
    exercises=[
        _pex("todo-m14-create-1", "The field-level 400",
             "`createFrom` has answered. If it answered with a list of field "
             "errors, send them in a validation 400 and stop.",
             _M14_FULL,
             """    const checked = createFrom(data);
    if (Array.isArray(checked)) {
      send(res, 400, { error: "validation", fields: checked });""",
             [(_M14_S2_SCRIPT, _M14_S2_OUT)],
             ["Keep `createFrom`'s answer in a variable.",
              "The failure is the one that is an array.",
              "The body is `{ error: \"validation\", fields: … }`, and the status is 400.",
              "`const checked = createFrom(data); if (Array.isArray(checked)) { send(res, 400, { error: \"validation\", fields: checked });`"]),
        _pfix("todo-m14-create-fix1", "Nothing is ever a string",
              "Every create is refused with `title: must be a string` — even "
              "`{\"title\":\"Buy milk\"}`. It compiles without a murmur.",
              _m14(create=_M14_CREATE.replace("titleFrom(obj.title)", "titleFrom(obj)")),
              _M14_FULL,
              [(_M14_S2_SCRIPT, _M14_S2_OUT)],
              ["What is `titleFrom` being handed?",
               "`titleFrom` checks a *title*. Is the whole body a string?",
               "Its parameter is `unknown`, which accepts anything — including the wrong thing.",
               "`titleFrom(obj.title)`"],
              difficulty="Easy"),
        _pch("todo-m14-create-build", "Write createFrom", "Easy",
             "Write `createFrom(data: unknown)`. It answers with the title to "
             "store, or a list holding the one thing wrong:\n\n"
             "* not an object → `body: must be a JSON object`\n"
             "* no `title` → `title: is required`\n"
             "* otherwise whatever `titleFrom(obj.title)` found wrong, if anything\n\n"
             "`objectFrom` and `titleFrom` are written above it.",
             _M14_FULL,
             _M14_CREATE.rstrip("\n"),
             [(_M14_S2_SCRIPT, _M14_S2_OUT),
              ("\n".join(["POST /todos null", 'POST /todos {"title":"' + _A101 + '"}',
                          'POST /todos {"title":"' + _A100 + '"}']),
               "\n".join([_v(_FE_BODY), _v(_FE_LONG),
                          '201 {"id":1,"title":"' + _A100 + '","done":false}']))],
             ["`const obj = objectFrom(data);` — and a list with a `body` error if it is `undefined`.",
              "`if (!(\"title\" in obj))` — a list with `is required`.",
              "`const title = titleFrom(obj.title);` — if that is not a string, it is a `FieldError`: return `[title]`.",
              "Otherwise `return title;`"]),
    ],
    quiz=[
        _pq("`createFrom` can only ever find one problem. Why does it return a *list*?",
            ["So create and patch fail in one shape, and a client reads one error format, not two",
             "Because `FieldError` cannot be returned on its own",
             "For performance",
             "Because `Array.isArray` needs an array to work"],
            0,
            "The format is the contract. Where a list of one looks redundant, "
            "a second format would be worse."),
        _pq("`titleFrom(obj)` compiles, when `titleFrom` checks titles. Why?",
            ["Its parameter is `unknown`, and `unknown` accepts every value — the compiler cannot know you meant the field",
             "Because `obj` is `any`",
             "It does not compile",
             "Because `object` is a kind of string"],
            0,
            "`unknown` protects what happens *inside* the function. It says "
            "nothing about whether the caller passed the right thing."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — collecting every error in a patch.
# ---------------------------------------------------------------------------

_M14_CHANGES_FIRSTFAIL = """function changesFrom(data: unknown): Partial<Todo> | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];
  }
  const changes: Partial<Todo> = {};
  if ("title" in obj) {
    const title = titleFrom(obj.title);
    if (typeof title !== "string") {
      return [title];
    }
    changes.title = title;
  }
  if ("done" in obj) {
    const done = doneFrom(obj.done);
    if (typeof done !== "boolean") {
      return [done];
    }
    changes.done = done;
  }
  return changes;
}
"""

_M14_S3_SCRIPT = "\n".join([
    _POST_A, 'PATCH /todos/1 {"title":"","done":"yes"}', 'PATCH /todos/1 {"title":"","done":true}',
    'PATCH /todos/1 {"done":1}', "GET /todos/1", 'PATCH /todos/1 {"done":true}'])
_M14_S3_OUT = "\n".join([
    "201 " + _TODO_A, _v(_FE_EMPTY, _FE_DONE), _v(_FE_EMPTY), _v(_FE_DONE),
    "200 " + _TODO_A, "200 " + _TODO_A_DONE])

_M14_S3 = _pstep(
    "collect", "Patch: every mistake, in one answer",
    "`doneFrom`, a list that collects, and the check that decides whether anything is applied.",
    """
A patch can carry two fields, so it can carry two mistakes:

```
PATCH /todos/1 {"title":"","done":"yes"}
```

Module 13's `changesFrom` returned at the first bad field. A client that sent
this would be told about the title, fix it, send again — and only *then* hear
about `done`. One round trip per mistake. A field-level error exists so that it
takes one:

```json
{"error":"validation","fields":[
  {"field":"title","message":"must not be empty"},
  {"field":"done","message":"must be true or false"}
]}
```

### Collect, then decide

```ts
function doneFrom(value: unknown): boolean | FieldError {
  if (typeof value !== "boolean") {
    return { field: "done", message: "must be true or false" };
  }
  return value;
}

function changesFrom(data: unknown): Partial<Todo> | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];
  }
  const changes: Partial<Todo> = {};
  const errors: FieldError[] = [];
  if ("title" in obj) {
    const title = titleFrom(obj.title);
    if (typeof title === "string") {
      changes.title = title;
    } else {
      errors.push(title);
    }
  }
  if ("done" in obj) {
    const done = doneFrom(obj.done);
    if (typeof done === "boolean") {
      changes.done = done;
    } else {
      errors.push(done);
    }
  }
  if (errors.length > 0) {
    return errors;
  }
  return changes;
}
```

Every field is checked, whatever happened to the one before. Each good value
goes into `changes` and each bad one into `errors` — and only at the end does the
function decide which to hand back.

### The decision is all or nothing

`errors.length > 0` — *any* error at all — and the whole patch is refused. It is
tempting to read `changes` as "the good part" and apply it anyway. Module 13
argued against that and the argument has not changed: a client that asked for
two changes did not ask for one of them.

### Still the patch rules

A missing field is still fine — that is what makes it a patch. `titleFrom` runs
only `if ("title" in obj)`, so `{"done":true}` never asks about the title. The
only new thing a patch can hear is the *value* rules: `{"title":""}` is refused
now, where module 13 applied it.
""",
    """
```bash
$ curl -s -X PATCH localhost:3000/todos/1 -d '{"title":"","done":"yes"}'
{"error":"validation","fields":[{"field":"title","message":"must not be empty"},{"field":"done","message":"must be true or false"}]}

$ curl -s -X PATCH localhost:3000/todos/1 -d '{"title":"","done":true}'
{"error":"validation","fields":[{"field":"title","message":"must not be empty"}]}

$ curl -s localhost:3000/todos/1
{"id":1,"title":"Buy milk","done":false}
```

Two errors named in one answer, and the half-good patch applied not at all.
""",
    pitfalls=[
        "A patch with two mistakes reports only one — `changesFrom` still returns at the first bad field. Collect into `errors` and decide at the end.",
        "`{\"title\":\"\",\"done\":true}` ticks the todo off and answers 200. The *any errors?* check is `errors.length > 1`, so a single error is ignored and the good half is applied. Any error at all refuses the patch: `> 0`.",
        "Reporting `done: is required` for `{\"title\":\"x\"}`. On a patch, absent is fine; only a field that is present and wrong is an error.",
        "Pushing into `errors` *and* setting the field on `changes`. Harmless while the lot is refused — until someone changes the check. Each value goes one place or the other.",
        "Answering the errors in a different order each time. They come out in the order the fields are checked — title, then done — and a client's tests will depend on that.",
    ],
    warmup=[
        _pq("`PATCH /todos/1 {\"title\":\"\",\"done\":true}`. What happens?",
            ["400 naming `title`, and nothing changes — one bad field refuses the whole patch",
             "200, with `done` ticked and the title left alone",
             "200, with the title set to `\"\"`",
             "400 naming both fields"],
            0,
            "`done: true` is fine on its own, so only the title is named — and "
            "because anything was wrong, nothing is applied."),
    ],
    exercises=[
        _pex("todo-m14-collect-1", "Keep the bad value",
             "`done` was present and `doneFrom` refused it. Add its `FieldError` "
             "to the list.",
             _M14_FULL,
             "errors.push(done);",
             [(_M14_S3_SCRIPT, _M14_S3_OUT)],
             ["`done` is a `FieldError` in this branch.",
              "The list is called `errors`.",
              "`errors.push(done);`"]),
        _pfix("todo-m14-collect-fix1", "One mistake at a time",
              "`PATCH /todos/1 {\"title\":\"\",\"done\":\"yes\"}` names only the "
              "title. The client fixes it, sends again, and only then hears about "
              "`done`.",
              _m14(changes=_M14_CHANGES_FIRSTFAIL),
              _M14_FULL,
              [(_M14_S3_SCRIPT, _M14_S3_OUT)],
              ["Where does `changesFrom` stop when the title is wrong?",
               "Every field should be checked before anything is returned.",
               "Collect into `const errors: FieldError[] = [];` with `errors.push(…)`, and return the list at the end if it is not empty."],
              difficulty="Easy"),
        _pfix("todo-m14-collect-fix2", "Half a patch",
              "`PATCH /todos/1 {\"title\":\"\",\"done\":true}` answers `200` with "
              "the todo ticked off. The title was refused — and the rest of the "
              "patch went through anyway.",
              _m14(changes=_M14_CHANGES.replace("errors.length > 0", "errors.length > 1")),
              _M14_FULL,
              [(_M14_S3_SCRIPT, _M14_S3_OUT)],
              ["How many errors does this patch have?",
               "How many errors does it take before `changesFrom` refuses?",
               "Any error at all: `errors.length > 0`."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why collect every field error, rather than returning at the first?",
            ["A client fixing mistakes one response at a time needs a round trip per mistake; one answer naming all of them needs one",
             "Because the compiler requires it",
             "It is faster",
             "So the store can apply the good fields"],
            0,
            "The whole point of naming fields is that a client can fix the "
            "request without guessing. Naming half of them is half a fix."),
        _pq("`changes` holds the good fields and `errors` holds one bad one. What does the patch do?",
            ["Nothing is applied — any error refuses the whole patch",
             "The good fields are applied and the error is reported",
             "The good fields are applied silently",
             "It depends on which field was bad"],
            0,
            "All or nothing, as since module 13. Applying the good half is a "
            "result the client never asked for."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the error is contract.
# ---------------------------------------------------------------------------

_M14_S4_SCRIPT = "\n".join([
    _POST_A, "PATCH /todos/1 []", "PATCH /todos/1 null", 'PATCH /todos/1 {"title":"   "}',
    'PATCH /todos/9 {"title":""}', "PATCH /todos/1 {}", 'PATCH /todos/1 {"title":"Buy oat milk"}'])
_M14_S4_OUT = "\n".join([
    "201 " + _TODO_A, _v(_FE_BODY), _v(_FE_BODY), _v(_FE_EMPTY), _NF,
    "200 " + _TODO_A, "200 " + _TODO_A_OAT])

_M14_S4 = _pstep(
    "contract", "The error is part of the contract",
    "`body` as a field, what a client reads, and why this shape was chosen with module 15 in mind.",
    """
Every 400 the API sends now has the same shape:

```ts
{ error: "validation", fields: FieldError[] }
```

That is a promise to every client, the same as the shape of a `Todo` is. Three
decisions went into it, and each one is worth being able to defend.

### 1. A body that is not an object is a field error too

`PATCH /todos/1 []` has no fields to name. It could get its own error code —
but then clients would need to handle two 400 shapes. Instead the body itself is
the field:

```json
{"error":"validation","fields":[{"field":"body","message":"must be a JSON object"}]}
```

One shape, and a client that shows field errors next to form boxes shows this
one at the top of the form.

### 2. `error` is for programs, `message` is for people

A client *compares* `error`: `if (reply.error === "validation")`. It *displays*
`message`. Those have different audiences, and different rules for changing
them — reword a message whenever you like; renaming an error code breaks every
client that checks for it.

### 3. `fields` is a list, even of one

Covered in step 2, and it is the decision module 15 leans on. Next module, every
failure in the app — this one, the 404s, and the 500 the replayer has been
sending for you since module 4 — becomes one union type with one place that
sends it. A validation failure will carry exactly this list.

### Check, then commit — still

`updateTodo` builds a new todo and only then swaps it into the store; module 11
set that up so a refused patch could leave the store untouched. It still does:
`changesFrom` answers before `updateTodo` is called at all. And the lookup still
comes first — `PATCH /todos/9 {"title":""}` is a 404, because there is nothing at
that address for the body to be wrong about.
""",
    """
```bash
$ curl -s -X PATCH localhost:3000/todos/1 -d 'null'
{"error":"validation","fields":[{"field":"body","message":"must be a JSON object"}]}

$ curl -s -i -X PATCH localhost:3000/todos/9 -d '{"title":""}'
HTTP/1.1 404 Not Found

$ curl -s -X PATCH localhost:3000/todos/1 -d '{}'
{"id":1,"title":"Buy milk","done":false}
```

The empty patch is still a valid patch: nothing asked for, nothing wrong.
""",
    pitfalls=[
        "Inventing a second 400 shape for a body that is not an object. Every client then needs two code paths for one status. Name the body as the field.",
        "Changing an `error` code because it reads better. Messages are for people and can change; codes are compared by programs and are contract.",
        "Validating before the lookup. `PATCH /todos/9` with a bad body is a 404 — the address is wrong before the body can be.",
        "Refusing `{}` on a patch. It asks for nothing and breaks no rule; the answer is the todo, unchanged.",
        "Putting the whole todo in the 400. The error names what was wrong with the *request*; the client already has what it sent.",
    ],
    warmup=[
        _pq("A client checks `if (reply.error === \"validation\")`. Which change breaks it?",
            ["Renaming the code to `\"invalid\"`",
             "Rewording `\"must not be empty\"` to `\"cannot be blank\"`",
             "Adding a third field error",
             "Answering a different todo"],
            0,
            "Codes are compared; messages are displayed. Only one of those is "
            "safe to reword."),
    ],
    exercises=[
        _pex("todo-m14-contract-1", "The body is the field",
             "The body is not an object at all. Answer with the one field error "
             "that says so.",
             _M14_FULL,
             """function changesFrom(data: unknown): Partial<Todo> | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];""",
             [(_M14_S4_SCRIPT, _M14_S4_OUT)],
             ["Start from `objectFrom(data)`.",
              "If it is `undefined`, the body was not an object.",
              "The field is `\"body\"` and the message is `\"must be a JSON object\"` — in a list.",
              "`const obj = objectFrom(data); if (obj === undefined) { return [{ field: \"body\", message: \"must be a JSON object\" }];`"]),
        _pch("todo-m14-contract-build", "Write changesFrom", "Medium",
             "Write `changesFrom(data: unknown)`:\n\n"
             "* not an object → `[{ field: \"body\", message: \"must be a JSON object\" }]`\n"
             "* each of `title` and `done` that is *present* is checked with "
             "`titleFrom` / `doneFrom`\n"
             "* every error is collected; if there are any, return the list\n"
             "* otherwise the `Partial<Todo>` of the fields that were sent\n\n"
             "`objectFrom`, `titleFrom` and `doneFrom` are written above it.",
             _M14_FULL,
             _M14_CHANGES.rstrip("\n"),
             [(_M14_S3_SCRIPT, _M14_S3_OUT), (_M14_S4_SCRIPT, _M14_S4_OUT)],
             ["`const obj = objectFrom(data);` first, and the `body` error if it is `undefined`.",
              "Two lists to fill: `const changes: Partial<Todo> = {};` and `const errors: FieldError[] = [];`",
              "`if (\"title\" in obj) { const title = titleFrom(obj.title); … }` — a string goes into `changes`, anything else into `errors`.",
              "The same for `done` with `doneFrom`, where success is `typeof done === \"boolean\"`.",
              "At the end: `if (errors.length > 0) { return errors; } return changes;`"]),
    ],
    quiz=[
        _pq("Why is a non-object body reported as `{\"field\":\"body\", …}` rather than with its own error code?",
            ["So every 400 has one shape, and a client needs one code path to show it",
             "Because `body` is a property of every todo",
             "Because the compiler requires a field name",
             "It should have its own code"],
            0,
            "Consistency is the feature. A second shape for one rare case costs "
            "every client a branch."),
        _pq("Which of these may you change freely once clients depend on the API?",
            ["The wording of a `message`",
             "The `error` code",
             "The name `fields`",
             "The name `field`"],
            0,
            "Messages are read by people. Everything else in the shape is read "
            "by programs."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M14_BUILD_BLANK = "\n\n".join(p.rstrip("\n") for p in (_M14_TITLE, _M14_DONE, _M14_CREATE, _M14_CHANGES))

_M14_FINAL = _pch(
    "todo-m14-build", "Module 14 build — a 400 that names the field", "Medium",
    "Write the four validators.\n\n"
    "* `titleFrom(value)` — the title, or the first rule it breaks: *must be a "
    "string*, *must not be empty* (spaces count as empty), *must be at most 100 "
    "characters*\n"
    "* `doneFrom(value)` — the boolean, or *must be true or false*\n"
    "* `createFrom(data)` — the title to store, or a one-item list: *body: must "
    "be a JSON object*, *title: is required*, or `titleFrom`'s error\n"
    "* `changesFrom(data)` — the changes, or **every** field error at once\n\n"
    "`FieldError` and `objectFrom` are above them; the handler below already "
    "sends `{ error: \"validation\", fields }` when a list comes back.",
    _M14_FULL,
    _M14_BUILD_BLANK,
    [("\n".join([_POST_A,
                 'POST /todos {"title":""}', 'POST /todos {"title":"  "}', "POST /todos {}",
                 'POST /todos {"title":null}', 'POST /todos "Buy milk"',
                 'POST /todos {"title":"' + _A101 + '"}',
                 'PATCH /todos/1 {"title":"","done":"yes"}', 'PATCH /todos/1 {"title":5,"done":true}',
                 "PATCH /todos/1 []", 'PATCH /todos/9 {"done":"yes"}',
                 'PATCH /todos/1 {"done":true}', _POST_B, "GET /todos"]),
      "\n".join(["201 " + _TODO_A,
                 _v(_FE_EMPTY), _v(_FE_EMPTY), _v(_FE_REQUIRED), _v(_FE_STRING), _v(_FE_BODY),
                 _v(_FE_LONG),
                 _v(_FE_EMPTY, _FE_DONE), _v(_FE_STRING), _v(_FE_BODY), _NF,
                 "200 " + _TODO_A_DONE, "201 " + _TODO_B,
                 "200 [" + _TODO_A_DONE + "," + _TODO_B + "]"]))],
    ["`titleFrom`: `typeof` first, then `value.trim() === \"\"`, then `value.length > 100`.",
     "`createFrom`: `objectFrom`, then `\"title\" in obj`, then `titleFrom(obj.title)` — always answering failure as a list.",
     "`changesFrom`: check each field that is present, push every error, and decide at the end.",
     "Six refused creates and no ids used: the second good create gets id 2.",
     "`PATCH /todos/9` with a bad body is a 404 — the handler looks up before it reads."],
)


_TODO_MODULES.append(_pmod(
    key="todo-validate", number=14, phase="trust",
    title="Validation and a field-level 400",
    what="a validator that reports which field was wrong, not just that something was",
    goal="Refuse values the application does not allow, and answer with a 400 that names every field that was wrong and why.",
    why=_M14_WHY,
    est_minutes=55,
    builds_on=["todo-unknown"],
    concepts=["value rules", "FieldError", "trim", "boundary values", "required vs wrong",
              "collecting errors", "all-or-nothing", "error codes vs messages"],
    deliverable="An API whose every 400 is `{\"error\":\"validation\",\"fields\":[…]}`, "
                "naming each field that was wrong and why — and which refuses an "
                "empty title at last.",
    objectives=[
        "Say the difference between a rule about a value's shape and a rule about the value itself",
        "Write a validator that answers with the value or a `FieldError`, and tell the two apart with `typeof`",
        "Refuse an empty or blank title with `.trim()`, and a too-long one at the right boundary",
        "Tell *required* from *wrong* on create, and say why a patch has no required fields",
        "Collect every field error in a patch into one response, and refuse the whole patch if there is any",
        "Defend the shape of the 400: a list of fields, a code for programs, a message for people",
    ],
    endpoints=[
        _pep("POST", "/todos", "Create a todo — a 400 names each field that was wrong",
             '{"title":"Buy milk"}', "Todo, with the id you assigned",
             "201 · 400 · 500 on bad JSON"),
        _pep("PATCH", "/todos/:id", "Change title and/or done — a 400 names every bad field at once",
             '{"done":true}', "Todo, as it now is", "200 · 400 · 404 · 500 on bad JSON"),
        _pep("*", "anything else", "Fall through", "", '{"error":"not_found"}', "404"),
    ],
    brief=_M14_BRIEF,
    syntax=_M14_SYNTAX,
    steps=[_M14_S1, _M14_S2, _M14_S3, _M14_S4],
    final_build=_M14_FINAL,
    acceptance=[
        "`curl -s -X POST localhost:3000/todos -d '{\"title\":\"\"}'` returns 400 and `{\"error\":\"validation\",\"fields\":[{\"field\":\"title\",\"message\":\"must not be empty\"}]}`.",
        "`curl -s -X POST localhost:3000/todos -d '{\"title\":\"   \"}'` is refused the same way — a blank title is an empty one.",
        "`curl -s -X POST localhost:3000/todos -d '{}'` names `title` as `is required`; `-d '{\"title\":5}'` names it as `must be a string`.",
        "A title of exactly 100 characters is accepted; one of 101 is refused with `must be at most 100 characters`.",
        "`curl -s -X PATCH localhost:3000/todos/1 -d '{\"title\":\"\",\"done\":\"yes\"}'` names **both** fields in one response, and changes nothing.",
        "`curl -s -X PATCH localhost:3000/todos/1 -d '[]'` returns 400 naming `body`.",
        "No response anywhere says `invalid_body` any more.",
        "A refused create uses no id: the next good create gets the next number.",
    ],
    manual_test="""
Restart with this module's validators, create one todo, and throw bad values at
it. Read each response as the client would — *can I tell what to fix?*

```bash
curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'

curl -s -X POST localhost:3000/todos -d '{"title":""}'
curl -s -X POST localhost:3000/todos -d '{"title":"   "}'
curl -s -X POST localhost:3000/todos -d '{}'
curl -s -X POST localhost:3000/todos -d '[]'

curl -s -X PATCH localhost:3000/todos/1 -d '{"title":"","done":"yes"}'
curl -s localhost:3000/todos/1          # unchanged
```

Now the boundary. Generate a title of exactly 100 characters, then one of 101:

```bash
t100=$(printf 'a%.0s' $(seq 100))
curl -s -o /dev/null -w '%{http_code}\\n' -X POST localhost:3000/todos -d "{\\"title\\":\\"$t100\\"}"    # 201
curl -s -o /dev/null -w '%{http_code}\\n' -X POST localhost:3000/todos -d "{\\"title\\":\\"${t100}a\\"}" # 400
```

And the one this module still leaves alone:

```bash
curl -s -i -X POST localhost:3000/todos -d 'not json'   # 500 — never became a value. Module 16.
```
""",
    reference="""// server.ts — module 14
//
// Every refusal names its field. Module 13 checked the SHAPE of a body; this
// module adds rules about VALUES — a title must not be blank and must be at most
// 100 characters — and answers
//   {"error":"validation","fields":[{"field":"title","message":"must not be empty"}]}
// naming every field that was wrong, in one response.
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

// One thing wrong with one field. `field` is the name the client used, so a
// form can show `message` next to the right box.
type FieldError = {
  field: string;
  message: string;
};

// A validator answers with the value, or with what was wrong with it. Shape
// first (module 13), because the value rules can only be asked of a string.
// The emptiness check trims, so a title of spaces counts as empty; the title is
// stored as sent.
function titleFrom(value: unknown): string | FieldError {
  if (typeof value !== "string") {
    return { field: "title", message: "must be a string" };
  }
  if (value.trim() === "") {
    return { field: "title", message: "must not be empty" };
  }
  if (value.length > 100) {
    return { field: "title", message: "must be at most 100 characters" };
  }
  return value;
}

function doneFrom(value: unknown): boolean | FieldError {
  if (typeof value !== "boolean") {
    return { field: "done", message: "must be true or false" };
  }
  return value;
}

// Create can only find one problem — there is one field — but answers with a
// LIST anyway, so both write routes fail in one shape. A title is required
// here; on a patch nothing is.
function createFrom(data: unknown): string | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];
  }
  if (!("title" in obj)) {
    return [{ field: "title", message: "is required" }];
  }
  const title = titleFrom(obj.title);
  if (typeof title !== "string") {
    return [title];
  }
  return title;
}

// Every field that is present is checked, whatever happened to the one before,
// so a client hears about every mistake in one response. Any error at all
// refuses the whole patch: applying the good half is a result nobody asked for.
function changesFrom(data: unknown): Partial<Todo> | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];
  }
  const changes: Partial<Todo> = {};
  const errors: FieldError[] = [];
  if ("title" in obj) {
    const title = titleFrom(obj.title);
    if (typeof title === "string") {
      changes.title = title;
    } else {
      errors.push(title);
    }
  }
  if ("done" in obj) {
    const done = doneFrom(obj.done);
    if (typeof done === "boolean") {
      changes.done = done;
    } else {
      errors.push(done);
    }
  }
  if (errors.length > 0) {
    return errors;
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
    // `not json` still throws here and becomes a 500: there is no value to
    // check. Catching it is module 16's.
    const data: unknown = JSON.parse(body);
    // A list means refused; a string is the title. Array.isArray tells which.
    const checked = createFrom(data);
    if (Array.isArray(checked)) {
      send(res, 400, { error: "validation", fields: checked });
      return;
    }
    // Checked before anything touches the store — a refused body never uses an id.
    const todo = addTodo(checked);
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
    const checked = changesFrom(data);
    if (Array.isArray(checked)) {
      send(res, 400, { error: "validation", fields: checked });
      return;
    }
    const updated = updateTodo(todo, checked);
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
        "Store titles trimmed — `\"  Buy milk \"` saved as `\"Buy milk\"`. Then decide whether that belongs in `titleFrom` (which would have to return the trimmed string) or in `addTodo`, and argue for your choice.",
        "`\"🥛\".length` is 2, not 1: `.length` counts UTF-16 code units, not characters. Find a title of 60 emoji that the 100 limit refuses, and look up `[...value].length` as a fix — then ask whether your *database* would count the same way.",
        "Add a `code` to each field error — `{\"field\":\"title\",\"code\":\"too_long\",\"message\":\"…\"}` — so a client can translate messages without matching English text.",
        "Refuse unknown fields on a patch, naming each one: `{\"field\":\"colour\",\"message\":\"is not a field you can set\"}`. Then list what this costs a client that is newer than your server.",
        "Answer 422 Unprocessable Content for value errors and keep 400 for shape errors. Plenty of APIs do. Write down what a client gains from the distinction — and whether it is worth two statuses for one shape.",
    ],
    glossary=[
        _pgloss("validation", "Checking that a request's values are ones the application allows — beyond whether they are the right type."),
        _pgloss("FieldError", "`{ field, message }` — one thing wrong with one field of a request. A validation 400 carries a list of them."),
        _pgloss("trim", "`value.trim()` — the string without whitespace at either end. Used so a title of spaces counts as empty."),
        _pgloss("boundary value", "The last value a rule allows, or the first it refuses — 100 and 101 for *at most 100*. Where off-by-one bugs live."),
        _pgloss("required field", "One a request must include. `title` on create; nothing on a patch."),
        _pgloss("collecting errors", "Checking every field and reporting all failures together, rather than stopping at the first."),
        _pgloss("error code", "The short fixed string a program compares — `\"validation\"`. Contract: renaming it breaks clients."),
        _pgloss("error message", "The human-readable text — `\"must not be empty\"`. For people, and safe to reword."),
    ],
    cheatsheet="""
```ts
type FieldError = { field: string; message: string };

// a validator: the value, or the first rule it broke
function titleFrom(value: unknown): string | FieldError {
  if (typeof value !== "string") {
    return { field: "title", message: "must be a string" };
  }
  if (value.trim() === "") {                   // spaces count as empty
    return { field: "title", message: "must not be empty" };
  }
  if (value.length > 100) {                    // 100 allowed, 101 not
    return { field: "title", message: "must be at most 100 characters" };
  }
  return value;
}

// a patch: check every present field, collect, decide at the end
const errors: FieldError[] = [];
if ("title" in obj) {
  const title = titleFrom(obj.title);
  if (typeof title === "string") {
    changes.title = title;
  } else {
    errors.push(title);
  }
}
if (errors.length > 0) {                       // any error refuses the lot
  return errors;
}

// the route
const checked = changesFrom(data);             // Partial<Todo> | FieldError[]
if (Array.isArray(checked)) {
  send(res, 400, { error: "validation", fields: checked });
  return;
}
```

| Body | POST | PATCH |
|---|---|---|
| `[]` · `null` · `"x"` | `body: must be a JSON object` | `body: must be a JSON object` |
| `{}` | `title: is required` | 200 — empty patch |
| `{"title":5}` | `title: must be a string` | `title: must be a string` |
| `{"title":""}` · `{"title":"  "}` | `title: must not be empty` | `title: must not be empty` |
| 101 characters | `title: must be at most 100 characters` | the same |
| `{"title":"","done":"yes"}` | `title: …` (done is not read) | **both** fields |
| `not json` | ⚠️ 500 — module 16 | ⚠️ 500 — module 16 |
""",
    self_check=[
        "Can you say which of this module's rules are about shape and which are about values?",
        "Can you explain why `titleFrom(obj)` compiles, and what every create then answers?",
        "Can you say why `\"   \"` needs `.trim()` to be refused, and why the stored title is not trimmed?",
        "Can you name the two titles that test *at most 100 characters*?",
        "Can you say why `{}` is `is required` on create and a valid patch on PATCH?",
        "Can you explain why a patch with one good field and one bad one changes nothing?",
    ],
    review=[
        _pq("Module 13 accepted `{\"title\":\"\"}`. Why was that correct *for module 13*?",
            ["It checked shape — an empty string is a string; refusing it is a rule about the value, which is this module's",
             "It was a bug module 13 missed",
             "Because empty strings are not valid JSON",
             "Because module 13 only checked PATCH"],
            0,
            "Shape and value are separate questions, and splitting them made two "
            "short modules instead of one long one."),
        _pq("A patch has a bad `title` and a bad `done`. What does the response say?",
            ["Both — two field errors, in the order checked, and nothing applied",
             "Only the title, the first one found",
             "Only `done`",
             "`invalid_body`"],
            0,
            "Collected, not first-fail. One round trip, however many mistakes."),
        _pq("`titleFrom` returns `string | FieldError`. How does the caller tell which it got?",
            ["`typeof result === \"string\"` — only one of the two is a string",
             "`result === undefined`",
             "`\"message\" in result` — the only way",
             "It cannot; it needs a cast"],
            0,
            "The two halves differ in `typeof`, so an ordinary check narrows them. "
            "(`\"message\" in result` also works once you know it is an object.)"),
        _pq("Why does the length rule use `> 100` rather than `>= 100`?",
            ["\"At most 100\" allows 100 itself; `>=` would refuse it",
             "`>=` does not work on numbers",
             "For speed",
             "Either is right"],
            0,
            "The boundary is where the rule's wording and the code have to agree "
            "exactly."),
        _pq("Which part of `{\"error\":\"validation\",\"fields\":[…]}` is safe to reword later?",
            ["Each field error's `message` — it is for people",
             "`\"validation\"`",
             "`fields`",
             "`field`"],
            0,
            "Everything a program compares is contract. Only the prose is not."),
        _pq("Why was the error shape decided \"with module 15 in mind\"?",
            ["Module 15 turns every failure into one union type; a validation failure will carry exactly this `fields` list",
             "Module 15 deletes it",
             "Module 15 changes the status to 422",
             "It was not"],
            0,
            "A shape clients depend on is expensive to change twice. Deciding it "
            "once, knowing where it goes next, is the cheap way."),
    ],
    milestone="Every refusal names its field. An empty title is refused at last, a "
              "patch with two mistakes hears about both in one answer, and a client "
              "can fix any 400 from the response alone.",
))
