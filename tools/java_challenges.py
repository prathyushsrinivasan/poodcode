# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Java Learn track — coding challenges.
#
# Java shipped ~134 fill-in-the-blank drills but no `kind="challenge"`
# exercises, so the Java tab lacked the "now put it together" step the
# TypeScript tab has (see typescript_expand.py). This file adds ONE
# self-contained coding challenge to EVERY Java concept, so each chapter pairs
# its short drills with a full little problem.
#
# exec()'d inside gen_seed.py's namespace AFTER java_core_drills.py, so it
# reuses ex(), prog() and _cls(). Each challenge is a complete stdin/stdout
# Java program graded by the SAME exact judge as the drills, scoped to what the
# syllabus has taught up to that point, and tagged Intro -> Easy -> Medium as
# the track progresses.
#
# Every `solution` here is proven end-to-end by tests/verify_exercises.rs,
# which compiles and runs it through the real judge.
# ---------------------------------------------------------------------------

import textwrap as _tw


def _b(src):
    """Indent a dedented main-body snippet to prog()'s 8-space level."""
    src = _tw.dedent(src).strip("\n")
    return "\n".join(("        " + ln) if ln.strip() else "" for ln in src.split("\n"))


def _chal(key, eid, title, diff, prompt, body, tests, hint=""):
    """A challenge whose starter is the Scanner scaffold plus one `____` where
    the learner writes the whole solution."""
    blank = _b(body)
    EXERCISES.setdefault(key, []).append(
        ex(eid, title, prompt, prog(blank), [blank], tests,
           hint=hint, kind="challenge", difficulty=diff)
    )


def _chal_cls(key, eid, title, diff, prompt, members, blank, tests, hint=""):
    """A challenge that needs class-level members (a helper method, a nested
    node class). `members` is the full class body already at its final 4-space
    indentation; `blank` is the fragment of it the learner writes, quoted
    verbatim from `members` so it matches exactly."""
    full = _cls(members.strip("\n"))
    EXERCISES.setdefault(key, []).append(
        ex(eid, title, prompt, full, [blank.strip("\n")], tests,
           hint=hint, kind="challenge", difficulty=diff)
    )


# ===========================================================================
# Foundations
# ===========================================================================

_chal("variables", "variables-challenge", "Rectangle report", "Intro",
      "The input is two integers `w h` — a rectangle's width and height. Print three lines: its area, its perimeter (`2 * (w + h)`), and whether it is a square (`true`/`false`).",
      """
      int w = sc.nextInt();
      int h = sc.nextInt();
      int area = w * h;
      int perimeter = 2 * (w + h);
      boolean square = w == h;
      System.out.println(area);
      System.out.println(perimeter);
      System.out.println(square);
      """,
      [("3 4", "12\n14\nfalse"), ("5 5", "25\n20\ntrue"),
       ("1 10", "10\n22\nfalse"), ("7 7", "49\n28\ntrue")],
      hint="Store each answer in its own well-named variable, then print them in order. A boolean prints as true or false.")

_chal("io_basics", "io_basics-challenge", "Profile card", "Intro",
      "The input is one line: a name, an age, and a city separated by spaces (`ada 36 london`). Read all three and print them on three lines, each labelled — `Name: ada`, `Age: 36`, `City: london`.",
      """
      String name = sc.next();
      int age = sc.nextInt();
      String city = sc.next();
      System.out.println("Name: " + name);
      System.out.println("Age: " + age);
      System.out.println("City: " + city);
      """,
      [("ada 36 london", "Name: ada\nAge: 36\nCity: london"),
       ("linus 54 helsinki", "Name: linus\nAge: 54\nCity: helsinki"),
       ("grace 85 arlington", "Name: grace\nAge: 85\nCity: arlington")],
      hint="sc.next() reads one word, sc.nextInt() reads one number. Build each line with + string concatenation.")

_chal("arithmetic", "arithmetic-challenge", "Split the bill", "Intro",
      "The input is `cents people` — a bill in cents and how many people are splitting it. Print four lines: the whole dollars in the bill (`cents / 100`), the leftover cents (`cents % 100`), each person's share in cents (`cents / people`, rounded down), and the cents left over after the split (`cents % people`).",
      """
      int cents = sc.nextInt();
      int people = sc.nextInt();
      System.out.println(cents / 100);
      System.out.println(cents % 100);
      System.out.println(cents / people);
      System.out.println(cents % people);
      """,
      [("1234 5", "12\n34\n246\n4"), ("500 2", "5\n0\n250\n0"),
       ("99 4", "0\n99\n24\n3"), ("10000 3", "100\n0\n3333\n1")],
      hint="Integer division / throws away the remainder; % gives you exactly that remainder back.")

_chal("conditionals", "conditionals-challenge", "Letter grade", "Intro",
      "The input is one integer score from 0 to 100. Print the letter grade: `A` for 90 and above, `B` for 80–89, `C` for 70–79, `D` for 60–69, otherwise `F`.",
      """
      int score = sc.nextInt();
      if (score >= 90) {
          System.out.println("A");
      } else if (score >= 80) {
          System.out.println("B");
      } else if (score >= 70) {
          System.out.println("C");
      } else if (score >= 60) {
          System.out.println("D");
      } else {
          System.out.println("F");
      }
      """,
      [("95", "A"), ("90", "A"), ("80", "B"), ("72", "C"),
       ("60", "D"), ("59", "F"), ("0", "F"), ("100", "A")],
      hint="Test from the highest band down. Once you reach an else-if, everything above it was already false, so you only need the lower bound.")

_chal("loops_basic", "loops_basic-challenge", "Countdown and total", "Intro",
      "The input is one integer `n`. Print the numbers from `n` down to 1 on one line, separated by single spaces, then print their sum on the next line.",
      """
      int n = sc.nextInt();
      StringBuilder sb = new StringBuilder();
      long sum = 0;
      for (int i = n; i >= 1; i--) {
          sb.append(i);
          if (i > 1) sb.append(' ');
          sum += i;
      }
      System.out.println(sb.toString());
      System.out.println(sum);
      """,
      [("5", "5 4 3 2 1\n15"), ("1", "1\n1"),
       ("3", "3 2 1\n6"), ("10", "10 9 8 7 6 5 4 3 2 1\n55")],
      hint="A countdown loop starts at n and uses i-- with the condition i >= 1. Append a space only when another number follows.")

_chal("boolean_logic", "boolean_logic-challenge", "Leap year", "Intro",
      "The input is one year. Print `true`/`false` for whether it is a leap year — divisible by 4, EXCEPT that years divisible by 100 are not leap years, UNLESS they are also divisible by 400. On the second line print whether the year is a century year (divisible by 100).",
      """
      int y = sc.nextInt();
      boolean leap = (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
      boolean century = y % 100 == 0;
      System.out.println(leap);
      System.out.println(century);
      """,
      [("2000", "true\ntrue"), ("1900", "false\ntrue"),
       ("2024", "true\nfalse"), ("2023", "false\nfalse"), ("2400", "true\ntrue")],
      hint="&& binds tighter than ||, so (div by 4 AND not div by 100) OR (div by 400) reads exactly like the rule.")

_chal("bit_manip", "bit_manip-challenge", "Bit report", "Easy",
      "The input is one non-negative integer `n`. Print three lines: how many 1-bits `n` has, whether `n` is a power of two (`true`/`false` — 0 is not), and the value of `n` with its lowest set bit cleared (`n & (n - 1)`).",
      """
      int n = sc.nextInt();
      int bits = 0;
      for (int i = 0; i < 32; i++) {
          if (((n >> i) & 1) == 1) bits++;
      }
      System.out.println(bits);
      System.out.println(n > 0 && (n & (n - 1)) == 0);
      System.out.println(n & (n - 1));
      """,
      [("12", "2\nfalse\n8"), ("16", "1\ntrue\n0"),
       ("7", "3\nfalse\n6"), ("1", "1\ntrue\n0"), ("0", "0\nfalse\n0")],
      hint="(n >> i) & 1 isolates bit i. n & (n - 1) always clears exactly the lowest set bit — so it is 0 precisely when n had one bit.")

_chal("overflow", "overflow-challenge", "Sums that outgrow int", "Easy",
      "The input is one integer `n` up to 2,000,000. Print the sum `1 + 2 + ... + n` using the closed form `n * (n + 1) / 2`, then print `n * n`. Both answers overflow a 32-bit `int` for large `n` — use `long` throughout.",
      """
      long n = sc.nextLong();
      long sum = n * (n + 1) / 2;
      long square = n * n;
      System.out.println(sum);
      System.out.println(square);
      """,
      [("3", "6\n9"), ("100000", "5000050000\n10000000000"),
       ("2000000", "2000001000000\n4000000000000"), ("1", "1\n1")],
      hint="Read into a long with sc.nextLong(). If even one operand is an int, the whole multiplication is done in int and wraps before it is widened.")

_chal("big_o", "big_o-challenge", "Counting the work", "Easy",
      "The input is one integer `n`. Print two lines that contrast two growth rates: first, how many times you can double from 1 without passing `n` (that is the size of a `for (i = 1; i <= n; i *= 2)` loop — Θ(log n)); second, how many unordered pairs `n` items form, `n * (n - 1) / 2` — Θ(n²). Use `long`.",
      """
      long n = sc.nextLong();
      long doublings = 0;
      for (long i = 1; i <= n; i *= 2) {
          doublings++;
      }
      long pairs = n * (n - 1) / 2;
      System.out.println(doublings);
      System.out.println(pairs);
      """,
      [("8", "4\n28"), ("1", "1\n0"), ("5", "3\n10"),
       ("1000000", "20\n499999500000")],
      hint="The doubling loop runs about log2(n) + 1 times — count the iterations rather than calling a log function.")

_chal("simulation", "simulation-challenge", "Robot walk", "Easy",
      "The input is one line of moves made of the characters `U`, `D`, `L`, `R`. Starting at `(0, 0)`, `U` adds 1 to y, `D` subtracts 1 from y, `R` adds 1 to x, `L` subtracts 1 from x. Print the final position as `x y`.",
      """
      String moves = sc.next();
      int x = 0;
      int y = 0;
      for (int i = 0; i < moves.length(); i++) {
          char c = moves.charAt(i);
          if (c == 'U') y++;
          else if (c == 'D') y--;
          else if (c == 'R') x++;
          else if (c == 'L') x--;
      }
      System.out.println(x + " " + y);
      """,
      [("UUDDLLRR", "0 0"), ("UUR", "1 2"),
       ("LLL", "-3 0"), ("R", "1 0"), ("UUUURDD", "1 2")],
      hint="Keep two counters and walk the string one character at a time — a simulation just does exactly what the rules say.")


# ===========================================================================
# Arrays
# ===========================================================================

_chal("iteration", "iteration-challenge", "Array report", "Intro",
      "The input is `n` on the first line and `n` integers on the second. Print three lines: their sum, the largest value, and how many of them are even.",
      """
      int n = sc.nextInt();
      int[] a = new int[n];
      for (int i = 0; i < n; i++) a[i] = sc.nextInt();
      long sum = 0;
      int max = a[0];
      int evens = 0;
      for (int i = 0; i < n; i++) {
          sum += a[i];
          if (a[i] > max) max = a[i];
          if (a[i] % 2 == 0) evens++;
      }
      System.out.println(sum);
      System.out.println(max);
      System.out.println(evens);
      """,
      [("5\n3 1 4 1 5", "14\n5\n1"), ("1\n7", "7\n7\n0"),
       ("4\n2 4 6 8", "20\n8\n4"), ("3\n-5 -2 -9", "-16\n-2\n1")],
      hint="One pass can answer all three questions. Seed max with a[0], not 0, so negative arrays work.")

_chal("array_patterns", "array_patterns-challenge", "Second largest", "Easy",
      "The input is `n` then `n` integers. Print the second largest DISTINCT value. If every value is the same (so there is no second distinct value), print `none`.",
      """
      int n = sc.nextInt();
      int[] a = new int[n];
      for (int i = 0; i < n; i++) a[i] = sc.nextInt();
      long best = Long.MIN_VALUE;
      long second = Long.MIN_VALUE;
      for (int i = 0; i < n; i++) {
          if (a[i] > best) {
              second = best;
              best = a[i];
          } else if (a[i] < best && a[i] > second) {
              second = a[i];
          }
      }
      if (second == Long.MIN_VALUE) System.out.println("none");
      else System.out.println(second);
      """,
      [("5\n3 1 4 1 5", "4"), ("3\n7 7 7", "none"),
       ("2\n1 2", "1"), ("6\n9 9 8 8 7 7", "8"), ("1\n5", "none")],
      hint="Track the best two as you scan. Skip a value equal to the current best so duplicates cannot fill the runner-up slot.")

_chal("two_pointers", "two_pointers-challenge", "Pair with a target sum", "Easy",
      "The input is `n target` then `n` integers **already sorted ascending**. Using two pointers from the ends, find a pair that sums to `target` and print the two values as `small large`. If no pair works, print `none`. In O(n), without a nested loop.",
      """
      int n = sc.nextInt();
      int target = sc.nextInt();
      int[] a = new int[n];
      for (int i = 0; i < n; i++) a[i] = sc.nextInt();
      int lo = 0;
      int hi = n - 1;
      String answer = "none";
      while (lo < hi) {
          int sum = a[lo] + a[hi];
          if (sum == target) {
              answer = a[lo] + " " + a[hi];
              break;
          } else if (sum < target) {
              lo++;
          } else {
              hi--;
          }
      }
      System.out.println(answer);
      """,
      [("5 9\n1 2 4 5 7", "2 7"), ("5 100\n1 2 4 5 7", "none"),
       ("4 6\n1 2 4 5", "1 5"), ("2 3\n1 2", "1 2"), ("1 5\n5", "none")],
      hint="Too small a sum means the small end must grow (lo++); too big means the large end must shrink (hi--).")

_chal("sliding_window", "sliding_window-challenge", "Best window of size k", "Easy",
      "The input is `n k` then `n` integers. Print the largest sum of any `k` consecutive elements. Slide the window instead of re-adding each block, so the whole thing is one pass.",
      """
      int n = sc.nextInt();
      int k = sc.nextInt();
      int[] a = new int[n];
      for (int i = 0; i < n; i++) a[i] = sc.nextInt();
      long sum = 0;
      for (int i = 0; i < k; i++) sum += a[i];
      long best = sum;
      for (int i = k; i < n; i++) {
          sum += a[i] - a[i - k];
          if (sum > best) best = sum;
      }
      System.out.println(best);
      """,
      [("6 3\n1 2 3 4 5 6", "15"), ("5 2\n2 1 5 1 3", "6"),
       ("4 4\n1 1 1 1", "4"), ("5 1\n-3 -1 -7 -2 -9", "-1"),
       ("7 3\n4 -1 2 1 -5 4 3", "5")],
      hint="Build the first window, then for each step add the entering element and subtract the leaving one: sum += a[i] - a[i - k].")

_chal("prefix_max", "prefix_max-challenge", "Visible peaks", "Easy",
      "The input is `n` then `n` heights. Walking left to right, a height is *visible* if it is strictly greater than every height before it (the first one always is). Print the number of visible heights on the first line and the visible heights themselves, space-separated, on the second.",
      """
      int n = sc.nextInt();
      int[] a = new int[n];
      for (int i = 0; i < n; i++) a[i] = sc.nextInt();
      StringBuilder sb = new StringBuilder();
      int count = 0;
      int best = Integer.MIN_VALUE;
      for (int i = 0; i < n; i++) {
          if (a[i] > best) {
              best = a[i];
              count++;
              if (sb.length() > 0) sb.append(' ');
              sb.append(a[i]);
          }
      }
      System.out.println(count);
      System.out.println(sb.toString());
      """,
      [("6\n3 1 4 1 5 9", "4\n3 4 5 9"), ("4\n5 4 3 2", "1\n5"),
       ("3\n1 2 3", "3\n1 2 3"), ("5\n2 2 2 3 3", "2\n2 3")],
      hint="Carry the running maximum of everything seen so far; a height is visible exactly when it beats that running maximum.")

# Rotating by reversal calls a helper three times, so this one needs a
# class-level method rather than the main-only scaffold.
_chal_cls("inplace_reverse", "inplace_reverse-challenge", "Rotate left by k", "Easy",
          "The input is `n k` then `n` integers. Rotate the array left by `k` positions **in place** using the reversal trick: reverse the first `k`, reverse the rest, then reverse the whole array. The `reverse(a, i, j)` helper is written for you — fill in `main`. (`k` can be ≥ `n`.)",
          """
    static void reverse(int[] a, int i, int j) {
        while (i < j) {
            int tmp = a[i];
            a[i] = a[j];
            a[j] = tmp;
            i++;
            j--;
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int k = sc.nextInt() % n;
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        reverse(a, 0, k - 1);
        reverse(a, k, n - 1);
        reverse(a, 0, n - 1);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(a[i]);
        }
        System.out.println(sb.toString());
    }
""",
          """
        int n = sc.nextInt();
        int k = sc.nextInt() % n;
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        reverse(a, 0, k - 1);
        reverse(a, k, n - 1);
        reverse(a, 0, n - 1);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(a[i]);
        }
        System.out.println(sb.toString());
""",
          [("5 2\n1 2 3 4 5", "3 4 5 1 2"), ("5 0\n1 2 3 4 5", "1 2 3 4 5"),
           ("5 7\n1 2 3 4 5", "3 4 5 1 2"), ("4 2\n1 2 3 4", "3 4 1 2"),
           ("3 1\n9 8 7", "8 7 9")],
          hint="Reduce k with k % n first. reverse(a, 0, k-1), then reverse(a, k, n-1), then reverse the whole array.")

_chal("prefix_sum", "prefix_sum-challenge", "Range sum queries", "Easy",
      "The input is `n q`, then `n` integers, then `q` query lines each holding `l r` (0-indexed, inclusive). Build a prefix-sum array once, then answer every query in O(1). Print one sum per line.",
      """
      int n = sc.nextInt();
      int q = sc.nextInt();
      long[] pre = new long[n + 1];
      for (int i = 0; i < n; i++) {
          pre[i + 1] = pre[i] + sc.nextInt();
      }
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < q; i++) {
          int l = sc.nextInt();
          int r = sc.nextInt();
          sb.append(pre[r + 1] - pre[l]).append('\\n');
      }
      System.out.print(sb.toString());
      """,
      [("5 3\n1 2 3 4 5\n0 4\n1 3\n2 2", "15\n9\n3"),
       ("4 2\n-1 -2 -3 -4\n0 1\n2 3", "-3\n-7"),
       ("1 1\n42\n0 0", "42"),
       ("6 2\n1 1 1 1 1 1\n0 5\n3 4", "6\n2")],
      hint="pre[i+1] = pre[i] + a[i]. Then the sum of a[l..r] is pre[r+1] - pre[l].")

_chal("grid", "grid-challenge", "Border sum", "Easy",
      "The input is `r c` then `r` rows of `c` integers. Print two lines: the sum of the border cells (row 0, row r-1, column 0, column c-1 — counting each cell once) and the sum of the interior cells.",
      """
      int r = sc.nextInt();
      int c = sc.nextInt();
      int[][] g = new int[r][c];
      for (int i = 0; i < r; i++) {
          for (int j = 0; j < c; j++) g[i][j] = sc.nextInt();
      }
      long border = 0;
      long inside = 0;
      for (int i = 0; i < r; i++) {
          for (int j = 0; j < c; j++) {
              if (i == 0 || i == r - 1 || j == 0 || j == c - 1) border += g[i][j];
              else inside += g[i][j];
          }
      }
      System.out.println(border);
      System.out.println(inside);
      """,
      [("3 3\n1 2 3\n4 5 6\n7 8 9", "40\n5"),
       ("2 2\n1 1\n1 1", "4\n0"),
       ("1 4\n1 2 3 4", "10\n0"),
       ("4 4\n1 1 1 1\n1 2 2 1\n1 2 2 1\n1 1 1 1", "12\n8")],
      hint="A cell is on the border exactly when its row is the first or last, or its column is the first or last — one condition, no double counting.")


# ===========================================================================
# Strings
# ===========================================================================

_chal("string_basics", "string_basics-challenge", "Word stats", "Intro",
      "The input is one line of lowercase words separated by single spaces. Print three lines: how many words there are, how many characters the line has excluding spaces, and the longest word (the first one, if several tie).",
      """
      String line = sc.nextLine();
      String[] words = line.split(" ");
      int letters = 0;
      String longest = words[0];
      for (int i = 0; i < words.length; i++) {
          letters += words[i].length();
          if (words[i].length() > longest.length()) longest = words[i];
      }
      System.out.println(words.length);
      System.out.println(letters);
      System.out.println(longest);
      """,
      [("the quick brown fox", "4\n16\nquick"),
       ("hello", "1\n5\nhello"),
       ("a bb ccc dd", "4\n8\nccc"),
       ("one two six ten", "4\n12\none")],
      hint="split(\" \") gives you the words; sum their lengths for the letter count and keep the longest seen so far.")

_chal("char_arrays", "char_arrays-challenge", "Caesar shift", "Easy",
      "The input is a line of lowercase letters and spaces, then a number `k` on the next line. Shift every letter forward by `k` positions in the alphabet, wrapping `z` around to `a`. Leave spaces alone. Print the result.",
      """
      String line = sc.nextLine();
      int k = Integer.parseInt(sc.nextLine().trim());
      char[] cs = line.toCharArray();
      for (int i = 0; i < cs.length; i++) {
          if (cs[i] != ' ') {
              cs[i] = (char) ('a' + (cs[i] - 'a' + k) % 26);
          }
      }
      System.out.println(new String(cs));
      """,
      [("abc\n1", "bcd"), ("xyz\n3", "abc"),
       ("hello world\n0", "hello world"), ("zebra\n1", "afcsb"),
       ("attack at dawn\n13", "nggnpx ng qnja")],
      hint="Map the letter to 0..25 with c - 'a', add k, take % 26, then map back with (char)('a' + x).")

_chal("canonical", "canonical-challenge", "Anagram check", "Easy",
      "The input is two lowercase words, one per line. Print `true` if they are anagrams of each other (same letters, same counts) and `false` otherwise. Compare their canonical forms — the sorted characters — rather than trying every rearrangement.",
      """
      String a = sc.next();
      String b = sc.next();
      char[] ca = a.toCharArray();
      char[] cb = b.toCharArray();
      Arrays.sort(ca);
      Arrays.sort(cb);
      System.out.println(Arrays.equals(ca, cb));
      """,
      [("listen\nsilent", "true"), ("hello\nworld", "false"),
       ("abc\nab", "false"), ("aab\naba", "true"), ("a\na", "true")],
      hint="Sorting both words gives each anagram class one shared representative — then a single equality check answers the question.")


# ===========================================================================
# Data Structures
# ===========================================================================

_chal("hashing", "hashing-challenge", "Most frequent word", "Easy",
      "The input is `n` then `n` lowercase words, one per line. Print the word that appears most often and its count, separated by a space. If several tie, print whichever reached the winning count first as you scan.",
      """
      int n = sc.nextInt();
      HashMap<String, Integer> counts = new HashMap<>();
      String best = "";
      int bestCount = 0;
      for (int i = 0; i < n; i++) {
          String w = sc.next();
          int c = counts.getOrDefault(w, 0) + 1;
          counts.put(w, c);
          if (c > bestCount) {
              bestCount = c;
              best = w;
          }
      }
      System.out.println(best + " " + bestCount);
      """,
      [("5\nab\ncd\nab\nef\nab", "ab 3"), ("3\nx\ny\nz", "x 1"),
       ("4\na\nb\nb\na", "b 2"), ("1\nsolo", "solo 1")],
      hint="getOrDefault(w, 0) + 1 counts without a null check. Track the leader as you go so no second pass is needed.")

_chal("complement", "complement-challenge", "Two-sum indices", "Easy",
      "The input is `n target` then `n` integers (**not** sorted). Print the 0-indexed positions `i j` (i < j) of the first pair that sums to `target` — for each value, look up whether its complement `target - value` was already seen. Print `none` if there is no such pair. O(n).",
      """
      int n = sc.nextInt();
      int target = sc.nextInt();
      HashMap<Integer, Integer> seen = new HashMap<>();
      String answer = "none";
      for (int i = 0; i < n; i++) {
          int v = sc.nextInt();
          Integer j = seen.get(target - v);
          if (j != null && answer.equals("none")) {
              answer = j + " " + i;
          }
          if (!seen.containsKey(v)) seen.put(v, i);
      }
      System.out.println(answer);
      """,
      [("4 9\n2 7 11 15", "0 1"), ("4 100\n2 7 11 15", "none"),
       ("5 6\n3 3 1 2 4", "0 1"), ("3 0\n-1 5 1", "0 2"), ("1 5\n5", "none")],
      hint="Store value -> first index. Before inserting the current value, ask the map whether target - value is already there.")

_chal("stack", "stack-challenge", "Balanced brackets", "Easy",
      "The input is one line made of the characters `()[]{}`. Print `true` if every bracket is closed by the matching kind in the right order, `false` otherwise.",
      """
      String s = sc.next();
      ArrayDeque<Character> stack = new ArrayDeque<>();
      boolean ok = true;
      for (int i = 0; i < s.length(); i++) {
          char c = s.charAt(i);
          if (c == '(' || c == '[' || c == '{') {
              stack.push(c);
          } else {
              char want = '{';
              if (c == ')') want = '(';
              else if (c == ']') want = '[';
              if (stack.isEmpty() || stack.pop() != want) {
                  ok = false;
                  break;
              }
          }
      }
      System.out.println(ok && stack.isEmpty());
      """,
      [("([]{})", "true"), ("([)]", "false"), ("(((", "false"),
       (")(", "false"), ("{}", "true"), ("[({})]", "true")],
      hint="Push every opener. On a closer, the top of the stack must be its partner — and at the end the stack must be empty.")

_chal("queue", "queue-challenge", "Hot potato", "Easy",
      "The input is `n k`. Players `1..n` stand in a queue. Repeatedly move the front player to the back `k - 1` times, then remove the player now at the front. Print the removal order on one line, space-separated.",
      """
      int n = sc.nextInt();
      int k = sc.nextInt();
      ArrayDeque<Integer> q = new ArrayDeque<>();
      for (int i = 1; i <= n; i++) q.addLast(i);
      StringBuilder sb = new StringBuilder();
      while (!q.isEmpty()) {
          for (int i = 0; i < k - 1; i++) q.addLast(q.pollFirst());
          if (sb.length() > 0) sb.append(' ');
          sb.append(q.pollFirst());
      }
      System.out.println(sb.toString());
      """,
      [("5 2", "2 4 1 5 3"), ("3 1", "1 2 3"),
       ("4 3", "3 2 4 1"), ("1 5", "1")],
      hint="pollFirst() takes from the front, addLast() puts on the back — that rotation is the whole game.")

_chal("visited_set", "visited_set-challenge", "First repeat", "Easy",
      "The input is `n` then `n` integers. Print the first value that appears for the SECOND time as you scan left to right, or `none` if every value is distinct.",
      """
      int n = sc.nextInt();
      HashSet<Integer> seen = new HashSet<>();
      String answer = "none";
      for (int i = 0; i < n; i++) {
          int v = sc.nextInt();
          if (!seen.add(v) && answer.equals("none")) {
              answer = String.valueOf(v);
          }
      }
      System.out.println(answer);
      """,
      [("5\n1 2 3 2 1", "2"), ("3\n1 2 3", "none"),
       ("4\n7 7 7 7", "7"), ("6\n5 1 4 1 5 9", "1")],
      hint="HashSet.add returns false when the value was already there — that single call both tests and records.")

_chal("heap", "heap-challenge", "Merge the stones", "Easy",
      "The input is `n` then `n` positive integers. Repeatedly remove the two SMALLEST values, add their sum back, and charge that sum as a cost — until one value remains. Print the total cost. (This is Huffman's rule.)",
      """
      int n = sc.nextInt();
      PriorityQueue<Long> pq = new PriorityQueue<>();
      for (int i = 0; i < n; i++) pq.add((long) sc.nextInt());
      long cost = 0;
      while (pq.size() > 1) {
          long a = pq.poll();
          long b = pq.poll();
          cost += a + b;
          pq.add(a + b);
      }
      System.out.println(cost);
      """,
      [("4\n1 2 3 4", "19"), ("2\n5 5", "10"),
       ("1\n7", "0"), ("3\n1 1 1", "5"), ("5\n4 3 2 6 1", "35")],
      hint="A PriorityQueue<Long> is a min-heap by default, so poll() always hands you the current smallest.")

_chal("top_k", "top_k-challenge", "Top k largest", "Easy",
      "The input is `n k` then `n` integers. Print the `k` largest values in DESCENDING order on one line, space-separated. Keep a size-`k` min-heap so you never sort the whole input.",
      """
      int n = sc.nextInt();
      int k = sc.nextInt();
      PriorityQueue<Integer> pq = new PriorityQueue<>();
      for (int i = 0; i < n; i++) {
          pq.add(sc.nextInt());
          if (pq.size() > k) pq.poll();
      }
      int[] out = new int[pq.size()];
      for (int i = out.length - 1; i >= 0; i--) out[i] = pq.poll();
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < out.length; i++) {
          if (i > 0) sb.append(' ');
          sb.append(out[i]);
      }
      System.out.println(sb.toString());
      """,
      [("6 3\n3 1 4 1 5 9", "9 5 4"), ("4 1\n2 8 5 1", "8"),
       ("3 3\n1 2 3", "3 2 1"), ("5 2\n-1 -2 -3 -4 -5", "-1 -2")],
      hint="Keep the heap at size k by polling the smallest whenever it grows past k; drain it backwards to get descending order.")

_chal("two_heaps", "two_heaps-challenge", "Running median", "Medium",
      "The input is `n` then `n` integers. After reading each one, print the median of everything read so far, one per line. For an even count print the LOWER of the two middle values. Keep a max-heap of the small half and a min-heap of the large half.",
      """
      int n = sc.nextInt();
      PriorityQueue<Integer> low = new PriorityQueue<>(Collections.reverseOrder());
      PriorityQueue<Integer> high = new PriorityQueue<>();
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < n; i++) {
          int v = sc.nextInt();
          if (low.isEmpty() || v <= low.peek()) low.add(v);
          else high.add(v);
          if (low.size() > high.size() + 1) high.add(low.poll());
          else if (high.size() > low.size()) low.add(high.poll());
          sb.append(low.peek()).append('\\n');
      }
      System.out.print(sb.toString());
      """,
      [("5\n1 2 3 4 5", "1\n1\n2\n2\n3"), ("1\n9", "9"),
       ("4\n4 3 2 1", "4\n3\n3\n2"), ("6\n5 15 1 3 8 7", "5\n5\n5\n3\n5\n5")],
      hint="Rebalance so low.size() equals high.size() or is exactly one bigger; then low.peek() is always the lower median.")

_chal("heap_greedy", "heap_greedy-challenge", "Meeting rooms", "Medium",
      "The input is `n` then `n` lines each holding a meeting's `start end`. Print the smallest number of rooms needed so no two meetings overlap in a room. Sort by start time and keep a min-heap of the end times currently in use.",
      """
      int n = sc.nextInt();
      int[][] m = new int[n][2];
      for (int i = 0; i < n; i++) {
          m[i][0] = sc.nextInt();
          m[i][1] = sc.nextInt();
      }
      Arrays.sort(m, (x, y) -> Integer.compare(x[0], y[0]));
      PriorityQueue<Integer> ends = new PriorityQueue<>();
      for (int i = 0; i < n; i++) {
          if (!ends.isEmpty() && ends.peek() <= m[i][0]) ends.poll();
          ends.add(m[i][1]);
      }
      System.out.println(ends.size());
      """,
      [("3\n0 30\n5 10\n15 20", "2"), ("2\n7 10\n2 4", "1"),
       ("1\n1 5", "1"), ("4\n1 4\n2 5\n3 6\n4 7", "3"),
       ("3\n1 2\n2 3\n3 4", "1")],
      hint="The heap's smallest end time is the room that frees up soonest — reuse it when the next meeting starts at or after that time.")

_chal("design_ds", "design_ds-challenge", "Stack with getMin", "Medium",
      "The input is `n` then `n` commands: `push v`, `pop`, or `min`. Maintain a stack that answers `min` in O(1) by pushing the running minimum onto a second stack. Print one line per `min` command.",
      """
      int n = sc.nextInt();
      ArrayDeque<Integer> data = new ArrayDeque<>();
      ArrayDeque<Integer> mins = new ArrayDeque<>();
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < n; i++) {
          String cmd = sc.next();
          if (cmd.equals("push")) {
              int v = sc.nextInt();
              data.push(v);
              mins.push(mins.isEmpty() ? v : Math.min(v, mins.peek()));
          } else if (cmd.equals("pop")) {
              data.pop();
              mins.pop();
          } else {
              sb.append(mins.peek()).append('\\n');
          }
      }
      System.out.print(sb.toString());
      """,
      [("6\npush 3\npush 1\nmin\npop\nmin\npush 0", "1\n3"),
       ("4\npush 5\nmin\npush 9\nmin", "5\n5"),
       ("5\npush 4\npush 4\nmin\npop\nmin", "4\n4"),
       ("7\npush 9\npush 2\npush 7\nmin\npop\npop\nmin", "2\n9")],
      hint="Every push also pushes min(value, current min); every pop pops both stacks, so their tops always agree.")

_chal("trie", "trie-challenge", "Longest common prefix", "Medium",
      "The input is `n` then `n` lowercase words. Print the longest prefix shared by ALL of them, or `(empty)` if there is none. (A trie stores exactly this: walk down while every word still agrees.)",
      """
      int n = sc.nextInt();
      String[] w = new String[n];
      for (int i = 0; i < n; i++) w[i] = sc.next();
      int len = 0;
      while (len < w[0].length()) {
          char c = w[0].charAt(len);
          boolean all = true;
          for (int i = 1; i < n; i++) {
              if (len >= w[i].length() || w[i].charAt(len) != c) {
                  all = false;
                  break;
              }
          }
          if (!all) break;
          len++;
      }
      String prefix = w[0].substring(0, len);
      System.out.println(prefix.isEmpty() ? "(empty)" : prefix);
      """,
      [("3\nflower\nflow\nflight", "fl"), ("3\ndog\ncar\nrace", "(empty)"),
       ("1\nalone", "alone"), ("2\nsame\nsame", "same"),
       ("3\nabc\nabcd\nab", "ab")],
      hint="Extend the prefix one character at a time; stop the moment any word disagrees or runs out of characters.")


# ===========================================================================
# Linked Lists — the Node class and list building are given, so the challenge
# is the pointer walk itself.
# ===========================================================================

_chal_cls("list_basics", "list_basics-challenge", "Nth node from the end", "Easy",
          "The input is `n k` then `n` values forming a linked list. Print the value of the k-th node from the END (k = 1 is the last node). Use the two-pass idea: walk once to learn the length, then walk to position `length - k`.",
          """
    static class Node {
        int val;
        Node next;
        Node(int val) { this.val = val; }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int k = sc.nextInt();
        Node head = null;
        Node tail = null;
        for (int i = 0; i < n; i++) {
            Node node = new Node(sc.nextInt());
            if (head == null) head = node;
            else tail.next = node;
            tail = node;
        }
        int len = 0;
        for (Node q = head; q != null; q = q.next) len++;
        Node p = head;
        for (int i = 0; i < len - k; i++) p = p.next;
        System.out.println(p.val);
    }
""",
          """
        int len = 0;
        for (Node q = head; q != null; q = q.next) len++;
        Node p = head;
        for (int i = 0; i < len - k; i++) p = p.next;
        System.out.println(p.val);
""",
          [("5 2\n1 2 3 4 5", "4"), ("5 5\n1 2 3 4 5", "1"),
           ("1 1\n42", "42"), ("3 1\n7 8 9", "9")],
          hint="The k-th from the end sits at 0-indexed position len - k. Count the nodes first, then take that many steps.")

_chal_cls("list_reversal", "list_reversal-challenge", "Reverse a linked list", "Easy",
          "The input is `n` then `n` values forming a linked list. Reverse it **in place** with the three-pointer walk (`prev`, `curr`, `next`) and print the reversed values space-separated.",
          """
    static class Node {
        int val;
        Node next;
        Node(int val) { this.val = val; }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        Node head = null;
        Node tail = null;
        for (int i = 0; i < n; i++) {
            Node node = new Node(sc.nextInt());
            if (head == null) head = node;
            else tail.next = node;
            tail = node;
        }
        Node prev = null;
        Node curr = head;
        while (curr != null) {
            Node next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        StringBuilder sb = new StringBuilder();
        for (Node p = prev; p != null; p = p.next) {
            if (sb.length() > 0) sb.append(' ');
            sb.append(p.val);
        }
        System.out.println(sb.toString());
    }
""",
          """
        Node prev = null;
        Node curr = head;
        while (curr != null) {
            Node next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        StringBuilder sb = new StringBuilder();
        for (Node p = prev; p != null; p = p.next) {
            if (sb.length() > 0) sb.append(' ');
            sb.append(p.val);
        }
        System.out.println(sb.toString());
""",
          [("5\n1 2 3 4 5", "5 4 3 2 1"), ("1\n7", "7"),
           ("2\n1 2", "2 1"), ("4\n9 8 7 6", "6 7 8 9")],
          hint="Save curr.next BEFORE you overwrite it, or the rest of the list is lost. When curr falls off the end, prev is the new head.")

_chal_cls("fast_slow", "fast_slow-challenge", "Middle of the list", "Easy",
          "The input is `n` then `n` values forming a linked list. Print the value of the middle node in ONE pass using a slow pointer that steps once and a fast pointer that steps twice. For an even length, print the SECOND of the two middle nodes.",
          """
    static class Node {
        int val;
        Node next;
        Node(int val) { this.val = val; }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        Node head = null;
        Node tail = null;
        for (int i = 0; i < n; i++) {
            Node node = new Node(sc.nextInt());
            if (head == null) head = node;
            else tail.next = node;
            tail = node;
        }
        Node slow = head;
        Node fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        System.out.println(slow.val);
    }
""",
          """
        Node slow = head;
        Node fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        System.out.println(slow.val);
""",
          [("5\n1 2 3 4 5", "3"), ("4\n1 2 3 4", "3"),
           ("1\n8", "8"), ("2\n1 2", "2"), ("7\n1 2 3 4 5 6 7", "4")],
          hint="Two steps for fast per one for slow: when fast reaches the end, slow sits at the middle. Guard with fast != null AND fast.next != null.")


# ===========================================================================
# Trees — the tree arrives as a level-order array with -1 for "no child", so
# every challenge is about the traversal, not about parsing.
# ===========================================================================

_chal_cls("tree_basics", "tree_basics-challenge", "Height and leaf count", "Easy",
          "The input is `n` then `n` values in level order, where `-1` marks a missing node. Node `i`'s children sit at `2*i + 1` and `2*i + 2`. Print the height (a single node has height 1) on the first line and the number of leaves on the second. The array is built for you — write the two recursive helpers' bodies and the printing.",
          """
    static int[] a;

    static int height(int i) {
        if (i >= a.length || a[i] == -1) return 0;
        return 1 + Math.max(height(2 * i + 1), height(2 * i + 2));
    }

    static int leaves(int i) {
        if (i >= a.length || a[i] == -1) return 0;
        boolean left = 2 * i + 1 < a.length && a[2 * i + 1] != -1;
        boolean right = 2 * i + 2 < a.length && a[2 * i + 2] != -1;
        if (!left && !right) return 1;
        return leaves(2 * i + 1) + leaves(2 * i + 2);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        System.out.println(height(0));
        System.out.println(leaves(0));
    }
""",
          """
    static int height(int i) {
        if (i >= a.length || a[i] == -1) return 0;
        return 1 + Math.max(height(2 * i + 1), height(2 * i + 2));
    }

    static int leaves(int i) {
        if (i >= a.length || a[i] == -1) return 0;
        boolean left = 2 * i + 1 < a.length && a[2 * i + 1] != -1;
        boolean right = 2 * i + 2 < a.length && a[2 * i + 2] != -1;
        if (!left && !right) return 1;
        return leaves(2 * i + 1) + leaves(2 * i + 2);
    }
""",
          [("7\n1 2 3 4 5 6 7", "3\n4"), ("1\n5", "1\n1"),
           ("3\n1 2 -1", "2\n1"), ("5\n1 2 3 -1 -1", "2\n2"),
           ("7\n1 2 3 4 -1 -1 -1", "3\n2")],
          hint="An empty slot has height 0 and no leaves. A node is a leaf when neither child index holds a real value.")

_chal_cls("tree_traversal", "tree_traversal-challenge", "Inorder and level order", "Easy",
          "The input is `n` then `n` values in level order with `-1` for a missing node. Print the INORDER traversal (left, node, right) on the first line and the LEVEL-ORDER traversal (skipping missing nodes) on the second — both space-separated.",
          """
    static int[] a;
    static StringBuilder sb = new StringBuilder();

    static void inorder(int i) {
        if (i >= a.length || a[i] == -1) return;
        inorder(2 * i + 1);
        if (sb.length() > 0) sb.append(' ');
        sb.append(a[i]);
        inorder(2 * i + 2);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        inorder(0);
        System.out.println(sb.toString());
        StringBuilder level = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (a[i] == -1) continue;
            if (level.length() > 0) level.append(' ');
            level.append(a[i]);
        }
        System.out.println(level.toString());
    }
""",
          """
    static void inorder(int i) {
        if (i >= a.length || a[i] == -1) return;
        inorder(2 * i + 1);
        if (sb.length() > 0) sb.append(' ');
        sb.append(a[i]);
        inorder(2 * i + 2);
    }
""",
          [("7\n1 2 3 4 5 6 7", "4 2 5 1 6 3 7\n1 2 3 4 5 6 7"),
           ("1\n9", "9\n9"),
           ("3\n2 1 3", "1 2 3\n2 1 3"),
           ("5\n1 2 3 -1 4", "2 4 1 3\n1 2 3 4")],
          hint="Inorder is: recurse left, visit, recurse right. The level order is just the array read left to right with the -1 gaps skipped.")

_chal_cls("bst", "bst-challenge", "Validate a BST", "Medium",
          "The input is `n` then `n` values in level order with `-1` for a missing node (all real values are positive). Print `true` if the tree is a valid binary search tree — every value in the left subtree strictly less than the node, every value on the right strictly greater — and `false` otherwise. Pass an allowed (low, high) range down as you recurse.",
          """
    static int[] a;

    static boolean valid(int i, long low, long high) {
        if (i >= a.length || a[i] == -1) return true;
        if (a[i] <= low || a[i] >= high) return false;
        return valid(2 * i + 1, low, a[i]) && valid(2 * i + 2, a[i], high);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        System.out.println(valid(0, Long.MIN_VALUE, Long.MAX_VALUE));
    }
""",
          """
    static boolean valid(int i, long low, long high) {
        if (i >= a.length || a[i] == -1) return true;
        if (a[i] <= low || a[i] >= high) return false;
        return valid(2 * i + 1, low, a[i]) && valid(2 * i + 2, a[i], high);
    }
""",
          [("3\n2 1 3", "true"), ("3\n1 2 3", "false"),
           ("7\n8 4 12 2 6 10 14", "true"),
           ("7\n8 4 12 2 9 10 14", "false"),
           ("1\n5", "true")],
          hint="Checking only node-vs-child is not enough — a deep descendant can still violate an ancestor's bound, so tighten (low, high) on the way down.")

_chal_cls("tree_dp", "tree_dp-challenge", "Maximum root-to-leaf sum", "Medium",
          "The input is `n` then `n` values in level order with `-1` for a missing node (values may be negative, and `-1` never appears as a real value). Print the largest sum along any path from the root down to a leaf. Aggregate in postorder: each node's answer is its own value plus the better of its two subtrees.",
          """
    static int[] a;

    static long best(int i) {
        if (i >= a.length || a[i] == -1) return Long.MIN_VALUE;
        long left = best(2 * i + 1);
        long right = best(2 * i + 2);
        if (left == Long.MIN_VALUE && right == Long.MIN_VALUE) return a[i];
        return a[i] + Math.max(left, right);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        System.out.println(best(0));
    }
""",
          """
    static long best(int i) {
        if (i >= a.length || a[i] == -1) return Long.MIN_VALUE;
        long left = best(2 * i + 1);
        long right = best(2 * i + 2);
        if (left == Long.MIN_VALUE && right == Long.MIN_VALUE) return a[i];
        return a[i] + Math.max(left, right);
    }
""",
          [("7\n1 2 3 4 5 6 7", "11"), ("1\n5", "5"),
           ("3\n1 2 -1", "3"), ("7\n10 5 20 -1 -1 1 30", "60"),
           ("3\n-5 -2 -9", "-7")],
          hint="A leaf's answer is just its own value. Use a sentinel for 'no subtree' so a one-child node does not accidentally pick the missing side.")


# ===========================================================================
# Searching & Sorting
# ===========================================================================

_chal("sorting", "sorting-challenge", "Sort by length then alphabetically", "Easy",
      "The input is `n` then `n` lowercase words. Print them one per line sorted by length (shortest first) and, for equal lengths, alphabetically.",
      """
      int n = sc.nextInt();
      String[] w = new String[n];
      for (int i = 0; i < n; i++) w[i] = sc.next();
      Arrays.sort(w, (x, y) -> x.length() != y.length()
              ? Integer.compare(x.length(), y.length())
              : x.compareTo(y));
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < n; i++) sb.append(w[i]).append('\\n');
      System.out.print(sb.toString());
      """,
      [("4\npear\nfig\napple\nkiwi", "fig\nkiwi\npear\napple"),
       ("3\nbb\naa\ncc", "aa\nbb\ncc"),
       ("1\nsolo", "solo"),
       ("4\nab\nba\nabc\na", "a\nab\nba\nabc")],
      hint="A comparator returns a negative/zero/positive int. Compare lengths first; only fall back to compareTo when they tie.")

_chal("binary_search", "binary_search-challenge", "First index at least target", "Easy",
      "The input is `n target` then `n` integers sorted ascending. Print the index of the FIRST element that is `>= target` (the lower bound), or `n` if every element is smaller. Use binary search — O(log n), not a scan.",
      """
      int n = sc.nextInt();
      int target = sc.nextInt();
      int[] a = new int[n];
      for (int i = 0; i < n; i++) a[i] = sc.nextInt();
      int lo = 0;
      int hi = n;
      while (lo < hi) {
          int mid = lo + (hi - lo) / 2;
          if (a[mid] >= target) hi = mid;
          else lo = mid + 1;
      }
      System.out.println(lo);
      """,
      [("5 4\n1 3 4 6 8", "2"), ("5 5\n1 3 4 6 8", "3"),
       ("5 9\n1 3 4 6 8", "5"), ("5 0\n1 3 4 6 8", "0"),
       ("4 3\n3 3 3 3", "0"), ("1 1\n1", "0")],
      hint="Search the half-open range [lo, hi). When a[mid] >= target the answer might BE mid, so move hi to mid rather than mid - 1.")

_chal("greedy", "greedy-challenge", "Fewest coins", "Easy",
      "The input is `amount` then `n` on the next line then `n` coin values sorted DESCENDING, where each coin divides the one above it (so greedy is optimal). Print the fewest coins that make `amount` exactly, then on the next line how many of each coin you used, space-separated in the same order.",
      """
      int amount = sc.nextInt();
      int n = sc.nextInt();
      int[] coins = new int[n];
      for (int i = 0; i < n; i++) coins[i] = sc.nextInt();
      int[] used = new int[n];
      int total = 0;
      for (int i = 0; i < n; i++) {
          used[i] = amount / coins[i];
          amount -= used[i] * coins[i];
          total += used[i];
      }
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < n; i++) {
          if (i > 0) sb.append(' ');
          sb.append(used[i]);
      }
      System.out.println(total);
      System.out.println(sb.toString());
      """,
      [("87\n4\n25 10 5 1", "6\n3 1 0 2"),
       ("0\n2\n5 1", "0\n0 0"),
       ("100\n4\n25 10 5 1", "4\n4 0 0 0"),
       ("9\n2\n5 1", "5\n1 4")],
      hint="Take as many of the biggest coin as fit (amount / coin), subtract what you took, and move on — the divisibility guarantee is what makes that safe.")

_chal("intervals", "intervals-challenge", "Merge overlapping intervals", "Medium",
      "The input is `n` then `n` lines each holding `start end`. Merge every overlapping or touching pair and print the merged intervals sorted by start, one `start end` per line.",
      """
      int n = sc.nextInt();
      int[][] iv = new int[n][2];
      for (int i = 0; i < n; i++) {
          iv[i][0] = sc.nextInt();
          iv[i][1] = sc.nextInt();
      }
      Arrays.sort(iv, (x, y) -> Integer.compare(x[0], y[0]));
      StringBuilder sb = new StringBuilder();
      int start = iv[0][0];
      int end = iv[0][1];
      for (int i = 1; i < n; i++) {
          if (iv[i][0] <= end) {
              end = Math.max(end, iv[i][1]);
          } else {
              sb.append(start).append(' ').append(end).append('\\n');
              start = iv[i][0];
              end = iv[i][1];
          }
      }
      sb.append(start).append(' ').append(end).append('\\n');
      System.out.print(sb.toString());
      """,
      [("4\n1 3\n2 6\n8 10\n15 18", "1 6\n8 10\n15 18"),
       ("2\n1 4\n4 5", "1 5"),
       ("1\n5 7", "5 7"),
       ("3\n5 6\n1 2\n3 4", "1 2\n3 4\n5 6"),
       ("3\n1 10\n2 3\n4 5", "1 10")],
      hint="Sort by start, then hold one open interval. The next one either extends it (start <= end) or closes it and starts a new one.")


# ===========================================================================
# Recursion & DP
# ===========================================================================

_chal_cls("recursion", "recursion-challenge", "Recursive digit sum", "Easy",
          "The input is one non-negative integer `n`. Write a RECURSIVE method that sums its digits, then keeps summing until a single digit remains (`9875 -> 29 -> 11 -> 2`). Print the final digit. No loops.",
          """
    static int digitSum(int n) {
        if (n < 10) return n;
        return n % 10 + digitSum(n / 10);
    }

    static int root(int n) {
        if (n < 10) return n;
        return root(digitSum(n));
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(root(n));
    }
""",
          """
    static int digitSum(int n) {
        if (n < 10) return n;
        return n % 10 + digitSum(n / 10);
    }

    static int root(int n) {
        if (n < 10) return n;
        return root(digitSum(n));
    }
""",
          [("9875", "2"), ("0", "0"), ("9", "9"),
           ("38", "2"), ("999999999", "9")],
          hint="Two base cases, both 'already a single digit'. digitSum peels one digit with % 10 and recurses on n / 10.")

_chal("dp", "dp-challenge", "House robber", "Medium",
      "The input is `n` then `n` non-negative values. Pick a subset with no two adjacent entries so the total is as large as possible, and print that total. Build it bottom-up: the best through house `i` is either skipping it (the best through `i - 1`) or taking it (`value[i]` plus the best through `i - 2`).",
      """
      int n = sc.nextInt();
      int[] a = new int[n];
      for (int i = 0; i < n; i++) a[i] = sc.nextInt();
      long skip = 0;
      long take = 0;
      for (int i = 0; i < n; i++) {
          long nextTake = skip + a[i];
          long nextSkip = Math.max(skip, take);
          take = nextTake;
          skip = nextSkip;
      }
      System.out.println(Math.max(skip, take));
      """,
      [("4\n1 2 3 1", "4"), ("5\n2 7 9 3 1", "12"),
       ("1\n5", "5"), ("3\n0 0 0", "0"), ("2\n4 9", "9")],
      hint="Two rolling numbers are enough: the best ending by taking house i, and the best ending by not taking it.")

_chal("recurrence", "recurrence-challenge", "Tribonacci", "Easy",
      "`T(0) = 0`, `T(1) = 1`, `T(2) = 1`, and `T(n) = T(n-1) + T(n-2) + T(n-3)`. The input is one `n` up to 70. Print `T(n)` — iteratively, with `long`, so it stays O(n) and does not overflow.",
      """
      int n = sc.nextInt();
      long a = 0;
      long b = 1;
      long c = 1;
      if (n == 0) {
          System.out.println(0);
      } else if (n <= 2) {
          System.out.println(1);
      } else {
          for (int i = 3; i <= n; i++) {
              long next = a + b + c;
              a = b;
              b = c;
              c = next;
          }
          System.out.println(c);
      }
      """,
      [("0", "0"), ("1", "1"), ("2", "1"), ("4", "4"),
       ("25", "1389537"), ("37", "2082876103")],
      hint="Roll three variables forward instead of recursing — plain recursion here recomputes the same values exponentially often.")

_chal("dp2d", "dp2d-challenge", "Grid paths with obstacles", "Medium",
      "The input is `r c` then an `r` × `c` grid of `0` (open) and `1` (blocked). Starting at the top-left and moving only right or down, print how many distinct paths reach the bottom-right. Print `0` if either end is blocked. Fill a 2-D table row by row.",
      """
      int r = sc.nextInt();
      int c = sc.nextInt();
      int[][] g = new int[r][c];
      for (int i = 0; i < r; i++) {
          for (int j = 0; j < c; j++) g[i][j] = sc.nextInt();
      }
      long[][] dp = new long[r][c];
      for (int i = 0; i < r; i++) {
          for (int j = 0; j < c; j++) {
              if (g[i][j] == 1) {
                  dp[i][j] = 0;
              } else if (i == 0 && j == 0) {
                  dp[i][j] = 1;
              } else {
                  long up = i > 0 ? dp[i - 1][j] : 0;
                  long left = j > 0 ? dp[i][j - 1] : 0;
                  dp[i][j] = up + left;
              }
          }
      }
      System.out.println(dp[r - 1][c - 1]);
      """,
      [("3 3\n0 0 0\n0 1 0\n0 0 0", "2"),
       ("3 3\n0 0 0\n0 0 0\n0 0 0", "6"),
       ("1 1\n0", "1"), ("1 1\n1", "0"),
       ("2 2\n0 1\n1 0", "0"),
       ("3 4\n0 0 0 0\n0 0 0 0\n0 0 0 0", "10")],
      hint="Each open cell's count is the cell above plus the cell to the left; a blocked cell contributes 0 to everything downstream.")

_chal_cls("backtracking", "backtracking-challenge", "All permutations", "Medium",
          "The input is `n` then `n` distinct lowercase letters. Print every permutation of them, one per line, in lexicographic order. Sort the letters first, then build each arrangement by choosing an unused letter, recursing, and undoing the choice.",
          """
    static char[] letters;
    static boolean[] used;
    static char[] current;
    static StringBuilder out = new StringBuilder();

    static void build(int depth) {
        if (depth == letters.length) {
            out.append(new String(current)).append('\\n');
            return;
        }
        for (int i = 0; i < letters.length; i++) {
            if (used[i]) continue;
            used[i] = true;
            current[depth] = letters[i];
            build(depth + 1);
            used[i] = false;
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        letters = new char[n];
        for (int i = 0; i < n; i++) letters[i] = sc.next().charAt(0);
        Arrays.sort(letters);
        used = new boolean[n];
        current = new char[n];
        build(0);
        System.out.print(out.toString());
    }
""",
          """
    static void build(int depth) {
        if (depth == letters.length) {
            out.append(new String(current)).append('\\n');
            return;
        }
        for (int i = 0; i < letters.length; i++) {
            if (used[i]) continue;
            used[i] = true;
            current[depth] = letters[i];
            build(depth + 1);
            used[i] = false;
        }
    }
""",
          [("3\na b c", "abc\nacb\nbac\nbca\ncab\ncba"),
           ("1\nz", "z"),
           ("2\nb a", "ab\nba")],
          hint="Mark a letter used, place it, recurse, then unmark it — that undo is what makes the next branch see a clean slate.")

_chal_cls("pruning", "pruning-challenge", "Subset sum with pruning", "Medium",
          "The input is `n target` then `n` positive integers. Print `true` if some subset sums to exactly `target`, else `false`. Sort descending and prune two ways: stop a branch once the running sum exceeds `target`, and stop it when even taking every remaining number cannot reach `target`.",
          """
    static int[] a;
    static long[] suffix;
    static long target;

    static boolean search(int i, long sum) {
        if (sum == target) return true;
        if (sum > target) return false;
        if (i == a.length) return false;
        if (sum + suffix[i] < target) return false;
        return search(i + 1, sum + a[i]) || search(i + 1, sum);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        target = sc.nextLong();
        a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        Arrays.sort(a);
        for (int i = 0; i < n / 2; i++) {
            int tmp = a[i];
            a[i] = a[n - 1 - i];
            a[n - 1 - i] = tmp;
        }
        suffix = new long[n + 1];
        for (int i = n - 1; i >= 0; i--) suffix[i] = suffix[i + 1] + a[i];
        System.out.println(search(0, 0));
    }
""",
          """
    static boolean search(int i, long sum) {
        if (sum == target) return true;
        if (sum > target) return false;
        if (i == a.length) return false;
        if (sum + suffix[i] < target) return false;
        return search(i + 1, sum + a[i]) || search(i + 1, sum);
    }
""",
          [("5 9\n3 34 4 12 5", "true"), ("5 30\n3 34 4 12 5", "false"),
           ("1 7\n7", "true"), ("1 7\n8", "false"),
           ("4 19\n3 34 4 12", "true"), ("3 0\n1 2 3", "true")],
          hint="suffix[i] is the sum of everything from i onward — if sum + suffix[i] is still short of the target, no choice below can save the branch.")


# ===========================================================================
# Graphs — every challenge reads `n m` then `m` edge lines, so the parsing
# stays the same and only the algorithm changes.
# ===========================================================================

_chal("graph_repr", "graph_repr-challenge", "Build an adjacency list", "Easy",
      "The input is `n m` then `m` lines each holding an undirected edge `u v` (vertices are `0..n-1`). Build an adjacency list, then print one line per vertex: the vertex, a colon and a space, then its neighbours in ASCENDING order, space-separated. A vertex with no neighbours prints just `3: `.",
      """
      int n = sc.nextInt();
      int m = sc.nextInt();
      List<List<Integer>> adj = new ArrayList<>();
      for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
      for (int i = 0; i < m; i++) {
          int u = sc.nextInt();
          int v = sc.nextInt();
          adj.get(u).add(v);
          adj.get(v).add(u);
      }
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < n; i++) {
          Collections.sort(adj.get(i));
          sb.append(i).append(": ");
          for (int j = 0; j < adj.get(i).size(); j++) {
              if (j > 0) sb.append(' ');
              sb.append(adj.get(i).get(j));
          }
          sb.append('\\n');
      }
      System.out.print(sb.toString());
      """,
      [("3 2\n0 1\n1 2", "0: 1\n1: 0 2\n2: 1"),
       ("4 2\n0 1\n0 2", "0: 1 2\n1: 0\n2: 0\n3:"),
       ("1 0", "0:"),
       ("2 1\n1 0", "0: 1\n1: 0")],
      hint="An undirected edge goes in BOTH lists. Sorting each list at the end makes the output order predictable.")

_chal("bfs", "bfs-challenge", "Shortest hop count", "Medium",
      "The input is `n m start` then `m` undirected edges `u v`. Print the number of edges on the shortest path from `start` to every vertex `0..n-1`, one per line, using `-1` for unreachable vertices. BFS from `start` — the first time you reach a vertex is already the shortest way.",
      """
      int n = sc.nextInt();
      int m = sc.nextInt();
      int start = sc.nextInt();
      List<List<Integer>> adj = new ArrayList<>();
      for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
      for (int i = 0; i < m; i++) {
          int u = sc.nextInt();
          int v = sc.nextInt();
          adj.get(u).add(v);
          adj.get(v).add(u);
      }
      int[] dist = new int[n];
      Arrays.fill(dist, -1);
      ArrayDeque<Integer> q = new ArrayDeque<>();
      dist[start] = 0;
      q.add(start);
      while (!q.isEmpty()) {
          int u = q.poll();
          for (int v : adj.get(u)) {
              if (dist[v] == -1) {
                  dist[v] = dist[u] + 1;
                  q.add(v);
              }
          }
      }
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < n; i++) sb.append(dist[i]).append('\\n');
      System.out.print(sb.toString());
      """,
      [("4 3 0\n0 1\n1 2\n2 3", "0\n1\n2\n3"),
       ("4 2 0\n0 1\n2 3", "0\n1\n-1\n-1"),
       ("1 0 0", "0"),
       ("5 4 2\n0 1\n1 2\n2 3\n3 4", "2\n1\n0\n1\n2")],
      hint="Mark a vertex the moment you enqueue it, not when you dequeue it — otherwise it can enter the queue twice.")

_chal("flood_fill", "flood_fill-challenge", "Count islands", "Medium",
      "The input is `r c` then an `r` × `c` grid of `0` (water) and `1` (land). Print how many islands there are — maximal groups of `1`s connected up, down, left or right. Flood-fill each unvisited land cell and count how many fills you start.",
      """
      int r = sc.nextInt();
      int c = sc.nextInt();
      int[][] g = new int[r][c];
      for (int i = 0; i < r; i++) {
          for (int j = 0; j < c; j++) g[i][j] = sc.nextInt();
      }
      int[] dr = {1, -1, 0, 0};
      int[] dc = {0, 0, 1, -1};
      int islands = 0;
      for (int i = 0; i < r; i++) {
          for (int j = 0; j < c; j++) {
              if (g[i][j] != 1) continue;
              islands++;
              ArrayDeque<int[]> stack = new ArrayDeque<>();
              stack.push(new int[]{i, j});
              g[i][j] = 0;
              while (!stack.isEmpty()) {
                  int[] cur = stack.pop();
                  for (int d = 0; d < 4; d++) {
                      int ni = cur[0] + dr[d];
                      int nj = cur[1] + dc[d];
                      if (ni < 0 || ni >= r || nj < 0 || nj >= c) continue;
                      if (g[ni][nj] != 1) continue;
                      g[ni][nj] = 0;
                      stack.push(new int[]{ni, nj});
                  }
              }
          }
      }
      System.out.println(islands);
      """,
      [("3 3\n1 1 0\n0 1 0\n0 0 1", "2"),
       ("2 2\n0 0\n0 0", "0"),
       ("1 5\n1 0 1 0 1", "3"),
       ("3 3\n1 1 1\n1 1 1\n1 1 1", "1"),
       ("4 4\n1 0 0 1\n0 0 0 0\n0 1 1 0\n0 1 0 0", "3")],
      hint="Sink each cell (set it to 0) as you visit it so the fill cannot revisit it and the outer loop only starts one fill per island.")

_chal("indegree", "indegree-challenge", "In-degree table", "Easy",
      "The input is `n m` then `m` DIRECTED edges `u v` (meaning `u -> v`). Print each vertex's in-degree — how many edges point AT it — one per line, then on a final line the vertices with in-degree 0, space-separated in ascending order (or `none`).",
      """
      int n = sc.nextInt();
      int m = sc.nextInt();
      int[] indeg = new int[n];
      for (int i = 0; i < m; i++) {
          sc.nextInt();
          int v = sc.nextInt();
          indeg[v]++;
      }
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < n; i++) sb.append(indeg[i]).append('\\n');
      StringBuilder roots = new StringBuilder();
      for (int i = 0; i < n; i++) {
          if (indeg[i] == 0) {
              if (roots.length() > 0) roots.append(' ');
              roots.append(i);
          }
      }
      sb.append(roots.length() == 0 ? "none" : roots.toString());
      System.out.println(sb.toString());
      """,
      [("3 2\n0 1\n1 2", "0\n1\n1\n0"),
       ("3 3\n0 1\n1 2\n2 0", "1\n1\n1\nnone"),
       ("4 2\n0 2\n1 2", "0\n0\n2\n0\n0 1 3"),
       ("1 0", "0\n0")],
      hint="Only the destination of each directed edge gets counted — read the source and throw it away.")

_chal("topo", "topo-challenge", "Topological order", "Medium",
      "The input is `n m` then `m` directed edges `u v` meaning `u` must come before `v`. Print one valid topological order on a single line, space-separated, always taking the SMALLEST available vertex next so the answer is unique. If the graph has a cycle, print `cycle`.",
      """
      int n = sc.nextInt();
      int m = sc.nextInt();
      List<List<Integer>> adj = new ArrayList<>();
      for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
      int[] indeg = new int[n];
      for (int i = 0; i < m; i++) {
          int u = sc.nextInt();
          int v = sc.nextInt();
          adj.get(u).add(v);
          indeg[v]++;
      }
      PriorityQueue<Integer> ready = new PriorityQueue<>();
      for (int i = 0; i < n; i++) {
          if (indeg[i] == 0) ready.add(i);
      }
      StringBuilder sb = new StringBuilder();
      int placed = 0;
      while (!ready.isEmpty()) {
          int u = ready.poll();
          placed++;
          if (sb.length() > 0) sb.append(' ');
          sb.append(u);
          for (int v : adj.get(u)) {
              indeg[v]--;
              if (indeg[v] == 0) ready.add(v);
          }
      }
      System.out.println(placed == n ? sb.toString() : "cycle");
      """,
      [("4 3\n0 1\n1 2\n2 3", "0 1 2 3"),
       ("3 3\n0 1\n1 2\n2 0", "cycle"),
       ("4 2\n1 0\n3 2", "1 0 3 2"),
       ("2 0", "0 1"),
       ("5 4\n0 2\n1 2\n2 3\n2 4", "0 1 2 3 4")],
      hint="Kahn's algorithm: repeatedly take a vertex with in-degree 0 and decrement its neighbours. If fewer than n get placed, something was stuck in a cycle.")

_chal("graph_cycle", "graph_cycle-challenge", "Cycle in a directed graph", "Medium",
      "The input is `n m` then `m` directed edges `u v`. Print `true` if the graph contains a directed cycle, `false` otherwise. (Kahn's algorithm answers this: a graph is acyclic exactly when a topological order can place every vertex.)",
      """
      int n = sc.nextInt();
      int m = sc.nextInt();
      List<List<Integer>> adj = new ArrayList<>();
      for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
      int[] indeg = new int[n];
      for (int i = 0; i < m; i++) {
          int u = sc.nextInt();
          int v = sc.nextInt();
          adj.get(u).add(v);
          indeg[v]++;
      }
      ArrayDeque<Integer> ready = new ArrayDeque<>();
      for (int i = 0; i < n; i++) {
          if (indeg[i] == 0) ready.add(i);
      }
      int placed = 0;
      while (!ready.isEmpty()) {
          int u = ready.poll();
          placed++;
          for (int v : adj.get(u)) {
              indeg[v]--;
              if (indeg[v] == 0) ready.add(v);
          }
      }
      System.out.println(placed != n);
      """,
      [("3 3\n0 1\n1 2\n2 0", "true"),
       ("3 2\n0 1\n1 2", "false"),
       ("1 1\n0 0", "true"),
       ("4 3\n0 1\n0 2\n1 3", "false"),
       ("5 5\n0 1\n1 2\n2 3\n3 1\n3 4", "true")],
      hint="Count how many vertices the peeling process manages to remove. Anything left behind is trapped in a cycle.")

_chal_cls("union_find", "union_find-challenge", "Count connected components", "Medium",
          "The input is `n m` then `m` undirected edges `u v`. Print the number of connected components, then on the next line the size of the largest one. Use union-find — the `find` and `union` helpers are yours to write.",
          """
    static int[] parent;
    static int[] size;

    static int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }

    static void union(int a, int b) {
        int ra = find(a);
        int rb = find(b);
        if (ra == rb) return;
        if (size[ra] < size[rb]) {
            int tmp = ra;
            ra = rb;
            rb = tmp;
        }
        parent[rb] = ra;
        size[ra] += size[rb];
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        parent = new int[n];
        size = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            size[i] = 1;
        }
        for (int i = 0; i < m; i++) union(sc.nextInt(), sc.nextInt());
        int components = 0;
        int largest = 0;
        for (int i = 0; i < n; i++) {
            if (find(i) == i) {
                components++;
                largest = Math.max(largest, size[i]);
            }
        }
        System.out.println(components);
        System.out.println(largest);
    }
""",
          """
    static int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }

    static void union(int a, int b) {
        int ra = find(a);
        int rb = find(b);
        if (ra == rb) return;
        if (size[ra] < size[rb]) {
            int tmp = ra;
            ra = rb;
            rb = tmp;
        }
        parent[rb] = ra;
        size[ra] += size[rb];
    }
""",
          [("5 3\n0 1\n1 2\n3 4", "2\n3"),
           ("4 0", "4\n1"),
           ("3 3\n0 1\n1 2\n0 2", "1\n3"),
           ("6 3\n0 1\n2 3\n4 5", "3\n2"),
           ("1 0", "1\n1")],
          hint="Halving the path inside find keeps the trees flat. Attach the smaller root under the larger so the sizes stay meaningful.")

_chal("dijkstra", "dijkstra-challenge", "Cheapest route", "Medium",
      "The input is `n m start` then `m` lines `u v w` — an undirected edge of non-negative weight `w`. Print the cheapest total weight from `start` to every vertex `0..n-1`, one per line, using `-1` for unreachable ones. Use a priority queue keyed by distance.",
      """
      int n = sc.nextInt();
      int m = sc.nextInt();
      int start = sc.nextInt();
      List<List<int[]>> adj = new ArrayList<>();
      for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
      for (int i = 0; i < m; i++) {
          int u = sc.nextInt();
          int v = sc.nextInt();
          int w = sc.nextInt();
          adj.get(u).add(new int[]{v, w});
          adj.get(v).add(new int[]{u, w});
      }
      long[] dist = new long[n];
      Arrays.fill(dist, Long.MAX_VALUE);
      dist[start] = 0;
      PriorityQueue<long[]> pq = new PriorityQueue<>((x, y) -> Long.compare(x[0], y[0]));
      pq.add(new long[]{0, start});
      while (!pq.isEmpty()) {
          long[] cur = pq.poll();
          int u = (int) cur[1];
          if (cur[0] > dist[u]) continue;
          for (int[] e : adj.get(u)) {
              long nd = cur[0] + e[1];
              if (nd < dist[e[0]]) {
                  dist[e[0]] = nd;
                  pq.add(new long[]{nd, e[0]});
              }
          }
      }
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < n; i++) {
          sb.append(dist[i] == Long.MAX_VALUE ? -1 : dist[i]).append('\\n');
      }
      System.out.print(sb.toString());
      """,
      [("4 4 0\n0 1 1\n1 2 2\n0 2 5\n2 3 1", "0\n1\n3\n4"),
       ("3 1 0\n0 1 7", "0\n7\n-1"),
       ("1 0 0", "0"),
       ("4 3 0\n0 1 10\n1 2 10\n2 3 10", "0\n10\n20\n30"),
       ("3 3 0\n0 1 4\n1 2 1\n0 2 2", "0\n3\n2")],
      hint="Skip a popped entry whose stored distance is already worse than dist[u] — that lazy deletion is what keeps the heap correct without a decrease-key.")

_chal("bellman_ford", "bellman_ford-challenge", "Negative-weight shortest paths", "Medium",
      "The input is `n m start` then `m` DIRECTED edges `u v w` where `w` may be negative. Relax every edge `n - 1` times, then print the distance from `start` to each vertex (`-1` for unreachable). If one more relaxation round still improves something, print `negative cycle` instead — nothing else.",
      """
      int n = sc.nextInt();
      int m = sc.nextInt();
      int start = sc.nextInt();
      int[][] edges = new int[m][3];
      for (int i = 0; i < m; i++) {
          edges[i][0] = sc.nextInt();
          edges[i][1] = sc.nextInt();
          edges[i][2] = sc.nextInt();
      }
      final long INF = Long.MAX_VALUE / 4;
      long[] dist = new long[n];
      Arrays.fill(dist, INF);
      dist[start] = 0;
      for (int round = 0; round < n - 1; round++) {
          for (int[] e : edges) {
              if (dist[e[0]] < INF && dist[e[0]] + e[2] < dist[e[1]]) {
                  dist[e[1]] = dist[e[0]] + e[2];
              }
          }
      }
      boolean negative = false;
      for (int[] e : edges) {
          if (dist[e[0]] < INF && dist[e[0]] + e[2] < dist[e[1]]) negative = true;
      }
      if (negative) {
          System.out.println("negative cycle");
      } else {
          StringBuilder sb = new StringBuilder();
          for (int i = 0; i < n; i++) sb.append(dist[i] >= INF ? -1 : dist[i]).append('\\n');
          System.out.print(sb.toString());
      }
      """,
      [("3 3 0\n0 1 4\n0 2 5\n1 2 -3", "0\n4\n1"),
       ("3 3 0\n0 1 1\n1 2 -1\n2 1 -1", "negative cycle"),
       ("3 1 0\n0 1 2", "0\n2\n-1"),
       ("1 0 0", "0"),
       ("4 4 0\n0 1 1\n1 2 1\n2 3 1\n0 3 10", "0\n1\n2\n3")],
      hint="Guard every relaxation with 'is the source reachable yet' — otherwise INF + a negative weight looks like an improvement.")

_chal("mst", "mst-challenge", "Minimum spanning tree weight", "Medium",
      "The input is `n m` then `m` undirected edges `u v w`. Print the total weight of a minimum spanning tree, or `disconnected` if no spanning tree exists. Sort the edges by weight and add each one that joins two different components (Kruskal).",
      """
      int n = sc.nextInt();
      int m = sc.nextInt();
      int[][] edges = new int[m][3];
      for (int i = 0; i < m; i++) {
          edges[i][0] = sc.nextInt();
          edges[i][1] = sc.nextInt();
          edges[i][2] = sc.nextInt();
      }
      Arrays.sort(edges, (x, y) -> Integer.compare(x[2], y[2]));
      int[] parent = new int[n];
      for (int i = 0; i < n; i++) parent[i] = i;
      long total = 0;
      int joined = 0;
      for (int[] e : edges) {
          int ra = e[0];
          while (parent[ra] != ra) ra = parent[ra];
          int rb = e[1];
          while (parent[rb] != rb) rb = parent[rb];
          if (ra == rb) continue;
          parent[rb] = ra;
          total += e[2];
          joined++;
      }
      System.out.println(joined == n - 1 ? String.valueOf(total) : "disconnected");
      """,
      [("4 5\n0 1 1\n1 2 2\n2 3 3\n0 3 10\n0 2 4", "6"),
       ("4 2\n0 1 1\n2 3 1", "disconnected"),
       ("1 0", "0"),
       ("3 3\n0 1 5\n1 2 5\n0 2 5", "10"),
       ("5 6\n0 1 2\n0 3 6\n1 2 3\n1 3 8\n1 4 5\n2 4 7", "16")],
      hint="A spanning tree on n vertices has exactly n - 1 edges — if you finish with fewer, the graph was never connected.")


# ===========================================================================
# Math
# ===========================================================================

_chal("math_digits", "math_digits-challenge", "Palindrome number", "Easy",
      "The input is one non-negative integer `n`. Without converting it to a String, build its reverse by peeling digits with `% 10` and `/ 10`. Print the reversed number on the first line and whether `n` is a palindrome on the second.",
      """
      long n = sc.nextLong();
      long rest = n;
      long reversed = 0;
      while (rest > 0) {
          reversed = reversed * 10 + rest % 10;
          rest /= 10;
      }
      System.out.println(reversed);
      System.out.println(reversed == n);
      """,
      [("12321", "12321\ntrue"), ("1234", "4321\nfalse"),
       ("0", "0\ntrue"), ("7", "7\ntrue"), ("1000", "1\nfalse")],
      hint="Each pass moves the built-up answer one place left (× 10) and drops the last digit of what remains in.")

_chal("number_theory", "number_theory-challenge", "GCD, LCM and primality", "Easy",
      "The input is two positive integers `a b`. Print three lines: their greatest common divisor (Euclid's algorithm), their least common multiple (`a / gcd * b`, in `long` so it does not overflow), and whether `a` is prime.",
      """
      long a = sc.nextLong();
      long b = sc.nextLong();
      long x = a;
      long y = b;
      while (y != 0) {
          long t = x % y;
          x = y;
          y = t;
      }
      long gcd = x;
      long lcm = a / gcd * b;
      boolean prime = a >= 2;
      for (long d = 2; d * d <= a; d++) {
          if (a % d == 0) {
              prime = false;
              break;
          }
      }
      System.out.println(gcd);
      System.out.println(lcm);
      System.out.println(prime);
      """,
      [("12 18", "6\n36\nfalse"), ("7 5", "1\n35\ntrue"),
       ("1 1", "1\n1\nfalse"), ("100000 99999", "1\n9999900000\nfalse"),
       ("13 26", "13\n26\ntrue")],
      hint="Divide before you multiply for the LCM, and stop trial division at d * d > a — beyond that any factor would already have shown up.")

_chal("modulo", "modulo-challenge", "Modular power", "Medium",
      "The input is `base exponent modulus`. Print `base^exponent mod modulus` using fast exponentiation by squaring — square the base and halve the exponent, taking the modulus at every step so nothing overflows a `long`.",
      """
      long base = sc.nextLong();
      long exp = sc.nextLong();
      long mod = sc.nextLong();
      long result = 1 % mod;
      base %= mod;
      while (exp > 0) {
          if ((exp & 1) == 1) result = result * base % mod;
          base = base * base % mod;
          exp >>= 1;
      }
      System.out.println(result);
      """,
      [("2 10 1000000007", "1024"), ("3 0 7", "1"),
       ("5 3 13", "8"), ("2 62 1000000007", "145586002"),
       ("10 9 1", "0"), ("7 1 5", "2")],
      hint="Reduce mod at every multiplication. result starts at 1 % mod so a modulus of 1 still gives 0.")
