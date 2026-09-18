/**
 * The navigation, grouped by what the learner is doing.
 *
 * It used to be a flat list of ten destinations under one heading, "Practice",
 * which covered the dashboard, a curriculum, a concept library, three courses,
 * a project track, a mastery programme, a Japanese bridge and learning paths —
 * a heading so broad it grouped nothing. The groups below are the actual
 * distinctions: what is due today, what teaches, what is a course, and the app
 * itself.
 *
 * It also could not collapse, and always took 220px — including on Solve and
 * the Projects workbench, which are exactly the pages where the width matters.
 * Ctrl+B toggles an icon-only rail, and the choice is remembered.
 *
 * Badges show what is genuinely waiting: `.nav-badge` had styling and no users
 * since the review count was removed.
 */

import { useEffect, useMemo, useState } from "react";
import { NavLink } from "react-router-dom";
import { api } from "../../api";
import { useStore } from "../../store";
import { useCurriculumData } from "../CurriculumData";
import { reviewLane } from "../../lib/dsaReview";
import { loadDoneChapters } from "../../lib/learnProgress";
import type { CardReview } from "../../types";

interface NavItem {
  to: string;
  label: string;
  icon: string;
  end?: boolean;
  /** Key into the badge map below. */
  badge?: "curriculum" | "vocab";
  /** Shows a dot when the track has been started but not finished. */
  progressKey?: "ts" | "java";
}

const GROUPS: { section: string; items: NavItem[] }[] = [
  {
    section: "Today",
    items: [{ to: "/", label: "Today", icon: "🏠", end: true }],
  },
  {
    section: "Learn",
    items: [
      { to: "/library", label: "DSA Curriculum", icon: "📚", badge: "curriculum" },
      { to: "/learn", label: "Learn", icon: "📘" },
      { to: "/paths", label: "Learning Paths", icon: "🧭" },
    ],
  },
  {
    section: "Courses",
    items: [
      { to: "/course", label: "TypeScript Course", icon: "📗", progressKey: "ts" },
      { to: "/java-course", label: "Java Course", icon: "☕", progressKey: "java" },
      { to: "/backend", label: "Backend Lab", icon: "🛠️" },
      { to: "/projects", label: "Projects", icon: "🧱" },
      { to: "/mastery", label: "6-Month Mastery", icon: "🎓" },
    ],
  },
  {
    section: "Languages",
    items: [{ to: "/jp-bridge", label: "日本語 → Java", icon: "🈁", badge: "vocab" }],
  },
  {
    section: "App",
    items: [{ to: "/settings", label: "Settings", icon: "⚙️" }],
  },
];

/** What is actually due, for the nav badges. */
function useBadges() {
  const { data: curriculum } = useCurriculumData();
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const [started, setStarted] = useState<Set<string>>(new Set());

  useEffect(() => {
    api
      .cardReviews()
      .then((rs) => setReviews(new Map(rs.map((r) => [r.card_id, r]))))
      .catch(() => {
        /* a badge is not worth an error; it just does not appear */
      });
    loadDoneChapters()
      .then(setStarted)
      .catch(() => {
        /* same */
      });
  }, []);

  const lane = useMemo(
    () => (curriculum ? reviewLane(curriculum, reviews) : null),
    [curriculum, reviews]
  );

  return {
    curriculum: lane ? lane.checksDue : 0,
    // 日本語 vocabulary cards are scheduled in the same card_reviews table.
    vocab: [...reviews.values()].filter(
      (r) => r.card_id.startsWith("jp-vocab") && r.due_date <= new Date().toISOString().slice(0, 10)
    ).length,
    inProgress: {
      ts: [...started].some((k) => k.startsWith("ts-course:")),
      java: [...started].some((k) => k.startsWith("java-course:")),
    },
  };
}

export function Sidebar() {
  const collapsed = useStore((s) => s.sidebarAuto ?? s.prefs.sidebarCollapsed);
  const toggleSidebar = useStore((s) => s.toggleSidebar);
  const badges = useBadges();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
        e.preventDefault();
        toggleSidebar();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [toggleSidebar]);

  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`} aria-label="Sections">
      <div className="brand">
        <span className="logo" aria-hidden>
          P
        </span>
        {!collapsed && <span className="brand-name">Poodcode</span>}
      </div>

      <nav>
        {GROUPS.map((group) => (
          <div key={group.section} className="nav-group">
            {/* The heading is decoration when collapsed: the rail is icons
                only, so a group label would be a word with nothing under it. */}
            {!collapsed && <div className="nav-section">{group.section}</div>}
            {collapsed && <div className="nav-rule" aria-hidden />}
            {group.items.map((item) => {
              const count = item.badge ? badges[item.badge] : 0;
              const dot = item.progressKey ? badges.inProgress[item.progressKey] : false;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
                  title={collapsed ? item.label : undefined}
                >
                  <span className="ico" aria-hidden>
                    {item.icon}
                  </span>
                  {!collapsed && <span className="nav-label">{item.label}</span>}
                  {count > 0 && (
                    <span className="nav-badge" title={`${count} due`}>
                      {collapsed ? "" : count}
                      <span className="sr-only"> — {count} due</span>
                    </span>
                  )}
                  {dot && count === 0 && (
                    <span className="nav-dot" title="In progress">
                      <span className="sr-only">in progress</span>
                    </span>
                  )}
                </NavLink>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="spacer" />
      {!collapsed && <div className="faint sidebar-foot">Offline · local-first</div>}
    </aside>
  );
}
