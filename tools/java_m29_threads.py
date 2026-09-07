# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 29 - Threads, and what they cost.  Opens Part 10.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# `Thread` and `Runnable` become legal here and nowhere earlier.
#
# DELIBERATELY NOT HERE: `synchronized`, `volatile`, the atomics and the locks
# are module 30; `ExecutorService`, `Callable` and `Future` are module 31. The
# scope linter enforces all of it. So this module never has two threads touching
# the same variable at the same time - every shared write in it is separated
# from every read by a `join()`, which is the one ordering guarantee available
# before module 30 teaches the rest.
#
# THE JUDGING PROBLEM, AND HOW THIS MODULE SOLVES IT
# --------------------------------------------------
# Every exercise in this course is graded by exact stdout comparison, and
# threads are the one topic where "run it again and get different output" is the
# whole point. Nothing here may be left to the scheduler. Three patterns keep
# every program in the module deterministic, and they are also lesson 29.5:
#
#   1. JOIN BEFORE YOU READ. A write in a thread and a read after `join()` on
#      that thread are ordered - `join` is the module's only happens-before.
#   2. ONE SLOT PER THREAD. Threads never share a counter; each writes
#      `result[i]` and main prints the array in index order after joining all.
#   3. START-JOIN-START-JOIN. Where the lesson is about ordering, threads are
#      run strictly one at a time, so interleaving cannot arise at all.
#
# Two threads printing at once appears in the PROSE of 29.5 - as the thing not
# to do - and never in a judged program.
#
# THREAD NAMES ARE ALWAYS EXPLICIT. `new Thread(r)` names itself `Thread-0`,
# `Thread-1`, ... from a JVM-wide counter that internal threads can also bump, so
# every thread in this module is constructed with `new Thread(r, "worker")` and
# the default names are described in prose only.
#
# BUGGY STARTERS ARE DETERMINISTICALLY BUGGY. `verify_java_course.py --starters`
# requires each "fix" starter to actually fail, so no starter here is merely
# *likely* to be wrong: `run()` instead of `start()` runs on the main thread and
# prints the wrong NAME every time, and a thread that is never started leaves
# its slot at 0 every time. Losing an update to a data race is module 30's
# subject, and even there it is drilled as a fill-in-the-blank rather than as a
# starter that has to fail on the scheduler's say-so.
# ---------------------------------------------------------------------------

_M29 = []

_IMPORTS29 = "import java.util.*;\n"

# main() declares the checked InterruptedException that `join` and `sleep` throw,
# rather than wrapping every call in a try/catch that would bury the point.
# `throws` has been legal since module 16.
_SIG29 = "    public static void main(String[] args) throws InterruptedException {"


def _j29s(body):
    """A Scanner-opening main that may join or sleep."""
    return _jcls(
        _SIG29 + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }",
        imports=_IMPORTS29,
    )


def _j29t(types, body):
    """Helper CLASSES above Main - a Runnable implementation or a Thread
    subclass - then a Scanner-opening main."""
    return _jp(
        _IMPORTS29 + "\n"
        + types.rstrip("\n") + "\n\n"
        + "public class Main {\n"
        + _SIG29 + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }\n}"
    )


# --- data ------------------------------------------------------------------

_N29 = (1, 5, 3, 7, 12)
_W29 = ("ada", "bo", "cy", "dee", "eli")
_A29 = ([3, 1, 2], [5], [4, 4, 4, 4], [10, -2, 7], [1, 2, 3, 4, 5, 6])


def _n29(n, out):
    """stdin = a single integer."""
    return _case(str(n), out)


def _w29(s, out):
    """stdin = a single word."""
    return _case(s, out)


def _tri(n):
    """1 + 2 + ... + n, the sum every worker in this module computes."""
    return n * (n + 1) // 2


# ===========================================================================
# 29.1 Processes, threads, and what they share
# ===========================================================================

_M29.append(_jlesson(
    "m29-what", "Processes, threads, and what they share",
    "A thread is a second place in the same program where execution is happening - "
    "sharing all the objects, sharing none of the local variables.",
    """
Every program you have written in this course so far ran on **one** thread. It
already had a name:

```java
System.out.println(Thread.currentThread().getName());   // main
```

The JVM created that thread, called `main` on it, and will exit when it returns.

**A process** is a running program with its own memory. Two processes cannot
see each other's objects at all; to talk they need a pipe, a socket or a file.
Starting one is expensive.

**A thread** is a second (or hundredth) line of execution *inside one process*.
Starting one is cheap, and - this is the entire subject of Part 10 - threads in a
process share memory.

Precisely what is shared and what is not:

| Each thread has its own | All threads share |
|---|---|
| call stack | the heap - every object, every array |
| local variables and parameters | `static` fields |
| program counter (where it is) | open files and sockets |

So two threads calling the same method each get their **own** copy of its local
variables, and there is no way for one to see the other's. But if both are
handed the same array, they are looking at the same memory - and that is both
why threads are useful and why the next module exists.

**Concurrency is not parallelism.** Concurrency is *structure*: several tasks in
flight at once, whether or not the machine can run them simultaneously. On a
single core the scheduler interleaves them. Parallelism is *execution*: two
things literally running at the same instant, which needs two cores. Java's
threads give you concurrency; the hardware decides how much of it is
parallelism.

**The cost.** A thread is cheap next to a process and expensive next to a method
call: each one reserves a stack (around half a megabyte of address space by
default), and every switch between them costs the scheduler something. A few
dozen threads is ordinary. A thread per request, at ten thousand requests, is
not - which is what module 31 is about.
""",
    warmup=[
        _jq("Two threads in the same process share…",
            ["the heap - every object and array, and all static fields",
             "nothing at all",
             "their local variables",
             "their call stacks"],
            0,
            "Objects live on the shared heap. Locals live on each thread's own stack."),
        _jq("What does each thread have entirely of its own?",
            ["Its call stack, and so its local variables",
             "Its own copy of every object",
             "Its own static fields",
             "Its own heap"],
            0,
            "One stack per thread; one heap for all of them."),
    ],
    exercises=[
        _je("j29-what-name", "The thread you were already on",
            "Every program in this course has been running on a thread called `main`. "
            "Print its name, then print twice the number read from stdin. Replace `____` "
            "with the line that prints the current thread's name.",
            _j29s("        int n = sc.nextInt();\n"
                  "        System.out.println(Thread.currentThread().getName());\n"
                  "        System.out.println(n * 2);"),
            "        System.out.println(Thread.currentThread().getName());",
            [_n29(n, _nl("main", n * 2)) for n in _N29],
            hints=["`Thread.currentThread()` is a static method returning the Thread you "
                   "are executing on.",
                   "`getName()` on that gives its name.",
                   "The JVM named this one `main` before it called your `main` method.",
                   "`System.out.println(Thread.currentThread().getName());`",
                   "There is nothing special about the name - you can `setName` it."],
            difficulty="Easy"),

        _jch("j29-what-shared", "The heap is shared", "Medium",
             "A thread and the code that started it share every object. Create a thread "
             "that writes `n * n` into `shared[0]`, start it, wait for it with `join()`, "
             "and print the slot. Replace `____` with the three lines that create, start "
             "and join the worker.",
             _j29s("        int n = sc.nextInt();\n"
                   "        int[] shared = new int[1];\n"
                   "        Thread worker = new Thread(() -> shared[0] = n * n, \"worker\");\n"
                   "        worker.start();\n"
                   "        worker.join();\n"
                   "        System.out.println(shared[0]);"),
             "        Thread worker = new Thread(() -> shared[0] = n * n, \"worker\");\n"
             "        worker.start();\n"
             "        worker.join();",
             [_n29(n, str(n * n)) for n in _N29],
             hints=["`Runnable` is a functional interface, so a lambda is a Runnable - "
                    "module 25's rule still applies.",
                    "`new Thread(runnable, name)` builds it; `start()` runs it on a new "
                    "thread.",
                    "The lambda captures `shared` and `n`, so both must be effectively "
                    "final - neither is ever reassigned here.",
                    "`worker.join()` blocks main until the worker has finished.",
                    "Without the `join`, reading `shared[0]` would be a race - the whole "
                    "reason the join is there."]),

        _jch("j29-what-stack", "Each thread has its own stack", "Medium",
             "One `Runnable`, run by two different threads, one after the other. Each "
             "thread gets its OWN copy of the Runnable's local variable, so both print "
             "the same total. Run them strictly one at a time - start, join, start, join - "
             "and print the input afterwards. Replace `____` with the Runnable and the "
             "four lines that run the two threads.",
             _j29s("        int n = sc.nextInt();\n"
                   "        Runnable job = () -> {\n"
                   "            int local = 0;\n"
                   "            for (int i = 1; i <= 3; i++) local += i;\n"
                   "            System.out.println(Thread.currentThread().getName() + \" \" + local);\n"
                   "        };\n"
                   "        Thread a = new Thread(job, \"a\");\n"
                   "        Thread b = new Thread(job, \"b\");\n"
                   "        a.start();\n"
                   "        a.join();\n"
                   "        b.start();\n"
                   "        b.join();\n"
                   "        System.out.println(n);"),
             "        Runnable job = () -> {\n"
             "            int local = 0;\n"
             "            for (int i = 1; i <= 3; i++) local += i;\n"
             "            System.out.println(Thread.currentThread().getName() + \" \" + local);\n"
             "        };\n"
             "        Thread a = new Thread(job, \"a\");\n"
             "        Thread b = new Thread(job, \"b\");\n"
             "        a.start();\n"
             "        a.join();\n"
             "        b.start();\n"
             "        b.join();",
             [_n29(n, _nl("a 6", "b 6", n)) for n in _N29],
             hints=["`local` is declared inside the Runnable, so it lives on whichever "
                    "thread is running it - two threads, two copies.",
                    "One Runnable object can be handed to any number of Threads.",
                    "Name the threads explicitly: `new Thread(job, \"a\")`.",
                    "Start, join, start, join - so `a` has finished before `b` begins and "
                    "the output order is fixed.",
                    "If you started both before joining either, the two lines could come "
                    "out in either order - which is exactly what the judge cannot allow."]),

        _jfix("j29-what-unstarted", "The thread that never ran",
              "This builds a Thread and then calls no method on it at all, so the "
              "Runnable never executes and the slot keeps its default `0`. Start the "
              "thread and wait for it.",
              _j29s("        int n = sc.nextInt();\n"
                    "        int[] shared = new int[1];\n"
                    "        Thread worker = new Thread(() -> shared[0] = n * n, \"worker\");\n"
                    "        System.out.println(shared[0]);"),
              _j29s("        int n = sc.nextInt();\n"
                    "        int[] shared = new int[1];\n"
                    "        Thread worker = new Thread(() -> shared[0] = n * n, \"worker\");\n"
                    "        worker.start();\n"
                    "        worker.join();\n"
                    "        System.out.println(shared[0]);"),
              [_n29(n, str(n * n)) for n in _N29],
              hints=["Constructing a `Thread` runs nothing - it only records what to run.",
                     "A thread in that condition is in the NEW state; lesson 3 names all "
                     "six.",
                     "`start()` asks the JVM for a new thread and calls `run()` on it.",
                     "You also need `join()`, or main might print before the worker has "
                     "written.",
                     "This is the quietest bug in the module: no error, no exception, just "
                     "a zero."],
              difficulty="Easy"),
    ],
    quiz=[
        _jq("Two threads call the same method. Their local variables are…",
            ["separate - one copy per thread, on that thread's own stack",
             "shared, like fields",
             "shared only if the method is static",
             "copied back and forth"],
            0,
            "Locals live on the stack, and each thread has its own stack."),
        _jq("Concurrency and parallelism differ in that…",
            ["concurrency is about structure - tasks in flight; parallelism is about "
             "literally executing at once",
             "they are the same thing",
             "concurrency needs several cores",
             "parallelism needs only one core"],
            0,
            "Concurrent code on one core interleaves; it is still concurrent."),
    ],
))


# ===========================================================================
# 29.2 Making one: Thread, Runnable, and start() vs run()
# ===========================================================================

_M29.append(_jlesson(
    "m29-create", "Making one - and `start()` vs `run()`",
    "Three ways to say what a thread should do, and the single method call that "
    "decides whether it is a thread at all.",
    """
There are three ways to give a thread its work, and they are the same three
ideas Part 4 and Part 8 already taught.

**1. Implement `Runnable` with a named class** - the module 14 way.

```java
class Greeter implements Runnable {
    private final String who;

    Greeter(String who) { this.who = who; }

    @Override
    public void run() {
        System.out.println("hello " + who);
    }
}

Thread t = new Thread(new Greeter("ada"), "worker");
```

**2. Extend `Thread`** and override `run()`.

```java
class Counter extends Thread {
    @Override
    public void run() { System.out.println("counting"); }
}
```

**3. A lambda**, because `Runnable` is a functional interface - one abstract
method, `void run()`, taking nothing. Module 25's rule applies unchanged.

```java
Thread t = new Thread(() -> System.out.println("hello"), "worker");
```

**Prefer `Runnable`.** Extending `Thread` spends your one inheritance slot on a
detail of *how* the work is scheduled, and it welds the task to the thread. A
`Runnable` is just a task: you can hand it to a Thread, run it inline, or - from
module 31 - give it to a pool. This is module 14's composition-over-inheritance
argument, in the standard library.

## `start()` versus `run()`

This is the most-asked question in the whole of Part 10, and it has a one-line
answer.

```java
t.start();   // asks the JVM for a NEW thread, which then calls run()
t.run();     // an ordinary method call, on the thread you are already on
```

`run()` compiles, runs, and does exactly what its body says - on the *calling*
thread. No thread is created. Nothing is concurrent. The tell is the name:

```java
Thread t = new Thread(
    () -> System.out.println(Thread.currentThread().getName()), "worker");

t.start();   // prints "worker"
t.run();     // prints "main"
```

`start()` may be called **once**. A second call throws
`IllegalThreadStateException`, which lesson 3 makes concrete.

**Naming.** `new Thread(r)` gives itself `Thread-0`, `Thread-1`, and so on from a
counter shared with the whole JVM. Every thread in this module is named
explicitly - `new Thread(r, "worker")`, or `setName` before `start` - because a
name you chose is one you can assert on.
""",
    warmup=[
        _jq("`t.run()` instead of `t.start()`…",
            ["runs the body on the current thread - no new thread exists",
             "does nothing", "throws IllegalThreadStateException",
             "starts the thread and waits for it"],
            0,
            "It is an ordinary method call. The tell is which name it prints."),
        _jq("`Runnable` is preferred to extending `Thread` mainly because…",
            ["it leaves your one inheritance slot free and separates the task from how it runs",
             "it is faster", "`Thread` is deprecated",
             "`Runnable` can return a value"],
            0,
            "Composition over inheritance - and a Runnable can go to a pool later."),
    ],
    exercises=[
        _je("j29-create-runnable", "A named Runnable",
            "`Greeter` implements `Runnable`. Build a Thread named `worker` that runs a "
            "`Greeter` for the word read from stdin, start it and join it. Replace `____` "
            "with the Thread construction.",
            _j29t("class Greeter implements Runnable {\n"
                  "    private final String who;\n\n"
                  "    Greeter(String who) {\n"
                  "        this.who = who;\n"
                  "    }\n\n"
                  "    @Override\n"
                  "    public void run() {\n"
                  "        System.out.println(\"hello \" + who + \" from \"\n"
                  "                + Thread.currentThread().getName());\n"
                  "    }\n"
                  "}",
                  "        String who = sc.next();\n"
                  "        Thread t = new Thread(new Greeter(who), \"worker\");\n"
                  "        t.start();\n"
                  "        t.join();\n"
                  "        System.out.println(\"done\");"),
            "        Thread t = new Thread(new Greeter(who), \"worker\");",
            [_w29(w, _nl("hello " + w + " from worker", "done")) for w in _W29],
            hints=["A `Runnable` is not a thread - it is the work. Something has to run it.",
                   "`new Thread(runnable, name)` is the two-argument constructor.",
                   "The name matters here: the Runnable prints whichever thread is "
                   "executing it.",
                   "`new Thread(new Greeter(who), \"worker\")`",
                   "`done` prints after the join, so the order is fixed."],
            difficulty="Easy"),

        _je("j29-create-extends", "Extending Thread",
            "`Adder` extends `Thread` and sums 1..limit inside `run()`. A Thread subclass "
            "can call `getName()` on itself directly. Set the thread's name to `adder`, "
            "start it and join it. Replace `____` with the line that names it.",
            _j29t("class Adder extends Thread {\n"
                  "    private final int limit;\n\n"
                  "    Adder(int limit) {\n"
                  "        this.limit = limit;\n"
                  "    }\n\n"
                  "    @Override\n"
                  "    public void run() {\n"
                  "        int sum = 0;\n"
                  "        for (int i = 1; i <= limit; i++) {\n"
                  "            sum += i;\n"
                  "        }\n"
                  "        System.out.println(getName() + \" \" + sum);\n"
                  "    }\n"
                  "}",
                  "        int n = sc.nextInt();\n"
                  "        Adder adder = new Adder(n);\n"
                  "        adder.setName(\"adder\");\n"
                  "        adder.start();\n"
                  "        adder.join();\n"
                  "        System.out.println(\"done\");"),
            "        adder.setName(\"adder\");",
            [_n29(n, _nl("adder " + str(_tri(n)), "done")) for n in _N29],
            hints=["`Adder` IS-A Thread here, so it inherits `setName`, `start` and "
                   "`getName`.",
                   "`setName` has to happen before the output is produced.",
                   "`adder.setName(\"adder\");`",
                   "Because it extends Thread, `run()` can call `getName()` with no "
                   "receiver.",
                   "That inheritance is exactly what the Runnable version avoids paying "
                   "for."],
            difficulty="Easy"),

        _jch("j29-create-lambda", "The same thing, as a lambda", "Easy",
             "`Runnable` has one abstract method taking nothing and returning nothing, so "
             "a lambda is one. Build and run a thread named `worker` that prints its own "
             "name and the sum 1..n. Replace `____` with the whole construction, start "
             "and join.",
             _j29s("        int n = sc.nextInt();\n"
                   "        Thread t = new Thread(() -> {\n"
                   "            int sum = 0;\n"
                   "            for (int i = 1; i <= n; i++) {\n"
                   "                sum += i;\n"
                   "            }\n"
                   "            System.out.println(Thread.currentThread().getName() + \" \" + sum);\n"
                   "        }, \"worker\");\n"
                   "        t.start();\n"
                   "        t.join();"),
             "        Thread t = new Thread(() -> {\n"
             "            int sum = 0;\n"
             "            for (int i = 1; i <= n; i++) {\n"
             "                sum += i;\n"
             "            }\n"
             "            System.out.println(Thread.currentThread().getName() + \" \" + sum);\n"
             "        }, \"worker\");\n"
             "        t.start();\n"
             "        t.join();",
             [_n29(n, "worker " + str(_tri(n))) for n in _N29],
             hints=["The lambda needs a braced body because it is several statements.",
                    "It returns nothing, which is what `void run()` wants.",
                    "`n` is captured, so it must be effectively final - read it once and "
                    "never reassign it.",
                    "The name goes in the Thread constructor's second argument, not in the "
                    "lambda.",
                    "Inside the lambda, `Thread.currentThread()` is the WORKER, not main."]),

        _jfix("j29-create-startrun", "`run()` is not `start()`",
              "This calls `run()` on the Thread, so the body executes on the main thread "
              "and prints `main` where the test expects `worker`. No second thread is ever "
              "created. Start it properly and wait for it.",
              _j29s("        String who = sc.next();\n"
                    "        Thread t = new Thread(\n"
                    "                () -> System.out.println(who + \" on \"\n"
                    "                        + Thread.currentThread().getName()), \"worker\");\n"
                    "        t.run();\n"
                    "        System.out.println(\"done\");"),
              _j29s("        String who = sc.next();\n"
                    "        Thread t = new Thread(\n"
                    "                () -> System.out.println(who + \" on \"\n"
                    "                        + Thread.currentThread().getName()), \"worker\");\n"
                    "        t.start();\n"
                    "        t.join();\n"
                    "        System.out.println(\"done\");"),
              [_w29(w, _nl(w + " on worker", "done")) for w in _W29],
              hints=["`run()` is just a method. Calling it does not ask the JVM for "
                     "anything.",
                     "The proof is in the output: it prints the name of whichever thread "
                     "executed the body.",
                     "`start()` is the method that creates a thread and has IT call "
                     "`run()`.",
                     "Add a `join()` too, so `done` cannot overtake the worker's line.",
                     "This is the single most common Part 10 interview question."],
              difficulty="Medium"),
    ],
    quiz=[
        _jq("How many times may `start()` be called on one Thread object?",
            ["Once - a second call throws IllegalThreadStateException",
             "As many as you like", "Twice", "Once per Runnable"],
            0,
            "A terminated thread cannot be restarted; make a new one."),
        _jq("`new Thread(r)` with no name gives the thread…",
            ["a generated name like `Thread-0`, from a JVM-wide counter",
             "the name of the Runnable's class", "no name at all", "the name `main`"],
            0,
            "Which is why this module always passes a name explicitly."),
    ],
))


# ===========================================================================
# 29.3 The lifecycle
# ===========================================================================

_M29.append(_jlesson(
    "m29-lifecycle", "The six states",
    "NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED - and the two of them "
    "you can observe with certainty.",
    """
`Thread.getState()` returns one of exactly six values, and naming them is a
standard interview question.

| State | What it means |
|---|---|
| `NEW` | constructed, `start()` not yet called |
| `RUNNABLE` | running, or ready to run and waiting for a core |
| `BLOCKED` | waiting to acquire a lock (module 30) |
| `WAITING` | waiting indefinitely - `join()`, `wait()` |
| `TIMED_WAITING` | waiting with a deadline - `sleep(ms)`, `join(ms)` |
| `TERMINATED` | `run()` has returned, or thrown |

Two things worth noticing.

**`RUNNABLE` does not mean "running".** Java does not distinguish "on a core
right now" from "ready and queued". Both are RUNNABLE, because which one it is
can change between you asking and you reading the answer.

**Only two states are worth asserting on.** Before `start()`, a thread is
reliably `NEW`. After `join()` returns, it is reliably `TERMINATED`. Everything
in between is a snapshot of something that has probably already changed - which
is why every judged program in this module only ever checks those two.

```java
Thread t = new Thread(job, "worker");
System.out.println(t.getState());    // NEW
t.start();
t.join();
System.out.println(t.getState());    // TERMINATED
System.out.println(t.isAlive());     // false
```

**The arrows only go one way at the ends.** NEW is reachable only at
construction and TERMINATED only once, so a thread cannot go back:

```java
t.start();
t.join();
t.start();     // IllegalThreadStateException
```

A `Thread` object is single-use, exactly like a stream in module 26. If you want
to do the work again, construct another one - or, from module 31, stop managing
threads by hand and hand tasks to a pool that keeps its own.

**`isAlive()`** is the coarse version: `true` between a successful `start()` and
the end of `run()`, `false` on either side.
""",
    warmup=[
        _jq("A thread that has been constructed but not started is in state…",
            ["NEW", "RUNNABLE", "WAITING", "TERMINATED"],
            0,
            "`start()` is what moves it out of NEW."),
        _jq("`RUNNABLE` means…",
            ["running OR ready to run - Java does not separate the two",
             "definitely executing on a core right now",
             "waiting for a lock", "sleeping"],
            0,
            "Which is why you cannot usefully assert on it."),
    ],
    exercises=[
        _je("j29-life-states", "NEW, then TERMINATED",
            "The only two states you can assert on. Print the worker's state before "
            "starting it, then - after joining - its state and whether it is alive. "
            "Replace `____` with the line that prints the state before the start.",
            _j29s("        int n = sc.nextInt();\n"
                  "        int[] out = new int[1];\n"
                  "        Thread t = new Thread(() -> out[0] = n + 1, \"worker\");\n"
                  "        System.out.println(t.getState());\n"
                  "        t.start();\n"
                  "        t.join();\n"
                  "        System.out.println(t.getState());\n"
                  "        System.out.println(t.isAlive());\n"
                  "        System.out.println(out[0]);"),
            "        System.out.println(t.getState());\n"
            "        t.start();",
            [_n29(n, _nl("NEW", "TERMINATED", "false", n + 1)) for n in _N29],
            hints=["`getState()` returns a `Thread.State`, an enum - printing it gives its "
                   "name in capitals.",
                   "Before `start()` the answer is fixed, and it is not RUNNABLE.",
                   "The blank covers the state print AND the `start()` that follows it.",
                   "After `join()` returns, `run()` has definitely finished.",
                   "`isAlive()` is `false` on both sides of the thread's life."],
            difficulty="Easy"),

        _jch("j29-life-restart", "A thread is single-use", "Medium",
             "Run the worker, join it, then try to `start()` it a second time and catch "
             "the `IllegalThreadStateException` that follows. Print `cannot restart` in "
             "the catch. Replace `____` with the second start and its try/catch.",
             _j29s("        int n = sc.nextInt();\n"
                   "        int[] out = new int[1];\n"
                   "        Thread t = new Thread(() -> out[0] = n * 3, \"worker\");\n"
                   "        t.start();\n"
                   "        t.join();\n"
                   "        System.out.println(out[0]);\n"
                   "        try {\n"
                   "            t.start();\n"
                   "            System.out.println(\"started again\");\n"
                   "        } catch (IllegalThreadStateException e) {\n"
                   "            System.out.println(\"cannot restart\");\n"
                   "        }\n"
                   "        System.out.println(t.getState());"),
             "        try {\n"
             "            t.start();\n"
             "            System.out.println(\"started again\");\n"
             "        } catch (IllegalThreadStateException e) {\n"
             "            System.out.println(\"cannot restart\");\n"
             "        }",
             [_n29(n, _nl(n * 3, "cannot restart", "TERMINATED")) for n in _N29],
             hints=["`IllegalThreadStateException` is unchecked, so catching it is a "
                    "choice, not a requirement.",
                    "`started again` must be INSIDE the try, after the `start()` - it "
                    "never runs.",
                    "The thread stays TERMINATED; the failed start changes nothing.",
                    "To run the work twice you need a second `Thread` object.",
                    "Module 26 made the same point about streams: some objects are "
                    "single-use by design."]),

        _jch("j29-life-alive", "Alive, in between", "Medium",
             "`isAlive()` before the start, and again after the join, with the worker's "
             "answer in between. Print `false`, the computed value, then `false`. Replace "
             "`____` with the whole sequence.",
             _j29s("        int n = sc.nextInt();\n"
                   "        int[] out = new int[1];\n"
                   "        Thread t = new Thread(() -> out[0] = n * n + 1, \"worker\");\n"
                   "        System.out.println(t.isAlive());\n"
                   "        t.start();\n"
                   "        t.join();\n"
                   "        System.out.println(out[0]);\n"
                   "        System.out.println(t.isAlive());"),
             "        System.out.println(t.isAlive());\n"
             "        t.start();\n"
             "        t.join();\n"
             "        System.out.println(out[0]);\n"
             "        System.out.println(t.isAlive());",
             [_n29(n, _nl("false", n * n + 1, "false")) for n in _N29],
             hints=["`isAlive()` is `false` in the NEW state - it has not started yet.",
                    "`join()` returns only once the worker has terminated.",
                    "So the second `isAlive()` is `false` too, for the opposite reason.",
                    "Checking `isAlive()` in a loop instead of joining is a busy-wait - "
                    "correct but wasteful.",
                    "The worker's result is safe to read only because the join is between "
                    "the write and the read."]),

        _jfix("j29-life-reuse", "Reuse the object, or build a new one?",
              "This tries to run the same `Thread` object twice and dies with "
              "`IllegalThreadStateException` on the second `start()`. Build a second "
              "Thread for the second run instead - the Runnable can be shared, the Thread "
              "cannot.",
              _j29s("        int n = sc.nextInt();\n"
                    "        int[] out = new int[2];\n"
                    "        Runnable job = () -> out[0] = out[0] + n;\n"
                    "        Thread t = new Thread(job, \"worker\");\n"
                    "        t.start();\n"
                    "        t.join();\n"
                    "        t.start();\n"
                    "        t.join();\n"
                    "        System.out.println(out[0]);"),
              _j29s("        int n = sc.nextInt();\n"
                    "        int[] out = new int[2];\n"
                    "        Runnable job = () -> out[0] = out[0] + n;\n"
                    "        Thread first = new Thread(job, \"worker-1\");\n"
                    "        first.start();\n"
                    "        first.join();\n"
                    "        Thread second = new Thread(job, \"worker-2\");\n"
                    "        second.start();\n"
                    "        second.join();\n"
                    "        System.out.println(out[0]);"),
              [_n29(n, str(n * 2)) for n in _N29],
              hints=["The Runnable is reusable; the Thread is not.",
                     "Construct a second `Thread` around the SAME `job`.",
                     "Join the first before starting the second, so the two `+ n` writes "
                     "cannot overlap.",
                     "That join is what makes `out[0] = out[0] + n` safe here - without it "
                     "this would be module 30's data race.",
                     "The answer is `n + n`."],
              difficulty="Medium"),
    ],
    quiz=[
        _jq("After `t.join()` returns, `t.getState()` is…",
            ["TERMINATED", "RUNNABLE", "WAITING", "NEW"],
            0,
            "join returns precisely because run() finished."),
        _jq("Calling `start()` on a TERMINATED thread…",
            ["throws IllegalThreadStateException", "runs it again",
             "returns false", "blocks forever"],
            0,
            "Thread objects are single-use. Build another."),
    ],
))


# ===========================================================================
# 29.4 sleep, join, interrupt
# ===========================================================================

_M29.append(_jlesson(
    "m29-sleepjoin", "`sleep`, `join`, and interruption",
    "The three methods that make one thread wait - and the flag that asks it to stop.",
    """
## `sleep`

```java
Thread.sleep(50);     // this thread pauses for at least 50 milliseconds
```

Three things about it, all of which get asked:

* It is **static**, and it always sleeps the **current** thread. `t.sleep(50)`
  compiles and does not sleep `t` - it sleeps whoever called it. Never write it.
* It is `TIMED_WAITING`, and the duration is a *minimum*. The scheduler owes you
  nothing beyond "not before".
* It throws `InterruptedException`, which is **checked** - so every call is
  inside a `try` or inside a method that declares `throws`.

## `join`

```java
worker.join();        // block until worker terminates
worker.join(100);     // ...or until 100ms pass, whichever comes first
```

`join()` is the ordering tool of this module. It does two jobs at once:

1. it waits, so the work is finished; and
2. it **publishes** - everything the worker wrote before it ended is guaranteed
   visible to you after the join returns.

That second job is the one people forget, and it is why every exercise here can
read a worker's result at all. Without a join, "the worker already wrote it" is
not a fact you are entitled to, no matter how long you wait. Module 30 is the
general version of this guarantee.

Note that `join(100)` gives you neither guarantee if it times out - check
`isAlive()` afterwards to find out which happened.

## Interruption

There is no `Thread.stop()`. Killing a thread from outside would leave whatever
it was halfway through in an unknown state, so the method exists, is deprecated,
and in modern Java throws. What you have instead is a **request**:

```java
t.interrupt();               // set t's interrupt flag
t.isInterrupted();           // read it
Thread.interrupted();        // read it AND clear it (static, current thread)
```

The flag does nothing by itself. It matters in two places:

* A thread **blocked** in `sleep`, `join` or `wait` throws
  `InterruptedException` immediately, **and clears the flag on its way out.**
* A thread that is merely computing sees nothing unless it checks
  `isInterrupted()` itself.

That clearing is the subtle bit, and lesson exercise four pins it down: after
you catch `InterruptedException`, the flag is `false` again. Swallowing that
exception with an empty `catch` therefore destroys the only evidence that anyone
asked you to stop - so either act on it, or restore the flag with
`Thread.currentThread().interrupt()`.
""",
    warmup=[
        _jq("`Thread.sleep(100)` sleeps…",
            ["the thread that called it - it is static and always affects the current thread",
             "the thread you call it on", "every thread", "the main thread"],
            0,
            "`t.sleep(100)` is a trap: it sleeps the caller, not `t`."),
        _jq("Catching `InterruptedException` from `sleep` leaves the interrupt flag…",
            ["cleared - throwing it resets the flag",
             "set", "unchanged", "set on the main thread"],
            0,
            "Which is why an empty catch block loses the request entirely."),
    ],
    exercises=[
        _jch("j29-sj-join", "One slot each", "Medium",
             "Three workers, three answers, and no shared counter: worker `i` writes "
             "`base + i` into `parts[i]`. Start all three, join all three, then print the "
             "slots in index order and their total. Replace `____` with the loop that "
             "creates and starts the threads, and the loop that joins them.",
             _j29s("        int base = sc.nextInt();\n"
                   "        int[] parts = new int[3];\n"
                   "        Thread[] workers = new Thread[3];\n"
                   "        for (int i = 0; i < 3; i++) {\n"
                   "            final int idx = i;\n"
                   "            workers[i] = new Thread(() -> parts[idx] = base + idx, \"w\" + idx);\n"
                   "            workers[i].start();\n"
                   "        }\n"
                   "        for (int i = 0; i < 3; i++) {\n"
                   "            workers[i].join();\n"
                   "        }\n"
                   "        int total = 0;\n"
                   "        for (int i = 0; i < 3; i++) {\n"
                   "            System.out.println(i + \" \" + parts[i]);\n"
                   "            total += parts[i];\n"
                   "        }\n"
                   "        System.out.println(total);"),
             "        for (int i = 0; i < 3; i++) {\n"
             "            final int idx = i;\n"
             "            workers[i] = new Thread(() -> parts[idx] = base + idx, \"w\" + idx);\n"
             "            workers[i].start();\n"
             "        }\n"
             "        for (int i = 0; i < 3; i++) {\n"
             "            workers[i].join();\n"
             "        }",
             [_n29(b, _nl(*([f"{i} {b + i}" for i in range(3)]
                            + [sum(b + i for i in range(3))]))) for b in _N29],
             hints=["`i` in a `for` loop is reassigned every pass, so it is NOT effectively "
                    "final and a lambda cannot capture it.",
                    "Copy it first: `final int idx = i;` inside the loop body.",
                    "Each thread writes a DIFFERENT slot, so there is no shared write at "
                    "all - nothing to synchronise.",
                    "Start them all in the first loop, then join them all in the second: "
                    "that is what makes it concurrent rather than sequential.",
                    "Main prints the slots itself, in index order - so the output is fixed "
                    "however the threads were scheduled."]),

        _je("j29-sj-sleep", "Sleeping is not finishing",
            "The worker sleeps briefly and only then writes its answer, so reading the "
            "slot without joining would find a zero. `join()` waits for the whole of "
            "`run()`, sleep included. Replace `____` with the join.",
            _j29s("        int n = sc.nextInt();\n"
                  "        int[] out = new int[1];\n"
                  "        Thread t = new Thread(() -> {\n"
                  "            try {\n"
                  "                Thread.sleep(30);\n"
                  "            } catch (InterruptedException e) {\n"
                  "                Thread.currentThread().interrupt();\n"
                  "            }\n"
                  "            out[0] = n * 10;\n"
                  "        }, \"sleeper\");\n"
                  "        t.start();\n"
                  "        t.join();\n"
                  "        System.out.println(out[0]);"),
            "        t.join();",
            [_n29(n, str(n * 10)) for n in _N29],
            hints=["`run()` cannot declare `throws`, so the sleep must be caught inside "
                   "the lambda.",
                   "Restoring the flag in the catch is the polite thing to do - the empty "
                   "catch is the bug.",
                   "`join()` returns only when `run()` has returned, sleep and all.",
                   "`t.join();`",
                   "Without it, main would very probably print `0` - and 'very probably' "
                   "is not something a test can rely on either way."],
            difficulty="Easy"),

        _jch("j29-sj-sequence", "Strict order, on purpose", "Medium",
             "Sometimes you want threads and NOT concurrency - a strict sequence. Run "
             "three workers start-join-start-join-start-join so each finishes before the "
             "next begins, each appending its index to the shared list of parts. Replace "
             "`____` with the loop.",
             _j29s("        int base = sc.nextInt();\n"
                   "        int[] parts = new int[3];\n"
                   "        for (int i = 0; i < 3; i++) {\n"
                   "            final int idx = i;\n"
                   "            Thread t = new Thread(() -> parts[idx] = base * (idx + 1), \"w\" + idx);\n"
                   "            t.start();\n"
                   "            t.join();\n"
                   "            System.out.println(\"w\" + idx + \" done \" + parts[idx]);\n"
                   "        }\n"
                   "        System.out.println(parts[0] + parts[1] + parts[2]);"),
             "        for (int i = 0; i < 3; i++) {\n"
             "            final int idx = i;\n"
             "            Thread t = new Thread(() -> parts[idx] = base * (idx + 1), \"w\" + idx);\n"
             "            t.start();\n"
             "            t.join();\n"
             "            System.out.println(\"w\" + idx + \" done \" + parts[idx]);\n"
             "        }",
             [_n29(b, _nl(*([f"w{i} done {b * (i + 1)}" for i in range(3)]
                            + [sum(b * (i + 1) for i in range(3))]))) for b in _N29],
             hints=["The join goes INSIDE the loop, immediately after the start.",
                    "That makes the program sequential - it is threads with all the "
                    "concurrency taken back out.",
                    "It is also the only arrangement where main can safely print "
                    "`parts[idx]` inside the loop.",
                    "Compare with the previous exercise: same three workers, two starts "
                    "and joins in different places, completely different amount of "
                    "parallelism.",
                    "The last line is the sum of `base * 1`, `base * 2` and `base * 3`."]),

        _jch("j29-sj-interrupt", "The flag that clears itself", "Hard",
             "Interrupt the MAIN thread, read the flag, then sleep - the sleep throws "
             "immediately AND clears the flag on the way out. Print the flag, `interrupted`, "
             "then the flag again. Replace `____` with the whole sequence.",
             _j29s("        int n = sc.nextInt();\n"
                   "        Thread.currentThread().interrupt();\n"
                   "        System.out.println(Thread.currentThread().isInterrupted());\n"
                   "        try {\n"
                   "            Thread.sleep(50);\n"
                   "            System.out.println(\"slept\");\n"
                   "        } catch (InterruptedException e) {\n"
                   "            System.out.println(\"interrupted\");\n"
                   "        }\n"
                   "        System.out.println(Thread.currentThread().isInterrupted());\n"
                   "        System.out.println(n);"),
             "        Thread.currentThread().interrupt();\n"
             "        System.out.println(Thread.currentThread().isInterrupted());\n"
             "        try {\n"
             "            Thread.sleep(50);\n"
             "            System.out.println(\"slept\");\n"
             "        } catch (InterruptedException e) {\n"
             "            System.out.println(\"interrupted\");\n"
             "        }\n"
             "        System.out.println(Thread.currentThread().isInterrupted());",
             [_n29(n, _nl("true", "interrupted", "false", n)) for n in _N29],
             hints=["A thread may interrupt itself - `Thread.currentThread().interrupt()`.",
                    "Setting the flag does nothing on its own, so the first print is "
                    "`true` and nothing else happens.",
                    "`sleep` on an already-interrupted thread throws IMMEDIATELY - it does "
                    "not sleep for 50ms first.",
                    "So `slept` never prints.",
                    "Throwing `InterruptedException` CLEARS the flag, which is why the "
                    "last print is `false` - the evidence is gone unless you restore it."]),
    ],
    quiz=[
        _jq("`worker.join()` guarantees…",
            ["the worker has finished, and everything it wrote is visible to you",
             "only that the worker has finished",
             "only that the worker has started",
             "that the worker ran on another core"],
            0,
            "The visibility half is what makes reading its result legal."),
        _jq("There is no working `Thread.stop()` because…",
            ["killing a thread mid-operation would leave shared state half-updated",
             "it was too slow", "it was replaced by `sleep`",
             "threads cannot be stopped at all"],
            0,
            "Interruption is a cooperative request instead."),
    ],
))


# ===========================================================================
# 29.5 Why the output moved
# ===========================================================================

_M29.append(_jlesson(
    "m29-order", "Why the output moved - and how to pin it down",
    "Unordered by default, ordered on purpose: the three patterns that make threaded "
    "output something you can actually assert on.",
    """
Here is a program with no bug in it that prints two different things on two
different runs:

```java
new Thread(() -> System.out.println("a"), "a").start();
new Thread(() -> System.out.println("b"), "b").start();
```

`ab` or `ba`. Both are correct. **There is no ordering between two threads
unless you create one**, and nothing in that code creates one. Add a `sleep` and
you have not fixed it - you have made one order *likely*, which is worse,
because it now fails once a month on a loaded machine instead of immediately on
your own.

This is why every judged program in this module is built from one of three
patterns.

**1. Join before you read.** A write inside `run()` and a read after `join()`
are ordered. This is the whole reason the exercises can print a worker's answer.

```java
worker.start();
worker.join();
System.out.println(result[0]);     // ordered, and visible
```

**2. One slot per thread, printed by main.** Threads never share a destination
and never print. Main joins them all, then walks the array in index order. The
*work* is concurrent; the *output* is sequential and fixed.

```java
for (int i = 0; i < k; i++) {
    final int idx = i;
    t[i] = new Thread(() -> parts[idx] = compute(idx), "w" + idx);
    t[i].start();
}
for (Thread t1 : t) t1.join();
for (int p : parts) System.out.println(p);
```

**3. Start-join-start-join**, when you want a strict sequence. The threads no
longer overlap at all, which is sometimes exactly what you want and always what
you want while debugging.

## Daemon threads

A thread is either a **user** thread or a **daemon** thread, and the JVM's exit
rule is one sentence: **it exits when the last user thread finishes**, without
waiting for any daemon.

```java
Thread t = new Thread(job, "background");
t.setDaemon(true);      // MUST be before start()
t.start();
```

Daemons are for genuinely disposable background work - a cache cleaner, a
metrics flusher. They are killed wherever they happen to be, with no unwinding
and no `finally`, so never put anything that must complete on one.

`setDaemon` throws `IllegalThreadStateException` if the thread **is alive** -
that is the javadoc's exact condition, and it is narrower than "has been
started". Setting the flag on a thread that has already terminated quietly
succeeds and means nothing. So the rule to actually follow is the positional
one: write `setDaemon(true)` on the line directly above `start()`, which is the
one moment it is both legal and useful.

## Priorities

`t.setPriority(Thread.MAX_PRIORITY)` is a **hint** to the OS scheduler, which is
free to ignore it, and does, differently on every platform. If your program's
correctness depends on a priority, your program is broken. Order comes from
`join`, from the locks in module 30, or from handing the problem to module 31 -
never from priorities.
""",
    warmup=[
        _jq("Two started, unjoined threads each printing one line produce…",
            ["either order - there is no ordering unless you create one",
             "always the start order", "always alphabetical order",
             "a compile error"],
            0,
            "And a `sleep` makes one order likely, not certain."),
        _jq("The JVM exits when…",
            ["the last USER thread finishes - daemon threads are not waited for",
             "the last thread of any kind finishes",
             "main returns, always",
             "every daemon thread finishes"],
            0,
            "Which is why a daemon must never hold work that has to complete."),
    ],
    exercises=[
        _jch("j29-order-slots", "Concurrent work, ordered output", "Hard",
             "Read `k` then `k` numbers, and square each one on its own thread, into its "
             "own slot. All `k` threads run at once; main joins them all and only then "
             "prints, in index order, followed by the total. Replace `____` with the "
             "start loop and the join loop.",
             _j29s("        int k = sc.nextInt();\n"
                   "        int[] in = new int[k];\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            in[i] = sc.nextInt();\n"
                   "        }\n"
                   "        int[] parts = new int[k];\n"
                   "        Thread[] workers = new Thread[k];\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int idx = i;\n"
                   "            workers[i] = new Thread(() -> parts[idx] = in[idx] * in[idx], \"w\" + idx);\n"
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
                   "        System.out.println(total);"),
             "        for (int i = 0; i < k; i++) {\n"
             "            final int idx = i;\n"
             "            workers[i] = new Thread(() -> parts[idx] = in[idx] * in[idx], \"w\" + idx);\n"
             "            workers[i].start();\n"
             "        }\n"
             "        for (Thread w : workers) {\n"
             "            w.join();\n"
             "        }",
             [_acase(a, _nl(*([f"{i} {v * v}" for i, v in enumerate(a)]
                              + [sum(v * v for v in a)]))) for a in _A29],
             hints=["Two separate loops: start them ALL, then join them all. One loop "
                    "doing both would be pattern 3, not this one.",
                    "`final int idx = i;` so the lambda has something effectively final to "
                    "capture.",
                    "No thread prints anything. Printing is main's job, after the joins.",
                    "Each thread owns exactly one slot, so no two threads ever write the "
                    "same memory.",
                    "The enhanced `for` over `workers` is a tidy way to join them all."]),

        _jch("j29-order-daemon", "The thread the JVM will not wait for", "Medium",
             "Mark a long-sleeping worker as a daemon and start it. Main prints its line "
             "and returns, and the JVM exits without ever waiting - so the daemon's own "
             "print never happens. Replace `____` with the daemon's creation, the "
             "`setDaemon` call and the start.",
             _j29s("        int n = sc.nextInt();\n"
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
                   "        System.out.println(\"main done \" + n);"),
             "        Thread background = new Thread(() -> {\n"
             "            try {\n"
             "                Thread.sleep(60000);\n"
             "                System.out.println(\"background finished\");\n"
             "            } catch (InterruptedException e) {\n"
             "                System.out.println(\"background interrupted\");\n"
             "            }\n"
             "        }, \"background\");\n"
             "        background.setDaemon(true);\n"
             "        background.start();",
             [_n29(n, "main done " + str(n)) for n in _N29],
             hints=["`setDaemon(true)` goes directly above `start()` - it throws "
                    "IllegalThreadStateException on a thread that is already alive.",
                    "The worker sleeps for a minute, so it cannot possibly finish first.",
                    "Main does not join it - that is the point.",
                    "When main returns there are no user threads left, so the JVM exits "
                    "and the daemon dies where it stands.",
                    "It is killed, not interrupted, so neither of its prints ever runs - "
                    "the only output is main's line."]),

        _je("j29-order-nodaemon", "…and the one it will",
            "The same worker without `setDaemon(true)` is a user thread, so the JVM waits "
            "for it even though main never joins it. Main's line prints first, then the "
            "worker's when it wakes. Replace `____` with the start, and note there is no "
            "join anywhere.",
            _j29s("        int n = sc.nextInt();\n"
                  "        Thread worker = new Thread(() -> {\n"
                  "            try {\n"
                  "                Thread.sleep(250);\n"
                  "                System.out.println(\"worker finished\");\n"
                  "            } catch (InterruptedException e) {\n"
                  "                System.out.println(\"worker interrupted\");\n"
                  "            }\n"
                  "        }, \"worker\");\n"
                  "        worker.start();\n"
                  "        System.out.println(\"main done \" + n);"),
            "        worker.start();",
            [_n29(n, _nl("main done " + str(n), "worker finished")) for n in _N29],
            hints=["No `setDaemon` call, so this is an ordinary user thread.",
                   "Main reaches its own print long before the worker's sleep is up.",
                   "Main returning does NOT end the JVM while a user thread is still "
                   "alive.",
                   "So the process stays up, the worker wakes, prints, and only then does "
                   "the JVM exit.",
                   "The sleep is what makes this particular order reliable - in general, two "
                   "unjoined threads have no order at all."],
            difficulty="Medium"),

        _jfix("j29-order-early", "Read after the join, not before it",
              "This starts the worker and prints the slot immediately, before the worker "
              "has had a chance to write it - so it prints `0`. Move the read after a "
              "`join()`, which is the only thing that orders the write against it.",
              _j29s("        int n = sc.nextInt();\n"
                    "        int[] out = new int[1];\n"
                    "        Thread worker = new Thread(() -> {\n"
                    "            try {\n"
                    "                Thread.sleep(250);\n"
                    "            } catch (InterruptedException e) {\n"
                    "                Thread.currentThread().interrupt();\n"
                    "            }\n"
                    "            out[0] = n * 7;\n"
                    "        }, \"worker\");\n"
                    "        worker.start();\n"
                    "        System.out.println(out[0]);"),
              _j29s("        int n = sc.nextInt();\n"
                    "        int[] out = new int[1];\n"
                    "        Thread worker = new Thread(() -> {\n"
                    "            try {\n"
                    "                Thread.sleep(250);\n"
                    "            } catch (InterruptedException e) {\n"
                    "                Thread.currentThread().interrupt();\n"
                    "            }\n"
                    "            out[0] = n * 7;\n"
                    "        }, \"worker\");\n"
                    "        worker.start();\n"
                    "        worker.join();\n"
                    "        System.out.println(out[0]);"),
              [_n29(n, str(n * 7)) for n in _N29],
              hints=["`start()` returns immediately - it does not wait for anything.",
                     "The sleep makes the bug obvious every run, but the bug is there "
                     "without it too.",
                     "Adding a `sleep` in MAIN would be the wrong fix: it makes the right "
                     "answer likely rather than certain.",
                     "`worker.join();` between the start and the read is the whole fix.",
                     "join both waits for the write and makes it visible - the two halves "
                     "you need."],
              difficulty="Easy"),
    ],
    quiz=[
        _jq("`setDaemon(true)` on a thread that is currently running…",
            ["throws IllegalThreadStateException - the flag cannot change while a "
             "thread is alive",
             "works, and takes effect immediately", "is silently ignored",
             "turns it into a user thread"],
            0,
            "The javadoc's condition is `isAlive()`, so put it above `start()`."),
        _jq("Making output deterministic by adding a `sleep` before a read is…",
            ["wrong - it makes the right answer likely, not guaranteed",
             "correct and idiomatic", "the same as a join",
             "faster than joining"],
            0,
            "It converts an obvious failure into a rare one."),
    ],
))


# ===========================================================================
# Capstone
# ===========================================================================

_M29_CAP_BODY = (
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
    "        System.out.println(total);"
)


def _cap29(a, k):
    """The Python mirror: k contiguous chunks, chunk i is [i*n/k, (i+1)*n/k)."""
    n = len(a)
    lines = []
    total = 0
    for i in range(k):
        part = sum(a[i * n // k:(i + 1) * n // k])
        total += part
        lines.append(f"{i} {part}")
    lines.append(str(total))
    return _nl(*lines)


_M29_CAP = _jcap(
    "The parallel sum",
    """
Split an array into `k` contiguous chunks, sum each chunk on its own thread, and
combine.

The arithmetic is the easy half. The design is the point, and it is the whole
module in one program:

* **One slot per worker.** Worker `i` writes `parts[i]` and nothing else. No two
  threads ever write the same memory, so there is nothing here that module 30
  would need to protect - and that is a *design* choice, not luck.
* **No worker prints.** Printing is main's job, after every join, walking the
  array in index order. The work is concurrent; the output is not.
* **Capture what a lambda may capture.** `i` is reassigned by the loop, so the
  bounds have to be copied into `final` locals before the lambda can see them.
* **Chunking that always covers the array.** `from = i * n / k`,
  `to = (i + 1) * n / k`. Consecutive chunks meet exactly, the last one ends at
  `n`, and no chunk is ever missed or double-counted - even when `k` does not
  divide `n`. An empty chunk sums to zero and prints as one, which is right.

Run it twice and the output is byte-for-byte identical. That is the standard.
""",
    _jch("j29-cap-parsum", "The parallel sum", "Hard",
         "Read `n`, the `n` values, then `k`. Sum each of the `k` chunks on its own "
         "thread, print `index sum` for each chunk in index order, then the grand total.",
         _j29s(_M29_CAP_BODY),
         _M29_CAP_BODY,
         [_akcase(a, k, _cap29(a, k))
          for (a, k) in ((_A29[0], 3), (_A29[1], 1), (_A29[2], 2),
                         (_A29[3], 2), (_A29[4], 4))],
         hints=["Read all the input on the main thread first - a Scanner is not something "
                "to share between threads.",
                "`final int from = idx * n / k;` and `final int to = (idx + 1) * n / k;` "
                "inside the loop, so the lambda can capture them.",
                "Accumulate into a LOCAL `sum` inside the lambda, and assign `parts[idx]` "
                "once at the end.",
                "Start every worker in the first loop; join every worker in a second loop "
                "afterwards.",
                "If you join inside the start loop you get the right answer with no "
                "parallelism at all.",
                "Main prints `i + \" \" + parts[i]` for each chunk, then the total.",
                "When `k` does not divide `n` the chunks come out uneven - that is "
                "expected, and the totals still add up.",
                "A chunk with no elements prints `0`; do not special-case it."]),
    example_io="stdin:  6\n        1 2 3 4 5 6\n        3\n\n"
               "stdout: 0 3\n        1 7\n        2 11\n        21",
    rubric=[
        "Every worker writes its own `parts[i]` and no shared accumulator.",
        "No worker prints; main produces all output after joining.",
        "Loop bounds are copied into `final` locals before being captured.",
        "All `k` threads are started before any is joined.",
        "Every thread is joined before any slot is read.",
        "Chunk bounds cover the array exactly, with no gap and no overlap, for any `k`.",
        "The output is identical on every run.",
    ],
    stretch=None,
)


_MODULES.append(_jmod(
    29, 10, "Multithreading",
    "Threads, and what they cost",
    "A second line of execution in the same process - how to make one, what it shares "
    "with you, and how to get an answer back out of it that you can trust.",
    """
A **thread** is a second place in the same program where execution is happening.
Threads share the heap - every object, every array, every static field - and
share nothing of each other's local variables.

* **Three ways to say what a thread should do**: implement `Runnable` (preferred),
  extend `Thread`, or write a lambda, since `Runnable` is a functional interface.
* **`start()` versus `run()`** is the interview question. `start()` asks the JVM
  for a new thread; `run()` is an ordinary method call on the thread you are
  already on. The tell is which name `Thread.currentThread().getName()` prints.
* **Six states**, of which two can be asserted on: `NEW` before `start()`,
  `TERMINATED` after `join()`. A Thread object is single-use - a second
  `start()` throws.
* **`join()` is the ordering tool.** It waits, and it publishes: everything the
  worker wrote is visible to you once it returns. Reading a worker's result
  without a join is not a slow bug, it is an invalid program.
* **Interruption is a request**, not a kill. `sleep` and `join` throw
  `InterruptedException` when interrupted - and clear the flag on the way out.
* **Order comes from `join`, never from `sleep` and never from priorities.**

Everything about two threads writing the *same* variable is module 30. This
module keeps them strictly apart - one slot per worker - which is why every
program in it prints the same thing every time.
""",
    _M29,
    capstone=_M29_CAP,
    objectives=[
        "Say what a thread has of its own and what it shares with every other thread.",
        "Distinguish concurrency from parallelism.",
        "Create a thread three ways, and say why `Runnable` is preferred to extending `Thread`.",
        "Explain what `run()` does instead of `start()`, and how to detect the mistake.",
        "Name the six thread states and say which two can be relied on.",
        "Use `join()` to order a worker's write against your read, and say why it is needed.",
        "Use `sleep`, and say which thread it affects and what it throws.",
        "Explain interruption as a request, and what catching `InterruptedException` does to the flag.",
        "Say when the JVM exits, and what a daemon thread is for.",
        "Make threaded output deterministic with one slot per thread and a join before every read.",
    ],
    why="Threads are where confident Java programmers start guessing. The questions are "
        "predictable - `start()` versus `run()`, the lifecycle states, what `join` "
        "actually guarantees, why there is no `stop()` - and they all have exact answers "
        "that most candidates half-know. The deeper habit this module builds is the one "
        "that survives the interview: threaded code you cannot predict the output of is "
        "not code you can test, and the fix is structural - give every worker its own "
        "slot and order every read behind a join - rather than a `sleep` in the right "
        "place.",
    est_minutes=300,
    glossary=[
        _jg("process", "A running program with its own memory. Two processes share no "
                       "objects."),
        _jg("thread", "A line of execution inside a process, with its own stack but "
                      "sharing the process's heap and static fields."),
        _jg("main thread", "The thread the JVM creates to call `main`. Its name is `main`."),
        _jg("concurrency", "Several tasks in flight at once - a structure, whether or not "
                           "they truly execute simultaneously."),
        _jg("parallelism", "Two things executing at the same instant, which needs more "
                           "than one core."),
        _jg("Runnable", "The functional interface holding the work: one method, "
                        "`void run()`, which cannot return a value or throw a checked "
                        "exception."),
        _jg("start()", "Asks the JVM for a new thread, which then calls `run()`. Legal "
                       "exactly once per Thread object."),
        _jg("join()", "Blocks until a thread terminates, and makes everything it wrote "
                      "visible to the joining thread."),
        _jg("daemon thread", "A thread the JVM will not wait for; the JVM exits when the "
                             "last USER thread ends. Set before `start()`."),
        _jg("interrupt", "A request to stop, delivered as a flag. Blocking calls throw "
                         "`InterruptedException` and clear the flag."),
        _jg("IllegalThreadStateException", "Thrown by a second `start()`, or by "
                                           "`setDaemon` after `start()`."),
    ],
    cheatsheet="""
```java
// --- making one -----------------------------------------------------------
class Job implements Runnable { public void run() { ... } }   // preferred
class T2 extends Thread      { public void run() { ... } }    // spends inheritance
Thread t = new Thread(() -> ..., "worker");   // Runnable is functional

// --- the one that matters -------------------------------------------------
t.start();    // NEW THREAD, which calls run()      -> prints "worker"
t.run();      // ordinary call on the current thread -> prints "main"
t.start();    // a SECOND time: IllegalThreadStateException

// --- states (getState()) --------------------------------------------------
NEW  RUNNABLE  BLOCKED  WAITING  TIMED_WAITING  TERMINATED
//   ^ before start()                                ^ after join()
//   the only two you can assert on; RUNNABLE means "running OR ready"

// --- waiting --------------------------------------------------------------
Thread.sleep(50);      // STATIC: sleeps the CURRENT thread. t.sleep(50) is a trap.
worker.join();         // waits AND publishes the worker's writes
worker.join(100);      // ...or gives up after 100ms - check isAlive() after
t.isAlive();           // false before start() and after run() returns

// --- interruption (a request, not a kill) ---------------------------------
t.interrupt();                        // set the flag
t.isInterrupted();                    // read it
Thread.interrupted();                 // read AND clear (static, current thread)
// sleep/join/wait throw InterruptedException AND CLEAR THE FLAG:
catch (InterruptedException e) { Thread.currentThread().interrupt(); }  // restore it

// --- daemon / priority ----------------------------------------------------
t.setDaemon(true);     // BEFORE start(). JVM exits when the last USER thread ends.
t.setPriority(...);    // a hint. Never a correctness tool.

// --- the three deterministic patterns -------------------------------------
worker.start(); worker.join(); read(result);        // 1. join before you read
for (...) { t[i].start(); }  for (...) { t[i].join(); }  print(parts);  // 2. a slot each
for (...) { t.start(); t.join(); }                  // 3. strict sequence

// --- and the anti-pattern -------------------------------------------------
a.start(); b.start();          // "a" then "b"? either. NO ordering exists.
Thread.sleep(100); read(x);    // makes the right answer LIKELY. Not a fix.
```
""",
    self_check=[
        "Can you say what two threads share, and what they never share?",
        "Can you give the difference between concurrency and parallelism in one sentence each?",
        "Can you say what `t.run()` does, and how you would detect it in output?",
        "Can you name all six thread states, and the two you can assert on?",
        "Can you say what `join()` guarantees beyond 'it waited'?",
        "Can you say which thread `Thread.sleep` affects, and what it throws?",
        "Can you say what catching `InterruptedException` does to the interrupt flag, and what to do about it?",
        "Can you say when the JVM exits, and what that means for a daemon thread?",
        "Can you explain why a lambda in a `for` loop needs `final int idx = i;`?",
        "Can you take a threaded program with unpredictable output and make it deterministic?",
    ],
    review=[
        _jq("```java\nThread t = new Thread(\n        () -> System.out.println(Thread.currentThread().getName()),\n        \"worker\");\nt.run();\n```\nWhat prints?",
            ["main", "worker", "Thread-0", "nothing"],
            0,
            "`run()` is a plain method call - no thread was created."),
        _jq("Reading a worker's result without joining is…",
            ["invalid - nothing orders the worker's write against your read",
             "fine if you sleep first", "fine, just slower",
             "fine if the field is an int"],
            0,
            "join is what both waits and publishes."),
        _jq("`t.start()` on a thread that has already terminated…",
            ["throws IllegalThreadStateException", "runs it again",
             "is a no-op", "resets it to NEW"],
            0,
            "Thread objects are single-use; construct another."),
        _jq("A lambda inside `for (int i = 0; ...)` cannot capture `i` because…",
            ["`i` is reassigned each pass, so it is not effectively final",
             "lambdas cannot capture ints", "`i` is private",
             "the loop has not finished"],
            0,
            "Copy it: `final int idx = i;` - module 25's rule, met again."),
        _jq("The JVM exits when…",
            ["the last user thread finishes", "main returns",
             "the last thread of any kind finishes", "every daemon finishes"],
            0,
            "Daemons are abandoned wherever they happen to be."),
    ],
    milestone="You can create threads three ways, say exactly what `start()` does that "
              "`run()` does not, name the lifecycle and the two states worth asserting "
              "on, and - the part that actually matters - write threaded programs whose "
              "output is the same on every run, because every read sits behind a join and "
              "every worker owns its own slot.",
))
