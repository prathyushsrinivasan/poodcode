# -*- coding: utf-8 -*-
"""Design drills from the TypeScript chapters' worked examples (X-10).

A worked example that declares a type and then uses it becomes a "design"
exercise: the declaration is blanked and the code that uses it stays, so the
shape has to be recovered from its use. It is judged on the example's output
and on a hidden claim that the learner's type is `Equal` to the original.

Candidates are proven here before they are cached: the example plus the claim
must compile. mastery_ts_derived.py builds the exercises from
tools/ts_designs.json and skips any whose example has changed since.

    python tools/gen_ts_designs.py && python tools/gen_seed.py
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = os.path.join(HERE, "..", "src-tauri", "seeds")
OUT = os.path.join(HERE, "ts_designs.json")
PER_CHAPTER = 2
EXAMPLE = re.compile(r"^#### (.+?)\n```ts\n(.*?)\n```", re.S | re.M)
PRELUDE = ("type Equal<X, Y> =\n  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;\n"
           "type Expect<T extends true> = T;\n")


def u16(code, offset):
    return len(code.encode("utf-16-le")[: offset * 2].decode("utf-16-le"))


def claim(name, shape):
    return f"type __Design = {shape};\ntype _d1 = Expect<Equal<{name}, __Design>>;\n"


def main():
    with open(os.path.join(SEEDS, "concepts.json"), encoding="utf-8") as f:
        concepts = [c for c in json.load(f) if c.get("language") == "typescript"]
    items, meta = [], {}
    for c in concepts:
        for sec in re.split(r"^### ", c["lesson"], flags=re.M):
            if not (sec.startswith("Worked examples") or sec.startswith("More worked examples")):
                continue
            for title, code in EXAMPLE.findall(sec):
                iid = f"{c['key']}#{len(meta)}"
                items.append({"id": iid, "src": code + "\n"})
                meta[iid] = (c["key"], title.strip(), code + "\n")
    r = subprocess.run(["node", os.path.join(HERE, "ts_signatures.mjs")], input=json.dumps(items),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit(r.stderr)
    candidates = []
    for res in json.loads(r.stdout):
        key, title, code = meta[res["id"]]
        for t in res["types"]:
            a, b = u16(code, t["start"]), u16(code, t["end"])
            decl = code[a:b]
            rest = code[:a] + code[b:]
            # Worth designing: an object shape or a union, used later in the program.
            if not t["shape"] or not re.search(r"[{|]", t["shape"]) or len(t["shape"]) > 160:
                continue
            if not re.search(r"(?<![\w$])" + re.escape(t["name"]) + r"(?![\w$])", code[b:]):
                continue
            if "\n" in decl.strip() and len(decl.splitlines()) > 8:
                continue
            candidates.append({"key": key, "title": title, "code": code, "name": t["name"], "decl": decl,
                               "shape": t["shape"], "starter": code[:a] + "____" + code[b:], "rest": rest})
    check = subprocess.run(["node", os.path.join(HERE, "ts_typecheck.mjs")],
                           input=json.dumps([{"id": str(i), "src": c["code"] + "\n" + PRELUDE + claim(c["name"], c["shape"]),
                                              "preset": "strict"} for i, c in enumerate(candidates)]),
                           capture_output=True, text=True, encoding="utf-8")
    if check.returncode != 0:
        sys.exit(check.stderr)
    clean = {d["id"] for d in json.loads(check.stdout) if not d["diagnostics"]}
    out = {}
    for i, c in enumerate(candidates):
        picks = out.setdefault(c.pop("key"), [])
        c.pop("rest")
        if str(i) in clean and len(picks) < PER_CHAPTER and not any(p["code"] == c["code"] for p in picks):
            picks.append(c)
    out = {k: v for k, v in sorted(out.items()) if v}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"{sum(len(v) for v in out.values())} design drills across {len(out)} chapters -> {os.path.relpath(OUT)}")


if __name__ == "__main__":
    main()
