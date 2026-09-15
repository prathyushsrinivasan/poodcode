# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The DSA Curriculum — the Problem Library, taught.
#
# exec()'d inside gen_seed.py's namespace near the end (after the problem bank
# and the concept catalog have been written), and also runnable on its own
# (`python tools/dsa_curriculum.py`) for a fast authoring loop. Defines a
# single global `DSA_CURRICULUM` (dict) which is written to
# src-tauri/seeds/dsa_curriculum.json, served by the `dsa_curriculum` command
# and rendered by src/pages/Library.tsx.
#
# WHAT THIS IS, AND WHAT IT IS NOT
#
# It is NOT a second problem bank. Every problem it schedules already exists in
# seeds/problems.json, and every deep-dive it links already exists in
# seeds/concepts.json. What this file adds is the thing a flat, filterable
# table of 243 problems cannot give you: an ORDER, and a reason for it.
#
# The unit of the curriculum is a UNIT: one technique, taught in the five
# beats that actually move someone from "I have seen this" to "I reach for it
# without thinking":
#
#   1. WHY  — the problem the previous unit leaves behind. A technique nobody
#             needed is a technique nobody remembers.
#   2. MODEL — how it works, in the fewest words that still make it predictable.
#   3. SKELETON — the code shape, in Java, that you should be able to type from
#             memory. Patterns are muscle memory; prose alone does not build it.
#   4. SIGNALS — the routing table: which words in a prompt mean this unit. This
#             is the single most under-taught part of DSA, and the reason people
#             who "know BFS" still fail to see it in a word problem.
#   5. LADDER — the problems, in rungs (warm up → core → variations → stretch),
#             so the next click is always obvious.
#
# Plus the two things that make a unit revisable: PITFALLS (the mistakes, by
# symptom, so a failing run is searchable) and CHECKS (answer-revealing
# questions you can ask yourself a month later).
#
# HARD DESIGN RULES, enforced by `_check_curriculum` at generation time:
#
#   1. EVERY PROBLEM IS PLACED EXACTLY ONCE. The curriculum and the library are
#      the same 243 problems; a problem that belongs to no unit is unreachable
#      by the teaching path, and a problem in two units makes "what is next?"
#      ambiguous. Both fail the build.
#   2. NO DANGLING REFERENCES. Every slug must exist in the problem bank and
#      every lesson key in the concept catalog — a broken link in a teaching
#      page is worse than no link.
#   3. PREREQUISITES POINT BACKWARDS, AND ARE NOT A CHAIN. A unit may only
#      require units that come before it, so the ladder can be walked top to
#      bottom with no jumps — and past the foundations stage, a long run of
#      units whose only prereq is the unit textually before them is rejected.
#      That run is not a dependency graph, it is the absence of one: it makes
#      the "builds on …" banner assert something false (that `tries` builds on
#      `dp-2d`) and it is invisible unless something checks for it.
#   4. RUNGS CLIMB. Within a unit the rungs' difficulty never decreases, so
#      "work down the page" is honest advice.
#
# Progress is NOT stored here and needs no new table: a unit's state is derived
# from the solved status the app already records per problem.
# ---------------------------------------------------------------------------

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))

_STAGES = []
_UNITS = []  # flat, in curriculum order; each carries its stage key


def _md(s):
    """Markdown authored as a column-0 triple-quoted block."""
    return s.lstrip("\n").rstrip() + "\n" if s else ""


def _stage(key, title, icon, tagline, goal):
    _STAGES.append({"key": key, "title": title, "icon": icon,
                    "tagline": tagline, "goal": _md(goal)})
    return key


def _sk(name, when, code, note=""):
    """One entry in a unit's skeleton playbook — the code shape to memorise."""
    return {"name": name, "when": when, "code": code.lstrip("\n").rstrip() + "\n",
            "note": note}


def _sig(when, reach_for, why=""):
    """One row of the signal → technique routing table."""
    return {"when": when, "reach_for": reach_for, "why": why}


def _cost(op, time, space, note=""):
    return {"op": op, "time": time, "space": space, "note": note}


def _pit(symptom, cause, fix):
    """A mistake indexed by its SYMPTOM, so a failing run can be searched."""
    return {"symptom": symptom, "cause": cause, "fix": fix}


def _chk(q, a):
    return {"q": q, "a": a}


def _trace(title, intro, headers, rows, takeaway=""):
    """A worked trace: the structure's state, one step per row.

    Prose is bad at state that changes over time, and every hard thing in the
    linear-structures stage IS state changing over time — what the stack holds
    when an element is popped, where `prev` and `cur` point after each line of a
    reversal, which half of the two heaps an element lands in. A table shows in
    one glance what three paragraphs only assert.

    Generic `headers` + `rows` rather than a fixed shape, because a monotonic
    stack wants (index, value, stack, resolved) and a median stream wants
    (insert, low half, high half, median).
    """
    return {"title": title, "intro": intro, "headers": list(headers),
            "rows": [list(r) for r in rows], "takeaway": takeaway}


def _rung(title, purpose, slugs, notes=None):
    return {"title": title, "purpose": purpose, "slugs": list(slugs),
            "notes": notes or {}}


def _unit(key, title, icon, stage, tagline, why, model,
          prereqs=(), signals=(), skeletons=(), costs=(), pitfalls=(),
          lessons=(), checks=(), interview="", rungs=(), next_up="",
          internals="", traces=(), build_it=""):
    """One technique, taught.

    `internals`, `traces` and `build_it` are optional depth, and they exist
    because a unit about a *data structure* has to answer a question a unit
    about a *technique* does not: why are these the costs? A learner who has
    never seen a heap's array layout is memorising "O(log n) insert" rather
    than understanding it, and the memory fails under interview pressure in a
    way the understanding does not.

      * `internals` — how the structure works underneath, and which Java class
        actually implements it.
      * `traces`    — the state, step by step (see `_trace`).
      * `build_it`  — write it from scratch, which is the only way the costs
        stop being trivia.
    """
    _UNITS.append({
        "key": key,
        "title": title,
        "icon": icon,
        "stage": stage,
        "tagline": tagline,
        "prereqs": list(prereqs),
        "why": _md(why),
        "model": _md(model),
        "internals": _md(internals),
        "signals": list(signals),
        "skeletons": list(skeletons),
        "traces": list(traces),
        "costs": list(costs),
        "pitfalls": list(pitfalls),
        "lessons": list(lessons),
        "checks": list(checks),
        "interview": _md(interview),
        "rungs": list(rungs),
        "build_it": _md(build_it),
        "next_up": _md(next_up),
    })


# ---------------------------------------------------------------------------
# Content — one file per stage, exec'd in order into this namespace. Each
# appends its stage and its units, so the flat `_UNITS` list is already in
# curriculum order by the time the lints run.
# ---------------------------------------------------------------------------

for _name in (
    "dsa_s1_foundations.py",
    "dsa_s2_patterns.py",
    "dsa_s3_search.py",
    "dsa_s4_structures.py",
    "dsa_s5_hierarchies.py",
    "dsa_s6_advanced.py",
):
    _p = os.path.join(_HERE, _name)
    if os.path.exists(_p):
        with open(_p, encoding="utf-8") as _f:
            exec(compile(_f.read(), _p, "exec"))


DSA_CURRICULUM = {
    "key": "dsa",
    "title": "DSA Curriculum",
    "subtitle": "Every problem in the library, in the order that teaches it.",
    "intro": _md("""
This is the problem bank with a **spine**. The same problems, the same judge —
but arranged as a course that starts at `System.out.println` and ends at
tries, Dijkstra and 2-D dynamic programming.

**How to use it.** Work top to bottom. Open a unit, read *Why this exists* and
*The model*, copy the skeleton out by hand once, then climb the rungs. A rung
is a group of problems that drill the same twist; when a rung stops being
interesting, move on — you do not have to clear every problem to progress.

**What "done" means here.** A unit turns green when you have solved most of its
core rungs, but the number is not the point: the point is that when you next
read a prompt with the words *"contiguous subarray"* in it, your hands start
typing a sliding window before you have finished the sentence. The **Signals**
table in each unit is that reflex, written down.

**Where the depth is.** Each unit links the full lesson for its technique in
**Learn** — that is where the derivations, the worked examples and the
language-level detail live. The unit page is the map; Learn is the terrain.
"""),
    "stages": [],
}


def _assemble():
    by_stage = {}
    for u in _UNITS:
        by_stage.setdefault(u["stage"], []).append(u)
    out = []
    for i, st in enumerate(_STAGES):
        units = by_stage.get(st["key"], [])
        out.append({**st, "ordering": i, "units": units})
    DSA_CURRICULUM["stages"] = out
    return DSA_CURRICULUM


# ---------------------------------------------------------------------------
# Generation-time lints. A curriculum whose links are broken or whose ladder
# skips a rung is worse than no curriculum, so these are assertions, not
# warnings: the build fails.
# ---------------------------------------------------------------------------

_DIFF_RANK = {"Intro": 0, "Easy": 1, "Medium": 2, "Hard": 3}

# How many units in a row may name nothing but their immediate predecessor
# before the "prereqs" column stops being a dependency graph. Foundations
# genuinely chains — you cannot loop before you can branch — so the check is
# scoped to stages 2+, where a run this long means the field was filled in by
# position rather than by thought.
_MAX_CHAIN_RUN = 2


def _check_curriculum(cur, concepts, problems):
    """`concepts` maps key → concept; `problems` maps slug → problem dict."""
    seen_units = set()
    seen_slugs = {}
    order = []
    chain_run = 0  # consecutive units whose prereqs are exactly [previous unit]

    for si, stage in enumerate(cur["stages"]):
        assert stage["units"], f"stage {stage['key']}: no units"
        for u in stage["units"]:
            key = u["key"]
            assert key not in seen_units, f"duplicate unit {key!r}"
            seen_units.add(key)
            order.append(key)

            assert u["why"], f"{key}: no 'why this exists'"
            assert u["model"], f"{key}: no mental model"
            assert u["rungs"], f"{key}: no problem ladder"
            assert u["checks"], f"{key}: no self-check questions"

            # A trace is only worth reading if every row is the same shape as
            # the header — a ragged one renders as a broken table.
            for t in u["traces"]:
                assert t["headers"], f"{key}: trace {t['title']!r} has no headers"
                assert len(t["rows"]) >= 2, \
                    f"{key}: trace {t['title']!r} needs at least two steps to show change"
                for i, row in enumerate(t["rows"]):
                    assert len(row) == len(t["headers"]), (
                        f"{key}: trace {t['title']!r} row {i} has {len(row)} cells, "
                        f"expected {len(t['headers'])}"
                    )

            # Rule 3 — prerequisites point backwards…
            for p in u["prereqs"]:
                assert p in seen_units, \
                    f"{key}: prerequisite {p!r} is not an earlier unit"

            # …and, past foundations, are not merely the chain. Counted as a run
            # rather than per unit because a single chain link is often the true
            # answer (`trees` really does build on `recursion` alone); it is
            # several in a row that means nobody wrote the graph down.
            if si > 0 and len(order) >= 2 and u["prereqs"] == [order[-2]]:
                chain_run += 1
                assert chain_run <= _MAX_CHAIN_RUN, (
                    f"{key}: {chain_run} units in a row list only the unit before them "
                    f"as a prerequisite. That is a chain, not a dependency graph — give "
                    f"each of these its real prereqs (see the 'builds on …' banner)."
                )
            else:
                chain_run = 0

            # Rule 2 — no dangling references.
            for lk in u["lessons"]:
                assert lk in concepts, f"{key}: unknown concept key {lk!r}"

            last_rank = -1
            for r in u["rungs"]:
                assert r["slugs"], f"{key}/{r['title']}: empty rung"
                assert r["purpose"], f"{key}/{r['title']}: no purpose"
                ranks = []
                for slug in r["slugs"]:
                    assert slug in problems, \
                        f"{key}/{r['title']}: unknown problem slug {slug!r}"
                    # Rule 1 — placed exactly once.
                    assert slug not in seen_slugs, \
                        f"{slug!r} is in both {seen_slugs[slug]!r} and {key!r}"
                    seen_slugs[slug] = key
                    ranks.append(_DIFF_RANK[problems[slug]["difficulty"]])
                for slug in r["notes"]:
                    assert slug in r["slugs"], \
                        f"{key}/{r['title']}: note for {slug!r}, which is not in the rung"
                # Rule 4 — rungs climb. Compared on the rung's *hardest*
                # problem, so a rung may open with an easy warm-up of its own.
                rank = max(ranks)
                assert rank >= last_rank, (
                    f"{key}: rung {r['title']!r} is easier than the rung before it"
                )
                last_rank = rank

    # Rule 1, the other half — every problem is reachable from the curriculum.
    unplaced = sorted(set(problems) - set(seen_slugs))
    assert not unplaced, (
        f"{len(unplaced)} problem(s) belong to no unit: {unplaced[:12]}"
        + (" …" if len(unplaced) > 12 else "")
    )
    return len(seen_units), len(seen_slugs)


# Only when run directly. gen_seed.py exec()s this file inside its own
# namespace, where __name__ is already "__main__" — so also check __file__.
if __name__ == "__main__" and os.path.basename(__file__) == "dsa_curriculum.py":
    _assemble()
    _seeds = os.path.join(_HERE, "..", "src-tauri", "seeds")
    with open(os.path.join(_seeds, "problems.json"), encoding="utf-8") as f:
        _problems = {p["slug"]: p for p in json.load(f)}
    with open(os.path.join(_seeds, "concepts.json"), encoding="utf-8") as f:
        _concepts = {c["key"]: c for c in json.load(f)}
    n_units, n_slugs = _check_curriculum(DSA_CURRICULUM, _concepts, _problems)
    out = os.path.join(_seeds, "dsa_curriculum.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(DSA_CURRICULUM, f, indent=2, ensure_ascii=False)
    print(f"Wrote DSA curriculum: {len(DSA_CURRICULUM['stages'])} stages, "
          f"{n_units} units, {n_slugs} problems placed to {os.path.relpath(out)}")
