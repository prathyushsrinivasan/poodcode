import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { useCrumb } from "../store";
import type {
  BigOItem,
  CalcDrill,
  CardReview,
  Concept,
  EdgeCase,
  Invariant,
  Rewrite,
  Trace,
  UnitCheck,
  Variant,
  Walkthrough,
} from "../types";
import { Markdown, InlineMarkdown } from "../components/Markdown";
import { Confidence, DiffBadge } from "../components/common";
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
  quizCardId,
  todayISO,
  unitChecks,
} from "../lib/dsaReview";
import { optionOrder } from "../lib/quizShuffle";
import { calcCardId, calcIsCorrect } from "../lib/unitLab";
import { UnitLab } from "../components/UnitLab";
import {
  variantCardId,
  variantQuestions,
  type VariantQuestion,
} from "../lib/dsaRecognition";
import { EmptyState, ErrorState, Icon, type IconName } from "../components/ui";
import { loadFailed } from "../lib/failures";

/**
 * One unit of the DSA curriculum: a technique, taught, then drilled.
 *
 * The generator authors up to sixteen parts per unit — why, the model, the loop
 * invariant, internals, traces, signals, the playbook, the family table, the
 * slow-vs-fast rewrites, costs, pitfalls, the ladder, a build-it exercise,
 * self-checks, Big-O drills and interview notes. They used to render as one
 * column of collapsible sections, all open, at full window width: a mid-sized
 * unit ran past 5000px, and the thing you came back for (the ladder) sat below
 * everything you had already read.
 *
 * They are now four tabs, in the order a unit is worked:
 *
 *   📖 Learn     — why it exists, the model, the invariant, what is underneath, traces
 *   🧰 Toolkit   — signals, the playbook, the family, slow vs fast, costs, pitfalls
 *   🧗 Practice  — the problem ladder, and building it yourself
 *   🔁 Review    — self-checks, pricing snippets, interview notes
 *
 * Each tab ends by handing you to the next, the last one to the next unit. The
 * tab is remembered per unit, so coming back from a Solve page lands on
 * Practice rather than on the motivation again.
 */
export default function CurriculumUnit() {
  const { key = "" } = useParams();
  const { data, error, reload, setSkipped } = useCurriculumData();
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const nav = useNavigate();

  useEffect(() => {
    api.concepts().then(setConcepts).catch(loadFailed("the concept links"));
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
      .catch(loadFailed("your review schedule"));
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
        <ErrorState title="Could not load the curriculum." error={error} onRetry={reload} />
      </div>
    );
  }
  if (!data) return <UnitSkeleton />;

  const hydrated = findUnit(data, key);
  if (!hydrated) {
    return (
      <div className="page cur-page">
        <EmptyState
          icon="map"
          title="No such unit."
          action={{ label: "Back to the curriculum", icon: "back", onClick: () => nav("/library") }}
        />
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

const TABS: { key: TabKey; icon: IconName; label: string; hint: string }[] = [
  { key: "learn", icon: "learn", label: "Learn", hint: "Why it exists and how it works" },
  { key: "toolkit", icon: "tools", label: "Toolkit", hint: "Signals, code shapes, the family, costs, pitfalls" },
  { key: "practice", icon: "trendUp", label: "Practice", hint: "The problem ladder" },
  { key: "review", icon: "refresh", label: "Review", hint: "Self-checks and interview prep" },
];

interface SectionDef {
  /** DOM id, and the `#hash` that deep-links to it. */
  id: string;
  tab: TabKey;
  icon: IconName;
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
  useCrumb(u.title, "DSA unit");
  const today = todayISO();
  const checkStats = unitChecks(hydrated, reviews, today);
  const bigoStats = cardStats(u.bigo.map((_, i) => bigoCardId(key, i)), reviews, today);
  const quizStats = cardStats(u.quizzes.map((_, i) => quizCardId(key, i)), reviews, today);
  const calcStats = cardStats(u.drills.map((_, i) => calcCardId(key, i)), reviews, today);
  // Derived from the family table, so a unit that gains a variant gains a
  // question without anything else being authored. Empty below three variants.
  const familyQuestions = variantQuestions(hydrated);
  const familyStats = cardStats(
    familyQuestions.map((_, i) => variantCardId(key, i)),
    reviews,
    today
  );
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
    icon: "target",
    title: "Why this exists",
    short: "Why this exists",
    body: <Markdown>{u.why}</Markdown>,
  });
  add({
    id: "model",
    tab: "learn",
    icon: "sparkles",
    title: "The model",
    short: "The model",
    body: <Markdown>{u.model}</Markdown>,
  });
  add(
    u.invariant && {
      id: "invariant",
      tab: "learn",
      icon: "locked",
      title: "Why it is allowed to skip the rest",
      short: "The invariant",
      lead: "Every technique here is a loop that refuses to re-read what it has already seen. This is the sentence that makes that legal — and the part people cannot produce under pressure is never the statement, it is why one iteration preserves it.",
      body: <InvariantBlock inv={u.invariant} />,
    }
  );
  add(
    u.lab && {
      id: "lab",
      tab: "learn",
      icon: "playground",
      title: "Try it: the lab",
      short: "The lab",
      lead: "Everything in this unit is a computation, and the fastest way to believe a rule is to poke it. Change the numbers; nothing here is graded.",
      body: (
        <>
          <UnitLab lab={u.lab} />
          {u.extra_labs.map((l, i) => (
            <div key={i} className="cu-extra-lab">
              <UnitLab lab={l} />
            </div>
          ))}
        </>
      ),
    }
  );
  add(
    u.internals && {
      id: "internals",
      tab: "learn",
      icon: "search",
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
      icon: "layers",
      title: "Worked traces",
      short: "Worked traces",
      count: String(u.traces.length),
      lead: "The state, one row per step. Everything hard here is state changing over time, which a table shows in one glance and prose only asserts.",
      body: u.traces.map((t, i) => <TraceTable key={i} trace={t} />),
    }
  );
  add(
    u.walkthrough && {
      id: "walkthrough",
      tab: "learn",
      icon: "paths",
      title: "One problem, start to finish",
      short: "Worked solution",
      lead: "The model explains the technique and the ladder hands you problems. This is the road between them: one problem taken from the prompt to a tested, priced solution, in the same six steps every time.",
      body: (
        <WalkthroughBlock
          walk={u.walkthrough}
          problemId={
            hydrated.rungs.flatMap((r) => r.items).find((i) => i.slug === u.walkthrough!.slug)
              ?.problem?.id ?? null
          }
          onOpen={(id) => nav(`/solve/${id}`)}
        />
      ),
    }
  );
  add(
    u.signals.length > 0 && {
      id: "signals",
      tab: "toolkit",
      icon: "hint",
      title: "Signals — when to reach for this",
      short: "Signals",
      count: String(u.signals.length),
      lead: "The routing table. Reading a prompt and landing on the technique without deriving it is most of what separates fast solvers from slow ones.",
      body: (
        <div className="card p-0 overflow-x-auto">
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
                <tr className="cursor-default" key={i}>
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
    u.stuck.length > 0 && {
      id: "stuck",
      tab: "toolkit",
      icon: "checklist",
      title: "Stuck before the first line?",
      short: "Stuck?",
      count: String(u.stuck.length),
      lead: "Pitfalls are for after a failed run. This is for before any code exists — not answers, but the question that tends to produce one.",
      body: (
        <div className="card p-0 overflow-x-auto">
          <table className="data">
            <thead>
              <tr>
                <th style={{ width: "40%" }}>If you are stuck on…</th>
                <th>Ask yourself</th>
              </tr>
            </thead>
            <tbody>
              {u.stuck.map((r, i) => (
                <tr className="cursor-default" key={i}>
                  <td><InlineMarkdown>{r.when}</InlineMarkdown></td>
                  <td><InlineMarkdown>{r.ask}</InlineMarkdown></td>
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
      icon: "keyboard",
      title: "The playbook",
      short: "Playbook",
      count: String(u.skeletons.length),
      lead: "Copy each of these out by hand once. Patterns are muscle memory, and reading them is not how that gets built — so each one has a pad that hides the original, compiles what you type, then diffs the two.",
      body: u.skeletons.map((s, i) => <SkeletonBlock key={i} skeleton={s} />),
    }
  );
  add(
    u.variants.length > 0 && {
      id: "variants",
      tab: "toolkit",
      icon: "map",
      title: "The family — one change each",
      short: "Family",
      count: String(u.variants.length),
      lead: "Most problems in this unit are the skeleton above with a single line different. Learning them as a list of problems is a reading list; learning them as a list of diffs is the technique.",
      body: <VariantTable variants={u.variants} />,
    }
  );
  add(
    u.rewrites.length > 0 && {
      id: "rewrites",
      tab: "toolkit",
      icon: "streak",
      title: "Slow beside fast",
      short: "Slow vs fast",
      count: String(u.rewrites.length),
      lead: "The re-scan, and then the same code with it deleted. Seeing only the fast version hides which part of it is the trick — and the edit is usually one line.",
      body: u.rewrites.map((r, i) => <RewriteBlock key={i} rewrite={r} />),
    }
  );
  add(
    u.costs.length > 0 && {
      id: "costs",
      tab: "toolkit",
      icon: "timer",
      title: "What it costs",
      short: "Costs",
      body: (
        <div className="card p-0 overflow-x-auto">
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
                <tr className="cursor-default" key={i}>
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
      icon: "warning",
      title: "Pitfalls, by symptom",
      short: "Pitfalls",
      count: String(u.pitfalls.length),
      lead: "Indexed by what you will actually see, so a failing run is searchable.",
      body: u.pitfalls.map((p, i) => (
        <div key={i} className="cu-pitfall">
          <div className="cu-pitfall-symptom">{p.symptom}</div>
          <div className="dim mb-1">
            <InlineMarkdown>{p.cause}</InlineMarkdown>
          </div>
          <div>
            <strong className="c-good">Fix: </strong>
            <InlineMarkdown>{p.fix}</InlineMarkdown>
          </div>
        </div>
      )),
    }
  );
  add({
    id: "ladder",
    tab: "practice",
    icon: "trendUp",
    title: "The problem ladder",
    short: "Problem ladder",
    count: `${hydrated.solved}/${hydrated.total}`,
    lead: "Work down the page. A rung is a group of problems drilling the same twist — when it stops being interesting, move to the next one. You do not have to clear a rung to move on.",
    body: hydrated.rungs.map((r, i) => (
      <RungBlock key={i} rung={r} number={i + 1} onOpen={(id) => nav(`/solve/${id}`)} />
    )),
  });
  add(
    u.edge_cases.length > 0 && {
      id: "edge-cases",
      tab: "practice",
      icon: "playground",
      title: "Test before you submit",
      short: "Edge cases",
      count: String(u.edge_cases.length),
      lead: "The hidden tests are built from cases like these. Each one names the bug it catches — paste the input into the custom-test box before you press Submit.",
      body: u.edge_cases.map((e, i) => <EdgeCaseRow key={i} edge={e} />),
    }
  );
  add(
    u.build_it && {
      id: "build",
      tab: "practice",
      icon: "build",
      title: "Build it yourself",
      short: "Build it yourself",
      body: <Markdown>{u.build_it}</Markdown>,
    }
  );
  add(
    u.checks.length > 0 && {
      id: "checks",
      tab: "review",
      icon: "done",
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
    u.followups.length > 0 && {
      id: "followups",
      tab: "review",
      icon: "shuffle",
      title: "What if…? The interviewer's twist",
      short: "What if…?",
      lead: "Solving it is where the interview starts. Each of these changes one assumption the solution rests on — say what breaks and what replaces it before you open the answer.",
      body: (
        <div className="cu-followups">
          {u.followups.map((f, i) => (
            <details key={i} className="cu-followup">
              <summary>{f.q}</summary>
              <Markdown>{f.a}</Markdown>
            </details>
          ))}
        </div>
      ),
    }
  );
  add(
    u.bigo.length > 0 && {
      id: "bigo",
      tab: "review",
      icon: "clock",
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
    u.quizzes.length > 0 && {
      id: "quizzes",
      tab: "review",
      icon: "tools",
      title: "Spot the bug, predict the result",
      short: "Spot the bug",
      count: deckCount(quizStats),
      lead: (
        <>
          The code in this unit is short, so its bugs are small: one comparison, one rounding,
          one missing <code>max</code>. Reading code and finding the line is a separate skill from
          writing it, and it is the one a failing hidden test demands. Scheduled like the other
          cards.
        </>
      ),
      body: u.quizzes.map((q, i) => (
        <ChoiceCard
          key={i}
          label={q.kind === "bug" ? "Spot the bug" : q.kind === "model" ? "Model it" : "Predict the result"}
          lang={q.kind === "model" ? "text" : "java"}
          prompt={q.prompt}
          code={q.code}
          options={q.options}
          answer={q.answer}
          why={q.why}
          mono={false}
          review={reviews.get(quizCardId(key, i))}
          today={today}
          onGrade={(right) => onGrade(quizCardId(key, i), right)}
        />
      )),
    }
  );
  add(
    u.drills.length > 0 && {
      id: "drills",
      tab: "review",
      icon: "edit",
      title: "Work it out by hand",
      short: "Work it out",
      count: deckCount(calcStats),
      lead: (
        <>
          Multiple choice lets you recognise an answer. These make you produce it — a bitwise AND, a
          modular inverse, where a cell lands — which is what an interviewer watches you do on a
          whiteboard. Type the answer; graded on the first try, and scheduled like the other cards.
        </>
      ),
      body: u.drills.map((d, i) => (
        <CalcCard
          key={i}
          drill={d}
          review={reviews.get(calcCardId(key, i))}
          today={today}
          onGrade={(right) => onGrade(calcCardId(key, i), right)}
        />
      )),
    }
  );
  add(
    familyQuestions.length > 0 && {
      id: "family-drill",
      tab: "review",
      icon: "map",
      title: "Which variant is this?",
      short: "Family drill",
      count: deckCount(familyStats),
      lead: (
        <>
          Routing <em>within</em> the technique. Knowing this unit is the right one is the easy
          half; the expensive confusions — longest versus shortest, at most versus exactly — are
          all one level down, and this is the only place that tests them.
        </>
      ),
      body: familyQuestions.map((q, i) => (
        <VariantCard
          key={i}
          question={q}
          review={reviews.get(variantCardId(key, i))}
          today={today}
          onGrade={(right) => onGrade(variantCardId(key, i), right)}
        />
      )),
    }
  );
  add(
    u.interview && {
      id: "interview",
      tab: "review",
      icon: "mastery",
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

  /** Jump to a section, switching tabs first when it lives on another one. */
  const goToSection = (id: string, onTab: TabKey) => {
    if (onTab !== tab) {
      setTab(onTab);
      rememberUnitTab(key, onTab);
    }
    setScrollTarget(id);
  };

  // Which of this tab's sections is in view, for the outline's highlight.
  const [activeSection, setActiveSection] = useState<string>("");
  const tabSectionIds = tabSections.map((s) => s.id).join("|");
  useEffect(() => {
    const main = scroller();
    const ids = tabSectionIds ? tabSectionIds.split("|") : [];
    if (!main || ids.length === 0) return;
    let frame = 0;
    const spy = () => {
      frame = 0;
      const line = main.getBoundingClientRect().top + 120;
      let current = ids[0]!;
      for (const id of ids) {
        const el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top <= line) current = id;
      }
      setActiveSection(current);
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(spy);
    };
    spy();
    main.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      main.removeEventListener("scroll", onScroll);
      if (frame) cancelAnimationFrame(frame);
    };
  }, [tabSectionIds]);
  const tabIndex = tabs.findIndex((t) => t.key === tab);
  const nextTab = tabs[tabIndex + 1] ?? null;
  const reviewDeck = {
    due: checkStats.due + bigoStats.due + quizStats.due + calcStats.due,
    started: checkStats.started + bigoStats.started + quizStats.started + calcStats.started,
    total: checkStats.total + bigoStats.total + quizStats.total + calcStats.total,
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
          DSA Curriculum
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
            className="ghost text-xs"
            onClick={() => nav(`/library/unit/${prev.unit.key}`)}
            title="[ — previous unit"
          >
            ← {prev.unit.icon} {prev.unit.title}
          </button>
        )}
        {next && (
          <button
            className="ghost text-xs"
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
        <div className="min-w-0">
          <h1>
            {u.title}
            <StatusBadge status={hydrated.status} stale={hydrated.stale} skipped={hydrated.skipped} />
          </h1>
          <div className="dim text-lg">
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
              tabIndex={t.key === tab ? 0 : -1}
              className={`cu-tab ${t.key === tab ? "active" : ""}`}
              onClick={() => selectTab(t.key)}
              onKeyDown={(e) => {
                const step = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
                if (!step) return;
                e.preventDefault();
                const bar = e.currentTarget.parentElement;
                const to = tabs[(i + step + tabs.length) % tabs.length]!;
                selectTab(to.key);
                requestAnimationFrame(() => (bar?.children[tabs.indexOf(to)] as HTMLElement | undefined)?.focus());
              }}
              title={`${t.hint} (${i + 1})`}
            >
              <span className="cu-tab-icon" aria-hidden>
                <Icon name={t.icon} size={16} />
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
                  <Icon name={s.icon} size={18} className="cu-section-icon" /> {s.title}
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
              <span className="text-2xl" aria-hidden>
                <Icon name={nextTab.icon} size={22} />
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
          {/* The whole unit, every tab, as one outline (UI_ROADMAP H4). A
              section on another tab is one click away: the tab switches, then
              the page scrolls to it. The section in view is highlighted. */}
          <nav aria-label="In this unit">
            <div className="cur-eyebrow">In this unit</div>
            {tabs.map((t) => (
              <div key={t.key} className={`cu-outline-group ${t.key === tab ? "current" : ""}`}>
                <button type="button" className="cu-outline-tab" onClick={() => selectTab(t.key)} aria-current={t.key === tab ? "true" : undefined}>
                  {t.label}
                </button>
                <div className="cu-aside-list">
                  {sections
                    .filter((s) => s.tab === t.key)
                    .map((s) => (
                      <button
                        key={s.id}
                        className={`cu-aside-link ${s.id === activeSection && t.key === tab ? "active" : ""}`}
                        aria-current={s.id === activeSection && t.key === tab ? "location" : undefined}
                        onClick={() => goToSection(s.id, s.tab)}
                      >
                        <Icon name={s.icon} size={14} />
                        <span>{s.short}</span>
                        {s.count && <span className="cu-aside-count">{s.count}</span>}
                      </button>
                    ))}
                </div>
              </div>
            ))}
          </nav>

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
                    <Icon name="learn" size={14} />
                    <span>{lessonName(k)}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="faint text-xs d-grid gap-1">
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
        <div className="row flex-wrap">
          <span className={`cur-num ${done ? "complete" : rung.solved > 0 ? "started" : ""}`}
            style={{ width: 26, height: 26, fontSize: 12 }}
          >
            {done ? "✓" : number}
          </span>
          <strong className={`${rung.optional ? "dim" : ""} text-lg`}>
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
          <span className="dim mono text-xs">
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
                <tr className="cursor-default" key={item.slug}>
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
                  {solved ? <Icon name="done" size={15} label="Solved" className="is-good" /> : p.solved_status === "attempted" ? <Icon name="partial" size={15} label="Attempted" className="is-accent" /> : <Icon name="todo" size={15} label="Not started" className="faint" />}
                </td>
                <td>
                  {/* The row is clickable for the mouse; this link is the same
                      target for Tab and Ctrl-click (D3). */}
                  <Link
                    to={`/solve/${p.id}`}
                    className={`row-link ${solved ? "dim" : ""}`}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <strong>{p.title}</strong>
                  </Link>
                  {slow && (
                    <span
                      className="faint text-xs ml-1"
                      title={`Solved, but it took ${Math.round(p.time_taken_seconds / 60)} minutes. Correct is not the same as fluent.`}
                    >
                      <Icon name="timer" size={12} /> {Math.round(p.time_taken_seconds / 60)}m
                    </span>
                  )}
                  {item.note && (
                    <div className="faint text-xs">
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
/** The four parts of a loop invariant, with the load-bearing one marked.
 *
 * `maintained` is called out rather than rendered as just another row because
 * it is the part that is always missing when someone half-knows a technique:
 * they can state the invariant and cannot say why moving the pointer preserves
 * it, which is exactly the step that licenses throwing away the rest of the
 * search space. Labelling it is a small nudge toward reading that one twice. */
function InvariantBlock({ inv }: { inv: Invariant }) {
  const parts: { label: string; text: string; key: keyof Invariant; hint?: string }[] = [
    { label: "The claim", key: "statement", text: inv.statement },
    {
      label: "True before the loop",
      key: "established",
      text: inv.established,
      hint: "The base case",
    },
    {
      label: "Still true after one step",
      key: "maintained",
      text: inv.maintained,
      hint: "The part that does the work",
    },
    { label: "What it gives you at the end", key: "at_exit", text: inv.at_exit },
  ];
  return (
    <div>
      <div className="cu-inv-claim">
        <Markdown>{inv.statement}</Markdown>
      </div>
      {parts.slice(1).map((p) => (
        <div key={p.key} className={"cu-inv" + (p.key === "maintained" ? " cu-inv-key" : "")}>
          <div className="cu-inv-label">
            {p.label}
            {p.hint && <span className="faint"> — {p.hint}</span>}
          </div>
          <Markdown>{p.text}</Markdown>
        </div>
      ))}
      {inv.note && (
        <div className="cu-inv-note">
          <Markdown>{inv.note}</Markdown>
        </div>
      )}
    </div>
  );
}

/** The technique's family, as a table of diffs.
 *
 * `change` gets its own column and comes first because that is the field that
 * makes this a technique rather than a reading list: every row is the same
 * skeleton, and the column says what to edit. */
function VariantTable({ variants }: { variants: Variant[] }) {
  return (
    <div className="card p-0 overflow-x-auto">
      <table className="data">
        <thead>
          <tr>
            <th style={{ width: 180 }}>Variant</th>
            <th>The one change</th>
            <th>Reach for it when</th>
            <th style={{ width: 150 }}>Cost</th>
          </tr>
        </thead>
        <tbody>
          {variants.map((v, i) => (
            <tr className="cursor-default" key={i}>
              <td>
                <strong>{v.name}</strong>
              </td>
              <td>
                <InlineMarkdown>{v.change}</InlineMarkdown>
                {v.gotcha && (
                  <div className="cu-var-gotcha">
                    <span className="cu-var-gotcha-tag">watch</span>{" "}
                    <InlineMarkdown>{v.gotcha}</InlineMarkdown>
                  </div>
                )}
              </td>
              <td className="dim">
                <InlineMarkdown>{v.when}</InlineMarkdown>
              </td>
              <td className="mono">{v.cost}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** The slow version and the fast one, side by side.
 *
 * The slow version is shown FIRST and by default, which is the whole point:
 * the lesson is the diff, and a reader who never sees what was deleted has to
 * take on faith which part of the fast version is doing the work. `why` stays
 * collapsed until asked for, so the code can be compared before being
 * explained. */
function RewriteBlock({ rewrite }: { rewrite: Rewrite }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="cu-rewrite">
      <div className="row mb-2">
        <strong>{rewrite.title}</strong>
      </div>
      <div className="cu-rewrite-pair">
        <div>
          <div className="cu-rewrite-label cu-rewrite-slow">Before — the re-scan</div>
          <pre className="cu-rewrite-code">
            <code>{rewrite.slow}</code>
          </pre>
        </div>
        <div>
          <div className="cu-rewrite-label cu-rewrite-fast">After</div>
          <pre className="cu-rewrite-code">
            <code>{rewrite.fast}</code>
          </pre>
        </div>
      </div>
      <p className="cu-rewrite-edit">
        <span className="cu-rewrite-edit-tag">the edit</span>{" "}
        <InlineMarkdown>{rewrite.edit}</InlineMarkdown>
      </p>
      <button className="ghost text-xs" onClick={() => setOpen((o) => !o)}>
        {open ? "Hide why" : "Why the edit cannot lose an answer →"}
      </button>
      {open && (
        <div className="mt-2">
          <Markdown>{rewrite.why}</Markdown>
        </div>
      )}
    </div>
  );
}

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
    <div className="mb-5">
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
      <div className="card p-0 overflow-x-auto">
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
              <tr className="cursor-default" key={i}>
                {row.map((cell, j) => (
                  <td key={j} className={`${j === 0 ? "" : "mono"} ws-nowrap`}>
                    <InlineMarkdown>{cell}</InlineMarkdown>
                  </td>
                ))}
              </tr>
            ))}
            {stepping && !done && (
              <tr className="cursor-default">
                <td colSpan={trace.headers.length} className="faint text-center">
                  … say the next row out loud, then reveal it
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {stepping && (
        <div className="row mt-2 gap-2">
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
          <span className="faint mono text-xs">
            {Math.min(shown!, trace.rows.length)}/{trace.rows.length}
          </span>
        </div>
      )}
      {/* The takeaway is the point of the trace, so it waits until the trace has
          actually been walked — reading the conclusion first would give the
          prediction away. */}
      {trace.takeaway && (!stepping || done) && (
        <p className="dim mt-2">
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
  return (
    <ChoiceCard
      label="What is the complexity?"
      code={item.code}
      options={item.options}
      answer={item.answer}
      why={item.why}
      mono
      review={review}
      today={today}
      onGrade={onGrade}
    />
  );
}

/** A graded multiple choice over a code fragment — the shape shared by the
 * Big-O drill and the spot-the-bug / predict drill. Grading on the first pick
 * is deliberate: a second guess after seeing red is not recall. */
function ChoiceCard({
  label,
  prompt,
  code,
  options,
  answer,
  why,
  mono,
  review,
  today,
  onGrade,
  lang = "java",
}: {
  label: string;
  prompt?: string;
  code: string;
  /** Fence language for `code` — "text" for a model quiz's input sketch. */
  lang?: string;
  options: string[];
  answer: string;
  why: string;
  /** Options are code-ish (complexities) rather than sentences. */
  mono: boolean;
  review: CardReview | undefined;
  today: string;
  onGrade: (right: boolean) => void;
}) {
  const [picked, setPicked] = useState<string | null>(null);
  const right = picked === answer;
  const due = isCardDue(review, today);
  const graded = (review?.reps ?? 0) > 0 || (review?.lapses ?? 0) > 0;

  return (
    <div className="card mb-3">
      <div className="row">
        <span className="dim text-sm">
          {label}
        </span>
        <span className="spacer" />
        {graded && !due && (
          <span className="faint mono text-xs" title="Next review">
            due {review!.due_date}
          </span>
        )}
        {graded && due && (
          <span className="badge c-accent border-accent">
            due
          </span>
        )}
      </div>
      {prompt && (
        <div style={{ margin: "6px 0" }}>
          <InlineMarkdown>{prompt}</InlineMarkdown>
        </div>
      )}
      <Markdown>{"```" + lang + "\n" + code + "```"}</Markdown>
      <div className={mono ? "grid cols-2" : "grid"}>
        {/* Authors list the answer early — across the seed it was never the last
            option — so the authored order would be a tell. Shuffled per snippet,
            deterministically, like every other multiple-choice question. */}
        {optionOrder(code, options.length).map((i) => options[i]).map((opt) => {
          let border: string | undefined;
          if (picked !== null) {
            if (opt === answer) border = "var(--good)";
            else if (opt === picked) border = "var(--bad)";
          }
          return (
            <button
              key={opt}
              style={{ textAlign: "left", borderColor: border, color: border, padding: "8px 10px" }}
              disabled={picked !== null}
              onClick={() => {
                setPicked(opt);
                onGrade(opt === answer);
              }}
            >
              {mono ? <span className="mono">{opt}</span> : <InlineMarkdown>{opt}</InlineMarkdown>}
            </button>
          );
        })}
      </div>
      {picked !== null && (
        <div className="mt-2">
          <strong style={{ color: right ? "var(--good)" : "var(--bad)" }}>
            {right ? "Correct." : mono ? `Not quite — it is ${answer}.` : "Not quite."}
          </strong>
          {!right && !mono && (
            <div className="mt-1">
              The answer: <InlineMarkdown>{answer}</InlineMarkdown>
            </div>
          )}
          <div className="dim mt-1">
            <Markdown>{why}</Markdown>
          </div>
        </div>
      )}
    </div>
  );
}

/** A "work it out by hand" card: type the answer, graded on the first
 * submission (a second try after seeing red is not recall). */
function CalcCard({
  drill,
  review,
  today,
  onGrade,
}: {
  drill: CalcDrill;
  review: CardReview | undefined;
  today: string;
  onGrade: (right: boolean) => void;
}) {
  const [typed, setTyped] = useState("");
  const [result, setResult] = useState<boolean | null>(null);
  const due = isCardDue(review, today);
  const graded = (review?.reps ?? 0) > 0 || (review?.lapses ?? 0) > 0;
  const submit = () => {
    if (result !== null || !typed.trim()) return;
    const right = calcIsCorrect(drill, typed);
    setResult(right);
    onGrade(right);
  };
  return (
    <div className="card mb-3">
      <div className="row">
        <span className="dim text-sm">Work it out</span>
        <span className="spacer" />
        {graded && !due && (
          <span className="faint mono text-xs" title="Next review">
            due {review!.due_date}
          </span>
        )}
        {graded && due && (
          <span className="badge c-accent border-accent">
            due
          </span>
        )}
      </div>
      <div style={{ margin: "6px 0" }}>
        <InlineMarkdown>{drill.prompt}</InlineMarkdown>
      </div>
      {drill.code && <Markdown>{"```java\n" + drill.code + "```"}</Markdown>}
      <div className="row gap-2">
        <input
          className="mono"
          aria-label="Your answer"
          value={typed}
          disabled={result !== null}
          placeholder="Your answer"
          onChange={(e) => setTyped(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submit();
          }}
          style={{ width: 200 }}
        />
        <button onClick={submit} disabled={result !== null || !typed.trim()}>
          Check
        </button>
      </div>
      {result !== null && (
        <div className="mt-2">
          <strong style={{ color: result ? "var(--good)" : "var(--bad)" }}>
            {result ? "Correct." : "Not quite."}
          </strong>{" "}
          {!result && (
            <span>
              The answer: <span className="mono">{drill.answer}</span>
            </span>
          )}
          <div className="dim mt-1">
            <Markdown>{drill.why}</Markdown>
          </div>
        </div>
      )}
    </div>
  );
}

/** One edge case: what it is, the bug it catches, and its input with a copy
 * button — the point is to paste it into the custom-test box, not to read it. */
function EdgeCaseRow({ edge }: { edge: EdgeCase }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(edge.input);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* a clipboard the browser refuses is not worth an error dialog */
    }
  };
  return (
    <div className="cu-pitfall">
      <div className="row">
        <div className="cu-pitfall-symptom">
          <InlineMarkdown>{edge.case}</InlineMarkdown>
        </div>
        <span className="spacer" />
        <span className="faint mono text-xs" title="The problem this input is for">
          {edge.slug}
        </span>
        <button className="ghost" style={{ fontSize: 12, padding: "2px 8px" }} onClick={copy}>
          {copied ? "Copied" : "Copy input"}
        </button>
      </div>
      <div className="dim mb-1">
        <strong>Catches: </strong>
        <InlineMarkdown>{edge.breaks}</InlineMarkdown>
      </div>
      <pre className="mono m-0 text-xs pre-wrap">
        {edge.input}
      </pre>
    </div>
  );
}

/** A worked solution: six fixed steps, numbered, with a way into the problem. */
function WalkthroughBlock({
  walk,
  problemId,
  onOpen,
}: {
  walk: Walkthrough;
  problemId: number | null;
  onOpen: (id: number) => void;
}) {
  return (
    <div className="card">
      <div className="row mb-2">
        <strong>{walk.title}</strong>
        <span className="spacer" />
        {problemId !== null && (
          <button
            className="ghost"
            style={{ fontSize: 12, padding: "2px 8px" }}
            onClick={() => onOpen(problemId)}
          >
            Open the problem →
          </button>
        )}
      </div>
      {walk.steps.map((st, i) => (
        <div key={i} style={{ marginTop: i ? 14 : 0 }}>
          <div className="dim text-sm fw-bold">
            {i + 1}. {st.name}
          </div>
          <Markdown>{st.body}</Markdown>
        </div>
      ))}
    </div>
  );
}

/** One family question: a problem shape, and which variant of this unit it is.
 *
 * Deliberately shaped like `BigOCard` rather than like `Check` — the answer is
 * one of a fixed set, so a multiple choice measures something a "did you
 * remember?" button cannot. The reveal shows the *edit* rather than restating
 * the answer, because the useful correction to "I said longest, it was
 * shortest" is the line that differs, not the label. */
function VariantCard({
  question,
  review,
  today,
  onGrade,
}: {
  question: VariantQuestion;
  review: CardReview | undefined;
  today: string;
  onGrade: (right: boolean) => void;
}) {
  const [picked, setPicked] = useState<string | null>(null);
  const right = picked === question.answerLabel;
  const due = isCardDue(review, today);
  const graded = (review?.reps ?? 0) > 0 || (review?.lapses ?? 0) > 0;

  return (
    <div className="card mb-3">
      <div className="row">
        <span className="dim text-sm">
          The prompt asks for…
        </span>
        <span className="spacer" />
        {graded && !due && (
          <span className="faint mono text-xs" title="Next review">
            due {review!.due_date}
          </span>
        )}
        {graded && due && (
          <span className="badge c-accent border-accent">
            due
          </span>
        )}
      </div>
      <p style={{ margin: "6px 0 12px", fontSize: 15 }}>
        <InlineMarkdown>{question.prompt}</InlineMarkdown>
      </p>
      <div className="grid cols-2">
        {question.options.map((opt) => {
          let border: string | undefined;
          if (picked !== null) {
            if (opt === question.answerLabel) border = "var(--good)";
            else if (opt === picked) border = "var(--bad)";
          }
          return (
            <button
              key={opt}
              style={{ textAlign: "left", borderColor: border, color: border, padding: "8px 10px" }}
              disabled={picked !== null}
              onClick={() => {
                setPicked(opt);
                onGrade(opt === question.answerLabel);
              }}
            >
              {opt}
            </button>
          );
        })}
      </div>
      {picked !== null && (
        <div className="mt-2">
          <strong style={{ color: right ? "var(--good)" : "var(--bad)" }}>
            {right ? "Correct." : `Not quite — it is ${question.answerLabel}.`}
          </strong>
          <div className="dim mt-1">
            <InlineMarkdown>{question.change}</InlineMarkdown>
          </div>
          {question.gotcha && (
            <div className="cu-var-gotcha mt-2">
              <span className="cu-var-gotcha-tag">watch</span>{" "}
              <InlineMarkdown>{question.gotcha}</InlineMarkdown>
            </div>
          )}
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
    <div className="card mb-2">
      <div className="row items-start">
        <div style={{ flex: 1, paddingTop: 4 }}>
          <InlineMarkdown>{check.q}</InlineMarkdown>
        </div>
        {graded && !due && (
          <span className="faint mono" style={{ fontSize: 12, paddingTop: 6 }} title="Next review">
            due {review!.due_date}
          </span>
        )}
        {graded && due && (
          <span className="badge c-accent border-accent mt-1">
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
          <div className="row mt-2 gap-2">
            <button
              className="ghost border-bad c-bad"
              onClick={() => {
                onGrade(false);
                setShow(false);
              }}
            >
              Forgot
            </button>
            <button
              className="ghost border-good c-good"
              onClick={() => {
                onGrade(true);
                setShow(false);
              }}
            >
              Had it
            </button>
            <span className="spacer" />
            {review && review.reps > 0 && (
              <span className="faint text-xs">
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
