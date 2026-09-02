# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 9 — Methods.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# The first module whose programs define anything alongside main(), which is
# why the course linter only permits `static ` from module 9 onward.
#
# The centre of gravity is lesson 9.3: Java is ALWAYS pass-by-value, and every
# confusing thing about passing arrays and strings around follows from that one
# sentence plus module 1's aliasing lesson. Everything else here — overloading,
# scope, varargs — is vocabulary by comparison.
# ---------------------------------------------------------------------------

_M9 = []


def _jm(helpers, body):
    """A `Main` with helper methods above a Scanner-opening `main`."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }"
    )


# --- 9.1 Defining and calling ----------------------------------------------

_M9.append(_jlesson(
    "m9-define", "Defining and calling a method",
    "The anatomy of a signature, and why everything here says `static`.",
    """
A method is a named, reusable block that takes inputs and (usually) hands back
a result.

```java
static int add(int a, int b) {
    return a + b;
}
```

Read it left to right:

| Part | Here | What it is |
|---|---|---|
| modifiers | `static` | how it is called — see below |
| return type | `int` | what it hands back; `void` for nothing |
| name | `add` | a verb, by convention: `add`, `findMax`, `isEmpty` |
| parameter list | `(int a, int b)` | the inputs, each with a declared type |
| body | `{ return a + b; }` | the work |

**The signature is the name plus the parameter types** — `add(int, int)`. The
return type is *not* part of it, which is why lesson 9.4's overloading rules
work the way they do.

**Why `static`?** `main` is `static`, meaning it belongs to the class rather
than to any object. A static method can only call other static methods directly,
so until Part 4 of the roadmap introduces objects, every helper you write beside
`main` must be `static` too. Leave it off and you get *"non-static method cannot
be referenced from a static context"* — one of the most common early Java
errors, and now you know exactly what it means.

**Calling** is the name plus arguments in parentheses:

```java
int total = add(3, 4);          // 7
System.out.println(add(1, 2));  // the result can be used directly
```

**Parameters versus arguments.** `a` and `b` in the definition are
*parameters* — placeholders. The `3` and `4` at the call site are *arguments* —
actual values. The distinction sounds pedantic until lesson 9.3, where the
whole question is what exactly gets copied into the parameters.

**Where methods go.** Inside the class, beside `main`, in any order — Java does
not care whether a method is defined above or below the code that calls it.

**Why bother.** Three reasons, in order of importance: a name for an idea
(`isPalindrome(s)` reads better than eight lines of loop), one place to fix a
bug, and one place to test. "Do not repeat yourself" is the third reason, not
the first.
""",
    warmup=[
        _jq("What is the *signature* of `static double area(int w, int h)`?",
            ["area(int, int)", "double area(int, int)", "area", "static double area"],
            0,
            "Name plus parameter types. The return type is deliberately excluded, which is "
            "why you cannot overload on return type alone."),
        _jq("You write `int twice(int x) { return x * 2; }` beside main and call it. What happens?",
            ["Compile error: non-static method cannot be referenced from a static context",
             "It works fine",
             "It works but returns 0",
             "Runtime NullPointerException"],
            0,
            "`main` is static, so it has no object to call an instance method on. Until "
            "objects arrive, helpers beside main must be `static`."),
    ],
    exercises=[
        _je("j9-def-call", "Call the helper",
            "`add` is already written. Replace `____` with the call that computes the "
            "sum of the two numbers read from input.",
            _jm("    static int add(int a, int b) {\n"
                "        return a + b;\n"
                "    }",
                "        int x = sc.nextInt();\n"
                "        int y = sc.nextInt();\n"
                "        System.out.println(add(x, y));"),
            "add(x, y)",
            [_case(f"{x}\n{y}", x + y) for (x, y) in ((3, 4), (-2, 10), (0, 0))],
            hints=["The name, then the arguments in parentheses.",
                   "Pass the two variables you just read.",
                   "`add(x, y)`"],
            difficulty="Intro"),

        _je("j9-def-body", "Write the body",
            "`square` should return its argument multiplied by itself. Replace "
            "`____` with the body.",
            _jm("    static int square(int x) {\n"
                "        return x * x;\n"
                "    }",
                "        int n = sc.nextInt();\n"
                "        System.out.println(square(n));"),
            "        return x * x;",
            [_case(n, n * n) for n in (5, 0, -3, 12)],
            hints=["One statement.",
                   "`return` hands the value back to the caller.",
                   "`return x * x;`"],
            difficulty="Intro"),

        _je("j9-def-sig", "Write the signature",
            "The body is written; the first line is missing. `isEven` takes an `int` "
            "and returns a `boolean`. Replace `____` with the whole signature line "
            "— and remember it has to be callable from `main`.",
            _jm("    static boolean isEven(int x) {\n"
                "        return x % 2 == 0;\n"
                "    }",
                "        int n = sc.nextInt();\n"
                "        System.out.println(isEven(n));"),
            "    static boolean isEven(int x) {",
            [_case(n, _jbool(n % 2 == 0)) for n in (4, 7, 0, -3)],
            hints=["Modifier, return type, name, parameter list, opening brace.",
                   "It must be `static`, or `main` cannot call it.",
                   "`static boolean isEven(int x) {`"]),

        _jfix("j9-def-return", "Missing return statement",
              "`max` should return the larger of two numbers. It does not compile: one "
              "path through the method returns nothing.",
              _jm("    static int max(int a, int b) {\n"
                  "        if (a > b) return a;\n"
                  "    }",
                  "        int x = sc.nextInt();\n"
                  "        int y = sc.nextInt();\n"
                  "        System.out.println(max(x, y));"),
              _jm("    static int max(int a, int b) {\n"
                  "        if (a > b) return a;\n"
                  "        return b;\n"
                  "    }",
                  "        int x = sc.nextInt();\n"
                  "        int y = sc.nextInt();\n"
                  "        System.out.println(max(x, y));"),
              [_case(f"{x}\n{y}", max(x, y)) for (x, y) in ((3, 4), (9, 2), (5, 5))],
              hints=["What does the method return when `a > b` is false?",
                     "A method declared `int` must return an int on EVERY path.",
                     "Add `return b;` after the `if`."],
              difficulty="Intro"),

        _jch("j9-def-min3", "The smallest of three", "Easy",
             "Write `min3`, which returns the smallest of its three `int` arguments. "
             "Write the whole method where you see `____` — signature and body.",
             _jm("    static int min3(int a, int b, int c) {\n"
                 "        int m = a;\n"
                 "        if (b < m) m = b;\n"
                 "        if (c < m) m = c;\n"
                 "        return m;\n"
                 "    }",
                 "        int x = sc.nextInt();\n"
                 "        int y = sc.nextInt();\n"
                 "        int z = sc.nextInt();\n"
                 "        System.out.println(min3(x, y, z));"),
             "    static int min3(int a, int b, int c) {\n"
             "        int m = a;\n"
             "        if (b < m) m = b;\n"
             "        if (c < m) m = c;\n"
             "        return m;\n"
             "    }",
             [_case(f"{x}\n{y}\n{z}", min(x, y, z))
              for (x, y, z) in ((3, 1, 2), (5, 5, 5), (-1, -9, 0), (10, 20, 30))],
             hints=["Three parameters, all `int`, and an `int` return type.",
                    "Module 1's running-minimum pattern, seeded from the first argument.",
                    "It must be `static` to be callable from `main`."]),
    ],
    quiz=[
        _jq("Does Java care whether a method is defined above or below the code that calls it?",
            ["No — methods in a class are visible to each other in any order",
             "Yes; it must be defined first",
             "Yes, unless it is static",
             "Only for recursive methods"],
            0,
            "Unlike C, Java resolves the whole class before compiling bodies, so order is "
            "purely a readability choice."),
        _jq("The best reason to extract a method is…",
            ["To give an idea a name, so the calling code reads as intent",
             "To avoid repeating code",
             "To make the program faster",
             "Because style guides require it"],
            0,
            "Naming is the biggest win: `isPalindrome(s)` says what, where the loop says how. "
            "Avoiding duplication is real but secondary; speed is not a reason at all."),
    ],
))

# --- 9.2 Returning ----------------------------------------------------------

_M9.append(_jlesson(
    "m9-return", "Return values and `void`",
    "`return` exits immediately — which is a control-flow tool, not just an exit.",
    """
**`return` does two things at once:** it hands back a value, and it leaves the
method there and then. Nothing after it in that method runs.

That second half makes it a control-flow tool. The **guard clause** is the
idiom to know:

```java
static int firstIndexOf(int[] a, int target) {
    for (int i = 0; i < a.length; i++) {
        if (a[i] == target) return i;      // leave the moment you know
    }
    return -1;                              // fell through: not found
}
```

Compare with module 1's version, which needed an `idx` variable and a `break`.
Returning straight out of the loop is shorter and has one less thing to get
wrong — and it is why methods make algorithms easier to write, not just easier
to reuse.

**`void` means "returns nothing".** A bare `return;` still works inside one, to
leave early:

```java
static void printIfPositive(int x) {
    if (x <= 0) return;                     // nothing more to do
    System.out.println(x);
}
```

**Every path must return.** A method declared with a return type has to return
on every possible route out, and the compiler checks it. `if (a > b) return a;`
with nothing after it is *"missing return statement"* — even if you can prove
the other branch never happens, the compiler will not take your word for it.

**Unreachable code is an error, not a warning:**

```java
static int f() {
    return 1;
    System.out.println("never");   // error: unreachable statement
}
```

Most languages shrug at this. Java refuses to compile it, which catches a
genuine class of mistake.

**Returning early versus a single exit.** Some style guides insist on one
`return` per method. Modern Java practice prefers early returns for guard
clauses, because the alternative is nested `if`s marching off the right of the
screen. Handle the exceptional cases first and get them out of the way; leave
the main path unindented at the bottom.
""",
    warmup=[
        _jq("```java\nstatic int f(int x) {\n    if (x > 0) return 1;\n    return 0;\n    System.out.println(x);\n}\n```",
            ["Compile error: unreachable statement",
             "It compiles; the println never runs",
             "It compiles and prints x when x <= 0",
             "Runtime error"],
            0,
            "Java treats unreachable code as an error rather than a warning. It is one of the "
            "few places the compiler is stricter than its peers."),
        _jq("What does a bare `return;` do in a `void` method?",
            ["Leaves the method immediately", "It does not compile",
             "Returns null", "Returns 0"],
            0,
            "It is the early-exit form for methods with no result — the basis of the guard "
            "clause."),
    ],
    exercises=[
        _je("j9-ret-guard", "Return the moment you know",
            "`indexOf` should return the first position of `target`, or `-1`. Replace "
            "`____` with the statement inside the loop — no flag variable, no `break`.",
            _jm("    static int indexOf(int[] a, int target) {\n"
                "        for (int i = 0; i < a.length; i++) {\n"
                "            if (a[i] == target) return i;\n"
                "        }\n"
                "        return -1;\n"
                "    }",
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        System.out.println(indexOf(a, target));"),
            "if (a[i] == target) return i;",
            [_akcase(a, t, a.index(t) if t in a else -1)
             for (a, t) in (([4, 7, 4, 9], 4), ([4, 7, 4, 9], 9), ([4, 7], 5), ([1], 1))],
            hints=["Returning leaves the loop and the method at once.",
                   "There is nothing to record — just hand back the index.",
                   "`if (a[i] == target) return i;`"]),

        _je("j9-ret-void", "A method that returns nothing",
            "`report` should print `positive`, `negative` or `zero` for its argument. "
            "Replace `____` with the return type — it hands nothing back.",
            _jm('    static void report(int x) {\n'
                '        if (x > 0) System.out.println("positive");\n'
                '        else if (x < 0) System.out.println("negative");\n'
                '        else System.out.println("zero");\n'
                "    }",
                "        int n = sc.nextInt();\n"
                "        report(n);"),
            "void",
            [_case(n, "positive" if n > 0 else "negative" if n < 0 else "zero")
             for n in (5, -3, 0)],
            hints=["The method prints; it does not produce a value.",
                   "There is a keyword for exactly that.",
                   "`void`"],
            difficulty="Intro"),

        _je("j9-ret-sign", "Three-way answer",
            "`sign` should return `1`, `-1` or `0` depending on its argument. Replace "
            "`____` with the guard clause for the negative case.",
            _jm("    static int sign(int x) {\n"
                "        if (x > 0) return 1;\n"
                "        if (x < 0) return -1;\n"
                "        return 0;\n"
                "    }",
                "        int n = sc.nextInt();\n"
                "        System.out.println(sign(n));"),
            "        if (x < 0) return -1;",
            [_case(n, 1 if n > 0 else -1 if n < 0 else 0) for n in (7, -7, 0, -1)],
            hints=["The same shape as the line above it.",
                   "Return -1 when the value is below zero.",
                   "`if (x < 0) return -1;`"],
            difficulty="Intro"),

        _jfix("j9-ret-unreachable", "Code after the return",
              "This does not compile. The method is correct up to a point; something "
              "after it can never run.",
              _jm("    static int doubled(int x) {\n"
                  "        return x * 2;\n"
                  '        System.out.println("doubling " + x);\n'
                  "    }",
                  "        int n = sc.nextInt();\n"
                  "        System.out.println(doubled(n));"),
              _jm("    static int doubled(int x) {\n"
                  '        System.out.println("doubling " + x);\n'
                  "        return x * 2;\n"
                  "    }",
                  "        int n = sc.nextInt();\n"
                  "        System.out.println(doubled(n));"),
              [_case(n, _nl(f"doubling {n}", n * 2)) for n in (5, 0, -2)],
              hints=["`return` leaves the method immediately.",
                     "Anything written after it is unreachable, which Java rejects outright.",
                     "Move the println above the return."],
              difficulty="Intro"),

        _jch("j9-ret-count", "Count what qualifies", "Easy",
             "Write `countGreater`, which returns how many elements of an `int[]` are "
             "strictly greater than a threshold. Write the whole method where you see "
             "`____`.",
             _jm("    static int countGreater(int[] a, int threshold) {\n"
                 "        int count = 0;\n"
                 "        for (int i = 0; i < a.length; i++) {\n"
                 "            if (a[i] > threshold) count++;\n"
                 "        }\n"
                 "        return count;\n"
                 "    }",
                 _RD_ARR
                 + "        int t = sc.nextInt();\n"
                   "        System.out.println(countGreater(a, t));"),
             "    static int countGreater(int[] a, int threshold) {\n"
             "        int count = 0;\n"
             "        for (int i = 0; i < a.length; i++) {\n"
             "            if (a[i] > threshold) count++;\n"
             "        }\n"
             "        return count;\n"
             "    }",
             [_akcase(a, t, sum(1 for x in a if x > t))
              for (a, t) in (([1, 5, 3, 8], 3), ([1, 1, 1], 1), ([9], 0), ([-3, -1], -2))],
             hints=["Two parameters: the array and the threshold. Returns an `int`.",
                    "Use `a.length` inside the method — the caller's `n` is not visible here.",
                    "Strictly greater, so a value equal to the threshold does not count."]),
    ],
    quiz=[
        _jq("Why is returning from inside a loop often better than setting a flag and breaking?",
            ["It removes a variable and a state to keep consistent",
             "It is faster",
             "It is required by the compiler",
             "It avoids the loop entirely"],
            0,
            "Fewer moving parts. The flag-and-break form has a variable that can be read "
            "before it is set, or set and then overwritten."),
        _jq("The compiler rejects a method with a return type but no return on some path. Why not just return 0?",
            ["Silently inventing a value would hide a genuine logic gap",
             "Because 0 is not valid for all types",
             "It is a historical accident",
             "It does return 0 — the error is about something else"],
            0,
            "The missing path is a bug you have not thought about yet. Forcing you to write "
            "the return makes you decide what the answer is."),
    ],
))

# --- 9.3 Pass-by-value ------------------------------------------------------

_M9.append(_jlesson(
    "m9-passing", "Java is always pass-by-value",
    "One sentence that explains every argument-passing surprise you will ever meet.",
    """
**Java passes arguments by value, always, with no exceptions.** The parameter
is a *copy* of what the caller supplied. The subtlety is entirely in *what* is
being copied.

**Primitives: the value is copied.** Changing the parameter cannot affect the
caller.

```java
static void increment(int x) { x = x + 1; }

int n = 5;
increment(n);
System.out.println(n);      // 5 — nothing happened
```

That is why **you cannot write a `swap(int, int)` method in Java.** It is a
classic interview question, and the answer is "you can't — pass an array or
return the pair instead".

**Objects (including arrays): the REFERENCE is copied.** Both the caller's
variable and the parameter now point at the *same object*, so changes to that
object's contents are visible to both:

```java
static void doubleAll(int[] a) {
    for (int i = 0; i < a.length; i++) a[i] = a[i] * 2;
}

int[] nums = {1, 2, 3};
doubleAll(nums);
System.out.println(Arrays.toString(nums));    // [2, 4, 6] — it DID change
```

This is module 1's aliasing lesson, arriving through a parameter list.

**But reassigning the parameter changes nothing for the caller:**

```java
static void replace(int[] a) {
    a = new int[]{9, 9, 9};        // repoints the LOCAL copy of the reference
}

int[] nums = {1, 2, 3};
replace(nums);                      // nums is still {1, 2, 3}
```

If Java were pass-by-*reference*, this would work. It does not, and that is the
proof. The two rules together:

> **Modifying the object it points at: visible to the caller.
> Repointing the parameter: invisible to the caller.**

**Strings look like primitives, and they are not.** The reference is copied,
exactly as for arrays — but a String cannot be modified, so there is nothing to
see. Every "modification" is really a reassignment, which is invisible:

```java
static void shout(String s) { s = s.toUpperCase(); }   // caller unaffected
```

If you want the caller to have the new text, **return it**:

```java
static String shout(String s) { return s.toUpperCase(); }
name = shout(name);
```

**The practical rule.** A method that takes an array can quietly rewrite the
caller's data. Decide on purpose which you are doing, and say so in the name:
`sortInPlace(a)` versus `sorted(a)` returning a copy. Silent mutation of a
caller's array is one of the easiest bugs to create and one of the hardest to
find.
""",
    warmup=[
        _jq("```java\nstatic void inc(int x) { x++; }\nint n = 5; inc(n);\nSystem.out.println(n);\n```",
            ["5", "6", "It does not compile", "Unpredictable"],
            0,
            "`x` is a copy. This is exactly why a `swap(int, int)` method is impossible in "
            "Java."),
        _jq("```java\nstatic void f(int[] a) { a = new int[]{9}; }\nint[] x = {1,2}; f(x);\nSystem.out.println(x.length);\n```",
            ["2", "1", "9", "0"],
            0,
            "The method repointed its own copy of the reference. The caller's variable still "
            "points at the original array — which is the proof that Java is not "
            "pass-by-reference."),
    ],
    exercises=[
        _je("j9-pass-array", "Methods can change your array",
            "`doubleAll` should double every element of the array it is given, and "
            "the caller must see the change. Replace `____` with the loop body.",
            _jm("    static void doubleAll(int[] a) {\n"
                "        for (int i = 0; i < a.length; i++) a[i] = a[i] * 2;\n"
                "    }",
                _RD_ARR
                + "        doubleAll(a);\n"
                  "        System.out.println(Arrays.toString(a));"),
            "for (int i = 0; i < a.length; i++) a[i] = a[i] * 2;",
            [_acase(a, _jarr([x * 2 for x in a]))
             for a in ([1, 2, 3], [-4, 0, 7], [5])],
            hints=["Write into the array's slots — that is what the caller can see.",
                   "An enhanced `for` would only change copies of the values.",
                   "`for (int i = 0; i < a.length; i++) a[i] = a[i] * 2;`"]),

        _je("j9-pass-return", "Give it back instead",
            "`shout` cannot change the caller's String — strings are immutable and "
            "the reference is a copy. So it returns the new text instead. Replace "
            "`____` with the line in `main` that keeps the result.",
            _jm("    static String shout(String s) {\n"
                '        return s.toUpperCase() + "!";\n'
                "    }",
                "        String name = sc.nextLine();\n"
                "        name = shout(name);\n"
                "        System.out.println(name);"),
            "name = shout(name);",
            [_scase(s, s.upper() + "!") for s in ("ada", "Grace Hopper", "x")],
            hints=["The method hands back a new String; the caller has to catch it.",
                   "Calling it and discarding the result would leave `name` untouched.",
                   "`name = shout(name);`"]),

        _jfix("j9-pass-reassign", "It replaced its own copy",
              "`zeroOut` should set every element of the caller's array to 0. It leaves "
              "the caller's array completely unchanged, because it reassigns the "
              "parameter instead of writing into the array.",
              _jm("    static void zeroOut(int[] a) {\n"
                  "        a = new int[a.length];\n"
                  "    }",
                  _RD_ARR
                  + "        zeroOut(a);\n"
                    "        System.out.println(Arrays.toString(a));"),
              _jm("    static void zeroOut(int[] a) {\n"
                  "        for (int i = 0; i < a.length; i++) a[i] = 0;\n"
                  "    }",
                  _RD_ARR
                  + "        zeroOut(a);\n"
                    "        System.out.println(Arrays.toString(a));"),
              [_acase(a, _jarr([0] * len(a))) for a in ([1, 2, 3], [7], [-1, 5])],
              hints=["What does assigning to the parameter `a` actually change?",
                     "It repoints the method's own copy of the reference — the caller never "
                     "sees it.",
                     "Write into the existing slots: `for (...) a[i] = 0;`"],
              difficulty="Medium"),

        _jch("j9-pass-swap", "The swap that does work", "Medium",
             "You cannot write `swap(int, int)` in Java — but you can swap two slots "
             "of an array, because the array itself is shared. Write "
             "`swap(int[] a, int i, int j)` so the caller sees the change. Write the "
             "whole method where you see `____`.",
             _jm("    static void swap(int[] a, int i, int j) {\n"
                 "        int t = a[i];\n"
                 "        a[i] = a[j];\n"
                 "        a[j] = t;\n"
                 "    }",
                 _RD_ARR
                 + "        int i = sc.nextInt();\n"
                   "        int j = sc.nextInt();\n"
                   "        swap(a, i, j);\n"
                   "        System.out.println(Arrays.toString(a));"),
             "    static void swap(int[] a, int i, int j) {\n"
             "        int t = a[i];\n"
             "        a[i] = a[j];\n"
             "        a[j] = t;\n"
             "    }",
             [_case(f"{len(a)}\n{_sp(a)}\n{i}\n{j}",
                    _jarr([a[j] if p == i else a[i] if p == j else a[p]
                           for p in range(len(a))]))
              for (a, i, j) in (([10, 20, 30, 40], 0, 3), ([10, 20, 30], 1, 2),
                                ([5, 6], 0, 1), ([1, 2, 3], 1, 1))],
             hints=["Three parameters, `void` return type.",
                    "Module 1's three-line swap, written inside the method.",
                    "It works because you are modifying the shared array, not reassigning the "
                    "parameter."]),
    ],
    quiz=[
        _jq("Which single sentence explains all of Java's argument passing?",
            ["Arguments are always passed by value; for objects, the value is the reference",
             "Primitives are by value, objects are by reference",
             "Everything is by reference except int and boolean",
             "It depends on whether the parameter is final"],
            0,
            "The 'objects are by reference' phrasing is the common misconception, and it "
            "cannot explain why reassigning a parameter has no effect on the caller."),
        _jq("A method takes `int[] data` and sorts it. What should its name signal?",
            ["That it mutates the caller's array — e.g. `sortInPlace`",
             "Nothing; sorting is always in place",
             "That it returns a new array",
             "That it is static"],
            0,
            "Silent mutation of a caller's array is a hard bug to find. `sortInPlace(a)` "
            "versus `sorted(a)` makes the contract visible at the call site."),
    ],
))

# --- 9.4 Overloading --------------------------------------------------------

_M9.append(_jlesson(
    "m9-overload", "Overloading",
    "One name, several parameter lists — and the rules Java uses to pick.",
    """
Two methods may share a name as long as their **parameter lists differ**:

```java
static int area(int side)            { return side * side; }
static int area(int w, int h)        { return w * h; }
static double area(double r)         { return 3.14159 * r * r; }
```

The compiler picks by looking at the argument types at each call site. This is
**compile-time** resolution — decided while compiling, not while running.

**The return type is not part of the signature.** These two cannot coexist:

```java
static int    f(int x) { ... }
static double f(int x) { ... }        // error: f(int) is already defined
```

Because a caller may ignore the result entirely (`f(3);`), the compiler would
have no information to choose with. Same reasoning for parameter *names*:
`f(int a)` and `f(int b)` are the same method.

**How Java chooses,** in order, stopping at the first that works:

1. **Exact match** — `f(int)` for an `int` argument.
2. **Widening** — `int` to `long`, `long` to `double`, `char` to `int`. So
   `f(long)` takes an `int` argument if there is no `f(int)`.
3. **Boxing** — `int` to `Integer`.
4. **Varargs** — `f(int...)` is the last resort.

That order is why a varargs overload never steals a call a fixed-arity one can
handle:

```java
static int sum(int a, int b)    { return a + b; }
static int sum(int... xs)       { ... }

sum(1, 2);      // calls sum(int, int) — step 1 beats step 4
sum(1, 2, 3);   // calls sum(int...)
```

**Ambiguity is a compile error, not a coin toss.** If two overloads are equally
good matches and neither is more specific, Java refuses to compile the call and
tells you so.

**Where you have already met it.** `System.out.println` is overloaded for every
primitive plus `String`, `char[]` and `Object` — that is why it prints anything
you hand it. `StringBuilder.append` is the same, and so is `Math.max`, which has
`int`, `long`, `float` and `double` versions.

**Overloading versus overriding.** Overloading is same name, *different*
parameters, resolved at compile time. Overriding is same name, *same*
parameters, in a subclass, resolved at run time. They are unrelated mechanisms
with confusingly similar names — Part 4 of the roadmap covers the second one.
""",
    warmup=[
        _jq("Why can't `int f(int x)` and `double f(int x)` coexist?",
            ["The return type is not part of the signature, so a caller ignoring the result would be ambiguous",
             "They can — Java allows it",
             "Because int and double are incompatible",
             "Because both are static"],
            0,
            "`f(3);` as a statement discards the result, giving the compiler nothing to choose "
            "with. So return type is excluded from overload resolution entirely."),
        _jq("With both `sum(int, int)` and `sum(int...)` defined, which does `sum(1, 2)` call?",
            ["sum(int, int) — exact matches beat varargs",
             "sum(int...) — varargs is more general",
             "It is ambiguous and fails to compile",
             "Whichever is declared first"],
            0,
            "Varargs is the last step in the resolution order, so a fixed-arity match always "
            "wins."),
    ],
    exercises=[
        _je("j9-ovl-second", "Add the second version",
            "`area` already handles a square. Add the overload for a rectangle, which "
            "takes a width and a height. Replace `____` with the whole second method.",
            _jm("    static int area(int side) {\n"
                "        return side * side;\n"
                "    }\n"
                "\n"
                "    static int area(int w, int h) {\n"
                "        return w * h;\n"
                "    }",
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        System.out.println(area(a));\n"
                "        System.out.println(area(a, b));"),
            "    static int area(int w, int h) {\n"
            "        return w * h;\n"
            "    }",
            [_case(f"{x}\n{y}", _nl(x * x, x * y))
             for (x, y) in ((3, 4), (5, 1), (2, 7))],
            hints=["Same name, two parameters instead of one.",
                   "Same return type is fine — it is the parameter list that must differ.",
                   "`static int area(int w, int h) { return w * h; }`"]),

        _je("j9-ovl-pick", "Which one runs?",
            "Two overloads of `describe` are defined. Replace `____` with the call "
            "that selects the **two-argument** one, using the values read from input.",
            _jm('    static String describe(int x) {\n'
                '        return "one:" + x;\n'
                "    }\n"
                "\n"
                '    static String describe(int x, int y) {\n'
                '        return "two:" + (x + y);\n'
                "    }",
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        System.out.println(describe(a));\n"
                "        System.out.println(describe(a, b));"),
            "describe(a, b)",
            [_case(f"{x}\n{y}", _nl(f"one:{x}", f"two:{x + y}"))
             for (x, y) in ((3, 4), (0, 0), (-2, 9))],
            hints=["The number of arguments decides which overload is chosen.",
                   "Pass both variables.",
                   "`describe(a, b)`"],
            difficulty="Intro"),

        _jfix("j9-ovl-rettype", "Overloaded on the return type",
              "This tries to define two versions of `half` that differ only in what "
              "they return. It does not compile. Give the second one a different "
              "parameter list instead — make it take an `int` count of how many times "
              "to halve.",
              _jm("    static int half(int x) {\n"
                  "        return x / 2;\n"
                  "    }\n"
                  "\n"
                  "    static double half(int x) {\n"
                  "        return x / 2.0;\n"
                  "    }",
                  "        int n = sc.nextInt();\n"
                  "        System.out.println(half(n));\n"
                  "        System.out.println(half(n, 2));"),
              _jm("    static int half(int x) {\n"
                  "        return x / 2;\n"
                  "    }\n"
                  "\n"
                  "    static int half(int x, int times) {\n"
                  "        int r = x;\n"
                  "        for (int i = 0; i < times; i++) r = r / 2;\n"
                  "        return r;\n"
                  "    }",
                  "        int n = sc.nextInt();\n"
                  "        System.out.println(half(n));\n"
                  "        System.out.println(half(n, 2));"),
              [_case(n, _nl(n // 2, n // 2 // 2)) for n in (20, 7, 100, 1)],
              hints=["Overloads must differ in their PARAMETER LIST, not their return type.",
                     "`main` already calls `half(n, 2)`, so the second version needs two "
                     "`int` parameters.",
                     "Halve `times` times in a loop and return the result."],
              difficulty="Medium"),

        _jch("j9-ovl-max", "Overload max", "Easy",
             "Write two overloads of `biggest`: one taking two `int`s and one taking "
             "three. The three-argument version should reuse the two-argument one. "
             "Write both methods where you see `____`.",
             _jm("    static int biggest(int a, int b) {\n"
                 "        if (a > b) return a;\n"
                 "        return b;\n"
                 "    }\n"
                 "\n"
                 "    static int biggest(int a, int b, int c) {\n"
                 "        return biggest(biggest(a, b), c);\n"
                 "    }",
                 "        int x = sc.nextInt();\n"
                 "        int y = sc.nextInt();\n"
                 "        int z = sc.nextInt();\n"
                 "        System.out.println(biggest(x, y));\n"
                 "        System.out.println(biggest(x, y, z));"),
             "    static int biggest(int a, int b) {\n"
             "        if (a > b) return a;\n"
             "        return b;\n"
             "    }\n"
             "\n"
             "    static int biggest(int a, int b, int c) {\n"
             "        return biggest(biggest(a, b), c);\n"
             "    }",
             [_case(f"{x}\n{y}\n{z}", _nl(max(x, y), max(x, y, z)))
              for (x, y, z) in ((3, 9, 5), (1, 1, 1), (-4, -9, -2), (10, 2, 30))],
             hints=["Two methods with the same name, differing in argument count.",
                    "The three-argument version can call the two-argument one twice — that is "
                    "not recursion, it is just reuse.",
                    "`return biggest(biggest(a, b), c);`"]),
    ],
    quiz=[
        _jq("Overload resolution happens…",
            ["at compile time, from the static types of the arguments",
             "at run time, from the actual values",
             "at class-load time",
             "only for static methods"],
            0,
            "That is the deepest difference from overriding, which is resolved at run time "
            "from the object's actual class."),
        _jq("`System.out.println` accepts an int, a String, a char[] and an Object. That is…",
            ["overloading — many methods with one name and different parameter lists",
             "overriding",
             "generics",
             "varargs"],
            0,
            "Roughly ten overloads. `StringBuilder.append` and `Math.max` work the same way."),
    ],
))

# --- 9.5 Scope and static ---------------------------------------------------

_M9.append(_jlesson(
    "m9-scope", "Scope, shadowing and `static` fields",
    "Where a name is visible, how long it lives, and what happens when two share a name.",
    """
**A variable exists from its declaration to the closing brace of the block that
declares it.** That is the whole rule; everything else follows.

```java
static void f() {
    int a = 1;
    if (a > 0) {
        int b = 2;                 // b exists only inside this if
        System.out.println(a + b); // a is visible — an inner block sees outer names
    }
    // System.out.println(b);      // error: b is out of scope
}
```

**A loop variable dies with the loop:**

```java
for (int i = 0; i < 10; i++) { ... }
// System.out.println(i);          // error: i does not exist here
```

If you need the value afterwards, declare it before the loop. That is exactly
why module 4's `k` write-pointer lives outside its loop.

**Parameters are locals** with the same lifetime as the method body — which is
the mechanism behind lesson 9.3.

**Methods cannot see each other's locals.** Every method has its own frame, so
`main`'s `n` does not exist inside `countGreater`. The only way in is a
parameter; the only way out is the return value. That is a feature: it is what
makes a method testable in isolation.

**A `static` field belongs to the class** and outlives every call:

```java
static int callCount = 0;              // one copy, for the whole program

static void ping() {
    callCount++;                        // every call sees the same field
}
```

Static fields are how a program keeps state between method calls before objects
exist. Use them sparingly — shared mutable state is exactly as awkward here as
anywhere else — but a counter or a cache is a legitimate use.

**Shadowing** is a local that has the same name as a field. Inside that method,
the local wins:

```java
static int total = 0;

static void add(int x) {
    int total = 0;                      // SHADOWS the field
    total = total + x;                   // updates the local; the field never moves
}
```

This compiles, runs, and silently does nothing useful — the same species of bug
as module 6's dropped return value. The fix is to not redeclare, or to be
explicit. Java's answer for instance fields is `this.total`; for a static field
it is `Main.total`.

**Java has no global variables.** The closest thing is a `public static` field
on a class, and reaching for it is usually a sign a parameter would be better.
""",
    warmup=[
        _jq("```java\nfor (int i = 0; i < 3; i++) { }\nSystem.out.println(i);\n```",
            ["Compile error: i is out of scope",
             "Prints 3", "Prints 2", "Prints 0"],
            0,
            "A variable declared in the `for` header lives only for the loop. Declare it "
            "before the loop if you need it afterwards."),
        _jq("```java\nstatic int total = 0;\nstatic void add(int x) { int total = 0; total += x; }\n```\nAfter `add(5)`, the field `total` is…",
            ["0 — the local shadowed the field",
             "5", "It does not compile", "Unpredictable"],
            0,
            "The inner declaration creates a new local that hides the field. Everything after "
            "it refers to the local, and the field is never touched."),
    ],
    exercises=[
        _je("j9-sc-field", "State that survives the call",
            "`bump` should increase a counter that keeps its value between calls. "
            "Replace `____` with the field declaration — it has to live outside any "
            "method.",
            _jm("    static int count = 0;\n"
                "\n"
                "    static void bump() {\n"
                "        count++;\n"
                "    }",
                "        int k = sc.nextInt();\n"
                "        for (int i = 0; i < k; i++) bump();\n"
                "        System.out.println(count);"),
            "    static int count = 0;",
            [_case(k, k) for k in (5, 1, 0, 20)],
            hints=["A field belongs to the class, not to a method.",
                   "It must be `static`, since every method here is.",
                   "`static int count = 0;`"]),

        _je("j9-sc-param", "Pass it in",
            "`describe` cannot see `main`'s variables — the only way in is through "
            "the parameter list. Replace `____` with the parameter list it needs.",
            _jm('    static String describe(int n, String label) {\n'
                '        return label + "=" + n;\n'
                "    }",
                "        String label = sc.nextLine();\n"
                "        int n = sc.nextInt();\n"
                "        System.out.println(describe(n, label));"),
            "(int n, String label)",
            [_lkcase(label, n, f"{label}={n}")
             for (label, n) in (("score", 42), ("count", 0), ("x y", -3))],
            hints=["Two parameters, each with a type and a name.",
                   "The call site is `describe(n, label)`, so the order is int first.",
                   "`(int n, String label)`"],
            difficulty="Intro"),

        _jfix("j9-sc-shadow", "The field that never changed",
              "`addTo` should accumulate into the `total` field, so the program prints "
              "the sum of the inputs. It always prints 0. Nothing throws and nothing "
              "fails to compile — a local is hiding the field.",
              _jm("    static int total = 0;\n"
                  "\n"
                  "    static void addTo(int x) {\n"
                  "        int total = 0;\n"
                  "        total = total + x;\n"
                  "    }",
                  _RD_ARR
                  + "        for (int i = 0; i < n; i++) addTo(a[i]);\n"
                    "        System.out.println(total);"),
              _jm("    static int total = 0;\n"
                  "\n"
                  "    static void addTo(int x) {\n"
                  "        total = total + x;\n"
                  "    }",
                  _RD_ARR
                  + "        for (int i = 0; i < n; i++) addTo(a[i]);\n"
                    "        System.out.println(total);"),
              [_acase(a, sum(a)) for a in ([1, 2, 3], [10], [-5, 5, 7])],
              hints=["There are two things called `total`. Which one does the method update?",
                     "The local declaration hides the field for the rest of the method.",
                     "Delete the local declaration so `total` refers to the field."],
              difficulty="Medium"),

        _jch("j9-sc-tracker", "Track the largest seen", "Medium",
             "Write a `static` field `best` and a method `see(int x)` that keeps "
             "`best` equal to the largest value it has ever been shown. `main` calls "
             "`see` for every element and then prints `best`. Seed `best` from the "
             "first element before the loop. Write the field and the method where you "
             "see `____`.",
             _jm("    static int best = 0;\n"
                 "\n"
                 "    static void see(int x) {\n"
                 "        if (x > best) best = x;\n"
                 "    }",
                 _RD_ARR
                 + "        best = a[0];\n"
                   "        for (int i = 0; i < n; i++) see(a[i]);\n"
                   "        System.out.println(best);"),
             "    static int best = 0;\n"
             "\n"
             "    static void see(int x) {\n"
             "        if (x > best) best = x;\n"
             "    }",
             [_acase(a, max(a)) for a in ([3, 9, 2], [-4, -11, -7], [5], [1, 1, 1])],
             hints=["The field goes outside every method; the method goes beside `main`.",
                    "Do NOT redeclare `best` inside `see` — that is the shadowing bug from "
                    "the exercise above.",
                    "`main` already seeds `best = a[0];`, which is what makes the "
                    "all-negative case work."]),
    ],
    quiz=[
        _jq("Why can't `countGreater` see `main`'s local variable `n`?",
            ["Each method has its own frame; locals are private to the call that made them",
             "Because n is not static",
             "Because n is declared after the method",
             "It can, as long as both are in the same class"],
            0,
            "That isolation is the point: a method's behaviour depends only on its arguments, "
            "which is what makes it testable and reusable."),
        _jq("A method declares a local with the same name as a static field. What happens?",
            ["It compiles; the local shadows the field for the rest of the method",
             "Compile error: duplicate variable",
             "The field is updated instead",
             "The local is ignored"],
            0,
            "Perfectly legal and occasionally intentional (constructor parameters do it), "
            "which is why accidental shadowing is such a quiet bug."),
    ],
))

# --- 9.6 Varargs ------------------------------------------------------------

_M9.append(_jlesson(
    "m9-varargs", "Varargs",
    "`int... xs` — any number of arguments, delivered as an array.",
    """
Sometimes you do not know how many arguments there will be. Varargs lets the
caller pass any number, and hands them to you as an **array**:

```java
static int sum(int... xs) {
    int total = 0;
    for (int x : xs) total += x;      // xs really is an int[]
    return total;
}

sum();              // 0  — an empty array, not null
sum(1);             // 1
sum(1, 2, 3);       // 6
sum(new int[]{1, 2, 3});   // 6 — an array is accepted directly
```

Inside the method `xs` is an ordinary `int[]`: it has `.length`, you can index
it, and you can loop over it. Everything from Part 1 applies.

**Three rules:**

1. **At most one varargs parameter, and it must be last.**
   `static void f(String label, int... xs)` is fine;
   `static void f(int... xs, String label)` does not compile — there would be
   no way to tell where the varargs stopped.
2. **Zero arguments gives an empty array, never `null`.** So `xs.length == 0`
   is the check, and looping over it is safe with no null test.
3. **A fixed-arity overload always wins.** With both `sum(int, int)` and
   `sum(int...)`, the call `sum(1, 2)` picks the first — varargs is the last
   step in resolution.

**Where you have already seen it.** `String.format("%s is %d", name, age)` and
`String.join("-", "a", "b", "c")` are both varargs, and so is
`Arrays.asList(...)`. `main(String[] args)` could equally have been written
`main(String... args)` — the JVM accepts either.

**A caution.** `f(int... xs)` and `f(int[] xs)` have the same signature after
compilation, so you cannot declare both. And overloading a varargs method
against another varargs method is a fast route to ambiguity errors. Varargs is
a convenience for call sites, not a design tool — use it where the argument
count genuinely varies, and prefer an explicit array parameter where it does
not.
""",
    warmup=[
        _jq("What is `xs` inside `static int f(int... xs)` when called as `f()`?",
            ["An int[] of length 0", "null", "An int[] of length 1 holding 0",
             "It does not compile"],
            0,
            "Java always constructs the array, even when it is empty — so you never need a "
            "null check on a varargs parameter."),
        _jq("Why must a varargs parameter be last?",
            ["Otherwise there is no way to tell where the variable-length part stops",
             "Because arrays must be last",
             "It doesn't — it can go anywhere",
             "Because it is always an Object[]"],
            0,
            "Any parameters after it would be indistinguishable from more varargs values."),
    ],
    exercises=[
        _je("j9-va-sum", "Any number of numbers",
            "`sum` should accept any number of `int` arguments. Replace `____` with "
            "the parameter declaration.",
            _jm("    static int sum(int... xs) {\n"
                "        int total = 0;\n"
                "        for (int x : xs) total += x;\n"
                "        return total;\n"
                "    }",
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        int c = sc.nextInt();\n"
                "        System.out.println(sum());\n"
                "        System.out.println(sum(a));\n"
                "        System.out.println(sum(a, b, c));"),
            "int... xs",
            [_case(f"{x}\n{y}\n{z}", _nl(0, x, x + y + z))
             for (x, y, z) in ((1, 2, 3), (5, 0, -5), (10, 10, 10))],
            hints=["Three dots between the type and the name.",
                   "The name is plural because it arrives as an array.",
                   "`int... xs`"]),

        _je("j9-va-count", "It really is an array",
            "`howMany` should return the number of arguments it was given. Replace "
            "`____` with the expression — `xs` is an ordinary `int[]` inside the "
            "method.",
            _jm("    static int howMany(int... xs) {\n"
                "        return xs.length;\n"
                "    }",
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        System.out.println(howMany());\n"
                "        System.out.println(howMany(a));\n"
                "        System.out.println(howMany(a, b));"),
            "xs.length",
            [_case(f"{x}\n{y}", _nl(0, 1, 2)) for (x, y) in ((7, 8), (0, 0))],
            hints=["Inside the method it is an array like any other.",
                   "Arrays use the FIELD `.length` — no parentheses.",
                   "`xs.length`"],
            difficulty="Intro"),

        _jfix("j9-va-order", "Varargs in the wrong place",
              "`report` should print a label followed by the total of any number of "
              "values. It does not compile, because the varargs parameter is not last.",
              _jm("    static void report(int... xs, String label) {\n"
                  "        int total = 0;\n"
                  "        for (int x : xs) total += x;\n"
                  '        System.out.println(label + "=" + total);\n'
                  "    }",
                  "        String label = sc.nextLine();\n"
                  "        int a = sc.nextInt();\n"
                  "        int b = sc.nextInt();\n"
                  "        report(label, a, b);"),
              _jm("    static void report(String label, int... xs) {\n"
                  "        int total = 0;\n"
                  "        for (int x : xs) total += x;\n"
                  '        System.out.println(label + "=" + total);\n'
                  "    }",
                  "        String label = sc.nextLine();\n"
                  "        int a = sc.nextInt();\n"
                  "        int b = sc.nextInt();\n"
                  "        report(label, a, b);"),
              [_case(f"{lab}\n{x}\n{y}", f"{lab}={x + y}")
               for (lab, x, y) in (("total", 3, 4), ("score", 0, 0), ("a b", -1, 1))],
              hints=["A varargs parameter has to be the last one in the list.",
                     "The call site is already `report(label, a, b)`.",
                     "`static void report(String label, int... xs)`"],
              difficulty="Intro"),

        _jch("j9-va-max", "Largest of many", "Medium",
             "Write `largest(int first, int... rest)` — a required first value plus "
             "any number of extras — returning the biggest of all of them. Requiring "
             "one argument means there is always an answer, even with no extras. "
             "Write the whole method where you see `____`.",
             _jm("    static int largest(int first, int... rest) {\n"
                 "        int best = first;\n"
                 "        for (int x : rest) {\n"
                 "            if (x > best) best = x;\n"
                 "        }\n"
                 "        return best;\n"
                 "    }",
                 "        int a = sc.nextInt();\n"
                 "        int b = sc.nextInt();\n"
                 "        int c = sc.nextInt();\n"
                 "        System.out.println(largest(a));\n"
                 "        System.out.println(largest(a, b));\n"
                 "        System.out.println(largest(a, b, c));"),
             "    static int largest(int first, int... rest) {\n"
             "        int best = first;\n"
             "        for (int x : rest) {\n"
             "            if (x > best) best = x;\n"
             "        }\n"
             "        return best;\n"
             "    }",
             [_case(f"{x}\n{y}\n{z}", _nl(x, max(x, y), max(x, y, z)))
              for (x, y, z) in ((3, 9, 2), (-4, -11, -7), (5, 5, 5), (1, 2, 3))],
             hints=["The required parameter comes first; the varargs one comes last.",
                    "Seed `best` with `first` — that is why the required parameter is there, "
                    "and it is module 1's 'seed from real data' rule again.",
                    "A for-each over `rest` is enough; it is safe even when `rest` is empty."]),
    ],
    quiz=[
        _jq("`static void f(int... xs)` and `static void f(int[] xs)` in the same class…",
            ["do not compile — they have the same signature after compilation",
             "are valid overloads",
             "are valid, but the array one is never called",
             "compile only if one is private"],
            0,
            "Varargs is syntactic sugar for an array parameter, so the two erase to the same "
            "signature."),
        _jq("Which of these is NOT a varargs method you have already used?",
            ["String.substring", "String.format", "String.join", "Arrays.asList"],
            0,
            "`substring` takes one or two fixed `int` parameters — that is overloading, not "
            "varargs. The other three take a variable number of arguments."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m9_toolkit(a, k):
    return _nl(
        f"sum={sum(a)}",
        f"max={max(a)}",
        f"count={sum(1 for x in a if x > k)}",
        f"reversed={_jarr(list(reversed(a)))}",
        f"original={_jarr(a)}",
    )


_M9_CAP = _jcap(
    "Array toolkit",
    """
Rebuild four things you wrote as loops in Part 1 — this time as **methods**,
with `main` reduced to reading input and printing.

Read the array, then a threshold `k`. Print:

```
sum=<total of the array>
max=<largest element>
count=<how many elements are strictly greater than k>
reversed=<the array reversed, in Arrays.toString form>
original=<the ORIGINAL array, unchanged, in Arrays.toString form>
```

Write four `static` methods and let `main` call them:

| Method | Returns |
|---|---|
| `sum(int[] a)` | the total |
| `max(int[] a)` | the largest element |
| `countGreater(int[] a, int k)` | how many exceed `k` |
| `reversed(int[] a)` | a **new** array, reversed |

**That last line of output is the real test.** `reversed` must not disturb the
caller's array — so it has to allocate a new one and fill it, not reverse in
place. If it reverses `a` directly, `original` comes out backwards and the case
fails. This is lesson 9.3 with a consequence attached: a method that receives an
array can silently rewrite the caller's data, and here you must choose not to.

`max` must be seeded from `a[0]`, not from `0` — one of the hidden cases is
entirely negative.
""",
    _jch("j9-cap-toolkit", "Array toolkit", "Hard",
         "Write the four methods where you see `____`, above `main`. `main` is "
         "already written and calls them in order.",
         _jm("    static int sum(int[] a) {\n"
             "        int total = 0;\n"
             "        for (int x : a) total += x;\n"
             "        return total;\n"
             "    }\n"
             "\n"
             "    static int max(int[] a) {\n"
             "        int best = a[0];\n"
             "        for (int i = 1; i < a.length; i++) {\n"
             "            if (a[i] > best) best = a[i];\n"
             "        }\n"
             "        return best;\n"
             "    }\n"
             "\n"
             "    static int countGreater(int[] a, int k) {\n"
             "        int count = 0;\n"
             "        for (int x : a) {\n"
             "            if (x > k) count++;\n"
             "        }\n"
             "        return count;\n"
             "    }\n"
             "\n"
             "    static int[] reversed(int[] a) {\n"
             "        int[] out = new int[a.length];\n"
             "        for (int i = 0; i < a.length; i++) out[i] = a[a.length - 1 - i];\n"
             "        return out;\n"
             "    }",
             _RD_ARR
             + "        int k = sc.nextInt();\n"
               '        System.out.println("sum=" + sum(a));\n'
               '        System.out.println("max=" + max(a));\n'
               '        System.out.println("count=" + countGreater(a, k));\n'
               '        System.out.println("reversed=" + Arrays.toString(reversed(a)));\n'
               '        System.out.println("original=" + Arrays.toString(a));'),
         "    static int sum(int[] a) {\n"
         "        int total = 0;\n"
         "        for (int x : a) total += x;\n"
         "        return total;\n"
         "    }\n"
         "\n"
         "    static int max(int[] a) {\n"
         "        int best = a[0];\n"
         "        for (int i = 1; i < a.length; i++) {\n"
         "            if (a[i] > best) best = a[i];\n"
         "        }\n"
         "        return best;\n"
         "    }\n"
         "\n"
         "    static int countGreater(int[] a, int k) {\n"
         "        int count = 0;\n"
         "        for (int x : a) {\n"
         "            if (x > k) count++;\n"
         "        }\n"
         "        return count;\n"
         "    }\n"
         "\n"
         "    static int[] reversed(int[] a) {\n"
         "        int[] out = new int[a.length];\n"
         "        for (int i = 0; i < a.length; i++) out[i] = a[a.length - 1 - i];\n"
         "        return out;\n"
         "    }",
         [_akcase(a, k, _m9_toolkit(a, k))
          for (a, k) in (([3, 1, 4, 1, 5], 2), ([-4, -11, -7], -8),
                         ([7], 0), ([2, 2, 2, 2], 2), ([10, 20, 30], 15))],
         hints=["All four are `static`, since `main` is.",
                "Inside a method use `a.length` — `main`'s `n` is not in scope there.",
                "`reversed` returns `int[]`, so it must allocate `new int[a.length]` and "
                "fill it. Reversing `a` in place would corrupt the `original` line.",
                "`out[i] = a[a.length - 1 - i]` fills the new array in one forward pass.",
                "Seed `max` with `a[0]`; the all-negative case is in the hidden tests."]),
    example_io="stdin:  5\n        3 1 4 1 5\n        2\n\n"
               "stdout: sum=14\n        max=5\n        count=3\n"
               "        reversed=[5, 1, 4, 1, 3]\n        original=[3, 1, 4, 1, 5]",
    rubric=[
        "Four separate `static` methods, each doing one job, with `main` only wiring them up.",
        "`reversed` allocates a new array — the `original` line proves the input survived.",
        "`max` is seeded from `a[0]`, so an all-negative array works.",
        "`countGreater` counts strictly greater, so an element equal to `k` is excluded.",
        "Every method uses `a.length` rather than expecting a separate length parameter.",
        "All five lines print, in order, with no spaces around `=`.",
    ],
)


_MODULES.append(_jmod(
    9, 3, "Methods and recursion",
    "Methods",
    "Turn loops into named, reusable, testable pieces — and understand exactly what "
    "happens to an argument when you pass it, which is the question behind half of "
    "Java's confusing behaviour.",
    """
Part 3 is about giving code a name. Everything you have written so far has
lived in one `main`; from here it lives in methods, which is what makes it
reusable, testable, and readable.

The module's centre is lesson 9.3. **Java is always pass-by-value** — one
sentence that explains why you cannot write `swap(int, int)`, why a method
*can* rewrite your array, and why it *cannot* replace it. That is module 1's
aliasing lesson arriving through a parameter list, and it is the single most
commonly misexplained thing in Java.

Everything else here is vocabulary: signatures, `void`, overloading, scope,
static fields and varargs. Useful, and much easier once passing makes sense.
""",
    _M9,
    capstone=_M9_CAP,
    objectives=[
        "Write a method signature from scratch and say why every helper beside `main` is `static`.",
        "Use `return` as control flow — guard clauses and early exits — and satisfy the every-path rule.",
        "State that Java is always pass-by-value, and predict what a method can and cannot change.",
        "Overload a method, and explain why the return type is excluded from the signature.",
        "Reason about scope, shadowing, and when a `static` field is the right tool.",
        "Write and call a varargs method, and give the three rules that constrain it.",
    ],
    why="\"Is Java pass-by-value or pass-by-reference?\" is asked in interviews constantly "
        "and answered wrongly most of the time. Beyond that, extracting a method is the "
        "single change that most improves code you have already written.",
    est_minutes=300,
    glossary=[
        _jg("signature", "A method's name plus its parameter types. The return type is NOT "
                         "part of it."),
        _jg("parameter", "The placeholder in the declaration: `int x`. A local variable of "
                         "the method."),
        _jg("argument", "The actual value at the call site: `f(5)`. It is copied into the "
                        "parameter."),
        _jg("void", "A return type meaning 'no result'. A bare `return;` still exits early."),
        _jg("guard clause", "An early return that handles an exceptional case first, keeping "
                            "the main path unindented."),
        _jg("pass-by-value", "The argument is copied into the parameter. For objects the copy "
                             "is of the reference, so the object is shared but the variable "
                             "is not."),
        _jg("overloading", "Several methods with one name and different parameter lists, "
                           "resolved at COMPILE time from the argument types."),
        _jg("scope", "The region where a name is visible: from its declaration to the end of "
                     "its enclosing block."),
        _jg("shadowing", "A local variable with the same name as a field, hiding it for the "
                         "rest of that method."),
        _jg("static", "Belongs to the class rather than to an object. Static methods can call "
                      "static methods; static fields are one shared copy."),
        _jg("varargs", "`int... xs` — any number of arguments, received as an array. Must be "
                       "the last parameter."),
    ],
    cheatsheet="""
```java
// --- anatomy ------------------------------------------------------------
static int add(int a, int b) { return a + b; }
//     ^^^ ^^^ ^^^^^^^^^^^^
//     |   |   parameters          signature = add(int, int)
//     |   return type             (the return type is NOT part of it)
//     modifier: needed to be callable from static main

// --- return as control flow --------------------------------------------
static int indexOf(int[] a, int target) {
    for (int i = 0; i < a.length; i++)
        if (a[i] == target) return i;      // leaves loop AND method
    return -1;                              // every path must return
}
static void f(int x) { if (x <= 0) return; ... }     // guard clause

// --- passing (ALWAYS by value) -----------------------------------------
static void inc(int x)      { x++; }             // caller unaffected
static void fill(int[] a)   { a[0] = 9; }        // caller DOES see this
static void swapOut(int[] a){ a = new int[3]; }  // caller unaffected
static String up(String s)  { return s.toUpperCase(); }   // return it

// --- overloading (compile-time; exact > widening > boxing > varargs) ---
static int  area(int side)          { ... }
static int  area(int w, int h)      { ... }
// static double area(int side)     // ERROR: same signature

// --- scope --------------------------------------------------------------
static int count = 0;                // field: outlives every call
static void f() {
    int local = 0;                    // dies at the closing brace
    for (int i = 0; ...) { }          // i dies with the loop
    // int count = 0;                 // would SHADOW the field
}

// --- varargs (last parameter only; empty array, never null) ------------
static int sum(int... xs) { int t = 0; for (int x : xs) t += x; return t; }
static int largest(int first, int... rest) { ... }
sum();  sum(1);  sum(1, 2, 3);  sum(new int[]{1, 2, 3});
```
""",
    self_check=[
        "Can you write a method signature from memory and say what each part is called?",
        "Can you explain why every helper beside `main` needs `static`, in terms of what `static` means?",
        "Can you say in one sentence how Java passes arguments, and defend it with the reassignment example?",
        "Can you explain why `swap(int, int)` is impossible but `swap(int[], int, int)` works?",
        "Can you say why two methods cannot differ only in return type?",
        "Would you spot an accidental shadowing bug in a code review?",
        "Can you give the three rules for varargs?",
    ],
    review=[
        _jq("```java\nstatic void f(int[] a) { a[0] = 99; a = new int[]{1}; }\nint[] x = {5, 6}; f(x);\nSystem.out.println(x[0] + \" \" + x.length);\n```",
            ["99 2", "1 1", "5 2", "99 1"],
            0,
            "Writing `a[0]` changes the shared object, so the caller sees 99. Reassigning `a` "
            "only repoints the method's own copy, so the caller's array is still length 2."),
        _jq("`static int f(int x) { if (x > 0) return 1; }` — what does the compiler say?",
            ["Missing return statement",
             "Nothing; it returns 0 when x <= 0",
             "Unreachable statement",
             "Nothing; it returns null"],
            0,
            "Every path out of a value-returning method must return. The compiler will not "
            "invent a default."),
        _jq("A method needs to give its caller back two values. What are your options in Part 3's toolkit?",
            ["Return an array, or write into an array the caller passed in",
             "Use two return statements",
             "Declare the parameters final",
             "Use pass-by-reference"],
            0,
            "There is no tuple and no out-parameter. Later parts add classes and records, "
            "which are the real answer."),
        _jq("Which pair is a valid overload?",
            ["f(int) and f(int, int)", "int f(int) and double f(int)",
             "f(int a) and f(int b)", "f(int...) and f(int[])"],
            0,
            "Only the parameter LIST distinguishes overloads. Different names, different "
            "return types, and varargs-versus-array all fail to."),
    ],
    milestone="You can factor a program into named methods, and you can answer \"is Java "
              "pass-by-value or pass-by-reference?\" correctly and prove it — which puts you "
              "ahead of most people who have been writing Java for years.",
))
