# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 29 practice - threads, and what they cost.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[29]`.
#
# Same gate as the module file: no `synchronized`, no `volatile`, no atomics, no
# locks (module 30), and no executors, `Callable` or `Future` (module 31).
#
# And the same determinism discipline, which matters more here than anywhere
# else in the course: every one of these 25 programs is graded by exact stdout
# comparison, so not one of them may depend on the scheduler. Concretely -
#
#   * no two threads ever write the same variable;
#   * every read of a worker's result sits behind that worker's `join()`;
#   * workers never print, except where the thread NAME is the answer and the
#     threads are run strictly one at a time.
#
# The five families are the five lessons: making a thread, the shared heap and
# the private stack, the lifecycle, sleep/join/interrupt, and pinning down the
# output order.
# ---------------------------------------------------------------------------

_IMPORTS29P = "import java.util.*;\n"

_SIG29P = "    public static void main(String[] args) throws InterruptedException {"


def _p29prog(body):
    return _jcls(
        _SIG29P + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }",
        imports=_IMPORTS29P,
    )


def _p29t(types, body):
    """Helper classes above Main."""
    return _jp(
        _IMPORTS29P + "\n"
        + types.rstrip("\n") + "\n\n"
        + "public class Main {\n"
        + _SIG29P + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }\n}"
    )


def _p29s(eid, title, difficulty, prompt, body, tests, hints):
    """Write main's whole body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p29prog(body), body, tests, hints)


def _p29c(eid, title, difficulty, prompt, types, body, tests, hints):
    """Write main's body; the helper classes are given."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p29t(types, body), body, tests, hints)


_NS29P = (1, 4, 6, 9, 3)
_WS29P = ("ada", "bo", "cy", "dee", "eli")
_AS29P = ([2, 5, 1], [7], [3, 3, 3, 3], [8, -4, 6], [1, 2, 3, 4, 5, 6])


def _n29p(n, out):
    return _case(str(n), out)


def _w29p(s, out):
    return _case(s, out)


def _tri29p(n):
    return n * (n + 1) // 2


# ===========================================================================
# Family A - making a thread and running it
# ===========================================================================

_P29_A = _jfam(
    "p29-make", "Making one, and running it",
    "Build a Thread around a Runnable, start it, join it, read the result.",
    """
The base motion of the whole module, and every variant is a twist on it:

```java
int[] out = new int[1];
Thread t = new Thread(() -> out[0] = n * 2, "worker");
t.start();
t.join();
System.out.println(out[0]);
```

Four steps, always in this order. **Construct** (nothing runs yet), **start**
(the JVM makes a thread, which calls `run()`), **join** (wait, and make the
worker's writes visible), **read**. Drop the join and the read is no longer a
legal thing to do.

The variants change what the worker computes and how the work is expressed - a
lambda, a named `Runnable`, a `Thread` subclass - but never that order.
""",
    [
        _p29s("j29-pa-double", "Double it on a thread", "Easy",
              "Read `n`, compute `n * 2` on a worker thread named `worker`, and print it "
              "from main after joining.",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        Thread t = new Thread(() -> out[0] = n * 2, \"worker\");\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(out[0]);",
              [_n29p(n, str(n * 2)) for n in _NS29P],
              ["A one-element array is the simplest way to get a value out of a lambda.",
               "The lambda captures `out` and `n`, and neither is ever reassigned.",
               "`new Thread(runnable, \"worker\")`.",
               "Join before you print, always.",
               "Main does the printing, not the worker."]),

        _p29s("j29-pa-sum", "The triangular number", "Easy",
              "Read `n` and sum `1..n` on a worker thread, accumulating into a local "
              "inside the lambda and writing the slot once at the end.",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        Thread t = new Thread(() -> {\n"
              "            int sum = 0;\n"
              "            for (int i = 1; i <= n; i++) {\n"
              "                sum += i;\n"
              "            }\n"
              "            out[0] = sum;\n"
              "        }, \"worker\");\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(out[0]);",
              [_n29p(n, str(_tri29p(n))) for n in _NS29P],
              ["The braced lambda body is needed because it is several statements.",
               "`sum` is a local of the lambda, so it lives on the worker's own stack.",
               "Write `out[0]` once, at the end - not inside the loop.",
               "You cannot accumulate into `out[0]` directly and gain anything; a local "
               "is clearer and cheaper.",
               "For n = 4 the answer is 10."]),

        _p29c("j29-pa-named", "A named Runnable", "Easy",
              "`Squarer` implements `Runnable` and writes its square into the array it "
              "was given. Run one on a thread named `worker` and print the result.",
              "class Squarer implements Runnable {\n"
              "    private final int value;\n"
              "    private final int[] out;\n\n"
              "    Squarer(int value, int[] out) {\n"
              "        this.value = value;\n"
              "        this.out = out;\n"
              "    }\n\n"
              "    @Override\n"
              "    public void run() {\n"
              "        out[0] = value * value;\n"
              "    }\n"
              "}",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        Thread t = new Thread(new Squarer(n, out), \"worker\");\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(out[0]);",
              [_n29p(n, str(n * n)) for n in _NS29P],
              ["A `Runnable` is the work; a `Thread` is what runs it.",
               "`new Thread(new Squarer(n, out), \"worker\")`.",
               "The Runnable is handed the array in its constructor - that is how it "
               "reports back.",
               "`run()` returns nothing, which is exactly why the array is needed.",
               "Module 31's `Callable` is the version that can just return a value."]),

        _p29c("j29-pa-extends", "A Thread subclass", "Medium",
              "`Tripler` extends `Thread` and stores its answer in a field. Start it, "
              "join it, then read the field - the join is what makes that read legal.",
              "class Tripler extends Thread {\n"
              "    private final int value;\n"
              "    private int result;\n\n"
              "    Tripler(int value) {\n"
              "        this.value = value;\n"
              "    }\n\n"
              "    int getResult() {\n"
              "        return result;\n"
              "    }\n\n"
              "    @Override\n"
              "    public void run() {\n"
              "        result = value * 3;\n"
              "    }\n"
              "}",
              "        int n = sc.nextInt();\n"
              "        Tripler t = new Tripler(n);\n"
              "        t.setName(\"tripler\");\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(t.getResult());\n"
              "        System.out.println(t.getName());",
              [_n29p(n, _nl(n * 3, "tripler")) for n in _NS29P],
              ["`Tripler` IS-A Thread, so it has `start`, `join`, `setName` and "
               "`getName` already.",
               "Name it before starting it.",
               "Reading `getResult()` after `join()` is safe; before, it would not be.",
               "The field is plain - no `volatile` needed, because the join publishes it.",
               "This works, and is still the design module 29 argues against: the task is "
               "welded to the thread."]),

        _p29s("j29-pa-two", "Two threads, two slots", "Medium",
              "Read `n`. One worker writes `n + 1` into slot 0, another writes `n * n` "
              "into slot 1. Start both, join both, print both slots and then their sum.",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[2];\n"
              "        Thread a = new Thread(() -> out[0] = n + 1, \"a\");\n"
              "        Thread b = new Thread(() -> out[1] = n * n, \"b\");\n"
              "        a.start();\n"
              "        b.start();\n"
              "        a.join();\n"
              "        b.join();\n"
              "        System.out.println(out[0]);\n"
              "        System.out.println(out[1]);\n"
              "        System.out.println(out[0] + out[1]);",
              [_n29p(n, _nl(n + 1, n * n, (n + 1) + n * n)) for n in _NS29P],
              ["Start both before joining either, or they run one after the other.",
               "The two workers write DIFFERENT slots, so nothing is shared.",
               "Main prints, so the order of the output is main's decision, not the "
               "scheduler's.",
               "Both joins must happen before the first print.",
               "For n = 4: 5, 16, 21."]),
    ])


# ===========================================================================
# Family B - shared heap, private stack
# ===========================================================================

_P29_B = _jfam(
    "p29-shared", "The shared heap and the private stack",
    "What a worker can see of yours, and what it keeps to itself.",
    """
Threads share the heap and share no stacks. So:

```java
int[] shared = new int[1];        // on the HEAP - the worker sees your writes
Runnable job = () -> {
    int local = 0;                // on the WORKER'S STACK - nobody else's
    ...
};
```

Give the same `Runnable` to two threads and you get **one** object with **two**
executions, each with its own copy of every local inside `run()`. That is why
the same job run twice produces the same answer twice, rather than the second
run continuing where the first left off.

Every variant below keeps writes separated - either one thread at a time, or
one slot each - because two threads writing one variable is module 30.
""",
    [
        _p29s("j29-pb-locals", "One job, two stacks", "Easy",
              "One `Runnable` that counts to 3 in a local and prints its thread's name "
              "and that local. Run it on thread `a`, join, then on thread `b`, join. "
              "Both print 3 - the second run does not continue the first.",
              "        int n = sc.nextInt();\n"
              "        Runnable job = () -> {\n"
              "            int local = 0;\n"
              "            for (int i = 0; i < 3; i++) {\n"
              "                local++;\n"
              "            }\n"
              "            System.out.println(Thread.currentThread().getName() + \" \" + local);\n"
              "        };\n"
              "        Thread a = new Thread(job, \"a\");\n"
              "        a.start();\n"
              "        a.join();\n"
              "        Thread b = new Thread(job, \"b\");\n"
              "        b.start();\n"
              "        b.join();\n"
              "        System.out.println(n);",
              [_n29p(n, _nl("a 3", "b 3", n)) for n in _NS29P],
              ["`local` is declared inside `run()`, so each execution gets a fresh one.",
               "Start-join-start-join, so the two printed lines cannot interleave.",
               "This is the ONE place a worker may print in this course - because only "
               "one is ever running.",
               "The same Runnable object is handed to both threads.",
               "If `local` were a field of a shared object instead, the second run would "
               "print 6 - and would be a race."]),

        _p29s("j29-pb-heap", "The worker sees your array", "Easy",
              "Fill an array with `1..n` on the main thread, then have a worker add up "
              "every element into slot 0 of a second array. Print the total after "
              "joining.",
              "        int n = sc.nextInt();\n"
              "        int[] data = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            data[i] = i + 1;\n"
              "        }\n"
              "        int[] out = new int[1];\n"
              "        Thread t = new Thread(() -> {\n"
              "            int sum = 0;\n"
              "            for (int v : data) {\n"
              "                sum += v;\n"
              "            }\n"
              "            out[0] = sum;\n"
              "        }, \"worker\");\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(out[0]);",
              [_n29p(n, str(_tri29p(n))) for n in _NS29P],
              ["`data` is an object on the heap, so the worker sees exactly the array "
               "main filled.",
               "Main finished writing `data` before `start()`, which is what makes those "
               "writes visible to the worker.",
               "`start()` publishes everything the starting thread did beforehand - the "
               "mirror image of `join()`.",
               "Accumulate into a local, then write the slot once.",
               "The answer is the triangular number of n."]),

        _p29s("j29-pb-mutate", "The worker writes into your array", "Medium",
              "Read `n` values into an array, then have a worker double every element "
              "in place. After joining, print the array with `Arrays.toString`.",
              "        int n = sc.nextInt();\n"
              "        int[] data = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            data[i] = sc.nextInt();\n"
              "        }\n"
              "        Thread t = new Thread(() -> {\n"
              "            for (int i = 0; i < data.length; i++) {\n"
              "                data[i] = data[i] * 2;\n"
              "            }\n"
              "        }, \"worker\");\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(Arrays.toString(data));",
              [_acase(a, _jarr([v * 2 for v in a])) for a in _AS29P],
              ["The array reference is captured; the array itself is shared memory.",
               "The worker mutates it in place - there is no copying anywhere.",
               "`data` is effectively final: the VARIABLE is never reassigned, even "
               "though its contents change.",
               "Only one thread touches the array at a time, so no synchronisation is "
               "needed.",
               "Print after the join, or you may see a half-doubled array."]),

        _p29s("j29-pb-slots", "A slot each, no sharing", "Medium",
              "Read `n` values. Give each element its own thread, which writes its cube "
              "into its own slot. Join them all, then print the slots one per line.",
              "        int n = sc.nextInt();\n"
              "        int[] data = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            data[i] = sc.nextInt();\n"
              "        }\n"
              "        int[] out = new int[n];\n"
              "        Thread[] workers = new Thread[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            final int idx = i;\n"
              "            workers[i] = new Thread(\n"
              "                    () -> out[idx] = data[idx] * data[idx] * data[idx], \"w\" + idx);\n"
              "            workers[i].start();\n"
              "        }\n"
              "        for (Thread w : workers) {\n"
              "            w.join();\n"
              "        }\n"
              "        for (int v : out) {\n"
              "            System.out.println(v);\n"
              "        }",
              [_acase(a, _nl(*[v ** 3 for v in a])) for a in _AS29P],
              ["`final int idx = i;` - the loop variable itself cannot be captured.",
               "Thread `i` writes only `out[i]`, so no two threads share a destination.",
               "Start them all first, then join them all.",
               "Main prints in index order, so the output does not depend on which "
               "thread finished first.",
               "Negative inputs cube to negative results - no special case needed."]),

        _p29s("j29-pb-count", "Counting without sharing a counter", "Hard",
              "Read `n` values and count how many are positive - but with one thread per "
              "element and no shared counter. Each thread writes 1 or 0 into its own "
              "slot; main adds the slots up after joining and prints the flags then the "
              "count.",
              "        int n = sc.nextInt();\n"
              "        int[] data = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            data[i] = sc.nextInt();\n"
              "        }\n"
              "        int[] flags = new int[n];\n"
              "        Thread[] workers = new Thread[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            final int idx = i;\n"
              "            workers[i] = new Thread(\n"
              "                    () -> flags[idx] = data[idx] > 0 ? 1 : 0, \"w\" + idx);\n"
              "            workers[i].start();\n"
              "        }\n"
              "        for (Thread w : workers) {\n"
              "            w.join();\n"
              "        }\n"
              "        int count = 0;\n"
              "        for (int f : flags) {\n"
              "            System.out.print(f);\n"
              "            count += f;\n"
              "        }\n"
              "        System.out.println();\n"
              "        System.out.println(count);",
              [_acase(a, _nl("".join("1" if v > 0 else "0" for v in a),
                             sum(1 for v in a if v > 0))) for a in _AS29P],
              ["A shared `count++` from many threads is module 30's data race - this "
               "avoids needing it at all.",
               "Each thread's answer is one bit, in its own slot.",
               "`System.out.print` for the flags, then an empty `println` to end the "
               "line.",
               "Main does the adding up, single-threaded, after every join.",
               "This 'map to slots, then reduce on one thread' shape is how you keep "
               "parallel work lock-free."]),
    ])


# ===========================================================================
# Family C - the lifecycle
# ===========================================================================

_P29_C = _jfam(
    "p29-life", "The lifecycle",
    "NEW before the start, TERMINATED after the join, and no way back.",
    """
Six states, two of them worth asserting on:

```java
Thread t = new Thread(job, "worker");
t.getState();     // NEW          - reliable
t.start();
t.join();
t.getState();     // TERMINATED   - reliable
t.isAlive();      // false
t.start();        // IllegalThreadStateException - single use
```

Anything sampled between those two points is a snapshot of something that has
probably already moved on, which is why none of these variants ask for one.
""",
    [
        _p29s("j29-pc-states", "Before and after", "Easy",
              "Print the worker's state, start and join it, print its state again, then "
              "its result.",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        Thread t = new Thread(() -> out[0] = n + 100, \"worker\");\n"
              "        System.out.println(t.getState());\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(t.getState());\n"
              "        System.out.println(out[0]);",
              [_n29p(n, _nl("NEW", "TERMINATED", n + 100)) for n in _NS29P],
              ["`Thread.State` is an enum; printing it gives the constant's name.",
               "Before `start()` it is NEW - never RUNNABLE.",
               "After `join()` returns, `run()` has definitely finished.",
               "Those are the only two states this course ever asserts on.",
               "The result read is legal because the join is between it and the write."]),

        _p29s("j29-pc-alive", "Alive on neither side", "Easy",
              "Print `isAlive()` before the start and after the join - `false` both "
              "times, for opposite reasons - with the worker's answer in between.",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        Thread t = new Thread(() -> out[0] = n * n * n, \"worker\");\n"
              "        System.out.println(t.isAlive());\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(out[0]);\n"
              "        System.out.println(t.isAlive());",
              [_n29p(n, _nl("false", n ** 3, "false")) for n in _NS29P],
              ["Not started yet: not alive.",
               "Already terminated: not alive.",
               "`isAlive()` is the coarse view of `getState()`.",
               "Polling `isAlive()` in a loop instead of joining is a busy-wait - "
               "correct, wasteful, and it publishes nothing.",
               "Print the result between the two checks."]),

        _p29s("j29-pc-restart", "It will not run twice", "Medium",
              "Run the worker, join it, then try to start it again and catch the "
              "`IllegalThreadStateException`. Print the result, `cannot restart`, and "
              "the final state.",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        Thread t = new Thread(() -> out[0] = n + 7, \"worker\");\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(out[0]);\n"
              "        try {\n"
              "            t.start();\n"
              "            System.out.println(\"restarted\");\n"
              "        } catch (IllegalThreadStateException e) {\n"
              "            System.out.println(\"cannot restart\");\n"
              "        }\n"
              "        System.out.println(t.getState());",
              [_n29p(n, _nl(n + 7, "cannot restart", "TERMINATED")) for n in _NS29P],
              ["`IllegalThreadStateException` is unchecked - catching it is optional.",
               "`restarted` is inside the try, after the throwing call, so it never "
               "runs.",
               "The failed start leaves the thread TERMINATED, unchanged.",
               "A Thread object is single-use, like a stream in module 26.",
               "To repeat the work, construct a second Thread around the same "
               "Runnable."]),

        _p29s("j29-pc-fresh", "A new Thread each time", "Medium",
              "Run the same `Runnable` twice, on two different Thread objects, one after "
              "the other. Each run adds `n` to slot 0, so the total is `2 * n`. Print "
              "each thread's state after its join, then the total.",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        Runnable job = () -> out[0] = out[0] + n;\n"
              "        Thread first = new Thread(job, \"first\");\n"
              "        first.start();\n"
              "        first.join();\n"
              "        System.out.println(first.getState());\n"
              "        Thread second = new Thread(job, \"second\");\n"
              "        second.start();\n"
              "        second.join();\n"
              "        System.out.println(second.getState());\n"
              "        System.out.println(out[0]);",
              [_n29p(n, _nl("TERMINATED", "TERMINATED", n * 2)) for n in _NS29P],
              ["One Runnable, two Threads - the work is reusable, the thread is not.",
               "Join the first before starting the second.",
               "That join is what makes `out[0] = out[0] + n` safe: the two "
               "read-modify-writes cannot overlap.",
               "Run them at the same time instead and this is the data race module 30 "
               "opens with.",
               "Both threads end TERMINATED; the total is `n + n`."]),

        _p29s("j29-pc-daemonflag", "The flag, and when it may change", "Hard",
              "The precise rule is `setDaemon` throws if the thread is ALIVE - not "
              "merely if it has been started. Print the worker's `isDaemon()`, set it "
              "while the worker is still NEW, print it again, run the worker, then try "
              "to change the flag on the MAIN thread, which certainly is alive.",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        Thread t = new Thread(() -> out[0] = n * 5, \"worker\");\n"
              "        System.out.println(t.isDaemon());\n"
              "        t.setDaemon(true);\n"
              "        System.out.println(t.isDaemon());\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(out[0]);\n"
              "        try {\n"
              "            Thread.currentThread().setDaemon(true);\n"
              "            System.out.println(\"main is a daemon now\");\n"
              "        } catch (IllegalThreadStateException e) {\n"
              "            System.out.println(\"cannot change a live thread\");\n"
              "        }",
              [_n29p(n, _nl("false", "true", n * 5, "cannot change a live thread"))
               for n in _NS29P],
              ["A thread created from a user thread is a user thread, so the first "
               "`isDaemon()` is `false`.",
               "While the worker is still NEW the flag may be set freely.",
               "Main is unquestionably alive, so changing ITS flag is the case that "
               "always throws - no timing involved.",
               "The javadoc condition is `isAlive()`, which is why setting the flag on "
               "an already-TERMINATED thread quietly succeeds instead of throwing.",
               "The practical rule is unchanged: put `setDaemon(true)` directly above "
               "`start()`, where it is always legal."]),
    ])


# ===========================================================================
# Family D - sleep, join, interrupt
# ===========================================================================

_P29_D = _jfam(
    "p29-wait", "`sleep`, `join` and the interrupt flag",
    "Waiting on purpose, and asking a thread to stop.",
    """
```java
Thread.sleep(50);        // STATIC - sleeps the CALLER. Throws InterruptedException.
worker.join();           // wait for worker AND see everything it wrote
t.interrupt();           // set a flag. Does not stop anything by itself.
```

The detail worth drilling until it is automatic: a blocking call that throws
`InterruptedException` **clears the flag on its way out**. So

```java
Thread.currentThread().interrupt();
System.out.println(Thread.currentThread().isInterrupted());   // true
try { Thread.sleep(50); } catch (InterruptedException e) { }   // throws AT ONCE
System.out.println(Thread.currentThread().isInterrupted());   // false
```

An empty catch block therefore throws away the only record that anyone asked
this thread to stop. Either act on it, or put the flag back.
""",
    [
        _p29s("j29-pd-sleepwake", "Sleeping is part of the work", "Easy",
              "The worker sleeps 30ms and only then writes its answer. Join it and print "
              "the answer - the join waits for the whole of `run()`, sleep included.",
              "        int n = sc.nextInt();\n"
              "        int[] out = new int[1];\n"
              "        Thread t = new Thread(() -> {\n"
              "            try {\n"
              "                Thread.sleep(30);\n"
              "            } catch (InterruptedException e) {\n"
              "                Thread.currentThread().interrupt();\n"
              "            }\n"
              "            out[0] = n * 11;\n"
              "        }, \"sleeper\");\n"
              "        t.start();\n"
              "        t.join();\n"
              "        System.out.println(out[0]);",
              [_n29p(n, str(n * 11)) for n in _NS29P],
              ["`run()` cannot declare `throws`, so the sleep is caught inside the "
               "lambda.",
               "Restoring the flag in the catch is the correct habit.",
               "`join()` returns only when `run()` returns.",
               "Reading the slot before the join would very likely print 0.",
               "'Very likely' is not something a program may depend on."]),

        _p29s("j29-pd-selfinterrupt", "The flag that clears itself", "Medium",
              "Interrupt the main thread, print the flag, then sleep - which throws at "
              "once and clears the flag. Print `interrupted` in the catch, then the flag "
              "again, then `n`.",
              "        int n = sc.nextInt();\n"
              "        Thread.currentThread().interrupt();\n"
              "        System.out.println(Thread.currentThread().isInterrupted());\n"
              "        try {\n"
              "            Thread.sleep(50);\n"
              "            System.out.println(\"slept\");\n"
              "        } catch (InterruptedException e) {\n"
              "            System.out.println(\"interrupted\");\n"
              "        }\n"
              "        System.out.println(Thread.currentThread().isInterrupted());\n"
              "        System.out.println(n);",
              [_n29p(n, _nl("true", "interrupted", "false", n)) for n in _NS29P],
              ["A thread can interrupt itself.",
               "Setting the flag alone does nothing - no exception, no stop.",
               "`sleep` on an already-interrupted thread throws immediately rather than "
               "sleeping.",
               "So `slept` never prints, and the 50ms never elapse.",
               "The throw clears the flag, which is why the last check is `false`."]),

        _p29s("j29-pd-restore", "Putting the flag back", "Medium",
              "Same as before, but restore the flag inside the catch with "
              "`Thread.currentThread().interrupt()`. Now the final check prints `true` - "
              "the request survives.",
              "        int n = sc.nextInt();\n"
              "        Thread.currentThread().interrupt();\n"
              "        System.out.println(Thread.currentThread().isInterrupted());\n"
              "        try {\n"
              "            Thread.sleep(50);\n"
              "            System.out.println(\"slept\");\n"
              "        } catch (InterruptedException e) {\n"
              "            System.out.println(\"interrupted\");\n"
              "            Thread.currentThread().interrupt();\n"
              "        }\n"
              "        System.out.println(Thread.currentThread().isInterrupted());\n"
              "        System.out.println(n);",
              [_n29p(n, _nl("true", "interrupted", "true", n)) for n in _NS29P],
              ["One extra line inside the catch is the whole difference.",
               "Re-interrupting sets the flag again, so callers further up can still "
               "see it.",
               "This is the standard thing to do when you cannot handle the "
               "interruption yourself.",
               "The alternative is to actually stop - return, or rethrow.",
               "What you must not do is swallow it silently."]),

        _p29s("j29-pd-static", "`Thread.interrupted()` reads and clears", "Hard",
              "`Thread.interrupted()` is static, reads the CURRENT thread's flag and "
              "clears it. Interrupt main, then call it twice: `true` then `false`. "
              "Finish by printing `n`.",
              "        int n = sc.nextInt();\n"
              "        Thread.currentThread().interrupt();\n"
              "        System.out.println(Thread.interrupted());\n"
              "        System.out.println(Thread.interrupted());\n"
              "        System.out.println(Thread.currentThread().isInterrupted());\n"
              "        System.out.println(n);",
              [_n29p(n, _nl("true", "false", "false", n)) for n in _NS29P],
              ["`Thread.interrupted()` is static and always concerns the current "
               "thread.",
               "It CLEARS the flag as it reads it, so a second call sees `false`.",
               "`isInterrupted()` is the instance method, and it does not clear.",
               "Two methods, one letter apart in meaning and completely different in "
               "effect - a favourite exam question.",
               "After the clearing call, the instance check agrees: `false`."]),

        _p29s("j29-pd-joinsequence", "Three joins, in order", "Hard",
              "Three workers, each sleeping a different amount and then writing its own "
              "slot. Start all three, then join them in index order and print each slot "
              "as its join returns - so the output order is fixed even though worker 0 "
              "sleeps longest.",
              "        int n = sc.nextInt();\n"
              "        int[] parts = new int[3];\n"
              "        Thread[] workers = new Thread[3];\n"
              "        for (int i = 0; i < 3; i++) {\n"
              "            final int idx = i;\n"
              "            workers[i] = new Thread(() -> {\n"
              "                try {\n"
              "                    Thread.sleep(30 - idx * 10);\n"
              "                } catch (InterruptedException e) {\n"
              "                    Thread.currentThread().interrupt();\n"
              "                }\n"
              "                parts[idx] = n + idx;\n"
              "            }, \"w\" + idx);\n"
              "            workers[i].start();\n"
              "        }\n"
              "        for (int i = 0; i < 3; i++) {\n"
              "            workers[i].join();\n"
              "            System.out.println(i + \" \" + parts[i]);\n"
              "        }",
              [_n29p(n, _nl(*[f"{i} {n + i}" for i in range(3)])) for n in _NS29P],
              ["Worker 0 sleeps 30ms, worker 2 sleeps 10ms - they FINISH in the "
               "opposite order to the joins.",
               "That does not matter: joining `workers[0]` first simply waits longer.",
               "Printing inside the join loop is safe because main is the only thing "
               "printing.",
               "The output is in index order regardless of completion order - which is "
               "the point.",
               "Had the workers printed for themselves, the order would have been the "
               "sleep order, and unpredictable in general."]),
    ])


# ===========================================================================
# Family E - pinning down the order
# ===========================================================================

_P29_E = _jfam(
    "p29-order", "Pinning down the order",
    "Turning work that could come out in any order into output that cannot.",
    """
Two started threads have **no** order between them. These variants drill the
three ways to get one back:

1. **join before you read** - the write and the read become ordered;
2. **a slot each, printed by main** - concurrent work, sequential output;
3. **start-join-start-join** - a strict sequence, no overlap at all.

And the daemon rule, which decides whether the JVM waits at all: it exits when
the last **user** thread ends, abandoning every daemon wherever it stands.
""",
    [
        _p29s("j29-pe-slots", "Squares, in index order", "Medium",
              "Read `n` values, square each on its own thread into its own slot, join "
              "them all, then print `index square` per line and the total.",
              "        int n = sc.nextInt();\n"
              "        int[] in = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            in[i] = sc.nextInt();\n"
              "        }\n"
              "        int[] parts = new int[n];\n"
              "        Thread[] workers = new Thread[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            final int idx = i;\n"
              "            workers[i] = new Thread(() -> parts[idx] = in[idx] * in[idx], \"w\" + idx);\n"
              "            workers[i].start();\n"
              "        }\n"
              "        for (Thread w : workers) {\n"
              "            w.join();\n"
              "        }\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            System.out.println(i + \" \" + parts[i]);\n"
              "            total += parts[i];\n"
              "        }\n"
              "        System.out.println(total);",
              [_acase(a, _nl(*([f"{i} {v * v}" for i, v in enumerate(a)]
                               + [sum(v * v for v in a)]))) for a in _AS29P],
              ["Start loop first, join loop second.",
               "`final int idx = i;` before the lambda.",
               "No worker prints; main walks the array afterwards.",
               "The total is computed on main, from slots that are all safely "
               "published.",
               "Run it a hundred times and the bytes are identical."]),

        _p29s("j29-pe-sequence", "A strict sequence", "Medium",
              "The same `n` values, but strictly one thread at a time: start, join, "
              "print, next. Print `w<i> <value>` for each, then the total.",
              "        int n = sc.nextInt();\n"
              "        int[] in = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            in[i] = sc.nextInt();\n"
              "        }\n"
              "        int[] parts = new int[n];\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            final int idx = i;\n"
              "            Thread t = new Thread(() -> parts[idx] = in[idx] + idx, \"w\" + idx);\n"
              "            t.start();\n"
              "            t.join();\n"
              "            System.out.println(\"w\" + idx + \" \" + parts[idx]);\n"
              "            total += parts[idx];\n"
              "        }\n"
              "        System.out.println(total);",
              [_acase(a, _nl(*([f"w{i} {v + i}" for i, v in enumerate(a)]
                               + [sum(v + i for i, v in enumerate(a))]))) for a in _AS29P],
              ["The join goes inside the loop, right after the start.",
               "That removes all the concurrency - deliberately.",
               "Only then is it safe to read `parts[idx]` inside the loop.",
               "Compare with the previous variant: same threads, joins in a different "
               "place, no parallelism left.",
               "Useful while debugging, and the right shape when each step needs the "
               "one before."]),

        _p29s("j29-pe-daemon", "Abandoned at exit", "Medium",
              "Start a daemon that sleeps for a minute before printing, then let main "
              "finish. The JVM exits without waiting, so only main's line appears.",
              "        int n = sc.nextInt();\n"
              "        Thread background = new Thread(() -> {\n"
              "            try {\n"
              "                Thread.sleep(60000);\n"
              "                System.out.println(\"background finished\");\n"
              "            } catch (InterruptedException e) {\n"
              "                System.out.println(\"background interrupted\");\n"
              "            }\n"
              "        }, \"background\");\n"
              "        background.setDaemon(true);\n"
              "        background.start();\n"
              "        System.out.println(\"main done \" + n);",
              [_n29p(n, "main done " + str(n)) for n in _NS29P],
              ["`setDaemon(true)` before `start()`, always.",
               "Main never joins it - that is the whole point.",
               "When main returns there is no user thread left, so the JVM exits.",
               "The daemon is killed where it stands: no exception, no `finally`, "
               "neither of its prints.",
               "So nothing that must complete may ever live on a daemon."]),

        _p29s("j29-pe-user", "…and waited for", "Medium",
              "The same worker WITHOUT `setDaemon`, sleeping briefly. Main prints and "
              "returns, but the JVM waits for the user thread, so the worker's line "
              "still appears - second.",
              "        int n = sc.nextInt();\n"
              "        Thread worker = new Thread(() -> {\n"
              "            try {\n"
              "                Thread.sleep(250);\n"
              "                System.out.println(\"worker finished\");\n"
              "            } catch (InterruptedException e) {\n"
              "                System.out.println(\"worker interrupted\");\n"
              "            }\n"
              "        }, \"worker\");\n"
              "        worker.start();\n"
              "        System.out.println(\"main done \" + n);",
              [_n29p(n, _nl("main done " + str(n), "worker finished")) for n in _NS29P],
              ["No `setDaemon` call at all, so it is an ordinary user thread.",
               "Main reaches its print immediately; the worker is still asleep.",
               "Main returning does not end the JVM while a user thread lives.",
               "The worker wakes, prints, and only then does the process exit.",
               "The sleep is what makes this particular order reliable - two unjoined "
               "threads with no sleep would have no order at all."]),

        _p29s("j29-pe-chunks", "Chunked, and deterministic", "Hard",
              "Read `n` values and a chunk count `k`. Sum chunk `i` - indices "
              "`[i*n/k, (i+1)*n/k)` - on thread `i`, join them all, then print "
              "`index sum` per chunk and the grand total.",
              "        int n = sc.nextInt();\n"
              "        int[] a = new int[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            a[i] = sc.nextInt();\n"
              "        }\n"
              "        int k = sc.nextInt();\n"
              "        int[] parts = new int[k];\n"
              "        Thread[] workers = new Thread[k];\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            final int from = idx * n / k;\n"
              "            final int to = (idx + 1) * n / k;\n"
              "            workers[i] = new Thread(() -> {\n"
              "                int sum = 0;\n"
              "                for (int j = from; j < to; j++) {\n"
              "                    sum += a[j];\n"
              "                }\n"
              "                parts[idx] = sum;\n"
              "            }, \"w\" + idx);\n"
              "            workers[i].start();\n"
              "        }\n"
              "        for (Thread w : workers) {\n"
              "            w.join();\n"
              "        }\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            System.out.println(i + \" \" + parts[i]);\n"
              "            total += parts[i];\n"
              "        }\n"
              "        System.out.println(total);",
              [_akcase(a, k, _nl(*([f"{i} {sum(a[i * len(a) // k:(i + 1) * len(a) // k])}"
                                    for i in range(k)]
                                   + [sum(a)])))
               for (a, k) in ((_AS29P[0], 3), (_AS29P[1], 1), (_AS29P[2], 2),
                              (_AS29P[3], 2), (_AS29P[4], 4))],
              ["Copy the bounds into `final` locals before the lambda captures them.",
               "`from = i*n/k` and `to = (i+1)*n/k` meet exactly, so nothing is missed "
               "or counted twice.",
               "Accumulate into a local and assign `parts[idx]` once.",
               "Start every worker before joining any of them.",
               "When `k` does not divide `n` the chunks are uneven, and the totals "
               "still add up to the sum of the whole array."]),
    ])


_PRACTICE[29] = [_P29_A, _P29_B, _P29_C, _P29_D, _P29_E]
