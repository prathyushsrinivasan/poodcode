export type ReadingKind = "short" | "medium" | "ab" | "long" | "information";
export type ReadingSkill = "Main point" | "Reason" | "Intention" | "Inference" | "Reference" | "Comparison" | "Find information";
export interface ReadingWord { text: string; reading: string; meaning: string; lemma?: string }
export interface ReadingQuestion {
  id: string;
  prompt: string;
  choices: { text: string; explanation: string }[];
  answer: number;
  evidence: string[];
  explanation: string;
}
export interface ReadingPassage {
  id: string;
  kind: ReadingKind;
  title: string;
  topic: string;
  skill: ReadingSkill;
  level: 1 | 2 | 3;
  texts: { label?: string; text: string; translation: string }[];
  questions: ReadingQuestion[];
}
export interface QuestionDraft {
  prompt: string;
  correct: string;
  evidence: string[];
  explanation: string;
  wrong: [string, string][];
}
// Choices retain their authored explanations when moved. Stable rotation keeps
// answer positions varied without changing the meaning or saved question IDs.
export function question(id: string, draft: QuestionDraft): ReadingQuestion {
  const choices = [{ text: draft.correct, explanation: draft.explanation },
    ...draft.wrong.map(([text, explanation]) => ({ text, explanation }))];
  const offset = [...id].reduce((n, c) => n + c.charCodeAt(0), 0) % 4;
  return { id, prompt: draft.prompt, choices: [...choices.slice(offset), ...choices.slice(0, offset)],
    answer: (4 - offset) % 4, evidence: draft.evidence, explanation: draft.explanation };
}
export type ShortDraft = [title: string, topic: string, skill: ReadingSkill, level: 1 | 2 | 3,
  text: string, translation: string, prompt: string, correct: string, evidence: string,
  explanation: string, wrong: [string, string][]];
export function shortPassage(row: ShortDraft, index: number): ReadingPassage {
  const [title, topic, skill, level, text, translation, prompt, correct, evidence, explanation, wrong] = row;
  const id = `short-${String(index + 1).padStart(3, "0")}`;
  return { id, kind: "short", title, topic, skill, level, texts: [{ text, translation }],
    questions: [question(`${id}-q1`, { prompt, correct, evidence: [evidence], explanation, wrong })] };
}
