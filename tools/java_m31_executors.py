# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 31 - Executors, tasks and results.  Closes Part 10.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# `ExecutorService`, `Executors.`, `Callable`, `Future` and the concurrent
# collections become legal here and nowhere earlier. Modules 29 and 30 managed
# threads by hand on purpose, so this module has something concrete to replace:
# every `new Thread(...)` / `start()` / `join()` trio becomes a submit and a get.
#
# THE JUDGING PROBLEM, AND HOW THIS MODULE SOLVES IT
# --------------------------------------------------
# A pool decides for itself which thread runs which task and in what order, so
# the determinism rules are stricter here than anywhere else in the course:
#
#   1. RESULTS ARE READ IN SUBMISSION ORDER. Keep the `List<Future<T>>` and
#      `get()` them in order, or use `invokeAll`, which returns its futures in
#      the order of the argument list whatever order the tasks actually ran in.
#      This is the module's central pattern and its central lesson.
#   2. TASKS DO NOT PRINT - with one exception: a single-thread executor, which
#      is documented to run tasks sequentially in submission order.
#   3. MAPS AND SETS ARE PRINTED THROUGH A TreeMap / sorted keys. A
#      ConcurrentHashMap's iteration order is unspecified, exactly as a
#      HashMap's is (module 27's rule, unchanged).
#   4. POOL THREAD NAMES ARE NEVER PRINTED. `pool-1-thread-3` depends on which
#      worker picked the task up.
#
# The one slow exercise is deliberate: `j31-shut-missing` ships a starter that
# never calls `shutdown()`, so the JVM hangs on its non-daemon pool threads and
# the verifier kills it at the 20-second timeout. That counts as the starter
# failing, which is what `--starters` wants, and it is the single most common
# real-world mistake with an ExecutorService - worth one slow case.
# ---------------------------------------------------------------------------

_M31 = []

_IMPORTS31 = ("import java.util.*;\n"
              "import java.util.concurrent.*;\n")

# `Future.get` throws both of these, and `invokeAll` throws the first.
_SIG31 = ("    public static void main(String[] args)\n"
          "            throws InterruptedException, ExecutionException {")


def _j31s(body):
    """A Scanner-opening main that may submit, get and await."""
    return _jcls(
        _SIG31 + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }",
        imports=_IMPORTS31,
    )


def _j31t(types, body):
    """Helper CLASSES above Main, then a Scanner-opening main."""
    return _jp(
        _IMPORTS31 + "\n"
        + types.rstrip("\n") + "\n\n"
        + "public class Main {\n"
        + _SIG31 + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }\n}"
    )


_K31 = (1, 2, 3, 4, 5)
_A31 = ([3, 1, 2], [5], [4, 4, 4, 4], [10, -2, 7], [1, 2, 3, 4, 5, 6])
_W31 = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"],
        ["pear", "fig", "plum"], ["alpha", "beta", "gamma", "d"])

_RD_W31 = ("        int n = sc.nextInt();\n"
           "        String[] words = new String[n];\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words[i] = sc.next();\n"
           "        }\n")


def _k31(k, out):
    return _case(str(k), out)


def _w31(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


# ===========================================================================
# 31.1 The pool
# ===========================================================================

_M31.append(_jlesson(
    "m31-pool", "Tasks, not threads",
    "Stop creating threads. Hand work to something that already has them.",
    """
Modules 29 and 30 created a thread per piece of work. That is fine for five
pieces of work and wrong for fifty thousand:

* a thread reserves a stack - roughly half a megabyte of address space each - so
  ten thousand of them is gigabytes before a single line of your code runs;
* creating and destroying one costs far more than the small task you gave it;
* nothing limits how many exist, so a burst of load creates a burst of threads
  and the machine spends its time switching between them instead of working.

The fix is to separate **what** from **who**: your code produces *tasks*, and a
pool of already-existing threads consumes them.

```java
ExecutorService pool = Executors.newFixedThreadPool(4);

pool.execute(() -> System.out.println("work"));   // hand over a Runnable

pool.shutdown();                                  // no new tasks accepted
pool.awaitTermination(1, TimeUnit.MINUTES);       // wait for the queued ones
```

The pool keeps its threads alive between tasks and feeds them from a queue.
Twenty thousand tasks on four threads is four threads.

## The factory methods

```java
Executors.newFixedThreadPool(n)    // exactly n threads, an unbounded queue
Executors.newSingleThreadExecutor()// exactly 1 - tasks run in SUBMISSION ORDER
Executors.newCachedThreadPool()    // grows as needed, reuses idle threads,
                                   // discards them after 60s. Unbounded: careful.
Executors.newVirtualThreadPerTaskExecutor()   // Java 21+, a virtual thread each
```

`newFixedThreadPool` is the default worth reaching for: the whole point is a
*bound* on concurrency, and it is the only one of the first three that gives you
one.

**`newSingleThreadExecutor` is the exception this course exploits**: with one
thread and a FIFO queue, tasks run one at a time in the order you submitted
them, so its output is completely predictable. That is why it is the only place
in Part 10 where a task is allowed to print.

## `execute` versus `submit`

```java
pool.execute(runnable);              // fire and forget. Returns void.
Future<?> f = pool.submit(runnable); // returns a handle; f.get() gives null
Future<Integer> g = pool.submit(callable);  // returns a handle to the RESULT
```

`execute` takes only a `Runnable` and gives you nothing back - including no way
to find out that the task threw. `submit` gives you a `Future`, which is the
next lesson and the reason to prefer it.
""",
    warmup=[
        _jq("A thread pool exists mainly to…",
            ["bound how many threads exist, and reuse them across many tasks",
             "make each task faster",
             "avoid needing synchronization",
             "run tasks in order"],
            0,
            "Separating tasks from threads is the whole idea."),
        _jq("`Executors.newSingleThreadExecutor()` runs submitted tasks…",
            ["one at a time, in submission order",
             "in any order", "in parallel on one core", "in reverse order"],
            0,
            "Which is exactly why its output is predictable."),
    ],
    exercises=[
        _jch("j31-pool-fixed", "A pool, and a slot each", "Medium",
             "Read `k` and hand the pool `k` tasks, task `i` writing `i * i` into "
             "`parts[i]`. Shut the pool down, wait for it, then print the slots in index "
             "order and their total. Replace `____` with the pool, the submissions and "
             "the shutdown.",
             _j31s("        int k = sc.nextInt();\n"
                   "        int[] parts = new int[k];\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int idx = i;\n"
                   "            pool.execute(() -> parts[idx] = idx * idx);\n"
                   "        }\n"
                   "        pool.shutdown();\n"
                   "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
                   "        int total = 0;\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            System.out.println(i + \" \" + parts[i]);\n"
                   "            total += parts[i];\n"
                   "        }\n"
                   "        System.out.println(total);"),
             "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            final int idx = i;\n"
             "            pool.execute(() -> parts[idx] = idx * idx);\n"
             "        }\n"
             "        pool.shutdown();\n"
             "        pool.awaitTermination(1, TimeUnit.MINUTES);",
             [_k31(k, _nl(*([f"{i} {i * i}" for i in range(k)]
                            + [sum(i * i for i in range(k))]))) for k in _K31],
             hints=["Two pool threads can serve any number of tasks - `k` may be far "
                    "larger than 2.",
                    "`final int idx = i;` before the lambda, exactly as with raw threads.",
                    "Each task owns its own slot, so there is nothing to synchronise.",
                    "`shutdown()` stops new submissions; `awaitTermination` waits for the "
                    "queued ones to finish.",
                    "Together they are this module's replacement for module 29's join "
                    "loop.",
                    "Main prints after the wait, in index order - so the pool's scheduling "
                    "cannot show through."]),

        _je("j31-pool-single", "One thread, in order",
            "A single-thread executor runs tasks one at a time in submission order, so "
            "here - uniquely in Part 10 - the tasks may print for themselves. Submit `k` "
            "tasks that each print their index, then `done`. Replace `____` with the "
            "executor.",
            _j31s("        int k = sc.nextInt();\n"
                  "        ExecutorService pool = Executors.newSingleThreadExecutor();\n"
                  "        for (int i = 0; i < k; i++) {\n"
                  "            final int idx = i;\n"
                  "            pool.execute(() -> System.out.println(\"task \" + idx));\n"
                  "        }\n"
                  "        pool.shutdown();\n"
                  "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
                  "        System.out.println(\"done\");"),
            "        ExecutorService pool = Executors.newSingleThreadExecutor();",
            [_k31(k, _nl(*([f"task {i}" for i in range(k)] + ["done"]))) for k in _K31],
            hints=["`Executors.newSingleThreadExecutor()` takes no argument.",
                   "One thread and a FIFO queue means one task at a time, in order.",
                   "Swap in `newFixedThreadPool(2)` and this output stops being "
                   "predictable at all.",
                   "`done` prints last because `awaitTermination` came first.",
                   "This is the only place in the module where a task prints - everywhere "
                   "else, main does."],
            difficulty="Easy"),

        _jch("j31-pool-submit", "`execute` gives you nothing back", "Medium",
             "`submit` hands you a `Future`. For a `Runnable` there is no result, so "
             "`get()` returns `null` - but it still blocks until the task is done, and "
             "still reports failure. Submit one Runnable, print what its `get()` returns, "
             "then the slot it wrote. Replace `____` with the submit and the get.",
             _j31s("        int k = sc.nextInt();\n"
                   "        int[] out = new int[1];\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
                   "        Future<?> handle = pool.submit(() -> {\n"
                   "            out[0] = k * 3;\n"
                   "        });\n"
                   "        System.out.println(handle.get());\n"
                   "        System.out.println(out[0]);\n"
                   "        pool.shutdown();"),
             "        Future<?> handle = pool.submit(() -> {\n"
             "            out[0] = k * 3;\n"
             "        });\n"
             "        System.out.println(handle.get());",
             [_k31(k, _nl("null", k * 3)) for k in _K31],
             hints=["`submit(Runnable)` returns a `Future<?>` - the wildcard because there "
                    "is no result type.",
                    "`get()` blocks until the task finishes, then returns `null`, which "
                    "prints as the four letters `null`.",
                    "The braced body matters. `submit` is overloaded, and an assignment "
                    "is an EXPRESSION with a value, so `() -> out[0] = k * 3` is a valid "
                    "`Callable<Integer>` and would return 3.",
                    "Wrapping the statement in braces makes the lambda void-compatible "
                    "only, so the `Runnable` overload is the one that applies.",
                    "So the get is doing the job `join()` did in module 29.",
                    "`execute` would give you no handle at all - and no way to learn the "
                    "task had failed."]),

        _jch("j31-pool-morethanthreads", "More tasks than threads", "Medium",
             "A pool of two threads, given `k` tasks: they queue up and are served as "
             "threads come free. Each task writes `i + 1` into its own slot. Print the "
             "slots and the total after the pool has drained. Replace `____` with the "
             "pool and the submission loop.",
             _j31s("        int k = sc.nextInt();\n"
                   "        int[] parts = new int[k];\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int idx = i;\n"
                   "            pool.execute(() -> parts[idx] = idx + 1);\n"
                   "        }\n"
                   "        pool.shutdown();\n"
                   "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
                   "        int total = 0;\n"
                   "        for (int p : parts) {\n"
                   "            total += p;\n"
                   "        }\n"
                   "        System.out.println(k);\n"
                   "        System.out.println(total);"),
             "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            final int idx = i;\n"
             "            pool.execute(() -> parts[idx] = idx + 1);\n"
             "        }",
             [_k31(k, _nl(k, k * (k + 1) // 2)) for k in _K31],
             hints=["The number of tasks and the number of threads are unrelated - that is "
                    "the point of a pool.",
                    "Tasks beyond the second wait in the pool's queue.",
                    "With raw threads, `k` tasks meant `k` threads; here it means two.",
                    "Nothing about WHICH thread ran WHICH task is observable, and nothing "
                    "here depends on it.",
                    "The total is 1 + 2 + ... + k."]),
    ],
    quiz=[
        _jq("`newCachedThreadPool` is risky under load because…",
            ["it is unbounded - it will create as many threads as there are tasks",
             "it is slow", "it never reuses threads",
             "it runs tasks out of order"],
            0,
            "A fixed pool gives you the bound that was the whole reason to pool."),
        _jq("`pool.execute(runnable)` returns…",
            ["void - no handle, and no way to learn the task threw",
             "a Future", "a Thread", "a boolean"],
            0,
            "`submit` is the one that hands you something back."),
    ],
))


# ===========================================================================
# 31.2 Callable and Future
# ===========================================================================

_M31.append(_jlesson(
    "m31-callable", "`Callable` and `Future`",
    "A task that can return a value and can fail - and the handle you collect both from.",
    """
`Runnable` has been quietly limiting you for two modules:

```java
public interface Runnable {
    void run();                 // returns NOTHING, throws NO checked exception
}
```

That is why every worker so far has written into an array slot: there was no
other way to get an answer out. And it is why every `Thread.sleep` inside a task
needed its own try/catch - `run()` cannot declare `throws`.

`Callable<V>` fixes both:

```java
public interface Callable<V> {
    V call() throws Exception;  // returns a V, and MAY throw anything
}
```

It is a functional interface too, so a lambda is one.

```java
Future<Integer> f = pool.submit(() -> 6 * 7);
System.out.println(f.get());        // 42
```

## `Future` is a receipt

`submit` returns immediately, before the task has run. The `Future` is your
claim on the eventual answer:

```java
f.get()                  // BLOCKS until the result exists, then returns it
f.get(2, TimeUnit.SECONDS)  // ...or throws TimeoutException
f.isDone()               // finished, failed or cancelled - true either way
f.cancel(true)           // ask to stop; true means interrupt it if running
f.isCancelled()
```

`get()` is this module's `join()`, and it publishes exactly as `join()` did:
whatever the task wrote before returning is visible to you afterwards.

## Failure is delivered, not lost

This is the real reason to prefer `submit` over `execute`. If a task throws, the
exception is captured and re-thrown to you, wrapped:

```java
Future<Integer> f = pool.submit(() -> { throw new IllegalStateException("nope"); });
try {
    f.get();
} catch (ExecutionException e) {
    System.out.println(e.getCause().getMessage());   // "nope"
}
```

**`ExecutionException` always wraps.** The thing you actually care about is
`e.getCause()`. And note when it surfaces: not when the task fails, but when
somebody calls `get()`. A task submitted with `execute`, or with `submit` and
never got, can fail completely silently - which is how exceptions disappear in
production.

`get()` also throws `InterruptedException`, because waiting can be interrupted -
so a `get()` sits in a method that declares both, or in a try/catch for both.
""",
    warmup=[
        _jq("`Callable<V>` differs from `Runnable` in that…",
            ["it returns a value and may throw a checked exception",
             "it is faster", "it cannot be a lambda",
             "it runs on the calling thread"],
            0,
            "Which removes both of the workarounds modules 29-30 needed."),
        _jq("A task throwing inside `submit` surfaces…",
            ["as an ExecutionException from `get()`, wrapping the real exception",
             "immediately, on the main thread", "as a printed stack trace only",
             "not at all, ever"],
            0,
            "If nobody calls get(), nobody finds out."),
    ],
    exercises=[
        _je("j31-call-value", "A task that returns something",
            "A `Callable<Integer>` hands its answer back through the `Future` instead of "
            "an array slot. Submit one that returns `k * k` and print the result. Replace "
            "`____` with the submission.",
            _j31s("        int k = sc.nextInt();\n"
                  "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
                  "        Future<Integer> answer = pool.submit(() -> k * k);\n"
                  "        System.out.println(answer.get());\n"
                  "        pool.shutdown();"),
            "        Future<Integer> answer = pool.submit(() -> k * k);",
            [_k31(k, str(k * k)) for k in _K31],
            hints=["`Callable<V>` is a functional interface, so a lambda returning a value "
                   "is one.",
                   "The lambda's body is an expression, so no braces and no `return` are "
                   "needed.",
                   "The target type `Future<Integer>` is what tells the compiler this is a "
                   "`Callable<Integer>` and not a `Runnable`.",
                   "`answer.get()` blocks until the value exists.",
                   "No array slot, no join - the result comes back through the return "
                   "type, as it should."],
            difficulty="Easy"),

        _jch("j31-call-throws", "Failure comes back wrapped", "Hard",
             "A `Callable` that throws does not crash the pool - the exception is stored "
             "and handed to whoever calls `get()`, wrapped in an `ExecutionException`. "
             "Submit a task that throws `IllegalStateException(\"task \" + k + \" failed\")`, "
             "catch the wrapper, and print the CAUSE's message, then its simple class "
             "name. Replace `____` with the submit and the try/catch.",
             _j31s("        int k = sc.nextInt();\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
                   "        Future<Integer> answer = pool.submit(() -> {\n"
                   "            throw new IllegalStateException(\"task \" + k + \" failed\");\n"
                   "        });\n"
                   "        try {\n"
                   "            System.out.println(answer.get());\n"
                   "        } catch (ExecutionException e) {\n"
                   "            System.out.println(e.getCause().getMessage());\n"
                   "            System.out.println(e.getCause().getClass().getSimpleName());\n"
                   "        }\n"
                   "        pool.shutdown();\n"
                   "        System.out.println(\"pool still fine\");"),
             "        Future<Integer> answer = pool.submit(() -> {\n"
             "            throw new IllegalStateException(\"task \" + k + \" failed\");\n"
             "        });\n"
             "        try {\n"
             "            System.out.println(answer.get());\n"
             "        } catch (ExecutionException e) {\n"
             "            System.out.println(e.getCause().getMessage());\n"
             "            System.out.println(e.getCause().getClass().getSimpleName());\n"
             "        }",
             [_k31(k, _nl(f"task {k} failed", "IllegalStateException",
                          "pool still fine")) for k in _K31],
             hints=["A lambda whose body only throws is still a `Callable<Integer>` - it "
                    "just never reaches a return.",
                    "`get()` is where the failure is delivered, not `submit()`.",
                    "`ExecutionException` is a wrapper; the interesting object is "
                    "`e.getCause()`.",
                    "So the message you want is `e.getCause().getMessage()`.",
                    "`getClass().getSimpleName()` on the cause gives "
                    "`IllegalStateException`.",
                    "The print inside the try never runs, and the pool survives - one bad "
                    "task does not poison it."]),

        _jch("j31-call-isdone", "The receipt after the fact", "Medium",
             "`isDone()` is only worth asking once you know the answer - before that it is "
             "a snapshot of something still moving. Submit a Callable, `get()` it, then "
             "report `isDone` and `isCancelled`. Replace `____` with the submit, the get "
             "and the two reports.",
             _j31s("        int k = sc.nextInt();\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
                   "        Future<Integer> answer = pool.submit(() -> k + 100);\n"
                   "        System.out.println(answer.get());\n"
                   "        System.out.println(answer.isDone());\n"
                   "        System.out.println(answer.isCancelled());\n"
                   "        pool.shutdown();"),
             "        Future<Integer> answer = pool.submit(() -> k + 100);\n"
             "        System.out.println(answer.get());\n"
             "        System.out.println(answer.isDone());\n"
             "        System.out.println(answer.isCancelled());",
             [_k31(k, _nl(k + 100, "true", "false")) for k in _K31],
             hints=["`get()` blocks, so everything after it knows the task has finished.",
                    "`isDone()` is therefore `true` - and would be true for a failed or "
                    "cancelled task too.",
                    "`isCancelled()` is `false`: nobody cancelled this one.",
                    "Asking `isDone()` BEFORE the get would be a race with the pool, and "
                    "is not something to assert on.",
                    "This mirrors module 29: NEW and TERMINATED were assertable, the "
                    "middle was not."]),

        _jfix("j31-call-execute", "`execute` cannot return a value",
              "This wants the task's result but uses `execute`, which takes a `Runnable` "
              "and returns `void` - so there is nothing to read and the code does not "
              "compile. Switch to `submit` with a `Callable` and read the answer from the "
              "`Future`.",
              _j31s("        int k = sc.nextInt();\n"
                    "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
                    "        Future<Integer> answer = pool.execute(() -> k * 2);\n"
                    "        System.out.println(answer.get());\n"
                    "        pool.shutdown();"),
              _j31s("        int k = sc.nextInt();\n"
                    "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
                    "        Future<Integer> answer = pool.submit(() -> k * 2);\n"
                    "        System.out.println(answer.get());\n"
                    "        pool.shutdown();"),
              [_k31(k, str(k * 2)) for k in _K31],
              hints=["`execute` is declared `void execute(Runnable)`.",
                     "There is no overload of it that takes a `Callable`.",
                     "`submit` has both: one for `Runnable`, one for `Callable<V>`.",
                     "Only the one-word change is needed - the lambda is already a "
                     "`Callable<Integer>`.",
                     "Prefer `submit` by default: it is also the only way to find out that "
                     "a task threw."],
              difficulty="Easy"),
    ],
    quiz=[
        _jq("`ExecutionException.getCause()` returns…",
            ["the exception the task actually threw",
             "the ExecutionException itself", "null", "an InterruptedException"],
            0,
            "The wrapper is plumbing; the cause is the news."),
        _jq("A task submitted with `execute` that throws…",
            ["fails silently as far as your code is concerned - there is no handle to ask",
             "crashes the pool", "is retried",
             "throws on the main thread"],
            0,
            "Which is the strongest argument for submit over execute."),
    ],
))


# ===========================================================================
# 31.3 Ordered results
# ===========================================================================

_M31.append(_jlesson(
    "m31-results", "Collecting results in order",
    "The tasks finish in whatever order they like. Your answers do not have to.",
    """
This is the pattern that makes concurrent code testable, and it is one idea:
**keep the futures in the order you submitted them, and `get()` them in that
order.**

```java
List<Future<Integer>> futures = new ArrayList<>();
for (int i = 0; i < k; i++) {
    final int idx = i;
    futures.add(pool.submit(() -> compute(idx)));      // submission order
}
for (Future<Integer> f : futures) {
    System.out.println(f.get());                       // ...is output order
}
```

Task 3 may well finish before task 0. It does not matter: the second loop asks
for task 0 first and blocks until it has it. The *work* is concurrent, the
*answers* are ordered - which is module 29's slot-per-worker pattern with the
slots managed for you.

Compare the alternative, which people write and then cannot test:

```java
List<Integer> results = new ArrayList<>();
pool.execute(() -> results.add(compute(idx)));   // WRONG twice over
```

`ArrayList` is not thread-safe, so concurrent `add`s can corrupt it outright -
and even with a thread-safe list, the *order* would be completion order, which
is to say arbitrary.

## `invokeAll`

When you have all the tasks up front, there is a single call that submits them,
waits for every one, and hands back the futures:

```java
List<Callable<Integer>> tasks = ...;
List<Future<Integer>> done = pool.invokeAll(tasks);   // blocks until ALL finish
for (Future<Integer> f : done) System.out.println(f.get());
```

The guarantee that matters: **the returned list is in the same order as the
argument list.** Not completion order. So `invokeAll` plus an in-order walk is
the whole pattern in two lines, and every `get()` afterwards returns
immediately, since everything is already finished.

`invokeAny` is the other one: it returns the result of whichever task finishes
first and cancels the rest. Useful for "ask three mirrors, take the fastest";
useless when you need every answer.
""",
    warmup=[
        _jq("`invokeAll` returns its futures…",
            ["in the order of the task list you passed in",
             "in completion order", "in a random order",
             "sorted by result"],
            0,
            "Which is exactly what makes the output reproducible."),
        _jq("Having tasks add their results to a shared `ArrayList` is wrong because…",
            ["ArrayList is not thread-safe, AND the order would be completion order",
             "it is slower", "ArrayList cannot hold Integers",
             "the list would be empty"],
            0,
            "Two separate bugs, either of which is fatal."),
    ],
    exercises=[
        _jch("j31-res-inorder", "Futures in a list", "Medium",
             "Read `k`, submit `k` Callables where task `i` returns `i * 10`, keeping "
             "every `Future` in a list in submission order. Then walk the list and print "
             "`index value`, followed by the total. Replace `____` with the submission "
             "loop and the collection loop.",
             _j31s("        int k = sc.nextInt();\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                   "        List<Future<Integer>> futures = new ArrayList<>();\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int idx = i;\n"
                   "            futures.add(pool.submit(() -> idx * 10));\n"
                   "        }\n"
                   "        int total = 0;\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            int value = futures.get(i).get();\n"
                   "            System.out.println(i + \" \" + value);\n"
                   "            total += value;\n"
                   "        }\n"
                   "        pool.shutdown();\n"
                   "        System.out.println(total);"),
             "        for (int i = 0; i < k; i++) {\n"
             "            final int idx = i;\n"
             "            futures.add(pool.submit(() -> idx * 10));\n"
             "        }\n"
             "        int total = 0;\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            int value = futures.get(i).get();\n"
             "            System.out.println(i + \" \" + value);\n"
             "            total += value;\n"
             "        }",
             [_k31(k, _nl(*([f"{i} {i * 10}" for i in range(k)]
                            + [sum(i * 10 for i in range(k))]))) for k in _K31],
             hints=["The list is `List<Future<Integer>>` - handles, not answers.",
                    "Adding in the submission loop is what fixes the order.",
                    "`futures.get(i).get()` is two different `get`s: the list's, then the "
                    "future's.",
                    "The second loop blocks on task 0 first even if task 3 finished long "
                    "ago.",
                    "`int value = ...get();` unboxes the `Integer` - module 17's "
                    "autoboxing, still applying.",
                    "The tasks run concurrently; the printing is strictly in index "
                    "order."]),

        _jch("j31-res-invokeall", "One call, every answer", "Medium",
             "Build a `List<Callable<Integer>>` where task `i` returns `i + 1`, hand the "
             "whole list to `invokeAll`, and print each result in order then the total. "
             "`invokeAll` blocks until every task is finished, so the `get()`s return "
             "instantly. Replace `____` with the task list, the invokeAll and the walk.",
             _j31s("        int k = sc.nextInt();\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                   "        List<Callable<Integer>> tasks = new ArrayList<>();\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int idx = i;\n"
                   "            tasks.add(() -> idx + 1);\n"
                   "        }\n"
                   "        List<Future<Integer>> done = pool.invokeAll(tasks);\n"
                   "        int total = 0;\n"
                   "        for (Future<Integer> f : done) {\n"
                   "            int value = f.get();\n"
                   "            System.out.println(value);\n"
                   "            total += value;\n"
                   "        }\n"
                   "        pool.shutdown();\n"
                   "        System.out.println(total);"),
             "        List<Callable<Integer>> tasks = new ArrayList<>();\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            final int idx = i;\n"
             "            tasks.add(() -> idx + 1);\n"
             "        }\n"
             "        List<Future<Integer>> done = pool.invokeAll(tasks);\n"
             "        int total = 0;\n"
             "        for (Future<Integer> f : done) {\n"
             "            int value = f.get();\n"
             "            System.out.println(value);\n"
             "            total += value;\n"
             "        }",
             [_k31(k, _nl(*([str(i + 1) for i in range(k)]
                            + [sum(i + 1 for i in range(k))]))) for k in _K31],
             hints=["The list holds `Callable<Integer>` - the tasks themselves, not "
                    "futures.",
                    "A lambda returning a value IS a `Callable<Integer>` here, because the "
                    "list's element type says so.",
                    "`invokeAll` submits everything and blocks until all of it is done.",
                    "Its returned list is in ARGUMENT order, not completion order - that "
                    "is the guarantee being used.",
                    "So the enhanced `for` walks the answers in the order the tasks were "
                    "built.",
                    "The total is 1 + 2 + ... + k."]),

        _jch("j31-res-chunks", "A chunked sum, with futures", "Hard",
             "Module 29's capstone, rewritten. Read `n` values then `k`; give chunk `i` - "
             "indices `[i*n/k, (i+1)*n/k)` - to its own `Callable<Integer>`, collect with "
             "`invokeAll`, and print `index sum` per chunk followed by the grand total. "
             "No array of partial results and no joins. Replace `____` with the tasks and "
             "the collection.",
             _j31s("        int n = sc.nextInt();\n"
                   "        int[] a = new int[n];\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            a[i] = sc.nextInt();\n"
                   "        }\n"
                   "        int k = sc.nextInt();\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                   "        List<Callable<Integer>> tasks = new ArrayList<>();\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int from = i * n / k;\n"
                   "            final int to = (i + 1) * n / k;\n"
                   "            tasks.add(() -> {\n"
                   "                int sum = 0;\n"
                   "                for (int j = from; j < to; j++) {\n"
                   "                    sum += a[j];\n"
                   "                }\n"
                   "                return sum;\n"
                   "            });\n"
                   "        }\n"
                   "        List<Future<Integer>> done = pool.invokeAll(tasks);\n"
                   "        int total = 0;\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            int part = done.get(i).get();\n"
                   "            System.out.println(i + \" \" + part);\n"
                   "            total += part;\n"
                   "        }\n"
                   "        pool.shutdown();\n"
                   "        System.out.println(total);"),
             "        List<Callable<Integer>> tasks = new ArrayList<>();\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            final int from = i * n / k;\n"
             "            final int to = (i + 1) * n / k;\n"
             "            tasks.add(() -> {\n"
             "                int sum = 0;\n"
             "                for (int j = from; j < to; j++) {\n"
             "                    sum += a[j];\n"
             "                }\n"
             "                return sum;\n"
             "            });\n"
             "        }\n"
             "        List<Future<Integer>> done = pool.invokeAll(tasks);\n"
             "        int total = 0;\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            int part = done.get(i).get();\n"
             "            System.out.println(i + \" \" + part);\n"
             "            total += part;\n"
             "        }",
             [_akcase(a, k, _nl(*([f"{i} {sum(a[i * len(a) // k:(i + 1) * len(a) // k])}"
                                   for i in range(k)] + [sum(a)])))
              for (a, k) in ((_A31[0], 3), (_A31[1], 1), (_A31[2], 2),
                             (_A31[3], 2), (_A31[4], 4))],
             hints=["The chunk bounds are the same as module 29's: `i*n/k` and "
                    "`(i+1)*n/k`.",
                    "Copy them into `final` locals so the lambda can capture them.",
                    "The lambda needs a braced body and an explicit `return sum;` - that "
                    "return is what makes it a Callable.",
                    "Compare with module 29: no `int[] parts`, no `Thread[]`, no join "
                    "loop.",
                    "`done.get(i)` is the list's get; `.get()` on that is the future's.",
                    "An empty chunk returns 0, which is correct and needs no special "
                    "case."]),

        _jch("j31-res-slots", "When you want them somewhere else", "Medium",
             "Futures are not always the right container - sometimes you want the answers "
             "in an array you already have. Submit `k` tasks writing `i * i * i` into "
             "`parts[i]`, keep the futures only to wait on, then print the array. Replace "
             "`____` with the submission loop and the waiting loop.",
             _j31s("        int k = sc.nextInt();\n"
                   "        int[] parts = new int[k];\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                   "        List<Future<?>> futures = new ArrayList<>();\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int idx = i;\n"
                   "            futures.add(pool.submit(() -> parts[idx] = idx * idx * idx));\n"
                   "        }\n"
                   "        for (Future<?> f : futures) {\n"
                   "            f.get();\n"
                   "        }\n"
                   "        pool.shutdown();\n"
                   "        System.out.println(Arrays.toString(parts));"),
             "        for (int i = 0; i < k; i++) {\n"
             "            final int idx = i;\n"
             "            futures.add(pool.submit(() -> parts[idx] = idx * idx * idx));\n"
             "        }\n"
             "        for (Future<?> f : futures) {\n"
             "            f.get();\n"
             "        }",
             [_k31(k, _jarr([i ** 3 for i in range(k)])) for k in _K31],
             hints=["`Future<?>` because the results are not wanted - only the waiting is.",
                    "Each task owns one slot, so there is nothing to synchronise.",
                    "The second loop's `get()` calls are pure waiting, discarding the "
                    "value.",
                    "They also PUBLISH: after the get, the task's write is visible to "
                    "main.",
                    "`awaitTermination` after `shutdown` would do the same job here; the "
                    "gets are more precise about which tasks you waited for."]),
    ],
    quiz=[
        _jq("Task 3 finishes before task 0. Walking the futures in submission order…",
            ["still prints task 0 first - `get()` blocks until it is ready",
             "prints task 3 first", "throws", "skips task 0"],
            0,
            "Concurrent work, ordered answers."),
        _jq("`invokeAny` differs from `invokeAll` in that it…",
            ["returns the first successful result and cancels the rest",
             "returns them in order", "runs them sequentially",
             "never blocks"],
            0,
            "For 'ask three mirrors, take the fastest'."),
    ],
))


# ===========================================================================
# 31.4 Shutdown
# ===========================================================================

_M31.append(_jlesson(
    "m31-shutdown", "Shutting it down",
    "A pool's threads are not daemons - if you never shut it down, your program never "
    "ends.",
    """
This is the mistake everybody makes once, and it is not subtle - the program
simply never exits:

```java
ExecutorService pool = Executors.newFixedThreadPool(4);
pool.submit(task);
// no shutdown
```

`main` returns, and the JVM does not. Pool threads are **user** threads (module
29's rule: the JVM exits when the last user thread ends), and they are sitting
there waiting for more work that will never arrive.

## The two shutdowns

```java
pool.shutdown();      // polite: refuse NEW tasks, run everything already queued
pool.shutdownNow();   // abrupt: refuse new, interrupt the running ones,
                      // and RETURN the queued tasks that never started
```

Neither one waits. Both return immediately, which is the other half of the
confusion:

```java
pool.shutdown();
if (!pool.awaitTermination(1, TimeUnit.MINUTES)) {   // returns false on timeout
    pool.shutdownNow();
}
```

That pair - `shutdown`, then `awaitTermination`, then `shutdownNow` if it timed
out - is the standard closing sequence.

**After `shutdown`, submitting throws** `RejectedExecutionException`, which is
unchecked:

```java
pool.shutdown();
pool.submit(task);      // RejectedExecutionException
```

## The state questions

```java
pool.isShutdown();      // has shutdown been CALLED?
pool.isTerminated();    // has it shut down AND has every task finished?
```

`isShutdown()` goes true the instant you ask for shutdown; `isTerminated()` only
once the queue has drained. They are not the same question.

## Put it in a `finally`

An exception between creating the pool and shutting it down leaks the pool and
hangs the JVM - the same shape as module 30's un-released lock, with the same
cure:

```java
ExecutorService pool = Executors.newFixedThreadPool(4);
try {
    ...
} finally {
    pool.shutdown();
}
```

`ExecutorService` extends `AutoCloseable` from Java 19, so try-with-resources
(module 16) works too, and `close()` shuts down and waits.
""",
    warmup=[
        _jq("A program that never calls `shutdown()` on its pool…",
            ["never exits - pool threads are user threads, and the JVM waits for them",
             "exits normally", "throws on exit", "leaks memory but exits"],
            0,
            "The most common ExecutorService bug there is."),
        _jq("`shutdown()` …",
            ["returns immediately; use `awaitTermination` to actually wait",
             "blocks until all tasks finish", "cancels running tasks",
             "throws if tasks are queued"],
            0,
            "Neither shutdown method waits for anything."),
    ],
    exercises=[
        _jch("j31-shut-states", "Called, and finished", "Medium",
             "`isShutdown()` and `isTerminated()` answer different questions. Submit `k` "
             "tasks into slots, print `isShutdown` before shutting down, then shut down, "
             "await termination, and print both flags. Replace `____` with the shutdown "
             "sequence and the reports.",
             _j31s("        int k = sc.nextInt();\n"
                   "        int[] parts = new int[k];\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int idx = i;\n"
                   "            pool.execute(() -> parts[idx] = idx + 1);\n"
                   "        }\n"
                   "        System.out.println(pool.isShutdown());\n"
                   "        pool.shutdown();\n"
                   "        System.out.println(pool.isShutdown());\n"
                   "        System.out.println(pool.awaitTermination(1, TimeUnit.MINUTES));\n"
                   "        System.out.println(pool.isTerminated());\n"
                   "        System.out.println(Arrays.toString(parts));"),
             "        System.out.println(pool.isShutdown());\n"
             "        pool.shutdown();\n"
             "        System.out.println(pool.isShutdown());\n"
             "        System.out.println(pool.awaitTermination(1, TimeUnit.MINUTES));\n"
             "        System.out.println(pool.isTerminated());",
             [_k31(k, _nl("false", "true", "true", "true",
                          _jarr([i + 1 for i in range(k)]))) for k in _K31],
             hints=["Before `shutdown()` is called, `isShutdown()` is `false`.",
                    "It becomes `true` the instant shutdown is requested - not when the "
                    "work is done.",
                    "`awaitTermination` returns `true` if everything finished inside the "
                    "timeout.",
                    "A whole minute is far more than these tasks need, so it returns "
                    "`true` almost immediately.",
                    "`isTerminated()` is `true` only after the queue has drained - which "
                    "the await has just guaranteed.",
                    "Reading `parts` is safe because the await published every task's "
                    "write."]),

        _jch("j31-shut-rejected", "The door is shut", "Medium",
             "After `shutdown()`, submitting throws the unchecked "
             "`RejectedExecutionException`. Run one task, shut the pool down, then try to "
             "submit another and catch the rejection. Replace `____` with the shutdown and "
             "the rejected submission.",
             _j31s("        int k = sc.nextInt();\n"
                   "        int[] out = new int[1];\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
                   "        pool.submit(() -> out[0] = k * 4).get();\n"
                   "        System.out.println(out[0]);\n"
                   "        pool.shutdown();\n"
                   "        try {\n"
                   "            pool.execute(() -> out[0] = -1);\n"
                   "            System.out.println(\"accepted\");\n"
                   "        } catch (RejectedExecutionException e) {\n"
                   "            System.out.println(\"rejected\");\n"
                   "        }\n"
                   "        System.out.println(out[0]);"),
             "        pool.shutdown();\n"
             "        try {\n"
             "            pool.execute(() -> out[0] = -1);\n"
             "            System.out.println(\"accepted\");\n"
             "        } catch (RejectedExecutionException e) {\n"
             "            System.out.println(\"rejected\");\n"
             "        }",
             [_k31(k, _nl(k * 4, "rejected", k * 4)) for k in _K31],
             hints=["`pool.submit(...).get()` submits and waits in one expression.",
                    "`RejectedExecutionException` is unchecked, so catching it is a "
                    "choice.",
                    "`accepted` is inside the try after the throwing call, so it never "
                    "runs.",
                    "The rejected task never executes, so the slot keeps its earlier "
                    "value.",
                    "This is the well-behaved failure - far better than silently dropping "
                    "the work."]),

        _jch("j31-shut-finally", "Shut it down in a `finally`", "Medium",
             "A pool leaked by an exception hangs the JVM, exactly as a lock leaked by an "
             "exception hangs the next thread. Compute `k * 5` in a task, print it, and "
             "guarantee the shutdown with a `finally`, printing `closed` there. Replace "
             "`____` with the try/finally.",
             _j31s("        int k = sc.nextInt();\n"
                   "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
                   "        try {\n"
                   "            Future<Integer> answer = pool.submit(() -> k * 5);\n"
                   "            System.out.println(answer.get());\n"
                   "        } finally {\n"
                   "            pool.shutdown();\n"
                   "            System.out.println(\"closed\");\n"
                   "        }\n"
                   "        System.out.println(pool.isShutdown());"),
             "        try {\n"
             "            Future<Integer> answer = pool.submit(() -> k * 5);\n"
             "            System.out.println(answer.get());\n"
             "        } finally {\n"
             "            pool.shutdown();\n"
             "            System.out.println(\"closed\");\n"
             "        }",
             [_k31(k, _nl(k * 5, "closed", "true")) for k in _K31],
             hints=["The pool is created BEFORE the try, so the finally can always see it.",
                    "That is the same shape as `lock()` outside the try in module 30.",
                    "The finally runs whether the body returns normally or throws.",
                    "`closed` therefore prints after the result, every time.",
                    "From Java 19 `ExecutorService` is `AutoCloseable`, so "
                    "try-with-resources does this for you."]),

        _jfix("j31-shut-missing", "The program that never ends",
              "This computes the right answer, prints it - and then hangs forever, "
              "because the pool's threads are user threads waiting for work that will "
              "never come. The JVM will not exit while they are alive. Shut the pool "
              "down.",
              _j31s("        int k = sc.nextInt();\n"
                    "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                    "        Future<Integer> answer = pool.submit(() -> k * 6);\n"
                    "        System.out.println(answer.get());"),
              _j31s("        int k = sc.nextInt();\n"
                    "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                    "        Future<Integer> answer = pool.submit(() -> k * 6);\n"
                    "        System.out.println(answer.get());\n"
                    "        pool.shutdown();"),
              [_k31(k, str(k * 6)) for k in _K31],
              hints=["The output is already correct - the problem is that the program "
                     "never finishes producing it.",
                     "Module 29's rule: the JVM exits when the last USER thread ends.",
                     "A pool's worker threads are user threads, and they idle rather than "
                     "exit.",
                     "One line: `pool.shutdown();` after the last use.",
                     "`shutdown()` lets the already-submitted work finish, so nothing is "
                     "lost.",
                     "Better still, put it in a `finally` - or use try-with-resources."],
              difficulty="Easy"),
    ],
    quiz=[
        _jq("`shutdownNow()` differs from `shutdown()` in that it…",
            ["interrupts running tasks and returns the queued ones that never started",
             "waits for running tasks", "is the same thing",
             "cannot be called twice"],
            0,
            "Polite versus abrupt. Neither one blocks."),
        _jq("`isShutdown()` is true and `isTerminated()` is false when…",
            ["shutdown has been requested but queued tasks are still running",
             "never - they always agree", "the pool was never started",
             "a task threw"],
            0,
            "Two different questions: asked, versus finished."),
    ],
))


# ===========================================================================
# 31.5 Concurrent collections
# ===========================================================================

_M31.append(_jlesson(
    "m31-collections", "The concurrent collections",
    "Why a `HashMap` breaks, why a synchronized wrapper is not enough, and what to use "
    "instead.",
    """
Part 6's collections are **not thread-safe**, and a `HashMap` written by two
threads at once does not merely lose an entry - it can corrupt its internal
table, lose unrelated entries, or (famously, before Java 8) spin forever inside
`get`.

There are three levels of answer.

## 1. A synchronized wrapper - rarely enough

```java
Map<String, Integer> m = Collections.synchronizedMap(new HashMap<>());
```

Every *method* is now synchronized. But module 30's lesson applies exactly:
atomicity belongs to a single call, and almost nothing useful is a single call.

```java
if (!m.containsKey(k)) m.put(k, 0);      // check-then-act. STILL A RACE.
m.put(k, m.get(k) + 1);                  // read-modify-write. STILL A RACE.
```

To fix those you must lock around the whole sequence yourself - at which point
the wrapper bought you nothing, and it serialises every access through one lock
besides. Iteration needs a manual `synchronized` block too.

## 2. `ConcurrentHashMap` - the real answer

Locks a small part of the table rather than the whole map, so readers never
block and writers only contend when they collide. Crucially, it provides the
compound operations as **single atomic calls**:

```java
map.putIfAbsent(key, value);              // the check-then-act, atomically
map.merge(key, 1, Integer::sum);          // the frequency count, atomically
map.computeIfAbsent(key, k -> new ...);   // build-on-demand, atomically
map.compute(key, (k, v) -> ...);
```

`merge(key, 1, Integer::sum)` is the whole word-count idiom in one atomic
operation: insert 1 if absent, otherwise combine the old value with 1 using the
function. Module 18 wrote this with `getOrDefault` and a `put`, which is two
operations and fine on one thread only.

`ConcurrentHashMap` permits no `null` key or value, precisely because
`get` returning `null` has to mean "absent" unambiguously.

## 3. `CopyOnWriteArrayList` - for reads

Every write copies the whole backing array. Absurd for write-heavy use, ideal
for a list read constantly and changed rarely - a listener list, a config
snapshot. Iterators see the array as it was when iteration began, so they never
throw `ConcurrentModificationException` (module 17) and never see later changes.

## Printing them

A `ConcurrentHashMap`'s iteration order is **unspecified**, exactly like a
`HashMap`'s. Module 27's rule stands: never print one directly. Copy it into a
`TreeMap`, or sort the keys, whenever the output has to be defined - which is
what every exercise below does.
""",
    warmup=[
        _jq("`Collections.synchronizedMap` makes this safe: `if (!m.containsKey(k)) m.put(k, 0);`",
            ["No - each call is atomic, the sequence is not",
             "Yes", "Yes, if the map is small", "Yes, for two threads"],
            0,
            "`putIfAbsent` is the single atomic call that does it."),
        _jq("The frequency-count idiom on a ConcurrentHashMap is…",
            ["map.merge(key, 1, Integer::sum)",
             "map.put(key, map.get(key) + 1)",
             "map.getOrDefault(key, 0) + 1 then put",
             "map.computeIfPresent(key, ...)"],
            0,
            "One atomic call; the other two are read-modify-write."),
    ],
    exercises=[
        _jch("j31-coll-merge", "A concurrent frequency table", "Hard",
             "Read `n` words and count how many share each length, from a pool, with "
             "`merge` doing the whole read-modify-write atomically. Print through a "
             "`TreeMap` so the key order is defined, then the number of distinct lengths. "
             "Replace `____` with the map, the tasks and the wait.",
             _j31s(_RD_W31
                   + "        ConcurrentHashMap<Integer, Integer> counts = new ConcurrentHashMap<>();\n"
                     "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                     "        for (String w : words) {\n"
                     "            pool.execute(() -> counts.merge(w.length(), 1, Integer::sum));\n"
                     "        }\n"
                     "        pool.shutdown();\n"
                     "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
                     "        System.out.println(new TreeMap<>(counts));\n"
                     "        System.out.println(counts.size());"),
             "        ConcurrentHashMap<Integer, Integer> counts = new ConcurrentHashMap<>();\n"
             "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
             "        for (String w : words) {\n"
             "            pool.execute(() -> counts.merge(w.length(), 1, Integer::sum));\n"
             "        }\n"
             "        pool.shutdown();\n"
             "        pool.awaitTermination(1, TimeUnit.MINUTES);",
             [_w31(ws, _nl("{" + ", ".join(
                 f"{ln}={c}" for ln, c in sorted(
                     {len(w): sum(1 for x in ws if len(x) == len(w)) for w in ws}.items()))
                 + "}",
                 len({len(w) for w in ws}))) for ws in _W31],
             hints=["`merge(key, 1, Integer::sum)` inserts 1 when the key is absent and "
                    "otherwise sums - atomically, in one call.",
                    "`map.put(key, map.get(key) + 1)` would be the module 30 race, "
                    "however concurrent the map is.",
                    "`w` in the enhanced `for` is effectively final, so the lambda may "
                    "capture it directly.",
                    "`shutdown` then `awaitTermination` is how you know every word has "
                    "been counted.",
                    "A ConcurrentHashMap's iteration order is undefined - "
                    "`new TreeMap<>(counts)` gives it a defined one.",
                    "`size()` is the number of distinct lengths, not the number of "
                    "words."]),

        _jch("j31-coll-putifabsent", "Check and act, atomically", "Medium",
             "`putIfAbsent` inserts only when the key is absent, and returns the value "
             "that was already there - or `null` if it did insert. Read `n` words, claim "
             "each first letter for the first word that has it, and print the claims "
             "sorted, then the size. Replace `____` with the map and the claiming loop.",
             _j31s(_RD_W31
                   + "        ConcurrentHashMap<String, String> owner = new ConcurrentHashMap<>();\n"
                     "        for (String w : words) {\n"
                     "            owner.putIfAbsent(w.substring(0, 1), w);\n"
                     "        }\n"
                     "        System.out.println(new TreeMap<>(owner));\n"
                     "        System.out.println(owner.size());"),
             "        ConcurrentHashMap<String, String> owner = new ConcurrentHashMap<>();\n"
             "        for (String w : words) {\n"
             "            owner.putIfAbsent(w.substring(0, 1), w);\n"
             "        }",
             [_w31(ws, _nl("{" + ", ".join(
                 f"{k}={v}" for k, v in sorted(
                     {w[0]: w for w in reversed(ws)}.items()))
                 + "}",
                 len({w[0] for w in ws}))) for ws in _W31],
             hints=["`putIfAbsent` is the atomic version of "
                    "`if (!map.containsKey(k)) map.put(k, v);`.",
                    "The FIRST word with a given first letter keeps the key; later ones "
                    "change nothing.",
                    "`w.substring(0, 1)` is a one-character String key.",
                    "Print through a `TreeMap` so the order is alphabetical rather than "
                    "undefined.",
                    "The size is the number of distinct first letters."]),

        _jch("j31-coll-cow", "Copy-on-write", "Medium",
             "A `CopyOnWriteArrayList` is safe to add to from many threads, but the "
             "resulting ORDER is completion order, which is nothing you may rely on. Add "
             "every word from a pool, then sort a copy before printing. Print the size, "
             "the sorted contents, then the first element of the sorted copy. Replace "
             "`____` with the list, the tasks and the wait.",
             _j31s(_RD_W31
                   + "        CopyOnWriteArrayList<String> seen = new CopyOnWriteArrayList<>();\n"
                     "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                     "        for (String w : words) {\n"
                     "            pool.execute(() -> seen.add(w));\n"
                     "        }\n"
                     "        pool.shutdown();\n"
                     "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
                     "        List<String> sorted = new ArrayList<>(seen);\n"
                     "        Collections.sort(sorted);\n"
                     "        System.out.println(seen.size());\n"
                     "        System.out.println(sorted);\n"
                     "        System.out.println(sorted.get(0));"),
             "        CopyOnWriteArrayList<String> seen = new CopyOnWriteArrayList<>();\n"
             "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
             "        for (String w : words) {\n"
             "            pool.execute(() -> seen.add(w));\n"
             "        }\n"
             "        pool.shutdown();\n"
             "        pool.awaitTermination(1, TimeUnit.MINUTES);",
             [_w31(ws, _nl(len(ws), "[" + ", ".join(sorted(ws)) + "]", sorted(ws)[0]))
              for ws in _W31],
             hints=["A plain `ArrayList` here could lose entries or corrupt itself "
                    "outright.",
                    "`CopyOnWriteArrayList.add` is safe, so the SIZE is reliable.",
                    "The ORDER is not - it is whichever task got there first.",
                    "So copy into an `ArrayList` and `Collections.sort` it before "
                    "printing.",
                    "Every write copies the whole array, which is why this class is for "
                    "read-heavy use only."]),

        # NOT a `fix`. The obvious version of this - ship the getOrDefault/put
        # starter and have the learner replace it - would need that starter to
        # FAIL for `--starters` to pass, and on three words and a quiet machine
        # it very often does not race at all. A bug that only sometimes shows is
        # exactly what this module warns about; it is not something to build a
        # test on. So the racing version lives in the prompt, and the exercise
        # is to write the atomic one.
        _jch("j31-coll-compose", "Two calls are still two calls", "Hard",
             "Counting with `counts.put(len, counts.getOrDefault(len, 0) + 1)` races even "
             "on a `ConcurrentHashMap`: it is a read and a write with a gap in the "
             "middle, and a thread-safe map guarantees each CALL, never a sequence. An "
             "increment landing in that gap is simply overwritten. Write the version that "
             "does the whole count in ONE atomic call, and print the histogram through a "
             "`TreeMap`. Replace `____` with the pool, the counting loop and the wait.",
             _j31s(_RD_W31
                   + "        ConcurrentHashMap<Integer, Integer> counts = new ConcurrentHashMap<>();\n"
                     "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                     "        for (String w : words) {\n"
                     "            pool.execute(() -> counts.merge(w.length(), 1, Integer::sum));\n"
                     "        }\n"
                     "        pool.shutdown();\n"
                     "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
                     "        System.out.println(new TreeMap<>(counts));"),
             "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
             "        for (String w : words) {\n"
             "            pool.execute(() -> counts.merge(w.length(), 1, Integer::sum));\n"
             "        }\n"
             "        pool.shutdown();\n"
             "        pool.awaitTermination(1, TimeUnit.MINUTES);",
             [_w31(ws, "{" + ", ".join(
                 f"{ln}={c}" for ln, c in sorted(
                     {len(w): sum(1 for x in ws if len(x) == len(w)) for w in ws}.items()))
                 + "}") for ws in _W31],
             hints=["`getOrDefault` then `put` is two trips into the map, with a gap "
                    "between them.",
                    "A thread-safe collection guarantees each CALL - the same rule as an "
                    "`AtomicInteger`, met again.",
                    "`counts.merge(w.length(), 1, Integer::sum)` inserts 1 if absent and "
                    "otherwise combines, atomically.",
                    "Module 18's `getOrDefault` idiom is correct on one thread and wrong "
                    "on several.",
                    "Note how badly the racing version would test: on three words it "
                    "usually gives the right answer anyway.",
                    "Print through `new TreeMap<>(counts)` - the map's own order is "
                    "undefined."]),
    ],
    quiz=[
        _jq("`ConcurrentHashMap` forbids null keys and values because…",
            ["`get` returning null must unambiguously mean 'absent'",
             "nulls are slow", "the table cannot store them",
             "it is an arbitrary restriction"],
            0,
            "With concurrent updates you cannot re-check the way you can on a HashMap."),
        _jq("`CopyOnWriteArrayList` suits…",
            ["lists read constantly and modified rarely",
             "write-heavy lists", "very large lists",
             "lists needing sorted order"],
            0,
            "Every single write copies the entire backing array."),
    ],
))


# ===========================================================================
# Capstone
# ===========================================================================

_M31_CAP_BODY = (
    _RD_W31
    + "        int k = sc.nextInt();\n"
      "        ConcurrentHashMap<Integer, Integer> lengths = new ConcurrentHashMap<>();\n"
      "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
      "        try {\n"
      "            List<Callable<Integer>> tasks = new ArrayList<>();\n"
      "            for (int i = 0; i < k; i++) {\n"
      "                final int from = i * n / k;\n"
      "                final int to = (i + 1) * n / k;\n"
      "                tasks.add(() -> {\n"
      "                    int chars = 0;\n"
      "                    for (int j = from; j < to; j++) {\n"
      "                        chars += words[j].length();\n"
      "                        lengths.merge(words[j].length(), 1, Integer::sum);\n"
      "                    }\n"
      "                    return chars;\n"
      "                });\n"
      "            }\n"
      "            List<Future<Integer>> done = pool.invokeAll(tasks);\n"
      "            int total = 0;\n"
      "            for (int i = 0; i < k; i++) {\n"
      "                int chars = done.get(i).get();\n"
      "                System.out.println(i + \" \" + chars);\n"
      "                total += chars;\n"
      "            }\n"
      "            System.out.println(total);\n"
      "            System.out.println(new TreeMap<>(lengths));\n"
      "            System.out.println(lengths.size());\n"
      "        } finally {\n"
      "            pool.shutdown();\n"
      "        }\n"
      "        System.out.println(pool.isShutdown());"
)


def _cap31(ws, k):
    n = len(ws)
    lines = []
    total = 0
    for i in range(k):
        chars = sum(len(w) for w in ws[i * n // k:(i + 1) * n // k])
        total += chars
        lines.append(f"{i} {chars}")
    lines.append(str(total))
    hist = {}
    for w in ws:
        hist[len(w)] = hist.get(len(w), 0) + 1
    lines.append("{" + ", ".join(f"{ln}={c}" for ln, c in sorted(hist.items())) + "}")
    lines.append(str(len(hist)))
    lines.append("true")
    return _nl(*lines)


def _cap31_case(ws, k):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(k)]), _cap31(ws, k))


_M31_CAP = _jcap(
    "The parallel word report",
    """
`n` words, `k` chunks, one pool - and every idea in the module in one program.

Each chunk task does two different kinds of work, which is the point:

* it **returns** its own character count, through `Callable<Integer>` - a
  per-task answer, kept per-task;
* it **contributes** to a shared length histogram, through
  `ConcurrentHashMap.merge` - a genuinely shared structure, updated atomically.

Then the output, all of it defined:

1. `index chars` for each chunk, taken from `invokeAll`'s futures **in argument
   order**, not completion order;
2. the grand total;
3. the histogram, printed through a **`TreeMap`** because a
   `ConcurrentHashMap`'s own iteration order is unspecified;
4. how many distinct lengths there were;
5. `true`, from `isShutdown()` after the `finally`.

The two rules that make it reproducible are worth stating plainly. **Results
come back in submission order** - `invokeAll` guarantees it, so chunk 0 prints
first even if it finished last. And **the shared map is only ever printed
sorted** - `merge` makes each update atomic, but nothing makes a hash table's
iteration order stable, and module 27 already banned printing one raw.

The pool is shut down in a `finally`, so an exception anywhere in the body still
lets the JVM exit rather than hanging on live pool threads.
""",
    _jch("j31-cap-report", "The parallel word report", "Hard",
         "Read `n` words then `k`. Split the words into `k` contiguous chunks, and for "
         "each chunk return its total character count while merging every word's length "
         "into a shared concurrent histogram. Print per-chunk counts in order, the total, "
         "the histogram sorted, the number of distinct lengths, and the pool's shutdown "
         "state.",
         _j31s(_M31_CAP_BODY),
         _M31_CAP_BODY,
         [_cap31_case(ws, k)
          for (ws, k) in ((_W31[0], 3), (_W31[1], 1), (_W31[2], 2),
                          (_W31[3], 3), (_W31[4], 2))],
         hints=["Read every word on the main thread first - a Scanner is not shareable.",
                "Chunk bounds are module 29's: `i*n/k` and `(i+1)*n/k`, copied into "
                "`final` locals.",
                "The task is a `Callable<Integer>`: accumulate `chars` in a local and "
                "`return` it.",
                "Inside the same loop, `lengths.merge(words[j].length(), 1, Integer::sum)` "
                "updates the shared histogram atomically.",
                "`pool.invokeAll(tasks)` returns the futures in ARGUMENT order - walk them "
                "by index.",
                "Print the histogram as `new TreeMap<>(lengths)`, never the "
                "ConcurrentHashMap itself.",
                "`lengths.size()` is the number of distinct lengths, not the word count.",
                "Wrap the whole body in a try with `pool.shutdown()` in the `finally`, "
                "then print `pool.isShutdown()` afterwards."]),
    example_io="stdin:  3\n        ada bo cy\n        3\n\n"
               "stdout: 0 3\n        1 2\n        2 2\n        7\n"
               "        {2=2, 3=1}\n        2\n        true",
    rubric=[
        "Each chunk is a `Callable<Integer>` returning its own character count.",
        "Results are read from `invokeAll`'s futures in argument order, not completion order.",
        "The shared histogram is a `ConcurrentHashMap` updated with a single atomic `merge`.",
        "No `get`-then-`put` pair anywhere on the shared map.",
        "The histogram is printed through a `TreeMap`, never directly.",
        "The pool is shut down in a `finally`.",
        "No task prints anything; all output comes from main.",
        "The output is identical on every run.",
    ],
    stretch=None,
)


_MODULES.append(_jmod(
    31, 10, "Multithreading",
    "Executors, tasks and results",
    "Stop managing threads. Submit tasks, collect futures in order, shut the pool down.",
    """
Modules 29 and 30 managed threads by hand. This module replaces all of it.

* **A pool separates the task from the thread.** `Executors.newFixedThreadPool(n)`
  bounds concurrency and reuses threads; `newSingleThreadExecutor` runs tasks in
  submission order; `newCachedThreadPool` is unbounded and needs care.
* **`Callable<V>` beats `Runnable`**: it returns a value and may throw a checked
  exception, so tasks stop writing into array slots.
* **`Future` is a receipt.** `get()` blocks, publishes, and re-throws a failed
  task's exception wrapped in an **`ExecutionException`** - so `getCause()` is
  what you want. A task that nobody `get()`s can fail in total silence, which is
  the case against `execute`.
* **Order comes from you, not the pool.** Keep the futures in submission order
  and `get()` them in that order, or use **`invokeAll`**, whose result list is in
  argument order. This is what makes concurrent output testable.
* **Shut the pool down.** Pool threads are user threads, so a program that never
  calls `shutdown()` never exits. `shutdown` then `awaitTermination`, in a
  `finally`.
* **Concurrent collections.** A synchronized wrapper makes each call atomic and
  leaves every check-then-act racing. `ConcurrentHashMap` provides the compound
  operations as single atomic calls - `putIfAbsent`, `merge`, `computeIfAbsent` -
  and is still printed through a `TreeMap`, because its iteration order is
  undefined.

That closes Part 10, and the course.
""",
    _M31,
    capstone=_M31_CAP,
    objectives=[
        "Say why a thread per task does not scale, and what a pool changes.",
        "Choose between a fixed, single-thread and cached executor, and say why cached is risky.",
        "Distinguish `execute` from `submit`, and say what each returns.",
        "Use `Callable<V>` and say what it can do that `Runnable` cannot.",
        "Use `Future.get()`, and say what it guarantees beyond returning a value.",
        "Handle a failed task through `ExecutionException` and `getCause()`.",
        "Explain how a task's exception can vanish entirely.",
        "Collect results in submission order, with a future list or with `invokeAll`.",
        "Say what `invokeAll` guarantees about ordering, and how `invokeAny` differs.",
        "Shut a pool down correctly, and explain why a program without it never exits.",
        "Distinguish `shutdown` from `shutdownNow`, and `isShutdown` from `isTerminated`.",
        "Say why `Collections.synchronizedMap` does not fix check-then-act.",
        "Use `ConcurrentHashMap`'s atomic compound operations, especially `merge`.",
        "Say why a concurrent map is still never printed directly.",
    ],
    why="Nobody writes `new Thread(...)` in production Java. They submit tasks to a pool, "
        "which means the questions that get asked are about this module: Runnable versus "
        "Callable, what a Future actually gives you, where a failed task's exception "
        "goes, the difference between shutdown and shutdownNow. The forgotten "
        "`shutdown()` is a genuine production incident, not a quiz answer. And the "
        "ordering pattern - submit concurrently, collect in submission order - is the one "
        "habit that makes concurrent code something you can write a test for, which is "
        "the difference between using threads and trusting them.",
    est_minutes=330,
    glossary=[
        _jg("ExecutorService", "A pool of threads fed from a task queue. You submit work; "
                               "it decides which thread runs it and when."),
        _jg("task", "A unit of work - a `Runnable` or a `Callable` - as opposed to the "
                    "thread that happens to run it."),
        _jg("Callable<V>", "A task returning a `V` that may throw a checked exception. A "
                           "functional interface, so a lambda is one."),
        _jg("Future<V>", "A receipt for a result that does not exist yet. `get()` blocks "
                         "until it does."),
        _jg("ExecutionException", "What `get()` throws when the task threw. The real "
                                  "exception is `getCause()`."),
        _jg("RejectedExecutionException", "Unchecked; thrown by a submission after "
                                          "`shutdown()`."),
        _jg("invokeAll", "Submits every task, blocks until all are done, and returns the "
                         "futures IN ARGUMENT ORDER."),
        _jg("invokeAny", "Returns the first successful result and cancels the rest."),
        _jg("shutdown", "Refuse new tasks, finish queued ones. Returns immediately."),
        _jg("shutdownNow", "Refuse new tasks, interrupt running ones, and return the "
                           "queued tasks that never started."),
        _jg("awaitTermination", "Block for up to a timeout waiting for the pool to finish; "
                                "false means it timed out."),
        _jg("ConcurrentHashMap", "A thread-safe map with atomic compound operations "
                                 "(`putIfAbsent`, `merge`, `computeIfAbsent`). No nulls. "
                                 "Iteration order undefined."),
        _jg("CopyOnWriteArrayList", "A list that copies its array on every write. For "
                                    "read-heavy, rarely-modified data."),
    ],
    cheatsheet="""
```java
import java.util.concurrent.*;

// --- getting a pool -------------------------------------------------------
ExecutorService pool = Executors.newFixedThreadPool(4);   // bounded: the default choice
Executors.newSingleThreadExecutor();   // 1 thread, SUBMISSION ORDER, output predictable
Executors.newCachedThreadPool();       // UNBOUNDED - a thread per task under load

// --- handing over work ----------------------------------------------------
pool.execute(runnable);                     // void. No handle, no error reporting.
Future<?>       f = pool.submit(runnable);  // f.get() -> null
Future<Integer> g = pool.submit(() -> 6*7); // Callable<V>: returns AND may throw

// --- collecting -----------------------------------------------------------
g.get();                     // BLOCKS, publishes, rethrows failures wrapped
g.get(2, TimeUnit.SECONDS);  // ...or TimeoutException
g.isDone(); g.cancel(true); g.isCancelled();

try { g.get(); }
catch (ExecutionException e) { e.getCause(); }   // THE CAUSE is the real exception

// --- ORDER: the pattern that makes it testable ----------------------------
List<Future<Integer>> fs = new ArrayList<>();
for (...) { final int idx = i; fs.add(pool.submit(() -> work(idx))); }
for (Future<Integer> f2 : fs) System.out.println(f2.get());   // SUBMISSION order

List<Future<Integer>> done = pool.invokeAll(tasks);  // blocks; ARGUMENT order
pool.invokeAny(tasks);                               // first success, cancels the rest

// --- shutting down (or the JVM NEVER EXITS) -------------------------------
pool.shutdown();                                   // polite; returns immediately
if (!pool.awaitTermination(1, TimeUnit.MINUTES)) pool.shutdownNow();
pool.isShutdown();    // was it ASKED?      pool.isTerminated();  // has it FINISHED?
try { ... } finally { pool.shutdown(); }           // or try-with-resources (Java 19+)
pool.submit(t);       // after shutdown -> RejectedExecutionException

// --- concurrent collections -----------------------------------------------
Collections.synchronizedMap(new HashMap<>());   // each CALL atomic; sequences still race
ConcurrentHashMap<K,V> m = new ConcurrentHashMap<>();   // no null key or value
m.putIfAbsent(k, v);              // check-then-act, atomically
m.merge(k, 1, Integer::sum);      // the frequency count, atomically
m.computeIfAbsent(k, x -> ...);
m.put(k, m.get(k) + 1);           // WRONG - two calls, still a race
System.out.println(new TreeMap<>(m));   // iteration order is UNDEFINED: sort to print
CopyOnWriteArrayList<T>           // read-heavy only; every write copies the array
```
""",
    self_check=[
        "Can you say what a pool changes about a thread per task, in cost terms?",
        "Can you say which executor gives predictable output, and why?",
        "Can you say what `execute` returns and what that costs you?",
        "Can you give two things `Callable` can do that `Runnable` cannot?",
        "Can you say what `Future.get()` guarantees beyond handing back a value?",
        "Can you get at the real exception a failed task threw?",
        "Can you describe how a task's exception disappears completely?",
        "Can you collect results in submission order two different ways?",
        "Can you say what `invokeAll` guarantees about the order of its result list?",
        "Can you explain why a program with no `shutdown()` hangs?",
        "Can you say what happens if you submit after shutdown?",
        "Can you say why `Collections.synchronizedMap` does not fix `if (!m.containsKey(k)) m.put(k, v);`?",
        "Can you write the frequency-count idiom as one atomic call?",
        "Can you say why you still never print a ConcurrentHashMap directly?",
    ],
    review=[
        _jq("A program submits a task, prints its result, and never calls `shutdown()`. It…",
            ["prints the result and then hangs forever",
             "prints the result and exits", "throws on exit",
             "never prints"],
            0,
            "Pool threads are user threads, and the JVM waits for them."),
        _jq("A task submitted with `execute` throws. Your code finds out…",
            ["never - there is no handle to ask",
             "immediately, on the main thread",
             "when the pool shuts down", "via a Future"],
            0,
            "Which is the argument for submit over execute."),
        _jq("Task 3 finishes first. `invokeAll(tasks)` returns futures…",
            ["in the order of the task list, so task 0 is still first",
             "in completion order, so task 3 is first",
             "in a random order", "sorted by result"],
            0,
            "That guarantee is what makes the output reproducible."),
        _jq("`m.put(k, m.get(k) + 1)` on a `ConcurrentHashMap` is…",
            ["a race - two atomic calls do not compose",
             "safe, because the map is concurrent", "a compile error",
             "safe if only two threads"],
            0,
            "`merge(k, 1, Integer::sum)` is the single atomic call."),
        _jq("`ExecutionException` wraps…",
            ["the exception the task threw, reachable with `getCause()`",
             "an InterruptedException", "a RejectedExecutionException",
             "nothing"],
            0,
            "The wrapper is plumbing; the cause is what happened."),
        _jq("Printing a `ConcurrentHashMap` directly is wrong because…",
            ["its iteration order is unspecified, like a HashMap's",
             "it is not thread-safe to iterate", "toString throws",
             "it would deadlock"],
            0,
            "Copy into a TreeMap, or sort the keys."),
    ],
    milestone="You can stop thinking in threads and start thinking in tasks: hand work to "
              "a bounded pool, get answers back through `Callable` and `Future` rather "
              "than array slots, collect them in submission order so the output is "
              "reproducible, surface a failed task instead of losing it, shut the pool "
              "down in a `finally` - and reach for `merge` rather than a get-then-put on "
              "a shared map.",
))
