# -*- coding: utf-8 -*-
"""Run every Backend Lab reference solution through Node and check it produces
the expected output.

This is the fast authoring loop; src-tauri/tests/verify_backend_course.rs proves
the same thing through the REAL judge that the app uses. Both must pass.

    python tools/verify_backend.py            # verify the generated seed
    python tools/verify_backend.py --starters # also confirm starters FAIL

Judging rules are copied from src-tauri/src/judge.rs `normalize`: drop \\r, strip
trailing whitespace per line, drop trailing blank lines.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, "..", "src-tauri", "seeds", "backend_course.json")
TIMEOUT = 20  # generous; the app's judge allows 6s per case on a warm machine


def normalize(s):
    lines = [ln.rstrip() for ln in s.replace("\r", "").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def run(code, stdin, workdir):
    path = os.path.join(workdir, "main.js")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    try:
        p = subprocess.run(
            ["node", "main.js"], cwd=workdir, input=stdin, capture_output=True,
            text=True, encoding="utf-8", timeout=TIMEOUT,
        )
        return p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1


def all_exercises(track):
    for p in track["projects"]:
        for s in p["steps"]:
            for ex in s["exercises"]:
                yield f"P{p['number']}/{s['key']}", ex
        if p.get("final_build"):
            yield f"P{p['number']}/final", p["final_build"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--starters", action="store_true",
                    help="also assert every starter FAILS (so the blank matters)")
    ap.add_argument("--only", default="", help="substring filter on exercise id")
    args = ap.parse_args()

    with open(SEED, encoding="utf-8") as f:
        track = json.load(f)

    failures = []
    checked = 0
    for where, ex in all_exercises(track):
        if args.only and args.only not in ex["id"]:
            continue
        with tempfile.TemporaryDirectory() as d:
            for i, t in enumerate(ex["tests"], start=1):
                out, err, rc = run(ex["solution"], t["input"], d)
                got, want = normalize(out), normalize(t["output"])
                if got != want:
                    failures.append(
                        f"{ex['id']} ({where}) case {i}\n"
                        f"    stdin:    {t['input']!r}\n"
                        f"    expected: {want!r}\n"
                        f"    got:      {got!r}\n"
                        f"    exit={rc} stderr={err.strip()[:400]!r}"
                    )
                    break
            else:
                checked += 1

        if args.starters and ex["kind"] != "fix":
            with tempfile.TemporaryDirectory() as d:
                t = ex["tests"][0]
                out, _, _ = run(ex["starter"], t["input"], d)
                if normalize(out) == normalize(t["output"]):
                    failures.append(f"{ex['id']}: the STARTER already passes — the blank is not load-bearing")

        if args.starters and ex["kind"] == "fix":
            with tempfile.TemporaryDirectory() as d:
                passed_all = True
                for t in ex["tests"]:
                    out, _, _ = run(ex["starter"], t["input"], d)
                    if normalize(out) != normalize(t["output"]):
                        passed_all = False
                        break
                if passed_all:
                    failures.append(f"{ex['id']}: the buggy starter PASSES — there is no bug to fix")

    for f_ in failures:
        print("FAIL " + f_, file=sys.stderr)
    print(f"\n{checked} exercise solutions verified, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
