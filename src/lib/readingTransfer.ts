import { READING_PASSAGES } from "../data/dokkai";
import { COMMON_READING_WORDS } from "../data/dokkai/vocabulary";
import type { ReadingPassage, ReadingWord } from "../data/dokkai/types";
import { plainReading, readingSegments, wordKey } from "./dokkaiText";
import { evidenceSentences } from "./readingEvidence";

export interface TransferExample { passageId: string; kind: string; title: string; sentence: string; wordText: string; at: number }
export function readingTransferExamples(word: ReadingWord, source: string, passages: readonly ReadingPassage[] = READING_PASSAGES,
  shared = COMMON_READING_WORDS, limit = 3): TransferExample[] {
  if (limit <= 0) return [];
  const key = wordKey(word);
  const fallback = shared.filter((candidate) => wordKey(candidate) === key);
  const examples: TransferExample[] = [];
  const seen = new Set<string>();
  for (const passage of passages) {
    if (passage.id === source) continue;
    for (const text of passage.texts) {
      const plain = plainReading(text.text);
      if (!plain.includes(word.text) && !(word.lemma && plain.includes(word.lemma))) continue;
      const sentences = evidenceSentences([text]);
      let offset = 0;
      for (const segment of readingSegments(text.text, fallback)) {
        if (segment.word && wordKey(segment.word) === key) {
          const sentence = sentences.find((s) => s.start <= offset && s.end >= offset + segment.text.length);
          if (sentence && !seen.has(sentence.text)) {
            examples.push({ passageId: passage.id, kind: passage.kind, title: passage.title,
              sentence: sentence.text, wordText: segment.text, at: offset - sentence.start });
            seen.add(sentence.text);
            if (examples.length >= limit) return examples;
            // One example per passage keeps the contexts varied.
            break;
          }
        }
        offset += segment.text.length;
      }
      if (examples[examples.length - 1]?.passageId === passage.id) break;
    }
  }
  return examples;
}
