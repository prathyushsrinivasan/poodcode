# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The strictness ladder, applied everywhere (TS_MASTERY_ROADMAP.md X-17).
#
# From week TS_INDEXED_FROM_WEEK the finals, problem sets and projects already
# run under `strict+indexed` (`noUncheckedIndexedAccess`). This extends the same
# rule to everything else a learner is judged on from that week on:
#
#   * every Mastery practice exercise of week 14+ that does not say otherwise,
#   * every Learn exercise on a chapter the programme first schedules in week
#     14+ — the Learn tab and the Mastery week show the same chapter, so they
#     must grade it the same way.
#
# An exercise that names its strictness keeps it: predict drills are pinned to
# `strict` on purpose (their answer is an inferred type, and the flag changes
# what `xs[0]` infers), and so are the chapter-derived exercises that quote a
# chapter's own code.
#
# STRICT_PINNED lists the exercises that would stop compiling under the flag.
# Every one is a fill-in-the-blank drill whose subject is not index safety — a
# generic `first<T>(arr: T[]): T`, an interface filled from `parts[0]` — and
# whose canonical answer reads an index. Rewriting them to `T | undefined`
# would change what the drill teaches, so they stay at plain `strict`, named.
# tools/verify_ts_mastery.py proves the list is exactly right: every pinned
# exercise fails under the flag, and everything else is checked with it on.
#
# Runs after mastery_ts_attach.py (see gen_seed.py), before concepts.json is
# written.
# ---------------------------------------------------------------------------

STRICT_PINNED = {
    # Learn chapters of weeks 14+
    "ts_generics-first", "ts_generics-last", "ts_generics-longest",
    "ts_classes-method", "ts_classes-inherit", "ts_classes-challenge",
    "ts_this_accessors-getter",
    "ts_modules-export", "ts_modules-challenge",
    "ts_utility_types-record", "ts_utility_types-pick", "ts_utility_types-challenge",
    "ts_async-all",
    "ts_compose-extends", "ts_compose-intersection", "ts_compose-circle", "ts_compose-challenge",
    "ts_structural_typing-duck", "ts_structural_typing-extra",
    "ts_satisfies-challenge",
    "ts_branded_types-units", "ts_branded_types-challenge",
    "ts_generic_constraints-pluck", "ts_generic_constraints-max", "ts_generic_constraints-challenge",
    "ts_keyof_indexed-challenge",
    "ts_mapped_types-getters", "ts_mapped_types-challenge",
    "ts_conditional_types-challenge",
    "ts_template_literal_types-challenge",
    "ts_type_level-challenge",
    "ts_iterators-challenge",
    "ts_error_types-challenge",
    "ts_declaration_files-augment", "ts_declaration_files-challenge",
    # Mastery practice: a chapter's worked example with its annotations
    # stripped (gen_ts_retypes.py) — the example itself reads `xs[0]`.
    "tsm-ts_async_patterns-rt1",
}

_ts_first_week = {}
for _tsw in TS_WEEKS:
    for _key in _tsw["concepts"]:
        _ts_first_week.setdefault(_key, _tsw["week"])


def _ladder(_ex, _week):
    """Give an exercise with no strictness of its own its week's preset."""
    if _ex["kind"] == "spot" or _ex.get("strictness"):
        return 0
    _preset = "strict" if _ex["id"] in STRICT_PINNED else _week_strictness(_week)
    if _preset:
        _ex["strictness"] = _preset
    return 1 if _preset == "strict+indexed" else 0


_ts_laddered = 0
_ts_pinned_seen = set()
for _tsw in TS_WEEKS:
    for _ex in _tsw["practice"]:
        _ts_laddered += _ladder(_ex, _tsw["week"])
        if _ex["id"] in STRICT_PINNED:
            _ts_pinned_seen.add(_ex["id"])
for _c in concepts:
    if _c.get("language") != "typescript":
        continue
    _week = _ts_first_week.get(_c["key"])
    assert _week is not None, f"TS chapter {_c['key']} is not scheduled in any Mastery week"
    for _ex in _c.get("exercises") or []:
        _ts_laddered += _ladder(_ex, _week)
        if _ex["id"] in STRICT_PINNED:
            _ts_pinned_seen.add(_ex["id"])

_ts_unknown_pins = sorted(STRICT_PINNED - _ts_pinned_seen)
assert not _ts_unknown_pins, f"STRICT_PINNED names exercises that do not exist: {_ts_unknown_pins}"
