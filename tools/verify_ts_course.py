# -*- coding: utf-8 -*-
"""Type-check and run every TypeScript course reference solution, and check it
produces the expected output.

This is the fast authoring loop; src-tauri/tests/verify_ts_course.rs proves the
same thing through the REAL judge that the app uses. Both must pass.

    python tools/verify_ts_course.py               # verify the generated seed
    python tools/verify_ts_course.py --starters    # also confirm starters FAIL
    python tools/verify_ts_course.py --only w6-    # filter by exercise id
    python tools/verify_ts_course.py --types-only  # skip execution (fast)

Requires Node 22.6+ on PATH (older Node cannot strip types) and an installed
`node_modules/typescript` for the type-check pass. A missing type-checker is a
HARD ERROR, not a skip: silently "verifying" without checking types is exactly
the hole this whole change exists to close.

Two passes, because a TypeScript exercise can now fail in two different ways:

1. **Type-check** — every program is compiled at its week's strictness preset
   (see INDEXED_FROM_WEEK in tools/typescript_course.py). All programs go
   through ONE Node process (tools/ts_typecheck.mjs) with a shared lib cache;
   spawning `tsc` 1,100 times would add ~15 minutes.
2. **Execute** — each solution is run per test case and its stdout compared.

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
SEED = os.path.join(HERE, "..", "src-tauri", "seeds", "ts_course.json")
CHECKER = os.path.join(HERE, "ts_typecheck.mjs")
RUN_TIMEOUT = 20  # generous; the app's judge allows 6s per case on a warm machine


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
    ok, ver = node_supports_type_stripping()
    major, minor = (int(x) for x in ver.split(".")[:2])
    native = major >= 24 or (major == 23 and minor >= 6) or (major == 22 and minor >= 18)
    return ["--no-warnings"] if native else ["--experimental-strip-types", "--no-warnings"]


def all_exercises(course):
    """Every judged exercise, with a human-readable location for error messages."""
    for wk in course["weeks"]:
        where = f"W{wk['number']}"
        for lesson in wk["lessons"]:
            for ex in lesson["exercises"]:
                yield f"{where}/{lesson['key']}", ex
        cap = wk.get("capstone")
        if cap:
            for ex in (cap.get("exercise"), cap.get("stretch")):
                if ex:
                    yield f"{where}/capstone", ex
        for fam in wk.get("practice", []):
            for ex in fam["exercises"]:
                yield f"{where}/practice/{fam['key']}", ex


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


def compose(code, ex):
    """The program the judge actually compiles: the learner's code plus the
    exercise's hidden harness. Mirrors `judge_with` in src-tauri/src/judge.rs —
    if the two ever disagree about this, the verifier stops proving anything."""
    harness = ex.get("harness") or ""
    if not harness.strip():
        return code
    return code.rstrip() + "\n" + harness


def check_solution(where, ex, args):
    """The solution must pass every case. Returns a list of failures."""
    failures = []
    for i, t in enumerate(ex["tests"], start=1):
        out, stderr, rc = run_program(compose(ex["solution"], ex), t["input"], args)
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

    A starter that does not type-check counts as failing — that is the normal
    case for a fill-in-the-blank, where `____` is not even valid syntax.
    """
    if type_failed:
        return []
    # A type-level exercise has no other way to fail: the type-check IS the
    # grade, so a starter that compiles is a starter that passes.
    if ex.get("judge_mode") == "types":
        return [f"{ex['id']} ({where}): the type-level starter already COMPILES — nothing to solve"]
    for t in ex["tests"]:
        out, _stderr, rc = run_program(compose(ex["starter"], ex), t["input"], args)
        # A crash counts as failing, exactly as the real judge scores it: a
        # nonzero exit is a runtime error, never "accepted".
        if rc != 0:
            return []
        if normalize(out) != normalize(t["output"]):
            return []
    kind = "buggy starter" if ex["kind"] == "fix" else "starter"
    return [f"{ex['id']} ({where}): the {kind} already PASSES — nothing to solve"]


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
    # em-dashes in these messages. Without this the summary raises
    # UnicodeEncodeError *after* failures were found — and that crash exits 0,
    # reporting a clean run for a course that does not verify.
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
        course = json.load(f)

    work = [(w, ex) for (w, ex) in all_exercises(course)
            if not args_ns.only or args_ns.only in ex["id"]]
    if not work:
        print("no exercises matched", file=sys.stderr)
        return 1

    failures = []

    # ---- Pass 1: type-check solutions (and starters when asked) ----
    # Everything is checked as `code + harness`, the same single file the judge
    # compiles — which is what makes the check meaningful for a function
    # exercise (the driver has to agree with the signature) and is the ENTIRE
    # grade for a type-level one.
    batch = [(ex["id"], compose(ex["solution"], ex), ex.get("strictness") or "strict")
             for (_w, ex) in work]
    if args_ns.starters:
        batch += [(ex["id"] + "\0starter", compose(ex["starter"], ex),
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
                + format_diagnostics(compose(ex["solution"], ex), d)
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
            # Only run solutions that type-check; a type error already failed.
            # Type-level exercises are never run at all — pass 1 was their grade.
            runnable = [(w, ex) for (w, ex) in work
                        if not (diags.get(ex["id"]) or []) and ex.get("judge_mode") != "types"]
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
    # a red squiggle. One that now fails to compile still counts as failing, but
    # it teaches something different, so surface the list rather than hide it.
    if compile_time_fixes:
        print(f"\nnote: {len(compile_time_fixes)} 'fix' starters fail at COMPILE time "
              f"rather than at run time — worth an authoring review:")
        print("  " + " ".join(sorted(compile_time_fixes)))

    mode = "type-checked" if args_ns.types_only else "type-checked and run"
    print(f"\n{len(work)} exercise solutions {mode}, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
