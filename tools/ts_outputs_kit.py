# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Computed expected outputs for TypeScript content.
#
# The rule everywhere in this app is that an expected output is produced by
# running the reference solution, never typed by hand. Authoring hundreds of
# problems, projects and worked examples by pasting outputs back in is how
# typos get in, so content authored after this file names only its INPUTS:
#
#     tests=_computed("tsm-w1-sum-of-line", solution, ["1 2 3", "-4", ...])
#
# and the outputs come from tools/ts_outputs.json, a cache written by
# `python tools/gen_ts_outputs.py`, which type-checks each solution and runs it
# on every input with the same Node flags as the judge. Each cache entry is
# pinned to a hash of (solution, strictness, inputs): edit any of them and the
# entry goes stale, and the build refuses to ship a stale or missing output —
# exactly like tools/ts_starters.json.
#
# gen_ts_outputs.py runs gen_seed.py with POODCODE_COLLECT_OUTPUTS=1, in which
# mode a stale entry yields empty outputs and is recorded in _TSO_PENDING
# instead of failing; the script computes those, writes the cache, and re-runs
# the build for real.
#
# exec()'d by gen_seed.py before any TypeScript content file that uses it.
# ---------------------------------------------------------------------------

import hashlib as _tso_hashlib

_TSO_PATH = os.path.join(HERE, "ts_outputs.json")
_TSO_COLLECT = os.environ.get("POODCODE_COLLECT_OUTPUTS") == "1"
try:
    with open(_TSO_PATH, encoding="utf-8") as _tso_f:
        _TSO_CACHE = json.load(_tso_f)
except FileNotFoundError:
    _TSO_CACHE = {}
_TSO_PENDING = []   # items whose outputs must be (re)computed
_TSO_SEEN = set()   # every id requested this build, so the cache can be pruned


def _tso_hash(solution, inputs, strictness):
    h = _tso_hashlib.sha256()
    for part in [solution, strictness or "strict", *inputs]:
        h.update(part.encode("utf-8"))
        h.update(b"\0")
    return h.hexdigest()[:20]


def _computed(eid, solution, inputs, strictness=""):
    """The (input, output) test list for `solution`, outputs from the cache."""
    assert eid not in _TSO_SEEN, f"{eid}: computed-output id used twice"
    _TSO_SEEN.add(eid)
    inputs = list(inputs)
    assert inputs, f"{eid}: needs at least one input"
    assert len(set(inputs)) == len(inputs), f"{eid}: repeats a test input"
    digest = _tso_hash(solution, inputs, strictness)
    entry = _TSO_CACHE.get(eid)
    if entry and entry.get("hash") == digest:
        return [{"input": i, "output": o} for (i, o) in zip(inputs, entry["outputs"])]
    _TSO_PENDING.append({"id": eid, "hash": digest, "solution": solution,
                         "inputs": inputs, "strictness": strictness or "strict"})
    if _TSO_COLLECT:
        return [{"input": i, "output": ""} for i in inputs]
    raise AssertionError(
        f"{eid}: expected outputs are missing or stale — run `python tools/gen_ts_outputs.py`"
    )


def _compiler_says(eid, source, expect_code, strictness=""):
    """What the compiler reports for `source`: a list of {code, line, msg}, from
    the same cache. `expect_code` (e.g. 2322) must be the first diagnostic, so a
    snippet that stops producing the error a lesson is about fails the build."""
    assert eid not in _TSO_SEEN, f"{eid}: computed-output id used twice"
    _TSO_SEEN.add(eid)
    digest = _tso_hash(source, ["<diagnostics>"], strictness)
    entry = _TSO_CACHE.get(eid)
    if entry and entry.get("hash") == digest:
        diags = entry["diagnostics"]
        assert diags, f"{eid}: the snippet compiles cleanly — it no longer shows TS{expect_code}"
        assert diags[0]["code"] == expect_code, (
            f"{eid}: expected TS{expect_code} first, the compiler reports "
            + ", ".join(f"TS{d['code']}" for d in diags))
        return diags
    _TSO_PENDING.append({"id": eid, "hash": digest, "solution": source, "inputs": [],
                         "strictness": strictness or "strict", "kind": "diagnostics"})
    if _TSO_COLLECT:
        return [{"code": expect_code, "line": 1, "msg": "(pending)"}]
    raise AssertionError(
        f"{eid}: compiler output is missing or stale — run `python tools/gen_ts_outputs.py`"
    )


def _tso_dump_pending():
    """Collect mode: hand the pending items (and the live ids) to the script."""
    if not _TSO_COLLECT:
        return
    out = os.environ.get("POODCODE_COLLECT_FILE") or os.path.join(HERE, ".ts_outputs_pending.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"pending": _TSO_PENDING, "seen": sorted(_TSO_SEEN)}, f)
