// Heuristic complexity analyzer. This is an ESTIMATE derived from code shape
// (loop nesting, recursion, sorting, allocations) — not a proof. It is meant to
// prompt reflection and compare against a problem's known-optimal complexity.

export interface ComplexityEstimate {
  time: string;
  space: string;
  signals: string[];
}

const LOOP_RE = /(^|[^.\w])(for|while)\b|\.(forEach|map|reduce|filter)\s*\(/;
const SORT_RE = /\.sort\s*\(|\bsorted\s*\(|Collections\.sort|Arrays\.sort|std::sort/;
const BINSEARCH_RE = /\b(mid|lo|hi|left|right)\b/;
/// Signals that a branching recursion is memoized, so it is polynomial, not
/// exponential: an explicit memo/dp/cache table, a visited set, or Python's
/// functools caching decorators.
const MEMO_RE =
  /\b(memo|dp|cache|visited|seen)\b|\bdp\s*\[|@lru_cache|@cache|functools\.(?:lru_)?cache|\.containsKey\s*\(|\bunordered_map\b/i;

function stripStrings(code: string): string {
  // Remove string/char literals and line comments so keywords inside them
  // don't skew the estimate.
  return code
    .replace(/"(?:[^"\\]|\\.)*"/g, '""')
    .replace(/'(?:[^'\\]|\\.)*'/g, "''")
    .replace(/`(?:[^`\\]|\\.)*`/g, "``")
    .replace(/\/\/[^\n]*/g, "")
    .replace(/#[^\n]*/g, "");
}

/**
 * Estimate the maximum nesting depth of loops. Brace-delimited code (Java, C++,
 * JS, Go, Rust…) is measured by tracking `{}` nesting so it is robust to
 * formatting; brace-free code (Python) falls back to indentation.
 */
export function loopDepth(code: string): number {
  const clean = stripStrings(code);
  const braces = (clean.match(/[{}]/g) || []).length;
  return braces >= 2 ? loopDepthByBraces(clean) : loopDepthByIndent(clean);
}

/** Indentation-based nesting — appropriate for Python-style code. */
function loopDepthByIndent(clean: string): number {
  const lines = clean.split("\n");
  const stack: number[] = [];
  let max = 0;
  for (const line of lines) {
    if (!LOOP_RE.test(line)) continue;
    const indent = line.match(/^\s*/)?.[0].length ?? 0;
    while (stack.length && stack[stack.length - 1] >= indent) stack.pop();
    stack.push(indent);
    max = Math.max(max, stack.length);
  }
  return max;
}

/**
 * Brace-based nesting. Walk the code as a token stream of loop keywords,
 * iterator calls, parentheses and `{ } ;`. Each loop keyword sits inside all
 * currently-open loop blocks, so its depth is `openLoopBlocks + 1` — this counts
 * both `{ }` loops and brace-less single-statement loops. Semicolons inside a
 * `for (…;…;…)` header are ignored via parenthesis-depth tracking.
 */
function loopDepthByBraces(clean: string): number {
  const tokenRe =
    /\bfor\b|\bwhile\b|\bdo\b|\.(?:forEach|map|reduce|filter)\b(?=\s*\()|[(){};]/g;
  const braceIsLoop: boolean[] = []; // per open brace: did a loop header open it
  let openLoopBlocks = 0;
  let parenDepth = 0;
  let pendingLoop = false;
  let max = 0;
  let m: RegExpExecArray | null;
  while ((m = tokenRe.exec(clean))) {
    const t = m[0];
    if (t === "(") {
      parenDepth++;
    } else if (t === ")") {
      parenDepth = Math.max(0, parenDepth - 1);
    } else if (t === "{") {
      braceIsLoop.push(pendingLoop);
      if (pendingLoop) openLoopBlocks++;
      pendingLoop = false;
    } else if (t === "}") {
      if (braceIsLoop.pop()) openLoopBlocks = Math.max(0, openLoopBlocks - 1);
    } else if (t === ";") {
      if (parenDepth === 0) pendingLoop = false; // brace-less loop body ended
    } else {
      // A loop keyword / iterator call: it nests inside every open loop block.
      max = Math.max(max, openLoopBlocks + 1);
      pendingLoop = true;
    }
  }
  return max;
}

/** Detect direct self-recursion and count self-call sites. */
export function recursionInfo(code: string): { recursive: boolean; branches: number } {
  const clean = stripStrings(code);
  // function <name>(  or  def <name>(  or  const <name> = (
  const names = new Set<string>();
  const re = /(?:function\s+([A-Za-z_]\w*)|def\s+([A-Za-z_]\w*)|([A-Za-z_]\w*)\s*=\s*(?:function|\())/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(clean))) {
    const name = m[1] || m[2] || m[3];
    if (name) names.add(name);
  }
  let branches = 0;
  let recursive = false;
  for (const name of names) {
    const calls = (clean.match(new RegExp(`\\b${name}\\s*\\(`, "g")) || []).length;
    // one occurrence is the definition; >1 means it calls itself
    if (calls > 1) {
      recursive = true;
      branches = Math.max(branches, calls - 1);
    }
  }
  return { recursive, branches };
}

export function analyzeComplexity(code: string): ComplexityEstimate {
  const signals: string[] = [];
  const clean0 = stripStrings(code);
  const depth = loopDepth(code);
  const { recursive, branches } = recursionInfo(code);
  const hasSort = SORT_RE.test(clean0);
  const memoized = MEMO_RE.test(clean0);
  const twoDTable = /\[\s*\[|new\s+\w+\[[^\]]*\]\[|vector<\s*vector/.test(clean0);
  const looksBinary =
    /while\b/.test(code) && BINSEARCH_RE.test(code) && /\/\s*2|>>\s*1|\/\/\s*2/.test(code);

  let time = "O(1)";
  if (recursive && branches >= 2 && memoized) {
    // Memoized branching recursion collapses to the number of distinct states.
    time = twoDTable ? "O(n^2)" : "O(n)";
    signals.push(
      `Branching recursion (~${branches} self-calls) but memoization detected — treated as polynomial (${time}), one solve per distinct state.`
    );
  } else if (recursive && branches >= 2) {
    time = "O(2^n)";
    signals.push(`Detected branching recursion (~${branches} self-calls) — likely exponential unless memoized.`);
  } else if (depth >= 3) {
    time = "O(n^3)";
    signals.push("Three or more nested loops.");
  } else if (depth === 2) {
    time = "O(n^2)";
    signals.push("Two nested loops.");
  } else if (depth === 1) {
    time = hasSort ? "O(n log n)" : "O(n)";
    signals.push(hasSort ? "A single loop plus a sort." : "A single pass over the input.");
  } else if (hasSort) {
    time = "O(n log n)";
    signals.push("Sorting dominates the running time.");
  } else if (looksBinary) {
    time = "O(log n)";
    signals.push("Binary-search style halving loop.");
  } else if (recursive) {
    time = "O(n)";
    signals.push("Linear recursion detected.");
  } else {
    signals.push("No loops or recursion detected — constant time.");
  }

  // Space estimate.
  const clean = stripStrings(code);
  const twoD = /\[\s*\[|new\s+\w+\[[^\]]*\]\[|vector<\s*vector/.test(clean);
  const allocates =
    /\bnew\b|\[\]|\{\}|list\(|dict\(|set\(|map\(|Array\(|defaultdict|vector<|HashMap|HashSet|ArrayList/.test(
      clean
    );
  let space = "O(1)";
  if (twoD) {
    space = "O(n^2)";
    signals.push("Allocates a 2-D table.");
  } else if (allocates) {
    space = "O(n)";
    signals.push("Allocates an auxiliary linear data structure.");
  } else if (recursive) {
    space = "O(n)";
    signals.push("Recursion uses stack space.");
  }

  return { time, space, signals };
}

const ORDER = [
  "O(1)",
  "O(log n)",
  "O(n)",
  "O(n log n)",
  "O(n^2)",
  "O(n^3)",
  "O(2^n)",
  "O(n!)",
];

function canonical(s: string): string {
  return s
    .replace(/\s+/g, " ")
    .replace(/²/g, "^2")
    .replace(/³/g, "^3")
    .trim();
}

export function rank(s: string): number {
  return ORDER.indexOf(canonical(s));
}

export type Comparison = "better" | "equal" | "worse" | "unknown";

/** Compare a user's estimated complexity against the optimal. */
export function compareComplexity(userC: string, optimalC: string): Comparison {
  const a = rank(userC);
  const b = rank(optimalC);
  if (a < 0 || b < 0) return "unknown";
  if (a === b) return "equal";
  return a < b ? "better" : "worse";
}
