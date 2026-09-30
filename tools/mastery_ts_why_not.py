# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Why-not notes for the TypeScript quiz banks (TS_MASTERY_ROADMAP.md X-37).
#
# A quiz that only explains the right answer leaves the learner who picked B
# guessing about what was wrong with B. `why_not` is a list parallel to a
# question's options: one sentence per wrong option, "" for the right one. The
# UI shows the note for an option once it has been chosen and marked
# (src/components/QuizChoices.tsx).
#
# Code-output and multi-select questions already carry theirs (built with the
# question). The authored single-choice questions — the week banks, top-ups
# and the chapter quizzes merged in by _finalize_mastery — get theirs from
#
#   tools/mastery_ts_whynot_m1.py .. m6.py
#
# each of which fills TS_WHY_NOT:
#
#   TS_WHY_NOT["<question text, verbatim>"] = {
#       "<wrong option, verbatim>": "Why it is wrong, in one or two sentences.",
#       ...
#   }
#
# Keyed by option TEXT rather than position, because a question can appear in
# more than one bank with its options in another order. Check a file on its own
# with `python tools/check_ts_why_not.py tools/mastery_ts_whynot_m3.py`.
#
# exec()'d by gen_seed.py after _finalize_mastery, so the chapter questions are
# already in the week banks.
# ---------------------------------------------------------------------------

TS_WHY_NOT = {}
for _wn_n in range(1, 7):
    _wn_path = os.path.join(HERE, f"mastery_ts_whynot_m{_wn_n}.py")
    if os.path.exists(_wn_path):
        with open(_wn_path, encoding="utf-8") as _wn_f:
            exec(compile(_wn_f.read(), _wn_path, "exec"))


def _wn_single_choice(q):
    """An authored single-choice question: no special kind, one answer."""
    return not q.get("kind") and "answers" not in q


def _wn_apply(q):
    notes = TS_WHY_NOT.get(q["question"])
    if notes is None:
        return False
    right = q["options"][q["answer"]]
    assert right not in notes, f"why-not for {q['question']!r} explains the RIGHT answer {right!r}"
    missing = [o for i, o in enumerate(q["options"]) if i != q["answer"] and o not in notes]
    assert not missing, f"why-not for {q['question']!r} has no note for {missing}"
    q["why_not"] = ["" if i == q["answer"] else notes[o].strip() for i, o in enumerate(q["options"])]
    return True


_wn_questions = [q for t in MASTERY if t.get("language") == "typescript"
                 for w in t["weeks"] for q in w["quiz"] if _wn_single_choice(q)]
_wn_questions += [q for c in concepts if c.get("language") == "typescript"
                  for q in (c.get("quiz") or []) if _wn_single_choice(q)]

_wn_known = {}
for _wn_q in _wn_questions:
    _wn_known.setdefault(_wn_q["question"], set()).update(_wn_q["options"])
for _wn_text, _wn_notes in TS_WHY_NOT.items():
    assert _wn_text in _wn_known, f"why-not for a question that is not in any TypeScript bank: {_wn_text!r}"
    _wn_stray = sorted(set(_wn_notes) - _wn_known[_wn_text])
    assert not _wn_stray, f"why-not for {_wn_text!r} names options it does not have: {_wn_stray}"
    for _wn_opt, _wn_note in _wn_notes.items():
        assert _wn_note.strip(), f"why-not for {_wn_text!r}: empty note for {_wn_opt!r}"

TS_WHY_NOT_MISSING = sorted({q["question"] for q in _wn_questions if not _wn_apply(q)})
