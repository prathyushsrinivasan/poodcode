# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc — an independent reference implementation, in Python, of the language
# exactly as it stands at the end of each module.
#
# exec()'d by tools/calc_project.py before the module files. Defines
# `_calc(src, m)`: the stdout of module m's main program for stdin `src`.
#
# WHY IT EXISTS. "Expected output is computed, not typed" is the trust model of
# the whole app. For modules 1-4 the outputs are token lists, simple enough to
# build with `_toks`. From module 5 on they are trees, numbers, error messages
# with columns, and carets — and a hand-typed expectation that happens to agree
# with a buggy TypeScript solution proves nothing. So every expected output from
# module 6 on comes from here, and the verifier then checks the learner-facing
# TypeScript against it. Two implementations in two languages agreeing is the
# evidence; neither is trusted alone.
#
# Feature gates follow the syllabus: `m >= 8` is "parentheses exist", and so on.
# Keep it boring and literal — it is an oracle, not an exhibit.
# ---------------------------------------------------------------------------

import math as _cmath
import sys as _csys

_C_DIGITS = "0123456789"
_C_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"

# Module 12's judged programs start with these names already bound.
_C_SEED_ENV = (("day", 24), ("week", 7), ("dozen", 12))

# What V8 says when the parser recurses too deep (module 17's boundary test).
_C_STACK_MSG = "Maximum call stack size exceeded"


class _CalcErr(Exception):
    def __init__(self, msg, pos, scan=False):
        super().__init__(msg)
        self.msg, self.pos, self.scan = msg, pos, scan


def _jsnum(x):
    """Format a number the way a JavaScript template literal does."""
    if isinstance(x, bool):
        return "true" if x else "false"
    if x != x:
        return "NaN"
    if x in (float("inf"), float("-inf")):
        return "Infinity" if x > 0 else "-Infinity"
    if x == 0:
        return "0"                  # `${-0}` is "0" too
    # Python's repr and JavaScript's ToString both print the SHORTEST digits
    # that round-trip; they differ only in when they switch to an exponent.
    r = repr(float(x))
    sign = "-" if r.startswith("-") else ""
    r = r.lstrip("-")
    mant, _, exp = r.partition("e")
    exp = int(exp) if exp else 0
    whole, _, frac = mant.partition(".")
    frac = "" if frac == "0" else frac
    digits = (whole + frac).lstrip("0") or "0"
    # Decimal exponent of the first significant digit.
    point = len(whole) + exp if whole != "0" else exp - (len(frac) - len(frac.lstrip("0")))
    n = point                     # digits before the decimal point
    if 21 >= n > 0 and n >= len(digits):
        return sign + digits + "0" * (n - len(digits))
    if 21 >= n > 0:
        return sign + digits[:n] + "." + digits[n:]
    if 0 >= n > -6:
        return sign + "0." + "0" * (-n) + digits
    e = n - 1
    m = digits[0] + ("." + digits[1:] if len(digits) > 1 else "")
    return f"{sign}{m}e{'+' if e > 0 else '-'}{abs(e)}"


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def _c_scan(src, m):
    toks = []
    i, line, ls = 0, 1, 0
    n = len(src)
    while i < n:
        ch = src[i]
        pos = (line, i - ls + 1)
        if ch == " " or (m >= 16 and ch == "\r"):
            i += 1
        elif m >= 16 and ch == "\n":
            i += 1
            line, ls = line + 1, i
        elif ch in _C_DIGITS:
            start = i
            while i < n and src[i] in _C_DIGITS:
                i += 1
            toks.append({"kind": "number", "v": float(src[start:i]), "pos": pos})
        elif ch in "+-*/" or (m >= 14 and ch in "<>"):
            toks.append({"kind": "op", "v": ch, "pos": pos})
            i += 1
        elif m >= 14 and ch == "=" and src[i + 1:i + 2] == "=":
            toks.append({"kind": "op", "v": "==", "pos": pos})
            i += 2
        elif m >= 13 and ch == "=":
            toks.append({"kind": "equals", "v": None, "pos": pos})
            i += 1
        elif m >= 13 and ch == ";":
            toks.append({"kind": "semi", "v": None, "pos": pos})
            i += 1
        elif m >= 8 and ch == "(":
            toks.append({"kind": "lparen", "v": None, "pos": pos})
            i += 1
        elif m >= 8 and ch == ")":
            toks.append({"kind": "rparen", "v": None, "pos": pos})
            i += 1
        elif m >= 12 and ch in _C_LETTERS:
            start = i
            while i < n and (src[i] in _C_LETTERS or src[i] in _C_DIGITS):
                i += 1
            word = src[start:i]
            if m >= 13 and word == "let":
                toks.append({"kind": "let", "v": None, "pos": pos})
            elif m >= 14 and word in ("true", "false"):
                toks.append({"kind": "bool", "v": word == "true", "pos": pos})
            elif m >= 15 and word in ("if", "then", "else"):
                toks.append({"kind": word, "v": None, "pos": pos})
            else:
                toks.append({"kind": "ident", "v": word, "pos": pos})
        else:
            raise _CalcErr(f"unexpected '{ch}'", pos, scan=True)
    toks.append({"kind": "eof", "v": None, "pos": (line, i - ls + 1)})
    return toks


def _c_describe(t):
    k = t["kind"]
    if k == "number":
        return f"'{_jsnum(t['v'])}'"
    if k in ("op", "ident"):
        return f"'{t['v']}'"
    if k == "bool":
        return "'true'" if t["v"] else "'false'"
    fixed = {"lparen": "'('", "rparen": "')'", "let": "'let'", "equals": "'='",
             "semi": "';'", "if": "'if'", "then": "'then'", "else": "'else'",
             "eof": "end of input"}
    return fixed[k]


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class _CParser:
    def __init__(self, toks, m):
        self.toks, self.i, self.m = toks, 0, m

    def peek(self):
        return self.toks[self.i]

    def advance(self):
        t = self.toks[self.i]
        if t["kind"] != "eof":
            self.i += 1
        return t

    def unexpected(self, t):
        return _CalcErr(f"unexpected {_c_describe(t)}", t["pos"])

    def expected(self, what, t):
        return _CalcErr(f"expected {what} but found {_c_describe(t)}", t["pos"])

    # expr is the top of the grammar: comparison from 14, sum before it.
    def expr(self):
        return self.comparison() if self.m >= 14 else self.sum()

    def _level(self, ops, nxt):
        left = nxt()
        t = self.peek()
        while t["kind"] == "op" and t["v"] in ops:
            self.advance()
            right = nxt()
            left = ("bin", t["v"], left, right, t["pos"])
            t = self.peek()
        return left

    def comparison(self):
        return self._level(("<", ">", "=="), self.sum)

    def sum(self):
        return self._level(("+", "-"), self.product)

    def product(self):
        return self._level(("*", "/"), self.unary if self.m >= 8 else self.primary)

    def unary(self):
        t = self.peek()
        if t["kind"] == "op" and t["v"] == "-":
            self.advance()
            return ("neg", self.unary(), t["pos"])
        return self.primary()

    def primary(self):
        t = self.advance()
        k, m = t["kind"], self.m
        if k == "number":
            return ("num", t["v"], t["pos"])
        if m >= 14 and k == "bool":
            return ("bool", t["v"], t["pos"])
        if m >= 12 and k == "ident":
            return ("var", t["v"], t["pos"])
        if m >= 8 and k == "lparen":
            inner = self.expr()
            close = self.advance()
            if close["kind"] != "rparen":
                raise self.expected("')'", close)
            return inner
        if m >= 15 and k == "if":
            cond = self.expr()
            tt = self.advance()
            if tt["kind"] != "then":
                raise self.expected("'then'", tt)
            yes = self.expr()
            et = self.advance()
            if et["kind"] != "else":
                raise self.expected("'else'", et)
            no = self.expr()
            return ("if", cond, yes, no, t["pos"])
        raise self.unexpected(t)

    def statement(self):
        if self.peek()["kind"] != "let":
            return ("expr", self.expr())
        self.advance()
        name = self.advance()
        if name["kind"] != "ident":
            raise self.expected("a name", name)
        eq = self.advance()
        if eq["kind"] != "equals":
            raise self.expected("'='", eq)
        return ("let", name["v"], self.expr())

    def program(self):
        stmts = []
        while True:
            stmts.append(self.statement())
            t = self.advance()
            if t["kind"] == "eof":
                return stmts
            if t["kind"] != "semi":
                raise self.unexpected(t)
            if self.peek()["kind"] == "eof":
                return stmts


def _c_show(e):
    k = e[0]
    if k == "num":
        return _jsnum(e[1])
    if k == "neg":
        return f"(neg {_c_show(e[1])})"
    return f"({e[1]} {_c_show(e[2])} {_c_show(e[3])})"


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

def _c_isnum(v):
    return not isinstance(v, bool)


def _c_eval(e, env, m):
    k = e[0]
    if k == "num":
        if m >= 11 and not _cmath.isfinite(e[1]):
            raise _CalcErr("number too large", e[2])
        return e[1]
    if k == "bool":
        return e[1]
    if k == "var":
        if e[1] not in env:
            raise _CalcErr(f"undefined variable '{e[1]}'", e[2])
        return env[e[1]]
    if k == "neg":
        v = _c_eval(e[1], env, m)
        if m >= 14 and not _c_isnum(v):
            raise _CalcErr("cannot apply '-' to a boolean", e[2])
        return -v
    if k == "if":
        c = _c_eval(e[1], env, m)
        if _c_isnum(c):
            raise _CalcErr("if condition must be a boolean", e[4])
        return _c_eval(e[2] if c else e[3], env, m)
    _, op, l, r, pos = e
    a = _c_eval(l, env, m)
    b = _c_eval(r, env, m)
    if op == "==":
        if _c_isnum(a) != _c_isnum(b):
            ta = "number" if _c_isnum(a) else "boolean"
            tb = "number" if _c_isnum(b) else "boolean"
            raise _CalcErr(f"cannot compare a {ta} with a {tb}", pos)
        return a == b
    if m >= 14 and (not _c_isnum(a) or not _c_isnum(b)):
        raise _CalcErr(f"cannot apply '{op}' to a boolean", pos)
    if op == "<":
        return a < b
    if op == ">":
        return a > b
    if op == "/":
        if b == 0:
            if m >= 11:
                raise _CalcErr("division by zero", pos)
            return float("nan") if a == 0 else _cmath.copysign(float("inf"), a) * _cmath.copysign(1, b)
        v = a / b
    elif op == "+":
        v = a + b
    elif op == "-":
        v = a - b
    else:
        v = a * b
    if m >= 11 and not _cmath.isfinite(v):
        raise _CalcErr("number too large", pos)
    return v


# ---------------------------------------------------------------------------
# The main program of each module
# ---------------------------------------------------------------------------

def _c_line(src, n):
    return src.split("\n")[n - 1].rstrip()


def _c_report(src, err, m):
    line, col = err.pos
    if m >= 16 or err.scan:
        head = f"error: {err.msg} at {line}:{col}"
    else:
        head = f"error: {err.msg}"
    if m < 17:
        return head
    return f"{head}\n  {_c_line(src, line)}\n  {' ' * (col - 1)}^"


def _c_run(src, m, env):
    """(text, exit code) for one program."""
    try:
        toks = _c_scan(src, m)
        p = _CParser(toks, m)
        if m >= 13:
            prog = p.program()
            val = None
            for s in prog:
                if s[0] == "let":
                    v = _c_eval(s[2], env, m)
                    env[s[1]] = v
                    val = v
                else:
                    val = _c_eval(s[1], env, m)
            return _jsnum(val), 0
        e = p.expr() if m >= 7 else p.primary()
        end = p.peek()
        if end["kind"] != "eof":
            raise p.unexpected(end)
        if m <= 8:
            return _c_show(e), 0
        return _jsnum(_c_eval(e, env, m)), 0
    except _CalcErr as err:
        return _c_report(src, err, m), 1
    except RecursionError:
        assert m >= 17, "deep nesting is only tested from module 17"
        return f"error: internal error: {_C_STACK_MSG}", 2


def _calc(src, m):
    """The expected stdout of module m's judged main program for stdin `src`."""
    old = _csys.getrecursionlimit()
    _csys.setrecursionlimit(10000)
    try:
        if m >= 18:
            env = {}
            out = []
            for line in src.split("\n"):
                if line.strip() == "":
                    continue
                out.append(_c_run(line.rstrip(), m, env)[0])
            return "\n".join(out)
        src = src.rstrip()
        env = dict(_C_SEED_ENV) if m == 12 else {}
        text, code = _c_run(src, m, env)
        if m == 17:
            return f"{text}\nexit {code}"
        return text
    finally:
        _csys.setrecursionlimit(old)


def _ctests(m, inputs):
    """[(input, expected)] for a module's main program, every output computed."""
    return [(s, _calc(s, m)) for s in inputs]
