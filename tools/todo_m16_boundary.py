# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 16 — The error boundary.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses modules 10-15's program pieces.
#
# CLOSES PHASE 4, and pays off three promises at once:
#
#   * `not json` BECOMES A 400. Modules 9, 11 and 13 all said the first module
#     with `catch` would do it. `parseJson` wraps `JSON.parse` in `try`/`catch`
#     and answers with a small union — `{ ok: true, data } | { ok: false }` — so
#     the routes never see the throw. A fourth kind, `invalid_json`, joins
#     `ApiError`, and module 15's `never` line makes the compiler point at
#     `errorReply` the moment it does. The module says so; it is the payoff.
#
#   * THE REPLAYER'S BOUNDARY BECOMES THE LEARNER'S. Since module 4 the given
#     replayer has wrapped every call to `handler` in a catch that turns an
#     escaping exception into `500 {"error":"server_error"}`. The roadmap asked
#     that this module be where the learner reads that code. It goes one
#     further: from this module on, the replayer (`_DRIVER_BARE`) starts the
#     server exactly the way the learner's own server.ts always has —
#     `createServer(handler)` — and has no catch at all. Which is the real
#     lesson: the learner's OWN server has had no boundary since module 4. The
#     judged programs now make that true for them too, so writing the boundary
#     is gradable: without it, the run crashes.
#
#   * `server_error` STARTS BEING SENT BY THE APP, through module 15's union.
#
# SOMETHING HAS TO THROW. The API has no bug that throws on ordinary input — the
# last three modules made sure of it — so there is a scaffolding route,
# `GET /boom`, that exists to throw, exactly as module 8's `/echo` existed to
# echo. Module 17 retires it in the contract data.
#
# THE GRADABLE BUGS: `instanceof Error` tested before `instanceof SyntaxError`
# (every parse failure reported as a refusal); a route still calling
# `JSON.parse` directly (a 500 where the contract says 400); no boundary at all
# (the process dies); a boundary whose `try` calls `route` without `await` (the
# rejection sails past the `catch` — the process dies); and a 500 that leaks
# the exception's text to the client. `headersSent` is taught and drilled but
# not graded as a fix: nothing in the API sends headers and then throws, and
# inventing a second scaffolding route to prove it was not worth the noise.
#
# NODE'S OWN ERROR MESSAGES ARE NEVER PRINTED to stdout. They differ between
# Node versions (`Unexpected token 'o', "not json" is not valid JSON` is 20+),
# and expected output has to be written down. Only messages the program itself
# chose appear in any expected output.
# ---------------------------------------------------------------------------

_M16_APIERROR = """type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "invalid_json" }
  | { kind: "server_error" };
"""

_M16_REPLY = _M15_REPLY.replace("""    case "server_error":""", """    case "invalid_json":
      return { status: 400, body: { error: "invalid_json" } };
    case "server_error":""")
assert _M16_REPLY != _M15_REPLY

_M16_PARSE = """type Parsed =
  | { ok: true; data: unknown }
  | { ok: false };

function parseJson(text: string): Parsed {
  try {
    return { ok: true, data: JSON.parse(text) };
  } catch {
    return { ok: false };
  }
}
"""

_M16_BOUNDARY = """async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  try {
    await route(req, res);
  } catch (err: unknown) {
    console.error(err);
    if (res.headersSent) {
      res.end();
      return;
    }
    sendError(res, { kind: "server_error" });
  }
}
"""

_M16_BOOM = """  if (req.method === "GET" && url.pathname === "/boom") {
    throw new Error("boom");
  }

"""


def _m16_parse_in(route, fn):
    """Swap one write route's bare JSON.parse for parseJson and a 400."""
    old = """    const body = await readBody(req);
    const data: unknown = JSON.parse(body);
    const checked = %s(data);""" % fn
    new = """    const body = await readBody(req);
    const parsed = parseJson(body);
    if (!parsed.ok) {
      sendError(res, { kind: "invalid_json" });
      return;
    }
    const checked = %s(parsed.data);""" % fn
    assert route.count(old) == 1, fn
    return route.replace(old, new)


_M16_ROUTE = _M15_HANDLER.replace("async function handler(", "async function route(")
_M16_ROUTE = _M16_ROUTE.replace('''  if (req.method === "POST" && url.pathname === "/todos") {''',
                                _M16_BOOM + '''  if (req.method === "POST" && url.pathname === "/todos") {''', 1)
_M16_ROUTE_PATCH_UNPARSED = _m16_parse_in(_M16_ROUTE, "createFrom")
_M16_ROUTE = _m16_parse_in(_M16_ROUTE_PATCH_UNPARSED, "changesFrom")
assert "JSON.parse" not in _M16_ROUTE


def _m16(route=_M16_ROUTE, boundary=_M16_BOUNDARY, parse=_M16_PARSE,
         apierror=_M16_APIERROR, reply=_M16_REPLY):
    """A module-16 server program: its own boundary, and a replayer without one."""
    return _server_bare("\n\n".join(p.rstrip("\n") for p in
                                    (_M10_STORE, _M10_SEND, _M10_READBODY,
                                     _M10_IDTEXT, _M10_PARSEID, _M10_TODOID,
                                     _M11_UPDATE, _M12_DELETE, _M12_SENDEMPTY,
                                     _M13_OBJECT, _M14_FIELDERROR, _M14_TITLE, _M14_DONE,
                                     _M14_CREATE, _M14_CHANGES,
                                     apierror, reply, _M15_SENDERROR,
                                     route, parse, boundary) if p))


_M16_FULL = _m16()

# --- Step 1's plain program: throw, catch, and what was caught --------------
_M16_DESCRIBE = """function describe(text: string): string {
  try {
    const data: unknown = JSON.parse(text);
    if (typeof data !== "number") {
      throw new Error("not a number");
    }
    return "number " + data;
  } catch (err: unknown) {
    if (err instanceof SyntaxError) {
      return "not JSON";
    }
    if (err instanceof Error) {
      return "refused: " + err.message;
    }
    return "something else";
  }
}
"""

_M16_S1_PRINTS = """
console.log(describe("42"));
console.log(describe("4 2"));
console.log(describe('"42"'));
console.log(describe("{"));
console.log(describe("null"));
console.log(describe(""));
console.log(describe("-7.5"));
"""
_M16_S1_OUT = "\n".join(["number 42", "not JSON", "refused: not a number", "not JSON",
                         "refused: not a number", "not JSON", "number -7.5"])


def _m16_s1(describe=_M16_DESCRIBE):
    return _plain(describe.rstrip("\n") + "\n" + _M16_S1_PRINTS)


_BADJSON = '400 {"error":"invalid_json"}'
_SERVER_ERR = '500 {"error":"server_error"}'

_M16_WHY = (
    "Two things in your API still end in a 500, and both are lies of a "
    "different kind. `POST /todos not json` answers \"something broke on our "
    "end\" when the client sent garbage — modules 9, 11 and 13 all promised the "
    "module with `catch` would fix it. And every 500 you have ever seen was "
    "written by the replayer, not by you: it has quietly wrapped your handler in "
    "a safety net since module 4. Your own `server.ts` has no such net. One "
    "exception in any route, and the process dies — taking every other "
    "request in flight with it."
)

_M16_BRIEF = """
### The whole module in one line

Catch what you expected to fail where it fails, and catch everything else at one
boundary — so a bug is a clean 500, never a dead server.

### Two kinds of failure

| | Expected | Unexpected |
|---|---|---|
| Example | the client sent `not json` | a bug in a route throws |
| Whose fault | the client's | yours |
| Where to catch it | right where it happens — around `JSON.parse` | once, around the whole handler |
| Answer | `400 {"error":"invalid_json"}` | `500 {"error":"server_error"}` |

### The net you did not know you had

Scroll down any program since module 4 and read the replayer:

```ts
const server = createServer((req, res) => {
  Promise.resolve(handler(req, res)).catch((err: unknown) => {
    console.error(err);
    if (res.headersSent) { res.end(); return; }
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end('{"error":"server_error"}');
  });
});
```

That `.catch` is an **error boundary**, and it has been answering for your bugs
all along. Your own `server.ts` says `createServer(handler)` — no boundary. **From
this module the replayer does the same**, so a throw that escapes `handler`
crashes the run. You write the boundary; then it is yours in both places.

### Four new words

```ts
throw new Error("boom");        // stop, and hand this error to whoever catches it
try { … } catch (err) { … }     // run this; if anything throws, run that instead
err instanceof SyntaxError      // what kind of error did I catch?
```

And `err` in a `catch` is `unknown` — module 13 all over again.
"""

_M16_SYNTAX = [
    _syn(
        'throw new Error("not a number");',
        "Stop running this function — and every function that called it — until "
        "something catches the error.",
        """
function half(n: number): number {
  if (n % 2 !== 0) {
    throw new Error("odd");
  }
  return n / 2;
}
""",
        "Nothing after a `throw` runs. It does not return; it unwinds.",
    ),
    _syn(
        "try {\n  …\n} catch (err: unknown) {\n  …\n}",
        "Run the `try` block. If anything in it throws — however deep — jump to "
        "the `catch` block, with the thrown value in `err`.",
        """
try {
  JSON.parse("not json");
  console.log("never printed");
} catch (err: unknown) {
  console.log("caught it");
}
""",
        "Under `strict`, `err` is `unknown`: anything can be thrown, not just "
        "errors. `catch {` with no variable is fine when you do not need it.",
    ),
    _syn(
        "err instanceof SyntaxError",
        "`true` if `err` was made by `new SyntaxError(…)` — or by anything built "
        "on it. Narrows `err` so you can read `.message`.",
        """
if (err instanceof Error) {
  console.log(err.message);   // err: Error
}
""",
        "`JSON.parse` throws a `SyntaxError`, which is a kind of `Error` — so "
        "`instanceof Error` is true for it too. Test the specific kind first.",
    ),
    _syn(
        "type Parsed =\n  | { ok: true; data: unknown }\n  | { ok: false };",
        "A union with a **boolean** tag: the value, or a note that there was "
        "none. `if (!parsed.ok)` narrows to the failure.",
        """
const parsed = parseJson(body);
if (!parsed.ok) {
  // no data here
} else {
  parsed.data;   // unknown
}
""",
        "Module 15's idea with a two-member union — where `true`/`false` is a "
        "perfectly good tag.",
    ),
    _syn(
        "res.headersSent",
        "`true` once the status line has gone to the client. After that a 500 "
        "cannot be sent — only the response can be ended.",
        """
if (res.headersSent) {
  res.end();
  return;
}
""",
        "Writing a second status throws — *inside the catch*, where nothing "
        "catches it.",
    ),
    _syn(
        "async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> { … }",
        "The function the server calls for every request. From this module it is "
        "the boundary, and the routes move into `route`.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — throw, try, catch.
# ---------------------------------------------------------------------------

_M16_S1 = _pstep(
    "throw", "Throw, try, catch",
    "What a throw does, what a `catch` receives, and telling one error from another.",
    """
Every function so far has reported failure by *returning* something:
`undefined`, a `FieldError`, a list. The caller checks, and decides. That is the
right tool when failure is ordinary — and it is the tool this track has used on
purpose.

`JSON.parse` does not work that way. Given text that is not JSON, it **throws**:

```ts
JSON.parse("not json");
console.log("this never runs");
```

A throw stops the function. And the function that called it. And the one that
called *that* — all the way up, until something **catches** it. If nothing does,
the program dies.

### Catching

```ts
try {
  const data: unknown = JSON.parse(text);
  // …only runs if the parse worked
} catch (err: unknown) {
  // …only runs if something in the try block threw
}
```

`err` is whatever was thrown. JavaScript lets you throw *anything* — a string, a
number, `null` — so the compiler types it `unknown`, and you narrow it like any
other value from outside.

### Throwing your own

```ts
throw new Error("not a number");
```

`new Error(message)` makes an error object with a `.message`. Throwing it hands
it to the nearest `catch`.

### What did I catch?

```ts
function describe(text: string): string {
  try {
    const data: unknown = JSON.parse(text);
    if (typeof data !== "number") {
      throw new Error("not a number");
    }
    return "number " + data;
  } catch (err: unknown) {
    if (err instanceof SyntaxError) {
      return "not JSON";
    }
    if (err instanceof Error) {
      return "refused: " + err.message;
    }
    return "something else";
  }
}
```

One `catch`, two kinds of failure: `JSON.parse`'s `SyntaxError`, and our own
`Error`. `instanceof` asks which constructor made the object — and narrows `err`
so `.message` can be read.

**Order matters.** A `SyntaxError` *is* an `Error` — built on it — so
`err instanceof Error` is true for both. Ask the specific question first.

### Returning versus throwing

Use a return value when failure is part of the job — a client *will* send an
empty title. Use a throw when failure means the job cannot continue at all.
The rest of this module needs both.
""",
    """
Your `describe` answers:

```
42        number 42
4 2       not JSON
"42"      refused: not a number
{         not JSON
null      refused: not a number
(empty)   not JSON
-7.5      number -7.5
```

If the `not JSON` lines come out as `refused: …` with a message you did not
write, the two `instanceof` checks are in the wrong order.
""",
    pitfalls=[
        "Every parse failure is reported as `refused: Unexpected token …` — `instanceof Error` is tested before `instanceof SyntaxError`, and a `SyntaxError` is an `Error`. Specific first.",
        "`Property 'message' does not exist on type 'unknown'` — reading `err.message` without narrowing. Anything can be thrown; `instanceof Error` proves it is an error.",
        "`catch (err: Error)` — does not compile. TypeScript only allows `unknown` (or `any`) there, because it cannot know what was thrown.",
        "Printing `err.message` from `JSON.parse` to a client or a test. Its wording differs between Node versions — and, next step, it is none of the client's business.",
        "Wrapping everything in `try` \"to be safe\". A `catch` that does not know what it caught cannot do anything sensible with it. Catch where you can *answer*.",
    ],
    warmup=[
        _pq("`JSON.parse(\"{\")` inside a `try`. What does the `catch` receive?",
            ["A `SyntaxError` — which is also an `Error`",
             "The string `\"{\"`",
             "`undefined`",
             "Nothing; `JSON.parse` returns `null` on bad input"],
            0,
            "Which is why the specific `instanceof` has to come first."),
        _pq("Under `strict`, what type is `err` in `catch (err)`?",
            ["`unknown` — anything at all can be thrown",
             "`Error`",
             "`any`",
             "`string`"],
            0,
            "A caught value comes from outside your control, exactly like a parsed "
            "body. Module 13's rules apply."),
    ],
    exercises=[
        _pex("todo-m16-throw-1", "Which error was it?",
             "`JSON.parse` failed. Recognise its kind of error and answer "
             "`not JSON`.",
             _m16_s1(),
             "err instanceof SyntaxError",
             [("", _M16_S1_OUT)],
             ["`JSON.parse` throws one particular kind of error.",
              "Ask whether `err` was made by that constructor.",
              "`err instanceof SyntaxError`"]),
        _pfix("todo-m16-throw-fix1", "Every error is an Error",
              "`describe(\"4 2\")` answers `refused: …` followed by a message "
              "nobody in this program wrote. So does every other text that is not "
              "JSON.",
              _m16_s1(_M16_DESCRIBE.replace("""    if (err instanceof SyntaxError) {
      return "not JSON";
    }
    if (err instanceof Error) {
      return "refused: " + err.message;
    }""", """    if (err instanceof Error) {
      return "refused: " + err.message;
    }
    if (err instanceof SyntaxError) {
      return "not JSON";
    }""")),
              _m16_s1(),
              [("", _M16_S1_OUT)],
              ["Is a `SyntaxError` an `Error`?",
               "Which check does a `SyntaxError` reach first?",
               "Ask `instanceof SyntaxError` before `instanceof Error`."],
              difficulty="Easy"),
        _pex("todo-m16-throw-2", "Refuse by throwing",
             "The parse worked, but the value is not a number. Stop, and hand the "
             "`catch` an error whose message is `not a number`.",
             _m16_s1(),
             'throw new Error("not a number");',
             [("", _M16_S1_OUT)],
             ["Make an error object with that message.",
              "Then hand it up to the `catch` — not with `return`.",
              '`throw new Error("not a number");`']),
    ],
    quiz=[
        _pq("A function three calls deep throws. What runs next?",
            ["The nearest enclosing `catch`, however many calls up — or, if there is none, the program dies",
             "The next line of that function",
             "The next line of the caller",
             "Nothing; a throw is ignored without a `catch`"],
            0,
            "A throw unwinds through every caller until something catches it. "
            "That reach is what makes one boundary enough."),
        _pq("When is returning a failure better than throwing one?",
            ["When failure is an ordinary answer the caller must handle — like a client's bad title",
             "Never; throwing is always cleaner",
             "Only in async functions",
             "When the function returns a string"],
            0,
            "A return value is in the signature, so the compiler makes the caller "
            "deal with it. A throw is invisible in the types."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — not json is a 400.
# ---------------------------------------------------------------------------

_M16_S2_SCRIPT = "\n".join([_POST_A, "POST /todos not json", "POST /todos {", "PATCH /todos/1 not json",
                            "PATCH /todos/9 not json", 'PATCH /todos/1 {"done":true}', "GET /todos"])
_M16_S2_OUT = "\n".join(["201 " + _TODO_A, _BADJSON, _BADJSON, _BADJSON, _NF,
                         "200 " + _TODO_A_DONE, "200 [" + _TODO_A_DONE + "]"])

_M16_S2 = _pstep(
    "json", "Not JSON is a 400",
    "`parseJson`, a union with a boolean tag, and the fourth kind of `ApiError`.",
    """
The client sent `not json`. Whose fault is that? The client's — so it is a 4xx,
and modules 9, 11 and 13 all promised this module would make it one.

Catch it **where it happens**, and turn the throw back into an ordinary value:

```ts
type Parsed =
  | { ok: true; data: unknown }
  | { ok: false };

function parseJson(text: string): Parsed {
  try {
    return { ok: true, data: JSON.parse(text) };
  } catch {
    return { ok: false };
  }
}
```

The throw never leaves `parseJson`. Callers get a union — module 15's idea with
two members and a `true`/`false` tag — and the compiler makes them check it:

```ts
const body = await readBody(req);
const parsed = parseJson(body);
if (!parsed.ok) {
  sendError(res, { kind: "invalid_json" });
  return;
}
const checked = createFrom(parsed.data);    // parsed.data exists only when ok
```

`catch {` with no variable says "I know what failed, and I do not need the
details" — the only thing `JSON.parse` can throw is a `SyntaxError`.

### A fourth kind of failure

```ts
type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "invalid_json" }                     // new
  | { kind: "server_error" };
```

Add that line and **the build fails**:

```
Type '{ kind: "invalid_json"; }' is not assignable to type 'never'.
```

Module 15's `never` line, doing exactly what it was put there to do: naming the
one place that has to learn about the new kind. Add the case —

```ts
    case "invalid_json":
      return { status: 400, body: { error: "invalid_json" } };
```

— and it compiles again.

### Why a new kind, and not a validation error?

`{"field":"body","message":"must be a JSON object"}` means *the JSON was fine
and was the wrong shape*. `not json` never got as far as having a shape. A
client that sees `invalid_json` knows to look at how it is **encoding** the
request, not at what it put in it.

### Still lookup first

`PATCH /todos/9 not json` is a 404. There is nothing at that address for the
body to be malformed about.
""",
    """
```bash
$ curl -s -i -X POST localhost:3000/todos -d 'not json'
HTTP/1.1 400 Bad Request
{"error":"invalid_json"}

$ curl -s -i -X PATCH localhost:3000/todos/1 -d '{'
HTTP/1.1 400 Bad Request
{"error":"invalid_json"}
```

`grep JSON.parse server.ts` finds exactly one line: inside `parseJson`.
""",
    pitfalls=[
        "`POST /todos not json` is a 400 and `PATCH /todos/1 not json` is still a 500 — one route still calls `JSON.parse` directly. Search for it: it should appear once, inside `parseJson`.",
        "Reading `parsed.data` before checking `parsed.ok`. It does not compile — `data` only exists on the success member.",
        "Reporting bad JSON as a validation error on `body`. That says the JSON was the wrong *shape*; this JSON has no shape at all.",
        "Wrapping the whole route in `try` to catch the parse. It catches the parse — and every bug below it, all reported as `invalid_json`: a bug of yours blamed on the client.",
        "Parsing before the lookup. `PATCH /todos/9 not json` is a 404.",
    ],
    warmup=[
        _pq("You add `{ kind: \"invalid_json\" }` to `ApiError`. What happens before you do anything else?",
            ["The build fails at `errorReply`'s `never` line, naming `invalid_json`",
             "Nothing — the union just grows",
             "Every route stops compiling",
             "Bad JSON becomes a 400 automatically"],
            0,
            "Module 15 put that line there for exactly this moment."),
    ],
    exercises=[
        _pch("todo-m16-json-1", "Catch the parse", "Easy",
             "Write the body of `parseJson`: try to parse `text`; answer `{ ok: "
             "true, data }` if it worked and `{ ok: false }` if it threw.",
             _M16_FULL,
             """  try {
    return { ok: true, data: JSON.parse(text) };
  } catch {
    return { ok: false };
  }""",
             [(_M16_S2_SCRIPT, _M16_S2_OUT)],
             ["`try { … } catch { … }` — you do not need the error itself.",
              "Inside the `try`: `return { ok: true, data: JSON.parse(text) };`",
              "Inside the `catch`: `return { ok: false };`"]),
        _pfix("todo-m16-json-fix1", "The route that still trusts JSON.parse",
              "`POST /todos not json` answers `400 {\"error\":\"invalid_json\"}`. "
              "`PATCH /todos/1 not json` answers `500 {\"error\":\"server_error\"}` "
              "— the client's mistake, reported as ours.",
              _m16(_M16_ROUTE_PATCH_UNPARSED),
              _M16_FULL,
              [(_M16_S2_SCRIPT, _M16_S2_OUT)],
              ["Search the routes for `JSON.parse`.",
               "One route still parses on its own, and the throw goes all the way up to the boundary.",
               "`const parsed = parseJson(body); if (!parsed.ok) { sendError(res, { kind: \"invalid_json\" }); return; } const checked = changesFrom(parsed.data);`"],
              difficulty="Easy"),
        _pex("todo-m16-json-2", "The fourth case",
             "`invalid_json` is in the union and `errorReply` has no case for it — "
             "the build says so. It is a 400 with body `{ error: \"invalid_json\" }`.",
             _M16_FULL,
             """    case "invalid_json":
      return { status: 400, body: { error: "invalid_json" } };""",
             [(_M16_S2_SCRIPT, _M16_S2_OUT)],
             ["The compiler named the kind. Add a `case` for it.",
              "It is the client's fault, so a 4xx.",
              '`case "invalid_json": return { status: 400, body: { error: "invalid_json" } };`']),
    ],
    quiz=[
        _pq("Why catch the parse inside `parseJson` rather than around the whole route?",
            ["So only a parse failure becomes `invalid_json` — a bug further down is not blamed on the client",
             "`try` cannot contain `await`",
             "It is faster",
             "The compiler requires it"],
            0,
            "Catch where you know what failed. A wide `catch` answers questions it "
            "does not understand."),
        _pq("Why is `not json` a new kind rather than a `body` validation error?",
            ["A validation error means the JSON had the wrong shape; this text never became JSON at all",
             "Because it needs a different status",
             "No reason; either is right",
             "Because validation errors cannot name `body`"],
            0,
            "Different mistake, different fix on the client: one is about content, "
            "the other about encoding."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — the boundary.
# ---------------------------------------------------------------------------

_M16_S3_SCRIPT = "\n".join([_POST_A, "GET /boom", "GET /todos/1", "GET /boom", _POST_B, "GET /todos"])
_M16_S3_OUT = "\n".join(["201 " + _TODO_A, _SERVER_ERR, "200 " + _TODO_A, _SERVER_ERR,
                         "201 " + _TODO_B, "200 [" + _TODO_A + "," + _TODO_B + "]"])

_M16_NO_BOUNDARY = _M16_ROUTE.replace("async function route(", "async function handler(")

_M16_S3 = _pstep(
    "boundary", "The boundary you were borrowing",
    "One `try` around every route, `await` inside it, and a replayer with no net.",
    """
Look at the last few lines of any program from modules 4 to 15. The replayer
started your server like this:

```ts
const server = createServer((req, res) => {
  Promise.resolve(handler(req, res)).catch((err: unknown) => {
    console.error(err);
    if (res.headersSent) { res.end(); return; }
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end('{"error":"server_error"}');
  });
});
```

Every 500 you have seen came from that `.catch`. It is an **error boundary**:
one place, around everything, that turns an exception nobody expected into a
response instead of a crash.

Now look at the bottom of your own `server.ts`:

```ts
const server = createServer(handler);
```

No boundary. Since module 8 your handler has been `async`, so an exception in it
becomes a *rejected promise* that nothing handles — and Node's answer to an
unhandled rejection is to **stop the process**. One bug in one route, and every
client of your server is disconnected.

**From this module, the replayer starts your server the same way** — the bottom
of every program now says `createServer(handler)`. So the boundary has to be
yours.

### Write it

Rename your handler to `route`, and write a new `handler` that calls it:

```ts
async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  try {
    await route(req, res);
  } catch (err: unknown) {
    console.error(err);
    if (res.headersSent) {
      res.end();
      return;
    }
    sendError(res, { kind: "server_error" });
  }
}
```

Three things to see in it:

* **`await route(req, res)`** — the `await` is not decoration. `route` is async;
  without `await` the `try` block finishes the instant the promise is *created*,
  and a rejection a moment later sails straight past the `catch`. A boundary that
  catches nothing.
* **`console.error(err)`** — the full error, stack trace and all, goes to *your*
  log. You need it to fix the bug.
* **`sendError(res, { kind: "server_error" })`** — and the client gets the same
  plain 500 as every other failure, through module 15's union. Its case has
  been waiting since last module.

### Something that throws

The API has no bug that throws on ordinary input — the last three modules made
sure of that. So there is a route that exists only to throw, the way module 8's
`/echo` existed only to echo:

```ts
if (req.method === "GET" && url.pathname === "/boom") {
  throw new Error("boom");
}
```

`GET /boom` with the boundary: a 500, and the server carries on answering. Without
it: the process dies. Module 17 deletes the route.
""",
    """
```bash
$ curl -s -i localhost:3000/boom
HTTP/1.1 500 Internal Server Error
{"error":"server_error"}

$ curl -s localhost:3000/todos        # still up
[…]
```

And in the terminal running the server, the whole stack trace — `Error: boom`,
with the line it came from.
""",
    pitfalls=[
        "The first `GET /boom` kills the server — there is no boundary, and the replayer (like your `server.ts`) no longer has one either.",
        "The boundary is there and the server still dies: `try { route(req, res); }` without `await`. The `try` ends before the promise rejects. `await` it.",
        "Swallowing the error — a `catch` that sends the 500 and logs nothing. The client is fine; you have no idea anything went wrong, or where.",
        "A `try` inside every route instead of one around all of them. Six copies of the same `catch`, and the seventh route someone adds has none.",
        "Keeping `/boom` in a real server. It is scaffolding; module 17 retires it.",
    ],
    warmup=[
        _pq("`try { route(req, res); } catch { … }` — `route` is async and rejects. What happens?",
            ["The `catch` never runs — the `try` finished when the promise was created — and the rejection is unhandled",
             "The `catch` runs",
             "The rejection is ignored safely",
             "It does not compile"],
            0,
            "A `try` can only catch what happens while it is running. `await` "
            "keeps it running until the promise settles."),
    ],
    exercises=[
        _pfix("todo-m16-boundary-fix1", "The server that dies",
              "The first `GET /boom` kills the whole process: every request after "
              "it gets no answer at all. Nothing catches what a route throws.\n\n"
              "Rename the handler to `route`, and write a new `handler` around it "
              "that turns anything it throws into a `server_error`.",
              _m16(_M16_NO_BOUNDARY, boundary=""),
              _M16_FULL,
              [(_M16_S3_SCRIPT, _M16_S3_OUT)],
              ["Who catches an error thrown in a route? Read the bottom of the program.",
               "`async function handler(req, res) { try { await route(req, res); } catch (err: unknown) { … } }`",
               "In the `catch`: log it with `console.error(err)`, then `sendError(res, { kind: \"server_error\" })`.",
               "Keep the `res.headersSent` check from the old replayer, too."],
              difficulty="Medium"),
        _pfix("todo-m16-boundary-fix2", "A boundary that catches nothing",
              "There is a `try` and a `catch` around every route, and the first "
              "`GET /boom` still kills the process.",
              _m16(boundary=_M16_BOUNDARY.replace("    await route(req, res);", "    route(req, res);")),
              _M16_FULL,
              [(_M16_S3_SCRIPT, _M16_S3_OUT)],
              ["`route` is `async`. What does calling it return?",
               "When does the `try` block finish — before or after that promise rejects?",
               "`await route(req, res);`"],
              difficulty="Easy"),
        _pex("todo-m16-boundary-1", "Answer for the bug",
             "Something in a route threw, and nothing has been sent yet. Answer the "
             "client with the API's server error.",
             _M16_FULL,
             '    sendError(res, { kind: "server_error" });\n  }\n}',
             [(_M16_S3_SCRIPT, _M16_S3_OUT)],
             ["Every failure leaves through one function.",
              "The kind for \"our fault\" has had a case since module 15.",
              '`sendError(res, { kind: "server_error" });` — and close the `catch` and the function.']),
    ],
    quiz=[
        _pq("Why one boundary around `route`, rather than a `try` in every route?",
            ["One place catches everything a route can throw — including routes nobody has written yet",
             "`try` is slow",
             "Routes cannot contain `try`",
             "There is no difference"],
            0,
            "A throw unwinds through every caller, so one `catch` at the top sees "
            "all of them. That reach is the point."),
        _pq("What did your own `server.ts` do, from module 8 to 15, when a route threw?",
            ["Crashed — `createServer(handler)` had no boundary; only the replayer did",
             "Answered 500",
             "Ignored it",
             "Answered 404"],
            0,
            "The judged programs were safer than the real thing. As of this module "
            "they are the same."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — what a 500 must not say.
# ---------------------------------------------------------------------------

_M16_LEAKY = _M16_BOUNDARY.replace('    sendError(res, { kind: "server_error" });',
                                   '    send(res, 500, { error: "server_error", detail: String(err) });')

_M16_S4_SCRIPT = "\n".join(["GET /boom", _POST_A, "POST /todos not json", "GET /todos/1"])
_M16_S4_OUT = "\n".join([_SERVER_ERR, "201 " + _TODO_A, _BADJSON, "200 " + _TODO_A])

_M16_S4 = _pstep(
    "leaks", "What a 500 must not say",
    "The log gets the details; the client gets two words. And the one thing that cannot be undone.",
    """
It is tempting to be helpful:

```ts
send(res, 500, { error: "server_error", detail: String(err) });
```

```
500 {"error":"server_error","detail":"Error: boom"}
```

Now imagine the error was not `boom`. Real exceptions say things like
*`ENOENT: no such file or directory, open '/srv/app/secrets/db.json'`* or
*`duplicate key value violates unique constraint "users_email_key"`*. Each one
tells a stranger how your server is laid out, what it runs on, and where to
push. An attacker's first job is to make your server throw and read what comes
back.

So the rule is absolute: **the details go to your log; the client gets
`{"error":"server_error"}`.**

| Audience | Gets | Because |
|---|---|---|
| You, in the log | the whole error and stack trace | you need it to fix the bug |
| The client | `500 {"error":"server_error"}` | it cannot fix your bug, and must not learn from it |

A 500 is *our* fault. Nothing in its body helps the client do anything
differently — which is exactly why it should say nothing.

### The one thing that cannot be undone

What if a route sends its answer, and *then* throws?

```ts
send(res, 200, todo);
somethingThatThrows();
```

The status line has gone. HTTP has no way to take it back, and calling
`writeHead` again throws — *inside your `catch`*, where nothing catches it, so
the process dies after all. That is what the check is for:

```ts
if (res.headersSent) {
  res.end();
  return;
}
```

If the answer has started, finish it and stop; the client has what it has. Only
if nothing has gone yet is there still a choice to make. Nothing in this API
sends and then throws today — but module 19 writes to disk after every change,
and a disk can fail.
""",
    """
```bash
$ curl -s localhost:3000/boom
{"error":"server_error"}
```

Two words for the client — and in your terminal, the whole story:

```
Error: boom
    at route (server.ts:…)
```
""",
    pitfalls=[
        "A 500 whose body includes the error text — `{\"error\":\"server_error\",\"detail\":\"Error: boom\"}`. Real error messages carry file paths, queries and versions. Log them; never send them.",
        "Sending `err.stack` \"only in development\" behind a flag. Flags get left on. The log is where development details belong.",
        "Leaving out the `headersSent` check. If a route has already answered, `writeHead` throws inside the `catch` — and that throw kills the process.",
        "Logging with `console.log`. The judge — and plenty of real log setups — treats stdout as the program's output. Errors go to `console.error`.",
    ],
    warmup=[
        _pq("Why should a 500's body say nothing about the error?",
            ["The client cannot fix the server's bug, and the details tell an attacker about your system",
             "To keep responses small",
             "Because JSON cannot hold stack traces",
             "It should include the message"],
            0,
            "4xx bodies help the client fix *its* request. A 5xx body has nothing "
            "the client can act on — only things it should not know."),
    ],
    exercises=[
        _pfix("todo-m16-leaks-fix1", "A helpful 500",
              "`GET /boom` answers `500 {\"error\":\"server_error\",\"detail\":\"Error: boom\"}`. "
              "Every exception's text is now sent to whoever caused it.",
              _m16(boundary=_M16_LEAKY),
              _M16_FULL,
              [(_M16_S4_SCRIPT, _M16_S4_OUT)],
              ["Who needs the error's details — the client, or you?",
               "The details are already in the log, one line up.",
               "Send the API's plain server error: `sendError(res, { kind: \"server_error\" });`"],
              difficulty="Easy"),
        _pex("todo-m16-leaks-1", "Too late for a 500",
             "Before sending a 500, check whether the route already answered. If "
             "it has, only ending the response is still possible.",
             _M16_FULL,
             "res.headersSent",
             [(_M16_S4_SCRIPT, _M16_S4_OUT)],
             ["`res` knows whether its status line has gone out.",
              "It is a property, not a method.",
              "`res.headersSent`"]),
    ],
    quiz=[
        _pq("A route has already sent `200` and then throws. What can the boundary still do?",
            ["End the response — the status has gone and cannot be replaced",
             "Send a 500 instead",
             "Send a second body",
             "Nothing; the request hangs"],
            0,
            "HTTP sends the status first. Once it is out, the only choices left "
            "are finishing and stopping."),
        _pq("Where do the details of a 500 belong?",
            ["In the server's log, via `console.error` — never in the response",
             "In the response body, for debugging",
             "In a response header",
             "Nowhere; discard them"],
            0,
            "Discarding them leaves you blind; sending them arms an attacker. The "
            "log is the one audience that needs them."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

# parseJson sits directly above the boundary in every program, so the build can
# blank both as one region.
_M16_BUILD_BLANK = "\n\n".join(p.rstrip("\n") for p in (_M16_PARSE, _M16_BOUNDARY))

_M16_FINAL = _pch(
    "todo-m16-build", "Module 16 build — a clean 500, never a dead server", "Medium",
    "Write `parseJson` and the boundary.\n\n"
    "* `Parsed` — `{ ok: true; data: unknown } | { ok: false }`\n"
    "* `parseJson(text)` — `JSON.parse` inside a `try`; `{ ok: false }` if it "
    "throws\n"
    "* `handler(req, res)` — awaits `route`; anything it throws is logged, and "
    "answered with a `server_error` unless the response has already started\n\n"
    "The routes above already call `parseJson` and answer `invalid_json`. The "
    "replayer below has no safety net: if your boundary misses a throw, the run "
    "dies.",
    _M16_FULL,
    _M16_BUILD_BLANK,
    [("\n".join([_POST_A, "POST /todos not json", 'POST /todos {"title":', "GET /boom",
                 "PATCH /todos/1 nope", "PATCH /todos/2 nope", 'PATCH /todos/1 {"done":"yes"}',
                 "GET /boom", 'PATCH /todos/1 {"done":true}', _POST_B, "DELETE /todos/2", "GET /todos"]),
      "\n".join(["201 " + _TODO_A, _BADJSON, _BADJSON, _SERVER_ERR,
                 _BADJSON, _NF, _v(_FE_DONE),
                 _SERVER_ERR, "200 " + _TODO_A_DONE, "201 " + _TODO_B, "204",
                 "200 [" + _TODO_A_DONE + "]"]))],
    ["`type Parsed = | { ok: true; data: unknown } | { ok: false };`",
     "`parseJson`: `try { return { ok: true, data: JSON.parse(text) }; } catch { return { ok: false }; }`",
     "`handler`: `try { await route(req, res); } catch (err: unknown) { … }` — the `await` is what makes the `catch` reachable.",
     "In the `catch`: `console.error(err)`; if `res.headersSent`, `res.end()` and return; otherwise `sendError(res, { kind: \"server_error\" })`.",
     "Two `GET /boom`s, and the server answers everything after both."],
)


_TODO_MODULES.append(_pmod(
    key="todo-boundary", number=16, phase="trust",
    title="The error boundary",
    what="try/catch, headersSent, and never leaking a stack trace",
    goal="Turn a body that is not JSON into a 400 where it happens, and every unexpected exception into a clean 500 at one boundary — so a bug never takes the server down.",
    why=_M16_WHY,
    est_minutes=60,
    builds_on=["todo-errors"],
    concepts=["throw", "try/catch", "catch variables are unknown", "instanceof",
              "expected vs unexpected failure", "error boundary", "unhandled rejection",
              "information leakage", "headersSent"],
    deliverable="A server where `not json` is `400 {\"error\":\"invalid_json\"}`, and "
                "an exception in any route is logged in full and answered with a "
                "plain 500 — while the server carries on.",
    objectives=[
        "Throw an error, catch it, and say where control goes in between",
        "Narrow a caught `unknown` with `instanceof`, testing the specific kind of error before the general one",
        "Catch an expected failure where it happens and turn it back into an ordinary value",
        "Add a kind to `ApiError` and follow the compiler to the one place that must change",
        "Write an error boundary around every route, and say why it needs `await`",
        "Say what a 500 must never contain, where those details go instead, and what `headersSent` protects",
    ],
    endpoints=[
        _pep("POST", "/todos", "Create a todo — bad JSON is the client's 400 at last",
             '{"title":"Buy milk"}', "Todo, with the id you assigned", "201 · 400"),
        _pep("PATCH", "/todos/:id", "Change title and/or done — bad JSON is a 400",
             '{"done":true}', "Todo, as it now is", "200 · 400 · 404"),
        _pep("GET", "/boom", "Scaffolding — a route that exists to throw, so the boundary has something to catch",
             "", '{"error":"server_error"}', "500"),
        _pep("*", "anything else", "Fall through — through `sendError`, like every failure now",
             "", '{"error":"not_found"}', "404"),
    ],
    brief=_M16_BRIEF,
    syntax=_M16_SYNTAX,
    steps=[_M16_S1, _M16_S2, _M16_S3, _M16_S4],
    final_build=_M16_FINAL,
    acceptance=[
        "`curl -s -i -X POST localhost:3000/todos -d 'not json'` returns 400 and `{\"error\":\"invalid_json\"}`.",
        "`curl -s -i -X PATCH localhost:3000/todos/1 -d 'not json'` returns 400; for a todo that does not exist, 404.",
        "`grep -n 'JSON.parse' server.ts` finds exactly one line, inside `parseJson`.",
        "`curl -s -i localhost:3000/boom` returns 500 and exactly `{\"error\":\"server_error\"}` — nothing else in the body.",
        "After `GET /boom`, the server still answers `GET /todos`.",
        "The terminal running the server shows the full `Error: boom` stack trace for every `/boom`.",
        "Removing the `await` in the boundary makes `GET /boom` crash the server — and putting it back fixes it.",
        "No response the API sends is a 500 for anything a client did.",
    ],
    manual_test="""
First, prove the danger to yourself. Before writing the boundary, add only the
`/boom` route, start the server, and:

```bash
curl -s localhost:3000/boom
curl -s localhost:3000/todos
```

The first gets no reply — `curl: (52) Empty reply from server` — and the second
cannot connect. Look at the terminal: the process has exited. That is what your
server has been one exception away from since module 8.

Now write the boundary, restart, and do it again:

```bash
curl -s -i localhost:3000/boom          # 500 {"error":"server_error"}
curl -s localhost:3000/todos            # still here
```

And the client's mistakes, which are no longer ours:

```bash
curl -s -i -X POST localhost:3000/todos -d 'not json'   # 400 invalid_json
curl -s -i -X POST localhost:3000/todos -d '{"title":'  # 400 invalid_json
curl -s -i -X POST localhost:3000/todos -d '{"title":""}'   # 400 validation
```

Last, check the log. Every `/boom` should have printed a stack trace to the
server's terminal — and none of it should appear in any response.
""",
    reference="""// server.ts — module 16
//
// Expected failures are caught where they happen: text that is not JSON is the
// client's 400, turned back into an ordinary value by parseJson. Unexpected ones
// are caught once, at the boundary around every route: logged in full, answered
// with a plain 500, and the server carries on. Until this module, one exception
// in any async route would have crashed this process.
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
// so a misspelt one is a compile error. Adding `invalid_json` here is what made
// errorReply's `never` line fail until it had a case — module 15's payoff.
type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "invalid_json" }
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
    case "invalid_json":
      return { status: 400, body: { error: "invalid_json" } };
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

// JSON.parse THROWS on text that is not JSON — the client's mistake, and an
// expected one. It is caught here, where we know exactly what failed, and turned
// back into an ordinary value the routes must check. This is the only JSON.parse
// in the file.
type Parsed =
  | { ok: true; data: unknown }
  | { ok: false };

function parseJson(text: string): Parsed {
  try {
    return { ok: true, data: JSON.parse(text) };
  } catch {
    return { ok: false };
  }
}

async function route(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const id = todoId(url.pathname);

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  // Scaffolding, like module 8's /echo: nothing in this API throws on ordinary
  // input, so this route exists to prove the boundary works. Module 17 deletes it.
  if (req.method === "GET" && url.pathname === "/boom") {
    throw new Error("boom");
  }

  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    const parsed = parseJson(body);
    if (!parsed.ok) {
      sendError(res, { kind: "invalid_json" });
      return;
    }
    // A list means refused; a string is the title. Array.isArray tells which.
    const checked = createFrom(parsed.data);
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
    const parsed = parseJson(body);
    if (!parsed.ok) {
      sendError(res, { kind: "invalid_json" });
      return;
    }
    const checked = changesFrom(parsed.data);
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

// The error boundary: one `try` around every route, so an exception anywhere —
// in a route that exists today or one added next year — is a clean 500 instead
// of a dead process. The `await` is what keeps the `try` open until `route`'s
// promise settles; without it the rejection would escape. The details go to the
// log, never to the client. And if the route had already started answering, the
// status cannot be replaced — only the response ended.
async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  try {
    await route(req, res);
  } catch (err: unknown) {
    console.error(err);
    if (res.headersSent) {
      res.end();
      return;
    }
    sendError(res, { kind: "server_error" });
  }
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Give every 500 an incident number — a counter — sent to the client as `{\"error\":\"server_error\",\"incident\":7}` and printed in the log next to the stack trace. The client can quote it to you, and it gives nothing away. What would you use instead of a counter in production?",
        "Add `process.on(\"uncaughtException\", …)` and read the Node documentation's warning about it. Why is \"log it and exit\" the only safe thing to do there — and what does that imply about running a server under something that restarts it?",
        "Make `readBody` reject on the request's `\"error\"` event, and on a body over 1 MB. Which of those is `invalid_json`, which is a new 413, and which is the boundary's business?",
        "Replace `/boom` with a real bug: have `updateTodo` throw if `indexOf` returns -1 — a case that \"cannot happen\". Is a throw the right tool for an invariant? What would you want the log to say?",
    ],
    glossary=[
        _pgloss("throw", "Stop the current function and every caller until something catches the thrown value. Nothing after the `throw` runs."),
        _pgloss("try/catch", "Run a block; if anything in it throws, run the `catch` block instead, with the thrown value."),
        _pgloss("instanceof", "`err instanceof SyntaxError` — whether an object was made by that constructor or one built on it. Narrows a caught `unknown`."),
        _pgloss("SyntaxError", "What `JSON.parse` throws on text that is not JSON. A kind of `Error`."),
        _pgloss("error boundary", "One `try`/`catch` around everything a request runs, turning any unexpected exception into a 500."),
        _pgloss("unhandled rejection", "A promise that rejects with nothing to catch it. Node stops the process."),
        _pgloss("information leakage", "Sending internal details — messages, paths, stack traces — to a client. A 500 body must never contain them."),
        _pgloss("headersSent", "`res.headersSent` — true once the status line is out. After that a 500 cannot replace it; only `res.end()` is left."),
    ],
    cheatsheet="""
```ts
// expected failure: catch where it happens, return a value
type Parsed = | { ok: true; data: unknown } | { ok: false };

function parseJson(text: string): Parsed {
  try {
    return { ok: true, data: JSON.parse(text) };
  } catch {
    return { ok: false };
  }
}

const parsed = parseJson(body);
if (!parsed.ok) {
  sendError(res, { kind: "invalid_json" });   // 400
  return;
}
const checked = createFrom(parsed.data);

// unexpected failure: one boundary around every route
async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  try {
    await route(req, res);                      // the await is load-bearing
  } catch (err: unknown) {
    console.error(err);                         // details → the log
    if (res.headersSent) {                      // too late for a status
      res.end();
      return;
    }
    sendError(res, { kind: "server_error" });   // two words → the client
  }
}

// what was caught?
if (err instanceof SyntaxError) { … }           // specific first
if (err instanceof Error) { err.message }       // then general
```

| Request | Before | Now |
|---|---|---|
| `POST /todos not json` | 500 — the replayer | `400 {"error":"invalid_json"}` |
| `PATCH /todos/1 {` | 500 — the replayer | `400 {"error":"invalid_json"}` |
| `PATCH /todos/9 not json` | 404 | 404 — lookup first |
| a route throws | 500 — the replayer | 500 — **your** boundary |
| a route throws, no boundary | 500 in the judge, a crash on your machine | a crash in both |
""",
    self_check=[
        "Can you say where control goes when a function three calls deep throws?",
        "Can you explain why `instanceof SyntaxError` must be tested before `instanceof Error`?",
        "Can you say which failures are caught where they happen and which at the boundary — and why a wide `catch` around a route is wrong for the first kind?",
        "Can you explain what happens to a rejection when the boundary calls `route` without `await`?",
        "Can you say what a 500 body contains, where the details go, and why?",
        "Can you say what the replayer did for you from module 4 to 15, and what your own `server.ts` did instead?",
    ],
    review=[
        _pq("`not json` was a 500 for seven modules. Why could no module before this one fix it?",
            ["`JSON.parse` throws before there is a value to check, and catching a throw needs `try`/`catch`",
             "Nobody noticed",
             "Because 400 was not introduced until now",
             "Because validation had to come first"],
            0,
            "Checking a value needs a value. Recovering from a throw needs a "
            "`catch` — this module's."),
        _pq("Which failures belong at the boundary?",
            ["Unexpected ones — bugs — that no route knew how to answer",
             "All of them, so routes stay short",
             "Only `not json`",
             "Validation failures"],
            0,
            "Expected failures have specific answers and are caught where they "
            "happen. The boundary is for everything nobody planned."),
        _pq("Why does the boundary need `await route(req, res)` rather than `route(req, res)`?",
            ["Without `await` the `try` finishes before the promise rejects, so the `catch` never sees it",
             "`route` returns nothing without `await`",
             "For speed",
             "It does not; both work"],
            0,
            "An async function's errors arrive later, as a rejection. `await` "
            "keeps the `try` open until then."),
        _pq("What should `500`'s body say?",
            ["`{\"error\":\"server_error\"}` and nothing more — details go to the log",
             "The error message, to help the client",
             "The stack trace, in development",
             "Nothing — an empty body"],
            0,
            "Same shape as every other error, and no information a stranger could "
            "use."),
        _pq("A route sent `200` and then threw. What does the boundary do?",
            ["Ends the response — `headersSent` is true, so a 500 can no longer be sent",
             "Sends a 500",
             "Sends the error message",
             "Retries the route"],
            0,
            "Writing a second status would throw inside the `catch` — the one "
            "place nothing catches it."),
        _pq("`catch (err: unknown)`. Why `unknown` and not `Error`?",
            ["JavaScript can throw any value at all — a string, a number, `null` — so the compiler cannot promise an `Error`",
             "`Error` is not a type",
             "For speed",
             "It could be `Error`; `unknown` is style"],
            0,
            "A caught value is outside input, like a parsed body. Narrow it with "
            "`instanceof` before trusting it."),
    ],
    milestone="Phase 4 is done: bad input gets a specific 400 naming the problem — "
              "never a 500 — and a bug in your own code is a logged, plain 500 "
              "rather than a dead server. The safety net you borrowed from the "
              "replayer since module 4 is yours now.",
))
