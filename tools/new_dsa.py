# -*- coding: utf-8 -*-
"""Generate src-tauri/seeds/new_dsa.json — the NEW_DSA course.

NEW_DSA.md is the map: a 13-phase syllabus, and one 16-section template that
every topic follows. Each topic is authored in its own module(s); this file
assembles them and enforces the template, so a topic cannot ship with a
section missing, a guided problem without its four layered hints, or a
"new problem" in Mastery that the learner already met earlier in the topic.

    python tools/new_dsa.py            # write the seed
    python tools/verify_new_dsa.py     # then prove every solution and starter

Expected outputs come from Python reference implementations (brute force where
practical), never from the TypeScript being tested.
"""

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import new_dsa_sw_learn as SWL  # noqa: E402
import new_dsa_sw_practice as SWP  # noqa: E402
import new_dsa_sw_refs as SWR  # noqa: E402

OUT = os.path.join(HERE, "..", "src-tauri", "seeds", "new_dsa.json")
PROBLEMS = os.path.join(HERE, "..", "src-tauri", "seeds", "problems.json")

# The template, in order (NEW_DSA.md). `key` is the topic field and the URL
# `?s=` value; the page renders exactly these, so the order lives here once.
SECTIONS = [
    ("concept", "Concept", "Understand"),
    ("mental_model", "Mental Model", "Understand"),
    ("ts_fundamentals", "TypeScript Fundamentals", "See"),
    ("patterns", "Syntax & Patterns", "See"),
    ("when_to_use", "When to Use It", "Recognize"),
    ("when_not", "When NOT to Use It", "Recognize"),
    ("examples", "Step-by-Step Examples", "See"),
    ("implementation", "Implementation", "Copy → Complete → Implement"),
    ("complexity", "Complexity", "Understand"),
    ("mistakes", "Common Mistakes", "Understand"),
    ("recognition", "Problem Recognition", "Recognize"),
    ("guided", "Guided Practice", "Apply"),
    ("independent", "Independent Practice", "Apply"),
    ("variations", "Variations", "Combine"),
    ("review", "Review", "Master"),
    ("mastery", "Mastery", "Master"),
]

HINT_LABELS = ["Nudge", "Approach", "Steps", "Code"]
VARIATION_STEPS = [
    "Basic version",
    "Different input",
    "Additional constraint",
    "Optimization requirement",
    "Combination with another technique",
]


def sliding_window():
    return {
        "key": "sliding-window",
        "title": "Sliding Window",
        "icon": "🪟",
        "phase": "Phase 5 — Core Algorithmic Patterns",
        "tagline": "Slide a range across the input and update what it holds, instead of recomputing it.",
        "est_minutes": 150,
        "prereqs": ["Arrays", "Strings", "Hashing"],
        "concept": SWL.CONCEPT,
        "mental_model": SWL.MENTAL_MODEL,
        "ts_fundamentals": SWL.TS_FUNDAMENTALS,
        "patterns": SWL.PATTERNS,
        "when_to_use": SWL.WHEN_TO_USE,
        "when_not": SWL.WHEN_NOT,
        "examples": SWL.EXAMPLES,
        "implementation": SWL.IMPLEMENTATION,
        "complexity": SWP.COMPLEXITY,
        "mistakes": SWP.MISTAKES,
        "recognition": SWP.RECOGNITION,
        "guided": SWP.GUIDED,
        "independent": SWP.INDEPENDENT,
        "variations": SWP.VARIATIONS,
        "review": SWP.REVIEW,
        "mastery": SWP.MASTERY,
    }


# ---------------------------------------------------------------------------
# Validation — the template's rules, enforced
# ---------------------------------------------------------------------------

def topic_exercises(t):
    """Every judged exercise in a topic, with the section it belongs to."""
    for ex in t["ts_fundamentals"]["drills"]:
        yield "ts_fundamentals", ex
    impl = t["implementation"]
    yield "implementation", impl["complete"]
    yield "implementation", impl["pseudocode"]["exercise"]
    yield "implementation", impl["scratch"]
    for g in t["guided"]:
        yield "guided", g["exercise"]
    for v in t["variations"]:
        if v.get("exercise"):
            yield "variations", v["exercise"]
    yield "mastery", t["mastery"]["syntax"]
    yield "mastery", t["mastery"]["implementation"]


def validate(course):
    errors = []
    problems = {p["slug"]: p for p in json.load(open(PROBLEMS, encoding="utf-8"))}

    for t in course["topics"]:
        where = t["key"]
        for key, _title, _phase in SECTIONS:
            if not t.get(key):
                errors.append(f"{where}: section '{key}' is missing or empty")

        ids = [ex["id"] for _s, ex in topic_exercises(t)]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            errors.append(f"{where}: duplicate exercise ids {sorted(dupes)}")
        for i in ids:
            if not i.startswith(f"ndsa:{t['key']}:"):
                errors.append(f"{where}: exercise id {i!r} is not namespaced ndsa:{t['key']}:")

        for g in t["guided"]:
            labels = [h["label"] for h in g["hints"]]
            if labels != HINT_LABELS:
                errors.append(f"{where}/guided/{g['key']}: hints must be exactly {HINT_LABELS}, got {labels}")
            if g["exercise"]["hints"]:
                errors.append(f"{where}/guided/{g['key']}: layered hints live on the problem, not the exercise")

        steps = [v["step"] for v in t["variations"]]
        if steps != VARIATION_STEPS:
            errors.append(f"{where}: variations must follow {VARIATION_STEPS}, got {steps}")

        m = t["mastery"]
        for part in ("understanding", "recognition"):
            if not 0 < m[part]["pass"] <= len(m[part]["questions"]):
                errors.append(f"{where}/mastery/{part}: pass mark out of range")
        if not 0 < m["application"]["need"] <= len(m["application"]["problems"]):
            errors.append(f"{where}/mastery/application: 'need' out of range")

        # Slugs must exist and be solvable in TypeScript — and Mastery's
        # "unfamiliar problem" must really be unfamiliar within this topic.
        seen_before = [p["slug"] for p in t["independent"]["problems"]] + \
                      [v["slug"] for v in t["variations"] if v.get("slug")]
        for s in seen_before + [p["slug"] for p in m["application"]["problems"]]:
            p = problems.get(s)
            if not p:
                errors.append(f"{where}: unknown problem slug {s!r}")
            elif not (p.get("starter_code") or {}).get("typescript"):
                errors.append(f"{where}: problem {s!r} has no TypeScript starter")
        for p in m["application"]["problems"]:
            if p["slug"] in seen_before:
                errors.append(f"{where}/mastery: {p['slug']!r} appears earlier in the topic, so it is not unfamiliar")

        stepper = t["mental_model"]["stepper"]
        n = len(stepper["cells"])
        for i, f in enumerate(stepper["frames"]):
            if not (0 <= f["lo"] <= n and -1 <= f["hi"] < n):
                errors.append(f"{where}/stepper frame {i}: lo/hi out of range")

        for ex in t["examples"]:
            tr = ex.get("trace")
            if tr and any(len(r) != len(tr["headers"]) for r in tr["rows"]):
                errors.append(f"{where}/examples/{ex['title']}: a trace row does not match its headers")

    return errors


def normalise(t):
    """Write every optional field out explicitly.

    Through Tauri, serde fills a missing field with its default; the mock
    backend (`npm run dev:mock`) serves this JSON as it is. Emitting the
    defaults here means both paths hand the page the same shape."""
    for e in t["examples"]:
        e.setdefault("lines", [])
        e.setdefault("question", None)
        e.setdefault("trace", None)
        e.setdefault("notes", [])
        e.setdefault("takeaway", "")
    for v in t["variations"]:
        v.setdefault("exercise", None)
        v.setdefault("slug", "")
    for p in t["independent"]["problems"] + t["mastery"]["application"]["problems"]:
        p.setdefault("nudge", "")
        p.setdefault("reveal", "")
    return t


def cross_check_refs():
    """The deque reference computes the large generated case, which the brute
    force cannot. Prove the two agree on many small arrays first."""
    rng = random.Random(1)
    for _ in range(400):
        n = rng.randint(1, 12)
        nums = [rng.randint(-5, 5) for _ in range(n)]
        k = rng.randint(1, n)
        if SWR.window_maxima(nums, k) != SWR.window_maxima_fast(nums, k):
            raise SystemExit(f"window_maxima_fast disagrees on {nums}, k={k}")


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass

    cross_check_refs()
    course = {
        "key": "new-dsa",
        "title": "NEW DSA",
        "subtitle": "Every topic in sixteen sections, from the idea to mastery, in TypeScript.",
        "sections": [{"key": k, "title": t, "phase": p} for (k, t, p) in SECTIONS],
        "topics": [normalise(sliding_window())],
    }
    errors = validate(course)
    if errors:
        for e in errors:
            print("ERROR " + e, file=sys.stderr)
        return 1

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(course, f, ensure_ascii=False, indent=2)
        f.write("\n")
    n_ex = sum(1 for t in course["topics"] for _ in topic_exercises(t))
    print(f"wrote {os.path.relpath(OUT)}: {len(course['topics'])} topic(s), {n_ex} judged exercises")
    return 0


if __name__ == "__main__":
    sys.exit(main())
