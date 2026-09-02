# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 10 practice - recursion.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[10]`.
#
# Module 10 scope: base case and recursive case, the call stack, factorial and
# Fibonacci, recursion over arrays and strings, recursive binary search,
# recursion vs iteration, StackOverflowError.
#
# Like module 9, the blanked region is the METHOD beside `main`. Depths are kept
# small on purpose: the naive Fibonacci variant is capped at n = 25 so the
# judged run stays fast, and no exercise recurses deep enough to blow the stack.
# ---------------------------------------------------------------------------


def _p10ex(eid, title, difficulty, prompt, helpers, body, tests, hints,
           read=_RD_ARR):
    helpers = helpers.strip("\n")
    members = (helpers + "\n\n"
               + _MAIN_SIG + "\n"
               + "        Scanner sc = new Scanner(System.in);\n"
               + read
               + body.rstrip("\n") + "\n"
               + "    }")
    return _jch(eid, title, difficulty, prompt, _jcls(members), helpers,
                tests, hints)


_RD_N = "        int n = Integer.parseInt(sc.nextLine());\n"
_RD_W = "        String w = sc.nextLine();\n"

_A10 = ([3, 1, 4, 1, 5], [7], [-2, -3, -1], [0, 0], [10, 20, 30])


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _collatz(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


# --- Family A - the shape of a recursive method ------------------------------

_P10_A = _jfam(
    "p10-shape", "The shape",
    "A base case, and a step that gets closer to it.",
    """
Every recursive method has exactly two parts, and writing them in this order
stops most mistakes:

```java
static long factorial(int n) {
    if (n <= 1) return 1;              // 1. BASE CASE — stop, no recursion
    return n * factorial(n - 1);       // 2. RECURSIVE CASE — smaller problem
}
```

**Write the base case first.** It is the only thing that ends the recursion, and
a method that recurses without one runs until the JVM throws
`StackOverflowError` — not a hang, but not a useful error either.

**The recursive call must make progress.** `factorial(n - 1)` is closer to the
base case than `factorial(n)`. A call like `factorial(n)` inside `factorial`, or
one that shrinks only sometimes, is the same bug as a `while` loop that forgets
to advance.

**Trust the recursion.** The hardest habit to build is *not* tracing the whole
call tree in your head. Assume `factorial(n - 1)` already returns the right
answer, and ask only: given that, what is the answer for `n`? If the base case is
right and the step is right, the whole thing is right — that is induction, and it
is the only way recursive code stays writable as it gets deeper.

**Each call gets its own copy of the parameters.** That is why recursion works at
all: fifteen frames of `factorial` on the stack each have their own `n`. It is
also why deep recursion costs memory where a loop costs none.

> `long` rather than `int` for factorial: `13!` already overflows `int`. Watch
> for that whenever a result grows multiplicatively.
""",
    [
        _p10ex("j10-pr-factorial", "Factorial", "Intro",
               "Write `static long factorial(int n)` returning `n!`, with `0! = 1`. "
               "`main` reads one integer and prints the result.",
               """
    static long factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
""",
               """        System.out.println(factorial(n));""",
               [_lcase(str(n), __import__("math").factorial(n))
                for n in (5, 0, 1, 10, 20)],
               ["Base case first: `n` of `0` or `1` gives `1`.",
                "The recursive case multiplies `n` by the factorial of `n - 1`.",
                "The return type is `long`, because `13!` overflows an `int`.",
                "`n` of `0` must return `1`, not `0` — that is why the base case "
                "tests `n <= 1`."],
               read=_RD_N),

        _p10ex("j10-pr-sumto", "Sum of 1 to n", "Intro",
               "Write `static int sumTo(int n)` returning `1 + 2 + … + n`, and `0` when "
               "`n` is `0`.",
               """
    static int sumTo(int n) {
        if (n <= 0) {
            return 0;
        }
        return n + sumTo(n - 1);
    }
""",
               """        System.out.println(sumTo(n));""",
               [_lcase(str(n), n * (n + 1) // 2) for n in (5, 0, 1, 10, 100)],
               ["The base case returns `0`, since summing nothing gives nothing.",
                "The step adds `n` to the sum of everything below it.",
                "Compare with factorial: the base value differs because the "
                "operation differs — `0` is the identity for `+`, `1` for `*`.",
                "The closed form `n * (n + 1) / 2` would be O(1); this is the "
                "recursive version on purpose."],
               read=_RD_N),

        _p10ex("j10-pr-power", "Raise to a power", "Easy",
               "Write `static long power(int base, int exp)` returning `base` to the "
               "power `exp`, with `exp >= 0` and anything to the power `0` being `1`. "
               "`main` reads two integers on one line.",
               """
    static long power(int base, int exp) {
        if (exp == 0) {
            return 1;
        }
        return base * power(base, exp - 1);
    }
""",
               """        System.out.println(power(p, q));""",
               [_case(str(p) + " " + str(q) + "\n", p ** q)
                for (p, q) in ((2, 10), (5, 0), (1, 100), (3, 4), (7, 2))],
               ["The base case is `exp == 0`, returning `1`.",
                "The step multiplies `base` by `base` raised to one less.",
                "Only `exp` shrinks; `base` is passed through unchanged.",
                "Case two is anything to the power zero, and case three is one to a "
                "large power — both are handled by the base case and the step "
                "without special code."],
               read="        String[] pq = sc.nextLine().split(\" \");\n"
                    "        int p = Integer.parseInt(pq[0]);\n"
                    "        int q = Integer.parseInt(pq[1]);\n"),

        _p10ex("j10-pr-countdown", "Count down and stop", "Easy",
               "Write `static void countdown(int n)` that prints `n`, `n-1`, … down to "
               "`1`, one per line, and then prints `go`. If `n` is `0` it prints only "
               "`go`.",
               """
    static void countdown(int n) {
        if (n <= 0) {
            System.out.println("go");
            return;
        }
        System.out.println(n);
        countdown(n - 1);
    }
""",
               """        countdown(n);""",
               [_lcase(str(n), _nl(*([str(i) for i in range(n, 0, -1)] + ["go"])))
                for n in (5, 0, 1, 3, 10)],
               ["A `void` recursive method still needs a base case — it just "
                "returns nothing.",
                "The base case prints `go` and then `return;` with no value.",
                "Print `n` BEFORE recursing, or the numbers come out ascending.",
                "That ordering is the whole difference between printing on the way "
                "down and on the way back up."],
               read=_RD_N),

        _p10ex("j10-pr-gcd", "Greatest common divisor", "Medium",
               "Write `static int gcd(int a, int b)` using Euclid's algorithm: the gcd "
               "of `a` and `b` is the gcd of `b` and `a % b`, and the gcd of `a` and `0` "
               "is `a`. `main` reads two positive integers on one line.",
               """
    static int gcd(int a, int b) {
        if (b == 0) {
            return a;
        }
        return gcd(b, a % b);
    }
""",
               """        System.out.println(gcd(p, q));""",
               [_case(str(p) + " " + str(q) + "\n", _gcd(p, q))
                for (p, q) in ((12, 18), (7, 1), (100, 75), (9, 9), (17, 5))],
               ["The base case is `b == 0`, and it returns `a`.",
                "The step swaps: `gcd(b, a % b)`.",
                "The arguments move as a pair, which is what makes progress — "
                "`a % b` is always smaller than `b`.",
                "It works even when `a < b` initially: the first call simply swaps "
                "them round.",
                "This is the classic example of recursion being clearer than the "
                "loop."],
               read="        String[] pq = sc.nextLine().split(\" \");\n"
                    "        int p = Integer.parseInt(pq[0]);\n"
                    "        int q = Integer.parseInt(pq[1]);\n"),
    ])


# --- Family B - recursion over arrays ----------------------------------------

_P10_B = _jfam(
    "p10-arrays", "Recursing over an array",
    "Carry an index; the base case is running off the end.",
    """
An array has no natural "smaller array" to hand to the next call — taking a
subarray would copy it, which is O(n) per level and turns an O(n) job into
O(n²). Instead you pass the **same array** plus **an index saying where you
are**:

```java
static int sum(int[] a, int i) {
    if (i == a.length) return 0;          // base: past the end
    return a[i] + sum(a, i + 1);          // step: this one, plus the rest
}
```

and start it from `main` with `sum(a, 0)`.

**The base case is `i == a.length`**, not `i == a.length - 1`. Stopping one
early drops the last element — an off-by-one that produces a plausible-looking
wrong answer rather than a crash, which makes it worse.

**The empty case falls out for free.** An array of length `0` makes the very
first call the base case, so `sum` returns `0` without a special branch.

**Two directions are available**, and they are not the same:

```java
return a[i] + sum(a, i + 1);      // process on the way DOWN
return sum(a, i + 1) + a[i];      // for + it makes no difference…
```

…but for anything order-sensitive — printing, building a string, reversing — it
matters enormously. The last variant here uses two indices moving towards each
other rather than one moving forward, which is the recursive form of module 4's
two-pointer swap.

> **Every one of these is worse than the loop** in Java: same complexity, more
> memory, and a stack limit around a few thousand frames. They are here because
> the *technique* transfers to trees and graphs, where there is no easy loop.
""",
    [
        _p10ex("j10-pr-arr-sum", "Sum, recursively", "Easy",
               "Write `static int sum(int[] a, int i)` returning the total of "
               "`a[i]` onwards. `main` calls `sum(a, 0)`.",
               """
    static int sum(int[] a, int i) {
        if (i == a.length) {
            return 0;
        }
        return a[i] + sum(a, i + 1);
    }
""",
               """        System.out.println(sum(a, 0));""",
               [_acase(a, sum(a)) for a in _A10],
               ["The base case is running off the end: `i == a.length`.",
                "It returns `0`, the identity for addition.",
                "The step is this element plus the sum of everything after it.",
                "Do not create a subarray — pass the same `a` with `i + 1`."]),

        _p10ex("j10-pr-arr-max", "Maximum, recursively", "Medium",
               "Write `static int max(int[] a, int i)` returning the largest value from "
               "index `i` onwards. `main` calls `max(a, 0)` and the array is never "
               "empty.",
               """
    static int max(int[] a, int i) {
        if (i == a.length - 1) {
            return a[i];
        }
        int rest = max(a, i + 1);
        if (a[i] > rest) {
            return a[i];
        }
        return rest;
    }
""",
               """        System.out.println(max(a, 0));""",
               [_acase(a, max(a)) for a in _A10],
               ["Here the base case IS the last element, `i == a.length - 1`, "
                "because there is no identity value for 'maximum of nothing'.",
                "That is why the prompt guarantees a non-empty array.",
                "Compute the maximum of the rest ONCE into a local variable — "
                "calling `max(a, i + 1)` twice doubles the work at every level and "
                "makes it exponential.",
                "Then return whichever is larger.",
                "Seeding is not an issue here: the recursion never invents a value, "
                "so all-negative arrays work."]),

        _p10ex("j10-pr-arr-contains", "Search, recursively", "Easy",
               "Write `static boolean contains(int[] a, int i, int k)` returning whether "
               "`k` appears at index `i` or later. `main` calls `contains(a, 0, k)`.",
               """
    static boolean contains(int[] a, int i, int k) {
        if (i == a.length) {
            return false;
        }
        if (a[i] == k) {
            return true;
        }
        return contains(a, i + 1, k);
    }
""",
               """        System.out.println(contains(a, 0, k));""",
               [_akcase(a, k, _jbool(k in a))
                for (a, k) in (([3, 1, 4], 4), ([7], 8), ([-2, -3], -3),
                               ([0, 0], 0), ([10, 20, 30], 15))],
               ["Two base cases: off the end gives `false`, and a match gives "
                "`true`.",
                "Order them so the bounds check comes first, or a miss reads past "
                "the end.",
                "The step passes `i + 1` with the same `k`.",
                "Returning `true` immediately is the recursive equivalent of an "
                "early `break`."],
               read=_RD_ARR + "        int k = sc.nextInt();\n"),

        _p10ex("j10-pr-arr-count", "Count, recursively", "Easy",
               "Write `static int count(int[] a, int i, int k)` returning how many times "
               "`k` occurs at index `i` or later. `main` calls `count(a, 0, k)`.",
               """
    static int count(int[] a, int i, int k) {
        if (i == a.length) {
            return 0;
        }
        int rest = count(a, i + 1, k);
        if (a[i] == k) {
            return 1 + rest;
        }
        return rest;
    }
""",
               """        System.out.println(count(a, 0, k));""",
               [_akcase(a, k, a.count(k))
                for (a, k) in (([3, 1, 4, 1], 1), ([7], 8), ([-2, -3], -3),
                               ([0, 0, 0], 0), ([10, 20, 30], 15))],
               ["Unlike the search, this one cannot stop early — every element has "
                "to be looked at.",
                "The base case returns `0`.",
                "Add `1` to the count from the rest when this element matches, "
                "otherwise pass the count straight through.",
                "Compute the rest once into a local, not twice in two branches."],
               read=_RD_ARR + "        int k = sc.nextInt();\n"),

        _p10ex("j10-pr-arr-reverse", "Reverse, recursively", "Medium",
               "Write `static void reverse(int[] a, int lo, int hi)` that reverses the "
               "array in place by swapping the ends and recursing inwards. `main` calls "
               "`reverse(a, 0, n - 1)` and then prints the array.",
               """
    static void reverse(int[] a, int lo, int hi) {
        if (lo >= hi) {
            return;
        }
        int tmp = a[lo];
        a[lo] = a[hi];
        a[hi] = tmp;
        reverse(a, lo + 1, hi - 1);
    }
""",
               """        reverse(a, 0, n - 1);
        System.out.println(Arrays.toString(a));""",
               [_acase(list(a), _jarr(list(reversed(a)))) for a in _A10],
               ["Two indices this time, moving towards each other — the recursive "
                "form of module 4's two-pointer swap.",
                "The base case is `lo >= hi`: the pointers have met or crossed, so "
                "there is nothing left to swap.",
                "Swap first, then recurse with `lo + 1, hi - 1`.",
                "It is `void` and works by modifying the caller's array — module "
                "9's pass-by-value lesson, now load-bearing.",
                "A one-element array starts with `lo == hi` and correctly does "
                "nothing."]),
    ])


# --- Family C - recursion over strings ---------------------------------------

_W10 = ("hello", "a", "racecar", "abcba", "aabbcc")


_P10_C = _jfam(
    "p10-strings", "Recursing over a string",
    "`substring` makes a smaller problem — at a price.",
    """
Strings *do* have a natural smaller version, so the classic form is very tidy:

```java
static String reverse(String s) {
    if (s.length() <= 1) return s;                   // base
    return reverse(s.substring(1)) + s.charAt(0);    // step
}
```

That reads beautifully, and it is worth knowing that it is also **O(n²)**:
`substring` copies, so each of the `n` levels copies most of the string. The
index-carrying form from family B avoids that:

```java
static int countChar(String s, int i, char c) {
    if (i == s.length()) return 0;
    return (s.charAt(i) == c ? 1 : 0) + countChar(s, i + 1, c);
}
```

Both appear below, deliberately, so the difference is something you have written
rather than something you have read.

**The base case is usually `length() <= 1`** for the substring form, and
`i == s.length()` for the index form. Using `== 0` for the substring form also
works — `"".substring(1)` would throw, but you never reach it, because the check
happens first.

**Palindrome is the natural two-index case:**

```java
static boolean isPal(String s, int lo, int hi) {
    if (lo >= hi) return true;                       // met or crossed: done
    if (s.charAt(lo) != s.charAt(hi)) return false;
    return isPal(s, lo + 1, hi - 1);
}
```

Notice it has *two* base cases and one step, and that the "true" case is the one
where you run out of characters to compare — the same shape as the recursive
array reversal.
""",
    [
        _p10ex("j10-pr-str-reverse", "Reverse a string", "Easy",
               "Write `static String reverse(String s)` returning the string reversed, "
               "using `substring`. Do not use `StringBuilder`.",
               """
    static String reverse(String s) {
        if (s.length() <= 1) {
            return s;
        }
        return reverse(s.substring(1)) + s.charAt(0);
    }
""",
               """        System.out.println(reverse(w));""",
               [_lcase(w, w[::-1]) for w in _W10],
               ["The base case is a string of length `0` or `1`, which is its own "
                "reverse.",
                "The step reverses everything after the first character, then puts "
                "the first character at the END.",
                "`s.substring(1)` is the rest; `s.charAt(0)` is the first.",
                "Getting the order the other way round returns the string "
                "unchanged, which is an easy mistake to miss."],
               read=_RD_W),

        _p10ex("j10-pr-str-palindrome", "Palindrome, two indices", "Medium",
               "Write `static boolean isPal(String s, int lo, int hi)` returning whether "
               "the range reads the same both ways. `main` calls "
               "`isPal(w, 0, w.length() - 1)`.",
               """
    static boolean isPal(String s, int lo, int hi) {
        if (lo >= hi) {
            return true;
        }
        if (s.charAt(lo) != s.charAt(hi)) {
            return false;
        }
        return isPal(s, lo + 1, hi - 1);
    }
""",
               """        System.out.println(isPal(w, 0, w.length() - 1));""",
               [_lcase(w, _jbool(w == w[::-1])) for w in _W10],
               ["Two base cases: pointers met or crossed means `true`; a mismatch "
                "means `false`.",
                "Check `lo >= hi` FIRST, or a one-character string compares nothing "
                "and still needs an answer.",
                "The step moves both pointers inwards together.",
                "This carries no copying cost, unlike the substring form."],
               read=_RD_W),

        _p10ex("j10-pr-str-count", "Count a character", "Easy",
               "Write `static int countChar(String s, int i, char c)` returning how many "
               "times `c` appears from index `i` onwards. `main` reads the line, then a "
               "character on the next line, and calls `countChar(w, 0, c)`.",
               """
    static int countChar(String s, int i, char c) {
        if (i == s.length()) {
            return 0;
        }
        int rest = countChar(s, i + 1, c);
        if (s.charAt(i) == c) {
            return 1 + rest;
        }
        return rest;
    }
""",
               """        System.out.println(countChar(w, 0, c));""",
               [_l2case(w, ch, w.count(ch))
                for (w, ch) in (("hello", "l"), ("a", "a"), ("racecar", "z"),
                                ("aabbcc", "b"), ("abcba", "a"))],
               ["The index-carrying form, so no copying.",
                "Base case: `i == s.length()` returns `0`.",
                "Add one when this character matches, then add the count from the "
                "rest.",
                "Compare `char`s with `==`, not `equals`."],
               read=_RD_W + "        char c = sc.nextLine().charAt(0);\n"),

        _p10ex("j10-pr-str-remove", "Remove every copy of a character", "Medium",
               "Write `static String remove(String s, char c)` returning the string with "
               "every occurrence of `c` removed, using `substring` recursion.",
               """
    static String remove(String s, char c) {
        if (s.length() == 0) {
            return s;
        }
        String rest = remove(s.substring(1), c);
        if (s.charAt(0) == c) {
            return rest;
        }
        return s.charAt(0) + rest;
    }
""",
               """        System.out.println(remove(w, c));""",
               [_l2case(w, ch, w.replace(ch, ""))
                for (w, ch) in (("hello", "l"), ("a", "a"), ("racecar", "z"),
                                ("aabbcc", "b"), ("abcba", "a"))],
               ["Base case: the empty string has nothing to remove.",
                "Recurse on `s.substring(1)` first, then decide what to do with the "
                "first character.",
                "If it matches, return the rest unchanged; otherwise put it back on "
                "the front.",
                "`s.charAt(0) + rest` works because `rest` is a String, so `+` "
                "concatenates rather than adding numbers. Two chars added together "
                "would give an int.",
                "Removing everything leaves the empty string and prints a blank "
                "line."],
               read=_RD_W + "        char c = sc.nextLine().charAt(0);\n"),

        _p10ex("j10-pr-str-alldigits", "All digits?", "Easy",
               "Write `static boolean allDigits(String s, int i)` returning whether "
               "every character from index `i` onwards is a digit. `main` calls "
               "`allDigits(w, 0)`. An empty string counts as `true`.",
               """
    static boolean allDigits(String s, int i) {
        if (i == s.length()) {
            return true;
        }
        if (!Character.isDigit(s.charAt(i))) {
            return false;
        }
        return allDigits(s, i + 1);
    }
""",
               """        System.out.println(allDigits(w, 0));""",
               [_lcase(w, _jbool(w.isdigit() if w else True))
                for w in ("12345", "1a2", "0", "abc", "999")],
               ["Two base cases: reaching the end is `true`, and a non-digit is "
                "`false`.",
                "The bounds check has to come first.",
                "`Character.isDigit` is module 7's classifier.",
                "This is the recursive version of 'a flag that starts true' — the "
                "recursion carries the truth instead of a variable."],
               read=_RD_W),
    ])


# --- Family D - divide and conquer -------------------------------------------

_P10_D = _jfam(
    "p10-divide", "Divide and conquer",
    "Halve the problem instead of shrinking it by one.",
    """
Everything so far reduced the problem by **one** step per call, giving `n`
frames and O(n) work — the same as a loop. The interesting recursions cut the
problem in **half**:

```java
static int bsearch(int[] a, int lo, int hi, int k) {
    if (lo > hi) return -1;                        // empty range: not found
    int mid = lo + (hi - lo) / 2;
    if (a[mid] == k) return mid;
    if (a[mid] < k) return bsearch(a, mid + 1, hi, k);
    return bsearch(a, lo, mid - 1, k);
}
```

That is O(log n) frames, and it is the recursive twin of module 3's loop. The
same three bugs apply — `lo > hi` rather than `lo >= hi` for the base case,
`lo + (hi - lo) / 2` for the midpoint, and `mid ± 1` so the range always shrinks.

**Exponentiation by squaring** is the other classic:

```java
static long fastPower(int b, int e) {
    if (e == 0) return 1;
    long half = fastPower(b, e / 2);
    if (e % 2 == 0) return half * half;
    return half * half * b;
}
```

`power` in family A used `e` multiplications; this uses about `log2(e)`. The
detail that makes it fast is computing `half` **once into a variable**. Writing
`fastPower(b, e/2) * fastPower(b, e/2)` looks identical and is exponentially
slower, because it recomputes the same value at every level. That single
mistake is what separates a good answer from a bad one here, and it is the same
mistake the naive Fibonacci makes in the next family.

**Digit recursion** halves nothing but shrinks fast, since dividing by ten
removes a digit each time — so `countDigits` and `digitSum` are O(number of
digits), not O(n).
""",
    [
        _p10ex("j10-pr-bsearch", "Binary search, recursively", "Medium",
               "The array arrives sorted ascending. Write "
               "`static int bsearch(int[] a, int lo, int hi, int k)` returning the index "
               "of `k` or `-1`. `main` calls `bsearch(a, 0, n - 1, k)`.",
               """
    static int bsearch(int[] a, int lo, int hi, int k) {
        if (lo > hi) {
            return -1;
        }
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == k) {
            return mid;
        }
        if (a[mid] < k) {
            return bsearch(a, mid + 1, hi, k);
        }
        return bsearch(a, lo, mid - 1, k);
    }
""",
               """        System.out.println(bsearch(a, 0, n - 1, k));""",
               [_akcase(a, k, (a.index(k) if k in a else -1))
                for (a, k) in (([1, 3, 5, 7, 9], 7), ([1, 3, 5, 7, 9], 1),
                               ([1, 3, 5, 7, 9], 4), ([42], 42),
                               ([1, 2, 3, 4, 5, 6], 6))],
               ["The base case is an EMPTY range: `lo > hi`, not `lo >= hi`.",
                "With `>=` a single-element range would never be examined, and case "
                "four is exactly that.",
                "Midpoint: `lo + (hi - lo) / 2`, which cannot overflow.",
                "Recurse on `mid + 1, hi` or `lo, mid - 1` — never on `mid` itself, "
                "or the range stops shrinking.",
                "The array is passed unchanged; only the bounds move."],
               read=_RD_ARR + "        int k = sc.nextInt();\n"),

        _p10ex("j10-pr-fastpower", "Power by squaring", "Hard",
               "Write `static long fastPower(int base, int exp)` using exponentiation by "
               "squaring, with `exp >= 0`. Compute the half-power **once** into a local "
               "variable.",
               """
    static long fastPower(int base, int exp) {
        if (exp == 0) {
            return 1;
        }
        long half = fastPower(base, exp / 2);
        if (exp % 2 == 0) {
            return half * half;
        }
        return half * half * base;
    }
""",
               """        System.out.println(fastPower(p, q));""",
               [_case(str(p) + " " + str(q) + "\n", p ** q)
                for (p, q) in ((2, 10), (5, 0), (1, 100), (3, 5), (2, 30))],
               ["Base case: exponent `0` returns `1`.",
                "Recurse on `exp / 2`, which is integer division.",
                "Store the result in a local `long half` — calling it twice would "
                "make this exponential rather than logarithmic.",
                "For an even exponent the answer is `half * half`; for an odd one "
                "multiply by `base` once more, because integer division lost the "
                "remainder.",
                "Case five is 2^30, which fits in a `long` comfortably but would be "
                "slow with the family A version."],
               read="        String[] pq = sc.nextLine().split(\" \");\n"
                    "        int p = Integer.parseInt(pq[0]);\n"
                    "        int q = Integer.parseInt(pq[1]);\n"),

        _p10ex("j10-pr-countdigits", "How many digits?", "Easy",
               "Write `static int countDigits(int n)` returning how many decimal digits "
               "a non-negative `n` has. `0` has one digit.",
               """
    static int countDigits(int n) {
        if (n < 10) {
            return 1;
        }
        return 1 + countDigits(n / 10);
    }
""",
               """        System.out.println(countDigits(n));""",
               [_lcase(str(n), len(str(n))) for n in (12345, 0, 7, 100, 999999)],
               ["Dividing by ten removes the last digit, which is the step.",
                "The base case is a single-digit number, `n < 10`, returning `1`.",
                "Using `n == 0` as the base case instead makes `countDigits(0)` "
                "return `0`, which the brief says is wrong.",
                "Each level adds one to the count from the rest."],
               read=_RD_N),

        _p10ex("j10-pr-digitsum", "Add up the digits", "Easy",
               "Write `static int digitSum(int n)` returning the sum of the decimal "
               "digits of a non-negative `n`.",
               """
    static int digitSum(int n) {
        if (n == 0) {
            return 0;
        }
        return n % 10 + digitSum(n / 10);
    }
""",
               """        System.out.println(digitSum(n));""",
               [_lcase(str(n), sum(int(d) for d in str(n)))
                for n in (12345, 0, 7, 100, 999999)],
               ["`n % 10` is the last digit; `n / 10` is everything before it.",
                "Base case `n == 0` returning `0` works here, because summing no "
                "digits gives zero — and it makes `digitSum(0)` correctly `0`.",
                "Contrast with the previous variant, where the same base case would "
                "have been wrong. The right base case depends on the question.",
                "Case four is `100`, whose digits sum to `1`."],
               read=_RD_N),

        _p10ex("j10-pr-reversenum", "Reverse the digits", "Medium",
               "Write `static int reverseNum(int n, int acc)` that reverses the digits "
               "of a non-negative `n`, carrying the answer in `acc`. `main` calls "
               "`reverseNum(n, 0)`. So `1230` becomes `321`.",
               """
    static int reverseNum(int n, int acc) {
        if (n == 0) {
            return acc;
        }
        return reverseNum(n / 10, acc * 10 + n % 10);
    }
""",
               """        System.out.println(reverseNum(n, 0));""",
               [_lcase(str(n), int(str(n)[::-1])) for n in (1230, 0, 7, 100, 123456)],
               ["This one carries an ACCUMULATOR — the answer is built up in the "
                "parameter rather than on the way back out.",
                "Each step shifts `acc` left by one digit and adds the current last "
                "digit: `acc * 10 + n % 10`.",
                "The base case returns the accumulator, not `0`.",
                "`reverseNum(0, 0)` returns `0` immediately, which is correct.",
                "Trailing zeros vanish, so `1230` gives `321` — that is arithmetic, "
                "not a bug.",
                "This shape is called tail recursion: nothing happens after the "
                "recursive call returns."],
               read=_RD_N),
    ])


# --- Family E - cost, memoisation and pitfalls -------------------------------

def _fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


_P10_E = _jfam(
    "p10-cost", "What recursion costs",
    "The exponential trap, and the one-line fix.",
    """
```java
static long fib(int n) {
    if (n < 2) return n;
    return fib(n - 1) + fib(n - 2);       // TWO calls: the tree explodes
}
```

This is correct and catastrophically slow. `fib(n)` calls `fib(n-1)` and
`fib(n-2)`, each of which does the same again — about **2^n** calls in total.
`fib(40)` takes seconds; `fib(60)` would outlast you. The reason is that the
same subproblem is recomputed enormously many times: `fib(30)` alone is
recalculated over a million times inside `fib(45)`.

**Memoisation fixes it with one array:**

```java
static long fib(int n, long[] memo) {
    if (n < 2) return n;
    if (memo[n] != 0) return memo[n];      // already known
    memo[n] = fib(n - 1, memo) + fib(n - 2, memo);
    return memo[n];
}
```

Now each `n` is computed once and looked up thereafter — **O(n)** instead of
O(2^n). The critical line is the **store**: reading the cache without ever
writing it changes nothing, and is exactly the bug module 10's fix-the-bug
exercise ships.

**The general rule:** a recursion that branches and revisits the same arguments
needs memoisation. One that branches into genuinely different subproblems (like
binary search, or merge sort) does not.

**And the hard limit:** each frame consumes stack, and the JVM's default is a
few thousand deep. Recursion depth proportional to `n` is fine for `n` in the
thousands and fatal for `n` in the millions — where a loop would be untroubled.
`StackOverflowError` is an `Error`, not an `Exception`: you are not meant to
catch it, you are meant to not cause it.
""",
    [
        _p10ex("j10-pr-fib-naive", "Fibonacci, the slow way", "Easy",
               "Write `static long fib(int n)` the naive way — two recursive calls, no "
               "cache. `n` is at most 25, so it finishes quickly. `fib(0)` is `0` and "
               "`fib(1)` is `1`.",
               """
    static long fib(int n) {
        if (n < 2) {
            return n;
        }
        return fib(n - 1) + fib(n - 2);
    }
""",
               """        System.out.println(fib(n));""",
               [_lcase(str(n), _fib(n)) for n in (10, 0, 1, 20, 25)],
               ["The base case covers both `0` and `1` at once: `if (n < 2) return "
                "n;`.",
                "The step adds the two previous Fibonacci numbers.",
                "Two recursive calls per level is what makes the call tree "
                "exponential.",
                "The cap of 25 is there so the judge does not time out — try 45 "
                "yourself some time and watch it crawl."],
               read=_RD_N),

        _p10ex("j10-pr-fib-memo", "Fibonacci, remembered", "Medium",
               "Write `static long fib(int n, long[] memo)` that caches results. `main` "
               "allocates `new long[n + 2]` and calls `fib(n, memo)`. `n` can be up to "
               "90.",
               """
    static long fib(int n, long[] memo) {
        if (n < 2) {
            return n;
        }
        if (memo[n] != 0) {
            return memo[n];
        }
        memo[n] = fib(n - 1, memo) + fib(n - 2, memo);
        return memo[n];
    }
""",
               """        long[] memo = new long[n + 2];
        System.out.println(fib(n, memo));""",
               [_lcase(str(n), _fib(n)) for n in (10, 0, 1, 50, 90)],
               ["Check the cache before recursing, and STORE into it afterwards.",
                "Reading without writing is the classic bug — it compiles, it is "
                "correct, and it is still exponential.",
                "`memo[n] != 0` works as 'already computed' because no Fibonacci "
                "number past index 0 is zero.",
                "Assign to `memo[n]` and then return it, so each value is computed "
                "exactly once.",
                "Case five is `fib(90)`, which the naive version could never "
                "finish — and which still fits in a `long`."],
               read=_RD_N),

        _p10ex("j10-pr-collatz", "Collatz steps", "Medium",
               "Write `static int collatz(int n)` returning how many steps it takes to "
               "reach `1`: halve `n` when even, otherwise use `3n + 1`. `collatz(1)` is "
               "`0`.",
               """
    static int collatz(int n) {
        if (n == 1) {
            return 0;
        }
        if (n % 2 == 0) {
            return 1 + collatz(n / 2);
        }
        return 1 + collatz(3 * n + 1);
    }
""",
               """        System.out.println(collatz(n));""",
               [_lcase(str(n), _collatz(n)) for n in (6, 1, 27, 7, 19)],
               ["Base case `n == 1` returns `0` — no steps needed once you are "
                "there.",
                "Two recursive cases, chosen by `n % 2`.",
                "Each adds `1` for the step just taken.",
                "Note that the argument does NOT always shrink — `3n + 1` grows. "
                "Nobody has proved this always terminates, which is why it is a "
                "famous open problem rather than a normal recursion.",
                "Case three is 27, which takes 111 steps and climbs above 9000 on "
                "the way."],
               read=_RD_N),

        _p10ex("j10-pr-hanoi", "Counting the moves", "Medium",
               "Write `static long hanoi(int n)` returning the number of moves needed to "
               "solve the Towers of Hanoi with `n` discs: zero discs needs zero moves, "
               "and `n` discs needs the moves for `n - 1`, plus one, plus the moves for "
               "`n - 1` again.",
               """
    static long hanoi(int n) {
        if (n == 0) {
            return 0;
        }
        return 2 * hanoi(n - 1) + 1;
    }
""",
               """        System.out.println(hanoi(n));""",
               [_lcase(str(n), 2 ** n - 1) for n in (3, 0, 1, 10, 40)],
               ["Base case: zero discs, zero moves.",
                "The recurrence in the prompt is `hanoi(n-1) + 1 + hanoi(n-1)`, "
                "which simplifies to `2 * hanoi(n - 1) + 1`.",
                "Writing it as two separate calls would be exponentially slow for "
                "the same reason naive Fibonacci is — case five is `n = 40` and "
                "would not finish.",
                "The closed form is `2^n - 1`, which is what your answers should "
                "match.",
                "`long` matters: 2^40 - 1 overflows an `int`."],
               read=_RD_N),

        _p10ex("j10-pr-mutual", "Two methods calling each other", "Medium",
               "Write BOTH `static boolean isEven(int n)` and "
               "`static boolean isOdd(int n)` defined in terms of each other: zero is "
               "even, zero is not odd, and otherwise each defers to the other with "
               "`n - 1`. `n` is non-negative and at most 1000.",
               """
    static boolean isEven(int n) {
        if (n == 0) {
            return true;
        }
        return isOdd(n - 1);
    }

    static boolean isOdd(int n) {
        if (n == 0) {
            return false;
        }
        return isEven(n - 1);
    }
""",
               """        System.out.println(isEven(n));
        System.out.println(isOdd(n));""",
               [_lcase(str(n), _nl(_jbool(n % 2 == 0), _jbool(n % 2 == 1)))
                for n in (4, 0, 1, 999, 1000)],
               ["Each method has its own base case at `n == 0`, and they disagree: "
                "zero is even and not odd.",
                "Neither method calls itself — each calls the other. That is mutual "
                "recursion.",
                "The pair still terminates because `n` shrinks on every call, "
                "whichever method it lands in.",
                "It uses `n` stack frames, so a large `n` would overflow the stack "
                "where `n % 2` would not. The cap of 1000 keeps it safe.",
                "This is a real technique for parsers, but here it is mostly a "
                "demonstration that 'recursive' does not mean 'self-calling'."],
               read=_RD_N),
    ])


_PRACTICE[10] = [_P10_A, _P10_B, _P10_C, _P10_D, _P10_E]
