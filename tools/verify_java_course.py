# -*- coding: utf-8 -*-
"""Compile and run every Java course reference solution, and check it produces
the expected output.

This is the fast authoring loop; src-tauri/tests/verify_java_course.rs proves the
same thing through the REAL judge that the app uses. Both must pass.

    python tools/verify_java_course.py              # verify the generated seed
    python tools/verify_java_course.py --starters   # also confirm starters FAIL
    python tools/verify_java_course.py --only j5-   # filter by exercise id

Requires a JDK on PATH (`javac` and `java`). If neither is installed the script
says so and exits non-zero rather than pretending to have verified anything.

Each exercise is compiled ONCE into its own scratch directory and then run per
test case, mirroring the app's compile-once/run-per-case judge. Exercises are
checked in parallel because `javac` startup dominates the wall clock.

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
SEED = os.path.join(HERE, "..", "src-tauri", "seeds", "java_course.json")
COMPILE_TIMEOUT = 60
RUN_TIMEOUT = 20  # generous; the app's judge allows 6s per case on a warm machine


def normalize(s):
    lines = [ln.rstrip() for ln in s.replace("\r", "").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def compile_program(code, workdir):
    """Write Main.java and compile it. Returns None on success, else the error."""
    path = os.path.join(workdir, "Main.java")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    try:
        p = subprocess.run(
            ["javac", "-nowarn", "Main.java"], cwd=workdir, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=COMPILE_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return "COMPILE TIMEOUT"
    if p.returncode != 0:
        return (p.stderr or p.stdout).strip()[:600]
    return None


def hard_kill(proc):
    """Terminate a runaway child for real.

    `subprocess.run(timeout=...)` is not enough on Windows: when it gives up it
    calls `Popen.kill()` and then `communicate()` with no deadline, and for a
    CPU-spinning JVM that second call has been observed to block indefinitely —
    so a single exercise can wedge the whole run and leave an orphan `java`
    burning a core. `taskkill /T` takes down the process tree instead.

    This is not hypothetical: module 10's `j10-vs-nomemo` ships a deliberately
    un-memoized Fibonacci as its buggy starter and is asked for fib(60), so the
    starter sweep hits it every single run.
    """
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)
    else:
        proc.kill()


def run_program(workdir, stdin):
    proc = subprocess.Popen(
        ["java", "-XX:TieredStopAtLevel=1", "Main"], cwd=workdir,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
    )
    try:
        out, err = proc.communicate(stdin, timeout=RUN_TIMEOUT)
        return out, err, proc.returncode
    except subprocess.TimeoutExpired:
        hard_kill(proc)
        try:
            proc.communicate(timeout=RUN_TIMEOUT)
        except subprocess.TimeoutExpired:
            pass
        return "", "TIMEOUT", -1


def all_exercises(course):
    """Every judged exercise, with a human-readable location for error messages."""
    for mod in course["weeks"]:
        where = f"M{mod['number']}"
        for lesson in mod["lessons"]:
            for ex in lesson["exercises"]:
                yield f"{where}/{lesson['key']}", ex
        cap = mod.get("capstone")
        if cap:
            for ex in (cap.get("exercise"), cap.get("stretch")):
                if ex:
                    yield f"{where}/capstone", ex
        for fam in mod.get("practice", []):
            for ex in fam["exercises"]:
                yield f"{where}/practice/{fam['key']}", ex


def check_solution(where, ex):
    """The solution must compile and pass every case. Returns a list of failures."""
    failures = []
    with tempfile.TemporaryDirectory() as d:
        err = compile_program(ex["solution"], d)
        if err:
            return [f"{ex['id']} ({where}): SOLUTION DOES NOT COMPILE\n    {err}"]
        for i, t in enumerate(ex["tests"], start=1):
            out, stderr, rc = run_program(d, t["input"])
            got, want = normalize(out), normalize(t["output"])
            if got != want:
                failures.append(
                    f"{ex['id']} ({where}) case {i}\n"
                    f"    stdin:    {t['input']!r}\n"
                    f"    expected: {want!r}\n"
                    f"    got:      {got!r}\n"
                    f"    exit={rc} stderr={stderr.strip()[:400]!r}"
                )
                break
    return failures


def check_starter(where, ex):
    """The starter must FAIL, or the blank is decorative. A starter that does not
    compile counts as failing, which is the normal case for a fill-in-the-blank."""
    with tempfile.TemporaryDirectory() as d:
        if compile_program(ex["starter"], d) is not None:
            return []  # does not compile => cannot pass => the blank matters
        for t in ex["tests"]:
            out, _stderr, rc = run_program(d, t["input"])
            # A crash counts as failing, exactly as the real judge scores it: a
            # nonzero exit is a runtime error, never "accepted". Without this a
            # starter that prints the right lines and THEN throws would look
            # like it passes, because only stdout was being compared.
            if rc != 0:
                return []
            if normalize(out) != normalize(t["output"]):
                return []  # fails at least one case => good
    kind = "buggy starter" if ex["kind"] == "fix" else "starter"
    return [f"{ex['id']} ({where}): the {kind} already PASSES — nothing to solve"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--starters", action="store_true",
                    help="also assert every starter FAILS (so the blank is load-bearing)")
    ap.add_argument("--only", default="", help="substring filter on exercise id")
    ap.add_argument("--jobs", type=int, default=max(2, (os.cpu_count() or 4)),
                    help="parallel exercises (javac startup dominates)")
    args = ap.parse_args()

    for tool in ("javac", "java"):
        if shutil.which(tool) is None:
            print(f"error: {tool} is not on PATH — install a JDK to verify the Java course",
                  file=sys.stderr)
            return 2

    with open(SEED, encoding="utf-8") as f:
        course = json.load(f)

    work = [(w, ex) for (w, ex) in all_exercises(course)
            if not args.only or args.only in ex["id"]]
    if not work:
        print("no exercises matched", file=sys.stderr)
        return 1

    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for result in pool.map(lambda p: check_solution(*p), work):
            failures.extend(result)
        if args.starters:
            for result in pool.map(lambda p: check_starter(*p), work):
                failures.extend(result)

    for f_ in failures:
        print("FAIL " + f_, file=sys.stderr)
    print(f"\n{len(work)} exercise solutions checked, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
