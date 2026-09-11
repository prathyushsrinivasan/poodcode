# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 8 — Reading a request body.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# THE BIGGEST SYNTAX JUMP IN THE TRACK, and the roadmap said so before it was
# written: `req.on("data")`, `setEncoding`, `new Promise`, `.then`, `async` and
# `await` all land here. The module answers that by making the jump three
# smaller ones, each motivated by the pain of the one before it:
#
#   step 1  callbacks        works, and the handler can no longer route
#   step 2  a promise        the collecting moves out of the handler
#   step 3  async/await      the value comes back where the router can use it
#   step 4  in the router    module 7's shape, unchanged, plus one `await`
#
# That ladder is the module. A rewrite that teaches `await` first and explains
# the events afterwards saves ten minutes and loses the reason any of it exists.
#
# WHY `setEncoding` COMES FIRST (roadmap decision 3): the hand-written ambient
# declaration types a `"data"` chunk as `string`, which is only true once
# `setEncoding("utf8")` has been called. Teaching it first is what makes the
# declaration honest — and it is better practice anyway, since concatenating
# Buffers happens to work right up to the first multi-byte character split
# across a chunk boundary.
#
# WHAT CANNOT BE GRADED HERE, and it is a whole family: every accumulation bug
# in this module — `body = chunk` instead of `body = body + chunk`, resolving
# inside the `"data"` listener instead of `"end"`, answering from the first
# chunk — is INVISIBLE at the body sizes a test can send. Node delivers a
# 20-byte body in exactly one chunk, so the buggy program and the correct one
# print the same thing. This is module 6's lesson again in a new costume (a bug
# that needs a malformed request cannot be a graded `fix`); here it is a bug
# that needs a 64 KB one. All three are taught in prose, pitfalls and quizzes.
#
# The two graded `fix`es were chosen because they fail on a five-byte body:
#   * the response sent outside the `"end"` listener  → answers `""`, instantly
#   * a missing `await`                               → answers `{"echo":{}}`
# Both are the module's real mistakes, and both fail at RUN time rather than
# compile time, which is what a `fix` is for.
#
# NO HANG IS GRADED. A promise that never resolves is the signature disaster of
# this module and it costs a 25s Python timeout plus a 30s Rust one to grade, to
# re-teach what module 4 step 3 already covers. It is in the pitfalls, the
# quizzes and the manual test, where you break it on purpose and watch curl sit
# there.
#
# `/echo` IS SCAFFOLDING, and the module says so in step 4: it exists because
# `JSON.parse` belongs to module 9, so the only honest thing to do with a body
# today is hand it back. Module 9 deletes the route and feeds the same
# `await readBody(req)` into the parser.
# ---------------------------------------------------------------------------

# --- Program fragments -----------------------------------------------------
# Shared so that a drill's blank and the module build cannot drift apart. Every
# one of these is code the learner already has from an earlier module, except
# `readBody`, which is what this module is for.

_M8_SEND = """function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}
"""

_M8_READBODY = """function readBody(req: IncomingMessage): Promise<string> {
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
"""

_M8_STORE = """type Todo = {
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
"""

_M8_SEEDED = 'addTodo("Buy milk");\naddTodo("Write tests");\n'

_M8_LIST = ('[{"id":1,"title":"Buy milk","done":false},'
            '{"id":2,"title":"Write tests","done":false}]')


def _m8(*parts):
    """A module-8 judged program: fragments, blank-line separated, then the
    given replayer. The separator is a blank line because a module build blanks
    `readBody` and `handler` together, and its blank has to match the program
    byte for byte."""
    return _server("\n\n".join(p.rstrip("\n") for p in parts))


_M8_WHY = (
    "Your router can tell a `POST /todos` from a `GET /todos` — and answers 404 "
    "to both, because a POST whose body you cannot read is a request for "
    "nothing. Everything you have read off a request so far arrived with it: "
    "the method and the target were sitting on `req` the moment your handler "
    "ran. The body is the one part that is not there yet. It turns up later, in "
    "pieces, through events — which is why this is the module where the shape "
    "of your handler changes rather than just its contents."
)

_M8_BRIEF = """
### The whole module in one line

Collect the pieces of the request body as they arrive, and get the finished
string back somewhere the router can use it.

### What is actually on `req` when your handler runs

```
                         handler runs here
                                │
  ─── request line ─── headers ─┴─ body … body … body ─── (end)
      GET /todos      Content-Type      arrives in chunks, over time
      ^^^^^^^^^^      ^^^^^^^^^^^^
      req.method      req.headers
      req.url         already parsed
```

Node calls your handler as soon as it has read the **headers**. It has to: the
headers are how you decide whether you even want the body. A file upload can be
four gigabytes, and no server buffers four gigabytes before letting you look at
where it was going.

So `req.body` does not exist. There is nothing to put in it yet.

### The body arrives as events

```ts
req.on("data", (chunk: string) => { … });   // 0 or more times, as bytes arrive
req.on("end", () => { … });                 // exactly once, when it is complete
```

`req.on(…)` **registers** a listener and returns immediately. It does not wait.
Every line after it runs before the first chunk shows up — which is the single
most confusing thing about this module, and the source of both bugs you will be
asked to fix.

### Three shapes, in order, each fixing the last

This module is one idea taught three times, because the first two shapes are
where the third one's syntax comes from:

| Step | Shape | What it fixes | What is still wrong |
|---|---|---|---|
| 1 | `req.on("end", () => send(…))` | nothing — the first thing that works | the body only exists inside a callback |
| 2 | `readBody(req).then((body) => …)` | collecting moves into a reusable function | still a callback, still cannot `return` |
| 3 | `const body = await readBody(req);` | the body is a value on a line | nothing. This is the one you keep |

You could be shown step 3 and nothing else. You would then have a piece of
syntax and no idea what it replaced, and `await` would look like magic instead
of what it is: a way of writing step 2 that reads top to bottom.

### What you get back is a string

Not an object. `readBody` hands you the characters the client sent, and if the
client sent JSON you have **text that looks like JSON**:

```
$ curl -s -X POST localhost:3000/echo -d '{"title":"Buy milk"}'
{"echo":"{\\"title\\":\\"Buy milk\\"}","length":20}
```

Look at the backslashes. That is `JSON.stringify` escaping a *string* that
happens to contain quotes — proof that nothing has parsed anything. Crossing
that gap is module 9, and it is one line.
"""

_M8_SYNTAX = [
    _syn(
        'req.setEncoding("utf8");',
        "Ask for the body as text. Call it **before** reading anything; from "
        "then on every chunk is a `string`.",
        """
req.setEncoding("utf8");
req.on("data", (chunk: string) => {
  // chunk is text. Without setEncoding it would be a Buffer.
});
""",
        "Skip it and the chunk is a Buffer. `\"\" + buffer` still produces "
        "something that looks right for plain ASCII, which is why this bug "
        "survives every test you write and dies on the first accented "
        "character that lands across a chunk boundary.",
    ),
    _syn(
        'req.on("data", (chunk: string) => { … })',
        "Register a listener for the next piece of the body. It fires **zero or "
        "more times** — once for a small body, many times for a large one, "
        "never for a request that has no body at all.",
        """
let body = "";
req.on("data", (chunk: string) => {
  body = body + chunk;      // accumulate. Never `body = chunk`.
});
""",
        "`req.on` returns immediately — it books a callback, it does not wait "
        "for one. Code written after this line runs *before* the first chunk.",
    ),
    _syn(
        'req.on("end", () => { … })',
        "Register a listener for \"the body is complete\". It fires exactly "
        "once, after the last `\"data\"`, and it is the only place the whole "
        "body exists.",
        """
req.on("end", () => {
  send(res, 200, { echo: body, length: body.length });
});
""",
        "`req.on(\"end\", …)` is the request finishing its way *in*. "
        "`res.end()` is the response finishing its way *out*. They are "
        "unrelated, they are one character apart, and mixing them up is a "
        "half-hour of confusion.",
    ),
    _syn(
        "new Promise<string>((resolve) => { … })",
        "A value that is not here yet, with the type it will have when it is. "
        "The function you pass runs immediately; calling `resolve(x)` is what "
        "says \"later has arrived, and it is `x`\".",
        """
function readBody(req: IncomingMessage): Promise<string> {
  return new Promise<string>((resolve) => {
    let body = "";
    req.on("data", (chunk: string) => { body = body + chunk; });
    req.on("end", () => { resolve(body); });   // ← the promise settles here
  });
}
""",
        "The type argument is not decoration. Write `new Promise((resolve) => …)` "
        "and TypeScript infers `Promise<unknown>`, and every use of the value "
        "downstream needs narrowing it should not need.",
    ),
    _syn(
        "readBody(req).then((body) => { … })",
        "Run a callback when the promise settles. The step-2 shape: better than "
        "raw events because the collecting is now a function you can reuse, and "
        "still a callback.",
        """
readBody(req).then((body) => {
  send(res, 200, { echo: body, length: body.length });
});
""",
        "You cannot `return` out of a `.then` callback into the function around "
        "it — the `return` belongs to the callback. That is precisely what "
        "breaks module 7's router, where every route ends in `return`.",
    ),
    _syn(
        "async function handler(req: IncomingMessage, res: ServerResponse): Promise<void>",
        "Mark a function as one that may wait. This is the price of `await`, "
        "and it is visible in the type: the function no longer returns `void`, "
        "it returns `Promise<void>`.",
        """
async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const body = await readBody(req);
  send(res, 200, { echo: body, length: body.length });
}
""",
        "`await` outside an `async` function is a syntax error, not a runtime "
        "one — so this is the rare mistake the compiler catches before you have "
        "finished typing it.",
    ),
    _syn(
        "const body = await readBody(req);",
        "Wait for the promise and unwrap it. `readBody(req)` is a "
        "`Promise<string>`; `await readBody(req)` is a `string`, on the "
        "following line, where the router can use it.",
        """
const body = await readBody(req);
send(res, 200, { echo: body, length: body.length });
""",
        "Forget the `await` and nothing complains: `body` is a promise, "
        "`JSON.stringify` turns it into `{}`, and the client gets "
        "`{\"echo\":{}}`. Learn that response on sight — it means a missing "
        "`await` and it means nothing else.",
    ),
    _syn(
        'const url = new URL(req.url ?? "/", "http://localhost");',
        "Module 6's parse, unchanged. The route still matches on "
        "`url.pathname`; only what happens *inside* a route is different today.",
        "",
        "",
        recap=True,
    ),
    _syn(
        "function send(res: ServerResponse, status: number, data: object): void { … }",
        "Module 5's helper. `{ echo: body }` is an object, so it goes through "
        "unchanged — but `body` on its own is a `string`, and `send` rejects it.",
        "",
        "That rejection is deliberate and it is module 5's decision earning its "
        "keep: an API that answers with a bare string has no room to add a "
        "field to the response later.",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — the events.
# ---------------------------------------------------------------------------

_M8_S1_FULL = _m8(_M8_SEND, """function handler(req: IncomingMessage, res: ServerResponse): void {
  req.setEncoding("utf8");
  let body = "";
  req.on("data", (chunk: string) => {
    body = body + chunk;
  });
  req.on("end", () => {
    send(res, 200, { echo: body, length: body.length });
  });
}
""")

_M8_S1 = _pstep(
    "stream", "The body is not there yet",
    "Headers now, body later — and the two events that deliver it.",
    """
Everything you have read off a request so far was already there. `req.method`
and `req.url` are strings sitting on the object the moment your handler is
called, because Node has read the request line and the headers before it calls
you.

It has not read the body. It deliberately has not read the body — a request can
carry four gigabytes, and a server that buffered all of it before letting you
look at the URL would be trivially easy to knock over. So the body is delivered
to you afterwards, in pieces, through two events:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  req.setEncoding("utf8");
  let body = "";

  req.on("data", (chunk: string) => {
    body = body + chunk;
  });

  req.on("end", () => {
    send(res, 200, { echo: body, length: body.length });
  });
}
```

That is a working handler. Type it, run it, `curl -X POST -d hello` at it, and
your body comes back. Then read the next three paragraphs, because the reason it
works is not the reason it looks like it works.

### `req.on` does not wait

`req.on("data", …)` **registers** a listener. It returns immediately — the
instant the two `req.on` calls are done, your handler is finished and Node goes
back to its event loop. The chunks arrive some time after that, and Node calls
your callbacks.

Which means the order things happen in is not the order they are written in:

```ts
req.on("data", (chunk: string) => { console.error("chunk:", chunk); });
req.on("end", () => { console.error("end"); });
console.error("handler finished");
```

prints `handler finished` **first**. That is not a quirk to memorise; it is the
whole reason the next two steps exist.

### Why `setEncoding("utf8")` comes first

Without it, a chunk is a `Buffer` — raw bytes. `"" + buffer` produces text
anyway, which is why skipping this line passes every test you would think to
write. It breaks when a multi-byte character (`é`, `→`, any emoji) is split
across two chunks: each half is decoded on its own and you get two replacement
characters where one letter should be.

Call `setEncoding("utf8")` before you read, and Node holds the incomplete
character back until the rest of it arrives. In this track the chunk is *typed*
`string` because of this call — so it is not just good practice, it is the thing
that makes the type true.

### `body = body + chunk`, always

`body = chunk` is right for every request you are going to test with, because
Node delivers a small body in a single chunk. It is wrong the first time
somebody posts something over about 64 KB, and then you have a bug that only
appears on large inputs, which is the worst kind.

Write the accumulation correctly now, while it costs you nothing.
""",
    """
```bash
$ curl -s -X POST localhost:3000/echo -d 'hello'
{"echo":"hello","length":5}

$ curl -s -X POST localhost:3000/echo -d ''
{"echo":"","length":0}

$ curl -s localhost:3000/anything
{"echo":"","length":0}
```

The second and third are worth checking as much as the first: a request with no
body does not hang and does not error. `"end"` fires immediately, `body` is
`""`, and you answer. A missing body is a real case, and today it is a boring
one.
""",
    pitfalls=[
        "Calling `send` after the two `req.on` lines rather than inside the `\"end\"` listener. The listeners are only registered at that point, so `body` is still `\"\"` — you answer instantly, correctly formatted, with nothing in it. This is the first graded fix.",
        "`body = chunk` instead of `body = body + chunk`. Correct output for every body small enough to arrive in one chunk, which is every body you will test with. It fails silently on the first large one.",
        "Skipping `setEncoding(\"utf8\")`. Chunks are Buffers, concatenation still produces something readable, and the bug waits for a multi-byte character split across a chunk boundary.",
        "Confusing `req.on(\"end\", …)` — the request has finished arriving — with `res.end()` — the response has finished going out. One character apart, opposite directions.",
        "Declaring `let body = \"\"` inside the `\"data\"` listener. It is reset on every chunk, so you keep only the last one — and again, with one chunk that is the whole body and the bug is invisible.",
        "Registering the listeners inside an `if` that does not always run, then answering outside it. Some requests then never get a response at all and simply hang.",
    ],
    warmup=[
        _pq("A handler registers a `\"data\"` listener that logs each chunk, then an "
            "`\"end\"` listener that logs `end`, then logs `handler finished` on the "
            "last line. What is printed first for a request with a body?",
            ["`handler finished` — `req.on` registers a callback and returns; nothing has arrived yet",
             "The first chunk, because `req.on(\"data\")` waits for one",
             "`end`, because it was registered last",
             "Nothing is printed until the body is complete"],
            0,
            "`req.on` books a callback and returns immediately. The handler runs to "
            "the end, Node goes back to its event loop, and only then do the chunks "
            "arrive. Everything in this module follows from that one fact."),
        _pq("A client sends a `GET` with no body at all. What happens to a handler "
            "that registers both listeners and answers inside `\"end\"`?",
            ["`\"end\"` fires immediately, `body` is `\"\"`, and the response goes out — no hang, no error",
             "`\"end\"` never fires, and the request hangs",
             "Node throws, because there is no body to read",
             "`\"data\"` fires once with an empty chunk, then `\"end\"`"],
            0,
            "No body means zero `\"data\"` events and one `\"end\"`. An empty body is "
            "an ordinary case, not a failure — which is why reading the body of a "
            "GET is harmless, even though it is pointless."),
    ],
    exercises=[
        _pex("todo-m8-stream-1", "Collect the chunks",
             "Register the listener that receives each piece of the body and adds "
             "it to `body`. The chunk is text — `setEncoding` above has seen to "
             "that — and there may be more than one of them.",
             _M8_S1_FULL,
             """  req.on("data", (chunk: string) => {
    body = body + chunk;
  });""",
             [("POST /echo hello\nPOST /echo hi\nGET /",
               '200 {"echo":"hello","length":5}'
               '\n200 {"echo":"hi","length":2}'
               '\n200 {"echo":"","length":0}')],
             ["`req.on(\"data\", …)` takes a callback that receives one chunk.",
              "The chunk is typed `string` because `setEncoding(\"utf8\")` was called above.",
              "Add to what you already have — `body = body + chunk` — rather than replacing it.",
              'req.on("data", (chunk: string) => { body = body + chunk; });']),
        _pex("todo-m8-stream-2", "Answer when it is complete",
             "The chunks are being collected. Now register the listener that fires "
             "once the body is complete, and answer from inside it with the echo "
             "and its length.",
             _M8_S1_FULL,
             """  req.on("end", () => {
    send(res, 200, { echo: body, length: body.length });
  });""",
             [("POST /echo hello\nPOST /echo there",
               '200 {"echo":"hello","length":5}'
               '\n200 {"echo":"there","length":5}')],
             ["The event is `\"end\"`, and its callback takes no arguments.",
              "This is the only place in the handler where `body` holds the whole body.",
              "The response object is `{ echo: body, length: body.length }`, in that key order.",
              'req.on("end", () => { send(res, 200, { echo: body, length: body.length }); });']),
        _pfix("todo-m8-stream-fix1", "The answer that arrives too early",
              "This handler collects the body correctly and still replies "
              "`{\"echo\":\"\",\"length\":0}` to everything — instantly, with a 200, "
              "looking for all the world like the client sent nothing.\n\n"
              "Nothing is missing. One thing is in the wrong place.",
              _m8(_M8_SEND, """function handler(req: IncomingMessage, res: ServerResponse): void {
  req.setEncoding("utf8");
  let body = "";
  req.on("data", (chunk: string) => {
    body = body + chunk;
  });
  send(res, 200, { echo: body, length: body.length });
}
"""),
              _M8_S1_FULL,
              [("POST /echo hello\nPOST /echo goodbye",
                '200 {"echo":"hello","length":5}'
                '\n200 {"echo":"goodbye","length":7}')],
              ["`req.on` registers a listener and returns. What is `body` on the very next line?",
               "The response is being sent while the body is still on its way.",
               "There is exactly one place in this handler where the whole body exists: inside a `\"end\"` listener that is not there yet.",
               "Wrap the `send` in `req.on(\"end\", () => { … });`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("How many times does the `\"data\"` listener fire?",
            ["Zero or more — once for a small body, many times for a large one, never for a request with no body",
             "Exactly once per request",
             "Once per header, then once for the body",
             "Exactly twice: the body and a terminator"],
            0,
            "That is why the accumulation has to be written as if there will be "
            "many, even though there will almost always be one on your machine."),
        _pq("What does `setEncoding(\"utf8\")` actually change?",
            ["Chunks arrive as `string` instead of `Buffer`, and a multi-byte character split across chunks is held back until it is whole",
             "It sets the `Content-Type` of the response",
             "It rejects requests that are not valid UTF-8",
             "Nothing at runtime; it is a type-level annotation"],
            0,
            "The second half is the part that matters. Byte-level concatenation "
            "looks fine until one character straddles two chunks — then each half "
            "is decoded separately and both are wrong."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — the promise.
# ---------------------------------------------------------------------------

_M8_S2_FULL = _m8(_M8_SEND, _M8_READBODY, """function handler(req: IncomingMessage, res: ServerResponse): void {
  readBody(req).then((body) => {
    send(res, 200, { echo: body, length: body.length });
  });
}
""")

_M8_S2 = _pstep(
    "promise", "A promise around the callbacks",
    "Get the collecting out of the handler — and see what a callback still costs you.",
    """
Step 1 works and it has already ruined your router.

Look at where the response is sent: inside the `"end"` callback. Every route
that needs the body would have to live in there too, which means module 7's flat
list of `if`s — each one ending in `return` — cannot be written at all. `return`
inside a callback returns from *the callback*.

What you want is for `readBody(req)` to be a thing you can call, that gives you
back the body. What is in the way is that the body does not exist yet, and a
function cannot return a value it does not have.

### A promise is exactly that missing piece

A `Promise<string>` is a value that says: *there will be a string here, later.*

```ts
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
```

Read it in two halves.

**The outside.** `readBody` returns a `Promise<string>` — immediately, on the
line you call it. Nothing waits.

**The inside.** The function you hand to `new Promise` runs straight away, and
its job is to register the same two listeners you wrote in step 1. The only new
line is `resolve(body)`, and `resolve` means *the promise you handed out a
moment ago now has this value in it*.

Everything about the events is unchanged. It has just been moved somewhere it
can be reused, and given a return type.

### Using it, the step-2 way

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  readBody(req).then((body) => {
    send(res, 200, { echo: body, length: body.length });
  });
}
```

`.then(cb)` says "run `cb` when the promise settles, with the value inside it".
This works. It is genuinely better than step 1: the stream handling is out of
the handler, `readBody` can be called from any route, and the type
`Promise<string>` documents what comes back.

### And it is still a callback

Count the improvements and then count what is left:

```ts
if (req.method === "POST" && url.pathname === "/echo") {
  readBody(req).then((body) => {
    send(res, 200, { echo: body, length: body.length });
    return;                     // ← returns from the callback. Not the handler.
  });
}
send(res, 404, { error: "not_found" });     // ← runs anyway. Every time.
```

That is a 404 sent on top of every successful echo. The fall-through you spent
module 7 getting right is now unavoidable, and the reason is structural: the
work happens inside a function, so the code around it cannot know when it is
done.

Step 3 fixes it, and the fix is one keyword.

### The type argument earns its place

`new Promise<string>` — not `new Promise`. Without it TypeScript has nothing to
infer from and gives you a promise of an unspecified value, which then needs
narrowing everywhere it is used. Say what the promise contains at the one place
you know it.
""",
    """
```bash
$ curl -s -X POST localhost:3000/echo -d 'hello'
{"echo":"hello","length":5}
```

Same output as step 1 — that is the point. Nothing the client can see has
changed. What changed is that `readBody` is now a function with a return type,
which is what makes step 3 possible. If your output moved, the move broke
something.
""",
    pitfalls=[
        "Calling `resolve` inside the `\"data\"` listener instead of `\"end\"`. It resolves on the first chunk — which for every body you can test with is the whole body, so the bug passes everything and truncates the first large request.",
        "Never calling `resolve` at all — a forgotten `\"end\"` listener, or a `resolve` inside an `if` that does not run. The promise never settles, the request hangs, and there is no error anywhere. This is module 4's missing `res.end()` wearing a different hat.",
        "`new Promise` without `<string>`. It compiles, and every use of the value downstream needs narrowing that the annotation would have made unnecessary.",
        "Trying to `return body` from inside the `\"end\"` listener. It returns from the listener, which nothing is looking at. `resolve` is how a value gets out of a callback.",
        "Calling `readBody(req)` twice on the same request. The stream was consumed by the first call, so the second registers listeners on something that has already ended — `\"end\"` never fires again and the promise never settles.",
        "`return` inside a `.then` callback. It returns from the callback; the function around it carries on to whatever is below, which in a router is the 404.",
    ],
    warmup=[
        _pq("`readBody(req)` is called. When does it return?",
            ["Immediately, with a promise that has nothing in it yet",
             "When the first chunk arrives",
             "When the body is complete, with the body",
             "It does not return; it blocks until `\"end\"` fires"],
            0,
            "That is what a promise is for. The function returns at once with a "
            "placeholder, and `resolve(body)` fills it in later. Nothing in "
            "JavaScript blocks waiting for I/O."),
    ],
    exercises=[
        _pex("todo-m8-promise-1", "Hand out the promise",
             "`readBody` has to return something on the line it is called, long "
             "before the body exists. Write the construction — with the type of "
             "the value it will eventually hold.",
             _M8_S2_FULL,
             "  return new Promise<string>((resolve) => {",
             [("POST /echo hello\nGET /",
               '200 {"echo":"hello","length":5}'
               '\n200 {"echo":"","length":0}')],
             ["`new Promise<T>(…)` takes one function, and hands it `resolve`.",
              "The eventual value is the body, and the body is a string.",
              "It is the return value of `readBody`, so it needs a `return`.",
              "`return new Promise<string>((resolve) => {`"]),
        _pex("todo-m8-promise-2", "Settle it",
             "The chunks are collected and the body is complete. Put the finished "
             "string into the promise that `readBody` handed out.",
             _M8_S2_FULL,
             "      resolve(body);",
             [("POST /echo hello\nPOST /echo abc",
               '200 {"echo":"hello","length":5}'
               '\n200 {"echo":"abc","length":3}')],
             ["`resolve(value)` is how a value escapes a callback.",
              "This belongs in the `\"end\"` listener — the one place the whole body exists.",
              "Resolving from the `\"data\"` listener would pass this test and lose everything after the first chunk.",
              "`resolve(body);`"]),
        _pch("todo-m8-promise-build", "Write readBody", "Medium",
             "Write the whole function.\n\n"
             "It takes the request, and returns a promise of the body as a string. "
             "Inside: ask for text, start with an empty string, add each chunk as "
             "it arrives, and settle the promise when the body is complete.\n\n"
             "Every line of it is step 1, plus one `resolve`.",
             _M8_S2_FULL,
             _M8_READBODY.rstrip("\n"),
             [("POST /echo hello\nPOST /echo a\nGET /health",
               '200 {"echo":"hello","length":5}'
               '\n200 {"echo":"a","length":1}'
               '\n200 {"echo":"","length":0}')],
             ["The signature is `function readBody(req: IncomingMessage): Promise<string>`.",
              "The body of it is `return new Promise<string>((resolve) => { … });`.",
              "Inside the promise: `req.setEncoding(\"utf8\")`, `let body = \"\"`, then the two listeners.",
              "`\"data\"` accumulates — `body = body + chunk` — and `\"end\"` calls `resolve(body)`.",
              "The third test has no body at all: zero `\"data\"` events, one `\"end\"`, and `resolve(\"\")`."]),
    ],
    quiz=[
        _pq("What is wrong with `readBody(req).then((body) => { send(res, 200, "
            "{ echo: body }); return; });` sitting above a fall-through 404 in "
            "module 7's router?",
            ["The `return` belongs to the callback, so the handler carries on and sends the 404 as well — on every successful request",
             "Nothing; `.then` is equivalent to `await` here",
             "`.then` runs before the body arrives",
             "The 404 is sent first, then the echo"],
            0,
            "The handler does not pause at `.then` — it registers a callback and "
            "runs to the bottom. The echo goes out later, on top of a 404 that has "
            "already gone. This is the structural problem `await` exists to solve."),
        _pq("Why does `resolve(body)` belong in the `\"end\"` listener rather than "
            "the `\"data\"` one?",
            ["`\"end\"` is the only point at which `body` holds the whole body — resolving on the first chunk truncates anything bigger than one chunk",
             "`\"data\"` cannot call `resolve`",
             "A promise can only be resolved from an event that fires once",
             "It does not matter; the last `resolve` wins"],
            0,
            "A promise settles once and ignores every later `resolve`, so resolving "
            "in `\"data\"` gives you the *first* chunk and silently drops the rest. "
            "With a small body those are the same string, which is what makes it "
            "such a durable bug."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — async / await.
# ---------------------------------------------------------------------------

_M8_S3_FULL = _m8(_M8_SEND, _M8_READBODY, """async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const body = await readBody(req);
  send(res, 200, { echo: body, length: body.length });
}
""")

_M8_S3 = _pstep(
    "await", "`async` and `await`",
    "The same promise, on a line, where the code around it can use the value.",
    """
Step 2 left you with a body you can only touch inside a callback. `await` takes
it out.

```ts
async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const body = await readBody(req);
  send(res, 200, { echo: body, length: body.length });
}
```

Two lines, both of them ordinary. `body` is a `string`. The next line uses it.
There is no callback, so there is nothing between you and a `return`.

### What `await` does

`readBody(req)` is a `Promise<string>`. `await readBody(req)` is a `string`.

That is the whole of it: `await` unwraps a promise into the value inside it, and
pauses **this function** until there is one. It is `.then` written so that the
rest of the function is the callback, rather than you having to write one.

```ts
readBody(req).then((body) => { send(res, 200, { echo: body }); });   // step 2
const body = await readBody(req);                                    // step 3
send(res, 200, { echo: body });
```

Identical behaviour. The second one can `return`, and the second one can sit in
the middle of a router.

### `async` is the price, and it is visible in the type

`await` is only legal inside a function marked `async`, and marking a function
`async` changes what it returns:

```
function  handler(…): void            →   async function handler(…): Promise<void>
```

Not `void` any more. A caller gets a promise back, and if the caller wants to
know when the handler finished, it has to look at it.

**Your caller already does.** Go and read the replayer at the bottom of the
program — the same one module 4 step 4 walked you through:

```ts
createServer((req, res) => {
  Promise.resolve(handler(req, res)).catch((err: unknown) => { … 500 … });
});
```

`Promise.resolve(x)` accepts either a promise or a plain value, which is why
that line has worked unchanged for modules 4 through 7 with a `void` handler and
works today with a `Promise<void>` one. And `.catch` is there because an `async`
function that throws does not throw at its caller — it returns a **rejected
promise**, and a rejected promise nobody looked at is an error that vanishes.
Writing that boundary yourself is module 16.

### Waiting is not blocking

Your handler pauses. Your server does not.

While one request is waiting for its body, Node is free to run anything else
that is ready — including the handler for a different request. That is the whole
argument for doing I/O this way, and it is why `await` costs you nothing except
having to say `async`.

### One `await` per thing you need

```ts
const body = await readBody(req);
```

Not two. Calling `readBody(req)` a second time on the same request registers
listeners on a stream that has already ended, so `"end"` never fires again and
that promise never settles. Read the body once, into a variable.
""",
    """
```bash
$ curl -s -X POST localhost:3000/echo -d 'hello'
{"echo":"hello","length":5}
```

Same answer for the third time, from a third shape. Now break it deliberately:
delete the word `await` and restart.

```bash
$ curl -s -X POST localhost:3000/echo -d 'hello'
{"echo":{},"length":undefined}
```

No error, no warning, a 200. Learn `{}` on sight — a promise where a value
should be is what it looks like from the outside.
""",
    pitfalls=[
        "Forgetting `await`. `body` is then a promise, `JSON.stringify` renders it as `{}`, and the client gets a cheerful 200 with `{\"echo\":{}}` in it. Nothing errors. This is the second graded fix.",
        "`await` in a function that is not marked `async`. A compile error rather than a runtime one — the one mistake in this module the tools catch for you.",
        "Leaving the handler's return type as `void` after adding `async`. An `async` function returns `Promise<void>`, and TypeScript will say so.",
        "Assuming `await` blocks the server. It suspends one handler; the process carries on serving everyone else.",
        "Calling `readBody(req)` twice for one request. The second call waits on a stream that has already ended, and hangs forever.",
        "`await`ing something that is not a promise. It is legal and does nothing useful — `await 5` is `5` — so a stray `await` on a plain value is invisible rather than an error.",
    ],
    warmup=[
        _pq("`readBody(req)` returns `Promise<string>`. What is the type of "
            "`await readBody(req)`?",
            ["`string` — `await` unwraps the promise into the value inside it",
             "`Promise<string>` — `await` only schedules it",
             "`void`",
             "`string | undefined`, because the body may not arrive"],
            0,
            "Unwrapping is the entire job. `Promise<T>` in, `T` out — and the "
            "function containing the `await` pauses until there is one."),
        _pq("A handler is marked `async` and its body contains no `await` at all. "
            "What is its return type?",
            ["`Promise<void>` — `async` changes the return type whether or not anything is awaited",
             "`void`, because nothing was awaited",
             "It is a compile error to mark a function `async` with no `await`",
             "`Promise<undefined>`"],
            0,
            "`async` is a promise on the way out, `await` is a promise on the way "
            "in, and they are independent. The keyword changes the signature by "
            "itself."),
    ],
    exercises=[
        _pex("todo-m8-await-1", "Mark it, and say what it returns",
             "This handler is about to `await`. Write its signature — the keyword "
             "that makes `await` legal, and the return type that keyword forces.",
             _M8_S3_FULL,
             "async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {",
             [("POST /echo hello\nGET /",
               '200 {"echo":"hello","length":5}'
               '\n200 {"echo":"","length":0}')],
             ["`await` is only legal inside a function marked one particular way.",
              "That keyword also changes what the function returns.",
              "`void` becomes `Promise<void>`; the parameters are unchanged.",
              "`async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {`"]),
        _pex("todo-m8-await-2", "Unwrap it",
             "Get the body out of the promise and into a `string` variable the next "
             "line can use.",
             _M8_S3_FULL,
             "  const body = await readBody(req);",
             [("POST /echo hello\nPOST /echo hey",
               '200 {"echo":"hello","length":5}'
               '\n200 {"echo":"hey","length":3}')],
             ["`readBody(req)` gives you a `Promise<string>`; you want the `string`.",
              "One keyword in front of the call does that.",
              "Read it once, into a `const` — a second call would wait on a stream that has already ended.",
              "`const body = await readBody(req);`"]),
        _pfix("todo-m8-await-fix1", "`{\"echo\":{}}`",
              "A 200, valid JSON, no error in the log — and the client gets "
              "`{\"echo\":{}}` no matter what it posts.\n\n"
              "That empty object is a specific symptom with exactly one cause. "
              "Find it. It is one word.",
              _m8(_M8_SEND, _M8_READBODY, """async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const body = readBody(req);
  send(res, 200, { echo: body });
}
"""),
              _m8(_M8_SEND, _M8_READBODY, """async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const body = await readBody(req);
  send(res, 200, { echo: body });
}
"""),
              [("POST /echo hello\nPOST /echo bye",
                '200 {"echo":"hello"}'
                '\n200 {"echo":"bye"}')],
              ["What type is `readBody(req)` before anything unwraps it?",
               "`JSON.stringify` of a promise is `{}` — a promise has no own enumerable properties.",
               "The function is already marked `async`, so the keyword you need is legal here.",
               "`const body = await readBody(req);`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does the given replayer wrap your handler in "
            "`Promise.resolve(handler(req, res)).catch(…)`?",
            ["`Promise.resolve` accepts a promise or a plain value, so it works for both handler shapes — and an `async` handler that throws rejects rather than throwing, so without `.catch` the error would vanish",
             "To make the handler run asynchronously",
             "To retry the request if the handler fails",
             "So that `await` is legal inside the handler"],
            0,
            "It is the reason that line has not changed since module 4, and the "
            "reason today's change to your handler's return type broke nothing. "
            "You write that boundary yourself in module 16."),
        _pq("A handler `await`s a body that takes two seconds to arrive. What is "
            "the server doing during those two seconds?",
            ["Serving other requests — one suspended handler does not stop the process",
             "Blocking; no other request is handled until this one finishes",
             "Spawning a thread for the waiting handler",
             "Polling the socket in a loop"],
            0,
            "`await` suspends one function and hands control back to the event "
            "loop. That is the whole argument for non-blocking I/O, and it is why "
            "one process can hold thousands of slow connections."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — back in the router.
# ---------------------------------------------------------------------------

_M8_S4_HANDLER = """async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "POST" && url.pathname === "/echo") {
    const body = await readBody(req);
    send(res, 200, { echo: body, length: body.length });
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""

# Order matters: `readBody` sits immediately above `handler` so the module build
# can blank the pair of them as one contiguous region.
_M8_S4_FULL = _m8(_M8_STORE, _M8_SEEDED, _M8_SEND, _M8_READBODY, _M8_S4_HANDLER)

_M8_S4 = _pstep(
    "route", "The body, inside a route",
    "Module 7's router, unchanged, plus one `await` in the one route that needs it.",
    """
Put it back where it belongs:

```ts
async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "POST" && url.pathname === "/echo") {
    const body = await readBody(req);
    send(res, 200, { echo: body, length: body.length });
    return;
  }

  send(res, 404, { error: "not_found" });
}
```

Compare it with the handler you finished module 7 with. The differences are:
`async` on the signature, `Promise<void>` as the return type, and four lines in
the middle. **The `GET /todos` route was not touched. The 404 was not touched.**

That is module 7's shape paying for itself for the first time: adding a route
that does something structurally new — waits — cost nothing anywhere else in the
router. A handler built as an `if / else if` chain would have needed rearranging
to fit a new branch in; this one needed an insertion point.

### Read the body inside the route, not at the top

You could `await readBody(req)` as the first line of the handler and have it
available everywhere. Do not.

A `GET` has no body, so awaiting one returns `""` immediately — it would work.
But every request would then pay for a read it does not need, and, worse, the
code would say something false: it would claim that reading the body is part of
routing. It is not. It is part of *this route*.

The rule is worth naming now, because it comes back twice: **do the work inside
the branch that needs it.** Module 17 does not parse query parameters for routes
that ignore them, and module 19 does not touch the disk for requests that only
read.

### What `/echo` is for

Nothing. It is scaffolding, and this is the only module it exists in.

`JSON.parse` belongs to module 9, so today there is exactly one honest thing to
do with a body you have read: hand it back and prove you have it. Module 9
deletes this route, keeps the `await readBody(req)` line verbatim, and feeds it
to a parser.

Meanwhile `/echo` is genuinely the best debugging tool in the project. When
module 14 starts rejecting bodies you are certain are correct, an endpoint that
tells you exactly what arrived is how you find out that curl ate your quotes.

### Look at what comes back

```bash
$ curl -s -X POST localhost:3000/echo -d '{"title":"Buy milk"}'
{"echo":"{\\"title\\":\\"Buy milk\\"}","length":20}
```

Those backslashes are the module's last lesson. You did not receive an object
with a `title` in it. You received **twenty characters of text** that happen to
be shaped like JSON, and `JSON.stringify` is escaping the quotes inside them
because as far as it is concerned this is a string like any other.

`body.title` does not exist. It would not compile if you tried, and that is the
type system telling you the truth: nothing has parsed anything yet.

One line closes that gap, and it is the first line of module 9.
""",
    """
```bash
$ curl -s localhost:3000/todos
[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]

$ curl -s -X POST localhost:3000/echo -d 'hello'
{"echo":"hello","length":5}

$ curl -s -i localhost:3000/echo
HTTP/1.1 404 Not Found
```

The third one is the check that matters: `/echo` is a `POST` route, so a `GET`
to the same path falls through to the 404 exactly as it did before you added it.
A route is still a verb *and* a path.
""",
    pitfalls=[
        "Reading the body at the top of the handler for every request. It works — a GET's body is `\"\"` — and it says something untrue about what routing is.",
        "Forgetting the `return` after the echo's `send`. The 404 below then runs on a response that has already gone; because the handler is `async`, the throw becomes a rejected promise rather than a crash, so it lands in the replayer's boundary and the client never sees it. Silent, and still wrong.",
        "Marking the handler `async` and leaving the return type `void`. The compiler catches it; the fix is `Promise<void>`.",
        "Putting the new route below the fall-through 404. It is unreachable, and the 404 has already answered by the time it runs.",
        "Expecting `body.title` to work. `body` is a `string`. Module 9 is where that changes, and it changes deliberately.",
        "Reaching for `JSON.parse` today. It is module 9's, and the point of stopping here is that reading a body and understanding one are two separate problems that fail in different ways.",
    ],
    warmup=[
        _pq("The echo route is added above the 404 and the `GET /todos` route is "
            "left exactly as it was. What had to change about `GET /todos`?",
            ["Nothing — it is synchronous, it sends and returns, and an `async` handler runs it identically",
             "It has to become `await send(res, 200, todos)`",
             "It has to move below the echo route",
             "It has to be wrapped in a promise so both routes have the same shape"],
            0,
            "An `async` function is an ordinary function until it hits an `await`. "
            "Routes that do not wait are unaffected, which is why this change was "
            "an insertion rather than a rewrite."),
    ],
    exercises=[
        _pex("todo-m8-route-1", "The route that waits",
             "Add the echo route to the router. It answers `POST /echo` with the "
             "body it was sent and that body's length — and, like every route "
             "before it, it stops there.",
             _M8_S4_FULL,
             """  if (req.method === "POST" && url.pathname === "/echo") {
    const body = await readBody(req);
    send(res, 200, { echo: body, length: body.length });
    return;
  }""",
             [("POST /echo hello\nGET /todos\nGET /echo\nPOST /nope hi",
               '200 {"echo":"hello","length":5}'
               '\n200 ' + _M8_LIST +
               '\n404 {"error":"not_found"}'
               '\n404 {"error":"not_found"}')],
             ["The condition is module 7's: a verb and a path, joined with `&&`.",
              "Inside it, `await readBody(req)` before you can answer with anything.",
              "The response object is `{ echo: body, length: body.length }`.",
              "It ends with `return;`, like every other route — there is a 404 below it.",
              "The third test is a `GET` to `/echo`: the path matches and the verb does not, so it must 404."]),
        _pch("todo-m8-route-build", "The whole router", "Medium",
             "Write the handler.\n\n"
             "Parse the target as module 6 did, then route:\n\n"
             "* `GET /todos` → `200` with the store's array\n"
             "* `POST /echo` → `200` with `{\"echo\":body,\"length\":n}`\n"
             "* anything else → `404` with `{\"error\":\"not_found\"}`\n\n"
             "One of those routes has to wait for something, which decides the "
             "handler's signature. `readBody`, `send` and the store are already "
             "written above.",
             _M8_S4_FULL,
             _M8_S4_HANDLER.rstrip("\n"),
             [("POST /echo hi\nGET /todos\nGET /\nDELETE /echo",
               '200 {"echo":"hi","length":2}'
               '\n200 ' + _M8_LIST +
               '\n404 {"error":"not_found"}'
               '\n404 {"error":"not_found"}')],
             ["The signature is `async` and returns `Promise<void>` — one route awaits.",
              "First line: `const url = new URL(req.url ?? \"/\", \"http://localhost\");`.",
              "Each route is `if (verb && path) { …; return; }`, and the 404 is the last statement, unconditional.",
              "The `GET /todos` route does not wait for anything and is unchanged from module 7.",
              "`await readBody(req)` goes inside the echo route, not at the top of the handler."]),
    ],
    quiz=[
        _pq("Why read the body inside the route rather than as the handler's first "
            "line?",
            ["Reading a body is what one route does, not what routing is — and routes that have no body should not pay for a read they ignore",
             "Because awaiting a body on a GET throws",
             "Because `await` is illegal before the first `if`",
             "It makes no difference at all; both are equally good"],
            0,
            "It would work — a GET's body is an immediate `\"\"`. The argument is "
            "about what the code claims, and the same argument decides where "
            "query parsing goes in module 17 and where disk reads go in module 19."),
        _pq("`POST /echo` with `{\"title\":\"Buy milk\"}` answers "
            "`{\"echo\":\"{\\\"title\\\":\\\"Buy milk\\\"}\",\"length\":20}`. What are "
            "the backslashes telling you?",
            ["That `body` is a string — `JSON.stringify` is escaping the quotes inside it, because nothing has parsed it",
             "That the client sent malformed JSON",
             "That `send` double-encodes objects",
             "That the body was truncated"],
            0,
            "You have twenty characters of text shaped like JSON, not an object. "
            "`body.title` does not exist and would not compile. Module 9 is one "
            "line, and it is that line."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M8_FINAL = _pch(
    "todo-m8-build", "Module 8 build — the server can read", "Medium",
    "Write both halves.\n\n"
    "**`readBody(req)`** — takes the request, returns a promise of the body as a "
    "string. Ask for text, accumulate the chunks, settle when the body is "
    "complete.\n\n"
    "**`handler(req, res)`** — parse the target, then route:\n\n"
    "* `GET /todos` → `200` with the store's array\n"
    "* `POST /echo` → `200` with `{\"echo\":body,\"length\":n}`\n"
    "* anything else, any verb → `404` with `{\"error\":\"not_found\"}`\n\n"
    "The third test posts something that looks like JSON. It comes back with its "
    "quotes escaped, because what you are holding is text — which is the whole "
    "point of stopping the module here.",
    _M8_S4_FULL,
    _M8_READBODY.rstrip("\n") + "\n\n" + _M8_S4_HANDLER.rstrip("\n"),
    [("POST /echo hello\nGET /todos\nPOST /echo {\"title\":\"Buy milk\"}\nGET /echo\nPOST /todos hi",
      '200 {"echo":"hello","length":5}'
      '\n200 ' + _M8_LIST +
      '\n200 {"echo":"{\\"title\\":\\"Buy milk\\"}","length":20}'
      '\n404 {"error":"not_found"}'
      '\n404 {"error":"not_found"}')],
    ["`readBody` returns `new Promise<string>((resolve) => { … })` and registers "
     "the two listeners inside it.",
     "`req.setEncoding(\"utf8\")` before anything, so the chunk really is a string.",
     "`\"data\"` accumulates with `body = body + chunk`; `\"end\"` calls `resolve(body)`.",
     "The handler is `async` and returns `Promise<void>`, because one of its "
     "routes awaits.",
     "Routes first, each `return`ing; the 404 last and unconditional.",
     "The fifth test is `POST /todos`, which no route claims yet — it 404s until "
     "module 9."],
)


_TODO_MODULES.append(_pmod(
    key="todo-body", number=8, phase="crud",
    title="Reading a request body",
    what="streams, promises and await — the body arrives in pieces",
    goal="Collect the body of a request and get it back as a string the router can use.",
    why=_M8_WHY,
    est_minutes=70,
    builds_on=["todo-server", "todo-json", "todo-url", "todo-routing"],
    concepts=["streams", "events", "setEncoding", "promises", "resolve",
              "async/await", "non-blocking I/O"],
    deliverable="A `readBody(req)` you will use in every remaining module that "
                "accepts input — and a handler that can wait.",
    objectives=[
        "Say why `req.body` does not exist, in terms of what Node has read when your handler is called",
        "Collect a body from `\"data\"` and `\"end\"`, and explain why `req.on` returning immediately is the source of both classic bugs",
        "Say what `setEncoding(\"utf8\")` changes and name the input that breaks without it",
        "Wrap the two listeners in a promise and explain what `resolve` does that `return` cannot",
        "Rewrite a `.then` callback as `await`, and say what `async` costs in the function's type",
        "Recognise `{\"echo\":{}}` as a missing `await` on sight",
        "Add a waiting route to module 7's router without touching any other route",
    ],
    endpoints=[
        _pep("POST", "/echo", "Hand back the body you were sent",
             "any text", '{"echo":"…","length":n}', "200"),
        # Word for word module 7's row: this module does not touch it, and the
        # Handbook's contract index reports a differing description as a change.
        _pep("GET", "/todos", "List every todo", "",
             "[Todo] — a bare array until module 18", "200"),
        # RETIREMENT. Module 7 added /health as its worked example of extending
        # the router, and this module's programs and reference do not carry it —
        # it is not part of the todo contract. Declared here, in the module that
        # dropped it, so the Handbook's contract index stops advertising it.
        _pep("GET", "/health", "Retired — module 7's example route; the builds from here on carry only the todo contract",
             "", "—", "—"),
        _pep("*", "anything else", "Fall through", "", '{"error":"not_found"}', "404"),
    ],
    brief=_M8_BRIEF,
    syntax=_M8_SYNTAX,
    steps=[_M8_S1, _M8_S2, _M8_S3, _M8_S4],
    final_build=_M8_FINAL,
    acceptance=[
        "`curl -s -X POST localhost:3000/echo -d 'hello'` returns `{\"echo\":\"hello\",\"length\":5}`.",
        "`curl -s -X POST localhost:3000/echo -d ''` returns `{\"echo\":\"\",\"length\":0}` rather than hanging.",
        "`curl -s -i localhost:3000/echo` returns 404 — the path matches and the verb does not.",
        "`curl -s localhost:3000/todos` still returns the list, unchanged from module 7.",
        "`readBody` calls `setEncoding(\"utf8\")` before reading, and accumulates with `body = body + chunk`.",
        "`resolve(body)` is inside the `\"end\"` listener, not the `\"data\"` one.",
        "The handler is `async` and declares `Promise<void>`; the `await` is inside the echo route, not at the top.",
        "Deleting the `await` gives you `{\"echo\":{}}` with a 200 — and you have seen it do that.",
    ],
    manual_test="""
With `node server.ts` running:

```bash
curl -s -X POST localhost:3000/echo -d 'hello'
curl -s -X POST localhost:3000/echo -d ''            # empty body — not an error
curl -s -X POST localhost:3000/echo -d '{"title":"Buy milk"}'   # look at the backslashes
curl -s localhost:3000/todos                          # unchanged from module 7
curl -s -i localhost:3000/echo                        # 404 — GET is not POST
```

Then break it three ways. Each one fails differently, and the difference is the
module:

```bash
# 1. move the `send` in readBody's "end" listener out of the listener, restart:
curl -s -X POST localhost:3000/echo -d 'hello'
#    → {"echo":"","length":0}, instantly. You answered before the body arrived.

# 2. put it back, delete the `await` in the echo route, restart:
curl -s -X POST localhost:3000/echo -d 'hello'
#    → {"echo":{}} with a 200. A promise where a string should be, and no error.

# 3. put it back, delete the `req.on("end", …)` listener entirely, restart:
curl -s -X POST localhost:3000/echo -d 'hello'
#    → hangs. Forever. Ctrl+C.
```

The third is the one to sit with. Nothing resolves the promise, so the `await`
never returns, so no response is ever written — and there is no error, no log
and no timeout. It is module 4's missing `res.end()` again, one layer further
down, and it is the failure mode of every promise you will ever write.

Then send it something big, which is the one thing the graded exercises cannot:

```bash
python -c "print('x' * 200000)" > big.txt
curl -s -X POST localhost:3000/echo --data-binary @big.txt | head -c 60
```

If your accumulation is `body = chunk` rather than `body = body + chunk`, that
is where it finally shows up — and now you know why the rule is written the way
it is.
""",
    reference="""// server.ts — module 8
//
// Phase 3 begins. The server could route a POST since module 7; it just had
// nothing to read. This module is the read.
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

// THE BODY READER. Every remaining module that accepts input calls this, and it
// never changes again — module 9 parses what it returns, module 13 stops
// trusting the result, module 14 validates it. None of them touch this.
//
// Why a promise at all: the two listeners below are the only way the body is
// delivered, and a value that arrives in a callback cannot be `return`ed. The
// promise is the box the value is put into so that `await` can take it out
// somewhere the router can use it.
function readBody(req: IncomingMessage): Promise<string> {
  return new Promise<string>((resolve) => {
    // BEFORE reading anything. Without it a chunk is a Buffer, concatenation
    // still produces readable text for ASCII, and the bug waits for a
    // multi-byte character split across two chunks.
    req.setEncoding("utf8");
    let body = "";

    // Fires zero or more times. `body = chunk` would pass every test on this
    // machine — Node delivers a small body in one chunk — and truncate the
    // first request over about 64 KB.
    req.on("data", (chunk: string) => {
      body = body + chunk;
    });

    // Fires exactly once, and is the only moment the whole body exists.
    // Resolving from the "data" listener instead settles the promise with the
    // FIRST chunk and silently drops the rest.
    //
    // If this listener is missing, nothing ever resolves: the await never
    // returns, no response is written, and the request hangs with no error
    // anywhere. That is this module's version of module 4's missing res.end().
    req.on("end", () => {
      resolve(body);
    });
  });
}

// `async` because one route waits, and therefore `Promise<void>` rather than
// `void`. The replayer at the bottom of every exercise has been ready for this
// since module 4: `Promise.resolve(handler(req, res)).catch(…)` accepts either
// shape, and the `.catch` is there because an async function that throws
// returns a rejected promise rather than throwing at its caller.
async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  // Unchanged from module 7. An async function is an ordinary function until it
  // reaches an await, so a route that does not wait is unaffected.
  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  // SCAFFOLDING, and the only module it exists in. JSON.parse is module 9's, so
  // the one honest thing to do with a body today is hand it back.
  //
  // The read is here rather than at the top of the handler on purpose: a GET has
  // no body, awaiting one returns "" immediately, and doing it anyway would
  // claim that reading input is part of routing. It is part of this route.
  if (req.method === "POST" && url.pathname === "/echo") {
    const body = await readBody(req);
    // `body` is a STRING. Post {"title":"x"} here and the quotes come back
    // escaped, because nothing has parsed anything. body.title does not exist
    // and does not compile. That gap is module 9, and it is one line.
    send(res, 200, { echo: body, length: body.length });
    return;
  }

  send(res, 404, { error: "not_found" });
}

// Still seeded, still deleted in module 9 — a POST that creates a todo is the
// next module, and these two lines come out the moment it lands.
addTodo("Buy milk");
addTodo("Write tests");

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Add `console.error(\"chunk\", chunk.length)` inside the `\"data\"` listener, then post a 200 KB file with `curl --data-binary @big.txt`. Count the chunks. That number is the reason the accumulation is written the way it is.",
        "Return the body's length in a header as well: `res.setHeader(\"X-Body-Length\", String(body.length))` before the `send`. Then check it with `curl -i` — and notice that no graded exercise in this track could have checked it, because the replayer prints no headers.",
        "Reject bodies over a size limit: count bytes in the `\"data\"` listener and resolve early with `\"\"` past 1 MB. Then work out what is still wrong with that (the client keeps sending, and you keep receiving) and look up `req.destroy()`.",
        "Rewrite `readBody` with `.then` instead of `await` in the handler, run the tests, then change it back. Reading the two side by side is the fastest way to see what `await` actually bought you.",
        "Add a second `await readBody(req)` in the echo route and watch the request hang forever. The stream was consumed by the first call; there is no second `\"end\"`.",
        "Make `readBody` resolve with the number of chunks as well as the body — `Promise<{ body: string; chunks: number }>` — and notice that the type argument is doing real work now.",
    ],
    glossary=[
        _pgloss("stream", "Data delivered in pieces over time rather than all at once. A request body is one; so is a file being read."),
        _pgloss("chunk", "One piece of a stream. For a small body there is exactly one, which is what hides half the bugs in this module."),
        _pgloss("event listener", "A function registered with `.on(name, fn)` to be called when something happens. Registering returns immediately."),
        _pgloss("setEncoding", "Ask a stream for text rather than bytes. Makes each chunk a `string`, and holds back a multi-byte character split across chunks."),
        _pgloss("promise", "A value that is not here yet, with the type it will have when it is. `Promise<string>` is \"a string, later\"."),
        _pgloss("resolve", "Put the value into a promise. How a result escapes a callback, since `return` inside one goes nowhere."),
        _pgloss("settle", "A promise going from pending to resolved or rejected. It happens once; later calls to `resolve` are ignored."),
        _pgloss("async", "Marks a function as one that may wait. Changes its return type from `T` to `Promise<T>`, whether or not it awaits anything."),
        _pgloss("await", "Unwrap a promise into its value, suspending this function until it settles. Legal only inside an `async` function."),
        _pgloss("non-blocking I/O", "Waiting for one thing without stopping everything else. An awaiting handler suspends; the process keeps serving."),
    ],
    cheatsheet="""
```ts
function readBody(req: IncomingMessage): Promise<string> {
  return new Promise<string>((resolve) => {
    req.setEncoding("utf8");                       // text, not Buffers — first
    let body = "";
    req.on("data", (chunk: string) => {
      body = body + chunk;                         // accumulate, never replace
    });
    req.on("end", () => {
      resolve(body);                               // the only place it is whole
    });
  });
}

async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "POST" && url.pathname === "/echo") {
    const body = await readBody(req);              // Promise<string> → string
    send(res, 200, { echo: body, length: body.length });
    return;
  }

  send(res, 404, { error: "not_found" });
}
```

**The three shapes, and why you keep the third**

| | Reads | Can `return` into the router |
|---|---|---|
| `req.on("end", () => send(…))` | inside out | no |
| `readBody(req).then((body) => …)` | inside out | no |
| `const body = await readBody(req);` | top to bottom | yes |

| Symptom | Cause |
|---|---|
| `{"echo":"","length":0}`, instantly | answered outside the `"end"` listener |
| `{"echo":{}}` with a 200 | missing `await` |
| the request hangs, no error | `resolve` never called — a missing `"end"` listener |
| correct until a large body, then truncated | `body = chunk` instead of `body = body + chunk` |
| garbled accented characters | no `setEncoding("utf8")` |
| `await` is a syntax error | the function is not marked `async` |

| Type | Is |
|---|---|
| `readBody(req)` | `Promise<string>` |
| `await readBody(req)` | `string` |
| `async function f(): Promise<void>` | a function that returns a promise |
""",
    self_check=[
        "Can you say why `req.body` does not exist, in terms of what Node has and has not read when it calls your handler?",
        "Can you explain why the line after `req.on(\"data\", …)` runs before the first chunk?",
        "Can you name the input that breaks a body reader with no `setEncoding(\"utf8\")`, and say why it survives every test you would write?",
        "Can you say what `resolve` does that `return` cannot, and why that is the reason promises exist?",
        "Can you rewrite a `.then` call as `await` and back, and say what `async` changed about the function's type?",
        "Can you name the symptom of a missing `await`, and the symptom of a promise that never resolves?",
        "Can you say why the body is read inside the route rather than at the top of the handler?",
        "Can you explain what the backslashes in `{\"echo\":\"{\\\"title\\\":\\\"Buy milk\\\"}\"}` prove?",
    ],
    review=[
        _pq("When Node calls your handler, what has it read from the request?",
            ["The request line and the headers — the body has not arrived and may never fully arrive",
             "Everything, including the body",
             "Only the method",
             "Nothing; the handler reads all of it"],
            0,
            "It has to call you early: the headers are how you decide whether you "
            "want the body, and a four-gigabyte upload is not something a server "
            "buffers before letting you look at the URL."),
        _pq("A body reader collects chunks and calls `resolve(body)` from inside "
            "the `\"data\"` listener. What is the symptom?",
            ["Nothing, until a body arrives in more than one chunk — then only the first chunk comes through",
             "The promise never settles and the request hangs",
             "A 500 on every POST",
             "The chunks arrive as Buffers"],
            0,
            "A promise settles once and ignores every later `resolve`. Small bodies "
            "arrive in one chunk, so the buggy version and the correct one are "
            "indistinguishable on anything you can conveniently test."),
        _pq("`const body = readBody(req);` — no `await`. What does the client get?",
            ["A 200 with `{\"echo\":{}}` — `JSON.stringify` of a promise is an empty object, and nothing errors",
             "A 500 from the replayer's error boundary",
             "A compile error",
             "The correct body; `await` is optional when the value is used immediately"],
            0,
            "That empty object is the signature of a missing `await` and it means "
            "nothing else. Recognising it on sight saves you the twenty minutes "
            "everyone spends the first time."),
        _pq("What does marking a function `async` change about its type?",
            ["Its return type becomes `Promise<T>` instead of `T`, whether or not it awaits anything",
             "Nothing; `async` is purely a runtime hint",
             "Its parameters become optional",
             "It can only be called from other `async` functions"],
            0,
            "Which is why the handler's annotation went from `void` to "
            "`Promise<void>` — and why the replayer's `Promise.resolve(…)` "
            "wrapper, written in module 4, needed no change today."),
        _pq("Why is `req.setEncoding(\"utf8\")` called before the listeners rather "
            "than after?",
            ["A listener registered first could receive a chunk before the encoding is set, and that chunk would be a Buffer",
             "It is required syntactically",
             "It has to be the first statement in the function",
             "Order does not matter at all"],
            0,
            "In practice nothing arrives during the same tick, so the order rarely "
            "bites — but \"set the mode before you start reading\" is the rule that "
            "is true regardless of scheduling, and it is free to follow."),
        _pq("Which route in module 8's handler had to change when the handler "
            "became `async`?",
            ["None of them — a route that does not await runs identically in an async function",
             "All of them; every `send` needs awaiting",
             "`GET /todos`, which must now return a promise",
             "The 404, which must move above the awaiting route"],
            0,
            "An `async` function is an ordinary function until it reaches an "
            "`await`. That is why adding a waiting route to module 7's flat router "
            "was an insertion rather than a rewrite."),
    ],
    milestone="Your server can read what a client sent it. Everything in phase 3 "
              "is built on that one line — module 9 parses it, module 11 applies "
              "it, module 13 stops trusting it — and `readBody` never changes "
              "again.",
))
