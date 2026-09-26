// The assertion panel for type-graded work (TS_MASTERY_ROADMAP M5-03).
//
// A type exercise's hidden `harness` is a list of claims — `type _1 =
// Expect<Equal<Mine, Expected>>;` and `// @ts-expect-error` lines — and the
// judge reports a failure as compiler messages located in `checks.ts(L,C)`
// (tscheck.rs relabels harness lines that way). This matches the two up, so
// the learner sees which claims hold and which fail, instead of a wall of
// TS2344 messages.

export type Assertion = {
  /** 1-based harness lines this claim spans. */
  from: number;
  to: number;
  kind: "equal" | "expect" | "rejects";
  /** The claim as written (joined onto one line). */
  text: string;
  /** For `Expect<Equal<left, right>>`: the two types compared. */
  left?: string;
  right?: string;
  /** For `@ts-expect-error — why`: the why. */
  note?: string;
};

/** Split `a, b` at the first comma not nested in brackets or quotes. */
export function splitTopLevel(s: string): [string, string] | null {
  let depth = 0;
  let quote: string | null = null;
  for (let i = 0; i < s.length; i++) {
    const c = s[i]!;
    if (quote) {
      if (c === "\\") i++;
      else if (c === quote) quote = null;
      continue;
    }
    if (c === '"' || c === "'" || c === "`") quote = c;
    else if ("<([{".includes(c)) depth++;
    else if (">)]}".includes(c)) {
      // `=>` is an arrow, not a closing angle bracket.
      if (!(c === ">" && s[i - 1] === "=")) depth--;
    } else if (c === "," && depth === 0) return [s.slice(0, i).trim(), s.slice(i + 1).trim()];
  }
  return null;
}

function bracketDelta(line: string): number {
  let d = 0;
  for (let i = 0; i < line.length; i++) {
    const c = line[i]!;
    if ("<([{".includes(c)) d++;
    else if (">)]}".includes(c) && !(c === ">" && line[i - 1] === "=")) d--;
  }
  return d;
}

export function parseAssertions(harness: string): Assertion[] {
  const lines = harness.split("\n");
  const out: Assertion[] = [];
  for (let i = 0; i < lines.length; i++) {
    const t = lines[i]!.trim();
    const directive = /^\/\/\s*@ts-expect-error\b(.*)$/.exec(t);
    if (directive) {
      let j = i + 1;
      while (j < lines.length && lines[j]!.trim() === "") j++;
      const note = (directive[1] ?? "").replace(/^\s*[—–:-]\s*/, "").trim();
      out.push({
        from: i + 1,
        to: i + 1,
        kind: "rejects",
        text: (lines[j] ?? "").trim(),
        note: note || undefined,
      });
      continue;
    }
    if (!/^type\s+\w+\s*=\s*Expect</.test(t)) continue;
    // Gather the whole statement: brackets balanced and a closing `;`.
    let j = i;
    let text = t;
    let depth = bracketDelta(t);
    while ((depth > 0 || !text.endsWith(";")) && j + 1 < lines.length) {
      j++;
      text += " " + lines[j]!.trim();
      depth += bracketDelta(lines[j]!);
    }
    const eq = /Expect<\s*Equal<([\s\S]*)>\s*>\s*;\s*$/.exec(text);
    const pair = eq ? splitTopLevel(eq[1]!) : null;
    out.push({
      from: i + 1,
      to: j + 1,
      kind: pair ? "equal" : "expect",
      text: text.replace(/\s+/g, " "),
      left: pair?.[0],
      right: pair?.[1],
    });
    i = j;
  }
  return out;
}

/** The harness lines (1-based) the compiler complained about. */
export function failingCheckLines(message: string): Set<number> {
  const lines = new Set<number>();
  for (const m of message.matchAll(/checks\.ts\((\d+),\d+\)/g)) lines.add(Number(m[1]));
  return lines;
}

/** Whether an assertion failed, given the failing harness lines. */
export function assertionFailed(a: Assertion, failing: Set<number>): boolean {
  for (let l = a.from; l <= a.to; l++) if (failing.has(l)) return true;
  return false;
}

/** True when the message has errors in the learner's own code, not the checks. */
export function hasOwnCodeErrors(message: string): boolean {
  return /main\.ts\(\d+,\d+\)/.test(message);
}
