# Projects Roadmap — the Todo API, modules 5-20

The plan for finishing **Todo API**, the first project in the new **Projects**
track (`tools/projects_track.py`). Modules 1-4 ship; 5-20 are one-line skeletons
waiting to be authored.

Where [`TS_ROADMAP.md`](TS_ROADMAP.md) plans a *time* ladder (32 weeks) and
[`JAVA_ROADMAP.md`](JAVA_ROADMAP.md) plans a *topic* ladder (31 modules), this
one plans a **build** ladder: every module leaves the application able to do one
more thing than it could before, and the roadmap is the order those capabilities
arrive in.

**Status legend** — ✅ built and shipping · 🚧 partially built · ⬜ planned.

---

## Where it stands

**Built:** modules 1-4 — **16 steps, 29 judged exercises**, four revealable
reference implementations, and the full infrastructure the other sixteen
modules will drop into. Both program shapes are proven end to end: `_plain`
(modules 1-3) and `_server` (module 4 on, booting a real server on port 0).

| | |
|---|---|
| Content generator | `tools/projects_track.py` (~700 lines) + one `todo_mNN_*.py` per module |
| Generated seed | `src-tauri/seeds/projects.json` |
| Rust model | `ProjectTrack` → `Project` → `ProjectModule` → `BackendStep` in `models.rs` |
| Command | `projects_track` (`commands.rs`), registered in `lib.rs` |
| UI | `src/pages/Projects.tsx`, routes `/projects`, `/projects/:project`, `/projects/:project/:module` |
| Fast verifier | `python tools/verify_projects.py --starters` (~40 s at 4 modules) |
| Judge-level verifier | `cd src-tauri && cargo test --test verify_projects` (~28 s at 4 modules) |

### The five questions every module answers

This is the track's actual product, and it is what the model is shaped around.
A module is not a chapter; it is a full pass through the development process at
a size that fits in one sitting.

| # | Question | Field |
|---|---|---|
| 1 | Why does this module exist? | `why` — the problem the *previous* module left behind |
| 2 | Where does it sit? | `phase` + `builds_on` + `deliverable` |
| 3 | What syntax do I need? | `syntax: SyntaxItem[]` — form, meaning, example, gotcha |
| 4 | What do I do? | `steps[]` — instructions, `checkpoint`, `pitfalls`, warm-up, exercises |
| 5 | Did I get it? | `final_build` + `acceptance` + `reference` (the reveal) |

---

## Six decisions — all taken ✅

Cheap to settle before authoring, expensive after.

### 1. A new track, not an eighth Backend Lab project ✅

The Backend Lab already builds a CRUD API. The overlap is real and the decision
was to leave it alone, because the two differ in the thing that matters:

| | Backend Lab | Projects |
|---|---|---|
| Language | JavaScript | TypeScript |
| Unit | a project (a whole server, one evening) | a module (one capability, 30-60 min) |
| Depth | 2 levels (Project → Step) | 3 levels (Project → Module → Step) |
| Assumes | you already write code | nothing — every token is taught before use |

Folding this into the Backend Lab would have meant inheriting the 2-level model,
which has nowhere to put a per-module roadmap position, syntax primer or `why`.
Those are the whole point.

### 2. TypeScript runs a real HTTP server under the existing judge ✅ — verified

This was the risk that could have sunk the track, so it was tested first. Node
runs `.ts` by *stripping* types, and the judge type-checks before running. Both
halves work for a server program:

```ts
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
```

runs, and type-checks clean. **Named imports, never default** — `import http
from "node:http"` makes `http.IncomingMessage` a *namespace* reference, which
the hand-written ambient declarations cannot satisfy without declaring one.
Named type imports are the better lesson anyway.

### 3. The ambient declarations were extended, narrowly ✅

`src-tauri/tslib/poodcode-env.d.ts` deliberately ships no `@types/node` (2.6 MB
plus transitive deps). Three things were missing and are now declared by hand,
each because a shipped program uses it: **`node:http`** (`createServer`,
`IncomingMessage`, `ServerResponse`, `Server`), **`URL`/`URLSearchParams`**, and
**`fetch`**.

Two choices inside that worth knowing:

* `req.on("data", …)` types its chunk as `string`, which is only true after
  `req.setEncoding("utf8")`. **Module 8 therefore teaches `setEncoding` before
  reading a body** — which makes the declaration honest and is better practice
  anyway.
* `Response.json()` returns `Promise<unknown>`, not `any`. Module 13's whole
  argument is that parsed input has to earn its type; a declaration handing back
  `any` would undercut it.

**Proved safe for the existing course:** all **897** TypeScript-course exercise
solutions still type-check clean against the extended file (`python
tools/verify_ts_course.py --types-only --starters`). Re-run that after any
further change here — a global added to this file is visible to every track.

### 4. `strict+indexed` everywhere, and it is content ✅

The whole track type-checks under `noUncheckedIndexedAccess`. This is not a
formality: module 10 splits a URL path and reads segment 2, and `/todos` has no
segment 2. The flag turns the single most common JavaScript crash into a
question asked at authoring time. Module 3 introduces it explicitly rather than
letting it ambush module 10.

### 5. Two lints, not one ✅

`_TODO_SCOPE_RULES` maps a token to the module that introduces it. Two passes
read it:

* **`_lint_scope`** — fails generation if an *earlier* module's program uses the
  token. (This is the Backend Lab's rule, and it works.)
* **`_lint_syntax_taught`** — fails generation unless the module at that number
  also **teaches** the token in its `syntax` primer.

The second is the new one and it is what makes the track's pitch enforceable
rather than aspirational. A scope rule with no matching syntax entry means the
track uses something it never explained; the build now refuses.

The given replayer is exempt via the `// ---- request replayer (given` marker —
it shows `async`/`await` in module 4, four modules before they are taught, and
counting that would be a false claim about what the learner is expected to write.

**It has already earned its keep:** module 2's id-collision demo needed to
remove an element, reached for `.splice(`, and the build failed because module
12 is supposed to introduce that. Swapped to `.shift()` (one line to explain,
and it leaves `splice` to the module where removing *by id* is the actual job).

### 6. Deterministic by construction ✅

Ids are counters, never `crypto.randomUUID()`; nothing prints a timestamp;
servers bind port 0 and the replayer prints one line per request in order.
Module 2 states the trade-off outright — a counter resets on restart and
collides across processes, which is exactly why production does not use one —
so the simplification is taught rather than hidden.

---

## The 20 modules

### Phase 1 — Model the data (1-3) — ✅ **done**

Ends with: a `Todo` type and an in-memory store you can add to, list and search.

**1. What a todo is** ✅ · `todo_m01_shape.py` · 4 steps, 8 exercises
Fields justified from the contract · `type` vs `interface` · annotation vs `as` ·
excess property checking · `JSON.stringify` and insertion order · a factory with
a declared return type.
**What it cost that the plan didn't predict:** nothing — but note it may use
*no* gated token at all, which rules out arrays, `find`, arrow functions and
stdin. Programs print a fixed sequence and carry one test each. That constraint
is why the module is about design rather than code volume.

**2. The store** ✅ · `todo_m02_store.py` · 4 steps, 8 exercises
Module state · `const` binding vs contents · the id counter · `for…of` vs
`for…in` · 200 + `[]` rather than 404.
**The module's real payload** is the `todos.length + 1` collision, demonstrated
as a runnable program rather than asserted — add, add, delete the first, add,
and watch two todos come out with id 2.

**3. Finding one, and the `undefined` you must handle** ✅ ·
`todo_m03_lookup.py` · 4 steps, 8 exercises
Arrow functions · `.find` · `Todo | undefined` · narrowing · what `!` costs in
status codes · `noUncheckedIndexedAccess`.
**This is the module the next seventeen lean on.** Every 404 in modules 10-12 is
this `if` with an HTTP response in it, and it is deliberately taught before
there is any HTTP in the way.

### Phase 2 — Put it on the network (4-7) — 🚧 **4 done, 5-7 outstanding**

Ends with: a real server answering `GET /todos`, 404ing everything else.

**4. Your first server** ✅ · `todo_m04_server.py` · 4 steps, 5 exercises
Named imports from `node:http` · the handler and what `req`/`res` are ·
`createServer` vs `listen` · `res.end` and the silent hang · reading the given
replayer.
**Two things the plan didn't predict.** The replayer owns `createServer` and
`listen`, so the judged exercises are always `handler` and nothing else — those
two are taught for the learner's own `server.ts` and appear in no blank. And
the module needed a fourth step nobody planned: *reading the replayer*. It has
been silently providing an error boundary since the first exercise, and leaving
that unexplained makes the exercises feel like magic. Step 4 also sets up module
16, where the learner writes that boundary themselves.
**Kept deliberately small:** every request gets the same answer. Step 3 makes
that the point rather than an omission, because a module that half-routes is a
mess you debug in module 7.

**5. Status codes and JSON** ⬜ · `writeHead`, `Content-Type`, one `send` helper
*Note:* the `send(res, status, data)` helper introduced here is used unchanged
for the rest of the project, so it is worth getting the signature right. The
Backend Lab's version is a good reference.

**6. Reading the request** ⬜ · `req.method`, `new URL(req.url ?? "/", base)`
*Why a `URL` rather than a string compare:* `/todos?done=true` does not equal
`/todos`, and finding that out in module 17 would mean rewriting the router.

**7. Routing, and 404 as the default** ⬜ · match method + path, fall through
*Capstone of the phase:* wires phase 1's store to the network. First module
where the learner sees their own data over HTTP.

### Phase 3 — Full CRUD (8-12)

Ends with: create, read, update and delete — the complete resource.
One module per verb, because each has its own status code and its own failure.

**8. Reading a request body** ⬜ · streams → promise, `async`/`await`,
`setEncoding`
*Introduces `async`/`await`* (decision 3: `setEncoding` first, so the chunk
really is a `string`). *Risk:* the biggest single syntax jump in the track.
Budget a longer module; consider splitting the promise wrapper into its own step
with its own drills.

**9. POST /todos — create** ⬜ · `JSON.parse`, 201, the id the client did not send

**10. GET /todos/:id — dynamic paths** ⬜ · `.split("/")`, `Number()`,
`Number.isInteger`
*This is where decision 4 pays off:* `parts[2]` is `string | undefined`, and
`/todos` really does hit this handler. Also the first 404 that is a real 404.

**11. PATCH /todos/:id — partial update** ⬜ · `Partial<Todo>`, object spread
*Introduces `...`*, which means every earlier module's programs must avoid a
literal `...` even inside a comment — the lint scans program text, not just code.

**12. DELETE /todos/:id — and 204** ⬜ · `findIndex`, `splice`, the empty body
*Closes the resource.* Pays off module 2's counter argument: this is the delete
that would have caused the collision.

### Phase 4 — Make it trustworthy (13-16)

Ends with: bad input gets a specific 400 naming the field — never a 500.

**13. `unknown` at the boundary** ⬜ · `JSON.parse` hands back `any`
*The pivot of the whole track.* Everything up to here assumed the client sends
what it promised. Cannot be taught as a "spot the error" exercise, because the
whole point is that **there is no error** — `any` is silent. The TypeScript
course's week 15 solved the same problem with its `retype` exercise kind; the
equivalent here is a `fix` whose starter compiles, runs, and returns nonsense.

**14. Validation and a field-level 400** ⬜ · a validator returning collected
errors
*Introduces `.map(`.* Output shape:
`{"error":"validation","fields":[{"field":"title","message":"must not be empty"}]}`

**15. One error shape, everywhere** ⬜ · a discriminated union, one place that
renders it
*The natural home for the track's second union*, and the module that makes
modules 9-12 shorter in retrospect. Consider having the learner refactor an
earlier handler as the build.

**16. The error boundary** ⬜ · `try`/`catch`, `headersSent`, no leaked traces
*Note:* the given replayer has always had this boundary in it (that is where its
500 comes from). This module is where the learner reads the code that has been
quietly protecting them since module 4 — a nice payoff if the step names it.

### Phase 5 — Make it real (17-20)

Ends with: a queryable, paginated, restart-proof API behind a router worth
extending.

**17. Filtering with query strings** ⬜ · `searchParams`, `.filter(`, and a
default for `?done=banana`

**18. Sorting and pagination** ⬜ · `.sort(`, `.slice(`, the `{items, total}`
envelope
*Contract change:* `GET /todos` stops returning a bare array. Say so loudly —
it is the project's one breaking change, and that is worth a paragraph about
why envelopes exist.

**19. Persistence on disk** ⬜ · `readFileSync`/`writeFileSync`, and validating
what you load
*Two things to get right:* the file is untrusted input too (module 13 applies to
your own disk), and the judged exercises must write to the scratch directory the
runner already provides. *Risk:* medium — check that a file written by one test
case does not leak into the next, since the judge reuses the compile artifact
across cases.

**20. A router, layers and a smoke test** ⬜ · split store/service/routes, then
prove it
*Closes the project.* The test runner is written by hand — zero dependencies —
which doubles as the argument for what a test framework actually does.

---

## Suggested batching

Each batch ends green and committable.

| Batch | Modules | Why this grouping |
|---|---|---|
| **A** ✅ | — | Model, command, page, generator, both verifiers, ambient declarations |
| **B** ✅ | 1-3 | Phase 1 — the data model, with no HTTP in the way |
| **C** 🚧 | 4 ✅, **5-7 left** | Phase 2 — first server. 4 landed early to prove the `_server` shape |
| **D** | 8-12 | Phase 3 — CRUD. Module 8 is the syntax jump; budget for it |
| **E** | 13-16 | Phase 4 — the trust story. 13 needs its exercise format decided first |
| **F** | 17-20 | Phase 5 — polish, persistence, structure |

**Module 8 is the one to think about before starting batch D**, and module 13
before batch E. Everything else is straightforward once phase 2 establishes the
program shape.

---

## Constraints every module must satisfy

* **Nothing before its module.** `_TODO_SCOPE_RULES` + `_lint_scope` fail the build
  if a program uses a token a later module introduces. Add the new module's
  tokens as it lands — and check first that no earlier module already uses one,
  or the rule is a false claim.
* **Every token is taught.** `_lint_syntax_taught` fails the build unless the
  introducing module's `syntax` primer shows the token. This is the half that
  makes the track self-contained.
* **Erasable syntax only.** The judge strips types rather than compiling them,
  so `enum`, `namespace` and parameter properties cannot run. All three are
  banned outright in every scope table (module 999) — unlike the TypeScript course,
  this track has no reason to teach them.
* **Named imports from `node:http`.** See decision 2.
* **Deterministic by construction.** Counters, not UUIDs. No timestamps. Port 0
  plus an ordered replayer.
* **Expected output is computed, not typed** — same trust model as the rest of
  the app.
* **Both verifiers must pass**: `python tools/verify_projects.py --starters` and
  `cd src-tauri && cargo test --test verify_projects`.

### Adding module N

1. Write `tools/todo_mNN_topic.py` — it appends one `_pmod(…)` to
   `_TODO_MODULES` and may use any helper from the parent.
2. Add it to `_TODO_MODULE_FILES` **in module order**, and delete the matching
   `_pskel` line from the skeleton list below it.
3. Add that module's new syntax to `_TODO_SCOPE_RULES`, and make sure the module's
   `syntax` primer teaches each token — `_lint_syntax_taught` will tell you if
   not.
4. `python tools/gen_seed.py && python tools/verify_projects.py --starters`

### A trap worth knowing

`_lint_scope` scans **program text, not code** — comments and strings included.
So a module numbered below 11 may not contain a literal `...` anywhere in a
program, even in prose inside a comment. Modules 1-3 use the Unicode ellipsis
`…` in their teaching text for exactly this reason.

---

## What "done" looks like

One project · 20 modules · 5 phases · roughly 160 judged exercises · a Todo API
that validates, paginates and persists · and a learner who was never once asked
to write a line of TypeScript the track had not already taught them.

## The second project

It landed early — see [`CALC_ROADMAP.md`](CALC_ROADMAP.md). **Calc**, an
expression language: scanner, parser, evaluator, error messages. Module 1 ships,
2-18 are planned.

It is not a queue-jump so much as a hedge: the Todo API teaches the shape of a
service and barely touches the type system, because HTTP hands you strings and
takes strings back. A language processor is three transformations over data you
designed yourself, every one of them a discriminated union walked recursively,
and it is where `never`, recursive types and exhaustive narrowing have a reason
to exist. The two projects share no subject matter at all, so they can be
authored in either order.

**What that cost this file's assumptions:** `_SCOPE_RULES` is now
`_TODO_SCOPE_RULES`, and both lints take the table as an argument — a syllabus
is a property of a project, not of the track. The track-level `harness_note`
also had to stop claiming that every program boots a server from module 4 on.
Everything else in the model turned out to be general already.
