# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 4 — Rearranging and counting.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# Reversal, rotation, frequency counting, duplicates, and the missing/repeating
# family. These are the questions that get asked *by name* in interviews, and
# they are all built from module 1's swap plus one new idea: an array whose
# INDEX is a value rather than a position (the counting array).
#
# Collections are banned by the course linter, which is deliberate here: doing
# frequency counting with an int[] first is what makes a HashMap make sense
# later, in Part 6 of the roadmap.
# ---------------------------------------------------------------------------

_M4 = []


# --- Python mirrors ---------------------------------------------------------

def _rot_left(a, k):
    n = len(a)
    return [a[(i + k) % n] for i in range(n)]


def _rot_right(a, k):
    n = len(a)
    k %= n
    return a[n - k:] + a[:n - k] if k else list(a)


def _freq10(a):
    f = [0] * 10
    for x in a:
        f[x] += 1
    return f


def _mode10(a):
    f = _freq10(a)
    best = 0
    for v in range(1, 10):
        if f[v] > f[best]:
            best = v
    return best


def _first_unique(a):
    f = _freq10(a)
    for x in a:
        if f[x] == 1:
            return x
    return -1


def _dedupe_sorted(a):
    out = [a[0]]
    for x in a[1:]:
        if x != out[-1]:
            out.append(x)
    return out


# --- 4.1 Reversal -----------------------------------------------------------

_M4.append(_jlesson(
    "m4-reverse", "Reversing an array",
    "Two pointers walking toward each other — and the loop bound that undoes itself.",
    """
Reversing in place is the first genuine **two-pointer** algorithm, and the
pattern is worth more than the result: one index starts at the front, one at
the back, and they walk toward each other swapping as they go.

```java
int i = 0, j = a.length - 1;
while (i < j) {
    int t = a[i]; a[i] = a[j]; a[j] = t;
    i++;
    j--;
}
```

**`i < j`, never `i <= j`.** When they meet on the middle element of an
odd-length array there is nothing to do — swapping a slot with itself is
harmless but pointless. More importantly, once they have *crossed*, every
remaining swap would undo one you already did.

**The for-loop spelling is the same algorithm:**

```java
for (int i = 0; i < a.length / 2; i++) {
    int t = a[i]; a[i] = a[a.length - 1 - i]; a[a.length - 1 - i] = t;
}
```

`a.length / 2` is the crucial half. Run this loop to `a.length` instead and
every pair gets swapped twice — the array comes back **exactly as it started**.
It is the same double-swap trap as module 2's in-place transpose, and it is
just as silent: no exception, no warning, no change.

Integer division does the right thing for odd lengths on its own: for `n = 5`,
`n / 2` is `2`, so indices 0 and 1 swap with 4 and 3 and the middle element at
index 2 is correctly left alone.

**Reversing a sub-range** is the same loop with different starting points, and
it is the building block of the rotation trick in the next lesson:

```java
int i = from, j = to;                       // both inclusive here
while (i < j) { /* swap */ i++; j--; }
```

**Cost:** O(n) time, O(1) space, exactly `n / 2` swaps. Building a reversed
copy into a second array is also O(n) time but O(n) space — fine, and sometimes
what you want, but say which one you are doing.
""",
    warmup=[
        _jq("```java\nfor (int i = 0; i < a.length; i++) {\n    int t = a[i]; a[i] = a[a.length-1-i]; a[a.length-1-i] = t;\n}\n```\nWhat does this leave in `a`?",
            ["The original array, unchanged", "The reversed array",
             "An ArrayIndexOutOfBoundsException", "Half-reversed"],
            0,
            "Every pair is swapped once from the left and once from the right, so each swap "
            "is undone. The bound has to be `a.length / 2`."),
        _jq("For `n = 5`, how many swaps does a correct in-place reversal perform?",
            ["2", "5", "3", "4"],
            0,
            "`n / 2` is 2 in integer arithmetic: (0,4) and (1,3). The middle element at "
            "index 2 is already where it belongs."),
    ],
    exercises=[
        _je("j4-rev-cond", "Until they meet",
            "Reverse the array in place with two pointers and print it. Replace "
            "`____` with the `while` condition.",
            _jscan(
                _RD_ARR
                + "        int i = 0;\n"
                  "        int j = n - 1;\n"
                  "        while (i < j) {\n"
                  "            int t = a[i]; a[i] = a[j]; a[j] = t;\n"
                  "            i++;\n"
                  "            j--;\n"
                  "        }\n"
                  "        System.out.println(Arrays.toString(a));"),
            "while (i < j) {",
            [_acase(a, _jarr(list(reversed(a))))
             for a in ([1, 2, 3, 4], [1, 2, 3, 4, 5], [7], [9, 8])],
            hints=["Stop as soon as the two pointers meet or cross.",
                   "Swapping the middle element with itself is pointless; swapping past the "
                   "crossing point undoes your work.",
                   "`while (i < j) {`"]),

        _je("j4-rev-half", "Only half the way",
            "The same reversal written as a `for` loop. Replace `____` with the loop "
            "bound — get this wrong and the array comes back unchanged.",
            _jscan(
                _RD_ARR
                + "        for (int i = 0; i < n / 2; i++) {\n"
                  "            int t = a[i];\n"
                  "            a[i] = a[n - 1 - i];\n"
                  "            a[n - 1 - i] = t;\n"
                  "        }\n"
                  "        System.out.println(Arrays.toString(a));"),
            "i < n / 2",
            [_acase(a, _jarr(list(reversed(a))))
             for a in ([1, 2, 3, 4], [1, 2, 3, 4, 5], [7], [9, 8])],
            hints=["Each pass handles a *pair*, so you need half as many passes as elements.",
                   "Integer division rounds down, which is exactly right for odd lengths.",
                   "`i < n / 2`"]),

        _jfix("j4-rev-double", "The reversal that reverses twice",
              "This is supposed to reverse the array. It prints the array exactly as "
              "it came in. One number in the loop header is wrong.",
              _jscan(
                  _RD_ARR
                  + "        for (int i = 0; i < n; i++) {\n"
                    "            int t = a[i];\n"
                    "            a[i] = a[n - 1 - i];\n"
                    "            a[n - 1 - i] = t;\n"
                    "        }\n"
                    "        System.out.println(Arrays.toString(a));"),
              _jscan(
                  _RD_ARR
                  + "        for (int i = 0; i < n / 2; i++) {\n"
                    "            int t = a[i];\n"
                    "            a[i] = a[n - 1 - i];\n"
                    "            a[n - 1 - i] = t;\n"
                    "        }\n"
                    "        System.out.println(Arrays.toString(a));"),
              [_acase(a, _jarr(list(reversed(a))))
               for a in ([1, 2, 3, 4], [1, 2, 3], [5, 6])],
              hints=["Trace the pair (0, n-1). When else does the loop touch it?",
                     "Every swap is performed twice, which cancels it out.",
                     "Stop halfway: `i < n / 2`."]),

        _jch("j4-rev-range", "Reverse just a slice", "Medium",
             "Read the array, then `from` and `to` (both **inclusive**). Reverse only "
             "that slice, leave the rest alone, and print the whole array. Write the "
             "whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int from = sc.nextInt();\n"
                   "        int to = sc.nextInt();\n"
                   "        int i = from;\n"
                   "        int j = to;\n"
                   "        while (i < j) {\n"
                   "            int t = a[i]; a[i] = a[j]; a[j] = t;\n"
                   "            i++;\n"
                   "            j--;\n"
                   "        }\n"
                   "        System.out.println(Arrays.toString(a));"),
             "        int i = from;\n"
             "        int j = to;\n"
             "        while (i < j) {\n"
             "            int t = a[i]; a[i] = a[j]; a[j] = t;\n"
             "            i++;\n"
             "            j--;\n"
             "        }\n"
             "        System.out.println(Arrays.toString(a));",
             [_case(f"{len(a)}\n{_sp(a)}\n{f_}\n{t}",
                    _jarr(a[:f_] + list(reversed(a[f_:t + 1])) + a[t + 1:]))
              for (a, f_, t) in (([1, 2, 3, 4, 5], 1, 3),
                                 ([1, 2, 3, 4, 5], 0, 4),
                                 ([1, 2, 3, 4, 5], 2, 2),
                                 ([9, 8, 7], 0, 1))],
             hints=["Exactly the two-pointer loop, but the pointers start at `from` and `to`.",
                    "`to` is inclusive here, so `j` starts *at* it, not one past it.",
                    "A one-element slice (`from == to`) must leave the array unchanged — the "
                    "`i < j` condition already handles that."]),
    ],
    quiz=[
        _jq("Reversing in place costs how much extra memory?",
            ["O(1) — two index variables and one temp",
             "O(n) — you need a second array",
             "O(log n)",
             "O(n) for odd lengths, O(1) for even"],
            0,
            "That is the whole appeal of the two-pointer form. Building a reversed copy is "
            "equally fast but O(n) space."),
        _jq("Why does `n / 2` handle odd lengths correctly with no special case?",
            ["Integer division rounds down, so the untouched middle element is skipped",
             "Because odd arrays cannot be reversed",
             "It doesn't — odd lengths need `n / 2 + 1`",
             "Because the middle element is always 0"],
            0,
            "For n = 5, `n / 2` is 2, so the loop swaps (0,4) and (1,3) and stops. Index 2 "
            "is already in its final position."),
    ],
))

# --- 4.2 Rotation -----------------------------------------------------------

_M4.append(_jlesson(
    "m4-rotate", "Rotating an array",
    "Modular arithmetic, and the three-reversal trick that does it in O(1) space.",
    """
"Rotate left by `k`" means every element moves `k` places toward the front, and
the ones that fall off the front wrap around to the back.

```
{1, 2, 3, 4, 5} rotated LEFT  by 2  ->  {3, 4, 5, 1, 2}
{1, 2, 3, 4, 5} rotated RIGHT by 2  ->  {4, 5, 1, 2, 3}
```

**With an extra array it is a one-liner** — the whole problem is getting the
index expression right:

```java
int[] b = new int[n];
for (int i = 0; i < n; i++) b[i] = a[(i + k) % n];      // LEFT by k
```

Read it as: "the value that ends up at position `i` came from `k` places
further along, wrapping". For a **right** rotation, push instead of pull:

```java
for (int i = 0; i < n; i++) b[(i + k) % n] = a[i];       // RIGHT by k
```

Both are O(n) time, O(n) space.

**`k` can be bigger than `n`.** Rotating by `n` is the identity, so only
`k % n` matters. The `% n` inside the index handles it for free above — but the
moment you index without the `%`, as the three-reversal version does, you must
normalise first with `k = k % n;` or you walk off the end.

**The three-reversal trick does it in O(1) space,** and it is the answer
interviewers are fishing for. To rotate **right** by `k`:

1. Reverse the whole array.
2. Reverse the first `k` elements.
3. Reverse the remaining `n - k`.

```
{1,2,3,4,5}, k = 2
reverse all      -> {5,4,3,2,1}
reverse first 2  -> {4,5,3,2,1}
reverse last 3   -> {4,5,1,2,3}     right-rotated by 2
```

Why it works: reversing the whole array puts the last `k` elements at the front
(in the wrong order) and the first `n-k` at the back (also reversed). The two
smaller reversals repair each block. For a **left** rotation, reverse the first
`k` and the rest first, then reverse the whole thing — or just rotate right by
`n - k`.

**Do not "rotate by one, k times".** It is O(n·k), which for k ≈ n is O(n²) —
and it is the answer that ends the interview early.
""",
    warmup=[
        _jq("`{1,2,3,4,5}` rotated LEFT by 2 is…",
            ["[3, 4, 5, 1, 2]", "[4, 5, 1, 2, 3]", "[2, 1, 5, 4, 3]", "[5, 4, 3, 2, 1]"],
            0,
            "Left means everything shifts toward the front, and 1 and 2 wrap around to the "
            "back. Right by 2 would give [4, 5, 1, 2, 3]."),
        _jq("Rotating an array of 5 elements left by 7 is the same as rotating left by…",
            ["2", "7", "5", "12"],
            0,
            "Every full turn of `n` restores the array, so only `k % n` matters — here "
            "7 % 5 = 2."),
    ],
    exercises=[
        _je("j4-rot-left", "Pull from further along",
            "Rotate the array **left** by `k` into a second array and print it. "
            "Replace `____` with the index expression that says where `b[i]` comes "
            "from. `k` may be larger than `n`.",
            _jscan(
                _RD_ARR
                + "        int k = sc.nextInt();\n"
                  "        int[] b = new int[n];\n"
                  "        for (int i = 0; i < n; i++) b[i] = a[(i + k) % n];\n"
                  "        System.out.println(Arrays.toString(b));"),
            "a[(i + k) % n]",
            [_akcase(a, k, _jarr(_rot_left(a, k)))
             for (a, k) in (([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 0),
                            ([1, 2, 3, 4, 5], 7), ([9], 3))],
            hints=["The element landing at `i` started `k` places further along.",
                   "Wrap with `% n` so it comes round the front again.",
                   "`a[(i + k) % n]`"],
            difficulty="Medium"),

        _je("j4-rot-right", "Push further along",
            "Now rotate **right** by `k`. Same array, opposite direction — this time "
            "the modulus goes on the *destination*. Replace `____` with the whole "
            "assignment.",
            _jscan(
                _RD_ARR
                + "        int k = sc.nextInt();\n"
                  "        int[] b = new int[n];\n"
                  "        for (int i = 0; i < n; i++) b[(i + k) % n] = a[i];\n"
                  "        System.out.println(Arrays.toString(b));"),
            "b[(i + k) % n] = a[i];",
            [_akcase(a, k, _jarr(_rot_right(a, k)))
             for (a, k) in (([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 0),
                            ([1, 2, 3, 4, 5], 6), ([4, 5], 1))],
            hints=["Read `a[i]` and decide where it lands.",
                   "It moves `k` places toward the back, wrapping.",
                   "`b[(i + k) % n] = a[i];`"],
            difficulty="Medium"),

        _jfix("j4-rot-mod", "It breaks when k is large",
              "This rotates left by `k` by copying into a second array. It works for "
              "small `k` and throws `ArrayIndexOutOfBoundsException` as soon as `k` "
              "reaches `n`. Fix it.",
              _jscan(
                  _RD_ARR
                  + "        int k = sc.nextInt();\n"
                    "        int[] b = new int[n];\n"
                    "        for (int i = 0; i < n; i++) b[i] = a[i + k];\n"
                    "        System.out.println(Arrays.toString(b));"),
              _jscan(
                  _RD_ARR
                  + "        int k = sc.nextInt();\n"
                    "        int[] b = new int[n];\n"
                    "        for (int i = 0; i < n; i++) b[i] = a[(i + k) % n];\n"
                    "        System.out.println(Arrays.toString(b));"),
              [_akcase(a, k, _jarr(_rot_left(a, k)))
               for (a, k) in (([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 5),
                              ([1, 2, 3], 4))],
              hints=["What is `a[i + k]` when `i + k` reaches `n`?",
                     "The index has to wrap round to the front of the array.",
                     "`a[(i + k) % n]`"]),

        _jch("j4-rot-reversal", "Rotate with no extra array", "Hard",
             "Rotate the array **right** by `k` **in place**, using three reversals "
             "and O(1) extra space:\n\n"
             "1. reverse the whole array,\n"
             "2. reverse the first `k` elements,\n"
             "3. reverse the last `n - k`.\n\n"
             "Normalise `k` with `k = k % n;` first, since `k` may be at least `n`. "
             "Print the result. Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int k = sc.nextInt();\n"
                   "        k = k % n;\n"
                   "        int i = 0;\n"
                   "        int j = n - 1;\n"
                   "        while (i < j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }\n"
                   "        i = 0;\n"
                   "        j = k - 1;\n"
                   "        while (i < j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }\n"
                   "        i = k;\n"
                   "        j = n - 1;\n"
                   "        while (i < j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }\n"
                   "        System.out.println(Arrays.toString(a));"),
             "        k = k % n;\n"
             "        int i = 0;\n"
             "        int j = n - 1;\n"
             "        while (i < j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }\n"
             "        i = 0;\n"
             "        j = k - 1;\n"
             "        while (i < j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }\n"
             "        i = k;\n"
             "        j = n - 1;\n"
             "        while (i < j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }\n"
             "        System.out.println(Arrays.toString(a));",
             [_akcase(a, k, _jarr(_rot_right(a, k)))
              for (a, k) in (([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 0),
                             ([1, 2, 3, 4, 5], 5), ([1, 2, 3, 4, 5], 7),
                             ([8, 9], 1), ([6], 4))],
             hints=["Three copies of the same two-pointer loop, with different start and end.",
                    "Reuse `i` and `j` — declare them once, then reassign before each reversal.",
                    "The second reversal covers indices `0 .. k-1`; the third covers "
                    "`k .. n-1`.",
                    "With `k = 0` the second reversal has `j = -1`, so its `while` never runs "
                    "— and the first and third reversals cancel out. That is correct."]),
    ],
    quiz=[
        _jq("Why is 'rotate by one, k times' a bad answer?",
            ["It is O(n·k), which becomes O(n²) when k is comparable to n",
             "It gives the wrong result",
             "It uses O(n) extra space",
             "It only works for k < n"],
            0,
            "It is correct, just quadratic. The extra-array version is O(n) time / O(n) "
            "space, and the three-reversal version is O(n) time / O(1) space."),
        _jq("In the three-reversal method, why must you do `k = k % n` first?",
            ["Steps 2 and 3 index by `k` directly, with no modulus to save them",
             "Because reversal only works for small k",
             "To make the rotation go the right way",
             "You don't — the reversals handle it"],
            0,
            "`j = k - 1` and `i = k` are raw indices. With k >= n they run off the end, "
            "unlike the `(i + k) % n` form which wraps on its own."),
    ],
))

# --- 4.3 Frequency counting -------------------------------------------------

_M4.append(_jlesson(
    "m4-frequency", "Counting with an array",
    "Index by value, not by position — the trick behind half of all counting questions.",
    """
Up to now every index has been a *position*. The counting array flips that
round: the **index is a value**, and the slot holds how many times that value
appeared.

```java
int[] freq = new int[10];                 // one slot per possible value, 0..9
for (int i = 0; i < a.length; i++) {
    freq[a[i]]++;                          // a[i] is used as an INDEX
}
```

Read `freq[a[i]]++` carefully — it is the whole lesson. `a[i]` is a value from
the data; using it to index `freq` is what makes this O(n) instead of O(n²).

**The precondition is a known, small value range.** `new int[10]` only works
because the values are 0…9. Three ways the range bites:

- **Negatives.** `freq[-3]` throws. Shift by an offset: with values in
  −5…5, allocate `new int[11]` and use `freq[x + 5]++`, remembering to
  subtract the offset when you read the answer back.
- **Huge ranges.** Values up to a billion would need a billion slots. That is
  exactly the point where a `HashMap<Integer, Integer>` takes over — Part 6 of
  the roadmap. Counting arrays are faster when they fit and impossible when
  they do not.
- **Sparse data.** Ten values spread over 0…1,000,000 wastes a megabyte to
  store ten counts.

**Reading the answers back** is a loop over the *value* range, not the data:

```java
for (int v = 0; v < freq.length; v++)
    if (freq[v] > 0) System.out.println(v + " appears " + freq[v] + " times");
```

Notice this comes out in **ascending value order** for free — a counting array
is a sort in disguise (that is literally counting sort).

**The mode** — the most frequent value — is module 1's argmax over `freq`:

```java
int mode = 0;
for (int v = 1; v < freq.length; v++) if (freq[v] > freq[mode]) mode = v;
```

Strict `>` means ties are broken by the **smallest** value, because the loop
walks values in ascending order.

**Two passes, not one.** Anything of the form "the first element that appears
exactly once" needs pass 1 to count and pass 2 to scan the original data in
order. Trying to do it in one pass is where people get stuck.
""",
    warmup=[
        _jq("What does `freq[a[i]]++;` do?",
            ["Uses the VALUE a[i] as an index into freq, and increments that slot",
             "Increments a[i] and then indexes freq",
             "Increments the i-th slot of freq",
             "It does not compile"],
            0,
            "The value becomes the index. That inversion is the entire trick — and it is why "
            "the value range has to be small and non-negative."),
        _jq("Values range from -5 to 5. What does the counting array look like?",
            ["`new int[11]`, incremented as `freq[x + 5]++`",
             "`new int[5]`, incremented as `freq[x]++`",
             "`new int[11]`, incremented as `freq[x]++`",
             "You cannot count negative values"],
            0,
            "Eleven distinct values need eleven slots, and the offset of +5 maps -5 onto "
            "index 0. Remember to subtract it again when reporting the value."),
    ],
    exercises=[
        _je("j4-freq-count", "Count the digits",
            "Every value is a single digit, 0 through 9. Print the ten counts on one "
            "line, in value order. Replace `____` with the statement that records "
            "one observation.",
            _jscan(
                _RD_ARR
                + "        int[] freq = new int[10];\n"
                  "        for (int i = 0; i < n; i++) freq[a[i]]++;\n"
                  '        for (int v = 0; v < 10; v++) System.out.print(freq[v] + " ");\n'
                  "        System.out.println();"),
            "freq[a[i]]++;",
            [_acase(a, _sp(_freq10(a)))
             for a in ([1, 3, 3, 7], [0, 0, 0], [9], [5, 4, 3, 2, 1, 0])],
            hints=["The value you just read is the slot you want to bump.",
                   "So the value goes inside the square brackets.",
                   "`freq[a[i]]++;`"]),

        _je("j4-freq-mode", "The most common value",
            "Print the value that appears most often (values are 0–9). On a tie, "
            "print the **smallest** such value. Replace `____` with the line that "
            "keeps `mode` up to date.",
            _jscan(
                _RD_ARR
                + "        int[] freq = new int[10];\n"
                  "        for (int i = 0; i < n; i++) freq[a[i]]++;\n"
                  "        int mode = 0;\n"
                  "        for (int v = 1; v < 10; v++) {\n"
                  "            if (freq[v] > freq[mode]) mode = v;\n"
                  "        }\n"
                  "        System.out.println(mode);"),
            "if (freq[v] > freq[mode]) mode = v;",
            [_acase(a, _mode10(a))
             for a in ([1, 3, 3, 7], [1, 1, 2, 2], [4], [9, 9, 9, 1, 1, 1, 0])],
            hints=["This is module 1's argmax, over `freq` instead of over the data.",
                   "Compare counts; assign values.",
                   "`if (freq[v] > freq[mode]) mode = v;` — strict `>` keeps the smallest "
                   "value on a tie, because the loop goes upward."],
            difficulty="Medium"),

        _jfix("j4-freq-index", "Counting the wrong thing",
              "This should count how many times each digit 0–9 appears. Instead it "
              "prints mostly 1s: it is counting positions rather than values. Fix it.",
              _jscan(
                  _RD_ARR
                  + "        int[] freq = new int[10];\n"
                    "        for (int i = 0; i < n; i++) freq[i]++;\n"
                    '        for (int v = 0; v < 10; v++) System.out.print(freq[v] + " ");\n'
                    "        System.out.println();"),
              _jscan(
                  _RD_ARR
                  + "        int[] freq = new int[10];\n"
                    "        for (int i = 0; i < n; i++) freq[a[i]]++;\n"
                    '        for (int v = 0; v < 10; v++) System.out.print(freq[v] + " ");\n'
                    "        System.out.println();"),
              [_acase(a, _sp(_freq10(a)))
               for a in ([1, 3, 3, 7], [2, 2, 2], [0, 9])],
              hints=["Which index is being incremented — a position or a value?",
                     "A counting array is indexed by the value you observed.",
                     "`freq[a[i]]++;`"]),

        _jch("j4-freq-unique", "First value that appears once", "Medium",
             "Values are 0–9. Print the **first** value in the original array order "
             "that appears exactly once, or `-1` if every value repeats. This needs "
             "two passes: one to count, one to scan the data in order. Write the "
             "whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int[] freq = new int[10];\n"
                   "        for (int i = 0; i < n; i++) freq[a[i]]++;\n"
                   "        int answer = -1;\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            if (freq[a[i]] == 1) { answer = a[i]; break; }\n"
                   "        }\n"
                   "        System.out.println(answer);"),
             "        int[] freq = new int[10];\n"
             "        for (int i = 0; i < n; i++) freq[a[i]]++;\n"
             "        int answer = -1;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            if (freq[a[i]] == 1) { answer = a[i]; break; }\n"
             "        }\n"
             "        System.out.println(answer);",
             [_acase(a, _first_unique(a))
              for a in ([2, 3, 2, 4, 3], [1, 1, 2, 2], [7], [5, 5, 5, 1], [1, 2, 3])],
             hints=["Pass 1 fills the counting array. Do not try to answer during it.",
                    "Pass 2 walks the ORIGINAL array, so 'first' means first in input order — "
                    "walking `freq` instead would give you the smallest value, not the first.",
                    "`if (freq[a[i]] == 1) { answer = a[i]; break; }`"]),
    ],
    quiz=[
        _jq("When is a counting array the wrong tool?",
            ["When the value range is huge or sparse — allocate a HashMap instead",
             "When there are more than 100 elements",
             "When the data is unsorted",
             "When values repeat"],
            0,
            "The array costs one slot per *possible* value, not per observed one. Values up "
            "to a billion need a billion slots; a map costs one entry per distinct value."),
        _jq("Reading a counting array back with `for (int v = 0; v < freq.length; v++)` gives values in what order?",
            ["Ascending value order — which is counting sort",
             "Original input order",
             "Descending frequency order",
             "Unspecified order"],
            0,
            "The index *is* the value, so walking the array upward walks the values upward. "
            "Emitting each value `freq[v]` times is literally counting sort."),
    ],
))

# --- 4.4 Duplicates ---------------------------------------------------------

_M4.append(_jlesson(
    "m4-duplicates", "Duplicates",
    "The O(n²) way, the sorted way, and removing them in place.",
    """
"Does this array contain a duplicate?" has three standard answers, and knowing
all three — with their costs — is the actual interview question.

**1. Brute force, O(n²) time, O(1) space.** Compare every pair:

```java
boolean dup = false;
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)          // j = i + 1, never j = 0
        if (a[i] == a[j]) dup = true;
```

`j = i + 1` matters twice over. It stops an element being compared with
**itself** (which would report a duplicate for every array), and it stops each
pair being checked twice.

**2. Sort first, O(n log n) time, O(1) space.** Once sorted, duplicates are
adjacent, so one pass finds them:

```java
Arrays.sort(a);
for (int i = 1; i < n; i++) if (a[i] == a[i - 1]) dup = true;
```

This destroys the original order — say so out loud, and copy first if the
caller cares.

**3. Counting array or hash set, O(n) time, O(range) space.** The counting
array from lesson 4.3: any slot reaching 2 is a duplicate. Fastest, but it buys
that speed with memory.

Naming all three and stating the trade-off is worth more than producing any one
of them.

**Counting distinct values in a sorted array** is the same adjacency idea,
inverted: a value is "new" exactly when it differs from its predecessor.

```java
int distinct = 1;                              // a[0] is always new
for (int i = 1; i < n; i++) if (a[i] != a[i - 1]) distinct++;
```

**Removing duplicates in place** is the classic follow-up. You cannot shrink an
array, so the contract becomes: *compact the unique values into the front and
return how many there are.* It is a two-pointer method — `k` is the write
position, `i` is the read position:

```java
int k = 1;                                     // a[0] is always kept
for (int i = 1; i < n; i++) {
    if (a[i] != a[k - 1]) {                     // different from last KEPT
        a[k] = a[i];
        k++;
    }
}
// a[0..k-1] now holds the unique values; a[k..] is stale
```

Compare against `a[k - 1]` — the last value you kept — not against `a[i - 1]`.
On `{1, 1, 1, 2}` the two agree, but the habit of comparing against the *kept*
value is what generalises to "keep at most two of each" and its cousins.
""",
    warmup=[
        _jq("`for (int j = 0; j < n; j++) if (a[i] == a[j]) dup = true;` — what goes wrong?",
            ["When j equals i, the element matches itself and every array reports a duplicate",
             "It misses duplicates at the end",
             "It is O(n) instead of O(n²)",
             "Nothing — it is correct"],
            0,
            "The inner loop must start at `i + 1`, which also halves the work by never "
            "checking a pair twice."),
        _jq("In-place duplicate removal returns `k`. What is `a[k]` afterwards?",
            ["Stale leftover data — only a[0..k-1] is meaningful",
             "Always 0", "The number of duplicates removed", "The last unique value"],
            0,
            "Arrays cannot shrink, so the tail keeps whatever was there. The contract is "
            "'the first k slots are the answer', which the caller must honour."),
    ],
    exercises=[
        _je("j4-dup-pairs", "Any duplicates at all?",
            "Print `true` when any value appears more than once, otherwise `false`. "
            "Use the brute-force pair scan. Replace `____` with the inner loop header.",
            _jscan(
                _RD_ARR
                + "        boolean dup = false;\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            for (int j = i + 1; j < n; j++) {\n"
                  "                if (a[i] == a[j]) dup = true;\n"
                  "            }\n"
                  "        }\n"
                  "        System.out.println(dup);"),
            "for (int j = i + 1; j < n; j++) {",
            [_acase(a, _jbool(len(set(a)) != len(a)))
             for a in ([1, 2, 3], [1, 2, 1], [5], [4, 4], [9, 8, 7, 8])],
            hints=["Never compare an element with itself.",
                   "Start the inner index just past the outer one.",
                   "`for (int j = i + 1; j < n; j++) {`"]),

        _je("j4-dup-distinct", "How many distinct values?",
            "The array arrives **sorted**. Print how many distinct values it holds. "
            "Replace `____` with the check that spots a value you have not seen.",
            _jscan(
                _RD_ARR
                + "        int distinct = 1;\n"
                  "        for (int i = 1; i < n; i++) {\n"
                  "            if (a[i] != a[i - 1]) distinct++;\n"
                  "        }\n"
                  "        System.out.println(distinct);"),
            "if (a[i] != a[i - 1]) distinct++;",
            [_acase(a, len(set(a)))
             for a in ([1, 1, 2, 3, 3], [1, 2, 3], [4, 4, 4], [7])],
            hints=["In sorted data, equal values sit next to each other.",
                   "So a new value is one that differs from its left neighbour.",
                   "`if (a[i] != a[i - 1]) distinct++;`"]),

        _jfix("j4-dup-self", "Everything looks like a duplicate",
              "This should report whether the array contains a repeated value. It "
              "prints `true` for every input, including `{1, 2, 3}`. Fix it.",
              _jscan(
                  _RD_ARR
                  + "        boolean dup = false;\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            for (int j = 0; j < n; j++) {\n"
                    "                if (a[i] == a[j]) dup = true;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(dup);"),
              _jscan(
                  _RD_ARR
                  + "        boolean dup = false;\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            for (int j = i + 1; j < n; j++) {\n"
                    "                if (a[i] == a[j]) dup = true;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(dup);"),
              [_acase(a, _jbool(len(set(a)) != len(a)))
               for a in ([1, 2, 3], [1, 2, 1], [8])],
              hints=["What happens on the iteration where `j` equals `i`?",
                     "An element is always equal to itself.",
                     "Start the inner loop at `i + 1`."]),

        _jch("j4-dup-remove", "Remove duplicates in place", "Hard",
             "The array arrives **sorted**. Compact the unique values into the front "
             "of the same array, then print two lines: the count of unique values, "
             "and those values space-separated. Use O(1) extra space — no second "
             "array. Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int k = 1;\n"
                   "        for (int i = 1; i < n; i++) {\n"
                   "            if (a[i] != a[k - 1]) {\n"
                   "                a[k] = a[i];\n"
                   "                k++;\n"
                   "            }\n"
                   "        }\n"
                   "        System.out.println(k);\n"
                   '        for (int i = 0; i < k; i++) System.out.print(a[i] + " ");\n'
                   "        System.out.println();"),
             "        int k = 1;\n"
             "        for (int i = 1; i < n; i++) {\n"
             "            if (a[i] != a[k - 1]) {\n"
             "                a[k] = a[i];\n"
             "                k++;\n"
             "            }\n"
             "        }\n"
             "        System.out.println(k);\n"
             '        for (int i = 0; i < k; i++) System.out.print(a[i] + " ");\n'
             "        System.out.println();",
             [_acase(a, _nl(len(_dedupe_sorted(a)), _sp(_dedupe_sorted(a))))
              for a in ([1, 1, 2, 3, 3], [1, 2, 3], [4, 4, 4], [7], [0, 0, 1, 1, 2, 2])],
             hints=["Two pointers: `k` is where to write next, `i` is where to read.",
                    "`a[0]` is always unique, so start `k` at 1 and `i` at 1.",
                    "Compare `a[i]` against `a[k - 1]` — the last value you actually kept.",
                    "Print only the first `k` slots; whatever is past them is stale."]),
    ],
    quiz=[
        _jq("Detecting duplicates by sorting first costs what, and what does it cost you?",
            ["O(n log n) time and O(1) space, but it destroys the original order",
             "O(n) time and O(n) space",
             "O(n²) time and O(1) space",
             "O(n log n) time, and nothing is lost"],
            0,
            "Sorting is the middle option between brute force and a hash set. If the caller "
            "needs the original order, copy the array first — and say so."),
        _jq("Why compare against `a[k - 1]` rather than `a[i - 1]` when compacting?",
            ["`a[k-1]` is the last value actually KEPT, which is what 'already seen' means",
             "`a[i-1]` would be out of bounds",
             "They are never equal",
             "To make the loop O(n)"],
            0,
            "For plain deduplication both work, but comparing against the kept value is the "
            "form that generalises — 'keep at most two of each' becomes `a[i] != a[k - 2]`."),
    ],
))

# --- 4.5 Missing and repeating ----------------------------------------------

_M4.append(_jlesson(
    "m4-missing", "Missing and repeating numbers",
    "The sum trick, the XOR trick, and the counting array that solves all of them.",
    """
A family of interview questions with a shared setup: an array that is *almost*
a permutation of `1..n`, with something wrong.

**"The array holds n distinct values from 1..n+1. Which one is missing?"**

The arithmetic answer is O(n) time, O(1) space, and needs no loop at all beyond
the sum:

```java
int expected = (n + 1) * (n + 2) / 2;      // sum of 1..n+1
int actual = 0;
for (int i = 0; i < n; i++) actual += a[i];
System.out.println(expected - actual);
```

The sum of `1..m` is `m(m+1)/2`. Here `m = n + 1`, so the expected total is
`(n+1)(n+2)/2`. Whatever is left over when you subtract the real total is the
missing value.

**The catch:** the sum can overflow `int` for large `n`. Use `long`, or use the
XOR trick, which cannot overflow at all:

```java
int x = 0;
for (int i = 0; i < n; i++) x ^= a[i];      // XOR of everything present
for (int v = 1; v <= n + 1; v++) x ^= v;    // XOR of everything expected
System.out.println(x);                       // only the missing one survives
```

Why it works: `v ^ v == 0` and `x ^ 0 == x`. Every value that appears in both
lists cancels itself out, leaving exactly the one that appeared only in the
expected list. XOR is commutative and associative, so the order never matters.

**"One value repeats — which?"** The sum trick inverts: `actual - expected` is
the repeated value. And when both a value is missing *and* another repeats,
one equation is not enough for two unknowns — which is where the counting
array wins:

```java
int[] count = new int[n + 1];               // values are 1..n
for (int i = 0; i < n; i++) count[a[i]]++;
for (int v = 1; v <= n; v++) {
    if (count[v] == 0) missing = v;
    if (count[v] == 2) repeated = v;
}
```

O(n) time, O(n) space, and — unlike the arithmetic tricks — it generalises
immediately to "which values are missing" and "which repeat how often". Reach
for the clever trick when space is constrained; reach for the counting array
when the question grows.
""",
    warmup=[
        _jq("An array holds 4 distinct values from 1..5, summing to 11. Which is missing?",
            ["4", "1", "5", "3"],
            0,
            "1+2+3+4+5 = 15, and 15 - 11 = 4. The sum trick is one subtraction once you have "
            "the total."),
        _jq("Why does the XOR trick not overflow?",
            ["XOR never carries — the result always fits in the same number of bits",
             "Because it uses long internally",
             "It does overflow, for large n",
             "Because the values are small"],
            0,
            "XOR is bitwise: each output bit depends only on the matching input bits. There "
            "is nothing to carry, so the magnitude never grows."),
    ],
    exercises=[
        _je("j4-mis-sum", "The missing number, by arithmetic",
            "The array holds `n` distinct values drawn from `1..n+1` — exactly one is "
            "missing. Print it, using the sum formula. Replace `____` with the "
            "expected total.",
            _jscan(
                _RD_ARR
                + "        int expected = (n + 1) * (n + 2) / 2;\n"
                  "        int actual = 0;\n"
                  "        for (int i = 0; i < n; i++) actual += a[i];\n"
                  "        System.out.println(expected - actual);"),
            "(n + 1) * (n + 2) / 2",
            [_acase(a, (len(a) + 1) * (len(a) + 2) // 2 - sum(a))
             for a in ([1, 2, 4, 5], [2, 3, 4, 5], [1, 2, 3, 4], [2])],
            hints=["The values run from 1 to n+1, so you want the sum of the first n+1 "
                   "integers.",
                   "The sum of 1..m is m(m+1)/2 — substitute m = n + 1.",
                   "`(n + 1) * (n + 2) / 2`"],
            difficulty="Medium"),

        _je("j4-mis-xor", "The missing number, by XOR",
            "Same problem, no arithmetic and no overflow risk. `x` already holds the "
            "XOR of everything present — replace `____` with the loop that XORs in "
            "everything that *should* be there.",
            _jscan(
                _RD_ARR
                + "        int x = 0;\n"
                  "        for (int i = 0; i < n; i++) x ^= a[i];\n"
                  "        for (int v = 1; v <= n + 1; v++) x ^= v;\n"
                  "        System.out.println(x);"),
            "for (int v = 1; v <= n + 1; v++) x ^= v;",
            [_acase(a, (len(a) + 1) * (len(a) + 2) // 2 - sum(a))
             for a in ([1, 2, 4, 5], [2, 3, 4, 5], [1, 2, 3, 4], [2])],
            hints=["The expected values run 1 through n+1 inclusive.",
                   "Every value present in both lists cancels itself to 0.",
                   "`for (int v = 1; v <= n + 1; v++) x ^= v;`"],
            difficulty="Medium"),

        _jfix("j4-mis-formula", "Off by one row of the triangle",
              "This should print the missing value from an array of `n` distinct "
              "values drawn from `1..n+1`. It is consistently wrong by the largest "
              "expected value. Fix the formula.",
              _jscan(
                  _RD_ARR
                  + "        int expected = n * (n + 1) / 2;\n"
                    "        int actual = 0;\n"
                    "        for (int i = 0; i < n; i++) actual += a[i];\n"
                    "        System.out.println(expected - actual);"),
              _jscan(
                  _RD_ARR
                  + "        int expected = (n + 1) * (n + 2) / 2;\n"
                    "        int actual = 0;\n"
                    "        for (int i = 0; i < n; i++) actual += a[i];\n"
                    "        System.out.println(expected - actual);"),
              [_acase(a, (len(a) + 1) * (len(a) + 2) // 2 - sum(a))
               for a in ([1, 2, 4, 5], [2, 3, 4], [1, 3])],
              hints=["`n * (n + 1) / 2` is the sum of 1..n. What is the actual value range?",
                     "There are n elements but n+1 possible values.",
                     "Substitute m = n + 1 into m(m+1)/2."]),

        _jch("j4-mis-both", "One missing, one repeated", "Hard",
             "The array holds `n` values, each in `1..n`. Exactly one value is "
             "missing and exactly one appears twice. Print them on one line as "
             "`missing repeated`. Use a counting array — two unknowns need more than "
             "one equation. Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int[] count = new int[n + 1];\n"
                   "        for (int i = 0; i < n; i++) count[a[i]]++;\n"
                   "        int missing = 0;\n"
                   "        int repeated = 0;\n"
                   "        for (int v = 1; v <= n; v++) {\n"
                   "            if (count[v] == 0) missing = v;\n"
                   "            if (count[v] == 2) repeated = v;\n"
                   "        }\n"
                   '        System.out.println(missing + " " + repeated);'),
             "        int[] count = new int[n + 1];\n"
             "        for (int i = 0; i < n; i++) count[a[i]]++;\n"
             "        int missing = 0;\n"
             "        int repeated = 0;\n"
             "        for (int v = 1; v <= n; v++) {\n"
             "            if (count[v] == 0) missing = v;\n"
             "            if (count[v] == 2) repeated = v;\n"
             "        }\n"
             '        System.out.println(missing + " " + repeated);',
             [_acase(a, "%d %d" % (
                 next(v for v in range(1, len(a) + 1) if a.count(v) == 0),
                 next(v for v in range(1, len(a) + 1) if a.count(v) == 2)))
              for a in ([1, 2, 2, 4], [3, 1, 3], [1, 1], [4, 3, 6, 2, 1, 1])],
             hints=["Values run 1..n, so the counting array needs `n + 1` slots (index 0 goes "
                    "unused).",
                    "Fill it in one pass, then answer in a second pass over the VALUES 1..n.",
                    "A count of 0 is the missing value; a count of 2 is the repeated one.",
                    "Both answers come out of the same loop — do not write two loops."]),
    ],
    quiz=[
        _jq("For n = 100,000, the sum trick's `expected` is about 5 × 10⁹. What happens in an `int`?",
            ["It overflows and wraps negative, giving a wrong answer with no exception",
             "Java promotes it to long automatically",
             "It throws ArithmeticException",
             "Nothing — 5 × 10⁹ fits in an int"],
            0,
            "`int` tops out near 2.1 × 10⁹. Use `long` for the totals, or use XOR, which "
            "cannot overflow."),
        _jq("Why can't the sum trick alone solve 'one missing AND one repeated'?",
            ["One equation cannot determine two unknowns — you only learn their difference",
             "Because the sum overflows",
             "It can, in a single pass",
             "Because the array is unsorted"],
            0,
            "`actual - expected` gives `repeated - missing`. A second equation (the sum of "
            "squares) would work, but a counting array is clearer and generalises."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m4_workbench(a, k):
    return _nl(
        f"reversed={_jarr(list(reversed(a)))}",
        f"rotated={_jarr(_rot_left(a, k))}",
        f"freq={_sp(_freq10(a))}",
        f"mode={_mode10(a)}",
    )


_M4_CAP = _jcap(
    "Array workbench",
    """
Four of this module's five lessons in one program.

Read `n`, then `n` values that are all single digits (0–9), then `k`. Print:

```
reversed=<the array reversed, in Arrays.toString form>
rotated=<the ORIGINAL array rotated LEFT by k, in Arrays.toString form>
freq=<the counts of 0,1,…,9, space separated>
mode=<the most frequent value; the smallest one, if there is a tie>
```

The one thing that will bite you: **`rotated` is the rotation of the original
array, not of the reversed one.** Reversing in place destroys the input, so
either work on a copy (`Arrays.copyOf` — module 1) or build the reversed array
separately. This is the aliasing lesson coming back to collect.

`k` may be larger than `n`, so the rotation needs its modulus. And `mode`
breaks ties toward the smaller value, which falls out for free if you scan
values 0 upward with a strict `>`.
""",
    _jch("j4-cap-workbench", "Array workbench", "Hard",
         "Write the whole program where you see `____` — four lines of output, in "
         "the order `reversed`, `rotated`, `freq`, `mode`.",
         _jscan(
             _RD_ARR
             + "        int k = sc.nextInt();\n"
               "        int[] rev = Arrays.copyOf(a, n);\n"
               "        int i = 0;\n"
               "        int j = n - 1;\n"
               "        while (i < j) {\n"
               "            int t = rev[i]; rev[i] = rev[j]; rev[j] = t;\n"
               "            i++;\n"
               "            j--;\n"
               "        }\n"
               '        System.out.println("reversed=" + Arrays.toString(rev));\n'
               "        int[] rot = new int[n];\n"
               "        for (int p = 0; p < n; p++) rot[p] = a[(p + k) % n];\n"
               '        System.out.println("rotated=" + Arrays.toString(rot));\n'
               "        int[] freq = new int[10];\n"
               "        for (int p = 0; p < n; p++) freq[a[p]]++;\n"
               '        System.out.print("freq=");\n'
               '        for (int v = 0; v < 10; v++) System.out.print(freq[v] + " ");\n'
               "        System.out.println();\n"
               "        int mode = 0;\n"
               "        for (int v = 1; v < 10; v++) {\n"
               "            if (freq[v] > freq[mode]) mode = v;\n"
               "        }\n"
               '        System.out.println("mode=" + mode);'),
         "        int[] rev = Arrays.copyOf(a, n);\n"
         "        int i = 0;\n"
         "        int j = n - 1;\n"
         "        while (i < j) {\n"
         "            int t = rev[i]; rev[i] = rev[j]; rev[j] = t;\n"
         "            i++;\n"
         "            j--;\n"
         "        }\n"
         '        System.out.println("reversed=" + Arrays.toString(rev));\n'
         "        int[] rot = new int[n];\n"
         "        for (int p = 0; p < n; p++) rot[p] = a[(p + k) % n];\n"
         '        System.out.println("rotated=" + Arrays.toString(rot));\n'
         "        int[] freq = new int[10];\n"
         "        for (int p = 0; p < n; p++) freq[a[p]]++;\n"
         '        System.out.print("freq=");\n'
         '        for (int v = 0; v < 10; v++) System.out.print(freq[v] + " ");\n'
         "        System.out.println();\n"
         "        int mode = 0;\n"
         "        for (int v = 1; v < 10; v++) {\n"
         "            if (freq[v] > freq[mode]) mode = v;\n"
         "        }\n"
         '        System.out.println("mode=" + mode);',
         [_akcase(a, k, _m4_workbench(a, k))
          for (a, k) in (([1, 3, 3, 7], 2), ([1, 3, 3, 7], 0), ([1, 3, 3, 7], 6),
                         ([5], 3), ([0, 0, 9, 9, 1], 4), ([2, 7, 1, 8, 2, 8], 3))],
         hints=["Reverse a COPY (`Arrays.copyOf(a, n)`), or the rotation will use reversed "
                "data.",
                "The rotation reads `a[(p + k) % n]` — the `% n` is what survives k >= n.",
                "The counting array is `new int[10]`, incremented as `freq[a[p]]++`.",
                'For the `freq=` line, print the label with `System.out.print`, then the ten '
                "counts, then a bare `System.out.println()`.",
                "`mode` is an argmax over `freq`, scanning values upward with strict `>` so "
                "ties go to the smaller value."]),
    example_io="stdin:  4\n        1 3 3 7\n        2\n\n"
               "stdout: reversed=[7, 3, 3, 1]\n        rotated=[3, 7, 1, 3]\n"
               "        freq=0 1 0 2 0 0 0 1 0 0\n        mode=3",
    rubric=[
        "`reversed` uses a copy, so `rotated` still sees the original order.",
        "The reversal loop stops at the crossing point — no double-swapping.",
        "`rotated` is a LEFT rotation and survives `k` greater than or equal to `n`.",
        "`freq` prints exactly ten counts, in value order 0 through 9.",
        "`mode` breaks ties toward the smaller value.",
        "It survives a one-element array and `k = 0`.",
    ],
)


_MODULES.append(_jmod(
    4, 1, "Arrays, deeply",
    "Rearranging and counting",
    "Reverse, rotate, count and deduplicate — the named interview questions, plus "
    "the one new idea that powers half of them: an array indexed by value instead "
    "of by position.",
    """
Everything here is a question you will be asked by name: "reverse an array in
place", "rotate by k", "find the duplicate", "find the missing number". They
are short enough to write in five minutes and subtle enough that the boundaries
are where people fail.

The genuinely new idea is the **counting array** — using a value as an index.
It is the O(n) answer to a whole family of questions, and doing it with a bare
`int[]` first is what makes `HashMap` obviously useful later rather than
magical.
""",
    _M4,
    capstone=_M4_CAP,
    objectives=[
        "Reverse an array in place with two pointers, and say why the bound is `n / 2`.",
        "Rotate left or right with a second array, and state why `% n` belongs where it does.",
        "Rotate in place with the three-reversal trick, in O(1) extra space.",
        "Build a counting array, handle negative values with an offset, and find the mode.",
        "Give three duplicate-detection strategies with their time/space trade-offs.",
        "Compact unique values into the front of a sorted array with a write pointer.",
        "Solve missing/repeating with the sum trick, the XOR trick, and a counting array — and say when each fails.",
    ],
    why="These are the questions that come up by name in screens and phone rounds. They "
        "also carry the two patterns module 5 is built on: two pointers walking toward "
        "each other, and an index that means something other than 'position'.",
    est_minutes=330,
    glossary=[
        _jg("in place", "Rearranging the original array with O(1) extra memory, rather than "
                        "building a new one."),
        _jg("two pointers", "Two indices moving through one array under a shared rule — "
                            "toward each other for reversal, or as read/write positions for "
                            "compaction."),
        _jg("rotation", "Shifting every element by k positions with wraparound. Rotating by "
                        "`n` is the identity, so only `k % n` matters."),
        _jg("counting array", "An `int[]` whose INDEX is a data value and whose slot is a "
                              "count. O(n) counting at the cost of one slot per possible "
                              "value."),
        _jg("offset", "A constant added to a value to make it a valid index — `freq[x + 5]` "
                      "for values from -5 upward."),
        _jg("mode", "The most frequently occurring value. An argmax over the counting array."),
        _jg("counting sort", "Emitting each value `freq[v]` times, in index order. Reading a "
                             "counting array back is already half of it."),
        _jg("write pointer", "In compaction, the index of the next slot to fill — usually "
                             "called `k`, and always behind or level with the read index."),
        _jg("XOR trick", "Using `v ^ v == 0` to cancel matched values so an unmatched one "
                         "survives. Cannot overflow, unlike the sum trick."),
    ],
    cheatsheet="""
```java
// --- reverse in place (two pointers) -----------------------------------
int i = 0, j = n - 1;
while (i < j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }

for (int i = 0; i < n / 2; i++) {          // same thing; n/2 or it no-ops
    int t = a[i]; a[i] = a[n-1-i]; a[n-1-i] = t;
}

// --- rotate with a second array ----------------------------------------
for (int i = 0; i < n; i++) b[i] = a[(i + k) % n];      // LEFT  by k
for (int i = 0; i < n; i++) b[(i + k) % n] = a[i];      // RIGHT by k

// --- rotate RIGHT in place, O(1) space ---------------------------------
k = k % n;                                  // required: raw indices below
reverse(0, n - 1);  reverse(0, k - 1);  reverse(k, n - 1);

// --- counting array ----------------------------------------------------
int[] freq = new int[10];                   // values 0..9
for (int i = 0; i < n; i++) freq[a[i]]++;   // the VALUE is the index

int[] freq = new int[11];                   // values -5..5
for (int i = 0; i < n; i++) freq[a[i] + 5]++;

int mode = 0;                               // smallest value wins a tie
for (int v = 1; v < freq.length; v++) if (freq[v] > freq[mode]) mode = v;

// --- duplicates ---------------------------------------------------------
for (int i = 0; i < n; i++)                 // brute force  O(n^2) / O(1)
    for (int j = i + 1; j < n; j++) ...     // j = i + 1, never 0

Arrays.sort(a);                             // sort first   O(n log n) / O(1)
for (int i = 1; i < n; i++) if (a[i] == a[i-1]) ...

// counting array                            //              O(n) / O(range)

// --- compact unique values (sorted input) ------------------------------
int k = 1;
for (int i = 1; i < n; i++)
    if (a[i] != a[k - 1]) { a[k] = a[i]; k++; }
// a[0..k-1] is the answer; a[k..] is stale

// --- missing value from 1..n+1 -----------------------------------------
long expected = (long)(n + 1) * (n + 2) / 2;         // long guards overflow
int x = 0;                                            // or XOR: no overflow
for (int i = 0; i < n; i++) x ^= a[i];
for (int v = 1; v <= n + 1; v++) x ^= v;
```
""",
    self_check=[
        "Can you write an in-place reversal and explain why `i <= j` and `i < n` are both wrong?",
        "Can you write left and right rotation and say why one modulus is on the source and the other on the destination?",
        "Can you do the three-reversal rotation without looking, including the `k % n`?",
        "Can you explain `freq[a[i]]++` to someone who has only ever indexed by position?",
        "Can you handle a counting array for values from -100 to 100?",
        "Can you name three ways to detect duplicates, with time and space for each?",
        "Can you say why the sum trick alone cannot find a missing AND a repeated value?",
    ],
    review=[
        _jq("An in-place reversal loop running to `i < n` instead of `i < n / 2` produces…",
            ["the original array", "the reversed array", "an exception", "a half-reversed array"],
            0,
            "Every pair is swapped twice, so each swap is undone. Same silent no-op as "
            "module 2's in-place transpose with the wrong inner bound."),
        _jq("Values range from -1000 to 1000. What size counting array, and what index expression?",
            ["new int[2001], freq[x + 1000]++",
             "new int[1000], freq[x]++",
             "new int[2000], freq[x]++",
             "A counting array cannot handle negatives"],
            0,
            "2001 distinct values from -1000 to 1000 inclusive, with an offset of 1000 "
            "mapping the smallest onto index 0."),
        _jq("You must detect duplicates without modifying the array and without extra memory. Which approach?",
            ["Brute-force pair comparison, O(n²) time",
             "Sort it first",
             "Use a counting array",
             "It is impossible"],
            0,
            "Sorting modifies the array and a counting array costs memory, so the O(n²) scan "
            "is the only one that fits both constraints. Naming the constraint that forces "
            "the choice is the point."),
        _jq("`{1, 1, 2, 3, 3}` after in-place duplicate removal. What is k, and what is a[3]?",
            ["k = 3, and a[3] is stale leftover data",
             "k = 3, and a[3] is 0",
             "k = 5, and a[3] is 3",
             "k = 2, and a[3] is 3"],
            0,
            "Three unique values are compacted into indices 0..2. The array is still length "
            "5; slots 3 and 4 keep whatever the shifting left behind."),
    ],
    milestone="You can reverse, rotate, count, deduplicate and hunt missing values — the "
              "whole family of named array questions — and you have the counting array in "
              "your toolkit, which is the O(n) answer to more questions than any other trick "
              "in this course.",
))
