# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 1 practice - arrays in memory.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[1]`.
#
# Five families, five variants each. A family drills ONE motion and twists a
# single dimension at a time, so the second variant is never a cold start - it
# is the first one with one thing moved. That is the whole design: the point is
# not 25 unrelated puzzles, it is five patterns you stop having to think about.
#
# Module 1 scope: index loops, enhanced for, `.length`, the `Arrays` utility
# class, aliasing vs copying. NO Arrays.sort (module 3), no String methods
# (6-7), no StringBuilder (8), no helper methods beside main (9), no recursion
# (10), no classes (11). The scope linter enforces all of that.
# ---------------------------------------------------------------------------


def _p1ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_ARR):
    """One practice problem: the stdin reading is given, the logic is blanked.

    Keeping the `Scanner` boilerplate visible is deliberate - the learner should
    be spending their attention on the traversal, not on re-typing input code
    for the twenty-fifth time."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


_A_SUM = ([3, 1, 4, 1, 5], [7], [-2, -3, 5], [0, 0, 0], [10, -10, 10, -10, 1])


# --- Family A - sweep and accumulate ---------------------------------------

_P1_A = _jfam(
    "p1-accumulate", "Sweep and accumulate",
    "One pass, one accumulator.",
    """
Nearly every array question you will ever be asked starts as this shape:

```java
int sum = 0;                                  // 1. the accumulator, before the loop
for (int i = 0; i < n; i++) {                 // 2. one pass
    sum += a[i];                              // 3. update it
}
System.out.println(sum);                      // 4. report it after
```

Three questions turn that skeleton into any of the five problems below:

1. **What is the accumulator, and what does it start at?** A sum starts at `0`.
   A count starts at `0`. A product would start at `1`.
2. **Does every element update it, or only some?** "Count the evens" is the same
   loop with an `if` around the update.
3. **Does the update depend on the index, or only the value?** If only the
   value, you may use the enhanced `for (int x : a)` and stop tracking `i`.

Get those three right and the loop writes itself. The variants below change
exactly one of the three at a time.
""",
    [
        _p1ex("j1-pr-sum", "Sum every element", "Intro",
              "Print the sum of all `n` values.",
              """
        int sum = 0;
        for (int i = 0; i < n; i++) {
            sum += a[i];
        }
        System.out.println(sum);
""",
              [_acase(a, sum(a)) for a in _A_SUM],
              ["Declare the accumulator BEFORE the loop, or it resets every time round.",
               "A sum starts at `0`.",
               "`for (int i = 0; i < n; i++) sum += a[i];`",
               "Print after the loop has finished, not inside it."]),

        _p1ex("j1-pr-count-even", "Count the even values", "Intro",
              "Print how many of the values are even. `0` counts as even.",
              """
        int count = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] % 2 == 0) {
                count++;
            }
        }
        System.out.println(count);
""",
              [_acase(a, sum(1 for x in a if x % 2 == 0)) for a in _A_SUM],
              ["Same skeleton as the sum — only the update changes.",
               "A count also starts at `0`, but it goes up by one rather than by the value.",
               "`a[i] % 2 == 0` is the test. It is true for negatives too: `-4 % 2` is `0`.",
               "Wrap the `count++` in that `if`, and leave the loop itself alone."]),

        _p1ex("j1-pr-sum-above", "Sum only what clears the bar", "Easy",
              "Read the array, then a threshold `k`. Print the sum of the values "
              "**strictly greater** than `k`.",
              """
        int k = sc.nextInt();
        int sum = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] > k) {
                sum += a[i];
            }
        }
        System.out.println(sum);
""",
              [_akcase(a, k, sum(x for x in a if x > k))
               for (a, k) in (([3, 1, 4, 1, 5], 2), ([7], 7), ([-2, -3, 5], -3),
                              ([0, 0, 0], 0), ([10, -10, 10], 0))],
              ["Read `k` first — it comes after the array on stdin.",
               "This is the counting variant again, but the update adds the value "
               "instead of adding one.",
               "**Strictly** greater means `>`, not `>=`. Case two hands you `k` equal "
               "to the only element, and expects `0`.",
               "If nothing clears the bar the answer is `0`, which the accumulator "
               "already is."]),

        _p1ex("j1-pr-average", "Integer average", "Easy",
              "Print the average of the values as an `int`. Java's `/` on two `int`s "
              "truncates toward zero — that is the answer we want, not a rounded one.",
              """
        int sum = 0;
        for (int i = 0; i < n; i++) {
            sum += a[i];
        }
        System.out.println(sum / n);
""",
              [_acase(a, _jdiv(sum(a), len(a))) for a in _A_SUM],
              ["Accumulate the sum exactly as in the first variant.",
               "Then divide by `n` — and `n` is already read for you.",
               "`sum / n` with both sides `int` is integer division: `7 / 2` is `3`.",
               "It truncates toward ZERO, so `-7 / 2` is `-3`, not `-4`. Case three "
               "checks that.",
               "Do not divide inside the loop — divide once, after it."]),

        _p1ex("j1-pr-alternating", "Alternating sum", "Easy",
              "Print `a[0] - a[1] + a[2] - a[3] + …` — add the even indices, "
              "subtract the odd ones.",
              """
        int sum = 0;
        for (int i = 0; i < n; i++) {
            if (i % 2 == 0) {
                sum += a[i];
            } else {
                sum -= a[i];
            }
        }
        System.out.println(sum);
""",
              [_acase(a, sum(x if i % 2 == 0 else -x for (i, x) in enumerate(a)))
               for a in _A_SUM],
              ["This is the first variant where the INDEX matters, not just the value.",
               "So the enhanced `for (int x : a)` will not do — you need `i`.",
               "`i % 2 == 0` tells you whether you are on an even index.",
               "Add on even `i`, subtract on odd `i`. Index 0 is even, so the first "
               "element is always added."]),
    ])


# --- Family B - running extreme --------------------------------------------

_B_ARR = ([3, 9, 2, 9, 4], [7], [-5, -2, -9], [1, 2, 3, 4], [4, 3, 2, 1])


def _second_largest(a):
    return sorted(set(a))[-2]


_P1_B = _jfam(
    "p1-extreme", "The running extreme",
    "Carry the best-so-far, and decide what beats it.",
    """
The second universal shape. You cannot know the maximum until you have seen
every element, so you carry the best answer *so far* and replace it whenever
something beats it:

```java
int best = a[0];                       // seed with a REAL element, not 0
for (int i = 1; i < n; i++) {          // start at 1 — index 0 is already in
    if (a[i] > best) {
        best = a[i];
    }
}
```

**Seed with `a[0]`, never with `0`.** Seeding a maximum with `0` is the single
most common bug in this pattern: it silently returns `0` for an all-negative
array. Variant three below is all-negative precisely to catch that.

Two dimensions get twisted in the variants:

- **What do you keep** — the value, or the *index* of the value? Keeping the
  index is strictly more useful, because `a[bestIndex]` gets you the value back.
- **What counts as beating it** — `>` keeps the FIRST of equal winners, `>=`
  keeps the LAST. That one character is the whole difference between variants
  two and three.
""",
    [
        _p1ex("j1-pr-max", "Largest value", "Intro",
              "Print the largest value in the array.",
              """
        int best = a[0];
        for (int i = 1; i < n; i++) {
            if (a[i] > best) {
                best = a[i];
            }
        }
        System.out.println(best);
""",
              [_acase(a, max(a)) for a in _B_ARR],
              ["Seed `best` with `a[0]`, not with `0`.",
               "Case three is all negative — a `0` seed would wrongly print `0`.",
               "Start the loop at `i = 1`, since index 0 is already accounted for.",
               "`if (a[i] > best) best = a[i];`"]),

        _p1ex("j1-pr-argmax", "Index of the largest", "Easy",
              "Print the **index** of the largest value. If the largest value appears "
              "more than once, print the **first** such index.",
              """
        int best = 0;
        for (int i = 1; i < n; i++) {
            if (a[i] > a[best]) {
                best = i;
            }
        }
        System.out.println(best);
""",
              [_acase(a, a.index(max(a))) for a in _B_ARR],
              ["Keep the index rather than the value: `int best = 0;` seeds with the "
               "index of the first element.",
               "Here `0` IS a valid seed — it is an index, not a value.",
               "Compare `a[i] > a[best]`, not `a[i] > best`.",
               "A strict `>` never replaces on a tie, so the first winner survives. "
               "Case one has two 9s and wants index 1."]),

        _p1ex("j1-pr-argmax-last", "Index of the LAST largest", "Easy",
              "Same array, same maximum — but if it appears more than once, print the "
              "**last** index where it occurs.",
              """
        int best = 0;
        for (int i = 1; i < n; i++) {
            if (a[i] >= a[best]) {
                best = i;
            }
        }
        System.out.println(best);
""",
              [_acase(a, len(a) - 1 - a[::-1].index(max(a))) for a in _B_ARR],
              ["This is the previous problem with exactly one character changed.",
               "Ties are the only difference, so the change has to be in the comparison.",
               "`>=` replaces on a tie, so the later of two equal winners wins.",
               "Case one has 9 at index 1 and index 3, and now wants 3."]),

        _p1ex("j1-pr-minmax", "Both ends in one pass", "Easy",
              "Print the smallest and the largest value, separated by one space, on a "
              "single line. Use one loop, not two.",
              """
        int lo = a[0];
        int hi = a[0];
        for (int i = 1; i < n; i++) {
            if (a[i] < lo) {
                lo = a[i];
            }
            if (a[i] > hi) {
                hi = a[i];
            }
        }
        System.out.println(lo + " " + hi);
""",
              [_acase(a, f"{min(a)} {max(a)}") for a in _B_ARR],
              ["Two accumulators, both seeded from `a[0]`.",
               "One loop with two independent `if`s inside — not `else if`, since a "
               "single element can be neither.",
               "For a one-element array both answers are that element; case two "
               "checks it.",
               'Print them on one line: `System.out.println(lo + " " + hi);`']),

        _p1ex("j1-pr-second", "Second largest distinct", "Medium",
              "Print the second largest **distinct** value. Every test array contains "
              "at least two distinct values, so an answer always exists.",
              """
        int best = a[0];
        int second = Integer.MIN_VALUE;
        for (int i = 1; i < n; i++) {
            if (a[i] > best) {
                second = best;
                best = a[i];
            } else if (a[i] < best && a[i] > second) {
                second = a[i];
            }
        }
        System.out.println(second);
""",
              [_acase(a, _second_largest(a))
               for a in ([3, 9, 2, 9, 4], [-5, -2, -9], [1, 2, 3, 4], [4, 3, 2, 1],
                         [8, 8, 8, 1])],
              ["Carry TWO values: the best, and the best of everything that is not "
               "the best.",
               "Seed `second` with `Integer.MIN_VALUE` — there is no real element you "
               "can safely seed it with.",
               "When a new maximum arrives, the old maximum becomes the runner-up: "
               "assign `second = best;` BEFORE `best = a[i];` or you lose it.",
               "**Distinct** is what the `a[i] < best` guard buys you. Without it, "
               "case five (`8 8 8 1`) would answer `8` instead of `1`.",
               "The two branches must be `else if`, not two `if`s — an element that "
               "beat the max must not also be considered for second place."]),
    ])


# --- Family C - linear search ----------------------------------------------

_C_CASES = (([4, 7, 2, 7, 9], 7), ([4, 7, 2], 5), ([1], 1), ([3, 3, 3], 3),
            ([-1, 0, 1], 0))


_P1_C = _jfam(
    "p1-search", "Linear search, five ways",
    "Walk until you find it — and decide what \"found\" means.",
    """
Searching an unsorted array means looking at every element until you find what
you want. (A sorted array can do far better — that is binary search, module 3.)

The base shape returns as soon as it succeeds:

```java
int found = -1;
for (int i = 0; i < n; i++) {
    if (a[i] == target) {
        found = i;
        break;                 // stop — the FIRST match is the answer
    }
}
System.out.println(found);
```

**`-1` is the conventional "not found".** It is not a magic number chosen at
random: it is the one `int` that can never be a valid index, which is why
`indexOf` in the String API (module 7) returns it too.

The variants twist three things:

- **`break` or keep going** — break gives you the first match, running to the
  end gives you the last.
- **What you report** — an index, a count, or a yes/no.
- **What "matches" means** — equal to a target, or merely bigger than one.

Watch the searches that find nothing. Every variant below has a case where the
answer is "no match", and getting that case right is most of the work.
""",
    [
        _p1ex("j1-pr-find-first", "First index of a target", "Intro",
              "Read the array, then a target `k`. Print the first index where `k` "
              "occurs, or `-1` if it never does.",
              """
        int k = sc.nextInt();
        int found = -1;
        for (int i = 0; i < n; i++) {
            if (a[i] == k) {
                found = i;
                break;
            }
        }
        System.out.println(found);
""",
              [_akcase(a, k, a.index(k) if k in a else -1) for (a, k) in _C_CASES],
              ["Seed the answer with `-1`, so \"never assigned\" already means "
               "\"not found\".",
               "`break` the moment you find it — the first match is the answer.",
               "Case two searches for a value that is not there and wants `-1`.",
               "Print once, after the loop. Printing inside it would print nothing "
               "on a miss."]),

        _p1ex("j1-pr-find-last", "Last index of a target", "Easy",
              "Same input. Print the **last** index where `k` occurs, or `-1`.",
              """
        int k = sc.nextInt();
        int found = -1;
        for (int i = 0; i < n; i++) {
            if (a[i] == k) {
                found = i;
            }
        }
        System.out.println(found);
""",
              [_akcase(a, k, (len(a) - 1 - a[::-1].index(k)) if k in a else -1)
               for (a, k) in _C_CASES],
              ["The previous problem minus one statement.",
               "If you never stop early, the last write wins — and the last write is "
               "the last match.",
               "So: delete the `break`.",
               "Case one has 7 at index 1 and index 3, and wants 3."]),

        _p1ex("j1-pr-count-target", "How many times", "Intro",
              "Same input. Print how many times `k` occurs. `0` if it never does.",
              """
        int k = sc.nextInt();
        int count = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] == k) {
                count++;
            }
        }
        System.out.println(count);
""",
              [_akcase(a, k, a.count(k)) for (a, k) in _C_CASES],
              ["No early exit — you have to see every element to count them all.",
               "The accumulator starts at `0`, and `0` is also the right answer for "
               "a miss.",
               "`if (a[i] == k) count++;`",
               "Case four is three identical values and wants `3`."]),

        _p1ex("j1-pr-contains", "Does it contain it?", "Intro",
              "Same input. Print `true` if `k` occurs anywhere, `false` otherwise.",
              """
        int k = sc.nextInt();
        boolean found = false;
        for (int i = 0; i < n; i++) {
            if (a[i] == k) {
                found = true;
                break;
            }
        }
        System.out.println(found);
""",
              [_akcase(a, k, _jbool(k in a)) for (a, k) in _C_CASES],
              ["The accumulator is a `boolean` this time, starting at `false`.",
               "`break` as soon as it turns true — there is nothing left to learn.",
               "`System.out.println(found)` prints a boolean as `true` or `false` "
               "already; you do not need an `if` to choose the word.",
               "Never write `if (found == true)`. `found` is already the condition."]),

        _p1ex("j1-pr-first-above", "First one over the line", "Easy",
              "Same input. Print the index of the first value **strictly greater** "
              "than `k`, or `-1` if none is.",
              """
        int k = sc.nextInt();
        int found = -1;
        for (int i = 0; i < n; i++) {
            if (a[i] > k) {
                found = i;
                break;
            }
        }
        System.out.println(found);
""",
              [_akcase(a, k, next((i for (i, x) in enumerate(a) if x > k), -1))
               for (a, k) in (([4, 7, 2, 7, 9], 7), ([4, 7, 2], 9), ([1], 0),
                              ([3, 3, 3], 3), ([-1, 0, 1], -2))],
              ["Identical to the first variant except for the test inside the `if`.",
               "\"Matches\" no longer means equal — it means bigger.",
               "Strictly greater is `>`. Case four is all 3s with `k` of 3, and wants "
               "`-1`.",
               "Case two has nothing above 9 and also wants `-1`."]),
    ])


# --- Family D - the Arrays toolbox -----------------------------------------

_D_ARR = ([3, 1, 4, 1, 5], [7], [-2, 0, 2], [9, 9], [1, 2, 3, 4, 5, 6])


_P1_D = _jfam(
    "p1-toolbox", "The Arrays toolbox",
    "The five `java.util.Arrays` calls worth knowing cold.",
    """
`java.util.Arrays` is a box of static helpers for things you would otherwise
hand-write. They are worth knowing cold, because reaching for the wrong one (or
not knowing one exists) is where a lot of clumsy array code comes from.

```java
Arrays.toString(a)            // "[3, 1, 4]" — for printing and debugging
Arrays.fill(a, 7)             // every slot becomes 7, IN PLACE
Arrays.copyOf(a, len)         // a NEW array of exactly len; pads 0 / truncates
Arrays.copyOfRange(a, i, j)   // a NEW array of a[i]..a[j-1]  — j is EXCLUSIVE
Arrays.equals(a, b)           // true if same length AND same values in order
```

Two traps worth stating out loud, because both bite constantly:

**`copyOfRange`'s second index is exclusive.** `copyOfRange(a, 1, 4)` gives you
indices 1, 2 and 3 — three elements, not four. The length is `j - i`, which is
the same convention as `substring` in module 6.

**`a == b` is not `Arrays.equals(a, b)`.** For arrays, `==` compares
*references* — whether the two names point at the same object — not contents.
Two separate arrays holding identical values are never `==`. This is exactly the
trap that `.equals()` on Strings sets in module 6, and it is worth meeting here
first, on arrays, where the reason is more obvious.
""",
    [
        _p1ex("j1-pr-tostring", "Print it like Java does", "Intro",
              "Print the array in `Arrays.toString` format — `[3, 1, 4, 1, 5]`, with "
              "square brackets and comma-space between values.",
              """
        System.out.println(Arrays.toString(a));
""",
              [_acase(a, _jarr(a)) for a in _D_ARR],
              ["Do not build the string by hand with a loop — there is a helper for "
               "exactly this.",
               "It lives on `Arrays`, and `import java.util.*;` is already at the top.",
               "`Arrays.toString(a)` returns the string; you still have to print it.",
               "Note the exact format it produces: `[3, 1, 4]` — comma AND space."]),

        _p1ex("j1-pr-fill", "Overwrite every slot", "Intro",
              "Read the array, then a value `k`. Set **every** element to `k`, then "
              "print the array in `Arrays.toString` format.",
              """
        int k = sc.nextInt();
        Arrays.fill(a, k);
        System.out.println(Arrays.toString(a));
""",
              [_akcase(a, k, _jarr([k] * len(a)))
               for (a, k) in (([3, 1, 4], 0), ([7], 7), ([-2, 0, 2], -1),
                              ([9, 9], 5), ([1, 2, 3, 4], 100))],
              ["A loop assigning `a[i] = k` would work, but there is a one-line "
               "helper.",
               "`Arrays.fill` changes the array **in place** and returns nothing.",
               "So call it as its own statement — `a = Arrays.fill(...)` does not "
               "compile.",
               "`Arrays.fill(a, k);` then print with `Arrays.toString(a)`."]),

        _p1ex("j1-pr-grow", "Grow the array", "Easy",
              "Read the array, then a count `k`. Print a copy that is `k` slots "
              "**longer**, in `Arrays.toString` format. The new slots hold whatever "
              "Java gives a fresh `int[]`.",
              """
        int k = sc.nextInt();
        int[] bigger = Arrays.copyOf(a, n + k);
        System.out.println(Arrays.toString(bigger));
""",
              [_akcase(a, k, _jarr(a + [0] * k))
               for (a, k) in (([3, 1, 4], 2), ([7], 1), ([-2, 0, 2], 0),
                              ([9, 9], 3), ([1], 5))],
              ["Arrays cannot grow — `copyOf` makes a NEW, longer one and copies the "
               "old values into the front.",
               "The new length is `n + k`.",
               "The padding is the default value for `int`, which is `0` — you do not "
               "write it yourself.",
               "Case three grows by `0`, which is just a plain copy.",
               "`int[] bigger = Arrays.copyOf(a, n + k);`"]),

        _p1ex("j1-pr-slice", "Take a slice", "Easy",
              "Read the array, then two indices `from` and `to`. Print "
              "`Arrays.copyOfRange(a, from, to)` in `Arrays.toString` format — "
              "remember `to` is **exclusive**.",
              """
        int[] slice = Arrays.copyOfRange(a, from, to);
        System.out.println(Arrays.toString(slice));
""",
              [_case(f"{len(a)}\n{_sp(a)}\n{fr} {to}", _jarr(a[fr:to]))
               for (a, fr, to) in (([3, 1, 4, 1, 5], 1, 4), ([7], 0, 1),
                                   ([-2, 0, 2], 0, 3), ([9, 9], 1, 1),
                                   ([1, 2, 3, 4, 5, 6], 2, 5))],
              ["`from` and `to` are already read for you — just use them.",
               "The slice runs from `from` up to but NOT including `to`.",
               "So its length is `to - from`, and case one (`1` to `4`) gives three "
               "values.",
               "Case four has `from` equal to `to`, which is legal and gives `[]`.",
               "`Arrays.copyOfRange(a, from, to)`"],
              read=_RD_ARR + "        int from = sc.nextInt();\n"
                             "        int to = sc.nextInt();\n"),

        _p1ex("j1-pr-equals", "Same contents?", "Easy",
              "Read two arrays. Print `true` if they have the same length and the same "
              "values in the same order, `false` otherwise. Do not write the "
              "comparison loop yourself.",
              """
        System.out.println(Arrays.equals(a, b));
""",
              [_a2case(a, b, _jbool(a == b))
               for (a, b) in (([3, 1, 4], [3, 1, 4]), ([3, 1, 4], [3, 1]),
                              ([7], [8]), ([1, 2], [2, 1]),
                              ([-1, 0], [-1, 0]))],
              ["Both arrays are read for you as `a` and `b`.",
               "`a == b` compiles, but asks whether they are the SAME object — which "
               "is false even for identical contents.",
               "The helper that compares contents is on `Arrays`.",
               "`Arrays.equals(a, b)` handles the length check for you too.",
               "Case four has the same values in a different order, and is `false`."],
              read=_RD_ARR2),
    ])


# --- Family E - aliasing versus copying -------------------------------------

_P1_E = _jfam(
    "p1-alias", "Aliasing versus copying",
    "Two names for one array, or two arrays.",
    """
This is the idea in module 1 that causes the most real bugs, and it is worth
drilling until it is reflex.

```java
int[] a = {1, 2, 3};
int[] b = a;              // NOT a copy — b is a second NAME for the same array
b[0] = 99;
System.out.println(a[0]); // 99  — a "changed" without being touched
```

An array variable holds a **reference** — the address of the array object, not
the values. Assigning one array variable to another copies the *address*, so
both names now point at one object, and a write through either is visible
through both. That is **aliasing**.

To get a genuinely independent array you must ask for one:

```java
int[] b = Arrays.copyOf(a, a.length);   // a real, separate copy
b[0] = 99;
System.out.println(a[0]);               // 1 — untouched
```

The five variants below alternate deliberately between mutating in place and
copying first. Before writing each one, ask the only question that matters:
**does the original have to survive?** If it does, copy. If it does not,
mutating in place is cheaper and clearer.
""",
    [
        _p1ex("j1-pr-alias", "Two names, one array", "Intro",
              "Make `b` a second name for `a` (not a copy). Set `b[0]` to `99`. Then "
              "print `a` in `Arrays.toString` format — it should show the change.",
              """
        int[] b = a;
        b[0] = 99;
        System.out.println(Arrays.toString(a));
""",
              [_acase(a, _jarr([99] + a[1:])) for a in _D_ARR],
              ["Plain assignment is what creates an alias — no helper involved.",
               "`int[] b = a;` copies the reference, not the contents.",
               "So `b[0] = 99;` writes into the one and only array.",
               "Print `a`, not `b` — the whole point is that they are the same "
               "object."]),

        _p1ex("j1-pr-copy", "A real copy leaves the original alone", "Easy",
              "Make `b` an independent copy of `a`. Set `b[0]` to `99`. Print `a` on "
              "the first line and `b` on the second, both in `Arrays.toString` format. "
              "`a` must be unchanged.",
              """
        int[] b = Arrays.copyOf(a, n);
        b[0] = 99;
        System.out.println(Arrays.toString(a));
        System.out.println(Arrays.toString(b));
""",
              [_acase(a, _nl(_jarr(a), _jarr([99] + a[1:]))) for a in _D_ARR],
              ["`int[] b = a;` would alias and fail this — you need a new object.",
               "`Arrays.copyOf(a, n)` builds one of the same length.",
               "Write into `b` only.",
               "Two `println`s: `a` first, then `b`. The first line proves the "
               "original survived."]),

        _p1ex("j1-pr-swap", "Swap the ends in place", "Easy",
              "Swap the first and last elements of `a` **in place**, then print `a` in "
              "`Arrays.toString` format. A one-element array is unchanged.",
              """
        int tmp = a[0];
        a[0] = a[n - 1];
        a[n - 1] = tmp;
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(([a[-1]] + a[1:-1] + [a[0]]) if len(a) > 1 else a))
               for a in _D_ARR],
              ["A swap needs a third variable — assigning `a[0] = a[n-1]` first "
               "destroys the value you still need.",
               "Save it: `int tmp = a[0];`",
               "Then overwrite `a[0]`, and finally put `tmp` where it belongs.",
               "The last index is `n - 1`. For a one-element array that IS index 0, "
               "so the swap harmlessly does nothing — case two checks it."]),

        _p1ex("j1-pr-double", "Double every element in place", "Intro",
              "Multiply every element of `a` by two, in place, then print `a` in "
              "`Arrays.toString` format.",
              """
        for (int i = 0; i < n; i++) {
            a[i] = a[i] * 2;
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr([x * 2 for x in a])) for a in _D_ARR],
              ["No copy needed — the original is not wanted afterwards.",
               "You must write back into the array: reading `a[i]` alone changes "
               "nothing.",
               "`a[i] = a[i] * 2;` — or `a[i] *= 2;`",
               "The enhanced `for (int x : a)` cannot do this: `x` is a copy of the "
               "element, so assigning to it writes nowhere."]),

        _p1ex("j1-pr-reverse-copy", "A reversed copy", "Medium",
              "Build a **new** array holding `a` reversed, without modifying `a`. "
              "Print `a` on the first line and the reversed copy on the second, both "
              "in `Arrays.toString` format.",
              """
        int[] rev = new int[n];
        for (int i = 0; i < n; i++) {
            rev[i] = a[n - 1 - i];
        }
        System.out.println(Arrays.toString(a));
        System.out.println(Arrays.toString(rev));
""",
              [_acase(list(a), _nl(_jarr(a), _jarr(a[::-1]))) for a in _D_ARR],
              ["Allocate the destination first: `int[] rev = new int[n];`",
               "Then fill it. The element that belongs at `rev[0]` is the LAST element "
               "of `a`.",
               "The mirror of index `i` is `n - 1 - i`. Check it: at `i = 0` that is "
               "`n - 1`, and at `i = n - 1` it is `0`.",
               "Write `rev[i] = a[n - 1 - i];` — reading from `a`, writing to `rev`, "
               "so `a` is never touched.",
               "The first printed line must still be the original order."]),
    ])


_PRACTICE[1] = [_P1_A, _P1_B, _P1_C, _P1_D, _P1_E]
