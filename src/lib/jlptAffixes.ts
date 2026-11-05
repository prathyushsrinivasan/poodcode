import { AFFIX_QUESTIONS, type AffixKind, type AffixLevel, type AffixQuestion } from "../data/jlptAffixes";
import { n2ResumeIndex, type N2Progress } from "./jlptN2";
import { seededRandom, shuffleWith } from "./quizShuffle";

export interface AffixFilters {
  level: AffixLevel | "all";
  kind: AffixKind | "all";
  affix: string;
  query: string;
}

export function filterAffixQuestions(filters: AffixFilters, questions = AFFIX_QUESTIONS) {
  const query = filters.query.trim().normalize("NFKC").toLowerCase();
  return questions.filter((q) => (filters.level === "all" || q.level === filters.level) &&
    (filters.kind === "all" || q.kind === filters.kind) && (!filters.affix || q.answer === filters.affix) &&
    (!query || `${q.sentence} ${q.answer} ${q.word} ${q.reading} ${q.translation} ${q.explanation}`
      .normalize("NFKC").toLowerCase().includes(query)));
}

/** Snapshot before recording any answers so correcting a mistake never changes
 * the active round. Mix without replacement; lesson practice resumes first. */
export function drawAffixRound(questions: AffixQuestion[], progress: N2Progress,
  mode: "lesson" | "mixed" | "review", size: number, seed: number): AffixQuestion[] {
  if (mode === "mixed") return shuffleWith(questions, seededRandom(seed)).slice(0, size);
  if (mode === "review") return questions.filter((q) => progress[q.id] && !progress[q.id].lastCorrect);
  const start = n2ResumeIndex(questions, progress);
  return [...questions.slice(start), ...questions.slice(0, start)];
}
