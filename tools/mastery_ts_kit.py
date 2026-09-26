# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Authoring helpers for the rest of TS_MASTERY_ROADMAP.md: week problem sets
# (X-21), runnable build projects (X-40/X-41/X-42) and more practice.
#
#   _tsp(week, id, title, tier, prompt, body, inputs, hints)
#       A problem-set problem: the stdin scaffold plus one `____` where the
#       whole solution goes. Tier is warm-up / core / stretch (shown as
#       Easy / Medium / Hard). Expected outputs are computed from `body`.
#   _tsp_types(week, id, title, tier, prompt, full, blank, checks, hints)
#       A type-graded problem: `blank` in `full` becomes the `____`, and the
#       hidden `checks` (Expect<Equal<…>> lines) are the tests.
#   _project(week, title, goal, requirements, body, inputs, …)
#       A structured, runnable project brief with acceptance tests computed
#       from the reference implementation `body`.
#
# Every problem and project runs at its week's strictness — `strict`, then
# `strict+indexed` from TS_INDEXED_FROM_WEEK — exactly like the finals.
#
# Content lives in tools/mastery_ts_more_m1.py .. m6.py; mastery_ts_attach.py
# attaches it to TS_WEEKS and checks it. exec()'d by gen_seed.py after
# mastery_ts_practice.py, so `_tl`, `_pr`, `_dx`, `_fx`, `_run`, `_STDIN` and
# `_TW_PRELUDE` exist.
# ---------------------------------------------------------------------------

TS_PROBLEM_SETS = {}   # week -> [exercise]
TS_PROJECTS = {}       # week -> project spec
TS_PRACTICE_MORE = {}  # week -> [exercise], appended to the week's practice
TS_CARDS_MORE = {}     # week -> [(front, back)], review cards for the chapters added later
TS_QUIZ_TOPUP = {}     # week -> [question], raising each week bank towards 40 (X-30)

_TS_TIER = {"warm-up": "Easy", "core": "Medium", "stretch": "Hard"}


def _week_strictness(week):
    return "strict+indexed" if week >= TS_INDEXED_FROM_WEEK else ""


def _tsp(week, eid, title, tier, prompt, body, inputs, hints=()):
    strictness = _week_strictness(week)
    solution = _TS_SCAFFOLD + body.strip("\n") + "\n"
    hints = list(hints)
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "", "hints": hints,
        "language": "typescript", "kind": "challenge", "difficulty": _TS_TIER[tier],
        "strictness": strictness, "harness": "", "judge_mode": "", "forbid": [],
        "starter": _TS_SCAFFOLD + "____\n", "solution": solution,
        "tests": _computed(eid, solution, inputs, strictness),
        "source_slug": "", "dataset": "",
    }


def _tspf(week, eid, title, tier, prompt, solution, blank, driver, inputs, hints=()):
    """A "write the function" problem: `solution` holds the function(s) the
    learner writes, with `blank` becoming the `____`; the hidden `driver` —
    appended exactly as the judge appends a harness — reads stdin, calls them
    and prints. Expected outputs are computed from solution + driver."""
    strictness = _week_strictness(week)
    solution = solution.strip("\n") + "\n"
    assert solution.count(blank) == 1, f"{eid}: blank must appear exactly once"
    driver = driver.strip("\n") + "\n"
    composed = solution.rstrip() + "\n" + driver
    hints = list(hints)
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "", "hints": hints,
        "language": "typescript", "kind": "challenge", "difficulty": _TS_TIER[tier],
        "strictness": strictness, "harness": driver, "judge_mode": "", "forbid": [],
        "starter": solution.replace(blank, "____", 1), "solution": solution,
        "tests": _computed(eid, composed, inputs, strictness),
        "source_slug": "", "dataset": "",
    }


def _tsp_types(week, eid, title, tier, prompt, full, blank, checks, hints=()):
    ex = _tl(eid, title, prompt, full, blank, checks, hints=hints, difficulty=_TS_TIER[tier])
    ex["strictness"] = _week_strictness(week) or "strict"
    return ex


# ---------------------------------------------------------------------------
# Multi-file workspaces (X-45). Mirrors src-tauri/src/tsbundle.rs line for
# line: files are introduced by `// @file name.ts`, sibling imports and export
# lists are dropped, `export` is stripped from declarations, a package import
# repeated across files is kept once, and every dropped or marker line becomes
# a blank line. The judge bundles a learner's workspace with the Rust version;
# expected outputs are computed from this one; verify_mastery.rs judges every
# multi-file reference through the Rust one — so a drift fails a test.
# ---------------------------------------------------------------------------
import re as _bundle_re

_BUNDLE_MARKER = _bundle_re.compile(r"^\s*//\s*@file\s+(\S+)\s*$")
_BUNDLE_DECL = ("declare", "async", "function", "const", "let", "var", "class", "interface", "type",
                "abstract", "enum", "namespace")


def _bundle_quoted_target(text):
    t = text.rstrip().rstrip(";").rstrip()
    if not t or t[-1] not in "\"'":
        return None
    q = t[-1]
    body = t[:-1]
    start = body.rfind(q)
    return None if start < 0 else body[start + 1:]


def _bundle_strip_export(line):
    indent = line[:len(line) - len(line.lstrip())]
    body = line.lstrip()
    if not body.startswith("export"):
        return line
    rest = body[len("export"):]
    if not rest[:1].isspace():
        return line
    rest = rest.lstrip()
    if rest.startswith("default") and rest[len("default"):][:1].isspace():
        rest = rest[len("default"):].lstrip()
    word = _bundle_re.match(r"[A-Za-z]*", rest).group(0)
    return indent + rest if word in _BUNDLE_DECL else line


def _bundle_ts(code):
    """Bundle a `// @file` workspace into one program (see above)."""
    lines = code.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    assert any(_BUNDLE_MARKER.match(l) for l in lines), "not a multi-file workspace"
    out, seen = [], set()
    i = 0
    while i < len(lines):
        line = lines[i]
        if _BUNDLE_MARKER.match(line):
            out.append("")
            i += 1
            continue
        t = line.lstrip()
        is_import = t.startswith("import ") or t.startswith("import{")
        is_export_list = (t.startswith("export {") or t.startswith("export{")
                          or t.startswith("export type {") or t.startswith("export *"))
        if is_import or is_export_list:
            j, text = i, line

            def complete(s):
                return _bundle_quoted_target(s) is not None or (
                    is_export_list and "}" in s and "from" not in s and s.rstrip().endswith((";", "}")))
            while not complete(text) and j + 1 < len(lines) and not _BUNDLE_MARKER.match(lines[j + 1]):
                j += 1
                text += "\n" + lines[j]
            target = _bundle_quoted_target(text)
            if is_export_list:
                drop = True
            elif target is not None and (target.startswith("./") or target.startswith("../")):
                drop = True
            else:
                key = " ".join(text.split())
                drop = key in seen
                seen.add(key)
            for k in range(i, j + 1):
                out.append("" if drop else lines[k])
            i = j + 1
            continue
        out.append(_bundle_strip_export(line))
        i += 1
    return "\n".join(out) + "\n"


_PROJECT_STARTER = (
    "// Build the project here. Read all of stdin from `input` above, and print\n"
    "// exactly what the requirements ask for. Run the tests as you go.\n"
)


def _project(week, title, goal, requirements, body, inputs, stretch=(), rubric=(), starter=None,
             multi_file=False, eid=None):
    """`multi_file`: `body` and `starter` are whole `// @file` workspaces (X-45),
    used as they are — no stdin scaffold is prepended, `main.ts` reads stdin
    itself — and the expected outputs come from the bundled reference."""
    strictness = _week_strictness(week)
    if multi_file:
        solution = body.strip("\n") + "\n"
        return {
            "title": title, "goal": goal.strip(),
            "requirements": list(requirements), "stretch": list(stretch),
            "rubric": list(rubric) or list(_DEFAULT_RUBRIC),
            "language": "typescript",
            "starter": starter.strip("\n") + "\n",
            "solution": solution,
            "tests": _computed(eid or f"project-w{week}", _bundle_ts(solution), inputs, strictness),
            "strictness": strictness,
        }
    solution = _TS_SCAFFOLD + body.strip("\n") + "\n"
    return {
        "title": title, "goal": goal.strip(),
        "requirements": list(requirements), "stretch": list(stretch),
        "rubric": list(rubric) or list(_DEFAULT_RUBRIC),
        "language": "typescript",
        "starter": _TS_SCAFFOLD + (starter.strip("\n") + "\n" if starter else _PROJECT_STARTER),
        "solution": solution,
        "tests": _computed(eid or f"project-w{week}", solution, inputs, strictness),
        "strictness": strictness,
    }


# The self-review every project ends with (X-42). A project may add its own.
_DEFAULT_RUBRIC = [
    "No `any` anywhere — not even one hidden in a cast",
    "Every function has a typed signature; locals are left to inference",
    "Bad input is handled on purpose, not by accident",
    "Names say what things are, not how they are stored",
    "I could explain every line to someone else",
]
