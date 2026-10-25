import { STUDY_LESSONS, STUDY_QUESTION_MAP, STUDY_QUESTIONS, STUDY_SECTIONS, type StudyQuestion, type StudySection } from "../data/n2Study";

export const STUDY_KEY = "jlpt-n2-study-v1";
export const DAY = 86_400_000;
export type Confidence = "guess" | "unsure" | "sure";
export type StudyMode = "learn" | "timed";
export type ReviewFilter = "due" | "mistakes" | "slow" | "confident" | "saved";
export const MISTAKE_REASONS = ["Unknown word", "Grammar connection", "Misread the question", "Unsupported inference", "Time pressure", "Careless slip"] as const;
export interface StudyDraft { answer: string; confidence: Confidence; assisted: boolean; elapsedMs: number }
export interface StudyAttempt extends StudyDraft {
  id: string; questionId: string; at: number; correct: boolean; mode: StudyMode; revealed: boolean;
}
export interface StudyReview {
  attempts: number; correct: number; stage: number; due: number; lastAt: number;
  lastCorrect: boolean; lastAssisted: boolean; lastSlow: boolean; lastConfidentWrong: boolean;
}
export interface StudySession {
  id: string; title: string; mode: StudyMode; questionIds: string[]; position: number;
  startedAt: number; questionStartedAt: number; deadline: number | null; paused: boolean;
  phase: "lesson" | "question" | "summary";
  drafts: Record<string, StudyDraft>; results: Record<string, StudyAttempt>;
  finishedAt?: number; expired?: boolean;
}
export interface StudyState {
  version: 1; revision: number;
  preferences: { examDate: string; dailyMinutes: number; roundSize: number };
  reviews: Record<string, StudyReview>;
  attempts: StudyAttempt[];
  bookmarks: string[];
  notes: Record<string, { text: string; reason: string }>;
  learned: string[];
  session: StudySession | null;
}
export function emptyStudy(): StudyState {
  return { version: 1, revision: 0, preferences: { examDate: "2026-12-06", dailyMinutes: 60, roundSize: 5 }, reviews: {}, attempts: [], bookmarks: [], notes: {}, learned: [], session: null };
}
function isObject(value: unknown): value is Record<string, unknown> { return !!value && typeof value === "object" && !Array.isArray(value); }
function integer(value: unknown, min = 0): value is number { return typeof value === "number" && Number.isSafeInteger(value) && value >= min; }
function timestamp(value: unknown): value is number { return integer(value) && value <= 8.64e15; }
function confidence(value: unknown): value is Confidence { return value === "guess" || value === "unsure" || value === "sure"; }
function draft(value: unknown): value is StudyDraft {
  return isObject(value) && typeof value.answer === "string" && value.answer.length <= 10_000 && confidence(value.confidence) && typeof value.assisted === "boolean" && integer(value.elapsedMs);
}
function attempt(value: unknown): value is StudyAttempt {
  return draft(value) && isObject(value) && typeof value.id === "string" && typeof value.questionId === "string" && timestamp(value.at) && typeof value.correct === "boolean" && typeof value.revealed === "boolean" && (value.mode === "learn" || value.mode === "timed");
}
export function validExamDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T12:00:00`);
  return Number.isFinite(date.getTime()) && localDay(date.getTime()) === value;
}
/** Reject damaged/future snapshots visibly instead of overwriting them with empty progress. */
export function parseStudy(raw?: string | null): StudyState {
  if (!raw) return emptyStudy();
  const fail = (): never => { throw new Error("This study snapshot cannot be read safely. Your saved data has not been changed."); };
  let p: unknown;
  try { p = JSON.parse(raw); } catch { return fail(); }
  if (!isObject(p) || p.version !== 1 || !integer(p.revision) || !isObject(p.preferences) || !isObject(p.reviews) || !isObject(p.notes) || !Array.isArray(p.attempts) || !Array.isArray(p.bookmarks) || !Array.isArray(p.learned)) return fail();
  const pref = p.preferences;
  if (typeof pref.examDate !== "string" || (pref.examDate !== "" && !validExamDate(pref.examDate)) || !integer(pref.dailyMinutes, 10) || pref.dailyMinutes > 240 || !integer(pref.roundSize, 1) || pref.roundSize > 20) return fail();
  const out = emptyStudy();
  out.revision = p.revision;
  out.preferences = { examDate: pref.examDate, dailyMinutes: pref.dailyMinutes, roundSize: pref.roundSize };
  for (const [id, r] of Object.entries(p.reviews)) {
    if (!isObject(r) || !integer(r.attempts, 1) || !integer(r.correct) || r.correct > r.attempts || !integer(r.stage) || r.stage > 3 || !timestamp(r.due) || !timestamp(r.lastAt) || ![r.lastCorrect, r.lastAssisted, r.lastSlow, r.lastConfidentWrong].every((v) => typeof v === "boolean")) return fail();
    out.reviews[id] = r as unknown as StudyReview;
  }
  if (!p.attempts.every(attempt) || !p.bookmarks.every((id) => typeof id === "string") || !p.learned.every((id) => typeof id === "string")) return fail();
  out.attempts = (p.attempts as StudyAttempt[]).slice(-3000);
  out.bookmarks = [...new Set(p.bookmarks as string[])]; out.learned = [...new Set(p.learned as string[])];
  for (const [id, n] of Object.entries(p.notes)) {
    if (!isObject(n) || typeof n.text !== "string" || n.text.length > 4000 || typeof n.reason !== "string") return fail();
    out.notes[id] = { text: n.text, reason: n.reason };
  }
  if (p.session !== null) {
    const s = p.session;
    if (!isObject(s) || typeof s.id !== "string" || typeof s.title !== "string" || !["learn", "timed"].includes(String(s.mode)) || !Array.isArray(s.questionIds) || !s.questionIds.length || !s.questionIds.every((id) => typeof id === "string") || new Set(s.questionIds).size !== s.questionIds.length || !integer(s.position) || s.position >= s.questionIds.length || !timestamp(s.startedAt) || !timestamp(s.questionStartedAt) || !(s.deadline === null || timestamp(s.deadline)) || typeof s.paused !== "boolean" || !["lesson", "question", "summary"].includes(String(s.phase)) || !isObject(s.drafts) || !Object.values(s.drafts).every(draft) || !isObject(s.results) || !Object.values(s.results).every(attempt) || (s.finishedAt !== undefined && !timestamp(s.finishedAt)) || (s.expired !== undefined && typeof s.expired !== "boolean")) return fail();
    const ids = s.questionIds as string[];
    for (const [id, r] of Object.entries(s.results as Record<string, StudyAttempt>)) if (!ids.includes(id) || r.questionId !== id || r.id !== `${s.id}:${id}`) return fail();
    if (s.mode === "timed" && (s.deadline === null || s.paused || s.phase === "lesson")) return fail();
    if (s.phase === "summary" && (Object.keys(s.results).length !== ids.length || s.finishedAt === undefined)) return fail();
    // Removed content must not strand an in-progress round. Keep its history.
    out.session = ids.every((id) => STUDY_QUESTION_MAP.has(id)) ? s as unknown as StudySession : null;
  }
  return out;
}
export function localDay(at = Date.now()): string {
  const d = new Date(at);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
export function daysToExam(date: string, now = Date.now()): number | null {
  if (!validExamDate(date)) return null;
  const [y, m, d] = date.split("-").map(Number);
  const today = new Date(now);
  return Math.round((Date.UTC(y, m - 1, d) - Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())) / DAY);
}
export function questionSection(q: StudyQuestion): StudySection { return STUDY_LESSONS.find((l) => l.id === q.lessonId)!.section; }
export function answerCorrect(q: StudyQuestion, answer: string): boolean {
  if (q.kind === "choice") return answer === String(q.answer);
  if (q.kind === "assembly") return [q.order, ...(q.acceptedOrders ?? [])].some((order) => answer === order.join(","));
  const normalized = answer.normalize("NFKC").replace(/\s/gu, "");
  return !!normalized && q.answers.includes(normalized);
}
export function displayAnswer(q: StudyQuestion, answer?: string): string {
  if (answer === undefined || answer === "") return "Unanswered";
  if (q.kind === "choice") return q.choices[Number(answer)]?.text ?? "Unanswered";
  if (q.kind === "assembly") return answer.split(",").map((n) => q.fragments[Number(n)] ?? "?").join(" → ");
  return answer;
}
export function targetAnswer(q: StudyQuestion): string {
  return q.kind === "choice" ? q.choices[q.answer].text : q.kind === "typed" ? q.answers[0] : q.before + q.order.map((n) => q.fragments[n]).join("") + q.after;
}
export function reviewQuestions(state: StudyState, filter: ReviewFilter, now = Date.now()): StudyQuestion[] {
  return STUDY_QUESTIONS.filter((q) => {
    const r = state.reviews[q.id];
    if (filter === "saved") return state.bookmarks.includes(q.id);
    if (!r) return false;
    return filter === "due" ? r.due <= now : filter === "mistakes" ? !r.lastCorrect || r.lastAssisted : filter === "slow" ? r.lastSlow : r.lastConfidentWrong;
  }).sort((a, b) => (state.reviews[a.id]?.due ?? 0) - (state.reviews[b.id]?.due ?? 0));
}
/** Interleave sections, then prioritize due, mistakes, unseen and least-recently seen. */
export function selectRound(state: StudyState, pool: StudyQuestion[], count: number, now = Date.now()): string[] {
  const priority = (q: StudyQuestion) => {
    const r = state.reviews[q.id];
    return !r ? 2 : r.due <= now ? 0 : !r.lastCorrect || r.lastAssisted ? 1 : 3;
  };
  const sorted = [...pool].sort((a, b) => priority(a) - priority(b) || (state.reviews[a.id]?.lastAt ?? 0) - (state.reviews[b.id]?.lastAt ?? 0));
  const result: StudyQuestion[] = [];
  const sectionCounts = new Map<StudySection, number>();
  const lessonCounts = new Map<string, number>();
  while (sorted.length && result.length < count) {
    const best = priority(sorted[0]);
    // Among equally urgent items, prefer sections and formats not yet used.
    // Merely avoiding the previous section would alternate the first two forever.
    let index = 0;
    for (let i = 1; i < sorted.length && priority(sorted[i]) === best; i++) {
      const candidate = sorted[i]; const current = sorted[index];
      const sectionDifference = (sectionCounts.get(questionSection(candidate)) ?? 0) - (sectionCounts.get(questionSection(current)) ?? 0);
      const lessonDifference = (lessonCounts.get(candidate.lessonId) ?? 0) - (lessonCounts.get(current.lessonId) ?? 0);
      if (sectionDifference < 0 || (sectionDifference === 0 && lessonDifference < 0)) index = i;
    }
    const selected = sorted.splice(index, 1)[0];
    result.push(selected);
    sectionCounts.set(questionSection(selected), (sectionCounts.get(questionSection(selected)) ?? 0) + 1);
    lessonCounts.set(selected.lessonId, (lessonCounts.get(selected.lessonId) ?? 0) + 1);
  }
  return result.map((q) => q.id);
}
export function startSession(state: StudyState, questionIds: string[], mode: StudyMode, title: string, now = Date.now(), id: string = crypto.randomUUID()): StudyState {
  const ids = [...new Set(questionIds)].filter((q) => STUDY_QUESTION_MAP.has(q)).slice(0, 30);
  if (!ids.length || (state.session && state.session.phase !== "summary")) return state;
  const budget = ids.reduce((sum, q) => sum + STUDY_QUESTION_MAP.get(q)!.targetSeconds, 0);
  return { ...state, session: { id, title, mode, questionIds: ids, position: 0, startedAt: now, questionStartedAt: now,
    deadline: mode === "timed" ? now + budget * 1000 : null,
    phase: mode === "timed" || state.learned.includes(STUDY_QUESTION_MAP.get(ids[0])!.lessonId) ? "question" : "lesson",
    paused: false, drafts: {}, results: {} } };
}
export const blankDraft = (): StudyDraft => ({ answer: "", confidence: "unsure", assisted: false, elapsedMs: 0 });
export function settleSession(s: StudySession, now: number): StudySession {
  if (s.paused || s.phase !== "question") return s;
  const id = s.questionIds[s.position];
  if (s.results[id]) return s;
  const draft = s.drafts[id] ?? blankDraft();
  const end = s.deadline === null ? now : Math.min(now, s.deadline);
  return { ...s, questionStartedAt: now, drafts: { ...s.drafts, [id]: { ...draft, elapsedMs: draft.elapsedMs + Math.max(0, end - s.questionStartedAt) } } };
}
export function updateDraft(state: StudyState, patch: Partial<StudyDraft>, now = Date.now()): StudyState {
  const s = state.session;
  if (!s || s.phase !== "question" || s.paused || (s.deadline !== null && now >= s.deadline)) return state;
  const id = s.questionIds[s.position];
  if (s.results[id]) return state;
  const timed = settleSession(s, now);
  const old = timed.drafts[id] ?? blankDraft();
  return { ...state, session: { ...timed, drafts: { ...timed.drafts, [id]: { ...old, ...patch, assisted: old.assisted || !!patch.assisted } } } };
}
function applyAttempt(state: StudyState, event: StudyAttempt): StudyState {
  // Results and scheduler update together in one persisted snapshot.
  if (state.attempts.some((a) => a.id === event.id)) return state;
  const old = state.reviews[event.questionId];
  const successful = event.correct && !event.assisted && event.confidence !== "guess";
  const stage = successful ? !old ? 1 : event.at >= old.due ? Math.min(3, old.stage + 1) : old.stage : 0;
  const days = stage === 0 ? 1 : stage === 1 ? 1 : stage === 2 ? 3 : 7;
  const due = successful && old && event.at < old.due ? old.due : event.at + days * DAY;
  const target = STUDY_QUESTION_MAP.get(event.questionId)!.targetSeconds;
  const review: StudyReview = { attempts: (old?.attempts ?? 0) + 1, correct: (old?.correct ?? 0) + Number(event.correct && !event.assisted),
    stage, due, lastAt: event.at, lastCorrect: event.correct, lastAssisted: event.assisted,
    lastSlow: event.elapsedMs > target * 1000, lastConfidentWrong: !event.correct && event.confidence === "sure" };
  return { ...state, reviews: { ...state.reviews, [event.questionId]: review }, attempts: [...state.attempts, event].slice(-3000) };
}
function makeAttempt(s: StudySession, id: string, now: number, revealed = false): StudyAttempt {
  const d = s.drafts[id] ?? blankDraft();
  return { ...d, id: `${s.id}:${id}`, questionId: id, at: now, mode: s.mode, revealed,
    assisted: d.assisted || revealed, correct: !revealed && answerCorrect(STUDY_QUESTION_MAP.get(id)!, d.answer) };
}
export function checkAnswer(state: StudyState, now = Date.now(), revealed = false): StudyState {
  const s = state.session;
  if (!s || s.mode !== "learn" || s.phase !== "question" || s.paused) return state;
  const id = s.questionIds[s.position];
  if (s.results[id] || (!revealed && !s.drafts[id]?.answer)) return state;
  const timed = settleSession(s, now);
  const event = makeAttempt(timed, id, now, revealed);
  return { ...applyAttempt(state, event), session: { ...timed, results: { ...s.results, [id]: event } } };
}
export function finishSession(state: StudyState, now = Date.now()): StudyState {
  const s = state.session;
  if (!s || s.phase === "summary") return state;
  const timed = settleSession(s, now);
  let next = state;
  const results = { ...s.results };
  // Leaving a guided round early must not turn unseen material into mistakes.
  // Timed rounds deliberately include every unanswered question as missed.
  const ids = s.mode === "timed" ? s.questionIds : s.questionIds.filter((id) => results[id] || timed.drafts[id]?.answer);
  if (!ids.length) return { ...state, session: null };
  for (const id of ids) {
    if (results[id]) continue;
    const event = makeAttempt(timed, id, now);
    results[id] = event;
    next = applyAttempt(next, event);
  }
  return { ...next, session: { ...timed, questionIds: ids, position: Math.min(timed.position, ids.length - 1), results, phase: "summary", finishedAt: now, expired: s.deadline !== null && now >= s.deadline } };
}
export function moveQuestion(state: StudyState, position: number, now = Date.now()): StudyState {
  const s = state.session;
  if (!s || s.phase !== "question" || position < 0 || position >= s.questionIds.length) return state;
  if (s.mode === "timed" && s.deadline !== null && now >= s.deadline) return finishSession(state, now);
  if (s.mode === "learn" && !s.results[s.questionIds[s.position]]) return state;
  const nextId = s.questionIds[position];
  const previous = STUDY_QUESTION_MAP.get(s.questionIds[s.position])!;
  const next = STUDY_QUESTION_MAP.get(nextId)!;
  return { ...state, session: { ...settleSession(s, now), position, questionStartedAt: now,
    phase: s.mode === "learn" && previous.lessonId !== next.lessonId && !state.learned.includes(next.lessonId) ? "lesson" : "question" } };
}
export function beginQuestions(state: StudyState, now = Date.now()): StudyState {
  const s = state.session;
  if (!s || s.phase !== "lesson") return state;
  const lesson = STUDY_QUESTION_MAP.get(s.questionIds[s.position])!.lessonId;
  return { ...state, learned: [...new Set([...state.learned, lesson])], session: { ...s, phase: "question", questionStartedAt: now } };
}
export function pauseSession(state: StudyState, paused: boolean, now = Date.now()): StudyState {
  const s = state.session;
  if (!s || s.mode === "timed" || s.phase === "summary" || s.paused === paused) return state;
  return { ...state, session: { ...settleSession(s, now), paused, questionStartedAt: now } };
}
export function sectionStats(state: StudyState, section: StudySection) {
  const questions = STUDY_QUESTIONS.filter((q) => questionSection(q) === section);
  const events = state.attempts.filter((a) => questions.some((q) => q.id === a.questionId));
  const independent = events.filter((a) => !a.assisted);
  return { total: questions.length, seen: questions.filter((q) => state.reviews[q.id]).length,
    retained: questions.filter((q) => (state.reviews[q.id]?.stage ?? 0) >= 3).length,
    attempts: independent.length, accuracy: independent.length ? Math.round(independent.filter((a) => a.correct).length / independent.length * 100) : null,
    averageSeconds: events.length ? Math.round(events.reduce((n, a) => n + a.elapsedMs, 0) / events.length / 1000) : 0,
    due: questions.filter((q) => state.reviews[q.id]?.due <= Date.now()).length };
}
export function dailyStats(state: StudyState, now = Date.now()) {
  const today = localDay(now);
  const events = state.attempts.filter((a) => localDay(a.at) === today);
  const unique = new Set(events.map((a) => a.questionId)).size;
  const seconds = Math.round(events.reduce((n, a) => n + a.elapsedMs, 0) / 1000);
  const days = new Set(state.attempts.map((a) => localDay(a.at)));
  const cursor = new Date(now);
  if (!days.has(today)) cursor.setDate(cursor.getDate() - 1);
  let streak = 0;
  while (days.has(localDay(cursor.getTime()))) { streak++; cursor.setDate(cursor.getDate() - 1); }
  return { unique, seconds, streak, correct: events.filter((a) => a.correct && !a.assisted).length, attempts: events.length };
}
export function weakestSection(state: StudyState): StudySection | null {
  const sampled = STUDY_SECTIONS.map((s) => ({ id: s.id, ...sectionStats(state, s.id) })).filter((s) => s.attempts >= 3);
  return sampled.sort((a, b) => (a.accuracy ?? 0) - (b.accuracy ?? 0))[0]?.id ?? null;
}
