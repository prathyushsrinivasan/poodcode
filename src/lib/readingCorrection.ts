import { normalizeHiragana } from "./kanjiWords";

export interface ReadingPart { text: string; changed: boolean }
/** Align kana by edit distance, so a missing kana does not mark the whole tail wrong. */
export function readingCorrection(input: string, accepted: readonly string[]) {
  const actual = [...normalizeHiragana(input)];
  function align(target: string) {
    const expected = [...target];
    const distance = Array.from({ length: actual.length + 1 }, (_, i) => Array.from({ length: expected.length + 1 }, (_, j) => i === 0 ? j : j === 0 ? i : 0));
    for (let i = 1; i <= actual.length; i++) for (let j = 1; j <= expected.length; j++) {
      distance[i][j] = Math.min(distance[i - 1][j] + 1, distance[i][j - 1] + 1, distance[i - 1][j - 1] + Number(actual[i - 1] !== expected[j - 1]));
    }
    const given: ReadingPart[] = [], correct: ReadingPart[] = [];
    let i = actual.length, j = expected.length;
    while (i || j) {
      if (i && j && distance[i][j] === distance[i - 1][j - 1] + Number(actual[i - 1] !== expected[j - 1])) {
        const changed = actual[i - 1] !== expected[j - 1];
        given.unshift({ text: actual[--i], changed }); correct.unshift({ text: expected[--j], changed });
      } else if (j && distance[i][j] === distance[i][j - 1] + 1) {
        correct.unshift({ text: expected[--j], changed: true });
      } else given.unshift({ text: actual[--i], changed: true });
    }
    return { given, correct, distance: distance[actual.length][expected.length], target };
  }
  const candidates = accepted.map((value) => align(normalizeHiragana(value))).sort((a, b) => a.distance - b.distance);
  return candidates[0] ?? { given: actual.map((text) => ({ text, changed: false })), correct: [], distance: 0, target: "" };
}
