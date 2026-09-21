# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 43 — geometry, which the roadmap had nothing for at all.
#
#   turn-directions         the cross product, as "which way did I turn?"
#   polygon-area-doubled    the shoelace formula, which is the same cross product summed
#   count-crossing-segments orientation tests, and the collinear cases that break them
#   convex-hull-points      Andrew's monotone chain
#
# Every one of these is the SAME primitive. The unit exists so that primitive
# gets learned once, with its sign convention and its integer arithmetic,
# instead of four times badly.
# ===========================================================================

_p(
    "turn-directions", "Which Way Did You Turn?", "Easy",
    topics=["Math", "Arrays"], subtopics=["Cross Product", "Geometry"],
    companies=["Amazon", "Uber"],
    shape="pairs", ret="String",
    todo="for each middle point, take the cross product of the incoming and outgoing vectors and read its sign",
    description=(
        "A delivery van visits `n` points in the order given. At every point except the first "
        "and the last it either turns left, turns right, or carries straight on.\n\n"
        "Print a string of `n-2` characters — `L`, `R` or `S` — one per turn, in order. "
        "Axes are the usual ones: x grows to the right, y grows upwards.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `x y`.\n\n"
        "### Output\nThe turn string."
    ),
    constraints="3 ≤ n ≤ 100000\n-10^6 ≤ x, y ≤ 10^6\n"
                "Consecutive points are always different.",
    hints=[
        "Angles, `atan2` and degrees will work and will also give you floating-point comparisons you cannot trust. There is an exact integer answer.",
        "The cross product of two 2-D vectors is the single number `ux·vy − uy·vx`. Its *sign* says which side of `u` the vector `v` falls on.",
        "With `u` the incoming vector and `v` the outgoing one: positive means a left turn, negative a right turn, zero means they are parallel — straight on.",
    ],
    opt=("O(n)", "O(n) for the output",
         "One cross product per interior point; two multiplications and a subtraction each."),
    editorial=(
        "## The one thing this teaches\n**The 2-D cross product is the whole of elementary "
        "geometry.** Orientation, area, \"is this point left of that line\", segment intersection "
        "and convex hulls are all the sign or the magnitude of this one expression:\n\n"
        "```java\nstatic long cross(long ax, long ay, long bx, long by, long cx, long cy) {\n"
        "    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);\n}\n```\n\n"
        "It is the z-component of the 3-D cross product of the two vectors, laid flat. Its "
        "magnitude is twice the area of the triangle ABC, and its sign is the orientation: "
        "**positive = counter-clockwise = left turn**.\n\n"
        "## Approach\n```java\nStringBuilder sb = new StringBuilder();\n"
        "for (int i = 1; i + 1 < n; i++) {\n"
        "    long c = cross(p[i-1][0], p[i-1][1], p[i][0], p[i][1], p[i+1][0], p[i+1][1]);\n"
        "    sb.append(c > 0 ? 'L' : c < 0 ? 'R' : 'S');\n}\n```\n\n"
        "## Keep it in integers\nWith coordinates to 10⁶ the differences reach 2·10⁶ "
        "and the product 4·10¹² — past `int`, so **cast to `long` before "
        "multiplying**. `(bx - ax) * (cy - ay)` with `int` operands overflows *before* the "
        "assignment, and the sign that comes out is arbitrary. This is the single most common "
        "geometry bug, and it does not show up on small tests.\n\n"
        "## Why not doubles\nA cross product of exactly 0 means collinear. In floating point it "
        "means \"about 10⁻¹³\", and now you need an epsilon whose right value "
        "depends on the input scale. When the input is integers, stay in integers and the "
        "collinear case is exact.\n\n"
        "## The sign convention\nPositive is counter-clockwise in the standard orientation "
        "(y upwards). On a screen, where y grows *downwards*, the same number means clockwise — "
        "so state which convention you are using before you argue about a sign."
    ),
    py='''
def solve(p):
    out = []
    for i in range(1, len(p) - 1):
        ax, ay = p[i - 1]
        bx, by = p[i]
        cx, cy = p[i + 1]
        cr = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        out.append("L" if cr > 0 else ("R" if cr < 0 else "S"))
    return "".join(out)
''',
    java='''
    static String solve(int[][] p) {
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i + 1 < p.length; i++) {
            long ax = p[i - 1][0], ay = p[i - 1][1];
            long bx = p[i][0], by = p[i][1];
            long cx = p[i + 1][0], cy = p[i + 1][1];
            long cr = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
            sb.append(cr > 0 ? 'L' : cr < 0 ? 'R' : 'S');
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "4\n0 0\n2 0\n2 2\n0 2\n"),
        ("Example 2", "3\n0 0\n1 1\n2 2\n"),
    ],
    hidden=[
        ("A single right turn", "3\n0 0\n1 0\n1 -1\n"),
        ("A zigzag", "6\n0 0\n1 0\n1 1\n2 1\n2 0\n3 0\n"),
        ("Doubling back", "3\n0 0\n5 0\n0 0\n"),
        ("Large coordinates", "4\n-1000000 -1000000\n1000000 -1000000\n1000000 1000000\n-1000000 1000000\n"),
        ("A spiral of left turns", "7\n0 0\n4 0\n4 4\n1 4\n1 1\n3 1\n3 3\n"),
    ],
    expl=[
        "Walking the bottom edge then up the right edge is a left turn, and again at the top-right corner: `LL`.",
        "Three points on one line — no turn at all.",
    ],
    prereqs=[
        ("arithmetic", "A product of two differences."),
        ("overflow", "10^6 coordinates make 4·10^12 products."),
    ],
)


_p(
    "polygon-area-doubled", "How Much Land", "Easy",
    topics=["Math", "Arrays"], subtopics=["Shoelace Formula", "Cross Product", "Geometry"],
    companies=["Amazon", "Google"],
    shape="pairs", ret="long",
    todo="sum x[i]*y[i+1] - x[i+1]*y[i] around the polygon, wrapping at the end, and take the absolute value",
    description=(
        "A field is a simple polygon — its edges do not cross — given by its `n` corners "
        "in order around the boundary, either clockwise or counter-clockwise.\n\n"
        "Its area may be a half-integer, so print **twice** the area, which is always a whole "
        "number.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `x y`.\n\n"
        "### Output\nTwice the area of the polygon."
    ),
    constraints="3 ≤ n ≤ 100000\n-10^6 ≤ x, y ≤ 10^6\n"
                "The polygon is simple and no two consecutive corners coincide.",
    hints=[
        "Chopping the shape into triangles by hand is hard for a non-convex field — and unnecessary.",
        "Take triangles from the **origin** to each edge instead. Their signed areas are cross products, and the parts outside the polygon cancel because their signs oppose.",
        "So the answer is `|Σ (x[i]·y[i+1] − x[i+1]·y[i])|`, with `i+1` wrapping to 0 at the end. Doubling the area is what removes the ½ and keeps it integral.",
    ],
    opt=("O(n)", "O(1)",
         "One pass around the boundary; two multiplications per edge."),
    editorial=(
        "## The one thing this teaches\n**The shoelace formula is the cross product, summed "
        "around a loop.** Each term is twice the signed area of the triangle (origin, corner i, "
        "corner i+1), and signed areas telescope: whatever a triangle covers outside the polygon "
        "is covered again with the opposite sign by another edge.\n\n"
        "## Approach\n```java\nlong s = 0;\nfor (int i = 0; i < n; i++) {\n"
        "    int j = (i + 1) % n;\n"
        "    s += (long) p[i][0] * p[j][1] - (long) p[j][0] * p[i][1];\n}\nreturn Math.abs(s);\n```\n\n"
        "## Why the origin does not matter\nShifting every corner by the same vector leaves the "
        "sum unchanged — the shifts cancel in pairs around the loop. So the origin can sit "
        "inside the field, outside it, or on a corner, and the answer is the same.\n\n"
        "## The sign you threw away\n`s` is *positive* when the corners are listed "
        "counter-clockwise and negative when clockwise, so the raw sum also tells you the "
        "polygon's orientation. Taking the absolute value at the end is the only reason the "
        "input may be given either way round.\n\n"
        "## Why twice the area\nThe true area is `|s| / 2`, and halving would force floating "
        "point or a fraction for an odd `s` — a triangle with corners (0,0), (1,0), (0,1) has "
        "area ½. Interview and contest statements ask for `2A` for exactly this reason.\n\n"
        "## Overflow\nA single term reaches 10⁶·10⁶ = 10¹², and 10⁵ of "
        "them reach 10¹⁷. That fits a `long` and does not fit an `int` — cast before "
        "the multiplication, not after."
    ),
    py='''
def solve(p):
    n = len(p)
    s = 0
    for i in range(n):
        x1, y1 = p[i]
        x2, y2 = p[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s)
''',
    java='''
    static long solve(int[][] p) {
        int n = p.length;
        long s = 0;
        for (int i = 0; i < n; i++) {
            int j = (i + 1) % n;
            s += (long) p[i][0] * p[j][1] - (long) p[j][0] * p[i][1];
        }
        return Math.abs(s);
    }
''',
    examples=[
        ("Example 1", "4\n0 0\n4 0\n4 3\n0 3\n"),
        ("Example 2", "3\n0 0\n1 0\n0 1\n"),
    ],
    hidden=[
        ("Listed clockwise", "4\n0 0\n0 3\n4 3\n4 0\n"),
        ("An L-shaped field", "6\n0 0\n4 0\n4 2\n2 2\n2 4\n0 4\n"),
        ("Far from the origin", "4\n1000 1000\n1005 1000\n1005 1002\n1000 1002\n"),
        ("Negative coordinates", "4\n-3 -3\n3 -3\n3 3\n-3 3\n"),
        ("Extreme coordinates", "4\n-1000000 -1000000\n1000000 -1000000\n1000000 1000000\n-1000000 1000000\n"),
        ("A thin sliver", "3\n0 0\n1000000 1\n1000000 0\n"),
    ],
    expl=[
        "A 4 by 3 rectangle has area 12, so twice the area is 24.",
        "A right triangle with legs 1 and 1 has area ½ — which is why the answer asked for is 1.",
    ],
    prereqs=[
        ("arithmetic", "A sum of products around a cycle."),
        ("array_patterns", "Wrapping from the last element back to the first."),
        ("overflow", "10^12 per term over 10^5 terms."),
    ],
)


_p(
    "count-crossing-segments", "Which Cables Touch", "Medium",
    topics=["Math", "Arrays"], subtopics=["Line Intersection", "Cross Product", "Geometry"],
    companies=["Google", "Bloomberg"],
    shape="pairs", ret="long",
    todo="for each pair of segments compare the four orientations; handle the collinear case with a bounding-box test",
    description=(
        "`n` points describe `n / 2` cables: points 1 and 2 are the ends of the first cable, "
        "points 3 and 4 of the second, and so on. `n` is always even.\n\n"
        "Two cables **touch** if they share at least one point — crossing in the middle, "
        "meeting at an endpoint, or overlapping along a stretch all count.\n\n"
        "Print how many of the pairs of cables touch.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `x y`.\n\n"
        "### Output\nThe number of touching pairs."
    ),
    constraints="2 ≤ n ≤ 200, and `n` is even\n-10^6 ≤ x, y ≤ 10^6\n"
                "A cable's two ends may coincide, making it a single point.",
    hints=[
        "Solving for the intersection point with fractions invites both division by zero (parallel cables) and floating-point error. Ask a yes/no question instead.",
        "Segments AB and CD cross properly when C and D fall on opposite sides of line AB **and** A and B fall on opposite sides of line CD — four cross-product signs.",
        "That test misses every touching case where a sign is zero. Handle those separately: if a point is collinear with the other segment, check whether it lies inside that segment's bounding box.",
    ],
    opt=("O(n²)", "O(1)",
         "Every pair of the n/2 cables, with a constant-time exact test."),
    editorial=(
        "## The one thing this teaches\n**Ask for a sign, not for a coordinate.** The "
        "intersection *point* needs division and floating point; whether an intersection *exists* "
        "needs four integer cross products and no division at all.\n\n"
        "## The proper-crossing test\n```java\nint o1 = sign(cross(a, b, c)), o2 = sign(cross(a, b, d));\n"
        "int o3 = sign(cross(c, d, a)), o4 = sign(cross(c, d, b));\n"
        "if (o1 != o2 && o3 != o4) return true;      // they cross in their interiors\n```\n"
        "`o1 != o2` says C and D are strictly on opposite sides of line AB. Both conditions "
        "together are needed: either alone allows a segment to miss the other one's span.\n\n"
        "## The collinear cases, which are where the bugs live\nAll four of these touch and all "
        "four have a zero among the orientations — a T-junction, a shared endpoint, one "
        "cable's end lying on the other, and two overlapping cables on one line. So:\n"
        "```java\nif (o1 == 0 && onSegment(a, b, c)) return true;\n"
        "if (o2 == 0 && onSegment(a, b, d)) return true;\n"
        "if (o3 == 0 && onSegment(c, d, a)) return true;\n"
        "if (o4 == 0 && onSegment(c, d, b)) return true;\nreturn false;\n```\n"
        "where `onSegment` is a bounding-box check, valid *only* because collinearity is already "
        "known:\n```java\nstatic boolean onSegment(int[] a, int[] b, int[] c) {\n"
        "    return Math.min(a[0], b[0]) <= c[0] && c[0] <= Math.max(a[0], b[0])\n"
        "        && Math.min(a[1], b[1]) <= c[1] && c[1] <= Math.max(a[1], b[1]);\n}\n```\n\n"
        "## Why the box test needs collinearity first\nOn its own it is wrong: (1,1) is inside "
        "the bounding box of the segment (0,0)–(2,0) and nowhere near it. The zero cross "
        "product supplies the missing half of the claim.\n\n"
        "## Degenerate cables\nA cable whose ends coincide is a point. The proper test can never "
        "fire for it (all four orientations involving it collapse), so it is handled entirely by "
        "the collinear branch — which is another reason not to skip that branch as an "
        "\"edge case\"."
    ),
    py='''
def solve(p):
    def sign(v):
        return (v > 0) - (v < 0)

    def cross(a, b, c):
        return sign((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))

    def on_seg(a, b, c):
        return (min(a[0], b[0]) <= c[0] <= max(a[0], b[0])
                and min(a[1], b[1]) <= c[1] <= max(a[1], b[1]))

    def touch(a, b, c, d):
        o1, o2 = cross(a, b, c), cross(a, b, d)
        o3, o4 = cross(c, d, a), cross(c, d, b)
        if o1 != o2 and o3 != o4:
            return True
        if o1 == 0 and on_seg(a, b, c):
            return True
        if o2 == 0 and on_seg(a, b, d):
            return True
        if o3 == 0 and on_seg(c, d, a):
            return True
        if o4 == 0 and on_seg(c, d, b):
            return True
        return False

    segs = [(p[2 * i], p[2 * i + 1]) for i in range(len(p) // 2)]
    count = 0
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            if touch(segs[i][0], segs[i][1], segs[j][0], segs[j][1]):
                count += 1
    return count
''',
    java='''
    static int sgn(long v) { return v > 0 ? 1 : v < 0 ? -1 : 0; }

    static int cross(int[] a, int[] b, int[] c) {
        long v = (long) (b[0] - a[0]) * (c[1] - a[1]) - (long) (b[1] - a[1]) * (c[0] - a[0]);
        return sgn(v);
    }

    static boolean onSeg(int[] a, int[] b, int[] c) {
        return Math.min(a[0], b[0]) <= c[0] && c[0] <= Math.max(a[0], b[0])
            && Math.min(a[1], b[1]) <= c[1] && c[1] <= Math.max(a[1], b[1]);
    }

    static boolean touch(int[] a, int[] b, int[] c, int[] d) {
        int o1 = cross(a, b, c), o2 = cross(a, b, d);
        int o3 = cross(c, d, a), o4 = cross(c, d, b);
        if (o1 != o2 && o3 != o4) return true;
        if (o1 == 0 && onSeg(a, b, c)) return true;
        if (o2 == 0 && onSeg(a, b, d)) return true;
        if (o3 == 0 && onSeg(c, d, a)) return true;
        if (o4 == 0 && onSeg(c, d, b)) return true;
        return false;
    }

    static long solve(int[][] p) {
        int k = p.length / 2;
        long count = 0;
        for (int i = 0; i < k; i++)
            for (int j = i + 1; j < k; j++)
                if (touch(p[2 * i], p[2 * i + 1], p[2 * j], p[2 * j + 1])) count++;
        return count;
    }
''',
    examples=[
        ("Example 1", "4\n0 0\n4 4\n0 4\n4 0\n"),
        ("Example 2", "4\n0 0\n1 0\n0 1\n1 1\n"),
    ],
    hidden=[
        ("One cable only", "2\n0 0\n5 5\n"),
        ("A shared endpoint", "4\n0 0\n2 0\n2 0\n2 2\n"),
        ("A T-junction", "4\n0 0\n4 0\n2 0\n2 5\n"),
        ("Collinear and overlapping", "4\n0 0\n4 0\n2 0\n6 0\n"),
        ("Collinear and apart", "4\n0 0\n1 0\n2 0\n3 0\n"),
        ("A degenerate point cable on another", "4\n0 0\n6 6\n3 3\n3 3\n"),
        ("Three cables, one touching pair", "6\n0 0\n4 4\n0 4\n4 0\n10 10\n12 12\n"),
    ],
    expl=[
        "The two diagonals of the square cross at (2, 2) — one touching pair.",
        "Two parallel horizontal cables one unit apart never meet.",
    ],
    prereqs=[
        ("arithmetic", "Cross products, compared only by sign."),
        ("conditionals", "Four orientation cases and their collinear fallbacks."),
        ("overflow", "Coordinate differences multiplied together."),
    ],
)


_p(
    "convex-hull-points", "Stretch the Rubber Band", "Hard",
    topics=["Math", "Arrays", "Sorting"], subtopics=["Convex Hull", "Monotone Chain", "Cross Product"],
    companies=["Google", "Amazon", "Meta"],
    shape="pairs", ret="String",
    todo="sort the points, sweep left to right building the lower chain and right to left for the upper, popping whenever the last turn is not a left turn",
    description=(
        "`n` fence posts stand in a field. Stretch a rubber band around all of them and let it "
        "snap tight: it touches a subset of the posts — the **convex hull**.\n\n"
        "Print the posts the band touches at a **corner**. A post lying flat on a straight "
        "stretch of band, between two others, is not a corner and must be left out.\n\n"
        "Duplicate posts count as one. List the corners **counter-clockwise**, starting from the "
        "one with the smallest `x` (and, among those, the smallest `y`).\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `x y`.\n\n"
        "### Output\nLine 1: `k`, the number of corners.\nNext `k` lines: `x y`."
    ),
    constraints="1 ≤ n ≤ 100000\n-10^6 ≤ x, y ≤ 10^6\nPosts may repeat.",
    hints=[
        "Sort the distinct points by x, then by y. Now build the hull in two halves: the lower boundary going left to right, and the upper boundary coming back.",
        "Push points onto a stack. Before pushing, while the last two stack entries and the new point do **not** make a left turn, pop — the middle one is inside or on the boundary.",
        "Popping on `cross <= 0` (rather than `< 0`) also removes points that lie exactly on an edge, which is what “corners only” asks for. Drop each chain's last point before joining them, or the two shared endpoints appear twice.",
    ],
    opt=("O(n log n)", "O(n)",
         "The sort dominates; the two sweeps push and pop each point at most once."),
    editorial=(
        "## The one thing this teaches\n**Andrew's monotone chain: sort, then sweep with a "
        "stack.** It is the same discipline as a monotonic stack — keep only the candidates "
        "no later candidate has made irrelevant — with \"turns the wrong way\" as the "
        "domination test.\n\n"
        "## Approach\n```java\nsortByXThenY(pts);                    // distinct points\n"
        "long[][] lower = new long[pts.length][];\nint k = 0;\n"
        "for (int[] q : pts) {\n"
        "    while (k >= 2 && cross(lower[k-2], lower[k-1], q) <= 0) k--;\n"
        "    lower[k++] = q;\n}\n// same loop over the points in reverse for the upper chain\n"
        "// hull = lower minus its last point, then upper minus its last point\n```\n\n"
        "## Why two chains\nA single sweep left to right can only ever produce one boundary — "
        "the points below every line through their neighbours. Reversing the order and repeating "
        "produces the other. Each chain's last point is the other chain's first, so both are "
        "dropped when they are concatenated.\n\n"
        "## `<= 0` versus `< 0`\nThis is the whole difference between \"corners only\" and \"every "
        "point on the boundary\". `<= 0` pops a collinear middle point and produces the minimal "
        "hull; `< 0` keeps it. The statement decides which one is wanted, and getting this "
        "backwards is the most common way this problem fails on a test with three collinear "
        "points.\n\n"
        "## The degenerate inputs\nOne distinct point: the hull is that point. Two: both. All "
        "collinear: the two extremes, since every point in between is popped. Handle these before "
        "the chains, or the concatenation drops points it should keep.\n\n"
        "## Why this output is unique\n\"Counter-clockwise from the lexicographically smallest "
        "corner\" pins down the one starting point and the one direction, and dropping collinear "
        "points pins down the set — so there is exactly one correct answer to compare "
        "against. A hull problem without those three sentences has many."
    ),
    py='''
def solve(p):
    pts = sorted(set((x, y) for x, y in p))
    if len(pts) <= 2:
        hull = pts
    else:
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        lower = []
        for q in pts:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
                lower.pop()
            lower.append(q)
        upper = []
        for q in reversed(pts):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
                upper.pop()
            upper.append(q)
        hull = lower[:-1] + upper[:-1]
    lines = [str(len(hull))]
    lines += ["%d %d" % (x, y) for x, y in hull]
    return "\\n".join(lines)
''',
    java='''
    static long crossH(long[] o, long[] a, long[] b) {
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    }

    static String solve(int[][] p) {
        TreeSet<long[]> set = new TreeSet<>((x, y) ->
            x[0] != y[0] ? Long.compare(x[0], y[0]) : Long.compare(x[1], y[1]));
        for (int[] q : p) set.add(new long[]{q[0], q[1]});
        long[][] pts = set.toArray(new long[0][]);
        List<long[]> hull = new ArrayList<>();
        if (pts.length <= 2) {
            hull.addAll(Arrays.asList(pts));
        } else {
            long[][] lower = new long[pts.length][];
            int k = 0;
            for (long[] q : pts) {
                while (k >= 2 && crossH(lower[k - 2], lower[k - 1], q) <= 0) k--;
                lower[k++] = q;
            }
            long[][] upper = new long[pts.length][];
            int u = 0;
            for (int i = pts.length - 1; i >= 0; i--) {
                long[] q = pts[i];
                while (u >= 2 && crossH(upper[u - 2], upper[u - 1], q) <= 0) u--;
                upper[u++] = q;
            }
            for (int i = 0; i < k - 1; i++) hull.add(lower[i]);
            for (int i = 0; i < u - 1; i++) hull.add(upper[i]);
        }
        StringBuilder sb = new StringBuilder();
        sb.append(hull.size());
        for (long[] q : hull) sb.append('\\n').append(q[0]).append(' ').append(q[1]);
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\n0 0\n4 0\n4 4\n0 4\n2 2\n"),
        ("Example 2", "4\n0 0\n1 1\n2 2\n3 3\n"),
    ],
    hidden=[
        ("One post", "1\n7 9\n"),
        ("The same post repeated", "3\n5 5\n5 5\n5 5\n"),
        ("A triangle with a point on an edge", "4\n0 0\n6 0\n3 0\n0 6\n"),
        ("A square with interior clutter", "8\n0 0\n10 0\n10 10\n0 10\n3 3\n7 2\n5 5\n1 9\n"),
        ("A vertical line", "3\n2 -5\n2 0\n2 7\n"),
        ("Extreme coordinates", "5\n-1000000 -1000000\n1000000 -1000000\n1000000 1000000\n-1000000 1000000\n0 0\n"),
        ("A convex polygon, every post a corner", "6\n0 0\n4 1\n6 5\n4 9\n1 8\n-1 4\n"),
    ],
    expl=[
        "The band touches the four corners of the square; the post at (2, 2) is strictly inside and is not touched.",
        "All four posts lie on one line, so the band collapses onto the two extreme ones.",
    ],
    prereqs=[
        ("sorting", "The points ordered by x, then y."),
        ("stack", "Popping candidates a later point makes irrelevant."),
        ("arithmetic", "The cross product, as a turn test."),
    ],
)
