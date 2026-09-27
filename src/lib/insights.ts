/**
 * Insights across every track (UI_ROADMAP I1).
 *
 * Statistics used to measure problems and nothing else, though most of what
 * the app now teaches is courses, units, modules and review decks. These
 * turn each track's own completion keys into one comparable row — done out of
 * total, in that track's own unit — and summarise the review decks' health.
 *
 * Everything here is derived from data the app already keeps; nothing is
 * estimated. Where something is not measured (reading time in a lesson), the
 * page says so rather than inventing it.
 */

import type {
  BackendTrack,
  CardReview,
  Concept,
  MasteryProgress,
  MasteryTrack,
  Problem,
  ProjectTrack,
  WeeklyCourse,
} from "../types";
import { isCleared, type HydratedCurriculum } from "./curriculum";

export interface TrackInsight {
  key: string;
  label: string;
  /** An IconName; typed loosely so this module stays free of UI imports. */
  icon: string;
  href: string;
  done: number;
  total: number;
  /** What one unit of progress is: "unit", "week", "module", "chapter". */
  unit: string;
  /** A second line: "3 cleared this month", "on the Todo API". */
  note?: string;
}

const pct = (done: number, total: number) => (total > 0 ? done / total : 0);

/** Share done, 0..1. */
export function share(t: Pick<TrackInsight, "done" | "total">): number {
  return pct(t.done, t.total);
}

export function curriculumInsight(c: HydratedCurriculum): TrackInsight {
  const core = c.stages.filter((s) => !s.optional).flatMap((s) => s.units);
  const cleared = core.filter((u) => isCleared(u.status) || u.skipped).length;
  return {
    key: "dsa",
    label: "DSA Curriculum",
    icon: "curriculum",
    href: "/library",
    done: cleared,
    total: core.length,
    unit: "unit",
    note: `${c.solved}/${c.total} of its problems solved`,
  };
}

/** A structured course: weeks (or modules) marked done under `${prefix}:wN`. */
export function courseInsight(
  course: WeeklyCourse,
  prefix: string,
  done: ReadonlySet<string>,
  opts: { key: string; label: string; icon: string; href: string }
): TrackInsight {
  const authored = course.weeks.filter((w) => w.authored);
  const unit = (course.unit_label || "Week").toLowerCase();
  return {
    ...opts,
    done: authored.filter((w) => done.has(`${prefix}:w${w.number}`)).length,
    total: authored.length,
    unit,
    note: authored.length < course.weeks.length ? `${course.weeks.length - authored.length} more ${unit}s planned` : undefined,
  };
}

export function backendInsight(track: BackendTrack, done: ReadonlySet<string>): TrackInsight {
  const authored = track.projects.filter((p) => p.authored);
  return {
    key: "backend",
    label: "Backend Lab",
    icon: "backend",
    href: "/backend",
    done: authored.filter((p) => done.has(`backend:${p.key}`)).length,
    total: authored.length,
    unit: "project",
  };
}

/** One row per project in the Projects track, counting written modules. */
export function projectInsights(track: ProjectTrack, done: ReadonlySet<string>): TrackInsight[] {
  return track.projects
    .filter((p) => p.authored)
    .map((p) => {
      const mods = p.modules.filter((m) => m.authored);
      return {
        key: `project:${p.key}`,
        label: p.title,
        icon: "projects",
        href: `/projects/${p.key}`,
        done: mods.filter((m) => done.has(`project:${p.key}:${m.key}`)).length,
        total: mods.length,
        unit: "module",
        note: "Projects track",
      };
    });
}

/** Learn chapters marked done, per language track. */
export function learnInsights(concepts: Concept[], done: ReadonlySet<string>, labels: Record<string, string>): TrackInsight[] {
  const byLang = new Map<string, Concept[]>();
  for (const c of concepts) {
    const lang = c.language || "java";
    if (!byLang.has(lang)) byLang.set(lang, []);
    byLang.get(lang)!.push(c);
  }
  return [...byLang.entries()].map(([lang, cs]) => ({
    key: `learn:${lang}`,
    label: `Learn · ${labels[lang] ?? lang}`,
    icon: "learn",
    href: `/learn?track=${lang}`,
    done: cs.filter((c) => done.has(c.key)).length,
    total: cs.length,
    unit: "chapter",
  }));
}

/** A Mastery programme: core weeks with a completion time. */
export function masteryInsight(track: MasteryTrack, rows: MasteryProgress[]): TrackInsight {
  const core = track.weeks.filter((w) => !w.optional);
  const mine = rows.filter((r) => r.track_key === track.key);
  const completed = new Set(mine.filter((r) => r.completed_at).map((r) => r.week));
  const seconds = mine.reduce((sum, r) => sum + r.study_seconds, 0);
  return {
    key: `mastery:${track.key}`,
    label: track.title,
    icon: "mastery",
    href: "/mastery",
    done: core.filter((w) => completed.has(w.week)).length,
    total: core.length,
    unit: "week",
    note: seconds > 0 ? `${Math.round(seconds / 3600)} h studied there` : undefined,
  };
}

// ---- Review decks ---------------------------------------------------------------

export interface ReviewHealth {
  total: number;
  due: number;
  /** Interval of three weeks or more — the card has stuck. */
  mature: number;
  /** Scheduled but not yet mature. */
  young: number;
  /** Share of reviews that were forgotten, over every card's history. */
  lapseRate: number;
  /** Share of cards whose most recent answer was a pass. */
  lastPass: number;
}

export function reviewHealth(cards: CardReview[], today: string): ReviewHealth {
  const total = cards.length;
  const due = cards.filter((c) => c.due_date <= today).length;
  const mature = cards.filter((c) => c.interval_days >= 21).length;
  const reps = cards.reduce((s, c) => s + c.reps + c.lapses, 0);
  const lapses = cards.reduce((s, c) => s + c.lapses, 0);
  const passed = cards.filter((c) => c.last_quality >= 2).length;
  return {
    total,
    due,
    mature,
    young: total - mature,
    lapseRate: reps > 0 ? lapses / reps : 0,
    lastPass: total > 0 ? passed / total : 0,
  };
}

/** Which deck a card belongs to, from its id's namespace (see dsaReview.ts,
 * dsaRecognition.ts and jpVocab.ts for the shapes). */
export function deckOf(cardId: string): string {
  if (cardId.startsWith("jp-vocab")) return "日本語 vocabulary";
  if (cardId.startsWith("dsa-route:") || cardId.startsWith("dsa-variant:")) return "Curriculum recognition";
  if (cardId.startsWith("dsa-")) return "Curriculum self-checks";
  if (cardId.startsWith("jp_")) return "日本語 glossaries";
  return "Learn decks";
}

export function reviewByDeck(cards: CardReview[], today: string): { deck: string; health: ReviewHealth }[] {
  const groups = new Map<string, CardReview[]>();
  for (const c of cards) {
    const d = deckOf(c.card_id);
    if (!groups.has(d)) groups.set(d, []);
    groups.get(d)!.push(c);
  }
  return [...groups.entries()]
    .map(([deck, cs]) => ({ deck, health: reviewHealth(cs, today) }))
    .sort((a, b) => b.health.total - a.health.total);
}

// ---- Problems ---------------------------------------------------------------------

/** Time spent solving, from each problem's own tally. */
export function solvingSeconds(problems: Problem[]): number {
  return problems.reduce((s, p) => s + (p.time_taken_seconds || 0), 0);
}

/** The tracks in order of most recently useful: started and unfinished first, then done, then untouched. */
export function orderTracks(tracks: TrackInsight[]): TrackInsight[] {
  const rank = (t: TrackInsight) => (t.total === 0 ? 3 : t.done === 0 ? 2 : t.done === t.total ? 1 : 0);
  return [...tracks].sort((a, b) => rank(a) - rank(b) || share(b) - share(a));
}
