# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Java core-concept drills — backfills fill-in-the-blank exercises for the
# high-value interview concepts that shipped with lessons but NO practice:
# Strings (string_basics / char_arrays / canonical), Hashing (hashing /
# complement), Stack / Queue, Recursion, Binary Search, Sorting.
#
# exec()'d inside gen_seed.py's namespace (see the hook after the
# typescript_defs.py include), so it reuses ex() and prog(). Each drill is a
# self-contained stdin/stdout Java program graded by the SAME exact judge as
# the Foundations drills (null problemId -> JudgeConfig::exact). Every solution
# is proven by tests/verify_exercises.rs (runs it through the real judge).
#
# Concepts already have lessons + CATEGORY; this only adds EXERCISES entries,
# so no SEED_VERSION bump (concepts are embedded JSON, not SQLite).
# ---------------------------------------------------------------------------


# A full class with a static helper (prog() only wraps a main body, so
# recursion drills that need a helper method use this instead).
def _cls(members):
    return (
        "import java.util.*;\n\n"
        "public class Main {\n"
        f"{members}\n"
        "}\n"
    )


JAVA_CORE_EXERCISES = {
    # === Strings ==========================================================
    "string_basics": [
        ex(
            "string_basics-count", "Count a letter",
            "Replace `____` with the condition that is true when the character at index `i` is `'a'`, so the program counts the `a`s in the line.",
            prog(
                "        String s = sc.nextLine();\n"
                "        int count = 0;\n"
                "        for (int i = 0; i < s.length(); i++) {\n"
                "            if (s.charAt(i) == 'a') count++;\n"
                "        }\n"
                "        System.out.println(count);"),
            ["s.charAt(i) == 'a'"],
            [("banana", "3"), ("apple", "1"), ("xyz", "0")],
            hint="charAt(i) returns the character at position i; compare it with the char literal 'a'.",
        ),
        ex(
            "string_basics-length", "Length of a word",
            "Replace `____` to print the number of characters in `s`. On a String, length is a method call.",
            prog(
                "        String s = sc.next();\n"
                "        System.out.println(s.length());"),
            ["s.length()"],
            [("hello", "5"), ("a", "1"), ("banana", "6")],
            hint="Strings use s.length() (with parentheses); arrays use arr.length (without).",
        ),
        ex(
            "string_basics-vowels", "Count the vowels",
            "Write the solution: count how many characters of the line are vowels (a, e, i, o, u) and print the total.",
            prog(
                "        String s = sc.nextLine();\n"
                "        int count = 0;\n"
                "        for (int i = 0; i < s.length(); i++) {\n"
                "            char ch = s.charAt(i);\n"
                "            if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') count++;\n"
                "        }\n"
                "        System.out.println(count);"),
            ["        int count = 0;\n"
             "        for (int i = 0; i < s.length(); i++) {\n"
             "            char ch = s.charAt(i);\n"
             "            if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') count++;\n"
             "        }\n"
             "        System.out.println(count);"],
            [("banana", "3"), ("sky", "0"), ("education", "5")],
            hint="Walk each character with charAt(i); add to the count when it is one of the five vowels.",
        ),
    ],
    "char_arrays": [
        ex(
            "char_arrays-index", "Letter to index",
            "Replace `____` with the expression that maps a lowercase letter to 0..25 (`'a'` -> 0, `'z'` -> 25).",
            prog(
                "        String s = sc.next();\n"
                "        char c = s.charAt(0);\n"
                "        System.out.println(c - 'a');"),
            ["c - 'a'"],
            [("a", "0"), ("z", "25"), ("c", "2")],
            hint="Subtracting the char 'a' turns a letter into its 0-based offset: c - 'a'.",
        ),
        ex(
            "char_arrays-rebuild", "Rebuild the string",
            "The characters were reversed in place inside `c`. Replace `____` with the expression that turns the char array back into a String.",
            prog(
                "        char[] c = sc.next().toCharArray();\n"
                "        int i = 0, j = c.length - 1;\n"
                "        while (i < j) {\n"
                "            char t = c[i];\n"
                "            c[i++] = c[j];\n"
                "            c[j--] = t;\n"
                "        }\n"
                "        System.out.println(new String(c));"),
            ["new String(c)"],
            [("code", "edoc"), ("abc", "cba"), ("racecar", "racecar")],
            hint="new String(charArray) builds a String from a char[].",
        ),
        ex(
            "char_arrays-maxfreq", "Most frequent letter count",
            "Write the solution: using a length-26 int array indexed by `ch - 'a'`, count each letter of the lowercase word and print the highest single-letter count.",
            prog(
                "        String s = sc.next();\n"
                "        int[] freq = new int[26];\n"
                "        for (char ch : s.toCharArray()) freq[ch - 'a']++;\n"
                "        int max = 0;\n"
                "        for (int f : freq) if (f > max) max = f;\n"
                "        System.out.println(max);"),
            ["        int[] freq = new int[26];\n"
             "        for (char ch : s.toCharArray()) freq[ch - 'a']++;\n"
             "        int max = 0;\n"
             "        for (int f : freq) if (f > max) max = f;\n"
             "        System.out.println(max);"],
            [("banana", "3"), ("abc", "1"), ("aabbbc", "3")],
            hint="freq[ch - 'a']++ tallies each letter; then scan freq for the largest value.",
        ),
    ],
    "canonical": [
        ex(
            "canonical-sortkey", "Sort the letters",
            "Replace `____` with the call that sorts the char array `c` in place, so the printed key is the letters in order (`tea` -> `aet`).",
            prog(
                "        char[] c = sc.next().toCharArray();\n"
                "        Arrays.sort(c);\n"
                "        System.out.println(new String(c));"),
            ["Arrays.sort(c);"],
            [("tea", "aet"), ("banana", "aaabnn"), ("dcba", "abcd")],
            hint="Arrays.sort(c) orders the characters; the sorted letters are the canonical key.",
        ),
        ex(
            "canonical-anagram", "Are they anagrams?",
            "Two words are read. Replace `____` with the test that is true when their sorted-letter keys are equal.",
            prog(
                "        char[] a = sc.next().toCharArray();\n"
                "        char[] b = sc.next().toCharArray();\n"
                "        Arrays.sort(a);\n"
                "        Arrays.sort(b);\n"
                "        System.out.println(new String(a).equals(new String(b)));"),
            ["new String(a).equals(new String(b))"],
            [("eat tea", "true"), ("abc abd", "false"), ("listen silent", "true")],
            hint="Compare the two canonical keys with .equals — equal keys mean anagrams.",
        ),
        ex(
            "canonical-groups", "Count anagram groups",
            "The first line is a count `n`, then `n` words. Write the solution: reduce each word to its sorted-letter key, and print how many DISTINCT keys there are.",
            prog(
                "        int n = sc.nextInt();\n"
                "        Set<String> keys = new HashSet<>();\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            char[] c = sc.next().toCharArray();\n"
                "            Arrays.sort(c);\n"
                "            keys.add(new String(c));\n"
                "        }\n"
                "        System.out.println(keys.size());"),
            ["        Set<String> keys = new HashSet<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            char[] c = sc.next().toCharArray();\n"
             "            Arrays.sort(c);\n"
             "            keys.add(new String(c));\n"
             "        }\n"
             "        System.out.println(keys.size());"],
            [("3\neat tea ate", "1"), ("3\nabc bca xyz", "2"), ("2\ncat dog", "2")],
            hint="Anagrams share a canonical key, so a Set of keys counts the distinct groups.",
        ),
    ],
    # === Data Structures — hashing / complement / stack / queue ===========
    "hashing": [
        ex(
            "hashing-dup", "Spot a duplicate",
            "Replace `____` with the condition that is true when `x` was ALREADY in the set (`add` returns false in that case).",
            prog(
                "        int n = sc.nextInt();\n"
                "        Set<Integer> seen = new HashSet<>();\n"
                "        boolean dup = false;\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            int x = sc.nextInt();\n"
                "            if (!seen.add(x)) { dup = true; break; }\n"
                "        }\n"
                "        System.out.println(dup ? \"duplicate\" : \"unique\");"),
            ["!seen.add(x)"],
            [("4\n1 3 2 3", "duplicate"), ("3\n1 2 3", "unique"), ("2\n5 5", "duplicate")],
            hint="seen.add(x) returns false when x is already present, so !seen.add(x) detects a repeat.",
        ),
        ex(
            "hashing-freq", "Highest frequency",
            "Replace `____` with the line that increments the count of `x` in the map (creating it at 1 the first time).",
            prog(
                "        int n = sc.nextInt();\n"
                "        Map<Integer,Integer> freq = new HashMap<>();\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            int x = sc.nextInt();\n"
                "            freq.merge(x, 1, Integer::sum);\n"
                "        }\n"
                "        int best = 0;\n"
                "        for (int c : freq.values()) best = Math.max(best, c);\n"
                "        System.out.println(best);"),
            ["freq.merge(x, 1, Integer::sum);"],
            [("4\n1 2 2 2", "3"), ("3\n5 6 7", "1"), ("5\n1 1 2 2 2", "3")],
            hint="map.merge(x, 1, Integer::sum) adds 1 to x's count, starting from 1.",
        ),
        ex(
            "hashing-firstunique", "First non-repeating value",
            "Write the solution: count every value, then scan the array IN ORDER and print the first value whose count is 1 (or `-1` if none).",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        Map<Integer,Integer> cnt = new HashMap<>();\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            a[i] = sc.nextInt();\n"
                "            cnt.merge(a[i], 1, Integer::sum);\n"
                "        }\n"
                "        int ans = -1;\n"
                "        for (int x : a) {\n"
                "            if (cnt.get(x) == 1) { ans = x; break; }\n"
                "        }\n"
                "        System.out.println(ans);"),
            ["        int ans = -1;\n"
             "        for (int x : a) {\n"
             "            if (cnt.get(x) == 1) { ans = x; break; }\n"
             "        }\n"
             "        System.out.println(ans);"],
            [("5\n1 2 2 3 1", "3"), ("3\n1 1 2", "2"), ("2\n4 4", "-1")],
            hint="First build the counts, then walk the original order and stop at the first count of 1.",
        ),
    ],
    "complement": [
        ex(
            "complement-value", "The missing partner",
            "For a pair summing to `target`, the partner of `x` is `target - x`. Replace `____` with that complement.",
            prog(
                "        int target = sc.nextInt();\n"
                "        int x = sc.nextInt();\n"
                "        System.out.println(target - x);"),
            ["target - x"],
            [("10 3", "7"), ("5 5", "0"), ("8 10", "-2")],
            hint="If x + partner = target, then partner = target - x.",
        ),
        ex(
            "complement-twosum", "Does a pair sum to target?",
            "Replace `____` with the lookup that checks whether the partner of `x` (its complement) has already been seen.",
            prog(
                "        int target = sc.nextInt();\n"
                "        int n = sc.nextInt();\n"
                "        Set<Integer> seen = new HashSet<>();\n"
                "        boolean found = false;\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            int x = sc.nextInt();\n"
                "            if (seen.contains(target - x)) { found = true; break; }\n"
                "            seen.add(x);\n"
                "        }\n"
                "        System.out.println(found ? \"found\" : \"none\");"),
            ["seen.contains(target - x)"],
            [("10 4\n2 7 4 8", "found"), ("5 3\n1 2 9", "none"), ("6 2\n3 3", "found")],
            hint="Check for target - x BEFORE inserting x, so a value is never paired with itself.",
        ),
        ex(
            "complement-countpairs", "Count pairs that sum to target",
            "Write the solution: for each value add how many earlier values equal its complement, then record the value. Print the total number of pairs.",
            prog(
                "        int target = sc.nextInt();\n"
                "        int n = sc.nextInt();\n"
                "        Map<Integer,Integer> seen = new HashMap<>();\n"
                "        int pairs = 0;\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            int x = sc.nextInt();\n"
                "            pairs += seen.getOrDefault(target - x, 0);\n"
                "            seen.merge(x, 1, Integer::sum);\n"
                "        }\n"
                "        System.out.println(pairs);"),
            ["        int pairs = 0;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            int x = sc.nextInt();\n"
             "            pairs += seen.getOrDefault(target - x, 0);\n"
             "            seen.merge(x, 1, Integer::sum);\n"
             "        }\n"
             "        System.out.println(pairs);"],
            [("6 4\n1 5 3 3", "2"), ("10 3\n2 7 4", "0"), ("4 4\n2 2 2 2", "6")],
            hint="Each new x forms a pair with every earlier complement; getOrDefault handles the missing case.",
        ),
    ],
    "stack": [
        ex(
            "stack-push", "Push the openers",
            "Replace `____` with the statement that pushes an opening bracket onto the stack.",
            prog(
                "        String s = sc.next();\n"
                "        Deque<Character> st = new ArrayDeque<>();\n"
                "        boolean ok = true;\n"
                "        for (char c : s.toCharArray()) {\n"
                "            if (c == '(') st.push(c);\n"
                "            else if (st.isEmpty()) { ok = false; break; }\n"
                "            else st.pop();\n"
                "        }\n"
                "        System.out.println(ok && st.isEmpty());"),
            ["st.push(c);"],
            [("(())", "true"), ("(()", "false"), ("())", "false")],
            hint="st.push(c) puts the opener on top; a closer later pops it back off.",
        ),
        ex(
            "stack-reverse", "Reverse with a stack",
            "Replace `____` to push each number onto the stack as it is read, so popping them prints the list reversed.",
            prog(
                "        int n = sc.nextInt();\n"
                "        Deque<Integer> st = new ArrayDeque<>();\n"
                "        for (int i = 0; i < n; i++) st.push(sc.nextInt());\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        while (!st.isEmpty()) sb.append(st.pop()).append(' ');\n"
                "        System.out.println(sb.toString().trim());"),
            ["st.push(sc.nextInt())"],
            [("3\n1 2 3", "3 2 1"), ("1\n5", "5"), ("4\n1 2 3 4", "4 3 2 1")],
            hint="A stack is last-in-first-out, so pushing in order and popping reverses it.",
        ),
        ex(
            "stack-brackets", "Match three bracket types",
            "Write the solution: verify `( ) [ ] { }` are balanced and properly nested. Push openers; each closer must pop its matching opener. Print `true`/`false`.",
            prog(
                "        String s = sc.next();\n"
                "        Deque<Character> st = new ArrayDeque<>();\n"
                "        Map<Character,Character> match = Map.of(')', '(', ']', '[', '}', '{');\n"
                "        boolean ok = true;\n"
                "        for (char c : s.toCharArray()) {\n"
                "            if (c == '(' || c == '[' || c == '{') st.push(c);\n"
                "            else if (st.isEmpty() || st.pop() != match.get(c)) { ok = false; break; }\n"
                "        }\n"
                "        System.out.println(ok && st.isEmpty());"),
            ["        Deque<Character> st = new ArrayDeque<>();\n"
             "        Map<Character,Character> match = Map.of(')', '(', ']', '[', '}', '{');\n"
             "        boolean ok = true;\n"
             "        for (char c : s.toCharArray()) {\n"
             "            if (c == '(' || c == '[' || c == '{') st.push(c);\n"
             "            else if (st.isEmpty() || st.pop() != match.get(c)) { ok = false; break; }\n"
             "        }\n"
             "        System.out.println(ok && st.isEmpty());"],
            [("([])", "true"), ("([)]", "false"), ("{[()]}", "true")],
            hint="On a closer, the top of the stack must be its matching opener; the stack must end empty.",
        ),
    ],
    "queue": [
        ex(
            "queue-offer", "Join the queue",
            "Replace `____` to add each number to the back of the queue, so polling returns them in arrival order.",
            prog(
                "        int n = sc.nextInt();\n"
                "        Queue<Integer> q = new ArrayDeque<>();\n"
                "        for (int i = 0; i < n; i++) q.offer(sc.nextInt());\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        while (!q.isEmpty()) sb.append(q.poll()).append(' ');\n"
                "        System.out.println(sb.toString().trim());"),
            ["q.offer(sc.nextInt())"],
            [("3\n1 2 3", "1 2 3"), ("1\n9", "9"), ("4\n4 3 2 1", "4 3 2 1")],
            hint="offer adds to the back; poll removes from the front — FIFO keeps arrival order.",
        ),
        ex(
            "queue-first", "First served",
            "Replace `____` with the call that removes and returns the front of the queue.",
            prog(
                "        int n = sc.nextInt();\n"
                "        Queue<Integer> q = new ArrayDeque<>();\n"
                "        for (int i = 0; i < n; i++) q.offer(sc.nextInt());\n"
                "        System.out.println(q.poll());"),
            ["q.poll()"],
            [("3\n5 6 7", "5"), ("1\n9", "9"), ("2\n2 1", "2")],
            hint="poll() takes the item at the front — the one that was added first.",
        ),
        ex(
            "queue-potato", "Hot potato (last one standing)",
            "Players `1..n` stand in a circle; every `k`th player is removed. Write the solution using a queue: move `k-1` players to the back, remove the next, repeat until one remains, then print them.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int k = sc.nextInt();\n"
                "        Queue<Integer> q = new ArrayDeque<>();\n"
                "        for (int i = 1; i <= n; i++) q.offer(i);\n"
                "        while (q.size() > 1) {\n"
                "            for (int i = 0; i < k - 1; i++) q.offer(q.poll());\n"
                "            q.poll();\n"
                "        }\n"
                "        System.out.println(q.poll());"),
            ["        while (q.size() > 1) {\n"
             "            for (int i = 0; i < k - 1; i++) q.offer(q.poll());\n"
             "            q.poll();\n"
             "        }\n"
             "        System.out.println(q.poll());"],
            [("5 2", "3"), ("1 3", "1"), ("7 3", "4")],
            hint="Rotating k-1 to the back puts the k-th player at the front, ready to be polled off.",
        ),
    ],
    # === Recursion ========================================================
    "recursion": [
        ex(
            "recursion-factorial", "Factorial",
            "Replace `____` with the recursive step: `n` times the factorial of `n - 1`.",
            _cls(
                "    static long fact(int n) {\n"
                "        if (n <= 1) return 1;\n"
                "        return n * fact(n - 1);\n"
                "    }\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "        int n = sc.nextInt();\n"
                "        System.out.println(fact(n));\n"
                "    }"),
            ["return n * fact(n - 1);"],
            [("4", "24"), ("0", "1"), ("5", "120")],
            hint="fact(n) = n * fact(n - 1); the base case n <= 1 stops the descent.",
        ),
        ex(
            "recursion-basecase", "The base case",
            "Replace `____` with the base-case condition that stops the recursion (sum of 0 is 0).",
            _cls(
                "    static int sum(int n) {\n"
                "        if (n == 0) return 0;\n"
                "        return n + sum(n - 1);\n"
                "    }\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "        System.out.println(sum(sc.nextInt()));\n"
                "    }"),
            ["n == 0"],
            [("5", "15"), ("1", "1"), ("10", "55")],
            hint="Without a base case the calls never stop; sum(0) should return 0.",
        ),
        ex(
            "recursion-fib", "Nth Fibonacci",
            "Write the recursive `fib` (fib(0)=0, fib(1)=1). Fill in both the base case and the recursive step.",
            _cls(
                "    static long fib(int n) {\n"
                "        if (n < 2) return n;\n"
                "        return fib(n - 1) + fib(n - 2);\n"
                "    }\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "        System.out.println(fib(sc.nextInt()));\n"
                "    }"),
            ["        if (n < 2) return n;\n"
             "        return fib(n - 1) + fib(n - 2);"],
            [("0", "0"), ("7", "13"), ("10", "55")],
            hint="Below 2, fib(n) is n itself; otherwise sum the two previous Fibonacci numbers.",
        ),
    ],
    # === Searching & Sorting — binary search / sorting ====================
    "binary_search": [
        ex(
            "binary_search-mid", "The midpoint",
            "Replace `____` with the overflow-safe midpoint of `lo` and `hi`.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int target = sc.nextInt();\n"
                "        int lo = 0, hi = n - 1, ans = -1;\n"
                "        while (lo <= hi) {\n"
                "            int mid = lo + (hi - lo) / 2;\n"
                "            if (a[mid] == target) { ans = mid; break; }\n"
                "            else if (a[mid] < target) lo = mid + 1;\n"
                "            else hi = mid - 1;\n"
                "        }\n"
                "        System.out.println(ans);"),
            ["lo + (hi - lo) / 2"],
            [("5\n1 3 5 7 9\n7", "3"), ("5\n1 3 5 7 9\n4", "-1"), ("3\n2 4 6\n2", "0")],
            hint="lo + (hi - lo) / 2 is the midpoint without the overflow risk of (lo + hi) / 2.",
        ),
        ex(
            "binary_search-loop", "The loop condition",
            "Replace `____` with the condition that keeps the search running while the window `[lo, hi]` is non-empty.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int target = sc.nextInt();\n"
                "        int lo = 0, hi = n - 1;\n"
                "        boolean found = false;\n"
                "        while (lo <= hi) {\n"
                "            int mid = lo + (hi - lo) / 2;\n"
                "            if (a[mid] == target) { found = true; break; }\n"
                "            else if (a[mid] < target) lo = mid + 1;\n"
                "            else hi = mid - 1;\n"
                "        }\n"
                "        System.out.println(found);"),
            ["lo <= hi"],
            [("5\n1 3 5 7 9\n5", "true"), ("4\n2 4 6 8\n3", "false"), ("3\n1 2 3\n3", "true")],
            hint="Keep going while lo <= hi; once lo passes hi the window is empty.",
        ),
        ex(
            "binary_search-first", "First occurrence",
            "The sorted array may contain duplicates. Write the solution: find the FIRST index equal to `target` (keep searching left after a hit), or print `-1`.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int target = sc.nextInt();\n"
                "        int lo = 0, hi = n - 1, ans = -1;\n"
                "        while (lo <= hi) {\n"
                "            int mid = lo + (hi - lo) / 2;\n"
                "            if (a[mid] == target) { ans = mid; hi = mid - 1; }\n"
                "            else if (a[mid] < target) lo = mid + 1;\n"
                "            else hi = mid - 1;\n"
                "        }\n"
                "        System.out.println(ans);"),
            ["        int lo = 0, hi = n - 1, ans = -1;\n"
             "        while (lo <= hi) {\n"
             "            int mid = lo + (hi - lo) / 2;\n"
             "            if (a[mid] == target) { ans = mid; hi = mid - 1; }\n"
             "            else if (a[mid] < target) lo = mid + 1;\n"
             "            else hi = mid - 1;\n"
             "        }\n"
             "        System.out.println(ans);"],
            [("6\n1 2 2 2 3 4\n2", "1"), ("5\n1 2 3 4 5\n6", "-1"), ("4\n2 2 2 2\n2", "0")],
            hint="On a match, record it but move hi left (hi = mid - 1) to look for an earlier one.",
        ),
    ],
    "sorting": [
        ex(
            "sorting-asc", "Sort ascending",
            "Replace `____` with the call that sorts the primitive array `a` in ascending order.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        Arrays.sort(a);\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        for (int x : a) sb.append(x).append(' ');\n"
                "        System.out.println(sb.toString().trim());"),
            ["Arrays.sort(a);"],
            [("3\n3 1 2", "1 2 3"), ("1\n5", "5"), ("5\n5 4 3 2 1", "1 2 3 4 5")],
            hint="Arrays.sort(a) sorts an int[] ascending in place.",
        ),
        ex(
            "sorting-desc", "Sort descending",
            "Primitive `int[]` has no comparator, so this uses `Integer[]`. Replace `____` with the comparator that sorts largest-first.",
            prog(
                "        int n = sc.nextInt();\n"
                "        Integer[] a = new Integer[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        Arrays.sort(a, Comparator.reverseOrder());\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        for (int x : a) sb.append(x).append(' ');\n"
                "        System.out.println(sb.toString().trim());"),
            ["Comparator.reverseOrder()"],
            [("3\n1 3 2", "3 2 1"), ("1\n5", "5"), ("4\n4 1 3 2", "4 3 2 1")],
            hint="Comparator.reverseOrder() gives descending order (needs Integer[], not int[]).",
        ),
        ex(
            "sorting-kth", "Kth smallest",
            "Write the solution: read `n` and `k`, then `n` numbers; sort them and print the k-th smallest (1-indexed).",
            prog(
                "        int n = sc.nextInt();\n"
                "        int k = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        Arrays.sort(a);\n"
                "        System.out.println(a[k - 1]);"),
            ["        Arrays.sort(a);\n"
             "        System.out.println(a[k - 1]);"],
            [("5 2\n5 1 4 2 3", "2"), ("3 1\n9 7 8", "7"), ("4 4\n1 2 3 4", "4")],
            hint="After sorting ascending, the k-th smallest sits at index k - 1.",
        ),
    ],
}
EXERCISES.update(JAVA_CORE_EXERCISES)
