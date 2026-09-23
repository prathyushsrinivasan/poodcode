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


_PROJECT_STARTER = (
    "// Build the project here. Read all of stdin from `input` above, and print\n"
    "// exactly what the requirements ask for. Run the tests as you go.\n"
)


def _project(week, title, goal, requirements, body, inputs, stretch=(), rubric=(), starter=None):
    strictness = _week_strictness(week)
    solution = _TS_SCAFFOLD + body.strip("\n") + "\n"
    return {
        "title": title, "goal": goal.strip(),
        "requirements": list(requirements), "stretch": list(stretch),
        "rubric": list(rubric) or list(_DEFAULT_RUBRIC),
        "language": "typescript",
        "starter": _TS_SCAFFOLD + (starter.strip("\n") + "\n" if starter else _PROJECT_STARTER),
        "solution": solution,
        "tests": _computed(f"project-w{week}", solution, inputs, strictness),
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
