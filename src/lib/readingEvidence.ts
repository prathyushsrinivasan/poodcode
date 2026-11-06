import { plainReading } from "./dokkaiText";

export interface EvidenceSentence { id: string; text: string; textIndex: number; start: number; end: number }
export function evidenceSentences(texts: { text: string }[]): EvidenceSentence[] {
  return texts.flatMap((source, textIndex) => {
    const plain = plainReading(source.text);
    const result: EvidenceSentence[] = [];
    const quotes: string[] = [];
    let from = 0;
    const flush = (end: number) => {
      const raw = plain.slice(from, end), text = raw.trim();
      if (text) {
        const start = from + raw.indexOf(text);
        result.push({ id: `${textIndex}:${start}`, text, textIndex, start, end: start + text.length });
      }
      from = end;
    };
    for (let index = 0; index < plain.length; index++) {
      const char = plain[index];
      if (char === "「") quotes.push("」");
      else if (char === "『") quotes.push("』");
      else if (char === quotes[quotes.length - 1]) quotes.pop();
      if (char === "\n" || (!quotes.length && "。！？".includes(char))) flush(index + 1);
    }
    flush(plain.length);
    return result;
  });
}
/** Feedback concerns overlap with authored evidence, not a new JLPT score. */
export function compareEvidence(texts: { text: string }[], quotes: string[], selected: string[]) {
  const sentences = evidenceSentences(texts);
  const chosen = sentences.filter((sentence) => selected.includes(sentence.id));
  const supports = (sentence: EvidenceSentence, quote: string) => {
    const plain = plainReading(texts[sentence.textIndex].text);
    if (!quote) return false;
    for (let at = plain.indexOf(quote); at >= 0; at = plain.indexOf(quote, at + quote.length)) {
      if (sentence.start < at + quote.length && sentence.end > at) return true;
    }
    return false;
  };
  return {
    selected: chosen,
    matching: chosen.filter((sentence) => quotes.some((quote) => supports(sentence, quote))),
    coversAll: quotes.length > 0 && quotes.every((quote) => chosen.some((sentence) => supports(sentence, quote))),
  };
}
