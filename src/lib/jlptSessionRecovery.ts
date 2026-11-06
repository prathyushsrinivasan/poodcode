import { AFFIX_QUESTIONS } from "../data/jlptAffixes";
import { N2_ASSEMBLY_QUESTIONS } from "../data/jlptN2SentenceOrder";
import { N2_QUESTIONS } from "../data/jlptN2";
import { KANJI_WORD_BY_ID } from "../data/kanjiWords";
import { READING_PASSAGES } from "../data/dokkai";

export const SESSION_PREFIX = "jlpt-session:";
const object = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);
const natural = (v: unknown) => typeof v === "number" && Number.isSafeInteger(v) && v >= 0;
function sorted(value: unknown): unknown {
  return Array.isArray(value) ? value.map(sorted) : object(value) ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => [k, sorted(v)])) : value;
}
/** Recovery must never supply altered exercise content, answer keys or IDs. */
export function validJlptSessionField(key: string, value: unknown): boolean {
  if (!key.startsWith(SESSION_PREFIX)) return false;
  const field = key.slice(key.lastIndexOf(":") + 1);
  const values = object(value) ? Object.values(value) : [];
  if (field === "round") {
    if (!Array.isArray(value) || value.length > 500) return false;
    const pool = key.includes("/affixes/") ? AFFIX_QUESTIONS : key.includes("/sentence-order/") ? N2_ASSEMBLY_QUESTIONS : key.includes("/patterns/") ? N2_QUESTIONS : key.includes("/reading/") ? READING_PASSAGES : [];
    return value.every((q) => object(q) && pool.some((original) => original.id === q.id && JSON.stringify(sorted(original)) === JSON.stringify(sorted(q))));
  }
  if (field === "ids") return Array.isArray(value) && value.every((id) => typeof id === "string" && KANJI_WORD_BY_ID.has(id)) && new Set(value).size === value.length;
  if (["position", "index", "correctCount", "remaining", "duration", "deadline"].includes(field)) return value === null && field === "deadline" || natural(value);
  if (field === "phase") return ["ready", "answer", "review", "finish"].includes(String(value));
  if (field === "stage") return value === "reading" || value === "meaning";
  if (["hint", "ruby", "expired", "reviewing", "flipped"].includes(field)) return typeof value === "boolean";
  if (field === "wordRound") return Array.isArray(value) && value.every((id) => typeof id === "string" && id.length <= 1000) && value.length <= 5000;
  if (["input", "seed"].includes(field)) return typeof value === "string" && value.length <= 10_000 || field === "seed" && natural(value);
  if (field === "answer") return value === null || typeof value === "string" && value.length <= 100 || natural(value) && Number(value) <= 4;
  if (field === "result") return value === null || ["correct", "incorrect", "revealed", "compare"].includes(String(value));
  if (["readingResult", "meaningResult"].includes(field)) return value === null || object(value) && typeof value.correct === "boolean" && typeof value.revealed === "boolean";
  if (["selected", "scratch"].includes(field)) return Array.isArray(value) && value.length <= 64 && value.every((n) => natural(n) && n <= 64) && new Set(value).size === value.length;
  if (field === "answers") return object(value) && values.every((v) => natural(v) && Number(v) <= 3);
  if (["checked", "aids", "revealed"].includes(field)) return object(value) && values.every((v) => typeof v === "boolean");
  if (field === "recordedModes") return object(value) && values.every((v) => ["independent", "assisted", "timed"].includes(String(v)));
  if (field === "skills") return object(value) && Object.entries(value).every(([id, skills]) => KANJI_WORD_BY_ID.has(id) && Array.isArray(skills) && skills.length > 0 && skills.length <= 2 && skills.every((s) => s === "reading" || s === "meaning"));
  if (field === "results") return Array.isArray(value) && value.every((v) => object(v) && typeof v.id === "string" && KANJI_WORD_BY_ID.has(v.id) && (v.reading === undefined || typeof v.reading === "boolean") && (v.meaning === undefined || typeof v.meaning === "boolean"));
  return false;
}
export interface RecoveredCourse { route: string; label: string }
export function recoveredCourses(storage: Pick<Storage, "getItem" | "key" | "length">): RecoveredCourse[] {
  const routes = new Set<string>();
  for (let i = 0; i < storage.length; i++) {
    const key = storage.key(i)!;
    if (!key.startsWith(SESSION_PREFIX) || !/:(round|ids|wordRound)$/.test(key)) continue;
    const route = key.slice(SESSION_PREFIX.length, key.lastIndexOf(":"));
    const prefix = `${SESSION_PREFIX}${route}:`;
    try {
      const round = JSON.parse(storage.getItem(key) ?? "[]");
      const position = JSON.parse(storage.getItem(`${prefix}position`) ?? storage.getItem(`${prefix}index`) ?? "0");
      const phase = JSON.parse(storage.getItem(`${prefix}phase`) ?? '"answer"');
      if (key.endsWith(":wordRound") && storage.getItem(`${prefix}reviewing`) !== "true") continue;
      if (Array.isArray(round) && position < round.length && phase !== "finish" && phase !== "review") routes.add(route);
    } catch { /* Invalid drafts remain available for inspection/export. */ }
  }
  return [...routes].map((route) => ({ route, label: route.includes("/kanji/") ? "Word Builder" : route.includes("/affixes/") ? "Affixes" : route.includes("/sentence-order/") ? "Sentence Order" : route.includes("/reading/") ? "Reading" : "Vocabulary patterns" }));
}
