import type { ChoiceQuestion } from "./schema";

export type ExplainedOption = readonly [text: string, why: string];
/** The first authored option is correct. IDs, not array positions, own progress. */
export function authoredChoice(id: string, lessonId: string, prompt: string,
  options: readonly [ExplainedOption, ExplainedOption, ExplainedOption, ExplainedOption],
  explanation: string, translation: string, extra: Partial<Pick<ChoiceQuestion, "focus" | "breakdown" | "tags" | "targetSeconds" | "hint" | "texts" | "evidence">> = {}): ChoiceQuestion {
  const offset = [...id].reduce((sum, char) => sum + char.charCodeAt(0), 0) % 4;
  const choices = options.map(([text, why]) => ({ text, why }));
  return { id, lessonId, kind: "choice", prompt, choices: [...choices.slice(offset), ...choices.slice(0, offset)],
    answer: (4 - offset) % 4, explanation, translation, targetSeconds: 35, tags: [],
    hint: "Use the complete sentence to check the meaning and form of the word.", ...extra };
}
