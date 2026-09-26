# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Attach the problem sets, projects and extra practice authored in
# mastery_ts_more_m1.py .. m6.py to TS_WEEKS, and check them. Runs last of the
# TypeScript Mastery files (see gen_seed.py).
# ---------------------------------------------------------------------------

_ts_week_numbers = {w["week"] for w in TS_WEEKS}
for _table in (TS_PROBLEM_SETS, TS_PROJECTS, TS_PRACTICE_MORE, TS_CARDS_MORE, TS_QUIZ_TOPUP):
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

# Quiz top-ups (X-30). Question texts stay unique within a week's bank — the
# chapter questions merged in later by _finalize_mastery are deduped against
# these, so a top-up never brings a twin into a sitting.
for _tsw in TS_WEEKS:
    _texts = {q["question"] for q in _tsw["quiz"]}
    for _q2 in TS_QUIZ_TOPUP.get(_tsw["week"], []):
        assert _q2["question"] not in _texts, f"TS week {_tsw['week']}: duplicate quiz question {_q2['question']!r}"
        assert len(_q2["options"]) == 4 and _q2["answer"] == 0, f"{_q2['question']!r}: four options, answer first"
        assert len(set(_q2["options"])) == 4, f"{_q2['question']!r}: repeated option"
        _texts.add(_q2["question"])
        _tsw["quiz"].append(_q2)

# Week 27's interview bank, timed mock sessions and code reviews
# (mastery_ts_w27.py). Only the capstone week carries them.
_w27 = next(w for w in TS_WEEKS if w["week"] == 27)
_bank_texts = set()
for _iq2 in TS_INTERVIEW_BANK:
    assert _iq2["question"] not in _bank_texts, f"interview bank: duplicate {_iq2['question']!r}"
    assert len(_iq2["answer"]) >= 200, f"interview bank: thin answer for {_iq2['question']!r}"
    _bank_texts.add(_iq2["question"])
assert len(TS_INTERVIEW_BANK) >= 60, "interview bank: the roadmap asks for 60 questions"
_w27_ids = {ex["id"]: ex for ex in _w27["problem_set"]}
for _ms in TS_MOCK_SESSIONS:
    assert _ms["minutes"] > 0 and _ms["rubric"], f"{_ms['title']}: needs a clock and a rubric"
    assert all(0 <= i < len(TS_INTERVIEW_BANK) for i in _ms["questions"]), f"{_ms['title']}: bad question index"
    assert _ms["problem"] in _w27_ids and _w27_ids[_ms["problem"]]["kind"] == "challenge", \
        f"{_ms['title']}: problem {_ms['problem']!r} is not a week-27 problem"
    assert _ms["puzzle"] in _w27_ids and _w27_ids[_ms["puzzle"]]["kind"] == "typelevel", \
        f"{_ms['title']}: puzzle {_ms['puzzle']!r} is not a week-27 type puzzle"
_cr_ids = set()
for _cr2 in TS_CODE_REVIEWS:
    assert _cr2["id"] not in _cr_ids, f"code review: duplicate id {_cr2['id']}"
    _cr_ids.add(_cr2["id"])
    assert len(_cr2["comments"]) >= 3, f"{_cr2['id']}: the model review needs 3+ comments"
    assert _TSO_COLLECT or _cr2["runs"] != _cr2["fixed_runs"], f"{_cr2['id']}: the fix changes nothing observable"
_w27["interview_bank"] = TS_INTERVIEW_BANK
_w27["mock_sessions"] = TS_MOCK_SESSIONS
_w27["code_reviews"] = TS_CODE_REVIEWS
