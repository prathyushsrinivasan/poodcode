import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { CardReview, Concept, Trace, UnitCheck } from "../types";
import { Markdown, InlineMarkdown } from "../components/Markdown";
import { Section, useCollapse } from "../components/Collapsible";
import { ClickableRow, Confidence, DiffBadge, Empty } from "../components/common";
import { StatusBadge, UnitProgress, useCurriculumData } from "../components/CurriculumData";
import { findUnit, neighbours, type HydratedRung } from "../lib/curriculum";
import { checkCardId, isCardDue, todayISO, unitChecks } from "../lib/dsaReview";

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
  const { data, setSkipped } = useCurriculumData();
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const nav = useNavigate();
  const { isOpen, toggle } = useCollapse(`dsa-unit:${key}`, true);

  useEffect(() => {
    api.concepts().then(setConcepts).catch(() => {});
  }, []);

  // Self-check scheduling lives in the same `card_reviews` table as the Learn
  // tab's decks, so this is one read and no new storage.
  useEffect(() => {
    api
      .cardReviews()
      .then((rs) => setReviews(new Map(rs.map((r) => [r.card_id, r]))))
      .catch(() => {});
  }, []);

  const gradeCheck = useCallback(async (index: number, remembered: boolean) => {
    const id = checkCardId(key, index);
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
  }, [key]);

  if (!data) return <div className="empty" style={{ paddingTop: "20vh" }}>Loading…</div>;

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
  const { prev, next } = neighbours(data, key);
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
        <button className="ghost" onClick={() => nav("/library")}>
          ← Curriculum
        </button>
        <span className="spacer" />
        {prev && (
          <button className="ghost" onClick={() => nav(`/library/unit/${prev.unit.key}`)}>
            ← {prev.unit.title}
          </button>
        )}
        {next && (
          <button className="ghost" onClick={() => nav(`/library/unit/${next.unit.key}`)}>
            {next.unit.title} →
          </button>
        )}
      </div>

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

      <Section title="🎯 Why this exists" open={isOpen("why")} onToggle={() => toggle("why")}>
        <Markdown>{u.why}</Markdown>
      </Section>

      <Section title="🧠 The model" open={isOpen("model")} onToggle={() => toggle("model")}>
        <Markdown>{u.model}</Markdown>
      </Section>

      {u.internals && (
        <Section
          title="🔬 How it works underneath"
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
        <Section title="⏱️ What it costs" open={isOpen("costs")} onToggle={() => toggle("costs")}>
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
          open={isOpen("pitfalls")}
          onToggle={() => toggle("pitfalls")}
          meta={<span className="dim mono">{u.pitfalls.length}</span>}
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
          open={isOpen("build")}
          onToggle={() => toggle("build")}
        >
          <Markdown>{u.build_it}</Markdown>
        </Section>
      )}

      {u.checks.length > 0 && (
        <Section
          title="✅ Self-check"
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

      {u.interview && (
        <Section
          title="💼 In an interview"
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
              return (
                <tr key={item.slug} onClick={() => onOpen(p.id)}>
                  <td style={{ width: 28 }}>{solved ? "✅" : p.solved_status === "attempted" ? "◐" : "○"}</td>
                  <td>
                    <strong className={solved ? "dim" : ""}>{p.title}</strong>
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
