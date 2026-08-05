import { describe, expect, it } from "vitest";
import {
  analyzeComplexity,
  compareComplexity,
  loopDepth,
  recursionInfo,
} from "./complexity";

describe("loopDepth", () => {
  it("counts nested loops by indentation", () => {
    const code = `for i in range(n):
    for j in range(n):
        total += a[i][j]`;
    expect(loopDepth(code)).toBe(2);
  });

  it("treats sibling loops as depth 1", () => {
    const code = `for (let i=0;i<n;i++) sum+=a[i];
for (let j=0;j<n;j++) prod*=a[j];`;
    expect(loopDepth(code)).toBe(1);
  });

  it("ignores loop keywords in strings", () => {
    expect(loopDepth('const s = "for while for";')).toBe(0);
  });

  it("counts brace-delimited nesting regardless of indentation (Java)", () => {
    const code = `for (int i=0;i<n;i++){
for (int j=0;j<n;j++){ sum += a[i][j]; }
}`;
    expect(loopDepth(code)).toBe(2);
  });

  it("does not count a brace-less single-statement loop as extra nesting", () => {
    const code = `for (int i=0;i<n;i++){
for (int j=0;j<n;j++) sum += a[j];
}`;
    expect(loopDepth(code)).toBe(2);
  });
});

describe("recursionInfo", () => {
  it("detects branching recursion", () => {
    const code = `function fib(n){ if(n<2) return n; return fib(n-1)+fib(n-2); }`;
    const r = recursionInfo(code);
    expect(r.recursive).toBe(true);
    expect(r.branches).toBeGreaterThanOrEqual(2);
  });
});

describe("analyzeComplexity", () => {
  it("linear single pass", () => {
    expect(analyzeComplexity("for x in a:\n    s += x").time).toBe("O(n)");
  });
  it("quadratic nested", () => {
    const code = "for i in range(n):\n    for j in range(n):\n        pass";
    expect(analyzeComplexity(code).time).toBe("O(n^2)");
  });
  it("sorting dominates", () => {
    expect(analyzeComplexity("a.sort()\nreturn a[0]").time).toBe("O(n log n)");
  });
  it("exponential recursion", () => {
    const code = `function f(n){return f(n-1)+f(n-2);}`;
    expect(analyzeComplexity(code).time).toBe("O(2^n)");
  });
  it("memoized branching recursion is polynomial, not exponential", () => {
    const code = `const memo = {};
function f(n){ if(n in memo) return memo[n]; if(n<2) return n; return memo[n]=f(n-1)+f(n-2); }`;
    expect(analyzeComplexity(code).time).toBe("O(n)");
  });
});

describe("compareComplexity", () => {
  it("ranks common complexities", () => {
    expect(compareComplexity("O(n^2)", "O(n log n)")).toBe("worse");
    expect(compareComplexity("O(n)", "O(n)")).toBe("equal");
    expect(compareComplexity("O(log n)", "O(n)")).toBe("better");
    expect(compareComplexity("O(n²)", "O(n^2)")).toBe("equal");
    expect(compareComplexity("O(R·C)", "O(n)")).toBe("unknown");
  });
});
