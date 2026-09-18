/**
 * "Continue" cards — one per track the learner has actually started.
 *
 * The Dashboard's answer to "what now?" used to be four buttons that repeated
 * the sidebar ("DSA Curriculum · TypeScript Course · Java Course · Backend
 * Lab"), which told you where the tracks were but not where *you* were in them.
 * Each card here names the last position and the next action instead.
 *
 * A track that has not been started renders nothing, so the page stays short
 * for someone following one track and fills in as they take on more.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";
import { loadDoneChapters } from "../../lib/learnProgress";
import type { WeeklyCourse } from "../../types";

export interface TrackCard {
  key: string;
  icon: string;
  track: string;
  /** Where they are: "Module 7 · Collections". */
  position: string;
  /** What the button does next. */
  action: string;
  href: string;
  /** 0-1, or null for tracks without a meaningful denominator. */
  progress: number | null;
  detail: string;
}

/* Completion is stored per week in the same chapter-done set the Learn tab
   uses, namespaced by the *route* key ("ts", "java") rather than the seed's own
   key ("typescript"). Course.tsx owns this convention; it is repeated here
   rather than exported because changing it would orphan existing progress. */
const weekKey = (trackKey: string, n: number) => `${trackKey}-course:w${n}`;

/** A course's resume point: the first authored week not yet marked done. */
function courseCard(
  course: WeeklyCourse,
  trackKey: string,
  done: Set<string>,
  icon: string,
  base: string
): TrackCard | null {
  const authored = course.weeks.filter((w) => w.authored);
  if (authored.length === 0) return null;

  const cleared = authored.filter((w) => done.has(weekKey(trackKey, w.number)));
  // Nothing cleared yet: this is a track not started, not one in progress.
  if (cleared.length === 0) return null;

  const resume = authored.find((w) => !done.has(weekKey(trackKey, w.number)));
  const unit = course.unit_label || "Week";
  const week = resume ?? authored[authored.length - 1];

  return {
    key: trackKey,
    icon,
    track: course.title,
    position: `${unit} ${week.number}${week.theme ? ` · ${week.theme}` : ""}`,
    action: resume ? `Resume ${unit.toLowerCase()} ${week.number}` : "Course complete — review",
    href: resume ? `${base}/${week.number}` : base,
    progress: cleared.length / authored.length,
    detail: `${cleared.length}/${authored.length} ${unit.toLowerCase()}s done`,
  };
}

/** Loads every track's position. Returns `null` while loading. */
export function useTrackCards() {
  const [cards, setCards] = useState<TrackCard[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const [ts, java, done] = await Promise.all([
        api.tsCourse().catch(() => null),
        api.javaCourse().catch(() => null),
        loadDoneChapters().catch(() => new Set<string>()),
      ]);
      if (cancelled) return;
      const list: TrackCard[] = [];
      if (ts) {
        const c = courseCard(ts, "ts", done, "📗", "/course");
        if (c) list.push(c);
      }
      if (java) {
        const c = courseCard(java, "java", done, "☕", "/java-course");
        if (c) list.push(c);
      }
      setCards(list);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return cards;
}

export function TrackCardView({ card }: { card: TrackCard }) {
  return (
    <div className="today-card">
      <div className="today-card-head">
        <span className="today-card-icon" aria-hidden>
          {card.icon}
        </span>
        <span className="today-card-track">{card.track}</span>
      </div>
      <div className="today-card-position">{card.position}</div>
      {card.progress !== null && (
        <div className="progress today-card-progress">
          <span style={{ width: `${Math.round(card.progress * 100)}%` }} />
        </div>
      )}
      <div className="today-card-detail">{card.detail}</div>
      <Link className="today-card-action" to={card.href}>
        {card.action} →
      </Link>
    </div>
  );
}
