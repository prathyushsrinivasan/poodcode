# -*- coding: utf-8 -*-
"""Fast authoring loop for the TypeScript Mastery programme.

Type-checks and runs, outside the app:

  * every exercise on the TypeScript Learn chapters (concepts.json),
  * every Mastery week's practice, coding final and project acceptance tests
    (mastery.json, TypeScript track),

and confirms every starter FAILS. The same checks as tools/verify_ts_course.py
(whose helpers this reuses), pointed at the Learn catalog and the Mastery seed.

    python tools/verify_ts_mastery.py                   # everything
    python tools/verify_ts_mastery.py --only ts_using   # filter by exercise id / chapter key
    python tools/verify_ts_mastery.py --weeks 11-14     # just those Mastery weeks
    python tools/verify_ts_mastery.py --types-only      # skip execution

src-tauri/tests/verify_exercises.rs and verify_mastery.rs prove the same things
through the REAL judge. This exists because they take minutes and this takes
seconds for a filtered run.
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify_ts_course as vc  # noqa: E402

SEEDS = os.path.join(HERE, "..", "src-tauri", "seeds")


def load(name):
    with open(os.path.join(SEEDS, name), encoding="utf-8") as f:
        return json.load(f)


def week_range(spec):
    if not spec:
        return None
    out = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out


def as_exercise(eid, kind, starter, solution, tests, strictness=""):
    """A final or a project, shaped like an exercise so the shared checks apply."""
    return {
        "id": eid, "kind": kind, "starter": starter, "solution": solution,
        "tests": tests, "strictness": strictness or "strict", "harness": "",
        "judge_mode": "", "forbid": [], "prompt": "",
    }


def collect(only, weeks, include_learn, include_mastery):
    work = []
    if include_learn:
        for c in load("concepts.json"):
            if c.get("language") != "typescript":
                continue
            for ex in c.get("exercises", []):
                if only and only not in ex["id"] and only not in c["key"]:
                    continue
                work.append((f"learn/{c['key']}", ex))
    if include_mastery:
        track = next(t for t in load("mastery.json") if t["key"] == "typescript")
        for w in track["weeks"]:
            n = w["week"]
            if weeks and n not in weeks:
                continue
            where = f"mastery/w{n}"
            for ex in w.get("practice", []):
                if not only or only in ex["id"]:
                    work.append((where + "/practice", ex))
            exam = w.get("exam")
            if exam and (not only or only in f"final-w{n}"):
                work.append((where + "/final", as_exercise(
                    f"final-w{n}", "final", exam["starter"], exam["solution"],
                    exam["tests"], exam.get("strictness"))))
            proj = w.get("project_spec")
            if proj and (not only or only in f"project-w{n}"):
                work.append((where + "/project", as_exercise(
                    f"project-w{n}", "project", proj["starter"], proj["solution"],
                    proj["tests"], proj.get("strictness"))))
    return work


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="substring of an exercise id or chapter key")
    ap.add_argument("--weeks", default="", help="Mastery weeks, e.g. 11-14 or 3,5")
    ap.add_argument("--learn-only", action="store_true")
    ap.add_argument("--mastery-only", action="store_true")
    ap.add_argument("--types-only", action="store_true")
    ap.add_argument("--jobs", type=int, default=max(2, (os.cpu_count() or 4)))
    a = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass

    work = collect(a.only, week_range(a.weeks), not a.mastery_only, not a.learn_only)
    if not work:
        print("nothing matched", file=sys.stderr)
        return 1

    failures = []
    batch = []
    for _w, ex in work:
        preset = ex.get("strictness") or "strict"
        batch.append((ex["id"], vc.compose(ex["solution"], ex), preset))
        batch.append((ex["id"] + "\0starter", vc.compose(ex["starter"], ex), preset))
    diags = vc.typecheck_batch(batch)

    starter_type_failed = set()
    for where, ex in work:
        d = diags.get(ex["id"]) or []
        if d:
            failures.append(f"{ex['id']} ({where}): SOLUTION DOES NOT TYPE-CHECK "
                            f"[{ex.get('strictness') or 'strict'}]\n"
                            + vc.format_diagnostics(vc.compose(ex["solution"], ex), d))
        failures.extend(vc.check_forbidden(where, ex))
        sd = diags.get(ex["id"] + "\0starter") or []
        if ex.get("kind") == "diagnose":
            failures.extend(vc.check_quoted_error(where, ex, sd))
        if sd:
            starter_type_failed.add(ex["id"])
        elif ex.get("judge_mode") == "types":
            failures.append(f"{ex['id']} ({where}): the type-level starter already COMPILES")

    if not a.types_only:
        args = vc.ts_node_args()

        def run_one(item):
            where, ex = item
            out = []
            if ex.get("judge_mode") != "types":
                if not ex.get("tests"):
                    out.append(f"{ex['id']} ({where}): no tests")
                    return out
                out += vc.check_solution(where, ex, args)
                if ex["id"] not in starter_type_failed:
                    out += vc.check_starter(where, ex, args, False)
            return out

        with ThreadPoolExecutor(max_workers=a.jobs) as pool:
            for res in pool.map(run_one, work):
                failures.extend(res)

    for f in failures:
        print("FAIL " + f)
    print(f"{len(work)} checked, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
