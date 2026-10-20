import { question, type ReadingPassage, type ReadingSkill } from "../types";

// Each question carries its own evidence and option-specific trap explanations.
export type MediumQuestion = [prompt: string, correct: string, evidence: string,
  explanation: string, wrong1: string, why1: string, wrong2: string, why2: string,
  wrong3: string, why3: string];
export function medium(id: string, title: string, topic: string, skill: ReadingSkill,
  level: 1 | 2 | 3, text: string, translation: string,
  drafts: [MediumQuestion, MediumQuestion, ...MediumQuestion[]]): ReadingPassage {
  return { id, kind: "medium", title, topic, skill, level, texts: [{ text, translation }],
    questions: drafts.map(([prompt, correct, quote, explanation, a, ax, b, bx, c, cx], i) =>
      question(`${id}-q${i + 1}`, { prompt, correct, evidence: [quote], explanation,
        wrong: [[a, ax], [b, bx], [c, cx]] })) };
}
