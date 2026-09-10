# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 5 — Status codes and JSON.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# INTRODUCES: `res.writeHead(status, headers)`, `Content-Type: application/json`,
# and the `send(res, status, data)` helper that EVERY response for the remaining
# fifteen modules goes through. Getting that signature right is the whole reason
# this module exists at the size it does.
#
# THE ONE DESIGN DECISION WORTH KNOWING: `data` is typed `object`, not `unknown`
# (gated to module 13) and not a union of the shapes we happen to send today.
# `object` is honest — every response this API sends is a JSON object or array,
# never a bare string — it type-checks, and it costs one sentence to explain.
# A union would need editing in six later modules; `unknown` would forward-
# reference the pivot of phase 4.
#
# WHAT THE JUDGE CANNOT SEE: the replayer prints `<status> <body>` and nothing
# else, so no exercise here can check a `Content-Type` header. That is stated
# plainly in step 2 rather than papered over — the header is verified by the
# acceptance checklist and `curl -i`, and saying so is cheaper than a learner
# discovering the gap and mistrusting everything else.
#
# THE ANSWER IS 404, DELIBERATELY. Nothing can read the request until module 6,
# so every request still gets the same response — but a server that handles no
# routes yet answering `404 {"error":"not_found"}` is not a placeholder, it is
# correct. It also means module 7 adds routing to a working default rather than
# building the default and the routes at once.
# ---------------------------------------------------------------------------

_M5_WHY = (
    "Your server answers every request with a 200 — and you never chose it. "
    "Node picked it, and it will keep picking it when the client asks for a "
    "todo that does not exist, sends a title that is empty, or hits a path you "
    "have never heard of. A status code the caller cannot trust is worse than "
    "no status code at all, because code on the other end branches on it. This "
    "module makes the status a decision, makes the body JSON, and puts both in "
    "one function you will call for the rest of the project."
)

_M5_BRIEF = """
### The whole module in one line

Stop letting Node choose your status code, and start saying what you are sending.

### What is wrong with module 4's answer

```
$ curl -i localhost:3000/todos/99
HTTP/1.1 200 OK
Date: …
Connection: keep-alive

hello
```

Three problems, in order of how much they will cost you:

1. **`200 OK` is a lie.** There is no todo 99. The client's code reads the
   status first — that is what it is for — and a 200 tells it "here is your
   todo", so it goes looking for a `title` in the body and finds the word
   `hello`.
2. **There is no `Content-Type` header at all.** You never said what you were
   sending, so the client has to guess. Some guess well. Guessing is not a
   contract.
3. **The body is not JSON.** Everything else in this project will be.

### Two lines fix all three

```ts
res.writeHead(404, { "Content-Type": "application/json" });
res.end(JSON.stringify({ error: "not_found" }));
```

Which produces:

```
$ curl -i localhost:3000/todos/99
HTTP/1.1 404 Not Found
Content-Type: application/json

{"error":"not_found"}
```

### And then you write it once

Those two lines are going to appear in every branch of every route: five verbs,
each with a success case and two or three failure cases. Written out each time
that is thirty copies of the same pair, and thirty places to forget the header.

So the second half of this module is one function:

```ts
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}
```

Every response from module 6 to module 20 goes through it. When module 15 wants
every error in the app to have the same shape, this is the function it changes;
when module 18 adds a header, this is where it goes. **That is the actual
deliverable of this module** — not the status code, the single place.

### Why the answer is 404 this module

Nothing has looked at the request yet — reading it is module 6 — so every
request still gets the same response. But `404 {"error":"not_found"}` is not a
placeholder standing in for a real answer. It is the *correct* answer for a
server that handles no routes, and it is what module 7 will keep as the
fall-through when the first real route lands.

A server that answers "I do not handle that" to everything is a finished,
honest module. Module 4 answered `hello` to everything, and `hello` was never
true.
"""

_M5_SYNTAX = [
    _syn(
        'res.writeHead(404, { "Content-Type": "application/json" })',
        "Set the status code and the headers, in one call, before you write any "
        "body. Status first, headers second.",
        """
res.writeHead(404, { "Content-Type": "application/json" });
res.end('{"error":"not_found"}');
""",
        "It must come BEFORE `res.end`. Once the body has started going out the "
        "status line has already gone with it, and Node throws "
        "`ERR_HTTP_HEADERS_SENT` if you try to change it.",
    ),
    _syn(
        '{ "Content-Type": "application/json" }',
        "The headers, as an object of name → value. This one tells the client "
        "how to read the bytes you are about to send.",
        """
res.writeHead(200, { "Content-Type": "application/json" });
""",
        "Leave it out and Node sends NO `Content-Type` at all — not a wrong one, "
        "none. What the client does with an untyped body is then the client's "
        "guess, and browsers and `fetch` guess differently.",
    ),
    _syn(
        "function send(res: ServerResponse, status: number, data: object): void { … }",
        "The one place every response in this project is written. Status and "
        "body in, one JSON response out.",
        """
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

send(res, 404, { error: "not_found" });
""",
        "`res` comes first because it is the thing being written to — the same "
        "order the built-in call has. Getting the parameter order settled now "
        "matters: fifteen modules call this.",
    ),
    _syn(
        "data: object",
        "\"Some object\" — good enough, because every response this API sends is "
        "a JSON object or an array, and in JavaScript an array is an object too.",
        """
send(res, 404, { error: "not_found" });   // fine
send(res, 200, todos);                    // fine — an array is an object
""",
        "It deliberately rejects `send(res, 200, \"hello\")`. A bare string is "
        "not JSON, and the type saying so is the point. Module 13 replaces this "
        "with something sharper once `unknown` is on the table.",
    ),
    _syn(
        "JSON.stringify(value)",
        "Turn a value into the JSON text that goes down the wire. Keys come out "
        "in the order you wrote them.",
        """
JSON.stringify({ error: "not_found" });   // {"error":"not_found"}
""",
        "Insertion order is not cosmetic here: the exercises compare the response "
        "text character for character, so an object built in the other order is a "
        "different answer.",
        recap=True,
    ),
    _syn(
        'res.end("hello")',
        "Still writes the body and finishes the response — `writeHead` sets what "
        "goes above it, and changes nothing about that.",
        "",
        "Exactly one `res.end` on every path, same as module 4. `send` is now the "
        "thing that owns that call.",
        recap=True,
    ),
]

_M5_S1 = _pstep(
    "status", "Say the status out loud",
    "`res.writeHead(status)` — the code stops being Node's default and starts being yours.",
    """
In module 4 your handler was:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}
```

and every response came back `200 OK`. Nobody decided that. Node writes a status
line whether or not you set one, and 200 is what it writes when you have not.

Add one line above the `res.end`:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.writeHead(404);
  res.end("not found");
}
```

### Two arguments, and the order

```ts
res.writeHead(status, headers);
```

The status is a number — `200`, `404`, `500` — and the headers are optional,
which is why this step can leave them out and step 2 can add them. There is no
overload where the number comes second, and no version that takes the reason
phrase: Node writes `Not Found` next to `404` for you, from a table.

### It has to come first

`writeHead` writes the *top* of the response — the status line and the headers.
`res.end` writes the *bottom* and closes it. Do them in that order or the top
has already gone:

```ts
res.end("not found");
res.writeHead(404);        // ERR_HTTP_HEADERS_SENT — too late
```

That one throws, which in the exercises means the replayer's boundary catches it
and you see a `500` you did not write. Module 4's step 4 warned you about
exactly this reading.

### The status is not decoration

The client branches on it. `fetch` exposes it as `reply.status` before anyone
has looked at a single byte of the body — that is what the replayer prints
first, and it is what the code calling your API will check first too. A 200 on
a failure means the caller's error handling never runs.
""",
    """
`curl -i localhost:3000` now prints `HTTP/1.1 404 Not Found` on the first line,
where it printed `200 OK` before. The body is whatever you passed to `res.end`.

Without `-i` nothing looks different at all, which is the point: the status is
the part of the response you cannot see unless you ask. Use `-i` for the rest of
this project.
""",
    pitfalls=[
        "Calling `res.writeHead` after `res.end`. The status line has already gone out, Node throws `ERR_HTTP_HEADERS_SENT`, and what you see is a 500 from the replayer's boundary rather than an error pointing at the line.",
        "Expecting the status to change what the body says. It does not — they are two independent halves of the response, and a 404 with the body `hello` is a perfectly well-formed lie.",
        "Passing the reason phrase: `res.writeHead(404, \"Not Found\")`. Node fills the phrase in from the number. That second argument is the headers, and a string there is a type error.",
        "Checking your work without `-i`. Every status code bug in this project is invisible in plain `curl` output.",
    ],
    warmup=[
        _pq("Module 4's handler never called `writeHead`, yet every response came "
            "back `200 OK`. Where did the 200 come from?",
            ["Node writes a status line whether or not you set one, and 200 is its default",
             "`res.end` returns 200 when it is given a string",
             "The replayer added it",
             "curl displays 200 when no status is present"],
            0,
            "A response is not valid without a status line, so Node writes one. "
            "The trouble is not that 200 is wrong today — it is that it will still "
            "be 200 on the day something has gone wrong."),
    ],
    exercises=[
        _pex("todo-m5-status-1", "Choose the code",
             "This server handles no routes at all, so the honest answer to every "
             "request is 404. Set the status before the body goes out.",
             _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.writeHead(404);
  res.end("not found");
}
"""),
             "  res.writeHead(404);",
             [("GET /\nPOST /todos", "404 not found\n404 not found")],
             ["One call on `res`, taking the status code as a number.",
              "It goes above the `res.end`, not below it.",
              "`  res.writeHead(404);`"]),
        _pfix("todo-m5-status-fix1", "The status disagrees with the body",
              "This handler says `not found` in the body and `200 OK` in the status "
              "line. Client code reads the status, so it believes the 200 and never "
              "looks at the body. Make the status tell the truth.",
              _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.writeHead(200);
  res.end("not found");
}
"""),
              _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.writeHead(404);
  res.end("not found");
}
"""),
              [("GET /todos/99", "404 not found")],
              ["The body is right; the number above it is not.",
               "Which code means \"there is nothing at this address\"?",
               "`res.writeHead(404);`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("What happens if you call `res.writeHead(404)` after `res.end(\"x\")`?",
            ["It throws `ERR_HTTP_HEADERS_SENT` — the status line went out with the body",
             "The status is quietly updated to 404",
             "Nothing at all; `writeHead` after `end` is ignored",
             "The client receives two responses"],
            0,
            "`writeHead` writes the top of the response and `end` writes the bottom "
            "and closes it. Once the bottom has gone, the top went with it. In an "
            "exercise this surfaces as a 500 from the replayer's boundary."),
    ],
)

_M5_S2 = _pstep(
    "content-type", "Say what you are sending",
    "The header that tells the client how to read the bytes — and the JSON body underneath it.",
    """
`writeHead` takes a second argument: the headers, as an object of name → value.

```ts
res.writeHead(404, { "Content-Type": "application/json" });
res.end(JSON.stringify({ error: "not_found" }));
```

### What the header actually does

Bytes are bytes. `{"error":"not_found"}` is twenty-one characters and nothing
about them says "this is JSON" — that claim lives in the header, and it is the
only place it can live.

Leave the header off and Node sends **no `Content-Type` at all**. Not a wrong
one; none. What happens next is up to the client: `fetch(…).json()` may refuse
outright, a browser will sniff the bytes and make its own decision, and two
browsers may decide differently. That is not a bug you can fix in your server
later — it is a contract you never wrote.

### The quotes around the name

```ts
{ "Content-Type": "application/json" }
```

The key is quoted because `Content-Type` has a hyphen in it, and an unquoted
key with a hyphen is a subtraction. Header names are case-insensitive on the
wire, but write it in the conventional `Content-Type` casing — the next person
to read your code is not case-insensitive.

### The body has to be a string

`res.end` takes a string. An object is not one:

```ts
res.end({ error: "not_found" });          // type error
res.end(JSON.stringify({ error: "not_found" }));   // ✓
```

TypeScript catches this one, which is a mercy — in plain JavaScript the first
line sends the literal text `[object Object]` and you find out from a confused
client.

### Key order is part of the answer

`JSON.stringify` emits keys in the order you wrote them:

```ts
JSON.stringify({ status: "ok", version: 1 });   // {"status":"ok","version":1}
JSON.stringify({ version: 1, status: "ok" });   // {"version":1,"status":"ok"}
```

Both are valid JSON and any parser reads them the same. But the exercises
compare the response *text*, so the second one fails a test written for the
first. Build response objects in the order the expected output shows.

### What the exercises here cannot check

The replayer prints `<status> <body>` — two things, neither of which is a
header. So **no exercise in this module can tell whether you set
`Content-Type`**, and one that "passes" with the header missing has not proved
anything about it.

That is worth knowing rather than tripping over. The header is checked in this
module's acceptance list and by `curl -i` against your own server, and those are
the only two places it can be checked. Nothing else in the track has this gap;
it is a property of what the replayer prints.
""",
    """
```bash
$ curl -i localhost:3000/todos/99
HTTP/1.1 404 Not Found
Content-Type: application/json
…

{"error":"not_found"}
```

The `Content-Type` line is there and says `application/json`, and the body
parses as JSON. Then take the header out, restart, and run it again — the line
disappears entirely rather than changing to something else. That absence is what
you are preventing.
""",
    pitfalls=[
        "Writing `{ Content-Type: \"application/json\" }` without quotes. The hyphen makes it an expression, not a key, and the error message is about `Content` being undefined rather than about headers.",
        "`res.end({ error: \"not_found\" })`. TypeScript stops it here; plain JavaScript would send the six-word string `[object Object]` and let the client work it out.",
        "Building the response object in a different key order than the expected output. Valid JSON, failing test — and the diff looks identical until you read it character by character.",
        "Assuming a passing exercise means your `Content-Type` is right. The replayer prints the status and the body and nothing else; only `curl -i` can tell you about the header.",
        "`application/json; charset=utf-8` is also correct and is what many servers send — but it is a different string, and the acceptance check in this module looks for the plain form.",
    ],
    warmup=[
        _pq("Your handler calls `res.end(JSON.stringify(todo))` but never sets a "
            "`Content-Type`. What goes out?",
            ["The JSON body, with no `Content-Type` header at all — the client has to guess",
             "The JSON body with `Content-Type: application/json`, since Node inspects the body",
             "A 500, because the header is required",
             "The JSON body with `Content-Type: text/plain`"],
            0,
            "Node does not inspect what you wrote. No header is sent, and clients "
            "differ in what they do with an untyped body — which is exactly the "
            "kind of difference you do not want to discover in production."),
    ],
    exercises=[
        _pex("todo-m5-json-1", "Declare the type",
             "The body is already JSON text, but nothing says so. Give `writeHead` "
             "both of its arguments: the status a server with no routes should "
             "answer with, and the header naming the body's type.",
             _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "not_found" }));
}
"""),
             '404, { "Content-Type": "application/json" }',
             [("GET /\nGET /todos/99", '404 {"error":"not_found"}\n404 {"error":"not_found"}')],
             ["The status is a number; the headers are an object of name to value.",
              "The header name has a hyphen in it, so the key has to be quoted.",
              '`404, { "Content-Type": "application/json" }`']),
        _pex("todo-m5-json-2", "A JSON body",
             "Answer `200` with the object `{ status: \"ok\", version: 1 }` as JSON. "
             "`res.end` takes a string, so the object has to become one.",
             _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ status: "ok", version: 1 }));
}
"""),
             'JSON.stringify({ status: "ok", version: 1 })',
             [("GET /health", '200 {"status":"ok","version":1}')],
             ["One call turns a value into JSON text.",
              "Keys come out in the order you write them — match the expected output.",
              '`JSON.stringify({ status: "ok", version: 1 })`']),
        _pfix("todo-m5-json-fix1", "Right JSON, wrong answer",
              "This response is valid JSON with the correct two fields in it, and the "
              "test still fails. Read the expected output character by character.",
              _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ version: 1, status: "ok" }));
}
"""),
              _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ status: "ok", version: 1 }));
}
"""),
              [("GET /health", '200 {"status":"ok","version":1}')],
              ["Both fields are present and both values are right.",
               "`JSON.stringify` emits keys in the order the object literal declares them.",
               "Swap the two properties so `status` comes first."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why must the key in `{ \"Content-Type\": \"application/json\" }` be quoted?",
            ["`Content-Type` contains a hyphen, and an unquoted key with a hyphen is parsed as a subtraction",
             "Header names must be quoted by the HTTP specification",
             "TypeScript requires quotes on every object key",
             "It does not — the quotes are a style choice"],
            0,
            "Unquoted object keys have to be valid identifiers. `Content-Type` is "
            "not one, so the quotes are load-bearing. `contentType` would be a "
            "legal key and the wrong header name."),
    ],
)

_M5_S3 = _pstep(
    "send", "One helper, every response",
    "Write the two lines once, in a function, and call it everywhere for the next fifteen modules.",
    """
Count the responses this project ends up sending. Five verbs; each has a success
case and two or three failures. That is roughly thirty places that all want the
same two lines:

```ts
res.writeHead(status, { "Content-Type": "application/json" });
res.end(JSON.stringify(data));
```

Thirty copies is thirty chances to forget the header, and one place to change
when module 15 decides every error should have the same shape. So write it once:

```ts
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}
```

and call it:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}
```

### Every part of that signature is a decision

**`res` first.** It is the thing being written to, and putting it first matches
the built-in calls (`res.writeHead(…)`, `res.end(…)`) you are replacing. Fifteen
modules call this function; an argument order you have to look up every time is
a small tax collected several hundred times.

**`status: number`, not a default.** You could give it `status = 200` and write
`send(res, todo)` on the happy path. Do not. Making the status impossible to
omit is the same argument as step 1: the code you did not choose is the one that
is wrong on the failure path.

**`data: object`.** Not `unknown`, which module 13 introduces for a reason and
which would need narrowing here for no benefit. Not a union of the shapes you
happen to send today, which would need editing in six later modules. `object`
says "some object", which is true of every response this API sends — a `Todo`,
an array of them, an error record — because an array is an object too.

It does reject `send(res, 200, "hello")`, and that is the point: a bare string
is not a JSON response, and the type is the thing stopping you.

**`: void`.** Same as `handler` — all of the effect is on `res`. And the same
rule follows it: **exactly one `send` on every path**, with a `return`
immediately after, once module 7 gives you more than one path.

### This is the actual deliverable

Not the status code and not the header. The single place. Everything the rest of
this project wants to do to a response — a new header, one error shape, logging
every reply — happens in these three lines or in thirty scattered ones. That
choice is being made now.
""",
    """
Your handler is one line long:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}
```

and `curl -i localhost:3000/anything` still prints `404`, `Content-Type:
application/json`, and `{"error":"not_found"}` — exactly what it printed at the
end of step 2. Nothing about the response changed; the code that produces it
moved. That is what a refactor is, and being able to tell that it worked
*because nothing changed* is the skill.
""",
    pitfalls=[
        "Forgetting `res` as the first parameter and reaching for it from the enclosing scope. It is not there — `send` is a top-level function and each request has its own `res`. Pass it in.",
        "Giving `status` a default so `send(res, data)` works. Every response then defaults to success, including the ones that are not, which is the bug module 4 left behind.",
        "Calling `send` twice on one request. It is two `res.end`s wearing a coat: the second throws. From module 7, `return` after every `send`.",
        "Typing `data` as `Todo`. It has to carry error objects and arrays too — `object` covers all three, and narrowing it to today's shape means editing this signature in module 9, 14 and 18.",
    ],
    exercises=[
        _pch("todo-m5-send-1", "Write the helper", "Easy",
             "`handler` already calls `send`. Write the function body — set the status "
             "and the JSON content type, then write the body as JSON text.\n\n"
             "Two lines, in the order the response goes out in.",
             _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}
"""),
             """  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));""",
             [("GET /\nPOST /todos {\"title\":\"Buy milk\"}",
               '404 {"error":"not_found"}\n404 {"error":"not_found"}')],
             ["Two lines: the top of the response, then the bottom.",
              "The status is the parameter, not a literal — that is the whole point of the helper.",
              "The body has to be a string, and `data` is an object.",
              '`res.writeHead(status, { "Content-Type": "application/json" });` then '
              '`res.end(JSON.stringify(data));`']),
        _pex("todo-m5-send-2", "Call it",
             "The helper is written. Answer every request with a 404 and the body "
             "`{\"error\":\"not_found\"}` by calling it.",
             _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}
"""),
             '  send(res, 404, { error: "not_found" });',
             [("GET /\nDELETE /todos/1", '404 {"error":"not_found"}\n404 {"error":"not_found"}')],
             ["Three arguments, in the order the signature declares them.",
              "The response object, then the status, then the object to send.",
              '`  send(res, 404, { error: "not_found" });`']),
        _pfix("todo-m5-send-fix1", "The helper ignores its own parameter",
              "The call site asks for a 404. The response comes back 200. The body is "
              "right, so the bug is not at the call site — read the helper.",
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}
"""),
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}
"""),
              [("GET /todos/99", '404 {"error":"not_found"}')],
              ["`send` takes a `status` parameter. Does it use it?",
               "A hard-coded number inside a function that was given one.",
               "`res.writeHead(status, …)`."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why is `data` typed `object` rather than `Todo`?",
            ["The same helper sends error records and arrays of todos too, and `object` covers all three",
             "`Todo` is not in scope inside `send`",
             "`JSON.stringify` only accepts `object`",
             "`object` is faster to type-check"],
            0,
            "`send` is the one exit from the application, so everything leaves "
            "through it: a `Todo`, a `Todo[]`, `{ error: … }`. Typing it to today's "
            "shape means editing the signature again in modules 9, 14 and 18."),
        _pq("What does typing `data` as `object` rule out?",
            ["`send(res, 200, \"hello\")` — a bare string is not a JSON response",
             "`send(res, 200, todos)` — arrays are not objects",
             "`send(res, 404, { error: \"not_found\" })` — object literals need a named type",
             "Nothing; `object` accepts every value"],
            0,
            "An array *is* an object, so a `Todo[]` passes. A string is not, and "
            "rejecting it is deliberate: every response this API sends is a JSON "
            "object or array. `null` and `undefined` are rejected too."),
    ],
)

_M5_S4 = _pstep(
    "codes", "Which code, and why 404 is this module's answer",
    "The five status codes this project uses, and the difference between \"you asked wrong\" and \"I broke\".",
    """
You will use six codes in this project and no others. Learning them as a set now
is cheaper than looking one up per module.

| Code | Means | First used |
|---|---|---|
| `200` | Here is what you asked for | module 7 — `GET /todos` |
| `201` | I created it, and here it is | module 9 — `POST /todos` |
| `204` | Done. There is deliberately no body | module 12 — `DELETE` |
| `400` | *Your* request was wrong | module 14 — validation |
| `404` | There is nothing at this address | module 7, and today |
| `500` | *I* broke | module 16 — the error boundary |

### The line that matters most

**`400` and `404` are the client's fault. `500` is yours.**

That is not a philosophical point — it decides who gets woken up. A client
reading a 500 retries, escalates, files a bug against your service. A client
reading a 400 fixes its own request and moves on. Answering 500 when someone
sent you a malformed title means your on-call rota pays for their typo; that is
the mistake this project spends all of phase 4 preventing.

The trap runs the other way too. A handler that crashes and gets caught somewhere
that answers 404 hides a real fault behind "not found", and you will never see
it in a dashboard.

### 404 versus 400

Both mean "I am not doing that", and the difference is *where* the problem is:

- **404 — the address.** `/todso`, `/todos/999`. There is nothing there. You
  cannot fix the request except by asking for something else.
- **400 — the payload.** `POST /todos` with `{"title":""}`. The address is fine,
  the door opened, and what you handed through it was not acceptable.

### So: 404 to everything, today

Your server handles no routes yet. Not "handles them badly" — handles none. The
truthful answer to `GET /todos` from a server that has never heard of `/todos`
is *there is nothing at this address*, which is a 404 with `{"error":
"not_found"}`.

That is not a placeholder. Module 7 adds `GET /todos` **above** this line and
leaves the line where it is, as the fall-through every unmatched request lands
on. You are writing the default first and the special cases after — which is
the opposite of how most people build a router, and much harder to get wrong.
""",
    """
Every request, whatever the method and whatever the path, comes back:

```
HTTP/1.1 404 Not Found
Content-Type: application/json

{"error":"not_found"}
```

and you can say which of the six codes each of `GET /todos`, `POST /todos` with
an empty title, and a crash inside your own handler will eventually deserve —
`200`, `400` and `500` — and why the middle one is not a 500.
""",
    pitfalls=[
        "Answering 500 for bad client input. It says \"I broke\", so it goes in your error budget and pages someone. `{\"title\":\"\"}` is a 400 and always was.",
        "Answering 404 for a route you do handle when the *record* is missing — that one is correct — but also answering 404 when your own code threw. A caught exception is a 500; hiding it behind \"not found\" means nobody ever finds it.",
        "Reaching for 403, 409 or 422 because they sound more precise. This project uses six codes. A vocabulary the client actually understands beats an exact one it does not.",
        "Treating today's 404 as scaffolding to delete in module 7. It is the fall-through, and it stays exactly where it is for the next fifteen modules.",
    ],
    warmup=[
        _pq("`POST /todos` arrives with the body `{\"title\":\"\"}` — a valid path, an "
            "empty title. Which code?",
            ["400 — the address was fine and the payload was not",
             "404 — the request could not be fulfilled",
             "500 — the server could not create the todo",
             "204 — nothing was created, so there is no content"],
            0,
            "404 is about the address, and `/todos` exists. 500 says the fault is "
            "yours, which would put someone else's typo in your incident count. "
            "400 says \"your request was wrong\", which is exactly what happened."),
    ],
    exercises=[
        _pfix("todo-m5-codes-fix1", "Not my fault",
              "This server handles no routes, so it answers every request the same "
              "way — with a 500, which says the server broke. Nothing broke. The "
              "client asked for an address that does not exist. Fix the code and the "
              "error name.",
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 500, { error: "server_error" });
}
"""),
              _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}
"""),
              [("GET /\nGET /todos\nDELETE /todos/1",
                '404 {"error":"not_found"}\n404 {"error":"not_found"}\n404 {"error":"not_found"}')],
              ["500 means the server broke. Did it?",
               "There is nothing at the address the client asked for.",
               '`send(res, 404, { error: "not_found" });`'],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why does it matter whether a bad request is answered 400 or 500?",
            ["500 says the fault is the server's — it is what alerting, retries and error budgets are counted from",
             "500 responses are slower than 400 responses",
             "A 400 body can contain JSON and a 500 body cannot",
             "Browsers refuse to display a 500"],
            0,
            "The two are read by machines before they are read by people. A 500 "
            "means \"I broke\", so it retries, alerts and counts against you. "
            "Answering 500 to a malformed title means somebody gets paged for a "
            "client's typo."),
        _pq("Module 7 adds `GET /todos`. What happens to this module's "
            "`send(res, 404, …)` line?",
            ["It stays, at the bottom, as the fall-through every unmatched request reaches",
             "It is deleted and replaced by the route",
             "It moves above the route so it runs first",
             "It becomes a 500 once real routes exist"],
            0,
            "You wrote the default before the special cases. A router built that "
            "way cannot forget its 404, which is the usual way a hand-written router "
            "ends up hanging on an unknown path."),
    ],
)

_M5_FINAL = _pch(
    "todo-m5-build", "Module 5 build — every response is deliberate JSON", "Easy",
    "Write both functions.\n\n"
    "`send` takes the response, a status code and an object, sets the status and "
    "a JSON `Content-Type`, and writes the object as JSON text. `handler` answers "
    "every request — any method, any path — with a `404` and the body "
    "`{\"error\":\"not_found\"}`, by calling `send`.\n\n"
    "Nothing reads the request yet, so there is still nothing to branch on.",
    _server("""
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}
"""),
    """function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}""",
    [("GET /\nGET /todos\nPOST /todos {\"title\":\"Buy milk\"}\nDELETE /todos/1\nPATCH /todos/1 {\"done\":true}",
      '404 {"error":"not_found"}\n404 {"error":"not_found"}\n404 {"error":"not_found"}'
      '\n404 {"error":"not_found"}\n404 {"error":"not_found"}')],
    ["Two functions: the helper first, then the handler that calls it.",
     "`send(res: ServerResponse, status: number, data: object): void` — the response "
     "first, because it is the thing being written to.",
     "Inside `send`: `writeHead` with the status and the header object, then `end` "
     "with the stringified data. In that order.",
     "Inside `handler`: one call, `send(res, 404, { error: \"not_found\" })`.",
     "The replayer prints the status and then the body, so every line comes back "
     '`404 {"error":"not_found"}`.'],
)

_TODO_MODULES.append(_pmod(
    key="todo-json", number=5, phase="network",
    title="Status codes and JSON",
    what="writeHead, Content-Type, and one `send` helper for every response",
    goal="Answer with a status code and a JSON body, from a single place.",
    why=_M5_WHY,
    est_minutes=45,
    builds_on=["todo-server"],
    concepts=["status codes", "writeHead", "Content-Type", "JSON responses",
              "a single response helper"],
    objectives=[
        "Set a status code deliberately with `writeHead`, and say where module 4's 200 came from",
        "Explain what `Content-Type` does and what happens when it is absent",
        "Write a `send(res, status, data)` helper and justify each part of its signature",
        "Say why `data` is typed `object` rather than `Todo` or `unknown`",
        "Name the six status codes this project uses and which of them are the client's fault",
        "Explain why a server with no routes should answer 404 rather than 200 or 500",
    ],
    deliverable="Every response is JSON with a deliberate status code, written in "
                "exactly one place in your file.",
    brief=_M5_BRIEF,
    syntax=_M5_SYNTAX,
    steps=[_M5_S1, _M5_S2, _M5_S3, _M5_S4],
    final_build=_M5_FINAL,
    acceptance=[
        "`curl -i localhost:3000/todos` prints `HTTP/1.1 404 Not Found` on the first line.",
        "The same response carries a `Content-Type: application/json` header — check it with `-i`, because nothing else can tell you.",
        "The body is exactly `{\"error\":\"not_found\"}` and parses as JSON.",
        "Every method and every path gets that same response — nothing reads the request yet.",
        "`writeHead` and `end` appear exactly once in your file, both inside `send`.",
        "Your handler is one line long, and it is a call to `send`.",
    ],
    manual_test="""
With `node server.ts` running:

```bash
curl -i localhost:3000
curl -i localhost:3000/todos
curl -i -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
```

All three print the same three things: `404 Not Found`, a `Content-Type:
application/json` header, and `{"error":"not_found"}`.

Now break it on purpose and watch what changes:

```bash
# 1. delete the header object from writeHead, restart, and run:
curl -i localhost:3000
# the Content-Type line is GONE — not wrong, absent.

# 2. put it back, then move writeHead below res.end, restart, and run:
curl -i localhost:3000
# ERR_HTTP_HEADERS_SENT in the server's terminal.
```

Both of those are worth doing once. The first is invisible without `-i`, and the
second is the error the replayer turns into a 500 you did not write.
""",
    reference="""// server.ts — module 5
//
// Two changes from module 4, and the second is the one that matters.
//
//   1. The status code and the Content-Type are now decisions rather than
//      whatever Node did in the absence of one.
//   2. Both live in ONE function. Every response from here to module 20 goes
//      through `send`, so a change to how this API answers is a change to three
//      lines rather than to thirty call sites.
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

// The single exit from this application.
//
// `res` first: it is the thing being written to, matching res.writeHead/res.end.
// `status` has no default on purpose — a status you can omit is a status that is
// 200 on the day something has gone wrong, which is the bug module 4 left.
// `data: object` because everything leaves through here: a Todo, an array of
// them, an error record. An array is an object too. It rejects a bare string,
// which is deliberate — that is not a JSON response.
//
// writeHead BEFORE end. writeHead writes the top of the response; end writes the
// bottom and closes it. The other order throws ERR_HTTP_HEADERS_SENT.
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

// Nothing reads the request until module 6, so every request gets the same
// answer — and for a server that handles no routes, "there is nothing at this
// address" is the true one. Module 7 adds GET /todos ABOVE this line and leaves
// the line itself alone: it becomes the fall-through, which is why this router
// cannot forget its 404.
function handler(req: IncomingMessage, res: ServerResponse): void {
  send(res, 404, { error: "not_found" });
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Add `res.setHeader(\"X-Powered-By\", \"handwritten\")` inside `send` before the `writeHead`, and confirm with `curl -i` that both headers arrive. That is the payoff of having one place: it took one line.",
        "Change `send` to use `res.statusCode = status` and `res.setHeader(…)` instead of `writeHead`, and check the response is identical. `writeHead` is the two of them in one call.",
        "Send `application/json; charset=utf-8` instead, then put a todo title with an emoji in it through `JSON.stringify` and see whether anything actually changes. Work out why not.",
        "Try `send(res, 200, \"hello\")` and read the type error. Then work out what would have gone down the wire in plain JavaScript.",
        "Log every response from inside `send` — `console.error(status, JSON.stringify(data))` — and note that you now have request logging for the whole application, for one line, forever. `console.error` rather than `log` so it does not land in the judged stdout.",
    ],
    glossary=[
        _pgloss("status code", "The three-digit number at the top of every response. Client code branches on it before it reads a byte of the body."),
        _pgloss("writeHead", "`res.writeHead(status, headers)` — writes the status line and headers. Must come before the body."),
        _pgloss("Content-Type", "The header saying how to read the body. `application/json` here. Absent unless you set it."),
        _pgloss("ERR_HTTP_HEADERS_SENT", "\"You tried to set the top of a response that has already gone out\" — almost always a `writeHead` after an `end`."),
        _pgloss("404", "There is nothing at this address. About the URL, not the payload."),
        _pgloss("400", "Your request was wrong. The address was fine; what you sent through it was not."),
        _pgloss("500", "*I* broke. The one code that is the server's fault, and the reason phase 4 exists."),
        _pgloss("send", "This project's one response helper. Status and object in, JSON response out — the single place every answer is written."),
    ],
    cheatsheet="""
```ts
// The single exit from the application. Every response goes through it.
function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });  // top of the response
  res.end(JSON.stringify(data));                                  // bottom, and close
}

send(res, 404, { error: "not_found" });
```

| Code | Means | Whose fault |
|---|---|---|
| 200 | Here it is | — |
| 201 | Created, and here it is | — |
| 204 | Done, deliberately no body | — |
| 400 | Your request was wrong | the client's |
| 404 | Nothing at this address | the client's |
| 500 | I broke | **yours** |

| Symptom | Cause |
|---|---|
| `ERR_HTTP_HEADERS_SENT` | `writeHead` after `end` — or two `send`s on one request |
| no `Content-Type` in `curl -i` | the header object was left off `writeHead` |
| `[object Object]` in the body | `res.end(data)` without `JSON.stringify` — TypeScript catches this |
| right fields, failing test | key order — `JSON.stringify` follows the object literal |
| status always 200 | `writeHead` never called, or `send` hard-codes it |

**The habit:** every response is `send(res, status, data)`. Never `res.end` directly again.
""",
    self_check=[
        "Can you say where module 4's 200 came from, and why an accidental 200 is worse than a wrong one you chose?",
        "Can you explain what is sent when you leave `Content-Type` off — and why \"nothing\" is a worse answer than \"the wrong type\"?",
        "Can you justify each of the four parts of `send`'s signature to someone who wants to add a default status?",
        "Can you name which of 400, 404 and 500 mean the fault is yours?",
        "Can you say why this module's 404 is not scaffolding that module 7 deletes?",
    ],
    review=[
        _pq("What is the difference between `res.writeHead(404)` and `res.end(\"not found\")`?",
            ["The first writes the status line and headers; the second writes the body and closes the response",
             "They are two ways of doing the same thing",
             "The first sets the body and the second sends it",
             "`writeHead` is for errors and `end` is for successes"],
            0,
            "They are the top and the bottom of one response. That is also why the "
            "order is fixed: once the bottom has gone out, the top went with it."),
        _pq("A handler does `res.end(JSON.stringify(todo))` and nothing else. Which "
            "two things are wrong?",
            ["No status was chosen — so it is 200 whatever happened — and no `Content-Type` was sent",
             "`JSON.stringify` cannot take a `Todo`, and `res.end` cannot take a string",
             "The response is never closed, and the client hangs",
             "Nothing is wrong; that is what `send` does"],
            0,
            "The body is fine. What is missing is everything above it: an "
            "accidental 200, and no header saying the bytes are JSON."),
        _pq("Why does `send` take `res` as its first parameter rather than reading it "
            "from an outer scope?",
            ["Each request has its own `res`, and `send` is a top-level function with no request in scope",
             "TypeScript requires the receiver to be the first parameter",
             "It makes the call shorter",
             "So the same call can send to several responses at once"],
            0,
            "There is no ambient `res` — a server handles one request per call to "
            "`handler`, each with its own pair of objects. Passing it in is the only "
            "thing that could work, and the order mirrors `res.writeHead(…)`."),
        _pq("Which of these does `data: object` reject?",
            ["`send(res, 200, \"ok\")`",
             "`send(res, 200, todos)` where `todos` is a `Todo[]`",
             "`send(res, 404, { error: \"not_found\" })`",
             "`send(res, 201, addTodo(\"Buy milk\"))`"],
            0,
            "Arrays and object literals are both objects, and `addTodo` returns a "
            "`Todo`. A string is not an object, and rejecting it is the point: a "
            "bare string is not a JSON response."),
    ],
    milestone="Every answer your server gives is now a deliberate status code and "
              "a JSON body — written in one place, which is the line the next "
              "fifteen modules are built on top of.",
))
