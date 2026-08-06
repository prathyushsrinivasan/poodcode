// Parser for the Visual Debugger's "trace my code" protocol. A program emits
// lines like `#T arr=[1, 2, 3] i=0 lo=2`; each becomes a step of named variable
// snapshots. Pure and dependency-free so it can be unit-tested.

export interface TraceStep {
  line: string;
  vars: Record<string, number | number[] | string>;
}

/** Parse all `#T ...` lines from a program's stdout into ordered steps. */
export function parseTrace(stdout: string): TraceStep[] {
  const steps: TraceStep[] = [];
  for (const raw of stdout.split("\n")) {
    const m = raw.match(/^\s*#T\s+(.*)$/);
    if (!m) continue;
    const vars: Record<string, number | number[] | string> = {};
    // key=value where value is [list], "quoted", or a bare token.
    const re = /(\w+)=(\[[^\]]*\]|"[^"]*"|\S+)/g;
    let mm: RegExpExecArray | null;
    while ((mm = re.exec(m[1]))) {
      const key = mm[1];
      const val = mm[2];
      if (val.startsWith("[")) {
        const inner = val.slice(1, -1).trim();
        vars[key] = inner ? inner.split(/[,\s]+/).filter(Boolean).map(Number) : [];
      } else if (/^-?\d+$/.test(val)) {
        vars[key] = Number(val);
      } else {
        vars[key] = val.replace(/^"|"$/g, "");
      }
    }
    steps.push({ line: m[1], vars });
  }
  return steps;
}
