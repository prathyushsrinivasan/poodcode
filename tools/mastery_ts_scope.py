# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Scope lint for the TypeScript Mastery track (TS_MASTERY_ROADMAP.md X-104):
# nothing a learner has to read or write in week N may use a construct that a
# later week teaches.
#
# Walks every judged program a week owns — its chapters' Learn exercises,
# practice, problem set, finals (and their type halves and alternates), the
# weekly project and the arc project — with line comments stripped, since a
# comment may mention what is coming. Order and spot exercises are left out:
# their code is the chapter's own worked example or pitfall, which the chapter
# chose to show in context.
#
# The Mastery track is for people who already program, so unlike the TS course
# (typescript_course.py) it does not gate loops, arrows or array methods: week
# 1 reads its input with `.split(…).map(Number)`. The rules below gate the
# constructs the programme actually sequences.
#
# exec()'d by gen_seed.py after mastery_ts_attach.py.
# ---------------------------------------------------------------------------

import re as _sc_re

# (token, first week it may appear in)
TS_SCOPE_RULES = [
    ("Object.groupBy(", 7), (".toSorted(", 7), (".toReversed(", 7), (".toSpliced(", 7),  # modern arrays
    ("interface ", 8), ("try {", 8), ("JSON.parse(", 8), ("JSON.stringify(", 8),       # objects & JSON
    ("as const", 10), ("enum ", 10),                                                 # literal types
    ("??=", 11), ("throw ", 11), (" asserts ", 11),                                  # nullish, assertion fns
    ("never", 12),                                                                   # exhaustiveness
    ("export ", 14), ("import type", 14), ("declare module", 14), ("declare global", 14),  # modules
    ("satisfies ", 15),
    ("Readonly<", 16), ("ReadonlyArray<", 16), ("Object.freeze(", 16),               # immutability
    ("Partial<", 17), ("Pick<", 17), ("Omit<", 17), ("Required<", 17), ("Record<string, never>", 17),
    ("Exclude<", 17), ("Extract<", 17), ("NonNullable<", 17), ("ReturnType<", 17), ("Parameters<", 17),
    ("Awaited<", 17),                                                                # utility types
    ("in keyof", 20), ("-readonly", 20), ("]-?:", 20), ("Capitalize<", 20),          # mapped types
    ("infer ", 21),                                                                  # conditional types
    ("Uppercase<", 22), ("Lowercase<", 22), ("Uncapitalize<", 22),                   # template literals
    ("super(", 23), ("abstract ", 23), ("protected ", 23),                           # class design
    ("function*", 24), ("yield ", 24), ("Symbol.iterator", 24),                      # iterators
    ("using ", 25), ("Symbol.dispose", 25), ("Symbol.asyncDispose", 25), (", { cause", 25),  # resources, causes
    ("await ", 26), ("new Promise", 26), ("setTimeout", 26), ("Promise.all", 26), ("AbortController", 26),
    #
    # DELIBERATELY NOT GATED — the weeks already use them before the chapter
    # that teaches them in depth, and a rule would be a false claim:
    #
    #   `new Map` / `new Set`  week 4 — counting and de-duplicating, before week 9
    #   `?.`                   week 4 — reading an optional regex group, before week 11
    #   `class ` / `this.`     week 11 — `instanceof` narrowing needs a class to test
    #   `keyof `               week 10 — a union of an object's keys, before week 19
    #   `<T>` generics         week 8 — small generic helpers, before week 18
    #   `async `               week 17 — `Awaited<ReturnType<typeof f>>` needs an async `f`
]

# Programs that knowingly preview a later week, with the reason. Keep short.
TS_SCOPE_EXEMPT = {
    "tsm-w6-json-walk": "recursion over a nested array read from stdin; JSON.parse is the one-line reader, JSON itself is week 8",
    "ts_recursion-flatten": "the same: the nested input arrives as JSON",
    "ts_runtime_validation-num": "deriving a type from a schema is the point of the chapter, a preview of weeks 20-21, and the chapter says so",
    "ts_runtime_validation-product": "the same schema-to-type preview",
}


def _sc_strip(src):
    return "\n".join(_sc_re.sub(r"//.*$", "", ln) for ln in src.split("\n"))


def _sc_programs(w):
    out = []
    for ex in w.get("practice", []) + w.get("problem_set", []):
        if ex["kind"] in ("order", "spot"):
            continue
        out.append((ex["id"], ex["solution"]))
        out.append((ex["id"] + ":starter", ex["starter"]))
    for key in w["concepts"]:
        for ex in EXERCISES.get(key, []):
            out.append((ex["id"], ex["solution"]))
    exam = w.get("exam")
    if exam:
        out.append((f"final-w{w['week']}", exam["solution"]))
        if exam.get("types"):
            out.append((exam["types"]["id"], exam["types"]["solution"]))
    for k, alt in enumerate(w.get("exam_alternates") or [], 1):
        out.append((f"final-w{w['week']}-alt{k}", alt["solution"]))
    for name in ("project_spec", "arc_project"):
        if w.get(name):
            out.append((f"{name}-w{w['week']}", w[name]["solution"]))
    return out


def _lint_ts_scope(weeks):
    problems = []
    for w in weeks:
        n = w["week"]
        for pid, src in _sc_programs(w):
            if pid.split(":")[0] in TS_SCOPE_EXEMPT:
                continue
            body = _sc_strip(src)
            for token, allowed_from in TS_SCOPE_RULES:
                if n < allowed_from and token in body:
                    problems.append(f"week {n} {pid} uses {token!r} (taught in week {allowed_from})")
    if problems:
        raise AssertionError("TS Mastery scope violations (X-104):\n  " + "\n  ".join(problems))


_lint_ts_scope(TS_WEEKS)
