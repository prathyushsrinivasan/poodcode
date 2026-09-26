# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Hint ladders for every TypeScript exercise (TS_MASTERY_ROADMAP.md X-18):
# nudge → strategy → near-answer, revealed one at a time.
#
# The authored hint stays the first rung. Exercises with fewer than two get the
# missing rungs derived from their own reference solution, so a derived hint
# can never disagree with the answer:
#
#   strategy     for a whole-solution blank: the building blocks the reference
#                uses ("`split`, a `Map` and `toSorted`")
#   near-answer  for a blank: how its answer begins; for a program to repair
#                (fix, diagnose, retype, refactor): the line that changes
#
# `_ts_ladder(ex)` tops up one exercise. exec()'d by gen_seed.py after the
# TypeScript chapters (it tops up the Learn exercises at once); the Mastery
# weeks call it from mastery_ts_scope.py, the last Mastery file.
# ---------------------------------------------------------------------------

import difflib as _tsh_difflib

_TSH_BLOCKS = [
    (".split(", "`split`"), ("new Map", "a `Map`"), ("new Set", "a `Set`"), (".reduce(", "`reduce`"),
    (".map(", "`map`"), (".filter(", "`filter`"), (".toSorted(", "`toSorted`"), (".sort(", "`sort`"),
    (".join(", "`join`"), (".slice(", "`slice`"), ("JSON.parse(", "`JSON.parse`"), ("switch (", "a `switch`"),
    ("while (", "a `while` loop"), ("for (", "a `for` loop"), ("Math.", "`Math`"), (".padStart(", "`padStart`"),
    (".localeCompare(", "`localeCompare`"), ("Object.entries(", "`Object.entries`"), ("?? ", "`??`"),
    ("class ", "a class"), ("function* ", "a generator"), ("await ", "`await`"), ("try {", "`try`/`catch`"),
]


def _tsh_blank_answer(starter, solution):
    i = starter.find("____")
    if i < 0:
        return None
    pre, post = starter[:i], starter[i + 4:]
    if not solution.startswith(pre) or not solution.endswith(post) or len(pre) + len(post) > len(solution):
        return None
    return solution[len(pre):len(solution) - len(post)]


def _tsh_changed_line(starter, solution):
    a = starter.rstrip("\n").split("\n")
    b = solution.rstrip("\n").split("\n")
    for tag, i1, _i2, _j1, _j2 in _tsh_difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag != "equal":
            return min(i1 + 1, len(a))
    return None


def _tsh_rungs(ex):
    """(strategy, near-answer) for one exercise; either may be None."""
    answer = _tsh_blank_answer(ex["starter"], ex["solution"])
    if answer is not None:
        answer = answer.strip("\n")
        lines = [ln for ln in answer.split("\n") if ln.strip()]
        if len(lines) > 1:
            used = [name for token, name in _TSH_BLOCKS if token in answer]
            strategy = None
            if used:
                listed = ", ".join(used[:-1]) + (" and " + used[-1] if len(used) > 1 else used[0])
                strategy = f"The reference solution uses {listed}."
            first = lines[0].strip()
            near = f"The reference solution is {len(lines)} lines and begins: `{first}`"
            return strategy, near
        text = answer.strip()
        words = text.split()
        if len(words) > 1:
            shown = " ".join(words[: (len(words) + 1) // 2])
            return None, f"The answer begins `{shown} …`"
        if len(text) > 2:
            return None, f"The answer is {len(text)} characters long and begins `{text[: len(text) // 2]}`."
        return None, None
    line = _tsh_changed_line(ex["starter"], ex["solution"])
    if line is not None:
        return None, f"The change starts on line {line} of the program."
    return None, None


def _ts_ladder(ex):
    if ex.get("kind") in ("spot", "order"):
        return ex
    hints = list(ex.get("hints") or ([ex["hint"]] if ex.get("hint") else []))
    if len(hints) >= 2:
        return ex
    strategy, near = _tsh_rungs(ex)
    for rung in (strategy, near):
        if rung and rung not in hints:
            hints.append(rung)
    ex["hints"] = hints
    ex["hint"] = hints[0] if hints else ""
    return ex


for _tsh_key, _tsh_c in CONCEPTS.items():
    if _tsh_c.get("language") == "typescript":
        for _tsh_ex in EXERCISES.get(_tsh_key, []):
            _ts_ladder(_tsh_ex)
