# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# "Price the snippet" — Big-O drills for every unit.
#
# exec'd by tools/dsa_curriculum.py after the six stage files, in the same
# namespace, so `_bigo` and `_UNITS` are already defined. Each list below is
# appended to the `bigo` of the unit with that key.
#
# WHY EVERY UNIT, AND NOT JUST `complexity`
#
# The drill started life in the complexity unit, on the argument that you can
# solve every problem there without once *stating* a cost. That argument is true
# of every unit. Knowing two pointers is O(n) is not the skill; the skill is
# seeing that a `while` nested inside a `for` is still O(n) when the inner
# pointer never moves back, and that `list.contains` inside a loop is not. Those
# traps are specific to each technique, so each unit prices its own.
#
# AUTHORING RULES
#
#   1. THE ANSWER IS THE TIGHT BOUND. Big-O is formally an upper bound, so
#      "O(n²)" is technically true of an O(n) loop. Every item here asks for the
#      tightest class, and no item offers a looser-but-true bound as a
#      distractor where that would make two options defensible.
#   2. EVERY ITEM IS A TRAP OR A CONTRAST. A snippet whose answer is obvious from
#      the shape of the loops teaches nothing; each one either hides its cost in
#      a library call or a pointer that never resets, or is paired with a
#      sibling that differs by one line and one complexity class.
#   3. THE WHY NAMES THE FIX, where there is one — the point of pricing a
#      snippet is knowing what to change.
#   4. VARIABLES ARE NAMED. `n`, `m`, `k`, `V`, `E` mean what the snippet's
#      comment says they mean; two independent sizes are never collapsed into n.
# ---------------------------------------------------------------------------

_BIGO_BY_UNIT = {
    # ---------------------------------------------------------------- stage 1
    "io-and-arithmetic": [
        _bigo(r"""
int n = sc.nextInt();
long sum = 0;
for (int i = 0; i < n; i++) sum += sc.nextInt();
System.out.println(sum);
""", "O(n)", ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            "One read per number. Reading the input is part of the cost — no program that must "
            "look at n numbers can be faster than O(n), which is why that is the floor for most "
            "problems."),
        _bigo(r"""
long total = (long) n * (n + 1) / 2;
System.out.println(total);
""", "O(1)", ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            "Arithmetic on fixed-width numbers costs the same whether `n` is 3 or 2 billion. "
            "A formula replacing a loop is the purest complexity win there is — and the `(long)` "
            "cast is what keeps it correct, not what makes it fast."),
        _bigo(r"""
String out = "";
for (int i = 0; i < n; i++) out += i + " ";
System.out.println(out);
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
            "Strings are immutable, so every `+=` copies everything built so far: 1 + 2 + … + n "
            "characters. It looks like one loop and is quadratic in the output size. Build output "
            "with a `StringBuilder`."),
        _bigo(r"""
StringBuilder sb = new StringBuilder();
for (int i = 0; i < n; i++) sb.append(i).append('\n');
System.out.print(sb);
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
            "`append` is amortised O(1): the buffer doubles when full, so the total copying is "
            "bounded by twice the final length. Same output as the `+=` loop, one complexity "
            "class cheaper — the difference is invisible at n = 100 and a timeout at n = 10⁵."),
        _bigo(r"""
int r = sc.nextInt(), c = sc.nextInt();
int[][] g = new int[r][c];
for (int i = 0; i < r; i++)
    for (int j = 0; j < c; j++) g[i][j] = sc.nextInt();
""", "O(r·c)", ["O(r + c)", "O(r·c)", "O(max(r, c)²)", "O(r² · c²)"],
            "Two independent sizes stay two variables. Calling this O(n²) is only right when the "
            "grid is square — and it is *linear* in the input, because the input is r·c numbers."),
    ],
    "branching": [
        _bigo(r"""
if (score >= 90) grade = 'A';
else if (score >= 80) grade = 'B';
else if (score >= 70) grade = 'C';
else grade = 'F';
""", "O(1)", ["O(1)", "O(log n)", "O(n)", "O(score)"],
            "The number of comparisons is fixed by the code, not by the input. A chain of ten "
            "`else if`s is still O(1); a chain whose length depends on the data would not be."),
        _bigo(r"""
for (int i = 0; i < n; i++) {
    if (i == 0) {
        for (int j = 0; j < n; j++) total += a[j];
    } else {
        total += a[i];
    }
}
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "The inner loop is inside a branch taken exactly once, so it adds n, not n·n. Price "
            "how often a branch runs, not whether it contains a loop."),
        _bigo(r"""
for (int i = 0; i < n; i++)
    if (a[i] % 2 == 0)
        for (int j = 0; j < n; j++) work++;
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(√n)"],
            "Complexity is the worst case unless you say otherwise, and the worst case is every "
            "element even. \"It only runs for half of them\" is a factor of ½, which does not "
            "change the class."),
        _bigo(r"""
for (int i = 0; i < n; i++)
    if (a[i] == target) return i;
return -1;
""", "O(n)", ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            "The early return makes the *best* case O(1) — target at index 0 — but the question "
            "without a qualifier is the worst case: the target absent, every element checked."),
        _bigo(r"""
int[] sides = {x, y, z};
Arrays.sort(sides);
boolean ok = sides[0] + sides[1] > sides[2];
""", "O(1)", ["O(1)", "O(n log n)", "O(log n)", "O(n)"],
            "Sorting is O(n log n) in the *length of the array*, and the length is 3. Sorting a "
            "fixed-size array is a constant amount of work — often the clearest way to avoid a "
            "tangle of comparisons."),
    ],
    "loops-and-digits": [
        _bigo(r"""
int count = 0;
for (int d = 1; d <= n; d++)
    if (n % d == 0) count++;
""", "O(n)", ["O(√n)", "O(n)", "O(log n)", "O(n²)"],
            "One iteration per candidate divisor up to the value n. Divisors come in pairs "
            "`(d, n/d)`, so stopping at `d * d <= n` and counting both halves makes it O(√n) — "
            "that trick belongs to the number-theory unit."),
        _bigo(r"""
int steps = 0;
for (long p = 1; p <= n; p *= 2) steps++;
""", "O(log n)", ["O(n)", "O(log n)", "O(√n)", "O(1)"],
            "`p` doubles, so it passes n after ⌊log₂ n⌋ + 1 steps. Whenever the loop variable is "
            "*multiplied* or *divided*, look for a log."),
        _bigo(r"""
int count = 0;
for (int i = 0; i * i <= n; i++) count++;
""", "O(√n)", ["O(n)", "O(√n)", "O(log n)", "O(n²)"],
            "The loop stops once i² exceeds n, i.e. once i passes √n. The condition, not the "
            "increment, decides how long a loop runs."),
        _bigo(r"""
for (int i = 0; i < n; i++)
    for (int j = 0; j < 10; j++)
        grid[i][j] = i * j;
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(10ⁿ)"],
            "The inner loop runs ten times whatever n is, so it is a constant factor. Nested "
            "loops multiply their *counts*, and one of these counts is 10."),
        _bigo(r"""
for (int i = 1; i <= n; i++) {
    int x = i;
    while (x > 0) { sum += x % 10; x /= 10; }
}
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "Each i has about log₁₀ i digits, and summing log i over 1…n gives Θ(n log n). In "
            "practice the inner loop runs at most 10 times for an `int`, which is why this is "
            "fast — but the growth is n log n."),
    ],
    "arrays-first-pass": [
        _bigo(r"""
int[] b = Arrays.copyOf(a, n);
for (int i = 0; i < n / 2; i++) {
    int t = b[i]; b[i] = b[n - 1 - i]; b[n - 1 - i] = t;
}
""", "O(n)", ["O(1)", "O(n)", "O(n²)", "O(n log n)"],
            "The copy is a hidden O(n) and the swap loop is n/2 — O(n) + O(n) is O(n). Library "
            "calls that touch every element cost what a loop over every element costs."),
        _bigo(r"""
int[] arr = new int[n];
int size = 0;
for (int x : input) {                      // n values
    for (int i = size; i > 0; i--) arr[i] = arr[i - 1];
    arr[0] = x;
    size++;
}
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "Inserting at the front shifts everything already stored: 0 + 1 + … + (n−1) moves. "
            "Arrays are cheap at the end and expensive at the front — build it reversed, or use "
            "an `ArrayDeque`."),
        _bigo(r"""
int[] best = new int[n];
best[0] = a[0];
for (int i = 1; i < n; i++) best[i] = Math.max(best[i - 1], a[i]);
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(log n)"],
            "Each entry reuses the one before it, so a running maximum is one pass. This is the "
            "smallest possible dynamic-programming idea, and it is worth recognising as one."),
        _bigo(r"""
for (int i = 0; i < n; i++) {
    int m = a[0];
    for (int j = 1; j <= i; j++) m = Math.max(m, a[j]);
    best[i] = m;
}
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(log n)"],
            "Same output as the running maximum, recomputed from scratch at every i: "
            "0 + 1 + … + (n−1) comparisons. When the answer at i only extends the answer at "
            "i−1, carry it instead of rebuilding it."),
        _bigo(r"""
for (int q = 0; q < Q; q++) {
    Arrays.fill(seen, false);             // seen.length == n
    seen[queries[q]] = true;
}
""", "O(Q·n)", ["O(Q)", "O(Q + n)", "O(Q·n)", "O(n)"],
            "`Arrays.fill` is a loop over n. Resetting a whole array per query multiplies the "
            "query count by the array size — undo only the entries you set, or stamp each entry "
            "with the query number instead."),
    ],
    # ---------------------------------------------------------------- stage 2
    "hashing": [
        _bigo(r"""
Set<Integer> seen = new HashSet<>();
for (int x : a) {
    if (seen.contains(target - x)) return true;
    seen.add(x);
}
return false;
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
            "`contains` and `add` are expected O(1), so one pass is O(n) — against O(n²) for "
            "checking every pair. \"Expected\" matters: it assumes a reasonable hash function, "
            "which `Integer` has."),
        _bigo(r"""
Map<String, Integer> freq = new TreeMap<>();
for (String w : words) freq.merge(w, 1, Integer::sum);   // n words
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "`TreeMap` is a red-black tree: every `merge` is O(log n). You pay for keeping the "
            "keys sorted. A `HashMap` counts the same words in O(n) — reach for `TreeMap` only "
            "when you need the order. (Word length is treated as bounded here.)"),
        _bigo(r"""
Map<String, List<String>> groups = new HashMap<>();
for (String w : words) {                  // n words, each of length ≤ k
    char[] c = w.toCharArray();
    Arrays.sort(c);
    groups.computeIfAbsent(new String(c), x -> new ArrayList<>()).add(w);
}
""", "O(n·k log k)", ["O(n)", "O(n·k)", "O(n·k log k)", "O(n²·k)"],
            "Sorting each word is O(k log k) and dominates; hashing the key is another O(k). "
            "String keys are never O(1) to hash — they are O(length). A 26-slot count array as "
            "the key brings it to O(n·k)."),
        _bigo(r"""
for (int x : a)                           // a has n elements
    if (map.containsValue(x)) hits++;     // map has n entries
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "Only *keys* are hashed. `containsValue` walks every entry, so this is a linear scan "
            "inside a loop. If you need to look values up, keep a second map keyed by value."),
        _bigo(r"""
int[] count = new int[26];
for (char ch : s.toCharArray()) count[ch - 'a']++;
int distinct = 0;
for (int i = 0; i < 26; i++) if (count[i] > 0) distinct++;
""", "O(n)", ["O(1)", "O(n)", "O(n log n)", "O(n²)"],
            "An array indexed by the character *is* a hash table with a perfect hash. The second "
            "loop is a constant 26, and `toCharArray` is a hidden O(n) copy — use `charAt` if the "
            "extra memory matters."),
    ],
    "two-pointers": [
        _bigo(r"""
int l = 0, r = n - 1;                     // a is sorted
while (l < r) {
    int s = a[l] + a[r];
    if (s == target) return true;
    if (s < target) l++; else r--;
}
""", "O(n)", ["O(n)", "O(n²)", "O(log n)", "O(n log n)"],
            "Every iteration moves one pointer inward and neither ever moves back, so there are at "
            "most n − 1 iterations. That monotone movement is the whole argument."),
        _bigo(r"""
Arrays.sort(a);
for (int i = 0; i < n; i++) {
    int l = i + 1, r = n - 1;
    while (l < r) { /* move l or r toward each other */ }
}
""", "O(n²)", ["O(n log n)", "O(n²)", "O(n³)", "O(n² log n)"],
            "3-sum: the sort is O(n log n), then n outer iterations each run an O(n) two-pointer "
            "scan. O(n log n) + O(n²) = O(n²). The pointers reset per `i`, which is exactly why "
            "this one is quadratic and the pair version is not."),
        _bigo(r"""
int w = 0;
for (int r = 0; r < n; r++)
    if (r == 0 || a[r] != a[r - 1]) a[w++] = a[r];
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "Read pointer and write pointer both only move forward. Compaction in place is one "
            "pass — no shifting, which is what makes it cheaper than `remove` in a loop."),
        _bigo(r"""
for (int i = 0; i < n; i++) {
    int j = i;
    while (j < n && a[j] == a[i]) j++;
    longest = Math.max(longest, j - i);
}
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(log n)"],
            "`j` restarts at `i` every time, so on an array of equal values it rescans the rest "
            "of the array for each i. Jump `i` to `j − 1` after the scan and each element is "
            "passed once: O(n). A second pointer is only linear if it never goes back."),
        _bigo(r"""
int i = 0, j = 0, k = 0;                  // a has n elements, b has m, both sorted
while (i < n && j < m) out[k++] = a[i] <= b[j] ? a[i++] : b[j++];
while (i < n) out[k++] = a[i++];
while (j < m) out[k++] = b[j++];
""", "O(n + m)", ["O(n·m)", "O(n + m)", "O((n + m) log (n + m))", "O(min(n, m))"],
            "Every step emits exactly one element, and there are n + m of them. Merging two "
            "sorted sequences is linear — that is the step merge sort is built on."),
    ],
    "sliding-window": [
        _bigo(r"""
for (int i = 0; i + k <= n; i++) {
    int s = 0;
    for (int j = i; j < i + k; j++) s += a[j];
    best = Math.max(best, s);
}
""", "O(n·k)", ["O(n)", "O(n·k)", "O(n²)", "O(k)"],
            "Every window is re-summed from scratch. Adjacent windows share k − 1 elements: add "
            "the one entering, subtract the one leaving, and it is O(n)."),
        _bigo(r"""
int left = 0;
for (int right = 0; right < n; right++) {
    sum += a[right];
    while (sum > S) sum -= a[left++];
    best = Math.max(best, right - left + 1);
}
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(S)"],
            "A `while` inside a `for`, and still linear: `left` only increases and never passes "
            "n, so the inner loop runs at most n times *in total* across the whole run. Count "
            "pointer moves, not loop nesting."),
        _bigo(r"""
TreeMap<Integer, Integer> win = new TreeMap<>();
for (int r = 0; r < n; r++) {
    win.merge(a[r], 1, Integer::sum);
    if (r >= k) {
        int out = a[r - k];
        if (win.merge(out, -1, Integer::sum) == 0) win.remove(out);
    }
    if (r >= k - 1) maxes.add(win.lastKey());
}
""", "O(n log k)", ["O(n)", "O(n log k)", "O(n·k)", "O(n log n)"],
            "The tree never holds more than k keys, so each operation is O(log k). A monotonic "
            "deque answers the same question in O(n) — but the tree also answers the "
            "window minimum from the same structure, which one deque cannot."),
        _bigo(r"""
Deque<Integer> dq = new ArrayDeque<>();   // indices, values decreasing
for (int i = 0; i < n; i++) {
    while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast();
    dq.addLast(i);
    if (dq.peekFirst() <= i - k) dq.pollFirst();
    if (i >= k - 1) out[i - k + 1] = a[dq.peekFirst()];
}
""", "O(n)", ["O(n)", "O(n·k)", "O(n log k)", "O(k)"],
            "Each index is added once and removed at most once, so all the `poll`s together are "
            "bounded by n. The amortised argument again: bound the total, not the per-step."),
        _bigo(r"""
int[] last = new int[128];
Arrays.fill(last, -1);
int left = 0;
for (int r = 0; r < s.length(); r++) {
    char c = s.charAt(r);
    left = Math.max(left, last[c] + 1);
    last[c] = r;
    best = Math.max(best, r - left + 1);
}
""", "O(n)", ["O(1)", "O(n)", "O(n²)", "O(n log n)"],
            "No inner loop at all: `left` jumps straight past the previous occurrence instead of "
            "shrinking one step at a time. The `fill` over 128 slots is a constant."),
    ],
    "prefix-sums": [
        _bigo(r"""
long[] pre = new long[n + 1];
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];
for (int[] qr : queries)                  // q queries
    out.add(pre[qr[1] + 1] - pre[qr[0]]);
""", "O(n + q)", ["O(n·q)", "O(n + q)", "O(q log n)", "O(n)"],
            "O(n) once to build, O(1) per query after. The build cost is paid once and shared by "
            "every query, which is the whole trade."),
        _bigo(r"""
for (int[] qr : queries) {                // q queries over an array of n
    long s = 0;
    for (int i = qr[0]; i <= qr[1]; i++) s += a[i];
    out.add(s);
}
""", "O(n·q)", ["O(n + q)", "O(n·q)", "O(q log n)", "O(q)"],
            "Each query can span the whole array. For a single query this is fine; for 10⁵ "
            "queries over 10⁵ elements it is 10¹⁰ additions. Build the prefix array."),
        _bigo(r"""
Map<Long, Integer> seen = new HashMap<>();
seen.put(0L, 1);
long run = 0;
for (int x : a) {
    run += x;
    count += seen.getOrDefault(run - k, 0);
    seen.merge(run, 1, Integer::sum);
}
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(n·k)"],
            "Subarrays summing to k, counted in one pass: a subarray ending here sums to k exactly "
            "when an earlier prefix equals `run − k`. The hash map turns \"find an earlier "
            "prefix\" from a scan into a lookup."),
        _bigo(r"""
for (int i = 0; i <= n; i++)
    for (int j = i + 1; j <= n; j++)
        if (pre[j] - pre[i] == k) count++;
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "Prefix sums make each subarray's sum O(1), but there are still n² subarrays to ask "
            "about. A prefix array speeds up the question; it does not reduce how many times you "
            "ask it."),
        _bigo(r"""
for (int i = 1; i <= r; i++)
    for (int j = 1; j <= c; j++)
        P[i][j] = g[i-1][j-1] + P[i-1][j] + P[i][j-1] - P[i-1][j-1];
// then q rectangle queries, each four lookups into P
""", "O(r·c + q)", ["O(r·c·q)", "O(r·c + q)", "O((r + c)·q)", "O(r·c)"],
            "Two dimensions, same trade: O(r·c) once, O(1) per rectangle by inclusion–exclusion. "
            "The subtraction of `P[i-1][j-1]` is the corner that was added twice."),
    ],
    "strings": [
        _bigo(r"""
for (int i = 0; i < n; i++)               // s has n chars, p has m ≤ n
    if (s.substring(i).startsWith(p)) count++;
""", "O(n²)", ["O(n)", "O(n·m)", "O(n²)", "O(m)"],
            "`substring` copies — since Java 7 it allocates a new array of n − i characters — so "
            "the copying alone is 1 + 2 + … + n. `s.startsWith(p, i)` compares in place and makes "
            "it O(n·m)."),
        _bigo(r"""
for (int i = 0; i < s.length(); i++)
    if (s.toCharArray()[i] == 'a') count++;
""", "O(n²)", ["O(n)", "O(n²)", "O(1)", "O(n log n)"],
            "`toCharArray` copies the entire string, and it is called once per character. Hoist "
            "the copy above the loop, or use `charAt(i)`, and it is O(n)."),
        _bigo(r"""
boolean pal = new StringBuilder(s).reverse().toString().equals(s);
""", "O(n)", ["O(1)", "O(n)", "O(n²)", "O(n log n)"],
            "Three linear passes — copy into the builder, reverse, copy out and compare — is "
            "still O(n). Two pointers from the ends do it in one pass with no extra memory, which "
            "is a space win rather than a time one."),
        _bigo(r"""
char[] x = s.toCharArray(), y = t.toCharArray();   // both length n
Arrays.sort(x);
Arrays.sort(y);
return Arrays.equals(x, y);
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "The anagram check by sorting. It is correct and short, and a 26-slot count array "
            "does it in O(n) — the difference an interviewer is usually fishing for."),
        _bigo(r"""
for (String w : words)                    // m words, each ≤ k chars
    if (text.indexOf(w) >= 0) found++;    // text has n chars
""", "O(m·n·k)", ["O(m + n)", "O(m·n)", "O(m·n·k)", "O(n log m)"],
            "`String.indexOf` is a naive search: O(n·k) in the worst case, per word. Real text "
            "rarely hits the worst case, which is why this is usually fast and occasionally a "
            "timeout. A trie or Aho–Corasick shares the work across words."),
    ],
    # ---------------------------------------------------------------- stage 3
    "sorting": [
        _bigo(r"""
List<Integer> xs = new ArrayList<>(input);   // n values
Collections.sort(xs);
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "`Collections.sort` is TimSort: O(n log n) worst case, and O(n) on input that is "
            "already sorted — it finds existing runs and merges them."),
        _bigo(r"""
words.sort((a, b) -> a.toLowerCase().compareTo(b.toLowerCase()));  // n words of length k
""", "O(k·n log n)", ["O(n log n)", "O(k·n log n)", "O(n²·k)", "O(n·k)"],
            "A sort makes O(n log n) comparisons, and this comparator allocates two lowercase "
            "copies each time, so every comparison is O(k). Precompute the keys once — or use "
            "`String.CASE_INSENSITIVE_ORDER`, which compares in place."),
        _bigo(r"""
// a is sorted except that one adjacent pair is swapped
for (int i = 1; i < n; i++) {
    int x = a[i], j = i - 1;
    while (j >= 0 && a[j] > x) { a[j + 1] = a[j]; j--; }
    a[j + 1] = x;
}
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
            "Insertion sort is O(n + inversions). Nearly-sorted input has almost no inversions, so "
            "the inner loop does O(1) work per element. Its worst case is O(n²), which is why it "
            "is only chosen when the input is known to be close."),
        _bigo(r"""
int[] cnt = new int[K + 1];               // values are in [0, K]
for (int x : a) cnt[x]++;
int w = 0;
for (int v = 0; v <= K; v++)
    while (cnt[v]-- > 0) a[w++] = v;
""", "O(n + K)", ["O(n log n)", "O(n + K)", "O(n·K)", "O(K)"],
            "Counting sort never compares, so the n log n lower bound does not apply. The `while` "
            "writes each element once in total, plus one visit per value in the range. Wonderful "
            "when K is small; useless when K is 10⁹."),
        _bigo(r"""
for (int i = 1; i <= n; i++) {            // a is random
    int[] prefix = Arrays.copyOf(a, i);
    Arrays.sort(prefix);
    medians[i - 1] = prefix[(i - 1) / 2];
}
""", "O(n² log n)", ["O(n log n)", "O(n²)", "O(n² log n)", "O(n³)"],
            "A running median by re-sorting everything seen so far: the i-th step costs "
            "O(i log i), which sums to O(n² log n). Two heaps maintain the median in O(log n) per "
            "element, O(n log n) overall."),
    ],
    "binary-search": [
        _bigo(r"""
int lo = 0, hi = n;
while (lo < hi) {
    int mid = (lo + hi) >>> 1;
    if (a[mid] < x) lo = mid + 1; else hi = mid;
}
""", "O(log n)", ["O(1)", "O(log n)", "O(n)", "O(√n)"],
            "The range halves every iteration, so after ⌈log₂(n+1)⌉ steps it is empty. `>>> 1` "
            "is the overflow-safe midpoint for non-negative ints."),
        _bigo(r"""
long lo = 1, hi = maxValue;               // M = maxValue
while (lo < hi) {
    long mid = lo + (hi - lo) / 2;
    if (feasible(a, mid)) hi = mid;       // feasible scans all n elements
    else lo = mid + 1;
}
""", "O(n log M)", ["O(log M)", "O(n log n)", "O(n log M)", "O(n·M)"],
            "Binary search on the answer: log M probes over the *value range*, each one an O(n) "
            "feasibility check. The log is of the range of answers, not the array length — which "
            "is why a 10⁹ range still means only ~30 probes."),
        _bigo(r"""
Arrays.sort(a);                           // n elements
for (int x : queries)                     // q queries
    if (Arrays.binarySearch(a, x) >= 0) hits++;
""", "O((n + q) log n)", ["O(n log n + q)", "O((n + q) log n)", "O(n·q)", "O(q log q)"],
            "Sort once, O(n log n); then O(log n) per query. Sorting pays off as soon as there is "
            "more than a handful of queries — for a single one, a linear scan is cheaper."),
        _bigo(r"""
// list is a java.util.LinkedList<Integer>, sorted, size n
int lo = 0, hi = n;
while (lo < hi) {
    int mid = (lo + hi) >>> 1;
    if (list.get(mid) < x) lo = mid + 1; else hi = mid;
}
""", "O(n log n)", ["O(log n)", "O(n)", "O(n log n)", "O(n²)"],
            "Binary search needs O(1) access to the middle, and `LinkedList.get` walks up to n/2 "
            "nodes. log n probes × O(n) walk = O(n log n) — worse than just scanning. "
            "`Collections.binarySearch` checks for `RandomAccess` and switches strategy for this "
            "exact reason."),
        _bigo(r"""
int lo = 0, hi = r * c;                   // matrix read row by row is sorted
while (lo < hi) {
    int mid = (lo + hi) >>> 1;
    if (m[mid / c][mid % c] < x) lo = mid + 1; else hi = mid;
}
""", "O(log(r·c))", ["O(log(r·c))", "O(r + c)", "O(r log c)", "O(r·c)"],
            "Treat the grid as one sorted array of r·c cells and map the index back with `/` and "
            "`%`. log(r·c) = log r + log c, so this beats a row-then-column staircase walk."),
    ],
    "math-number-theory": [
        _bigo(r"""
for (long d = 2; d * d <= n; d++)
    if (n % d == 0) return false;
return n >= 2;
""", "O(√n)", ["O(n)", "O(√n)", "O(log n)", "O(n log log n)"],
            "If n has a factor above √n, it has a matching one below it, so trial division can "
            "stop at √n. `d * d <= n` avoids the floating-point `Math.sqrt` — keep `d` a `long` "
            "so the square cannot overflow."),
        _bigo(r"""
boolean[] composite = new boolean[n + 1];
for (int p = 2; (long) p * p <= n; p++)
    if (!composite[p])
        for (int m = p * p; m <= n; m += p) composite[m] = true;
""", "O(n log log n)", ["O(n)", "O(n log log n)", "O(n√n)", "O(n²)"],
            "The sieve of Eratosthenes: prime p crosses off n/p multiples, and summing n/p over "
            "primes gives n log log n — which is under 4n for any n you will meet. Starting at "
            "`p * p` is safe because smaller multiples were crossed off by smaller primes."),
        _bigo(r"""
while (b != 0) {
    long t = a % b;
    a = b;
    b = t;
}
return a;
""", "O(log min(a, b))", ["O(1)", "O(log min(a, b))", "O(min(a, b))", "O(√a)"],
            "Euclid's algorithm: every two steps the smaller number at least halves. The worst "
            "case is consecutive Fibonacci numbers, and even for 64-bit values that is under 100 "
            "iterations."),
        _bigo(r"""
long r = 1;
while (e > 0) {
    if ((e & 1) == 1) r = r * base % MOD;
    base = base * base % MOD;
    e >>= 1;
}
""", "O(log e)", ["O(e)", "O(log e)", "O(√e)", "O(1)"],
            "Fast exponentiation squares the base and halves the exponent, so it takes one step "
            "per *bit* of e. 2⁶⁰ as an exponent is 60 multiplications instead of 10¹⁸."),
        _bigo(r"""
int count = 0;
for (int i = 2; i <= n; i++)
    if (isPrime(i)) count++;              // isPrime: trial division up to √i
""", "O(n√n)", ["O(n)", "O(n log log n)", "O(n√n)", "O(log n)"],
            "Up to √i work for each of n numbers. (The precise count is a little lower — most "
            "composites exit on a tiny factor, leaving the primes to pay full price — but it "
            "grows far faster than the sieve.) Counting primes up to n is a sieve problem."),
    ],
    "bit-manipulation": [
        _bigo(r"""
for (int mask = 0; mask < (1 << n); mask++)
    for (int i = 0; i < n; i++)
        if ((mask & (1 << i)) != 0) sum[mask] += a[i];
""", "O(n·2ⁿ)", ["O(2ⁿ)", "O(n·2ⁿ)", "O(n²)", "O(n!)"],
            "2ⁿ subsets, n bits checked in each. Reusing `sum[mask ^ lowestBit]` computes each "
            "subset sum in O(1) and brings it to O(2ⁿ) — the same trick as a running prefix."),
        _bigo(r"""
int x = 0;
for (int v : a) x ^= v;
return x;
""", "O(n)", ["O(n)", "O(n log n)", "O(1)", "O(n²)"],
            "One pass, O(1) extra space. Pairs cancel under XOR in any order, so what remains is "
            "the element that appears an odd number of times — no hash set needed."),
        _bigo(r"""
int c = 0;
while (x != 0) {
    x &= x - 1;                           // clears the lowest set bit
    c++;
}
""", "O(number of set bits)", ["O(1)", "O(number of set bits)", "O(x)", "O(√x)"],
            "Kernighan's trick removes one set bit per iteration, so the loop runs once per 1-bit "
            "rather than once per bit position. For an `int` that is at most 32 either way — "
            "`Integer.bitCount` is the O(1) library call."),
        _bigo(r"""
for (int mask = 0; mask < (1 << n); mask++)
    for (int sub = mask; sub > 0; sub = (sub - 1) & mask)
        work++;
""", "O(3ⁿ)", ["O(2ⁿ)", "O(n·2ⁿ)", "O(3ⁿ)", "O(4ⁿ)"],
            "Every (mask, submask) pair is visited once, and each element is in one of three "
            "states — not in mask, in mask but not sub, in both — so there are 3ⁿ pairs. It is "
            "far less than the 4ⁿ the two nested exponentials suggest."),
        _bigo(r"""
boolean powerOfTwo = x > 0 && (x & (x - 1)) == 0;
""", "O(1)", ["O(1)", "O(log x)", "O(√x)", "O(x)"],
            "A power of two has a single set bit, and `x − 1` flips it and every bit below, so "
            "the AND is zero exactly then. A loop that halves x would be O(log x)."),
    ],
    "simulation-and-matrix": [
        _bigo(r"""
for (int i = 0; i < n; i++)               // n × n matrix
    for (int j = i + 1; j < n; j++) {
        int t = m[i][j]; m[i][j] = m[j][i]; m[j][i] = t;
    }
for (int[] row : m) reverse(row);         // rotate 90° clockwise
""", "O(n²)", ["O(n)", "O(n²)", "O(n³)", "O(n log n)"],
            "Transpose then reverse each row: each cell is touched a constant number of times. "
            "For a matrix, n² is *linear in the input* — it is the number of cells."),
        _bigo(r"""
for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
        for (int k = 0; k < n; k++)
            c[i][j] += a[i][k] * b[k][j];
""", "O(n³)", ["O(n²)", "O(n³)", "O(n² log n)", "O(2ⁿ)"],
            "Schoolbook matrix multiplication: n² output cells, each a dot product of length n. "
            "Swapping the loop order to i-k-j keeps it O(n³) but is several times faster, "
            "because it walks memory in order."),
        _bigo(r"""
for (int gen = 0; gen < k; gen++)
    for (int i = 0; i < r; i++)
        for (int j = 0; j < c; j++)
            next[i][j] = rule(g, i, j);   // checks the 8 neighbours
""", "O(k·r·c)", ["O(r·c)", "O(k·r·c)", "O(k + r·c)", "O(k·(r·c)²)"],
            "Every generation touches every cell, and each cell looks at a constant 8 neighbours. "
            "Simulation cost is steps × state size, and the step count usually comes from the "
            "input — read it off the constraints before you simulate."),
        _bigo(r"""
while (top <= bottom && left <= right) {
    for (int j = left; j <= right; j++) out.add(m[top][j]);
    top++;
    // … right column, bottom row, left column, each shrinking one boundary
}
""", "O(r·c)", ["O(r + c)", "O(r·c)", "O(r·c·min(r, c))", "O(max(r, c)²)"],
            "Spiral order visits every cell exactly once. The outer `while` runs min(r, c)/2 "
            "times, but multiplying it by the inner loops double-counts — count the cells emitted."),
        _bigo(r"""
List<Integer> q = new ArrayList<>(people);   // n people; T = total tickets
while (!q.isEmpty()) {
    int p = q.remove(0);
    if (--tickets[p] > 0) q.add(p);
}
""", "O(T·n)", ["O(T)", "O(T·n)", "O(n²)", "O(T log n)"],
            "The loop runs T times, and `ArrayList.remove(0)` shifts every remaining element. "
            "Simulating a queue with a list turns an O(T) simulation into O(T·n); an `ArrayDeque` "
            "makes each step O(1)."),
    ],
    # ---------------------------------------------------------------- stage 4
    "stacks": [
        _bigo(r"""
Deque<Character> st = new ArrayDeque<>();
for (char ch : s.toCharArray()) {
    if (ch == '(') st.push(ch);
    else if (st.isEmpty() || st.pop() != '(') return false;
}
return st.isEmpty();
""", "O(n)", ["O(1)", "O(n)", "O(n²)", "O(n log n)"],
            "One push or pop per character, each O(1). The stack is what lets you match without "
            "rescanning — a count would do for one bracket type, but not for three."),
        _bigo(r"""
Deque<Integer> st = new ArrayDeque<>();   // indices awaiting a greater element
for (int i = 0; i < n; i++) {
    while (!st.isEmpty() && a[st.peek()] < a[i]) ans[st.pop()] = a[i];
    st.push(i);
}
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "The monotonic stack. Each index is pushed once and popped at most once, so the inner "
            "`while` does at most n pops over the whole run. It looks quadratic and is linear."),
        _bigo(r"""
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        if (a[j] > a[i]) { ans[i] = a[j]; break; }
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(n/2)"],
            "Next-greater by scanning ahead. The `break` helps on random data and not at all on a "
            "decreasing array, where every scan runs to the end. That worst case is the one the "
            "monotonic stack fixes."),
        _bigo(r"""
Stack<Integer> st = new Stack<>();
for (int x : a)
    if (st.search(x) == -1) st.push(x);
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "`Stack.search` is a linear scan from the top. A stack answers \"what is on top?\" in "
            "O(1) and \"is x anywhere in here?\" in O(n) — use a set beside it for the second. "
            "(And prefer `ArrayDeque`: `Stack` is synchronised legacy.)"),
        _bigo(r"""
void push(int x) {
    st.push(x);
    mins.push(mins.isEmpty() ? x : Math.min(x, mins.peek()));
}
int getMin() { return mins.peek(); }
// n pushes, then n calls to getMin()
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "Each push records the minimum *as of that height*, so `getMin` is a peek: O(1). "
            "Paying O(1) extra space per element to avoid an O(n) scan per query is the whole "
            "min-stack idea."),
    ],
    "queues-and-deques": [
        _bigo(r"""
Deque<Integer> q = new ArrayDeque<>();
for (int x : a)                           // n elements
    if (!q.contains(x)) q.offer(x);
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "`ArrayDeque` is O(1) at both ends and O(n) everywhere else — `contains` included. A "
            "queue plus a `HashSet` of what is in it keeps both operations O(1)."),
        _bigo(r"""
LinkedList<Integer> q = new LinkedList<>(values);   // n values
long total = 0;
for (int i = 0; i < q.size(); i++) total += q.get(i);
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(log n)"],
            "`LinkedList.get(i)` walks from the nearer end, O(n) per call. An indexed loop over "
            "a linked list is a quadratic loop; the for-each loop uses an iterator and is O(n)."),
        _bigo(r"""
Deque<Integer> recent = new ArrayDeque<>();
int ping(int t) {                         // called n times, t increasing
    recent.addLast(t);
    while (recent.peekFirst() < t - 3000) recent.pollFirst();
    return recent.size();
}
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
            "Total cost over all n calls: each timestamp is added once and polled at most once. "
            "A single call can poll many, but the total cannot exceed n — O(1) amortised per "
            "call."),
        _bigo(r"""
for (int i = 0; i < k; i++)
    dq.addLast(dq.pollFirst());           // dq is an ArrayDeque of size n
""", "O(k)", ["O(1)", "O(k)", "O(n·k)", "O(n)"],
            "Round-robin rotation: both ends of an `ArrayDeque` are O(1), so k rotations are O(k) "
            "regardless of n. The same loop on an `ArrayList` with `remove(0)` is O(n·k)."),
        _bigo(r"""
void offer(int x) {                       // circular array queue
    if (size == buf.length) buf = grow(buf);   // copies into an array twice as big
    buf[(head + size++) % buf.length] = x;
}
// n calls to offer, starting from capacity 1
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "The copies cost 1 + 2 + 4 + … + n < 2n in total, so n offers are O(n): amortised O(1) "
            "each. Growing by a *constant* amount instead of doubling would make it O(n²)."),
    ],
    "linked-lists": [
        _bigo(r"""
for (int x : values) {                    // n values, no tail pointer
    Node cur = head;
    while (cur.next != null) cur = cur.next;
    cur.next = new Node(x);
}
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "Appending walks to the end every time: 1 + 2 + … + n steps. Keep a `tail` reference "
            "and each append is O(1)."),
        _bigo(r"""
int len = 0;
for (Node c = head; c != null; c = c.next) len++;
Node mid = head;
for (int i = 0; i < len / 2; i++) mid = mid.next;
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(log n)"],
            "Count, then walk halfway: 1.5n steps. The slow/fast pointer version also takes about "
            "1.5n pointer moves — it is one pass, not a faster one. Say that if asked why you "
            "chose either."),
        _bigo(r"""
Node result = null;
for (Node list : lists)                   // k lists, each of length m
    result = mergeTwo(result, list);      // O(length(result) + m)
""", "O(k²·m)", ["O(k·m)", "O(k·m log k)", "O(k²·m)", "O(k·m²)"],
            "The result grows m, 2m, 3m, … and is re-walked by every merge: m·k(k+1)/2. Merging "
            "pairs of lists level by level, or a heap of the k heads, gives O(k·m log k)."),
        _bigo(r"""
Node slow = head, fast = head;
while (fast != null && fast.next != null) {
    slow = slow.next;
    fast = fast.next.next;
    if (slow == fast) return true;
}
return false;
""", "O(n)", ["O(n)", "O(n²)", "O(log n)", "O(n log n)"],
            "Floyd's cycle detection. Without a cycle, `fast` reaches the end in n/2 steps. With "
            "one, once `slow` enters the loop `fast` closes the gap by one node per step, so they "
            "meet within one lap. O(n) time, O(1) space — a `HashSet` of visited nodes is O(n) "
            "space."),
        _bigo(r"""
Map<Node, Node> copy = new HashMap<>();
for (Node c = head; c != null; c = c.next) copy.put(c, new Node(c.val));
for (Node c = head; c != null; c = c.next) {
    copy.get(c).next = copy.get(c.next);
    copy.get(c).random = copy.get(c.random);
}
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(1)"],
            "Two passes and O(1) expected map operations. The map from old node to new node is "
            "what turns \"find the copy of whatever `random` points at\" from a walk into a "
            "lookup."),
    ],
    "heaps": [
        _bigo(r"""
PriorityQueue<Integer> pq = new PriorityQueue<>(values);   // n values, a Collection
""", "O(n)", ["O(n)", "O(n log n)", "O(log n)", "O(n²)"],
            "The collection constructor heapifies bottom-up: most nodes are near the leaves and "
            "sift down a short way, and the sum is O(n). Offering the same n values one at a time "
            "is O(n log n)."),
        _bigo(r"""
PriorityQueue<Integer> pq = new PriorityQueue<>();   // min-heap
for (int x : a) {                         // n values
    pq.offer(x);
    if (pq.size() > k) pq.poll();
}
""", "O(n log k)", ["O(n log n)", "O(n log k)", "O(n·k)", "O(k log n)"],
            "The k largest, with a min-heap capped at size k: every operation is on a heap of at "
            "most k + 1 elements. When k is small, log k is nearly a constant; sorting would be "
            "O(n log n)."),
        _bigo(r"""
for (int x : toDelete)                    // n deletions
    pq.remove(x);                         // pq holds n elements
""", "O(n²)", ["O(n log n)", "O(n²)", "O(n)", "O(log n)"],
            "`PriorityQueue.remove(Object)` has to *find* the element first, and a heap is not "
            "ordered for searching — that is O(n) before the O(log n) fix-up. Lazy deletion "
            "(mark it, skip it when it surfaces) keeps removals O(log n)."),
        _bigo(r"""
List<Integer> out = new ArrayList<>();
while (!pq.isEmpty()) out.add(pq.poll());   // pq holds n elements
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "n polls at O(log n) each: heap sort. Note that *iterating* a `PriorityQueue` is O(n) "
            "but not in order — only polling gives sorted output."),
        _bigo(r"""
PriorityQueue<Node> pq = new PriorityQueue<>((x, y) -> Integer.compare(x.val, y.val));
for (Node h : heads) if (h != null) pq.offer(h);   // k lists, N nodes in total
while (!pq.isEmpty()) {
    Node x = pq.poll();
    tail = tail.next = x;
    if (x.next != null) pq.offer(x.next);
}
""", "O(N log k)", ["O(N log N)", "O(N log k)", "O(N·k)", "O(k log N)"],
            "The heap holds one node per list, so it never exceeds k, and each of the N nodes "
            "passes through it once. `Integer.compare` rather than `x.val − y.val`, which "
            "overflows."),
    ],
    "design": [
        _bigo(r"""
int get(int key) {
    if (!map.containsKey(key)) return -1;
    order.remove(Integer.valueOf(key));   // order: ArrayList of keys, size ≤ capacity
    order.add(key);
    return map.get(key);
}
""", "O(capacity)", ["O(1)", "O(log capacity)", "O(capacity)", "O(capacity²)"],
            "An LRU cache that tracks recency in a list: `remove(Object)` searches and shifts. "
            "The standard design — a hash map into a doubly linked list, or `LinkedHashMap` with "
            "access order — makes `get` and `put` O(1)."),
        _bigo(r"""
boolean remove(int x) {                   // vals: ArrayList, pos: HashMap value -> index
    Integer i = pos.get(x);
    if (i == null) return false;
    int last = vals.get(vals.size() - 1);
    vals.set(i, last);
    pos.put(last, i);
    vals.remove(vals.size() - 1);
    pos.remove(x);
    return true;
}
""", "O(1)", ["O(1)", "O(n)", "O(log n)", "O(√n)"],
            "Swap the victim with the last element, then remove from the end — the only O(1) "
            "removal an `ArrayList` has. The map of positions is what finds the victim without a "
            "scan. This is how an O(1) `getRandom` set is built."),
        _bigo(r"""
String get(String key, int t) {           // hist holds the n versions of key
    TreeMap<Integer, String> hist = store.get(key);
    if (hist == null) return "";
    Map.Entry<Integer, String> e = hist.floorEntry(t);
    return e == null ? "" : e.getValue();
}
""", "O(log n)", ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "`floorEntry` is a tree descent. If versions only ever arrive in increasing time, an "
            "`ArrayList` plus binary search gives the same O(log n) with less memory per entry."),
        _bigo(r"""
void addNum(int x) {                      // low: max-heap, high: min-heap
    low.offer(x);
    high.offer(low.poll());
    if (high.size() > low.size()) low.offer(high.poll());
}
double findMedian() {
    return low.size() > high.size() ? low.peek() : (low.peek() + high.peek()) / 2.0;
}
""", "O(log n)", ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "`addNum` does a constant number of heap operations, O(log n) each; `findMedian` "
            "peeks, O(1). Keeping a sorted `ArrayList` instead makes add O(n)."),
        _bigo(r"""
int get(int key) {                        // LinkedHashMap with accessOrder = true
    Integer v = cache.get(key);
    return v == null ? -1 : v;
}
// removeEldestEntry evicts when size() > capacity
""", "O(1)", ["O(1)", "O(log n)", "O(n)", "O(capacity)"],
            "`LinkedHashMap` in access order is a hash table threaded through a doubly linked "
            "list: `get` hashes, then relinks one node. That is the LRU cache in a dozen lines — "
            "and saying *why* it is O(1) is the part the interviewer is listening for."),
    ],
    # ---------------------------------------------------------------- stage 5
    "recursion": [
        _bigo(r"""
long fib(int n) {
    if (n <= 1) return n;
    if (memo[n] != 0) return memo[n];
    return memo[n] = fib(n - 1) + fib(n - 2);
}
""", "O(n)", ["O(n)", "O(2ⁿ)", "O(n²)", "O(log n)"],
            "Memoised, each n is computed once and every later call returns in O(1). Without the "
            "memo it is O(φⁿ) ≈ O(1.618ⁿ) — the same code, exponentially apart."),
        _bigo(r"""
long pow(long b, int e) {
    if (e == 0) return 1;
    long half = pow(b, e / 2) * pow(b, e / 2);
    return e % 2 == 0 ? half : half * b;
}
""", "O(e)", ["O(log e)", "O(e)", "O(e log e)", "O(2ᵉ)"],
            "It halves e, which suggests O(log e) — but it recurses *twice* per level. The call "
            "tree has log e levels and doubles in width each time: 2^(log e) = e calls. Store "
            "`pow(b, e / 2)` in a variable and it really is O(log e)."),
        _bigo(r"""
int sum(int[] a) {
    if (a.length == 0) return 0;
    return a[0] + sum(Arrays.copyOfRange(a, 1, a.length));
}
""", "O(n²)", ["O(n)", "O(n²)", "O(n log n)", "O(2ⁿ)"],
            "n calls, and each copies the rest of the array: n + (n−1) + … + 1. Pass an index "
            "instead of a slice and it is O(n). Slicing is free in some languages' notation and "
            "never free in Java."),
        _bigo(r"""
void gen(StringBuilder sb, int n) {
    if (sb.length() == n) { System.out.println(sb); return; }
    for (char c : new char[]{'0', '1'}) {
        sb.append(c);
        gen(sb, n);
        sb.deleteCharAt(sb.length() - 1);
    }
}
""", "O(n·2ⁿ)", ["O(2ⁿ)", "O(n·2ⁿ)", "O(n²)", "O(n!)"],
            "2ⁿ leaves, and printing each one costs n characters. The internal nodes add only "
            "2ⁿ more calls. When the output itself is exponential, no algorithm can be faster "
            "than its size."),
        _bigo(r"""
void sort(int[] a, int lo, int hi) {
    if (hi - lo < 2) return;
    int mid = (lo + hi) >>> 1;
    sort(a, lo, mid);
    sort(a, mid, hi);
    merge(a, lo, mid, hi);                // O(hi - lo)
}
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "T(n) = 2T(n/2) + O(n). Draw the tree: log n levels, and each level's merges touch n "
            "elements in total. Counting work *per level* is the reliable way to price a "
            "divide-and-conquer recursion."),
    ],
    "trees": [
        _bigo(r"""
int height(Node t) {
    return t == null ? 0 : 1 + Math.max(height(t.left), height(t.right));
}
""", "O(n)", ["O(log n)", "O(n)", "O(n log n)", "O(h)"],
            "Every node is visited exactly once, however the tree is shaped. The *stack depth* is "
            "O(h), which is the space cost — and why a 10⁵-node chain overflows it."),
        _bigo(r"""
boolean balanced(Node t) {
    if (t == null) return true;
    return Math.abs(height(t.left) - height(t.right)) <= 1
        && balanced(t.left) && balanced(t.right);
}
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "`height` is O(size of subtree), and it is called at every node. On a chain that is "
            "n + (n−1) + … = O(n²); on a balanced tree O(n log n). Return the height and the "
            "verdict from one post-order pass and it is O(n)."),
        _bigo(r"""
Deque<Node> q = new ArrayDeque<>();
q.offer(root);
while (!q.isEmpty()) {
    int size = q.size();
    for (int i = 0; i < size; i++) {
        Node t = q.poll();
        if (t.left != null) q.offer(t.left);
        if (t.right != null) q.offer(t.right);
    }
    levels++;
}
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(h·n)"],
            "Level-order BFS: each node is offered once and polled once. The inner `for` only "
            "groups the polls by level — it does not repeat any of them."),
        _bigo(r"""
String ser(Node t) {
    if (t == null) return "#";
    return t.val + "," + ser(t.left) + "," + ser(t.right);
}
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"],
            "Each call concatenates its children's full strings, so a node at depth d is copied d "
            "times. On a skewed tree that is O(n²). Pass one `StringBuilder` down the recursion "
            "and append to it: O(n)."),
        _bigo(r"""
int count(Node t) {                       // t is a COMPLETE binary tree
    if (t == null) return 0;
    int hl = leftHeight(t), hr = rightHeight(t);   // walk the edges, O(log n)
    if (hl == hr) return (1 << hl) - 1;
    return 1 + count(t.left) + count(t.right);
}
""", "O(log² n)", ["O(n)", "O(log n)", "O(log² n)", "O(√n)"],
            "In a complete tree, one of the two children is always perfect and returns after its "
            "height walk. So only one real recursion per level: log n levels × O(log n) height "
            "walk. Faster than visiting the nodes you are counting."),
    ],
    "bst": [
        _bigo(r"""
Node find(Node t, int x) {
    while (t != null && t.val != x) t = x < t.val ? t.left : t.right;
    return t;
}
""", "O(h)", ["O(log n)", "O(h)", "O(n log n)", "O(1)"],
            "One step down per comparison, so the cost is the height. h is log n for a balanced "
            "tree and n for a chain — saying \"O(log n)\" for a BST you did not balance is the "
            "classic wrong answer."),
        _bigo(r"""
Node root = null;
for (int i = 0; i < n; i++) root = insert(root, i);   // plain, unbalanced BST
""", "O(n²)", ["O(n log n)", "O(n²)", "O(n)", "O(log n)"],
            "Sorted keys build a chain: the i-th insert walks i nodes. Inserting in random order "
            "averages O(n log n); a self-balancing tree guarantees it."),
        _bigo(r"""
TreeMap<Integer, Integer> m = new TreeMap<>();
for (int i = 0; i < n; i++) m.put(i, i);
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "The same sorted keys into a red-black tree. Rotations keep the height ≤ 2 log n, so "
            "every `put` is O(log n) whatever the order. This is what you are paying for when you "
            "choose `TreeMap`."),
        _bigo(r"""
Deque<Node> st = new ArrayDeque<>();
Node cur = root;
while (true) {                            // kth smallest
    while (cur != null) { st.push(cur); cur = cur.left; }
    cur = st.pop();
    if (--k == 0) return cur.val;
    cur = cur.right;
}
""", "O(h + k)", ["O(n)", "O(h + k)", "O(k log n)", "O(log n)"],
            "An in-order walk that stops at the k-th node: h to reach the minimum, then roughly "
            "one step per node emitted. For small k on a balanced tree that is far less than a "
            "full O(n) traversal."),
        _bigo(r"""
boolean valid(Node t, long lo, long hi) {
    if (t == null) return true;
    if (t.val <= lo || t.val >= hi) return false;
    return valid(t.left, lo, t.val) && valid(t.right, t.val, hi);
}
""", "O(n)", ["O(n)", "O(n log n)", "O(h)", "O(n²)"],
            "Each node is checked once against bounds inherited from its ancestors. Comparing a "
            "node only with its children is O(n) too — and wrong, because the BST property is "
            "about the whole subtree."),
    ],
    "backtracking": [
        _bigo(r"""
void go(int i, List<Integer> cur) {
    if (i == n) { out.add(new ArrayList<>(cur)); return; }
    go(i + 1, cur);                       // skip a[i]
    cur.add(a[i]);
    go(i + 1, cur);                       // take a[i]
    cur.remove(cur.size() - 1);
}
""", "O(n·2ⁿ)", ["O(2ⁿ)", "O(n·2ⁿ)", "O(n!)", "O(n²)"],
            "2ⁿ subsets, and copying each into the output costs up to n. The recursion itself is "
            "2ⁿ⁺¹ calls; the copies are what add the factor of n."),
        _bigo(r"""
void perm(List<Integer> cur, boolean[] used) {
    if (cur.size() == n) { out.add(new ArrayList<>(cur)); return; }
    for (int i = 0; i < n; i++) {
        if (used[i]) continue;
        used[i] = true; cur.add(a[i]);
        perm(cur, used);
        used[i] = false; cur.remove(cur.size() - 1);
    }
}
""", "O(n·n!)", ["O(n!)", "O(n·n!)", "O(2ⁿ)", "O(nⁿ)"],
            "n! permutations, each copied in O(n). The `used` array is what keeps it from being "
            "nⁿ — without it you would generate every sequence with repeats and filter them."),
        _bigo(r"""
for (int i = 0; i < r; i++)
    for (int j = 0; j < c; j++)
        if (dfs(i, j, 0)) return true;
// dfs tries the 4 neighbours, never steps back onto the current path,
// and stops when it has matched all L letters
""", "O(r·c·3ᴸ)", ["O(r·c + L)", "O(r·c·L)", "O(r·c·3ᴸ)", "O(3^(r·c))"],
            "Word search: from each of r·c starts, the first step has 4 choices and every later "
            "one at most 3, because the cell you came from is on the path. Pruning on a mismatched "
            "letter makes real inputs far faster; the bound is the worst case."),
        _bigo(r"""
void place(int row) {                     // n-queens, O(1) conflict checks via sets
    if (row == n) { solutions++; return; }
    for (int col = 0; col < n; col++) {
        if (cols.contains(col) || d1.contains(row - col) || d2.contains(row + col)) continue;
        cols.add(col); d1.add(row - col); d2.add(row + col);
        place(row + 1);
        cols.remove(col); d1.remove(row - col); d2.remove(row + col);
    }
}
""", "O(n!)", ["O(nⁿ)", "O(n!)", "O(2ⁿ)", "O(n²)"],
            "One queen per row, and each placed queen removes at least one column from every "
            "later row: n choices, then ≤ n−1, then ≤ n−2… The diagonal checks prune far more "
            "in practice. Placing row by row, rather than trying all n² cells, is where the "
            "exponent drops from nⁿ-ish to n!."),
        _bigo(r"""
void part(int start, List<String> cur) {  // palindrome partitioning of s, length n
    if (start == n) { out.add(new ArrayList<>(cur)); return; }
    for (int end = start + 1; end <= n; end++)
        if (isPal[start][end - 1]) {      // precomputed, O(1) lookup
            cur.add(s.substring(start, end));
            part(end, cur);
            cur.remove(cur.size() - 1);
        }
}
""", "O(n·2ⁿ)", ["O(2ⁿ)", "O(n·2ⁿ)", "O(n!)", "O(n³)"],
            "A string of n characters has 2ⁿ⁻¹ ways to cut it, and on \"aaaa…\" every piece is a "
            "palindrome, so all of them are produced — each costing O(n) to build and copy. The "
            "precomputed table only stops the palindrome *checks* from adding another factor."),
    ],
    "graph-traversal": [
        _bigo(r"""
Deque<Integer> q = new ArrayDeque<>();
q.offer(s); seen[s] = true;
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : adj.get(u))              // adjacency lists
        if (!seen[v]) { seen[v] = true; q.offer(v); }
}
""", "O(V + E)", ["O(V)", "O(V + E)", "O(V·E)", "O(V²)"],
            "Each vertex is enqueued once, and each adjacency list is walked once when its vertex "
            "is polled — so every edge is looked at once (twice if undirected). Marking `seen` on "
            "*enqueue* is what guarantees the once."),
        _bigo(r"""
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v = 0; v < V; v++)           // adjacency MATRIX
        if (adj[u][v] && !seen[v]) { seen[v] = true; q.offer(v); }
}
""", "O(V²)", ["O(V + E)", "O(V²)", "O(E log V)", "O(V·E)"],
            "Same BFS, but finding a vertex's neighbours means scanning a whole row of V cells, "
            "even if it has two. Fine for dense graphs; for 10⁵ vertices the matrix alone does "
            "not fit in memory."),
        _bigo(r"""
for (int i = 0; i < r; i++)
    for (int j = 0; j < c; j++)
        if (grid[i][j] == '1') { islands++; flood(i, j); }   // flood sets cells to '0'
""", "O(r·c)", ["O(r·c)", "O((r·c)²)", "O(r·c·log(r·c))", "O(r + c)"],
            "The nested loops *look* like each call could flood the whole grid, making it "
            "quadratic. But `flood` erases what it visits, so every cell is flooded at most once "
            "in total. Price the whole run, not the worst single call."),
        _bigo(r"""
for (int s = 0; s < V; s++) {
    Arrays.fill(dist, -1);
    bfs(s, dist);                         // standard O(V + E) BFS
}
""", "O(V·(V + E))", ["O(V + E)", "O(V·(V + E))", "O(V³)", "O(E log V)"],
            "All-pairs shortest paths in an unweighted graph: one BFS per source. For sparse "
            "graphs that is O(V²) — better than Floyd–Warshall's O(V³). One BFS seeded with *all* "
            "sources at once (multi-source BFS) is O(V + E) when you only need the nearest source."),
        _bigo(r"""
void dfs(int u) {
    visited.add(u);                       // visited is an ArrayList
    for (int v : adj.get(u))
        if (!visited.contains(v)) dfs(v);
}
""", "O(V·E)", ["O(V + E)", "O(V·E)", "O(V²)", "O(E log V)"],
            "Every edge check does a linear `contains` over up to V visited vertices. The "
            "traversal is right and the bookkeeping makes it slow — a `boolean[]` or `HashSet` "
            "restores O(V + E)."),
    ],
    "topological-sort": [
        _bigo(r"""
Deque<Integer> q = new ArrayDeque<>();
for (int u = 0; u < V; u++) if (indeg[u] == 0) q.offer(u);
while (!q.isEmpty()) {
    int u = q.poll();
    order.add(u);
    for (int v : adj.get(u)) if (--indeg[v] == 0) q.offer(v);
}
""", "O(V + E)", ["O(V + E)", "O(V·E)", "O(V²)", "O(V log V + E)"],
            "Kahn's algorithm: each vertex enters the queue once and each edge decrements one "
            "in-degree once. If `order` ends up shorter than V, what is left contains a cycle."),
        _bigo(r"""
for (int step = 0; step < V; step++) {
    int pick = -1;
    for (int u = 0; u < V; u++)
        if (!done[u] && indeg[u] == 0) { pick = u; break; }
    if (pick == -1) return null;          // cycle
    done[pick] = true;
    order.add(pick);
    for (int v : adj.get(pick)) indeg[v]--;
}
""", "O(V² + E)", ["O(V + E)", "O(V² + E)", "O(V·E)", "O(V log V + E)"],
            "Correct, and it rescans every vertex to find the next zero in-degree. The queue in "
            "Kahn's algorithm exists so that a vertex is found the moment its in-degree hits zero, "
            "instead of being searched for."),
        _bigo(r"""
PriorityQueue<Integer> pq = new PriorityQueue<>();
for (int u = 0; u < V; u++) if (indeg[u] == 0) pq.offer(u);
while (!pq.isEmpty()) {
    int u = pq.poll();
    order.add(u);
    for (int v : adj.get(u)) if (--indeg[v] == 0) pq.offer(v);
}
""", "O(V log V + E)", ["O(V + E)", "O(V log V + E)", "O(E log E)", "O(V²)"],
            "The lexicographically smallest topological order: Kahn's algorithm with a heap "
            "instead of a queue. Every vertex passes through the heap once, at O(log V); the "
            "edges are still O(1) each."),
        _bigo(r"""
for (int u : topo)                        // vertices in topological order
    for (int v : adj.get(u))
        longest[v] = Math.max(longest[v], longest[u] + 1);
""", "O(V + E)", ["O(V + E)", "O(V·E)", "O(2^V)", "O(E log V)"],
            "Longest path is NP-hard in a general graph and linear in a DAG: processing vertices "
            "in topological order means every predecessor is final before you relax from it. The "
            "order is doing the work a priority queue does in Dijkstra."),
        _bigo(r"""
int[] color = new int[V];                 // 0 white, 1 on stack, 2 done
boolean hasCycle(int u) {
    color[u] = 1;
    for (int v : adj.get(u)) {
        if (color[v] == 1) return true;
        if (color[v] == 0 && hasCycle(v)) return true;
    }
    color[u] = 2;
    return false;
}
// called for every white vertex
""", "O(V + E)", ["O(V + E)", "O(V²)", "O(V·E)", "O(E²)"],
            "Three colours mean a finished (black) vertex is never re-entered, so each vertex and "
            "edge is processed once. With only two colours you either miss cycles or re-explore "
            "finished subgraphs — which can be exponential."),
    ],
    "union-find": [
        _bigo(r"""
int find(int x) {
    return parent[x] == x ? x : (parent[x] = find(parent[x]));   // path compression
}
void union(int a, int b) {                // union by size
    a = find(a); b = find(b);
    if (a == b) return;
    if (size[a] < size[b]) { int t = a; a = b; b = t; }
    parent[b] = a; size[a] += size[b];
}
// m operations on n elements
""", "O(m·α(n))", ["O(m log n)", "O(m·α(n))", "O(m·n)", "O(n + m²)"],
            "With both optimisations the amortised cost is the inverse Ackermann function α(n), "
            "which is at most 4 for any n that fits in the universe. Say \"effectively constant\" "
            "— and know that it needs *both* halves."),
        _bigo(r"""
int find(int x) { while (parent[x] != x) x = parent[x]; return x; }
void union(int a, int b) { parent[find(a)] = find(b); }
// unions (0,1), (0,2), (0,3), … (0,n−1), in that order
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(n·α(n))"],
            "No rank, no compression, and this order builds a chain: 0 → 1 → 2 → … Every union "
            "calls `find(0)`, which walks the whole chain built so far. That is the degenerate "
            "case both optimisations exist to prevent."),
        _bigo(r"""
int find(int x) { while (parent[x] != x) x = parent[x]; return x; }
void union(int a, int b) {                // union by size, NO path compression
    a = find(a); b = find(b);
    if (a == b) return;
    if (size[a] < size[b]) { int t = a; a = b; b = t; }
    parent[b] = a; size[a] += size[b];
}
// m operations on n elements
""", "O(m log n)", ["O(m)", "O(m log n)", "O(m·n)", "O(m·α(n))"],
            "Union by size alone caps the height at log n: a node's tree at least doubles in size "
            "every time the node gets deeper, and it cannot double more than log n times."),
        _bigo(r"""
edges.sort(Comparator.comparingInt(e -> e[2]));   // E edges, V vertices
for (int[] e : edges)
    if (dsu.union(e[0], e[1])) cost += e[2];      // union returns false if already joined
""", "O(E log E)", ["O(E·α(V))", "O(E log E)", "O(V²)", "O(E·V)"],
            "Kruskal's algorithm: the sort dominates, and the union–find part is O(E·α(V)). "
            "Since E ≤ V², log E ≤ 2 log V, so O(E log V) is the same thing."),
        _bigo(r"""
for (int[] e : edges) {                   // E edges, n elements
    dsu.union(e[0], e[1]);
    int comps = 0;
    for (int i = 0; i < n; i++) if (dsu.find(i) == i) comps++;
    out.add(comps);
}
""", "O(E·n)", ["O(E·α(n))", "O(E·n)", "O(E + n)", "O(n²)"],
            "Recounting roots after every edge is n finds per edge (strictly O(E·n·α(n))). Start "
            "a counter at n and decrement it whenever `union` actually merges two sets: O(E·α(n))."),
    ],
    "shortest-paths": [
        _bigo(r"""
PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(x -> x[0]));
pq.offer(new long[]{0, s});
while (!pq.isEmpty()) {
    long[] top = pq.poll();
    int u = (int) top[1];
    if (top[0] > dist[u]) continue;       // stale entry
    for (int[] e : adj.get(u))
        if (dist[u] + e[1] < dist[e[0]]) {
            dist[e[0]] = dist[u] + e[1];
            pq.offer(new long[]{dist[e[0]], e[0]});
        }
}
""", "O((V + E) log V)", ["O(V + E)", "O((V + E) log V)", "O(V·E)", "O(V²)"],
            "Dijkstra with a binary heap and lazy deletion: every successful relaxation pushes "
            "one entry, so the heap sees O(E) pushes at O(log E) = O(log V) each. The stale-entry "
            "skip is what keeps old, longer distances from being expanded."),
        _bigo(r"""
for (int it = 0; it < V; it++) {
    int u = -1;
    for (int v = 0; v < V; v++)
        if (!done[v] && (u == -1 || dist[v] < dist[u])) u = v;
    done[u] = true;
    for (int[] e : adj.get(u)) dist[e[0]] = Math.min(dist[e[0]], dist[u] + e[1]);
}
""", "O(V²)", ["O(V²)", "O((V + E) log V)", "O(V·E)", "O(V³)"],
            "Dijkstra with a linear scan for the closest vertex: V scans of V. Worse than the heap "
            "on sparse graphs and *better* on dense ones, where E ≈ V² makes the heap version "
            "O(V² log V)."),
        _bigo(r"""
for (int i = 0; i < V - 1; i++)
    for (int[] e : edges)                 // e = {u, v, w}
        if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]])
            dist[e[1]] = dist[e[0]] + e[2];
""", "O(V·E)", ["O(V + E)", "O(V·E)", "O(E log V)", "O(V³)"],
            "Bellman–Ford: V − 1 rounds, each relaxing every edge. Slower than Dijkstra, and it "
            "survives negative edge weights — one more round that still improves something means "
            "a negative cycle."),
        _bigo(r"""
for (int k = 0; k < V; k++)
    for (int i = 0; i < V; i++)
        for (int j = 0; j < V; j++)
            d[i][j] = Math.min(d[i][j], d[i][k] + d[k][j]);
""", "O(V³)", ["O(V²)", "O(V³)", "O(V²·E)", "O(V·E)"],
            "Floyd–Warshall: all pairs, allowing intermediate vertices 0…k. The loop order "
            "matters — `k` must be outermost — and at V = 500 the 1.25·10⁸ steps are fine."),
        _bigo(r"""
Deque<Integer> dq = new ArrayDeque<>();   // every edge weight is 0 or 1
dq.offer(s);
while (!dq.isEmpty()) {
    int u = dq.pollFirst();
    for (int[] e : adj.get(u))
        if (dist[u] + e[1] < dist[e[0]]) {
            dist[e[0]] = dist[u] + e[1];
            if (e[1] == 0) dq.offerFirst(e[0]); else dq.offerLast(e[0]);
        }
}
""", "O(V + E)", ["O(V + E)", "O((V + E) log V)", "O(V·E)", "O(V²)"],
            "0-1 BFS: a zero-weight edge goes to the front, a one-weight edge to the back, so the "
            "deque stays sorted by distance without a heap. A vertex can be pushed at most twice "
            "(once per possible improvement), keeping it linear."),
    ],
    # ---------------------------------------------------------------- stage 6
    "greedy": [
        _bigo(r"""
Arrays.sort(iv, Comparator.comparingInt(x -> x[1]));   // n intervals, by end
int end = Integer.MIN_VALUE, kept = 0;
for (int[] x : iv)
    if (x[0] >= end) { kept++; end = x[1]; }
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"],
            "Most greedy algorithms are \"sort by the right key, then one pass\", and the sort is "
            "the cost. The exhaustive alternative — try every subset of intervals — is O(2ⁿ); the "
            "exchange argument is what licenses skipping it."),
        _bigo(r"""
int count = 0;
for (int c : coinsDescending) {           // k denominations, amount A
    count += amount / c;
    amount %= c;
}
""", "O(k)", ["O(k)", "O(A)", "O(k·A)", "O(log A)"],
            "Division instead of subtracting one coin at a time, which would be O(k + A). "
            "Whether greedy is even *correct* depends on the coin system — for {1, 3, 4} and "
            "amount 6 it gives 3 coins when 2 suffice."),
        _bigo(r"""
int reach = 0;
for (int i = 0; i < n; i++) {
    if (i > reach) return false;
    reach = Math.max(reach, i + a[i]);
}
return true;
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(2ⁿ)"],
            "Jump game: carry the furthest reachable index. The DP that asks \"can I reach i?\" by "
            "checking every earlier j is O(n²); the greedy observation is that reachability is a "
            "prefix, so one number describes it."),
        _bigo(r"""
Arrays.sort(greed);                       // n children
Arrays.sort(cookies);                     // m cookies
int i = 0, j = 0;
while (i < n && j < m) {
    if (cookies[j] >= greed[i]) i++;
    j++;
}
""", "O(n log n + m log m)", ["O(n + m)", "O(n log n + m log m)", "O(n·m)", "O((n + m)²)"],
            "Two sorts, then a two-pointer pass of O(n + m). Two independent sizes, two sort "
            "costs — do not fold them into one n."),
        _bigo(r"""
PriorityQueue<Long> pq = new PriorityQueue<>(ropes);   // n ropes
long cost = 0;
while (pq.size() > 1) {
    long joined = pq.poll() + pq.poll();
    cost += joined;
    pq.offer(joined);
}
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "Always join the two cheapest: n − 1 rounds of three heap operations. The same shape "
            "as building a Huffman code. Re-sorting the list every round instead would be "
            "O(n² log n)."),
    ],
    "intervals": [
        _bigo(r"""
Arrays.sort(iv, Comparator.comparingInt(x -> x[0]));   // n intervals
List<int[]> out = new ArrayList<>();
for (int[] x : iv) {
    if (out.isEmpty() || out.get(out.size() - 1)[1] < x[0]) out.add(x);
    else out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], x[1]);
}
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "Merge intervals: sort by start, then one pass comparing with the last merged "
            "interval. Once sorted, an interval can only overlap the one just before it, so no "
            "backward search is needed."),
        _bigo(r"""
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        if (iv[i][0] < iv[j][1] && iv[j][0] < iv[i][1]) overlaps++;
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(n³)"],
            "Checking every pair is the honest answer when you need *every* overlapping pair — "
            "the output itself can be n². When you only need \"does any overlap?\", sort and "
            "compare neighbours in O(n log n)."),
        _bigo(r"""
Arrays.sort(iv, Comparator.comparingInt(x -> x[0]));   // n meetings
PriorityQueue<Integer> ends = new PriorityQueue<>();
for (int[] x : iv) {
    if (!ends.isEmpty() && ends.peek() <= x[0]) ends.poll();
    ends.offer(x[1]);
}
int rooms = ends.size();
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(n·rooms)"],
            "Meeting rooms: the heap holds the end time of every room in use, and each meeting "
            "does at most one poll and one offer. Scanning every room for a free one would be "
            "O(n·rooms)."),
        _bigo(r"""
List<int[]> out = new ArrayList<>();      // intervals: n, sorted, non-overlapping
for (int[] cur : intervals) {
    if (cur[1] < add[0]) out.add(cur);
    else if (cur[0] > add[1]) { out.add(add); add = cur; }
    else add = new int[]{Math.min(add[0], cur[0]), Math.max(add[1], cur[1])};
}
out.add(add);
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "Inserting into an already sorted, disjoint list needs no sort: one pass that copies "
            "what is left of the new interval, absorbs what overlaps it, and carries the rest. "
            "Re-sorting everything would be the O(n log n) way to get the same answer."),
        _bigo(r"""
for (int[] x : intervals)                 // n intervals over a timeline of length T
    for (int t = x[0]; t < x[1]; t++) busy[t]++;
int peak = Arrays.stream(busy).max().getAsInt();
""", "O(n·T)", ["O(n + T)", "O(n·T)", "O(n log n)", "O(T log T)"],
            "Painting every time slot of every interval. A difference array records only the two "
            "endpoints — `diff[start]++`, `diff[end]--` — and one prefix-sum pass recovers the "
            "counts: O(n + T)."),
    ],
    "dp-1d": [
        _bigo(r"""
long a = 1, b = 1;                        // ways to climb n stairs, 1 or 2 at a time
for (int i = 2; i <= n; i++) {
    long c = a + b;
    a = b;
    b = c;
}
""", "O(n)", ["O(n)", "O(2ⁿ)", "O(log n)", "O(n²)"],
            "Each state depends only on the two before it, so two variables replace the whole "
            "table: O(n) time, O(1) space. Rolling the table like this is worth doing whenever "
            "the recurrence has a short reach."),
        _bigo(r"""
for (int i = 0; i < n; i++) {
    lis[i] = 1;
    for (int j = 0; j < i; j++)
        if (a[j] < a[i]) lis[i] = Math.max(lis[i], lis[j] + 1);
}
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"],
            "Longest increasing subsequence: n states, and each looks back over every earlier "
            "state. The number of states times the work per state is how every DP is priced."),
        _bigo(r"""
int len = 0;
for (int x : a) {                         // tails[i]: smallest tail of an increasing run of length i+1
    int i = Arrays.binarySearch(tails, 0, len, x);
    if (i < 0) i = -(i + 1);
    tails[i] = x;
    if (i == len) len++;
}
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "The same LIS length by patience sorting: `tails` stays sorted, so the look-back "
            "becomes a binary search. Same answer, a log instead of a linear factor per state."),
        _bigo(r"""
dp[0] = true;                             // word break; s has length n
for (int i = 1; i <= n; i++)
    for (int j = 0; j < i; j++)
        if (dp[j] && dict.contains(s.substring(j, i))) { dp[i] = true; break; }
""", "O(n³)", ["O(n)", "O(n²)", "O(n³)", "O(2ⁿ)"],
            "n² (j, i) pairs, and each `substring` plus its hash is another O(n). Only letting "
            "`j` go back as far as the longest dictionary word, L, gives O(n·L²) — and without "
            "the table the plain recursion is O(2ⁿ)."),
    ],
    "dp-2d": [
        _bigo(r"""
for (int i = 1; i <= n; i++)              // strings of length n and m
    for (int j = 1; j <= m; j++)
        dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1)
                 ? dp[i - 1][j - 1] + 1
                 : Math.max(dp[i - 1][j], dp[i][j - 1]);
""", "O(n·m)", ["O(n + m)", "O(n·m)", "O(2^(n+m))", "O((n + m)²)"],
            "Longest common subsequence: n·m states, O(1) each. Each row only reads the row above, "
            "so two rows are enough — O(min(n, m)) space if you make the shorter string the "
            "columns."),
        _bigo(r"""
int lcs(int i, int j) {                   // NO memo
    if (i == n || j == m) return 0;
    if (a.charAt(i) == b.charAt(j)) return 1 + lcs(i + 1, j + 1);
    return Math.max(lcs(i + 1, j), lcs(i, j + 1));
}
""", "O(2^(n+m))", ["O(n·m)", "O(2^(n+m))", "O((n + m)²)", "O(n!)"],
            "Every mismatch branches twice, and a path can be n + m calls long. Most of those "
            "calls repeat an (i, j) already solved — which is exactly the redundancy a memo table "
            "of n·m entries removes."),
        _bigo(r"""
for (int i = 0; i < r; i++)
    for (int j = 0; j < c; j++)
        paths[i][j] = (i == 0 || j == 0) ? 1 : paths[i - 1][j] + paths[i][j - 1];
""", "O(r·c)", ["O(r + c)", "O(r·c)", "O(2^(r+c))", "O(C(r + c, r))"],
            "Grid paths: one O(1) state per cell. The *answer* is the binomial C(r+c−2, r−1), "
            "which is astronomically larger than the work — counting paths never requires listing "
            "them."),
        _bigo(r"""
int[] dp = new int[m + 1];                // edit distance, strings of length n and m
for (int j = 0; j <= m; j++) dp[j] = j;
for (int i = 1; i <= n; i++) {
    int diag = dp[0];
    dp[0] = i;
    for (int j = 1; j <= m; j++) {
        int up = dp[j];
        dp[j] = a.charAt(i - 1) == b.charAt(j - 1) ? diag : 1 + Math.min(diag, Math.min(up, dp[j - 1]));
        diag = up;                        // the old dp[j] is the next cell's diagonal
    }
}
""", "O(n·m)", ["O(n·m)", "O(n + m)", "O(m)", "O(3^(n+m))"],
            "Rolling to one row changes the *space* to O(m) and leaves the time at n·m. O(m) is the "
            "memory, not the work — and the saved `diag` is what keeps the rolled version correct."),
    ],
    "dp-knapsack": [
        _bigo(r"""
Arrays.fill(dp, INF);
dp[0] = 0;
for (int x = 1; x <= A; x++)              // amount A
    for (int c : coins)                   // k coins
        if (c <= x && dp[x - c] + 1 < dp[x]) dp[x] = dp[x - c] + 1;
""", "O(A·k)", ["O(A + k)", "O(A·k)", "O(kᴬ)", "O(A log k)"],
            "Coin change: A states, k transitions each. It is *pseudo-polynomial* — polynomial "
            "in the amount's value, exponential in the number of digits needed to write it. "
            "A = 10⁹ is 30 bits of input and a table you cannot build."),
        _bigo(r"""
for (int i = 1; i <= n; i++)              // n items, capacity W
    for (int w = 0; w <= W; w++) {
        dp[i][w] = dp[i - 1][w];
        if (wt[i - 1] <= w) dp[i][w] = Math.max(dp[i][w], dp[i - 1][w - wt[i - 1]] + val[i - 1]);
    }
""", "O(n·W)", ["O(n·W)", "O(2ⁿ)", "O(n + W)", "O(n log W)"],
            "0/1 knapsack: pseudo-polynomial again. When W is small this beats trying all 2ⁿ "
            "subsets; when W is 10⁹ the 2ⁿ approach (or meet-in-the-middle) is the one that "
            "runs."),
    ],
    "dp-intervals-states": [
        _bigo(r"""
for (int len = 2; len <= n; len++)        // interval DP
    for (int i = 0; i + len - 1 < n; i++) {
        int j = i + len - 1;
        for (int k = i; k < j; k++)
            dp[i][j] = Math.min(dp[i][j], dp[i][k] + dp[k + 1][j] + cost(i, j));   // cost O(1)
    }
""", "O(n³)", ["O(n²)", "O(n³)", "O(2ⁿ)", "O(n² log n)"],
            "O(n²) intervals, and each tries O(n) split points. Filling by increasing *length* "
            "is what guarantees both halves are solved before the whole — the loop order is the "
            "correctness argument."),
    ],
    "tries": [
        _bigo(r"""
void insert(String w) {                   // w has length L
    Node cur = root;
    for (char ch : w.toCharArray()) {
        int i = ch - 'a';
        if (cur.next[i] == null) cur.next[i] = new Node();
        cur = cur.next[i];
    }
    cur.end = true;
}
""", "O(L)", ["O(L)", "O(L log n)", "O(n·L)", "O(1)"],
            "One step per character, and the step is an array index — independent of how many "
            "words the trie already holds. That independence from n is the reason tries exist."),
        _bigo(r"""
for (String w : words) insert(w);         // n words, N characters in total
""", "O(N)", ["O(n)", "O(N)", "O(n·N)", "O(N log n)"],
            "Building a trie is linear in the total input size. Memory is the real cost: up to N "
            "nodes, each with a 26-slot array in this layout — which is why a `HashMap` child map "
            "is used when the alphabet is large."),
        _bigo(r"""
boolean startsWith(String p) {            // p has length P
    Node cur = root;
    for (char ch : p.toCharArray()) {
        cur = cur.next[ch - 'a'];
        if (cur == null) return false;
    }
    return true;
}
""", "O(P)", ["O(P)", "O(n)", "O(P log n)", "O(N)"],
            "Prefix lookup costs the prefix length, nothing else. A `HashSet` of whole words "
            "cannot answer \"does anything start with this?\" without scanning every word."),
        _bigo(r"""
List<String> complete(String p) {         // prefix length P
    Node cur = walk(p);                   // O(P), null if absent
    List<String> out = new ArrayList<>();
    if (cur != null) collect(cur, new StringBuilder(p), out);   // DFS over the subtree
    return out;
}
""", "O(P + K)", ["O(P)", "O(P + K)", "O(K log K)", "O(N)"],
            "Autocomplete: O(P) to reach the node, then a DFS proportional to K, the number of "
            "characters in the subtree below it (the output and the paths to it). A short prefix "
            "on a big dictionary makes K large — which is why real autocomplete caps the "
            "results."),
        _bigo(r"""
Set<String> prefixes = new HashSet<>();
for (String w : words)                    // n words, each of length L
    for (int i = 1; i <= w.length(); i++)
        prefixes.add(w.substring(0, i));
""", "O(n·L²)", ["O(n·L)", "O(n·L²)", "O(n²·L)", "O(L²)"],
            "Every word has L prefixes, and each is copied and hashed in O(L). A trie stores the "
            "same prefixes *shared*: one node per character, O(n·L) to build."),
    ],
}


def _attach_bigo():
    by_key = {u["key"]: u for u in _UNITS}
    for key, items in _BIGO_BY_UNIT.items():
        assert key in by_key, f"dsa_bigo.py: no unit {key!r}"
        by_key[key]["bigo"].extend(items)


_attach_bigo()
