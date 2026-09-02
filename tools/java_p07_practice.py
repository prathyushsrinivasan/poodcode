# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 7 practice - the String API and the classic problems.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[7]`.
#
# Module 7 scope: indexOf / lastIndexOf / contains / startsWith / endsWith,
# isEmpty / isBlank, toUpperCase / toLowerCase / strip / replace / repeat,
# split and String.join, Character.isDigit and friends, toCharArray, and the
# classic problems (reversal, palindrome, anagram, character frequency).
#
# StringBuilder is module 8, so anything built here is built with `+` or printed
# as it goes - which is exactly the tension module 8 then resolves.
#
# READING NOTE: word-based problems need whole lines, so they use
# `sc.nextLine()`. Anything that also needs a number reads it with
# `Integer.parseInt(sc.nextLine())` rather than `nextInt()`, because mixing
# `nextInt()` with `nextLine()` leaves the newline in the buffer and the next
# `nextLine()` returns "".
# ---------------------------------------------------------------------------


_RD_LINE = "        String s = sc.nextLine();\n"
_RD_LINE2 = _RD_LINE + "        String t = sc.nextLine();\n"
_RD_LINE_K = _RD_LINE + "        int k = Integer.parseInt(sc.nextLine());\n"


def _p7ex(eid, title, difficulty, prompt, body, tests, hints, read=None):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt,
                _jscan((read if read is not None else _RD_LINE) + body + "\n"),
                body, tests, hints)


# --- Family A - finding ------------------------------------------------------

_FIND = (("hello world", "o"), ("banana", "na"), ("abc", "z"),
         ("aaaa", "aa"), ("one", "one"))


def _count_overlap(s, t):
    return sum(1 for i in range(len(s) - len(t) + 1) if s[i:i + len(t)] == t)


def _count_nonoverlap(s, t):
    n, i = 0, 0
    while True:
        j = s.find(t, i)
        if j < 0:
            return n
        n += 1
        i = j + len(t)


_P7_A = _jfam(
    "p7-find", "Finding things inside a string",
    "`indexOf` and its three useful variations.",
    """
Module 6 made you hand-roll searching with `substring` and `equals`. The library
has done it for you all along:

```java
s.indexOf(t)              // first index of t, or -1
s.indexOf(t, from)        // first index at or after `from`, or -1
s.lastIndexOf(t)          // last index of t, or -1
s.contains(t)             // true / false — just indexOf(t) >= 0
```

**`-1` is "not found"**, the same convention as your own linear search in module
1. It is not a valid index, which is what makes it safe as a sentinel.

Both `indexOf` and `lastIndexOf` are overloaded for a `char` as well as a
`String`, so `s.indexOf('a')` and `s.indexOf("a")` both work.

**The `from` overload is what makes counting possible.** To find every
occurrence, restart the search just past the last hit:

```java
int count = 0;
int i = s.indexOf(t);
while (i >= 0) {
    count++;
    i = s.indexOf(t, i + t.length());     // skip past this match
}
```

Two very different answers hide in that line. Resuming at `i + t.length()`
counts **non-overlapping** matches; resuming at `i + 1` counts **overlapping**
ones. `"aaaa"` contains `"aa"` twice or three times depending on which you mean,
and the question rarely says — so state your assumption. The variants below ask
for each explicitly.

> `contains` takes a `CharSequence`, so `s.contains('a')` does **not** compile —
> it needs `s.contains("a")` with double quotes. It is a common and confusing
> first error.
""",
    [
        _p7ex("j7-pr-indexof", "Where does it first appear?", "Intro",
              "Read a line, then a search string on the next line. Print the index of "
              "its first occurrence, or `-1`.",
              """
        System.out.println(s.indexOf(t));
""",
              [_l2case(a, b, a.find(b)) for (a, b) in _FIND],
              ["One call does it.",
               "`indexOf` returns `-1` when there is no match, which is exactly what "
               "the brief asks for — no `if` needed.",
               "Case three searches for something absent.",
               "The whole search string must match, not just its first character."],
              read=_RD_LINE2),

        _p7ex("j7-pr-lastindexof", "And where does it last appear?", "Intro",
              "Same input. Print the index of the **last** occurrence, or `-1`.",
              """
        System.out.println(s.lastIndexOf(t));
""",
              [_l2case(a, b, a.rfind(b)) for (a, b) in _FIND],
              ["There is a matching method that scans from the right.",
               "It returns the START index of the match, not its end.",
               "It also returns `-1` when nothing matches.",
               "Case one has two `o`s, so the answers differ from the previous "
               "variant."],
              read=_RD_LINE2),

        _p7ex("j7-pr-contains", "Is it in there at all?", "Intro",
              "Same input. Print `true` if the second line occurs anywhere in the "
              "first, `false` otherwise.",
              """
        System.out.println(s.contains(t));
""",
              [_l2case(a, b, _jbool(b in a)) for (a, b) in _FIND],
              ["There is a method that answers this directly.",
               "It takes a String, so double quotes — a `char` argument will not "
               "compile.",
               "`s.indexOf(t) >= 0` would also work and is exactly what it does "
               "underneath.",
               "Print the boolean directly."],
              read=_RD_LINE2),

        _p7ex("j7-pr-count-nonoverlap", "How many, without overlapping", "Medium",
              "Same input, with a non-empty search string. Print how many "
              "**non-overlapping** occurrences there are — after each match, resume "
              "searching past its end.",
              """
        int count = 0;
        int i = s.indexOf(t);
        while (i >= 0) {
            count++;
            i = s.indexOf(t, i + t.length());
        }
        System.out.println(count);
""",
              [_l2case(a, b, _count_nonoverlap(a, b)) for (a, b) in _FIND],
              ["Find the first match, then loop while the index is not `-1`.",
               "Use the two-argument `indexOf(t, from)` to resume.",
               "Non-overlapping means resuming at `i + t.length()`, just past the "
               "match you counted.",
               "Case four is `aaaa` containing `aa`, which gives `2` under this "
               "rule.",
               "Update `i` at the bottom of the loop or it never terminates."],
              read=_RD_LINE2),

        _p7ex("j7-pr-count-overlap", "How many, counting overlaps", "Medium",
              "Same input. Print how many occurrences there are when overlapping "
              "matches **do** count — after each match, resume one character later.",
              """
        int count = 0;
        int i = s.indexOf(t);
        while (i >= 0) {
            count++;
            i = s.indexOf(t, i + 1);
        }
        System.out.println(count);
""",
              [_l2case(a, b, _count_overlap(a, b)) for (a, b) in _FIND],
              ["Identical to the previous variant except for the resume point.",
               "Resuming at `i + 1` lets the next match start inside the one you "
               "just counted.",
               "Case four is `aaaa` containing `aa`, which now gives `3`.",
               "Every other case is unchanged, which is why the difference is easy "
               "to miss in testing — always ask which one is wanted."],
              read=_RD_LINE2),
    ])


# --- Family B - testing and trimming -----------------------------------------

_TRIM = ("  padded  ", "none", "   ", "", " one two ")


_P7_B = _jfam(
    "p7-testing", "Testing and trimming",
    "The predicates, and the difference between empty and blank.",
    """
```java
s.startsWith(p)     s.endsWith(q)          // prefix / suffix, true or false
s.isEmpty()         // length() == 0 — nothing at all
s.isBlank()         // empty OR only whitespace          (Java 11+)
s.strip()           // whitespace off both ends          (Java 11+)
s.equalsIgnoreCase(t)
```

**`isEmpty` versus `isBlank` is the distinction worth holding on to.** `"   "`
is *not* empty — it has three characters — but it is blank. Almost every
real-world "did the user type anything?" check wants `isBlank`, and using
`isEmpty` there is a bug that survives testing because nobody types spaces on
purpose.

**`strip()` versus `trim()`.** `trim()` is the ancient one and removes anything
with a code below `U+0020`; `strip()` is Unicode-aware and removes anything
`Character.isWhitespace` accepts. Prefer `strip()` in new code — and remember it
**returns** a new string rather than modifying `s`, because strings are
immutable.

```java
s.strip();          // computed and discarded
s = s.strip();      // what you meant
```

**`equalsIgnoreCase` is not `toLowerCase().equals(...)`** in every locale, and it
is clearer besides. Reach for it directly.

The reading here uses `nextLine()` precisely so that leading and trailing spaces
survive — `next()` would silently eat them and the trimming variants would have
nothing to do.
""",
    [
        _p7ex("j7-pr-prefix-suffix", "Ends", "Intro",
              "Read a line, then a second line `t`. Print `s.startsWith(t)` on the "
              "first output line and `s.endsWith(t)` on the second.",
              """
        System.out.println(s.startsWith(t));
        System.out.println(s.endsWith(t));
""",
              [_l2case(a, b, _nl(_jbool(a.startswith(b)), _jbool(a.endswith(b))))
               for (a, b) in (("hello world", "hello"), ("hello world", "world"),
                              ("abc", "abc"), ("abc", "abcd"), ("banana", "na"))],
              ["Two library calls, no loops and no substring arithmetic.",
               "Neither one throws when `t` is longer than `s` — they simply return "
               "`false`. Case four checks that.",
               "A string starts with and ends with itself, so case three prints "
               "`true` twice."],
              read=_RD_LINE2),

        _p7ex("j7-pr-empty-blank", "Empty, or merely blank?", "Easy",
              "Read one line. Print its length, then `isEmpty()`, then `isBlank()` — "
              "three lines.",
              """
        System.out.println(s.length());
        System.out.println(s.isEmpty());
        System.out.println(s.isBlank());
""",
              [_lcase(w if w else " ", _nl(len(w if w else " "),
                                           _jbool(len(w if w else " ") == 0),
                                           _jbool((w if w else " ").strip() == "")))
               for w in _TRIM],
              ["Three calls, three lines, in that order.",
               "`isEmpty()` is true only for a length of zero.",
               "`isBlank()` is true for zero length OR nothing but whitespace, so "
               "the all-spaces case prints `3 false true`.",
               "That row is the whole point of the exercise: a string can be "
               "meaningfully empty without being technically empty."]),

        _p7ex("j7-pr-strip", "Trim the edges", "Intro",
              "Read one line. Print its stripped form wrapped in square brackets, like "
              "`[hello]`, so the absence of spaces is visible.",
              """
        System.out.println("[" + s.strip() + "]");
""",
              [_lcase(w if w else " ", "[" + (w if w else " ").strip() + "]")
               for w in _TRIM],
              ["`strip()` removes whitespace from BOTH ends and returns a new "
               "string.",
               "It does not touch spaces in the middle — the last case keeps the gap "
               "between its two words.",
               "Concatenate the brackets around the result.",
               "An all-whitespace line strips down to nothing and prints `[]`."]),

        _p7ex("j7-pr-ignorecase", "Same word, whatever the case", "Intro",
              "Read two lines. Print `true` if they are equal ignoring case, `false` "
              "otherwise.",
              """
        System.out.println(s.equalsIgnoreCase(t));
""",
              [_l2case(a, b, _jbool(a.lower() == b.lower()))
               for (a, b) in (("Hello", "hello"), ("Java", "JAVA"), ("abc", "abd"),
                              ("a", "A"), ("", " "))],
              ["There is a single method for this — no case conversion needed.",
               "`s.equals(t)` would be case-sensitive and wrong here.",
               "Case five compares an empty line with a space and is `false`, "
               "because ignoring case does not ignore whitespace."],
              read=_RD_LINE2),

        _p7ex("j7-pr-strip-compare", "Equal once tidied up", "Easy",
              "Read two lines. Print `true` if they are equal after stripping "
              "whitespace from both ends **and** ignoring case, `false` otherwise.",
              """
        System.out.println(s.strip().equalsIgnoreCase(t.strip()));
""",
              [_l2case(a, b, _jbool(a.strip().lower() == b.strip().lower()))
               for (a, b) in ((" Hello ", "hello"), ("Java", "  JAVA"),
                              (" abc", "abd "), (" a ", "A"), ("  ", ""))],
              ["Chain the calls: strip each side, then compare ignoring case.",
               "`s.strip()` returns a new string, so you can call `equalsIgnoreCase` "
               "straight on it.",
               "Stripping a whitespace-only line leaves the empty string, so case "
               "five is `true`.",
               "This is the normalisation almost every real form-input comparison "
               "needs."],
              read=_RD_LINE2),
    ])


# --- Family C - transforming -------------------------------------------------

_P7_C = _jfam(
    "p7-transform", "Transforming",
    "Case, replacement, repetition — all returning new strings.",
    """
```java
s.toUpperCase()   s.toLowerCase()
s.replace('a', 'b')      s.replace("ab", "xy")     // every occurrence
s.repeat(k)                                        // Java 11+
s.toCharArray()                                    // a real char[] you can edit
```

Every one of these **returns a new string**. None of them modifies `s`, because
none of them can. If a call to one of these appears on a line by itself, that
line does nothing.

**`replace` replaces every occurrence**, not just the first — unlike
`replaceFirst`. It is overloaded for `char, char` and for `String, String`, and
neither version treats its argument as a regular expression. (`replaceAll` does,
which is a separate and much sharper trap: `s.replaceAll(".", "x")` replaces
*everything*, because `.` matches any character.)

**`toCharArray` is the escape hatch.** Strings are immutable, but the `char[]`
it hands you is an ordinary array, so anything you learned in modules 1-5 works
on it:

```java
char[] c = s.toCharArray();
// swap, sort, reverse, count — all the array patterns
String back = new String(c);        // build a String from it again
```

That round trip — string to array, array work, array back to string — is the
standard way to do in-place-feeling string work before `StringBuilder` arrives
in module 8. `new String(char[])` is the constructor that closes the loop, and
it is worth remembering because `c.toString()` on a `char[]` gives you a useless
`[C@1b6d3586` instead.
""",
    [
        _p7ex("j7-pr-case", "Shout and whisper", "Intro",
              "Read one line. Print it in upper case, then in lower case.",
              """
        System.out.println(s.toUpperCase());
        System.out.println(s.toLowerCase());
""",
              [_lcase(w, _nl(w.upper(), w.lower()))
               for w in ("Hello World", "java", "ABC", "MiXeD", "a1b2")],
              ["Two calls, two lines.",
               "Neither one changes `s` — both return new strings.",
               "Digits and punctuation are left alone, which case five shows."]),

        _p7ex("j7-pr-replace", "Swap one character for another", "Intro",
              "Read a line, then a line holding exactly two characters: the one to "
              "replace and its replacement. Print the line with **every** occurrence "
              "replaced.",
              """
        System.out.println(s.replace(t.charAt(0), t.charAt(1)));
""",
              [_l2case(a, b, a.replace(b[0], b[1]))
               for (a, b) in (("hello", "lL"), ("banana", "an"), ("abc", "zz"),
                              ("aaa", "ab"), ("a b c", " -"))],
              ["The second line gives you both characters: `t.charAt(0)` and "
               "`t.charAt(1)`.",
               "`replace` takes them as `char`s and replaces every occurrence, not "
               "just the first.",
               "Case three replaces a character that is not there, leaving the line "
               "unchanged.",
               "Remember to print the RESULT — `s.replace(...)` on its own line "
               "would do nothing at all."],
              read=_RD_LINE2),

        _p7ex("j7-pr-repeat-lib", "Say it k times", "Intro",
              "Read a line, then `k` on the next line. Print the line repeated `k` "
              "times with no separator, using the library rather than a loop.",
              """
        System.out.println(s.repeat(k));
""",
              [_case(f"{w}\n{k}", w * k)
               for (w, k) in (("ab", 3), ("a", 1), ("hi", 0), ("Java", 2),
                              ("xy", 4))],
              ["Module 6 made you build this with a loop; there is a method for it.",
               "`s.repeat(k)` returns the repeated string.",
               "`k` of `0` gives the empty string and prints a blank line.",
               "Unlike the loop version this is O(total length), not O(n^2)."],
              read=_RD_LINE_K),

        _p7ex("j7-pr-reverse-chars", "Reverse via char array", "Easy",
              "Read one line. Print it reversed, by converting to a `char[]`, reversing "
              "that array with the two-pointer swap from module 4, and building a new "
              "String from it. `StringBuilder` is module 8 — do not use it.",
              """
        char[] c = s.toCharArray();
        for (int i = 0; i < c.length / 2; i++) {
            char tmp = c[i];
            c[i] = c[c.length - 1 - i];
            c[c.length - 1 - i] = tmp;
        }
        System.out.println(new String(c));
""",
              [_lcase(w, w[::-1])
               for w in ("hello", "a", "racecar", "ab cd", "Java")],
              ["`s.toCharArray()` gives an ordinary array you may modify.",
               "Note it is `c.length` — a FIELD, because this is now an array, not "
               "a string.",
               "Reverse with the module 4 two-pointer swap, stopping at "
               "`c.length / 2`.",
               "Convert back with `new String(c)`. Calling `c.toString()` instead "
               "prints something like `[C@1b6d3586`.",
               "Case three is a palindrome and comes out unchanged."]),

        _p7ex("j7-pr-title", "Capitalise each word", "Medium",
              "Read a line of lowercase words separated by single spaces. Print it with "
              "the first letter of each word in upper case. Use `split` and build the "
              "answer with `+`.",
              """
        String[] parts = s.split(" ");
        String out = "";
        for (int i = 0; i < parts.length; i++) {
            if (i > 0) {
                out = out + " ";
            }
            out = out + parts[i].substring(0, 1).toUpperCase() + parts[i].substring(1);
        }
        System.out.println(out);
""",
              [_lcase(w, " ".join(p[0].upper() + p[1:] for p in w.split(" ")))
               for w in ("hello world", "java", "one two three", "a b", "x")],
              ["`split(\" \")` gives you a `String[]` of the words.",
               "For each word, upper-case just the first character and keep the rest "
               "as-is.",
               "`substring(0, 1)` is the first character as a String — "
               "`charAt(0)` would be a `char` and `toUpperCase` is not a char "
               "method.",
               "`substring(1)` is everything after it, and is the empty string for a "
               "one-letter word, which is correct.",
               "Add the separating space before every word except the first."]),
    ])


# --- Family D - split and join -----------------------------------------------

_SENT = ("the quick brown fox", "hello", "a bb ccc dddd", "one two", "x y z")


_P7_D = _jfam(
    "p7-split", "Splitting and joining",
    "From one string to many, and back.",
    """
```java
String[] parts = s.split(" ");            // cut on every space
String back = String.join("-", parts);    // glue with a separator
```

These two are inverses, and between them they replace an enormous amount of
manual index arithmetic.

**`split` takes a regular expression**, not a plain string. That is the trap.
`split(" ")` happens to be fine because a space is not a regex metacharacter —
but `split(".")` matches *every* character and gives you an array of empty
strings, and `split("|")` behaves just as strangely. To split on a literal dot
you need `split("\\\\.")`.

**`split` drops trailing empty strings but keeps leading ones.** `"a,,b,,"`
split on `","` gives `["a", "", "b"]` — length 3, not 5. Surprising, documented,
and worth knowing before it costs you an afternoon.

**Consecutive separators produce empty strings in the middle.** Splitting
`"a  b"` (two spaces) on `" "` gives `["a", "", "b"]`. Real text-processing code
usually splits on `"\\\\s+"` for that reason. Every line in this family uses
single spaces so the simple form is correct.

`String.join` is the tidy inverse and takes any number of pieces, or an array.
It never adds a trailing separator, which is exactly the bug you keep having to
avoid when concatenating by hand.
""",
    [
        _p7ex("j7-pr-wordcount", "How many words?", "Intro",
              "Read a line of words separated by single spaces. Print how many words "
              "there are.",
              """
        String[] parts = s.split(" ");
        System.out.println(parts.length);
""",
              [_lcase(w, len(w.split(" "))) for w in _SENT],
              ["`split(\" \")` returns an array.",
               "Its size is `parts.length` — a field, since it is an array.",
               "A line with no spaces splits into a single-element array, so case "
               "two prints `1`."]),

        _p7ex("j7-pr-longest-word", "The longest word", "Easy",
              "Same input. Print the longest word. If several tie, print the first.",
              """
        String[] parts = s.split(" ");
        String best = parts[0];
        for (int i = 1; i < parts.length; i++) {
            if (parts[i].length() > best.length()) {
                best = parts[i];
            }
        }
        System.out.println(best);
""",
              [_lcase(w, max(w.split(" "), key=len)) for w in _SENT],
              ["Module 1's running maximum, over an array of strings.",
               "The thing being compared is `length()`, but the thing you KEEP is "
               "the word.",
               "Seed with `parts[0]`, never with an empty string.",
               "A strict `>` keeps the first of equal-length words.",
               "Python-style `max` does not exist here — write the loop."]),

        _p7ex("j7-pr-join", "Glue them back together", "Intro",
              "Read a line of space-separated words, then a separator on the next line. "
              "Print the words joined with that separator.",
              """
        String[] parts = s.split(" ");
        System.out.println(String.join(t, parts));
""",
              [_l2case(a, b, b.join(a.split(" ")))
               for (a, b) in (("the quick brown fox", "-"), ("hello", "-"),
                              ("a bb ccc", ", "), ("one two", ""),
                              ("x y z", "+"))],
              ["`String.join` is a STATIC method — call it on the class, not on a "
               "string.",
               "The separator comes first, then the pieces.",
               "It accepts the array directly; no loop is needed.",
               "It never appends a trailing separator, which is the bug you have to "
               "code around when concatenating by hand.",
               "An empty separator glues the words together with nothing between."],
              read=_RD_LINE2),

        _p7ex("j7-pr-reverse-words", "Words backwards", "Easy",
              "Same single-line input. Print the words in reverse order, separated by "
              "single spaces. The letters within each word stay as they are.",
              """
        String[] parts = s.split(" ");
        for (int i = parts.length - 1; i >= 0; i--) {
            System.out.print(parts[i]);
            if (i > 0) {
                System.out.print(" ");
            }
        }
        System.out.println();
""",
              [_lcase(w, " ".join(reversed(w.split(" ")))) for w in _SENT],
              ["Split, then walk the array from the last index down to `0`.",
               "The loop condition is `i >= 0`, or you drop the first word.",
               "Print a space after every word except the last, which is the one at "
               "`i == 0`.",
               "Do not reverse the characters — only the order of the words."]),

        _p7ex("j7-pr-initials", "Just the initials", "Easy",
              "Same input, all lowercase. Print the first letter of each word, in upper "
              "case, with no separator — so `the quick brown fox` gives `TQBF`.",
              """
        String[] parts = s.split(" ");
        for (int i = 0; i < parts.length; i++) {
            System.out.print(parts[i].substring(0, 1).toUpperCase());
        }
        System.out.println();
""",
              [_lcase(w, "".join(p[0].upper() for p in w.split(" "))) for w in _SENT],
              ["Split into words, then take one character from each.",
               "`substring(0, 1)` gives a String, which `toUpperCase()` accepts.",
               "`charAt(0)` would give a `char`, which has no `toUpperCase()` method "
               "— `Character.toUpperCase(c)` is the char equivalent.",
               "Print with no separator and finish with a bare `println()`."]),
    ])


# --- Family E - character classification -------------------------------------

_MIXED = ("abc123", "Hello, World!", "42", "  ", "a1!B2?")


_P7_E = _jfam(
    "p7-classify", "Classifying characters",
    "`Character.isDigit` and the rest of the family.",
    """
Module 6 made you write `c >= '0' && c <= '9'` by hand. That is what these do,
plus correct handling of the rest of Unicode:

```java
Character.isDigit(c)        Character.isLetter(c)
Character.isLetterOrDigit(c)
Character.isUpperCase(c)    Character.isLowerCase(c)
Character.isWhitespace(c)
Character.toUpperCase(c)    Character.toLowerCase(c)
```

They are **static methods on `Character`**, not methods on `char` — `c.isDigit()`
does not compile, because `char` is a primitive and primitives have no methods.
That is the same reason `int` has no `.toString()`.

**Use them instead of range checks in real code.** `c >= '0' && c <= '9'` is
correct for ASCII and wrong for the Arabic-Indic digits `٠١٢`, which
`Character.isDigit` accepts. Knowing that the range check is what the method
*replaces* is why module 6 made you write it first.

**Converting a digit character to its value is still subtraction.**
`Character.isDigit(c)` tells you whether it is a digit; it does not give you the
number. That is `c - '0'`, or `Character.getNumericValue(c)`.

The classic use is a single pass that classifies as it goes:

```java
for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (Character.isDigit(c)) digits++;
    else if (Character.isLetter(c)) letters++;
    else other++;
}
```
""",
    [
        _p7ex("j7-pr-classify", "Count the kinds", "Easy",
              "Read one line. Print three numbers on one line, space separated: how many "
              "characters are letters, how many are digits, and how many are neither.",
              """
        int letters = 0;
        int digits = 0;
        int other = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isLetter(c)) {
                letters++;
            } else if (Character.isDigit(c)) {
                digits++;
            } else {
                other++;
            }
        }
        System.out.println(letters + " " + digits + " " + other);
""",
              [_lcase(w, f"{sum(1 for c in w if c.isalpha())} "
                        f"{sum(1 for c in w if c.isdigit())} "
                        f"{sum(1 for c in w if not c.isalnum())}")
               for w in _MIXED],
              ["Three counters, one pass.",
               "`Character.isLetter` and `Character.isDigit` are static — call them "
               "on `Character`, not on the char.",
               "Chain with `else if` so each character is counted exactly once.",
               "Spaces and punctuation both fall into the third bucket."]),

        _p7ex("j7-pr-sum-digits-mixed", "Add up the digits only", "Easy",
              "Read one line that may contain anything. Print the sum of the numeric "
              "values of its digit characters. Print `0` if there are none.",
              """
        int sum = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isDigit(c)) {
                sum += c - '0';
            }
        }
        System.out.println(sum);
""",
              [_lcase(w, sum(int(c) for c in w if c.isdigit())) for w in _MIXED],
              ["Test with `Character.isDigit`, then convert with `c - '0'`.",
               "Those are two separate steps: the test does not give you the value.",
               "Adding `c` itself would add the character code — `'4'` is 52, not 4.",
               "A line with no digits leaves the accumulator at `0`."]),

        _p7ex("j7-pr-keep-letters", "Letters only", "Intro",
              "Read one line. Print it with everything that is not a letter removed.",
              """
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isLetter(c)) {
                System.out.print(c);
            }
        }
        System.out.println();
""",
              [_lcase(w, "".join(c for c in w if c.isalpha())) for w in _MIXED],
              ["Print as you go rather than accumulating — no StringBuilder until "
               "module 8, and no need for one here.",
               "One `if`, one `System.out.print(c)`.",
               "An input with no letters prints a blank line.",
               "Finish with a bare `System.out.println();`."]),

        _p7ex("j7-pr-is-numeric", "Is it a number?", "Easy",
              "Read one line. Print `true` if it is non-empty and consists **only** of "
              "digit characters, `false` otherwise.",
              """
        boolean numeric = s.length() > 0;
        for (int i = 0; i < s.length(); i++) {
            if (!Character.isDigit(s.charAt(i))) {
                numeric = false;
            }
        }
        System.out.println(numeric);
""",
              [_lcase(w if w else " ", _jbool((w if w else " ").isdigit()))
               for w in ("42", "abc123", "", "007", "1 2")],
              ["Two conditions: non-empty, AND every character a digit.",
               "Seed the flag from the length check, then knock it down on the first "
               "non-digit.",
               "The empty string must be `false` — an empty check that returns `true` "
               "is the classic bug here.",
               "A space is not a digit, so case five is `false`."]),

        _p7ex("j7-pr-palindrome-clean", "Palindrome, ignoring everything else", "Hard",
              "Read one line. Considering **only** letters and digits, and ignoring "
              "case, print `true` if it reads the same both ways and `false` otherwise. "
              "An input with no letters or digits counts as a palindrome.",
              """
        int lo = 0;
        int hi = s.length() - 1;
        boolean same = true;
        while (lo < hi) {
            if (!Character.isLetterOrDigit(s.charAt(lo))) {
                lo++;
            } else if (!Character.isLetterOrDigit(s.charAt(hi))) {
                hi--;
            } else {
                char a = Character.toLowerCase(s.charAt(lo));
                char b = Character.toLowerCase(s.charAt(hi));
                if (a != b) {
                    same = false;
                    break;
                }
                lo++;
                hi--;
            }
        }
        System.out.println(same);
""",
              [_lcase(w, _jbool((lambda t: t == t[::-1])(
                  "".join(c.lower() for c in w if c.isalnum()))))
               for w in ("A man, a plan, a canal: Panama", "race a car", "  ",
                         "ab@ba", "0P")],
              ["Two pointers walking inwards, exactly as in module 4 — but they no "
               "longer move in lockstep.",
               "Skip a non-alphanumeric character by advancing only THAT pointer, "
               "and do not compare on that iteration.",
               "Three branches: skip left, skip right, or compare and move both.",
               "Normalise case with `Character.toLowerCase` before comparing.",
               "A line with nothing to compare never enters the comparing branch and "
               "stays `true`.",
               "Case five is `0P`, whose two characters are alphanumeric but "
               "different, so `false` — a good check that you are not lower-casing a "
               "digit into a letter."]),
    ])


_PRACTICE[7] = [_P7_A, _P7_B, _P7_C, _P7_D, _P7_E]
