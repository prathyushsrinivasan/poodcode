// The two exercise kinds that are not typed into an editor (TS_MASTERY_ROADMAP
// X-15, X-16):
//
//   order — a Parsons problem. The program's lines arrive shuffled; the learner
//           reorders them and the result is judged by running it, so any order
//           that prints the right thing is right (two independent declarations
//           may go either way round).
//   spot  — "click the buggy line". The exercise names the lines of its
//           starter that the fix changes; clicking any of them solves it.
//
// The program for an `order` exercise is stored as ordinary source text — one
// piece per line — so saving, resetting and judging work exactly as they do
// for code typed into the editor.

/** A program's pieces: its lines, without the final newline's empty line. */
export function toLines(code: string): string[] {
  const lines = code.split("\n");
  if (lines.length > 0 && lines[lines.length - 1] === "") lines.pop();
  return lines;
}

/** The program a list of pieces makes. */
export function fromLines(lines: string[]): string {
  return lines.join("\n") + "\n";
}

/** Move the piece at `from` so that it ends up at index `to`. Out-of-range
 * moves leave the list as it was. */
export function moveLine(lines: string[], from: number, to: number): string[] {
  if (from === to || from < 0 || to < 0 || from >= lines.length || to >= lines.length) return lines;
  const next = [...lines];
  const [piece] = next.splice(from, 1);
  next.splice(to, 0, piece!);
  return next;
}

/** How many pieces already sit where the reference program has them — a hint
 * of progress, never the grade (the grade is running the program). */
export function inPlace(lines: string[], solution: string): number {
  const want = toLines(solution);
  return lines.reduce((n, line, i) => n + (want[i] === line ? 1 : 0), 0);
}

/** A spot-the-bug click: right when the 1-based `line` is one the fix changes. */
export function isBugLine(bugLines: number[] | undefined, line: number): boolean {
  return (bugLines ?? []).includes(line);
}
