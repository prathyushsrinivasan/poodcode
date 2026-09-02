# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 1 — Arrays in memory.
#
# exec()'d by tools/java_course.py inside its namespace; appends one module to
# `_MODULES`. See that file's header for the helpers and the design rules.
#
# The opening module deliberately does NOT teach "what is an array" — the
# course assumes you can already declare one and loop over it. It teaches the
# things people who "know arrays" still get wrong: that the length is baked in
# at creation, that `b = a` is not a copy, that an enhanced `for` hands you a
# copy of each primitive, and that seeding a max with 0 quietly breaks on
# negative data.
# ---------------------------------------------------------------------------

_M1 = []

# --- 1.1 What an array actually is -----------------------------------------

_MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_M1.append(_jlesson(
    "m1-memory", "What an array actually is",
    "One heap object, a fixed length, and slots that start at a default value.",
    """
You have written `int[] a = new int[5];` before. Here is what that line really
does, because every array bug in this module comes from one of these facts.

**`a` is a reference, not the array.** The array is a single object on the
heap. `a` is a variable holding its address. Two variables can hold the same
address — that is the whole of lesson 1.6.

**The length is baked in at creation and can never change.** `a.length` is a
`final` field on the object. There is no `add`, no `remove`, no resize. Growing
an array means allocating a new one and copying — which is exactly what
`ArrayList` does for you later in the roadmap.

**Every slot starts at the type's default,** not at garbage:

| Element type | Default |
|---|---|
| `int`, `long`, `short`, `byte` | `0` |
| `double`, `float` | `0.0` |
| `char` | `'\\u0000'` (prints as nothing) |
| `boolean` | `false` |
| any object type (`String`, `int[]`, …) | `null` |

**`length` on an array is a field; on a String it is a method.**

```java
int[] a = new int[5];
System.out.println(a.length);     // 5   — no parentheses, it is a field
// "hello".length()               //     — parentheses, it is a method
```

Getting this backwards is the single most common Java compile error in week
one, and it never fully stops happening.

**Two ways to make one.**

```java
int[] a = new int[5];                 // 5 slots, all 0
int[] b = {3, 1, 4, 1, 5};            // literal — length inferred as 5
int[] c = new int[]{3, 1, 4};         // the long form of the same thing
```

The short literal form only works **in the declaration**. `int[] d; d = {1,2};`
does not compile — you need `d = new int[]{1, 2};`.

**Valid indices are `0` to `a.length - 1`.** Anything else throws
`ArrayIndexOutOfBoundsException` at runtime — not at compile time, which is why
an off-by-one in a loop condition survives all the way to a crash.
""",
    warmup=[
        _jq("What does this print?\n```java\nint[] a = new int[3];\nSystem.out.println(a[2]);\n```",
            ["0", "null", "an unpredictable value", "ArrayIndexOutOfBoundsException"],
            0,
            "`new int[3]` zero-fills every slot. Java never hands you uninitialized array "
            "memory — that is a C habit. If the element type were `String`, you would get "
            "`null` instead."),
        _jq("Which line does NOT compile?\n```java\nint[] a = new int[5];      // 1\nint[] b = {1, 2, 3};       // 2\nint[] c;  c = {1, 2, 3};   // 3\nint[] d = new int[]{1, 2}; // 4\n```",
            ["Line 3", "Line 1", "Line 2", "Line 4"],
            0,
            "The bare `{1, 2, 3}` shorthand is only legal in a declaration. Assigning later "
            "needs the explicit `new int[]{1, 2, 3}`."),
    ],
    exercises=[
        _je("j1-mem-default", "Allocate the slots",
            "Read `n`, then create an `int` array with `n` slots and print it. "
            "Replace `____` with the allocation — and notice what the slots hold "
            "before you have written anything into them.",
            _jscan(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        System.out.println(Arrays.toString(a));"),
            "new int[n]",
            [_case(3, _jarr([0] * 3)), _case(1, _jarr([0] * 1)), _case(6, _jarr([0] * 6))],
            hints=["`new int[n]` allocates n slots.",
                   "The size goes in the square brackets, not in parentheses.",
                   "`new int[n]` — and every slot comes back as 0."],
            difficulty="Intro"),

        _je("j1-mem-length", "Field, not method",
            "The array is already filled. Replace `____` so the program prints how "
            "many elements it holds. Careful: this is an array, not a String.",
            _jscan(_RD_ARR + "        System.out.println(a.length);"),
            "a.length",
            [_acase([4, 8, 15, 16], str(len([4, 8, 15, 16]))),
             _acase([7], str(1)),
             _acase([2, 2, 2, 2, 2, 2, 2], str(7))],
            hints=["Arrays expose length as a *field*.",
                   "No parentheses — `a.length()` will not compile.",
                   "`a.length`"],
            difficulty="Intro"),

        _je("j1-mem-literal", "Index from zero",
            "`days` holds the number of days in each month, January first. Read a "
            "month number `k` (1 = January) and print that month's length. Replace "
            "`____` with the expression that reaches the right slot.",
            _jscan(
                "        int k = sc.nextInt();\n"
                "        int[] days = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};\n"
                "        System.out.println(days[k - 1]);"),
            "days[k - 1]",
            [_case(k, _MONTH_DAYS[k - 1]) for k in (1, 2, 9, 12)],
            hints=["January is month 1 but lives at index 0.",
                   "Every index is one less than the month number.",
                   "`days[k - 1]`"],
            difficulty="Intro"),

        _jfix("j1-mem-oob", "One step too far",
              "This should print the sum of the array, but it crashes with "
              "`ArrayIndexOutOfBoundsException`. Find the bug and fix it.",
              _jscan(
                  _RD_ARR
                  + "        int sum = 0;\n"
                    "        for (int i = 0; i <= n; i++) sum += a[i];\n"
                    "        System.out.println(sum);"),
              _jscan(
                  _RD_ARR
                  + "        int sum = 0;\n"
                    "        for (int i = 0; i < n; i++) sum += a[i];\n"
                    "        System.out.println(sum);"),
              [_acase(a, sum(a)) for a in ([1, 2, 3, 4], [10], [-5, 5, -5, 5, 100])],
              hints=["Look at the loop's stopping condition.",
                     "With n elements the last valid index is n - 1.",
                     "`i <= n` should be `i < n`."],
              difficulty="Intro"),

        _jch("j1-mem-squares", "Build a table", "Easy",
             "Read `n`, then build an array whose slot `i` holds `(i + 1)` squared, "
             "and print it with `Arrays.toString`. For `n = 4` that is "
             "`[1, 4, 9, 16]`. Write the whole block where you see `____`.",
             _jscan(
                 "        int n = sc.nextInt();\n"
                 "        int[] sq = new int[n];\n"
                 "        for (int i = 0; i < n; i++) sq[i] = (i + 1) * (i + 1);\n"
                 "        System.out.println(Arrays.toString(sq));"),
             "        int[] sq = new int[n];\n"
             "        for (int i = 0; i < n; i++) sq[i] = (i + 1) * (i + 1);\n"
             "        System.out.println(Arrays.toString(sq));",
             [_case(n, _jarr([(i + 1) ** 2 for i in range(n)])) for n in (1, 4, 6)],
             hints=["Allocate `new int[n]` first — you cannot grow it later.",
                    "Index `i` should hold `(i + 1) * (i + 1)`, because index 0 is the first square.",
                    "`Arrays.toString(sq)` prints it in the `[1, 4, 9, 16]` shape."]),
    ],
    quiz=[
        _jq("Why does `int[] a = new int[3]; a.length = 5;` fail to compile?",
            ["`length` is a final field — an array's size is fixed at creation",
             "You must call `a.setLength(5)` instead",
             "You can only resize an array before writing to it",
             "It compiles, but silently does nothing"],
            0,
            "Array length is immutable. To 'grow' one you allocate a bigger array and copy "
            "(`Arrays.copyOf`) — which is what `ArrayList` does under the hood."),
        _jq("`String[] names = new String[3];` — what is `names[0]`?",
            ["null", "\"\" (the empty string)", "0", "It throws until you assign it"],
            0,
            "Object element types default to `null`, not to an empty object. Reading it is "
            "fine; calling a method on it is a `NullPointerException`."),
    ],
))

# --- 1.2 Traversal ----------------------------------------------------------

_M1.append(_jlesson(
    "m1-traverse", "Two ways to walk an array",
    "The index loop, the enhanced for, and the moment you must not use the second one.",
    """
There are exactly two loops you need, and choosing wrongly is a bug, not a
style opinion.

**The index loop — when you need `i`.**

```java
for (int i = 0; i < a.length; i++) {
    System.out.println(i + ": " + a[i]);
}
```

Use it when you need the position, when you need to **write** into the array,
when you walk backwards, or when you skip (`i += 2`).

**The enhanced for ("for-each") — when you only need the values.**

```java
for (int x : a) {
    sum += x;
}
```

Read it as "for each int x in a". Shorter, and impossible to get an off-by-one
wrong, because there is no index to get wrong.

**The trap.** For a primitive array, `x` is a **copy** of the element. Writing
to `x` changes the copy and nothing else:

```java
int[] a = {1, 2, 3};
for (int x : a) x = x * 2;
System.out.println(Arrays.toString(a));   // [1, 2, 3] — unchanged!
```

To actually modify the array you need the index:

```java
for (int i = 0; i < a.length; i++) a[i] = a[i] * 2;   // [2, 4, 6]
```

The rule of thumb that never fails: **reading → for-each; writing → index.**

**Backwards** is just the index loop run in reverse, and it is worth being able
to write without thinking:

```java
for (int i = a.length - 1; i >= 0; i--) { ... }
```

Start at `length - 1` (the last valid index), stop at `>= 0` (index 0 is real
data). `i > 0` would silently skip the first element.
""",
    warmup=[
        _jq("What does this print?\n```java\nint[] a = {1, 2, 3};\nfor (int x : a) x = x * 10;\nSystem.out.println(Arrays.toString(a));\n```",
            ["[1, 2, 3]", "[10, 20, 30]", "[0, 0, 0]", "It does not compile"],
            0,
            "`x` is a fresh copy of each element. Assigning to it changes the copy, and the "
            "array never hears about it. This compiles cleanly, which is what makes it "
            "dangerous."),
        _jq("How many elements does this loop visit?\n```java\nfor (int i = a.length - 1; i > 0; i--) System.out.print(a[i]);\n```",
            ["All but the first", "All of them", "All but the last", "None — it never runs"],
            0,
            "`i > 0` stops before index 0, so element `a[0]` is skipped. Walking backwards "
            "needs `i >= 0`."),
    ],
    exercises=[
        _je("j1-trav-sum", "For-each the sum",
            "Total the array. You only need the values, never the positions — so "
            "replace `____` with an enhanced `for` header that hands you each "
            "element as `x`.",
            _jscan(
                _RD_ARR
                + "        int sum = 0;\n"
                  "        for (int x : a) sum += x;\n"
                  "        System.out.println(sum);"),
            "for (int x : a)",
            [_acase(a, sum(a)) for a in ([3, 1, 4, 1, 5], [-2, -3], [42])],
            hints=["The shape is `for (Type name : array)`.",
                   "The element type is `int`.",
                   "`for (int x : a)`"],
            difficulty="Intro"),

        _je("j1-trav-index", "Position and value",
            "Print one line per element, formatted `index: value` — so `[7, 9]` "
            "prints `0: 7` then `1: 9`. Replace `____` with the text to print.",
            _jscan(
                _RD_ARR
                + '        for (int i = 0; i < n; i++) System.out.println(i + ": " + a[i]);'),
            'i + ": " + a[i]',
            [_acase(a, _nl(*[f"{i}: {v}" for i, v in enumerate(a)]))
             for a in ([7, 9], [5], [10, 20, 30, 40])],
            hints=["Glue the pieces with `+`.",
                   'The separator is a colon and a space: `": "`.',
                   '`i + ": " + a[i]`']),

        _jfix("j1-trav-double", "The doubling that never happened",
              "This should double every element and print the result, but the array "
              "comes back untouched. The loop is the problem — rewrite it so the "
              "array itself changes.",
              _jscan(
                  _RD_ARR
                  + "        for (int x : a) x = x * 2;\n"
                    "        System.out.println(Arrays.toString(a));"),
              _jscan(
                  _RD_ARR
                  + "        for (int i = 0; i < n; i++) a[i] = a[i] * 2;\n"
                    "        System.out.println(Arrays.toString(a));"),
              [_acase(a, _jarr([x * 2 for x in a]))
               for a in ([1, 2, 3], [-4, 0, 7], [5])],
              hints=["`x` in a for-each is a copy of the element, not the slot itself.",
                     "To write into the array you need the index.",
                     "Swap the for-each for `for (int i = 0; i < n; i++) a[i] = a[i] * 2;`"]),

        _jch("j1-trav-even", "Every other one", "Easy",
             "Print the elements at **even indices** (0, 2, 4, …) on one line, "
             "separated by spaces. For `[10, 20, 30, 40, 50]` print `10 30 50`. "
             "Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + '        for (int i = 0; i < n; i += 2) System.out.print(a[i] + " ");\n'
                   "        System.out.println();"),
             '        for (int i = 0; i < n; i += 2) System.out.print(a[i] + " ");\n'
             "        System.out.println();",
             [_acase(a, _sp(a[::2]))
              for a in ([10, 20, 30, 40, 50], [1, 2], [9], [4, 4, 4, 4])],
             hints=["Even indices means stepping by 2 — this is an index loop, not a for-each.",
                    "`System.out.print` (no `ln`) keeps everything on one line.",
                    "A trailing space is fine; the judge trims it. End with a bare "
                    "`System.out.println();` so the line is terminated."]),
    ],
    quiz=[
        _jq("You need to replace every negative element with 0. Which loop?",
            ["The index loop — you are writing into the array",
             "The enhanced for — it is shorter",
             "Either; they behave identically",
             "The enhanced for, but you must declare `x` as `final`"],
            0,
            "Reading → for-each. Writing → index. The for-each variable is a copy for "
            "primitives, so assigning to it cannot change the array."),
        _jq("What is the last index the loop `for (int i = 0; i < a.length; i++)` visits?",
            ["a.length - 1", "a.length", "a.length + 1", "It depends on the element type"],
            0,
            "The condition is checked *before* each pass, so the loop stops the moment `i` "
            "reaches `a.length` — the last body run is at `a.length - 1`, the last valid index."),
    ],
))

# --- 1.3 Aggregates ---------------------------------------------------------


def _minmaxsum(a):
    return f"{max(a)} {min(a)} {sum(a)}"


_M1.append(_jlesson(
    "m1-aggregate", "Max, min, sum — and where the winner is",
    "One pass, a running answer, and the seed value that quietly breaks everything.",
    """
Almost every array question is a variation on "walk it once, keep a running
answer". Get the shape into your fingers:

```java
int max = a[0];                       // seed with REAL DATA
for (int i = 1; i < a.length; i++) {  // start at 1 — index 0 is already in
    if (a[i] > max) max = a[i];
}
```

**Never seed a max with `0`.** It is the most common bug in this whole module:

```java
int max = 0;                          // WRONG
int[] temps = {-4, -11, -7};
// ... loop ...
System.out.println(max);              // 0 — a temperature that never happened
```

Seeding with `a[0]` is always right, because `a[0]` is genuinely in the data.
(The other correct seed is `Integer.MIN_VALUE`, which is what you use when the
array might be empty and you want "no answer" to be obvious.)

**Sum is the exception** — seed it with `0`, because 0 is the identity for
addition. Seed a product with `1` for the same reason.

**Where the winner is.** Often you need the *index*, not the value. Track the
index and compare through it, so you never have to keep two variables in sync:

```java
int best = 0;
for (int i = 1; i < a.length; i++) {
    if (a[i] > a[best]) best = i;     // compare a[i] against a[best]
}
// value is a[best], position is best
```

Using `>` keeps the **first** of a tie; `>=` keeps the **last**. Interviewers
ask which one you want, so decide on purpose.

**Watch the overflow.** `int` tops out near 2.1 billion. Summing a long array
of large values silently wraps to a negative number — the fix is `long sum = 0;`.
It is worth saying out loud in an interview even when the test data is small.
""",
    warmup=[
        _jq("What does this print?\n```java\nint[] a = {-4, -11, -7};\nint max = 0;\nfor (int x : a) if (x > max) max = x;\nSystem.out.println(max);\n```",
            ["0", "-4", "-11", "It does not compile"],
            0,
            "Nothing in the array beats the seed, so the seed survives and the program "
            "reports a maximum that is not in the data. Seed with `a[0]`."),
        _jq("With `int best = 0;` and `if (a[i] > a[best]) best = i;`, which index wins a tie?",
            ["The first one", "The last one", "Undefined", "It throws on a tie"],
            0,
            "A later equal value fails the strict `>`, so `best` never moves. Use `>=` if "
            "you want the last occurrence instead."),
    ],
    exercises=[
        _je("j1-agg-max", "The running maximum",
            "`max` is already seeded with the first element. Replace `____` with "
            "the line that keeps it up to date as the loop walks the rest.",
            _jscan(
                _RD_ARR
                + "        int max = a[0];\n"
                  "        for (int i = 1; i < n; i++) {\n"
                  "            if (a[i] > max) max = a[i];\n"
                  "        }\n"
                  "        System.out.println(max);"),
            "if (a[i] > max) max = a[i];",
            [_acase(a, max(a)) for a in ([3, 9, 2], [-4, -11, -7], [5], [1, 1, 1, 1])],
            hints=["Compare the current element against the running maximum.",
                   "When it is bigger, the running maximum becomes it.",
                   "`if (a[i] > max) max = a[i];`"],
            difficulty="Intro"),

        _je("j1-agg-argmax", "Where the maximum lives",
            "Print the **index** of the largest element (the first one, if there is "
            "a tie). `best` tracks the position. Replace `____` with the condition "
            "that decides whether position `i` beats the current best.",
            _jscan(
                _RD_ARR
                + "        int best = 0;\n"
                  "        for (int i = 1; i < n; i++) {\n"
                  "            if (a[i] > a[best]) best = i;\n"
                  "        }\n"
                  "        System.out.println(best);"),
            "a[i] > a[best]",
            [_acase(a, a.index(max(a)))
             for a in ([3, 9, 2], [9, 9, 1], [1, 2, 3, 4], [-4, -11, -7])],
            hints=["`best` is an index, so the value at it is `a[best]`.",
                   "Compare values, assign indices.",
                   "`a[i] > a[best]` — strict `>` keeps the first of a tie."]),

        _jfix("j1-agg-zero", "A maximum that never happened",
              "This prints the largest element — except on data where every value is "
              "negative, when it reports `0`. Fix it so it always reports a value "
              "that is actually in the array.",
              _jscan(
                  _RD_ARR
                  + "        int max = 0;\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            if (a[i] > max) max = a[i];\n"
                    "        }\n"
                    "        System.out.println(max);"),
              _jscan(
                  _RD_ARR
                  + "        int max = a[0];\n"
                    "        for (int i = 1; i < n; i++) {\n"
                    "            if (a[i] > max) max = a[i];\n"
                    "        }\n"
                    "        System.out.println(max);"),
              [_acase(a, max(a)) for a in ([-4, -11, -7], [-1], [3, 9, 2])],
              hints=["Where does `max` start, and is that value in the array?",
                     "Seed with real data instead of an invented number.",
                     "`int max = a[0];` — and then start the loop at `i = 1`."]),

        _jch("j1-agg-minmax", "One pass, three answers", "Easy",
             "In a **single** pass, work out the maximum, the minimum and the sum, "
             "then print them on one line separated by spaces — `max min sum`. For "
             "`[3, 9, 2]` print `9 2 14`. Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int max = a[0];\n"
                   "        int min = a[0];\n"
                   "        int sum = 0;\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            if (a[i] > max) max = a[i];\n"
                   "            if (a[i] < min) min = a[i];\n"
                   "            sum += a[i];\n"
                   "        }\n"
                   '        System.out.println(max + " " + min + " " + sum);'),
             "        int max = a[0];\n"
             "        int min = a[0];\n"
             "        int sum = 0;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            if (a[i] > max) max = a[i];\n"
             "            if (a[i] < min) min = a[i];\n"
             "            sum += a[i];\n"
             "        }\n"
             '        System.out.println(max + " " + min + " " + sum);',
             [_acase(a, _minmaxsum(a))
              for a in ([3, 9, 2], [-4, -11, -7], [5], [2, 2, 2])],
             hints=["Seed max and min with `a[0]`, sum with `0`.",
                    "Three `if`/accumulate statements inside one loop — do not write three loops.",
                    "Starting the loop at `i = 0` is harmless here: comparing `a[0]` with itself "
                    "changes nothing."]),
    ],
    quiz=[
        _jq("Why is `0` a correct seed for a sum but a wrong seed for a maximum?",
            ["0 is the identity for addition, but it is a claim that the data contains a 0",
             "It isn't — `0` is wrong for both",
             "It isn't — `0` is fine for both, the loop fixes it",
             "Because `sum` is a `long` and `max` is an `int`"],
            0,
            "Adding 0 changes nothing, so it is a safe starting point. But a maximum seeded "
            "at 0 asserts that 0 is a candidate answer — false for all-negative data."),
        _jq("You are summing 100,000 values that each reach 100,000. What breaks, and how do you fix it?",
            ["`int` overflows and wraps negative — declare `long sum = 0;`",
             "Nothing; Java promotes automatically",
             "It throws ArithmeticException — catch it",
             "The array is too big to allocate"],
            0,
            "10^10 is far past `int`'s ~2.1 billion ceiling. Java wraps silently rather than "
            "throwing, so the only symptom is a wrong (often negative) answer."),
    ],
))

# --- 1.4 Linear search ------------------------------------------------------

_M1.append(_jlesson(
    "m1-search", "Linear search",
    "Walk until you find it, report -1 when you don't, and stop as soon as you can.",
    """
Linear search is the only search that works on **unsorted** data, and its shape
is worth memorising because half of the array questions in this course are a
variation on it.

```java
int idx = -1;                              // "not found" sentinel
for (int i = 0; i < a.length; i++) {
    if (a[i] == target) { idx = i; break; }
}
System.out.println(idx);
```

Three decisions are baked into those five lines.

**`-1` is the convention for "not found".** It is not special to Java — it is a
value that cannot be a valid index, so callers can test `if (idx == -1)` with no
ambiguity. `String.indexOf` returns `-1` too, and so will your own methods in
module 9.

**`break` matters.** Without it the loop keeps going and `idx` ends up holding
the *last* match rather than the first. That is a real bug, not an
inefficiency — see the fix-the-bug below.

**First or last is a choice.** Want the last occurrence instead? Do not
add a flag; just walk backwards and break:

```java
for (int i = a.length - 1; i >= 0; i--) {
    if (a[i] == target) { idx = i; break; }
}
```

**Counting is the version with no `break`,** because you want to see every
match:

```java
int count = 0;
for (int i = 0; i < a.length; i++) if (a[i] == target) count++;
```

**Cost.** Best case 1 comparison, worst case `n`, average `n/2` — so O(n). You
cannot do better on unsorted data, because any element you did not look at
could have been the one. That sentence is the whole justification for sorting
first, which is module 3.
""",
    warmup=[
        _jq("`a = {4, 7, 4, 9}`, target `4`. What does this print?\n```java\nint idx = -1;\nfor (int i = 0; i < a.length; i++) if (a[i] == 4) idx = i;\nSystem.out.println(idx);\n```",
            ["2", "0", "-1", "1"],
            0,
            "Without a `break` the loop runs to the end, so the *last* match overwrites the "
            "first. If you wanted the first index, this is a bug."),
        _jq("Why is `-1` used for 'not found' rather than `0`?",
            ["0 is a valid index, so it could not be told apart from a real hit",
             "-1 is faster to compare against",
             "Java requires it",
             "0 means 'not found' only for empty arrays"],
            0,
            "A sentinel has to be a value the real answer can never take. Index 0 is a "
            "perfectly good hit, so it cannot double as failure."),
    ],
    exercises=[
        _je("j1-search-index", "First occurrence",
            "Read the array, then a `target`. Print the index of its **first** "
            "occurrence, or `-1` if it is not there. Replace `____` with what "
            "happens when the element matches.",
            _jscan(
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        int idx = -1;\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            if (a[i] == target) { idx = i; break; }\n"
                  "        }\n"
                  "        System.out.println(idx);"),
            "{ idx = i; break; }",
            [_akcase(a, t, a.index(t) if t in a else -1)
             for (a, t) in (([4, 7, 4, 9], 4), ([4, 7, 4, 9], 9), ([4, 7, 4, 9], 5), ([1], 1))],
            hints=["Record the position, then stop looking.",
                   "Two statements go inside the braces.",
                   "`{ idx = i; break; }`"]),

        _je("j1-search-count", "How many times",
            "Count how many elements equal `target` and print the count. Replace "
            "`____` with the whole `if` statement. (No `break` this time — think "
            "about why.)",
            _jscan(
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        int count = 0;\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            if (a[i] == target) count++;\n"
                  "        }\n"
                  "        System.out.println(count);"),
            "if (a[i] == target) count++;",
            [_akcase(a, t, a.count(t))
             for (a, t) in (([4, 7, 4, 9], 4), ([1, 1, 1], 1), ([4, 7], 5))],
            hints=["Compare with `==`, then bump the counter.",
                   "Breaking early would stop you finding the rest.",
                   "`if (a[i] == target) count++;`"],
            difficulty="Intro"),

        _jfix("j1-search-first", "It finds the wrong one",
              "This should print the index of the **first** occurrence of `target`. "
              "On `[4, 7, 4, 9]` looking for `4` it prints `2` instead of `0`. Fix it.",
              _jscan(
                  _RD_ARR
                  + "        int target = sc.nextInt();\n"
                    "        int idx = -1;\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            if (a[i] == target) idx = i;\n"
                    "        }\n"
                    "        System.out.println(idx);"),
              _jscan(
                  _RD_ARR
                  + "        int target = sc.nextInt();\n"
                    "        int idx = -1;\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            if (a[i] == target) { idx = i; break; }\n"
                    "        }\n"
                    "        System.out.println(idx);"),
              [_akcase(a, t, a.index(t) if t in a else -1)
               for (a, t) in (([4, 7, 4, 9], 4), ([2, 2, 2], 2), ([4, 7], 9))],
              hints=["The loop keeps running after it has already found the answer.",
                     "A later match overwrites the earlier one.",
                     "`{ idx = i; break; }` — stop as soon as you have it."]),

        _jch("j1-search-last", "Last occurrence", "Easy",
             "Print the index of the **last** occurrence of `target`, or `-1`. Do it "
             "by walking the array backwards and stopping at the first hit — no flag "
             "variable. Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int target = sc.nextInt();\n"
                   "        int idx = -1;\n"
                   "        for (int i = n - 1; i >= 0; i--) {\n"
                   "            if (a[i] == target) { idx = i; break; }\n"
                   "        }\n"
                   "        System.out.println(idx);"),
             "        int idx = -1;\n"
             "        for (int i = n - 1; i >= 0; i--) {\n"
             "            if (a[i] == target) { idx = i; break; }\n"
             "        }\n"
             "        System.out.println(idx);",
             [_akcase(a, t, (len(a) - 1 - a[::-1].index(t)) if t in a else -1)
              for (a, t) in (([4, 7, 4, 9], 4), ([4, 7, 4, 9], 9), ([4, 7], 5), ([3, 3, 3], 3))],
             hints=["Start at `n - 1`, count down, stop at `>= 0`.",
                    "`i > 0` would skip index 0 — a real element.",
                    "The first hit going backwards *is* the last occurrence going forwards."]),
    ],
    quiz=[
        _jq("What is the worst-case cost of linear search over n elements, and why can't you beat it on unsorted data?",
            ["O(n) — any element you skipped could have been the match",
             "O(log n) — you can halve the range each time",
             "O(1) — the JIT caches the array",
             "O(n²) — each comparison rescans"],
            0,
            "Without order there is no information linking one element to the next, so "
            "skipping any element risks missing the answer. That is exactly why module 3 "
            "sorts first."),
        _jq("You need the last occurrence. Which is better: forward loop with no break, or backward loop with break?",
            ["Backward with break — same answer, and it stops early",
             "Forward with no break — clearer to read",
             "They are identical in every way",
             "Neither works; you need two passes"],
            0,
            "Both are O(n) worst case, but the backward loop stops at the first hit it "
            "meets, which is often much sooner — and it needs no 'have I seen one yet' flag."),
    ],
))

# --- 1.5 The Arrays utility class ------------------------------------------

_M1.append(_jlesson(
    "m1-utils", "The `Arrays` utility class",
    "The handful of `java.util.Arrays` calls worth knowing by heart.",
    """
`java.util.Arrays` is a bag of `static` helpers for arrays. You get it with
`import java.util.*;` (already at the top of every program in this course).
These are the ones that earn their place:

| Call | What it does |
|---|---|
| `Arrays.toString(a)` | `"[3, 1, 4]"` — the printable form of a 1D array |
| `Arrays.fill(a, v)` | writes `v` into every slot, in place |
| `Arrays.copyOf(a, len)` | a **new** array of length `len`; truncates or zero-pads |
| `Arrays.copyOfRange(a, from, to)` | a new array of `a[from]` … `a[to - 1]` |
| `Arrays.equals(a, b)` | `true` when same length and same elements, in order |
| `Arrays.sort(a)` | sorts in place (module 3 — hand-write it first) |
| `Arrays.deepToString(m)` | printable form of a 2D array (module 2) |

**`toString` is the one that saves you an hour.** Printing an array directly
gives you `[I@1b6d3586` — the type tag and a hash, not the contents:

```java
System.out.println(a);                    // [I@1b6d3586
System.out.println(Arrays.toString(a));   // [3, 1, 4]
```

**`copyOfRange` is half-open:** `from` is included, `to` is excluded, so the
new length is exactly `to - from`. Every range API in Java works this way
(`substring` in module 6 included), so it is worth getting comfortable now.

**`copyOf` doubles as "grow":**

```java
int[] bigger = Arrays.copyOf(a, a.length + 1);   // last slot is 0
bigger[a.length] = 99;                            // ...now it is 99
```

That is literally how `ArrayList` grows, minus the bookkeeping.

**`Arrays.equals` vs `==`.** `a == b` asks "are these the same object?".
`Arrays.equals(a, b)` asks "do these hold the same values?". You almost always
want the second, and the difference is the same trap that `String` `==` sets
in module 6.
""",
    warmup=[
        _jq("What does `System.out.println(new int[]{1, 2, 3});` print?",
            ["Something like `[I@1b6d3586`", "`[1, 2, 3]`", "`123`", "It does not compile"],
            0,
            "Arrays do not override `toString()`, so you get the default "
            "`type@hashcode` form. `Arrays.toString(a)` is the fix."),
        _jq("`Arrays.copyOfRange(a, 1, 4)` on `{10, 20, 30, 40, 50}` gives what?",
            ["[20, 30, 40]", "[20, 30, 40, 50]", "[10, 20, 30, 40]", "[20, 30]"],
            0,
            "`from` is inclusive and `to` is exclusive, so you get indices 1, 2, 3 — length "
            "`to - from` = 3."),
    ],
    exercises=[
        _je("j1-util-fill", "Fill it in",
            "Read `n` and `v`, then set every slot of the array to `v` and print it. "
            "Replace `____` with the one call that does it — no loop.",
            _jscan(
                "        int n = sc.nextInt();\n"
                "        int v = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        Arrays.fill(a, v);\n"
                "        System.out.println(Arrays.toString(a));"),
            "Arrays.fill(a, v);",
            [_case(f"{n} {v}", _jarr([v] * n)) for (n, v) in ((3, 7), (1, -2), (5, 0))],
            hints=["It lives on `Arrays` and takes the array first.",
                   "It modifies the array in place and returns nothing.",
                   "`Arrays.fill(a, v);`"],
            difficulty="Intro"),

        _je("j1-util-range", "A slice of it",
            "Read the array, then `from` and `to`. Print the slice `a[from]` up to "
            "**but not including** `a[to]`. Replace `____` with the call.",
            _jscan(
                _RD_ARR
                + "        int from = sc.nextInt();\n"
                  "        int to = sc.nextInt();\n"
                  "        int[] part = Arrays.copyOfRange(a, from, to);\n"
                  "        System.out.println(Arrays.toString(part));"),
            "Arrays.copyOfRange(a, from, to)",
            [_case(f"{len(a)}\n{_sp(a)}\n{f_}\n{t}", _jarr(a[f_:t]))
             for (a, f_, t) in (([10, 20, 30, 40, 50], 1, 4),
                                ([10, 20, 30, 40, 50], 0, 5),
                                ([10, 20, 30, 40, 50], 2, 3))],
            hints=["Three arguments: the array, then the two bounds.",
                   "It returns a new array — it does not modify `a`.",
                   "`Arrays.copyOfRange(a, from, to)`"]),

        _je("j1-util-equals", "Same values?",
            "Read two arrays and print `true` when they hold the same elements in "
            "the same order, otherwise `false`. Replace `____` with the expression. "
            "(`a == b` would always print `false` here — think about why.)",
            _jscan(_RD_ARR2 + "        System.out.println(Arrays.equals(a, b));"),
            "Arrays.equals(a, b)",
            [_a2case(a, b, _jbool(a == b))
             for (a, b) in (([1, 2, 3], [1, 2, 3]), ([1, 2, 3], [1, 2]),
                            ([1, 2], [2, 1]), ([5], [5]))],
            hints=["`Arrays` has a method for exactly this comparison.",
                   "`==` on two arrays compares references, and these are two different objects.",
                   "`Arrays.equals(a, b)`"]),

        _jch("j1-util-grow", "Append to a fixed-size array", "Easy",
             "Arrays cannot grow — so make a longer one. Read the array and a value "
             "`v`, then print an array that is `a` with `v` appended. Use "
             "`Arrays.copyOf`, not a manual loop. Write the whole block where you "
             "see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int v = sc.nextInt();\n"
                   "        int[] bigger = Arrays.copyOf(a, n + 1);\n"
                   "        bigger[n] = v;\n"
                   "        System.out.println(Arrays.toString(bigger));"),
             "        int[] bigger = Arrays.copyOf(a, n + 1);\n"
             "        bigger[n] = v;\n"
             "        System.out.println(Arrays.toString(bigger));",
             [_akcase(a, v, _jarr(a + [v]))
              for (a, v) in (([1, 2, 3], 9), ([7], 0), ([-1, -2], -3))],
             hints=["`Arrays.copyOf(a, n + 1)` gives you the old values plus one 0 slot.",
                    "The new slot is at index `n` — the old length is the new last index.",
                    "Three lines: copy, assign, print."]),
    ],
    quiz=[
        _jq("What is the length of `Arrays.copyOfRange(a, 2, 2)`?",
            ["0 — an empty array", "1", "It throws IllegalArgumentException", "a.length - 2"],
            0,
            "The length is always `to - from`. An empty range is legal and gives an empty "
            "array; only `from > to` throws."),
        _jq("`int[] a = {1,2}; int[] b = {1,2};` — what do `a == b` and `Arrays.equals(a, b)` give?",
            ["false and true", "true and true", "false and false", "true and false"],
            0,
            "They are two distinct objects, so `==` (reference identity) is false, while "
            "`Arrays.equals` compares contents and is true."),
    ],
))

# --- 1.6 Aliasing vs copying ------------------------------------------------

_M1.append(_jlesson(
    "m1-alias", "`b = a` is not a copy",
    "Reference semantics, the bug it causes, and the three ways to actually copy.",
    """
This is the lesson that separates people who "know arrays" from people who can
be trusted with them.

**An array variable holds a reference.** Assigning it copies the *reference*,
not the array:

```java
int[] a = {1, 2, 3};
int[] b = a;          // b and a now point at the SAME object
b[0] = 99;
System.out.println(a[0]);   // 99  — you changed "both", because there is one array
```

There was only ever one array. `a` and `b` are two names for it — they are
**aliases**. Nothing was copied and nothing was cloned.

**Three ways to make a real copy:**

```java
int[] c = Arrays.copyOf(a, a.length);          // clearest, and can resize
int[] d = a.clone();                            // shortest
int[] e = new int[a.length];
System.arraycopy(a, 0, e, 0, a.length);         // fastest, ugliest, rarely needed
```

All three are **shallow**. For an `int[]` that is a full copy, because the
elements *are* the values. For an array of objects — or a 2D array, which is an
array of arrays (module 2) — you get new outer slots pointing at the **same**
inner objects. `copyOf` on an `int[][]` does not protect the rows.

**Where it bites.** "Keep a backup before I sort/modify" is the classic:

```java
int[] backup = a;      // NOT a backup — it is a second label on the same array
// ...modify a...
// backup is modified too, and the original is gone forever
```

**Swapping** is the other place references matter — or rather, don't:

```java
int temp = a[i];
a[i] = a[j];
a[j] = temp;
```

You need the temp because the first assignment destroys `a[i]`. Every reversal,
rotation and sort in modules 3 and 4 is built out of this three-line move, so
make it automatic.
""",
    warmup=[
        _jq("What does this print?\n```java\nint[] a = {1, 2, 3};\nint[] b = a;\nb[0] = 99;\nSystem.out.println(a[0]);\n```",
            ["99", "1", "0", "It does not compile"],
            0,
            "`b = a` copies the reference. There is one array with two names, so writing "
            "through `b` is writing through `a`."),
        _jq("Why does swapping `a[i]` and `a[j]` need a temp variable?",
            ["The first assignment overwrites one of the values before it is read",
             "Java forbids assigning two array slots in one statement",
             "It does not — `a[i] = a[j]; a[j] = a[i];` works",
             "Because arrays are passed by reference"],
            0,
            "`a[i] = a[j]` destroys the old `a[i]`, so the second assignment would copy the "
            "value back onto itself and both slots end up holding `a[j]`."),
    ],
    exercises=[
        _je("j1-alias-copy", "A copy that is really a copy",
            "The program takes a copy, scribbles on the copy, and prints the "
            "**original** — which must come back untouched. Replace `____` with the "
            "expression that makes a genuine copy.",
            _jscan(
                _RD_ARR
                + "        int[] copy = Arrays.copyOf(a, n);\n"
                  "        copy[0] = 999;\n"
                  "        System.out.println(Arrays.toString(a));"),
            "Arrays.copyOf(a, n)",
            [_acase(a, _jarr(a)) for a in ([1, 2, 3], [7], [-5, 0, 5])],
            hints=["`= a` would alias, not copy.",
                   "`Arrays.copyOf` takes the array and the new length.",
                   "`Arrays.copyOf(a, n)`"]),

        _jfix("j1-alias-bug", "The backup that wasn't",
              "This is meant to snapshot the array, zero out the first element, then "
              "print the **snapshot** — which should still show the original first "
              "element. It prints `0` instead. Fix the snapshot.",
              _jscan(
                  _RD_ARR
                  + "        int[] backup = a;\n"
                    "        a[0] = 0;\n"
                    "        System.out.println(Arrays.toString(backup));"),
              _jscan(
                  _RD_ARR
                  + "        int[] backup = Arrays.copyOf(a, n);\n"
                    "        a[0] = 0;\n"
                    "        System.out.println(Arrays.toString(backup));"),
              [_acase(a, _jarr(a)) for a in ([4, 5, 6], [9], [-1, -2, -3])],
              hints=["How many array objects does this program actually create?",
                     "`backup = a` gives the same array a second name.",
                     "`int[] backup = Arrays.copyOf(a, n);` (or `a.clone()`)."]),

        _jch("j1-alias-swap", "Swap two slots", "Easy",
             "Read the array, then two indices `i` and `j`. Swap those two elements "
             "and print the array. Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int i = sc.nextInt();\n"
                   "        int j = sc.nextInt();\n"
                   "        int temp = a[i];\n"
                   "        a[i] = a[j];\n"
                   "        a[j] = temp;\n"
                   "        System.out.println(Arrays.toString(a));"),
             "        int temp = a[i];\n"
             "        a[i] = a[j];\n"
             "        a[j] = temp;\n"
             "        System.out.println(Arrays.toString(a));",
             [_case(f"{len(a)}\n{_sp(a)}\n{i}\n{j}",
                    _jarr([a[j] if k == i else a[i] if k == j else a[k] for k in range(len(a))]))
              for (a, i, j) in (([10, 20, 30, 40], 0, 3),
                                ([10, 20, 30, 40], 1, 2),
                                ([5, 6], 0, 1),
                                ([1, 2, 3], 1, 1))],
             hints=["Save one value before you overwrite it.",
                    "Three assignments, in the right order.",
                    "temp = a[i]; a[i] = a[j]; a[j] = temp;"]),
    ],
    quiz=[
        _jq("Which of these does NOT give you an independent copy of `int[] a`?",
            ["int[] b = a;", "int[] b = a.clone();", "int[] b = Arrays.copyOf(a, a.length);",
             "int[] b = Arrays.copyOfRange(a, 0, a.length);"],
            0,
            "The first one copies the reference, so `b` is a second name for the same array. "
            "The other three each allocate a new array."),
        _jq("`Arrays.copyOf` on an `int[][]` gives you…",
            ["new outer slots pointing at the SAME row arrays — writes to a row are shared",
             "a fully independent deep copy",
             "a compile error — it only accepts 1D arrays",
             "a copy of the rows but not the outer array"],
            0,
            "All the standard copies are shallow. A 2D array is an array of references to "
            "rows, so a shallow copy shares every row. Module 2 comes back to this."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m1_report(a):
    """Python mirror of the capstone, so its expected output is computed."""
    avg = _jdiv(sum(a), len(a))
    return _nl(
        f"count={len(a)}",
        f"max={max(a)}",
        f"min={min(a)}",
        f"sum={sum(a)}",
        f"avg={avg}",
        f"above={sum(1 for x in a if x > avg)}",
    )


_M1_CAP = _jcap(
    "Scores report",
    """
Everything in module 1, in one program.

Read `n` and then `n` integer scores. Print a six-line report — one `key=value`
per line, in exactly this order and with no spaces around the `=`:

```
count=<how many scores>
max=<the largest>
min=<the smallest>
sum=<the total>
avg=<the mean, as integer division: sum / n>
above=<how many scores are STRICTLY greater than avg>
```

Two things this is really testing:

- **Seed your max and min from the data,** not from `0`. One of the hidden
  cases is all-negative, and a `0` seed fails it.
- **`avg` uses integer division,** so `7 / 2` is `3`, not `3.5`. That is
  deliberate — it keeps the output exact and makes you notice that `sum / n`
  in Java is not the arithmetic mean.

You need two passes (or one pass plus a second loop): you cannot count how many
scores beat the average until you know the average.
""",
    _jch("j1-cap-report", "Scores report", "Medium",
         "Write the whole report where you see `____` — six `key=value` lines, in "
         "the order `count`, `max`, `min`, `sum`, `avg`, `above`.",
         _jscan(
             _RD_ARR
             + "        int max = a[0];\n"
               "        int min = a[0];\n"
               "        int sum = 0;\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            if (a[i] > max) max = a[i];\n"
               "            if (a[i] < min) min = a[i];\n"
               "            sum += a[i];\n"
               "        }\n"
               "        int avg = sum / n;\n"
               "        int above = 0;\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            if (a[i] > avg) above++;\n"
               "        }\n"
               '        System.out.println("count=" + n);\n'
               '        System.out.println("max=" + max);\n'
               '        System.out.println("min=" + min);\n'
               '        System.out.println("sum=" + sum);\n'
               '        System.out.println("avg=" + avg);\n'
               '        System.out.println("above=" + above);'),
         "        int max = a[0];\n"
         "        int min = a[0];\n"
         "        int sum = 0;\n"
         "        for (int i = 0; i < n; i++) {\n"
         "            if (a[i] > max) max = a[i];\n"
         "            if (a[i] < min) min = a[i];\n"
         "            sum += a[i];\n"
         "        }\n"
         "        int avg = sum / n;\n"
         "        int above = 0;\n"
         "        for (int i = 0; i < n; i++) {\n"
         "            if (a[i] > avg) above++;\n"
         "        }\n"
         '        System.out.println("count=" + n);\n'
         '        System.out.println("max=" + max);\n'
         '        System.out.println("min=" + min);\n'
         '        System.out.println("sum=" + sum);\n'
         '        System.out.println("avg=" + avg);\n'
         '        System.out.println("above=" + above);',
         [_acase(a, _m1_report(a))
          for a in ([70, 85, 90, 60], [5], [-4, -11, -7], [10, 10, 10, 10],
                    [1, 2, 3, 4, 5, 6, 7])],
         hints=["Seed `max` and `min` with `a[0]`; seed `sum` with 0.",
                "`int avg = sum / n;` — integer division, on purpose.",
                "A second loop counts how many elements are `> avg`. Strictly greater, so "
                "an element exactly equal to the average does not count.",
                'Print with `System.out.println("count=" + n);` and so on — no spaces '
                "around the `=`."]),
    example_io="stdin:  4\n        70 85 90 60\n\n"
               "stdout: count=4\n        max=90\n        min=60\n        sum=305\n"
               "        avg=76\n        above=2",
    rubric=[
        "`max` and `min` are seeded from the array, not from 0 or from a made-up number.",
        "All six lines print, in the stated order, with no spaces around `=`.",
        "`avg` is `sum / n` in `int` arithmetic — no casting to `double`.",
        "`above` counts strictly-greater, so a score equal to the average is excluded.",
        "It survives an array of one element and an array that is entirely negative.",
    ],
)


_MODULES.append(_jmod(
    1, 1, "Arrays, deeply",
    "Arrays in memory",
    "Stop guessing about arrays: know what the object looks like, walk it two ways "
    "without off-by-ones, aggregate it in one pass, search it, and understand why "
    "`b = a` has ruined somebody's afternoon.",
    """
You can already write `int[] a = new int[5];` and loop over it. This module is
about the layer underneath that — the one that decides whether your array code
is correct on the awkward inputs.

By the end you will have written, from scratch and without looking anything up:
a one-pass max/min/sum, a linear search that returns `-1`, a real copy, and a
swap. Every array algorithm in modules 3, 4 and 5 is built out of exactly those
four moves.
""",
    _M1,
    capstone=_M1_CAP,
    objectives=[
        "Explain what `new int[5]` allocates, what the slots hold, and why the length can never change.",
        "Choose the index loop or the enhanced `for` on purpose, and say why the wrong one silently fails.",
        "Find a max, a min, a sum and the *index* of the max in a single pass, seeded correctly.",
        "Write a linear search that returns the first index or `-1`, and know when to drop the `break`.",
        "Reach for `Arrays.toString`, `fill`, `copyOf`, `copyOfRange` and `equals` without looking them up.",
        "Tell aliasing from copying, and swap two slots without losing a value.",
    ],
    why="Every later module — sorting, rotation, sliding windows, and every array "
        "question you will ever be asked in an interview — is these six lessons "
        "recombined. The bugs are here too: the off-by-one, the `max = 0` seed, and "
        "the backup that was never a backup.",
    est_minutes=300,
    glossary=[
        _jg("element", "One slot of an array, reached by its index: `a[3]`."),
        _jg("index", "A slot's position, counting from 0. Valid range is `0` to `a.length - 1`."),
        _jg("a.length", "A `final` field on the array object holding its size. No parentheses — "
                        "unlike `String.length()`."),
        _jg("default value", "What every slot holds before you write to it: `0` for integer "
                             "types, `0.0` for floating point, `false` for `boolean`, `null` for "
                             "any object type."),
        _jg("reference", "The value an array variable actually holds — the address of the array "
                         "object, not the elements."),
        _jg("aliasing", "Two variables holding the same reference, so writing through one is "
                        "visible through the other. `int[] b = a;` aliases."),
        _jg("shallow copy", "A copy of the outer array whose slots still point at the same inner "
                            "objects. `Arrays.copyOf` on an `int[][]` shares the rows."),
        _jg("sentinel", "A value that cannot be a real answer, used to mean 'nothing here' — "
                        "`-1` for a not-found index."),
        _jg("in place", "Modifying the original array rather than building a new one. "
                        "`Arrays.fill` and `Arrays.sort` are in place; `Arrays.copyOf` is not."),
        _jg("ArrayIndexOutOfBoundsException", "Thrown at *runtime* when an index is negative or "
                                              "`>= length`. The compiler cannot catch it."),
    ],
    cheatsheet="""
```java
// --- create -------------------------------------------------------------
int[] a = new int[5];              // 5 slots, all 0
int[] b = {3, 1, 4, 1, 5};         // literal (declaration only)
int[] c = new int[]{3, 1, 4};      // literal, assignable later

a.length                            // FIELD, no parentheses

// --- traverse -----------------------------------------------------------
for (int i = 0; i < a.length; i++) { ... }        // need the index / writing
for (int x : a) { ... }                            // read-only, values only
for (int i = a.length - 1; i >= 0; i--) { ... }    // backwards

// --- aggregate (seed from real data!) -----------------------------------
int max = a[0];
for (int i = 1; i < a.length; i++) if (a[i] > max) max = a[i];

int best = 0;                                       // index of the max
for (int i = 1; i < a.length; i++) if (a[i] > a[best]) best = i;

long sum = 0;                                       // long guards overflow
for (int x : a) sum += x;

// --- linear search ------------------------------------------------------
int idx = -1;
for (int i = 0; i < a.length; i++)
    if (a[i] == target) { idx = i; break; }         // drop break to count

// --- java.util.Arrays ---------------------------------------------------
Arrays.toString(a)                  // "[3, 1, 4]"   — printing an array raw
Arrays.fill(a, 7)                   //                 gives you [I@1b6d3586
Arrays.copyOf(a, len)               // new array; truncates or zero-pads
Arrays.copyOfRange(a, from, to)     // half-open: to is EXCLUDED
Arrays.equals(a, b)                 // contents; `==` compares references

// --- copy vs alias ------------------------------------------------------
int[] alias = a;                    // SAME array, two names
int[] copy  = a.clone();            // independent (shallow)

// --- swap ---------------------------------------------------------------
int t = a[i]; a[i] = a[j]; a[j] = t;
```
""",
    self_check=[
        "Can you say, without running it, what `new boolean[3]` and `new String[3]` hold?",
        "Can you write a backwards loop with the right start and the right stopping condition, first try?",
        "Can you explain why `for (int x : a) x = 0;` compiles but does nothing?",
        "Can you find the index of the maximum, and say whether your code keeps the first or the last of a tie?",
        "Can you explain to someone else why `int[] backup = a;` is not a backup?",
        "Do you reach for `Arrays.toString` automatically when a println gives you `[I@1b6d3586`?",
    ],
    review=[
        _jq("`int[] a = new int[3]; System.out.println(a.length());` — what happens?",
            ["Compile error: length is a field, not a method",
             "Prints 3", "Prints 0", "Runtime exception"],
            0,
            "Arrays use the field `a.length`; Strings use the method `s.length()`. Mixing "
            "them up is caught at compile time, which is the one mercy here."),
        _jq("Which single line correctly appends `9` to `int[] a = {1, 2}`?",
            ["You cannot — you must build a longer array, e.g. `Arrays.copyOf(a, 3)` then assign",
             "a.add(9);", "a[2] = 9;", "a.length = 3; a[2] = 9;"],
            0,
            "Array length is fixed. `a[2] = 9` throws, `add` does not exist, and `length` "
            "cannot be assigned. Growing means allocating and copying."),
        _jq("After `int[] b = a; b[1] = 5;`, how many array objects exist?",
            ["One", "Two", "Two, but they share elements", "Depends on the array's size"],
            0,
            "`b = a` copied a reference. Only `new` (or `clone`/`copyOf`) creates an array "
            "object, and none of those were called."),
        _jq("Linear search over an unsorted array of 1,000,000 elements, target not present. How many comparisons?",
            ["1,000,000", "About 500,000", "About 20", "1"],
            0,
            "'Not present' is the worst case: you have to look at every element to be sure. "
            "The ~n/2 figure is the *average* for a target that IS present."),
    ],
    milestone="You can reason about what an array is in memory, walk it correctly in either "
              "direction, aggregate and search it in one pass, and you will never again "
              "confuse a copy with an alias.",
))
