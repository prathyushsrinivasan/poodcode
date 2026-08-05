// Minimal line-level diff (LCS based) used to compare two code attempts.
// Pure and dependency-free so it can be unit-tested and rendered as add/del rows.

export type DiffType = "same" | "add" | "del";
export interface DiffOp {
  type: DiffType;
  text: string;
}

/** Diff two blocks of text line-by-line. `del` lines come from `a`, `add` from `b`. */
export function lineDiff(a: string, b: string): DiffOp[] {
  const A = a.replace(/\r/g, "").split("\n");
  const B = b.replace(/\r/g, "").split("\n");
  const n = A.length;
  const m = B.length;

  // dp[i][j] = length of the longest common subsequence of A[i:], B[j:].
  const dp: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] = A[i] === B[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }

  const ops: DiffOp[] = [];
  let i = 0;
  let j = 0;
  while (i < n && j < m) {
    if (A[i] === B[j]) {
      ops.push({ type: "same", text: A[i] });
      i++;
      j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      ops.push({ type: "del", text: A[i] });
      i++;
    } else {
      ops.push({ type: "add", text: B[j] });
      j++;
    }
  }
  while (i < n) ops.push({ type: "del", text: A[i++] });
  while (j < m) ops.push({ type: "add", text: B[j++] });
  return ops;
}

/** Count added / removed lines in a diff. */
export function diffStats(ops: DiffOp[]): { added: number; removed: number } {
  let added = 0;
  let removed = 0;
  for (const op of ops) {
    if (op.type === "add") added++;
    else if (op.type === "del") removed++;
  }
  return { added, removed };
}
