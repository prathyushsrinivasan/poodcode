# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 8 — StringBuilder and StringBuffer.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# The payoff module for Part 2. Modules 6 and 7 deliberately built every string
# with `+` in a loop, so the opening claim here — "everything you have written
# so far is quadratic, and here is the one-class fix" — lands on code the
# learner actually typed.
#
# StringBuilder is the FIRST mutable text type in the course, so the lessons
# lean on the contrast with String at every step: methods change the object and
# return `this` (so chaining works and dropping the result is fine), which is
# the exact opposite of module 6's rule.
# ---------------------------------------------------------------------------

_M8 = []

_RD_LINE = "        String s = sc.nextLine();\n"
_RD_LINE_INT = _RD_LINE + "        int k = sc.nextInt();\n"


# --- Python mirrors ---------------------------------------------------------

def _devowel(s):
    return "".join(c for c in s if c not in "aeiou")


def _rle_encode(s):
    out = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(s[i] + str(j - i))
        i = j
    return "".join(out)


def _rle_decode(e):
    out = []
    p = 0
    while p < len(e):
        c = e[p]
        p += 1
        count = 0
        while p < len(e) and e[p].isdigit():
            count = count * 10 + int(e[p])
            p += 1
        out.append(c * count)
    return "".join(out)


# --- 8.1 Why it exists ------------------------------------------------------

_M8.append(_jlesson(
    "m8-why", "Why `+` in a loop is quadratic",
    "The one performance fact every Java developer is expected to know.",
    """
Module 6 established that strings are immutable, so every `+` allocates a new
one and copies both operands into it. Inside a loop, that is a disaster:

```java
String out = "";
for (int i = 0; i < n; i++) out = out + "x";
```

Pass 1 copies 0 characters, pass 2 copies 1, pass 3 copies 2 … pass n copies
n−1. The total is `0 + 1 + 2 + … + (n-1)` = **n(n−1)/2** character copies —
the same triangular number as module 3's comparison count, and just as
quadratic. For n = 100,000 that is about **five billion** copies, and it also
allocates 100,000 throwaway strings for the garbage collector to clean up.

**`StringBuilder` is a mutable string.** It keeps a `char[]` with room to
spare, and `append` writes into the free space:

```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < n; i++) sb.append("x");
String out = sb.toString();               // ONE string, built once
```

That is **O(n)**: each character is written once, plus occasional array
doublings whose total cost is also O(n) (the same amortised argument as
`ArrayList`'s growth). Five billion copies become one hundred thousand.

**The three rules that differ from `String`:**

1. **It changes in place.** `sb.append("x")` modifies `sb` — you do not have to
   assign the result anywhere. The opposite of every String method.
2. **It also returns itself**, which is what makes chaining work:
   `sb.append(a).append(b).append(c)`.
3. **`toString()` is what produces the String** at the end. `sb` is not a
   String and cannot be passed where one is required — though
   `System.out.println(sb)` works, because `println` calls `toString` for you.

**The classic mistake** is creating the builder *inside* the loop, which
throws away everything on every pass:

```java
for (int i = 0; i < n; i++) {
    StringBuilder sb = new StringBuilder();   // WRONG: a fresh, empty one
    sb.append(i);
}
```

Declare it once, before the loop. Same instinct as module 2's per-row
accumulator, in reverse.

**When `+` is fine.** In a *single expression*, `"a" + b + "c"` is compiled to
one StringBuilder chain automatically, so it costs nothing. The compiler simply
cannot do that across loop iterations. So: `+` for readable one-liners,
`StringBuilder` for loops.
""",
    warmup=[
        _jq("Appending one character 1,000 times with `out = out + c` copies roughly how many characters?",
            ["500,000", "1,000", "2,000", "1,000,000"],
            0,
            "0 + 1 + … + 999 = 999 × 1000 / 2 ≈ 500,000. StringBuilder does it in 1,000."),
        _jq("What is wrong with declaring `StringBuilder sb = new StringBuilder();` inside the loop?",
            ["Each pass starts from an empty builder, so only the last append survives",
             "Nothing — it is equivalent",
             "It fails to compile",
             "It makes the loop O(n²) but still correct"],
            0,
            "You get a brand new, empty builder every pass. Declare it once, before the loop."),
    ],
    exercises=[
        _je("j8-why-build", "Build it properly",
            "Read a line and a number `k`, and print the line repeated `k` times. Use "
            "a `StringBuilder`. Replace `____` with the loop that appends.",
            _jscan(
                _RD_LINE_INT
                + "        StringBuilder sb = new StringBuilder();\n"
                  "        for (int i = 0; i < k; i++) sb.append(s);\n"
                  "        System.out.println(sb.toString());"),
            "        for (int i = 0; i < k; i++) sb.append(s);",
            [_lkcase(s, k, s * k)
             for (s, k) in (("ab", 3), ("x", 5), ("hi ", 2), ("q", 1))],
            hints=["The builder already exists — you only need the loop.",
                   "`append` changes `sb` in place; there is nothing to assign.",
                   "`for (int i = 0; i < k; i++) sb.append(s);`"],
            difficulty="Intro"),

        _jfix("j8-why-inside", "The builder that resets every pass",
              "This should print the digits `0` to `k-1` run together — for `k = 4`, "
              "`0123`. It prints only the last digit. One line is in the wrong place.",
              _jscan(
                  "        int k = sc.nextInt();\n"
                  "        for (int i = 0; i < k; i++) {\n"
                  "            StringBuilder sb = new StringBuilder();\n"
                  "            sb.append(i);\n"
                  "            if (i == k - 1) System.out.println(sb.toString());\n"
                  "        }"),
              _jscan(
                  "        int k = sc.nextInt();\n"
                  "        StringBuilder sb = new StringBuilder();\n"
                  "        for (int i = 0; i < k; i++) {\n"
                  "            sb.append(i);\n"
                  "        }\n"
                  "        System.out.println(sb.toString());"),
              [_case(k, "".join(str(i) for i in range(k))) for k in (4, 1, 10)],
              hints=["How many StringBuilder objects does this program create?",
                     "A new one each pass means everything appended before it is discarded.",
                     "Declare the builder once, before the loop, and print once after it."]),

        _jch("j8-why-count", "Count up in one string", "Easy",
             "Read `k` and print the numbers `1` to `k` on one line, separated by "
             "spaces, built with a `StringBuilder`. Write the whole block where you "
             "see `____`.",
             _jscan(
                 "        int k = sc.nextInt();\n"
                 "        StringBuilder sb = new StringBuilder();\n"
                 "        for (int i = 1; i <= k; i++) {\n"
                 '            if (i > 1) sb.append(" ");\n'
                 "            sb.append(i);\n"
                 "        }\n"
                 "        System.out.println(sb.toString());"),
             "        StringBuilder sb = new StringBuilder();\n"
             "        for (int i = 1; i <= k; i++) {\n"
             '            if (i > 1) sb.append(" ");\n'
             "            sb.append(i);\n"
             "        }\n"
             "        System.out.println(sb.toString());",
             [_case(k, " ".join(str(i) for i in range(1, k + 1))) for k in (5, 1, 3, 10)],
             hints=["Declare the builder before the loop.",
                    "`append` takes an `int` directly — no conversion needed.",
                    "Put the separator before every value except the first, so there is no "
                    "trailing space."]),
    ],
    quiz=[
        _jq("`String x = \"a\" + b + \"c\";` in one expression — is that slow?",
            ["No — the compiler turns the whole chain into one StringBuilder",
             "Yes, it allocates three strings",
             "Yes, it is O(n²)",
             "Only if b is long"],
            0,
            "Within a single expression the compiler does the optimisation for you. It cannot "
            "do it across loop iterations, which is the only case that matters."),
        _jq("Why is StringBuilder's growth still O(n) overall despite occasional array copies?",
            ["Capacity doubles, so the copies are geometric and sum to O(n) — amortised",
             "Because it never copies",
             "Because the JVM preallocates 1MB",
             "It isn't; it is O(n log n)"],
            0,
            "n + n/2 + n/4 + … < 2n. Exactly the same amortised argument that makes "
            "`ArrayList.add` O(1)."),
    ],
))

# --- 8.2 The basics ---------------------------------------------------------

_M8.append(_jlesson(
    "m8-basics", "`append`, `toString`, and mutation in place",
    "A mutable string: methods that change the object and hand it back.",
    """
```java
StringBuilder sb = new StringBuilder();          // empty
StringBuilder sb = new StringBuilder("hello");   // pre-filled with text
StringBuilder sb = new StringBuilder(100);       // empty, room for 100 chars
```

**Watch the last two.** `new StringBuilder("10")` holds the text `10`;
`new StringBuilder(10)` is **empty** with capacity 10. Passing an `int` when you
meant text is a real bug, and a silent one — you get an empty builder rather
than a compile error.

**`append` takes anything.** There is an overload for every primitive plus
`Object` and `char[]`, and each converts to text the same way `+` does:

```java
sb.append("text");   sb.append(42);     sb.append('c');
sb.append(3.5);      sb.append(true);   sb.append(someObject);
```

**Every mutator returns `this`,** which is why chaining reads naturally:

```java
sb.append(name).append(" is ").append(age).append(" years old");
```

Each call modifies `sb` and hands `sb` straight back. That return value is a
convenience, not the result — unlike `String`, **dropping it is completely
fine**, because the object already changed.

**Reading and editing in place:**

```java
sb.length()               // like String — a method
sb.charAt(i)              // like String
sb.setCharAt(i, 'x')      // NO String equivalent — this is the mutable part
sb.setLength(0)           // truncate to empty, reusing the buffer
sb.toString()             // finally, a String
```

`setCharAt` is the clearest demonstration of what makes a builder different: a
`String` has nothing like it, because a String's characters can never change.

**`sb.length` does not compile.** Same rule as `String`: a method, not a field.
Only arrays use the bare field.

**`toString()` at the end.** `sb` is a `StringBuilder`, not a `String`, so it
cannot be passed to something expecting a `String` and `sb.equals(otherText)`
does **not** compare characters — `StringBuilder` does not override `equals`,
so it falls back to reference identity and is essentially always false. Convert
first: `sb.toString().equals(other)`. That is a genuinely nasty trap and worth
remembering.

`System.out.println(sb)` works because `println` calls `toString()` for you.
""",
    warmup=[
        _jq("`new StringBuilder(10).length()` is…",
            ["0 — the int argument sets CAPACITY, not content",
             "2 — it holds the text \"10\"",
             "10",
             "It does not compile"],
            0,
            "The `int` constructor pre-sizes the buffer. `new StringBuilder(\"10\")` is the "
            "one that holds text."),
        _jq("`sb.append(\"abc\"); ` — do you need to assign the result?",
            ["No: it changes sb in place and returns sb only for chaining",
             "Yes, like every String method",
             "Only when chaining",
             "Yes, or it will not compile"],
            0,
            "This is exactly opposite to `String`. The return value exists so calls can be "
            "chained; ignoring it loses nothing."),
    ],
    exercises=[
        _je("j8-b-append", "Append the line",
            "Print the line with `>> ` in front and ` <<` after, built with a "
            "`StringBuilder`. Replace `____` with the chain of appends.",
            _jscan(
                _RD_LINE
                + "        StringBuilder sb = new StringBuilder();\n"
                  '        sb.append(">> ").append(s).append(" <<");\n'
                  "        System.out.println(sb.toString());"),
            'sb.append(">> ").append(s).append(" <<");',
            [_scase(s, f">> {s} <<") for s in ("hello", "a b c", "x")],
            hints=["Three appends, in order.",
                   "Each one returns the builder, so they chain with dots.",
                   '`sb.append(">> ").append(s).append(" <<");`'],
            difficulty="Intro"),

        _je("j8-b-mixed", "Append anything",
            "Read a line and a number `k`, and print `<line> has <k> items` using a "
            "builder. `append` has an overload for `int`, so no conversion is needed. "
            "Replace `____`.",
            _jscan(
                _RD_LINE_INT
                + "        StringBuilder sb = new StringBuilder();\n"
                  '        sb.append(s).append(" has ").append(k).append(" items");\n'
                  "        System.out.println(sb.toString());"),
            'sb.append(s).append(" has ").append(k).append(" items");',
            [_lkcase(s, k, f"{s} has {k} items")
             for (s, k) in (("cart", 3), ("the box", 0), ("x", 42))],
            hints=["Four appends chained together.",
                   "`append(k)` takes the int directly and converts it like `+` would.",
                   '`sb.append(s).append(" has ").append(k).append(" items");`'],
            difficulty="Intro"),

        _je("j8-b-setchar", "Change one character",
            "Read a line and an index `k`, and print the line with the character at "
            "`k` replaced by `*`. This is the thing a `String` cannot do — replace "
            "`____` with the call.",
            _jscan(
                _RD_LINE_INT
                + "        StringBuilder sb = new StringBuilder(s);\n"
                  "        sb.setCharAt(k, '*');\n"
                  "        System.out.println(sb.toString());"),
            "sb.setCharAt(k, '*');",
            [_lkcase(s, k, s[:k] + "*" + s[k + 1:])
             for (s, k) in (("hello", 0), ("hello", 4), ("abcdef", 2))],
            hints=["The method name pairs with `charAt`.",
                   "It takes the position and the new character.",
                   "`sb.setCharAt(k, '*');` — single quotes, it is a char."]),

        _jfix("j8-b-length", "length without the parentheses",
              "This should print how many characters the builder holds after two "
              "appends. It does not compile.",
              _jscan(
                  _RD_LINE
                  + "        StringBuilder sb = new StringBuilder();\n"
                    "        sb.append(s).append(s);\n"
                    "        System.out.println(sb.length);"),
              _jscan(
                  _RD_LINE
                  + "        StringBuilder sb = new StringBuilder();\n"
                    "        sb.append(s).append(s);\n"
                    "        System.out.println(sb.length());"),
              [_scase(s, len(s) * 2) for s in ("hello", "ab", "x y")],
              hints=["Is `length` a field or a method here?",
                     "StringBuilder follows String, not arrays.",
                     "`sb.length()`"],
              difficulty="Intro"),

        _jch("j8-b-numbers", "A table of squares", "Easy",
             "Read `k` and print one line holding `1:1 2:4 3:9 …` up to `k`, "
             "space separated, built with a single `StringBuilder`. For `k = 3` print "
             "`1:1 2:4 3:9`. Write the whole block where you see `____`.",
             _jscan(
                 "        int k = sc.nextInt();\n"
                 "        StringBuilder sb = new StringBuilder();\n"
                 "        for (int i = 1; i <= k; i++) {\n"
                 '            if (i > 1) sb.append(" ");\n'
                 '            sb.append(i).append(":").append(i * i);\n'
                 "        }\n"
                 "        System.out.println(sb.toString());"),
             "        StringBuilder sb = new StringBuilder();\n"
             "        for (int i = 1; i <= k; i++) {\n"
             '            if (i > 1) sb.append(" ");\n'
             '            sb.append(i).append(":").append(i * i);\n'
             "        }\n"
             "        System.out.println(sb.toString());",
             [_case(k, " ".join(f"{i}:{i * i}" for i in range(1, k + 1)))
              for k in (3, 1, 6)],
             hints=["One builder, declared before the loop.",
                    "Three appends per entry, chained: the number, the colon, the square.",
                    "The separator goes before every entry except the first."]),
    ],
    quiz=[
        _jq("`sb.equals(\"hello\")` where sb holds \"hello\" gives…",
            ["false — StringBuilder does not override equals, so it compares references",
             "true", "It does not compile", "It throws"],
            0,
            "A genuinely nasty trap. Convert first: `sb.toString().equals(\"hello\")`."),
        _jq("Which of these has NO String equivalent?",
            ["setCharAt", "charAt", "length()", "toString()"],
            0,
            "Writing one character in place is only possible on a mutable type. It is the "
            "clearest illustration of what a builder is for."),
    ],
))

# --- 8.3 Editing ------------------------------------------------------------

_M8.append(_jlesson(
    "m8-edit", "`insert`, `delete`, `replace`, `reverse`",
    "The mutators — and the index shift that bites when you delete forwards.",
    """
```java
sb.insert(i, x)          // shift right and put x at index i
sb.delete(from, to)      // remove [from, to)  — half-open, as ever
sb.deleteCharAt(i)       // remove exactly one
sb.replace(from, to, x)  // delete that range, insert x in its place
sb.reverse()             // in place, no copy
sb.indexOf(t)            // like String's, and -1 when absent
```

All of them mutate `sb` and return it. All the ranges are half-open, so
`sb.delete(1, 4)` removes three characters — the same rule as `substring` and
`Arrays.copyOfRange`.

**`reverse()` is why this class turns up in interview answers.** Reversing a
string is one call and O(n) with no extra allocation beyond the builder:

```java
String backwards = new StringBuilder(s).reverse().toString();
```

Compare with module 7's loop, which was O(n²). (An interviewer asking you to
reverse a string usually wants the manual version — but knowing this one-liner
exists, and saying so, is the right move.)

**`insert` at `length()` is legal** and equivalent to `append`. `insert` at
anything beyond that throws.

**The index-shift trap.** Deleting while walking forwards skips elements,
because every deletion pulls the rest of the string left:

```java
for (int i = 0; i < sb.length(); i++)          // WRONG
    if (isVowel(sb.charAt(i))) sb.deleteCharAt(i);
```

Delete index 2, and what was at index 3 slides into index 2 — but the loop has
already moved on to 3. Two adjacent vowels, and the second one survives.

Two fixes, and both are worth knowing:

```java
for (int i = sb.length() - 1; i >= 0; i--)     // walk BACKWARDS
    if (isVowel(sb.charAt(i))) sb.deleteCharAt(i);
```

Walking backwards works because deleting at `i` only shifts things at indices
*above* `i`, which you have already passed. It is the same reason you iterate a
list backwards when removing from it.

The other fix — usually the better one — is to **build a new builder with only
the characters you want**, rather than deleting from the old one. That is O(n)
instead of O(n²), since each `deleteCharAt` shifts the whole tail.

**A caution on `insert` and `delete` in loops:** each one is O(n) because of
the shifting. `append` is the only O(1) operation here. Building by appending
beats editing in place, essentially always.
""",
    warmup=[
        _jq("`sb` holds \"hello\". After `sb.delete(1, 3)` it holds…",
            ["\"hlo\"", "\"hllo\"", "\"ho\"", "\"hel\""],
            0,
            "Half-open: indices 1 and 2 ('e' and 'l') are removed, index 3 is kept. The "
            "count removed is always `to - from`."),
        _jq("Deleting vowels from \"aa\" with a FORWARD loop and `deleteCharAt` leaves…",
            ["\"a\" — the second vowel slid into the index the loop just left",
             "\"\" — both are removed",
             "\"aa\"",
             "An IndexOutOfBoundsException"],
            0,
            "Deleting index 0 shifts the second 'a' down to index 0, but the loop has already "
            "advanced to 1. Walk backwards, or build a new builder."),
    ],
    exercises=[
        _je("j8-e-reverse", "Reverse in one call",
            "Print the line reversed, using the builder's own method rather than a "
            "loop. Replace `____`.",
            _jscan(
                _RD_LINE
                + "        StringBuilder sb = new StringBuilder(s);\n"
                  "        sb.reverse();\n"
                  "        System.out.println(sb.toString());"),
            "sb.reverse();",
            [_scase(s, s[::-1]) for s in ("hello", "abc", "x", "a b c")],
            hints=["It does exactly what it is named.",
                   "It reverses the builder in place, so nothing needs assigning.",
                   "`sb.reverse();`"],
            difficulty="Intro"),

        _je("j8-e-insert", "Put something in the middle",
            "Read a line and an index `k`, and print the line with `--` inserted at "
            "position `k`. Replace `____`.",
            _jscan(
                _RD_LINE_INT
                + "        StringBuilder sb = new StringBuilder(s);\n"
                  '        sb.insert(k, "--");\n'
                  "        System.out.println(sb.toString());"),
            'sb.insert(k, "--");',
            [_lkcase(s, k, s[:k] + "--" + s[k:])
             for (s, k) in (("hello", 2), ("hello", 0), ("hello", 5))],
            hints=["Two arguments: where, then what.",
                   "Everything from `k` onward shifts right.",
                   '`sb.insert(k, "--");` — inserting at `length()` is legal and acts like '
                   "append."]),

        _je("j8-e-deletechar", "Drop one character",
            "Read a line and an index `k`, and print the line with the character at "
            "`k` removed. Replace `____`.",
            _jscan(
                _RD_LINE_INT
                + "        StringBuilder sb = new StringBuilder(s);\n"
                  "        sb.deleteCharAt(k);\n"
                  "        System.out.println(sb.toString());"),
            "sb.deleteCharAt(k);",
            [_lkcase(s, k, s[:k] + s[k + 1:])
             for (s, k) in (("hello", 0), ("hello", 4), ("abcdef", 3))],
            hints=["There is a single-character version of `delete`.",
                   "It takes just the index.",
                   "`sb.deleteCharAt(k);`"],
            difficulty="Intro"),

        _jfix("j8-e-range", "It removes one too few",
              "This should remove the characters from index `from` up to but not "
              "including `to`. It always leaves one extra character behind, because "
              "the second argument is being treated as inclusive.",
              _jscan(
                  _RD_LINE
                  + "        int from = sc.nextInt();\n"
                    "        int to = sc.nextInt();\n"
                    "        StringBuilder sb = new StringBuilder(s);\n"
                    "        sb.delete(from, to - 1);\n"
                    "        System.out.println(sb.toString());"),
              _jscan(
                  _RD_LINE
                  + "        int from = sc.nextInt();\n"
                    "        int to = sc.nextInt();\n"
                    "        StringBuilder sb = new StringBuilder(s);\n"
                    "        sb.delete(from, to);\n"
                    "        System.out.println(sb.toString());"),
              [_case(f"{s}\n{f_}\n{t}", s[:f_] + s[t:])
               for (s, f_, t) in (("hello", 1, 3), ("abcdef", 0, 4), ("abcdef", 2, 6))],
              hints=["Every range in Java is half-open — `to` is already excluded.",
                     "So subtracting one from it removes one character too few.",
                     "`sb.delete(from, to);`"],
              difficulty="Intro"),

        _jch("j8-e-devowel", "Remove every vowel", "Hard",
             "Print the line with every lowercase vowel (`a e i o u`) removed. Use a "
             "`StringBuilder` and `deleteCharAt` — and walk the builder **backwards**, "
             "or adjacent vowels will survive. Write the whole block where you see "
             "`____`.",
             _jscan(
                 _RD_LINE
                 + "        StringBuilder sb = new StringBuilder(s);\n"
                   "        for (int i = sb.length() - 1; i >= 0; i--) {\n"
                   "            char c = sb.charAt(i);\n"
                   "            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') sb.deleteCharAt(i);\n"
                   "        }\n"
                   "        System.out.println(sb.toString());"),
             "        for (int i = sb.length() - 1; i >= 0; i--) {\n"
             "            char c = sb.charAt(i);\n"
             "            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') sb.deleteCharAt(i);\n"
             "        }\n"
             "        System.out.println(sb.toString());",
             [_scase(s, _devowel(s))
              for s in ("banana", "aa", "queueing", "rhythm", "hello world")],
             hints=["Start at `sb.length() - 1` and count down to 0.",
                    "Deleting at `i` only shifts characters ABOVE `i`, which you have already "
                    "visited — that is why backwards works.",
                    "`aa` and `queueing` are the cases a forward loop fails on.",
                    "A line with no vowels at all must come back unchanged."]),
    ],
    quiz=[
        _jq("Why does removing matching characters by `deleteCharAt` in a forward loop fail?",
            ["Each deletion shifts the tail left into an index the loop has already passed",
             "deleteCharAt throws inside a loop",
             "The length is cached before the loop starts",
             "It doesn't fail"],
            0,
            "The successor slides into the current index while the loop moves on. Walking "
            "backwards, or building a fresh builder, both avoid it."),
        _jq("Which StringBuilder operation is O(1), and which are O(n)?",
            ["append is O(1) amortised; insert, delete and deleteCharAt shift the tail",
             "All of them are O(1)",
             "Only reverse is O(n)",
             "append is O(n); the rest are O(1)"],
            0,
            "Appending writes into free space at the end. Anything that changes the middle "
            "has to move everything after it — so build by appending rather than editing."),
    ],
))

# --- 8.4 Capacity -----------------------------------------------------------

_M8.append(_jlesson(
    "m8-capacity", "Capacity, length, and pre-sizing",
    "What the buffer is doing underneath, and the one time you should care.",
    """
A `StringBuilder` wraps a `char[]` that is deliberately **bigger than the text
it holds**. Two different numbers describe it:

- **`length()`** — how many characters are actually in there. This is the one
  you use.
- **`capacity()`** — how many the current array could hold before it has to
  grow. An implementation detail.

The default capacity is 16. When an append would overflow it, the builder
allocates a new array of roughly **twice the old size plus two** and copies
everything across. Because the capacity doubles, the copies are geometric:
`n + n/2 + n/4 + …` is under `2n`, so **all the growth together is O(n)**. That
is the amortised argument, and it is exactly how `ArrayList` grows too.

**Pre-sizing** skips the intermediate copies when you already know the answer's
size:

```java
StringBuilder sb = new StringBuilder(n * 8);    // no growth at all
```

This matters when `n` is large and you are in a hot path. It is a micro-
optimisation everywhere else, and reaching for it in ordinary code is noise —
but knowing *why* it helps is what an interviewer is checking.

**`setLength` does two useful things.** `sb.setLength(0)` empties the builder
while **keeping the buffer**, which is the cheap way to reuse one builder across
many iterations of an outer loop. `sb.setLength(n)` truncates to `n` characters
(or pads with `'\\0'` if `n` is longer, which you almost never want).

**Do not test against `capacity()`.** It is unspecified beyond "at least
`length()`", so a program whose output depends on it is a program whose output
depends on your JDK version. Assert on `length()`.

**Trimming** — `sb.trimToSize()` shrinks the buffer down to the text. Relevant
only if you are holding a builder for a long time, which you generally should
not be: build, call `toString()`, let the builder go.
""",
    warmup=[
        _jq("A new `StringBuilder()` has length and capacity of…",
            ["length 0, capacity 16", "length 16, capacity 16",
             "length 0, capacity 0", "both unspecified"],
            0,
            "16 is the documented default. Length counts real characters and starts at 0."),
        _jq("Why does doubling the buffer keep total growth cost at O(n)?",
            ["The copies form a geometric series that sums to under 2n",
             "Because copying is free",
             "Because it only ever grows once",
             "It doesn't — growth is O(n²)"],
            0,
            "n + n/2 + n/4 + … < 2n. Growing by a fixed amount instead of doubling *would* be "
            "O(n²) — which is the actual reason doubling is used."),
    ],
    exercises=[
        _je("j8-c-length", "How much is in there?",
            "Read a line and a number `k`. Append the line `k` times to a builder and "
            "print how many characters it holds. Replace `____` with the length call.",
            _jscan(
                _RD_LINE_INT
                + "        StringBuilder sb = new StringBuilder();\n"
                  "        for (int i = 0; i < k; i++) sb.append(s);\n"
                  "        System.out.println(sb.length());"),
            "sb.length()",
            [_lkcase(s, k, len(s) * k)
             for (s, k) in (("abc", 4), ("x", 100), ("hello ", 3), ("q", 0))],
            hints=["Length is the count of real characters, not the buffer size.",
                   "It is a method, like String's.",
                   "`sb.length()`"],
            difficulty="Intro"),

        _je("j8-c-presize", "Ask for the room up front",
            "Same job, but pre-size the builder so it never has to grow: it will hold "
            "`s.length() * k` characters. Replace `____` with the construction.",
            _jscan(
                _RD_LINE_INT
                + "        StringBuilder sb = new StringBuilder(s.length() * k);\n"
                  "        for (int i = 0; i < k; i++) sb.append(s);\n"
                  "        System.out.println(sb.length());"),
            "new StringBuilder(s.length() * k)",
            [_lkcase(s, k, len(s) * k)
             for (s, k) in (("abc", 4), ("x", 100), ("hello", 2))],
            hints=["The `int` constructor sets the capacity.",
                   "The final size is the line's length times the repeat count.",
                   "`new StringBuilder(s.length() * k)` — and note this gives an EMPTY "
                   "builder, not one containing a number."]),

        _jch("j8-c-reuse", "Reuse one builder", "Medium",
             "Read `k`, then `k` lines. For each line, print it followed by its "
             "length in brackets — `hello[5]`. Use **one** `StringBuilder` for all "
             "`k` lines, emptying it between them with `setLength(0)`. Write the "
             "whole block where you see `____`.",
             _jscan(
                 "        int k = Integer.parseInt(sc.nextLine());\n"
                 "        StringBuilder sb = new StringBuilder();\n"
                 "        for (int i = 0; i < k; i++) {\n"
                 "            String line = sc.nextLine();\n"
                 "            sb.setLength(0);\n"
                 '            sb.append(line).append("[").append(line.length()).append("]");\n'
                 "            System.out.println(sb.toString());\n"
                 "        }"),
             "        StringBuilder sb = new StringBuilder();\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            String line = sc.nextLine();\n"
             "            sb.setLength(0);\n"
             '            sb.append(line).append("[").append(line.length()).append("]");\n'
             "            System.out.println(sb.toString());\n"
             "        }",
             [_case(f"{len(ls)}\n" + "\n".join(ls),
                    _nl(*[f"{x}[{len(x)}]" for x in ls]))
              for ls in (["hello", "hi", "abc"], ["solo"], ["a", "bb", "ccc", "dddd"])],
             hints=["The builder is declared ONCE, outside the loop — that is the point of "
                    "the exercise.",
                    "`sb.setLength(0)` empties it while keeping the buffer, so the next line "
                    "starts clean.",
                    "Forget the `setLength(0)` and every line comes out with all the previous "
                    "ones stuck to the front."]),
    ],
    quiz=[
        _jq("Is it worth writing `new StringBuilder(expectedSize)` in ordinary code?",
            ["Rarely — it matters in hot paths with large n, and is noise elsewhere",
             "Always — never use the no-arg constructor",
             "Never — the JVM ignores it",
             "Only when the size is under 16"],
            0,
            "Growth is already amortised O(n). Pre-sizing removes a constant factor, which is "
            "worth it when the constant is being paid millions of times."),
        _jq("Why should a test never assert on `capacity()`?",
            ["It is unspecified beyond being at least length(), so it can vary by JDK",
             "It always throws",
             "It is private",
             "It is always exactly 16"],
            0,
            "The growth policy is an implementation detail. `length()` is the contract."),
    ],
))

# --- 8.5 StringBuffer -------------------------------------------------------

_M8.append(_jlesson(
    "m8-buffer", "`StringBuffer` and choosing between the three",
    "The same class with locks on, and the decision table you can recite.",
    """
`StringBuffer` has **the same API** as `StringBuilder` — `append`, `insert`,
`delete`, `reverse`, `toString`, all of it. The only difference is that every
method is `synchronized`, so it is safe for several threads to use one instance
at the same time.

```java
StringBuffer sb = new StringBuffer();
sb.append("same").append(" methods").reverse();
```

**The history explains the oddity.** `StringBuffer` came first, in Java 1.0,
and was synchronized by default. It turned out that essentially every builder
is a local variable used by one thread, so the locking was pure overhead. Java
5 added `StringBuilder` — the identical class with the locks removed — and it
has been the right default ever since.

**Which to use:**

| Situation | Use |
|---|---|
| A one-off concatenation in an expression | `+` |
| Building text in a loop, or any local building | **`StringBuilder`** |
| One builder genuinely shared across threads | `StringBuffer` |
| Text that will not change | `String` |

In practice: **`StringBuilder`, always**, unless you can point at the two
threads. And even then, sharing a mutable buffer between threads is usually a
design worth revisiting — each thread building its own and joining the results
at the end is simpler and faster.

**The interview answer,** compressed: "`String` is immutable, so concatenating
in a loop is O(n²). `StringBuilder` is a mutable buffer, so it is O(n) —
that is what I would use. `StringBuffer` is the same class with synchronized
methods, kept for backwards compatibility from before `StringBuilder` existed;
I would only reach for it if one builder were genuinely shared between threads."

**A caveat worth knowing.** `StringBuffer`'s per-method locking makes each
*call* atomic, not each *sequence* of calls. Two threads interleaving
`append(a); append(b);` can still produce `a b a b` in an unhelpful order. It
protects the buffer's internal state, not your intent — which is another reason
the answer is usually "do not share it".
""",
    warmup=[
        _jq("What is the difference between StringBuilder and StringBuffer?",
            ["StringBuffer's methods are synchronized; the APIs are otherwise identical",
             "StringBuffer is immutable",
             "StringBuilder cannot be reversed",
             "StringBuffer is faster"],
            0,
            "Same methods, same behaviour, plus locking. The locking is why StringBuilder is "
            "the faster default."),
        _jq("Why does StringBuffer exist at all if StringBuilder is better?",
            ["It predates StringBuilder — Java 1.0 versus Java 5 — and is kept for compatibility",
             "It is required for multi-line strings",
             "It handles Unicode better",
             "It is the only one with reverse()"],
            0,
            "Synchronizing by default turned out to be the wrong guess. `StringBuilder` is "
            "the correction, and the old class stayed for existing code."),
    ],
    exercises=[
        _je("j8-sbf-reverse", "The same API, with locks",
            "Print the line reversed, this time using a `StringBuffer` — the methods "
            "are identical. Replace `____` with the construction.",
            _jscan(
                _RD_LINE
                + "        StringBuffer sb = new StringBuffer(s);\n"
                  "        sb.reverse();\n"
                  "        System.out.println(sb.toString());"),
            "new StringBuffer(s)",
            [_scase(s, s[::-1]) for s in ("hello", "abc", "x")],
            hints=["Exactly like the StringBuilder version, with the other class name.",
                   "The String constructor pre-fills it with the text.",
                   "`new StringBuffer(s)`"],
            difficulty="Intro"),

        _jch("j8-sbf-palindrome", "Palindrome by reversing", "Medium",
             "Print `true` when the line reads the same in both directions. Do it by "
             "building the reversed text with a builder and comparing — which needs "
             "`toString()` before the comparison, because `StringBuilder` does not "
             "override `equals`. Write the whole block where you see `____`.",
             _jscan(
                 _RD_LINE
                 + "        StringBuilder sb = new StringBuilder(s);\n"
                   "        sb.reverse();\n"
                   "        System.out.println(s.equals(sb.toString()));"),
             "        StringBuilder sb = new StringBuilder(s);\n"
             "        sb.reverse();\n"
             "        System.out.println(s.equals(sb.toString()));",
             [_scase(s, _jbool(s == s[::-1]))
              for s in ("racecar", "hello", "abba", "x", "ab")],
             hints=["Three lines: build from `s`, reverse, compare.",
                    "`s.equals(sb)` would be false always — a String never equals a "
                    "StringBuilder. Call `toString()` first.",
                    "Module 7's two-pointer version is still the better answer for an "
                    "interview: this one allocates a whole second string."]),
    ],
    quiz=[
        _jq("A method builds a string in a local variable and returns it. Which type?",
            ["StringBuilder — it is local, so no synchronization is needed",
             "StringBuffer — returning it makes it shared",
             "String with += — it is clearer",
             "char[]"],
            0,
            "A local builder is visible to one thread by construction. The returned `String` "
            "is immutable and therefore safe to share anyway."),
        _jq("Does StringBuffer make `sb.append(a); sb.append(b);` atomic as a pair?",
            ["No — each call is atomic, but another thread can interleave between them",
             "Yes, consecutive calls are grouped",
             "Yes, if they are chained with dots",
             "Only for String arguments"],
            0,
            "Per-method locking protects the buffer's internals, not your sequence. Guarding "
            "the intent needs your own synchronized block."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m8_rle(s):
    enc = _rle_encode(s)
    dec = _rle_decode(enc)
    return _nl(
        f"encoded={enc}",
        f"decoded={dec}",
        f"ok={_jbool(dec == s)}",
    )


_M8_CAP = _jcap(
    "Run-length codec",
    """
Encode a string, decode it back, and prove the round trip — all with
`StringBuilder`, because both halves build text in a loop.

Read one line of lowercase letters. Print:

```
encoded=<the run-length encoding>
decoded=<the encoding decoded back>
ok=<true when decoded equals the original>
```

**Run-length encoding** replaces each run of identical characters with the
character followed by the run's length: `aaabbc` becomes `a3b2c1`. Every run
gets a count, including runs of one — that keeps the format unambiguous.

**Encoding.** Walk the line with two indices: `i` at the start of a run, `j`
scanning forward while the character is the same. Append the character and
`j - i`, then jump `i` to `j`.

**Decoding is the harder half, and the point of the exercise.** A count can be
more than one digit — twelve `a`s encode as `a12` — so after reading the letter
you must keep consuming digits while they are digits, accumulating with
`count = count * 10 + (c - '0')`. Reading a single digit would decode `a12` as
one `a` followed by a stray `2`.

Then append the character `count` times and continue. `Character.isDigit` from
module 7 is how you know when the number ends.

Both halves want a `StringBuilder`: the output is built one piece at a time, in
a loop, which is exactly the case module 8 exists for.
""",
    _jch("j8-cap-rle", "Run-length codec", "Hard",
         "Write the whole codec where you see `____` — encode, decode the encoding, "
         "then report whether the round trip matched.",
         _jscan(
             _RD_LINE
             + "        StringBuilder enc = new StringBuilder();\n"
               "        int i = 0;\n"
               "        while (i < s.length()) {\n"
               "            char c = s.charAt(i);\n"
               "            int j = i;\n"
               "            while (j < s.length() && s.charAt(j) == c) j++;\n"
               "            enc.append(c).append(j - i);\n"
               "            i = j;\n"
               "        }\n"
               "        String e = enc.toString();\n"
               '        System.out.println("encoded=" + e);\n'
               "        StringBuilder dec = new StringBuilder();\n"
               "        int p = 0;\n"
               "        while (p < e.length()) {\n"
               "            char c = e.charAt(p);\n"
               "            p++;\n"
               "            int count = 0;\n"
               "            while (p < e.length() && Character.isDigit(e.charAt(p))) {\n"
               "                count = count * 10 + (e.charAt(p) - '0');\n"
               "                p++;\n"
               "            }\n"
               "            for (int t = 0; t < count; t++) dec.append(c);\n"
               "        }\n"
               '        System.out.println("decoded=" + dec.toString());\n'
               '        System.out.println("ok=" + s.equals(dec.toString()));'),
         "        StringBuilder enc = new StringBuilder();\n"
         "        int i = 0;\n"
         "        while (i < s.length()) {\n"
         "            char c = s.charAt(i);\n"
         "            int j = i;\n"
         "            while (j < s.length() && s.charAt(j) == c) j++;\n"
         "            enc.append(c).append(j - i);\n"
         "            i = j;\n"
         "        }\n"
         "        String e = enc.toString();\n"
         '        System.out.println("encoded=" + e);\n'
         "        StringBuilder dec = new StringBuilder();\n"
         "        int p = 0;\n"
         "        while (p < e.length()) {\n"
         "            char c = e.charAt(p);\n"
         "            p++;\n"
         "            int count = 0;\n"
         "            while (p < e.length() && Character.isDigit(e.charAt(p))) {\n"
         "                count = count * 10 + (e.charAt(p) - '0');\n"
         "                p++;\n"
         "            }\n"
         "            for (int t = 0; t < count; t++) dec.append(c);\n"
         "        }\n"
         '        System.out.println("decoded=" + dec.toString());\n'
         '        System.out.println("ok=" + s.equals(dec.toString()));',
         [_scase(s, _m8_rle(s))
          for s in ("aaabbc", "abc", "a", "aaaaaaaaaaaab", "zzzzzzzzzz",
                    "aabbaabb")],
         hints=["Encode with two indices: `i` marks the start of a run and `j` scans while "
                "the character stays the same.",
                "`enc.append(c).append(j - i)` — the `int` overload writes the count as text.",
                "For decoding, read the letter, advance past it, then loop while "
                "`Character.isDigit(...)` accumulating `count = count * 10 + (c - '0')`.",
                "Reading only one digit breaks on any run of ten or more — `a12` is in the "
                "hidden tests.",
                "Compare with `s.equals(dec.toString())`; `s.equals(dec)` is always false, "
                "because a String never equals a StringBuilder."]),
    example_io="stdin:  aaabbc\n\n"
               "stdout: encoded=a3b2c1\n        decoded=aaabbc\n        ok=true",
    rubric=[
        "Every run gets a count, including runs of length one.",
        "The decoder consumes multi-digit counts, so a run of 12 round-trips correctly.",
        "Both halves build their output with a StringBuilder declared outside the loop.",
        "`ok` compares `s` against `dec.toString()`, never against the builder itself.",
        "It survives a one-character line and a line with no repeats at all.",
        "All three lines print, in order, with no spaces around `=`.",
    ],
)


_MODULES.append(_jmod(
    8, 2, "Strings",
    "StringBuilder and StringBuffer",
    "Fix the O(n²) that modules 6 and 7 left you with: a mutable text buffer, its "
    "editing methods, how it grows, and the one-sentence answer to "
    "\"String vs StringBuilder vs StringBuffer\".",
    """
Everything you have built with `+` in a loop so far has been quadratic. This
module is the fix, and it is one class.

The mental shift is that `StringBuilder` is **mutable** — its methods change
the object and return it for chaining, which is the exact opposite of every
String method you have met. That single difference explains `setCharAt`,
explains why you never assign the result of `append`, and explains the
index-shift trap when you delete while iterating forwards.

It also closes Part 2 with the question every Java interview asks in some form:
String versus StringBuilder versus StringBuffer. By the end you should be able
to answer it in three sentences, with the reason for each.
""",
    _M8,
    capstone=_M8_CAP,
    objectives=[
        "Explain why `out = out + x` in a loop is O(n²), with the triangular-number argument.",
        "Build text with `append` and finish with `toString()`, declaring the builder outside the loop.",
        "Use `setCharAt`, `insert`, `delete`, `deleteCharAt` and `reverse`, remembering ranges are half-open.",
        "Avoid the index shift when removing characters, by walking backwards or by rebuilding.",
        "Describe capacity, doubling, and why total growth is still O(n) — and pre-size when it matters.",
        "Choose between `String`, `StringBuilder` and `StringBuffer` and justify it in one sentence.",
    ],
    why="\"String vs StringBuilder vs StringBuffer\" is asked in almost every Java "
        "interview, and string-building in a loop is one of the few beginner mistakes "
        "that actually shows up as a production performance bug.",
    est_minutes=270,
    glossary=[
        _jg("mutable", "Can be changed in place after construction. `StringBuilder` is; "
                       "`String` is not."),
        _jg("append", "Add to the end. The only O(1) StringBuilder operation, because it "
                      "writes into spare capacity."),
        _jg("method chaining", "`sb.append(a).append(b)` — possible because each mutator "
                               "returns `this`."),
        _jg("capacity", "How many characters the internal `char[]` can hold before it must "
                        "grow. An implementation detail — never assert on it."),
        _jg("length()", "How many characters are actually present. The number you use, and "
                        "the one that is contractually specified."),
        _jg("amortised O(1)", "Cheap on average across many operations even when one is "
                              "expensive. Doubling makes `append` amortised O(1)."),
        _jg("setLength(0)", "Empties the builder while keeping its buffer — how you reuse one "
                            "builder across iterations."),
        _jg("index shift", "Deleting at index `i` moves everything above it down by one, "
                           "which a forward loop then skips over."),
        _jg("synchronized", "Method-level locking. What `StringBuffer` adds over "
                            "`StringBuilder`, and why it is slower."),
    ],
    cheatsheet="""
```java
// --- why ----------------------------------------------------------------
String out = "";
for (...) out = out + x;             // O(n^2): each pass copies everything

StringBuilder sb = new StringBuilder();      // declare ONCE, outside the loop
for (...) sb.append(x);                       // O(n)
String out = sb.toString();

// --- construct ----------------------------------------------------------
new StringBuilder()                  // empty, capacity 16
new StringBuilder("hi")              // pre-filled with text
new StringBuilder(1000)              // EMPTY, capacity 1000  <- not "1000"

// --- read / write in place ---------------------------------------------
sb.length()                          // method, like String
sb.charAt(i)
sb.setCharAt(i, 'x')                 // no String equivalent — this is the point
sb.setLength(0)                      // empty it, keep the buffer
sb.toString()                        // finally a String

// --- mutate (all return `this`, all ranges half-open) ------------------
sb.append(anything)                  // String, int, char, double, boolean, ...
sb.insert(i, x)                      // insert at length() == append
sb.delete(from, to)                  // removes to - from characters
sb.deleteCharAt(i)
sb.replace(from, to, x)
sb.reverse()
sb.indexOf(t)                        // -1 when absent

// --- removing while iterating ------------------------------------------
for (int i = sb.length() - 1; i >= 0; i--)   // BACKWARDS, or you skip elements
    if (drop(sb.charAt(i))) sb.deleteCharAt(i);

// --- traps --------------------------------------------------------------
sb.equals("hello")                   // ALWAYS false — no equals override
sb.toString().equals("hello")        // correct
sb.length                            // does not compile

// --- choosing -----------------------------------------------------------
// String      : text that will not change
// +           : a one-off concatenation in a single expression
// StringBuilder: building in a loop  <- the default
// StringBuffer : the same, synchronized; only for a genuinely shared buffer
```
""",
    self_check=[
        "Can you state, with the arithmetic, why concatenating in a loop is quadratic?",
        "Do you declare the builder before the loop without having to think about it?",
        "Can you list the mutators and say which ranges are half-open?",
        "Can you explain why deleting forwards skips characters, and give two fixes?",
        "Can you say what capacity is, how it grows, and why the total is still O(n)?",
        "Would you spot `sb.equals(someString)` in a code review?",
        "Can you answer \"String vs StringBuilder vs StringBuffer\" in three sentences?",
    ],
    review=[
        _jq("`StringBuilder sb = new StringBuilder(5); System.out.println(sb.length());`",
            ["0", "5", "1", "16"],
            0,
            "The `int` constructor sets capacity, not content. The builder is empty."),
        _jq("`sb` holds \"abcdef\". After `sb.delete(2, 4)` it holds…",
            ["\"abef\"", "\"abcf\"", "\"abf\"", "\"abcef\""],
            0,
            "Half-open: indices 2 and 3 ('c' and 'd') go, index 4 stays. `to - from` = 2 "
            "characters removed."),
        _jq("Which is the correct way to test a builder's contents against a String?",
            ["sb.toString().equals(text)", "sb.equals(text)", "sb == text",
             "text.equals(sb)"],
            0,
            "`StringBuilder` inherits `Object.equals`, so every comparison against a String "
            "is false. Convert first."),
        _jq("You are writing a method that assembles a 10 MB report line by line. Which type?",
            ["StringBuilder, pre-sized if you can estimate the length",
             "String with +=, for readability",
             "StringBuffer, because the report is large",
             "char[] managed by hand"],
            0,
            "It is a local buffer built in a loop — the textbook StringBuilder case. Pre-sizing "
            "avoids about twenty array doublings on the way."),
    ],
    milestone="Part 2 is done. You understand Java's text types from the model up: why "
              "String is immutable, what that costs, and the mutable buffer that fixes it "
              "— and you can answer the interview question about all three.",
))
