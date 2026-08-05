// Structure-preserving test-input generation.
//
// The old generator emitted a hardcoded "N then N ints" blob that was invalid
// for most problems and carried no expected output. Instead we start from a
// *real* template input (an existing example/hidden case) and mutate only its
// "payload" integers, holding structural counts fixed so the shape stays valid.
// Expected outputs are then computed by running a known-correct oracle solution
// (see TestCaseManager) — making generated cases usable for Submit, not just Run.

export type GenMode = "perturb" | "min" | "max" | "large";

/** Small deterministic PRNG so generation is reproducible and testable. */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const INT_RE = /^[+-]?\d+$/;
const isIntTok = (s: string): boolean => INT_RE.test(s);

/** Split a line into [tok, sep, tok, sep, …], preserving exact whitespace. */
function splitLine(line: string): string[] {
  return line.split(/(\s+)/);
}

/** Number of whitespace-separated integer tokens on a line. */
function intTokenCount(line: string): number {
  return splitLine(line).filter((t, i) => i % 2 === 0 && isIntTok(t)).length;
}

/**
 * Mutate a template stdin, preserving line/whitespace structure and any integer
 * that looks structural (a count of the next line's tokens, or of the remaining
 * lines). Lines carrying such a count are frozen wholesale (covers "n", "n k",
 * and "rows cols" dimension lines) so the generated input stays well-formed.
 */
export function mutateInput(input: string, mode: GenMode, rand: () => number): string {
  const hadTrailingNewline = input.endsWith("\n");
  const body = input.replace(/\r/g, "").replace(/\n$/, "");
  const lines = body.length ? body.split("\n") : [];

  const remainingLinesAfter = (li: number) => lines.length - li - 1;
  const isSizeValue = (v: number, li: number) => {
    if (v < 0) return false;
    const nextCount = li + 1 < lines.length ? intTokenCount(lines[li + 1]) : -1;
    return v === nextCount || v === remainingLinesAfter(li);
  };
  const isDimensionLine = (li: number) =>
    splitLine(lines[li]).some((t, i) => i % 2 === 0 && isIntTok(t) && isSizeValue(parseInt(t, 10), li));

  const out = lines.map((line, li) => {
    const frozen = isDimensionLine(li);
    return splitLine(line)
      .map((tok, i) => {
        if (i % 2 === 1 || !isIntTok(tok)) return tok; // separators & non-ints
        if (frozen) return tok;
        return String(mutateValue(parseInt(tok, 10), mode, rand));
      })
      .join("");
  });

  let result = out.join("\n");
  if (hadTrailingNewline) result += "\n";
  return result;
}

function mutateValue(v: number, mode: GenMode, rand: () => number): number {
  const allowNeg = v < 0;
  const mag = Math.max(9, Math.abs(v));
  const signed = (r: number) => (allowNeg && rand() < 0.5 ? -r : r);
  switch (mode) {
    case "min":
      return allowNeg ? -mag : 0;
    case "max":
      return mag;
    case "large": {
      const big = Math.max(1000, mag * 100);
      return signed(Math.floor(rand() * (big + 1)));
    }
    case "perturb":
    default:
      return signed(Math.floor(rand() * (mag + 1)));
  }
}

/** Whether a template input has anything worth mutating (at least one payload int). */
export function hasMutablePayload(input: string): boolean {
  const before = input;
  // If perturbing with two different fixed RNGs can change the string, it's mutable.
  const a = mutateInput(before, "min", () => 0);
  const b = mutateInput(before, "max", () => 0);
  return a !== b || a !== before;
}
