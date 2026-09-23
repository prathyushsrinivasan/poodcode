// The TypeScript error glossary: src/data/ts_errors.json, generated and
// verified by tools/gen_ts_errors.py (every "bad" program really produces its
// code; every "good" one type-checks clean and runs).
//
// Pure helpers only — the page and the compile-error links decide nothing
// themselves, so this is what the tests cover.

import data from "../data/ts_errors.json";

export interface TsErrorEntry {
  code: number;
  /** The compiler's message, with the specifics replaced by placeholders. */
  title: string;
  /** One sentence: what the error means. */
  meaning: string;
  /** The usual cause and the usual fix, in prose. */
  cause: string;
  /** A minimal program that produces this code. */
  bad: string;
  /** The same program, fixed. */
  good: string;
  /** The TypeScript Mastery week that teaches the idea behind it. */
  week: number;
  /** The judge preset the example is checked at ("strict" / "strict+indexed"). */
  preset: string;
}

export const TS_ERRORS: TsErrorEntry[] = data as TsErrorEntry[];

const BY_CODE = new Map(TS_ERRORS.map((e) => [e.code, e]));

/** The glossary entry for a code, if there is one. */
export function errorEntry(code: number): TsErrorEntry | undefined {
  return BY_CODE.get(code);
}

/** Every distinct `TSnnnn` code mentioned in compiler output, in order of first
 * appearance. tsc prints `error TS2322:`; the judge's relabelled harness
 * messages keep the same form, so one pattern finds both. */
export function codesIn(text: string): number[] {
  const seen = new Set<number>();
  for (const m of text.matchAll(/\bTS(\d{4,5})\b/g)) seen.add(Number(m[1]));
  return [...seen];
}

/** The glossary entries for the codes in some compiler output — the ones the
 * learner can click through to. Codes the glossary doesn't cover are skipped. */
export function entriesIn(text: string): TsErrorEntry[] {
  return codesIn(text)
    .map((c) => BY_CODE.get(c))
    .filter((e): e is TsErrorEntry => e !== undefined);
}

/** Search by code ("2322", "TS2322") or by words in the title, meaning or cause.
 * Every word must match somewhere; an empty query returns everything. */
export function searchErrors(query: string, entries: TsErrorEntry[] = TS_ERRORS): TsErrorEntry[] {
  const q = query.trim().toLowerCase();
  if (!q) return entries;
  const code = /^(?:ts)?(\d+)$/.exec(q);
  if (code) return entries.filter((e) => String(e.code).startsWith(code[1]));
  const words = q.split(/\s+/);
  return entries.filter((e) => {
    const hay = `${e.title} ${e.meaning} ${e.cause}`.toLowerCase();
    return words.every((w) => hay.includes(w));
  });
}
