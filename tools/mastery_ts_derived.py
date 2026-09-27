# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Review cards and practice derived from the chapters themselves
# (TS_MASTERY_ROADMAP.md X-05, X-15, X-16, X-50).
#
# Every TypeScript chapter carries worked examples, real compiler errors and
# pitfalls, each with the output or diagnostic it really produces (recorded in
# TS_CHAPTER_DATA by ts_chapter_kit.py). Nothing here is typed by hand, so none
# of it can drift from what the programs do:
#
#   cards   — "what does this print?" for each worked example, "what does the
#             compiler say?" for each error, "what goes wrong here?" for each
#             pitfall. Added to the week that schedules the chapter.
#   order   — Parsons problems (X-15): a short worked example's lines, shuffled.
#             Judged by running the learner's order, so any order that prints
#             the right thing is right.
#   spot    — "click the buggy line" (X-16): a pitfall's wrong program, with
#             the lines that differ from the fix as the answer.
#
# exec()'d by gen_seed.py just before mastery_ts_attach.py.
# ---------------------------------------------------------------------------

import difflib as _tsd_difflib
import random as _tsd_random

_TSD_MIN_ORDER_LINES = 4
_TSD_MAX_ORDER_LINES = 12
_TSD_ORDER_PER_CHAPTER = 2
# Shuffles that happened to produce a program that already passes (the
# verifiers insist every starter fails): shuffled again with this salt.
_TSD_RESHUFFLE = {"tsm-ts_type_predicates-order2": "2", "tsm-ts_assertions-order2": "2"}


def _tsd_code_lines(code):
    """A program's lines without blank or comment-only lines — the pieces a
    Parsons problem hands out and the program a spot exercise shows. Neither
    changes what the program prints — except a `// @ts-…` directive, which
    changes what compiles, so it stays."""
    return [ln.rstrip() for ln in code.rstrip("\n").split("\n")
            if ln.strip() and (not ln.strip().startswith("//") or ln.strip().startswith("// @ts-"))]


def _tsd_indent(text):
    return "\n".join("    " + ln for ln in (text or "(nothing)").split("\n"))


def _tsd_orderable(code):
    """Line-shuffling only makes sense for a program whose lines stand alone:
    no multi-line strings or block comments, and no multi-file workspace."""
    if "/*" in code or "@file" in code:
        return False
    return all(ln.count("`") % 2 == 0 for ln in code.split("\n"))


def _tsd_shuffle(eid, lines):
    rng = _tsd_random.Random(eid + _TSD_RESHUFFLE.get(eid, ""))
    best = None
    for _ in range(50):
        order = list(lines)
        rng.shuffle(order)
        moved = sum(1 for a, b in zip(order, lines) if a != b)
        if best is None or moved > best[0]:
            best = (moved, order)
        if moved >= (len(lines) + 1) // 2 and order[0] != lines[0]:
            break
    return best[1]


def _tsd_order(key, name, ex, eid, strictness):
    lines = _tsd_code_lines(ex["code"])
    tests = ex["tests"]
    first = tests[0]
    prompt = (f"The lines of the worked example “{ex['title']}” from {name}, shuffled. "
              "Put them back in an order that compiles and")
    if first["input"]:
        prompt += " — given the input below — prints exactly the output below.\n\nInput:\n" \
                  + _tsd_indent(first["input"]) + "\n\nPrints:\n" + _tsd_indent(first["output"])
    else:
        prompt += " prints exactly:\n\n" + _tsd_indent(first["output"])
    return {
        "id": eid, "title": f"Put it in order: {ex['title']}", "prompt": prompt,
        "hint": "Declarations before the lines that use them; a block's lines between its opening and closing braces.",
        "hints": ["Declarations before the lines that use them; a block's lines between its opening and closing braces.",
                  "Indentation is a clue: an indented line belongs inside the nearest block that opens above it."],
        "language": "typescript", "kind": "order", "difficulty": "",
        "strictness": strictness, "harness": "", "judge_mode": "", "forbid": [],
        "starter": "\n".join(_tsd_shuffle(eid, lines)) + "\n",
        "solution": "\n".join(lines) + "\n",
        "tests": tests, "source_slug": "", "dataset": "",
    }


def _tsd_bug_lines(wrong, right):
    """1-based lines of `wrong` that the fix changes or removes. A fix that only
    inserts lines has no line to click, and returns []."""
    sm = _tsd_difflib.SequenceMatcher(a=wrong, b=right, autojunk=False)
    out = []
    for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            out.extend(range(i1 + 1, i2 + 1))
    return out


def _tsd_spot(key, name, p, eid, strictness):
    if p["right_tests"] is None or len(p["inputs"]) != 1:
        return None
    wrong = _tsd_code_lines(p["wrong"])
    right = _tsd_code_lines(p["right"])
    bug = _tsd_bug_lines(wrong, right)
    if not bug or len(bug) > 3 or len(bug) * 2 > len(wrong):
        return None
    inp = p["inputs"][0]
    right_out = p["right_tests"][0]["output"]
    if p["wrong_label"] == "Prints:":
        prompt = "This program runs, but prints the wrong thing"
        prompt += " for the input below.\n\nInput:\n" + _tsd_indent(inp) if inp else "."
        prompt += "\n\nIt prints:\n" + _tsd_indent(p["wrong_shows"]) \
                  + "\n\nIt should print:\n" + _tsd_indent(right_out)
        prompt += "\n\nClick the line that causes it."
    else:
        # Drop the line number: finding the line is the exercise.
        message = p["wrong_shows"].split(": ", 1)[1] if p["wrong_shows"].startswith("line ") else p["wrong_shows"]
        prompt = "The compiler rejects this program:\n\n" + _tsd_indent(message)
        prompt += "\n\nClick the line you would change so that it compiles and prints:\n" + _tsd_indent(right_out)
    return {
        # The pitfall's own title names the bug, so it waits for the explanation.
        "id": eid, "title": f"Spot the bug: {name} #{eid.rsplit('spot', 1)[1]}", "prompt": prompt,
        "hint": "", "hints": [],
        "language": "typescript", "kind": "spot", "difficulty": "",
        "strictness": strictness, "harness": "", "judge_mode": "", "forbid": [],
        "starter": "\n".join(wrong) + "\n", "solution": "\n".join(right) + "\n",
        "tests": p["right_tests"], "source_slug": "", "dataset": "",
        "explanation": f"**{p['title']}.** {p['note']}", "lines": bug,
    }


def _tsd_repair(key, name, p, eid):
    """A pitfall too spread out to click on (the fix changes several lines, or
    only adds some) becomes a repair instead (X-11): `fix` when the wrong
    program runs and prints the wrong thing, `diagnose` when the compiler
    rejects it. The learner edits the wrong program until the right program's
    tests pass."""
    if p["right_tests"] is None:
        return None
    wrong = "\n".join(_tsd_code_lines(p["wrong"])) + "\n"
    right = "\n".join(_tsd_code_lines(p["right"])) + "\n"
    single = len(p["inputs"]) == 1 and "\n" not in p["inputs"][0].strip()
    if p["wrong_label"] == "Prints:":
        kind = "fix"
        if single:
            inp = p["inputs"][0].strip()
            prompt = ("This program runs, but prints the wrong thing" + (f" for the input `{inp}`" if inp else "")
                      + ".\n\nIt prints:\n" + _tsd_indent(p["wrong_shows"])
                      + "\n\nIt should print:\n" + _tsd_indent(p["right_tests"][0]["output"])
                      + "\n\nFix it — every test must pass.")
        else:
            prompt = "This program runs, but prints the wrong thing for some of its inputs. Fix it — every test must pass."
    else:
        kind = "diagnose"
        message = p["wrong_shows"].split(": ", 1)[1] if p["wrong_shows"].startswith("line ") else p["wrong_shows"]
        prompt = f"The compiler rejects this program:\n\n    {message.split(chr(10))[0]}\n\nFix the cause so it compiles and every test passes."
    return {
        "id": eid, "title": f"{'Fix it' if kind == 'fix' else 'Read the error'}: {name} #{eid.rsplit('-', 1)[1][2:]}",
        "prompt": prompt, "hint": p["title"], "hints": [p["title"]],
        "language": "typescript", "kind": kind, "difficulty": "",
        "strictness": "", "harness": "", "judge_mode": "", "forbid": [],
        "starter": wrong, "solution": right, "tests": p["right_tests"], "source_slug": "", "dataset": "",
        "explanation": f"**{p['title']}.** {p['note']}",
    }


def _tsd_cards(name, data):
    cards = []
    for ex in data["examples"]:
        t = ex["tests"][0]
        if not t["output"]:
            continue
        front = f"*{name}* — what does this print?\n\n```ts\n{ex['code'].rstrip()}\n```"
        if t["input"]:
            front += f"\n\nInput:\n```text\n{t['input'].rstrip()}\n```"
        cards.append((front, f"```text\n{t['output']}\n```\n\n({ex['title']})"))
    for er in data["errors"]:
        flag = " with `noUncheckedIndexedAccess` on" if er["strictness"] == "strict+indexed" else ""
        front = f"*{name}* — what does the compiler say{flag}, and why?\n\n```ts\n{er['code'].rstrip()}\n```"
        cards.append((front, f"```text\n{er['message']}\n```\n\n{er['note']}"))
    for p in data["pitfalls"]:
        front = f"*{name}* — what goes wrong here?\n\n```ts\n{p['wrong'].rstrip()}\n```"
        if p["inputs"] and p["inputs"][0]:
            front += f"\n\nInput:\n```text\n{p['inputs'][0].rstrip()}\n```"
        back = (f"{p['wrong_label']}\n```text\n{p['wrong_shows']}\n```\n\n**{p['title']}.** {p['note']}"
                f"\n\nThe fix:\n```ts\n{p['right'].rstrip()}\n```")
        cards.append((front, back))
    return cards


_TSD_NO_COMPILE = "Nothing: it does not compile"
_TSD_THROWS = "It throws an error at runtime"


def _tsd_output_question(name, p, n):
    """A code-output question (X-31) from a pitfall: the wrong program, and
    what it really does against what it was meant to do. Only single-line
    inputs, so the question can say what it reads."""
    if p["right_tests"] is None or len(p["inputs"]) != 1 or "\n" in p["inputs"][0].strip():
        return None
    inp = p["inputs"][0].strip()
    right_out = p["right_tests"][0]["output"]
    if p["wrong_label"] == "Prints:":
        answer = p["wrong_shows"]
        options = [answer, right_out, _TSD_NO_COMPILE, _TSD_THROWS]
        # X-37: each wrong option is wrong for a reason the pitfall itself proves.
        why_not = ["",
                   "That is what the corrected program prints. The bug is exactly what makes this one print something else.",
                   "It compiles: the compiler accepts every line, which is what makes this bug easy to miss.",
                   "It runs to the end without throwing; it just prints the wrong thing."]
    else:
        message = p["wrong_shows"].split(": ", 1)[1] if p["wrong_shows"].startswith("line ") else p["wrong_shows"]
        answer = f"Nothing: it does not compile ({message.split(chr(10))[0]})"
        options = [answer, right_out, _TSD_THROWS]
        why_not = ["",
                   "That is what it prints once corrected. As written, the compiler rejects it before it can run.",
                   "It never gets to run: the type-check fails first, so nothing is thrown."]
    if len(set(options)) != len(options) or not all(o.strip() for o in options):
        return None
    reads = f" given the input `{inp}`" if inp else ""
    return {
        "question": f"{name}, program {n}: what does it print{reads}?",
        "options": options, "answer": 0, "kind": "output", "code": p["wrong"],
        "explanation": f"{p['title']}. {p['note']}", "why_not": why_not,
    }


# Predict-the-type drills on the worked examples (X-10): the answers were read
# from the checker by tools/gen_ts_predicts.py. An entry whose example has
# changed since is skipped — a stale cache loses a drill, it never misleads.
try:
    with open(os.path.join(HERE, "ts_predicts.json"), encoding="utf-8") as _tsd_pf:
        _TSD_PREDICTS = json.load(_tsd_pf)
except FileNotFoundError:
    _TSD_PREDICTS = {}


def _tsd_predicts(key, name, data):
    codes = {ex["code"] for ex in data["examples"]}
    out = []
    for i, p in enumerate(_TSD_PREDICTS.get(key, []), start=1):
        if p["code"] not in codes:
            continue
        ex = _pr(f"tsm-{key}-predict{i}", f"Read the inference: {p['title']}", p["code"], p["name"], p["type"],
                 hints=["Read the declaration of `" + p["name"] + "` and what it is initialised with.",
                        "Write the type out in full — literal types, `readonly` and all — not a wider one that also fits."],
                 why=f"The program is the worked example “{p['title']}” from {name}.")
        out.append(ex)
    return out


TS_DERIVED_COUNTS = {"order": 0, "spot": 0, "cards": 0, "output": 0, "predict": 0, "repair": 0}
_tsd_fronts = {c["front"] for w in TS_WEEKS for c in w["flashcards"]}
_tsd_fronts |= {f for cs in TS_CARDS_MORE.values() for f, _ in cs}
for _tsd_w in TS_WEEKS:
    _tsd_n = _tsd_w["week"]
    for _tsd_key in _tsd_w["concepts"]:
        _tsd_data = TS_CHAPTER_DATA.get(_tsd_key)
        assert _tsd_data, f"{_tsd_key}: scheduled in week {_tsd_n} but has no chapter data"
        _tsd_name = CONCEPTS[_tsd_key]["name"]
        # The chapter's own code was checked at plain `strict`; run it there.
        _tsd_more = TS_PRACTICE_MORE.setdefault(_tsd_n, [])
        _tsd_fit = [ex for ex in _tsd_data["examples"]
                    if _tsd_orderable(ex["code"])
                    and _TSD_MIN_ORDER_LINES <= len(_tsd_code_lines(ex["code"])) <= _TSD_MAX_ORDER_LINES
                    and all(t["output"] for t in ex["tests"])]
        _tsd_fit.sort(key=lambda ex: -len(_tsd_code_lines(ex["code"])))
        for _tsd_i, _tsd_ex in enumerate(_tsd_fit[:_TSD_ORDER_PER_CHAPTER], start=1):
            _tsd_more.append(_tsd_order(_tsd_key, _tsd_name, _tsd_ex, f"tsm-{_tsd_key}-order{_tsd_i}", ""))
            TS_DERIVED_COUNTS["order"] += 1
        _tsd_j = 0
        _tsd_r = 0
        for _tsd_p in _tsd_data["pitfalls"]:
            _tsd_ex = _tsd_spot(_tsd_key, _tsd_name, _tsd_p, f"tsm-{_tsd_key}-spot{_tsd_j + 1}", "")
            if _tsd_ex is not None:
                _tsd_j += 1
                _tsd_more.append(_tsd_ex)
                TS_DERIVED_COUNTS["spot"] += 1
                continue
            # Too spread out to click on: repair it instead (X-11).
            _tsd_ex = _tsd_repair(_tsd_key, _tsd_name, _tsd_p, f"tsm-{_tsd_key}-rp{_tsd_r + 1}")
            if _tsd_ex is not None:
                _tsd_r += 1
                _tsd_more.append(_tsd_ex)
                TS_DERIVED_COUNTS["repair"] += 1
        for _tsd_ex in _tsd_predicts(_tsd_key, _tsd_name, _tsd_data):
            _tsd_more.append(_tsd_ex)
            TS_DERIVED_COUNTS["predict"] += 1
        _tsd_texts = {q["question"] for q in _tsd_w["quiz"]}
        _tsd_k = 0
        for _tsd_p in _tsd_data["pitfalls"]:
            _tsd_q = _tsd_output_question(_tsd_name, _tsd_p, _tsd_k + 1)
            if _tsd_q is not None and _tsd_q["question"] not in _tsd_texts:
                _tsd_k += 1
                _tsd_texts.add(_tsd_q["question"])
                _tsd_w["quiz"].append(_tsd_q)
                TS_DERIVED_COUNTS["output"] += 1
        _tsd_cards_week = TS_CARDS_MORE.setdefault(_tsd_n, [])
        for _tsd_front, _tsd_back in _tsd_cards(_tsd_name, _tsd_data):
            if _tsd_front in _tsd_fronts:
                continue
            _tsd_fronts.add(_tsd_front)
            _tsd_cards_week.append((_tsd_front, _tsd_back))
            TS_DERIVED_COUNTS["cards"] += 1
print(f"  derived from chapters: {TS_DERIVED_COUNTS['cards']} cards, "
      f"{TS_DERIVED_COUNTS['order']} order, {TS_DERIVED_COUNTS['spot']} spot exercises, "
      f"{TS_DERIVED_COUNTS['output']} code-output questions, {TS_DERIVED_COUNTS['predict']} predict drills, {TS_DERIVED_COUNTS['repair']} repairs")

# X-07: every compiler error a chapter shows has a glossary entry, so its
# TsErrorLinks badge leads somewhere. Add missing ones to ts_errors_more.py.
import json as _tsd_json
import re as _tsd_re
with open(os.path.join(HERE, "..", "src", "data", "ts_errors.json"), encoding="utf-8") as _tsd_f:
    _tsd_glossary = {e["code"] for e in _tsd_json.load(_tsd_f)}
_tsd_shown = {}
for _tsd_key, _tsd_data in TS_CHAPTER_DATA.items():
    _tsd_texts = [e["message"] for e in _tsd_data["errors"]]
    _tsd_texts += [p["wrong_shows"] for p in _tsd_data["pitfalls"] if p["wrong_label"] != "Prints:"]
    for _tsd_t in _tsd_texts:
        for _tsd_code in _tsd_re.findall(r"error TS(\d+)", _tsd_t):
            _tsd_shown.setdefault(int(_tsd_code), _tsd_key)
_tsd_missing = sorted(c for c in _tsd_shown if c not in _tsd_glossary)
assert _TSO_COLLECT or not _tsd_missing, \
    "X-07: chapters show errors the glossary lacks: " + ", ".join(f"TS{c} ({_tsd_shown[c]})" for c in _tsd_missing)
