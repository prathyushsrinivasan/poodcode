# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 15 — One error shape, everywhere.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses modules 10-14's program pieces.
#
# THE TRACK'S DISCRIMINATED UNION. Every failure the API can report becomes one
# member of `ApiError`, tagged with a `kind`, and exactly one function —
# `errorReply` — turns a kind into a status and a body. `sendError` sends it.
# After this module no route writes an error body by hand, so the class of bug
# where a status and its body disagree (`send(res, 400, { error: "not_found" })`)
# or a code drifts (`"notfound"`) can no longer be written. Both are graded, as
# routes that were missed in the refactor.
#
# THREE KINDS, AND ONE OF THEM IS NOT SENT YET. `not_found` and `validation` are
# what the app sends today. `server_error` is what the REPLAYER has sent on the
# app's behalf since module 4, and it is in the union because it is part of the
# contract. Module 16 is where the app starts sending it itself, and adds a
# fourth kind — `invalid_json` — at which point the `never` line below makes the
# compiler point at the one place that must change. That is this module's
# payoff, cashed one module later.
#
# DECIDE, THEN DO. `errorReply(err)` is a pure function — no `res`, no I/O — so
# steps 1 and 2 run it as a plain program, printing exactly the lines the
# replayer would. `sendError` is two lines. Module 20's tests lean on that split.
#
# COMPILE-TIME ON PURPOSE. The module's whole argument is that the compiler now
# catches a missing case and a misspelt kind, so one `fix` is deliberately a
# compile error (a kind with no case: step 2). The verifier lists it, as
# intended. The runtime fixes are the ones the union cannot catch: routes that
# never went through it.
#
# NO `try`, NO `throw`, NO `.map(` in these programs, comments included.
# ---------------------------------------------------------------------------

_M15_APIERROR = """type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "server_error" };
"""

_M15_REPLY = """type ErrorReply = {
  status: number;
  body: object;
};

function errorReply(err: ApiError): ErrorReply {
  switch (err.kind) {
    case "not_found":
      return { status: 404, body: { error: "not_found" } };
    case "validation":
      return { status: 400, body: { error: "validation", fields: err.fields } };
    case "server_error":
      return { status: 500, body: { error: "server_error" } };
  }
  const unhandled: never = err;
  return unhandled;
}
"""

# The body of errorReply alone — step 4 has the learner write it inside the
# signature they are given.
_M15_REPLY_BODY = _M15_REPLY.split(": ErrorReply {\n", 1)[1].rsplit("\n}", 1)[0]
assert _M15_REPLY_BODY.startswith("  switch") and _M15_REPLY_BODY.endswith("return unhandled;")

_M15_SENDERROR = """function sendError(res: ServerResponse, err: ApiError): void {
  const reply = errorReply(err);
  send(res, reply.status, reply.body);
}
"""

_M15_HANDLER = (_M14_HANDLER
                .replace('send(res, 404, { error: "not_found" });', 'sendError(res, { kind: "not_found" });')
                .replace('send(res, 400, { error: "validation", fields: checked });',
                         'sendError(res, { kind: "validation", fields: checked });'))
assert "{ error:" not in _M15_HANDLER, "module 15: a route still writes its own error body"


def _m15(handler=_M15_HANDLER, apierror=_M15_APIERROR, reply=_M15_REPLY, senderror=_M15_SENDERROR):
    """A module-15 server program: module 14's, with every failure sent by kind."""
    return _server("\n\n".join(p.rstrip("\n") for p in
                               (_M10_STORE, _M10_SEND, _M10_READBODY,
                                _M10_IDTEXT, _M10_PARSEID, _M10_TODOID,
                                _M11_UPDATE, _M12_DELETE, _M12_SENDEMPTY,
                                _M13_OBJECT, _M14_FIELDERROR, _M14_TITLE, _M14_DONE,
                                _M14_CREATE, _M14_CHANGES,
                                apierror, reply, senderror, handler)))


_M15_FULL = _m15()

# --- Steps 1-2's plain program: every kind, as the replayer would print it --
_M15_PLAIN_PRINTS = """
function show(err: ApiError): void {
  const reply = errorReply(err);
  console.log(reply.status + " " + JSON.stringify(reply.body));
}

show({ kind: "not_found" });
show({ kind: "validation", fields: [{ field: "title", message: "must not be empty" }] });
show({ kind: "server_error" });
"""

_M15_PLAIN_OUT = "\n".join([
    '404 {"error":"not_found"}',
    _v(_FE_EMPTY),
    '500 {"error":"server_error"}',
])


def _m15_plain(apierror=_M15_APIERROR, reply=_M15_REPLY):
    return _plain("\n\n".join(p.rstrip("\n") for p in (_M14_FIELDERROR, apierror, reply))
                  + "\n" + _M15_PLAIN_PRINTS)


_M15_WHY = (
    "Count the error responses in your handler: four `send(res, 404, { error: "
    "\"not_found\" })`, two validation 400s, and a 500 you did not write at all "
    "— the replayer sends that one for you. Each is a status and a body typed "
    "out by hand, and nothing connects them. `send(res, 400, { error: "
    "\"not_found\" })` compiles. So does `{ error: \"notfound\" }` in one route "
    "and `\"not_found\"` in the rest. A client that checks `error` would break on "
    "one route in five, and no test you have would notice. The contract lives "
    "in seven copies; this module makes it live in one."
)

_M15_BRIEF = """
### The whole module in one line

Describe every failure as one type, and turn it into a response in exactly one
place.

### Seven copies of a contract

```ts
send(res, 404, { error: "not_found" });                    // ×4, in four routes
send(res, 400, { error: "validation", fields: checked });  // ×2
res.writeHead(500, …); res.end('{"error":"server_error"}'); // in the replayer
```

Every one of those lines pairs a status with a code by hand. Get one pair wrong
and it compiles, runs, and tells a client something false.

### One type for every failure

```ts
type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "server_error" };
```

A **discriminated union**: several object shapes, each tagged with a `kind`
whose type is one exact string. The tag says which member you are holding, and
only the validation member has `fields`.

### One place that turns it into a response

```ts
function errorReply(err: ApiError): ErrorReply {
  switch (err.kind) {
    case "not_found":
      return { status: 404, body: { error: "not_found" } };
    …
  }
}
```

Routes stop saying *what status and what body* and start saying *what went
wrong*: `sendError(res, { kind: "not_found" })`. The status and the body can no
longer disagree, because they are only ever written down together, once.

### And the compiler keeps the list

Add a fourth kind to the union and forget to handle it, and the build fails,
pointing at `errorReply`. Module 16 adds that fourth kind.
"""

_M15_SYNTAX = [
    _syn(
        '{ kind: "not_found" }',
        "An object whose `kind` has a **literal type**: not any string, exactly "
        "`\"not_found\"`. The tag a union is told apart by.",
        """
type NotFound = { kind: "not_found" };
const a: NotFound = { kind: "not_found" };   // fine
const b: NotFound = { kind: "not-found" };   // error — a different string
""",
        "A typo in a tag is a compile error, not a quiet wrong answer. That alone "
        "is worth the type.",
    ),
    _syn(
        "type ApiError =\n  | { kind: \"not_found\" }\n  | { kind: \"validation\"; fields: FieldError[] };",
        "A **discriminated union**: one of several shapes, each with a `kind` "
        "that says which. Members can carry different fields.",
        """
const e: ApiError = { kind: "validation", fields: [] };
""",
        "The leading `|` is optional and lets each member sit on its own line.",
    ),
    _syn(
        "switch (err.kind) {\n  case \"not_found\":\n    return …;\n}",
        "Compare one value against a list of cases. Inside each `case`, the "
        "compiler narrows `err` to the member with that `kind`.",
        """
switch (err.kind) {
  case "not_found":
    return 404;
  case "validation":
    return err.fields.length;   // fields exists only here
}
""",
        "A `case` without a `return` (or `break`) *falls through* into the next "
        "one. This track returns from every case, so it never happens.",
    ),
    _syn(
        "const unhandled: never = err;",
        "`never` is the type with no values. After a `switch` that handled every "
        "kind, `err` can be nothing — so this line compiles. Miss a kind, and it "
        "does not.",
        """
// with a case for every kind:  fine — err is never here
// missing the "server_error" case:
//   Type '{ kind: "server_error"; }' is not assignable to type 'never'.
""",
        "The error message names the kind you forgot. It is the compiler "
        "keeping your to-do list.",
    ),
    _syn(
        "function errorReply(err: ApiError): ErrorReply { … }",
        "The **one** place a failure becomes a status and a body. Pure — no "
        "`res`, no sending — so it can be run and printed on its own.",
        """
errorReply({ kind: "not_found" });
// { status: 404, body: { error: "not_found" } }
""",
    ),
    _syn(
        'sendError(res, { kind: "not_found" });',
        "What every route writes now: *what went wrong*, not *which status and "
        "which body*.",
        """
function sendError(res: ServerResponse, err: ApiError): void {
  const reply = errorReply(err);
  send(res, reply.status, reply.body);
}
""",
    ),
    _syn(
        "type FieldError = { field: string; message: string };",
        "Module 14's field error. A validation failure carries a list of them "
        "unchanged.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — a union that says which member it is.
# ---------------------------------------------------------------------------

_M15_S1 = _pstep(
    "kind", "A union that says which one it is",
    "Literal types, the `kind` tag, `switch`, and narrowing inside a `case`.",
    """
Module 14 already used unions: `string | FieldError`, `Partial<Todo> |
FieldError[]`. You told the halves apart with `typeof` and `Array.isArray` —
which worked because the halves *happened* to be different kinds of value. A
404 and a validation failure are both objects. Nothing about their shape says
which is which, so give each one a label:

```ts
type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "server_error" };
```

### A literal type

`kind: "not_found"` is not a string with a value in it. It is a *type* that
only one value belongs to — the string `"not_found"`. So:

```ts
const e: ApiError = { kind: "not-found" };
// Type '"not-found"' is not assignable to type
//   '"not_found" | "validation" | "server_error"'. Did you mean '"not_found"'?
```

A misspelt tag is caught before the program runs.

### `switch`, and what a `case` knows

```ts
function errorReply(err: ApiError): ErrorReply {
  switch (err.kind) {
    case "not_found":
      return { status: 404, body: { error: "not_found" } };
    case "validation":
      return { status: 400, body: { error: "validation", fields: err.fields } };
    case "server_error":
      return { status: 500, body: { error: "server_error" } };
  }
  …
}
```

`switch` compares `err.kind` against each `case` in turn and runs the first
that matches. And inside each one the compiler has narrowed `err`: in the
`"validation"` case it is the member that has `fields`. Try reading `err.fields`
in the `"not_found"` case — it does not compile, because that member has none.

### Pure on purpose

`errorReply` takes an error and returns a status and a body. It sends nothing
and has no `res` — so it can run as a plain program, printing exactly the lines
the replayer would:

```
404 {"error":"not_found"}
400 {"error":"validation","fields":[{"field":"title","message":"must not be empty"}]}
500 {"error":"server_error"}
```

Deciding what to send, and sending it, are two different jobs. Keeping them
apart is what makes the deciding testable — module 20 cashes that.
""",
    """
Your `errorReply` prints the three lines above: 404 for `not_found`, 400 with the
field list for `validation`, 500 for `server_error`.

If the validation line says 404, a case was copied from the one above it and
only half-edited.
""",
    pitfalls=[
        "A validation failure answers 404 — its `case` was copied from `not_found` and the status was never changed. This is exactly the bug that used to be spread over seven lines; now it can only be in one.",
        "`Property 'fields' does not exist on type '{ kind: \"not_found\"; }'` — reading `fields` outside the `\"validation\"` case, where the compiler has not narrowed `err`.",
        "Writing `kind: string` in the union. Then every member has the same tag type and the compiler cannot tell them apart — no narrowing, no typo checking. The tag must be a literal.",
        "`switch (err)` instead of `switch (err.kind)`. The cases are strings; compare the tag, not the object.",
        "Leaving out a `return` in a case: it falls through into the next one. Here the compiler usually catches it (the next case reads fields this member does not have), but not always — return from every case.",
    ],
    warmup=[
        _pq("`type E = { kind: \"not_found\" };` — what may `kind` hold?",
            ["Only the exact string `\"not_found\"`",
             "Any string",
             "Any string starting with `not`",
             "`\"not_found\"` or `undefined`"],
            0,
            "A literal type has exactly one value. That is what lets a tag be "
            "checked for typos and used to narrow."),
    ],
    exercises=[
        _pex("todo-m15-kind-1", "Only validation has fields",
             "In the `\"validation\"` case, put the failure's field list into the "
             "body.",
             _m15_plain(),
             "err.fields",
             [("", _M15_PLAIN_OUT)],
             ["In this `case`, `err` is the validation member.",
              "That member carries a list called `fields`.",
              "`err.fields`"]),
        _pfix("todo-m15-kind-fix1", "Copied from the case above",
              "A validation failure comes out as `404` — with a perfectly good "
              "validation body.",
              _m15_plain(reply=_M15_REPLY.replace(
                  'return { status: 400, body: { error: "validation"',
                  'return { status: 404, body: { error: "validation"')),
              _m15_plain(),
              [("", _M15_PLAIN_OUT)],
              ["Which status does the `\"validation\"` case return?",
               "A body whose values the client got wrong is a 4xx — which one?",
               "`status: 400`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("What does the compiler know about `err` inside `case \"validation\":`?",
            ["That it is the validation member — so `err.fields` is allowed",
             "Nothing more than `ApiError`",
             "That it is a string",
             "That `fields` is empty"],
            0,
            "Narrowing on a literal tag, just as `typeof` narrowed in module 13 — "
            "but on a property you designed."),
        _pq("Why can module 14's `typeof` / `Array.isArray` checks not tell a 404 from a validation failure?",
            ["Both are plain objects — nothing about their shape differs until you add a tag",
             "They can; the tag is decoration",
             "Because `typeof` does not work on unions",
             "Because 404s have no body"],
            0,
            "Module 14's halves differed by luck — a string and an object. Two "
            "objects need a field that says which is which."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — never: the compiler keeps the list.
# ---------------------------------------------------------------------------

_M15_REPLY_MISSING = _M15_REPLY.replace("""    case "server_error":
      return { status: 500, body: { error: "server_error" } };
""", "")

_M15_S2 = _pstep(
    "never", "`never`: the compiler keeps the list",
    "Exhaustiveness — what a forgotten `case` looks like, and the one line that makes it an error.",
    """
Look at the end of `errorReply`:

```ts
  switch (err.kind) {
    case "not_found":    return …;
    case "validation":   return …;
    case "server_error": return …;
  }
  const unhandled: never = err;
  return unhandled;
}
```

Every case returns. So how does anything reach the last two lines?

### Nothing does — and that is the point

After each `case`, the compiler crosses that member off the list of things `err`
could still be. After all three there is nothing left, and a type with no values
has a name: **`never`**. So `err` *is* `never` by the end of the switch, and
assigning it to a `never` variable is fine.

Now suppose the union grows and the `switch` does not:

```ts
type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "server_error" };            // added

// …but errorReply still has only two cases:

const unhandled: never = err;
// Type '{ kind: "server_error"; }' is not assignable to type 'never'.
```

After two cases, `err` can still be the server-error member — so it is *not*
`never`, and the line fails to compile. The message names **exactly the kind you
forgot**.

### Why this matters more than it looks

The day someone adds a kind of failure, the compiler walks them to every place
that needs to know. Without the `never` line, a forgotten case compiles fine and
`errorReply` returns `undefined` at runtime — `send` then crashes on it, and
every error of the new kind is a 500.

Module 16 adds a kind. You will see this message then, on purpose.

(The `return unhandled;` only exists to satisfy the return type. It can never
run: there is no value of type `never` to return.)
""",
    """
Your `errorReply` compiles with all three cases. Delete the `server_error` case
and it stops compiling, with a message that names `server_error`. Put it back.

That is the whole workflow: **add to the union, read the errors, add the cases.**
""",
    pitfalls=[
        "Deleting the `never` line because \"it never runs\". It does not run — it *compiles*, and that is its whole job. Without it a forgotten kind is a runtime crash.",
        "Adding a `default:` case that returns a generic 500. It swallows every future kind silently — exactly what the `never` line exists to prevent.",
        "Reading `Type '{ kind: \"server_error\"; }' is not assignable to type 'never'` as a type puzzle. Read it as a sentence: *you did not handle server_error.*",
        "Typing `err` as `any` to make the error go away. Then the switch narrows nothing and every check in this module is gone.",
    ],
    warmup=[
        _pq("After `case` statements for every member of the union, what is the type of `err`?",
            ["`never` — there is no member left for it to be",
             "`ApiError`",
             "`undefined`",
             "`unknown`"],
            0,
            "Each case crosses one member off. When the list is empty, the type "
            "is the empty type."),
    ],
    exercises=[
        _pex("todo-m15-never-1", "Make the compiler check",
             "Every kind has a case. Add the line that turns a forgotten one into "
             "a compile error.",
             _m15_plain(),
             "const unhandled: never = err;",
             [("", _M15_PLAIN_OUT)],
             ["After the switch, what can `err` still be?",
              "Assign it to a variable whose type has no values.",
              "`const unhandled: never = err;`"]),
        _pfix("todo-m15-never-fix1", "The kind nobody handled",
              "This does not compile:\n\n"
              "    Type '{ kind: \"server_error\"; }' is not assignable to type 'never'.\n\n"
              "The union has three kinds. Read the message as a sentence, and do "
              "what it says. A server error is a 500 with body "
              "`{\"error\":\"server_error\"}`.",
              _m15_plain(reply=_M15_REPLY_MISSING),
              _m15_plain(),
              [("", _M15_PLAIN_OUT)],
              ["Which kind does the message name?",
               "Which `case` is missing from the `switch`?",
               "`case \"server_error\": return { status: 500, body: { error: \"server_error\" } };`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("A teammate adds `{ kind: \"too_large\" }` to `ApiError` and nothing else. What happens?",
            ["The build fails at `errorReply`'s `never` line, naming `too_large`",
             "It compiles, and too-large errors become 500s",
             "It compiles, and too-large errors become 404s",
             "The union rejects the new member"],
            0,
            "That is the line's whole value: a new kind cannot ship without "
            "someone deciding what it looks like on the wire."),
        _pq("Why is a `default:` case that returns a 500 worse than the `never` line?",
            ["It turns every future forgotten kind into a quiet 500 instead of a compile error",
             "`default` is slower",
             "`default` does not compile with unions",
             "It is not worse"],
            0,
            "A default answers questions nobody has asked yet. For a closed list "
            "you own, you want the compiler to ask them."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — sendError: one place.
# ---------------------------------------------------------------------------

_M15_S3_SCRIPT = "\n".join([_POST_A, "GET /todos/9", "PATCH /todos/9 {}", "DELETE /todos/9",
                            "GET /nothing", 'POST /todos {"title":""}', "DELETE /todos/1", "GET /todos/1"])
_M15_S3_OUT = "\n".join(["201 " + _TODO_A, _NF, _NF, _NF, _NF, _v(_FE_EMPTY), "204", _NF])

_M15_GET_ROUTE_OK = """  if (req.method === "GET" && id !== undefined) {
    const todo = findTodo(id);
    if (todo === undefined) {
      sendError(res, { kind: "not_found" });"""

_M15_DELETE_ROUTE_OK = """    const removed = deleteTodo(id);
    if (!removed) {
      sendError(res, { kind: "not_found" });"""

assert _M15_HANDLER.count(_M15_GET_ROUTE_OK) == 1 and _M15_HANDLER.count(_M15_DELETE_ROUTE_OK) == 1

_M15_S3 = _pstep(
    "one-place", "`sendError`: one place",
    "Every route says what went wrong; one function says what that looks like.",
    """
With `errorReply` written, sending an error is two lines:

```ts
function sendError(res: ServerResponse, err: ApiError): void {
  const reply = errorReply(err);
  send(res, reply.status, reply.body);
}
```

Now go through the handler and replace every hand-written error:

```ts
send(res, 404, { error: "not_found" });                    // before
sendError(res, { kind: "not_found" });                     // after

send(res, 400, { error: "validation", fields: checked });  // before
sendError(res, { kind: "validation", fields: checked });   // after
```

Six replacements. When you are done, search the handler for `error:` — there
should be no hits. **No route writes an error body any more.**

### What just became impossible

| Bug | Before | Now |
|---|---|---|
| Status and body disagree | `send(res, 400, { error: "not_found" })` compiles | a route names a kind; the status comes with it |
| A code drifts | `{ error: "notfound" }` in one route compiles | `{ kind: "notfound" }` is a compile error |
| A validation 400 without its fields | `{ error: "validation" }` compiles | `{ kind: "validation" }` is missing `fields` — compile error |

The routes still say *where* things go wrong. They no longer get a say in what
a failure looks like on the wire.

### The one that got away

A refactor like this is only as good as its completeness. A route you missed
still compiles — `send` is still there, and still takes any status and any
object. That is why the search for `error:` matters, and it is what this step's
two fixes are: a route somebody missed.
""",
    """
```bash
$ grep -n 'error:' server.ts
(only inside errorReply)

$ curl -s -i localhost:3000/todos/9
HTTP/1.1 404 Not Found
{"error":"not_found"}

$ curl -s -i -X DELETE localhost:3000/todos/9
HTTP/1.1 404 Not Found
{"error":"not_found"}
```

Same bytes as before the refactor — which is the point of a refactor.
""",
    pitfalls=[
        "One route answers `{\"error\":\"notfound\"}` — it was missed in the refactor and still writes its body by hand. Search for `error:` outside `errorReply`.",
        "A missing todo answers `400 {\"error\":\"not_found\"}`. A hand-written status and body that disagree — the bug this module removes, surviving in a route nobody converted.",
        "Converting the routes but leaving the old bodies in `errorReply` subtly different — `\"not found\"` with a space. The refactor must not change a byte on the wire; compare before and after.",
        "Passing `sendError(res, { kind: \"validation\" })` without `fields`. It does not compile — the validation member requires them — which is the union doing its job.",
        "Sending a success through `sendError`. It is for failures; `send` and `sendEmpty` still answer the happy paths.",
    ],
    warmup=[
        _pq("After this step, where is the status code for \"not found\" written down?",
            ["Once — in `errorReply`'s `\"not_found\"` case",
             "In every route that can 404",
             "In `send`",
             "In the replayer"],
            0,
            "One copy of the contract. A route says *not found*; only "
            "`errorReply` knows that means 404."),
    ],
    exercises=[
        _pex("todo-m15-one-place-1", "Decide, then send",
             "Write the body of `sendError`: ask `errorReply` what the failure "
             "looks like, then send it.",
             _M15_FULL,
             """  const reply = errorReply(err);
  send(res, reply.status, reply.body);""",
             [(_M15_S3_SCRIPT, _M15_S3_OUT)],
             ["`errorReply(err)` answers with a status and a body.",
              "`send` takes both.",
              "`const reply = errorReply(err); send(res, reply.status, reply.body);`"]),
        _pfix("todo-m15-one-place-fix1", "The route that was missed",
              "`DELETE /todos/9` answers `404 {\"error\":\"notfound\"}`. Every "
              "other route spells it `not_found`, and a client checking for that "
              "breaks on this one.",
              _m15(_M15_HANDLER.replace(
                  _M15_DELETE_ROUTE_OK,
                  _M15_DELETE_ROUTE_OK.replace('sendError(res, { kind: "not_found" });',
                                               'send(res, 404, { error: "notfound" });'))),
              _M15_FULL,
              [(_M15_S3_SCRIPT, _M15_S3_OUT)],
              ["Which route answers differently?",
               "It writes its own body. Should any route?",
               "`sendError(res, { kind: \"not_found\" });`"],
              difficulty="Intro"),
        _pfix("todo-m15-one-place-fix2", "A 400 that says not found",
              "`GET /todos/9` answers `400 {\"error\":\"not_found\"}`. The body is "
              "right; the status says the *client* sent something wrong.",
              _m15(_M15_HANDLER.replace(
                  _M15_GET_ROUTE_OK,
                  _M15_GET_ROUTE_OK.replace('sendError(res, { kind: "not_found" });',
                                            'send(res, 400, { error: "not_found" });'))),
              _M15_FULL,
              [(_M15_S3_SCRIPT, _M15_S3_OUT)],
              ["The status and the body disagree. Where were they written?",
               "Neither should be written in a route at all.",
               "`sendError(res, { kind: \"not_found\" });`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why can `send(res, 400, { error: \"not_found\" })` not be caught by the compiler, when `sendError(res, { kind: \"not-found\" })` can?",
            ["`send` takes any number and any object; `sendError` takes an `ApiError`, whose tags are literal types",
             "Because 400 is not a valid status",
             "It can be caught either way",
             "Because `send` is older"],
            0,
            "The types are only as strict as the parameter. `object` accepts "
            "everything; `ApiError` accepts three shapes."),
        _pq("How do you find routes a refactor like this missed?",
            ["Search for error bodies (`error:`) outside `errorReply` — a missed route still compiles",
             "The compiler lists them",
             "They crash at startup",
             "The replayer reports them"],
            0,
            "`send` is still a valid function, so the old way still works. "
            "Completeness is on you — or on a test."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the refactor, and what it costs.
# ---------------------------------------------------------------------------

_M15_PATCH_ROUTE = """  if (req.method === "PATCH" && id !== undefined) {
    const todo = findTodo(id);
    if (todo === undefined) {
      sendError(res, { kind: "not_found" });
      return;
    }
    const body = await readBody(req);
    const data: unknown = JSON.parse(body);
    const checked = changesFrom(data);
    if (Array.isArray(checked)) {
      sendError(res, { kind: "validation", fields: checked });
      return;
    }
    const updated = updateTodo(todo, checked);
    send(res, 200, updated);
    return;
  }"""
assert _M15_HANDLER.count(_M15_PATCH_ROUTE) == 1

_M15_S4_SCRIPT = "\n".join([_POST_A, 'PATCH /todos/1 {"title":"","done":"yes"}', "PATCH /todos/2 {}",
                            'PATCH /todos/1 {"done":true}', "PATCH /todos/1 null"])
_M15_S4_OUT = "\n".join(["201 " + _TODO_A, _v(_FE_EMPTY, _FE_DONE), _NF, "200 " + _TODO_A_DONE, _v(_FE_BODY)])

_M15_S4 = _pstep(
    "refactor", "A refactor that changes nothing — on purpose",
    "What the union bought, what it cost, and the error it cannot send yet.",
    """
Put the handler from before this module next to the one after it. Every route
is the same length, give or take. The responses are byte-for-byte identical.
So what was the point?

### What moved

Knowledge. Before, *every route* knew that "not found" means 404 and a body of
`{"error":"not_found"}`. Now only `errorReply` knows. The routes know something
smaller and truer: *this is the place a todo might be missing.*

That is what "the contract lives in one place" means in practice:

* **Changing an error is one edit.** Add a `message` to every error body? One
  function.
* **Adding an error is guided.** A new kind fails to compile until
  `errorReply` handles it.
* **Reading the API is one function.** Every failure it can send, with its
  status, in one `switch`.

### What it cost

A type, a function and a helper — about twenty lines — and one more name to
learn. Worth it at six call sites. Not worth it at one: if your API had a single
error, a `send(res, 404, …)` would be fine. Abstractions pay for themselves in
the number of places they replace.

### The error you do not send yet

`server_error` has a case in `errorReply`, and nothing in your code sends it.
The replayer does — its boundary has turned every exception into
`500 {"error":"server_error"}` since module 4. Next module, that boundary becomes
yours, and it will say `sendError(res, { kind: "server_error" })`. It also adds a
fourth kind for bodies that are not JSON at all — and when it does, your
`never` line will fail the build, exactly as step 2 showed.
""",
    """
The PATCH route, rewritten, still answers:

```
PATCH /todos/1 {"title":"","done":"yes"}   400  both fields
PATCH /todos/2 {}                          404
PATCH /todos/1 {"done":true}               200
PATCH /todos/1 null                        400  body
```

— with no `error:` anywhere inside it.
""",
    pitfalls=[
        "Measuring a refactor by lines saved. This one saves almost none. It moves a decision into one place, which is what makes the *next* change cheap.",
        "Changing a response while refactoring. A refactor that alters output is two changes at once, and when a client breaks you will not know which one did it.",
        "Treating `server_error` as dead code and deleting it. It is part of the contract — clients see it today, from the replayer — and module 16 sends it.",
        "Building the union bigger than the API: kinds nothing will send \"for later\". Every kind is a promise to clients. Add them when a route needs one.",
    ],
    warmup=[
        _pq("After this module, what do the routes know about error responses?",
            ["Only *what* went wrong — the kind. Status and body are `errorReply`'s business",
             "Each route's status code",
             "The body format, but not the status",
             "Nothing; errors are sent by the replayer"],
            0,
            "Knowledge moved from six places to one. That is the whole refactor."),
    ],
    exercises=[
        _pch("todo-m15-refactor-1", "Rewrite the patch route", "Easy",
             "Write the `PATCH /todos/:id` route. Every failure leaves through "
             "`sendError`:\n\n"
             "* no todo with that id → `not_found` (before reading the body)\n"
             "* `changesFrom` answers with a list → `validation`, carrying it\n"
             "* otherwise apply the changes and answer 200 with the todo",
             _M15_FULL,
             _M15_PATCH_ROUTE,
             [(_M15_S4_SCRIPT, _M15_S4_OUT)],
             ["`if (req.method === \"PATCH\" && id !== undefined) { … }`",
              "Look up first: `const todo = findTodo(id);` — and `sendError(res, { kind: \"not_found\" })` if it is `undefined`.",
              "Then read, parse to `unknown`, and `changesFrom(data)`.",
              "`Array.isArray(checked)` → `sendError(res, { kind: \"validation\", fields: checked })`.",
              "Otherwise `send(res, 200, updateTodo(todo, checked))` — and `return` after every send."]),
        _pch("todo-m15-refactor-2", "Write errorReply", "Easy",
             "Write `errorReply(err)`: a `switch` on the kind, one `case` per "
             "member, and the `never` line after it.\n\n"
             "| kind | status | body |\n|---|---|---|\n"
             "| `not_found` | 404 | `{ error: \"not_found\" }` |\n"
             "| `validation` | 400 | `{ error: \"validation\", fields }` |\n"
             "| `server_error` | 500 | `{ error: \"server_error\" }` |",
             _m15_plain(),
             _M15_REPLY_BODY,
             [("", _M15_PLAIN_OUT)],
             ["`switch (err.kind) { … }`",
              "Each `case \"…\":` returns `{ status: …, body: { … } }`.",
              "Only in the `\"validation\"` case can you read `err.fields`.",
              "After the switch: `const unhandled: never = err; return unhandled;`"]),
    ],
    quiz=[
        _pq("The handler is about the same length after this module. What was gained?",
            ["The error contract lives in one function, so changing or adding an error is one guided edit",
             "Nothing — it is style",
             "Faster responses",
             "Smaller responses"],
            0,
            "Lines are the wrong measure. Count the places that must change when "
            "the contract does: six before, one after."),
        _pq("`server_error` has a case, and nothing in your code sends it. Why keep it?",
            ["Clients already receive it — from the replayer's boundary — and module 16 moves that boundary into your code",
             "For symmetry",
             "The compiler requires three members",
             "It should be deleted"],
            0,
            "The union describes the contract, and the 500 has been part of it "
            "since module 4."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M15_BUILD_BLANK = "\n\n".join(p.rstrip("\n") for p in (_M15_APIERROR, _M15_REPLY, _M15_SENDERROR))

_M15_FINAL = _pch(
    "todo-m15-build", "Module 15 build — one error shape, everywhere", "Medium",
    "Write the three pieces every route's failures now go through.\n\n"
    "* `ApiError` — a union of `not_found`, `validation` (carrying `fields: "
    "FieldError[]`) and `server_error`, each tagged with `kind`\n"
    "* `ErrorReply` and `errorReply(err)` — a `switch` on the kind returning the "
    "status and body, with the `never` line after it\n"
    "* `sendError(res, err)` — `errorReply`, then `send`\n\n"
    "The handler below already calls `sendError` everywhere. The script throws "
    "every failure the API has at it; the responses must be byte-for-byte what "
    "module 14 sent.",
    _M15_FULL,
    _M15_BUILD_BLANK,
    [("\n".join([_POST_A, "GET /todos/9", "GET /nope", "DELETE /todos/9", "PATCH /todos/9 {}",
                 'POST /todos {"title":""}', "POST /todos []",
                 'PATCH /todos/1 {"title":5,"done":"no"}', 'PATCH /todos/1 {"done":true}',
                 "DELETE /todos/1", "GET /todos/1", "GET /todos"]),
      "\n".join(["201 " + _TODO_A, _NF, _NF, _NF, _NF,
                 _v(_FE_EMPTY), _v(_FE_BODY), _v(_FE_STRING, _FE_DONE), "200 " + _TODO_A_DONE,
                 "204", _NF, "200 []"]))],
    ["`type ApiError = | { kind: \"not_found\" } | { kind: \"validation\"; fields: FieldError[] } | { kind: \"server_error\" };`",
     "`type ErrorReply = { status: number; body: object };`",
     "`errorReply`: `switch (err.kind)`, three `case`s that each `return`, then `const unhandled: never = err; return unhandled;`",
     "`sendError`: `const reply = errorReply(err); send(res, reply.status, reply.body);`"],
)


_TODO_MODULES.append(_pmod(
    key="todo-errors", number=15, phase="trust",
    title="One error shape, everywhere",
    what="a discriminated union, and a single place that turns it into a response",
    goal="Describe every failure the API can report as one union type, and turn it into a status and body in exactly one place.",
    why=_M15_WHY,
    est_minutes=50,
    builds_on=["todo-validate"],
    concepts=["literal types", "discriminated union", "switch", "narrowing by tag",
              "never", "exhaustiveness", "single source of truth", "refactoring"],
    deliverable="A handler in which no route writes an error body: every failure is "
                "an `ApiError`, and `errorReply` is the only place a kind becomes a "
                "status and a body.",
    objectives=[
        "Write a discriminated union with a literal `kind` tag, and say why the tag must be a literal",
        "Narrow a union member with `switch`, and read a field only the narrowed member has",
        "Use `never` to make a forgotten `case` a compile error, and read the message it produces",
        "Separate deciding a response (`errorReply`, pure) from sending it (`sendError`)",
        "Refactor every error in the handler through one function without changing a byte on the wire",
        "Say what an abstraction like this costs, and at how many call sites it pays for itself",
    ],
    endpoints=[
        _pep("*", "anything else", "Fall through — through `sendError`, like every failure now",
             "", '{"error":"not_found"}', "404"),
    ],
    brief=_M15_BRIEF,
    syntax=_M15_SYNTAX,
    steps=[_M15_S1, _M15_S2, _M15_S3, _M15_S4],
    final_build=_M15_FINAL,
    acceptance=[
        "`grep -n 'error:' server.ts` finds error bodies only inside `errorReply`.",
        "`curl -s -i localhost:3000/todos/9` still returns 404 and `{\"error\":\"not_found\"}` — byte-for-byte what module 14 sent.",
        "`curl -s -X POST localhost:3000/todos -d '{\"title\":\"\"}'` still returns the module-14 validation 400, fields and all.",
        "Deleting any `case` from `errorReply` makes `npx tsc --noEmit --strict server.ts` fail, naming the kind you removed.",
        "Changing a route to `sendError(res, { kind: \"not-found\" })` fails to compile.",
        "`errorReply` sends nothing and takes no `res` — you can call it and print the result.",
    ],
    manual_test="""
A refactor's manual test is a before-and-after. Before you change anything, save
what the old server says:

```bash
node server.ts &
for r in 'GET /todos/9' 'GET /nope' 'DELETE /todos/9'; do
  set -- $r; curl -s -X $1 localhost:3000$2; echo
done > before.txt
curl -s -X POST localhost:3000/todos -d '{"title":""}' >> before.txt
kill %1
```

Make this module's changes, run the same thing into `after.txt`, and:

```bash
diff before.txt after.txt && echo identical
```

Then try to break it on purpose, and watch the compiler refuse:

```bash
# in errorReply, delete the "server_error" case
npx tsc --noEmit --strict --noUncheckedIndexedAccess server.ts
# error TS2322: Type '{ kind: "server_error"; }' is not assignable to type 'never'.
```

Put the case back.
""",
    reference="""// server.ts — module 15
//
// One error shape, everywhere. Every failure the API reports is an ApiError —
// a union tagged by `kind` — and errorReply is the ONLY place a kind becomes a
// status and a body. No route writes an error body any more; each one says
// what went wrong, and nothing else.
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

// ---- errors ----------------------------------------------------------------
// Every failure the API can report, tagged by `kind`. A kind is a literal type,
// so a misspelt one is a compile error. `server_error` is what the replayer's
// boundary has sent on our behalf since module 4; module 16 makes it ours.
type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "server_error" };

type ErrorReply = {
  status: number;
  body: object;
};

// The ONE place a failure becomes a status and a body — so they can never
// disagree. Pure: it decides and sends nothing, which is what makes it testable.
function errorReply(err: ApiError): ErrorReply {
  switch (err.kind) {
    case "not_found":
      return { status: 404, body: { error: "not_found" } };
    case "validation":
      return { status: 400, body: { error: "validation", fields: err.fields } };
    case "server_error":
      return { status: 500, body: { error: "server_error" } };
  }
  // Every case returns, so `err` is `never` here — nothing is left for it to be.
  // Add a kind to ApiError without a case above and THIS line stops compiling,
  // naming the kind. The return only satisfies the return type; it cannot run.
  const unhandled: never = err;
  return unhandled;
}

function sendError(res: ServerResponse, err: ApiError): void {
  const reply = errorReply(err);
  send(res, reply.status, reply.body);
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
      sendError(res, { kind: "validation", fields: checked });
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
      sendError(res, { kind: "not_found" });
      return;
    }
    send(res, 200, todo);
    return;
  }

  if (req.method === "PATCH" && id !== undefined) {
    const todo = findTodo(id);                 // look up first: a bad body to a
    if (todo === undefined) {                  // missing todo is still a 404
      sendError(res, { kind: "not_found" });
      return;
    }
    const body = await readBody(req);
    const data: unknown = JSON.parse(body);
    const checked = changesFrom(data);
    if (Array.isArray(checked)) {
      sendError(res, { kind: "validation", fields: checked });
      return;
    }
    const updated = updateTodo(todo, checked);
    send(res, 200, updated);
    return;
  }

  if (req.method === "DELETE" && id !== undefined) {
    const removed = deleteTodo(id);
    if (!removed) {
      sendError(res, { kind: "not_found" });
      return;
    }
    sendEmpty(res, 204);
    return;
  }

  sendError(res, { kind: "not_found" });
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Add a human-readable `message` to every error body — `{\"error\":\"not_found\",\"message\":\"no todo with that id\"}`. Count the edits it takes: it should be one function.",
        "Give `not_found` an optional `id` and say which todo was missing. What does `errorReply` need, and what do the routes need? Is it worth it?",
        "Write `statusOf(kind)` as a lookup object — `{ not_found: 404, validation: 400, server_error: 500 }` — typed with `Record<ApiError[\"kind\"], number>`. Delete a key and watch the compiler complain without a `never` in sight. When would you prefer each?",
        "Read RFC 9457 (Problem Details for HTTP APIs). Map `ApiError` onto its `type`/`title`/`status` fields and decide what you would gain and lose by adopting it.",
    ],
    glossary=[
        _pgloss("literal type", "A type with exactly one value — `\"not_found\"` as a type. Makes a misspelt tag a compile error."),
        _pgloss("discriminated union", "A union of object types that share a field (the *tag* or *discriminant*, here `kind`) with a different literal type in each."),
        _pgloss("switch", "Compares one value against a list of `case`s. On a tag, each case narrows the union to its member."),
        _pgloss("fall through", "What a `case` with no `return` or `break` does: carries on into the next case. This track returns from every case."),
        _pgloss("never", "The type with no values. What a union narrows to once every member has been handled."),
        _pgloss("exhaustiveness check", "`const unhandled: never = err;` after a switch — compiles only if every member had a case, so a forgotten one is a build error."),
        _pgloss("single source of truth", "One place a fact is written down. Here: which status and body each failure gets."),
        _pgloss("refactor", "Changing code's structure without changing what it does. Tested by comparing output before and after."),
    ],
    cheatsheet="""
```ts
type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "server_error" };

type ErrorReply = { status: number; body: object };

// the ONE place a failure becomes a response — pure, so it can be tested
function errorReply(err: ApiError): ErrorReply {
  switch (err.kind) {
    case "not_found":
      return { status: 404, body: { error: "not_found" } };
    case "validation":                                   // err.fields exists only here
      return { status: 400, body: { error: "validation", fields: err.fields } };
    case "server_error":
      return { status: 500, body: { error: "server_error" } };
  }
  const unhandled: never = err;                          // a forgotten kind stops the build
  return unhandled;
}

function sendError(res: ServerResponse, err: ApiError): void {
  const reply = errorReply(err);
  send(res, reply.status, reply.body);
}

// in a route: say WHAT went wrong, nothing else
sendError(res, { kind: "not_found" });
sendError(res, { kind: "validation", fields: checked });
```

| You write | The compiler says |
|---|---|
| `{ kind: "not-found" }` | `Type '"not-found"' is not assignable … Did you mean '"not_found"'?` |
| `{ kind: "validation" }` | `Property 'fields' is missing` |
| `err.fields` in the `not_found` case | `Property 'fields' does not exist` |
| a kind with no `case` | `Type '{ kind: "…"; }' is not assignable to type 'never'` |

| Kind | Status | Body |
|---|---|---|
| `not_found` | 404 | `{"error":"not_found"}` |
| `validation` | 400 | `{"error":"validation","fields":[…]}` |
| `server_error` | 500 | `{"error":"server_error"}` — sent by the replayer until module 16 |
""",
    self_check=[
        "Can you say what a literal type is, and why the tag of a discriminated union must be one?",
        "Can you explain why `err.fields` compiles in one `case` and not another?",
        "Can you say what type `err` has after a `switch` that handled every kind — and what happens to the next line if one is missing?",
        "Can you say why `errorReply` takes no `res`?",
        "Can you name the two bugs that cannot be written any more, and the one way the old bug can still sneak in?",
        "Can you say why `server_error` is in the union when nothing in your code sends it?",
    ],
    review=[
        _pq("What makes `ApiError` a *discriminated* union rather than just a union?",
            ["Every member has a `kind` field with its own literal type, so checking `kind` tells you which member you hold",
             "It has more than two members",
             "It is declared with `type`",
             "Its members are objects"],
            0,
            "The discriminant is what lets the compiler narrow. Without it, "
            "several object shapes are indistinguishable."),
        _pq("`const unhandled: never = err;` after the switch — when does it fail to compile?",
            ["When some member of the union has no `case`, so `err` could still be that member",
             "Always — `never` cannot be assigned",
             "When the switch has a `default`",
             "At runtime, when an unknown kind arrives"],
            0,
            "It is a compile-time check that costs nothing at runtime — and names "
            "the kind that was forgotten."),
        _pq("Why is `errorReply` separate from `sendError`?",
            ["Deciding the response is pure and can be run and tested on its own; sending needs a live `res`",
             "`switch` cannot call `send`",
             "For speed",
             "Because `sendError` is given"],
            0,
            "Decide, then do. The deciding half is where the bugs are, and it is "
            "the half you can print."),
        _pq("After the refactor, a route still has `send(res, 404, { error: \"notfound\" })`. What catches it?",
            ["Nothing automatic — `send` accepts any object; you find it by searching, or a test does",
             "The `never` line",
             "The literal type on `kind`",
             "The replayer"],
            0,
            "The union protects every call that goes *through* it. A call that "
            "goes around it is invisible to it."),
        _pq("Module 16 will add `{ kind: \"invalid_json\" }`. What happens the moment it is added to the union?",
            ["`errorReply` stops compiling until it has a case for it",
             "Invalid JSON becomes a 500 automatically",
             "Nothing until a route sends it",
             "Every route must be changed"],
            0,
            "Step 2's lesson, cashed one module later."),
        _pq("When is an abstraction like `errorReply` *not* worth writing?",
            ["When it would replace one call site — the cost is fixed, the saving scales with the places it replaces",
             "Never; always write it",
             "When the API has more than three errors",
             "When the errors have bodies"],
            0,
            "Abstractions are paid for up front and repaid per use. Six uses "
            "repays it; one does not."),
    ],
    milestone="Every failure the API reports has one shape and one home. The "
              "routes say what went wrong; `errorReply` says what that looks like; "
              "and the compiler refuses a kind nobody handled.",
))
