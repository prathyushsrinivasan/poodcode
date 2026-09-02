# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 18 - Sets and Maps.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# OUTPUT STABILITY - the hard constraint on this whole module:
#   HashSet and HashMap have NO specified iteration order, so a judged program
#   must never print one directly. Every exercise here either
#     * uses LinkedHashSet / LinkedHashMap (insertion order) or
#       TreeSet / TreeMap (sorted order), both of which ARE specified, or
#     * prints something order-free: a size, a contains result, a lookup.
#   That constraint is not a workaround - it is exactly the lesson, and the
#   prose says so.
#
# `Comparable` and `Comparator` are module 20; TreeMap and TreeSet are used here
# only with String and Integer keys, whose natural ordering is built in, so the
# word never appears in a module 18 program.
# ---------------------------------------------------------------------------

_M18 = []


# --- 18.1 Set ---------------------------------------------------------------

_M18.append(_jlesson(
    "m18-set", "`Set`",
    "A collection with no duplicates, and no index.",
    """
```java
Set<String> seen = new HashSet<>();
seen.add("a");
seen.add("a");                 // ignored — already there
System.out.println(seen.size());        // 1
System.out.println(seen.contains("a")); // true
```

A `Set` holds each element **at most once** and has **no positions** — there is
no `get(i)`, because there is no "first". Everything else is familiar: `add`,
`remove`, `contains`, `size`, `isEmpty`, `clear`, and the enhanced `for`.

**`add` returns a boolean**: `true` if the set changed, `false` if the element
was already present. That single return value replaces the whole
"check-then-add" dance:

```java
if (seen.add(word)) { ... }    // ran for the FIRST occurrence only
```

**Why use one?** Because `contains` is **O(1)** on a `HashSet` against **O(n)**
on a list. Checking membership inside a loop turns an O(n²) algorithm into an
O(n) one, and that is the single most common reason a set appears in real code.

## The contract you must honour

A `HashSet` finds elements by their **hash code**, then confirms with
**`equals`**. So an element type must override **both**, consistently — module
13's contract, now with teeth:

- Override `equals` but not `hashCode`, and two equal objects land in different
  buckets. The set will happily hold both, and `contains` will return `false`
  for something you just added.
- `String`, `Integer` and the other library types already do this correctly,
  which is why they work out of the box.

**Never mutate an element after putting it in a set.** Changing a field that
`hashCode` depends on leaves the object filed under its old hash, and it becomes
unreachable — present in the set, but invisible to `contains`. Immutable
elements (module 12) make this impossible, which is a strong argument for them.

> **`HashSet` has no specified iteration order.** Printing one directly gives an
> order you must not rely on — it can change between JDK versions. The next
> lesson gives you two sets that *do* specify their order.
""",
    warmup=[
        _jq("What does `set.add(x)` return when `x` is already present?",
            ["false, and the set is unchanged", "true", "the old element",
             "it throws"],
            0,
            "Which makes `if (set.add(x))` a neat 'first time only' test."),
        _jq("Why must a set element override both equals and hashCode?",
            ["The set locates by hash and confirms with equals, so the two must agree",
             "For printing",
             "To allow sorting",
             "It only needs equals"],
            0,
            "Override one without the other and the set can hold two equal objects, or "
            "lose one you added."),
    ],
    exercises=[
        _je("j18-set-create", "Count the distinct ones",
            "Read `n` words and print how many are distinct. Replace `____` with the "
            "declaration of an empty set of strings.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Set<String> seen = new HashSet<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            seen.add(sc.next());\n"
                   "        }\n"
                   "        System.out.println(seen.size());"),
            "Set<String> seen = new HashSet<>();",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), len(set(ws)))
             for ws in (["a", "b", "a"], ["solo"], ["x", "x", "x"],
                        ["p", "q", "r"], ["a", "b", "a", "b"])],
            hints=["Declare the variable as the interface `Set<String>`.",
                   "Construct a `HashSet`, the usual implementation.",
                   "`Set<String> seen = new HashSet<>();`",
                   "Adding a duplicate is silently ignored, so `size()` is the "
                   "distinct count.",
                   "Note that only the SIZE is printed — a HashSet's order is not "
                   "specified, so the set itself must not be."],
            difficulty="Intro"),

        _je("j18-set-first", "React the first time only",
            "Print each word the first time it appears and nothing on repeats. Replace "
            "`____` with the condition that is true only for a word not seen before.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Set<String> seen = new HashSet<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String w = sc.next();\n"
                   "            if (seen.add(w)) {\n"
                   "                System.out.println(w);\n"
                   "            }\n"
                   "        }"),
            "seen.add(w)",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   _nl(*[w for (i, w) in enumerate(ws) if w not in ws[:i]]))
             for ws in (["a", "b", "a"], ["solo"], ["x", "x", "x"],
                        ["p", "q", "r"], ["a", "b", "a", "c"])],
            hints=["`add` already tells you whether the set changed.",
                   "It returns `true` only when the element was NOT there before.",
                   "So the whole check is the call itself: `if (seen.add(w))`.",
                   "Writing `if (!seen.contains(w)) { seen.add(w); ... }` also works "
                   "but does the lookup twice."],
            difficulty="Easy"),

        _jfix("j18-set-order", "Printing an unordered set",
              "This prints a `HashSet` directly, whose iteration order is not specified "
              "— so the output cannot be relied on. Change the set to the one that "
              "keeps **insertion order**, so the distinct words print in the order they "
              "first appeared.",
              _jscan("        int n = sc.nextInt();\n"
                     "        Set<String> seen = new HashSet<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            seen.add(sc.next());\n"
                     "        }\n"
                     "        System.out.println(seen);"),
              _jscan("        int n = sc.nextInt();\n"
                     "        Set<String> seen = new LinkedHashSet<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            seen.add(sc.next());\n"
                     "        }\n"
                     "        System.out.println(seen);"),
              [_case("\n".join([str(len(ws)), " ".join(ws)]),
                     "[" + ", ".join([w for (i, w) in enumerate(ws)
                                      if w not in ws[:i]]) + "]")
               for ws in (["b", "a", "b"], ["solo"], ["x", "y", "x", "z"],
                          ["q", "p"], ["c", "b", "a"])],
              hints=["`HashSet` makes no promise about order at all — the same program "
                     "may print differently on another JDK.",
                     "One implementation keeps a linked list alongside the hash table "
                     "so it can iterate in insertion order.",
                     "Only the constructor changes; the variable stays `Set<String>`.",
                     "`new LinkedHashSet<>()`",
                     "Case five would print sorted-looking output from a TreeSet, so "
                     "check you chose the insertion-order one, not the sorted one."],
              difficulty="Medium"),

        _jch("j18-set-dupes", "Any repeats?", "Easy",
             "Read `n` words. Print `true` if any word appears more than once, `false` "
             "otherwise. Use a set and stop as soon as you know.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Set<String> seen = new HashSet<>();\n"
                    "        boolean dupe = false;\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            if (!seen.add(sc.next())) {\n"
                    "                dupe = true;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(dupe);"),
             "        Set<String> seen = new HashSet<>();\n"
             "        boolean dupe = false;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            if (!seen.add(sc.next())) {\n"
             "                dupe = true;\n"
             "            }\n"
             "        }\n"
             "        System.out.println(dupe);",
             [_case("\n".join([str(len(ws)), " ".join(ws)]),
                    _jbool(len(set(ws)) != len(ws)))
              for ws in (["a", "b", "a"], ["solo"], ["x", "y", "z"],
                         ["p", "p"], ["a", "b", "c", "d"])],
             hints=["`add` returning `false` means the word was already there.",
                    "So `!seen.add(w)` is exactly 'this is a repeat'.",
                    "You must still read every remaining word, so keep looping — set "
                    "a flag rather than breaking out mid-read.",
                    "The alternative — comparing `seen.size()` with `n` at the end — "
                    "also works.",
                    "Only a boolean is printed, so the set's order never matters."]),
    ],
    quiz=[
        _jq("Why is a Set often used purely for `contains`?",
            ["It is O(1) on a HashSet, against O(n) on a list",
             "It sorts automatically",
             "It uses less memory",
             "Lists have no contains"],
            0,
            "Swapping a list for a set inside a loop is the standard way to turn an "
            "O(n^2) algorithm into O(n)."),
        _jq("What happens if you mutate an object after adding it to a HashSet?",
            ["It stays filed under its old hash and becomes unreachable",
             "The set re-hashes it",
             "It is removed",
             "Nothing"],
            0,
            "Which is a strong argument for immutable elements."),
    ],
))


# --- 18.2 the three sets ----------------------------------------------------

_M18.append(_jlesson(
    "m18-setkinds", "The three kinds of Set",
    "Same interface, three different orders.",
    """
| Implementation | Iteration order | `add`/`contains` | Needs |
|---|---|---|---|
| `HashSet` | **none specified** | O(1) | `hashCode` + `equals` |
| `LinkedHashSet` | insertion order | O(1) | `hashCode` + `equals` |
| `TreeSet` | **sorted** | O(log n) | elements to be orderable |

All three implement `Set`, so the code around them is identical — only the
constructor changes.

**`HashSet` is the default.** Fastest, smallest, and you usually do not care
about order.

**`LinkedHashSet`** keeps a linked list threaded through the entries, so
iteration follows the order things were first added. It costs a little memory
and gives you reproducibility — which matters enormously for anything you print,
log or test.

**`TreeSet`** keeps its elements sorted, so iterating gives ascending order for
free. It is a red-black tree, so operations are O(log n) rather than O(1) — you
are paying for the ordering. It also adds `first()`, `last()`, `headSet`,
`tailSet` and friends.

**Converting between them is one constructor call**, and this is the standard
way to sort the contents of a hash-based set:

```java
Set<String> sorted = new TreeSet<>(anyOtherSet);
```

## Which to reach for

- Need speed and nothing else? **`HashSet`.**
- Printing or comparing output? **`LinkedHashSet`**, so the result is
  reproducible.
- Need it in order? **`TreeSet`.**

> **`TreeSet` uses `compareTo`, not `equals`.** Two elements that compare equal
> are treated as the same element even if `equals` disagrees. For `String` and
> `Integer` the two always agree, so it does not bite here — but module 20
> returns to it once you can write your own ordering.
""",
    warmup=[
        _jq("Which Set iterates in sorted order?",
            ["TreeSet", "HashSet", "LinkedHashSet", "All of them"],
            0,
            "LinkedHashSet gives insertion order; HashSet gives no guarantee at all."),
        _jq("What do you give up by choosing TreeSet over HashSet?",
            ["O(1) operations - TreeSet is O(log n)", "Duplicate handling",
             "The contains method", "Nothing"],
            0,
            "The ordering is not free; it is paid for in every add and lookup."),
    ],
    exercises=[
        _je("j18-kinds-tree", "Sorted, for free",
            "Read `n` words and print the distinct ones in **alphabetical** order. "
            "Replace `____` with the constructor that gives sorted iteration.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Set<String> words = new TreeSet<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            words.add(sc.next());\n"
                   "        }\n"
                   "        System.out.println(words);"),
            "new TreeSet<>()",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   "[" + ", ".join(sorted(set(ws))) + "]")
             for ws in (["pear", "apple", "pear"], ["solo"], ["c", "b", "a"],
                        ["x", "y"], ["dog", "cat", "ant", "cat"])],
            hints=["Three implementations, three orders — you want the sorted one.",
                   "`new TreeSet<>()`",
                   "`String` has a natural ordering built in, so nothing else is "
                   "needed.",
                   "Duplicates still collapse, because it is still a `Set`."],
            difficulty="Intro"),

        _je("j18-kinds-linked", "In the order they arrived",
            "Print the distinct words in the order they were **first seen**. Replace "
            "`____` with the constructor that guarantees that.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Set<String> words = new LinkedHashSet<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            words.add(sc.next());\n"
                   "        }\n"
                   "        System.out.println(words);"),
            "new LinkedHashSet<>()",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   "[" + ", ".join([w for (i, w) in enumerate(ws)
                                    if w not in ws[:i]]) + "]")
             for ws in (["pear", "apple", "pear"], ["solo"], ["c", "b", "a"],
                        ["x", "y"], ["dog", "cat", "ant", "cat"])],
            hints=["Insertion order, not sorted order — case three would come out "
                   "`[a, b, c]` from a TreeSet and must come out `[c, b, a]` here.",
                   "`new LinkedHashSet<>()`",
                   "A repeated word keeps its ORIGINAL position; re-adding does not "
                   "move it to the end.",
                   "That is why case one starts with `pear`."],
            difficulty="Easy"),

        _jch("j18-kinds-sort", "Sorting a hash set", "Easy",
             "The words are collected in a `HashSet`, whose iteration order is not "
             "specified — printing it directly would give output you cannot rely on. "
             "Where you see `____`, produce the same elements in sorted order and "
             "print them, without changing how the set is built.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Set<String> words = new HashSet<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            words.add(sc.next());\n"
                    "        }\n"
                    "        Set<String> sorted = new TreeSet<>(words);\n"
                    "        System.out.println(sorted);"),
             "        Set<String> sorted = new TreeSet<>(words);\n"
             "        System.out.println(sorted);",
             [_case("\n".join([str(len(ws)), " ".join(ws)]),
                    "[" + ", ".join(sorted(set(ws))) + "]")
              for ws in (["pear", "apple", "pear"], ["solo"], ["c", "b", "a"],
                         ["x", "y"], ["dog", "cat", "ant"])],
             hints=["Every set implementation has a constructor that takes another "
                    "collection and copies it.",
                    "So converting is one line: `new TreeSet<>(words)`.",
                    "Print the new set, not the original.",
                    "This is the standard idiom for 'I used a HashSet for speed and "
                    "now I need the output ordered'.",
                    "Note that a HashSet of a few short strings often *happens* to "
                    "come out sorted — which is exactly why relying on it is "
                    "dangerous rather than safe."]),

        _jch("j18-kinds-intersect", "What appears in both", "Medium",
             "Read two groups of words. Print, in alphabetical order, the words that "
             "appear in **both**. Use `retainAll`.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Set<String> a = new TreeSet<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            a.add(sc.next());\n"
                    "        }\n"
                    "        int m = sc.nextInt();\n"
                    "        Set<String> b = new TreeSet<>();\n"
                    "        for (int i = 0; i < m; i++) {\n"
                    "            b.add(sc.next());\n"
                    "        }\n"
                    "        a.retainAll(b);\n"
                    "        System.out.println(a);"),
             "        a.retainAll(b);\n"
             "        System.out.println(a);",
             [_case("\n".join([str(len(xs)), " ".join(xs),
                               str(len(ys)), " ".join(ys)]),
                    "[" + ", ".join(sorted(set(xs) & set(ys))) + "]")
              for (xs, ys) in ((["a", "b", "c"], ["b", "c", "d"]),
                               (["x"], ["y"]),
                               (["p", "q"], ["q", "p"]),
                               (["dog", "cat"], ["cat"]),
                               (["a", "a", "b"], ["b", "b"]))],
             hints=["`retainAll` keeps only the elements also present in the other "
                    "collection — set intersection, in place.",
                    "It MODIFIES the set it is called on, so `a` becomes the "
                    "intersection.",
                    "Both sets are `TreeSet`s, so the result prints alphabetically "
                    "with no extra work.",
                    "The siblings are `addAll` (union) and `removeAll` (difference).",
                    "An empty intersection prints `[]`."]),
    ],
    quiz=[
        _jq("How do you convert a HashSet's contents into sorted order?",
            ["new TreeSet<>(theHashSet)", "Call sort() on it",
             "It is already sorted", "Convert to an array first"],
            0,
            "Every collection has a constructor taking another collection, which makes "
            "converting a one-liner."),
        _jq("Which set would you use for output you intend to assert on in a test?",
            ["LinkedHashSet or TreeSet - both specify their order",
             "HashSet", "Any of them", "None"],
            0,
            "A HashSet's order can differ between JDK versions, so a test asserting on "
            "it is not really a test."),
    ],
))


# --- 18.3 Map ---------------------------------------------------------------

_M18.append(_jlesson(
    "m18-map", "`Map`",
    "Look something up by a key.",
    """
```java
Map<String, Integer> ages = new HashMap<>();
ages.put("Ada", 36);
ages.put("Bo", 41);
System.out.println(ages.get("Ada"));        // 36
System.out.println(ages.get("Nobody"));     // null
System.out.println(ages.containsKey("Bo")); // true
System.out.println(ages.size());            // 2
```

A `Map` stores **key to value** pairs. Keys are unique — `put` with an existing
key **replaces** the value and returns the old one. A `Map` is not a
`Collection`; it is its own interface.

| Call | Does |
|---|---|
| `put(k, v)` | insert or replace; returns the previous value or `null` |
| `get(k)` | the value, or **`null`** if absent |
| `getOrDefault(k, d)` | the value, or `d` if absent |
| `containsKey(k)` | is that key present |
| `remove(k)` | remove and return the old value |
| `keySet()` / `values()` / `entrySet()` | views for iterating |

**`get` returning `null` is the trap.** Unboxing it explodes:

```java
int n = ages.get("Nobody");        // NullPointerException
```

`getOrDefault` exists precisely to avoid that.

## The frequency-count idiom

Counting occurrences is what maps get used for more than anything else:

```java
Map<String, Integer> counts = new HashMap<>();
for (String w : words) {
    counts.put(w, counts.getOrDefault(w, 0) + 1);
}
```

Read it as: *whatever it was, or zero if new, plus one.* One line, no `if`, no
null. `merge(w, 1, Integer::sum)` is the modern alternative, but the
`getOrDefault` form is clearer while method references are still ahead of you.

This is module 4's counting array, freed from needing small integer keys and a
known range.

**Keys must honour `hashCode` and `equals`**, exactly as set elements must — a
`HashMap` is what a `HashSet` is built on. And as with sets, **`HashMap` has no
specified iteration order**, so a program that prints one directly is not
reproducible.
""",
    warmup=[
        _jq("What does `map.get(k)` return for a key that is not present?",
            ["null", "0", "an empty string", "it throws"],
            0,
            "Which is why assigning it straight into an `int` can throw a "
            "NullPointerException."),
        _jq("What does `put` return when the key was already present?",
            ["The previous value", "null", "true", "the new value"],
            0,
            "Useful when you want to know whether you replaced something."),
    ],
    exercises=[
        _je("j18-map-create", "Store and look up",
            "Read `n` name/age pairs, then a name to look up. Print that person's age, "
            "or `-1` if unknown. Replace `____` with the lookup that supplies the "
            "default safely.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Map<String, Integer> ages = new HashMap<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            ages.put(sc.next(), sc.nextInt());\n"
                   "        }\n"
                   "        String who = sc.next();\n"
                   "        System.out.println(ages.getOrDefault(who, -1));"),
            "ages.getOrDefault(who, -1)",
            [_case("\n".join([str(len(rows))]
                             + [f"{k} {v}" for (k, v) in rows] + [q]),
                   dict(rows).get(q, -1))
             for (rows, q) in (([("Ada", 36), ("Bo", 41)], "Ada"),
                               ([("Ada", 36)], "Nobody"),
                               ([("x", 0)], "x"),
                               ([("a", 1), ("b", 2)], "b"),
                               ([("p", 7)], "q"))],
            hints=["`ages.get(who)` returns `null` for an unknown name, and assigning "
                   "that to an `int` throws.",
                   "There is a method that takes the fallback as a second argument.",
                   "`ages.getOrDefault(who, -1)`",
                   "It returns an `Integer`, which unboxes cleanly because it is never "
                   "null."],
            difficulty="Easy"),

        _je("j18-map-count", "Count the words",
            "Read `n` words, then one word to report on. Print how many times that word "
            "occurred. Replace `____` with the counting line.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Map<String, Integer> counts = new HashMap<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String w = sc.next();\n"
                   "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                   "        }\n"
                   "        String q = sc.next();\n"
                   "        System.out.println(counts.getOrDefault(q, 0));"),
            "counts.put(w, counts.getOrDefault(w, 0) + 1);",
            [_case("\n".join([str(len(ws)), " ".join(ws), q]), ws.count(q))
             for (ws, q) in ((["a", "b", "a"], "a"), (["solo"], "solo"),
                             (["x", "y"], "z"), (["p", "p", "p"], "p"),
                             (["a", "b", "c"], "b"))],
            hints=["The idiom is: put back whatever was there, or zero if new, plus "
                   "one.",
                   "`counts.getOrDefault(w, 0)` gives the current count without any "
                   "null risk.",
                   "`counts.put(w, counts.getOrDefault(w, 0) + 1);`",
                   "This is module 4's counting array without needing small integer "
                   "keys or a known range."],
            difficulty="Easy"),

        _jfix("j18-map-npe", "The null that unboxed",
              "This throws a `NullPointerException` for a word that was never seen, "
              "because `get` returns `null` and it is being unboxed into an `int`. Fix "
              "it so an unseen word reports `0`.",
              _jscan("        int n = sc.nextInt();\n"
                     "        Map<String, Integer> counts = new HashMap<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            String w = sc.next();\n"
                     "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                     "        }\n"
                     "        String q = sc.next();\n"
                     "        int c = counts.get(q);\n"
                     "        System.out.println(c);"),
              _jscan("        int n = sc.nextInt();\n"
                     "        Map<String, Integer> counts = new HashMap<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            String w = sc.next();\n"
                     "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                     "        }\n"
                     "        String q = sc.next();\n"
                     "        int c = counts.getOrDefault(q, 0);\n"
                     "        System.out.println(c);"),
              [_case("\n".join([str(len(ws)), " ".join(ws), q]), ws.count(q))
               for (ws, q) in ((["a", "b", "a"], "a"), (["x", "y"], "z"),
                               (["solo"], "other"), (["p", "p"], "p"),
                               (["a"], "b"))],
              hints=["`counts.get(q)` is an `Integer`, and it is `null` when the key "
                     "is absent.",
                     "`int c = null` cannot work, so unboxing throws.",
                     "Supply the fallback at the lookup instead.",
                     "`counts.getOrDefault(q, 0)`",
                     "Cases two, three and five all ask about words that were never "
                     "seen."],
              difficulty="Easy"),

        _jch("j18-map-replace", "What did it replace?", "Medium",
             "Read `n` key/value pairs, putting each into a map. Print `new` when a key "
             "was not present before, and `was <old value>` when it replaced something.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Map<String, Integer> m = new HashMap<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String k = sc.next();\n"
                    "            int v = sc.nextInt();\n"
                    "            Integer old = m.put(k, v);\n"
                    "            if (old == null) {\n"
                    '                System.out.println("new");\n'
                    "            } else {\n"
                    '                System.out.println("was " + old);\n'
                    "            }\n"
                    "        }"),
             "            Integer old = m.put(k, v);\n"
             "            if (old == null) {\n"
             '                System.out.println("new");\n'
             "            } else {\n"
             '                System.out.println("was " + old);\n'
             "            }",
             [_case("\n".join([str(len(rows))] + [f"{k} {v}" for (k, v) in rows]),
                    _nl(*[(lambda seen: "new" if k not in seen else f"was {seen[k]}")(
                        dict(rows[:i])) for (i, (k, v)) in enumerate(rows)]))
              for rows in ([("a", 1), ("a", 2)],
                           [("x", 5)],
                           [("p", 1), ("q", 2), ("p", 3)],
                           [("k", 0), ("k", 0)],
                           [("a", 1), ("b", 2), ("c", 3)])],
             hints=["`put` returns the PREVIOUS value for that key, or `null` if there "
                    "was none.",
                    "Capture it in an `Integer`, not an `int` — it may be null.",
                    "Compare it with `== null`; that is the one place `==` is right "
                    "for a wrapper.",
                    "Case four replaces a value with the same number and must still "
                    "print `was 0`."]),
    ],
    quiz=[
        _jq("Which avoids a NullPointerException when counting?",
            ["counts.getOrDefault(w, 0) + 1", "counts.get(w) + 1",
             "counts.put(w, counts.get(w))", "counts.size() + 1"],
            0,
            "`get` returns null for a new key, and `null + 1` cannot unbox."),
        _jq("Is Map a Collection?",
            ["No - it is a separate interface", "Yes", "Only HashMap is",
             "Only if it holds Collections"],
            0,
            "Which is why it has no `add`, and why you iterate through keySet(), "
            "values() or entrySet()."),
    ],
))


# --- 18.4 map kinds and iteration -------------------------------------------

_M18.append(_jlesson(
    "m18-mapkinds", "Map flavours, and iterating one",
    "The same three orders, and the three views.",
    """
| Implementation | Key order | `get`/`put` |
|---|---|---|
| `HashMap` | **none specified** | O(1) |
| `LinkedHashMap` | insertion order | O(1) |
| `TreeMap` | **sorted by key** | O(log n) |

Exactly the same three-way choice as the sets, for exactly the same reasons —
because `HashSet` is a `HashMap` underneath.

## Iterating

A `Map` is not a `Collection`, so you iterate one of its three **views**:

```java
for (String k : m.keySet())          { ... }        // keys
for (int v : m.values())             { ... }        // values (may repeat)
for (Map.Entry<String, Integer> e : m.entrySet()) { // both — the efficient one
    System.out.println(e.getKey() + "=" + e.getValue());
}
```

**Prefer `entrySet()` when you need both.** Looping `keySet()` and calling
`get(k)` inside does a second lookup for every entry — correct, but twice the
work for no reason.

**A `TreeMap` iterates by sorted key**, which is what makes it the right choice
whenever you are printing a report:

```java
Map<String, Integer> counts = new TreeMap<>(hashCounts);   // one line to sort
```

**A map's `toString` is specified as `{a=1, b=2}`** — braces, `key=value`,
comma-space. Combined with a `TreeMap` that gives fully reproducible output,
which is what the exercises here assert on.

**The views are live.** `keySet()` is not a copy: removing from it removes from
the map, and modifying the map while iterating a view throws
`ConcurrentModificationException`, exactly as with a list. `entry.setValue(v)`
is the one legal modification during iteration, and it writes through to the
map.
""",
    warmup=[
        _jq("Which view should you iterate when you need both key and value?",
            ["entrySet()", "keySet()", "values()", "Any - they are identical"],
            0,
            "Iterating keySet() and calling get() inside does a second lookup for every "
            "entry."),
        _jq("What does a TreeMap's iteration order follow?",
            ["Sorted key order", "Insertion order", "Value order", "Unspecified"],
            0,
            "Which makes it the natural choice for printed reports."),
    ],
    exercises=[
        _je("j18-mk-tree", "A report in key order",
            "Count the words and print the whole map, with keys in alphabetical order. "
            "Replace `____` with the constructor that guarantees that.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Map<String, Integer> counts = new TreeMap<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String w = sc.next();\n"
                   "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                   "        }\n"
                   "        System.out.println(counts);"),
            "new TreeMap<>()",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   "{" + ", ".join(f"{k}={ws.count(k)}" for k in sorted(set(ws))) + "}")
             for ws in (["pear", "apple", "pear"], ["solo"], ["c", "b", "a"],
                        ["x", "y", "x"], ["dog", "cat", "ant", "cat"])],
            hints=["Three implementations, three orders — you want the sorted one.",
                   "`new TreeMap<>()`",
                   "A map prints as `{key=value, key=value}` with braces.",
                   "A `HashMap` here would produce output you could not rely on."],
            difficulty="Intro"),

        _je("j18-mk-entryset", "Walk the pairs",
            "Print each key and value as `key=value` on its own line, in sorted key "
            "order. Replace `____` with the enhanced `for` header over the pair view.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Map<String, Integer> counts = new TreeMap<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String w = sc.next();\n"
                   "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                   "        }\n"
                   "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
                   '            System.out.println(e.getKey() + "=" + e.getValue());\n'
                   "        }"),
            "for (Map.Entry<String, Integer> e : counts.entrySet()) {",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   _nl(*[f"{k}={ws.count(k)}" for k in sorted(set(ws))]))
             for ws in (["pear", "apple", "pear"], ["solo"], ["c", "b", "a"],
                        ["x", "y", "x"], ["dog", "cat", "ant"])],
            hints=["The element type of `entrySet()` is `Map.Entry<K, V>` — note the "
                   "dot, since `Entry` is nested inside `Map`.",
                   "Both type arguments must be written out.",
                   "`for (Map.Entry<String, Integer> e : counts.entrySet()) {`",
                   "Then `e.getKey()` and `e.getValue()` read the pair with no second "
                   "lookup."],
            difficulty="Medium"),

        _jch("j18-mk-onepass", "One lookup, not two", "Medium",
             "Print each pair as `key:value`, one per line, in sorted key order. Walk "
             "`entrySet()` rather than iterating `keySet()` and calling `get` inside — "
             "that would do a second hash lookup for every entry.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Map<String, Integer> counts = new TreeMap<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String w = sc.next();\n"
                    "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                    "        }\n"
                    "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
                    '            System.out.println(e.getKey() + ":" + e.getValue());\n'
                    "        }"),
             "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
             '            System.out.println(e.getKey() + ":" + e.getValue());\n'
             "        }",
             [_case("\n".join([str(len(ws)), " ".join(ws)]),
                    _nl(*[f"{k}:{ws.count(k)}" for k in sorted(set(ws))]))
              for ws in (["pear", "apple", "pear"], ["solo"], ["c", "b", "a"],
                         ["x", "y", "x"], ["dog", "cat"])],
             hints=["`entrySet()` hands you the key and the value together, so no "
                    "`get` is needed.",
                    "The element type is `Map.Entry<String, Integer>` — note the dot, "
                    "since `Entry` is nested inside `Map`.",
                    "`e.getKey()` and `e.getValue()` read the pair.",
                    "The separator is a colon with no spaces.",
                    "The map is a `TreeMap`, so the keys already arrive "
                    "alphabetically."]),

        _jch("j18-mk-max", "The most common word", "Hard",
             "Count the words and print the one that occurs most often, then its count, "
             "separated by a space. On a tie, print the alphabetically **first** of the "
             "tied words.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Map<String, Integer> counts = new TreeMap<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String w = sc.next();\n"
                    "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                    "        }\n"
                    '        String bestWord = "";\n'
                    "        int bestCount = -1;\n"
                    "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
                    "            if (e.getValue() > bestCount) {\n"
                    "                bestCount = e.getValue();\n"
                    "                bestWord = e.getKey();\n"
                    "            }\n"
                    "        }\n"
                    '        System.out.println(bestWord + " " + bestCount);'),
             '        String bestWord = "";\n'
             "        int bestCount = -1;\n"
             "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
             "            if (e.getValue() > bestCount) {\n"
             "                bestCount = e.getValue();\n"
             "                bestWord = e.getKey();\n"
             "            }\n"
             "        }\n"
             '        System.out.println(bestWord + " " + bestCount);',
             [_case("\n".join([str(len(ws)), " ".join(ws)]),
                    (lambda best: f"{best} {ws.count(best)}")(
                        min(sorted(set(ws)), key=lambda w: -ws.count(w))))
              for ws in (["a", "b", "a"], ["solo"], ["x", "y"],
                         ["p", "q", "q", "p"], ["dog", "cat", "cat", "ant"])],
             hints=["Count first, then run module 1's running maximum over the "
                    "entries.",
                    "The map is a `TreeMap`, so `entrySet()` arrives in alphabetical "
                    "key order.",
                    "That means a strict `>` keeps the alphabetically first of any "
                    "tie, with no extra comparison — case three and case four both "
                    "depend on it.",
                    "Seed `bestCount` at `-1` so the first entry always wins; no real "
                    "count is negative.",
                    "Track BOTH the word and the count, and print them separated by a "
                    "space."]),
    ],
    quiz=[
        _jq("Why prefer entrySet() over keySet() plus get()?",
            ["It avoids a second hash lookup for every entry",
             "It is the only way to get values",
             "keySet() is unordered",
             "There is no difference"],
            0,
            "Both are correct; one does twice the work."),
        _jq("What is `keySet()` - a copy or a view?",
            ["A live view: removing from it removes from the map",
             "An independent copy",
             "An immutable snapshot",
             "A List"],
            0,
            "Which also means modifying the map while iterating it throws "
            "ConcurrentModificationException."),
    ],
))


# ===========================================================================
# Capstone
# ===========================================================================

def _m18_run(words, stop):
    kept = [w for w in words if w != stop]
    counts = {}
    for w in kept:
        counts[w] = counts.get(w, 0) + 1
    keys = sorted(counts)
    lines = ["distinct=" + str(len(keys))]
    lines.append("[" + ", ".join(keys) + "]")
    for k in keys:
        lines.append(f"{k}={counts[k]}")
    if keys:
        best = min(keys, key=lambda w: (-counts[w], w))
        lines.append("top=" + best + " " + str(counts[best]))
    else:
        lines.append("top=none 0")
    return _nl(*lines)


def _m18_case(words, stop):
    return _case("\n".join([str(len(words)), " ".join(words), stop]),
                 _m18_run(words, stop))


_M18_CAP = _jcap(
    "Word report",
    """
The classic use of both structures at once: a set to answer "have I seen this",
and a map to answer "how many times".

## Input

```
n
<n words on one line>
<one stop-word to ignore entirely>
```

## Output

1. `distinct=<how many different words survive>`
2. The surviving words as a sorted set, printed directly — `[a, b, c]`
3. One `word=count` line per surviving word, in alphabetical order
4. `top=<most frequent word> <its count>`, alphabetically first on a tie, or
   `top=none 0` when nothing survives

## What the hidden cases check

- **The stop-word is removed before anything is counted**, so it appears in no
  line.
- **Output order is specified, so the implementations must be too.** A `HashSet`
  or `HashMap` printed directly would produce an order this test cannot rely on.
  Use `TreeSet` and `TreeMap`, or convert before printing.
- **The tie rule falls out of the ordering.** Iterating a `TreeMap` gives
  alphabetical keys, so a strict `>` in the running maximum keeps the first tied
  word without any extra comparison.
- **Every word being the stop-word must not crash.** Guard the `top=` line;
  there is no maximum of nothing.
- **A map prints as `{a=1}` and a set as `[a]`** — line 2 is a set, and lines of
  type 3 are printed one pair at a time, not as a whole map.
""",
    _jch("j18-cap-report", "Word report", "Hard",
         "Write the whole body where you see `____`: read the words and the stop-word, "
         "filter, count, and print the four sections.",
         _jscan("        int n = sc.nextInt();\n"
                "        List<String> words = new ArrayList<>();\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            words.add(sc.next());\n"
                "        }\n"
                "        String stop = sc.next();\n"
                "        Map<String, Integer> counts = new TreeMap<>();\n"
                "        for (String w : words) {\n"
                "            if (!w.equals(stop)) {\n"
                "                counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                "            }\n"
                "        }\n"
                '        System.out.println("distinct=" + counts.size());\n'
                "        Set<String> distinct = new TreeSet<>(counts.keySet());\n"
                "        System.out.println(distinct);\n"
                '        String bestWord = "none";\n'
                "        int bestCount = 0;\n"
                "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
                '            System.out.println(e.getKey() + "=" + e.getValue());\n'
                "            if (e.getValue() > bestCount) {\n"
                "                bestCount = e.getValue();\n"
                "                bestWord = e.getKey();\n"
                "            }\n"
                "        }\n"
                '        System.out.println("top=" + bestWord + " " + bestCount);'),
         "        int n = sc.nextInt();\n"
         "        List<String> words = new ArrayList<>();\n"
         "        for (int i = 0; i < n; i++) {\n"
         "            words.add(sc.next());\n"
         "        }\n"
         "        String stop = sc.next();\n"
         "        Map<String, Integer> counts = new TreeMap<>();\n"
         "        for (String w : words) {\n"
         "            if (!w.equals(stop)) {\n"
         "                counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
         "            }\n"
         "        }\n"
         '        System.out.println("distinct=" + counts.size());\n'
         "        Set<String> distinct = new TreeSet<>(counts.keySet());\n"
         "        System.out.println(distinct);\n"
         '        String bestWord = "none";\n'
         "        int bestCount = 0;\n"
         "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
         '            System.out.println(e.getKey() + "=" + e.getValue());\n'
         "            if (e.getValue() > bestCount) {\n"
         "                bestCount = e.getValue();\n"
         "                bestWord = e.getKey();\n"
         "            }\n"
         "        }\n"
         '        System.out.println("top=" + bestWord + " " + bestCount);',
         [_m18_case(ws, stop) for (ws, stop) in (
             (["a", "b", "a", "the"], "the"),
             (["x"], "x"),
             (["dog", "cat", "cat", "ant"], "none"),
             (["p", "q", "q", "p"], "z"),
             (["solo"], "other"),
         )],
         hints=["Use a `TreeMap` for the counts, so both the `word=count` lines and "
                "the `top=` scan arrive in alphabetical order.",
                "Filter the stop-word BEFORE counting — compare with `.equals`.",
                "`distinct=` is just `counts.size()`, since each key is one distinct "
                "surviving word.",
                "Line 2 is a SET printed directly, which gives the `[a, b]` form. "
                "`new TreeSet<>(counts.keySet())` builds it in one line.",
                "One loop over `entrySet()` can both print each pair and track the "
                "maximum — no second pass needed.",
                "Seed `bestWord` as `\"none\"` and `bestCount` as `0`, which is exactly "
                "the answer required when nothing survives.",
                "Because the keys arrive alphabetically, a strict `>` already keeps "
                "the first of a tie.",
                "Case two removes the only word, so the map is empty and the loop "
                "never runs — the seeds carry the `top=none 0` line."]),
    example_io="stdin:  4\n        a b a the\n        the\n\n"
               "stdout: distinct=2\n        [a, b]\n        a=2\n        b=1\n"
               "        top=a 2",
    rubric=[
        "The stop-word is filtered out before any counting.",
        "Counts live in a `TreeMap`, so the report is in alphabetical key order.",
        "`distinct=` uses the map's size.",
        "Line 2 prints a `Set`, giving the bracketed form.",
        "A single `entrySet()` loop both prints and finds the maximum.",
        "The tie rule relies on the sorted iteration plus a strict `>`.",
        "An empty result prints `top=none 0` rather than crashing.",
        "No `HashSet` or `HashMap` is printed directly anywhere.",
    ],
)


_MODULES.append(_jmod(
    18, 6, "The collections framework",
    "Sets and Maps",
    "Store things without duplicates, look things up by key, and choose deliberately "
    "between the hashed, insertion-ordered and sorted flavours of each.",
    """
A `List` answers *what is at position 3*. A `Set` answers *have I seen this*, and
a `Map` answers *what is this associated with* — and both do it in O(1) rather
than by scanning.

That single fact is why sets and maps appear everywhere. Replacing a
`list.contains(x)` inside a loop with a `set.contains(x)` turns an O(n²)
algorithm into an O(n) one, and the **frequency-count idiom** —
`counts.put(w, counts.getOrDefault(w, 0) + 1)` — is module 4's counting array
freed from needing small integer keys and a known range.

The price is the **`hashCode`/`equals` contract**. A hash structure locates by
hash and confirms with equals, so an element or key type must honour both,
consistently, and must not be mutated afterwards. Module 13 introduced that
contract; this is where breaking it silently loses your data.

The other running theme is **iteration order**, and it is why this module is
careful. `HashSet` and `HashMap` specify none at all, so a program that prints
one directly is not reproducible. `LinkedHashSet`/`LinkedHashMap` give insertion
order and `TreeSet`/`TreeMap` give sorted order — and converting is a single
constructor call. Choosing deliberately between the three is most of the skill.
""",
    _M18,
    capstone=_M18_CAP,
    objectives=[
        "Use a `Set` for membership and de-duplication, including `add`'s boolean return.",
        "Say why set elements and map keys must honour hashCode and equals together.",
        "Choose between HashSet, LinkedHashSet and TreeSet by the order you need.",
        "Convert between implementations with a single constructor call.",
        "Use a `Map` for lookup, and avoid the null that `get` returns.",
        "Write the frequency-count idiom with `getOrDefault`.",
        "Iterate a map through keySet, values and entrySet, and say why entrySet is preferred.",
        "Explain why printing a HashMap directly makes a program non-reproducible.",
    ],
    why="Counting, de-duplicating and looking up are three of the most common things "
        "any program does, and doing them with a list is the most common performance "
        "mistake there is. The hashCode/equals contract and the "
        "HashMap/LinkedHashMap/TreeMap comparison are both standard interview ground.",
    est_minutes=330,
    glossary=[
        _jg("Set", "A collection with no duplicates and no index."),
        _jg("HashSet", "The default Set. O(1), no specified iteration order."),
        _jg("LinkedHashSet", "A Set that iterates in insertion order."),
        _jg("TreeSet", "A Set that iterates in sorted order. O(log n)."),
        _jg("Map", "Key-to-value associations with unique keys. Not a Collection."),
        _jg("HashMap", "The default Map. O(1), no specified iteration order."),
        _jg("LinkedHashMap", "A Map that iterates in insertion order."),
        _jg("TreeMap", "A Map that iterates in sorted key order. O(log n)."),
        _jg("getOrDefault", "A lookup that supplies a fallback instead of returning "
                            "null - the safe way to count."),
        _jg("entrySet", "The view giving key and value together, avoiding a second "
                        "lookup."),
        _jg("Map.Entry", "One key-value pair, with getKey() and getValue()."),
        _jg("view", "keySet(), values() and entrySet() are live windows onto the map, "
                    "not copies."),
        _jg("hashCode/equals contract", "Equal objects must have equal hash codes. "
                                        "Break it and a hash structure loses your data."),
    ],
    cheatsheet="""
```java
// --- Set ------------------------------------------------------------------
Set<String> s = new HashSet<>();         // O(1), NO specified order
Set<String> s = new LinkedHashSet<>();   // insertion order
Set<String> s = new TreeSet<>();         // sorted, O(log n)
Set<String> sorted = new TreeSet<>(s);   // convert in one line

s.add(x)        // returns TRUE only if the set changed  -> "first time" test
s.contains(x)   // O(1) on HashSet vs O(n) on a List
s.remove(x)  s.size()  s.isEmpty()
a.retainAll(b)  // intersection, IN PLACE   (addAll = union, removeAll = difference)

// --- Map ------------------------------------------------------------------
Map<String, Integer> m = new HashMap<>();      // no specified order
Map<String, Integer> m = new LinkedHashMap<>();// insertion order
Map<String, Integer> m = new TreeMap<>();      // sorted by key

m.put(k, v)                 // returns the PREVIOUS value, or null
m.get(k)                    // null when absent  -> unboxing it can throw
m.getOrDefault(k, 0)        // the safe lookup
m.containsKey(k)  m.remove(k)  m.size()

// --- the counting idiom ---------------------------------------------------
counts.put(w, counts.getOrDefault(w, 0) + 1);

// --- iterating a map ------------------------------------------------------
for (String k : m.keySet())   { ... }
for (int v : m.values())      { ... }
for (Map.Entry<String, Integer> e : m.entrySet()) {   // preferred for both
    e.getKey(); e.getValue();
}

// --- printing -------------------------------------------------------------
System.out.println(set);   // [a, b]
System.out.println(map);   // {a=1, b=2}
// ...but ONLY reproducible for LinkedHash* / Tree*.  Never assert on a HashMap.
```
""",
    self_check=[
        "Can you say what `set.add(x)` returns, and use it as a 'first time only' test?",
        "Can you explain why overriding equals without hashCode breaks a HashSet?",
        "Can you name the three Set implementations and the order each guarantees?",
        "Can you convert a HashSet's contents to sorted order in one line?",
        "Can you say what `map.get(k)` returns for an absent key, and why that can throw?",
        "Can you write the frequency-count idiom from memory?",
        "Can you say why entrySet() beats keySet() plus get()?",
        "Can you explain why printing a HashMap makes a test unreliable?",
    ],
    review=[
        _jq("Which Set gives you the elements back in the order you added them?",
            ["LinkedHashSet", "HashSet", "TreeSet", "None of them"],
            0,
            "TreeSet gives sorted order; HashSet gives no guarantee."),
        _jq("```java\nMap<String,Integer> m = new HashMap<>();\nint c = m.get(\"x\");\n```\nWhat happens?",
            ["NullPointerException - get returns null and it cannot unbox",
             "c is 0", "It does not compile", "c is -1"],
            0,
            "`getOrDefault(\"x\", 0)` is the fix."),
        _jq("Why is `counts.put(w, counts.getOrDefault(w, 0) + 1)` preferred over a containsKey check?",
            ["It is one lookup-and-store with no null and no branch",
             "It is the only way that compiles",
             "containsKey does not exist",
             "It sorts the map"],
            0,
            "Read it as 'whatever it was, or zero if new, plus one'."),
        _jq("In the capstone, why does a strict `>` keep the alphabetically first tied word?",
            ["Because a TreeMap's entrySet arrives in alphabetical key order, so the earliest tie is seen first and never replaced",
             "Because > compares strings",
             "It does not - a second comparison is needed",
             "Because the map is a HashMap"],
            0,
            "Choosing the right implementation removed the need for a tie-break "
            "comparison entirely."),
    ],
    milestone="You can pick the right structure for membership, counting and lookup, "
              "honour the contract that makes hashing work, and produce output that is "
              "reproducible rather than accidentally ordered.",
))
