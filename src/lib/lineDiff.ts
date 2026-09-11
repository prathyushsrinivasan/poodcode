// A line diff, for showing what one module of a project changed in the file the
// project is building.
//
// WHY A PROJECT NEEDS ONE. Every module of a Projects-track build carries a
// `reference`: the whole program as it stands at the end of that module. The
// track's pitch is that each module adds exactly one capability — and the only
// evidence of that on screen was a wall of 150 lines per module, most of which
// the previous module had already shown you. The diff between two consecutive
// references IS the module, stated in code: the lines it added, the lines it
// deleted (module 9 deletes the seed calls and a whole route), and nothing else.
//
// WHY NOT A LIBRARY. The inputs are a few hundred lines at most and there are
// two of them at a time, so the textbook LCS table is small (after trimming the
// common prefix and suffix, usually a few thousand cells) and needs no clever
// algorithm. A dependency would buy nothing but weight. This is also the one
// implementation in the app: lib/diff.ts, which the Solve page uses to compare
// attempts, is a thin wrapper over `diffLines`.
//
// COMMENT CHURN. The references are teaching material, so their comments change
// from module to module even where the code does not — module 9 rewrites the
// comment above `addTodo` to explain server-owned identity. That is real change
// and worth seeing, but it can drown the one route a module actually added, so
// `codeLines` offers a view that ignores comment-only and blank lines while
// keeping every surviving line's original line number.

/** One line of a program, and where it sits in the original text (1-based). */
export interface NumberedLine {
  no: number;
  text: string;
}

export type DiffOp = "same" | "add" | "del";

export interface DiffLine {
  op: DiffOp;
  text: string;
  /** Line number in the older text; null for an added line. */
  oldNo: number | null;
  /** Line number in the newer text; null for a deleted line. */
  newNo: number | null;
}

/** Every line of a text, numbered. A single trailing newline does not produce
 * an empty last line — references are normalized to end with exactly one. */
export function numberLines(src: string): NumberedLine[] {
  const lines = src.replace(/\r/g, "").split("\n");
  if (lines.length > 0 && lines[lines.length - 1] === "") lines.pop();
  return lines.map((text, i) => ({ no: i + 1, text }));
}

/** True for a line that carries no code: blank, or a `//` comment on its own.
 *
 * Only whole-line comments are recognised. Stripping a trailing `// …` would
 * need a tokenizer to avoid cutting `"http://localhost"` in half, and a line
 * with code on it has changed if its code changed regardless of its comment. */
export function isCommentOrBlank(text: string): boolean {
  const t = text.trim();
  return t === "" || t.startsWith("//");
}

/** The lines of a program that carry code, keeping their original numbers. */
export function codeLines(src: string): NumberedLine[] {
  return numberLines(src).filter((l) => !isCommentOrBlank(l.text));
}

/** How many lines of a program carry code — the "size" a growth chart plots. */
export const countCodeLines = (src: string): number => codeLines(src).length;

/** Lines compare equal regardless of trailing whitespace, exactly as the judge
 * compares output. Leading whitespace is kept: re-indenting a block is a change
 * worth showing, since it usually means the block moved inside something. */
const key = (l: NumberedLine) => l.text.trimEnd();

/**
 * The shortest edit turning `a` into `b`, as a sequence of kept, deleted and
 * added lines in reading order.
 *
 * Within a run of changes, deletions come before additions — the conventional
 * order, and the one that reads as "this became that".
 */
export function diffLines(a: readonly NumberedLine[], b: readonly NumberedLine[]): DiffLine[] {
  // Trim the common prefix and suffix first. Consecutive references share most
  // of their text, so this usually shrinks the table below to a sliver.
  let start = 0;
  while (start < a.length && start < b.length && key(a[start]!) === key(b[start]!)) start++;
  let endA = a.length;
  let endB = b.length;
  while (endA > start && endB > start && key(a[endA - 1]!) === key(b[endB - 1]!)) {
    endA--;
    endB--;
  }

  const same = (x: NumberedLine, y: NumberedLine): DiffLine => ({
    op: "same",
    text: y.text,
    oldNo: x.no,
    newNo: y.no,
  });

  const out: DiffLine[] = [];
  for (let i = 0; i < start; i++) out.push(same(a[i]!, b[i]!));

  // dp[i][j] = length of the longest common subsequence of a[i..endA) and
  // b[j..endB), over the trimmed middle only. Flattened into one array.
  const n = endA - start;
  const m = endB - start;
  const w = m + 1;
  const dp = new Uint32Array((n + 1) * w);
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i * w + j] =
        key(a[start + i]!) === key(b[start + j]!)
          ? dp[(i + 1) * w + j + 1]! + 1
          : Math.max(dp[(i + 1) * w + j]!, dp[i * w + j + 1]!);
    }
  }

  let i = 0;
  let j = 0;
  while (i < n || j < m) {
    const x = a[start + i];
    const y = b[start + j];
    if (i < n && j < m && x && y && key(x) === key(y)) {
      out.push(same(x, y));
      i++;
      j++;
    } else if (j >= m || (i < n && dp[(i + 1) * w + j]! >= dp[i * w + j + 1]!)) {
      out.push({ op: "del", text: x!.text, oldNo: x!.no, newNo: null });
      i++;
    } else {
      out.push({ op: "add", text: y!.text, oldNo: null, newNo: y!.no });
      j++;
    }
  }

  for (let k = 0; k < a.length - endA; k++) out.push(same(a[endA + k]!, b[endB + k]!));
  return out;
}

/** Diff two whole programs, optionally ignoring comment-only and blank lines. */
export function diffSources(before: string, after: string, opts: { codeOnly?: boolean } = {}) {
  const pick = opts.codeOnly ? codeLines : numberLines;
  return diffLines(pick(before), pick(after));
}

export interface DiffStats {
  added: number;
  removed: number;
}

export function diffStats(lines: readonly DiffLine[]): DiffStats {
  let added = 0;
  let removed = 0;
  for (const l of lines) {
    if (l.op === "add") added++;
    else if (l.op === "del") removed++;
  }
  return { added, removed };
}

/** A diff for display: the changed lines with some context around each, and
 * the long unchanged stretches between them folded into a count. */
export type DiffChunk =
  | { kind: "lines"; lines: DiffLine[] }
  | { kind: "gap"; lines: DiffLine[] };

/**
 * Fold every run of unchanged lines longer than `2 * context` into a gap,
 * keeping `context` lines of it on each side of a change. A leading or trailing
 * run keeps context only on the side that touches a change.
 *
 * Gaps carry their lines rather than just a count, so a viewer can unfold one
 * in place without recomputing anything.
 */
export function foldUnchanged(lines: readonly DiffLine[], context = 3): DiffChunk[] {
  const chunks: DiffChunk[] = [];
  let buf: DiffLine[] = [];
  const flush = () => {
    if (buf.length) chunks.push({ kind: "lines", lines: buf });
    buf = [];
  };

  let i = 0;
  while (i < lines.length) {
    if (lines[i]!.op !== "same") {
      buf.push(lines[i]!);
      i++;
      continue;
    }
    let j = i;
    while (j < lines.length && lines[j]!.op === "same") j++;
    const run = lines.slice(i, j);
    const atStart = i === 0;
    const atEnd = j === lines.length;
    const keepHead = atStart ? 0 : context;
    const keepTail = atEnd ? 0 : context;
    if (run.length > keepHead + keepTail) {
      buf.push(...run.slice(0, keepHead));
      flush();
      chunks.push({ kind: "gap", lines: run.slice(keepHead, run.length - keepTail) });
      buf.push(...run.slice(run.length - keepTail));
    } else {
      buf.push(...run);
    }
    i = j;
  }
  flush();
  return chunks;
}
