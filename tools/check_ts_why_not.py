# -*- coding: utf-8 -*-
"""Why-not notes for the TypeScript quiz banks (tools/mastery_ts_why_not.py):
a worklist to author from, and a check for a notes file on its own.

    python tools/check_ts_why_not.py --worklist 3 > m3.json   # month 3's questions
    python tools/check_ts_why_not.py tools/mastery_ts_whynot_m3.py --month 3

A question belongs to the month of the first week whose bank holds it (week 27
counts as month 6). The worklist is every authored single-choice question of
that month: its text, options, right answer, explanation and any code. The
check runs a notes file, confirms every key is a real question and every wrong
option (and no right one) has a non-empty note, and with --month reports what
of that month is still missing. Writes nothing.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = os.path.join(HERE, "..", "src-tauri", "seeds")


def month_of(week):
    for m, last in enumerate((4, 8, 13, 17, 22), start=1):
        if week <= last:
            return m
    return 6


def questions():
    """{text: {"week", "variants": [question, ...]}} for every single-choice question."""
    with open(os.path.join(SEEDS, "mastery.json"), encoding="utf-8") as f:
        track = next(t for t in json.load(f) if t.get("language") == "typescript")
    out = {}
    for w in track["weeks"]:
        for q in w["quiz"]:
            if q.get("kind") or "answers" in q:
                continue
            e = out.setdefault(q["question"], {"week": w["week"], "variants": []})
            if all(v["options"] != q["options"] for v in e["variants"]):
                e["variants"].append(q)
    return out


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--worklist", type=int, help="print month N's questions as JSON")
    ap.add_argument("--month", type=int, help="report month N's questions still without notes")
    a = ap.parse_args()
    qs = questions()

    if a.worklist:
        items = []
        for text, e in qs.items():
            if month_of(e["week"]) != a.worklist:
                continue
            v = e["variants"][0]
            wrong = sorted({o for q in e["variants"] for i, o in enumerate(q["options"]) if i != q["answer"]})
            items.append({"week": e["week"], "question": text, "options": v["options"],
                          "right": v["options"][v["answer"]], "wrong": wrong,
                          "explanation": v.get("explanation", ""), "code": v.get("code", "")})
        items.sort(key=lambda it: it["week"])
        json.dump(items, sys.stdout, indent=1, ensure_ascii=False)
        print()
        return 0

    ns = {"TS_WHY_NOT": {}}
    for path in a.files:
        with open(path, encoding="utf-8") as f:
            exec(compile(f.read(), path, "exec"), ns)
    notes = ns["TS_WHY_NOT"]
    failures = []
    for text, by_option in notes.items():
        e = qs.get(text)
        if e is None:
            failures.append(f"not a question in any TypeScript bank: {text[:90]!r}")
            continue
        for q in e["variants"]:
            right = q["options"][q["answer"]]
            if right in by_option:
                failures.append(f"{text[:70]!r}: has a note for the RIGHT answer {right[:50]!r}")
            for i, o in enumerate(q["options"]):
                if i != q["answer"] and not (by_option.get(o) or "").strip():
                    failures.append(f"{text[:70]!r}: no note for wrong option {o[:60]!r}")
        known = {o for q in e["variants"] for o in q["options"]}
        for o in by_option:
            if o not in known:
                failures.append(f"{text[:70]!r}: note for an option it does not have: {o[:60]!r}")
        vals = [v.strip() for v in by_option.values()]
        if len(set(vals)) != len(vals):
            failures.append(f"{text[:70]!r}: two options share the same note — say what is wrong with EACH")
        for o, v in by_option.items():
            if len(v) > 400:
                failures.append(f"{text[:70]!r}: the note for {o[:40]!r} is {len(v)} chars; keep it to one or two sentences")
    for f in failures:
        print("FAIL " + f)
    print(f"{len(notes)} question(s) annotated, {len(failures)} failure(s)")
    if a.month:
        todo = [t for t, e in qs.items() if month_of(e["week"]) == a.month and t not in notes]
        print(f"month {a.month}: {len(todo)} question(s) still without notes")
        for t in todo[:10]:
            print("  - " + t[:100])
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
