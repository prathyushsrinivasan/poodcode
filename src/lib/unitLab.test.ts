import { describe, expect, it } from "vitest";
import {
  bitRows,
  bits32,
  calcCardId,
  calcIsCorrect,
  cellImages,
  extendedEuclid,
  factorize,
  javaLongMul,
  neighbours,
  normalizeAnswer,
  parseBig,
  phiFrom,
  powerSteps,
  ringOf,
  spiralOrder,
  toInt32,
} from "./unitLab";

const row = (a: bigint, b: bigint, k: bigint, expr: string) =>
  bitRows(a, b, k).find((r) => r.expr === expr)?.value;

describe("Java int semantics", () => {
  it("wraps to 32 bits", () => {
    expect(toInt32(2147483648n)).toBe(-2147483648n);
    expect(toInt32(-1n)).toBe(-1n);
    expect(toInt32(4294967297n)).toBe(1n);
  });

  it("shows two's complement", () => {
    expect(bits32(-1n)).toBe("1".repeat(32));
    expect(bits32(12n)).toBe("0".repeat(28) + "1100");
    expect(bits32(-8n).slice(-4)).toBe("1000");
  });

  it("evaluates the operators like Java", () => {
    expect(row(13n, 11n, 2n, "a & b")).toBe(9n);
    expect(row(13n, 11n, 2n, "a | b")).toBe(15n);
    expect(row(13n, 11n, 2n, "a ^ b")).toBe(6n);
    expect(row(13n, 11n, 2n, "~a")).toBe(-14n);
    expect(row(-8n, 0n, 1n, "a >> 1")).toBe(-4n);
    expect(row(-8n, 0n, 28n, "a >>> 28")).toBe(15n);
    expect(row(1n, 0n, 32n, "a << 32")).toBe(1n); // count mod 32
    expect(row(1n, 0n, 31n, "a << 31")).toBe(-2147483648n);
    expect(row(40n, 0n, 0n, "a & -a")).toBe(8n);
    expect(row(40n, 0n, 0n, "a & (a - 1)")).toBe(32n);
    expect(row(255n, 0n, 0n, "Integer.bitCount(a)")).toBe(8n);
    expect(row(0n, 0n, 0n, "Integer.numberOfTrailingZeros(a)")).toBe(32n);
    expect(row(92n, 0n, 0n, "Gosper's next(a)")).toBe(99n);
  });

  it("wraps long multiplication", () => {
    expect(javaLongMul(10n ** 18n, 10n ** 18n)).not.toBe(10n ** 36n);
    expect(javaLongMul(3n, 4n)).toBe(12n);
    expect(javaLongMul(1n << 62n, 2n)).toBe(-(1n << 63n));
  });

  it("parses what people type", () => {
    expect(parseBig(" -1_000 ")).toBe(-1000n);
    expect(parseBig("0xff")).toBe(255n);
    expect(parseBig("0b101")).toBe(5n);
    expect(parseBig("12a")).toBeNull();
    expect(parseBig("")).toBeNull();
  });
});

describe("number theory", () => {
  it("finds inverses with extended Euclid, and their absence", () => {
    expect(extendedEuclid(17n, 60n).inverse).toBe(53n);
    expect(extendedEuclid(7n, 26n).inverse).toBe(15n);
    const none = extendedEuclid(4n, 10n);
    expect(none.inverse).toBeNull();
    expect(none.gcd).toBe(2n);
    // every row keeps r ≡ 17·s (mod 60)
    for (const s of extendedEuclid(17n, 60n).steps) {
      expect((((s.r0 - 17n * s.s0) % 60n) + 60n) % 60n).toBe(0n);
    }
  });

  it("powers by squaring", () => {
    expect(powerSteps(3n, 13n, 1000n).value).toBe(323n);
    expect(powerSteps(2n, 10n, 1000n).value).toBe(24n);
    expect(powerSteps(10n ** 18n, 2n, 1_000_000_007n).value).toBe(2401n);
    expect(powerSteps(5n, 0n, 7n).value).toBe(1n);
    expect(powerSteps(5n, 3n, 1n).value).toBe(0n);
  });

  it("factorises and computes phi", () => {
    expect(factorize(360n)).toEqual([[2n, 3], [3n, 2], [5n, 1]]);
    expect(factorize(97n)).toEqual([[97n, 1]]);
    expect(factorize(1n)).toEqual([]);
    expect(factorize(10n ** 15n)).toBeNull();
    expect(phiFrom(36n, factorize(36n)!)).toBe(12n);
  });
});

describe("grid", () => {
  it("clips neighbours at the border", () => {
    expect(neighbours(4, 5, 0, 0, false)).toHaveLength(2);
    expect(neighbours(4, 5, 0, 0, true)).toHaveLength(3);
    expect(neighbours(5, 5, 2, 2, true)).toHaveLength(8);
    expect(neighbours(1, 1, 0, 0, true)).toHaveLength(0);
  });

  it("maps cells under each transformation", () => {
    const img = Object.fromEntries(cellImages(4, 4, 1, 3).map((x) => [x.name, x.to]));
    expect(img["Rotate 90° clockwise"]).toEqual([3, 2]);
    expect(img["Transpose"]).toEqual([3, 1]);
    // four clockwise rotations of a square return every cell home
    for (let i = 0; i < 4; i++)
      for (let j = 0; j < 4; j++) {
        let cell: [number, number] = [i, j];
        for (let t = 0; t < 4; t++) cell = [cell[1], 4 - 1 - cell[0]];
        expect(cell).toEqual([i, j]);
      }
  });

  it("walks the spiral once per cell, including single rows and columns", () => {
    for (const [r, c] of [[3, 4], [1, 5], [5, 1], [4, 4], [1, 1]]) {
      const s = spiralOrder(r, c);
      expect(s).toHaveLength(r * c);
      expect(new Set(s.map(([i, j]) => i * c + j)).size).toBe(r * c);
    }
    expect(spiralOrder(3, 3).map(([i, j]) => i * 3 + j + 1)).toEqual([1, 2, 3, 6, 9, 8, 7, 4, 5]);
  });

  it("finds a cell's ring", () => {
    expect(ringOf(6, 8, 2, 5)).toBe(2);
    expect(ringOf(6, 8, 0, 4)).toBe(0);
  });
});

describe("calc drills", () => {
  it("ids its cards in their own namespace", () => {
    expect(calcCardId("bit-manipulation", 3)).toBe("dsa-calc:bit-manipulation:3");
  });

  it("forgives form and not content", () => {
    const d = { answer: "3 2", accept: ["(3, 2)"] };
    expect(calcIsCorrect(d, "3 2")).toBe(true);
    expect(calcIsCorrect(d, " (3,2) ")).toBe(true);
    expect(calcIsCorrect(d, "2 3")).toBe(false);
    expect(calcIsCorrect(d, "")).toBe(false);
    expect(calcIsCorrect({ answer: "-1", accept: [] }, "−1")).toBe(true);
    expect(normalizeAnswer("  YES ")).toBe("yes");
  });
});
