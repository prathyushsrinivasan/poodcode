# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 6 practice - the object behind the text.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[6]`.
#
# Module 6 scope: creating strings, the string pool, literals vs new String,
# immutability, length()/charAt()/substring(), equals() vs ==, compareTo, and
# what `s = s + x` really costs. Newly allowed at this module: charAt,
# substring, .equals.
#
# Deliberately NOT used here (module 7 owns them): indexOf, split, String.join,
# Character.isDigit and friends, toCharArray, toUpperCase, strip, replace,
# repeat. Every character test below is written by hand with comparisons, which
# is exactly the point of this module.  StringBuilder is module 8.
# ---------------------------------------------------------------------------


def _p6ex(eid, title, difficulty, prompt, body, tests, hints, read=None):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt,
                _jscan((read if read is not None else _RD_S) + body + "\n"),
                body, tests, hints)


_RD_S = "        String s = sc.next();\n"
_RD_S2 = _RD_S + "        String t = sc.next();\n"
_RD_SK = _RD_S + "        int k = sc.nextInt();\n"
_RD_SC = _RD_S + "        char c = sc.next().charAt(0);\n"

# Test words: no spaces, since every read uses sc.next().
_WORDS = ("hello", "a", "racecar", "Java", "aabbcc")


# --- Family A - reading characters -------------------------------------------

_P6_A = _jfam(
    "p6-chars", "Reading a string one character at a time",
    "`length()` and `charAt(i)`, and nothing else.",
    """
A `String` is not an array, but it is indexed like one. Two methods carry almost
all of module 6:

```java
s.length()        // a METHOD, with parentheses  (arrays use a FIELD, a.length)
s.charAt(i)       // the char at index i, 0-based
```

**`length()` versus `length`** is a genuine irritation and a real source of
compile errors: arrays have a field `a.length`, strings have a method
`s.length()`. There is no deep reason — it is history — so the only cure is
having written both enough times.

The traversal is exactly the array traversal you already know:

```java
for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    ...
}
```

**`charAt` throws on a bad index.** `StringIndexOutOfBoundsException`, and the
valid range is `0` to `length() - 1`, same as an array.

**A `char` is a number.** `char` is a 16-bit integer type, so `c == 'a'` is an
ordinary numeric comparison and `c - 'a'` is an `int`. That is what the last
family in this module is built on.

> **Strings are immutable.** `s.charAt(0) = 'x'` does not compile — there is no
> such thing as assigning into a string. Every "change" produces a *new* string,
> which is why the last variant here builds its answer by concatenation.
""",
    [
        _p6ex("j6-pr-length", "How long is it?", "Intro",
              "Print the number of characters in the word.",
              """
        System.out.println(s.length());
""",
              [_scase(w, len(w)) for w in _WORDS],
              ["A string's length is a METHOD, not a field.",
               "Arrays use `a.length`; strings use `s.length()`.",
               "`System.out.println(s.length());`"]),

        _p6ex("j6-pr-ends", "First and last", "Intro",
              "Print the first character and the last character, separated by a space, "
              "on one line.",
              """
        System.out.println(s.charAt(0) + " " + s.charAt(s.length() - 1));
""",
              [_scase(w, f"{w[0]} {w[-1]}") for w in _WORDS],
              ["`charAt(0)` is the first character.",
               "The last index is `length() - 1`, exactly as with an array.",
               "A one-character word has the same character at both ends, which case "
               "two checks.",
               "Beware: `char + char` in Java adds their numeric codes. Putting a "
               "String between them, as the format requires, keeps it text."]),

        _p6ex("j6-pr-count-char", "Count one character", "Intro",
              "Read the word, then a single character `c`. Print how many times `c` "
              "occurs.",
              """
        int count = 0;
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) == c) {
                count++;
            }
        }
        System.out.println(count);
""",
              [_case(f"{w}\n{c}", w.count(c))
               for (w, c) in (("hello", "l"), ("a", "a"), ("racecar", "z"),
                              ("aabbcc", "b"), ("Java", "a"))],
              ["The same counting loop as module 1, over characters instead of ints.",
               "Compare chars with `==` — they are numbers, not objects.",
               "(`equals` is for Strings; a `char` is a primitive.)",
               "Case three counts a character that never appears and must print "
               "`0`.",
               "Case five is case-sensitive: `Java` has two lowercase `a`s, not "
               "three."],
              read=_RD_SC),

        _p6ex("j6-pr-alternate", "Every other character", "Easy",
              "Print the characters at indices 0, 2, 4, … with no separators, on one "
              "line.",
              """
        for (int i = 0; i < s.length(); i += 2) {
            System.out.print(s.charAt(i));
        }
        System.out.println();
""",
              [_scase(w, w[::2]) for w in _WORDS],
              ["Step the loop by two: `i += 2`.",
               "Print each character with `System.out.print`, no separator.",
               "Finish with a bare `System.out.println();` to end the line.",
               "A one-character word prints just that character."]),

        _p6ex("j6-pr-reverse", "Backwards", "Easy",
              "Print the word reversed. `StringBuilder` does not exist until module 8, "
              "so build the answer by walking backwards.",
              """
        for (int i = s.length() - 1; i >= 0; i--) {
            System.out.print(s.charAt(i));
        }
        System.out.println();
""",
              [_scase(w, w[::-1]) for w in _WORDS],
              ["Start at the last index, `length() - 1`, and count down to `0`.",
               "The loop condition is `i >= 0`, not `i > 0`, or you lose the first "
               "character.",
               "Printing as you go avoids building a string at all.",
               "Case three is a palindrome, so it comes out unchanged - a useful "
               "sanity check that you have not simply printed it forwards."]),
    ])


# --- Family B - substrings ---------------------------------------------------

_P6_B = _jfam(
    "p6-substring", "Substrings",
    "One index or two, and the second one is exclusive.",
    """
```java
s.substring(from)          // from `from` to the end
s.substring(from, to)      // from `from` up to but NOT including `to`
```

**`to` is exclusive**, exactly like `Arrays.copyOfRange` in module 1. So the
length of the result is `to - from`, and `s.substring(0, s.length())` is the
whole string. Saying "the length is `to - from`" out loud is the fastest way to
stop getting this wrong.

The legal range is wider than you might expect: `from` and `to` may both equal
`length()`, which yields an empty string. `s.substring(2, 2)` is `""`, not an
error. What throws is `from > to`, or either index outside `0..length()`.

**Every substring is a new String.** The original is untouched — it cannot be
touched, because strings are immutable. `s.substring(1)` does not shorten `s`;
it returns something new that you must assign or use.

```java
s.substring(1);            // computed and thrown away — a no-op
s = s.substring(1);        // this is what you meant
```

That mistake — calling a String method and discarding the result — is the single
most common String bug there is, and it is a direct consequence of immutability.
""",
    [
        _p6ex("j6-pr-prefix", "The first k characters", "Intro",
              "Read the word, then `k` (always between `0` and the word's length). Print "
              "the first `k` characters.",
              """
        System.out.println(s.substring(0, k));
""",
              [_case(f"{w}\n{k}", w[:k])
               for (w, k) in (("hello", 2), ("a", 1), ("racecar", 0),
                              ("Java", 4), ("aabbcc", 5))],
              ["One call: `substring(0, k)`.",
               "The second index is exclusive, so this gives exactly `k` characters.",
               "`k` of `0` yields the empty string, which prints as a blank line — "
               "case three.",
               "`k` equal to the length gives the whole word back."],
              read=_RD_SK),

        _p6ex("j6-pr-suffix", "The last k characters", "Easy",
              "Same input. Print the **last** `k` characters.",
              """
        System.out.println(s.substring(s.length() - k));
""",
              [_case(f"{w}\n{k}", w[len(w) - k:])
               for (w, k) in (("hello", 2), ("a", 1), ("racecar", 0),
                              ("Java", 4), ("aabbcc", 5))],
              ["The one-argument form runs from an index to the end.",
               "To get `k` characters from the end, start at `length() - k`.",
               "Check it: `k` equal to the length starts at `0` and gives everything.",
               "`k` of `0` starts at `length()`, which is legal and gives the empty "
               "string."],
              read=_RD_SK),

        _p6ex("j6-pr-middle", "A slice out of the middle", "Easy",
              "Read the word, then `from` and `to`. Print `s.substring(from, to)` — "
              "remember `to` is exclusive.",
              """
        System.out.println(s.substring(from, to));
""",
              [_case(f"{w}\n{fr} {to}", w[fr:to])
               for (w, fr, to) in (("hello", 1, 4), ("a", 0, 1), ("racecar", 2, 2),
                                   ("Java", 0, 4), ("aabbcc", 2, 5))],
              ["Pass both indices straight through.",
               "The result has `to - from` characters.",
               "Case three has `from == to` and yields the empty string rather than "
               "an error.",
               "Nothing you do here changes `s` — substring returns a new String."],
              read=_RD_S + "        int from = sc.nextInt();\n"
                           "        int to = sc.nextInt();\n"),

        _p6ex("j6-pr-startswith", "Does it start with that?", "Medium",
              "Read two words, `s` and `t`. Print `true` if `s` begins with `t`, "
              "`false` otherwise. `startsWith` and `indexOf` belong to module 7 — use "
              "`substring` and `equals`.",
              """
        boolean yes = false;
        if (t.length() <= s.length()) {
            yes = s.substring(0, t.length()).equals(t);
        }
        System.out.println(yes);
""",
              [_s2case(a, b, _jbool(a.startswith(b)))
               for (a, b) in (("hello", "he"), ("hello", "lo"), ("a", "a"),
                              ("Java", "Javas"), ("aabbcc", "aab"))],
              ["Take the first `t.length()` characters of `s` and compare them "
               "with `t`.",
               "The length check has to come FIRST: if `t` is longer than `s`, the "
               "substring call would throw.",
               "Compare Strings with `.equals(...)`, never `==`.",
               "Case four has a prefix longer than the word and must print `false` "
               "rather than crash."],
              read=_RD_S2),

        _p6ex("j6-pr-count-pattern", "Count the occurrences of a word", "Medium",
              "Read two words, `s` and `t` (with `t` non-empty). Print how many times "
              "`t` occurs in `s`, counting **overlapping** occurrences. Use `substring` "
              "and `equals`.",
              """
        int count = 0;
        for (int i = 0; i + t.length() <= s.length(); i++) {
            if (s.substring(i, i + t.length()).equals(t)) {
                count++;
            }
        }
        System.out.println(count);
""",
              [_s2case(a, b, sum(1 for i in range(len(a) - len(b) + 1)
                                 if a[i:i + len(b)] == b))
               for (a, b) in (("aaaa", "aa"), ("hello", "l"), ("a", "a"),
                              ("racecar", "cec"), ("aabbcc", "xy"))],
              ["Slide a window of `t.length()` characters along `s`.",
               "The loop bound is the subtle part: the last valid start is "
               "`s.length() - t.length()`, so the condition is "
               "`i + t.length() <= s.length()`.",
               "Advancing by ONE each time is what counts overlapping matches — "
               "case one is `aaaa` containing `aa` three times, not twice.",
               "Compare with `.equals`, and remember the second substring index is "
               "exclusive so `i + t.length()` is right.",
               "A pattern that never occurs gives `0`."],
              read=_RD_S2),
    ])


# --- Family C - comparing ----------------------------------------------------

def _cmp_sign(a, b):
    return -1 if a < b else (1 if a > b else 0)


_P6_C = _jfam(
    "p6-compare", "Comparing strings",
    "`equals` for value, `==` for identity, `compareTo` for order.",
    """
The single most important thing in module 6.

```java
s.equals(t)        // do they hold the same CHARACTERS?
s == t             // are they the SAME OBJECT?
```

For strings you almost always want `equals`. `==` compares references — the
question arrays already raised in module 1 — and it gives *wrong answers that
look right* because of the **string pool**.

```java
String a = "hi";
String b = "hi";
System.out.println(a == b);              // true  — both point at the pooled literal

String c = new String("hi");
System.out.println(a == c);              // FALSE — new String forces a fresh object
System.out.println(a.equals(c));         // true  — same characters
```

Java interns string *literals*: every `"hi"` in your source refers to one shared
object. So `==` on literals happens to work, which is exactly what makes the bug
so dangerous — it passes every test you write with literals and then fails on a
string that was read from input or built at run time. **Use `equals`. Always.**

`compareTo` gives you order rather than equality:

```java
a.compareTo(b)     // < 0 if a comes first, 0 if equal, > 0 if a comes after
```

It compares character by character, and on the first difference returns the
difference of the two character codes. **Do not rely on the exact number** —
only its sign is specified. It is case-sensitive and uses character codes, so
every uppercase letter sorts before every lowercase one: `"Zebra"` comes before
`"apple"`.
""",
    [
        _p6ex("j6-pr-equals", "Same characters?", "Intro",
              "Read two words. Print `true` if they hold the same characters, `false` "
              "otherwise.",
              """
        System.out.println(s.equals(t));
""",
              [_s2case(a, b, _jbool(a == b))
               for (a, b) in (("hello", "hello"), ("hello", "Hello"), ("a", "a"),
                              ("Java", "java"), ("aabbcc", "aabbc"))],
              ["Use `.equals(...)`, not `==`.",
               "`==` would ask whether they are the same object, and words read from "
               "input are not pooled — so it would print `false` even for identical "
               "text.",
               "`equals` is case-SENSITIVE: cases two and four differ only in case "
               "and are `false`."],
              read=_RD_S2),

        _p6ex("j6-pr-identity", "Pooled or not", "Medium",
              "Read one word `s`. Build `String pooled = \"hi\";` and "
              "`String fresh = new String(\"hi\");`. Print three lines: "
              "`pooled == fresh`, then `pooled.equals(fresh)`, then "
              "`s.equals(\"hi\")`.",
              """
        String pooled = "hi";
        String fresh = new String("hi");
        System.out.println(pooled == fresh);
        System.out.println(pooled.equals(fresh));
        System.out.println(s.equals("hi"));
""",
              [_scase(w, _nl("false", "true", _jbool(w == "hi")))
               for w in ("hi", "hello", "a", "HI", "hii")],
              ["The first line is `false`: `new String(...)` deliberately creates a "
               "separate object, even though the characters match.",
               "The second is `true`: `equals` compares characters.",
               "The third depends on the input, and shows the case that matters — "
               "comparing against text you did not write as a literal.",
               "Print the booleans directly; `println` renders them as `true` and "
               "`false` already.",
               "This is the whole lesson in three lines: identity and equality are "
               "different questions."]),

        _p6ex("j6-pr-compare-sign", "Which comes first?", "Easy",
              "Read two words. Print `-1` if `s` comes before `t`, `1` if it comes "
              "after, and `0` if they are equal. `compareTo` returns a character-code "
              "difference, so reduce it to its sign yourself.",
              """
        int c = s.compareTo(t);
        if (c < 0) {
            System.out.println(-1);
        } else if (c > 0) {
            System.out.println(1);
        } else {
            System.out.println(0);
        }
""",
              [_s2case(a, b, _cmp_sign(a, b))
               for (a, b) in (("apple", "banana"), ("banana", "apple"),
                              ("a", "a"), ("Zebra", "apple"), ("ab", "abc"))],
              ["`compareTo` returns a number whose SIGN is meaningful; its magnitude "
               "is not specified and varies between cases.",
               "So branch on `< 0`, `> 0` and `== 0` rather than printing the value.",
               "It is case-sensitive by character code, so every capital sorts before "
               "every lowercase letter — case four gives `-1`.",
               "When one word is a prefix of the other, the shorter one comes first: "
               "case five gives `-1`."],
              read=_RD_S2),

        _p6ex("j6-pr-first-alpha", "The earlier word", "Intro",
              "Read two words. Print whichever comes first in `compareTo` order. If "
              "they are equal, print either.",
              """
        if (s.compareTo(t) <= 0) {
            System.out.println(s);
        } else {
            System.out.println(t);
        }
""",
              [_s2case(a, b, a if a <= b else b)
               for (a, b) in (("apple", "banana"), ("banana", "apple"),
                              ("a", "a"), ("Zebra", "apple"), ("ab", "abc"))],
              ["One comparison and an `if`.",
               "`s.compareTo(t) <= 0` means `s` comes first or they are equal.",
               "Print the whole word, not the comparison result.",
               "This is the comparison step every sort in module 3 was built on, now "
               "on strings instead of ints."],
              read=_RD_S2),

        _p6ex("j6-pr-anagram", "Same letters, rearranged?", "Hard",
              "Read two words made only of lowercase letters. Print `true` if each is a "
              "rearrangement of the other, `false` otherwise. Use a counting array over "
              "the 26 letters — `toCharArray` and `Arrays.sort` on chars belong to "
              "later modules.",
              """
        boolean same = s.length() == t.length();
        if (same) {
            int[] freq = new int[26];
            for (int i = 0; i < s.length(); i++) {
                freq[s.charAt(i) - 'a']++;
            }
            for (int i = 0; i < t.length(); i++) {
                freq[t.charAt(i) - 'a']--;
            }
            for (int i = 0; i < 26; i++) {
                if (freq[i] != 0) {
                    same = false;
                }
            }
        }
        System.out.println(same);
""",
              [_s2case(a, b, _jbool(sorted(a) == sorted(b)))
               for (a, b) in (("listen", "silent"), ("hello", "world"),
                              ("a", "a"), ("aabb", "bbaa"), ("abc", "ab"))],
              ["Different lengths can never be anagrams — check that first and skip "
               "the rest.",
               "`c - 'a'` maps `'a'`..`'z'` onto `0`..`25`, because a `char` is a "
               "number.",
               "Count up for every letter of `s`, then count DOWN for every letter "
               "of `t`.",
               "If they match, every slot ends at exactly `0` — no second array "
               "needed.",
               "Case five has different lengths and must not index out of range.",
               "This is O(n); sorting both words would be O(n log n)."],
              read=_RD_S2),
    ])


# --- Family D - immutability and concatenation -------------------------------

_P6_D = _jfam(
    "p6-immutable", "Immutability and the cost of `+`",
    "Every change makes a new string.",
    """
A `String` can never be modified. Every method that looks like it changes one
actually returns a **new** string:

```java
String s = "hello";
s.substring(1);          // makes "ello" and throws it away
s = s.substring(1);      // s now refers to the new string; the old one is garbage
```

This is why `String` is `final` (module 14's reasoning, met early): if you could
subclass it and add mutable state, every method that trusts a String to be
stable would break.

**The cost.** Because strings are immutable, `s = s + x` cannot append. It
allocates a brand-new string and copies **everything** across:

```java
String out = "";
for (int i = 0; i < n; i++) {
    out = out + a[i];        // copies the whole accumulated string, every time
}
```

Iteration `i` copies `i` characters, so the total work is
`1 + 2 + 3 + … + n`, which is **O(n²)**. For a hundred items nobody notices; for
a hundred thousand the program appears to hang.

Module 8 introduces `StringBuilder`, which makes this O(n). Until then, the two
honest options are:

- **Print as you go** instead of accumulating — `System.out.print` in the loop.
  Free, and enough for most of these problems.
- **Accumulate anyway** and know what it costs. Fine at these sizes.

The variants below deliberately do it the expensive way, so that module 8's fix
lands on a problem you have actually felt.
""",
    [
        _p6ex("j6-pr-concat", "Join two words", "Intro",
              "Read two words. Print them joined with a single dash between them, like "
              "`hello-world`.",
              """
        System.out.println(s + "-" + t);
""",
              [_s2case(a, b, f"{a}-{b}")
               for (a, b) in (("hello", "world"), ("a", "b"), ("Java", "rocks"),
                              ("x", "yz"), ("aabbcc", "dd"))],
              ["`+` on strings concatenates.",
               "The dash is a string literal in double quotes, not a char in single "
               "quotes — `'-'` between two Strings would still work here, but "
               "`'a' + '-'` alone would add numbers.",
               "One `println` is enough."],
              read=_RD_S2),

        _p6ex("j6-pr-repeat", "Say it k times", "Easy",
              "Read a word, then `k`. Print the word repeated `k` times with no "
              "separator. `repeat` is a module 7 method, so build it in a loop.",
              """
        String out = "";
        for (int i = 0; i < k; i++) {
            out = out + s;
        }
        System.out.println(out);
""",
              [_case(f"{w}\n{k}", w * k)
               for (w, k) in (("ab", 3), ("a", 1), ("hi", 0), ("Java", 2),
                              ("x", 5))],
              ["Start with the empty string `\"\"` and append `k` times.",
               "`out = out + s;` — the assignment is essential, since `out + s` on "
               "its own is discarded.",
               "`k` of `0` prints an empty line, which is correct.",
               "This is the O(n^2) pattern the lesson warns about. At `k = 5` it "
               "does not matter; the point is to notice it."],
              read=_RD_SK),

        _p6ex("j6-pr-remove-char", "Drop every copy of a character", "Easy",
              "Read a word, then a character `c`. Print the word with every occurrence "
              "of `c` removed. `replace` belongs to module 7 — build the answer "
              "yourself.",
              """
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) != c) {
                System.out.print(s.charAt(i));
            }
        }
        System.out.println();
""",
              [_case(f"{w}\n{c}", w.replace(c, ""))
               for (w, c) in (("hello", "l"), ("a", "a"), ("racecar", "z"),
                              ("aabbcc", "b"), ("Java", "a"))],
              ["This is module 4's write-cursor idea, but printing instead of "
               "storing.",
               "Print only the characters that do NOT match.",
               "No accumulator is needed at all — which sidesteps the O(n^2) cost "
               "entirely.",
               "Case two removes everything and prints a blank line.",
               "Finish with a bare `System.out.println();`."],
              read=_RD_SC),

        _p6ex("j6-pr-swap-case-manual", "Flip the letter case", "Medium",
              "Read a word of letters only. Print it with every uppercase letter made "
              "lowercase and vice versa. `toUpperCase` belongs to module 7 — do the "
              "arithmetic yourself.",
              """
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch >= 'a' && ch <= 'z') {
                System.out.print((char) (ch - 'a' + 'A'));
            } else {
                System.out.print((char) (ch - 'A' + 'a'));
            }
        }
        System.out.println();
""",
              [_scase(w, w.swapcase())
               for w in ("hello", "A", "Java", "ABC", "aBcD")],
              ["A `char` is a number, so you can test ranges: `ch >= 'a' && "
               "ch <= 'z'`.",
               "To go from lowercase to uppercase, subtract `'a'` to get 0-25, then "
               "add `'A'`.",
               "The arithmetic produces an `int`, so cast back: `(char) (...)`. "
               "Without the cast you print a number.",
               "Every test word is letters only, so an `else` covering uppercase is "
               "enough."]),

        _p6ex("j6-pr-join-numbers", "Join with commas", "Medium",
              "Read `n` and then `n` integers. Print them separated by commas with no "
              "spaces, like `1,2,3`. Build the answer as a String rather than printing "
              "as you go.",
              """
        String out = "";
        for (int i = 0; i < n; i++) {
            if (i > 0) {
                out = out + ",";
            }
            out = out + a[i];
        }
        System.out.println(out);
""",
              [_acase(a, ",".join(str(x) for x in a))
               for a in ([1, 2, 3], [7], [0, 0], [-1, 2, -3], [5, 4, 3, 2, 1])],
              ["`String.join` is a module 7 method, so do it by hand.",
               "Add the comma BEFORE each element except the first, which avoids a "
               "trailing comma.",
               "`out = out + a[i];` works even though `a[i]` is an `int` — "
               "concatenation converts it for you.",
               "A single value prints with no comma at all.",
               "Note what this costs: each `+` copies the whole accumulated string. "
               "Module 8 replaces it with `StringBuilder`."],
              read=_RD_ARR),
    ])


# --- Family E - character arithmetic -----------------------------------------

_P6_E = _jfam(
    "p6-chararith", "Characters are numbers",
    "`c - 'a'`, and what it unlocks.",
    """
`char` is a 16-bit unsigned integer type holding a Unicode code point. Java lets
you use it as a number without ceremony, and three consequences do most of the
work in string problems:

**Ranges are comparisons.**

```java
if (c >= 'a' && c <= 'z')     // lowercase letter
if (c >= '0' && c <= '9')     // digit
```

`Character.isDigit` and friends arrive in module 7 and are what you should use
in real code — but knowing they are only range checks stops them being magic.

**Letters map onto 0-25 by subtraction.**

```java
int index = c - 'a';          // 'a' -> 0, 'b' -> 1, … 'z' -> 25
char back = (char) ('a' + index);
```

That is the bridge between characters and the counting arrays of module 4, and
it is how the anagram check earlier in this module worked.

**Digits convert by subtraction too.**

```java
int value = c - '0';          // '7' -> 7
```

`c - '0'` works because the digit characters are consecutive in the code table.
Writing `(int) c` instead gives you 55, the code for `'7'`, which is a classic
mistake.

> **Always cast back.** `'a' + 1` is an `int`, so `System.out.println('a' + 1)`
> prints `98`, not `b`. You need `(char) ('a' + 1)`. Arithmetic on `char`
> promotes to `int` and Java will not put it back for you.
""",
    [
        _p6ex("j6-pr-vowels", "Count the vowels", "Intro",
              "Read a lowercase word. Print how many of its characters are vowels "
              "(`a`, `e`, `i`, `o`, `u`).",
              """
        int count = 0;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') {
                count++;
            }
        }
        System.out.println(count);
""",
              [_scase(w, sum(1 for ch in w if ch in "aeiou"))
               for w in ("hello", "a", "rhythm", "aeiou", "banana")],
              ["Compare a `char` with `==` and single quotes: `ch == 'a'`.",
               "Chain the five tests with `||`.",
               "Double quotes would make it a String and the comparison would not "
               "compile.",
               "Case three has no vowels at all and prints `0`."]),

        _p6ex("j6-pr-digit-sum", "Add up the digits", "Easy",
              "Read a word made only of digit characters. Print the sum of the digits "
              "as a number.",
              """
        int sum = 0;
        for (int i = 0; i < s.length(); i++) {
            sum += s.charAt(i) - '0';
        }
        System.out.println(sum);
""",
              [_scase(w, sum(int(ch) for ch in w))
               for w in ("123", "7", "0000", "999", "10203")],
              ["`charAt(i)` gives you the CHARACTER `'7'`, whose numeric code is 55.",
               "Subtracting `'0'` converts it to the value `7`.",
               "`sum += s.charAt(i) - '0';` — the subtraction already produces an "
               "`int`.",
               "Casting with `(int) ch` instead would add character codes and give a "
               "wildly wrong total."]),

        _p6ex("j6-pr-caesar", "Shift every letter", "Medium",
              "Read a lowercase word, then `k` (between `0` and `25`). Print the word "
              "with every letter shifted `k` places forward through the alphabet, "
              "wrapping from `z` back to `a`.",
              """
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            System.out.print((char) ('a' + (ch - 'a' + k) % 26));
        }
        System.out.println();
""",
              [_case(f"{w}\n{k}",
                     "".join(chr(ord('a') + (ord(ch) - ord('a') + k) % 26) for ch in w))
               for (w, k) in (("abc", 1), ("xyz", 3), ("hello", 0),
                              ("a", 25), ("zebra", 13))],
              ["Three steps: map the letter to 0-25, add `k` and wrap with `% 26`, "
               "then map back.",
               "Map down with `ch - 'a'` and back up with `'a' + ...`.",
               "The `% 26` is what wraps `z` round to `a` — case two relies on it.",
               "Cast the result to `(char)`, or you print numbers.",
               "`k` of `0` must leave the word unchanged."],
              read=_RD_SK),

        _p6ex("j6-pr-is-palindrome-str", "Reads the same both ways", "Easy",
              "Read a word. Print `true` if it reads the same forwards and backwards, "
              "`false` otherwise. Compare characters directly — do not build a reversed "
              "copy.",
              """
        boolean same = true;
        for (int i = 0; i < s.length() / 2; i++) {
            if (s.charAt(i) != s.charAt(s.length() - 1 - i)) {
                same = false;
            }
        }
        System.out.println(same);
""",
              [_scase(w, _jbool(w == w[::-1]))
               for w in ("racecar", "a", "hello", "abba", "abca")],
              ["The same two-pointer pairing as module 4, over characters.",
               "The partner of index `i` is `length() - 1 - i`.",
               "Only the first half needs checking, so the bound is `length() / 2`.",
               "Compare chars with `!=`, not `.equals` — they are primitives.",
               "A one-character word is a palindrome and must print `true`."]),

        _p6ex("j6-pr-letter-freq", "Count every letter", "Medium",
              "Read a lowercase word. Print 26 numbers separated by single spaces — the "
              "count of `a`, then `b`, and so on through `z`.",
              """
        int[] freq = new int[26];
        for (int i = 0; i < s.length(); i++) {
            freq[s.charAt(i) - 'a']++;
        }
        for (int i = 0; i < 26; i++) {
            System.out.print(freq[i] + " ");
        }
        System.out.println();
""",
              [_scase(w, _sp([w.count(chr(ord('a') + i)) for i in range(26)]))
               for w in ("hello", "a", "aabbcc", "zzz", "banana")],
              ["This is module 4's counting array, indexed by letter instead of by "
               "value.",
               "`s.charAt(i) - 'a'` turns the character into a slot number from `0` "
               "to `25`.",
               "`new int[26]` is already all zeros.",
               "Then print all 26 slots, including the zeros for letters that never "
               "appear.",
               "One `System.out.print` per slot with a trailing space, then a bare "
               "`println()`."]),
    ])


_PRACTICE[6] = [_P6_A, _P6_B, _P6_C, _P6_D, _P6_E]
