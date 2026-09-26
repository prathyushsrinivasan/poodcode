# -*- coding: utf-8 -*-
"""Predict-the-type drills from the TypeScript chapters' worked examples
(TS_MASTERY_ROADMAP.md X-10).

Every worked example in a TypeScript lesson is a whole program the learner has
just read. This asks the checker — with the judge's own options, via
tools/ts_typecheck.mjs — what type it gives each top-level `const` declared
without an annotation, keeps the ones worth predicting, and caches them in
tools/ts_predicts.json. mastery_ts_derived.py turns each into a `predict`
exercise in the week that schedules the chapter (and skips any whose example
has since changed, so a stale cache can only lose drills, never mislead).

    python tools/gen_ts_predicts.py && python tools/gen_seed.py
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = os.path.join(HERE, "..", "src-tauri", "seeds")
OUT = os.path.join(HERE, "ts_predicts.json")
PER_CHAPTER = 3

EXAMPLE = re.compile(r"^#### (.+?)\n```ts\n(.*?)\n```", re.S | re.M)
TOO_EASY = {"string", "number", "boolean", "void", "undefined", "null", "unknown", "never"}


def examples(lesson):
    """(title, code) for each worked example, in the lesson's example sections."""
    out = []
    for sec in re.split(r"^### ", lesson, flags=re.M):
        if sec.startswith("Worked examples") or sec.startswith("More worked examples"):
            out += [(t.strip(), c + "\n") for t, c in EXAMPLE.findall(sec)]
    return out


def interest(t):
    """How much reading this inference teaches: literal types, unions, tuples,
    object shapes, `readonly` and generic arguments are the point; a bare
    `number[]` or a class name is not. 0 means skip."""
    if t in TOO_EASY or len(t) > 70 or len(t) < 2:
        return 0
    if any(bad in t for bad in ("any", "typeof", "import(", "__", "=>", "Iterator")):
        return 0
    if t in ("string[]", "number[]", "boolean[]") or t.replace("_", "a").isidentifier():
        return 0
    if t.startswith('"') and t.endswith('"') and "|" not in t and len(t) > 14:
        return 0  # a long sentence's literal type: copying, not predicting
    score = 0
    score += 2 if "|" in t else 0
    score += 2 if '"' in t or t.lstrip("-").replace(".", "").isdigit() or t in ("true", "false") else 0
    score += 2 if "{" in t else 0
    score += 2 if "readonly" in t else 0
    score += 2 if t.startswith("[") or ", " in t and "[" in t else 0
    score += 1 if "<" in t else 0
    return score


def main():
    with open(os.path.join(SEEDS, "concepts.json"), encoding="utf-8") as f:
        concepts = [c for c in json.load(f) if c.get("language") == "typescript"]
    items, meta = [], {}
    for c in concepts:
        for i, (title, code) in enumerate(examples(c["lesson"])):
            if "typeof" in code or "@file" in code:
                continue  # the drill bans `typeof`; a scene using it could not be answered
            iid = f"{c['key']}#{i}"
            items.append({"id": iid, "src": code, "preset": "strict", "infer": True})
            meta[iid] = (c["key"], title, code)
    r = subprocess.run(["node", os.path.join(HERE, "ts_typecheck.mjs")], input=json.dumps(items),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit(r.stderr)
    cands = {}
    for res in json.loads(r.stdout):
        if res["diagnostics"]:
            continue
        key, title, code = meta[res["id"]]
        for d in res["consts"]:
            score = interest(d["type"])
            if score >= 2:
                cands.setdefault(key, []).append((score, title, code, d["name"], d["type"]))
    out = {}
    for key, cs in cands.items():
        picks = out.setdefault(key, [])
        # Best first, one per worked example.
        for score, title, code, name, t in sorted(cs, key=lambda c: -c[0]):
            if len(picks) < PER_CHAPTER and not any(p["code"] == code for p in picks):
                picks.append({"title": title, "code": code, "name": name, "type": t})
    out = {k: v for k, v in sorted(out.items()) if v}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"{sum(len(v) for v in out.values())} predict drills across {len(out)} chapters -> {os.path.relpath(OUT)}")


if __name__ == "__main__":
    main()
