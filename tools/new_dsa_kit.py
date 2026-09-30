# -*- coding: utf-8 -*-
"""Building blocks for NEW_DSA topics (see NEW_DSA.md and tools/new_dsa.py).

Every judged exercise in a topic asks for ONE TypeScript function. The learner
never writes I/O: a hidden harness (appended by the judge, exactly as the
TypeScript course does) reads the case from stdin one argument per line, calls
the function and prints what it returned. Expected outputs are never typed by
hand — they come from a Python reference implementation passed to `exercise`,
and tools/verify_new_dsa.py then proves the TypeScript solution agrees.
"""

import textwrap

# ---------------------------------------------------------------------------
# Argument / return encoding — one argument per stdin line
# ---------------------------------------------------------------------------

PARSE = {
    "int": "Number({line}.trim())",
    "int[]": '({line}.trim() === "" ? [] : {line}.trim().split(/\\s+/).map(Number))',
    "string": "{line}",
}

PRINT = {
    "int": "console.log(String({call}));",
    "int[]": 'console.log({call}.join(" "));',
    "bool": 'console.log({call} ? "true" : "false");',
}


def encode_arg(ty, value):
    if ty == "int":
        return str(value)
    if ty == "int[]":
        return " ".join(str(v) for v in value)
    if ty == "string":
        return value
    raise ValueError(f"unknown argument type {ty}")


def encode_ret(ty, value):
    if ty == "int":
        return str(value)
    if ty == "int[]":
        return " ".join(str(v) for v in value)
    if ty == "bool":
        return "true" if value else "false"
    raise ValueError(f"unknown return type {ty}")


def harness(fn, params, ret):
    """The hidden driver: parse each argument line, call `fn`, print the result.

    Every name is prefixed `__nd` so it cannot collide with the learner's code,
    and `fs` is imported under a private alias for the same reason (mirrors the
    problem bank's own wrapper in src-tauri/src/harness.rs)."""
    out = [
        "",
        "// ---- checker: reads the arguments, calls your function, prints the result ----",
        'import * as __ndFs from "fs";',
        'const __ndIn: string[] = __ndFs.readFileSync(0, "utf8").split("\\n");',
        'const __ndLine = (i: number): string => (__ndIn[i] ?? "").replace(/\\r$/, "");',
    ]
    names = []
    for i, (_name, ty) in enumerate(params):
        line = f"__ndLine({i})"
        out.append(f"const __ndA{i} = {PARSE[ty].format(line=line)};")
        names.append(f"__ndA{i}")
    out.append(PRINT[ret].format(call=f"{fn}({', '.join(names)})"))
    return "\n".join(out) + "\n"


def tests_for(params, ret, cases, ref):
    tests = []
    for args in cases:
        if len(args) != len(params):
            raise ValueError(f"case {args!r} does not match parameters {params!r}")
        stdin = "\n".join(encode_arg(ty, v) for (_n, ty), v in zip(params, args)) + "\n"
        tests.append({"input": stdin, "output": encode_ret(ret, ref(*args)) + "\n"})
    return tests


def code(s):
    """Dedent an authored code block and end it with exactly one newline."""
    return textwrap.dedent(s).strip("\n") + "\n"


def md(s):
    return textwrap.dedent(s).strip("\n") + "\n"


def exercise(
    id,
    title,
    prompt,
    *,
    fn,
    params,
    ret,
    starter,
    solution,
    cases,
    ref,
    hints=(),
    kind="challenge",
    difficulty="",
    explanation="",
    extra_tests=(),
    harness_src=None,
):
    """A judged TypeScript exercise in the shape of `Exercise` (src/types.ts)."""
    return {
        "id": id,
        "title": title,
        "prompt": md(prompt),
        "hint": "",
        "hints": list(hints),
        "language": "typescript",
        "kind": kind,
        "difficulty": difficulty,
        "strictness": "",
        "harness": harness_src if harness_src is not None else harness(fn, params, ret),
        "judge_mode": "",
        "forbid": [],
        "starter": code(starter),
        "solution": code(solution),
        "tests": tests_for(params, ret, cases, ref) + list(extra_tests),
        "source_slug": "",
        "dataset": "",
        "explanation": md(explanation) if explanation else "",
    }


def quiz(question, options, answer, explanation, why_not=None, code_src="", kind=""):
    """A multiple-choice question in the shape of `QuizQuestion` (src/types.ts).

    `answer` is the index of the right option. `why_not` maps a wrong option's
    index to the reason it is wrong — every wrong option must have one, because
    a recognition drill that only says "no" teaches nothing about the near miss.
    """
    why_not = why_not or {}
    if not 0 <= answer < len(options):
        raise ValueError(f"answer {answer} out of range for {question!r}")
    missing = [i for i in range(len(options)) if i != answer and i not in why_not]
    if missing:
        raise ValueError(f"{question!r}: options {missing} have no why_not")
    q = {
        "question": question,
        "options": options,
        "answer": answer,
        "explanation": md(explanation),
        "why_not": [why_not.get(i, "") for i in range(len(options))],
    }
    if code_src:
        q["code"] = code(code_src)
    if kind:
        q["kind"] = kind
    return q


def multi(question, options, answers, explanation, why_not=None):
    """A select-every-right-answer question (`kind: "multi"`)."""
    q = quiz(question, options, answers[0], explanation,
             why_not={i: w for i, w in (why_not or {}).items()}
             | {i: "" for i in range(len(options)) if i not in (why_not or {})},
             kind="multi")
    q["answers"] = list(answers)
    return q
