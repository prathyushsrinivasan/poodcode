// Question-level analytics (TS_MASTERY_ROADMAP X-38): how often each quiz
// question has been answered right and wrong on this device. A question you
// always get right may be too easy; one you keep missing is either a real gap
// or an ambiguous question — both worth a look.

export type QuestionStat = { right: number; wrong: number };

const KEY = "poodcode:quiz-stats";

export function quizStats(): Record<string, QuestionStat> {
  try {
    const v: unknown = JSON.parse(localStorage.getItem(KEY) || "{}");
    if (typeof v !== "object" || v === null) return {};
    const out: Record<string, QuestionStat> = {};
    for (const [q, s] of Object.entries(v as Record<string, unknown>)) {
      const st = s as Partial<QuestionStat>;
      if (typeof st?.right === "number" && typeof st?.wrong === "number") out[q] = { right: st.right, wrong: st.wrong };
    }
    return out;
  } catch {
    return {};
  }
}

/** Record one marked sitting. */
export function recordSitting(outcomes: { question: string; right: boolean }[]): void {
  try {
    const all = quizStats();
    for (const o of outcomes) {
      const s = all[o.question] ?? { right: 0, wrong: 0 };
      if (o.right) s.right++;
      else s.wrong++;
      all[o.question] = s;
    }
    localStorage.setItem(KEY, JSON.stringify(all));
  } catch {
    /* private mode */
  }
}

/** Questions missed most (2+ attempts, under 40% right) and questions never
 * missed (3+ attempts). */
export function flaggedQuestions(stats: Record<string, QuestionStat>) {
  const rows = Object.entries(stats).map(([question, s]) => ({
    question,
    ...s,
    attempts: s.right + s.wrong,
    rate: s.right / Math.max(1, s.right + s.wrong),
  }));
  return {
    missed: rows.filter((r) => r.attempts >= 2 && r.rate < 0.4).sort((a, b) => a.rate - b.rate || b.attempts - a.attempts),
    tooEasy: rows.filter((r) => r.attempts >= 3 && r.wrong === 0).sort((a, b) => b.attempts - a.attempts),
  };
}
