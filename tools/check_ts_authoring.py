# -*- coding: utf-8 -*-
"""Check per-chapter TypeScript Mastery content on its own, without rebuilding
the seeds (see tools/mastery_ts_chapter_kit.py).

    python tools/check_ts_authoring.py tools/mastery_ts_x_m3.py
    python tools/check_ts_authoring.py tools/mastery_ts_fam_m3.py --report
    python tools/check_ts_authoring.py tools/mastery_ts_x_m3.py --only ts_generics

Runs the content file(s) against the real chapter kit, computes every expected
output by running the references (as tools/gen_ts_outputs.py would), then
applies every check tools/verify_ts_mastery.py makes — solution type-checks and
passes, starter fails, a diagnose prompt quotes an error the starter really
emits, forbidden tokens — plus the week scope lint (mastery_ts_scope.py) and a
determinism re-run. Writes nothing: several of these can run at once.

`--report` prints each chapter's count against the targets
(mastery_ts_chapter_check.py), counting what the seeds already have.
"""

import argparse
import ast
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify_ts_course as vc  # noqa: E402
import verify_ts_mastery as vm  # noqa: E402


def pick(path, names):
    """Compile only the named top-level assignments and functions of `path`."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), path)
    keep = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            keep.append(node)
        elif isinstance(node, ast.Assign) and any(getattr(t, "id", "") in names for t in node.targets):
            keep.append(node)
    found = {getattr(n, "name", None) or n.targets[0].id for n in keep}
    missing = set(names) - found
    assert not missing, f"{path}: {sorted(missing)} not found"
    return compile(ast.Module(body=keep, type_ignores=[]), path, "exec")


def namespace():
    track = next(t for t in vm.load("mastery.json") if t["key"] == "typescript")
    ns = {"os": os, "json": json, "re": re, "HERE": HERE, "__name__": "authoring",
          "TS_WEEKS": [{"week": w["week"], "concepts": w["concepts"]} for w in track["weeks"]],
          "TS_PRACTICE_MORE": {}, "_TS_TIER": {"warm-up": "Easy", "core": "Medium", "stretch": "Hard"}}
    exec(pick(os.path.join(HERE, "mastery_defs.py"), ["_TS_SCAFFOLD", "TS_INDEXED_FROM_WEEK"]), ns)
    exec(pick(os.path.join(HERE, "mastery_ts_practice.py"), ["_TW_PRELUDE", "_tl"]), ns)
    exec(pick(os.path.join(HERE, "mastery_ts_kit.py"), ["_week_strictness"]), ns)
    pending = []

    def computed(eid, solution, inputs, strictness=""):
        inputs = list(inputs)
        assert inputs, f"{eid}: needs at least one input"
        assert len(set(inputs)) == len(inputs), f"{eid}: repeats a test input"
        tests = [{"input": i, "output": None} for i in inputs]
        pending.append((eid, solution, tests))
        return tests

    ns["_computed"] = computed
    path = os.path.join(HERE, "mastery_ts_chapter_kit.py")
    with open(path, encoding="utf-8") as f:
        exec(compile(f.read(), path, "exec"), ns)
    return ns, pending, track


def scope_problems(ns, exercises):
    sc = {"re": re, "_sc_re": re}
    exec(pick(os.path.join(HERE, "mastery_ts_scope.py"),
              ["TS_SCOPE_RULES", "TS_SCOPE_EXEMPT", "_sc_strip", "_sc_uses"]), sc)
    out = []
    for chapter, ex in exercises:
        week = ns["TS_CHAPTER_WEEK"][chapter]
        for label, src in (("solution", ex["solution"]), ("starter", ex["starter"])):
            body = sc["_sc_strip"](src)
            for token, allowed_from in sc["TS_SCOPE_RULES"]:
                if week < allowed_from and sc["_sc_uses"](body, token):
                    out.append(f"{ex['id']} ({label}): uses {token!r}, which week {allowed_from} teaches — "
                               f"{chapter} is week {week}")
    return out


def report(ns, track, only):
    targets = {"predict": 3, "diagnose": 3, "retype": 3, "design": 3, "fix": 2, "families": 4}
    keys = sorted(ns["TS_CHAPTER_WEEK"], key=len, reverse=True)
    fam_re = re.compile(r"-fam-(.+)-\d+$")
    counts = {k: {t: 0 for t in targets} for k in keys}
    fams = {k: set() for k in keys}
    seen = set()
    items = [ex for w in track["weeks"] for ex in w["practice"]]
    items += [ex for exs in ns["TS_CHAPTER_PRACTICE"].values() for ex in exs]
    for ex in items:
        if ex["id"] in seen:
            continue  # already in the seeds from an earlier build
        seen.add(ex["id"])
        key = next((k for k in keys if ex["id"].startswith(f"tsm-{k}-")), None)
        if key is None:
            continue
        m = fam_re.search(ex["id"])
        if m:
            fams[key].add(m.group(1))
        elif ex["kind"] in counts[key]:
            counts[key][ex["kind"]] += 1
    for k in keys:
        counts[k]["families"] = len(fams[k])
    chapters = sorted(ns["TS_CHAPTER_WEEK"], key=lambda k: (ns["TS_CHAPTER_WEEK"][k], k))
    print("\nchapter (week): count/target — * short")
    for k in chapters:
        if only and only not in k:
            continue
        cells = [f"{t} {counts[k][t]}/{want}{'*' if counts[k][t] < want else ''}" for t, want in targets.items()]
        print(f"  {k} (w{ns['TS_CHAPTER_WEEK'][k]}): " + "  ".join(cells))


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--only", default="", help="substring of an exercise id or chapter key")
    ap.add_argument("--report", action="store_true", help="per-chapter counts against the targets")
    ap.add_argument("--jobs", type=int, default=max(2, (os.cpu_count() or 4) // 2))
    a = ap.parse_args()

    ns, pending, track = namespace()
    for path in a.files:
        with open(path, encoding="utf-8") as f:
            exec(compile(f.read(), path, "exec"), ns)

    exercises = [(ch, ex) for ch, exs in ns["TS_CHAPTER_PRACTICE"].items() for ex in exs
                 if not a.only or a.only in ex["id"]]
    ids = [ex["id"] for _, ex in exercises]
    failures = [f"duplicate id {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]

    # Expected outputs, computed from the references — run twice, so an output
    # that depends on timing or iteration order is caught here, not in CI.
    args = vc.ts_node_args()
    wanted = {ex["id"] for _, ex in exercises}
    todo = [(eid, sol, tests) for eid, sol, tests in pending if eid in wanted]

    def compute(item):
        eid, sol, tests = item
        for t in tests:
            out, err, rc = vc.run_program(sol, t["input"], args)
            if rc != 0:
                return f"{eid}: the reference exits {rc} on input {t['input']!r}: {err.strip()[:400]}"
            again, _e, _rc = vc.run_program(sol, t["input"], args)
            if vc.normalize(again) != vc.normalize(out):
                return f"{eid}: the reference prints different things on two runs of {t['input']!r}"
            if not vc.normalize(out).strip():
                return f"{eid}: the reference prints nothing on input {t['input']!r}"
            t["output"] = vc.normalize(out)
        return None

    with ThreadPoolExecutor(max_workers=a.jobs) as pool:
        failures += [r for r in pool.map(compute, todo) if r]

    work = [(f"authoring/{ch}", ex) for ch, ex in exercises
            if all(t["output"] is not None for t in ex["tests"])]
    failures += vm.check_work(work, False, a.jobs)
    failures += scope_problems(ns, exercises)

    for f in failures:
        print("FAIL " + f)
    by_kind = {}
    for _, ex in exercises:
        by_kind[ex["kind"]] = by_kind.get(ex["kind"], 0) + 1
    print(f"{len(exercises)} checked ({', '.join(f'{n} {k}' for k, n in sorted(by_kind.items()))}), "
          f"{len(failures)} failure(s)")
    if a.report:
        report(ns, track, a.only)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
