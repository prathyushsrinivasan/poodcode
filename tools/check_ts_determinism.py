# -*- coding: utf-8 -*-
"""Determinism check for timer-driven TypeScript content (TS_MASTERY_ROADMAP.md M6-03).

A program whose output depends on how fast the machine is will pass on an idle
laptop and fail for a learner running a build in the background — twice already
a chapter demo raced 10 ms steps against a 25 ms timeout and flipped under load.
This finds every program that uses real time (timers, clocks, setImmediate):

  * Mastery practice, problems, finals, alternates, projects and arc projects,
  * every Learn exercise on a TypeScript chapter,
  * every worked example and pitfall in a TypeScript lesson whose printed
    output the lesson shows,

and runs each one several times at once, with every core kept busy by the
other runs, comparing each run with the output the content promises.

    python tools/check_ts_determinism.py            # 3 runs each
    python tools/check_ts_determinism.py --runs 5

Exit status 1 if any run differs.
"""

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify_ts_course as vc  # noqa: E402
import verify_ts_mastery as vm  # noqa: E402

TIMING = re.compile(r"\b(setTimeout|setInterval|setImmediate|Date\.now|performance\.now|new Date\(\))")
FENCE = re.compile(r"```(\w*)\n(.*?)\n```", re.S)


def lesson_programs():
    """(id, code, [(input, expected)]) for each lesson code block the lesson
    shows the output of: a ```ts block followed by Input:/Prints: blocks."""
    out = []
    for c in vm.load("concepts.json"):
        if c.get("language") != "typescript":
            continue
        lesson = c.get("lesson", "")
        blocks = [(m.start(), m.group(1), m.group(2)) for m in FENCE.finditer(lesson)]
        for i, (pos, lang, code) in enumerate(blocks):
            if lang != "ts" or not TIMING.search(code):
                continue
            cases, j, pending_input = [], i + 1, ""
            while j < len(blocks) and blocks[j][1] == "text":
                label = lesson[blocks[j - 1][0]:blocks[j][0]].rsplit("```", 1)[-1].strip()
                if label.endswith("Input:"):
                    pending_input = blocks[j][2]
                elif label.endswith("Prints:"):
                    expected = "" if blocks[j][2] == "(nothing)" else blocks[j][2]
                    cases.append((pending_input, expected))
                    pending_input = ""
                else:
                    break
                j += 1
            if cases:
                out.append((f"{c['key']}-lesson-block{i}", code + "\n", cases))
    return out


def exercise_programs():
    out = []
    for where, ex in vm.collect("", None, True, True):
        if ex.get("judge_mode") == "types" or not ex.get("tests"):
            continue
        program = vc.compose(ex["solution"], ex)
        if TIMING.search(program):
            out.append((f"{where}/{ex['id']}", program, [(t["input"], t["output"]) for t in ex["tests"]]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass

    programs = exercise_programs() + lesson_programs()
    node = vc.ts_node_args()
    jobs = [(pid, code, inp, want) for pid, code, cases in programs for inp, want in cases for _ in range(args.runs)]
    print(f"{len(programs)} timer-driven programs, {len(jobs)} runs")

    def run(job):
        pid, code, inp, want = job
        got, err, rc = vc.run_program(code, inp, node)
        return pid, inp, vc.normalize(want), vc.normalize(got) if rc == 0 else f"(exit {rc}) {err.strip()[:200]}"

    # Twice as many workers as cores: every run competes for CPU, which is the
    # condition a timing race needs in order to show itself.
    failures = {}
    with ThreadPoolExecutor(max_workers=2 * (os.cpu_count() or 4)) as pool:
        for pid, inp, want, got in pool.map(run, jobs):
            if want != got:
                failures.setdefault((pid, inp), (want, got))
    for (pid, inp), (want, got) in sorted(failures.items()):
        print(f"FLAKY {pid} on input {inp!r}\n  expected: {want!r}\n  got:      {got!r}")
    print(f"{len(programs)} checked, {len(failures)} nondeterministic")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
