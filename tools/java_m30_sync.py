# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 30 - Shared state: races, locks and visibility.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# `synchronized`, `volatile`, the atomics and `ReentrantLock` become legal here
# and nowhere earlier. Module 29 kept every worker on its own slot with a join
# between the write and the read - deliberately, so that this module has the
# thing it needs to fix: two threads reaching for one variable.
#
# DELIBERATELY NOT HERE: `ExecutorService`, `Callable`, `Future` and the
# concurrent collections are module 31.
#
# THE JUDGING PROBLEM, AND HOW THIS MODULE SOLVES IT
# --------------------------------------------------
# A data race is by definition something that MIGHT go wrong, and every exercise
# in this course is graded by exact stdout comparison. A judged program whose
# output depends on the scheduler would be a broken test, so this module never
# ships one. Two techniques, and they cover every program here:
#
#   1. THE FIXED CODE IS DETERMINISTIC ANYWAY. A correctly synchronised counter
#      incremented k*m times prints exactly k*m, every run, on every machine.
#      Most exercises here are simply that: the right answer, guaranteed. The
#      `fix` exercises pair that with an unsynchronised starter driven hard
#      enough (tens of thousands of increments per thread) that losing at least
#      one update is a certainty in practice - which is all `--starters`
#      requires, since a starter only has to FAIL.
#
#   2. WHERE THE LOST UPDATE ITSELF IS THE ANSWER, THE INTERLEAVING IS STAGED
#      WITH JOINS. One thread reads the counter and stops; other threads then
#      increment it, each fully joined; finally the first thread writes back the
#      value it read. Every step is ordered by a join, so the output is fixed -
#      and the program still shows a real lost update performed by real threads.
#
# An EARLIER DRAFT of this module widened the race window with a 40ms sleep
# between the read and the write, on the theory that every thread would read
# before any wrote. It is written down here because it failed: the verifier runs
# exercises in parallel, thread start-up on a loaded machine can exceed 40ms,
# and cases at k=2, 4 and 5 all came out as 2 instead of 1. Any timing-based
# determinism is a flaky test waiting to happen. Hence the joins.
#
# DEADLOCK is taught in prose, in a warm-up and in the review quiz, but is never
# a judged program: a deadlocked starter would be "correctly" failing by hanging
# until the 20-second timeout, which would make the test suite slow for no
# teaching gain.
# ---------------------------------------------------------------------------

_M30 = []

_IMPORTS30 = ("import java.util.*;\n"
              "import java.util.concurrent.atomic.*;\n"
              "import java.util.concurrent.locks.*;\n")

_SIG30 = "    public static void main(String[] args) throws InterruptedException {"


def _j30s(body):
    """A Scanner-opening main that may join or sleep."""
    return _jcls(
        _SIG30 + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }",
        imports=_IMPORTS30,
    )


def _j30write(eid, title, difficulty, prompt, body, tests, hints, types=None):
    """A challenge whose PROMPT quotes the broken code, instead of a `fix` whose
    starter is the broken code.

    Every "here is an unsynchronised counter, repair it" exercise wants to be a
    `_jfix`. None of them can be. `verify_java_course.py --starters` requires a
    buggy starter to FAIL, and an unsynchronised counter is only PROBABLY wrong:
    driving `k` threads through 50,000 increments each loses an update on
    essentially every run - until the machine is busy enough that the threads
    stop overlapping and the answer comes out exactly right. That is not a
    hypothetical either. `j30-atom-compose` shipped as a `_jfix` and its starter
    PASSED a full-course run, because the verifier checks exercises in parallel
    and the two threads were never in flight at once.

    A test that depends on a race actually happening is precisely the bug this
    module teaches people to fear, so the module does not contain one. The
    broken version is quoted and dissected in the prompt, and the learner writes
    the correct one - which is deterministic, being correct.

    Module 31 keeps two real `_jfix` exercises, because both of those bugs are
    deterministic: `execute` where a value is wanted does not compile, and a
    pool that is never shut down always hangs."""
    return _jch(eid, title, difficulty, prompt,
                _j30t(types, body) if types else _j30s(body),
                body.rstrip("\n"), tests, hints)


def _j30h(helpers, body):
    """Static helper METHODS beside main - for the lock-ordering exercise, where
    the ordering rule belongs in one place both callers share."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _SIG30 + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }",
        imports=_IMPORTS30,
    )


def _j30t(types, body):
    """Helper CLASSES above Main, then a Scanner-opening main."""
    return _jp(
        _IMPORTS30 + "\n"
        + types.rstrip("\n") + "\n\n"
        + "public class Main {\n"
        + _SIG30 + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n    }\n}"
    )


# The catch every lambda needs, since `run()` may not declare a checked
# exception. Restoring the flag is the habit module 29 established.
_CATCH30 = ("            } catch (InterruptedException e) {\n"
            "                Thread.currentThread().interrupt();\n"
            "            }\n")

_K30 = (2, 3, 4, 5, 2)          # thread counts
_KM30 = ((2, 500), (3, 400), (4, 250), (5, 200), (2, 1000))

# For `fix` exercises, where the BUGGY starter must reliably fail. An
# unsynchronised counter driven this hard loses updates on every run in
# practice; the fixed version prints k*m exactly. Still cheap: a few hundred
# thousand lock acquisitions is milliseconds.
_KMBIG30 = ((2, 50000), (3, 40000), (4, 25000), (5, 20000), (2, 100000))

# Shared by the two visibility exercises: a counter whose field really is
# volatile, so the lesson is that visibility was never the missing guarantee.
_VOLATILE_COUNTER30 = (
    "class Counter {\n"
    "    private volatile int value;\n\n"
    "    int get() {\n"
    "        return value;\n"
    "    }\n\n"
    "    void set(int v) {\n"
    "        value = v;\n"
    "    }\n"
    "}"
)


def _k30(k, out):
    return _case(str(k), out)


def _km30(k, m, out):
    return _case(f"{k} {m}", out)


# ===========================================================================
# 30.1 The lost update
# ===========================================================================

_M30.append(_jlesson(
    "m30-race", "The lost update",
    "`count++` is three operations, not one - and that is the whole problem.",
    """
Module 29 was careful never to let two threads touch the same variable. Here is
what happens when they do.

```java
count++;
```

One character of syntax, three separate machine operations:

1. **read** `count` into a register;
2. **add** one to the register;
3. **write** the register back to `count`.

Nothing stops another thread running between any two of those steps. So with
`count` at 0 and two threads incrementing:

| | thread A | thread B | `count` |
|---|---|---|---|
| 1 | reads 0 | | 0 |
| 2 | | reads 0 | 0 |
| 3 | writes 1 | | 1 |
| 4 | | writes 1 | **1** |

Two increments, one result. That is a **lost update**, and it is the canonical
**race condition**: the program's correctness depends on the order two threads
happened to be scheduled in.

## Making it reproducible

A real race is hard to see, because the window between the read and the write is
a few nanoseconds wide. It fails once in ten million increments - which means it
fails in production and never on your laptop. For teaching, we can prise the
window open:

```java
int seen = counter[0];
Thread.sleep(40);              // <- widen the window ON PURPOSE
counter[0] = seen + 1;
```

Now every thread reads before any thread writes, so `k` threads reliably produce
**1**. Every exercise in this lesson uses that trick, and it is worth being
clear about why: **the sleep does not cause the bug, it only makes it certain.**
Take the sleep out and the bug is still there - just rare enough to survive code
review, testing, and six months of production.

## The other shape: check-then-act

Lost updates are one family. The other is **check-then-act**, where a decision
is made on information that is stale by the time it is used:

```java
if (list.isEmpty()) {      // check
    list.add(x);           // ...act. Another thread may have added between the two.
}
```

Both families have the same cause and the same cure: the sequence has to be
**atomic** - indivisible from every other thread's point of view. The rest of
this module is four ways to buy that.
""",
    warmup=[
        _jq("`count++` from two threads with no synchronisation can lose an update because…",
            ["it is a read, an add and a write, and another thread can run in between",
             "`++` is not supported on shared fields",
             "the JVM reorders it",
             "int is too small"],
            0,
            "Three steps, and nothing makes them indivisible."),
        _jq("Adding a `sleep` between the read and the write…",
            ["makes an existing race reproducible - it does not create one",
             "creates the race", "fixes the race",
             "has no effect on the outcome"],
            0,
            "The bug is there either way; the sleep only widens the window."),
    ],
    exercises=[
        _jch("j30-race-lost", "A lost update, staged", "Medium",
             "The interleaving from the table above, performed by real threads with the "
             "steps pinned down by joins so you can watch it. A reader thread reads the "
             "counter and stops. Then `k` threads each increment it properly, one after "
             "another - print the count, which is `k`. Finally the reader wakes up and "
             "writes back the value it read plus one, throwing all `k` increments away - "
             "print the count again, which is `1`. Replace `____` with the three phases.",
             _j30s("        int k = sc.nextInt();\n"
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
                   "        System.out.println(counter[0]);"),
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
             "        writer.join();",
             [_k30(k, _nl(k, 1)) for k in _K30],
             hints=["Phase one: one thread copies `counter[0]` into `stale[0]` and ends. "
                    "It has now done the READ half of a read-modify-write.",
                    "Phase two: `k` threads each do a complete increment, started and "
                    "joined one at a time, so the count climbs cleanly to `k`.",
                    "Phase three: the original reader's WRITE finally lands - "
                    "`counter[0] = stale[0] + 1`, which is `0 + 1`.",
                    "Every step is separated by a join, so this prints the same thing "
                    "every run.",
                    "In real code these three phases are nanoseconds apart and nobody "
                    "arranges them - the JVM does, at random.",
                    "`k` increments, and the final count is 1. That is what a lost update "
                    "costs."]),

        _j30write("j30-race-fixed", "…and the same bug, at full speed", "Medium",
              "No staging this time. Written the obvious way -\n\n"
              "```java\n"
              "Runnable job = () -> {\n"
              "    for (int i = 0; i < m; i++) {\n"
              "        counter[0]++;              // read, add, write\n"
              "    }\n"
              "};\n"
              "```\n\n"
              "- `k` threads race on `counter[0]` with a window nanoseconds wide, and the "
              "total lands somewhere under `k * m`. Write the version that puts the "
              "increment inside a `synchronized` block on the shared `lock`, so the "
              "answer is exactly `k * m`. Replace `____` with the whole body.",
              ("        int k = sc.nextInt();\n"
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
                    "        Thread[] workers = new Thread[k];\n"
                    "        for (int i = 0; i < k; i++) {\n"
                    "            workers[i] = new Thread(job, \"w\" + i);\n"
                    "            workers[i].start();\n"
                    "        }\n"
                    "        for (Thread w : workers) {\n"
                    "            w.join();\n"
                    "        }\n"
                    "        System.out.println(counter[0]);"),
              [_km30(k, m, str(k * m)) for (k, m) in _KMBIG30],
              ["`counter[0]++` is the read-modify-write. It needs to be indivisible.",
               "`synchronized (lock) { counter[0]++; }`, with the loop left outside.",
               "Every thread locks the same `lock` object - that is what makes them "
               "take turns.",
               "Locking inside the loop rather than around it keeps the critical "
               "section as small as possible.",
               "Note how much harder the broken version is to SEE than the staged one: "
               "no sleep, no arrangement, and a wrong answer that is merely a bit too "
               "small.",
               "It is also, maddeningly, not wrong every time - on a busy machine the "
               "threads may not overlap at all and the total comes out right.",
               "With the lock in place it is exactly `k * m`, on every run and every "
               "machine."]),

        _jch("j30-race-checkthenact", "Check, then act", "Hard",
             "The other shape of race, written correctly. Read `k`; each thread claims "
             "the slot by writing its own index plus one, but only if the slot is still "
             "0 - with a pause sitting between the check and the act, which is exactly "
             "where another thread would slip in. Write the check and the act as ONE "
             "synchronized region so the pair cannot be split. The threads are run "
             "strictly one at a time here, so thread 0 always claims it and the answer "
             "is always 1. Replace `____` with the guarded region.",
             _j30s("        int k = sc.nextInt();\n"
                   "        int[] slot = new int[1];\n"
                   "        Object lock = new Object();\n"
                   "        Thread[] workers = new Thread[k];\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int idx = i;\n"
                   "            workers[i] = new Thread(() -> {\n"
                   "                synchronized (lock) {\n"
                   "                    if (slot[0] == 0) {\n"
                   "                        try {\n"
                   "                            Thread.sleep(20);\n"
                   "                        } catch (InterruptedException e) {\n"
                   "                            Thread.currentThread().interrupt();\n"
                   "                        }\n"
                   "                        slot[0] = idx + 1;\n"
                   "                    }\n"
                   "                }\n"
                   "            }, \"w\" + idx);\n"
                   "            workers[i].start();\n"
                   "            workers[i].join();\n"
                   "        }\n"
                   "        System.out.println(slot[0]);"),
             "                synchronized (lock) {\n"
             "                    if (slot[0] == 0) {\n"
             "                        try {\n"
             "                            Thread.sleep(20);\n"
             "                        } catch (InterruptedException e) {\n"
             "                            Thread.currentThread().interrupt();\n"
             "                        }\n"
             "                        slot[0] = idx + 1;\n"
             "                    }\n"
             "                }",
             [_k30(k, "1") for k in _K30],
             hints=["The `if` and the assignment must be inside ONE synchronised block.",
                    "Guarding only the assignment would leave the check outside, which is "
                    "exactly the bug - even though this particular arrangement would "
                    "still print 1.",
                    "The threads are started and joined one at a time here, so thread 0 "
                    "always claims the slot first - which is what makes the answer "
                    "testable at all.",
                    "Every later thread finds a non-zero slot and does nothing.",
                    "So the answer is always 1, whatever `k` is.",
                    "Check-then-act is why `Map` has `putIfAbsent` - one atomic operation "
                    "instead of two racing ones."]),

        _jch("j30-race-safeslots", "The race you can design away", "Easy",
             "Not every shared counter needs a lock - sometimes it needs to not be "
             "shared. Read `k` and have thread `i` write `i + 1` into `parts[i]`, then "
             "let MAIN add the slots up after joining. No two threads touch the same "
             "memory, so there is nothing to synchronise. Replace `____` with the start "
             "and join loops.",
             _j30s("        int k = sc.nextInt();\n"
                   "        int[] parts = new int[k];\n"
                   "        Thread[] workers = new Thread[k];\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            final int idx = i;\n"
                   "            workers[i] = new Thread(() -> parts[idx] = idx + 1, \"w\" + idx);\n"
                   "            workers[i].start();\n"
                   "        }\n"
                   "        for (Thread w : workers) {\n"
                   "            w.join();\n"
                   "        }\n"
                   "        int total = 0;\n"
                   "        for (int p : parts) {\n"
                   "            total += p;\n"
                   "        }\n"
                   "        System.out.println(total);"),
             "        for (int i = 0; i < k; i++) {\n"
             "            final int idx = i;\n"
             "            workers[i] = new Thread(() -> parts[idx] = idx + 1, \"w\" + idx);\n"
             "            workers[i].start();\n"
             "        }\n"
             "        for (Thread w : workers) {\n"
             "            w.join();\n"
             "        }",
             [_k30(k, str(k * (k + 1) // 2)) for k in _K30],
             hints=["This is module 29's pattern, and it is still the best answer when it "
                    "fits.",
                    "Different threads write different slots, so no two writes ever "
                    "collide.",
                    "The joins publish every slot before main reads any of them.",
                    "Main does the summing, single-threaded - one thread cannot race with "
                    "itself.",
                    "The total is 1 + 2 + ... + k.",
                    "The fastest lock is the one you designed out of existence."]),
    ],
    quiz=[
        _jq("A race condition is…",
            ["a program whose correctness depends on the order threads happen to run in",
             "any program using threads",
             "a program that is slow",
             "two threads reading the same variable"],
            0,
            "Two readers are fine. It takes a write to make a race."),
        _jq("`if (map.get(k) == null) map.put(k, v);` from two threads is…",
            ["a check-then-act race - both can pass the check",
             "safe, because get and put are each atomic",
             "safe if the map is a HashMap",
             "a lost update"],
            0,
            "Each call is atomic; the SEQUENCE is not. That is what putIfAbsent is for."),
    ],
))


# ===========================================================================
# 30.2 synchronized
# ===========================================================================

_M30.append(_jlesson(
    "m30-sync", "`synchronized`, and the lock you did not know you had",
    "Every object carries a lock. `synchronized` is how you take it.",
    """
**Every Java object has a lock** - a *monitor*, or *intrinsic lock* - whether
you ever use it or not. `synchronized` acquires it on entry and releases it on
exit, including when the block exits by throwing.

Two forms.

**A synchronized block** names the object explicitly:

```java
synchronized (lock) {
    counter++;
}
```

**A synchronized method** is shorthand. On an instance method the lock is
`this`; on a `static` method it is the **`Class` object**, which is a different
lock entirely:

```java
synchronized void add() { ... }          // locks `this`
static synchronized void tally() { ... } // locks Counter.class - NOT this
```

That difference is a favourite exam question: a `static synchronized` method and
an instance `synchronized` method on the same class **do not exclude each
other**, because they are taking two different locks.

## Mutual exclusion is per lock, not per block

Threads take turns only if they are locking **the same object**. This is the
most common way `synchronized` gets written and still fails to protect
anything:

```java
Runnable job = () -> {
    Object lock = new Object();      // a NEW lock per execution
    synchronized (lock) { count++; } // ...so nobody ever waits. Useless.
};
```

The lock must be shared exactly as widely as the data it guards.

## Which object to lock

Locking `this` is the default because it is what a synchronized method does, but
it is public: any other code holding a reference to your object can lock it too,
and now your class's correctness depends on strangers. The safer habit is a
private lock nobody else can name:

```java
private final Object lock = new Object();
```

`final`, so it cannot be reassigned out from under a thread that is waiting.

## Reentrancy

Intrinsic locks are **reentrant**: a thread that already holds a lock can take
it again without blocking on itself.

```java
synchronized void outer() { inner(); }   // both lock `this`
synchronized void inner() { ... }        // fine - same thread, same lock
```

Without that, a synchronized method calling another synchronized method on the
same object would deadlock instantly - which is to say, inheritance would not
work.

## Keep the critical section small

Everything inside the block is serialised, so it is the part of your program
that does not get faster with more cores. Do the reading, the parsing and the
formatting outside; hold the lock only across the actual shared update. And
never hold a lock while sleeping or doing I/O - the exercises in lesson 1 do it
only so you can watch the effect.
""",
    warmup=[
        _jq("A `static synchronized` method and an instance `synchronized` method…",
            ["take DIFFERENT locks - the Class object and `this` - so they do not exclude each other",
             "take the same lock", "cannot both exist", "always deadlock"],
            0,
            "One of the most-missed details in the whole topic."),
        _jq("`synchronized` on a lock object created INSIDE the runnable…",
            ["protects nothing - each execution gets its own lock, so nobody ever waits",
             "works normally", "is a compile error", "is faster"],
            0,
            "The lock must be shared as widely as the data it guards."),
    ],
    exercises=[
        _jch("j30-sync-block", "Taking turns", "Medium",
             "Read `k` and `m`. Run `k` threads, each incrementing a shared slot `m` "
             "times inside a `synchronized` block on the shared `lock`. Join them all and "
             "print the total, which is exactly `k * m`. Replace `____` with the "
             "Runnable's body.",
             _j30s("        int k = sc.nextInt();\n"
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
                   "        Thread[] workers = new Thread[k];\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            workers[i] = new Thread(job, \"w\" + i);\n"
                   "            workers[i].start();\n"
                   "        }\n"
                   "        for (Thread w : workers) {\n"
                   "            w.join();\n"
                   "        }\n"
                   "        System.out.println(counter[0]);"),
             "            for (int i = 0; i < m; i++) {\n"
             "                synchronized (lock) {\n"
             "                    counter[0]++;\n"
             "                }\n"
             "            }",
             [_km30(k, m, str(k * m)) for (k, m) in _KM30],
             hints=["The loop goes outside the synchronized block, not inside it.",
                    "Locking once per increment keeps the critical section as small as it "
                    "can be.",
                    "Every thread locks the same `lock` object - that is what makes them "
                    "take turns.",
                    "`counter[0]++` is the read-modify-write the lock is protecting.",
                    "With the lock in place the answer is exactly `k * m`, on every run.",
                    "Without it, this is the lesson-1 race - just too fast to see."]),

        _jch("j30-sync-method", "A synchronized method", "Medium",
             "`Tally` keeps a private count and exposes `add()` and `get()`. Make `add` "
             "`synchronized` so it locks the Tally instance. Read `k` and `m`, have `k` "
             "threads call `add()` `m` times each, and print the total after joining. "
             "Replace `____` with the two methods.",
             _j30t("class Tally {\n"
                   "    private int count;\n\n"
                   "    synchronized void add() {\n"
                   "        count++;\n"
                   "    }\n\n"
                   "    synchronized int get() {\n"
                   "        return count;\n"
                   "    }\n"
                   "}",
                   "        int k = sc.nextInt();\n"
                   "        int m = sc.nextInt();\n"
                   "        Tally tally = new Tally();\n"
                   "        Thread[] workers = new Thread[k];\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            workers[i] = new Thread(() -> {\n"
                   "                for (int j = 0; j < m; j++) {\n"
                   "                    tally.add();\n"
                   "                }\n"
                   "            }, \"w\" + i);\n"
                   "            workers[i].start();\n"
                   "        }\n"
                   "        for (Thread w : workers) {\n"
                   "            w.join();\n"
                   "        }\n"
                   "        System.out.println(tally.get());"),
             "    synchronized void add() {\n"
             "        count++;\n"
             "    }\n\n"
             "    synchronized int get() {\n"
             "        return count;\n"
             "    }",
             [_km30(k, m, str(k * m)) for (k, m) in _KM30],
             hints=["`synchronized` goes in the modifier list, like `public` or `static`.",
                    "On an instance method the lock is `this` - here, the one shared "
                    "`Tally`.",
                    "`get()` is synchronized too: reading an int is atomic, but that is "
                    "not the same as seeing the LATEST value.",
                    "All `k` threads share one `Tally`, so they share one lock.",
                    "This is module 12's encapsulation doing real work - the field is "
                    "private, so the lock cannot be bypassed.",
                    "The total is `k * m`."]),

        _j30write("j30-sync-perthread", "The lock that protects nothing", "Hard",
              "This looks synchronised and protects nothing:\n\n"
              "```java\n"
              "Runnable job = () -> {\n"
              "    Object lock = new Object();     // a NEW lock, once per THREAD\n"
              "    for (int i = 0; i < m; i++) {\n"
              "        synchronized (lock) { counter[0]++; }   // nobody ever waits\n"
              "    }\n"
              "};\n"
              "```\n\n"
              "`k` threads take `k` different locks, so the `synchronized` is pure "
              "decoration and the total lands under `k * m`. Write it with the lock "
              "declared OUTSIDE the Runnable, so all `k` threads capture and take the "
              "same one. Replace `____` with the whole body.",
              ("        int k = sc.nextInt();\n"
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
                    "        Thread[] workers = new Thread[k];\n"
                    "        for (int i = 0; i < k; i++) {\n"
                    "            workers[i] = new Thread(job, \"w\" + i);\n"
                    "            workers[i].start();\n"
                    "        }\n"
                    "        for (Thread w : workers) {\n"
                    "            w.join();\n"
                    "        }\n"
                    "        System.out.println(counter[0]);"),
              [_km30(k, m, str(k * m)) for (k, m) in _KMBIG30],
              ["Ask what object each thread is actually locking.",
               "`new Object()` inside the lambda runs once per THREAD - so there are "
               "`k` locks, not one.",
               "A lock only one thread is interested in never makes anybody wait.",
               "Declare the lock beside the data it guards, above the Runnable.",
               "Then the lambda captures it, and all `k` threads take the same one.",
               "The broken version compiles, reads as thread-safe, and is not - which is "
               "exactly why it is worth recognising on sight."]),

        _jch("j30-sync-static", "Two locks, not one", "Hard",
             "`Registry` has a `static synchronized` method locking `Registry.class` and "
             "an instance `synchronized` method locking `this`. They are different locks, "
             "so they never exclude each other - the program is only safe because each "
             "counter is guarded consistently by ONE of them. Read `k` and `m`, drive "
             "both counters from `k` threads, and print the static total then the "
             "instance total. Replace `____` with the loop body.",
             _j30t("class Registry {\n"
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
                   "        Thread[] workers = new Thread[k];\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            workers[i] = new Thread(() -> {\n"
                   "                for (int j = 0; j < m; j++) {\n"
                   "                    Registry.bumpGlobal();\n"
                   "                    registry.bumpLocal();\n"
                   "                }\n"
                   "            }, \"w\" + i);\n"
                   "            workers[i].start();\n"
                   "        }\n"
                   "        for (Thread w : workers) {\n"
                   "            w.join();\n"
                   "        }\n"
                   "        System.out.println(Registry.global());\n"
                   "        System.out.println(registry.local());"),
             "                for (int j = 0; j < m; j++) {\n"
             "                    Registry.bumpGlobal();\n"
             "                    registry.bumpLocal();\n"
             "                }",
             [_km30(k, m, _nl(k * m, k * m)) for (k, m) in _KM30],
             hints=["`Registry.bumpGlobal()` is static - call it on the class.",
                    "`registry.bumpLocal()` is an instance method on the shared object.",
                    "The two methods take different locks, so a thread in one does not "
                    "block a thread in the other.",
                    "That is safe HERE only because each field is always guarded by the "
                    "same lock as itself.",
                    "A field touched by both a static and an instance synchronized method "
                    "would be unprotected.",
                    "Both totals come out as `k * m`."]),
    ],
    quiz=[
        _jq("`synchronized` releases the lock…",
            ["on every exit from the block, including one caused by an exception",
             "only on a normal exit", "when you call unlock()",
             "when the thread ends"],
            0,
            "Which is one thing it gives you free over a manual lock."),
        _jq("Intrinsic locks are reentrant, meaning…",
            ["a thread already holding the lock can acquire it again without blocking",
             "two threads may hold it at once", "it can be unlocked twice",
             "it works across processes"],
            0,
            "Without it, one synchronized method calling another would self-deadlock."),
    ],
))


# ===========================================================================
# 30.3 Visibility and volatile
# ===========================================================================

_M30.append(_jlesson(
    "m30-visibility", "Visibility, and `volatile`",
    "The second half of the problem: not 'two threads collided', but 'one thread never "
    "found out'.",
    """
Everything so far has been about **atomicity** - operations getting interleaved.
There is a second, quieter failure, and it bites even when only one thread
writes.

```java
boolean running = true;          // written by main

// worker:
while (running) { }              // may loop FOREVER, even after main sets it false
System.out.println("stopped");
```

Nothing here is interleaved. The worker simply never sees the write. Legally.

**Why.** Between your source and the hardware sit a compiler that reorders and a
CPU with per-core caches. A thread is entitled to keep `running` in a register
and never re-read it, because within *that thread* nothing changes it. The Java
Memory Model only guarantees one thread sees another's write when the two are
connected by a **happens-before** relationship - and an ordinary field read
creates none.

You have already been using two of those relationships:

* everything a thread does before `start()` is visible to the new thread;
* everything a thread does before it ends is visible to whoever `join()`s it.

That is exactly why module 29's programs were correct without a single lock.

## `volatile`

```java
volatile boolean running = true;
```

`volatile` says: every read comes from main memory, every write goes to main
memory, and neither may be reordered across the other. The stop-flag loop above
now terminates.

**What `volatile` is not.** It gives you **visibility, not atomicity**:

```java
volatile int count;
count++;        // STILL A RACE. Read, add, write - three operations.
```

`volatile` makes each read and each write indivisible and visible. It does
nothing whatever about a sequence of them. So:

* **one writer, many readers, and the new value does not depend on the old** -
  `volatile` is exactly right, and cheaper than a lock;
* **anything read-modify-write** - you need a lock or an atomic.

The stop flag is the canonical fit: main writes `false`, workers read it, and
the new value does not depend on the old one.

**A `long` or `double`** has one extra wrinkle: without `volatile`, a 64-bit
write is permitted to be split into two 32-bit halves, so another thread can see
a value that was never written. Declaring it `volatile` (or guarding it) fixes
that too.
""",
    warmup=[
        _jq("A worker looping on a non-volatile `boolean running` may…",
            ["never see the write and loop forever - legally",
             "always see it, just late", "throw an exception",
             "see it only on one core"],
            0,
            "Without happens-before, the JVM may keep it in a register."),
        _jq("`volatile int count; count++;` is…",
            ["still a race - volatile gives visibility, not atomicity",
             "safe", "safe if only two threads", "a compile error"],
            0,
            "Read-modify-write needs a lock or an atomic."),
    ],
    exercises=[
        _jch("j30-vis-stopflag", "The stop flag", "Medium",
             "`Flag` holds a `volatile boolean`. Start a worker that spins until the flag "
             "goes false and then prints `stopped`; main sleeps briefly, lowers the flag, "
             "joins, and prints `n`. The `volatile` is what guarantees the worker ever "
             "notices. Replace `____` with the worker's creation and start.",
             _j30t("class Flag {\n"
                   "    private volatile boolean running = true;\n\n"
                   "    boolean isRunning() {\n"
                   "        return running;\n"
                   "    }\n\n"
                   "    void stop() {\n"
                   "        running = false;\n"
                   "    }\n"
                   "}",
                   "        int n = sc.nextInt();\n"
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
                   "        System.out.println(n);"),
             "        Thread worker = new Thread(() -> {\n"
             "            while (flag.isRunning()) {\n"
             "                // spin until main lowers the flag\n"
             "            }\n"
             "            System.out.println(\"stopped\");\n"
             "        }, \"worker\");\n"
             "        worker.start();",
             [_k30(n, _nl("stopped", n)) for n in _K30],
             hints=["The worker's loop condition has to re-read the flag every pass.",
                    "It prints only after the loop ends, so `stopped` comes before main's "
                    "number.",
                    "Main sleeps to let the worker get into its loop, then calls `stop()`.",
                    "`volatile` is why the worker's next read sees `false` rather than a "
                    "cached `true`.",
                    "Without it this program is allowed to hang forever - and on a "
                    "server JVM it often does.",
                    "A spin loop like this burns a whole core; real code waits rather than "
                    "spins, which is module 31's business."]),

        _jch("j30-vis-notatomic", "Visible, and still wrong", "Hard",
             "`Counter` holds a `volatile int`, so every read really does return the "
             "freshest value - and the lost update happens anyway, because the gap is "
             "between the read and the write. The same staged interleaving as lesson 1, "
             "on a volatile field: a reader reads and stops, `k` threads increment "
             "cleanly (print the count - it is `k`), then the reader's stale write lands "
             "(print it again - it is `1`). Replace `____` with the three phases.",
             _j30t("class Counter {\n"
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
                   "        System.out.println(counter.get());"),
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
             "        writer.join();",
             [_k30(k, _nl(k, 1)) for k in _K30],
             hints=["Every read here really does return the newest value - volatile "
                    "guarantees that much, and it is not enough.",
                    "The problem is the gap BETWEEN the `get` and the `set`, which "
                    "volatile says nothing about.",
                    "The reader thread performs the READ half and then ends, holding the "
                    "stale 0 in `stale[0]`.",
                    "The `k` bump threads then each do a complete get-then-set, joined one "
                    "at a time, so the count climbs to `k`.",
                    "The writer thread finally completes the reader's WRITE half, setting "
                    "the count to `0 + 1`.",
                    "'I made it volatile' is the most common wrong answer to 'how did you "
                    "make it thread-safe?'"]),

        _jch("j30-vis-publish", "Publishing safely with `start` and `join`", "Medium",
             "Module 29's programs had no `volatile` and were still correct, because "
             "`start()` and `join()` create happens-before edges. Fill an array on main, "
             "start a worker that sums it, join, and print - every write is visible to "
             "the worker, and its write is visible back to main. Replace `____` with the "
             "worker and the join.",
             _j30s("        int n = sc.nextInt();\n"
                   "        int[] data = new int[n];\n"
                   "        for (int i = 0; i < n; i++) {\n"
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
                   "        System.out.println(out[0]);"),
             "        Thread worker = new Thread(() -> {\n"
             "            int sum = 0;\n"
             "            for (int v : data) {\n"
             "                sum += v;\n"
             "            }\n"
             "            out[0] = sum;\n"
             "        }, \"worker\");\n"
             "        worker.start();\n"
             "        worker.join();",
             [_k30(k, str(k * (k + 1) // 2)) for k in _K30],
             hints=["Everything main did BEFORE `start()` is visible to the new thread.",
                    "Everything the worker did before ending is visible after `join()`.",
                    "So neither the array nor the result slot needs `volatile`.",
                    "Only one thread touches each piece of data at a time - the handoffs "
                    "are the start and the join.",
                    "The sum of 1..n is the triangular number.",
                    "Remove the join and you lose both the waiting and the visibility."]),

        _j30write("j30-vis-notenough", "The `volatile` that was not enough", "Medium",
              "`Counter.value` is already `volatile`, and this still loses updates:\n\n"
              "```java\n"
              "for (int i = 0; i < m; i++) {\n"
              "    counter.set(counter.get() + 1);   // freshest possible read...\n"
              "}                                     // ...and a wide-open gap after it\n"
              "```\n\n"
              "Every read really does return the newest value - `volatile` delivers "
              "exactly what it promises, and it was never the missing piece. Write the "
              "version that makes the whole read-modify-write indivisible with a "
              "`synchronized` block on the `lock` already declared. Replace `____` with "
              "the whole body.",
              ("        int k = sc.nextInt();\n"
                    "        int m = sc.nextInt();\n"
                    "        Counter counter = new Counter();\n"
                    "        Object lock = new Object();\n"
                    "        Runnable job = () -> {\n"
                    "            for (int i = 0; i < m; i++) {\n"
                    "                synchronized (lock) {\n"
                    "                    counter.set(counter.get() + 1);\n"
                    "                }\n"
                    "            }\n"
                    "        };\n"
                    "        Thread[] workers = new Thread[k];\n"
                    "        for (int i = 0; i < k; i++) {\n"
                    "            workers[i] = new Thread(job, \"w\" + i);\n"
                    "            workers[i].start();\n"
                    "        }\n"
                    "        for (Thread w : workers) {\n"
                    "            w.join();\n"
                    "        }\n"
                    "        System.out.println(counter.get());"),
              [_km30(k, m, str(k * m)) for (k, m) in _KMBIG30],
              ["Do not remove the `volatile` - it is not wrong, it is just not the "
               "guarantee this code needed.",
               "The gap is between `get()` and `set()`, and no field modifier can "
               "close it.",
               "Wrap the whole `counter.set(counter.get() + 1)` in "
               "`synchronized (lock) { ... }`.",
               "Every thread locks the same `lock`, so they take turns and each "
               "reads what the last one wrote.",
               "With the lock in place the `volatile` is now redundant - a lock "
               "already gives visibility as well as exclusion.",
               "'I made the field volatile' is the most common wrong answer to 'how "
               "did you make this thread-safe?'"],
              types=_VOLATILE_COUNTER30),
    ],
    quiz=[
        _jq("`volatile` guarantees…",
            ["visibility and ordering, but not atomicity of read-modify-write",
             "atomicity of ++", "mutual exclusion", "that writes never reorder anywhere"],
            0,
            "One writer, and a value that does not depend on the old one."),
        _jq("Module 29's programs needed no volatile because…",
            ["`start()` and `join()` create happens-before edges that publish the writes",
             "ints are always visible", "they used arrays",
             "they only used one core"],
            0,
            "That is precisely what join buys you beyond waiting."),
    ],
))


# ===========================================================================
# 30.4 Atomics
# ===========================================================================

_M30.append(_jlesson(
    "m30-atomics", "Atomics, and compare-and-set",
    "A read-modify-write that cannot be interrupted - without a lock.",
    """
`java.util.concurrent.atomic` gives you variables whose read-modify-write is a
single indivisible operation:

```java
AtomicInteger count = new AtomicInteger(0);

count.incrementAndGet();     // ++count  - returns the NEW value
count.getAndIncrement();     // count++  - returns the OLD value
count.addAndGet(5);          // += 5, returns the new value
count.get();                 // the current value
count.set(7);                // plain write
```

The method names carry the whole distinction that `++` hides: `getAndIncrement`
returns what it was, `incrementAndGet` returns what it became.

## How, without a lock

Underneath is one CPU instruction - **compare-and-set**:

```java
count.compareAndSet(expected, newValue);   // true if it swapped, false if it did not
```

"If the value is still `expected`, make it `newValue`, and tell me whether you
did" - atomically, in hardware. `incrementAndGet` is a loop around it:

```java
int old;
do {
    old = count.get();
} while (!count.compareAndSet(old, old + 1));   // retry if someone beat us
```

Nobody ever blocks. A thread that loses the race just tries again, which is why
this is called **lock-free**. Under light contention it is faster than a lock;
under heavy contention the retries add up and a lock can win.

## `AtomicInteger` is not a thread-safe `int`

The atomic operations are the *methods*. Compose two of them and you are racing
again:

```java
count.set(count.get() + 1);        // TWO operations. Exactly the lesson-1 race.
if (count.get() == 0) count.set(1); // check-then-act, again
```

Use `incrementAndGet`, or `compareAndSet` in a retry loop, or `updateAndGet`
with a lambda - never a `get` followed by a `set`.

## When an atomic is not enough

One variable, one atomic. The moment **two** fields must change together -
debit one account and credit another, and never be seen half-done - no single
atomic can express it, and you are back to a lock. That is the next lesson, and
the capstone.

The family: `AtomicInteger`, `AtomicLong`, `AtomicBoolean`, and
`AtomicReference<T>` for objects.
""",
    warmup=[
        _jq("`getAndIncrement()` returns…",
            ["the value BEFORE the increment", "the value after",
             "void", "the number of retries"],
            0,
            "`incrementAndGet` is the other one. The names say which."),
        _jq("`count.set(count.get() + 1)` on an AtomicInteger is…",
            ["a race - two atomic operations do not compose into one",
             "safe", "the same as incrementAndGet", "a compile error"],
            0,
            "Atomicity belongs to a single call, not to a sequence."),
    ],
    exercises=[
        _jch("j30-atom-increment", "The lock-free counter", "Medium",
             "Read `k` and `m`, and have `k` threads each call `incrementAndGet()` `m` "
             "times on one shared `AtomicInteger`. No lock anywhere, and the total is "
             "still exactly `k * m`. Replace `____` with the start loop and the join "
             "loop.",
             _j30s("        int k = sc.nextInt();\n"
                   "        int m = sc.nextInt();\n"
                   "        AtomicInteger count = new AtomicInteger(0);\n"
                   "        Thread[] workers = new Thread[k];\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            workers[i] = new Thread(() -> {\n"
                   "                for (int j = 0; j < m; j++) {\n"
                   "                    count.incrementAndGet();\n"
                   "                }\n"
                   "            }, \"w\" + i);\n"
                   "            workers[i].start();\n"
                   "        }\n"
                   "        for (Thread w : workers) {\n"
                   "            w.join();\n"
                   "        }\n"
                   "        System.out.println(count.get());"),
             "        for (int i = 0; i < k; i++) {\n"
             "            workers[i] = new Thread(() -> {\n"
             "                for (int j = 0; j < m; j++) {\n"
             "                    count.incrementAndGet();\n"
             "                }\n"
             "            }, \"w\" + i);\n"
             "            workers[i].start();\n"
             "        }\n"
             "        for (Thread w : workers) {\n"
             "            w.join();\n"
             "        }",
             [_km30(k, m, str(k * m)) for (k, m) in _KM30],
             hints=["`new AtomicInteger(0)` is the shared counter; every thread captures "
                    "the same one.",
                    "`count.incrementAndGet()` is the whole read-modify-write, "
                    "indivisibly.",
                    "The loop counter `j` is a local, so it is not shared at all.",
                    "Start every thread, then join every thread - never join inside the "
                    "start loop.",
                    "`count.get()` after the joins is the total: `k * m`.",
                    "Compare with the synchronized version: same answer, no lock, and no "
                    "thread ever blocked."]),

        _je("j30-atom-getand", "Before or after",
            "`getAndIncrement` returns the old value; `incrementAndGet` returns the new "
            "one. Starting from `n`, print the result of a `getAndIncrement`, then of an "
            "`incrementAndGet`, then the final value. Replace `____` with the first of "
            "the two calls.",
            _j30s("        int n = sc.nextInt();\n"
                  "        AtomicInteger count = new AtomicInteger(n);\n"
                  "        System.out.println(count.getAndIncrement());\n"
                  "        System.out.println(count.incrementAndGet());\n"
                  "        System.out.println(count.get());"),
            "        System.out.println(count.getAndIncrement());",
            [_k30(n, _nl(n, n + 2, n + 2)) for n in _K30],
            hints=["`getAndIncrement` is the postfix `n++`: you get the old value.",
                   "So the first line prints `n`, and the counter is now `n + 1`.",
                   "`incrementAndGet` is the prefix `++n`: you get the new value.",
                   "So the second line prints `n + 2`, which is also the final value.",
                   "Both increment. They differ only in what they hand back."],
            difficulty="Easy"),

        _jch("j30-atom-cas", "Compare and set", "Hard",
             "`compareAndSet(expected, next)` swaps only if the value is still what you "
             "expected, and reports whether it did. Starting from `n`, show a successful "
             "swap, a failed one, and the final value. Replace `____` with the three "
             "prints.",
             _j30s("        int n = sc.nextInt();\n"
                   "        AtomicInteger count = new AtomicInteger(n);\n"
                   "        System.out.println(count.compareAndSet(n, n + 10));\n"
                   "        System.out.println(count.compareAndSet(n, 999));\n"
                   "        System.out.println(count.get());"),
             "        System.out.println(count.compareAndSet(n, n + 10));\n"
             "        System.out.println(count.compareAndSet(n, 999));\n"
             "        System.out.println(count.get());",
             [_k30(n, _nl("true", "false", n + 10)) for n in _K30],
             hints=["The first call expects `n`, which is what is there, so it swaps and "
                    "returns `true`.",
                    "After that the value is `n + 10`.",
                    "The second call still expects `n`, does NOT find it, and returns "
                    "`false` - changing nothing.",
                    "So `999` is never written.",
                    "That 'I did not overwrite somebody else's change' is exactly the "
                    "guarantee a retry loop is built on.",
                    "Every atomic increment in the JDK is this call in a `while` loop."]),

        _j30write("j30-atom-compose", "Two atomic calls are not one atomic call",
              "Medium",
              "Being an `AtomicInteger` does not rescue this:\n\n"
              "```java\n"
              "for (int i = 0; i < m; i++) {\n"
              "    count.set(count.get() + 1);   // two atomic calls, one race\n"
              "}\n"
              "```\n\n"
              "Each call is indivisible; the pair is not, and another thread's increment "
              "lands in the gap and is overwritten. Write the version that does the whole "
              "read-modify-write in ONE call, so the total is exactly `k * m`. Replace "
              "`____` with the whole body.",
              ("        int k = sc.nextInt();\n"
                    "        int m = sc.nextInt();\n"
                    "        AtomicInteger count = new AtomicInteger(0);\n"
                    "        Runnable job = () -> {\n"
                    "            for (int i = 0; i < m; i++) {\n"
                    "                count.incrementAndGet();\n"
                    "            }\n"
                    "        };\n"
                    "        Thread[] workers = new Thread[k];\n"
                    "        for (int i = 0; i < k; i++) {\n"
                    "            workers[i] = new Thread(job, \"w\" + i);\n"
                    "            workers[i].start();\n"
                    "        }\n"
                    "        for (Thread w : workers) {\n"
                    "            w.join();\n"
                    "        }\n"
                    "        System.out.println(count.get());"),
              [_km30(k, m, str(k * m)) for (k, m) in _KMBIG30],
              ["Being an `AtomicInteger` protects each CALL, not a sequence of two.",
               "`count.get()` and `count.set(...)` are two trips, with a gap in "
               "between where another thread runs.",
               "One call does the whole job: `count.incrementAndGet()`.",
               "That is a single hardware compare-and-set, retried until it wins.",
               "The type was never the problem - the composition was.",
               "The answer becomes exactly `k * m`, on every run."]),
    ],
    quiz=[
        _jq("`compareAndSet(expected, next)` returns false when…",
            ["the current value is no longer `expected`, and it changes nothing",
             "the value is null", "another thread is blocked",
             "the new value is smaller"],
            0,
            "Losing the race and knowing it is the point - you retry."),
        _jq("Atomics are called lock-free because…",
            ["a thread that loses the race retries rather than blocking",
             "they never fail", "they use a faster lock",
             "only one thread may use them"],
            0,
            "No blocking, no waiting queue - just a hardware CAS and a retry."),
    ],
))


# ===========================================================================
# 30.5 Locks and deadlock
# ===========================================================================

_M30.append(_jlesson(
    "m30-locks", "`ReentrantLock`, and deadlock",
    "The explicit lock - what it buys over `synchronized`, and the way two of them kill "
    "a program.",
    """
`ReentrantLock` is `synchronized` as an object rather than a keyword.

```java
private final ReentrantLock lock = new ReentrantLock();

lock.lock();
try {
    counter++;
} finally {
    lock.unlock();        // ALWAYS in a finally. Non-negotiable.
}
```

That `finally` is the price of the extra power: `synchronized` releases its lock
on every exit path automatically, and a `ReentrantLock` does not. An exception
between `lock()` and `unlock()` without a `finally` leaks the lock, and the next
thread to ask for it waits forever.

**What you get in return**, none of which `synchronized` can do:

```java
if (lock.tryLock()) { ... }                      // take it, or carry on - never block
if (lock.tryLock(1, TimeUnit.SECONDS)) { ... }   // ...or give up after a while
lock.lockInterruptibly();                        // waiting can be interrupted
new ReentrantLock(true);                         // fair: longest waiter goes first
```

`tryLock` is the important one: it turns "block until I can" into a decision you
can make. And **fairness** is a real trade - a fair lock hands out order and
gives up throughput, so the default is unfair.

Prefer `synchronized` when it fits. Reach for `ReentrantLock` when you need
`tryLock`, a timeout, interruptibility, or fairness.

## Deadlock

Two threads, two locks, opposite orders:

```java
// thread 1                     // thread 2
synchronized (a) {              synchronized (b) {
    synchronized (b) { ... }        synchronized (a) { ... }
}                               }
```

Thread 1 holds `a` and wants `b`; thread 2 holds `b` and wants `a`. Neither will
ever release. No exception, no CPU burn, no error - the program simply stops,
which is why deadlock is so much worse to diagnose than a race.

It needs four conditions at once, and breaking any one prevents it: mutual
exclusion, hold-and-wait, no pre-emption, and **circular wait**. The last is the
one you can actually control:

> **Impose a global order on locks, and always take them in that order.**

If both threads lock the lower-numbered account first, the cycle cannot form -
which is precisely the trick the capstone uses. `tryLock` with a timeout is the
other defence: you detect the situation, back off, and retry.

## The best lock is no lock

Before reaching for any of this, ask whether the sharing is necessary at all:

* **Confinement** - give each thread its own data, as module 29's slot-per-worker
  pattern does.
* **Immutability** - an object whose fields are `final` and never change cannot
  race. This is what module 12's immutable objects were quietly preparing.
* **A single atomic** - when exactly one variable is shared.

A lock is what is left when none of those fit.
""",
    warmup=[
        _jq("`lock.unlock()` belongs in a `finally` because…",
            ["an exception in the body would otherwise leak the lock forever",
             "it is faster", "the compiler requires it",
             "unlock can throw"],
            0,
            "`synchronized` does this for you; an explicit lock does not."),
        _jq("The deadlock condition you can most practically design away is…",
            ["circular wait - impose a global lock order",
             "mutual exclusion", "no pre-emption", "hold-and-wait"],
            0,
            "Always take the lower-numbered lock first, and no cycle can form."),
    ],
    exercises=[
        _jch("j30-lock-counter", "lock, try, finally, unlock", "Medium",
             "Read `k` and `m` and drive a shared counter from `k` threads, each "
             "incrementing `m` times under a `ReentrantLock`. The unlock goes in a "
             "`finally`. Print `k * m`. Replace `____` with the locked increment.",
             _j30s("        int k = sc.nextInt();\n"
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
                   "        Thread[] workers = new Thread[k];\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            workers[i] = new Thread(job, \"w\" + i);\n"
                   "            workers[i].start();\n"
                   "        }\n"
                   "        for (Thread w : workers) {\n"
                   "            w.join();\n"
                   "        }\n"
                   "        System.out.println(counter[0]);"),
             "            for (int i = 0; i < m; i++) {\n"
             "                lock.lock();\n"
             "                try {\n"
             "                    counter[0]++;\n"
             "                } finally {\n"
             "                    lock.unlock();\n"
             "                }\n"
             "            }",
             [_km30(k, m, str(k * m)) for (k, m) in _KM30],
             hints=["`lock()` comes BEFORE the `try`, not inside it - if `lock()` itself "
                    "threw, the finally would unlock something you never took.",
                    "The body of the try is only the critical section.",
                    "`finally { lock.unlock(); }` runs on every exit path.",
                    "All `k` threads share one lock object, captured by the lambda.",
                    "This is module 16's try/finally doing exactly the job it was "
                    "introduced for.",
                    "The total is `k * m`, the same as the synchronized version."]),

        _jch("j30-lock-trylock", "Take it, or do something else", "Medium",
             "`tryLock()` returns immediately with `true` or `false` instead of blocking. "
             "On an uncontended lock it succeeds; while YOU already hold it a reentrant "
             "acquire also succeeds - so unlock it twice. Print `true`, `true`, then the "
             "hold count, then `n`. Replace `____` with the tryLock sequence.",
             _j30s("        int n = sc.nextInt();\n"
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
                   "        System.out.println(n);"),
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
             "        }",
             [_k30(n, _nl("true", "true", 2, 0, n)) for n in _K30],
             hints=["Nobody else holds the lock, so the first `tryLock()` returns `true`.",
                    "The lock is REENTRANT, so the same thread taking it again also "
                    "returns `true`.",
                    "Each successful acquire must be matched by exactly one `unlock()` - "
                    "hence the nested try/finally.",
                    "`getHoldCount()` reports how many times THIS thread holds it: 2 in "
                    "the middle.",
                    "After both unlocks the hold count is back to 0.",
                    "`tryLock` never blocks, which is what makes deadlock recovery "
                    "possible."]),

        _jch("j30-lock-ordering", "Always take the lower one first", "Hard",
             "Two accounts and two threads transferring in opposite directions - the "
             "classic deadlock. Break the cycle by always locking the LOWER-indexed "
             "account first, whichever way the money is going. Read `n`; each thread "
             "moves `n` across once. The balances end where they started, so print both "
             "and their total. Replace `____` with the ordered transfer.",
             _j30h("    static void transfer(int[] balances, ReentrantLock[] locks,\n"
                   "            int from, int to, int amount) {\n"
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
                   "    }",
                   "        int n = sc.nextInt();\n"
                   "        int[] balances = {100, 100};\n"
                   "        ReentrantLock[] locks = {new ReentrantLock(), new ReentrantLock()};\n"
                   "        Runnable aToB = () -> {\n"
                   "            transfer(balances, locks, 0, 1, n);\n"
                   "        };\n"
                   "        Runnable bToA = () -> {\n"
                   "            transfer(balances, locks, 1, 0, n);\n"
                   "        };\n"
                   "        Thread t1 = new Thread(aToB, \"t1\");\n"
                   "        Thread t2 = new Thread(bToA, \"t2\");\n"
                   "        t1.start();\n"
                   "        t2.start();\n"
                   "        t1.join();\n"
                   "        t2.join();\n"
                   "        System.out.println(balances[0]);\n"
                   "        System.out.println(balances[1]);\n"
                   "        System.out.println(balances[0] + balances[1]);"),
             "        Runnable aToB = () -> {\n"
             "            transfer(balances, locks, 0, 1, n);\n"
             "        };\n"
             "        Runnable bToA = () -> {\n"
             "            transfer(balances, locks, 1, 0, n);\n"
             "        };",
             [_k30(n, _nl(100, 100, 200)) for n in _K30],
             hints=["`transfer` is written for you below `main`; it locks "
                    "`min(from, to)` first and `max(from, to)` second.",
                    "Because BOTH threads use that same rule, they can never hold locks "
                    "in a cycle.",
                    "Locking `from` then `to` instead would deadlock the moment the two "
                    "transfers overlap.",
                    "Each thread moves `n` one way, so the two transfers cancel out.",
                    "The balances return to 100 and 100 whichever order they ran in.",
                    "The total is invariant by construction - money is only ever moved, "
                    "never created."]),

        _jch("j30-lock-immutable", "The lock you did not need", "Medium",
             "`Point` is immutable: `final` fields, no setters, and `moved` returns a NEW "
             "Point. An object that cannot change cannot race, so several threads may "
             "share it with no lock at all. Read `n`, have two threads each derive their "
             "own moved copy into their own slot, and print the original and both copies. "
             "Replace `____` with the two threads and their joins.",
             _j30t("class Point {\n"
                   "    private final int x;\n"
                   "    private final int y;\n\n"
                   "    Point(int x, int y) {\n"
                   "        this.x = x;\n"
                   "        this.y = y;\n"
                   "    }\n\n"
                   "    Point moved(int dx, int dy) {\n"
                   "        return new Point(x + dx, y + dy);\n"
                   "    }\n\n"
                   "    @Override\n"
                   "    public String toString() {\n"
                   "        return x + \",\" + y;\n"
                   "    }\n"
                   "}",
                   "        int n = sc.nextInt();\n"
                   "        Point origin = new Point(n, n);\n"
                   "        Point[] out = new Point[2];\n"
                   "        Thread a = new Thread(() -> out[0] = origin.moved(1, 0), \"a\");\n"
                   "        Thread b = new Thread(() -> out[1] = origin.moved(0, 1), \"b\");\n"
                   "        a.start();\n"
                   "        b.start();\n"
                   "        a.join();\n"
                   "        b.join();\n"
                   "        System.out.println(origin);\n"
                   "        System.out.println(out[0]);\n"
                   "        System.out.println(out[1]);"),
             "        Thread a = new Thread(() -> out[0] = origin.moved(1, 0), \"a\");\n"
             "        Thread b = new Thread(() -> out[1] = origin.moved(0, 1), \"b\");\n"
             "        a.start();\n"
             "        b.start();\n"
             "        a.join();\n"
             "        b.join();",
             [_k30(n, _nl(f"{n},{n}", f"{n + 1},{n}", f"{n},{n + 1}")) for n in _K30],
             hints=["Both threads only READ `origin`, and readers never race with each "
                    "other.",
                    "`moved` returns a new Point rather than mutating - so there is no "
                    "shared write at all.",
                    "Each thread writes its own slot in `out`, which is module 29's "
                    "pattern again.",
                    "The joins publish both slots before main prints them.",
                    "`origin` is unchanged, because nothing could have changed it.",
                    "This is module 12's immutability, and it is the cheapest thread "
                    "safety there is."]),
    ],
    quiz=[
        _jq("`ReentrantLock` over `synchronized` buys you…",
            ["tryLock, timeouts, interruptible waiting and optional fairness",
             "better performance always", "automatic unlocking",
             "protection from deadlock"],
            0,
            "And costs you the finally block that `synchronized` did for free."),
        _jq("A deadlocked program…",
            ["stops, with no exception and no CPU use",
             "throws DeadlockException", "spins at 100% CPU",
             "recovers after a timeout"],
            0,
            "Silence is what makes it so much harder to find than a race."),
    ],
))


# ===========================================================================
# Capstone
# ===========================================================================

_M30_CAP_TYPES = (
    "class Bank {\n"
    "    private final int[] balances;\n"
    "    private final ReentrantLock[] locks;\n\n"
    "    Bank(int[] balances) {\n"
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
    "}"
)

_M30_CAP_BODY = (
    "        int n = sc.nextInt();\n"
    "        int[] start = new int[n];\n"
    "        for (int i = 0; i < n; i++) {\n"
    "            start[i] = sc.nextInt();\n"
    "        }\n"
    "        int t = sc.nextInt();\n"
    "        int[] from = new int[t];\n"
    "        int[] to = new int[t];\n"
    "        int[] amount = new int[t];\n"
    "        for (int i = 0; i < t; i++) {\n"
    "            from[i] = sc.nextInt();\n"
    "            to[i] = sc.nextInt();\n"
    "            amount[i] = sc.nextInt();\n"
    "        }\n"
    "        Bank bank = new Bank(start);\n"
    "        Thread[] workers = new Thread[t];\n"
    "        for (int i = 0; i < t; i++) {\n"
    "            final int idx = i;\n"
    "            workers[i] = new Thread(\n"
    "                    () -> bank.transfer(from[idx], to[idx], amount[idx]), \"t\" + idx);\n"
    "            workers[i].start();\n"
    "        }\n"
    "        for (Thread w : workers) {\n"
    "            w.join();\n"
    "        }\n"
    "        int total = 0;\n"
    "        for (int i = 0; i < n; i++) {\n"
    "            System.out.println(i + \" \" + bank.balance(i));\n"
    "            total += bank.balance(i);\n"
    "        }\n"
    "        System.out.println(total);"
)


def _cap30(start, transfers):
    """The Python mirror. Transfers are plain additions, so the final balances do
    not depend on the order they are applied in - which is exactly why this
    program can be judged at all."""
    bal = list(start)
    for (f, t, amt) in transfers:
        bal[f] -= amt
        bal[t] += amt
    lines = [f"{i} {b}" for i, b in enumerate(bal)]
    lines.append(str(sum(bal)))
    return _nl(*lines)


def _cap30_case(start, transfers):
    parts = [str(len(start)), _sp(start), str(len(transfers))]
    for (f, t, amt) in transfers:
        parts.append(f"{f} {t} {amt}")
    return _case("\n".join(parts), _cap30(start, transfers))


_CAP30_DATA = (
    ([100, 100], [(0, 1, 30), (1, 0, 30)]),
    ([100, 100, 100], [(0, 1, 10), (1, 2, 20), (2, 0, 5)]),
    ([50], [(0, 0, 25)]),
    ([10, 20, 30, 40], [(3, 0, 15), (0, 3, 15), (1, 2, 5), (2, 1, 5)]),
    ([200, 0], [(0, 1, 50), (0, 1, 50), (0, 1, 25)]),
)


_M30_CAP = _jcap(
    "The bank",
    """
`n` accounts, `t` transfers, every transfer on its own thread, all at once.

A transfer is the thing a single atomic cannot express: **two** balances must
change together, and no one may ever observe the money in mid-air. So it needs a
lock - two, in fact - and that is where deadlock comes from.

The design, and every part of it is one of this module's lessons:

* **A lock per account, not one lock for the bank.** One global lock would be
  correct and would serialise every transfer in the system, including the ones
  that share no accounts.
* **Take the lower-numbered lock first, always.** `min(from, to)` then
  `max(from, to)`, regardless of which way the money is moving. Both threads of
  an A→B / B→A pair then reach for the same lock first, so the circular wait
  that deadlock needs cannot form. Locking `from` then `to` would be the bug.
* **`unlock` in a `finally`, nested.** Two locks, two try/finally blocks, and
  the inner unlock happens before the outer one.
* **Main reads only after joining everything**, and prints the accounts in index
  order.

**Why this is testable at all.** A transfer is a pair of additions, and addition
commutes - so the final balances are the same whatever order the transfers land
in. The *order* is nondeterministic; the *answer* is not. The total is invariant
by construction, since money is only ever moved. If your total ever differs from
the sum of the opening balances, you have a real bug, not a scheduling quirk.

Note the third test case: an account transferring to itself. `min` and `max` are
then the same index, and the lock is taken twice by one thread - which works
only because `ReentrantLock` is reentrant. Unlock it as many times as you locked
it.
""",
    _jch("j30-cap-bank", "The bank", "Hard",
         "Read `n` opening balances, then `t` transfers as `from to amount`. Run every "
         "transfer on its own thread with per-account locks taken in index order, then "
         "print `index balance` per account and the grand total.",
         _j30t(_M30_CAP_TYPES, _M30_CAP_BODY),
         _M30_CAP_BODY,
         [_cap30_case(s, ts) for (s, ts) in _CAP30_DATA],
         hints=["Read every number on the main thread first, into parallel arrays.",
                "`Bank` is written for you: it builds one `ReentrantLock` per account and "
                "orders them with `Math.min` and `Math.max`.",
                "One thread per transfer: `new Thread(() -> bank.transfer(from[idx], "
                "to[idx], amount[idx]), \"t\" + idx)`.",
                "`final int idx = i;` before the lambda, as always.",
                "Start every thread in the first loop, join every thread in the second.",
                "Read the balances only after every join, and print them in index order.",
                "A self-transfer locks the same account twice - fine, because the lock is "
                "reentrant, provided you unlock twice too.",
                "The total must equal the sum of the opening balances in every case."]),
    example_io="stdin:  2\n        100 100\n        2\n        0 1 30\n        1 0 30\n\n"
               "stdout: 0 100\n        1 100\n        200",
    rubric=[
        "One lock per account, not a single lock for the whole bank.",
        "Both locks are taken in a consistent global order - lower index first.",
        "Each `unlock` sits in a `finally`, and the two are correctly nested.",
        "Every transfer runs on its own thread, all started before any is joined.",
        "Balances are read only after every thread has been joined.",
        "A self-transfer works, relying on the lock being reentrant.",
        "The printed total equals the sum of the opening balances in every case.",
        "The output is identical on every run.",
    ],
    stretch=None,
)


_MODULES.append(_jmod(
    30, 10, "Multithreading",
    "Shared state: races, locks and visibility",
    "What goes wrong when two threads reach for one variable, and the four things you "
    "can do about it.",
    """
Module 29 kept every worker on its own slot. This one lets them share, and fixes
what breaks.

* **`count++` is three operations** - read, add, write - so two threads can lose
  an update. That is a **race condition**: correctness depending on scheduling.
  The other shape is **check-then-act**, where the decision is stale before it is
  used.
* **`synchronized`** takes an object's intrinsic lock, and releases it on every
  exit including a thrown one. Instance methods lock `this`; `static` ones lock
  the **`Class`** - two different locks. Mutual exclusion only happens between
  threads locking the *same* object.
* **Visibility is a separate problem.** A thread may never see another's write at
  all. **`volatile`** guarantees it sees the latest value - and does **not** make
  `++` atomic. `start()` and `join()` create the same guarantee, which is why
  module 29 needed neither.
* **Atomics** make one read-modify-write indivisible without a lock, on a
  hardware compare-and-set. Two atomic calls still do not compose into one.
* **`ReentrantLock`** adds `tryLock`, timeouts, interruptibility and fairness,
  and costs you an explicit `unlock` in a `finally`.
* **Deadlock** is two threads taking two locks in opposite orders. The practical
  cure is a **global lock order**.
* **The best lock is no lock**: confine the data to one thread, or make it
  immutable.

`ExecutorService`, `Callable` and the concurrent collections are module 31.
""",
    _M30,
    capstone=_M30_CAP,
    objectives=[
        "Explain why `count++` can lose an update, step by step.",
        "Recognise check-then-act as a race, and name the atomic operation that replaces it.",
        "Use `synchronized` blocks and methods, and say which object each one locks.",
        "Explain why a `static synchronized` and an instance `synchronized` method do not exclude each other.",
        "Spot a lock that protects nothing because it is not shared.",
        "Distinguish visibility from atomicity, and say exactly what `volatile` does and does not give.",
        "Name the happens-before edges created by `start()` and `join()`.",
        "Use `AtomicInteger`, and say why `set(get() + 1)` is still a race.",
        "Explain compare-and-set, and why atomics are called lock-free.",
        "Use `ReentrantLock` with `unlock` in a `finally`, and say what it buys over `synchronized`.",
        "Explain deadlock, and prevent it with a global lock ordering.",
        "Choose confinement or immutability over locking where it fits.",
    ],
    why="This is the module that separates people who have used threads from people who "
        "understand them. The interview questions are exact - why `++` is not atomic, "
        "what `volatile` does and does not guarantee, why `static synchronized` locks "
        "something different, what deadlock needs and how to prevent it - and almost "
        "everyone gets the `volatile` one wrong. The habit underneath matters more: "
        "concurrency bugs do not show up in testing, so they have to be designed out "
        "rather than debugged out, and the ranked answer is always confinement first, "
        "then immutability, then an atomic, then a lock.",
    est_minutes=360,
    glossary=[
        _jg("race condition", "A program whose correctness depends on the order in which "
                              "threads happen to be scheduled."),
        _jg("lost update", "Two read-modify-write sequences interleaving so that one "
                           "increment overwrites the other."),
        _jg("check-then-act", "Deciding on a value that another thread may change before "
                              "the decision is used."),
        _jg("atomic", "Indivisible from every other thread's point of view."),
        _jg("critical section", "The region a lock protects. Keep it small: it is the "
                                "part that does not scale."),
        _jg("intrinsic lock", "The monitor every Java object carries, taken by "
                              "`synchronized`."),
        _jg("reentrant", "A lock the holding thread may acquire again without blocking."),
        _jg("visibility", "Whether one thread's write is observable by another at all - "
                          "separate from atomicity."),
        _jg("happens-before", "The ordering that makes a write visible to a later read. "
                              "Created by a lock, by `volatile`, by `start()` and by "
                              "`join()`."),
        _jg("volatile", "Every read and write goes to main memory and is not reordered "
                        "across. Visibility, never atomicity of `++`."),
        _jg("compare-and-set", "A hardware instruction that swaps a value only if it is "
                               "still what you expected, and reports whether it did."),
        _jg("lock-free", "Progress without blocking: a thread that loses the race retries "
                         "rather than waiting."),
        _jg("deadlock", "Threads each holding a lock the other needs. No exception, no CPU "
                        "use - the program simply stops."),
        _jg("lock ordering", "Giving every lock a global rank and always acquiring in that "
                             "order, so a circular wait cannot form."),
    ],
    cheatsheet="""
```java
// --- the bug --------------------------------------------------------------
count++;              // READ, ADD, WRITE. Another thread can run in between.
if (m.get(k) == null) m.put(k, v);     // check-then-act: both threads pass the check

// --- synchronized ---------------------------------------------------------
synchronized (lock) { counter++; }     // releases on EVERY exit, throws included
synchronized void add() {}             // locks `this`
static synchronized void tally() {}    // locks Foo.class - A DIFFERENT LOCK
private final Object lock = new Object();   // better than locking `this` (public)
// Threads take turns only if they lock the SAME object:
Runnable bad = () -> { Object l = new Object(); synchronized (l) {...} };  // useless

// --- visibility -----------------------------------------------------------
volatile boolean running;   // every read/write hits main memory; no reordering
volatile int count; count++;           // STILL A RACE - visibility, not atomicity
// happens-before you already had:  everything before start()  -> the new thread
//                                  everything before a thread ends -> after join()

// --- atomics (java.util.concurrent.atomic) --------------------------------
AtomicInteger c = new AtomicInteger(0);
c.incrementAndGet();     // ++c : returns the NEW value
c.getAndIncrement();     // c++ : returns the OLD value
c.addAndGet(5);  c.get();  c.set(7);
c.compareAndSet(expected, next);       // true if swapped; the basis of lock-free
c.set(c.get() + 1);                    // WRONG - two operations, not one

// --- ReentrantLock (java.util.concurrent.locks) ---------------------------
lock.lock();                           // OUTSIDE the try
try { ... } finally { lock.unlock(); } // ALWAYS a finally
lock.tryLock();                        // true/false, never blocks
lock.tryLock(1, TimeUnit.SECONDS);  lock.lockInterruptibly();
new ReentrantLock(true);               // fair: order, at the cost of throughput

// --- deadlock -------------------------------------------------------------
// t1: sync(a){ sync(b){} }     t2: sync(b){ sync(a){} }    -> stops, silently
locks[min(i,j)].lock(); locks[max(i,j)].lock();   // global order: no cycle possible

// --- ranked, best first ---------------------------------------------------
// 1 confine (a slot each)   2 immutable (final fields)
// 3 one atomic              4 a lock
```
""",
    self_check=[
        "Can you walk through a lost update, step by step, with two threads?",
        "Can you say why a sleep makes a race reproducible without causing it?",
        "Can you say which object a `synchronized` instance method locks, and which a static one locks?",
        "Can you spot a `synchronized` block that protects nothing, and say why?",
        "Can you state what `volatile` guarantees, and what it does not?",
        "Can you name two happens-before edges you were already relying on in module 29?",
        "Can you say why `set(get() + 1)` on an AtomicInteger is a race?",
        "Can you explain compare-and-set and why it needs no lock?",
        "Can you say why `unlock()` must be in a `finally` and `lock()` outside the `try`?",
        "Can you describe deadlock and give the one practical way to prevent it?",
        "Can you rank confinement, immutability, atomics and locks, and say when each fits?",
    ],
    review=[
        _jq("Two threads each run `count++` a thousand times on a shared int. The result is…",
            ["at most 2000, and usually less - updates get lost",
             "always 2000", "always 1000", "always 0"],
            0,
            "Every interleaved read-modify-write pair costs you one increment."),
        _jq("```java\nvolatile int count;\ncount++;\n```\nThis is…",
            ["still a race - volatile gives visibility, not atomicity",
             "thread-safe", "thread-safe for two threads",
             "slower but correct"],
            0,
            "The single most common wrong answer in the whole topic."),
        _jq("A `static synchronized` method and a `synchronized` instance method on the same object…",
            ["take different locks and can run at the same time",
             "take the same lock", "deadlock", "cannot both be called"],
            0,
            "Class object versus `this`. A field touched by both is unprotected."),
        _jq("`lock.unlock()` outside a `finally` risks…",
            ["leaking the lock if the body throws, hanging every later thread",
             "a compile error", "an IllegalMonitorStateException always",
             "nothing"],
            0,
            "`synchronized` does this for you; an explicit lock does not."),
        _jq("The practical cure for deadlock is…",
            ["a global lock order, always acquired lowest-first",
             "more locks", "fair locks", "longer timeouts"],
            0,
            "Break the circular wait and no cycle can form."),
        _jq("Given a choice, the cheapest thread safety is…",
            ["not sharing at all - confine the data, or make it immutable",
             "a fair ReentrantLock", "volatile on every field",
             "synchronizing every method"],
            0,
            "A lock is what is left when confinement and immutability do not fit."),
    ],
    milestone="You can explain exactly how a lost update happens, say what `volatile` "
              "does and refuse to over-claim for it, pick between a synchronized block, "
              "an atomic and an explicit lock on the merits, prevent deadlock with a lock "
              "ordering - and, before any of that, notice when the right answer is to "
              "stop sharing the data at all.",
))
