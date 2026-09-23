# -*- coding: utf-8 -*-
"""Compute the expected outputs for TypeScript content that names only its
inputs (see tools/ts_outputs_kit.py), then rebuild the seeds.

    python tools/gen_ts_outputs.py

1. Runs gen_seed.py in collect mode, which records every item whose cached
   outputs are missing or stale instead of failing.
2. Type-checks each such reference solution (at its strictness) and refuses
   to cache anything from a solution that does not compile.
3. Runs it on every input with the judge's Node flags; a nonzero exit or a
   timeout is an error, never an output.
4. Writes tools/ts_outputs.json (entries for ids no longer used are pruned),
   then runs gen_seed.py normally, which now finds every output.
"""

import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify_ts_course as vc  # noqa: E402

CACHE = os.path.join(HERE, "ts_outputs.json")


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass
    with tempfile.TemporaryDirectory() as d:
        pending_file = os.path.join(d, "pending.json")
        env = dict(os.environ, POODCODE_COLLECT_OUTPUTS="1", POODCODE_COLLECT_FILE=pending_file)
        p = subprocess.run([sys.executable, os.path.join(HERE, "gen_seed.py")], env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if p.returncode != 0 or not os.path.exists(pending_file):
            print(p.stdout[-3000:], p.stderr[-6000:], sep="\n")
            print("error: gen_seed.py failed in collect mode", file=sys.stderr)
            return 1
        with open(pending_file, encoding="utf-8") as f:
            collected = json.load(f)

    pending, seen = collected["pending"], set(collected["seen"])
    try:
        with open(CACHE, encoding="utf-8") as f:
            cache = json.load(f)
    except FileNotFoundError:
        cache = {}

    failures = []
    if pending:
        diags = vc.typecheck_batch([(it["id"], it["solution"], it["strictness"]) for it in pending])
        args = vc.ts_node_args()

        def run(it):
            d = diags.get(it["id"]) or []
            if it.get("kind") == "diagnostics":
                # A lesson's "what the compiler says" snippet: the diagnostics
                # ARE the output. The build checks the expected code is first.
                return it, d, ""
            if d:
                return it, None, "does not type-check:\n" + vc.format_diagnostics(it["solution"], d)
            outs = []
            for inp in it["inputs"]:
                out, err, rc = vc.run_program(it["solution"], inp, args)
                if rc != 0:
                    return it, None, f"exit {rc} on input {inp!r}: {err.strip()[:500]}"
                outs.append(vc.normalize(out))
            return it, outs, ""

        with ThreadPoolExecutor(max_workers=max(2, os.cpu_count() or 4)) as pool:
            for it, outs, err in pool.map(run, pending):
                if err:
                    failures.append(f"{it['id']}: {err}")
                elif it.get("kind") == "diagnostics":
                    cache[it["id"]] = {"hash": it["hash"], "diagnostics": outs}
                else:
                    cache[it["id"]] = {"hash": it["hash"], "outputs": outs}

    pruned = sorted(k for k in cache if k not in seen)
    for k in pruned:
        del cache[k]
    with open(CACHE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(sorted(cache.items())), f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"computed {len(pending) - len(failures)} item(s), pruned {len(pruned)}, "
          f"{len(cache)} cached")
    if failures:
        for msg in failures:
            print("FAIL " + msg)
        return 1

    p = subprocess.run([sys.executable, os.path.join(HERE, "gen_seed.py")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print(p.stdout[-3000:], p.stderr[-6000:], sep="\n")
        return 1
    print("seeds rebuilt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
