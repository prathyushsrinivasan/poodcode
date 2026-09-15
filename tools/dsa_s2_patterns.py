# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 2 — Cost, and the four patterns that beat it.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# This is the hinge of the whole curriculum. Stage 1 wrote correct code without
# ever asking what it cost; from here on, "it works" is only half an answer.
# The stage opens with Big-O because the four techniques that follow — hashing,
# two pointers, sliding window, prefix sums — are all answers to the SAME
# question: how do I stop re-reading data I have already seen?
#
# That framing is deliberate. Taught as four separate tricks they are four
# things to memorise; taught as four ways to reuse work they are one idea, and
# the signal table in each unit is how you pick between them.
# ---------------------------------------------------------------------------

_S2 = _stage(
    "patterns", "Cost & Core Patterns", "⚡",
    "Stop re-reading what you have already seen.",
    """
Every technique in this stage removes a nested loop, and each removes it a
different way:

| Pattern | The work it reuses |
| --- | --- |
| **Hashing** | *“Have I seen this value?”* — answered in O(1) instead of a scan |
| **Two pointers** | Sorted order, so neither pointer ever needs to go back |
| **Sliding window** | The previous window's answer, adjusted at both ends |
| **Prefix sums** | Every range sum, precomputed once |

Learn to recognise which one a prompt is asking for and the Medium tier stops
looking like a different sport from the Easy tier. That recognition is the
skill; the code is four short templates you will have memorised by the end of
the stage.
""")


# --- Unit 5 — Complexity ----------------------------------------------------

_unit(
    "complexity", "Cost: Big-O in Practice", "⏱️", _S2,
    "Count the work before you write it, and know when n² is fine.",
    weight=2,
    prereqs=["arrays-first-pass"],
    why="""
Every problem you have solved so far was small enough that nothing you wrote
could be too slow. That ends here. From this unit on, the interesting question
is never *"does it work?"* but *"does it work at n = 200,000?"* — and the answer
has to be decidable **before** you type, because a wrong choice of approach is
not something you can patch afterwards.

Big-O gets taught as a maths topic. It is really a *budgeting* topic: you are
given a constraint, you have roughly 10⁸ simple operations to spend, and the
constraint tells you which shapes of solution fit.
""",
    model="""
### Read the constraint, pick the shape

A rough but reliable table. Take the largest `n` in the constraints and read
off what you can afford:

| n up to | Budget allows | Typical approach |
| --- | --- | --- |
| 10–12 | O(n!) | Permutations, brute force |
| 20–25 | O(2ⁿ) | Subsets, bitmask DP |
| 500 | O(n³) | Triple loop, Floyd–Warshall |
| 5,000 | O(n²) | Every pair, 2-D DP |
| 10⁵–10⁶ | O(n log n) | Sort, heap, binary search |
| 10⁶–10⁷ | O(n) | One pass, hashing, two pointers |
| 10⁹+ | O(log n) or O(1) | Binary search on the answer, a formula |

Read it backwards too, and it becomes a *hint*: a constraint of `n ≤ 20` is the
setter telling you an exponential search is intended. A constraint of `n ≤ 10⁵`
is them telling you O(n²) will time out.

### Counting the work

Big-O keeps the fastest-growing term and drops constants, because at large n
nothing else matters:

- **Sequential** code adds: O(n) then O(n) is O(n). Two passes are still linear.
- **Nested** code multiplies: a loop inside a loop over the same data is O(n²).
- **Halving** is logarithmic: each step throws away half the remaining input, so
  it finishes in about log₂ n steps — 20 for a million, 30 for a billion.
- **A call inside a loop counts.** `list.contains(x)` inside a `for` is O(n²),
  and it is the most common accidental quadratic there is, because the nesting
  is hidden behind a method name.

### Space

Same counting, applied to memory you allocate. An extra array is O(n); a fixed
26-slot counter is O(1). Recursion costs stack depth even when it allocates
nothing — a recursion n deep is O(n) space.

### When O(n²) is the right answer

When n is small, when the quadratic version is obviously correct and the linear
one is delicate, or when you need a baseline to test the fast one against.
"Optimal" is defined by the constraints, not by pride.
""",
    signals=[
        _sig("`n ≤ 20`", "Exponential search (subsets, permutations)",
             "The constraint is a hint that nothing polynomial is expected."),
        _sig("`n ≤ 5,000`", "O(n²) is fine",
             "Do the simple thing; a clever linear solution is wasted effort."),
        _sig("`n ≤ 10⁵` or more", "O(n log n) at worst",
             "Quadratic will time out. Sort, hash or two-pointer it."),
        _sig("Values up to 10⁹ but few of them", "Binary search or a formula",
             "Cost tracks the count of items, not the size of the numbers."),
        _sig("A `.contains()` or `indexOf` inside a loop", "Hash it instead",
             "The hidden inner scan makes an innocent-looking loop quadratic."),
    ],
    skeletons=[
        _sk("The accidental quadratic",
            "Recognise this shape — it is the single most common performance bug.",
            """
// O(n²): contains() scans the whole list on every iteration
for (int x : a) {
    if (seenList.contains(x)) { ... }
    seenList.add(x);
}

// O(n): the same logic, with a hash set
Set<Integer> seen = new HashSet<>();
for (int x : a) {
    if (!seen.add(x)) { ... }   // add returns false if already present
}
""",
            "`Set.add` returning `false` is the idiomatic “I have seen this before”."),
        _sk("Counting sort / frequency array",
            "When the values are small integers or letters, counting beats sorting.",
            """
int[] freq = new int[26];               // O(1) space — 26 is a constant
for (char c : s.toCharArray()) freq[c - 'a']++;
""",
            "O(n) time, O(1) space. The alphabet is a constant, however big it feels."),
    ],
    costs=[
        _cost("O(1)", "constant", "—", "Array index, hash lookup, arithmetic."),
        _cost("O(log n)", "~20 steps at n = 10⁶", "—", "Binary search, heap push/pop, tree descent."),
        _cost("O(n)", "10⁶ is instant", "—", "A pass. The floor for anything that must read all input."),
        _cost("O(n log n)", "10⁶ is comfortable", "—", "Sorting. The usual cost of imposing order."),
        _cost("O(n²)", "10⁴ is fine, 10⁵ is not", "—", "Every pair. Check the constraint first."),
        _cost("O(2ⁿ)", "n ≤ 25", "—", "Every subset. Only viable because n is tiny."),
    ],
    pitfalls=[
        _pit("“Time limit exceeded” on the large test only",
             "The approach is a tier too slow — usually a hidden inner scan.",
             "Count the loops, including the ones inside library calls, then re-read the constraint."),
        _pit("Optimising code that was never the bottleneck",
             "Constant-factor tinkering inside an O(n²) algorithm.",
             "Change the shape, not the constant. O(n log n) beats a tuned O(n²) at any interesting n."),
        _pit("`String` concatenation in a loop is mysteriously slow",
             "`s += x` allocates a whole new string each time, making the loop O(n²) in "
             "total characters.",
             "Accumulate with `StringBuilder` and call `toString()` once."),
        _pit("Claiming O(n) for something that sorts",
             "Sorting is O(n log n); a single call can dominate everything around it.",
             "State the complexity of every library call you make, not just your loops."),
    ],
    lessons=["big_o", "alg_big_o", "alg_analyzing", "alg_space"],
    checks=[
        _chk("A problem says `1 ≤ n ≤ 200000`. Is an O(n²) solution acceptable?",
             "No — that is 4×10¹⁰ operations. The constraint is telling you to find an "
             "O(n log n) or O(n) approach."),
        _chk("Why is `for (x : a) if (list.contains(x))` quadratic?",
             "`contains` on a list is itself a linear scan, so the loop nests one O(n) "
             "operation inside another. A `HashSet` makes the inner step O(1)."),
        _chk("Are two sequential O(n) passes worse than one?",
             "Not in Big-O — O(n) + O(n) = O(n). Only the constant factor differs, and "
             "clarity usually wins that trade."),
        _chk("What is the space complexity of a recursion that goes n levels deep and "
             "allocates nothing?",
             "O(n) — every pending call keeps a frame on the stack. Deep recursion is a "
             "memory cost even when it looks free."),
        _chk("`n ≤ 22` and the problem asks for every possible selection. What does that hint?",
             "That 2ⁿ ≈ 4 million is the intended cost — enumerate the subsets, and do not "
             "hunt for a polynomial trick that probably does not exist."),
    ],
    interview="""
"What is the time and space complexity?" is asked in essentially every
interview, and the high-scoring version of the answer has three parts: the
complexity, *why* (the loops that produce it), and whether it is optimal
*given the constraints*. Volunteering the third part — "this is O(n log n)
because of the sort; O(n) is possible with counting since the values are
bounded" — is what separates a pass from a strong pass.
""",
    rungs=[
        _rung("Core", "Feel the difference between a quadratic and a linear solution on the same problem.",
              ["second-largest", "count-above-average", "count-equal-pairs"],
              {"second-largest": "Solvable by sorting (O(n log n)) or by two accumulators (O(n)). Write both and compare.",
               "count-above-average": "The two-pass solution people try to avoid. It is still O(n) — that is the lesson.",
               "count-equal-pairs": "Every pair is O(n²); counting occurrences first makes it O(n). The gap here is the whole unit in one problem."}),
    ],
    next_up="""
`count-equal-pairs` became linear by *counting what it had seen*. Generalise
that and you have the most useful data structure in interview programming.
""",
)


# --- Unit 6 — Hashing -------------------------------------------------------

_unit(
    "hashing", "Hashing: Trade Space for Time", "🗝️", _S2,
    "“Have I seen this?” in O(1), and everything that follows from it.",
    weight=3,
    prereqs=["arrays-first-pass", "complexity"],
    why="""
The commonest reason code is quadratic is that it searches. *For each element,
look through the rest* is two nested loops, and the inner one is almost always
asking a question a hash table can answer instantly: **have I seen this value,
and if so, where or how often?**

Hashing is the single highest-return pattern in this curriculum. It turns a
whole tier of O(n²) solutions into O(n) with a few lines, and the cost is memory
— which is nearly always the right trade.
""",
    model="""
### Three structures, three questions

| You need to know | Use | Cost |
| --- | --- | --- |
| *Have I seen x?* | `HashSet<T>` | O(1) add / contains |
| *How many times have I seen x?* | `HashMap<T, Integer>` | O(1) get / put |
| *Where did I see x?* | `HashMap<T, Integer>` value = index | O(1) |

All three are the same structure underneath. Choosing is just naming what the
value means.

### The complement trick

Two-sum is the archetype, and it generalises: **as you scan, ask whether the
partner you need has already gone past.**

```java
for (int i = 0; i < n; i++) {
    int need = target - a[i];
    if (seen.containsKey(need)) return new int[]{ seen.get(need), i };
    seen.put(a[i], i);          // AFTER the check, never before
}
```

Checking before inserting is what stops an element pairing with itself. That one
line ordering is the whole difference between right and wrong.

### Canonical forms

*Group the anagrams* is the same question as *are these equal?* once you can
reduce each item to a **canonical form** — a representative that is identical
for everything in a group. Sorted letters (`"eat"` → `"aet"`) is one; a
26-length count signature is another, and is O(n) rather than O(n log n).

The pattern is worth naming because it is how you hash something that is not
already a key: reduce it to something equal-when-equivalent, then hash *that*.

### Counting when the keys are small

If the keys are letters or small integers, an `int[]` beats a `HashMap` on every
axis — no boxing, no hashing, cache friendly:

```java
int[] freq = new int[26];
freq[c - 'a']++;
```

Reach for the map only when the key space is large or not an integer.
""",
    signals=[
        _sig("“does it contain a duplicate?”", "`HashSet`",
             "`add` returning false *is* the duplicate test."),
        _sig("“two numbers that sum to target”", "Complement map",
             "Look for `target - x` among what you have already passed."),
        _sig("“group / anagram / same letters”", "Canonical key → `HashMap<String, …>`",
             "Sorted letters or a count signature makes equivalent items share a key."),
        _sig("“most frequent”, “appears more than n/2 times”", "Frequency map",
             "Count in one pass, decide in a second."),
        _sig("“longest consecutive sequence”", "`HashSet` + start detection",
             "Membership tests replace sorting; only extend from a run's first element."),
        _sig("Keys are letters or values ≤ a few thousand", "`int[]` counter",
             "Same algorithm without boxing, hashing or allocation."),
    ],
    skeletons=[
        _sk("Seen-set",
            "Duplicates, first repeat, membership.",
            """
Set<Integer> seen = new HashSet<>();
for (int x : a) {
    if (!seen.add(x)) {         // false ⇒ x was already there
        return true;
    }
}
return false;
""",
            "`add` reports novelty and inserts in one operation — no separate `contains`."),
        _sk("Complement lookup",
            "Two-sum and every variation of “find the partner”.",
            """
Map<Integer, Integer> seen = new HashMap<>();   // value → index
for (int i = 0; i < a.length; i++) {
    Integer j = seen.get(target - a[i]);
    if (j != null) return new int[]{ j, i };
    seen.put(a[i], i);
}
""",
            "Check, then insert. Inserting first lets an element pair with itself."),
        _sk("Frequency map",
            "Counting, majority, top-k, anagram checks.",
            """
Map<Integer, Integer> freq = new HashMap<>();
for (int x : a) freq.merge(x, 1, Integer::sum);
""",
            "`merge` replaces the `getOrDefault(x, 0) + 1` dance."),
        _sk("Canonical key",
            "Grouping items that are equivalent under some transformation.",
            """
Map<String, Integer> groups = new HashMap<>();
for (String w : words) {
    char[] c = w.toCharArray();
    Arrays.sort(c);                       // the canonical form
    groups.merge(new String(c), 1, Integer::sum);
}
""",
            "A 26-int count signature is the O(n) alternative to sorting each word."),
        _sk("Longest consecutive run",
            "Sequence problems where sorting would be too slow.",
            """
Set<Integer> set = new HashSet<>(list);
int best = 0;
for (int x : set) {
    if (set.contains(x - 1)) continue;    // only start from a run's first value
    int len = 1;
    while (set.contains(x + len)) len++;
    best = Math.max(best, len);
}
""",
            "The `continue` is what keeps it O(n): each run is walked exactly once."),
    ],
    costs=[
        _cost("`HashMap` / `HashSet` get, put, contains", "O(1) average", "O(n)",
              "Worst case O(n) on adversarial keys; not a concern for these problems."),
        _cost("Building a frequency map", "O(n)", "O(k)", "k = number of distinct keys."),
        _cost("`int[]` counter", "O(n)", "O(1)", "When the key space is a fixed alphabet."),
        _cost("Sorting-based grouping", "O(n · m log m)", "O(n · m)",
              "m = item length. The count-signature version drops the log."),
    ],
    pitfalls=[
        _pit("Two-sum returns the same index twice",
             "The current element was inserted into the map before the complement check.",
             "Always check first, insert afterwards."),
        _pit("`map.get(k)` throws a `NullPointerException`",
             "A missing key returns `null`, which unboxes to an NPE when assigned to `int`.",
             "`map.getOrDefault(k, 0)`, or hold the result in an `Integer` and test for null."),
        _pit("Counting with `HashMap` is unexpectedly slow",
             "Boxing every `int` into an `Integer` allocates on the hot path.",
             "When keys are bounded and small, use an `int[]` instead."),
        _pit("Objects that should be equal end up in different buckets",
             "A custom key class overrides `equals` but not `hashCode`.",
             "Override both, or use an already-hashable canonical form such as a `String`."),
        _pit("Longest-consecutive degrades to O(n²)",
             "Every element walks its whole run, instead of only run starts doing so.",
             "Skip any `x` where `x - 1` is present."),
    ],
    lessons=["hashing", "complement", "canonical", "visited_set"],
    checks=[
        _chk("Why check the map before inserting the current element in two-sum?",
             "Otherwise `target - a[i] == a[i]` finds the element itself and reports a pair "
             "of one element with itself."),
        _chk("When is `int[26]` better than `HashMap<Character, Integer>`?",
             "Whenever the keys are a fixed small alphabet: no boxing, no hashing, better "
             "cache behaviour, and O(1) space by definition."),
        _chk("Longest-consecutive uses a set and still claims O(n). How?",
             "Each run is walked only from its smallest element — guarded by "
             "`if (set.contains(x - 1)) continue;` — so every value is visited a constant "
             "number of times overall."),
        _chk("What makes a good canonical key for grouping anagrams?",
             "Anything identical for equivalent items: sorted characters (O(m log m)) or a "
             "26-slot count signature rendered as a string (O(m))."),
        _chk("What is the worst-case complexity of a `HashMap` lookup, and why is it "
             "acceptable?",
             "O(n) if every key collides. With well-distributed hashes it is O(1) average, "
             "and Java's map switches long buckets to trees, capping it at O(log n)."),
    ],
    interview="""
Hashing is the expected answer often enough that the interesting follow-up is
always *"now do it without extra space"*. That is your cue to look for sorting,
two pointers, or an in-place marking trick — and to say out loud what you are
giving up: sorting costs O(n log n), and marking usually destroys the input.
""",
    internals="""
### What `HashMap` actually is

A **bucket array**, plus a rule for turning a key into an index into it.

```
hash = key.hashCode()
hash ^= (hash >>> 16)          // spread the high bits down
index = hash & (table.length - 1)   // cheap modulo, because length is a power of 2
```

Each bucket holds the entries whose keys landed on that index — a **collision**.
Java keeps them in a short linked list, and once a single bucket reaches **8**
entries (with a table of at least 64) it converts that list into a red-black
tree, so a pathological bucket degrades to O(log k) rather than O(k). That is
the entire reason `get` can be called O(1) with a straight face: the average
bucket is tiny, and the worst bucket is bounded.

### Load factor, and why the cost is *amortised*

`HashMap` grows when `size > capacity × 0.75`. Growing means allocating a table
of twice the length and re-indexing **every** entry, because the index depends
on `table.length`. That single insert costs O(n).

Spread over the n inserts that led to it, the cost per insert is still O(1) —
the same amortisation argument as `ArrayList` growth. It is worth being able to
say out loud, because "insert is O(1)" is false about *that* insert and true
about the sequence.

If you know the final size, `new HashMap<>(expectedSize / 0.75f + 1)` skips the
resizes entirely. Rarely decisive, occasionally the difference between passing
and timing out on 10⁶ insertions.

### What `HashMap` does *not* promise

**Any order at all.** Not insertion order, not key order, and not a stable
order across runs or across JDK versions. Code that iterates a `HashMap` and
prints is code whose output is not specified, and the judge compares text — so
this is a correctness bug, not a style one.

When order matters, say which order you mean:

| You want | Use |
|---|---|
| insertion order | `LinkedHashMap` |
| sorted by key | `TreeMap` — O(log n) per op, not O(1) |
| no order, fastest | `HashMap` |

### `hashCode` and `equals` are a pair

Two keys that are `equals` **must** have the same `hashCode`, or the map will
store both and find neither reliably. Java's `Integer`, `Long`, `String` and
`List` all honour this. A custom key class that overrides `equals` and forgets
`hashCode` is the classic silent bug — and an `int[]` used as a key is the same
bug with no override in sight, because arrays hash by identity. Use a
`List<Integer>` or a joined string instead.
""",
    rungs=[
        _rung("Warm up", "One set, one question: have I seen this before?",
              ["contains-duplicate", "two-sum-exists"],
              {"contains-duplicate": "Try it with a nested loop first, then with a set, and time both mentally against n = 10⁵."}),
        _rung("Core", "The complement trick and the frequency map.",
              ["two-sum-fn", "two-sum-indices", "two-sum-any", "valid-anagram", "first-unique-char"],
              {"two-sum-indices": "The canonical interview problem. You should be able to type this from memory.",
               "valid-anagram": "Counting beats sorting here — and the `int[26]` version is the one to remember."}),
        _rung("Variations", "Canonical keys, and counts used for a decision.",
              ["majority-element", "group-anagrams-count"],
              {"majority-element": "Counting solves it in O(n) space; look up Boyer–Moore afterwards for the O(1) version."}),
        _rung("Stretch", "A set used for membership instead of for duplicates.",
              ["longest-consecutive"],
              {"longest-consecutive": "Sorting makes it easy and O(n log n). The set version is O(n) — and the `continue` is the entire trick."}),
    ],
    next_up="""
Hashing buys speed with memory. The next unit buys it with **order** — and
spends no memory at all.
""",
)


# --- Unit 7 — Two pointers --------------------------------------------------

_unit(
    "two-pointers", "Two Pointers", "↔️", _S2,
    "When the data is sorted, neither index ever needs to go back.",
    weight=3,
    prereqs=["arrays-first-pass"],
    why="""
Hashing costs O(n) memory. When the array is **sorted** — or can be — you can
often get the same O(n) time for O(1) space, because sortedness tells you which
direction to move. That is the whole idea: each comparison rules out a whole
range, so a pointer never has to revisit anything.

It is also the answer to the interviewer's favourite follow-up, *"can you do it
without the hash map?"*.
""",
    model="""
### Two arrangements

**Converging** — one pointer at each end, walking inward:

```java
int l = 0, r = n - 1;
while (l < r) {
    if (good(a[l], a[r])) return ...;
    else if (tooSmall) l++;
    else r--;
}
```

Correct because of an *invariant*: at every step the answer, if it exists, lies
between `l` and `r`. When the sum is too small, no pair using `a[l]` can work —
`a[l]` is already paired with the largest remaining value — so discarding it
loses nothing. Being able to state that sentence is the difference between
knowing the pattern and having memorised it.

**Same direction** — a `read` pointer that always advances and a `write`
pointer that only advances when something is kept:

```java
int write = 0;
for (int read = 0; read < n; read++) {
    if (keep(a[read])) a[write++] = a[read];
}
```

This is how every in-place filter, dedupe and compaction works, and it is
exactly the shape of `move-zeroes`.

### Reversal and palindromes

Swapping inward from both ends reverses in place in O(1) space; comparing
inward instead of swapping tests a palindrome. Same skeleton, one line changed.

### When the array is *not* sorted

You may sort it first — if the problem does not depend on original positions.
That is the trade: O(n log n) time for O(1) extra space. If indices must be
preserved, hashing is the right tool and two pointers is not.
""",
    signals=[
        _sig("“sorted array” + “find a pair”", "Converging pointers",
             "Sortedness makes each comparison discard one end."),
        _sig("“in place”, “without extra space”", "Read/write pointers",
             "Compaction needs no buffer, only a second index."),
        _sig("“reverse”, “is it a palindrome?”", "Swap or compare from both ends",
             "One skeleton, two uses."),
        _sig("“container”, “two lines”, “max area”", "Converging with a greedy move",
             "Move the limiting side; the other cannot improve while it is the bottleneck."),
        _sig("“merge two sorted …”", "One pointer per input",
             "Compare heads, take the smaller, advance that pointer."),
        _sig("Indices in the ORIGINAL order matter", "Hashing, not two pointers",
             "Sorting destroys the positions the answer is expressed in."),
    ],
    skeletons=[
        _sk("Converging pair search",
            "Two-sum on a sorted array, closest pair, container problems.",
            """
int l = 0, r = a.length - 1;
while (l < r) {
    int sum = a[l] + a[r];
    if (sum == target) return new int[]{ l, r };
    if (sum < target) l++;      // need bigger: only the left can grow
    else               r--;     // need smaller: only the right can shrink
}
""",
            "Say the invariant out loud: “if a pair exists, it is inside [l, r]”."),
        _sk("Read / write compaction",
            "Move zeroes, remove duplicates, filter in place.",
            """
int write = 0;
for (int read = 0; read < a.length; read++) {
    if (a[read] != 0) a[write++] = a[read];
}
while (write < a.length) a[write++] = 0;    // pad the tail
""",
            "`write` only advances on a keep, so it never overtakes `read`."),
        _sk("Reverse / palindrome in place",
            "Reversal, palindrome checks, rotation building blocks.",
            """
int l = 0, r = s.length - 1;
while (l < r) {
    char t = s[l]; s[l] = s[r]; s[r] = t;   // swap → reverse
    // or: if (s[l] != s[r]) return false;  // compare → palindrome
    l++; r--;
}
""",
            "`l < r` not `l <= r`: the middle element needs no partner."),
        _sk("Merge two sorted inputs",
            "Merging arrays or lists; the merge step of merge sort.",
            """
int i = 0, j = 0, k = 0;
while (i < n && j < m) out[k++] = (a[i] <= b[j]) ? a[i++] : b[j++];
while (i < n) out[k++] = a[i++];
while (j < m) out[k++] = b[j++];
""",
            "The two tail loops are not optional — exactly one of them runs."),
    ],
    costs=[
        _cost("Converging scan", "O(n)", "O(1)", "Each step retires one element."),
        _cost("Sort, then two pointers", "O(n log n)", "O(1)", "The sort dominates."),
        _cost("Hashing alternative", "O(n)", "O(n)", "Faster asymptotically; costs memory and keeps indices."),
        _cost("Merging two sorted inputs", "O(n + m)", "O(n + m)", "O(1) extra if merged in place from the back."),
    ],
    pitfalls=[
        _pit("Infinite loop",
             "A branch that advances neither pointer — usually a missing `l++` in an "
             "equality case.",
             "Every branch of the `while` must move at least one pointer."),
        _pit("The middle element is processed twice",
             "`while (l <= r)` in a swap or compare loop.",
             "Use `l < r`; a single middle element is already in place."),
        _pit("The answer's indices are wrong",
             "The array was sorted, which moved every element away from its original index.",
             "If positions matter, hash instead — or sort (value, index) pairs."),
        _pit("Compaction overwrites data it still needs",
             "`write` was advanced on every iteration rather than only on a keep.",
             "Increment `write` inside the `if`, never in the loop header."),
        _pit("Container-of-water moves the wrong side",
             "Advancing the taller line; the area is limited by the shorter one.",
             "Always move the shorter side — it is the only one that can improve."),
    ],
    lessons=["two_pointers", "alg_two_pointers", "inplace_reverse", "char_arrays"],
    checks=[
        _chk("Why is it safe to discard `a[l]` when `a[l] + a[r] < target`?",
             "Because `a[r]` is the largest value left: if `a[l]` cannot reach the target "
             "even with it, it cannot reach it with anything smaller."),
        _chk("Two pointers versus a hash map for two-sum — which and when?",
             "Sorted input or a no-extra-space requirement → two pointers (O(1) space). "
             "Unsorted input where the original indices are the answer → hashing."),
        _chk("In `move-zeroes`, why can `write` never overtake `read`?",
             "`write` advances only when an element is kept, and `read` advances every "
             "iteration, so `write ≤ read` always holds."),
        _chk("Why move the shorter line in the container problem?",
             "The area is `min(height) × width`. Narrowing loses width, so the only way to "
             "gain is a taller minimum — impossible while the short side stays."),
    ],
    interview="""
Two pointers is the canonical *"optimise it"* answer, and the points are in the
justification, not the code. Interviewers listen for the invariant — "if a
solution exists it lies within the window, and this comparison proves the
element I am dropping cannot be part of one". Say that and the follow-up
usually stops.
""",
    rungs=[
        _rung("Warm up", "One skeleton, walked from both ends.",
              ["reverse-string", "reverse-array-fn", "is-palindrome-fn"],
              {"reverse-string": "The swap loop. `l < r`, not `l <= r`."}),
        _rung("Core", "Convergence with a decision rule, and same-direction compaction.",
              ["move-zeroes", "two-sum-sorted", "merge-sorted-arrays"],
              {"two-sum-sorted": "Compare directly with `two-sum-indices` from the hashing unit — same question, opposite trade.",
               "merge-sorted-arrays": "Try merging from the back once you have it working forwards; that is the O(1)-space version."}),
        _rung("Variations", "A greedy convergence whose correctness needs an argument.",
              ["container-most-water"],
              {"container-most-water": "Write down why moving the shorter side is safe before you code it."}),
        _rung("Stretch", "The hardest thing two pointers do: two invariants at once.",
              ["trapping-rain-water"],
              {"trapping-rain-water": "Do it with two prefix-max arrays first (easier, O(n) space), then collapse it to two pointers."}),
    ],
    next_up="""
Converging pointers handle *pairs*. When the question is about a **contiguous
run** instead, the two pointers move the same way — and that is a window.
""",
)


# --- Unit 8 — Sliding window ------------------------------------------------

_unit(
    "sliding-window", "Sliding Window", "🪟", _S2,
    "Every contiguous-subarray question, in one pass.",
    weight=3,
    prereqs=["two-pointers", "hashing"],
    why="""
*"The longest substring with …"*, *"the smallest subarray such that …"*,
*"every window of size k"* — these all look like they need to examine every
subarray, which is O(n²) starts times O(n) work. They do not. Because the
windows overlap almost completely, the answer for one window is the answer for
the last one with **one element added and maybe a few removed**.

That reuse is the whole technique, and it turns a cubic brute force into a
single pass.
""",
    model="""
### The one template

```java
int l = 0;
for (int r = 0; r < n; r++) {
    add(a[r]);                       // extend the window to the right
    while (windowIsInvalid()) {
        remove(a[l++]);              // shrink from the left until it is valid again
    }
    best = Math.max(best, r - l + 1);   // every window here is valid
}
```

Four things to fill in, and they are the whole design:

1. **What state does the window carry?** A count, a sum, a frequency map.
2. **What makes it invalid?** A duplicate, a sum over the limit, too many
   distinct values.
3. **When is the answer recorded?** After shrinking, for a *longest* question;
   inside the shrink loop, for a *shortest* one.
4. **Can the left pointer ever move backwards?** If yes, this is not a sliding
   window.

### Why it is O(n), not O(n²)

The `while` inside the `for` looks quadratic but is not: `l` only ever
increases, and it can increase at most n times in total across the whole run.
That argument — *amortised, because each element enters and leaves the window
exactly once* — is the one to say aloud in an interview.

### Fixed versus variable windows

**Fixed size k**: no `while`. Add the entering element, remove the leaving one,
record after the window is full.

```java
for (int r = 0; r < n; r++) {
    sum += a[r];
    if (r >= k) sum -= a[r - k];
    if (r >= k - 1) best = Math.max(best, sum);
}
```

**Variable size**: the `while` shrinks until valid. Longest asks for the biggest
valid window; shortest asks for the smallest, and records inside the shrink.

### The limit

Sliding window needs the property that **extending can only make things worse
and shrinking can only make them better** (monotonicity). With negative numbers
in a sum problem that breaks — adding an element can *reduce* the sum — and the
technique is simply wrong. That is when prefix sums with a hash map take over.
""",
    signals=[
        _sig("“contiguous”, “substring”, “subarray”", "A window",
             "Contiguity is the precondition — a subsequence is a different problem."),
        _sig("“longest … such that”", "Expand always, shrink while invalid, record after",
             "The answer is the largest window that is still valid."),
        _sig("“shortest / minimum window such that”", "Record inside the shrink loop",
             "You want the smallest valid window, found as you contract."),
        _sig("“every window of size k”, “average of k”", "Fixed window",
             "Add one, remove one; no `while` needed."),
        _sig("“at most k distinct / k replacements”", "Map or counter as window state",
             "The constraint is the invalidity test."),
        _sig("“maximum / minimum of every window of size k”", "A monotonic deque",
             "The window is easy; keeping its extreme in O(1) needs the queues unit."),
        _sig("Contiguous sums with NEGATIVE values", "Prefix sums + hash map",
             "Growing a window can shrink the sum, so shrinking is not monotone."),
    ],
    skeletons=[
        _sk("Variable window — longest",
            "Longest substring without repeats, longest with at most k distinct.",
            """
Map<Character, Integer> count = new HashMap<>();
int l = 0, best = 0;
for (int r = 0; r < s.length(); r++) {
    count.merge(s.charAt(r), 1, Integer::sum);
    while (count.get(s.charAt(r)) > 1) {          // invalid: a duplicate
        char c = s.charAt(l++);
        if (count.merge(c, -1, Integer::sum) == 0) count.remove(c);
    }
    best = Math.max(best, r - l + 1);
}
""",
            "Record AFTER the shrink — inside it the window is still invalid."),
        _sk("Variable window — shortest",
            "Minimum window substring, smallest subarray with sum ≥ target.",
            """
int l = 0, best = Integer.MAX_VALUE;
for (int r = 0; r < n; r++) {
    add(a[r]);
    while (valid()) {                     // note: shrink while VALID
        best = Math.min(best, r - l + 1);
        remove(a[l++]);
    }
}
""",
            "The mirror image of the longest template: the loop condition flips."),
        _sk("Fixed window of size k",
            "Rolling averages, maximum sum of k consecutive elements.",
            """
long sum = 0, best = Long.MIN_VALUE;
for (int r = 0; r < n; r++) {
    sum += a[r];
    if (r >= k) sum -= a[r - k];          // the element leaving
    if (r >= k - 1) best = Math.max(best, sum);
}
""",
            "Off-by-one central: `r >= k` removes, `r >= k - 1` records."),
    ],
    costs=[
        _cost("Variable window", "O(n)", "O(k)",
              "Each element enters and leaves once — amortised, despite the nested `while`."),
        _cost("Fixed window", "O(n)", "O(1)", "Pure add-one / remove-one."),
        _cost("Window with a frequency map", "O(n)", "O(alphabet)",
              "O(1) space when the alphabet is fixed, e.g. `int[128]`."),
        _cost("Brute force over all subarrays", "O(n²) or O(n³)", "O(1)",
              "What the window replaces."),
    ],
    pitfalls=[
        _pit("The answer is one too large or one too small",
             "Window length is `r - l + 1`, not `r - l`.",
             "Check it on a single-element window: `l == r` must give 1."),
        _pit("The longest answer includes an invalid window",
             "`best` was updated before the shrink loop ran.",
             "For *longest*, record after shrinking; for *shortest*, record inside."),
        _pit("The map keeps keys with a count of zero",
             "Decrementing without removing leaves stale keys, so `map.size()` "
             "over-reports the distinct count.",
             "Remove the key when its count hits 0, or compare counts rather than sizes."),
        _pit("Infinite loop in the shrink",
             "`l` is not incremented on some path inside the `while`.",
             "The shrink body must always advance `l`."),
        _pit("Correct on positives, wrong with negative numbers",
             "Sliding window assumes growth is monotone; negatives break that.",
             "Switch to prefix sums with a hash map of earlier prefix values."),
    ],
    lessons=["sliding_window", "alg_sliding_window"],
    checks=[
        _chk("Why is the nested `while` still O(n) overall?",
             "`l` never decreases and is bounded by n, so across the entire run the shrink "
             "loop executes at most n times in total. Each element enters and leaves once."),
        _chk("Where do you record the answer for *longest* versus *shortest*?",
             "Longest: after the shrink, when the window is valid again. Shortest: inside "
             "the shrink, while it is still valid and getting smaller."),
        _chk("Why does a sliding window fail for “subarray summing to k” with negatives?",
             "Extending the window can decrease the sum, so there is no monotone "
             "invalidity test to shrink on. Prefix sums plus a hash map handle it."),
        _chk("What is the window length when `l == r`?",
             "One — `r - l + 1`. Getting this wrong is the most common off-by-one in the "
             "whole pattern."),
    ],
    interview="""
This pattern is asked by name, and the follow-up is always the complexity of
the nested loop. "O(n), because the left pointer only moves forward and each
element enters and leaves the window exactly once" is the answer being fished
for. Then be ready for *"what if there are negative numbers?"* — the honest
answer is that the window breaks and prefix sums take over.
""",
    rungs=[
        _rung("Warm up", "The slide itself, with nothing else attached.",
              ["fixed-window-max-sum", "window-covering-letters"],
              {"fixed-window-max-sum": "The fixed window: add what entered, subtract what left. Two reads per step no matter how wide `k` is.",
               "window-covering-letters": "The variable right edge, with the left edge nailed to 0 — so the only new idea is maintaining a summary of what the window holds."}),
        _rung("Core", "The four window shapes — longest valid, shortest valid, and count them all.",
              ["longest-unique-substring", "longest-k-distinct", "min-window-sum-atleast",
               "subarray-sum-at-most"],
              {"longest-unique-substring": "The template problem. Type it from memory, then check where you recorded `best`.",
               "longest-k-distinct": "Grow, then repair: extend the right edge unconditionally and shrink only to restore the invariant. Remove zero counts from the map or `size()` stops meaning anything.",
               "min-window-sum-atleast": "The mirror image — shrink while the window is *still valid*, and record inside the shrink. Getting this pair backwards is the unit's most common bug.",
               "subarray-sum-at-most": "Counting all valid windows rather than finding one, which is the shape people never think to look for: `r - left + 1` per step."}),
        _rung("Variations", "A construction problem that turns out to be a window with a budget.",
              ["longest-ones-k-flips"],
              {"longest-ones-k-flips": "Nothing in the code decides *which* zeros to flip — the budget becomes the window invariant and the choices disappear. That reframing is the skill."}),
        _rung("Stretch", "A window whose validity test needs two counters.",
              ["min-window-length"],
              {"min-window-length": "The *shortest* variant, so the answer is recorded inside the shrink. Track “how many required characters are satisfied” as a single int rather than comparing whole maps."}),
    ],
    next_up="""
Windows handle contiguous runs you can grow and shrink. When the ranges are
arbitrary — or the values can be negative — you precompute instead.
""",
)


# --- Unit 9 — Prefix sums ---------------------------------------------------

_unit(
    "prefix-sums", "Prefix Sums", "➕", _S2,
    "Precompute once, answer any range in O(1).",
    weight=2,
    prereqs=["arrays-first-pass", "hashing"],
    why="""
Answering *"what is the sum of `a[l..r]`?"* by looping costs O(n), and a problem
that asks it many times is quietly quadratic. One preprocessing pass fixes it
permanently: store the running total, and every range sum becomes a single
subtraction.

The pattern then generalises past sums in two directions that are worth far more
than the base case: **prefix + hash map** solves subarray-sum counting with
negative numbers (where sliding window fails), and the same difference trick
run over a timeline is how every *"how many are active at once?"* problem is
solved.
""",
    model="""
### The identity

With `pre[i]` = sum of the first `i` elements (`pre[0] = 0`):

```
sum(a[l..r]) = pre[r + 1] − pre[l]
```

The `+1` offset and `pre[0] = 0` exist so that ranges starting at index 0 need
no special case. Use an array of size `n + 1`; the off-by-ones disappear.

### Prefix + hash map

*"How many subarrays sum to k?"* becomes a **complement** question about prefix
values: a subarray ending at `r` sums to k exactly when some earlier prefix
equals `pre[r] − k`. So count prefix values as you go:

```java
Map<Long, Integer> seen = new HashMap<>();
seen.put(0L, 1);                    // the empty prefix
long run = 0; int count = 0;
for (int x : a) {
    run += x;
    count += seen.getOrDefault(run - k, 0);
    seen.merge(run, 1, Integer::sum);
}
```

`seen.put(0L, 1)` before the loop is what lets a subarray starting at index 0 be
counted. Forgetting it is the classic bug.

This works with negative numbers, which is exactly where sliding window gave up.

### Prefix products

Product-except-self is the same idea in two directions: a prefix product from
the left and a suffix product from the right, multiplied at each index. It
avoids division, which matters because the array may contain zeros.

### Difference arrays and sweeps

To apply *"add v to every index in [l, r]"* many times, do not touch the range.
Record `diff[l] += v` and `diff[r + 1] -= v`, then take the prefix sum once at
the end: k updates become O(k + n) instead of O(k · n).

The same idea run over events (`+1` at a start, `−1` at an end, processed in
time order) answers *"the maximum number of things active at once"* — which is
the whole intervals unit in embryo.
""",
    signals=[
        _sig("“sum of the range l..r”, many queries", "Prefix array",
             "One pass up front, then O(1) per query."),
        _sig("“how many subarrays sum to k” with negatives", "Prefix + hash map",
             "Sliding window is invalid; prefix complements are not."),
        _sig("“product of all except self”, no division", "Prefix and suffix products",
             "Two passes, no division, survives zeros."),
        _sig("“add v to a range”, repeated", "Difference array",
             "Mark the endpoints, prefix-sum once at the end."),
        _sig("“maximum simultaneous …”, boarding and leaving", "Sweep of ±1 events",
             "The running total at any moment is the answer."),
        _sig("Running total requested per index", "Prefix array is literally the answer",
             "No subtraction needed."),
    ],
    skeletons=[
        _sk("Build and query",
            "Repeated range-sum questions.",
            """
long[] pre = new long[n + 1];
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];

// sum of a[l..r] inclusive:
long s = pre[r + 1] - pre[l];
""",
            "Size `n + 1` with `pre[0] = 0` removes every special case."),
        _sk("Count subarrays with a given sum",
            "Works with negative values, where a window cannot.",
            """
Map<Long, Integer> seen = new HashMap<>();
seen.put(0L, 1);                       // empty prefix — do not omit
long run = 0; int count = 0;
for (int x : a) {
    run += x;
    count += seen.getOrDefault(run - k, 0);
    seen.merge(run, 1, Integer::sum);
}
""",
            "The complement trick from the hashing unit, applied to prefixes."),
        _sk("Prefix × suffix",
            "Product (or max, or gcd) of everything except index i.",
            """
int[] res = new int[n];
int pre = 1;
for (int i = 0; i < n; i++) { res[i] = pre; pre *= a[i]; }
int suf = 1;
for (int i = n - 1; i >= 0; i--) { res[i] *= suf; suf *= a[i]; }
""",
            "No division, so a zero anywhere in the array is handled for free."),
        _sk("Difference array / sweep",
            "Many range updates, or “how many are active at once”.",
            """
int[] diff = new int[n + 1];
for (int[] u : updates) { diff[u[0]] += u[2]; diff[u[1] + 1] -= u[2]; }
int cur = 0, best = 0;
for (int i = 0; i < n; i++) { cur += diff[i]; best = Math.max(best, cur); }
""",
            "`diff[r + 1]` is why the array has n + 1 slots."),
    ],
    costs=[
        _cost("Build prefix array", "O(n)", "O(n)", "One pass."),
        _cost("Range-sum query", "O(1)", "—", "A single subtraction."),
        _cost("Prefix + hash map counting", "O(n)", "O(n)", "One pass, one map."),
        _cost("k range updates via difference array", "O(k + n)", "O(n)",
              "Versus O(k · n) if each range is touched directly."),
        _cost("Naive repeated range sums", "O(q · n)", "O(1)", "What the prefix replaces."),
    ],
    pitfalls=[
        _pit("Every range sum is off by one element",
             "The `pre[r + 1] - pre[l]` offset was written as `pre[r] - pre[l]`.",
             "Verify on a length-1 range: `sum(a[i..i])` must equal `a[i]`."),
        _pit("Subarrays starting at index 0 are never counted",
             "`seen.put(0, 1)` was omitted before the loop.",
             "Seed the map with the empty prefix."),
        _pit("The prefix sums overflow",
             "n values near 10⁹ sum well past `int` range even though each fits.",
             "Make the prefix array `long[]`."),
        _pit("Product-except-self breaks on zeros",
             "The solution divided the total product by `a[i]`.",
             "Use prefix × suffix products and never divide."),
        _pit("The sweep is one index short",
             "`diff` was allocated with n slots, so `diff[r + 1]` is out of bounds for the "
             "last range.",
             "Allocate `n + 1`."),
    ],
    lessons=["prefix_sum", "alg_prefix_sums"],
    checks=[
        _chk("Why does the prefix array have n + 1 entries?",
             "So `pre[0] = 0` represents the empty prefix, which makes ranges starting at "
             "index 0 obey the same formula as every other range."),
        _chk("Why seed the map with `(0 → 1)` when counting subarrays with sum k?",
             "A subarray that starts at index 0 needs the *empty* prefix as its left "
             "endpoint. Without the seed, every such subarray is missed."),
        _chk("Subarray sum = k, with negative numbers. Window or prefix?",
             "Prefix plus a hash map. The window relies on growth being monotone, and "
             "negatives break that assumption."),
        _chk("Why avoid division in product-except-self?",
             "A single zero makes division undefined, and two zeros make every answer zero. "
             "Prefix × suffix handles both without a special case."),
    ],
    interview="""
Prefix sums are rarely the headline of a question — they are the step that makes
the headline tractable, which is why interviewers like them. The tell you are
expected to show is recognising that *"many range queries"* or *"count the
subarrays"* means preprocessing, and being able to say why the hash-map variant
survives negative numbers when a sliding window does not.
""",
    rungs=[
        _rung("Warm up", "The running total, and a sweep over events.",
              ["running-sum", "bank-balance"],
              {"running-sum": "The prefix array is literally the required output."}),
        _rung("Core", "Two-directional prefixes, and the ±1 sweep.",
              ["product-except-self", "max-passengers"],
              {"product-except-self": "Solve it without division. That constraint is the entire problem.",
               "max-passengers": "A +1/−1 sweep. The same shape returns in the intervals unit as “minimum meeting rooms”."}),
        _rung("Stretch", "Prefix values as hash keys.",
              ["subarray-sum-k"],
              {"subarray-sum-k": "The hashing unit's complement trick, applied to prefix sums. Seed the map with 0 → 1."}),
    ],
    next_up="""
The array patterns are in place. Next, the same reasoning applied to text —
where the data structure is the same but the operations have their own costs.
""",
)


# --- Unit 10 — Strings ------------------------------------------------------

_unit(
    "strings", "Strings & Character Work", "🔤", _S2,
    "An array of characters, with an immutability tax.",
    weight=3,
    prereqs=["arrays-first-pass", "hashing"],
    why="""
Strings are arrays of characters, so every pattern in this stage applies
unchanged. What is new is **cost**: in Java a `String` is immutable, so every
`+=` allocates a whole new one. A loop that builds a string with `+=` is O(n²)
in total characters, and it is the most common accidental quadratic after
`list.contains`.

The other new thing is that characters are numbers. `c - 'a'` gives 0…25, which
turns letters into array indices — the trick behind every counting solution in
this unit.
""",
    model="""
### The costs that matter

| Operation | Cost | Note |
| --- | --- | --- |
| `charAt(i)` | O(1) | It is an array read |
| `length()` | O(1) | Stored, not counted |
| `substring(i, j)` | O(j − i) | **Copies** — it is not a view |
| `s + t` | O(\\|s\\| + \\|t\\|) | Allocates a new string every time |
| `StringBuilder.append` | O(1) amortised | The right tool for building |
| `equals` | O(n) | Compares content; `==` compares identity |

`substring` copying is why a naive *"check every substring"* loop is O(n³)
rather than O(n²) — the copy hides inside the comparison.

### Characters are numbers

```java
int idx = c - 'a';                    // 'a'..'z' → 0..25
char back = (char) ('a' + idx);
boolean isDigit = c >= '0' && c <= '9';
```

That mapping gives you an O(1)-space frequency table for any lowercase problem —
`int[26]` — which is faster and clearer than a `HashMap<Character, Integer>`.

### Building output

```java
StringBuilder sb = new StringBuilder();
for (...) sb.append(x);
System.out.println(sb);
```

Build once, print once. Printing inside a loop with `println` is also slow, for
the same underlying reason — each call flushes.

### Canonical forms, again

Anagrams, case-insensitive comparison and "ignore punctuation" are all the same
move: reduce each string to a canonical form and compare *those*. That is the
hashing unit's idea, and text is where it earns its keep.
""",
    signals=[
        _sig("“count the …” over characters", "`int[26]` or `int[128]` frequency array",
             "Letters are indices; no map needed."),
        _sig("“build the result string”", "`StringBuilder`",
             "`+=` in a loop is quadratic."),
        _sig("“is it a palindrome?”", "Two pointers over `charAt`",
             "No copying, O(1) space."),
        _sig("“same letters”, “anagram”", "Sorted characters or a count signature",
             "Canonical form, then compare or hash."),
        _sig("“run-length”, “consecutive equal characters”", "One pass with a run counter",
             "Extend-or-reset, from the arrays unit."),
        _sig("“words”, “split on spaces”", "One pass counting transitions, or `split`",
             "Beware of repeated and leading spaces when counting manually."),
    ],
    skeletons=[
        _sk("Character frequency",
            "Anagrams, unique characters, counting letters.",
            """
int[] freq = new int[26];
for (char c : s.toCharArray()) freq[c - 'a']++;
""",
            "Use `int[128]` when the input is not guaranteed lowercase ASCII letters."),
        _sk("Build with StringBuilder",
            "Any output longer than a single value.",
            """
StringBuilder sb = new StringBuilder();
for (int i = 0; i < n; i++) {
    sb.append(part(i));
    if (i + 1 < n) sb.append(' ');
}
System.out.println(sb);
""",
            "One allocation, one print — instead of n of each."),
        _sk("Run-length scan",
            "Compression, longest run of a character, grouping neighbours.",
            """
for (int i = 0; i < s.length(); ) {
    int j = i;
    while (j < s.length() && s.charAt(j) == s.charAt(i)) j++;
    sb.append(s.charAt(i)).append(j - i);   // the run [i, j)
    i = j;
}
""",
            "The outer `for` has no increment — the inner loop is what advances `i`."),
        _sk("Vertical scan for a common prefix",
            "Longest common prefix across many strings.",
            """
for (int i = 0; i < first.length(); i++) {
    char c = first.charAt(i);
    for (String w : words)
        if (i == w.length() || w.charAt(i) != c)
            return first.substring(0, i);
}
return first;
""",
            "Compare column by column; stop at the first disagreement."),
    ],
    costs=[
        _cost("One pass over characters", "O(n)", "O(1)", "With an `int[26]` counter."),
        _cost("Sorting a string's characters", "O(n log n)", "O(n)",
              "The canonical form for anagram grouping — count signatures are O(n)."),
        _cost("Building with `+=` in a loop", "O(n²)", "O(n²) churn", "The bug. Use `StringBuilder`."),
        _cost("`substring(i, j)`", "O(j − i)", "O(j − i)", "A copy, not a view."),
    ],
    pitfalls=[
        _pit("String building is inexplicably slow on large input",
             "`s += x` inside a loop allocates and copies the whole string each iteration.",
             "Use `StringBuilder` and convert once at the end."),
        _pit("`ArrayIndexOutOfBoundsException` in a frequency array",
             "`c - 'a'` on an uppercase letter, a digit or a space gives a negative or "
             "out-of-range index.",
             "Use `int[128]` indexed by the raw char, or normalise the case first."),
        _pit("Two identical-looking strings compare as different",
             "`==` compares references. Literals may be interned, which makes it work "
             "sometimes — the worst possible failure mode.",
             "Always `equals`."),
        _pit("The word count is one too high",
             "Splitting on a single space counts empty tokens from repeated or leading spaces.",
             "Count transitions from space to non-space, or split on `\\s+` after trimming."),
        _pit("A substring comparison loop is O(n³)",
             "Each `substring` call copies before the comparison even starts.",
             "Compare with `charAt` in place, or use indices rather than copies."),
    ],
    lessons=["string_basics", "canonical", "char_arrays"],
    checks=[
        _chk("Why is `result += c` inside a loop O(n²)?",
             "`String` is immutable, so each `+=` allocates a new string and copies "
             "everything built so far. Summed over n iterations that is quadratic."),
        _chk("What does `c - 'a'` give you, and when is it wrong?",
             "The 0-based index of a lowercase letter. It is wrong — silently negative or "
             "too large — for uppercase letters, digits, spaces or punctuation."),
        _chk("Is `s.substring(i, j)` O(1)?",
             "No. Modern Java copies the range, so it is O(j − i). A loop of substrings is "
             "a hidden extra factor of n."),
        _chk("Two ways to test whether two words are anagrams — and their costs?",
             "Sort both and compare: O(n log n). Count characters into `int[26]` and compare "
             "the tables: O(n). The second is preferred and also generalises to grouping."),
    ],
    interview="""
String questions are rarely about strings — they are array questions wearing a
costume, plus one Java-specific trap the interviewer is watching for. Reaching
for `StringBuilder` unprompted, and saying "`substring` copies, so I will
compare in place", both register as production instincts rather than
competitive-programming ones.
""",
    rungs=[
        _rung("Warm up", "Count characters; build output properly.",
              ["count-vowels", "count-words", "password-strength"],
              {"count-words": "Decide what two consecutive spaces mean before you code — that is the bug."}),
        _rung("Core", "A pass that transforms rather than counts.",
              ["caesar-cipher", "max-nesting-depth", "run-length-encode"],
              {"caesar-cipher": "Modular arithmetic on `c - 'a'`; watch the wrap and the non-letters.",
               "run-length-encode": "The run scan, with `StringBuilder` for the output."}),
        _rung("Variations", "Comparing many strings at once.",
              ["longest-common-prefix", "longest-common-prefix-strs"],
              {"longest-common-prefix": "Vertical scan, column by column — no substring copies needed."}),
    ],
    next_up="""
That is the pattern toolkit for linear data. The next stage adds **order** —
sorting and binary search — and the number-theory and bit tricks that sit
beside them.
""",
)
