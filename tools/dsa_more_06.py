# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 6 — graph traversal and topological order.
#
#   island-perimeter              count edges, not cells: 4 per cell minus 2 per shared side
#   max-area-of-island            flood fill that returns a size
#   surrounded-regions            flood from the border and keep what it reaches
#   pacific-atlantic              search backwards, uphill, from each ocean; intersect
#   open-the-lock                 BFS over states that are not stored anywhere
#   shortest-bridge               find one island, then multi-source BFS to the other
#   course-order-smallest         Kahn's algorithm with a min-heap
#   parallel-courses              Kahn's algorithm, counted in layers
#   eventual-safe-states          Kahn's algorithm on the reversed graph
#   longest-increasing-path-grid  the grid is a DAG; topological layers give the longest path
# ===========================================================================

_p(
    "island-perimeter", "Island Perimeter", "Easy",
    topics=["Graphs", "Matrix"], subtopics=["Grid", "Counting"], companies=["Meta", "Google"],
    shape="grid", ret="int", todo="add 4 for every land cell, subtract 2 for every pair of adjacent land cells",
    description=(
        "A grid of `1` (land) and `0` (water) contains **exactly one island** (connected "
        "horizontally or vertically). Lakes inside it do not connect to the outside. Find the "
        "island's perimeter.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `0`s and `1`s.\n\n"
        "### Output\nThe perimeter."
    ),
    constraints="1 ≤ r, c ≤ 100\nThere is exactly one island.",
    hints=[
        "No search is needed — every land cell contributes its own sides.",
        "A land cell has 4 sides. A side shared with another land cell is not on the perimeter.",
        "Count land cells and adjacent land pairs (look only right and down, so each pair is counted once): 4·cells − 2·pairs.",
    ],
    opt=("O(r·c)", "O(1)", "One pass over the grid, checking two neighbours per cell."),
    editorial=(
        "## The one thing this teaches\n**Count the thing asked for, not the thing it looks "
        "like.** It sounds like a graph problem, and a BFS that counts water-or-edge neighbours "
        "works. But perimeter is a property of *sides*, and sides can be counted locally.\n\n"
        "## Approach\n```java\nint cells = 0, shared = 0;\nfor (int i = 0; i < r; i++)\n"
        "    for (int j = 0; j < c; j++) {\n        if (g[i][j] != '1') continue;\n        cells++;\n"
        "        if (i + 1 < r && g[i + 1][j] == '1') shared++;   // down\n"
        "        if (j + 1 < c && g[i][j + 1] == '1') shared++;   // right\n    }\nreturn 4 * cells - 2 * shared;\n```\n\n"
        "Each shared side removes one side from *each* of its two cells, hence the 2. Looking "
        "only down and right counts every adjacent pair exactly once.\n\n"
        "## Lakes\nA lake's shoreline is inside the island, and this formula counts it as "
        "perimeter — which is what \"perimeter\" means for a shape with a hole. The statement "
        "says so to remove the doubt."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    cells = shared = 0
    for i in range(r):
        for j in range(c):
            if g[i][j] != "1":
                continue
            cells += 1
            if i + 1 < r and g[i + 1][j] == "1":
                shared += 1
            if j + 1 < c and g[i][j + 1] == "1":
                shared += 1
    return 4 * cells - 2 * shared
''',
    java='''
    static int solve(char[][] g) {
        int r = g.length, c = g[0].length, cells = 0, shared = 0;
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++) {
                if (g[i][j] != '1') continue;
                cells++;
                if (i + 1 < r && g[i + 1][j] == '1') shared++;
                if (j + 1 < c && g[i][j + 1] == '1') shared++;
            }
        return 4 * cells - 2 * shared;
    }
''',
    examples=[("Example 1", "4 4\n0100\n1110\n0100\n1100\n"), ("Example 2", "1 1\n1\n")],
    hidden=[
        ("Single cell in a row", "1 2\n10\n"),
        ("Solid square", "2 2\n11\n11\n"),
        ("Ring with a lake", "3 3\n111\n101\n111\n"),
    ],
    expl=[
        "7 land cells give 28 sides; 6 adjacent pairs remove 12: perimeter 16.",
        "One cell, four sides.",
    ],
    prereqs=[
        ("grid", "Checking a cell's down and right neighbours within the grid bounds."),
        ("big_o", "A local count replaces a traversal: one pass, no visited set."),
    ],
)

_p(
    "max-area-of-island", "Max Area of Island", "Medium",
    topics=["Graphs", "Matrix"], subtopics=["Flood Fill", "Grid"], companies=["Amazon", "Meta"],
    shape="grid", ret="int", todo="flood fill each unvisited land cell, counting cells; keep the largest count",
    description=(
        "In a grid of `1` (land) and `0` (water), an island is a group of land cells connected "
        "horizontally or vertically. Find the area of the **largest** island, or 0 if there is "
        "no land.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `0`s and `1`s.\n\n"
        "### Output\nThe largest area."
    ),
    constraints="1 ≤ r, c ≤ 50",
    hints=[
        "Number of Islands counts components. This asks for the size of each one.",
        "Flood fill from every unvisited land cell, counting the cells you mark.",
        "Mark a cell visited when you push it. An explicit stack avoids deep recursion on large islands.",
    ],
    opt=("O(r·c)", "O(r·c)", "Every cell is pushed at most once; the stack can hold the whole grid."),
    editorial=(
        "## The one thing this teaches\n**A traversal can return a value.** The flood fill from "
        "Number of Islands visits a component; make it count what it visits and you have "
        "component sizes. Most component questions — largest, smallest, how many of size k — "
        "are this with a different aggregate.\n\n"
        "## Approach\n```java\nint best = 0;\nfor (int i = 0; i < r; i++)\n    for (int j = 0; j < c; j++) {\n"
        "        if (g[i][j] != '1') continue;\n        int area = 0;\n"
        "        Deque<int[]> st = new ArrayDeque<>();\n        st.push(new int[]{i, j});\n"
        "        g[i][j] = '0';                       // mark on push\n"
        "        while (!st.isEmpty()) {\n            int[] cur = st.pop();\n            area++;\n"
        "            for (each neighbour that is '1') { set it to '0'; push it; }\n        }\n"
        "        best = Math.max(best, area);\n    }\n```\n\n"
        "## Mark on push, not on pop\nMarking when popping lets the same cell be pushed by "
        "several neighbours before it is processed, and it is then *counted* several times — "
        "the area comes out too large, not just slow."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    best = 0
    for i in range(r):
        for j in range(c):
            if g[i][j] != "1":
                continue
            g[i][j] = "0"
            st = [(i, j)]
            area = 0
            while st:
                x, y = st.pop()
                area += 1
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < r and 0 <= ny < c and g[nx][ny] == "1":
                        g[nx][ny] = "0"
                        st.append((nx, ny))
            best = max(best, area)
    return best
''',
    java='''
    static int solve(char[][] g) {
        int r = g.length, c = g[0].length, best = 0;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++) {
                if (g[i][j] != '1') continue;
                g[i][j] = '0';
                Deque<int[]> st = new ArrayDeque<>();
                st.push(new int[]{i, j});
                int area = 0;
                while (!st.isEmpty()) {
                    int[] cur = st.pop();
                    area++;
                    for (int[] d : dirs) {
                        int x = cur[0] + d[0], y = cur[1] + d[1];
                        if (x >= 0 && y >= 0 && x < r && y < c && g[x][y] == '1') { g[x][y] = '0'; st.push(new int[]{x, y}); }
                    }
                }
                best = Math.max(best, area);
            }
        return best;
    }
''',
    examples=[("Example 1", "4 5\n11000\n11001\n00011\n00011\n"), ("Example 2", "2 3\n000\n000\n")],
    hidden=[
        ("Single cell", "1 1\n1\n"),
        ("Diagonals do not connect", "3 3\n101\n010\n101\n"),
        ("Winding island", "3 4\n1111\n0001\n1111\n"),
    ],
    expl=[
        "The top-left island has 4 cells; the one on the right has 5.",
        "No land.",
    ],
    prereqs=[
        ("flood_fill", "A traversal from each unvisited land cell that counts the cells it marks."),
        ("visited_set", "Marking cells when they are pushed, so none is counted twice."),
    ],
)

_p(
    "surrounded-regions", "Surrounded Regions", "Medium",
    topics=["Graphs", "Matrix"], subtopics=["Flood Fill", "BFS"], companies=["Google", "Uber"],
    shape="grid", ret="String", todo="flood from every border O marking it safe; then every other O becomes X",
    description=(
        "In a grid of `X` and `O`, a region of `O`s (connected horizontally or vertically) is "
        "**captured** if it does not touch the border: all its cells become `X`. Regions touching "
        "the border survive.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `X`s and `O`s.\n\n"
        "### Output\nThe grid after capturing, one row per line."
    ),
    constraints="1 ≤ r, c ≤ 200",
    hints=[
        "Deciding for each region whether it touches the border means exploring it anyway.",
        "Turn it around: the surviving O's are exactly those reachable from a border O.",
        "Flood from every border O, marking cells with a temporary symbol. Then unmarked O → X, marked → O.",
    ],
    opt=("O(r·c)", "O(r·c)", "Each cell is flooded at most once."),
    editorial=(
        "## The one thing this teaches\n**Search from the side that is easy to identify.** "
        "\"Surrounded\" is hard to test region by region; \"connected to the border\" is a single "
        "flood seeded from border cells. Complementing the question turns many searches with "
        "an early-exit condition into one search with none.\n\n"
        "## Approach\n```java\n// 1. mark everything reachable from a border 'O' as 'S' (safe)\n"
        "for (each border cell with 'O') flood(i, j);          // 'O' -> 'S'\n"
        "// 2. rewrite\nfor (each cell) g[i][j] = g[i][j] == 'S' ? 'O' : 'X';\n```\n\n"
        "## Why a temporary symbol\nChanging border-connected cells to `S` doubles as the visited "
        "marker for the flood *and* remembers the answer for the rewrite pass. Using a separate "
        "boolean grid works too; flipping captured cells during the flood does not, because a "
        "region is only known to be captured after all of it has been explored."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    st = [(i, j) for i in range(r) for j in range(c)
          if (i in (0, r - 1) or j in (0, c - 1)) and g[i][j] == "O"]
    for i, j in st:
        g[i][j] = "S"
    while st:
        x, y = st.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < r and 0 <= ny < c and g[nx][ny] == "O":
                g[nx][ny] = "S"
                st.append((nx, ny))
    return "\\n".join("".join("O" if ch == "S" else "X" for ch in row) for row in g)
''',
    java='''
    static String solve(char[][] g) {
        int r = g.length, c = g[0].length;
        Deque<int[]> st = new ArrayDeque<>();
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                if ((i == 0 || j == 0 || i == r - 1 || j == c - 1) && g[i][j] == 'O') { g[i][j] = 'S'; st.push(new int[]{i, j}); }
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!st.isEmpty()) {
            int[] cur = st.pop();
            for (int[] d : dirs) {
                int x = cur[0] + d[0], y = cur[1] + d[1];
                if (x >= 0 && y >= 0 && x < r && y < c && g[x][y] == 'O') { g[x][y] = 'S'; st.push(new int[]{x, y}); }
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < r; i++) {
            if (i > 0) sb.append('\\n');
            for (int j = 0; j < c; j++) sb.append(g[i][j] == 'S' ? 'O' : 'X');
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "4 4\nXXXX\nXOOX\nXXOX\nXOXX\n"), ("Example 2", "1 1\nX\n")],
    hidden=[
        ("Everything touches the border", "3 3\nOOO\nOXO\nOOO\n"),
        ("Single captured cell", "3 3\nXXX\nXOX\nXXX\n"),
        ("Region reaches the border through a corridor", "4 5\nXXXXX\nXOXOX\nXOOOX\nXXXOX\n"),
    ],
    expl=[
        "The three inner O's are enclosed; the bottom O is on the border and survives.",
        "No O's at all.",
    ],
    prereqs=[
        ("flood_fill", "One flood seeded from every border O finds all the regions that survive."),
        ("grid", "Border cells identified by their row or column index."),
    ],
)

_p(
    "pacific-atlantic", "Pacific Atlantic Water Flow", "Medium",
    topics=["Graphs", "Matrix"], subtopics=["BFS", "Grid"], companies=["Google", "Amazon"],
    shape="matrix", ret="String", todo="BFS uphill from each ocean's edge cells; output cells reached by both",
    description=(
        "A grid of heights has the **Pacific** along its top and left edges and the **Atlantic** "
        "along its bottom and right edges. Water flows from a cell to a neighbour (up, down, left, "
        "right) whose height is **less than or equal**, and from an edge cell into the adjacent "
        "ocean. Which cells can reach both oceans?\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` heights.\n\n"
        "### Output\nOne line `row col` per qualifying cell, in row-major order."
    ),
    constraints="1 ≤ r, c ≤ 200\n0 ≤ height ≤ 10^5",
    hints=[
        "Running a search from every cell toward the oceans is O((r·c)²).",
        "Reverse the flow: from each ocean, which cells could have sent water here? Move to neighbours that are HIGHER or equal.",
        "One multi-source BFS per ocean, seeded with its edge cells. Answer: cells marked by both.",
    ],
    opt=("O(r·c)", "O(r·c)", "Two traversals, each visiting every cell at most once."),
    editorial=(
        "## The one thing this teaches\n**Reverse the edges, share the search.** \"Can this cell "
        "reach the ocean?\" asked for every cell is r·c searches. \"Which cells can reach the "
        "ocean?\" asked once from the ocean's side is a single multi-source search, walking the "
        "flow backwards — uphill.\n\n"
        "## Approach\n```java\nboolean[][] pac = bfs(pacificEdgeCells), atl = bfs(atlanticEdgeCells);\n"
        "for (each cell) if (pac[i][j] && atl[i][j]) output(i, j);\n\n"
        "// inside bfs, from (x, y) to neighbour (nx, ny):\n"
        "if (!seen[nx][ny] && h[nx][ny] >= h[x][y]) { seen[nx][ny] = true; q.add(...); }\n```\n\n"
        "## The direction of the comparison\nForward, water moves to `≤`. Backwards, the search "
        "moves to `≥`. Writing `≤` in the reversed search is the one-character bug that makes "
        "every answer wrong while still looking plausible.\n\n"
        "The corners top-right and bottom-left always qualify: each touches both oceans."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])

    def reach(starts):
        seen = [[False] * c for _ in range(r)]
        q = deque()
        for i, j in starts:
            if not seen[i][j]:
                seen[i][j] = True
                q.append((i, j))
        while q:
            x, y = q.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < r and 0 <= ny < c and not seen[nx][ny] and m[nx][ny] >= m[x][y]:
                    seen[nx][ny] = True
                    q.append((nx, ny))
        return seen

    pac = reach([(0, j) for j in range(c)] + [(i, 0) for i in range(r)])
    atl = reach([(r - 1, j) for j in range(c)] + [(i, c - 1) for i in range(r)])
    return "\\n".join(f"{i} {j}" for i in range(r) for j in range(c) if pac[i][j] and atl[i][j])
''',
    java='''
    static boolean[][] reach(int[][] m, List<int[]> starts) {
        int r = m.length, c = m[0].length;
        boolean[][] seen = new boolean[r][c];
        ArrayDeque<int[]> q = new ArrayDeque<>();
        for (int[] s : starts) if (!seen[s[0]][s[1]]) { seen[s[0]][s[1]] = true; q.add(s); }
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!q.isEmpty()) {
            int[] cur = q.poll();
            for (int[] d : dirs) {
                int x = cur[0] + d[0], y = cur[1] + d[1];
                if (x < 0 || y < 0 || x >= r || y >= c || seen[x][y] || m[x][y] < m[cur[0]][cur[1]]) continue;
                seen[x][y] = true;
                q.add(new int[]{x, y});
            }
        }
        return seen;
    }

    static String solve(int[][] m) {
        int r = m.length, c = m[0].length;
        List<int[]> p = new ArrayList<>(), a = new ArrayList<>();
        for (int j = 0; j < c; j++) { p.add(new int[]{0, j}); a.add(new int[]{r - 1, j}); }
        for (int i = 0; i < r; i++) { p.add(new int[]{i, 0}); a.add(new int[]{i, c - 1}); }
        boolean[][] pac = reach(m, p), atl = reach(m, a);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                if (pac[i][j] && atl[i][j]) { if (sb.length() > 0) sb.append('\\n'); sb.append(i).append(' ').append(j); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5 5\n1 2 2 3 5\n3 2 3 4 4\n2 4 5 3 1\n6 7 1 4 5\n5 1 1 2 4\n"),
        ("Example 2", "1 1\n1\n"),
    ],
    hidden=[
        ("Flat grid", "2 2\n1 1\n1 1\n"),
        ("Spiral", "3 3\n1 2 3\n8 9 4\n7 6 5\n"),
        ("A pit in the middle", "2 3\n3 3 3\n3 1 3\n"),
    ],
    expl=[
        "Seven cells drain both ways, including the central peak at (2, 2).",
        "A single cell touches all four edges.",
    ],
    prereqs=[
        ("bfs", "A multi-source BFS from each ocean's edge, moving against the flow."),
        ("grid", "Neighbour checks within bounds, with a height comparison deciding each move."),
    ],
)

_p(
    "open-the-lock", "Open the Lock", "Medium",
    topics=["Graphs", "Strings"], subtopics=["BFS"], companies=["Google", "Amazon"],
    shape="str_list", ret="int", todo="BFS from 0000 over the 8 one-wheel turns, skipping dead ends",
    description=(
        "A lock has four wheels, each showing a digit `0`–`9`, and starts at `0000`. One move "
        "turns one wheel one step up or down (`9` wraps to `0` and back). Some combinations are "
        "**dead ends**: the lock jams if it ever shows one. What is the fewest moves to reach the "
        "target?\n\n"
        "### Input\n- Line 1: the target.\n- Line 2: `d`, the number of dead ends.\n"
        "- Line 3: the `d` dead ends (empty if `d` is 0).\n\n"
        "### Output\nThe minimum number of moves, or `-1` if the target cannot be reached."
    ),
    constraints="0 ≤ d ≤ 500\nThe target and dead ends are 4-digit strings.",
    hints=[
        "Each combination is a node; each has 8 neighbours (4 wheels × up or down). The graph is never built.",
        "Fewest moves in an unweighted graph is BFS from 0000.",
        "Put the dead ends in the visited set before starting. If 0000 itself is a dead end, the answer is −1.",
    ],
    opt=("O(10⁴ · 8)", "O(10⁴)", "At most 10 000 states, each generating 8 neighbours."),
    editorial=(
        "## The one thing this teaches\n**An implicit graph.** Nothing in the input is an edge "
        "list — the nodes are all 10⁴ combinations and the edges are generated on demand by "
        "turning a wheel. BFS does not care whether edges are stored or computed.\n\n"
        "## Approach\n```java\nSet<String> seen = new HashSet<>(Arrays.asList(deadends));\n"
        "if (seen.contains(\"0000\")) return -1;\nDeque<String> q = new ArrayDeque<>(List.of(\"0000\"));\n"
        "seen.add(\"0000\");\nfor (int steps = 0; !q.isEmpty(); steps++) {\n"
        "    for (int k = q.size(); k > 0; k--) {\n        String cur = q.poll();\n"
        "        if (cur.equals(target)) return steps;\n"
        "        for (String next : turns(cur)) if (seen.add(next)) q.add(next);\n    }\n}\nreturn -1;\n```\n\n"
        "## Dead ends are visited nodes\nSeeding the visited set with the dead ends means the BFS "
        "never enters them, with no separate check. Wrapping a digit is `(d + 1) % 10` and "
        "`(d + 9) % 10` — the second avoids a negative remainder.\n\n"
        "## Faster, if asked\nBidirectional BFS from both `0000` and the target meets in the "
        "middle and explores far fewer states."
    ),
    py='''
def solve(s, words):
    target = s
    seen = set(words)
    if "0000" in seen:
        return -1
    seen.add("0000")
    q = deque([("0000", 0)])
    while q:
        cur, steps = q.popleft()
        if cur == target:
            return steps
        for i in range(4):
            d = int(cur[i])
            for nd in ((d + 1) % 10, (d + 9) % 10):
                nxt = cur[:i] + str(nd) + cur[i + 1:]
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, steps + 1))
    return -1
''',
    java='''
    static int solve(String target, String[] deadends) {
        Set<String> seen = new HashSet<>(Arrays.asList(deadends));
        if (seen.contains("0000")) return -1;
        seen.add("0000");
        ArrayDeque<String> q = new ArrayDeque<>();
        q.add("0000");
        for (int steps = 0; !q.isEmpty(); steps++) {
            for (int k = q.size(); k > 0; k--) {
                String cur = q.poll();
                if (cur.equals(target)) return steps;
                char[] ch = cur.toCharArray();
                for (int i = 0; i < 4; i++) {
                    char orig = ch[i];
                    int d = orig - '0';
                    for (int nd : new int[]{(d + 1) % 10, (d + 9) % 10}) {
                        ch[i] = (char) ('0' + nd);
                        String next = new String(ch);
                        if (seen.add(next)) q.add(next);
                    }
                    ch[i] = orig;
                }
            }
        }
        return -1;
    }
''',
    examples=[("Example 1", "0202\n5\n0201 0101 0102 1212 2002\n"), ("Example 2", "8888\n1\n8887\n")],
    hidden=[
        ("Target walled in", "8888\n8\n8887 8889 8878 8898 8788 8988 7888 9888\n"),
        ("Already open", "0000\n1\n8888\n"),
        ("Start is a dead end", "0009\n1\n0000\n"),
        ("No dead ends", "1111\n0\n\n"),
    ],
    expl=[
        "0000 → 1000 → 1100 → 1200 → 1201 → 1202 → 0202: six moves, avoiding every dead end.",
        "Each wheel turns down twice, 0 → 9 → 8: eight moves. The last wheel never shows 7, so the dead end 8887 is never hit.",
    ],
    prereqs=[
        ("bfs", "Breadth-first search counts the fewest moves in an unweighted state graph."),
        ("visited_set", "A set of seen combinations, pre-filled with the dead ends."),
    ],
)

_p(
    "shortest-bridge", "Shortest Bridge", "Medium",
    topics=["Graphs", "Matrix"], subtopics=["BFS", "Flood Fill"], companies=["Google", "Uber"],
    shape="grid", ret="int", todo="flood one island into a queue, then BFS outward over water until the other island",
    description=(
        "A grid of `1` (land) and `0` (water) contains **exactly two islands**. Find the fewest "
        "water cells you must turn into land to connect them.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `0`s and `1`s.\n\n"
        "### Output\nThe minimum number of cells to flip."
    ),
    constraints="2 ≤ r·c\n1 ≤ r, c ≤ 100\nThere are exactly two islands.",
    hints=[
        "The answer is the shortest water path between any cell of island A and any cell of island B.",
        "Find island A with a flood fill and put ALL its cells in a BFS queue at distance 0.",
        "Expand level by level over water; the first time you touch a land cell not in A, the current level is the answer.",
    ],
    opt=("O(r·c)", "O(r·c)", "One flood fill and one multi-source BFS, each visiting a cell at most once."),
    editorial=(
        "## The one thing this teaches\n**Two traversals, composed.** A DFS or flood fill "
        "*identifies* a set; a BFS *measures distance* from a set. Seeding the BFS with every "
        "cell of one island at once is what makes it \"distance from the island\" rather than "
        "\"distance from one cell\" — and it is the difference between O(r·c) and O((r·c)²).\n\n"
        "## Approach\n```java\n// 1. flood fill the first land cell found; mark its cells 2 and add them to q\n"
        "// 2. BFS by levels\nfor (int steps = 0; ; steps++) {\n"
        "    for (int k = q.size(); k > 0; k--) {\n        int[] cur = q.poll();\n"
        "        for (each neighbour (x, y)) {\n            if (g[x][y] == '1') return steps;   // reached island B\n"
        "            if (g[x][y] == '0') { g[x][y] = '2'; q.add(new int[]{x, y}); }\n        }\n    }\n}\n```\n\n"
        "## Counting flips, not steps\nFrom island A, touching island B directly (distance 0 "
        "levels of water) means 0 flips; each BFS level crossed over water adds one flipped "
        "cell. Returning `steps` when a neighbour is land from B counts exactly the water cells "
        "between them."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    si, sj = next((i, j) for i in range(r) for j in range(c) if g[i][j] == "1")
    g[si][sj] = "2"
    st = [(si, sj)]
    q = deque()
    while st:
        x, y = st.pop()
        q.append((x, y))
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < r and 0 <= ny < c and g[nx][ny] == "1":
                g[nx][ny] = "2"
                st.append((nx, ny))
    steps = 0
    while q:
        for _ in range(len(q)):
            x, y = q.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < r and 0 <= ny < c:
                    if g[nx][ny] == "1":
                        return steps
                    if g[nx][ny] == "0":
                        g[nx][ny] = "2"
                        q.append((nx, ny))
        steps += 1
    return -1
''',
    java='''
    static int solve(char[][] g) {
        int r = g.length, c = g[0].length;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        ArrayDeque<int[]> q = new ArrayDeque<>();
        outer:
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                if (g[i][j] == '1') {
                    ArrayDeque<int[]> st = new ArrayDeque<>();
                    g[i][j] = '2';
                    st.push(new int[]{i, j});
                    while (!st.isEmpty()) {
                        int[] cur = st.pop();
                        q.add(cur);
                        for (int[] d : dirs) {
                            int x = cur[0] + d[0], y = cur[1] + d[1];
                            if (x >= 0 && y >= 0 && x < r && y < c && g[x][y] == '1') { g[x][y] = '2'; st.push(new int[]{x, y}); }
                        }
                    }
                    break outer;
                }
        for (int steps = 0; !q.isEmpty(); steps++) {
            for (int k = q.size(); k > 0; k--) {
                int[] cur = q.poll();
                for (int[] d : dirs) {
                    int x = cur[0] + d[0], y = cur[1] + d[1];
                    if (x < 0 || y < 0 || x >= r || y >= c) continue;
                    if (g[x][y] == '1') return steps;
                    if (g[x][y] == '0') { g[x][y] = '2'; q.add(new int[]{x, y}); }
                }
            }
        }
        return -1;
    }
''',
    examples=[("Example 1", "2 2\n01\n10\n"), ("Example 2", "3 3\n010\n000\n001\n")],
    hidden=[
        ("Island inside a ring", "5 5\n11111\n10001\n10101\n10001\n11111\n"),
        ("One gap", "1 3\n101\n"),
        ("Far corners", "4 4\n1100\n1000\n0000\n0011\n"),
    ],
    expl=[
        "Flip either 0 to join the two single-cell islands.",
        "Flip (1, 1) and (1, 2), or another two-cell path.",
    ],
    prereqs=[
        ("flood_fill", "Identifying every cell of the first island."),
        ("bfs", "A multi-source BFS from that whole island, counting water levels to the second one."),
    ],
)

_p(
    "course-order-smallest", "Course Order (Lexicographically Smallest)", "Medium",
    topics=["Graphs"], subtopics=["Topological Sort", "Priority Queue"], companies=["Amazon", "Microsoft"],
    shape="graph", ret="String", todo="Kahn's algorithm with a min-heap of available courses; IMPOSSIBLE if not all are taken",
    description=(
        "Courses are numbered `0` to `n − 1`. Each pair `a b` means `a` must be taken **before** `b`. "
        "Print an order in which all courses can be taken; if several exist, print the "
        "**lexicographically smallest** (smallest first course, then smallest second, …).\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `a b`.\n\n"
        "### Output\nThe course order separated by spaces, or `IMPOSSIBLE` if the prerequisites form a cycle."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 5·10^4\n0 ≤ a, b < n (a pair may be repeated, and a may equal b)",
    hints=[
        "Kahn's algorithm takes any course whose prerequisites are all done. Which one you take is a free choice.",
        "To make the order smallest, always take the smallest available course: keep available courses in a min-heap.",
        "If fewer than n courses come out, the rest are stuck on a cycle.",
    ],
    opt=("O((n + m) log n)", "O(n + m)", "Each course passes through the heap once; each pair decrements one in-degree once."),
    editorial=(
        "## The one thing this teaches\n**The queue in Kahn's algorithm is a policy.** Any "
        "container of available nodes produces *a* topological order. A FIFO queue produces one; a "
        "min-heap produces the lexicographically smallest, because at every step it commits the "
        "smallest course that could legally come next.\n\n"
        "## Approach\n```java\nPriorityQueue<Integer> pq = new PriorityQueue<>();\n"
        "for (int i = 0; i < n; i++) if (indeg[i] == 0) pq.add(i);\nList<Integer> order = new ArrayList<>();\n"
        "while (!pq.isEmpty()) {\n    int u = pq.poll();\n    order.add(u);\n"
        "    for (int v : adj.get(u)) if (--indeg[v] == 0) pq.add(v);\n}\n"
        "return order.size() == n ? join(order) : \"IMPOSSIBLE\";\n```\n\n"
        "## Why greedy is right here\nChoosing the smallest available course first can never "
        "block a later course — taking a course only *removes* constraints. So the earliest "
        "position is always filled by the smallest possible value.\n\n"
        "## Repeated pairs and self-loops\nA repeated pair adds its in-degree twice and "
        "decrements it twice, so it is harmless. `a a` gives a course an in-degree that can never "
        "reach 0: a cycle of length one, correctly reported as impossible."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    h = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(h)
    order = []
    while h:
        u = heapq.heappop(h)
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(h, v)
    return " ".join(map(str, order)) if len(order) == n else "IMPOSSIBLE"
''',
    java='''
    static String solve(int n, int[][] edges) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); indeg[e[1]]++; }
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        for (int i = 0; i < n; i++) if (indeg[i] == 0) pq.add(i);
        StringBuilder sb = new StringBuilder();
        int taken = 0;
        while (!pq.isEmpty()) {
            int u = pq.poll();
            if (taken++ > 0) sb.append(' ');
            sb.append(u);
            for (int v : adj.get(u)) if (--indeg[v] == 0) pq.add(v);
        }
        return taken == n ? sb.toString() : "IMPOSSIBLE";
    }
''',
    examples=[("Example 1", "4 3\n0 1\n0 2\n1 3\n"), ("Example 2", "2 2\n0 1\n1 0\n")],
    hidden=[
        ("No prerequisites", "3 0\n"),
        ("Smallest is not the first root", "5 4\n4 0\n3 0\n2 1\n1 0\n"),
        ("Self-loop", "1 1\n0 0\n"),
        ("Repeated pair", "3 3\n2 0\n2 0\n0 1\n"),
    ],
    expl=[
        "0 first; then 1 and 2 are available and 1 is smaller; 3 unlocks after 1 but 2 is smaller.",
        "Each course waits for the other.",
    ],
    prereqs=[
        ("topo", "Kahn's algorithm: repeatedly take a course whose prerequisites are all done."),
        ("heap", "A min-heap of available courses makes every choice the smallest possible."),
    ],
)

_p(
    "parallel-courses", "Parallel Courses (Minimum Semesters)", "Medium",
    topics=["Graphs"], subtopics=["Topological Sort", "BFS"], companies=["Google", "Uber"],
    shape="graph", ret="int", todo="Kahn's algorithm level by level; count levels; -1 if a cycle blocks some course",
    description=(
        "Courses `0` to `n − 1` have prerequisites: a pair `a b` means `a` must be finished in an "
        "**earlier** semester than `b`. You may take any number of courses in a semester. What is "
        "the minimum number of semesters to take them all?\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `a b`.\n\n"
        "### Output\nThe minimum number of semesters, or `-1` if it is impossible."
    ),
    constraints="1 ≤ n ≤ 5000\n0 ≤ m ≤ 5000\n0 ≤ a, b < n, a ≠ b, no repeated pairs",
    hints=[
        "In the first semester, take every course with no prerequisites — there is no reason to wait.",
        "Each semester is one LAYER of Kahn's algorithm: everything whose in-degree reached 0 during the previous layer.",
        "Count the layers. If fewer than n courses were taken, there is a cycle.",
    ],
    opt=("O(n + m)", "O(n + m)", "Kahn's algorithm, processed one layer at a time."),
    editorial=(
        "## The one thing this teaches\n**BFS layers of a topological sort measure depth.** "
        "Taking every available course immediately is optimal, because delaying a course can only "
        "delay what depends on it. So semester k contains exactly the courses whose longest "
        "prerequisite chain has length k — and Kahn's algorithm, run layer by layer, finds them.\n\n"
        "## Approach\n```java\nDeque<Integer> q = new ArrayDeque<>();\n"
        "for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);\nint semesters = 0, taken = 0;\n"
        "while (!q.isEmpty()) {\n    semesters++;\n    for (int k = q.size(); k > 0; k--) {\n"
        "        int u = q.poll();\n        taken++;\n"
        "        for (int v : adj.get(u)) if (--indeg[v] == 0) q.add(v);\n    }\n}\n"
        "return taken == n ? semesters : -1;\n```\n\n"
        "## Same answer, other name\nThe number of semesters is the number of nodes on the "
        "longest path in the DAG. The layered BFS computes that without ever tracking paths."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    semesters = taken = 0
    while q:
        semesters += 1
        for _ in range(len(q)):
            u = q.popleft()
            taken += 1
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
    return semesters if taken == n else -1
''',
    java='''
    static int solve(int n, int[][] edges) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); indeg[e[1]]++; }
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);
        int semesters = 0, taken = 0;
        while (!q.isEmpty()) {
            semesters++;
            for (int k = q.size(); k > 0; k--) {
                int u = q.poll();
                taken++;
                for (int v : adj.get(u)) if (--indeg[v] == 0) q.add(v);
            }
        }
        return taken == n ? semesters : -1;
    }
''',
    examples=[("Example 1", "3 2\n0 2\n1 2\n"), ("Example 2", "3 3\n0 1\n1 2\n2 0\n")],
    hidden=[
        ("Single course", "1 0\n"),
        ("A chain", "4 3\n0 1\n1 2\n2 3\n"),
        ("Wide", "5 4\n0 4\n1 4\n2 4\n3 4\n"),
        ("Two components", "6 5\n0 1\n0 2\n1 3\n2 3\n4 5\n"),
    ],
    expl=[
        "Courses 0 and 1 together, then course 2.",
        "The three courses form a cycle.",
    ],
    prereqs=[
        ("topo", "Kahn's algorithm, where each layer of zero in-degree courses is one semester."),
        ("bfs", "Processing the queue level by level to count layers."),
    ],
)

_p(
    "eventual-safe-states", "Find Eventual Safe States", "Medium",
    topics=["Graphs"], subtopics=["Topological Sort", "Cycle Detection"], companies=["Google", "Amazon"],
    shape="graph", ret="String", todo="reverse the edges; peel off nodes whose out-degree reaches 0, starting from terminal nodes",
    description=(
        "In a directed graph, a node is **terminal** if it has no outgoing edges, and **safe** if "
        "every path starting from it ends at a terminal node (so no path can reach a cycle).\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v`, an edge `u → v`.\n\n"
        "### Output\nThe safe nodes in increasing order, separated by spaces, or `NONE`."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 4·10^4\nSelf-loops may appear; no repeated edges.",
    hints=[
        "Terminal nodes are safe. A node is safe exactly when ALL of its outgoing edges lead to safe nodes.",
        "That is Kahn's algorithm on the reversed graph, with out-degree in place of in-degree.",
        "Start from terminal nodes; when a node's remaining out-degree reaches 0, it is safe. Whatever never reaches 0 can reach a cycle.",
    ],
    opt=("O(n + m)", "O(n + m)", "Each edge is reversed once and decremented once."),
    editorial=(
        "## The one thing this teaches\n**Topological sort in the other direction.** Kahn's "
        "algorithm removes nodes with nothing coming *in*. Here safety propagates backwards from "
        "nodes with nothing going *out*: a node becomes safe once every node it points to is "
        "safe. Reverse the edges and it is the same algorithm.\n\n"
        "## Approach\n```java\n// rev[v] lists u for each edge u -> v; out[u] = out-degree\n"
        "Deque<Integer> q = new ArrayDeque<>();\n"
        "for (int u = 0; u < n; u++) if (out[u] == 0) q.add(u);\nboolean[] safe = new boolean[n];\n"
        "while (!q.isEmpty()) {\n    int v = q.poll();\n    safe[v] = true;\n"
        "    for (int u : rev.get(v)) if (--out[u] == 0) q.add(u);\n}\n```\n\n"
        "## Why nodes on or leading to a cycle are left over\nA node on a cycle always has an "
        "outgoing edge to another cycle node, which never becomes safe, so its out-degree never "
        "reaches 0 — and that failure propagates to everything that can reach it.\n\n"
        "The DFS alternative colours nodes white/grey/black and marks a node unsafe if its search "
        "meets a grey node; it answers the same question in the same time."
    ),
    py='''
def solve(n, edges):
    rev = [[] for _ in range(n)]
    out = [0] * n
    for u, v in edges:
        rev[v].append(u)
        out[u] += 1
    q = deque(u for u in range(n) if out[u] == 0)
    safe = [False] * n
    while q:
        v = q.popleft()
        safe[v] = True
        for u in rev[v]:
            out[u] -= 1
            if out[u] == 0:
                q.append(u)
    res = [str(i) for i in range(n) if safe[i]]
    return " ".join(res) if res else "NONE"
''',
    java='''
    static String solve(int n, int[][] edges) {
        List<List<Integer>> rev = new ArrayList<>();
        for (int i = 0; i < n; i++) rev.add(new ArrayList<>());
        int[] out = new int[n];
        for (int[] e : edges) { rev.get(e[1]).add(e[0]); out[e[0]]++; }
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int u = 0; u < n; u++) if (out[u] == 0) q.add(u);
        boolean[] safe = new boolean[n];
        while (!q.isEmpty()) {
            int v = q.poll();
            safe[v] = true;
            for (int u : rev.get(v)) if (--out[u] == 0) q.add(u);
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) if (safe[i]) { if (sb.length() > 0) sb.append(' '); sb.append(i); }
        return sb.length() == 0 ? "NONE" : sb.toString();
    }
''',
    examples=[
        ("Example 1", "7 7\n0 1\n0 2\n1 2\n1 3\n2 5\n3 0\n4 5\n"),
        ("Example 2", "5 10\n0 1\n0 2\n0 3\n0 4\n1 1\n1 2\n2 3\n2 4\n3 0\n3 4\n"),
    ],
    hidden=[
        ("Everything on a cycle", "3 3\n0 1\n1 2\n2 0\n"),
        ("No edges", "3 0\n"),
        ("Self-loop poisons its predecessor", "4 3\n0 1\n1 1\n2 3\n"),
    ],
    expl=[
        "0 → 1 → 3 → 0 is a cycle, so 0, 1 and 3 are unsafe; 2, 4, 5 and 6 are safe.",
        "Only node 4, which is terminal.",
    ],
    prereqs=[
        ("topo", "Kahn's algorithm on the reversed graph, peeling nodes whose out-degree reaches 0."),
        ("graph_cycle", "Nodes that can reach a cycle are exactly the ones never peeled."),
    ],
)

_p(
    "longest-increasing-path-grid", "Longest Increasing Path in a Matrix", "Hard",
    topics=["Graphs", "Matrix"], subtopics=["Topological Sort", "Grid"], companies=["Google", "Meta", "Amazon"],
    shape="matrix", ret="int", todo="edges go from smaller to larger neighbours; peel the DAG in layers from cells with no smaller neighbour",
    description=(
        "Find the length of the longest **strictly increasing** path in a grid, moving up, down, "
        "left or right.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` integers.\n\n"
        "### Output\nThe length of the longest increasing path (a single cell counts as 1)."
    ),
    constraints="1 ≤ r, c ≤ 200\n0 ≤ value ≤ 2^31 − 1",
    hints=[
        "A strictly increasing path can never revisit a cell, so there is no need for a visited set — the moves form a DAG.",
        "Memoised DFS works: longest(x) = 1 + max(longest(y)) over larger neighbours y.",
        "Without recursion: treat each cell's count of smaller neighbours as an in-degree and run Kahn's algorithm in layers. The number of layers is the answer.",
    ],
    opt=("O(r·c)", "O(r·c)", "Every cell and each of its four edges is processed once."),
    editorial=(
        "## The one thing this teaches\n**Strict order means no cycles.** Drawing an edge from "
        "each cell to every *larger* neighbour gives a directed graph in which a cycle would need "
        "a value larger than itself. So it is a DAG, the longest path is well-defined, and both "
        "tools for DAGs apply.\n\n"
        "## Approach — memoised DFS\n```java\nint dfs(int x, int y) {\n"
        "    if (memo[x][y] != 0) return memo[x][y];\n    int best = 1;\n"
        "    for (each neighbour (nx, ny) with m[nx][ny] > m[x][y]) best = Math.max(best, 1 + dfs(nx, ny));\n"
        "    return memo[x][y] = best;\n}\n```\n\n"
        "## Approach — topological layers\nCount, for every cell, how many neighbours are "
        "smaller: that is its in-degree. Cells with 0 are the starts of paths. Remove a layer, "
        "decrement larger neighbours, and repeat. A path of length L needs L layers, so the "
        "number of layers is the answer — and there is no recursion to overflow on a 200×200 "
        "snake.\n\n"
        "## Why no visited set\nIn most grid searches a missing visited set loops forever. Here "
        "strictness makes revisiting impossible, which is also why the memo is sound: a cell's "
        "answer does not depend on how you arrived."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])
    indeg = [[0] * c for _ in range(r)]
    for i in range(r):
        for j in range(c):
            for ni, nj in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= ni < r and 0 <= nj < c and m[ni][nj] < m[i][j]:
                    indeg[i][j] += 1
    q = deque((i, j) for i in range(r) for j in range(c) if indeg[i][j] == 0)
    layers = 0
    while q:
        layers += 1
        for _ in range(len(q)):
            i, j = q.popleft()
            for ni, nj in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= ni < r and 0 <= nj < c and m[ni][nj] > m[i][j]:
                    indeg[ni][nj] -= 1
                    if indeg[ni][nj] == 0:
                        q.append((ni, nj))
    return layers
''',
    java='''
    static int solve(int[][] m) {
        int r = m.length, c = m[0].length;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int[][] indeg = new int[r][c];
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                for (int[] d : dirs) {
                    int x = i + d[0], y = j + d[1];
                    if (x >= 0 && y >= 0 && x < r && y < c && m[x][y] < m[i][j]) indeg[i][j]++;
                }
        ArrayDeque<int[]> q = new ArrayDeque<>();
        for (int i = 0; i < r; i++) for (int j = 0; j < c; j++) if (indeg[i][j] == 0) q.add(new int[]{i, j});
        int layers = 0;
        while (!q.isEmpty()) {
            layers++;
            for (int k = q.size(); k > 0; k--) {
                int[] cur = q.poll();
                for (int[] d : dirs) {
                    int x = cur[0] + d[0], y = cur[1] + d[1];
                    if (x >= 0 && y >= 0 && x < r && y < c && m[x][y] > m[cur[0]][cur[1]] && --indeg[x][y] == 0)
                        q.add(new int[]{x, y});
                }
            }
        }
        return layers;
    }
''',
    examples=[("Example 1", "3 3\n9 9 4\n6 6 8\n2 1 1\n"), ("Example 2", "3 3\n3 4 5\n3 2 6\n2 2 1\n")],
    hidden=[
        ("Single cell", "1 1\n7\n"),
        ("All equal", "2 2\n1 1\n1 1\n"),
        ("Spiral uses every cell", "3 3\n1 2 3\n8 9 4\n7 6 5\n"),
        ("Snake", "2 3\n1 2 3\n6 5 4\n"),
    ],
    expl=[
        "1 → 2 → 6 → 9.",
        "3 → 4 → 5 → 6. Equal neighbours cannot be chained.",
    ],
    prereqs=[
        ("topo", "The strictly increasing moves form a DAG, peeled in layers by in-degree."),
        ("dp", "Equivalently, a memoised longest path from each cell over its larger neighbours."),
    ],
)
