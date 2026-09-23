# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# 6-Month Mastery programme — the curated, week-by-week track.
#
# The Learn tab is a reference library: 50 TypeScript chapters you can read in
# any order. This file turns that library into a *programme* — 26 weeks, each
# with a theme, a short list of concepts to study, curated Library problems to
# solve, a build project, and an end-of-week quiz that gates the next week.
#
# exec()'d inside gen_seed.py's namespace AFTER typescript_mastery.py, so every
# concept key referenced below already exists. gen_seed.py writes the result to
# src-tauri/seeds/mastery.json, which the `mastery` Tauri command serves.
#
# INVARIANTS the build asserts (see the checks at the bottom of this file):
#   * every `concepts` key resolves to a real concept in CONCEPTS
#   * every `problems` slug resolves to a real problem in the seed bank
#   * every concept in the track's language is scheduled exactly once, so the
#     programme genuinely covers the syllabus with nothing repeated or dropped
#   * every quiz question's `answer` indexes a real option
# ---------------------------------------------------------------------------


def _q(question, options, answer, explanation):
    return {
        "question": question,
        "options": list(options),
        "answer": answer,
        "explanation": explanation,
    }


def _w(week, phase, title, goal, concepts, problems, project, quiz, optional=False):
    """One week of the programme. `problems` is a list of (slug, why) pairs.
    `optional` marks a week after the programme proper (see the field below).

    `exam`, `contest`, `quiz_from` and `quiz_sample` are attached afterwards by
    `_attach` so the week tables above stay readable."""
    return {
        "week": week,
        "phase": phase,
        "title": title,
        "goal": goal,
        "concepts": concepts,
        "problems": [{"slug": s, "note": n} for (s, n) in problems],
        "project": project,
        "quiz": [_q(*row) for row in quiz],
        # Filled in by _attach / _finalize_mastery.
        "quiz_from": [],
        "quiz_sample": 4,
        "exam": None,
        "contest": None,
        # Authored review cards, seeded into the flashcard deck when the week
        # is completed. Filled per track after the tables (mastery_ts_cards.py).
        "flashcards": [],
        # Optional graded practice (mastery_ts_practice.py); never gates.
        "practice": [],
        # A week after the programme proper (the TypeScript capstone): open once
        # the week before it is done, never counted toward totals or pace.
        "optional": optional,
        # The week's own tiered problem set, and the project as a runnable
        # brief (mastery_ts_kit.py). Empty / None until a track authors them.
        "problem_set": [],
        "project_spec": None,
    }


def _attach(weeks, exams, extra_quiz=None, quiz_from=None, contests=None, sample=4):
    """Bolt the coding finals, extra bank questions, cross-track quiz sources and
    checkpoint contests onto an already-authored week list."""
    extra_quiz = extra_quiz or {}
    quiz_from = quiz_from or {}
    contests = contests or {}
    for w in weeks:
        n = w["week"]
        w["quiz"].extend(_q(*row) for row in extra_quiz.get(n, []))
        w["quiz_from"] = list(quiz_from.get(n, []))
        w["quiz_sample"] = sample
        w["exam"] = exams.get(n)
        if n in contests:
            title, seconds = contests[n]
            w["contest"] = {"title": title, "duration_seconds": seconds}
    return weeks


def _finalize_mastery(tracks, concepts):
    """Expand each week's question BANK: the authored questions, plus the quiz
    questions already written for the concepts that week studies, plus any
    cross-track concepts named in `quiz_from` (the Java track reuses the
    language-agnostic Algorithms and Java Vocab banks this way).

    The UI samples `quiz_sample` of the bank and shuffles, so a retake is not a
    memory test for answer positions. Deduped by question text; `quiz_from` is
    consumed here and dropped from the emitted JSON."""
    for track in tracks:
        for week in track["weeks"]:
            seen = {q["question"] for q in week["quiz"]}
            sources = list(week["concepts"]) + list(week.pop("quiz_from", []))
            for key in sources:
                for q in concepts.get(key, {}).get("quiz", []) or []:
                    if q["question"] in seen:
                        continue
                    seen.add(q["question"])
                    week["quiz"].append(q)
            # Never ask for more questions than the bank can supply.
            week["quiz_sample"] = min(week["quiz_sample"], len(week["quiz"]))


# ===========================================================================
# TypeScript coding finals — one per week.
#
# A multiple-choice quiz is the weakest possible gate for a programming
# curriculum, so every week also ends with a real problem run through the same
# judge as the Learn challenges (`run_tests` with a null problem id). The week
# only unlocks the next one when BOTH are passed.
#
# Each final synthesises the week's chapters rather than drilling one of them,
# and is scoped to what the syllabus has taught so far. Every `solution` is
# proven end-to-end by tests/verify_mastery.rs.
# ===========================================================================

_TS_SCAFFOLD = 'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8").trim();\n'


def _ts_exam(title, prompt, body, tests, hint=""):
    """A TypeScript final: the stdin scaffold plus one `____` for the whole
    solution, exactly like a Learn challenge."""
    body = body.strip("\n")
    solution = _TS_SCAFFOLD + body + "\n"
    return {
        "title": title,
        "prompt": prompt,
        "hint": hint,
        "language": "typescript",
        "starter": _TS_SCAFFOLD + "____\n",
        "solution": solution,
        "tests": [{"input": i, "output": o} for (i, o) in tests],
    }


def _ts_exam_io(eid, title, prompt, body, inputs, hint="", strictness="strict+indexed"):
    """A final that names only its inputs: the expected outputs are computed by
    running the reference (ts_outputs_kit.py, `python tools/gen_ts_outputs.py`).
    `strictness` must match the week's (TS_INDEXED_FROM_WEEK below)."""
    solution = _TS_SCAFFOLD + body.strip("\n") + "\n"
    tests = _computed(eid, solution, inputs, strictness)
    return _ts_exam(title, prompt, body, [(t["input"], t["output"]) for t in tests], hint)


# ---------------------------------------------------------------------------
# The TypeScript weeks live one month per file — tools/mastery_ts_m1.py ..
# mastery_ts_m6.py — exec'd in order. Each appends its weeks to TS_WEEKS and
# fills the three per-week tables below:
#
#   TS_EXAMS            the coding final (`_ts_exam`)
#   TS_QUIZ_EXTRA       authored bank questions. Weeks whose chapters carry
#                       their own quizzes get a deep bank for free via
#                       _finalize_mastery; the rest need questions of their own.
#   TS_EXAM_MORE_TESTS  extra final tests (see the comment on the loop below)
# ---------------------------------------------------------------------------
TS_INDEXED_FROM_WEEK = 14  # the strictness ladder — see the comment further down
TS_WEEKS = []
TS_EXAMS = {}
TS_QUIZ_EXTRA = {}
TS_EXAM_MORE_TESTS = {}
for _ts_month in range(1, 7):
    _ts_month_path = os.path.join(HERE, f"mastery_ts_m{_ts_month}.py")
    with open(_ts_month_path, encoding="utf-8") as _ts_mf:
        exec(compile(_ts_mf.read(), _ts_month_path, "exec"))

TS_CONTESTS = {
    4: ("Checkpoint — Month 1: language foundations", 60 * 60),
    8: ("Checkpoint — Month 2: functions & data", 75 * 60),
    13: ("Mastery checkpoint — Months 1–3", 90 * 60),
    17: ("Checkpoint — Month 4: rigor", 90 * 60),
    22: ("Checkpoint — Month 5: generics & type-level", 90 * 60),
    26: ("Mastery finale — the whole programme", 120 * 60),
}

# The monthly checkpoints draw on the whole month, not just their own week — a
# timed set that mixes weeks is what shows whether the month has stuck. Week
# 13 keeps drawing on its own (already cross-month) review problems.
TS_CONTEST_SLUGS = {
    4: ["leap-year", "is-prime", "count-words", "caesar-cipher"],
    8: ["fizzbuzz-value", "sort-by-frequency", "second-largest", "run-length-encode"],
    17: ["missing-number", "product-except-self", "longest-common-prefix-strs", "merge-intervals"],
    22: ["kth-largest-element", "time-based-kv", "top-k-frequent", "implement-trie-ops"],
    # The finale spans the programme rather than its last week's problems.
    26: ["longest-unique-substring", "evaluate-rpn", "hit-counter", "median-from-stream",
         "word-ladder-length"],
}

# ---------------------------------------------------------------------------
# More tests for the TypeScript finals. The originals had 2-5 each, which is
# too few to gate a week on: a final with two tests can be passed by special-
# casing them. These bring every final to at least 8, and aim at the edges the
# originals skipped — empty and single-item input, duplicates, boundaries,
# unsorted input, and (weeks 15 and 19) inherited keys like `toString`, which
# `name in obj` wrongly accepts.
#
# Every expected output here was produced by running the week's reference
# solution, not typed by hand, and tests/verify_mastery.rs re-proves all of
# them against the real judge.
# (The tests themselves are in each month file's TS_EXAM_MORE_TESTS.)
# ---------------------------------------------------------------------------
for _wk, _pairs in TS_EXAM_MORE_TESTS.items():
    TS_EXAMS[_wk]["tests"].extend({"input": i, "output": o} for (i, o) in _pairs)

# The strictness ladder. Week 14 teaches `noUncheckedIndexedAccess`, and its own
# final is "treat every index and map access as possibly missing" — which used
# to be graded at plain `strict`, where `lines[i]` is a `string` and nothing
# needs treating. From week 14 on, every final is checked the way the week
# teaches: an index read is `T | undefined` until you handle it. (The constant
# is defined above the month files, which need it for computed outputs.)
for _wk, _exam in TS_EXAMS.items():
    _exam["strictness"] = "strict+indexed" if _wk >= TS_INDEXED_FROM_WEEK else ""
TS_EXAMS[TS_INDEXED_FROM_WEEK]["prompt"] += (
    " This final — and every one after it — is checked with `noUncheckedIndexedAccess` on,"
    " so `lines[i]` is `string | undefined` until you deal with the missing case."
)

_attach(TS_WEEKS, TS_EXAMS, extra_quiz=TS_QUIZ_EXTRA, contests=TS_CONTESTS, sample=4)
for _tsw in TS_WEEKS:
    if _tsw["contest"] is not None:
        _tsw["contest"]["slugs"] = list(TS_CONTEST_SLUGS.get(_tsw["week"], []))




# ===========================================================================
# JAVA MASTERY TRACK
#
# The same 26-week shape as the TypeScript programme, over the Java syllabus:
# language foundations, then the array/string scanning patterns, then the data
# structures, then trees, then recursion/DP, then graphs.
#
# Its question banks lean on two existing, already-authored sets of quizzes —
# the language-agnostic Algorithms track and the Java Vocab track — pulled in
# per week via `quiz_from`. Those are real questions about exactly this
# material, so reusing them is better than paraphrasing them.
# ===========================================================================

_JAVA_SCAFFOLD = (
    "import java.util.*;\n\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
)


def _java_exam(title, prompt, body, tests, hint=""):
    """A Java final: the Scanner scaffold plus one `____` for the whole body."""
    indented = _b(body)
    return {
        "title": title,
        "prompt": prompt,
        "hint": hint,
        "language": "java",
        "starter": prog("        ____"),
        "solution": prog(indented),
        "tests": [{"input": i, "output": o} for (i, o) in tests],
    }


def _java_exam_cls(title, prompt, members, blank, tests, hint=""):
    """A Java final that needs class-level members (a helper method or a Node
    class). `members` is the full class body; `blank` is the fragment of it the
    learner writes, quoted verbatim."""
    full = _cls(members.strip("\n"))
    starter = full.replace(blank.strip("\n"), "____", 1)
    assert starter != full, f"java exam {title}: blank not found"
    return {
        "title": title,
        "prompt": prompt,
        "hint": hint,
        "language": "java",
        "starter": starter,
        "solution": full,
        "tests": [{"input": i, "output": o} for (i, o) in tests],
    }


JAVA_WEEKS = [
    # =======================================================================
    # MONTH 1 — Java foundations
    # =======================================================================
    _w(1, "Month 1 · Java foundations",
       "Reading Input & Variables",
       "Get data in, get answers out, and name values with the right type.",
       ["io_basics", "variables"],
       [("print-greeting", "The smallest possible read-and-print."),
        ("echo-line", "Whole-line input rather than a token."),
        ("add-two-numbers", "Two tokens, one arithmetic result."),
        ("rectangle-area", "Name the intermediate values.")],
       "Write a `Profile.java` that reads a name, an age and a city, then prints a three-line labelled summary — one variable per field, each explicitly typed.",
       [("Which Scanner call reads a whole line including spaces?",
         ["nextLine()", "next()", "nextString()", "readLine()"], 0,
         "`next()` stops at whitespace and returns one token. Mixing `nextInt()` with `nextLine()` also famously leaves the newline behind — read it off deliberately."),
        ("What is the difference between `int` and `Integer`?",
         ["int is a primitive; Integer is an object wrapper that can be null",
          "They are identical",
          "Integer is faster",
          "int can be null"], 0,
         "Collections can only hold objects, which is why `List<Integer>` exists — and why an unboxed null throws a NullPointerException."),
        ("What does `System.out.println(1 + 2 + \"x\")` print?",
         ["3x", "12x", "x3", "1 + 2x"], 0,
         "Evaluation is left to right: the two ints add first, then the result is concatenated. `\"x\" + 1 + 2` would give x12.")]),

    _w(2, "Month 1 · Java foundations",
       "Arithmetic & Booleans",
       "Integer division, remainder, and building conditions that read like the rule.",
       ["arithmetic", "boolean_logic"],
       [("even-or-odd", "Remainder as a predicate."),
        ("is-multiple", "The same idea, generalised."),
        ("larger-of-two", "A comparison feeding a decision."),
        ("leap-year", "A rule with nested exceptions — mind && over ||.")],
       "Write a `Change.java` that reads an amount in cents and prints how many quarters, dimes, nickels and pennies it takes, using only `/` and `%`.",
       [("What is `-7 / 2` in Java?",
         ["-3, because integer division truncates toward zero",
          "-4, rounding down",
          "-3.5",
          "3"], 0,
         "Java truncates toward zero, so -7/2 is -3 and -7%2 is -1. Languages that floor instead (like Python) give -4 and 1."),
        ("Why does `0.1 + 0.2 == 0.3` fail for doubles?",
         ["Binary floating point cannot represent those decimals exactly",
          "== compares references for doubles",
          "Java rounds to 15 digits",
          "It does not fail"], 0,
         "Compare with a tolerance, or use integers (cents) or BigDecimal when exactness matters."),
        ("What does short-circuit evaluation of `a && b` guarantee?",
         ["b is not evaluated when a is false",
          "Both sides always evaluate",
          "b evaluates first",
          "The result is cached"], 0,
         "This is what makes `if (arr != null && arr.length > 0)` safe. The non-short-circuiting `&` would evaluate both and throw.")]),

    _w(3, "Month 1 · Java foundations",
       "Conditionals & Loops",
       "Branch and repeat deliberately, with the right loop for the job.",
       ["conditionals", "loops_basic"],
       [("max-of-three", "Chained comparisons."),
        ("countdown", "Build output in a loop."),
        ("sum-to-n", "Accumulate a running total."),
        ("fizzbuzz-value", "Order the conditions correctly.")],
       "Write a `Triangle.java` that reads `n` and prints a right triangle of `*`, then the same triangle right-aligned — one nested loop each.",
       [("What is the difference between `while` and `do-while`?",
         ["do-while always runs the body at least once",
          "while can be broken out of; do-while cannot",
          "do-while is faster",
          "There is none"], 0,
         "`do-while` tests after the body, which is what you want for 'read, then decide whether to read again' loops."),
        ("What does `break` do inside nested loops?",
         ["Exits only the innermost loop, unless a label is used",
          "Exits every loop",
          "Exits the method",
          "Skips to the next iteration"], 0,
         "`continue` skips one iteration; a labelled break (`outer: for ...` then `break outer;`) is how you leave several levels at once."),
        ("Why does `for (int i = 0; i <= n; i++)` over an array of length n break?",
         ["The last index is n - 1, so i == n is out of bounds",
          "The loop never runs",
          "It skips the first element",
          "It is fine"], 0,
         "Off-by-one at the boundary is the most common array bug. The half-open convention `i < n` avoids it.")]),

    _w(4, "Month 1 · Java foundations",
       "Overflow & Bit Manipulation",
       "Know when an int is not big enough, and work with the bits directly.",
       ["overflow", "bit_manip"],
       [("factorial", "Growth that outruns int quickly."),
        ("number-of-1-bits", "Popcount."),
        ("power-of-two", "One bit trick, one line."),
        ("single-number", "XOR as a cancelling accumulator."),
        ("count-bits", "Popcount for a whole range.")],
       "Write a `Bits.java` that reads an int and prints its 32-bit binary form, its popcount, and the value with only its lowest set bit kept (`n & -n`).",
       [("`int a = 2_000_000_000; int b = a + a;` — what is b?",
         ["A negative number; the addition wrapped around",
          "4000000000",
          "Integer.MAX_VALUE",
          "It throws ArithmeticException"], 0,
         "Java's int arithmetic wraps silently. Widening one operand to long BEFORE the operation is the fix — casting the result afterwards is too late."),
        ("What does `n & (n - 1)` do?",
         ["Clears the lowest set bit",
          "Sets the lowest bit",
          "Halves n",
          "Flips every bit"], 0,
         "Which is why `n > 0 && (n & (n - 1)) == 0` tests for a power of two, and why repeating it counts set bits."),
        ("What is the difference between `>>` and `>>>`?",
         [">> keeps the sign bit; >>> shifts in zeros",
          ">>> is left shift",
          "They are identical for ints",
          ">> is unsigned"], 0,
         "For negative numbers `>>` preserves the sign while `>>>` does not — which is why `>>>` is used for the midpoint trick and hash mixing.")]),

    # =======================================================================
    # MONTH 2 — Numbers, arrays, strings
    # =======================================================================
    _w(5, "Month 2 · Numbers, arrays & strings",
       "Digits, Number Theory & Modular Arithmetic",
       "Take numbers apart, factor them, and keep results inside a modulus.",
       ["math_digits", "number_theory", "modulo"],
       [("count-digits", "Peel with / and %."),
        ("sum-of-digits", "Accumulate while peeling."),
        ("reverse-integer", "Rebuild in the other direction."),
        ("palindrome-number", "Compare without converting to a String."),
        ("gcd", "Euclid's algorithm."),
        ("is-prime", "Stop at the square root.")],
       "Write a `Modpow.java` computing `base^exp mod m` by squaring, and check it against a slow loop for small inputs.",
       [("Why does trial division stop at `d * d <= n`?",
         ["Any factor above the square root pairs with one below it",
          "Larger divisors cannot exist",
          "It is an approximation",
          "To avoid overflow"], 0,
         "Factors come in pairs around the square root, so finding none below it proves there are none at all."),
        ("Why compute LCM as `a / gcd * b` rather than `a * b / gcd`?",
         ["Dividing first keeps the intermediate value from overflowing",
          "It is faster",
          "a * b / gcd is wrong",
          "gcd may be zero"], 0,
         "Both are mathematically equal, but `a * b` can overflow long before the division brings it back down."),
        ("Why take the modulus at every step of modular exponentiation?",
         ["It keeps every intermediate product inside the range of a long",
          "It makes the result correct, which it otherwise would not be",
          "It is faster to compute",
          "It is only needed at the end"], 0,
         "The maths works either way; the reduction is what stops the intermediate values overflowing.")]),

    _w(6, "Month 2 · Numbers, arrays & strings",
       "Array Iteration & Patterns",
       "Scan an array once and answer several questions at the same time.",
       ["iteration", "array_patterns"],
       [("array-sum", "The basic accumulator."),
        ("array-maximum", "Seed correctly for negatives."),
        ("second-largest", "Track two values in one pass."),
        ("count-evens", "A predicate count."),
        ("running-sum", "Carry state across iterations.")],
       "Write a `Stats.java` that reads `n` then `n` numbers and prints min, max, sum, mean (2 decimals) and how many are above the mean — using no more than two passes.",
       [("Why seed a running maximum with `a[0]` rather than 0?",
         ["An all-negative array would otherwise report 0",
          "0 is slower",
          "a[0] is always the largest",
          "It avoids an off-by-one"], 0,
         "Seeding with a real element (or Integer.MIN_VALUE) is what makes the scan correct for every input, not just non-negative ones."),
        ("What does `int[] b = a;` do?",
         ["Copies the reference — both names see the same array",
          "Copies the contents",
          "Creates an empty array of the same length",
          "Is a compile error"], 0,
         "Arrays are objects. `Arrays.copyOf` or `clone()` is what actually duplicates the contents."),
        ("What is `arr.length` versus `s.length()`?",
         ["Arrays expose a length FIELD; String exposes a length() METHOD",
          "Both are methods",
          "Both are fields",
          "length() only works on char arrays"], 0,
         "A small inconsistency in the language, and one of the most common compile errors when moving between the two.")]),

    _w(7, "Month 2 · Numbers, arrays & strings",
       "Strings & Char Arrays",
       "Traverse text efficiently, and know when to drop to a char array.",
       ["string_basics", "char_arrays"],
       [("reverse-string", "Two pointers or a StringBuilder."),
        ("count-vowels", "A membership test per character."),
        ("count-words", "Splitting and its edge cases."),
        ("caesar-cipher", "Character arithmetic with wrap-around."),
        ("first-unique-char", "Two passes with a frequency table.")],
       "Write a `Words.java` that reads a line and prints the word count, the longest word, and the line with every word reversed in place.",
       [("Why is building a string with `s += c` in a loop slow?",
         ["Strings are immutable, so each += allocates and copies a new string",
          "The compiler cannot optimise +=",
          "It is not slow",
          "Because of Unicode handling"], 0,
         "That makes the loop O(n²). `StringBuilder` appends into a growable buffer and is the standard fix."),
        ("What does `s.charAt(i) - 'a'` give you?",
         ["The 0-based position of the letter in the alphabet",
          "The ASCII code of s.charAt(i)",
          "A String of length 1",
          "A compile error"], 0,
         "chars are integers, so subtracting 'a' maps 'a'..'z' onto 0..25 — the index into a 26-element counting array."),
        ("Why compare strings with `.equals()` rather than `==`?",
         ["== compares references, which differ for equal strings built at runtime",
          "equals is faster",
          "== does not compile for strings",
          "They are interchangeable"], 0,
         "Literals are interned so `==` often appears to work, which makes the bug show up only once the string comes from input.")]),

    _w(8, "Month 2 · Numbers, arrays & strings",
       "Canonical Forms & Simulation",
       "Give equivalent things one representation, and just follow the rules.",
       ["canonical", "simulation"],
       [("valid-anagram", "Sorting as a canonical key."),
        ("group-anagrams-count", "Grouping by that key."),
        ("robot-grid-walk", "Follow the instructions exactly."),
        ("minesweeper-counts", "Neighbour counting in a grid."),
        ("rotate-matrix-90", "Index arithmetic done carefully.")],
       "Write a `Life.java` that reads a grid and prints the next Game of Life generation — a pure simulation with careful boundary handling.",
       [("What makes a good canonical form?",
         ["Equivalent inputs map to the same key, and different ones do not",
          "It is always shorter than the input",
          "It is reversible",
          "It is always a sorted string"], 0,
         "Sorted characters work for anagrams; a 26-length count vector is the O(n) alternative with the same property."),
        ("Why copy the grid before applying Game of Life rules?",
         ["Every cell's next state depends on the CURRENT generation",
          "The original is readonly",
          "To avoid an out-of-bounds error",
          "Copying is not necessary"], 0,
         "Updating in place lets already-updated neighbours feed into later cells, which silently computes the wrong generation."),
        ("What is the usual way to visit a cell's four neighbours?",
         ["Two offset arrays, dr = {1,-1,0,0} and dc = {0,0,1,-1}, in one loop",
          "Four separate if blocks, which is the only correct way",
          "A nested loop over the whole grid",
          "Recursion"], 0,
         "The direction-array idiom keeps the bounds check in one place; the eight-neighbour version just extends the arrays.")]),

    # =======================================================================
    # MONTH 3 — Scanning patterns
    # =======================================================================
    _w(9, "Month 3 · Scanning patterns",
       "Two Pointers & In-place Work",
       "Walk a sorted array from both ends, and rearrange without extra space.",
       ["two_pointers", "inplace_reverse"],
       [("two-sum-sorted", "The canonical converging walk."),
        ("move-zeroes", "A write pointer trailing a read pointer."),
        ("reverse-array-fn", "Swap toward the middle."),
        ("container-most-water", "Move the limiting side."),
        ("is-palindrome-fn", "Converge and compare.")],
       "Write a `Dutch.java` sorting an array of 0s, 1s and 2s in one pass with three pointers — no sorting library call.",
       [("Why does the two-pointer sum walk require a SORTED array?",
         ["Sortedness is what makes 'too small' imply moving the low pointer",
          "It does not; it works on any array",
          "Sorting removes duplicates",
          "To allow binary search inside the loop"], 0,
         "Without order, a smaller sum tells you nothing about which side to move, and the O(n) argument collapses."),
        ("What does the write-pointer idiom achieve in move-zeroes?",
         ["Compaction in place: the write index only advances on a kept element",
          "It sorts the array",
          "It reverses the array",
          "It counts the zeroes"], 0,
         "Read every element, write only the ones you keep, then fill the tail — the standard in-place filter."),
        ("Rotating by reversal: reverse first k, reverse the rest, reverse the whole. Why does it work?",
         ["Each reversal puts a block in place while reversing it; the final one undoes that",
          "It is a coincidence of index arithmetic",
          "It only works when k divides n",
          "It requires extra space"], 0,
         "Three linear reversals give an O(n) time, O(1) space rotation — much simpler than juggling with cycle following.")]),

    _w(10, "Month 3 · Scanning patterns",
        "Sliding Window",
        "Maintain a window instead of recomputing every subarray.",
        ["sliding_window"],
        [("max-consecutive-ones", "The simplest window."),
         ("longest-unique-substring", "A window with a set."),
         ("min-window-length", "A window with counts."),
         ("best-time-buy-sell", "A running minimum, which is the degenerate case.")],
        "Write a `Window.java` that reads `n k` and `n` numbers and prints the maximum, minimum and average of every window of size k — one pass.",
        [("What is the difference between a fixed and a variable window?",
          ["A fixed window always moves both ends together; a variable one grows until a condition breaks, then shrinks",
           "A variable window can move backwards",
           "A fixed window needs sorting",
           "There is none"], 0,
          "The variable form is the one that solves 'longest substring with property P' — grow greedily, shrink only while the property is violated."),
         ("Why is the sliding-window sum O(n) rather than O(n·k)?",
          ["Each step adds the entering element and subtracts the leaving one",
           "Because k is small",
           "Because the array is sorted",
           "It is O(n·k)"], 0,
          "Reusing the previous window's answer is the whole trick — the same idea as a prefix sum, computed incrementally."),
         ("A window over an array with negative numbers — which pattern breaks?",
          ["Variable-size windows that assume growing the window grows the sum",
           "Fixed-size windows",
           "Both break",
           "Neither breaks"], 0,
          "Monotonicity is the hidden precondition of the shrink step. With negatives you usually need prefix sums plus a map instead.")]),

    _w(11, "Month 3 · Scanning patterns",
        "Prefix Sums & Running Maxima",
        "Precompute once so every range query is constant time.",
        ["prefix_sum", "prefix_max"],
        [("running-sum", "Building the prefix array."),
         ("product-except-self", "Prefix and suffix passes."),
         ("subarray-sum-k", "Prefix sums plus a hash map."),
         ("count-above-average", "Two passes over one aggregate.")],
        "Write a `Ranges.java` that reads an array and `q` queries and answers each `l r` range sum in O(1) after an O(n) build.",
        [("Given `pre[i+1] = pre[i] + a[i]`, what is the sum of `a[l..r]`?",
          ["pre[r+1] - pre[l]", "pre[r] - pre[l]",
           "pre[r] - pre[l-1]", "pre[r+1] - pre[l+1]"], 0,
          "The off-by-one is exactly why the prefix array is given an extra leading zero — it makes l = 0 work without a special case."),
         ("Why does subarray-sum-k need a hash map of prefix sums?",
          ["A subarray sums to k exactly when two prefix sums differ by k",
           "To deduplicate the array",
           "To sort the prefix sums",
           "It does not need one"], 0,
          "Counting earlier prefixes equal to `current - k` turns an O(n²) scan into one pass."),
         ("What does a difference array give you?",
          ["O(1) range UPDATES, with one final pass to materialise the values",
           "O(1) range queries",
           "A sorted array",
           "The maximum of a range"], 0,
          "It is the dual of a prefix sum: prefix sums make queries cheap, difference arrays make updates cheap.")]),

    _w(12, "Month 3 · Scanning patterns",
        "Hashing, Complements & Visited Sets",
        "Trade memory for time — the single most reusable idea in the syllabus.",
        ["hashing", "complement", "visited_set"],
        [("contains-duplicate", "A set, one pass."),
         ("two-sum-indices", "Complement lookup."),
         ("majority-element", "Counting in a map."),
         ("longest-consecutive", "A set turns a sort into a scan."),
         ("count-occurrences", "The basic frequency table.")],
        "Write an `Index.java` that reads lines of `word document` and answers lookup queries from an inverted index built in one pass.",
        [("Why is `map.getOrDefault(k, 0) + 1` preferred over a containsKey check?",
          ["It is one lookup and one branch fewer, with the same behaviour",
           "containsKey does not work for Integer keys",
           "It handles null values differently",
           "It is required for HashMap"], 0,
          "`merge(k, 1, Integer::sum)` is the same idea. Both avoid the double lookup of checking then getting."),
         ("What must a key type get right to work in a HashMap?",
          ["equals and hashCode must agree — equal objects must hash the same",
           "It must implement Comparable",
           "It must be immutable",
           "It must override toString"], 0,
          "Immutability matters too (mutating a key after insertion loses it), but the equals/hashCode contract is the hard requirement."),
         ("What does the complement pattern replace?",
          ["The inner loop of a nested search, by asking 'have I already seen what I need?'",
           "Sorting",
           "Recursion",
           "The need for a hash map"], 0,
          "It converts 'find a pair' from O(n²) to O(n) by storing what has been seen instead of re-scanning it.")]),

    _w(13, "Month 3 · Scanning patterns",
        "Checkpoint — Consolidation",
        "No new concepts. Re-solve across everything so far and prove it stuck.",
        [],
        [("two-sum-indices", "Hashing — Week 12."),
         ("longest-unique-substring", "Sliding window plus a set — Weeks 10, 12."),
         ("product-except-self", "Prefix and suffix — Week 11."),
         ("group-anagrams-count", "Canonical keys — Week 8."),
         ("move-zeroes", "In-place two pointers — Week 9.")],
        "Re-implement your Week 6 `Stats.java` from scratch without looking at it, then diff the two and justify every difference.",
        [("You need the k largest of a huge stream. Which shape fits best?",
          ["A size-k min-heap, so memory stays O(k)",
           "Sorting the whole stream",
           "A hash map of counts",
           "Two pointers"], 0,
          "Sorting needs the whole stream in memory and does more work than asked. The heap keeps only the current top k."),
         ("A problem says 'contiguous subarray'. Which two techniques should come to mind first?",
          ["Sliding window and prefix sums",
           "Binary search and sorting",
           "DFS and BFS",
           "Union-find and topological sort"], 0,
          "Contiguity is the signal. Once the problem says 'subsequence' instead, you are usually in dynamic-programming territory."),
         ("What does `Arrays.sort` use for an `int[]`?",
          ["A dual-pivot quicksort, which is not stable",
           "Merge sort, which is stable",
           "Heap sort",
           "Counting sort"], 0,
          "Primitives get quicksort (no stability concern since values are indistinguishable); object arrays get a stable TimSort.")]),
]


JAVA_EXAMS = {
    1: _java_exam(
        "Profile card",
        "The input is a name, an age and a city on one line. Print three labelled lines — `Name: ada`, `Age: 36`, `City: london` — then a fourth line with the age in dog years (age times 7).",
        """
        String name = sc.next();
        int age = sc.nextInt();
        String city = sc.next();
        System.out.println("Name: " + name);
        System.out.println("Age: " + age);
        System.out.println("City: " + city);
        System.out.println(age * 7);
        """,
        [("ada 36 london", "Name: ada\nAge: 36\nCity: london\n252"),
         ("bob 10 paris", "Name: bob\nAge: 10\nCity: paris\n70"),
         ("z 0 x", "Name: z\nAge: 0\nCity: x\n0")],
        hint="Read the three tokens in order with next()/nextInt()/next(), then build each line with string concatenation."),

    2: _java_exam(
        "Coin breakdown",
        "The input is an amount in cents. Print how many quarters (25), dimes (10), nickels (5) and pennies (1) it takes, one per line, taking as many of each as possible in that order.",
        """
        int cents = sc.nextInt();
        int quarters = cents / 25;
        cents %= 25;
        int dimes = cents / 10;
        cents %= 10;
        int nickels = cents / 5;
        cents %= 5;
        System.out.println(quarters);
        System.out.println(dimes);
        System.out.println(nickels);
        System.out.println(cents);
        """,
        [("87", "3\n1\n0\n2"), ("0", "0\n0\n0\n0"),
         ("100", "4\n0\n0\n0"), ("99", "3\n2\n0\n4")],
        hint="Divide to take the coins, then use % to keep only what is left before moving to the next denomination."),

    3: _java_exam(
        "Right triangle",
        "The input is one integer `n`. Print a left-aligned triangle of `*` with rows 1..n, then a blank line, then the same triangle right-aligned in a field of width `n` (padded with spaces).",
        """
        int n = sc.nextInt();
        for (int i = 1; i <= n; i++) {
            StringBuilder row = new StringBuilder();
            for (int j = 0; j < i; j++) row.append('*');
            System.out.println(row.toString());
        }
        System.out.println();
        for (int i = 1; i <= n; i++) {
            StringBuilder row = new StringBuilder();
            for (int j = 0; j < n - i; j++) row.append(' ');
            for (int j = 0; j < i; j++) row.append('*');
            System.out.println(row.toString());
        }
        """,
        [("3", "*\n**\n***\n\n  *\n **\n***"),
         ("1", "*\n\n*"),
         ("4", "*\n**\n***\n****\n\n   *\n  **\n ***\n****")],
        hint="Two nested loops per triangle: the inner one writes the padding, then the stars. Trailing spaces are trimmed by the judge, leading ones are not."),

    4: _java_exam(
        "Bit report",
        "The input is one non-negative int. Print its 32-bit binary form with leading zeros, its popcount, the value with only the lowest set bit kept (`n & -n`), and whether it is a power of two.",
        """
        int n = sc.nextInt();
        StringBuilder bits = new StringBuilder();
        for (int i = 31; i >= 0; i--) bits.append((n >> i) & 1);
        int count = 0;
        int rest = n;
        while (rest != 0) {
            rest &= rest - 1;
            count++;
        }
        System.out.println(bits.toString());
        System.out.println(count);
        System.out.println(n & -n);
        System.out.println(n > 0 && (n & (n - 1)) == 0);
        """,
        [("12", "00000000000000000000000000001100\n2\n4\nfalse"),
         ("16", "00000000000000000000000000010000\n1\n16\ntrue"),
         ("0", "00000000000000000000000000000000\n0\n0\nfalse"),
         ("7", "00000000000000000000000000000111\n3\n1\nfalse")],
        hint="Walk bits from 31 down to 0 for the binary string; `rest &= rest - 1` clears one set bit per pass, which counts them."),

    5: _java_exam(
        "Modular power",
        "The input is `base exp mod`. Print `base^exp mod m` computed by squaring, then the greatest common divisor of `base` and `mod`, then whether `base` is prime.",
        """
        long base = sc.nextLong();
        long exp = sc.nextLong();
        long mod = sc.nextLong();
        long result = 1 % mod;
        long b = base % mod;
        long e = exp;
        while (e > 0) {
            if ((e & 1) == 1) result = result * b % mod;
            b = b * b % mod;
            e >>= 1;
        }
        System.out.println(result);
        long x = base;
        long y = mod;
        while (y != 0) {
            long t = x % y;
            x = y;
            y = t;
        }
        System.out.println(x);
        boolean prime = base >= 2;
        for (long d = 2; d * d <= base; d++) {
            if (base % d == 0) {
                prime = false;
                break;
            }
        }
        System.out.println(prime);
        """,
        [("2 10 1000", "24\n2\ntrue"), ("3 0 7", "1\n1\ntrue"),
         ("12 3 100", "28\n4\nfalse"), ("5 3 13", "8\n1\ntrue")],
        hint="Reduce mod at every multiplication. Keep the gcd loop separate from the exponentiation so neither clobbers the other's variables."),

    6: _java_exam(
        "Array statistics",
        "The input is `n` then `n` integers. Print the minimum, the maximum, the sum, the mean to exactly two decimals, and how many values are strictly above the mean.",
        """
        int n = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        int min = a[0];
        int max = a[0];
        long sum = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] < min) min = a[i];
            if (a[i] > max) max = a[i];
            sum += a[i];
        }
        double mean = (double) sum / n;
        int above = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] > mean) above++;
        }
        System.out.println(min);
        System.out.println(max);
        System.out.println(sum);
        System.out.printf("%.2f%n", mean);
        System.out.println(above);
        """,
        [("4\n1 2 3 4", "1\n4\n10\n2.50\n2"),
         ("1\n7", "7\n7\n7\n7.00\n0"),
         ("3\n-5 -1 -3", "-5\n-1\n-9\n-3.00\n1"),
         ("5\n2 2 2 2 2", "2\n2\n10\n2.00\n0")],
        hint="Seed min and max with a[0]. Cast to double BEFORE dividing, or integer division truncates the mean."),

    7: _java_exam(
        "Word report",
        "The input is one line of lowercase words. Print the word count, the longest word (first on a tie), the line with each word reversed in place, and the number of vowels in the whole line.",
        """
        String line = sc.nextLine();
        String[] words = line.split(" ");
        String longest = words[0];
        StringBuilder out = new StringBuilder();
        int vowels = 0;
        for (int i = 0; i < words.length; i++) {
            if (words[i].length() > longest.length()) longest = words[i];
            if (i > 0) out.append(' ');
            out.append(new StringBuilder(words[i]).reverse());
        }
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') vowels++;
        }
        System.out.println(words.length);
        System.out.println(longest);
        System.out.println(out.toString());
        System.out.println(vowels);
        """,
        [("the quick brown fox", "4\nquick\neht kciuq nworb xof\n5"),
         ("hello", "1\nhello\nolleh\n2"),
         ("a bb ccc", "3\nccc\na bb ccc\n1")],
        hint="StringBuilder.reverse() gives you each reversed word; count the vowels over the original line, spaces and all."),

    8: _java_exam(
        "Game of Life step",
        "The input is `r c` then an `r` x `c` grid of 0/1. Print the next generation: a live cell with 2 or 3 live neighbours survives, a dead cell with exactly 3 becomes alive, everything else dies. Rows are space-separated values.",
        """
        int r = sc.nextInt();
        int c = sc.nextInt();
        int[][] g = new int[r][c];
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) g[i][j] = sc.nextInt();
        }
        int[][] next = new int[r][c];
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                int live = 0;
                for (int di = -1; di <= 1; di++) {
                    for (int dj = -1; dj <= 1; dj++) {
                        if (di == 0 && dj == 0) continue;
                        int ni = i + di;
                        int nj = j + dj;
                        if (ni < 0 || ni >= r || nj < 0 || nj >= c) continue;
                        live += g[ni][nj];
                    }
                }
                if (g[i][j] == 1) next[i][j] = (live == 2 || live == 3) ? 1 : 0;
                else next[i][j] = live == 3 ? 1 : 0;
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                if (j > 0) sb.append(' ');
                sb.append(next[i][j]);
            }
            sb.append('\\n');
        }
        System.out.print(sb.toString());
        """,
        [("3 3\n0 1 0\n0 1 0\n0 1 0", "0 0 0\n1 1 1\n0 0 0"),
         ("2 2\n1 1\n1 1", "1 1\n1 1"),
         ("3 3\n0 0 0\n0 0 0\n0 0 0", "0 0 0\n0 0 0\n0 0 0"),
         ("1 3\n1 1 1", "0 1 0")],
        hint="Write into a SECOND grid — updating in place lets already-updated neighbours corrupt the count for later cells."),

    9: _java_exam(
        "Dutch national flag",
        "The input is `n` then `n` values, each 0, 1 or 2. Sort them in ONE pass with three pointers (no library sort) and print the result space-separated, then the count of each value as `zeros ones twos`.",
        """
        int n = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        int low = 0;
        int mid = 0;
        int high = n - 1;
        while (mid <= high) {
            if (a[mid] == 0) {
                int t = a[low];
                a[low] = a[mid];
                a[mid] = t;
                low++;
                mid++;
            } else if (a[mid] == 2) {
                int t = a[high];
                a[high] = a[mid];
                a[mid] = t;
                high--;
            } else {
                mid++;
            }
        }
        StringBuilder sb = new StringBuilder();
        int[] counts = new int[3];
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(a[i]);
            counts[a[i]]++;
        }
        System.out.println(sb.toString());
        System.out.println(counts[0] + " " + counts[1] + " " + counts[2]);
        """,
        [("6\n2 0 1 2 1 0", "0 0 1 1 2 2\n2 2 2"),
         ("1\n1", "1\n0 1 0"),
         ("4\n2 2 2 2", "2 2 2 2\n0 0 4"),
         ("5\n0 1 2 0 1", "0 0 1 1 2\n2 2 1")],
        hint="Only advance mid when you swap a 0 forward or see a 1 — after swapping a 2 back, the newly arrived value has not been examined yet."),

    10: _java_exam(
        "Window report",
        "The input is `n k` then `n` integers. For every window of `k` consecutive values print `max min sum` on its own line, then the largest window sum on the final line.",
        """
        int n = sc.nextInt();
        int k = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        StringBuilder sb = new StringBuilder();
        long best = Long.MIN_VALUE;
        for (int start = 0; start + k <= n; start++) {
            int max = a[start];
            int min = a[start];
            long sum = 0;
            for (int i = start; i < start + k; i++) {
                if (a[i] > max) max = a[i];
                if (a[i] < min) min = a[i];
                sum += a[i];
            }
            sb.append(max).append(' ').append(min).append(' ').append(sum).append('\\n');
            if (sum > best) best = sum;
        }
        System.out.print(sb.toString());
        System.out.println(best);
        """,
        [("5 3\n1 2 3 4 5", "3 1 6\n4 2 9\n5 3 12\n12"),
         ("3 3\n7 7 7", "7 7 21\n21"),
         ("4 2\n-1 -2 -3 -4", "-1 -2 -3\n-2 -3 -5\n-3 -4 -7\n-3"),
         ("1 1\n9", "9 9 9\n9")],
        hint="Seed best with Long.MIN_VALUE so an all-negative array reports the real maximum rather than 0."),

    11: _java_exam(
        "Range sum queries",
        "The input is `n q`, then `n` integers, then `q` lines of `l r` (0-indexed, inclusive). Build a prefix-sum array once and answer each query in O(1), one per line. Finish with the largest answer.",
        """
        int n = sc.nextInt();
        int q = sc.nextInt();
        long[] pre = new long[n + 1];
        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + sc.nextInt();
        StringBuilder sb = new StringBuilder();
        long best = Long.MIN_VALUE;
        for (int i = 0; i < q; i++) {
            int l = sc.nextInt();
            int r = sc.nextInt();
            long sum = pre[r + 1] - pre[l];
            sb.append(sum).append('\\n');
            if (sum > best) best = sum;
        }
        System.out.print(sb.toString());
        System.out.println(best);
        """,
        [("5 3\n1 2 3 4 5\n0 4\n1 3\n2 2", "15\n9\n3\n15"),
         ("4 2\n-1 -2 -3 -4\n0 1\n2 3", "-3\n-7\n-3"),
         ("1 1\n42\n0 0", "42\n42"),
         ("6 2\n1 1 1 1 1 1\n0 5\n3 4", "6\n2\n6")],
        hint="The extra leading zero in the prefix array is what lets l = 0 work with no special case."),

    12: _java_exam(
        "Inverted index",
        "The input is `n` then `n` lines of `document word word ...`, then a final line of query words. For each query print `word: doc1 doc2` with the documents in first-appearance order, or `word: -` when the word was never seen.",
        """
        int n = sc.nextInt();
        sc.nextLine();
        LinkedHashMap<String, List<String>> index = new LinkedHashMap<>();
        for (int i = 0; i < n; i++) {
            String[] parts = sc.nextLine().trim().split("\\\\s+");
            String doc = parts[0];
            for (int j = 1; j < parts.length; j++) {
                List<String> docs = index.computeIfAbsent(parts[j], k -> new ArrayList<>());
                if (!docs.contains(doc)) docs.add(doc);
            }
        }
        StringBuilder sb = new StringBuilder();
        for (String query : sc.nextLine().trim().split("\\\\s+")) {
            List<String> docs = index.get(query);
            sb.append(query).append(": ");
            if (docs == null) sb.append('-');
            else sb.append(String.join(" ", docs));
            sb.append('\\n');
        }
        System.out.print(sb.toString());
        """,
        [("2\nd1 cat dog\nd2 dog bird\ndog cat fish", "dog: d1 d2\ncat: d1\nfish: -"),
         ("1\na x\nx", "x: a"),
         ("2\nd1 k\nd2 k\nk", "k: d1 d2")],
        hint="Call sc.nextLine() once after nextInt() to consume the rest of that line, or the first readLine comes back empty."),

    13: _java_exam(
        "Checkpoint: word frequency report",
        "The input is a line of words. Print the three most frequent as `word=count`, one per line, ties broken alphabetically, then the number of distinct words and the total word count separated by a space.",
        """
        String[] words = sc.nextLine().trim().split("\\\\s+");
        HashMap<String, Integer> counts = new HashMap<>();
        for (String w : words) counts.merge(w, 1, Integer::sum);
        List<Map.Entry<String, Integer>> ranked = new ArrayList<>(counts.entrySet());
        ranked.sort((a, b) -> b.getValue().equals(a.getValue())
                ? a.getKey().compareTo(b.getKey())
                : b.getValue() - a.getValue());
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < Math.min(3, ranked.size()); i++) {
            sb.append(ranked.get(i).getKey()).append('=').append(ranked.get(i).getValue()).append('\\n');
        }
        System.out.print(sb.toString());
        System.out.println(counts.size() + " " + words.length);
        """,
        [("a b a c b a", "a=3\nb=2\nc=1\n3 6"),
         ("solo", "solo=1\n1 1"),
         ("x y", "x=1\ny=1\n2 2"),
         ("z z y y x", "y=2\nz=2\nx=1\n3 5")],
        hint="merge(w, 1, Integer::sum) is the compact counting idiom; sort the entry list by count descending with an alphabetical tie-break."),
}




JAVA_WEEKS += [
    # =======================================================================
    # MONTH 4 — Data structures
    # =======================================================================
    _w(14, "Month 4 · Data structures",
       "Stacks",
       "Use LIFO order to match, undo, and find the next greater thing.",
       ["stack"],
       [("valid-parentheses", "The canonical matching problem."),
        ("min-stack", "An auxiliary stack carrying an invariant."),
        ("next-greater-element", "The monotonic stack."),
        ("daily-temperatures", "The same pattern over distances.")],
       "Write a `Rpn.java` evaluating a reverse-Polish expression from stdin, reporting `error` on a malformed one rather than crashing.",
       [("Which Java type should you use as a stack?",
         ["ArrayDeque, via push/pop/peek",
          "java.util.Stack",
          "LinkedList only",
          "ArrayList with remove(0)"], 0,
         "`Stack` extends Vector and is synchronised legacy code; `ArrayDeque` is the modern, faster choice — and `remove(0)` on an ArrayList is O(n)."),
        ("What makes a stack monotonic?",
         ["You pop before pushing so the contents stay sorted in one direction",
          "It stores only distinct values",
          "It is backed by a sorted array",
          "It never pops"], 0,
         "Popping everything the new element dominates is what makes 'next greater element' linear overall — each element is pushed and popped at most once."),
        ("Why does min-stack need a second stack rather than a single min variable?",
         ["Popping the current minimum has to restore the previous one",
          "For thread safety",
          "To keep push O(1)",
          "It does not"], 0,
         "A lone variable cannot recover the old minimum after a pop. Storing the running minimum alongside each element keeps every operation O(1).")]),

    _w(15, "Month 4 · Data structures",
       "Queues & Designed Structures",
       "FIFO order, and building a data structure to a stated interface.",
       ["queue", "design_ds"],
       [("implement-queue-stacks", "One structure built from another."),
        ("implement-stack-queues", "The mirror image."),
        ("design-circular-queue", "Fixed capacity with wrap-around indices."),
        ("lru-cache", "Two structures kept in step."),
        ("design-hashmap", "Buckets from scratch.")],
       "Write a `RingBuffer.java` with a fixed capacity that overwrites the oldest entry when full, plus a `toString` listing contents oldest-first.",
       [("Why is `ArrayList.remove(0)` a poor queue dequeue?",
         ["It shifts every remaining element, making it O(n)",
          "It throws on an empty list",
          "It returns the wrong element",
          "It is fine"], 0,
         "`ArrayDeque.pollFirst()` is O(1). Using a list as a queue is a classic accidental O(n²)."),
        ("What does LRU need in order to be O(1) for both get and put?",
         ["A hash map for lookup plus a doubly-linked list for recency order",
          "A single TreeMap",
          "A priority queue keyed by timestamp",
          "An ArrayList of keys"], 0,
         "The map finds the node; the linked list moves it to the front without a scan. `LinkedHashMap` with access order bundles both."),
        ("In a circular queue, how do you distinguish full from empty?",
         ["Keep an explicit size (or leave one slot unused)",
          "Compare head and tail only",
          "Check for null entries",
          "It cannot be distinguished"], 0,
         "head == tail is ambiguous on its own — it holds for both states, which is why a size counter is the usual fix.")]),

    _w(16, "Month 4 · Data structures",
       "Heaps & Priority Queues",
       "Always know the current extreme — including with two heaps at once.",
       ["heap", "top_k", "two_heaps", "heap_greedy"],
       [("kth-largest-element", "A size-k heap."),
        ("top-k-frequent", "Counting, then a heap."),
        ("last-stone-weight", "Repeated extremes."),
        ("median-from-stream", "Two heaps kept balanced."),
        ("min-meeting-rooms", "Greedy with the earliest-finishing room.")],
       "Write a `Huffman.java` that reads weights, repeatedly merges the two smallest, and prints the total merge cost plus the number of merges.",
       [("What order does Java's `PriorityQueue` use by default?",
         ["Natural order — it is a MIN-heap",
          "Reverse order — a max-heap",
          "Insertion order",
          "Undefined"], 0,
         "`new PriorityQueue<>(Collections.reverseOrder())` gives a max-heap. Getting this backwards is the single most common heap bug."),
        ("To keep the k LARGEST elements, which heap do you maintain?",
         ["A min-heap of size k, polling whenever it grows past k",
          "A max-heap of size k",
          "A min-heap of size n",
          "A max-heap of size n"], 0,
         "The min-heap's root is the weakest survivor, so it is exactly the one to evict — O(n log k) instead of O(n log n)."),
        ("Does iterating a `PriorityQueue` give sorted order?",
         ["No — only poll() respects the ordering",
          "Yes, always",
          "Yes, but only for primitives",
          "Only after calling sort()"], 0,
         "The backing array is heap-ordered, not sorted. Printing a PriorityQueue directly is a routine source of confusing output.")]),

    _w(17, "Month 4 · Data structures",
       "Tries",
       "Share prefixes so lookup costs the length of the word, not the size of the dictionary.",
       ["trie"],
       [("implement-trie-ops", "Insert, search, startsWith."),
        ("longest-common-prefix-strs", "The degenerate one-path case."),
        ("replace-words-roots", "Walk until a root matches."),
        ("longest-buildable-word", "Only words whose prefixes are all present."),
        ("word-dictionary-wildcard", "Branching search over the trie.")],
       "Write an `Autocomplete.java` that loads a dictionary, then for each query prints the first five completions in alphabetical order.",
       [("What does a trie cost to look up a word of length L?",
         ["O(L), independent of how many words are stored",
          "O(log n) in the dictionary size",
          "O(n) in the dictionary size",
          "O(L log n)"], 0,
         "That independence from dictionary size is the whole point, and why tries beat hash sets for prefix queries."),
        ("Why does a trie node need an `isWord` flag?",
         ["To distinguish a stored word from a mere prefix of longer words",
          "To mark the root",
          "To count children",
          "To support deletion only"], 0,
         "Without it, storing \"cars\" would make \"car\" appear to be in the dictionary."),
        ("What is the main cost of a trie over a hash set?",
         ["Memory — a node per character, each with child pointers",
          "Slower exact lookup",
          "It cannot store duplicates",
          "It requires sorted input"], 0,
         "A 26-way array per node is fast but wasteful; a HashMap per node trades some speed for much less memory on sparse dictionaries.")]),

    _w(18, "Month 4 · Data structures",
       "Linked Lists",
       "Pointer surgery: reverse, find the middle, detect a cycle.",
       ["list_basics", "list_reversal", "fast_slow"],
       [("list-length", "Walk to the end."),
        ("reverse-linked-list", "The three-pointer walk."),
        ("middle-of-list", "Fast and slow in one pass."),
        ("has-cycle", "Floyd's algorithm."),
        ("merge-two-sorted-lists", "Two cursors and a dummy head."),
        ("remove-nth-from-end", "A gap between two pointers.")],
       "Write a `Palindrome.java` that decides whether a linked list reads the same forwards and backwards in O(n) time and O(1) extra space.",
       [("In `reverse`, why must you save `curr.next` before reassigning it?",
         ["Overwriting it first loses the rest of the list",
          "To keep the list sorted",
          "For the null check",
          "You do not have to"], 0,
         "The saved `next` is the only remaining handle on the untouched tail. When curr falls off the end, prev is the new head."),
        ("Why does a dummy head node simplify list building?",
         ["It removes the special case for inserting the very first node",
          "It makes the list circular",
          "It stores the length",
          "It speeds up traversal"], 0,
         "You always append after a real node, then return `dummy.next` — no branch for the empty case."),
        ("Why do fast and slow pointers meet inside a cycle?",
         ["The gap closes by one each step, so the faster one must catch up",
          "They start at the same node",
          "The cycle length is always even",
          "They do not always meet"], 0,
         "Once both are inside the loop the distance shrinks by exactly one per step, so a meeting is guaranteed.")]),

    # =======================================================================
    # MONTH 5 — Trees, sorting & search
    # =======================================================================
    _w(19, "Month 5 · Trees, sorting & search",
        "Binary Trees & Traversals",
        "Recurse over structure, and know what each traversal order gives you.",
        ["tree_basics", "tree_traversal"],
        [("max-depth-tree", "The simplest recursion on a tree."),
         ("count-nodes-tree", "Aggregate over both subtrees."),
         ("inorder-traversal", "Left, node, right."),
         ("level-order-traversal", "BFS with a queue."),
         ("invert-binary-tree", "Structural mutation."),
         ("symmetric-tree", "Two cursors descending in mirror.")],
        "Write a `Serialize.java` that prints a tree in preorder with `#` for null, then rebuilds it from that string and prints its inorder to prove the round trip.",
        [("Which traversal of a BST produces sorted order?",
          ["Inorder", "Preorder", "Postorder", "Level order"], 0,
          "Left subtree, node, right subtree visits keys in ascending order — the property behind kth-smallest and BST validation."),
         ("Why is postorder the right shape for 'compute something from both subtrees'?",
          ["Both children are fully processed before the node combines them",
           "It visits fewer nodes",
           "It is iterative by nature",
           "It works only on balanced trees"], 0,
          "Height, diameter and subtree sums are all postorder aggregations — the node's answer needs its children's answers first."),
         ("What does level-order need that depth-first traversals do not?",
          ["A queue", "A stack", "Recursion", "A visited set"], 0,
          "BFS is queue-driven. Processing a whole level at a time means recording the queue size before draining it.")]),

    _w(20, "Month 5 · Trees, sorting & search",
        "BSTs & Tree DP",
        "Exploit ordering, and aggregate answers upward through a tree.",
        ["bst", "tree_dp"],
        [("bst-search", "Ordering turns search into a descent."),
         ("validate-bst", "Bounds passed down, not just child comparisons."),
         ("lca-bst", "Ordering makes the ancestor obvious."),
         ("kth-smallest-bst", "Inorder with a counter."),
         ("diameter-of-tree", "A postorder aggregation."),
         ("max-path-sum", "The hardest version of the same shape.")],
        "Write a `BstRange.java` that reads a BST and a range `lo hi` and prints the sum of all keys inside it, pruning subtrees that cannot contribute.",
        [("Why is comparing each node only against its children NOT enough to validate a BST?",
          ["A deep descendant can violate a distant ancestor's bound",
           "Children may be null",
           "Duplicates are allowed",
           "It is enough"], 0,
          "Pass a (low, high) range down and tighten it at each step — the local check misses violations one level further away."),
         ("What does a tree-DP function typically return?",
          ["Its subtree's answer, while updating a global best on the way up",
           "Only a boolean",
           "The node's depth",
           "Nothing; it mutates the tree"], 0,
          "Diameter and max-path-sum both do this: return the best downward path, but combine both sides into the global answer at each node."),
         ("What is the worst-case height of an unbalanced BST with n nodes?",
          ["n, when the keys arrive already sorted",
           "log n always",
           "sqrt(n)",
           "n / 2"], 0,
          "Sorted insertion degenerates the tree into a linked list, which is why self-balancing trees (Java's TreeMap uses a red-black tree) exist.")]),

    _w(21, "Month 5 · Trees, sorting & search",
        "Sorting & Binary Search",
        "Order the data, then exploit that order.",
        ["sorting", "binary_search"],
        [("kth-smallest", "Sort, then index."),
         ("sort-by-frequency", "A comparator with a tie-break."),
         ("binary-search-first", "The lower-bound form."),
         ("search-insert-position", "Where it WOULD go."),
         ("integer-sqrt", "Binary search on the answer, not the array."),
         ("mountain-array", "Search a shape rather than a value.")],
        "Write a `Bounds.java` implementing lowerBound and upperBound over a sorted array with duplicates, and print how many times a target occurs.",
        [("Why write `mid = lo + (hi - lo) / 2` instead of `(lo + hi) / 2`?",
          ["The naive form can overflow int for large indices",
           "It is faster",
           "It rounds differently",
           "It handles empty ranges"], 0,
          "A famous bug that sat in the JDK's own binarySearch for years."),
         ("For a lower bound, why is the update `hi = mid` rather than `hi = mid - 1`?",
          ["mid itself may be the answer, so it must stay in the range",
           "To avoid an infinite loop",
           "Because the range is inclusive",
           "It should be mid - 1"], 0,
          "Half-open `[lo, hi)` with `hi = mid` is the form that reliably finds the FIRST qualifying element."),
         ("What does `Arrays.sort` use for an object array?",
          ["A stable TimSort", "Dual-pivot quicksort", "Heap sort", "Counting sort"], 0,
          "Objects get stability (equal elements keep their relative order); primitives get quicksort, where stability is meaningless.")]),

    _w(22, "Month 5 · Trees, sorting & search",
        "Greedy & Intervals",
        "When does taking the locally best choice actually give the global optimum?",
        ["greedy", "intervals"],
        [("jump-game", "Track the furthest reachable index."),
         ("merge-intervals", "Sort by start, then fold."),
         ("non-overlapping-remove", "Sort by END — the classic surprise."),
         ("min-arrows-balloons", "The same shape as interval scheduling."),
         ("can-attend-meetings", "The simplest overlap check."),
         ("insert-interval", "Merging into an already-sorted set.")],
        "Write a `Schedule.java` that reads meetings and prints the largest number that can be attended without overlap, plus which ones.",
        [("For maximum non-overlapping intervals, what do you sort by?",
          ["End time — finishing earliest leaves the most room",
           "Start time",
           "Duration",
           "Start time descending"], 0,
          "Sorting by start solves MERGING; sorting by end solves SELECTION. Mixing them up is the classic interval mistake."),
         ("What must be true for a greedy algorithm to be correct?",
          ["The locally optimal choice is always part of some global optimum",
           "The input is sorted",
           "There are no duplicates",
           "It runs in O(n log n)"], 0,
          "This is the exchange-argument property. Without it — coin change with arbitrary denominations, for instance — greedy silently returns a worse answer."),
         ("Two intervals overlap when…",
          ["a.start <= b.end && b.start <= a.end",
           "a.start < b.start",
           "a.end == b.start",
           "They share an endpoint"], 0,
          "Whether touching endpoints count as overlapping is a per-problem decision — read the statement rather than assuming.")]),

    # =======================================================================
    # MONTH 6 — Recursion, DP & graphs
    # =======================================================================
    _w(23, "Month 6 · Recursion, DP & graphs",
        "Grids & Flood Fill",
        "Treat a grid as a graph and explore its connected regions.",
        ["grid", "flood_fill"],
        [("number-of-islands", "The canonical flood fill."),
         ("territory-capture", "Filling from the border inward."),
         ("color-bomb-explosion", "Region replacement."),
         ("spiral-order", "Pure index discipline."),
         ("set-matrix-zeroes", "In-place marking."),
         ("shortest-path-binary-matrix", "BFS on a grid.")],
        "Write a `Regions.java` that reads a character grid and prints the number of regions and the size of the largest, treating equal adjacent characters as connected.",
        [("Why mark a cell visited as you ENQUEUE it rather than when you dequeue it?",
          ["Otherwise the same cell can be enqueued several times before processing",
           "Dequeuing is slower",
           "It changes the traversal order",
           "There is no difference"], 0,
          "Marking on dequeue lets duplicates pile up in the queue, which can blow up the memory and the running time."),
         ("Why is a recursive flood fill risky on a large grid?",
          ["The recursion depth can equal the number of cells and overflow the stack",
           "It gives the wrong answer",
           "It cannot handle diagonals",
           "It is slower asymptotically"], 0,
          "An explicit stack or a BFS queue has the same complexity without depending on the JVM's stack size."),
         ("What is a common trick to avoid a separate visited array?",
          ["Overwrite each visited cell with a sentinel value in the grid itself",
           "Use a HashSet of coordinates, which is always faster",
           "Sort the grid first",
           "Traverse twice"], 0,
          "It saves memory and is fine when the grid may be mutated — otherwise copy first or use a boolean array.")]),

    _w(24, "Month 6 · Recursion, DP & graphs",
        "Recursion, Backtracking & Pruning",
        "Explore a decision tree, undo cleanly, and cut branches that cannot win.",
        ["recursion", "recurrence", "backtracking", "pruning"],
        [("generate-subsets", "Take-or-skip at each element."),
         ("generate-permutations", "Choose, recurse, undo."),
         ("combination-sum-count", "Repetition allowed."),
         ("letter-combinations-phone", "A product of choices."),
         ("word-search", "Backtracking over a grid."),
         ("n-queens-count", "Where pruning stops being optional.")],
        "Write a `Sudoku.java` that reads a 9x9 grid and reports whether it is solvable, using constraint checks to prune before recursing.",
        [("What distinguishes backtracking from plain recursion?",
          ["It UNDOES its choice after recursing, so siblings see a clean state",
           "It is always iterative",
           "It uses memoisation",
           "It never revisits a state"], 0,
          "The undo step is the definition. Forgetting it is why the second branch of a search returns nonsense."),
         ("Why does naive recursive Fibonacci take exponential time?",
          ["The same subproblems are recomputed along different branches",
           "Recursion is inherently slow",
           "The stack depth is exponential",
           "It does not"], 0,
          "Memoising collapses it to linear. Recognising overlapping subproblems is the step from recursion to dynamic programming."),
         ("What is the point of a pruning check?",
          ["Abandon a branch as soon as it cannot possibly lead to a solution",
           "Reduce the recursion depth",
           "Make the search iterative",
           "Sort the candidates"], 0,
          "It does not change the worst case, but on real inputs it is often the difference between milliseconds and never finishing.")]),

    _w(25, "Month 6 · Recursion, DP & graphs",
        "Dynamic Programming & Complexity",
        "Find the state, write the recurrence, then decide top-down or bottom-up.",
        ["dp", "dp2d", "big_o"],
        [("climbing-stairs", "The smallest recurrence."),
         ("house-robber", "Two rolling states."),
         ("coin-change", "Unbounded choice."),
         ("unique-paths", "A 2-D table."),
         ("longest-common-subsequence", "The classic 2-D DP."),
         ("edit-distance", "Three transitions per cell.")],
        "Write a `Knapsack.java` solving 0/1 knapsack bottom-up, printing the best value and the chosen items, with the table reduced to one dimension.",
        [("What are the two ingredients of a dynamic-programming solution?",
          ["Overlapping subproblems and optimal substructure",
           "Sorting and binary search",
           "A greedy choice and a tie-break",
           "Recursion and a visited set"], 0,
          "Without overlap, memoising buys nothing; without optimal substructure, combining subproblem answers is simply invalid."),
         ("What is the difference between memoisation and tabulation?",
          ["Memoisation is top-down and computes only the states it needs; tabulation is bottom-up and fills them all",
           "Memoisation is always faster",
           "Tabulation uses recursion",
           "They give different answers"], 0,
          "Top-down is usually easier to derive from the recurrence; bottom-up avoids stack depth and makes rolling-array space savings obvious."),
         ("`for (int i = 0; i < n; i++) for (int j = i; j < n; j++)` — what is the complexity?",
          ["O(n²) — roughly n²/2 iterations, and constants are dropped",
           "O(n)",
           "O(n log n)",
           "O(n² log n)"], 0,
          "Half of a quadratic is still quadratic. Big-O describes the growth rate, not the constant factor.")]),

    _w(26, "Month 6 · Recursion, DP & graphs",
        "Graphs & Capstone",
        "Represent a graph, traverse it, order it, connect it, and weight it.",
        ["graph_repr", "bfs", "indegree", "topo", "graph_cycle",
         "union_find", "dijkstra", "bellman_ford", "mst"],
        [("number-of-provinces", "Connectivity, two ways."),
         ("course-schedule", "Topological order and cycles."),
         ("count-components", "Union-find or DFS."),
         ("dijkstra-shortest-path", "Weighted shortest paths."),
         ("mst-total-weight", "Kruskal with union-find."),
         ("word-ladder-length", "BFS over an implicit graph.")],
        "Capstone: write a `Network.java` that reads a weighted graph and reports whether it is connected, its MST weight, the shortest path between two nodes, and whether it contains a cycle — one program, four algorithms.",
        [("When is BFS the right choice over DFS for shortest paths?",
          ["On unweighted graphs, where the first arrival is already the shortest",
           "Always",
           "Only on trees",
           "When the graph is weighted"], 0,
          "With weights you need Dijkstra (non-negative) or Bellman-Ford (negatives allowed) — BFS's guarantee depends on every edge costing the same."),
         ("What does Kahn's algorithm placing fewer than n vertices tell you?",
          ["The graph contains a directed cycle",
           "The graph is disconnected",
           "The input had duplicate edges",
           "Nothing"], 0,
          "Anything left with a non-zero in-degree is trapped in a cycle — which is why the same routine answers both 'topological order' and 'is it acyclic'."),
         ("Why can Dijkstra fail on negative edge weights?",
          ["It finalises a node on first extraction, which a later negative edge could improve",
           "The priority queue cannot hold negatives",
           "It loops forever",
           "It cannot — Dijkstra handles them"], 0,
          "Bellman-Ford relaxes every edge n-1 times instead, which is slower but tolerates negatives and detects negative cycles.")]),
]


JAVA_EXAMS.update({
    14: _java_exam(
        "Reverse-Polish calculator",
        "The input is one line of space-separated RPN tokens (integers and the operators `+ - * /`). Print the result, or `error` if the expression is malformed (too few operands, leftover operands, or division by zero).",
        """
        String[] tokens = sc.nextLine().trim().split("\\\\s+");
        ArrayDeque<Long> stack = new ArrayDeque<>();
        boolean ok = true;
        for (String t : tokens) {
            if (t.equals("+") || t.equals("-") || t.equals("*") || t.equals("/")) {
                if (stack.size() < 2) {
                    ok = false;
                    break;
                }
                long b = stack.pop();
                long a = stack.pop();
                if (t.equals("/") && b == 0) {
                    ok = false;
                    break;
                }
                if (t.equals("+")) stack.push(a + b);
                else if (t.equals("-")) stack.push(a - b);
                else if (t.equals("*")) stack.push(a * b);
                else stack.push(a / b);
            } else {
                stack.push(Long.parseLong(t));
            }
        }
        if (!ok || stack.size() != 1) System.out.println("error");
        else System.out.println(stack.pop());
        """,
        [("3 4 +", "7"), ("5 1 2 + 4 * + 3 -", "14"),
         ("1 +", "error"), ("1 2", "error"), ("4 0 /", "error"),
         ("6 2 /", "3")],
        hint="Pop the RIGHT operand first — `a - b` with the pops in the wrong order silently computes b - a."),

    15: _java_exam(
        "Ring buffer",
        "The input is `capacity n` then `n` values. Push each into a fixed-capacity buffer that drops the oldest once full. Print the contents oldest-first space-separated (or `(empty)`), then the size, then whether it is full.",
        """
        int capacity = sc.nextInt();
        int n = sc.nextInt();
        ArrayDeque<Integer> buffer = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            buffer.addLast(sc.nextInt());
            if (buffer.size() > capacity) buffer.pollFirst();
        }
        StringBuilder sb = new StringBuilder();
        for (int v : buffer) {
            if (sb.length() > 0) sb.append(' ');
            sb.append(v);
        }
        System.out.println(sb.length() == 0 ? "(empty)" : sb.toString());
        System.out.println(buffer.size());
        System.out.println(buffer.size() == capacity);
        """,
        [("3 5\n1 2 3 4 5", "3 4 5\n3\ntrue"),
         ("5 2\n7 8", "7 8\n2\nfalse"),
         ("1 3\n1 2 3", "3\n1\ntrue"),
         ("2 0", "(empty)\n0\nfalse")],
        hint="addLast then trim from the front — iterating an ArrayDeque walks it front-to-back, which is oldest-first."),

    16: _java_exam(
        "Huffman merge cost",
        "The input is `n` then `n` positive weights. Repeatedly remove the two smallest, push back their sum, and charge that sum — until one remains. Print the total cost, then the number of merges performed.",
        """
        int n = sc.nextInt();
        PriorityQueue<Long> pq = new PriorityQueue<>();
        for (int i = 0; i < n; i++) pq.add(sc.nextLong());
        long cost = 0;
        int merges = 0;
        while (pq.size() > 1) {
            long a = pq.poll();
            long b = pq.poll();
            cost += a + b;
            pq.add(a + b);
            merges++;
        }
        System.out.println(cost);
        System.out.println(merges);
        """,
        [("4\n1 2 3 4", "19\n3"), ("1\n7", "0\n0"),
         ("2\n5 5", "10\n1"), ("5\n4 3 2 6 1", "35\n4")],
        hint="A PriorityQueue<Long> is a min-heap, so poll() hands you the smallest. n items always take n-1 merges."),

    17: _java_exam(
        "Autocomplete",
        "The input is `n` then `n` dictionary words, then `q` then `q` prefixes. For each prefix print up to five completions in alphabetical order, space-separated, or `(none)`.",
        """
        int n = sc.nextInt();
        List<String> words = new ArrayList<>();
        for (int i = 0; i < n; i++) words.add(sc.next());
        Collections.sort(words);
        int q = sc.nextInt();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < q; i++) {
            String prefix = sc.next();
            List<String> hits = new ArrayList<>();
            for (String w : words) {
                if (w.startsWith(prefix)) hits.add(w);
                if (hits.size() == 5) break;
            }
            sb.append(hits.isEmpty() ? "(none)" : String.join(" ", hits)).append('\\n');
        }
        System.out.print(sb.toString());
        """,
        [("4\ncar cat dog cart\n2\nca do", "car cart cat\ndog"),
         ("3\na ab abc\n1\nab", "ab abc"),
         ("2\nxy yz\n1\nq", "(none)"),
         ("6\naa ab ac ad ae af\n1\na", "aa ab ac ad ae")],
        hint="Sorting once up front means the first five matches you find are already the alphabetically first five."),

    18: _java_exam_cls(
        "Linked list palindrome",
        "The input is `n` then `n` values forming a linked list. Print `true` if the values read the same forwards and backwards, using O(1) extra space: find the middle with fast/slow, reverse the second half, then compare. Print the list's length on the second line.",
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
        Node prev = null;
        Node curr = slow;
        while (curr != null) {
            Node next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        boolean palindrome = true;
        Node left = head;
        Node right = prev;
        while (right != null && left != null) {
            if (left.val != right.val) {
                palindrome = false;
                break;
            }
            left = left.next;
            right = right.next;
        }
        System.out.println(palindrome);
        System.out.println(n);
    }
""",
        """
        Node slow = head;
        Node fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        Node prev = null;
        Node curr = slow;
        while (curr != null) {
            Node next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        boolean palindrome = true;
        Node left = head;
        Node right = prev;
        while (right != null && left != null) {
            if (left.val != right.val) {
                palindrome = false;
                break;
            }
            left = left.next;
            right = right.next;
        }
        System.out.println(palindrome);
        System.out.println(n);
""",
        [("5\n1 2 3 2 1", "true\n5"), ("4\n1 2 2 1", "true\n4"),
         ("3\n1 2 3", "false\n3"), ("1\n9", "true\n1"),
         ("2\n4 4", "true\n2")],
        hint="Reverse from the slow pointer onward; comparing until the reversed half runs out handles both odd and even lengths."),

    19: _java_exam_cls(
        "Serialize and rebuild a tree",
        "The input is `n` then `n` level-order values with `-1` for a missing node. Print the tree's preorder with `#` for null (space-separated), then its inorder (real values only, space-separated).",
        """
    static int[] a;
    static StringBuilder pre = new StringBuilder();
    static StringBuilder ino = new StringBuilder();

    static void preorder(int i) {
        if (i >= a.length || a[i] == -1) {
            if (pre.length() > 0) pre.append(' ');
            pre.append('#');
            return;
        }
        if (pre.length() > 0) pre.append(' ');
        pre.append(a[i]);
        preorder(2 * i + 1);
        preorder(2 * i + 2);
    }

    static void inorder(int i) {
        if (i >= a.length || a[i] == -1) return;
        inorder(2 * i + 1);
        if (ino.length() > 0) ino.append(' ');
        ino.append(a[i]);
        inorder(2 * i + 2);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        preorder(0);
        inorder(0);
        System.out.println(pre.toString());
        System.out.println(ino.toString());
    }
""",
        """
    static void preorder(int i) {
        if (i >= a.length || a[i] == -1) {
            if (pre.length() > 0) pre.append(' ');
            pre.append('#');
            return;
        }
        if (pre.length() > 0) pre.append(' ');
        pre.append(a[i]);
        preorder(2 * i + 1);
        preorder(2 * i + 2);
    }

    static void inorder(int i) {
        if (i >= a.length || a[i] == -1) return;
        inorder(2 * i + 1);
        if (ino.length() > 0) ino.append(' ');
        ino.append(a[i]);
        inorder(2 * i + 2);
    }
""",
        [("3\n2 1 3", "2 1 # # 3 # #\n1 2 3"),
         ("1\n5", "5 # #\n5"),
         ("7\n1 2 3 4 5 6 7", "1 2 4 # # 5 # # 3 6 # # 7 # #\n4 2 5 1 6 3 7")],
        hint="Preorder emits the node then both children, so a null slot still contributes a `#`. Inorder skips nulls entirely."),

    20: _java_exam_cls(
        "BST range sum",
        "The input is `n`, then `n` level-order values with `-1` for a missing node (values are positive and form a valid BST), then `lo hi`. Print the sum of every key in `[lo, hi]`, then how many keys were in range — pruning subtrees that cannot contribute.",
        """
    static int[] a;
    static int lo;
    static int hi;
    static long sum = 0;
    static int count = 0;

    static void walk(int i) {
        if (i >= a.length || a[i] == -1) return;
        int v = a[i];
        if (v > lo) walk(2 * i + 1);
        if (v >= lo && v <= hi) {
            sum += v;
            count++;
        }
        if (v < hi) walk(2 * i + 2);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        lo = sc.nextInt();
        hi = sc.nextInt();
        walk(0);
        System.out.println(sum);
        System.out.println(count);
    }
""",
        """
    static void walk(int i) {
        if (i >= a.length || a[i] == -1) return;
        int v = a[i];
        if (v > lo) walk(2 * i + 1);
        if (v >= lo && v <= hi) {
            sum += v;
            count++;
        }
        if (v < hi) walk(2 * i + 2);
    }
""",
        [("7\n8 4 12 2 6 10 14\n5 12", "36\n4"),
         ("3\n2 1 3\n1 3", "6\n3"),
         ("1\n5\n6 10", "0\n0"),
         ("7\n8 4 12 2 6 10 14\n8 8", "8\n1")],
        hint="Only descend left when the node's key is above lo, and right when it is below hi — that is the pruning."),

    21: _java_exam(
        "Lower and upper bound",
        "The input is `n target` then `n` integers sorted ascending (duplicates allowed). Print the first index whose value is >= target, the first index whose value is > target, and how many times target occurs.",
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
        int lower = lo;
        lo = 0;
        hi = n;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] > target) hi = mid;
            else lo = mid + 1;
        }
        int upper = lo;
        System.out.println(lower);
        System.out.println(upper);
        System.out.println(upper - lower);
        """,
        [("6 3\n1 2 3 3 3 5", "2\n5\n3"),
         ("5 4\n1 2 3 5 6", "3\n3\n0"),
         ("4 1\n1 1 1 1", "0\n4\n4"),
         ("3 9\n1 2 3", "3\n3\n0")],
        hint="The two searches differ by one character: >= for the lower bound, > for the upper. Their gap is the occurrence count."),

    22: _java_exam(
        "Meeting schedule",
        "The input is `n` then `n` lines of `start end`. Print the largest number of meetings attendable without overlap, then their `start end` pairs one per line in the order chosen. A meeting starting exactly when another ends is fine.",
        """
        int n = sc.nextInt();
        int[][] m = new int[n][2];
        for (int i = 0; i < n; i++) {
            m[i][0] = sc.nextInt();
            m[i][1] = sc.nextInt();
        }
        Arrays.sort(m, (x, y) -> x[1] != y[1] ? Integer.compare(x[1], y[1]) : Integer.compare(x[0], y[0]));
        List<int[]> chosen = new ArrayList<>();
        int lastEnd = Integer.MIN_VALUE;
        for (int[] meeting : m) {
            if (meeting[0] >= lastEnd) {
                chosen.add(meeting);
                lastEnd = meeting[1];
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int[] meeting : chosen) sb.append(meeting[0]).append(' ').append(meeting[1]).append('\\n');
        System.out.println(chosen.size());
        System.out.print(sb.toString());
        """,
        [("3\n0 30\n5 10\n15 20", "2\n5 10\n15 20"),
         ("2\n1 4\n4 5", "2\n1 4\n4 5"),
         ("1\n1 5", "1\n1 5"),
         ("4\n1 4\n2 5\n3 6\n4 7", "2\n1 4\n4 7")],
        hint="Sort by END time — finishing earliest leaves the most room for what follows. Sorting by start solves a different problem."),

    23: _java_exam(
        "Count regions",
        "The input is `r c` then `r` rows of `c` characters (no spaces). Adjacent cells (up/down/left/right) holding the SAME character belong to one region. Print the number of regions, then the size of the largest.",
        """
        int r = sc.nextInt();
        int c = sc.nextInt();
        char[][] g = new char[r][];
        for (int i = 0; i < r; i++) g[i] = sc.next().toCharArray();
        boolean[][] seen = new boolean[r][c];
        int[] dr = {1, -1, 0, 0};
        int[] dc = {0, 0, 1, -1};
        int regions = 0;
        int largest = 0;
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                if (seen[i][j]) continue;
                regions++;
                char target = g[i][j];
                int size = 0;
                ArrayDeque<int[]> stack = new ArrayDeque<>();
                stack.push(new int[]{i, j});
                seen[i][j] = true;
                while (!stack.isEmpty()) {
                    int[] cur = stack.pop();
                    size++;
                    for (int d = 0; d < 4; d++) {
                        int ni = cur[0] + dr[d];
                        int nj = cur[1] + dc[d];
                        if (ni < 0 || ni >= r || nj < 0 || nj >= c) continue;
                        if (seen[ni][nj] || g[ni][nj] != target) continue;
                        seen[ni][nj] = true;
                        stack.push(new int[]{ni, nj});
                    }
                }
                if (size > largest) largest = size;
            }
        }
        System.out.println(regions);
        System.out.println(largest);
        """,
        [("3 3\naab\naab\nccb", "3\n4"),
         ("1 1\nx", "1\n1"),
         ("2 2\nab\nba", "4\n1"),
         ("2 3\naaa\naaa", "1\n6")],
        hint="Mark each cell seen as you PUSH it, not when you pop it, or the same cell enters the stack several times."),

    24: _java_exam_cls(
        "Sudoku solvable",
        "The input is 9 lines of 9 digits, `0` meaning empty. Print `true` if the puzzle can be completed legally and `false` otherwise, then the number of empty cells in the input. Reject an already-illegal board up front — searching one wastes the whole run.",
        """
    static int[][] g = new int[9][9];

    static boolean ok(int r, int c, int v) {
        for (int i = 0; i < 9; i++) {
            if (g[r][i] == v || g[i][c] == v) return false;
        }
        int br = r / 3 * 3;
        int bc = c / 3 * 3;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (g[br + i][bc + j] == v) return false;
            }
        }
        return true;
    }

    static boolean givensAreLegal() {
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                int v = g[r][c];
                if (v == 0) continue;
                g[r][c] = 0;
                boolean fine = ok(r, c, v);
                g[r][c] = v;
                if (!fine) return false;
            }
        }
        return true;
    }

    static boolean solve(int pos) {
        if (pos == 81) return true;
        int r = pos / 9;
        int c = pos % 9;
        if (g[r][c] != 0) return solve(pos + 1);
        for (int v = 1; v <= 9; v++) {
            if (!ok(r, c, v)) continue;
            g[r][c] = v;
            if (solve(pos + 1)) return true;
            g[r][c] = 0;
        }
        return false;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int empty = 0;
        for (int i = 0; i < 9; i++) {
            String row = sc.next();
            for (int j = 0; j < 9; j++) {
                g[i][j] = row.charAt(j) - '0';
                if (g[i][j] == 0) empty++;
            }
        }
        System.out.println(givensAreLegal() && solve(0));
        System.out.println(empty);
    }
""",
        """
    static boolean ok(int r, int c, int v) {
        for (int i = 0; i < 9; i++) {
            if (g[r][i] == v || g[i][c] == v) return false;
        }
        int br = r / 3 * 3;
        int bc = c / 3 * 3;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (g[br + i][bc + j] == v) return false;
            }
        }
        return true;
    }

    static boolean givensAreLegal() {
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                int v = g[r][c];
                if (v == 0) continue;
                g[r][c] = 0;
                boolean fine = ok(r, c, v);
                g[r][c] = v;
                if (!fine) return false;
            }
        }
        return true;
    }

    static boolean solve(int pos) {
        if (pos == 81) return true;
        int r = pos / 9;
        int c = pos % 9;
        if (g[r][c] != 0) return solve(pos + 1);
        for (int v = 1; v <= 9; v++) {
            if (!ok(r, c, v)) continue;
            g[r][c] = v;
            if (solve(pos + 1)) return true;
            g[r][c] = 0;
        }
        return false;
    }
""",
        [("534678912\n672195348\n198342567\n859761423\n426853791\n713924856\n961537284\n287419635\n345286179",
          "true\n0"),
         ("534678912\n672195348\n198342567\n859761423\n426853791\n713924856\n961537284\n287419635\n345286170",
          "true\n1"),
         ("110000000\n000000000\n000000000\n000000000\n000000000\n000000000\n000000000\n000000000\n000000000",
          "false\n79")],
        hint="Check the givens first — an illegal board has no solution, and searching for one takes effectively forever. Then undo each placement (`g[r][c] = 0`) when a branch fails."),

    25: _java_exam(
        "0/1 knapsack",
        "The input is `n capacity` then `n` lines of `weight value`. Print the best achievable value, then how much capacity it uses. Fill the table bottom-up with a single rolling row.",
        """
        int n = sc.nextInt();
        int capacity = sc.nextInt();
        int[] weight = new int[n];
        int[] value = new int[n];
        for (int i = 0; i < n; i++) {
            weight[i] = sc.nextInt();
            value[i] = sc.nextInt();
        }
        int[] best = new int[capacity + 1];
        for (int i = 0; i < n; i++) {
            for (int w = capacity; w >= weight[i]; w--) {
                best[w] = Math.max(best[w], best[w - weight[i]] + value[i]);
            }
        }
        int answer = best[capacity];
        int used = 0;
        for (int w = 0; w <= capacity; w++) {
            if (best[w] == answer) {
                used = w;
                break;
            }
        }
        System.out.println(answer);
        System.out.println(used);
        """,
        [("3 5\n2 3\n3 4\n4 5", "7\n5"),
         ("1 1\n2 9", "0\n0"),
         ("2 10\n5 10\n5 10", "20\n10"),
         ("3 4\n1 1\n2 2\n3 3", "4\n4")],
        hint="Iterate the capacity DOWNWARD so each item is used at most once — an ascending loop turns this into unbounded knapsack."),

    26: _java_exam(
        "Capstone: network report",
        "The input is `n m src dst` then `m` lines of `u v w` (undirected, non-negative weights). Print four lines: whether the graph is connected, the total weight of a minimum spanning tree (or `-1` if disconnected), the shortest distance from `src` to `dst` (or `-1`), and the number of connected components.",
        """
        int n = sc.nextInt();
        int m = sc.nextInt();
        int src = sc.nextInt();
        int dst = sc.nextInt();
        int[][] edges = new int[m][3];
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int i = 0; i < m; i++) {
            int u = sc.nextInt();
            int v = sc.nextInt();
            int w = sc.nextInt();
            edges[i][0] = u;
            edges[i][1] = v;
            edges[i][2] = w;
            adj.get(u).add(new int[]{v, w});
            adj.get(v).add(new int[]{u, w});
        }
        int[] parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        Arrays.sort(edges, (x, y) -> Integer.compare(x[2], y[2]));
        long mst = 0;
        int joined = 0;
        for (int[] e : edges) {
            int ra = e[0];
            while (parent[ra] != ra) ra = parent[ra];
            int rb = e[1];
            while (parent[rb] != rb) rb = parent[rb];
            if (ra == rb) continue;
            parent[rb] = ra;
            mst += e[2];
            joined++;
        }
        int components = 0;
        for (int i = 0; i < n; i++) {
            int r = i;
            while (parent[r] != r) r = parent[r];
            if (r == i) components++;
        }
        boolean connected = components == 1;
        long[] dist = new long[n];
        Arrays.fill(dist, Long.MAX_VALUE);
        dist[src] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>((x, y) -> Long.compare(x[0], y[0]));
        pq.add(new long[]{0, src});
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
        System.out.println(connected);
        System.out.println(joined == n - 1 ? String.valueOf(mst) : "-1");
        System.out.println(dist[dst] == Long.MAX_VALUE ? "-1" : String.valueOf(dist[dst]));
        System.out.println(components);
        """,
        [("4 4 0 3\n0 1 1\n1 2 2\n2 3 1\n0 3 10", "true\n4\n4\n1"),
         ("4 2 0 3\n0 1 1\n2 3 1", "false\n-1\n-1\n2"),
         ("1 0 0 0", "true\n0\n0\n1"),
         ("3 3 0 2\n0 1 4\n1 2 1\n0 2 2", "true\n3\n2\n1")],
        hint="Four algorithms, one parse: Kruskal gives the MST and the components, Dijkstra gives the distance. Keep their state separate."),
})

JAVA_QUIZ_FROM = {
    1: ["jv_keywords"],
    2: ["jv_types"],
    3: ["alg_what_is"],
    4: ["jv_types", "jv_jvm"],
    5: ["alg_analyzing"],
    6: ["alg_linear_search"],
    7: ["jv_strings"],
    8: ["jv_strings", "alg_pattern_recognition"],
    9: ["alg_two_pointers"],
    10: ["alg_sliding_window"],
    11: ["alg_prefix_sums"],
    12: ["jv_collections"],
    13: ["alg_big_o", "alg_pattern_recognition"],
    14: ["jv_collections", "alg_space"],
    15: ["jv_oop", "jv_collections"],
    16: ["jv_collections", "alg_efficient_sorts"],
    17: ["jv_collections", "jv_strings"],
    18: ["jv_collections", "jv_jvm"],
    19: ["alg_recursion"],
    20: ["alg_recursion", "jv_generics"],
    21: ["alg_binary_search", "alg_sorting_basics", "alg_efficient_sorts",
         "alg_non_comparison_sorts"],
    22: ["alg_pattern_recognition"],
    23: ["alg_space"],
    24: ["alg_recursion", "alg_recurrences"],
    25: ["alg_recurrences", "alg_big_o", "alg_analyzing"],
    26: ["alg_pattern_recognition", "jv_collections"],
}

JAVA_CONTESTS = {
    13: ("Java checkpoint — Months 1–3", 90 * 60),
    26: ("Java finale — the whole programme", 120 * 60),
}

_attach(JAVA_WEEKS, JAVA_EXAMS, quiz_from=JAVA_QUIZ_FROM,
        contests=JAVA_CONTESTS, sample=4)


MASTERY = [
    {
        "key": "typescript",
        "title": "TypeScript Mastery",
        "language": "typescript",
        "subtitle": "26 weeks from `const` to conditional types — every chapter, in order, with problems, a build project and an end-of-week exam.",
        "intro": (
            "This is the Learn library turned into a programme. Each week gives you a "
            "small number of chapters to study, curated problems from the Library to "
            "apply them, a build project of your own, and a quiz you must pass to "
            "unlock the next week. Weeks ahead of you stay sealed — the point is to "
            "go in order. Weeks behind you stay open forever."
        ),
        "pass_mark": 75,
        "exam_language": "typescript",
        "weeks": TS_WEEKS,
    },
    {
        "key": "java",
        "title": "Java Mastery",
        "language": "java",
        "subtitle": "26 weeks from `Scanner` to Dijkstra — the whole Java syllabus in order, with problems, a build project and an end-of-week exam.",
        "intro": (
            "The interview-focused half of the app, sequenced. Each week gives you a "
            "few chapters, curated problems from the Library, something to build, and "
            "an exam — multiple choice plus a real coding final — that you must pass "
            "to unlock the next week. Weeks ahead stay sealed; weeks behind stay open."
        ),
        "pass_mark": 75,
        "exam_language": "java",
        "weeks": JAVA_WEEKS,
    },
]


# ---------------------------------------------------------------------------
# Invariants — a broken curriculum is worse than no curriculum, so fail the
# build rather than shipping dangling references.
# ---------------------------------------------------------------------------
# Stricter rules, per track. They start with TypeScript, which was brought up to
# them first (TS_MASTERY_ROADMAP.md, batch A); the Java track still has finals
# with 3 tests and repeats slots outside its checkpoint week, so it joins once
# it has been brought up too.
#   min_exam_tests           — a final is a gate; 2-3 tests can be special-cased.
#   starter_required         — every curated problem opens in the track's language.
#   repeats_need_review_note — a slug may reappear only as a labelled review.
#   min_quiz_bank            — distinct questions per week, so retakes differ.
_TRACK_RULES = {
    "typescript": {"min_exam_tests": 8, "starter_required": True,
                   "repeats_need_review_note": True, "min_quiz_bank": 16},
}


def _check_mastery(tracks, concepts, problems):
    """`problems` maps slug -> the generated problem (for its starter languages)."""
    for track in tracks:
        rules = _TRACK_RULES.get(track["key"], {})
        first_seen = {}
        lang = track["language"]
        in_language = {k for k, c in concepts.items() if c.get("language", "java") == lang}
        scheduled = []
        seen_weeks = set()
        for week in track["weeks"]:
            assert week["week"] not in seen_weeks, f"duplicate week {week['week']}"
            seen_weeks.add(week["week"])
            for key in week["concepts"]:
                assert key in concepts, f"week {week['week']}: unknown concept {key!r}"
                assert key in in_language, f"week {week['week']}: {key!r} is not a {lang} concept"
                scheduled.append(key)
            for ref in week["problems"]:
                assert ref["slug"] in problems, \
                    f"week {week['week']}: unknown problem slug {ref['slug']!r}"
                if rules.get("starter_required"):
                    assert track["exam_language"] in problems[ref["slug"]]["starter_code"], \
                        f"week {week['week']}: {ref['slug']!r} has no {track['exam_language']} starter"
                if ref["slug"] in first_seen and rules.get("repeats_need_review_note"):
                    assert ref["note"].startswith("Review"), \
                        f"week {week['week']}: {ref['slug']!r} was already curated in week " \
                        f"{first_seen[ref['slug']]} — pick another problem, or label it a review"
                first_seen.setdefault(ref["slug"], week["week"])
            assert week["quiz"], f"week {week['week']}: no end-of-week quiz"
            assert len(week["quiz"]) >= rules.get("min_quiz_bank", 1), \
                f"week {week['week']}: quiz bank has {len(week['quiz'])} questions; " \
                f"this track needs at least {rules['min_quiz_bank']}"
            for q in week["quiz"]:
                assert 0 <= q["answer"] < len(q["options"]), \
                    f"week {week['week']}: answer index out of range for {q['question']!r}"
                assert len(q["options"]) >= 2, f"week {week['week']}: quiz needs options"
            assert week["quiz_sample"] >= 1, f"week {week['week']}: quiz_sample must be >= 1"
            assert len(week["quiz"]) >= week["quiz_sample"], \
                f"week {week['week']}: bank of {len(week['quiz'])} is smaller than the sample"

            exam = week["exam"]
            assert exam, f"week {week['week']}: no coding final"
            assert "____" in exam["starter"], \
                f"week {week['week']}: exam starter has no ____ blank"
            assert exam["starter"] != exam["solution"], \
                f"week {week['week']}: exam starter equals its solution"
            assert exam["tests"], f"week {week['week']}: exam has no tests"
            assert len(exam["tests"]) >= rules.get("min_exam_tests", 1), \
                f"week {week['week']}: the final has {len(exam['tests'])} tests; " \
                f"this track needs at least {rules['min_exam_tests']}"
            inputs = [t["input"] for t in exam["tests"]]
            assert len(set(inputs)) == len(inputs), \
                f"week {week['week']}: the final repeats a test input"
            assert exam["language"] == track["exam_language"], \
                f"week {week['week']}: exam language does not match the track"

            if week["contest"]:
                assert week["problems"], \
                    f"week {week['week']}: a checkpoint contest needs problems to draw from"
                assert week["contest"]["duration_seconds"] > 0, \
                    f"week {week['week']}: contest needs a positive duration"
                for slug in week["contest"].get("slugs", []):
                    assert slug in problems, \
                        f"week {week['week']}: checkpoint slug {slug!r} is not a problem"
                    if rules.get("starter_required"):
                        assert track["exam_language"] in problems[slug]["starter_code"], \
                            f"week {week['week']}: checkpoint slug {slug!r} has no {track['exam_language']} starter"

        assert sorted(seen_weeks) == list(range(1, len(track["weeks"]) + 1)), \
            f"{track['key']}: weeks must be numbered 1..N with no gaps"
        flags = [w["optional"] for w in track["weeks"]]
        assert flags == sorted(flags), \
            f"{track['key']}: optional weeks must come after every core week"

        duplicates = {k for k in scheduled if scheduled.count(k) > 1}
        assert not duplicates, f"{track['key']}: concepts scheduled twice: {sorted(duplicates)}"

        missing = in_language - set(scheduled)
        assert not missing, \
            f"{track['key']}: concepts never scheduled (syllabus gap): {sorted(missing)}"
