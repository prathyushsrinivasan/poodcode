/**
 * Reading helpers shared by every deck that asks you to *type* a Japanese
 * reading — the Learn tab's glossary cards (`CardStudy`) and the 日本語
 * vocabulary list.
 *
 * The two decks store a reading in different shapes: a glossary card carries
 * "へんすう (hensū)" in one string, while a vocabulary word keeps the hiragana
 * and the rōmaji in separate fields. `kanaOf` / `romajiOf` pull the halves out
 * of the first shape, `joinReading` builds it from the second, and
 * `acceptsReading` is the one grader both decks call — so a typed answer is
 * never judged by two slightly different rules.
 */

/** Any hiragana or katakana character. */
const KANA = /[ぁ-ゟァ-ヺ]/;

/** The kana half of a reading: "へんすう (hensū)" → "へんすう". A katakana
 * loanword is stored as bare rōmaji ("kōdo") and has no kana half, so "". */
export function kanaOf(reading: string): string {
  const head = reading.split("(")[0].trim();
  return KANA.test(head) ? head : "";
}

/** The rōmaji half: "へんすう (hensū)" → "hensū". A reading that is already
 * bare rōmaji is returned as it stands. */
export function romajiOf(reading: string): string {
  const m = reading.match(/\(([^)]+)\)/);
  return (m ? m[1] : reading).trim();
}

/** Build the "かな (rōmaji)" shape from the two fields a vocabulary word keeps
 * apart, so it can be graded by the same helpers. */
export function joinReading(kana: string, romaji: string): string {
  return romaji ? `${kana} (${romaji})` : kana;
}

/**
 * Normalize rōmaji for lenient typed grading: lowercase, fold the long-vowel
 * macrons, drop everything that isn't a latin letter, then collapse the long
 * vowels themselves — so the three ways people actually type けいしょう
 * ("keishō", "keishou", "keishoo") all grade the same.
 *
 * "ei" is deliberately left alone: in Hepburn it is two vowels (せいてき is
 * "seiteki", never "sēteki"), and collapsing it would accept "setki".
 */
export function normRomaji(s: string): string {
  return s
    .toLowerCase()
    .replace(/[āáàâ]/g, "a")
    .replace(/[īíìî]/g, "i")
    .replace(/[ūúùû]/g, "u")
    .replace(/[ēéèê]/g, "e")
    .replace(/[ōóòô]/g, "o")
    .replace(/[^a-z]/g, "")
    .replace(/ou/g, "o")
    .replace(/([aiueo])\1+/g, "$1");
}

/** Normalize typed kana: drop spacing and the long-vowel mark, and read
 * katakana as hiragana so either script is accepted. */
export function normKana(s: string): string {
  return s
    .replace(/[\s・ー]/g, "")
    .replace(/[ァ-ヶ]/g, (c) => String.fromCharCode(c.charCodeAt(0) - 0x60));
}

/**
 * Does `typed` answer `reading`? Input containing kana is compared against the
 * kana half, anything else against the rōmaji half — so the answer can be typed
 * in whichever script the learner's keyboard is in.
 */
export function acceptsReading(typed: string, reading: string): boolean {
  const t = typed.trim();
  if (!t) return false;
  const kana = kanaOf(reading);
  if (kana && KANA.test(t)) return normKana(t) === normKana(kana);
  return normRomaji(t) === normRomaji(romajiOf(reading));
}
