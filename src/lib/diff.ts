// Minimal line-level diff used to compare two code attempts, and expected
// against actual output. Pure and dependency-free so it can be unit-tested and
// rendered as add/del rows.
//
// The algorithm lives in lineDiff.ts, which the Projects track's build history
// also uses; this is the small unnumbered API the Solve page and test results
// were written against. Lines compare equal regardless of trailing whitespace,
// and a final newline does not count as an extra empty line — the same two
// allowances the judge makes when it compares output.

import { diffLines, numberLines } from "./lineDiff";

export type DiffType = "same" | "add" | "del";
export interface DiffOp {
  type: DiffType;
  text: string;
}

/** Diff two blocks of text line-by-line. `del` lines come from `a`, `add` from `b`. */
export function lineDiff(a: string, b: string): DiffOp[] {
  return diffLines(numberLines(a), numberLines(b)).map((l) => ({ type: l.op, text: l.text }));
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
