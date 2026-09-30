# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Per-chapter practice for the TypeScript Mastery track (TS_MASTERY_ROADMAP.md
# X-10, X-11, X-19).
#
# The roadmap's targets are per CHAPTER, not per week: at least three each of
# predict / diagnose / retype / design, two of fix, and four practice families
# on every one of the 87 chapters. Content for that lives in
#
#   tools/mastery_ts_x_m1.py .. m6.py     the reading kinds, one file a month
#   tools/mastery_ts_fam_m1.py .. m6.py   the families, one file a month
#
# written with the helpers below. Each helper names the CHAPTER, and the
# exercise lands in the Mastery week that first schedules it, at that week's
# strictness. Ids are `tsm-<chapter>-x<kind><n>` and `tsm-<chapter>-fam-<fid>-<n>`,
# so every exercise is attributable to its chapter (see TS_CHAPTER_TARGETS in
# mastery_ts_chapter_check.py, which enforces the targets).
#
# Every expected output is computed from the reference (tools/ts_outputs_kit.py):
# a helper takes INPUTS, never outputs. A program here follows the stdin
# scaffold (`input` is stdin, trimmed), exactly like a problem-set problem.
#
# Check a content file on its own — without rebuilding the seeds — with
#
#     python tools/check_ts_authoring.py tools/mastery_ts_x_m3.py
#
# exec()'d by gen_seed.py after mastery_ts_kinds_more.py and before
# mastery_ts_attach.py.
# ---------------------------------------------------------------------------

import re as _ck_re

_CK_PRELUDE = _TW_PRELUDE + "type IsAny<T> = 0 extends 1 & T ? true : false;\n"
_CK_ANY = _ck_re.compile(r"\bany\b")

TS_CHAPTER_WEEK = {}
for _ck_w in TS_WEEKS:
    for _ck_key in _ck_w["concepts"]:
        TS_CHAPTER_WEEK.setdefault(_ck_key, _ck_w["week"])

TS_CHAPTER_PRACTICE = {}  # chapter -> [exercise], in authoring order

_CK_KINDS = {"pr": "predict", "dx": "diagnose", "rt": "retype", "dz": "design", "fx": "fix"}


def _ck_add(chapter, ex):
    assert chapter in TS_CHAPTER_WEEK, f"{ex['id']}: {chapter!r} is not a TypeScript chapter any week schedules"
    TS_PRACTICE_MORE.setdefault(TS_CHAPTER_WEEK[chapter], []).append(ex)
    TS_CHAPTER_PRACTICE.setdefault(chapter, []).append(ex)
    return ex


def _ck_strictness(chapter):
    return _week_strictness(TS_CHAPTER_WEEK[chapter]) or "strict"


def _ck_ex(chapter, abbr, n, title, prompt, starter, solution, inputs, harness="", forbid=(), hints=(),
           difficulty="Medium", body=True):
    """One reading-kind exercise. `starter`/`solution` are bodies after the stdin
    scaffold when `body` (the default), whole programs otherwise. No `inputs`
    means a type-only exercise: judged by the compiler alone, never run."""
    assert chapter in TS_CHAPTER_WEEK, f"{chapter!r} is not a TypeScript chapter any week schedules"
    eid = f"tsm-{chapter}-x{abbr}{n}"
    strictness = _ck_strictness(chapter)
    if body:
        starter = _TS_SCAFFOLD + starter.strip("\n") + "\n"
        solution = _TS_SCAFFOLD + solution.strip("\n") + "\n"
    else:
        starter = starter.strip("\n") + "\n"
        solution = solution.strip("\n") + "\n"
    assert starter != solution, f"{eid}: starter equals solution"
    assert title.strip() and prompt.strip(), f"{eid}: needs a title and a prompt"
    hints = list(hints)
    assert hints, f"{eid}: give at least one hint"
    inputs = list(inputs or [])
    return _ck_add(chapter, {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0], "hints": hints,
        "language": "typescript", "kind": _CK_KINDS[abbr], "difficulty": difficulty,
        "strictness": strictness,
        "harness": (_CK_PRELUDE + "\n" + harness.strip("\n") + "\n") if harness.strip() else "",
        "judge_mode": "" if inputs else "types", "forbid": list(forbid),
        "starter": starter, "solution": solution,
        "tests": _computed(eid, solution, inputs, strictness) if inputs else [],
        "source_slug": "", "dataset": "",
    })


def _xpr(chapter, n, title, code, expr, answer, hints=(), why=""):
    """Predict: annotate `check` with exactly the type the compiler infers for
    `expr` (an identifier or dotted path declared in `code`). `code` is a whole
    snippet — no stdin. Graded by Equal<typeof check, typeof expr>, with
    `typeof` banned so the answer cannot be copied from the question."""
    code = code.strip("\n") + "\n"
    assert "typeof" not in code, f"{chapter} predict {n}: the snippet may not use typeof (it is banned)"
    line = "const check: {} = " + expr + ";\n"
    prompt = (f"What type does TypeScript already infer for `{expr}`? Annotate `check` with exactly "
              f"that type — not merely one that fits." + (f" {why}" if why else ""))
    return _ck_ex(chapter, "pr", n, title, prompt, code + line.format("____"), code + line.format(answer),
                  None, harness=f"type _1 = Expect<Equal<typeof check, typeof {expr}>>;", forbid=["typeof"],
                  hints=hints, difficulty="Easy", body=False)


def _xdx(chapter, n, title, error, broken, fixed, inputs, ask="Fix the cause.", hints=()):
    """Diagnose: `broken` fails to compile with `error` (quote the real message,
    starting with its TSnnnn code — the verifier re-derives the code from the
    starter); `fixed` compiles and runs on `inputs`."""
    assert _ck_re.search(r"\bTS\d{4,5}\b", error), f"{chapter} diagnose {n}: quote the compiler's TSnnnn code"
    prompt = f"The compiler rejects this program:\n\n    {error}\n\n{ask}"
    return _ck_ex(chapter, "dx", n, title, prompt, broken, fixed, inputs, hints=hints)


def _xfx(chapter, n, title, prompt, broken, fixed, inputs, hints=()):
    """Fix: `broken` compiles and prints the wrong thing (or crashes) on at
    least one of `inputs`; `fixed` is right on all of them."""
    return _ck_ex(chapter, "fx", n, title, prompt, broken, fixed, inputs, hints=hints)


def _xrt(chapter, n, title, prompt, anyish, typed, asserts, inputs, hints=()):
    """Retype: `anyish` runs and prints the right thing with `any` where the
    types should be; `typed` says what is really there. `asserts` are hidden
    Expect<Equal<…>> claims that `any` cannot satisfy."""
    assert _CK_ANY.search(anyish), f"{chapter} retype {n}: the starter needs an `any` to replace"
    assert not _CK_ANY.search(typed), f"{chapter} retype {n}: the solution still says `any`"
    assert "Expect<" in asserts, f"{chapter} retype {n}: give Expect<Equal<…>> claims"
    return _ck_ex(chapter, "rt", n, title, prompt, anyish, typed, inputs, harness=asserts, hints=hints)


def _xdz(chapter, n, title, prompt, full, blank, asserts, inputs, hints=()):
    """Design: `blank` (a unique substring of `full`, normally a whole type
    declaration) becomes the ____, to be recovered from how the code uses it.
    `asserts` are hidden claims about the type. Empty `inputs` makes it
    type-only (judged by the compiler alone)."""
    assert full.count(blank) == 1, f"{chapter} design {n}: the blank must appear exactly once"
    assert "Expect<" in asserts, f"{chapter} design {n}: give Expect<Equal<…>> claims"
    return _ck_ex(chapter, "dz", n, title, prompt, full.replace(blank, "____", 1), full, inputs,
                  harness=asserts, hints=hints)


def _xfam(chapter, fid, title, variants):
    """A practice family: five (twist, prompt, body, inputs) — the base problem,
    then four variations that each twist ONE dimension (the input's shape, the
    output's format, an edge case, a rule, a generalisation). `body` follows
    the stdin scaffold; the learner writes it from a blank."""
    assert len(variants) == 5, f"{chapter}/{fid}: a family has five variations"
    strictness = _ck_strictness(chapter)
    for n, (twist, prompt, body, inputs) in enumerate(variants, start=1):
        eid = f"tsm-{chapter}-fam-{fid}-{n}"
        assert (n == 1) == (not twist), f"{eid}: only the base problem has no twist"
        solution = _TS_SCAFFOLD + body.strip("\n") + "\n"
        lead = "The base problem." if n == 1 else f"Twist {n - 1}: {twist}."
        _ck_add(chapter, {
            "id": eid, "title": f"{title} ({n}/5){'' if n == 1 else ' — ' + twist}",
            "prompt": f"{lead} {prompt}",
            "hint": "", "hints": [],
            "language": "typescript", "kind": "challenge", "difficulty": "Easy" if n <= 2 else "Medium",
            "strictness": strictness, "harness": "", "judge_mode": "", "forbid": [],
            "starter": _TS_SCAFFOLD + "____\n", "solution": solution,
            "tests": _computed(eid, solution, inputs, strictness),
            "source_slug": "", "dataset": "",
        })


def _xtfam(chapter, fid, title, variants, prelude=""):
    """A type-level family: five (twist, prompt, full, blank, checks). `blank`
    (unique in `full`) is the ____; `checks` are hidden Expect<Equal<…>> claims;
    `prelude` (hidden helper types) goes before every check."""
    assert len(variants) == 5, f"{chapter}/{fid}: a family has five variations"
    for n, (twist, prompt, full, blank, checks) in enumerate(variants, start=1):
        eid = f"tsm-{chapter}-fam-{fid}-{n}"
        assert (n == 1) == (not twist), f"{eid}: only the base problem has no twist"
        ex = _tl(eid, "", prompt, full, blank, prelude + checks, difficulty="Easy" if n <= 2 else "Medium")
        ex["strictness"] = _ck_strictness(chapter)
        lead = "The base problem." if n == 1 else f"Twist {n - 1}: {twist}."
        ex["title"] = f"{title} ({n}/5){'' if n == 1 else ' — ' + twist}"
        ex["prompt"] = f"{lead} {prompt}"
        _ck_add(chapter, ex)
