# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Java core-concept drills, batch 2 — backfills 10 more previously lesson-only
# (or entirely blank) concepts:
#   Math:            math_digits, number_theory, modulo   (completes Math)
#   Arrays:          prefix_sum                            (+ writes its lesson)
#   Foundations:     bit_manip                             (+ writes its lesson)
#   Searching&Sort:  greedy                                (completes category)
#   Recursion & DP:  dp, recurrence
#   Data Structures: heap
#   Graphs:          bfs
#
# exec()'d inside gen_seed.py's namespace (hook after java_core_drills.py).
# Reuses ex() and prog(); adds lessons for the two concepts that shipped blank.
# Every solution is a self-contained stdin/stdout Java program proven by
# tests/verify_exercises.rs through the real judge. No SEED_VERSION bump.
# ---------------------------------------------------------------------------


# --- lessons for the two concepts that shipped with no lesson text ----------
LESSONS.update({
    "prefix_sum": """### Worked example
To answer "sum of elements from index 1 to 3" instantly, precompute running totals. With `a = [1, 2, 3, 4, 5]` the prefix array is `[0, 1, 3, 6, 10, 15]` (length n+1). The range sum `a[1..3]` is `prefix[4] - prefix[1] = 10 - 1 = 9` — one subtraction, no loop.

### In code (Java)
```java
int[] a = {1, 2, 3, 4, 5};
long[] prefix = new long[a.length + 1];
for (int i = 0; i < a.length; i++) prefix[i + 1] = prefix[i] + a[i];
long rangeSum = prefix[4] - prefix[1]; // sum of a[1..3] = 9
```

### Watch out for
- `prefix[i]` is the sum of the first `i` elements, so `prefix[0] = 0` and `prefix[n]` is the grand total.
- The inclusive range `[l, r]` is `prefix[r + 1] - prefix[l]`.
- Use a `long[]` prefix — repeated sums overflow `int` quickly.
""",
    "bit_manip": """### Worked example
Bitwise operators act on the binary form of an integer. `5` is `101`, so bits 0 and 2 are set. `5 & 1` (AND with `001`) is `1`, telling you the lowest bit is on — i.e. the number is odd.

### In code (Java)
```java
int n = 5;               // 101
n & 1;                   // 1  — lowest bit (odd?)
n >> 1;                  // 2  — divide by 2 (drop lowest bit)
n << 1;                  // 10 — multiply by 2
Integer.bitCount(n);     // 2  — number of set bits
n & (n - 1);             // 4  — clears the lowest set bit
```

### Watch out for
- `&` AND, `|` OR, `^` XOR, `~` NOT, `<<` / `>>` shift, `>>>` unsigned shift.
- Test bit `i` with `(n >> i) & 1`; set it with `n | (1 << i)`.
- For `x > 0`, `(x & (x - 1)) == 0` means `x` is a power of two.
""",
})


JAVA_CORE2_EXERCISES = {
    # === Math =============================================================
    "math_digits": [
        ex(
            "math_digits-sum", "Sum the digits",
            "Replace `____` with the expression for the last digit of `n`, so the loop adds up every digit.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int sum = 0;\n"
                "        while (n > 0) {\n"
                "            sum += n % 10;\n"
                "            n /= 10;\n"
                "        }\n"
                "        System.out.println(sum);"),
            ["n % 10"],
            [("123", "6"), ("9", "9"), ("100", "1")],
            hint="n % 10 peels off the last digit; n /= 10 removes it.",
        ),
        ex(
            "math_digits-count", "Count the digits",
            "Replace `____` with the statement that drops the last digit of `n` each pass, so the loop counts how many digits it has.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int count = 0;\n"
                "        while (n > 0) {\n"
                "            count++;\n"
                "            n /= 10;\n"
                "        }\n"
                "        System.out.println(count);"),
            ["n /= 10;"],
            [("123", "3"), ("7", "1"), ("1000", "4")],
            hint="Integer division n /= 10 shortens the number by one digit.",
        ),
        ex(
            "math_digits-reverse", "Reverse the digits",
            "Write the solution: build the reversed number by repeatedly taking the last digit of `n` and appending it (`123` -> `321`).",
            prog(
                "        int n = sc.nextInt();\n"
                "        int rev = 0;\n"
                "        while (n > 0) {\n"
                "            rev = rev * 10 + n % 10;\n"
                "            n /= 10;\n"
                "        }\n"
                "        System.out.println(rev);"),
            ["        int rev = 0;\n"
             "        while (n > 0) {\n"
             "            rev = rev * 10 + n % 10;\n"
             "            n /= 10;\n"
             "        }\n"
             "        System.out.println(rev);"],
            [("123", "321"), ("1230", "321"), ("5", "5")],
            hint="rev = rev * 10 + (last digit) shifts the built-up number left and adds the new digit.",
        ),
    ],
    "number_theory": [
        ex(
            "number_theory-gcd", "Euclid's GCD",
            "Replace `____` with the recursive step of Euclid's algorithm (`gcd(b, a % b)`), with the base case `b == 0`.",
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static long gcd(long a, long b) {\n"
            "        return b == 0 ? a : gcd(b, a % b);\n"
            "    }\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        long a = sc.nextLong();\n"
            "        long b = sc.nextLong();\n"
            "        System.out.println(gcd(a, b));\n"
            "    }\n"
            "}\n",
            ["return b == 0 ? a : gcd(b, a % b);"],
            [("12 18", "6"), ("7 5", "1"), ("100 10", "10")],
            hint="gcd(a, b) = gcd(b, a % b), and gcd(a, 0) = a.",
        ),
        ex(
            "number_theory-prime", "Is it prime?",
            "Replace `____` with the divisibility test that, when true, proves `n` is not prime.",
            prog(
                "        int n = sc.nextInt();\n"
                "        boolean prime = n >= 2;\n"
                "        for (int d = 2; (long) d * d <= n; d++) {\n"
                "            if (n % d == 0) { prime = false; break; }\n"
                "        }\n"
                "        System.out.println(prime);"),
            ["n % d == 0"],
            [("7", "true"), ("12", "false"), ("1", "false")],
            hint="If n % d == 0 for some d in [2, sqrt(n)], then d divides n, so n isn't prime.",
        ),
        ex(
            "number_theory-lcm", "Least common multiple",
            "Write the solution: compute `lcm(a, b)` as `a / gcd(a, b) * b` (divide before multiplying to avoid overflow) and print it.",
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static long gcd(long a, long b) {\n"
            "        return b == 0 ? a : gcd(b, a % b);\n"
            "    }\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        long a = sc.nextLong();\n"
            "        long b = sc.nextLong();\n"
            "        long result = a / gcd(a, b) * b;\n"
            "        System.out.println(result);\n"
            "    }\n"
            "}\n",
            ["        long result = a / gcd(a, b) * b;\n"
             "        System.out.println(result);"],
            [("4 6", "12"), ("3 5", "15"), ("10 10", "10")],
            hint="lcm(a, b) = a / gcd(a, b) * b — dividing first keeps the intermediate value small.",
        ),
    ],
    "modulo": [
        ex(
            "modulo-reduce", "Drop the extra turns",
            "Rotating a length-`n` array by `k` is the same as rotating by `k % n`. Replace `____` with that reduced amount.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int k = sc.nextInt();\n"
                "        System.out.println(k % n);"),
            ["k % n"],
            [("5 7", "2"), ("3 3", "0"), ("10 4", "4")],
            hint="k % n removes whole cycles, leaving the effective offset in [0, n).",
        ),
        ex(
            "modulo-floormod", "Safe modulo of negatives",
            "Java's `%` can be negative. Replace `____` with the call that always returns a non-negative remainder in `[0, n)`.",
            prog(
                "        int x = sc.nextInt();\n"
                "        int n = sc.nextInt();\n"
                "        System.out.println(Math.floorMod(x, n));"),
            ["Math.floorMod(x, n)"],
            [("-1 5", "4"), ("7 5", "2"), ("-7 3", "2")],
            hint="Math.floorMod(x, n) wraps negatives correctly, unlike the % operator.",
        ),
        ex(
            "modulo-clock", "Wrap around a 24-hour clock",
            "Write the solution: given a start hour and hours to add, print the resulting hour on a 24-hour clock (it must stay in 0..23).",
            prog(
                "        int start = sc.nextInt();\n"
                "        int add = sc.nextInt();\n"
                "        int hour = Math.floorMod(start + add, 24);\n"
                "        System.out.println(hour);"),
            ["        int hour = Math.floorMod(start + add, 24);\n"
             "        System.out.println(hour);"],
            [("22 5", "3"), ("0 0", "0"), ("10 40", "2")],
            hint="Add the hours, then reduce modulo 24 so the clock wraps past midnight.",
        ),
    ],
    # === Arrays — prefix sums =============================================
    "prefix_sum": [
        ex(
            "prefix_sum-build", "Build the prefix array",
            "Replace `____` with the line that fills `prefix[i + 1]` as the running total (previous prefix plus the next value).",
            prog(
                "        int n = sc.nextInt();\n"
                "        long[] prefix = new long[n + 1];\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            prefix[i + 1] = prefix[i] + sc.nextInt();\n"
                "        }\n"
                "        int l = sc.nextInt();\n"
                "        int r = sc.nextInt();\n"
                "        System.out.println(prefix[r + 1] - prefix[l]);"),
            ["prefix[i + 1] = prefix[i] + sc.nextInt();"],
            [("5\n1 2 3 4 5\n1 3", "9"), ("3\n10 20 30\n0 2", "60"), ("4\n1 1 1 1\n2 3", "2")],
            hint="Each prefix entry is the one before it plus the current element.",
        ),
        ex(
            "prefix_sum-total", "The grand total",
            "`prefix[n]` holds the sum of all `n` elements. Replace `____` with that value.",
            prog(
                "        int n = sc.nextInt();\n"
                "        long[] prefix = new long[n + 1];\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            prefix[i + 1] = prefix[i] + sc.nextInt();\n"
                "        }\n"
                "        System.out.println(prefix[n]);"),
            ["prefix[n]"],
            [("5\n1 2 3 4 5", "15"), ("3\n10 20 30", "60"), ("1\n7", "7")],
            hint="prefix[n] is the running total after adding every element.",
        ),
        ex(
            "prefix_sum-maxrange", "Best range among queries",
            "After the values comes a count `q` and then `q` ranges `l r`. Write the solution: print the largest range sum among the queries (each is `prefix[r + 1] - prefix[l]`).",
            prog(
                "        int n = sc.nextInt();\n"
                "        long[] prefix = new long[n + 1];\n"
                "        for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + sc.nextInt();\n"
                "        int q = sc.nextInt();\n"
                "        long best = Long.MIN_VALUE;\n"
                "        for (int i = 0; i < q; i++) {\n"
                "            int l = sc.nextInt();\n"
                "            int r = sc.nextInt();\n"
                "            best = Math.max(best, prefix[r + 1] - prefix[l]);\n"
                "        }\n"
                "        System.out.println(best);"),
            ["        int q = sc.nextInt();\n"
             "        long best = Long.MIN_VALUE;\n"
             "        for (int i = 0; i < q; i++) {\n"
             "            int l = sc.nextInt();\n"
             "            int r = sc.nextInt();\n"
             "            best = Math.max(best, prefix[r + 1] - prefix[l]);\n"
             "        }\n"
             "        System.out.println(best);"],
            [("5\n1 2 3 4 5\n2\n0 4\n1 2", "15"), ("3\n10 20 30\n2\n0 0\n1 2", "50"), ("4\n1 1 1 1\n1\n0 3", "4")],
            hint="Each query is one subtraction on the prefix array; keep the maximum.",
        ),
    ],
    # === Foundations — bit manipulation ===================================
    "bit_manip": [
        ex(
            "bit_manip-testbit", "Is a bit set?",
            "Replace `____` with the expression that is true when bit `i` of `n` is 1.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int i = sc.nextInt();\n"
                "        boolean set = ((n >> i) & 1) == 1;\n"
                "        System.out.println(set);"),
            ["((n >> i) & 1) == 1"],
            [("5 0", "true"), ("5 1", "false"), ("5 2", "true")],
            hint="Shift bit i down to position 0 with n >> i, then mask it with & 1.",
        ),
        ex(
            "bit_manip-popcount", "Count the set bits",
            "Replace `____` with the trick that clears the lowest set bit of `n`, so the loop runs once per 1-bit.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int count = 0;\n"
                "        while (n != 0) {\n"
                "            n = n & (n - 1);\n"
                "            count++;\n"
                "        }\n"
                "        System.out.println(count);"),
            ["n & (n - 1)"],
            [("5", "2"), ("7", "3"), ("8", "1")],
            hint="n & (n - 1) removes the lowest set bit; count how many times you can do it.",
        ),
        ex(
            "bit_manip-poweroftwo", "Power of two?",
            "Write the solution: print `true` when `n` is a positive power of two. A power of two has exactly one set bit.",
            prog(
                "        int n = sc.nextInt();\n"
                "        boolean pow = n > 0 && (n & (n - 1)) == 0;\n"
                "        System.out.println(pow);"),
            ["        boolean pow = n > 0 && (n & (n - 1)) == 0;\n"
             "        System.out.println(pow);"],
            [("8", "true"), ("6", "false"), ("1", "true")],
            hint="For x > 0, (x & (x - 1)) == 0 is true exactly when x has a single set bit.",
        ),
    ],
    # === Searching & Sorting — greedy =====================================
    "greedy": [
        ex(
            "greedy-coins", "Fewest coins",
            "Coins `{25, 10, 5, 1}` are tried largest-first. Replace `____` with the line that adds as many of coin `c` as fit into what remains.",
            prog(
                "        int amount = sc.nextInt();\n"
                "        int[] coins = {25, 10, 5, 1};\n"
                "        int used = 0;\n"
                "        for (int c : coins) {\n"
                "            used += amount / c;\n"
                "            amount %= c;\n"
                "        }\n"
                "        System.out.println(used);"),
            ["used += amount / c;"],
            [("30", "2"), ("41", "4"), ("99", "9")],
            hint="amount / c is how many of coin c fit; amount %= c leaves the remainder.",
        ),
        ex(
            "greedy-largest", "Largest number from digits",
            "Greedily place the biggest digits first. The digits are sorted ascending, so replace `____` with the call that flips them into descending order.",
            prog(
                "        String s = sc.next();\n"
                "        char[] d = s.toCharArray();\n"
                "        Arrays.sort(d);\n"
                "        StringBuilder sb = new StringBuilder(new String(d));\n"
                "        sb.reverse();\n"
                "        System.out.println(sb.toString());"),
            ["sb.reverse();"],
            [("312", "321"), ("1000", "1000"), ("52341", "54321")],
            hint="Sorting ascending then reversing puts the largest digit first.",
        ),
        ex(
            "greedy-cookies", "Assign cookies",
            "Children have greed factors, cookies have sizes; a child is satisfied by a cookie at least as big as their greed. Write the solution: sort both, then greedily match the smallest cookie that satisfies the least-greedy remaining child, and print how many children are satisfied.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] g = new int[n];\n"
                "        for (int i = 0; i < n; i++) g[i] = sc.nextInt();\n"
                "        int m = sc.nextInt();\n"
                "        int[] s = new int[m];\n"
                "        for (int i = 0; i < m; i++) s[i] = sc.nextInt();\n"
                "        Arrays.sort(g);\n"
                "        Arrays.sort(s);\n"
                "        int child = 0;\n"
                "        for (int j = 0; j < m && child < n; j++) {\n"
                "            if (s[j] >= g[child]) child++;\n"
                "        }\n"
                "        System.out.println(child);"),
            ["        Arrays.sort(g);\n"
             "        Arrays.sort(s);\n"
             "        int child = 0;\n"
             "        for (int j = 0; j < m && child < n; j++) {\n"
             "            if (s[j] >= g[child]) child++;\n"
             "        }\n"
             "        System.out.println(child);"],
            [("3\n1 2 3\n2\n1 1", "1"), ("2\n1 2\n3\n1 2 3", "2"), ("2\n10 20\n2\n5 5", "0")],
            hint="Sort both, then sweep the cookies; each cookie that clears the current child's greed satisfies them.",
        ),
    ],
    # === Recursion & DP — dp / recurrence =================================
    "dp": [
        ex(
            "dp-stairs", "Climbing stairs",
            "Ways to climb `n` stairs (1 or 2 steps at a time) follow `ways(i) = ways(i-1) + ways(i-2)`. Replace `____` with that transition.",
            prog(
                "        int n = sc.nextInt();\n"
                "        long a = 1, b = 1;\n"
                "        for (int i = 2; i <= n; i++) {\n"
                "            long c = a + b;\n"
                "            a = b;\n"
                "            b = c;\n"
                "        }\n"
                "        System.out.println(b);"),
            ["long c = a + b;"],
            [("2", "2"), ("5", "8"), ("1", "1")],
            hint="Each step's ways is the sum of the previous two — carry them in a and b.",
        ),
        ex(
            "dp-robber", "House robber",
            "You can't take two adjacent values. `incl`/`excl` track the best if you take or skip the current house. Replace `____` with the new 'take' value (skip-the-previous plus this house).",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] v = new int[n];\n"
                "        for (int i = 0; i < n; i++) v[i] = sc.nextInt();\n"
                "        long incl = 0, excl = 0;\n"
                "        for (int x : v) {\n"
                "            long newIncl = excl + x;\n"
                "            excl = Math.max(incl, excl);\n"
                "            incl = newIncl;\n"
                "        }\n"
                "        System.out.println(Math.max(incl, excl));"),
            ["long newIncl = excl + x;"],
            [("4\n1 2 3 1", "4"), ("3\n2 7 9", "11"), ("1\n5", "5")],
            hint="To take house x you must have skipped the previous one, so it's excl + x.",
        ),
        ex(
            "dp-coinchange", "Coin change (fewest coins)",
            "Write the solution: given an amount and a set of coin values, print the fewest coins that make the amount, or `-1` if impossible. Build `dp[a]` = fewest coins for amount `a`.",
            prog(
                "        int amount = sc.nextInt();\n"
                "        int m = sc.nextInt();\n"
                "        int[] coins = new int[m];\n"
                "        for (int i = 0; i < m; i++) coins[i] = sc.nextInt();\n"
                "        int[] dp = new int[amount + 1];\n"
                "        Arrays.fill(dp, amount + 1);\n"
                "        dp[0] = 0;\n"
                "        for (int a = 1; a <= amount; a++) {\n"
                "            for (int c : coins) {\n"
                "                if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);\n"
                "            }\n"
                "        }\n"
                "        System.out.println(dp[amount] > amount ? -1 : dp[amount]);"),
            ["        int[] dp = new int[amount + 1];\n"
             "        Arrays.fill(dp, amount + 1);\n"
             "        dp[0] = 0;\n"
             "        for (int a = 1; a <= amount; a++) {\n"
             "            for (int c : coins) {\n"
             "                if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);\n"
             "            }\n"
             "        }\n"
             "        System.out.println(dp[amount] > amount ? -1 : dp[amount]);"],
            [("11\n3\n1 2 5", "3"), ("3\n1\n2", "-1"), ("6\n2\n1 3", "2")],
            hint="dp[a] = min over coins c of dp[a - c] + 1; an untouched sentinel means 'impossible'.",
        ),
    ],
    "recurrence": [
        ex(
            "recurrence-fib", "Fibonacci",
            "Fibonacci sums the previous two terms. Replace `____` with the next term `a + b`.",
            prog(
                "        int n = sc.nextInt();\n"
                "        long a = 0, b = 1;\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            long c = a + b;\n"
                "            a = b;\n"
                "            b = c;\n"
                "        }\n"
                "        System.out.println(a);"),
            ["long c = a + b;"],
            [("0", "0"), ("7", "13"), ("10", "55")],
            hint="Advance the pair (a, b) -> (b, a + b) n times; a holds fib(n).",
        ),
        ex(
            "recurrence-tribonacci", "Tribonacci",
            "The tribonacci sequence (0, 1, 1, 2, 4, 7, 13, ...) sums the previous THREE terms. Replace `____` with that transition.",
            prog(
                "        int n = sc.nextInt();\n"
                "        long[] t = new long[Math.max(n + 1, 3)];\n"
                "        t[0] = 0; t[1] = 1; t[2] = 1;\n"
                "        for (int i = 3; i <= n; i++) {\n"
                "            t[i] = t[i - 1] + t[i - 2] + t[i - 3];\n"
                "        }\n"
                "        System.out.println(t[n]);"),
            ["t[i] = t[i - 1] + t[i - 2] + t[i - 3];"],
            [("4", "4"), ("6", "13"), ("0", "0")],
            hint="Each term is the sum of the three before it; seed t[0..2] = 0, 1, 1.",
        ),
        ex(
            "recurrence-custom", "A custom recurrence",
            "Solve `f(n) = 2*f(n-1) + 3*f(n-2)` with `f(0) = 1`, `f(1) = 2`. Write the solution: iterate bottom-up and print `f(n)`.",
            prog(
                "        int n = sc.nextInt();\n"
                "        long a = 1, b = 2;\n"
                "        if (n == 0) { System.out.println(a); return; }\n"
                "        for (int i = 2; i <= n; i++) {\n"
                "            long c = 2 * b + 3 * a;\n"
                "            a = b;\n"
                "            b = c;\n"
                "        }\n"
                "        System.out.println(b);"),
            ["        long a = 1, b = 2;\n"
             "        if (n == 0) { System.out.println(a); return; }\n"
             "        for (int i = 2; i <= n; i++) {\n"
             "            long c = 2 * b + 3 * a;\n"
             "            a = b;\n"
             "            b = c;\n"
             "        }\n"
             "        System.out.println(b);"],
            [("0", "1"), ("2", "7"), ("3", "20")],
            hint="Carry the two previous terms; each new term is 2*(previous) + 3*(one before that).",
        ),
    ],
    # === Data Structures — heap ===========================================
    "heap": [
        ex(
            "heap-minorder", "Pop in sorted order",
            "A `PriorityQueue` is a min-heap. Replace `____` with the call that removes and returns the smallest remaining item.",
            prog(
                "        int n = sc.nextInt();\n"
                "        PriorityQueue<Integer> pq = new PriorityQueue<>();\n"
                "        for (int i = 0; i < n; i++) pq.offer(sc.nextInt());\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        while (!pq.isEmpty()) sb.append(pq.poll()).append(' ');\n"
                "        System.out.println(sb.toString().trim());"),
            ["pq.poll()"],
            [("3\n5 1 3", "1 3 5"), ("1\n9", "9"), ("4\n4 3 2 1", "1 2 3 4")],
            hint="poll() always returns the current minimum of a PriorityQueue.",
        ),
        ex(
            "heap-max", "Largest element",
            "Replace `____` with the comparator that turns the default min-heap into a max-heap, so `poll()` returns the largest value.",
            prog(
                "        int n = sc.nextInt();\n"
                "        PriorityQueue<Integer> pq = new PriorityQueue<>(Comparator.reverseOrder());\n"
                "        for (int i = 0; i < n; i++) pq.offer(sc.nextInt());\n"
                "        System.out.println(pq.poll());"),
            ["Comparator.reverseOrder()"],
            [("3\n5 1 3", "5"), ("1\n9", "9"), ("4\n2 8 4 1", "8")],
            hint="Comparator.reverseOrder() makes the heap yield the maximum first.",
        ),
        ex(
            "heap-kthlargest", "Kth largest element",
            "Write the solution: keep a min-heap of size `k`; after adding each value, drop the smallest if the heap grew past `k`. The heap's minimum is then the k-th largest — print it.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int k = sc.nextInt();\n"
                "        PriorityQueue<Integer> pq = new PriorityQueue<>();\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            pq.offer(sc.nextInt());\n"
                "            if (pq.size() > k) pq.poll();\n"
                "        }\n"
                "        System.out.println(pq.poll());"),
            ["        PriorityQueue<Integer> pq = new PriorityQueue<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            pq.offer(sc.nextInt());\n"
             "            if (pq.size() > k) pq.poll();\n"
             "        }\n"
             "        System.out.println(pq.poll());"],
            [("5 2\n3 2 1 5 4", "4"), ("3 1\n7 8 9", "9"), ("4 3\n10 5 20 15", "10")],
            hint="A size-k min-heap keeps the k largest seen so far; its smallest is the k-th largest.",
        ),
    ],
    # === Graphs — BFS =====================================================
    "bfs": [
        ex(
            "bfs-expand", "Visit neighbours",
            "The graph is built as an adjacency list. Replace `____` with the step that, for an unseen neighbour `w`, marks it seen and enqueues it (mark on ENQUEUE to avoid duplicates).",
            prog(
                "        int n = sc.nextInt();\n"
                "        int m = sc.nextInt();\n"
                "        List<List<Integer>> adj = new ArrayList<>();\n"
                "        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());\n"
                "        for (int i = 0; i < m; i++) {\n"
                "            int u = sc.nextInt();\n"
                "            int v = sc.nextInt();\n"
                "            adj.get(u).add(v);\n"
                "            adj.get(v).add(u);\n"
                "        }\n"
                "        Queue<Integer> q = new ArrayDeque<>();\n"
                "        boolean[] seen = new boolean[n];\n"
                "        q.offer(0);\n"
                "        seen[0] = true;\n"
                "        int count = 0;\n"
                "        while (!q.isEmpty()) {\n"
                "            int u = q.poll();\n"
                "            count++;\n"
                "            for (int w : adj.get(u)) {\n"
                "                if (!seen[w]) { seen[w] = true; q.offer(w); }\n"
                "            }\n"
                "        }\n"
                "        System.out.println(count);"),
            ["if (!seen[w]) { seen[w] = true; q.offer(w); }"],
            [("3 2\n0 1\n1 2", "3"), ("4 2\n0 1\n2 3", "2"), ("1 0", "1")],
            hint="Only enqueue a neighbour you haven't seen, and mark it seen at that moment.",
        ),
        ex(
            "bfs-distance", "Shortest distance",
            "BFS finds shortest distances in an unweighted graph. Replace `____` with the line that sets a newly-reached node's distance to one more than the node you came from.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int m = sc.nextInt();\n"
                "        List<List<Integer>> adj = new ArrayList<>();\n"
                "        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());\n"
                "        for (int i = 0; i < m; i++) {\n"
                "            int u = sc.nextInt();\n"
                "            int v = sc.nextInt();\n"
                "            adj.get(u).add(v);\n"
                "            adj.get(v).add(u);\n"
                "        }\n"
                "        int t = sc.nextInt();\n"
                "        int[] dist = new int[n];\n"
                "        Arrays.fill(dist, -1);\n"
                "        Queue<Integer> q = new ArrayDeque<>();\n"
                "        q.offer(0);\n"
                "        dist[0] = 0;\n"
                "        while (!q.isEmpty()) {\n"
                "            int u = q.poll();\n"
                "            for (int w : adj.get(u)) {\n"
                "                if (dist[w] == -1) { dist[w] = dist[u] + 1; q.offer(w); }\n"
                "            }\n"
                "        }\n"
                "        System.out.println(dist[t]);"),
            ["dist[w] = dist[u] + 1;"],
            [("3 2\n0 1\n1 2\n2", "2"), ("4 2\n0 1\n2 3\n3", "-1"), ("2 1\n0 1\n1", "1")],
            hint="Each BFS layer is one step further, so a neighbour's distance is dist[u] + 1.",
        ),
        ex(
            "bfs-components", "Count connected components",
            "Write the solution: run a BFS from every not-yet-seen node and count how many separate components the undirected graph has.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int m = sc.nextInt();\n"
                "        List<List<Integer>> adj = new ArrayList<>();\n"
                "        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());\n"
                "        for (int i = 0; i < m; i++) {\n"
                "            int u = sc.nextInt();\n"
                "            int v = sc.nextInt();\n"
                "            adj.get(u).add(v);\n"
                "            adj.get(v).add(u);\n"
                "        }\n"
                "        boolean[] seen = new boolean[n];\n"
                "        int components = 0;\n"
                "        for (int start = 0; start < n; start++) {\n"
                "            if (seen[start]) continue;\n"
                "            components++;\n"
                "            Queue<Integer> q = new ArrayDeque<>();\n"
                "            q.offer(start);\n"
                "            seen[start] = true;\n"
                "            while (!q.isEmpty()) {\n"
                "                int u = q.poll();\n"
                "                for (int w : adj.get(u)) {\n"
                "                    if (!seen[w]) { seen[w] = true; q.offer(w); }\n"
                "                }\n"
                "            }\n"
                "        }\n"
                "        System.out.println(components);"),
            ["        boolean[] seen = new boolean[n];\n"
             "        int components = 0;\n"
             "        for (int start = 0; start < n; start++) {\n"
             "            if (seen[start]) continue;\n"
             "            components++;\n"
             "            Queue<Integer> q = new ArrayDeque<>();\n"
             "            q.offer(start);\n"
             "            seen[start] = true;\n"
             "            while (!q.isEmpty()) {\n"
             "                int u = q.poll();\n"
             "                for (int w : adj.get(u)) {\n"
             "                    if (!seen[w]) { seen[w] = true; q.offer(w); }\n"
             "                }\n"
             "            }\n"
             "        }\n"
             "        System.out.println(components);"],
            [("5 3\n0 1\n1 2\n3 4", "2"), ("4 0", "4"), ("3 2\n0 1\n1 2", "1")],
            hint="Every time you start a BFS from an unseen node you've found a new component.",
        ),
    ],
}
EXERCISES.update(JAVA_CORE2_EXERCISES)
