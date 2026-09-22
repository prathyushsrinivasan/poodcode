import type { CalcDrill } from "../types";

/**
 * The arithmetic behind a unit's interactive lab (`UnitLab.tsx`) and its
 * "work it out by hand" cards.
 *
 * Everything here is pure, and everything that models Java arithmetic does it
 * with `BigInt` and explicit wrapping, because JavaScript numbers are neither
 * Java's `int` nor its `long`: `1 << 32` is 1 in both Java and JS, but
 * `2 ** 53 + 1` is not representable in a JS number at all, and the modular
 * lab's whole point is products near 10¹⁸.
 */

// ------------------------------------------------------------------ Java ints

const TWO32 = 1n << 32n;

/** Wrap to a Java `int` (32-bit two's complement). */
export function toInt32(x: bigint): bigint {
  const m = ((x % TWO32) + TWO32) % TWO32;
  return m >= 1n << 31n ? m - TWO32 : m;
}

/** Parse a user-typed integer, or null. Accepts a leading minus, `_` separators
 * (as Java allows), and hex/binary prefixes. */
export function parseBig(text: string): bigint | null {
  const t = text.trim().replace(/_/g, "");
  if (!/^-?(\d+|0x[0-9a-f]+|0b[01]+)$/i.test(t)) return null;
  const neg = t.startsWith("-");
  const body = neg ? t.slice(1) : t;
  try {
    const v = BigInt(body);
    return neg ? -v : v;
  } catch {
    return null;
  }
}

/** The 32 bits of a Java int, most significant first. */
export function bits32(x: bigint): string {
  const u = ((toInt32(x) % TWO32) + TWO32) % TWO32;
  return u.toString(2).padStart(32, "0");
}

/** Java's `int` shift: the count is taken mod 32. */
function shiftCount(k: bigint): bigint {
  return ((k % 32n) + 32n) % 32n;
}

export interface BitRow {
  /** The Java expression, e.g. `a & b`. */
  expr: string;
  value: bigint;
  /** A one-line note on what the result means. */
  note: string;
}

/** Every operator the bit lab shows, evaluated with Java `int` semantics. */
export function bitRows(aIn: bigint, bIn: bigint, kIn: bigint): BitRow[] {
  const a = toInt32(aIn);
  const b = toInt32(bIn);
  const k = shiftCount(kIn);
  const ua = ((a % TWO32) + TWO32) % TWO32;
  const popcount = (x: bigint) => bits32(x).split("").filter((c) => c === "1").length;
  const tz = (x: bigint) => {
    const s = bits32(x);
    const i = s.lastIndexOf("1");
    return i < 0 ? 32 : 31 - i;
  };
  const rows: BitRow[] = [
    { expr: "a & b", value: toInt32(a & b), note: "1 where both are 1" },
    { expr: "a | b", value: toInt32(a | b), note: "1 where either is 1" },
    { expr: "a ^ b", value: toInt32(a ^ b), note: "1 where they differ" },
    { expr: "~a", value: toInt32(~a), note: "every bit flipped: −a − 1" },
    {
      expr: `a << ${kIn}`,
      value: toInt32(a << k),
      note: k === kIn ? `a × 2^${k}, wrapped to 32 bits` : `count taken mod 32: really a << ${k}`,
    },
    { expr: `a >> ${kIn}`, value: toInt32(a >> k), note: "arithmetic: the sign bit is copied in" },
    { expr: `a >>> ${kIn}`, value: toInt32(ua >> k), note: "logical: zeros come in at the top" },
    { expr: "a & -a", value: toInt32(a & toInt32(-a)), note: "the lowest set bit alone" },
    { expr: "a & (a - 1)", value: toInt32(a & toInt32(a - 1n)), note: "a with its lowest set bit cleared" },
    {
      expr: "Integer.bitCount(a)",
      value: BigInt(popcount(a)),
      note: "the number of 1s",
    },
    {
      expr: "Integer.numberOfTrailingZeros(a)",
      value: BigInt(tz(a)),
      note: "the index of the lowest 1 (32 for zero)",
    },
  ];
  if (a > 0n) {
    // Gosper's hack: the next larger value with the same popcount.
    const c = a & -a;
    const r = a + c;
    const next = (((r ^ a) >> 2n) / c) | r;
    rows.push({ expr: "Gosper's next(a)", value: next, note: "next larger number with as many 1s" });
  }
  return rows;
}

// --------------------------------------------------------------- number theory

export function gcdBig(a: bigint, b: bigint): bigint {
  a = a < 0n ? -a : a;
  b = b < 0n ? -b : b;
  while (b !== 0n) [a, b] = [b, a % b];
  return a;
}

export interface EuclidStep {
  q: bigint | null;
  r0: bigint;
  s0: bigint;
  r1: bigint;
  s1: bigint;
}

/** The extended-Euclid table for (a, m): each row keeps r ≡ a·s (mod m). */
export function extendedEuclid(a: bigint, m: bigint): {
  steps: EuclidStep[];
  gcd: bigint;
  inverse: bigint | null;
} {
  let r0 = a, r1 = m, s0 = 1n, s1 = 0n;
  const steps: EuclidStep[] = [{ q: null, r0, s0, r1, s1 }];
  while (r1 !== 0n && steps.length < 200) {
    const q = r0 / r1;
    [r0, r1] = [r1, r0 - q * r1];
    [s0, s1] = [s1, s0 - q * s1];
    steps.push({ q, r0, s0, r1, s1 });
  }
  const g = r0 < 0n ? -r0 : r0;
  const inverse = g === 1n && m > 1n ? (((s0 * (r0 < 0n ? -1n : 1n)) % m) + m) % m : null;
  return { steps, gcd: g, inverse };
}

export interface PowerStep {
  e: bigint;
  bit: bigint;
  base: bigint;
  result: bigint;
}

/** Square-and-multiply for b^e mod m, one row per exponent bit. */
export function powerSteps(b: bigint, e: bigint, m: bigint): { steps: PowerStep[]; value: bigint } {
  if (m === 1n) return { steps: [], value: 0n };
  let base = ((b % m) + m) % m;
  let r = 1n;
  const steps: PowerStep[] = [];
  let x = e < 0n ? 0n : e;
  while (x > 0n && steps.length < 128) {
    const bit = x & 1n;
    if (bit === 1n) r = (r * base) % m;
    steps.push({ e: x, bit, base, result: r });
    base = (base * base) % m;
    x >>= 1n;
  }
  return { steps, value: r % m };
}

/** Prime factorisation by trial division; gives up (returns null) past 10¹⁴ so
 * a typo cannot freeze the page. */
export function factorize(n: bigint): [bigint, number][] | null {
  if (n < 2n || n > 10n ** 14n) return n < 2n ? [] : null;
  const out: [bigint, number][] = [];
  let x = n;
  for (let d = 2n; d * d <= x; d++) {
    if (x % d !== 0n) continue;
    let e = 0;
    while (x % d === 0n) {
      x /= d;
      e++;
    }
    out.push([d, e]);
  }
  if (x > 1n) out.push([x, 1]);
  return out;
}

export function phiFrom(n: bigint, factors: [bigint, number][]): bigint {
  let r = n;
  for (const [p] of factors) r -= r / p;
  return r;
}

/** What `a * b` does in a Java `long`: wraps modulo 2⁶⁴. */
export function javaLongMul(a: bigint, b: bigint): bigint {
  const m = 1n << 64n;
  const u = (((a * b) % m) + m) % m;
  return u >= 1n << 63n ? u - m : u;
}

// ------------------------------------------------------------------------ grid

export type Cell = [number, number];

export function neighbours(rows: number, cols: number, i: number, j: number, eight: boolean): Cell[] {
  const out: Cell[] = [];
  for (let di = -1; di <= 1; di++)
    for (let dj = -1; dj <= 1; dj++) {
      if (di === 0 && dj === 0) continue;
      if (!eight && di !== 0 && dj !== 0) continue;
      const ni = i + di, nj = j + dj;
      if (ni >= 0 && ni < rows && nj >= 0 && nj < cols) out.push([ni, nj]);
    }
  return out;
}

/** Where cell (i, j) of an r × c grid goes under each transformation. */
export function cellImages(r: number, c: number, i: number, j: number): { name: string; to: Cell; shape: string }[] {
  return [
    { name: "Transpose", to: [j, i], shape: `${c} × ${r}` },
    { name: "Rotate 90° clockwise", to: [j, r - 1 - i], shape: `${c} × ${r}` },
    { name: "Rotate 90° counter-clockwise", to: [c - 1 - j, i], shape: `${c} × ${r}` },
    { name: "Rotate 180°", to: [r - 1 - i, c - 1 - j], shape: `${r} × ${c}` },
    { name: "Flip left–right", to: [i, c - 1 - j], shape: `${r} × ${c}` },
    { name: "Flip top–bottom", to: [r - 1 - i, j], shape: `${r} × ${c}` },
  ];
}

/** The ring (layer) a cell belongs to: its distance to the nearest border. */
export function ringOf(r: number, c: number, i: number, j: number): number {
  return Math.min(i, j, r - 1 - i, c - 1 - j);
}

/** Every cell in spiral order (the four-boundary walk, with both guards). */
export function spiralOrder(r: number, c: number): Cell[] {
  const out: Cell[] = [];
  let top = 0, bot = r - 1, left = 0, right = c - 1;
  while (top <= bot && left <= right) {
    for (let j = left; j <= right; j++) out.push([top, j]);
    top++;
    for (let i = top; i <= bot; i++) out.push([i, right]);
    right--;
    if (top <= bot) {
      for (let j = right; j >= left; j--) out.push([bot, j]);
      bot--;
    }
    if (left <= right) {
      for (let i = bot; i >= top; i--) out.push([i, left]);
      left++;
    }
  }
  return out;
}

// ---------------------------------------------------------------- calc drills

/** Stable card id for one "work it out by hand" drill. Its own namespace, so
 * adding drills never reschedules a quiz or a Big-O card. */
export function calcCardId(unitKey: string, index: number): string {
  return `dsa-calc:${unitKey}:${index}`;
}

/** Compare typed answers loosely on form and strictly on content: case,
 * whitespace, a Unicode minus and surrounding brackets do not matter; digits,
 * signs and order do. */
export function normalizeAnswer(s: string): string {
  return s
    .toLowerCase()
    .replace(/[−–—]/g, "-")
    .replace(/[()[\]{}`]/g, "")
    .replace(/,/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function calcIsCorrect(drill: Pick<CalcDrill, "answer" | "accept">, typed: string): boolean {
  const t = normalizeAnswer(typed);
  if (!t) return false;
  return [drill.answer, ...drill.accept].some((a) => normalizeAnswer(a) === t);
}
