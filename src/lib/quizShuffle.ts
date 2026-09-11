// Deterministic shuffling for multiple-choice questions.
//
// WHY THIS EXISTS. Content authors write the correct option first — it is the
// natural way to write a question, and the generators' `_pq(question, options,
// answer, …)` makes it easy — and every one of the Projects track's quiz
// questions, and every one of the Java course's, has `answer: 0`. Rendered in
// authored order, the right answer was always the top button, and a learner who
// noticed could score full marks without reading a word.
//
// Fixing it in the data would mean re-authoring ~850 questions and trusting
// every future author to randomise by hand. Fixing it at display time fixes all
// of them at once and cannot regress.
//
// WHY DETERMINISTIC. The order is seeded from the question's own text, so it is
// stable across re-renders and sessions: a question you are coming back to
// looks the way it did, and a screenshot of one matches what someone else sees.
// A different `salt` gives a different order — the review drill uses that so a
// question met again in a later round is not memorised by position.

/** Separates a salt from the question it salts, so ("a", "bc") and ("ab",
 * "c") cannot hash alike. Written as an escape: a raw NUL in the source makes
 * every tool treat the file as binary. */
const SEP = "\u0000";

/** FNV-1a, 32-bit. Small, fast and well-distributed enough to seed a shuffle. */
export function hashString(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/** mulberry32 — a tiny seeded PRNG returning floats in [0, 1). */
export function seededRandom(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** A Fisher-Yates shuffle of `items` driven by `rand`. Returns a new array. */
export function shuffleWith<T>(items: readonly T[], rand: () => number): T[] {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    const tmp = out[i]!;
    out[i] = out[j]!;
    out[j] = tmp;
  }
  return out;
}

/**
 * The order to display a question's options in, as indices into the authored
 * `options` array: `order[k]` is the authored index of the option shown k-th.
 *
 * Grading is untouched — the caller still compares the authored index of what
 * was picked against `answer`. Only where each option appears changes.
 */
export function optionOrder(question: string, optionCount: number, salt = ""): number[] {
  const indices = Array.from({ length: optionCount }, (_, i) => i);
  return shuffleWith(indices, seededRandom(hashString(salt + SEP + question)));
}
