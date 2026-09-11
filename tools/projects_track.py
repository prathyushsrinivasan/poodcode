# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Projects — build one real application in TypeScript, broken all the way down.
#
# exec()'d inside gen_seed.py's namespace; defines a single global
# `PROJECT_TRACK` (dict) which gen_seed writes to
# src-tauri/seeds/projects.json (served by the `projects_track` command). Also
# runnable on its own (`python tools/projects_track.py`) so the verifier can
# check every program without a full seed regeneration.
#
# WHY A THIRD TRACK, next to the Backend Lab it superficially resembles:
#
#   The Backend Lab's unit is a PROJECT — a whole server you finish in an
#   evening, in JavaScript. That is the right size for someone who already
#   writes code and wants the shape of a backend.
#
#   This track's unit is a MODULE: one 30-60 minute slice that adds exactly one
#   capability to an application you keep building, in TypeScript. Small enough
#   that the full development process fits inside it — why this module exists,
#   where it sits on the roadmap, every piece of syntax it needs taught before
#   it is used, ordered steps with a checkpoint each, exercises you write
#   yourself, and a revealable reference. That is what "broken down as much as
#   possible" buys: at no point are you asked to write a line whose syntax the
#   track has not already put in front of you.
#
# HARD DESIGN RULES
#   1. ZERO DEPENDENCIES. Node built-ins only (`node:http`, `node:fs`). No
#      Express, no npm install — the app is offline-first and the judge runs a
#      single file in a scratch directory with no node_modules.
#   2. NOTHING BEFORE ITS MODULE. Each project has a scope table mapping a
#      token to the module that introduces it; `_lint_scope` FAILS generation
#      if an earlier module's program uses it.
#   3. EVERY TOKEN IS TAUGHT. `_lint_syntax_taught` FAILS generation unless the
#      module that introduces a token also declares it in that module's
#      `syntax` primer. This is rule 2's other half and the reason the track can
#      claim to be self-contained: a scope rule without a syntax entry means the
#      track uses something it never explained.
#   4. ERASABLE SYNTAX ONLY. The judge runs TypeScript by STRIPPING types, not
#      compiling them, so `enum`, `namespace` and parameter properties cannot
#      run. None of them are needed here; every scope table bans them outright.
#   5. EVERY PROGRAM IS DETERMINISTIC. Ids come from counters, not UUIDs;
#      nothing prints a timestamp. Each module says plainly where the real world
#      would use randomness instead.
#
# EXECUTION MODEL: exercises run through the same stdin/stdout judge as every
# other track, at the `strict+indexed` preset (`noUncheckedIndexedAccess`) —
# which is not a formality here: `path.split("/")[2]` really can be missing, and
# a todo API that pretends otherwise is the bug this track is trying to prevent.
# Server programs boot a REAL server on port 0 and replay a request script read
# from stdin — see `_DRIVER`. Pure-logic programs just print.
#
# EXERCISE KINDS: "drill" (fill one ____ blank), "challenge" (write a whole
# region where you see ____), "fix" (a complete but buggy program to correct —
# no blank; starter=buggy, solution=fixed).
# ---------------------------------------------------------------------------

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _pbp(src):
    """Normalize a triple-quoted program or Markdown block: drop the leading
    newline, guarantee exactly one trailing newline."""
    return src.lstrip("\n").rstrip() + "\n"


def _pq(question, options, answer, explanation):
    return {"question": question, "options": options, "answer": answer,
            "explanation": explanation}


def _pgloss(term, definition):
    return {"term": term, "def": definition}


def _pep(method, path, purpose, request, response, status):
    return {"method": method, "path": path, "purpose": purpose,
            "request": request, "response": response, "status": status}


def _syn(form, means, example="", note="", recap=False):
    """One entry in a module's syntax primer.

    `form` is the syntax itself and is what `_lint_syntax_taught` matches scope
    tokens against, so write it the way the code writes it.
    """
    return {"form": form, "means": means, "example": _pbp(example) if example else "",
            "note": note, "recap": bool(recap)}


def _phase(key, title, outcome, summary):
    return {"key": key, "title": title, "outcome": outcome, "summary": summary}


# ---------------------------------------------------------------------------
# Program shapes.
#
# Two of them. `_plain` is pure logic printed to stdout — the first modules,
# before there is a server at all. `_server` boots a real one and replays a
# request script, and is identical in every module that uses it, so it becomes
# invisible after the first read: the only thing that changes is the code above.
#
# The replayer is GIVEN, never blanked. It is also deliberately written in the
# same TypeScript the learner is being taught — `addr === null ? 0 : addr.port`
# rather than a `!`, because `server.address()` really can be null and the
# track's whole argument is that you handle that rather than assert it away.
# ---------------------------------------------------------------------------

_DRIVER = """
// ---- request replayer (given — don't edit) --------------------------------
// stdin:  one request per line —  METHOD /path [json body]
// stdout: one line per request —  <status> <response body>
// An error your handler throws becomes a 500 — exactly what a framework does.
const server = createServer((req, res) => {
  Promise.resolve(handler(req, res)).catch((err: unknown) => {
    console.error(err);
    if (res.headersSent) { res.end(); return; }
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end('{"error":"server_error"}');
  });
});
await new Promise<void>((ok) => server.listen(0, "127.0.0.1", () => ok()));
const addr = server.address();
const base = `http://127.0.0.1:${addr === null ? 0 : addr.port}`;
for (const line of readFileSync(0, "utf8").split("\\n")) {
  const text = line.trim();
  if (!text) continue;
  const parts = text.split(" ");
  const method = parts[0] ?? "GET";
  const path = parts[1] ?? "/";
  const body = parts.slice(2).join(" ");
  const headers: Record<string, string> = {};
  if (body) headers["Content-Type"] = "application/json";
  const reply = await fetch(base + path, { method, headers, body: body || undefined });
  console.log(reply.status, (await reply.text()).trim());
}
server.close();
"""

_HTTP_IMPORTS = (
    'import { createServer, type IncomingMessage, type ServerResponse } from "node:http";\n'
    'import { readFileSync } from "node:fs";\n'
)


def _server(code, imports=_HTTP_IMPORTS):
    """A complete judged program: imports, the learner's code, the replayer."""
    return imports + "\n" + _pbp(code) + "\n" + _pbp(_DRIVER)


def _plain(code):
    """A judged program with no server — pure logic printed to stdout."""
    return _pbp(code)


def _stdin(code):
    """A judged program that reads stdin but boots no server."""
    return 'import { readFileSync } from "node:fs";\n\n' + _pbp(code)


def _ptests(pairs):
    return [{"input": i, "output": o} for (i, o) in pairs]


# ---------------------------------------------------------------------------
# Exercises.
# ---------------------------------------------------------------------------

_PIDS = set()


def _pmk(eid, title, prompt, full, tests, hints, difficulty, kind,
         starter=None, blank=None):
    """Build an Exercise dict. Either `blank` (a unique substring of `full`
    replaced by ____ to form the starter) OR an explicit `starter` (for "fix")."""
    assert eid not in _PIDS, f"duplicate project exercise id: {eid}"
    _PIDS.add(eid)
    if starter is None:
        assert blank is not None, f"{eid}: need blank or starter"
        assert full.count(blank) == 1, (
            f"{eid}: blank must appear exactly once in the solution "
            f"(found {full.count(blank)}): {blank[:60]!r}"
        )
        starter = full.replace(blank, "____", 1)
    assert starter != full, f"{eid}: starter equals solution"
    assert tests, f"{eid}: needs at least one test"
    hints = list(hints or [])
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "",
        "hints": hints,
        "language": "typescript",
        "kind": kind, "difficulty": difficulty,
        # The whole track is checked under noUncheckedIndexedAccess. See the
        # header: an absent path segment is a real case here, not a formality.
        "strictness": "strict+indexed",
        "harness": "", "judge_mode": "", "forbid": [],
        "starter": starter, "solution": full, "tests": _ptests(tests),
        "source_slug": "", "dataset": "",
    }


def _pex(eid, title, prompt, full, blank, tests, hints=(), difficulty="Intro"):
    return _pmk(eid, title, prompt, full, tests, hints, difficulty, "drill", blank=blank)


def _pch(eid, title, difficulty, prompt, full, blank, tests, hints=()):
    return _pmk(eid, title, prompt, full, tests, hints, difficulty, "challenge", blank=blank)


def _pfix(eid, title, prompt, buggy, fixed, tests, hints=(), difficulty="Easy"):
    return _pmk(eid, title, prompt, fixed, tests, hints, difficulty, "fix", starter=buggy)


def _pstep(key, title, what, instructions, checkpoint, pitfalls=(), warmup=(),
           exercises=(), quiz=()):
    return {
        "key": key, "title": title, "what": what,
        "instructions": _pbp(instructions) if instructions else "",
        "checkpoint": _pbp(checkpoint) if checkpoint else "",
        "pitfalls": list(pitfalls), "warmup": list(warmup),
        "exercises": list(exercises), "quiz": list(quiz),
    }


def _pmod(key, number, phase, title, what, goal, why, est_minutes, builds_on,
          concepts, objectives, deliverable, brief, syntax, steps,
          endpoints=(), final_build=None, acceptance=(), manual_test="",
          reference="", stretch=(), glossary=(), cheatsheet="", self_check=(),
          review=(), milestone="", authored=True):
    return {
        "key": key, "number": number, "phase": phase, "title": title,
        "what": what, "goal": goal, "why": why, "authored": authored,
        "est_minutes": est_minutes, "builds_on": list(builds_on),
        "concepts": list(concepts), "objectives": list(objectives),
        "deliverable": deliverable,
        "brief": _pbp(brief) if brief else "",
        "syntax": list(syntax),
        "endpoints": list(endpoints),
        "steps": list(steps), "final_build": final_build,
        "acceptance": list(acceptance),
        "manual_test": _pbp(manual_test) if manual_test else "",
        "reference": _pbp(reference) if reference else "",
        "stretch": list(stretch), "glossary": list(glossary),
        "cheatsheet": _pbp(cheatsheet) if cheatsheet else "",
        "self_check": list(self_check), "review": list(review),
        "milestone": milestone,
    }


def _pskel(key, number, phase, title, what, goal, deliverable=""):
    """A planned module, shown as 'coming soon' until it is authored."""
    return _pmod(key, number, phase, title, what, goal, "", 0, [], [], [],
                 deliverable, "", [], [], authored=False)


# ---------------------------------------------------------------------------
# Scope: the module that first introduces each token.
#
# ONE TABLE PER PROJECT, because the syllabus is a property of the project, not
# of the track: the Todo API introduces `.split(` in module 10 to pull an id out
# of a path, and Calc introduces it in module 18 to cut stdin into lines. A
# shared table would have to pick one and lie about the other.
#
# Read a table as that project's syllabus. `_lint_scope` fails generation if a
# module numbered lower than the value uses the token, and `_lint_syntax_taught`
# fails if the module at the value does not TEACH it in its syntax primer.
# Together they are the guarantee the track's pitch rests on.
#
# Tokens deliberately absent from the Todo table: `const`, `let`, `function`,
# `return`, `if`, template literals and `.push(` — module 1 uses all of them, so
# a rule would be a false claim about when the track first shows them. Module
# 1's syntax primer covers them instead.
# ---------------------------------------------------------------------------

_TODO_SCOPE_RULES = [
    # --- Phase 1: model the data -------------------------------------------
    ("type ", 1),
    ("interface ", 99),        # the track uses `type` throughout; see module 1
    ("JSON.stringify(", 1),
    (".push(", 2),
    ("for (", 2),
    (".length", 2),
    # Module 2 needs *some* way to remove an element, to demonstrate the id
    # collision `todos.length + 1` causes. `shift` is one line to explain and
    # leaves `splice` to module 12, where removing by id is the actual job.
    (".shift(", 2),
    # Arrow functions arrive with the first callback that needs one, in module 3.
    # An earlier draft gated them at 14 with the other array methods, which would
    # have forced `.find(function (t) { … })` on module 3 — teaching a workaround
    # for a rule of our own making rather than the idiom everyone actually writes.
    ("=>", 3),
    (".find(", 3),
    ("undefined", 3),
    # --- Phase 2: put it on the network ------------------------------------
    ("createServer(", 4),
    (".listen(", 4),
    ("res.end(", 4),
    ("res.writeHead(", 5),
    ("req.method", 6),
    ("req.url", 6),
    # `??` lands here rather than earlier because module 6 is the first place the
    # COMPILER forces it: `new URL(req.url, base)` is a type error, since the
    # target is `string | undefined` and the constructor takes a `string`. The
    # driver uses it four modules early, which is exactly what `_GIVEN_MARKER`
    # is for.
    ("??", 6),
    ("new URL(", 6),
    (".pathname", 6),
    # --- Phase 3: full CRUD ------------------------------------------------
    ('req.on("data"', 8),
    ("setEncoding(", 8),
    ("new Promise", 8),
    (".then(", 8),
    ("async ", 8),
    ("await ", 8),
    ("JSON.parse(", 9),
    (".split(", 10),
    ("Number(", 10),
    ("Number.isInteger(", 10),
    ("Partial<", 11),
    ("...", 11),               # object spread, taught with Partial
    # You have the object `findTodo` returned and want its position, to swap
    # the patched copy in. Module 12's `.findIndex(` is the other question: you
    # have only an id.
    (".indexOf(", 11),
    (".findIndex(", 12),
    (".splice(", 12),
    # --- Phase 4: make it trustworthy --------------------------------------
    ("unknown", 13),
    ("typeof ", 13),
    ("Array.isArray(", 13),
    # The `in` operator on a property name — `"title" in obj` — which is how an
    # `object` earns a readable property. Written with the closing quote so it
    # matches `"title" in obj` and not a `for (const k in xs)` loop.
    ('" in ', 13),
    (".map(", 14),             # collecting one error per bad field
    ("try {", 16),
    ("catch ", 16),
    ("throw ", 16),
    ("instanceof ", 16),
    # --- Phase 5: make it real ---------------------------------------------
    ("searchParams", 17),
    (".filter(", 17),
    (".sort(", 18),
    (".slice(", 18),
    ("writeFileSync(", 19),
    ("existsSync(", 19),
    # --- Never. Type-stripping cannot run these (design rule 4). -----------
    ("enum ", 999),
    ("namespace ", 999),
    ("declare ", 999),
]

# The replayer is given, not written, so its syntax must not be counted against
# the module it appears in — module 4 shows `async`/`await` in the driver long
# before module 8 teaches them. Everything from this marker to the end of the
# program is exempt.
_GIVEN_MARKER = "// ---- request replayer (given"


def _authored_region(program):
    """The part of a program the learner is responsible for."""
    cut = program.find(_GIVEN_MARKER)
    return program if cut < 0 else program[:cut]


def _all_programs(module):
    """(id, program) for every starter and solution in a module."""
    for step in module["steps"]:
        for ex in step["exercises"]:
            yield f"{ex['id']}:starter", ex["starter"]
            yield f"{ex['id']}:solution", ex["solution"]
    fb = module.get("final_build")
    if fb:
        yield f"{fb['id']}:starter", fb["starter"]
        yield f"{fb['id']}:solution", fb["solution"]


def _all_exercises(project):
    """(where, exercise) for every judged exercise in a project."""
    for m in project["modules"]:
        for step in m["steps"]:
            for ex in step["exercises"]:
                yield f"M{m['number']}/{step['key']}", ex
        if m.get("final_build"):
            yield f"M{m['number']}/final", m["final_build"]


def _lint_scope(modules, rules):
    problems = []
    for m in modules:
        if not m.get("authored"):
            continue
        n = m["number"]
        for pid, prog in _all_programs(m):
            body = _authored_region(prog)
            for token, allowed_from in rules:
                if n < allowed_from and token in body:
                    problems.append(
                        f"Module {n} program {pid} uses {token!r} "
                        f"(not introduced until module {allowed_from})"
                    )
    if problems:
        raise AssertionError("Projects scope violations:\n  " + "\n  ".join(problems))


def _lint_syntax_taught(modules, rules):
    """Design rule 3: the module that introduces a token must teach it.

    Without this, a scope table only promises that syntax appears in the right
    ORDER — not that it was ever explained. This is the half that makes the
    track self-contained, and it is why the rules tables are worth keeping honest.
    """
    by_number = {m["number"]: m for m in modules}
    problems = []
    for token, intro in rules:
        if intro > 90:            # 99/999 are bans, not introductions
            continue
        m = by_number.get(intro)
        if m is None or not m.get("authored"):
            continue
        taught = " ".join(s["form"] for s in m["syntax"])
        if token.strip() not in taught:
            problems.append(
                f"Module {intro} ({m['key']}) introduces {token!r} but its "
                f"syntax primer never shows it"
            )
    if problems:
        raise AssertionError(
            "Projects syntax not taught:\n  " + "\n  ".join(problems)
        )


def _lint_structure(project):
    phases = {p["key"] for p in project["roadmap"]}
    seen = set()
    for i, m in enumerate(project["modules"], start=1):
        assert m["number"] == i, (
            f"module {m['key']} is out of order (number {m['number']}, position {i})"
        )
        assert m["key"] not in seen, f"duplicate module key: {m['key']}"
        assert m["phase"] in phases, f"{m['key']}: unknown phase {m['phase']!r}"
        seen.add(m["key"])
        for dep in m["builds_on"]:
            assert dep in seen, f"{m['key']} builds_on unknown/later module {dep!r}"
        if not m["authored"]:
            continue
        assert m["steps"], f"authored module {m['key']} has no steps"
        assert m["deliverable"], f"authored module {m['key']} has no deliverable"
        assert m["why"], f"authored module {m['key']} has no why"
        assert m["syntax"], f"authored module {m['key']} has no syntax primer"
        step_keys = set()
        for s in m["steps"]:
            assert s["key"] not in step_keys, f"{m['key']}: duplicate step {s['key']}"
            step_keys.add(s["key"])
            assert s["instructions"], f"{m['key']}/{s['key']}: no instructions"
            assert s["checkpoint"], f"{m['key']}/{s['key']}: no checkpoint"


# ---------------------------------------------------------------------------
# Project 1 — the Todo API.
#
# The roadmap is five phases of four modules. Each phase ends with the
# application able to do something you can demonstrate over curl, which is what
# makes it a phase rather than an arbitrary grouping.
# ---------------------------------------------------------------------------

_TODO_PHASES = [
    _phase("model", "Phase 1 · Model the data",
           "A `Todo` type and an in-memory store you can add to, list and search — no server yet.",
           "Before a single byte goes over the network, decide what a todo *is*. "
           "Getting the type right first is what makes every later module short."),
    _phase("network", "Phase 2 · Put it on the network",
           "A real HTTP server that answers `GET /todos` with your list as JSON, and 404s everything else.",
           "Turn the store into a service: a server, status codes, JSON responses, "
           "and a router that knows the difference between a path it handles and one it doesn't."),
    _phase("crud", "Phase 3 · Full CRUD",
           "Create, read, update and delete a todo over HTTP — the complete resource.",
           "One module per verb, because each one has its own status code, its own "
           "failure mode and its own thing to get wrong."),
    _phase("trust", "Phase 4 · Make it trustworthy",
           "Bad input gets a specific 400 telling you which field was wrong — never a 500, never a crash.",
           "Everything so far assumed the client sends what it promised. "
           "This is where the API stops trusting it."),
    _phase("real", "Phase 5 · Make it real",
           "A queryable, paginated list that survives a restart, behind a router you'd be happy to extend.",
           "The difference between a demo and something you would deploy: "
           "query strings, persistence, and a structure that has room for the next feature."),
]

_TODO_ENDPOINTS = [
    _pep("GET", "/todos", "List todos, newest first",
         "", '{"items":[Todo],"total":n}', "200"),
    _pep("POST", "/todos", "Create a todo",
         '{"title":"Buy milk"}', "Todo", "201 · 400"),
    _pep("GET", "/todos/:id", "Fetch one todo", "", "Todo", "200 · 404"),
    _pep("PATCH", "/todos/:id", "Update title and/or done",
         '{"done":true}', "Todo", "200 · 400 · 404"),
    _pep("DELETE", "/todos/:id", "Delete a todo", "", "(empty)", "204 · 404"),
]

# Every module of the Todo API, in order. Authored modules live one per file in
# tools/todo_mNN_*.py, each appending to `_TODO_MODULES`; the rest are skeletons
# below. Order in this tuple matters — `_lint_structure` checks it positionally.
_TODO_MODULE_FILES = (
    "todo_m01_shape.py",
    "todo_m02_store.py",
    "todo_m03_lookup.py",
    "todo_m04_server.py",
    "todo_m05_json.py",
    "todo_m06_request.py",
    "todo_m07_routing.py",
    "todo_m08_body.py",
    "todo_m09_create.py",
    "todo_m10_one.py",
    "todo_m11_update.py",
    "todo_m12_delete.py",
    "todo_m13_unknown.py",
)

_TODO_MODULES = []

for _fname in _TODO_MODULE_FILES:
    _path = os.path.join(HERE, _fname)
    assert os.path.exists(_path), f"missing project module file: {_fname}"
    with open(_path, encoding="utf-8") as _f:
        exec(compile(_f.read(), _path, "exec"))

# --- Planned modules ------------------------------------------------------
# Delete a line here as its file lands in `_TODO_MODULE_FILES` above.
_TODO_MODULES += [
    _pskel("todo-validate", 14, "trust", "Validation and a field-level 400",
           "a validator that reports which field was wrong, not just that something was",
           "Reject a bad body with a useful error.",
           "A client can tell what it got wrong from the response alone."),
    _pskel("todo-errors", 15, "trust", "One error shape, everywhere",
           "a discriminated union, and a single place that turns it into a response",
           "Make every failure in the app answer in the same format.",
           "Every error response has the same shape, whatever produced it."),
    _pskel("todo-boundary", 16, "trust", "The error boundary",
           "try/catch, headersSent, and never leaking a stack trace",
           "Survive a bug in your own handler.",
           "A thrown exception is a clean 500, not a hung request."),
    _pskel("todo-filter", 17, "real", "Filtering with query strings",
           "searchParams, and a default when the parameter is absent or junk",
           "Serve ?done=true without breaking ?done=banana.",
           "The list can be asked a question."),
    _pskel("todo-page", 18, "real", "Sorting and pagination",
           "?sort, ?limit, ?offset, and the envelope that makes paging usable",
           "Return a page of results and the total count.",
           "The list stays usable with ten thousand todos in it."),
    _pskel("todo-persist", 19, "real", "Persistence on disk",
           "read the file on boot, write it on change, and validate what you load",
           "Survive a restart.",
           "Your todos are still there tomorrow."),
    _pskel("todo-structure", 20, "real", "A router, layers and a smoke test",
           "split store / service / routes, then prove it with a test you wrote",
           "Leave the code in a shape you would be happy to add a feature to.",
           "The finished Todo API — structured, tested, and yours."),
]

_lint_scope(_TODO_MODULES, _TODO_SCOPE_RULES)
_lint_syntax_taught(_TODO_MODULES, _TODO_SCOPE_RULES)

_TODO = {
    "key": "todo-api",
    "number": 1,
    "title": "Todo API",
    "tagline": "A task list with a real HTTP interface — built in TypeScript, from nothing.",
    "language": "typescript",
    "goal": "Build a complete, validated, persistent CRUD API for todos over "
            "plain `node:http`, in TypeScript, with no dependencies at all.",
    "why": "It is the smallest application that still needs every idea a real "
           "backend needs — a data model, routing, verbs, validation, error "
           "contracts, querying and storage. Nothing here is a toy except the "
           "subject matter.",
    "authored": True,
    "est_minutes": 20 * 45,
    "stack": ["TypeScript", "node:http", "node:fs", "zero dependencies"],
    "completion_note": "A module completes once you have read it through and "
                       "solved its exercises — but the real deliverable is the "
                       "server running on your own machine.",
    "brief": _pbp("""
### What you are building

A **todo list backend**. Not a UI — the API underneath one. When you are done,
this works against a server running on your own machine:

```
$ curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
{"id":1,"title":"Buy milk","done":false}

$ curl -s localhost:3000/todos
{"items":[{"id":1,"title":"Buy milk","done":false}],"total":1}

$ curl -s -X PATCH localhost:3000/todos/1 -d '{"done":true}'
{"id":1,"title":"Buy milk","done":true}

$ curl -s -X POST localhost:3000/todos -d '{"title":""}'
{"error":"validation","fields":[{"field":"title","message":"must not be empty"}]}
```

That last line is the one worth looking at twice. Anyone can return data on the
happy path; the difference between an exercise and an API is what happens when
the client sends something wrong, and half this track is about that.

### How it is broken up

**20 modules in 5 phases.** A module is one sitting — 30 to 60 minutes — and
adds exactly one capability. Every module tells you *why it exists* before it
tells you what to type, teaches every piece of syntax it needs before using it,
walks you through the build in ordered steps with a checkpoint each, gives you
judged exercises to write yourself, and ends with a reference you can reveal and
compare against.

You are never asked to write a line of TypeScript this track has not already put
in front of you. That is enforced at build time, not promised in prose.
"""),
    "endpoints": _TODO_ENDPOINTS,
    "setup": _pbp("""
You need **Node 22 or newer** — it runs `.ts` files directly by stripping the
type annotations, so there is no build step and nothing to install.

```bash
mkdir todo-api && cd todo-api
```

Everything lives in one file to begin with. Create `server.ts` and run it with:

```bash
node server.ts
```

If Node complains about the `.ts` extension, you are on an older version — check
with `node --version`.

> **A word on the type-check.** Running a `.ts` file *strips* the types; it does
> not check them. Node will happily run `const n: number = "seven"`. The
> exercises here are type-checked before they run, so they catch it — but on
> your own machine, install TypeScript (`npm i -D typescript`) and run
> `npx tsc --noEmit --strict server.ts` when something surprises you.
"""),
    "roadmap": _TODO_PHASES,
    "modules": _TODO_MODULES,
    "acceptance": [
        "`POST /todos` with a valid title returns 201 and the created todo, with an id you did not send.",
        "`GET /todos/:id` returns 200 for a todo that exists and 404 for one that does not.",
        "`PATCH /todos/:id` with `{\"done\":true}` changes only `done`, leaving the title alone.",
        "`DELETE /todos/:id` returns 204 with an empty body, and 404 the second time you call it.",
        "`POST /todos` with `{\"title\":\"\"}` returns 400 naming `title` — not 500, not 201.",
        "`GET /todos?done=true&limit=2` returns at most two todos, all completed, plus a total.",
        "Stopping the server and starting it again does not lose your todos.",
        "Every response, success or failure, is JSON with a `Content-Type` header.",
    ],
    "manual_test": _pbp("""
With `node server.ts` running in one terminal, drive it from another:

```bash
# create two
curl -s -X POST localhost:3000/todos -H 'Content-Type: application/json' -d '{"title":"Buy milk"}'
curl -s -X POST localhost:3000/todos -H 'Content-Type: application/json' -d '{"title":"Write tests"}'

# list, fetch one, update, delete
curl -s localhost:3000/todos
curl -s localhost:3000/todos/1
curl -s -X PATCH localhost:3000/todos/1 -H 'Content-Type: application/json' -d '{"done":true}'
curl -s -i -X DELETE localhost:3000/todos/2

# the failure paths — these matter more
curl -s -i -X POST localhost:3000/todos -H 'Content-Type: application/json' -d '{"title":""}'
curl -s -i localhost:3000/todos/999
curl -s -i -X POST localhost:3000/todos -H 'Content-Type: application/json' -d 'not json'
```

`-i` prints the status line. Get into the habit of using it: a body that looks
right under a status code that is wrong is the most common bug in this track.
"""),
    "stretch": [
        "Add `PUT /todos/:id` and work out from the spec how it should differ from `PATCH`.",
        "Add tags to a todo, and `GET /todos?tag=work`.",
        "Add `POST /todos/:id/complete` and argue with yourself about whether it should exist.",
        "Swap the JSON file for SQLite via `node:sqlite`, keeping the store's interface unchanged.",
        "Put a real HTML page in front of it, served from the same server.",
    ],
    "milestone": "You have written a complete backend service — model, routes, "
                 "verbs, validation, error contract, querying and storage — "
                 "with no framework between you and the request.",
}

_lint_structure(_TODO)


# ---------------------------------------------------------------------------
# Project 2 — Calc, a small expression language.
#
# Authored in its own file for the same reason the Todo modules are: this one is
# already 800 lines before a single module lands. It defines `_CALC` (and its
# own scope table), and runs its own lints before handing the project back.
#
# WHY AN INTERPRETER SECOND. The Todo API teaches the shape of a service and
# almost nothing about the type system beyond `type` and narrowing, because HTTP
# hands you strings and you hand back strings. A language processor is the
# opposite: it is three transformations over data you designed yourself, and
# every one of them is a discriminated union walked recursively. Between them
# the two projects cover the two halves of writing TypeScript for a living, and
# they share no subject matter at all.
# ---------------------------------------------------------------------------

_calc_path = os.path.join(HERE, "calc_project.py")
assert os.path.exists(_calc_path), "missing tools/calc_project.py"
with open(_calc_path, encoding="utf-8") as _calc_f:
    exec(compile(_calc_f.read(), _calc_path, "exec"))


PROJECT_TRACK = {
    "key": "projects",
    "title": "Projects",
    "subtitle": "Build real applications, in TypeScript, broken all the way down.",
    "intro": _pbp("""
The other tracks teach you TypeScript. This one asks you to **build something
with it**, and refuses to skip a step on the way.

### What makes this different

A tutorial hands you finished code and explains it. That feels productive and
teaches almost nothing, because reading code you did not write is not the skill
you are trying to acquire. Here, every module hands you the *reason* first, the
*syntax* second, and then makes you write it.

Each module answers five questions, in this order:

1. **Why does this module exist?** — the problem the last module left behind.
2. **Where does it sit?** — its place on the project roadmap, and what the app
   can do at the end of it that it could not at the start.
3. **What syntax do I need?** — every piece of TypeScript the module uses,
   taught before it is used. Never a forward reference.
4. **What do I do?** — ordered steps, each with a checkpoint that tells you
   whether it worked, and the mistakes that cost people an hour.
5. **Did I get it?** — judged exercises you write yourself, then a reference
   implementation you can reveal and compare against.

### How to work through it

Do the modules in order and **type the code** — the typos are the lesson. Keep
your own copy of the project open in one window and the module in another; the
judged exercises check your understanding, but only the thing running on your
own machine proves you built it.

Reveal the reference *after* you have something working, and read it as "here is
another way", not as the answer. Where it differs from yours, work out which of
you is right — sometimes it will be you.
"""),
    "harness_note": _pbp("""
Judged exercises in this track come in three shapes. Which one you are looking
at is obvious from the program: if there is a replayer at the bottom, it is the
third.

**Pure logic** — the opening modules of either project, before there is anything
to drive. Your program prints to stdout and is compared line for line.

**A program on stdin** — Calc, from module 2 on. The source text your language
has to process arrives on stdin; what you print is the answer. One test case per
input, so a single exercise can be checked against `1 + 2`, `7`, and the empty
string at once.

**A real server** — the Todo API, from module 4 on. Your program boots an actual
HTTP server on a free port and a *replayer* fires a script of requests at it, so
you are debugging a real server rather than a simulation.

- **stdin** holds one request per line: `METHOD /path [json body]`
- **stdout** prints one line per request: `<status> <response body>`

So the input

```
POST /todos {"title":"Buy milk"}
GET /todos/1
GET /todos/99
```

produces

```
201 {"id":1,"title":"Buy milk","done":false}
200 {"id":1,"title":"Buy milk","done":false}
404 {"error":"not_found"}
```

The replayer at the bottom of each program is **given** — you never edit it, and
the syntax rules do not count it against the module it appears in. Your job is
always the code above it.

Three things worth knowing up front:

- **Everything is type-checked before it runs**, under `strict` plus
  `noUncheckedIndexedAccess`. That second flag means `parts[2]` has type
  `string | undefined` — because a URL really might not have a third segment.
  Handling it is not ceremony; it is the bug you are being taught to avoid.
- **Key order matters.** `JSON.stringify` emits keys in insertion order, so
  build response objects in the order the expected output shows.
- **Ids are counters, not UUIDs.** Real services use `crypto.randomUUID()`;
  these use `1, 2, 3` so the expected output can be written down at all. The
  modules say so wherever it matters.
"""),
    "projects": [_TODO, _CALC],
}


# Only when run directly. gen_seed.py exec()s this file inside its own
# namespace, where __name__ is already "__main__" — so also check that __file__
# is really this script, or the seed would be written twice per generation.
if __name__ == "__main__" and os.path.basename(__file__) == "projects_track.py":
    out = os.path.join(HERE, "..", "src-tauri", "seeds", "projects.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(PROJECT_TRACK, f, indent=2, ensure_ascii=False)
    n_mod = sum(1 for p in PROJECT_TRACK["projects"] for m in p["modules"] if m["authored"])
    n_ex = sum(1 for p in PROJECT_TRACK["projects"] for _ in _all_exercises(p))
    print(f"Wrote {len(PROJECT_TRACK['projects'])} project(s), {n_mod} authored "
          f"modules ({n_ex} judged exercises) to {os.path.relpath(out)}")
