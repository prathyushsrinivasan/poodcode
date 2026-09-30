// Where a piece of Markdown's outline starts, so Markdown.tsx can seat its
// headings under the page's own (UI_ROADMAP D9).

/** The shallowest ATX heading in `md` (1-6), or null when it has none. Fenced
 * code is skipped, so a `# comment` in a bash block never counts. */
export function topHeadingLevel(md: string): number | null {
  let top: number | null = null;
  let fence: string | null = null;
  for (const line of md.split("\n")) {
    const f = /^\s{0,3}(`{3,}|~{3,})/.exec(line);
    if (f) {
      if (fence === null) fence = f[1]![0]!;
      else if (f[1]![0] === fence) fence = null;
      continue;
    }
    if (fence !== null) continue;
    const h = /^\s{0,3}(#{1,6})(\s|$)/.exec(line);
    if (h && (top === null || h[1]!.length < top)) top = h[1]!.length;
  }
  return top;
}
