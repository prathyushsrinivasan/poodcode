# -*- coding: utf-8 -*-
"""Type-check and run every Projects-track reference solution, and check it
produces the expected output.

This is the fast authoring loop; src-tauri/tests/verify_projects.rs proves the
same thing through the REAL judge that the app uses. Both must pass.

    python tools/verify_projects.py               # verify the generated seed
    python tools/verify_projects.py --starters    # also confirm starters FAIL
    python tools/verify_projects.py --only m3-    # filter by exercise id
    python tools/verify_projects.py --types-only  # skip execution (fast)

Requires Node 22.6+ on PATH (older Node cannot strip types) and an installed
`node_modules/typescript` for the type-check pass. A missing type-checker is a
HARD ERROR, not a skip.

Two passes, mirroring tools/verify_ts_course.py:

1. **Type-check** — every program is compiled at its exercise's strictness
   preset (`strict+indexed` throughout this track). All programs go through ONE
   Node process (tools/ts_typecheck.mjs) with a shared lib cache.
2. **Execute** — each solution is run per test case and its stdout compared.

WHY THIS TRACK NEEDS ITS OWN VERIFIER rather than reusing the Backend Lab's:
that one runs `main.js` through Node and never type-checks, because the Backend
Lab is JavaScript. Here the types are half the content — an exercise whose
solution does not type-check is broken even if it prints the right thing — so
the type pass is not optional.

Judging rules are copied from src-tauri/src/judge.rs `normalize`: drop \\r, strip
trailing whitespace per line, drop trailing blank lines.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, "..", "src-tauri", "seeds", "projects.json")
CHECKER = os.path.join(HERE, "ts_typecheck.mjs")
RUN_TIMEOUT = 25  # a server program binds a port and replays requests


def normalize(s):
    lines = [ln.rstrip() for ln in s.replace("\r", "").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def node_supports_type_stripping():
    """Node >= 22.6 can run .ts directly; older Node cannot run these at all."""
    try:
        out = subprocess.run(["node", "--version"], capture_output=True, text=True,
                             timeout=30).stdout.strip().lstrip("v")
        major, minor = (int(x) for x in out.split(".")[:2])
    except Exception:
        return False, "unknown"
    return (major > 22 or (major == 22 and minor >= 6)), out


def ts_node_args():
    """Mirror src-tauri/src/exec.rs `ts_node_args`: the flag is only needed on
    the Node versions where type stripping is not yet the default."""
    _ok, ver = node_supports_type_stripping()
    major, minor = (int(x) for x in ver.split(".")[:2])
    native = major >= 24 or (major == 23 and minor >= 6) or (major == 22 and minor >= 18)
    return ["--no-warnings"] if native else ["--experimental-strip-types", "--no-warnings"]


def all_exercises(track):
    """Every judged exercise, with a human-readable location for error messages."""
    for project in track["projects"]:
        for module in project["modules"]:
            where = f"M{module['number']}"
            for step in module["steps"]:
                for ex in step["exercises"]:
                    yield f"{where}/{step['key']}", ex
            if module.get("final_build"):
                yield f"{where}/final", module["final_build"]


# --------------------------------------------------------------------------
# Pass 1 — type-check
# --------------------------------------------------------------------------

def typecheck_batch(items):
    """items: [(key, source, preset)]. Returns {key: [diagnostic, ...]}."""
    if not items:
        return {}
    payload = [{"id": k, "src": s, "preset": p} for (k, s, p) in items]
    proc = subprocess.run(
        ["node", CHECKER], input=json.dumps(payload), capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        raise SystemExit(
            "error: type-check pass failed to run:\n" + (proc.stderr or proc.stdout)
        )
    return {r["id"]: r["diagnostics"] for r in json.loads(proc.stdout)}


def format_diagnostics(source, diags, limit=3):
    src = source.split("\n")
    out = []
    for d in diags[:limit]:
        out.append(f"    TS{d['code']} line {d['line']}: {d['msg']}")
        if 0 < d["line"] <= len(src):
            out.append(f"        | {src[d['line'] - 1]}")
    if len(diags) > limit:
        out.append(f"    … and {len(diags) - limit} more")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Pass 2 — execute
# --------------------------------------------------------------------------

def run_program(code, stdin, args):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "main.ts")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(code)
        try:
            p = subprocess.run(
                ["node", *args, "main.ts"], cwd=d, input=stdin, capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=RUN_TIMEOUT,
            )
            return p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired:
            return "", "TIMEOUT", -1


def check_solution(where, ex, args):
    """The solution must pass every case. Returns a list of failures."""
    failures = []
    for i, t in enumerate(ex["tests"], start=1):
        out, stderr, rc = run_program(ex["solution"], t["input"], args)
        got, want = normalize(out), normalize(t["output"])
        if rc != 0 or got != want:
            failures.append(
                f"{ex['id']} ({where}) case {i}\n"
                f"    stdin:    {t['input']!r}\n"
                f"    expected: {want!r}\n"
                f"    got:      {got!r}\n"
                f"    exit={rc} stderr={stderr.strip()[:400]!r}"
            )
            break
    return failures


def check_starter(where, ex, args, type_failed):
    """The starter must FAIL, or the blank is decorative.

    A starter that does not type-check counts as failing — the normal case for a
    fill-in-the-blank, where `____` is not valid syntax to begin with.
    """
    if type_failed:
        return []
    for t in ex["tests"]:
        out, _stderr, rc = run_program(ex["starter"], t["input"], args)
        # A crash counts as failing, exactly as the real judge scores it.
        if rc != 0:
            return []
        if normalize(out) != normalize(t["output"]):
            return []
    kind = {"fix": "buggy starter"}.get(ex["kind"], "starter")
    return [f"{ex['id']} ({where}): the {kind} already PASSES — nothing to solve"]


def check_reveals_match(track):
    """A module's `reference` is the "reveal solution" for the whole module, and
    it is prose-adjacent — nothing runs it. So at minimum assert it exists and is
    not a stub, since an empty reveal is worse than no reveal button.
    """
    problems = []
    for project in track["projects"]:
        for m in project["modules"]:
            if not m["authored"]:
                continue
            if len(m.get("reference") or "") < 200:
                problems.append(
                    f"M{m['number']} ({m['key']}): reference implementation is "
                    f"missing or a stub"
                )
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--starters", action="store_true",
                    help="also assert every starter FAILS (so the blank is load-bearing)")
    ap.add_argument("--only", default="", help="substring filter on exercise id")
    ap.add_argument("--types-only", action="store_true",
                    help="run the type-check pass only (fast; skips execution)")
    ap.add_argument("--jobs", type=int, default=max(2, (os.cpu_count() or 4)),
                    help="parallel exercises for the execution pass")
    args_ns = ap.parse_args()

    # A Windows console defaults to a legacy codepage that cannot encode the
    # em-dashes in these messages; without this the summary raises
    # UnicodeEncodeError *after* failures were found, and that crash exits 0.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass

    if shutil.which("node") is None:
        print("error: node is not on PATH — install Node.js 22.6+", file=sys.stderr)
        return 2
    if not os.path.exists(CHECKER):
        print(f"error: {CHECKER} is missing", file=sys.stderr)
        return 2

    with open(SEED, encoding="utf-8") as f:
        track = json.load(f)

    work = [(w, ex) for (w, ex) in all_exercises(track)
            if not args_ns.only or args_ns.only in ex["id"]]
    if not work:
        print("no exercises matched", file=sys.stderr)
        return 1

    failures = list(check_reveals_match(track)) if not args_ns.only else []

    # ---- Pass 1: type-check ----
    batch = [(ex["id"], ex["solution"], ex.get("strictness") or "strict")
             for (_w, ex) in work]
    if args_ns.starters:
        batch += [(ex["id"] + "\0starter", ex["starter"],
                   ex.get("strictness") or "strict")
                  for (_w, ex) in work]
    diags = typecheck_batch(batch)

    starter_type_failed = set()
    compile_time_fixes = []
    for where, ex in work:
        d = diags.get(ex["id"]) or []
        if d:
            failures.append(
                f"{ex['id']} ({where}): SOLUTION DOES NOT TYPE-CHECK "
                f"[{ex.get('strictness') or 'strict'}]\n"
                + format_diagnostics(ex["solution"], d)
            )
        if args_ns.starters and (diags.get(ex["id"] + "\0starter") or []):
            starter_type_failed.add(ex["id"])
            if ex["kind"] == "fix":
                compile_time_fixes.append(ex["id"])

    # ---- Pass 2: execute ----
    if not args_ns.types_only:
        ok, ver = node_supports_type_stripping()
        if not ok:
            print(f"error: Node {ver} cannot run TypeScript — need 22.6+", file=sys.stderr)
            return 2
        node_args = ts_node_args()
        with ThreadPoolExecutor(max_workers=args_ns.jobs) as pool:
            runnable = [(w, ex) for (w, ex) in work if not (diags.get(ex["id"]) or [])]
            for result in pool.map(lambda p: check_solution(p[0], p[1], node_args), runnable):
                failures.extend(result)
            if args_ns.starters:
                for result in pool.map(
                    lambda p: check_starter(p[0], p[1], node_args,
                                            p[1]["id"] in starter_type_failed),
                    work,
                ):
                    failures.extend(result)

    for f_ in failures:
        print("FAIL " + f_, file=sys.stderr)

    # A `fix` exercise is meant to fail at RUN time — the lesson is the bug, not
    # a red squiggle. One that fails to compile still counts as failing, but it
    # teaches something different, so surface the list rather than hide it.
    if compile_time_fixes:
        print(f"\nnote: {len(compile_time_fixes)} 'fix' starters fail at COMPILE time "
              f"rather than at run time — worth an authoring review:")
        print("  " + " ".join(sorted(compile_time_fixes)))

    mode = "type-checked" if args_ns.types_only else "type-checked and run"
    print(f"\n{len(work)} exercise solutions {mode}, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
