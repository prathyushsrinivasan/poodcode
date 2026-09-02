# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 10 — Recursion basics.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`. This is
# the last authored module: it closes Part 3 and the shipped scope of the
# course (see JAVA_ROADMAP.md for what Parts 4-14 will cover).
#
# Recursion comes LAST in Part 3 rather than first, because every recursive
# solution here is a method calling itself — so it needs module 9's method
# mechanics, and because seeing the iterative version first (modules 1-8) is
# what makes "why would I write it this way?" answerable.
#
# The Python mirrors below compute every expected output, including the
# call-count traces in lesson 10.6 where hand-typing would be hopeless.
# ---------------------------------------------------------------------------

_M10 = []


# --- Python mirrors ---------------------------------------------------------

def _updown(n):
    out = [str(i) for i in range(n, 0, -1)]
    out += [str(i) for i in range(1, n + 1)]
    return _nl(*out) if out else ""


def _digit_sum(n):
    return n if n < 10 else n % 10 + _digit_sum(n // 10)


def _gcd(a, b):
    return a if b == 0 else _gcd(b, a % b)


def _fib(n):
    """Iterative on purpose: the Java side is (sometimes) the naive exponential
    version, but generating the seed must not be. `_fib(70)` written naively
    here would not finish this decade."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _fib_calls(n):
    """How many times a naive recursive fib() is entered while computing
    fib(n). Satisfies calls(n) = 1 + calls(n-1) + calls(n-2), which is
    2*fib(n+1) - 1 — computed iteratively for the same reason as above."""
    return 2 * _fib(n + 1) - 1


def _remove_char(s, c):
    return s.replace(c, "")


def _bsearch_rec(a, target, lo, hi):
    if lo > hi:
        return -1
    mid = lo + (hi - lo) // 2
    if a[mid] == target:
        return mid
    if a[mid] < target:
        return _bsearch_rec(a, target, mid + 1, hi)
    return _bsearch_rec(a, target, lo, mid - 1)


def _fast_pow(b, e):
    if e == 0:
        return 1
    half = _fast_pow(b, e // 2)
    return half * half if e % 2 == 0 else half * half * b


def _atkcase(a, t, k, out):
    """stdin = a length-prefixed array, then a target, then one more integer."""
    return _case(f"{len(a)}\n{_sp(a)}\n{t}\n{k}", out)


# --- 10.1 The two parts -----------------------------------------------------

_M10.append(_jlesson(
    "m10-base", "Base case and recursive case",
    "A method that calls itself, a case that doesn't, and the stack in between.",
    """
A **recursive** method calls itself on a smaller version of its own problem.
Every one of them has exactly two parts, and both are mandatory:

```java
static void countdown(int n) {
    if (n == 0) {                     // BASE CASE: stop, do not recurse
        System.out.println("go");
        return;
    }
    System.out.println(n);
    countdown(n - 1);                  // RECURSIVE CASE: smaller problem
}
```

**The base case** is the input simple enough to answer outright. **The
recursive case** must make *progress* toward it — here `n - 1` marches toward
0. Miss the base case, or fail to shrink the problem, and the method calls
itself forever until the stack runs out:
`java.lang.StackOverflowError`.

**Three questions to ask of any recursive method,** and if all three answer
"yes" it is correct:

1. Is there a base case that returns without recursing?
2. Does every recursive call move strictly closer to it?
3. Assuming the recursive call returns the right answer for the smaller
   problem, does this method then build the right answer? (This is the
   "recursive leap of faith" — do not trace it all the way down.)

**The call stack** is what makes it work. Each call gets its own **frame**
holding its own parameters and locals. `countdown(3)` puts four frames on the
stack — `n = 3, 2, 1, 0` — and they unwind in reverse as each returns.

That is why the placement of a statement matters so much:

```java
static void updown(int n) {
    if (n == 0) return;
    System.out.println(n);          // printed on the way DOWN
    updown(n - 1);
    System.out.println(n);          // printed on the way BACK UP
}
```

`updown(3)` prints `3 2 1 1 2 3`. Every frame's second println is waiting,
paused, until everything beneath it has finished — which is exactly what the
stack is holding for you. Half the point of learning recursion is developing
the feel for that "on the way down / on the way back up" distinction.

**Returning a value** works the same way — the recursive call is an expression
whose value you use:

```java
static int sumTo(int n) {
    if (n == 0) return 0;              // base
    return n + sumTo(n - 1);           // n plus the answer to the smaller problem
}
```
""",
    warmup=[
        _jq("What does `updown(2)` print, given the method above?",
            ["2 1 1 2 (one per line)", "2 1", "1 2", "2 1 2"],
            0,
            "Each frame prints on the way down and again on the way back up, so the output is "
            "a mirror. The second println waits, paused, until everything below it finishes."),
        _jq("A recursive method with no base case produces…",
            ["StackOverflowError", "an infinite loop that never errors",
             "a compile error", "OutOfMemoryError"],
            0,
            "Each call consumes a stack frame, and the stack is finite — typically some tens "
            "of thousands of frames deep."),
    ],
    exercises=[
        _je("j10-base-countdown", "Stop at zero",
            "`countdown` should print `n`, `n-1`, … down to `1`, then the word `go`. "
            "Replace `____` with the base case.",
            _jm('    static void countdown(int n) {\n'
                "        if (n == 0) {\n"
                '            System.out.println("go");\n'
                "            return;\n"
                "        }\n"
                "        System.out.println(n);\n"
                "        countdown(n - 1);\n"
                "    }",
                "        int k = sc.nextInt();\n"
                "        countdown(k);"),
            "        if (n == 0) {\n"
            '            System.out.println("go");\n'
            "            return;\n"
            "        }",
            [_case(k, _nl(*([str(i) for i in range(k, 0, -1)] + ["go"])))
             for k in (3, 1, 0, 5)],
            hints=["The base case is the value simple enough to answer without recursing.",
                   'At zero there is nothing left to count — print `go` and return.',
                   'if (n == 0) { System.out.println("go"); return; }'],
            difficulty="Intro"),

        _je("j10-base-sum", "Sum by recursion",
            "`sumTo` should return `1 + 2 + … + n`, with `sumTo(0)` being 0. Replace "
            "`____` with the recursive case.",
            _jm("    static int sumTo(int n) {\n"
                "        if (n == 0) return 0;\n"
                "        return n + sumTo(n - 1);\n"
                "    }",
                "        int k = sc.nextInt();\n"
                "        System.out.println(sumTo(k));"),
            "return n + sumTo(n - 1);",
            [_case(k, k * (k + 1) // 2) for k in (5, 1, 0, 10)],
            hints=["`n` plus the answer to the same question for a smaller number.",
                   "Take the leap of faith: assume `sumTo(n - 1)` is already correct.",
                   "`return n + sumTo(n - 1);`"],
            difficulty="Intro"),

        _jfix("j10-base-missing", "It never stops",
              "`countUp` should print `1` up to `n`. It crashes with "
              "`StackOverflowError` — there is nothing telling it when to stop.",
              _jm("    static void countUp(int i, int n) {\n"
                  "        System.out.println(i);\n"
                  "        countUp(i + 1, n);\n"
                  "    }",
                  "        int k = sc.nextInt();\n"
                  "        countUp(1, k);"),
              _jm("    static void countUp(int i, int n) {\n"
                  "        if (i > n) return;\n"
                  "        System.out.println(i);\n"
                  "        countUp(i + 1, n);\n"
                  "    }",
                  "        int k = sc.nextInt();\n"
                  "        countUp(1, k);"),
              [_case(k, _nl(*[str(i) for i in range(1, k + 1)])) for k in (3, 1, 5)],
              hints=["Which of the two mandatory parts is missing?",
                     "There must be an input the method answers without calling itself.",
                     "Add `if (i > n) return;` as the first line."],
              difficulty="Intro"),

        _jch("j10-base-updown", "Down and back up", "Medium",
             "Write `updown(int n)`, which prints `n` down to `1` and then `1` back up "
             "to `n`, one number per line. For `n = 3` that is `3 2 1 1 2 3`. Do it "
             "with **one** println before the recursive call and one after — no "
             "loops. Write the whole method where you see `____`.",
             _jm("    static void updown(int n) {\n"
                 "        if (n == 0) return;\n"
                 "        System.out.println(n);\n"
                 "        updown(n - 1);\n"
                 "        System.out.println(n);\n"
                 "    }",
                 "        int k = sc.nextInt();\n"
                 "        updown(k);"),
             "    static void updown(int n) {\n"
             "        if (n == 0) return;\n"
             "        System.out.println(n);\n"
             "        updown(n - 1);\n"
             "        System.out.println(n);\n"
             "    }",
             [_case(k, _updown(k)) for k in (3, 1, 4)],
             hints=["Base case first: at 0 there is nothing to print, so just return.",
                    "The first println happens on the way DOWN, the second on the way back UP.",
                    "The second println is paused in its frame until every deeper call has "
                    "finished — that is the call stack doing the work for you.",
                    "`n = 0` must print nothing at all."]),
    ],
    quiz=[
        _jq("What are the three questions that establish a recursive method is correct?",
            ["Is there a base case? Does each call approach it? Does it combine the smaller answer correctly?",
             "Is it static? Does it return a value? Does it have a loop?",
             "Is it tail-recursive? Is it memoized? Is it O(n)?",
             "Does it compile, run, and terminate?"],
            0,
            "The third is the leap of faith: assume the recursive call is right and check only "
            "the step you are writing. Tracing all the way down is how people get lost."),
        _jq("Why does a statement AFTER the recursive call run in reverse order?",
            ["Each frame pauses there until every deeper call has returned",
             "Java reorders the statements",
             "It doesn't — it runs in the same order",
             "Because of the base case"],
            0,
            "The frames unwind last-in-first-out, so the deepest call's trailing statement runs "
            "first. It is the stack made visible."),
    ],
))

# --- 10.2 Numeric recursion -------------------------------------------------

_M10.append(_jlesson(
    "m10-numbers", "Recursion on numbers",
    "Factorial, powers, gcd, Fibonacci — and the one that is a trap.",
    """
**Factorial** is the textbook example because its mathematical definition is
already recursive: `n! = n × (n-1)!`, and `0! = 1`.

```java
static int factorial(int n) {
    if (n <= 1) return 1;                 // 0! and 1! are both 1
    return n * factorial(n - 1);
}
```

Note `n <= 1` rather than `n == 1`: it covers 0 in the same line and stops
negative input from recursing forever. Guarding the base case a little more
widely than strictly necessary is cheap insurance.

`int` overflows at `13!`, so real factorials want `long` (good to `20!`) or
`BigInteger`. Worth saying out loud.

**Power** — `b^e = b × b^(e-1)`, with `b^0 = 1`:

```java
static int power(int b, int e) {
    if (e == 0) return 1;
    return b * power(b, e - 1);
}
```

**Greatest common divisor**, by Euclid, is the most elegant recursion in
ordinary use:

```java
static int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}
```

The base case is `b == 0`, not `a == 0`, and the arguments swap on every call.
It is O(log n) and there is no simpler iterative version worth writing — this is
a case where recursion genuinely is the clearest code.

**Digit manipulation** works because `/ 10` and `% 10` shrink the problem:

```java
static int digitSum(int n) {
    if (n < 10) return n;                 // one digit left
    return n % 10 + digitSum(n / 10);     // last digit + the rest
}
```

**Fibonacci is the trap.** The definition is recursive — `F(n) = F(n-1) +
F(n-2)`, `F(0) = 0`, `F(1) = 1` — so the code writes itself:

```java
static int fib(int n) {
    if (n < 2) return n;                  // covers BOTH base cases at once
    return fib(n - 1) + fib(n - 2);
}
```

…and it is **exponential**. `fib(40)` makes over 300 million calls, because
`fib(n-2)` is recomputed inside `fib(n-1)` and so on, all the way down. It is
correct, elegant, and unusable — which makes it the perfect illustration of
why "recursive" does not mean "good". Lesson 10.6 fixes it with memoization.

Note that `if (n < 2) return n;` collapses both base cases: it returns 0 for 0
and 1 for 1. Writing only `if (n == 0) return 0;` leaves `fib(1)` recursing into
`fib(-1)`, and away it goes.
""",
    warmup=[
        _jq("Why is factorial's base case `n <= 1` rather than `n == 1`?",
            ["It covers 0 too, and stops negative input recursing forever",
             "Because 1! is undefined",
             "For speed",
             "There is no difference"],
            0,
            "`0!` is 1, and a stray negative argument with `n == 1` would recurse past it "
            "forever. A slightly wider guard is cheap."),
        _jq("`fib(n)` written naively makes roughly how many calls for n = 40?",
            ["Hundreds of millions", "40", "1,600", "About 100"],
            0,
            "The call tree branches twice per level with almost no sharing, so the count grows "
            "like φⁿ. Correct, elegant, and unusable."),
    ],
    exercises=[
        _je("j10-num-fact", "Factorial",
            "`factorial` should return `n!`, with `0!` and `1!` both equal to 1. "
            "Replace `____` with the base case.",
            _jm("    static long factorial(int n) {\n"
                "        if (n <= 1) return 1;\n"
                "        return n * factorial(n - 1);\n"
                "    }",
                "        int k = sc.nextInt();\n"
                "        System.out.println(factorial(k));"),
            "if (n <= 1) return 1;",
            [_case(k, __import__("math").factorial(k)) for k in (5, 1, 0, 12)],
            hints=["Which inputs can you answer without recursing?",
                   "Both 0 and 1 give 1, so one comparison covers them.",
                   "`if (n <= 1) return 1;`"],
            difficulty="Intro"),

        _je("j10-num-gcd", "Euclid's algorithm",
            "`gcd` should return the greatest common divisor. Replace `____` with the "
            "recursive case — mind which argument goes where.",
            _jm("    static int gcd(int a, int b) {\n"
                "        if (b == 0) return a;\n"
                "        return gcd(b, a % b);\n"
                "    }",
                "        int x = sc.nextInt();\n"
                "        int y = sc.nextInt();\n"
                "        System.out.println(gcd(x, y));"),
            "return gcd(b, a % b);",
            [_case(f"{x}\n{y}", _gcd(x, y))
             for (x, y) in ((48, 18), (17, 5), (100, 100), (7, 0))],
            hints=["The arguments swap: the old `b` becomes the new `a`.",
                   "The new second argument is the remainder.",
                   "`return gcd(b, a % b);`"],
            difficulty="Medium"),

        _je("j10-num-digits", "Sum of the digits",
            "`digitSum` should add up a non-negative number's decimal digits — for "
            "`472` that is 13. Replace `____` with the recursive case.",
            _jm("    static int digitSum(int n) {\n"
                "        if (n < 10) return n;\n"
                "        return n % 10 + digitSum(n / 10);\n"
                "    }",
                "        int k = sc.nextInt();\n"
                "        System.out.println(digitSum(k));"),
            "return n % 10 + digitSum(n / 10);",
            [_case(k, _digit_sum(k)) for k in (472, 5, 999, 1000)],
            hints=["`% 10` gives you the last digit; `/ 10` gives you everything else.",
                   "Add the last digit to the answer for the rest.",
                   "`return n % 10 + digitSum(n / 10);`"],
            difficulty="Medium"),

        _jfix("j10-num-fibbase", "One base case short",
              "`fib` should return the nth Fibonacci number with `fib(0) = 0` and "
              "`fib(1) = 1`. It crashes with `StackOverflowError` for every input "
              "above 0, because one base case is missing.",
              _jm("    static int fib(int n) {\n"
                  "        if (n == 0) return 0;\n"
                  "        return fib(n - 1) + fib(n - 2);\n"
                  "    }",
                  "        int k = sc.nextInt();\n"
                  "        System.out.println(fib(k));"),
              _jm("    static int fib(int n) {\n"
                  "        if (n < 2) return n;\n"
                  "        return fib(n - 1) + fib(n - 2);\n"
                  "    }",
                  "        int k = sc.nextInt();\n"
                  "        System.out.println(fib(k));"),
              [_case(k, _fib(k)) for k in (0, 1, 7, 12)],
              hints=["Trace `fib(1)`: it recurses into `fib(0)` and `fib(-1)`. What stops "
                     "`fib(-1)`?",
                     "Both 0 and 1 must return without recursing.",
                     "`if (n < 2) return n;` handles both in one line."]),

        _jch("j10-num-power", "Raise to a power", "Easy",
             "Write `power(int b, int e)` returning `b` raised to `e`, for `e >= 0`, "
             "recursively — no loop and no `Math.pow`. `power(b, 0)` is 1. Write the "
             "whole method where you see `____`.",
             _jm("    static long power(int b, int e) {\n"
                 "        if (e == 0) return 1;\n"
                 "        return b * power(b, e - 1);\n"
                 "    }",
                 "        int b = sc.nextInt();\n"
                 "        int e = sc.nextInt();\n"
                 "        System.out.println(power(b, e));"),
             "    static long power(int b, int e) {\n"
             "        if (e == 0) return 1;\n"
             "        return b * power(b, e - 1);\n"
             "    }",
             [_case(f"{b}\n{e}", b ** e)
              for (b, e) in ((2, 10), (5, 0), (3, 4), (7, 1), (2, 30))],
             hints=["Base case: anything to the power 0 is 1.",
                    "Recursive case: `b` times `b` to the power `e - 1`.",
                    "Return `long`, so the 2^30 case does not overflow."]),
    ],
    quiz=[
        _jq("Which of these is a case where recursion is genuinely the clearest code?",
            ["Euclid's gcd — the swap-and-remainder step is the definition",
             "Fibonacci",
             "Factorial",
             "Summing 1 to n"],
            0,
            "Factorial and summation are one-line loops. `gcd`'s iterative version needs a "
            "temp and a swap; the recursion is literally the mathematical statement."),
        _jq("`static int factorial(int n)` gives wrong answers from about n = 13. Why?",
            ["13! exceeds int's ~2.1 billion range and silently wraps",
             "The recursion gets too deep",
             "Because the base case is wrong",
             "Because factorial is undefined past 12"],
            0,
            "`long` reaches 20!; past that you need `BigInteger`. The recursion depth of 13 is "
            "nothing — overflow is the limit here."),
    ],
))

# --- 10.3 Recursion over arrays --------------------------------------------

_M10.append(_jlesson(
    "m10-arrays", "Recursion over arrays",
    "Shrink by an index, not by copying — and get the base case exactly right.",
    """
An array cannot get smaller, so you pass an **index** that marks where the
remaining problem starts. "The rest of the array from `i`" is the smaller
problem.

```java
static int sumFrom(int[] a, int i) {
    if (i == a.length) return 0;          // nothing left: the empty sum is 0
    return a[i] + sumFrom(a, i + 1);
}
// call it as sumFrom(a, 0)
```

**The base case is `i == a.length`, not `a.length - 1`.** Think of it as "have
I run off the end?" rather than "am I on the last element?". Stopping at
`a.length - 1` silently drops the final element, and the answer looks almost
right — which makes it much harder to spot than a crash.

**The identity value matters.** An empty sum is `0`; an empty product would be
`1`; an empty count is `0`. Same rule as module 1's accumulator seeding.

**Maximum needs a different base case,** because there is no sensible "maximum
of nothing":

```java
static int maxFrom(int[] a, int i) {
    if (i == a.length - 1) return a[i];   // ONE element left: it wins
    int rest = maxFrom(a, i + 1);
    return a[i] > rest ? a[i] : rest;
}
```

Here `a.length - 1` **is** right, because the base case is "exactly one element
remains". The base case follows from the problem, not from a habit — that is
the actual lesson.

**Searching** returns as soon as it knows, which is a natural fit:

```java
static int indexOf(int[] a, int target, int i) {
    if (i == a.length) return -1;         // ran off the end
    if (a[i] == target) return i;         // found it
    return indexOf(a, target, i + 1);
}
```

**A word of honesty.** Every one of these is an ordinary `for` loop in
disguise, and the loop is faster (no frames) and safer (no stack limit). They
are here because they are the clearest possible practice at picking a base case
and shrinking a problem — and because the next lesson's binary search and Part
12's tree traversals are recursion you cannot easily write as a loop.

**Do not pass `Arrays.copyOfRange(a, 1, a.length)`** to shrink the array. It is
tempting and it works, but it copies the whole tail on every call — O(n²) time
and O(n²) allocation for what should be O(n). Pass the index.
""",
    warmup=[
        _jq("`sumFrom` with the base case `if (i == a.length - 1) return 0;` does what?",
            ["Silently omits the last element from the total",
             "Throws ArrayIndexOutOfBoundsException",
             "Works correctly",
             "Loops forever"],
            0,
            "It stops one step early and returns the identity instead of the last element. "
            "An almost-right answer is harder to notice than a crash."),
        _jq("Why does the recursive maximum stop at `i == a.length - 1` while the sum stops at `i == a.length`?",
            ["There is no maximum of an empty array, but the sum of nothing is 0",
             "It is an arbitrary style choice",
             "Because max returns int and sum returns long",
             "Because max is not really recursive"],
            0,
            "The base case comes from the problem. Sum has an identity value; max does not, so "
            "its simplest answerable case is one element."),
    ],
    exercises=[
        _je("j10-arr-sum", "Total, recursively",
            "`sumFrom` should total the array from index `i` onward. Replace `____` "
            "with the base case.",
            _jm("    static int sumFrom(int[] a, int i) {\n"
                "        if (i == a.length) return 0;\n"
                "        return a[i] + sumFrom(a, i + 1);\n"
                "    }",
                _RD_ARR + "        System.out.println(sumFrom(a, 0));"),
            "if (i == a.length) return 0;",
            [_acase(a, sum(a)) for a in ([1, 2, 3, 4], [7], [-5, 5, -5])],
            hints=["The simplest case is 'there is nothing left'.",
                   "That is when the index has run past the last valid position.",
                   "`if (i == a.length) return 0;` — 0 is the sum of nothing."],
            difficulty="Medium"),

        _je("j10-arr-max", "Largest, recursively",
            "`maxFrom` should return the largest element from index `i` onward. "
            "Replace `____` with the recursive case — compare this element against "
            "the answer for the rest.",
            _jm("    static int maxFrom(int[] a, int i) {\n"
                "        if (i == a.length - 1) return a[i];\n"
                "        int rest = maxFrom(a, i + 1);\n"
                "        if (a[i] > rest) return a[i];\n"
                "        return rest;\n"
                "    }",
                _RD_ARR + "        System.out.println(maxFrom(a, 0));"),
            "        int rest = maxFrom(a, i + 1);\n"
            "        if (a[i] > rest) return a[i];\n"
            "        return rest;",
            [_acase(a, max(a)) for a in ([3, 9, 2], [-4, -11, -7], [5], [1, 2, 3, 4])],
            hints=["Ask for the maximum of everything after `i`, then compare.",
                   "Store the recursive answer in a local — calling it twice would double the "
                   "work for nothing.",
                   "Return whichever of `a[i]` and `rest` is larger."],
            difficulty="Medium"),

        _jfix("j10-arr-offby", "One element short",
              "`sumFrom` should total the whole array. Its answer is always missing "
              "exactly the last element. Fix the base case.",
              _jm("    static int sumFrom(int[] a, int i) {\n"
                  "        if (i == a.length - 1) return 0;\n"
                  "        return a[i] + sumFrom(a, i + 1);\n"
                  "    }",
                  _RD_ARR + "        System.out.println(sumFrom(a, 0));"),
              _jm("    static int sumFrom(int[] a, int i) {\n"
                  "        if (i == a.length) return 0;\n"
                  "        return a[i] + sumFrom(a, i + 1);\n"
                  "    }",
                  _RD_ARR + "        System.out.println(sumFrom(a, 0));"),
              [_acase(a, sum(a)) for a in ([1, 2, 3, 4], [7], [-5, 5, 10])],
              hints=["At `i == a.length - 1` there is still one element to add.",
                     "The stopping point is 'the index has run off the end'.",
                     "`if (i == a.length) return 0;`"],
              difficulty="Medium"),

        _jch("j10-arr-search", "Search, recursively", "Medium",
             "Write `indexOf(int[] a, int target, int i)` returning the first index at "
             "or after `i` holding `target`, or `-1` if there is none. Two base cases "
             "and one recursive call — no loop. Write the whole method where you see "
             "`____`.",
             _jm("    static int indexOf(int[] a, int target, int i) {\n"
                 "        if (i == a.length) return -1;\n"
                 "        if (a[i] == target) return i;\n"
                 "        return indexOf(a, target, i + 1);\n"
                 "    }",
                 _RD_ARR
                 + "        int target = sc.nextInt();\n"
                   "        System.out.println(indexOf(a, target, 0));"),
             "    static int indexOf(int[] a, int target, int i) {\n"
             "        if (i == a.length) return -1;\n"
             "        if (a[i] == target) return i;\n"
             "        return indexOf(a, target, i + 1);\n"
             "    }",
             [_akcase(a, t, a.index(t) if t in a else -1)
              for (a, t) in (([4, 7, 4, 9], 4), ([4, 7, 4, 9], 9),
                             ([4, 7], 5), ([1], 1), ([3, 3, 3], 3))],
             hints=["Two base cases: ran off the end (-1), and found it (i).",
                    "Order matters — check the end-of-array case FIRST, or `a[i]` throws.",
                    "The recursive case just moves on: `return indexOf(a, target, i + 1);`"]),
    ],
    quiz=[
        _jq("Why pass an index rather than `Arrays.copyOfRange(a, 1, a.length)`?",
            ["Copying the tail on every call makes an O(n) job O(n²) in time and memory",
             "copyOfRange does not compile in a recursive method",
             "The index version is easier to read",
             "There is no difference"],
            0,
            "Each call would copy nearly the whole array. The index costs one `int` per frame "
            "and shares the original."),
        _jq("You need the product of an array recursively. What is the base case's return value?",
            ["1 — the identity for multiplication",
             "0", "a[0]", "It has no base case"],
            0,
            "Same rule as module 1's accumulator seeding: 0 for sums, 1 for products. "
            "Returning 0 here would zero out every answer."),
    ],
))

# --- 10.4 Recursion over strings -------------------------------------------

_M10.append(_jlesson(
    "m10-strings", "Recursion over strings",
    "`substring` makes the problem smaller — at a price worth knowing.",
    """
A String genuinely can be made smaller, because `substring` hands you a new
one. That makes string recursion read very cleanly:

```java
static String reverse(String s) {
    if (s.length() <= 1) return s;                    // base: 0 or 1 chars
    return reverse(s.substring(1)) + s.charAt(0);     // rest reversed, then the first
}
```

Read the recursive case as: "reverse everything after the first character, then
put the first character on the end". The leap of faith does the rest.

**Counting** follows the same shape, with a number instead of text:

```java
static int countOf(String s, char c) {
    if (s.length() == 0) return 0;                     // empty: none
    int rest = countOf(s.substring(1), c);
    if (s.charAt(0) == c) return 1 + rest;
    return rest;
}
```

**Palindrome** peels a character off *each* end, which needs **two** base
cases:

```java
static boolean isPal(String s) {
    if (s.length() <= 1) return true;                  // 0 or 1: trivially yes
    if (s.charAt(0) != s.charAt(s.length() - 1)) return false;
    return isPal(s.substring(1, s.length() - 1));      // strip both ends
}
```

Writing only `if (s.length() == 0)` looks like it covers the base, and it does
not: an odd-length palindrome shrinks down to **one** character, and then
`s.substring(1, 0)` throws `StringIndexOutOfBoundsException` because the start
is past the end. `<= 1` covers both. It is the most common bug in recursive
string code, and it only shows up on odd-length input.

**The cost.** Every `substring` allocates a new String and copies its
characters, so `reverse` on an n-character string does O(n²) copying — the
same quadratic you met in module 6, wearing a different hat. The iterative
`StringBuilder` version from module 8 is O(n) and is what you would actually
ship.

So string recursion is for learning and for genuinely tree-shaped problems, not
for reversing text in production. Saying that in an interview — "here is the
recursive one, and here is why I would write the iterative one" — is worth more
than either version alone.

**An index-based alternative** avoids the copying entirely, and is the right
shape once you care:

```java
static boolean isPal(String s, int i, int j) {
    if (i >= j) return true;
    if (s.charAt(i) != s.charAt(j)) return false;
    return isPal(s, i + 1, j - 1);
}
```

That is module 7's two-pointer check with the loop replaced by recursion — same
O(n) time, same O(1) data, just O(n) stack.
""",
    warmup=[
        _jq("`isPal` with only `if (s.length() == 0) return true;` fails how, on `\"aba\"`?",
            ["It shrinks to one character, then `substring(1, 0)` throws",
             "It returns false", "It loops forever", "It works fine"],
            0,
            "Stripping both ends of a 3-character string leaves 1, and stripping both ends of "
            "*that* asks for `substring(1, 0)` — start past end. `<= 1` is the fix."),
        _jq("Recursive `reverse` using `substring(1)` costs how much?",
            ["O(n²) — every call allocates and copies a new string",
             "O(n)", "O(log n)", "O(1)"],
            0,
            "Each of the n calls copies up to n characters. The `StringBuilder` version from "
            "module 8 is O(n)."),
    ],
    exercises=[
        _je("j10-str-rev", "Reverse, recursively",
            "`reverse` should return the line reversed. Replace `____` with the "
            "recursive case.",
            _jm("    static String reverse(String s) {\n"
                "        if (s.length() <= 1) return s;\n"
                "        return reverse(s.substring(1)) + s.charAt(0);\n"
                "    }",
                "        String line = sc.nextLine();\n"
                "        System.out.println(reverse(line));"),
            "return reverse(s.substring(1)) + s.charAt(0);",
            [_scase(s, s[::-1]) for s in ("hello", "ab", "x", "a b c")],
            hints=["Reverse everything after the first character…",
                   "…then stick the first character on the END.",
                   "`return reverse(s.substring(1)) + s.charAt(0);`"],
            difficulty="Medium"),

        _je("j10-str-count", "Count a character",
            "`countOf` should count how many times `c` appears in `s`. Replace "
            "`____` with the base case.",
            _jm("    static int countOf(String s, char c) {\n"
                "        if (s.length() == 0) return 0;\n"
                "        int rest = countOf(s.substring(1), c);\n"
                "        if (s.charAt(0) == c) return 1 + rest;\n"
                "        return rest;\n"
                "    }",
                "        String line = sc.nextLine();\n"
                "        System.out.println(countOf(line, 'a'));"),
            "if (s.length() == 0) return 0;",
            # No zero-byte stdin case: `sc.nextLine()` would throw before the
            # program ran. The empty-string base case is still exercised — every
            # input recurses down to it.
            [_scase(s, s.count("a")) for s in ("banana", "xyz", "aaa", "a")],
            hints=["The simplest string is the empty one.",
                   "It contains no occurrences of anything.",
                   "`if (s.length() == 0) return 0;`"],
            difficulty="Intro"),

        _jfix("j10-str-palbase", "It throws on odd lengths",
              "`isPal` works for even-length input and throws "
              "`StringIndexOutOfBoundsException` on anything odd — try `aba`. One base "
              "case is too narrow.",
              _jm("    static boolean isPal(String s) {\n"
                  "        if (s.length() == 0) return true;\n"
                  "        if (s.charAt(0) != s.charAt(s.length() - 1)) return false;\n"
                  "        return isPal(s.substring(1, s.length() - 1));\n"
                  "    }",
                  "        String line = sc.nextLine();\n"
                  "        System.out.println(isPal(line));"),
              _jm("    static boolean isPal(String s) {\n"
                  "        if (s.length() <= 1) return true;\n"
                  "        if (s.charAt(0) != s.charAt(s.length() - 1)) return false;\n"
                  "        return isPal(s.substring(1, s.length() - 1));\n"
                  "    }",
                  "        String line = sc.nextLine();\n"
                  "        System.out.println(isPal(line));"),
              [_scase(s, _jbool(s == s[::-1]))
               for s in ("aba", "racecar", "abba", "hello", "x")],
              hints=["Trace `aba`: it strips both ends and calls itself with what?",
                     "A one-character string is a palindrome, and stripping both ends of it "
                     "asks for `substring(1, 0)`.",
                     "`if (s.length() <= 1) return true;`"],
              difficulty="Medium"),

        _jch("j10-str-remove", "Remove every occurrence", "Medium",
             "Write `removeChar(String s, char c)` returning `s` with every `c` "
             "removed, recursively — no loop and no `replace`. Write the whole method "
             "where you see `____`.",
             _jm("    static String removeChar(String s, char c) {\n"
                 '        if (s.length() == 0) return "";\n'
                 "        String rest = removeChar(s.substring(1), c);\n"
                 "        if (s.charAt(0) == c) return rest;\n"
                 "        return s.charAt(0) + rest;\n"
                 "    }",
                 "        String line = sc.nextLine();\n"
                 "        System.out.println(removeChar(line, 'a'));"),
             "    static String removeChar(String s, char c) {\n"
             '        if (s.length() == 0) return "";\n'
             "        String rest = removeChar(s.substring(1), c);\n"
             "        if (s.charAt(0) == c) return rest;\n"
             "        return s.charAt(0) + rest;\n"
             "    }",
             [_scase(s, _remove_char(s, "a"))
              for s in ("banana", "aaa", "xyz", "a b a", "abcabc")],
             hints=['Base case: the empty string comes back as `""`.',
                    "Solve the rest first, then decide whether to keep the first character.",
                    "`s.charAt(0) + rest` — a char plus a String concatenates, giving a String.",
                    "A string of nothing but `c` must come back empty, and a string with no "
                    "`c` must come back unchanged."]),
    ],
    quiz=[
        _jq("Why does recursive string work usually get rewritten with indices in real code?",
            ["`substring` copies, so index recursion is O(n) instead of O(n²)",
             "Because substring is deprecated",
             "Because recursion cannot take two parameters",
             "It doesn't — substring is free"],
            0,
            "Passing `i` and `j` into the same string shares one object, exactly as passing an "
            "index into an array does."),
        _jq("`s.charAt(0) + rest` where `rest` is a String produces…",
            ["a String — the char is converted, because one operand is a String",
             "an int", "a char", "a compile error"],
            0,
            "Module 6's `+` rule: if either operand is a String, the whole expression "
            "concatenates. `s.charAt(0) + s.charAt(1)` — two chars — would be an int."),
    ],
))

# --- 10.5 Divide and conquer ------------------------------------------------

_M10.append(_jlesson(
    "m10-divide", "Divide and conquer",
    "Recursive binary search, fast exponentiation, and where recursion earns its keep.",
    """
The recursions so far shrank the problem by **one**, which a loop does just as
well. Divide and conquer shrinks it by **half**, or splits it into independent
halves — and that is where recursion stops being an exercise.

**Binary search, recursively** — module 3's algorithm with the loop replaced by
a call:

```java
static int bsearch(int[] a, int target, int lo, int hi) {
    if (lo > hi) return -1;                           // base: empty range
    int mid = lo + (hi - lo) / 2;
    if (a[mid] == target) return mid;                 // base: found
    if (a[mid] < target) return bsearch(a, target, mid + 1, hi);
    return bsearch(a, target, lo, mid - 1);
}
```

Every detail from module 3 survives: the overflow-safe midpoint, and `mid ± 1`
so the range always shrinks. The `while (lo <= hi)` condition becomes the base
case `if (lo > hi) return -1;` — the same test, inverted. Depth is O(log n), so
about 30 frames for a billion elements. Perfectly safe.

**Fast exponentiation** turns O(n) into O(log n) by squaring:

```java
static long power(int b, int e) {
    if (e == 0) return 1;
    long half = power(b, e / 2);                       // ONE call, reused
    if (e % 2 == 0) return half * half;
    return half * half * b;
}
```

The line that matters is `long half = power(b, e / 2);`. Writing
`power(b, e/2) * power(b, e/2)` instead computes the same thing twice and
collapses the whole saving back to O(n) — the same mistake naive Fibonacci
makes, in miniature.

**Splitting into halves** is the shape of merge sort, quicksort and every tree
algorithm:

```java
static int maxIn(int[] a, int lo, int hi) {
    if (lo == hi) return a[lo];                        // one element
    int mid = lo + (hi - lo) / 2;
    int left = maxIn(a, lo, mid);
    int right = maxIn(a, mid + 1, hi);
    return left > right ? left : right;
}
```

For a maximum this is pure showmanship — it is still O(n) and a loop is
simpler. But the *shape* is exactly merge sort's, and it is worth writing once
in a context simple enough that only the recursion is new.

**When is recursion the right tool?** When the data or the problem is itself
branching. Trees, graphs, nested structures, backtracking, and divide-and-
conquer sorts have no natural loop form — writing them iteratively means
managing an explicit stack yourself, which is strictly worse. Linear scans do
not qualify, which is why lessons 10.3 and 10.4 were honest about being
practice rather than production.
""",
    warmup=[
        _jq("Recursive binary search's base case `if (lo > hi) return -1;` corresponds to what in the loop version?",
            ["The loop condition `while (lo <= hi)` failing",
             "The `mid ± 1` adjustment",
             "The overflow-safe midpoint",
             "Nothing — the loop version has no equivalent"],
            0,
            "Same test, inverted: the loop continues while `lo <= hi`, and the recursion stops "
            "when that stops being true."),
        _jq("Why store `power(b, e/2)` in a local instead of writing it twice?",
            ["Writing it twice recomputes the whole subtree, making it O(n) again",
             "Because Java forbids two identical calls",
             "For readability only",
             "To avoid overflow"],
            0,
            "It is naive Fibonacci's mistake in miniature: the shared subproblem must be "
            "computed once and reused, or the halving buys nothing."),
    ],
    exercises=[
        _je("j10-div-bsearch", "Binary search, recursively",
            "The array arrives **sorted**. `bsearch` should return the index of "
            "`target` or `-1`. Replace `____` with the two recursive calls.",
            _jm("    static int bsearch(int[] a, int target, int lo, int hi) {\n"
                "        if (lo > hi) return -1;\n"
                "        int mid = lo + (hi - lo) / 2;\n"
                "        if (a[mid] == target) return mid;\n"
                "        if (a[mid] < target) return bsearch(a, target, mid + 1, hi);\n"
                "        return bsearch(a, target, lo, mid - 1);\n"
                "    }",
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        System.out.println(bsearch(a, target, 0, n - 1));"),
            "        if (a[mid] < target) return bsearch(a, target, mid + 1, hi);\n"
            "        return bsearch(a, target, lo, mid - 1);",
            [_akcase(a, t, _bsearch_rec(a, t, 0, len(a) - 1))
             for (a, t) in (([1, 3, 5, 7, 9], 7), ([1, 3, 5, 7, 9], 1),
                            ([1, 3, 5, 7, 9], 4), ([2], 2), ([2], 8))],
            hints=["Too small at `mid` means the answer is to the right: `mid + 1` to `hi`.",
                   "Otherwise it is to the left: `lo` to `mid - 1`.",
                   "`mid ± 1` in both, or the range never shrinks and you recurse forever."],
            difficulty="Medium"),

        _je("j10-div-power", "Exponentiation by squaring",
            "`power` should compute `b^e` in O(log e) by halving the exponent. "
            "Replace `____` with the line that computes the half-power exactly once.",
            _jm("    static long power(int b, int e) {\n"
                "        if (e == 0) return 1;\n"
                "        long half = power(b, e / 2);\n"
                "        if (e % 2 == 0) return half * half;\n"
                "        return half * half * b;\n"
                "    }",
                "        int b = sc.nextInt();\n"
                "        int e = sc.nextInt();\n"
                "        System.out.println(power(b, e));"),
            "long half = power(b, e / 2);",
            [_case(f"{b}\n{e}", _fast_pow(b, e))
             for (b, e) in ((2, 10), (3, 5), (5, 0), (2, 40), (7, 1))],
            hints=["One recursive call, whose result is used twice.",
                   "The exponent halves, and integer division handles the odd case — the "
                   "leftover `b` is multiplied back in below.",
                   "`long half = power(b, e / 2);`"],
            difficulty="Hard"),

        _jch("j10-div-max", "Maximum by splitting", "Medium",
             "Write `maxIn(int[] a, int lo, int hi)` returning the largest element in "
             "the inclusive range `lo..hi`, by splitting the range in half and taking "
             "the larger of the two answers. Write the whole method where you see "
             "`____`.",
             _jm("    static int maxIn(int[] a, int lo, int hi) {\n"
                 "        if (lo == hi) return a[lo];\n"
                 "        int mid = lo + (hi - lo) / 2;\n"
                 "        int left = maxIn(a, lo, mid);\n"
                 "        int right = maxIn(a, mid + 1, hi);\n"
                 "        if (left > right) return left;\n"
                 "        return right;\n"
                 "    }",
                 _RD_ARR + "        System.out.println(maxIn(a, 0, n - 1));"),
             "    static int maxIn(int[] a, int lo, int hi) {\n"
             "        if (lo == hi) return a[lo];\n"
             "        int mid = lo + (hi - lo) / 2;\n"
             "        int left = maxIn(a, lo, mid);\n"
             "        int right = maxIn(a, mid + 1, hi);\n"
             "        if (left > right) return left;\n"
             "        return right;\n"
             "    }",
             [_acase(a, max(a))
              for a in ([3, 9, 2, 7], [-4, -11, -7], [5], [1, 2, 3, 4, 5, 6])],
             hints=["Base case: a range holding exactly one element is that element.",
                    "Split at `mid`, then recurse on `lo..mid` and `mid + 1..hi`.",
                    "The left half must include `mid` and the right half must start after it, "
                    "or the two halves overlap and the recursion never terminates.",
                    "This is merge sort's skeleton with the merging replaced by a comparison."]),
    ],
    quiz=[
        _jq("Recursive binary search on a billion elements uses about how many stack frames?",
            ["30", "1,000,000,000", "1,000", "30,000"],
            0,
            "log₂(10⁹) ≈ 30. Halving the problem keeps the depth logarithmic, which is why "
            "divide-and-conquer recursion never overflows the stack."),
        _jq("Which problem genuinely needs recursion rather than a loop?",
            ["Walking a tree — the data itself branches",
             "Summing an array",
             "Reversing a string",
             "Finding a maximum"],
            0,
            "Branching data has no natural loop form; iterating it means managing your own "
            "explicit stack, which is strictly worse than letting the call stack do it."),
    ],
))

# --- 10.6 Recursion versus iteration ---------------------------------------

_M10.append(_jlesson(
    "m10-vs", "Recursion versus iteration",
    "What it costs, when it breaks, and the one-line fix for the exponential case.",
    """
**Every recursion has an iterative equivalent** and vice versa — recursion is
never *required*. It is a choice about clarity, made against three real costs.

**1. Stack frames.** Each call allocates a frame holding parameters, locals and
a return address. The JVM's stack is finite — typically a few hundred kilobytes,
so roughly **10,000 to 50,000 frames** before `StackOverflowError`. A loop uses
one frame no matter how many iterations. So:

- Depth O(log n) — binary search, fast power: **completely safe**, 30 frames.
- Depth O(n) with n in the thousands: fine.
- Depth O(n) with n in the millions: it will crash.

**2. Java does not do tail-call optimisation.** In some languages a recursive
call in tail position is compiled into a jump, costing no stack. Java does not
do this and there are no current plans to, so a "tail-recursive" Java method
still overflows at the same depth as any other. Do not rely on it.

**3. Overlapping subproblems.** Naive Fibonacci is exponential because
`fib(n-2)` is recomputed inside `fib(n-1)`, and again below that, on and on:

```
fib(5) calls fib(4) and fib(3)
fib(4) calls fib(3) and fib(2)      <- fib(3) computed twice already
```

`fib(30)` makes over 2.7 million calls to compute 31 distinct values.

**Memoization is the fix, and it is four lines.** Keep an array of answers
already computed:

```java
static long[] memo;                              // 0 means "not computed yet"

static long fib(int n) {
    if (n < 2) return n;
    if (memo[n] != 0) return memo[n];             // already known
    memo[n] = fib(n - 1) + fib(n - 2);            // compute once, store
    return memo[n];
}
```

Every value is computed exactly once, so it is **O(n)** — 2.7 million calls
become about 60. That single change is the entire idea behind dynamic
programming (Part 12 of the roadmap): recursion plus a table of remembered
answers.

The `!= 0` sentinel works here because no Fibonacci number past `F(0)` is zero.
In general you want a separate "computed" flag or a fill value that cannot be a
real answer — the same sentinel-choosing problem as module 1's `-1`.

**Choosing, in practice:**

| Use a loop when | Use recursion when |
|---|---|
| The problem is linear | The data or problem branches |
| Depth would be O(n) and n is large | Depth is O(log n) |
| The loop is not more complicated | The loop needs its own explicit stack |
| It is a hot path | Clarity matters more than a few frames |

Trees, graphs, backtracking, divide-and-conquer sorts, nested structures:
recursion. Scanning a list: a loop.
""",
    warmup=[
        _jq("Roughly how deep can Java recurse before StackOverflowError?",
            ["Tens of thousands of frames", "About 100", "Millions", "Unlimited"],
            0,
            "It varies with frame size and the `-Xss` setting, but 10,000–50,000 is the "
            "practical range. O(log n) depths never come close."),
        _jq("Java optimises a tail-recursive call into a jump, so it uses no stack.",
            ["False — Java does not do tail-call optimisation",
             "True, since Java 8",
             "True, but only for static methods",
             "True, but only with -Xss"],
            0,
            "Some languages guarantee it; Java does not. A tail-recursive Java method "
            "overflows at exactly the same depth as any other."),
    ],
    exercises=[
        _je("j10-vs-calls", "Count the waste",
            "`fib` is the naive version, and `calls` counts how many times it is "
            "entered. Print the value and then the call count, so you can see the "
            "explosion. Replace `____` with the line that records a call.",
            _jm("    static int calls = 0;\n"
                "\n"
                "    static int fib(int n) {\n"
                "        calls++;\n"
                "        if (n < 2) return n;\n"
                "        return fib(n - 1) + fib(n - 2);\n"
                "    }",
                "        int k = sc.nextInt();\n"
                "        int value = fib(k);\n"
                "        System.out.println(value);\n"
                "        System.out.println(calls);"),
            "        calls++;",
            [_case(k, _nl(_fib(k), _fib_calls(k))) for k in (5, 10, 1, 20)],
            hints=["Every entry into the method is one call, including the base cases.",
                   "So the increment is the first statement of the method.",
                   "`calls++;` — and notice the count for n = 20 versus the answer."],
            difficulty="Medium"),

        _je("j10-vs-memo", "Remember what you computed",
            "`fib` now has a `memo` array. Replace `____` with the line that stores "
            "the freshly computed answer before returning it.",
            _jm("    static long[] memo;\n"
                "\n"
                "    static long fib(int n) {\n"
                "        if (n < 2) return n;\n"
                "        if (memo[n] != 0) return memo[n];\n"
                "        memo[n] = fib(n - 1) + fib(n - 2);\n"
                "        return memo[n];\n"
                "    }",
                "        int k = sc.nextInt();\n"
                "        memo = new long[k + 2];\n"
                "        System.out.println(fib(k));"),
            "        memo[n] = fib(n - 1) + fib(n - 2);",
            [_case(k, _fib(k)) for k in (10, 1, 0, 50, 70)],
            hints=["Compute the sum and put it in the table, indexed by `n`.",
                   "The line below already returns `memo[n]`, so you only have to fill it.",
                   "`memo[n] = fib(n - 1) + fib(n - 2);` — and note that `fib(70)` finishes "
                   "instantly, where the naive version would take longer than this course."],
            difficulty="Medium"),

        _jfix("j10-vs-nomemo", "It stores nothing",
              "This is meant to be the memoized Fibonacci, but it never writes to the "
              "table — so it is still exponential and the hidden test for `fib(45)` "
              "times out. Fix it so each value is computed once.",
              _jm("    static long[] memo;\n"
                  "\n"
                  "    static long fib(int n) {\n"
                  "        if (n < 2) return n;\n"
                  "        if (memo[n] != 0) return memo[n];\n"
                  "        return fib(n - 1) + fib(n - 2);\n"
                  "    }",
                  "        int k = sc.nextInt();\n"
                  "        memo = new long[k + 2];\n"
                  "        System.out.println(fib(k));"),
              _jm("    static long[] memo;\n"
                  "\n"
                  "    static long fib(int n) {\n"
                  "        if (n < 2) return n;\n"
                  "        if (memo[n] != 0) return memo[n];\n"
                  "        memo[n] = fib(n - 1) + fib(n - 2);\n"
                  "        return memo[n];\n"
                  "    }",
                  "        int k = sc.nextInt();\n"
                  "        memo = new long[k + 2];\n"
                  "        System.out.println(fib(k));"),
              [_case(k, _fib(k)) for k in (10, 45, 60)],
              hints=["The lookup is there, but nothing ever fills the table.",
                     "Compute the sum INTO `memo[n]`, then return it.",
                     "`memo[n] = fib(n - 1) + fib(n - 2); return memo[n];`"],
              difficulty="Medium"),

        _jch("j10-vs-both", "Both versions, same answer", "Medium",
             "Write two methods that each compute `1 + 2 + … + n`: `sumLoop(int n)` "
             "with a `for` loop, and `sumRec(int n)` recursively. `main` prints both, "
             "on two lines — they must agree. Write both methods where you see "
             "`____`.",
             _jm("    static int sumLoop(int n) {\n"
                 "        int total = 0;\n"
                 "        for (int i = 1; i <= n; i++) total += i;\n"
                 "        return total;\n"
                 "    }\n"
                 "\n"
                 "    static int sumRec(int n) {\n"
                 "        if (n == 0) return 0;\n"
                 "        return n + sumRec(n - 1);\n"
                 "    }",
                 "        int k = sc.nextInt();\n"
                 "        System.out.println(sumLoop(k));\n"
                 "        System.out.println(sumRec(k));"),
             "    static int sumLoop(int n) {\n"
             "        int total = 0;\n"
             "        for (int i = 1; i <= n; i++) total += i;\n"
             "        return total;\n"
             "    }\n"
             "\n"
             "    static int sumRec(int n) {\n"
             "        if (n == 0) return 0;\n"
             "        return n + sumRec(n - 1);\n"
             "    }",
             [_case(k, _nl(k * (k + 1) // 2, k * (k + 1) // 2))
              for k in (5, 1, 0, 100)],
             hints=["Two separate methods, both `static int`, both taking one `int`.",
                    "The loop version accumulates from 1 to n; the recursive one has a base "
                    "case at 0.",
                    "`n = 0` must give 0 from both — the loop never runs and the recursion "
                    "hits its base case immediately.",
                    "For n in the millions the recursive one would overflow the stack and the "
                    "loop would not. That difference is the whole lesson."]),
    ],
    quiz=[
        _jq("Memoizing naive Fibonacci changes its complexity from…",
            ["exponential to O(n)", "O(n²) to O(n)", "O(n) to O(log n)",
             "exponential to O(n²)"],
            0,
            "Each of the n values is computed exactly once and reused thereafter. That "
            "recursion-plus-a-table pattern is the whole of dynamic programming."),
        _jq("You must process a directory tree of unknown depth. Loop or recursion?",
            ["Recursion — the data branches, so a loop would need its own explicit stack",
             "A loop, always",
             "Recursion, but only if the depth is under 100",
             "Neither works in Java"],
            0,
            "Branching data is exactly the case recursion is for. The iterative version means "
            "pushing directories onto a stack by hand — the same algorithm, written worse."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m10_toolkit(a, target, k):
    return _nl(
        f"sum={sum(a)}",
        f"max={max(a)}",
        f"index={_bsearch_rec(a, target, 0, len(a) - 1)}",
        f"fact={__import__('math').factorial(k)}",
        f"fib={_fib(k)}",
        f"gcd={_gcd(a[0], a[len(a) - 1])}",
    )


_M10_CAP = _jcap(
    "Recursion toolkit",
    """
Six recursive methods and a `main` that only wires them up — the closing
project of the course.

Read a **sorted array of positive integers**, then a `target`, then a small
number `k` (0 ≤ k ≤ 20). Print:

```
sum=<total of the array, recursively>
max=<largest element, recursively>
index=<recursive binary search for target, or -1>
fact=<k!, recursively>
fib=<the kth Fibonacci number, with fib(0)=0 and fib(1)=1>
gcd=<gcd of the first and last elements, recursively>
```

Six methods, and **not one loop anywhere** — every method must recurse:

| Method | Base case |
|---|---|
| `sumFrom(a, i)` | `i == a.length` → 0 |
| `maxFrom(a, i)` | `i == a.length - 1` → `a[i]` |
| `bsearch(a, target, lo, hi)` | `lo > hi` → −1 |
| `factorial(k)` | `k <= 1` → 1 |
| `fib(k)` | `k < 2` → `k` |
| `gcd(a, b)` | `b == 0` → `a` |

Two things to get right:

- **`fact` and `fib` need `long`.** `20!` is about 2.4 × 10¹⁸, which fits a
  `long` and overflows an `int` many times over.
- **`fib` can stay naive.** `k` never exceeds 20, so the exponential version
  finishes instantly — but memoizing it (lesson 10.6) is a fair extra if you
  want it.

Notice how little is left in `main`: reading input and printing. That is what
Part 3 has been for.
""",
    _jch("j10-cap-toolkit", "Recursion toolkit", "Hard",
         "Write the six recursive methods where you see `____`, above `main`. "
         "`main` is already written and calls them in order. No loops.",
         _jm("    static int sumFrom(int[] a, int i) {\n"
             "        if (i == a.length) return 0;\n"
             "        return a[i] + sumFrom(a, i + 1);\n"
             "    }\n"
             "\n"
             "    static int maxFrom(int[] a, int i) {\n"
             "        if (i == a.length - 1) return a[i];\n"
             "        int rest = maxFrom(a, i + 1);\n"
             "        if (a[i] > rest) return a[i];\n"
             "        return rest;\n"
             "    }\n"
             "\n"
             "    static int bsearch(int[] a, int target, int lo, int hi) {\n"
             "        if (lo > hi) return -1;\n"
             "        int mid = lo + (hi - lo) / 2;\n"
             "        if (a[mid] == target) return mid;\n"
             "        if (a[mid] < target) return bsearch(a, target, mid + 1, hi);\n"
             "        return bsearch(a, target, lo, mid - 1);\n"
             "    }\n"
             "\n"
             "    static long factorial(int k) {\n"
             "        if (k <= 1) return 1;\n"
             "        return k * factorial(k - 1);\n"
             "    }\n"
             "\n"
             "    static long fib(int k) {\n"
             "        if (k < 2) return k;\n"
             "        return fib(k - 1) + fib(k - 2);\n"
             "    }\n"
             "\n"
             "    static int gcd(int a, int b) {\n"
             "        if (b == 0) return a;\n"
             "        return gcd(b, a % b);\n"
             "    }",
             _RD_ARR
             + "        int target = sc.nextInt();\n"
               "        int k = sc.nextInt();\n"
               '        System.out.println("sum=" + sumFrom(a, 0));\n'
               '        System.out.println("max=" + maxFrom(a, 0));\n'
               '        System.out.println("index=" + bsearch(a, target, 0, n - 1));\n'
               '        System.out.println("fact=" + factorial(k));\n'
               '        System.out.println("fib=" + fib(k));\n'
               '        System.out.println("gcd=" + gcd(a[0], a[n - 1]));'),
         "    static int sumFrom(int[] a, int i) {\n"
         "        if (i == a.length) return 0;\n"
         "        return a[i] + sumFrom(a, i + 1);\n"
         "    }\n"
         "\n"
         "    static int maxFrom(int[] a, int i) {\n"
         "        if (i == a.length - 1) return a[i];\n"
         "        int rest = maxFrom(a, i + 1);\n"
         "        if (a[i] > rest) return a[i];\n"
         "        return rest;\n"
         "    }\n"
         "\n"
         "    static int bsearch(int[] a, int target, int lo, int hi) {\n"
         "        if (lo > hi) return -1;\n"
         "        int mid = lo + (hi - lo) / 2;\n"
         "        if (a[mid] == target) return mid;\n"
         "        if (a[mid] < target) return bsearch(a, target, mid + 1, hi);\n"
         "        return bsearch(a, target, lo, mid - 1);\n"
         "    }\n"
         "\n"
         "    static long factorial(int k) {\n"
         "        if (k <= 1) return 1;\n"
         "        return k * factorial(k - 1);\n"
         "    }\n"
         "\n"
         "    static long fib(int k) {\n"
         "        if (k < 2) return k;\n"
         "        return fib(k - 1) + fib(k - 2);\n"
         "    }\n"
         "\n"
         "    static int gcd(int a, int b) {\n"
         "        if (b == 0) return a;\n"
         "        return gcd(b, a % b);\n"
         "    }",
         [_atkcase(a, t, k, _m10_toolkit(a, t, k))
          for (a, t, k) in (([1, 3, 5, 7, 9], 7, 5),
                            ([2, 4, 6, 8], 5, 0),
                            ([6], 6, 1),
                            ([12, 18, 24, 30], 24, 12),
                            ([1, 2, 3, 4, 5, 6, 7, 8], 1, 20))],
         hints=["Write them one at a time and check each line of output before moving on.",
                "`sumFrom` stops at `i == a.length` (nothing left, so 0); `maxFrom` stops at "
                "`i == a.length - 1` (one element left, so that element).",
                "`bsearch` is module 3's loop with `while (lo <= hi)` turned into the base "
                "case `if (lo > hi) return -1;` — keep the overflow-safe midpoint and the "
                "`mid ± 1`.",
                "`factorial` and `fib` must return `long`: 20! is about 2.4e18, far past int.",
                "`gcd(a, b)` recurses as `gcd(b, a % b)` and stops when `b` is 0. The "
                "arguments swap on every call.",
                "Not one of the six methods may contain a loop."]),
    example_io="stdin:  5\n        1 3 5 7 9\n        7\n        5\n\n"
               "stdout: sum=25\n        max=9\n        index=3\n        fact=120\n"
               "        fib=5\n        gcd=1",
    rubric=[
        "All six methods are recursive — no `for` and no `while` anywhere.",
        "`sumFrom` and `maxFrom` use the base cases the table specifies, so nothing is dropped.",
        "`bsearch` returns -1 for an absent target and uses the overflow-safe midpoint.",
        "`factorial` and `fib` return `long`, so `k = 20` is exact.",
        "`gcd` swaps its arguments and stops at `b == 0`.",
        "`main` contains only input reading and printing.",
        "It survives a one-element array and `k = 0`.",
    ],
)


_MODULES.append(_jmod(
    10, 3, "Methods and recursion",
    "Recursion basics",
    "Write a method that calls itself, pick base cases that are actually right, "
    "picture the call stack, and know when recursion is the clearest tool and when "
    "it is the wrong one.",
    """
Recursion comes last on purpose. You have written every one of these algorithms
as a loop already, so the question is no longer "how do I solve this?" but "what
does this way buy me?" — which is the only useful way to learn it.

The mechanics are small: a base case, a step that shrinks the problem, and the
leap of faith that the recursive call is already correct. What takes practice is
picking the base case (10.3's `i == a.length` versus `i == a.length - 1` is the
whole lesson in miniature) and recognising the shapes where recursion genuinely
beats a loop — halving, and branching data.

The module ends on the honest comparison: stack limits, no tail-call
optimisation, exponential blowup on overlapping subproblems, and the four-line
memoization that fixes it — which is also your first look at dynamic
programming.
""",
    _M10,
    capstone=_M10_CAP,
    objectives=[
        "Write a recursive method with a correct base case and a step that provably shrinks the problem.",
        "Explain the call stack, and predict output printed before versus after the recursive call.",
        "Write factorial, power, gcd, digit sum and Fibonacci recursively.",
        "Recurse over arrays and strings by passing an index, and pick the base case from the problem.",
        "Write recursive binary search and fast exponentiation, and say why their depth is O(log n).",
        "State recursion's three costs — frames, no tail-call optimisation, overlapping subproblems.",
        "Memoize an exponential recursion into a linear one, and name that as dynamic programming.",
    ],
    why="Trees, graphs, backtracking, and every divide-and-conquer sort are recursive by "
        "nature — Part 12 of the roadmap is built on this module. And memoized recursion "
        "is dynamic programming, which is the hardest thing interviews ask for.",
    est_minutes=330,
    glossary=[
        _jg("base case", "The input simple enough to answer without recursing. Every "
                         "recursion needs at least one, and picking it wrongly is the usual bug."),
        _jg("recursive case", "The branch that calls the method on a strictly smaller "
                              "problem."),
        _jg("call stack", "The stack of frames, one per active call, each holding that call's "
                          "parameters and locals."),
        _jg("stack frame", "One call's private workspace. Recursion depth is limited by how "
                           "many of these fit."),
        _jg("StackOverflowError", "Thrown when the stack runs out — typically after tens of "
                                  "thousands of frames."),
        _jg("recursive leap of faith", "Assume the recursive call is correct for the smaller "
                                       "problem, and check only the step you are writing."),
        _jg("divide and conquer", "Splitting a problem into halves and combining the results. "
                                  "Depth O(log n), so stack-safe."),
        _jg("tail call", "A recursive call that is the last thing a method does. Some "
                         "languages optimise it into a jump; Java does not."),
        _jg("overlapping subproblems", "The same sub-answer recomputed many times, as in naive "
                                       "Fibonacci. What makes it exponential."),
        _jg("memoization", "Caching computed answers in a table so each is computed once. "
                           "Turns exponential recursion linear, and is the core of dynamic "
                           "programming."),
    ],
    cheatsheet="""
```java
// --- the shape ----------------------------------------------------------
static T solve(problem p) {
    if (isSimple(p)) return answer;          // BASE CASE — must exist
    return combine(solve(smaller(p)));       // RECURSIVE CASE — must shrink
}

// --- before vs after the call (the stack, made visible) ----------------
static void updown(int n) {
    if (n == 0) return;
    System.out.println(n);      // on the way DOWN
    updown(n - 1);
    System.out.println(n);      // on the way BACK UP
}                                // updown(3) -> 3 2 1 1 2 3

// --- numbers ------------------------------------------------------------
static long factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }
static int  gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }
static int  digitSum(int n)   { return n < 10 ? n : n % 10 + digitSum(n/10); }
static int  fib(int n)        { return n < 2 ? n : fib(n-1) + fib(n-2); }  // EXPONENTIAL

// --- arrays: pass an INDEX, never a copy -------------------------------
static int sumFrom(int[] a, int i) {
    if (i == a.length) return 0;              // nothing left -> identity
    return a[i] + sumFrom(a, i + 1);
}
static int maxFrom(int[] a, int i) {
    if (i == a.length - 1) return a[i];        // ONE left -> that element
    int rest = maxFrom(a, i + 1);
    return a[i] > rest ? a[i] : rest;
}

// --- strings: substring shrinks, but copies (O(n^2)) -------------------
static String reverse(String s) {
    if (s.length() <= 1) return s;
    return reverse(s.substring(1)) + s.charAt(0);
}
static boolean isPal(String s) {
    if (s.length() <= 1) return true;          // <= 1, not == 0 !
    if (s.charAt(0) != s.charAt(s.length()-1)) return false;
    return isPal(s.substring(1, s.length() - 1));
}

// --- divide and conquer: depth O(log n), stack-safe --------------------
static int bsearch(int[] a, int t, int lo, int hi) {
    if (lo > hi) return -1;
    int mid = lo + (hi - lo) / 2;
    if (a[mid] == t) return mid;
    if (a[mid] < t) return bsearch(a, t, mid + 1, hi);
    return bsearch(a, t, lo, mid - 1);
}
static long power(int b, int e) {
    if (e == 0) return 1;
    long half = power(b, e / 2);               // ONE call, reused
    return e % 2 == 0 ? half * half : half * half * b;
}

// --- memoization: exponential -> linear --------------------------------
static long[] memo;
static long fib(int n) {
    if (n < 2) return n;
    if (memo[n] != 0) return memo[n];
    memo[n] = fib(n - 1) + fib(n - 2);
    return memo[n];
}
```
""",
    self_check=[
        "Can you name the two mandatory parts of a recursion and the three questions that check it?",
        "Can you predict the output of a method that prints both before and after its recursive call?",
        "Can you say why array sum stops at `i == a.length` but array max stops at `i == a.length - 1`?",
        "Can you write recursive binary search from memory, base case and midpoint included?",
        "Can you explain why `substring`-based recursion is O(n²) and what to pass instead?",
        "Can you state Java's recursion depth limit and say why binary search never approaches it?",
        "Can you memoize naive Fibonacci in four lines and say what that pattern is called?",
    ],
    review=[
        _jq("```java\nstatic int f(int n) { if (n == 0) return 0; return n + f(n - 2); }\n```\nWhat is `f(5)`?",
            ["StackOverflowError — 5 never reaches 0 by steps of 2",
             "9", "15", "6"],
            0,
            "Progress toward the base case is not enough; it has to actually REACH it. "
            "`n <= 0` would have been the safe guard."),
        _jq("Recursive `isPal` with the base case `s.length() == 0` fails on which input?",
            ["Any odd-length palindrome, such as \"aba\"",
             "Any even-length string",
             "The empty string",
             "It never fails"],
            0,
            "An odd-length palindrome shrinks to one character; stripping both ends of that "
            "asks for `substring(1, 0)`, which throws."),
        _jq("Which of these recursions is safe at n = 1,000,000?",
            ["Binary search — depth is about 20",
             "Recursive array sum — depth n",
             "Recursive string reverse — depth n",
             "None of them"],
            0,
            "Only logarithmic depth is safe at that scale. The linear-depth ones overflow "
            "somewhere in the tens of thousands."),
        _jq("Naive `fib(45)` versus memoized `fib(45)`: roughly how many calls each?",
            ["About 3.6 billion versus about 90",
             "The same",
             "About 45 versus about 45",
             "About 2,000 versus about 45"],
            0,
            "Exponential versus linear. That gap — from a four-line change — is why "
            "memoization is the first thing to reach for when a recursion recomputes."),
    ],
    milestone="The shipped course is complete. You can write recursion correctly, reason "
              "about the call stack, choose it over a loop for the right reasons, and "
              "memoize an exponential recursion — which is where dynamic programming, and "
              "Part 12 of the roadmap, begin.",
))
