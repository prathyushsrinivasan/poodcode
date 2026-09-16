/**
 * Speaking Japanese out loud, through the browser's own speech synthesis.
 *
 * No audio ships with the app and nothing is fetched: `speechSynthesis` uses
 * voices installed in the operating system, so this stays offline like the rest
 * of the app. The cost of that is that a Japanese voice may simply not be
 * installed — on a stock Windows or Linux box it often isn't — and there is
 * nothing the app can do about it but say so.
 *
 * The decision logic below is pure and takes plain objects, because the test
 * environment is node with no DOM. Everything that touches `window` is confined
 * to the three functions at the bottom, and none of it runs at import time.
 */

/** The parts of `SpeechSynthesisVoice` we actually read — so the pure helpers
 * can be called with plain objects in a test. */
export interface VoiceLike {
  lang: string;
  name: string;
  default?: boolean;
}

/** Is this voice Japanese? Matches "ja", "ja-JP" and the underscore spelling
 * some platforms report. */
export function isJapaneseVoice(v: VoiceLike): boolean {
  const lang = v.lang.toLowerCase().replace("_", "-");
  return lang === "ja" || lang.startsWith("ja-");
}

/**
 * The best Japanese voice in the list, or undefined if there is none.
 * An exact `ja-JP` wins over a bare `ja`, and the platform default wins among
 * equals — otherwise the first one offered.
 */
export function pickJapaneseVoice(voices: VoiceLike[]): VoiceLike | undefined {
  const ja = voices.filter(isJapaneseVoice);
  if (ja.length === 0) return undefined;
  const score = (v: VoiceLike) =>
    (v.lang.toLowerCase().replace("_", "-") === "ja-jp" ? 2 : 0) + (v.default ? 1 : 0);
  return ja.reduce((best, v) => (score(v) > score(best) ? v : best), ja[0]);
}

export function hasJapaneseVoice(voices: VoiceLike[]): boolean {
  return voices.some(isJapaneseVoice);
}

/* ------------------------------------------------- everything below is DOM */

/** Does this browser offer speech synthesis at all? */
export function speechSupported(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

/** The voices the browser currently knows about. Chrome and Edge populate this
 * list asynchronously and return [] on the first call — see `onVoicesChanged`. */
export function currentVoices(): SpeechSynthesisVoice[] {
  if (!speechSupported()) return [];
  try {
    return window.speechSynthesis.getVoices();
  } catch {
    return [];
  }
}

/** Subscribe to the list being (re)populated. Returns an unsubscribe function. */
export function onVoicesChanged(fn: () => void): () => void {
  if (!speechSupported()) return () => {};
  window.speechSynthesis.addEventListener("voiceschanged", fn);
  return () => window.speechSynthesis.removeEventListener("voiceschanged", fn);
}

/**
 * Say each string in turn, cancelling anything already queued so pressing the
 * button twice restarts rather than stacking up. Slightly under normal speed:
 * these are single words and one short sentence, and the point is to hear the
 * shape of them.
 */
export function speakJapanese(texts: string[], voice?: SpeechSynthesisVoice | null): void {
  if (!speechSupported()) return;
  try {
    window.speechSynthesis.cancel();
    for (const text of texts) {
      if (!text) continue;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "ja-JP";
      if (voice) utterance.voice = voice;
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  } catch {
    /* a browser that refuses to speak is not worth breaking the card over */
  }
}
