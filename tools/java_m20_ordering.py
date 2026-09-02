# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 20 - Ordering, sorting, and choosing a collection.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# Closes Part 6. `Comparable`, `Comparator` and `Collections.` become legal
# here. Lambdas and method references are Part 8 and stay banned, so every
# Comparator in this module is a NAMED class implementing the interface -
# which is module 14's material doing real work, and is worth writing out at
# least once before the shorthand arrives.
# ---------------------------------------------------------------------------

_M20 = []


def _recent_k(words, k):
    """Mirror of the deque-based most-recently-used list: remove any earlier
    sighting, push to the front, and trim the oldest past k."""
    recent = []
    for w in words:
        if w in recent:
            recent.remove(w)
        recent.insert(0, w)
        if len(recent) > k:
            recent.pop()
    return recent


# --- 20.1 Comparable --------------------------------------------------------

_M20.append(_jlesson(
    "m20-comparable", "`Comparable`",
    "A type's own natural ordering.",
    """
`Integer` sorts ascending and `String` sorts alphabetically because both
implement **`Comparable`**:

```java
class Person implements Comparable<Person> {
    private final String name;
    private final int age;

    @Override
    public int compareTo(Person other) {
        return Integer.compare(this.age, other.age);   // by age, ascending
    }
}
```

**The return value is a sign, not a number:**

| Return | Meaning |
|---|---|
| negative | `this` comes **before** `other` |
| zero | they tie |
| positive | `this` comes **after** `other` |

Only the sign is specified, so never compare the result to `1` or `-1` — test
`< 0`, `== 0`, `> 0`.

**Use `Integer.compare(a, b)`, not `a - b`.** Subtraction is the classic bug: it
overflows. `Integer.compare(2_000_000_000, -2_000_000_000)` is correct;
`a - b` wraps around to a negative and reverses the order. `Integer.compare`
compiles to the same thing without the hazard, and `Double.compare` additionally
handles `NaN`.

**Delegate for fields that are already comparable:**

```java
return this.name.compareTo(other.name);     // String already knows how
```

## The contract

- **Antisymmetric:** `a.compareTo(b)` and `b.compareTo(a)` must have opposite
  signs.
- **Transitive:** if `a < b` and `b < c` then `a < c`.
- **Consistent with `equals`** — *strongly recommended*, not required.
  `compareTo` returning `0` should mean the same as `equals` returning `true`.

That last one matters because **`TreeSet` and `TreeMap` use `compareTo`, not
`equals`**. If two objects compare equal, a `TreeSet` treats them as the same
element and silently keeps only one — even if `equals` says they differ. A
`HashSet` would keep both. Same data, two different answers, decided entirely by
which collection you picked.
""",
    warmup=[
        _jq("What does a negative return from `compareTo` mean?",
            ["this comes before other", "this comes after other", "they are equal",
             "an error"],
            0,
            "Only the SIGN is specified - never test against -1."),
        _jq("Why use `Integer.compare(a, b)` rather than `a - b`?",
            ["Subtraction can overflow and reverse the answer for large values",
             "It is faster",
             "a - b does not compile",
             "There is no difference"],
            0,
            "A classic bug that only appears with values near the int limits."),
    ],
    exercises=[
        _je("j20-cmp-implements", "Give a type its natural order",
            "`Person` should sort by age. Replace `____` with the class declaration "
            "that promises a natural ordering.",
            _joop("class Person implements Comparable<Person> {\n"
                  "    private final String name;\n"
                  "    private final int age;\n"
                  "\n"
                  "    Person(String name, int age) {\n"
                  "        this.name = name;\n"
                  "        this.age = age;\n"
                  "    }\n"
                  "\n"
                  "    String name() {\n"
                  "        return name;\n"
                  "    }\n"
                  "\n"
                  "    @Override\n"
                  "    public int compareTo(Person other) {\n"
                  "        return Integer.compare(this.age, other.age);\n"
                  "    }\n"
                  "}",
                  "        int n = sc.nextInt();\n"
                  "        List<Person> people = new ArrayList<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            people.add(new Person(sc.next(), sc.nextInt()));\n"
                  "        }\n"
                  "        Collections.sort(people);\n"
                  "        for (Person p : people) {\n"
                  "            System.out.println(p.name());\n"
                  "        }"),
            "class Person implements Comparable<Person> {",
            [_case("\n".join([str(len(rows))] + [f"{nm} {ag}" for (nm, ag) in rows]),
                   _nl(*[nm for (nm, ag) in sorted(rows, key=lambda r: r[1])]))
             for rows in ([("Ada", 36), ("Bo", 20)],
                          [("solo", 1)],
                          [("a", 3), ("b", 1), ("c", 2)],
                          [("x", 5), ("y", 5)],
                          [("p", 10), ("q", -1)])],
            hints=["The interface is generic: it takes the type being compared.",
                   "`class Person implements Comparable<Person> {`",
                   "`compareTo` must be `public`, because interface methods are.",
                   "`Collections.sort` only accepts a list whose elements are "
                   "Comparable.",
                   "Case four is a tie, and Java's sort is stable, so the two stay in "
                   "input order."],
            difficulty="Medium"),

        _je("j20-cmp-compare", "Compare without overflowing",
            "Replace `____` with the body of `compareTo`, ordering by `age` ascending "
            "using the overflow-safe helper rather than subtraction.",
            _joop("class Person implements Comparable<Person> {\n"
                  "    private final String name;\n"
                  "    private final int age;\n"
                  "\n"
                  "    Person(String name, int age) {\n"
                  "        this.name = name;\n"
                  "        this.age = age;\n"
                  "    }\n"
                  "\n"
                  "    String name() {\n"
                  "        return name;\n"
                  "    }\n"
                  "\n"
                  "    @Override\n"
                  "    public int compareTo(Person other) {\n"
                  "        return Integer.compare(this.age, other.age);\n"
                  "    }\n"
                  "}",
                  "        int n = sc.nextInt();\n"
                  "        List<Person> people = new ArrayList<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            people.add(new Person(sc.next(), sc.nextInt()));\n"
                  "        }\n"
                  "        Collections.sort(people);\n"
                  "        for (Person p : people) {\n"
                  "            System.out.println(p.name());\n"
                  "        }"),
            "        return Integer.compare(this.age, other.age);",
            [_case("\n".join([str(len(rows))] + [f"{nm} {ag}" for (nm, ag) in rows]),
                   _nl(*[nm for (nm, ag) in sorted(rows, key=lambda r: r[1])]))
             for rows in ([("Ada", 36), ("Bo", 20)],
                          [("solo", 1)],
                          [("a", 2000000000), ("b", -2000000000)],
                          [("x", 5), ("y", 5)],
                          [("p", 10), ("q", -1)])],
            hints=["`this.age - other.age` looks right and overflows.",
                   "Case three is exactly that: the difference does not fit in an "
                   "`int`, and subtraction gives the wrong sign.",
                   "`Integer.compare(this.age, other.age)`",
                   "It returns a negative, zero or positive number — the sign is all "
                   "that matters."],
            difficulty="Medium"),

        _jfix("j20-cmp-subtract", "The comparison that overflowed",
              "This orders by `value` using subtraction, which overflows for values far "
              "apart and puts them in the wrong order. Replace it with the "
              "overflow-safe comparison.",
              _joop("class Box implements Comparable<Box> {\n"
                    "    private final String tag;\n"
                    "    private final int value;\n"
                    "\n"
                    "    Box(String tag, int value) {\n"
                    "        this.tag = tag;\n"
                    "        this.value = value;\n"
                    "    }\n"
                    "\n"
                    "    String tag() {\n"
                    "        return tag;\n"
                    "    }\n"
                    "\n"
                    "    @Override\n"
                    "    public int compareTo(Box other) {\n"
                    "        return this.value - other.value;\n"
                    "    }\n"
                    "}",
                    "        int n = sc.nextInt();\n"
                    "        List<Box> boxes = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            boxes.add(new Box(sc.next(), sc.nextInt()));\n"
                    "        }\n"
                    "        Collections.sort(boxes);\n"
                    "        for (Box b : boxes) {\n"
                    "            System.out.println(b.tag());\n"
                    "        }"),
              _joop("class Box implements Comparable<Box> {\n"
                    "    private final String tag;\n"
                    "    private final int value;\n"
                    "\n"
                    "    Box(String tag, int value) {\n"
                    "        this.tag = tag;\n"
                    "        this.value = value;\n"
                    "    }\n"
                    "\n"
                    "    String tag() {\n"
                    "        return tag;\n"
                    "    }\n"
                    "\n"
                    "    @Override\n"
                    "    public int compareTo(Box other) {\n"
                    "        return Integer.compare(this.value, other.value);\n"
                    "    }\n"
                    "}",
                    "        int n = sc.nextInt();\n"
                    "        List<Box> boxes = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            boxes.add(new Box(sc.next(), sc.nextInt()));\n"
                    "        }\n"
                    "        Collections.sort(boxes);\n"
                    "        for (Box b : boxes) {\n"
                    "            System.out.println(b.tag());\n"
                    "        }"),
              [_case("\n".join([str(len(rows))] + [f"{nm} {v}" for (nm, v) in rows]),
                     _nl(*[nm for (nm, v) in sorted(rows, key=lambda r: r[1])]))
               for rows in ([("big", 2000000000), ("small", -2000000000)],
                            [("a", 1), ("b", 2)],
                            [("x", -2147483648), ("y", 2147483647)],
                            [("p", 0), ("q", 0)],
                            [("m", 5), ("n", -5)])],
              hints=["`2000000000 - (-2000000000)` is 4 billion, which does not fit "
                     "in an `int` — it wraps to a negative.",
                     "So the comparison claims the larger value comes first.",
                     "Cases one and three are the ones that expose it; the small "
                     "cases pass either way.",
                     "`Integer.compare(this.value, other.value)` cannot overflow.",
                     "Nothing else changes."],
              difficulty="Medium"),

        _jch("j20-cmp-string", "Order by a String field", "Easy",
             "Make `Person` sort alphabetically by name by delegating to `String`'s own "
             "ordering. Write the whole class where you see `____`; it needs the two "
             "fields, a constructor, `String name()`, and `compareTo`.",
             _joop("class Person implements Comparable<Person> {\n"
                   "    private final String name;\n"
                   "    private final int age;\n"
                   "\n"
                   "    Person(String name, int age) {\n"
                   "        this.name = name;\n"
                   "        this.age = age;\n"
                   "    }\n"
                   "\n"
                   "    String name() {\n"
                   "        return name;\n"
                   "    }\n"
                   "\n"
                   "    @Override\n"
                   "    public int compareTo(Person other) {\n"
                   "        return this.name.compareTo(other.name);\n"
                   "    }\n"
                   "}",
                   "        int n = sc.nextInt();\n"
                   "        List<Person> people = new ArrayList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            people.add(new Person(sc.next(), sc.nextInt()));\n"
                   "        }\n"
                   "        Collections.sort(people);\n"
                   "        for (Person p : people) {\n"
                   "            System.out.println(p.name());\n"
                   "        }"),
             "class Person implements Comparable<Person> {\n"
             "    private final String name;\n"
             "    private final int age;\n"
             "\n"
             "    Person(String name, int age) {\n"
             "        this.name = name;\n"
             "        this.age = age;\n"
             "    }\n"
             "\n"
             "    String name() {\n"
             "        return name;\n"
             "    }\n"
             "\n"
             "    @Override\n"
             "    public int compareTo(Person other) {\n"
             "        return this.name.compareTo(other.name);\n"
             "    }\n"
             "}",
             [_case("\n".join([str(len(rows))] + [f"{nm} {ag}" for (nm, ag) in rows]),
                    _nl(*[nm for (nm, ag) in sorted(rows, key=lambda r: r[0])]))
              for rows in ([("Bo", 20), ("Ada", 36)],
                           [("solo", 1)],
                           [("c", 1), ("a", 2), ("b", 3)],
                           [("Zed", 5), ("apple", 5)],
                           [("p", 1), ("q", 2)])],
             hints=["`String` already implements `Comparable`, so delegate to it.",
                    "`return this.name.compareTo(other.name);`",
                    "Both fields are `private final`, assigned in the constructor.",
                    "`compareTo` must be `public`; `name()` need not be.",
                    "Case four mixes cases: `compareTo` on String is by character "
                    "code, so every capital sorts before every lowercase letter."]),
    ],
    quiz=[
        _jq("Which collection uses compareTo rather than equals to decide sameness?",
            ["TreeSet", "HashSet", "ArrayList", "LinkedHashSet"],
            0,
            "So two objects that compare equal collapse into one, even if equals says "
            "they differ."),
        _jq("What is required of `a.compareTo(b)` and `b.compareTo(a)`?",
            ["They must have opposite signs", "They must be equal",
             "Both must be positive", "Nothing"],
            0,
            "Antisymmetry. Breaking it makes sorts produce nonsense or throw."),
    ],
))


# --- 20.2 Comparator --------------------------------------------------------

_M20.append(_jlesson(
    "m20-comparator", "`Comparator`",
    "Ordering as a separate object, so a type can have many.",
    """
`Comparable` gives a type **one** ordering, baked in. But people are sorted by
name in one screen and by age in another, and you may not even own the class.

A **`Comparator`** is an ordering held separately:

```java
class ByAge implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return Integer.compare(a.age(), b.age());
    }
}

people.sort(new ByAge());
```

**The differences from `Comparable`:**

| | `Comparable` | `Comparator` |
|---|---|---|
| Lives | inside the class | outside it |
| Method | `compareTo(other)` — one argument | `compare(a, b)` — two |
| How many | one per type | as many as you like |
| Needs the source | yes | **no** |

The return value means the same thing, and `Integer.compare` is still how you
build it safely.

**Reversing is one line:** swap the arguments.

```java
return Integer.compare(b.age(), a.age());     // descending
```

**Tie-breaking is a second comparison**, only reached when the first ties:

```java
public int compare(Person a, Person b) {
    int byAge = Integer.compare(a.age(), b.age());
    if (byAge != 0) {
        return byAge;                      // decided
    }
    return a.name().compareTo(b.name());   // tie: fall back to name
}
```

That shape — *compare, return if decided, otherwise fall through* — extends to
as many keys as you need, and it is exactly what the capstone asks for.

> In modern Java a comparator is usually a lambda or
> `Comparator.comparing(Person::age)`. Both are Part 8. Writing the named class
> once makes it obvious that a comparator is *just an object implementing an
> interface* — module 14's material, doing real work.
""",
    warmup=[
        _jq("How many Comparators can a type have?",
            ["Any number", "One", "One per field", "None if it is Comparable"],
            0,
            "That is the whole point: Comparable gives one ordering, Comparator gives "
            "as many as you need."),
        _jq("How do you reverse a Comparator's ordering?",
            ["Swap the two arguments in the comparison",
             "Negate the field values",
             "Return the opposite boolean",
             "You cannot"],
            0,
            "`Integer.compare(b.x(), a.x())` instead of `Integer.compare(a.x(), "
            "b.x())`."),
    ],
    exercises=[
        _je("j20-cr-implements", "An ordering object",
            "Replace `____` with the declaration of a comparator class that orders "
            "`Person`s.",
            _joop("class Person {\n"
                  "    private final String name;\n"
                  "    private final int age;\n"
                  "\n"
                  "    Person(String name, int age) {\n"
                  "        this.name = name;\n"
                  "        this.age = age;\n"
                  "    }\n"
                  "\n"
                  "    String name() {\n"
                  "        return name;\n"
                  "    }\n"
                  "\n"
                  "    int age() {\n"
                  "        return age;\n"
                  "    }\n"
                  "}\n"
                  "\n"
                  "class ByAge implements Comparator<Person> {\n"
                  "    @Override\n"
                  "    public int compare(Person a, Person b) {\n"
                  "        return Integer.compare(a.age(), b.age());\n"
                  "    }\n"
                  "}",
                  "        int n = sc.nextInt();\n"
                  "        List<Person> people = new ArrayList<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            people.add(new Person(sc.next(), sc.nextInt()));\n"
                  "        }\n"
                  "        people.sort(new ByAge());\n"
                  "        for (Person p : people) {\n"
                  "            System.out.println(p.name());\n"
                  "        }"),
            "class ByAge implements Comparator<Person> {",
            [_case("\n".join([str(len(rows))] + [f"{nm} {ag}" for (nm, ag) in rows]),
                   _nl(*[nm for (nm, ag) in sorted(rows, key=lambda r: r[1])]))
             for rows in ([("Ada", 36), ("Bo", 20)],
                          [("solo", 1)],
                          [("a", 3), ("b", 1), ("c", 2)],
                          [("x", 5), ("y", 5)],
                          [("p", 10), ("q", -1)])],
            hints=["A comparator is an ordinary class implementing a generic "
                   "interface.",
                   "`class ByAge implements Comparator<Person> {`",
                   "`Person` itself is NOT Comparable here — the ordering lives "
                   "entirely outside it.",
                   "`compare` takes TWO arguments and must be `public`."],
            difficulty="Medium"),

        _je("j20-cr-reverse", "Largest first",
            "Replace `____` with the body of `compare` so the list comes out in "
            "DESCENDING age order.",
            _joop("class Person {\n"
                  "    private final String name;\n"
                  "    private final int age;\n"
                  "\n"
                  "    Person(String name, int age) {\n"
                  "        this.name = name;\n"
                  "        this.age = age;\n"
                  "    }\n"
                  "\n"
                  "    String name() {\n"
                  "        return name;\n"
                  "    }\n"
                  "\n"
                  "    int age() {\n"
                  "        return age;\n"
                  "    }\n"
                  "}\n"
                  "\n"
                  "class ByAgeDesc implements Comparator<Person> {\n"
                  "    @Override\n"
                  "    public int compare(Person a, Person b) {\n"
                  "        return Integer.compare(b.age(), a.age());\n"
                  "    }\n"
                  "}",
                  "        int n = sc.nextInt();\n"
                  "        List<Person> people = new ArrayList<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            people.add(new Person(sc.next(), sc.nextInt()));\n"
                  "        }\n"
                  "        people.sort(new ByAgeDesc());\n"
                  "        for (Person p : people) {\n"
                  "            System.out.println(p.name());\n"
                  "        }"),
            "        return Integer.compare(b.age(), a.age());",
            [_case("\n".join([str(len(rows))] + [f"{nm} {ag}" for (nm, ag) in rows]),
                   _nl(*[nm for (nm, ag) in sorted(rows, key=lambda r: -r[1])]))
             for rows in ([("Ada", 36), ("Bo", 20)],
                          [("solo", 1)],
                          [("a", 3), ("b", 1), ("c", 2)],
                          [("x", 5), ("y", 5)],
                          [("p", 10), ("q", -1)])],
            hints=["Reversing an ordering means swapping the two arguments.",
                   "`Integer.compare(b.age(), a.age())`",
                   "Negating the result would also work but breaks for "
                   "`Integer.MIN_VALUE`, whose negation overflows.",
                   "Ties keep input order, because Java's sort is stable — case four "
                   "checks it."],
            difficulty="Easy"),

        _jfix("j20-cr-tiebreak", "The tie that was never broken",
              "This orders by age but ignores ties, so equal ages come out in input "
              "order. Add a tie-break so that people of the same age are ordered by "
              "name.",
              _joop("class Person {\n"
                    "    private final String name;\n"
                    "    private final int age;\n"
                    "\n"
                    "    Person(String name, int age) {\n"
                    "        this.name = name;\n"
                    "        this.age = age;\n"
                    "    }\n"
                    "\n"
                    "    String name() {\n"
                    "        return name;\n"
                    "    }\n"
                    "\n"
                    "    int age() {\n"
                    "        return age;\n"
                    "    }\n"
                    "}\n"
                    "\n"
                    "class ByAgeThenName implements Comparator<Person> {\n"
                    "    @Override\n"
                    "    public int compare(Person a, Person b) {\n"
                    "        return Integer.compare(a.age(), b.age());\n"
                    "    }\n"
                    "}",
                    "        int n = sc.nextInt();\n"
                    "        List<Person> people = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            people.add(new Person(sc.next(), sc.nextInt()));\n"
                    "        }\n"
                    "        people.sort(new ByAgeThenName());\n"
                    "        for (Person p : people) {\n"
                    "            System.out.println(p.name());\n"
                    "        }"),
              _joop("class Person {\n"
                    "    private final String name;\n"
                    "    private final int age;\n"
                    "\n"
                    "    Person(String name, int age) {\n"
                    "        this.name = name;\n"
                    "        this.age = age;\n"
                    "    }\n"
                    "\n"
                    "    String name() {\n"
                    "        return name;\n"
                    "    }\n"
                    "\n"
                    "    int age() {\n"
                    "        return age;\n"
                    "    }\n"
                    "}\n"
                    "\n"
                    "class ByAgeThenName implements Comparator<Person> {\n"
                    "    @Override\n"
                    "    public int compare(Person a, Person b) {\n"
                    "        int byAge = Integer.compare(a.age(), b.age());\n"
                    "        if (byAge != 0) {\n"
                    "            return byAge;\n"
                    "        }\n"
                    "        return a.name().compareTo(b.name());\n"
                    "    }\n"
                    "}",
                    "        int n = sc.nextInt();\n"
                    "        List<Person> people = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            people.add(new Person(sc.next(), sc.nextInt()));\n"
                    "        }\n"
                    "        people.sort(new ByAgeThenName());\n"
                    "        for (Person p : people) {\n"
                    "            System.out.println(p.name());\n"
                    "        }"),
              [_case("\n".join([str(len(rows))] + [f"{nm} {ag}" for (nm, ag) in rows]),
                     _nl(*[nm for (nm, ag) in sorted(rows, key=lambda r: (r[1], r[0]))]))
               for rows in ([("Bo", 30), ("Ada", 30)],
                            [("solo", 1)],
                            [("c", 2), ("a", 2), ("b", 1)],
                            [("z", 5), ("y", 5), ("x", 5)],
                            [("p", 10), ("q", -1)])],
              hints=["Compute the first comparison into a variable.",
                     "Return it immediately if it is non-zero — that decides the "
                     "order.",
                     "Only when it is zero do you fall through to the second key.",
                     "`return a.name().compareTo(b.name());` delegates to String's own "
                     "ordering.",
                     "Case one has two people aged 30 in the wrong alphabetical order, "
                     "which is exactly what the tie-break fixes."],
              difficulty="Medium"),

        _jch("j20-cr-length", "Order strings by length", "Medium",
             "Write a comparator class `ByLength` that orders words by length "
             "ascending, breaking ties alphabetically. `main` sorts and prints them.",
             _joop("class ByLength implements Comparator<String> {\n"
                   "    @Override\n"
                   "    public int compare(String a, String b) {\n"
                   "        int byLen = Integer.compare(a.length(), b.length());\n"
                   "        if (byLen != 0) {\n"
                   "            return byLen;\n"
                   "        }\n"
                   "        return a.compareTo(b);\n"
                   "    }\n"
                   "}",
                   "        int n = sc.nextInt();\n"
                   "        List<String> words = new ArrayList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            words.add(sc.next());\n"
                   "        }\n"
                   "        words.sort(new ByLength());\n"
                   "        System.out.println(words);"),
             "class ByLength implements Comparator<String> {\n"
             "    @Override\n"
             "    public int compare(String a, String b) {\n"
             "        int byLen = Integer.compare(a.length(), b.length());\n"
             "        if (byLen != 0) {\n"
             "            return byLen;\n"
             "        }\n"
             "        return a.compareTo(b);\n"
             "    }\n"
             "}",
             [_case("\n".join([str(len(ws)), " ".join(ws)]),
                    "[" + ", ".join(sorted(ws, key=lambda w: (len(w), w))) + "]")
              for ws in (["bbb", "a", "cc"], ["solo"], ["dog", "cat", "ox"],
                         ["zz", "aa"], ["one", "two", "six", "a"])],
             hints=["A comparator over `String` implements `Comparator<String>` — you "
                    "do not need to own the type.",
                    "Compare lengths first with `Integer.compare(a.length(), "
                    "b.length())`.",
                    "Return that if non-zero; otherwise fall through to "
                    "`a.compareTo(b)`.",
                    "`compare` must be `public`.",
                    "Case four has two words of equal length and must come out "
                    "alphabetically."]),
    ],
    quiz=[
        _jq("Why can a Comparator order a type you do not own?",
            ["It lives outside the class, so the class needs no modification",
             "It uses reflection",
             "It cannot",
             "Because of generics"],
            0,
            "Comparable requires editing the source; Comparator does not."),
        _jq("What is the tie-breaking shape?",
            ["Compute the first comparison, return it if non-zero, otherwise fall through",
             "Add the two comparisons together",
             "Multiply them",
             "Return zero"],
            0,
            "It chains to as many keys as you like."),
    ],
))


# --- 20.3 sorting -----------------------------------------------------------

_M20.append(_jlesson(
    "m20-sorting", "Sorting collections",
    "The four calls, and what stability buys you.",
    """
```java
Collections.sort(list);              // natural ordering; elements must be Comparable
Collections.sort(list, cmp);         // with a comparator
list.sort(cmp);                      // the modern equivalent (Java 8+)
list.sort(null);                     // natural ordering, via the same method

Arrays.sort(array);                  // natural ordering
Arrays.sort(array, cmp);             // objects only — no comparator for int[]
```

**All of these sort in place.** Nothing is returned; the list or array is
rearranged. `list = Collections.sort(list)` does not compile, which is a useful
error to have met.

**`list.sort(cmp)` is preferred** in new code — it is a method on `List` rather
than a static utility, so there is no import and no ceremony.

## Stability

**Java's object sort is stable**: elements that compare equal keep their
relative order. That is what makes multi-key sorting by repeated passes work:

```java
people.sort(new ByName());     // first
people.sort(new ByAge());      // then — ties stay in name order
```

Sort by the **least** significant key first, then the most significant. Both
this and a single comparator with a tie-break give the same answer; the
comparator is clearer and faster, but knowing why the two-pass version works is
worth having.

`Arrays.sort` on **primitives is not stable** — it is a dual-pivot quicksort, and
for `int` values indistinguishable from one another stability is meaningless
anyway. On objects it uses TimSort, which is stable.

## Sorted collections take a comparator too

```java
Set<String> byLength = new TreeSet<>(new ByLength());
Map<String, Integer> m = new TreeMap<>(new ByLength());
```

The comparator then defines the ordering **and** what counts as a duplicate —
`TreeSet` uses `compare`, not `equals`. A comparator that returns `0` for two
different words means the set will hold only one of them, which is a real bug
worth having seen.

**`Collections` has more than `sort`:** `reverse`, `shuffle`, `max`, `min`,
`frequency`, `unmodifiableList`, `nCopies`. `max` and `min` take a comparator
too.
""",
    warmup=[
        _jq("What does `Collections.sort(list)` return?",
            ["Nothing - it sorts in place", "A new sorted list",
             "A boolean", "The first element"],
            0,
            "`list = Collections.sort(list)` does not compile."),
        _jq("What does a STABLE sort guarantee?",
            ["Elements that compare equal keep their relative order",
             "It never throws",
             "It is O(n)",
             "It sorts in place"],
            0,
            "Which is what makes sorting by repeated passes over different keys work."),
    ],
    exercises=[
        _je("j20-sort-natural", "Sort by natural order",
            "Read `n` words and print them sorted alphabetically. Replace `____` with "
            "the call that sorts the list in place.",
            _jscan("        int n = sc.nextInt();\n"
                   "        List<String> words = new ArrayList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            words.add(sc.next());\n"
                   "        }\n"
                   "        Collections.sort(words);\n"
                   "        System.out.println(words);"),
            "Collections.sort(words);",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   "[" + ", ".join(sorted(ws)) + "]")
             for ws in (["pear", "apple"], ["solo"], ["c", "b", "a"],
                        ["x", "x", "a"], ["dog", "cat", "ant"])],
            hints=["`String` is already `Comparable`, so no comparator is needed.",
                   "`Collections.sort(words);`",
                   "It sorts IN PLACE and returns nothing — assigning the result would "
                   "not compile.",
                   "`words.sort(null);` would do the same thing."],
            difficulty="Intro"),

        _je("j20-sort-method", "The modern call",
            "Sort the words by length, breaking ties alphabetically, using the "
            "comparator supplied. Replace `____` with the `List` method that takes a "
            "comparator.",
            _joop("class ByLength implements Comparator<String> {\n"
                  "    @Override\n"
                  "    public int compare(String a, String b) {\n"
                  "        int byLen = Integer.compare(a.length(), b.length());\n"
                  "        if (byLen != 0) {\n"
                  "            return byLen;\n"
                  "        }\n"
                  "        return a.compareTo(b);\n"
                  "    }\n"
                  "}",
                  "        int n = sc.nextInt();\n"
                  "        List<String> words = new ArrayList<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            words.add(sc.next());\n"
                  "        }\n"
                  "        words.sort(new ByLength());\n"
                  "        System.out.println(words);"),
            "words.sort(new ByLength());",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   "[" + ", ".join(sorted(ws, key=lambda w: (len(w), w))) + "]")
             for ws in (["bbb", "a", "cc"], ["solo"], ["dog", "cat", "ox"],
                        ["zz", "aa"], ["one", "a", "six"])],
            hints=["`List` has its own `sort` method taking a comparator.",
                   "`words.sort(new ByLength());`",
                   "`Collections.sort(words, new ByLength())` is the older equivalent.",
                   "A new comparator instance is created for the call; it holds no "
                   "state."],
            difficulty="Easy"),

        _jfix("j20-sort-assign", "Sorting is not a function",
              "This tries to assign the result of `Collections.sort`, which returns "
              "nothing — so it does not compile. Fix it to sort in place and print the "
              "sorted list.",
              _jscan("        int n = sc.nextInt();\n"
                     "        List<String> words = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            words.add(sc.next());\n"
                     "        }\n"
                     "        List<String> sorted = Collections.sort(words);\n"
                     "        System.out.println(sorted);"),
              _jscan("        int n = sc.nextInt();\n"
                     "        List<String> words = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            words.add(sc.next());\n"
                     "        }\n"
                     "        Collections.sort(words);\n"
                     "        System.out.println(words);"),
              [_case("\n".join([str(len(ws)), " ".join(ws)]),
                     "[" + ", ".join(sorted(ws)) + "]")
               for ws in (["pear", "apple"], ["solo"], ["c", "b", "a"],
                          ["x", "x", "a"], ["dog", "cat"])],
              hints=["`Collections.sort` is `void` — there is nothing to assign.",
                     "It rearranges the list you pass it.",
                     "Call it as a statement, then print the original list.",
                     "This is the same shape as `Arrays.fill` and `Arrays.sort` in "
                     "module 1 and 3: in-place methods that return nothing.",
                     "If you genuinely need both orders, copy the list first."],
              difficulty="Easy"),

        _jch("j20-sort-twopass", "Two passes, least significant first", "Hard",
             "Sort the people by age, and alphabetically by name within each age — "
             "using TWO sorts rather than one tie-breaking comparator, relying on "
             "stability. `ByName` and `ByAge` are given.",
             _joop("class Person {\n"
                   "    private final String name;\n"
                   "    private final int age;\n"
                   "\n"
                   "    Person(String name, int age) {\n"
                   "        this.name = name;\n"
                   "        this.age = age;\n"
                   "    }\n"
                   "\n"
                   "    String name() {\n"
                   "        return name;\n"
                   "    }\n"
                   "\n"
                   "    int age() {\n"
                   "        return age;\n"
                   "    }\n"
                   "}\n"
                   "\n"
                   "class ByName implements Comparator<Person> {\n"
                   "    @Override\n"
                   "    public int compare(Person a, Person b) {\n"
                   "        return a.name().compareTo(b.name());\n"
                   "    }\n"
                   "}\n"
                   "\n"
                   "class ByAge implements Comparator<Person> {\n"
                   "    @Override\n"
                   "    public int compare(Person a, Person b) {\n"
                   "        return Integer.compare(a.age(), b.age());\n"
                   "    }\n"
                   "}",
                   "        int n = sc.nextInt();\n"
                   "        List<Person> people = new ArrayList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            people.add(new Person(sc.next(), sc.nextInt()));\n"
                   "        }\n"
                   "        people.sort(new ByName());\n"
                   "        people.sort(new ByAge());\n"
                   "        for (Person p : people) {\n"
                   '            System.out.println(p.name() + " " + p.age());\n'
                   "        }"),
             "        people.sort(new ByName());\n"
             "        people.sort(new ByAge());\n"
             "        for (Person p : people) {\n"
             '            System.out.println(p.name() + " " + p.age());\n'
             "        }",
             [_case("\n".join([str(len(rows))] + [f"{nm} {ag}" for (nm, ag) in rows]),
                    _nl(*[f"{nm} {ag}"
                          for (nm, ag) in sorted(rows, key=lambda r: (r[1], r[0]))]))
              for rows in ([("Bo", 30), ("Ada", 30), ("Cy", 20)],
                           [("solo", 1)],
                           [("c", 2), ("a", 2), ("b", 1)],
                           [("z", 5), ("y", 5), ("x", 5)],
                           [("p", 10), ("q", -1)])],
             hints=["Sort by the LEAST significant key first — here that is the name.",
                    "Then sort by the most significant key, the age.",
                    "Java's object sort is stable, so the second sort preserves the "
                    "name order within each group of equal ages.",
                    "Doing it the other way round would lose the name ordering "
                    "entirely.",
                    "A single comparator with a tie-break gives the same answer and is "
                    "faster; this exercise is about understanding WHY stability "
                    "matters.",
                    "Print `name age` separated by one space."]),
    ],
    quiz=[
        _jq("To sort by age, then by name within each age, using two passes, which comes first?",
            ["Sort by name, then by age", "Sort by age, then by name",
             "Either order works", "Two passes cannot do it"],
            0,
            "Least significant key first, relying on the second sort's stability."),
        _jq("What does a TreeSet built with a comparator use to detect duplicates?",
            ["The comparator's compare returning 0", "equals", "hashCode",
             "Both equals and compare"],
            0,
            "So a comparator that ties two different elements makes the set silently "
            "keep only one."),
    ],
))


# --- 20.4 choosing ----------------------------------------------------------

_M20.append(_jlesson(
    "m20-choose", "Choosing a collection",
    "The decision, in one page.",
    """
## Start with the question you are asking

| Your question | Reach for |
|---|---|
| What is at position `i`? | `List` → **`ArrayList`** |
| Have I seen this before? | `Set` → **`HashSet`** |
| What is associated with this key? | `Map` → **`HashMap`** |
| What arrived first? | `Queue` → **`ArrayDeque`** |
| What was most recent? | `Deque` as a stack → **`ArrayDeque`** |
| What is the smallest right now? | **`PriorityQueue`** |

## Then ask about order

| Order you need | Set | Map |
|---|---|---|
| Do not care (fastest) | `HashSet` | `HashMap` |
| Insertion order | `LinkedHashSet` | `LinkedHashMap` |
| Sorted | `TreeSet` | `TreeMap` |

Converting is always one constructor call, so it is cheap to change your mind:
`new TreeSet<>(hashSet)`.

## Costs, side by side

| | get by index | search | insert at end | insert at front |
|---|---|---|---|---|
| `ArrayList` | O(1) | O(n) | O(1)* | O(n) |
| `LinkedList` | O(n) | O(n) | O(1) | O(1) |
| `ArrayDeque` | — | O(n) | O(1)* | O(1)* |
| `HashSet` / `HashMap` | — | **O(1)** | O(1)* | — |
| `TreeSet` / `TreeMap` | — | O(log n) | O(log n) | — |
| `PriorityQueue` | — | O(n) | O(log n) | — |

\\* amortised

## The rules that actually decide it

1. **Default to `ArrayList` and `HashMap`.** Together they cover most code.
2. **Reach for a `Set` the moment you write `list.contains(x)` inside a loop.**
   That single change turns O(n²) into O(n), and it is the most common
   performance fix there is.
3. **Program to the interface.** `List<String> x = new ArrayList<>();` — so
   changing your mind costs one line.
4. **If output order matters, say so in the type.** `HashMap` guarantees
   nothing; `LinkedHashMap` and `TreeMap` do.
5. **Never `java.util.Stack` or `Vector`.** Legacy, synchronised for no reason,
   and `Stack` inherits every list method.
6. **Honour `equals`/`hashCode`** for anything used as a set element or map key,
   and do not mutate it afterwards.

> **Sizing matters at scale.** `new ArrayList<>(n)` and `new HashMap<>(n)` skip
> the repeated regrowth and rehashing when you already know roughly how many
> elements are coming.
""",
    warmup=[
        _jq("You are writing `list.contains(x)` inside a loop over n items. What should you change?",
            ["Use a Set - contains becomes O(1) and the whole loop O(n)",
             "Sort the list first",
             "Use a LinkedList",
             "Nothing"],
            0,
            "The single most common performance fix in everyday Java."),
        _jq("Which pair should be your default?",
            ["ArrayList and HashMap", "LinkedList and TreeMap",
             "Vector and Hashtable", "ArrayDeque and TreeSet"],
            0,
            "They cover most code; reach for the others when you have a specific "
            "reason."),
    ],
    exercises=[
        _jch("j20-ch-contains", "Swap the list for a set", "Medium",
             "Read `n` known words, then `m` queries. For each query print `yes` or "
             "`no`. Use a `Set` so each lookup is O(1) rather than a scan.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Set<String> known = new HashSet<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            known.add(sc.next());\n"
                    "        }\n"
                    "        int m = sc.nextInt();\n"
                    "        for (int i = 0; i < m; i++) {\n"
                    "            if (known.contains(sc.next())) {\n"
                    '                System.out.println("yes");\n'
                    "            } else {\n"
                    '                System.out.println("no");\n'
                    "            }\n"
                    "        }"),
             "        Set<String> known = new HashSet<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            known.add(sc.next());\n"
             "        }\n"
             "        int m = sc.nextInt();\n"
             "        for (int i = 0; i < m; i++) {\n"
             "            if (known.contains(sc.next())) {\n"
             '                System.out.println("yes");\n'
             "            } else {\n"
             '                System.out.println("no");\n'
             "            }\n"
             "        }",
             [_case("\n".join([str(len(ks)), " ".join(ks),
                               str(len(qs)), " ".join(qs)]),
                    _nl(*["yes" if q in ks else "no" for q in qs]))
              for (ks, qs) in ((["a", "b"], ["a", "c"]),
                               (["solo"], ["solo"]),
                               (["x", "y", "z"], ["y", "w", "z"]),
                               (["p"], ["q"]),
                               (["dog", "cat"], ["cat", "cat", "ant"]))],
             hints=["A `HashSet` gives O(1) membership, against O(n) for a list.",
                    "With `n` known words and `m` queries that is O(n + m) instead of "
                    "O(n * m).",
                    "Only the SET's contents matter, so no order is ever printed — "
                    "which is why a HashSet is safe here.",
                    "Print `yes` or `no`, one per query."]),

        _jch("j20-ch-ordered-report", "Pick the ordered one", "Medium",
             "Count the words and print a `word=count` line for each, in alphabetical "
             "order. Choose the map implementation that gives that order without any "
             "sorting step.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Map<String, Integer> counts = new TreeMap<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String w = sc.next();\n"
                    "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                    "        }\n"
                    "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
                    '            System.out.println(e.getKey() + "=" + e.getValue());\n'
                    "        }"),
             "        Map<String, Integer> counts = new TreeMap<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String w = sc.next();\n"
             "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
             "        }\n"
             "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
             '            System.out.println(e.getKey() + "=" + e.getValue());\n'
             "        }",
             [_case("\n".join([str(len(ws)), " ".join(ws)]),
                    _nl(*[f"{k}={ws.count(k)}" for k in sorted(set(ws))]))
              for ws in (["pear", "apple", "pear"], ["solo"], ["c", "b", "a"],
                         ["x", "y", "x"], ["dog", "cat", "ant", "cat"])],
             hints=["A `HashMap` would need a separate sorting step; a `TreeMap` "
                    "arrives sorted.",
                    "That is rule 4: if output order matters, put it in the type.",
                    "The counting idiom is unchanged — only the constructor differs.",
                    "Walk `entrySet()` so you get key and value in one lookup."]),

        _jch("j20-ch-recent", "Keep only the most recent k", "Hard",
             "Read `n` words then `k`. Print the LAST `k` distinct words in the order "
             "they were most recently seen, one per line. A repeat counts as a fresh "
             "sighting and moves the word to the most recent position.",
             _jscan("        int n = sc.nextInt();\n"
                    "        List<String> words = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            words.add(sc.next());\n"
                    "        }\n"
                    "        int k = sc.nextInt();\n"
                    "        Deque<String> recent = new ArrayDeque<>();\n"
                    "        for (String w : words) {\n"
                    "            recent.remove(w);\n"
                    "            recent.addFirst(w);\n"
                    "            if (recent.size() > k) {\n"
                    "                recent.removeLast();\n"
                    "            }\n"
                    "        }\n"
                    "        while (!recent.isEmpty()) {\n"
                    "            System.out.println(recent.pollFirst());\n"
                    "        }"),
             "        Deque<String> recent = new ArrayDeque<>();\n"
             "        for (String w : words) {\n"
             "            recent.remove(w);\n"
             "            recent.addFirst(w);\n"
             "            if (recent.size() > k) {\n"
             "                recent.removeLast();\n"
             "            }\n"
             "        }\n"
             "        while (!recent.isEmpty()) {\n"
             "            System.out.println(recent.pollFirst());\n"
             "        }",
             [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                    _nl(*_recent_k(ws, k)))
              for (ws, k) in ((["a", "b", "a", "c"], 2),
                              (["solo"], 3),
                              (["x", "y", "z"], 2),
                              (["p", "p", "p"], 1),
                              (["a", "b", "c", "d"], 3))],
             hints=["A `Deque` gives you both ends: most recent at the front, oldest "
                    "at the back.",
                    "On each sighting, `remove(w)` first — that drops any earlier "
                    "position for the same word, so a repeat moves rather than "
                    "duplicating. It is O(n) but the deque is tiny.",
                    "Then `addFirst(w)` puts it at the most-recent end.",
                    "Trim with `removeLast()` whenever the size exceeds `k`.",
                    "Drain from the front, so the most recent prints first.",
                    "This is the shape of every 'recently opened files' list, and of "
                    "an LRU cache."]),

        _jch("j20-ch-first-unique", "The first word that never repeats", "Hard",
             "Read `n` words. Print the first word that occurs exactly once, or `none` "
             "if every word repeats. Use a map that preserves insertion order so one "
             "pass over it answers the question.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Map<String, Integer> counts = new LinkedHashMap<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String w = sc.next();\n"
                    "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
                    "        }\n"
                    '        String answer = "none";\n'
                    "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
                    "            if (e.getValue() == 1) {\n"
                    "                answer = e.getKey();\n"
                    "                break;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(answer);"),
             "        Map<String, Integer> counts = new LinkedHashMap<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String w = sc.next();\n"
             "            counts.put(w, counts.getOrDefault(w, 0) + 1);\n"
             "        }\n"
             '        String answer = "none";\n'
             "        for (Map.Entry<String, Integer> e : counts.entrySet()) {\n"
             "            if (e.getValue() == 1) {\n"
             "                answer = e.getKey();\n"
             "                break;\n"
             "            }\n"
             "        }\n"
             "        System.out.println(answer);",
             [_case("\n".join([str(len(ws)), " ".join(ws)]),
                    next((w for w in dict.fromkeys(ws) if ws.count(w) == 1), "none"))
              for ws in (["a", "b", "a"], ["x", "x"], ["solo"],
                         ["p", "q", "p", "q", "r"], ["z", "z", "y", "y"])],
             hints=["A `LinkedHashMap` keeps keys in the order they were FIRST "
                    "inserted, which is exactly the order the question asks about.",
                    "A `HashMap` would give no reliable order and a `TreeMap` would "
                    "give alphabetical — both wrong here.",
                    "Count in one pass, then walk `entrySet()` and take the first "
                    "count of exactly `1`.",
                    "`break` as soon as you find it.",
                    "Seed the answer as `\"none\"` so the all-repeat case needs no "
                    "special handling.",
                    "A repeated word keeps its original position in a "
                    "LinkedHashMap — re-putting does not move it."]),
    ],
    quiz=[
        _jq("Which collection would you use for 'the smallest right now', repeatedly?",
            ["PriorityQueue", "TreeSet", "ArrayList with sort", "HashMap"],
            0,
            "peek is O(1) and poll is O(log n). Re-sorting a list every time would be "
            "far worse."),
        _jq("Why does `new ArrayList<>(n)` help at scale?",
            ["It skips the repeated regrowth and copying as the list fills",
             "It makes get faster",
             "It sorts the list",
             "It has no effect"],
            0,
            "The same applies to `new HashMap<>(n)` and rehashing."),
    ],
))


# ===========================================================================
# Capstone
# ===========================================================================

def _m20_run(rows, mode):
    if mode == "name":
        ordered = sorted(rows, key=lambda r: r[0])
    elif mode == "salary":
        ordered = sorted(rows, key=lambda r: (-r[2], r[0]))
    else:
        ordered = sorted(rows, key=lambda r: (r[1], r[0]))
    out = [f"{nm} {dept} {sal}" for (nm, dept, sal) in ordered]
    depts = sorted(set(d for (_n, d, _s) in rows))
    out.append("departments=" + "[" + ", ".join(depts) + "]")
    total = {}
    for (_n, d, s) in rows:
        total[d] = total.get(d, 0) + s
    best = min(sorted(total), key=lambda d: -total[d])
    out.append("top=" + best + " " + str(total[best]))
    return _nl(*out)


def _m20_case(rows, mode):
    return _case("\n".join([str(len(rows))]
                           + [f"{nm} {d} {s}" for (nm, d, s) in rows] + [mode]),
                 _m20_run(rows, mode))


_M20_CAP = _jcap(
    "Staff report",
    """
Three orderings of the same data, plus two summaries — the whole of Part 6 in
one program.

## Input

```
n
<name> <department> <salary>     x n
<mode>
```

`mode` is `name`, `salary` or `dept`.

## Output

First the `n` employees, one per line as `name department salary`, ordered by:

| mode | Ordering |
|---|---|
| `name` | name ascending |
| `salary` | salary **descending**, ties broken by name ascending |
| anything else | department ascending, ties broken by name ascending |

Then two summary lines:

```
departments=[<every distinct department, alphabetically>]
top=<department with the highest total salary> <that total>
```

On a tie for the top department, take the alphabetically first.

## What the hidden cases check

- **Three comparators, each a named class.** Lambdas are Part 8; write the
  classes out.
- **Descending is a swap, not a negation.** `Integer.compare(b.salary(),
  a.salary())` — negating the result breaks for `Integer.MIN_VALUE`.
- **Every ordering has a tie-break**, so the output is fully determined.
- **`departments=` prints a `Set`**, giving the bracketed form, and must be
  alphabetical — so choose the implementation that already is.
- **Totals need a `Map`**, and the top-department scan must be alphabetical for
  the tie rule to fall out of a strict `>`.
- **`Integer.compare`, never subtraction.** One case has salaries far enough
  apart to overflow.
""",
    _jch("j20-cap-staff", "Staff report", "Hard",
         "Write the `Employee` class and the three comparators where you see `____`. "
         "`main` is written: it reads the data, picks a comparator from the mode, "
         "sorts, prints, and produces the two summaries.",
         _joop("class Employee {\n"
               "    private final String name;\n"
               "    private final String dept;\n"
               "    private final int salary;\n"
               "\n"
               "    Employee(String name, String dept, int salary) {\n"
               "        this.name = name;\n"
               "        this.dept = dept;\n"
               "        this.salary = salary;\n"
               "    }\n"
               "\n"
               "    String name() {\n"
               "        return name;\n"
               "    }\n"
               "\n"
               "    String dept() {\n"
               "        return dept;\n"
               "    }\n"
               "\n"
               "    int salary() {\n"
               "        return salary;\n"
               "    }\n"
               "\n"
               "    @Override\n"
               "    public String toString() {\n"
               '        return name + " " + dept + " " + salary;\n'
               "    }\n"
               "}\n"
               "\n"
               "class ByName implements Comparator<Employee> {\n"
               "    @Override\n"
               "    public int compare(Employee a, Employee b) {\n"
               "        return a.name().compareTo(b.name());\n"
               "    }\n"
               "}\n"
               "\n"
               "class BySalaryDesc implements Comparator<Employee> {\n"
               "    @Override\n"
               "    public int compare(Employee a, Employee b) {\n"
               "        int bySal = Integer.compare(b.salary(), a.salary());\n"
               "        if (bySal != 0) {\n"
               "            return bySal;\n"
               "        }\n"
               "        return a.name().compareTo(b.name());\n"
               "    }\n"
               "}\n"
               "\n"
               "class ByDept implements Comparator<Employee> {\n"
               "    @Override\n"
               "    public int compare(Employee a, Employee b) {\n"
               "        int byDept = a.dept().compareTo(b.dept());\n"
               "        if (byDept != 0) {\n"
               "            return byDept;\n"
               "        }\n"
               "        return a.name().compareTo(b.name());\n"
               "    }\n"
               "}",
               "        int n = sc.nextInt();\n"
               "        List<Employee> staff = new ArrayList<>();\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            staff.add(new Employee(sc.next(), sc.next(), sc.nextInt()));\n"
               "        }\n"
               "        String mode = sc.next();\n"
               '        if (mode.equals("name")) {\n'
               "            staff.sort(new ByName());\n"
               '        } else if (mode.equals("salary")) {\n'
               "            staff.sort(new BySalaryDesc());\n"
               "        } else {\n"
               "            staff.sort(new ByDept());\n"
               "        }\n"
               "        for (Employee e : staff) {\n"
               "            System.out.println(e);\n"
               "        }\n"
               "        Set<String> depts = new TreeSet<>();\n"
               "        Map<String, Integer> totals = new TreeMap<>();\n"
               "        for (Employee e : staff) {\n"
               "            depts.add(e.dept());\n"
               "            totals.put(e.dept(),\n"
               "                totals.getOrDefault(e.dept(), 0) + e.salary());\n"
               "        }\n"
               '        System.out.println("departments=" + depts);\n'
               '        String bestDept = "";\n'
               "        int bestTotal = -1;\n"
               "        for (Map.Entry<String, Integer> en : totals.entrySet()) {\n"
               "            if (en.getValue() > bestTotal) {\n"
               "                bestTotal = en.getValue();\n"
               "                bestDept = en.getKey();\n"
               "            }\n"
               "        }\n"
               '        System.out.println("top=" + bestDept + " " + bestTotal);'),
         "class Employee {\n"
         "    private final String name;\n"
         "    private final String dept;\n"
         "    private final int salary;\n"
         "\n"
         "    Employee(String name, String dept, int salary) {\n"
         "        this.name = name;\n"
         "        this.dept = dept;\n"
         "        this.salary = salary;\n"
         "    }\n"
         "\n"
         "    String name() {\n"
         "        return name;\n"
         "    }\n"
         "\n"
         "    String dept() {\n"
         "        return dept;\n"
         "    }\n"
         "\n"
         "    int salary() {\n"
         "        return salary;\n"
         "    }\n"
         "\n"
         "    @Override\n"
         "    public String toString() {\n"
         '        return name + " " + dept + " " + salary;\n'
         "    }\n"
         "}\n"
         "\n"
         "class ByName implements Comparator<Employee> {\n"
         "    @Override\n"
         "    public int compare(Employee a, Employee b) {\n"
         "        return a.name().compareTo(b.name());\n"
         "    }\n"
         "}\n"
         "\n"
         "class BySalaryDesc implements Comparator<Employee> {\n"
         "    @Override\n"
         "    public int compare(Employee a, Employee b) {\n"
         "        int bySal = Integer.compare(b.salary(), a.salary());\n"
         "        if (bySal != 0) {\n"
         "            return bySal;\n"
         "        }\n"
         "        return a.name().compareTo(b.name());\n"
         "    }\n"
         "}\n"
         "\n"
         "class ByDept implements Comparator<Employee> {\n"
         "    @Override\n"
         "    public int compare(Employee a, Employee b) {\n"
         "        int byDept = a.dept().compareTo(b.dept());\n"
         "        if (byDept != 0) {\n"
         "            return byDept;\n"
         "        }\n"
         "        return a.name().compareTo(b.name());\n"
         "    }\n"
         "}",
         [_m20_case(rows, mode) for (rows, mode) in (
             ([("Ada", "eng", 100), ("Bo", "ops", 90), ("Cy", "eng", 110)], "salary"),
             ([("Bo", "ops", 50), ("Ada", "eng", 50)], "name"),
             ([("z", "b", 10), ("y", "a", 20), ("x", "a", 30)], "dept"),
             ([("solo", "one", 7)], "other"),
             ([("p", "a", 2000000000), ("q", "b", -2000000000)], "salary"),
         )],
         hints=["`Employee` needs three `private final` fields, a constructor, three "
                "getters, and a `toString()` returning `name dept salary`.",
                "`toString()` must be `public` — `println(e)` calls it.",
                "Each comparator is a NAMED class implementing "
                "`Comparator<Employee>`, with a `public int compare(Employee a, "
                "Employee b)`.",
                "`ByName` delegates straight to `String.compareTo`.",
                "`BySalaryDesc` swaps the arguments — `Integer.compare(b.salary(), "
                "a.salary())`. Case five has salaries far enough apart that "
                "subtraction would overflow.",
                "Both the salary and department comparators need the tie-break shape: "
                "compute, return if non-zero, otherwise fall through to name.",
                "`main` is already written and uses a `TreeSet` for the departments "
                "and a `TreeMap` for the totals — which is why the tie rule for "
                "`top=` falls out of a strict `>`.",
                "You are writing only the types above `main`; do not change `main`."]),
    example_io="stdin:  3\n        Ada eng 100\n        Bo ops 90\n        Cy eng 110\n"
               "        salary\n\n"
               "stdout: Cy eng 110\n        Ada eng 100\n        Bo ops 90\n"
               "        departments=[eng, ops]\n        top=eng 210",
    rubric=[
        "`Employee` has private final fields, getters, and a public `toString()`.",
        "Three separate named comparator classes, each implementing `Comparator<Employee>`.",
        "`compare` is `public` in all three.",
        "Descending is done by swapping arguments, not by negating.",
        "`Integer.compare` is used for the salary, never subtraction.",
        "Both multi-key comparators use the compute-return-fall-through tie-break shape.",
        "Every ordering is fully determined, so no output depends on input order.",
        "`main` is left exactly as given.",
    ],
)


_MODULES.append(_jmod(
    20, 6, "The collections framework",
    "Ordering, sorting, and choosing",
    "Give a type its natural order, write orderings that live outside it, sort with "
    "either, and choose a collection by the question you are asking.",
    """
Part 6 closes on the two things that turn a pile of collections into a toolkit:
knowing how to order what is in them, and knowing which one to pick.

**`Comparable`** gives a type one built-in ordering, through `compareTo`. Only
the *sign* of the result is specified, and it must be built with
`Integer.compare` rather than subtraction — the overflow bug is real and the
test cases here prove it. The contract also has a quiet consequence: `TreeSet`
and `TreeMap` use `compareTo`, not `equals`, so two objects that compare equal
collapse into one.

**`Comparator`** lifts the ordering out of the class, so a type can have as many
as you like — and so you can order types you do not own. Reversing is a swap of
arguments; multi-key ordering is *compute, return if decided, otherwise fall
through*. Writing them as named classes here is deliberate: a comparator is just
an object implementing an interface, which is module 14 doing real work. Lambdas
make it shorter in Part 8, not different.

**Sorting** is `Collections.sort` or the newer `list.sort`, always in place. Java's
object sort is **stable**, which is what makes sorting by repeated passes over
different keys work — least significant first.

And then **the choice itself**. Default to `ArrayList` and `HashMap`; reach for a
`Set` the moment `contains` appears inside a loop; put the order you need into
the type rather than sorting afterwards; and never use `Vector` or
`java.util.Stack`.
""",
    _M20,
    capstone=_M20_CAP,
    objectives=[
        "Implement `Comparable` and write a correct `compareTo`.",
        "Say why only the sign of the result is specified, and why subtraction is wrong.",
        "Write a `Comparator` as a named class, and reverse one correctly.",
        "Chain comparisons to break ties across several keys.",
        "Sort with Collections.sort, list.sort and Arrays.sort, and know they sort in place.",
        "Explain stability, and use it to sort by several keys in separate passes.",
        "Say what a TreeSet built with a comparator treats as a duplicate.",
        "Choose a collection from the question being asked, and justify it by cost.",
    ],
    why="Sorting by something other than the default is one of the most common things "
        "any application does, and 'Comparable versus Comparator' is asked in almost "
        "every Java interview. The choosing lesson is the one you will reach for "
        "weekly: picking the wrong collection is the most common cause of accidentally "
        "quadratic code.",
    est_minutes=330,
    glossary=[
        _jg("Comparable", "An interface a type implements to define its ONE natural "
                          "ordering, via compareTo."),
        _jg("compareTo", "Returns negative, zero or positive. Only the sign is "
                         "specified."),
        _jg("Comparator", "An ordering held as a separate object, via compare(a, b). A "
                          "type may have any number."),
        _jg("Integer.compare", "The overflow-safe comparison. `a - b` wraps for values "
                               "far apart."),
        _jg("natural ordering", "The order compareTo defines - ascending for Integer, "
                                "alphabetical for String."),
        _jg("stable sort", "Equal elements keep their relative order. Java's object sort "
                           "is stable; its primitive sort is not."),
        _jg("tie-break", "Compute the first comparison, return it if non-zero, otherwise "
                         "fall through to the next key."),
        _jg("Collections", "The static utility class: sort, reverse, shuffle, max, min, "
                           "frequency, unmodifiableList."),
        _jg("in-place", "Sorting rearranges the collection and returns nothing - "
                        "assigning the result does not compile."),
    ],
    cheatsheet="""
```java
// --- Comparable: one natural ordering, inside the class -------------------
class Person implements Comparable<Person> {
    @Override
    public int compareTo(Person other) {
        return Integer.compare(this.age, other.age);   // NOT this.age - other.age
    }
}
// negative = this first, 0 = tie, positive = this later.  ONLY the sign matters.

// --- Comparator: any number of orderings, outside the class ---------------
class ByAge implements Comparator<Person> {
    @Override
    public int compare(Person a, Person b) {
        return Integer.compare(a.age(), b.age());
    }
}
// descending: swap the arguments
return Integer.compare(b.age(), a.age());

// tie-break: compute, return if decided, fall through
int byAge = Integer.compare(a.age(), b.age());
if (byAge != 0) return byAge;
return a.name().compareTo(b.name());

// --- sorting (ALL in place, all return void) ------------------------------
Collections.sort(list);          // natural; elements must be Comparable
Collections.sort(list, cmp);
list.sort(cmp);                  // preferred
list.sort(null);                 // natural ordering
Arrays.sort(arr);  Arrays.sort(objArr, cmp);

// stable => sort by LEAST significant key first for a multi-pass sort
people.sort(new ByName());
people.sort(new ByAge());

// sorted collections take one too — and it then defines DUPLICATES
Set<String> s = new TreeSet<>(new ByLength());

// --- choosing --------------------------------------------------------------
// position?      List      -> ArrayList
// seen it?       Set       -> HashSet          (contains O(1) vs O(n))
// look up?       Map       -> HashMap
// first in?      Queue     -> ArrayDeque
// most recent?   Deque     -> ArrayDeque  (push/pop)
// smallest now?  PriorityQueue
// order matters in output? LinkedHash* (insertion) or Tree* (sorted)
// never: Vector, java.util.Stack
```
""",
    self_check=[
        "Can you write compareTo for a two-field ordering without using subtraction?",
        "Can you say why only the sign of compareTo's result is specified?",
        "Can you explain what a TreeSet does with two elements that compare equal?",
        "Can you write a Comparator as a named class from memory?",
        "Can you reverse an ordering correctly, and say why negating is risky?",
        "Can you write the tie-break shape for three keys?",
        "Can you say why `list = Collections.sort(list)` does not compile?",
        "Can you explain why a two-pass sort needs the least significant key first?",
        "Given a problem, can you name the collection and justify it by cost?",
    ],
    review=[
        _jq("Why is `return this.age - other.age;` a bug?",
            ["It overflows for values far apart, reversing the comparison",
             "It does not compile",
             "It is slower",
             "It returns the wrong type"],
            0,
            "`Integer.compare(a, b)` is the safe form and compiles to the same thing "
            "without the hazard."),
        _jq("How do you reverse a Comparator?",
            ["Swap the two arguments in the comparison",
             "Negate the returned value",
             "Return -1 always",
             "Sort then reverse the list"],
            0,
            "Negating breaks for Integer.MIN_VALUE, whose negation overflows."),
        _jq("To sort by department, then by name within each department, in two passes:",
            ["Sort by name first, then by department",
             "Sort by department first, then by name",
             "Either order",
             "It cannot be done in two passes"],
            0,
            "Least significant key first, relying on the second sort's stability."),
        _jq("You write `list.contains(x)` inside a loop over n elements. What is the fix?",
            ["Put the candidates in a HashSet - contains becomes O(1)",
             "Sort the list first",
             "Use a LinkedList",
             "Nothing is wrong"],
            0,
            "It turns an O(n^2) loop into O(n), and it is the most common performance "
            "fix in everyday Java."),
    ],
    milestone="You can order any type by any rule, sort with the right call, and choose "
              "a collection from the question you are asking rather than from habit. "
              "Part 6 — the collections framework — is complete.",
))
