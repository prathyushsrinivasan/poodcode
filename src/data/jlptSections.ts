import { GRAMMAR_LESSONS } from "./n2Study/grammar";
import { READING_SKILL_LESSONS } from "./n2Study/readingSkills";
/** The JLPT landing page follows the four groups used in the practice outline. */
export const JLPT_PRACTICE: Record<string, { title: string; lessonIds: string[] }> = {
  "kanji-reading": { title: "Kanji Reading", lessonIds: ["compound-readings", "reading-choice", "compound-sound-changes", "context-readings"] },
  "kanji-spelling": { title: "Kanji Spelling", lessonIds: ["kanji-spelling", "visual-kanji", "homophone-spelling", "okurigana"] },
  context: { title: "Vocabulary in Context", lessonIds: ["context", "collocations", "confused-words", "vocabulary-particles", "transitivity", "adverbs"] },
  paraphrase: { title: "Similar Meaning", lessonIds: ["paraphrase", "word-senses"] },
  usage: { title: "Correct Usage", lessonIds: ["usage", "vocabulary-register", "usage-repair"] },
  grammar: { title: "Grammar Selection", lessonIds: ["wake", "limit", "change", ...GRAMMAR_LESSONS.map((l) => l.id)] },
  "sentence-order": { title: "Sentence Order", lessonIds: ["assembly-links"] },
  "text-grammar": { title: "Grammar in Passages", lessonIds: ["paragraph-links"] },
  "reading-skills": { title: "Reading Skills", lessonIds: [...READING_SKILL_LESSONS.map((l) => l.id), "reading-tables"] },
};

interface JlptSection {
  id: string;
  japanese: string;
  title: string;
  items: { label: string; to?: string }[];
}
const root = "/japanese/n2";
export const JLPT_SECTIONS: JlptSection[] = [
  { id: "vocabulary", japanese: "文字・語彙", title: "Kanji & Vocabulary", items: [
    { label: "Kanji Reading", to: `${root}/practice/kanji-reading` },
    { label: "Kanji Spelling", to: `${root}/practice/kanji-spelling` },
    { label: "Word Formation", to: `${root}/affixes/mixed` },
    { label: "Vocabulary in Context", to: `${root}/practice/context` },
    { label: "Similar Meaning", to: `${root}/practice/paraphrase` },
    { label: "Correct Usage", to: `${root}/practice/usage` },
  ] },
  { id: "grammar", japanese: "文法", title: "Grammar", items: [
    { label: "Grammar Selection", to: `${root}/practice/grammar` },
    { label: "Sentence Order", to: `${root}/practice/sentence-order` },
    { label: "Grammar in Passages", to: `${root}/practice/text-grammar` },
  ] },
  { id: "reading", japanese: "読解", title: "Reading", items: [
    { label: "Short Passage", to: `${root}/reading/short` },
    { label: "Medium Passage", to: `${root}/reading/medium` },
    { label: "Comparing Texts", to: `${root}/reading/ab` },
    { label: "Long Passage", to: `${root}/reading/long` },
    { label: "Information Retrieval", to: `${root}/reading/information` },
  ] },
  { id: "listening", japanese: "聴解", title: "Listening", items: [
    { label: "Task Comprehension" },
    { label: "Key Information" },
    { label: "Overall Meaning" },
    { label: "Quick Response" },
    { label: "Combining Information" },
  ] },
];
