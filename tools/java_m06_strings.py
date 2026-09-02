# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 6 — Strings: the object behind the text.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# Part 2 opens on the two facts that explain every String surprise in Java:
# a String is an OBJECT (so `==` asks the wrong question) and it is IMMUTABLE
# (so every method returns a new one and ignoring the return value is a no-op).
# The API tour is module 7; this module is the model underneath it.
#
# Scanner note: every program here reads whole lines with `sc.nextLine()`, so
# spaces in the input are preserved. Programs that also need a number read the
# line(s) first and the number last, which side-steps the classic
# nextInt()/nextLine() leftover-newline trap.
# ---------------------------------------------------------------------------

_M6 = []

_RD_LINE = "        String s = sc.nextLine();\n"
_RD_2LINE = ("        String s = sc.nextLine();\n"
             "        String t = sc.nextLine();\n")
_RD_LINE_INT = _RD_LINE + "        int k = sc.nextInt();\n"


def _lkcase(s, k, out):
    """stdin = one line of text, then an integer on the next line."""
    return _case(f"{s}\n{k}", out)


def _cmp_sign(s, t):
    """Python mirror of `Integer.signum(s.compareTo(t))`. Java compares char by
    char and falls back to the length difference, which for ASCII data is the
    same ordering Python's `<` gives — but the mirror is written out rather
    than assumed."""
    for i in range(min(len(s), len(t))):
        if s[i] != t[i]:
            d = ord(s[i]) - ord(t[i])
            return 1 if d > 0 else -1
    d = len(s) - len(t)
    return 0 if d == 0 else (1 if d > 0 else -1)


# --- 6.1 Creating strings ---------------------------------------------------

_M6.append(_jlesson(
    "m6-create", "Creating a String",
    "Literals, the string pool, `new String`, and the `length` that needs parentheses.",
    """
A `String` is an **object**, not a primitive. That one fact drives everything
in this module.

**Two ways to make one, and they are not the same:**

```java
String a = "hello";                 // a LITERAL — goes in the string pool
String b = "hello";                 // the SAME pooled object; a == b is true
String c = new String("hello");     // a brand new object on the heap
                                     // c == a is FALSE; c.equals(a) is true
```

The **string pool** is a cache the JVM keeps of every literal in your program.
Identical literals are stored once and shared, because strings are immutable
and therefore safe to share. `new String(...)` explicitly opts out and
allocates a fresh object — which is why you should essentially never write it.
Its only real use is forcing a distinct object for a demonstration exactly like
this one.

A string built at runtime — read from input, or assembled with `+` from
variables — is **not** pooled, so `==` against a literal is false even when the
characters match. That is the single most common Java beginner bug, and
lesson 6.4 is entirely about it.

**`length()` has parentheses.** Arrays use the field `a.length`; strings use the
method `s.length()`. Mixing them up is a compile error in both directions,
which is the one mercy:

```java
"hello".length()      // 5
new int[5].length     // 5
```

**Empty is not null.**

```java
String empty = "";      // a real String, length 0
String missing = null;  // no object at all — any method call throws NPE
```

`""` is a perfectly good string you can call methods on. `null` is the absence
of one, and `missing.length()` is a `NullPointerException`. Java 11 added
`isEmpty()` for `length() == 0`, and `isBlank()` for "empty or only
whitespace" — module 7.
""",
    warmup=[
        _jq("```java\nString a = \"hi\";\nString b = \"hi\";\nString c = new String(\"hi\");\nSystem.out.println((a == b) + \" \" + (a == c));\n```",
            ["true false", "true true", "false false", "false true"],
            0,
            "`a` and `b` are the same pooled literal, so `==` is true. `new String` forces a "
            "separate object, so `a == c` is false even though the text matches."),
        _jq("Which line does NOT compile?",
            ["`int n = s.length;`", "`int n = s.length();`",
             "`int n = a.length;` where a is an int[]", "`String e = \"\";`"],
            0,
            "`length` is a method on String and a field on arrays. Getting it backwards fails "
            "at compile time in both directions."),
    ],
    exercises=[
        _je("j6-cre-length", "How long is the line?",
            "Read one line of text and print how many characters it holds. Replace "
            "`____` — and remember this is a String, not an array.",
            _jscan(_RD_LINE + "        System.out.println(s.length());"),
            "s.length()",
            [_scase(s, len(s)) for s in ("hello", "a b c", "x", "the quick brown fox")],
            hints=["Strings expose length as a method.",
                   "That means parentheses.",
                   "`s.length()`"],
            difficulty="Intro"),

        _je("j6-cre-empty", "Is there anything there?",
            "Print `true` when the line has no characters at all, otherwise `false`. "
            "Use the length, not a library helper. Replace `____` with the condition.",
            _jscan(_RD_LINE + "        System.out.println(s.length() == 0);"),
            "s.length() == 0",
            # NOTE: the empty case is stdin "\n" — a blank LINE. Feeding a
            # zero-byte stdin would make `sc.nextLine()` throw
            # NoSuchElementException before the program could answer anything.
            [_case("\n", "true")]
            + [_scase(s, _jbool(len(s) == 0)) for s in ("hello", " ", "x")],
            hints=["An empty string has length 0.",
                   "Compare the length against 0 with `==`.",
                   "`s.length() == 0` — note that a single space is NOT empty."],
            difficulty="Intro"),

        _je("j6-cre-copy", "Same text, different object",
            "`t` is deliberately built with `new String(s)`, so it holds the same "
            "characters in a different object. Print `false true` — the reference "
            "comparison, then the content comparison. Replace `____` with the second "
            "one.",
            _jscan(
                _RD_LINE
                + "        String t = new String(s);\n"
                  '        System.out.println((s == t) + " " + s.equals(t));'),
            "s.equals(t)",
            [_scase(s, "false true") for s in ("hello", "a b", "x")],
            hints=["`==` asks 'same object?'. You want 'same characters?'.",
                   "That question is a method on String.",
                   "`s.equals(t)`"]),

        _jfix("j6-cre-field", "length without the parentheses",
              "This should print the length of the line, but it does not compile. Fix "
              "it.",
              _jscan(_RD_LINE + "        System.out.println(s.length);"),
              _jscan(_RD_LINE + "        System.out.println(s.length());"),
              [_scase(s, len(s)) for s in ("hello", "a b c", "z")],
              hints=["Is `length` a field or a method on a String?",
                     "Arrays have the field; Strings have the method.",
                     "`s.length()`"],
              difficulty="Intro"),

        _jch("j6-cre-total", "Two lines, one total", "Easy",
             "Read two lines and print three things on one line, space separated: the "
             "length of the first, the length of the second, and their total. Write "
             "the whole block where you see `____`.",
             _jscan(
                 _RD_2LINE
                 + '        System.out.println(s.length() + " " + t.length() + " " + (s.length() + t.length()));'),
             '        System.out.println(s.length() + " " + t.length() + " " + (s.length() + t.length()));',
             [_s2case(s, t, f"{len(s)} {len(t)} {len(s) + len(t)}")
              for (s, t) in (("hello", "world"), ("a", "bcd"), ("one two", "three"))],
             hints=["`sc.nextLine()` twice gives you both lines.",
                    "Build the output with `+`.",
                    "The total needs its own parentheses — `+ (s.length() + t.length())` — or "
                    "Java will concatenate the two numbers as text instead of adding them. "
                    "That trap gets its own lesson in 6.5."]),
    ],
    quiz=[
        _jq("Why is it safe for the JVM to share one object between two identical literals?",
            ["Strings are immutable, so no holder of the reference can change it",
             "Because literals are constants",
             "It isn't safe — the pool is a legacy mistake",
             "Because the compiler copies them anyway"],
            0,
            "Sharing mutable objects would be a disaster; sharing immutable ones is free. "
            "Immutability is what makes the pool possible."),
        _jq("`String s = null; System.out.println(s.length());` does what?",
            ["Throws NullPointerException at runtime",
             "Prints 0", "Prints -1", "Fails to compile"],
            0,
            "`null` means there is no object to call a method on. `\"\"` — a real, empty "
            "string — would print 0."),
    ],
))

# --- 6.2 Immutability -------------------------------------------------------

_M6.append(_jlesson(
    "m6-immutable", "Immutability",
    "Every String method returns a new String — and ignoring it does nothing at all.",
    """
**A `String`'s characters can never change.** There is no method anywhere in
the class that modifies the string it is called on. Every method that looks
like it edits the text actually **returns a new String** and leaves the
original exactly as it was.

```java
String s = "hello";
s.toUpperCase();                     // creates "HELLO"... and throws it away
System.out.println(s);               // hello

s = s.toUpperCase();                 // NOW s refers to the new string
System.out.println(s);               // HELLO
```

The first version compiles cleanly, runs without complaint, and does nothing.
No warning, no exception. It is the single most common String bug in Java, and
it applies to every method in the class: `substring`, `replace`, `trim`,
`concat`, all of them.

**The rule:** if a String method's result matters, **assign it to something**.

**What `s = s.toUpperCase()` actually does.** It does not change the string —
it changes what `s` points at. The old string is untouched and is garbage
collected once nothing refers to it. If another variable still points at the
original, it still sees the original:

```java
String a = "hi";
String b = a;
a = a + "!";                          // a is a NEW string
System.out.println(b);                // hi — b never moved
```

Compare with module 1's arrays: `int[] b = a; b[0] = 99;` *does* change what
`a` sees, because arrays are mutable. Strings cannot be aliased into trouble
that way — immutability makes them safe to share, which is exactly why the pool
works and why `String` is the standard type for map keys.

**The cost.** Every `+` allocates. Building a string in a loop:

```java
String out = "";
for (int i = 0; i < n; i++) out = out + i;    // allocates a NEW string each pass
```

is O(n²) work, because each round copies everything built so far. For `n` in
the thousands that is genuinely slow. The fix is `StringBuilder` — module 8,
which exists entirely because of this paragraph.
""",
    warmup=[
        _jq("```java\nString s = \"hello\";\ns.toUpperCase();\nSystem.out.println(s);\n```",
            ["hello", "HELLO", "It does not compile", "An empty line"],
            0,
            "`toUpperCase()` returns a new string, which is discarded. The original is "
            "untouched — no warning, no error, no effect."),
        _jq("```java\nString a = \"hi\";\nString b = a;\na = a + \"!\";\nSystem.out.println(b);\n```",
            ["hi", "hi!", "null", "It does not compile"],
            0,
            "`a + \"!\"` builds a new string and points `a` at it. `b` still refers to the "
            "original, which was never modified — unlike the array case in module 1."),
    ],
    exercises=[
        _je("j6-imm-assign", "Keep the result",
            "Print the line in upper case. `toUpperCase()` returns the new string "
            "rather than changing `s`, so replace `____` with a statement that keeps "
            "the result.",
            _jscan(
                _RD_LINE
                + "        s = s.toUpperCase();\n"
                  "        System.out.println(s);"),
            "s = s.toUpperCase();",
            [_scase(s, s.upper()) for s in ("hello", "Mixed Case", "abc def", "X")],
            hints=["The method gives you a new string; you have to catch it.",
                   "Point `s` at the result.",
                   "`s = s.toUpperCase();`"],
            difficulty="Intro"),

        _je("j6-imm-concat", "Add to the end",
            "Print the line with an exclamation mark appended. Replace `____` with "
            "the statement that builds the new string and keeps it.",
            _jscan(
                _RD_LINE
                + '        s = s + "!";\n'
                  "        System.out.println(s);"),
            's = s + "!";',
            [_scase(s, s + "!") for s in ("hello", "hi there", "x")],
            hints=["`+` on strings builds a new one.",
                   "Assign it back to `s`.",
                   '`s = s + "!";` — or the equivalent `s += "!";`'],
            difficulty="Intro"),

        _jfix("j6-imm-lost", "The change that vanished",
              "This should print the line in upper case with an exclamation mark. It "
              "prints the line completely unchanged. Neither method call is wrong — "
              "something else is.",
              _jscan(
                  _RD_LINE
                  + "        s.toUpperCase();\n"
                    '        s.concat("!");\n'
                    "        System.out.println(s);"),
              _jscan(
                  _RD_LINE
                  + "        s = s.toUpperCase();\n"
                    '        s = s.concat("!");\n'
                    "        System.out.println(s);"),
              [_scase(s, s.upper() + "!") for s in ("hello", "a b", "Zz")],
              hints=["What does a String method do with its result?",
                     "Nothing in the String class ever modifies the string it is called on.",
                     "Assign both results back: `s = s.toUpperCase();` and "
                     '`s = s.concat("!");`']),

        _jch("j6-imm-repeat", "Build it up in a loop", "Easy",
             "Read a line and then a number `k`. Print the line repeated `k` times, "
             "with no separator, built by concatenating in a loop. (This is "
             "deliberately the O(n²) way — module 8 shows the fast one.) Write the "
             "whole block where you see `____`.",
             _jscan(
                 _RD_LINE_INT
                 + '        String out = "";\n'
                   "        for (int i = 0; i < k; i++) out = out + s;\n"
                   "        System.out.println(out);"),
             '        String out = "";\n'
             "        for (int i = 0; i < k; i++) out = out + s;\n"
             "        System.out.println(out);",
             [_lkcase(s, k, s * k)
              for (s, k) in (("ab", 3), ("x", 1), ("hi ", 2), ("q", 0))],
             hints=['Start from the empty string `""`, not from `null`.',
                    "Each pass has to keep the result: `out = out + s;`",
                    "With `k = 0` the loop never runs and the answer is an empty line — which "
                    "is correct."]),
    ],
    quiz=[
        _jq("Why is `String` immutable, given the inconvenience?",
            ["It makes strings safe to share and cache — the pool, and safe map keys",
             "To save memory in every case",
             "Because the JVM cannot modify heap objects",
             "For backwards compatibility with C"],
            0,
            "Sharing one object between many holders is only safe if nobody can change it. "
            "It also means a String used as a HashMap key cannot have its hash change "
            "underneath the map."),
        _jq("`out = out + i;` inside a loop of n iterations costs…",
            ["O(n²), because each pass copies everything built so far",
             "O(n), because concatenation is O(1)",
             "O(n log n)",
             "O(1) — the compiler optimises it away"],
            0,
            "Each `+` allocates a new string and copies the old contents. Java does optimise "
            "a single expression's `+` chain, but not one that spans loop iterations."),
    ],
))

# --- 6.3 Indexing -----------------------------------------------------------


def _middle(s):
    n = len(s)
    return s[(n - 1) // 2:(n + 2) // 2] if n % 2 == 0 else s[n // 2]


_M6.append(_jlesson(
    "m6-index", "Reaching inside: `charAt` and `substring`",
    "Zero-based positions, half-open ranges, and the exception waiting at the end.",
    """
A String indexes exactly like an array — from `0` to `length() - 1` — but with
methods instead of brackets.

```java
String s = "hello";
s.charAt(0)                 // 'h'   — a char, not a String
s.charAt(s.length() - 1)    // 'o'   — the last character
s.charAt(s.length())        // StringIndexOutOfBoundsException
```

**`charAt` returns a `char`,** which is a primitive holding one UTF-16 code
unit — not a one-character String. That matters: `char` compares with `==`
(and it is the *correct* operator there), and `char` arithmetic works, so
`s.charAt(i) - 'a'` gives 0 for `'a'`, 1 for `'b'`, and so on. That expression
is how you index a counting array by letter, which is module 7's frequency
work.

**`substring` is half-open**, exactly like `Arrays.copyOfRange` in module 1:

```java
s.substring(1, 4)          // "ell"  — index 1 up to, but NOT including, 4
s.substring(2)             // "llo"  — from 2 to the end
s.substring(0, s.length()) // the whole string
s.substring(3, 3)          // ""     — an empty range is legal
```

The length of `s.substring(a, b)` is always `b - a`. Every range API in Java
follows this rule, and once you trust it, off-by-ones stop happening.

**The legal end index is `length()`, not `length() - 1`.** `substring` takes a
*boundary*, and there is a boundary after the last character. So
`s.substring(0, s.length())` is fine while `s.charAt(s.length())` throws —
`charAt` takes a *position*, and there is no character there. Boundaries versus
positions is the whole distinction.

**Useful one-liners built from these two:**

```java
s.substring(0, s.length() - 1)      // drop the last character
s.substring(1)                       // drop the first character
s.charAt(s.length() / 2)             // the middle character (odd length)
```

Walking a string is module 1's index loop with `charAt`:

```java
for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    ...
}
```
""",
    warmup=[
        _jq("`\"hello\".substring(1, 4)` is…",
            ["\"ell\"", "\"ello\"", "\"hell\"", "\"ell\" only if you also call trim()"],
            0,
            "Half-open: index 1 included, index 4 excluded. The length is always `to - from` "
            "— here 3."),
        _jq("Which of these throws?",
            ["s.charAt(s.length())", "s.substring(0, s.length())",
             "s.substring(s.length())", "s.charAt(s.length() - 1)"],
            0,
            "`substring` takes boundaries, and there is a boundary after the last character. "
            "`charAt` takes a position, and there is no character at index `length()`."),
    ],
    exercises=[
        _je("j6-idx-char", "One character",
            "Read a line, then an index `k`, and print the character at that "
            "position. Replace `____`.",
            _jscan(_RD_LINE_INT + "        System.out.println(s.charAt(k));"),
            "s.charAt(k)",
            [_lkcase(s, k, s[k])
             for (s, k) in (("hello", 0), ("hello", 4), ("a b c", 2), ("x", 0))],
            hints=["The method takes the position and gives you the character.",
                   "Positions start at 0.",
                   "`s.charAt(k)`"],
            difficulty="Intro"),

        _je("j6-idx-ends", "First and last",
            "Print the first and last characters of the line, separated by a space. "
            "Replace `____` with the expression for the **last** one.",
            _jscan(
                _RD_LINE
                + '        System.out.println(s.charAt(0) + " " + s.charAt(s.length() - 1));'),
            "s.charAt(s.length() - 1)",
            [_scase(s, f"{s[0]} {s[-1]}") for s in ("hello", "ab", "z", "a b")],
            hints=["The last valid position is one less than the length.",
                   "`s.length()` itself is out of range for `charAt`.",
                   "`s.charAt(s.length() - 1)`"],
            difficulty="Intro"),

        _je("j6-idx-sub", "A slice of text",
            "Read a line, then `from` and `to` on the following lines, and print the "
            "slice from `from` up to but not including `to`. Replace `____`.",
            _jscan(
                _RD_LINE
                + "        int from = sc.nextInt();\n"
                  "        int to = sc.nextInt();\n"
                  "        System.out.println(s.substring(from, to));"),
            "s.substring(from, to)",
            [_case(f"{s}\n{f_}\n{t}", s[f_:t])
             for (s, f_, t) in (("hello", 1, 4), ("hello", 0, 5),
                                ("abcdef", 2, 3), ("abcdef", 3, 3))],
            hints=["Two arguments: the start, then the exclusive end.",
                   "The result's length is always `to - from`.",
                   "`s.substring(from, to)`"]),

        _jfix("j6-idx-last", "One past the end",
              "This should print the last character of the line. It throws "
              "`StringIndexOutOfBoundsException`. Fix it.",
              _jscan(_RD_LINE + "        System.out.println(s.charAt(s.length()));"),
              _jscan(_RD_LINE + "        System.out.println(s.charAt(s.length() - 1));"),
              [_scase(s, s[-1]) for s in ("hello", "z", "ab c")],
              hints=["Valid positions run from 0 to length() - 1.",
                     "There is no character sitting at index `length()`.",
                     "`s.charAt(s.length() - 1)`"],
              difficulty="Intro"),

        _jch("j6-idx-middle", "The middle", "Medium",
             "Print the middle of the line: the single middle character when the "
             "length is odd, or the **two** middle characters when it is even. For "
             "`hello` print `l`; for `code` print `od`. Write the whole block where "
             "you see `____`.",
             _jscan(
                 _RD_LINE
                 + "        int n = s.length();\n"
                   "        if (n % 2 == 1) {\n"
                   "            System.out.println(s.charAt(n / 2));\n"
                   "        } else {\n"
                   "            System.out.println(s.substring(n / 2 - 1, n / 2 + 1));\n"
                   "        }"),
             "        int n = s.length();\n"
             "        if (n % 2 == 1) {\n"
             "            System.out.println(s.charAt(n / 2));\n"
             "        } else {\n"
             "            System.out.println(s.substring(n / 2 - 1, n / 2 + 1));\n"
             "        }",
             [_scase(s, _middle(s)) for s in ("hello", "code", "x", "ab", "abcdefg")],
             hints=["Odd and even need different answers, so branch on `n % 2`.",
                    "For odd length the middle position is `n / 2` (integer division).",
                    "For even length the two middle characters run from `n / 2 - 1` up to "
                    "`n / 2 + 1` — remember `substring`'s end is exclusive, so that is "
                    "exactly two characters."]),
    ],
    quiz=[
        _jq("What type does `s.charAt(0)` return?",
            ["char — a primitive, comparable with ==", "String of length 1",
             "int", "Character"],
            0,
            "A `char` is a primitive, so `==` is the right comparison and arithmetic like "
            "`c - 'a'` works. A one-character String would need `.equals`."),
        _jq("What is `\"abc\".substring(3)`?",
            ["\"\" — the empty string", "\"c\"", "It throws", "null"],
            0,
            "`length()` is a legal boundary, so starting there gives an empty string. "
            "`substring(4)` would throw."),
    ],
))

# --- 6.4 Comparison ---------------------------------------------------------

_M6.append(_jlesson(
    "m6-equals", "`equals` versus `==`",
    "The most-failed Java question, and the ordering methods that go with it.",
    """
```java
String a = "hello";
String b = new String("hello");

a == b          // false — two different objects
a.equals(b)     // true  — the same characters
```

**`==` on objects compares references: "is this the same object?"** For
strings that is almost never the question you mean. `equals` compares
**contents**, which is what you want essentially always.

**Why it seems to work sometimes.** Identical *literals* are shared through the
pool, so `"hi" == "hi"` really is `true`. That is exactly what makes the bug so
dangerous: it passes every test you write with literals, then fails in
production the moment a string comes from user input, a file, or a network
response — because those are not pooled.

```java
String typed = sc.nextLine();        // user types: hello
typed == "hello"                      // false! different object
typed.equals("hello")                 // true
```

**Put the literal first when the other side might be null:**

```java
if ("quit".equals(command)) { ... }   // safe even when command is null
if (command.equals("quit")) { ... }   // NullPointerException when it is
```

This is not a style tic; it is the standard way to avoid a whole class of
crash. (`Objects.equals(a, b)` handles null on both sides.)

**The comparison family:**

| Call | Question |
|---|---|
| `a.equals(b)` | exactly the same characters? |
| `a.equalsIgnoreCase(b)` | the same ignoring case? |
| `a.compareTo(b)` | ordering: negative / 0 / positive |
| `a.compareToIgnoreCase(b)` | the same, case-insensitively |

**`compareTo` returns a number, not a boolean.** It compares character by
character and returns the difference at the first mismatch; if one string is a
prefix of the other, it returns the length difference. You care about the
**sign**, not the magnitude:

- negative → `a` comes before `b`
- zero → equal
- positive → `a` comes after `b`

`Integer.signum(...)` collapses it to −1 / 0 / 1 when you only want the
direction. The ordering is by UTF-16 code unit, so all uppercase letters sort
before all lowercase ones: `"Zebra".compareTo("apple")` is negative, because
`'Z'` is 90 and `'a'` is 97. That surprises people, and it is why
`compareToIgnoreCase` exists.
""",
    warmup=[
        _jq("A user types `hello`. What does `typed == \"hello\"` give?",
            ["false — the typed string is a new object, not the pooled literal",
             "true — the characters match",
             "true, but only on some JVMs",
             "It does not compile"],
            0,
            "Runtime-built strings are not pooled. This is why `==` appears to work in "
            "hand-written tests and fails on real input."),
        _jq("Why is `\"quit\".equals(command)` preferred over `command.equals(\"quit\")`?",
            ["It cannot throw NullPointerException when `command` is null",
             "It is faster",
             "It ignores case",
             "There is no difference"],
            0,
            "A literal is never null, so calling `equals` on it is always safe. The reverse "
            "order crashes on a null `command`."),
    ],
    exercises=[
        _je("j6-eq-equals", "Same text?",
            "Read two lines and print `true` when they hold exactly the same "
            "characters. Replace `____` with the comparison.",
            _jscan(_RD_2LINE + "        System.out.println(s.equals(t));"),
            "s.equals(t)",
            [_s2case(s, t, _jbool(s == t))
             for (s, t) in (("hello", "hello"), ("hello", "Hello"),
                            ("abc", "abd"), ("x", "x"))],
            hints=["`==` would ask a different question — 'same object?'.",
                   "Content comparison is a method.",
                   "`s.equals(t)`"],
            difficulty="Intro"),

        _je("j6-eq-ignore", "Same text, ignoring case",
            "Same two lines, but treat upper and lower case as equal. Replace "
            "`____`.",
            _jscan(_RD_2LINE + "        System.out.println(s.equalsIgnoreCase(t));"),
            "s.equalsIgnoreCase(t)",
            [_s2case(s, t, _jbool(s.lower() == t.lower()))
             for (s, t) in (("hello", "HELLO"), ("Hello", "hello"),
                            ("abc", "abd"), ("MiXeD", "mixed"))],
            hints=["There is a dedicated method for this — you do not need to lower-case "
                   "both sides yourself.",
                   "Its name says exactly what it does.",
                   "`s.equalsIgnoreCase(t)`"],
            difficulty="Intro"),

        _je("j6-eq-order", "Which comes first?",
            "Print `-1` when the first line sorts before the second, `0` when they "
            "are equal, and `1` when it sorts after. `Integer.signum` collapses "
            "`compareTo`'s raw number down to the sign — replace `____` with what "
            "goes inside it.",
            _jscan(_RD_2LINE
                   + "        System.out.println(Integer.signum(s.compareTo(t)));"),
            "s.compareTo(t)",
            [_s2case(s, t, _cmp_sign(s, t))
             for (s, t) in (("apple", "banana"), ("banana", "apple"),
                            ("apple", "apple"), ("Zebra", "apple"), ("ab", "abc"))],
            hints=["The ordering method returns a number, not a boolean.",
                   "Negative means the receiver sorts first.",
                   "`s.compareTo(t)` — and note that `Zebra` sorts BEFORE `apple`, because "
                   "uppercase letters have smaller code units."],
            difficulty="Medium"),

        _jfix("j6-eq-refeq", "It never matches",
              "This should print `true` when the two typed lines are the same text. It "
              "prints `false` even for identical input. Fix it.",
              _jscan(_RD_2LINE + "        System.out.println(s == t);"),
              _jscan(_RD_2LINE + "        System.out.println(s.equals(t));"),
              [_s2case(s, t, _jbool(s == t))
               for (s, t) in (("hello", "hello"), ("abc", "abd"), ("x", "x"))],
              hints=["What question does `==` ask about two objects?",
                     "Both lines came from input, so they are two separate objects even when "
                     "the text matches.",
                     "`s.equals(t)`"]),

        _jch("j6-eq-sorted", "Put them in order", "Medium",
             "Read two lines and print them on two lines in alphabetical order "
             "(smaller first). If they are equal, either order is the same output. "
             "Use `compareTo`. Write the whole block where you see `____`.",
             _jscan(
                 _RD_2LINE
                 + "        if (s.compareTo(t) <= 0) {\n"
                   "            System.out.println(s);\n"
                   "            System.out.println(t);\n"
                   "        } else {\n"
                   "            System.out.println(t);\n"
                   "            System.out.println(s);\n"
                   "        }"),
             "        if (s.compareTo(t) <= 0) {\n"
             "            System.out.println(s);\n"
             "            System.out.println(t);\n"
             "        } else {\n"
             "            System.out.println(t);\n"
             "            System.out.println(s);\n"
             "        }",
             [_s2case(s, t, _nl(*sorted([s, t], key=lambda x: [ord(c) for c in x])))
              for (s, t) in (("banana", "apple"), ("apple", "banana"),
                             ("same", "same"), ("Zebra", "apple"))],
             hints=["Compare with `compareTo` and branch on the SIGN of the result.",
                    "`<= 0` means 'first one sorts first, or they are equal'.",
                    "Do not compare with `<` against a string — `compareTo` gives you an int, "
                    "and that int is what you test."]),
    ],
    quiz=[
        _jq("`\"Zebra\".compareTo(\"apple\")` is negative. Why?",
            ["'Z' is code unit 90 and 'a' is 97, so uppercase sorts before lowercase",
             "Because Zebra is shorter",
             "Because Z comes after a in the alphabet, so it is inverted",
             "It is actually positive"],
            0,
            "`compareTo` orders by code unit, not by dictionary convention. "
            "`compareToIgnoreCase` gives the ordering people usually expect."),
        _jq("When IS `==` the right operator for text comparison?",
            ["On `char` values — `s.charAt(i) == 'a'` is correct",
             "Never, in any circumstance",
             "Whenever both sides are literals",
             "When comparing a String to null is impossible"],
            0,
            "`char` is a primitive, so `==` compares values. It is String — an object — where "
            "`==` asks the wrong question."),
    ],
))

# --- 6.5 Concatenation ------------------------------------------------------

_M6.append(_jlesson(
    "m6-concat", "Building strings with `+`",
    "The one operator Java overloads — and the evaluation order that catches everybody.",
    """
`+` is the only operator Java overloads: on numbers it adds, and if **either
side is a String** it concatenates, converting the other side to text first.

```java
"total: " + 5        // "total: 5"       int becomes "5"
"x" + 'y'            // "xy"             char becomes "y"
"flag: " + true      // "flag: true"
"n: " + null         // "n: null"        even null, without throwing
```

**The trap is evaluation order.** `+` is left-associative, and the decision to
add or to concatenate is made **per operator**, left to right:

```java
System.out.println(1 + 2 + "a");     // "3a"   — 1+2 is arithmetic, then concat
System.out.println("a" + 1 + 2);     // "a12"  — concat, then concat again
```

Nothing about the second line is a special case: once the left operand is a
String, every following `+` is concatenation. Force the arithmetic with
parentheses:

```java
System.out.println("sum: " + a + b);      // "sum: 34"  — almost never wanted
System.out.println("sum: " + (a + b));    // "sum: 7"
```

That parenthesis is the single most common source of wrong output in beginner
Java, and you have already met it in module 6.1's challenge.

**The alternatives:**

```java
s.concat("!")                 // Strings only; throws on null; rarely used
String.valueOf(42)            // "42"    — the explicit, null-safe conversion
Integer.toString(42)          // "42"    — same result, number types only
String.format("%s is %d", name, age)      // printf-style templating
"-".repeat(20)                // Java 11+ — a line of dashes
```

`String.valueOf(x)` is what `+` calls under the covers. It is worth knowing by
name because it handles `null` by producing `"null"` rather than throwing,
which `x.toString()` does not.

**What `+` costs.** In a single expression the compiler collapses the whole
chain into one `StringBuilder`, so `"a" + b + "c" + d` is efficient. Across
**loop iterations** it cannot, so each pass allocates and copies — the O(n²)
problem from lesson 6.2, and the reason module 8 exists.
""",
    warmup=[
        _jq("`System.out.println(1 + 2 + \"a\" + 3 + 4);`",
            ["3a34", "1234a", "3a7", "10a"],
            0,
            "Left to right: 1+2 is arithmetic (3), then `3 + \"a\"` concatenates, and from "
            "there every `+` is concatenation."),
        _jq("`int a = 3, b = 4; System.out.println(\"sum: \" + a + b);`",
            ["sum: 34", "sum: 7", "sum: 3 4", "It does not compile"],
            0,
            "The left operand is already a String, so both `+`s concatenate. "
            "`\"sum: \" + (a + b)` gives `sum: 7`."),
    ],
    exercises=[
        _je("j6-cat-greet", "Build a greeting",
            "Read a name on one line and print `Hello, <name>!` — for `Ada`, print "
            "`Hello, Ada!`. Replace `____` with the expression.",
            _jscan(_RD_LINE + '        System.out.println("Hello, " + s + "!");'),
            '"Hello, " + s + "!"',
            [_scase(s, f"Hello, {s}!") for s in ("Ada", "Grace Hopper", "X")],
            hints=["Three pieces glued with `+`.",
                   "Mind the comma and the space in the first piece.",
                   '`"Hello, " + s + "!"`'],
            difficulty="Intro"),

        _je("j6-cat-sum", "Label a number",
            "Read a line, then two integers `a` and `b`. Print "
            "`<line>: <a plus b>` — for the line `total` and the numbers 3 and 4, "
            "print `total: 7`. Replace `____` with the expression, and mind the "
            "evaluation order.",
            _jscan(
                _RD_LINE
                + "        int a = sc.nextInt();\n"
                  "        int b = sc.nextInt();\n"
                  '        System.out.println(s + ": " + (a + b));'),
            's + ": " + (a + b)',
            [_case(f"{s}\n{x}\n{y}", f"{s}: {x + y}")
             for (s, x, y) in (("total", 3, 4), ("score", 10, -2), ("n", 0, 0))],
            hints=["Once the left side is a String, every `+` after it concatenates.",
                   "So the addition has to be forced to happen first.",
                   '`s + ": " + (a + b)` — the parentheses are load-bearing.']),

        _jfix("j6-cat-parens", "It glued the numbers together",
              "This should print the sum of `a` and `b` after the label. For 3 and 4 "
              "it prints `sum: 34` instead of `sum: 7`. Fix it.",
              _jscan(
                  "        int a = sc.nextInt();\n"
                  "        int b = sc.nextInt();\n"
                  '        System.out.println("sum: " + a + b);'),
              _jscan(
                  "        int a = sc.nextInt();\n"
                  "        int b = sc.nextInt();\n"
                  '        System.out.println("sum: " + (a + b));'),
              [_case(f"{x}\n{y}", f"sum: {x + y}")
               for (x, y) in ((3, 4), (10, -2), (0, 0))],
              hints=["`+` is left-associative and decides its meaning one operator at a time.",
                     "The first `+` has a String on the left, so it concatenates — and so does "
                     "the next one.",
                     "Wrap the addition: `(a + b)`."],
              difficulty="Intro"),

        _jch("j6-cat-list", "Comma-separate the lines", "Medium",
             "Read `k` on the first line, then `k` more lines. Print them all on one "
             "line separated by `, ` — with no trailing comma. For 3 lines `a`, `b`, "
             "`c` print `a, b, c`. Write the whole block where you see `____`.",
             _jscan(
                 "        int k = Integer.parseInt(sc.nextLine());\n"
                 '        String out = "";\n'
                 "        for (int i = 0; i < k; i++) {\n"
                 "            String line = sc.nextLine();\n"
                 '            if (i > 0) out = out + ", ";\n'
                 "            out = out + line;\n"
                 "        }\n"
                 "        System.out.println(out);"),
             '        String out = "";\n'
             "        for (int i = 0; i < k; i++) {\n"
             "            String line = sc.nextLine();\n"
             '            if (i > 0) out = out + ", ";\n'
             "            out = out + line;\n"
             "        }\n"
             "        System.out.println(out);",
             [_case(f"{len(parts)}\n" + "\n".join(parts), ", ".join(parts))
              for parts in (["a", "b", "c"], ["solo"], ["one", "two"],
                            ["red", "green", "blue", "black"])],
             hints=['Start with `String out = "";` and append as you go.',
                    "The separator goes BEFORE every piece except the first — that is what "
                    "`if (i > 0)` is for. Appending it after each piece leaves a trailing "
                    "comma.",
                    "`Integer.parseInt(sc.nextLine())` reads the count as a whole line, so the "
                    "following `nextLine()` calls line up cleanly.",
                    "Module 7 does this in one call with `String.join`."]),
    ],
    quiz=[
        _jq("What does `String.valueOf(null_object)` give, versus `null_object.toString()`?",
            ["\"null\" versus a NullPointerException",
             "Both give \"null\"",
             "Both throw",
             "\"\" versus \"null\""],
            0,
            "`String.valueOf` is null-safe by design, which is exactly why `+` uses it "
            "internally and never throws on a null operand."),
        _jq("`\"a\" + b + \"c\" + d` in one expression is compiled to…",
            ["a single StringBuilder chain — it is efficient",
             "four separate String allocations",
             "a call to String.concat three times",
             "the same O(n²) code as a loop"],
            0,
            "The compiler collapses a whole `+` chain within one expression. What it cannot "
            "collapse is concatenation spread across loop iterations."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m6_card(s, k):
    return _nl(
        f"len={len(s)}",
        f"upper={s.upper()}",
        f"first={s[0]}",
        f"last={s[-1]}",
        f"head={s[:k]}",
        f"tail={s[len(s) - k:]}",
        f"same={_jbool(s[:k] == s[len(s) - k:])}",
    )


_M6_CAP = _jcap(
    "String inspector",
    """
Everything in module 6 applied to one line of text.

Read a line `s` (it may contain spaces), then an integer `k` on the next line.
You may assume `1 <= k <= s.length()`. Print seven lines:

```
len=<s.length()>
upper=<s in upper case>
first=<the first character>
last=<the last character>
head=<the first k characters>
tail=<the last k characters>
same=<true when head and tail are the same text, else false>
```

Three things this is really testing:

- **`upper` needs the return value assigned or used.** `s.toUpperCase();` on
  its own does nothing — lesson 6.2's whole point.
- **`tail` is `s.substring(s.length() - k)`**, the one-argument form. Trying to
  write it as a two-argument call is where the off-by-one lives.
- **`same` uses `.equals`, not `==`.** Both halves are runtime-built strings,
  so `==` would print `false` even for `abab` with `k = 2`.

Read the line first and the number second — that ordering keeps the Scanner out
of trouble.
""",
    _jch("j6-cap-inspect", "String inspector", "Medium",
         "Write the whole report where you see `____` — seven `key=value` lines, in "
         "the order `len`, `upper`, `first`, `last`, `head`, `tail`, `same`.",
         _jscan(
             _RD_LINE_INT
             + '        System.out.println("len=" + s.length());\n'
               '        System.out.println("upper=" + s.toUpperCase());\n'
               '        System.out.println("first=" + s.charAt(0));\n'
               '        System.out.println("last=" + s.charAt(s.length() - 1));\n'
               "        String head = s.substring(0, k);\n"
               "        String tail = s.substring(s.length() - k);\n"
               '        System.out.println("head=" + head);\n'
               '        System.out.println("tail=" + tail);\n'
               '        System.out.println("same=" + head.equals(tail));'),
         '        System.out.println("len=" + s.length());\n'
         '        System.out.println("upper=" + s.toUpperCase());\n'
         '        System.out.println("first=" + s.charAt(0));\n'
         '        System.out.println("last=" + s.charAt(s.length() - 1));\n'
         "        String head = s.substring(0, k);\n"
         "        String tail = s.substring(s.length() - k);\n"
         '        System.out.println("head=" + head);\n'
         '        System.out.println("tail=" + tail);\n'
         '        System.out.println("same=" + head.equals(tail));',
         [_lkcase(s, k, _m6_card(s, k))
          for (s, k) in (("hello", 2), ("abab", 2), ("racecar", 3),
                         ("x", 1), ("the quick fox", 3), ("Mixed Case", 5))],
         hints=["`s.toUpperCase()` returns the new string — use it in the concatenation "
                "directly, or assign it first.",
                "`head` is `s.substring(0, k)` — the two-argument, half-open form.",
                "`tail` is `s.substring(s.length() - k)` — the one-argument form, which runs "
                "to the end.",
                "Compare `head` and `tail` with `.equals`; `==` would ask whether they are the "
                "same object, and they never are.",
                "No spaces around the `=` in the output."]),
    example_io="stdin:  hello\n        2\n\n"
               "stdout: len=5\n        upper=HELLO\n        first=h\n        last=o\n"
               "        head=he\n        tail=lo\n        same=false",
    rubric=[
        "The line is read with `nextLine()`, so input containing spaces still works.",
        "`upper` uses the value `toUpperCase()` returns rather than calling it and dropping it.",
        "`head` and `tail` are both exactly `k` characters, for every legal `k`.",
        "`same` uses `.equals`, and prints `true` for `abab` with `k = 2`.",
        "It survives a one-character line with `k = 1`.",
        "All seven lines print, in order, with no spaces around `=`.",
    ],
)


_MODULES.append(_jmod(
    6, 2, "Strings",
    "The object behind the text",
    "Understand what a String actually is — an immutable object, sometimes pooled — "
    "and get `equals`, `charAt`, `substring` and `+` right for the reasons rather "
    "than by memory.",
    """
Part 2 opens with the model, not the API. Two facts explain every String
surprise in Java:

**A String is an object.** So `==` asks "same object?", which is the wrong
question, and the string pool makes that wrong question *look* right whenever
you test with literals.

**A String is immutable.** So every method returns a new string and changes
nothing, and ignoring the return value is a silent no-op. It is also why
building text in a loop with `+` is quadratic, which is the entire reason
module 8 exists.

Get these two right and module 7's forty-odd methods are just vocabulary.
""",
    _M6,
    capstone=_M6_CAP,
    objectives=[
        "Explain the string pool and predict `==` for literals, `new String`, and input.",
        "Say why every String method returns a new object, and spot a dropped return value.",
        "Index with `charAt` and slice with `substring`, and say why one accepts `length()` and the other does not.",
        "Choose between `equals`, `equalsIgnoreCase` and `compareTo`, and put the literal first for null safety.",
        "Predict the output of any `+` chain mixing numbers and text.",
        "State why concatenating in a loop is O(n²) and name the fix.",
    ],
    why="`equals` versus `==` is the most-asked and most-failed Java interview question, "
        "and 'the string method that did nothing' is the bug that costs beginners the "
        "most hours. Both are consequences of the same two facts.",
    est_minutes=270,
    glossary=[
        _jg("immutable", "Cannot be changed after construction. Every String method returns a "
                         "new String and leaves the original alone."),
        _jg("string pool", "A JVM-wide cache of literals, so identical literals are one shared "
                           "object. Safe only because strings are immutable."),
        _jg("literal", 'A string written directly in source: `"hello"`. Literals are pooled; '
                       "runtime-built strings are not."),
        _jg("reference equality", "`==`, which asks whether two variables point at the same "
                                  "object. Almost never what you want for text."),
        _jg("value equality", "`.equals()`, which compares contents. What you want for text, "
                              "essentially always."),
        _jg("char", "A primitive holding one UTF-16 code unit. Compared with `==`, and "
                    "arithmetic works: `c - 'a'` gives a 0-based letter index."),
        _jg("half-open range", "`substring(from, to)` includes `from` and excludes `to`, so "
                               "the length is `to - from`. Every Java range works this way."),
        _jg("compareTo", "Ordering by code unit: negative, zero or positive. Uppercase sorts "
                         "before lowercase, which is why `compareToIgnoreCase` exists."),
        _jg("String.valueOf", "The null-safe conversion to text. What `+` calls internally, "
                              "which is why `\"x\" + null` prints `xnull` rather than throwing."),
    ],
    cheatsheet="""
```java
// --- create -------------------------------------------------------------
String a = "hello";                 // literal — POOLED
String b = new String("hello");     // new object — a == b is FALSE
String empty = "";                  // real, length 0
String missing = null;              // no object — any call throws NPE

s.length()                          // METHOD (arrays use the FIELD .length)

// --- immutability: assign the result, always ---------------------------
s.toUpperCase();                    // does NOTHING — result discarded
s = s.toUpperCase();                // correct

// --- index and slice ----------------------------------------------------
s.charAt(0)                         // char, not String
s.charAt(s.length() - 1)            // last char  (charAt takes a POSITION)
s.substring(1, 4)                   // half-open: length is 4 - 1 = 3
s.substring(2)                      // from 2 to the end
s.substring(0, s.length())          // legal — substring takes a BOUNDARY
s.substring(0, s.length() - 1)      // drop the last character

for (int i = 0; i < s.length(); i++) { char c = s.charAt(i); ... }

// --- compare ------------------------------------------------------------
s.equals(t)                         // contents          <- use this
s == t                              // same object?      <- almost never
s.equalsIgnoreCase(t)
Integer.signum(s.compareTo(t))      // -1 / 0 / 1
"quit".equals(command)              // literal first: null-safe

// --- build --------------------------------------------------------------
"total: " + 5                       // "total: 5"
1 + 2 + "a"                         // "3a"
"a" + 1 + 2                         // "a12"
"sum: " + (a + b)                   // parentheses are load-bearing
String.valueOf(42)                  // null-safe conversion
String.format("%s is %d", name, n)
"-".repeat(20)                      // Java 11+

String out = "";
for (...) out = out + x;            // O(n^2) — use StringBuilder (module 8)
```
""",
    self_check=[
        "Can you predict `==` for two literals, a literal and `new String`, and a literal and typed input?",
        "Can you spot a dropped return value — `s.trim();` on its own — in someone else's code?",
        "Can you say why `s.substring(0, s.length())` is fine but `s.charAt(s.length())` throws?",
        "Do you write `\"quit\".equals(cmd)` rather than `cmd.equals(\"quit\")` without thinking about it?",
        "Can you predict the output of `1 + 2 + \"a\" + 3 + 4` and explain each step?",
        "Can you explain why `\"Zebra\".compareTo(\"apple\")` is negative?",
    ],
    review=[
        _jq("`String s = sc.nextLine();` and the user types `yes`. Which test is correct?",
            ["\"yes\".equals(s)", "s == \"yes\"", "\"yes\" == s", "s.compareTo(\"yes\")"],
            0,
            "Input is not pooled, so both `==` forms are false. Putting the literal first "
            "also protects against `s` being null. `compareTo` returns an int, not a boolean."),
        _jq("`s = \"hello\"; s.substring(1, 3); System.out.println(s);` prints…",
            ["hello", "el", "ell", "It does not compile"],
            0,
            "`substring` returns a new string that is immediately discarded. Immutability "
            "again — nothing you call can change `s`."),
        _jq("The length of `s.substring(a, b)` is always…",
            ["b - a", "b - a + 1", "b", "s.length() - a"],
            0,
            "Half-open ranges always have length `to - from` — the same rule as "
            "`Arrays.copyOfRange` in module 1."),
        _jq("Building a 10,000-character string with `out += c` in a loop does roughly how much copying?",
            ["About 50 million character copies — it is quadratic",
             "10,000 copies — it is linear",
             "None; the compiler uses a StringBuilder",
             "It throws OutOfMemoryError"],
            0,
            "Each pass copies everything so far: 1 + 2 + … + 10,000 ≈ 5 × 10⁷. `StringBuilder` "
            "does it in one pass."),
    ],
    milestone="You know what a String actually is, so `equals` versus `==` and the "
              "method-that-did-nothing are no longer things you memorise — they are things "
              "you can derive.",
))
