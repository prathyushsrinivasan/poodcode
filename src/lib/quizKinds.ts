// Quiz question kinds beyond plain multiple choice (TS_MASTERY_ROADMAP X-31).
//
//   ""        one right option (the default)
//   "output"  the same, but the question carries a program and the options are
//             what it might print — rendered as program output
//   "multi"   select every right option; `answers` lists them
//   "type"    type the answer: the learner's text becomes `type Answer = …`
//             after the question's code, and the hidden `harness` of
//             `Expect<Equal<Answer, …>>` claims has to compile
//
// Every quiz UI grades with `picked === answer` and keeps `picked` as one
// number (-1 = unanswered). The kinds keep that contract, so a sitting, its
// stats and its saved misses need no special cases:
//
//   multi — `picked` is MULTI plus a bitmask of the selected options, and a
//           drawn paper's `answer` is MULTI plus the mask of the right ones
//   type  — `picked` is 0 once the typed answer checks, 1 when it does not;
//           `answer` is 0

import type { QuizQuestion } from "../types";

/** Offset for multi-select picks: far above any option index. */
export const MULTI = 1 << 20;

export type QuizKind = "" | "output" | "multi" | "type";

export function quizKind(q: { kind?: string }): QuizKind {
  return q.kind === "output" || q.kind === "multi" || q.kind === "type" ? q.kind : "";
}

/** The mask for a set of option indices. */
export function maskOf(indices: number[]): number {
  return indices.reduce((m, i) => m | (1 << i), 0);
}

/** Toggle one option of a multi-select pick; clearing the last one unanswers it. */
export function toggleMulti(picked: number, option: number): number {
  const mask = (picked >= MULTI ? picked - MULTI : 0) ^ (1 << option);
  return mask === 0 ? -1 : MULTI + mask;
}

/** Whether option `i` is selected in a multi-select pick. */
export function isSelected(picked: number, i: number): boolean {
  return picked >= MULTI && ((picked - MULTI) & (1 << i)) !== 0;
}

/** The value `picked` must equal for a question to be right. */
export function expectedPick(q: Pick<QuizQuestion, "answer" | "answers" | "kind">): number {
  if (quizKind(q) === "multi") return MULTI + maskOf(q.answers ?? []);
  if (quizKind(q) === "type") return 0;
  return q.answer;
}

/** The right answer as text — the back of a flashcard made from a miss. */
export function answerText(q: Pick<QuizQuestion, "options" | "answer" | "answers" | "kind" | "type_answer">): string {
  const kind = quizKind(q);
  if (kind === "type") return "`" + (q.type_answer ?? q.options[0] ?? "") + "`";
  if (kind === "multi") return (q.answers ?? []).map((i) => "- " + q.options[i]).join("\n");
  const text = q.options[q.answer] ?? "";
  return kind === "output" ? "```text\n" + text + "\n```" : text;
}

/** A question with its options shuffled: `answers`/`answer` follow the options. */
export function reorderOptions<Q extends QuizQuestion>(q0: Q, options: string[]): Q {
  const at = (i: number) => options.indexOf(q0.options[i]!);
  // `why_not` is parallel to the options, so it moves with them.
  const q: Q = q0.why_not
    ? { ...q0, why_not: options.map((o) => q0.why_not![q0.options.indexOf(o)] ?? "") }
    : q0;
  if (quizKind(q) === "multi") {
    const answers = (q0.answers ?? []).map(at).sort((a, b) => a - b);
    return { ...q, options, answers, answer: MULTI + maskOf(answers) };
  }
  if (quizKind(q) === "type") return { ...q, options, answer: 0 };
  return { ...q, options, answer: at(q0.answer) };
}

/** The program a typed answer is checked as, and the text it may not use:
 * spelling the type out is the question, so `typeof x` is not an answer. */
export function typeAnswerProgram(q: Pick<QuizQuestion, "code">, typed: string): string {
  return `${(q.code ?? "").trimEnd()}\ntype Answer = ${typed.trim()};\n`;
}
export const TYPE_ANSWER_FORBID = ["typeof", "ReturnType", "Parameters", "keyof"];

/** The first banned word in a typed answer, if any. */
export function bannedIn(typed: string): string | null {
  return TYPE_ANSWER_FORBID.find((w) => new RegExp(`\\b${w}\\b`).test(typed)) ?? null;
}

/** The front of a flashcard made from a missed question: the question, and
 * its program when it has one — "what does this print?" means nothing alone. */
export function questionText(q: Pick<QuizQuestion, "question" | "code">): string {
  return q.code ? `${q.question}\n\n\`\`\`ts\n${q.code.trimEnd()}\n\`\`\`` : q.question;
}
