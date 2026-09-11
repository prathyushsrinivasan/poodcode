# Projects Roadmap — the Todo API, modules 14-20

The plan for finishing **Todo API**, the first project in the **Projects** track
(`tools/projects_track.py`). Modules 1-13 ship — phases 1, 2 and 3 are complete
and phase 4 is under way — and 14-20 are one-line skeletons waiting to be
authored.

Where [`TS_ROADMAP.md`](TS_ROADMAP.md) plans a *time* ladder (32 weeks) and
[`JAVA_ROADMAP.md`](JAVA_ROADMAP.md) plans a *topic* ladder (31 modules), this
one plans a **build** ladder: every module leaves the application able to do one
more thing than it could before, and the roadmap is the order those capabilities
arrive in.

**Status legend** — ✅ built and shipping · 🚧 partially built · ⬜ planned.

---

## Where it stands

**Built:** modules 1-13 — **52 steps, 124 judged exercises**, thirteen revealable
reference implementations (all type-checked by the verifier since module 12
landed), and the full infrastructure the other eight modules will drop into.
Both program shapes are proven end to end: `_plain` (modules 1-3, and the
function-level steps of 10-12) and `_server` (module 4 on, booting a real server
on port 0).

**Phase 3 closed with module 12.** Every verb on the resource works — list,
create, fetch, patch, delete — and the phase ended by paying off two debts from
phase 1: module 3's `Todo | undefined` became the project's first real 404s
(module 10), and module 2's id counter was vindicated by grading the collision a
`todos.length + 1` store causes after a delete (module 12).

**Phase 2 closed with module 7**, which is the first module where the learner's
own data goes over HTTP. The application now answers `GET /todos` from the store
and 404s everything else, behind a router that the remaining twelve modules
add one `if` to each.

**Phase 3 opened with module 8**, the track's biggest syntax jump, and it landed
without needing the extra budget the plan set aside. **Module 9 closed the loop
that started in module 1**: data in the application now comes from outside it,
the seed calls and the `/echo` route are gone, and the API accepts three things
it should not — which is the whole argument for phase 4, made from evidence
rather than assertion.

| | |
|---|---|
| Content generator | `tools/projects_track.py` (~700 lines) + one `todo_mNN_*.py` per module |
| Generated seed | `src-tauri/seeds/projects.json` |
| Rust model | `ProjectTrack` → `Project` → `ProjectModule` → `BackendStep` in `models.rs` |
| Command | `projects_track` (`commands.rs`), registered in `lib.rs` |
| UI | `src/pages/Projects.tsx`, routes `/projects`, `/projects/:project`, `/projects/:project/:module`, and four project-level pages — `reference`, `history`, `workbench`, `review` |
| Handbook index | `src/lib/projectIndex.ts` — six indexes: syntax, glossary, pitfalls, checks, contract, cheat sheets |
| Build history | `src/pages/ProjectHistory.tsx` + `src/lib/lineDiff.ts` (the app's one line diff — `lib/diff.ts` wraps it) |
| Workbench | `src/pages/ProjectWorkbench.tsx` + `src/lib/workbench.ts` — runs through `run_scratch` / `run_tests` |
| Review | `src/pages/ProjectReview.tsx` + `src/lib/projectReview.ts`; option order from `src/lib/quizShuffle.ts` |
| Fast verifier | `python tools/verify_projects.py --starters` — every solution, every starter, and every module `reference` type-checked |
| Judge-level verifier | `cd src-tauri && cargo test --test verify_projects` |

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

### The Handbook — where questions 3, 4 and 5 go to live

`/projects/:project/reference` gathers four kinds of module writing into one
searchable page (`src/lib/projectIndex.ts`). It started as a syntax-and-glossary
reference; it grew two more tabs once it became clear the tabs are read at
completely different *moments*:

| Tab | Source field | Ordered | Read when |
|---|---|---|---|
| 🔤 **Syntax** | `syntax[]`, minus recaps | by module | you are learning — top to bottom it *is* the syllabus |
| 📖 **Glossary** | `glossary[]` | A-Z | you arrive with a word in hand |
| ⚠️ **Pitfalls** | every step's `pitfalls[]` | by module, then step | **something is broken** |
| ✅ **Checks** | each module's `acceptance[]` | by module | **something that used to work has stopped** |
| 📋 **Contract** | each module's `endpoints[]` | by the module that added the row | "when does `DELETE` start working?" · "did `GET /todos` change under me?" |
| 🧾 **Cheat sheets** | each module's `cheatsheet` | by module | you want the whole project on one page |

The bottom two are the reason the page stopped being called a reference. They
are the tabs you open in a hurry, and until they existed the forty-odd pitfalls
the track has written lived inside a *collapsed step* inside a module you had
already finished — which is exactly the wrong place, because you want that list
at the one moment you are not reading the module that wrote it.

Three details worth keeping through any rewrite:

* **A pitfall row deep-links to its step**, not to the module — `?step=<key>`,
  which `ModuleDetail` already opens and scrolls to. Landing on the top of a
  1,000-line module page would have thrown away half the feature.
* **Pitfalls are not deduplicated per module.** Two modules warning about the
  same trap from different angles is the track working. Only a byte-identical
  repeat is dropped. (Syntax is the opposite: first-taught wins, always.)
* **One search box, four indexes, and it says where else it hit.** A query with
  no match in the current tab prints `also 3 in ⚠️ Pitfalls` as a link. This is
  the cheapest thing on the page and the one that changes how it is used —
  searching a symptom like `hangs` lands in Pitfalls without knowing to go there.

**The contract tab is the one that reads the project as a ladder**, and two
rules keep it honest:

* **A rewording is not a revision.** Rows are compared on `request`, `response`
  and `status` only — never `purpose`, which is prose a later module often puts
  better. The newest wording wins for display; only a contract change is listed
  under "Changed in". Building this immediately caught `GET /todos` being
  reported as changed in modules 8 and 9 when it had not moved since 7, and both
  modules' rows were corrected.
* **Retirement is declared in the data, not the schema.** A module that removes
  a route re-declares it with an **em-dash status**, and the row renders struck
  through. Module 9 does this for module 8's `POST /echo`. Without it the
  contract index would go on advertising a route the application no longer has —
  and "this used to exist" is worth keeping rather than deleting.

**What that asks of a module author.** Six fields stopped being page decoration
and became index entries. Four of these are new asks:

* **`pitfalls` are now a published index**, so write each one as a *symptom
  first*, not a cause first — "the request hangs with no error anywhere;
  `resolve` was never called" rather than the reverse. That is the word the
  reader searches for.
* **`acceptance` is now cross-module**, so each check must make sense out of its
  module's context. Name the command and the expected answer.
* **`endpoints` rows must be word-for-word identical to the previous module's**
  when the route has not changed, or the contract tab reports a revision that
  did not happen. Reword the `purpose` freely; leave `request`/`response`/
  `status` alone unless you mean it.
* **`cheatsheet` is read as part of one long page**, so it must stand on its own
  — no "as above", no pronouns pointing at the module's prose.

* **`recap=True` now means something.** A recap is dropped from the index, on
  the grounds that it points at an explanation rather than being one. So mark a
  primer entry `recap` whenever an earlier module introduced the form — module 7
  recaps the store, the parse and `send` — and do *not* mark the module's own new
  syntax that way, or it vanishes from the index.
* **`form` is a key.** Entries are deduplicated by exact `form` string, so write
  it the way the code writes it (which `_lint_syntax_taught` already required)
  and keep it identical across a recap and its original.

Nothing about this changes the seed or the Rust model — it is all derived from
data the modules already carry.

### Three more pages, and what each asks of an author

The Handbook indexes the *prose*. Three more project-level pages use the parts
of a module the Handbook never touched — and like it, none needed a model change.

| Page | Reads | What it is for |
|---|---|---|
| 🕰️ **Build history** | every module's `reference` | the ladder as a sequence of diffs — "what did module 9 do?" answered in code |
| 🧪 **Workbench** | every module's `final_build` | run a build against requests of your own, through the real judge |
| 🔁 **Review** | every `warmup`, step `quiz` and module `review` | ~170 questions asked again, mixed, misses first |

Details worth keeping:

* **Build history defaults to "code only"**, ignoring whole-line comments and
  blank lines. The references rewrite their commentary as the project learns
  more, and it swamps the signal: module 9 is `+4 −4` in code and `+40 −48` with
  comments. Line numbers stay the original ones either way.
* **The Workbench never overwrites silently.** "Open in the workbench" on a
  module page arrives as `?load=<module>` and *offers* the load; loading over
  code that exists nowhere else — not the reference, the starter or the
  learner's draft — asks first. It also never marks anything solved.
* **Replies are only paired with requests when that is provably right**: one
  `<status> <body>` line per non-blank request line, or the raw output instead.
  A handler that `console.log`s would otherwise put answers next to the wrong
  requests.
* **Every quiz's options are shuffled for display**, stably, seeded by the
  question text (`quizShuffle.ts`). All 125 Projects questions — and all 717 of
  the Java course's — had `answer: 0`, so the right option was always the top
  button. Authors can keep writing the right answer first.

What that asks of a module author:

* **`reference` is now diffed against its predecessor**, so keep unchanged code
  byte-identical between modules — reordering functions for no reason shows up
  as churn. And it is now **type-checked** at `strict+indexed` by the verifier;
  a reference is the learner's file, so it `listen`s on 3000 and is never run.
* **`final_build.tests[0].input` is the Workbench's default request script.**
  Make the first test the one worth replaying by hand.
* **Quiz questions are now read out of context.** A review question that says
  "the function above" means nothing in the Review page; name the thing.

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

### Phase 2 — Put it on the network (4-7) — ✅ **done**

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

**5. Status codes and JSON** ✅ · `todo_m05_json.py` · 4 steps, 10 exercises
`writeHead` · the header object · `Content-Type` · `JSON.stringify` key order ·
the `send(res, status, data)` helper · the six status codes and whose fault each
one is.
**The decision the plan didn't have to make:** what type `data` is. `unknown` is
gated to module 13 and a union of today's shapes would need editing in six later
modules, so it is **`object`** — true of every response this API sends, since an
array is an object, and it usefully rejects a bare string. Module 13 sharpens it.
**A gap worth knowing about:** the replayer prints `<status> <body>` and no
headers, so **no exercise in this module can check `Content-Type`**. Step 2 says
so outright rather than letting a learner find it; the header is verified by the
acceptance list and `curl -i`. It is the only place in the track with this hole.
**The answer is 404, deliberately** — a server that handles no routes yet has
"there is nothing at this address" as its *correct* answer, and module 7 then
adds routes above a working default rather than building both at once.

**6. Reading the request** ✅ · `todo_m06_request.py` · 4 steps, 10 exercises
`req.method` · `req.url` and why the name lies · `??` · `new URL(target, base)` ·
`.pathname`.
**The structure the plan didn't predict** is the method/URL split, and it is
worth preserving through any re-cut: `req.method` is only ever *compared*
(`req.method === "GET"` is legal on `string | undefined` with no narrowing), so
it needs nothing; `req.url` has its value *used*, so it needs the fallback. That
is why `??` is introduced in step 2 rather than step 1 — it lands at the first
point the compiler forces it, since `new URL(req.url, base)` is a type error.
**Two exercises had to be rewritten** because the verifier caught them: a `fix`
on `||`-vs-`??` and one on the disappearing `undefined` key both only misbehave
on a *malformed* request, and the replayer only ever sends well-formed ones. Both
lessons are still taught in prose, pitfalls and quizzes; the graded fixes became
"the right union, the wrong property" and "parsed once, for every request", which
fail on ordinary input. **Worth remembering when authoring modules 8-20: if a
bug needs a broken request to show itself, it cannot be a graded `fix`.**

**7. Routing, and 404 as the default** ✅ · `todo_m07_routing.py` · 4 steps, 8 exercises
The route as method + path · `&&` not `||` · the `return` after every `send` ·
serving the store · the fall-through as the last statement · adding a second
route · 405.
**Capstone of the phase, and it introduces no new gated syntax at all** — which
is the mark of a capstone working. Everything is composition: `if`, `&&`,
`return`, the store from 2-3, `send` from 5, the parse from 6.
**Seeded at boot:** there is no POST until module 9, so the programs call
`addTodo` twice before `listen` or `GET /todos` would only ever return `[]`.
Deleted in module 9.
**No timeout-based exercise, on purpose.** The signature bug here — a handler
with no fall-through — *hangs* rather than failing, so grading it would cost a
25 s Python timeout plus a 30 s Rust one to re-teach what module 4 step 3 already
covers with a one-line `res.end()` fix. It is taught in the warm-up, the pitfalls
and a manual test that has you delete the line and watch curl sit there.
**The 405 question is raised and answered "no":** `POST /todos` is arguably a 405
rather than a 404, and doing 405 properly needs the set of verbs a path allows
plus an `Allow` header — which is a routing table, which is module 20. Naming the
simplification is cheaper than a learner finding it.

### Phase 3 — Full CRUD (8-12) — ✅ **done**

Ends with: create, read, update and delete — the complete resource.
One module per verb, because each has its own status code and its own failure.

*A contract fix found while building phase 3:* module 7 added `GET /health` as
its example of extending the router, and module 8's programs and reference
dropped it without declaring a retirement — so the Handbook's contract tab went
on advertising it. Module 8 now carries the em-dash row that says so.

**8. Reading a request body** ✅ · `todo_m08_body.py` · 4 steps, 12 exercises
`req.on("data")` / `"end"` · `setEncoding` · `new Promise` · `.then` ·
`async`/`await` · the body inside a route.
**The plan's advice was right and was taken:** the promise wrapper got its own
step. What the plan did not predict is that it wanted *three*, not two — the
module is one idea taught three times, and the ladder is the module:

| Step | Shape | What it fixes | What is still wrong |
|---|---|---|---|
| 1 | `req.on("end", …)` | first thing that works | the body only exists in a callback |
| 2 | `readBody(req).then(…)` | collecting becomes a reusable function | still a callback, still cannot `return` |
| 3 | `await readBody(req)` | the body is a value on a line | nothing |
| 4 | in the router | module 7's shape, plus one `await` | — |

Teaching `await` first and back-filling the events saves ten minutes and loses
the reason any of it exists. **`.then(` was added to `_TODO_SCOPE_RULES` at 8**
so that step 2 is a taught shape rather than a smuggled one.

**A whole family of bugs turned out to be ungradable, and it is worth
remembering.** Every accumulation bug here — `body = chunk` instead of
`body = body + chunk`, `resolve` in the `"data"` listener instead of `"end"`,
answering from the first chunk — is **invisible at test size**, because Node
delivers a 20-byte body in exactly one chunk. The buggy and correct programs
print the same thing. This is module 6's rule in a new costume: there, a bug
needed a *malformed* request; here it needs a *64 KB* one. All three are taught
in prose, pitfalls and quizzes; the manual test has you post 200 KB and watch one
of them finally show up.

The two graded `fix`es were chosen because they fail on a five-byte body, and
both fail at run time rather than compile time:
* `send` outside the `"end"` listener → answers `{"echo":"","length":0}` instantly
* a missing `await` → answers `{"echo":{}}` with a 200 and no error anywhere

**No hang is graded**, for module 7's reason: a promise that never resolves is
this module's signature disaster and costs 25 s + 30 s of timeout per run,
forever, to re-teach module 4 step 3.

**`/echo` is scaffolding and the module says so.** `JSON.parse` is module 9's, so
the only honest thing to do with a body today is hand it back — and the reply
comes back with its quotes escaped, which is the cleanest possible proof that
you are holding *text*, not an object. Module 9 deletes the route and keeps the
`await readBody(req)` line verbatim.

**9. POST /todos — create** ✅ · `todo_m09_create.py` · 4 steps, 10 exercises
`JSON.parse` and the `any` it hands back · 201 Created · the id the client did
not send · the route, and the empty list.
**The module where the application stops being yours** — the first data in it
that came from outside the process, and the first time "what id does it get?"
has the answer "not the one they sent".
**The plan's three bullets held, and a fourth was needed:** the deletions.
The two `addTodo` seed calls (module 7) and the `/echo` route (module 8) both
come out here, and both had a stated expiry date when they were added, so this
is a debt being paid rather than a change of mind. `GET /todos` on a fresh
process now correctly returns `200 []` — which step 4 makes a point of, because
reaching for 404 there is a real and common misreading of what a collection is.
**The 500 is graded on purpose.** `POST /todos notjson` produces
`500 {"error":"server_error"}` through the replayer's boundary, and the module
build asserts it. It is the cheapest demonstration of what phase 4 is for: the
API's answer to bad input today is "something broke on our end", which is a lie.
Grading the lie is what stops it being a surprise in module 14. The manual test
goes further and shows three requests the route wrongly accepts — `not json`,
`{}` and `{"title":""}` — with zero crashes between them, which is the whole
argument for `unknown` in one screen.
**A technique gets named here** and it is reused in module 11: the client's `id`
is *ignored, not rejected*, because `addTodo` takes a title and there is no
parameter an id could travel through. The safest way to ignore input is to write
code with nowhere to put it.

**10. GET /todos/:id — dynamic paths** ✅ · `todo_m10_one.py` · 4 steps, 12 exercises
`.split("/")` and index 2 · `Number` and the `NaN` it answers instead of failing
· `Number.isInteger` · `undefined` in a return type · 404 over 400.
**The design is three functions, one idea each** — `idText` (is the path shaped
`/todos/<x>`?), `parseId` (is `x` a whole number from 1?) and `todoId` (both).
Steps 1 and 2 are `_plain` programs that print what each function makes of eight
inputs, so one exercise checks eight paths and a wrong answer is a wrong line,
not a wrong status three requests later.
**Decision 4 paid off exactly as planned — and it is graded at compile time.**
`return parseId(idText(pathname))` fails with TS2345, because the `undefined`
from `parts[2]` travels through `idText`'s honest return type to the one function
that needs a string. `todo-m10-route-fix1` is the only `fix` in the project whose
starter is *meant* to fail at compile time, and the verifier lists it for that
reason. Without the flag, `todoId("/todos")` would have been a silent `NaN`
lookup.
**`/todos/abc` is a 404**, argued from module 5's definition: a `GET` sends
nothing that could be wrong. `Number("")` is `0` — the empty piece `/todos/`
produces — so `id < 1` is load-bearing and graded.
**Module 9's promise kept:** the `Location` header is in the stretch list, now
that it would point at something.

**11. PATCH /todos/:id — partial update** ✅ · `todo_m11_update.py` · 4 steps, 12 exercises
`Partial<Todo>` · `changesFrom` · object spread and "later key wins" · absent vs
`undefined` · `indexOf` and replacing in the store · lookup before read.
**Two things the plan did not predict.** Replacing needs a *position*, and
`.findIndex(` was module 12's — so `.indexOf(` was added to the scope table at
11: you hold the object `findTodo` returned and want where it is. Module 12's
`findIndex` then has the other question to itself (you have only an id). And
`changesFrom` takes **`data: any`, written out loud** — the honest type of what
`JSON.parse` returned, and the single word module 13 changes to `unknown`, at
which point every line of the function stops compiling. That is module 13's
whole argument, set up on purpose.
**Replace, not mutate, is justified by module 14**, not by style: a new object
can be validated before it is stored, so a rejected patch leaves the store
untouched. The step says so; module 14 should cash it.
**The best graded bug is the explicit `undefined`:** `{ title: data.title, done:
data.done }` for a `{"done":true}` body makes `title: undefined`, which wins the
spread, and `JSON.stringify` drops it — the title vanishes and nothing errors.
**Lookup before read is graded too**: `PATCH /todos/9 notjson` must be a 404, and
parsing first makes it a 500. (Verified first: answering before reading a body —
even a 200 KB one — is safe under the replayer.)

**12. DELETE /todos/:id — and 204** ✅ · `todo_m12_delete.py` · 4 steps, 9 exercises
`findIndex` and `-1` · `splice(i, 1)` · positions vs ids · `sendEmpty` and 204 ·
module 2's collision.
**Closes the resource, and every graded bug is silent data loss** — which is why
they are worth grading: an unchecked `-1` makes `splice(-1, 1)` delete the *last*
todo and answer 204; `splice(i)` deletes everything after `i` too. **Module 2 is
paid off over HTTP**: a `todos.length + 1` store hands out id 3 twice after
deleting the middle of three.
**One lesson turned out ungradable, found by testing before authoring:** Node's
`ServerResponse` silently discards a body sent with a 204, so `send(res, 204, …)`
prints exactly `204` through the replayer, like the correct `sendEmpty`. Taught
in prose and in the manual test, where `curl -i` shows the stray
`Content-Type`. This joins trap 3's list below.
**A second response helper**, `sendEmpty(res, status)`: module 5's rule — every
response leaves through a helper — still holds, with one helper per kind.

### Phase 4 — Make it trustworthy (13-16)

Ends with: bad input gets a specific 400 naming the field — never a 500.

**13. `unknown` at the boundary** ✅ · `todo_m13_unknown.py` · 4 steps, 12 exercises
`unknown` vs `any` · `typeof` and the three kinds it calls `"object"` ·
`Array.isArray` · the `in` operator · `objectFrom` / `titleFrom` / `changesFrom` ·
the first 400.
**The format problem the plan worried about solved itself.** The plan said this
module could not be "spot the error" because `any` is silent. Module 11 had
already written `changesFrom(data: any)`, so the one-word change to `unknown`
produces a *list* of compile errors — every place the API trusted a client — and
the brief tells the learner to make that change first and read the list. The
graded exercises then split cleanly: most mistakes are now compile errors (one
`fix` is deliberately compile-time, the missing `in` check), and the runtime ones
are exactly what `unknown` cannot check for you — `typeof null` and arrays being
`"object"`, and the old trusting route itself, which is the plan's "starter
compiles, runs, and returns nonsense", graded as `todo-m13-create-fix1`.
**A decision the plan did not make: the bare 400 arrives here, not in 14.** When
narrowing fails, the compiler insists on an answer, and a body of the wrong shape
is the client's fault. So module 13 answers `400 {"error":"invalid_body"}`, and
module 14 replaces it with one that names the field. Module 9's status table and
its forward references were corrected to match.
**Shape here, values in 14** — the split that makes two modules rather than one.
`{"title":""}` is a string, so module 13 accepts it and says so in its build;
refusing it is a rule of the application, not a fact about types.
**`not json` stays a 500**, and module 13 says why: `JSON.parse` throws before
there is a value to check. Module 9 had claimed module 14 would make it a 400,
which no module before `try`/`catch` (16) can do; modules 9 and 11 now say 16.
**A crash removed on the way**: `POST /todos null` was a 500 (reading `.title` off
`null` throws) and is now a 400. Worth pointing at, because it shows checking the
shape is not only about quiet wrong answers.
**Scope table:** `'" in '` added at 13 — written with the closing quote so it
matches `"title" in obj` and never a `for … in` loop.

**14. Validation and a field-level 400** ⬜ · a validator returning collected
errors
*Introduces `.map(`.* Output shape:
`{"error":"validation","fields":[{"field":"title","message":"must not be empty"}]}`
*What module 13 left it:* `titleFrom` and `changesFrom` already answer "right
shape, or `undefined`". Module 14 needs them to say *what* was wrong instead, so
their return types change again — to a list of field errors, or to module 15's
union early. Every `{"error":"invalid_body"}` becomes this shape. The empty title
is the one value rule the project has promised; decide the others (a maximum
length?) before starting. `updateTodo` already builds before it stores, so a
patch whose *result* is invalid can be refused with the store untouched — module
11 set that up for this module.

**15. One error shape, everywhere** ⬜ · a discriminated union, one place that
renders it
*The natural home for the track's second union*, and the module that makes
modules 9-12 shorter in retrospect. Consider having the learner refactor an
earlier handler as the build.

**16. The error boundary** ⬜ · `try`/`catch`, `headersSent`, no leaked traces
*Note:* the given replayer has always had this boundary in it (that is where its
500 comes from). This module is where the learner reads the code that has been
quietly protecting them since module 4 — a nice payoff if the step names it.
*It also owns `not json`:* the first module with `catch` is the only one that can
turn `JSON.parse`'s throw into a 400. Modules 9, 11 and 13 all promise that it
does.

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
| **C** ✅ | 4-7 | Phase 2 — first server, deliberate responses, routing |
| **D** ✅ | 8-12 | Phase 3 — CRUD, one verb per module |
| **E** 🚧 | 13 ✅ · **14-16** ← next | Phase 4 — the trust story |
| **F** | 17-20 | Phase 5 — polish, persistence, structure |

**Module 14 is the one to think about next**: the error *shape* it introduces is
contract, and module 15 is supposed to turn it into one union for every error the
API has. Decide the field-error shape with 15 in mind, or 15 rewrites 14.

### What phase 3 established that batch E can rely on

* **The id is parsed once**, at the top of the handler: `const id =
  todoId(url.pathname)`. Every `:id` route is `if (verb && id !== undefined)`.
* **Two response helpers**: `send(res, status, data: object)` and
  `sendEmpty(res, status)`. Module 15's "one error shape" sits on `send`.
* **Every write route is lookup → read → parse → build → store → answer**, and
  `updateTodo` already separates *build* from *store*. Module 14's validator goes
  between them and never touches the store on a 400.
* **`changesFrom(data: any)` and the create route's `data.title` are the only two
  places parsed input is read.** Module 13 has exactly two sites to close.
* **Ids are never reused** and positions are always found by looking —
  `indexOf` or `findIndex` — never by arithmetic on an id.
* **`/todos/abc` is a 404.** If module 14 wants to revisit that as a 400, it is
  the one module that could justify it; otherwise leave it.

### What phase 2 established that batch D can rely on

* **`send(res, status, data: object)`** is the only way a response leaves the
  application. A new response shape is a call, never a `writeHead` pair.
* **The router is flat** — `if (verb && path) { send(…); return; }` repeated,
  with an unconditional 404 as the last statement. Adding a verb is adding one
  `if` above that line, and modules 9-12 are each expected to be exactly that
  plus their own logic.
* **`url.pathname`** is what routes match on, so a query string never breaks a
  route and module 17 is additive.
* **The seeded `addTodo` calls come out in module 9**, when a client can create
  its own todos. That is the first thing module 9 should do.

### What modules 8 and 9 add to that list, for modules 10-12

* **`readBody(req)` never changes again.** Module 9 parses what it returns, 11
  applies it, 13 stops trusting it, 14 validates it. None of them touch the
  function. Copy it in verbatim as given code above the handler.
* **The handler is `async` and returns `Promise<void>` from here on.** The given
  replayer's `Promise.resolve(handler(req, res)).catch(…)` — written in module 4
  — accepts both shapes, so nothing about the harness changed and nothing about
  it needs to.
* **The read goes inside the route that needs it**, never at the top of the
  handler. Module 8 argues this explicitly, and 17 (query parsing) and 19 (disk
  reads) inherit the argument rather than re-making it.
* **`/echo` is deleted in module 9.** It existed in exactly one module, and
  module 9 declares its retirement in the contract data.
* **The write route is four lines and the order is forced:** `await readBody`,
  `JSON.parse`, store, `send`. Modules 11 and 14 are these four lines with
  something inserted between two of them — a lookup, a validator — never a
  different shape.
* **`JSON.parse` returns `any` and modules 9-12 knowingly trust it.** Every one
  of them should say so where it matters rather than quietly working around it;
  module 13 is only a good module if the reader arrives already uncomfortable.
* **The store's `addTodo(title)` signature is load-bearing.** It is why no route
  needs a check for a client-supplied id. Module 11 wants the same property for
  the fields a `PATCH` may change.

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

### Three traps worth knowing

**1. `_lint_scope` scans program text, not code** — comments and strings
included. So a module numbered below 11 may not contain a literal `...` anywhere
in a program, even in prose inside a comment. Modules 1-3 use the Unicode
ellipsis `…` in their teaching text for exactly this reason. The same applies to
`unknown` and `typeof` (module 13) — say "a path nothing handles", not "an
unknown path", in a program comment.

**2. A blank must be unique in the whole program, and the program includes the
replayer.** The driver contains `res.writeHead(500, { "Content-Type":
"application/json" })`, `??`, `.split(`, `.slice(` and `await`, so a blank of
`{ "Content-Type": "application/json" }` matches twice and `_pmk` refuses it.
Widen the blank until it is unique — module 5 blanks `404, { "Content-Type":
… }` for this reason.

**3. A graded `fix` needs a bug that an ordinary request can expose.** The
replayer only ever sends valid request lines *and* only ever sends small ones,
and both halves of that bite:

* **Malformed input is unreachable.** `??` versus `||` on `req.url`, a key
  dropped because `req.method` was `undefined` — the starter *passes*, and
  `verify_projects.py --starters` rejects it. Two of module 6's exercises were
  rewritten for this.
* **Large input is unreachable.** A 20-byte body arrives in one chunk, so
  `body = chunk`, a `resolve` in the `"data"` listener and an answer built from
  the first chunk all behave identically to the correct code. Module 8 hit this
  with three separate bugs and graded none of them.
* **Headers are unreachable.** The replayer prints the status and the body, and
  Node itself discards a body sent with a 204 — so `send(res, 204, …)` is
  indistinguishable from `sendEmpty(res, 204)`. Module 12 teaches it with
  `curl -i` instead.

Teach those lessons in prose, pitfalls and quizzes; grade something that fails on
ordinary input. When the lesson genuinely needs a big or broken request, the
`manual_test` block is where it goes — module 8's posts 200 KB and watches the
accumulation bug finally appear.

Related: a bug whose symptom is a **hang** (a route with no `res.end`, a handler
with no fall-through) does fail the starter check, but only by timing out — 25 s
in the Python verifier plus 30 s in the Rust one, every run, forever. Module 7
declined to buy that lesson twice; module 4 already grades it cheaply.

---

## What "done" looks like

One project · 20 modules · 5 phases · roughly 170 judged exercises · a Todo API
that validates, paginates and persists · and a learner who was never once asked
to write a line of TypeScript the track had not already taught them.

At 13 of 20 the run rate is **9.5 exercises per module** (124 so far) — call the
finished project 190. Seven modules remain, and one decision: module 14's error
shape, which module 15 inherits.

## The second project

It landed early — see [`CALC_ROADMAP.md`](CALC_ROADMAP.md). **Calc**, an
expression language: scanner, parser, evaluator, error messages. Modules 1-4
ship — phase 1 is complete — and 5-18 are planned.

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
