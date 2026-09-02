# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 8 practice - StringBuilder and StringBuffer.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[8]`.
#
# Module 8 scope: why `+=` in a loop is O(n^2), append / insert / delete /
# deleteCharAt / replace / reverse / setCharAt, capacity, StringBuffer and how
# to choose. Everything from modules 1-7 is still available.
#
# Capacity is never PRINTED by any exercise here: the growth policy
# (`2 * old + 2`) is an implementation detail rather than a specification, and
# a judged test must not depend on one.
# ---------------------------------------------------------------------------


_RD_L = "        String s = sc.nextLine();\n"
_RD_L2 = _RD_L + "        String t = sc.nextLine();\n"
_RD_LK = _RD_L + "        int k = Integer.parseInt(sc.nextLine());\n"


def _p8ex(eid, title, difficulty, prompt, body, tests, hints, read=None):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt,
                _jscan((read if read is not None else _RD_L) + body + "\n"),
                body, tests, hints)


_LINES = ("hello world", "a", "racecar", "ab cd ef", "aaabbc")


# --- Family A - building -----------------------------------------------------

_P8_A = _jfam(
    "p8-append", "Building with `append`",
    "One buffer, many appends, one `toString` at the end.",
    """
`StringBuilder` is a **mutable** character buffer. Unlike `String`, appending to
it does not copy anything — it writes into spare space it already owns, and only
grows (by reallocating) when it runs out.

```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < n; i++) {
    sb.append(a[i]);
}
System.out.println(sb.toString());        // or just println(sb)
```

**The cost difference is the whole point of this module.** Module 6 built
strings with `out = out + x`, which allocates a new string and copies everything
each time — `1 + 2 + … + n` character copies, so **O(n²)**. `append` is
**amortised O(1)**, making the loop O(n). For a hundred items you cannot tell;
for a hundred thousand, the difference is minutes versus milliseconds.

**`append` is overloaded for everything** — `int`, `char`, `double`, `boolean`,
`Object`, `char[]` — so you never convert by hand. And it **returns the builder
itself**, which is what makes chaining work:

```java
sb.append("x = ").append(42).append('\\n');
```

That return-`this` trick is the standard "fluent" pattern, and you will meet it
again all over the Java library.

**`toString()` is the exit.** `System.out.println(sb)` calls it for you, so it is
rarely written explicitly — but `sb.equals(otherSb)` does **not** compare
contents (StringBuilder does not override `equals`), so comparisons always go
through `toString()`. That is a real trap and the last family drills it.
""",
    [
        _p8ex("j8-pr-join-csv", "Comma-separated", "Intro",
              "Read `n` and then `n` integers. Print them separated by commas with no "
              "spaces, built with a `StringBuilder`.",
              """
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) {
                sb.append(",");
            }
            sb.append(a[i]);
        }
        System.out.println(sb);
""",
              [_acase(a, ",".join(str(x) for x in a))
               for a in ([1, 2, 3], [7], [0, 0], [-1, 2, -3], [5, 4, 3, 2, 1])],
              ["Create one `StringBuilder` before the loop, not inside it.",
               "`append` is overloaded for `int`, so `sb.append(a[i])` needs no "
               "conversion.",
               "Add the comma before every element except the first, which avoids a "
               "trailing comma.",
               "`System.out.println(sb)` calls `toString()` for you.",
               "This is the module 6 exercise again, now O(n) instead of O(n^2)."],
              read=_RD_ARR),

        _p8ex("j8-pr-repeat-sb", "Repeat it", "Intro",
              "Read a line, then `k`. Print the line repeated `k` times with no "
              "separator, built with a `StringBuilder`.",
              """
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < k; i++) {
            sb.append(s);
        }
        System.out.println(sb);
""",
              [_case(w + "\n" + str(k) + "\n", w * k)
               for (w, k) in (("ab", 3), ("a", 1), ("hi", 0), ("Java", 2),
                              ("xy", 4))],
              ["One builder, `k` appends.",
               "`k` of `0` leaves the builder empty and prints a blank line.",
               "`s.repeat(k)` from module 7 would also work; the point here is the "
               "loop that does not cost O(n^2).",
               "No separator, so nothing to special-case."],
              read=_RD_LK),

        _p8ex("j8-pr-alphabet", "The first k letters", "Easy",
              "Read `k` between `0` and `26` on a single line. Print the first `k` "
              "lowercase letters with no separator, built with a `StringBuilder`.",
              """
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < k; i++) {
            sb.append((char) ('a' + i));
        }
        System.out.println(sb);
""",
              [_lcase(str(k), "".join(chr(ord('a') + i) for i in range(k)))
               for k in (5, 1, 0, 26, 3)],
              ["`'a' + i` is an `int`, so cast it to `(char)` before appending.",
               "Without the cast, `append` picks the `int` overload and you get "
               "numbers.",
               "That cast is the same one module 6 needed for character arithmetic.",
               "`k` of `0` prints a blank line; `k` of `26` prints the whole "
               "alphabet."],
              read="        int k = Integer.parseInt(sc.nextLine());\n"),

        _p8ex("j8-pr-chain", "Chained appends", "Easy",
              "Read a line, then `k`. Using a **single chained statement**, append the "
              "line, then a space, then `k`, then a space, then whether `k` is greater "
              "than zero. Print the result. Expected shape: `hello 3 true`.",
              """
        StringBuilder sb = new StringBuilder();
        sb.append(s).append(" ").append(k).append(" ").append(k > 0);
        System.out.println(sb);
""",
              [_case(w + "\n" + str(k) + "\n", f"{w} {k} {str(k > 0).lower()}")
               for (w, k) in (("hello", 3), ("a", 0), ("x", -2), ("Java", 1),
                              ("ab cd", 10))],
              ["Every `append` returns the builder itself, so calls can be chained "
               "left to right.",
               "`append` is overloaded for `String`, `int` and `boolean`, so no "
               "conversion is needed anywhere.",
               "`k > 0` is a boolean expression and appends as `true` or `false`.",
               "Case two and three have `k` at or below zero and must print "
               "`false`."],
              read=_RD_LK),

        _p8ex("j8-pr-words-sep", "Join the words differently", "Easy",
              "Read a line of space-separated words, then a separator on the next line. "
              "Print the words joined with that separator, built with a "
              "`StringBuilder`.",
              """
        String[] parts = s.split(" ");
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < parts.length; i++) {
            if (i > 0) {
                sb.append(t);
            }
            sb.append(parts[i]);
        }
        System.out.println(sb);
""",
              [_l2case(a, b, b.join(a.split(" ")))
               for (a, b) in (("the quick brown fox", "-"), ("hello", "-"),
                              ("a bb ccc", ", "), ("one two", ""),
                              ("x y z", "+"))],
              ["Split into words first, exactly as in module 7.",
               "Then append the separator before every word except the first.",
               "An empty separator is legal and glues the words together — case "
               "four.",
               "`String.join` would do this in one call; writing the loop is what "
               "makes the separator logic explicit."],
              read=_RD_L2),
    ])


# --- Family B - reversing ----------------------------------------------------

_P8_B = _jfam(
    "p8-reverse", "Reversing",
    "The one-line reverse, and what to do with it.",
    """
```java
new StringBuilder(s).reverse().toString()
```

That is the whole thing. `reverse()` flips the buffer **in place** and returns
`this`, so it chains — and because the constructor accepts a `String`, the round
trip is a single expression.

Compare it with what module 6 and module 7 needed: a backwards `charAt` loop, or
`toCharArray` plus a two-pointer swap plus `new String(...)`. All three are
correct; this one is what you write in real code, and the other two are what you
write when an interviewer says "without using the library".

**`reverse()` mutates.** It does not return a reversed copy and leave the
original alone:

```java
StringBuilder sb = new StringBuilder("abc");
sb.reverse();
System.out.println(sb);        // cba — sb itself changed
```

If you need both orders, build a second builder.

**The palindrome one-liner** falls straight out:

```java
s.equals(new StringBuilder(s).reverse().toString())
```

It allocates two extra objects where the two-pointer scan allocates none, so for
a very long string the manual version is better — but for clarity this wins, and
knowing both is the point.

> `reverse()` is Unicode-aware about surrogate pairs, so it will not break an
> emoji in half. The hand-written character loop will. That is a genuine
> advantage of the library version and worth mentioning if asked.
""",
    [
        _p8ex("j8-pr-reverse-line", "Backwards", "Intro",
              "Read one line and print it reversed, using `StringBuilder`.",
              """
        System.out.println(new StringBuilder(s).reverse());
""",
              [_lcase(w, w[::-1]) for w in _LINES],
              ["The constructor takes the String directly.",
               "`reverse()` returns the builder, so it can be printed straight "
               "away.",
               "`println` calls `toString()` for you.",
               "Case three is a palindrome and comes out unchanged."]),

        _p8ex("j8-pr-palindrome-sb", "Palindrome, the short way", "Intro",
              "Read one line. Print `true` if it reads the same both ways, `false` "
              "otherwise. Use the reverse-and-compare approach.",
              """
        System.out.println(s.equals(new StringBuilder(s).reverse().toString()));
""",
              [_lcase(w, _jbool(w == w[::-1]))
               for w in ("racecar", "a", "hello", "abba", "ab ba")],
              ["Reverse it, convert back to a String, and compare.",
               "`toString()` is required here — comparing a String with a "
               "StringBuilder using `equals` is always `false`.",
               "That is because `StringBuilder` does not override `equals`, so it "
               "falls back to reference identity.",
               "Case five contains a space and is not a palindrome."]),

        _p8ex("j8-pr-reverse-each-word", "Each word backwards", "Medium",
              "Read a line of space-separated words. Print it with the letters of each "
              "word reversed but the words still in their original order.",
              """
        String[] parts = s.split(" ");
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < parts.length; i++) {
            if (i > 0) {
                sb.append(" ");
            }
            sb.append(new StringBuilder(parts[i]).reverse());
        }
        System.out.println(sb);
""",
              [_lcase(w, " ".join(p[::-1] for p in w.split(" "))) for w in _LINES],
              ["Split into words, reverse each one, and reassemble.",
               "Each word needs its OWN builder — reversing the accumulating one "
               "would undo your work.",
               "`append` accepts a `StringBuilder` directly, so no `toString()` is "
               "needed there.",
               "Keep the words in their original order and separated by single "
               "spaces."]),

        _p8ex("j8-pr-reverse-word-order", "Words backwards, letters forwards", "Easy",
              "Read a line of space-separated words. Print the words in reverse order, "
              "with the letters of each word untouched.",
              """
        String[] parts = s.split(" ");
        StringBuilder sb = new StringBuilder();
        for (int i = parts.length - 1; i >= 0; i--) {
            if (i < parts.length - 1) {
                sb.append(" ");
            }
            sb.append(parts[i]);
        }
        System.out.println(sb);
""",
              [_lcase(w, " ".join(reversed(w.split(" ")))) for w in _LINES],
              ["Walk the word array from the last index down to `0`.",
               "Do not reverse any word's characters — only their order.",
               "The separator goes before every word except the FIRST one you "
               "append, which is the one at the highest index.",
               "Compare with the previous variant: the two are easy to confuse and "
               "produce different answers for every multi-word line."]),

        _p8ex("j8-pr-reverse-range", "Reverse part of it", "Medium",
              "Read a line, then `from` and `to` on the next line separated by a space "
              "(`to` exclusive, always valid). Print the line with only that range "
              "reversed.",
              """
        StringBuilder sb = new StringBuilder(s);
        int lo = from;
        int hi = to - 1;
        while (lo < hi) {
            char tmp = sb.charAt(lo);
            sb.setCharAt(lo, sb.charAt(hi));
            sb.setCharAt(hi, tmp);
            lo++;
            hi--;
        }
        System.out.println(sb);
""",
              [_case(w + "\n" + str(fr) + " " + str(to) + "\n",
                     w[:fr] + w[fr:to][::-1] + w[to:])
               for (w, fr, to) in (("hello world", 0, 5), ("abcdef", 2, 5),
                                   ("a", 0, 1), ("abcd", 0, 4), ("abcdef", 3, 3))],
              ["`reverse()` reverses the WHOLE builder, so it cannot help here.",
               "`setCharAt` is what makes a builder mutable in place — a String has "
               "no such method.",
               "Use the module 4 two-pointer swap between `from` and `to - 1`, since "
               "`to` is exclusive.",
               "Read both indices from one line: `sc.nextLine().split(\" \")` then "
               "`Integer.parseInt`, or read them as shown.",
               "Case five has an empty range and must leave the line unchanged."],
              read=_RD_L + "        String[] fr = sc.nextLine().split(\" \");\n"
                           "        int from = Integer.parseInt(fr[0]);\n"
                           "        int to = Integer.parseInt(fr[1]);\n"),
    ])


# --- Family C - editing ------------------------------------------------------

_P8_C = _jfam(
    "p8-edit", "Editing in place",
    "insert, delete, replace, setCharAt.",
    """
These are what a builder can do that a `String` fundamentally cannot.

```java
sb.insert(i, x)          // shift everything from i right, put x in the gap
sb.deleteCharAt(i)       // remove one character
sb.delete(from, to)      // remove a range — `to` EXCLUSIVE, as always
sb.replace(from, to, x)  // delete that range and insert x in its place
sb.setCharAt(i, c)       // overwrite one character — returns void!
sb.charAt(i)             // read one, same as String
sb.length()              // same as String
```

**Two shapes of index convention live side by side here**, and mixing them up is
the main source of bugs:

- `insert(i, x)` puts `x` **before** the character currently at `i`. So
  `insert(0, x)` prepends and `insert(sb.length(), x)` appends.
- `delete(from, to)` and `replace(from, to, x)` use a half-open range, so they
  affect `to - from` characters — the same convention as `substring` and
  `copyOfRange`.

**`setCharAt` returns `void`.** Almost every other builder method returns the
builder for chaining, so `sb.setCharAt(0, 'x').append("y")` looks reasonable and
does not compile. `deleteCharAt`, `insert`, `delete`, `replace` and `append` all
return `this`; `setCharAt` is the odd one out.

**`replace` here is not `String.replace`.** `String.replace` swaps every
occurrence of a *value*; `StringBuilder.replace` swaps a *range of positions*.
Same name, unrelated jobs.
""",
    [
        _p8ex("j8-pr-insert", "Put something in the middle", "Intro",
              "Read a line, then `k` on the next line (a valid index). Print the line "
              "with a `*` inserted so that it appears at index `k`.",
              """
        StringBuilder sb = new StringBuilder(s);
        sb.insert(k, "*");
        System.out.println(sb);
""",
              [_case(w + "\n" + str(k) + "\n", w[:k] + "*" + w[k:])
               for (w, k) in (("hello", 2), ("abc", 0), ("abc", 3), ("a", 1),
                              ("ab cd", 2))],
              ["`insert` takes the index first, then what to insert.",
               "It puts the new text BEFORE the character currently at that index.",
               "`k` of `0` prepends; `k` equal to the length appends.",
               "Build the builder from `s` via its constructor."],
              read=_RD_LK),

        _p8ex("j8-pr-delete-at", "Drop one character", "Intro",
              "Read a line, then a valid index `k`. Print the line with the character at "
              "index `k` removed.",
              """
        StringBuilder sb = new StringBuilder(s);
        sb.deleteCharAt(k);
        System.out.println(sb);
""",
              [_case(w + "\n" + str(k) + "\n", w[:k] + w[k + 1:])
               for (w, k) in (("hello", 0), ("hello", 4), ("abc", 1), ("a", 0),
                              ("ab cd", 2))],
              ["`deleteCharAt` takes a single index.",
               "The valid range is `0` to `length() - 1`, like `charAt`.",
               "Removing the only character of a one-character line leaves an empty "
               "builder, which prints a blank line.",
               "Everything after the gap shifts left by one."],
              read=_RD_LK),

        _p8ex("j8-pr-delete-range", "Cut out a range", "Easy",
              "Read a line, then `from` and `to` on the next line separated by a space "
              "(`to` exclusive, always valid). Print the line with that range removed.",
              """
        StringBuilder sb = new StringBuilder(s);
        sb.delete(from, to);
        System.out.println(sb);
""",
              [_case(w + "\n" + str(fr) + " " + str(to) + "\n", w[:fr] + w[to:])
               for (w, fr, to) in (("hello world", 5, 11), ("abcdef", 1, 3),
                                   ("a", 0, 1), ("abcd", 0, 0), ("abcdef", 0, 6))],
              ["`delete` takes a half-open range: `to` is NOT removed.",
               "So it removes `to - from` characters.",
               "An empty range (`from == to`) removes nothing — case four.",
               "Deleting the whole range leaves an empty builder and a blank line."],
              read=_RD_L + "        String[] fr = sc.nextLine().split(\" \");\n"
                           "        int from = Integer.parseInt(fr[0]);\n"
                           "        int to = Integer.parseInt(fr[1]);\n"),

        _p8ex("j8-pr-replace-range", "Swap a range for something else", "Easy",
              "Read a line, then a replacement string on the second line, then `from` "
              "and `to` on the third (space separated, `to` exclusive, always valid). "
              "Print the line with that range replaced by the replacement.",
              """
        StringBuilder sb = new StringBuilder(s);
        sb.replace(from, to, t);
        System.out.println(sb);
""",
              [_case(w + "\n" + rep + "\n" + str(fr) + " " + str(to) + "\n",
                     w[:fr] + rep + w[to:])
               for (w, rep, fr, to) in (("hello world", "there", 6, 11),
                                        ("abcdef", "X", 1, 3),
                                        ("abc", "", 0, 1),
                                        ("abcd", "ZZZZ", 0, 4),
                                        ("ab cd", "-", 2, 3))],
              ["`StringBuilder.replace` works on POSITIONS, not on a value to match "
               "— it is unrelated to `String.replace`.",
               "The signature is `replace(from, to, String)`.",
               "The replacement need not be the same length as the range it "
               "replaces.",
               "An empty replacement makes it behave exactly like `delete` — case "
               "three."],
              read=_RD_L2 + "        String[] fr = sc.nextLine().split(\" \");\n"
                            "        int from = Integer.parseInt(fr[0]);\n"
                            "        int to = Integer.parseInt(fr[1]);\n"),

        _p8ex("j8-pr-setchar", "Overwrite one character", "Easy",
              "Read a line, then a valid index `k`. Print the line with the character at "
              "index `k` replaced by `#`.",
              """
        StringBuilder sb = new StringBuilder(s);
        sb.setCharAt(k, '#');
        System.out.println(sb);
""",
              [_case(w + "\n" + str(k) + "\n", w[:k] + "#" + w[k + 1:])
               for (w, k) in (("hello", 0), ("hello", 4), ("abc", 1), ("a", 0),
                              ("ab cd", 2))],
              ["`setCharAt` overwrites rather than inserting, so the length does not "
               "change.",
               "It takes a `char`, so single quotes: `'#'`, not `\"#\"`.",
               "It returns `void` — you cannot chain anything onto it.",
               "That makes it the one builder method that breaks the fluent "
               "pattern."],
              read=_RD_LK),
    ])


# --- Family D - classic transformations --------------------------------------

def _rle(s):
    out = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(s[i] + str(j - i))
        i = j
    return "".join(out)


def _dedupe_adjacent(s):
    out = []
    for ch in s:
        if not out or out[-1] != ch:
            out.append(ch)
    return "".join(out)


def _squeeze_spaces(s):
    out = []
    for ch in s:
        if ch == " " and out and out[-1] == " ":
            continue
        out.append(ch)
    return "".join(out)


def _interleave(a, b):
    out = []
    for i in range(max(len(a), len(b))):
        if i < len(a):
            out.append(a[i])
        if i < len(b):
            out.append(b[i])
    return "".join(out)


_P8_D = _jfam(
    "p8-transform", "The classic transformations",
    "Where a builder actually earns its keep.",
    """
These are the problems `StringBuilder` was made for: the output is built one
character at a time, its final length is not known in advance, and the input may
be long.

The shape is always the same — walk the input, append what survives:

```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (...) sb.append(c);
}
System.out.println(sb);
```

which is module 4's **write-cursor** pattern with the builder playing the part
of the output array — and, unlike an array, it does not need its length decided
up front.

Two of the variants below need to look at a **run** of equal characters. The
standard way, without helper methods, is an inner scan that advances a second
index and then jumps the outer one:

```java
int i = 0;
while (i < s.length()) {
    int j = i;
    while (j < s.length() && s.charAt(j) == s.charAt(i)) j++;
    // s[i..j-1] is a run of (j - i) identical characters
    i = j;                        // jump, do not i++
}
```

**Advancing `i` to `j` rather than incrementing it** is what keeps this O(n).
Forgetting it is an infinite loop, which is worth meeting deliberately once.
""",
    [
        _p8ex("j8-pr-remove-vowels", "Drop the vowels", "Intro",
              "Read one line. Print it with every lowercase vowel (`a e i o u`) "
              "removed.",
              """
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c != 'a' && c != 'e' && c != 'i' && c != 'o' && c != 'u') {
                sb.append(c);
            }
        }
        System.out.println(sb);
""",
              [_lcase(w, "".join(c for c in w if c not in "aeiou")) for w in _LINES],
              ["Walk the line, append only what survives.",
               "Five `&&` tests, or a single `\"aeiou\".indexOf(c) < 0` using module "
               "7's method.",
               "Uppercase vowels are not mentioned, so leave them alone.",
               "A line that is all vowels prints blank."]),

        _p8ex("j8-pr-dedupe-adjacent", "Collapse repeats", "Easy",
              "Read one line. Print it with every run of identical adjacent characters "
              "reduced to a single character — `aaabbc` becomes `abc`.",
              """
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (sb.length() == 0 || sb.charAt(sb.length() - 1) != c) {
                sb.append(c);
            }
        }
        System.out.println(sb);
""",
              [_lcase(w, _dedupe_adjacent(w)) for w in _LINES],
              ["Compare each character with the last one you KEPT, not with its "
               "neighbour in the input.",
               "The last kept character is `sb.charAt(sb.length() - 1)`.",
               "Guard with `sb.length() == 0` first, or that call throws on the "
               "first character. `||` short-circuits, so the order matters.",
               "This is module 4's sorted-dedupe, adapted to adjacency rather than "
               "sortedness."]),

        _p8ex("j8-pr-squeeze-spaces", "One space is enough", "Easy",
              "Read one line. Print it with every run of consecutive spaces reduced to a "
              "single space. Leading and trailing spaces are kept (reduced to one if "
              "there were several).",
              """
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == ' ' && sb.length() > 0 && sb.charAt(sb.length() - 1) == ' ') {
                continue;
            }
            sb.append(c);
        }
        System.out.println(sb);
""",
              [_lcase(w, _squeeze_spaces(w))
               for w in ("a  b", "hello   world", "a", "  x  y  ", "no doubles")],
              ["Only spaces collapse — every other character is appended "
               "unconditionally.",
               "Skip a space when the last kept character is also a space.",
               "The `sb.length() > 0` guard must come before the `charAt`, and `&&` "
               "short-circuits so it does.",
               "Case four begins and ends with two spaces, which each become one.",
               "`split(\"\\\\s+\")` plus `join` is another route, but it drops the "
               "leading and trailing spaces the brief asks you to keep."]),

        _p8ex("j8-pr-rle", "Run-length encode", "Medium",
              "Read one line. Print each run of identical characters as the character "
              "followed by the length of the run — so `aaabbc` becomes `a3b2c1`. Every "
              "run gets a count, even a run of one.",
              """
        StringBuilder sb = new StringBuilder();
        int i = 0;
        while (i < s.length()) {
            int j = i;
            while (j < s.length() && s.charAt(j) == s.charAt(i)) {
                j++;
            }
            sb.append(s.charAt(i)).append(j - i);
            i = j;
        }
        System.out.println(sb);
""",
              [_lcase(w, _rle(w)) for w in _LINES],
              ["Use two indices: `i` at the start of the run, `j` scanning forward "
               "while the character stays the same.",
               "The run length is `j - i`.",
               "Append the character and then the count — `append` handles the `int` "
               "for you.",
               "Then jump: `i = j;`. Writing `i++` instead is an infinite loop.",
               "The bounds check `j < s.length()` must come before the `charAt`, or "
               "the last run throws.",
               "Runs of one still get a `1`, so `abc` becomes `a1b1c1`."]),

        _p8ex("j8-pr-interleave", "Zip two lines together", "Medium",
              "Read two lines. Print their characters alternately, starting with the "
              "first line's. When one runs out, append the rest of the other.",
              """
        StringBuilder sb = new StringBuilder();
        int len = s.length();
        if (t.length() > len) {
            len = t.length();
        }
        for (int i = 0; i < len; i++) {
            if (i < s.length()) {
                sb.append(s.charAt(i));
            }
            if (i < t.length()) {
                sb.append(t.charAt(i));
            }
        }
        System.out.println(sb);
""",
              [_l2case(a, b, _interleave(a, b))
               for (a, b) in (("abc", "xyz"), ("ab", "wxyz"), ("abcd", "xy"),
                              ("a", ""), ("", "b"))],
              ["Loop up to the LONGER of the two lengths.",
               "Guard each append with its own bounds check, so the shorter line "
               "simply stops contributing.",
               "That handles the leftover tail automatically — no second loop "
               "needed.",
               "Cases four and five have an empty line, which contributes nothing "
               "at all.",
               "`Math.max` would tidy the length calculation; the explicit `if` "
               "keeps it obvious."],
              read=_RD_L2),
    ])


# --- Family E - cost and choice ----------------------------------------------

_P8_E = _jfam(
    "p8-choose", "Cost, and choosing the right one",
    "`String` vs `StringBuilder` vs `StringBuffer`.",
    """
## The three of them

| | Mutable | Thread-safe | Use it when |
|---|---|---|---|
| `String` | no | yes (trivially — it cannot change) | the value is fixed |
| `StringBuilder` | yes | **no** | building a string, single-threaded |
| `StringBuffer` | yes | yes (every method `synchronized`) | building one shared across threads |

`StringBuilder` and `StringBuffer` have the **same API**, method for method.
`StringBuffer` came first; `StringBuilder` was added in Java 5 as the
unsynchronised — and therefore faster — version.

**The default is `StringBuilder`.** A buffer being built inside one method is
never shared across threads, so paying for locking gains nothing. `StringBuffer`
is the one you reach for deliberately, and rarely.

## What `+` really compiles to

A single `a + b + c` is *not* slow — the compiler turns it into one
`StringBuilder` behind the scenes. What is slow is `+` **in a loop**, because
each iteration creates a fresh builder, copies everything in, and throws it
away:

```java
for (...) out = out + x;    // a NEW builder per iteration: O(n^2)
for (...) sb.append(x);     // one builder, reused: O(n)
```

So "never concatenate" is the wrong lesson. The right one is: **never
concatenate in a loop.**

## The `equals` trap

```java
StringBuilder a = new StringBuilder("hi");
StringBuilder b = new StringBuilder("hi");
a.equals(b);                          // FALSE — no equals override
a.toString().equals(b.toString());    // true
```

`StringBuilder` does not override `equals`, so it inherits `Object`'s reference
comparison. Always compare through `toString()`. It is module 13's
`equals`/`hashCode` lesson arriving early, as a real bug.
""",
    [
        _p8ex("j8-pr-equals-trap", "Comparing builders", "Medium",
              "Read one line. Build two separate `StringBuilder`s from it. Print "
              "`a.equals(b)` on the first line and `a.toString().equals(b.toString())` "
              "on the second.",
              """
        StringBuilder a = new StringBuilder(s);
        StringBuilder b = new StringBuilder(s);
        System.out.println(a.equals(b));
        System.out.println(a.toString().equals(b.toString()));
""",
              [_lcase(w, _nl("false", "true")) for w in _LINES],
              ["The first line is always `false`, whatever the input.",
               "`StringBuilder` does not override `equals`, so it compares "
               "references — and these are two separate objects.",
               "The second line is always `true`, because `String` DOES override "
               "`equals`.",
               "This is the same identity-versus-value distinction as `==` on "
               "Strings in module 6, one level further in.",
               "Always compare builders through `toString()`."]),

        _p8ex("j8-pr-buffer", "The synchronised twin", "Intro",
              "Read a line, then `k`. Using a **`StringBuffer`** rather than a "
              "`StringBuilder`, append the line `k` times and print the result. The API "
              "is identical.",
              """
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < k; i++) {
            sb.append(s);
        }
        System.out.println(sb);
""",
              [_case(w + "\n" + str(k) + "\n", w * k)
               for (w, k) in (("ab", 3), ("a", 1), ("hi", 0), ("Java", 2),
                              ("xy", 4))],
              ["Change the type; change nothing else.",
               "`StringBuffer` has exactly the same methods as `StringBuilder`.",
               "The only difference is that each is `synchronized`, which costs "
               "time and buys thread safety you do not need here.",
               "That is the point of the exercise: knowing they are "
               "interchangeable, and that `StringBuilder` is the right default."],
              read=_RD_LK),

        _p8ex("j8-pr-build-long", "Build a long one", "Easy",
              "Read `k` (up to 200000) on a single line. Append the character `x` to a "
              "`StringBuilder` `k` times, then print the builder's length. Do not build "
              "it with `+`.",
              """
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < k; i++) {
            sb.append('x');
        }
        System.out.println(sb.length());
""",
              [_lcase(str(k), k) for k in (5, 0, 1, 100000, 200000)],
              ["One builder, `k` appends, then `length()`.",
               "Print the LENGTH, not the builder — nobody wants 200000 x's on "
               "screen.",
               "`sb.length()` is a method here, like `String.length()`.",
               "Try the same loop with `out = out + \"x\"` and a `k` of 200000 some "
               "time: it takes minutes rather than milliseconds. That gap is the "
               "entire reason this class exists."],
              read="        int k = Integer.parseInt(sc.nextLine());\n"),

        _p8ex("j8-pr-group", "Insert a separator every k characters", "Medium",
              "Read a line, then `k` (at least 1). Print the line with a `-` inserted "
              "after every `k` characters, but not at the very end. So `abcdef` with "
              "`k = 2` gives `ab-cd-ef`.",
              """
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            if (i > 0 && i % k == 0) {
                sb.append('-');
            }
            sb.append(s.charAt(i));
        }
        System.out.println(sb);
""",
              [_case(w + "\n" + str(k) + "\n",
                     "-".join(w[i:i + k] for i in range(0, len(w), k)) if w else "")
               for (w, k) in (("abcdef", 2), ("abcde", 2), ("abc", 1),
                              ("abc", 5), ("a", 1))],
              ["Add the separator BEFORE a character rather than after one — that "
               "is what stops a trailing dash.",
               "The condition is `i > 0 && i % k == 0`: a boundary, but not the "
               "start.",
               "Case two has a leftover group of one at the end, which is fine.",
               "A `k` larger than the line produces no separators at all.",
               "Inserting after and then deleting the last character also works, but "
               "the `i > 0` guard is cleaner."],
              read=_RD_LK),

        _p8ex("j8-pr-rle-decode", "Decode a run-length encoding", "Hard",
              "Read a line in the form produced by the encoder — a character followed by "
              "a count, repeated, like `a3b12c1`. Counts may have more than one digit. "
              "Print the expanded line.",
              """
        StringBuilder sb = new StringBuilder();
        int i = 0;
        while (i < s.length()) {
            char c = s.charAt(i);
            i++;
            int count = 0;
            while (i < s.length() && Character.isDigit(s.charAt(i))) {
                count = count * 10 + (s.charAt(i) - '0');
                i++;
            }
            for (int j = 0; j < count; j++) {
                sb.append(c);
            }
        }
        System.out.println(sb);
""",
              [_lcase(enc, "".join(ch * int(num) for (ch, num) in pairs))
               for (enc, pairs) in ((("a3b2c1"), [("a", "3"), ("b", "2"), ("c", "1")]),
                                    (("x1"), [("x", "1")]),
                                    (("a12"), [("a", "12")]),
                                    (("a1b1c1"), [("a", "1"), ("b", "1"), ("c", "1")]),
                                    (("z2y10"), [("z", "2"), ("y", "10")]))],
              ["Take one character, then read every digit that follows it.",
               "Multi-digit counts mean you must accumulate: "
               "`count = count * 10 + (digit)`.",
               "That is the standard hand-rolled `parseInt`, and `c - '0'` converts "
               "each digit.",
               "The digit loop needs `i < s.length()` before the `charAt`, for the "
               "count that ends the line.",
               "Then append the character `count` times.",
               "Case three is `a12` — twelve `a`s, not one `a` then two of "
               "something."]),
    ])


_PRACTICE[8] = [_P8_A, _P8_B, _P8_C, _P8_D, _P8_E]
