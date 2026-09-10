# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 6 — Reading the request.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# INTRODUCES: `req.method`, `req.url`, `??`, `new URL(input, base)` and
# `.pathname`. This is the module that makes module 7 a fifteen-line `if` ladder
# instead of a rewrite.
#
# WHY `??` LANDS HERE and not earlier: this is the first place the COMPILER
# forces it. `new URL(req.url, base)` is a type error, because `req.url` is
# `string | undefined` and the constructor takes a `string`. Teaching a nullish
# fallback at the point where the alternative does not compile beats teaching it
# as a piece of vocabulary six modules earlier.
#
# THE METHOD/URL SPLIT, which is the module's real structure:
#   * `req.method` is `string | undefined` and you only ever COMPARE it —
#     `req.method === "GET"` is legal on the union with no narrowing at all, and
#     it is exactly the condition module 7 writes. Step 1.
#   * `req.url` is `string | undefined` and you have to USE the value, so it
#     needs the fallback. Step 2.
# That split is why `??` is introduced in step 2 rather than step 1, and it is
# worth preserving if this module is ever re-cut.
#
# WHY A `URL` OBJECT AND NOT A STRING COMPARE: `/todos?done=true` !== `/todos`.
# Finding that out in module 17, when query strings arrive, would mean rewriting
# the router that module 7 is about to build. The `fix` exercise in step 3 is
# that exact bug, eleven modules early and costing nothing.
#
# STILL NO ROUTING. The server can now tell requests apart and says so in the
# response body; branching on what it sees is module 7. A module that half-routes
# is a mess you debug twice.
# ---------------------------------------------------------------------------

_M6_WHY = (
    "Your server answers `404 not_found` to everything, and it is not being "
    "modest — it genuinely cannot tell `GET /todos` from `DELETE /nonsense`, "
    "because nothing in your handler has ever looked at `req`. Routing is one "
    "`if` away, but the `if` needs something to test, and getting that "
    "something right is fiddlier than it looks: the method can be missing, and "
    "the thing Node calls `req.url` is not a URL."
)

_M6_BRIEF = """
### The whole module in one line

Open the envelope: find out which verb was used and which path was asked for.

### What is actually in `req`

Two things matter this module, and both of them are `string | undefined`:

```ts
req.method     // "GET" | "POST" | … | undefined
req.url        // "/todos?done=true" | undefined
```

That union is not TypeScript being pedantic. A malformed request really can
arrive without either, and module 3 already taught you the shape of the answer:
handle the `undefined` rather than assert it away.

But the two are handled *differently*, and the difference is the spine of this
module:

| | What you do with it | Does it need a fallback? |
|---|---|---|
| `req.method` | compare it — `req.method === "GET"` | **no** |
| `req.url` | use the value — parse it, read the path | **yes** |

Comparing a `string | undefined` to `"GET"` is perfectly legal: if it is
`undefined` the comparison is simply `false`, which is the right answer. Passing
a `string | undefined` to something that wants a `string` is not legal, and that
is where `??` comes in.

### `req.url` is not a URL

This is the trap the module exists for.

```
the client asks for:   http://localhost:3000/todos?done=true
req.url is:            /todos?done=true
```

No scheme, no host, no port — a path and a query string, and nothing else. Node
calls the property `url`, and it is a *request target*. So this:

```ts
if (req.url === "/todos") { … }
```

works perfectly, right up until someone asks for `/todos?done=true`, at which
point it silently stops matching. Your router 404s a path it handles, and
nothing anywhere logs a reason.

### So parse it into something that knows its own parts

```ts
const url = new URL(req.url ?? "/", "http://localhost");
url.pathname     // "/todos"        ← what you route on
url.search       // "?done=true"    ← module 17's problem
```

`new URL` needs an absolute URL, and `/todos?done=true` is relative, so you give
it a base to be relative *to*. The base is a formality — you never read the host
back out — but without it the parse throws.

And now `url.pathname` is `/todos` whether or not there was a query string on
the end, which is what module 7 is going to compare against.

### The end of this module

Your server still answers everything the same way. But the answer now contains
what it was asked:

```
$ curl -s localhost:3000/todos?done=true
{"method":"GET","path":"/todos"}
```

Which is one `if` short of a router. That `if` is module 7.
"""

_M6_SYNTAX = [
    _syn(
        "req.method",
        "The verb the client used — `\"GET\"`, `\"POST\"`, `\"DELETE\"`. Typed "
        "`string | undefined`, because a malformed request can arrive without one.",
        """
if (req.method === "GET") {
  // …
}
""",
        "You do NOT have to narrow it to compare it. `undefined === \"GET\"` is "
        "`false`, which is the answer you wanted anyway. Reaching for `!` here is "
        "a habit that will cost you in module 10, where the union is real.",
    ),
    _syn(
        "req.url",
        "The request target: the path plus the query string, and nothing else. "
        "Not a URL, despite the name — no scheme, no host, no port.",
        """
// client asks for http://localhost:3000/todos?done=true
req.url;      // "/todos?done=true"
""",
        "`req.url === \"/todos\"` is `false` the moment anyone adds a query "
        "string. That is a route that silently stops matching, with nothing in "
        "any log to say why.",
    ),
    _syn(
        'req.url ?? "/"',
        "Nullish coalescing: the value on the left unless it is `null` or "
        "`undefined`, in which case the one on the right. Turns a "
        "`string | undefined` into a `string`.",
        """
const target: string = req.url ?? "/";
""",
        "`??` only falls back on `null` and `undefined`. `||` also falls back on "
        "`\"\"`, `0` and `false` — which is a bug waiting for module 17, where "
        "`?done=` is an empty string that means something.",
    ),
    _syn(
        'new URL(req.url ?? "/", "http://localhost")',
        "Parse a request target into an object that knows its own parts. The "
        "second argument is the base the first is relative to.",
        """
const url = new URL(req.url ?? "/", "http://localhost");
""",
        "The base is required, not optional — `new URL(\"/todos\")` throws, "
        "because that is not an absolute URL. The host you pass is never read "
        "back out; it exists to make the parse legal.",
    ),
    _syn(
        "url.pathname",
        "The path, with any query string removed. This is the thing you route on.",
        """
const url = new URL("/todos?done=true", "http://localhost");
url.pathname;   // "/todos"
url.search;     // "?done=true"
""",
        "`pathname` keeps the leading slash and never includes the `?`. It is "
        "also case-sensitive and does not collapse a trailing slash — `/todos/` "
        "is not `/todos`.",
    ),
    _syn(
        "function send(res: ServerResponse, status: number, data: object): void { … }",
        "Module 5's response helper. Every answer in this module still goes "
        "through it — only what is inside `data` changes.",
        "",
        "",
        recap=True,
    ),
]

_M6_S1 = _pstep(
    "method", "Which verb",
    "`req.method` — and why you can compare it without narrowing it.",
    """
The first thing your handler has ever read off the request:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 200, { isGet: req.method === "GET" });
}
```

`req.method` is the verb, in upper case, as a string: `"GET"`, `"POST"`,
`"PATCH"`, `"DELETE"`. It is not normalised for you in the sense of being
predictable — it is normalised in the sense that HTTP method names *are* upper
case, so `"get"` is not something you have to defend against.

### Why the type is `string | undefined`

Hover it and you get `string | undefined`, which surprises people. Node types it
that way because a request that never got a valid request line still produces an
`IncomingMessage` — the property is absent rather than the object being missing.

It is rare. It is not impossible. And module 3 already told you what this
project does about a union like that: handle it, do not assert it away.

### The good news: comparing needs no narrowing at all

```ts
req.method === "GET"
```

That compiles as it stands. `===` between `string | undefined` and `"GET"` is
fine, because comparison is defined for both halves of the union: if the method
is `undefined`, the answer is `false` — which is what you wanted. A request with
no method is not a GET.

So the condition module 7 will write is already legal today:

```ts
if (req.method === "GET" && url.pathname === "/todos") { … }
```

No `!`, no `if (req.method !== undefined)` wrapper, no cast. That is worth
noticing, because the next property does not get off so lightly.

### When you have to do more

The moment you want the *value* rather than the answer to a comparison —
putting it in a response, logging it, using it as an object key — the union is
back and you have to say what happens when it is missing. That is step 2's
problem, and `req.url` has it much worse.
""",
    """
```bash
$ curl -s localhost:3000/todos
{"isGet":true}

$ curl -s -X DELETE localhost:3000/todos
{"isGet":false}
```

Your server has, for the first time, given two different answers to two
different requests. Nothing routes yet — the code path is identical either way —
but the response is no longer independent of what was asked.
""",
    pitfalls=[
        "Writing `req.method!.toUpperCase()` to get rid of the union. Methods already arrive upper case, and the `!` is a promise to the compiler you cannot keep. If you want a value out of it, use `??`, which step 2 teaches.",
        "Comparing lower case: `req.method === \"get\"` is always false. HTTP method names are upper case on the wire.",
        "Wrapping the comparison in `if (req.method !== undefined)`. Unnecessary — `undefined === \"GET\"` is already `false`, and the extra nesting is one more level to read in module 7's router.",
        "Assuming a browser only sends GET and POST. `fetch` sends whatever you ask it to, and so does curl's `-X`. Your router will see PATCH and DELETE from module 11.",
    ],
    warmup=[
        _pq("`req.method` is typed `string | undefined`. Why does "
            "`req.method === \"GET\"` compile without narrowing?",
            ["Comparison is defined for both halves of the union — an absent method is simply not a GET",
             "TypeScript narrows the union automatically inside an `if`",
             "`===` ignores `undefined` operands",
             "It does not compile; the example is wrong"],
            0,
            "You are not using the value, you are asking a question about it, and "
            "the question has a sensible answer either way. Needing `!` or a guard "
            "is a sign you are about to use the value rather than compare it."),
    ],
    exercises=[
        _pex("todo-m6-method-1", "Was that a GET?",
             "Answer every request with `200` and a body saying whether the request "
             "used the `GET` verb. Compare `req.method` — you do not need to narrow "
             "it first.",
             _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 200, { isGet: req.method === "GET" });
}
"""),
             'req.method === "GET"',
             [("GET /todos\nDELETE /todos/1\nPOST /todos {\"title\":\"Buy milk\"}",
               '200 {"isGet":true}\n200 {"isGet":false}\n200 {"isGet":false}')],
             ["The property is on `req`, and the verb arrives in upper case.",
              "A comparison, not a narrowing — `===` works on the union as it stands.",
              '`req.method === "GET"`']),
        _pfix("todo-m6-method-fix1", "Case matters",
              "This handler is supposed to report whether the request was a GET, and "
              "it reports `false` every single time — including for a GET.",
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 200, { isGet: req.method === "get" });
}
"""),
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 200, { isGet: req.method === "GET" });
}
"""),
              [("GET /todos\nPOST /todos", '200 {"isGet":true}\n200 {"isGet":false}')],
              ["The comparison itself is the right shape. Look at the string.",
               "HTTP method names travel in upper case, and `===` on strings is case-sensitive.",
               '`req.method === "GET"`'],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("A request arrives with no method at all. What does "
            "`req.method === \"GET\"` evaluate to, and is that a problem?",
            ["`false`, and no — a request without a method is not a GET, which is the right answer",
             "It throws, so the comparison needs a guard",
             "`true`, because `undefined` is falsy",
             "`undefined`, which is neither true nor false"],
            0,
            "This is why the union costs nothing here. The awkward case has the "
            "answer you would have chosen anyway, so there is nothing to write."),
    ],
)

_M6_S2 = _pstep(
    "url", "Which path — and the name that lies",
    "`req.url` is a path plus a query string, and it can be missing. `??` is how you get a `string` out of it.",
    """
```ts
req.url        // "/todos?done=true"
```

### It is not a URL

The client asked for `http://localhost:3000/todos?done=true`. What reaches your
handler is:

```
/todos?done=true
```

The scheme, host and port were used to *get* to your server and are not repeated
in the request line. Node calls the property `url` anyway. The correct name for
this is a **request target**, and remembering that is what stops you writing
`new URL(req.url)` and wondering why it throws.

### It is also `string | undefined`

Same reason as `req.method`: a malformed request line leaves it absent. And this
time you cannot shrug it off with a comparison, because you are going to *use*
the value — parse it, read the path out of it, route on it.

### `??` — the fallback

```ts
const target: string = req.url ?? "/";
```

Read it as: **the left-hand value, unless it is `null` or `undefined`, in which
case the right-hand one.** The result is a plain `string`, and that is what the
next step's `new URL` wants.

Choosing `"/"` as the fallback is deliberate: it is a real path, it will not
match any route you write, and it therefore falls through to the 404 you already
have. A request so broken it had no target gets "there is nothing at this
address", which is true.

### `??` is not `||`

They look interchangeable. They are not:

```ts
const a = req.url ?? "/";       // falls back only on null / undefined
const b = req.url || "/";       // ALSO falls back on ""
```

For `req.url` the difference is invisible, because an empty target does not
happen. It stops being invisible in module 17, where `?done=` gives you the
empty string and the empty string *means something* — and `||` would quietly
replace it with a default. Learn the one that only does what it says.

### Where it does not help

`??` gives you a `string`. It does not give you a *path*: `"/todos?done=true"`
is still one flat string with a `?` in the middle of it, and comparing it to
`"/todos"` is still `false`. That is step 3.
""",
    """
```bash
$ curl -s localhost:3000/todos
{"target":"/todos"}

$ curl -s "localhost:3000/todos?done=true"
{"target":"/todos?done=true"}
```

Note the second one. The query string is in there, glued to the path, in the
same string — which is exactly the problem step 3 solves. Quote the URL in your
shell, or `?done=true` gets eaten before curl ever sees it.
""",
    pitfalls=[
        "`new URL(req.url)` — a type error, because `req.url` may be undefined, and a runtime throw even once you fix that, because a request target is relative. Two separate problems in one short line.",
        "Using `||` instead of `??` out of habit. Identical behaviour here, different behaviour on `\"\"`, `0` and `false` — and module 17 has a query parameter where the empty string is a real value.",
        "Falling back to `\"\"` rather than `\"/\"`. An empty string is not a path, and it will parse into something surprising rather than falling through to your 404.",
        "Forgetting the quotes in the shell: `curl localhost:3000/todos?done=true` lets the shell interpret the `?`. Quote the whole URL.",
    ],
    warmup=[
        _pq("A client requests `http://localhost:3000/todos?done=true`. What is "
            "`req.url` inside your handler?",
            ["`\"/todos?done=true\"` — the path and query only",
             "`\"http://localhost:3000/todos?done=true\"` — the whole URL",
             "`\"/todos\"` — the query is parsed out for you",
             "A `URL` object with a `pathname` property"],
            0,
            "The scheme, host and port got the request to your server and are not "
            "repeated in the request line. What you get is the target: path plus "
            "query, as one string."),
    ],
    exercises=[
        _pex("todo-m6-url-1", "What was asked for",
             "Answer with the raw request target under the key `target`. `req.url` "
             "can be absent, and the response has to say something either way — fall "
             "back to `\"/\"`.",
             _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 200, { target: req.url ?? "/" });
}
"""),
             'req.url ?? "/"',
             [("GET /todos\nGET /todos?done=true\nDELETE /todos/1",
               '200 {"target":"/todos"}\n200 {"target":"/todos?done=true"}\n200 {"target":"/todos/1"}')],
             ["The property is on `req`, and it is `string | undefined`.",
              "Two question marks give you the value unless it is null or undefined.",
              '`req.url ?? "/"`']),
        _pfix("todo-m6-url-fix1", "The right union, the wrong property",
              "This answers `{\"target\":\"GET\"}`. The fallback is correct, the type "
              "checks out, and it is reading the wrong thing off the request.\n\n"
              "Both properties are `string | undefined`, so the compiler cannot tell "
              "these two apart. Only you can.",
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 200, { target: req.method ?? "/" });
}
"""),
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 200, { target: req.url ?? "/" });
}
"""),
              [("GET /todos\nGET /todos?done=true\nDELETE /todos/1",
                '200 {"target":"/todos"}\n200 {"target":"/todos?done=true"}'
                '\n200 {"target":"/todos/1"}')],
              ["The response is reporting the verb where it should report the target.",
               "`req.method` and `req.url` have the same type, so swapping them type-checks.",
               "`req.url ?? \"/\"`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why is `\"/\"` a better fallback for a missing `req.url` than `\"\"`?",
            ["`\"/\"` is a real path that matches no route, so the request falls through to the 404 you already have",
             "`\"\"` is not a valid string in TypeScript",
             "`\"/\"` is the only value `new URL` accepts",
             "There is no difference; both are arbitrary"],
            0,
            "The fallback decides what a broken request gets. `\"/\"` sends it "
            "down the path you have already built and tested — the fall-through — "
            "rather than into a parse of something that is not a path at all."),
        _pq("Where does the difference between `??` and `||` first bite in this "
            "project?",
            ["Module 17 — `?done=` gives the empty string, which `||` would replace with a default",
             "Module 8 — an empty request body",
             "It never bites; they are interchangeable",
             "Module 10 — an id of `0`"],
            0,
            "An empty query value is a value: the client sent the parameter and "
            "left it blank. `||` cannot tell that from \"absent\", and the bug is a "
            "filter that quietly ignores what you asked for."),
    ],
)

_M6_S3 = _pstep(
    "parse", "Turn it into something that knows its own parts",
    "`new URL(target, base)` and `.pathname` — the string compare that would have broken in module 17.",
    """
You have a `string`. You need a *path*, and `"/todos?done=true"` is not one:

```ts
"/todos?done=true" === "/todos"      // false
```

Everything downstream routes on the path. So parse the target properly:

```ts
const url = new URL(req.url ?? "/", "http://localhost");
const path = url.pathname;           // "/todos"
```

### Why there are two arguments

`new URL` parses **absolute** URLs. `/todos?done=true` is relative — it has no
scheme and no host — so on its own it throws:

```ts
new URL("/todos");                          // TypeError: Invalid URL
new URL("/todos", "http://localhost");      // ✓
```

The second argument is what the first is relative *to*. And the host you pass is
a formality: you never read it back out, nothing routes on it, and
`"http://localhost"` versus `"http://example.com"` changes nothing about
`pathname`. It exists to make the parse legal.

(A server that genuinely needs its own address builds the base from the `Host`
header. This one never does, which is why a constant is honest here and a
`Host`-derived base would be ceremony.)

### What you get back

```ts
const url = new URL("/todos?done=true", "http://localhost");

url.pathname       // "/todos"        ← route on this
url.search         // "?done=true"    ← module 17
url.searchParams   // a parsed query  ← module 17
url.href           // "http://localhost/todos?done=true"
```

`pathname` keeps its leading slash, never contains a `?`, and is not tidied up
for you: it is case-sensitive, and `/todos/` is a different path from `/todos`.
Both of those are choices real routers make differently — yours is making the
simple one.

### The bug you just avoided

Here is what module 7 would look like if you routed on `req.url` directly:

```ts
if (req.method === "GET" && req.url === "/todos") { … }
```

Correct on `GET /todos`. Silently wrong on `GET /todos?done=true`, which falls
through to the 404 — for a route you handle, with nothing in any log explaining
why. And you would not find out until module 17, at which point every route in
the file needs changing.

Two lines now instead. This is most of what "design" means in practice: the
cheap version and the correct version cost the same today, and only one of them
is still true in eleven modules.
""",
    """
```bash
$ curl -s localhost:3000/todos
{"path":"/todos"}

$ curl -s "localhost:3000/todos?done=true&limit=2"
{"path":"/todos"}
```

The same path, twice, whatever is hanging off the end of it. That equality is
the thing module 7 routes on.
""",
    pitfalls=[
        "`new URL(target)` with one argument. It throws `TypeError: Invalid URL` at runtime for any relative target — which the replayer turns into a 500, so the message you see first is about the status, not the URL.",
        "Building the URL outside the handler, once. Each request has its own target; a URL parsed at startup is the same URL forever.",
        "Routing on `url.href` or on the raw `req.url`. Both carry the query string, and both stop matching the moment anyone adds one.",
        "Expecting `/todos/` and `/todos` to be the same path. `pathname` does not normalise the trailing slash, and neither will your router unless you write that.",
        "Expecting case-insensitive matching. `/Todos` is not `/todos`, and the client will not be told why.",
    ],
    warmup=[
        _pq("`new URL(\"/todos?done=true\", \"http://localhost\").pathname` is:",
            ["`\"/todos\"`",
             "`\"/todos?done=true\"`",
             "`\"todos\"` — the leading slash is stripped",
             "`\"http://localhost/todos\"`"],
            0,
            "`pathname` is the path and only the path: leading slash kept, query "
            "string removed. That is the whole reason to parse rather than compare "
            "strings."),
    ],
    exercises=[
        _pex("todo-m6-parse-1", "Parse the target",
             "Build a `URL` from the request target so the query string can be "
             "separated from the path. It needs a base to be relative to — use "
             "`\"http://localhost\"`.",
             _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 200, { path: url.pathname });
}
"""),
             'new URL(req.url ?? "/", "http://localhost")',
             [("GET /todos\nGET /todos?done=true", '200 {"path":"/todos"}\n200 {"path":"/todos"}')],
             ["Two arguments: the target, and the base it is relative to.",
              "The target may be missing, so it still needs its fallback.",
              '`new URL(req.url ?? "/", "http://localhost")`']),
        _pex("todo-m6-parse-2", "Just the path",
             "The URL is parsed. Report the path — without the query string, whatever "
             "the client hung off the end of it.",
             _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 200, { path: url.pathname });
}
"""),
             "url.pathname",
             [("GET /\nGET /todos?done=true&limit=2\nDELETE /todos/1",
               '200 {"path":"/"}\n200 {"path":"/todos"}\n200 {"path":"/todos/1"}')],
             ["The property that holds the path and nothing else.",
              "Not `href`, not `search` — the one that keeps the leading slash and drops the `?`.",
              "`url.pathname`"]),
        _pfix("todo-m6-parse-fix1", "The route that stops matching",
              "This reports the path by handing back the raw request target. It looks "
              "right on `/todos` and is wrong the moment a query string arrives — the "
              "exact bug that would break every route in module 7. Parse it properly.",
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 200, { path: req.url ?? "/" });
}
"""),
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 200, { path: url.pathname });
}
"""),
              [("GET /todos\nGET /todos?done=true", '200 {"path":"/todos"}\n200 {"path":"/todos"}')],
              ["The first request passes and the second does not. Compare the two.",
               "The raw target carries the query string; you want the path on its own.",
               "Two lines: build a `new URL(…, \"http://localhost\")`, then send its `pathname`."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does `new URL(req.url ?? \"/\")` throw at runtime?",
            ["A request target is relative, and `new URL` parses absolute URLs unless you give it a base",
             "`req.url` is `string | undefined`, and the `??` does not remove the union",
             "`new URL` is not available without importing it",
             "It does not throw; the base argument is optional"],
            0,
            "The `??` fixes the type; the base fixes the parse. They are two "
            "separate problems, and the second one only shows up when you run it — "
            "as a 500 from the replayer's boundary."),
        _pq("Which host should you pass as the base?",
            ["Any valid one — it is never read back out, and it does not affect `pathname`",
             "The real host from the `Host` header, or routing breaks",
             "`\"http://127.0.0.1:3000\"` exactly, to match the listening address",
             "None — pass an empty string"],
            0,
            "You only ever read `pathname`, `search` and `searchParams`, none of "
            "which depend on the host. The base exists to make a relative target "
            "parseable. A server that builds absolute links for clients would care; "
            "this one does not."),
    ],
)

_M6_S4 = _pstep(
    "echo", "Both at once — the request line",
    "Method and path in one response. One `if` short of a router.",
    """
Put the two halves together:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 200, { method: req.method ?? "UNKNOWN", path: url.pathname });
}
```

Three lines, and your server can describe what it was asked for:

```
$ curl -s -X DELETE localhost:3000/todos/1
{"method":"DELETE","path":"/todos/1"}
```

### `req.method ?? "UNKNOWN"` — why the fallback is back

Step 1 said comparing `req.method` needs no narrowing, and that is still true.
This is not a comparison. You are putting the value in a response, so the union
matters again:

```ts
send(res, 200, { method: req.method });          // compiles!
```

That compiles, and on a request with no method `JSON.stringify` **drops the key
entirely** — the client gets `{"path":"/todos"}` and no `method` at all. A
missing key is a worse answer than a placeholder, because the client's own code
then reads `undefined` from a field the contract said would be there.

`?? "UNKNOWN"` says the thing you actually know: the request came in, and it did
not say what it was.

### What you have, and what you do not

You have everything a router needs. `req.method === "GET"` and
`url.pathname === "/todos"` are both true for exactly one kind of request, and
you can evaluate both today.

What you do not have is a single `if`. That is deliberate. Module 7 is short —
it is one branch and a fall-through — precisely because this module did the
fiddly part: the union on the method, the union on the target, the base URL, and
the query string that would have broken the string compare.

### One more time on the shape

```
module 4:  answer something                 → hello, to everybody
module 5:  answer deliberately              → 404 not_found, to everybody
module 6:  know what was asked              → still to everybody
module 7:  answer differently               → routing
```

Each of those is one sitting, and none of them left the server broken at the end
of it. That is what building in slices looks like.
""",
    """
```bash
$ curl -s localhost:3000/todos
{"method":"GET","path":"/todos"}

$ curl -s -X POST "localhost:3000/todos?draft=1"
{"method":"POST","path":"/todos"}

$ curl -s -X DELETE localhost:3000/todos/1
{"method":"DELETE","path":"/todos/1"}
```

Three requests, three different answers, and the keys come out in the order the
object literal declares them — `method` then `path`.
""",
    pitfalls=[
        "`{ method: req.method }` with no fallback. It compiles, and on a method-less request `JSON.stringify` silently omits the key rather than writing `null`. The client reads `undefined` from a field your contract promised.",
        "Building the object in the other key order. Valid JSON, failing test — `JSON.stringify` follows the literal, as module 5 said.",
        "Hoisting the `const url = …` line out of the handler to \"avoid rebuilding it\". There is no `req` at module scope, so the target has to be hard-coded, and every request then reports the same path. Per-request data is built per request.",
        "Parsing the URL before checking the method, or after — it makes no difference here, and it will make none in module 7 either. Do not spend time on it.",
        "Wiring the store in now because the parts are all there. Module 7 is next and it is short; a module that half-routes is a mess you debug twice.",
    ],
    exercises=[
        _pch("todo-m6-echo-1", "Describe the request", "Easy",
             "Write the handler body. Parse the request target into a `URL` with "
             "`\"http://localhost\"` as its base, then answer `200` with `method` and "
             "`path` — in that key order.\n\n"
             "A request with no method should report `\"UNKNOWN\"` rather than "
             "leaving the key out.",
             _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 200, { method: req.method ?? "UNKNOWN", path: url.pathname });
}
"""),
             """  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 200, { method: req.method ?? "UNKNOWN", path: url.pathname });""",
             [("GET /todos\nPOST /todos?draft=1 {\"title\":\"Buy milk\"}\nDELETE /todos/1",
               '200 {"method":"GET","path":"/todos"}\n200 {"method":"POST","path":"/todos"}'
               '\n200 {"method":"DELETE","path":"/todos/1"}')],
             ["Two lines: parse, then send.",
              "The target needs its `?? \"/\"` fallback before it can be parsed, and the base is the second argument.",
              "You are using the method's value rather than comparing it, so it needs a fallback too.",
              '`const url = new URL(req.url ?? "/", "http://localhost");` then '
              '`send(res, 200, { method: req.method ?? "UNKNOWN", path: url.pathname });`']),
        _pfix("todo-m6-echo-fix1", "Parsed once, for every request",
              "The method changes from request to request. The path never does — it "
              "is `/` no matter what was asked for.\n\n"
              "Nothing in the handler is wrong. Look above it.",
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

const url = new URL("/", "http://localhost");

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 200, { method: req.method ?? "UNKNOWN", path: url.pathname });
}
"""),
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 200, { method: req.method ?? "UNKNOWN", path: url.pathname });
}
"""),
              [("GET /todos\nPOST /todos?draft=1\nDELETE /todos/1",
                '200 {"method":"GET","path":"/todos"}\n200 {"method":"POST","path":"/todos"}'
                '\n200 {"method":"DELETE","path":"/todos/1"}')],
              ["The URL is built once, when the program starts — before any request exists.",
               "There is no `req` at module scope, which is why the target had to be hard-coded.",
               "Move the `const url = …` line inside the handler and build it from `req.url ?? \"/\"`."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("`send(res, 200, { method: req.method })` on a request with no method "
            "produces which body?",
            ["`{}` — `JSON.stringify` omits keys whose value is `undefined`",
             "`{\"method\":null}`",
             "`{\"method\":undefined}`",
             "A type error, so nothing is sent"],
            0,
            "`undefined` is not representable in JSON, and `JSON.stringify` drops "
            "the key rather than inventing a `null`. The client then reads a field "
            "your contract promised and gets nothing."),
    ],
)

_M6_FINAL = _pch(
    "todo-m6-build", "Module 6 build — a server that knows what it was asked", "Easy",
    "Write the handler.\n\n"
    "Parse the request target into a `URL` — remember it is relative, so it needs "
    "`\"http://localhost\"` as a base, and it can be absent, so it needs a "
    "fallback. Then answer `200` with the verb under `method` and the path under "
    "`path`, in that order.\n\n"
    "The path must not include the query string, and a request with no method "
    "must still report something. `send` is already written.",
    _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 200, { method: req.method ?? "UNKNOWN", path: url.pathname });
}
"""),
    """function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 200, { method: req.method ?? "UNKNOWN", path: url.pathname });
}""",
    [("GET /\nGET /todos\nGET /todos?done=true&limit=2\nPOST /todos {\"title\":\"Buy milk\"}\nPATCH /todos/1 {\"done\":true}\nDELETE /todos/1",
      '200 {"method":"GET","path":"/"}\n200 {"method":"GET","path":"/todos"}'
      '\n200 {"method":"GET","path":"/todos"}\n200 {"method":"POST","path":"/todos"}'
      '\n200 {"method":"PATCH","path":"/todos/1"}\n200 {"method":"DELETE","path":"/todos/1"}')],
    ["The whole handler goes in the blank: signature and body.",
     "Two statements inside it — parse the target, then send.",
     '`new URL(req.url ?? "/", "http://localhost")` — the fallback for the union, '
     "the base for the relative target.",
     "Route the path off `url.pathname`, not off `req.url` — look at the third "
     "test line to see why.",
     '`req.method ?? "UNKNOWN"`, because you are using the value rather than '
     "comparing it, and a dropped key is worse than a placeholder."],
)

_TODO_MODULES.append(_pmod(
    key="todo-url", number=6, phase="network",
    title="Reading the request",
    what="req.method and the URL, parsed properly rather than by string match",
    goal="Tell one request apart from another.",
    why=_M6_WHY,
    est_minutes=45,
    builds_on=["todo-lookup", "todo-json"],
    concepts=["req.method", "req.url", "request target", "nullish coalescing",
              "the WHATWG URL", "pathname"],
    deliverable="A server that knows which verb and which path it was asked for, "
                "and says so in the response.",
    objectives=[
        "Read `req.method` and say why comparing it needs no narrowing but using it does",
        "Explain what `req.url` actually contains, and why the name is misleading",
        "Use `??` to turn a `string | undefined` into a `string`, and say how it differs from `||`",
        "Parse a relative request target with `new URL(target, base)` and say what the base is for",
        "Route on `url.pathname` and explain the module-17 bug a raw string compare would cause",
        "Predict what `JSON.stringify` does with a key whose value is `undefined`",
    ],
    brief=_M6_BRIEF,
    syntax=_M6_SYNTAX,
    steps=[_M6_S1, _M6_S2, _M6_S3, _M6_S4],
    final_build=_M6_FINAL,
    acceptance=[
        "`curl -s localhost:3000/todos` prints `{\"method\":\"GET\",\"path\":\"/todos\"}`.",
        "`curl -s \"localhost:3000/todos?done=true\"` prints the same thing — the query string is not in the path.",
        "`curl -s -X DELETE localhost:3000/todos/1` reports `DELETE` and `/todos/1`.",
        "Your handler contains no `!` and no cast — both unions are handled with `===` or `??`.",
        "The `URL` is built inside the handler, once per request, not at startup.",
        "You can say what the `\"http://localhost\"` base is for, and what would change if it were a different host.",
    ],
    manual_test="""
With `node server.ts` running:

```bash
curl -s localhost:3000/todos
curl -s "localhost:3000/todos?done=true&limit=2"     # quote it, or the shell eats the ?
curl -s -X POST localhost:3000/todos
curl -s -X DELETE localhost:3000/todos/1
```

Then prove the thing this module is really about:

```bash
# 1. route on the raw target instead — replace url.pathname with (req.url ?? "/")
curl -s localhost:3000/todos                 # {"path":"/todos"}         looks fine
curl -s "localhost:3000/todos?done=true"     # {"path":"/todos?done=true"}  ← the bug

# 2. drop the base argument from new URL, restart, and watch it 500
curl -s -i localhost:3000/todos
```

The first is the one to sit with. It is invisible on every request you would
think to type, and it breaks a route you handle.
""",
    reference="""// server.ts — module 6
//
// The handler reads the request for the first time. Two properties, two unions,
// and one parse — and after this module, routing is a single `if`.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  // req.url is NOT a URL. It is the request target — path plus query string,
  // relative, e.g. "/todos?done=true". Two things are wrong with using it as-is:
  //
  //   1. It is `string | undefined`, so `??` supplies a path for the malformed
  //      case. "/" is chosen because it matches no route and therefore falls
  //      through to the 404 below, which is the truthful answer for a request
  //      that never said what it wanted.
  //   2. It is relative, so `new URL` needs a base to resolve it against. The
  //      host is a formality — nothing here ever reads it back out — and a
  //      server that builds absolute links for clients would derive it from the
  //      Host header instead.
  //
  // Parsing rather than string-comparing is what makes `?done=true` (module 17)
  // a feature rather than a router rewrite: pathname is "/todos" either way.
  const url = new URL(req.url ?? "/", "http://localhost");

  // req.method is `string | undefined` too, and it gets treated differently
  // depending on what you do with it:
  //
  //   compare it  ->  `req.method === "GET"` needs nothing. An absent method is
  //                   not a GET, which is the answer you wanted. That is module
  //                   7's condition, and it is already legal today.
  //   use it      ->  the union is real again. Without the `??`, JSON.stringify
  //                   DROPS the key on a method-less request — the client reads
  //                   `undefined` from a field the contract promised. A
  //                   placeholder is a better answer than a missing key.
  send(res, 200, { method: req.method ?? "UNKNOWN", path: url.pathname });
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Print `url.search` and `url.searchParams.get(\"done\")` alongside the path for `?done=true`. That is module 17 sitting there fully parsed, eleven modules early — you are simply not routing on it yet.",
        "Add `href` to the response and see the base you passed reappear in it. That is the only place the host ever shows up.",
        "Ask for `/todos/` with a trailing slash and confirm `pathname` keeps it. Then decide whether your router should treat it as `/todos`, and note that whatever you decide is code you have to write.",
        "Send a request with a path containing a space (`curl -s \"localhost:3000/a%20b\"`) and see what `pathname` gives you. Percent-decoding is a thing `URL` does and a string compare does not.",
        "Echo `req.headers[\"user-agent\"]` too, and note the header name is lower case. Node lower-cases every incoming header name — a detail module 8 relies on.",
    ],
    glossary=[
        _pgloss("request target", "What `req.url` actually holds: path plus query string, relative. Not a URL."),
        _pgloss("req.method", "The verb, upper case, typed `string | undefined`. Safe to compare without narrowing."),
        _pgloss("??", "Nullish coalescing — the left value unless it is `null` or `undefined`. Unlike `||`, it does not fall back on `\"\"`, `0` or `false`."),
        _pgloss("base URL", "The second argument to `new URL`, giving a relative target something to resolve against. Never read back out here."),
        _pgloss("pathname", "The path with the query string removed. The thing you route on."),
        _pgloss("search", "The query string including its `?`. Module 17's raw material."),
        _pgloss("WHATWG URL", "The `URL` class shared by browsers and Node — the standard parser, rather than a hand-rolled split."),
    ],
    cheatsheet="""
```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  //                  ^ union fallback  ^ target is relative — base required

  req.method === "GET"                  // comparing: no narrowing needed
  req.method ?? "UNKNOWN"               // using the value: fallback needed

  url.pathname                          // "/todos"      ← route on this
  url.search                            // "?done=true"  ← module 17
}
```

| You have | You want | Write |
|---|---|---|
| `req.method` | is it a GET? | `req.method === "GET"` |
| `req.method` | the verb, as a string | `req.method ?? "UNKNOWN"` |
| `req.url` | a `string` | `req.url ?? "/"` |
| the target | the path alone | `new URL(target, base).pathname` |

| Symptom | Cause |
|---|---|
| `TypeError: Invalid URL` → a 500 | `new URL` with no base — the target is relative |
| a route stops matching with `?x=1` on it | routing on `req.url` instead of `url.pathname` |
| a key vanishes from the response | its value was `undefined`; `JSON.stringify` drops it |
| `isGet` always false | compared against lower-case `"get"` |

**`??` not `||`.** They agree today. They disagree in module 17, on `?done=`.
""",
    self_check=[
        "Can you say what `req.url` contains for `http://localhost:3000/todos?done=true`, and why the property name is misleading?",
        "Can you explain why comparing `req.method` needs no narrowing but putting it in a response does?",
        "Can you say what the base argument to `new URL` is for, and what breaks without it?",
        "Can you describe the bug a `req.url === \"/todos\"` router has, and name the module where it would have surfaced?",
        "Can you say what `JSON.stringify({ a: undefined })` produces, and why a missing key is worse than a placeholder?",
        "Can you give a case where `??` and `||` behave differently, and say which one this project uses?",
    ],
    review=[
        _pq("Why does this project parse `req.url` instead of comparing it to a "
            "string?",
            ["The target carries the query string, so `/todos?done=true` would stop matching a `/todos` route",
             "`req.url` is not a string, so it cannot be compared",
             "String comparison is slower than parsing",
             "`new URL` lower-cases the path, which routing needs"],
            0,
            "The string compare is correct on every request you would think to "
            "type by hand and wrong on the first one with a query string. Parsing "
            "costs one line now and saves rewriting every route in module 17."),
        _pq("`const target = req.url ?? \"/\"` — what is the type of `target`?",
            ["`string`",
             "`string | undefined`",
             "`\"/\"`",
             "`unknown`"],
            0,
            "That is the whole job of `??` here: it removes `undefined` from the "
            "union by supplying a value for that case, so what comes out is a plain "
            "`string` — which is what `new URL` requires."),
        _pq("Which of these still compiles cleanly and is still wrong?",
            ["`send(res, 200, { method: req.method })` — the key disappears when the method is absent",
             "`new URL(req.url)` — missing base",
             "`req.method === \"GET\"` — the union is not narrowed",
             "`url.pathname === \"/todos\"` — pathname could be undefined"],
            0,
            "That is the dangerous kind of bug: the type checker is satisfied, the "
            "happy path works, and the failure is a field silently missing from a "
            "response. The other three either do not compile or are fine."),
        _pq("Module 7 adds routing. What does it need from this module?",
            ["`req.method === \"GET\"` and `url.pathname === \"/todos\"` — two conditions that are already legal to write",
             "A `Router` class to register handlers on",
             "The request body, so it can tell requests apart",
             "Nothing — routing works off `req` directly"],
            0,
            "That is why module 7 is short. The awkward parts — two unions, a "
            "relative target and a query string — were all dealt with here, so "
            "routing is one branch and a fall-through."),
    ],
    milestone="Your server can tell one request from another. Everything from "
              "here is deciding what to do about it.",
))
