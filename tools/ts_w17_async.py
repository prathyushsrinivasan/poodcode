# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 17 — async & promises.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ===========================================================================
# THE DETERMINISM RULE FOR THIS WEEK — read before adding an exercise.
# ===========================================================================
#
# Every exercise is graded by exact stdout comparison, and this is the one week
# where "run it again, get a different answer" is the whole subject. So the same
# discipline the Java course applies to threads (java_m30_sync.py) applies here:
# **output is deterministic by construction, never by luck.** Concretely:
#
#   1. ORDER COMES FROM THE PROGRAM, NOT FROM THE SCHEDULER. Either await in a
#      fixed order, or collect results and print them by index. `Promise.all`
#      and `Promise.allSettled` both resolve to results in ARGUMENT order
#      however the work actually finished — that is a specified guarantee, and
#      lesson 6 is built on proving it.
#
#   2. NOTHING PRINTS ELAPSED TIME. Not once. A duration is the one thing here
#      that genuinely varies per machine.
#
#   3. A RACE MUST HAVE AN UNAMBIGUOUS WINNER. Two legitimate ways:
#        - a microtask against a timer — an already-resolved promise always
#          beats any `setTimeout`, because the microtask queue drains before
#          the first timer callback runs (lesson 4);
#        - two timers with delays FAR apart (1 ms vs 40 ms). Timer callbacks fire
#          in expiry order even on a loaded machine, so this is safe — but the
#          margin has to be wide enough that nobody has to think about it.
#      Two timers with the same delay, or a "slow" computation against a timer,
#      are both banned: the first is insertion order pretending to be timing,
#      the second is a coin toss.
#
#   4. RETRIES AND FAILURES ARE DRIVEN BY A COUNTER, NEVER BY TIMING. `flaky()`
#      fails on attempts 1 and 2 and succeeds on 3 because it counts, so the
#      transcript is identical on every machine.
#
#   5. DELAYS STAY TINY (1-60 ms). The judge allows about six seconds per case.
#      A delay exists to make something finish out of order, not to simulate a
#      network.
#
# Every program in this file was run four times before it shipped, and the
# stdout compared across runs; anything that varied was redesigned rather than
# loosened. Two exercises deliberately ship a program whose output is *stable
# but wrong* — `w17-order` fix1 prints in completion order and `w17-seqpar`
# fix1 prints before the work finishes — because a `fix` needs a starter that
# fails the same way every time.
#
# ---------------------------------------------------------------------------
# WHAT THE ENVIRONMENT ACTUALLY PROVIDES (all verified against the real judge)
#
#   setTimeout / clearTimeout / queueMicrotask   declared in poodcode-env.d.ts
#   Promise, .all/.allSettled/.race/.any         lib.es2024
#   Promise.withResolvers                        lib.es2024
#   Awaited<T>                                   lib.es2024, gated at 17
#   TOP-LEVEL AWAIT                              works, with or without an import
#
# There is no `process`, no `Date`-based pacing in any shipped program, and no
# way to do real I/O — which is exactly right: this week is about the *shape* of
# asynchronous code, and a `delay()` built on `setTimeout` is a truer stand-in
# for a slow call than anything the judge could actually wait on.
#
# ---------------------------------------------------------------------------
# ONE SHARP EDGE, FOUND BY THE VERIFIER AND WORTH KEEPING WRITTEN DOWN.
#
# Node decides whether a file is an ES module by scanning it for module syntax —
# an `import`, an `export`, or a top-level `await`. That scan does **not** see an
# `await` that appears only inside a template expression:
#
#     console.log(`total ${await total(3)}`);     // the file's ONLY await
#
# Node parses the file as CommonJS, where top-level await is illegal, and reports
# `SyntaxError: Missing } in template expression` — which says nothing at all
# about the real problem. The type-checker is happy throughout, because
# `moduleDetection: Force` makes it treat every file as a module.
#
# Two exercises here interpolate an awaited value and nothing else, so both carry
# an explicit `export {};` — week 16's marker, doing exactly the job week 16 said
# it does. Any exercise added later whose only top-level await sits inside a
# template literal needs the same line.
# ---------------------------------------------------------------------------
#
# One runtime fact worth knowing, because two exercises depend on it: an
# unhandled rejection **kills the process** (Node's default is
# `--unhandled-rejections=throw`). A floating promise is therefore not a style
# problem here, it is a crash — which makes it a far better lesson than a lint
# rule ever is.
# ---------------------------------------------------------------------------

# The helper used by most of the week. Written out per exercise rather than
# hoisted into a prefix, because the learner has to be able to read it: a promise
# that resolves when a timer fires is the smallest complete picture of what a
# promise IS, and hiding it in scaffolding would waste it.
_DELAY = (
    'function delay(ms: number): Promise<void> {\n'
    '  return new Promise((resolve) => {\n'
    '    setTimeout(resolve, ms);\n  });\n}\n'
)

# `after(ms, value)` — the same idea with a value attached. Note the arrow inside
# `setTimeout`: for a `Promise<void>` you can pass `resolve` straight to
# setTimeout (its value parameter is optional), but for a `Promise<T>` you cannot,
# because `resolve` then requires an argument.
_AFTER = (
    'function after<T>(ms: number, value: T): Promise<T> {\n'
    '  return new Promise((resolve) => {\n'
    '    setTimeout(() => resolve(value), ms);\n  });\n}\n'
)

# --- Week 17 --------------------------------------------------------------
_WEEKS.append(_week(
    17, 5, _M5,
    "Async & Promises",
    "Write code that waits: promises, async/await, error handling that survives a rejection, and the difference between doing three things in a row and doing three things at once.",
    """
Every program you have written so far ran top to bottom and finished. Real
programs wait — for a file, a database, an HTTP response, a user. This week is
about what "waiting" means when there is only one thread to do it on.

## The one fact everything follows from

JavaScript runs your code on **one thread**. It cannot block that thread to wait
for something, because blocking it stops everything — so instead, slow work is
started, your function returns, and a **callback** runs later with the result.

That "later" is what a promise describes, and what `await` lets you write as if
it were not there:

```ts
const text = await load("ledger.json");   // reads as if it blocked
console.log(text.length);                  // …but the thread was free the whole time
```

## Three things that are easy to get wrong

* **Forgetting to wait.** `total(3)` where `total` is `async` gives you a
  *promise*, not a number, and `${total(3)}` prints `[object Promise]` without a
  single complaint from the compiler.
* **Doing it in a row when you meant at once.** Three awaits in a loop take as
  long as all three added up. `Promise.all` takes as long as the slowest one.
* **Losing an error.** A rejected promise that nobody is waiting on does not
  print a warning here — it **kills the process**.

## A note on how this week is graded

Output is compared exactly, so every program in this week is built to produce the
**same output on every machine**: results are printed in a fixed order, no program
ever prints how long anything took, and where two things race, one of them wins by
a mile and lesson 4 explains why. That is not a testing trick — it is how
asynchronous code is written when you want to be able to reason about it, and the
discipline is worth more than the syntax.

⏱️ Budget about **nine hours**.
""",
    objectives=[
        "Explain why a single-threaded runtime cannot block, and what it does instead",
        "Describe a promise's three states and what settles it",
        "Build a promise with `new Promise` and resolve it from a callback",
        "Chain with `.then`, and say what the chain's value is at each step",
        "Rewrite a `.then` chain as `async`/`await` and say what `await` unwraps",
        "Say what an `async` function returns, whatever its `return` statement says",
        "Order sync code, microtasks and timers correctly, and say why that order is guaranteed",
        "Catch a rejection with `try`/`catch`, and narrow the `unknown` it gives you",
        "Say what happens to a rejection nobody awaits",
        "Choose between sequential awaits and `Promise.all`, and say what each costs",
        "Pick between `all`, `allSettled`, `race` and `any` from the failure behaviour you need",
        "Type an async function, and use `Awaited<T>` to talk about what a promise yields",
        "Write a retry, a timeout and a sequential pipeline",
    ],
    why="Asynchrony is where most production bugs live. Not because promises are hard, but because the order things happen in stops being the order they are written in, and every assumption you did not know you had made shows up at once. Interviews probe this constantly — 'what does this print?' is nearly always an event-loop question — and the answer is a model you can carry, not a rule you memorised.",
    est_minutes=540,
    glossary=[
        _gloss("single-threaded", "One call stack. Your code never runs in two places at once, so it must never block."),
        _gloss("callback", "A function handed to something slow, called later with the result."),
        _gloss("promise", "An object representing a value that is not here yet. Has three states and settles once."),
        _gloss("pending", "Not settled yet."),
        _gloss("fulfilled", "Settled with a value."),
        _gloss("rejected", "Settled with a reason — by convention an Error."),
        _gloss("settled", "Fulfilled or rejected. A promise settles at most once; later calls do nothing."),
        _gloss("executor", "The `(resolve, reject) => …` function you pass to `new Promise`. It runs immediately."),
        _gloss(".then", "Registers a callback for fulfilment and returns a NEW promise of the callback's result."),
        _gloss(".catch", "`.then(undefined, fn)` — a handler for the rejection branch."),
        _gloss(".finally", "Runs on either outcome, and passes the outcome through unchanged."),
        _gloss("async function", "A function that always returns a promise, whatever its return statement says."),
        _gloss("await", "Suspends the async function until the promise settles, then yields the value — or throws the reason."),
        _gloss("top-level await", "`await` outside any function, legal in a module."),
        _gloss("Promise<T>", "The type of a promise yielding T. An async function returning T is typed Promise<T>."),
        _gloss("Awaited<T>", "What you get after awaiting T — recursively, so Awaited<Promise<Promise<X>>> is X."),
        _gloss("microtask", "A promise continuation. The whole microtask queue drains before the next timer."),
        _gloss("macrotask", "A timer or I/O callback. One per event-loop turn, after the microtasks."),
        _gloss("event loop", "Run the sync code, drain the microtasks, take one macrotask, repeat."),
        _gloss("Promise.all", "Fails fast; on success yields results in ARGUMENT order, not completion order."),
        _gloss("Promise.allSettled", "Never rejects; yields one {status, value|reason} per input, in argument order."),
        _gloss("Promise.race", "Settles as the first input settles — including a rejection."),
        _gloss("Promise.any", "The first FULFILMENT; rejects with an AggregateError only if all of them reject."),
        _gloss("Promise.withResolvers", "Returns { promise, resolve, reject } so you can settle it from elsewhere."),
        _gloss("floating promise", "A promise nobody awaits. If it rejects, the process dies."),
        _gloss("fail fast", "Reject as soon as one input rejects (what `all` does)."),
        _gloss("sequential", "Each await waits for the previous. Total time is the sum."),
        _gloss("concurrent", "All started, then awaited together. Total time is the slowest."),
    ],
    cheatsheet="""
```ts
// ---- a promise, built by hand -------------------------------------------
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {        // the executor runs IMMEDIATELY
    setTimeout(resolve, ms);               // …and settles it later
  });
}
function after<T>(ms: number, value: T): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(value), ms);  // a Promise<T>'s resolve NEEDS the value
  });
}

// ---- chain, or await ----------------------------------------------------
Promise.resolve(2).then((v) => v * 2).then((v) => console.log(v));   // 4
const v = await after(1, 2);                                          // 2

// ---- async functions ----------------------------------------------------
async function total(n: number): Promise<number> { return n * 2; }   // NOT `: number`
console.log(await total(3));      // 6
console.log(`${total(3)}`);       // [object Promise]  ← the missing-await bug

// ---- the order, and it is guaranteed -----------------------------------
console.log("1 sync");
setTimeout(() => console.log("4 timer"), 0);      // macrotask: last
Promise.resolve().then(() => console.log("3 microtask"));
console.log("2 sync");
// sync code first, then EVERY microtask, then the first timer.

// ---- errors -------------------------------------------------------------
try {
  await mightReject();
} catch (err) {                    // unknown, exactly as in week 15
  console.log(err instanceof Error ? err.message : String(err));
} finally { /* always */ }

return mightReject();              // ❌ inside a try: not awaited, so not caught
return await mightReject();        // ✅

boom();                            // ❌ floating: an unhandled rejection kills the process

// ---- in a row, or at once ----------------------------------------------
for (const id of ids) { out.push(await load(id)); }        // sequential: sum of times
const out = await Promise.all(ids.map(load));              // concurrent: slowest time
[1, 2].forEach(async (n) => { out.push(await load(n)); }); // ❌ forEach does not wait

// ---- the four combinators ----------------------------------------------
await Promise.all([a, b]);         // [A, B] in ARGUMENT order; throws on first reject
await Promise.allSettled([a, b]);  // [{status:"fulfilled",value}|{status:"rejected",reason}]
await Promise.race([work, after(50, "timed out")]);        // first to SETTLE
await Promise.any([a, b]);         // first to FULFIL

const r = (await Promise.allSettled([a]))[0];
if (r !== undefined && r.status === "fulfilled") { r.value; }   // narrow before .value

// ---- typing -------------------------------------------------------------
type Yielded = Awaited<Promise<Promise<string>>>;     // string
async function first<T>(xs: readonly Promise<T>[]): Promise<T | undefined> { … }
```
""",
    self_check=[
        "Can you say why a single-threaded runtime must not block, and what it does instead?",
        "Can you name a promise's three states, and say how many times one may settle?",
        "Can you write `delay(ms)` from memory?",
        "Can you say what `.then` returns, and why that makes chaining work?",
        "Can you say what an `async` function returns when its body says `return 2`?",
        "Can you order sync code, a `Promise.resolve().then` and a `setTimeout(…, 0)` — and justify it?",
        "Can you say what type `catch (err)` gives you, and how to get a message out of it?",
        "Can you say what happens to a rejected promise nobody awaits?",
        "Can you say why `return p` inside a `try` is not protected by its `catch`?",
        "Can you say which of a loop of awaits and `Promise.all` takes longer, and why?",
        "Can you say what order `Promise.all`'s results come back in?",
        "Can you pick between `all`, `allSettled`, `race` and `any` for 'load five pages, report the ones that failed'?",
        "Can you say why `forEach` with an async callback does not wait?",
        "Can you write a retry that gives up after three attempts?",
    ],
    review=[
        _q("JavaScript runs your code on…",
           ["one thread per promise", "one thread", "a thread pool", "two threads"], 1,
           "Which is why nothing may block it."),
        _q("A promise may settle…",
           ["any number of times", "at most once", "twice", "only on success"], 1,
           "Later resolve/reject calls do nothing."),
        _q("The executor passed to `new Promise` runs…",
           ["later", "immediately, synchronously", "on await", "never"], 1,
           "Only the settling is deferred."),
        _q("`.then((v) => v * 2)` returns…",
           ["the number", "a new promise of the callback's result", "void", "the same promise"], 1,
           "Which is what makes a chain a chain."),
        _q("`async function f(): Promise<number> { return 2; }` — what does `f()` give you?",
           ["2", "a promise that fulfils with 2", "void", "an error"], 1,
           "An async function always returns a promise."),
        _q("`async function f(): number` is…",
           ["fine", "TS1064 — the return type must be Promise<T>", "implicit any", "void"], 1,
           "The compiler is explicit about it."),
        _q("`await` in a non-async, non-module-top-level position is…",
           ["allowed", "TS1308", "ignored", "a promise"], 1,
           "Only async functions and module top level."),
        _q("Given sync code, a `.then` and a `setTimeout(…, 0)`, the order is…",
           ["timer, microtask, sync", "sync, microtask, timer", "sync, timer, microtask",
            "undefined"], 1,
           "The microtask queue drains completely before the first timer."),
        _q("`console.log(`${total(3)}`)` where total is async prints…",
           ["6", "[object Promise]", "undefined", "a type error"], 1,
           "And the compiler says nothing, because a promise is a perfectly good template value."),
        _q("`catch (err)` types err as…",
           ["Error", "unknown", "any", "never"], 1,
           "Week 15's rule, unchanged by asynchrony."),
        _q("`return mightReject();` inside a `try` is…",
           ["caught by its catch", "NOT caught — the promise leaves the try before it settles",
            "a syntax error", "the same as return await"], 1,
           "`return await` is the version that is protected."),
        _q("A rejected promise nobody awaits…",
           ["is ignored", "kills the process on Node's default setting", "logs a warning only",
            "resolves"], 1,
           "Which makes a floating promise a crash, not a style issue."),
        _q("Three awaits in a loop take…",
           ["the slowest one's time", "the sum of all three", "no time", "twice the slowest"], 1,
           "That is what sequential means."),
        _q("`Promise.all`'s results come back in…",
           ["completion order", "argument order, whatever finished first", "random order",
            "reverse order"], 1,
           "A specified guarantee, and the basis of every deterministic concurrent program."),
        _q("`Promise.all` rejects…",
           ["never", "as soon as any input rejects", "when all reject", "after all settle"], 1,
           "Fail fast."),
        _q("To load five pages and report which failed, reach for…",
           ["all", "allSettled", "race", "any"], 1,
           "It never rejects and reports every outcome."),
        _q("`Promise.race` settles when…",
           ["the first input fulfils", "the first input SETTLES — a rejection can win",
            "all settle", "the last settles"], 1,
           "`any` is the one that ignores rejections."),
        _q("`[1, 2].forEach(async (n) => { … })`…",
           ["waits for each", "does not wait at all — forEach ignores the returned promises",
            "runs them in order", "is a type error"], 1,
           "Use `for … of` with await, or Promise.all."),
        _q("`Awaited<Promise<Promise<string>>>` is…",
           ["Promise<string>", "string", "unknown", "never"], 1,
           "It unwraps recursively."),
        _q("A deterministic retry is driven by…",
           ["a timer", "a counter", "the load average", "chance"], 1,
           "Which is why this week's retries count attempts."),
    ],
    milestone="Budget Buddy can load a ledger that arrives in pages, one slow request each, all of them in flight at once. Two pages fail; the report names them, totals the three that worked, and prints everything in page order — the same output on every machine, even though the pages finish in a different order every time.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w17-why", "One thread, and what it cannot do",
            "Why asynchronous code exists at all.",
            """
There is **one** call stack. Your code never runs in two places at once.

That has one enormous consequence: nothing may **block**. A function that waited
half a second for a file would freeze the entire program for half a second —
every other piece of work, every timer, every response.

So instead of waiting, JavaScript **schedules**:

```ts
console.log("start");
setTimeout(() => {
  console.log("later");
}, 0);
console.log("end");
```

```
start
end
later
```

Even at `0` milliseconds, `later` comes last. `setTimeout` does not pause
anything — it hands a function to the runtime and returns immediately. The
callback runs when the current work is **completely finished**.

## The proof that it runs afterwards

```ts
let stage = "scheduled";
setTimeout(() => {
  console.log(`timer saw: ${stage}`);
}, 0);
stage = "synchronous work finished";
console.log("main done");
```

```
main done
timer saw: synchronous work finished
```

The callback was created before the assignment and still sees the *new* value,
because it did not run until the synchronous code had finished. This is the whole
model in five lines.

## Why callbacks alone are not enough

A callback cannot give a value **back** to the function that scheduled it:

```ts
function fetchLater(): string {
  setTimeout(() => {
    return "done";        // returns from the CALLBACK, to nobody
  }, 0);
}                          // ❌ TS2355: A function whose declared type is neither
                           //    'undefined', 'void', nor 'any' must return a value.
```

There is nothing to return, because the value does not exist yet when
`fetchLater` returns. The classic answer was to take a callback yourself —

```ts
function fetchLater(done: (value: string) => void): void {
  setTimeout(() => { done("done"); }, 0);
}
```

— and that works, right up until you need two of them in sequence, then error
handling, then three in parallel. That pile of nested callbacks is what promises
were invented to replace, and lesson 2 is the replacement.

> ⚠️ **Common mistakes:** expecting `setTimeout(…, 0)` to run immediately;
> returning a value from inside a callback; and reading a variable the callback
> will fill in, before it has.
""",
            warmup=[
                _q("`setTimeout(f, 0)` runs f…",
                   ["immediately", "after the current synchronous code finishes", "never",
                    "on the next line"], 1,
                   "Zero is a minimum, not a promise."),
                _q("A callback scheduled before an assignment sees…",
                   ["the old value", "the new value — it runs later", "undefined", "either"], 1,
                   "Which is the proof it ran afterwards."),
                _q("Why can a function not return the value its callback receives?",
                   ["scoping", "the value does not exist yet when the function returns",
                    "types", "it can"], 1,
                   "The reason promises exist."),
                _q("Blocking the thread to wait would…",
                   ["be efficient", "freeze every other piece of work", "be fine", "be faster"], 1,
                   "One thread, one stack."),
            ],
            exercises=[
                _ex("tscourse-w17-why-1", "Later means later",
                    "Schedule the middle line so the output reads start, end, later.",
                    'console.log("start");\n'
                    'setTimeout(() => {\n'
                    '  console.log("later");\n'
                    '}, 0);\n'
                    'console.log("end");\n',
                    'setTimeout(() => {', [("", "start\nend\nlater")],
                    hints=["The callback goes to the runtime; the two logs around it are synchronous.",
                           "Write setTimeout(() => {"]),
                _ex("tscourse-w17-why-2", "What the callback sees",
                    "Assign the new stage after scheduling, and watch the callback report it.",
                    'let stage = "scheduled";\n'
                    'setTimeout(() => {\n'
                    '  console.log(`timer saw: ${stage}`);\n'
                    '}, 0);\n'
                    'stage = "synchronous work finished";\n'
                    'console.log("main done");\n',
                    'stage = "synchronous work finished";',
                    [("", "main done\ntimer saw: synchronous work finished")],
                    hints=["The callback reads the variable when it RUNS, not when it was created.",
                           'Write stage = "synchronous work finished";'],
                    difficulty="Easy"),
                _ex("tscourse-w17-why-3", "Hand the value to a callback",
                    "Since the function cannot return the value, let the caller supply somewhere to put it.",
                    'function fetchLater(done: (value: string) => void): void {\n'
                    '  setTimeout(() => {\n'
                    '    done("done");\n  }, 0);\n}\n'
                    'fetchLater((value) => {\n'
                    '  console.log(`got ${value}`);\n});\n'
                    'console.log("asked");\n',
                    'function fetchLater(done: (value: string) => void): void {',
                    [("", "asked\ngot done")],
                    hints=["The parameter is a function taking the value and returning nothing.",
                           "Write function fetchLater(done: (value: string) => void): void {"],
                    difficulty="Medium"),
                _ex("tscourse-w17-why-4", "Two in a row, the old way",
                    "Nest the second step inside the first's callback, which is how sequencing was done before promises.",
                    'function step(name: string, done: () => void): void {\n'
                    '  setTimeout(() => {\n'
                    '    console.log(name);\n    done();\n  }, 0);\n}\n'
                    'step("first", () => {\n'
                    '  step("second", () => {\n'
                    '    console.log("both done");\n  });\n});\n',
                    '  step("second", () => {', [("", "first\nsecond\nboth done")],
                    hints=["The second step can only start once the first has called back.",
                           'Write step("second", () => {'],
                    difficulty="Medium"),
                _diagnose("tscourse-w17-why-d1", "The return that goes nowhere",
                          "TS2355: A function whose declared type is neither 'undefined', 'void', nor 'any' must return a value.",
                          'function fetchLater(): string {\n'
                          '  setTimeout(() => {\n'
                          '    return "done";\n  }, 0);\n}\n'
                          'console.log(fetchLater());\n',
                          'function fetchLater(done: (value: string) => void): void {\n'
                          '  setTimeout(() => {\n'
                          '    done("done");\n  }, 0);\n}\n'
                          'fetchLater((value) => {\n'
                          '  console.log(value);\n});\n',
                          [("", "done")],
                          hints=["The `return` inside the callback returns from the CALLBACK, so the outer function returns nothing.",
                                 "The value cannot be returned at all — it does not exist yet.",
                                 "Take a callback parameter and hand the value to it instead."],
                          difficulty="Medium"),
                _fix("tscourse-w17-why-fix1", "Fix the read that was too early",
                     "This prints an empty line: `result` is read on the line after the timer is *scheduled*, long before the callback fills it in. Print it where it is known.",
                     'let result = "";\n'
                     'setTimeout(() => {\n'
                     '  result = "loaded";\n'
                     '}, 0);\n'
                     'console.log(result);\n',
                     'let result = "";\n'
                     'setTimeout(() => {\n'
                     '  result = "loaded";\n'
                     '  console.log(result);\n'
                     '}, 0);\n',
                     [("", "loaded")],
                     hints=["Nothing between the scheduling and the log gave the callback a chance to run.",
                            "The only place the value is certainly there is inside the callback.",
                            "Move the console.log into the callback, after the assignment."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Nested callbacks became unmanageable mainly because of…",
                   ["performance", "sequencing plus error handling plus parallelism, all by hand",
                    "syntax", "types"], 1,
                   "Promises replace exactly that."),
                _q("`setTimeout` returns…",
                   ["the callback's value", "a handle, immediately", "a promise", "void"], 1,
                   "It never waits."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w17-promise", "A value that has not arrived",
            "Three states, one settlement, and a chain.",
            """
A **promise** is an object standing in for a value that is not here yet. It has
three states and settles **once**:

```
pending ──► fulfilled (with a value)
        └─► rejected  (with a reason)
```

## Building one

```ts
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}
```

The function you pass to `new Promise` is the **executor**, and it runs
**immediately and synchronously** — only the `resolve` call is deferred. Two
details worth having straight:

* For a `Promise<void>` you can hand `resolve` straight to `setTimeout`. For a
  `Promise<T>` you cannot, because `resolve` then needs the value:

```ts
function after<T>(ms: number, value: T): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(value), ms);
  });
}
```

* Calling `resolve` twice does nothing the second time. A settled promise is
  settled.

## Ready-made ones

```ts
Promise.resolve(2);                       // already fulfilled with 2
Promise.reject(new Error("no"));          // already rejected
```

## `.then` returns a new promise

This is the part that makes chains work:

```ts
Promise.resolve(2)
  .then((v) => v * 2)        // Promise<number>, fulfilling with 4
  .then((v) => `= ${v}`)     // Promise<string>, fulfilling with "= 4"
  .then((v) => { console.log(v); });
```

Each `.then` hands its callback's **return value** to the next one. If the
callback returns a promise, it is flattened — you never get a
`Promise<Promise<T>>`, which is why `await` in lesson 3 only ever needs to unwrap
one layer.

And if a callback returns nothing, the next step receives `undefined`. That is
the single most common promise bug, and it is this lesson's `fix`.

## The rejection branch

```ts
Promise.reject(new Error("no"))
  .catch((err: unknown) => {
    console.log(err instanceof Error ? err.message : "?");
  });
```

`.catch(fn)` is `.then(undefined, fn)`. `.finally(fn)` runs on either outcome and
passes the outcome through unchanged.

## Typing

A function returning a promise is typed `Promise<T>` where `T` is what it
eventually yields:

```ts
function loadName(): Promise<string> { … }
```

There is no `Promise` without a type argument worth writing — `Promise<void>` is
what you want for "it finished, there is no value".

> ⚠️ **Common mistakes:** expecting the executor to run later; forgetting to
> `return` inside a `.then`; and using a promise as though it were the value it
> will produce.
""",
            warmup=[
                _q("A promise's three states are…",
                   ["new, running, done", "pending, fulfilled, rejected", "open, closed, failed",
                    "start, wait, end"], 1,
                   "And it settles at most once."),
                _q("The executor passed to `new Promise` runs…",
                   ["when awaited", "immediately", "after a tick", "never"], 1,
                   "Only the settling is deferred."),
                _q("`.then((v) => v * 2)` evaluates to…",
                   ["a number", "a new promise of the callback's result", "void", "the input promise"], 1,
                   "Chains are made of new promises."),
                _q("A `.then` callback that returns nothing hands the next step…",
                   ["the previous value", "undefined", "a promise", "an error"], 1,
                   "The classic missing-return bug."),
            ],
            exercises=[
                _ex("tscourse-w17-pr-1", "Build a delay",
                    "Wrap `setTimeout` in a promise that fulfils when the timer fires.",
                    _DELAY +
                    'delay(1).then(() => {\n'
                    '  console.log("done waiting");\n});\n'
                    'console.log("waiting");\n',
                    '  return new Promise((resolve) => {',
                    [("", "waiting\ndone waiting")],
                    hints=["The executor receives `resolve`; hand it to setTimeout.",
                           "Write return new Promise((resolve) => {"],
                    difficulty="Medium"),
                _ex("tscourse-w17-pr-2", "A promise with a value",
                    "For a `Promise<T>` the resolve call needs the value, so wrap it in an arrow.",
                    _AFTER +
                    'after(1, "page 1").then((page) => {\n'
                    '  console.log(page);\n});\n',
                    '    setTimeout(() => resolve(value), ms);',
                    [("", "page 1")],
                    hints=["`resolve` cannot be passed bare here — it needs an argument.",
                           "Write setTimeout(() => resolve(value), ms);"],
                    difficulty="Medium"),
                _ex("tscourse-w17-pr-3", "Transform along the chain",
                    "Double the value in the first step, so the second prints `= 4`.",
                    'Promise.resolve(2)\n'
                    '  .then((v) => v * 2)\n'
                    '  .then((v) => {\n'
                    '    console.log(`= ${v}`);\n  });\n',
                    '  .then((v) => v * 2)', [("", "= 4")],
                    hints=["Each step's return value becomes the next step's input.",
                           "Write .then((v) => v * 2)"],
                    difficulty="Easy"),
                _ex("tscourse-w17-pr-4", "Settle once",
                    "Resolve it twice on purpose and watch the second call do nothing.",
                    'const once: Promise<string> = new Promise((resolve) => {\n'
                    '  resolve("first");\n'
                    '  resolve("second");\n});\n'
                    'once.then((v) => {\n'
                    '  console.log(v);\n});\n',
                    '  resolve("second");', [("", "first")],
                    hints=["A settled promise is settled; the second call is simply ignored.",
                           'Write resolve("second");'],
                    difficulty="Easy"),
                _ex("tscourse-w17-pr-5", "Handle the rejection branch",
                    "Catch the rejection and print its message, narrowing the `unknown` reason first.",
                    'Promise.reject(new Error("page missing"))\n'
                    '  .catch((err: unknown) => {\n'
                    '    console.log(err instanceof Error ? err.message : "?");\n  });\n',
                    '  .catch((err: unknown) => {', [("", "page missing")],
                    hints=["`.catch` takes the rejection reason, which is `unknown` — week 15's rule.",
                           "Write .catch((err: unknown) => {"],
                    difficulty="Medium"),
                _ex("tscourse-w17-pr-6", "Type the promise",
                    "Give the loader the return type that says what it eventually yields.",
                    _AFTER +
                    'function loadName(): Promise<string> {\n'
                    '  return after(1, "ledger.json");\n}\n'
                    'loadName().then((name) => {\n'
                    '  console.log(name);\n});\n',
                    'function loadName(): Promise<string> {', [("", "ledger.json")],
                    hints=["The generic parameter is what arrives, not the promise itself.",
                           "Write function loadName(): Promise<string> {"],
                    difficulty="Easy"),
                _diagnose("tscourse-w17-pr-d1", "A promise is not its value",
                          "TS2322: Type 'Promise<number>' is not assignable to type 'number'.",
                          'const n: number = Promise.resolve(2).then((v) => v * 2);\n'
                          'console.log(n);\n',
                          'Promise.resolve(2)\n'
                          '  .then((v) => v * 2)\n'
                          '  .then((v) => {\n'
                          '    console.log(v);\n  });\n',
                          [("", "4")],
                          hints=["`.then` gives you a promise, not the number inside it — the value does not exist yet.",
                                 "Everything that needs the value has to happen inside a callback.",
                                 "Add a second `.then` that logs it."],
                          difficulty="Medium"),
                _fix("tscourse-w17-pr-fix1", "Fix the step that forgot to return",
                     "This prints `got undefined`. The first `.then` computes the doubled value and throws it away, so the next step receives nothing.",
                     'Promise.resolve(2)\n'
                     '  .then((v) => {\n'
                     '    v * 2;\n  })\n'
                     '  .then((v) => {\n'
                     '    console.log(`got ${v}`);\n  });\n',
                     'Promise.resolve(2)\n'
                     '  .then((v) => {\n'
                     '    return v * 2;\n  })\n'
                     '  .then((v) => {\n'
                     '    console.log(`got ${v}`);\n  });\n',
                     [("", "got 4")],
                     hints=["A block-bodied arrow returns `undefined` unless you say otherwise.",
                            "The next step receives whatever the previous callback RETURNED.",
                            "Add the `return`."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("A `.then` callback that returns a promise gives the next step…",
                   ["a Promise<Promise<T>>", "the flattened value", "undefined", "an error"], 1,
                   "Promises never nest, which is why await unwraps one layer."),
                _q("`.finally(fn)`…",
                   ["swallows errors", "runs on either outcome and passes it through unchanged",
                    "only runs on success", "returns void"], 1,
                   "For cleanup."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w17-await", "`async` and `await`",
            "The same promises, written as though they were not there.",
            """
`await` suspends the function until a promise settles, then gives you the value:

```ts
const page = await after(1, "page 1");
console.log(page);                        // "page 1"
```

Compare it to the chain it replaces:

```ts
after(1, "page 1").then((page) => { console.log(page); });
```

The difference is not brevity, it is that **normal control flow works again** —
`if`, `for`, `try`/`catch`, early `return`. A `.then` chain has to express all of
those as callbacks.

## `async` is a contract about the return type

```ts
async function total(n: number): Promise<number> {
  return n * 2;                  // a plain number…
}
const t = total(3);               // …but `t` is Promise<number>
console.log(await t);             // 6
```

**An `async` function always returns a promise.** Saying `return 2` fulfils the
promise with 2; the annotation must therefore be `Promise<number>`, and writing
`: number` is an error the compiler names precisely:

```
TS1064: The return type of an async function or method must be the global
        Promise<T> type. Did you mean to write 'Promise<number>'?
```

Throwing inside an `async` function rejects its promise instead of propagating a
throw to the caller. That symmetry — `return` ⇒ fulfil, `throw` ⇒ reject — is the
whole of lesson 5.

## Where `await` is allowed

```ts
async function f(): Promise<void> { await g(); }     // ✅ inside async
const v = await g();                                 // ✅ top level of a module
function h(): void { await g(); }                    // ❌ TS1308
```

Every program in this week may use **top-level await**, which is what lets these
exercises read like the inside of an async function without one.

## `await` on something that is not a promise

Perfectly legal, and it still yields to the microtask queue:

```ts
const v = await 3;        // 3, one microtask later
```

Which matters more than it looks: `await` always defers the rest of the function,
even when there was nothing to wait for. Lesson 4 is built on that.

## The missing `await`

The bug this week is famous for:

```ts
console.log(`${total(3)}`);       // [object Promise]
```

No error, no warning — a promise is a perfectly good thing to interpolate into a
string. The compiler cannot help because nothing is wrong *with the types*: you
asked for the text of a promise and you got it.

> ⚠️ **Common mistakes:** annotating an async function's return as `T` instead of
> `Promise<T>`; forgetting `await` and getting `[object Promise]`; and assuming
> `await` on a non-promise is a no-op.
""",
            warmup=[
                _q("`async function f(): Promise<number> { return 2; }` — `f()` is…",
                   ["2", "Promise<number>", "number", "void"], 1,
                   "Always a promise."),
                _q("`async function f(): number` gives…",
                   ["nothing", "TS1064", "a promise anyway", "implicit any"], 1,
                   "The compiler even suggests the fix."),
                _q("`await` in a plain function is…",
                   ["allowed", "TS1308", "a promise", "ignored"], 1,
                   "Async functions and module top level only."),
                _q("`await 3` gives…",
                   ["a promise", "3, one microtask later", "an error", "undefined"], 1,
                   "And still defers the rest of the function."),
            ],
            exercises=[
                _ex("tscourse-w17-aw-1", "Await instead of then",
                    "Replace the chain with a single awaited expression.",
                    _AFTER +
                    'const page = await after(1, "page 1");\n'
                    'console.log(page);\n',
                    'const page = await after(1, "page 1");', [("", "page 1")],
                    hints=["One keyword in front of the call.",
                           'Write const page = await after(1, "page 1");'],
                    difficulty="Easy"),
                _ex("tscourse-w17-aw-2", "Type an async function",
                    "Annotate the return type the way an async function must be annotated.",
                    'async function total(n: number): Promise<number> {\n'
                    '  return n * 2;\n}\n'
                    'console.log(await total(3));\n',
                    'async function total(n: number): Promise<number> {',
                    [("", "6")],
                    hints=["The body returns a number; the function returns a promise of one.",
                           "Write async function total(n: number): Promise<number> {"],
                    difficulty="Easy"),
                _ex("tscourse-w17-aw-3", "Await at the top level",
                    "Read stdin, hand it to the async formatter and await the result.",
                    _FS +
                    'async function shout(text: string): Promise<string> {\n'
                    '  return text.trim().toUpperCase();\n}\n'
                    'const line = fs.readFileSync(0, "utf8");\n'
                    'console.log(await shout(line));\n',
                    'console.log(await shout(line));',
                    [("coffee", "COFFEE"), ("flat white", "FLAT WHITE")],
                    hints=["Top-level await is legal in a module, and these programs are modules.",
                           "Write console.log(await shout(line));"],
                    difficulty="Easy"),
                _ex("tscourse-w17-aw-4", "Normal control flow, restored",
                    "Loop over the ids and await each one — the thing a `.then` chain cannot express directly.",
                    _AFTER +
                    'async function load(id: number): Promise<string> {\n'
                    '  return after(1, `page ${id}`);\n}\n'
                    'for (const id of [1, 2, 3]) {\n'
                    '  console.log(await load(id));\n}\n',
                    '  console.log(await load(id));',
                    [("", "page 1\npage 2\npage 3")],
                    hints=["Inside the loop body, await the call and log what comes back.",
                           "Write console.log(await load(id));"],
                    difficulty="Medium"),
                _ex("tscourse-w17-aw-5", "An async function that yields no value",
                    "Give the logger the return type for 'it finished, there is nothing to hand back'.",
                    _DELAY +
                    'async function announce(name: string): Promise<void> {\n'
                    '  await delay(1);\n'
                    '  console.log(`ready: ${name}`);\n}\n'
                    'await announce("ledger");\n'
                    'console.log("after");\n',
                    'async function announce(name: string): Promise<void> {',
                    [("", "ready: ledger\nafter")],
                    hints=["There is no value, but there is still a promise.",
                           "Write async function announce(name: string): Promise<void> {"],
                    difficulty="Easy"),
                _predict("tscourse-w17-aw-p1", "What an async call gives you",
                         'async function total(n: number): Promise<number> {\n'
                         '  return n * 2;\n}\n'
                         'const pending = total(3);\n',
                         "pending", "Promise<number>",
                         why="The body returns a number; the question is what the CALL evaluates to.",
                         hints=["An async function always returns the same kind of thing.",
                                "Write Promise<number>."]),
                _diagnose("tscourse-w17-aw-d1", "`await` with nowhere to suspend",
                          "TS1308: 'await' expressions are only allowed within async functions and at the top levels of modules.",
                          'function load(): string {\n'
                          '  const v = await Promise.resolve("x");\n'
                          '  return v;\n}\n'
                          'console.log(load());\n',
                          'async function load(): Promise<string> {\n'
                          '  const v = await Promise.resolve("x");\n'
                          '  return v;\n}\n'
                          'console.log(await load());\n',
                          [("", "x")],
                          hints=["Only an async function can be suspended, so only an async function can await.",
                                 "Marking it async also changes what it returns.",
                                 "Make it `async` with `Promise<string>`, and await the call."],
                          difficulty="Medium"),
                _diagnose("tscourse-w17-aw-d2", "The return type an async function cannot have",
                          "TS1064: The return type of an async function or method must be the global Promise<T> type. Did you mean to write 'Promise<number>'?",
                          'async function total(): number {\n'
                          '  return 1;\n}\n'
                          'console.log(await total());\n',
                          'async function total(): Promise<number> {\n'
                          '  return 1;\n}\n'
                          'console.log(await total());\n',
                          [("", "1")],
                          hints=["The body really does return a number — but the function does not.",
                                 "The compiler has written the answer in the message.",
                                 "Write `: Promise<number>`."],
                          difficulty="Easy"),
                # `export {};` is load-bearing, not decoration: once the only top-level
                # await lives inside a template expression, Node's module detection
                # misses it and parses the file as CommonJS. See the file header.
                _fix("tscourse-w17-aw-fix1", "Fix the `[object Promise]`",
                     "This prints `[object Promise]` and the compiler said nothing — a promise is a perfectly good value to interpolate. Wait for it.",
                     'async function total(n: number): Promise<number> {\n'
                     '  return n * 2;\n}\n'
                     'export {};\n'
                     'console.log(`total ${total(3)}`);\n',
                     'async function total(n: number): Promise<number> {\n'
                     '  return n * 2;\n}\n'
                     'export {};\n'
                     'console.log(`total ${await total(3)}`);\n',
                     [("", "total 6")],
                     hints=["Nothing is wrong with the types: you asked for the text of a promise.",
                            "The value is one keyword away.",
                            "Write ${await total(3)}."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("`throw` inside an async function…",
                   ["crashes immediately", "rejects the promise it returned", "returns undefined",
                    "is a type error"], 1,
                   "return ⇒ fulfil, throw ⇒ reject."),
                _q("The real argument for `await` over `.then` is…",
                   ["it is shorter", "if/for/try/return all work again", "it is faster",
                    "it is typed"], 1,
                   "Control flow, not brevity."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w17-order", "The order things run in",
            "Sync code, then every microtask, then one timer. Guaranteed.",
            """
This is the lesson interviews are really asking about, and it is three rules.

## The event loop, in three rules

1. Run the current synchronous code **to completion**. Nothing interrupts it.
2. Drain the **microtask** queue — every promise continuation, including ones
   added while draining.
3. Take **one** macrotask (a timer, an I/O callback). Then go back to rule 2.

```ts
console.log("1 sync");
setTimeout(() => {
  console.log("4 timer");
}, 0);
Promise.resolve().then(() => {
  console.log("3 microtask");
});
console.log("2 sync");
```

```
1 sync
2 sync
3 microtask
4 timer
```

The microtask beats the `0` ms timer **every time**. It is not a race and it does
not depend on the machine: microtasks are drained before the next macrotask is
taken, full stop.

## `await` is a microtask boundary

Everything after an `await` is a continuation, which is why two async functions
started together interleave in a completely predictable way:

```ts
async function a(): Promise<void> {
  console.log("a1");
  await null;              // suspend HERE
  console.log("a2");
}
async function b(): Promise<void> {
  console.log("b1");
  await null;
  console.log("b2");
}
await Promise.all([a(), b()]);
console.log("done");
```

```
a1
b1
a2
b2
done
```

`a` runs to its `await` and suspends; `b` runs to its `await` and suspends; then
the two continuations run in the order they were queued. Reading this program
correctly is a genuine skill and it is entirely mechanical.

## Timers are ordered by expiry

Two timers with different delays fire in delay order, however busy the machine
is — the runtime sorts them by when they are due:

```ts
setTimeout(() => console.log("second"), 20);
setTimeout(() => console.log("first"), 1);
```

Two timers with the **same** delay fire in the order they were scheduled. That is
also specified, but it is a bad thing to depend on: it looks like timing and is
really insertion order, and one small edit reverses it.

## What is NOT guaranteed, and the rule that follows

* How long anything takes. `setTimeout(f, 10)` means "not before 10 ms".
* The completion order of independent work.

So, the rule this whole week follows:

> **Decide the output order in the program, not in the scheduler.** Await in a
> fixed order, or collect the results and print them by index.

`Promise.all` and `Promise.allSettled` give you that for free: their results are
in **argument order** whatever finished first. The `fix` at the end of this lesson
is exactly this bug — a program whose output order is decided by how fast each
piece happened to be.

> ⚠️ **Common mistakes:** thinking `setTimeout(…, 0)` jumps the queue; expecting
> a `.then` to run before the rest of the synchronous function; and printing from
> inside callbacks and hoping the order is stable.
""",
            warmup=[
                _q("Between a `.then` callback and a `setTimeout(…, 0)`, which runs first?",
                   ["the timer", "the .then — microtasks drain before the next macrotask",
                    "whichever was scheduled first", "it varies"], 1,
                   "Not a race at all."),
                _q("Microtasks added while the queue is draining…",
                   ["wait for the next turn", "are drained in the same pass", "are dropped",
                    "become timers"], 1,
                   "Which is how a promise chain finishes in one go."),
                _q("Two timers with delays 1 and 20 fire…",
                   ["in scheduling order", "in delay order", "at the same time", "unpredictably"], 1,
                   "Sorted by expiry."),
                _q("`await null` does…",
                   ["nothing", "suspends the function for one microtask", "throw", "wait 1 ms"], 1,
                   "Which is why it is enough to interleave two functions."),
            ],
            exercises=[
                _ex("tscourse-w17-ord-1", "Sync, microtask, timer",
                    "Add the microtask so the four lines print in the order they are numbered.",
                    'console.log("1 sync");\n'
                    'setTimeout(() => {\n'
                    '  console.log("4 timer");\n'
                    '}, 0);\n'
                    'Promise.resolve().then(() => {\n'
                    '  console.log("3 microtask");\n});\n'
                    'console.log("2 sync");\n',
                    'Promise.resolve().then(() => {',
                    [("", "1 sync\n2 sync\n3 microtask\n4 timer")],
                    hints=["An already-resolved promise's continuation is a microtask.",
                           "Write Promise.resolve().then(() => {"],
                    difficulty="Medium"),
                _ex("tscourse-w17-ord-2", "Queue a microtask directly",
                    "`queueMicrotask` puts a function on the same queue promises use. Watch it beat the synchronous line it was written above.",
                    'queueMicrotask(() => {\n'
                    '  console.log("microtask");\n});\n'
                    'console.log("sync");\n',
                    'queueMicrotask(() => {', [("", "sync\nmicrotask")],
                    hints=["Same queue as a promise continuation, without a promise.",
                           "Write queueMicrotask(() => {"],
                    difficulty="Easy"),
                _ex("tscourse-w17-ord-3", "Timers, in expiry order",
                    "Schedule the later line with the longer delay, so the output reads first then second.",
                    'setTimeout(() => {\n'
                    '  console.log("second");\n'
                    '}, 20);\n'
                    'setTimeout(() => {\n'
                    '  console.log("first");\n'
                    '}, 1);\n',
                    '}, 20);', [("", "first\nsecond")],
                    hints=["The runtime sorts pending timers by when they are due, not by when they were created.",
                           "Write }, 20);"],
                    difficulty="Easy"),
                _ex("tscourse-w17-ord-4", "Two async functions, interleaved",
                    "Suspend each function once, so the two halves interleave predictably.",
                    'async function a(): Promise<void> {\n'
                    '  console.log("a1");\n'
                    '  await null;\n'
                    '  console.log("a2");\n}\n'
                    'async function b(): Promise<void> {\n'
                    '  console.log("b1");\n'
                    '  await null;\n'
                    '  console.log("b2");\n}\n'
                    'await Promise.all([a(), b()]);\n'
                    'console.log("done");\n',
                    'await Promise.all([a(), b()]);',
                    [("", "a1\nb1\na2\nb2\ndone")],
                    hints=["Start both, then wait for both together.",
                           "Write await Promise.all([a(), b()]);"],
                    difficulty="Medium"),
                _ex("tscourse-w17-ord-5", "Print by index, not by arrival",
                    "The pages finish in reverse order. Await them together and print the array, so the order is the program's decision.",
                    _AFTER +
                    'async function load(id: number): Promise<string> {\n'
                    '  return after((4 - id) * 10, `page ${id}`);\n}\n'
                    'const pages = await Promise.all([load(1), load(2), load(3)]);\n'
                    'for (const page of pages) {\n'
                    '  console.log(page);\n}\n',
                    'const pages = await Promise.all([load(1), load(2), load(3)]);',
                    [("", "page 1\npage 2\npage 3")],
                    hints=["Page 3 finishes first and page 1 last — and the output must not show that.",
                           "`Promise.all` resolves to results in ARGUMENT order.",
                           "Write const pages = await Promise.all([load(1), load(2), load(3)]);"],
                    difficulty="Medium"),
                _fix("tscourse-w17-ord-fix1", "Fix the output that arrival order decided",
                     "Each page prints from inside its own callback, so the transcript is in completion order — `b`, `c`, `a` — rather than the order the program asked for. Collect the results and print them by index.",
                     _AFTER +
                     'for (const [ms, name] of [[30, "a"], [1, "b"], [15, "c"]] as const) {\n'
                     '  after(ms, name).then((got) => {\n'
                     '    console.log(got);\n  });\n}\n',
                     _AFTER +
                     'const jobs = [[30, "a"], [1, "b"], [15, "c"]] as const;\n'
                     'const names = await Promise.all(jobs.map(([ms, name]) => after(ms, name)));\n'
                     'for (const name of names) {\n'
                     '  console.log(name);\n}\n',
                     [("", "a\nb\nc")],
                     hints=["The work may finish in any order; the OUTPUT may not.",
                            "Start all three, then await them together.",
                            "`Promise.all` over the mapped jobs gives you the names in argument order."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The event loop's cycle is…",
                   ["one task, one microtask, repeat", "sync to completion, drain ALL microtasks, one macrotask, repeat",
                    "microtasks last", "unspecified"], 1,
                   "Three rules, and they explain every puzzle."),
                _q("Depending on two equal-delay timers firing in scheduling order is…",
                   ["fine", "specified but fragile — it is insertion order dressed as timing",
                    "impossible", "faster"], 1,
                   "One edit reverses it."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w17-errors", "When it goes wrong",
            "A rejection is a throw that happens later.",
            """
Inside an `async` function the symmetry is exact:

| in the body | to the caller |
|---|---|
| `return v` | the promise **fulfils** with v |
| `throw e` | the promise **rejects** with e |

So `await` does the mirror image: it either hands you the value, or **throws** the
reason — which means `try`/`catch` works exactly as it always has:

```ts
try {
  const page = await load(1);
  console.log(page);
} catch (err) {
  console.log(err instanceof Error ? err.message : String(err));
} finally {
  console.log("done");
}
```

`catch (err)` is **`unknown`**, for the same reason as in week 15: anything can be
thrown, including a string or `undefined`. Narrow it before you read `.message`,
or the compiler stops you:

```
TS18046: 'err' is of type 'unknown'.
```

## The `try` that catches nothing

This is the subtle one, and it is worth memorising:

```ts
async function run(): Promise<string> {
  try {
    return boom();            // ❌ the promise LEAVES the try before it settles
  } catch {
    return "caught";
  }
}
```

`return boom()` returns the promise itself. By the time it rejects, the `try`
block is long gone — so the `catch` never runs and the rejection escapes.

```ts
    return await boom();      // ✅ settled inside the try, so the catch works
```

`return await` looks redundant and is not. Inside a `try`, it is the difference
between handling an error and losing one.

## A rejection nobody is waiting for

```ts
async function boom(): Promise<void> {
  throw new Error("x");
}
boom();                       // nobody awaits, nobody catches
console.log("kept going");
```

That program prints `kept going` and then **dies** — an unhandled rejection is a
fatal error on Node's default setting. A "floating promise" is not a tidiness
issue, it is a crash, and it is why linters flag every un-awaited call.

Either `await` it, or attach a handler, or say explicitly that you do not care:

```ts
await boom();                          // handle it here
boom().catch(() => { /* logged */ });  // handle it there
```

## Wrapping, rather than swallowing

Catching an error to add context and rethrowing it is good practice; catching it
to print a message and carrying on as though nothing happened is how a corrupted
ledger gets written:

```ts
try {
  return await load(id);
} catch (err) {
  throw new Error(`page ${id}: ${err instanceof Error ? err.message : "failed"}`);
}
```

And where failure is *expected* — a page that might legitimately be missing —
week 15's `Result` pattern is still the better answer. Rejection is for the
exceptional case.

> ⚠️ **Common mistakes:** `return p` instead of `return await p` inside a `try`;
> reading `err.message` without narrowing; and leaving a promise floating.
""",
            warmup=[
                _q("`throw` in an async function…",
                   ["crashes", "rejects the returned promise", "returns undefined",
                    "is caught automatically"], 1,
                   "The mirror of `return`."),
                _q("`catch (err)` types err as…",
                   ["Error", "unknown", "any", "the thrown type"], 1,
                   "Anything can be thrown."),
                _q("`return p` inside a try, where p rejects…",
                   ["is caught", "escapes — p leaves the try before it settles", "throws sync",
                    "returns undefined"], 1,
                   "`return await p` is the fix."),
                _q("A rejected promise nobody awaits…",
                   ["is ignored", "kills the process by default", "warns once", "retries"], 1,
                   "Which makes floating promises a real bug."),
            ],
            exercises=[
                _ex("tscourse-w17-err-1", "Catch a rejection",
                    "Wrap the await so the rejection is handled rather than fatal.",
                    'async function load(id: number): Promise<string> {\n'
                    '  if (id > 1) {\n'
                    '    throw new Error(`page ${id} missing`);\n  }\n'
                    '  return `page ${id}`;\n}\n'
                    'try {\n'
                    '  console.log(await load(2));\n'
                    '} catch (err) {\n'
                    '  console.log(err instanceof Error ? err.message : "?");\n}\n',
                    'try {', [("", "page 2 missing")],
                    hints=["`await` throws the rejection reason, so ordinary try/catch applies.",
                           "Write try {"],
                    difficulty="Easy"),
                _ex("tscourse-w17-err-2", "Narrow the unknown",
                    "Get the message out of the caught value without asserting anything.",
                    'async function boom(): Promise<void> {\n'
                    '  throw new Error("page missing");\n}\n'
                    'try {\n'
                    '  await boom();\n'
                    '} catch (err) {\n'
                    '  console.log(err instanceof Error ? err.message : String(err));\n}\n',
                    '  console.log(err instanceof Error ? err.message : String(err));',
                    [("", "page missing")],
                    hints=["Test what it is before reading a member — week 15's guard.",
                           'Write console.log(err instanceof Error ? err.message : String(err));'],
                    difficulty="Medium"),
                _ex("tscourse-w17-err-3", "Cleanup that always runs",
                    "Add the block that runs on either outcome.",
                    'async function load(): Promise<string> {\n'
                    '  throw new Error("nope");\n}\n'
                    'try {\n'
                    '  console.log(await load());\n'
                    '} catch {\n'
                    '  console.log("failed");\n'
                    '} finally {\n'
                    '  console.log("closed");\n}\n',
                    '} finally {', [("", "failed\nclosed")],
                    hints=["One keyword, after the catch.",
                           "Write } finally {"],
                    difficulty="Easy"),
                _ex("tscourse-w17-err-4", "`return await`, inside a try",
                    "Settle the promise inside the try block so the catch can see its rejection.",
                    'async function boom(): Promise<string> {\n'
                    '  throw new Error("x");\n}\n'
                    'async function run(): Promise<string> {\n'
                    '  try {\n'
                    '    return await boom();\n'
                    '  } catch {\n'
                    '    return "caught";\n  }\n}\n'
                    'console.log(await run());\n',
                    '    return await boom();', [("", "caught")],
                    hints=["Returning the promise itself hands it to the caller unsettled, and the try is over.",
                           "Write return await boom();"],
                    difficulty="Medium"),
                _ex("tscourse-w17-err-5", "Wrap, do not swallow",
                    "Catch the failure, add which page it was, and rethrow.",
                    'async function load(id: number): Promise<string> {\n'
                    '  throw new Error("timed out");\n}\n'
                    'async function loadPage(id: number): Promise<string> {\n'
                    '  try {\n'
                    '    return await load(id);\n'
                    '  } catch (err) {\n'
                    '    throw new Error(`page ${id}: ${err instanceof Error ? err.message : "failed"}`);\n  }\n}\n'
                    'try {\n'
                    '  await loadPage(3);\n'
                    '} catch (err) {\n'
                    '  console.log(err instanceof Error ? err.message : "?");\n}\n',
                    '    throw new Error(`page ${id}: ${err instanceof Error ? err.message : "failed"}`);',
                    [("", "page 3: timed out")],
                    hints=["Build a new Error whose message carries the context, and throw that.",
                           'Write throw new Error(`page ${id}: ${err instanceof Error ? err.message : "failed"}`);'],
                    difficulty="Medium"),
                _ex("tscourse-w17-err-6", "Handle it where it floats",
                    "This call is deliberately not awaited. Attach a handler so its rejection cannot kill the process.",
                    'async function boom(): Promise<void> {\n'
                    '  throw new Error("background failure");\n}\n'
                    'boom().catch((err: unknown) => {\n'
                    '  console.log(err instanceof Error ? `logged: ${err.message}` : "?");\n});\n'
                    'console.log("kept going");\n',
                    'boom().catch((err: unknown) => {',
                    [("", "kept going\nlogged: background failure")],
                    hints=["`.catch` on the call itself is enough — the promise is no longer unhandled.",
                           "Write boom().catch((err: unknown) => {"],
                    difficulty="Medium"),
                _diagnose("tscourse-w17-err-d1", "The message on an unknown",
                          "TS18046: 'err' is of type 'unknown'.",
                          'async function run(): Promise<string> {\n'
                          '  try {\n'
                          '    await Promise.reject(new Error("boom"));\n'
                          '    return "ok";\n'
                          '  } catch (err) {\n'
                          '    return err.message;\n  }\n}\n'
                          'console.log(await run());\n',
                          'async function run(): Promise<string> {\n'
                          '  try {\n'
                          '    await Promise.reject(new Error("boom"));\n'
                          '    return "ok";\n'
                          '  } catch (err) {\n'
                          '    return err instanceof Error ? err.message : String(err);\n  }\n}\n'
                          'console.log(await run());\n',
                          [("", "boom")],
                          hints=["Anything can be thrown, so the compiler will not assume it was an Error.",
                                 "Narrow with `instanceof` and supply the other branch.",
                                 "Write return err instanceof Error ? err.message : String(err);"],
                          difficulty="Easy"),
                _fix("tscourse-w17-err-fix1", "Fix the try that catches nothing",
                     "This prints nothing and exits non-zero: `return boom()` hands the promise to the caller *unsettled*, so it rejects after the `try` block is over and the `catch` never runs. One keyword fixes it.",
                     'async function boom(): Promise<string> {\n'
                     '  throw new Error("x");\n}\n'
                     'async function run(): Promise<string> {\n'
                     '  try {\n'
                     '    return boom();\n'
                     '  } catch {\n'
                     '    return "caught";\n  }\n}\n'
                     'console.log(await run());\n',
                     'async function boom(): Promise<string> {\n'
                     '  throw new Error("x");\n}\n'
                     'async function run(): Promise<string> {\n'
                     '  try {\n'
                     '    return await boom();\n'
                     '  } catch {\n'
                     '    return "caught";\n  }\n}\n'
                     'console.log(await run());\n',
                     [("", "caught")],
                     hints=["The rejection happens after the try block has finished executing.",
                            "To be caught here, the promise has to settle INSIDE the try.",
                            "Write return await boom();"],
                     difficulty="Medium"),
                _fix("tscourse-w17-err-fix2", "Fix the floating promise",
                     "The program prints `kept going` and then dies: nothing awaits `boom()`, and an unhandled rejection is fatal. Wait for it, and report the failure.",
                     'async function boom(): Promise<void> {\n'
                     '  throw new Error("background failure");\n}\n'
                     'boom();\n'
                     'console.log("kept going");\n',
                     'async function boom(): Promise<void> {\n'
                     '  throw new Error("background failure");\n}\n'
                     'try {\n'
                     '  await boom();\n'
                     '} catch (err) {\n'
                     '  console.log(err instanceof Error ? err.message : "?");\n}\n'
                     'console.log("kept going");\n',
                     [("", "background failure\nkept going")],
                     hints=["A promise nobody waits for still rejects — and here that ends the process.",
                            "Await it inside a try, and print the message from the catch.",
                            "The `kept going` line then comes last, because the await happens before it."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`return await p` inside a try is…",
                   ["redundant", "the difference between catching p's rejection and losing it",
                    "slower", "a lint error"], 1,
                   "One of the few places the extra keyword matters."),
                _q("For a failure that is part of the contract — a page that may be missing — prefer…",
                   ["throwing", "week 15's Result pattern", "a floating promise", "process.exit"], 1,
                   "Rejection is for the exceptional case."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w17-seqpar", "In a row, or all at once",
            "The same three awaits, three times the time.",
            """
```ts
for (const id of [1, 2, 3]) {
  pages.push(await load(id));      // SEQUENTIAL: each waits for the last
}
```

Total time: the **sum**. If each load takes 100 ms, this takes 300.

```ts
const pages = await Promise.all([1, 2, 3].map(load));   // CONCURRENT
```

Total time: the **slowest**. If each takes 100 ms, this takes 100.

Same three calls, same results, a third of the wall clock. The difference is
whether the next call starts before the previous one has finished.

## When sequential is right

Not always a mistake — sometimes it is the only correct answer:

* **Each call needs the previous result.** A cursor, a page token, an id you only
  learn from the last response.
* **You must not hammer the other end.** Rate limits are real.
* **Order of side effects matters.** Three writes that must land in order.

Otherwise, concurrency is free and you should take it.

## The two-phase shape

`Promise.all` is one way; the other is worth knowing because it makes the
mechanism obvious:

```ts
const started = [load(1), load(2), load(3)];   // all three in flight NOW
const a = await started[0];                     // …then collect, in order
```

Calling an async function **starts** it. Awaiting only decides when you look at
the result. `Promise.all` is a tidy wrapper over exactly this.

## `.map` with an async callback

```ts
const promises = [1, 2, 3].map(load);       // Promise<string>[] — NOT string[]
const pages = await Promise.all(promises);  // string[]
```

`.map` does not know anything about promises. It calls the function three times
and collects what comes back, which is three promises. Forget the `Promise.all`
and the compiler catches it:

```
TS2322: Type 'Promise<number>[]' is not assignable to type 'number[]'.
```

## `forEach` is the trap

```ts
const out: number[] = [];
[1, 2, 3].forEach(async (n) => {
  out.push(await double(n));
});
console.log(out.join(","));        // prints nothing at all
```

`forEach` **discards** its callback's return value, so every one of those
promises is floating and nothing waits for any of them. The array is still empty
when it is printed. The compiler cannot help: `forEach` is declared to take a
function returning `void`, and an async function returning `Promise<void>` is
assignable to that.

The two correct shapes:

```ts
for (const n of [1, 2, 3]) { out.push(await double(n)); }        // sequential
const out = await Promise.all([1, 2, 3].map(double));            // concurrent
```

## And the order results come back in

```ts
const pages = await Promise.all([load(1), load(2), load(3)]);
```

`pages` is `[page1, page2, page3]` — in **argument order** — even when page 3
finishes first. That is a specified guarantee, and it is what makes concurrent
code with deterministic output possible at all.

> ⚠️ **Common mistakes:** awaiting in a loop when nothing depends on the previous
> answer; `forEach` with an async callback; and assuming `Promise.all` returns
> results in the order they completed.
""",
            warmup=[
                _q("Three awaits in a loop, 100 ms each, take…",
                   ["100 ms", "300 ms", "no time", "200 ms"], 1,
                   "Sequential means the sum."),
                _q("`await Promise.all(ids.map(load))` takes…",
                   ["the sum", "the slowest one's time", "no time", "twice the slowest"], 1,
                   "They are all in flight at once."),
                _q("`[1,2].map(asyncFn)` gives…",
                   ["values", "an array of promises", "void", "a promise of an array"], 1,
                   "map knows nothing about promises."),
                _q("`forEach` with an async callback…",
                   ["waits", "discards every promise and waits for none", "is a type error",
                    "runs sequentially"], 1,
                   "Which is why the array is still empty."),
            ],
            exercises=[
                _ex("tscourse-w17-sp-1", "One after another",
                    "Await inside the loop, so each page is fetched only after the last has arrived.",
                    _AFTER +
                    'async function load(id: number): Promise<string> {\n'
                    '  return after(1, `page ${id}`);\n}\n'
                    'const pages: string[] = [];\n'
                    'for (const id of [1, 2, 3]) {\n'
                    '  pages.push(await load(id));\n}\n'
                    'console.log(pages.join(", "));\n',
                    '  pages.push(await load(id));',
                    [("", "page 1, page 2, page 3")],
                    hints=["Push the awaited result, not the promise.",
                           "Write pages.push(await load(id));"],
                    difficulty="Easy"),
                _ex("tscourse-w17-sp-2", "All at once",
                    "Start all three loads and await them together.",
                    _AFTER +
                    'async function load(id: number): Promise<string> {\n'
                    '  return after((4 - id) * 8, `page ${id}`);\n}\n'
                    'const pages = await Promise.all([1, 2, 3].map(load));\n'
                    'console.log(pages.join(", "));\n',
                    'const pages = await Promise.all([1, 2, 3].map(load));',
                    [("", "page 1, page 2, page 3")],
                    hints=["`.map(load)` gives you the promises; one call awaits all of them.",
                           "Write const pages = await Promise.all([1, 2, 3].map(load));"],
                    difficulty="Medium"),
                _ex("tscourse-w17-sp-3", "Start, then collect",
                    "Put all three in flight on one line, then await them in order to show that calling is what starts the work.",
                    _AFTER +
                    'async function load(id: number): Promise<string> {\n'
                    '  return after((4 - id) * 8, `page ${id}`);\n}\n'
                    'const started = [load(1), load(2), load(3)];\n'
                    'for (const pending of started) {\n'
                    '  console.log(await pending);\n}\n',
                    'const started = [load(1), load(2), load(3)];',
                    [("", "page 1\npage 2\npage 3")],
                    hints=["An async function starts running the moment it is called.",
                           "Write const started = [load(1), load(2), load(3)];"],
                    difficulty="Medium"),
                _ex("tscourse-w17-sp-4", "Argument order, not arrival order",
                    "Page 3 finishes first. Prove the results still come back in the order they were asked for.",
                    _AFTER +
                    'async function load(id: number): Promise<number> {\n'
                    '  return after((4 - id) * 10, id);\n}\n'
                    'const ids = await Promise.all([load(1), load(2), load(3)]);\n'
                    'console.log(ids.join(" "));\n',
                    'const ids = await Promise.all([load(1), load(2), load(3)]);',
                    [("", "1 2 3")],
                    hints=["The delays are deliberately reversed, and the output must not show it.",
                           "Write const ids = await Promise.all([load(1), load(2), load(3)]);"],
                    difficulty="Medium"),
                _ex("tscourse-w17-sp-5", "Sequential because it has to be",
                    "Each page's id comes from the previous page, so concurrency is not available. Chain them.",
                    _AFTER +
                    'async function next(id: number): Promise<number> {\n'
                    '  return after(1, id * 2);\n}\n'
                    'let id = 1;\n'
                    'const seen: number[] = [id];\n'
                    'for (let i = 0; i < 3; i = i + 1) {\n'
                    '  id = await next(id);\n'
                    '  seen.push(id);\n}\n'
                    'console.log(seen.join(" -> "));\n',
                    '  id = await next(id);', [("", "1 -> 2 -> 4 -> 8")],
                    hints=["The next call's argument is the previous call's result, so nothing can overlap.",
                           "Write id = await next(id);"],
                    difficulty="Medium"),
                _diagnose("tscourse-w17-sp-d1", "An array of promises is not an array of values",
                          "TS2322: Type 'Promise<number>[]' is not assignable to type 'number[]'.",
                          'async function double(n: number): Promise<number> {\n'
                          '  return n * 2;\n}\n'
                          'const out: number[] = [1, 2].map(double);\n'
                          'console.log(out.join(" "));\n',
                          'async function double(n: number): Promise<number> {\n'
                          '  return n * 2;\n}\n'
                          'const out: number[] = await Promise.all([1, 2].map(double));\n'
                          'console.log(out.join(" "));\n',
                          [("", "2 4")],
                          hints=["`.map` collects whatever the callback returned, and an async function returns a promise.",
                                 "Something has to wait for all of them.",
                                 "Wrap the mapped array in `await Promise.all(...)`."],
                          difficulty="Medium"),
                _fix("tscourse-w17-sp-fix1", "Fix the forEach that did not wait",
                     "This prints an empty line. `forEach` throws away what its callback returns, so all three promises are floating and the array is still empty when it is joined. Use a loop that can wait.",
                     'async function double(n: number): Promise<number> {\n'
                     '  return n * 2;\n}\n'
                     'const out: number[] = [];\n'
                     '[1, 2, 3].forEach(async (n) => {\n'
                     '  out.push(await double(n));\n});\n'
                     'console.log(out.join(","));\n',
                     'async function double(n: number): Promise<number> {\n'
                     '  return n * 2;\n}\n'
                     'const out: number[] = [];\n'
                     'for (const n of [1, 2, 3]) {\n'
                     '  out.push(await double(n));\n}\n'
                     'console.log(out.join(","));\n',
                     [("", "2,4,6")],
                     hints=["`forEach` is declared to take a callback returning void, so an async callback type-checks and is ignored.",
                            "Nothing in the program ever waits for those three promises.",
                            "Replace the forEach with `for (const n of [1, 2, 3])`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Sequential awaits are the RIGHT choice when…",
                   ["always", "each call needs the previous result, or order of writes matters",
                    "never", "the calls are slow"], 1,
                   "Otherwise take the concurrency."),
                _q("Calling an async function…",
                   ["does nothing until awaited", "starts it immediately", "blocks", "queues a timer"], 1,
                   "Awaiting only decides when you look."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w17-combinators", "`all`, `allSettled`, `race`, `any`",
            "Four ways to combine promises, chosen by what you want failure to do.",
            """
All four take an iterable of promises. They differ only in **when they settle**
and **what one failure does**.

## `Promise.all` — everything, or nothing

```ts
const pages = await Promise.all([load(1), load(2), load(3)]);   // string[]
```

* Fulfils with results in **argument order**.
* Rejects **as soon as any input rejects** ("fail fast") — with that one reason,
  and you lose the others' results.

Reach for it when partial success is useless to you.

## `Promise.allSettled` — tell me about all of them

```ts
const results = await Promise.allSettled([load(1), load(2)]);
for (const r of results) {
  console.log(r.status === "fulfilled" ? `ok ${r.value}` : "failed");
}
```

* **Never rejects.**
* Yields one object per input, in argument order:
  `{ status: "fulfilled", value }` or `{ status: "rejected", reason }`.

It is a **discriminated union** (week 9), so you must narrow on `status` before
touching `.value` — the compiler insists:

```
TS2339: Property 'value' does not exist on type 'PromiseSettledResult<number>'.
```

Reach for it when you want a report rather than an outcome. This week's capstone
is built on it.

## `Promise.race` — whoever settles first

```ts
const winner = await Promise.race([work, after(50, "timed out")]);
```

* Settles exactly as the **first input settles** — including a rejection. A fast
  failure beats a slow success.

The timeout wrapper is the canonical use, and essentially the only one you will
write by hand.

## `Promise.any` — whoever succeeds first

```ts
const v = await Promise.any([mirrorA(), mirrorB()]);
```

* Fulfils with the **first fulfilment**, ignoring earlier rejections.
* Rejects only if **all** of them reject, with an `AggregateError` whose `errors`
  array holds every reason.

Reach for it for redundant sources.

## Choosing, in one line each

| you want | use |
|---|---|
| all of them, or fail | `all` |
| a report on every one | `allSettled` |
| the first answer, or a timeout | `race` |
| any one that works | `any` |

## Determinism, since output is compared exactly

A race needs an unambiguous winner. Two safe forms: an already-resolved promise
against a timer (the microtask always wins — lesson 4), or two timers with delays
far apart. Two timers with the *same* delay is not a race, it is insertion order
wearing a disguise.

> ⚠️ **Common mistakes:** `all` where you wanted `allSettled`, losing four results
> to one failure; reading `.value` without checking `.status`; and expecting
> `race` to ignore a rejection — that is `any`.
""",
            warmup=[
                _q("`Promise.all` rejects…",
                   ["never", "as soon as one input rejects", "when all reject", "after all settle"], 1,
                   "Fail fast."),
                _q("`Promise.allSettled` rejects…",
                   ["on the first failure", "never", "when all fail", "on a timeout"], 1,
                   "It reports instead."),
                _q("`Promise.race` settles when the first input…",
                   ["fulfils", "settles — a rejection can win", "rejects", "times out"], 1,
                   "`any` is the one that waits for a success."),
                _q("`Promise.any` rejects…",
                   ["on the first failure", "only when all reject, with an AggregateError",
                    "never", "on a timeout"], 1,
                   "Made for redundant sources."),
            ],
            exercises=[
                _ex("tscourse-w17-cb-1", "All of them, or nothing",
                    "Await all three loads together and join the results.",
                    _AFTER +
                    'async function load(id: number): Promise<string> {\n'
                    '  return after((4 - id) * 8, `page ${id}`);\n}\n'
                    'const pages = await Promise.all([load(1), load(2), load(3)]);\n'
                    'console.log(pages.join(" | "));\n',
                    'const pages = await Promise.all([load(1), load(2), load(3)]);',
                    [("", "page 1 | page 2 | page 3")],
                    hints=["One combinator, one array.",
                           "Write const pages = await Promise.all([load(1), load(2), load(3)]);"],
                    difficulty="Easy"),
                _ex("tscourse-w17-cb-2", "Fail fast, caught",
                    "One page is missing. Catch the rejection `all` produces and report it.",
                    'async function load(id: number): Promise<string> {\n'
                    '  if (id === 2) {\n'
                    '    throw new Error("page 2 missing");\n  }\n'
                    '  return `page ${id}`;\n}\n'
                    'try {\n'
                    '  const pages = await Promise.all([load(1), load(2), load(3)]);\n'
                    '  console.log(pages.join(" | "));\n'
                    '} catch (err) {\n'
                    '  console.log(err instanceof Error ? `gave up: ${err.message}` : "?");\n}\n',
                    '  const pages = await Promise.all([load(1), load(2), load(3)]);',
                    [("", "gave up: page 2 missing")],
                    hints=["One rejection rejects the whole thing, and the other two results are lost.",
                           "Write const pages = await Promise.all([load(1), load(2), load(3)]);"],
                    difficulty="Medium"),
                _ex("tscourse-w17-cb-3", "A report on every one",
                    "Use the combinator that never rejects, then narrow each result on its status.",
                    'async function load(id: number): Promise<string> {\n'
                    '  if (id === 2) {\n'
                    '    throw new Error("page 2 missing");\n  }\n'
                    '  return `page ${id}`;\n}\n'
                    'const results = await Promise.allSettled([load(1), load(2), load(3)]);\n'
                    'for (const r of results) {\n'
                    '  if (r.status === "fulfilled") {\n'
                    '    console.log(`ok ${r.value}`);\n'
                    '  } else {\n'
                    '    console.log(`failed ${r.reason instanceof Error ? r.reason.message : "?"}`);\n  }\n}\n',
                    'const results = await Promise.allSettled([load(1), load(2), load(3)]);',
                    [("", "ok page 1\nfailed page 2 missing\nok page 3")],
                    hints=["The combinator that reports rather than rejects.",
                           "Write const results = await Promise.allSettled([load(1), load(2), load(3)]);"],
                    difficulty="Medium"),
                _ex("tscourse-w17-cb-4", "First to settle",
                    "Race the slow work against a timeout that is nowhere near as slow.",
                    _AFTER +
                    'const winner = await Promise.race([\n'
                    '  after(60, "the work finished"),\n'
                    '  after(1, "timed out"),\n'
                    ']);\n'
                    'console.log(winner);\n',
                    'const winner = await Promise.race([', [("", "timed out")],
                    hints=["The first to SETTLE wins, and one of these is sixty times faster.",
                           "Write const winner = await Promise.race(["],
                    difficulty="Easy"),
                _ex("tscourse-w17-cb-5", "First to succeed",
                    "One mirror is down. Take whichever one works.",
                    'async function mirrorA(): Promise<string> {\n'
                    '  throw new Error("A is down");\n}\n'
                    'async function mirrorB(): Promise<string> {\n'
                    '  return "from B";\n}\n'
                    'const page = await Promise.any([mirrorA(), mirrorB()]);\n'
                    'console.log(page);\n',
                    'const page = await Promise.any([mirrorA(), mirrorB()]);',
                    [("", "from B")],
                    hints=["`race` would let the failure win; this one ignores rejections until there are no others.",
                           "Write const page = await Promise.any([mirrorA(), mirrorB()]);"],
                    difficulty="Medium"),
                _ex("tscourse-w17-cb-6", "Count the successes",
                    "Filter the settled results down to the fulfilled ones and report how many there were.",
                    'async function load(id: number): Promise<number> {\n'
                    '  if (id % 2 === 0) {\n'
                    '    throw new Error("even pages are missing");\n  }\n'
                    '  return id;\n}\n'
                    'const results = await Promise.allSettled([load(1), load(2), load(3), load(4)]);\n'
                    'const ok = results.filter((r) => r.status === "fulfilled");\n'
                    'console.log(`${ok.length} of ${results.length}`);\n',
                    'const ok = results.filter((r) => r.status === "fulfilled");',
                    [("", "2 of 4")],
                    hints=["Filter on the discriminant.",
                           'Write const ok = results.filter((r) => r.status === "fulfilled");'],
                    difficulty="Medium"),
                _predict("tscourse-w17-cb-p1", "What `all` gives you for a mixed tuple",
                         'async function id(): Promise<number> {\n'
                         '  return 1;\n}\n'
                         'async function name(): Promise<string> {\n'
                         '  return "x";\n}\n'
                         'const both = await Promise.all([id(), name()]);\n',
                         "both", "[number, string]",
                         why="`all` over a tuple of promises keeps each position's own type.",
                         hints=["Not an array of a union — the positions are remembered.",
                                "Two positions, two different types.",
                                "Write [number, string]."],
                         difficulty="Medium"),
                _diagnose("tscourse-w17-cb-d1", "The value that might not be there",
                          "TS2339: Property 'value' does not exist on type 'PromiseSettledResult<number>'.",
                          'const rs = await Promise.allSettled([Promise.resolve(1)]);\n'
                          'const first = rs[0];\n'
                          'if (first !== undefined) {\n'
                          '  console.log(first.value);\n}\n',
                          'const rs = await Promise.allSettled([Promise.resolve(1)]);\n'
                          'const first = rs[0];\n'
                          'if (first !== undefined && first.status === "fulfilled") {\n'
                          '  console.log(first.value);\n}\n',
                          [("", "1")],
                          hints=["A settled result is a discriminated union: one member has `value`, the other has `reason`.",
                                 "Checking it is present is not the same as checking it succeeded.",
                                 'Add `&& first.status === "fulfilled"`.'],
                          difficulty="Medium"),
            ],
            quiz=[
                _q("Losing four good results to one failure is the sign you wanted…",
                   ["race", "allSettled", "any", "all"], 1,
                   "A report, not an outcome."),
                _q("A settled result must be narrowed on `.status` because…",
                   ["it is optional", "it is a discriminated union — only one member has `value`",
                    "it is unknown", "of strict mode"], 1,
                   "Week 9's pattern, in the standard library."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w17-typing", "Typing asynchrony",
            "`Promise<T>`, `Awaited<T>`, and the generic async function.",
            """
## `Promise<T>` is the only shape

Whatever an async function's body does, its type is `Promise<T>`:

```ts
async function total(n: number): Promise<number> { return n * 2; }
async function announce(s: string): Promise<void> { console.log(s); }
async function loadOrNot(id: number): Promise<string | undefined> { … }
```

Note the third one: an async function that may find nothing returns
`Promise<string | undefined>`, **not** `Promise<string> | undefined`. The
absence is in the value, not in the promise — the promise always exists.

## `Awaited<T>`

The utility that answers "what do I get if I await this?":

```ts
type A = Awaited<Promise<number>>;               // number
type B = Awaited<Promise<Promise<string>>>;      // string — it unwraps recursively
type C = Awaited<number>;                         // number — a non-promise is itself
```

The recursion is not a curiosity: it mirrors the runtime, where a promise that
resolves *with a promise* is flattened, so `Promise<Promise<T>>` never actually
exists as a value. `Awaited<T>` is how you write a generic helper that talks about
the resolved type:

```ts
async function firstOf<T>(ps: readonly Promise<T>[]): Promise<T | undefined> {
  for (const p of ps) { return await p; }
  return undefined;
}
```

## Inference already knows

You rarely need to annotate the return type of an async function — it is inferred
from the returns, wrapped in a promise:

```ts
async function load(id: number) {        // inferred: Promise<string>
  return `page ${id}`;
}
```

Annotate anyway on anything exported, for the same reason as always: the
annotation is the contract, and it stops an accidental change of shape from
propagating silently.

## The generic async function

```ts
async function mapAsync<T, U>(
  xs: readonly T[],
  f: (x: T) => Promise<U>,
): Promise<U[]> {
  return Promise.all(xs.map(f));
}
```

Two type parameters, one promise in the callback's return, one promise around the
whole result. This signature is worth being able to write from memory — it is the
shape of nearly every async utility you will read.

## `void` versus `undefined`, once more

`Promise<void>` means "it finished; there is no value". `Promise<undefined>`
means "it finished, and the value is `undefined`" — technically different, and
`void` is the one you want, because it also permits a callback that happens to
return something and lets you ignore it.

> ⚠️ **Common mistakes:** `Promise<string> | undefined` where you meant
> `Promise<string | undefined>`; annotating an async function `: T` (TS1064); and
> reaching for `any` when `Awaited<T>` was the answer.
""",
            warmup=[
                _q("`Awaited<Promise<Promise<string>>>` is…",
                   ["Promise<string>", "string", "unknown", "never"], 1,
                   "It unwraps all the way down."),
                _q("`Awaited<number>` is…",
                   ["never", "number", "Promise<number>", "undefined"], 1,
                   "A non-promise awaits to itself."),
                _q("An async function that may find nothing returns…",
                   ["Promise<string> | undefined", "Promise<string | undefined>", "string | undefined",
                    "undefined"], 1,
                   "The promise always exists."),
                _q("The inferred return type of `async function f() { return 1; }` is…",
                   ["number", "Promise<number>", "void", "unknown"], 1,
                   "Inference wraps it for you."),
            ],
            exercises=[
                _ex("tscourse-w17-ty-1", "The absence is in the value",
                    "Type the loader that may not find the page.",
                    'async function loadOrNot(id: number): Promise<string | undefined> {\n'
                    '  return id === 1 ? "page 1" : undefined;\n}\n'
                    'export {};\n'
                    'console.log(`${await loadOrNot(1)} ${await loadOrNot(9)}`);\n',
                    'async function loadOrNot(id: number): Promise<string | undefined> {',
                    [("", "page 1 undefined")],
                    hints=["The promise is always there; the string may not be.",
                           "Write async function loadOrNot(id: number): Promise<string | undefined> {"],
                    difficulty="Medium"),
                _ex("tscourse-w17-ty-2", "What awaiting gives you",
                    "Name the resolved type with the utility, and annotate the value with it.",
                    'type Page = Awaited<Promise<string>>;\n'
                    'const page: Page = await Promise.resolve("page 1");\n'
                    'console.log(page.toUpperCase());\n',
                    'type Page = Awaited<Promise<string>>;', [("", "PAGE 1")],
                    hints=["One utility type, taking the promise type.",
                           "Write type Page = Awaited<Promise<string>>;"],
                    difficulty="Easy"),
                _ex("tscourse-w17-ty-3", "A generic async map",
                    "Write the signature every async utility is shaped like: an array in, an async callback, a promise of the results.",
                    'async function mapAsync<T, U>(\n'
                    '  xs: readonly T[],\n'
                    '  f: (x: T) => Promise<U>,\n'
                    '): Promise<U[]> {\n'
                    '  return Promise.all(xs.map(f));\n}\n'
                    'async function double(n: number): Promise<number> {\n'
                    '  return n * 2;\n}\n'
                    'console.log((await mapAsync([1, 2, 3], double)).join(" "));\n',
                    '): Promise<U[]> {', [("", "2 4 6")],
                    hints=["The callback yields one U at a time; the whole call yields all of them.",
                           "Write ): Promise<U[]> {"],
                    difficulty="Medium"),
                _ex("tscourse-w17-ty-4", "Nothing to hand back",
                    "Annotate the function that finishes without a value.",
                    _DELAY +
                    'async function flush(name: string): Promise<void> {\n'
                    '  await delay(1);\n'
                    '  console.log(`flushed ${name}`);\n}\n'
                    'await flush("ledger");\n',
                    'async function flush(name: string): Promise<void> {',
                    [("", "flushed ledger")],
                    hints=["`void` rather than `undefined`, for the usual reason.",
                           "Write async function flush(name: string): Promise<void> {"],
                    difficulty="Easy"),
                _ex("tscourse-w17-ty-5", "A generic that returns the first result",
                    "Give the helper the return type that covers an empty array as well.",
                    'async function firstOf<T>(ps: readonly Promise<T>[]): Promise<T | undefined> {\n'
                    '  for (const p of ps) {\n'
                    '    return await p;\n  }\n'
                    '  return undefined;\n}\n'
                    'console.log(await firstOf([Promise.resolve("a"), Promise.resolve("b")]));\n'
                    'console.log(await firstOf<string>([]));\n',
                    'async function firstOf<T>(ps: readonly Promise<T>[]): Promise<T | undefined> {',
                    [("", "a\nundefined")],
                    hints=["An empty array has no first element, so the union has to say so.",
                           "Write async function firstOf<T>(ps: readonly Promise<T>[]): Promise<T | undefined> {"],
                    difficulty="Medium"),
                _types("tscourse-w17-ty-t1", "Unwrap it completely",
                       "Write the alias that says what you get from awaiting a doubly-wrapped promise.",
                       'type Yielded = Awaited<Promise<Promise<string>>>;\n'
                       'type Plain = Awaited<number>;\n',
                       'type Yielded = Awaited<Promise<Promise<string>>>;',
                       'type _1 = Expect<Equal<Yielded, string>>;\n'
                       'type _2 = Expect<Equal<Plain, number>>;\n',
                       hints=["The utility recurses, so no matter how many layers there are the answer is the innermost type.",
                              "Write type Yielded = Awaited<Promise<Promise<string>>>;"],
                       difficulty="Medium"),
                _predict("tscourse-w17-ty-p1", "The inferred return type",
                         'async function load(id: number) {\n'
                         '  return `page ${id}`;\n}\n'
                         'const pending = load(1);\n',
                         "pending", "Promise<string>",
                         why="The body returns a template string, and the function is async.",
                         hints=["Inference wraps what you returned.",
                                "Write Promise<string>."]),
                _diagnose("tscourse-w17-ty-d1", "The promise in the wrong place",
                          "TS2322: Type 'Promise<string | undefined>' is not assignable to type 'Promise<string> | undefined'.",
                          'async function loadOrNot(id: number): Promise<string | undefined> {\n'
                          '  return id === 1 ? "page 1" : undefined;\n}\n'
                          'const pending: Promise<string> | undefined = loadOrNot(1);\n'
                          'console.log(await pending);\n',
                          'async function loadOrNot(id: number): Promise<string | undefined> {\n'
                          '  return id === 1 ? "page 1" : undefined;\n}\n'
                          'const pending: Promise<string | undefined> = loadOrNot(1);\n'
                          'console.log(await pending);\n',
                          [("", "page 1")],
                          hints=["The call always returns a promise — there is no version of this where the promise is missing.",
                                 "Move the `| undefined` inside the angle brackets.",
                                 "Write const pending: Promise<string | undefined> = loadOrNot(1);"],
                          difficulty="Medium"),
            ],
            quiz=[
                _q("`Promise<void>` is preferred over `Promise<undefined>` because…",
                   ["it is shorter", "it says 'no value' and tolerates a callback that returns one anyway",
                    "they are identical", "undefined is banned"], 1,
                   "Same distinction as anywhere else `void` appears."),
                _q("Annotating an exported async function's return type is worth doing because…",
                   ["inference fails", "the annotation is the contract, and stops a shape change propagating silently",
                    "it is faster", "it is required"], 1,
                   "Same reason as every other exported signature."),
            ],
        ),
        # ---- Lesson 9 --------------------------------------------------
        _lesson(
            "w17-patterns", "Patterns worth stealing",
            "Retry, timeout, pipeline, and a promise you settle from outside.",
            """
Four shapes that cover most of what asynchronous code is actually for.

## `delay`

```ts
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => { setTimeout(resolve, ms); });
}
```

You will write this in every project that does not already have it. Note that it
is **not** `async` — there is nothing to await inside it, and wrapping it in an
async function would add a layer for no reason.

## Retry, driven by a counter

```ts
async function retry<T>(work: () => Promise<T>, attempts: number): Promise<T> {
  let last = "no attempts made";
  for (let i = 1; i <= attempts; i = i + 1) {
    try {
      return await work();
    } catch (err) {
      last = err instanceof Error ? err.message : "failed";
    }
  }
  throw new Error(`gave up after ${attempts}: ${last}`);
}
```

Three things make this correct rather than nearly-correct:

* **`return await work()`**, not `return work()` — inside a `try`, lesson 5's rule.
* The last error is **kept**, so the final failure says something useful.
* The loop is bounded. "Retry until it works" is an outage amplifier.

Real retries add a growing delay between attempts (`await delay(50 * i)`), which
is worth knowing the name of — *backoff* — even where a test cannot observe it.

## Timeout, with `race`

```ts
async function withTimeout<T>(work: Promise<T>, ms: number, fallback: T): Promise<T> {
  return Promise.race([work, after(ms, fallback)]);
}
```

The honest limitation: the slow work is **not cancelled**. It keeps running and
its result is thrown away, because a promise has no cancel. (`AbortController` is
how real APIs opt into cancellation, and it is worth looking up once you need it.)

## A pipeline

```ts
async function pipeline(id: number): Promise<string> {
  const raw = await fetchPage(id);
  const parsed = await parse(raw);
  return format(parsed);
}
```

Deliberately sequential: each step needs the previous result. Written with
`.then` this is a chain; written with `await` it reads like the three steps it is.

## `Promise.withResolvers`

For the case where the thing that settles the promise is somewhere else entirely —
an event handler, a callback API you are wrapping:

```ts
const { promise, resolve } = Promise.withResolvers<string>();
onReady(() => { resolve("ready"); });
console.log(await promise);
```

Before this existed, everyone assigned `resolve` to an outer variable from inside
the executor, and it was as awkward as it sounds.

> ⚠️ **Common mistakes:** an unbounded retry; `return work()` inside a retry's
> `try`; and believing a timeout cancelled anything.
""",
            warmup=[
                _q("`delay` should be…",
                   ["async", "a plain function returning a promise", "a class", "a generator"], 1,
                   "There is nothing inside it to await."),
                _q("A retry's `try` must use…",
                   ["return work()", "return await work()", "either", "throw"], 1,
                   "Or the rejection escapes the catch."),
                _q("A timeout built with `race`…",
                   ["cancels the slow work", "leaves the slow work running and discards its result",
                    "throws", "retries"], 1,
                   "Promises have no cancel."),
                _q("`Promise.withResolvers()` returns…",
                   ["a promise", "{ promise, resolve, reject }", "a callback", "void"], 1,
                   "For settling from outside."),
            ],
            exercises=[
                _ex("tscourse-w17-pat-1", "Retry until it works",
                    "Return the successful attempt from inside the try, so a rejection is caught and retried.",
                    'let attempts = 0;\n'
                    'async function flaky(): Promise<string> {\n'
                    '  attempts = attempts + 1;\n'
                    '  if (attempts < 3) {\n'
                    '    throw new Error(`attempt ${attempts} failed`);\n  }\n'
                    '  return `ok on attempt ${attempts}`;\n}\n'
                    'async function retry(times: number): Promise<string> {\n'
                    '  for (let i = 1; i <= times; i = i + 1) {\n'
                    '    try {\n'
                    '      return await flaky();\n'
                    '    } catch (err) {\n'
                    '      console.log(err instanceof Error ? err.message : "?");\n    }\n  }\n'
                    '  return "gave up";\n}\n'
                    'console.log(await retry(5));\n',
                    '      return await flaky();',
                    [("", "attempt 1 failed\nattempt 2 failed\nok on attempt 3")],
                    hints=["The promise has to settle inside the try, or the catch never sees the rejection.",
                           "Write return await flaky();"],
                    difficulty="Medium"),
                _ex("tscourse-w17-pat-2", "Give up, with the reason",
                    "Keep the last error so the final failure says something useful.",
                    'async function alwaysFails(n: number): Promise<string> {\n'
                    '  throw new Error(`attempt ${n} failed`);\n}\n'
                    'async function retry(times: number): Promise<string> {\n'
                    '  let last = "no attempts made";\n'
                    '  for (let i = 1; i <= times; i = i + 1) {\n'
                    '    try {\n'
                    '      return await alwaysFails(i);\n'
                    '    } catch (err) {\n'
                    '      last = err instanceof Error ? err.message : "failed";\n    }\n  }\n'
                    '  throw new Error(`gave up after ${times}: ${last}`);\n}\n'
                    'try {\n'
                    '  await retry(3);\n'
                    '} catch (err) {\n'
                    '  console.log(err instanceof Error ? err.message : "?");\n}\n',
                    '  throw new Error(`gave up after ${times}: ${last}`);',
                    [("", "gave up after 3: attempt 3 failed")],
                    hints=["After the loop, nothing has succeeded — say how many tries and what the last problem was.",
                           'Write throw new Error(`gave up after ${times}: ${last}`);'],
                    difficulty="Medium"),
                _ex("tscourse-w17-pat-3", "A timeout that is not a cliff",
                    "Race the work against a fallback value, so a slow call degrades instead of hanging.",
                    _AFTER +
                    'async function withTimeout<T>(work: Promise<T>, ms: number, fallback: T): Promise<T> {\n'
                    '  return Promise.race([work, after(ms, fallback)]);\n}\n'
                    'console.log(await withTimeout(after(1, "fast enough"), 50, "timed out"));\n'
                    'console.log(await withTimeout(after(60, "too slow"), 5, "timed out"));\n',
                    '  return Promise.race([work, after(ms, fallback)]);',
                    [("", "fast enough\ntimed out")],
                    hints=["Two promises in the race: the real work, and a timer carrying the fallback.",
                           "Write return Promise.race([work, after(ms, fallback)]);"],
                    difficulty="Medium"),
                _ex("tscourse-w17-pat-4", "A three-step pipeline",
                    "Each step needs the previous one's result. Await the parse between fetch and format.",
                    _AFTER +
                    'async function fetchPage(id: number): Promise<string> {\n'
                    '  return after(1, `  raw ${id}  `);\n}\n'
                    'async function parse(raw: string): Promise<string> {\n'
                    '  return after(1, raw.trim());\n}\n'
                    'function format(parsed: string): string {\n'
                    '  return `[${parsed}]`;\n}\n'
                    'async function pipeline(id: number): Promise<string> {\n'
                    '  const raw = await fetchPage(id);\n'
                    '  const parsed = await parse(raw);\n'
                    '  return format(parsed);\n}\n'
                    'console.log(await pipeline(7));\n',
                    '  const parsed = await parse(raw);', [("", "[raw 7]")],
                    hints=["Nothing here can overlap: parse needs what fetch returned.",
                           "Write const parsed = await parse(raw);"],
                    difficulty="Easy"),
                _ex("tscourse-w17-pat-5", "Settle it from outside",
                    "Take the promise and its resolver apart, so a callback elsewhere can settle it.",
                    'const { promise, resolve } = Promise.withResolvers<string>();\n'
                    'function onReady(handler: () => void): void {\n'
                    '  setTimeout(handler, 1);\n}\n'
                    'onReady(() => {\n'
                    '  resolve("ready");\n});\n'
                    'console.log(await promise);\n',
                    'const { promise, resolve } = Promise.withResolvers<string>();',
                    [("", "ready")],
                    hints=["Destructure the two members you need from the call.",
                           "Write const { promise, resolve } = Promise.withResolvers<string>();"],
                    difficulty="Medium"),
                _ex("tscourse-w17-pat-6", "Backoff, without measuring it",
                    "Wait a little longer before each retry. The transcript only shows the attempts — the delays are real but nothing prints a duration.",
                    _DELAY +
                    'let attempts = 0;\n'
                    'async function flaky(): Promise<string> {\n'
                    '  attempts = attempts + 1;\n'
                    '  if (attempts < 3) {\n'
                    '    throw new Error(`attempt ${attempts}`);\n  }\n'
                    '  return "succeeded";\n}\n'
                    'async function retry(times: number): Promise<string> {\n'
                    '  for (let i = 1; i <= times; i = i + 1) {\n'
                    '    try {\n'
                    '      return await flaky();\n'
                    '    } catch {\n'
                    '      await delay(i * 2);\n    }\n  }\n'
                    '  return "gave up";\n}\n'
                    'console.log(await retry(5));\n'
                    'console.log(`attempts: ${attempts}`);\n',
                    '      await delay(i * 2);', [("", "succeeded\nattempts: 3")],
                    hints=["The wait grows with the attempt number.",
                           "Write await delay(i * 2);"],
                    difficulty="Medium"),
                _fix("tscourse-w17-pat-fix1", "Fix the retry that retries nothing",
                     "`return work()` hands the promise back before it settles, so the `catch` never runs, the loop never goes round, and the first failure escapes as an unhandled rejection that kills the process.",
                     'let attempts = 0;\n'
                     'async function flaky(): Promise<string> {\n'
                     '  attempts = attempts + 1;\n'
                     '  if (attempts < 3) {\n'
                     '    throw new Error(`attempt ${attempts} failed`);\n  }\n'
                     '  return `ok on attempt ${attempts}`;\n}\n'
                     'async function retry(times: number): Promise<string> {\n'
                     '  for (let i = 1; i <= times; i = i + 1) {\n'
                     '    try {\n'
                     '      return flaky();\n'
                     '    } catch {\n'
                     '      continue;\n    }\n  }\n'
                     '  return "gave up";\n}\n'
                     'console.log(await retry(5));\n',
                     'let attempts = 0;\n'
                     'async function flaky(): Promise<string> {\n'
                     '  attempts = attempts + 1;\n'
                     '  if (attempts < 3) {\n'
                     '    throw new Error(`attempt ${attempts} failed`);\n  }\n'
                     '  return `ok on attempt ${attempts}`;\n}\n'
                     'async function retry(times: number): Promise<string> {\n'
                     '  for (let i = 1; i <= times; i = i + 1) {\n'
                     '    try {\n'
                     '      return await flaky();\n'
                     '    } catch {\n'
                     '      continue;\n    }\n  }\n'
                     '  return "gave up";\n}\n'
                     'console.log(await retry(5));\n',
                     [("", "ok on attempt 3")],
                     hints=["A retry loop that cannot see a failure is not a retry loop.",
                            "The promise must settle inside the `try` for the `catch` to fire.",
                            "Write return await flaky();"],
                     difficulty="Medium"),
                _fix("tscourse-w17-pat-fix2", "Fix the unbounded retry",
                     "`while (true)` with no counter is an outage amplifier: against something that is genuinely down it never stops. Bound it at the number of attempts the caller asked for, and say so when it gives up.",
                     'async function alwaysFails(): Promise<string> {\n'
                     '  throw new Error("down");\n}\n'
                     'async function retry(times: number): Promise<string> {\n'
                     '  while (true) {\n'
                     '    try {\n'
                     '      return await alwaysFails();\n'
                     '    } catch {\n'
                     '      continue;\n    }\n  }\n}\n'
                     'console.log(await retry(3));\n',
                     'async function alwaysFails(): Promise<string> {\n'
                     '  throw new Error("down");\n}\n'
                     'async function retry(times: number): Promise<string> {\n'
                     '  for (let i = 1; i <= times; i = i + 1) {\n'
                     '    try {\n'
                     '      return await alwaysFails();\n'
                     '    } catch {\n'
                     '      continue;\n    }\n  }\n'
                     '  return `gave up after ${times}`;\n}\n'
                     'console.log(await retry(3));\n',
                     [("", "gave up after 3")],
                     hints=["The starter never terminates — the judge times it out.",
                            "The parameter is there for a reason: use it as the loop bound.",
                            "After the loop, return a message naming how many attempts were made."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Adding a growing delay between retries is called…",
                   ["throttling", "backoff", "debouncing", "polling"], 1,
                   "And it is what stops a retry storm."),
                _q("To cancel work rather than discard its result, you need…",
                   ["Promise.cancel", "AbortController — promises themselves have no cancel",
                    "clearTimeout", "race"], 1,
                   "Worth looking up when you need it."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #17 — the paged loader",
        """
The ledger has outgrown one file. It now arrives in **pages**, one slow request
each, and some of those requests fail. Load them all **concurrently**, report
every page's outcome, and total the ones that worked.

Input: one line per page. A line is a space-separated list of `cents` values, or
the single word `ERR` for a page whose request fails.

```
325 90000
ERR
200 150
```

```
Page 1:   ok (2 entries)
Page 2:   failed (page 2 is unavailable)
Page 3:   ok (2 entries)
Loaded:   4 entries from 2 of 3 pages
Total:    $906.75
```

**What it has to do:**

1. `loadPage(index, line)` is `async` and returns the page's `readonly number[]`.
   It waits `(pages.length - index) * 8` milliseconds first — deliberately
   backwards, so the **last** page finishes **first** — and then either returns
   the parsed amounts or throws `new Error(\\`page N is unavailable\\`)` for an
   `ERR` line. N is the 1-based page number.
2. Start every page at once and wait for all of them with **`Promise.allSettled`**
   — not `all`, because one failed page must not cost you the others.
3. Print one line per page, **in page order**, whatever order they finished in.
4. Then the summary: how many entries loaded, from how many of how many pages,
   and the total formatted as dollars.

**Why `allSettled` and not `all`:** `all` rejects the moment page 2 throws, and
the two pages that worked are thrown away with it. `allSettled` reports every
outcome and never rejects — and its results come back in **argument order**,
which is what makes the output identical on every machine even though the pages
always complete in a different order.

Empty input prints `Loaded:   0 entries from 0 of 0 pages` and a zero total, with
no page lines at all.
""",
        _ch("tscourse-w17-capstone", "Budget Buddy #17", "Hard",
            "Load every page concurrently with `Promise.allSettled`, report each outcome in "
            "page order, and total what arrived.",
            _FS +
            'function delay(ms: number): Promise<void> {\n'
            '  return new Promise((resolve) => {\n'
            '    setTimeout(resolve, ms);\n  });\n}\n'
            'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
            'async function loadPage(index: number, line: string): Promise<readonly number[]> {\n'
            '  await delay((lines.length - index) * 8);\n'
            '  if (line.trim() === "ERR") {\n'
            '    throw new Error(`page ${index + 1} is unavailable`);\n  }\n'
            '  return line.trim().split(/\\s+/).map(Number);\n}\n'
            'const results = await Promise.allSettled(lines.map((line, i) => loadPage(i, line)));\n'
            'let entries = 0;\n'
            'let okPages = 0;\n'
            'let total = 0;\n'
            'for (let i = 0; i < results.length; i = i + 1) {\n'
            '  const r = results[i];\n'
            '  if (r === undefined) {\n'
            '    continue;\n  }\n'
            '  if (r.status === "fulfilled") {\n'
            '    okPages = okPages + 1;\n'
            '    entries = entries + r.value.length;\n'
            '    for (const cents of r.value) {\n'
            '      total = total + cents;\n    }\n'
            '    console.log(`Page ${i + 1}:   ok (${r.value.length} entries)`);\n'
            '  } else {\n'
            '    const why = r.reason instanceof Error ? r.reason.message : "unknown";\n'
            '    console.log(`Page ${i + 1}:   failed (${why})`);\n  }\n}\n'
            'console.log(`Loaded:   ${entries} entries from ${okPages} of ${results.length} pages`);\n'
            'console.log(`Total:    $${(total / 100).toFixed(2)}`);\n',
            'const results = await Promise.allSettled(lines.map((line, i) => loadPage(i, line)));\n'
            'let entries = 0;\n'
            'let okPages = 0;\n'
            'let total = 0;\n'
            'for (let i = 0; i < results.length; i = i + 1) {\n'
            '  const r = results[i];\n'
            '  if (r === undefined) {\n'
            '    continue;\n  }\n'
            '  if (r.status === "fulfilled") {\n'
            '    okPages = okPages + 1;\n'
            '    entries = entries + r.value.length;\n'
            '    for (const cents of r.value) {\n'
            '      total = total + cents;\n    }\n'
            '    console.log(`Page ${i + 1}:   ok (${r.value.length} entries)`);\n'
            '  } else {\n'
            '    const why = r.reason instanceof Error ? r.reason.message : "unknown";\n'
            '    console.log(`Page ${i + 1}:   failed (${why})`);\n  }\n}',
            [("325 90000\nERR\n200 150",
              "Page 1:   ok (2 entries)\nPage 2:   failed (page 2 is unavailable)\n"
              "Page 3:   ok (2 entries)\nLoaded:   4 entries from 2 of 3 pages\nTotal:    $906.75"),
             ("100 200 300",
              "Page 1:   ok (3 entries)\nLoaded:   3 entries from 1 of 1 pages\nTotal:    $6.00"),
             ("ERR\nERR",
              "Page 1:   failed (page 1 is unavailable)\nPage 2:   failed (page 2 is unavailable)\n"
              "Loaded:   0 entries from 0 of 2 pages\nTotal:    $0.00"),
             ("", "Loaded:   0 entries from 0 of 0 pages\nTotal:    $0.00"),
             ("1\n2\n3\n4",
              "Page 1:   ok (1 entries)\nPage 2:   ok (1 entries)\nPage 3:   ok (1 entries)\n"
              "Page 4:   ok (1 entries)\nLoaded:   4 entries from 4 of 4 pages\nTotal:    $0.10")],
            hints=["`lines.map((line, i) => loadPage(i, line))` starts every page at once — the map's index is the page number minus one.",
                   "`Promise.allSettled` never rejects, so there is no try/catch around it at all.",
                   "Walk the results by index: the index IS the page number minus one, and the results are in argument order.",
                   "Narrow each result on `r.status` before touching `.value` or `.reason` — it is a discriminated union.",
                   "Under noUncheckedIndexedAccess, `results[i]` is possibly undefined; skip it rather than asserting.",
                   "The reason is `unknown`, so narrow it with `instanceof Error` before reading `.message`.",
                   "Nothing in the program prints a duration, and nothing prints from inside a callback."]),
        example_io="Page 1:   ok (2 entries)\nPage 2:   failed (page 2 is unavailable)\nPage 3:   ok (2 entries)\nLoaded:   4 entries from 2 of 3 pages\nTotal:    $906.75",
        rubric=["every page is started before any is awaited — the loads are concurrent, not sequential",
                "`Promise.allSettled` is used, so one failed page does not cost the others",
                "output is in page order, never completion order",
                "each result is narrowed on `.status` before `.value` or `.reason` is read",
                "the rejection reason is narrowed with `instanceof Error`",
                "no index access is asserted with `!`",
                "nothing prints an elapsed time",
                "empty input prints the summary and no page lines"],
        stretch=_ch("tscourse-w17-capstone-stretch", "Budget Buddy #17 (stretch)", "Hard",
                    "Give each page a deadline. A page whose request takes longer than 20 ms is "
                    "reported as `timed out` rather than waited for — so a single slow page cannot "
                    "hold up the report. Use `Promise.race` per page, and keep `allSettled` for the "
                    "set. A line of `SLOW` is a page that takes 60 ms; everything else takes 1 ms.",
                    _FS +
                    'function after<T>(ms: number, value: T): Promise<T> {\n'
                    '  return new Promise((resolve) => {\n'
                    '    setTimeout(() => resolve(value), ms);\n  });\n}\n'
                    'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
                    'type PageResult =\n'
                    '  | { readonly kind: "ok"; readonly cents: readonly number[] }\n'
                    '  | { readonly kind: "late" };\n'
                    'async function loadPage(line: string): Promise<readonly number[]> {\n'
                    '  const text = line.trim();\n'
                    '  if (text === "SLOW") {\n'
                    '    return after(60, []);\n  }\n'
                    '  return after(1, text.split(/\\s+/).map(Number));\n}\n'
                    'async function loadWithDeadline(line: string, ms: number): Promise<PageResult> {\n'
                    '  const work: Promise<PageResult> = loadPage(line).then((cents) => ({\n'
                    '    kind: "ok" as const,\n    cents,\n  }));\n'
                    '  return Promise.race([work, after<PageResult>(ms, { kind: "late" })]);\n}\n'
                    'const results = await Promise.allSettled(lines.map((l) => loadWithDeadline(l, 20)));\n'
                    'let total = 0;\n'
                    'let late = 0;\n'
                    'for (let i = 0; i < results.length; i = i + 1) {\n'
                    '  const r = results[i];\n'
                    '  if (r === undefined || r.status === "rejected") {\n'
                    '    continue;\n  }\n'
                    '  if (r.value.kind === "late") {\n'
                    '    late = late + 1;\n'
                    '    console.log(`Page ${i + 1}:   timed out`);\n'
                    '    continue;\n  }\n'
                    '  for (const cents of r.value.cents) {\n'
                    '    total = total + cents;\n  }\n'
                    '  console.log(`Page ${i + 1}:   ok (${r.value.cents.length} entries)`);\n}\n'
                    'console.log(`Late:     ${late}`);\n'
                    'console.log(`Total:    $${(total / 100).toFixed(2)}`);\n',
                    'async function loadWithDeadline(line: string, ms: number): Promise<PageResult> {\n'
                    '  const work: Promise<PageResult> = loadPage(line).then((cents) => ({\n'
                    '    kind: "ok" as const,\n    cents,\n  }));\n'
                    '  return Promise.race([work, after<PageResult>(ms, { kind: "late" })]);\n}',
                    [("325 90000\nSLOW\n200",
                      "Page 1:   ok (2 entries)\nPage 2:   timed out\nPage 3:   ok (1 entries)\n"
                      "Late:     1\nTotal:    $905.25"),
                     ("SLOW\nSLOW", "Page 1:   timed out\nPage 2:   timed out\nLate:     2\nTotal:    $0.00"),
                     ("100", "Page 1:   ok (1 entries)\nLate:     0\nTotal:    $1.00")],
                    hints=["Race the real work against a timer carrying the `late` member of the union.",
                           "The work's promise has to be mapped into the union first, so both sides of the race have the same type.",
                           "`after<PageResult>(ms, { kind: \"late\" })` pins the type argument so the race resolves to PageResult.",
                           "The slow page keeps running and its result is discarded — a race cancels nothing."]),
    ),
))
