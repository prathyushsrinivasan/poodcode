# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 25 - Lambdas, functional interfaces and method references.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# OPENS PART 8. The token ` -> ` becomes legal here and nowhere earlier, which
# was a deliberate twenty-four-module wait: every `Comparator` in module 20 and
# every interface implementation in module 14 is a NAMED class on purpose, so
# this module opens by collapsing one the learner has already written by hand.
# That is the whole argument for lambdas, made with their own code.
#
# SEQUENCING: a lambda is only ever an instance of a functional interface, so
# the order is (1) the syntax against a Comparator they already know, (2) the
# four interfaces in java.util.function, (3) writing one of your own - which is
# what proves there is no magic, (4) capture and effectively-final, the rule
# that actually bites in real code, and (5) method references as the shorthand
# for the lambdas that only forward.
#
# STREAMS ARE NOT HERE. `.stream()` is gated to module 26. Every exercise in
# this module drives its lambdas with an ordinary loop, so the lambda is the
# only new idea on the page.
#
# IMPORTS: java.util.function is NOT covered by `java.util.*`, so every program
# here uses _IMPORTS25.
# ---------------------------------------------------------------------------

_M25 = []

_IMPORTS25 = "import java.util.*;\nimport java.util.function.*;\n"


def _j25s(body):
    """Scanner-opening main, no helpers."""
    return _jscan(body, imports=_IMPORTS25)


def _j25(helpers, body):
    """Static helper methods above a Scanner-opening main."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS25,
    )


def _j25t(types, helpers, body):
    """Top-level types above `Main`, with optional helpers inside it."""
    return _jp(
        _IMPORTS25 + "\n"
        + types.strip("\n") + "\n\n"
        + "public class Main {\n"
        + (helpers.rstrip("\n") + "\n\n" if helpers.strip() else "")
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }\n}"
    )


_RD_W25 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")

_RD_N25 = ("        int n = sc.nextInt();\n"
           "        List<Integer> nums = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            nums.add(sc.nextInt());\n"
           "        }\n")

_W25 = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
        ["alpha", "beta", "gamma", "d"])

_N25 = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])

# (word list, limit) pairs, for the exercises that capture a threshold.
_WL25 = ((["ada", "bo", "cy"], 2), (["solo"], 3), (["x", "yy", "zzz"], 1),
         (["pear", "fig"], 3), (["alpha", "beta", "gamma", "d"], 4))


def _w25(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n25(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _wl25(ws, limit, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(limit)]), out)


def _jl25(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


# --- 25.1 The lambda ---------------------------------------------------------

_M25.append(_jlesson(
    "m25-lambda", "The lambda",
    "The named class you wrote in module 20, in one line.",
    """
Here is a comparator from module 20, written exactly the way that module
insisted on - as a named class:

```java
class ByLength implements Comparator<String> {
    @Override
    public int compare(String a, String b) {
        return Integer.compare(a.length(), b.length());
    }
}
words.sort(new ByLength());
```

Nine lines, of which one is the idea. Here is the same thing:

```java
words.sort((a, b) -> Integer.compare(a.length(), b.length()));
```

A **lambda expression** is an instance of an interface with a single abstract
method, written as just the parameters and the body. `Comparator<String>` has
one abstract method, `compare(String, String)`, so the compiler knows that
`(a, b)` are two Strings and that the result is the `int` that method returns.
Nothing else could it have meant.

**The syntax, in three forms:**

```java
(String a, String b) -> Integer.compare(a.length(), b.length())   // explicit types
(a, b) -> Integer.compare(a.length(), b.length())                 // inferred - normal
w -> w.length()                                                   // one parameter, no parens
() -> new ArrayList<String>()                                     // no parameters
```

**Expression body versus block body.** If the body is a single expression, its
value *is* the result - no `return`, no semicolon, no braces:

```java
(a, b) -> Integer.compare(a.length(), b.length())
```

If you need more than one statement, use braces - and then `return` comes back,
because it is now an ordinary method body:

```java
(a, b) -> {
    if (a.length() != b.length()) {
        return Integer.compare(a.length(), b.length());
    }
    return a.compareTo(b);
}
```

Mixing the two is the beginner's compile error: `w -> return w.length()` is not
legal, and neither is `w -> { w.length(); }` where a value was wanted.

**Where a lambda is allowed** is exactly where the compiler can name the
interface it must implement - an assignment, a parameter, a return. This is
called the **target type**. A lambda on its own, with nothing to be, does not
compile.
""",
    warmup=[
        _jq("A lambda is…",
            ["an instance of an interface with a single abstract method",
             "a new kind of method", "an anonymous class, exactly",
             "a function pointer"],
            0,
            "Which is why it needs a target type: the compiler has to know which "
            "interface."),
        _jq("`w -> w.length()` - where is the `return`?",
            ["An expression body IS the result; `return` would be a syntax error",
             "It is implied but you may write it",
             "It is missing and this does not compile",
             "It is only needed for ints"],
            0,
            "`return` appears only in a braced block body."),
    ],
    exercises=[
        _je("j25-lam-length", "Sorting with an arrow",
            "Sort the words by length, shortest first, with a lambda rather than the "
            "named `Comparator` class module 20 made you write. Replace `____` with that "
            "one line.",
            _j25s(_RD_W25
                  + "        words.sort((a, b) -> Integer.compare(a.length(), b.length()));\n"
                    "        System.out.println(words);\n"
                    "        System.out.println(words.size());"),
            "        words.sort((a, b) -> Integer.compare(a.length(), b.length()));",
            [_w25(ws, _nl(_jl25(sorted(ws, key=len)), len(ws))) for ws in _W25],
            hints=["`list.sort` takes a `Comparator<String>`, whose one abstract method "
                   "takes two Strings and returns an int.",
                   "So the lambda's parameters are `(a, b)` and its body is that int.",
                   "Never subtract lengths - module 20's rule still holds. Use "
                   "`Integer.compare`.",
                   "`words.sort((a, b) -> Integer.compare(a.length(), b.length()));`",
                   "The sort is stable, so words of equal length keep their input "
                   "order."],
            difficulty="Easy"),

        _jfix("j25-lam-return", "The return that cannot be there",
              "This lambda has an expression body but also a `return`, which is a syntax "
              "error - an expression body already *is* the result. Drop the `return`.",
              _j25s(_RD_W25
                    + "        words.sort((a, b) -> return Integer.compare(a.length(), b.length()));\n"
                      "        System.out.println(words);\n"
                      "        System.out.println(words.get(0));"),
              _j25s(_RD_W25
                    + "        words.sort((a, b) -> Integer.compare(a.length(), b.length()));\n"
                      "        System.out.println(words);\n"
                      "        System.out.println(words.get(0));"),
              [_w25(ws, _nl(_jl25(sorted(ws, key=len)), sorted(ws, key=len)[0]))
               for ws in _W25],
              hints=["`return` belongs to a braced block body, not an expression one.",
                     "Either delete the `return`, or wrap the body in `{ }` and keep it - "
                     "here, delete it.",
                     "`(a, b) -> Integer.compare(a.length(), b.length())`",
                     "After sorting, the first element is the shortest word."],
              difficulty="Easy"),

        _je("j25-lam-block", "When one expression is not enough",
            "Sort by length, and break ties alphabetically. That needs two statements, so "
            "the lambda needs a braced body - and inside braces, `return` is required. "
            "Replace `____` with the whole sort call.",
            _j25s(_RD_W25
                  + "        words.sort((a, b) -> {\n"
                    "            if (a.length() != b.length()) {\n"
                    "                return Integer.compare(a.length(), b.length());\n"
                    "            }\n"
                    "            return a.compareTo(b);\n"
                    "        });\n"
                    "        System.out.println(words);\n"
                    "        System.out.println(words.size());"),
            "        words.sort((a, b) -> {\n"
            "            if (a.length() != b.length()) {\n"
            "                return Integer.compare(a.length(), b.length());\n"
            "            }\n"
            "            return a.compareTo(b);\n"
            "        });",
            [_w25(ws, _nl(_jl25(sorted(ws, key=lambda w: (len(w), w))), len(ws)))
             for ws in _W25],
            hints=["Two statements means braces, and braces mean `return`.",
                   "The multi-key shape is module 20's: compare the first key, and only "
                   "fall through to the second when it ties.",
                   "`a.compareTo(b)` is the alphabetical tie-break.",
                   "Note the `);` at the end - the lambda is an argument, so the call's "
                   "parenthesis still has to close.",
                   "With ties broken explicitly, the result no longer depends on the "
                   "input order at all."],
            difficulty="Medium"),

        _jch("j25-lam-desc", "Largest first", "Easy",
             "Sort the numbers into descending order with a lambda, then print the list "
             "and its first element.",
             _j25s(_RD_N25
                   + "        nums.sort((a, b) -> Integer.compare(b, a));\n"
                     "        System.out.println(nums);\n"
                     "        System.out.println(nums.get(0));"),
             "        nums.sort((a, b) -> Integer.compare(b, a));\n"
             "        System.out.println(nums);\n"
             "        System.out.println(nums.get(0));",
             [_n25(xs, _nl(_jl25(sorted(xs, reverse=True)), sorted(xs, reverse=True)[0]))
              for xs in _N25],
             hints=["Descending is ascending with the two arguments swapped.",
                    "`(a, b) -> Integer.compare(b, a)` - note `b` first.",
                    "`Integer.compare(b, a)`, never `b - a`: the subtraction overflows "
                    "for large values, which is module 20's warning.",
                    "After the sort, `nums.get(0)` is the largest.",
                    "Two printed lines."]),
    ],
    quiz=[
        _jq("`words.sort((a, b) -> Integer.compare(a.length(), b.length()));` - what type is `a`?",
            ["String - inferred from Comparator<String>", "Object", "var", "int"],
            0,
            "The target type supplies the parameter types; you rarely write them."),
        _jq("Which does NOT compile?",
            ["w -> return w.length()", "w -> w.length()",
             "w -> { return w.length(); }", "(String w) -> w.length()"],
            0,
            "`return` is only legal inside a braced body."),
    ],
))


# --- 25.2 The four functional interfaces -------------------------------------

_M25.append(_jlesson(
    "m25-interfaces", "The four you will actually use",
    "`Predicate`, `Function`, `Consumer`, `Supplier` - and their one method each.",
    """
A lambda needs an interface to be an instance of. Rather than make you declare
one every time, the JDK ships the common shapes in **`java.util.function`** -
which is *not* covered by `import java.util.*`, so these programs import it
separately.

Four cover almost everything:

| Interface | Method | Shape | Reads as |
|---|---|---|---|
| `Predicate<T>` | `test(T)` | T in, `boolean` out | "is it?" |
| `Function<T, R>` | `apply(T)` | T in, R out | "turn it into" |
| `Consumer<T>` | `accept(T)` | T in, nothing out | "do this with it" |
| `Supplier<T>` | `get()` | nothing in, T out | "make me one" |

```java
Predicate<String> isLong  = w -> w.length() > 3;
Function<String, Integer> length = w -> w.length();
Consumer<String> shout    = w -> System.out.println(w.toUpperCase());
Supplier<List<String>> maker = () -> new ArrayList<>();

isLong.test("generics");   // true
length.apply("ada");       // 3
shout.accept("bo");        // prints BO
maker.get();               // a new empty list
```

The method name matters, because that is what you call: `test`, `apply`,
`accept`, `get`. There is no universal "call it" syntax - a lambda is an object,
and you invoke its one method.

**`BiFunction<T, U, R>`** takes two arguments (`apply(T, U)`), and
`BinaryOperator<T>` is the common case where both arguments and the result are
the same type - which is exactly what `Comparator` would be, if `Comparator` did
not predate all of this.

**The real payoff is a parameter.** Once a method can take behaviour as an
argument, one method serves every question you have not thought of yet:

```java
static int countMatching(List<String> items, Predicate<String> test) {
    int count = 0;
    for (String item : items) {
        if (test.test(item)) {
            count++;
        }
    }
    return count;
}

countMatching(words, w -> w.length() > 3);
countMatching(words, w -> w.startsWith("a"));
```

One loop, written once. That is the same argument as `Comparator` in module 20,
now generalised past sorting.
""",
    warmup=[
        _jq("Which interface has the method `test`?",
            ["Predicate", "Function", "Consumer", "Supplier"],
            0,
            "T in, boolean out."),
        _jq("`Supplier<T>`'s method takes…",
            ["no arguments, and returns a T", "a T, and returns nothing",
             "a T, and returns a T", "two arguments"],
            0,
            "`get()` - it makes one rather than transforming one."),
    ],
    exercises=[
        _je("j25-fi-predicate", "A question as a value",
            "Count how many words are longer than three characters, using a `Predicate` "
            "to hold the question. Replace `____` with its declaration.",
            _j25s(_RD_W25
                  + "        Predicate<String> isLong = w -> w.length() > 3;\n"
                    "        int count = 0;\n"
                    "        for (String w : words) {\n"
                    "            if (isLong.test(w)) {\n"
                    "                count++;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(count);\n"
                    "        System.out.println(words.size());"),
            "        Predicate<String> isLong = w -> w.length() > 3;",
            [_w25(ws, _nl(sum(1 for w in ws if len(w) > 3), len(ws))) for ws in _W25],
            hints=["The element type is `String` and the answer is a boolean, so the "
                   "type is `Predicate<String>`.",
                   "One parameter needs no parentheses: `w -> ...`.",
                   "`Predicate<String> isLong = w -> w.length() > 3;`",
                   "It is called with `.test(w)`, not by writing `isLong(w)`."],
            difficulty="Easy"),

        _je("j25-fi-function", "A transformation as a value",
            "Add up the lengths of every word, using a `Function` to hold the "
            "transformation from a word to its length. Replace `____` with its "
            "declaration.",
            _j25s(_RD_W25
                  + "        Function<String, Integer> length = w -> w.length();\n"
                    "        int total = 0;\n"
                    "        for (String w : words) {\n"
                    "            total += length.apply(w);\n"
                    "        }\n"
                    "        System.out.println(total);\n"
                    "        System.out.println(words.size());"),
            "        Function<String, Integer> length = w -> w.length();",
            [_w25(ws, _nl(sum(len(w) for w in ws), len(ws))) for ws in _W25],
            hints=["`Function<T, R>` names the input type first and the result type "
                   "second.",
                   "A `String` goes in and an `int` comes out - but a type argument must "
                   "be a reference type, so the result is `Integer`.",
                   "`Function<String, Integer> length = w -> w.length();`",
                   "`total += length.apply(w)` unboxes the `Integer` back to an `int`."],
            difficulty="Easy"),

        _je("j25-fi-consumer", "An action as a value",
            "Print every word in capitals, using a `Consumer` to hold the action. "
            "Replace `____` with its declaration.",
            _j25s(_RD_W25
                  + "        Consumer<String> shout = w -> System.out.println(w.toUpperCase());\n"
                    "        for (String w : words) {\n"
                    "            shout.accept(w);\n"
                    "        }\n"
                    "        System.out.println(words.size());"),
            "        Consumer<String> shout = w -> System.out.println(w.toUpperCase());",
            [_w25(ws, _nl(*([w.upper() for w in ws] + [len(ws)]))) for ws in _W25],
            hints=["A `Consumer<T>` takes a T and returns nothing.",
                   "The body is a statement with no value, which is fine - the interface "
                   "expects none.",
                   "`Consumer<String> shout = w -> System.out.println(w.toUpperCase());`",
                   "Call it with `.accept(w)`.",
                   "One line per word, then the count."],
            difficulty="Easy"),

        _jch("j25-fi-higher", "Behaviour as a parameter", "Medium",
             "Write `countMatching`, which counts the elements of a list that satisfy a "
             "`Predicate` handed to it. `main` calls it twice with two different "
             "questions and one loop.",
             _j25("    static int countMatching(List<String> items, Predicate<String> test) {\n"
                  "        int count = 0;\n"
                  "        for (String item : items) {\n"
                  "            if (test.test(item)) {\n"
                  "                count++;\n"
                  "            }\n"
                  "        }\n"
                  "        return count;\n"
                  "    }",
                  _RD_W25
                  + "        System.out.println(countMatching(words, w -> w.length() > 3));\n"
                    "        System.out.println(countMatching(words, w -> w.startsWith(\"a\")));\n"
                    "        System.out.println(words.size());"),
             "    static int countMatching(List<String> items, Predicate<String> test) {\n"
             "        int count = 0;\n"
             "        for (String item : items) {\n"
             "            if (test.test(item)) {\n"
             "                count++;\n"
             "            }\n"
             "        }\n"
             "        return count;\n"
             "    }",
             [_w25(ws, _nl(sum(1 for w in ws if len(w) > 3),
                           sum(1 for w in ws if w.startswith("a")),
                           len(ws)))
              for ws in _W25],
             hints=["The second parameter is the behaviour: `Predicate<String> test`.",
                    "Inside, ask it with `test.test(item)`.",
                    "The two call sites differ only in the lambda, which is the entire "
                    "point.",
                    "`startsWith` is module 7's, and works unchanged here.",
                    "Three printed lines."]),
    ],
    quiz=[
        _jq("`Function<String, Integer> f = w -> w.length();` is called with…",
            ["f.apply(w)", "f(w)", "f.test(w)", "f.get(w)"],
            0,
            "A lambda is an object; you invoke its single method by name."),
        _jq("Why does `countMatching(List, Predicate<String>)` beat two separate methods?",
            ["The loop is written once and the question varies per call",
             "It is faster", "It avoids generics", "It allows null"],
            0,
            "Behaviour as a parameter - the same argument as Comparator, generalised."),
    ],
))


# --- 25.3 Your own functional interface --------------------------------------

_M25.append(_jlesson(
    "m25-own", "Writing the interface yourself",
    "There is no magic: a lambda implements an interface, and you can declare it.",
    """
`Predicate` and friends are ordinary interfaces in an ordinary package. Nothing
stops you declaring your own - and doing it once is what makes lambdas stop
feeling like new syntax:

```java
@FunctionalInterface
interface Transform {
    String apply(String value);
}

Transform shout = w -> w.toUpperCase();
System.out.println(shout.apply("ada"));    // ADA
```

The name of the method is yours (`apply`, `run`, `convert` - whatever reads
best), and the lambda fits because the interface has **exactly one abstract
method**. That is the only requirement.

**`@FunctionalInterface`** is optional but worth writing. It does not make the
interface functional - having one abstract method does that. What it does is
make the compiler *check*, and fail the interface itself the day someone adds a
second method, instead of failing every lambda that used it:

```java
@FunctionalInterface
interface Transform {
    String apply(String value);
    String undo(String value);      // COMPILE ERROR on the annotation
}
```

**What does not count against the one-method budget:** `default` and `static`
interface methods (module 14) have bodies, so they are not abstract, and an
interface may have any number of them and still be functional. Nor do
`public` overrides of `Object`'s own methods, like `equals`.

**When to declare your own rather than use `java.util.function`:** when the
name carries meaning your reader needs. `Transform` and `Combiner` say more at a
call site than `Function<String, String>` and `BinaryOperator<Integer>` do. When
it says nothing extra, use the standard one - everybody already knows it.
""",
    warmup=[
        _jq("What makes an interface usable as a lambda's type?",
            ["Exactly one abstract method", "The @FunctionalInterface annotation",
             "Being in java.util.function", "Having no methods"],
            0,
            "The annotation only asks the compiler to check that."),
        _jq("A functional interface may also declare…",
            ["any number of default and static methods",
             "one more abstract method", "nothing else", "only fields"],
            0,
            "Those have bodies, so they are not abstract."),
    ],
    exercises=[
        _je("j25-own-iface", "Declaring the shape",
            "`main` needs an interface a `String`-to-`String` lambda can be an instance "
            "of. Replace `____` with that interface, named `Transform`, with one abstract "
            "method `apply` - and annotated so the compiler enforces the single-method "
            "rule.",
            _j25t("@FunctionalInterface\n"
                  "interface Transform {\n"
                  "    String apply(String value);\n"
                  "}", "",
                  _RD_W25
                  + "        Transform shout = w -> w.toUpperCase();\n"
                    "        for (String w : words) {\n"
                    "            System.out.println(shout.apply(w));\n"
                    "        }\n"
                    "        System.out.println(words.size());"),
            "@FunctionalInterface\n"
            "interface Transform {\n"
            "    String apply(String value);\n"
            "}",
            [_w25(ws, _nl(*([w.upper() for w in ws] + [len(ws)]))) for ws in _W25],
            hints=["Interface methods are implicitly public and abstract, so the "
                   "declaration is one line with a semicolon.",
                   "`String apply(String value);` - a String in, a String out.",
                   "`@FunctionalInterface` sits directly above `interface Transform {`.",
                   "Only `Main` may be `public`; the interface is package-private.",
                   "The lambda `w -> w.toUpperCase()` then fits it exactly."],
            difficulty="Medium"),

        _je("j25-own-annotation", "Asking the compiler to check",
            "`Combiner` folds two ints into one, and `main` uses it to total the "
            "numbers. Replace `____` with the annotation that makes the compiler reject "
            "the interface if a second abstract method is ever added.",
            _j25t("@FunctionalInterface\n"
                  "interface Combiner {\n"
                  "    int combine(int a, int b);\n"
                  "}", "",
                  _RD_N25
                  + "        Combiner add = (a, b) -> a + b;\n"
                    "        int total = 0;\n"
                    "        for (int x : nums) {\n"
                    "            total = add.combine(total, x);\n"
                    "        }\n"
                    "        System.out.println(total);\n"
                    "        System.out.println(nums.size());"),
            "@FunctionalInterface",
            [_n25(xs, _nl(sum(xs), len(xs))) for xs in _N25],
            hints=["It is optional - the interface already works without it.",
                   "What it buys is the error landing on the INTERFACE rather than on "
                   "every lambda that used it.",
                   "`@FunctionalInterface`",
                   "Note this one uses primitive `int` parameters, which a "
                   "`Function<Integer, Integer>` could not do without boxing.",
                   "The fold starts at 0 and combines one number at a time."],
            difficulty="Medium"),

        _jfix("j25-own-two", "One abstract method, not two",
              "`Transform` declares two abstract methods, so it is not a functional "
              "interface - the `@FunctionalInterface` annotation fails, and so does the "
              "lambda that tried to be one. `undo` is unused; remove it.",
              _j25t("@FunctionalInterface\n"
                    "interface Transform {\n"
                    "    String apply(String value);\n"
                    "\n"
                    "    String undo(String value);\n"
                    "}", "",
                    _RD_W25
                    + "        Transform shout = w -> w.toUpperCase();\n"
                      "        System.out.println(shout.apply(words.get(0)));\n"
                      "        System.out.println(words.size());"),
              _j25t("@FunctionalInterface\n"
                    "interface Transform {\n"
                    "    String apply(String value);\n"
                    "}", "",
                    _RD_W25
                    + "        Transform shout = w -> w.toUpperCase();\n"
                      "        System.out.println(shout.apply(words.get(0)));\n"
                      "        System.out.println(words.size());"),
              [_w25(ws, _nl(ws[0].upper(), len(ws))) for ws in _W25],
              hints=["The error names the annotation: *Transform is not a functional "
                     "interface - multiple non-overriding abstract methods*.",
                     "A lambda supplies ONE method body, so it can never satisfy two "
                     "abstract methods.",
                     "Delete `undo` entirely.",
                     "Had `undo` been given a `default` body instead, the interface would "
                     "still be functional - default methods are not abstract.",
                     "Two printed lines."],
              difficulty="Medium"),

        _jch("j25-own-use", "A method that takes your interface", "Medium",
             "Write `mapAll`, which applies a `Transform` to every element of a list and "
             "returns the results as a new list. `main` calls it twice with two different "
             "lambdas.",
             _j25t("@FunctionalInterface\n"
                   "interface Transform {\n"
                   "    String apply(String value);\n"
                   "}",
                   "    static List<String> mapAll(List<String> items, Transform t) {\n"
                   "        List<String> out = new ArrayList<>();\n"
                   "        for (String item : items) {\n"
                   "            out.add(t.apply(item));\n"
                   "        }\n"
                   "        return out;\n"
                   "    }",
                   _RD_W25
                   + "        System.out.println(mapAll(words, w -> w.toUpperCase()));\n"
                     "        System.out.println(mapAll(words, w -> w + \"!\"));\n"
                     "        System.out.println(words.size());"),
             "    static List<String> mapAll(List<String> items, Transform t) {\n"
             "        List<String> out = new ArrayList<>();\n"
             "        for (String item : items) {\n"
             "            out.add(t.apply(item));\n"
             "        }\n"
             "        return out;\n"
             "    }",
             [_w25(ws, _nl(_jl25([w.upper() for w in ws]),
                           _jl25([w + "!" for w in ws]),
                           len(ws)))
              for ws in _W25],
             hints=["The second parameter is the behaviour: `Transform t`.",
                    "Build a new list rather than modifying the input - `mapAll` is "
                    "asked for results, not for a side effect.",
                    "`out.add(t.apply(item));`",
                    "The original list is untouched, so `words.size()` is unchanged at "
                    "the end.",
                    "This is `map`, hand-written. Module 26 is the JDK's version."]),
    ],
    quiz=[
        _jq("`@FunctionalInterface` on an interface with two abstract methods…",
            ["fails to compile, which is the point of the annotation",
             "is ignored", "makes it functional", "is a warning"],
            0,
            "It moves the error to the declaration instead of every lambda."),
        _jq("When is your own interface better than `Function<String, String>`?",
            ["When a domain name reads better at the call site",
             "Always", "Never", "Only for primitives"],
            0,
            "`Transform` says something; `Function<String, String>` says only its shape."),
    ],
))


# --- 25.4 Capture and scope --------------------------------------------------

_M25.append(_jlesson(
    "m25-capture", "What a lambda can see",
    "Effectively final, and the scope a lambda does *not* open.",
    """
A lambda can use the local variables around it - that is what makes it useful:

```java
int limit = sc.nextInt();
Predicate<String> longer = w -> w.length() > limit;    // captures `limit`
```

But only if the captured variable is **final or effectively final** -
"effectively final" meaning you never assign to it after its initialisation.
This does not compile:

```java
int count = 0;
Consumer<String> tally = w -> count++;    // ERROR: must be final or effectively final
```

*local variables referenced from a lambda expression must be final or
effectively final.* The reason is that a lambda can outlive the method that
made it - it can be stored, returned, or run later - and a local variable
cannot. Java captures the **value**, so allowing the assignment would mean
writing to a copy and silently losing it.

**The workaround is usually to stop mutating.** Count with an ordinary loop, or
have the lambda *answer* rather than *accumulate*. Reaching for a one-element
array to smuggle a mutable slot through is a well-known trick and almost always
a sign the code wanted a plain loop.

**A lambda is not a new scope.** Unlike an anonymous class, a lambda body lives
in the enclosing method's scope, so it cannot redeclare a name that is already
there:

```java
String w = words.get(0);
Predicate<String> isLong = w -> w.length() > 3;   // ERROR: w is already defined
```

The same rule means `this` inside a lambda is the *enclosing* object, not the
lambda - which is the single most useful practical difference from an anonymous
class, where `this` means the anonymous instance.

**Capture is what makes a returned lambda work.** A method can build behaviour
out of its arguments and hand it back:

```java
static Predicate<String> longerThan(int limit) {
    return w -> w.length() > limit;
}
```

`limit` is a parameter, so it is effectively final, and the returned lambda
carries its value with it. That is a **closure**, and it is how you get
configurable behaviour without a class.
""",
    warmup=[
        _jq("`int count = 0; Consumer<String> c = w -> count++;`",
            ["Does not compile - count must be effectively final",
             "Compiles and counts", "Compiles but counts wrongly",
             "Compiles with a warning"],
            0,
            "Java captures the value, so the assignment is refused outright."),
        _jq("Inside a lambda, `this` refers to…",
            ["the enclosing object", "the lambda itself",
             "null", "the functional interface"],
            0,
            "Unlike an anonymous class, a lambda opens no new scope."),
    ],
    exercises=[
        _je("j25-cap-effective", "Capturing a value",
            "Read a limit, then count the words longer than it. The lambda captures "
            "`limit`, which is never reassigned and so is effectively final. Replace "
            "`____` with the predicate's declaration.",
            _j25s(_RD_W25
                  + "        int limit = sc.nextInt();\n"
                    "        Predicate<String> longer = w -> w.length() > limit;\n"
                    "        int count = 0;\n"
                    "        for (String w : words) {\n"
                    "            if (longer.test(w)) {\n"
                    "                count++;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(count);\n"
                    "        System.out.println(limit);"),
            "        Predicate<String> longer = w -> w.length() > limit;",
            [_wl25(ws, limit, _nl(sum(1 for w in ws if len(w) > limit), limit))
             for (ws, limit) in _WL25],
            hints=["`limit` is read from input and then never assigned again, which is "
                   "exactly what effectively final means.",
                   "`Predicate<String> longer = w -> w.length() > limit;`",
                   "`count` is assigned inside the loop, but the lambda never touches "
                   "`count` - only the loop does.",
                   "That distinction is the whole lesson: capture is fine, capturing "
                   "something you then mutate is not."],
            difficulty="Medium"),

        _jfix("j25-cap-final", "The counter the lambda cannot keep",
              "The `Consumer` tries to increment a captured local, which does not "
              "compile. The `Predicate` is fine - it only reads. Drop the consumer and do "
              "the counting in the loop that was already there.",
              _j25s(_RD_W25
                    + "        int count = 0;\n"
                      "        Predicate<String> isLong = w -> w.length() > 3;\n"
                      "        Consumer<String> tally = w -> { if (isLong.test(w)) count++; };\n"
                      "        for (String w : words) {\n"
                      "            tally.accept(w);\n"
                      "        }\n"
                      "        System.out.println(count);\n"
                      "        System.out.println(words.size());"),
              _j25s(_RD_W25
                    + "        int count = 0;\n"
                      "        Predicate<String> isLong = w -> w.length() > 3;\n"
                      "        for (String w : words) {\n"
                      "            if (isLong.test(w)) {\n"
                      "                count++;\n"
                      "            }\n"
                      "        }\n"
                      "        System.out.println(count);\n"
                      "        System.out.println(words.size());"),
              [_w25(ws, _nl(sum(1 for w in ws if len(w) > 3), len(ws))) for ws in _W25],
              hints=["The error is on `count++` inside the lambda: *local variables "
                     "referenced from a lambda expression must be final or effectively "
                     "final*.",
                     "The predicate is untouched - reading a captured value was never "
                     "the problem.",
                     "Move the `if` into the loop and increment there.",
                     "`count` is still a plain local; the loop may assign to it freely "
                     "because the loop is not a lambda.",
                     "Wanting to mutate from inside a lambda is usually the signal that "
                     "a plain loop is the honest tool."],
              difficulty="Medium"),

        _jfix("j25-cap-shadow", "The name that was already taken",
              "The lambda's parameter is called `w`, and so is a local variable declared "
              "two lines above - and a lambda opens no new scope, so that is a redeclaration "
              "and does not compile. Rename the lambda's parameter.",
              _j25s(_RD_W25
                    + "        String w = words.get(0);\n"
                      "        Predicate<String> isLong = w -> w.length() > 3;\n"
                      "        System.out.println(w);\n"
                      "        System.out.println(isLong.test(w));"),
              _j25s(_RD_W25
                    + "        String w = words.get(0);\n"
                      "        Predicate<String> isLong = value -> value.length() > 3;\n"
                      "        System.out.println(w);\n"
                      "        System.out.println(isLong.test(w));"),
              [_w25(ws, _nl(ws[0], _jbool(len(ws[0]) > 3))) for ws in _W25],
              hints=["The error is *variable w is already defined in method main*.",
                     "An anonymous class WOULD have allowed this, because it opens its "
                     "own scope. A lambda does not.",
                     "Any unused name works: `value`, `s`, `word`.",
                     "`Predicate<String> isLong = value -> value.length() > 3;`",
                     "The test still runs against the local `w`, which is the first "
                     "word."],
              difficulty="Medium"),

        _jch("j25-cap-factory", "Behaviour built to order", "Hard",
             "Write `longerThan`, a method that takes a limit and RETURNS a predicate "
             "testing against it - a closure over its own parameter. `main` reads the "
             "limit, builds the predicate and counts with it.",
             _j25("    static Predicate<String> longerThan(int limit) {\n"
                  "        return w -> w.length() > limit;\n"
                  "    }",
                  _RD_W25
                  + "        int limit = sc.nextInt();\n"
                    "        Predicate<String> test = longerThan(limit);\n"
                    "        int count = 0;\n"
                    "        for (String w : words) {\n"
                    "            if (test.test(w)) {\n"
                    "                count++;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(count);\n"
                    "        System.out.println(limit);"),
             "    static Predicate<String> longerThan(int limit) {\n"
             "        return w -> w.length() > limit;\n"
             "    }",
             [_wl25(ws, limit, _nl(sum(1 for w in ws if len(w) > limit), limit))
              for (ws, limit) in _WL25],
             hints=["The RETURN type is the behaviour: `Predicate<String>`.",
                    "The body is a single `return` of a lambda.",
                    "`return w -> w.length() > limit;`",
                    "A parameter is effectively final unless you assign to it, so "
                    "capturing `limit` is legal.",
                    "The returned lambda outlives the call to `longerThan`, carrying the "
                    "captured value with it - that is a closure.",
                    "Two printed lines: the count, then the limit."]),
    ],
    quiz=[
        _jq("Why must a captured local be effectively final?",
            ["The lambda captures the value and can outlive the method",
             "For speed", "Because of erasure", "It need not be"],
            0,
            "Assigning would write to a copy and lose it silently."),
        _jq("`String w = ...; Predicate<String> p = w -> ...;` fails because…",
            ["a lambda opens no new scope, so `w` is already defined",
             "predicates cannot take Strings", "`w` is not final", "of erasure"],
            0,
            "An anonymous class would have allowed the shadowing; a lambda does not."),
    ],
))


# --- 25.5 Method references --------------------------------------------------

_M25.append(_jlesson(
    "m25-methodref", "Method references",
    "When the lambda only forwards, name the method instead.",
    """
Some lambdas do nothing but pass their argument straight to a method:

```java
w -> w.toUpperCase()
w -> System.out.println(w)
w -> Integer.parseInt(w)
```

Each has a shorter spelling - a **method reference**, written with `::`:

```java
String::toUpperCase
System.out::println
Integer::parseInt
```

They mean exactly the same thing and produce exactly the same object. There are
four kinds, and it is worth being able to name them:

| Kind | Written | Equivalent lambda |
|---|---|---|
| **static** | `Integer::parseInt` | `s -> Integer.parseInt(s)` |
| **bound instance** | `System.out::println` | `s -> System.out.println(s)` |
| **unbound instance** | `String::toUpperCase` | `s -> s.toUpperCase()` |
| **constructor** | `ArrayList::new` | `() -> new ArrayList<>()` |

The one that surprises people is the **unbound** kind: `String::toUpperCase`
looks like it is missing an argument, but it is not. The lambda's parameter
becomes the *receiver* - the thing the method is called **on** - rather than an
argument passed to it.

**`Comparator.comparing` pairs with them beautifully.** It takes a `Function`
that extracts a sort key and builds the comparator for you:

```java
words.sort(Comparator.comparing(String::length));
```

which is module 20's "sort by a key" in one line, and reads better than the
two-parameter lambda it replaces.

**`forEach` is on every collection**, not just streams - `Iterable.forEach`
takes a `Consumer`:

```java
words.forEach(System.out::println);
```

**When not to use one.** If the lambda does anything besides forward - adds a
condition, changes the argument, calls two methods - it is not a method
reference, and trying to force one produces something less readable than the
lambda you started with.
""",
    warmup=[
        _jq("`String::toUpperCase` as a `Function<String, String>` means…",
            ["s -> s.toUpperCase()", "s -> String.toUpperCase(s)",
             "() -> new String()", "it does not compile"],
            0,
            "The unbound kind: the parameter becomes the receiver."),
        _jq("`ArrayList::new` is a…",
            ["constructor reference", "static method reference",
             "bound instance reference", "syntax error"],
            0,
            "It fits a `Supplier`, among others."),
    ],
    exercises=[
        _je("j25-mr-comparing", "Sorting by an extracted key",
            "Sort the words by length using `Comparator.comparing` and a method "
            "reference for the key, rather than a two-parameter lambda. Replace `____` "
            "with that sort call.",
            _j25s(_RD_W25
                  + "        words.sort(Comparator.comparing(String::length));\n"
                    "        System.out.println(words);\n"
                    "        System.out.println(words.size());"),
            "        words.sort(Comparator.comparing(String::length));",
            [_w25(ws, _nl(_jl25(sorted(ws, key=len)), len(ws))) for ws in _W25],
            hints=["`Comparator.comparing` takes a `Function` that extracts the key to "
                   "sort on.",
                   "The key here is the length, and `String::length` is the unbound "
                   "reference for it.",
                   "`words.sort(Comparator.comparing(String::length));`",
                   "This is the same result as `(a, b) -> Integer.compare(a.length(), "
                   "b.length())`, said once instead of twice.",
                   "Still stable, so equal-length words keep their input order."],
            difficulty="Medium"),

        _je("j25-mr-println", "Printing without a lambda",
            "Print every word with `forEach` - which every collection has, taking a "
            "`Consumer` - and a bound method reference rather than a lambda. Replace "
            "`____` with that line.",
            _j25s(_RD_W25
                  + "        words.forEach(System.out::println);\n"
                    "        System.out.println(words.size());"),
            "        words.forEach(System.out::println);",
            [_w25(ws, _nl(*(list(ws) + [len(ws)]))) for ws in _W25],
            hints=["`w -> System.out.println(w)` forwards its argument and does nothing "
                   "else.",
                   "`System.out` is a specific object, so the receiver is already fixed - "
                   "this is the BOUND kind.",
                   "`words.forEach(System.out::println);`",
                   "`forEach` here is `Iterable.forEach`; no stream is involved.",
                   "One line per word, then the count."],
            difficulty="Easy"),

        _je("j25-mr-static", "A static method as a value",
            "The input is a list of numeric tokens read as text. Add them up using a "
            "`Function` built from a static method reference. Replace `____` with its "
            "declaration.",
            _j25s(_RD_W25
                  + "        Function<String, Integer> parse = Integer::parseInt;\n"
                    "        int total = 0;\n"
                    "        for (String w : words) {\n"
                    "            total += parse.apply(w);\n"
                    "        }\n"
                    "        System.out.println(total);\n"
                    "        System.out.println(words.size());"),
            "        Function<String, Integer> parse = Integer::parseInt;",
            [_w25([str(x) for x in xs], _nl(sum(xs), len(xs))) for xs in _N25],
            hints=["The lambda would be `s -> Integer.parseInt(s)` - pure forwarding.",
                   "`Integer::parseInt` is a STATIC reference: the class name, then the "
                   "method.",
                   "`Function<String, Integer> parse = Integer::parseInt;`",
                   "`parseInt` handles a leading minus sign, so negative tokens are "
                   "fine.",
                   "The total unboxes back to an `int` on the way into `total`."],
            difficulty="Medium"),

        _jch("j25-mr-convert", "Three references, no lambdas", "Medium",
             "Build a list of the words in capitals and print each one - writing the "
             "transformation and the printing as method references rather than lambdas. "
             "Print the new list's size at the end.",
             _j25s(_RD_W25
                   + "        Function<String, String> up = String::toUpperCase;\n"
                     "        List<String> shouts = new ArrayList<>();\n"
                     "        for (String w : words) {\n"
                     "            shouts.add(up.apply(w));\n"
                     "        }\n"
                     "        shouts.forEach(System.out::println);\n"
                     "        System.out.println(shouts.size());"),
             "        Function<String, String> up = String::toUpperCase;\n"
             "        List<String> shouts = new ArrayList<>();\n"
             "        for (String w : words) {\n"
             "            shouts.add(up.apply(w));\n"
             "        }\n"
             "        shouts.forEach(System.out::println);\n"
             "        System.out.println(shouts.size());",
             [_w25(ws, _nl(*([w.upper() for w in ws] + [len(ws)]))) for ws in _W25],
             hints=["`String::toUpperCase` is the UNBOUND kind - the argument becomes "
                    "the receiver.",
                    "Its type is `Function<String, String>`: a String in, a String out.",
                    "Build the new list with an ordinary loop and `up.apply(w)`.",
                    "`shouts.forEach(System.out::println);` for the printing.",
                    "The last line is the size of the NEW list, which equals the "
                    "original's."]),
    ],
    quiz=[
        _jq("`words.sort(Comparator.comparing(String::length));` replaces…",
            ["(a, b) -> Integer.compare(a.length(), b.length())",
             "a -> a.length()", "String::compareTo", "nothing"],
            0,
            "`comparing` takes the key extractor and builds the comparator."),
        _jq("When is a method reference the WRONG choice?",
            ["When the lambda does anything besides forward its argument",
             "When the method is static", "For constructors", "Inside forEach"],
            0,
            "Forcing one then reads worse than the lambda it replaced."),
    ],
))


# --- Capstone ----------------------------------------------------------------

_M25_CAP_HELPERS = (
    "    static int countMatching(List<String> items, Predicate<String> test) {\n"
    "        int count = 0;\n"
    "        for (String item : items) {\n"
    "            if (test.test(item)) {\n"
    "                count++;\n"
    "            }\n"
    "        }\n"
    "        return count;\n"
    "    }\n"
    "\n"
    "    static List<String> mapAll(List<String> items, Function<String, String> f) {\n"
    "        List<String> out = new ArrayList<>();\n"
    "        for (String item : items) {\n"
    "            out.add(f.apply(item));\n"
    "        }\n"
    "        return out;\n"
    "    }\n"
    "\n"
    "    static void each(List<String> items, Consumer<String> action) {\n"
    "        for (String item : items) {\n"
    "            action.accept(item);\n"
    "        }\n"
    "    }"
)

_M25_CAP_BODY = (
    _RD_W25
    + "        int limit = sc.nextInt();\n"
      "        System.out.println(countMatching(words, w -> w.length() > limit));\n"
      "        List<String> shouts = mapAll(words, String::toUpperCase);\n"
      "        System.out.println(shouts);\n"
      "        each(shouts, System.out::println);\n"
      "        System.out.println(words.size());"
)


def _m25_cap_case(ws, limit):
    return _wl25(ws, limit,
                 _nl(*([sum(1 for w in ws if len(w) > limit),
                        _jl25([w.upper() for w in ws])]
                       + [w.upper() for w in ws]
                       + [len(ws)])))


_M25_CAP = _jcap(
    "The tiny toolkit",
    """
Three methods that take behaviour as a parameter - one of each shape - and a
`main` that supplies that behaviour three different ways.

* **`countMatching(items, test)`** - takes a `Predicate<String>` and counts the
  elements that satisfy it.
* **`mapAll(items, f)`** - takes a `Function<String, String>` and returns a new
  list of the results, leaving the input alone.
* **`each(items, action)`** - takes a `Consumer<String>` and runs it against
  every element, returning nothing.

`main` then calls them with a **capturing lambda** (`w -> w.length() > limit`),
an **unbound method reference** (`String::toUpperCase`) and a **bound method
reference** (`System.out::println`) - the three ways you will actually write
behaviour in real Java.

Between them these three methods are `filter`, `map` and `forEach`,
hand-written. Module 26 hands you the JDK's version and a pipeline to chain them
in.
""",
    _jch("j25-cap-toolkit", "The tiny toolkit", "Hard",
         "Write the three methods described in the brief so the given `main` compiles "
         "and prints its lines.",
         _j25(_M25_CAP_HELPERS, _M25_CAP_BODY),
         _M25_CAP_HELPERS,
         [_m25_cap_case(ws, limit) for (ws, limit) in _WL25],
         hints=["`countMatching` takes a `Predicate<String>` and asks it with "
                "`test.test(item)`.",
                "`mapAll` takes a `Function<String, String>` and calls `f.apply(item)`, "
                "building a NEW list.",
                "`each` takes a `Consumer<String>` and calls `action.accept(item)`; it "
                "returns `void`.",
                "All three are generic in nothing - the element type is `String` "
                "throughout, so no `<T>` is needed.",
                "`w -> w.length() > limit` captures `limit`, which is effectively final "
                "because it is read once and never reassigned.",
                "`String::toUpperCase` is unbound (the argument is the receiver); "
                "`System.out::println` is bound (the receiver is already fixed).",
                "Output order: the count, then the shouted list on one line, then each "
                "shouted word on its own line, then the original size."]),
    example_io="stdin:  3\n        ada bo cy\n        2\n\n"
               "stdout: 1\n        [ADA, BO, CY]\n        ADA\n        BO\n        CY\n"
               "        3",
    rubric=[
        "`countMatching` takes a `Predicate<String>` and returns an int.",
        "`mapAll` takes a `Function<String, String>` and returns a new list, leaving the input unmodified.",
        "`each` takes a `Consumer<String>` and returns void.",
        "Each helper invokes its parameter by the interface's own method name (`test`, `apply`, `accept`).",
        "`main` passes a capturing lambda, an unbound method reference and a bound method reference.",
        "No helper hard-codes the behaviour it was handed.",
        "The lines are printed in the order the brief lists them.",
    ],
)


_MODULES.append(_jmod(
    25, 8, "Java 8+",
    "Lambdas, functional interfaces and method references",
    "A lambda is an instance of a one-method interface - and once behaviour can be a "
    "value, the loop you keep rewriting becomes a parameter.",
    """
Module 20 made you write every `Comparator` as a named class, and module 14
every interface implementation. This module collapses them:

```java
words.sort((a, b) -> Integer.compare(a.length(), b.length()));
```

A **lambda** is an instance of an interface with exactly one abstract method,
written as parameters and a body. The compiler works out the types from the
**target type** - the interface it is being asked to be.

* **`java.util.function`** ships the four shapes you need almost every time:
  `Predicate<T>` (`test`), `Function<T, R>` (`apply`), `Consumer<T>` (`accept`)
  and `Supplier<T>` (`get`). It is not covered by `import java.util.*`.
* **Your own** works identically - one abstract method, and
  `@FunctionalInterface` to make the compiler enforce that. Declaring one is
  what proves there is no magic here.
* **Capture** is by value, so a captured local must be final or effectively
  final. A lambda opens no new scope, so it cannot shadow a name either - and
  `this` means the enclosing object.
* **Method references** (`String::toUpperCase`, `System.out::println`,
  `Integer::parseInt`, `ArrayList::new`) are the shorthand for a lambda that
  only forwards.

The real prize is behaviour as a parameter: `countMatching(items, test)` is one
loop that answers every question you have not thought of yet. Module 26 chains
that idea into a pipeline.
""",
    _M25,
    capstone=_M25_CAP,
    objectives=[
        "Rewrite a named `Comparator` class as a lambda, and say what supplied the parameter types.",
        "Choose between an expression body and a braced body, and say where `return` is legal.",
        "Name the four `java.util.function` interfaces, their methods and their shapes.",
        "Declare your own functional interface and explain what `@FunctionalInterface` checks.",
        "Say why a captured local must be effectively final, and fix code that mutates one.",
        "Explain why a lambda cannot shadow an enclosing local, and what `this` means inside one.",
        "Write a method that returns a lambda closing over its parameter.",
        "Convert forwarding lambdas into the four kinds of method reference, and say when not to.",
    ],
    why="Lambdas are the dividing line between Java that looks like 2005 and Java that "
        "looks like today, and every modern API - streams, `Comparator.comparing`, "
        "`forEach`, anything reactive - is designed around them. In interviews the "
        "questions are predictable and specific: what is a functional interface, why must "
        "a captured variable be effectively final, what does `this` mean in a lambda, and "
        "what is the difference from an anonymous class. Each has a one-line answer you "
        "now have.",
    est_minutes=330,
    glossary=[
        _jg("lambda expression", "An instance of a functional interface written as "
                                 "parameters and a body: `w -> w.length()`."),
        _jg("functional interface", "An interface with exactly one abstract method - the "
                                    "only thing a lambda can be."),
        _jg("@FunctionalInterface", "Optional annotation asking the compiler to fail the "
                                    "interface if it ever stops having exactly one "
                                    "abstract method."),
        _jg("target type", "The interface the compiler expects at that position, which is "
                           "what gives a lambda its meaning and its parameter types."),
        _jg("expression body", "A lambda body that is a single expression; its value is "
                               "the result, and `return` is illegal."),
        _jg("block body", "A braced lambda body of one or more statements, where `return` "
                          "is required to produce a value."),
        _jg("Predicate<T>", "`boolean test(T)` - a question."),
        _jg("Function<T, R>", "`R apply(T)` - a transformation."),
        _jg("Consumer<T>", "`void accept(T)` - an action."),
        _jg("Supplier<T>", "`T get()` - a factory."),
        _jg("effectively final", "A local never assigned after initialisation. Only such "
                                 "locals may be captured."),
        _jg("closure", "A lambda that captures a value from its enclosing scope and "
                       "carries it beyond that scope's lifetime."),
        _jg("method reference", "`Class::method` or `object::method` - the shorthand for "
                                "a lambda that only forwards its argument."),
    ],
    cheatsheet="""
```java
import java.util.function.*;      // NOT covered by java.util.*

// --- syntax ---------------------------------------------------------------
(a, b) -> Integer.compare(a.length(), b.length())   // inferred types
w -> w.length()                                     // one param, no parens
() -> new ArrayList<String>()                       // no params
(a, b) -> { ...; return x; }                        // block body NEEDS return
w -> return w.length()                              // ERROR: expression body

// --- the four shapes ------------------------------------------------------
Predicate<String>          isLong = w -> w.length() > 3;      // .test(w)
Function<String, Integer>  len    = w -> w.length();          // .apply(w)
Consumer<String>           shout  = w -> System.out.println(w);  // .accept(w)
Supplier<List<String>>     maker  = () -> new ArrayList<>();  // .get()

// --- your own -------------------------------------------------------------
@FunctionalInterface
interface Transform { String apply(String value); }   // exactly ONE abstract method
                                                      // default/static ones do not count

// --- capture --------------------------------------------------------------
int limit = 3;
Predicate<String> p = w -> w.length() > limit;   // OK: limit effectively final
int count = 0;
Consumer<String> c = w -> count++;               // ERROR: must be effectively final
String w = "x";
Predicate<String> q = w -> ...;                  // ERROR: no new scope, w already defined
// `this` inside a lambda == the ENCLOSING object (unlike an anonymous class)

// --- method references ----------------------------------------------------
Integer::parseInt        // static          s -> Integer.parseInt(s)
System.out::println      // bound instance  s -> System.out.println(s)
String::toUpperCase      // unbound         s -> s.toUpperCase()
ArrayList::new           // constructor     () -> new ArrayList<>()

words.sort(Comparator.comparing(String::length));   // sort by an extracted key
words.forEach(System.out::println);                 // Iterable.forEach - no stream

// --- behaviour as a parameter ---------------------------------------------
static int countMatching(List<String> items, Predicate<String> test) { ... }
countMatching(words, w -> w.length() > 3);
countMatching(words, w -> w.startsWith("a"));
```
""",
    self_check=[
        "Can you rewrite a named Comparator class as a lambda, and say where its parameter types came from?",
        "Can you say when `return` is legal in a lambda body, and when it is a syntax error?",
        "Can you name all four `java.util.function` interfaces with their method names?",
        "Can you declare a functional interface and say what `@FunctionalInterface` actually checks?",
        "Can you explain why a captured local must be effectively final?",
        "Can you say why a lambda parameter cannot reuse an enclosing local's name, and what `this` means inside one?",
        "Can you write a method that returns a `Predicate` closing over its argument?",
        "Can you name the four kinds of method reference and give an example of each?",
    ],
    review=[
        _jq("```java\nwords.sort((a, b) -> Integer.compare(a.length(), b.length()));\n```\nWhat gave `a` its type?",
            ["The target type `Comparator<String>`", "The first element",
             "An explicit cast", "Erasure"],
            0,
            "A lambda means nothing without an interface to be an instance of."),
        _jq("`int total = 0; Consumer<Integer> c = x -> total += x;`",
            ["Compile error - total must be effectively final",
             "Works", "Works but total stays 0", "Needs a cast"],
            0,
            "Capture is by value, so the assignment is refused."),
        _jq("`String::toUpperCase` used as a `Function<String, String>`…",
            ["calls toUpperCase ON the argument - the unbound kind",
             "is a static reference", "needs an instance first", "does not compile"],
            0,
            "The lambda's parameter becomes the receiver."),
        _jq("An interface with one abstract method and three `default` methods is…",
            ["functional - default methods are not abstract",
             "not functional", "functional only with the annotation",
             "a compile error"],
            0,
            "Only abstract methods count against the budget."),
    ],
    milestone="You can pass behaviour as a value: a lambda where the shape is obvious, a "
              "method reference where it only forwards, your own functional interface "
              "where the name earns its keep - and you can explain capture, scope and "
              "`this` well enough to survive the interview questions about all three.",
))
