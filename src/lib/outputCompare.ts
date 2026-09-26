// Where does my output first go wrong? (TS_MASTERY_ROADMAP M1-02)
//
// A failing test used to show "expected" and "got" as two blobs; on a
// twenty-line output the one wrong character is hard to find, and a trailing
// space or a missing last line is invisible. This finds the first difference
// the judge would care about — after the SAME normalisation the judge applies
// (judge.rs `normalize`: CR dropped, trailing whitespace per line and trailing
// blank lines ignored) — and says in words what it is.

export function normalizeOutput(s: string): string {
  const lines = s.replace(/\r/g, "").split("\n").map((l) => l.replace(/\s+$/, ""));
  while (lines.length > 0 && lines[lines.length - 1] === "") lines.pop();
  return lines.join("\n");
}

export type Difference =
  | { kind: "same" }
  /** Your output stops before line `line` of the expected output. */
  | { kind: "missing"; line: number; expected: string }
  /** Your output has a line `line` the expected output does not. */
  | { kind: "extra"; line: number; actual: string }
  /** Line `line` differs, first at 1-based `column`. */
  | { kind: "char"; line: number; column: number; expected: string; actual: string };

export function firstDifference(expected: string, actual: string): Difference {
  const e = normalizeOutput(expected).split("\n");
  const a = normalizeOutput(actual).split("\n");
  const emptyE = normalizeOutput(expected) === "";
  const emptyA = normalizeOutput(actual) === "";
  if (emptyE && emptyA) return { kind: "same" };
  if (emptyA) return { kind: "missing", line: 1, expected: e[0] ?? "" };
  if (emptyE) return { kind: "extra", line: 1, actual: a[0] ?? "" };
  for (let i = 0; i < Math.max(e.length, a.length); i++) {
    const el = e[i];
    const al = a[i];
    if (el === undefined) return { kind: "extra", line: i + 1, actual: al ?? "" };
    if (al === undefined) return { kind: "missing", line: i + 1, expected: el };
    if (el === al) continue;
    let c = 0;
    while (c < el.length && c < al.length && el[c] === al[c]) c++;
    return { kind: "char", line: i + 1, column: c + 1, expected: el, actual: al };
  }
  return { kind: "same" };
}

/** Spaces and tabs made visible, for lines where spacing is the difference. */
export function visibleWhitespace(line: string): string {
  return line.replace(/ /g, "·").replace(/\t/g, "→");
}

const show = (s: string) => (s === "" ? "nothing" : `\`${s}\``);

/** One sentence saying what the first difference is. */
export function describeDifference(d: Difference): string {
  switch (d.kind) {
    case "same":
      return "The outputs match once trailing spaces and blank lines are ignored.";
    case "missing":
      return `Your output stops after ${d.line - 1} line${d.line - 1 === 1 ? "" : "s"}; line ${d.line} should be ${show(d.expected)}.`;
    case "extra":
      return `Your output has an extra line ${d.line}: ${show(d.actual)}.`;
    case "char": {
      const { expected: e, actual: a, column: c } = d;
      if (e.toLowerCase() === a.toLowerCase()) return `Line ${d.line} differs only in upper/lower case.`;
      if (e.replace(/\s+/g, " ") === a.replace(/\s+/g, " ") || e.replace(/\s/g, "") === a.replace(/\s/g, "")) {
        return `Line ${d.line} differs only in spacing, starting at column ${c}.`;
      }
      if (c > a.length) return `Line ${d.line} ends early — after ${show(a)} it should go on with ${show(e.slice(c - 1))}.`;
      if (c > e.length) return `Line ${d.line} runs on — after ${show(e)} you print ${show(a.slice(c - 1))} too.`;
      return `Line ${d.line} differs at column ${c}: expected ${show(e.slice(c - 1, c + 11))}, you printed ${show(a.slice(c - 1, c + 11))}.`;
    }
  }
}
