# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Key terms for every TypeScript chapter (TS_MASTERY_ROADMAP.md X-08).
#
# The TypeScript course already defines 623 terms, week by week. Each term is
# given to the first chapter — in the Mastery programme's order — whose lesson
# uses it, so a term is defined where the learner first meets it, and appended
# to that lesson as a "Key terms" section (which the chapter's cheat sheet also
# shows). The programme order is read from the week tables in
# mastery_ts_m1.py … m6.py, because the Mastery weeks are built after the
# concepts are written.
#
# exec()'d by gen_seed.py right after typescript_course.py (TS_COURSE).
# ---------------------------------------------------------------------------

import ast as _gl_ast
import re as _gl_re

_GL_PER_CHAPTER = 10
# Words whose first use in the programme is in another sense ("optional
# chaining" is not an array-method chain); defined where they are taught instead.
_GL_AMBIGUOUS = {"chain"}


def _gl_programme_order():
    order = []
    for n in range(1, 7):
        with open(os.path.join(HERE, f"mastery_ts_m{n}.py"), encoding="utf-8") as f:
            tree = _gl_ast.parse(f.read())
        weeks = []
        for node in _gl_ast.walk(tree):
            if (isinstance(node, _gl_ast.Call) and getattr(node.func, "id", "") == "_w" and len(node.args) >= 5
                    and isinstance(node.args[0], _gl_ast.Constant) and isinstance(node.args[4], _gl_ast.List)):
                keys = [e.value for e in node.args[4].elts if isinstance(e, _gl_ast.Constant)]
                weeks.append((node.args[0].value, keys))
        for _week, keys in sorted(weeks):
            order += [k for k in keys if k not in order]
    return order


def _gl_prose(md):
    """The lesson without its code blocks — a term in a program is not a
    term being taught."""
    return _gl_re.sub(r"```.*?```", " ", md, flags=_gl_re.S)


_gl_order = [k for k in _gl_programme_order() if k in LESSONS]
_gl_missing = sorted(k for k, c in CONCEPTS.items() if c.get("language") == "typescript" and k not in _gl_order)
assert not _gl_missing, f"X-08: TypeScript chapters not found in the Mastery week tables: {_gl_missing}"

_gl_terms = []
_gl_seen = set()
for _gl_week in TS_COURSE.get("weeks", []):
    for _gl_t in _gl_week.get("glossary") or []:
        _gl_name = _gl_t["term"].strip()
        if _gl_name.lower() not in _gl_seen and len(_gl_name) > 1 and _gl_name.lower() not in _GL_AMBIGUOUS:
            _gl_seen.add(_gl_name.lower())
            _gl_terms.append((_gl_name, _gl_t["def"].strip()))

TS_CHAPTER_TERMS = {k: [] for k in _gl_order}
_gl_texts = {k: _gl_prose(LESSONS[k]).lower() for k in _gl_order}
for _gl_name, _gl_def in _gl_terms:
    _gl_pat = _gl_re.compile(r"(?<![\w$])" + _gl_re.escape(_gl_name.lower()) + r"(?![\w$])")
    for _gl_key in _gl_order:
        if _gl_pat.search(_gl_texts[_gl_key]):
            if len(TS_CHAPTER_TERMS[_gl_key]) < _GL_PER_CHAPTER:
                TS_CHAPTER_TERMS[_gl_key].append((_gl_name, _gl_def))
            break

for _gl_key, _gl_list in TS_CHAPTER_TERMS.items():
    if _gl_list:
        LESSONS[_gl_key] = (LESSONS[_gl_key].rstrip() + "\n\n### Key terms\n"
                            + "\n".join(f"- **{t}** — {d}" for t, d in _gl_list))
print(f"  key terms: {sum(len(v) for v in TS_CHAPTER_TERMS.values())} across "
      f"{sum(1 for v in TS_CHAPTER_TERMS.values() if v)} TypeScript chapters")
