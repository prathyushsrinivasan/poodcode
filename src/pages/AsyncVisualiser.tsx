// Async, made visible (TS_MASTERY_ROADMAP M6-01, M6-02):
//   * Event loop — step through a snippet and watch the call stack, the
//     microtask queue, the timer queue and the output change.
//   * Promise combinators — lay promises on a timeline and see when (and with
//     what) Promise.all / allSettled / race / any settle.
// Both are models (lib/eventLoop.ts), proven against the real engine by
// lib/eventLoop.test.ts.

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  SCENARIOS,
  settle,
  simulate,
  type Combinator,
  type TimedPromise,
} from "../lib/eventLoop";

export default function AsyncVisualiser() {
  const [tab, setTab] = useState<"loop" | "combinators">("loop");
  return (
    <div className="page">
      <h1 className="page-title">🔁 Async, step by step</h1>
      <p className="page-sub">
        Why does <code>setTimeout(f, 0)</code> run last? When does <code>Promise.all</code> give up? Step through it.
        For Week 26 of <Link to="/mastery">the Mastery programme</Link>; try your own snippets in the{" "}
        <Link to="/playground/ts">playground</Link>.
      </p>
      <div className="row" style={{ gap: 6, marginBottom: 12 }} role="tablist">
        <button className={tab === "loop" ? "" : "ghost"} onClick={() => setTab("loop")} role="tab" aria-selected={tab === "loop"}>
          Event loop
        </button>
        <button
          className={tab === "combinators" ? "" : "ghost"}
          onClick={() => setTab("combinators")}
          role="tab"
          aria-selected={tab === "combinators"}
        >
          Promise combinators
        </button>
      </div>
      {tab === "loop" ? <EventLoop /> : <Combinators />}
    </div>
  );
}

function EventLoop() {
  const [key, setKey] = useState(SCENARIOS[0]!.key);
  const scenario = SCENARIOS.find((s) => s.key === key) ?? SCENARIOS[0]!;
  const steps = useMemo(() => simulate(scenario.program), [scenario]);
  const [i, setI] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [guess, setGuess] = useState("");
  const step = steps[Math.min(i, steps.length - 1)]!;
  const done = i >= steps.length - 1;

  useEffect(() => {
    setI(0);
    setPlaying(false);
    setGuess("");
  }, [key]);

  useEffect(() => {
    if (!playing) return;
    if (done) {
      setPlaying(false);
      return;
    }
    const t = setTimeout(() => setI((n) => n + 1), 900);
    return () => clearTimeout(t);
  }, [playing, i, done]);

  const guessLines = guess.split("\n").map((l) => l.trim()).filter(Boolean);
  const finalOut = steps[steps.length - 1]!.output;
  const guessedRight = guessLines.length > 0 && guessLines.join("\n") === finalOut.join("\n");

  return (
    <>
      <div className="row" style={{ gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
        {SCENARIOS.map((s) => (
          <button key={s.key} className={s.key === key ? "" : "ghost"} onClick={() => setKey(s.key)}>
            {s.title}
          </button>
        ))}
      </div>
      <p style={{ marginTop: 0 }}>{scenario.lesson}</p>

      <div className="loop-grid">
        <div>
          <div className="io-label">Code</div>
          <pre className="io-block loop-code">
            {scenario.code.split("\n").map((l, n) => (
              <div key={n} className={step.line === n + 1 ? "loop-line-now" : undefined}>
                <span className="oc-no">{n + 1}</span>
                {l || " "}
              </div>
            ))}
          </pre>
          <div className="io-label" style={{ marginTop: 10 }}>
            Predict first — what does it print, line by line?
          </div>
          <textarea
            value={guess}
            onChange={(e) => setGuess(e.target.value)}
            placeholder="Write your prediction before stepping."
            style={{ width: "100%", minHeight: 70, fontFamily: "var(--font-mono)", fontSize: 12 }}
          />
          {done && guessLines.length > 0 && (
            <p className="quiz-note" style={{ color: guessedRight ? "var(--good)" : "var(--bad)" }}>
              {guessedRight ? "✓ Exactly right." : "Not quite — compare your lines with the output on the right."}
            </p>
          )}
        </div>

        <div>
          <div className="loop-boxes">
            <LoopBox title="Call stack" items={[...step.stack].reverse()} empty="empty" hint="top of stack first" />
            <LoopBox title="Microtask queue" items={step.microtasks} empty="empty" hint="runs next, all of it" />
            <LoopBox
              title="Task queue (timers)"
              items={step.tasks.map((t) => `${t.label} · due ${t.due} ms`)}
              empty="empty"
              hint="one per loop turn"
            />
            <LoopBox title="Output" items={step.output} empty="nothing yet" mono />
          </div>
          <div className="card loop-note">
            <span className="badge">
              step {i + 1}/{steps.length} · {step.clock} ms
            </span>{" "}
            {step.note}
          </div>
          <div className="row" style={{ gap: 6, marginTop: 8 }}>
            <button className="ghost" onClick={() => setI(0)} disabled={i === 0}>
              ⏮ Reset
            </button>
            <button className="ghost" onClick={() => setI((n) => Math.max(0, n - 1))} disabled={i === 0}>
              ◀ Back
            </button>
            <button onClick={() => setI((n) => Math.min(steps.length - 1, n + 1))} disabled={done}>
              Step ▶
            </button>
            <button className="ghost" onClick={() => (done ? (setI(0), setPlaying(true)) : setPlaying((p) => !p))}>
              {playing ? "⏸ Pause" : "▶ Play"}
            </button>
            <button className="ghost" onClick={() => setI(steps.length - 1)} disabled={done}>
              ⏭ End
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function LoopBox({
  title,
  items,
  empty,
  hint,
  mono,
}: {
  title: string;
  items: string[];
  empty: string;
  hint?: string;
  mono?: boolean;
}) {
  return (
    <div className="card loop-box">
      <div className="io-label">
        {title} {hint && <span className="dim" style={{ textTransform: "none" }}>· {hint}</span>}
      </div>
      {items.length === 0 ? (
        <div className="dim quiz-note">{empty}</div>
      ) : (
        items.map((it, k) => (
          <div key={k} className={`loop-item ${mono ? "mono" : ""}`}>
            {it}
          </div>
        ))
      )}
    </div>
  );
}

const DEFAULT_ITEMS: TimedPromise[] = [
  { label: "users", ms: 120, ok: true },
  { label: "orders", ms: 60, ok: false },
  { label: "prices", ms: 200, ok: true },
];

const COMBINATORS: { key: Combinator; note: string }[] = [
  { key: "all", note: "every value, or the first rejection — fail fast" },
  { key: "allSettled", note: "waits for everything; never rejects" },
  { key: "race", note: "the first to settle, either way — the timeout pattern" },
  { key: "any", note: "the first success; rejects only if all do" },
];

function Combinators() {
  const [items, setItems] = useState<TimedPromise[]>(DEFAULT_ITEMS);
  const [comb, setComb] = useState<Combinator>("all");
  const s = settle(comb, items);
  const max = Math.max(50, ...items.map((p) => p.ms), s.at ?? 0) * 1.1;
  const W = 640;
  const rowH = 28;
  const x = (ms: number) => 110 + (ms / max) * (W - 130);
  const H = (items.length + 2) * rowH + 20;
  const color = (ok: boolean) => (ok ? "var(--good)" : "var(--bad)");

  const update = (k: number, patch: Partial<TimedPromise>) =>
    setItems(items.map((p, i) => (i === k ? { ...p, ...patch } : p)));

  return (
    <>
      <div className="row" style={{ gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
        {COMBINATORS.map((c) => (
          <button key={c.key} className={c.key === comb ? "" : "ghost"} onClick={() => setComb(c.key)} title={c.note}>
            Promise.{c.key}
          </button>
        ))}
      </div>
      <p className="dim quiz-note" style={{ marginTop: 0 }}>
        <code>Promise.{comb}</code> — {COMBINATORS.find((c) => c.key === comb)!.note}.
      </p>

      <div className="card" style={{ overflowX: "auto" }}>
        <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={`Timeline for Promise.${comb}`}>
          {items.map((p, k) => (
            <g key={k}>
              <text x={4} y={k * rowH + 24} className="timeline-label">
                {p.label}
              </text>
              <rect x={x(0)} y={k * rowH + 12} width={Math.max(2, x(p.ms) - x(0))} height={14} rx={4} fill={color(p.ok)} opacity={0.35} />
              <circle cx={x(p.ms)} cy={k * rowH + 19} r={6} fill={color(p.ok)} />
              <text x={x(p.ms) + 10} y={k * rowH + 24} className="timeline-label">
                {p.ok ? "fulfils" : "rejects"} @ {p.ms} ms
              </text>
            </g>
          ))}
          <g>
            <text x={4} y={(items.length + 0.5) * rowH + 24} className="timeline-label timeline-strong">
              Promise.{comb}
            </text>
            {s.at !== null ? (
              <>
                <rect
                  x={x(0)}
                  y={(items.length + 0.5) * rowH + 12}
                  width={Math.max(2, x(s.at) - x(0))}
                  height={14}
                  rx={4}
                  fill={s.outcome === "fulfilled" ? "var(--good)" : "var(--bad)"}
                  opacity={0.6}
                />
                <line
                  x1={x(s.at)}
                  x2={x(s.at)}
                  y1={4}
                  y2={H - 6}
                  stroke="var(--accent)"
                  strokeDasharray="4 4"
                />
              </>
            ) : (
              <text x={x(0)} y={(items.length + 0.5) * rowH + 24} className="timeline-label">
                pending forever
              </text>
            )}
          </g>
        </svg>
        <p style={{ margin: "6px 0 0" }}>
          {s.at === null ? (
            <>It never settles: {s.value}.</>
          ) : (
            <>
              <strong style={{ color: s.outcome === "fulfilled" ? "var(--good)" : "var(--bad)" }}>{s.outcome}</strong> at{" "}
              {s.at} ms with <code>{s.value}</code>.
            </>
          )}
        </p>
      </div>

      <div className="io-label">Promises</div>
      {items.map((p, k) => (
        <div key={k} className="row" style={{ gap: 8, alignItems: "center", margin: "4px 0" }}>
          <input
            value={p.label}
            onChange={(e) => update(k, { label: e.target.value.replace(/\s/g, "") || `p${k + 1}` })}
            style={{ width: 110, fontFamily: "var(--font-mono)" }}
            aria-label="Label"
          />
          <input
            type="number"
            min={0}
            max={5000}
            value={p.ms}
            onChange={(e) => update(k, { ms: Math.max(0, Math.min(5000, Number(e.target.value) || 0)) })}
            style={{ width: 90 }}
            aria-label="Delay in ms"
          />
          <span className="dim quiz-note">ms</span>
          <button className="ghost" onClick={() => update(k, { ok: !p.ok })} style={{ color: color(p.ok) }}>
            {p.ok ? "fulfils" : "rejects"}
          </button>
          <button className="ghost" onClick={() => setItems(items.filter((_, i) => i !== k))} aria-label={`Remove ${p.label}`}>
            ×
          </button>
        </div>
      ))}
      <button
        className="ghost"
        onClick={() => setItems([...items, { label: `p${items.length + 1}`, ms: 100, ok: true }])}
        disabled={items.length >= 8}
      >
        + promise
      </button>
    </>
  );
}
