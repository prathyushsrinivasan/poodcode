import { SHORT_WORK } from "./shortWork";
import { SHORT_LEARNING } from "./shortLearning";
import { SHORT_COMMUNITY } from "./shortCommunity";
import { SHORT_LIFE } from "./shortLife";
import { EXTENDED_PASSAGES } from "./extended";
import { MEDIUM_SET_01 } from "./medium/set01";
import { MEDIUM_SET_02 } from "./medium/set02";
import { MEDIUM_SET_03 } from "./medium/set03";
import { MEDIUM_SET_04 } from "./medium/set04";
import { MEDIUM_SET_05 } from "./medium/set05";
import { MEDIUM_SET_06 } from "./medium/set06";
import { MEDIUM_SET_07 } from "./medium/set07";
import { MEDIUM_SET_08 } from "./medium/set08";
import { MEDIUM_SET_09 } from "./medium/set09";
import { MEDIUM_SET_10 } from "./medium/set10";
import { PAIRED_PASSAGES } from "./paired";
import { LONG_PASSAGES } from "./long";
import { INFORMATION_PASSAGES } from "./information";
import { ADDITIONAL_PAIRED_PASSAGES } from "./additions/paired";
import { ADDITIONAL_LONG_PASSAGES } from "./additions/long";
import { ADDITIONAL_INFORMATION_PASSAGES } from "./additions/information";
import { shortPassage, type ReadingKind, type ReadingPassage, type ReadingSkill } from "./types";
export const READING_SECTIONS: { id: ReadingKind; name: string; english: string; length: string; description: string }[] = [
  { id: "short", name: "短文", english: "Short passages", length: "About 200 characters", description: "One focused question. Build accuracy with reasons, references, intentions and main points." },
  { id: "medium", name: "中文", english: "Medium passages", length: "About 500 characters", description: "100 passages in ten practice sets. Follow examples and contrasts across paragraphs, then answer two questions." },
  { id: "ab", name: "AB問題文・統合理解", english: "Compare two texts", length: "About 300 characters each", description: "Find shared positions and distinguish each writer's emphasis." },
  { id: "long", name: "長文・主張理解", english: "Long passages", length: "About 1,000 characters", description: "Follow a sustained argument and connect individual examples to its conclusion." },
  { id: "information", name: "情報検索", english: "Information retrieval", length: "About 700 characters", description: "Read notices and guides. Combine conditions, deadlines, fees and exceptions." },
];
export const READING_PASSAGES: ReadingPassage[] = [
  ...[...SHORT_WORK, ...SHORT_LEARNING, ...SHORT_COMMUNITY, ...SHORT_LIFE].map(shortPassage),
  ...EXTENDED_PASSAGES,
  ...MEDIUM_SET_01, ...MEDIUM_SET_02, ...MEDIUM_SET_03, ...MEDIUM_SET_04, ...MEDIUM_SET_05,
  ...MEDIUM_SET_06, ...MEDIUM_SET_07, ...MEDIUM_SET_08, ...MEDIUM_SET_09, ...MEDIUM_SET_10,
  ...PAIRED_PASSAGES, ...ADDITIONAL_PAIRED_PASSAGES,
  ...LONG_PASSAGES, ...ADDITIONAL_LONG_PASSAGES,
  ...INFORMATION_PASSAGES, ...ADDITIONAL_INFORMATION_PASSAGES,
];
export const READING_QUESTIONS = READING_PASSAGES.flatMap((p) => p.questions);
export const READING_TIPS: Record<ReadingSkill, string> = {
  "Main point": "Find the claim that covers the whole passage. An example supports the claim; it is not necessarily the claim itself. Check the ending and contrast words such as しかし.",
  Reason: "Ask what the stated action responds to. Look for から, ため and the situation immediately before the action. Distinguish the original reason from a later benefit.",
  Intention: "Identify who wants whom to do what. Follow the request, then check why it is being made. A deadline for preparation is not necessarily a deadline for the main event.",
  Inference: "Choose only what the text supports. Be careful with 必ず, 全て and だけ: a qualified claim such as とは限らない does not prove its opposite is always true.",
  Reference: "Look just before これ・それ・この方法. Replace the reference with your candidate and reread. It may refer to a whole process rather than the nearest noun.",
  Comparison: "Summarize A and B separately first. Match agreement at the same level, then identify a point supported by only one writer. Do not transfer A's example to B.",
  "Find information": "Read the person's needs first. Locate the relevant heading, then check every condition and exception. Combine deadline, eligibility and cost rules before choosing.",
};
