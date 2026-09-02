# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 20 practice - ordering, sorting, and choosing.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[20]`.
#
# Lambdas and method references are Part 8 and stay banned, so every Comparator
# here is a NAMED class implementing the interface. That is module 14's material
# doing real work, and worth writing out at least once before the shorthand.
#
# Java's object sort is STABLE, so every ordering below is either total or its
# ties are explicitly broken - no expected output depends on an unspecified
# order.
# ---------------------------------------------------------------------------


_RD_W20 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")

_RD_P20 = ("        int n = sc.nextInt();\n"
           "        List<Person> people = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            people.add(new Person(sc.next(), sc.nextInt()));\n"
           "        }\n")

_PERSON = """
class Person {
    private final String name;
    private final int age;

    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    String name() {
        return name;
    }

    int age() {
        return age;
    }
}
"""


def _p20ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_W20):
    """Blank is the body of `main`."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


def _p20types(eid, title, difficulty, prompt, types, body, tests, hints):
    """Blank is the type(s) above `main`."""
    types = types.strip("\n")
    return _jch(eid, title, difficulty, prompt, _joop(types, body), types,
                tests, hints)


def _w20(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _pcase(rows, out):
    return _case("\n".join([str(len(rows))] + [f"{n} {a}" for (n, a) in rows]), out)


def _jl(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


def _treeset_report(rows):
    """A TreeSet ordered by value keeps the FIRST box of each value, then
    iterates in VALUE order - not insertion order."""
    kept = []
    seen = []
    for (tag, value) in rows:
        if value not in seen:
            seen.append(value)
            kept.append((tag, value))
    kept.sort(key=lambda r: r[1])
    return _nl(len(kept), *[t for (t, _v) in kept])


def _recent_k20(words, k):
    """Most-recently-used list of at most k distinct words, newest first."""
    recent = []
    for w in words:
        if w in recent:
            recent.remove(w)
        recent.insert(0, w)
        if len(recent) > k:
            recent.pop()
    return recent


_WS20 = (["pear", "apple", "fig"], ["solo"], ["c", "b", "a"],
         ["zz", "aa"], ["one", "a", "six", "to"])

_PS20 = ([("Ada", 36), ("Bo", 20)],
         [("solo", 1)],
         [("a", 3), ("b", 1), ("c", 2)],
         [("Bo", 30), ("Ada", 30)],
         [("p", 10), ("q", -1)])


# --- Family A - Comparable -----------------------------------------------------

_P20_A = _jfam(
    "p20-comparable", "`Comparable`",
    "One natural ordering, built into the type.",
    """
```java
class Person implements Comparable<Person> {
    @Override
    public int compareTo(Person other) {
        return Integer.compare(this.age, other.age);
    }
}
```

**Only the sign is specified:**

| Return | Meaning |
|---|---|
| negative | `this` comes **before** `other` |
| zero | tie |
| positive | `this` comes **after** |

Never compare the result to `1` or `-1` — test `< 0`, `== 0`, `> 0`.

**Use `Integer.compare(a, b)`, never `a - b`.** Subtraction overflows:
`2_000_000_000 - (-2_000_000_000)` does not fit in an `int` and wraps to a
negative, reversing the order. `Integer.compare` compiles to the same work
without the hazard, and `Double.compare` also handles `NaN`.

**Delegate for fields that already know how:**

```java
return this.name.compareTo(other.name);      // String is Comparable
```

**The contract:** antisymmetric (`a.compareTo(b)` and `b.compareTo(a)` have
opposite signs), transitive, and *strongly recommended* to be consistent with
`equals`.

That last point has teeth: **`TreeSet` and `TreeMap` use `compareTo`, not
`equals`.** Two objects that compare equal are treated as the same element, so a
`TreeSet` silently keeps only one — where a `HashSet` would keep both. Same data,
two different answers, decided by which collection you chose.
""",
    [
        _p20types("j20-pr-cmp-age", "Order by age", "Medium",
                  "Write a `Person` class implementing `Comparable<Person>`, ordering "
                  "by age ascending with `Integer.compare`. It needs `private final` "
                  "fields, a constructor, `name()` and `age()`.",
                  _PERSON.strip("\n").replace(
                      "class Person {",
                      "class Person implements Comparable<Person> {").replace(
                      "    int age() {\n        return age;\n    }\n}",
                      "    int age() {\n        return age;\n    }\n\n"
                      "    @Override\n"
                      "    public int compareTo(Person other) {\n"
                      "        return Integer.compare(this.age, other.age);\n"
                      "    }\n}"),
                  """        int n = sc.nextInt();
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            people.add(new Person(sc.next(), sc.nextInt()));
        }
        Collections.sort(people);
        for (Person p : people) {
            System.out.println(p.name());
        }""",
                  [_pcase(rows, _nl(*[n for (n, a) in sorted(rows, key=lambda r: r[1])]))
                   for rows in _PS20],
                  ["`implements Comparable<Person>` — the interface is generic.",
                   "`compareTo` must be `public`, because interface methods are.",
                   "`Integer.compare(this.age, other.age)` rather than subtraction.",
                   "`Collections.sort` only accepts a list of Comparable elements.",
                   "Case four is a tie; Java's sort is stable, so the two keep their "
                   "input order."]),

        _p20types("j20-pr-cmp-name", "Order by name", "Easy",
                  "Same `Person` class, but ordering alphabetically by name — "
                  "delegating to `String`'s own ordering.",
                  _PERSON.strip("\n").replace(
                      "class Person {",
                      "class Person implements Comparable<Person> {").replace(
                      "    int age() {\n        return age;\n    }\n}",
                      "    int age() {\n        return age;\n    }\n\n"
                      "    @Override\n"
                      "    public int compareTo(Person other) {\n"
                      "        return this.name.compareTo(other.name);\n"
                      "    }\n}"),
                  """        int n = sc.nextInt();
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            people.add(new Person(sc.next(), sc.nextInt()));
        }
        Collections.sort(people);
        for (Person p : people) {
            System.out.println(p.name());
        }""",
                  [_pcase(rows, _nl(*[n for (n, a) in sorted(rows, key=lambda r: r[0])]))
                   for rows in _PS20],
                  ["`String` already implements `Comparable`, so delegate to it.",
                   "`return this.name.compareTo(other.name);`",
                   "No `Integer.compare` is needed — there is no arithmetic.",
                   "String ordering is by character code, so every capital sorts "
                   "before every lowercase letter."]),

        _p20types("j20-pr-cmp-overflow", "Do not subtract", "Hard",
                  "Write a `Box` class implementing `Comparable<Box>` ordering by "
                  "`value` ascending. Use `Integer.compare` — the test data includes "
                  "values far enough apart that subtraction would overflow. It needs a "
                  "`tag()` accessor.",
                  """
class Box implements Comparable<Box> {
    private final String tag;
    private final int value;

    Box(String tag, int value) {
        this.tag = tag;
        this.value = value;
    }

    String tag() {
        return tag;
    }

    @Override
    public int compareTo(Box other) {
        return Integer.compare(this.value, other.value);
    }
}
""",
                  """        int n = sc.nextInt();
        List<Box> boxes = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            boxes.add(new Box(sc.next(), sc.nextInt()));
        }
        Collections.sort(boxes);
        for (Box b : boxes) {
            System.out.println(b.tag());
        }""",
                  [_pcase(rows, _nl(*[n for (n, v) in sorted(rows, key=lambda r: r[1])]))
                   for rows in ([("big", 2000000000), ("small", -2000000000)],
                                [("a", 1), ("b", 2)],
                                [("x", -2147483648), ("y", 2147483647)],
                                [("p", 0), ("q", 0)],
                                [("m", 5), ("n", -5)])],
                  ["`this.value - other.value` overflows for values far apart and "
                   "returns the wrong sign.",
                   "Cases one and three are exactly that; the small cases would pass "
                   "either way.",
                   "`Integer.compare(this.value, other.value)` cannot overflow.",
                   "That is why the rule is 'always compare, never subtract'."]),

        _p20types("j20-pr-cmp-desc", "Natural order, descending", "Medium",
                  "Write `Box implements Comparable<Box>` ordering by `value` "
                  "DESCENDING, by swapping the arguments to `Integer.compare`.",
                  """
class Box implements Comparable<Box> {
    private final String tag;
    private final int value;

    Box(String tag, int value) {
        this.tag = tag;
        this.value = value;
    }

    String tag() {
        return tag;
    }

    @Override
    public int compareTo(Box other) {
        return Integer.compare(other.value, this.value);
    }
}
""",
                  """        int n = sc.nextInt();
        List<Box> boxes = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            boxes.add(new Box(sc.next(), sc.nextInt()));
        }
        Collections.sort(boxes);
        for (Box b : boxes) {
            System.out.println(b.tag());
        }""",
                  [_pcase(rows, _nl(*[n for (n, v) in sorted(rows, key=lambda r: -r[1])]))
                   for rows in ([("a", 1), ("b", 3), ("c", 2)],
                                [("solo", 5)],
                                [("x", -1), ("y", 1)],
                                [("p", 0), ("q", 0)],
                                [("m", 100), ("n", 50), ("o", 75)])],
                  ["Reversing an ordering means swapping the two arguments.",
                   "`Integer.compare(other.value, this.value)`",
                   "Negating the result would also usually work, but breaks for "
                   "`Integer.MIN_VALUE`, whose negation overflows.",
                   "Ties keep input order, because Java's sort is stable — case four "
                   "checks it."]),

        _p20types("j20-pr-cmp-treeset", "compareTo decides duplicates", "Hard",
                  "Write `Box implements Comparable<Box>` ordering by `value`. `main` "
                  "puts them in a `TreeSet` — so two boxes with the SAME value are "
                  "treated as one element, even though they are different objects.",
                  """
class Box implements Comparable<Box> {
    private final String tag;
    private final int value;

    Box(String tag, int value) {
        this.tag = tag;
        this.value = value;
    }

    String tag() {
        return tag;
    }

    @Override
    public int compareTo(Box other) {
        return Integer.compare(this.value, other.value);
    }
}
""",
                  """        int n = sc.nextInt();
        Set<Box> boxes = new TreeSet<>();
        for (int i = 0; i < n; i++) {
            boxes.add(new Box(sc.next(), sc.nextInt()));
        }
        System.out.println(boxes.size());
        for (Box b : boxes) {
            System.out.println(b.tag());
        }""",
                  [_pcase(rows, _treeset_report(rows))
                   for rows in ([("a", 1), ("b", 2)],
                                [("a", 1), ("b", 1)],
                                [("solo", 5)],
                                [("x", 2), ("y", 1), ("z", 2)],
                                [("p", 0), ("q", 0), ("r", 0)])],
                  ["A `TreeSet` decides sameness with `compareTo`, NOT with "
                   "`equals`.",
                   "So two boxes with equal values collapse into one, and the first "
                   "one added wins.",
                   "Case two adds two boxes with value 1 and keeps only `a`.",
                   "A `HashSet` would have kept both, since it uses equals and "
                   "hashCode — which this class does not override.",
                   "That divergence is why the contract says compareTo SHOULD agree "
                   "with equals.",
                   "The set iterates in sorted order, so the tags come out by "
                   "value."]),
    ])


# --- Family B - Comparator -----------------------------------------------------

_P20_B = _jfam(
    "p20-comparator", "`Comparator`",
    "Ordering as an object, so a type can have many.",
    """
`Comparable` gives a type **one** ordering. A `Comparator` holds one **outside**
the class, so there can be as many as you like — and so you can order types you
do not own:

```java
class ByAge implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return Integer.compare(a.age(), b.age());
    }
}

people.sort(new ByAge());
```

| | `Comparable` | `Comparator` |
|---|---|---|
| Lives | inside the class | outside |
| Method | `compareTo(other)` — one arg | `compare(a, b)` — two |
| How many | one | any number |
| Needs the source | yes | **no** |

**Reversing is a swap:** `Integer.compare(b.age(), a.age())`.

**Tie-breaking is a second comparison, reached only when the first ties:**

```java
int byAge = Integer.compare(a.age(), b.age());
if (byAge != 0) {
    return byAge;                      // decided
}
return a.name().compareTo(b.name());   // tie: fall through
```

*Compute, return if decided, otherwise fall through* — and it chains to as many
keys as you need.

**`compare` must be `public`**, since it comes from an interface. Forgetting is
*attempting to assign weaker access privileges* — module 13's rule again.

> Modern Java writes these as lambdas or `Comparator.comparing(Person::age)`.
> Both are Part 8. Writing the named class makes it obvious that a comparator is
> just an object implementing an interface.
""",
    [
        _p20types("j20-pr-cr-age", "An ordering object", "Medium",
                  "`Person` is NOT Comparable. Write a `ByAge` comparator class "
                  "ordering by age ascending. Write both `Person` and `ByAge`.",
                  _PERSON.strip("\n") + """

class ByAge implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return Integer.compare(a.age(), b.age());
    }
}
""",
                  """        int n = sc.nextInt();
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            people.add(new Person(sc.next(), sc.nextInt()));
        }
        people.sort(new ByAge());
        for (Person p : people) {
            System.out.println(p.name());
        }""",
                  [_pcase(rows, _nl(*[n for (n, a) in sorted(rows, key=lambda r: r[1])]))
                   for rows in _PS20],
                  ["`Person` stays a plain class — the ordering lives entirely "
                   "outside it.",
                   "`class ByAge implements Comparator<Person>`",
                   "`compare` takes TWO arguments and must be `public`.",
                   "`people.sort(new ByAge())` passes an instance of it."]),

        _p20types("j20-pr-cr-desc", "Largest first", "Easy",
                  "Same `Person`. Write a `ByAgeDesc` comparator ordering by age "
                  "DESCENDING.",
                  _PERSON.strip("\n") + """

class ByAgeDesc implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return Integer.compare(b.age(), a.age());
    }
}
""",
                  """        int n = sc.nextInt();
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            people.add(new Person(sc.next(), sc.nextInt()));
        }
        people.sort(new ByAgeDesc());
        for (Person p : people) {
            System.out.println(p.name());
        }""",
                  [_pcase(rows, _nl(*[n for (n, a) in sorted(rows, key=lambda r: -r[1])]))
                   for rows in _PS20],
                  ["Swap the two arguments: `Integer.compare(b.age(), a.age())`.",
                   "Negating the result breaks for `Integer.MIN_VALUE`.",
                   "Ties keep input order because the sort is stable — case four "
                   "checks it.",
                   "Only the comparator differs from the previous variant."]),

        _p20types("j20-pr-cr-length", "Order strings you do not own", "Medium",
                  "Write a `ByLength` comparator over `String`, ordering by length "
                  "ascending and breaking ties alphabetically.",
                  """
class ByLength implements Comparator<String> {
    @Override
    public int compare(String a, String b) {
        int byLen = Integer.compare(a.length(), b.length());
        if (byLen != 0) {
            return byLen;
        }
        return a.compareTo(b);
    }
}
""",
                  """        int n = sc.nextInt();
        List<String> words = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            words.add(sc.next());
        }
        words.sort(new ByLength());
        System.out.println(words);""",
                  [_w20(ws, _jl(sorted(ws, key=lambda w: (len(w), w))))
                   for ws in _WS20],
                  ["You cannot add a `compareTo` to `String`, but you can write a "
                   "comparator for it — that is the whole advantage.",
                   "`implements Comparator<String>`",
                   "Compare lengths first, then fall through to `a.compareTo(b)`.",
                   "Case four has two words of equal length and must come out "
                   "alphabetically."]),

        _p20types("j20-pr-cr-tiebreak", "Break the tie", "Medium",
                  "Same `Person`. Write `ByAgeThenName`, ordering by age ascending and "
                  "then by name alphabetically within each age.",
                  _PERSON.strip("\n") + """

class ByAgeThenName implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        int byAge = Integer.compare(a.age(), b.age());
        if (byAge != 0) {
            return byAge;
        }
        return a.name().compareTo(b.name());
    }
}
""",
                  """        int n = sc.nextInt();
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            people.add(new Person(sc.next(), sc.nextInt()));
        }
        people.sort(new ByAgeThenName());
        for (Person p : people) {
            System.out.println(p.name());
        }""",
                  [_pcase(rows,
                          _nl(*[n for (n, a) in sorted(rows, key=lambda r: (r[1], r[0]))]))
                   for rows in ([("Bo", 30), ("Ada", 30)],
                                [("solo", 1)],
                                [("c", 2), ("a", 2), ("b", 1)],
                                [("z", 5), ("y", 5), ("x", 5)],
                                [("p", 10), ("q", -1)])],
                  ["Compute the first comparison into a variable.",
                   "Return it immediately if non-zero — that decides the order.",
                   "Only on a tie do you fall through to the second key.",
                   "Case one has two people aged 30 in the wrong alphabetical order, "
                   "which is exactly what the tie-break fixes.",
                   "The shape chains to as many keys as you need."]),

        _p20types("j20-pr-cr-two", "Two orderings, one type", "Hard",
                  "Same `Person`. Write BOTH a `ByName` and a `ByAge` comparator. "
                  "`main` sorts by name, prints, then sorts by age and prints again.",
                  _PERSON.strip("\n") + """

class ByName implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return a.name().compareTo(b.name());
    }
}

class ByAge implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return Integer.compare(a.age(), b.age());
    }
}
""",
                  """        int n = sc.nextInt();
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            people.add(new Person(sc.next(), sc.nextInt()));
        }
        people.sort(new ByName());
        for (Person p : people) {
            System.out.println(p.name());
        }
        people.sort(new ByAge());
        for (Person p : people) {
            System.out.println(p.name());
        }""",
                  [_pcase(rows,
                          _nl(*([n for (n, a) in sorted(rows, key=lambda r: r[0])]
                                + [n for (n, a) in sorted(rows, key=lambda r: (r[1], r[0]))])))
                   for rows in _PS20],
                  ["Two comparator classes, both over `Person`, neither touching the "
                   "class itself.",
                   "That is what `Comparable` cannot do: it allows exactly one "
                   "ordering.",
                   "The second sort starts from the name-sorted list. Because the "
                   "sort is STABLE, people of equal age stay in name order — which is "
                   "why the expected output breaks age ties alphabetically.",
                   "That is the two-pass multi-key sort, met by accident.",
                   "Case four is two people aged 30, and the name sort decides their "
                   "final order."]),
    ])


# --- Family C - sorting ---------------------------------------------------------

_P20_C = _jfam(
    "p20-sorting", "Sorting",
    "The calls, and what stability buys.",
    """
```java
Collections.sort(list);          // natural ordering; elements must be Comparable
Collections.sort(list, cmp);     // with a comparator
list.sort(cmp);                  // the modern equivalent
list.sort(null);                 // natural ordering, same method
Arrays.sort(arr);                // arrays too
```

**All of them sort in place and return nothing.** `list = Collections.sort(list)`
does not compile — a useful error to have met once, and the same shape as
`Arrays.fill` and `Arrays.sort` from modules 1 and 3.

**`list.sort(cmp)` is preferred** in new code: a method on `List` rather than a
static utility.

## Stability

Java's **object** sort is stable — elements that compare equal keep their
relative order. Its **primitive** sort is not, and for indistinguishable `int`s
that is meaningless anyway.

Stability is what makes multi-key sorting by repeated passes work:

```java
people.sort(new ByName());     // least significant FIRST
people.sort(new ByAge());      // then most significant
```

Sort by the least significant key first. Doing it the other way round loses the
inner ordering entirely. A single tie-breaking comparator gives the same answer
in one pass and is faster — but knowing *why* the two-pass version works is worth
having.

**`Collections` has more than `sort`:** `reverse`, `shuffle`, `max`, `min`,
`frequency`, `nCopies`, `unmodifiableList`. `max` and `min` take a comparator
too, and both throw on an empty collection.
""",
    [
        _p20ex("j20-pr-sort-natural", "Sort them", "Intro",
               "Print the words sorted alphabetically, as a list.",
               """
        Collections.sort(words);
        System.out.println(words);
""",
               [_w20(ws, _jl(sorted(ws))) for ws in _WS20],
               ["`String` is already `Comparable`, so no comparator is needed.",
                "`Collections.sort(words);` sorts in place and returns nothing.",
                "Print the original list afterwards.",
                "`words.sort(null);` would do exactly the same thing."]),

        _p20ex("j20-pr-sort-inplace", "Keep the original too", "Medium",
               "Print the words in their original order, then a sorted copy — the "
               "original must be unchanged.",
               """
        System.out.println(words);
        List<String> sorted = new ArrayList<>(words);
        Collections.sort(sorted);
        System.out.println(sorted);
""",
               [_w20(ws, _nl(_jl(ws), _jl(sorted(ws)))) for ws in _WS20],
               ["Sorting is in place, so sorting `words` would destroy the order you "
                "still need.",
                "`List<String> copy = words;` would alias, not copy.",
                "`new ArrayList<>(words)` makes a genuine copy.",
                "Sort the copy, and print the original first."]),

        _p20ex("j20-pr-sort-reverse", "Reverse it afterwards", "Easy",
               "Print the words sorted in DESCENDING alphabetical order, using "
               "`Collections.sort` followed by `Collections.reverse`.",
               """
        Collections.sort(words);
        Collections.reverse(words);
        System.out.println(words);
""",
               [_w20(ws, _jl(sorted(ws, reverse=True))) for ws in _WS20],
               ["Sort ascending first, then flip the whole list.",
                "`Collections.reverse` also works in place and returns nothing.",
                "A comparator that swaps its arguments would do it in one pass and is "
                "usually better — this variant is about knowing the utility exists.",
                "Both calls are statements, not expressions."]),

        _p20ex("j20-pr-sort-minmax", "Smallest and largest", "Easy",
               "Print the alphabetically first word, then the last, without sorting the "
               "list.",
               """
        System.out.println(Collections.min(words));
        System.out.println(Collections.max(words));
""",
               [_w20(ws, _nl(min(ws), max(ws))) for ws in _WS20],
               ["`Collections.min` and `max` scan once in O(n) — no sort needed.",
                "They use natural ordering here, and both have overloads taking a "
                "comparator.",
                "Both throw `NoSuchElementException` on an empty collection.",
                "A one-word list gives the same answer twice."]),

        _p20types("j20-pr-sort-twopass", "Two passes, stability at work", "Hard",
                  "Write `ByName` and `ByAge` comparators for the given `Person`. "
                  "`main` sorts by name and THEN by age, relying on stability to break "
                  "age ties alphabetically. Print `name age` per line.",
                  _PERSON.strip("\n") + """

class ByName implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return a.name().compareTo(b.name());
    }
}

class ByAge implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return Integer.compare(a.age(), b.age());
    }
}
""",
                  """        int n = sc.nextInt();
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            people.add(new Person(sc.next(), sc.nextInt()));
        }
        people.sort(new ByName());
        people.sort(new ByAge());
        for (Person p : people) {
            System.out.println(p.name() + " " + p.age());
        }""",
                  [_pcase(rows,
                          _nl(*[f"{n} {a}" for (n, a) in
                                sorted(rows, key=lambda r: (r[1], r[0]))]))
                   for rows in ([("Bo", 30), ("Ada", 30), ("Cy", 20)],
                                [("solo", 1)],
                                [("c", 2), ("a", 2), ("b", 1)],
                                [("z", 5), ("y", 5), ("x", 5)],
                                [("p", 10), ("q", -1)])],
                  ["Sort by the LEAST significant key first — the name.",
                   "Then by the most significant — the age.",
                   "Java's object sort is stable, so the second sort preserves name "
                   "order within each age group.",
                   "Doing it the other way round would lose the name ordering "
                   "entirely.",
                   "A single tie-breaking comparator gives the same answer in one "
                   "pass; this is about understanding why stability matters."]),
    ])


# --- Family D - multi-key -------------------------------------------------------

_P20_D = _jfam(
    "p20-multikey", "Ordering by several keys",
    "Compute, return if decided, fall through.",
    """
```java
public int compare(Person a, Person b) {
    int byAge = Integer.compare(a.age(), b.age());
    if (byAge != 0) {
        return byAge;
    }
    return a.name().compareTo(b.name());
}
```

Three things make this shape work, and all three are easy to get wrong:

**Compute into a variable.** Calling the comparison twice — once to test, once to
return — does the work twice and reads worse.

**Return as soon as it is decided.** A non-zero result is the answer; nothing
after it should run.

**Only the LAST key needs no guard**, because there is nothing to fall through
to.

**Adding a third key is one more block**, always in most-significant-first order.
The keys are tried in the order you write them, which is the opposite of the
two-pass sort where the least significant goes first. Mixing those two rules up
is the standard mistake.

**Make the ordering total.** If the final key can still tie, the result depends
on the input order — which is fine when the sort is stable and you meant it, and
a bug when you did not. Every ordering in these exercises ends in a key that
cannot tie, so the expected output is fully determined.

**Descending on one key only** is still a swap, applied to just that comparison:

```java
int bySalary = Integer.compare(b.salary(), a.salary());   // descending
if (bySalary != 0) return bySalary;
return a.name().compareTo(b.name());                      // ascending
```
""",
    [
        _p20types("j20-pr-mk-len-alpha", "Length, then alphabet", "Medium",
                  "Write `ByLengthThenAlpha` over `String`: shorter first, ties broken "
                  "alphabetically.",
                  """
class ByLengthThenAlpha implements Comparator<String> {
    @Override
    public int compare(String a, String b) {
        int byLen = Integer.compare(a.length(), b.length());
        if (byLen != 0) {
            return byLen;
        }
        return a.compareTo(b);
    }
}
""",
                  """        int n = sc.nextInt();
        List<String> words = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            words.add(sc.next());
        }
        words.sort(new ByLengthThenAlpha());
        System.out.println(words);""",
                  [_w20(ws, _jl(sorted(ws, key=lambda w: (len(w), w))))
                   for ws in _WS20],
                  ["Compute the length comparison into a variable first.",
                   "Return it if non-zero; otherwise fall through.",
                   "The last key needs no guard, because nothing follows it.",
                   "Case four has two two-letter words and must come out "
                   "alphabetically."]),

        _p20types("j20-pr-mk-desc-then", "Descending, then ascending", "Medium",
                  "Write `ByAgeDescThenName` over the given `Person`: age DESCENDING, "
                  "ties broken by name ASCENDING.",
                  _PERSON.strip("\n") + """

class ByAgeDescThenName implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        int byAge = Integer.compare(b.age(), a.age());
        if (byAge != 0) {
            return byAge;
        }
        return a.name().compareTo(b.name());
    }
}
""",
                  """        int n = sc.nextInt();
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            people.add(new Person(sc.next(), sc.nextInt()));
        }
        people.sort(new ByAgeDescThenName());
        for (Person p : people) {
            System.out.println(p.name() + " " + p.age());
        }""",
                  [_pcase(rows, _nl(*[f"{n} {a}" for (n, a) in
                                      sorted(rows, key=lambda r: (-r[1], r[0]))]))
                   for rows in ([("Bo", 30), ("Ada", 30), ("Cy", 20)],
                                [("solo", 1)],
                                [("c", 2), ("a", 2), ("b", 1)],
                                [("z", 5), ("y", 5), ("x", 5)],
                                [("p", 10), ("q", -1)])],
                  ["Each key gets its own direction: swap the arguments for the "
                   "descending one only.",
                   "`Integer.compare(b.age(), a.age())` descending, then "
                   "`a.name().compareTo(b.name())` ascending.",
                   "Mixing directions is exactly why comparators beat a single "
                   "`compareTo`.",
                   "Case four is three people of the same age, ordered by name."]),

        _p20types("j20-pr-mk-three", "Three keys deep", "Hard",
                  "Write a `Rec` class with `private final String name`, "
                  "`private final int group`, `private final int score`, accessors, and "
                  "a `ByAll` comparator ordering by group ascending, then score "
                  "DESCENDING, then name ascending.",
                  """
class Rec {
    private final String name;
    private final int group;
    private final int score;

    Rec(String name, int group, int score) {
        this.name = name;
        this.group = group;
        this.score = score;
    }

    String name() {
        return name;
    }

    int group() {
        return group;
    }

    int score() {
        return score;
    }
}

class ByAll implements Comparator<Rec> {
    @Override
    public int compare(Rec a, Rec b) {
        int byGroup = Integer.compare(a.group(), b.group());
        if (byGroup != 0) {
            return byGroup;
        }
        int byScore = Integer.compare(b.score(), a.score());
        if (byScore != 0) {
            return byScore;
        }
        return a.name().compareTo(b.name());
    }
}
""",
                  """        int n = sc.nextInt();
        List<Rec> recs = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            recs.add(new Rec(sc.next(), sc.nextInt(), sc.nextInt()));
        }
        recs.sort(new ByAll());
        for (Rec r : recs) {
            System.out.println(r.name() + " " + r.group() + " " + r.score());
        }""",
                  [_case("\n".join([str(len(rows))]
                                   + [f"{nm} {g} {s}" for (nm, g, s) in rows]),
                         _nl(*[f"{nm} {g} {s}" for (nm, g, s) in
                               sorted(rows, key=lambda r: (r[1], -r[2], r[0]))]))
                   for rows in ([("a", 1, 10), ("b", 1, 20), ("c", 2, 5)],
                                [("solo", 3, 3)],
                                [("x", 1, 5), ("y", 1, 5)],
                                [("p", 2, 1), ("q", 1, 1)],
                                [("m", 1, 9), ("n", 1, 9), ("o", 1, 1)])],
                  ["Three blocks, most significant first.",
                   "Only the middle key is descending, so only it swaps its "
                   "arguments.",
                   "Each of the first two returns early when decided; the last needs "
                   "no guard.",
                   "Case three and five have full ties on the first two keys, so the "
                   "name decides.",
                   "The ordering is total, so the output does not depend on input "
                   "order at all."]),

        _p20types("j20-pr-mk-treeset", "A comparator decides duplicates", "Hard",
                  "Write `ByLength` over `String` — ordering ONLY by length, with no "
                  "tie-break. `main` puts the words in a `TreeSet` built with it, so "
                  "words of equal length collapse into one element.",
                  """
class ByLength implements Comparator<String> {
    @Override
    public int compare(String a, String b) {
        return Integer.compare(a.length(), b.length());
    }
}
""",
                  """        int n = sc.nextInt();
        Set<String> set = new TreeSet<>(new ByLength());
        for (int i = 0; i < n; i++) {
            set.add(sc.next());
        }
        System.out.println(set.size());
        System.out.println(set);""",
                  [_w20(ws, (lambda kept: _nl(len(kept), _jl(kept)))(
                      sorted((lambda: [w for (i, w) in enumerate(ws)
                                       if len(w) not in [len(x) for x in ws[:i]]])(),
                             key=len)))
                   for ws in _WS20],
                  ["A sorted collection built with a comparator uses that comparator "
                   "to decide DUPLICATES as well as order.",
                   "This one ties any two words of the same length, so the set keeps "
                   "only the first of each length.",
                   "That is a real bug when unintended — and here it is the point of "
                   "the exercise.",
                   "Adding a `a.compareTo(b)` tie-break would keep them all.",
                   "The size therefore counts distinct LENGTHS, not distinct words."]),

        _p20types("j20-pr-mk-stable-check", "When the ordering is not total", "Hard",
                  "Write `ByAgeOnly` over the given `Person`, comparing ages and "
                  "nothing else. `main` sorts and prints — people of equal age keep "
                  "their INPUT order, because Java's sort is stable.",
                  _PERSON.strip("\n") + """

class ByAgeOnly implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return Integer.compare(a.age(), b.age());
    }
}
""",
                  """        int n = sc.nextInt();
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            people.add(new Person(sc.next(), sc.nextInt()));
        }
        people.sort(new ByAgeOnly());
        for (Person p : people) {
            System.out.println(p.name() + " " + p.age());
        }""",
                  [_pcase(rows, _nl(*[f"{n} {a}" for (n, a) in
                                      sorted(rows, key=lambda r: r[1])]))
                   for rows in ([("Bo", 30), ("Ada", 30), ("Cy", 20)],
                                [("solo", 1)],
                                [("c", 2), ("a", 2), ("b", 1)],
                                [("z", 5), ("y", 5), ("x", 5)],
                                [("p", 10), ("q", -1)])],
                  ["The ordering is not total: several people can compare equal.",
                   "Python's `sorted` and Java's `List.sort` are BOTH stable, which "
                   "is why the expected output is well defined at all.",
                   "Case one keeps `Bo` before `Ada`, because that was the input "
                   "order — not alphabetical.",
                   "If you want alphabetical there, add a tie-break; relying on "
                   "stability for a rule you actually care about is fragile.",
                   "Case four is three people of one age, all keeping input order."]),
    ])


# --- Family E - choosing --------------------------------------------------------

_P20_E = _jfam(
    "p20-choosing", "Choosing a collection",
    "The decision, and what it costs to get wrong.",
    """
| Your question | Reach for |
|---|---|
| What is at position `i`? | `ArrayList` |
| Have I seen this? | `HashSet` |
| What is associated with this key? | `HashMap` |
| What arrived first? | `ArrayDeque` as a queue |
| What was most recent? | `ArrayDeque` as a stack |
| What is smallest right now? | `PriorityQueue` |
| …and I need it in order? | `LinkedHash*` (insertion) or `Tree*` (sorted) |

**The six rules:**

1. **Default to `ArrayList` and `HashMap`.**
2. **Reach for a `Set` the moment `list.contains(x)` appears inside a loop** —
   O(n²) becomes O(n), and it is the most common performance fix in everyday
   Java.
3. **Program to the interface**, so changing your mind costs one line.
4. **If output order matters, put it in the type** rather than sorting
   afterwards.
5. **Never `Vector` or `java.util.Stack`.**
6. **Honour `equals`/`hashCode`** for set elements and map keys, and do not
   mutate them afterwards.

**Sorting versus a sorted collection.** If you build once and read once, sort at
the end. If you insert and read repeatedly, a `TreeMap` or `TreeSet` keeps the
order for you at O(log n) per operation rather than re-sorting at O(n log n)
each time.

**Sorting versus a heap.** If you need everything in order, sort. If you only
need the extreme — the smallest, the top k — a heap is better, and the k-largest
idiom is O(n log k) against O(n log n).
""",
    [
        _p20ex("j20-pr-ch-contains", "Set instead of list", "Medium",
               "Read `n` known words, then `m` queries. Print `yes` or `no` per query, "
               "using a set so each lookup is O(1).",
               """
        Set<String> known = new HashSet<>(words);
        int m = sc.nextInt();
        for (int i = 0; i < m; i++) {
            if (known.contains(sc.next())) {
                System.out.println("yes");
            } else {
                System.out.println("no");
            }
        }
""",
               [_case("\n".join([str(len(ks)), " ".join(ks),
                                 str(len(qs)), " ".join(qs)]),
                      _nl(*["yes" if q in ks else "no" for q in qs]))
                for (ks, qs) in ((["a", "b"], ["a", "c"]),
                                 (["solo"], ["solo"]),
                                 (["x", "y", "z"], ["y", "w"]),
                                 (["p"], ["q"]),
                                 (["dog", "cat"], ["cat", "ant"]))],
               ["`new HashSet<>(words)` converts in one line.",
                "`contains` is O(1) on a set against O(n) on the list.",
                "With n known words and m queries that is O(n + m) instead of "
                "O(n * m).",
                "Nothing is printed as a collection, so a HashSet's order never "
                "matters."]),

        _p20ex("j20-pr-ch-sorted-report", "Put the order in the type", "Medium",
               "Count the words and print `word=count` per line in alphabetical order — "
               "with no sorting step.",
               """
        Map<String, Integer> counts = new TreeMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        for (Map.Entry<String, Integer> e : counts.entrySet()) {
            System.out.println(e.getKey() + "=" + e.getValue());
        }
""",
               [_w20(ws, _nl(*[f"{k}={ws.count(k)}" for k in sorted(set(ws))]))
                for ws in _WS20],
               ["A `TreeMap` arrives sorted; a `HashMap` would need a separate "
                "sorting step.",
                "That is rule 4: if output order matters, put it in the type.",
                "The counting idiom is unchanged — only the constructor differs.",
                "Walk `entrySet()` so key and value come together."]),

        _p20ex("j20-pr-ch-topk", "Heap instead of sort", "Hard",
               "Read `n` words, then `k`. Print the `k` alphabetically LAST words in "
               "ascending order, one per line, keeping a heap of at most `k`.",
               """
        int k = sc.nextInt();
        Queue<String> pq = new PriorityQueue<>();
        for (String w : words) {
            pq.offer(w);
            if (pq.size() > k) {
                pq.poll();
            }
        }
        while (!pq.isEmpty()) {
            System.out.println(pq.poll());
        }
""",
               [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                      _nl(*sorted(ws)[len(ws) - k:]))
                for (ws, k) in ((["pear", "apple", "fig"], 2), (["solo"], 1),
                                (["c", "b", "a"], 3), (["zz", "aa"], 1),
                                (["one", "six", "two"], 2))],
               ["A MIN-heap capped at `k` keeps the k LARGEST — the head is the "
                "smallest survivor, which is the one to discard.",
                "`String` has a natural ordering, so no comparator is needed.",
                "Draining gives ascending order, which is what the brief asks for.",
                "O(n log k) rather than O(n log n) — worth it when n is huge and k is "
                "small.",
                "Duplicates count separately."]),

        _p20ex("j20-pr-ch-recent", "Deque instead of list", "Hard",
               "Read the words, then `k`. Print the last `k` DISTINCT words, most "
               "recent first, one per line. A repeat moves a word to the front.",
               """
        int k = sc.nextInt();
        Deque<String> recent = new ArrayDeque<>();
        for (String w : words) {
            recent.remove(w);
            recent.addFirst(w);
            if (recent.size() > k) {
                recent.removeLast();
            }
        }
        while (!recent.isEmpty()) {
            System.out.println(recent.pollFirst());
        }
""",
               [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                      _nl(*_recent_k20(ws, k)))
                for (ws, k) in ((["a", "b", "a", "c"], 2), (["solo"], 3),
                                (["x", "y", "z"], 2), (["p", "p", "p"], 1),
                                (["a", "b", "c", "d"], 3))],
               ["A deque gives both ends: newest at the front, oldest at the back.",
                "`remove(w)` first drops any earlier position, so a repeat MOVES "
                "rather than duplicating.",
                "`addFirst(w)` puts it at the most-recent end.",
                "Trim with `removeLast()` past `k`.",
                "This is the shape of a 'recently opened' list and of an LRU cache."]),

        _p20ex("j20-pr-ch-all", "Pick one of each", "Hard",
               "Read the words. Print four lines: the count of distinct words; the "
               "distinct words sorted; the first word that never repeats (or `none`); "
               "and the alphabetically last word.",
               """
        Set<String> distinct = new TreeSet<>(words);
        System.out.println(distinct.size());
        System.out.println(distinct);
        Map<String, Integer> counts = new LinkedHashMap<>();
        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }
        String unique = "none";
        for (Map.Entry<String, Integer> e : counts.entrySet()) {
            if (e.getValue() == 1) {
                unique = e.getKey();
                break;
            }
        }
        System.out.println(unique);
        System.out.println(Collections.max(words));
""",
               [_w20(ws, _nl(len(set(ws)), _jl(sorted(set(ws))),
                             next((w for w in dict.fromkeys(ws)
                                   if ws.count(w) == 1), "none"),
                             max(ws)))
                for ws in (["pear", "apple", "pear"], ["solo"], ["c", "b", "a"],
                           ["x", "x"], ["one", "a", "one", "six"])],
               ["Four questions, and each wants a different structure — that is the "
                "whole exercise.",
                "Distinct and sorted: a `TreeSet`, which gives both the count and the "
                "bracketed printout.",
                "First non-repeating: a `LinkedHashMap`, because the question is "
                "about FIRST-SEEN order. A TreeMap would give alphabetical and a "
                "HashMap nothing reliable.",
                "Alphabetically last: `Collections.max`, an O(n) scan with no sort.",
                "Case four has no unique word and must print `none`."]),
    ])


_PRACTICE[20] = [_P20_A, _P20_B, _P20_C, _P20_D, _P20_E]
