# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 4 — Your first server.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# INTRODUCES: `node:http` (named imports), `createServer`, `listen`, the
# request/response pair, and `res.end`. FIRST MODULE TO USE `_server` — every
# program from here on boots a real server and is driven by the given replayer.
#
# WHAT THE LEARNER WRITES vs WHAT IS GIVEN: the replayer owns `createServer`
# and `listen`, so the judged exercises are always the `handler` function and
# nothing else. `createServer`/`listen` are still taught in the syntax primer
# and step 2, because the learner's OWN server.ts needs them — the judged
# programs simply do not, and pretending otherwise would mean blanking code the
# replayer has to control.
#
# DELIBERATELY NOT HERE: `res.writeHead` and status codes (module 5),
# `req.method` and the URL (module 6), routing (module 7). Every request gets
# the same answer, and step 3 makes that the point rather than an omission.
# ---------------------------------------------------------------------------

_M4_WHY = (
    "Three modules in, you have a store that can add, list and find todos — "
    "and absolutely nothing can reach it. A function call is not an API. "
    "Everything so far runs, prints and exits; a server is the opposite shape "
    "of program, one that starts and then *waits*, and getting that shape into "
    "your head is the whole job of this module."
)

_M4_BRIEF = """
### The whole module in one line

Start a program that does not exit, and make it answer when something asks.

### The shape change

Every program you have written so far runs top to bottom and stops. A server
does not:

```
your programs so far:   start → do the work → print → exit
a server:               start → listen → wait ... → handle a request → wait ...
```

That "wait" is why your terminal will appear to hang when you run it. It has not
frozen; it is doing its job. `Ctrl+C` stops it, and you will do that several
hundred times before this project is finished.

### Three things, and what each one is

```ts
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
```

**`handler`** is your code. It is called once per request, and gets two things:
`req`, everything the client sent, and `res`, the thing you write the answer
into. You will spend the rest of this project writing versions of this function.

**`createServer(handler)`** builds a server that will call your function. It does
not start anything — nothing is listening yet.

**`listen(port, host, callback)`** is what actually opens the port. From this
moment the process stays alive.

### Why the import is written that way

```ts
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
```

Named, not default. You could write `import http from "node:http"` and call
`http.createServer(…)` — but then annotating the handler needs
`http.IncomingMessage`, which asks the compiler to treat `http` as a *namespace*
as well as a value. Importing the two types by name is simpler and says exactly
what you are using.

The `type` keyword on `IncomingMessage` and `ServerResponse` marks them as
type-only imports: they exist for the compiler and vanish at runtime. That is
not decoration here — Node runs your `.ts` by **stripping** the types, so an
import that turns out to be types-only has to disappear cleanly. Saying `type`
makes that guaranteed rather than inferred.

### `res.end` does two things

```ts
res.end("hello");
```

It writes the body **and** it finishes the response. Both halves matter:

- Forget to call it and the client waits forever. No error, no crash, no log
  line — just a request that never comes back. This is the single most common
  way a hand-written Node server hangs, and you will do it at least once.
- Call it twice and the second call is an error, because the response is
  already gone.

So: **exactly one `res.end` on every path through your handler.** Once routing
arrives in module 7 and there are five paths, that sentence becomes something
you actively check for.

### One answer for everybody, for now

This handler replies `hello` to `GET /`, to `POST /todos`, and to
`DELETE /nonsense`. It cannot tell them apart, because nothing has looked at
`req` yet — that is module 6, and routing on what it finds is module 7.

Resist wiring the store in now. A server that answers one thing correctly is a
finished module; a server that half-routes is a mess you debug in module 7.
"""

_M4_SYNTAX = [
    _syn(
        'import { createServer, type IncomingMessage, type ServerResponse } from "node:http";',
        "Bring in the server builder and the two types you annotate a handler "
        "with. Named imports, and `type` on the two that are types.",
        """
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
""",
        "`import http from \"node:http\"` also works for the *value*, but then "
        "`http.IncomingMessage` asks the compiler to treat `http` as a namespace "
        "too. Import the types by name and the problem does not arise.",
    ),
    _syn(
        "function handler(req: IncomingMessage, res: ServerResponse): void { … }",
        "The function the server calls once per request. `req` is what the client "
        "sent; `res` is what you write the answer into.",
        """
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}
""",
        "`req` is unused in this module and that is fine — nothing has looked at "
        "the request yet. Reading it is module 6.",
    ),
    _syn(
        "createServer(handler)",
        "Build a server that will call your handler. Nothing is listening yet.",
        """
const server = createServer(handler);
""",
        "Pass the function, do not call it: `createServer(handler)`, never "
        "`createServer(handler())`. The second runs your handler once, immediately, "
        "with no request to give it.",
    ),
    _syn(
        'server.listen(3000, "127.0.0.1", () => console.log("listening"));',
        "Open the port. From here the process stays alive and waits.",
        """
const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
        "Port already in use? A previous run is still going. Find it and stop it — "
        "`EADDRINUSE` means exactly that and nothing else.",
    ),
    _syn(
        'res.end("hello")',
        "Write the body and finish the response. Exactly one of these on every "
        "path through your handler.",
        """
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}
""",
        "Forget it and the client waits forever, with no error anywhere. Call it "
        "twice and the second is an error. Neither is caught by the compiler.",
    ),
    _syn(
        "type Todo = { id: number; title: string; done: boolean };",
        "The store from modules 1-3. Nothing in this module touches it yet — "
        "wiring it up is module 7.",
        "",
        "",
        recap=True,
    ),
]

_M4_S1 = _pstep(
    "handler", "The function that answers",
    "One function, called once per request, given two objects.",
    """
Start a fresh section at the bottom of `server.ts`, under the store. First the
import:

```ts
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
```

Imports go at the top of the file in real code — put it there. It is written
here as "first" because it is the first thing this module needs, not because of
where it sits.

Then the handler:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}
```

### What the two parameters are

**`req: IncomingMessage`** — everything the client sent. The method, the path,
the headers, and (from module 8) the body. You are not going to read any of it
this module, which is why every request will get the same answer.

**`res: ServerResponse`** — the thing you write the answer into. Note that you do
not *return* a response; you write into an object that was handed to you. That
surprises people coming from languages where a handler returns a value, and it
is the reason a handler that forgets to write anything fails silently rather
than failing to compile.

**`: void`** — the handler gives nothing back. All of its effect is on `res`.

### `req` is unused, and that is fine

TypeScript will not complain: `strict` does not include unused-parameter
checking. Leave it named `req` rather than deleting it — the signature is fixed
by what the server will call, and module 6 needs it.
""",
    """
Your `server.ts` compiles with the import and the handler in it. Nothing runs
differently yet — `handler` is defined and nobody calls it.

If you get "Cannot find module 'node:http'", check the spelling of the `node:`
prefix. If you get an error about `IncomingMessage` not being a type, you wrote
a default import — go back and use the named form.
""",
    pitfalls=[
        "Writing `import http from \"node:http\"` and then annotating with `http.IncomingMessage`. That needs `http` to be a namespace as well as a value; use named type imports instead.",
        "Expecting to `return` a response. You do not — you write into `res`. A handler that returns a value and never touches `res` compiles cleanly and hangs.",
        "Deleting the unused `req` parameter. The signature is fixed by the server that will call it, and module 6 needs it back.",
    ],
    warmup=[
        _pq("Why is `type` written on `IncomingMessage` and `ServerResponse` but not "
            "on `createServer`?",
            ["The first two are only used as types, and `type` guarantees they vanish at runtime",
             "`createServer` is a type and the other two are values",
             "It is a style choice with no effect",
             "`type` is required on every third import"],
            0,
            "Node runs your `.ts` by stripping types, so an import used only in "
            "annotations has to disappear cleanly. Marking it `type` makes that "
            "guaranteed. `createServer` is a real function you call, so it stays."),
    ],
    exercises=[
        _pex("todo-m4-handler-1", "Type the handler",
             "The handler's parameters are not annotated, so the program does not "
             "compile. Give them the two types you imported.",
             _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}
"""),
             "req: IncomingMessage, res: ServerResponse",
             [("GET /", "200 hello")],
             ["Two parameters, two imported types, in the order the server passes them.",
              "The request comes first, the response second.",
              "`function handler(req: IncomingMessage, res: ServerResponse): void {`"]),
    ],
)

_M4_S2 = _pstep(
    "listen", "Start it",
    "`createServer` builds it; `listen` opens the port.",
    """
Two more lines at the bottom of your own `server.ts`:

```ts
const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
```

**`createServer(handler)`** hands your function to a server object. Nothing is
open yet — this line alone would let the program exit immediately.

**`listen(port, host, callback)`** opens the port. Three arguments worth
knowing:

- **`3000`** — the port. Anything above 1024 is yours to use without special
  permission. If you get `EADDRINUSE`, a previous run of your server is still
  going; stop it.
- **`"127.0.0.1"`** — this machine only. Nothing outside your computer can
  reach it, which is what you want while learning.
- **the callback** — runs once the port is actually open. Printing there is how
  you know it worked; printing *after* the `listen` call instead would tell you
  nothing, because `listen` does not wait.

Now run it:

```bash
node server.ts
```

The terminal prints `listening on 3000` and then sits there. **That is correct.**
It has not hung — it is waiting for a request, which is the entire point of a
server. Leave it running and open a second terminal.

### The judged exercises do this for you

You will notice the exercises in this module have no `createServer` or `listen`
in the part you edit. That is on purpose: a *replayer* at the bottom of each
program starts your handler on a free port, fires a script of requests at it,
and prints one line per request. It is given, you never edit it, and step 4
reads it properly.
""",
    """
In one terminal:

```bash
$ node server.ts
listening on 3000
```

and it stays there. In another:

```bash
$ curl localhost:3000
hello
```

If curl hangs instead of printing, your handler is not calling `res.end` — go to
step 3. If curl says "connection refused", the server is not running, or it is
on a different port than you asked for.
""",
    pitfalls=[
        "`createServer(handler())` — with the brackets. That calls your handler once, right now, with nothing to give it, and passes the *result* to createServer. The error is confusing; the fix is to delete two characters.",
        "`EADDRINUSE`. A previous `node server.ts` is still running. It is not a code bug, and restarting your editor will not fix it — stop the process.",
        "Printing \"listening\" after the `listen` call rather than in its callback. `listen` does not wait, so the message tells you nothing about whether the port opened.",
        "Expecting the terminal to come back. It will not, and should not. `Ctrl+C` when you are done.",
    ],
    quiz=[
        _pq("`createServer(handler)` runs and the program exits immediately. Why?",
            ["`createServer` builds a server but opens nothing — `listen` is what keeps the process alive",
             "The handler threw an error",
             "`createServer` needs a port argument",
             "Node exits unless you call `process.stdin.resume()`"],
            0,
            "Nothing is listening, so there is no open handle keeping the event loop "
            "alive, so Node has nothing left to do and exits. `listen` is the line "
            "that changes that."),
    ],
)

_M4_S3 = _pstep(
    "end", "Answer — and the hang when you don't",
    "`res.end` writes the body and closes the response. Exactly one per path.",
    """
```ts
res.end("hello");
```

One call, two jobs: it writes `hello` as the body, and it tells the client the
response is over. Both matter, and the failure modes are opposite.

### Forget it, and the request never comes back

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  // ... work out the answer ...
}
```

That compiles. It runs. The server does not crash, nothing appears in the log,
and `curl` sits there until you give up. The client is waiting for a response
that is never coming, because nothing ever told it the response was finished.

This is the most common way a hand-written Node server hangs, and TypeScript
cannot help you: "did every path through this function write a response?" is not
a question a type checker asks. It is a question *you* ask, every time you add a
branch — which is why, from module 7 onwards, `return` after every `res.end` is
worth making a habit.

### Call it twice, and the second one errors

```ts
res.end("hello");
res.end("again");     // the response is already gone
```

The usual cause is a missing `return`:

```ts
if (somethingWrong) {
  res.end("bad");     // ← no return, so execution carries on
}
res.end("hello");     // ← and ends the response a second time
```

Module 7 has five paths and this bug is waiting in every one of them. The habit
that prevents it is one line long: **`return` immediately after every
`res.end`.**

### What the status code is right now

You have not set one, so it is **200**. That is Node's default, and it is
correct for a successful `GET` — but it is *accidentally* correct, and an
accidental 200 is exactly what you get on an error path too. Module 5 makes it
deliberate.
""",
    """
`curl localhost:3000` prints `hello` and returns to the prompt. `curl
localhost:3000/anything` does the same.

Then break it deliberately: comment out the `res.end` line, restart, and run
`curl localhost:3000` again. It hangs — no error, no log, nothing — until you
press `Ctrl+C`. Sit with that for a moment; it is what the bug looks like from
the outside, and recognising it will save you an hour later. Put the line back.
""",
    pitfalls=[
        "No `res.end` on some path. Silent hang. No error, no log line, and the compiler cannot see it — the only symptom is a curl that never returns.",
        "A missing `return` after `res.end`, so a later `res.end` runs too. Fine today with one path; a real bug in module 7 with five.",
        "Assuming the 200 you are getting was a decision. Nobody set it — it is the default, and it will be just as 200 when something has gone wrong. Module 5 fixes that.",
    ],
    warmup=[
        _pq("A handler computes the answer correctly, logs it, and returns — but never "
            "calls `res.end`. What does the client see?",
            ["Nothing — the request hangs until the client gives up",
             "A 500 error",
             "An empty 200 response",
             "A compile error before the server starts"],
            0,
            "The response was never finished, so there is nothing to send and nothing "
            "closes the connection. No error is raised anywhere, which is what makes "
            "this so unpleasant to track down."),
    ],
    exercises=[
        _pex("todo-m4-end-1", "Send the answer",
             "The handler does nothing, so every request hangs. Answer with the text "
             "`hello`.",
             _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}
"""),
             '  res.end("hello");',
             [("GET /\nGET /todos", "200 hello\n200 hello")],
             ["One call writes the body and finishes the response.",
              "The method is on `res`, and the body goes in as a string.",
              '`  res.end("hello");`']),
        _pfix("todo-m4-end-fix1", "It answers with nothing",
              "This server responds — the status comes back — but the body is empty. "
              "The client wanted `hello`. Fix it.",
              _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end();
}
"""),
              _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}
"""),
              [("GET /", "200 hello")],
              ["The response is being finished, but nothing is being written into it.",
               "`res.end()` closes the response; `res.end(text)` writes a body first.",
               '`res.end("hello");`'],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why is `return` after every `res.end` worth making a habit, even though "
            "this module's handler has only one path?",
            ["Without it, a later `res.end` on the same request runs and errors — and module 7 has five paths",
             "`res.end` does not actually send unless you return",
             "TypeScript requires a return in a `void` function",
             "It makes the response faster"],
            0,
            "`res.end` does not stop your function. Execution carries on, and if it "
            "reaches another `res.end` the response has already gone. With one path "
            "it cannot happen; with five it happens constantly."),
    ],
)

_M4_S4 = _pstep(
    "replayer", "How the exercises drive your server",
    "Read the given code once, and it becomes invisible.",
    """
Every judged exercise from here on has a block at the bottom marked
`request replayer (given — don't edit)`. You never write it, but reading it once
is worth the two minutes, because otherwise the exercises feel like magic.

It does four things:

**1. Starts your handler on a free port.**

```ts
const server = createServer((req, res) => { ... handler(req, res) ... });
await new Promise<void>((ok) => server.listen(0, "127.0.0.1", () => ok()));
```

Port `0` means "any free port" — so two exercises never collide. It then reads
the port back out with `server.address()`.

**2. Reads a request script from stdin**, one request per line:

```
GET /
POST /todos {"title":"Buy milk"}
```

**3. Sends each one and prints `<status> <body>`:**

```
200 hello
201 {"id":1,"title":"Buy milk","done":false}
```

That format is why a routing mistake shows up as a wrong *status code* rather
than as a mystery. When an exercise fails, read the status first.

**4. Catches anything your handler throws** and turns it into a `500`:

```ts
Promise.resolve(handler(req, res)).catch((err: unknown) => { ... 500 ... });
```

This is a real error boundary, and it has been quietly protecting you since your
first exercise. **You will write this yourself in module 16** — at which point
you can come back and compare.

### Two consequences worth remembering

- **Requests run in order, one at a time.** So the output is deterministic and
  an expected output can be written down at all. A real server handles them
  concurrently.
- **The status is printed before the body.** `200 hello` is one line: status,
  space, body.
""",
    """
You can look at the replayer in any exercise below and say what each of its four
parts does, and you know that the `500` you will occasionally see comes from its
`catch` rather than from anything you wrote deliberately.
""",
    pitfalls=[
        "Editing the replayer to make a test pass. It is identical in every exercise, and the thing being graded is always the code above it.",
        "Reading `500` as \"my server returned 500\". It usually means your handler *threw* and the boundary caught it — look at the exception, not the status.",
        "Expecting concurrency. The replayer sends one request at a time, in order, which is what makes the expected output writable.",
    ],
    exercises=[
        _pch("todo-m4-build-drill", "Answer every request", "Intro",
             "Write a handler that answers `ready` to any request at all — every method, "
             "every path. One line in the blank.",
             _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("ready");
}
"""),
             '  res.end("ready");',
             [("GET /\nPOST /todos\nDELETE /nonsense\nGET /todos/99",
               "200 ready\n200 ready\n200 ready\n200 ready")],
             ["Nothing looks at the request, so there is nothing to branch on.",
              "One call, writing the body and finishing the response.",
              '`  res.end("ready");`']),
    ],
    quiz=[
        _pq("An exercise prints `500 {\"error\":\"server_error\"}` for one of its "
            "requests. What is the most likely cause?",
            ["Your handler threw an exception, and the replayer's boundary caught it",
             "You returned the wrong status code from your handler",
             "The port was already in use",
             "The replayer could not parse that line of stdin"],
            0,
            "The replayer wraps your handler in a `catch` that answers 500 — the same "
            "thing a framework does. A 500 you did not write means something threw, "
            "so look for the exception rather than for a status code in your code."),
    ],
)

_M4_FINAL = _pch(
    "todo-m4-build", "Module 4 build — a server that answers", "Easy",
    "Write the handler for a server that answers `hello` to every request, "
    "whatever the method and whatever the path.\n\n"
    "Give it the right parameter types and make sure every request gets exactly "
    "one response. The imports and the replayer are already there.",
    _server("""
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}
"""),
    """function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");
}""",
    [("GET /\nGET /todos\nPOST /todos {\"title\":\"Buy milk\"}\nDELETE /todos/1",
      "200 hello\n200 hello\n200 hello\n200 hello")],
    ["The whole handler goes in the blank: signature and body.",
     "`req: IncomingMessage, res: ServerResponse`, returning `void`.",
     "One `res.end(\"hello\")` — nothing looks at the request yet, so there is "
     "nothing to branch on.",
     "The status is 200 because that is Node's default. You do not set it until "
     "module 5."],
)

_TODO_MODULES.append(_pmod(
    key="todo-server", number=4, phase="network",
    title="Your first server",
    what="createServer, listen, and a response that says hello",
    goal="Get a real HTTP server running and answer one request.",
    why=_M4_WHY,
    est_minutes=40,
    builds_on=["todo-shape"],
    concepts=["node:http", "request/response", "listen", "ports", "res.end"],
    objectives=[
        "Describe how a server's shape differs from every program you have written so far",
        "Import `createServer` and the two handler types the way this project does, and say why",
        "Write a handler and name what `req` and `res` each are",
        "Open a port with `listen` and explain what the callback is for",
        "Predict what happens when a handler forgets `res.end`, and recognise it from outside",
        "Read the given replayer and say what each of its four parts does",
    ],
    deliverable="A real HTTP server on port 3000 that answers every request from "
                "code you wrote — reachable with curl.",
    brief=_M4_BRIEF,
    syntax=_M4_SYNTAX,
    steps=[_M4_S1, _M4_S2, _M4_S3, _M4_S4],
    final_build=_M4_FINAL,
    acceptance=[
        "`node server.ts` prints a listening message and then stays running.",
        "`curl localhost:3000` prints `hello` and returns to the prompt.",
        "`curl localhost:3000/anything` prints `hello` too — nothing routes yet.",
        "Commenting out `res.end` makes curl hang rather than error, and you recognise that symptom.",
        "You can say why the response is a 200 without having set one.",
    ],
    manual_test="""
In one terminal:

```bash
node server.ts
```

In another:

```bash
curl localhost:3000
curl localhost:3000/todos
curl -i localhost:3000            # -i shows the status line: HTTP/1.1 200 OK
curl -i -X POST localhost:3000    # same answer — nothing looks at the method yet
```

Get used to `-i` now. From module 5 the status code is the most important part
of the response, and it is the part you cannot see without it.
""",
    reference="""// server.ts — module 4
//
// Imports go at the top of the file. Named, not default: annotating the handler
// needs IncomingMessage and ServerResponse as TYPES, and `type` on them
// guarantees they vanish when Node strips types to run this file.
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

// Called once per request. `req` is everything the client sent — unused for now,
// because reading it is module 6. `res` is what you write the answer into: you
// do not RETURN a response, which is why a handler that forgets to write one
// fails silently rather than failing to compile.
//
// Exactly one res.end on every path. Forget it and the client waits forever
// with no error anywhere; call it twice and the second one errors. Neither is
// something the compiler can catch.
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");     // status is 200 — Node's default, not a decision.
}                       //                  Module 5 makes it deliberate.

// createServer builds it and opens nothing; listen is what keeps the process
// alive. The callback runs once the port is actually open — printing after the
// listen call instead would tell you nothing, because listen does not wait.
const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Answer with HTML instead: `res.end(\"<h1>hello</h1>\")`, then open localhost:3000 in a browser. You never said it was HTML — no `Content-Type` header goes out at all — so whether you get a heading or the raw tags is the browser guessing at the bytes. Module 5 stops the guessing.",
        "Add a second `res.end` after the first and read the error Node gives you. That is the bug a missing `return` causes in module 7.",
        "Start two copies of the server on the same port and read `EADDRINUSE` properly. You will meet it again.",
        "Print `req.method` inside the handler — just to stdout, not to the response — and watch it change as you curl with `-X POST`. That is module 6, one line early.",
    ],
    glossary=[
        _pgloss("handler", "The function a server calls once per request, given a request and a response object."),
        _pgloss("IncomingMessage", "Node's type for the request — method, path, headers and (later) the body."),
        _pgloss("ServerResponse", "Node's type for the response you write into. You do not return it; you fill it in."),
        _pgloss("port", "The number a server listens on. Above 1024 needs no special permission."),
        _pgloss("EADDRINUSE", "\"That port is taken\" — almost always a previous run of your own server still going."),
        _pgloss("type-only import", "`import { type X }` — an import used solely in annotations, guaranteed to vanish at runtime."),
        _pgloss("replayer", "The given block at the bottom of each exercise that boots your handler on a free port and fires a request script at it."),
    ],
    cheatsheet="""
```ts
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

// Called once per request. You write into `res`; you do not return anything.
function handler(req: IncomingMessage, res: ServerResponse): void {
  res.end("hello");        // writes the body AND finishes the response
}

const server = createServer(handler);                    // builds — opens nothing
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
```

| Symptom | Cause |
|---|---|
| curl hangs, no error anywhere | a path with no `res.end` |
| "write after end" error | two `res.end` calls — usually a missing `return` |
| `EADDRINUSE` | a previous run is still listening |
| terminal does not come back | correct — that is the server waiting |
| status is 200 and you never set one | Node's default. Module 5 makes it deliberate |

**The habit to start now:** `return` immediately after every `res.end`.
""",
    self_check=[
        "Can you explain how a server's shape differs from every program you wrote in modules 1-3?",
        "Can you say what `req` and `res` each are, and why you write into one rather than returning it?",
        "Can you describe, from the client's side, what a missing `res.end` looks like — and why nothing logs an error?",
        "Can you say why `createServer(handler())` is wrong, and what it actually does?",
        "Can you name where the 200 came from, given you never set a status code?",
    ],
    review=[
        _pq("What is the difference between `createServer(handler)` and "
            "`server.listen(3000, …)`?",
            ["The first builds a server that will call your function; only the second opens a port and keeps the process alive",
             "The first opens the port; the second starts accepting requests",
             "They are two names for the same operation",
             "The first is for HTTP and the second for HTTPS"],
            0,
            "`createServer` is pure construction — a program that only calls it exits "
            "immediately, because nothing is holding the event loop open. `listen` is "
            "the line that changes that."),
        _pq("Your handler is `function handler(req, res) { const answer = \"hello\"; }`. "
            "What happens when you curl it?",
            ["It hangs — the response was never finished",
             "It returns an empty 200",
             "It returns 500",
             "It fails to compile, because `answer` is unused"],
            0,
            "Nothing wrote to `res` and nothing closed it, so there is no response to "
            "send and nothing tells the client it is over. No error is raised — which "
            "is what makes it hard to find."),
        _pq("Why does the replayer use `server.listen(0, …)` rather than a fixed port?",
            ["`0` means \"any free port\", so exercises can never collide with each other or with your own server",
             "`0` disables networking so the tests run offline",
             "It is a placeholder the judge substitutes",
             "Port 0 is faster because it skips the TCP handshake"],
            0,
            "Port 0 asks the OS for any free port; the replayer then reads it back "
            "with `server.address()`. That is also why your own `node server.ts` on "
            "3000 can keep running while you solve exercises."),
    ],
    milestone="You have a server. Something outside your program can reach code "
              "you wrote — which is the whole difference between a script and a "
              "service.",
))
