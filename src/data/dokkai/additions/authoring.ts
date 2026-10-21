import { question, type ReadingKind, type ReadingPassage, type ReadingSkill } from "../types";

// Explicit passage IDs protect saved progress; questions keep their authored order.
export type ExtendedQuestion = [prompt: string, correct: string, evidence: string[], explanation: string,
  wrong1: string, why1: string, wrong2: string, why2: string, wrong3: string, why3: string];
export function extended(id: string, kind: ReadingKind, title: string, topic: string, skill: ReadingSkill,
  level: 1 | 2 | 3, texts: ReadingPassage["texts"], drafts: ExtendedQuestion[]): ReadingPassage {
  return { id, kind, title, topic, skill, level, texts,
    questions: drafts.map(([prompt, correct, evidence, explanation, a, ax, b, bx, c, cx], i) =>
      question(`${id}-q${i + 1}`, { prompt, correct, evidence, explanation, wrong: [[a, ax], [b, bx], [c, cx]] })) };
}
