import { useCallback, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { BigOItem, CardReview, Concept, Trace, UnitCheck } from "../types";
import { Markdown, InlineMarkdown } from "../components/Markdown";
import { Section, useCollapse } from "../components/Collapsible";
import { ClickableRow, Confidence, DiffBadge, Empty } from "../components/common";
import { UnitSkeleton } from "../components/Skeleton";
import { StatusBadge, UnitProgress, useCurriculumData } from "../components/CurriculumData";
import {
  findUnit,
  neighbours,
  rememberLastUnit,
  type HydratedRung,
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

/**
 * One unit of the DSA curriculum: a technique, taught, then drilled.
 *
 * The page is the five beats the generator authors, in the order they are
 * useful — why the technique exists, how it works, the code shape to memorise,
 * the *signals* that should make you reach for it, what it costs, what goes
 * wrong, and then the problems. Everything above the ladder is there so that
 * the ladder is not just a list of links.
 *
 * Sections are collapsible and remembered, because the second visit to a unit
 * wants the pitfalls and the ladder, not the motivation you have already read.
 */
export default function CurriculumUnit() {
  const { key = "" } = useParams();
  const { data, error, setSkipped } = useCurriculumData();
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const nav = useNavigate();
  // The third argument is a shared namespace: a section with no per-unit
  // opinion falls back to the preference for its *type*, so "always show me
  // pitfalls, never the motivation" is stated once rather than 33 times.
  const { isOpen, toggle, open, toggleEverywhere } = useCollapse(
    `dsa-unit:${key}`,
    true,
    "dsa-section"
  );
  const { hash } = useLocation();
  // Refs so the key handler is registered once rather than re-bound on every
  // data change — the listener reads the latest values instead of closing over
  // stale ones.
  const dataRef = useRef(data);
  dataRef.current = data;
  const keyRef = useRef(key);
  keyRef.current = key;

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

  const gradeCheck = useCallback(
    (index: number, remembered: boolean) => grade(checkCardId(key, index), remembered),
    [grade, key]
  );
  const gradeBigO = useCallback(
    (index: number, right: boolean) => grade(bigoCardId(key, index), right),
    [grade, key]
  );

  /**
   * Honour `#pitfalls` and friends: force that section open, then scroll to it.
   *
   * Forcing it open matters — sections remember their collapsed state, so
   * arriving at a link and finding the section shut because you closed it last
   * week is the link not working. Waits a frame so the section body has rendered
   * before we measure where to scroll.
   */
  useEffect(() => {
    const target = hash.replace(/^#/, "");
    if (!target || !data) return;
    open(target);
    const id = requestAnimationFrame(() => {
      document.getElementById(target)?.scrollIntoView({ block: "start", behavior: "smooth" });
    });
    return () => cancelAnimationFrame(id);
  }, [hash, data, open]);

  /**
   * `[` / `]` page between units, `g l` goes back to the curriculum.
   *
   * The prev/next buttons already existed and nothing was bound to them. Skipped
   * while focus is in an input or a Monaco editor, because `[` is a character
   * there and stealing it would be worse than the shortcut is good.
   */
  useEffect(() => {
    let gPending = false;
    const typing = (el: EventTarget | null) => {
      const node = el as HTMLElement | null;
      if (!node) return false;
      const tag = node.tagName;
      return (
        tag === "INPUT" ||
        tag === "TEXTAREA" ||
        tag === "SELECT" ||
        node.isContentEditable ||
        !!node.closest?.(".monaco-editor")
      );
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey || typing(e.target)) return;
      if (gPending && e.key === "l") {
        gPending = false;
        e.preventDefault();
        nav("/library");
        return;
      }
      gPending = e.key === "g";
      if (e.key === "[" || e.key === "]") {
        const data0 = dataRef.current;
        if (!data0) return;
        const n = neighbours(data0, keyRef.current);
        const to = e.key === "[" ? n.prev : n.next;
        if (to) {
          e.preventDefault();
          nav(`/library/unit/${to.unit.key}`);
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [nav]);

  // `error` used to be ignored here, so a failed fetch left the page saying
  // "Loading…" forever with no explanation. Library handled it; this did not.
  if (error) {
    return (
      <div className="page page-wide">
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
      <div className="page page-wide">
        <Empty icon="🤔" text="No such unit." />
        <button onClick={() => nav("/library")}>Back to the curriculum</button>
      </div>
    );
  }

  const u = hydrated.unit;
  const today = todayISO();
  const checkStats = unitChecks(hydrated, reviews, today);
  const bigoStats = cardStats(u.bigo.map((_, i) => bigoCardId(key, i)), reviews, today);
  const { prev, next } = neighbours(data, key);
  const stageIndex = data.stages.findIndex((s) => s.units.some((x) => x.unit.key === key));
  const stage =
    stageIndex < 0
      ? null
      : {
          ...data.stages[stageIndex],
          number: stageIndex + 1,
          count: data.stages.length,
          unitNumber:
            data.stages[stageIndex].units.findIndex((x) => x.unit.key === key) + 1,
          unitCount: data.stages[stageIndex].units.length,
        };
  // For a stale unit, "re-practise" means a problem you already solved — the
  // point is to prove the technique is still there, not to meet a new one.
  const firstSolved =
    hydrated.rungs
      .flatMap((r) => r.items)
      .find((i) => i.problem?.solved_status === "solved")?.problem ?? null;
  const conceptName = (k: string) => concepts.find((c) => c.key === k)?.name ?? k;
  const conceptWhat = (k: string) => concepts.find((c) => c.key === k)?.what ?? "";

  return (
    <div className="page page-wide">
      <div className="row" style={{ marginBottom: 4 }}>
        <button className="ghost" onClick={() => nav("/library")} title="g l">
          ← Curriculum
        </button>
        <span className="spacer" />
        {prev && (
          <button
            className="ghost"
            onClick={() => nav(`/library/unit/${prev.unit.key}`)}
            title="[ — previous unit"
          >
            ← {prev.unit.title}
          </button>
        )}
        {next && (
          <button
            className="ghost"
            onClick={() => nav(`/library/unit/${next.unit.key}`)}
            title="] — next unit"
          >
            {next.unit.title} →
          </button>
        )}
      </div>

      {/* Where am I? The header was icon + title + tagline, so you could not
          tell stage 2 from stage 5 without going back. */}
      {stage && (
        <p className="faint" style={{ fontSize: 12, margin: "0 0 2px" }}>
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              nav("/library");
            }}
          >
            {stage.icon} Stage {stage.number} of {stage.count} · {stage.title}
          </a>
          {" · "}
          unit {stage.unitNumber} of {stage.unitCount}
        </p>
      )}

      <div className="row">
        <h1 className="page-title" style={{ marginBottom: 0 }}>
          {u.icon} {u.title}
        </h1>
        <span className="spacer" />
        <StatusBadge
          status={hydrated.status}
          stale={hydrated.stale}
          skipped={hydrated.skipped}
        />
        <button
          className="ghost"
          title={
            hydrated.skipped
              ? "Put this unit back in the ladder"
              : "Counts as cleared for what unlocks next, without pretending you solved it here"
          }
          onClick={() => setSkipped([key], !hydrated.skipped)}
        >
          {hydrated.skipped ? "Un-skip" : "I know this — skip it"}
        </button>
      </div>
      <p className="page-sub">{u.tagline}</p>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row">
          <span className="dim">
            {hydrated.solved} of {hydrated.total} problems solved
          </span>
          <span className="spacer" />
          {hydrated.next && (
            <button className="primary" onClick={() => nav(`/solve/${hydrated.next!.id}`)}>
              Next problem: {hydrated.next.title} →
            </button>
          )}
        </div>
        <UnitProgress solved={hydrated.solved} total={hydrated.total} stale={hydrated.stale} />
        {hydrated.stale && (
          <p className="faint" style={{ fontSize: 12, marginTop: 10, marginBottom: 0 }}>
            You cleared this {hydrated.lastPractisedDays} days ago and have not touched it
            since — past the {hydrated.staleAfterDays}-day window a cleared unit buys. Green
            and <em>remembered</em> are not the same thing.{" "}
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
              <> · {checkStats.due} self-check{checkStats.due === 1 ? "" : "s"} due below.</>
            )}
          </p>
        )}
        {hydrated.unmetPrereqTitles.length > 0 && (
          <p className="faint" style={{ fontSize: 12, marginTop: 10, marginBottom: 0 }}>
            This unit builds on <strong>{hydrated.unmetPrereqTitles.join(", ")}</strong>, which
            you have not finished. Nothing is locked — but if something here reads as a leap,
            that is where the missing step is.
          </p>
        )}
      </div>

      <Section
        title="🎯 Why this exists"
        id="why"
        open={isOpen("why")}
        onToggle={() => toggle("why")}
        meta={<EverywhereToggle open={isOpen("why")} onSet={(v) => toggleEverywhere("why", v)} />}
      >
        <Markdown>{u.why}</Markdown>
      </Section>

      <Section title="🧠 The model" id="model" open={isOpen("model")} onToggle={() => toggle("model")}>
        <Markdown>{u.model}</Markdown>
      </Section>

      {u.internals && (
        <Section
          title="🔬 How it works underneath"
          id="internals"
          open={isOpen("internals")}
          onToggle={() => toggle("internals")}
        >
          <p className="dim" style={{ marginTop: 0 }}>
            The costs above are consequences of a layout. Quoting them without it is
            memorisation — this is where they stop being trivia.
          </p>
          <Markdown>{u.internals}</Markdown>
        </Section>
      )}

      {u.signals.length > 0 && (
        <Section
          title="🔔 Signals — when to reach for this"
          id="signals"
          open={isOpen("signals")}
          onToggle={() => toggle("signals")}
          meta={<span className="dim mono">{u.signals.length}</span>}
        >
          <p className="dim" style={{ marginTop: 0 }}>
            The routing table. Reading a prompt and landing on the technique without
            deriving it is most of what separates fast solvers from slow ones.
          </p>
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
                <tr key={i}>
                  <td><InlineMarkdown>{s.when}</InlineMarkdown></td>
                  <td><strong><InlineMarkdown>{s.reach_for}</InlineMarkdown></strong></td>
                  <td className="dim"><InlineMarkdown>{s.why}</InlineMarkdown></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      )}

      {u.skeletons.length > 0 && (
        <Section
          title="⌨️ The playbook"
          id="skeletons"
          open={isOpen("skeletons")}
          onToggle={() => toggle("skeletons")}
          meta={<span className="dim mono">{u.skeletons.length}</span>}
        >
          <p className="dim" style={{ marginTop: 0 }}>
            Copy each of these out by hand once. Patterns are muscle memory, and
            reading them is not how that gets built.
          </p>
          {u.skeletons.map((s, i) => (
            <div key={i} style={{ marginBottom: 18 }}>
              <div className="row">
                <strong>{s.name}</strong>
                {s.when && <span className="dim"> — {s.when}</span>}
              </div>
              <Markdown>{"```java\n" + s.code + "```"}</Markdown>
              {s.note && (
                <p className="faint" style={{ fontSize: 12, marginTop: -6 }}>
                  <InlineMarkdown>{s.note}</InlineMarkdown>
                </p>
              )}
            </div>
          ))}
        </Section>
      )}

      {u.traces.length > 0 && (
        <Section
          title="🎞️ Worked traces"
          id="traces"
          open={isOpen("traces")}
          onToggle={() => toggle("traces")}
          meta={<span className="dim mono">{u.traces.length}</span>}
        >
          <p className="dim" style={{ marginTop: 0 }}>
            The state, one row per step. Everything hard here is state changing over
            time, which a table shows in one glance and prose only asserts.
          </p>
          {u.traces.map((t, i) => (
            <TraceTable key={i} trace={t} />
          ))}
        </Section>
      )}

      {u.costs.length > 0 && (
        <Section title="⏱️ What it costs" id="costs" open={isOpen("costs")} onToggle={() => toggle("costs")}>
          <table className="data">
            <thead>
              <tr>
                <th>Operation</th>
                <th style={{ width: 140 }}>Time</th>
                <th style={{ width: 140 }}>Space</th>
                <th>Note</th>
              </tr>
            </thead>
            <tbody>
              {u.costs.map((c, i) => (
                <tr key={i}>
                  <td><InlineMarkdown>{c.op}</InlineMarkdown></td>
                  <td className="mono">{c.time}</td>
                  <td className="mono">{c.space}</td>
                  <td className="dim"><InlineMarkdown>{c.note}</InlineMarkdown></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      )}

      {u.pitfalls.length > 0 && (
        <Section
          title="⚠️ Pitfalls, by symptom"
          id="pitfalls"
          open={isOpen("pitfalls")}
          onToggle={() => toggle("pitfalls")}
          meta={
            <>
              <EverywhereToggle
                open={isOpen("pitfalls")}
                onSet={(v) => toggleEverywhere("pitfalls", v)}
              />
              <span className="dim mono">{u.pitfalls.length}</span>
            </>
          }
        >
          <p className="dim" style={{ marginTop: 0 }}>
            Indexed by what you will actually see, so a failing run is searchable.
          </p>
          {u.pitfalls.map((p, i) => (
            <div key={i} className="hint" style={{ marginBottom: 10 }}>
              <div className="hint-label">{p.symptom}</div>
              <div className="dim" style={{ marginBottom: 4 }}>
                <InlineMarkdown>{p.cause}</InlineMarkdown>
              </div>
              <div>
                <strong>Fix: </strong>
                <InlineMarkdown>{p.fix}</InlineMarkdown>
              </div>
            </div>
          ))}
        </Section>
      )}

      {u.lessons.length > 0 && (
        <Section
          title="📘 Go deeper in Learn"
          id="lessons"
          open={isOpen("lessons")}
          onToggle={() => toggle("lessons")}
          meta={<span className="dim mono">{u.lessons.length}</span>}
        >
          <p className="dim" style={{ marginTop: 0 }}>
            This page is the map. These are the terrain — full lessons with
            derivations, worked examples and drills.
          </p>
          {u.lessons.map((k) => (
            <ClickableRow
              key={k}
              onActivate={() => nav(`/learn/${k}`)}
              className="row"
              style={{ padding: "8px 10px", borderRadius: 6, gap: 8 }}
              title={`Open the ${conceptName(k)} lesson`}
            >
              <span>📖</span>
              <strong>{conceptName(k)}</strong>
              <span className="dim">— {conceptWhat(k)}</span>
            </ClickableRow>
          ))}
        </Section>
      )}

      <Section
        title="🧗 Practice"
        id="ladder"
        open={isOpen("ladder")}
        onToggle={() => toggle("ladder")}
        meta={
          <span className="dim mono">
            {hydrated.solved}/{hydrated.total}
          </span>
        }
      >
        <p className="dim" style={{ marginTop: 0 }}>
          Work down the page. A rung is a group of problems drilling the same twist —
          when it stops being interesting, move to the next one. You do not have to
          clear a rung to move on.
        </p>
        {hydrated.rungs.map((r, i) => (
          <RungBlock key={i} rung={r} onOpen={(id) => nav(`/solve/${id}`)} />
        ))}
      </Section>

      {u.build_it && (
        <Section
          title="🔨 Build it yourself"
          id="build"
          open={isOpen("build")}
          onToggle={() => toggle("build")}
        >
          <Markdown>{u.build_it}</Markdown>
        </Section>
      )}

      {u.checks.length > 0 && (
        <Section
          title="✅ Self-check"
          id="checks"
          open={isOpen("checks")}
          onToggle={() => toggle("checks")}
          meta={
            <span className="dim mono">
              {checkStats.due > 0 ? `${checkStats.due} due · ` : ""}
              {checkStats.started}/{checkStats.total}
            </span>
          }
        >
          <p className="dim" style={{ marginTop: 0 }}>
            Answer out loud, reveal, then say whether you had it. Each of these is
            a scheduled card — grading it here is what makes it come back in a
            month instead of never.
          </p>
          {u.checks.map((c, i) => (
            <Check
              key={i}
              check={c}
              review={reviews.get(checkCardId(key, i))}
              today={today}
              onGrade={(remembered) => gradeCheck(i, remembered)}
            />
          ))}
        </Section>
      )}

      {u.bigo.length > 0 && (
        <Section
          title="⏳ Price the snippet"
          id="bigo"
          open={isOpen("bigo")}
          onToggle={() => toggle("bigo")}
          meta={
            <span className="dim mono">
              {bigoStats.due > 0 ? `${bigoStats.due} due · ` : ""}
              {bigoStats.started}/{bigoStats.total}
            </span>
          }
        >
          <p className="dim" style={{ marginTop: 0 }}>
            You can solve every problem in this unit without once <em>stating</em> a
            complexity, which is the opposite of the skill. Read, price, then check —
            these are scheduled like the self-checks.
          </p>
          {u.bigo.map((b, i) => (
            <BigOCard
              key={i}
              item={b}
              review={reviews.get(bigoCardId(key, i))}
              today={today}
              onGrade={(right) => gradeBigO(i, right)}
            />
          ))}
        </Section>
      )}

      {u.interview && (
        <Section
          title="💼 In an interview"
          id="interview"
          open={isOpen("interview")}
          onToggle={() => toggle("interview")}
        >
          <Markdown>{u.interview}</Markdown>
        </Section>
      )}

      {u.next_up && (
        <div className="card" style={{ marginTop: 16 }}>
          <div className="io-label">What comes next</div>
          <Markdown>{u.next_up}</Markdown>
          {next && (
            <button className="primary" onClick={() => nav(`/library/unit/${next.unit.key}`)}>
              {next.unit.icon} {next.unit.title} →
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function RungBlock({ rung, onOpen }: { rung: HydratedRung; onOpen: (id: number) => void }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div className="row">
        <strong className={rung.optional ? "dim" : ""}>{rung.title}</strong>
        {rung.optional && (
          <span
            className="badge"
            style={{ color: "var(--text-faint)", borderColor: "var(--text-faint)" }}
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
        <span className="dim mono">
          {rung.solved}/{rung.total}
        </span>
      </div>
      <p className="dim" style={{ margin: "2px 0 8px" }}>
        {rung.purpose}
      </p>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="data">
          <tbody>
            {rung.items.map((item) => {
              const p = item.problem;
              if (!p) {
                return (
                  <tr key={item.slug}>
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
                  <td style={{ width: 28 }}>{solved ? "✅" : p.solved_status === "attempted" ? "◐" : "○"}</td>
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
                  <td style={{ width: 90 }}>
                    <DiffBadge d={p.difficulty} />
                  </td>
                  <td style={{ width: 100 }} onClick={(e) => e.stopPropagation()}>
                    <Confidence value={p.confidence} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/** A trace renders as a table with a takeaway, because the point of a trace is
 * never the table — it is the sentence the table makes obvious. State columns
 * are monospaced so successive rows line up and the change is visible. */
function TraceTable({ trace }: { trace: Trace }) {
  return (
    <div style={{ marginBottom: 22 }}>
      <strong>{trace.title}</strong>
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
            {trace.rows.map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  <td key={j} className={j === 0 ? "" : "mono"} style={{ whiteSpace: "nowrap" }}>
                    <InlineMarkdown>{cell}</InlineMarkdown>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {trace.takeaway && (
        <p className="dim" style={{ marginTop: 8 }}>
          <InlineMarkdown>{trace.takeaway}</InlineMarkdown>
        </p>
      )}
    </div>
  );
}

/** "Do this on every unit" — sets the shared, section-type preference.
 *
 * Collapse state is per unit, which is right for a one-off and wrong for a
 * standing preference: "I always want pitfalls open and the motivation closed"
 * had to be re-expressed 33 times. This writes the shared key instead, and a
 * later per-unit toggle still wins over it. */
function EverywhereToggle({ open, onSet }: { open: boolean; onSet: (open: boolean) => void }) {
  return (
    <button
      className="ghost"
      style={{ fontSize: 11, padding: "1px 6px" }}
      title={
        open
          ? "Keep this section open on every unit"
          : "Keep this section closed on every unit"
      }
      onClick={(e) => {
        e.stopPropagation(); // the header itself is the collapse toggle
        onSet(open);
      }}
    >
      {open ? "open everywhere" : "closed everywhere"}
    </button>
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
    <div className="card" style={{ marginBottom: 12, background: "var(--bg-elev-2)" }}>
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
        {item.options.map((opt) => {
          let border: string | undefined;
          if (picked !== null) {
            if (opt === item.answer) border = "var(--good)";
            else if (opt === picked) border = "var(--bad)";
          }
          return (
            <button
              key={opt}
              className="ghost"
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
  onGrade,
}: {
  check: UnitCheck;
  review: CardReview | undefined;
  today: string;
  onGrade: (remembered: boolean) => void;
}) {
  const [show, setShow] = useState(false);
  const due = isCardDue(review, today);
  const graded = (review?.reps ?? 0) > 0 || (review?.lapses ?? 0) > 0;

  return (
    <div className="card" style={{ marginBottom: 8, background: "var(--bg-elev-2)" }}>
      <div className="row">
        <div>
          <InlineMarkdown>{check.q}</InlineMarkdown>
        </div>
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
        <button className="ghost" onClick={() => setShow((s) => !s)}>
          {show ? "Hide" : "Reveal"}
        </button>
      </div>
      {show && (
        <>
          <div className="dim" style={{ marginTop: 8 }}>
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
