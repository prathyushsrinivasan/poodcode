# -*- coding: utf-8 -*-
"""Print the TypeScript Mastery track's content numbers from the built seeds
(TS_MASTERY_ROADMAP.md X-106), so the roadmap's "where it stands" figures are
regenerated rather than hand-counted.

    python tools/ts_mastery_stats.py          # a Markdown table
    python tools/ts_mastery_stats.py --weeks  # plus one row per week

Reads src-tauri/seeds/concepts.json and mastery.json — run gen_seed.py first.
"""

import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = os.path.join(HERE, "..", "src-tauri", "seeds")


def load(name):
    with open(os.path.join(SEEDS, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--weeks", action="store_true", help="also print one row per week")
    args = ap.parse_args()

    concepts = load("concepts.json")
    items = concepts if isinstance(concepts, list) else list(concepts.values())
    chapters = [c for c in items if isinstance(c, dict) and c.get("language") == "typescript"]
    track = next(t for t in load("mastery.json") if t.get("language") == "typescript")
    weeks = track["weeks"]
    core = [w for w in weeks if not w.get("optional")]

    lesson_lengths = [len(c.get("lesson", "")) for c in chapters]
    exercise_kinds = Counter(e.get("kind", "?") for c in chapters for e in c.get("exercises", []) or [])
    practice_kinds = Counter(e.get("kind", "?") for w in weeks for e in w.get("practice", []))
    problem_set = [e for w in weeks for e in (w.get("problem_set") or [])]
    typelevel = sum(1 for e in problem_set if e.get("kind") == "typelevel")
    projects = [w["project_spec"] for w in weeks if w.get("project_spec")]
    quiz = [len(w["quiz"]) for w in weeks]
    cards = [len(w["flashcards"]) for w in weeks]
    finals = [len(w["exam"]["tests"]) for w in weeks]

    rows = [
        ("Weeks", f"{len(core)} core + {len(weeks) - len(core)} optional"),
        ("TypeScript Learn chapters", f"{len(chapters)}"),
        ("Lesson length", f"{min(lesson_lengths):,}–{max(lesson_lengths):,} characters (median {sorted(lesson_lengths)[len(lesson_lengths) // 2]:,})"),
        ("Learn exercises", f"{sum(exercise_kinds.values())} ({', '.join(f'{n} {k}' for k, n in exercise_kinds.most_common())})"),
        ("Chapter quiz questions", f"{sum(len(c.get('quiz', []) or []) for c in chapters)}"),
        ("Week practice", f"{sum(practice_kinds.values())} ({', '.join(f'{n} {k}' for k, n in practice_kinds.most_common())})"),
        ("Problem-set problems", f"{len(problem_set)} ({typelevel} type-graded), in {sum(1 for w in weeks if w.get('problem_set'))} weeks"),
        ("Runnable projects", f"{len(projects)} ({sum(len(p['tests']) for p in projects)} acceptance tests)"),
        ("Week quiz banks", f"{sum(quiz)} questions (min {min(quiz)}, max {max(quiz)} per week)"),
        ("Review cards", f"{sum(cards)} (min {min(cards)} per week)"),
        ("Coding finals", f"{len(finals)} with {sum(finals)} tests (min {min(finals)})"),
        ("Checkpoint contests", f"{sum(1 for w in weeks if w.get('contest'))}"),
    ]
    print("| | now |")
    print("|---|---|")
    for label, value in rows:
        print(f"| {label} | {value} |")

    if args.weeks:
        print()
        print("| week | title | chapters | problems | practice | project tests | quiz | cards | final tests |")
        print("|---|---|---|---|---|---|---|---|---|")
        for w in weeks:
            spec = w.get("project_spec")
            print(f"| {w['week']} | {w['title']} | {len(w['concepts'])} | {len(w.get('problem_set') or [])} | "
                  f"{len(w.get('practice', []))} | {len(spec['tests']) if spec else 0} | {len(w['quiz'])} | "
                  f"{len(w['flashcards'])} | {len(w['exam']['tests'])} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
