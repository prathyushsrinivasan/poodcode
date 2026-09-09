# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The 8-month structured TypeScript course (POLISHED build).
#
# exec()'d inside gen_seed.py's namespace AFTER the other TypeScript files, so it
# can reuse `_P` (program normalizer). Defines a single global `TS_COURSE` (dict)
# which gen_seed writes to src-tauri/seeds/ts_course.json (served by `ts_course`).
#
# HARD DESIGN RULE (the user's core ask): a week may only require syntax/concepts
# introduced in that week or earlier. A gen-time `_lint_scope` check at the end
# enforces this by scanning every program for constructs that appear before the
# week that teaches them (loops<W4, functions<W5, array methods<W6, reduce<W8,
# object literals<W7). If you add content that violates the ladder, generation
# FAILS loudly.
#
# EXECUTION MODEL: exercises run through the same stdin/stdout judge as every
# Learn drill (Node type-stripping). Every blank targets RUNTIME code; programs
# read stdin with `fs.readFileSync(0,"utf8")`; output is matched exactly (after
# whitespace normalization). Each `solution` is verified end-to-end by
# tests/verify_ts_course.rs and a Node verifier.
#
# EXERCISE KINDS: "drill" (fill one ____ blank), "challenge"/"capstone" (write a
# whole solution where you see ____), "fix" (a complete but buggy program the
# learner corrects — no blank; starter=buggy, solution=fixed).
# ---------------------------------------------------------------------------


import os
import re


def _prog(src):
    return _P(src)


def _q(question, options, answer, explanation):
    return {"question": question, "options": options, "answer": answer,
            "explanation": explanation}


def _gloss(term, definition):
    return {"term": term, "def": definition}


def _tests(pairs):
    return [{"input": i, "output": o} for (i, o) in pairs]


def _mk(eid, title, prompt, full, tests, hints, difficulty, kind, starter=None,
        blank=None, harness="", judge_mode="", forbid=()):
    """Build a course Exercise dict. Either `blank` (a unique substring of `full`
    replaced by ____ to form the starter) OR an explicit `starter` (for "fix").

    `harness` is TypeScript appended to the learner's program before it compiles
    — never shown in the editor. `judge_mode` picks how the result is graded:
    "" (run it, compare stdout) or "types" (it only has to type-check).

    `forbid` lists substrings the learner may not submit. It exists for the
    questions whose assertions cannot protect themselves: "what type does
    TypeScript infer for `x`?" is checked with `Equal<Answer, typeof x>`, and
    `type Answer = typeof x` satisfies that without answering anything."""
    full = _prog(full)
    if starter is None:
        assert blank is not None, f"{eid}: need blank or starter"
        assert blank in full, f"{eid}: blank not found in solution: {blank!r}"
        starter = full.replace(blank, "____", 1)
        assert starter != full, f"{eid}: no blank applied"
    else:
        starter = _prog(starter)
        assert starter != full, f"{eid}: starter equals solution"
    if judge_mode == "types":
        assert not tests, f"{eid}: a type-level exercise is graded by the compiler, not by tests"
        assert harness.strip(), f"{eid}: a type-level exercise needs assertions in its harness"
    else:
        assert tests, f"{eid}: needs at least one test"
    forbid = list(forbid or [])
    for banned in forbid:
        assert banned not in full, (
            f"{eid}: the solution itself uses banned text {banned!r} — the exercise "
            f"would be unsolvable and 'Reveal solution' would hand out a rejected program"
        )
    hints = list(hints or [])
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "",
        "hints": hints, "language": "typescript",
        "kind": kind, "difficulty": difficulty,
        # Overwritten per week by _apply_strictness() at the end of this file.
        "strictness": "strict",
        "harness": _prog(harness) if harness else "",
        "judge_mode": judge_mode,
        "forbid": forbid,
        "starter": starter, "solution": full, "tests": _tests(tests),
        "source_slug": "", "dataset": "",
    }


def _ex(eid, title, prompt, full, blank, tests, hints=(), difficulty="Intro"):
    return _mk(eid, title, prompt, full, tests, hints, difficulty, "drill", blank=blank)


def _ch(eid, title, difficulty, prompt, full, blank, tests, hints=()):
    return _mk(eid, title, prompt, full, tests, hints, difficulty, "challenge", blank=blank)


def _fix(eid, title, prompt, buggy, fixed, tests, hints=(), difficulty="Easy"):
    return _mk(eid, title, prompt, fixed, tests, hints, difficulty, "fix", starter=buggy)


# ---------------------------------------------------------------------------
# FUNCTION EXERCISES — graded on what the function RETURNS
#
# A plain drill has to print its own answer, so every solution carries
# `console.log` scaffolding around the part that is actually being taught. A
# function exercise moves that scaffolding into a hidden harness: the learner
# writes only the function, and the driver below reads the case's stdin, calls
# it, and prints the return value in a canonical form.
#
# This is what lets the course pose a problem the way an interviewer does —
# "implement `twoSum(nums, target)`" — and grade the value that comes back.
# ---------------------------------------------------------------------------

def _harness_parse(ty, idx):
    """TypeScript that reads argument `idx` off stdin as `ty`."""
    src = f"__pcArg({idx})"
    if ty == "number":
        return f"Number({src})"
    if ty == "string":
        return src
    if ty == "boolean":
        return f'({src} === "true")'
    if ty == "number[]":
        return f"__pcNums({src})"
    if ty == "string[]":
        return f"__pcStrs({src})"
    raise AssertionError(f"unsupported harness parameter type: {ty!r}")


def _harness_print(ty, v):
    """TypeScript that renders a return value of type `ty` for the judge.

    Scalars and flat arrays print the way the rest of the course prints them
    (space-separated), so expected outputs read naturally. Anything richer —
    `number[][]`, a tuple, an object — falls back to JSON, which is canonical
    without needing a printer per shape."""
    if ty in ("number", "boolean"):
        return f"String({v})"
    if ty == "string":
        return v
    if ty in ("number[]", "boolean[]"):
        return f'{v}.map(String).join(" ")'
    if ty == "string[]":
        return f'{v}.join(" ")'
    return f"JSON.stringify({v})"


def _driver_ty(param):
    """The CONCRETE type the driver parses for a parameter.

    A parameter is `(name, type)`, or `(name, type, driver_type)` when the
    declared type is not something stdin can be parsed into — a generic `T[]`
    is driven as `number[]`, and the type argument is inferred from that, just
    as it would be at a real call site."""
    return param[2] if len(param) > 2 else param[1]


def _fn_harness(name, params, prints):
    """The hidden driver: one argument per stdin line, in declaration order.

    The call is left un-annotated so a *generic* function can be driven too —
    the type argument is inferred from what the driver passes, exactly as it
    would be at a real call site. The printer still pins the shape: a function
    returning the wrong thing fails to compile here rather than printing
    nonsense."""
    lines = [
        'import * as fs from "fs";',
        'const __pcLines: string[] = fs.readFileSync(0, "utf8").split("\\n");',
        # `?? ""` is not decoration: from week 6 these programs compile under
        # noUncheckedIndexedAccess, where __pcLines[i] is `string | undefined`.
        'const __pcArg = (i: number): string => (__pcLines[i] ?? "").trim();',
    ]
    driven = [_driver_ty(p) for p in params]
    if "number[]" in driven:
        lines.append('const __pcNums = (s: string): number[] => (s ? s.split(/\\s+/).map(Number) : []);')
    if "string[]" in driven:
        lines.append('const __pcStrs = (s: string): string[] => (s ? s.split(/\\s+/) : []);')
    args = ", ".join(_harness_parse(t, i) for i, t in enumerate(driven))
    lines.append(f"const __pcOut = {name}({args});")
    lines.append(f"console.log({_harness_print(prints, '__pcOut')});")
    return "\n".join(lines) + "\n"


def _fn(eid, title, prompt, name, params, returns, body, tests, hints=(),
        difficulty="Medium", generics="", prints=None):
    """A blank-page function exercise: the learner writes the whole body.

    `generics` is the angle-bracket clause for a generic signature ("T" →
    `function f<T>(…)`), and `prints` is the CONCRETE return type the driver
    sees once the type arguments are inferred — which differs from `returns`
    exactly when the signature is generic (`returns="T"`, `prints="number"`).
    A parameter may likewise carry a third element, the concrete type the
    driver passes in; see `_driver_ty`.

    The ____ sits where the body goes, so this still satisfies the course's
    "every starter has a blank" rule — but here the blank is the whole
    algorithm, not one token."""
    sig = ", ".join(f"{p[0]}: {p[1]}" for p in params)
    tp = f"<{generics}>" if generics else ""
    body = "\n".join("  " + ln if ln.strip() else ln for ln in _prog(body).split("\n"))
    solution = f"function {name}{tp}({sig}): {returns} {{\n{body.rstrip()}\n}}\n"
    starter = f"function {name}{tp}({sig}): {returns} {{\n  ____\n}}\n"
    return _mk(eid, title, prompt, solution, tests, hints, difficulty, "challenge",
               starter=starter, harness=_fn_harness(name, params, prints or returns))


# ---------------------------------------------------------------------------
# TYPE-LEVEL EXERCISES — graded by the compiler alone
#
# `Pick<T, K>` has no runtime value to print, so a type cannot be graded by
# running anything. These exercises are judged purely on whether the program
# type-checks: the harness carries `Expect<Equal<…>>` lines, each of which is
# one claim about the learner's type that fails at COMPILE time when wrong.
#
# `Equal` is the standard identity check (Millsap/type-challenges): two types
# are equal only when the two deferred conditional types are mutually
# assignable, which — unlike `A extends B ? … : …` — distinguishes `any`,
# `unknown` and a union from their members.
# ---------------------------------------------------------------------------

_TYPE_PRELUDE = """\
// Supplied by the checker. Equal<X, Y> is true only when X and Y are the SAME
// type, not merely assignable to each other.
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;
"""


def _types(eid, title, prompt, full, blank, asserts, hints=(), difficulty="Medium"):
    """A type-level drill. `asserts` is one `type _n = Expect<...>` per claim."""
    return _mk(eid, title, prompt, full, [], hints, difficulty, "drill", blank=blank,
               harness=_TYPE_PRELUDE + "\n" + _prog(asserts), judge_mode="types")


# ---------------------------------------------------------------------------
# THE FOUR READING KINDS
#
# Everything above asks the learner to WRITE something and grades what it does.
# That misses most of what using TypeScript actually feels like, which is
# reading: reading an inference you did not write, reading an error the compiler
# raised, reading a type that lies. These four kinds grade that, and each is a
# rearrangement of machinery that already exists rather than a new judge.
#
#   _predict  — name the type the compiler infers. The claim is
#               `Equal<typeof check, typeof x>`, so it is checked against the
#               REAL inference and never against a type hard-coded in the harness.
#               That is also why revealing the harness ("What's being checked?")
#               gives nothing away — and why `typeof` has to be banned, or the
#               answer would be a copy of the question.
#
#   _diagnose — a program that genuinely fails to compile, with the compiler's
#               own message quoted in the prompt. tools/verify_ts_course.py
#               type-checks every one of these starters (whether or not
#               --starters was passed) and fails if the quoted TSnnnn code is
#               not one the starter really emits, so the course cannot ship an
#               invented error message.
#
#   _retype   — a program that runs correctly and whose types say nothing. It is
#               graded on stdout AND on assertions, because the harness is
#               compiled in both modes: `Equal` is false for `any` against any
#               real type, so leaving an `any` in place fails the check without
#               needing to scan the source for the word.
#
#   _design   — the types are blanked out and the implementation is left intact,
#               so the shape has to be worked out from the code that consumes
#               it. Graded on stdout plus the same assertions.
# ---------------------------------------------------------------------------

def _predict(eid, title, code, expr, answer, hints=(), difficulty="Easy", why=""):
    """Predict the inferred type of `expr`.

    `code` sets the scene and must bind everything `expr` refers to. The learner
    annotates one more binding with the type they think `expr` already has, and
    the claim is `Equal<typeof check, typeof <expr>>` — their answer against the
    compiler's real opinion, never against a type restated in the harness.

    Deliberately an *annotation* rather than `type Answer = …`: a type alias is
    a week-8 concept (see `_SCOPE_RULES`) and predicting an inference is worth
    doing from week 1. Annotating a `const` needs nothing the first lesson has
    not already taught.

    `Equal` and not assignability, because assignability would accept every
    answer that is merely wide enough — `unknown` would pass everything, and
    `number` would pass where the honest answer is the literal type `7`.
    """
    # `typeof` in a TYPE position takes a name, not an expression: `typeof xs[0]`
    # and `typeof a * b` are both syntax errors. Bind the interesting expression
    # to a const in `code` and predict that instead.
    assert re.fullmatch(r"[A-Za-z_$][\w$]*(\.[A-Za-z_$][\w$]*)*", expr), (
        f"{eid}: predict target must be an identifier or dotted path, got {expr!r}"
    )
    code = _prog(code)
    line = "const check: {} = " + expr + ";\n"
    full = code + line.format(answer)
    starter = code + line.format("____")
    prompt = (f"What type does TypeScript already infer for `{expr}`? "
              f"Annotate `check` with exactly that type — not merely one that fits."
              + (f" {why}" if why else ""))
    return _mk(eid, title, prompt, full, [], hints, difficulty, "predict",
               starter=starter,
               harness=_TYPE_PRELUDE + f"\ntype _1 = Expect<Equal<typeof check, typeof {expr}>>;\n",
               judge_mode="types",
               # Without this the answer is `typeof <expr>` — which compiles,
               # proves nothing, and is right there in the revealed harness.
               forbid=["typeof"])


def _diagnose(eid, title, error, broken, fixed, tests, hints=(), difficulty="Medium",
              ask="Fix the cause."):
    """Read a real compiler error, then repair what caused it.

    `error` is the message tsc prints, including its `TSnnnn` code — the
    verifier re-derives that code from the starter and fails if it does not
    match, so this text cannot drift away from what the compiler really says.
    """
    assert "TS" in error, f"{eid}: quote the compiler's TSnnnn code in the error"
    prompt = f"The compiler rejects this program:\n\n    {error}\n\n{ask}"
    return _mk(eid, title, prompt, fixed, tests, hints, difficulty, "diagnose",
               starter=broken)


def _retype(eid, title, prompt, anyish, typed, asserts, tests, hints=(),
            difficulty="Medium"):
    """Replace `any` with types that describe what is actually there.

    Graded on stdout like any other program, plus `asserts` — which `any` cannot
    satisfy, because `Equal` treats it as its own type rather than as a wildcard.
    """
    # Word-boundary matched, or "many", "company" and "Germany" would all count
    # as an `any` and make these assertions lie in both directions.
    any_kw = re.compile(r"\bany\b")
    assert any_kw.search(_prog(anyish)), f"{eid}: a retype starter needs an `any` to replace"
    assert not any_kw.search(_prog(typed)), f"{eid}: the solution still contains `any`"
    return _mk(eid, title, prompt, typed, tests, hints, difficulty, "retype",
               starter=anyish, harness=_TYPE_PRELUDE + "\n" + _prog(asserts))


def _design(eid, title, prompt, full, blank, asserts, tests, hints=(),
            difficulty="Medium"):
    """Write the type declarations first; the implementation is already there.

    `blank` is the type declaration to withhold. The implementation below it
    stays visible on purpose: the shape is meant to be recovered from how the
    value is used, which is the skill this kind is for.
    """
    return _mk(eid, title, prompt, full, tests, hints, difficulty, "design",
               blank=blank, harness=_TYPE_PRELUDE + "\n" + _prog(asserts))


def _lesson(key, title, what, lesson_md, exercises, warmup=None, quiz=None):
    return {"key": key, "title": title, "what": what,
            "lesson": _prog(lesson_md) if lesson_md else "",
            "warmup": warmup or [], "exercises": exercises, "quiz": quiz or []}


def _cap_auto(title, brief, exercise, example_io="", rubric=None, stretch=None):
    return {"title": title, "brief": _prog(brief), "kind": "auto",
            "exercise": exercise, "example_io": example_io,
            "rubric": rubric or [], "reference": "", "stretch": stretch}


def _cap_brief(title, brief, reference="", rubric=None, stretch=None):
    return {"title": title, "brief": _prog(brief), "kind": "brief",
            "exercise": None, "example_io": "",
            "rubric": rubric or [], "reference": _prog(reference) if reference else "",
            "stretch": stretch}


def _fam(key, title, pattern, intro, exercises):
    """One PRACTICE FAMILY: several variants of a SINGLE pattern, drilled back to
    back. `pattern` names the motion in one line; `intro` is a short walkthrough
    of the base case, so each variant is a twist on something already shown
    rather than a cold start.

    Practice is deliberately NOT required to finish a week — the UI leaves it out
    of the completion gate — so adding 25 problems never moves the finish line.
    The scope linter still covers it (see `_all_programs`): a week-4 practice
    problem cannot reach for a week-8 idea any more than a lesson can.
    """
    assert exercises, f"{key}: a practice family with no variants"
    return {"key": key, "title": title, "pattern": pattern,
            "intro": _prog(intro) if intro else "", "exercises": exercises}


def _week(number, month, month_title, theme, goal, summary, lessons, capstone=None,
          objectives=None, why="", est_minutes=40, glossary=None, cheatsheet="",
          self_check=None, review=None, milestone="", authored=True, practice=None):
    return {
        "number": number, "month": month, "month_title": month_title,
        "theme": theme, "goal": goal, "summary": _prog(summary) if summary else "",
        "authored": authored, "lessons": lessons, "capstone": capstone,
        "objectives": objectives or [], "why": why, "est_minutes": est_minutes,
        "glossary": glossary or [], "cheatsheet": _prog(cheatsheet) if cheatsheet else "",
        "self_check": self_check or [], "review": review or [], "milestone": milestone,
        # Filled in by the practice pass below, keyed on week number, so a week
        # file never has to know whether practice exists for it yet.
        "practice": practice or [],
    }


def _skel(number, month, month_title, theme, goal, summary=""):
    return _week(number, month, month_title, theme, goal, summary, [], None,
                 authored=False)


_FS = 'import * as fs from "fs";\n'
_WEEKS = []

# Program prefixes shared by more than one week. They live here rather than in
# the week that introduces them because a later week reuses them, and a week
# file must never depend on another week file having been exec'd first.
_NUMS = _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
_WORDS = _FS + 'const words = fs.readFileSync(0, "utf8").trim().split(" ");\n'
_LINE = _FS + 'const line = fs.readFileSync(0, "utf8").trim();\n'

# ===========================================================================
# MONTH TITLES — carried by every week in the month.
# ===========================================================================
_M1 = "First Steps: Values, Logic & Loops"
_M2 = "Data & Functions"
_M3 = "The Type System, Properly"
# Defined up here, not down in the skeleton list, because the authored week files
# are exec'd BEFORE that list and a week in month 4 needs its title to exist. The
# skeletons for weeks not yet authored reuse the same names.
_M4 = "Robust, Real-World Programs"


# ===========================================================================
# AUTHORED WEEKS — one file each, exec'd into this namespace in order.
#
# Split out of this file once it passed 15,000 lines: at the rate the authored
# weeks were growing (week 1 is 980 lines, week 10 is 2,290), the remaining 22
# weeks would have taken it past 58,000. Same arrangement as the Java course's
# `_MODULE_FILES`. Each file appends exactly one week to `_WEEKS`.
#
# Order matters: `_WEEKS` is consumed positionally by the lint and strictness
# passes at the bottom of this file.
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))

_WEEK_FILES = (
    "ts_w01_basics.py",        # Month 1 — values, variables & output
    "ts_w02_text.py",          #          text & input
    "ts_w03_decisions.py",     #          making decisions
    "ts_w04_loops.py",         #          loops
    "ts_w05_functions.py",     # Month 2 — functions
    "ts_w06_arrays.py",        #          arrays
    "ts_w07_objects.py",       #          objects
    "ts_w08_types.py",         #          types that describe your data
    "ts_w09_unions.py",        # Month 3 — unions & narrowing
    "ts_w10_generics.py",      #          generics
    "ts_w11_classes.py",       #          classes & objects
    "ts_w12_structural.py",    #          structural typing, variance & satisfies
    "ts_w13_immutability.py",  # Month 4 — immutability & readonly
    "ts_w14_utility.py",       #          utility types
    "ts_w15_nullsafety.py",    #          null-safety & error handling
)

for _week_file in _WEEK_FILES:
    _path = os.path.join(_HERE, _week_file)
    with open(_path, encoding="utf-8") as _f:
        exec(compile(_f.read(), _path, "exec"))

# ===========================================================================
# MONTHS 3-8 — themed skeletons (authored in later batches).
#
# SEQUENCING NOTE. This list is the syllabus, and it used to have a hole in it:
# **classes appeared in no week at all**, in a course that reaches linked lists
# and trees in month 5 and cannot teach either without them. `satisfies`,
# structural typing, variance, `tsconfig` and declaration files were missing the
# same way — all six already exist as Learn concepts (`ts_classes`,
# `ts_this_accessors`, `ts_satisfies`, `ts_structural_typing`, `ts_tsconfig`,
# `ts_declaration_files`), so the gap was purely one of sequencing.
#
# Fitting them into a fixed 32 weeks needed three merges, each of a pair that
# was really one topic split in two:
#
#   - "Recursion" (was week 19) into "Recursion & Backtracking" (week 25).
#     Backtracking IS recursion; teaching it twice, six weeks apart, bought
#     nothing.
#   - "Optionals & Null-Safety" + "Error Handling" -> week 15. Both answer the
#     same question: the value isn't there, or getting it went wrong.
#   - "Modules & Organization" + the new tsconfig/declaration-file material ->
#     week 16. All three are about how a *project* is built rather than how a
#     program is written.
#
# Classes land in week 11 — after generics (so a generic `Stack<T>` is
# available) and six weeks before the data structures that need them.
#
# Two further topics turned up in a sweep as appearing in NO week and no
# skeleton, despite having complete Learn concepts written:
#
#   - `enum` (`ts_enums`) -> week 12, where comparing it against a literal union
#     and an `as const` object is the actual lesson rather than an aside.
#   - `JSON.parse`/`stringify` (`ts_json`) -> week 15. The more serious of the
#     two: `JSON.parse` returns `any`, so it is exactly where `unknown`, type
#     guards and validation stop being theoretical.
#
# ---------------------------------------------------------------------------
# WHERE THE CAPSTONE ARC ENDS (decided, not left open)
#
# Budget Buddy runs unbroken from week 1's receipt line to week 10's generic
# toolkit, each week's capstone reopening the last one's code. It keeps earning
# that through week 20 — classes give it a real Ledger, async a loader, maps
# fast lookup, trees a category hierarchy — and it **ends there**.
#
# It does not survive weeks 21-28. A budget app cannot honestly motivate binary
# search, dynamic programming or graph traversal, and bending it to fit would
# produce exactly the contrived capstone the first ten weeks avoid. So:
#
#   weeks 11-20  Budget Buddy #11-#20, ending with the category tree.
#   weeks 21-28  interview reps — a timed problem in the week's technique,
#                judged the same way, with no pretence of being a product.
#   weeks 29-32  a small typed library built from the type-level material
#                (DeepReadonly, a typed event emitter, a router whose paths are
#                parsed by template literal types).
#
# Each week's `milestone` string is what carries this narrative to the learner,
# so it is worth writing the milestone before the lessons.
# ===========================================================================
_WEEKS += [
    _skel(16, 4, _M4, "Modules, tsconfig & Declaration Files",
          "Split a program across files, then control how the whole project is checked: "
          "import/export, compiler strictness, and .d.ts files for untyped code."),
]
_M5 = "Async & Data Structures"
_WEEKS += [
    _skel(17, 5, _M5, "Async & Promises",
          "Work with promises and async/await for tasks that take time."),
    _skel(18, 5, _M5, "Stacks & Queues",
          "Build and use LIFO/FIFO structures and know when each fits."),
    _skel(19, 5, _M5, "Maps & Sets",
          "Reach for hash maps and sets to get O(1) lookup and de-duplication."),
    _skel(20, 5, _M5, "Linked Lists & Trees",
          "Model data as nodes that point to other nodes."),
]
_M6 = "Algorithmic Thinking"
_WEEKS += [
    _skel(21, 6, _M6, "Big-O & Complexity",
          "Reason about the time and space cost of your code."),
    _skel(22, 6, _M6, "Searching & Two Pointers",
          "Binary search a sorted array and sweep it with two pointers."),
    _skel(23, 6, _M6, "Sliding Window & Prefix Sums",
          "Answer range and subarray questions in linear time."),
    _skel(24, 6, _M6, "Sorting",
          "Understand the common sorts and use sorting as a problem-solving tool."),
]
_M7 = "DSA Interview Core"
_WEEKS += [
    _skel(25, 7, _M7, "Recursion & Backtracking",
          "Solve problems whose definition refers to themselves, then use that to "
          "generate and search combinatorial spaces (subsets, permutations)."),
    _skel(26, 7, _M7, "Dynamic Programming",
          "Turn overlapping recursion into fast, memoized DP."),
    _skel(27, 7, _M7, "Graphs: BFS & DFS",
          "Traverse graphs and grids to answer reachability and shortest-path questions."),
    _skel(28, 7, _M7, "Heaps & Intervals",
          "Use priority queues and interval techniques on classic problems."),
]
_M8 = "Advanced Types & Interview Polish"
_WEEKS += [
    _skel(29, 8, _M8, "Conditional & Mapped Types",
          "Compute new types from existing ones with conditional and mapped types."),
    _skel(30, 8, _M8, "Inference & Template Literal Types",
          "Bend the inference engine and build types from string patterns."),
    _skel(31, 8, _M8, "Type-Level Challenges",
          "Solve 'type gymnastics' puzzles the way interviewers pose them."),
    _skel(32, 8, _M8, "Mock Interview Week",
          "Put it together under time: DSA solved in TypeScript plus type challenges."),
]


# ===========================================================================
# PRACTICE — bulk variation drilling, one optional file per week.
#
# Kept OUT of the week files on purpose: those are the teaching path and are
# long enough already. A practice file only appends to `_PRACTICE[n]`, so adding
# practice to a week never touches that week's content.
#
# `CourseWeek.practice` and the UI that renders it have existed since the Java
# course was built — families appear above the capstone with their own progress
# chip, and are deliberately left out of the completion gate, so adding 25
# problems never moves the finish line. This wiring is what lets the TypeScript
# course populate them too; a week with no file here simply gets none.
#
# Runs after the skeletons so that every week — authored or not — ends up with
# the key present. A file is listed only once it exists, so the tuple grows with
# the course.
# ===========================================================================
_PRACTICE = {}

_PRACTICE_FILES = (
    "ts_p01_practice.py",      # week 1 — report, money, convert
)

for _prac_file in _PRACTICE_FILES:
    _path = os.path.join(_HERE, _prac_file)
    if os.path.exists(_path):
        with open(_path, encoding="utf-8") as _f:
            exec(compile(_f.read(), _path, "exec"))

for _w in _WEEKS:
    _w["practice"] = _PRACTICE.get(_w["number"], [])


# ===========================================================================
# CONCEPT-SCOPE LINT — enforce "never require concepts beyond this week".
# For each authored week, scan every program (drills/fixes/challenges/capstone/
# stretch) for tokens that belong to a LATER week. Fails generation if violated.
# ===========================================================================
def _all_exercises(week):
    """Every judged Exercise dict in a week — lessons, capstone, stretch, practice.

    Practice counts: it is optional to *complete*, but it is judged by the same
    judge, so it needs the same strictness preset as the rest of its week.
    """
    out = []
    for l in week["lessons"]:
        out.extend(l["exercises"])
    cap = week.get("capstone")
    if cap:
        for ex in (cap.get("exercise"), cap.get("stretch")):
            if ex:
                out.append(ex)
    for fam in week.get("practice", []):
        out.extend(fam["exercises"])
    return out


def _all_programs(week):
    out = []
    for l in week["lessons"]:
        for ex in l["exercises"]:
            out.append((ex["id"], ex["solution"]))
            out.append((ex["id"] + ":starter", ex["starter"]))
    cap = week.get("capstone")
    if cap:
        for ex in (cap.get("exercise"), cap.get("stretch")):
            if ex:
                out.append((ex["id"], ex["solution"]))
        if cap.get("reference"):
            out.append((cap["title"] + ":ref", cap["reference"]))
    # Practice is scoped exactly like a lesson program: a week-4 variation may
    # not reach for a week-8 idea just because it lives in a different file.
    for fam in week.get("practice", []):
        for ex in fam["exercises"]:
            out.append((ex["id"], ex["solution"]))
            out.append((ex["id"] + ":starter", ex["starter"]))
    return out


# ===========================================================================
# STRICTNESS LADDER — which tsc preset each week's programs are judged under.
#
# Every judged program is type-checked before it runs (src-tauri/src/tscheck.rs).
# `noUncheckedIndexedAccess` — which types `a[i]` as `T | undefined` — is the one
# flag the course cannot switch on from week 1: weeks 1-5 have not yet met the
# guard, the `??` or the `!` needed to satisfy it, so requiring it there would
# demand syntax the syllabus has not taught. Week 6 is where arrays are
# introduced, so that is where it turns on and gets a lesson of its own.
# ===========================================================================
INDEXED_FROM_WEEK = 6


def _apply_strictness(weeks):
    for w in weeks:
        preset = "strict+indexed" if w["number"] >= INDEXED_FROM_WEEK else "strict"
        for ex in _all_exercises(w):
            ex["strictness"] = preset


# (token substring, first week it's allowed). A program in a week EARLIER than
# the listed week must not contain the token.
_SCOPE_RULES = [
    ("while (", 4), ("for (", 4),          # loops
    ("=> ", 5), ("function ", 5),          # functions
    (".map(", 6), (".filter(", 6),
    (".split(", 6), (".join(", 6),         # array methods
    (".push(", 6), (".sort(", 6), (".find(", 6),   # array mutation/search
    ("?.", 7), ("Object.keys(", 7),         # optional chaining, object reflection
    (".reduce(", 8),                        # reduce
    ("interface ", 8), ("type ", 8),        # named types (annotations OK earlier)
    ("keyof ", 10),                         # keyof / indexed access
    # --- Constructs sequenced in months 3-8, gated before they are authored ---
    #
    # Every token below was checked against all ten authored weeks and appears in
    # none of them, so gating it at the week that teaches it costs nothing today
    # and constrains the content that has not been written yet. The ladder is
    # only load-bearing if it is written down BEFORE the content, not after.
    ("class ", 11), ("this.", 11),                   # classes
    ("private ", 11), ("protected ", 11), ("static ", 11),
    ("implements ", 11), ("abstract ", 11), ("super(", 11), ("super.", 11),
    #
    # `#private` names are NOT listed, and do not need to be: `#x` is only legal
    # inside a class body, so `class ` above already gates every use of one.
    # A bare ("#", 11) rule would instead match any stray `#` in a string.
    #
    # `extends ` is likewise absent, and MUST stay absent: week 10 uses it 79
    # times for generic constraints (`<T extends keyof U>`), so a rule here would
    # be a false claim about when the course first shows the keyword.
    ("satisfies ", 12),
    # `enum ` is safe to gate here: the only earlier occurrence in the repo is
    # inside a week-2 `diagnose` PROMPT (a quoted compiler message), and the lint
    # scans programs only.
    ("enum ", 12),
    ("ReadonlyArray<", 13), ("Object.freeze(", 13), ("Object.isFrozen(", 13),
    ("Partial<", 14), ("Pick<", 14), ("Omit<", 14),  # utility types
    ("Required<", 14), ("Readonly<", 14), ("Exclude<", 14), ("Extract<", 14),
    ("ReturnType<", 14), ("Parameters<", 14),
    #
    # `ReturnType<`/`Parameters<` appear once each in a week-8 HARNESS. Harnesses
    # are hidden from the learner and are not walked by `_all_programs`, so gating
    # them here is an honest claim about when the course first *shows* them.
    ("NonNullable<", 15), ("Awaited<", 17),
    ("JSON.parse(", 15), ("JSON.stringify(", 15), ("??=", 15),
    ("export ", 16), ("declare ", 16),               # modules & ambient decls
    ("async ", 17), ("await ", 17), ("Promise<", 17),
    ("new Map(", 19), ("new Set(", 19),
    #
    # DELIBERATELY NOT GATED, because the authored weeks already use them and a
    # rule here would be a false claim about when the course first shows them:
    #
    #   `new `        week 9  — `new Error(...)`, long before any class is declared
    #   `readonly `   week 8  — as a field modifier while modelling data
    #   `as const`    week 9  — pinning a literal type
    #   `Record<`     week 10 — as a generic example
    #   `try {`       week 8  — parsing at the boundary
    #   `catch `/`throw ` week 9 — the `instanceof Error` guard
    #
    # Weeks 13 and 15 therefore DEEPEN immutability and error handling rather
    # than introducing them; their lesson text should be written that way.
]


def _lint_scope(weeks):
    problems = []
    for w in weeks:
        if not w.get("authored"):
            continue
        wn = w["number"]
        for pid, prog in _all_programs(w):
            for token, allowed_from in _SCOPE_RULES:
                if wn < allowed_from and token in prog:
                    problems.append(
                        f"Week {wn} program {pid} uses {token!r} (not introduced until week {allowed_from})"
                    )
    if problems:
        raise AssertionError("TS course scope violations:\n  " + "\n  ".join(problems))


_lint_scope(_WEEKS)
_apply_strictness(_WEEKS)


TS_COURSE = {
    "key": "typescript",
    "title": "TypeScript: Zero to Interview",
    "subtitle": (
        "An 8-month, week-by-week course from your very first line of code to "
        "interview-ready — DSA solved in TypeScript and deep type-system mastery. "
        "Each authored week is five to ten hours of study across seven to nine "
        "lessons, with a goal, warm-ups that make you predict the output, "
        "fill-in-the-blank drills, fix-the-bug programs, an integrative "
        "challenge, hint ladders, a glossary, a cheat sheet, and a growing "
        "capstone project (Budget Buddy). You also read as much as you write: "
        "predict the type the compiler infers, decode a real error message, "
        "replace `any` with types that mean something, and design a type before "
        "the code that satisfies it. "
        "Nothing ever requires syntax a later week hasn't taught yet."
    ),
    "weeks": _WEEKS,
}
