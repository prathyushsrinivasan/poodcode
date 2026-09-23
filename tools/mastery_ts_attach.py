# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Attach the problem sets, projects and extra practice authored in
# mastery_ts_more_m1.py .. m6.py to TS_WEEKS, and check them. Runs last of the
# TypeScript Mastery files (see gen_seed.py).
# ---------------------------------------------------------------------------

_ts_week_numbers = {w["week"] for w in TS_WEEKS}
for _table in (TS_PROBLEM_SETS, TS_PROJECTS, TS_PRACTICE_MORE, TS_CARDS_MORE):
    _unknown = sorted(set(_table) - _ts_week_numbers)
    assert not _unknown, f"TS Mastery content for weeks that do not exist: {_unknown}"

_ts_ids = set()
for _tsw in TS_WEEKS:
    for _ex in _tsw["practice"]:
        _ts_ids.add(_ex["id"])

for _tsw in TS_WEEKS:
    _n = _tsw["week"]
    _more = TS_PRACTICE_MORE.get(_n, [])
    _set = TS_PROBLEM_SETS.get(_n, [])
    for _ex in _more + _set:
        assert _ex["id"] not in _ts_ids, f"TS week {_n}: duplicate exercise id {_ex['id']}"
        _ts_ids.add(_ex["id"])
        _want = _week_strictness(_n) or "strict"
        assert (_ex.get("strictness") or "strict") in (_want, "strict+indexed"), \
            f"{_ex['id']}: runs at {_ex.get('strictness')!r}, week {_n} is {_want!r}"
    for _ex in _set:
        assert _ex["kind"] in ("challenge", "typelevel"), f"{_ex['id']}: problem-set kind {_ex['kind']!r}"
        assert _ex["difficulty"] in ("Easy", "Medium", "Hard"), f"{_ex['id']}: needs a tier"
    _tsw["practice"] = _tsw["practice"] + _more
    _tsw["problem_set"] = _set
    _spec = TS_PROJECTS.get(_n)
    if _spec is not None:
        assert len(_spec["requirements"]) >= 3, f"week {_n} project: needs 3+ numbered requirements"
        assert len(_spec["tests"]) >= 5, f"week {_n} project: needs 5+ acceptance tests"
        assert _spec["starter"] != _spec["solution"], f"week {_n} project: starter equals solution"
    _tsw["project_spec"] = _spec

# Review cards for chapters added after mastery_ts_cards.py was written. Fronts
# stay unique across the whole track — the deck dedupes on them.
_ts_fronts = {c["front"] for w in TS_WEEKS for c in w["flashcards"]}
for _tsw in TS_WEEKS:
    for _front, _back in TS_CARDS_MORE.get(_tsw["week"], []):
        assert _front not in _ts_fronts, f"TS week {_tsw['week']}: duplicate card front {_front!r}"
        assert _front.strip() and _back.strip(), f"TS week {_tsw['week']}: empty card"
        _ts_fronts.add(_front)
        _tsw["flashcards"].append({"front": _front, "back": _back})
