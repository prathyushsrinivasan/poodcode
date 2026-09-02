# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 23 - Wildcards.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# The token `? extends`, `? super` and `<?>` become legal here and nowhere
# earlier (the scope linter enforces it), so modules 21 and 22 had to solve
# every "accept a list of anything" problem with a named type parameter. That is
# deliberate: a wildcard is only meaningful once you have felt invariance push
# back.
#
# The spine is one fact - `List<Integer>` is NOT a `List<Number>` - and three
# consequences: `<?>` when the type does not matter, `? extends` when you only
# read, `? super` when you only write. PECS is the mnemonic, not the lesson.
#
# Arrays ARE covariant, which is the contrast that makes invariance look like a
# choice rather than an oversight - lesson 23.1 ends on an ArrayStoreException.
# ---------------------------------------------------------------------------

_M23 = []


def _j23(helpers, body):
    """Static helper methods above a Scanner-opening `main`."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }"
    )


_RD_WORDS23 = ("        int n = sc.nextInt();\n"
               "        List<String> words = new ArrayList<>();\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            words.add(sc.next());\n"
               "        }\n")

_RD_NUMS23 = ("        int n = sc.nextInt();\n"
              "        List<Integer> nums = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            nums.add(sc.nextInt());\n"
              "        }\n")

_WORDS23 = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
            ["alpha", "beta", "gamma", "d"])

_NUMS23 = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])


def _wcase23(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _ncase23(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _jlist23(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


# --- 23.1 Invariance ---------------------------------------------------------

_M23.append(_jlesson(
    "m23-invariance", "Why `List<Integer>` is not a `List<Number>`",
    "Generics are invariant - and arrays, which are not, show you why.",
    """
`Integer` is a `Number`. So this ought to work, and it does not:

```java
List<Integer> ints = new ArrayList<>();
List<Number> nums = ints;         // COMPILE ERROR: incompatible types
```

Generic types are **invariant**: `List<Integer>` and `List<Number>` are
unrelated types, no matter how their type arguments are related. `List<Object>`
is not a supertype of anything either.

That looks like an inconvenience until you finish the thought:

```java
List<Number> nums = ints;   // if this compiled...
nums.add(3.14);             // ...this would be legal, and perfectly typed
int x = ints.get(0);        // ...and this would explode.
```

A `Double` would have landed in a list the compiler still believes contains only
`Integer`s. Invariance is what makes that sentence impossible to write.

**Arrays made the other choice, and you can watch it fail.** Java's arrays are
**covariant** - a `String[]` really is an `Object[]`:

```java
String[] words = new String[3];
Object[] any = words;        // compiles: arrays are covariant
any[0] = Integer.valueOf(42);   // compiles too - and throws at RUN TIME
```

That last line throws `ArrayStoreException`. The array carries its real element
type at run time and checks every store, which is a check on *every single
assignment* forever. Generics chose the compile-time answer instead: no run-time
check, and no way to write the bad program in the first place.

**So how do you write a method that takes "a list of any kind of number"?**
Module 22's answer was a bounded type parameter:

```java
static <T extends Number> double total(List<T> items)
```

That works. But `T` is never used for anything except naming the element type -
the method never needs to say "the same T" twice. When a type parameter is used
exactly once, a **wildcard** says the same thing more directly, and that is what
the rest of this module is about:

```java
static double total(List<? extends Number> items)
```
""",
    warmup=[
        _jq("`List<Number> nums = ints;` where `ints` is a `List<Integer>`…",
            ["Does not compile - generics are invariant",
             "Compiles and works",
             "Compiles, then throws at run time",
             "Compiles with a warning"],
            0,
            "If it compiled you could `add(3.14)` to a list of Integers."),
        _jq("`Object[] any = words;` where words is a `String[]`…",
            ["Compiles - arrays are covariant - and a bad store throws ArrayStoreException",
             "Does not compile",
             "Compiles and is completely safe",
             "Copies the array"],
            0,
            "Arrays check element types at run time. Generics moved that check to "
            "compile time."),
    ],
    exercises=[
        _jfix("j23-inv-assign", "Assigning the wrong list",
              "This tries to hold a `List<Integer>` in a `List<Number>` variable, and "
              "generics are invariant, so it does not compile. Build the `List<Number>` "
              "directly instead - adding an `Integer` to it is fine, because `Integer` "
              "IS a `Number`.",
              _jscan(_RD_NUMS23
                     + "        List<Number> any = nums;\n"
                       "        System.out.println(any);\n"
                       "        System.out.println(any.size());"),
              _jscan("        int n = sc.nextInt();\n"
                     "        List<Number> any = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            any.add(sc.nextInt());\n"
                     "        }\n"
                     "        System.out.println(any);\n"
                     "        System.out.println(any.size());"),
              [_ncase23(xs, _nl(_jlist23(xs), len(xs))) for xs in _NUMS23],
              hints=["The error is *incompatible types: List<Integer> cannot be "
                     "converted to List<Number>*.",
                     "The relationship between `Integer` and `Number` says nothing "
                     "about the relationship between their lists.",
                     "Declare and fill one `List<Number>` from the start: "
                     "`List<Number> any = new ArrayList<>();`",
                     "`any.add(sc.nextInt())` autoboxes to `Integer`, which is a "
                     "`Number`, so the add is legal.",
                     "Printing a `List<Number>` of Integers still shows the plain "
                     "values."],
              difficulty="Medium"),

        _je("j23-inv-object", "A list of anything at all",
            "A `List<Object>` really can hold both a word and a number - what it cannot "
            "do is stand in for a `List<String>`. Replace `____` with that list's "
            "declaration.",
            _jscan("        String word = sc.next();\n"
                   "        int n = sc.nextInt();\n"
                   "        List<Object> everything = new ArrayList<>();\n"
                   "        everything.add(word);\n"
                   "        everything.add(n);\n"
                   "        System.out.println(everything);\n"
                   "        System.out.println(everything.size());"),
            "List<Object> everything = new ArrayList<>();",
            [_case(f"{w} {n}", _nl(f"[{w}, {n}]", 2))
             for (w, n) in (("ada", 42), ("bo", 0), ("x", -3), ("zed", 7),
                            ("generics", 1))],
            hints=["The element type has to be the one type every reference type "
                   "extends.",
                   "`List<Object> everything = new ArrayList<>();`",
                   "The `int` autoboxes to an `Integer`, which is an `Object`.",
                   "This is still not a `List<String>` - invariance cuts both ways."],
            difficulty="Intro"),

        _jfix("j23-inv-arraystore", "The array that accepted the wrong thing",
              "Arrays are covariant, so `Object[] any = words;` compiles - and then the "
              "store of an `Integer` into it throws `ArrayStoreException` at run time. "
              "That run-time failure is exactly what invariance prevents for generics. "
              "Delete the aliasing and the bad store, and print the first word and the "
              "length instead.",
              _jscan("        int n = sc.nextInt();\n"
                     "        String[] words = new String[n];\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            words[i] = sc.next();\n"
                     "        }\n"
                     "        Object[] any = words;\n"
                     "        any[0] = Integer.valueOf(42);\n"
                     "        System.out.println(words[0]);\n"
                     "        System.out.println(words.length);"),
              _jscan("        int n = sc.nextInt();\n"
                     "        String[] words = new String[n];\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            words[i] = sc.next();\n"
                     "        }\n"
                     "        System.out.println(words[0]);\n"
                     "        System.out.println(words.length);"),
              [_wcase23(ws, _nl(ws[0], len(ws))) for ws in _WORDS23],
              hints=["Run it: the exception names the type the array actually holds.",
                     "The array knows at run time that it is really a `String[]`, and "
                     "refuses the Integer.",
                     "Two lines go away - the alias and the store.",
                     "What is left just prints `words[0]` and `words.length`.",
                     "A `List<String>` could never have been aliased that way, because "
                     "the compiler would have stopped at the assignment."],
              difficulty="Medium"),

        _jch("j23-inv-copy", "Widening the honest way", "Easy",
             "You cannot assign a `List<String>` to a `List<Object>` - but you can copy "
             "the elements across, because each individual `String` IS an `Object`. "
             "Build that copy, print it, and print its size.",
             _jscan(_RD_WORDS23
                    + "        List<Object> any = new ArrayList<>();\n"
                      "        for (String w : words) {\n"
                      "            any.add(w);\n"
                      "        }\n"
                      "        System.out.println(any);\n"
                      "        System.out.println(any.size());"),
             "        List<Object> any = new ArrayList<>();\n"
             "        for (String w : words) {\n"
             "            any.add(w);\n"
             "        }\n"
             "        System.out.println(any);\n"
             "        System.out.println(any.size());",
             [_wcase23(ws, _nl(_jlist23(ws), len(ws))) for ws in _WORDS23],
             hints=["Element by element is always allowed - it is only the whole-list "
                    "assignment that is not.",
                    "`List<Object> any = new ArrayList<>();` then an enhanced `for`.",
                    "`any.add(w)` is legal because a `String` is an `Object`.",
                    "The copy is a separate list; the original is untouched.",
                    "Two lines out: the list, then its size."]),
    ],
    quiz=[
        _jq("Generics are invariant because…",
            ["otherwise you could add a Double to a list the compiler believes holds Integers",
             "the JVM cannot represent subtypes",
             "it is faster",
             "of type erasure alone"],
            0,
            "Invariance is what makes the unsafe program unwritable."),
        _jq("`ArrayStoreException` exists because…",
            ["arrays are covariant, so every store has to be checked at run time",
             "arrays are invariant",
             "of autoboxing",
             "arrays cannot hold objects"],
            0,
            "The check generics avoid entirely by refusing the assignment up front."),
    ],
))


# --- 23.2 The unbounded wildcard ---------------------------------------------

_M23.append(_jlesson(
    "m23-unknown", "`<?>` - the unknown type",
    "A list of *something*, where the something does not matter.",
    """
Sometimes a method genuinely does not care what is in the list:

```java
static void report(List<?> items) {
    System.out.println(items.size());
    System.out.println(items.isEmpty());
}
```

`List<?>` is read "list of unknown". It accepts a `List<String>`, a
`List<Integer>`, a `List<Pair<String, Integer>>` - anything at all, which a
plain `List<Object>` parameter would not.

**What you can do with a `List<?>`:**

* anything that does not mention the element type - `size()`, `isEmpty()`,
  `clear()`, `toString()`;
* **read** elements as `Object`, because whatever the unknown type is, it is
  certainly an `Object`.

```java
for (Object item : items) {
    System.out.println(item);
}
```

**What you cannot do:** add anything.

```java
items.add("x");     // COMPILE ERROR - even here
items.add(null);    // the one exception; null is every reference type
```

The reason is worth saying out loud: the compiler knows the list has *one*
specific element type, it just does not know *which*. A `List<Integer>` would be
ruined by a `"x"`, so the only safe answer is to refuse every element.

**`List<?>` is not a raw `List`.** They look similar and behave oppositely:

| | `List` (raw) | `List<?>` |
|---|---|---|
| `add("x")` | allowed, unchecked | compile error |
| Type safety | switched off | fully enforced |
| Use it | never, in new code | whenever the element type does not matter |

A raw type says "stop checking me"; a wildcard says "check me, I just cannot
name the type".

**When to reach for it:** a method that only counts, prints, or clears. If you
need to *use* the elements as something more specific than `Object`, you want
one of the bounded wildcards in the next two lessons.
""",
    warmup=[
        _jq("What can you add to a `List<?>`?",
            ["Only null", "Anything", "Only Objects", "Only Strings"],
            0,
            "The list has one real element type; the compiler just does not know which, "
            "so it refuses everything except null."),
        _jq("Reading from a `List<?>` gives you…",
            ["Object", "the element type", "a raw type", "nothing - reads are banned"],
            0,
            "Whatever the unknown type is, it is an Object."),
    ],
    exercises=[
        _je("j23-unk-header", "A parameter that takes any list",
            "`report` prints how many elements a list has and whether it is empty, "
            "whatever it holds. Replace `____` with its signature line.",
            _j23("    static void report(List<?> items) {\n"
                 "        System.out.println(items.size());\n"
                 "        System.out.println(items.isEmpty());\n"
                 "    }",
                 _RD_WORDS23 + "        report(words);"),
            "    static void report(List<?> items) {",
            [_wcase23(ws, _nl(len(ws), "false")) for ws in _WORDS23],
            hints=["The method never touches an element, so it does not need to name "
                   "the type.",
                   "`List<Object>` would NOT accept a `List<String>` - invariance.",
                   "`static void report(List<?> items) {`",
                   "`size()` and `isEmpty()` do not mention the element type, so both "
                   "are allowed."],
            difficulty="Easy"),

        _je("j23-unk-read", "Reading out of the unknown",
            "Whatever the list holds, each element is at least an `Object`. Replace "
            "`____` with the loop that prints every element.",
            _j23("    static void printAll(List<?> items) {\n"
                 "        for (Object item : items) {\n"
                 "            System.out.println(item);\n"
                 "        }\n"
                 "    }",
                 _RD_WORDS23 + "        printAll(words);"),
            "        for (Object item : items) {\n"
            "            System.out.println(item);\n"
            "        }",
            [_wcase23(ws, _nl(*ws)) for ws in _WORDS23],
            hints=["The element type is unknown, so the most specific type you can "
                   "name for it is `Object`.",
                   "An enhanced `for` with an `Object` loop variable.",
                   "`for (Object item : items) {`",
                   "`println(Object)` calls the element's own `toString`."],
            difficulty="Easy"),

        _jfix("j23-unk-add", "Adding to the unknown",
              "This tries to append a marker to a `List<?>`, and it does not compile - "
              "the compiler will not let anything into a list whose element type it "
              "cannot name. Drop the add and have the method report the size before "
              "and after printing instead.",
              _j23("    static void report(List<?> items) {\n"
                   '        items.add("marker");\n'
                   "        System.out.println(items.size());\n"
                   "        for (Object item : items) {\n"
                   "            System.out.println(item);\n"
                   "        }\n"
                   "    }",
                   _RD_WORDS23 + "        report(words);"),
              _j23("    static void report(List<?> items) {\n"
                   "        System.out.println(items.size());\n"
                   "        for (Object item : items) {\n"
                   "            System.out.println(item);\n"
                   "        }\n"
                   "    }",
                   _RD_WORDS23 + "        report(words);"),
              [_wcase23(ws, _nl(len(ws), *ws)) for ws in _WORDS23],
              hints=["The error is *no suitable method found for add(String)* - the "
                     "parameter type is `capture of ?`.",
                     "If the list were really a `List<Integer>`, that String would have "
                     "ruined it.",
                     "Reads are fine; only the write has to go.",
                     "What is left prints the size, then every element.",
                     "Writing is what `? super` (lesson 23.4) is for."],
              difficulty="Medium"),

        _jch("j23-unk-total", "Measure anything", "Medium",
             "Write `totalLength`, which takes a list of anything and returns the total "
             "number of characters in the printed form of its elements. `main` calls it "
             "on a list of words and on a list of numbers.",
             _j23("    static int totalLength(List<?> items) {\n"
                  "        int total = 0;\n"
                  "        for (Object item : items) {\n"
                  "            total += item.toString().length();\n"
                  "        }\n"
                  "        return total;\n"
                  "    }",
                  _RD_WORDS23
                  + "        int m = sc.nextInt();\n"
                    "        List<Integer> nums = new ArrayList<>();\n"
                    "        for (int i = 0; i < m; i++) {\n"
                    "            nums.add(sc.nextInt());\n"
                    "        }\n"
                    "        System.out.println(totalLength(words));\n"
                    "        System.out.println(totalLength(nums));"),
             "    static int totalLength(List<?> items) {\n"
             "        int total = 0;\n"
             "        for (Object item : items) {\n"
             "            total += item.toString().length();\n"
             "        }\n"
             "        return total;\n"
             "    }",
             [_case("\n".join([str(len(ws)), " ".join(ws), str(len(xs)),
                               " ".join(str(x) for x in xs)]),
                    _nl(sum(len(w) for w in ws), sum(len(str(x)) for x in xs)))
              for (ws, xs) in zip(_WORDS23, _NUMS23)],
             hints=["The parameter is `List<?>` - the method works for both call sites "
                    "only if it names no element type.",
                    "Each element comes out as an `Object`, which is enough: every "
                    "object has `toString()`.",
                    "`total += item.toString().length();`",
                    "A negative number's printed form includes the minus sign, and that "
                    "counts.",
                    "The return type is an ordinary `int`."]),
    ],
    quiz=[
        _jq("`List<?>` versus raw `List` - the difference is…",
            ["`List<?>` keeps full type checking; a raw type switches it off",
             "they are identical",
             "`List<?>` allows adds",
             "raw types are safer"],
            0,
            "One says 'I cannot name the type'; the other says 'stop checking me'."),
        _jq("Which call does NOT compile for `static void report(List<Object> xs)`?",
            ["report(new ArrayList<String>())", "report(new ArrayList<Object>())",
             "report(objects)", "all of them compile"],
            0,
            "Invariance again - which is exactly why the parameter should have been "
            "`List<?>`."),
    ],
))


# --- 23.3 Upper-bounded wildcards --------------------------------------------

_M23.append(_jlesson(
    "m23-extends", "`? extends T` - producers",
    "A list you only read from can be a list of any subtype.",
    """
`List<?>` gives you elements as `Object`, which is often not enough. An
**upper-bounded wildcard** keeps the flexibility and gives back the type:

```java
static double total(List<? extends Number> items) {
    double sum = 0;
    for (Number item : items) {     // every element IS a Number
        sum += item.doubleValue();
    }
    return sum;
}
```

`List<? extends Number>` means "a list of some *unknown* type, which is
`Number` or a subtype of it". So all of these are legal arguments:

```java
total(integers);   // List<Integer>
total(doubles);    // List<Double>
total(numbers);    // List<Number> — `extends` includes the bound itself
```

**You can read, at the bound's type. You still cannot write.**

```java
Number n = items.get(0);   // fine - whatever it holds, it is a Number
items.add(Integer.valueOf(1));   // COMPILE ERROR
```

The read is safe because every possible element type is a `Number`. The write is
not, because "some subtype of Number" might be `Double`, and an `Integer` does
not belong in a `List<Double>`.

That is why this is called a **producer**: the list produces values for you and
receives nothing.

**Compare it with module 22's bounded type parameter:**

```java
static <T extends Number> double total(List<T> items)     // works
static double total(List<? extends Number> items)         // says the same thing
```

Both accept the same arguments. The rule of thumb: **if the type parameter is
used exactly once, a wildcard is the simpler spelling.** If you need to say "the
same T" twice - two parameters of the same type, or a return type that matches
the parameter - keep the type parameter.

**The bound may be any type, and `extends` covers interfaces too**, exactly as
in module 22: `List<? extends Comparable<String>>` is a list of things comparable
to a String.
""",
    warmup=[
        _jq("Which is NOT a legal argument for `total(List<? extends Number> xs)`?",
            ["List<String>", "List<Integer>", "List<Double>", "List<Number>"],
            0,
            "`String` is not a `Number`, so it does not satisfy the upper bound."),
        _jq("Inside a method taking `List<? extends Number>`, `items.add(1)` is…",
            ["a compile error - the unknown subtype might be Double",
             "fine", "fine if you cast", "fine for Integer only"],
            0,
            "Upper-bounded wildcards produce values; they never accept them."),
    ],
    exercises=[
        _je("j23-ext-header", "Accept any kind of number",
            "`total` adds up a list of numbers of any wrapper type. Replace `____` with "
            "its signature line, using a wildcard rather than a type parameter.",
            _j23("    static double total(List<? extends Number> items) {\n"
                 "        double sum = 0;\n"
                 "        for (Number item : items) {\n"
                 "            sum += item.doubleValue();\n"
                 "        }\n"
                 "        return sum;\n"
                 "    }",
                 _RD_NUMS23 + "        System.out.println(total(nums));"),
            "    static double total(List<? extends Number> items) {",
            [_ncase23(xs, str(float(sum(xs)))) for xs in _NUMS23],
            hints=["The element type is unknown, but it is certainly a `Number` or "
                   "below.",
                   "The syntax is `? extends` followed by the upper bound.",
                   "`static double total(List<? extends Number> items) {`",
                   "That is what lets the loop variable be a `Number`."],
            difficulty="Medium"),

        _je("j23-ext-read", "Reading at the bound",
            "Whatever the list really holds, every element is at least a `Number` - so "
            "the loop variable can say so. Replace `____` with that loop's header.",
            _j23("    static double biggest(List<? extends Number> items) {\n"
                 "        double best = items.get(0).doubleValue();\n"
                 "        for (Number item : items) {\n"
                 "            if (item.doubleValue() > best) {\n"
                 "                best = item.doubleValue();\n"
                 "            }\n"
                 "        }\n"
                 "        return best;\n"
                 "    }",
                 _RD_NUMS23 + "        System.out.println(biggest(nums));"),
            "for (Number item : items) {",
            [_ncase23(xs, str(float(max(xs)))) for xs in _NUMS23],
            hints=["`Object` would compile too, but then `doubleValue()` would not.",
                   "The wildcard's bound tells you the most specific type every element "
                   "is guaranteed to have.",
                   "`for (Number item : items) {`",
                   "The result is a `double`, so it prints with a decimal point."],
            difficulty="Easy"),

        _jfix("j23-ext-narrow", "The parameter that was too narrow",
              "`total` is declared to take a `List<Number>`, so `main`'s "
              "`List<Integer>` is rejected: *incompatible types*. Widen the parameter "
              "with an upper-bounded wildcard so any list of numbers is accepted.",
              _j23("    static double total(List<Number> items) {\n"
                   "        double sum = 0;\n"
                   "        for (Number item : items) {\n"
                   "            sum += item.doubleValue();\n"
                   "        }\n"
                   "        return sum;\n"
                   "    }",
                   _RD_NUMS23
                   + "        System.out.println(total(nums));\n"
                     "        System.out.println(nums.size());"),
              _j23("    static double total(List<? extends Number> items) {\n"
                   "        double sum = 0;\n"
                   "        for (Number item : items) {\n"
                   "            sum += item.doubleValue();\n"
                   "        }\n"
                   "        return sum;\n"
                   "    }",
                   _RD_NUMS23
                   + "        System.out.println(total(nums));\n"
                     "        System.out.println(nums.size());"),
              [_ncase23(xs, _nl(str(float(sum(xs))), len(xs))) for xs in _NUMS23],
              hints=["The body is already correct - it only ever reads.",
                     "`List<Integer>` is not a `List<Number>`; invariance, from lesson "
                     "23.1.",
                     "Only the parameter type changes.",
                     "`List<? extends Number> items`",
                     "Module 22's `<T extends Number>` would also work - but `T` would "
                     "be used exactly once, which is the signal to prefer a wildcard."],
              difficulty="Medium"),

        _jch("j23-ext-two", "One method, two element types", "Medium",
             "Using the `total` method already written, read a list of whole numbers "
             "and build a second list of halves (`Double`s) from the same input. Print "
             "the total of the whole numbers, the total of the halves, and the two "
             "added together - proving one method serves both lists.",
             _j23("    static double total(List<? extends Number> items) {\n"
                  "        double sum = 0;\n"
                  "        for (Number item : items) {\n"
                  "            sum += item.doubleValue();\n"
                  "        }\n"
                  "        return sum;\n"
                  "    }",
                  _RD_NUMS23
                  + "        List<Double> halves = new ArrayList<>();\n"
                    "        for (int x : nums) {\n"
                    "            halves.add(x / 2.0);\n"
                    "        }\n"
                    "        System.out.println(total(nums));\n"
                    "        System.out.println(total(halves));\n"
                    "        System.out.println(total(nums) + total(halves));"),
             "        List<Double> halves = new ArrayList<>();\n"
             "        for (int x : nums) {\n"
             "            halves.add(x / 2.0);\n"
             "        }\n"
             "        System.out.println(total(nums));\n"
             "        System.out.println(total(halves));\n"
             "        System.out.println(total(nums) + total(halves));",
             [_ncase23(xs, _nl(str(float(sum(xs))),
                               str(sum(x / 2.0 for x in xs)),
                               str(float(sum(xs)) + sum(x / 2.0 for x in xs))))
              for xs in ([3, 1, 2], [5], [-4, -8, -2], [10, 10, 2], [7, 2, 9, 4])],
             hints=["`List<Double> halves = new ArrayList<>();` - a different element "
                    "type entirely.",
                    "`x / 2.0` is a `double`, which autoboxes to `Double` on the way "
                    "into the list.",
                    "Both lists are legal arguments because both element types are "
                    "below `Number`.",
                    "A `List<Number>` parameter would have accepted neither.",
                    "Three printed lines, all of them doubles."]),
    ],
    quiz=[
        _jq("`List<? extends Number>` lets you…",
            ["read elements as Number, but add nothing",
             "read and add", "add but not read", "neither"],
            0,
            "A producer. The unknown subtype makes every write unsafe."),
        _jq("When is a wildcard preferable to `<T extends Number>`?",
            ["When the type parameter would be used exactly once",
             "Always", "Never", "Only for static methods"],
            0,
            "If you must say 'the same T' twice, you need the named parameter."),
    ],
))


# --- 23.4 Lower-bounded wildcards and PECS -----------------------------------

_M23.append(_jlesson(
    "m23-super", "`? super T` - consumers, and PECS",
    "The mirror image: a list you only write into can be a list of any supertype.",
    """
The other direction. A **lower-bounded wildcard** says "some unknown type, which
is `T` or a *supertype* of it":

```java
static void addWords(List<? super String> target) {
    target.add("ada");     // always safe
    target.add("bo");
}
```

`addWords` accepts a `List<String>`, a `List<Object>` - any list that is
guaranteed to be able to hold a `String`. The write is safe because whatever the
unknown type is, a `String` fits in it.

**Reading is what you lose.** The only thing you can safely say about an element
is that it is an `Object`:

```java
Object o = target.get(0);   // fine
String s = target.get(0);   // COMPILE ERROR - it might be a List<Object>
```

So the two are exact mirrors:

| Wildcard | You may | Because |
|---|---|---|
| `? extends T` | **read** as `T` | every element is at least a `T` |
| `? super T` | **write** a `T` | the list can definitely hold a `T` |

**PECS - Producer Extends, Consumer Super.** Ask what the parameter does *for
the method*: if the collection produces values you consume, use `extends`; if
the method pushes values into it, use `super`. The classic signature has one of
each:

```java
static <T> void copy(List<? super T> dest, List<? extends T> src) {
    for (T item : src) {     // src PRODUCES Ts
        dest.add(item);      // dest CONSUMES Ts
    }
}
```

`copy(objects, words)` then compiles with `T` inferred as `String`: a
`List<Object>` can certainly consume Strings, and a `List<String>` certainly
produces them. Written with plain `List<T>` on both sides, the same call would
be rejected.

**You have already used it.** The JDK's own signature is
`list.sort(Comparator<? super E> c)` - the comparator only *consumes* elements,
so a `Comparator<Object>` is perfectly good for sorting a `List<String>`. That
`? super` in module 20's method signature was this, all along.

**And the last rule: never use a wildcard as a return type.** It only pushes the
problem onto every caller, who then has to deal with an unknown type they cannot
name.
""",
    warmup=[
        _jq("`static void addWords(List<? super String> target)` accepts…",
            ["List<String> and List<Object>", "only List<String>",
             "only List<Object>", "any list at all"],
            0,
            "Any list guaranteed able to hold a String - that is, String or a supertype "
            "of it."),
        _jq("PECS stands for…",
            ["Producer Extends, Consumer Super", "Parameter Extends, Class Super",
             "Public Extends, Class Static", "Producer Erases, Consumer Stores"],
            0,
            "Ask what the collection does for the method, then pick the wildcard."),
    ],
    exercises=[
        _je("j23-sup-header", "A list you only write into",
            "`fill` copies every word into a target list that is guaranteed able to "
            "hold Strings - it might be a `List<String>` or a `List<Object>`. Replace "
            "`____` with its signature line.",
            _j23("    static void fill(List<? super String> target, List<String> src) {\n"
                 "        for (String item : src) {\n"
                 "            target.add(item);\n"
                 "        }\n"
                 "    }",
                 _RD_WORDS23
                 + "        List<Object> any = new ArrayList<>();\n"
                   "        fill(any, words);\n"
                   "        System.out.println(any);\n"
                   "        System.out.println(any.size());"),
            "    static void fill(List<? super String> target, List<String> src) {",
            [_wcase23(ws, _nl(_jlist23(ws), len(ws))) for ws in _WORDS23],
            hints=["`main` passes a `List<Object>`, so a `List<String>` parameter would "
                   "be rejected.",
                   "The method only ADDS to `target`, which is the signal for a lower "
                   "bound.",
                   "`static void fill(List<? super String> target, List<String> src) {`",
                   "Read it as: some unknown type that `String` fits into."],
            difficulty="Medium"),

        _jfix("j23-sup-wrong", "The wildcard pointing the wrong way",
              "`fill` writes into `target`, but `target` is declared `? extends "
              "String` - a producer - so the `add` does not compile. Point the wildcard "
              "the other way, as PECS says a consumer should be.",
              _j23("    static void fill(List<? extends String> target, List<String> src) {\n"
                   "        for (String item : src) {\n"
                   "            target.add(item);\n"
                   "        }\n"
                   "    }",
                   _RD_WORDS23
                   + "        List<Object> any = new ArrayList<>();\n"
                     "        fill(any, words);\n"
                     "        System.out.println(any);\n"
                     "        System.out.println(any.size());"),
              _j23("    static void fill(List<? super String> target, List<String> src) {\n"
                   "        for (String item : src) {\n"
                   "            target.add(item);\n"
                   "        }\n"
                   "    }",
                   _RD_WORDS23
                   + "        List<Object> any = new ArrayList<>();\n"
                     "        fill(any, words);\n"
                     "        System.out.println(any);\n"
                     "        System.out.println(any.size());"),
              [_wcase23(ws, _nl(_jlist23(ws), len(ws))) for ws in _WORDS23],
              hints=["Two things are wrong at once, and one change fixes both: the add "
                     "is rejected, and `List<Object>` is not a `List<? extends String>` "
                     "either.",
                     "Which side of PECS is `target` on? The method pushes values into "
                     "it.",
                     "Consumer Super.",
                     "`List<? super String> target`",
                     "`src` is genuinely a producer, and could be widened to "
                     "`? extends String` too - it is only left concrete here to keep "
                     "one change in view."],
              difficulty="Medium"),

        _je("j23-sup-copy", "The PECS signature",
            "`copy` moves elements from a source list into a destination list. The "
            "source produces, the destination consumes - one wildcard of each kind. "
            "Replace `____` with the signature line.",
            _j23("    static <T> void copy(List<? super T> dest, List<? extends T> src) {\n"
                 "        for (T item : src) {\n"
                 "            dest.add(item);\n"
                 "        }\n"
                 "    }",
                 _RD_WORDS23
                 + "        List<Object> any = new ArrayList<>();\n"
                   "        copy(any, words);\n"
                   "        copy(any, words);\n"
                   "        System.out.println(any);\n"
                   "        System.out.println(any.size());"),
            "    static <T> void copy(List<? super T> dest, List<? extends T> src) {",
            [_wcase23(ws, _nl(_jlist23(list(ws) + list(ws)), 2 * len(ws)))
             for ws in _WORDS23],
            hints=["The method still needs a named `T`, because the two parameters have "
                   "to be related to each other.",
                   "Destination consumes: `? super T`. Source produces: `? extends T`.",
                   "`static <T> void copy(List<? super T> dest, List<? extends T> src) {`",
                   "The call `copy(any, words)` then infers `T` as `String`.",
                   "Called twice, so every word appears twice in the destination."],
            difficulty="Hard"),

        _jch("j23-sup-both", "Producer and consumer together", "Hard",
            "Write `moveAll`, which copies everything from a source list into a "
            "destination and returns how many elements it moved. Use PECS for both "
            "parameters. `main` moves a list of words and then a list of numbers into "
            "the same `List<Object>`.",
             _j23("    static <T> int moveAll(List<? super T> dest, List<? extends T> src) {\n"
                  "        int moved = 0;\n"
                  "        for (T item : src) {\n"
                  "            dest.add(item);\n"
                  "            moved++;\n"
                  "        }\n"
                  "        return moved;\n"
                  "    }",
                  _RD_WORDS23
                  + "        int m = sc.nextInt();\n"
                    "        List<Integer> nums = new ArrayList<>();\n"
                    "        for (int i = 0; i < m; i++) {\n"
                    "            nums.add(sc.nextInt());\n"
                    "        }\n"
                    "        List<Object> any = new ArrayList<>();\n"
                    "        System.out.println(moveAll(any, words));\n"
                    "        System.out.println(moveAll(any, nums));\n"
                    "        System.out.println(any);\n"
                    "        System.out.println(any.size());"),
             "    static <T> int moveAll(List<? super T> dest, List<? extends T> src) {\n"
             "        int moved = 0;\n"
             "        for (T item : src) {\n"
             "            dest.add(item);\n"
             "            moved++;\n"
             "        }\n"
             "        return moved;\n"
             "    }",
             [_case("\n".join([str(len(ws)), " ".join(ws), str(len(xs)),
                               " ".join(str(x) for x in xs)]),
                    _nl(len(ws), len(xs),
                        _jlist23(list(ws) + list(xs)), len(ws) + len(xs)))
              for (ws, xs) in zip(_WORDS23, _NUMS23)],
             hints=["The signature is the PECS one: "
                    "`static <T> int moveAll(List<? super T> dest, List<? extends T> src)`.",
                    "The loop variable can be a `T`, because the source produces `T`s.",
                    "`dest.add(item)` is legal because the destination consumes `T`s.",
                    "Count the moves in an ordinary `int` and return it.",
                    "The two calls infer `T` as `String` and then as `Integer` - the "
                    "same `List<Object>` is a legal destination for both.",
                    "A `List<T> dest` parameter would have rejected both calls."]),
    ],
    quiz=[
        _jq("Reading from a `List<? super String>` gives you…",
            ["Object", "String", "the unknown type", "a compile error"],
            0,
            "It might really be a `List<Object>`, so `Object` is all that can be "
            "promised."),
        _jq("Why is `list.sort(Comparator<? super E> c)` written that way?",
            ["The comparator only consumes elements, so a comparator of any supertype works",
             "Comparators are always super",
             "To allow lambdas",
             "For speed"],
            0,
            "Consumer Super, in the standard library you have already been using."),
    ],
))


# --- Capstone ----------------------------------------------------------------

_M23_CAP_HELPERS = (
    "    static int describe(List<?> items) {\n"
    "        return items.size();\n"
    "    }\n"
    "\n"
    "    static double total(List<? extends Number> items) {\n"
    "        double sum = 0;\n"
    "        for (Number item : items) {\n"
    "            sum += item.doubleValue();\n"
    "        }\n"
    "        return sum;\n"
    "    }\n"
    "\n"
    "    static <T> void copy(List<? super T> dest, List<? extends T> src) {\n"
    "        for (T item : src) {\n"
    "            dest.add(item);\n"
    "        }\n"
    "    }"
)

_M23_CAP_BODY = (
    "        int n = sc.nextInt();\n"
    "        List<String> words = new ArrayList<>();\n"
    "        for (int i = 0; i < n; i++) {\n"
    "            words.add(sc.next());\n"
    "        }\n"
    "        int m = sc.nextInt();\n"
    "        List<Integer> nums = new ArrayList<>();\n"
    "        for (int i = 0; i < m; i++) {\n"
    "            nums.add(sc.nextInt());\n"
    "        }\n"
    "        List<Double> halves = new ArrayList<>();\n"
    "        for (int x : nums) {\n"
    "            halves.add(x / 2.0);\n"
    "        }\n"
    "        System.out.println(describe(words));\n"
    "        System.out.println(describe(nums));\n"
    "        System.out.println(total(nums));\n"
    "        System.out.println(total(halves));\n"
    "        List<Object> ledger = new ArrayList<>();\n"
    "        copy(ledger, words);\n"
    "        copy(ledger, nums);\n"
    "        System.out.println(ledger);\n"
    "        System.out.println(describe(ledger));"
)


def _m23_cap_case(ws, xs):
    halves = [x / 2.0 for x in xs]
    return _case("\n".join([str(len(ws)), " ".join(ws), str(len(xs)),
                            " ".join(str(x) for x in xs)]),
                 _nl(len(ws), len(xs), str(float(sum(xs))), str(sum(halves)),
                     _jlist23(list(ws) + list(xs)), len(ws) + len(xs)))


_M23_CAP = _jcap(
    "The transfer desk",
    """
Three methods, one of each wildcard, and a `main` that could not be written
without them.

* **`describe(list)`** - takes a list of anything at all and returns its size.
  The element type is genuinely irrelevant here.
* **`total(list)`** - takes a list of any kind of number and returns the sum as
  a `double`. It only reads, so it is a producer.
* **`copy(dest, src)`** - moves every element of `src` into `dest`. The source
  produces, the destination consumes: one wildcard of each kind, tied together
  by a named type parameter.

`main` then pours a `List<String>` and a `List<Integer>` into the same
`List<Object>` ledger. Every one of those calls would be rejected if the
parameters were written as plain parameterized types - which is the point of the
whole module.
""",
    _jch("j23-cap-transfer", "The transfer desk", "Hard",
         "Write the three methods described in the brief so the given `main` compiles "
         "and prints its six lines.",
         _j23(_M23_CAP_HELPERS, _M23_CAP_BODY),
         _M23_CAP_HELPERS,
         [_m23_cap_case(ws, xs) for (ws, xs) in (
             (["ada", "bo", "cy"], [3, 1, 2]),
             (["solo"], [5]),
             (["x", "yy", "zzz"], [-4, -8, -2]),
             (["pear", "fig"], [10, 10, 2]),
             (["alpha", "beta", "gamma", "d"], [7, 2, 9, 4]),
         )],
         hints=["`describe` needs no type at all: `static int describe(List<?> items)`.",
                "`total` reads numbers, so it is a producer: "
                "`List<? extends Number> items`, and the loop variable is a `Number`.",
                "Sum into a `double` with `item.doubleValue()`, which is what the "
                "`Number` bound promises.",
                "`copy` is the PECS signature: "
                "`static <T> void copy(List<? super T> dest, List<? extends T> src)`.",
                "Its loop variable is a `T`, and the body is a single "
                "`dest.add(item);`.",
                "`copy(ledger, words)` infers `T` as `String`; `copy(ledger, nums)` "
                "infers `Integer`. The same `List<Object>` is a legal destination for "
                "both.",
                "None of the three may be written with a plain `List<Object>` or "
                "`List<Number>` parameter - invariance would reject every call.",
                "The ledger prints in the order things were copied: words first, then "
                "numbers."]),
    example_io="stdin:  3\n        ada bo cy\n        3\n        3 1 2\n\n"
               "stdout: 3\n        3\n        6.0\n        3.0\n"
               "        [ada, bo, cy, 3, 1, 2]\n        6",
    rubric=[
        "`describe` takes `List<?>` and names no element type.",
        "`total` takes `List<? extends Number>` and reads its elements as `Number`.",
        "`total` returns a double, computed with `doubleValue()`.",
        "`copy` declares a type parameter `T` and uses `? super T` for the destination.",
        "`copy` uses `? extends T` for the source, and iterates it as `T`.",
        "No method uses a plain `List<Object>` or `List<Number>` parameter.",
        "Nothing is added to a `? extends` list, and nothing is read as `T` from a `? super` list.",
        "All six lines are printed in order.",
    ],
)


_MODULES.append(_jmod(
    23, 7, "Generics",
    "Wildcards",
    "`List<Integer>` is not a `List<Number>` - and the three wildcards that make useful "
    "methods possible anyway: `<?>` when the type does not matter, `? extends` when you "
    "only read, `? super` when you only write.",
    """
One fact drives this whole module: generic types are **invariant**. A
`List<Integer>` is not a `List<Number>`, and a `List<String>` is not a
`List<Object>`, however obviously related the element types are. Arrays made the
opposite choice and pay for it with `ArrayStoreException` on every store;
generics moved the check to compile time by refusing the assignment instead.

That is safe, and it makes ordinary methods impossible to write - a `total`
taking `List<Number>` accepts nothing anyone actually has. **Wildcards** are the
repair:

* `List<?>` - a list of unknown type. Read as `Object`, add nothing, and use it
  for methods that only count, print or clear.
* `List<? extends Number>` - a **producer**. Read elements as `Number`, add
  nothing.
* `List<? super String>` - a **consumer**. Add Strings, read only as `Object`.

**PECS** - Producer Extends, Consumer Super - is how you decide, and
`copy(List<? super T> dest, List<? extends T> src)` is the signature that puts
both halves in one line. The rule is not academic: `list.sort(Comparator<?
super E>)` has been in your hands since module 20.
""",
    _M23,
    capstone=_M23_CAP,
    objectives=[
        "State what invariance means and give the unsafe program it prevents.",
        "Contrast array covariance with generic invariance, including ArrayStoreException.",
        "Use `List<?>` for a method that does not care about the element type.",
        "Explain why nothing but `null` can be added to a `List<?>`, and how that differs from a raw type.",
        "Use `? extends T` for a parameter you only read from, and say what the loop variable's type is.",
        "Use `? super T` for a parameter you only write into, and say what a read gives you.",
        "Apply PECS to choose a wildcard, and write the `copy(dest, src)` signature from memory.",
        "Choose between a wildcard and a bounded type parameter, and avoid wildcards in return types.",
    ],
    why="Wildcards are the part of generics people quietly avoid, and then cannot read "
        "the JDK's own signatures - `Collections.sort`, `addAll`, `Comparator<? super "
        "E>`. PECS is also a standard interview question with a one-line answer, and the "
        "underlying idea (ask for exactly the capability you need, no more) is a design "
        "instinct well beyond Java.",
    est_minutes=330,
    glossary=[
        _jg("invariance", "`List<Integer>` and `List<Number>` are unrelated types, "
                          "however their element types are related."),
        _jg("covariance", "The opposite: a `String[]` IS an `Object[]`. Java's arrays "
                          "work this way, and check stores at run time."),
        _jg("ArrayStoreException", "Thrown when a covariant array reference is used to "
                                   "store the wrong element type."),
        _jg("wildcard", "The `?` in a type argument - an unknown type."),
        _jg("unbounded wildcard", "`List<?>` - element type unknown and unconstrained. "
                                  "Read as Object, add nothing."),
        _jg("upper-bounded wildcard", "`List<? extends T>` - a producer. Read as T, add "
                                      "nothing."),
        _jg("lower-bounded wildcard", "`List<? super T>` - a consumer. Add Ts, read as "
                                      "Object."),
        _jg("PECS", "Producer Extends, Consumer Super - the rule for choosing between "
                    "them."),
        _jg("capture", "The compiler's internal name for the unknown type, which is why "
                       "errors mention 'capture of ?'."),
    ],
    cheatsheet="""
```java
// --- invariance -----------------------------------------------------------
List<Integer> ints = new ArrayList<>();
List<Number> nums = ints;         // COMPILE ERROR - generics are invariant
Object[] any = new String[3];     // fine - arrays are covariant...
any[0] = 42;                      // ...ArrayStoreException at RUN TIME

// --- the three wildcards --------------------------------------------------
void report(List<?> xs)                  // any list; read as Object; add nothing
double total(List<? extends Number> xs)  // PRODUCER: read as Number; add nothing
void fill(List<? super String> xs)       // CONSUMER: add Strings; read as Object

// --- PECS: Producer Extends, Consumer Super -------------------------------
static <T> void copy(List<? super T> dest, List<? extends T> src) {
    for (T item : src) {      // src produces
        dest.add(item);       // dest consumes
    }
}
copy(objects, words);         // T inferred as String

// --- in the JDK you already use -------------------------------------------
list.sort(Comparator<? super E> c);      // the comparator only consumes
list.addAll(Collection<? extends E> c);  // the source only produces

// --- choosing -------------------------------------------------------------
// type parameter used ONCE            -> wildcard
// need to say "the same T" twice      -> <T> ...
// return type                         -> never a wildcard
// List<?>  is fully type-checked;  raw List is not checked at all
```
""",
    self_check=[
        "Can you write the two lines that show why `List<Number> n = ints;` has to be illegal?",
        "Can you explain what ArrayStoreException is and why generics have no equivalent?",
        "Can you say what may be added to a `List<?>`, and why?",
        "Can you state the difference between `List<?>` and a raw `List`?",
        "Can you say what the loop variable's type is inside a `List<? extends Number>` method?",
        "Can you say what a read from a `List<? super String>` gives you, and why?",
        "Can you expand PECS and write the `copy` signature from memory?",
        "Can you explain why `list.sort` takes a `Comparator<? super E>`?",
    ],
    review=[
        _jq("```java\nList<Integer> ints = new ArrayList<>();\nList<Number> nums = ints;\n```",
            ["Compile error - generics are invariant", "Fine",
             "Compiles, throws at run time", "Fine, with a warning"],
            0,
            "Otherwise `nums.add(3.14)` would put a Double into a list of Integers."),
        _jq("Inside `static double total(List<? extends Number> xs)`, which line fails?",
            ["xs.add(Integer.valueOf(1));", "Number n = xs.get(0);",
             "int size = xs.size();", "for (Number x : xs) { ... }"],
            0,
            "A producer never accepts. The unknown subtype might be `Double`."),
        _jq("Which parameter should be `? super T`?",
            ["The destination that the method adds elements to",
             "The source it reads from", "Both", "Neither"],
            0,
            "Consumer Super. The source is the producer, so it takes `? extends T`."),
        _jq("In the capstone, why must `copy` take wildcards rather than `List<T>` twice?",
            ["`copy(ledger, words)` mixes a List<Object> destination with a List<String> source",
             "Because copy is static",
             "To avoid casts",
             "Because Object has no type argument"],
            0,
            "With `List<T>` on both sides the compiler would need one `T` that is both "
            "Object and String."),
    ],
    milestone="You can read and write the wildcard signatures the standard library is "
              "built from, and choose between `extends`, `super` and a named type "
              "parameter by asking what the method actually does with the collection.",
))
