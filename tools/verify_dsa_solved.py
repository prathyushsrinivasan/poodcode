# -*- coding: utf-8 -*-
"""Compile and run every DSA-curriculum Solved Example on its sample input.

    python tools/verify_dsa_solved.py

Each example's `code` (static Java methods) is wrapped in a class with a `main`
that prints `sample_call`; the output must equal `sample_output`, so the sample
shown on the page is what the code really produces. Needs a JDK (javac, java).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, "..", "src-tauri", "seeds", "dsa_curriculum.json")


def main():
    if not (shutil.which("javac") and shutil.which("java")):
        print("error: javac/java not found; install a JDK", file=sys.stderr)
        return 2
    course = json.load(open(SEED, encoding="utf-8"))
    examples = [(u["key"], e) for s in course["stages"] for u in s["units"] for e in u.get("solved_examples", [])]
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (key, e) in enumerate(examples):
            d = os.path.join(tmp, f"ex{i}")
            os.makedirs(d)
            src = ("public class Main {\n" + e["code"] +
                   "    public static void main(String[] args) {\n"
                   f"        System.out.println({e['sample_call']});\n    }}\n}}\n")
            with open(os.path.join(d, "Main.java"), "w", encoding="utf-8") as f:
                f.write(src)
            c = subprocess.run(["javac", "Main.java"], cwd=d, capture_output=True, text=True)
            if c.returncode:
                failures.append(f"{key}/{e['title']}: does not compile\n{c.stderr}")
                continue
            r = subprocess.run(["java", "Main"], cwd=d, capture_output=True, text=True, timeout=30)
            got = r.stdout.strip()
            if got != e["sample_output"]:
                failures.append(f"{key}/{e['title']}: printed {got!r}, page says {e['sample_output']!r}")
    for f_ in failures:
        print("FAIL " + f_, file=sys.stderr)
    print(f"{len(examples)} solved examples compiled and run, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
