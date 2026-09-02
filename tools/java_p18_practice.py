# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 18 practice - sets and maps.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[18]`.
#
# OUTPUT STABILITY, enforced throughout: no exercise ever prints a HashSet or a
# HashMap directly, because neither specifies an iteration order. Anything
# printed as a collection is a LinkedHashSet/LinkedHashMap (insertion order) or
# a TreeSet/TreeMap (sorted). HashSet and HashMap appear only where the output
# is order-free - a size, a boolean, a single lookup.
#
# Comparators and Collections.* are module 20, so nothing here sorts explicitly;
# where sorted output is wanted, a TreeSet or TreeMap provides it.
# ---------------------------------------------------------------------------


_RD_W18 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")


def _p18ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_W18):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


def _w18(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _w18k(ws, k, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(k)]), out)


def _jset(xs):
    return "[" + ", ".join(xs) + "]"


def _jmap(pairs):
    return "{" + ", ".join(f"{k}={v}" for (k, v) in pairs) + "}"


def _firstseen(ws):
    out = []
    for w in ws:
        if w not in out:
            out.append(w)
    return out


_WS18 = (["a", "b", "a"], ["solo"], ["x", "x", "x"], ["c", "b", "a"],
         ["dog", "cat", "ant", "cat"])


# --- Family A - membership ----------------------------------------------------

_P18_A = _jfam(
    "p18-membership", "Sets for membership",
    "The O(1) answer to 'have I seen this'.",
    """
```java
Set<String> seen = new HashSet<>();
seen.add("a");                 // returns TRUE only if the set changed
seen.contains("a");            // O(1)
seen.size();                   // duplicates were never stored
```

A `Set` holds each element at most once and has no positions. The reason to
reach for one is almost always **`contains`**: O(1) on a `HashSet` against O(n)
on a list. Replacing a `list.contains(x)` inside a loop with a set is the single
most common performance fix in everyday Java, and it turns O(n²) into O(n).

**`add` returns a boolean**, and it replaces the whole check-then-add dance:

```java
if (seen.add(word)) { ... }        // runs for the FIRST occurrence only
```

Reading it as *"was this new?"* makes a lot of code shorter.

**Elements must honour `hashCode` and `equals` together.** A hash structure
locates by hash and confirms with equals, so overriding one without the other
means the set can hold two equal objects — or lose one you just added.
`String` and `Integer` already do this correctly.

**Never print a `HashSet`.** Its iteration order is unspecified and can change
between JDK versions. Every exercise in this family prints only order-free
things — a count, a boolean, a single word — which is exactly when a `HashSet`
is the right choice.
""",
    [
        _p18ex("j18-pr-distinct", "How many different?", "Intro",
               "Print how many distinct words there are.",
               """
        Set<String> seen = new HashSet<>();
        for (String w : words) {
            seen.add(w);
        }
        System.out.println(seen.size());
""",
               [_w18(ws, len(set(ws))) for ws in _WS18],
               ["Adding a duplicate is silently ignored, so the size IS the distinct "
                "count.",
                "Declare the variable as `Set<String>` and construct a `HashSet`.",
                "Only the size is printed — a HashSet's order must never be relied "
                "on.",
                "No `if` is needed; `add` already handles duplicates."]),

        _p18ex("j18-pr-firsttime", "React the first time only", "Easy",
               "Print each word the first time it appears, and nothing on repeats.",
               """
        Set<String> seen = new HashSet<>();
        for (String w : words) {
            if (seen.add(w)) {
                System.out.println(w);
            }
        }
""",
               [_w18(ws, _nl(*_firstseen(ws))) for ws in _WS18],
               ["`add` returns `true` only when the element was not already there.",
                "So the whole test is the call itself: `if (seen.add(w))`.",
                "`if (!seen.contains(w)) { seen.add(w); ... }` also works but does "
                "the lookup twice.",
                "The output order is the INPUT order, because you print as you go — "
                "not the set's order."]),

        _p18ex("j18-pr-hasdupe", "Any repeats at all?", "Easy",
               "Print `true` if any word appears more than once, `false` otherwise.",
               """
        Set<String> seen = new HashSet<>();
        boolean dupe = false;
        for (String w : words) {
            if (!seen.add(w)) {
                dupe = true;
            }
        }
        System.out.println(dupe);
""",
               [_w18(ws, _jbool(len(set(ws)) != len(ws))) for ws in _WS18],
               ["`add` returning `false` means the word was already present.",
                "So `!seen.add(w)` reads as 'this is a repeat'.",
                "A flag that starts `false` and is only raised.",
                "Comparing `seen.size()` with `n` at the end would work too."]),

        _p18ex("j18-pr-lookup", "Is it known?", "Easy",
               "Read the words, then one more. Print `yes` if it is among them, `no` "
               "otherwise.",
               """
        String q = sc.next();
        Set<String> known = new HashSet<>(words);
        if (known.contains(q)) {
            System.out.println("yes");
        } else {
            System.out.println("no");
        }
""",
               [_case("\n".join([str(len(ws)), " ".join(ws), q]),
                      "yes" if q in ws else "no")
                for (ws, q) in ((["a", "b"], "a"), (["solo"], "other"),
                                (["x", "x"], "x"), (["p", "q"], "z"),
                                (["dog", "cat"], "cat"))],
               ["Every set has a constructor taking another collection, so building "
                "from the list is one line.",
                "`new HashSet<>(words)`",
                "`contains` is O(1) here against O(n) on the list.",
                "Only `yes` or `no` is printed, so the set's order never matters."]),

        _p18ex("j18-pr-common", "In both groups", "Medium",
               "Read two groups of words. Print how many distinct words appear in "
               "BOTH.",
               """
        int m = sc.nextInt();
        Set<String> other = new HashSet<>();
        for (int i = 0; i < m; i++) {
            other.add(sc.next());
        }
        Set<String> first = new HashSet<>(words);
        first.retainAll(other);
        System.out.println(first.size());
""",
               [_case("\n".join([str(len(a)), " ".join(a), str(len(b)), " ".join(b)]),
                      len(set(a) & set(b)))
                for (a, b) in ((["a", "b", "c"], ["b", "c", "d"]),
                               (["x"], ["y"]),
                               (["p", "q"], ["q", "p"]),
                               (["dog", "cat"], ["cat"]),
                               (["a", "a", "b"], ["b", "b"]))],
               ["`retainAll` keeps only the elements also in the other collection — "
                "set intersection, in place.",
                "It MODIFIES the set it is called on, so build a set from the first "
                "group and shrink that.",
                "Only the size is printed, so a HashSet is safe.",
                "Its siblings are `addAll` (union) and `removeAll` (difference)."]),
    ])


# --- Family B - order ----------------------------------------------------------

_P18_B = _jfam(
    "p18-order", "Choosing the order",
    "Three implementations, three guarantees.",
    """
| Implementation | Iteration order | add / contains |
|---|---|---|
| `HashSet` | **none specified** | O(1) |
| `LinkedHashSet` | insertion order | O(1) |
| `TreeSet` | **sorted** | O(log n) |

All three implement `Set`, so only the constructor changes.

**`HashSet` is the default** — fastest, smallest, and usually you do not care.
**`LinkedHashSet`** threads a linked list through the entries so iteration
follows first-insertion order; it costs a little memory and buys reproducibility,
which matters for anything printed, logged or tested. **`TreeSet`** keeps
elements sorted at O(log n) per operation — you are paying for the ordering.

**Converting is one constructor call**, and that is the standard way to sort the
contents of a hash-based set:

```java
Set<String> sorted = new TreeSet<>(anyOtherSet);
```

**A repeat does not move an element in a `LinkedHashSet`.** Re-adding something
already present is a no-op, so it keeps its original position. That is the
difference between "first seen" and "last seen" order, and it catches people.

> A `HashSet` of a few short strings often *happens* to come out sorted. That is
> exactly why relying on it is dangerous rather than safe: it works on your
> machine and fails on someone else's.
""",
    [
        _p18ex("j18-pr-sorted", "Sorted, for free", "Intro",
               "Print the distinct words in alphabetical order, as a set.",
               """
        Set<String> sorted = new TreeSet<>(words);
        System.out.println(sorted);
""",
               [_w18(ws, _jset(sorted(set(ws)))) for ws in _WS18],
               ["A `TreeSet` iterates in sorted order, so no sorting step is needed.",
                "Its constructor accepts the list directly.",
                "`String` has a natural ordering built in.",
                "Duplicates still collapse, because it is still a `Set`."]),

        _p18ex("j18-pr-insertion", "In the order they arrived", "Easy",
               "Print the distinct words in the order they were FIRST seen, as a set.",
               """
        Set<String> seen = new LinkedHashSet<>(words);
        System.out.println(seen);
""",
               [_w18(ws, _jset(_firstseen(ws))) for ws in _WS18],
               ["`LinkedHashSet` guarantees insertion order.",
                "Case four is `c b a`, which a TreeSet would print as `[a, b, c]` — "
                "so this variant tells the two apart.",
                "A repeated word keeps its ORIGINAL position; re-adding does not move "
                "it to the end.",
                "That is why case one prints `[a, b]` and not `[b, a]`."]),

        _p18ex("j18-pr-convert", "Sort a hash set", "Easy",
               "Collect the words in a `HashSet` (for speed), then print them sorted by "
               "converting to a `TreeSet`.",
               """
        Set<String> fast = new HashSet<>(words);
        Set<String> ordered = new TreeSet<>(fast);
        System.out.println(ordered);
""",
               [_w18(ws, _jset(sorted(set(ws)))) for ws in _WS18],
               ["Build with the fast implementation, print with the ordered one.",
                "Converting is a single constructor call.",
                "Printing `fast` directly would give an order you must not rely on.",
                "This is the standard idiom for 'I used a HashSet and now I need "
                "ordered output'."]),

        _p18ex("j18-pr-firstlast", "Ends of a sorted set", "Medium",
               "Print the alphabetically first distinct word, then the last.",
               """
        TreeSet<String> sorted = new TreeSet<>(words);
        System.out.println(sorted.first());
        System.out.println(sorted.last());
""",
               [_w18(ws, _nl(sorted(set(ws))[0], sorted(set(ws))[-1]))
                for ws in _WS18],
               ["`first()` and `last()` are on `TreeSet`, not on `Set` — so declare "
                "the variable as `TreeSet<String>` here rather than the interface.",
                "That is a legitimate exception to 'program to the interface': you "
                "are using capabilities the interface does not have.",
                "A one-word input gives the same answer twice.",
                "Both are O(log n), not a scan."]),

        _p18ex("j18-pr-difference", "Only in the first", "Medium",
               "Read two groups. Print, sorted, the distinct words that appear in the "
               "first group but not the second.",
               """
        int m = sc.nextInt();
        Set<String> other = new HashSet<>();
        for (int i = 0; i < m; i++) {
            other.add(sc.next());
        }
        Set<String> only = new TreeSet<>(words);
        only.removeAll(other);
        System.out.println(only);
""",
               [_case("\n".join([str(len(a)), " ".join(a), str(len(b)), " ".join(b)]),
                      _jset(sorted(set(a) - set(b))))
                for (a, b) in ((["a", "b", "c"], ["b"]),
                               (["x"], ["x"]),
                               (["p", "q"], ["z"]),
                               (["dog", "cat", "ant"], ["cat", "dog"]),
                               (["a", "a", "b"], ["b"]))],
               ["`removeAll` deletes every element also present in the other "
                "collection — set difference, in place.",
                "Build the first group as a `TreeSet` so the result prints sorted.",
                "The second group can stay a `HashSet`; it is only ever queried.",
                "Case two removes everything and prints `[]`."]),
    ])


# --- Family C - maps -----------------------------------------------------------

_P18_C = _jfam(
    "p18-map", "Maps: lookup and counting",
    "The frequency idiom, and the null that catches you.",
    """
```java
Map<String, Integer> ages = new HashMap<>();
ages.put("Ada", 36);          // returns the PREVIOUS value, or null
ages.get("Ada");              // 36
ages.get("Nobody");           // null  <-- the trap
ages.getOrDefault("Nobody", 0);
ages.containsKey("Ada");
```

**`get` returns `null` for an absent key**, and unboxing that explodes:

```java
int n = ages.get("Nobody");   // NullPointerException
```

`getOrDefault` exists precisely to avoid it, and it is what makes the counting
idiom a one-liner:

```java
counts.put(w, counts.getOrDefault(w, 0) + 1);
```

Read it as *whatever it was, or zero if new, plus one.* No `if`, no `containsKey`
check, no null. This is module 4's counting array freed from needing small
integer keys and a known range — and it is what maps are used for more than
anything else.

**Keys must honour `hashCode` and `equals`**, exactly as set elements must: a
`HashSet` is a `HashMap` underneath.

**A `Map` is not a `Collection`.** It has no `add`, and you iterate one of its
three views — `keySet()`, `values()`, `entrySet()`.

**`HashMap` has no specified iteration order**, so nothing in this family prints
one directly. Counting into a `HashMap` and querying a single key is perfectly
safe; printing the whole thing is not.
""",
    [
        _p18ex("j18-pr-count-one", "How many times?", "Easy",
               "Read the words, then one more. Print how many times it occurred.",
               """
        String q = sc.next();
        Map<String, Integer> counts = new HashMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        System.out.println(counts.getOrDefault(q, 0));
""",
               [_case("\n".join([str(len(ws)), " ".join(ws), q]), ws.count(q))
                for (ws, q) in ((["a", "b", "a"], "a"), (["solo"], "solo"),
                                (["x", "y"], "z"), (["p", "p", "p"], "p"),
                                (["a", "b", "c"], "b"))],
               ["The counting idiom is `put(w, getOrDefault(w, 0) + 1)`.",
                "Use `getOrDefault` for the final lookup too, so an unseen word gives "
                "`0` rather than throwing.",
                "Only one number is printed, so a HashMap is safe here.",
                "Case three asks about a word that never appeared."]),

        _p18ex("j18-pr-lookup-default", "Look up with a fallback", "Easy",
               "Read `n` name/age pairs, then a name. Print that age, or `-1` if the "
               "name is unknown.",
               """
        int n = sc.nextInt();
        Map<String, Integer> ages = new HashMap<>();
        for (int i = 0; i < n; i++) {
            ages.put(sc.next(), sc.nextInt());
        }
        String who = sc.next();
        System.out.println(ages.getOrDefault(who, -1));
""",
               [_case("\n".join([str(len(rows))]
                                + [f"{k} {v}" for (k, v) in rows] + [q]),
                      dict(rows).get(q, -1))
                for (rows, q) in (([("Ada", 36), ("Bo", 41)], "Ada"),
                                  ([("Ada", 36)], "Nobody"),
                                  ([("x", 0)], "x"),
                                  ([("a", 1), ("b", 2)], "b"),
                                  ([("p", 7)], "q"))],
               ["`ages.get(who)` returns `null` for an unknown name, and assigning "
                "that to an `int` throws.",
                "`getOrDefault(who, -1)` supplies the fallback safely.",
                "Read the query name after all the pairs.",
                "`put` with a repeated key would replace rather than duplicate."],
               read=""),

        _p18ex("j18-pr-previous", "What did it replace?", "Medium",
               "Read `n` key/value pairs. For each, print `new` if the key was absent, "
               "or `was <old>` if it replaced something.",
               """
        int n = sc.nextInt();
        Map<String, Integer> m = new HashMap<>();
        for (int i = 0; i < n; i++) {
            String k = sc.next();
            int v = sc.nextInt();
            Integer old = m.put(k, v);
            if (old == null) {
                System.out.println("new");
            } else {
                System.out.println("was " + old);
            }
        }
""",
               [_case("\n".join([str(len(rows))] + [f"{k} {v}" for (k, v) in rows]),
                      _nl(*[("new" if k not in dict(rows[:i])
                             else "was " + str(dict(rows[:i])[k]))
                            for (i, (k, v)) in enumerate(rows)]))
                for rows in ([("a", 1), ("a", 2)],
                             [("x", 5)],
                             [("p", 1), ("q", 2), ("p", 3)],
                             [("k", 0), ("k", 0)],
                             [("a", 1), ("b", 2)])],
               ["`put` returns the PREVIOUS value for that key, or `null`.",
                "Capture it in an `Integer`, not an `int` — it may be null.",
                "Compare with `== null`; that is the one place `==` is right for a "
                "wrapper.",
                "Case four replaces a value with the same number and must still print "
                "`was 0`."],
               read=""),

        _p18ex("j18-pr-remove-key", "Take one out", "Easy",
               "Read the words and count them, then read one word to remove. Print the "
               "number of distinct words before and after removing it.",
               """
        String q = sc.next();
        Map<String, Integer> counts = new HashMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        System.out.println(counts.size());
        counts.remove(q);
        System.out.println(counts.size());
""",
               [_case("\n".join([str(len(ws)), " ".join(ws), q]),
                      _nl(len(set(ws)), len(set(ws) - {q})))
                for (ws, q) in ((["a", "b", "a"], "a"), (["solo"], "other"),
                                (["x", "y"], "y"), (["p", "p"], "p"),
                                (["a", "b", "c"], "z"))],
               ["`size()` on a map is the number of KEYS.",
                "`remove(k)` deletes the whole entry and returns the old value, which "
                "you can ignore.",
                "Removing a key that is not there changes nothing — cases two and "
                "five.",
                "Only sizes are printed, so a HashMap is fine."]),

        _p18ex("j18-pr-total-values", "Add up the values", "Medium",
               "Read `n` name/score pairs and print the total of all the scores. A "
               "repeated name REPLACES its earlier score rather than adding to it.",
               """
        int n = sc.nextInt();
        Map<String, Integer> scores = new HashMap<>();
        for (int i = 0; i < n; i++) {
            scores.put(sc.next(), sc.nextInt());
        }
        int total = 0;
        for (int v : scores.values()) {
            total += v;
        }
        System.out.println(total);
""",
               [_case("\n".join([str(len(rows))] + [f"{k} {v}" for (k, v) in rows]),
                      sum(dict(rows).values()))
                for rows in ([("a", 1), ("b", 2)],
                             [("x", 5)],
                             [("p", 1), ("p", 9)],
                             [("a", 0), ("b", 0), ("c", 0)],
                             [("m", -3), ("n", 3)])],
               ["`values()` is a view of all the values, iterable with the enhanced "
                "`for`.",
                "`put` with an existing key replaces, so case three totals `9`, not "
                "`10`.",
                "The order of `values()` is unspecified for a HashMap — which does "
                "not matter here, because addition is commutative.",
                "Only the total is printed."],
               read=""),
    ])


# --- Family D - reports --------------------------------------------------------

_P18_D = _jfam(
    "p18-report", "Iterating a map, and reporting",
    "The three views, and why order has to be chosen.",
    """
A `Map` is not a `Collection`, so you iterate one of its **views**:

```java
for (String k : m.keySet())    { ... }              // keys
for (int v : m.values())       { ... }              // values, may repeat
for (Map.Entry<String, Integer> e : m.entrySet()) { // BOTH — the efficient one
    e.getKey(); e.getValue();
}
```

**Prefer `entrySet()` when you need both.** Iterating `keySet()` and calling
`get(k)` inside does a second hash lookup for every entry — correct, but twice
the work for nothing.

Note the element type: **`Map.Entry<K, V>`**, with a dot, because `Entry` is
nested inside `Map`. Both type arguments must be written out.

**A map's `toString` is specified** as `{a=1, b=2}` — braces, `key=value`, comma
and space. Combined with a `TreeMap` that gives fully reproducible output, which
is what these exercises assert on.

**The three flavours mirror the sets exactly:** `HashMap` (no order),
`LinkedHashMap` (insertion), `TreeMap` (sorted by key). Choosing is the same
decision, for the same reasons — and converting is the same one-line constructor
call.

**The views are live.** `keySet()` is not a copy: removing from it removes from
the map, and modifying the map while iterating a view throws
`ConcurrentModificationException`, exactly as with a list.
""",
    [
        _p18ex("j18-pr-report-sorted", "A report in key order", "Intro",
               "Count the words and print the whole map, keys in alphabetical order.",
               """
        Map<String, Integer> counts = new TreeMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        System.out.println(counts);
""",
               [_w18(ws, _jmap([(k, ws.count(k)) for k in sorted(set(ws))]))
                for ws in _WS18],
               ["A `TreeMap` iterates in sorted key order, so no sorting step is "
                "needed.",
                "A map prints as `{key=value, key=value}` with braces.",
                "A `HashMap` here would give output you could not rely on.",
                "The counting idiom is unchanged — only the constructor differs."]),

        _p18ex("j18-pr-entryset", "One pair per line", "Easy",
               "Count the words and print `word=count` on its own line for each, in "
               "alphabetical order, walking `entrySet()`.",
               """
        Map<String, Integer> counts = new TreeMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        for (Map.Entry<String, Integer> e : counts.entrySet()) {
            System.out.println(e.getKey() + "=" + e.getValue());
        }
""",
               [_w18(ws, _nl(*[f"{k}={ws.count(k)}" for k in sorted(set(ws))]))
                for ws in _WS18],
               ["The element type is `Map.Entry<String, Integer>` — note the dot.",
                "`e.getKey()` and `e.getValue()` read the pair with one lookup.",
                "Iterating `keySet()` and calling `get(k)` would do a second hash "
                "lookup per entry.",
                "The map is a `TreeMap`, so the keys arrive sorted."]),

        _p18ex("j18-pr-insertion-report", "In the order first seen", "Medium",
               "Count the words and print `word=count` per line, but in the order each "
               "word was FIRST seen rather than alphabetically.",
               """
        Map<String, Integer> counts = new LinkedHashMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        for (Map.Entry<String, Integer> e : counts.entrySet()) {
            System.out.println(e.getKey() + "=" + e.getValue());
        }
""",
               [_w18(ws, _nl(*[f"{k}={ws.count(k)}" for k in _firstseen(ws)]))
                for ws in _WS18],
               ["`LinkedHashMap` keeps keys in first-insertion order.",
                "Case four is `c b a`, which a TreeMap would report alphabetically — "
                "so this variant tells them apart.",
                "Re-putting an existing key does NOT move it to the end, which is why "
                "the counting idiom does not disturb the order.",
                "Everything else is identical to the sorted version."]),

        _p18ex("j18-pr-keys-values", "Keys, then values", "Easy",
               "Count the words. Print the sorted key set on the first line, then the "
               "total of all the counts on the second.",
               """
        Map<String, Integer> counts = new TreeMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        System.out.println(counts.keySet());
        int total = 0;
        for (int v : counts.values()) {
            total += v;
        }
        System.out.println(total);
""",
               [_w18(ws, _nl(_jset(sorted(set(ws))), len(ws))) for ws in _WS18],
               ["`keySet()` returns a `Set`, so it prints in the bracketed form.",
                "Because the map is a `TreeMap`, that set is sorted.",
                "`values()` is iterable with the enhanced `for`.",
                "The total of all the counts is always the original word count."]),

        _p18ex("j18-pr-most-common", "The most common word", "Hard",
               "Count the words and print the most frequent one and its count, "
               "separated by a space. On a tie, print the alphabetically first.",
               """
        Map<String, Integer> counts = new TreeMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        String bestWord = "";
        int bestCount = -1;
        for (Map.Entry<String, Integer> e : counts.entrySet()) {
            if (e.getValue() > bestCount) {
                bestCount = e.getValue();
                bestWord = e.getKey();
            }
        }
        System.out.println(bestWord + " " + bestCount);
""",
               [_w18(ws, (lambda b: f"{b} {ws.count(b)}")(
                   min(sorted(set(ws)), key=lambda w: -ws.count(w))))
                for ws in _WS18],
               ["Count first, then run module 1's running maximum over the entries.",
                "Because the map is a `TreeMap`, `entrySet()` arrives alphabetically "
                "— so a strict `>` already keeps the first of any tie, with no extra "
                "comparison.",
                "Choosing the right implementation removed the tie-break entirely.",
                "Seed `bestCount` at `-1` so the first entry always wins.",
                "Track BOTH the word and the count."]),
    ])


# --- Family E - putting them together ------------------------------------------

_P18_E = _jfam(
    "p18-combined", "Sets and maps together",
    "The problems these two were made for.",
    """
Most real uses combine them: a **set** to answer *have I seen this*, and a
**map** to answer *how many* or *what is it associated with*.

Three patterns come up constantly:

**Group by a key.** A map whose values are lists:

```java
Map<Character, List<String>> byLetter = new TreeMap<>();
for (String w : words) {
    char c = w.charAt(0);
    if (!byLetter.containsKey(c)) {
        byLetter.put(c, new ArrayList<>());
    }
    byLetter.get(c).add(w);
}
```

(`computeIfAbsent` does this in one line, but it takes a lambda — Part 8.)

**Invert a map.** Values become keys. Watch for collisions: two keys may share a
value, so the inverted map's values usually have to be lists or sets.

**Find the first non-repeating element.** Count in one pass, then walk in
**insertion order** looking for a count of one — which is why `LinkedHashMap`
exists.

The recurring decision is the same one: **what order does the output need?** Get
that into the type and the code stays short. Reach for `HashMap` when nothing is
printed as a collection, `TreeMap` when a sorted report is wanted, and
`LinkedHashMap` when "in the order they arrived" is part of the question.
""",
    [
        _p18ex("j18-pr-first-unique", "First word that never repeats", "Hard",
               "Print the first word that occurs exactly once, or `none` if every word "
               "repeats.",
               """
        Map<String, Integer> counts = new LinkedHashMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        String answer = "none";
        for (Map.Entry<String, Integer> e : counts.entrySet()) {
            if (e.getValue() == 1) {
                answer = e.getKey();
                break;
            }
        }
        System.out.println(answer);
""",
               [_w18(ws, next((w for w in _firstseen(ws) if ws.count(w) == 1), "none"))
                for ws in (["a", "b", "a"], ["x", "x"], ["solo"],
                           ["p", "q", "p", "q", "r"], ["z", "z", "y", "y"])],
               ["The question is about ORDER, so a `LinkedHashMap` is the right "
                "choice — a HashMap gives no reliable order and a TreeMap gives "
                "alphabetical.",
                "Count in one pass, then walk `entrySet()` for the first count of "
                "exactly `1`.",
                "`break` as soon as you find it.",
                "Seed the answer as `\"none\"` so the all-repeat case needs no special "
                "handling.",
                "Re-putting a key does not move it, which is what preserves "
                "first-seen order."]),

        _p18ex("j18-pr-group", "Group by first letter", "Hard",
               "Print one line per distinct first letter, in alphabetical order, as "
               "`<letter>: [words]` — the words in the order they appeared.",
               """
        Map<Character, List<String>> groups = new TreeMap<>();
        for (String w : words) {
            char c = w.charAt(0);
            if (!groups.containsKey(c)) {
                groups.put(c, new ArrayList<>());
            }
            groups.get(c).add(w);
        }
        for (Map.Entry<Character, List<String>> e : groups.entrySet()) {
            System.out.println(e.getKey() + ": " + e.getValue());
        }
""",
               [_w18(ws, _nl(*[f"{c}: [" + ", ".join(w for w in ws if w[0] == c) + "]"
                               for c in sorted(set(w[0] for w in ws))]))
                for ws in (["ant", "bee", "ape"], ["solo"], ["x", "y"],
                           ["dog", "deer", "cat"], ["a", "b", "a"])],
               ["The map's values are Lists, so the type is "
                "`Map<Character, List<String>>`.",
                "Create the list the first time a letter is seen — check with "
                "`containsKey` before `get`.",
                "`groups.get(c).add(w)` then appends to the existing list.",
                "A `TreeMap` gives the letters alphabetically; the lists keep the "
                "words in input order because you append as you go.",
                "Printing a List directly gives the `[a, b]` form the brief asks "
                "for.",
                "`computeIfAbsent` does the create-if-missing step in one line, but "
                "it needs a lambda — Part 8."]),

        _p18ex("j18-pr-unique-only", "The ones that appear once", "Medium",
               "Print, in alphabetical order, the words that occur exactly once, as a "
               "set.",
               """
        Map<String, Integer> counts = new TreeMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        Set<String> once = new TreeSet<>();
        for (Map.Entry<String, Integer> e : counts.entrySet()) {
            if (e.getValue() == 1) {
                once.add(e.getKey());
            }
        }
        System.out.println(once);
""",
               [_w18(ws, _jset(sorted(w for w in set(ws) if ws.count(w) == 1)))
                for ws in _WS18],
               ["Count first, then filter on a count of exactly `1`.",
                "Collect into a `TreeSet` so the output is sorted and bracketed.",
                "Walking a `TreeMap` would already be alphabetical, so the TreeSet is "
                "belt and braces — but it makes the output type explicit.",
                "Case three has no word occurring once and prints `[]`."]),

        _p18ex("j18-pr-invert", "Turn it inside out", "Hard",
               "Read `n` name/score pairs. Print one line per distinct score, in "
               "ascending order, as `<score>: [names]` — the names alphabetical.",
               """
        int n = sc.nextInt();
        Map<Integer, Set<String>> byScore = new TreeMap<>();
        for (int i = 0; i < n; i++) {
            String who = sc.next();
            int v = sc.nextInt();
            if (!byScore.containsKey(v)) {
                byScore.put(v, new TreeSet<>());
            }
            byScore.get(v).add(who);
        }
        for (Map.Entry<Integer, Set<String>> e : byScore.entrySet()) {
            System.out.println(e.getKey() + ": " + e.getValue());
        }
""",
               [_case("\n".join([str(len(rows))] + [f"{k} {v}" for (k, v) in rows]),
                      _nl(*[f"{s}: [" + ", ".join(sorted(
                          n for (n, sc2) in rows if sc2 == s)) + "]"
                          for s in sorted(set(v for (_k, v) in rows))]))
                for rows in ([("Ada", 10), ("Bo", 20), ("Cy", 10)],
                             [("solo", 5)],
                             [("x", 1), ("y", 1)],
                             [("p", 3), ("q", 1), ("r", 2)],
                             [("a", 0), ("b", 0), ("c", 0)])],
               ["Inverting means the old values become keys — and several names may "
                "share a score, so the new values must be collections.",
                "`Map<Integer, Set<String>>` with a `TreeMap` for ascending scores "
                "and a `TreeSet` for alphabetical names.",
                "Create the inner set the first time a score is seen.",
                "That collision handling is the whole difficulty of inverting a "
                "map.",
                "Case five puts every name under one score."],
               read=""),

        _p18ex("j18-pr-two-groups", "Compare two word lists", "Hard",
               "Read two groups of words. Print three sorted sets: those only in the "
               "first, those in both, and those only in the second.",
               """
        int m = sc.nextInt();
        Set<String> second = new TreeSet<>();
        for (int i = 0; i < m; i++) {
            second.add(sc.next());
        }
        Set<String> first = new TreeSet<>(words);
        Set<String> onlyFirst = new TreeSet<>(first);
        onlyFirst.removeAll(second);
        Set<String> both = new TreeSet<>(first);
        both.retainAll(second);
        Set<String> onlySecond = new TreeSet<>(second);
        onlySecond.removeAll(first);
        System.out.println(onlyFirst);
        System.out.println(both);
        System.out.println(onlySecond);
""",
               [_case("\n".join([str(len(a)), " ".join(a), str(len(b)), " ".join(b)]),
                      _nl(_jset(sorted(set(a) - set(b))),
                          _jset(sorted(set(a) & set(b))),
                          _jset(sorted(set(b) - set(a)))))
                for (a, b) in ((["a", "b", "c"], ["b", "c", "d"]),
                               (["x"], ["y"]),
                               (["p", "q"], ["q", "p"]),
                               (["dog", "cat"], ["cat"]),
                               (["a", "a", "b"], ["b", "b"]))],
               ["`removeAll` and `retainAll` MODIFY the set they are called on, so "
                "each answer needs its own copy.",
                "`new TreeSet<>(first)` makes one in a single line.",
                "Computing them in place on `first` would destroy it before the next "
                "answer could be worked out.",
                "All three are `TreeSet`s, so every line prints sorted.",
                "An empty result prints `[]`."]),
    ])


_PRACTICE[18] = [_P18_A, _P18_B, _P18_C, _P18_D, _P18_E]
