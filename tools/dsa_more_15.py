# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 15 — extra practice: tries, hashing, math, bits, windows, prefix sums.
#
#   count-distinct-substrings      insert every suffix into a trie; new nodes are new substrings
#   search-suggestions-system      sort once; each prefix is a contiguous block of the sorted list
#   bulls-and-cows                 exact matches first, then the overlap of the remaining counts
#   longest-harmonious-subseq      count values; pair each with value + 1
#   duplicate-subtrees-count       serialise every subtree; a repeated string is a repeated subtree
#   excel-column-number            base 26 with no zero digit
#   add-binary                     schoolbook addition from the right with a carry
#   min-swaps-group-ones           a circular window the size of the number of ones
#   min-start-value                the lowest prefix sum decides the start
#   valid-palindrome-ii            on the first mismatch, try skipping either side once
# ===========================================================================

_p(
    "count-distinct-substrings", "Count Distinct Substrings", "Medium",
    topics=["Strings", "Data Structures"], subtopics=["Trie"], companies=["Google"],
    shape="str", ret="long", todo="insert every suffix into a trie and count the nodes created",
    description=(
        "Count the **distinct** non-empty substrings of `s`.\n\n"
        "### Input\nOne line: `s`.\n\n### Output\nThe number of distinct substrings."
    ),
    constraints="1 ≤ |s| ≤ 300\ns consists of lowercase English letters.",
    hints=[
        "Every substring is a prefix of some suffix.",
        "Insert all n suffixes into a trie. Each trie node (except the root) spells one distinct prefix of a suffix.",
        "So the number of nodes created is the answer — equal substrings share a path and create no new node.",
    ],
    opt=("O(n²)", "O(n²)", "n suffix insertions of up to n characters; at most n(n+1)/2 nodes."),
    editorial=(
        "## The one thing this teaches\n**A trie deduplicates prefixes by construction.** Two equal "
        "strings follow the same path, so inserting a set of strings creates exactly one node per "
        "distinct prefix. Since every substring is a prefix of a suffix, inserting all suffixes "
        "counts all distinct substrings.\n\n"
        "## Approach\n```java\nint count = 0;\nfor (int i = 0; i < n; i++) {           // suffix starting at i\n"
        "    Node cur = root;\n    for (int j = i; j < n; j++) {\n        int c = s.charAt(j) - 'a';\n"
        "        if (cur.next[c] == null) { cur.next[c] = new Node(); count++; }\n"
        "        cur = cur.next[c];\n    }\n}\n```\n\n"
        "## Compared with a hash set\nA `HashSet<String>` of all substrings is O(n³) — each "
        "substring is copied and hashed. The trie shares the copies. For long strings, a suffix "
        "array or suffix automaton does it in O(n log n) or O(n)."
    ),
    py='''
def solve(s):
    return len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)})
''',
    java='''
    static class Node {
        Node[] next = new Node[26];
    }

    static long solve(String s) {
        Node root = new Node();
        long count = 0;
        for (int i = 0; i < s.length(); i++) {
            Node cur = root;
            for (int j = i; j < s.length(); j++) {
                int c = s.charAt(j) - 'a';
                if (cur.next[c] == null) { cur.next[c] = new Node(); count++; }
                cur = cur.next[c];
            }
        }
        return count;
    }
''',
    examples=[("Example 1", "aabbaba\n"), ("Example 2", "abcdefg\n")],
    hidden=[
        ("Single letter", "a\n"),
        ("One repeated letter", "aaaa\n"),
        ("Alternating", "abab\n"),
        ("banana", "banana\n"),
    ],
    expl=[
        "21 distinct substrings out of 28 in total.",
        "All 7·8/2 = 28 substrings are different.",
    ],
    prereqs=[
        ("trie", "Inserting strings into a trie creates one node per distinct prefix."),
        ("string_basics", "Every substring is a prefix of some suffix."),
    ],
)

_p(
    "search-suggestions-system", "Search Suggestions System", "Medium",
    topics=["Strings", "Data Structures"], subtopics=["Trie", "Binary Search", "Sorting"], companies=["Amazon"],
    shape="str_list", ret="String", todo="sort products; for each prefix, binary search its first match and take up to three",
    description=(
        "As each letter of `searchWord` is typed, suggest up to **three** products that start with "
        "the typed prefix, in lexicographic order.\n\n"
        "### Input\n- Line 1: `searchWord`.\n- Line 2: the number of products.\n- Line 3: the products.\n\n"
        "### Output\nOne line per typed prefix: the suggestions separated by spaces, or `-` if there are none."
    ),
    constraints="1 ≤ |searchWord| ≤ 1000\n1 ≤ products ≤ 1000, distinct\nAll strings are lowercase letters.",
    hints=[
        "In a sorted list, all words starting with a given prefix are contiguous.",
        "For each prefix, binary search for the first word ≥ prefix; the next (up to) three words are the candidates.",
        "Keep only candidates that actually start with the prefix. A trie storing the three smallest words per node also works.",
    ],
    opt=("O(n log n + L log n)", "O(1) extra", "One sort, then a binary search per typed prefix."),
    editorial=(
        "## The one thing this teaches\n**A sorted list is an implicit trie.** Every trie node "
        "corresponds to a contiguous block of the sorted words — the ones with that prefix. Binary "
        "search finds the start of the block; the first three entries are the three smallest.\n\n"
        "## Approach\n```java\nArrays.sort(products);\nString prefix = \"\";\nfor (char c : searchWord.toCharArray()) {\n"
        "    prefix += c;\n    int i = lowerBound(products, prefix);\n"
        "    List<String> got = new ArrayList<>();\n"
        "    for (int j = i; j < Math.min(i + 3, n) && products[j].startsWith(prefix); j++) got.add(products[j]);\n"
        "    output(got);\n}\n```\n\n"
        "## The trie version\nInsert products in sorted order into a trie whose nodes keep a list of "
        "at most three words; the first three to pass through a node are its answer. More memory, "
        "and O(L) per keystroke with no search — the shape of real autocomplete."
    ),
    py='''
def solve(s, words):
    products = sorted(words)
    out = []
    for i in range(1, len(s) + 1):
        prefix = s[:i]
        j = bisect_left(products, prefix)
        got = [w for w in products[j:j + 3] if w.startswith(prefix)]
        out.append(" ".join(got) if got else "-")
    return "\\n".join(out)
''',
    java='''
    static class Node {
        Node[] next = new Node[26];
        List<String> top = new ArrayList<>();
    }

    static String solve(String word, String[] products) {
        String[] sorted = products.clone();
        Arrays.sort(sorted);
        Node root = new Node();
        for (String p : sorted) {
            Node cur = root;
            for (int i = 0; i < p.length(); i++) {
                int c = p.charAt(i) - 'a';
                if (cur.next[c] == null) cur.next[c] = new Node();
                cur = cur.next[c];
                if (cur.top.size() < 3) cur.top.add(p);
            }
        }
        StringBuilder sb = new StringBuilder();
        Node cur = root;
        for (int i = 0; i < word.length(); i++) {
            if (cur != null) cur = cur.next[word.charAt(i) - 'a'];
            if (i > 0) sb.append('\\n');
            if (cur == null || cur.top.isEmpty()) sb.append('-');
            else sb.append(String.join(" ", cur.top));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "mouse\n5\nmobile mouse moneypot monitor mousepad\n"),
        ("Example 2", "havana\n1\nhavana\n"),
    ],
    hidden=[
        ("Suggestions narrow", "bags\n5\nbags baggage banner box cloths\n"),
        ("Nothing matches", "xyz\n2\nabc abd\n"),
        ("Matches then stop", "bat\n3\nba bb bat\n"),
    ],
    expl=[
        "`m` and `mo` suggest the three smallest; from `mou` only `mouse` and `mousepad` match.",
        "Every prefix of `havana` matches the one product.",
    ],
    prereqs=[
        ("trie", "Each prefix's matching words form one trie node — or one contiguous sorted block."),
        ("binary_search", "Finding the first word not less than the prefix."),
    ],
)

_p(
    "bulls-and-cows", "Bulls and Cows", "Medium",
    topics=["Hashing", "Strings"], subtopics=["Counting"], companies=["Google", "Amazon"],
    shape="str2", ret="String", todo="count exact matches as bulls; for the rest, add min(secret count, guess count) per digit as cows",
    description=(
        "In Bulls and Cows, a **bull** is a digit of the guess in the right position, and a **cow** "
        "is a digit that exists in the secret but in a different position (each secret digit can "
        "be matched at most once). Report the hint as `xAyB`: x bulls and y cows.\n\n"
        "### Input\n- Line 1: the secret.\n- Line 2: the guess (same length).\n\n### Output\n`xAyB`."
    ),
    constraints="1 ≤ length ≤ 1000\nBoth strings consist of digits and have equal length.",
    hints=[
        "Bulls are easy: positions where the characters are equal.",
        "Cows must not reuse a secret digit that is already a bull, or already a cow.",
        "Count the digits at non-bull positions for each string separately; cows = Σ over digits of min(secretCount, guessCount).",
    ],
    opt=("O(n)", "O(1)", "One pass and two 10-slot count arrays."),
    editorial=(
        "## The one thing this teaches\n**Matching with multiplicity is a minimum of counts.** How "
        "many times can digit d be paired between two bags? As many as the smaller bag has. "
        "Summing that over the ten digits pairs everything that can pair, with no digit used "
        "twice.\n\n"
        "## Approach\n```java\nint bulls = 0;\nint[] s = new int[10], g = new int[10];\n"
        "for (int i = 0; i < n; i++) {\n"
        "    if (secret.charAt(i) == guess.charAt(i)) bulls++;\n"
        "    else { s[secret.charAt(i) - '0']++; g[guess.charAt(i) - '0']++; }\n}\n"
        "int cows = 0;\nfor (int d = 0; d < 10; d++) cows += Math.min(s[d], g[d]);\n"
        "return bulls + \"A\" + cows + \"B\";\n```\n\n"
        "## Why exclude bulls from the counts\n`secret = 1123`, `guess = 0111`: position 1 is a "
        "bull (the `1`). Counting it again as available for cows would give 2 cows; excluding "
        "bull positions leaves secret `{1,2,3}` and guess `{0,1,1}`, which share one `1` — 1A1B."
    ),
    py='''
def solve(s, t):
    bulls = sum(1 for a, b in zip(s, t) if a == b)
    sc = Counter(a for a, b in zip(s, t) if a != b)
    gc = Counter(b for a, b in zip(s, t) if a != b)
    cows = sum(min(sc[d], gc[d]) for d in sc)
    return f"{bulls}A{cows}B"
''',
    java='''
    static String solve(String secret, String guess) {
        int bulls = 0;
        int[] s = new int[10], g = new int[10];
        for (int i = 0; i < secret.length(); i++) {
            if (secret.charAt(i) == guess.charAt(i)) bulls++;
            else { s[secret.charAt(i) - '0']++; g[guess.charAt(i) - '0']++; }
        }
        int cows = 0;
        for (int d = 0; d < 10; d++) cows += Math.min(s[d], g[d]);
        return bulls + "A" + cows + "B";
    }
''',
    examples=[("Example 1", "1807\n7810\n"), ("Example 2", "1123\n0111\n")],
    hidden=[
        ("Nothing in common", "1\n0\n"),
        ("Perfect guess", "1234\n1234\n"),
        ("All cows", "1122\n2211\n"),
        ("Leading zeros", "0000\n0001\n"),
    ],
    expl=[
        "The 8 is a bull; 1, 0 and 7 are cows.",
        "The second 1 is a bull; one more 1 is a cow.",
    ],
    prereqs=[
        ("hashing", "Digit counts at the non-bull positions of each string."),
        ("string_basics", "Comparing two equal-length strings position by position."),
    ],
)

_p(
    "longest-harmonious-subseq", "Longest Harmonious Subsequence", "Easy",
    topics=["Hashing", "Arrays"], subtopics=["Counting"], companies=["Amazon"],
    shape="arr", ret="int", todo="count values; for each x with x + 1 present, the candidate is count[x] + count[x + 1]",
    description=(
        "A **harmonious** array has a maximum and a minimum that differ by **exactly 1**. Find the "
        "length of the longest harmonious subsequence.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n### Output\nThe maximum length, or 0."
    ),
    constraints="1 ≤ n ≤ 2·10^4\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "A subsequence ignores order, so only how many of each value you take matters.",
        "A harmonious subsequence uses only two values, x and x + 1 — and should take every copy of both.",
        "Count values; for each x where x + 1 also occurs, try count[x] + count[x + 1].",
    ],
    opt=("O(n)", "O(n)", "One counting pass and one pass over the distinct values."),
    editorial=(
        "## The one thing this teaches\n**\"Subsequence\" can mean \"order does not matter\".** "
        "Because you may skip anything, the only decision is which values to keep — and a "
        "harmonious set is two adjacent values, all copies of each.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> cnt = new HashMap<>();\nfor (int x : a) cnt.merge(x, 1, Integer::sum);\n"
        "int best = 0;\nfor (int x : cnt.keySet())\n"
        "    if (cnt.containsKey(x + 1)) best = Math.max(best, cnt.get(x) + cnt.get(x + 1));\n```\n\n"
        "## Exactly 1\nAn array of equal values has max − min = 0, which is not harmonious: "
        "`1 1 1 1` gives 0. Checking that `x + 1` is present is what enforces it.\n\n"
        "`x + 1` at `x = 2³¹ − 1` overflows an int; the constraint stops short, but a `long` key "
        "removes the question."
    ),
    py='''
def solve(a):
    cnt = Counter(a)
    return max((cnt[x] + cnt[x + 1] for x in cnt if x + 1 in cnt), default=0)
''',
    java='''
    static int solve(int[] a) {
        Map<Long, Integer> cnt = new HashMap<>();
        for (int x : a) cnt.merge((long) x, 1, Integer::sum);
        int best = 0;
        for (Map.Entry<Long, Integer> e : cnt.entrySet()) {
            Integer up = cnt.get(e.getKey() + 1);
            if (up != null) best = Math.max(best, e.getValue() + up);
        }
        return best;
    }
''',
    examples=[("Example 1", "8\n1 3 2 2 5 2 3 7\n"), ("Example 2", "4\n1 2 3 4\n")],
    hidden=[
        ("All equal", "4\n1 1 1 1\n"),
        ("Single element", "1\n5\n"),
        ("Negatives", "6\n-1 0 -1 0 -1 1\n"),
    ],
    expl=[
        "`3 2 2 2 3`: three 2s and two 3s.",
        "Any two adjacent values: length 2.",
    ],
    prereqs=[
        ("hashing", "A count per value, then a lookup of value + 1."),
        ("array_patterns", "A subsequence that ignores order reduces to choosing values."),
    ],
)

_p(
    "duplicate-subtrees-count", "Find Duplicate Subtrees (Count)", "Medium",
    topics=["Trees", "Hashing"], subtopics=["Tree DFS", "Canonical Form"], companies=["Google", "Amazon"],
    shape="tree", ret="int", todo="serialise each subtree post-order; count serialisations seen exactly twice",
    description=(
        "Two subtrees are **duplicates** if they have the same structure and the same values. "
        "Count how many **distinct** subtrees occur more than once.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe number of distinct duplicated subtrees."
    ),
    constraints="1 ≤ nodes ≤ 5000\n-200 ≤ value ≤ 200",
    hints=[
        "Comparing every pair of subtrees is far too slow.",
        "Give each subtree a canonical string: its value plus its children's strings, with a marker for null.",
        "Count strings in a map; each time a count reaches exactly 2, one more distinct duplicate exists.",
    ],
    opt=("O(n²)", "O(n²)", "String serialisations can total O(n²); assigning integer ids to subtrees makes it O(n)."),
    editorial=(
        "## The one thing this teaches\n**Canonical forms turn structure into keys.** Two subtrees "
        "are equal exactly when their serialisations are equal, so a hash map of serialisations "
        "finds every repeat — the same move as sorting letters to group anagrams.\n\n"
        "## Approach\n```java\nMap<String, Integer> seen = new HashMap<>();\nint dups = 0;\n"
        "String ser(TreeNode t) {\n    if (t == null) return \"#\";\n"
        "    String key = t.val + \",\" + ser(t.left) + \",\" + ser(t.right);\n"
        "    if (seen.merge(key, 1, Integer::sum) == 2) dups++;      // count each shape once\n"
        "    return key;\n}\n```\n\n"
        "## The null markers matter\nWithout `#`, a node with only a left child and one with only "
        "a right child serialise identically. The markers make the string describe the shape.\n\n"
        "## Going linear\nReplace each serialisation with a small integer id — `(val, leftId, "
        "rightId)` mapped to an id — so keys have constant length."
    ),
    py='''
def solve(root):
    import sys
    sys.setrecursionlimit(20000)
    seen = defaultdict(int)
    dups = 0

    def ser(t):
        nonlocal dups
        if not t:
            return "#"
        key = f"{t.val},{ser(t.left)},{ser(t.right)}"
        seen[key] += 1
        if seen[key] == 2:
            dups += 1
        return key

    ser(root)
    return dups
''',
    java='''
    static Map<List<Integer>, Integer> ids = new HashMap<>();
    static Map<Integer, Integer> uses = new HashMap<>();
    static int dups = 0;

    static int id(TreeNode t) {
        if (t == null) return 0;
        List<Integer> key = Arrays.asList(t.val, id(t.left), id(t.right));
        Integer got = ids.get(key);
        if (got == null) { got = ids.size() + 1; ids.put(key, got); }
        if (uses.merge(got, 1, Integer::sum) == 2) dups++;
        return got;
    }

    static int solve(TreeNode root) {
        id(root);
        return dups;
    }
''',
    examples=[("Example 1", "1 2 3 4 null 2 4 null null 4\n"), ("Example 2", "2 1 1\n")],
    hidden=[
        ("Single node", "1\n"),
        ("Values and shape both matter", "2 2 2 3 null 3 null\n"),
        ("Full tree of ones", "1 1 1 1 1 1 1\n"),
        ("Mirror shapes differ", "0 1 1 2 null null 2\n"),
    ],
    expl=[
        "The leaf `4` and the subtree `2 → 4` each occur twice.",
        "The leaf `1` occurs twice.",
    ],
    prereqs=[
        ("canonical", "Serialising each subtree so equal subtrees produce equal keys."),
        ("hashing", "Counting serialisations and noticing the second occurrence."),
    ],
)

_p(
    "excel-column-number", "Excel Sheet Column Number", "Easy",
    topics=["Math", "Strings"], subtopics=["Digits"], companies=["Microsoft", "Bloomberg"],
    shape="str", ret="long", todo="read left to right: value = value × 26 + (letter − 'A' + 1)",
    description=(
        "Spreadsheet columns are named `A`…`Z`, then `AA`, `AB`, …, `AZ`, `BA`, …. Convert a column "
        "name to its number (`A` = 1).\n\n"
        "### Input\nOne line: the column name.\n\n### Output\nThe column number."
    ),
    constraints="1 ≤ length ≤ 7\nThe name uses uppercase letters and its number is at most 2^31 − 1.",
    hints=[
        "It is like reading a base-26 number, one letter at a time.",
        "A is worth 1 and Z is worth 26 — there is no zero digit.",
        "value = value × 26 + (c − 'A' + 1), left to right.",
    ],
    opt=("O(L)", "O(1)", "One pass over the letters."),
    editorial=(
        "## The one thing this teaches\n**Positional notation, with digits 1..26 instead of "
        "0..25.** Reading any base left to right is `value = value × base + digit`. The only twist "
        "is that there is no zero: `Z` is 26, and `AA` comes right after it as 26 + 1 = 27.\n\n"
        "## Approach\n```java\nlong value = 0;\nfor (char c : name.toCharArray()) value = value * 26 + (c - 'A' + 1);\n```\n\n"
        "## The reverse is the harder direction\nNumber to name must handle the missing zero: "
        "subtract 1 before each `% 26`, or 26 would become \"A0\". Knowing why is the interview "
        "follow-up."
    ),
    py='''
def solve(s):
    value = 0
    for ch in s:
        value = value * 26 + (ord(ch) - 64)
    return value
''',
    java='''
    static long solve(String s) {
        long value = 0;
        for (int i = 0; i < s.length(); i++) value = value * 26 + (s.charAt(i) - 'A' + 1);
        return value;
    }
''',
    examples=[("Example 1", "AB\n"), ("Example 2", "ZY\n")],
    hidden=[
        ("First column", "A\n"),
        ("Last single letter", "Z\n"),
        ("Three letters", "AAA\n"),
        ("Largest int", "FXSHRXW\n"),
    ],
    expl=[
        "1 × 26 + 2 = 28.",
        "26 × 26 + 25 = 701.",
    ],
    prereqs=[
        ("math_digits", "Reading a positional number left to right with value × base + digit."),
        ("string_basics", "Converting a letter to its position with c − 'A' + 1."),
    ],
)

_p(
    "add-binary", "Add Binary", "Easy",
    topics=["Bit Manipulation", "Strings"], subtopics=["Bit Manipulation"], companies=["Meta", "Microsoft"],
    shape="str2", ret="String", todo="walk both strings from the right with a carry; append (sum % 2), then reverse",
    description=(
        "Add two binary numbers given as strings and print their sum in binary.\n\n"
        "### Input\n- Line 1: `a`.\n- Line 2: `b`.\n\n### Output\nThe binary sum, without leading zeros."
    ),
    constraints="1 ≤ |a|, |b| ≤ 10^4\nBoth are binary strings without leading zeros (except \"0\").",
    hints=[
        "The strings can be 10 000 bits — no primitive type holds them.",
        "Add from the rightmost bits, keeping a carry, exactly as with decimal digits.",
        "Continue while either string has bits left or the carry is 1. Build the result backwards, then reverse.",
    ],
    opt=("O(max(|a|, |b|))", "O(max(|a|, |b|))", "One pass over the longer string."),
    editorial=(
        "## The one thing this teaches\n**Schoolbook addition in any base.** At each position, "
        "`sum = bitA + bitB + carry`; write `sum % 2`, carry `sum / 2`. The same loop in base 10 is "
        "Add Strings, and on linked lists it is Add Two Numbers.\n\n"
        "## Approach\n```java\nStringBuilder out = new StringBuilder();\nint i = a.length() - 1, j = b.length() - 1, carry = 0;\n"
        "while (i >= 0 || j >= 0 || carry > 0) {\n    int sum = carry;\n"
        "    if (i >= 0) sum += a.charAt(i--) - '0';\n    if (j >= 0) sum += b.charAt(j--) - '0';\n"
        "    out.append(sum % 2);\n    carry = sum / 2;\n}\nreturn out.reverse().toString();\n```\n\n"
        "## The final carry\nThe `|| carry > 0` in the condition produces the extra leading 1 of "
        "`1 + 1 = 10`. Forgetting it is the classic bug."
    ),
    py='''
def solve(s, t):
    return bin(int(s, 2) + int(t, 2))[2:]
''',
    java='''
    static String solve(String a, String b) {
        StringBuilder out = new StringBuilder();
        int i = a.length() - 1, j = b.length() - 1, carry = 0;
        while (i >= 0 || j >= 0 || carry > 0) {
            int sum = carry;
            if (i >= 0) sum += a.charAt(i--) - '0';
            if (j >= 0) sum += b.charAt(j--) - '0';
            out.append(sum % 2);
            carry = sum / 2;
        }
        return out.reverse().toString();
    }
''',
    examples=[("Example 1", "11\n1\n"), ("Example 2", "1010\n1011\n")],
    hidden=[
        ("Zeros", "0\n0\n"),
        ("Carry ripples", "1111\n1111\n"),
        ("Longer than a long", "1" * 70 + "\n1\n"),
        ("Different lengths", "100000\n1\n"),
    ],
    expl=[
        "3 + 1 = 4.",
        "10 + 11 = 21.",
    ],
    prereqs=[
        ("bit_manip", "Binary digits added with a carry of sum / 2."),
        ("math_digits", "Schoolbook addition from the least significant digit."),
    ],
)

_p(
    "min-swaps-group-ones", "Minimum Swaps to Group All 1s (Circular)", "Medium",
    topics=["Arrays", "Sliding Window"], subtopics=["Sliding Window", "Fixed Window"], companies=["Amazon", "Microsoft"],
    shape="arr", ret="int", todo="window size = total ones; slide it around the circle; answer = ones − max ones in a window",
    description=(
        "A **circular** array holds `0`s and `1`s. A swap exchanges the values at any two positions. "
        "What is the fewest swaps that make all the `1`s contiguous (possibly wrapping around the "
        "end)?\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values.\n\n### Output\nThe minimum number of swaps."
    ),
    constraints="1 ≤ n ≤ 10^5\na[i] ∈ {0, 1}",
    hints=[
        "If there are k ones, they must end up filling some window of length k.",
        "The swaps needed for a window = the zeros inside it = k − (ones inside it).",
        "Slide a window of length k around the circle (index mod n) and take the window with the most ones.",
    ],
    opt=("O(n)", "O(1)", "One fixed-size window pass over the circle."),
    editorial=(
        "## The one thing this teaches\n**Fix the target shape, then measure its cost.** The ones "
        "will occupy *some* window of length k. For a given window the cost is exactly its zero "
        "count — each zero inside is swapped with a one outside. So minimise zeros, i.e. maximise "
        "ones, over all windows of length k.\n\n"
        "## Approach\n```java\nint k = count of ones;\nif (k == 0) return 0;\nint inWin = 0;\n"
        "for (int i = 0; i < k; i++) inWin += a[i];\nint best = inWin;\n"
        "for (int i = k; i < n + k; i++) {                 // wrap with % n\n"
        "    inWin += a[i % n] - a[(i - k) % n];\n    best = Math.max(best, inWin);\n}\nreturn k - best;\n```\n\n"
        "## The circle\nIndexing `i % n` slides the window across the seam without copying the "
        "array twice. A linear version of the problem is the same loop stopped at `n`."
    ),
    py='''
def solve(a):
    n = len(a)
    k = sum(a)
    if k == 0:
        return 0
    doubled = a + a
    best = max(sum(doubled[i:i + k]) for i in range(n))
    return k - best
''',
    java='''
    static int solve(int[] a) {
        int n = a.length, k = 0;
        for (int x : a) k += x;
        if (k == 0) return 0;
        int inWin = 0;
        for (int i = 0; i < k; i++) inWin += a[i];
        int best = inWin;
        for (int i = k; i < n + k; i++) {
            inWin += a[i % n] - a[(i - k) % n];
            best = Math.max(best, inWin);
        }
        return k - best;
    }
''',
    examples=[("Example 1", "7\n0 1 0 1 1 0 0\n"), ("Example 2", "9\n0 1 1 1 0 0 1 1 0\n")],
    hidden=[
        ("Already grouped across the seam", "5\n1 1 0 0 1\n"),
        ("No ones", "1\n0\n"),
        ("All ones", "4\n1 1 1 1\n"),
        ("Alternating", "6\n1 0 1 0 1 0\n"),
    ],
    expl=[
        "Swap the first 1 into position 2: `0 0 1 1 1 0 0`.",
        "Two swaps group the five 1s, for example wrapping from the end.",
    ],
    prereqs=[
        ("sliding_window", "A fixed window of length equal to the number of ones, slid around the circle."),
        ("modulo", "Index mod n lets the window wrap past the end."),
    ],
)

_p(
    "min-start-value", "Minimum Start Value for a Positive Running Sum", "Easy",
    topics=["Arrays", "Prefix Sum"], subtopics=["Prefix Sum"], companies=["Swiggy"],
    shape="arr", ret="long", todo="find the minimum prefix sum m; the start must be 1 − m, and at least 1",
    description=(
        "Choose a positive starting value, then add the array's elements one by one. What is the "
        "**smallest** starting value for which the running total is **at least 1** after every "
        "step?\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n### Output\nThe minimum start value."
    ),
    constraints="1 ≤ n ≤ 100\n-100 ≤ a[i] ≤ 100",
    hints=[
        "The running total after step i is start + prefix[i].",
        "It must stay ≥ 1 everywhere, so start ≥ 1 − prefix[i] for every i.",
        "The tightest constraint comes from the smallest prefix sum. The start is also at least 1.",
    ],
    opt=("O(n)", "O(1)", "One pass tracking the lowest prefix sum."),
    editorial=(
        "## The one thing this teaches\n**A constraint on every prefix is a constraint on the worst "
        "prefix.** \"Never drop below 1\" is n inequalities, but they all have the form "
        "`start ≥ 1 − prefix`, and only the smallest prefix matters.\n\n"
        "## Approach\n```java\nlong run = 0, lowest = 0;\nfor (int x : a) { run += x; lowest = Math.min(lowest, run); }\n"
        "return 1 - lowest;          // lowest ≤ 0, so this is ≥ 1\n```\n\n"
        "Starting `lowest` at 0 (the empty prefix) handles the \"at least 1\" requirement for "
        "arrays that never go negative.\n\n"
        "## Where it recurs\nThe same minimum-prefix reasoning finds Gas Station's starting point "
        "and the best time to buy a stock."
    ),
    py='''
def solve(a):
    start = 1
    while True:
        run = start
        ok = True
        for x in a:
            run += x
            if run < 1:
                ok = False
                break
        if ok:
            return start
        start += 1
''',
    java='''
    static long solve(int[] a) {
        long run = 0, lowest = 0;
        for (int x : a) { run += x; lowest = Math.min(lowest, run); }
        return 1 - lowest;
    }
''',
    examples=[("Example 1", "5\n-3 2 -3 4 2\n"), ("Example 2", "2\n1 2\n")],
    hidden=[
        ("Steady decline", "3\n1 -2 -3\n"),
        ("One big drop", "1\n-100\n"),
        ("All zeros", "4\n0 0 0 0\n"),
    ],
    expl=[
        "The lowest prefix sum is −4, so the start must be 5.",
        "The total never drops, so 1 works.",
    ],
    prereqs=[
        ("prefix_sum", "The running total is the start plus a prefix sum."),
        ("prefix_max", "Tracking the minimum prefix — the same running extreme, pointed down."),
    ],
)

_p(
    "valid-palindrome-ii", "Valid Palindrome II (Delete at Most One)", "Easy",
    topics=["Strings", "Two Pointers"], subtopics=["Two Pointers"], companies=["Meta", "Microsoft"],
    shape="str", ret="String", todo="two pointers; at the first mismatch, check whether skipping either side leaves a palindrome",
    description=(
        "Can `s` become a palindrome after deleting **at most one** character?\n\n"
        "### Input\nOne line: `s`.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |s| ≤ 10^5\ns consists of lowercase English letters.",
    hints=[
        "Trying every deletion and checking is O(n²).",
        "Walk inward from both ends. While the characters match, no deletion is needed.",
        "At the first mismatch the deletion must be one of those two characters: check s[l+1..r] and s[l..r−1].",
    ],
    opt=("O(n)", "O(1)", "One inward walk, then at most two more linear checks."),
    editorial=(
        "## The one thing this teaches\n**Spend a choice only when forced.** Matching outer "
        "characters never need deleting. The first mismatch is the only place a deletion can help, "
        "and there it can only be one of the two mismatched characters — two cases, each an "
        "ordinary palindrome check.\n\n"
        "## Approach\n```java\nint l = 0, r = n - 1;\nwhile (l < r) {\n"
        "    if (s.charAt(l) != s.charAt(r))\n"
        "        return isPal(s, l + 1, r) || isPal(s, l, r - 1) ? \"YES\" : \"NO\";\n"
        "    l++; r--;\n}\nreturn \"YES\";\n```\n\n"
        "## Why both sides must be tried\n`deeee`: the mismatch is `d` vs `e`, and only deleting "
        "the left `d` works. `eeeed` needs the right one. A solution that always deletes from the "
        "left passes the first and fails the second."
    ),
    py='''
def solve(s):
    if s == s[::-1]:
        return "YES"
    for i in range(len(s)):
        t = s[:i] + s[i + 1:]
        if t == t[::-1]:
            return "YES"
    return "NO"
''',
    java='''
    static boolean isPal(String s, int l, int r) {
        while (l < r) if (s.charAt(l++) != s.charAt(r--)) return false;
        return true;
    }

    static String solve(String s) {
        int l = 0, r = s.length() - 1;
        while (l < r) {
            if (s.charAt(l) != s.charAt(r)) return isPal(s, l + 1, r) || isPal(s, l, r - 1) ? "YES" : "NO";
            l++; r--;
        }
        return "YES";
    }
''',
    examples=[("Example 1", "aba\n"), ("Example 2", "abca\n")],
    hidden=[
        ("Two deletions needed", "abc\n"),
        ("Single letter", "a\n"),
        ("Delete on the left", "deeee\n"),
        ("Delete on the right", "eeeed\n"),
        ("Long miss", "eeccccbebaeeabebccceea\n"),
    ],
    expl=[
        "Already a palindrome.",
        "Delete `c` (or `b`).",
    ],
    prereqs=[
        ("two_pointers", "Converging pointers, branching once at the first mismatch."),
        ("string_basics", "A palindrome check over a sub-range, without copying."),
    ],
)
