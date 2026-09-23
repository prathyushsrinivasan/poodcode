"""Every Problem Library TypeScript starter must pass the judge's type-check.

The judge type-checks every TypeScript run at `--strict` before executing it
(src-tauri/src/tscheck.rs). Until tools/gen_ts_starters.mjs existed, all 607
TypeScript starters were copied JavaScript and every one failed that check — so
a learner opening any Library problem in TypeScript hit compile errors before
typing a character. This makes that impossible to regress.

  * Full-program starters are checked exactly as shipped.
  * Function-harness stubs are checked with a stand-in call below them, so a
    stub whose declared types disagree with what the harness passes fails here
    instead of at the learner's first run. (The real glue is Rust —
    harness::wrap — and tests/exec_judge.rs proves it end to end per type.)

Batch-checked through tools/ts_typecheck.mjs in one process — about two
minutes for the whole library, rather than ~20 minutes spawning `tsc` per starter.

Usage: python tools/verify_ts_starters.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEED = os.path.join(ROOT, "src-tauri", "seeds", "problems.json")

# What the harness passes for each declared type (harness.rs::node_parse).
_ARG = {
    "int": "0", "long": "0", "double": "0", "bool": "false", "string": '""',
    "int[]": "[] as number[]", "long[]": "[] as number[]", "double[]": "[] as number[]",
    "string[]": "[] as string[]",
}
_RET = {
    "int": "number", "long": "number", "double": "number", "bool": "boolean",
    "string": "string", "int[]": "number[]", "long[]": "number[]",
    "double[]": "number[]", "string[]": "string[]",
}


def with_call(stub, spec):
    args = ", ".join(_ARG[p["type"]] for p in spec["params"])
    return f"{stub}\nconst __check: {_RET[spec['returns']]} = {spec['name']}({args});\nvoid __check;\n"


def main():
    problems = json.load(open(SEED, encoding="utf-8"))
    items, missing = [], []
    for p in problems:
        src = p["starter_code"].get("typescript")
        if src is None:
            missing.append(p["slug"])
            continue
        if p.get("function_spec"):
            src = with_call(src, p["function_spec"])
        items.append({"id": p["slug"], "src": src, "preset": "strict"})

    r = subprocess.run(
        ["node", os.path.join(HERE, "ts_typecheck.mjs")],
        input=json.dumps(items), capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        sys.exit(f"ts_typecheck.mjs failed:\n{r.stderr}")
    failing = [o for o in json.loads(r.stdout) if o["diagnostics"]]

    for o in failing:
        print(f"FAIL {o['id']}")
        for d in o["diagnostics"][:3]:
            print(f"    L{d['line']} TS{d['code']} {d['msg']}")
    if missing:
        print(f"MISSING a TypeScript starter: {', '.join(missing)}")
    print(f"{len(items) - len(failing)}/{len(items)} TypeScript starters type-check"
          f"{'' if not missing else f'; {len(missing)} missing'}")
    sys.exit(1 if failing or missing else 0)


if __name__ == "__main__":
    main()
