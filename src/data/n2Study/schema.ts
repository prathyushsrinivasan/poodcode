/** Stable, content-only contracts. Learning state belongs in lib/n2Study. */
export const STUDY_SECTIONS = [
  { id: "kanji", title: "Kanji readings", japanese: "漢字の読み", description: "Recognize the word, recall its reading." },
  { id: "vocabulary", title: "Vocabulary", japanese: "語彙", description: "Word building, context, paraphrases and natural usage." },
  { id: "grammar", title: "Grammar contrasts", japanese: "文法形式", description: "Understand the difference between similar patterns." },
  { id: "assembly", title: "Sentence assembly", japanese: "文の組み立て ★", description: "Connect fragments, then check the whole sentence." },
  { id: "text", title: "Text grammar", japanese: "文章の文法", description: "Follow connections across a paragraph." },
  { id: "reading", title: "Reading", japanese: "読解", description: "Find the claim, evidence and conditions." },
] as const;
export type StudySection = typeof STUDY_SECTIONS[number]["id"];
export interface StudyLesson {
  id: string;
  section: StudySection;
  title: string;
  format: string;
  takeaway: string;
  steps: string[];
  trap: string;
  examples: { japanese: string; english: string }[];
  next?: { label: string; href: string };
}
interface BaseQuestion {
  id: string;
  lessonId: string;
  prompt: string;
  hint: string;
  explanation: string;
  translation: string;
  targetSeconds: number;
  tags: string[];
  texts?: { label?: string; text: string; translation: string }[];
  evidence?: string[];
}
export interface ChoiceQuestion extends BaseQuestion {
  kind: "choice";
  choices: { text: string; why: string; trap?: string }[];
  answer: number;
}
export interface TypedQuestion extends BaseQuestion {
  kind: "typed";
  answers: string[];
  word: string;
  meaning: string;
}
export interface AssemblyQuestion extends BaseQuestion {
  kind: "assembly";
  before: string;
  after: string;
  fragments: string[];
  order: number[];
  acceptedOrders?: number[][];
  starIndex: number;
}
export type StudyQuestion = ChoiceQuestion | TypedQuestion | AssemblyQuestion;
