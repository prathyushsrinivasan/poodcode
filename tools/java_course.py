# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The Java course — "After the Basics".
#
# exec()'d inside gen_seed.py's namespace LAST (after backend_course.py), so it
# is free to use short private helper names without shadowing anything still in
# use. Defines a single global `JAVA_COURSE` (dict) which gen_seed writes to
# src-tauri/seeds/java_course.json (served by the `java_course` command and
# rendered by the same src/pages/Course.tsx as the TypeScript course).
#
# It is also runnable on its own (`python tools/java_course.py`) so the verifier
# loop does not need a full seed regeneration.
#
# WHO IT IS FOR: someone who already has Java's basics — variables, types,
# operators, if/else, loops, printing, and enough arrays to declare one and loop
# over it. So Module 1 opens on the memory model and traversal *fluency*, not on
# `int x = 5;`. The full roadmap (and what each part covers) is JAVA_ROADMAP.md.
#
# SHIPPED SCOPE: Parts 1-3 of that roadmap — Arrays (modules 1-5), Strings
# (6-8), Methods and recursion (9-10). Everything after that is planned, not
# authored, and is deliberately absent rather than stubbed.
#
# HARD DESIGN RULES
#   1. NOTHING BEFORE ITS MODULE. A module may only require ideas introduced in
#      it or earlier — no StringBuilder before module 8, no helper methods
#      before module 9, no recursion before module 10. `_lint_scope` at the
#      bottom scans every program and FAILS generation on a violation.
#   2. EXPECTED OUTPUTS ARE COMPUTED, NEVER TYPED. Every test case's expected
#      stdout comes from a Python mirror of the intended algorithm (the helpers
#      below plus per-exercise lambdas), the same trust model gen_seed.py uses
#      for the problem bank. Typing an expected output by hand is a bug waiting
#      to happen, especially for multi-line traces like "print each sorting
#      pass".
#   3. NO COLLECTIONS. Parts 1-3 are about arrays, strings and methods, so
#      HashMap/ArrayList/streams/lambdas are banned outright by the linter —
#      they belong to Parts 6-8 of the roadmap and would rob those modules of
#      their point.
#
# EXECUTION MODEL: exercises run through the same stdin/stdout judge as every
# other track (`javac Main.java` -> `java Main`). Programs read stdin with a
# Scanner and print with System.out; output is compared after whitespace
# normalization. Every `solution` is proved end-to-end by
# tools/verify_java_course.py and src-tauri/tests/verify_java_course.rs.
#
# EXERCISE KINDS: "drill" (fill one ____ blank), "challenge" (write a whole
# region where you see ____), "fix" (a complete but buggy program the learner
# corrects — no blank; starter=buggy, solution=fixed).
# ---------------------------------------------------------------------------

import json
import os


# ===========================================================================
# Text / program normalizers
# ===========================================================================

def _jp(src):
    """Normalize a triple-quoted program or Markdown block: drop the leading
    newline, guarantee exactly one trailing newline."""
    return src.lstrip("\n").rstrip() + "\n"


_IMPORTS = "import java.util.*;\n"

# The exact signature line every program shares. The scope linter strips it
# before looking for `static `, so "does this program define a helper method?"
# is answerable with a substring search.
_MAIN_SIG = "    public static void main(String[] args) {"


def _jmain(body, imports=_IMPORTS):
    """A complete `Main` whose main() body is `body` (indented 8 spaces)."""
    return _jp(
        imports
        + "\npublic class Main {\n"
        + _MAIN_SIG + "\n"
        + body.rstrip("\n")
        + "\n    }\n}"
    )


def _jscan(body, imports=_IMPORTS):
    """A complete `Main` that opens a Scanner, then runs `body`."""
    return _jmain("        Scanner sc = new Scanner(System.in);\n" + body, imports)


def _jcls(members, imports=_IMPORTS):
    """A complete `Main` whose whole body you write — for modules 9-10, where
    the learner defines helper methods alongside main()."""
    return _jp(imports + "\npublic class Main {\n" + members.rstrip("\n") + "\n}")


def _joop(types, body, imports=_IMPORTS):
    """Helper CLASSES above `public class Main`, then a Scanner-opening main —
    the shape every Part 4 program takes.

    `javac Main.java` compiles every type in the file and `java -cp . Main`
    runs it (see src-tauri/src/exec.rs), so extra top-level classes need no
    build changes at all. Only `Main` may be `public`; the rest are
    package-private, which is exactly right for a single-file exercise."""
    return _jp(
        imports + "\n"
        + types.rstrip("\n") + "\n\n"
        + "public class Main {\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }\n}"
    )


# ===========================================================================
# stdin / stdout builders — the "computed, never typed" half of design rule 2.
#
# Each of these takes the DATA a case is about, renders the stdin the Java
# program will read, and runs a Python mirror of the algorithm to produce the
# expected stdout. Nothing below ever hard-codes an expected value.
# ===========================================================================

def _sp(xs):
    """Space-joined — how a Java program prints a row of numbers."""
    return " ".join(str(x) for x in xs)


def _nl(*parts):
    """Newline-joined expected output, from already-stringified pieces."""
    return "\n".join(str(p) for p in parts)


def _jarr(xs):
    """Exactly what `Arrays.toString(a)` prints."""
    return "[" + ", ".join(str(x) for x in xs) + "]"


def _jdeep(rows):
    """Exactly what `Arrays.deepToString(m)` prints."""
    return "[" + ", ".join(_jarr(r) for r in rows) + "]"


def _jbool(b):
    return "true" if b else "false"


def _jdiv(a, b):
    """Java's integer division (truncates toward zero), which differs from
    Python's // for negatives. Used wherever a lesson prints an average."""
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def _case(stdin, stdout):
    """One (stdin, expected stdout) pair, normalized like the judge does."""
    return (str(stdin), str(stdout).rstrip())


def _acase(a, out):
    """stdin = `n` then the n values on one line; stdout = `out`."""
    return _case(f"{len(a)}\n{_sp(a)}", out)


def _a2case(a, b, out):
    """stdin = two length-prefixed arrays on their own lines."""
    return _case(f"{len(a)}\n{_sp(a)}\n{len(b)}\n{_sp(b)}", out)


def _akcase(a, k, out):
    """stdin = a length-prefixed array, then a single extra integer `k`."""
    return _case(f"{len(a)}\n{_sp(a)}\n{k}", out)


def _mcase(m, out):
    """stdin = `rows cols` then one line per row; stdout = `out`."""
    head = f"{len(m)} {len(m[0])}"
    return _case(head + "\n" + "\n".join(_sp(r) for r in m), out)


def _scase(s, out):
    """stdin = one line of text; stdout = `out`."""
    return _case(s, out)


def _s2case(s, t, out):
    """stdin = two lines of text."""
    return _case(f"{s}\n{t}", out)


# Reusable stdin-reading snippets, so every array exercise reads its input the
# same way and the learner stops having to re-read the boilerplate.
_RD_ARR = (
    "        int n = sc.nextInt();\n"
    "        int[] a = new int[n];\n"
    "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
)

_RD_ARR2 = _RD_ARR + (
    "        int m = sc.nextInt();\n"
    "        int[] b = new int[m];\n"
    "        for (int i = 0; i < m; i++) b[i] = sc.nextInt();\n"
)

_RD_MAT = (
    "        int rows = sc.nextInt();\n"
    "        int cols = sc.nextInt();\n"
    "        int[][] m = new int[rows][cols];\n"
    "        for (int r = 0; r < rows; r++)\n"
    "            for (int c = 0; c < cols; c++) m[r][c] = sc.nextInt();\n"
)


# ===========================================================================
# Content builders — the same shapes the Rust `CourseWeek` model expects.
# ===========================================================================

def _jq(question, options, answer, explanation):
    return {"question": question, "options": options, "answer": answer,
            "explanation": explanation}


def _jg(term, definition):
    return {"term": term, "def": definition}


def _tests(pairs):
    return [{"input": i, "output": o} for (i, o) in pairs]


def _jmk(eid, title, prompt, full, tests, hints, difficulty, kind, starter=None,
         blank=None):
    """Build one course Exercise. Either `blank` (a unique substring of `full`
    replaced by ____ to form the starter) OR an explicit `starter` (for "fix")."""
    full = _jp(full)
    if starter is None:
        assert blank is not None, f"{eid}: need blank or starter"
        assert blank in full, f"{eid}: blank not found in solution: {blank!r}"
        starter = full.replace(blank, "____", 1)
        assert starter != full, f"{eid}: no blank applied"
    else:
        starter = _jp(starter)
        assert starter != full, f"{eid}: starter equals solution"
    assert tests, f"{eid}: needs at least one test"
    # A zero-byte stdin makes `Scanner.nextLine()` throw NoSuchElementException
    # before the program can print anything, so "the empty input" has to be
    # spelled as a blank LINE ("\n"), not as "".
    for (stdin, _out) in tests:
        assert stdin != "", (
            f"{eid}: empty stdin — use \"\\n\" for a blank line, or the Scanner throws"
        )
    hints = list(hints or [])
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "",
        "hints": hints, "language": "java",
        "kind": kind, "difficulty": difficulty,
        "starter": starter, "solution": full, "tests": _tests(tests),
        "source_slug": "", "dataset": "",
    }


def _je(eid, title, prompt, full, blank, tests, hints=(), difficulty="Easy"):
    """A fill-in-the-blank drill."""
    return _jmk(eid, title, prompt, full, tests, hints, difficulty, "drill", blank=blank)


def _jch(eid, title, difficulty, prompt, full, blank, tests, hints=()):
    """A write-the-whole-region coding challenge."""
    return _jmk(eid, title, prompt, full, tests, hints, difficulty, "challenge", blank=blank)


def _jfix(eid, title, prompt, buggy, fixed, tests, hints=(), difficulty="Easy"):
    """A complete but buggy program to correct."""
    return _jmk(eid, title, prompt, fixed, tests, hints, difficulty, "fix", starter=buggy)


def _jlesson(key, title, what, lesson_md, exercises, warmup=None, quiz=None):
    return {"key": key, "title": title, "what": what,
            "lesson": _jp(lesson_md) if lesson_md else "",
            "warmup": warmup or [], "exercises": exercises, "quiz": quiz or []}


def _jcap(title, brief, exercise, example_io="", rubric=None, stretch=None):
    """A judged capstone: the learner writes it, the judge grades it."""
    return {"title": title, "brief": _jp(brief), "kind": "auto",
            "exercise": exercise, "example_io": example_io,
            "rubric": rubric or [], "reference": "", "stretch": stretch}


def _jmod(number, part, part_title, theme, goal, summary, lessons, capstone=None,
          objectives=None, why="", est_minutes=240, glossary=None, cheatsheet="",
          self_check=None, review=None, milestone=""):
    """One module. Field names mirror the shared Rust `CourseWeek` model, so
    `month`/`month_title` carry the PART and `number` carries the MODULE — the
    UI renders them with the course's own `unit_label` / `group_label`."""
    return {
        "number": number, "month": part, "month_title": part_title,
        "theme": theme, "goal": goal, "summary": _jp(summary) if summary else "",
        "authored": True, "lessons": lessons, "capstone": capstone,
        "objectives": objectives or [], "why": why, "est_minutes": est_minutes,
        "glossary": glossary or [], "cheatsheet": _jp(cheatsheet) if cheatsheet else "",
        "self_check": self_check or [], "review": review or [], "milestone": milestone,
    }


_MODULES = []


# ===========================================================================
# The content itself — one file per module, so no single file is unreadable and
# a module can be re-read on its own. Each appends its module to `_MODULES`.
# ===========================================================================

_HERE = os.path.dirname(os.path.abspath(__file__))

_MODULE_FILES = (
    "java_m01_arrays.py",      # Part 1 — arrays in memory
    "java_m02_matrix.py",      #          2D and multidimensional arrays
    "java_m03_sortsearch.py",  #          searching and sorting by hand
    "java_m04_rearrange.py",   #          rearranging and counting
    "java_m05_windows.py",     #          prefix sums, two pointers, windows
    "java_m06_strings.py",     # Part 2 — the object behind the text
    "java_m07_stringapi.py",   #          the String API and classic problems
    "java_m08_builder.py",     #          StringBuilder and StringBuffer
    "java_m09_methods.py",     # Part 3 — methods
    "java_m10_recursion.py",   #          recursion basics
    "java_m11_objects.py",     # Part 4 — classes and objects
    "java_m12_encapsulation.py",  #       encapsulation
    "java_m13_inheritance.py",    #       inheritance and polymorphism
    # Part 4 is not finished: abstract classes, interfaces, composition and
    # association are still to be authored (see JAVA_ROADMAP.md). The scope
    # linter already reserves `abstract `, `interface ` and `implements ` for
    # that module, so nothing earlier can use them in the meantime.
)

for _part_file in _MODULE_FILES:
    _path = os.path.join(_HERE, _part_file)
    if os.path.exists(_path):
        with open(_path, encoding="utf-8") as _f:
            exec(compile(_f.read(), _path, "exec"))

_MODULES.sort(key=lambda m: m["number"])


# ===========================================================================
# SCOPE LINT — enforce "never require an idea a later module teaches".
#
# For each module, scan every program (drills, fixes, challenges, capstones)
# for tokens that belong to a LATER module. `main`'s own signature is stripped
# first, so a bare `static ` really does mean "this program defines a helper
# method" rather than matching main() in every single program.
# ===========================================================================

# (token, first module it may appear in). 999 = banned in this whole course.
_SCOPE_RULES = [
    # --- Parts 6-8 of the roadmap. Using them here would gut those modules. ---
    ("ArrayList", 999), ("HashMap", 999), ("HashSet", 999), ("TreeMap", 999),
    ("LinkedList", 999), ("Collections.", 999), (".stream()", 999),
    ("List<", 999), ("Map<", 999), ("Set<", 999), (" -> ", 999),
    ("Optional", 999),
    # --- Ordering within the shipped parts ---------------------------------
    ("Arrays.sort", 3), ("Arrays.binarySearch", 3),
    ("charAt(", 6), ("substring(", 6), (".equals(", 6),
    (".indexOf(", 7), (".split(", 7), ("String.join", 7),
    ("Character.is", 7), (".toCharArray()", 7),
    ("StringBuilder", 8), ("StringBuffer", 8),
    ("static ", 9),          # a helper method beside main()
    # --- Part 4: objects. A second top-level class in the file is the tell,
    # since `public class Main {` is stripped as scaffolding first.
    ("class ", 11), ("this.", 11), ("private ", 12), ("protected ", 12),
    ("extends ", 13), ("super", 13), ("@Override", 13),
    ("abstract ", 14), ("interface ", 14), ("implements ", 14),
]

# Text that every program (or many early ones) contains and that would trip a
# rule it has nothing to do with: `class Main {` versus the blanket "class "
# ban, and `Arrays.equals(` versus the String-`.equals(` rule. Stripped before
# any rule is applied.
_SCAFFOLD = (
    _MAIN_SIG,
    "public class Main {",
    "class Main {",
    "Arrays.equals(",
    "Arrays.deepEquals(",
)


def _strip_scaffold(prog):
    out = prog
    for text in _SCAFFOLD:
        out = out.replace(text, "")
    return out


def _all_programs(mod):
    out = []
    for l in mod["lessons"]:
        for ex in l["exercises"]:
            out.append((ex["id"], ex["solution"]))
            out.append((ex["id"] + ":starter", ex["starter"]))
    cap = mod.get("capstone")
    if cap:
        for ex in (cap.get("exercise"), cap.get("stretch")):
            if ex:
                out.append((ex["id"], ex["solution"]))
                out.append((ex["id"] + ":starter", ex["starter"]))
    return out


def _lint_scope(mods):
    problems = []
    for m in mods:
        n = m["number"]
        for pid, prog in _all_programs(m):
            body = _strip_scaffold(prog)
            for token, allowed_from in _SCOPE_RULES:
                if n < allowed_from and token in body:
                    where = ("is not part of this course"
                             if allowed_from == 999
                             else f"is not introduced until module {allowed_from}")
                    problems.append(f"Module {n} program {pid} uses {token!r} — it {where}")
    if problems:
        raise AssertionError("Java course scope violations:\n  " + "\n  ".join(problems))


def _lint_ids(mods):
    """Exercise ids are the localStorage keys that record 'solved', so a
    duplicate would silently mark two different exercises done at once."""
    seen = {}
    for m in mods:
        for pid, _ in _all_programs(m):
            eid = pid.split(":starter")[0]
            if eid in seen and seen[eid] != m["number"]:
                raise AssertionError(f"duplicate exercise id {eid!r}")
            seen[eid] = m["number"]


_lint_scope(_MODULES)
_lint_ids(_MODULES)


JAVA_COURSE = {
    "key": "java",
    "title": "Java: After the Basics",
    "subtitle": (
        "You know the syntax — variables, if/else, loops, printing. This is the "
        "part that turns that into fluency: arrays in depth, strings in depth, "
        "methods, and object-oriented programming, in thirteen judged modules. "
        "Each module is a goal, four to six lessons, warm-ups that make you "
        "predict the output, fill-in-the-blank drills, fix-the-bug programs, a "
        "coding challenge, a glossary, a cheat sheet and a project. Nothing ever "
        "needs an idea a later module hasn't taught yet."
    ),
    # The UI is shared with the TypeScript course, which is a *time* ladder
    # (Month 1, Week 3). This one is a *topic* ladder, so it relabels the same
    # two levels rather than pretending a topic takes exactly a week.
    "unit_label": "Module",
    "group_label": "Part",
    "weeks": _MODULES,
}


# Only when run directly. gen_seed.py exec()s this file inside its own
# namespace, where __name__ is already "__main__" — so also check that __file__
# is really this script, or the seed would be written twice per generation.
if __name__ == "__main__" and os.path.basename(__file__) == "java_course.py":
    out = os.path.join(_HERE, "..", "src-tauri", "seeds", "java_course.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(JAVA_COURSE, f, indent=2, ensure_ascii=False)
    n_les = sum(len(m["lessons"]) for m in _MODULES)
    n_ex = sum(len(l["exercises"]) for m in _MODULES for l in m["lessons"])
    n_ex += sum(1 for m in _MODULES if (m.get("capstone") or {}).get("exercise"))
    print(f"Wrote Java course: {len(_MODULES)} modules, {n_les} lessons, "
          f"{n_ex} judged exercises to {os.path.relpath(out)}")
