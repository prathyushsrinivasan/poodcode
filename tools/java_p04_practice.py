# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 4 practice - rearranging and counting.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[4]`.
#
# Module 4 scope: reversal by two pointers, rotation (extra array and the
# three-reversal trick), frequency/counting arrays, duplicates, missing and
# repeating numbers. Arrays.sort is available (module 3). Still no String
# methods, no StringBuilder, no helper methods beside main, no recursion.
# ---------------------------------------------------------------------------


def _p4ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_ARR):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


_R_ARR = ([1, 2, 3, 4, 5], [7], [1, 2], [4, 4, 4], [9, 8, 7, 6])


# --- Family A - reversal ----------------------------------------------------

_P4_A = _jfam(
    "p4-reverse", "Reversal by two pointers",
    "Walk in from both ends, swapping as you go.",
    """
Reversing an array is the archetypal **two-pointer** motion, and it is the
building block for rotation, palindromes and half the string questions in
module 7.

```java
int lo = 0, hi = n - 1;
while (lo < hi) {
    int tmp = a[lo];
    a[lo] = a[hi];
    a[hi] = tmp;
    lo++;
    hi--;
}
```

Or, written as a counted loop, the form you will see more often:

```java
for (int i = 0; i < n / 2; i++) {
    int tmp = a[i];
    a[i] = a[n - 1 - i];
    a[n - 1 - i] = tmp;
}
```

**The `n / 2` is load-bearing.** Run to `n` and every pair gets swapped twice,
leaving the array exactly as it started — a bug that looks like "my code does
nothing". Integer division also handles odd lengths correctly for free: the
middle element is its own partner and rightly stays put.

**The partner of `i` is `n - 1 - i`.** Check it at both ends every time you
write it: at `i = 0` it is `n - 1`, and at `i = n - 1` it is `0`.

The variants generalise this to *part* of an array, which is exactly what the
three-reversal rotation trick in the next family needs.
""",
    [
        _p4ex("j4-pr-rev", "Reverse it in place", "Intro",
              "Reverse the array in place, then print it in `Arrays.toString` format.",
              """
        for (int i = 0; i < n / 2; i++) {
            int tmp = a[i];
            a[i] = a[n - 1 - i];
            a[n - 1 - i] = tmp;
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(list(reversed(a)))) for a in _R_ARR],
              ["Swap the ends, then work inwards.",
               "Stop at `n / 2`, or you swap everything back again.",
               "The partner of index `i` is `n - 1 - i`.",
               "A swap needs a temporary variable.",
               "Odd lengths need no special case — the middle element pairs with "
               "itself."]),

        _p4ex("j4-pr-rev-range", "Reverse just a slice", "Easy",
              "Read the array, then `from` and `to` (both inclusive, and always valid). "
              "Reverse only `a[from..to]` in place, leaving the rest alone, then print "
              "the whole array in `Arrays.toString` format.",
              """
        int lo = from;
        int hi = to;
        while (lo < hi) {
            int tmp = a[lo];
            a[lo] = a[hi];
            a[hi] = tmp;
            lo++;
            hi--;
        }
        System.out.println(Arrays.toString(a));
""",
              [_case(f"{len(a)}\n{_sp(a)}\n{fr} {to}",
                     _jarr(a[:fr] + list(reversed(a[fr:to + 1])) + a[to + 1:]))
               for (a, fr, to) in (([1, 2, 3, 4, 5], 1, 3), ([1, 2, 3, 4, 5], 0, 4),
                                   ([7], 0, 0), ([1, 2], 0, 1),
                                   ([9, 8, 7, 6], 2, 3))],
              ["The two-pointer form is easier here than the counted one, because "
               "the range does not start at 0.",
               "Seed `lo = from` and `hi = to` and walk them towards each other.",
               "The loop runs while `lo < hi` — when they meet or cross, stop.",
               "`to` is INCLUSIVE here, unlike `copyOfRange`. Case two reverses the "
               "whole array.",
               "A one-element range does nothing at all, which the `lo < hi` "
               "condition already handles."],
              read=_RD_ARR + "        int from = sc.nextInt();\n"
                             "        int to = sc.nextInt();\n"),

        _p4ex("j4-pr-rev-first-k", "Reverse the first k", "Easy",
              "Read the array, then `k` (always between `0` and `n`). Reverse only the "
              "first `k` elements in place, then print the whole array in "
              "`Arrays.toString` format.",
              """
        int k = sc.nextInt();
        for (int i = 0; i < k / 2; i++) {
            int tmp = a[i];
            a[i] = a[k - 1 - i];
            a[k - 1 - i] = tmp;
        }
        System.out.println(Arrays.toString(a));
""",
              [_akcase(a, k, _jarr(list(reversed(a[:k])) + a[k:]))
               for (a, k) in (([1, 2, 3, 4, 5], 3), ([1, 2, 3, 4, 5], 5),
                              ([1, 2, 3, 4, 5], 0), ([7], 1), ([9, 8, 7, 6], 2))],
              ["Same counted loop as a full reversal, with `n` replaced by `k` "
               "everywhere.",
               "The bound is `k / 2`, and the partner of `i` is `k - 1 - i`.",
               "`k` of `0` must leave the array untouched — the loop body simply "
               "never runs.",
               "`k` of `n` is a full reversal.",
               "Do not touch anything from index `k` onwards."]),

        _p4ex("j4-pr-palindrome", "Does it read the same both ways?", "Intro",
              "Print `true` if the array is the same forwards and backwards, `false` "
              "otherwise. Do not modify or copy it.",
              """
        boolean same = true;
        for (int i = 0; i < n / 2; i++) {
            if (a[i] != a[n - 1 - i]) {
                same = false;
            }
        }
        System.out.println(same);
""",
              [_acase(list(a), _jbool(a == list(reversed(a))))
               for a in ([1, 2, 1], [7], [1, 2], [4, 4, 4], [1, 2, 2, 1])],
              ["Same pairing as a reversal, but comparing instead of swapping.",
               "Checking the first half is enough — the second half is the same "
               "comparisons in the other order.",
               "Compare `a[i]` with `a[n - 1 - i]`.",
               "A flag that starts `true` and is only knocked down.",
               "A single element is trivially a palindrome, and so is an empty "
               "half — case two must print `true`."]),

        _p4ex("j4-pr-swap-halves", "Swap the two halves", "Medium",
              "Swap the first half of the array with the second half, in place, then "
              "print it in `Arrays.toString` format. If `n` is odd the middle element "
              "stays exactly where it is.",
              """
        int half = n / 2;
        for (int i = 0; i < half; i++) {
            int tmp = a[i];
            a[i] = a[n - half + i];
            a[n - half + i] = tmp;
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(a[len(a) - len(a) // 2:]
                                     + (a[len(a) // 2:len(a) - len(a) // 2])
                                     + a[:len(a) // 2]))
               for a in ([1, 2, 3, 4], [1, 2, 3, 4, 5], [7], [1, 2], [9, 8, 7, 6])],
              ["This is NOT a reversal — the halves keep their internal order.",
               "`half` is `n / 2`. For odd `n` that leaves one element over.",
               "Element `i` of the first half pairs with element `i` of the SECOND "
               "half, which begins at index `n - half`.",
               "For odd `n`, `n - half` is `half + 1`, so the middle index is skipped "
               "automatically — no special case needed.",
               "Case two is `[4, 5, 3, 1, 2]`: the `3` never moves."]),
    ])


# --- Family B - rotation ----------------------------------------------------

def _rot_left(a, k):
    k %= len(a)
    return a[k:] + a[:k]


def _rot_right(a, k):
    k %= len(a)
    return a[-k:] + a[:-k] if k else list(a)


_P4_B = _jfam(
    "p4-rotate", "Rotation",
    "Everything moves k places, and the ends wrap around.",
    """
Rotating left by `k` means the element at index `k` becomes the new first
element, and the `k` that fell off the front reappear at the back.

**The straightforward way** is a second array and one modular subscript:

```java
int[] out = new int[n];
for (int i = 0; i < n; i++) {
    out[i] = a[(i + k) % n];            // left rotation
}
```

`% n` is doing the wrapping. For a **right** rotation the arithmetic is the
mirror, and needs care because Java's `%` can return a negative:

```java
out[(i + k) % n] = a[i];                // right rotation, written as a scatter
```

**Always normalise `k` first with `k = k % n`.** A `k` of `n` is a no-op, and a
`k` larger than `n` is just `k % n` — without this, `(i + k)` overflows the
array or wastes an enormous amount of work.

**The three-reversal trick** does it in place with no extra array:

```java
// rotate LEFT by k:
reverse(a, 0, k - 1);      // reverse the first k
reverse(a, k, n - 1);      // reverse the rest
reverse(a, 0, n - 1);      // reverse the whole thing
```

Try it on `1 2 3 4 5` with `k = 2`: `21 543` → `21543` → reversed → `34512`.
It is O(n) time and O(1) space, and it is the answer interviewers are usually
fishing for. Since module 9's helper methods do not exist yet, you will write
those three reversals inline.
""",
    [
        _p4ex("j4-pr-rot1", "Rotate left by one", "Intro",
              "Move every element one place towards the front; the first element wraps "
              "around to the end. Print the result in `Arrays.toString` format.",
              """
        int first = a[0];
        for (int i = 0; i < n - 1; i++) {
            a[i] = a[i + 1];
        }
        a[n - 1] = first;
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(_rot_left(a, 1))) for a in _R_ARR],
              ["Save `a[0]` before the shifting starts — the first move destroys it.",
               "Then slide everything left: `a[i] = a[i + 1]`.",
               "Stop at `i < n - 1`, or `a[i + 1]` runs off the end.",
               "Finally put the saved value in the last slot.",
               "A one-element array is unchanged, and the code handles it without a "
               "special case."]),

        _p4ex("j4-pr-rot-left-k", "Rotate left by k", "Easy",
              "Read the array, then `k` (`0 <= k`, and it may be larger than `n`). Print "
              "the array rotated left by `k` in `Arrays.toString` format. Use a second "
              "array.",
              """
        int k = sc.nextInt();
        k = k % n;
        int[] out = new int[n];
        for (int i = 0; i < n; i++) {
            out[i] = a[(i + k) % n];
        }
        System.out.println(Arrays.toString(out));
""",
              [_akcase(a, k, _jarr(_rot_left(a, k)))
               for (a, k) in (([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 0),
                              ([1, 2, 3, 4, 5], 5), ([1, 2, 3, 4, 5], 7),
                              ([7], 3))],
              ["Normalise first: `k = k % n;`. Cases four and five pass a `k` bigger "
               "than `n`.",
               "Allocate `int[] out = new int[n];`.",
               "For a LEFT rotation the value that lands at `out[i]` comes from "
               "further along: `a[(i + k) % n]`.",
               "The `% n` wraps the tail back to the front.",
               "`k` of `0` and `k` of `n` both leave the array unchanged."]),

        _p4ex("j4-pr-rot-right-k", "Rotate right by k", "Medium",
              "Same input. Print the array rotated **right** by `k` in "
              "`Arrays.toString` format. Use a second array.",
              """
        int k = sc.nextInt();
        k = k % n;
        int[] out = new int[n];
        for (int i = 0; i < n; i++) {
            out[(i + k) % n] = a[i];
        }
        System.out.println(Arrays.toString(out));
""",
              [_akcase(a, k, _jarr(_rot_right(a, k)))
               for (a, k) in (([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 0),
                              ([1, 2, 3, 4, 5], 5), ([1, 2, 3, 4, 5], 7),
                              ([7], 3))],
              ["Normalise `k` first, exactly as before.",
               "The easiest correct form is a SCATTER rather than a gather: decide "
               "where each element goes, instead of where each slot comes from.",
               "Element `i` moves right by `k`, landing at `(i + k) % n`.",
               "So `out[(i + k) % n] = a[i];`",
               "Writing it as a gather instead needs `a[(i - k + n) % n]` — the "
               "`+ n` is essential, because `%` on a negative gives a negative in "
               "Java. The scatter avoids that trap entirely."]),

        _p4ex("j4-pr-rot-reversal", "Rotate left by k, in place", "Hard",
              "Same input. Rotate left by `k` **in place**, using no second array, via "
              "the three-reversal trick. Print the array in `Arrays.toString` format.",
              """
        int k = sc.nextInt();
        k = k % n;
        int lo = 0;
        int hi = k - 1;
        while (lo < hi) {
            int tmp = a[lo];
            a[lo] = a[hi];
            a[hi] = tmp;
            lo++;
            hi--;
        }
        lo = k;
        hi = n - 1;
        while (lo < hi) {
            int tmp = a[lo];
            a[lo] = a[hi];
            a[hi] = tmp;
            lo++;
            hi--;
        }
        lo = 0;
        hi = n - 1;
        while (lo < hi) {
            int tmp = a[lo];
            a[lo] = a[hi];
            a[hi] = tmp;
            lo++;
            hi--;
        }
        System.out.println(Arrays.toString(a));
""",
              [_akcase(a, k, _jarr(_rot_left(a, k)))
               for (a, k) in (([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 0),
                              ([1, 2, 3, 4, 5], 5), ([1, 2, 3, 4, 5], 7),
                              ([9, 8, 7, 6], 1))],
              ["Normalise `k` first, or the range bounds go out of the array.",
               "Three reversals, in this order: `[0, k-1]`, then `[k, n-1]`, then "
               "the whole array `[0, n-1]`.",
               "Module 9 has helper methods; this module does not, so write the same "
               "two-pointer loop three times with different bounds.",
               "Each one is `lo`/`hi` walking inwards while `lo < hi`.",
               "When `k` normalises to `0` the first range is `[0, -1]`, which is "
               "empty, and the second and third cancel out — so it correctly does "
               "nothing. Cases two and three rely on that.",
               "Trace `1 2 3 4 5` with `k = 2`: `2 1 | 5 4 3`, then reverse it all "
               "to get `3 4 5 1 2`."]),

        _p4ex("j4-pr-rot-detect", "Is it a rotation of the other?", "Medium",
              "Read two arrays of the same length. Print `true` if the second is some "
              "left rotation of the first, `false` otherwise. Try every offset.",
              """
        boolean found = false;
        for (int k = 0; k < n; k++) {
            boolean same = true;
            for (int i = 0; i < n; i++) {
                if (a[(i + k) % n] != b[i]) {
                    same = false;
                }
            }
            if (same) {
                found = true;
            }
        }
        System.out.println(found);
""",
              [_a2case(a, b, _jbool(any(_rot_left(a, k) == b for k in range(len(a)))))
               for (a, b) in (([1, 2, 3, 4], [3, 4, 1, 2]), ([1, 2, 3, 4], [1, 2, 3, 4]),
                              ([1, 2, 3, 4], [4, 3, 2, 1]), ([7], [7]),
                              ([1, 2, 2], [2, 1, 2]))],
              ["Both arrays are read for you, as `a` and `b`, and are the same "
               "length.",
               "Try each possible offset `k` from `0` to `n - 1`.",
               "For a given `k`, the arrays match if `a[(i + k) % n] == b[i]` for "
               "every `i`.",
               "That inner check is a flag that starts `true` and gets knocked down.",
               "`k = 0` means they are simply equal, so an identical pair is a "
               "rotation — case two is `true`.",
               "Case three is a reversal, not a rotation, and is `false`."],
              read=_RD_ARR2),
    ])


# --- Family C - counting arrays ---------------------------------------------

_RD_ARR_M = _RD_ARR + "        int m = sc.nextInt();\n"


def _mcase_freq(a, m, out):
    return _case(f"{len(a)}\n{_sp(a)}\n{m}", out)


_F_CASES = (([1, 2, 2, 3], 3), ([0], 0), ([2, 2, 2], 2), ([0, 1, 2, 3], 3),
            ([3, 1, 3, 1, 3], 3))


_P4_C = _jfam(
    "p4-counting", "Counting arrays",
    "Use the value as an index.",
    """
When the values are small non-negative integers, you can count them without any
searching at all — by using **the value itself as an index**:

```java
int[] freq = new int[m + 1];        // slots 0..m, all starting at 0
for (int i = 0; i < n; i++) {
    freq[a[i]]++;                   // the value IS the index
}
```

One pass, O(n), and afterwards `freq[v]` is exactly how many times `v` appeared.
Compare that with the obvious alternative — for each value, scan the array
counting matches — which is O(n²). This trick is the ancestor of the hash map
you will meet in Part 6, and it is why "count the occurrences" is almost never
a nested loop.

**Its two costs are worth stating plainly:**

- You need to know the **range in advance** (here, every value is between `0`
  and `m`), because the array has to be allocated up front.
- You pay `m + 1` slots of memory even if only three distinct values appear.
  Counting values up to a million to find duplicates among ten numbers is a bad
  trade — that is exactly where a `HashMap` wins.

`new int[m + 1]` gives every slot the `int` default of `0`, so there is no
initialisation loop to write. The `+ 1` is because the slots are `0..m`
inclusive.
""",
    [
        _p4ex("j4-pr-freq", "Count every value", "Easy",
              "Read the array, then `m`. Every value is between `0` and `m` inclusive. "
              "Print `freq[0]`, `freq[1]`, … `freq[m]` separated by single spaces on "
              "one line.",
              """
        int[] freq = new int[m + 1];
        for (int i = 0; i < n; i++) {
            freq[a[i]]++;
        }
        for (int v = 0; v <= m; v++) {
            System.out.print(freq[v] + " ");
        }
        System.out.println();
""",
              [_mcase_freq(a, m, _sp([a.count(v) for v in range(m + 1)]))
               for (a, m) in _F_CASES],
              ["Allocate `m + 1` slots, so indices `0` through `m` all exist.",
               "Java zeroes a new `int[]` for you — no initialisation loop needed.",
               "`freq[a[i]]++` is the whole counting step: the value is the index.",
               "Then print slots `0` to `m` INCLUSIVE, so the loop is `v <= m`.",
               "Values that never appear print `0`, which is what case four's "
               "neighbours show."],
              read=_RD_ARR_M),

        _p4ex("j4-pr-mode", "The most common value", "Easy",
              "Same input. Print the value that appears most often. If several tie, "
              "print the **smallest** of them.",
              """
        int[] freq = new int[m + 1];
        for (int i = 0; i < n; i++) {
            freq[a[i]]++;
        }
        int best = 0;
        for (int v = 1; v <= m; v++) {
            if (freq[v] > freq[best]) {
                best = v;
            }
        }
        System.out.println(best);
""",
              [_mcase_freq(a, m, min(range(m + 1), key=lambda v: (-a.count(v), v)))
               for (a, m) in _F_CASES],
              ["Count first, then run module 1's running-maximum over the FREQUENCY "
               "array.",
               "Track the value (the index into `freq`), not the count.",
               "Seed with `best = 0` and scan from `v = 1`.",
               "A strict `>` never replaces on a tie, and because you scan upwards "
               "that keeps the smallest tied value — which is what the brief asks "
               "for.",
               "Case one has 2 appearing twice and everything else once, so `2`."],
              read=_RD_ARR_M),

        _p4ex("j4-pr-distinct", "How many different values?", "Intro",
              "Same input. Print how many distinct values appear at least once.",
              """
        int[] freq = new int[m + 1];
        for (int i = 0; i < n; i++) {
            freq[a[i]]++;
        }
        int distinct = 0;
        for (int v = 0; v <= m; v++) {
            if (freq[v] > 0) {
                distinct++;
            }
        }
        System.out.println(distinct);
""",
              [_mcase_freq(a, m, len(set(a))) for (a, m) in _F_CASES],
              ["Count first, then count how many slots are non-zero.",
               "The second loop walks the frequency array, not the original.",
               "`if (freq[v] > 0) distinct++;`",
               "Case three is three copies of one value, so the answer is `1`."],
              read=_RD_ARR_M),

        _p4ex("j4-pr-once", "The values that appear exactly once", "Easy",
              "Same input. Print every value that occurs exactly once, in ascending "
              "order, separated by single spaces on one line. Print an empty line if "
              "there are none.",
              """
        int[] freq = new int[m + 1];
        for (int i = 0; i < n; i++) {
            freq[a[i]]++;
        }
        for (int v = 0; v <= m; v++) {
            if (freq[v] == 1) {
                System.out.print(v + " ");
            }
        }
        System.out.println();
""",
              [_mcase_freq(a, m, _sp([v for v in range(m + 1) if a.count(v) == 1]))
               for (a, m) in _F_CASES],
              ["Walking the frequency array from `0` upwards gives ascending order "
               "for free — no sorting needed.",
               "The test is `freq[v] == 1`, exactly.",
               "Case three has no value occurring once, so only the blank line is "
               "printed.",
               "Finish with a bare `System.out.println();` so the line is terminated "
               "either way."],
              read=_RD_ARR_M),

        _p4ex("j4-pr-first-repeat", "First value to repeat", "Medium",
              "Same input. Print the first value that appears more than once, judged by "
              "where its **second** occurrence falls. Print `-1` if every value is "
              "unique.",
              """
        int[] seen = new int[m + 1];
        int answer = -1;
        for (int i = 0; i < n; i++) {
            if (seen[a[i]] == 1 && answer == -1) {
                answer = a[i];
            }
            seen[a[i]] = 1;
        }
        System.out.println(answer);
""",
              [_mcase_freq(a, m, (lambda: next((v for (i, v) in enumerate(a)
                                                if v in a[:i]), -1))())
               for (a, m) in _F_CASES],
              ["This one needs a single pass in ORIGINAL order, not a pass over the "
               "frequency array — the answer depends on position.",
               "Use the counting array as a 'have I seen this?' marker.",
               "Check the marker BEFORE setting it, or every value looks repeated.",
               "Guard with `answer == -1` so only the first repeat sticks.",
               "Case one sees `2` again at index 2, so the answer is `2`. Case four "
               "has all-unique values and wants `-1`."],
              read=_RD_ARR_M),
    ])


# --- Family D - missing and repeating ---------------------------------------

_P4_D = _jfam(
    "p4-missing", "Missing and repeating",
    "What arithmetic tells you that searching would not.",
    """
A classic interview family, and the point is that the *obvious* answer is not
the good one.

Given `n - 1` distinct values drawn from `1..n`, which one is missing? You could
sort, or use a counting array. But the numbers `1..n` have a known total:

```java
long expected = (long) n * (n + 1) / 2;      // Gauss
long actual = 0;
for (int i = 0; i < n; i++) actual += a[i];
System.out.println(expected - actual);
```

O(n) time, **O(1) space**, one pass, no extra array at all. The same trick finds
a single duplicate: `actual - expected` is the repeated value.

**Two cautions that matter in an interview:**

- **Overflow.** `n * (n + 1) / 2` for `n` near 2 billion overflows `int` long
  before the answer does. Compute the total in `long`. The cases here are small,
  but saying it out loud is most of the point.
- **It only works for exactly one anomaly.** Two missing numbers give one sum
  and no way to separate them. That is where the counting array earns its keep
  — the last two variants use it for precisely that reason.

The lesson generalises: when the data has *structure* (a known range, a known
total, distinctness), arithmetic often beats searching.
""",
    [
        _p4ex("j4-pr-missing", "The missing number", "Easy",
              "The `n` values are distinct and drawn from `1..n+1`, with exactly one of "
              "that range absent. Print the missing value. Use the sum formula, not a "
              "search.",
              """
        long expected = (long) (n + 1) * (n + 2) / 2;
        long actual = 0;
        for (int i = 0; i < n; i++) {
            actual += a[i];
        }
        System.out.println(expected - actual);
""",
              [_acase(list(a), (len(a) + 1) * (len(a) + 2) // 2 - sum(a))
               for a in ([1, 2, 4], [2], [1, 2, 3, 4], [2, 3, 4, 5], [5, 1, 3, 2])],
              ["The full range here is `1..n+1` — there are `n` values present and "
               "one absent.",
               "The total of `1..N` is `N * (N + 1) / 2`, and here `N` is `n + 1`.",
               "So the expected total is `(n + 1) * (n + 2) / 2`.",
               "Subtract the actual total; the difference is the missing value.",
               "Compute in `long` and cast before multiplying, or large inputs "
               "overflow. `(long) (n + 1) * (n + 2) / 2` casts early enough; "
               "`(long) ((n + 1) * (n + 2) / 2)` would not.",
               "Case three is missing the largest value, case four the smallest — "
               "both fall out of the arithmetic with no special case."]),

        _p4ex("j4-pr-repeated", "The repeated number", "Easy",
              "The `n` values are drawn from `1..n-1`, each appearing once except one "
              "value which appears twice. Print the repeated value.",
              """
        long expected = (long) (n - 1) * n / 2;
        long actual = 0;
        for (int i = 0; i < n; i++) {
            actual += a[i];
        }
        System.out.println(actual - expected);
""",
              [_acase(list(a), sum(a) - (len(a) - 1) * len(a) // 2)
               for a in ([1, 2, 2], [1, 1], [1, 2, 3, 3], [3, 1, 2, 3],
                         [1, 2, 3, 4, 4])],
              ["The mirror of the missing-number trick.",
               "The range is `1..n-1`, so the expected total is `(n - 1) * n / 2`.",
               "The actual total is larger by exactly the repeated value.",
               "So the answer is `actual - expected`, not the other way round.",
               "Case two is the smallest possible instance: `1 1`, where the answer "
               "is `1`."]),

        _p4ex("j4-pr-both", "Missing and repeating together", "Medium",
              "The `n` values are drawn from `1..n`; one value is missing and one "
              "appears twice. Print the missing value and the repeated value on one "
              "line, separated by a space. A counting array is the clearest route.",
              """
        int[] freq = new int[n + 1];
        for (int i = 0; i < n; i++) {
            freq[a[i]]++;
        }
        int missing = 0;
        int repeated = 0;
        for (int v = 1; v <= n; v++) {
            if (freq[v] == 0) {
                missing = v;
            }
            if (freq[v] == 2) {
                repeated = v;
            }
        }
        System.out.println(missing + " " + repeated);
""",
              [_acase(list(a), (lambda c: f"{[v for v in range(1, len(a) + 1) if c.count(v) == 0][0]} "
                                          f"{[v for v in range(1, len(a) + 1) if c.count(v) == 2][0]}")(list(a)))
               for a in ([1, 2, 2], [1, 1], [1, 2, 3, 3], [3, 1, 2, 3],
                         [1, 2, 4, 4, 5])],
              ["Two anomalies mean one sum is not enough information — you need "
               "per-value counts.",
               "Allocate `new int[n + 1]` so slots `1..n` exist.",
               "One pass to count, one pass over slots `1..n` to read off the "
               "answers.",
               "The missing value has a count of `0`; the repeated one has `2`.",
               "Print missing first, then repeated."]),

        _p4ex("j4-pr-permutation", "Is it a permutation of 1..n?", "Medium",
              "Print `true` if the `n` values are exactly `1..n` in some order, each "
              "appearing once, and `false` otherwise. Values outside that range must be "
              "rejected without crashing.",
              """
        int[] freq = new int[n + 1];
        boolean ok = true;
        for (int i = 0; i < n; i++) {
            if (a[i] < 1 || a[i] > n) {
                ok = false;
            } else {
                freq[a[i]]++;
            }
        }
        for (int v = 1; v <= n; v++) {
            if (freq[v] != 1) {
                ok = false;
            }
        }
        System.out.println(ok);
""",
              [_acase(list(a), _jbool(sorted(a) == list(range(1, len(a) + 1))))
               for a in ([3, 1, 2], [1], [1, 1, 2], [1, 2, 4], [4, 3, 2, 1])],
              ["The range check has to come FIRST, and has to guard the counting — "
               "a value of `4` in a 3-element array would throw if you indexed with "
               "it.",
               "That is why the increment sits in an `else`.",
               "After counting, every slot from `1` to `n` must hold exactly `1`.",
               "Case four contains `4` with `n = 3`, which is out of range and must "
               "print `false` rather than crash.",
               "Case three has a duplicate and a gap, so it is `false` too."]),

        _p4ex("j4-pr-xor-missing", "The missing number, without adding", "Hard",
              "Same as the missing-number problem — `n` distinct values from `1..n+1`, "
              "one absent — but find it with **XOR** instead of sums, so nothing can "
              "overflow. Print the missing value.",
              """
        int x = 0;
        for (int v = 1; v <= n + 1; v++) {
            x = x ^ v;
        }
        for (int i = 0; i < n; i++) {
            x = x ^ a[i];
        }
        System.out.println(x);
""",
              [_acase(list(a), (len(a) + 1) * (len(a) + 2) // 2 - sum(a))
               for a in ([1, 2, 4], [2], [1, 2, 3, 4], [2, 3, 4, 5], [5, 1, 3, 2])],
              ["XOR has two properties that make this work: `v ^ v == 0`, and order "
               "does not matter.",
               "So XOR every number in the full range `1..n+1` together, then XOR "
               "every number actually present.",
               "Each present value appears twice in that combined XOR and cancels "
               "itself out. Exactly one number appears once — the missing one.",
               "Both loops fold into the same variable `x`, starting at `0`.",
               "Unlike the sum version this can never overflow, which is the reason "
               "to know it."]),
    ])


# --- Family E - rearranging in place -----------------------------------------

_P4_E = _jfam(
    "p4-partition", "Rearranging in place",
    "One read cursor, one write cursor.",
    """
The last big array motion: rearrange the contents according to some rule,
without a second array.

The tool is **two cursors moving at different speeds**. One reads every element;
the other marks where the next *kept* element belongs:

```java
int w = 0;                              // write cursor
for (int r = 0; r < n; r++) {           // read cursor
    if (keep(a[r])) {
        a[w] = a[r];
        w++;
    }
}
// a[0..w-1] now holds the kept elements, in their original relative order
```

Because `w` never runs ahead of `r`, you can never clobber an element you have
not read yet — which is what makes this safe to do in place.

Two properties fall out, and both get drilled below:

- **`w` ends up as the count** of kept elements. That is why the standard
  "remove duplicates in place" problems return a length rather than a new array.
- **It is stable.** Kept elements keep their relative order, because you copy
  them in the order you meet them. A version that swaps from both ends is faster
  but destroys that order — and interviewers usually want stability, so read the
  question carefully.

A second pass filling `a[w..n-1]` with whatever should go at the back turns the
same skeleton into a partition.
""",
    [
        _p4ex("j4-pr-move-zeros", "Push the zeros to the back", "Medium",
              "Move every `0` to the end of the array, keeping the relative order of "
              "everything else. Do it in place, then print the array in "
              "`Arrays.toString` format.",
              """
        int w = 0;
        for (int r = 0; r < n; r++) {
            if (a[r] != 0) {
                a[w] = a[r];
                w++;
            }
        }
        while (w < n) {
            a[w] = 0;
            w++;
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr([x for x in a if x != 0]
                                     + [0] * a.count(0)))
               for a in ([0, 1, 0, 3], [7], [0, 0], [1, 2, 3], [0, 0, 1])],
              ["Two cursors: `r` reads every slot, `w` marks where the next non-zero "
               "goes.",
               "Copy only the non-zeros forward, incrementing `w` each time.",
               "After the loop, `w` is the number of non-zeros — so everything from "
               "`w` to `n - 1` should be `0`.",
               "Fill that tail in a second loop.",
               "Order is preserved because you copy in the order you read. Case one "
               "must give `[1, 3, 0, 0]`, not `[3, 1, 0, 0]`."]),

        _p4ex("j4-pr-evens-first", "Evens first, odds after", "Medium",
              "Rearrange so that every even value comes before every odd value, with "
              "the evens in their original relative order and the odds likewise. Print "
              "the result in `Arrays.toString` format. A second array is allowed here.",
              """
        int[] out = new int[n];
        int w = 0;
        for (int r = 0; r < n; r++) {
            if (a[r] % 2 == 0) {
                out[w] = a[r];
                w++;
            }
        }
        for (int r = 0; r < n; r++) {
            if (a[r] % 2 != 0) {
                out[w] = a[r];
                w++;
            }
        }
        System.out.println(Arrays.toString(out));
""",
              [_acase(list(a), _jarr([x for x in a if x % 2 == 0]
                                     + [x for x in a if x % 2 != 0]))
               for a in ([1, 2, 3, 4], [7], [2, 4], [1, 3, 5], [4, 1, 2, 3, 6])],
              ["Keeping BOTH groups in their original order is much easier with a "
               "second array and two passes.",
               "First pass copies the evens; second pass continues from the same "
               "`w` and copies the odds.",
               "Declare `w` outside both loops so the second pass carries on where "
               "the first stopped.",
               "In Java `-3 % 2` is `-1`, not `1`, so test evenness with "
               "`% 2 == 0` rather than `% 2 == 1`.",
               "Swapping from both ends would be O(1) space but would scramble the "
               "order within each group."]),

        _p4ex("j4-pr-partition-k", "Everything below k first", "Medium",
              "Read the array, then `k`. Rearrange so that every value strictly less "
              "than `k` comes before every value greater than or equal to `k`, with "
              "both groups keeping their original relative order. Print the result in "
              "`Arrays.toString` format.",
              """
        int k = sc.nextInt();
        int[] out = new int[n];
        int w = 0;
        for (int r = 0; r < n; r++) {
            if (a[r] < k) {
                out[w] = a[r];
                w++;
            }
        }
        for (int r = 0; r < n; r++) {
            if (a[r] >= k) {
                out[w] = a[r];
                w++;
            }
        }
        System.out.println(Arrays.toString(out));
""",
              [_akcase(a, k, _jarr([x for x in a if x < k] + [x for x in a if x >= k]))
               for (a, k) in (([3, 1, 4, 1, 5], 3), ([7], 7), ([1, 2, 3], 0),
                              ([5, 4, 3], 10), ([2, 9, 2, 9], 5))],
              ["The same two-pass shape as evens-first, with the test swapped for a "
               "comparison against `k`.",
               "The split is **strictly** less than `k` versus greater-or-equal, so "
               "a value exactly equal to `k` goes in the second group. Case two "
               "checks that.",
               "One shared `w` across both passes.",
               "Case three sends everything to the second group, case four everything "
               "to the first — both must still print the original order."]),

        _p4ex("j4-pr-dedupe-sorted", "Squeeze out duplicates", "Medium",
              "The array arrives **already sorted** ascending. Remove duplicates in "
              "place so the distinct values fill the front, then print the new length "
              "on the first line and the distinct prefix in `Arrays.toString` format on "
              "the second.",
              """
        int w = 0;
        for (int r = 0; r < n; r++) {
            if (w == 0 || a[r] != a[w - 1]) {
                a[w] = a[r];
                w++;
            }
        }
        System.out.println(w);
        System.out.println(Arrays.toString(Arrays.copyOf(a, w)));
""",
              [_acase(list(a), _nl(len(sorted(set(a))), _jarr(sorted(set(a)))))
               for a in ([1, 1, 2, 3], [7], [1, 1, 1], [1, 2, 3], [0, 0, 1, 1, 2])],
              ["Because the array is sorted, duplicates are adjacent — so you only "
               "ever compare with the last value you KEPT.",
               "That is `a[w - 1]`, not `a[r - 1]`.",
               "Guard the very first element with `w == 0`, since `a[-1]` does not "
               "exist. Java's `||` short-circuits, so putting that test first is "
               "what makes it safe.",
               "`w` ends up as the number of distinct values.",
               "Print the prefix with `Arrays.copyOf(a, w)` — the tail still holds "
               "stale values and must not be shown."]),

        _p4ex("j4-pr-remove-k", "Delete every copy of k", "Easy",
              "Read the array, then `k`. Remove every occurrence of `k`, keeping the "
              "order of the rest. Print how many values remain on the first line, and "
              "those values in `Arrays.toString` format on the second.",
              """
        int k = sc.nextInt();
        int w = 0;
        for (int r = 0; r < n; r++) {
            if (a[r] != k) {
                a[w] = a[r];
                w++;
            }
        }
        System.out.println(w);
        System.out.println(Arrays.toString(Arrays.copyOf(a, w)));
""",
              [_akcase(a, k, _nl(len([x for x in a if x != k]),
                                 _jarr([x for x in a if x != k])))
               for (a, k) in (([3, 1, 3, 2], 3), ([7], 7), ([1, 2, 3], 9),
                              ([4, 4, 4], 4), ([0, 1, 0], 0))],
              ["The plain form of the write-cursor pattern: keep what does not "
               "match.",
               "`w` counts the survivors as it goes.",
               "Removing everything leaves `w` at `0`, and `Arrays.copyOf(a, 0)` "
               "correctly prints `[]`. Cases two and four check that.",
               "Print the count first, then the trimmed copy — never the whole "
               "array, whose tail is stale."]),
    ])


_PRACTICE[4] = [_P4_A, _P4_B, _P4_C, _P4_D, _P4_E]
