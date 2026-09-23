# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The chapter template for new TypeScript Learn chapters (TS_MASTERY_ROADMAP.md
# X-02 to X-07).
#
# The first 50 TypeScript chapters are a page of syntax and a "Watch out for"
# list. A chapter written with `_chapter` is structured data rendered into one
# lesson with a fixed spine:
#
#   Why it exists        — the problem this feature solves, before any syntax
#   The core idea        — the concept itself
#   Worked examples      — whole programs, each with the output it really prints
#   What the compiler says — real TSnnnn diagnostics for the mistakes this
#                           chapter's learner will make
#   Pitfalls             — looks right, isn't: the wrong program, what it
#                           prints, and the fix with what IT prints
#   In an interview      — appended by ts_lesson_interview.py
#   Where it shows up later — forward links
#
# Nothing printed in a lesson is typed by hand. Example and pitfall outputs come
# from running the program, and compiler messages from running the checker,
# both through tools/ts_outputs_kit.py (`python tools/gen_ts_outputs.py`).
# Exercises likewise name only their inputs (`_drill`, `_chal`).
#
# exec()'d by gen_seed.py after typescript_mastery.py (so `tsx`, `_P`, `_MS`
# and the TSM_* registries exist) and before ts_lesson_interview.py.
# ---------------------------------------------------------------------------

import re

TS_INTERVIEW_MORE = {}      # key -> [(question, answer)], merged by ts_lesson_interview.py
TS_CHAPTER_KEYS = []        # every chapter built with _chapter, in authoring order
TS_LESSON_MIN_CHARS = 4000  # X-03: 15-25 minutes of reading, before the interview block


def _fence(code, lang="ts"):
    return f"```{lang}\n{code.rstrip()}\n```"


def _tsmsg(d):
    """A diagnostic as `tsc --pretty false` prints it. The checker flattens a
    chained message with " " as the newline, so each chain level arrives as a
    run of 1 + 2*depth spaces; turn those back into indented lines."""
    msg = re.sub(r" {3,}", lambda m: "\n" + " " * (len(m.group(0)) - 1), d["msg"])
    return f"line {d['line']}: error TS{d['code']}: {msg}"


def _drill(eid, title, prompt, full, blanks, inputs, hint=""):
    """A fill-in-the-blank drill whose expected outputs are computed. Learn
    exercises are judged on stdout at plain `strict` (verify_exercises.rs);
    type-graded work belongs in a Mastery week's practice instead."""
    full = _P(full)
    tests = _computed(eid, full, inputs)
    return tsx(eid, title, prompt, full, blanks, [(t["input"], t["output"]) for t in tests], hint)


def _chal(eid, title, difficulty, prompt, body, inputs, hint=""):
    """A whole-solution challenge on the stdin scaffold, outputs computed."""
    body = body.strip("\n")
    full = _P(_MS + body)
    tests = _computed(eid, full, inputs)
    return tsc(eid, title, difficulty, prompt, full, body,
               [(t["input"], t["output"]) for t in tests], hint)


def _cq(question, answer, wrong, explanation):
    """A chapter quiz question, correct option first (the UI shuffles)."""
    return {"question": question, "options": [answer] + list(wrong), "answer": 0,
            "explanation": explanation}


def _render_examples(key, examples):
    parts = []
    for i, ex in enumerate(examples, start=1):
        title, code, inputs, note = ex
        code = _P(code)
        tests = _computed(f"{key}-example{i}", code, inputs or [""])
        parts.append(f"#### {title}\n{_fence(code)}")
        for t in tests:
            if t["input"]:
                parts.append("Input:\n" + _fence(t["input"], "text"))
            parts.append("Prints:\n" + _fence(t["output"] or "(nothing)", "text"))
        if note:
            parts.append(note.strip())
    return "\n\n".join(parts)


def _render_errors(key, errors):
    parts = []
    for i, (code, snippet, note, *rest) in enumerate(errors, start=1):
        strictness = rest[0] if rest else ""
        snippet = _P(snippet)
        diags = _compiler_says(f"{key}-error{i}", snippet, code, strictness)
        first = diags[0]
        flag = " (with `noUncheckedIndexedAccess`)" if strictness == "strict+indexed" else ""
        parts.append(_fence(snippet) + "\n"
                     + _fence(_tsmsg(first), "text")
                     + (f"\n\n{flag.strip()}" if flag else "")
                     + "\n\n" + note.strip())
    return "\n\n".join(parts)


def _pitfall_side(eid, side, inputs):
    """One side of a pitfall: a program that runs (str), or `(source, TSnnnn)` —
    a program whose point is what the compiler says about it. Returns
    (code, label, shown text)."""
    if isinstance(side, tuple):
        source, expect = _P(side[0]), side[1]
        d = _compiler_says(eid, source, expect)[0]
        return source, "The compiler says:", _tsmsg(d)
    source = _P(side)
    outs = _computed(eid, source, inputs)
    return source, "Prints:", "\n".join(t["output"] for t in outs) or "(nothing)"


def _render_pitfalls(key, pitfalls):
    """Each pitfall: `(title, wrong, right, note[, inputs])`. The two sides must
    visibly differ — a pitfall whose fix prints the same thing shows nothing."""
    parts = []
    for i, (title, wrong, right, note, *rest) in enumerate(pitfalls, start=1):
        inputs = rest[0] if rest else [""]
        wc, wl, wo = _pitfall_side(f"{key}-pitfall{i}-wrong", wrong, inputs)
        rc, rl, ro = _pitfall_side(f"{key}-pitfall{i}-right", right, inputs)
        assert (wl, wo) != (rl, ro) or _TSO_COLLECT, \
            f"{key} pitfall {i}: the wrong and right programs show the same thing"
        parts.append(f"#### {title}\n{_fence(wc)}\n{wl}\n{_fence(wo, 'text')}\n\n"
                     f"{note.strip()}\n\n{_fence(rc)}\n{rl}\n{_fence(ro, 'text')}")
    return "\n\n".join(parts)


def _chapter(key, category, name, what, deep, note, *, why, idea, examples, errors,
             pitfalls, later, exercises, quiz, interview):
    """Register a templated chapter. See the header for the lesson's spine."""
    assert key.startswith("ts_") and key not in CONCEPTS, f"{key}: new chapter keys must be fresh ts_*"
    assert len(examples) >= 3, f"{key}: needs at least 3 worked examples (X-04)"
    assert len(errors) >= 2, f"{key}: needs at least 2 compiler errors (X-07)"
    assert len(pitfalls) >= 3, f"{key}: needs at least 3 pitfalls (X-05)"
    assert len(interview) >= 3, f"{key}: needs at least 3 interview questions (X-06)"
    assert len(exercises) >= 3, f"{key}: needs at least 3 exercises"
    assert len(quiz) >= 5, f"{key}: needs at least 5 quiz questions"
    lesson = "\n\n".join([
        "### Why it exists\n" + why.strip(),
        "### The core idea\n" + idea.strip(),
        "### Worked examples\n" + _render_examples(key, examples),
        "### What the compiler says\n" + _render_errors(key, errors),
        "### Pitfalls\n" + _render_pitfalls(key, pitfalls),
        "### Where it shows up later\n" + "\n".join(f"- {line}" for line in later),
    ])
    assert len(lesson) >= TS_LESSON_MIN_CHARS or _TSO_COLLECT, \
        f"{key}: lesson is {len(lesson)} characters; the template asks for {TS_LESSON_MIN_CHARS}+"
    CONCEPTS[key] = {"name": name, "what": what, "deep": deep, "java": note,
                     "language": "typescript", "quiz": quiz}
    CATEGORY[key] = category
    LESSONS[key] = lesson
    EXERCISES[key] = exercises
    TS_INTERVIEW_MORE[key] = interview
    TS_CHAPTER_KEYS.append(key)
