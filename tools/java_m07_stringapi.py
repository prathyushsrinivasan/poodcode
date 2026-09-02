# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 7 — The String API and the classic string problems.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# Module 6 built the model; this is the vocabulary plus the four problems that
# get asked by name: reversal, palindrome, character frequency, anagram.
#
# StringBuilder is still banned by the linter until module 8, on purpose: the
# reversal here is written with `+` in a loop so that module 8's opening claim
# ("this is quadratic and here is the fix") lands on something you have
# actually written.
# ---------------------------------------------------------------------------

_M7 = []

_RD_LINE = "        String s = sc.nextLine();\n"
_RD_2LINE = ("        String s = sc.nextLine();\n"
             "        String t = sc.nextLine();\n")


# --- Python mirrors ---------------------------------------------------------

def _count_sub(s, t):
    """Non-overlapping occurrences, matching the indexOf/fromIndex loop."""
    return s.count(t)


def _title(s):
    return s[:1].upper() + s[1:].lower()


def _letter_freq(s):
    f = [0] * 26
    for ch in s:
        if "a" <= ch <= "z":
            f[ord(ch) - ord("a")] += 1
    return f


def _top_letter(s):
    f = _letter_freq(s)
    best = 0
    for v in range(1, 26):
        if f[v] > f[best]:
            best = v
    return chr(ord("a") + best)


def _is_anagram(s, t):
    if len(s) != len(t):
        return False
    return sorted(s) == sorted(t)


def _clean_palindrome(s):
    kept = [c.lower() for c in s if c.isalpha() and c.isascii()]
    return kept == kept[::-1]


def _longest_word(words):
    best = words[0]
    for w in words[1:]:
        if len(w) > len(best):
            best = w
    return best


# --- 7.1 Searching inside a string -----------------------------------------

_M7.append(_jlesson(
    "m7-search", "Finding things: `indexOf` and friends",
    "The -1 convention again, the `fromIndex` overload, and the readable wrappers.",
    """
Everything in this group answers "is it in there, and where?".

```java
s.indexOf("lo")           // first index, or -1
s.indexOf("lo", 5)        // first index at or after 5, or -1
s.lastIndexOf("l")        // last index, or -1
s.contains("ell")         // boolean — indexOf(x) >= 0, spelled readably
s.startsWith("he")        // boolean
s.endsWith("lo")          // boolean
s.isEmpty()               // length() == 0
s.isBlank()               // Java 11+: empty, or only whitespace
```

**`indexOf` returns `-1` when absent** — module 1's sentinel convention,
straight out of the standard library. That leads to the single most common bug
in this group:

```java
if (s.indexOf("he") > 0)  { ... }     // WRONG: misses a match at index 0
if (s.indexOf("he") >= 0) { ... }     // right
if (s.contains("he"))      { ... }    // better — says what you mean
```

Index 0 is a perfectly good hit. Use `contains` when you only care whether it
is there; it is the same call with the comparison already done correctly.

**The `fromIndex` overload is how you find *every* occurrence.** Search, then
resume just past what you found:

```java
int count = 0;
int i = s.indexOf(t);
while (i >= 0) {
    count++;
    i = s.indexOf(t, i + t.length());     // skip past the match
}
```

Resuming at `i + t.length()` counts **non-overlapping** occurrences: `"aaa"`
contains `"aa"` twice if you allow overlaps and once if you do not. Resuming at
`i + 1` gives you the overlapping count. Deciding which one the question wants
is the interesting half of the problem.

**`indexOf` also works on a single `char`,** which is faster and needs no
quotes-versus-apostrophes thought: `s.indexOf('a')`.

**`isEmpty()` versus `isBlank()`.** `"   ".isEmpty()` is false — there really
are three characters. `"   ".isBlank()` is true. For validating user input you
almost always want `isBlank`.

**Cost.** `indexOf` is a straightforward scan: O(n·m) worst case for a pattern
of length m, with no clever preprocessing. That is fine for ordinary text and
is worth knowing when someone asks about substring search algorithms.
""",
    warmup=[
        _jq("`\"hello\".indexOf(\"he\")` returns 0. What does `if (s.indexOf(\"he\") > 0)` do?",
            ["Misses the match, because 0 is not greater than 0",
             "Works correctly",
             "Throws",
             "Matches only when the needle appears twice"],
            0,
            "`-1` is the only failure value, so the test has to be `>= 0`. `contains` avoids "
            "the question entirely."),
        _jq("Counting `\"aa\"` in `\"aaaa\"`, resuming at `i + t.length()` gives…",
            ["2 — non-overlapping", "3 — overlapping", "4", "1"],
            0,
            "Matches at 0 and 2. Resuming at `i + 1` instead would find 0, 1, 2 — three "
            "overlapping matches."),
    ],
    exercises=[
        _je("j7-srch-index", "Where does it start?",
            "Read two lines: the text, then the thing to look for. Print the index of "
            "its first occurrence, or `-1`. Replace `____`.",
            _jscan(_RD_2LINE + "        System.out.println(s.indexOf(t));"),
            "s.indexOf(t)",
            [_s2case(s, t, s.find(t))
             for (s, t) in (("hello world", "world"), ("hello", "he"),
                            ("hello", "xyz"), ("abcabc", "c"))],
            hints=["The method is named for what it returns.",
                   "It gives -1 when the needle is absent.",
                   "`s.indexOf(t)`"],
            difficulty="Intro"),

        _je("j7-srch-last", "The last one",
            "Same two lines, but print the index of the **last** occurrence, or `-1`. "
            "Replace `____`.",
            _jscan(_RD_2LINE + "        System.out.println(s.lastIndexOf(t));"),
            "s.lastIndexOf(t)",
            [_s2case(s, t, s.rfind(t))
             for (s, t) in (("abcabc", "c"), ("abcabc", "abc"),
                            ("hello", "l"), ("hello", "z"))],
            hints=["There is a matching method that scans from the end.",
                   "It still returns -1 when absent.",
                   "`s.lastIndexOf(t)`"],
            difficulty="Intro"),

        _je("j7-srch-contains", "Is it in there?",
            "Print `true` when the second line appears anywhere in the first. Use the "
            "method that says what you mean, not an index comparison. Replace `____`.",
            _jscan(_RD_2LINE + "        System.out.println(s.contains(t));"),
            "s.contains(t)",
            [_s2case(s, t, _jbool(t in s))
             for (s, t) in (("hello world", "lo w"), ("hello", "he"),
                            ("hello", "xyz"), ("abc", "abc"))],
            hints=["One method returns a boolean directly.",
                   "It is the readable form of `indexOf(t) >= 0`.",
                   "`s.contains(t)`"],
            difficulty="Intro"),

        _jfix("j7-srch-zero", "It misses matches at the start",
              "This should print `true` when the second line appears in the first. It "
              "prints `false` when the match is right at the beginning — try `hello` "
              "and `he`. Fix the test.",
              _jscan(_RD_2LINE + "        System.out.println(s.indexOf(t) > 0);"),
              _jscan(_RD_2LINE + "        System.out.println(s.indexOf(t) >= 0);"),
              [_s2case(s, t, _jbool(t in s))
               for (s, t) in (("hello", "he"), ("hello", "lo"), ("hello", "zz"))],
              hints=["What value does `indexOf` return when the needle IS at index 0?",
                     "-1 is the only 'not found' value, so every other result is a hit.",
                     "`s.indexOf(t) >= 0` — or better, `s.contains(t)`."]),

        _jch("j7-srch-count", "How many times?", "Medium",
             "Print how many **non-overlapping** times the second line occurs in the "
             "first. Use `indexOf` with its `fromIndex` overload — no nested loops. "
             "Write the whole block where you see `____`.",
             _jscan(
                 _RD_2LINE
                 + "        int count = 0;\n"
                   "        int i = s.indexOf(t);\n"
                   "        while (i >= 0) {\n"
                   "            count++;\n"
                   "            i = s.indexOf(t, i + t.length());\n"
                   "        }\n"
                   "        System.out.println(count);"),
             "        int count = 0;\n"
             "        int i = s.indexOf(t);\n"
             "        while (i >= 0) {\n"
             "            count++;\n"
             "            i = s.indexOf(t, i + t.length());\n"
             "        }\n"
             "        System.out.println(count);",
             [_s2case(s, t, _count_sub(s, t))
              for (s, t) in (("aaaa", "aa"), ("abcabcabc", "abc"),
                             ("hello", "z"), ("banana", "na"), ("aaa", "a"))],
             hints=["Find the first match before the loop, then loop while it is not -1.",
                    "Resume the search just past the match you counted: "
                    "`s.indexOf(t, i + t.length())`.",
                    "Resuming at `i + 1` would count overlapping matches instead — `aaaa` "
                    "would give 3 rather than 2."]),
    ],
    quiz=[
        _jq("`\"   \".isEmpty()` and `\"   \".isBlank()` give…",
            ["false and true", "true and true", "false and false", "true and false"],
            0,
            "Three spaces are three real characters, so it is not empty — but it is blank. "
            "`isBlank` is what you want for validating input."),
        _jq("Why prefer `s.contains(t)` over `s.indexOf(t) >= 0`?",
            ["It states the intent and removes the chance of writing `> 0`",
             "It is asymptotically faster",
             "It handles null t",
             "It is the only one that works on empty strings"],
            0,
            "They compile to the same scan. `contains` simply cannot be written with the "
            "off-by-one that `indexOf` invites."),
    ],
))

# --- 7.2 Transforming -------------------------------------------------------

_M7.append(_jlesson(
    "m7-transform", "Transforming: case, whitespace, replacement",
    "All of these return a new String — and one of them takes a regex.",
    """
```java
s.toUpperCase()        s.toLowerCase()
s.trim()               // removes chars <= ' ' from both ends
s.strip()              // Java 11+: Unicode-aware trim
s.replace("a", "o")    // ALL occurrences; plain text, no regex
s.repeat(3)            // Java 11+
```

Every one of them returns a new String and changes nothing — module 6's rule,
and it does not stop being true because the method has a more exciting name.

**`replace` replaces every occurrence, not just the first.** There is no
"replace first" in `String`; if you need it you slice around `indexOf`
yourself.

**`replace` is plain text; `replaceAll` is a regex.** This is the sharpest edge
in the whole String class:

```java
"a.b.c".replace(".", "-")       // "a-b-c"     — literal dot
"a.b.c".replaceAll(".", "-")    // "-----"     — regex dot = ANY character
```

Both compile. Both run. One of them quietly destroys your data. **If you do not
want a regex, use `replace`** — and the same warning applies to `split`, which
is regex-only and gets its own lesson next.

**`trim` versus `strip`.** `trim()` removes anything with a code point at or
below `' '` (space, tab, newline, and a handful of control characters).
`strip()` (Java 11) uses the proper Unicode definition of whitespace, so it also
handles non-breaking spaces. For ASCII input they agree; prefer `strip` in new
code.

**Chaining reads left to right** and each step operates on the previous
result:

```java
s.trim().toLowerCase().replace(" ", "-")     // "  Hello World " -> "hello-world"
```

Each link allocates a new string. For three steps that is irrelevant; inside a
hot loop over millions of rows it is worth noticing.

**Building a "title case" word** is the standard exercise, and it is just
module 6's `substring` twice:

```java
s.substring(0, 1).toUpperCase() + s.substring(1).toLowerCase()
```

`substring(0, 1)` rather than `charAt(0)` because a `char` has no
`toUpperCase()` of its own — that lives on `Character`, which is lesson 7.4.
""",
    warmup=[
        _jq("`\"a.b.c\".replaceAll(\".\", \"-\")` gives…",
            ["\"-----\"", "\"a-b-c\"", "\"abc\"", "It throws"],
            0,
            "`replaceAll` takes a regex, and `.` matches any character. `replace` — no "
            "'All' — is the literal-text version and gives `a-b-c`."),
        _jq("`String s = \"  hi  \"; s.trim(); System.out.println(s.length());`",
            ["6", "2", "4", "It does not compile"],
            0,
            "`trim()` returns a new string that is thrown away. The original still has both "
            "pairs of spaces. Immutability, again."),
    ],
    exercises=[
        _je("j7-tr-lower", "Fold the case",
            "Print the line in lower case. Replace `____` — and keep the result.",
            _jscan(_RD_LINE + "        System.out.println(s.toLowerCase());"),
            "s.toLowerCase()",
            [_scase(s, s.lower()) for s in ("HELLO", "MiXeD Case", "already")],
            hints=["There is a method for each direction.",
                   "It returns the new string rather than modifying `s`.",
                   "`s.toLowerCase()`"],
            difficulty="Intro"),

        _je("j7-tr-trim", "Cut the padding",
            "Print the line with leading and trailing spaces removed, wrapped in "
            "square brackets so you can see the result. Replace `____`.",
            _jscan(_RD_LINE + '        System.out.println("[" + s.trim() + "]");'),
            "s.trim()",
            [_scase(s, "[" + s.strip() + "]")
             for s in ("  hi  ", "hi", "   spaced   out   ", "  ")],
            hints=["One call removes whitespace from both ends.",
                   "It does not touch spaces in the middle.",
                   "`s.trim()`"],
            difficulty="Intro"),

        _je("j7-tr-replace", "Swap every occurrence",
            "Print the line with every letter `a` replaced by `o`. Use the literal "
            "(non-regex) method. Replace `____`.",
            _jscan(_RD_LINE + '        System.out.println(s.replace("a", "o"));'),
            's.replace("a", "o")',
            [_scase(s, s.replace("a", "o"))
             for s in ("banana", "abcabc", "no vowels here", "aaa")],
            hints=["The plain-text method has no `All` in its name.",
                   "It replaces every occurrence, not just the first.",
                   '`s.replace("a", "o")`'],
            difficulty="Intro"),

        _jfix("j7-tr-dropped", "The trim that did nothing",
              "This should print the length of the line **after** trimming its "
              "surrounding spaces. It prints the untrimmed length. Fix it.",
              _jscan(
                  _RD_LINE
                  + "        s.trim();\n"
                    "        System.out.println(s.length());"),
              _jscan(
                  _RD_LINE
                  + "        s = s.trim();\n"
                    "        System.out.println(s.length());"),
              [_scase(s, len(s.strip())) for s in ("  hi  ", "hi", "   a b   ")],
              hints=["Strings are immutable — what does `trim()` do with its result?",
                     "Nothing in the String class modifies the string it is called on.",
                     "`s = s.trim();`"],
              difficulty="Intro"),

        _jch("j7-tr-title", "Title case one word", "Medium",
             "Print the line with its first character upper-cased and every other "
             "character lower-cased — `hELLO` becomes `Hello`. Assume the line is not "
             "empty. Write the whole block where you see `____`.",
             _jscan(
                 _RD_LINE
                 + "        System.out.println(s.substring(0, 1).toUpperCase() + s.substring(1).toLowerCase());"),
             "        System.out.println(s.substring(0, 1).toUpperCase() + s.substring(1).toLowerCase());",
             [_scase(s, _title(s))
              for s in ("hELLO", "hello", "HELLO", "x", "mixed CASE here")],
             hints=["Two slices: the first character, and everything after it.",
                    "`substring(0, 1)` gives a one-character String, which has "
                    "`toUpperCase()`; a `char` would not.",
                    "Glue the two transformed pieces with `+`."]),
    ],
    quiz=[
        _jq("You need to turn every `|` in a line into a comma. Which call is safe?",
            ["replace(\"|\", \",\") — literal text",
             "replaceAll(\"|\", \",\") — it is the same thing",
             "Either; `|` is not special",
             "split(\"|\") then join"],
            0,
            "`|` is regex alternation, so `replaceAll(\"|\", \",\")` matches the empty string "
            "everywhere and inserts commas between every character. `replace` is literal."),
        _jq("`s.trim().toLowerCase().replace(\" \", \"-\")` allocates how many strings?",
            ["Three — one per step", "One", "None; it is done in place", "Two"],
            0,
            "Each call returns a new String. Irrelevant for one line, worth noticing inside a "
            "loop over millions of rows."),
    ],
))

# --- 7.3 split and join -----------------------------------------------------

_M7.append(_jlesson(
    "m7-split", "`split`, `join`, and `toCharArray`",
    "Text to array and back — with the regex trap that catches everyone once.",
    """
```java
String[] parts = s.split(" ");             // "a b c" -> {"a", "b", "c"}
String joined  = String.join("-", parts);  // {"a","b","c"} -> "a-b-c"
char[] chars   = s.toCharArray();          // "abc" -> {'a','b','c'}
```

Now every array technique from Part 1 applies to text: traverse it, sort it,
count it, two-pointer it.

**`split` takes a REGEX, always.** There is no literal-text version. So:

```java
"a.b.c".split(".")        // an EMPTY array — `.` matches every character
"a.b.c".split("\\\\.")      // {"a", "b", "c"} — the escaped, literal dot
"a|b".split("|")          // splits between every character
"a b".split("\\\\s+")       // splits on any run of whitespace — the useful one
```

The characters you must escape are `. | * + ? ^ $ ( ) [ ] { } \\`. In Java
source the backslash itself needs escaping, so a literal dot is the four
characters `"\\\\."`. Getting an unexpectedly empty array back from `split` is
almost always this.

**Splitting on runs of whitespace** is what you actually want for word
counting, because it survives double spaces:

```java
String[] words = s.trim().split("\\\\s+");
```

Without the `trim()`, a leading space produces an empty first element —
`split` strips trailing empties but keeps leading ones.

**`String.join` is the inverse** and takes the separator first. It is the
one-call version of module 6's manual comma-separator loop, including getting
the "no trailing separator" part right.

**`toCharArray` gives you a real `char[]`** — a mutable copy, so writing to it
does not affect the string (which could not be modified anyway). It is how you
sort the characters of a word, which is lesson 7.6's anagram check:

```java
char[] cs = s.toCharArray();
Arrays.sort(cs);                    // module 3's sort, on characters
```

`Arrays.toString(cs)` prints it as `[a, b, c]`; `new String(cs)` turns it back
into text.
""",
    warmup=[
        _jq("`\"a.b.c\".split(\".\").length` is…",
            ["0", "3", "1", "5"],
            0,
            "`.` is the regex 'any character', so every character is a separator and every "
            "piece is empty — and `split` drops trailing empty pieces, leaving nothing."),
        _jq("Which splits `\"the  quick   fox\"` (irregular spacing) into exactly 3 words?",
            ["s.trim().split(\"\\\\s+\")", "s.split(\" \")",
             "s.split(\"\\\\s\")", "s.split(\"  \")"],
            0,
            "`\\s+` matches a run of whitespace, so repeated spaces do not produce empty "
            "pieces. The `trim()` handles a leading space."),
    ],
    exercises=[
        _je("j7-sp-count", "How many words?",
            "The line holds words separated by single spaces. Print how many there "
            "are. Replace `____` with the split.",
            _jscan(
                _RD_LINE
                + '        String[] parts = s.split(" ");\n'
                  "        System.out.println(parts.length);"),
            's.split(" ")',
            [_scase(s, len(s.split(" ")))
             for s in ("the quick brown fox", "one", "a b", "x y z w v")],
            hints=["The separator is a single space, written as a String.",
                   "It returns a `String[]`, so `.length` (the array field) gives the count.",
                   '`s.split(" ")`'],
            difficulty="Intro"),

        _je("j7-sp-first", "The first word",
            "Print the first space-separated word of the line. Replace `____`.",
            _jscan(
                _RD_LINE
                + '        String[] parts = s.split(" ");\n'
                  "        System.out.println(parts[0]);"),
            "parts[0]",
            [_scase(s, s.split(" ")[0])
             for s in ("the quick brown fox", "solo", "a b c")],
            hints=["`split` gives you an ordinary array.",
                   "So index it exactly as in module 1.",
                   "`parts[0]`"],
            difficulty="Intro"),

        _je("j7-sp-join", "Glue them back",
            "Split the line on spaces and print the pieces re-joined with hyphens. "
            "Replace `____` with the join call — separator first.",
            _jscan(
                _RD_LINE
                + '        String[] parts = s.split(" ");\n'
                  '        System.out.println(String.join("-", parts));'),
            'String.join("-", parts)',
            [_scase(s, "-".join(s.split(" ")))
             for s in ("the quick fox", "solo", "a b c d")],
            hints=["It is a static method on `String`.",
                   "The separator is the FIRST argument.",
                   '`String.join("-", parts)`'],
            difficulty="Intro"),

        _jfix("j7-sp-regex", "Split on a dot, get nothing",
              "This should split `a.b.c` into three pieces and print how many there "
              "are. It prints `0`. The separator is being read as a regex.",
              _jscan(
                  _RD_LINE
                  + '        String[] parts = s.split(".");\n'
                    "        System.out.println(parts.length);"),
              _jscan(
                  _RD_LINE
                  + '        String[] parts = s.split("\\\\.");\n'
                    "        System.out.println(parts.length);"),
              [_scase(s, len(s.split(".")))
               for s in ("a.b.c", "one.two", "nodots")],
              hints=["`split` always takes a regex. What does `.` mean in a regex?",
                     "It matches ANY character, so every piece comes out empty.",
                     'Escape it — and in Java source the backslash itself needs escaping, so '
                     'the argument is `"\\\\."`.'],
              difficulty="Medium"),

        _jch("j7-sp-reverse", "Reverse the word order", "Medium",
             "The line holds words separated by single spaces. Print the same words "
             "in reverse order, still space separated. Split, walk the array "
             "backwards, and join with `+`. Write the whole block where you see "
             "`____`.",
             _jscan(
                 _RD_LINE
                 + '        String[] parts = s.split(" ");\n'
                   '        String out = "";\n'
                   "        for (int i = parts.length - 1; i >= 0; i--) {\n"
                   '            if (i < parts.length - 1) out = out + " ";\n'
                   "            out = out + parts[i];\n"
                   "        }\n"
                   "        System.out.println(out);"),
             '        String out = "";\n'
             "        for (int i = parts.length - 1; i >= 0; i--) {\n"
             '            if (i < parts.length - 1) out = out + " ";\n'
             "            out = out + parts[i];\n"
             "        }\n"
             "        System.out.println(out);",
             [_scase(s, " ".join(reversed(s.split(" "))))
              for s in ("the quick brown fox", "solo", "a b", "one two three")],
             hints=["Module 1's backwards loop: start at `parts.length - 1`, stop at `>= 0`.",
                    "The separator goes before every piece except the first one you emit — "
                    "which is the piece at the highest index.",
                    "A trailing space would also pass (the judge trims it), but getting the "
                    "separator logic right is the exercise."]),
    ],
    quiz=[
        _jq("You are splitting a CSV line on commas. Is `split(\",\")` safe?",
            ["Yes — a comma has no special meaning in a regex",
             "No — commas must be escaped as \"\\\\,\"",
             "No — you must use `replace` first",
             "Only if the line has no spaces"],
            0,
            "`,` is an ordinary character. The dangerous separators are the metacharacters: "
            ". | * + ? ^ $ ( ) [ ] { } and backslash."),
        _jq("`String.join` takes its arguments in which order?",
            ["Separator first, then the pieces", "Pieces first, then the separator",
             "It takes only an array", "It is not a static method"],
            0,
            "`String.join(\"-\", parts)`. It also accepts a varargs list of strings directly, "
            "which is module 9's varargs in the wild."),
    ],
))

# --- 7.4 Characters ---------------------------------------------------------


def _classify(s):
    letters = sum(1 for c in s if c.isascii() and c.isalpha())
    digits = sum(1 for c in s if c.isascii() and c.isdigit())
    return letters, digits, len(s) - letters - digits


_M7.append(_jlesson(
    "m7-chars", "Working with characters",
    "`Character` tests, char arithmetic, and the `==` that is finally correct.",
    """
Walking a string is module 1's index loop with `charAt`:

```java
for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    ...
}
```

**`char` is a primitive, so `==` is right here.** After a whole module of
"never use `==` on strings", this is the exception that is not an exception:
`s.charAt(i) == 'a'` compares two `char` values, which is exactly what you
want. Note the **single quotes**: `'a'` is a char, `"a"` is a String, and they
are not interchangeable. A `char` has no methods at all, so
`s.charAt(i).equals('a')` does not compile.

**The `Character` class holds the tests,** as static methods:

```java
Character.isDigit(c)          Character.isLetter(c)
Character.isLetterOrDigit(c)  Character.isWhitespace(c)
Character.isUpperCase(c)      Character.isLowerCase(c)
Character.toUpperCase(c)      Character.toLowerCase(c)   // return a char
```

Use these rather than hand-rolling `c >= 'a' && c <= 'z'` — they are clearer
and they are right about characters outside ASCII.

**Char arithmetic is the trick behind letter counting.** A `char` is a number,
so subtracting gives you an offset:

```java
'a' - 'a'    // 0
'c' - 'a'    // 2
'z' - 'a'    // 25
```

which makes `s.charAt(i) - 'a'` a 0-based index into a 26-slot counting array —
module 4's counting array, applied to letters. This is the standard shape of
every "character frequency" question:

```java
int[] freq = new int[26];
for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;
```

It assumes lowercase ASCII letters only; anything else indexes out of range or,
worse, into the wrong slot. Lower-case the input first and skip non-letters.

**Digits convert the same way:** `c - '0'` turns `'7'` into the `int` 7. That is
how you parse a number by hand — and it is why `'7'` and `7` are different
things. `(int) '7'` is 55, its code unit.
""",
    warmup=[
        _jq("`s.charAt(i).equals('a')` — what happens?",
            ["It does not compile: char is a primitive with no methods",
             "It works, and is preferred over ==",
             "It compiles but is always false",
             "It throws NullPointerException"],
            0,
            "Primitives have no methods. Compare chars with `==`, which is genuinely correct "
            "here because it compares values, not references."),
        _jq("What is `'c' - 'a'`?",
            ["2 — chars are numbers, so subtracting gives an offset",
             "\"c-a\"", "0", "A compile error"],
            0,
            "That offset is exactly the index into a 26-slot counting array, which is how "
            "every letter-frequency problem is solved."),
    ],
    exercises=[
        _je("j7-ch-digits", "Count the digits",
            "Print how many characters of the line are digits. Replace `____` with "
            "the test.",
            _jscan(
                _RD_LINE
                + "        int count = 0;\n"
                  "        for (int i = 0; i < s.length(); i++) {\n"
                  "            if (Character.isDigit(s.charAt(i))) count++;\n"
                  "        }\n"
                  "        System.out.println(count);"),
            "Character.isDigit(s.charAt(i))",
            [_scase(s, sum(1 for c in s if c.isdigit()))
             for s in ("abc123", "no digits", "42", "a1b2c3")],
            hints=["The tests live on the `Character` class, as static methods.",
                   "Pass it the character at position `i`.",
                   "`Character.isDigit(s.charAt(i))`"],
            difficulty="Intro"),

        _je("j7-ch-vowels", "Count the vowels",
            "Print how many characters are vowels (`a e i o u`, lower case only). "
            "Replace `____` with the condition — and note that `==` is the right "
            "operator for chars.",
            _jscan(
                _RD_LINE
                + "        int count = 0;\n"
                  "        for (int i = 0; i < s.length(); i++) {\n"
                  "            char c = s.charAt(i);\n"
                  "            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') count++;\n"
                  "        }\n"
                  "        System.out.println(count);"),
            "c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u'",
            [_scase(s, sum(1 for c in s if c in "aeiou"))
             for s in ("banana", "sky", "education", "aeiou")],
            hints=["Five comparisons joined with `||`.",
                   "Single quotes for chars — `'a'`, not `\"a\"`.",
                   "`c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u'`"]),

        _je("j7-ch-offset", "Letter to index",
            "Print the 0-based alphabet position of the line's first character "
            "(`a` is 0, `z` is 25). The line starts with a lowercase letter. Replace "
            "`____` with the expression.",
            _jscan(_RD_LINE + "        System.out.println(s.charAt(0) - 'a');"),
            "s.charAt(0) - 'a'",
            [_scase(s, ord(s[0]) - ord("a")) for s in ("apple", "zebra", "cat", "moon")],
            hints=["Chars are numbers, so you can subtract one from another.",
                   "Subtract the character that should map to 0.",
                   "`s.charAt(0) - 'a'`"]),

        _jfix("j7-ch-quotes", "String where a char belongs",
              "This should count how many characters are the letter `a`. It does not "
              "compile. Fix the comparison.",
              _jscan(
                  _RD_LINE
                  + "        int count = 0;\n"
                    "        for (int i = 0; i < s.length(); i++) {\n"
                    '            if (s.charAt(i) == "a") count++;\n'
                    "        }\n"
                    "        System.out.println(count);"),
              _jscan(
                  _RD_LINE
                  + "        int count = 0;\n"
                    "        for (int i = 0; i < s.length(); i++) {\n"
                    "            if (s.charAt(i) == 'a') count++;\n"
                    "        }\n"
                    "        System.out.println(count);"),
              [_scase(s, s.count("a")) for s in ("banana", "xyz", "aaa")],
              hints=["What type does `charAt` return, and what type is `\"a\"`?",
                     "A char and a String cannot be compared.",
                     "Use single quotes: `'a'`."],
              difficulty="Intro"),

        _jch("j7-ch-classify", "Letters, digits, everything else", "Medium",
             "Print three numbers on one line, space separated: how many characters "
             "are letters, how many are digits, and how many are neither. Write the "
             "whole block where you see `____`.",
             _jscan(
                 _RD_LINE
                 + "        int letters = 0;\n"
                   "        int digits = 0;\n"
                   "        int other = 0;\n"
                   "        for (int i = 0; i < s.length(); i++) {\n"
                   "            char c = s.charAt(i);\n"
                   "            if (Character.isLetter(c)) letters++;\n"
                   "            else if (Character.isDigit(c)) digits++;\n"
                   "            else other++;\n"
                   "        }\n"
                   '        System.out.println(letters + " " + digits + " " + other);'),
             "        int letters = 0;\n"
             "        int digits = 0;\n"
             "        int other = 0;\n"
             "        for (int i = 0; i < s.length(); i++) {\n"
             "            char c = s.charAt(i);\n"
             "            if (Character.isLetter(c)) letters++;\n"
             "            else if (Character.isDigit(c)) digits++;\n"
             "            else other++;\n"
             "        }\n"
             '        System.out.println(letters + " " + digits + " " + other);',
             [_scase(s, "%d %d %d" % _classify(s))
              for s in ("abc123 !", "hello", "42", "   ", "a1!b2?")],
             hints=["Three counters, declared before the loop.",
                    "An `if / else if / else` chain, so each character is counted exactly once.",
                    "Spaces and punctuation both fall into `other`."]),
    ],
    quiz=[
        _jq("Why is `int[] freq = new int[26]; freq[c - 'a']++;` dangerous on arbitrary input?",
            ["Anything outside 'a'..'z' produces an index outside 0..25",
             "Because `char` arithmetic is undefined",
             "Because 26 should be 25",
             "It isn't — Java clamps the index"],
            0,
            "An uppercase 'A' gives -32; a space gives -65. Lower-case the input and skip "
            "non-letters first."),
        _jq("`(int) '7'` versus `'7' - '0'` give…",
            ["55 and 7", "7 and 7", "55 and 55", "7 and 55"],
            0,
            "The cast exposes the code unit; the subtraction converts the digit character to "
            "its numeric value. That difference is the whole of hand-rolled parsing."),
    ],
))

# --- 7.5 Reversal and palindromes ------------------------------------------

_M7.append(_jlesson(
    "m7-classic", "Reversal and palindromes",
    "Two named questions, and why the good palindrome answer never reverses anything.",
    """
**Reversing a string** without `StringBuilder` (module 8) is module 1's
backwards loop:

```java
String out = "";
for (int i = s.length() - 1; i >= 0; i--) out = out + s.charAt(i);
```

Correct, and **O(n²)** — every `+` copies everything built so far. Remember
that number; module 8 opens by fixing it.

**Palindrome** — reads the same forwards and backwards. The obvious answer is
to reverse and compare:

```java
s.equals(reversed)          // O(n) time, O(n) extra space
```

The better answer never builds anything. It is module 4's two pointers, walking
inward and comparing as they go:

```java
int i = 0, j = s.length() - 1;
boolean pal = true;
while (i < j) {
    if (s.charAt(i) != s.charAt(j)) { pal = false; break; }
    i++;
    j--;
}
```

**O(n) time, O(1) space, and it exits early** on the first mismatch. `abcdef`
is rejected after one comparison, where the reverse-and-compare version builds
a whole new string first. That is the answer an interviewer is after, and the
reason this lesson sits after module 4 rather than before it.

**`i < j` again.** They meet on the middle character of an odd-length string,
which is trivially equal to itself.

**The realistic version** — "is `A man, a plan, a canal: Panama` a
palindrome?" — adds two rules: **ignore case**, and **skip anything that is not
a letter**. Do it with the same two pointers and two skip loops:

```java
while (i < j) {
    while (i < j && !Character.isLetter(s.charAt(i))) i++;
    while (i < j && !Character.isLetter(s.charAt(j))) j--;
    if (Character.toLowerCase(s.charAt(i)) != Character.toLowerCase(s.charAt(j))) {
        pal = false;
        break;
    }
    i++;
    j--;
}
```

The `i < j` guard inside each skip loop is what stops the pointers running off
the ends of a string with no letters at all. Building a cleaned copy first is
also fine and much easier to read — it just costs O(n) space, and saying which
trade you are making is the point.
""",
    warmup=[
        _jq("Why is the two-pointer palindrome check better than reverse-and-compare?",
            ["O(1) space instead of O(n), and it exits on the first mismatch",
             "It is asymptotically faster in the worst case",
             "It handles uppercase automatically",
             "There is no difference"],
            0,
            "Both are O(n) worst case, but the two-pointer version allocates nothing and "
            "usually stops long before the end."),
        _jq("In the cleaned-palindrome loop, why does each skip loop also test `i < j`?",
            ["So a string with no letters cannot drive the pointers past each other",
             "To make it faster",
             "Because Character.isLetter can throw",
             "It is redundant"],
            0,
            "Without it, `\"...\"` would run `i` off the end and `charAt` would throw. The "
            "guard makes the skip loops safe on degenerate input."),
    ],
    exercises=[
        _je("j7-pal-two", "Palindrome, two pointers",
            "Print `true` when the line reads the same forwards and backwards "
            "(exact characters — no case folding, no skipping). Replace `____` with "
            "the comparison and what happens when it fails.",
            _jscan(
                _RD_LINE
                + "        int i = 0;\n"
                  "        int j = s.length() - 1;\n"
                  "        boolean pal = true;\n"
                  "        while (i < j) {\n"
                  "            if (s.charAt(i) != s.charAt(j)) { pal = false; break; }\n"
                  "            i++;\n"
                  "            j--;\n"
                  "        }\n"
                  "        System.out.println(pal);"),
            "if (s.charAt(i) != s.charAt(j)) { pal = false; break; }",
            [_scase(s, _jbool(s == s[::-1]))
             for s in ("racecar", "hello", "abba", "x", "ab")],
            hints=["Compare the two characters the pointers are on.",
                   "Chars compare with `!=`, not with `.equals`.",
                   "`if (s.charAt(i) != s.charAt(j)) { pal = false; break; }`"],
            difficulty="Medium"),

        _je("j7-rev-loop", "Reverse it the slow way",
            "Print the line reversed, built one character at a time. Replace `____` "
            "with the loop. (Yes, this is the O(n²) version — module 8 fixes it.)",
            _jscan(
                _RD_LINE
                + '        String out = "";\n'
                  "        for (int i = s.length() - 1; i >= 0; i--) out = out + s.charAt(i);\n"
                  "        System.out.println(out);"),
            "        for (int i = s.length() - 1; i >= 0; i--) out = out + s.charAt(i);",
            [_scase(s, s[::-1]) for s in ("hello", "abc", "x", "a b c")],
            hints=["Walk backwards: start at `s.length() - 1`, stop at `>= 0`.",
                   "`i > 0` would drop the first character.",
                   "Append each character to `out` and keep the result."]),

        _jfix("j7-pal-case", "It rejects capitals",
              "This checks whether the line is a palindrome, but says `false` for "
              "`Racecar` because `R` and `r` are different characters. Fix it so case "
              "is ignored.",
              _jscan(
                  _RD_LINE
                  + "        int i = 0;\n"
                    "        int j = s.length() - 1;\n"
                    "        boolean pal = true;\n"
                    "        while (i < j) {\n"
                    "            if (s.charAt(i) != s.charAt(j)) { pal = false; break; }\n"
                    "            i++;\n"
                    "            j--;\n"
                    "        }\n"
                    "        System.out.println(pal);"),
              _jscan(
                  _RD_LINE
                  + "        s = s.toLowerCase();\n"
                    "        int i = 0;\n"
                    "        int j = s.length() - 1;\n"
                    "        boolean pal = true;\n"
                    "        while (i < j) {\n"
                    "            if (s.charAt(i) != s.charAt(j)) { pal = false; break; }\n"
                    "            i++;\n"
                    "            j--;\n"
                    "        }\n"
                    "        System.out.println(pal);"),
              [_scase(s, _jbool(s.lower() == s.lower()[::-1]))
               for s in ("Racecar", "racecar", "Hello", "AbBa")],
              hints=["`'R'` and `'r'` are different code units.",
                     "Fold the case once, before the loop, rather than on every comparison.",
                     "`s = s.toLowerCase();` — and remember to keep the result."]),

        _jch("j7-pal-clean", "Palindrome, ignoring everything but letters", "Hard",
             "Print `true` when the line is a palindrome once you ignore case and "
             "skip every character that is not a letter. `A man, a plan, a canal: "
             "Panama` is `true`. Do it with two pointers and O(1) extra space — do "
             "not build a cleaned copy. Write the whole block where you see `____`.",
             _jscan(
                 _RD_LINE
                 + "        int i = 0;\n"
                   "        int j = s.length() - 1;\n"
                   "        boolean pal = true;\n"
                   "        while (i < j) {\n"
                   "            while (i < j && !Character.isLetter(s.charAt(i))) i++;\n"
                   "            while (i < j && !Character.isLetter(s.charAt(j))) j--;\n"
                   "            if (Character.toLowerCase(s.charAt(i)) != Character.toLowerCase(s.charAt(j))) {\n"
                   "                pal = false;\n"
                   "                break;\n"
                   "            }\n"
                   "            i++;\n"
                   "            j--;\n"
                   "        }\n"
                   "        System.out.println(pal);"),
             "        int i = 0;\n"
             "        int j = s.length() - 1;\n"
             "        boolean pal = true;\n"
             "        while (i < j) {\n"
             "            while (i < j && !Character.isLetter(s.charAt(i))) i++;\n"
             "            while (i < j && !Character.isLetter(s.charAt(j))) j--;\n"
             "            if (Character.toLowerCase(s.charAt(i)) != Character.toLowerCase(s.charAt(j))) {\n"
             "                pal = false;\n"
             "                break;\n"
             "            }\n"
             "            i++;\n"
             "            j--;\n"
             "        }\n"
             "        System.out.println(pal);",
             [_scase(s, _jbool(_clean_palindrome(s)))
              for s in ("A man, a plan, a canal: Panama", "race a car",
                        "No lemon, no melon", "abc", ".,!", "a")],
             hints=["Two skip loops inside the main loop — one advancing `i`, one retreating "
                    "`j`.",
                    "Each skip loop must also test `i < j`, or a line with no letters runs the "
                    "pointers off the ends.",
                    "Compare with `Character.toLowerCase(...)` on both sides rather than "
                    "lower-casing the whole string, so the indices still line up with the "
                    "original.",
                    "A line of pure punctuation is vacuously a palindrome — `true`."]),
    ],
    quiz=[
        _jq("Reversing a 100,000-character string with `out = out + c` in a loop does about how much work?",
            ["5 × 10⁹ character copies — quadratic",
             "100,000 copies — linear",
             "None; the compiler optimises it",
             "It throws StackOverflowError"],
            0,
            "1 + 2 + … + 100,000 ≈ n²/2. This is precisely why `StringBuilder` exists, and "
            "module 8 is about it."),
        _jq("Which palindrome check is best for a 1,000,000-character string that differs at index 1?",
            ["Two pointers — it stops after two comparisons and allocates nothing",
             "Reverse and compare with equals",
             "Sort both halves and compare",
             "They all cost the same"],
            0,
            "Reverse-and-compare must build the whole reversed string before it can compare "
            "anything. Two pointers exits immediately."),
    ],
))

# --- 7.6 Anagrams and character frequency ----------------------------------

_M7.append(_jlesson(
    "m7-anagram", "Character frequency and anagrams",
    "Module 4's counting array, indexed by letter.",
    """
```java
int[] freq = new int[26];
for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;
```

That is module 4's counting array with `c - 'a'` as the index. Everything in
this lesson is a use of it.

**Preconditions, stated once:** the input is lowercase ASCII letters. Anything
else — an uppercase letter, a space, a digit — indexes outside `0..25` and
throws, or silently corrupts a neighbouring slot. Real code lower-cases first
and skips non-letters; the drills here promise clean input so the counting is
the focus.

**The most frequent letter** is module 1's argmax over `freq`:

```java
int best = 0;
for (int v = 1; v < 26; v++) if (freq[v] > freq[best]) best = v;
char letter = (char) ('a' + best);         // index back to a character
```

`(char) ('a' + best)` is the inverse of `c - 'a'` — add the offset back and
cast, because `'a' + 1` is an `int` (2 + 2 = 4, and `char` + `int` = `int`).

**Anagram** — same letters, same counts, different order. Two standard answers:

**Sort both.** Four lines, O(n log n), and obviously correct:

```java
char[] x = s.toCharArray();
char[] y = t.toCharArray();
Arrays.sort(x);
Arrays.sort(y);
boolean anagram = Arrays.equals(x, y);
```

**Count once, un-count once.** O(n), and the one to reach for:

```java
if (s.length() != t.length()) { anagram = false; }        // check FIRST
else {
    int[] freq = new int[26];
    for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;
    for (int i = 0; i < t.length(); i++) freq[t.charAt(i) - 'a']--;
    for (int v = 0; v < 26; v++) if (freq[v] != 0) anagram = false;
}
```

**The length check is not an optimisation, it is correctness.** Without it the
second loop reads past the end of the shorter string and throws. (Even if you
looped safely, `"aab"` versus `"ab"` would leave a non-zero slot — but the
crash comes first.) Interviewers watch for this line specifically.

One counting array, incremented for one word and decremented for the other,
must end at all zeros. It is a nice trick precisely because it needs only one
array and one pass over each string.
""",
    warmup=[
        _jq("Why check `s.length() != t.length()` before the counting loops?",
            ["The un-counting loop would read past the end of the shorter string",
             "It makes it faster",
             "Because counting arrays cannot hold negatives",
             "It is unnecessary — the zero check catches it"],
            0,
            "Correctness first: the second loop is bounded by `t.length()`, and with a longer "
            "`t` it indexes a string that has already ended."),
        _jq("`(char) ('a' + 2)` is…",
            ["'c'", "99", "\"c\"", "A compile error without the cast"],
            0,
            "`'a' + 2` is the int 99; the cast turns it back into a char. Without the cast "
            "you would print 99."),
    ],
    exercises=[
        _je("j7-an-freq", "Count every letter",
            "The line is lowercase letters only. Print the 26 counts on one line, "
            "space separated, in alphabetical order. Replace `____` with the "
            "increment.",
            _jscan(
                _RD_LINE
                + "        int[] freq = new int[26];\n"
                  "        for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;\n"
                  '        for (int v = 0; v < 26; v++) System.out.print(freq[v] + " ");\n'
                  "        System.out.println();"),
            "freq[s.charAt(i) - 'a']++;",
            [_scase(s, _sp(_letter_freq(s))) for s in ("banana", "abc", "zzz", "a")],
            hints=["The slot to bump is decided by the character.",
                   "Subtract `'a'` to turn a letter into an index 0..25.",
                   "`freq[s.charAt(i) - 'a']++;`"],
            difficulty="Medium"),

        _je("j7-an-top", "The most common letter",
            "Same lowercase line. Print the letter that occurs most often — the "
            "alphabetically smallest one, if there is a tie. Replace `____` with the "
            "conversion from index back to character.",
            _jscan(
                _RD_LINE
                + "        int[] freq = new int[26];\n"
                  "        for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;\n"
                  "        int best = 0;\n"
                  "        for (int v = 1; v < 26; v++) {\n"
                  "            if (freq[v] > freq[best]) best = v;\n"
                  "        }\n"
                  "        System.out.println((char) ('a' + best));"),
            "(char) ('a' + best)",
            [_scase(s, _top_letter(s)) for s in ("banana", "abcabc", "zzz", "q")],
            hints=["Adding the offset back gives you the code unit.",
                   "But `'a' + best` is an `int`, so it needs a cast.",
                   "`(char) ('a' + best)`"],
            difficulty="Medium"),

        _je("j7-an-sort", "Anagram by sorting",
            "Read two lines of lowercase letters and print `true` when they are "
            "anagrams. Sort both as `char[]` and compare. Replace `____` with the "
            "comparison.",
            _jscan(
                _RD_2LINE
                + "        char[] x = s.toCharArray();\n"
                  "        char[] y = t.toCharArray();\n"
                  "        Arrays.sort(x);\n"
                  "        Arrays.sort(y);\n"
                  "        System.out.println(Arrays.equals(x, y));"),
            "Arrays.equals(x, y)",
            [_s2case(s, t, _jbool(_is_anagram(s, t)))
             for (s, t) in (("listen", "silent"), ("hello", "world"),
                            ("aab", "ab"), ("abc", "cba"))],
            hints=["Two arrays, compared by contents — module 1's utility method.",
                   "`x == y` would compare references, and they are different objects.",
                   "`Arrays.equals(x, y)` — and note it handles the different-length case for "
                   "free."],
            difficulty="Medium"),

        _jfix("j7-an-length", "It crashes on unequal words",
              "This checks whether two lowercase words are anagrams by counting up "
              "for the first and down for the second. It throws "
              "`StringIndexOutOfBoundsException` whenever the second word is longer. "
              "Add the check that belongs at the top.",
              _jscan(
                  _RD_2LINE
                  + "        boolean anagram = true;\n"
                    "        int[] freq = new int[26];\n"
                    "        for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;\n"
                    "        for (int i = 0; i < s.length(); i++) freq[t.charAt(i) - 'a']--;\n"
                    "        for (int v = 0; v < 26; v++) if (freq[v] != 0) anagram = false;\n"
                    "        System.out.println(anagram);"),
              _jscan(
                  _RD_2LINE
                  + "        boolean anagram = true;\n"
                    "        if (s.length() != t.length()) {\n"
                    "            anagram = false;\n"
                    "        } else {\n"
                    "            int[] freq = new int[26];\n"
                    "            for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;\n"
                    "            for (int i = 0; i < t.length(); i++) freq[t.charAt(i) - 'a']--;\n"
                    "            for (int v = 0; v < 26; v++) if (freq[v] != 0) anagram = false;\n"
                    "        }\n"
                    "        System.out.println(anagram);"),
              [_s2case(s, t, _jbool(_is_anagram(s, t)))
               for (s, t) in (("ab", "abc"), ("listen", "silent"),
                              ("aab", "ab"), ("abc", "xyz"))],
              hints=["The second loop is bounded by `s.length()` but indexes into `t`.",
                     "Words of different lengths can never be anagrams, so answer that first.",
                     "Guard the whole thing with `if (s.length() != t.length())` and only "
                     "count in the `else`."],
              difficulty="Medium"),

        _jch("j7-an-count", "Anagram in one pass each", "Hard",
             "Read two lines of lowercase letters and print `true` when they are "
             "anagrams — this time in O(n), with **one** counting array: increment "
             "for the first word, decrement for the second, and require every slot to "
             "end at zero. Check the lengths first. Write the whole block where you "
             "see `____`.",
             _jscan(
                 _RD_2LINE
                 + "        boolean anagram = true;\n"
                   "        if (s.length() != t.length()) {\n"
                   "            anagram = false;\n"
                   "        } else {\n"
                   "            int[] freq = new int[26];\n"
                   "            for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;\n"
                   "            for (int i = 0; i < t.length(); i++) freq[t.charAt(i) - 'a']--;\n"
                   "            for (int v = 0; v < 26; v++) {\n"
                   "                if (freq[v] != 0) anagram = false;\n"
                   "            }\n"
                   "        }\n"
                   "        System.out.println(anagram);"),
             "        boolean anagram = true;\n"
             "        if (s.length() != t.length()) {\n"
             "            anagram = false;\n"
             "        } else {\n"
             "            int[] freq = new int[26];\n"
             "            for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;\n"
             "            for (int i = 0; i < t.length(); i++) freq[t.charAt(i) - 'a']--;\n"
             "            for (int v = 0; v < 26; v++) {\n"
             "                if (freq[v] != 0) anagram = false;\n"
             "            }\n"
             "        }\n"
             "        System.out.println(anagram);",
             [_s2case(s, t, _jbool(_is_anagram(s, t)))
              for (s, t) in (("listen", "silent"), ("hello", "world"),
                             ("aab", "ab"), ("abc", "cba"), ("a", "a"),
                             ("aabb", "abbb"))],
             hints=["The length check comes first and short-circuits everything else.",
                    "One array, `new int[26]` — increment for `s`, decrement for `t`.",
                    "Index with `charAt(i) - 'a'` in both loops.",
                    "Afterwards every slot must be exactly 0; any non-zero slot means the "
                    "letters did not match up."]),
    ],
    quiz=[
        _jq("Sorting-based anagram check versus counting-based. What is the trade?",
            ["O(n log n) and four obvious lines, versus O(n) and a length check you must not forget",
             "The sorting version is wrong",
             "The counting version uses more memory",
             "They are identical in cost"],
            0,
            "Both are fine answers. The counting version is faster and is the one interviewers "
            "expect after you offer the sorting one."),
        _jq("Your anagram checker must handle `\"Listen\"` and `\"Silent!\"`. What changes?",
            ["Lower-case both and skip non-letters before counting",
             "Nothing — the counting array handles it",
             "Use a 52-slot array",
             "Sort instead of counting"],
            0,
            "`'L' - 'a'` is negative and `'!' - 'a'` is far out of range, so both would throw. "
            "Normalising the input is the fix."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m7_report(s):
    words = s.split(" ")
    letters, digits, _ = _classify(s)
    return _nl(
        f"chars={len(s)}",
        f"words={len(words)}",
        f"letters={letters}",
        f"digits={digits}",
        f"longest={_longest_word(words)}",
        f"top={_top_letter(s)}",
        f"joined={'-'.join(words)}",
    )


_M7_CAP = _jcap(
    "Text report",
    """
One line of text, seven facts about it — the whole module in one program.

Read a single line made of words separated by **single spaces**. The line
contains at least one lowercase letter, and may also contain digits and
punctuation. Print:

```
chars=<total characters in the line, spaces included>
words=<number of space-separated words>
letters=<how many characters are letters>
digits=<how many characters are digits>
longest=<the longest word; the FIRST one, if there is a tie>
top=<the most frequent lowercase letter; the alphabetically smallest, on a tie>
joined=<the words re-joined with hyphens>
```

Everything you need is in this module:

- `split(" ")` for `words`, `longest` and `joined`;
- `String.join("-", parts)` for `joined`;
- `Character.isLetter` / `isDigit` over `charAt` for the two counts;
- a 26-slot counting array indexed by `charAt(i) - 'a'` for `top`.

**Guard the frequency array.** The line may contain digits, punctuation and
uppercase letters, and every one of them would index outside `0..25`. Count a
character only when it is in `'a'..'z'`. Getting that guard right is the main
thing this capstone is checking.
""",
    _jch("j7-cap-report", "Text report", "Hard",
         "Write the whole report where you see `____` — seven `key=value` lines, in "
         "the order `chars`, `words`, `letters`, `digits`, `longest`, `top`, "
         "`joined`.",
         _jscan(
             _RD_LINE
             + '        String[] parts = s.split(" ");\n'
               '        System.out.println("chars=" + s.length());\n'
               '        System.out.println("words=" + parts.length);\n'
               "        int letters = 0;\n"
               "        int digits = 0;\n"
               "        int[] freq = new int[26];\n"
               "        for (int i = 0; i < s.length(); i++) {\n"
               "            char c = s.charAt(i);\n"
               "            if (Character.isLetter(c)) letters++;\n"
               "            if (Character.isDigit(c)) digits++;\n"
               "            if (c >= 'a' && c <= 'z') freq[c - 'a']++;\n"
               "        }\n"
               '        System.out.println("letters=" + letters);\n'
               '        System.out.println("digits=" + digits);\n'
               "        String longest = parts[0];\n"
               "        for (int i = 1; i < parts.length; i++) {\n"
               "            if (parts[i].length() > longest.length()) longest = parts[i];\n"
               "        }\n"
               '        System.out.println("longest=" + longest);\n'
               "        int best = 0;\n"
               "        for (int v = 1; v < 26; v++) {\n"
               "            if (freq[v] > freq[best]) best = v;\n"
               "        }\n"
               '        System.out.println("top=" + (char) (\'a\' + best));\n'
               '        System.out.println("joined=" + String.join("-", parts));'),
         '        String[] parts = s.split(" ");\n'
         '        System.out.println("chars=" + s.length());\n'
         '        System.out.println("words=" + parts.length);\n'
         "        int letters = 0;\n"
         "        int digits = 0;\n"
         "        int[] freq = new int[26];\n"
         "        for (int i = 0; i < s.length(); i++) {\n"
         "            char c = s.charAt(i);\n"
         "            if (Character.isLetter(c)) letters++;\n"
         "            if (Character.isDigit(c)) digits++;\n"
         "            if (c >= 'a' && c <= 'z') freq[c - 'a']++;\n"
         "        }\n"
         '        System.out.println("letters=" + letters);\n'
         '        System.out.println("digits=" + digits);\n'
         "        String longest = parts[0];\n"
         "        for (int i = 1; i < parts.length; i++) {\n"
         "            if (parts[i].length() > longest.length()) longest = parts[i];\n"
         "        }\n"
         '        System.out.println("longest=" + longest);\n'
         "        int best = 0;\n"
         "        for (int v = 1; v < 26; v++) {\n"
         "            if (freq[v] > freq[best]) best = v;\n"
         "        }\n"
         '        System.out.println("top=" + (char) (\'a\' + best));\n'
         '        System.out.println("joined=" + String.join("-", parts));',
         [_scase(s, _m7_report(s))
          for s in ("the quick brown fox",
                    "abc 123 def",
                    "banana",
                    "a bb ccc dd",
                    "hello world 42 times!")],
         hints=["Split once, at the top, and reuse `parts` for words, longest and joined.",
                "One character loop can do all three jobs: count letters, count digits, and "
                "fill the frequency array.",
                "Guard the frequency increment with `if (c >= 'a' && c <= 'z')` — a digit or "
                "a space would index outside the array.",
                "`longest` is module 1's argmax, comparing `parts[i].length()`; strict `>` "
                "keeps the first of a tie.",
                "`top` converts back with `(char) ('a' + best)`, and `joined` is one "
                "`String.join(\"-\", parts)` call."]),
    example_io="stdin:  the quick brown fox\n\n"
               "stdout: chars=19\n        words=4\n        letters=16\n        digits=0\n"
               "        longest=quick\n        top=o\n        joined=the-quick-brown-fox",
    rubric=[
        "`chars` counts the spaces too — it is the raw line length.",
        "The frequency array is guarded, so digits and punctuation cannot index out of range.",
        "`longest` keeps the FIRST word of a tie (strict `>`).",
        "`top` breaks ties toward the alphabetically smaller letter.",
        "`joined` has no trailing hyphen.",
        "All seven lines print, in order, with no spaces around `=`.",
    ],
)


_MODULES.append(_jmod(
    7, 2, "Strings",
    "The String API and the classic problems",
    "Learn the forty methods worth knowing, the regex trap hiding in three of them, "
    "and the four string problems that get asked by name: reversal, palindrome, "
    "character frequency, anagram.",
    """
Module 6 was the model; this is the vocabulary and the problems. The methods
divide into four groups — search, transform, split/join, and the `Character`
tests — and once you can move between `String`, `String[]` and `char[]` freely,
every array technique from Part 1 becomes available for text.

Two things to carry out of here. **`split` and `replaceAll` take regexes**, so
a dot or a pipe does not mean what you think — the most common silent
data-mangler in Java. And **`charAt(i) - 'a'`** turns a letter into an index,
which is module 4's counting array applied to text and the answer to every
frequency and anagram question.
""",
    _M7,
    capstone=_M7_CAP,
    objectives=[
        "Search with `indexOf` / `lastIndexOf` / `contains`, using `>= 0` and the `fromIndex` overload.",
        "Transform with case, `trim`, `replace` and `repeat`, always keeping the result.",
        "Say when a String method takes a regex, and escape a literal dot correctly.",
        "Move between `String`, `String[]` and `char[]` with `split`, `String.join` and `toCharArray`.",
        "Use the `Character` tests and `char` arithmetic, and know why `==` is right for chars.",
        "Check a palindrome with two pointers in O(1) space, including the clean-input variant.",
        "Build a 26-slot letter-frequency array, and check anagrams both by sorting and by counting.",
    ],
    why="These are the string questions interviews actually ask, and the regex trap in "
        "`split`/`replaceAll` is the one that quietly corrupts production data rather "
        "than throwing.",
    est_minutes=330,
    glossary=[
        _jg("indexOf", "First position of a substring or char, or -1. Test with `>= 0`, never "
                       "`> 0`."),
        _jg("fromIndex", "`indexOf(t, i)` resumes the search at `i`. How you find every "
                         "occurrence."),
        _jg("regex", "A pattern language. `split` and `replaceAll` take one; `replace` does "
                     "not. `.` `|` `*` `+` `?` `^` `$` `(` `)` `[` `]` `{` `}` are special."),
        _jg("\\\\s+", "The regex for 'one or more whitespace characters' — what you want for "
                      "word splitting, since it survives double spaces."),
        _jg("toCharArray", "A mutable `char[]` copy of the string. The bridge to every array "
                           "technique from Part 1."),
        _jg("Character", "The utility class holding `isDigit`, `isLetter`, `isWhitespace`, "
                         "`toLowerCase` and friends, as static methods on `char`."),
        _jg("char arithmetic", "`c - 'a'` gives a 0-based letter index; `(char) ('a' + i)` "
                               "converts back. `c - '0'` turns a digit character into its value."),
        _jg("palindrome", "Reads the same in both directions. Best checked with two pointers "
                          "— O(1) space and an early exit."),
        _jg("anagram", "Same letters, same counts, different order. Sort both (O(n log n)) or "
                       "count once and un-count once (O(n))."),
        _jg("isBlank", "Java 11+: empty or whitespace-only. What you usually want for input "
                       "validation, where `isEmpty` is too strict."),
    ],
    cheatsheet="""
```java
// --- search -------------------------------------------------------------
s.indexOf(t)            s.indexOf(t, from)      // -1 when absent
s.lastIndexOf(t)
s.contains(t)           // == indexOf(t) >= 0, spelled correctly
s.startsWith(p)         s.endsWith(q)
s.isEmpty()             s.isBlank()             // "   " -> false, true

int i = s.indexOf(t);                            // every occurrence
while (i >= 0) { count++; i = s.indexOf(t, i + t.length()); }

// --- transform (all return a NEW string) -------------------------------
s.toUpperCase()  s.toLowerCase()
s.trim()         s.strip()                       // strip is Java 11+
s.replace("a", "o")      // LITERAL text, all occurrences
s.replaceAll("a", "o")   // REGEX — "." means any character!
s.repeat(3)              // Java 11+

s.substring(0,1).toUpperCase() + s.substring(1).toLowerCase()   // Title case

// --- split / join / chars ----------------------------------------------
String[] p = s.split(" ");            // REGEX. Escape . | * + ? ^ $ ( ) [ ]
String[] w = s.trim().split("\\\\s+");   // words, robust to double spaces
String[] d = s.split("\\\\.");           // a literal dot
String  j  = String.join("-", p);     // separator FIRST
char[]  c  = s.toCharArray();         // then Arrays.sort(c), new String(c)

// --- characters ---------------------------------------------------------
char c = s.charAt(i);
c == 'a'                              // == is CORRECT for char
Character.isLetter(c)   Character.isDigit(c)   Character.isWhitespace(c)
Character.toLowerCase(c)
c - 'a'                               // 0..25    (char) ('a' + i)  // back
c - '0'                               // '7' -> 7

// --- palindrome, two pointers, O(1) space ------------------------------
int i = 0, j = s.length() - 1;
while (i < j) {
    if (s.charAt(i) != s.charAt(j)) { pal = false; break; }
    i++; j--;
}

// --- letter frequency / anagram ----------------------------------------
int[] freq = new int[26];
for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;

if (s.length() != t.length()) anagram = false;   // CHECK FIRST
else { for (s) freq[..]++;  for (t) freq[..]--;  all slots must be 0 }
```
""",
    self_check=[
        "Do you write `contains` rather than `indexOf(t) > 0` without having to think?",
        "Can you say which String methods take a regex, and escape a literal dot in Java source?",
        "Can you split a line into words in a way that survives double spaces?",
        "Can you explain why `s.charAt(i) == 'a'` is correct while `s == \"a\"` is not?",
        "Can you write `charAt(i) - 'a'` and its inverse without deriving them?",
        "Can you write the two-pointer palindrome check, and the punctuation-skipping version?",
        "Can you give both anagram solutions and say which line makes the counting one correct?",
    ],
    review=[
        _jq("`\"1,2,,4\".split(\",\").length` is…",
            ["4 — the empty middle piece is kept", "3", "5", "0"],
            0,
            "`split` drops *trailing* empty pieces only. An empty piece in the middle is real "
            "data and is preserved."),
        _jq("You need to replace every `$` in a template with a value. Which call?",
            ["replace(\"$\", value) — literal", "replaceAll(\"$\", value)",
             "split(\"$\") then join", "Either replace or replaceAll"],
            0,
            "`$` is the regex end-of-input anchor, so `replaceAll` would append instead of "
            "substituting. `replace` is literal and correct."),
        _jq("`int[] f = new int[26]; f[c - 'a']++;` and `c` is `' '` (a space). What happens?",
            ["ArrayIndexOutOfBoundsException — ' ' - 'a' is -65",
             "It silently counts a space as an 'a'",
             "Nothing; Java ignores negative indices",
             "It counts into slot 25"],
            0,
            "Space is code unit 32 and 'a' is 97, so the index is −65. Guard the increment or "
            "normalise the input first."),
        _jq("Which palindrome implementation uses O(1) extra space?",
            ["Two pointers comparing charAt(i) and charAt(j)",
             "Reverse with a loop and compare with equals",
             "toCharArray, sort, compare",
             "split into characters and reverse the array"],
            0,
            "The two-pointer version allocates nothing at all — just two ints — and exits on "
            "the first mismatch."),
    ],
    milestone="You can reach for the right String method without looking it up, you will "
              "never be caught by `split(\".\")` again, and you can write reversal, "
              "palindrome, frequency and anagram from memory.",
))
