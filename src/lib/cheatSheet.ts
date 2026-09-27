// A one-screen cheat sheet for a TypeScript chapter (TS_MASTERY_ROADMAP X-08),
// built from the lesson itself so it can never disagree with it: the worked
// examples' titles, the compiler errors it shows (named from the error
// glossary), each pitfall with the first sentence of its explanation, and the
// interview questions.

import { splitPitfalls } from "./lessonSections";

export type CheatSheet = {
  examples: string[];
  errors: { code: number; title: string }[];
  pitfalls: { title: string; gist: string }[];
  questions: string[];
  /** X-08: the chapter's "Key terms" section, `- **term** — definition`. */
  terms: { term: string; def: string }[];
};

/** The lines of `md` outside fenced code blocks. */
function prose(md: string): string[] {
  let fence = false;
  return md.split("\n").filter((ln) => {
    if (ln.startsWith("```")) {
      fence = !fence;
      return false;
    }
    return !fence;
  });
}

/** The body of a `### Name` section (to the next `###` or higher heading). */
function section(md: string, name: RegExp): string {
  const lines = md.split("\n");
  let fence = false;
  let start = -1;
  const out: string[] = [];
  for (const ln of lines) {
    if (ln.startsWith("```")) fence = !fence;
    if (!fence && /^#{1,3}\s/.test(ln)) {
      if (start >= 0) break;
      if (name.test(ln.replace(/^#+\s*/, ""))) start = 1;
      continue;
    }
    if (start >= 0) out.push(ln);
  }
  return out.join("\n");
}

function firstSentence(text: string): string {
  const t = text.trim();
  const m = /^(.+?[.!?])(\s|$)/.exec(t);
  return (m ? m[1]! : t).trim();
}

export function cheatSheet(lesson: string, glossary: Map<number, string>): CheatSheet {
  const examples = ["Worked examples", "More worked examples"].flatMap((s) =>
    prose(section(lesson, new RegExp(`^${s}$`)))
      .filter((ln) => ln.startsWith("#### "))
      .map((ln) => ln.slice(5).trim())
  );

  const errors: { code: number; title: string }[] = [];
  for (const m of lesson.matchAll(/error TS(\d+)/g)) {
    const code = Number(m[1]);
    if (!errors.some((e) => e.code === code)) errors.push({ code, title: glossary.get(code) ?? "" });
  }

  const pitfalls = (splitPitfalls(lesson)?.pitfalls ?? []).map((p) => {
    const para = prose(p.body)
      .map((ln) => ln.trim())
      .filter((ln) => ln && !/^(Prints|Input|The compiler says):?$/.test(ln))[0];
    return { title: p.title, gist: para ? firstSentence(para) : "" };
  });

  const questions = prose(section(lesson, /^In an interview$/))
    .map((ln) => /^\*\*(.+)\*\*$/.exec(ln.trim())?.[1])
    .filter((q): q is string => !!q);

  const terms = prose(section(lesson, /^Key terms$/))
    .map((ln) => /^- \*\*(.+?)\*\* — (.+)$/.exec(ln.trim()))
    .filter((m): m is RegExpExecArray => m !== null)
    .map((m) => ({ term: m[1]!, def: m[2]! }));

  return { examples, errors, pitfalls, questions, terms };
}

/** The sheet as Markdown, for display and printing. */
export function cheatSheetMarkdown(name: string, what: string, s: CheatSheet): string {
  const parts = [`## ${name}`, what];
  if (s.examples.length) parts.push("**Worked examples** — " + s.examples.join(" · "));
  if (s.errors.length)
    parts.push("**Errors you will meet**\n\n" + s.errors.map((e) => `- \`TS${e.code}\`${e.title ? " — " + e.title : ""}`).join("\n"));
  if (s.pitfalls.length)
    parts.push("**Pitfalls**\n\n" + s.pitfalls.map((p) => `- **${p.title}**${p.gist ? " — " + p.gist : ""}`).join("\n"));
  if (s.terms.length) parts.push("**Key terms**\n\n" + s.terms.map((t) => `- **${t.term}** — ${t.def}`).join("\n"));
  if (s.questions.length) parts.push("**Can you answer?**\n\n" + s.questions.map((q) => `- ${q}`).join("\n"));
  return parts.join("\n\n");
}
