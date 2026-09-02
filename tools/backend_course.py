# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Backend Lab — build a CRUD HTTP API from scratch, one project at a time.
#
# exec()'d inside gen_seed.py's namespace; defines a single global
# `BACKEND_TRACK` (dict) which gen_seed writes to
# src-tauri/seeds/backend_course.json (served by the `backend_track` command).
# The file is also runnable on its own (`python tools/backend_course.py`) so the
# Node verifier can check every program without a full seed regeneration.
#
# WHY PROJECTS, NOT WEEKS: the TypeScript course is a time ladder. Backend work
# is learned by finishing servers, so this track is a BUILD ladder — seven
# projects, each a running program, each reopening the previous one's code to
# add the next layer (routing → CRUD → validation → persistence → query →
# auth → structure). Every project states what to do, in what order, and how to
# tell it worked.
#
# HARD DESIGN RULES
#   1. ZERO DEPENDENCIES. Node built-ins only (`node:http`, `node:fs`,
#      `node:crypto`). No Express, no npm install — the app is offline-first and
#      the judge runs a single file in a scratch directory with no node_modules.
#      Learning the raw `http` module first is also the point: Express only
#      makes sense once you know what it is hiding.
#   2. NOTHING BEFORE ITS PROJECT. A project may only use ideas introduced in it
#      or in an earlier one. `_lint_scope` at the bottom enforces this and FAILS
#      generation on violation.
#   3. EVERY PROGRAM IS DETERMINISTIC. Ids come from counters, not UUIDs; tokens
#      are `tok_1`, `tok_2`; nothing prints a timestamp or a hash. Each lesson
#      says plainly where the real world would use randomness instead.
#
# EXECUTION MODEL: exercises run through the same stdin/stdout judge as every
# other track (`node main.js`; Node detects ESM from the `import` syntax, so
# top-level `await` works). Each program boots a REAL server on port 0 and
# replays a request script read from stdin — see `_DRIVER`. stdin holds one
# request per line (`METHOD /path [@token] [json body]`) and each line prints
# `<status> <response body>`, so a routing bug surfaces as a wrong status code
# instead of a mystery. Every `solution` is proved end-to-end by
# tests/verify_backend_course.rs and tools/verify_backend.py.
#
# EXERCISE KINDS: "drill" (fill one ____ blank), "challenge" (write a whole
# region where you see ____), "fix" (a complete but buggy program to correct —
# no blank; starter=buggy, solution=fixed).
# ---------------------------------------------------------------------------

import json
import os


def _bp(src):
    """Normalize a triple-quoted program or Markdown block: drop the leading
    newline, guarantee exactly one trailing newline."""
    return src.lstrip("\n").rstrip() + "\n"


def _q(question, options, answer, explanation):
    return {"question": question, "options": options, "answer": answer,
            "explanation": explanation}


def _gloss(term, definition):
    return {"term": term, "def": definition}


def _ep(method, path, purpose, request, response, status):
    return {"method": method, "path": path, "purpose": purpose,
            "request": request, "response": response, "status": status}


# ---------------------------------------------------------------------------
# The request replayer appended to every HTTP exercise. It is given to the
# learner (never blanked) and is identical in all seven projects, so it becomes
# invisible after the first read: the only thing that changes is the handler
# above it.
# ---------------------------------------------------------------------------
_DRIVER = """
// ---- request replayer (given — don't edit) --------------------------------
// stdin:  one request per line —  METHOD /path [@token] [json body]
// stdout: one line per request —  <status> <response body>
// An error your handler throws becomes a 500 — exactly what a framework does.
const server = http.createServer((req, res) => {
  Promise.resolve(handler(req, res)).catch((err) => {
    console.error(err);
    if (res.headersSent) return res.end();
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end('{"error":"server_error"}');
  });
});
await new Promise((ok) => server.listen(0, "127.0.0.1", ok));
const base = `http://127.0.0.1:${server.address().port}`;
for (const line of fs.readFileSync(0, "utf8").split("\\n")) {
  const [method, path, ...rest] = line.trim().split(" ");
  if (!method) continue;
  const token = rest[0]?.startsWith("@") ? rest.shift().slice(1) : "";
  const body = rest.join(" ");
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(base + path, { method, headers, body: body || undefined });
  console.log(res.status, (await res.text()).trim());
}
server.close();
"""

_IMPORTS = 'import http from "node:http";\nimport fs from "node:fs";\n'


def _server(code, imports=_IMPORTS):
    """A complete judged program: imports, the learner's handler, the replayer."""
    return imports + "\n" + _bp(code) + "\n" + _bp(_DRIVER)


def _plain(code):
    """A judged program with no server — pure logic printed to stdout."""
    return _bp(code)


def _tests(pairs):
    return [{"input": i, "output": o} for (i, o) in pairs]


_IDS = set()


def _mk(eid, title, prompt, full, tests, hints, difficulty, kind, starter=None,
        blank=None):
    """Build an Exercise dict. Either `blank` (a unique substring of `full`
    replaced by ____ to form the starter) OR an explicit `starter` (for "fix")."""
    assert eid not in _IDS, f"duplicate backend exercise id: {eid}"
    _IDS.add(eid)
    if starter is None:
        assert blank is not None, f"{eid}: need blank or starter"
        assert full.count(blank) == 1, (
            f"{eid}: blank must appear exactly once in the solution "
            f"(found {full.count(blank)}): {blank[:60]!r}"
        )
        starter = full.replace(blank, "____", 1)
    else:
        assert starter != full, f"{eid}: starter equals solution"
    assert starter != full, f"{eid}: no blank applied"
    assert tests, f"{eid}: needs at least one test"
    hints = list(hints or [])
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "",
        "hints": hints, "language": "javascript",
        "kind": kind, "difficulty": difficulty,
        "starter": starter, "solution": full, "tests": _tests(tests),
        "source_slug": "", "dataset": "",
    }


def _ex(eid, title, prompt, full, blank, tests, hints=(), difficulty="Intro"):
    return _mk(eid, title, prompt, full, tests, hints, difficulty, "drill", blank=blank)


def _ch(eid, title, difficulty, prompt, full, blank, tests, hints=()):
    return _mk(eid, title, prompt, full, tests, hints, difficulty, "challenge", blank=blank)


def _fix(eid, title, prompt, buggy, fixed, tests, hints=(), difficulty="Easy"):
    return _mk(eid, title, prompt, fixed, tests, hints, difficulty, "fix", starter=buggy)


def _step(key, title, what, instructions, checkpoint, pitfalls=(), warmup=(),
          exercises=(), quiz=()):
    return {
        "key": key, "title": title, "what": what,
        "instructions": _bp(instructions) if instructions else "",
        "checkpoint": _bp(checkpoint) if checkpoint else "",
        "pitfalls": list(pitfalls), "warmup": list(warmup),
        "exercises": list(exercises), "quiz": list(quiz),
    }


def _project(key, number, title, tagline, level, goal, why, est_minutes,
             builds_on, concepts, objectives, brief, endpoints, setup, steps,
             final_build=None, acceptance=(), manual_test="", reference="",
             stretch=(), glossary=(), cheatsheet="", self_check=(), review=(),
             milestone="", authored=True):
    return {
        "key": key, "number": number, "title": title, "tagline": tagline,
        "level": level, "goal": goal, "why": why, "authored": authored,
        "est_minutes": est_minutes, "builds_on": list(builds_on),
        "concepts": list(concepts), "objectives": list(objectives),
        "brief": _bp(brief) if brief else "",
        "endpoints": list(endpoints),
        "setup": _bp(setup) if setup else "",
        "steps": list(steps), "final_build": final_build,
        "acceptance": list(acceptance),
        "manual_test": _bp(manual_test) if manual_test else "",
        "reference": _bp(reference) if reference else "",
        "stretch": list(stretch), "glossary": list(glossary),
        "cheatsheet": _bp(cheatsheet) if cheatsheet else "",
        "self_check": list(self_check), "review": list(review),
        "milestone": milestone,
    }


def _skel(key, number, title, tagline, level, goal, why=""):
    return _project(key, number, title, tagline, level, goal, why, 0, [], [], [],
                    "", [], "", [], authored=False)


# The `send` helper every project uses. Introduced in project 1, step 2 and
# never re-explained — it is the single place a status code and a JSON body
# meet, which is exactly the habit this track is trying to build.
_SEND = """
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}
"""

# Reading a request body is a stream, so it is a promise. Introduced in
# project 2, step 2.
_READ_BODY = """
function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}
"""

_PROJECTS = []


# ===========================================================================
# PROJECT 1 — Your First HTTP Server
# ===========================================================================

_P1_S1 = _step(
    "what-is-a-server",
    "What a server actually is",
    "A program that listens on a port and answers requests. That's the whole idea.",
    """
A web server is not a mysterious thing. It is **a program that never exits**.
It waits on a port, and every time a request arrives it runs a function you
wrote and sends back some bytes. That function is the entire job.

### Do this

1. Make a folder for the project and open a terminal in it:

   ```
   mkdir notes-api
   cd notes-api
   ```

   There is no `npm install` in this whole track. Node already ships everything
   you need.

2. Create a file called `server.js` with exactly this:

   ```js
   import http from "node:http";

   function handler(req, res) {
     res.writeHead(200, { "Content-Type": "text/plain" });
     res.end("pong");
   }

   const server = http.createServer(handler);
   server.listen(3000, () => console.log("listening on http://localhost:3000"));
   ```

3. Run it:

   ```
   node server.js
   ```

   The terminal prints `listening on http://localhost:3000` **and then hangs**.
   That hang is not a bug — it is the server waiting. A web server that exits is
   a broken web server.

4. Open <http://localhost:3000> in a browser. You should see `pong`. Try
   <http://localhost:3000/anything> too — also `pong`, because your handler
   ignores the path so far.

5. Stop the server with `Ctrl+C`.

### What each piece means

| Piece | What it is |
| --- | --- |
| `http.createServer(handler)` | Builds a server. Nothing is listening yet. |
| `server.listen(3000)` | Claims port 3000 and starts accepting connections. |
| `handler(req, res)` | Runs **once per request**. |
| `req` | What the client sent: `req.method`, `req.url`, `req.headers`. |
| `res` | The reply you are writing. Nothing is sent until you call `res.end()`. |
| `res.writeHead(status, headers)` | Sets the status line and headers. Must come **before** `res.end()`. |
| `res.end(body)` | Sends the body and closes the response. |

### One rule that will save you an hour

**Every request must end in exactly one `res.end()`.** Call it zero times and
the browser spins forever waiting for a reply that never comes. Call it twice
and Node throws `ERR_STREAM_WRITE_AFTER_END`. When a request hangs, the first
thing to look for is a branch of your handler that forgot to reply.

Add a `console.log(req.method, req.url)` as the first line of your handler and
refresh the browser. You will usually see **two** lines — the page and the
browser asking for `/favicon.ico`. Your server answers every request, including
the ones you did not mean to make.
""",
    """
- `node server.js` prints the listening line and does not return to the prompt.
- <http://localhost:3000> shows `pong` in the browser.
- Your terminal logs the method and path of each request.
- `Ctrl+C` stops it, and the port is free again.
""",
    pitfalls=[
        "`EADDRINUSE` means something is already on port 3000 — usually a server you forgot to Ctrl+C in another terminal. Change the port or stop the old one.",
        "Editing server.js while it runs changes nothing: Node read the file once at startup. Stop it and start it again after every edit.",
        "A browser can only send GET requests from the address bar. You cannot test POST by typing a URL.",
    ],
    warmup=[
        _q("Your handler is `res.writeHead(200); res.end(\"pong\");`. You request `POST /notes/17`. What comes back?",
           ["404, because /notes/17 has no route", "200 with the body `pong`",
            "405, because POST is not allowed", "Nothing — POST needs a body"],
           1,
           "The handler never looks at req.method or req.url, so every request takes the same path and gets the same answer. Routing is something you write; it is not automatic."),
    ],
    exercises=[
        _ex("be1-pong", "Answer every request",
            "Send back the plain text `pong` for any request that arrives.",
            _server("""
function handler(req, res) {
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("pong");
}
"""),
            '  res.end("pong");',
            [("GET /ping", "200 pong"),
             ("GET /anything\nPOST /somewhere/else", "200 pong\n200 pong")],
            hints=["`res.end(body)` sends the body and closes the response.",
                   "The body has to be a string here, so pass the text in quotes.",
                   "`res.end(\"pong\");`"]),
    ],
    quiz=[
        _q("Why does `node server.js` not return you to the shell prompt?",
           ["The file has a syntax error", "Node is still compiling",
            "The server is listening — a server that exits cannot answer requests",
            "It is waiting for you to type a request"],
           2,
           "`listen()` keeps the process alive on purpose. The 'hang' IS the server running."),
        _q("What happens if a branch of your handler never calls `res.end()`?",
           ["Node sends an empty 200 automatically", "The client waits until it times out",
            "Node throws immediately", "The next request gets that response"],
           1,
           "Nothing is sent until you end the response, so the client just waits. A hanging request almost always means a branch with no reply."),
    ],
)

_P1_S2 = _step(
    "status-and-json",
    "Status codes and JSON bodies",
    "The status code is the answer; the body is the detail.",
    """
`pong` is fine for a heartbeat, but an API talks in **JSON**, and every reply
carries a **status code** that says how it went before the client reads a single
byte of the body.

### The five families

| Range | Meaning | You will use |
| --- | --- | --- |
| 1xx | informational | almost never |
| 2xx | it worked | `200 OK`, `201 Created`, `204 No Content` |
| 3xx | look elsewhere | redirects |
| 4xx | **the client got it wrong** | `400`, `401`, `403`, `404`, `409` |
| 5xx | **the server got it wrong** | `500` |

The 4xx/5xx split is the one that matters. A 4xx says *"you sent me something I
can't work with — change your request"*. A 5xx says *"your request was fine, I
broke"*. Returning 500 for a missing note is a lie that will send some future
person hunting through server logs for a bug that does not exist.

### Do this

1. Add a `send` helper at the top of `server.js`. Every reply in this whole
   track goes through it:

   ```js
   function send(res, status, data) {
     res.writeHead(status, { "Content-Type": "application/json" });
     res.end(data === null ? "" : JSON.stringify(data));
   }
   ```

   Two things happen here, and both are required:

   - `Content-Type: application/json` tells the client how to read the bytes.
     Without it, browsers and `fetch` treat your JSON as plain text.
   - `JSON.stringify(data)` turns your object into a string. `res.end()` only
     accepts a string or a Buffer — hand it an object and Node throws.

2. Rewrite the handler to answer `/health` with JSON and everything else with a
   404:

   ```js
   function handler(req, res) {
     if (req.url === "/health") return send(res, 200, { status: "ok" });
     send(res, 404, { error: "not_found" });
   }
   ```

3. Restart and check both paths:

   ```
   curl -i http://localhost:3000/health
   curl -i http://localhost:3000/nope
   ```

   `-i` prints the status line and headers, which is the whole point here. Look
   for `HTTP/1.1 200 OK` on the first and `HTTP/1.1 404 Not Found` on the second.

### Why `return send(...)`

`send` does not stop your handler — `return` does. Without the `return`, the
`/health` branch falls through and the 404 line runs too, giving you a double
reply and a crash. Getting into the habit of writing `return send(...)` for
every terminal branch removes an entire category of bug.
""",
    """
- `curl -i http://localhost:3000/health` shows `HTTP/1.1 200 OK`,
  `Content-Type: application/json`, and the body `{"status":"ok"}`.
- `curl -i http://localhost:3000/nope` shows `HTTP/1.1 404 Not Found`.
- No branch of the handler replies twice.
""",
    pitfalls=[
        "`res.end(obj)` throws — `res.end()` takes a string or a Buffer, never an object. Always `JSON.stringify` first.",
        "Forgetting `return` in front of `send(...)` makes the handler fall through and reply twice.",
        "A 404 with a 200 status code is worse than useless: clients check the status, not your prose.",
    ],
    warmup=[
        _q("A client asks for a note that does not exist. Which status is right?",
           ["500 Internal Server Error", "400 Bad Request",
            "404 Not Found", "204 No Content"],
           2,
           "The request was well-formed; the resource simply isn't there — that is exactly 404. 500 would falsely blame your server, and 400 would falsely blame the request's syntax."),
    ],
    exercises=[
        _ex("be1-json-health", "Send JSON, not a string",
            "Finish `send` so the body goes out as JSON text.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req, res) {
  send(res, 200, { status: "ok" });
}
"""),
            "JSON.stringify(data)",
            [("GET /health", '200 {"status":"ok"}'),
             ("GET /a\nGET /b", '200 {"status":"ok"}\n200 {"status":"ok"}')],
            hints=["`res.end()` will not accept a plain object.",
                   "There is a built-in that turns an object into JSON text.",
                   "`JSON.stringify(data)`"]),
        _fix("be1-not-found", "The lying status code",
             "This server answers unknown paths with a body that says `not_found` — but a status code that says everything is fine. Fix the status.",
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req, res) {
  if (req.url === "/health") return send(res, 200, { status: "ok" });
  send(res, 200, { error: "not_found" });
}
"""),
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req, res) {
  if (req.url === "/health") return send(res, 200, { status: "ok" });
  send(res, 404, { error: "not_found" });
}
"""),
             [("GET /health\nGET /nope", '200 {"status":"ok"}\n404 {"error":"not_found"}'),
              ("GET /notes\nGET /health", '404 {"error":"not_found"}\n200 {"status":"ok"}')],
             hints=["The body is already right. Read the status codes.",
                    "Which family does 'the thing you asked for does not exist' belong to?",
                    "The fall-through line should send 404, not 200."]),
    ],
    quiz=[
        _q("What does `Content-Type: application/json` actually change?",
           ["It validates that your body is valid JSON",
            "It tells the client how to interpret the bytes you sent",
            "It makes JSON.stringify unnecessary",
            "It compresses the response"],
           1,
           "The header is a label, not a checker. You can send garbage with a JSON content type — the header only tells the client how to read it."),
        _q("Your database is down and a request fails because of it. Which status?",
           ["400, the request could not be fulfilled", "404, the data isn't there",
            "500, the failure is on your side", "204, there is nothing to return"],
           2,
           "The client did nothing wrong, so it is a 5xx. The 4xx/5xx line is about WHO must change something for the request to succeed."),
    ],
)

_P1_S3 = _step(
    "routing",
    "Routing on method and path",
    "One handler, many endpoints — and the difference between 404 and 405.",
    """
Right now your handler branches on `req.url` alone. A real endpoint is a
**pair**: a method *and* a path. `GET /notes` (list them) and `POST /notes`
(create one) are different operations that happen to share a path.

### Do this

1. Add a `/version` endpoint alongside `/health`, and make both refuse
   non-GET requests:

   ```js
   function handler(req, res) {
     if (req.url === "/health") {
       if (req.method !== "GET") return send(res, 405, { error: "method_not_allowed" });
       return send(res, 200, { status: "ok" });
     }
     if (req.url === "/version") {
       if (req.method !== "GET") return send(res, 405, { error: "method_not_allowed" });
       return send(res, 200, { version: "1.0.0" });
     }
     send(res, 404, { error: "not_found" });
   }
   ```

2. Test all four cases — the two happy paths and the two failures:

   ```
   curl -i http://localhost:3000/health
   curl -i http://localhost:3000/version
   curl -i -X POST http://localhost:3000/health
   curl -i http://localhost:3000/nope
   ```

### 404 versus 405

These are easy to confuse and the distinction is genuinely useful:

- **404 Not Found** — *this path does not exist here.* `/helth` is a typo.
- **405 Method Not Allowed** — *this path exists, but not with that verb.*
  `POST /health` is a misunderstanding, not a typo.

A client that gets 405 learns something ("I used the wrong verb"). A client
that gets 404 for the same mistake goes looking for a missing route. Checking
the path first, then the method, is what makes the difference expressible.

### The shape to notice

Look at the structure: **match the path, then match the method, then act.** That
nesting is the seed of a router. In project 7 you will pull it out into a real
routing table with path parameters; for now, writing it by hand is what makes
the eventual abstraction feel like a relief rather than magic.
""",
    """
- `GET /health` → 200, `GET /version` → 200 with `{"version":"1.0.0"}`.
- `POST /health` → 405, not 404 and not 200.
- `GET /nope` → 404.
""",
    pitfalls=[
        "Checking the method before the path makes 405 impossible to express — you cannot say 'wrong verb for this path' if you never matched the path.",
        "`req.url` includes the query string, so `/health?x=1` will not equal `/health`. The next step fixes this properly.",
    ],
    exercises=[
        _ch("be1-route-table", "Two endpoints and two ways to be wrong", "Easy",
            "Write the routing. `GET /health` → 200 `{\"status\":\"ok\"}`. `GET /version` → 200 `{\"version\":\"1.0.0\"}`. Either path with any other method → 405 `{\"error\":\"method_not_allowed\"}`. Any other path → 404 `{\"error\":\"not_found\"}`.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req, res) {
  if (req.url === "/health") {
    if (req.method !== "GET") return send(res, 405, { error: "method_not_allowed" });
    return send(res, 200, { status: "ok" });
  }
  if (req.url === "/version") {
    if (req.method !== "GET") return send(res, 405, { error: "method_not_allowed" });
    return send(res, 200, { version: "1.0.0" });
  }
  send(res, 404, { error: "not_found" });
}
"""),
            """  if (req.url === "/health") {
    if (req.method !== "GET") return send(res, 405, { error: "method_not_allowed" });
    return send(res, 200, { status: "ok" });
  }
  if (req.url === "/version") {
    if (req.method !== "GET") return send(res, 405, { error: "method_not_allowed" });
    return send(res, 200, { version: "1.0.0" });
  }
  send(res, 404, { error: "not_found" });""",
            [("GET /health\nGET /version\nPOST /health\nGET /nope",
              '200 {"status":"ok"}\n200 {"version":"1.0.0"}\n405 {"error":"method_not_allowed"}\n404 {"error":"not_found"}'),
             ("DELETE /version\nPOST /nope\nGET /health",
              '405 {"error":"method_not_allowed"}\n404 {"error":"not_found"}\n200 {"status":"ok"}')],
            hints=["Match the path first, then the method inside it.",
                   "`return send(...)` on every branch that finishes the request.",
                   "The final line — reached only when no path matched — is the 404."]),
    ],
    quiz=[
        _q("`POST /health` on a server where /health only supports GET. Best status?",
           ["404 Not Found", "400 Bad Request",
            "405 Method Not Allowed", "501 Not Implemented"],
           2,
           "The path exists; the verb is wrong. 405 tells the client exactly that, which 404 cannot."),
        _q("Why match the path BEFORE the method?",
           ["It is faster", "Methods are case-sensitive",
            "Because 405 means 'this path exists with another verb' — you must match the path to know that",
            "Node requires that order"],
           2,
           "The order encodes the meaning. Method-first collapses 'unknown path' and 'wrong verb' into one indistinguishable case."),
    ],
)

_P1_S4 = _step(
    "query-strings",
    "Query strings and input you did not write",
    "The first data a stranger controls — parse it deliberately.",
    """
`req.url` is a raw string like `/echo?msg=hi`. Comparing it with `===` breaks
the moment anyone adds a query parameter. Parse it properly instead.

### Do this

1. Split path from query with the built-in `URL` class:

   ```js
   const url = new URL(req.url, "http://localhost");
   url.pathname;                    // "/echo"
   url.searchParams.get("msg");     // "hi", or null if absent
   ```

   `req.url` is only the part after the host (`/echo?msg=hi`), and `new URL()`
   needs an absolute URL — hence the throwaway `"http://localhost"` base. It is
   never used for anything; it just satisfies the parser.

2. Add an `/echo` endpoint that requires a `msg` parameter:

   ```js
   if (url.pathname === "/echo") {
     const msg = url.searchParams.get("msg");
     if (msg === null) return send(res, 400, { error: "missing_msg" });
     return send(res, 200, { msg });
   }
   ```

3. Change every other `req.url ===` comparison to `url.pathname ===` so that
   `/health?x=1` still works.

4. Try it:

   ```
   curl "http://localhost:3000/echo?msg=hi"
   curl "http://localhost:3000/echo"
   ```

   Quote the URL in the shell — an unquoted `&` puts your curl in the background.

### Three things about query values that bite

- **Everything is a string.** `?limit=10` gives you `"10"`, not `10`. And
  `?done=false` gives you the string `"false"`, which is *truthy*. Writing
  `if (url.searchParams.get("done"))` treats `?done=false` as true. You will do
  this once and remember it forever.
- **Missing and empty are different.** `.get("msg")` returns `null` when the
  parameter is absent and `""` when it is present but empty (`?msg=`). Compare
  against `null` explicitly, not with `if (!msg)`.
- **It is untrusted input.** A query string is typed by a stranger. Everything
  from here on assumes exactly that.
""",
    """
- `GET /echo?msg=hi` → 200 `{"msg":"hi"}`.
- `GET /echo` (no parameter) → 400 `{"error":"missing_msg"}`.
- `GET /health?debug=1` still returns 200, not 404.
""",
    pitfalls=[
        "`new URL(req.url)` alone throws — req.url is relative, so it needs the second base argument.",
        "`if (!value)` treats a legitimately empty or `\"0\"` value as missing. Compare with `null` when you mean absent.",
        "Every query value is a string. `\"false\"`, `\"0\"` and `\"\"` all need converting on purpose.",
    ],
    warmup=[
        _q("`url.searchParams.get(\"done\")` on the request `GET /notes?done=false`. What is the value, and is it truthy?",
           ["The boolean false; falsy", "The string \"false\"; truthy",
            "null; falsy", "The string \"false\"; falsy"],
           1,
           "Query parameters are always strings, and every non-empty string is truthy. `if (get(\"done\"))` is therefore true for ?done=false — a classic filter bug."),
    ],
    exercises=[
        _ch("be1-echo", "Echo a query parameter", "Easy",
            "Write the handler. `GET /echo?msg=hi` → 200 `{\"msg\":\"hi\"}`. `GET /echo` with no `msg` → 400 `{\"error\":\"missing_msg\"}`. Any other path → 404 `{\"error\":\"not_found\"}`.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  if (url.pathname !== "/echo") return send(res, 404, { error: "not_found" });
  const msg = url.searchParams.get("msg");
  if (msg === null) return send(res, 400, { error: "missing_msg" });
  send(res, 200, { msg });
}
"""),
            """  const url = new URL(req.url, "http://localhost");
  if (url.pathname !== "/echo") return send(res, 404, { error: "not_found" });
  const msg = url.searchParams.get("msg");
  if (msg === null) return send(res, 400, { error: "missing_msg" });
  send(res, 200, { msg });""",
            [("GET /echo?msg=hi\nGET /echo\nGET /other",
              '200 {"msg":"hi"}\n400 {"error":"missing_msg"}\n404 {"error":"not_found"}'),
             ("GET /echo?msg=\nGET /echo?msg=hello&extra=1",
              '200 {"msg":""}\n200 {"msg":"hello"}')],
            hints=["Parse with `new URL(req.url, \"http://localhost\")` and branch on `url.pathname`.",
                   "`searchParams.get` returns null when the parameter is absent — but \"\" when it is present and empty. The second test case checks you kept those apart.",
                   "`{ msg }` is shorthand for `{ msg: msg }`."]),
    ],
    quiz=[
        _q("Why pass `\"http://localhost\"` as the second argument to `new URL(req.url, ...)`?",
           ["To make the server listen there", "Because req.url is relative and URL needs an absolute one",
            "To allow cross-origin requests", "It sets the Host header"],
           1,
           "req.url is only the path and query. The base is a parsing formality and is discarded."),
        _q("`?msg=` versus no `msg` at all. What does `searchParams.get(\"msg\")` return?",
           ["\"\" and \"\"", "null and null", "\"\" and null", "undefined and null"],
           2,
           "Present-but-empty gives the empty string; absent gives null. `if (!msg)` cannot tell them apart, which matters as soon as empty is a legal value."),
    ],
)

_P1_FINAL = _ch(
    "be1-final", "The whole Project 1 server", "Easy",
    "Build the whole Project 1 server. `GET /health` → 200 `{\"status\":\"ok\"}`. `GET /version` → 200 `{\"version\":\"1.0.0\"}`. `GET /echo?msg=hi` → 200 `{\"msg\":\"hi\"}`, and 400 `{\"error\":\"missing_msg\"}` when `msg` is absent. A known path with the wrong method → 405 `{\"error\":\"method_not_allowed\"}`. Anything else → 404 `{\"error\":\"not_found\"}`. Query strings must not break path matching.",
    _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  const path = url.pathname;

  if (path !== "/health" && path !== "/version" && path !== "/echo") {
    return send(res, 404, { error: "not_found" });
  }
  if (req.method !== "GET") {
    return send(res, 405, { error: "method_not_allowed" });
  }
  if (path === "/health") return send(res, 200, { status: "ok" });
  if (path === "/version") return send(res, 200, { version: "1.0.0" });

  const msg = url.searchParams.get("msg");
  if (msg === null) return send(res, 400, { error: "missing_msg" });
  send(res, 200, { msg });
}
"""),
    """  const url = new URL(req.url, "http://localhost");
  const path = url.pathname;

  if (path !== "/health" && path !== "/version" && path !== "/echo") {
    return send(res, 404, { error: "not_found" });
  }
  if (req.method !== "GET") {
    return send(res, 405, { error: "method_not_allowed" });
  }
  if (path === "/health") return send(res, 200, { status: "ok" });
  if (path === "/version") return send(res, 200, { version: "1.0.0" });

  const msg = url.searchParams.get("msg");
  if (msg === null) return send(res, 400, { error: "missing_msg" });
  send(res, 200, { msg });""",
    [("GET /health\nGET /version\nGET /echo?msg=hi",
      '200 {"status":"ok"}\n200 {"version":"1.0.0"}\n200 {"msg":"hi"}'),
     ("GET /echo\nPOST /health\nGET /nope\nDELETE /echo?msg=hi",
      '400 {"error":"missing_msg"}\n405 {"error":"method_not_allowed"}\n404 {"error":"not_found"}\n405 {"error":"method_not_allowed"}'),
     ("GET /health?debug=1\nPOST /nope",
      '200 {"status":"ok"}\n404 {"error":"not_found"}')],
    hints=["Parse the URL once at the top and use `url.pathname` everywhere.",
           "Reject unknown paths first, then the wrong method — that ordering is what lets 404 and 405 mean different things.",
           "The last test checks two things at once: a query string must not break `/health`, and an unknown path must be 404 even with a non-GET method."])

_P1 = _project(
    "first-server", 1,
    "Your First HTTP Server",
    "A program that listens on a port and answers — no framework, no install.",
    "Starter",
    "Write, run and reason about a real HTTP server in one file, routing on method and path and answering in JSON with honest status codes.",
    "Every framework you will ever use — Express, Fastify, NestJS — is a wrapper around exactly this. Knowing what it wraps is the difference between using a framework and being trapped by one.",
    110,
    [],
    ["node:http", "request/response", "status codes", "routing", "JSON", "query strings"],
    ["Start a server on a port and explain why the process does not exit",
     "Send a JSON body with the right Content-Type and an honest status code",
     "Route on method and path, and tell 404 from 405",
     "Parse a query string without breaking path matching",
     "Debug a hanging request and a double reply"],
    """
You are going to build a tiny service with three endpoints and no dependencies
at all. It will not store anything yet — project 2 does that. The point of this
project is to make the request/response cycle concrete: bytes arrive, your
function runs, bytes go back.

By the end you will have `server.js`, runnable with `node server.js`, that
answers a health check, reports its version, echoes a query parameter, and says
something *accurate* when you ask it for something it does not have.

Keep this folder. Project 2 opens the same file and grows it into a real API.
""",
    [_ep("GET", "/health", "Liveness check", "", '{"status":"ok"}', "200"),
     _ep("GET", "/version", "Report the build", "", '{"version":"1.0.0"}', "200"),
     _ep("GET", "/echo?msg=…", "Echo a query parameter", "", '{"msg":"hi"}', "200 · 400"),
     _ep("*", "/anything-else", "Unknown path", "", '{"error":"not_found"}', "404"),
     _ep("POST", "/health", "Known path, wrong verb", "", '{"error":"method_not_allowed"}', "405")],
    """
```
mkdir notes-api
cd notes-api
```

Create one file, `server.js`. That is the entire setup — there is no
`package.json`, no `npm install`, and no build step in this track.

Run it with:

```
node server.js
```

Node decides a file is an ES module when it sees `import` syntax, so `import
http from "node:http"` works with no configuration. Every edit needs a restart:
stop with `Ctrl+C`, run again.

**Requires Node 18 or newer** (this app ships with a newer one). Check with
`node --version`.
""",
    [_P1_S1, _P1_S2, _P1_S3, _P1_S4],
    final_build=_P1_FINAL,
    acceptance=[
        "`node server.js` starts and keeps running until Ctrl+C.",
        "`GET /health` returns 200 and `{\"status\":\"ok\"}` with a JSON Content-Type.",
        "`GET /version` returns 200 and `{\"version\":\"1.0.0\"}`.",
        "`GET /echo?msg=hi` returns 200 and `{\"msg\":\"hi\"}`.",
        "`GET /echo` with no msg returns 400, not 500 and not an empty 200.",
        "`POST /health` returns 405; `GET /nope` returns 404.",
        "`GET /health?debug=1` still returns 200 — query strings do not break routing.",
        "No branch of the handler can reply twice or fail to reply.",
    ],
    manual_test="""
With the server running in one terminal, use another:

```
curl -i http://localhost:3000/health
curl -i http://localhost:3000/version
curl -i "http://localhost:3000/echo?msg=hi"
curl -i "http://localhost:3000/echo"
curl -i -X POST http://localhost:3000/health
curl -i http://localhost:3000/nope
curl -i "http://localhost:3000/health?debug=1"
```

`-i` prints the status line and headers — read them, not just the body. On
Windows PowerShell, `curl` is an alias for `Invoke-WebRequest`; use `curl.exe`
explicitly, or run these in Git Bash.

No curl? The browser address bar covers every GET here.
""",
    reference="""
import http from "node:http";

function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  const path = url.pathname;

  if (path !== "/health" && path !== "/version" && path !== "/echo") {
    return send(res, 404, { error: "not_found" });
  }
  if (req.method !== "GET") {
    return send(res, 405, { error: "method_not_allowed" });
  }
  if (path === "/health") return send(res, 200, { status: "ok" });
  if (path === "/version") return send(res, 200, { version: "1.0.0" });

  const msg = url.searchParams.get("msg");
  if (msg === null) return send(res, 400, { error: "missing_msg" });
  send(res, 200, { msg });
}

const server = http.createServer(handler);
server.listen(3000, () => console.log("listening on http://localhost:3000"));
""",
    stretch=[
        "Read the port from `process.env.PORT`, defaulting to 3000. This is how every deployed service is configured.",
        "Log one line per request: method, path, status and elapsed milliseconds. You will need to record the time before replying.",
        "Add `GET /uptime` returning seconds since start. Compute it from a timestamp captured at boot.",
        "Return a `Allow: GET` header alongside every 405 — the spec actually requires it.",
    ],
    glossary=[
        _gloss("port", "A number a process claims on a machine so incoming connections can find it. Only one listener per port at a time — hence EADDRINUSE."),
        _gloss("handler", "The function run once per request, receiving the request and the response objects."),
        _gloss("status code", "The three-digit verdict on a request. 2xx worked, 4xx blames the client, 5xx blames the server."),
        _gloss("Content-Type", "A header labelling the format of the body so the client knows how to read it."),
        _gloss("query string", "The `?a=1&b=2` tail of a URL. Always strings, always attacker-controlled."),
        _gloss("404 vs 405", "404: no such path. 405: that path exists, but not with this verb."),
        _gloss("endpoint", "A method + path pair, together with what it does. `GET /notes` and `POST /notes` are two endpoints."),
    ],
    cheatsheet="""
```js
import http from "node:http";

// one reply, always through here
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

// what you get per request
req.method                       // "GET" | "POST" | "PUT" | "PATCH" | "DELETE"
req.url                          // "/echo?msg=hi"  — path AND query
req.headers["content-type"]      // header names arrive lowercased

// parse it
const url = new URL(req.url, "http://localhost");
url.pathname;                    // "/echo"
url.searchParams.get("msg");     // "hi" | "" | null

// start it
http.createServer(handler).listen(3000);
```

| Status | Say it out loud |
| --- | --- |
| 200 | Here it is. |
| 201 | I made it; here it is. |
| 204 | Done. Nothing to show you. |
| 400 | Your request is malformed. |
| 404 | No such thing here. |
| 405 | That exists, but not with that verb. |
| 500 | I broke. Not your fault. |
""",
    self_check=[
        "I can explain, without looking, why `node server.js` does not return to the prompt.",
        "I know why `res.end({a:1})` throws and what to write instead.",
        "I can say what a client should conclude from 404 versus 405.",
        "I know why `if (searchParams.get(\"done\"))` is true for `?done=false`.",
        "I can find the cause of a request that hangs forever.",
    ],
    review=[
        _q("Which of these is a single endpoint?",
           ["/notes", "GET", "GET /notes", "http://localhost:3000"],
           2,
           "An endpoint is a method + path pair. The same path with a different verb is a different endpoint."),
        _q("`res.writeHead(200, …)` is called AFTER `res.end(body)`. What happens?",
           ["The status is applied retroactively", "Node throws — headers cannot be set after the response was sent",
            "Nothing; order is irrelevant", "The response is sent twice"],
           1,
           "`end()` flushes the response. Headers must be set before anything is sent."),
        _q("Which status best fits 'you sent me JSON I could not parse'?",
           ["404", "500", "400", "204"],
           2,
           "The client's request is malformed, so it is 4xx — specifically 400. Returning 500 would blame your own server for their typo."),
        _q("Why is `req.url === \"/health\"` fragile?",
           ["req.url is lowercased", "req.url includes the query string, so /health?x=1 will not match",
            "req.url includes the host", "It is not — it is the recommended way"],
           1,
           "That is exactly why you parse with `new URL(...)` and compare `url.pathname` instead."),
    ],
    milestone="You can write and run an HTTP server from scratch, and you know what a framework would have been doing for you.",
)

_PROJECTS.append(_P1)


# ===========================================================================
# PROJECT 2 — The Notes API: CRUD in memory
# ===========================================================================

# A second, smaller replayer for the one exercise that practises the store on
# its own, with no HTTP in the way.
_STORE_DRIVER = """
// ---- store driver (given — don't edit) ------------------------------------
// stdin: one command per line — CREATE <title> | LIST | FIND <id> | REMOVE <id>
for (const line of fs.readFileSync(0, "utf8").split("\\n")) {
  const [cmd, ...rest] = line.trim().split(" ");
  if (!cmd) continue;
  const arg = rest.join(" ");
  if (cmd === "CREATE") console.log(JSON.stringify(create(arg)));
  if (cmd === "LIST") console.log(JSON.stringify(list()));
  if (cmd === "FIND") console.log(JSON.stringify(find(Number(arg)) ?? null));
  if (cmd === "REMOVE") console.log(remove(Number(arg)));
}
"""


def _store_prog(code):
    return 'import fs from "node:fs";\n\n' + _bp(code) + "\n" + _bp(_STORE_DRIVER)


_P2_S1 = _step(
    "resource-model",
    "Resources, and the store behind them",
    "CRUD is four operations; HTTP already has verbs for all four.",
    """
An API is organised around **resources** — nouns, not actions. Your noun here is
a *note*. Once you have the noun, HTTP gives you the verbs for free, and the
whole design fits in one table:

| Operation | Method | Path | Success |
| --- | --- | --- | --- |
| Create | `POST` | `/notes` | 201 + the created note |
| Read all | `GET` | `/notes` | 200 + an array |
| Read one | `GET` | `/notes/:id` | 200 + the note |
| Update | `PUT` | `/notes/:id` | 200 + the updated note |
| Delete | `DELETE` | `/notes/:id` | 204, empty body |

Two paths, five endpoints. Notice what is *not* here: no `/createNote`, no
`/getNoteById`, no `/deleteAllNotes`. Putting the verb in the path is the most
common way a first API goes wrong — it throws away everything HTTP already
knows how to express, and it means every client has to learn your vocabulary
instead of the standard one.

### The collection / item split

`/notes` is a **collection**; `/notes/17` is an **item**. They behave
differently and you will route them differently, so learn to see the split:
`GET /notes` cannot 404 (an empty list is a fine answer), while `GET /notes/17`
absolutely can.

### Do this

1. Open `server.js` from project 1 and add a store above the handler:

   ```js
   const notes = new Map();
   let nextId = 1;

   function create(title) {
     const note = { id: nextId++, title, done: false };
     notes.set(note.id, note);
     return note;
   }

   function list() {
     return [...notes.values()];
   }

   function find(id) {
     return notes.get(id);
   }

   function remove(id) {
     return notes.delete(id);
   }
   ```

2. Read those five lines carefully, because each one is a decision:

   - **A `Map`, not an array.** Looking a note up by id is `notes.get(id)` —
     one step, no scanning. With an array you would write `.find()` every time
     and get O(n) lookups for free.
   - **`nextId++` returns the value and *then* increments**, so the first note
     gets id 1. Real services use `crypto.randomUUID()`; a counter is used here
     so the ids are predictable enough to write tests against.
   - **`[...notes.values()]`** copies into a fresh array so callers cannot
     mutate your store by accident.
   - **`notes.delete(id)` returns a boolean** — `true` if something was
     removed. That boolean is how your DELETE route will know whether to answer
     204 or 404, so do not throw it away.

3. Keep the store **separate from the handler**. The handler translates HTTP;
   the store keeps data. Blurring them is what makes a server impossible to
   test, and project 4 will cash in on the separation.

### About the Map key

`notes.get("1")` and `notes.get(1)` are different lookups — `Map` compares keys
with `===`, and a string is never `===` a number. Ids come out of a URL as
strings, so **every** lookup needs `Number(rawId)` first. This bug is
responsible for an enormous number of confusing 404s.
""",
    """
- You can call `create("Buy milk")` and get `{ id: 1, title: "Buy milk", done: false }`.
- A second `create` gives id 2 — the counter is outside the function.
- `find(1)` returns the note; `find(999)` returns `undefined`.
- `remove(1)` returns `true`, and calling it again returns `false`.
""",
    pitfalls=[
        "`notes.get(\"1\")` misses a note stored under the number 1. Convert ids from the URL with `Number()` before every lookup.",
        "Putting `let nextId = 1` INSIDE create() resets it on every call, so every note gets id 1.",
        "Returning `notes.values()` instead of `[...notes.values()]` hands out a live iterator that JSON.stringify turns into `{}`.",
    ],
    warmup=[
        _q("Which of these is a well-designed endpoint for creating a note?",
           ["GET /createNote?title=Buy", "POST /notes", "POST /notes/create", "PUT /addNote"],
           1,
           "The path names the resource; the method says what you are doing to it. Verbs in the path duplicate what HTTP already expresses — and GET must never create anything."),
    ],
    exercises=[
        _ex("be2-store", "The store behind the API",
            "Finish `create` so each note gets the next id and lands in the Map. The first note must be id 1.",
            _store_prog("""
const notes = new Map();
let nextId = 1;

function create(title) {
  const note = { id: nextId++, title, done: false };
  notes.set(note.id, note);
  return note;
}

function list() {
  return [...notes.values()];
}

function find(id) {
  return notes.get(id);
}

function remove(id) {
  return notes.delete(id);
}
"""),
            "  const note = { id: nextId++, title, done: false };",
            [("CREATE Buy milk\nCREATE Walk dog\nLIST",
              '{"id":1,"title":"Buy milk","done":false}\n'
              '{"id":2,"title":"Walk dog","done":false}\n'
              '[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":false}]'),
             ("CREATE One\nFIND 1\nFIND 99\nREMOVE 1\nREMOVE 1\nLIST",
              '{"id":1,"title":"One","done":false}\n'
              '{"id":1,"title":"One","done":false}\n'
              'null\ntrue\nfalse\n[]')],
            hints=["The note needs three fields, in the order the expected output shows: id, title, done.",
                   "`nextId++` yields the current value and then increments — which is exactly what you want for the first id to be 1.",
                   "`const note = { id: nextId++, title, done: false };`"]),
    ],
    quiz=[
        _q("Why store notes in a Map keyed by id rather than in an array?",
           ["Maps use less memory", "Lookup by id is one step instead of a scan",
            "Arrays cannot hold objects", "JSON.stringify only works on Maps"],
           1,
           "Read-one, update and delete all start by finding a note by id. A Map makes that a single operation; an array makes it a scan every time."),
        _q("`GET /notes` when nothing has been created yet. What should it return?",
           ["404 with an error", "200 with `[]`", "204 with no body", "500"],
           1,
           "The collection exists and is empty — that is a successful answer. 404 would mean the /notes endpoint itself does not exist."),
    ],
)

_P2_S2 = _step(
    "read-body",
    "Reading a request body",
    "The body arrives in pieces, so getting it is asynchronous. This surprises everyone once.",
    """
`POST` and `PUT` carry a body. Unlike `req.method` and `req.url`, the body is
**not sitting there waiting for you** — Node hands you the request as soon as
the headers arrive, and the body streams in afterwards, in chunks. So reading it
is asynchronous, and there is no `req.body` in plain Node. (If you have seen
`req.body` before, that was Express adding it for you.)

### Do this

1. Add this helper to `server.js`:

   ```js
   function readBody(req) {
     return new Promise((ok) => {
       let raw = "";
       req.on("data", (chunk) => (raw += chunk));
       req.on("end", () => ok(raw));
     });
   }
   ```

   `req.on("data", …)` fires once per chunk; `req.on("end", …)` fires once,
   when there are no more. You accumulate, then resolve. That is the entire
   pattern, and it is what every body parser in every framework is doing
   underneath.

2. Make your handler `async`, and read the body before you use it:

   ```js
   async function handler(req, res) {
     const raw = await readBody(req);
     const data = raw ? JSON.parse(raw) : {};
     // …
   }
   ```

3. Note the `raw ? … : {}`. A `GET` has no body, so `raw` is `""` — and
   `JSON.parse("")` throws `SyntaxError: Unexpected end of JSON input`. Guarding
   with a default is the difference between a working GET and a 500.

### The mistake to make once, deliberately

Delete the `await` and run a POST. `raw` is now a `Promise`, `JSON.parse` gets
`"[object Promise]"`, and you get a 500 whose stack trace points at a line that
looks perfectly fine. Put the `await` back. Recognising this failure on sight is
worth the thirty seconds.

### Why the body is a stream at all

An upload can be gigabytes. Node refuses to decide for you whether to hold all
of that in memory, so it hands you the pieces and lets you choose. For JSON
bodies, accumulating a string is the right choice — but a production server also
caps how much it will accumulate, or a single request can exhaust its memory.
""",
    """
- `POST /notes` with a JSON body reaches your handler with the parsed object.
- `GET /notes` still works — an empty body does not throw.
- Removing the `await` produces a 500, and you know why on sight.
""",
    pitfalls=[
        "There is no `req.body` in plain Node. That is an Express addition, and reaching for it gives you `undefined`.",
        "`JSON.parse(\"\")` throws. Any request without a body needs a default before you parse.",
        "Forgetting `await` gives you a Promise, not a string — and an error message that points nowhere useful.",
    ],
    warmup=[
        _q("Your handler runs `const raw = readBody(req); const data = JSON.parse(raw);`. What happens on a POST?",
           ["It works — readBody is synchronous", "`data` is an empty object",
            "JSON.parse throws, so the request 500s", "The request hangs forever"],
           2,
           "Without `await`, `raw` is a Promise. JSON.parse stringifies it to \"[object Promise]\", which is not valid JSON."),
    ],
    exercises=[
        _ex("be2-read-body", "Collect the chunks",
            "Finish `readBody` so the promise resolves with the whole body once the stream ends.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const raw = await readBody(req);
  const data = raw ? JSON.parse(raw) : {};
  send(res, 200, { got: data.title ?? null, len: raw.length });
}
"""),
            '    req.on("end", () => ok(raw));',
            [('POST /echo {"title":"Buy milk"}', '200 {"got":"Buy milk","len":20}'),
             ('GET /echo\nPOST /echo {"title":"Hi"}', '200 {"got":null,"len":0}\n200 {"got":"Hi","len":14}')],
            hints=["The `data` listener is already accumulating into `raw`. You need the event that fires when there is no more.",
                   "Resolve the promise with the accumulated string — `ok` is the resolve function.",
                   '`req.on("end", () => ok(raw));`']),
        _fix("be2-empty-body", "The GET that 500s",
             "POSTing works, but every GET comes back as a 500. Find out why and fix it — GETs must return `{\"got\":null}`.",
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const raw = await readBody(req);
  const data = JSON.parse(raw);
  send(res, 200, { got: data.title ?? null });
}
"""),
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const raw = await readBody(req);
  const data = raw ? JSON.parse(raw) : {};
  send(res, 200, { got: data.title ?? null });
}
"""),
             [('POST /x {"title":"Hi"}\nGET /x', '200 {"got":"Hi"}\n200 {"got":null}'),
              ('GET /x\nGET /y', '200 {"got":null}\n200 {"got":null}')],
             hints=["A GET carries no body, so `raw` is the empty string. What does JSON.parse do with that?",
                    "`JSON.parse(\"\")` throws — and a throw inside the handler becomes a 500.",
                    "Parse only when there is something to parse: `raw ? JSON.parse(raw) : {}`."]),
    ],
    quiz=[
        _q("Why is reading a request body asynchronous in Node?",
           ["Because JSON parsing is slow", "Because the body arrives in chunks after the headers, and may be huge",
            "Because Node is single-threaded", "It is not — Express made it async"],
           1,
           "Node gives you the request as soon as the headers land and streams the body afterwards, so you decide how much to hold in memory."),
        _q("Which listener tells you the body is complete?",
           ["req.on(\"data\")", "req.on(\"close\")", "req.on(\"end\")", "req.on(\"finish\")"],
           2,
           "`data` fires once per chunk and may fire many times; `end` fires exactly once, when there are no more chunks."),
    ],
)

_P2_S3 = _step(
    "create-and-read",
    "Create and read",
    "POST returns 201 and the created thing; GET one 404s honestly.",
    """
Now wire the store to the routes. Two paths — the collection and the item — so
first you have to tell them apart.

### Do this

1. Split the path into segments at the top of the handler:

   ```js
   const url = new URL(req.url, "http://localhost");
   const [, resource, rawId] = url.pathname.split("/");
   ```

   `"/notes/17".split("/")` gives `["", "notes", "17"]` — the leading empty
   string is the piece before the first slash. The comma with nothing before it
   skips it. For `/notes` you get `rawId === undefined`, which is exactly the
   signal you need: **`rawId` undefined means the collection; defined means an
   item.**

2. Reject anything that is not the notes resource:

   ```js
   if (resource !== "notes") return send(res, 404, { error: "not_found" });
   ```

3. Handle the collection:

   ```js
   if (rawId === undefined) {
     if (req.method === "GET") return send(res, 200, list());
     if (req.method === "POST") {
       const data = JSON.parse((await readBody(req)) || "{}");
       const note = create(data.title);
       res.writeHead(201, {
         "Content-Type": "application/json",
         Location: `/notes/${note.id}`,
       });
       return res.end(JSON.stringify(note));
     }
     return send(res, 405, { error: "method_not_allowed" });
   }
   ```

4. Handle a single item:

   ```js
   const note = find(Number(rawId));
   if (!note) return send(res, 404, { error: "not_found" });
   if (req.method === "GET") return send(res, 200, note);
   return send(res, 405, { error: "method_not_allowed" });
   ```

   `Number(rawId)` is not optional — see the Map-key warning in step 1.

### Why 201 and not 200

`201 Created` says *a new resource now exists*, and the `Location` header says
where. A client can follow that header without guessing your URL scheme. `200`
would merely say "fine", which is true but much less useful. Returning the
created note in the body matters too: the client did not know the id it was
about to get, and this is how it finds out.

### Find-then-act

Look at the shape of the item branch: **find it, 404 if missing, then act.**
Every item route in this track follows it. Writing the 404 check once, before
the method branches, means you cannot forget it in the third one.
""",
    """
- `POST /notes {"title":"Buy milk"}` → 201, body `{"id":1,"title":"Buy milk","done":false}`,
  and a `Location: /notes/1` header (`curl -i` shows it).
- `GET /notes` → 200 and an array containing it.
- `GET /notes/1` → 200 and the note.
- `GET /notes/999` → 404, and `GET /nope` → 404.
""",
    pitfalls=[
        "`find(rawId)` without `Number()` always misses — the URL gives you a string and the Map key is a number.",
        "Returning 200 from POST loses the 'something new exists' signal; clients that follow Location break.",
        "Checking the method before checking that the note exists produces 405s for notes that were never there.",
    ],
    exercises=[
        _ch("be2-create-read", "Create, list, read one", "Easy",
            "Write the routing for the collection and the item. `POST /notes` → 201 with the created note. `GET /notes` → 200 with the array. `GET /notes/:id` → 200, or 404 `{\"error\":\"not_found\"}` if there is no such note. Any other path → 404. Any other method → 405 `{\"error\":\"method_not_allowed\"}`.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

const notes = new Map();
let nextId = 1;

async function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  const [, resource, rawId] = url.pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = { id: nextId++, title: data.title, done: false };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  if (req.method === "GET") return send(res, 200, note);
  return send(res, 405, { error: "method_not_allowed" });
}
"""),
            """  const url = new URL(req.url, "http://localhost");
  const [, resource, rawId] = url.pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = { id: nextId++, title: data.title, done: false };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  if (req.method === "GET") return send(res, 200, note);
  return send(res, 405, { error: "method_not_allowed" });""",
            [('POST /notes {"title":"Buy milk"}\nGET /notes/1\nGET /notes',
              '201 {"id":1,"title":"Buy milk","done":false}\n'
              '200 {"id":1,"title":"Buy milk","done":false}\n'
              '200 [{"id":1,"title":"Buy milk","done":false}]'),
             ('GET /notes\nGET /notes/1\nGET /users\nPUT /notes',
              '200 []\n404 {"error":"not_found"}\n404 {"error":"not_found"}\n405 {"error":"method_not_allowed"}'),
             ('POST /notes {"title":"A"}\nPOST /notes {"title":"B"}\nGET /notes/2\nPOST /notes/1',
              '201 {"id":1,"title":"A","done":false}\n'
              '201 {"id":2,"title":"B","done":false}\n'
              '200 {"id":2,"title":"B","done":false}\n'
              '405 {"error":"method_not_allowed"}')],
            hints=["`url.pathname.split(\"/\")` gives `[\"\", \"notes\", \"17\"]`. Destructure past the empty first piece.",
                   "`rawId === undefined` distinguishes the collection from an item. Handle the collection branch first and return from it.",
                   "In the item branch: `notes.get(Number(rawId))`, 404 if that is undefined, and only then look at the method."]),
    ],
    quiz=[
        _q("Why does a successful POST return 201 rather than 200?",
           ["201 is faster", "201 means a new resource exists, and pairs with a Location header",
            "200 is only for GET", "Because the body is JSON"],
           1,
           "The status carries meaning a client can act on: something new exists, and Location says where to find it."),
        _q("`\"/notes\".split(\"/\")` evaluates to what?",
           ['["notes"]', '["", "notes"]', '["", "notes", ""]', '["/", "notes"]'],
           1,
           "The piece before the leading slash is an empty string. That is why the id lands in the third slot and is `undefined` for the collection."),
    ],
)

_P2_S4 = _step(
    "update-and-delete",
    "Update and delete",
    "PUT replaces the whole thing. DELETE says 204 and nothing else.",
    """
Two operations left, and both have a subtlety that is easy to get wrong.

### PUT replaces

`PUT /notes/1` means *"make note 1 look like this"*. It is a **replacement**,
not a merge: any field the client leaves out goes back to its default. That is
what makes PUT **idempotent** — sending the same PUT ten times leaves the
resource in exactly the state one PUT would have.

```js
if (req.method === "PUT") {
  const data = JSON.parse((await readBody(req)) || "{}");
  const updated = { id: note.id, title: data.title, done: data.done === true };
  notes.set(note.id, updated);
  return send(res, 200, updated);
}
```

Notice the `id` is taken from the **existing note**, never from the body. A
client that sends `{"id": 999}` must not be able to renumber your data — the id
is in the URL, and the URL wins. Notice too that `done` is normalised with
`=== true`, so a missing field becomes `false` rather than `undefined` (which
`JSON.stringify` would silently drop from the response).

Merging instead of replacing is the mistake to avoid here. It looks harmless
and is *convenient*, which is exactly why it is a trap: `PUT` then means
something different on your server than everywhere else, and there is no longer
any way for a client to clear a field. Partial updates have their own verb —
`PATCH` — and project 3 adds it.

### DELETE returns 204

```js
if (req.method === "DELETE") {
  notes.delete(note.id);
  res.writeHead(204);
  return res.end();
}
```

`204 No Content` means *it worked and there is deliberately nothing to show
you*. A 204 **must not** carry a body — some clients will not even read it.
Note that `send(res, 204, null)` from your helper does the same job, since it
writes an empty body for `null`.

### Deleting twice

The first `DELETE /notes/1` returns 204. What should the second return? In this
track: **404**, because by then there is no note 1 to delete. (You will
occasionally see APIs answer 204 both times, on the grounds that the end state
is the same either way. Both are defensible; what matters is picking one and
being consistent — and your find-then-act structure gives you 404 for free.)
""",
    """
- `PUT /notes/1 {"title":"Renamed","done":true}` → 200 with all three fields updated.
- `PUT /notes/1 {"title":"Only"}` → `done` comes back `false`, not missing — PUT replaced it.
- A PUT with `{"id":999,...}` does not change the note's id.
- `DELETE /notes/1` → 204 with an empty body; a second `DELETE /notes/1` → 404.
""",
    pitfalls=[
        "Sending a body with 204. The status means 'no content'; some clients will not read what you send.",
        "Taking the id from the request body instead of the URL lets a client renumber your store.",
        "Merging on PUT instead of replacing means a client can never clear a field, and your PUT no longer means what PUT means everywhere else.",
    ],
    warmup=[
        _q("Note 1 is `{id:1,title:\"A\",done:true}`. A client sends `PUT /notes/1 {\"title\":\"B\"}`. What should note 1 be afterwards?",
           ['{id:1,title:"B",done:true}', '{id:1,title:"B",done:false}',
            '{id:1,title:"B"}', "Unchanged — the body is incomplete"],
           1,
           "PUT replaces. The omitted `done` returns to its default of false. If you wanted to keep it, that is a PATCH — a different verb, added in project 3."),
    ],
    exercises=[
        _fix("be2-put-merge", "The PUT that merges",
             "This PUT keeps fields the client left out, so a note can never be un-done. Make PUT replace the whole note: a missing `title` becomes `null` and a missing `done` becomes `false`. The id must always come from the URL.",
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

const notes = new Map([[1, { id: 1, title: "Buy milk", done: true }]]);

async function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  const [, resource, rawId] = url.pathname.split("/");
  if (resource !== "notes" || rawId === undefined) {
    return send(res, 404, { error: "not_found" });
  }
  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });

  if (req.method === "PUT") {
    const data = JSON.parse((await readBody(req)) || "{}");
    const updated = { ...note, ...data };
    notes.set(note.id, updated);
    return send(res, 200, updated);
  }
  if (req.method === "GET") return send(res, 200, note);
  return send(res, 405, { error: "method_not_allowed" });
}
"""),
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

const notes = new Map([[1, { id: 1, title: "Buy milk", done: true }]]);

async function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  const [, resource, rawId] = url.pathname.split("/");
  if (resource !== "notes" || rawId === undefined) {
    return send(res, 404, { error: "not_found" });
  }
  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });

  if (req.method === "PUT") {
    const data = JSON.parse((await readBody(req)) || "{}");
    const updated = { id: note.id, title: data.title ?? null, done: data.done === true };
    notes.set(note.id, updated);
    return send(res, 200, updated);
  }
  if (req.method === "GET") return send(res, 200, note);
  return send(res, 405, { error: "method_not_allowed" });
}
"""),
             [('PUT /notes/1 {"title":"Renamed"}',
               '200 {"id":1,"title":"Renamed","done":false}'),
              ('PUT /notes/1 {"id":999,"title":"Hacked","done":true}\nGET /notes/1\nGET /notes/999',
               '200 {"id":1,"title":"Hacked","done":true}\n'
               '200 {"id":1,"title":"Hacked","done":true}\n'
               '404 {"error":"not_found"}')],
             hints=["`{ ...note, ...data }` keeps every old field the client did not mention. That is a merge, and PUT is not a merge.",
                    "Build the replacement from scratch: id from the existing note, title from the body, done normalised to a real boolean.",
                    "`{ id: note.id, title: data.title ?? null, done: data.done === true }` — and note how spreading `data` would also have let the client overwrite the id."]),
    ],
    quiz=[
        _q("What does it mean that PUT is idempotent?",
           ["It can only be called once", "Repeating the same PUT leaves the same final state",
            "It never fails", "It does not change anything"],
           1,
           "Idempotent means repeating the request has no additional effect. That is why a client can safely retry a PUT after a timeout — and why POST, which creates a new note each time, is not idempotent."),
        _q("Why must a 204 response have an empty body?",
           ["Bodies are slow", "204 literally means 'no content' — clients are entitled to ignore anything sent",
            "Node forbids it", "So that DELETE stays idempotent"],
           1,
           "The status is a promise about the response. Breaking it means clients that skip reading the body silently lose whatever you sent."),
    ],
)

_P2_FINAL = _ch(
    "be2-final", "The complete Notes API", "Medium",
    "Build the whole CRUD API. `POST /notes` → 201 with `{id,title,done}` (done starts false). `GET /notes` → 200 array. `GET /notes/:id` → 200 or 404. `PUT /notes/:id` → 200 with the note fully replaced (id from the URL, missing title → null, missing done → false), or 404. `DELETE /notes/:id` → 204 empty, or 404 if it is already gone. Unknown resource → 404. Unsupported method on a real path → 405 `{\"error\":\"method_not_allowed\"}`.",
    _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

const notes = new Map();
let nextId = 1;

async function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  const [, resource, rawId] = url.pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = { id: nextId++, title: data.title ?? null, done: false };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "PUT") {
    const data = JSON.parse((await readBody(req)) || "{}");
    const updated = { id: note.id, title: data.title ?? null, done: data.done === true };
    notes.set(note.id, updated);
    return send(res, 200, updated);
  }
  if (req.method === "DELETE") {
    notes.delete(note.id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });
}
"""),
    """  const url = new URL(req.url, "http://localhost");
  const [, resource, rawId] = url.pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = { id: nextId++, title: data.title ?? null, done: false };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "PUT") {
    const data = JSON.parse((await readBody(req)) || "{}");
    const updated = { id: note.id, title: data.title ?? null, done: data.done === true };
    notes.set(note.id, updated);
    return send(res, 200, updated);
  }
  if (req.method === "DELETE") {
    notes.delete(note.id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });""",
    [('POST /notes {"title":"Buy milk"}\nPOST /notes {"title":"Walk dog"}\nGET /notes',
      '201 {"id":1,"title":"Buy milk","done":false}\n'
      '201 {"id":2,"title":"Walk dog","done":false}\n'
      '200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":false}]'),
     ('POST /notes {"title":"A"}\nPUT /notes/1 {"title":"B","done":true}\nGET /notes/1\nDELETE /notes/1\nGET /notes/1\nDELETE /notes/1',
      '201 {"id":1,"title":"A","done":false}\n'
      '200 {"id":1,"title":"B","done":true}\n'
      '200 {"id":1,"title":"B","done":true}\n'
      '204\n'
      '404 {"error":"not_found"}\n'
      '404 {"error":"not_found"}'),
     ('GET /notes\nPUT /notes\nGET /users/1\nPOST /notes {"title":"X"}\nPUT /notes/1 {"done":true}',
      '200 []\n'
      '405 {"error":"method_not_allowed"}\n'
      '404 {"error":"not_found"}\n'
      '201 {"id":1,"title":"X","done":false}\n'
      '200 {"id":1,"title":null,"done":true}')],
    hints=["Structure it in three layers: reject a non-notes resource, then handle the collection (`rawId === undefined`), then the item.",
           "In the item branch, find the note and 404 once, before any method check — all three item verbs need it.",
           "The last test is the PUT-replaces rule: `{\"done\":true}` with no title must come back with `title: null`, not the old title."])

_P2 = _project(
    "notes-crud", 2,
    "The Notes API — CRUD in Memory",
    "Five endpoints, one resource, the four operations every API is made of.",
    "Core",
    "Turn the bare server into a real resource API: create, list, read, replace and delete notes, with the status code each case deserves.",
    "Every product you have ever used is mostly CRUD with a nicer name. Get this shape right once and you will recognise it everywhere for the rest of your career.",
    150,
    ["first-server"],
    ["resources", "collection vs item", "request bodies", "201 Created", "204 No Content", "idempotency"],
    ["Map the four CRUD operations onto HTTP methods without inventing paths",
     "Read and parse a JSON request body from a stream",
     "Route a collection path and an item path differently",
     "Return 201 with a Location header on create, and 204 on delete",
     "Explain why PUT replaces rather than merges"],
    """
You are going to grow project 1's `server.js` into a working Notes API — the
smallest thing that is honestly a CRUD service. Notes live in memory in a `Map`,
so everything disappears when you stop the process. That is deliberate: project
4 adds persistence, and doing it in that order keeps the two ideas separate.

One thing this project deliberately does **not** do is validate input. `POST
/notes` with no title will happily store `title: null`. That gap is the subject
of project 3, and feeling the gap first is the point.
""",
    [_ep("POST", "/notes", "Create a note", '{"title":"Buy milk"}', '{"id":1,"title":"Buy milk","done":false}', "201"),
     _ep("GET", "/notes", "List every note", "", '[{"id":1,…}]', "200"),
     _ep("GET", "/notes/:id", "Read one note", "", '{"id":1,…}', "200 · 404"),
     _ep("PUT", "/notes/:id", "Replace a note", '{"title":"New","done":true}', '{"id":1,"title":"New","done":true}', "200 · 404"),
     _ep("DELETE", "/notes/:id", "Delete a note", "", "(empty)", "204 · 404")],
    """
Keep working in the same folder and the same `server.js`. Nothing new to
install.

```
cd notes-api
node server.js
```

You will be sending POST and PUT requests now, which a browser address bar
cannot do. Use `curl` from a second terminal — the **Try it yourself** section
below has every command ready to paste.
""",
    [_P2_S1, _P2_S2, _P2_S3, _P2_S4],
    final_build=_P2_FINAL,
    acceptance=[
        "`POST /notes {\"title\":\"Buy milk\"}` returns 201 and `{\"id\":1,\"title\":\"Buy milk\",\"done\":false}`.",
        "The 201 response carries a `Location: /notes/1` header.",
        "`GET /notes` returns 200 and an array; on a fresh server that array is `[]`, not a 404.",
        "`GET /notes/1` returns the note; `GET /notes/999` returns 404.",
        "`PUT /notes/1 {\"title\":\"New\"}` replaces the note — `done` comes back `false`, not the old value.",
        "A PUT body containing `\"id\": 999` does not change the note's id.",
        "`DELETE /notes/1` returns 204 with an empty body; repeating it returns 404.",
        "`GET /users` returns 404 and `PUT /notes` returns 405.",
        "The store functions never touch `req` or `res`.",
    ],
    manual_test="""
```
curl -i -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" \\
  -d '{"title":"Buy milk"}'

curl -i http://localhost:3000/notes
curl -i http://localhost:3000/notes/1
curl -i http://localhost:3000/notes/999

curl -i -X PUT http://localhost:3000/notes/1 \\
  -H "Content-Type: application/json" \\
  -d '{"title":"Buy oat milk","done":true}'

curl -i -X PUT http://localhost:3000/notes/1 \\
  -H "Content-Type: application/json" \\
  -d '{"title":"Only a title"}'      # done must come back false

curl -i -X DELETE http://localhost:3000/notes/1
curl -i -X DELETE http://localhost:3000/notes/1      # now 404
```

Check the `Location` header on the create, and that the DELETE response really
is empty.

On Windows PowerShell the single quotes will not survive — run these in Git
Bash, or swap to `--data-raw "{\\"title\\":\\"Buy milk\\"}"`.
""",
    reference="""
import http from "node:http";

// ---- helpers ---------------------------------------------------------------
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

// ---- store -----------------------------------------------------------------
const notes = new Map();
let nextId = 1;

const list = () => [...notes.values()];
const find = (id) => notes.get(id);
const remove = (id) => notes.delete(id);

function create(title) {
  const note = { id: nextId++, title: title ?? null, done: false };
  notes.set(note.id, note);
  return note;
}

// ---- routes ----------------------------------------------------------------
async function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  const [, resource, rawId] = url.pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  // collection: /notes
  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, list());
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = create(data.title);
      res.writeHead(201, {
        "Content-Type": "application/json",
        Location: `/notes/${note.id}`,
      });
      return res.end(JSON.stringify(note));
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  // item: /notes/:id   — find it once, 404 once, then act
  const note = find(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "PUT") {
    const data = JSON.parse((await readBody(req)) || "{}");
    const updated = { id: note.id, title: data.title ?? null, done: data.done === true };
    notes.set(note.id, updated);
    return send(res, 200, updated);
  }
  if (req.method === "DELETE") {
    remove(note.id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });
}

const server = http.createServer((req, res) => {
  Promise.resolve(handler(req, res)).catch((err) => {
    console.error(err);
    if (!res.headersSent) send(res, 500, { error: "server_error" });
  });
});
server.listen(3000, () => console.log("listening on http://localhost:3000"));
""",
    stretch=[
        "Add `POST /notes/:id/done` that flips `done` to true. Then argue with yourself about whether that verb-in-the-path is justified, and what the alternative would be.",
        "Give every note a `createdAt`. You will immediately notice your tests cannot predict it — that tension is real, and the usual answer is to inject a clock.",
        "Support `GET /notes?done=true`. Remember that query values are strings; project 5 does this properly.",
        "Cap the request body at 1 MB in `readBody` and reject anything larger with 413. An unbounded accumulator is a real denial-of-service hole.",
    ],
    glossary=[
        _gloss("resource", "The noun your API exposes. Notes, users, orders. Paths name resources; methods say what to do to them."),
        _gloss("collection vs item", "/notes is the collection; /notes/17 is one item. A collection cannot 404 for being empty; an item can."),
        _gloss("CRUD", "Create, Read, Update, Delete — the four operations, mapped to POST, GET, PUT, DELETE."),
        _gloss("idempotent", "Repeating the request gives the same final state. PUT and DELETE are; POST is not."),
        _gloss("201 Created", "A new resource exists. Pairs with a Location header pointing at it."),
        _gloss("204 No Content", "It worked and there is deliberately nothing to send back. Must have an empty body."),
        _gloss("Location header", "Where the thing you just created lives, so the client does not have to guess your URL scheme."),
    ],
    cheatsheet="""
```js
// path → resource + id
const url = new URL(req.url, "http://localhost");
const [, resource, rawId] = url.pathname.split("/");
// "/notes"     → resource "notes", rawId undefined   (collection)
// "/notes/17"  → resource "notes", rawId "17"        (item — a STRING)

// body (async! there is no req.body in plain Node)
function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (c) => (raw += c));
    req.on("end", () => ok(raw));
  });
}
const data = JSON.parse((await readBody(req)) || "{}");

// find-then-act — every item route
const note = notes.get(Number(rawId));      // Number() is not optional
if (!note) return send(res, 404, { error: "not_found" });
```

| Verb | Path | Status | Body back |
| --- | --- | --- | --- |
| POST | /notes | 201 + Location | the created note |
| GET | /notes | 200 | array (maybe empty) |
| GET | /notes/:id | 200 / 404 | the note |
| PUT | /notes/:id | 200 / 404 | the replaced note |
| DELETE | /notes/:id | 204 / 404 | nothing |
""",
    self_check=[
        "I can write the CRUD-to-HTTP table from memory.",
        "I can explain why reading a request body is asynchronous.",
        "I know why `notes.get(rawId)` fails and `notes.get(Number(rawId))` works.",
        "I can say what PUT does to a field the client left out, and why.",
        "I know why my DELETE returns 204 and not 200.",
    ],
    review=[
        _q("Which pair of endpoints shares a path but does different work?",
           ["GET /notes and GET /notes/1", "POST /notes and GET /notes",
            "PUT /notes/1 and DELETE /notes/2", "GET /notes and GET /users"],
           1,
           "Same path, different verb, different operation. That is exactly what routing on method + path is for."),
        _q("A POST is retried after a network timeout, and both attempts reach the server. What happens?",
           ["Nothing — POST is idempotent", "Two notes are created",
            "The second returns 409", "The second replaces the first"],
           1,
           "POST is not idempotent: each one creates. This is a real problem in production, usually solved with a client-supplied idempotency key."),
        _q("Why take the id from the URL rather than the request body on PUT?",
           ["The body might be missing", "URLs are faster to parse",
            "Otherwise a client could renumber or overwrite another note",
            "JSON cannot hold numbers"],
           2,
           "The URL identifies the resource. Trusting an id in the body hands a client the ability to write wherever it likes."),
        _q("`GET /notes/abc` on a server that does `Number(rawId)`. What happens?",
           ["It throws", "Number(\"abc\") is NaN, no note matches, so 404",
            "It returns the first note", "500"],
           1,
           "`NaN` is never a key in the Map, so find-then-act produces a clean 404. Project 3 makes that rejection explicit with a 400 instead."),
    ],
    milestone="You have written a real CRUD API — the shape underneath most of the software you use every day.",
)

_PROJECTS.append(_P2)


# ===========================================================================
# PROJECT 3 — Validation & Error Contracts
# ===========================================================================

_VALIDATE_DRIVER = """
// ---- validator driver (given — don't edit) ---------------------------------
// stdin: one JSON object per line. Prints validate()'s result for each.
for (const line of fs.readFileSync(0, "utf8").split("\\n")) {
  const text = line.trim();
  if (!text) continue;
  console.log(JSON.stringify(validate(JSON.parse(text))));
}
"""


def _validate_prog(code):
    return 'import fs from "node:fs";\n\n' + _bp(code) + "\n" + _bp(_VALIDATE_DRIVER)


_LONG = "x" * 101

_P3_S1 = _step(
    "error-contract",
    "One error shape, everywhere",
    "Decide what a failure looks like once, then never improvise again.",
    """
Your API currently accepts anything. `POST /notes {}` stores a note with no
title. `POST /notes {"title": 42}` stores a number. Nobody notices until a
screen somewhere renders `undefined`, and by then the bad data is everywhere.

Two things fix this, and they are separate: **validating input**, and **saying
so in a predictable way.**

### The error contract

Every failure from here on has the same shape:

```json
{ "error": "validation_failed", "fields": { "title": "title is required" } }
```

- `error` is a **stable, machine-readable code**. Clients branch on it. It never
  changes wording, and it is never a sentence.
- `fields` is present only for validation failures, and maps each bad field to a
  human-readable reason.

Simple failures keep the same envelope with no `fields`:

```json
{ "error": "not_found" }
```

Why it matters: without a contract, every endpoint invents its own error. One
returns `{"message": "..."}`, another a bare string, a third an HTML page from
some framework's default handler. Client code then grows a tangle of guesses.
Pick a shape on day one — this one is fine — and hold it.

### Do this

1. Add a validator **above your routes**. It is a pure function: data in, errors
   out. It never touches `req` or `res`, which is what makes it easy to reason
   about and trivial to test.

   ```js
   function validate(data) {
     const fields = {};

     if (data.title === undefined) {
       fields.title = "title is required";
     } else if (typeof data.title !== "string" || data.title.trim() === "") {
       fields.title = "title must be a non-empty string";
     } else if (data.title.trim().length > 100) {
       fields.title = "title must be 100 characters or fewer";
     }

     if (data.done !== undefined && typeof data.done !== "boolean") {
       fields.done = "done must be true or false";
     }

     return fields;
   }
   ```

2. Use it in `POST` before you touch the store:

   ```js
   const fields = validate(data);
   if (Object.keys(fields).length > 0) {
     return send(res, 400, { error: "validation_failed", fields });
   }
   ```

3. **Store the trimmed value**, not the raw one: `title: data.title.trim()`.
   Validating one value and storing a different one is a subtle, real bug —
   `"  "` passes a naive check and stores as whitespace.

### Three rules worth internalising

- **Collect all the errors, then report.** Returning on the first bad field
  makes a client fix one thing, resubmit, and discover the next. Users hate
  that, and so do you when you are the client.
- **Check presence and type separately.** `if (!data.title)` conflates missing,
  empty and `false`. Being explicit about `undefined` versus wrong-type is what
  lets you give a message that actually helps.
- **Validation belongs at the edge.** Everything past the validator can assume
  the data is well-formed. That assumption is only safe if there is exactly one
  door in.
""",
    """
- `validate({title: "Buy milk"})` returns `{}` — no errors.
- `validate({})` returns `{title: "title is required"}`.
- `validate({title: "ok", done: "yes"})` complains about `done`, not `title`.
- `POST /notes {}` now returns 400 with the `validation_failed` envelope, and the store is untouched.
""",
    pitfalls=[
        "`if (!data.title)` treats missing, empty and the number 0 identically — you cannot write a useful message from that.",
        "Returning after the first error makes clients play whack-a-mole. Collect everything, then respond.",
        "Validating `title.trim()` but storing `title` lets `\"  \"` through into your data.",
    ],
    warmup=[
        _q("`validate({title: \"\"})` with the rules above. What comes back?",
           ['{} — an empty string is a string', '{title: "title is required"}',
            '{title: "title must be a non-empty string"}', "It throws"],
           2,
           "The field is present, so it is not 'required'; it is present and unusable, which is a different message. Separating those two cases is the whole point of checking `undefined` explicitly."),
    ],
    exercises=[
        _ex("be3-validate", "Collect every error",
            "Finish `validate` so a missing title is reported as `title is required`. It must return an object of field → message, and `{}` when everything is fine.",
            _validate_prog("""
function validate(data) {
  const fields = {};

  if (data.title === undefined) {
    fields.title = "title is required";
  } else if (typeof data.title !== "string" || data.title.trim() === "") {
    fields.title = "title must be a non-empty string";
  } else if (data.title.trim().length > 100) {
    fields.title = "title must be 100 characters or fewer";
  }

  if (data.done !== undefined && typeof data.done !== "boolean") {
    fields.done = "done must be true or false";
  }

  return fields;
}
"""),
            """  if (data.title === undefined) {
    fields.title = "title is required";
  } else if""",
            [('{"title":"Buy milk"}\n{}\n{"title":"   "}',
              '{}\n{"title":"title is required"}\n{"title":"title must be a non-empty string"}'),
             ('{"title":123}\n{"title":"ok","done":"yes"}\n{"done":1}\n{"title":"ok","done":true}',
              '{"title":"title must be a non-empty string"}\n'
              '{"done":"done must be true or false"}\n'
              '{"title":"title is required","done":"done must be true or false"}\n'
              '{}'),
             ('{"title":"' + _LONG + '"}',
              '{"title":"title must be 100 characters or fewer"}')],
            hints=["A missing field and a present-but-wrong field need different messages, so test for `undefined` first.",
                   "The `else if` chain already handles the wrong-type and too-long cases — you only supply the missing case.",
                   "Third test case: a bad `done` AND a missing title must both be reported in one response."]),
    ],
    quiz=[
        _q("Why should the `error` value be a short code rather than a sentence?",
           ["Sentences are slower to send", "Clients branch on it, so it must be stable while wording changes",
            "JSON cannot hold long strings", "It makes the status code redundant"],
           1,
           "Codes are the API; messages are for humans. Change a message and nothing breaks — change a code and every client does."),
        _q("A client sends `{}` to POST /notes. Which status?",
           ["404 Not Found", "422 only — 400 would be wrong",
            "400 Bad Request", "500 Internal Server Error"],
           2,
           "The request is well-formed HTTP but the content is unusable, so it is 4xx. 400 is universally understood; 422 is a defensible alternative, but pick one and be consistent."),
    ],
)

_P3_S2 = _step(
    "bad-json",
    "Malformed JSON is a 400, not a 500",
    "The first thing a stranger sends you will not be valid JSON.",
    """
Your handler does `JSON.parse(raw)`. What happens when a client sends
`{title: "oops"}` — valid JavaScript, invalid JSON? `JSON.parse` throws, nothing
catches it, and your framework-shaped catch-all turns it into a **500**.

That is a lie. A 500 says *"I broke"* and sends people to read your server logs.
The truth is *"you sent me something I cannot parse"* — a **400**.

### Do this

1. Wrap the parse and translate the failure:

   ```js
   let data;
   try {
     data = raw ? JSON.parse(raw) : {};
   } catch {
     return send(res, 400, { error: "invalid_json" });
   }
   ```

2. Reject a body that parses but is not an object. `JSON.parse("42")`,
   `JSON.parse("null")` and `JSON.parse("[1,2]")` all succeed, and none of them
   is a note:

   ```js
   if (data === null || typeof data !== "object" || Array.isArray(data)) {
     return send(res, 400, { error: "invalid_json" });
   }
   ```

   `typeof null === "object"` is a famous JavaScript wart, and arrays are
   objects too — hence all three checks.

3. Pull the whole thing into one helper so no route can forget it:

   ```js
   async function readJson(req) {
     const raw = await readBody(req);
     if (!raw) return {};
     const data = JSON.parse(raw);   // caller catches
     if (data === null || typeof data !== "object" || Array.isArray(data)) {
       throw new SyntaxError("body must be a JSON object");
     }
     return data;
   }
   ```

### The general principle

**Translate every failure at your boundary into a status the client can act
on.** An exception escaping to the top of your server is not an error-handling
strategy; it is the absence of one. There will always be a last-resort 500 —
project 7 builds it deliberately — but a 500 should mean *you found a bug in my
server*, and nothing else. Every 500 you can turn into a specific 4xx is one
fewer false alarm.
""",
    """
- `POST /notes` with the body `{oops` returns 400 `{"error":"invalid_json"}` — not 500.
- `POST /notes` with the body `[1,2]` also returns 400.
- `POST /notes` with valid JSON still works.
- Nothing in your terminal prints a stack trace for these.
""",
    pitfalls=[
        "`typeof null === \"object\"`, so a null body slips past a plain typeof check.",
        "`JSON.parse(\"[1,2]\")` succeeds — an array is valid JSON and an invalid note.",
        "A bare `catch (e) { send(res, 500, e.message) }` leaks internals to strangers. Return a code, log the detail.",
    ],
    warmup=[
        _q("Which of these makes `JSON.parse` THROW?",
           ['"null"', '"[1,2]"', "\"{title: 'x'}\"", '"42"'],
           2,
           "Unquoted keys and single quotes are JavaScript, not JSON. The other three all parse successfully — which is exactly why parsing alone is not enough: you must also check the shape."),
    ],
    exercises=[
        _fix("be3-bad-json", "The 500 that should be a 400",
             "Malformed JSON currently crashes into a 500, and a JSON array is accepted as if it were a note. Both should be 400 `{\"error\":\"invalid_json\"}`.",
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const raw = await readBody(req);
  const data = raw ? JSON.parse(raw) : {};
  send(res, 200, { title: data.title ?? null });
}
"""),
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const raw = await readBody(req);
  let data;
  try {
    data = raw ? JSON.parse(raw) : {};
  } catch {
    return send(res, 400, { error: "invalid_json" });
  }
  if (data === null || typeof data !== "object" || Array.isArray(data)) {
    return send(res, 400, { error: "invalid_json" });
  }
  send(res, 200, { title: data.title ?? null });
}
"""),
             [('POST /notes {"title":"ok"}\nPOST /notes {oops}',
               '200 {"title":"ok"}\n400 {"error":"invalid_json"}'),
              ('POST /notes [1,2]\nPOST /notes null\nPOST /notes 42\nGET /notes',
               '400 {"error":"invalid_json"}\n400 {"error":"invalid_json"}\n'
               '400 {"error":"invalid_json"}\n200 {"title":null}')],
             hints=["`JSON.parse` throws on malformed input. An uncaught throw in the handler becomes a 500.",
                    "Wrap the parse in try/catch and return 400 from the catch.",
                    "Then check the shape: `null`, arrays and numbers all parse fine but are not objects. Remember `typeof null === \"object\"`."]),
    ],
    quiz=[
        _q("Why is 500 the wrong status for malformed JSON?",
           ["500 is reserved for crashes", "It blames the server for the client's mistake, and hides a real signal",
            "400 is faster", "JSON errors are always the server's fault"],
           1,
           "A 500 means 'I have a bug'. Using it for bad input means your alerting can never tell real bugs from strangers typing nonsense."),
        _q("What does `typeof null` evaluate to?",
           ['"null"', '"undefined"', '"object"', '"boolean"'],
           2,
           "A long-standing JavaScript wart. It is why a null check has to be explicit before any typeof test for objects."),
    ],
)

_P3_S3 = _step(
    "patch",
    "PATCH: partial updates done properly",
    "PUT replaces. PATCH edits. Do not make one verb do both.",
    """
Project 2 established that `PUT` replaces the whole resource. That is correct,
and it is also inconvenient: a client that just wants to tick a note off has to
send the title back too, and a client with a stale copy will happily overwrite
someone else's edit. The answer is not to weaken PUT — it is to add **PATCH**.

`PATCH /notes/1 {"done": true}` means *"change only what I mention"*.

### Do this

```js
if (req.method === "PATCH") {
  const data = await readJson(req);

  if (Object.keys(data).length === 0) {
    return send(res, 400, { error: "empty_patch" });
  }

  const fields = validate(data, { partial: true });
  if (Object.keys(fields).length > 0) {
    return send(res, 400, { error: "validation_failed", fields });
  }

  const updated = { ...note };
  if (data.title !== undefined) updated.title = data.title.trim();
  if (data.done !== undefined) updated.done = data.done;
  notes.set(note.id, updated);
  return send(res, 200, updated);
}
```

And teach the validator to skip the required check when patching:

```js
function validate(data, { partial = false } = {}) {
  const fields = {};
  if (data.title === undefined) {
    if (!partial) fields.title = "title is required";
  } else if (…)
  …
}
```

### Three details that matter

- **`undefined` versus present.** Copy a field only when the client actually
  sent it. `updated.title = data.title` unconditionally would blank the title on
  `{"done": true}` — reintroducing the exact bug PATCH exists to avoid.
- **An empty patch is a client bug.** `PATCH /notes/1 {}` asks for nothing. It
  is harmless to allow, but rejecting it with 400 surfaces a broken client
  instead of silently doing nothing.
- **Copy unknown fields nowhere.** `{ ...note }` then explicit assignment means
  `{"admin": true}` in the body is ignored. If you had written
  `{ ...note, ...data }`, any key a client invents lands in your store —
  including ones your code later trusts. This is called mass assignment, and it
  has caused real breaches.

### PUT or PATCH?

| You want to… | Verb |
| --- | --- |
| Set the resource to exactly this | PUT |
| Change one or two fields | PATCH |
| Retry safely after a timeout | Either — both are idempotent |
| Create something new | POST |
""",
    """
- `PATCH /notes/1 {"done":true}` → 200, and the title is unchanged.
- `PATCH /notes/1 {"title":"New"}` → 200, and `done` is unchanged.
- `PATCH /notes/1 {}` → 400 `{"error":"empty_patch"}`.
- `PATCH /notes/1 {"done":"yes"}` → 400 with `fields.done` set.
- `PATCH /notes/1 {"admin":true}` does not put `admin` in the stored note.
""",
    pitfalls=[
        "`{ ...note, ...data }` copies every key the client invented straight into your store. Assign known fields explicitly.",
        "Assigning a field without checking for `undefined` turns a partial update back into a destructive one.",
        "Forgetting `partial: true` makes every PATCH without a title fail as 'title is required'.",
    ],
    exercises=[
        _ch("be3-patch", "Partial updates", "Medium",
            "Write the PATCH branch. `{\"done\":true}` changes only done; `{\"title\":\" New \"}` stores the trimmed title and leaves done alone; `{}` → 400 `{\"error\":\"empty_patch\"}`; a bad type → 400 `{\"error\":\"validation_failed\",\"fields\":{…}}`; unknown keys are ignored. Respond 200 with the updated note.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

function validate(data, { partial = false } = {}) {
  const fields = {};
  if (data.title === undefined) {
    if (!partial) fields.title = "title is required";
  } else if (typeof data.title !== "string" || data.title.trim() === "") {
    fields.title = "title must be a non-empty string";
  }
  if (data.done !== undefined && typeof data.done !== "boolean") {
    fields.done = "done must be true or false";
  }
  return fields;
}

const notes = new Map([[1, { id: 1, title: "Buy milk", done: false }]]);

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  const note = resource === "notes" ? notes.get(Number(rawId)) : undefined;
  if (!note) return send(res, 404, { error: "not_found" });
  if (req.method === "GET") return send(res, 200, note);
  if (req.method !== "PATCH") return send(res, 405, { error: "method_not_allowed" });

  const data = JSON.parse((await readBody(req)) || "{}");
  if (Object.keys(data).length === 0) return send(res, 400, { error: "empty_patch" });
  const fields = validate(data, { partial: true });
  if (Object.keys(fields).length > 0) {
    return send(res, 400, { error: "validation_failed", fields });
  }
  const updated = { ...note };
  if (data.title !== undefined) updated.title = data.title.trim();
  if (data.done !== undefined) updated.done = data.done;
  notes.set(note.id, updated);
  send(res, 200, updated);
}
"""),
            """  const data = JSON.parse((await readBody(req)) || "{}");
  if (Object.keys(data).length === 0) return send(res, 400, { error: "empty_patch" });
  const fields = validate(data, { partial: true });
  if (Object.keys(fields).length > 0) {
    return send(res, 400, { error: "validation_failed", fields });
  }
  const updated = { ...note };
  if (data.title !== undefined) updated.title = data.title.trim();
  if (data.done !== undefined) updated.done = data.done;
  notes.set(note.id, updated);
  send(res, 200, updated);""",
            [('PATCH /notes/1 {"done":true}\nPATCH /notes/1 {"title":"  Renamed  "}\nGET /notes/1',
              '200 {"id":1,"title":"Buy milk","done":true}\n'
              '200 {"id":1,"title":"Renamed","done":true}\n'
              '200 {"id":1,"title":"Renamed","done":true}'),
             ('PATCH /notes/1 {}\nPATCH /notes/1 {"done":"yes"}\nPATCH /notes/1 {"title":""}',
              '400 {"error":"empty_patch"}\n'
              '400 {"error":"validation_failed","fields":{"done":"done must be true or false"}}\n'
              '400 {"error":"validation_failed","fields":{"title":"title must be a non-empty string"}}'),
             ('PATCH /notes/1 {"admin":true}\nGET /notes/1\nPATCH /notes/9 {"done":true}',
              '200 {"id":1,"title":"Buy milk","done":false}\n'
              '200 {"id":1,"title":"Buy milk","done":false}\n'
              '404 {"error":"not_found"}')],
            hints=["Four gates before you touch the store: empty patch, validation, then copy, then save.",
                   "Copy the existing note first, then overwrite only the keys the client actually sent — check each against `undefined`.",
                   "The last test is the mass-assignment check: `{\"admin\":true}` is a non-empty patch that passes validation but must leave the note untouched, because you never copy unknown keys."]),
    ],
    quiz=[
        _q("Why is `{ ...note, ...data }` dangerous in a PATCH?",
           ["It is slow", "It copies any key the client invented into your stored object",
            "It loses the id", "Spread does not work on Maps"],
           1,
           "That is mass assignment. If any part of your system later trusts a field like `role` or `owner`, a client just set it."),
        _q("A client sends `PATCH /notes/1 {\"done\":true}` and your code runs `updated.title = data.title`. What happens?",
           ["Nothing — title is unchanged", "The title becomes undefined and disappears from the response",
            "It throws", "The title becomes null"],
           1,
           "`data.title` is undefined, and JSON.stringify drops undefined values entirely — so the field silently vanishes. Guard every assignment with an `undefined` check."),
    ],
)

_P3_S4 = _step(
    "status-choice",
    "Choosing the right failure",
    "400, 404, 409 — three different things a client can do about it.",
    """
You now have several ways to fail. Getting the choice right is what makes an API
pleasant, because the status tells the client **what to do next**.

| Situation | Status | What the client should do |
| --- | --- | --- |
| Body is not JSON | 400 `invalid_json` | Fix the serialiser |
| Field missing or wrong type | 400 `validation_failed` | Fix the input |
| `/notes/abc` — id is not a number | 400 `invalid_id` | Fix the URL |
| `/notes/999` — id is fine, note is gone | 404 `not_found` | Stop asking |
| Title already exists | 409 `duplicate_title` | Pick another title, or edit the existing note |
| Right path, wrong verb | 405 `method_not_allowed` | Use the right verb |

### 400 versus 404 on an id

`/notes/abc` and `/notes/999` are different failures. `abc` is **malformed** —
no note could ever have that id, so the request is wrong. `999` is
**well-formed but absent** — it may have existed yesterday. Saying so:

```js
function parseId(rawId) {
  return /^[1-9][0-9]*$/.test(rawId) ? Number(rawId) : null;
}

const id = parseId(rawId);
if (id === null) return send(res, 400, { error: "invalid_id" });
const note = notes.get(id);
if (!note) return send(res, 404, { error: "not_found" });
```

The regex rejects `abc`, `-1`, `1.5`, `01` and the empty string. Compare that
with `Number(rawId)`, which cheerfully accepts `" 12 "`, `"0x10"` and `""` (as
0) and returns `NaN` for the rest — a bug generator.

### 409 Conflict

409 means *the request is valid, but it clashes with the current state*. A
duplicate title is the classic case:

```js
const clash = [...notes.values()].some(
  (n) => n.id !== note?.id && n.title.toLowerCase() === title.toLowerCase()
);
if (clash) return send(res, 409, { error: "duplicate_title" });
```

Note `n.id !== note?.id` — when updating, a note is allowed to keep its own
title. Forgetting that exclusion makes every PUT of an unchanged note fail,
which is a genuinely baffling bug from the client's side.

### The habit

Before writing any failure response, ask: **whose fault, and what should they do
about it?** The status falls out of the answer, and the code in the body names
the specific case. Get in the habit now, while there are six of them, rather
than later when there are sixty.
""",
    """
- `GET /notes/abc` → 400 `{"error":"invalid_id"}`.
- `GET /notes/999` → 404 `{"error":"not_found"}`.
- Creating a note whose title already exists → 409 `{"error":"duplicate_title"}`.
- Renaming a note to its own current title still succeeds.
""",
    pitfalls=[
        "`Number(\"\")` is 0 and `Number(\" 12 \")` is 12 — `Number()` alone is not id validation.",
        "A duplicate check that does not exclude the note being updated makes every no-op update fail with 409.",
        "Case-sensitive duplicate checks let \"Buy Milk\" and \"buy milk\" both through, which users read as a bug.",
    ],
    warmup=[
        _q("`GET /notes/abc`. Which status is most useful to the client?",
           ["404 — there is no such note", "400 — that is not a valid id at all",
            "500 — Number(\"abc\") is NaN", "204 — nothing to return"],
           1,
           "No note could ever have the id `abc`, so the request itself is malformed. 404 would suggest it might exist later and invite a retry."),
    ],
    exercises=[
        _ch("be3-status-choice", "Pick the right failure", "Medium",
            "Write the guards for `POST /notes` and `GET /notes/:id`. Non-numeric id → 400 `{\"error\":\"invalid_id\"}`. Valid id, no note → 404 `{\"error\":\"not_found\"}`. POST with a title that already exists (ignoring case) → 409 `{\"error\":\"duplicate_title\"}`. POST with a missing title → 400 `{\"error\":\"validation_failed\",\"fields\":{\"title\":\"title is required\"}}`. Otherwise create with 201.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

const notes = new Map();
let nextId = 1;

function parseId(rawId) {
  return /^[1-9][0-9]*$/.test(rawId) ? Number(rawId) : null;
}

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  if (rawId === undefined) {
    if (req.method !== "POST") return send(res, 405, { error: "method_not_allowed" });
    const data = JSON.parse((await readBody(req)) || "{}");
    if (typeof data.title !== "string" || data.title.trim() === "") {
      return send(res, 400, {
        error: "validation_failed",
        fields: { title: "title is required" },
      });
    }
    const title = data.title.trim();
    const clash = [...notes.values()].some(
      (n) => n.title.toLowerCase() === title.toLowerCase()
    );
    if (clash) return send(res, 409, { error: "duplicate_title" });
    const note = { id: nextId++, title, done: false };
    notes.set(note.id, note);
    return send(res, 201, note);
  }

  const id = parseId(rawId);
  if (id === null) return send(res, 400, { error: "invalid_id" });
  const note = notes.get(id);
  if (!note) return send(res, 404, { error: "not_found" });
  send(res, 200, note);
}
"""),
            """  if (rawId === undefined) {
    if (req.method !== "POST") return send(res, 405, { error: "method_not_allowed" });
    const data = JSON.parse((await readBody(req)) || "{}");
    if (typeof data.title !== "string" || data.title.trim() === "") {
      return send(res, 400, {
        error: "validation_failed",
        fields: { title: "title is required" },
      });
    }
    const title = data.title.trim();
    const clash = [...notes.values()].some(
      (n) => n.title.toLowerCase() === title.toLowerCase()
    );
    if (clash) return send(res, 409, { error: "duplicate_title" });
    const note = { id: nextId++, title, done: false };
    notes.set(note.id, note);
    return send(res, 201, note);
  }

  const id = parseId(rawId);
  if (id === null) return send(res, 400, { error: "invalid_id" });
  const note = notes.get(id);
  if (!note) return send(res, 404, { error: "not_found" });
  send(res, 200, note);""",
            [('POST /notes {"title":"Buy milk"}\nPOST /notes {"title":"buy MILK"}\nPOST /notes {}',
              '201 {"id":1,"title":"Buy milk","done":false}\n'
              '409 {"error":"duplicate_title"}\n'
              '400 {"error":"validation_failed","fields":{"title":"title is required"}}'),
             ('GET /notes/abc\nGET /notes/999\nGET /notes/-1\nGET /notes/1.5',
              '400 {"error":"invalid_id"}\n404 {"error":"not_found"}\n'
              '400 {"error":"invalid_id"}\n400 {"error":"invalid_id"}'),
             ('POST /notes {"title":"  Spaced  "}\nGET /notes/1\nPOST /notes {"title":"Spaced"}',
              '201 {"id":1,"title":"Spaced","done":false}\n'
              '200 {"id":1,"title":"Spaced","done":false}\n'
              '409 {"error":"duplicate_title"}')],
            hints=["Two branches: `rawId === undefined` is the collection (POST), otherwise it is an item (GET).",
                   "Validate the id BEFORE looking it up — `parseId` returning null is a 400, a missing note is a 404.",
                   "Store the trimmed title, and compare titles lowercased so the duplicate check is not fooled by capitalisation."]),
    ],
    quiz=[
        _q("What does 409 Conflict mean?",
           ["The server is overloaded", "The request is valid but clashes with the current state",
            "Two clients sent requests at once", "The URL is wrong"],
           1,
           "409 says: nothing is wrong with your request in isolation — it just cannot be reconciled with what is here now."),
        _q("Why exclude the note being updated from a duplicate-title check?",
           ["To make it faster", "Otherwise a note conflicts with itself and no update can ever succeed",
            "Because ids are unique", "It is not necessary"],
           1,
           "The note's own title is already in the store. Without the exclusion, re-saving an unchanged note returns 409 — a bug that looks like magic from the outside."),
    ],
)

_P3_FINAL = _ch(
    "be3-final", "The validated Notes API", "Medium",
    "Build the whole Project 3 server. Guards in order: id shape (400 `invalid_id`), note exists (404 `not_found`), JSON parses and is an object (400 `invalid_json`), fields valid (400 `validation_failed` + `fields`), no duplicate title ignoring case and excluding the note itself (409 `duplicate_title`). POST → 201; GET one/all → 200; PATCH partial → 200, with `{}` → 400 `empty_patch` and unknown keys ignored; DELETE → 204. Wrong verb on a real path → 405. Titles are stored trimmed.",
    _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

const notes = new Map();
let nextId = 1;

function parseId(rawId) {
  return /^[1-9][0-9]*$/.test(rawId) ? Number(rawId) : null;
}

function validate(data, { partial = false } = {}) {
  const fields = {};
  if (data.title === undefined) {
    if (!partial) fields.title = "title is required";
  } else if (typeof data.title !== "string" || data.title.trim() === "") {
    fields.title = "title must be a non-empty string";
  } else if (data.title.trim().length > 100) {
    fields.title = "title must be 100 characters or fewer";
  }
  if (data.done !== undefined && typeof data.done !== "boolean") {
    fields.done = "done must be true or false";
  }
  return fields;
}

function duplicate(title, selfId) {
  return [...notes.values()].some(
    (n) => n.id !== selfId && n.title.toLowerCase() === title.toLowerCase()
  );
}

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  let body;
  if (req.method === "POST" || req.method === "PATCH") {
    const raw = await readBody(req);
    try {
      body = raw ? JSON.parse(raw) : {};
    } catch {
      return send(res, 400, { error: "invalid_json" });
    }
    if (body === null || typeof body !== "object" || Array.isArray(body)) {
      return send(res, 400, { error: "invalid_json" });
    }
  }

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    if (req.method === "POST") {
      const fields = validate(body);
      if (Object.keys(fields).length > 0) {
        return send(res, 400, { error: "validation_failed", fields });
      }
      const title = body.title.trim();
      if (duplicate(title, null)) return send(res, 409, { error: "duplicate_title" });
      const note = { id: nextId++, title, done: body.done === true };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const id = parseId(rawId);
  if (id === null) return send(res, 400, { error: "invalid_id" });
  const note = notes.get(id);
  if (!note) return send(res, 404, { error: "not_found" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "DELETE") {
    notes.delete(id);
    return send(res, 204, null);
  }
  if (req.method === "PATCH") {
    if (Object.keys(body).length === 0) return send(res, 400, { error: "empty_patch" });
    const fields = validate(body, { partial: true });
    if (Object.keys(fields).length > 0) {
      return send(res, 400, { error: "validation_failed", fields });
    }
    const updated = { ...note };
    if (body.title !== undefined) {
      const title = body.title.trim();
      if (duplicate(title, id)) return send(res, 409, { error: "duplicate_title" });
      updated.title = title;
    }
    if (body.done !== undefined) updated.done = body.done;
    notes.set(id, updated);
    return send(res, 200, updated);
  }
  return send(res, 405, { error: "method_not_allowed" });
}
"""),
    """  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  let body;
  if (req.method === "POST" || req.method === "PATCH") {
    const raw = await readBody(req);
    try {
      body = raw ? JSON.parse(raw) : {};
    } catch {
      return send(res, 400, { error: "invalid_json" });
    }
    if (body === null || typeof body !== "object" || Array.isArray(body)) {
      return send(res, 400, { error: "invalid_json" });
    }
  }

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    if (req.method === "POST") {
      const fields = validate(body);
      if (Object.keys(fields).length > 0) {
        return send(res, 400, { error: "validation_failed", fields });
      }
      const title = body.title.trim();
      if (duplicate(title, null)) return send(res, 409, { error: "duplicate_title" });
      const note = { id: nextId++, title, done: body.done === true };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const id = parseId(rawId);
  if (id === null) return send(res, 400, { error: "invalid_id" });
  const note = notes.get(id);
  if (!note) return send(res, 404, { error: "not_found" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "DELETE") {
    notes.delete(id);
    return send(res, 204, null);
  }
  if (req.method === "PATCH") {
    if (Object.keys(body).length === 0) return send(res, 400, { error: "empty_patch" });
    const fields = validate(body, { partial: true });
    if (Object.keys(fields).length > 0) {
      return send(res, 400, { error: "validation_failed", fields });
    }
    const updated = { ...note };
    if (body.title !== undefined) {
      const title = body.title.trim();
      if (duplicate(title, id)) return send(res, 409, { error: "duplicate_title" });
      updated.title = title;
    }
    if (body.done !== undefined) updated.done = body.done;
    notes.set(id, updated);
    return send(res, 200, updated);
  }
  return send(res, 405, { error: "method_not_allowed" });""",
    [('POST /notes {"title":"  Buy milk  "}\nPOST /notes {"title":"BUY MILK"}\nPOST /notes {}\nPOST /notes {oops}',
      '201 {"id":1,"title":"Buy milk","done":false}\n'
      '409 {"error":"duplicate_title"}\n'
      '400 {"error":"validation_failed","fields":{"title":"title is required"}}\n'
      '400 {"error":"invalid_json"}'),
     ('POST /notes {"title":"A"}\nPATCH /notes/1 {"done":true}\nPATCH /notes/1 {}\nPATCH /notes/1 {"admin":true}\nGET /notes/1',
      '201 {"id":1,"title":"A","done":false}\n'
      '200 {"id":1,"title":"A","done":true}\n'
      '400 {"error":"empty_patch"}\n'
      '200 {"id":1,"title":"A","done":true}\n'
      '200 {"id":1,"title":"A","done":true}'),
     ('GET /notes/abc\nGET /notes/999\nPOST /notes {"title":"A"}\nPATCH /notes/1 {"title":"A"}\nPATCH /notes/1 {"done":"yes"}\nDELETE /notes/1\nGET /notes',
      '400 {"error":"invalid_id"}\n404 {"error":"not_found"}\n'
      '201 {"id":1,"title":"A","done":false}\n'
      '200 {"id":1,"title":"A","done":false}\n'
      '400 {"error":"validation_failed","fields":{"done":"done must be true or false"}}\n'
      '204\n200 []'),
     ('POST /notes {"title":"A"}\nPOST /notes {"title":"B"}\nPATCH /notes/2 {"title":"a"}\nPUT /notes/1 {"title":"x"}',
      '201 {"id":1,"title":"A","done":false}\n'
      '201 {"id":2,"title":"B","done":false}\n'
      '409 {"error":"duplicate_title"}\n'
      '405 {"error":"method_not_allowed"}')],
    hints=["Parse the body once, before routing — both POST and PATCH need it, and both need the same invalid_json answer.",
           "Order the item guards deliberately: invalid id (400) before missing note (404), because a malformed id can never identify a note.",
           "The fourth test has two traps: patching note 2 to note 1's title is a 409, but patching note 1 to its OWN title (third test) must succeed — that is what the `selfId` exclusion is for."])

_P3 = _project(
    "validation", 3,
    "Validation & Error Contracts",
    "Stop trusting the client, and fail in a way clients can act on.",
    "Core",
    "Reject bad input at the edge with one consistent error shape, add PATCH for partial updates, and pick the right status for every kind of failure.",
    "Every field you fail to validate becomes bad data you will migrate later, and every improvised error shape becomes a branch in someone's client code. Both are much cheaper to prevent than to fix.",
    150,
    ["first-server", "notes-crud"],
    ["validation", "error envelopes", "400 vs 404 vs 409", "PATCH", "mass assignment", "trust boundaries"],
    ["Write a pure validator that collects every error before responding",
     "Return one consistent error envelope from every failure path",
     "Turn a malformed body into a 400 instead of a 500",
     "Implement PATCH without reintroducing destructive updates",
     "Choose between 400, 404, 405 and 409 and justify the choice"],
    """
Project 2's API believes everything it is told. This one does not.

You will add a pure `validate` function, a single error envelope, a `PATCH`
endpoint for partial updates, and a deliberate answer to each kind of failure —
malformed JSON, a bad id, a missing field, a duplicate title, a wrong verb.

The theme underneath all of it is the **trust boundary**. Everything that
arrives over the network is a stranger's guess at what your API wants. The
validator is the one door in; past it, the rest of your code can finally assume
its data is well-formed.
""",
    [_ep("POST", "/notes", "Create, validated", '{"title":"Buy milk"}', '{"id":1,…}', "201 · 400 · 409"),
     _ep("GET", "/notes/:id", "Read one", "", '{"id":1,…}', "200 · 400 · 404"),
     _ep("PATCH", "/notes/:id", "Partial update", '{"done":true}', '{"id":1,…}', "200 · 400 · 404 · 409"),
     _ep("DELETE", "/notes/:id", "Delete", "", "(empty)", "204 · 400 · 404"),
     _ep("—", "any failure", "One error envelope", "", '{"error":"code","fields":{…}}', "4xx")],
    """
Same folder, same `server.js`. Keep project 2's version working before you
start changing it — if you break something here, you want to know it was this
change.

```
cd notes-api
node server.js
```

A quick way to send a deliberately broken body with curl:

```
curl -i -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" \\
  -d '{oops'
```
""",
    [_P3_S1, _P3_S2, _P3_S3, _P3_S4],
    final_build=_P3_FINAL,
    acceptance=[
        "`POST /notes {}` returns 400 with `{\"error\":\"validation_failed\",\"fields\":{\"title\":\"title is required\"}}`.",
        "A body with a bad title AND a bad `done` reports both fields in one response.",
        "`POST /notes` with a malformed body returns 400 `invalid_json`, and nothing prints a stack trace.",
        "A body that is `null`, a number or an array is rejected as `invalid_json`.",
        "Titles are stored trimmed — `\"  Buy milk  \"` comes back as `\"Buy milk\"`.",
        "`PATCH /notes/1 {\"done\":true}` leaves the title alone; `PATCH /notes/1 {}` returns 400 `empty_patch`.",
        "`PATCH /notes/1 {\"admin\":true}` does not add `admin` to the stored note.",
        "`GET /notes/abc` returns 400 `invalid_id`; `GET /notes/999` returns 404 `not_found`.",
        "Creating a note with an existing title (any capitalisation) returns 409; renaming a note to its own title does not.",
        "`validate` never references `req` or `res`.",
    ],
    manual_test="""
```
# a validation failure, with both fields reported
curl -i -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" -d '{"done":"yes"}'

# malformed JSON — must be 400, not 500
curl -i -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" -d '{oops'

# an array is valid JSON and an invalid note
curl -i -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" -d '[1,2]'

# trimming
curl -i -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" -d '{"title":"   Buy milk   "}'

# duplicate, ignoring case
curl -i -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" -d '{"title":"buy MILK"}'

# partial update, then a mass-assignment attempt
curl -i -X PATCH http://localhost:3000/notes/1 \\
  -H "Content-Type: application/json" -d '{"done":true}'
curl -i -X PATCH http://localhost:3000/notes/1 \\
  -H "Content-Type: application/json" -d '{"admin":true}'

# id shapes
curl -i http://localhost:3000/notes/abc      # 400
curl -i http://localhost:3000/notes/999      # 404
```

Watch your server's terminal while you run these. If a stack trace appears, an
error escaped that should have been translated into a status.
""",
    reference="""
import http from "node:http";

function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

/** Parse a JSON object body. Throws SyntaxError for anything that is not one. */
async function readJson(req) {
  const raw = await readBody(req);
  if (!raw) return {};
  const data = JSON.parse(raw);
  if (data === null || typeof data !== "object" || Array.isArray(data)) {
    throw new SyntaxError("body must be a JSON object");
  }
  return data;
}

// ---- store -----------------------------------------------------------------
const notes = new Map();
let nextId = 1;

// ---- validation (pure: no req, no res) -------------------------------------
function parseId(rawId) {
  return /^[1-9][0-9]*$/.test(rawId) ? Number(rawId) : null;
}

function validate(data, { partial = false } = {}) {
  const fields = {};
  if (data.title === undefined) {
    if (!partial) fields.title = "title is required";
  } else if (typeof data.title !== "string" || data.title.trim() === "") {
    fields.title = "title must be a non-empty string";
  } else if (data.title.trim().length > 100) {
    fields.title = "title must be 100 characters or fewer";
  }
  if (data.done !== undefined && typeof data.done !== "boolean") {
    fields.done = "done must be true or false";
  }
  return fields;
}

function duplicate(title, selfId) {
  return [...notes.values()].some(
    (n) => n.id !== selfId && n.title.toLowerCase() === title.toLowerCase()
  );
}

// ---- routes ----------------------------------------------------------------
async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  let body;
  if (req.method === "POST" || req.method === "PUT" || req.method === "PATCH") {
    try {
      body = await readJson(req);
    } catch {
      return send(res, 400, { error: "invalid_json" });
    }
  }

  // ---- collection ----------------------------------------------------------
  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    if (req.method === "POST") {
      const fields = validate(body);
      if (Object.keys(fields).length > 0) {
        return send(res, 400, { error: "validation_failed", fields });
      }
      const title = body.title.trim();
      if (duplicate(title, null)) return send(res, 409, { error: "duplicate_title" });
      const note = { id: nextId++, title, done: body.done === true };
      notes.set(note.id, note);
      res.writeHead(201, {
        "Content-Type": "application/json",
        Location: `/notes/${note.id}`,
      });
      return res.end(JSON.stringify(note));
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  // ---- item: malformed id, then missing note, then act ---------------------
  const id = parseId(rawId);
  if (id === null) return send(res, 400, { error: "invalid_id" });
  const note = notes.get(id);
  if (!note) return send(res, 404, { error: "not_found" });

  if (req.method === "GET") return send(res, 200, note);

  if (req.method === "PUT") {
    const fields = validate(body);
    if (Object.keys(fields).length > 0) {
      return send(res, 400, { error: "validation_failed", fields });
    }
    const title = body.title.trim();
    if (duplicate(title, id)) return send(res, 409, { error: "duplicate_title" });
    const updated = { id, title, done: body.done === true };
    notes.set(id, updated);
    return send(res, 200, updated);
  }

  if (req.method === "PATCH") {
    if (Object.keys(body).length === 0) return send(res, 400, { error: "empty_patch" });
    const fields = validate(body, { partial: true });
    if (Object.keys(fields).length > 0) {
      return send(res, 400, { error: "validation_failed", fields });
    }
    const updated = { ...note };
    if (body.title !== undefined) {
      const title = body.title.trim();
      if (duplicate(title, id)) return send(res, 409, { error: "duplicate_title" });
      updated.title = title;
    }
    if (body.done !== undefined) updated.done = body.done;
    notes.set(id, updated);
    return send(res, 200, updated);
  }

  if (req.method === "DELETE") {
    notes.delete(id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });
}

const server = http.createServer((req, res) => {
  Promise.resolve(handler(req, res)).catch((err) => {
    console.error(err);
    if (!res.headersSent) send(res, 500, { error: "server_error" });
  });
});
server.listen(3000, () => console.log("listening on http://localhost:3000"));
""",
    stretch=[
        "Reject unknown fields instead of ignoring them, with 400 and `fields: {colour: \"unknown field\"}`. Strict input is friendlier than it sounds — a typo'd field name currently vanishes silently.",
        "Add a `Retry-After` header to your 409s where it makes sense, and read what the spec says about it.",
        "Move the validator into `validate.js` and write a plain Node script that exercises it with twenty inputs. Being able to test it with no server running is the payoff for keeping it pure.",
        "Support `PUT` with an `If-Match` header so a stale client cannot clobber a newer edit. This is optimistic concurrency, and 412 is its status.",
    ],
    glossary=[
        _gloss("trust boundary", "The line where untrusted input becomes trusted data. Your validator IS that line."),
        _gloss("error envelope", "The fixed shape every failure response uses, so clients can parse errors without special cases."),
        _gloss("error code", "A short stable string like `validation_failed` that clients branch on. Not a sentence."),
        _gloss("PATCH", "Partial update: change only the fields mentioned. PUT replaces everything."),
        _gloss("mass assignment", "Copying a request body straight onto a stored object, letting a client set fields you never meant to expose."),
        _gloss("409 Conflict", "The request is valid but clashes with current state — a duplicate, or a stale version."),
        _gloss("idempotent", "Repeating the request changes nothing further. PUT, PATCH and DELETE are; POST is not."),
    ],
    cheatsheet="""
```js
// one envelope, every failure
{ "error": "validation_failed", "fields": { "title": "title is required" } }
{ "error": "not_found" }

// pure validator — collect, do not early-return
function validate(data, { partial = false } = {}) {
  const fields = {};
  if (data.title === undefined) { if (!partial) fields.title = "title is required"; }
  else if (typeof data.title !== "string" || data.title.trim() === "") { … }
  if (data.done !== undefined && typeof data.done !== "boolean") { … }
  return fields;                       // {} means valid
}

// a body is only a body if it is an OBJECT
if (data === null || typeof data !== "object" || Array.isArray(data)) → 400

// ids: shape first, existence second
/^[1-9][0-9]*$/.test(rawId) ? Number(rawId) : null   // null → 400 invalid_id
notes.get(id)                                        // undefined → 404 not_found

// PATCH: copy, then assign only what was sent
const updated = { ...note };
if (data.title !== undefined) updated.title = data.title.trim();
```

| Failure | Status | Code |
| --- | --- | --- |
| Unparseable body | 400 | `invalid_json` |
| Bad / missing field | 400 | `validation_failed` + `fields` |
| Id is not a number | 400 | `invalid_id` |
| Patch with no keys | 400 | `empty_patch` |
| No such note | 404 | `not_found` |
| Wrong verb | 405 | `method_not_allowed` |
| Title already taken | 409 | `duplicate_title` |
""",
    self_check=[
        "I can explain why the validator returns an object of errors instead of throwing on the first one.",
        "I know three bodies that parse as valid JSON but are not valid notes.",
        "I can state the difference between PUT and PATCH in one sentence.",
        "I know what mass assignment is and where my code prevents it.",
        "I can justify 400 for `/notes/abc` and 404 for `/notes/999`.",
    ],
    review=[
        _q("Which body would `JSON.parse` accept but your API must still reject?",
           ["{oops", '{"title":"ok"}', "[1,2]", "an empty body"],
           2,
           "Arrays are valid JSON. Parsing successfully says nothing about whether the shape is the one you wanted."),
        _q("Your validator returns on the first error it finds. What is the cost?",
           ["It is slower", "Clients fix one field, resubmit, and discover the next one",
            "It cannot detect type errors", "None — it is better"],
           1,
           "Round-tripping errors one at a time is a bad experience and makes form UIs impossible to do well."),
        _q("`PATCH /notes/1` with `{}`. Which is the most defensible response?",
           ["200 with the unchanged note", "400 empty_patch — the client asked for nothing",
            "204", "500"],
           1,
           "Both 200 and 400 are defensible; 400 surfaces a broken client instead of quietly succeeding. What matters is that you chose, and documented it."),
        _q("Why validate at the edge rather than inside the store?",
           ["The store is slower", "So everything past the validator can assume well-formed data",
            "Stores cannot throw", "It is not — validate everywhere"],
           1,
           "One door in means one place to reason about. Scattering checks through every layer means you can never be sure they are all present."),
    ],
    milestone="Your API now refuses bad input politely and predictably — the difference between a demo and something you could let a stranger use.",
)

_PROJECTS.append(_P3)


# ===========================================================================
# PROJECT 4 — Make It Survive a Restart
# ===========================================================================

_P4_S1 = _step(
    "store-module",
    "Pull the store out of the routes",
    "One module owns the data; the routes only translate HTTP.",
    """
Your handler currently does two unrelated jobs: it speaks HTTP (statuses,
headers, JSON) and it manages data (the Map, the id counter). While the data
lives in a Map, mixing them is merely untidy. The moment data lives on disk it
becomes unworkable — so separate them **first**, while the change is boring.

### Do this

1. Create `store.js` next to `server.js`:

   ```js
   const notes = new Map();
   let nextId = 1;

   export function list() {
     return [...notes.values()];
   }

   export function find(id) {
     return notes.get(id);
   }

   export function create({ title, done }) {
     const note = { id: nextId++, title, done: done === true };
     notes.set(note.id, note);
     return note;
   }

   export function replace(id, note) {
     notes.set(id, note);
     return note;
   }

   export function remove(id) {
     return notes.delete(id);
   }
   ```

2. Import it at the top of `server.js`:

   ```js
   import * as store from "./store.js";
   ```

   The `.js` extension is required — ES modules do not guess extensions the way
   CommonJS `require` did.

3. Replace every direct `notes.get(...)` / `notes.set(...)` in your routes with
   `store.find(...)` / `store.replace(...)`. When you are done, **`server.js`
   should not contain the word `Map`**, and `store.js` should not contain `req`,
   `res` or any status code. That mutual ignorance is the whole point.

### Why this is worth doing before persistence

The interface — `list`, `find`, `create`, `replace`, `remove` — says *what* you
can do with notes and says nothing about *where* they are. That is why the next
step can swap a Map for a file, and after that a file for a real database,
without your routes noticing. A layer that hides how something is stored is
usually called a **repository**, and this is the smallest honest version of one.

The second payoff is testability. `store.js` can be exercised by a plain script
with no server, no ports and no HTTP — which is why the drills for it are the
fastest ones in this whole track.

### A note about the drills

The judged exercises here are single files, so the store sits at the top of the
file behind a comment banner instead of in its own module. Everything else is
identical. In **your** project, use two real files — that is the version you
want to have written.
""",
    """
- `store.js` exists and exports list, find, create, replace and remove.
- `server.js` imports it and contains no `Map` and no `notes` variable.
- `store.js` contains no `req`, no `res` and no status codes.
- Everything from project 3 still works exactly as before.
""",
    pitfalls=[
        "`import * as store from \"./store\"` fails in ES modules — the `.js` extension is mandatory.",
        "Leaking the Map out of the module (`export const notes`) undoes the whole point: callers go back to reaching in directly.",
        "Returning the stored object by reference lets a route mutate the store without going through it. Fine here; something to know once concurrency is real.",
    ],
    warmup=[
        _q("After the refactor, which of these belongs in store.js?",
           ['send(res, 404, { error: "not_found" })', "function find(id) { return notes.get(id); }",
            'new URL(req.url, "http://localhost")', "the 405 method check"],
           1,
           "The store knows about notes and nothing else. Statuses, URLs and responses are HTTP concerns and stay in server.js."),
    ],
    exercises=[
        _ex("be4-store-api", "A store with a real interface",
            "Finish `create` so it assigns the next id, normalises `done` to a boolean, stores the note and returns it.",
            _store_prog("""
// ---- store.js (in your project this is its own module) ---------------------
const notes = new Map();
let nextId = 1;

function list() {
  return [...notes.values()];
}

function find(id) {
  return notes.get(id);
}

function create(title) {
  const note = { id: nextId++, title, done: false };
  notes.set(note.id, note);
  return note;
}

function remove(id) {
  return notes.delete(id);
}
"""),
            """function create(title) {
  const note = { id: nextId++, title, done: false };
  notes.set(note.id, note);
  return note;
}""",
            [("CREATE Buy milk\nCREATE Walk dog\nFIND 2\nREMOVE 1\nLIST",
              '{"id":1,"title":"Buy milk","done":false}\n'
              '{"id":2,"title":"Walk dog","done":false}\n'
              '{"id":2,"title":"Walk dog","done":false}\n'
              'true\n'
              '[{"id":2,"title":"Walk dog","done":false}]'),
             ("CREATE Only\nREMOVE 9\nFIND 9\nLIST",
              '{"id":1,"title":"Only","done":false}\nfalse\nnull\n'
              '[{"id":1,"title":"Only","done":false}]')],
            hints=["Three lines: build the note, put it in the Map, return it.",
                   "The id comes from the counter — `nextId++` yields the current value first.",
                   "Store it under `note.id` so `find(1)` can get it back."]),
    ],
    quiz=[
        _q("What is the main benefit of the store having a named interface?",
           ["It runs faster", "Where the data lives can change without the routes changing",
            "It uses less memory", "Maps require it"],
           1,
           "`find(id)` says what you want, not where it comes from. That is what lets the next step swap a Map for a file with no route changes."),
        _q("Which of these would break the separation?",
           ["store.create(data)", "store.list()",
            "export const notes = new Map()", "store.remove(id)"],
           2,
           "Exporting the Map lets callers bypass the interface entirely, and every guarantee the module wanted to make evaporates."),
    ],
)

_P4_S2 = _step(
    "save-and-load",
    "Load at boot, save on every change",
    "The simplest persistence that actually works: one JSON file.",
    """
Time to make notes outlive the process. You are not reaching for a database
yet — a JSON file teaches every idea that matters (serialising, loading,
handling a missing file, keeping the counter) with none of the setup.

### Do this

1. At the top of `store.js`:

   ```js
   import fs from "node:fs";

   const FILE = "notes.json";
   let notes = new Map();
   let nextId = 1;
   ```

   `notes` becomes `let`, because `load()` replaces it wholesale.

2. Write the two halves:

   ```js
   function load() {
     try {
       const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
       notes = new Map(data.notes.map((n) => [n.id, n]));
       nextId = data.nextId;
     } catch {
       notes = new Map();
       nextId = 1;
     }
   }

   function save() {
     fs.writeFileSync(FILE, JSON.stringify({ notes: [...notes.values()], nextId }));
   }

   load();   // runs once, at import time
   ```

3. Call `save()` at the end of `create`, `replace` and `remove` — **every**
   function that changes something. Not in `list` or `find`; reads change
   nothing.

### The details that are actually the lesson

- **A Map does not survive `JSON.stringify`.** `JSON.stringify(new Map())` is
  `"{}"` — the entries are simply gone, with no error. Convert to an array on
  the way out and rebuild the Map on the way in. This bites everyone once.
- **Missing file is the normal first run.** The `catch` is not defensive
  paranoia; it is the path every new install takes. Note that the same catch
  also covers a corrupt file, which is a *very* different situation quietly
  handled the same way — worth a comment in real code.
- **Persist `nextId`, not just the notes.** Step 4 shows what happens when you
  forget.
- **`readFileSync` blocks the whole process.** At boot that is exactly what you
  want: nothing should serve requests before the data is loaded. Inside a
  request handler it would be a serious problem — Node has one thread for your
  code, and a blocking read stops every other request too. Booting is the one
  place a sync call is clearly right.

### Reading the file

Stop the server, look at `notes.json`, start it again:

```
node server.js         # create a couple of notes, then Ctrl+C
cat notes.json
node server.js         # your notes are still there
```

Seeing your data as plain text on disk is the moment persistence stops being
abstract.
""",
    """
- Create two notes, stop the server, and `notes.json` contains them.
- Start the server again and `GET /notes` returns both.
- Delete `notes.json`, start the server, and it comes up empty instead of crashing.
- `list` and `find` do not write to disk.
""",
    pitfalls=[
        "`JSON.stringify(map)` silently produces `{}`. Convert with `[...map.values()]` first.",
        "Forgetting to save inside `remove` means deleted notes come back on the next boot.",
        "Catching a missing file and a corrupt file with the same `catch` silently discards real data. Fine here; know that you are doing it.",
    ],
    warmup=[
        _q("`const m = new Map([[1, {id:1}]]); JSON.stringify({ notes: m })` produces what?",
           ['{"notes":[{"id":1}]}', '{"notes":{}}', '{"notes":{"1":{"id":1}}}', "It throws"],
           1,
           "JSON.stringify has no idea what a Map is and serialises its own enumerable properties — of which there are none. The data vanishes with no error, which is why this bug is so confusing the first time."),
    ],
    exercises=[
        _ex("be4-load", "Survive a restart",
            "Finish `load` so the saved notes come back as a Map keyed by id. `POST /_restart` reloads from disk — it stands in for stopping and starting the process, which the drill runner cannot do.",
            _server("""
const FILE = "notes.json";
let notes = new Map();
let nextId = 1;

function load() {
  try {
    const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
    notes = new Map(data.notes.map((n) => [n.id, n]));
    nextId = data.nextId;
  } catch {
    notes = new Map();
    nextId = 1;
  }
}

function save() {
  fs.writeFileSync(FILE, JSON.stringify({ notes: [...notes.values()], nextId }));
}

// Each drill run starts with no data file, so runs cannot contaminate each other.
try { fs.rmSync(FILE); } catch {}
load();

function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");

  // Given: stands in for stopping and restarting `node server.js`.
  if (resource === "_restart") {
    notes = new Map();   // a fresh process starts with nothing in memory,
    nextId = 1;          // so only what reached DISK can come back
    load();
    return send(res, 200, { restarted: true });
  }

  if (resource !== "notes") return send(res, 404, { error: "not_found" });
  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    const data = JSON.parse((await readBody(req)) || "{}");
    const note = { id: nextId++, title: data.title ?? null, done: false };
    notes.set(note.id, note);
    save();
    return send(res, 201, note);
  }
  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  send(res, 200, note);
}
"""),
            "    notes = new Map(data.notes.map((n) => [n.id, n]));",
            [('POST /notes {"title":"A"}\nPOST /_restart\nGET /notes',
              '201 {"id":1,"title":"A","done":false}\n'
              '200 {"restarted":true}\n'
              '200 [{"id":1,"title":"A","done":false}]'),
             ('POST /notes {"title":"A"}\nPOST /notes {"title":"B"}\nPOST /_restart\nGET /notes/2\nPOST /notes {"title":"C"}\nGET /notes',
              '201 {"id":1,"title":"A","done":false}\n'
              '201 {"id":2,"title":"B","done":false}\n'
              '200 {"restarted":true}\n'
              '200 {"id":2,"title":"B","done":false}\n'
              '201 {"id":3,"title":"C","done":false}\n'
              '200 [{"id":1,"title":"A","done":false},{"id":2,"title":"B","done":false},{"id":3,"title":"C","done":false}]')],
            hints=["`save()` writes `{ notes: [...], nextId }` — an ARRAY of notes, because a Map does not survive JSON.",
                   "So loading has to turn that array back into a Map.",
                   "`new Map()` accepts an array of `[key, value]` pairs: `data.notes.map((n) => [n.id, n])`."]),
    ],
    quiz=[
        _q("Why is `readFileSync` acceptable at boot but a problem inside a request handler?",
           ["It is slower in handlers", "Node runs your code on one thread — a blocking read at boot delays nothing, but in a handler it stalls every other request",
            "It is not allowed in handlers", "Handlers cannot import fs"],
           1,
           "Booting has nothing to block; a live server has everything to block. The single-threaded model is what makes the difference."),
        _q("Which store functions need to call `save()`?",
           ["All of them", "Only create", "create, replace and remove — the ones that change something", "Only remove"],
           2,
           "Writes persist; reads do not change anything, so saving on `list` would be pure overhead."),
    ],
)

_P4_S3 = _step(
    "save-everywhere",
    "The write you forgot",
    "Persistence is only as good as its least-covered mutation.",
    """
Adding `save()` to `create` feels like finishing the job. It is not: **every**
function that changes state needs it, and the one you forget will be discovered
by a user, not by you.

The failure is quiet in the worst way. Everything looks right while the process
is running, because the in-memory Map is correct. Only a restart reveals that
disk and memory disagreed — and by then you have lost the thread connecting
cause to effect.

### Do this

1. List every function in `store.js` that mutates: `create`, `replace`,
   `remove`. Confirm each one ends with `save()`.

2. Make the invariant hard to break rather than remembering it. One option is to
   funnel writes through a single helper:

   ```js
   function mutate(fn) {
     const result = fn();
     save();
     return result;
   }

   export const remove = (id) => mutate(() => notes.delete(id));
   ```

   Another is to save from one place at the end of each request. Either way, the
   goal is the same: **make it impossible to change data without persisting it.**
   A rule that relies on memory is a rule you will break.

### A word on durability

`fs.writeFileSync` is not atomic. If the process dies mid-write, `notes.json`
is left half-written, and your `load()` catch quietly turns that into an empty
store. The standard fix is **write-then-rename**:

```js
function save() {
  const tmp = FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
  fs.renameSync(tmp, FILE);   // atomic on the same filesystem
}
```

A rename within one filesystem either happens or does not — there is no state
where `notes.json` is half of each file. Adopt this now: it costs one line and
removes a whole class of data loss.

It is worth being honest about the limits, though. Rewriting the entire file on
every change is fine for hundreds of notes and hopeless for millions, and it
has no answer at all for two processes writing at once. Those limits are exactly
what a real database exists to solve. Knowing *why* you would reach for one
beats reaching for one reflexively.
""",
    """
- Create a note, delete it, restart the server: it stays deleted.
- Update a note, restart: the update survived.
- `save()` writes to a temp file and renames it.
- No mutating function can complete without persisting.
""",
    pitfalls=[
        "A missing `save()` is invisible until a restart — the running process looks perfectly correct.",
        "`writeFileSync` straight over the live file can leave it half-written if the process dies mid-write.",
        "`renameSync` is only atomic within one filesystem. A temp file in /tmp and a data file on another volume is a copy, not a rename.",
    ],
    exercises=[
        _fix("be4-forgot-save", "The delete that comes back",
             "Deleting a note works — until you restart, and there it is again. Find the missing write and fix it. (Use the atomic temp-file-then-rename form.)",
             _server("""
const FILE = "notes.json";
let notes = new Map();
let nextId = 1;

function load() {
  try {
    const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
    notes = new Map(data.notes.map((n) => [n.id, n]));
    nextId = data.nextId;
  } catch {
    notes = new Map();
    nextId = 1;
  }
}

function save() {
  const tmp = FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
  fs.renameSync(tmp, FILE);
}

try { fs.rmSync(FILE); } catch {}
load();

function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource === "_restart") {
    notes = new Map();   // a fresh process starts with nothing in memory,
    nextId = 1;          // so only what reached DISK can come back
    load();
    return send(res, 200, { restarted: true });
  }
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    const data = JSON.parse((await readBody(req)) || "{}");
    const note = { id: nextId++, title: data.title ?? null, done: false };
    notes.set(note.id, note);
    save();
    return send(res, 201, note);
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  if (req.method === "DELETE") {
    notes.delete(note.id);
    return send(res, 204, null);
  }
  send(res, 200, note);
}
"""),
             _server("""
const FILE = "notes.json";
let notes = new Map();
let nextId = 1;

function load() {
  try {
    const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
    notes = new Map(data.notes.map((n) => [n.id, n]));
    nextId = data.nextId;
  } catch {
    notes = new Map();
    nextId = 1;
  }
}

function save() {
  const tmp = FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
  fs.renameSync(tmp, FILE);
}

try { fs.rmSync(FILE); } catch {}
load();

function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource === "_restart") {
    notes = new Map();   // a fresh process starts with nothing in memory,
    nextId = 1;          // so only what reached DISK can come back
    load();
    return send(res, 200, { restarted: true });
  }
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    const data = JSON.parse((await readBody(req)) || "{}");
    const note = { id: nextId++, title: data.title ?? null, done: false };
    notes.set(note.id, note);
    save();
    return send(res, 201, note);
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  if (req.method === "DELETE") {
    notes.delete(note.id);
    save();
    return send(res, 204, null);
  }
  send(res, 200, note);
}
"""),
             [('POST /notes {"title":"A"}\nDELETE /notes/1\nGET /notes\nPOST /_restart\nGET /notes',
               '201 {"id":1,"title":"A","done":false}\n204\n200 []\n'
               '200 {"restarted":true}\n200 []'),
              ('POST /notes {"title":"A"}\nPOST /notes {"title":"B"}\nDELETE /notes/1\nPOST /_restart\nGET /notes',
               '201 {"id":1,"title":"A","done":false}\n'
               '201 {"id":2,"title":"B","done":false}\n204\n'
               '200 {"restarted":true}\n'
               '200 [{"id":2,"title":"B","done":false}]')],
             hints=["Look at what happens BEFORE the restart versus after. The delete works in memory.",
                    "Which functions change state? Which of them writes to disk?",
                    "The DELETE branch mutates the Map and returns without calling `save()`."]),
    ],
    quiz=[
        _q("Why is a missing `save()` such a hard bug to notice?",
           ["It throws only in production", "The running process is correct — only a restart reveals the disagreement",
            "It corrupts the file", "It only happens under load"],
           1,
           "Memory and disk drift apart silently. The symptom appears at restart, far from the code that caused it."),
        _q("What does write-to-temp-then-rename protect against?",
           ["Two processes writing at once", "A crash mid-write leaving a half-written data file",
            "Disk running out of space", "JSON parse errors"],
           1,
           "A rename within a filesystem is atomic: readers see either the old file or the new one, never half of either. It does NOT solve concurrent writers — that needs locking, or a database."),
    ],
)

_P4_S4 = _step(
    "ids-after-restart",
    "The id counter has to persist too",
    "Save the notes but not the counter, and your next note overwrites your first.",
    """
Here is a bug worth meeting deliberately, because it is subtle, it is silent,
and it destroys data.

Suppose you save the notes but not `nextId`. On restart, `load()` fills the Map
from disk — and `nextId` is still `1`, its initial value. The very next `POST`
creates a note with id 1 and calls `notes.set(1, …)`, **overwriting** the note
that was already there. No error, no warning. One note is simply gone, and the
API happily returns 201.

### Two ways to fix it

1. **Persist the counter** — what your `save()` already does:

   ```js
   fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
   ```

2. **Derive it on load** — belt and braces, and it repairs a file written by an
   older version of your code:

   ```js
   nextId = Math.max(0, ...data.notes.map((n) => n.id)) + 1;
   ```

   `Math.max(0, ...[])` is `0`, so an empty file gives `nextId = 1`. Spreading
   an empty array into `Math.max()` alone would give `-Infinity`, which is the
   kind of detail that turns a fix into a new bug.

Doing both is reasonable: persist it for correctness, derive it as a repair.

### Why real systems use UUIDs

A counter has to be shared. Two processes serving the same data cannot both hold
`nextId` in memory without eventually colliding, and there is no way to hand out
"the next id" without coordination. So production systems either let a database
own the sequence, or stop coordinating altogether:

```js
import crypto from "node:crypto";
const id = crypto.randomUUID();   // "3f2b9c40-..." — no shared state at all
```

Random ids are unguessable too, which matters: sequential ids leak how many
notes exist and let anyone walk `/notes/1`, `/notes/2`, `/notes/3` through your
whole dataset. (This track keeps counters purely so the expected output of a
drill can be written down.)

### Do this

1. Make sure `nextId` is in your saved JSON.
2. Add the `Math.max` derivation to `load()` as a repair.
3. Test it honestly: create two notes, stop the server, **hand-edit
   `notes.json`** to remove `nextId`, start again, and create a third note. With
   the derivation, it gets id 3. Without it, it silently destroys note 1.
""",
    """
- Create two notes, restart, create a third: it gets id 3, and the first two survive.
- Deleting `nextId` from notes.json by hand still yields correct ids on the next boot.
- With an empty or missing file, the first note gets id 1.
""",
    pitfalls=[
        "Saving only the notes array. The counter resets to 1 and the next create overwrites your oldest note — silently.",
        "`Math.max(...[])` is `-Infinity`. Always seed it: `Math.max(0, ...ids)`.",
        "Sequential ids let anyone enumerate your entire dataset by counting upwards.",
    ],
    warmup=[
        _q("Two notes are saved (ids 1 and 2), but `nextId` is not persisted. After a restart, what does the next POST do?",
           ["Creates id 3", "Creates id 1 and overwrites the existing note 1",
            "Throws a duplicate-id error", "Creates id 0"],
           1,
           "`nextId` is back to its initial 1, and `Map.set` overwrites without complaint. The response is a cheerful 201 for a create that destroyed data."),
    ],
    exercises=[
        _fix("be4-nextid", "The id that eats a note",
             "Notes survive a restart, but the id counter does not — so the first note created after a restart overwrites an old one. Fix `load` so the counter is restored from the saved value, and derive it from the notes as a repair when it is missing.",
             _server("""
const FILE = "notes.json";
let notes = new Map();
let nextId = 1;

function load() {
  try {
    const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
    notes = new Map(data.notes.map((n) => [n.id, n]));
  } catch {
    notes = new Map();
    nextId = 1;
  }
}

function save() {
  const tmp = FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
  fs.renameSync(tmp, FILE);
}

try { fs.rmSync(FILE); } catch {}
load();

function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const [, resource] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource === "_restart") {
    notes = new Map();   // a fresh process starts with nothing in memory,
    nextId = 1;          // so only what reached DISK can come back
    load();
    return send(res, 200, { restarted: true });
  }
  if (resource !== "notes") return send(res, 404, { error: "not_found" });
  if (req.method === "GET") return send(res, 200, [...notes.values()]);

  const data = JSON.parse((await readBody(req)) || "{}");
  const note = { id: nextId++, title: data.title ?? null, done: false };
  notes.set(note.id, note);
  save();
  send(res, 201, note);
}
"""),
             _server("""
const FILE = "notes.json";
let notes = new Map();
let nextId = 1;

function load() {
  try {
    const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
    notes = new Map(data.notes.map((n) => [n.id, n]));
    nextId = data.nextId ?? Math.max(0, ...data.notes.map((n) => n.id)) + 1;
  } catch {
    notes = new Map();
    nextId = 1;
  }
}

function save() {
  const tmp = FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
  fs.renameSync(tmp, FILE);
}

try { fs.rmSync(FILE); } catch {}
load();

function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const [, resource] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource === "_restart") {
    notes = new Map();   // a fresh process starts with nothing in memory,
    nextId = 1;          // so only what reached DISK can come back
    load();
    return send(res, 200, { restarted: true });
  }
  if (resource !== "notes") return send(res, 404, { error: "not_found" });
  if (req.method === "GET") return send(res, 200, [...notes.values()]);

  const data = JSON.parse((await readBody(req)) || "{}");
  const note = { id: nextId++, title: data.title ?? null, done: false };
  notes.set(note.id, note);
  save();
  send(res, 201, note);
}
"""),
             [('POST /notes {"title":"A"}\nPOST /notes {"title":"B"}\nPOST /_restart\nPOST /notes {"title":"C"}\nGET /notes',
               '201 {"id":1,"title":"A","done":false}\n'
               '201 {"id":2,"title":"B","done":false}\n'
               '200 {"restarted":true}\n'
               '201 {"id":3,"title":"C","done":false}\n'
               '200 [{"id":1,"title":"A","done":false},{"id":2,"title":"B","done":false},{"id":3,"title":"C","done":false}]'),
              ('POST /notes {"title":"A"}\nPOST /_restart\nPOST /_restart\nPOST /notes {"title":"B"}\nGET /notes',
               '201 {"id":1,"title":"A","done":false}\n'
               '200 {"restarted":true}\n200 {"restarted":true}\n'
               '201 {"id":2,"title":"B","done":false}\n'
               '200 [{"id":1,"title":"A","done":false},{"id":2,"title":"B","done":false}]')],
             hints=["`save()` already writes `nextId`. Look at what `load()` does with it.",
                    "The Map is restored but the counter is left at its initial value, so the next id collides with an existing note.",
                    "Restore it from the file, and fall back to `Math.max(0, ...ids) + 1` when the file has no counter — seed the max with 0 so an empty list gives 1, not -Infinity."]),
    ],
    quiz=[
        _q("Why seed `Math.max` with 0 when deriving the next id?",
           ["For readability", "`Math.max()` with no arguments is -Infinity, so an empty store would break",
            "Ids start at 0", "It is not necessary"],
           1,
           "`Math.max(...[])` is `-Infinity`, giving `nextId = -Infinity + 1`. The seed makes the empty case give 1."),
        _q("Why do production systems usually prefer UUIDs to a counter?",
           ["They are shorter", "No shared state is needed, and they cannot be enumerated",
            "They sort better", "JSON handles them better"],
           1,
           "A counter needs coordination between every writer. UUIDs need none, and they do not leak your record count or let anyone walk /notes/1, /notes/2, /notes/3."),
    ],
)

_P4_FINAL = _ch(
    "be4-final", "The persistent Notes API", "Medium",
    "Build a Notes API whose data survives a restart. Keep notes and `nextId` in one JSON file, load at boot (an absent file means an empty store), and save after every change — create, replace and delete. `POST /notes` → 201; `GET /notes` → 200 array; `GET /notes/:id` → 200 or 404; `DELETE /notes/:id` → 204 or 404. The given `POST /_restart` stands in for restarting the process: after it, everything saved must come back, including the counter.",
    _server("""
const FILE = "notes.json";
let notes = new Map();
let nextId = 1;

function load() {
  try {
    const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
    notes = new Map(data.notes.map((n) => [n.id, n]));
    nextId = data.nextId ?? Math.max(0, ...data.notes.map((n) => n.id)) + 1;
  } catch {
    notes = new Map();
    nextId = 1;
  }
}

function save() {
  const tmp = FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
  fs.renameSync(tmp, FILE);
}

try { fs.rmSync(FILE); } catch {}
load();

function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource === "_restart") {
    notes = new Map();   // a fresh process starts with nothing in memory,
    nextId = 1;          // so only what reached DISK can come back
    load();
    return send(res, 200, { restarted: true });
  }
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, [...notes.values()]);
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = { id: nextId++, title: data.title ?? null, done: false };
      notes.set(note.id, note);
      save();
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "DELETE") {
    notes.delete(note.id);
    save();
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });
}
"""),
    """function load() {
  try {
    const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
    notes = new Map(data.notes.map((n) => [n.id, n]));
    nextId = data.nextId ?? Math.max(0, ...data.notes.map((n) => n.id)) + 1;
  } catch {
    notes = new Map();
    nextId = 1;
  }
}

function save() {
  const tmp = FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
  fs.renameSync(tmp, FILE);
}""",
    [('GET /notes\nPOST /notes {"title":"A"}\nPOST /_restart\nGET /notes',
      '200 []\n201 {"id":1,"title":"A","done":false}\n'
      '200 {"restarted":true}\n200 [{"id":1,"title":"A","done":false}]'),
     ('POST /notes {"title":"A"}\nPOST /notes {"title":"B"}\nDELETE /notes/1\nPOST /_restart\nGET /notes\nPOST /notes {"title":"C"}',
      '201 {"id":1,"title":"A","done":false}\n'
      '201 {"id":2,"title":"B","done":false}\n204\n'
      '200 {"restarted":true}\n'
      '200 [{"id":2,"title":"B","done":false}]\n'
      '201 {"id":3,"title":"C","done":false}'),
     ('POST /notes {"title":"A"}\nPOST /_restart\nGET /notes/1\nGET /notes/9\nDELETE /notes/9\nPUT /notes/1',
      '201 {"id":1,"title":"A","done":false}\n'
      '200 {"restarted":true}\n'
      '200 {"id":1,"title":"A","done":false}\n'
      '404 {"error":"not_found"}\n404 {"error":"not_found"}\n'
      '405 {"error":"method_not_allowed"}')],
    hints=["`save` must write BOTH the notes array and `nextId` — a Map cannot be JSON.stringify'd, and a lost counter overwrites old notes.",
           "`load` rebuilds the Map from the array and restores the counter; a missing or unreadable file is the normal first run, so the catch resets to empty.",
           "Second test: the counter must survive the restart, so the note created after it gets id 3 even though only one note remains."])

_P4 = _project(
    "persistence", 4,
    "Make It Survive a Restart",
    "A store module, a JSON file on disk, and the writes people forget.",
    "Core",
    "Separate storage from routing, then give the store a file so notes outlive the process — including the id counter.",
    "An API that forgets everything on restart is a demo. The step from demo to service is smaller than it looks, and every part of it is a lesson you will reuse against a real database.",
    150,
    ["first-server", "notes-crud", "validation"],
    ["repository layer", "node:fs", "serialisation", "atomic writes", "durability", "id generation"],
    ["Separate a store module from the routes and keep them mutually ignorant",
     "Serialise a Map to JSON and rebuild it on load",
     "Handle a missing data file as the normal first run",
     "Save on every mutation, and make that hard to forget",
     "Explain why the id counter must persist, and what UUIDs solve"],
    """
Everything so far disappears when you press `Ctrl+C`. In this project it stops
doing that.

You will first pull the data out of the handler into a `store.js` module with a
named interface, then give that module a JSON file: load at boot, save on every
change, write atomically. Along the way you will meet three bugs that are worth
meeting on purpose — a Map that vanishes through `JSON.stringify`, a delete that
never reaches disk, and an id counter that resets and eats your oldest note.

The drills use a `POST /_restart` endpoint that **throws away everything in
memory** — the Map and the id counter — and then calls `load()`. It stands in
for stopping and starting `node server.js`, which a drill runner cannot do, and
it is faithful in the way that matters: after it, only what reached **disk**
comes back. In your own project, use the real thing: `Ctrl+C`, then `node
server.js` again.
""",
    [_ep("POST", "/notes", "Create and persist", '{"title":"Buy milk"}', '{"id":1,…}', "201"),
     _ep("GET", "/notes", "List from the loaded store", "", "[…]", "200"),
     _ep("GET", "/notes/:id", "Read one", "", '{"id":1,…}', "200 · 404"),
     _ep("DELETE", "/notes/:id", "Delete and persist", "", "(empty)", "204 · 404"),
     _ep("POST", "/_restart", "Drills only: reload from disk", "", '{"restarted":true}', "200")],
    """
Same folder. This project adds a second source file:

```
notes-api/
  server.js     routes and HTTP
  store.js      data, and where it lives
  notes.json    created on first save — do not commit it
```

```
cd notes-api
node server.js
```

If you are using git here, add `notes.json` to `.gitignore`. Committing your
development data is a habit worth not forming.
""",
    [_P4_S1, _P4_S2, _P4_S3, _P4_S4],
    final_build=_P4_FINAL,
    acceptance=[
        "`store.js` exports list, find, create, replace and remove, and mentions neither `req` nor `res`.",
        "`server.js` contains no `Map` and no direct file access.",
        "Creating notes, stopping the server and starting it again returns the same notes.",
        "Deleting a note and restarting leaves it deleted.",
        "Deleting `notes.json` and starting the server yields an empty store, not a crash.",
        "`notes.json` contains both the notes array and `nextId`.",
        "After a restart, a new note gets the next unused id — no note is ever overwritten.",
        "`save()` writes a temp file and renames it over the real one.",
        "`list` and `find` never write to disk.",
    ],
    manual_test="""
```
node server.js

curl -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" -d '{"title":"Survives"}'
curl -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" -d '{"title":"Also survives"}'

# Ctrl+C, then look at the file
cat notes.json

# start again — the notes are still there
node server.js
curl http://localhost:3000/notes

# delete one, restart, confirm it stays gone
curl -X DELETE http://localhost:3000/notes/1
# Ctrl+C; node server.js
curl http://localhost:3000/notes

# the counter test: create a third note — it must NOT reuse id 1 or 2
curl -X POST http://localhost:3000/notes \\
  -H "Content-Type: application/json" -d '{"title":"Third"}'

# the first-run test
# Ctrl+C; rm notes.json; node server.js
curl http://localhost:3000/notes        # []
```

Then do the honest version of the counter test: stop the server, open
`notes.json` in an editor, delete the `nextId` field, save, restart, and create
a note. With the `Math.max` repair it gets the right id; without it, it destroys
your oldest note.
""",
    reference="""
// ---------------------------------------------------------------- store.js --
import fs from "node:fs";

const FILE = "notes.json";
let notes = new Map();
let nextId = 1;

function load() {
  try {
    const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
    notes = new Map(data.notes.map((n) => [n.id, n]));
    // Prefer the saved counter; derive it as a repair for older/edited files.
    nextId = data.nextId ?? Math.max(0, ...data.notes.map((n) => n.id)) + 1;
  } catch {
    // Missing file is the normal first run. (A corrupt file lands here too —
    // in a real service you would want those two cases to differ.)
    notes = new Map();
    nextId = 1;
  }
}

function save() {
  const tmp = FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
  fs.renameSync(tmp, FILE);   // atomic within one filesystem
}

load();

export const list = () => [...notes.values()];
export const find = (id) => notes.get(id);

export function create({ title, done }) {
  const note = { id: nextId++, title: title ?? null, done: done === true };
  notes.set(note.id, note);
  save();
  return note;
}

export function replace(id, note) {
  notes.set(id, note);
  save();
  return note;
}

export function remove(id) {
  const existed = notes.delete(id);
  if (existed) save();
  return existed;
}

// --------------------------------------------------------------- server.js --
import http from "node:http";
import * as store from "./store.js";

function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  if (rawId === undefined) {
    if (req.method === "GET") return send(res, 200, store.list());
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      return send(res, 201, store.create(data));
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = store.find(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "PUT") {
    const data = JSON.parse((await readBody(req)) || "{}");
    return send(res, 200, store.replace(note.id, {
      id: note.id, title: data.title ?? null, done: data.done === true,
    }));
  }
  if (req.method === "DELETE") {
    store.remove(note.id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });
}

const server = http.createServer((req, res) => {
  Promise.resolve(handler(req, res)).catch((err) => {
    console.error(err);
    if (!res.headersSent) send(res, 500, { error: "server_error" });
  });
});
server.listen(3000, () => console.log("listening on http://localhost:3000"));
""",
    stretch=[
        "Switch ids to `crypto.randomUUID()`. Notice what breaks: every hard-coded `/notes/1` in your notes and tests. That pain is the argument for not hard-coding ids in tests.",
        "Debounce saving — write at most once every 200 ms instead of on every mutation — and then reason carefully about what a crash inside that window costs you.",
        "Add a `GET /notes/export` that streams the file with `Content-Disposition: attachment`.",
        "Swap the JSON file for `node:sqlite`. Because every route goes through the store interface, only store.js should change — which is the whole point of project 4's first step.",
    ],
    glossary=[
        _gloss("repository", "A module that hides where data lives behind a named interface, so callers never learn the difference between a Map, a file and a database."),
        _gloss("serialisation", "Turning in-memory values into text you can store. A Map does not survive it; an array of entries does."),
        _gloss("durability", "The guarantee that a write survives a crash. Write-then-rename is the cheap version."),
        _gloss("atomic write", "A write that either fully happens or not at all. `renameSync` over an existing file is atomic within a filesystem."),
        _gloss("blocking call", "Work that stops the single thread running your code. Fine at boot; ruinous inside a request handler."),
        _gloss("UUID", "A random 128-bit id. Needs no coordination between writers and cannot be enumerated by counting."),
    ],
    cheatsheet="""
```js
import fs from "node:fs";

// load — a missing file is the NORMAL first run
function load() {
  try {
    const data = JSON.parse(fs.readFileSync(FILE, "utf8"));
    notes = new Map(data.notes.map((n) => [n.id, n]));       // array → Map
    nextId = data.nextId ?? Math.max(0, ...data.notes.map((n) => n.id)) + 1;
  } catch {
    notes = new Map();
    nextId = 1;
  }
}

// save — atomically, and on EVERY mutation
function save() {
  const tmp = FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ notes: [...notes.values()], nextId }));
  fs.renameSync(tmp, FILE);
}
```

| Trap | Symptom |
| --- | --- |
| `JSON.stringify(map)` | `{}` — data gone, no error |
| No `save()` in remove | Deleted notes return after a restart |
| `nextId` not persisted | Next create silently overwrites note 1 |
| `Math.max(...[])` | `-Infinity` |
| `readFileSync` in a handler | Every other request stalls |
""",
    self_check=[
        "I can explain what `JSON.stringify` does to a Map and why.",
        "I know which of my store functions write to disk and why the others must not.",
        "I can say what write-then-rename protects against, and what it does not.",
        "I can describe exactly how a lost id counter destroys data.",
        "I could swap the JSON file for a database by changing one file.",
    ],
    review=[
        _q("`load()` catches an error and starts empty. Which two very different situations does that treat identically?",
           ["A missing file and a permissions error", "A missing file and a corrupt file",
            "An empty file and a large file", "A locked file and a slow disk"],
           1,
           "First run and data corruption both land in the same catch. Silently discarding real data is a much bigger deal than starting fresh, and a real service distinguishes them."),
        _q("Where should `save()` be called?",
           ["Once at process exit", "In every function that mutates state",
            "In every function, including reads", "Once per second on a timer"],
           1,
           "Exit handlers do not run on a hard kill, and timers lose the last window of writes. Saving on mutation is the only version with no data-loss story to explain."),
        _q("What does the store interface buy you when you later move to SQLite?",
           ["Faster queries", "Only store.js changes — the routes are untouched",
            "Automatic migrations", "Nothing"],
           1,
           "That insulation is exactly why step 1 came before step 2."),
        _q("Why does `Math.max(0, ...ids) + 1` need the 0?",
           ["To make ids start at 1", "Because `Math.max()` with no arguments is -Infinity",
            "To skip id 0", "It does not"],
           1,
           "The empty-store case would otherwise produce `-Infinity + 1`, and every id after that would be nonsense."),
    ],
    milestone="Your API has a memory. Stop it, start it, and everything is where you left it.",
)

_PROJECTS.append(_P4)


# ===========================================================================
# PROJECT 5 — Search, Filter, Sort, Paginate
# ===========================================================================

_QUERY_DRIVER = """
// ---- query driver (given — don't edit) -------------------------------------
// stdin: one query string per line (no leading "?"). Use "-" for an empty one.
for (const line of fs.readFileSync(0, "utf8").split("\\n")) {
  const text = line.trim();
  if (!text) continue;
  const params = new URLSearchParams(text === "-" ? "" : text);
  console.log(JSON.stringify(parseQuery(params)));
}
"""


def _query_prog(code):
    return 'import fs from "node:fs";\n\n' + _bp(code) + "\n" + _bp(_QUERY_DRIVER)


_SEED_NOTES = """
const notes = new Map([
  [1, { id: 1, title: "Buy milk", done: false }],
  [2, { id: 2, title: "Walk dog", done: true }],
  [3, { id: 3, title: "Buy bread", done: false }],
]);
"""

_P5_S1 = _step(
    "parse-query",
    "Parse the query string defensively",
    "Six parameters, all strings, all written by a stranger.",
    """
`GET /notes` returning every note works right up until there are ten thousand of
them. The fix is a **query interface**: search, filter, sort and paginate. All
four arrive as query parameters, which means all four arrive as **strings you
did not write**.

### The parameters

| Parameter | Example | Default | Rule |
| --- | --- | --- | --- |
| `q` | `q=milk` | `""` | case-insensitive substring of the title |
| `done` | `done=true` | none | `true` / `false`; anything else is ignored |
| `sort` | `sort=title` | `id` | one of `id`, `title`, `done` — **whitelisted** |
| `order` | `order=desc` | `asc` | `desc` or `asc` |
| `limit` | `limit=20` | `10` | 1…50; clamped, never trusted |
| `offset` | `offset=40` | `0` | ≥ 0 |

### Do this

Write one pure function that turns raw parameters into settled options. Nothing
downstream should ever touch `searchParams` again:

```js
const SORTS = ["id", "title", "done"];

function parseQuery(params) {
  const rawLimit = Number(params.get("limit"));
  const rawOffset = Number(params.get("offset"));
  const sort = params.get("sort");
  const done = params.get("done");

  return {
    q: (params.get("q") ?? "").trim().toLowerCase(),
    done: done === null ? null : done === "true",
    sort: SORTS.includes(sort) ? sort : "id",
    order: params.get("order") === "desc" ? "desc" : "asc",
    limit: Number.isInteger(rawLimit) && rawLimit > 0 ? Math.min(rawLimit, 50) : 10,
    offset: Number.isInteger(rawOffset) && rawOffset >= 0 ? rawOffset : 0,
  };
}
```

### Why each line is written that way

- **`done === null ? null : done === "true"`** — three states, not two. Absent
  means *do not filter*; `true` and `false` are both real filters. Collapsing
  absent and false is the single most common bug in list endpoints.
- **`SORTS.includes(sort)`** — a whitelist, not a sanitiser. Anything not on the
  list becomes the default. Passing a client-supplied string to `a[sort]` lets a
  caller sort by any property that happens to exist; hand the same string to a
  database and you have SQL injection.
- **`Math.min(rawLimit, 50)`** — clamping is not politeness, it is protection.
  Without a ceiling, `?limit=10000000` is a denial-of-service request that your
  own code carries out enthusiastically.
- **`Number.isInteger`** — `Number("abc")` is `NaN`, `Number("2.5")` is `2.5`
  and `Number("")` is `0`. Only integers survive; everything else takes the
  default rather than producing `slice(NaN, NaN)`, which silently returns
  nothing.
- **`.trim().toLowerCase()` once, here** — normalise at the boundary so the
  filter downstream is a plain `includes`, and reject nothing for having a
  trailing space.

### Reject or default?

This parser **defaults** on bad input: `?limit=abc` quietly becomes 10. The
alternative is to return 400 `invalid_query`. Both are defensible — defaulting
is forgiving, rejecting is honest — and the only wrong answer is doing one for
some parameters and the other for the rest without noticing. Pick one, write it
down, apply it everywhere.
""",
    """
- `parseQuery` on an empty query gives `{q:"", done:null, sort:"id", order:"asc", limit:10, offset:0}`.
- `?limit=999` gives 50; `?limit=abc` gives 10; `?offset=-3` gives 0.
- `?sort=whatever` falls back to `id`.
- `?done=false` gives `done: false`, and no `done` at all gives `null`.
""",
    pitfalls=[
        "Treating a missing `done` the same as `done=false` — the filter then hides every completed note by default.",
        "No ceiling on `limit` turns one request into a full table scan you paid for.",
        "`Number(\"\")` is 0 and `Number(\"2.5\")` is 2.5. `Number.isInteger` is what actually filters those out.",
        "Interpolating a client-supplied `sort` into a query is how SQL injection gets in. Whitelist.",
    ],
    warmup=[
        _q("`?limit=abc&offset=-5` with the parser above. What comes out?",
           ["limit NaN, offset -5", "limit 10, offset 0", "A 400 response", "limit 0, offset 0"],
           1,
           "`Number(\"abc\")` is NaN so it fails Number.isInteger, and -5 fails the `>= 0` test. Both fall back to their defaults rather than producing a nonsensical slice."),
    ],
    exercises=[
        _ex("be5-parse-query", "Settle the options once",
            "Finish `parseQuery`: `limit` must be a positive integer, capped at 50, and default to 10 when it is missing or unusable.",
            _query_prog("""
const SORTS = ["id", "title", "done"];

function parseQuery(params) {
  const rawLimit = Number(params.get("limit"));
  const rawOffset = Number(params.get("offset"));
  const sort = params.get("sort");
  const done = params.get("done");

  return {
    q: (params.get("q") ?? "").trim().toLowerCase(),
    done: done === null ? null : done === "true",
    sort: SORTS.includes(sort) ? sort : "id",
    order: params.get("order") === "desc" ? "desc" : "asc",
    limit: Number.isInteger(rawLimit) && rawLimit > 0 ? Math.min(rawLimit, 50) : 10,
    offset: Number.isInteger(rawOffset) && rawOffset >= 0 ? rawOffset : 0,
  };
}
"""),
            "    limit: Number.isInteger(rawLimit) && rawLimit > 0 ? Math.min(rawLimit, 50) : 10,",
            [("-\nq=%20Milk%20&done=true",
              '{"q":"","done":null,"sort":"id","order":"asc","limit":10,"offset":0}\n'
              '{"q":"milk","done":true,"sort":"id","order":"asc","limit":10,"offset":0}'),
             ("limit=5&offset=10\nlimit=999\nlimit=abc&offset=-3\nlimit=2.5\nlimit=0",
              '{"q":"","done":null,"sort":"id","order":"asc","limit":5,"offset":10}\n'
              '{"q":"","done":null,"sort":"id","order":"asc","limit":50,"offset":0}\n'
              '{"q":"","done":null,"sort":"id","order":"asc","limit":10,"offset":0}\n'
              '{"q":"","done":null,"sort":"id","order":"asc","limit":10,"offset":0}\n'
              '{"q":"","done":null,"sort":"id","order":"asc","limit":10,"offset":0}'),
             ("sort=title&order=desc\nsort=secret&order=up\ndone=false",
              '{"q":"","done":null,"sort":"title","order":"desc","limit":10,"offset":0}\n'
              '{"q":"","done":null,"sort":"id","order":"asc","limit":10,"offset":0}\n'
              '{"q":"","done":false,"sort":"id","order":"asc","limit":10,"offset":0}')],
            hints=["Three things have to be true for the client's limit to be used: it is an integer, it is positive, and it is not above the cap.",
                   "`Number.isInteger` rejects NaN and 2.5 in one check; `Math.min` applies the ceiling.",
                   "`Number.isInteger(rawLimit) && rawLimit > 0 ? Math.min(rawLimit, 50) : 10`"]),
    ],
    quiz=[
        _q("Why must `done` have three states rather than two?",
           ["To support null values in the store", "Absent means 'do not filter' — which is different from 'filter for false'",
            "Because query values are strings", "It does not"],
           1,
           "Collapsing absent into false makes `GET /notes` silently hide every completed note, which reads as data loss."),
        _q("What is the real risk of using a client-supplied `sort` field without a whitelist?",
           ["Slower sorting", "It can address properties you never meant to expose — and against a database, it is injection",
            "The response is unsorted", "Nothing, since sort only reorders"],
           1,
           "A whitelist turns an open-ended string into one of three known values. That is a different kind of safety from escaping."),
    ],
)

_P5_S2 = _step(
    "filter-and-search",
    "Filtering and searching",
    "Narrow the list before you do anything else with it.",
    """
With options settled, filtering is small — which is the payoff for having done
the parsing properly.

### Do this

```js
let items = [...notes.values()];

if (opts.q) {
  items = items.filter((n) => n.title.toLowerCase().includes(opts.q));
}
if (opts.done !== null) {
  items = items.filter((n) => n.done === opts.done);
}
```

Two things to notice:

- **`opts.q` is already lowercased and trimmed**, so the filter is a plain
  `includes`. Normalising at the parser rather than in the loop means the
  comparison is written — and can be wrong — in exactly one place.
- **`opts.done !== null`**, not `if (opts.done)`. Filtering for `done=false` is a
  real request, and `if (opts.done)` would ignore it.

### Order the pipeline deliberately

**filter → count → sort → paginate.** Getting this order wrong produces bugs
that are hard to see and easy to ship:

- Counting before filtering makes `total` describe the wrong set, so the client
  renders page links to pages that are empty.
- Paginating before filtering takes the first ten notes and *then* removes the
  non-matching ones, so page 1 might return three results and page 2 might
  return seven — with no way to tell how many matches there really are.

`total` is the size **after filtering and before pagination**. That is the
number a client needs to draw a pager, and it is the only number that is
meaningfully "how many matched".

### About this search

`includes` on a lowercased title is a substring match. It is honest and it is
enough here — but say what it is not: no ranking, no word stemming, no accent
folding, no matching across fields. Real search is a genuinely different problem
solved by a different piece of software. Knowing where your simple version stops
is more useful than pretending it does not.
""",
    """
- `?q=buy` returns only the notes whose titles contain "buy", any capitalisation.
- `?done=true` returns only completed notes; `?done=false` returns only the others.
- `?q=buy&done=false` applies both.
- `total` reflects the filtered count, not the size of the store.
""",
    pitfalls=[
        "`if (opts.done)` skips the `done=false` filter entirely — the request is silently ignored.",
        "Lowercasing inside the filter instead of in the parser means one forgotten `.toLowerCase()` makes search case-sensitive again.",
        "Computing `total` from the store rather than from the filtered list makes every pager wrong.",
    ],
    exercises=[
        _ch("be5-filter", "Search and filter", "Easy",
            "Return `{\"items\":[…],\"total\":N}` for `GET /notes`. Apply `q` as a case-insensitive substring match on the title, and `done` as an exact match — but only when the client actually sent it. `total` is the number of matches.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}
""" + _SEED_NOTES + """
function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  if (url.pathname !== "/notes") return send(res, 404, { error: "not_found" });

  const q = (url.searchParams.get("q") ?? "").trim().toLowerCase();
  const rawDone = url.searchParams.get("done");
  const done = rawDone === null ? null : rawDone === "true";

  let items = [...notes.values()];
  if (q) items = items.filter((n) => n.title.toLowerCase().includes(q));
  if (done !== null) items = items.filter((n) => n.done === done);

  send(res, 200, { items, total: items.length });
}
"""),
            """  const q = (url.searchParams.get("q") ?? "").trim().toLowerCase();
  const rawDone = url.searchParams.get("done");
  const done = rawDone === null ? null : rawDone === "true";

  let items = [...notes.values()];
  if (q) items = items.filter((n) => n.title.toLowerCase().includes(q));
  if (done !== null) items = items.filter((n) => n.done === done);

  send(res, 200, { items, total: items.length });""",
            [("GET /notes?q=buy",
              '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":3,"title":"Buy bread","done":false}],"total":2}'),
             ("GET /notes?done=true\nGET /notes?done=false",
              '200 {"items":[{"id":2,"title":"Walk dog","done":true}],"total":1}\n'
              '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":3,"title":"Buy bread","done":false}],"total":2}'),
             ("GET /notes\nGET /notes?q=BUY&done=false\nGET /notes?q=zzz",
              '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":true},{"id":3,"title":"Buy bread","done":false}],"total":3}\n'
              '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":3,"title":"Buy bread","done":false}],"total":2}\n'
              '200 {"items":[],"total":0}')],
            hints=["Lowercase the search term once, up front, so the filter is a plain `includes`.",
                   "`done` has three states. `searchParams.get` returns null when it is absent — and absent means do not filter at all.",
                   "The second test is the one that catches `if (done)`: `?done=false` must actually filter."]),
    ],
    quiz=[
        _q("Which pipeline order is correct?",
           ["paginate → filter → sort", "filter → count → sort → paginate",
            "sort → paginate → filter", "count → paginate → filter → sort"],
           1,
           "Filter first so the count means something, then order the matches, then cut out the page. Any other order makes `total` or the page contents wrong."),
        _q("What should `total` be for `?q=buy&limit=1` when two notes match?",
           ["1 — the number returned", "2 — the number of matches before pagination",
            "3 — the number of notes in the store", "0"],
           1,
           "`total` exists so a client can draw a pager. The number it needs is how many matched, not how many fitted on this page."),
    ],
)

_P5_S3 = _step(
    "sorting",
    "Sorting without surprises",
    "The default comparator is a trap, and so is sorting the wrong array.",
    """
`Array.prototype.sort` has two behaviours that catch people out.

**It sorts as strings by default.** `[1, 2, 10].sort()` is `[1, 10, 2]`, because
`"10" < "2"`. Any sort of numbers needs a comparator.

**It mutates.** `items.sort(...)` reorders the array in place and returns the
same array. When `items` is a fresh `[...notes.values()]` that is harmless; when
it is an array something else is holding, you have just changed that too. Sort a
copy and the question stops arising.

### One comparator for three field types

You are sorting by `id` (number), `title` (string) or `done` (boolean), so you
need a comparator that handles all three:

```js
function compare(a, b) {
  if (a === b) return 0;
  return a < b ? -1 : 1;
}
```

`<` compares strings lexicographically, numbers numerically, and booleans as
`false < true`. A comparator must return a **negative number, zero or a positive
number** — and this is where the classic bug lives:

```js
items.sort((a, b) => a.title > b.title);          // BUG: returns true/false
items.sort((a, b) => a.title - b.title);          // BUG: strings give NaN
```

Both are silently wrong rather than loud. `true`/`false` coerce to 1/0 and never
to -1, so "less than" can never be expressed. `NaN` is treated as zero by the
spec, so the array comes back in its original order and looks *almost* right —
which is worse.

### Do this

```js
const dir = opts.order === "desc" ? -1 : 1;
items = [...items].sort((a, b) => dir * compare(a[opts.sort], b[opts.sort]));
```

Multiplying by the direction is better than sorting and then reversing:
`.reverse()` also reverses ties, so two notes with the same title swap places
depending on the direction — and JavaScript's sort is guaranteed stable
precisely so that does not happen.

`a[opts.sort]` is safe here **only because `opts.sort` came out of a whitelist**.
That is the same guarantee doing work twice.
""",
    """
- `?sort=title` orders alphabetically; `?sort=title&order=desc` reverses it.
- `?sort=id` is numeric — 2 comes before 10, not after.
- `?sort=nonsense` falls back to id order rather than returning a jumble.
- Sorting one request does not change the order returned by the next.
""",
    pitfalls=[
        "`(a, b) => a.x - b.x` on strings gives NaN, which the spec treats as 0 — so the array comes back unsorted, looking almost right.",
        "`(a, b) => a.x > b.x` returns a boolean, which can never be negative, so the comparator can never say 'less than'.",
        "`.sort()` with no comparator compares stringified values: `[1,2,10]` becomes `[1,10,2]`.",
        "Sorting ascending and then `.reverse()` also reverses ties, throwing away sort stability.",
    ],
    warmup=[
        _q("`[{t:\"Cherry\"},{t:\"Apple\"}].sort((a,b) => a.t - b.t)` — what order comes back?",
           ["Apple, Cherry", "Cherry, Apple — unchanged", "It throws", "Randomly one or the other"],
           1,
           "Subtracting strings gives NaN, and the spec says a NaN comparator result is treated as +0 — 'these are equal'. A stable sort therefore leaves everything exactly where it was."),
    ],
    exercises=[
        _fix("be5-sort", "The sort that does nothing",
             "Sorting by `id` works, but `?sort=title` comes back in the original order. Fix the comparator so it orders numbers, strings and booleans correctly — and so it does not sort the caller's array in place.",
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}
""" + _SEED_NOTES + """
const SORTS = ["id", "title", "done"];

function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  if (url.pathname !== "/notes") return send(res, 404, { error: "not_found" });

  const raw = url.searchParams.get("sort");
  const sort = SORTS.includes(raw) ? raw : "id";
  const dir = url.searchParams.get("order") === "desc" ? -1 : 1;

  const items = [...notes.values()];
  items.sort((a, b) => dir * (a[sort] - b[sort]));

  send(res, 200, { items, total: items.length });
}
"""),
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}
""" + _SEED_NOTES + """
const SORTS = ["id", "title", "done"];

function compare(a, b) {
  if (a === b) return 0;
  return a < b ? -1 : 1;
}

function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  if (url.pathname !== "/notes") return send(res, 404, { error: "not_found" });

  const raw = url.searchParams.get("sort");
  const sort = SORTS.includes(raw) ? raw : "id";
  const dir = url.searchParams.get("order") === "desc" ? -1 : 1;

  const items = [...notes.values()].sort((a, b) => dir * compare(a[sort], b[sort]));

  send(res, 200, { items, total: items.length });
}
"""),
             [("GET /notes?sort=title",
               '200 {"items":[{"id":3,"title":"Buy bread","done":false},{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":true}],"total":3}'),
              ("GET /notes?sort=title&order=desc\nGET /notes?sort=id",
               '200 {"items":[{"id":2,"title":"Walk dog","done":true},{"id":1,"title":"Buy milk","done":false},{"id":3,"title":"Buy bread","done":false}],"total":3}\n'
               '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":true},{"id":3,"title":"Buy bread","done":false}],"total":3}'),
              ("GET /notes?sort=done&order=desc\nGET /notes?sort=nope",
               '200 {"items":[{"id":2,"title":"Walk dog","done":true},{"id":1,"title":"Buy milk","done":false},{"id":3,"title":"Buy bread","done":false}],"total":3}\n'
               '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":true},{"id":3,"title":"Buy bread","done":false}],"total":3}')],
             hints=["What does `\"Buy milk\" - \"Walk dog\"` evaluate to, and what does sort do with that result?",
                    "Write a `compare(a, b)` that works for strings, numbers and booleans by using `<` rather than `-`.",
                    "Also sort a copy: `[...notes.values()].sort(...)` rather than sorting an array someone else may be holding."]),
    ],
    quiz=[
        _q("What must a comparator return?",
           ["true or false", "A negative number, zero, or a positive number",
            "Exactly -1, 0 or 1", "The smaller of the two values"],
           1,
           "Any negative or positive number works — which is why `a - b` is idiomatic for numbers, and why booleans (never negative) silently fail."),
        _q("Why multiply by a direction instead of sorting then calling `.reverse()`?",
           ["It is faster", "reverse() also flips ties, discarding the stability the sort guaranteed",
            "reverse() mutates", "There is no difference"],
           1,
           "Stable sorting means equal elements keep their relative order. Reversing the whole array reverses those too, so ties move for no reason the user can see."),
    ],
)

_P5_S4 = _step(
    "paginate",
    "Pagination and the response envelope",
    "A page of results is useless without knowing how many there are.",
    """
Last step of the pipeline: cut out the page, and tell the client enough to ask
for the next one.

### Do this

```js
const total = items.length;                                  // AFTER filtering
const page = items.slice(opts.offset, opts.offset + opts.limit);

send(res, 200, {
  items: page,
  total,
  limit: opts.limit,
  offset: opts.offset,
});
```

`slice` is well behaved at the edges: an offset past the end gives `[]` rather
than an error, and a limit longer than what remains just returns what remains.
That is one of the reasons the parser guaranteed both are non-negative integers
— `slice(NaN, NaN)` returns an empty array with no complaint at all.

### Why an envelope, not a bare array

`GET /notes` used to return `[…]`. Now it returns an object. That is a
**breaking change** for any existing client, and it is the right one: a bare
array has nowhere to put `total`, so a client cannot render "showing 1–10 of
57", cannot know whether to draw a next-page link, and has to guess whether a
short page means the end or an error.

Two lessons come free with this:

- **Envelope list responses from day one.** Adding a field to an object is
  cheap; changing an array into an object is not.
- **A single item stays bare.** `GET /notes/1` returns the note itself, not
  `{item: …}`. Envelopes solve a collection problem.

### Offset pagination and its limit

`limit`/`offset` is simple, easy to reason about, and lets a client jump
straight to page 40. It also has a real flaw: if a note is inserted while
someone is paging, everything shifts down by one, and the reader sees an item
twice or misses one entirely. Deeper pages get slower too, since the database
must count past everything it skips.

The alternative is **cursor pagination** — `?after=<id of the last item you
saw>` — which is immune to shifting and stays fast at any depth, at the cost of
not being able to jump to page 40. Offset is the right choice here; knowing why
you might outgrow it is the point.
""",
    """
- `?limit=2` returns two items with the full `total`.
- `?limit=2&offset=2` returns the next page; `?offset=99` returns `{"items":[],"total":3,…}`.
- The response always carries `items`, `total`, `limit` and `offset`.
- `GET /notes/1` still returns the note itself, not an envelope.
""",
    pitfalls=[
        "Computing `total` after slicing means it always equals the page size — and every pager built on it is wrong.",
        "An unclamped `limit` lets one request ask for everything you have.",
        "Changing a list response from an array to an envelope breaks existing clients. Do it once, early, on purpose.",
    ],
    warmup=[
        _q("Three notes match. `?limit=2&offset=2`. What should the response be?",
           ['items has 1 note, total 3', 'items has 1 note, total 1',
            'items has 2 notes, total 3', "404 — the page is past the end"],
           0,
           "The slice returns whatever remains — one note. `total` still describes the whole match set, which is what the client needs to know there is nothing after this."),
    ],
    exercises=[
        _ch("be5-paginate", "Cut out the page", "Easy",
            "Complete the list endpoint: filter by `q`, then respond with `{\"items\":…,\"total\":…,\"limit\":…,\"offset\":…}`. `limit` defaults to 10, is capped at 50, and falls back to the default when it is not a positive integer; `offset` defaults to 0. `total` is the number of matches BEFORE the page is cut.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}
""" + _SEED_NOTES + """
function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  if (url.pathname !== "/notes") return send(res, 404, { error: "not_found" });
  const params = url.searchParams;

  const q = (params.get("q") ?? "").trim().toLowerCase();
  const rawLimit = Number(params.get("limit"));
  const rawOffset = Number(params.get("offset"));
  const limit = Number.isInteger(rawLimit) && rawLimit > 0 ? Math.min(rawLimit, 50) : 10;
  const offset = Number.isInteger(rawOffset) && rawOffset >= 0 ? rawOffset : 0;

  let items = [...notes.values()];
  if (q) items = items.filter((n) => n.title.toLowerCase().includes(q));

  const total = items.length;
  send(res, 200, { items: items.slice(offset, offset + limit), total, limit, offset });
}
"""),
            """  const q = (params.get("q") ?? "").trim().toLowerCase();
  const rawLimit = Number(params.get("limit"));
  const rawOffset = Number(params.get("offset"));
  const limit = Number.isInteger(rawLimit) && rawLimit > 0 ? Math.min(rawLimit, 50) : 10;
  const offset = Number.isInteger(rawOffset) && rawOffset >= 0 ? rawOffset : 0;

  let items = [...notes.values()];
  if (q) items = items.filter((n) => n.title.toLowerCase().includes(q));

  const total = items.length;
  send(res, 200, { items: items.slice(offset, offset + limit), total, limit, offset });""",
            [("GET /notes?limit=2",
              '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":true}],"total":3,"limit":2,"offset":0}'),
             ("GET /notes?limit=2&offset=2\nGET /notes?offset=99",
              '200 {"items":[{"id":3,"title":"Buy bread","done":false}],"total":3,"limit":2,"offset":2}\n'
              '200 {"items":[],"total":3,"limit":10,"offset":99}'),
             ("GET /notes?q=buy&limit=1\nGET /notes?limit=999\nGET /notes?limit=abc",
              '200 {"items":[{"id":1,"title":"Buy milk","done":false}],"total":2,"limit":1,"offset":0}\n'
              '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":true},{"id":3,"title":"Buy bread","done":false}],"total":3,"limit":50,"offset":0}\n'
              '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":true},{"id":3,"title":"Buy bread","done":false}],"total":3,"limit":10,"offset":0}')],
            hints=["Settle limit and offset first, then filter, then take `total`, then slice. That order is the lesson.",
                   "`?offset=99` must still report the real total — `slice` past the end gives `[]` without complaint.",
                   "Third test: `?q=buy&limit=1` returns one item but `total` is 2, because total counts matches, not the page."]),
    ],
    quiz=[
        _q("Why return an envelope instead of a bare array?",
           ["Arrays are slower to serialise", "There is nowhere in an array to put total, limit and offset",
            "JSON requires an object at the top level", "To support sorting"],
           1,
           "Without `total` a client cannot render a pager or tell a last page from an error. And adding a field to an object never breaks anyone; turning an array into an object does."),
        _q("What is the main weakness of offset pagination?",
           ["It cannot sort", "Inserts shift the window, so a reader can see an item twice or skip one",
            "It is limited to 50 items", "It does not work with filters"],
           1,
           "Offsets address positions, and positions move. Cursor pagination addresses an item instead, which is why it is immune."),
    ],
)

_P5_FINAL = _ch(
    "be5-final", "The full query endpoint", "Medium",
    "Build `GET /notes` with the whole pipeline: parse (`q`, `done`, `sort`, `order`, `limit`, `offset` with the defaults and the 50 cap), filter, count, sort, paginate, and respond `{\"items\":…,\"total\":…,\"limit\":…,\"offset\":…}`. `sort` is whitelisted to id/title/done; anything else falls back to id. `done` filters only when the client sent it. `total` counts matches before the page is cut. Any other path → 404.",
    _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}
""" + _SEED_NOTES + """
const SORTS = ["id", "title", "done"];

function compare(a, b) {
  if (a === b) return 0;
  return a < b ? -1 : 1;
}

function parseQuery(params) {
  const rawLimit = Number(params.get("limit"));
  const rawOffset = Number(params.get("offset"));
  const sort = params.get("sort");
  const done = params.get("done");
  return {
    q: (params.get("q") ?? "").trim().toLowerCase(),
    done: done === null ? null : done === "true",
    sort: SORTS.includes(sort) ? sort : "id",
    order: params.get("order") === "desc" ? "desc" : "asc",
    limit: Number.isInteger(rawLimit) && rawLimit > 0 ? Math.min(rawLimit, 50) : 10,
    offset: Number.isInteger(rawOffset) && rawOffset >= 0 ? rawOffset : 0,
  };
}

function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  if (url.pathname !== "/notes") return send(res, 404, { error: "not_found" });

  const opts = parseQuery(url.searchParams);
  let items = [...notes.values()];
  if (opts.q) items = items.filter((n) => n.title.toLowerCase().includes(opts.q));
  if (opts.done !== null) items = items.filter((n) => n.done === opts.done);

  const total = items.length;
  const dir = opts.order === "desc" ? -1 : 1;
  items = [...items].sort((a, b) => dir * compare(a[opts.sort], b[opts.sort]));

  send(res, 200, {
    items: items.slice(opts.offset, opts.offset + opts.limit),
    total,
    limit: opts.limit,
    offset: opts.offset,
  });
}
"""),
    """  const opts = parseQuery(url.searchParams);
  let items = [...notes.values()];
  if (opts.q) items = items.filter((n) => n.title.toLowerCase().includes(opts.q));
  if (opts.done !== null) items = items.filter((n) => n.done === opts.done);

  const total = items.length;
  const dir = opts.order === "desc" ? -1 : 1;
  items = [...items].sort((a, b) => dir * compare(a[opts.sort], b[opts.sort]));

  send(res, 200, {
    items: items.slice(opts.offset, opts.offset + opts.limit),
    total,
    limit: opts.limit,
    offset: opts.offset,
  });""",
    [("GET /notes",
      '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":true},{"id":3,"title":"Buy bread","done":false}],"total":3,"limit":10,"offset":0}'),
     ("GET /notes?q=buy&sort=title\nGET /notes?done=false&limit=1",
      '200 {"items":[{"id":3,"title":"Buy bread","done":false},{"id":1,"title":"Buy milk","done":false}],"total":2,"limit":10,"offset":0}\n'
      '200 {"items":[{"id":1,"title":"Buy milk","done":false}],"total":2,"limit":1,"offset":0}'),
     ("GET /notes?sort=title&order=desc&limit=2\nGET /notes?limit=2&offset=2\nGET /notes?sort=hack&limit=999",
      '200 {"items":[{"id":2,"title":"Walk dog","done":true},{"id":1,"title":"Buy milk","done":false}],"total":3,"limit":2,"offset":0}\n'
      '200 {"items":[{"id":3,"title":"Buy bread","done":false}],"total":3,"limit":2,"offset":2}\n'
      '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk dog","done":true},{"id":3,"title":"Buy bread","done":false}],"total":3,"limit":50,"offset":0}'),
     ("GET /notes?q=BUY&done=false&sort=title&order=desc\nGET /notes?offset=99\nGET /users",
      '200 {"items":[{"id":1,"title":"Buy milk","done":false},{"id":3,"title":"Buy bread","done":false}],"total":2,"limit":10,"offset":0}\n'
      '200 {"items":[],"total":3,"limit":10,"offset":99}\n'
      '404 {"error":"not_found"}')],
    hints=["Settle every option first with parseQuery, then run the pipeline in order: filter, count, sort, slice.",
           "`total` is taken between filtering and sorting — sorting does not change the count, and slicing must not change it either.",
           "The second test shows why order matters: `?done=false&limit=1` returns one item but reports total 2."])

_P5 = _project(
    "query-api", 5,
    "Search, Filter, Sort, Paginate",
    "The list endpoint every real API grows, and the bugs it grows with.",
    "Core",
    "Turn `GET /notes` into a proper query interface — search, filter, whitelisted sort, clamped pagination — behind one response envelope.",
    "Returning every row works until it does not, and it stops working in production rather than on your machine. The pipeline in this project is the same one behind every 'showing 1–10 of 57' you have ever seen.",
    140,
    ["first-server", "notes-crud", "validation"],
    ["query parameters", "filtering", "sorting", "pagination", "response envelopes", "whitelisting"],
    ["Parse untrusted query parameters into settled, clamped options",
     "Filter on a three-state boolean without collapsing absent into false",
     "Write a comparator that is correct for strings, numbers and booleans",
     "Order the pipeline so `total` means what clients think it means",
     "Explain when offset pagination stops being good enough"],
    """
`GET /notes` currently returns everything. This project turns it into the
endpoint you would actually ship: `?q=` to search, `?done=` to filter, `?sort=`
and `?order=` to order, `?limit=` and `?offset=` to page — all behind one
envelope that tells a client how many matches there are.

The four steps mirror the pipeline exactly: **parse → filter → sort →
paginate**. Most list-endpoint bugs are really order-of-pipeline bugs, so the
order is the lesson as much as the code is.

Note that this project changes what `GET /notes` returns, from a bare array to
an object. That is a breaking change, and doing it deliberately — with a reason
you can state — is the point.
""",
    [_ep("GET", "/notes?q=", "Search titles (case-insensitive)", "", "{items,total,limit,offset}", "200"),
     _ep("GET", "/notes?done=", "Filter by completion", "", "{items,total,…}", "200"),
     _ep("GET", "/notes?sort=&order=", "Order by id, title or done", "", "{items,total,…}", "200"),
     _ep("GET", "/notes?limit=&offset=", "Page (limit ≤ 50)", "", "{items,total,limit,offset}", "200"),
     _ep("GET", "/notes/:id", "Unchanged — a bare note, no envelope", "", '{"id":1,…}', "200 · 404")],
    """
Same folder, same files. The work here is almost entirely in one place — the
`GET /notes` branch — so it is a good moment to notice how much easier that is
now that the store is its own module.

```
cd notes-api
node server.js
```

Create half a dozen notes before you start so the paging has something to page.
Quote your URLs in the shell: an unquoted `&` sends curl to the background.
""",
    [_P5_S1, _P5_S2, _P5_S3, _P5_S4],
    final_build=_P5_FINAL,
    acceptance=[
        "`GET /notes` returns `{items, total, limit, offset}` with limit 10 and offset 0.",
        "`?q=buy` matches case-insensitively on the title; `?q=zzz` gives `items: []` and `total: 0`.",
        "`?done=false` actually filters — it is not treated as 'no filter'.",
        "`?sort=title` orders alphabetically and `?sort=id` orders numerically.",
        "`?sort=anything-else` falls back to id instead of returning a jumble.",
        "`?order=desc` reverses the order without disturbing ties.",
        "`?limit=999` is clamped to 50; `?limit=abc` falls back to 10.",
        "`?offset=99` returns an empty page but still reports the real total.",
        "`total` counts matches after filtering and before pagination.",
        "`GET /notes/1` still returns a bare note, not an envelope.",
    ],
    manual_test="""
Create six notes first, then:

```
curl "http://localhost:3000/notes"
curl "http://localhost:3000/notes?q=buy"
curl "http://localhost:3000/notes?q=BUY"          # same results
curl "http://localhost:3000/notes?done=false"     # must filter, not ignore
curl "http://localhost:3000/notes?sort=title"
curl "http://localhost:3000/notes?sort=title&order=desc"
curl "http://localhost:3000/notes?limit=2"
curl "http://localhost:3000/notes?limit=2&offset=2"
curl "http://localhost:3000/notes?limit=999"      # clamped to 50
curl "http://localhost:3000/notes?limit=abc"      # falls back to 10
curl "http://localhost:3000/notes?offset=999"     # [] but the real total
curl "http://localhost:3000/notes?sort=constructor"   # falls back to id
```

Check `total` on every one of these. It should describe the matches, never the
page — that single number is where most list-endpoint bugs show up.
""",
    reference="""
const SORTS = ["id", "title", "done"];

/** Works for strings, numbers and booleans — `-` does not. */
function compare(a, b) {
  if (a === b) return 0;
  return a < b ? -1 : 1;
}

/** Untrusted params in, settled options out. Nothing downstream sees raw input. */
function parseQuery(params) {
  const rawLimit = Number(params.get("limit"));
  const rawOffset = Number(params.get("offset"));
  const sort = params.get("sort");
  const done = params.get("done");

  return {
    q: (params.get("q") ?? "").trim().toLowerCase(),
    done: done === null ? null : done === "true",   // three states
    sort: SORTS.includes(sort) ? sort : "id",       // whitelist, not sanitise
    order: params.get("order") === "desc" ? "desc" : "asc",
    limit: Number.isInteger(rawLimit) && rawLimit > 0 ? Math.min(rawLimit, 50) : 10,
    offset: Number.isInteger(rawOffset) && rawOffset >= 0 ? rawOffset : 0,
  };
}

/** filter → count → sort → paginate. The order IS the correctness. */
function query(all, params) {
  const opts = parseQuery(params);

  let items = all;
  if (opts.q) items = items.filter((n) => n.title.toLowerCase().includes(opts.q));
  if (opts.done !== null) items = items.filter((n) => n.done === opts.done);

  const total = items.length;

  const dir = opts.order === "desc" ? -1 : 1;
  items = [...items].sort((a, b) => dir * compare(a[opts.sort], b[opts.sort]));

  return {
    items: items.slice(opts.offset, opts.offset + opts.limit),
    total,
    limit: opts.limit,
    offset: opts.offset,
  };
}

// in the route:
//   if (rawId === undefined && req.method === "GET")
//     return send(res, 200, query(store.list(), url.searchParams));
""",
    stretch=[
        "Add `?fields=id,title` so a client can ask for a subset of each note. Whitelist the field names — the same lesson as `sort`, and the same consequence for skipping it.",
        "Switch to cursor pagination: `?after=<id>&limit=`, returning `nextCursor`. Then write down what you gained and what you gave up.",
        "Support multi-key sorting (`?sort=done,title`) by chaining comparators: return the first non-zero result.",
        "Add `Link` headers with `rel=\"next\"` and `rel=\"prev\"`. It is how GitHub's API paginates, and it means clients never build URLs themselves.",
    ],
    glossary=[
        _gloss("query parameter", "A `?key=value` pair. Always a string, always written by the caller, never to be trusted."),
        _gloss("whitelist", "Accept only values from a known list; everything else takes the default. Stronger than trying to filter out bad input."),
        _gloss("clamping", "Forcing a value into a safe range, e.g. `Math.min(limit, 50)`."),
        _gloss("envelope", "A wrapper object around a list response so it can also carry total, limit and offset."),
        _gloss("offset pagination", "Skip N, take M. Simple, jumpable, but shifts when rows are inserted."),
        _gloss("cursor pagination", "Continue after a specific item. Stable under inserts and fast at depth; cannot jump to page 40."),
        _gloss("stable sort", "Equal elements keep their relative order. Guaranteed in JavaScript since ES2019 — and thrown away by `.reverse()`."),
    ],
    cheatsheet="""
```js
// the pipeline — the ORDER is the correctness
let items = all;
if (opts.q) items = items.filter((n) => n.title.toLowerCase().includes(opts.q));
if (opts.done !== null) items = items.filter((n) => n.done === opts.done);
const total = items.length;                              // ← after filter, before page
items = [...items].sort((a, b) => dir * compare(a[opts.sort], b[opts.sort]));
items = items.slice(opts.offset, opts.offset + opts.limit);

// a comparator for strings, numbers AND booleans
const compare = (a, b) => (a === b ? 0 : a < b ? -1 : 1);
```

| Trap | What you get |
| --- | --- |
| `if (opts.done)` | `?done=false` silently ignored |
| `[1,2,10].sort()` | `[1,10,2]` — string comparison |
| `(a,b) => a.t - b.t` on strings | NaN → treated as 0 → unsorted |
| `(a,b) => a.t > b.t` | boolean → never negative → wrong |
| no `Math.min(limit, 50)` | `?limit=10000000` |
| `total` after slicing | every pager in every client is wrong |
| `.sort()` then `.reverse()` | ties flip; stability lost |
""",
    self_check=[
        "I can explain why `done` needs three states and what breaks with two.",
        "I know two comparator mistakes that fail silently rather than loudly.",
        "I can say exactly where in the pipeline `total` is computed, and why there.",
        "I can justify whitelisting `sort` in terms of something worse than a wrong order.",
        "I can describe one situation where offset pagination returns a duplicate.",
    ],
    review=[
        _q("`?done=false` returns every note, completed ones included. What is the bug?",
           ["The filter runs after pagination", "The code tests `if (opts.done)`, which is false for the string-derived false",
            "`done` is not in the sort whitelist", "total is computed too early"],
           1,
           "A legitimate `false` filter is indistinguishable from 'no filter' under a truthiness test. Compare against null instead."),
        _q("Why is `Math.min(limit, 50)` a security measure and not just tidiness?",
           ["It prevents SQL injection", "Without it, one request can ask the server to do unbounded work",
            "It stops negative numbers", "It makes responses smaller"],
           1,
           "An unbounded limit is a denial-of-service request that your own code carries out — a client asking for ten million rows."),
        _q("Two notes both have the title \"Buy milk\". You sort ascending then reverse. What happened to them?",
           ["Nothing — they are equal", "Their relative order flipped, discarding sort stability",
            "One is dropped", "They are sorted by id"],
           1,
           "Reverse does not know which order was meaningful. Multiplying the comparator by -1 keeps ties where they were."),
        _q("A note is inserted at the top while a client reads page 2 with offset pagination. What can happen?",
           ["Nothing", "The client sees an item it already saw on page 1",
            "The request 500s", "The total goes negative"],
           1,
           "Every item shifts down one position, so the item that was last on page 1 is now first on page 2. That is precisely the flaw cursor pagination removes."),
    ],
    milestone="Your list endpoint behaves like a real one — searchable, sortable, paged, and honest about how much there is.",
)

_PROJECTS.append(_P5)


# ===========================================================================
# PROJECT 6 — Users, Tokens & Ownership
# ===========================================================================

_PASSWORD_DRIVER = """
// ---- password driver (given — don't edit) ----------------------------------
// stdin: one line per check —  <password to store> <password to try>
// prints:  <is the plaintext visible in the record?> <does the attempt verify?>
for (const line of fs.readFileSync(0, "utf8").split("\\n")) {
  const [stored, attempt] = line.trim().split(" ");
  if (!stored) continue;
  const record = hashPassword(stored);
  console.log(record.includes(stored), verifyPassword(attempt, record));
}
"""


def _password_prog(code):
    return ('import fs from "node:fs";\nimport crypto from "node:crypto";\n\n'
            + _bp(code) + "\n" + _bp(_PASSWORD_DRIVER))


_AUTH_IMPORTS = ('import http from "node:http";\nimport fs from "node:fs";\n'
                 'import crypto from "node:crypto";\n')

_P6_S1 = _step(
    "hashing",
    "Never store a password",
    "Store something you can check a password against — and nothing more.",
    """
The moment your API has users, it has passwords, and there is exactly one rule:
**you never store the password.** Not encrypted, not encoded, not "hashed with
MD5". If your database is ever read by someone it should not be — and databases
leak — the passwords in it must be useless to them.

What you store instead is a **salted hash**: the output of a deliberately slow
one-way function. You can check a guess against it. You cannot get the password
back out of it.

### Do this

```js
import crypto from "node:crypto";

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto.scryptSync(password, salt, 32).toString("hex");
  return `${salt}:${hash}`;
}

function verifyPassword(attempt, record) {
  const [salt, hash] = record.split(":");
  const attemptHash = crypto.scryptSync(attempt, salt, 32);
  return crypto.timingSafeEqual(attemptHash, Buffer.from(hash, "hex"));
}
```

### Why each piece is there

- **A random salt, per user.** Without one, two people who choose the same
  password get the same hash — so an attacker cracks a password once and gets
  every account that shares it, and a precomputed table of common passwords
  works instantly. The salt is not a secret; store it right next to the hash.
- **scrypt, not SHA-256.** General-purpose hashes are built to be *fast*, which
  is precisely wrong here: a GPU computes billions of SHA-256 hashes per second.
  scrypt is deliberately slow and memory-hungry, so an attacker's guesses cost
  real time and real hardware. (bcrypt and argon2 are the other right answers;
  scrypt ships with Node, which is why it is used here.)
- **`timingSafeEqual`, not `===`.** String comparison returns as soon as it
  finds a difference, so a wrong guess that shares a longer prefix takes very
  slightly longer to reject. Measured across enough requests, that leak is
  enough to reconstruct a value byte by byte. `timingSafeEqual` always takes the
  same time.

### Notice what never leaves the server

Nothing in this project ever returns a hash, a salt, or a password. The only
thing an endpoint says about a password is **yes** or **no**. If you find
yourself logging a request body during debugging, remember that you are now
logging passwords — that is how they end up in log aggregators forever.
""",
    """
- `hashPassword("hunter2")` returns a `salt:hash` string containing no trace of `hunter2`.
- Hashing the same password twice gives two different records — different salts.
- `verifyPassword("hunter2", record)` is true; `verifyPassword("hunter3", record)` is false.
- No endpoint ever returns the record.
""",
    pitfalls=[
        "Reusing one salt for every user makes the salt pointless — the whole point is that identical passwords hash differently.",
        "SHA-256 and MD5 are fast by design, which is exactly the wrong property for a password. Use scrypt, bcrypt or argon2.",
        "`attemptHash === hash` leaks timing. Use `crypto.timingSafeEqual`, which also throws if the two buffers differ in length.",
        "Logging request bodies during debugging logs plaintext passwords.",
    ],
    warmup=[
        _q("Why store a random salt alongside each password hash?",
           ["To encrypt the hash", "So identical passwords produce different hashes, defeating precomputed tables",
            "To make the hash shorter", "So the password can be recovered"],
           1,
           "The salt is not secret and is not encryption. Its only job is to make every hash unique, so cracking one account does not crack every account that shares that password."),
    ],
    exercises=[
        _ex("be6-hash", "Store something safe",
            "Finish `hashPassword` so it returns `salt:hash` with a fresh random salt each time. The driver prints whether the plaintext is visible in the record (it must be `false`) and whether the attempt verifies.",
            _password_prog("""
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto.scryptSync(password, salt, 32).toString("hex");
  return `${salt}:${hash}`;
}

function verifyPassword(attempt, record) {
  const [salt, hash] = record.split(":");
  const attemptHash = crypto.scryptSync(attempt, salt, 32);
  return crypto.timingSafeEqual(attemptHash, Buffer.from(hash, "hex"));
}
"""),
            """  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto.scryptSync(password, salt, 32).toString("hex");
  return `${salt}:${hash}`;""",
            [("hunter2 hunter2\nhunter2 wrongpw", "false true\nfalse false"),
             ("supersecret supersecret\nsupersecret Supersecret\nzurgle zurgle",
              "false true\nfalse false\nfalse true")],
            hints=["Three lines: make a random salt, derive the hash from password + salt, join them with a colon.",
                   "`crypto.randomBytes(16).toString(\"hex\")` gives a salt; `crypto.scryptSync(password, salt, 32)` gives a 32-byte hash.",
                   "`verifyPassword` splits on `:` and re-derives with the same salt, so store them in that order."]),
    ],
    quiz=[
        _q("Why is SHA-256 a poor choice for password storage?",
           ["It is not secure", "It is fast, so an attacker can try billions of guesses per second",
            "It produces short output", "It cannot be salted"],
           1,
           "SHA-256 is an excellent hash and a terrible password hash. Password hashing wants slowness on purpose — that is what scrypt, bcrypt and argon2 sell."),
        _q("What does `crypto.timingSafeEqual` protect against?",
           ["Hash collisions", "An attacker inferring a secret from how long a comparison takes",
            "Brute force", "Replay attacks"],
           1,
           "`===` short-circuits at the first differing byte. That timing difference is measurable, and it is enough to reconstruct a value one byte at a time."),
    ],
)

_P6_S2 = _step(
    "register-and-login",
    "Register, log in, get a token",
    "A password proves who you are once; a token carries it afterwards.",
    """
Sending a username and password on every request would mean hashing on every
request — slow by design — and spreading the password across every log and proxy
in the path. So you exchange it **once** for a token.

### Do this

1. Add a user store and a token store:

   ```js
   const users = new Map();      // username -> { username, password }
   const tokens = new Map();     // token    -> username
   let nextToken = 1;
   ```

2. `POST /register` — create a user, refuse duplicates:

   ```js
   if (users.has(username)) return send(res, 409, { error: "user_exists" });
   users.set(username, { username, password: hashPassword(password) });
   return send(res, 201, { username });
   ```

   The response contains the username and nothing else. There is no version of
   this endpoint that should return the password record.

3. `POST /login` — verify, then issue:

   ```js
   const user = users.get(username);
   if (!user || !verifyPassword(password, user.password)) {
     return send(res, 401, { error: "invalid_credentials" });
   }
   const token = `tok_${nextToken++}`;
   tokens.set(token, username);
   return send(res, 200, { token });
   ```

### The detail that is easy to get wrong

**One error for both failures.** An unknown username and a wrong password both
return exactly `401 invalid_credentials`. Saying "no such user" tells an
attacker which usernames exist, which turns one guessing problem into two much
easier ones. (A careful implementation also spends the same *time* on both
paths, by verifying against a dummy hash when the user is missing — otherwise
the response time leaks the same fact.)

### About these tokens

`tok_1` is a counter so that the drills have predictable output. **Do not ship
this.** A guessable token is not a credential — an attacker simply tries `tok_1`
through `tok_500`. Real tokens are unguessable random values:

```js
const token = crypto.randomBytes(32).toString("hex");
```

Two other things a real token needs and this one does not have: an **expiry**,
so a leaked token stops working, and a way to **revoke** it, so logging out
means something. A server-side token map like this one can revoke by deleting.
JWTs, which carry their claims inside the token itself, cannot — which is the
main trade-off in that whole debate.
""",
    """
- `POST /register {"username":"ada","password":"hunter2"}` → 201 `{"username":"ada"}` and nothing else.
- Registering the same username again → 409.
- `POST /login` with the right password → 200 `{"token":"tok_1"}`.
- A wrong password and an unknown user both return the same 401 `invalid_credentials`.
""",
    pitfalls=[
        "Different errors for 'no such user' and 'wrong password' tell an attacker which usernames are real.",
        "Returning the user record from /register leaks the hash and salt.",
        "Sequential tokens are guessable. Counters are used here only so the expected output can be written down.",
        "No expiry means a leaked token is valid forever.",
    ],
    exercises=[
        _ch("be6-login", "Register and log in", "Medium",
            "Write both endpoints. `POST /register` → 201 `{\"username\":…}`, or 409 `{\"error\":\"user_exists\"}` for a duplicate, or 400 `{\"error\":\"validation_failed\"}` if either field is missing. `POST /login` → 200 `{\"token\":\"tok_N\"}` (N counting from 1), or 401 `{\"error\":\"invalid_credentials\"}` for BOTH a wrong password and an unknown user.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  return `${salt}:${crypto.scryptSync(password, salt, 32).toString("hex")}`;
}

function verifyPassword(attempt, record) {
  const [salt, hash] = record.split(":");
  return crypto.timingSafeEqual(
    crypto.scryptSync(attempt, salt, 32),
    Buffer.from(hash, "hex")
  );
}

const users = new Map();
const tokens = new Map();
let nextToken = 1;

async function handler(req, res) {
  const { pathname } = new URL(req.url, "http://localhost");
  const body = JSON.parse((await readBody(req)) || "{}");
  const { username, password } = body;

  if (pathname === "/register" && req.method === "POST") {
    if (typeof username !== "string" || typeof password !== "string") {
      return send(res, 400, { error: "validation_failed" });
    }
    if (users.has(username)) return send(res, 409, { error: "user_exists" });
    users.set(username, { username, password: hashPassword(password) });
    return send(res, 201, { username });
  }

  if (pathname === "/login" && req.method === "POST") {
    const user = users.get(username);
    if (!user || !verifyPassword(password ?? "", user.password)) {
      return send(res, 401, { error: "invalid_credentials" });
    }
    const token = `tok_${nextToken++}`;
    tokens.set(token, username);
    return send(res, 200, { token });
  }

  send(res, 404, { error: "not_found" });
}
""", imports=_AUTH_IMPORTS),
            """  if (pathname === "/register" && req.method === "POST") {
    if (typeof username !== "string" || typeof password !== "string") {
      return send(res, 400, { error: "validation_failed" });
    }
    if (users.has(username)) return send(res, 409, { error: "user_exists" });
    users.set(username, { username, password: hashPassword(password) });
    return send(res, 201, { username });
  }

  if (pathname === "/login" && req.method === "POST") {
    const user = users.get(username);
    if (!user || !verifyPassword(password ?? "", user.password)) {
      return send(res, 401, { error: "invalid_credentials" });
    }
    const token = `tok_${nextToken++}`;
    tokens.set(token, username);
    return send(res, 200, { token });
  }""",
            [('POST /register {"username":"ada","password":"hunter2"}\nPOST /login {"username":"ada","password":"hunter2"}',
              '201 {"username":"ada"}\n200 {"token":"tok_1"}'),
             ('POST /register {"username":"ada","password":"hunter2"}\nPOST /register {"username":"ada","password":"other"}\nPOST /register {"username":"bob"}\nPOST /login {"username":"ada","password":"wrong"}\nPOST /login {"username":"nobody","password":"hunter2"}',
              '201 {"username":"ada"}\n409 {"error":"user_exists"}\n'
              '400 {"error":"validation_failed"}\n'
              '401 {"error":"invalid_credentials"}\n'
              '401 {"error":"invalid_credentials"}'),
             ('POST /register {"username":"ada","password":"pw"}\nPOST /register {"username":"bob","password":"pw"}\nPOST /login {"username":"ada","password":"pw"}\nPOST /login {"username":"bob","password":"pw"}\nGET /whoami',
              '201 {"username":"ada"}\n201 {"username":"bob"}\n'
              '200 {"token":"tok_1"}\n200 {"token":"tok_2"}\n'
              '404 {"error":"not_found"}')],
            hints=["Register: validate, reject duplicates, then store the HASH — never the password itself.",
                   "Login: an unknown user and a wrong password must produce the identical 401, so combine them into one condition.",
                   "`verifyPassword` needs a string; `password ?? \"\"` keeps a missing field from throwing before you can return the 401."]),
    ],
    quiz=[
        _q("Why return the same error for an unknown user and a wrong password?",
           ["It is less code", "Otherwise the response tells an attacker which usernames exist",
            "The status codes differ anyway", "To keep the client simple"],
           1,
           "Username enumeration turns one hard guessing problem into two easy ones. A careful version also equalises the response TIME, not just the message."),
        _q("What is wrong with `tok_1`, `tok_2`, `tok_3` as real tokens?",
           ["They are too short to store", "They are trivially guessable — an attacker just counts",
            "They cannot be revoked", "Nothing"],
           1,
           "A credential must be unguessable. `crypto.randomBytes(32).toString(\"hex\")` is; a counter is the opposite of one."),
    ],
)

_P6_S3 = _step(
    "authenticate",
    "Checking the token: 401 versus 403",
    "Two different sentences: 'I don't know who you are' and 'I know, and no'.",
    """
A token is worthless unless every protected route actually checks it. Write that
check **once**.

### Do this

```js
function authenticate(req) {
  const header = req.headers.authorization ?? "";
  if (!header.startsWith("Bearer ")) return null;
  const token = header.slice("Bearer ".length);
  return tokens.get(token) ?? null;      // the username, or null
}
```

and at the top of every protected route:

```js
const username = authenticate(req);
if (!username) return send(res, 401, { error: "unauthorized" });
```

Node lowercases incoming header names, so it is `req.headers.authorization`,
never `req.headers.Authorization`. The `Bearer ` prefix is the scheme; the
format is `Authorization: Bearer <token>`.

### 401 versus 403

This is the pair people get wrong most often, and the distinction is simple:

- **401 Unauthorized** — *I do not know who you are.* No token, malformed token,
  unknown token, expired token. The name is a historical misnomer: 401 is about
  **authentication**.
- **403 Forbidden** — *I know exactly who you are, and you still may not.*
  Ada is logged in and asked for Bob's note.

The practical difference is what a client does next. A 401 means "log in again"
— and a browser app will redirect to the login screen. A 403 means "logging in
again will not help; you are simply not allowed". Return 403 where 401 belongs
and users get stuck; return 401 where 403 belongs and they get logged out for no
reason.

### Where the check has to be

Every protected route, without exception. The way to get that right is to stop
relying on remembering — put the check in one place that runs before routing.
That is what middleware is, and project 7 builds it.

### And the mistake this step exists to prevent

```js
if (req.headers.authorization) { /* let them in */ }   // WRONG
```

That accepts `Authorization: Bearer anything`. The header being *present* is not
the check; the token being *in your token store* is the check.
""",
    """
- A request with no `Authorization` header → 401 `{"error":"unauthorized"}`.
- `Authorization: Bearer made-up-token` → 401, not 200.
- A token from a real login → 200.
- Reaching for another user's note while logged in → 403, not 401.
""",
    pitfalls=[
        "Testing the header for truthiness accepts any garbage after `Bearer`.",
        "`req.headers.Authorization` is always undefined — Node lowercases header names.",
        "Returning 403 for a missing token makes clients that redirect on 401 hang instead of prompting for login.",
        "Forgetting the check on one route makes the other ten pointless.",
    ],
    warmup=[
        _q("Ada is logged in and requests Bob's note. Which status?",
           ["401 — she is not authorised", "403 — the server knows who she is and refuses anyway",
            "404 — she cannot see it", "400"],
           1,
           "401 means 'I don't know who you are' and tells the client to log in — which would not help Ada at all. 403 is the honest answer. (Some APIs deliberately return 404 to avoid confirming the note exists; that is a considered trade-off, not a default.)"),
    ],
    exercises=[
        _fix("be6-401", "The check that checks nothing",
             "Any `Authorization` header gets in, and a missing one is answered with 403. Verify the token against the store, and return 401 `{\"error\":\"unauthorized\"}` when it is missing or unknown.",
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

const tokens = new Map([["tok_1", "ada"]]);

function authenticate(req) {
  const header = req.headers.authorization ?? "";
  if (header) return header.slice("Bearer ".length);
  return null;
}

function handler(req, res) {
  const { pathname } = new URL(req.url, "http://localhost");
  if (pathname !== "/whoami") return send(res, 404, { error: "not_found" });
  const username = authenticate(req);
  if (!username) return send(res, 403, { error: "forbidden" });
  send(res, 200, { username });
}
""", imports=_AUTH_IMPORTS),
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

const tokens = new Map([["tok_1", "ada"]]);

function authenticate(req) {
  const header = req.headers.authorization ?? "";
  if (!header.startsWith("Bearer ")) return null;
  return tokens.get(header.slice("Bearer ".length)) ?? null;
}

function handler(req, res) {
  const { pathname } = new URL(req.url, "http://localhost");
  if (pathname !== "/whoami") return send(res, 404, { error: "not_found" });
  const username = authenticate(req);
  if (!username) return send(res, 401, { error: "unauthorized" });
  send(res, 200, { username });
}
""", imports=_AUTH_IMPORTS),
             [("GET /whoami @tok_1\nGET /whoami\nGET /whoami @made-up",
               '200 {"username":"ada"}\n401 {"error":"unauthorized"}\n401 {"error":"unauthorized"}'),
              ("GET /whoami @tok_2\nGET /whoami @tok_1\nGET /other @tok_1",
               '401 {"error":"unauthorized"}\n200 {"username":"ada"}\n404 {"error":"not_found"}')],
             hints=["What does the current `authenticate` return for `Bearer made-up`? It never consults the token store.",
                    "Check the `Bearer ` prefix, then look the token up in `tokens` — an unknown token is null.",
                    "Also fix the status: no usable token means 401 unauthorized, not 403."]),
    ],
    quiz=[
        _q("What does 401 actually mean?",
           ["You are not allowed", "I do not know who you are — authenticate and try again",
            "Your token expired", "The resource is private"],
           1,
           "Despite being named 'Unauthorized', 401 is about authentication. 403 is the one about permission."),
        _q("Why must the token be looked up rather than merely present?",
           ["To find the username", "Because otherwise `Bearer anything` is accepted as a valid login",
            "For performance", "To check expiry"],
           1,
           "Both, in fact — but the security point is decisive: presence of a header proves nothing about who sent it."),
    ],
)

_P6_S4 = _step(
    "ownership",
    "Ownership: your notes are yours",
    "Authentication says who you are. Authorisation says what that lets you touch.",
    """
Everyone shares one list of notes right now. Log in as Ada and you can read,
edit and delete Bob's notes. Authentication alone does not fix that —
**authorisation** does.

### Do this

1. Stamp every note with its owner at creation:

   ```js
   const note = { id: nextId++, title, done: false, owner: username };
   ```

2. Scope the collection so a list only ever shows your own:

   ```js
   const mine = [...notes.values()].filter((n) => n.owner === username);
   ```

3. Check ownership on every item route, **after** the 404:

   ```js
   const note = notes.get(id);
   if (!note) return send(res, 404, { error: "not_found" });
   if (note.owner !== username) return send(res, 403, { error: "forbidden" });
   ```

### The order of those two checks

404 first, then 403. That order says: *this note exists, and it is not yours.*
The alternative order — 403 before you have even looked — would return
"forbidden" for notes that do not exist, which is confusing and leaks nothing
useful in exchange.

There is a real argument for a **third** option: returning 404 for someone
else's note, so the API never confirms it exists at all. That is the right call
when the ids are guessable and the mere existence of a record is sensitive
(a medical record, a private repository). It is a deliberate trade — you are
choosing to confuse honest users a little to tell attackers nothing. This
project uses 403 because it is clearer to learn from; know that the other choice
exists and why you might make it.

### The mistake worth naming

**Filtering in the client is not authorisation.** If `GET /notes` returns
everyone's notes and the browser hides the ones that are not yours, then anyone
who opens the network tab has all of them. Every ownership rule has to live on
the server, because the server is the only part an attacker does not control.

Related: never accept the owner from the request body. `POST /notes {"owner":
"bob"}` must not create a note owned by Bob. The owner comes from the
authenticated token and from nowhere else — the same lesson as taking the id
from the URL in project 2, and mass assignment in project 3.
""",
    """
- Ada's `GET /notes` shows only Ada's notes.
- Ada reading Bob's note by id → 403; reading a note that does not exist → 404.
- Ada deleting Bob's note → 403, and Bob's note is still there.
- `POST /notes {"owner":"bob"}` creates a note owned by the caller, not by Bob.
""",
    pitfalls=[
        "Checking ownership before checking existence returns 403 for notes that never existed.",
        "Taking `owner` from the request body lets anyone create or move notes into another account.",
        "Filtering on the client is not access control — the response already left your server.",
        "Forgetting to scope the LIST while carefully guarding the item routes leaks every title anyway.",
    ],
    exercises=[
        _ch("be6-ownership", "Scope everything to the owner", "Medium",
            "Write the notes routes. Every request needs a valid token (401 otherwise). `GET /notes` lists only the caller's notes. `POST /notes` stamps the owner from the token, ignoring any `owner` in the body. `GET /notes/:id` and `DELETE /notes/:id` return 404 when there is no such note and 403 `{\"error\":\"forbidden\"}` when it belongs to somebody else.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

const tokens = new Map([["tok_ada", "ada"], ["tok_bob", "bob"]]);
const notes = new Map();
let nextId = 1;

function authenticate(req) {
  const header = req.headers.authorization ?? "";
  if (!header.startsWith("Bearer ")) return null;
  return tokens.get(header.slice("Bearer ".length)) ?? null;
}

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  const username = authenticate(req);
  if (!username) return send(res, 401, { error: "unauthorized" });

  if (rawId === undefined) {
    if (req.method === "GET") {
      return send(res, 200, [...notes.values()].filter((n) => n.owner === username));
    }
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = { id: nextId++, title: data.title ?? null, done: false, owner: username };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  if (note.owner !== username) return send(res, 403, { error: "forbidden" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "DELETE") {
    notes.delete(note.id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });
}
""", imports=_AUTH_IMPORTS),
            """  const username = authenticate(req);
  if (!username) return send(res, 401, { error: "unauthorized" });

  if (rawId === undefined) {
    if (req.method === "GET") {
      return send(res, 200, [...notes.values()].filter((n) => n.owner === username));
    }
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = { id: nextId++, title: data.title ?? null, done: false, owner: username };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  if (note.owner !== username) return send(res, 403, { error: "forbidden" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "DELETE") {
    notes.delete(note.id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });""",
            [('POST /notes @tok_ada {"title":"Ada note"}\nPOST /notes @tok_bob {"title":"Bob note"}\nGET /notes @tok_ada',
              '201 {"id":1,"title":"Ada note","done":false,"owner":"ada"}\n'
              '201 {"id":2,"title":"Bob note","done":false,"owner":"bob"}\n'
              '200 [{"id":1,"title":"Ada note","done":false,"owner":"ada"}]'),
             ('POST /notes @tok_bob {"title":"Bob note"}\nGET /notes/1 @tok_ada\nDELETE /notes/1 @tok_ada\nGET /notes/9 @tok_ada\nGET /notes/1 @tok_bob',
              '201 {"id":1,"title":"Bob note","done":false,"owner":"bob"}\n'
              '403 {"error":"forbidden"}\n403 {"error":"forbidden"}\n'
              '404 {"error":"not_found"}\n'
              '200 {"id":1,"title":"Bob note","done":false,"owner":"bob"}'),
             ('POST /notes {"title":"No token"}\nPOST /notes @nope {"title":"Bad token"}\nPOST /notes @tok_ada {"title":"Mine","owner":"bob"}\nGET /notes @tok_bob',
              '401 {"error":"unauthorized"}\n401 {"error":"unauthorized"}\n'
              '201 {"id":1,"title":"Mine","done":false,"owner":"ada"}\n'
              '200 []')],
            hints=["Authenticate once, before any routing decision — every branch below needs it.",
                   "The list must be filtered by owner; the item routes need 404 BEFORE 403 so 'forbidden' only ever means a note that really exists.",
                   "Third test: the body says `\"owner\":\"bob\"` and it must be ignored — the owner comes from the token."]),
    ],
    quiz=[
        _q("Why check 404 before 403 on an item route?",
           ["It is faster", "So 'forbidden' only ever means a note that actually exists",
            "403 requires a body", "It does not matter"],
           1,
           "Otherwise 403 becomes the answer for notes that never existed, which tells the client nothing true."),
        _q("Where must the `owner` of a new note come from?",
           ["The request body", "The authenticated token",
            "A query parameter", "Whichever is provided"],
           1,
           "Anything the client sends, the client controls. The token is the only statement about identity your server actually verified."),
    ],
)

_P6_FINAL = _ch(
    "be6-final", "The multi-user Notes API", "Hard",
    "Build the whole authenticated API. `POST /register` → 201 `{\"username\":…}` / 409 `user_exists` / 400 `validation_failed`. `POST /login` → 200 `{\"token\":\"tok_N\"}` / 401 `invalid_credentials` for both bad password and unknown user. Everything under `/notes` needs a valid bearer token (401 `unauthorized` otherwise). `GET /notes` lists only the caller's notes; `POST /notes` stamps the owner from the token; `GET`/`DELETE /notes/:id` give 404 when absent and 403 `forbidden` when owned by someone else. Passwords are stored only as salted hashes and never returned.",
    _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  return `${salt}:${crypto.scryptSync(password, salt, 32).toString("hex")}`;
}

function verifyPassword(attempt, record) {
  const [salt, hash] = record.split(":");
  return crypto.timingSafeEqual(
    crypto.scryptSync(attempt, salt, 32),
    Buffer.from(hash, "hex")
  );
}

const users = new Map();
const tokens = new Map();
const notes = new Map();
let nextToken = 1;
let nextId = 1;

function authenticate(req) {
  const header = req.headers.authorization ?? "";
  if (!header.startsWith("Bearer ")) return null;
  return tokens.get(header.slice("Bearer ".length)) ?? null;
}

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");

  if (resource === "register" || resource === "login") {
    if (req.method !== "POST") return send(res, 405, { error: "method_not_allowed" });
    const data = JSON.parse((await readBody(req)) || "{}");
    const { username, password } = data;

    if (resource === "register") {
      if (typeof username !== "string" || typeof password !== "string") {
        return send(res, 400, { error: "validation_failed" });
      }
      if (users.has(username)) return send(res, 409, { error: "user_exists" });
      users.set(username, { username, password: hashPassword(password) });
      return send(res, 201, { username });
    }

    const user = users.get(username);
    if (!user || !verifyPassword(password ?? "", user.password)) {
      return send(res, 401, { error: "invalid_credentials" });
    }
    const token = `tok_${nextToken++}`;
    tokens.set(token, username);
    return send(res, 200, { token });
  }

  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  const username = authenticate(req);
  if (!username) return send(res, 401, { error: "unauthorized" });

  if (rawId === undefined) {
    if (req.method === "GET") {
      return send(res, 200, [...notes.values()].filter((n) => n.owner === username));
    }
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = { id: nextId++, title: data.title ?? null, done: false, owner: username };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  if (note.owner !== username) return send(res, 403, { error: "forbidden" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "DELETE") {
    notes.delete(note.id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });
}
""", imports=_AUTH_IMPORTS),
    """  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");

  if (resource === "register" || resource === "login") {
    if (req.method !== "POST") return send(res, 405, { error: "method_not_allowed" });
    const data = JSON.parse((await readBody(req)) || "{}");
    const { username, password } = data;

    if (resource === "register") {
      if (typeof username !== "string" || typeof password !== "string") {
        return send(res, 400, { error: "validation_failed" });
      }
      if (users.has(username)) return send(res, 409, { error: "user_exists" });
      users.set(username, { username, password: hashPassword(password) });
      return send(res, 201, { username });
    }

    const user = users.get(username);
    if (!user || !verifyPassword(password ?? "", user.password)) {
      return send(res, 401, { error: "invalid_credentials" });
    }
    const token = `tok_${nextToken++}`;
    tokens.set(token, username);
    return send(res, 200, { token });
  }

  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  const username = authenticate(req);
  if (!username) return send(res, 401, { error: "unauthorized" });

  if (rawId === undefined) {
    if (req.method === "GET") {
      return send(res, 200, [...notes.values()].filter((n) => n.owner === username));
    }
    if (req.method === "POST") {
      const data = JSON.parse((await readBody(req)) || "{}");
      const note = { id: nextId++, title: data.title ?? null, done: false, owner: username };
      notes.set(note.id, note);
      return send(res, 201, note);
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = notes.get(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });
  if (note.owner !== username) return send(res, 403, { error: "forbidden" });

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "DELETE") {
    notes.delete(note.id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });""",
    [('POST /register {"username":"ada","password":"hunter2"}\nPOST /login {"username":"ada","password":"hunter2"}\nPOST /notes @tok_1 {"title":"Mine"}\nGET /notes @tok_1',
      '201 {"username":"ada"}\n200 {"token":"tok_1"}\n'
      '201 {"id":1,"title":"Mine","done":false,"owner":"ada"}\n'
      '200 [{"id":1,"title":"Mine","done":false,"owner":"ada"}]'),
     ('POST /register {"username":"ada","password":"pw"}\nPOST /register {"username":"ada","password":"pw"}\nPOST /register {"username":"bob"}\nPOST /login {"username":"ada","password":"nope"}\nPOST /login {"username":"ghost","password":"pw"}',
      '201 {"username":"ada"}\n409 {"error":"user_exists"}\n'
      '400 {"error":"validation_failed"}\n'
      '401 {"error":"invalid_credentials"}\n401 {"error":"invalid_credentials"}'),
     ('POST /register {"username":"ada","password":"pw"}\nPOST /register {"username":"bob","password":"pw"}\nPOST /login {"username":"ada","password":"pw"}\nPOST /login {"username":"bob","password":"pw"}\nPOST /notes @tok_1 {"title":"Ada"}\nPOST /notes @tok_2 {"title":"Bob","owner":"ada"}\nGET /notes @tok_1\nGET /notes/2 @tok_1\nDELETE /notes/2 @tok_1\nGET /notes/9 @tok_1',
      '201 {"username":"ada"}\n201 {"username":"bob"}\n'
      '200 {"token":"tok_1"}\n200 {"token":"tok_2"}\n'
      '201 {"id":1,"title":"Ada","done":false,"owner":"ada"}\n'
      '201 {"id":2,"title":"Bob","done":false,"owner":"bob"}\n'
      '200 [{"id":1,"title":"Ada","done":false,"owner":"ada"}]\n'
      '403 {"error":"forbidden"}\n403 {"error":"forbidden"}\n'
      '404 {"error":"not_found"}'),
     ('GET /notes\nGET /notes @tok_99\nGET /users @tok_1\nPUT /register',
      '401 {"error":"unauthorized"}\n401 {"error":"unauthorized"}\n'
      '404 {"error":"not_found"}\n405 {"error":"method_not_allowed"}')],
    hints=["Handle /register and /login first — they are the only routes that must work WITHOUT a token.",
           "Then one authenticate call guards everything under /notes; the two failure modes are 401 (no valid token) and 403 (valid token, someone else's note).",
           "Third test is the important one: Bob's POST carries `\"owner\":\"ada\"` and must still be owned by Bob, and Ada must get 403 — not 404 and not the note."])

_P6 = _project(
    "auth", 6,
    "Users, Tokens & Ownership",
    "Who are you, and what does that let you touch?",
    "Advanced",
    "Add registration with hashed passwords, token login, a single authentication check, and per-owner authorisation on every route.",
    "Authentication and authorisation are where mistakes stop being bugs and start being incidents. The four ideas here — never store a password, one error for both login failures, 401 versus 403, and never trust the client for identity — cover most of what goes wrong.",
    170,
    ["first-server", "notes-crud", "validation", "persistence"],
    ["password hashing", "scrypt", "bearer tokens", "401 vs 403", "authorisation", "ownership"],
    ["Store passwords as salted, deliberately slow hashes and verify them safely",
     "Exchange credentials for a token once, and check that token on every protected route",
     "Explain and correctly apply the 401/403 distinction",
     "Scope every read and write to the authenticated owner",
     "Name three ways an auth implementation leaks information it should not"],
    """
The API has been single-user so far: everything belongs to everybody. Now it
gets accounts.

You will add `POST /register` and `POST /login`, store passwords as salted scrypt
hashes, hand out a token on login, check that token in one place, and stamp
every note with its owner so that Ada cannot read, edit or delete Bob's notes.

Two honest caveats about what this project is and is not. The tokens are
counters (`tok_1`) purely so the drills have predictable output — real ones are
random and expire, and the lesson says exactly where. And there is no HTTPS
here: over plain HTTP, a token is readable by anything on the network path. In
production, authentication without TLS is not authentication.
""",
    [_ep("POST", "/register", "Create an account", '{"username":"ada","password":"…"}', '{"username":"ada"}', "201 · 400 · 409"),
     _ep("POST", "/login", "Exchange credentials for a token", '{"username":"ada","password":"…"}', '{"token":"tok_1"}', "200 · 401"),
     _ep("GET", "/notes", "List YOUR notes", "Bearer token", "[…]", "200 · 401"),
     _ep("POST", "/notes", "Create, owned by you", '{"title":"…"}', '{"id":1,…,"owner":"ada"}', "201 · 401"),
     _ep("GET", "/notes/:id", "Read one of yours", "Bearer token", '{"id":1,…}', "200 · 401 · 403 · 404"),
     _ep("DELETE", "/notes/:id", "Delete one of yours", "Bearer token", "(empty)", "204 · 401 · 403 · 404")],
    """
Same folder. This project adds a third module:

```
notes-api/
  server.js
  store.js
  auth.js      hashing, the user store, the token store
  notes.json
```

```
cd notes-api
node server.js
```

Sending a token with curl:

```
curl -H "Authorization: Bearer tok_1" http://localhost:3000/notes
```

A convenient shell habit while testing:

```
TOKEN=$(curl -s -X POST http://localhost:3000/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"ada","password":"hunter2"}' | sed 's/.*"token":"//;s/".*//')

curl -H "Authorization: Bearer $TOKEN" http://localhost:3000/notes
```
""",
    [_P6_S1, _P6_S2, _P6_S3, _P6_S4],
    final_build=_P6_FINAL,
    acceptance=[
        "No stored record contains a plaintext password, and no response ever returns one.",
        "Registering the same password twice produces two different stored records — the salts differ.",
        "`POST /register` returns only the username; duplicates return 409 and missing fields return 400.",
        "A wrong password and an unknown username return the identical 401 `invalid_credentials`.",
        "`Authorization: Bearer made-up` returns 401, not 200 — the token is looked up, not merely present.",
        "A missing token returns 401; another user's note returns 403.",
        "`GET /notes` shows only the caller's notes.",
        "`POST /notes {\"owner\":\"bob\"}` creates a note owned by the caller.",
        "A note that does not exist returns 404 even for its would-be owner — 404 is checked before 403.",
        "Password verification uses `timingSafeEqual`, not `===`.",
    ],
    manual_test="""
```
# register two users
curl -i -X POST http://localhost:3000/register \\
  -H "Content-Type: application/json" -d '{"username":"ada","password":"hunter2"}'
curl -i -X POST http://localhost:3000/register \\
  -H "Content-Type: application/json" -d '{"username":"bob","password":"hunter2"}'

# duplicate → 409; missing field → 400
curl -i -X POST http://localhost:3000/register \\
  -H "Content-Type: application/json" -d '{"username":"ada","password":"x"}'

# both failures look identical
curl -i -X POST http://localhost:3000/login \\
  -H "Content-Type: application/json" -d '{"username":"ada","password":"wrong"}'
curl -i -X POST http://localhost:3000/login \\
  -H "Content-Type: application/json" -d '{"username":"ghost","password":"wrong"}'

# log in as each user, keep both tokens
curl -X POST http://localhost:3000/login \\
  -H "Content-Type: application/json" -d '{"username":"ada","password":"hunter2"}'
curl -X POST http://localhost:3000/login \\
  -H "Content-Type: application/json" -d '{"username":"bob","password":"hunter2"}'

# no token, then a made-up one — both 401
curl -i http://localhost:3000/notes
curl -i -H "Authorization: Bearer made-up" http://localhost:3000/notes

# ada creates a note and tries to claim it for bob — the owner must be ada
curl -i -X POST http://localhost:3000/notes \\
  -H "Authorization: Bearer <ADA_TOKEN>" -H "Content-Type: application/json" \\
  -d '{"title":"Ada only","owner":"bob"}'

# bob cannot see or delete it — 403, not 404 and not 200
curl -i -H "Authorization: Bearer <BOB_TOKEN>" http://localhost:3000/notes
curl -i -H "Authorization: Bearer <BOB_TOKEN>" http://localhost:3000/notes/1
curl -i -X DELETE -H "Authorization: Bearer <BOB_TOKEN>" http://localhost:3000/notes/1
```

Then open the stored user records and confirm you cannot find either password
anywhere in them.
""",
    reference="""
// ------------------------------------------------------------------ auth.js --
import crypto from "node:crypto";

const users = new Map();      // username -> { username, password: "salt:hash" }
const tokens = new Map();     // token    -> username
let nextToken = 1;

export function hashPassword(password) {
  // A fresh salt per user: identical passwords must not produce identical hashes.
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto.scryptSync(password, salt, 32).toString("hex");
  return `${salt}:${hash}`;
}

export function verifyPassword(attempt, record) {
  const [salt, hash] = record.split(":");
  const attemptHash = crypto.scryptSync(attempt, salt, 32);
  // Constant time: `===` would leak the answer through how long it takes.
  return crypto.timingSafeEqual(attemptHash, Buffer.from(hash, "hex"));
}

export function register(username, password) {
  if (users.has(username)) return null;
  const user = { username, password: hashPassword(password) };
  users.set(username, user);
  return { username };
}

export function login(username, password) {
  const user = users.get(username);
  // ONE answer for both failures — never confirm which usernames exist.
  if (!user || !verifyPassword(password ?? "", user.password)) return null;
  // Real tokens: crypto.randomBytes(32).toString("hex"), with an expiry.
  const token = `tok_${nextToken++}`;
  tokens.set(token, username);
  return token;
}

/** The authenticated username, or null. */
export function authenticate(req) {
  const header = req.headers.authorization ?? "";
  if (!header.startsWith("Bearer ")) return null;
  return tokens.get(header.slice("Bearer ".length)) ?? null;
}

// ---------------------------------------------------------------- server.js --
// (excerpt: the parts this project adds)

async function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");

  // --- public routes -------------------------------------------------------
  if (resource === "register" && req.method === "POST") {
    const { username, password } = await readJson(req);
    if (typeof username !== "string" || typeof password !== "string") {
      return send(res, 400, { error: "validation_failed" });
    }
    const created = auth.register(username, password);
    if (!created) return send(res, 409, { error: "user_exists" });
    return send(res, 201, created);
  }

  if (resource === "login" && req.method === "POST") {
    const { username, password } = await readJson(req);
    const token = auth.login(username, password);
    if (!token) return send(res, 401, { error: "invalid_credentials" });
    return send(res, 200, { token });
  }

  if (resource !== "notes") return send(res, 404, { error: "not_found" });

  // --- everything below needs a token ---------------------------------------
  const username = auth.authenticate(req);
  if (!username) return send(res, 401, { error: "unauthorized" });

  if (rawId === undefined) {
    if (req.method === "GET") {
      return send(res, 200, store.list().filter((n) => n.owner === username));
    }
    if (req.method === "POST") {
      const data = await readJson(req);
      // The owner comes from the TOKEN, never from the body.
      return send(res, 201, store.create({ ...data, owner: username }));
    }
    return send(res, 405, { error: "method_not_allowed" });
  }

  const note = store.find(Number(rawId));
  if (!note) return send(res, 404, { error: "not_found" });          // 404 first…
  if (note.owner !== username) return send(res, 403, { error: "forbidden" });  // …then 403

  if (req.method === "GET") return send(res, 200, note);
  if (req.method === "DELETE") {
    store.remove(note.id);
    return send(res, 204, null);
  }
  return send(res, 405, { error: "method_not_allowed" });
}
""",
    stretch=[
        "Give tokens an expiry: store `{ username, expiresAt }` and treat an expired token as 401. Then add `POST /logout` that deletes it — and notice that this is trivial for server-side tokens and impossible for a plain JWT.",
        "Swap `tok_N` for `crypto.randomBytes(32).toString(\"hex\")` and watch every hard-coded token in your notes stop working. That is the correct outcome.",
        "Add rate limiting on /login: after five failures for a username, refuse for a minute with 429. Brute force is the attack this actually stops.",
        "Add roles: an `admin` may read anyone's notes. Then look for every place you wrote `note.owner !== username` and think about how many places a rule like this needs to be right.",
        "Read about JWTs and write down, in your own words, what you would gain and lose by replacing this token map with one.",
    ],
    glossary=[
        _gloss("authentication", "Establishing who is making the request. Failure is 401."),
        _gloss("authorisation", "Deciding what that identity may do. Failure is 403."),
        _gloss("salt", "Random per-user data mixed into a password hash so identical passwords hash differently. Not secret."),
        _gloss("scrypt", "A deliberately slow, memory-hard hash designed for passwords. bcrypt and argon2 are the alternatives."),
        _gloss("bearer token", "A credential sent as `Authorization: Bearer <token>`. Whoever holds it is treated as the user — so it must be unguessable and travel over TLS."),
        _gloss("timing attack", "Deducing a secret from how long a comparison takes. Defeated by constant-time comparison."),
        _gloss("username enumeration", "Learning which accounts exist from differing error messages or response times."),
        _gloss("mass assignment", "Letting a request body set fields it should not — such as `owner`."),
    ],
    cheatsheet="""
```js
import crypto from "node:crypto";

// store a password
const salt = crypto.randomBytes(16).toString("hex");            // per user, not secret
const hash = crypto.scryptSync(password, salt, 32).toString("hex");
const record = `${salt}:${hash}`;                               // never the plaintext

// check one
crypto.timingSafeEqual(crypto.scryptSync(attempt, salt, 32), Buffer.from(hash, "hex"));

// read the token (Node LOWERCASES header names)
const header = req.headers.authorization ?? "";
if (!header.startsWith("Bearer ")) return null;
return tokens.get(header.slice("Bearer ".length)) ?? null;      // look it UP

// order on every item route
if (!note) → 404          // does it exist?
if (note.owner !== me) → 403   // is it mine?
```

| Situation | Status | Code |
| --- | --- | --- |
| No / bad / unknown token | 401 | `unauthorized` |
| Wrong password OR unknown user | 401 | `invalid_credentials` |
| Valid token, someone else's note | 403 | `forbidden` |
| No such note | 404 | `not_found` |
| Username taken | 409 | `user_exists` |
""",
    self_check=[
        "I can explain what a salt does and why it is not a secret.",
        "I can say why scrypt is preferred over SHA-256 here, in terms of speed.",
        "I can state the difference between 401 and 403 and what a client does with each.",
        "I know three ways an auth endpoint can leak which usernames exist.",
        "I can point at the line that stops a client from choosing a note's owner.",
    ],
    review=[
        _q("Two users pick the same password. With per-user salts, what do their stored records look like?",
           ["Identical", "Different, because the salts differ",
            "Different only if the usernames differ", "Identical but with different lengths"],
           1,
           "That is the entire purpose of a salt: it makes cracking one record useless against any other."),
        _q("Your API returns 403 when no token is supplied. What breaks?",
           ["Nothing", "Clients that redirect to login on 401 never prompt the user — they just see a refusal",
            "The token store", "CORS"],
           1,
           "401 and 403 drive different client behaviour. Confusing them means a logged-out user is told they are forbidden rather than being asked to log in."),
        _q("`POST /notes {\"title\":\"x\",\"owner\":\"admin\"}` with Ada's valid token. What must happen?",
           ["403 forbidden", "The note is created owned by ada — the body's owner is ignored",
            "400, because owner is not allowed", "The note is created owned by admin"],
           1,
           "Rejecting it with 400 is also defensible. What is never acceptable is honouring it: identity comes from the token."),
        _q("Why is `crypto.timingSafeEqual` needed when `===` gives the same answer?",
           ["=== does not work on Buffers", "=== returns early on the first difference, and that timing leaks the secret",
            "=== is deprecated", "timingSafeEqual is faster"],
           1,
           "Both are true of Buffers, but the security reason is the timing leak — measurable across many requests, and enough to reconstruct a value byte by byte."),
    ],
    milestone="Your API has accounts, and one user's data is genuinely out of another user's reach.",
)

_PROJECTS.append(_P6)


# ===========================================================================
# PROJECT 7 — Refactor to Layers & Write Tests
# ===========================================================================

_MATCH_DRIVER = """
// ---- matcher driver (given — don't edit) -----------------------------------
// stdin: one case per line —  <pattern> <path>
for (const line of fs.readFileSync(0, "utf8").split("\\n")) {
  const [pattern, path] = line.trim().split(" ");
  if (!pattern) continue;
  console.log(JSON.stringify(matchRoute(pattern, path)));
}
"""

_SUITE_DRIVER = """
// ---- suite driver (given — don't edit) -------------------------------------
// stdin: one case per line —  <name> | <actual json> | <expected json>
for (const line of fs.readFileSync(0, "utf8").split("\\n")) {
  const text = line.trim();
  if (!text) continue;
  const [name, actual, expected] = text.split(" | ");
  test(name, () => assertEqual(JSON.parse(actual), JSON.parse(expected)));
}
console.log(`${passed} passed, ${failed} failed`);
"""


def _match_prog(code):
    return 'import fs from "node:fs";\n\n' + _bp(code) + "\n" + _bp(_MATCH_DRIVER)


def _suite_prog(code):
    return 'import fs from "node:fs";\n\n' + _bp(code) + "\n" + _bp(_SUITE_DRIVER)


_P7_S1 = _step(
    "router",
    "A route table with path parameters",
    "Stop parsing paths by hand; declare them instead.",
    """
Your handler has grown a staircase of `if` statements that pick apart
`pathname.split("/")` by index. It works, and it stops working the moment you
add `/notes/:id/comments`. Time to write the thing every framework has: a
**route table** and a **matcher**.

### Do this

1. Write the matcher. Given a pattern and a path, it returns the captured
   parameters, or `null` for no match:

   ```js
   function matchRoute(pattern, path) {
     const p = pattern.split("/");
     const s = path.split("/");
     if (p.length !== s.length) return null;

     const params = {};
     for (let i = 0; i < p.length; i++) {
       if (p[i].startsWith(":")) params[p[i].slice(1)] = s[i];
       else if (p[i] !== s[i]) return null;
     }
     return params;
   }
   ```

   `matchRoute("/notes/:id", "/notes/17")` gives `{ id: "17" }`.
   `matchRoute("/notes/:id", "/notes")` gives `null` — different lengths.

2. Declare the routes as data instead of control flow:

   ```js
   const routes = [
     { method: "GET",    path: "/notes",     fn: listNotes },
     { method: "POST",   path: "/notes",     fn: createNote },
     { method: "GET",    path: "/notes/:id", fn: getNote },
     { method: "DELETE", path: "/notes/:id", fn: deleteNote },
   ];
   ```

3. Dispatch, keeping 405 alive:

   ```js
   let pathMatched = false;
   for (const route of routes) {
     const params = matchRoute(route.path, url.pathname);
     if (params === null) continue;
     pathMatched = true;                       // the PATH exists…
     if (route.method !== req.method) continue; // …but maybe not with this verb
     return route.fn({ params, body });
   }
   // no route ran:
   throw new HttpError(pathMatched ? 405 : 404, pathMatched ? "method_not_allowed" : "not_found");
   ```

   The `pathMatched` flag is doing the same job the nested `if`s did in project
   1: remembering that the path was real so a wrong verb can still be a 405.

### Two things to notice

- **`null` and `{}` are different answers.** `/notes` matching `/notes` is a
  *success* that captured nothing, so it returns an empty object; `null` is
  reserved for "did not match". Keeping those apart is the contract. `if
  (!params) continue;` happens to work — but only because `null` was chosen for
  the miss and `{}` is truthy. Have the matcher return `false` for a miss one
  day, or `{}`, and the loop silently takes the wrong branch. `params === null`
  states the rule instead of relying on which values happen to be falsy.
- **Params are always strings.** `{ id: "17" }`, never `17`. The same `Number()`
  conversion you have been doing since project 2 still applies — a router does
  not know your ids are numbers.

### What you just built

That is the core of Express's router, minus wildcards, regex segments and
mounting. It is worth having written once: `app.get("/notes/:id", …)` stops
being magic and becomes "a matcher and a loop", and you gain the ability to
reason about why route order matters.
""",
    """
- `matchRoute("/notes/:id", "/notes/17")` → `{id: "17"}`.
- `matchRoute("/notes", "/notes")` → `{}` (empty, but a match).
- `matchRoute("/notes/:id", "/notes")` → `null`.
- `GET /nope` → 404 and `PUT /notes/1` → 405, with the table doing the work.
""",
    pitfalls=[
        "Signalling 'no match' with an empty object instead of `null` makes it indistinguishable from a successful match on a pattern that captures nothing.",
        "Comparing segment counts is what stops `/notes/:id` matching `/notes`. Skip it and you get `{id: undefined}`.",
        "Route parameters are strings. `params.id` is `\"17\"`.",
        "Losing the `pathMatched` flag collapses 405 back into 404.",
    ],
    warmup=[
        _q("`matchRoute(\"/notes\", \"/notes\")` returns `{}`, not `true` and not `null`. Why?",
           ["`{}` is falsy, which stops the loop",
            "A match always returns the captures — empty here — while `null` stays reserved for 'no match'",
            "It should return true; `{}` is a bug",
            "There is no difference between `{}` and `null` to the caller"],
           1,
           "Matching and capturing are two different questions. Every match answers with an object the caller can read params from, even when there are none; only a miss is null. Collapse those and 'matched nothing' becomes indistinguishable from 'did not match'."),
    ],
    exercises=[
        _ex("be7-match", "Match a path pattern",
            "Finish `matchRoute`. Return an object of captured parameters when the pattern matches, and `null` when it does not. Segments beginning with `:` capture; every other segment must match exactly.",
            _match_prog("""
function matchRoute(pattern, path) {
  const p = pattern.split("/");
  const s = path.split("/");
  if (p.length !== s.length) return null;

  const params = {};
  for (let i = 0; i < p.length; i++) {
    if (p[i].startsWith(":")) params[p[i].slice(1)] = s[i];
    else if (p[i] !== s[i]) return null;
  }
  return params;
}
"""),
            """    if (p[i].startsWith(":")) params[p[i].slice(1)] = s[i];
    else if (p[i] !== s[i]) return null;""",
            [("/notes/:id /notes/17\n/notes /notes\n/notes/:id /notes",
              '{"id":"17"}\n{}\nnull'),
             ("/notes /notes/17\n/users/:uid/notes/:id /users/7/notes/3\n/notes/:id /users/17\n/notes/:id /notes/abc",
              'null\n{"uid":"7","id":"3"}\nnull\n{"id":"abc"}')],
            hints=["Walk the two segment arrays together; the lengths were already checked.",
                   "A segment starting with `:` captures — its name is the segment minus the colon.",
                   "Any literal segment that differs means the whole pattern fails: return null immediately."]),
    ],
    quiz=[
        _q("Why does the matcher compare segment counts first?",
           ["For speed", "So `/notes/:id` cannot match `/notes` and capture undefined",
            "Because split returns different types", "It does not need to"],
           1,
           "Without it, the loop would run over a shorter array and capture `undefined` as the id — a match that should never have happened."),
        _q("What type is `params.id` after matching `/notes/17`?",
           ["number", "string", "undefined", "It depends on the pattern"],
           1,
           "Paths are text. The router captures `\"17\"`, and converting it is still your job."),
    ],
)

_P7_S2 = _step(
    "middleware",
    "Middleware: the things every request needs",
    "Cross-cutting work belongs in one chain, not in twelve handlers.",
    """
Some work has to happen on every request — logging it, parsing the body,
checking the token. Copying that into each handler means the day you add the
thirteenth handler is the day one of them is missing the auth check.

A **middleware chain** is a list of functions that each get a look at the
request before your handler does. Any one of them may answer and stop the chain.

### Do this

1. Give each request a small **context** object for the things middleware
   discovers, so nothing has to be bolted onto `req`:

   ```js
   const ctx = { params: {}, body: {}, user: null };
   ```

2. Write middleware that returns `true` when it has already responded:

   ```js
   const middleware = [
     (req, res, ctx) => { ctx.startedAt = Date.now(); },

     async (req, res, ctx) => {
       const raw = await readBody(req);
       if (!raw) return;
       try {
         ctx.body = JSON.parse(raw);
       } catch {
         send(res, 400, { error: "invalid_json" });
         return true;                       // answered — stop here
       }
     },

     (req, res, ctx) => {
       const user = authenticate(req);
       if (!user) {
         send(res, 401, { error: "unauthorized" });
         return true;
       }
       ctx.user = user;
     },
   ];
   ```

3. Run them in order, stopping at the first one that answered:

   ```js
   for (const mw of middleware) {
     if (await mw(req, res, ctx)) return;    // it replied; we are done
   }
   // …only now dispatch to the route
   ```

### Why order is the whole design

The list reads top to bottom, and that is exactly the order things happen:
timing starts, then the body is parsed, then the caller is identified, then your
handler runs knowing all three are settled. Move authentication above body
parsing and you reject bad tokens without reading the body — slightly faster,
and it means your logs never contain the body of an unauthenticated request.
These are real design decisions, and they are visible because the chain is a
list you can read.

### How this differs from Express

Express passes each middleware a `next` callback, and not calling it stops the
chain. The version here uses a return value instead, because it is simpler to
follow and does the same thing. Both are the same idea: **a pipeline you can
add a stage to without touching any handler.**

### The rule the chain enforces

Once you have this, "did I remember the auth check on that route?" stops being a
question. That is the real value — not less typing, but a class of mistake you
can no longer make.
""",
    """
- A request with no token is rejected by the chain, and the route function never runs.
- A malformed body is rejected before any handler sees it.
- A valid request reaches the handler with `ctx.body` and `ctx.user` already set.
- Adding a new route needs no auth code at all.
""",
    pitfalls=[
        "Forgetting to `await` an async middleware means the chain runs on before the body has arrived.",
        "Middleware that responds but does not signal a stop leaves the chain running, producing a second reply and a crash.",
        "Putting body parsing after authentication is a real choice — just make it on purpose, not by accident.",
    ],
    exercises=[
        _ch("be7-middleware", "Run the chain", "Medium",
            "Write `runMiddleware` and the dispatch that follows it. Run each middleware in order, `await`ing it; if one returns true it has already responded, so stop. If the chain finishes, reply 200 with `{\"user\":…,\"n\":…,\"path\":…}` from the context.",
            _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

const tokens = new Map([["tok_1", "ada"]]);
let counter = 0;

// ---- the chain (given) -----------------------------------------------------
const middleware = [
  (req, res, ctx) => {
    ctx.n = ++counter;
  },
  (req, res, ctx) => {
    if (req.method !== "GET") {
      send(res, 405, { error: "method_not_allowed" });
      return true;
    }
  },
  (req, res, ctx) => {
    const header = req.headers.authorization ?? "";
    const user = header.startsWith("Bearer ")
      ? tokens.get(header.slice("Bearer ".length))
      : undefined;
    if (!user) {
      send(res, 401, { error: "unauthorized" });
      return true;
    }
    ctx.user = user;
  },
];

async function runMiddleware(req, res, ctx) {
  for (const mw of middleware) {
    if (await mw(req, res, ctx)) return true;
  }
  return false;
}

async function handler(req, res) {
  const ctx = { user: null, n: 0, path: new URL(req.url, "http://localhost").pathname };
  if (await runMiddleware(req, res, ctx)) return;
  send(res, 200, { user: ctx.user, n: ctx.n, path: ctx.path });
}
"""),
            """async function runMiddleware(req, res, ctx) {
  for (const mw of middleware) {
    if (await mw(req, res, ctx)) return true;
  }
  return false;
}

async function handler(req, res) {
  const ctx = { user: null, n: 0, path: new URL(req.url, "http://localhost").pathname };
  if (await runMiddleware(req, res, ctx)) return;
  send(res, 200, { user: ctx.user, n: ctx.n, path: ctx.path });
}""",
            [("GET /notes @tok_1", '200 {"user":"ada","n":1,"path":"/notes"}'),
             ("GET /notes @tok_1\nPOST /notes @tok_1\nGET /notes",
              '200 {"user":"ada","n":1,"path":"/notes"}\n'
              '405 {"error":"method_not_allowed"}\n'
              '401 {"error":"unauthorized"}'),
             ("GET /a @tok_1\nGET /b @bad\nGET /c @tok_1",
              '200 {"user":"ada","n":1,"path":"/a"}\n'
              '401 {"error":"unauthorized"}\n'
              '200 {"user":"ada","n":3,"path":"/c"}')],
            hints=["Loop the array in order and `await` each call — one of them may be async in a real chain.",
                   "A middleware returning true means it has already replied: stop the loop and tell the caller.",
                   "Third test proves the counter middleware runs even for requests the chain later rejects — the third request is number 3, not number 2."]),
    ],
    quiz=[
        _q("A middleware sends a 401 but returns nothing. What happens?",
           ["Nothing — the chain stops anyway", "The chain continues and the handler replies again, which throws",
            "Node retries the request", "The 401 is discarded"],
           1,
           "Sending a response does not stop your loop. Without the stop signal you get a second `res.end()` and ERR_STREAM_WRITE_AFTER_END."),
        _q("What is the main benefit of a middleware chain over calling `authenticate()` in each handler?",
           ["It is faster", "A route cannot accidentally be missing the check",
            "It allows async code", "It makes handlers shorter"],
           1,
           "The last two are pleasant; the first is the point. Cross-cutting rules should not depend on remembering."),
    ],
)

_P7_S3 = _step(
    "errors",
    "One error path, and nothing leaks",
    "Throw a typed error where the problem is; translate it in exactly one place.",
    """
Look at how a failure travels through your code now: every route that cannot
find a note constructs a 404 response itself. That is fine for four routes and
unmanageable for forty, and it means the shape of your errors is defined in
forty places.

Better: **throw where the problem is, translate where the response is made.**

### Do this

1. A typed error that carries its own status:

   ```js
   class HttpError extends Error {
     constructor(status, code) {
       super(code);
       this.status = status;
       this.code = code;
     }
   }
   ```

2. Throw it from anywhere — including deep inside the store, where there is no
   `res` to reply with:

   ```js
   function mustFind(rawId) {
     const note = notes.get(Number(rawId));
     if (!note) throw new HttpError(404, "not_found");
     return note;
   }
   ```

   Handlers become the thing they should have been all along: the happy path.

3. Translate once, at the boundary:

   ```js
   try {
     // …routing and dispatch…
   } catch (err) {
     if (err instanceof HttpError) return send(res, err.status, { error: err.code });
     console.error(err);                                  // full detail: your logs
     send(res, 500, { error: "server_error" });           // opaque: the client
   }
   ```

### The two halves of that catch

They are doing opposite jobs on purpose.

- An `HttpError` is **expected**. You threw it deliberately, its code is part of
  your API, and the client is meant to read it.
- Anything else is a **bug**. The client gets `server_error` and nothing more,
  while the full stack goes to your logs.

Never `send(res, 500, { error: err.message })`. A stack trace or an exception
message tells a stranger your file paths, your library versions, sometimes a
connection string with credentials in it. Verbose errors are a genuine
information-disclosure vulnerability, and they are usually introduced during
debugging by someone who meant to take them out again.

### And the log line

`console.error(err)` is not optional. The client gets an opaque answer, so the
detail has to survive *somewhere*, or you have made your own service
undebuggable to protect it from strangers. Opaque outward, verbose inward.
""",
    """
- A missing note gives 404 `not_found`, thrown from the store, not built in the route.
- An unexpected exception gives 500 `{"error":"server_error"}` and nothing else.
- The full stack trace appears in your terminal.
- No route builds an error response itself any more.
""",
    pitfalls=[
        "`send(res, 500, { error: err.message })` leaks file paths, library versions and sometimes credentials.",
        "Catching everything and returning 500 hides your deliberate 404s and 400s — check `instanceof HttpError` first.",
        "Swallowing the error without logging it makes your own service undebuggable.",
        "Throwing after the response has been sent — check `res.headersSent` before writing in the catch.",
    ],
    warmup=[
        _q("Your catch does `send(res, 500, { error: err.message })`. A database call fails. What might a stranger now see?",
           ["Nothing useful", "The connection string, file paths, or library internals",
            "Only the status code", "The request they sent"],
           1,
           "Exception messages are written for you, not for the public. That is why the outward answer must be opaque and the inward one verbose."),
    ],
    exercises=[
        _fix("be7-leak", "The catch that says too much",
             "Every failure becomes a 500, and the message is handed straight to the client. Fix the handler: an `HttpError` keeps its own status and code; anything else is an opaque 500 `{\"error\":\"server_error\"}`.",
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

class HttpError extends Error {
  constructor(status, code) {
    super(code);
    this.status = status;
    this.code = code;
  }
}

const notes = new Map([[1, { id: 1, title: "Buy milk", done: false }]]);

function mustFind(rawId) {
  const note = notes.get(Number(rawId));
  if (!note) throw new HttpError(404, "not_found");
  return note;
}

function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  try {
    if (resource === "boom") throw new Error("db://user:hunter2@localhost refused");
    if (resource !== "notes") throw new HttpError(404, "not_found");
    if (rawId === undefined) return send(res, 200, [...notes.values()]);
    send(res, 200, mustFind(rawId));
  } catch (err) {
    send(res, 500, { error: err.message });
  }
}
"""),
             _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

class HttpError extends Error {
  constructor(status, code) {
    super(code);
    this.status = status;
    this.code = code;
  }
}

const notes = new Map([[1, { id: 1, title: "Buy milk", done: false }]]);

function mustFind(rawId) {
  const note = notes.get(Number(rawId));
  if (!note) throw new HttpError(404, "not_found");
  return note;
}

function handler(req, res) {
  const [, resource, rawId] = new URL(req.url, "http://localhost").pathname.split("/");
  try {
    if (resource === "boom") throw new Error("db://user:hunter2@localhost refused");
    if (resource !== "notes") throw new HttpError(404, "not_found");
    if (rawId === undefined) return send(res, 200, [...notes.values()]);
    send(res, 200, mustFind(rawId));
  } catch (err) {
    if (err instanceof HttpError) return send(res, err.status, { error: err.code });
    console.error(err);
    send(res, 500, { error: "server_error" });
  }
}
"""),
             [("GET /notes/1\nGET /notes/9\nGET /boom",
               '200 {"id":1,"title":"Buy milk","done":false}\n'
               '404 {"error":"not_found"}\n'
               '500 {"error":"server_error"}'),
              ("GET /users\nGET /notes\nGET /boom",
               '404 {"error":"not_found"}\n'
               '200 [{"id":1,"title":"Buy milk","done":false}]\n'
               '500 {"error":"server_error"}')],
             hints=["Two kinds of thing arrive in that catch, and they deserve opposite treatment.",
                    "An HttpError already knows its status and its public code — use them.",
                    "Everything else is a bug: log the real error to stderr, and tell the client only `server_error`."]),
    ],
    quiz=[
        _q("Why check `instanceof HttpError` before falling back to 500?",
           ["For performance", "Otherwise your deliberate 404s and 400s are all reported as server bugs",
            "Because HttpError has no message", "To rethrow it"],
           1,
           "A blanket 500 destroys the distinction the whole error contract is built on — and makes your alerting fire on ordinary client mistakes."),
        _q("What is the right split between what the client sees and what you log?",
           ["Both get the full message", "Client gets an opaque code; your logs get the full stack",
            "Both get only the status", "Client gets the stack; logs get the code"],
           1,
           "Opaque outward, verbose inward. Either half alone is a mistake: one leaks, the other makes your service undebuggable."),
    ],
)

_P7_S4 = _step(
    "tests",
    "Write the tests yourself",
    "A test runner is thirty lines. Knowing that changes how you think about testing.",
    """
You have been checking this API by hand with `curl` for six projects. That does
not scale, and it does not protect you from breaking project 2 while writing
project 7. Time to automate it — starting by writing the runner, so that
`describe`/`it`/`expect` stop looking like a language feature.

### Do this

```js
let passed = 0;
let failed = 0;

function assertEqual(actual, expected) {
  const a = JSON.stringify(actual);
  const b = JSON.stringify(expected);
  if (a !== b) throw new Error(`expected ${b}, got ${a}`);
}

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`PASS ${name}`);
  } catch (err) {
    failed++;
    console.log(`FAIL ${name}: ${err.message}`);
  }
}
```

That is the whole idea. **A failing assertion is a thrown error; a test runner
is a try/catch with a counter.** Everything a real framework adds — async
support, nested suites, watch mode, better diffs, parallelism — is convenience
on top of these fifteen lines.

Comparing with `JSON.stringify` gives you deep equality for free. It is not
perfect: key order matters, and `undefined` values disappear. Knowing the
limitation is better than not knowing you had one.

### Then test the API, not just the functions

Two kinds of test, and you want both:

- **Unit tests** for the pure pieces — `validate`, `parseQuery`, `matchRoute`,
  `compare`. No server, no ports, instant. This is the payoff for having kept
  them pure since project 3.
- **Integration tests** that boot the real server on port 0 and send real
  requests:

  ```js
  const server = http.createServer(handler);
  await new Promise((ok) => server.listen(0, ok));
  const base = `http://127.0.0.1:${server.address().port}`;

  const res = await fetch(`${base}/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "Buy milk" }),
  });
  assertEqual(res.status, 201);
  ```

  **Port 0 means "any free port"**, which is how tests avoid colliding with your
  running dev server — and with each other. It is the same trick the drills in
  this whole track have been using.

### Red, then green

Write the test **before** the fix. A test you have never seen fail is a test you
have no reason to trust — plenty of them pass because they assert nothing.
Watch it fail for the right reason, then make it pass.

Node also ships `node --test` and `node:assert`, which are worth using once you
have written this. But write this first.
""",
    """
- `node test.js` prints a PASS or FAIL line per test and a summary.
- A deliberately broken assertion prints FAIL with the expected and actual values.
- Tests cover both the pure functions and the running server.
- You have watched at least one test fail before making it pass.
""",
    pitfalls=[
        "A test with no assertion always passes. Break it on purpose once to prove it can fail.",
        "Hard-coding port 3000 in tests collides with your dev server. Use port 0.",
        "Tests that share state pass alone and fail together. Reset the store between them.",
        "JSON.stringify equality depends on key order and drops undefined — fine, as long as you know it.",
    ],
    warmup=[
        _q("Why insist on watching a new test fail before you make it pass?",
           ["It is traditional", "A test that has never failed might be asserting nothing at all",
            "It makes the test faster", "To measure coverage"],
           1,
           "Plenty of green tests are green because of a typo'd assertion or a fixture that was never loaded. Seeing red first is the only cheap proof the test is wired up."),
    ],
    exercises=[
        _ch("be7-tests", "Build the test runner", "Easy",
            "Write `assertEqual` and `test`. `assertEqual` compares deeply (JSON) and throws `expected <b>, got <a>` on a mismatch. `test(name, fn)` runs the function, printing `PASS <name>` or `FAIL <name>: <message>`, and counts each into `passed` / `failed`.",
            _suite_prog("""
let passed = 0;
let failed = 0;

function assertEqual(actual, expected) {
  const a = JSON.stringify(actual);
  const b = JSON.stringify(expected);
  if (a !== b) throw new Error(`expected ${b}, got ${a}`);
}

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`PASS ${name}`);
  } catch (err) {
    failed++;
    console.log(`FAIL ${name}: ${err.message}`);
  }
}
"""),
            """function assertEqual(actual, expected) {
  const a = JSON.stringify(actual);
  const b = JSON.stringify(expected);
  if (a !== b) throw new Error(`expected ${b}, got ${a}`);
}

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`PASS ${name}`);
  } catch (err) {
    failed++;
    console.log(`FAIL ${name}: ${err.message}`);
  }
}""",
            [("adds numbers | 4 | 4\noff by one | 4 | 5\ndeep equal | {\"a\":[1,2]} | {\"a\":[1,2]}",
              "PASS adds numbers\nFAIL off by one: expected 5, got 4\nPASS deep equal\n2 passed, 1 failed"),
             ("all good | [1,2] | [1,2]\nwrong shape | {\"a\":1} | {\"a\":2}\nnested | {\"x\":{\"y\":[3]}} | {\"x\":{\"y\":[3]}}\nnull vs zero | null | 0",
              'PASS all good\nFAIL wrong shape: expected {"a":2}, got {"a":1}\nPASS nested\n'
              'FAIL null vs zero: expected 0, got null\n2 passed, 2 failed')],
            hints=["A failing assertion is just a thrown Error; a test is a try/catch around calling the function.",
                   "Compare `JSON.stringify` of both sides — that gives deep equality without writing a recursive walk.",
                   "The failure line is `FAIL <name>: <err.message>`, and the message is the one assertEqual threw."]),
    ],
    quiz=[
        _q("What is a test runner, mechanically?",
           ["A separate process per test", "A try/catch around a function, plus counters",
            "A JSON schema validator", "A code coverage tool"],
           1,
           "Failing assertions throw; the runner catches, counts and reports. Everything else a framework offers is convenience on top."),
        _q("Why listen on port 0 in integration tests?",
           ["It is faster", "The OS picks any free port, so tests never collide with each other or your dev server",
            "Port 0 disables networking", "It is required for fetch"],
           1,
           "Then `server.address().port` tells you which one you got — the same trick every drill in this track uses."),
    ],
)

_P7_FINAL = _ch(
    "be7-final", "The assembled service", "Hard",
    "Wire the pieces together. Dispatch through the given route table with `matchRoute`: if a path matches but no method does, 405 `method_not_allowed`; if nothing matches, 404 `not_found`. Parse a JSON body into the context (unparseable → 400 `invalid_json`). Call the matched route with `{params, body}`; it returns `[status, data]`. Wrap everything in one catch: an `HttpError` becomes its own status and code, anything else is logged and becomes 500 `{\"error\":\"server_error\"}`.",
    _server("""
function send(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(data === null ? "" : JSON.stringify(data));
}

function readBody(req) {
  return new Promise((ok) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => ok(raw));
  });
}

class HttpError extends Error {
  constructor(status, code) {
    super(code);
    this.status = status;
    this.code = code;
  }
}

function matchRoute(pattern, path) {
  const p = pattern.split("/");
  const s = path.split("/");
  if (p.length !== s.length) return null;
  const params = {};
  for (let i = 0; i < p.length; i++) {
    if (p[i].startsWith(":")) params[p[i].slice(1)] = s[i];
    else if (p[i] !== s[i]) return null;
  }
  return params;
}

// ---- the service (given) ---------------------------------------------------
const notes = new Map();
let nextId = 1;

function mustFind(rawId) {
  const note = notes.get(Number(rawId));
  if (!note) throw new HttpError(404, "not_found");
  return note;
}

const routes = [
  { method: "GET", path: "/notes", fn: () => [200, [...notes.values()]] },
  {
    method: "POST",
    path: "/notes",
    fn: ({ body }) => {
      if (typeof body.title !== "string" || body.title.trim() === "") {
        throw new HttpError(400, "validation_failed");
      }
      const note = { id: nextId++, title: body.title.trim(), done: false };
      notes.set(note.id, note);
      return [201, note];
    },
  },
  { method: "GET", path: "/notes/:id", fn: ({ params }) => [200, mustFind(params.id)] },
  {
    method: "DELETE",
    path: "/notes/:id",
    fn: ({ params }) => {
      notes.delete(mustFind(params.id).id);
      return [204, null];
    },
  },
  { method: "GET", path: "/boom", fn: () => { throw new Error("db://user:hunter2@host refused"); } },
];

async function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  try {
    let pathMatched = false;
    for (const route of routes) {
      const params = matchRoute(route.path, url.pathname);
      if (params === null) continue;
      pathMatched = true;
      if (route.method !== req.method) continue;

      let body = {};
      const raw = await readBody(req);
      if (raw) {
        try {
          body = JSON.parse(raw);
        } catch {
          throw new HttpError(400, "invalid_json");
        }
      }
      const [status, data] = await route.fn({ params, body });
      return send(res, status, data);
    }
    if (pathMatched) throw new HttpError(405, "method_not_allowed");
    throw new HttpError(404, "not_found");
  } catch (err) {
    if (err instanceof HttpError) return send(res, err.status, { error: err.code });
    console.error(err);
    send(res, 500, { error: "server_error" });
  }
}
"""),
    """async function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  try {
    let pathMatched = false;
    for (const route of routes) {
      const params = matchRoute(route.path, url.pathname);
      if (params === null) continue;
      pathMatched = true;
      if (route.method !== req.method) continue;

      let body = {};
      const raw = await readBody(req);
      if (raw) {
        try {
          body = JSON.parse(raw);
        } catch {
          throw new HttpError(400, "invalid_json");
        }
      }
      const [status, data] = await route.fn({ params, body });
      return send(res, status, data);
    }
    if (pathMatched) throw new HttpError(405, "method_not_allowed");
    throw new HttpError(404, "not_found");
  } catch (err) {
    if (err instanceof HttpError) return send(res, err.status, { error: err.code });
    console.error(err);
    send(res, 500, { error: "server_error" });
  }
}""",
    [('POST /notes {"title":"  Buy milk  "}\nGET /notes/1\nGET /notes',
      '201 {"id":1,"title":"Buy milk","done":false}\n'
      '200 {"id":1,"title":"Buy milk","done":false}\n'
      '200 [{"id":1,"title":"Buy milk","done":false}]'),
     ('GET /notes/9\nPUT /notes/1\nGET /nope\nPOST /notes/1',
      '404 {"error":"not_found"}\n405 {"error":"method_not_allowed"}\n'
      '404 {"error":"not_found"}\n405 {"error":"method_not_allowed"}'),
     ('POST /notes {}\nPOST /notes {oops}\nGET /boom',
      '400 {"error":"validation_failed"}\n400 {"error":"invalid_json"}\n'
      '500 {"error":"server_error"}'),
     ('POST /notes {"title":"A"}\nDELETE /notes/1\nGET /notes/1\nDELETE /notes/1',
      '201 {"id":1,"title":"A","done":false}\n204\n'
      '404 {"error":"not_found"}\n404 {"error":"not_found"}')],
    hints=["Loop the route table with `matchRoute`; remember that a match returns an object (possibly empty) and a miss returns null.",
           "Track whether any route's PATH matched even when the method did not — that flag is what separates 405 from 404.",
           "One try/catch wraps the whole thing: HttpError keeps its status and code; anything else is logged and answered with an opaque 500."])

_P7 = _project(
    "layered", 7,
    "Refactor to Layers & Write Tests",
    "Turn six projects of accumulated code into something you could hand over.",
    "Advanced",
    "Extract a router, a middleware chain and one error boundary, then write the test runner and the tests that keep it all honest.",
    "The code works; that was never the hard part. What makes a service maintainable is that the next person can add a route without reading everything, and change something without breaking what they cannot see.",
    150,
    ["first-server", "notes-crud", "validation", "persistence", "query-api", "auth"],
    ["routing tables", "path parameters", "middleware", "error boundaries", "layering", "testing"],
    ["Write a route matcher with path parameters and dispatch through a table",
     "Run cross-cutting work in a middleware chain instead of in every handler",
     "Throw typed errors and translate them in exactly one place",
     "Keep internal detail out of responses while keeping it in your logs",
     "Write a test runner and both unit and integration tests"],
    """
Six projects in, `server.js` is long, and each new endpoint means another branch
in the same staircase. Nothing about it is wrong; it has simply outgrown its
shape. This project gives it a new one.

You will extract three things — a **router** (a table plus a matcher), a
**middleware chain** (the work every request needs) and an **error boundary**
(one place where any failure becomes a response) — and then write a **test
runner** and the tests that stop this refactor from quietly breaking project 2.

By the end you will have written a very small framework. That is deliberate: the
next time you open Express, Fastify or Hono, you will recognise every piece,
including the ones they do differently.
""",
    [_ep("—", "route table", "Declarative routes with :params", "", "matchRoute → {id:\"17\"} | null", "—"),
     _ep("—", "middleware", "Body, auth, timing — once, in order", "", "returns true to stop the chain", "—"),
     _ep("—", "error boundary", "HttpError → status; anything else → 500", "", '{"error":"code"}', "4xx · 500"),
     _ep("GET", "/notes/:id", "Dispatched through the table", "", '{"id":1,…}', "200 · 404"),
     _ep("PUT", "/notes/:id", "Path matches, method does not", "", '{"error":"method_not_allowed"}', "405")],
    """
Same folder. This is the layout you are refactoring towards:

```
notes-api/
  server.js       boot: create the server, listen
  router.js       matchRoute + the route table
  middleware.js   the chain
  errors.js       HttpError + the boundary
  notes.js        the route handlers for one resource
  store.js        data
  auth.js         hashing, users, tokens
  test.js         the runner and the tests
```

```
node server.js     # the service
node test.js       # the tests
```

Refactor in small steps, and keep the API working after each one. `node test.js`
passing is what tells you that — which is a good reason to write step 4's tests
early rather than last.
""",
    [_P7_S1, _P7_S2, _P7_S3, _P7_S4],
    final_build=_P7_FINAL,
    acceptance=[
        "Routes are declared in a table, not as a staircase of `if` statements.",
        "`matchRoute(\"/notes/:id\", \"/notes/17\")` returns `{id: \"17\"}`; `matchRoute(\"/notes/:id\", \"/notes\")` returns null.",
        "A path that matches with a different verb returns 405, not 404.",
        "Body parsing, authentication and logging each appear exactly once, in the chain.",
        "A middleware that responds stops the chain, and the route function never runs.",
        "`mustFind` throws `HttpError(404)` from the store layer, with no `res` in sight.",
        "One catch translates HttpError to its status and everything else to an opaque 500.",
        "No response body ever contains an exception message or a stack trace, and every unexpected error is logged.",
        "`node test.js` prints PASS/FAIL lines and a summary.",
        "There are unit tests for the pure functions AND integration tests against a real server on port 0.",
        "Every endpoint from projects 2, 3, 5 and 6 still behaves as it did.",
    ],
    manual_test="""
```
node server.js
node test.js       # in another terminal

# routing
curl -i http://localhost:3000/notes/1
curl -i -X PUT http://localhost:3000/notes/1     # 405 — path matches, verb does not
curl -i http://localhost:3000/nope               # 404

# the error boundary — the body must be opaque, your terminal must not be
curl -i http://localhost:3000/boom               # {"error":"server_error"}

# the middleware chain still guards everything
curl -i http://localhost:3000/notes              # 401 without a token
```

Then the refactor's real test: break something on purpose. Delete a line from
`matchRoute` and run `node test.js`. If nothing goes red, your tests are not
testing what you think they are.
""",
    reference="""
// ------------------------------------------------------------------ errors.js --
export class HttpError extends Error {
  constructor(status, code) {
    super(code);
    this.status = status;
    this.code = code;
  }
}

/** The ONE place a failure becomes a response. Opaque outward, verbose inward. */
export function handleError(res, err, send) {
  if (err instanceof HttpError) return send(res, err.status, { error: err.code });
  console.error(err);                            // full detail → your logs
  if (!res.headersSent) send(res, 500, { error: "server_error" });
}

// ------------------------------------------------------------------ router.js --
/** Captured params, or null. `{}` is a MATCH — compare against null, not falsy. */
export function matchRoute(pattern, path) {
  const p = pattern.split("/");
  const s = path.split("/");
  if (p.length !== s.length) return null;

  const params = {};
  for (let i = 0; i < p.length; i++) {
    if (p[i].startsWith(":")) params[p[i].slice(1)] = s[i];
    else if (p[i] !== s[i]) return null;
  }
  return params;
}

// -------------------------------------------------------------- middleware.js --
// Each returns true if it has already answered. Order IS the design.
export const middleware = [
  (req, res, ctx) => { ctx.startedAt = Date.now(); },

  async (req, res, ctx) => {
    const raw = await readBody(req);
    if (!raw) return;
    try {
      ctx.body = JSON.parse(raw);
    } catch {
      send(res, 400, { error: "invalid_json" });
      return true;
    }
  },

  (req, res, ctx) => {
    if (PUBLIC.has(ctx.path)) return;            // /register, /login
    const user = auth.authenticate(req);
    if (!user) {
      send(res, 401, { error: "unauthorized" });
      return true;
    }
    ctx.user = user;
  },
];

// ------------------------------------------------------------------ server.js --
const routes = [
  { method: "GET",    path: "/notes",     fn: notes.list },
  { method: "POST",   path: "/notes",     fn: notes.create },
  { method: "GET",    path: "/notes/:id", fn: notes.get },
  { method: "PATCH",  path: "/notes/:id", fn: notes.patch },
  { method: "DELETE", path: "/notes/:id", fn: notes.remove },
];

async function handler(req, res) {
  const url = new URL(req.url, "http://localhost");
  const ctx = { params: {}, body: {}, user: null, path: url.pathname, query: url.searchParams };

  try {
    for (const mw of middleware) {
      if (await mw(req, res, ctx)) return;       // it answered; stop
    }

    let pathMatched = false;
    for (const route of routes) {
      const params = matchRoute(route.path, url.pathname);
      if (params === null) continue;
      pathMatched = true;                        // the path is real…
      if (route.method !== req.method) continue; // …just not with this verb
      ctx.params = params;
      const [status, data] = await route.fn(ctx);
      return send(res, status, data);
    }
    throw new HttpError(pathMatched ? 405 : 404,
                        pathMatched ? "method_not_allowed" : "not_found");
  } catch (err) {
    handleError(res, err, send);
  }
}

// --------------------------------------------------------------------- test.js --
let passed = 0;
let failed = 0;

function assertEqual(actual, expected) {
  const a = JSON.stringify(actual);
  const b = JSON.stringify(expected);
  if (a !== b) throw new Error(`expected ${b}, got ${a}`);
}

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`PASS ${name}`);
  } catch (err) {
    failed++;
    console.log(`FAIL ${name}: ${err.message}`);
  }
}

// unit — pure, instant, no server
test("matches a param", () => assertEqual(matchRoute("/notes/:id", "/notes/17"), { id: "17" }));
test("rejects a length mismatch", () => assertEqual(matchRoute("/notes/:id", "/notes"), null));
test("a bare match is an empty object", () => assertEqual(matchRoute("/notes", "/notes"), {}));

// integration — a real server on a real (arbitrary) port
const server = http.createServer(handler);
await new Promise((ok) => server.listen(0, ok));
const base = `http://127.0.0.1:${server.address().port}`;

const created = await fetch(`${base}/notes`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "Buy milk" }),
});
test("create returns 201", () => assertEqual(created.status, 201));

console.log(`${passed} passed, ${failed} failed`);
server.close();
process.exit(failed > 0 ? 1 : 0);      // non-zero exit is what CI reads
""",
    stretch=[
        "Add a `Router` class with `.get(path, fn)` and `.post(path, fn)` so routes are registered rather than listed. You have now rewritten Express's public API.",
        "Give each request an id, put it in `ctx`, log it, and return it in the `X-Request-Id` header. Tracing a report back to one log line is worth a great deal.",
        "Add a real logging middleware: method, path, status, milliseconds — one line per request, written after the response is sent.",
        "Add graceful shutdown: on SIGINT, stop accepting connections, finish in-flight requests, then exit. Deployments do this constantly, and getting it wrong drops requests.",
        "Make `node test.js` exit non-zero on failure and wire it into a git pre-commit hook. Tests nobody runs are decoration.",
    ],
    glossary=[
        _gloss("router", "A table mapping method + path pattern to a handler, plus the matcher that resolves a request against it."),
        _gloss("path parameter", "A capturing segment like `:id`. Always captured as a string."),
        _gloss("middleware", "A function that runs before the handler and may answer instead of it. A chain of them is a pipeline."),
        _gloss("context", "A per-request object carrying what middleware discovered: params, body, user."),
        _gloss("error boundary", "The single place every failure becomes a response, so error shape is defined once."),
        _gloss("information disclosure", "Leaking internal detail — stack traces, paths, credentials — in a response. A real vulnerability class."),
        _gloss("unit vs integration test", "Unit: one pure function, no server. Integration: a real server on a real port, real requests."),
    ],
    cheatsheet="""
```js
// router — {} is a MATCH, null is a miss
function matchRoute(pattern, path) {
  const p = pattern.split("/"), s = path.split("/");
  if (p.length !== s.length) return null;
  const params = {};
  for (let i = 0; i < p.length; i++) {
    if (p[i].startsWith(":")) params[p[i].slice(1)] = s[i];
    else if (p[i] !== s[i]) return null;
  }
  return params;
}

// dispatch — the flag is what keeps 405 alive
let pathMatched = false;
for (const r of routes) {
  const params = matchRoute(r.path, url.pathname);
  if (params === null) continue;
  pathMatched = true;
  if (r.method !== req.method) continue;
  return send(res, ...(await r.fn({ ...ctx, params })));
}
throw new HttpError(pathMatched ? 405 : 404, pathMatched ? "method_not_allowed" : "not_found");

// one boundary — opaque outward, verbose inward
catch (err) {
  if (err instanceof HttpError) return send(res, err.status, { error: err.code });
  console.error(err);
  send(res, 500, { error: "server_error" });
}

// a test runner, in full
function test(name, fn) {
  try { fn(); passed++; console.log(`PASS ${name}`); }
  catch (e) { failed++; console.log(`FAIL ${name}: ${e.message}`); }
}
```
""",
    self_check=[
        "I can explain why `matchRoute` must return null rather than a falsy object.",
        "I can say what the `pathMatched` flag is for in one sentence.",
        "I know what a middleware must do after it sends a response, and what happens if it forgets.",
        "I can name what a leaked exception message can tell a stranger.",
        "I have watched a test of mine fail for the right reason before making it pass.",
    ],
    review=[
        _q("`matchRoute` returns `{}` for `/notes`. Why prefer `params === null` over `!params`?",
           ["`!params` is broken for `{}`",
            "Both work today — but `=== null` states the contract instead of depending on which return values happen to be falsy",
            "`null` is truthy", "It is faster"],
           1,
           "`{}` is truthy, so `!params` does behave correctly right now. The explicit comparison is what keeps it correct if the matcher ever returns another falsy miss value."),
        _q("What is the failure mode of a middleware that responds but returns nothing?",
           ["The response is lost", "The chain continues and something replies a second time, throwing",
            "Node retries", "It becomes a 500"],
           1,
           "Sending does not stop your loop. The stop signal is what ends the chain."),
        _q("Which error should reach the client verbatim?",
           ["All of them", "None — clients get a stable code; the detail goes to your logs",
            "Only 500s", "Only validation errors"],
           1,
           "The `error` code is part of your API and is meant to be read. Exception text is for you, and can leak paths, versions and credentials."),
        _q("Why write the tests before the refactor rather than after?",
           ["They are easier to write first", "They are what tells you the refactor did not change behaviour",
            "So they run faster", "Coverage tools need it"],
           1,
           "A refactor is by definition a change that should not alter behaviour. Without tests you have no way to make that claim."),
    ],
    milestone="You have written your own miniature framework — and you understand every line of the real one you use next.",
)

_PROJECTS.append(_P7)


# ===========================================================================
# SCOPE LINT — enforce "never require an idea from a later project".
# ===========================================================================
def _all_programs(project):
    out = []
    for s in project["steps"]:
        for ex in s["exercises"]:
            out.append((ex["id"], ex["solution"]))
            out.append((ex["id"] + ":starter", ex["starter"]))
    if project.get("final_build"):
        out.append((project["final_build"]["id"], project["final_build"]["solution"]))
    if project.get("reference"):
        out.append((project["key"] + ":reference", project["reference"]))
    return out


# (token, first project number it may appear in). A program in an EARLIER
# project must not contain the token.
_SCOPE_RULES = [
    ("readBody", 2),                   # request bodies
    ("JSON.parse", 2),
    ("readFileSync(\"", 4),            # persistence (the replayer's stdin read is stripped)
    ("writeFileSync", 4),
    ("searchParams.get(\"limit\")", 5),
    ("scryptSync", 6),                 # hashing / auth
    ("bearer", 6),
    ("matchRoute", 7),                 # the extracted router
]


def _authored_region(prog):
    """The part of a program the learner is responsible for: everything except
    the import block at the top and the given replayer at the bottom."""
    body = prog.split("// ---- request replayer")[0]
    return "\n".join(l for l in body.split("\n") if not l.startswith("import "))


def _lint_scope(projects):
    problems = []
    for p in projects:
        if not p.get("authored"):
            continue
        n = p["number"]
        for pid, prog in _all_programs(p):
            body = _authored_region(prog)
            for token, allowed_from in _SCOPE_RULES:
                if n < allowed_from and token in body:
                    problems.append(
                        f"Project {n} program {pid} uses {token!r} "
                        f"(not introduced until project {allowed_from})"
                    )
    if problems:
        raise AssertionError("Backend Lab scope violations:\n  " + "\n  ".join(problems))


def _lint_numbering(projects):
    seen = set()
    for i, p in enumerate(projects, start=1):
        assert p["number"] == i, f"project {p['key']} is out of order (number {p['number']}, position {i})"
        assert p["key"] not in seen, f"duplicate project key: {p['key']}"
        seen.add(p["key"])
        for dep in p["builds_on"]:
            assert dep in seen, f"{p['key']} builds_on unknown/later project {dep!r}"
        if p["authored"]:
            assert p["steps"], f"authored project {p['key']} has no steps"
            step_keys = set()
            for s in p["steps"]:
                assert s["key"] not in step_keys, f"{p['key']}: duplicate step key {s['key']}"
                step_keys.add(s["key"])
                assert s["instructions"], f"{p['key']}/{s['key']}: no instructions"
                assert s["checkpoint"], f"{p['key']}/{s['key']}: no checkpoint"


_lint_scope(_PROJECTS)
_lint_numbering(_PROJECTS)


BACKEND_TRACK = {
    "key": "backend",
    "title": "Backend Lab: CRUD From Scratch",
    "subtitle": (
        "Seven projects that build a real CRUD API one layer at a time — routing, "
        "resources, validation, persistence, querying, authentication and structure "
        "— in plain Node with zero dependencies. Every project tells you what to "
        "build, in what order, and how to know it worked."
    ),
    "intro": _bp("""
### How to use this track

Each project is **a server you finish and run**, not a chapter you read. They
are meant to be done in order: project 2 opens project 1's file and grows it,
project 3 grows that, and so on. By project 7 you are refactoring a service you
wrote yourself, which is the only way that lesson lands.

Inside a project, each step has three parts:

- **Instructions** — what to do, in order, with the code to write.
- **Checkpoint** — the observable result that proves the step is done. If you
  cannot see it, do not move on.
- **Drills** — short judged exercises on the idea the step just introduced.

Then a **final build** puts the whole project together, and an **acceptance
checklist** plus **manual tests** let you confirm your own copy works.

### Ground rules

1. **No dependencies.** Node built-ins only. No Express, no npm install. Every
   framework you will meet later is a wrapper over what you are about to write,
   and wrappers are much easier to use once you know what is underneath.
2. **Type the code, do not paste it.** The typos are the lesson.
3. **Run your own server.** The judged drills check your understanding; only
   your own `node server.js` and a `curl` prove you built the thing.
"""),
    "harness_note": _bp("""
Every judged exercise here boots a **real HTTP server** and replays a script of
requests against it, so you are debugging an actual server rather than a
simulation.

- **stdin** holds one request per line: `METHOD /path [@token] [json body]`
- **stdout** prints one line per request: `<status> <response body>`

So the input

```
POST /notes {"title":"Buy milk"}
GET /notes/1
GET /notes/99
```

produces

```
201 {"id":1,"title":"Buy milk","done":false}
200 {"id":1,"title":"Buy milk","done":false}
404 {"error":"not_found"}
```

The replayer at the bottom of each program is **given** — you never edit it.
Your job is always the code above it. Two consequences worth knowing:

- **Key order matters.** `JSON.stringify` emits keys in insertion order, so
  build response objects in the order the expected output shows.
- **Ids are counters, not UUIDs.** Real services use `crypto.randomUUID()`;
  these use `1, 2, 3` so the expected output can be written down at all. The
  lessons say so wherever it matters.
"""),
    "projects": _PROJECTS,
}


# Only when run directly. gen_seed.py exec()s this file inside its own
# namespace, where __name__ is already "__main__" — so also check that __file__
# is really this script, or the seed would be written twice per generation.
if __name__ == "__main__" and os.path.basename(__file__) == "backend_course.py":
    out = os.path.join(os.path.dirname(__file__), "..", "src-tauri", "seeds",
                       "backend_course.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(BACKEND_TRACK, f, indent=2, ensure_ascii=False)
    n_ex = sum(len(e["exercises"]) for p in BACKEND_TRACK["projects"] for e in p["steps"])
    n_ex += sum(1 for p in BACKEND_TRACK["projects"] if p.get("final_build"))
    print(f"Wrote {len(BACKEND_TRACK['projects'])} backend projects "
          f"({n_ex} judged exercises) to {os.path.relpath(out)}")
