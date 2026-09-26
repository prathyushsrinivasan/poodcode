// A lesson's "### Pitfalls" section, split into one card per pitfall
// (TS_MASTERY_ROADMAP X-05). Each pitfall is a `#### title` followed by the
// wrong program, what it does, why, and the fix — long enough that a list of
// them reads as a wall; as collapsed cards the titles become a checklist.

export type Pitfall = { title: string; body: string };
export type LessonParts = { before: string; heading: string; pitfalls: Pitfall[]; after: string };

/** Split `lesson` around its `### Pitfalls` section, or null when it has none.
 * Fenced code is skipped, so a `###` inside a code block never counts. */
export function splitPitfalls(lesson: string): LessonParts | null {
  const lines = lesson.split("\n");
  let inFence = false;
  let start = -1;
  let end = lines.length;
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i]!;
    if (ln.startsWith("```")) inFence = !inFence;
    if (inFence) continue;
    if (start < 0 && /^###\s+Pitfalls\s*$/.test(ln)) start = i;
    else if (start >= 0 && /^#{1,3}\s/.test(ln)) {
      end = i;
      break;
    }
  }
  if (start < 0) return null;
  const pitfalls: Pitfall[] = [];
  inFence = false;
  let current: Pitfall | null = null;
  const intro: string[] = [];
  for (const ln of lines.slice(start + 1, end)) {
    if (ln.startsWith("```")) inFence = !inFence;
    const m = !inFence && /^####\s+(.*)$/.exec(ln);
    if (m) {
      current = { title: m[1]!.trim(), body: "" };
      pitfalls.push(current);
    } else if (current) current.body += ln + "\n";
    else intro.push(ln);
  }
  if (pitfalls.length === 0) return null;
  for (const p of pitfalls) p.body = p.body.trim();
  return {
    before: lines.slice(0, start).join("\n").trimEnd(),
    heading: [lines[start]!, ...intro].join("\n").trim(),
    pitfalls,
    after: lines.slice(end).join("\n").trimStart(),
  };
}
