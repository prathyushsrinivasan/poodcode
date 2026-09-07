# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 30 practice - shared state: races, locks and visibility.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[30]`.
#
# Same gate as the module file: `Thread`/`Runnable` (29), `synchronized`,
# `volatile`, the atomics and `ReentrantLock` (30) - and no `ExecutorService`,
# `Callable`, `Future` or concurrent collection, which are module 31.
#
# Same determinism discipline too, and it is the whole reason these 25 programs
# can be graded at all:
#
#   * a CORRECTLY synchronised counter driven k*m times prints exactly k*m,
#     every run, on every machine - so most variants are simply the right
#     answer;
#   * where the LOST UPDATE is the answer, the interleaving is staged with
#     joins: one thread reads and stops, k threads then increment cleanly, and
#     finally the first thread's stale write lands. Every step is ordered, so
#     the output is fixed, and it is still a real lost update by real threads;
#   * anything whose answer would depend on WHICH thread won is run strictly one
#     thread at a time.
#
# NOTE for anyone extending this file: do NOT reach for a sleep to "widen the
# race window" and make an unsynchronised result predictable. The first draft of
# this module did exactly that with 40ms, and it failed verification at k=2, 4
# and 5 - the verifier runs exercises in parallel and thread start-up on a
# loaded machine can outlast the window. Stage it with joins instead.
# ---------------------------------------------------------------------------

_IMPORTS30P = ("import java.util.*;\n"
               "import java.util.concurrent.atomic.*;\n"
               "import java.util.concurrent.locks.*;\n")

_SIG30P = "    public static void main(String[] args) throws InterruptedException {"

_CATCH30P = ("            } catch (InterruptedException e) {\n"
             "                Thread.currentThread().interrupt();\n"
             "            }\n")


def _p30prog(body):
    return _jcls(
        _SIG30P + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }",
        imports=_IMPORTS30P,
    )


def _p30t(types, body):
    return _jp(
        _IMPORTS30P + "\n"
        + types.rstrip("\n") + "\n\n"
        + "public class Main {\n"
        + _SIG30P + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }\n}"
    )


def _p30s(eid, title, difficulty, prompt, body, tests, hints):
    """Write main's whole body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p30prog(body), body, tests, hints)


def _p30c(eid, title, difficulty, prompt, types, body, tests, hints):
    """Write main's body; the helper classes are given."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p30t(types, body), body, tests, hints)


def _p30m(eid, title, difficulty, prompt, types, body, tests, hints):
    """Write the helper CLASS; main is given."""
    return _jch(eid, title, difficulty, prompt, _p30t(types, body),
                types.rstrip("\n").lstrip("\n"), tests, hints)


_K30P = (2, 3, 4, 5, 2)
_KM30P = ((2, 500), (3, 400), (4, 250), (5, 200), (2, 1000))


def _k30p(k, out):
    return _case(str(k), out)


def _km30p(k, m, out):
    return _case(f"{k} {m}", out)


# The start-all-then-join-all scaffolding every counter variant shares.
def _drive30(inner, name="w"):
    return ("        Thread[] workers = new Thread[k];\n"
            "        for (int i = 0; i < k; i++) {\n"
            "            workers[i] = new Thread(" + inner + ", \"" + name + "\" + i);\n"
            "            workers[i].start();\n"
            "        }\n"
            "        for (Thread w : workers) {\n"
            "            w.join();\n"
            "        }\n")


# ===========================================================================
# Family A - the lost update
# ===========================================================================

_P30_A = _jfam(
    "p30-race", "The lost update",
    "Read, then write much later - and watch k increments become one.",
    """
`count++` is a read, an add and a write, and anything may happen between them.
To make that visible rather than merely true, these variants **stage** the
interleaving with joins:

```java
Thread reader = new Thread(() -> stale[0] = counter[0]);   // the READ half
reader.start(); reader.join();

for (...) { bump.start(); bump.join(); }                   // k clean increments

Thread writer = new Thread(() -> counter[0] = stale[0] + 1);  // the WRITE half
writer.start(); writer.join();                             // ...lands far too late
```

Every step is ordered by a join, so the program prints the same thing every run
- and it is still a genuine lost update, performed by genuine threads. The
counter climbs to `k` and then collapses to `1`.

In real code nobody arranges this. The three phases are nanoseconds apart, the
JVM interleaves them at random, and the result is a total that is merely a
little too small. The fixes come in the families that follow; here the job is to
see the shape.
""",
    [
        _p30s("j30-pa-lost", "k increments, one result", "Medium",
              "Stage the interleaving. A reader thread copies the counter into `stale` "
              "and ends. Then `k` threads each increment the counter properly, started "
              "and joined one at a time - print the count, which is `k`. Then a writer "
              "thread completes the reader's half-finished increment by writing "
              "`stale + 1` - print the count again, which is `1`.",
              "        int k = sc.nextInt();\n"
              "        int[] counter = new int[1];\n"
              "        int[] stale = new int[1];\n"
              "        Thread reader = new Thread(() -> stale[0] = counter[0], \"reader\");\n"
              "        reader.start();\n"
              "        reader.join();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            Thread bump = new Thread(() -> counter[0] = counter[0] + 1, \"b\" + i);\n"
              "            bump.start();\n"
              "            bump.join();\n"
              "        }\n"
              "        System.out.println(counter[0]);\n"
              "        Thread writer = new Thread(() -> counter[0] = stale[0] + 1, \"writer\");\n"
              "        writer.start();\n"
              "        writer.join();\n"
              "        System.out.println(counter[0]);",
              [_k30p(k, _nl(k, 1)) for k in _K30P],
              ["The reader performs only the READ half of a read-modify-write, then "
               "ends.",
               "The `k` bump threads are joined one at a time, so the count climbs "
               "cleanly to `k`.",
               "The writer performs the WRITE half, using the value read long ago.",
               "`stale[0]` is 0, so the counter is set to 1 and every increment is "
               "discarded.",
               "Joins make this reproducible; in real code the same thing happens in "
               "nanoseconds, unarranged."]),

        _p30s("j30-pa-both", "The count, and what it should have been", "Medium",
              "The same staged lost update, but account for the damage: print the final "
              "count, then `k`, then how many increments were thrown away.",
              "        int k = sc.nextInt();\n"
              "        int[] counter = new int[1];\n"
              "        int[] stale = new int[1];\n"
              "        Thread reader = new Thread(() -> stale[0] = counter[0], \"reader\");\n"
              "        reader.start();\n"
              "        reader.join();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            Thread bump = new Thread(() -> counter[0] = counter[0] + 1, \"b\" + i);\n"
              "            bump.start();\n"
              "            bump.join();\n"
              "        }\n"
              "        Thread writer = new Thread(() -> counter[0] = stale[0] + 1, \"writer\");\n"
              "        writer.start();\n"
              "        writer.join();\n"
              "        System.out.println(counter[0]);\n"
              "        System.out.println(k);\n"
              "        System.out.println(k - counter[0]);",
              [_k30p(k, _nl(1, k, k - 1)) for k in _K30P],
              ["The final count is 1 for every `k`.",
               "The intended total is `k` - one increment per bump thread.",
               "So the loss is `k - 1`.",
               "Nothing in the program can detect this by itself; only knowing the "
               "intended answer reveals it.",
               "That is why races are found by reasoning about the code, not by running "
               "it."]),

        _p30s("j30-pa-serial", "The same code, one thread at a time", "Easy",
              "Identical Runnable, but started and joined one at a time so the threads "
              "never overlap. Now every read sees the previous write and the count "
              "reaches `k`.",
              "        int k = sc.nextInt();\n"
              "        int[] counter = new int[1];\n"
              "        Runnable job = () -> {\n"
              "            int seen = counter[0];\n"
              "            try {\n"
              "                Thread.sleep(5);\n"
              + _CATCH30P
              + "            counter[0] = seen + 1;\n"
                "        };\n"
                "        for (int i = 0; i < k; i++) {\n"
                "            Thread t = new Thread(job, \"w\" + i);\n"
                "            t.start();\n"
                "            t.join();\n"
                "        }\n"
                "        System.out.println(counter[0]);",
              [_k30p(k, str(k)) for k in _K30P],
              ["The join moves INSIDE the loop, right after the start.",
               "That removes every overlap, and with it the race.",
               "The unsafe code is unchanged - only the scheduling is.",
               "This is not a fix, it is the absence of concurrency.",
               "It is still a useful diagnostic: if serialising makes the bug go away, "
               "it was a race."]),

        _p30c("j30-pa-object", "A race inside an object", "Medium",
              "`Meter` splits a read-modify-write into `read()` and `writeBack()`, which "
              "is what an unsynchronised `bump()` amounts to. Stage it: a reader thread "
              "calls `read()`, `k` threads then bump cleanly, and a writer thread finally "
              "calls `writeBack()`. Print the reading before and after that last write.",
              "class Meter {\n"
              "    private int reading;\n\n"
              "    int read() {\n"
              "        return reading;\n"
              "    }\n\n"
              "    void writeBack(int seen) {\n"
              "        reading = seen + 1;\n"
              "    }\n\n"
              "    void bump() {\n"
              "        reading = reading + 1;\n"
              "    }\n\n"
              "    int reading() {\n"
              "        return reading;\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        Meter meter = new Meter();\n"
              "        int[] stale = new int[1];\n"
              "        Thread reader = new Thread(() -> stale[0] = meter.read(), \"reader\");\n"
              "        reader.start();\n"
              "        reader.join();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            Thread bump = new Thread(meter::bump, \"b\" + i);\n"
              "            bump.start();\n"
              "            bump.join();\n"
              "        }\n"
              "        System.out.println(meter.reading());\n"
              "        Thread writer = new Thread(() -> meter.writeBack(stale[0]), \"writer\");\n"
              "        writer.start();\n"
              "        writer.join();\n"
              "        System.out.println(meter.reading());",
              [_k30p(k, _nl(k, 1)) for k in _K30P],
              ["`meter::bump` is a method reference, and `Runnable` is a functional "
               "interface - module 25 again.",
               "`read()` and `writeBack()` are the two halves an unguarded `bump()` "
               "really consists of.",
               "Every thread works on the SAME Meter, so they share the field.",
               "After `k` clean bumps the reading is `k`; the stale write drops it to 1.",
               "`private` protects against the wrong code touching the field. It does "
               "nothing at all about two threads."]),

        _p30s("j30-pa-noshare", "The race designed away", "Easy",
              "The same `k` increments with no shared variable at all: thread `i` writes "
              "1 into `parts[i]`, and main adds them up after joining. The answer is `k`, "
              "with no lock anywhere.",
              "        int k = sc.nextInt();\n"
              "        int[] parts = new int[k];\n"
              "        Thread[] workers = new Thread[k];\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            workers[i] = new Thread(() -> parts[idx] = 1, \"w\" + idx);\n"
              "            workers[i].start();\n"
              "        }\n"
              "        for (Thread w : workers) {\n"
              "            w.join();\n"
              "        }\n"
              "        int total = 0;\n"
              "        for (int p : parts) {\n"
              "            total += p;\n"
              "        }\n"
              "        System.out.println(total);",
              [_k30p(k, str(k)) for k in _K30P],
              ["Different slots, so no two threads ever write the same memory.",
               "`final int idx = i;` before the lambda.",
               "The joins publish every slot before main reads one.",
               "Main sums them single-threaded, and one thread cannot race itself.",
               "Confinement beats every lock in this module - when it fits."]),
    ])


# ===========================================================================
# Family B - synchronized
# ===========================================================================

_P30_B = _jfam(
    "p30-sync", "`synchronized`",
    "Taking an object's lock - and making sure it is the same object every time.",
    """
```java
synchronized (lock) { counter++; }   // block: you name the lock
synchronized void add() { }          // method: the lock is `this`
static synchronized void tally() { } // static method: the lock is Foo.class
```

Two rules do most of the work:

1. **Threads take turns only if they lock the same object.** A lock created
   inside the task protects nothing.
2. **Guard a field with one lock, consistently.** A field reached by both a
   `static synchronized` and an instance `synchronized` method is guarded by two
   different locks, which is the same as none.
""",
    [
        _p30s("j30-pb-block", "A synchronized block", "Medium",
              "Read `k` and `m`; `k` threads each increment a shared slot `m` times "
              "inside `synchronized (lock)`. Print the total, `k * m`.",
              "        int k = sc.nextInt();\n"
              "        int m = sc.nextInt();\n"
              "        int[] counter = new int[1];\n"
              "        Object lock = new Object();\n"
              "        Runnable job = () -> {\n"
              "            for (int i = 0; i < m; i++) {\n"
              "                synchronized (lock) {\n"
              "                    counter[0]++;\n"
              "                }\n"
              "            }\n"
              "        };\n"
              + _drive30("job")
              + "        System.out.println(counter[0]);",
              [_km30p(k, m, str(k * m)) for (k, m) in _KM30P],
              ["The loop is outside the block, so the lock is taken once per increment.",
               "A critical section should be as small as it can be.",
               "All `k` threads capture and lock the same `lock` object.",
               "`counter[0]++` is the read-modify-write being protected.",
               "The answer is exactly `k * m`, every run."]),

        _p30m("j30-pb-method", "A synchronized method", "Medium",
              "Write `Meter` so that `bump()` and `reading()` are both synchronized on "
              "the instance. `k` threads bump it `m` times each; print `k * m`.",
              "class Meter {\n"
              "    private int reading;\n\n"
              "    synchronized void bump() {\n"
              "        reading++;\n"
              "    }\n\n"
              "    synchronized int reading() {\n"
              "        return reading;\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        int m = sc.nextInt();\n"
              "        Meter meter = new Meter();\n"
              "        Runnable job = () -> {\n"
              "            for (int i = 0; i < m; i++) {\n"
              "                meter.bump();\n"
              "            }\n"
              "        };\n"
              + _drive30("job")
              + "        System.out.println(meter.reading());",
              [_km30p(k, m, str(k * m)) for (k, m) in _KM30P],
              ["`synchronized` sits in the modifier list, before the return type.",
               "On an instance method the lock is `this` - the one shared Meter.",
               "Synchronize the getter too: reading an int is atomic, but that is not "
               "the same as seeing the latest value.",
               "The field stays `private`, so the lock cannot be bypassed.",
               "`k * m` on every run."]),

        _p30s("j30-pb-wronglock", "One lock, not k locks", "Hard",
              "Fix the classic mistake by construction: declare the lock OUTSIDE the "
              "Runnable so all `k` threads share it, guard the read-pause-write, and "
              "print `k`. (A lock created inside the lambda would give one lock per "
              "thread and a count of 1.)",
              "        int k = sc.nextInt();\n"
              "        int[] counter = new int[1];\n"
              "        Object lock = new Object();\n"
              "        Runnable job = () -> {\n"
              "            synchronized (lock) {\n"
              "                int seen = counter[0];\n"
              "                try {\n"
              "                    Thread.sleep(40);\n"
              "                } catch (InterruptedException e) {\n"
              "                    Thread.currentThread().interrupt();\n"
              "                }\n"
              "                counter[0] = seen + 1;\n"
              "            }\n"
              "        };\n"
              + _drive30("job")
              + "        System.out.println(counter[0]);",
              [_k30p(k, str(k)) for k in _K30P],
              ["The lock must be declared beside the data it guards, not inside the "
               "task.",
               "The lambda then CAPTURES it, so every thread takes the same one.",
               "The whole read-pause-write goes inside the block - guarding only the "
               "write would leave the gap open.",
               "Holding a lock across a sleep is terrible practice; here it is what "
               "makes the effect visible.",
               "The count reaches `k` because each thread now reads what the last one "
               "wrote."]),

        _p30m("j30-pb-privatelock", "A lock nobody else can reach", "Medium",
              "Write `Safe` so it guards its field with a `private final Object lock` "
              "rather than with `this` - so no outside code can interfere with its "
              "locking. `k` threads bump it `m` times each; print `k * m`.",
              "class Safe {\n"
              "    private final Object lock = new Object();\n"
              "    private int value;\n\n"
              "    void bump() {\n"
              "        synchronized (lock) {\n"
              "            value++;\n"
              "        }\n"
              "    }\n\n"
              "    int value() {\n"
              "        synchronized (lock) {\n"
              "            return value;\n"
              "        }\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        int m = sc.nextInt();\n"
              "        Safe safe = new Safe();\n"
              "        Runnable job = () -> {\n"
              "            for (int i = 0; i < m; i++) {\n"
              "                safe.bump();\n"
              "            }\n"
              "        };\n"
              + _drive30("job")
              + "        System.out.println(safe.value());",
              [_km30p(k, m, str(k * m)) for (k, m) in _KM30P],
              ["`private final Object lock = new Object();` - final so it cannot be "
               "swapped while a thread waits on it.",
               "Locking `this` is public: any caller holding your object can lock it "
               "too.",
               "Both methods must use the SAME lock, or the field is unguarded.",
               "The getter locks as well, for visibility.",
               "This is module 12's encapsulation extended to the lock itself."]),

        _p30m("j30-pb-static", "The class lock", "Hard",
              "Write `Registry` with a `static synchronized` counter and an instance "
              "`synchronized` counter. They take DIFFERENT locks, which is safe only "
              "because each field is guarded consistently by one of them. `k` threads "
              "bump both `m` times; print the static total then the instance total.",
              "class Registry {\n"
              "    private static int globalCount;\n"
              "    private int localCount;\n\n"
              "    static synchronized void bumpGlobal() {\n"
              "        globalCount++;\n"
              "    }\n\n"
              "    static synchronized int global() {\n"
              "        return globalCount;\n"
              "    }\n\n"
              "    synchronized void bumpLocal() {\n"
              "        localCount++;\n"
              "    }\n\n"
              "    synchronized int local() {\n"
              "        return localCount;\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        int m = sc.nextInt();\n"
              "        Registry registry = new Registry();\n"
              "        Runnable job = () -> {\n"
              "            for (int i = 0; i < m; i++) {\n"
              "                Registry.bumpGlobal();\n"
              "                registry.bumpLocal();\n"
              "            }\n"
              "        };\n"
              + _drive30("job")
              + "        System.out.println(Registry.global());\n"
                "        System.out.println(registry.local());",
              [_km30p(k, m, _nl(k * m, k * m)) for (k, m) in _KM30P],
              ["A `static synchronized` method locks `Registry.class`; an instance one "
               "locks `this`.",
               "So a thread inside one does not block a thread inside the other.",
               "That is safe here only because `globalCount` is always reached through "
               "the class lock and `localCount` always through the instance lock.",
               "A field reached through both would be effectively unguarded.",
               "Both totals come out `k * m`."]),
    ])


# ===========================================================================
# Family C - visibility and volatile
# ===========================================================================

_P30_C = _jfam(
    "p30-visible", "Visibility and `volatile`",
    "Whether the other thread ever finds out - a different question from who went first.",
    """
```java
volatile boolean running = true;   // every read from memory, every write to it
```

`volatile` gives **visibility and ordering**. It does not give **atomicity**:

```java
volatile int count;
count++;          // still read, add, write. Still a race.
```

The fit is one writer, many readers, and a new value that does not depend on the
old - the stop flag. Anything read-modify-write needs a lock or an atomic.

And remember the two happens-before edges module 29 was already leaning on:
everything before `start()` is visible to the new thread, and everything a
thread did is visible after you `join()` it.
""",
    [
        _p30c("j30-pc-stopflag", "The stop flag", "Medium",
              "`Flag` wraps a `volatile boolean`. Start a worker that spins until the "
              "flag drops and then prints `stopped`; main sleeps 30ms, lowers it, joins, "
              "and prints `k`.",
              "class Flag {\n"
              "    private volatile boolean running = true;\n\n"
              "    boolean isRunning() {\n"
              "        return running;\n"
              "    }\n\n"
              "    void stop() {\n"
              "        running = false;\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        Flag flag = new Flag();\n"
              "        Thread worker = new Thread(() -> {\n"
              "            while (flag.isRunning()) {\n"
              "                // spin until main lowers the flag\n"
              "            }\n"
              "            System.out.println(\"stopped\");\n"
              "        }, \"worker\");\n"
              "        worker.start();\n"
              "        Thread.sleep(30);\n"
              "        flag.stop();\n"
              "        worker.join();\n"
              "        System.out.println(k);",
              [_k30p(k, _nl("stopped", k)) for k in _K30P],
              ["The loop condition re-reads the flag every pass.",
               "`stopped` prints once the loop ends, before main's number.",
               "`volatile` is what guarantees the worker's next read sees `false`.",
               "Without it the JVM may hoist the read out of the loop and spin forever - "
               "legally.",
               "A spin loop burns a core; real code waits instead, which is module 31."]),

        _p30c("j30-pc-notatomic", "Fresh, and still wrong", "Hard",
              "`Counter.value` is `volatile`, so every read really is the newest value - "
              "and the lost update happens anyway, because the gap is between the read "
              "and the write. Stage it exactly as in family A: a reader reads and stops, "
              "`k` threads increment cleanly (print the count), then the stale write "
              "lands (print it again).",
              "class Counter {\n"
              "    private volatile int value;\n\n"
              "    int get() {\n"
              "        return value;\n"
              "    }\n\n"
              "    void set(int v) {\n"
              "        value = v;\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        Counter counter = new Counter();\n"
              "        int[] stale = new int[1];\n"
              "        Thread reader = new Thread(() -> stale[0] = counter.get(), \"reader\");\n"
              "        reader.start();\n"
              "        reader.join();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            Thread bump = new Thread(() -> counter.set(counter.get() + 1), \"b\" + i);\n"
              "            bump.start();\n"
              "            bump.join();\n"
              "        }\n"
              "        System.out.println(counter.get());\n"
              "        Thread writer = new Thread(() -> counter.set(stale[0] + 1), \"writer\");\n"
              "        writer.start();\n"
              "        writer.join();\n"
              "        System.out.println(counter.get());",
              [_k30p(k, _nl(k, 1)) for k in _K30P],
              ["Every `get()` really does return the freshest value - `volatile` "
               "delivers exactly what it promises.",
               "The problem is the gap between the `get` and the `set`.",
               "No field modifier can turn two calls into one operation.",
               "The count reaches `k`, then collapses to 1 when the stale write lands.",
               "The cure is a lock, or `incrementAndGet` - never `volatile` alone."]),

        _p30s("j30-pc-publish", "Published by start and join", "Medium",
              "No `volatile` anywhere and still correct. Fill an array on main, start a "
              "worker that sums it into a slot, join, and print - `start()` publishes "
              "main's writes to the worker, and `join()` publishes the worker's back.",
              "        int k = sc.nextInt();\n"
              "        int[] data = new int[k];\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            data[i] = i + 1;\n"
              "        }\n"
              "        int[] out = new int[1];\n"
              "        Thread worker = new Thread(() -> {\n"
              "            int sum = 0;\n"
              "            for (int v : data) {\n"
              "                sum += v;\n"
              "            }\n"
              "            out[0] = sum;\n"
              "        }, \"worker\");\n"
              "        worker.start();\n"
              "        worker.join();\n"
              "        System.out.println(out[0]);",
              [_k30p(k, str(k * (k + 1) // 2)) for k in _K30P],
              ["Everything main did before `start()` is visible to the new thread.",
               "Everything the worker did is visible after `join()` returns.",
               "So neither the input array nor the result slot needs `volatile`.",
               "Only one thread touches each piece at a time; the handoffs are the start "
               "and the join.",
               "The answer is the triangular number of `k`."]),

        _p30m("j30-pc-safepublish", "Immutable, so nothing to publish", "Medium",
              "Write `Reading` as an immutable value: two `final` fields, no setters, "
              "`toString` printing `value@when`. Two threads each build their own from a "
              "shared origin; nothing is ever mutated, so nothing needs guarding.",
              "class Reading {\n"
              "    private final int value;\n"
              "    private final int when;\n\n"
              "    Reading(int value, int when) {\n"
              "        this.value = value;\n"
              "        this.when = when;\n"
              "    }\n\n"
              "    Reading later(int by) {\n"
              "        return new Reading(value, when + by);\n"
              "    }\n\n"
              "    @Override\n"
              "    public String toString() {\n"
              "        return value + \"@\" + when;\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        Reading origin = new Reading(k, 0);\n"
              "        Reading[] out = new Reading[2];\n"
              "        Thread a = new Thread(() -> out[0] = origin.later(1), \"a\");\n"
              "        Thread b = new Thread(() -> out[1] = origin.later(2), \"b\");\n"
              "        a.start();\n"
              "        b.start();\n"
              "        a.join();\n"
              "        b.join();\n"
              "        System.out.println(origin);\n"
              "        System.out.println(out[0]);\n"
              "        System.out.println(out[1]);",
              [_k30p(k, _nl(f"{k}@0", f"{k}@1", f"{k}@2")) for k in _K30P],
              ["Both fields `final`, assigned once in the constructor, with no setter.",
               "`later` returns a NEW Reading rather than changing this one.",
               "Two threads only read `origin`, and readers never race.",
               "`final` fields have a publication guarantee of their own: a correctly "
               "constructed immutable object is safe to share with no synchronisation.",
               "`origin` prints unchanged, because nothing could have changed it."]),

        _p30s("j30-pc-confined", "Confined to one thread", "Easy",
              "The cheapest safety of all: data no other thread can see. Each of `k` "
              "threads builds its own local total from its own index and writes it to its "
              "own slot; main prints the slots and their sum.",
              "        int k = sc.nextInt();\n"
              "        int[] parts = new int[k];\n"
              "        Thread[] workers = new Thread[k];\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            workers[i] = new Thread(() -> {\n"
              "                int local = 0;\n"
              "                for (int j = 0; j <= idx; j++) {\n"
              "                    local += j;\n"
              "                }\n"
              "                parts[idx] = local;\n"
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
              [_k30p(k, _nl(*([f"{i} {i * (i + 1) // 2}" for i in range(k)]
                              + [sum(i * (i + 1) // 2 for i in range(k))])))
               for k in _K30P],
              ["`local` lives on the worker's own stack - no other thread can name it.",
               "The only shared write is `parts[idx]`, and each index has one owner.",
               "`final int idx = i;` before the lambda.",
               "Main aggregates after every join, single-threaded.",
               "Thread `i` computes 0+1+...+i."]),
    ])


# ===========================================================================
# Family D - atomics
# ===========================================================================

_P30_D = _jfam(
    "p30-atomic", "Atomics",
    "One indivisible read-modify-write, and no lock in sight.",
    """
```java
AtomicInteger c = new AtomicInteger(0);
c.incrementAndGet();    // ++c : the NEW value
c.getAndIncrement();    // c++ : the OLD value
c.addAndGet(5);
c.compareAndSet(expected, next);   // swap only if unchanged; true if it did
```

Underneath is a hardware compare-and-set, retried in a loop, so a thread that
loses never blocks - it just tries again.

The trap is composition. Each *call* is atomic; two calls are not:

```java
c.set(c.get() + 1);     // exactly the family A race, in nicer clothing
```
""",
    [
        _p30s("j30-pd-increment", "The lock-free counter", "Medium",
              "Read `k` and `m`; `k` threads each call `incrementAndGet()` `m` times on "
              "one shared `AtomicInteger`. Print the total, `k * m` - with no lock.",
              "        int k = sc.nextInt();\n"
              "        int m = sc.nextInt();\n"
              "        AtomicInteger count = new AtomicInteger(0);\n"
              "        Runnable job = () -> {\n"
              "            for (int i = 0; i < m; i++) {\n"
              "                count.incrementAndGet();\n"
              "            }\n"
              "        };\n"
              + _drive30("job")
              + "        System.out.println(count.get());",
              [_km30p(k, m, str(k * m)) for (k, m) in _KM30P],
              ["One shared `AtomicInteger`, captured by every lambda.",
               "`incrementAndGet()` is the whole read-modify-write, indivisibly.",
               "No thread ever blocks - a loser retries in hardware.",
               "Start all, then join all.",
               "The total is exactly `k * m`."]),

        _p30s("j30-pd-names", "Old value or new", "Easy",
              "Starting from `k`: print `getAndIncrement()`, then `incrementAndGet()`, "
              "then `addAndGet(10)`, then `get()`.",
              "        int k = sc.nextInt();\n"
              "        AtomicInteger count = new AtomicInteger(k);\n"
              "        System.out.println(count.getAndIncrement());\n"
              "        System.out.println(count.incrementAndGet());\n"
              "        System.out.println(count.addAndGet(10));\n"
              "        System.out.println(count.get());",
              [_k30p(k, _nl(k, k + 2, k + 12, k + 12)) for k in _K30P],
              ["`getAndIncrement` is `k++`: it hands back the old value, `k`.",
               "The counter is now `k + 1`.",
               "`incrementAndGet` is `++k`: it hands back the new value, `k + 2`.",
               "`addAndGet(10)` returns the new value again, `k + 12`.",
               "The final `get()` agrees with the line above it."]),

        _p30s("j30-pd-cas", "Compare and set", "Medium",
              "Starting from `k`: a successful `compareAndSet(k, k + 10)`, then a failed "
              "`compareAndSet(k, 999)`, then the value.",
              "        int k = sc.nextInt();\n"
              "        AtomicInteger count = new AtomicInteger(k);\n"
              "        System.out.println(count.compareAndSet(k, k + 10));\n"
              "        System.out.println(count.compareAndSet(k, 999));\n"
              "        System.out.println(count.get());",
              [_k30p(k, _nl("true", "false", k + 10)) for k in _K30P],
              ["The first call finds `k`, swaps, and returns `true`.",
               "The value is now `k + 10`.",
               "The second still expects `k`, does not find it, and returns `false`.",
               "It changes nothing, so `999` is never written.",
               "'I did not clobber anyone else's change' is the guarantee every retry "
               "loop is built on."]),

        _p30s("j30-pd-caslooop", "Compare-and-set by hand", "Hard",
              "Write `incrementAndGet` yourself: `k` threads, each looping until its own "
              "`compareAndSet` succeeds, `m` times each. Print `k * m`.",
              "        int k = sc.nextInt();\n"
              "        int m = sc.nextInt();\n"
              "        AtomicInteger count = new AtomicInteger(0);\n"
              "        Runnable job = () -> {\n"
              "            for (int i = 0; i < m; i++) {\n"
              "                int old;\n"
              "                do {\n"
              "                    old = count.get();\n"
              "                } while (!count.compareAndSet(old, old + 1));\n"
              "            }\n"
              "        };\n"
              + _drive30("job")
              + "        System.out.println(count.get());",
              [_km30p(k, m, str(k * m)) for (k, m) in _KM30P],
              ["Read the current value, then try to swap it for one more.",
               "If the swap fails somebody else changed it, so read again and retry.",
               "`do { old = count.get(); } while (!count.compareAndSet(old, old + 1));`",
               "This is exactly what `incrementAndGet` does inside the JDK.",
               "No thread blocks; a loser just goes round again. That is lock-free."]),

        _p30c("j30-pd-notenough", "When one atomic is not enough", "Hard",
              "Two fields that must change together cannot be covered by a single "
              "atomic, so `Pair` guards both with one lock. `k` threads each move 1 from "
              "left to right; the total is invariant. Print left, right and the total.",
              "class Pair {\n"
              "    private final Object lock = new Object();\n"
              "    private int left;\n"
              "    private int right;\n\n"
              "    Pair(int left, int right) {\n"
              "        this.left = left;\n"
              "        this.right = right;\n"
              "    }\n\n"
              "    void move() {\n"
              "        synchronized (lock) {\n"
              "            left--;\n"
              "            right++;\n"
              "        }\n"
              "    }\n\n"
              "    int left() {\n"
              "        synchronized (lock) {\n"
              "            return left;\n"
              "        }\n"
              "    }\n\n"
              "    int right() {\n"
              "        synchronized (lock) {\n"
              "            return right;\n"
              "        }\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        Pair pair = new Pair(100, 0);\n"
              + _drive30("pair::move")
              + "        System.out.println(pair.left());\n"
                "        System.out.println(pair.right());\n"
                "        System.out.println(pair.left() + pair.right());",
              [_k30p(k, _nl(100 - k, k, 100)) for k in _K30P],
              ["Two `AtomicInteger`s would make each field safe and the PAIR still "
               "broken - a reader could catch the money in mid-air.",
               "The invariant spans both fields, so one lock must cover both.",
               "`pair::move` is a method reference standing in for a Runnable.",
               "`k` threads move 1 each, so left ends at `100 - k` and right at `k`.",
               "The total is 100 in every case, because nothing is created or "
               "destroyed."]),
    ])


# ===========================================================================
# Family E - locks, ordering, and doing without
# ===========================================================================

_P30_E = _jfam(
    "p30-locks", "Explicit locks and lock ordering",
    "`ReentrantLock`, the mandatory `finally`, and the rule that prevents deadlock.",
    """
```java
lock.lock();                            // OUTSIDE the try
try { ... } finally { lock.unlock(); }  // ALWAYS a finally
lock.tryLock();                         // true or false, never blocks
```

`synchronized` releases its lock on every exit for free; an explicit lock does
not, so the `finally` is not optional.

And when two locks are involved, **give them a global order and always take the
lower one first**. Both threads of an A→B / B→A pair then reach for the same
lock first, so the circular wait deadlock needs cannot form.
""",
    [
        _p30s("j30-pe-lock", "lock, try, finally, unlock", "Medium",
              "Read `k` and `m` and drive a shared counter from `k` threads under a "
              "`ReentrantLock`, unlocking in a `finally`. Print `k * m`.",
              "        int k = sc.nextInt();\n"
              "        int m = sc.nextInt();\n"
              "        int[] counter = new int[1];\n"
              "        ReentrantLock lock = new ReentrantLock();\n"
              "        Runnable job = () -> {\n"
              "            for (int i = 0; i < m; i++) {\n"
              "                lock.lock();\n"
              "                try {\n"
              "                    counter[0]++;\n"
              "                } finally {\n"
              "                    lock.unlock();\n"
              "                }\n"
              "            }\n"
              "        };\n"
              + _drive30("job")
              + "        System.out.println(counter[0]);",
              [_km30p(k, m, str(k * m)) for (k, m) in _KM30P],
              ["`lock()` goes before the `try`, not inside it.",
               "If `lock()` itself threw, a finally inside would unlock something you "
               "never held.",
               "The try body is only the critical section.",
               "`finally { lock.unlock(); }` runs on every exit path.",
               "The total is `k * m`."]),

        _p30s("j30-pe-trylock", "Never blocking", "Medium",
              "`tryLock()` returns at once with `true` or `false`. On a free lock it "
              "succeeds; the same thread may take it again because the lock is "
              "reentrant. Print `true`, `true`, the hold count, then the hold count "
              "after both unlocks, then `k`.",
              "        int k = sc.nextInt();\n"
              "        ReentrantLock lock = new ReentrantLock();\n"
              "        System.out.println(lock.tryLock());\n"
              "        try {\n"
              "            System.out.println(lock.tryLock());\n"
              "            try {\n"
              "                System.out.println(lock.getHoldCount());\n"
              "            } finally {\n"
              "                lock.unlock();\n"
              "            }\n"
              "        } finally {\n"
              "            lock.unlock();\n"
              "        }\n"
              "        System.out.println(lock.getHoldCount());\n"
              "        System.out.println(k);",
              [_k30p(k, _nl("true", "true", 2, 0, k)) for k in _K30P],
              ["Nobody holds the lock, so the first `tryLock()` is `true`.",
               "Reentrancy means the same thread taking it again is also `true`.",
               "Every successful acquire needs exactly one `unlock` - hence the nesting.",
               "`getHoldCount()` is 2 in the middle and 0 after both unlocks.",
               "`tryLock` is what makes backing off - and so deadlock recovery - "
               "possible."]),

        _p30c("j30-pe-ordering", "Lower index first", "Hard",
              "`Accounts` transfers between two balances, always locking "
              "`min(from, to)` before `max(from, to)`. Two threads transfer in opposite "
              "directions at once; because both obey the same order, no cycle can form. "
              "Print both balances and the total.",
              "class Accounts {\n"
              "    private final int[] balances;\n"
              "    private final ReentrantLock[] locks;\n\n"
              "    Accounts(int[] balances) {\n"
              "        this.balances = balances;\n"
              "        this.locks = new ReentrantLock[balances.length];\n"
              "        for (int i = 0; i < balances.length; i++) {\n"
              "            this.locks[i] = new ReentrantLock();\n"
              "        }\n"
              "    }\n\n"
              "    void transfer(int from, int to, int amount) {\n"
              "        int first = Math.min(from, to);\n"
              "        int second = Math.max(from, to);\n"
              "        locks[first].lock();\n"
              "        try {\n"
              "            locks[second].lock();\n"
              "            try {\n"
              "                balances[from] -= amount;\n"
              "                balances[to] += amount;\n"
              "            } finally {\n"
              "                locks[second].unlock();\n"
              "            }\n"
              "        } finally {\n"
              "            locks[first].unlock();\n"
              "        }\n"
              "    }\n\n"
              "    int balance(int i) {\n"
              "        return balances[i];\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        Accounts accounts = new Accounts(new int[] {100, 100});\n"
              "        Thread t1 = new Thread(() -> accounts.transfer(0, 1, k), \"t1\");\n"
              "        Thread t2 = new Thread(() -> accounts.transfer(1, 0, k), \"t2\");\n"
              "        t1.start();\n"
              "        t2.start();\n"
              "        t1.join();\n"
              "        t2.join();\n"
              "        System.out.println(accounts.balance(0));\n"
              "        System.out.println(accounts.balance(1));\n"
              "        System.out.println(accounts.balance(0) + accounts.balance(1));",
              [_k30p(k, _nl(100, 100, 200)) for k in _K30P],
              ["Both threads lock account 0 first, whichever way their money is going.",
               "Locking `from` then `to` instead is the deadlock: t1 holds 0 wanting 1, "
               "t2 holds 1 wanting 0.",
               "The two transfers are equal and opposite, so the balances return to "
               "100 and 100.",
               "The total never changes - money is moved, never made.",
               "A global lock order is the one deadlock cure you can apply mechanically."]),

        _p30c("j30-pe-selftransfer", "Transferring to yourself", "Hard",
              "With `min`/`max` ordering, a transfer from an account to itself locks the "
              "SAME lock twice - which works only because `ReentrantLock` is reentrant, "
              "and needs two unlocks. `k` threads each self-transfer 10; the balance is "
              "unchanged. Print it, and the hold count afterwards.",
              "class Accounts {\n"
              "    private final int[] balances;\n"
              "    private final ReentrantLock[] locks;\n\n"
              "    Accounts(int[] balances) {\n"
              "        this.balances = balances;\n"
              "        this.locks = new ReentrantLock[balances.length];\n"
              "        for (int i = 0; i < balances.length; i++) {\n"
              "            this.locks[i] = new ReentrantLock();\n"
              "        }\n"
              "    }\n\n"
              "    void transfer(int from, int to, int amount) {\n"
              "        int first = Math.min(from, to);\n"
              "        int second = Math.max(from, to);\n"
              "        locks[first].lock();\n"
              "        try {\n"
              "            locks[second].lock();\n"
              "            try {\n"
              "                balances[from] -= amount;\n"
              "                balances[to] += amount;\n"
              "            } finally {\n"
              "                locks[second].unlock();\n"
              "            }\n"
              "        } finally {\n"
              "            locks[first].unlock();\n"
              "        }\n"
              "    }\n\n"
              "    int balance(int i) {\n"
              "        return balances[i];\n"
              "    }\n\n"
              "    int holds(int i) {\n"
              "        return locks[i].getHoldCount();\n"
              "    }\n"
              "}",
              "        int k = sc.nextInt();\n"
              "        Accounts accounts = new Accounts(new int[] {50});\n"
              + _drive30("() -> accounts.transfer(0, 0, 10)")
              + "        System.out.println(accounts.balance(0));\n"
                "        System.out.println(accounts.holds(0));",
              [_k30p(k, _nl(50, 0)) for k in _K30P],
              ["When `from` equals `to`, `min` and `max` are the same index.",
               "So `locks[0]` is locked twice by one thread - legal, because the lock is "
               "reentrant.",
               "It is also unlocked twice, which is what keeps the hold count balanced.",
               "A non-reentrant lock would deadlock against itself here, instantly.",
               "The balance is unchanged: minus 10 then plus 10 on the same account."]),

        _p30s("j30-pe-nolock", "The lock you did not need", "Easy",
              "Ranked best first: do not share. `k` threads each compute `idx * idx` "
              "into their own slot, with no lock, no atomic and no volatile. Print each "
              "slot and the total.",
              "        int k = sc.nextInt();\n"
              "        int[] parts = new int[k];\n"
              "        Thread[] workers = new Thread[k];\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            final int idx = i;\n"
              "            workers[i] = new Thread(() -> parts[idx] = idx * idx, \"w\" + idx);\n"
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
              [_k30p(k, _nl(*([f"{i} {i * i}" for i in range(k)]
                              + [sum(i * i for i in range(k))]))) for k in _K30P],
              ["No two threads write the same slot, so there is nothing to guard.",
               "The joins publish every write before main reads it.",
               "Main aggregates single-threaded.",
               "This has the fewest moving parts of anything in the module, and is the "
               "fastest.",
               "Reach for a lock only when confinement and immutability genuinely do not "
               "fit."]),
    ])


_PRACTICE[30] = [_P30_A, _P30_B, _P30_C, _P30_D, _P30_E]
