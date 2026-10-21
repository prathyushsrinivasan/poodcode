import entries from "./words.json";

export interface KanjiWord {
  id: string;
  written: string;
  readings: string[];
  levels: string[];
  meanings: string[];
  cue: string;
  note: string;
  aliases: string[];
  source: string;
  dictionaryIds: string[];
  options: { text: string; correct: boolean; explanation: string }[];
}
export const KANJI_WORDS: KanjiWord[] = entries;
export const KANJI_WORD_BY_ID = new Map(KANJI_WORDS.map((word) => [word.id, word]));
export const KANJI_GROUPS = [
  { id: "life", kanji: "生", gloss: "Life, birth & growth" },
  { id: "learning", kanji: "学", gloss: "Learning & scholarship" },
  { id: "meeting", kanji: "会", gloss: "Meeting & association" },
  { id: "people", kanji: "人", gloss: "People & human affairs" },
  { id: "heart", kanji: "心", gloss: "Heart, mind & feelings" },
  { id: "intention", kanji: "意", gloss: "Intention, meaning & ideas" },
  { id: "power", kanji: "力", gloss: "Power, effort & ability" },
  { id: "going", kanji: "行", gloss: "Going, conduct & carrying out" },
  { id: "movement", kanji: "動", gloss: "Movement, action & change" },
  { id: "affairs", kanji: "事", gloss: "Matters, events & work" },
  { id: "things", kanji: "物", gloss: "Things, materials & objects" },
  { id: "together", kanji: "合", gloss: "Joining, fitting & combining" },
  { id: "settled", kanji: "定", gloss: "Fixing, deciding & establishing" },
  { id: "becoming", kanji: "成", gloss: "Becoming, achieving & forming" },
  { id: "change", kanji: "化", gloss: "Change & transformation" },
  { id: "nature", kanji: "性", gloss: "Nature, qualities & properties" },
  { id: "expression", kanji: "表", gloss: "Surface, expression & representation" },
  { id: "taking", kanji: "取", gloss: "Taking, obtaining & handling" },
  { id: "exchange", kanji: "交", gloss: "Exchange, crossing & interaction" },
  { id: "division", kanji: "分", gloss: "Dividing, shares & distinctions" },
] as const;
export type KanjiGroup = (typeof KANJI_GROUPS)[number];
export const wordsForKanji = (kanji: string) => KANJI_WORDS.filter((word) => word.written.includes(kanji));
export const KANJI_PROGRESS_KEY = "jlpt-kanji-word-practice-v1";
