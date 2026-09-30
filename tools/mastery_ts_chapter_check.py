# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The per-chapter practice targets (TS_MASTERY_ROADMAP.md X-10, X-11, X-19),
# checked once every week's practice is attached.
#
# An exercise counts for a chapter when its id says so: `tsm-<chapter>-…`. That
# covers the chapter-derived exercises (mastery_ts_derived.py, ids like
# `tsm-ts_generics-rt1`) and the per-chapter content (mastery_ts_chapter_kit.py,
# `tsm-ts_generics-xrt1`, `tsm-ts_generics-fam-pairs-3`). Practice authored per
# WEEK (`tsm-w12-…`) is extra and counts for no chapter.
#
# exec()'d by gen_seed.py after mastery_ts_attach.py.
# ---------------------------------------------------------------------------

TS_CHAPTER_TARGETS = {"predict": 3, "diagnose": 3, "retype": 3, "design": 3, "fix": 2, "families": 4}

# Longest key first, so `ts_generic_constraints` is not read as `ts_generics`.
_cc_keys = sorted(TS_CHAPTER_WEEK, key=len, reverse=True)
_cc_re = __import__("re").compile(r"-fam-(.+)-\d+$")
TS_CHAPTER_COUNTS = {k: {kind: 0 for kind in TS_CHAPTER_TARGETS} for k in TS_CHAPTER_WEEK}
_cc_families = {k: set() for k in TS_CHAPTER_WEEK}
for _cc_w in TS_WEEKS:
    for _cc_ex in _cc_w["practice"]:
        _cc_key = next((k for k in _cc_keys if _cc_ex["id"].startswith(f"tsm-{k}-")), None)
        if _cc_key is None:
            continue
        _cc_fam = _cc_re.search(_cc_ex["id"])
        if _cc_fam:
            _cc_families[_cc_key].add(_cc_fam.group(1))
        elif _cc_ex["kind"] in TS_CHAPTER_COUNTS[_cc_key]:
            TS_CHAPTER_COUNTS[_cc_key][_cc_ex["kind"]] += 1
for _cc_key, _cc_fams in _cc_families.items():
    TS_CHAPTER_COUNTS[_cc_key]["families"] = len(_cc_fams)

TS_CHAPTER_SHORT = {
    k: {kind: want - c[kind] for kind, want in TS_CHAPTER_TARGETS.items() if c[kind] < want}
    for k, c in TS_CHAPTER_COUNTS.items()
}
TS_CHAPTER_SHORT = {k: v for k, v in TS_CHAPTER_SHORT.items() if v}
assert not TS_CHAPTER_SHORT, (
    f"X-10/X-11/X-19: {len(TS_CHAPTER_SHORT)} chapter(s) below the per-chapter practice targets "
    f"{TS_CHAPTER_TARGETS} — e.g. " + ", ".join(f"{k} {v}" for k, v in list(TS_CHAPTER_SHORT.items())[:5])
)
