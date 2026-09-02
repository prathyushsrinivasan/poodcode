# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 9 practice - methods.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[9]`.
#
# Module 9 scope: defining and calling, the anatomy of a signature, parameters
# vs arguments, return values and void, pass-by-value for primitives / arrays /
# Strings, overloading, scope and shadowing, static, varargs.
#
# SHAPE: unlike every earlier module, the blanked region here is the METHOD (or
# methods) beside `main`, not the body of `main`. `main` is given and does the
# calling, so the exercise is exactly "write this method to this signature" -
# which is what the module is about.
# ---------------------------------------------------------------------------


def _p9ex(eid, title, difficulty, prompt, helpers, body, tests, hints,
          read=_RD_ARR):
    """`helpers` (the blanked region) sits beside a given `main` that calls it."""
    helpers = helpers.strip("\n")
    members = (helpers + "\n\n"
               + _MAIN_SIG + "\n"
               + "        Scanner sc = new Scanner(System.in);\n"
               + read
               + body.rstrip("\n") + "\n"
               + "    }")
    return _jch(eid, title, difficulty, prompt, _jcls(members), helpers,
                tests, hints)


_A9 = ([3, 1, 4, 1, 5], [7], [-2, -3, -1], [0, 0], [10, 20, 30, 40])


# --- Family A - writing the method -------------------------------------------

_P9_A = _jfam(
    "p9-write", "Writing the method",
    "A signature is a contract; fill in the body.",
    """
Everything you have written so far lived inside `main`. A method pulls a piece
of that out and gives it a name:

```java
static int sum(int[] a) {
    int total = 0;
    for (int i = 0; i < a.length; i++) total += a[i];
    return total;
}
```

Read the **signature** left to right, because every part is doing a job:

| Part | Means |
|---|---|
| `static` | belongs to the class, not to an object — so `main` can call it directly |
| `int` | the type this method hands back |
| `sum` | the name |
| `(int[] a)` | the parameter list: what it needs |

**`static` is not optional here.** `main` is `static`, and a static method has no
object to work with, so it can only call other static methods of the class
directly. Leaving it off gives you *"non-static method cannot be referenced from
a static context"* — probably the single most common compile error a Java
beginner meets. Module 11 explains what the alternative is.

**Use the parameter, not the outside world.** Inside the method you have
`a.length`, not `n` — `n` is a local variable of `main` and is invisible here.
That is the point of a parameter: the method works for *any* array it is handed,
not just the one `main` happens to have read.

**Every path must return.** A method declared `int` has to return an `int` on
every route through it, or it will not compile — Java checks this, it is not a
warning.

`main` is already written in each of these. Your job is the method above it.
""",
    [
        _p9ex("j9-pr-sum", "A method that adds up", "Intro",
              "Write `static int sum(int[] a)` returning the total of every element. "
              "`main` already reads the array and prints the result.",
              """
    static int sum(int[] a) {
        int total = 0;
        for (int i = 0; i < a.length; i++) {
            total += a[i];
        }
        return total;
    }
""",
              """        System.out.println(sum(a));""",
              [_acase(a, sum(a)) for a in _A9],
              ["The signature is given in the prompt — copy it exactly.",
               "Inside the method the array is called `a` and its length is "
               "`a.length`. There is no `n` here.",
               "Accumulate into a local variable and `return` it at the end.",
               "`static` is required, because `main` is static."]),

        _p9ex("j9-pr-max", "A method that picks the biggest", "Intro",
              "Write `static int max(int[] a)` returning the largest element. The array "
              "is never empty.",
              """
    static int max(int[] a) {
        int best = a[0];
        for (int i = 1; i < a.length; i++) {
            if (a[i] > best) {
                best = a[i];
            }
        }
        return best;
    }
""",
              """        System.out.println(max(a));""",
              [_acase(a, max(a)) for a in _A9],
              ["Module 1's running maximum, now with a name and a return type.",
               "Seed with `a[0]`, never `0` — case three is all negative.",
               "Start the loop at `1`.",
               "Return the answer; do not print it inside the method. `main` does "
               "the printing."]),

        _p9ex("j9-pr-countif", "A method that counts", "Easy",
              "Write `static int countAbove(int[] a, int k)` returning how many elements "
              "are strictly greater than `k`. `main` reads the array and then `k`.",
              """
    static int countAbove(int[] a, int k) {
        int count = 0;
        for (int i = 0; i < a.length; i++) {
            if (a[i] > k) {
                count++;
            }
        }
        return count;
    }
""",
              """        System.out.println(countAbove(a, k));""",
              [_akcase(a, k, sum(1 for x in a if x > k))
               for (a, k) in (([3, 1, 4, 1, 5], 2), ([7], 7), ([-2, -3, -1], -5),
                              ([0, 0], 0), ([10, 20, 30], 25))],
              ["Two parameters this time, in the order the signature gives.",
               "Both are available inside the method; neither is a global.",
               "**Strictly** greater is `>`. Case two has `k` equal to the only "
               "element and expects `0`.",
               "Return the count."],
              read=_RD_ARR + "        int k = sc.nextInt();\n"),

        _p9ex("j9-pr-contains-m", "A method that answers yes or no", "Easy",
              "Write `static boolean contains(int[] a, int k)` returning whether `k` "
              "appears anywhere in the array.",
              """
    static boolean contains(int[] a, int k) {
        for (int i = 0; i < a.length; i++) {
            if (a[i] == k) {
                return true;
            }
        }
        return false;
    }
""",
              """        System.out.println(contains(a, k));""",
              [_akcase(a, k, _jbool(k in a))
               for (a, k) in (([3, 1, 4], 4), ([7], 8), ([-2, -3], -3),
                              ([0, 0], 0), ([10, 20, 30], 15))],
              ["The return type is `boolean`, so return `true` or `false` — not "
               "`1` and `0`.",
               "`return` exits the method immediately, so you can return `true` "
               "from inside the loop and skip the rest.",
               "The final `return false;` after the loop is what handles 'never "
               "found', and the compiler requires it.",
               "No flag variable is needed once you return early."],
              read=_RD_ARR + "        int k = sc.nextInt();\n"),

        _p9ex("j9-pr-average", "A method that returns a different type", "Easy",
              "Write `static int average(int[] a)` returning the integer average "
              "(`total / length`, truncating toward zero). The array is never empty.",
              """
    static int average(int[] a) {
        int total = 0;
        for (int i = 0; i < a.length; i++) {
            total += a[i];
        }
        return total / a.length;
    }
""",
              """        System.out.println(average(a));""",
              [_acase(a, _jdiv(sum(a), len(a))) for a in _A9],
              ["Sum first, then divide once — not inside the loop.",
               "Divide by `a.length`, the method's own view of the size.",
               "Both operands are `int`, so this is integer division and truncates "
               "toward zero.",
               "Case three is all negative: `-6 / 3` is `-2`, and `-2 / 3` would be "
               "`0` rather than `-1`."]),
    ])


# --- Family B - return values and void ---------------------------------------

_P9_B = _jfam(
    "p9-return", "Returning, and not returning",
    "`void` does something; everything else hands something back.",
    """
A method either **produces a value** or **performs an effect**. Mixing the two
is usually a design smell, and the type says which you chose.

```java
static void printAll(int[] a) {          // effect: prints, hands back nothing
    for (int x : a) System.out.print(x + " ");
    System.out.println();
}

static int sum(int[] a) { ... return total; }   // value: hands back a number
```

**`void` means there is no value**, so `int x = printAll(a);` does not compile
and neither does `System.out.println(printAll(a))`. A bare `return;` is still
legal inside a `void` method — it means "stop here" — but `return something;` is
not.

**Prefer returning over printing.** A method that computes *and* prints can only
ever be used one way. A method that returns can be printed, compared, summed, or
tested. Every method in family A returned rather than printed for exactly that
reason, and every one of them is reusable because of it.

**Returning exits immediately.** Code after a `return` on the same path is
unreachable and will not compile — which is a useful check rather than a
nuisance.

**One method, one job.** If you find yourself wanting to return two things, that
is Java telling you it is two methods (or, from module 11, an object).
""",
    [
        _p9ex("j9-pr-void-print", "A method that only prints", "Intro",
              "Write `static void printAll(int[] a)` that prints every element separated "
              "by single spaces on one line. It returns nothing.",
              """
    static void printAll(int[] a) {
        for (int i = 0; i < a.length; i++) {
            System.out.print(a[i] + " ");
        }
        System.out.println();
    }
""",
              """        printAll(a);""",
              [_acase(a, _sp(a)) for a in _A9],
              ["The return type is `void`, so the method contains no `return "
               "value;` statement at all.",
               "It is called as a statement on its own line, not inside a "
               "`println`.",
               "Print each element with a trailing space, then end the line with a "
               "bare `System.out.println();`.",
               "`System.out.println(printAll(a))` would not compile — there is no "
               "value to print."]),

        _p9ex("j9-pr-bool-sorted", "A method that returns a boolean", "Easy",
              "Write `static boolean isSorted(int[] a)` returning whether the array is "
              "in non-decreasing order. Equal neighbours are allowed.",
              """
    static boolean isSorted(int[] a) {
        for (int i = 1; i < a.length; i++) {
            if (a[i - 1] > a[i]) {
                return false;
            }
        }
        return true;
    }
""",
              """        System.out.println(isSorted(a));""",
              [_acase(a, _jbool(all(a[i - 1] <= a[i] for i in range(1, len(a)))))
               for a in ([1, 2, 3], [7], [3, 2, 1], [1, 1, 2], [10, 20, 15])],
              ["Return `false` as soon as you find a pair out of order — there is "
               "no point continuing.",
               "If the loop finishes without returning, everything was in order, so "
               "`return true;` at the end.",
               "Non-decreasing allows equals, so the failing test is a strict `>`.",
               "A one-element array never enters the loop and is trivially sorted."]),

        _p9ex("j9-pr-string-return", "A method that returns a String", "Easy",
              "Write `static String describe(int n)` returning `\"negative\"`, `\"zero\"` "
              "or `\"positive\"`. `main` reads one integer and prints the result.",
              """
    static String describe(int n) {
        if (n < 0) {
            return "negative";
        }
        if (n == 0) {
            return "zero";
        }
        return "positive";
    }
""",
              """        System.out.println(describe(v));""",
              [_case(str(v) + "\n", "negative" if v < 0 else ("zero" if v == 0 else "positive"))
               for v in (5, 0, -3, 1, -100)],
              ["Three routes out, each returning a different `String`.",
               "Once you `return`, the rest of the method does not run — so no "
               "`else` is needed.",
               "The compiler insists every path returns, which is why the last line "
               "has no `if` around it.",
               "String literals go in double quotes."],
              read="        int v = Integer.parseInt(sc.nextLine());\n"),

        _p9ex("j9-pr-early-return", "Stop as soon as you know", "Easy",
              "Write `static int firstNegative(int[] a)` returning the index of the "
              "first negative value, or `-1` if there is none.",
              """
    static int firstNegative(int[] a) {
        for (int i = 0; i < a.length; i++) {
            if (a[i] < 0) {
                return i;
            }
        }
        return -1;
    }
""",
              """        System.out.println(firstNegative(a));""",
              [_acase(a, next((i for (i, x) in enumerate(a) if x < 0), -1))
               for a in ([3, 1, 4], [7], [-2, -3, -1], [0, 0], [1, -5, -6])],
              ["Return the index the moment you find a match.",
               "The `-1` after the loop is the 'not found' answer, the same "
               "convention as `indexOf`.",
               "No flag variable and no `break` are needed — returning does both "
               "jobs.",
               "Case five has two negatives and must report the first."]),

        _p9ex("j9-pr-two-methods", "Two methods, one job each", "Medium",
              "Write BOTH `static int sum(int[] a)` and "
              "`static int countNonZero(int[] a)`. `main` prints the sum on the first "
              "line and the count of non-zero elements on the second.",
              """
    static int sum(int[] a) {
        int total = 0;
        for (int i = 0; i < a.length; i++) {
            total += a[i];
        }
        return total;
    }

    static int countNonZero(int[] a) {
        int count = 0;
        for (int i = 0; i < a.length; i++) {
            if (a[i] != 0) {
                count++;
            }
        }
        return count;
    }
""",
              """        System.out.println(sum(a));
        System.out.println(countNonZero(a));""",
              [_acase(a, _nl(sum(a), sum(1 for x in a if x != 0))) for a in _A9],
              ["Two separate methods, each with one responsibility.",
               "They do not call each other and do not share state.",
               "Both take the same parameter type and both return an `int`.",
               "A single method returning both numbers is not possible — that is "
               "what module 11's objects are for.",
               "Order matters: `main` prints the sum first."]),
    ])


# --- Family C - pass-by-value ------------------------------------------------

_P9_C = _jfam(
    "p9-byvalue", "Java is pass-by-value. Always.",
    "What a method can change, and what it cannot.",
    """
This is the topic in module 9 that interviews probe hardest, and the confusion
is almost always caused by sloppy wording rather than genuine difficulty.

**Java passes everything by value.** The *value* of a variable is copied into
the parameter. For an `int` that value is the number; for an array or a String
that value is a **reference** — the address of the object.

So:

```java
static void tryIncrement(int x) { x = x + 1; }      // caller's int: UNCHANGED
static void fill(int[] a)       { a[0] = 99; }      // caller's array: CHANGED
static void reassign(int[] a)   { a = new int[3]; } // caller's array: UNCHANGED
```

Read those three again, because they are the whole lesson:

1. **A primitive parameter is a copy.** Assigning to it changes the copy.
   Nothing outside can be affected, which is why a `swap(int a, int b)` method
   is impossible in Java.
2. **An array parameter is a copy of the reference.** Both the copy and the
   original point at the *same object*, so writing *through* it —
   `a[0] = 99` — is visible to the caller.
3. **Reassigning the parameter repoints the copy only.** The caller's reference
   still points where it always did.

**"Java passes objects by reference" is wrong**, and it is wrong in a way that
predicts the wrong answer for case 3. The accurate sentence is *Java passes
references by value.* Being able to say that precisely is what the question is
testing.

**Strings behave like case 3, always.** `s = s + "!"` inside a method cannot
affect the caller, because Strings are immutable — there is no "write through
the reference" option at all.
""",
    [
        _p9ex("j9-pr-primitive", "The increment that does not stick", "Easy",
              "Write `static void tryIncrement(int x)` whose body is `x = x + 1;`. "
              "`main` prints the value before the call and after it.",
              """
    static void tryIncrement(int x) {
        x = x + 1;
    }
""",
              """        System.out.println(v);
        tryIncrement(v);
        System.out.println(v);""",
              [_case(str(v) + "\n", _nl(v, v)) for v in (5, 0, -3, 1, 100)],
              ["Write exactly the body described — the point is that it looks like "
               "it should work.",
               "`x` is a COPY of the caller's variable. Incrementing it changes "
               "the copy.",
               "So both printed lines are the same number.",
               "This is why Java cannot have a `swap(int, int)` method."],
              read="        int v = Integer.parseInt(sc.nextLine());\n"),

        _p9ex("j9-pr-array-write", "The array write that does stick", "Easy",
              "Write `static void bump(int[] a)` that adds `1` to every element. `main` "
              "prints the array afterwards.",
              """
    static void bump(int[] a) {
        for (int i = 0; i < a.length; i++) {
            a[i] = a[i] + 1;
        }
    }
""",
              """        bump(a);
        System.out.println(Arrays.toString(a));""",
              [_acase(list(a), _jarr([x + 1 for x in a])) for a in _A9],
              ["The parameter is a copy of the REFERENCE, but it points at the "
               "caller's array.",
               "Writing through it — `a[i] = ...` — modifies the one and only "
               "array.",
               "So `main` sees the change without anything being returned.",
               "The method is `void`; it works by effect, not by value."]),

        _p9ex("j9-pr-array-reassign", "The reassignment that does not", "Medium",
              "Write `static void replace(int[] a)` whose body assigns a brand-new "
              "array to the parameter: `a = new int[] {9, 9, 9};`. `main` prints the "
              "original array afterwards, unchanged.",
              """
    static void replace(int[] a) {
        a = new int[] {9, 9, 9};
    }
""",
              """        replace(a);
        System.out.println(Arrays.toString(a));""",
              [_acase(list(a), _jarr(a)) for a in _A9],
              ["Assigning to the parameter itself repoints only the local copy of "
               "the reference.",
               "The caller's variable still points at the original array, so nothing "
               "it sees has changed.",
               "Contrast with the previous variant, where you wrote THROUGH the "
               "reference instead of overwriting it.",
               "This single difference is why 'Java passes objects by reference' is "
               "the wrong sentence."]),

        _p9ex("j9-pr-swap-fail", "The swap that cannot work", "Medium",
              "Write `static void trySwap(int x, int y)` that swaps its two parameters "
              "using a temporary. `main` prints both values before and after calling "
              "it — and they will be unchanged.",
              """
    static void trySwap(int x, int y) {
        int tmp = x;
        x = y;
        y = tmp;
    }
""",
              """        System.out.println(p + " " + q);
        trySwap(p, q);
        System.out.println(p + " " + q);""",
              [_case(str(p) + " " + str(q) + "\n", _nl(f"{p} {q}", f"{p} {q}"))
               for (p, q) in ((1, 2), (0, 0), (-5, 5), (7, 7), (100, -100))],
              ["Write the swap correctly, with a temporary — it really does swap "
               "the parameters.",
               "But the parameters are copies, so the caller never sees it.",
               "Both printed lines are therefore identical.",
               "The working alternatives are to return a value, to pass an array, "
               "or (from module 11) to pass an object."],
              read="        String[] pq = sc.nextLine().split(\" \");\n"
                   "        int p = Integer.parseInt(pq[0]);\n"
                   "        int q = Integer.parseInt(pq[1]);\n"),

        _p9ex("j9-pr-string-param", "Strings cannot be changed either", "Medium",
              "Write `static void shout(String s)` whose body is `s = s + \"!\";`. "
              "`main` prints the string before and after the call.",
              """
    static void shout(String s) {
        s = s + "!";
    }
""",
              """        System.out.println(w);
        shout(w);
        System.out.println(w);""",
              [_lcase(w, _nl(w, w)) for w in ("hello", "a", "hi there", "x", "Java")],
              ["`s = s + \"!\"` builds a NEW string and points the local parameter "
               "at it.",
               "The caller's variable is untouched, exactly like the array "
               "reassignment.",
               "There is no 'write through the reference' option for a String, "
               "because Strings are immutable.",
               "So both lines print the original.",
               "To actually change it, the method must RETURN the new string."],
              read="        String w = sc.nextLine();\n"),
    ])


# --- Family D - overloading --------------------------------------------------

_P9_D = _jfam(
    "p9-overload", "Overloading",
    "Same name, different parameter lists.",
    """
Two methods may share a name as long as their **parameter lists differ** — in
number, in types, or in order:

```java
static int max(int a, int b)              { ... }
static int max(int a, int b, int c)       { ... }
static int max(int[] a)                   { ... }
```

The compiler picks one by looking at the arguments at the **call site**. That is
the key phrase: overload resolution happens at **compile time**, from the
*declared* types of the arguments. (Module 13's overriding is the opposite —
chosen at run time from the object's actual class. Being able to state that
contrast is the exam answer.)

**The return type is not part of the signature.** These two cannot coexist:

```java
static int  f(int x) { ... }
static long f(int x) { ... }     // does not compile — same parameter list
```

because a call like `f(3);` on its own would be ambiguous.

**Widening beats boxing beats varargs.** When several overloads could match,
Java prefers a plain widening conversion (`int` to `long`), then autoboxing
(`int` to `Integer`), and only falls back to a varargs method if nothing else
fits. So a varargs overload never accidentally steals a call a fixed-arity one
could take — which is exactly what makes family E's `sum(int...)` safe to add
alongside `sum(int, int)`.

The most useful everyday case is **the convenience overload**: a short form that
supplies a default and delegates to the full one.
""",
    [
        _p9ex("j9-pr-overload-max", "max for two, three, or many", "Medium",
              "Write three overloads: `static int max(int a, int b)`, "
              "`static int max(int a, int b, int c)` and `static int max(int[] a)`. "
              "`main` calls all three and prints three lines.",
              """
    static int max(int a, int b) {
        if (a > b) {
            return a;
        }
        return b;
    }

    static int max(int a, int b, int c) {
        return max(max(a, b), c);
    }

    static int max(int[] a) {
        int best = a[0];
        for (int i = 1; i < a.length; i++) {
            if (a[i] > best) {
                best = a[i];
            }
        }
        return best;
    }
""",
              """        System.out.println(max(a[0], a[1]));
        System.out.println(max(a[0], a[1], a[2]));
        System.out.println(max(a));""",
              [_acase(a, _nl(max(a[0], a[1]), max(a[0], a[1], a[2]), max(a)))
               for a in ([3, 1, 4], [7, 7, 7], [-2, -3, -1], [1, 2, 3],
                         [10, 20, 30, 40])],
              ["All three share the name `max` and differ only in parameters.",
               "The three-argument version should DELEGATE to the two-argument one "
               "rather than repeating the comparison — `max(max(a, b), c)`.",
               "That delegation is not recursion; it is one overload calling a "
               "different method that happens to share a name.",
               "The array version needs `a[0]` as its seed, as always.",
               "Every test array has at least three elements, so `main`'s calls are "
               "always valid."]),

        _p9ex("j9-pr-overload-area", "A convenience overload", "Easy",
              "Write `static int area(int w, int h)` returning `w * h`, and "
              "`static int area(int side)` for a square, which must **delegate** to the "
              "two-argument version rather than multiplying again.",
              """
    static int area(int w, int h) {
        return w * h;
    }

    static int area(int side) {
        return area(side, side);
    }
""",
              """        System.out.println(area(p, q));
        System.out.println(area(p));""",
              [_case(str(p) + " " + str(q) + "\n", _nl(p * q, p * p))
               for (p, q) in ((3, 4), (1, 1), (0, 5), (7, 7), (12, 2))],
              ["The one-argument form is the convenience: a square is a rectangle "
               "with equal sides.",
               "It should call `area(side, side)`, not write `side * side`.",
               "That way the real logic lives in exactly one place — if the "
               "calculation ever changes, only one method changes.",
               "The compiler tells the two apart purely by argument count."],
              read="        String[] pq = sc.nextLine().split(\" \");\n"
                   "        int p = Integer.parseInt(pq[0]);\n"
                   "        int q = Integer.parseInt(pq[1]);\n"),

        _p9ex("j9-pr-overload-type", "Same count, different types", "Medium",
              "Write `static String kind(int x)` returning `\"int\"` and "
              "`static String kind(double x)` returning `\"double\"`. `main` calls each "
              "with a literal of the matching type.",
              """
    static String kind(int x) {
        return "int";
    }

    static String kind(double x) {
        return "double";
    }
""",
              """        System.out.println(kind(v));
        System.out.println(kind(1.5));
        System.out.println(kind(2));""",
              [_case(str(v) + "\n", _nl("int", "double", "int")) for v in (5, 0, -3, 1, 100)],
              ["The parameter lists have the same LENGTH but different types, "
               "which is enough to overload on.",
               "`v` is an `int`, `1.5` is a `double` literal, and `2` is an `int` "
               "literal.",
               "So the output is `int`, `double`, `int` regardless of the value "
               "read.",
               "Note that Java would rather widen `int` to `double` than fail — so "
               "if you deleted the `int` overload, every call would print "
               "`double`."],
              read="        int v = Integer.parseInt(sc.nextLine());\n"),

        _p9ex("j9-pr-overload-order", "Order counts too", "Medium",
              "Write `static String tag(int a, String b)` returning `\"int-String\"` and "
              "`static String tag(String a, int b)` returning `\"String-int\"`. `main` "
              "calls each.",
              """
    static String tag(int a, String b) {
        return "int-String";
    }

    static String tag(String a, int b) {
        return "String-int";
    }
""",
              """        System.out.println(tag(v, "x"));
        System.out.println(tag("x", v));""",
              [_case(str(v) + "\n", _nl("int-String", "String-int"))
               for v in (5, 0, -3, 1, 100)],
              ["Same names, same number of parameters, same set of types — only "
               "the ORDER differs, and that is enough.",
               "The compiler matches the argument order at the call site.",
               "Neither method looks at its arguments at all; they just report "
               "which one was chosen.",
               "This is a useful trick for seeing overload resolution directly."],
              read="        int v = Integer.parseInt(sc.nextLine());\n"),

        _p9ex("j9-pr-overload-print", "Overloads that print", "Easy",
              "Write `static void show(int x)` printing `int: ` followed by the value, "
              "and `static void show(int[] a)` printing `array: ` followed by "
              "`Arrays.toString(a)`. `main` calls both.",
              """
    static void show(int x) {
        System.out.println("int: " + x);
    }

    static void show(int[] a) {
        System.out.println("array: " + Arrays.toString(a));
    }
""",
              """        show(a[0]);
        show(a);""",
              [_acase(a, _nl(f"int: {a[0]}", f"array: {_jarr(a)}")) for a in _A9],
              ["`int` and `int[]` are completely different types, so these overload "
               "cleanly.",
               "Both return `void` — return type plays no part in overloading, but "
               "it does not prevent it either.",
               "Mind the exact prefixes, including the space after the colon.",
               "`Arrays.toString` is needed for the array; plain concatenation "
               "would print its address."]),
    ])


# --- Family E - varargs and scope --------------------------------------------

_P9_E = _jfam(
    "p9-varargs", "Varargs and scope",
    "Any number of arguments, and where a name is visible.",
    """
## Varargs

```java
static int sum(int... xs) {
    int total = 0;
    for (int x : xs) total += x;
    return total;
}

sum();              // 0 arguments
sum(1, 2, 3);       // 3 arguments
sum(arr);           // an int[] works too
```

**Inside the method, `xs` is simply an `int[]`.** The `...` is compiler sugar:
Java collects the loose arguments into an array for you. That is why
`xs.length` works and why you can pass an existing array straight in.

**Three rules:**

- The varargs parameter must be **last**: `f(String label, int... xs)` is fine,
  `f(int... xs, String label)` is not — there would be no way to know where the
  varargs stopped.
- There can be **only one** per method, for the same reason.
- Zero arguments is legal, and gives you an **empty array**, not `null`. So
  `sum()` returns `0` without any special case.

## Scope and shadowing

A name declared inside a block is visible only within it:

```java
static int f(int x) {
    int y = 1;
    if (x > 0) {
        int z = 2;      // z exists only inside these braces
    }
    return y;           // z is not in scope here
}
```

**A parameter shadows a field of the same name** (module 11 makes this matter
properly, and is why `this.name = name;` exists). Within a method, the innermost
declaration wins, and Java forbids re-declaring a local name in a nested block —
so accidental shadowing between locals is a compile error rather than a silent
bug.
""",
    [
        _p9ex("j9-pr-varargs-sum", "Sum of any number of values", "Easy",
              "Write `static int sum(int... xs)` returning the total. `main` calls it "
              "with no arguments, with three literals, and with the array it read.",
              """
    static int sum(int... xs) {
        int total = 0;
        for (int x : xs) {
            total += x;
        }
        return total;
    }
""",
              """        System.out.println(sum());
        System.out.println(sum(1, 2, 3));
        System.out.println(sum(a));""",
              [_acase(a, _nl(0, 6, sum(a))) for a in _A9],
              ["The parameter is declared `int... xs` and behaves as an `int[]` "
               "inside.",
               "So the enhanced `for` works on it directly.",
               "Calling it with no arguments gives an EMPTY array, so the loop does "
               "not run and the answer is `0` — no special case needed.",
               "An existing `int[]` can be passed straight in, which is why "
               "`sum(a)` compiles."]),

        _p9ex("j9-pr-varargs-min", "Smallest of any number", "Medium",
              "Write `static int min(int... xs)` returning the smallest value, or "
              "`Integer.MAX_VALUE` when called with nothing.",
              """
    static int min(int... xs) {
        int best = Integer.MAX_VALUE;
        for (int x : xs) {
            if (x < best) {
                best = x;
            }
        }
        return best;
    }
""",
              """        System.out.println(min(a));
        System.out.println(min(4, 2, 9));
        System.out.println(min() == Integer.MAX_VALUE);""",
              [_acase(a, _nl(min(a), 2, "true")) for a in _A9],
              ["Seeding with `Integer.MAX_VALUE` is what makes the empty call "
               "behave sensibly — nothing can beat it, so it survives.",
               "This is the one situation where seeding from a sentinel rather than "
               "`xs[0]` is right, because there may be no `xs[0]`.",
               "The third line compares against `Integer.MAX_VALUE` and prints "
               "`true`.",
               "For a non-empty call the sentinel is harmless: the first real value "
               "always beats it."]),

        _p9ex("j9-pr-varargs-label", "A fixed parameter, then the rest", "Medium",
              "Write `static String join(String sep, int... xs)` returning the values "
              "joined by `sep`, with no trailing separator. Return the empty string when "
              "there are no values.",
              """
    static String join(String sep, int... xs) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < xs.length; i++) {
            if (i > 0) {
                sb.append(sep);
            }
            sb.append(xs[i]);
        }
        return sb.toString();
    }
""",
              """        System.out.println(join("-", a));
        System.out.println(join(",", 1, 2, 3));
        System.out.println("[" + join("-") + "]");""",
              [_acase(a, _nl("-".join(str(x) for x in a), "1,2,3", "[]"))
               for a in _A9],
              ["The varargs parameter must come LAST, after the separator.",
               "Inside, `xs` is an `int[]` — use an index loop so you know when you "
               "are on the first element.",
               "Add the separator before every value except the first, which avoids "
               "a trailing one.",
               "With no values the loop never runs and the builder is empty, so the "
               "third line prints `[]`.",
               "`StringBuilder` is module 8 and is the right tool here."]),

        _p9ex("j9-pr-scope-shadow", "Which one wins?", "Medium",
              "Write `static int shadow(int x)` that declares a local `int y = x * 2;`, "
              "then inside an `if (x > 0)` block declares `int z = y + 1;` and returns "
              "`z`, and otherwise returns `y`.",
              """
    static int shadow(int x) {
        int y = x * 2;
        if (x > 0) {
            int z = y + 1;
            return z;
        }
        return y;
    }
""",
              """        System.out.println(shadow(v));""",
              [_case(str(v) + "\n", (v * 2 + 1) if v > 0 else v * 2)
               for v in (5, 0, -3, 1, 100)],
              ["`y` is declared in the method body, so it is visible everywhere "
               "after its declaration, including inside the `if`.",
               "`z` is declared inside the `if` block and exists only there — "
               "returning it from outside would not compile.",
               "That is why the `return z;` has to be INSIDE the block.",
               "Case two and three are zero or negative and take the other route, "
               "returning `y`."],
              read="        int v = Integer.parseInt(sc.nextLine());\n"),

        _p9ex("j9-pr-static-counter", "A method that remembers", "Hard",
              "Declare `static int calls = 0;` beside the methods, and write "
              "`static int next()` which increments it and returns the new value. `main` "
              "calls it three times.",
              """
    static int calls = 0;

    static int next() {
        calls = calls + 1;
        return calls;
    }
""",
              """        System.out.println(next());
        System.out.println(next());
        System.out.println(next());""",
              [_case(str(v) + "\n", _nl(1, 2, 3)) for v in (5, 0, -3, 1, 100)],
              ["A `static` field belongs to the CLASS, so it survives between "
               "calls — unlike a local variable, which is created fresh each time.",
               "Declare it beside the methods, not inside one.",
               "Increment first, then return, so the first call reports `1`.",
               "The output is the same whatever the input, which is the point: the "
               "state lives in the class.",
               "This is the closest module 9 gets to an object. Module 11 does it "
               "properly."],
              read="        int v = Integer.parseInt(sc.nextLine());\n"),
    ])


_PRACTICE[9] = [_P9_A, _P9_B, _P9_C, _P9_D, _P9_E]
