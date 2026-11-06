import { STUDY_LESSONS, STUDY_QUESTION_MAP, STUDY_QUESTIONS, type StudyQuestion } from "../data/n2Study";
import { KANJI_PROGRESS_KEY, KANJI_WORDS } from "../data/kanjiWords";
import { AFFIX_PROGRESS_KEY, AFFIX_QUESTIONS } from "../data/jlptAffixes";
import { N2_ASSEMBLY_LESSONS, N2_ASSEMBLY_PROGRESS_KEY, N2_ASSEMBLY_QUESTIONS } from "../data/jlptN2SentenceOrder";
import { N2_LESSONS, N2_QUESTIONS } from "../data/jlptN2";
import { READING_PASSAGES } from "../data/dokkai";
import { latestReadingResult, parseReadingProgress, READING_PROGRESS_KEY } from "./dokkai";
import { plainReading } from "./dokkaiText";
import { parseKanjiProgress } from "./kanjiWords";
import { N2_PROGRESS_KEY, parseN2Progress } from "./jlptN2";
import { answerComplete, beginQuestions, parseStudy, questionSection, selectRound, startSession, STUDY_KEY, type StudySession, type StudyState } from "./n2Study";
import { seededRandom, shuffleWith } from "./quizShuffle";
import { validJlptSessionField } from "./jlptSessionRecovery";

export interface JlptItem { id: string; source: "Guided" | "Word Builder" | "Affixes" | "Sentence Order" | "Reading" | "Patterns" | "Saved word"; title: string; search: string; href: string; concept: string; vocabulary?: boolean; alias?: string }
const root = "/japanese/n2";
export const JLPT_CATALOG: JlptItem[] = [
  ...STUDY_QUESTIONS.map((q): JlptItem => ({ id: q.id, source: "Guided", title: q.kind === "typed" ? q.word : q.kind === "assembly" ? q.before + " … " + q.after : q.prompt,
    search: [q.prompt, q.translation, q.explanation, ...q.tags, ...(q.texts?.map((t) => t.text) ?? []), q.kind === "typed" ? q.answers.join(" ") + q.meaning : q.kind === "choice" ? q.choices.map((c) => c.text).join(" ") : q.fragments.join(" ")].join(" "),
    href: `${root}/lesson/${q.lessonId}`, concept: q.lessonId, vocabulary: ["kanji", "vocabulary"].includes(questionSection(q)) })),
  ...KANJI_WORDS.map((w): JlptItem => ({ id: `kanji:${w.id}`, source: "Word Builder", title: w.written, search: `${w.readings.join(" ")} ${w.meanings.join(" ")} ${w.cue} ${w.aliases.join(" ")}`, href: `${root}/kanji/word/${w.id}`, concept: "Word Builder", vocabulary: true })),
  ...AFFIX_QUESTIONS.map((q): JlptItem => ({ id: `affix:${q.id}`, source: "Affixes", title: q.word, search: `${q.reading} ${q.sentence} ${q.translation} ${q.explanation}`, href: `${root}/affixes/${q.lessonId}?q=${encodeURIComponent(q.word)}`, concept: `Affix · ${q.answer}`, vocabulary: true })),
  ...N2_ASSEMBLY_LESSONS.flatMap((l) => l.questions.map((q): JlptItem => ({ id: `order:${q.id}`, source: "Sentence Order", title: q.before + " … " + q.after, search: `${q.choices.join(" ")} ${q.translation} ${l.title}`, href: `${root}/sentence-order/${l.id}?question=${q.id}`, concept: l.title, alias: `assembly-${q.id}` }))),
  ...READING_PASSAGES.flatMap((p) => p.questions.map((q): JlptItem => ({ id: `reading:${q.id}`, source: "Reading", title: `${p.title} · ${plainReading(q.prompt)}`, search: `${p.topic} ${p.skill} ${p.texts.map((t) => plainReading(t.text) + " " + t.translation).join(" ")}`, href: `${root}/reading/${p.kind}/${p.id}`, concept: `Reading · ${p.skill}`, alias: STUDY_QUESTION_MAP.has(`study-${q.id}`) ? `study-${q.id}` : undefined }))),
  ...N2_QUESTIONS.map((q): JlptItem => ({ id: `pattern:${q.id}`, source: "Patterns", title: q.sentence, search: `${q.answer} ${q.translation} ${q.explanation}`, href: `${root}/patterns/${N2_LESSONS.find((l) => l.questions.some((item) => item.id === q.id))!.id}?question=${q.id}`, concept: "Vocabulary patterns", vocabulary: true })),
];
export const JLPT_ITEM_MAP = new Map(JLPT_CATALOG.map((i) => [i.id, i]));
export interface ReviewItem extends JlptItem { attempted: boolean; mistakes: number; due: boolean; saved: boolean; slow: boolean; confident: boolean; reason: string; note: string; nativePending?: boolean }
export function reviewInventory(state: StudyState, settings: Record<string, string>, now = Date.now()): ReviewItem[] {
  const kanji = parseKanjiProgress(settings[KANJI_PROGRESS_KEY]);
  const affix = parseN2Progress(settings[AFFIX_PROGRESS_KEY], AFFIX_QUESTIONS);
  const order = parseN2Progress(settings[N2_ASSEMBLY_PROGRESS_KEY], N2_ASSEMBLY_QUESTIONS);
  const patterns = parseN2Progress(settings[N2_PROGRESS_KEY]);
  const reading = parseReadingProgress(settings[READING_PROGRESS_KEY]);
  const items = JLPT_CATALOG.map((item): ReviewItem => {
    const q = state.reviews[item.id];
    const native = item.source === "Word Builder" ? Object.values(kanji.words[item.id.slice(6)] ?? {})
      : item.source === "Affixes" ? [affix[item.id.slice(6)]] : item.source === "Sentence Order" ? [order[item.id.slice(6)]]
        : item.source === "Reading" ? [latestReadingResult(reading.results[item.id.slice(8)])] : item.source === "Patterns" ? [patterns[item.id.slice(8)]] : [];
    const rows = native.filter((r) => !!r);
    const missed = q ? !q.lastCorrect || q.lastAssisted : rows.some((r) => !r.lastCorrect);
    const attempts = q ? q.attempts - q.correct : 0;
    const note = state.notes[item.id];
    const nativeSaved = item.source === "Reading" && reading.bookmarks.includes(READING_PASSAGES.find((p) => p.questions.some((q) => `reading:${q.id}` === item.id))!.id);
    return { ...item, attempted: !!q || rows.length > 0, mistakes: missed ? Math.max(1, attempts, ...rows.map((r) => r.attempts - r.correct)) : 0,
      due: q ? q.due <= now : missed, saved: state.bookmarks.includes(item.id) || nativeSaved,
      slow: q?.lastSlow ?? false, confident: q?.lastConfidentWrong ?? false, reason: note?.reason ?? "", note: note?.text ?? "" };
  });
  // A guided copy and its original are one exercise in the aggregate queue.
  // Legacy schedules stay in their own stores; no history is migrated or summed.
  const merged = items.filter((i) => !i.alias).map((i) => {
    const originals = items.filter((other) => other.alias === i.id);
    return originals.reduce((out, native) => ({ ...out, attempted: out.attempted || native.attempted,
      due: out.due || native.due, mistakes: Math.max(out.mistakes, native.mistakes), nativePending: native.due || out.nativePending, href: native.due ? native.href : out.href,
      saved: out.saved || native.saved, reason: out.reason || native.reason, note: out.note || native.note }), i);
  });
  return [...merged, ...Object.entries(reading.words).map(([key, w]): ReviewItem => ({ id: `word:${key}`, source: "Saved word", title: w.text, search: `${w.reading} ${w.meaning}`, href: `${root}/reading/vocabulary`, concept: "Saved reading words", vocabulary: true, attempted: w.reviews > 0, mistakes: w.reviews && !w.interval ? 1 : 0, due: w.due <= now, saved: true, slow: false, confident: false, reason: state.notes[`word:${key}`]?.reason ?? "", note: state.notes[`word:${key}`]?.text ?? "" }))];
}
export type WorkspaceFilter = "due" | "saved" | "mistakes" | "reason" | "confident" | "slow" | "trouble" | "all";
export function filterReview(items: ReviewItem[], filter: WorkspaceFilter, reason = "", query = "") {
  const search = query.trim().normalize("NFKC").toLowerCase();
  return items.filter((i) => (!search || `${i.title} ${i.search} ${i.note} ${i.concept}`.normalize("NFKC").toLowerCase().includes(search)) &&
    (filter === "all" || filter === "due" && i.due || filter === "saved" && i.saved || filter === "mistakes" && (i.mistakes > 0 || !!i.note || !!i.reason) || filter === "reason" && !!i.reason && (!reason || i.reason === reason) || filter === "confident" && i.confident || filter === "slow" && i.slow || filter === "trouble" && i.mistakes >= 3));
}
export function conceptProgress(state: StudyState) {
  return STUDY_LESSONS.map((l) => {
    const questions = STUDY_QUESTIONS.filter((q) => q.lessonId === l.id);
    const reviews = questions.flatMap((q) => state.reviews[q.id] ? [state.reviews[q.id]] : []);
    return { id: l.id, title: l.format, total: questions.length, seen: reviews.length, retained: reviews.filter((r) => r.stage >= 3).length,
      correct: reviews.reduce((n, r) => n + r.correct, 0), attempts: reviews.reduce((n, r) => n + r.attempts, 0) };
  }).filter((c) => c.total > 0);
}
export function newExamples(state: StudyState, ids: string[], count: number) {
  const concepts = new Set(ids.map((id) => STUDY_QUESTION_MAP.get(id)?.lessonId));
  return selectRound(state, STUDY_QUESTIONS.filter((q) => concepts.has(q.lessonId) && !ids.includes(q.id) && !state.reviews[q.id]), count);
}
export type PracticePlan = "daily" | "diagnostic" | "weak" | "mini" | "written";
export interface MockConfig { vocabulary: number; grammar: number; reading: number; minutes: number; fresh: boolean }
const category = (q: StudyQuestion) => { const s = questionSection(q); return s === "kanji" || s === "vocabulary" ? "vocabulary" : s === "reading" ? "reading" : "grammar"; };
export function planPractice(state: StudyState, kind: PracticePlan, config: MockConfig, seen: Set<string> = new Set(), seed = Date.now()): string[] {
  const shuffled = shuffleWith(STUDY_QUESTIONS, seededRandom(seed));
  if (kind === "mini" || kind === "written") {
    const pool = shuffled.filter((q) => q.kind !== "typed" && (!config.fresh || !state.reviews[q.id] && !seen.has(q.id)));
    return (["vocabulary", "grammar", "reading"] as const).flatMap((section) => pool.filter((q) => category(q) === section).slice(0, config[section]).map((q) => q.id));
  }
  if (kind === "diagnostic") {
    // Two independently attempted examples per section, with format diversity.
    return ["kanji", "vocabulary", "grammar", "assembly", "text", "reading"].flatMap((s) => selectRound(state, shuffled.filter((q) => questionSection(q) === s), 2));
  }
  if (kind === "weak") {
    const weak = conceptProgress(state).filter((c) => c.attempts > 0 && c.correct / c.attempts < 0.8).map((c) => c.id);
    return selectRound(state, shuffled.filter((q) => weak.includes(q.lessonId)), state.preferences.roundSize);
  }
  return selectRound(state, shuffled, state.preferences.roundSize);
}
export function startPlannedPractice(state: StudyState, ids: string[], kind: PracticePlan, minutes: number, now = Date.now()): StudyState {
  if (state.session && state.session.phase !== "summary") return state;
  const mock = kind === "mini" || kind === "written";
  if (mock && (!Number.isInteger(minutes) || minutes < 1 || minutes > 240)) return state;
  const titles: Record<PracticePlan, string> = { daily: "Mixed daily practice", diagnostic: "Short diagnostic", weak: "Weak-area round", mini: "Mini written mock", written: "N2 written practice mock" };
  const next = beginQuestions(startSession(state, ids, mock ? "timed" : "learn", titles[kind], now));
  if (!mock || next === state || !next.session || next.session === state.session) return next;
  return { ...next, session: { ...next.session, deadline: now + minutes * 60_000, mock: { kind, minutes }, flags: [] } };
}
export function toggleFlag(state: StudyState, id: string): StudyState {
  const s = state.session;
  if (!s || s.mode !== "timed" || s.phase !== "question" || !s.questionIds.includes(id)) return state;
  const flags = s.flags ?? [];
  return { ...state, session: { ...s, flags: flags.includes(id) ? flags.filter((q) => q !== id) : [...flags, id] } };
}
export function resultsBreakdown(s: StudySession) {
  return ["vocabulary", "grammar", "reading"].map((section) => {
    const ids = s.questionIds.filter((id) => category(STUDY_QUESTION_MAP.get(id)!) === section);
    const results = ids.flatMap((id) => s.results[id] ? [s.results[id]] : []);
    return { section, total: ids.length, answered: results.filter((r) => answerComplete(STUDY_QUESTION_MAP.get(r.questionId)!, r.answer)).length, correct: results.filter((r) => r.correct && !r.assisted).length,
      slow: results.filter((r) => r.elapsedMs > STUDY_QUESTION_MAP.get(r.questionId)!.targetSeconds * 1000).length,
      confidentWrong: results.filter((r) => !r.correct && r.confidence === "sure").length,
      seconds: Math.round(results.reduce((n, r) => n + r.elapsedMs, 0) / 1000), target: ids.reduce((n, id) => n + STUDY_QUESTION_MAP.get(id)!.targetSeconds, 0) };
  }).filter((r) => r.total);
}
export const JLPT_BACKUP_KEYS = [STUDY_KEY, KANJI_PROGRESS_KEY, AFFIX_PROGRESS_KEY, N2_ASSEMBLY_PROGRESS_KEY, READING_PROGRESS_KEY, N2_PROGRESS_KEY];
export interface JlptBackup { format: "poodcode-jlpt"; version: 1; exportedAt: string; settings: Record<string, string>; recovery: Record<string, string> }
export function parseJlptBackup(raw: string): JlptBackup {
  if (raw.length > 25_000_000) throw new Error("Backup exceeds 25 MB.");
  const p = JSON.parse(raw) as JlptBackup;
  if (!p || p.format !== "poodcode-jlpt" || p.version !== 1 || !p.settings || typeof p.settings !== "object" || Array.isArray(p.settings) || !p.recovery || typeof p.recovery !== "object" || Array.isArray(p.recovery)) throw new Error("Choose a version 1 JLPT backup.");
  for (const [key, value] of Object.entries(p.settings)) {
    if (!JLPT_BACKUP_KEYS.includes(key) || typeof value !== "string") throw new Error("Unexpected backup setting.");
    if (key === STUDY_KEY) parseStudy(value);
    else {
      const data = JSON.parse(value);
      if (!data || typeof data !== "object" || Array.isArray(data)) throw new Error("Invalid course progress.");
      // Parsers intentionally tolerate old rows when loading the app. An import
      // must be lossless: reject malformed or unknown records before any write.
      const normalized = key === KANJI_PROGRESS_KEY ? parseKanjiProgress(value) : key === READING_PROGRESS_KEY ? parseReadingProgress(value) : parseN2Progress(value, key === AFFIX_PROGRESS_KEY ? AFFIX_QUESTIONS : key === N2_ASSEMBLY_PROGRESS_KEY ? N2_ASSEMBLY_QUESTIONS : N2_QUESTIONS);
      if (stableJson(data) !== stableJson(normalized)) throw new Error(`Invalid or unavailable records in ${key}. Nothing has been imported.`);
    }
  }
  for (const [key, value] of Object.entries(p.recovery)) if (typeof value !== "string" || value.length > 2_000_000 || !validJlptSessionField(key, JSON.parse(value))) throw new Error("Invalid session recovery record.");
  if (!p.settings[STUDY_KEY]) throw new Error("The backup has no JLPT study snapshot.");
  return p;
}
function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${JSON.stringify(k)}:${stableJson(v)}`).join(",")}}`;
  return JSON.stringify(value);
}
export const COURSE_LINKS = [{ label: "Word Builder", href: `${root}/kanji` }, { label: "Full Sentence Order course", href: `${root}/sentence-order` }, { label: "Affix library", href: `${root}/affixes` }];
