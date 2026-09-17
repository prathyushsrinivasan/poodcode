import { useCallback, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { BigOItem, CardReview, Concept, Trace, UnitCheck } from "../types";
import { Markdown, InlineMarkdown } from "../components/Markdown";
import { Confidence, DiffBadge, Empty } from "../components/common";
import { UnitSkeleton } from "../components/Skeleton";
import { SkeletonBlock } from "../components/UnitPractice";
import { StatusBadge, UnitProgress, useCurriculumData } from "../components/CurriculumData";
import {
  findUnit,
  neighbours,
  readUnitTab,
  rememberLastUnit,
  rememberUnitTab,
  type HydratedCurriculum,
  type HydratedRung,
  type HydratedUnit,
} from "../lib/curriculum";
import {
  bigoCardId,
  cardStats,
  checkCardId,
  isCardDue,
  isSlowSolve,
  todayISO,
  unitChecks,
} from "../lib/dsaReview";
import { optionOrder } from "../lib/quizShuffle";

/**
 * One unit of the DSA curriculum: a technique, taught, then drilled.
 *
 * The generator authors up to thirteen parts per unit — why, the model,
 * internals, traces, signals, the playbook, costs, pitfalls, the ladder, a
 * build-it exercise, self-checks, Big-O drills and interview notes. They used to
 * render as one column of collapsible sections, all open, at full window width:
 * a mid-sized unit ran past 5000px, and the thing you came back for (the ladder)
 * sat below everything you had already read.
 *
 * They are now four tabs, in the order a unit is worked:
 *
 *   📖 Learn     — why it exists, the model, what is underneath, traces
 *   🧰 Toolkit   — signals, the playbook, costs, pitfalls
 *   🧗 Practice  — the problem ladder, and building it yourself
 *   🔁 Review    — self-checks, pricing snippets, interview notes
 *
 * Each tab ends by handing you to the next, the last one to the next unit. The
 * tab is remembered per unit, so coming back from a Solve page lands on
 * Practice rather than on the motivation again.
 */
export default function CurriculumUnit() {
  const { key = "" } = useParams();
  const { data, error, setSkipped } = useCurriculumData();
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const nav = useNavigate();

  useEffect(() => {
    api.concepts().then(setConcepts).catch(() => {});
  }, []);

  // Remembered so /library can offer "Resume Backtracking" beside "Up next".
  useEffect(() => {
    if (key) rememberLastUnit(key);
  }, [key]);

  // Self-check scheduling lives in the same `card_reviews` table as the Learn
  // tab's decks, so this is one read and no new storage.
  useEffect(() => {
    api
      .cardReviews()
      .then((rs) => setReviews(new Map(rs.map((r) => [r.card_id, r]))))
      .catch(() => {});
  }, []);

  const grade = useCallback(async (id: string, remembered: boolean) => {
    try {
      // Remembered → "Good" (2), forgot → "Again" (0). Two buttons rather than
      // four: a self-check you had to think about is not a different outcome
      // from one you knew, and asking for a confidence grade on top of recall
      // is how a revision pass turns into a chore nobody does.
      const r = await api.gradeCard(id, remembered ? 2 : 0);
      setReviews((m) => new Map(m).set(id, r));
    } catch {
      /* grading is a convenience; a failed write must not eat the answer */
    }
  }, []);

  // `error` used to be ignored here, so a failed fetch left the page saying
  // "Loading…" forever with no explanation.
  if (error) {
    return (
      <div className="page cur-page">
        <button className="ghost" onClick={() => nav("/library")}>
          ← Curriculum
        </button>
        <Empty icon="⚠️" text={`Could not load the curriculum: ${error}`} />
      </div>
    );
  }
  if (!data) return <UnitSkeleton />;

  const hydrated = findUnit(data, key);
  if (!hydrated) {
    return (
      <div className="page cur-page">
        <Empty icon="🤔" text="No such unit." />
        <button onClick={() => nav("/library")}>Back to the curriculum</button>
      </div>
    );
  }

  // Keyed by unit, so paging with `[` / `]` starts each unit on its own
  // remembered tab instead of inheriting the previous unit's.
  return (
    <UnitView
      key={key}
      data={data}
      hydrated={hydrated}
      reviews={reviews}
      concepts={concepts}
      onGrade={grade}
      onSetSkipped={(v) => setSkipped([key], v)}
    />
  );
}

type TabKey = "learn" | "toolkit" | "practice" | "review";

const TABS: { key: TabKey; icon: string; label: string; hint: string }[] = [
  { key: "learn", icon: "📖", label: "Learn", hint: "Why it exists and how it works" },
  { key: "toolkit", icon: "🧰", label: "Toolkit", hint: "Signals, code shapes, costs, pitfalls" },
  { key: "practice", icon: "🧗", label: "Practice", hint: "The problem ladder" },
  { key: "review", icon: "🔁", label: "Review", hint: "Self-checks and interview prep" },
];

interface SectionDef {
  /** DOM id, and the `#hash` that deep-links to it. */
  id: string;
  tab: TabKey;
  icon: string;
  title: string;
  /** For the "on this tab" list, where the full title does not fit. */
  short: string;
  count?: string;
  lead?: React.ReactNode;
  meta?: React.ReactNode;
  body: React.ReactNode;
}

/** The scroll container. The page itself never scrolls; `.main` does. */
const scroller = () => document.querySelector<HTMLElement>(".main");

function UnitView({
  data,
  hydrated,
  reviews,
  concepts,
  onGrade,
  onSetSkipped,
}: {
  data: HydratedCurriculum;
  hydrated: HydratedUnit;
  reviews: Map<string, CardReview>;
  concepts: Concept[];
  onGrade: (cardId: string, remembered: boolean) => void;
  onSetSkipped: (skipped: boolean) => void;
}) {
  const nav = useNavigate();
  const { hash } = useLocation();
  const hashTarget = hash.replace(/^#/, "");
  // null = each card decides for itself; true = the whole section is open.
  const [revealAll, setRevealAll] = useState<boolean | null>(null);
  const tabsTopRef = useRef<HTMLDivElement>(null);

  const u = hydrated.unit;
  const key = u.key;
  const today = todayISO();
  const checkStats = unitChecks(hydrated, reviews, today);
  const bigoStats = cardStats(u.bigo.map((_, i) => bigoCardId(key, i)), reviews, today);
  const { prev, next } = neighbours(data, key);
  const stageIndex = data.stages.findIndex((s) => s.units.some((x) => x.unit.key === key));
  const stage = stageIndex < 0 ? null : data.stages[stageIndex];
  const libraryUrl = stage ? `/library?stage=${stage.key}` : "/library";
  // For a stale unit, "re-practise" means a problem you already solved — the
  // point is to prove the technique is still there, not to meet a new one.
  const firstSolved =
    hydrated.rungs
      .flatMap((r) => r.items)
      .find((i) => i.problem?.solved_status === "solved")?.problem ?? null;
  const concept = (k: string) => concepts.find((c) => c.key === k);
  // A unit can link the same lesson name in two tracks (Two Pointers in Java and
  // in Algorithms); name the track only when that would otherwise read twice.
  const lessonName = (k: string) => {
    const c = concept(k);
    if (!c) return k;
    const twin = u.lessons.some((o) => o !== k && concept(o)?.name === c.name);
    return twin && c.language ? `${c.name} · ${c.language[0].toUpperCase()}${c.language.slice(1)}` : c.name;
  };
  // Never-graded cards count as due, so "4 due" on a deck you have not opened
  // would be noise. Say due only once reviewing has begun.
  const deckCount = (s: { due: number; started: number; total: number }) =>
    s.started > 0 && s.due > 0 ? `${s.due} due` : `${s.started}/${s.total}`;

  const sections: SectionDef[] = [];
  const add = (s: SectionDef | false | "" | null | undefined) => {
    if (s) sections.push(s);
  };

  add({
    id: "why",
    tab: "learn",
    icon: "🎯",
    title: "Why this exists",
    short: "Why this exists",
    body: <Markdown>{u.why}</Markdown>,
  });
  add({
    id: "model",
    tab: "learn",
    icon: "🧠",
    title: "The model",
    short: "The model",
    body: <Markdown>{u.model}</Markdown>,
  });
  add(
    u.internals && {
      id: "internals",
      tab: "learn",
      icon: "🔬",
      title: "How it works underneath",
      short: "Underneath",
      lead: "The costs in the Toolkit are consequences of a layout. Quoting them without it is memorisation — this is where they stop being trivia.",
      body: <Markdown>{u.internals}</Markdown>,
    }
  );
  add(
    u.traces.length > 0 && {
      id: "traces",
      tab: "learn",
      icon: "🎞️",
      title: "Worked traces",
      short: "Worked traces",
      count: String(u.traces.length),
      lead: "The state, one row per step. Everything hard here is state changing over time, which a table shows in one glance and prose only asserts.",
      body: u.traces.map((t, i) => <TraceTable key={i} trace={t} />),
    }
  );
  add(
    u.signals.length > 0 && {
      id: "signals",
      tab: "toolkit",
      icon: "🔔",
      title: "Signals — when to reach for this",
      short: "Signals",
      count: String(u.signals.length),
      lead: "The routing table. Reading a prompt and landing on the technique without deriving it is most of what separates fast solvers from slow ones.",
      body: (
        <div className="card" style={{ padding: 0, overflowX: "auto" }}>
          <table className="data">
            <thead>
              <tr>
                <th style={{ width: "38%" }}>When the prompt says…</th>
                <th style={{ width: "26%" }}>Reach for</th>
                <th>Because</th>
              </tr>
            </thead>
            <tbody>
              {u.signals.map((s, i) => (
                <tr key={i} style={{ cursor: "default" }}>
                  <td><InlineMarkdown>{s.when}</InlineMarkdown></td>
                  <td><strong><InlineMarkdown>{s.reach_for}</InlineMarkdown></strong></td>
                  <td className="dim"><InlineMarkdown>{s.why}</InlineMarkdown></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ),
    }
  );
  add(
    u.skeletons.length > 0 && {
      id: "skeletons",
      tab: "toolkit",
      icon: "⌨️",
      title: "The playbook",
      short: "Playbook",
      count: String(u.skeletons.length),
      lead: "Copy each of these out by hand once. Patterns are muscle memory, and reading them is not how that gets built — so each one has a pad that hides the original, compiles what you type, then diffs the two.",
      body: u.skeletons.map((s, i) => <SkeletonBlock key={i} skeleton={s} />),
    }
  );
  add(
    u.costs.length > 0 && {
      id: "costs",
      tab: "toolkit",
      icon: "⏱️",
      title: "What it costs",
      short: "Costs",
      body: (
        <div className="card" style={{ padding: 0, overflowX: "auto" }}>
          <table className="data">
            <thead>
              <tr>
                <th>Operation</th>
                <th style={{ width: 130 }}>Time</th>
                <th style={{ width: 130 }}>Space</th>
                <th>Note</th>
              </tr>
            </thead>
            <tbody>
              {u.costs.map((c, i) => (
                <tr key={i} style={{ cursor: "default" }}>
                  <td><InlineMarkdown>{c.op}</InlineMarkdown></td>
                  <td className="mono">{c.time}</td>
                  <td className="mono">{c.space}</td>
                  <td className="dim"><InlineMarkdown>{c.note}</InlineMarkdown></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ),
    }
  );
  add(
    u.pitfalls.length > 0 && {
      id: "pitfalls",
      tab: "toolkit",
      icon: "⚠️",
      title: "Pitfalls, by symptom",
      short: "Pitfalls",
      count: String(u.pitfalls.length),
      lead: "Indexed by what you will actually see, so a failing run is searchable.",
      body: u.pitfalls.map((p, i) => (
        <div key={i} className="cu-pitfall">
          <div className="cu-pitfall-symptom">{p.symptom}</div>
          <div className="dim" style={{ marginBottom: 6 }}>
            <InlineMarkdown>{p.cause}</InlineMarkdown>
          </div>
          <div>
            <strong style={{ color: "var(--good)" }}>Fix: </strong>
            <InlineMarkdown>{p.fix}</InlineMarkdown>
          </div>
        </div>
      )),
    }
  );
  add({
    id: "ladder",
    tab: "practice",
    icon: "🧗",
    title: "The problem ladder",
    short: "Problem ladder",
    count: `${hydrated.solved}/${hydrated.total}`,
    lead: "Work down the page. A rung is a group of problems drilling the same twist — when it stops being interesting, move to the next one. You do not have to clear a rung to move on.",
    body: hydrated.rungs.map((r, i) => (
      <RungBlock key={i} rung={r} number={i + 1} onOpen={(id) => nav(`/solve/${id}`)} />
    )),
  });
  add(
    u.build_it && {
      id: "build",
      tab: "practice",
      icon: "🔨",
      title: "Build it yourself",
      short: "Build it yourself",
      body: <Markdown>{u.build_it}</Markdown>,
    }
  );
  add(
    u.checks.length > 0 && {
      id: "checks",
      tab: "review",
      icon: "✅",
      title: "Self-check",
      short: "Self-check",
      count: deckCount(checkStats),
      lead: "Answer out loud, reveal, then say whether you had it. Each of these is a scheduled card — grading it here is what makes it come back in a month instead of never.",
      meta: (
        <button
          className="ghost"
          style={{ fontSize: 12, padding: "2px 8px" }}
          title="Individually revealable is right for study and wrong for the month-later scan"
          onClick={() => setRevealAll((v) => (v === true ? null : true))}
        >
          {revealAll === true ? "Hide all answers" : "Reveal all answers"}
        </button>
      ),
      body: u.checks.map((c, i) => (
        <Check
          key={i}
          check={c}
          review={reviews.get(checkCardId(key, i))}
          today={today}
          forceShow={revealAll}
          onGrade={(remembered) => onGrade(checkCardId(key, i), remembered)}
        />
      )),
    }
  );
  add(
    u.bigo.length > 0 && {
      id: "bigo",
      tab: "review",
      icon: "⏳",
      title: "Price the snippet",
      short: "Price the snippet",
      count: deckCount(bigoStats),
      lead: (
        <>
          You can solve every problem in this unit without once <em>stating</em> a complexity,
          which is the opposite of the skill. Read, price, then check — these are scheduled like
          the self-checks.
        </>
      ),
      body: u.bigo.map((b, i) => (
        <BigOCard
          key={i}
          item={b}
          review={reviews.get(bigoCardId(key, i))}
          today={today}
          onGrade={(right) => onGrade(bigoCardId(key, i), right)}
        />
      )),
    }
  );
  add(
    u.interview && {
      id: "interview",
      tab: "review",
      icon: "💼",
      title: "In an interview",
      short: "In an interview",
      body: <Markdown>{u.interview}</Markdown>,
    }
  );

  const tabs = TABS.filter((t) => sections.some((s) => s.tab === t.key));

  const [tab, setTab] = useState<TabKey>(() => {
    const fromHash = sections.find((s) => s.id === hashTarget)?.tab;
    const remembered = tabs.find((t) => t.key === readUnitTab(key))?.key;
    return fromHash ?? remembered ?? tabs[0]?.key ?? "learn";
  });
  const [scrollTarget, setScrollTarget] = useState<string | null>(hashTarget || null);

  // A fresh unit starts at the top; arriving with `#pitfalls` scrolls there
  // instead. Mount only — the hash effect below handles later changes.
  const startsAtHash = useRef(!!hashTarget);
  useEffect(() => {
    if (!startsAtHash.current) scroller()?.scrollTo({ top: 0 });
  }, []);

  /**
   * Honour `#pitfalls` and friends: switch to the tab holding that section, then
   * scroll to it. Arriving at a link and finding the section on another tab is
   * the link not working.
   */
  const sectionTab = (id: string) => sections.find((s) => s.id === id)?.tab;
  const hashTab = sectionTab(hashTarget);
  useEffect(() => {
    if (!hashTab) return;
    setTab(hashTab);
    setScrollTarget(hashTarget);
  }, [hashTarget, hashTab]);

  // Scrolls after the tab holding the target has rendered.
  useEffect(() => {
    if (!scrollTarget) return;
    const id = requestAnimationFrame(() => {
      document.getElementById(scrollTarget)?.scrollIntoView({ block: "start", behavior: "smooth" });
      setScrollTarget(null);
    });
    return () => cancelAnimationFrame(id);
  }, [scrollTarget, tab]);

  const selectTab = useCallback(
    (t: TabKey) => {
      setTab(t);
      rememberUnitTab(key, t);
      // If you have scrolled past the tab bar, a new tab should start at its
      // own top rather than somewhere in the middle of the page.
      const main = scroller();
      const marker = tabsTopRef.current;
      if (main && marker) {
        const top =
          marker.getBoundingClientRect().top - main.getBoundingClientRect().top + main.scrollTop;
        if (main.scrollTop > top) main.scrollTo({ top });
      }
    },
    [key]
  );

  /**
   * `1`–`4` switch tabs, `[` / `]` page between units, `g l` goes back to the
   * curriculum. Skipped while focus is in an input or a Monaco editor, because
   * those keys are characters there and stealing them would be worse than the
   * shortcut is good. The handler lives in a ref so the listener is registered
   * once and still sees the latest tabs and neighbours.
   */
  const gPending = useRef(false);
  const onKey = useRef<(e: KeyboardEvent) => void>(() => {});
  onKey.current = (e: KeyboardEvent) => {
    const node = e.target as HTMLElement | null;
    const typing =
      !!node &&
      (node.tagName === "INPUT" ||
        node.tagName === "TEXTAREA" ||
        node.tagName === "SELECT" ||
        node.isContentEditable ||
        !!node.closest?.(".monaco-editor"));
    if (e.ctrlKey || e.metaKey || e.altKey || typing) return;
    if (gPending.current && e.key === "l") {
      gPending.current = false;
      e.preventDefault();
      nav(libraryUrl);
      return;
    }
    gPending.current = e.key === "g";
    const digit = Number(e.key);
    if (Number.isInteger(digit) && digit >= 1 && digit <= tabs.length) {
      e.preventDefault();
      selectTab(tabs[digit - 1].key);
      return;
    }
    const to = e.key === "[" ? prev : e.key === "]" ? next : null;
    if (to) {
      e.preventDefault();
      nav(`/library/unit/${to.unit.key}`);
    }
  };
  useEffect(() => {
    const listener = (e: KeyboardEvent) => onKey.current(e);
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);

  const tabSections = sections.filter((s) => s.tab === tab);
  const tabIndex = tabs.findIndex((t) => t.key === tab);
  const nextTab = tabs[tabIndex + 1] ?? null;
  const reviewDeck = {
    due: checkStats.due + bigoStats.due,
    started: checkStats.started + bigoStats.started,
    total: checkStats.total + bigoStats.total,
  };

  const tabCount = (t: TabKey): { text: string; due: boolean } | null => {
    if (t === "practice") return { text: `${hydrated.solved}/${hydrated.total}`, due: false };
    if (t === "review" && reviewDeck.total > 0) {
      const text = deckCount(reviewDeck);
      return { text, due: text.endsWith("due") };
    }
    return null;
  };

  return (
    <div className="page cur-page">
      <div className="cu-topbar">
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            nav(libraryUrl);
          }}
          title="g l"
        >
          📚 DSA Curriculum
        </a>
        {stage && (
          <>
            <span>›</span>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                nav(libraryUrl);
              }}
            >
              {stage.icon} {stage.optional ? "Optional stage" : `Stage ${stageIndex + 1}`} · {stage.title}
            </a>
            <span>›</span>
            <span>
              Unit {stage.units.findIndex((x) => x.unit.key === key) + 1} of {stage.units.length}
            </span>
          </>
        )}
        <span className="spacer" />
        {prev && (
          <button
            className="ghost"
            style={{ fontSize: 12 }}
            onClick={() => nav(`/library/unit/${prev.unit.key}`)}
            title="[ — previous unit"
          >
            ← {prev.unit.icon} {prev.unit.title}
          </button>
        )}
        {next && (
          <button
            className="ghost"
            style={{ fontSize: 12 }}
            onClick={() => nav(`/library/unit/${next.unit.key}`)}
            title="] — next unit"
          >
            {next.unit.icon} {next.unit.title} →
          </button>
        )}
      </div>

      <div className="cu-hero">
        <div className="cu-hero-icon" aria-hidden>
          {u.icon}
        </div>
        <div style={{ minWidth: 0 }}>
          <h1>
            {u.title}
            <StatusBadge status={hydrated.status} stale={hydrated.stale} skipped={hydrated.skipped} />
          </h1>
          <div className="dim" style={{ fontSize: 15 }}>
            {u.tagline}
          </div>
          <div className="cu-hero-progress">
            <UnitProgress solved={hydrated.solved} total={hydrated.total} stale={hydrated.stale} />
            <span>
              {hydrated.solved} of {hydrated.total} problems solved
            </span>
          </div>
        </div>
        <div className="cu-hero-actions">
          {hydrated.next && (
            <button className="primary" onClick={() => nav(`/solve/${hydrated.next!.id}`)}>
              Next problem: {hydrated.next.title} →
            </button>
          )}
          <button
            className="ghost"
            title={
              hydrated.skipped
                ? "Put this unit back in the ladder"
                : "Counts as cleared for what unlocks next, without pretending you solved it here"
            }
            onClick={() => onSetSkipped(!hydrated.skipped)}
          >
            {hydrated.skipped ? "Un-skip this unit" : "I know this — skip it"}
          </button>
        </div>
      </div>

      {hydrated.stale && (
        <div className="cu-notice">
          You cleared this {hydrated.lastPractisedDays} days ago and have not touched it since —
          past the {hydrated.staleAfterDays}-day window a cleared unit buys. Green and{" "}
          <em>remembered</em> are not the same thing.{" "}
          {firstSolved && (
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                nav(`/solve/${firstSolved.id}`);
              }}
            >
              Re-practise {firstSolved.title}
            </a>
          )}
          {u.checks.length > 0 && checkStats.due > 0 && (
            <>
              {" · "}
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  selectTab("review");
                }}
              >
                {checkStats.due} self-check{checkStats.due === 1 ? "" : "s"} due
              </a>
            </>
          )}
        </div>
      )}
      {hydrated.unmetPrereqTitles.length > 0 && (
        <div className="cu-notice">
          This unit builds on <strong>{hydrated.unmetPrereqTitles.join(", ")}</strong>, which you
          have not finished. Nothing is locked — but if something here reads as a leap, that is
          where the missing step is.
        </div>
      )}

      <div ref={tabsTopRef} />
      <div className="cu-tabs" role="tablist" aria-label="Unit sections">
        {tabs.map((t, i) => {
          const count = tabCount(t.key);
          return (
            <button
              key={t.key}
              role="tab"
              aria-selected={t.key === tab}
              className={`cu-tab ${t.key === tab ? "active" : ""}`}
              onClick={() => selectTab(t.key)}
              title={`${t.hint} (${i + 1})`}
            >
              <span className="cu-tab-icon" aria-hidden>
                {t.icon}
              </span>
              <span>
                <span className="cu-tab-label">{t.label}</span>
                <span className="cu-tab-hint">{t.hint}</span>
              </span>
              {count && <span className={`cu-tab-count ${count.due ? "due" : ""}`}>{count.text}</span>}
            </button>
          );
        })}
      </div>

      <div className="cu-body">
        <div className="cu-main" role="tabpanel">
          {tabSections.map((s) => (
            <section key={s.id} id={s.id} className="cu-section">
              <div className="cu-section-head">
                <h2>
                  {s.icon} {s.title}
                </h2>
                <span className="spacer" />
                {s.meta}
              </div>
              {s.lead && <p className="cu-lead">{s.lead}</p>}
              {s.body}
            </section>
          ))}

          {nextTab ? (
            <div className="cu-tab-end">
              <span style={{ fontSize: 24 }} aria-hidden>
                {nextTab.icon}
              </span>
              <div style={{ flex: 1, minWidth: 200 }}>
                <div className="cur-eyebrow">Next in this unit</div>
                <strong>{nextTab.label}</strong>
                <span className="dim"> — {nextTab.hint}</span>
              </div>
              <button className="primary" onClick={() => selectTab(nextTab.key)}>
                Continue to {nextTab.label} →
              </button>
            </div>
          ) : (
            <div className="cu-tab-end">
              <div style={{ flex: 1, minWidth: 240 }}>
                <div className="cur-eyebrow">What comes next</div>
                {u.next_up ? (
                  <Markdown>{u.next_up}</Markdown>
                ) : (
                  <p style={{ margin: "4px 0 0" }}>That is the whole unit.</p>
                )}
              </div>
              {next ? (
                <button className="primary" onClick={() => nav(`/library/unit/${next.unit.key}`)}>
                  {next.unit.icon} {next.unit.title} →
                </button>
              ) : (
                <button onClick={() => nav(libraryUrl)}>Back to the curriculum</button>
              )}
            </div>
          )}
        </div>

        <aside className="cu-aside">
          <div>
            <div className="cur-eyebrow">On this tab</div>
            <div className="cu-aside-list">
              {tabSections.map((s) => (
                <button
                  key={s.id}
                  className="cu-aside-link"
                  onClick={() =>
                    document
                      .getElementById(s.id)
                      ?.scrollIntoView({ block: "start", behavior: "smooth" })
                  }
                >
                  <span aria-hidden>{s.icon}</span>
                  <span>{s.short}</span>
                  {s.count && <span className="cu-aside-count">{s.count}</span>}
                </button>
              ))}
            </div>
          </div>

          {u.lessons.length > 0 && (
            <div>
              <div className="cur-eyebrow">Go deeper in Learn</div>
              <p className="faint" style={{ fontSize: 12, margin: "4px 0 6px" }}>
                This page is the map; these are the terrain — full lessons with derivations and
                drills.
              </p>
              <div className="cu-aside-list">
                {u.lessons.map((k) => (
                  <button
                    key={k}
                    className="cu-aside-link"
                    onClick={() => nav(`/learn/${k}`)}
                    title={concept(k)?.what || `Open the ${k} lesson`}
                  >
                    <span aria-hidden>📘</span>
                    <span>{lessonName(k)}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="faint" style={{ fontSize: 12, display: "grid", gap: 6 }}>
            <div className="cur-eyebrow">Keys</div>
            <div>
              <span className="kbd">1</span>–<span className="kbd">{tabs.length}</span> switch tab
            </div>
            <div>
              <span className="kbd">[</span> <span className="kbd">]</span> previous / next unit
            </div>
            <div>
              <span className="kbd">g</span> <span className="kbd">l</span> back to the curriculum
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

function RungBlock({
  rung,
  number,
  onOpen,
}: {
  rung: HydratedRung;
  number: number;
  onOpen: (id: number) => void;
}) {
  // A rung is explicitly "a group of problems drilling the same twist", and there
  // was no way to work it as one: you clicked a row, solved it, came back, and
  // re-scanned for the next unsolved line. The first unsolved problem is what
  // "work this rung" means, and the Solve page now carries the rest of the walk.
  const unsolved = rung.items
    .map((i) => i.problem)
    .filter((p) => p && p.solved_status !== "solved");
  const first = unsolved[0] ?? null;
  const done = rung.total > 0 && rung.solved === rung.total;

  return (
    <div className="cu-rung" style={rung.optional ? { borderStyle: "dashed" } : undefined}>
      <div className="cu-rung-head">
        <div className="row" style={{ flexWrap: "wrap" }}>
          <span className={`cur-num ${done ? "complete" : rung.solved > 0 ? "started" : ""}`}
            style={{ width: 26, height: 26, fontSize: 12 }}
          >
            {done ? "✓" : number}
          </span>
          <strong className={rung.optional ? "dim" : ""} style={{ fontSize: 15 }}>
            {rung.title}
          </strong>
          {rung.optional && (
            <span
              className="badge"
              title={
                rung.counted
                  ? "Optional — you have started it, so it now counts toward this unit"
                  : "Optional — skipping it costs you nothing, and it is not counted until you start it"
              }
            >
              optional
            </span>
          )}
          <span className="spacer" />
          <span className="dim mono" style={{ fontSize: 12 }}>
            {rung.solved}/{rung.total}
          </span>
          {first && (
            <button
              style={{ fontSize: 12, padding: "3px 10px" }}
              title={`Start at ${first.title}; the Solve page carries you to the next one`}
              onClick={() => onOpen(first.id)}
            >
              Work this rung ({unsolved.length} left) →
            </button>
          )}
        </div>
        {rung.purpose && (
          <p className="dim" style={{ margin: "6px 0 0 36px" }}>
            {rung.purpose}
          </p>
        )}
      </div>
      <table className="data">
        <tbody>
          {rung.items.map((item) => {
            const p = item.problem;
            if (!p) {
              return (
                <tr key={item.slug} style={{ cursor: "default" }}>
                  <td colSpan={4} className="faint">
                    {item.slug} — not in your library
                  </td>
                </tr>
              );
            }
            const solved = p.solved_status === "solved";
            const slow = isSlowSolve(p);
            return (
              <tr key={item.slug} onClick={() => onOpen(p.id)}>
                <td style={{ width: 52, textAlign: "center" }}>
                  {solved ? "✅" : p.solved_status === "attempted" ? "◐" : "○"}
                </td>
                <td>
                  <strong className={solved ? "dim" : ""}>{p.title}</strong>
                  {slow && (
                    <span
                      className="faint"
                      style={{ fontSize: 12, marginLeft: 6 }}
                      title={`Solved, but it took ${Math.round(p.time_taken_seconds / 60)} minutes. Correct is not the same as fluent.`}
                    >
                      🐢 {Math.round(p.time_taken_seconds / 60)}m
                    </span>
                  )}
                  {item.note && (
                    <div className="faint" style={{ fontSize: 12 }}>
                      <InlineMarkdown>{item.note}</InlineMarkdown>
                    </div>
                  )}
                </td>
                <td style={{ width: 110 }}>
                  <DiffBadge d={p.difficulty} />
                </td>
                <td style={{ width: 120 }} onClick={(e) => e.stopPropagation()}>
                  <Confidence value={p.confidence} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/** A trace renders as a table with a takeaway, because the point of a trace is
 * never the table — it is the sentence the table makes obvious. State columns
 * are monospaced so successive rows line up and the change is visible. */
function TraceTable({ trace }: { trace: Trace }) {
  /**
   * `null` shows the whole table; a number shows the first `n` rows.
   *
   * A static trace *shows*; a step-through *tests*. Revealing one row at a time
   * with the next state hidden turns reading into predicting, which is the
   * difference between recognising the algorithm and being able to run it. The
   * whole table stays one click away, because during a first read predicting is
   * not the job.
   */
  const [shown, setShown] = useState<number | null>(null);
  const stepping = shown !== null;
  const visible = stepping ? trace.rows.slice(0, shown!) : trace.rows;
  const done = stepping && shown! >= trace.rows.length;

  return (
    <div style={{ marginBottom: 26 }}>
      <div className="row">
        <strong>{trace.title}</strong>
        <span className="spacer" />
        <button
          className="ghost"
          style={{ fontSize: 12, padding: "2px 8px" }}
          title={
            stepping
              ? "Show the whole table"
              : "Reveal one row at a time and predict the next state"
          }
          onClick={() => setShown(stepping ? null : 1)}
        >
          {stepping ? "Show all rows" : "▶ Step through"}
        </button>
      </div>
      {trace.intro && (
        <p className="dim" style={{ margin: "4px 0 8px" }}>
          <InlineMarkdown>{trace.intro}</InlineMarkdown>
        </p>
      )}
      <div className="card" style={{ padding: 0, overflowX: "auto" }}>
        <table className="data">
          <thead>
            <tr>
              {trace.headers.map((h, i) => (
                <th key={i}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visible.map((row, i) => (
              <tr key={i} style={{ cursor: "default" }}>
                {row.map((cell, j) => (
                  <td key={j} className={j === 0 ? "" : "mono"} style={{ whiteSpace: "nowrap" }}>
                    <InlineMarkdown>{cell}</InlineMarkdown>
                  </td>
                ))}
              </tr>
            ))}
            {stepping && !done && (
              <tr style={{ cursor: "default" }}>
                <td colSpan={trace.headers.length} className="faint" style={{ textAlign: "center" }}>
                  … say the next row out loud, then reveal it
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {stepping && (
        <div className="row" style={{ marginTop: 8, gap: 8 }}>
          <button
            className="ghost"
            disabled={shown! <= 1}
            onClick={() => setShown((n) => Math.max(1, (n ?? 1) - 1))}
          >
            ← Back
          </button>
          <button disabled={done} onClick={() => setShown((n) => (n ?? 0) + 1)}>
            Reveal the next row →
          </button>
          <span className="spacer" />
          <span className="faint mono" style={{ fontSize: 12 }}>
            {Math.min(shown!, trace.rows.length)}/{trace.rows.length}
          </span>
        </div>
      )}
      {/* The takeaway is the point of the trace, so it waits until the trace has
          actually been walked — reading the conclusion first would give the
          prediction away. */}
      {trace.takeaway && (!stepping || done) && (
        <p className="dim" style={{ marginTop: 8 }}>
          <InlineMarkdown>{trace.takeaway}</InlineMarkdown>
        </p>
      )}
    </div>
  );
}

/** One Big-O drill item: a snippet, four prices, and the reason.
 *
 * Unlike a self-check there is no "did you have it?" to self-report — the answer
 * is multiple choice, so the grade is the choice. Self-grading a question with
 * one right answer would only add a way to lie to yourself. */
function BigOCard({
  item,
  review,
  today,
  onGrade,
}: {
  item: BigOItem;
  review: CardReview | undefined;
  today: string;
  onGrade: (right: boolean) => void;
}) {
  const [picked, setPicked] = useState<string | null>(null);
  const right = picked === item.answer;
  const due = isCardDue(review, today);
  const graded = (review?.reps ?? 0) > 0 || (review?.lapses ?? 0) > 0;

  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <div className="row">
        <span className="dim" style={{ fontSize: 13 }}>
          What is the complexity?
        </span>
        <span className="spacer" />
        {graded && !due && (
          <span className="faint mono" style={{ fontSize: 12 }} title="Next review">
            due {review!.due_date}
          </span>
        )}
        {graded && due && (
          <span className="badge" style={{ color: "var(--accent)", borderColor: "var(--accent)" }}>
            due
          </span>
        )}
      </div>
      <Markdown>{"```java\n" + item.code + "```"}</Markdown>
      <div className="grid cols-2">
        {/* Authors list the answer early — across the seed it was never the last
            option — so the authored order would be a tell. Shuffled per snippet,
            deterministically, like every other multiple-choice question. */}
        {optionOrder(item.code, item.options.length).map((i) => item.options[i]).map((opt) => {
          let border: string | undefined;
          if (picked !== null) {
            if (opt === item.answer) border = "var(--good)";
            else if (opt === picked) border = "var(--bad)";
          }
          return (
            <button
              key={opt}
              style={{ textAlign: "left", borderColor: border, color: border, padding: "8px 10px" }}
              disabled={picked !== null}
              onClick={() => {
                setPicked(opt);
                onGrade(opt === item.answer);
              }}
            >
              <span className="mono">{opt}</span>
            </button>
          );
        })}
      </div>
      {picked !== null && (
        <div style={{ marginTop: 10 }}>
          <strong style={{ color: right ? "var(--good)" : "var(--bad)" }}>
            {right ? "Correct." : `Not quite — it is ${item.answer}.`}
          </strong>
          <div className="dim" style={{ marginTop: 4 }}>
            <Markdown>{item.why}</Markdown>
          </div>
        </div>
      )}
    </div>
  );
}

/** One self-check, revealable and gradeable.
 *
 * The grade buttons appear only after the answer is revealed, because grading
 * your recall before seeing the answer is not a measurement of anything. */
function Check({
  check,
  review,
  today,
  forceShow,
  onGrade,
}: {
  check: UnitCheck;
  review: CardReview | undefined;
  today: string;
  /** Section-wide reveal: `true` shows every answer, `null` returns control to
   * the per-card button. A revision scan wants all of them at once; a study
   * session wants one at a time, and neither should win permanently. */
  forceShow: boolean | null;
  onGrade: (remembered: boolean) => void;
}) {
  const [own, setOwn] = useState(false);
  const show = forceShow ?? own;
  const setShow = (v: boolean | ((p: boolean) => boolean)) =>
    setOwn(typeof v === "function" ? v(show) : v);
  const due = isCardDue(review, today);
  const graded = (review?.reps ?? 0) > 0 || (review?.lapses ?? 0) > 0;

  return (
    <div className="card" style={{ marginBottom: 10 }}>
      <div className="row" style={{ alignItems: "flex-start" }}>
        <div style={{ flex: 1, paddingTop: 4 }}>
          <InlineMarkdown>{check.q}</InlineMarkdown>
        </div>
        {graded && !due && (
          <span className="faint mono" style={{ fontSize: 12, paddingTop: 6 }} title="Next review">
            due {review!.due_date}
          </span>
        )}
        {graded && due && (
          <span className="badge" style={{ color: "var(--accent)", borderColor: "var(--accent)", marginTop: 5 }}>
            due
          </span>
        )}
        <button className="ghost" onClick={() => setShow((s) => !s)}>
          {show ? "Hide" : "Reveal"}
        </button>
      </div>
      {show && (
        <>
          <div className="dim" style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--border)" }}>
            <InlineMarkdown>{check.a}</InlineMarkdown>
          </div>
          <div className="row" style={{ marginTop: 10, gap: 8 }}>
            <button
              className="ghost"
              style={{ borderColor: "var(--bad)", color: "var(--bad)" }}
              onClick={() => {
                onGrade(false);
                setShow(false);
              }}
            >
              Forgot
            </button>
            <button
              className="ghost"
              style={{ borderColor: "var(--good)", color: "var(--good)" }}
              onClick={() => {
                onGrade(true);
                setShow(false);
              }}
            >
              Had it
            </button>
            <span className="spacer" />
            {review && review.reps > 0 && (
              <span className="faint" style={{ fontSize: 12 }}>
                {review.reps} correct in a row
                {review.lapses > 0 && ` · ${review.lapses} lapse${review.lapses === 1 ? "" : "s"}`}
              </span>
            )}
          </div>
        </>
      )}
    </div>
  );
}
