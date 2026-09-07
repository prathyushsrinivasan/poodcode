# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 31 practice - executors, tasks and results.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[31]`.
#
# The last practice file in the course. Everything from modules 29-31 is legal
# here; nothing later exists.
#
# DETERMINISM, which is strictest in this module because a pool schedules itself:
#
#   * results are read in SUBMISSION order - keep the futures in a list and
#     `get()` them in order, or use `invokeAll`, whose result list is in
#     argument order however the tasks actually ran;
#   * tasks never print, EXCEPT under `newSingleThreadExecutor`, which is
#     documented to run them sequentially in submission order;
#   * maps are printed through a `TreeMap` - a ConcurrentHashMap's iteration
#     order is as undefined as a HashMap's (module 27's rule, unchanged);
#   * pool thread names are never printed: `pool-1-thread-3` depends on which
#     worker happened to pick the task up.
#
# And, as in module 30: no variant here relies on a race ACTUALLY happening.
# A `getOrDefault`/`put` pair on three words usually produces the right answer
# anyway, so the broken versions are described in prose and the exercises write
# the correct one.
# ---------------------------------------------------------------------------

_IMPORTS31P = ("import java.util.*;\n"
               "import java.util.concurrent.*;\n")

_SIG31P = ("    public static void main(String[] args)\n"
           "            throws InterruptedException, ExecutionException {")


def _p31prog(body):
    return _jcls(
        _SIG31P + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }",
        imports=_IMPORTS31P,
    )


def _p31s(eid, title, difficulty, prompt, body, tests, hints):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p31prog(body), body, tests, hints)


_K31P = (1, 2, 3, 4, 5)
_A31P = ([2, 5, 1], [7], [3, 3, 3, 3], [8, -4, 6], [1, 2, 3, 4, 5, 6])
_W31P = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"],
         ["pear", "fig", "plum"], ["alpha", "beta", "gamma", "d"])

_RD_W31P = ("        int n = sc.nextInt();\n"
            "        String[] words = new String[n];\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            words[i] = sc.next();\n"
            "        }\n")


def _k31p(k, out):
    return _case(str(k), out)


def _w31p(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _hist31p(ws):
    """Exactly what `new TreeMap<>(counts)` prints for a length histogram."""
    hist = {}
    for w in ws:
        hist[len(w)] = hist.get(len(w), 0) + 1
    return "{" + ", ".join(f"{ln}={c}" for ln, c in sorted(hist.items())) + "}"


# ===========================================================================
# Family A - pools and tasks
# ===========================================================================

_P31_A = _jfam(
    "p31-pool", "Pools and tasks",
    "Hand work over, wait for the pool to drain, read the results.",
    """
```java
ExecutorService pool = Executors.newFixedThreadPool(2);
for (...) pool.execute(task);
pool.shutdown();
pool.awaitTermination(1, TimeUnit.MINUTES);
```

`shutdown` plus `awaitTermination` is this module's replacement for module 29's
join loop: it is how you know every task has finished before you read anything.

The number of tasks and the number of threads are unrelated - two threads will
happily serve five hundred tasks, one after another, from the queue.
""",
    [
        _p31s("j31-pa-slots", "A pool, and a slot each", "Medium",
              "Read `k`, hand the pool `k` tasks where task `i` writes `i * 2` into its "
              "own slot, drain the pool, then print the slots in index order and the "
              "total.",
              "        int k = sc.nextInt();\n"
              "        int[] parts = new int[k];\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            pool.execute(() -> parts[idx] = idx * 2);\n"
              "        }\n"
              "        pool.shutdown();\n"
              "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            System.out.println(i + \" \" + parts[i]);\n"
              "            total += parts[i];\n"
              "        }\n"
              "        System.out.println(total);",
              [_k31p(k, _nl(*([f"{i} {i * 2}" for i in range(k)]
                              + [sum(i * 2 for i in range(k))]))) for k in _K31P],
              ["`final int idx = i;` before the lambda, exactly as with raw threads.",
               "Each task owns one slot, so there is nothing to synchronise.",
               "`shutdown` then `awaitTermination` is the join loop's replacement.",
               "Main prints afterwards, in index order.",
               "Two threads serve all `k` tasks from the queue."]),

        _p31s("j31-pa-single", "One thread, submission order", "Easy",
              "A single-thread executor runs tasks one at a time in submission order, so "
              "here the tasks may print for themselves. Submit `k` tasks each printing "
              "`step i`, then print `done`.",
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newSingleThreadExecutor();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            pool.execute(() -> System.out.println(\"step \" + idx));\n"
              "        }\n"
              "        pool.shutdown();\n"
              "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
              "        System.out.println(\"done\");",
              [_k31p(k, _nl(*([f"step {i}" for i in range(k)] + ["done"])))
               for k in _K31P],
              ["`Executors.newSingleThreadExecutor()` takes no argument.",
               "One thread plus a FIFO queue means one task at a time, in order.",
               "Change it to `newFixedThreadPool(2)` and this output stops being "
               "predictable.",
               "`done` prints last because the await comes first.",
               "This is the only shape in Part 10 where a task is allowed to print."]),

        _p31s("j31-pa-morethan", "More tasks than threads", "Medium",
              "A two-thread pool given `k` tasks: they queue and are served as threads "
              "free up. Task `i` writes `i + 1`; print `k` and the total.",
              "        int k = sc.nextInt();\n"
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
              "        System.out.println(total);",
              [_k31p(k, _nl(k, k * (k + 1) // 2)) for k in _K31P],
              ["Tasks and threads are unrelated counts.",
               "With raw threads, `k` tasks meant `k` threads; here it means two.",
               "Which thread ran which task is not observable, and nothing here depends "
               "on it.",
               "The total is 1 + 2 + ... + k.",
               "That bound on thread count is the entire reason pools exist."]),

        _p31s("j31-pa-submitnull", "A Runnable has no result", "Medium",
              "`submit(Runnable)` gives a `Future<?>` whose `get()` returns `null` - it "
              "is pure waiting. Note the braces: without them the assignment would be an "
              "expression, making the lambda a `Callable<Integer>` instead. Print the "
              "`get()`, then the slot.",
              "        int k = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
              "        Future<?> handle = pool.submit(() -> {\n"
              "            out[0] = k * 7;\n"
              "        });\n"
              "        System.out.println(handle.get());\n"
              "        System.out.println(out[0]);\n"
              "        pool.shutdown();",
              [_k31p(k, _nl("null", k * 7)) for k in _K31P],
              ["`Future<?>` - the wildcard because there is no result type.",
               "`get()` blocks, then returns `null`, which prints as `null`.",
               "The braced body is what makes the lambda void-compatible only.",
               "Drop the braces and `submit` picks its `Callable` overload, because an "
               "assignment has a value.",
               "Either way the get publishes the task's write to main."]),

        _p31s("j31-pa-shutdown", "Asked, and finished", "Medium",
              "`isShutdown()` and `isTerminated()` answer different questions. Print "
              "`isShutdown` before the shutdown, after it, then the result of "
              "`awaitTermination`, then `isTerminated`.",
              "        int k = sc.nextInt();\n"
              "        int[] parts = new int[k];\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            pool.execute(() -> parts[idx] = idx);\n"
              "        }\n"
              "        System.out.println(pool.isShutdown());\n"
              "        pool.shutdown();\n"
              "        System.out.println(pool.isShutdown());\n"
              "        System.out.println(pool.awaitTermination(1, TimeUnit.MINUTES));\n"
              "        System.out.println(pool.isTerminated());\n"
              "        System.out.println(Arrays.toString(parts));",
              [_k31p(k, _nl("false", "true", "true", "true",
                            _jarr(list(range(k))))) for k in _K31P],
              ["`isShutdown()` is `false` until shutdown is actually requested.",
               "It becomes `true` immediately - it asks whether shutdown was CALLED.",
               "`awaitTermination` returns `true` when everything finished inside the "
               "timeout.",
               "`isTerminated()` is `true` only once the queue has drained.",
               "Reading `parts` is safe because the await published every write."]),
    ])


# ===========================================================================
# Family B - Callable and Future
# ===========================================================================

_P31_B = _jfam(
    "p31-callable", "`Callable` and `Future`",
    "Tasks that return a value, and tasks that fail.",
    """
```java
Future<Integer> f = pool.submit(() -> 6 * 7);   // Callable<V>: returns AND may throw
f.get();                                        // blocks, publishes, rethrows
```

`Runnable` returns nothing and cannot throw a checked exception, which is why
every worker in modules 29 and 30 wrote into an array slot. `Callable<V>` needs
neither workaround.

When a task throws, the exception is stored and handed to whoever calls `get()`,
wrapped:

```java
catch (ExecutionException e) { e.getCause(); }   // the CAUSE is the real one
```

And if nobody ever calls `get()`, nobody ever finds out.
""",
    [
        _p31s("j31-pb-value", "A task with an answer", "Easy",
              "Submit a `Callable<Integer>` returning `k * k * k` and print the result.",
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
              "        Future<Integer> answer = pool.submit(() -> k * k * k);\n"
              "        System.out.println(answer.get());\n"
              "        pool.shutdown();",
              [_k31p(k, str(k ** 3)) for k in _K31P],
              ["A lambda returning a value is a `Callable<Integer>` here.",
               "The target type `Future<Integer>` is what selects that overload.",
               "The body is an expression, so no braces and no `return`.",
               "`get()` blocks until the value exists.",
               "No array slot and no join - the answer comes back through the return "
               "type."]),

        _p31s("j31-pb-failure", "Failure, wrapped", "Hard",
              "Submit a task that throws `IllegalStateException(\"bad \" + k)`, catch the "
              "`ExecutionException` from `get()`, and print the cause's message and its "
              "simple class name. Then show the pool still works by running a second "
              "task.",
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
              "        Future<Integer> bad = pool.submit(() -> {\n"
              "            throw new IllegalStateException(\"bad \" + k);\n"
              "        });\n"
              "        try {\n"
              "            System.out.println(bad.get());\n"
              "        } catch (ExecutionException e) {\n"
              "            System.out.println(e.getCause().getMessage());\n"
              "            System.out.println(e.getCause().getClass().getSimpleName());\n"
              "        }\n"
              "        Future<Integer> good = pool.submit(() -> k + 1);\n"
              "        System.out.println(good.get());\n"
              "        pool.shutdown();",
              [_k31p(k, _nl(f"bad {k}", "IllegalStateException", k + 1))
               for k in _K31P],
              ["A lambda that only throws is still a `Callable<Integer>`.",
               "The failure surfaces at `get()`, not at `submit()`.",
               "`ExecutionException` is the wrapper; `getCause()` is the real "
               "exception.",
               "The print inside the try never runs.",
               "One failed task does not poison the pool - the second one runs "
               "normally."]),

        _p31s("j31-pb-done", "The receipt, afterwards", "Medium",
              "Submit a Callable, `get()` it, then report `isDone` and `isCancelled` - "
              "both of which are only worth asking once the answer is in.",
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
              "        Future<Integer> answer = pool.submit(() -> k * 11);\n"
              "        System.out.println(answer.get());\n"
              "        System.out.println(answer.isDone());\n"
              "        System.out.println(answer.isCancelled());\n"
              "        pool.shutdown();",
              [_k31p(k, _nl(k * 11, "true", "false")) for k in _K31P],
              ["`get()` blocks, so everything after it knows the task finished.",
               "`isDone()` is `true` - and would be for a failed or cancelled task too.",
               "`isCancelled()` is `false`: nobody cancelled this one.",
               "Asking `isDone()` before the get would race the pool.",
               "Module 29 made the same point: NEW and TERMINATED were assertable, the "
               "middle was not."]),

        _p31s("j31-pb-rejected", "After the door shuts", "Medium",
              "Run one task, shut the pool down, then try to submit another and catch the "
              "unchecked `RejectedExecutionException`. Print the first result, "
              "`rejected`, and the slot again.",
              "        int k = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
              "        pool.submit(() -> {\n"
              "            out[0] = k * 9;\n"
              "        }).get();\n"
              "        System.out.println(out[0]);\n"
              "        pool.shutdown();\n"
              "        try {\n"
              "            pool.execute(() -> out[0] = -1);\n"
              "            System.out.println(\"accepted\");\n"
              "        } catch (RejectedExecutionException e) {\n"
              "            System.out.println(\"rejected\");\n"
              "        }\n"
              "        System.out.println(out[0]);",
              [_k31p(k, _nl(k * 9, "rejected", k * 9)) for k in _K31P],
              ["`pool.submit(...).get()` submits and waits in one expression.",
               "`RejectedExecutionException` is unchecked, so catching it is a choice.",
               "`accepted` sits after the throwing call, so it never runs.",
               "The rejected task never executes, so the slot keeps its earlier value.",
               "Rejecting loudly is far better than silently dropping the work."]),

        _p31s("j31-pb-finally", "Shut it down in a finally", "Medium",
              "Compute `k * 12` in a task, print it, and guarantee the shutdown with a "
              "`finally` that prints `closed`. Then print `isShutdown`.",
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(1);\n"
              "        try {\n"
              "            Future<Integer> answer = pool.submit(() -> k * 12);\n"
              "            System.out.println(answer.get());\n"
              "        } finally {\n"
              "            pool.shutdown();\n"
              "            System.out.println(\"closed\");\n"
              "        }\n"
              "        System.out.println(pool.isShutdown());",
              [_k31p(k, _nl(k * 12, "closed", "true")) for k in _K31P],
              ["The pool is created before the try, so the finally can always see it.",
               "Same shape as `lock()` outside the try in module 30.",
               "A leaked pool hangs the JVM, exactly as a leaked lock hangs the next "
               "thread.",
               "`closed` prints after the result, on every path.",
               "From Java 19 `ExecutorService` is `AutoCloseable`, so try-with-resources "
               "works too."]),
    ])


# ===========================================================================
# Family C - results in order
# ===========================================================================

_P31_C = _jfam(
    "p31-order", "Results in submission order",
    "The one pattern that makes concurrent output something you can test.",
    """
```java
List<Future<Integer>> fs = new ArrayList<>();
for (...) fs.add(pool.submit(task));       // submission order
for (Future<Integer> f : fs) f.get();      // ...is output order
```

Task 3 may finish long before task 0. It makes no difference: the second loop
asks for task 0 first and blocks until it has it.

`invokeAll` does the same thing in one call, and its returned list is **in
argument order**, not completion order.

What never works is letting tasks append to a shared list: an `ArrayList` is not
thread-safe, and even a safe one would give you completion order.
""",
    [
        _p31s("j31-pc-futures", "A list of receipts", "Medium",
              "Submit `k` Callables where task `i` returns `i * 5`, keeping the futures "
              "in submission order, then print `index value` per task and the total.",
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
              "        List<Future<Integer>> futures = new ArrayList<>();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            futures.add(pool.submit(() -> idx * 5));\n"
              "        }\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            int value = futures.get(i).get();\n"
              "            System.out.println(i + \" \" + value);\n"
              "            total += value;\n"
              "        }\n"
              "        pool.shutdown();\n"
              "        System.out.println(total);",
              [_k31p(k, _nl(*([f"{i} {i * 5}" for i in range(k)]
                              + [sum(i * 5 for i in range(k))]))) for k in _K31P],
              ["The list holds handles, not answers: `List<Future<Integer>>`.",
               "Adding inside the submission loop is what fixes the order.",
               "`futures.get(i).get()` is the list's get, then the future's.",
               "The loop blocks on task 0 first even if task 3 finished long ago.",
               "Concurrent work, ordered answers."]),

        _p31s("j31-pc-invokeall", "One call, every answer", "Medium",
              "Build a `List<Callable<Integer>>` where task `i` returns `i * i`, pass it "
              "to `invokeAll`, and print each result in order then the total.",
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
              "        List<Callable<Integer>> tasks = new ArrayList<>();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            tasks.add(() -> idx * idx);\n"
              "        }\n"
              "        List<Future<Integer>> done = pool.invokeAll(tasks);\n"
              "        int total = 0;\n"
              "        for (Future<Integer> f : done) {\n"
              "            int value = f.get();\n"
              "            System.out.println(value);\n"
              "            total += value;\n"
              "        }\n"
              "        pool.shutdown();\n"
              "        System.out.println(total);",
              [_k31p(k, _nl(*([str(i * i) for i in range(k)]
                              + [sum(i * i for i in range(k))]))) for k in _K31P],
              ["The list element type `Callable<Integer>` is what makes the lambdas "
               "Callables.",
               "`invokeAll` submits everything and blocks until all of it is done.",
               "Its returned list is in ARGUMENT order - that is the guarantee being "
               "used.",
               "So every `get()` afterwards returns immediately.",
               "The total is the sum of the squares below `k`."]),

        _p31s("j31-pc-chunks", "A chunked sum", "Hard",
              "Read `n` values then `k`. Give chunk `i` - indices "
              "`[i*n/k, (i+1)*n/k)` - to its own Callable, collect with `invokeAll`, and "
              "print `index sum` per chunk then the grand total.",
              "        int n = sc.nextInt();\n"
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
              "        System.out.println(total);",
              [_akcase(a, k, _nl(*([f"{i} {sum(a[i * len(a) // k:(i + 1) * len(a) // k])}"
                                    for i in range(k)] + [sum(a)])))
               for (a, k) in ((_A31P[0], 3), (_A31P[1], 1), (_A31P[2], 2),
                              (_A31P[3], 2), (_A31P[4], 3))],
              ["Chunk bounds are module 29's: `i*n/k` and `(i+1)*n/k`.",
               "Copy them into `final` locals for the lambda to capture.",
               "The braced lambda needs an explicit `return sum;` - that return is what "
               "makes it a Callable.",
               "Compare with module 29: no `int[] parts`, no `Thread[]`, no join loop.",
               "An empty chunk returns 0, which is right and needs no special case."]),

        _p31s("j31-pc-words", "Longest word per chunk", "Hard",
              "Read `n` words then `k`. Each chunk returns the LENGTH of its longest "
              "word (0 for an empty chunk). Collect with `invokeAll` and print each "
              "chunk's answer in order, then the largest of them.",
              "        int n = sc.nextInt();\n"
              "        String[] words = new String[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            words[i] = sc.next();\n"
              "        }\n"
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
              "        List<Callable<Integer>> tasks = new ArrayList<>();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int from = i * n / k;\n"
              "            final int to = (i + 1) * n / k;\n"
              "            tasks.add(() -> {\n"
              "                int best = 0;\n"
              "                for (int j = from; j < to; j++) {\n"
              "                    if (words[j].length() > best) {\n"
              "                        best = words[j].length();\n"
              "                    }\n"
              "                }\n"
              "                return best;\n"
              "            });\n"
              "        }\n"
              "        List<Future<Integer>> done = pool.invokeAll(tasks);\n"
              "        int overall = 0;\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            int best = done.get(i).get();\n"
              "            System.out.println(i + \" \" + best);\n"
              "            if (best > overall) {\n"
              "                overall = best;\n"
              "            }\n"
              "        }\n"
              "        pool.shutdown();\n"
              "        System.out.println(overall);",
              [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                     _nl(*([f"{i} {max([len(w) for w in ws[i * len(ws) // k:(i + 1) * len(ws) // k]] + [0])}"
                            for i in range(k)]
                           + [max(len(w) for w in ws)])))
               for (ws, k) in ((_W31P[0], 3), (_W31P[1], 1), (_W31P[2], 2),
                               (_W31P[3], 3), (_W31P[4], 2))],
              ["Start `best` at 0 so an empty chunk answers 0 without a special case.",
               "The comparison is on `length()`, and the answer is the length, not the "
               "word.",
               "`invokeAll` gives the chunk answers back in chunk order.",
               "Main combines them - the reduce step is single-threaded and trivial.",
               "Splitting a max this way works because max is associative, exactly like "
               "sum."]),

        _p31s("j31-pc-slots", "Futures for waiting only", "Medium",
              "Sometimes the answers belong in an array you already have. Submit `k` "
              "tasks writing `i * 4` into `parts[i]`, keep the futures only to wait on, "
              "then print the array.",
              "        int k = sc.nextInt();\n"
              "        int[] parts = new int[k];\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
              "        List<Future<?>> futures = new ArrayList<>();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            futures.add(pool.submit(() -> {\n"
              "                parts[idx] = idx * 4;\n"
              "            }));\n"
              "        }\n"
              "        for (Future<?> f : futures) {\n"
              "            f.get();\n"
              "        }\n"
              "        pool.shutdown();\n"
              "        System.out.println(Arrays.toString(parts));",
              [_k31p(k, _jarr([i * 4 for i in range(k)])) for k in _K31P],
              ["`Future<?>` because the results are not wanted - only the waiting.",
               "The braces make each lambda a `Runnable` rather than a Callable.",
               "Each task owns one slot, so nothing needs synchronising.",
               "The `get()` calls both wait and publish.",
               "`awaitTermination` would do the same job less precisely."]),
    ])


# ===========================================================================
# Family D - concurrent collections
# ===========================================================================

_P31_D = _jfam(
    "p31-concurrent", "The concurrent collections",
    "Atomic compound operations, and printing something whose order is undefined.",
    """
```java
map.putIfAbsent(k, v);            // the check-then-act, atomically
map.merge(k, 1, Integer::sum);    // the frequency count, atomically
map.computeIfAbsent(k, x -> ...); // build-on-demand, atomically
map.put(k, map.get(k) + 1);       // WRONG - two calls, still a race
```

A thread-safe collection guarantees each **call**. A sequence of two is exactly
the module 30 race, whatever the collection.

And printing: a `ConcurrentHashMap`'s iteration order is as undefined as a
`HashMap`'s, so every variant here goes through `new TreeMap<>(map)`.
""",
    [
        _p31s("j31-pd-merge", "A concurrent frequency table", "Hard",
              "Read `n` words and count how many share each length, from a pool, using "
              "`merge` so each update is a single atomic call. Print through a `TreeMap`, "
              "then the number of distinct lengths.",
              _RD_W31P
              + "        ConcurrentHashMap<Integer, Integer> counts = new ConcurrentHashMap<>();\n"
                "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                "        for (String w : words) {\n"
                "            pool.execute(() -> counts.merge(w.length(), 1, Integer::sum));\n"
                "        }\n"
                "        pool.shutdown();\n"
                "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
                "        System.out.println(new TreeMap<>(counts));\n"
                "        System.out.println(counts.size());",
              [_w31p(ws, _nl(_hist31p(ws), len({len(w) for w in ws})))
               for ws in _W31P],
              ["`merge(key, 1, Integer::sum)` inserts 1 when absent and otherwise sums - "
               "in one atomic call.",
               "`map.put(k, map.get(k) + 1)` would race however concurrent the map is.",
               "`w` in the enhanced `for` is effectively final, so the lambda captures "
               "it directly.",
               "`new TreeMap<>(counts)` gives the print a defined order.",
               "`size()` is the number of distinct lengths, not the number of words."]),

        _p31s("j31-pd-putifabsent", "First claim wins", "Medium",
              "Read `n` words and let the first word with each first letter claim it, "
              "using `putIfAbsent`. Print the claims through a `TreeMap`, then the size.",
              _RD_W31P
              + "        ConcurrentHashMap<String, String> owner = new ConcurrentHashMap<>();\n"
                "        for (String w : words) {\n"
                "            owner.putIfAbsent(w.substring(0, 1), w);\n"
                "        }\n"
                "        System.out.println(new TreeMap<>(owner));\n"
                "        System.out.println(owner.size());",
              [_w31p(ws, _nl("{" + ", ".join(
                  f"{k}={v}" for k, v in sorted({w[0]: w for w in reversed(ws)}.items()))
                  + "}", len({w[0] for w in ws}))) for ws in _W31P],
              ["`putIfAbsent` is the atomic form of "
               "`if (!map.containsKey(k)) map.put(k, v);`.",
               "The first word with a given letter keeps the key; later ones change "
               "nothing.",
               "`w.substring(0, 1)` gives a one-character String key.",
               "Print through a `TreeMap` for alphabetical rather than undefined order.",
               "The size is the number of distinct first letters."]),

        _p31s("j31-pd-computeifabsent", "Build it once, on demand", "Hard",
              "`computeIfAbsent` runs the supplier only when the key is missing. Group "
              "the words by length into lists, then print the groups through a `TreeMap` "
              "and the number of groups.",
              _RD_W31P
              + "        ConcurrentHashMap<Integer, List<String>> groups = new ConcurrentHashMap<>();\n"
                "        for (String w : words) {\n"
                "            groups.computeIfAbsent(w.length(), len -> new ArrayList<>()).add(w);\n"
                "        }\n"
                "        System.out.println(new TreeMap<>(groups));\n"
                "        System.out.println(groups.size());",
              [_w31p(ws, _nl("{" + ", ".join(
                  f"{ln}=[" + ", ".join(w for w in ws if len(w) == ln) + "]"
                  for ln in sorted({len(w) for w in ws})) + "}",
                  len({len(w) for w in ws}))) for ws in _W31P],
              ["`computeIfAbsent` returns the existing value, or the one it just built.",
               "So the `.add(w)` chains straight onto whichever list that is.",
               "The lambda takes the KEY as its argument, even when it ignores it.",
               "This is module 27's `groupingBy`, written by hand on a concurrent map.",
               "The lists themselves are plain ArrayLists, which is safe here only "
               "because this loop is single-threaded."]),

        _p31s("j31-pd-cow", "Copy-on-write", "Medium",
              "Add every word to a `CopyOnWriteArrayList` from a pool. The SIZE is "
              "reliable; the ORDER is completion order and must not be relied on - so "
              "sort a copy before printing. Print the size, the sorted list, and its "
              "first element.",
              _RD_W31P
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
                "        System.out.println(sorted.get(0));",
              [_w31p(ws, _nl(len(ws), "[" + ", ".join(sorted(ws)) + "]", sorted(ws)[0]))
               for ws in _W31P],
              ["A plain `ArrayList` here could lose entries or corrupt itself outright.",
               "`CopyOnWriteArrayList.add` is safe, so the size is reliable.",
               "The order is whichever task got there first - never printable as is.",
               "Copy into an `ArrayList` and `Collections.sort` before printing.",
               "Every write copies the whole array, so this class is for read-heavy use "
               "only."]),

        _p31s("j31-pd-report", "Counts and totals together", "Hard",
              "Read `n` words. From a pool, merge each word's length into a shared "
              "concurrent histogram AND accumulate the total character count in an "
              "`AtomicInteger`. Print the histogram through a `TreeMap`, the distinct "
              "count, and the total characters.",
              _RD_W31P
              + "        ConcurrentHashMap<Integer, Integer> counts = new ConcurrentHashMap<>();\n"
                "        java.util.concurrent.atomic.AtomicInteger chars =\n"
                "                new java.util.concurrent.atomic.AtomicInteger();\n"
                "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                "        for (String w : words) {\n"
                "            pool.execute(() -> {\n"
                "                counts.merge(w.length(), 1, Integer::sum);\n"
                "                chars.addAndGet(w.length());\n"
                "            });\n"
                "        }\n"
                "        pool.shutdown();\n"
                "        pool.awaitTermination(1, TimeUnit.MINUTES);\n"
                "        System.out.println(new TreeMap<>(counts));\n"
                "        System.out.println(counts.size());\n"
                "        System.out.println(chars.get());",
              [_w31p(ws, _nl(_hist31p(ws), len({len(w) for w in ws}),
                             sum(len(w) for w in ws))) for ws in _W31P],
              ["Two shared structures, each updated by a single atomic call.",
               "`merge` for the map, `addAndGet` for the counter - never a get followed "
               "by a set.",
               "Both are read only after `awaitTermination`, so every update is "
               "published.",
               "The histogram is printed through a `TreeMap`; the AtomicInteger needs no "
               "such care.",
               "The character total is the sum of every word's length."]),
    ])


# ===========================================================================
# Family E - putting it together
# ===========================================================================

_P31_E = _jfam(
    "p31-together", "Whole pipelines",
    "Split, submit, collect in order, shut down - the shape of the module.",
    """
Every variant here is the same five steps:

1. read the input on the main thread;
2. split it into `k` chunks with `i*n/k` and `(i+1)*n/k`;
3. submit one `Callable` per chunk;
4. collect with `invokeAll` and read the futures **in order**;
5. shut the pool down, in a `finally`.

Anything shared between the tasks is updated with a single atomic call and
printed sorted.
""",
    [
        _p31s("j31-pe-sumchunks", "Sum, by chunk", "Medium",
              "Read `n` values then `k`; sum each chunk in its own Callable, and print "
              "`index sum` in order followed by the total. Shut the pool down in a "
              "`finally`.",
              "        int n = sc.nextInt();\n"
              "        int[] a = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            a[i] = sc.nextInt();\n"
              "        }\n"
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
              "        try {\n"
              "            List<Callable<Integer>> tasks = new ArrayList<>();\n"
              "            for (int i = 0; i < k; i++) {\n"
              "                final int from = i * n / k;\n"
              "                final int to = (i + 1) * n / k;\n"
              "                tasks.add(() -> {\n"
              "                    int sum = 0;\n"
              "                    for (int j = from; j < to; j++) {\n"
              "                        sum += a[j];\n"
              "                    }\n"
              "                    return sum;\n"
              "                });\n"
              "            }\n"
              "            List<Future<Integer>> done = pool.invokeAll(tasks);\n"
              "            int total = 0;\n"
              "            for (int i = 0; i < k; i++) {\n"
              "                int part = done.get(i).get();\n"
              "                System.out.println(i + \" \" + part);\n"
              "                total += part;\n"
              "            }\n"
              "            System.out.println(total);\n"
              "        } finally {\n"
              "            pool.shutdown();\n"
              "        }",
              [_akcase(a, k, _nl(*([f"{i} {sum(a[i * len(a) // k:(i + 1) * len(a) // k])}"
                                    for i in range(k)] + [sum(a)])))
               for (a, k) in ((_A31P[0], 3), (_A31P[1], 1), (_A31P[2], 2),
                              (_A31P[3], 2), (_A31P[4], 3))],
              ["Read all the input first - a Scanner is not shareable.",
               "`final int from` and `final int to` inside the loop.",
               "`invokeAll` blocks until every chunk is finished.",
               "Walk `done` by index so the output is in chunk order.",
               "The `finally` guarantees the pool is shut down even if a get throws."]),

        _p31s("j31-pe-countpositive", "Counting, by chunk", "Medium",
              "Same shape: each chunk returns how many of its values are positive. Print "
              "each chunk's count in order, then the total.",
              "        int n = sc.nextInt();\n"
              "        int[] a = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            a[i] = sc.nextInt();\n"
              "        }\n"
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
              "        try {\n"
              "            List<Callable<Integer>> tasks = new ArrayList<>();\n"
              "            for (int i = 0; i < k; i++) {\n"
              "                final int from = i * n / k;\n"
              "                final int to = (i + 1) * n / k;\n"
              "                tasks.add(() -> {\n"
              "                    int count = 0;\n"
              "                    for (int j = from; j < to; j++) {\n"
              "                        if (a[j] > 0) {\n"
              "                            count++;\n"
              "                        }\n"
              "                    }\n"
              "                    return count;\n"
              "                });\n"
              "            }\n"
              "            List<Future<Integer>> done = pool.invokeAll(tasks);\n"
              "            int total = 0;\n"
              "            for (int i = 0; i < k; i++) {\n"
              "                int part = done.get(i).get();\n"
              "                System.out.println(i + \" \" + part);\n"
              "                total += part;\n"
              "            }\n"
              "            System.out.println(total);\n"
              "        } finally {\n"
              "            pool.shutdown();\n"
              "        }",
              [_akcase(a, k, _nl(*([f"{i} {sum(1 for v in a[i * len(a) // k:(i + 1) * len(a) // k] if v > 0)}"
                                    for i in range(k)]
                                   + [sum(1 for v in a if v > 0)])))
               for (a, k) in ((_A31P[0], 3), (_A31P[1], 1), (_A31P[2], 2),
                              (_A31P[3], 2), (_A31P[4], 3))],
              ["`count` is a local of the lambda, so no two tasks share it.",
               "A shared counter here would need an atomic; a returned value needs "
               "nothing.",
               "That is the general lesson: return per-task answers rather than "
               "accumulating into shared state.",
               "The chunk counts add up to the whole array's count.",
               "Negative and zero values are not counted."]),

        _p31s("j31-pe-charcount", "Characters, by chunk", "Medium",
              "Read `n` words then `k`; each chunk returns its total character count. "
              "Print each in order, then the grand total.",
              _RD_W31P
              + "        int k = sc.nextInt();\n"
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
                "                    }\n"
                "                    return chars;\n"
                "                });\n"
                "            }\n"
                "            List<Future<Integer>> done = pool.invokeAll(tasks);\n"
                "            int total = 0;\n"
                "            for (int i = 0; i < k; i++) {\n"
                "                int part = done.get(i).get();\n"
                "                System.out.println(i + \" \" + part);\n"
                "                total += part;\n"
                "            }\n"
                "            System.out.println(total);\n"
                "        } finally {\n"
                "            pool.shutdown();\n"
                "        }",
              [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                     _nl(*([f"{i} {sum(len(w) for w in ws[i * len(ws) // k:(i + 1) * len(ws) // k])}"
                            for i in range(k)]
                           + [sum(len(w) for w in ws)])))
               for (ws, k) in ((_W31P[0], 3), (_W31P[1], 1), (_W31P[2], 2),
                               (_W31P[3], 3), (_W31P[4], 2))],
              ["The words array is read on the main thread before any task starts.",
               "`start()` - or here, submission - publishes those writes to the tasks.",
               "Each chunk accumulates into its own local and returns it.",
               "`invokeAll` hands the answers back in chunk order.",
               "The grand total is every word's length added up."]),

        _p31s("j31-pe-both", "Per-chunk answers and a shared map", "Hard",
              "Read `n` words then `k`. Each chunk returns its word COUNT, and every "
              "task also merges its words' lengths into a shared concurrent histogram. "
              "Print each chunk's count in order, the total, the histogram sorted, and "
              "the number of distinct lengths.",
              _RD_W31P
              + "        int k = sc.nextInt();\n"
                "        ConcurrentHashMap<Integer, Integer> hist = new ConcurrentHashMap<>();\n"
                "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
                "        try {\n"
                "            List<Callable<Integer>> tasks = new ArrayList<>();\n"
                "            for (int i = 0; i < k; i++) {\n"
                "                final int from = i * n / k;\n"
                "                final int to = (i + 1) * n / k;\n"
                "                tasks.add(() -> {\n"
                "                    for (int j = from; j < to; j++) {\n"
                "                        hist.merge(words[j].length(), 1, Integer::sum);\n"
                "                    }\n"
                "                    return to - from;\n"
                "                });\n"
                "            }\n"
                "            List<Future<Integer>> done = pool.invokeAll(tasks);\n"
                "            int total = 0;\n"
                "            for (int i = 0; i < k; i++) {\n"
                "                int part = done.get(i).get();\n"
                "                System.out.println(i + \" \" + part);\n"
                "                total += part;\n"
                "            }\n"
                "            System.out.println(total);\n"
                "            System.out.println(new TreeMap<>(hist));\n"
                "            System.out.println(hist.size());\n"
                "        } finally {\n"
                "            pool.shutdown();\n"
                "        }",
              [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                     _nl(*([f"{i} {(i + 1) * len(ws) // k - i * len(ws) // k}"
                            for i in range(k)]
                           + [len(ws), _hist31p(ws), len({len(w) for w in ws})])))
               for (ws, k) in ((_W31P[0], 3), (_W31P[1], 1), (_W31P[2], 2),
                               (_W31P[3], 3), (_W31P[4], 2))],
              ["Two kinds of result at once: a returned per-chunk value and a shared "
               "structure.",
               "The chunk size is simply `to - from`, and they sum to `n`.",
               "The shared histogram is only ever touched with a single atomic `merge`.",
               "The futures give the chunk counts in order; the map is printed sorted.",
               "That combination - return what is per-task, share only what must be "
               "shared - is the whole module."]),

        _p31s("j31-pe-maxchunk", "The largest chunk", "Hard",
              "Read `n` values then `k`; each chunk returns its own maximum, using "
              "`Integer.MIN_VALUE` as the starting point so negative values work. Print "
              "each chunk's maximum in order, then the largest overall. Every chunk here "
              "has at least one element.",
              "        int n = sc.nextInt();\n"
              "        int[] a = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            a[i] = sc.nextInt();\n"
              "        }\n"
              "        int k = sc.nextInt();\n"
              "        ExecutorService pool = Executors.newFixedThreadPool(2);\n"
              "        try {\n"
              "            List<Callable<Integer>> tasks = new ArrayList<>();\n"
              "            for (int i = 0; i < k; i++) {\n"
              "                final int from = i * n / k;\n"
              "                final int to = (i + 1) * n / k;\n"
              "                tasks.add(() -> {\n"
              "                    int best = Integer.MIN_VALUE;\n"
              "                    for (int j = from; j < to; j++) {\n"
              "                        if (a[j] > best) {\n"
              "                            best = a[j];\n"
              "                        }\n"
              "                    }\n"
              "                    return best;\n"
              "                });\n"
              "            }\n"
              "            List<Future<Integer>> done = pool.invokeAll(tasks);\n"
              "            int overall = Integer.MIN_VALUE;\n"
              "            for (int i = 0; i < k; i++) {\n"
              "                int best = done.get(i).get();\n"
              "                System.out.println(i + \" \" + best);\n"
              "                if (best > overall) {\n"
              "                    overall = best;\n"
              "                }\n"
              "            }\n"
              "            System.out.println(overall);\n"
              "        } finally {\n"
              "            pool.shutdown();\n"
              "        }",
              [_akcase(a, k, _nl(*([f"{i} {max(a[i * len(a) // k:(i + 1) * len(a) // k])}"
                                    for i in range(k)] + [max(a)])))
               for (a, k) in ((_A31P[0], 3), (_A31P[1], 1), (_A31P[2], 2),
                              (_A31P[3], 2), (_A31P[4], 3))],
              ["Starting at 0 would be wrong for an all-negative chunk - use "
               "`Integer.MIN_VALUE`.",
               "Each chunk's maximum is computed entirely in a local.",
               "Main takes the maximum of the maxima, which works because max is "
               "associative.",
               "The futures are read in chunk order, so the per-chunk lines are "
               "reproducible.",
               "Every test here gives each chunk at least one element, so no chunk "
               "returns MIN_VALUE."]),
    ])


_PRACTICE[31] = [_P31_A, _P31_B, _P31_C, _P31_D, _P31_E]
