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
# table of 615 problems cannot give you: an ORDER, and a reason for it.
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
#      the same 615 problems; a problem that belongs to no unit is unreachable
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
#   5. EVERY SUBSTANTIAL UNIT OPENS BELOW ITS CEILING. Rule 4 compares each
#      rung's *hardest* problem, so a unit that starts at Medium and stays
#      there passes it cleanly — which is how a dozen units came to label their
#      first rung "Warm up" while opening at their own maximum difficulty. A
#      unit with more than four problems must open with an Intro or an Easy.
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


def _stage(key, title, icon, tagline, goal, optional=False, router=(), cheatsheet=""):
    """One stage. `optional` marks a stage beyond the interview core: the app
    leaves it out of the course's overall progress and does not send "Continue"
    into it until the core is done. Optional stages must come last (see
    `_check_curriculum`), so the core can always be walked top to bottom without
    stepping through one.

    `router` is the stage's own routing table (see `_route`). A unit's `signals`
    answer "does THIS technique apply?", which is the question you can only ask
    once you have guessed the technique. The stage router answers the question
    that actually comes first: *given this prompt, which of these units is it?*
    Nothing else in the curriculum answers that, and on a stage whose six units
    all take an array and return a number, it is the entire difficulty.
    """
    _STAGES.append({"key": key, "title": title, "icon": icon,
                    "tagline": tagline, "goal": _md(goal), "optional": bool(optional),
                    "router": list(router), "cheatsheet": _md(cheatsheet)})
    return key


def _route(when, unit, why, not_when=""):
    """One row of a stage's routing table: a prompt shape → the unit that owns it.

    `not_when` is the near miss — the phrasing that looks like this row and is
    not. Confusable pairs are where the time actually goes ("longest substring
    with at most k distinct" is a window; "count substrings with exactly k
    distinct" is two windows subtracted), so the row that does not say what it
    excludes is only half a routing rule.
    """
    return {"when": when, "unit": unit, "why": why, "not_when": not_when}


def _sk(name, when, code, note=""):
    """One entry in a unit's skeleton playbook — the code shape to memorise."""
    return {"name": name, "when": when, "code": code.lstrip("\n").rstrip() + "\n",
            "note": note}


def _sig(when, reach_for, why=""):
    """One row of the signal → technique routing table."""
    return {"when": when, "reach_for": reach_for, "why": why}


def _inv(statement, established, maintained, at_exit, note=""):
    """A unit's loop invariant, stated as the four parts that make it a proof.

    Every technique in the patterns stage is a loop that refuses to re-read what
    it has already seen, and the *reason* each one is allowed to is an invariant
    — a sentence that is true before the loop, stays true across one iteration,
    and at exit is strong enough to be the answer. That sentence is what the
    units currently assert in passing and never state.

    It is four fields rather than a paragraph because the paragraph is where the
    parts go missing, and the missing part is always the same one: people can
    state the invariant and cannot say why moving the pointer *preserves* it,
    which is exactly the step that makes discarding half the search space legal.

      * `statement`   — the sentence, precisely, in terms of the variables.
      * `established` — why it is true before the first iteration.
      * `maintained`  — why one iteration leaves it true. The load-bearing part.
      * `at_exit`     — what it gives you once the loop condition fails.
    """
    return {"statement": statement, "established": established,
            "maintained": maintained, "at_exit": at_exit, "note": note}


def _var(name, change, when, cost, gotcha=""):
    """One member of a technique's family: the skeleton with ONE thing changed.

    The patterns stage does not really teach six techniques. It teaches six
    skeletons and about thirty problems that are each of those skeletons with a
    single line different — and a learner who has solved "longest substring with
    at most k distinct" has *not* thereby learned "count substrings with exactly
    k distinct", because nothing told them the second is the first, run twice,
    subtracted.

    `change` is the edit, stated as an edit. That is the whole point of the
    field: a table of related problems is a reading list, while a table of
    *diffs* is a technique.
    """
    return {"name": name, "change": change, "when": when, "cost": cost,
            "gotcha": gotcha}


def _rw(title, slow, fast, edit, why):
    """The slow version, the fast version, and the one edit between them.

    This stage's thesis is "stop re-reading what you have already seen", and the
    honest way to teach it is to show the re-reading and then delete it. A
    learner shown only the fast version has no idea which part of it is the
    trick; shown both, the diff *is* the lesson, and it is one line often
    enough that seeing it once is worth a page of prose.

    `edit` is that line, named in words. `why` is the complexity argument for
    why the edit is allowed — not that it is faster, but why it does not lose
    an answer.
    """
    return {"title": title, "slow": slow.lstrip("\n").rstrip() + "\n",
            "fast": fast.lstrip("\n").rstrip() + "\n", "edit": edit,
            "why": _md(why)}


def _cost(op, time, space, note=""):
    return {"op": op, "time": time, "space": space, "note": note}


def _pit(symptom, cause, fix):
    """A mistake indexed by its SYMPTOM, so a failing run can be searched."""
    return {"symptom": symptom, "cause": cause, "fix": fix}


def _chk(q, a):
    return {"q": q, "a": a}


def _bigo(code, answer, options, why):
    """One "what is the Big-O of this snippet?" item, graded.

    The complexity unit had three problems and no way to practise the thing it
    teaches: you can solve every problem in it without ever once *stating* a
    complexity, which is the opposite of the skill. Reading a snippet and
    pricing it is a drill, not a problem — it takes fifteen seconds and there is
    nothing to submit to a judge — so it lives on the unit page and is scheduled
    like a self-check.

    `why` is required. An answer without the reason it is the answer teaches the
    answer, and the answers are memorable enough to survive without the
    understanding.
    """
    assert answer in options, f"Big-O item answer {answer!r} is not among its options"
    return {"code": code.lstrip("\n").rstrip() + "\n", "answer": answer,
            "options": list(options), "why": _md(why)}


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


_QUIZ_KINDS = {"bug": "Spot the bug", "predict": "Predict the result"}


def _quiz(kind, prompt, code, answer, options, why):
    """A graded multiple-choice drill over a code fragment.

    The other drills ask you to recall (self-checks), to price (Big-O) or to
    classify (the family drill). None of them hands you *broken* code — and the
    commonest failure in a technique whose code is eight lines long is a
    one-character boundary bug. Two kinds:

      * `bug`     — the snippet is wrong; which change fixes it?
      * `predict` — the snippet is right; what does it return or leave behind?

    Scheduled like the Big-O cards (`dsa-quiz:<unit>:<i>`), and `why` is
    required for the same reason.
    """
    assert kind in _QUIZ_KINDS, f"quiz kind {kind!r} is not one of {sorted(_QUIZ_KINDS)}"
    assert answer in options, f"quiz answer {answer!r} is not among its options"
    return {"kind": kind, "prompt": prompt, "code": code.lstrip("\n").rstrip() + "\n",
            "answer": answer, "options": list(options), "why": _md(why)}


def _stuck(when, ask):
    """One row of a unit's "stuck?" triage: the moment BEFORE any code exists.

    Pitfalls are indexed by the symptom of a failed run, which presumes a run.
    The learner this serves has read the prompt and has no idea — and the help
    that works then is not an answer but the question that produces one.
    """
    return {"when": when, "ask": ask}


def _edge(slug, case, input, breaks):
    """An edge case worth testing before you submit: a ready-to-paste stdin
    `input` for the problem `slug` (on this unit's ladder, so the input format
    is real and the case can be run against its reference), and the bug it
    `breaks`. The hidden tests are built from exactly these, and naming them
    beforehand is cheaper than a wrong submission."""
    return {"slug": slug, "case": case, "input": input.lstrip("\n"), "breaks": breaks}


_WALK_STEPS = ("Read", "Route", "Brute force", "Insight", "Code", "Test and price")


def _walk(slug, title, steps):
    """One problem solved start to finish, in six fixed steps.

    The model explains the technique and the ladder hands you problems; nothing
    in between shows one problem travelling the whole road — prompt, routing,
    the slow version, the observation, the code, and the test cases and cost.
    The steps are fixed so every walkthrough is read the same way. `steps` is a
    list of markdown bodies, one per name in `_WALK_STEPS`.
    """
    assert len(steps) == len(_WALK_STEPS), \
        f"walkthrough {slug}: {len(steps)} steps, expected {len(_WALK_STEPS)}"
    return {"slug": slug, "title": title,
            "steps": [{"name": n, "body": _md(b)} for n, b in zip(_WALK_STEPS, steps)]}


def _rung(title, purpose, slugs, notes=None, optional=False):
    """One step of a unit's ladder.

    `optional` marks a rung the unit does not *ask* of you — the surplus a unit
    accumulated because the bank happened to contain sixteen tree problems, not
    because sixteen is what learning trees takes. It stays reachable and stays
    on the page; it just does not count toward the unit's total until you start
    it (see `hydrate` in src/lib/curriculum.ts). Deleting those problems would
    be the wrong fix: nothing is wrong with them, they simply should not be what
    stands between you and the next technique.
    """
    return {"title": title, "purpose": purpose, "slugs": list(slugs),
            "notes": notes or {}, "optional": bool(optional)}


def _extra(title, purpose, slugs, notes=None):
    """An optional rung — `_rung(..., optional=True)`, named so the authoring
    files read as what they are and the flag cannot be lost in a long call."""
    return _rung(title, purpose, slugs, notes, optional=True)


def _unit(key, title, icon, stage, tagline, why, model,
          prereqs=(), signals=(), skeletons=(), costs=(), pitfalls=(),
          lessons=(), checks=(), interview="", rungs=(), next_up="",
          internals="", traces=(), build_it="", weight=2, bigo=(),
          invariant=None, variants=(), rewrites=(), quizzes=(), stuck=(),
          edge_cases=(), walkthrough=None):
    """One technique, taught.

    `weight` is **interview yield**, 1-3, and it exists to stop the bank's
    accidental distribution from defining the syllabus. "Every problem placed
    exactly once" is the right rule for reachability, but on its own it meant
    `sliding-window` got two problems and `trees` got sixteen — a ratio that
    reflects which problems somebody happened to author, not which technique is
    worth eight times the time. Each weight carries a target problem-count band
    (`_WEIGHT_BANDS`), reported as a ledger at generation time rather than
    asserted; see `_check_weight_bands` for why it is a warning.

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
    assert weight in (1, 2, 3), f"{key}: weight must be 1, 2 or 3 (got {weight!r})"
    _UNITS.append({
        "key": key,
        "title": title,
        "icon": icon,
        "stage": stage,
        "tagline": tagline,
        "weight": weight,
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
        "bigo": list(bigo),
        "interview": _md(interview),
        "rungs": list(rungs),
        "build_it": _md(build_it),
        "next_up": _md(next_up),
        # `None` rather than {} so the frontend's "does this unit have one?"
        # test is a null check and not a key count.
        "invariant": dict(invariant) if invariant else None,
        "variants": list(variants),
        "rewrites": list(rewrites),
        "quizzes": list(quizzes),
        "stuck": list(stuck),
        "edge_cases": list(edge_cases),
        "walkthrough": dict(walkthrough) if walkthrough else None,
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
    "dsa_s4_numbers.py",
    "dsa_s5_structures.py",
    "dsa_s6_hierarchies.py",
    "dsa_s7_dp.py",
    "dsa_s8_beyond.py",
    "dsa_s8_more.py",
):
    _p = os.path.join(_HERE, _name)
    if os.path.exists(_p):
        with open(_p, encoding="utf-8") as _f:
            exec(compile(_f.read(), _p, "exec"))

# Cross-cutting content, authored per concern rather than per stage and attached
# to units by key: where the batched problems sit on each ladder, the Big-O
# drills every unit carries, and the worked traces. Required, not optional — the
# lints below fail the build if a unit loses them.
for _name in ("dsa_placements.py", "dsa_syllabus.py", "dsa_bigo.py", "dsa_traces.py",
              "dsa_s3_depth.py", "dsa_s3_help.py"):
    _p = os.path.join(_HERE, _name)
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

_RANK_NAME = {v: k for k, v in _DIFF_RANK.items()}

# A unit with this many problems or fewer is exempt from the on-ramp rule: it
# is too short to wall anyone off, and inventing an Easy problem to satisfy a
# lint would be the tail wagging the dog.
_ONRAMP_MIN_UNIT = 4

# Target problem count per `weight` — how much of a learner's time a technique
# should get, given how often it decides an interview. Counted over the rungs a
# unit actually *asks* of you, so an "Extra practice" rung does not paper over
# a thin unit or inflate an overweight one.
_WEIGHT_BANDS = {3: (8, 14), 2: (5, 9), 1: (3, 6)}

# The fewest Big-O drill items a unit may carry.
_MIN_BIGO = 4

# Units whose optional-depth fields are no longer optional.
#
# `internals`, `traces` and `build_it` started as a linear-structures-stage
# thing, on the argument that a unit about a *structure* has to answer "why are
# these the costs?" while a unit about a technique does not. That argument is
# only half right: the question a trace answers is "what is the state, step by
# step", and the places where the state is hardest to hold in prose are
# Dijkstra's queue, a DP table, a backtracking stack and a DSU forest — none of
# which are in that stage.
#
# Listed explicitly rather than derived, because "which units need internals" is
# a pedagogical judgement. The point of the list is that authored depth cannot
# silently disappear.
#
# Traces are the exception: every unit now has at least one (tools/dsa_traces.py
# covers the ones the stage files did not), including `io-and-arithmetic`, whose
# state turned out to be the *type* of each intermediate result. So the rule is
# simply "every unit", checked where the lint runs.
_NEEDS_INTERNALS = {
    "hashing", "binary-search", "stacks", "queues-and-deques", "linked-lists",
    "heaps", "design", "trees", "tries",
    # Not a data structure, but the unit with the most machinery hidden behind
    # ordinary-looking syntax: immutability, a copying `substring`, `+=` that is
    # quadratic, and a `char` that is not a character.
    "strings",
    # Order & Search: the call stack is recursion's hidden cost, and "which
    # algorithm does Arrays.sort run" decides stability and the worst case.
    "recursion", "sorting",
}
_NEEDS_BUILD_IT = {
    "stacks", "queues-and-deques", "linked-lists", "heaps", "design",
    "union-find", "tries", "dp-1d",
    # The patterns stage: every one of these is a loop you should be able to
    # write from an empty file, and "I have read it" is not that.
    "complexity", "hashing", "two-pointers", "sliding-window", "prefix-sums",
    "strings",
    "recursion", "sorting", "binary-search", "greedy", "intervals",
}

# Units whose whole correctness argument is a loop invariant (see `_inv`).
#
# Scoped deliberately rather than applied everywhere: a unit about a *structure*
# is explained by its layout (`internals`), and a unit about a *table* by its
# recurrence. These are the ones where the question "why is it allowed to skip
# the rest of the search space?" has no other answer, and where leaving it
# unstated is how people end up moving the wrong pointer.
_NEEDS_INVARIANT = {"two-pointers", "sliding-window", "prefix-sums", "hashing",
                    # Order & Search: induction, the partition regions, the
                    # half-open search, stays-ahead, and merge's "last block".
                    "recursion", "sorting", "binary-search", "greedy", "intervals"}

# Units that must carry a family table (see `_var`) and a slow-vs-fast rewrite
# (see `_rw`). The patterns stage is where both pay most: its six skeletons
# account for most Easy/Medium array problems, and the difference between two
# of its problems is usually one line.
_NEEDS_VARIANTS = {
    "complexity", "hashing", "two-pointers", "sliding-window", "prefix-sums",
    "strings",
    # Order & Search. Each unit is a handful of skeletons whose problems differ
    # by one line — first-true vs last-true, sort by start vs by end.
    "recursion", "sorting", "binary-search", "greedy", "intervals",
}
_NEEDS_REWRITES = dict.fromkeys(_NEEDS_VARIANTS)

# Units that must carry the round-2 help layer: spot-the-bug / predict drills,
# a "stuck?" triage, an edge-case checklist and one worked solution. Started on
# Order & Search, where boundary bugs are the commonest failure.
_NEEDS_HELP = {"recursion", "sorting", "binary-search", "greedy", "intervals"}
_MIN_HELP = 4

# The fewest family rows a unit carrying a family table may have. Two is a
# comparison; one is a claim.
_MIN_VARIANTS = 3


def _check_curriculum(cur, concepts, problems):
    """`concepts` maps key → concept; `problems` maps slug → problem dict."""
    seen_units = set()
    seen_titles = {}
    seen_slugs = {}
    order = []
    chain_run = 0  # consecutive units whose prereqs are exactly [previous unit]
    weights = {}   # unit key -> (weight, required problems, total problems)
    stage_of = {}  # unit key -> stage index, so the ledger can skip foundations
    linked_concepts = set()

    seen_optional_stage = None
    for si, stage in enumerate(cur["stages"]):
        assert stage["units"], f"stage {stage['key']}: no units"

        # The stage router. Its rows must point at units of *this* stage: a row
        # sending you to a unit three stages away is not a routing rule for the
        # stage, it is a cross-reference, and it would render as a dead chip.
        stage_unit_keys = {x["key"] for x in stage["units"]}
        seen_routes = set()
        for r in stage.get("router", []):
            assert r["unit"] in stage_unit_keys, (
                f"stage {stage['key']}: router row {r['when']!r} points at "
                f"{r['unit']!r}, which is not a unit of this stage"
            )
            for part in ("when", "why"):
                assert r.get(part, "").strip(), \
                    f"stage {stage['key']}: router row for {r['unit']!r} has no {part!r}"
            assert r["when"] not in seen_routes, \
                f"stage {stage['key']}: two router rows for {r['when']!r}"
            seen_routes.add(r["when"])
        # Optional stages sit after the whole core. A core stage after an optional
        # one would make "finish the core" require walking through optional work.
        if stage.get("optional"):
            seen_optional_stage = stage["key"]
        else:
            assert seen_optional_stage is None, (
                f"stage {stage['key']}: a core stage follows the optional stage "
                f"{seen_optional_stage!r} — optional stages must come last"
            )
        for u in stage["units"]:
            key = u["key"]
            assert key not in seen_units, f"duplicate unit {key!r}"
            seen_units.add(key)
            order.append(key)
            stage_of[key] = si

            # Titles must be unique, not merely keys. The recognition drill
            # (src/lib/dsaRecognition.ts) uses a unit's title as its answer in a
            # multiple-choice routing question, so two units sharing one would
            # make that question unanswerable — a failure that would show up as
            # a confusing quiz rather than as an error.
            assert u["title"] not in seen_titles, (
                f"{key}: title {u['title']!r} is also used by "
                f"{seen_titles[u['title']]!r} — the recognition drill offers titles as "
                f"answers, so they have to identify a unit on their own"
            )
            seen_titles[u["title"]] = key

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
                linked_concepts.add(lk)

            # Big-O drill items. Every unit prices its own snippets (see
            # tools/dsa_bigo.py for why this is not just the complexity unit).
            assert len(u["bigo"]) >= _MIN_BIGO, (
                f"{key}: {len(u['bigo'])} Big-O item(s), fewer than {_MIN_BIGO} — every "
                f"unit's Review tab prices the traps specific to its technique"
            )
            for i, b in enumerate(u["bigo"]):
                assert b["code"].strip(), f"{key}: Big-O item {i} has no snippet"
                assert len(b["options"]) >= 3, \
                    f"{key}: Big-O item {i} has {len(b['options'])} options — fewer than " \
                    f"three is a coin toss"
                assert len(set(b["options"])) == len(b["options"]), \
                    f"{key}: Big-O item {i} repeats an option"
                assert b["answer"] in b["options"], \
                    f"{key}: Big-O item {i} answer is not among its options"
                assert b["why"].strip(), (
                    f"{key}: Big-O item {i} has no explanation. The answers are memorable "
                    f"enough to survive without the understanding, which is the failure."
                )

            # Authored depth cannot regress.
            if key in _NEEDS_INTERNALS:
                assert u["internals"].strip(), \
                    f"{key}: no internals — what layout are its costs a consequence of?"
            assert u["traces"], (
                f"{key}: no worked trace. Every unit is state changing over time, "
                f"which is the one thing prose cannot show and a table can."
            )
            if key in _NEEDS_BUILD_IT:
                assert u["build_it"].strip(), \
                    f"{key}: no build-it-yourself exercise"

            # The loop invariant. Checked field by field, because the part that
            # goes missing is always `maintained` — and a unit that states the
            # invariant without saying why one iteration preserves it has
            # asserted the conclusion and skipped the proof.
            inv = u["invariant"]
            if key in _NEEDS_INVARIANT:
                assert inv, (
                    f"{key}: no loop invariant. This unit's correctness argument IS an "
                    f"invariant; without it the rule for which pointer to move is a "
                    f"memorised coin flip."
                )
            if inv:
                for part in ("statement", "established", "maintained", "at_exit"):
                    assert inv.get(part, "").strip(), (
                        f"{key}: invariant is missing {part!r} — all four parts or none, "
                        f"since three of them do not prove anything"
                    )

            # The family table.
            if key in _NEEDS_VARIANTS:
                assert len(u["variants"]) >= _MIN_VARIANTS, (
                    f"{key}: {len(u['variants'])} variant(s), fewer than {_MIN_VARIANTS}. "
                    f"Most problems in this unit are its skeleton with one line changed; "
                    f"a table of fewer than three is not a family."
                )
            seen_variants = set()
            for v in u["variants"]:
                for part in ("name", "change", "when", "cost"):
                    assert v.get(part, "").strip(), \
                        f"{key}: variant {v.get('name', '?')!r} has no {part!r}"
                assert v["name"] not in seen_variants, \
                    f"{key}: two variants named {v['name']!r}"
                seen_variants.add(v["name"])

            # Slow-vs-fast rewrites.
            if key in _NEEDS_REWRITES:
                assert u["rewrites"], (
                    f"{key}: no slow-vs-fast rewrite. This stage exists to delete a "
                    f"re-scan; showing only the fast version hides which part is the trick."
                )
            for rw in u["rewrites"]:
                for part in ("title", "slow", "fast", "edit"):
                    assert rw.get(part, "").strip(), \
                        f"{key}: rewrite {rw.get('title', '?')!r} has no {part!r}"
                assert rw["why"].strip(), (
                    f"{key}: rewrite {rw['title']!r} has no 'why'. \"It is faster\" is the "
                    f"observation; the explanation is why the edit cannot lose an answer."
                )
                assert rw["slow"].strip() != rw["fast"].strip(), \
                    f"{key}: rewrite {rw['title']!r} has identical slow and fast versions"

            # The help layer.
            if key in _NEEDS_HELP:
                for field in ("quizzes", "stuck", "edge_cases"):
                    assert len(u[field]) >= _MIN_HELP, \
                        f"{key}: {len(u[field])} {field}, fewer than {_MIN_HELP}"
                assert u["walkthrough"], f"{key}: no worked solution"
            for i, q in enumerate(u["quizzes"]):
                assert q["prompt"].strip() and q["code"].strip(), f"{key}: quiz {i} is empty"
                assert len(q["options"]) >= 3 and len(set(q["options"])) == len(q["options"]), \
                    f"{key}: quiz {i} needs three or more distinct options"
                assert q["why"].strip(), f"{key}: quiz {i} has no explanation"
            ladder = {sl for r in u["rungs"] for sl in r["slugs"]}
            for i, e in enumerate(u["edge_cases"]):
                assert e["slug"] in ladder, \
                    f"{key}: edge case {i} names {e['slug']!r}, which is not on this unit's ladder"
                assert e["case"].strip() and e["input"].strip() and e["breaks"].strip(), \
                    f"{key}: edge case {i} is incomplete"
            for i, st in enumerate(u["stuck"]):
                assert st["when"].strip() and st["ask"].strip(), f"{key}: stuck row {i} is incomplete"
            w = u["walkthrough"]
            if w:
                assert w["slug"] in problems, f"{key}: walkthrough names unknown problem {w['slug']!r}"
                assert w["slug"] in {sl for r in u["rungs"] for sl in r["slugs"]}, \
                    f"{key}: walkthrough problem {w['slug']!r} is not on this unit's ladder"
                assert all(st["body"].strip() for st in w["steps"]), \
                    f"{key}: walkthrough has an empty step"

            last_rank = -1
            first_rung_floor = None   # easiest problem on the opening rung
            unit_n = 0                # every problem in the unit
            required_n = 0            # what the unit actually asks of you
            seen_optional = False     # optional rungs must come last
            misplaced_required = False
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
                unit_n += len(r["slugs"])

                if r["optional"]:
                    # An optional rung is off the ladder, so Rule 4 does not
                    # apply to it: it holds a unit's *surplus*, whose difficulty
                    # has nothing to do with where the required rungs finished.
                    # Demanding it climb would force the surplus to be sorted
                    # into the ladder, which is the thing being undone.
                    seen_optional = True
                    continue
                if seen_optional:
                    misplaced_required = True
                if first_rung_floor is None:
                    first_rung_floor = min(ranks)
                required_n += len(r["slugs"])

                # Rule 4 — rungs climb. Compared on the rung's *hardest*
                # problem, so a rung may open with an easy warm-up of its own.
                rank = max(ranks)
                assert rank >= last_rank, (
                    f"{key}: rung {r['title']!r} is easier than the rung before it"
                )
                last_rank = rank

            # An optional rung belongs after the required ones: "work down the
            # page" has to stay true, and a skippable rung in the middle makes
            # the page's order a suggestion rather than a sequence.
            assert not misplaced_required, (
                f"{key}: a required rung follows an optional one — put the "
                f"optional rungs last so the page can still be worked downwards"
            )
            assert first_rung_floor is not None, \
                f"{key}: every rung is optional, so the unit asks nothing"
            weights[key] = (u["weight"], required_n, unit_n)

            # Rule 5 — a substantial unit opens below its ceiling. Expressed as
            # "opens on an Intro or an Easy" rather than "one rank below the
            # hardest", because the latter is satisfied by a unit that is ten
            # Mediums and two Hards — which is precisely the shape being
            # rejected. Scoped to units with more than four problems: a
            # three-problem unit has no room for an on-ramp and does not need
            # one, since it is over before it can wall anybody off.
            if unit_n > _ONRAMP_MIN_UNIT and first_rung_floor > _DIFF_RANK["Easy"]:
                floor_name = _RANK_NAME[first_rung_floor]
                raise AssertionError(
                    f"{key}: {unit_n} problems and the first rung "
                    f"({u['rungs'][0]['title']!r}) opens at {floor_name}. A first rung "
                    f"at the unit's ceiling is a wall with a warm-up's label on it — "
                    f"author an Intro or Easy entry problem (see tools/dsa_onramps.py)."
                )

    # Rule 1, the other half — every problem is reachable from the curriculum.
    unplaced = sorted(set(problems) - set(seen_slugs))
    assert not unplaced, (
        f"{len(unplaced)} problem(s) belong to no unit: {unplaced[:12]}"
        + (" …" if len(unplaced) > 12 else "")
    )
    # The mirror of Rule 1, for lessons. Every problem is reachable from the
    # curriculum; so should every *algorithms* concept be. `alg_*` and `ds_*`
    # are the algorithm-and-structure lessons — the ones this curriculum is a
    # path through — and one no unit links is a lesson only reachable by
    # browsing the Learn tab and guessing. (Language concepts are deliberately
    # not covered: the DSA curriculum is not the Java course.)
    unlinked = sorted(
        k for k in concepts
        if k.startswith(("alg_", "ds_")) and k not in linked_concepts
    )
    assert not unlinked, (
        f"{len(unlinked)} algorithm concept(s) are linked by no unit: {unlinked}. "
        f"Add each to the `lessons` of the unit that teaches it."
    )

    _check_weight_bands(weights, stage_of, order)
    return len(seen_units), len(seen_slugs)


def _check_weight_bands(weights, stage_of, order):
    """Print the content-debt ledger. Deliberately NOT an assertion.

    A unit outside its band is a statement about the *syllabus*, not about the
    data being malformed: `greedy` having four problems does not make the
    curriculum broken, it makes it thin in a place worth being thick. Failing
    the build on it would mean every unrelated change to any unit is blocked
    until somebody authors four greedy problems — which is how a quality bar
    turns into a reason to stop running the generator.

    So it prints, every time, and the number going down is the only thing that
    matters. Structural rules (dangling slugs, a rung that does not climb, a
    unit that opens at its ceiling) stay assertions, because those are bugs.

    Stage 1 is exempt. Foundations is deliberately broad and cheap — its 28
    Intro problems exist so the keyboard stops being the bottleneck, and their
    count is not a claim about interview yield.
    """
    rows = []
    for key in order:
        if stage_of[key] == 0:
            continue
        weight, required, total = weights[key]
        lo, hi = _WEIGHT_BANDS[weight]
        if required < lo:
            rows.append((key, weight, required, total, f"thin, wants {lo - required} more"))
        elif required > hi:
            rows.append((key, weight, required, total, f"heavy by {required - hi}"))
    # ASCII only: this goes to a console whose encoding is not ours to choose
    # (cp932 on the authoring machine), and a ledger that crashes the generator
    # on an em-dash is worse than no ledger.
    if not rows:
        print("DSA weight bands: every unit past foundations is inside its band.")
        return
    print(f"DSA weight bands: {len(rows)} unit(s) outside their band "
          f"(a ledger, not an error):")
    for key, weight, required, total, note in rows:
        lo, hi = _WEIGHT_BANDS[weight]
        extra = f" (+{total - required} optional)" if total > required else ""
        print(f"    {key:24s} weight {weight}  {required:2d} problems{extra:16s} "
              f"band {lo}-{hi}  -> {note}")


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
