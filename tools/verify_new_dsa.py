# -*- coding: utf-8 -*-
"""Type-check and run every NEW_DSA reference solution against its tests, and
confirm every starter FAILS (so no blank or stub is decorative).

    python tools/verify_new_dsa.py

Reuses the TypeScript course's verifier (tools/verify_ts_course.py) for the
mechanics — same type-checker, same Node flags, same output normalisation as
the app's judge — and only supplies a different list of exercises.
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import verify_ts_course as V  # noqa: E402
from new_dsa import topic_exercises  # noqa: E402

SEED = os.path.join(HERE, "..", "src-tauri", "seeds", "new_dsa.json")


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass

    with open(SEED, encoding="utf-8") as f:
        course = json.load(f)
    work = [(f"{t['key']}/{section}", ex) for t in course["topics"] for section, ex in topic_exercises(t)]

    batch = [(ex["id"], V.compose(ex["solution"], ex), "strict") for _w, ex in work]
    batch += [(ex["id"] + "\0starter", V.compose(ex["starter"], ex), "strict") for _w, ex in work]
    diags = V.typecheck_batch(batch)

    failures = []
    for where, ex in work:
        d = diags.get(ex["id"]) or []
        if d:
            failures.append(f"{ex['id']} ({where}): SOLUTION DOES NOT TYPE-CHECK\n"
                            + V.format_diagnostics(V.compose(ex["solution"], ex), d))

    ok, ver = V.node_supports_type_stripping()
    if not ok:
        print(f"error: Node {ver} cannot run TypeScript — need 22.6+", file=sys.stderr)
        return 2
    args = V.ts_node_args()
    runnable = [(w, ex) for w, ex in work if not diags.get(ex["id"])]
    with ThreadPoolExecutor(max_workers=max(2, os.cpu_count() or 4)) as pool:
        for r in pool.map(lambda p: V.check_solution(p[0], p[1], args), runnable):
            failures.extend(r)
        for r in pool.map(
            lambda p: V.check_starter(p[0], p[1], args, bool(diags.get(p[1]["id"] + "\0starter"))),
            work,
        ):
            failures.extend(r)

    for f_ in failures:
        print("FAIL " + f_, file=sys.stderr)
    print(f"\n{len(work)} NEW_DSA solutions type-checked and run, starters checked, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
