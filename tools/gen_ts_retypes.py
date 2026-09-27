# -*- coding: utf-8 -*-
"""Retype drills from the TypeScript chapters' worked examples (X-10).

A worked example whose functions are fully annotated becomes a "retype"
exercise: every parameter and return annotation of those functions is replaced
with `any`, and the learner puts real types back. It is judged on the example's
real output and on hidden claims — `Equal<Parameters<typeof f>[i], T>` and
`Equal<ReturnType<typeof f>, R>` against the original annotations — which
`any` cannot satisfy.

This caches the signature spans (parsed by tools/ts_signatures.mjs) in
tools/ts_retypes.json; mastery_ts_derived.py builds the exercises and skips any
entry whose example has changed since.

    python tools/gen_ts_retypes.py && python tools/gen_seed.py
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = os.path.join(HERE, "..", "src-tauri", "seeds")
OUT = os.path.join(HERE, "ts_retypes.json")
PER_CHAPTER = 2

EXAMPLE = re.compile(r"^#### (.+?)\n```ts\n(.*?)\n```", re.S | re.M)


def u16(code, offset):
    """A JavaScript (UTF-16) string offset as a Python index."""
    return len(code.encode("utf-16-le")[: offset * 2].decode("utf-16-le"))


def any_starter(code, fns):
    """The example with every parameter and return annotation of `fns` replaced
    by `any` (`Promise<any>` for an async function's return)."""
    spans = []
    for f in fns:
        spans += [(u16(code, p["start"]), u16(code, p["end"]), "any") for p in f["params"]]
        spans.append((u16(code, f["ret"]["start"]), u16(code, f["ret"]["end"]), "Promise<any>" if f.get("async") else "any"))
    for a, b, text in sorted(spans, reverse=True):
        code = code[:a] + text + code[b:]
    return code


def main():
    with open(os.path.join(SEEDS, "concepts.json"), encoding="utf-8") as f:
        concepts = [c for c in json.load(f) if c.get("language") == "typescript"]
    items, meta = [], {}
    for c in concepts:
        for sec in re.split(r"^### ", c["lesson"], flags=re.M):
            if not (sec.startswith("Worked examples") or sec.startswith("More worked examples")):
                continue
            for i, (title, code) in enumerate(EXAMPLE.findall(sec)):
                iid = f"{c['key']}#{len(meta)}"
                items.append({"id": iid, "src": code + "\n"})
                meta[iid] = (c["key"], title.strip(), code + "\n")
    r = subprocess.run(["node", os.path.join(HERE, "ts_signatures.mjs")], input=json.dumps(items),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit(r.stderr)
    candidates = []
    for res in json.loads(r.stdout):
        # A type predicate (`x is T`), an assertion signature or a `never`
        # return cannot be restated as a type in a claim; leave those out.
        fns = [f for f in res["fns"]
               if "any" not in f["ret"]["text"] and all("any" not in p["text"] for p in f["params"])
               and not re.search(r"\bis\b|^asserts\b|^never$", f["ret"]["text"])]
        if not fns:
            continue
        key, title, code = meta[res["id"]]
        candidates.append({"key": key, "title": title, "code": code, "fns": fns, "starter": any_starter(code, fns)})
    # The starter must compile as it stands — "it runs, and its types say
    # nothing" — so an example where `any` spreads into new errors is left out.
    check = subprocess.run(["node", os.path.join(HERE, "ts_typecheck.mjs")],
                           input=json.dumps([{"id": str(i), "src": c["starter"], "preset": "strict"}
                                             for i, c in enumerate(candidates)]),
                           capture_output=True, text=True, encoding="utf-8")
    if check.returncode != 0:
        sys.exit(check.stderr)
    clean = {d["id"] for d in json.loads(check.stdout) if not d["diagnostics"]}
    out = {}
    for i, c in enumerate(candidates):
        picks = out.setdefault(c.pop("key"), [])
        if str(i) in clean and len(picks) < PER_CHAPTER:
            picks.append(c)
    out = {k: v for k, v in sorted(out.items()) if v}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"{sum(len(v) for v in out.values())} retype drills across {len(out)} chapters -> {os.path.relpath(OUT)}")


if __name__ == "__main__":
    main()
