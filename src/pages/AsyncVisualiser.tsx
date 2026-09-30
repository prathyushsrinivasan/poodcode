// Step by step (TS_MASTERY_ROADMAP M2-02, M2-03, M6-01, M6-02):
//   * Call stack — recursion and closures, frame by frame, with each frame's
//     locals and what closures captured (lib/callStack.ts).
//   * Array pipeline — a filter/map/reduce chain with every intermediate array
//     (lib/pipeline.ts).
//   * Event loop — step through a snippet and watch the call stack, the
//     microtask queue, the timer queue and the output change.
//   * Promise combinators — lay promises on a timeline and see when (and with
//     what) Promise.all / allSettled / race / any settle.
// Both are models (lib/eventLoop.ts), proven against the real engine by
// lib/eventLoop.test.ts.

import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { STACK_SCENARIOS, traceScenario } from "../lib/callStack";
import {
  PIPE_METHODS,
  PIPE_PRESETS,
  describe,
  runPipeline,
  type PipeMethod,
  type PipeStep,
} from "../lib/pipeline";
import {
  SCENARIOS,
  settle,
  simulate,
  type Combinator,
  type TimedPromise,
} from "../lib/eventLoop";
import { Icon, ScrollX } from "../components/ui";

const TABS = [
  ["stack", "Call stack"],
  ["pipeline", "Array pipeline"],
  ["loop", "Event loop"],
  ["combinators", "Promise combinators"],
] as const;
type Tab = (typeof TABS)[number][0];

export default function AsyncVisualiser() {
  const [params, setParams] = useSearchParams();
  const requested = params.get("tab");
  const tab: Tab = TABS.some(([k]) => k === requested) ? (requested as Tab) : "stack";
  return (
    <div className="page">
      <h1 className="page-title">Step by step</h1>
      <p className="page-sub">
        What is on the call stack right now? What does each array method hand to the next? Why does{" "}
        <code>setTimeout(f, 0)</code> run last? Step through it. Try your own snippets in the{" "}
        <Link to="/playground/ts">playground</Link>.
      </p>
      <div className="row gap-1 mb-3 flex-wrap" role="tablist">
        {TABS.map(([key, label]) => (
          <button
            key={key}
            className={tab === key ? "" : "ghost"}
            onClick={() => setParams({ tab: key }, { replace: true })}
            role="tab"
            aria-selected={tab === key}
          >
            {label}
          </button>
        ))}
      </div>
      {tab === "stack" && <CallStackView />}
      {tab === "pipeline" && <PipelineView />}
      {tab === "loop" && <EventLoop />}
      {tab === "combinators" && <Combinators />}
    </div>
  );
}

function CallStackView() {
  const [key, setKey] = useState(STACK_SCENARIOS[0]!.key);
  const scenario = STACK_SCENARIOS.find((s) => s.key === key) ?? STACK_SCENARIOS[0]!;
  const steps = useMemo(() => traceScenario(scenario), [scenario]);
  const [i, setI] = useState(0);
  const step = steps[Math.min(i, steps.length - 1)]!;
  const done = i >= steps.length - 1;

  useEffect(() => setI(0), [key]);

  return (
    <>
      <div className="row gap-1 flex-wrap mb-2">
        {STACK_SCENARIOS.map((s) => (
          <button key={s.key} className={s.key === key ? "" : "ghost"} onClick={() => setKey(s.key)}>
            {s.title}
          </button>
        ))}
      </div>
      <p className="mt-0">{scenario.lesson}</p>
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
          <LoopBox title="Output" items={step.output} empty="nothing yet" mono />
        </div>
        <div>
          <div className="card loop-box">
            <div className="io-label">
              Call stack <span className="dim" style={{ textTransform: "none" }}>· top of stack first</span>
            </div>
            {step.frames.length === 0 ? (
              <div className="dim quiz-note">empty</div>
            ) : (
              [...step.frames].reverse().map((f, k) => (
                <div key={k} className={`stack-frame ${k === 0 ? "top" : ""}`}>
                  <strong>{f.name}</strong>
                  {f.locals.length > 0 && (
                    <div className="stack-locals">
                      {f.locals.map(([name, value]) => (
                        <span key={name}>
                          <code>{name}</code> = <code>{value}</code>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
          {step.captured.length > 0 && (
            <div className="card loop-box mt-2">
              <div className="io-label">Captured by closures</div>
              {step.captured.map(([name, value]) => (
                <div key={name} className="loop-item mono">
                  {name} = {value}
                </div>
              ))}
            </div>
          )}
          <div className="card loop-note">
            <span className="badge">
              step {i + 1}/{steps.length}
            </span>{" "}
            {step.note}
          </div>
          <div className="row gap-1 mt-2">
            <button className="ghost" onClick={() => setI(0)} disabled={i === 0}>
              <Icon name="reset" size={14} /> Reset
            </button>
            <button className="ghost" onClick={() => setI((n) => Math.max(0, n - 1))} disabled={i === 0}>
              ◀ Back
            </button>
            <button onClick={() => setI((n) => Math.min(steps.length - 1, n + 1))} disabled={done}>
              Step ▶
            </button>
            <button className="ghost" onClick={() => setI(steps.length - 1)} disabled={done}>
              <Icon name="forward" size={14} /> End
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function PipelineView() {
  const [input, setInput] = useState(PIPE_PRESETS[0]!.input);
  const [steps, setSteps] = useState<PipeStep[]>(PIPE_PRESETS[0]!.steps);
  const [lesson, setLesson] = useState(PIPE_PRESETS[0]!.lesson);
  let parsed: unknown;
  let parseError = "";
  try {
    parsed = JSON.parse(input);
  } catch (e) {
    parseError = e instanceof Error ? e.message : String(e);
  }
  const results = parseError ? [] : runPipeline(parsed, steps);

  const update = (k: number, patch: Partial<PipeStep>) => setSteps(steps.map((s, i) => (i === k ? { ...s, ...patch } : s)));

  return (
    <>
      <div className="row gap-1 flex-wrap mb-2">
        {PIPE_PRESETS.map((p) => (
          <button
            key={p.title}
            className="ghost"
            onClick={() => {
              setInput(p.input);
              setSteps(p.steps);
              setLesson(p.lesson);
            }}
          >
            {p.title}
          </button>
        ))}
      </div>
      <p className="mt-0">{lesson}</p>
      <div className="card">
        <div className="io-label">Input (JSON)</div>
        <input className="w-full ff-mono"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="Input array as JSON"
        />
        {parseError && <p className="quiz-note c-bad">Not valid JSON: {parseError}</p>}
        {steps.map((s, k) => {
          const r = results[k];
          return (
            <div key={k} className="pipe-step">
              <div className="row gap-1 items-center">
                <code>.</code>
                <select value={s.method} onChange={(e) => update(k, { method: e.target.value as PipeMethod })}>
                  {PIPE_METHODS.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
                <code>(</code>
                <input className="flex-1 ff-mono"
                  value={s.arg}
                  onChange={(e) => update(k, { arg: e.target.value })}
                  aria-label={`Argument of step ${k + 1}`}
                />
                <code>)</code>
                <button className="ghost" onClick={() => setSteps(steps.filter((_, i) => i !== k))} aria-label="Remove step">
                  ×
                </button>
              </div>
              {r && (
                <div className="pipe-result">
                  {r.error ? (
                    <span className="c-bad">{r.error}</span>
                  ) : (
                    <>
                      → <code>{describe(r.value)}</code>
                      {r.mutatedInput && <span className="badge ml-1">mutated its input</span>}
                    </>
                  )}
                </div>
              )}
            </div>
          );
        })}
        <button className="ghost" onClick={() => setSteps([...steps, { method: "map", arg: "(x) => x" }])}>
          + step
        </button>
        <p className="dim quiz-note mb-0">
          Each argument is plain JavaScript (no type annotations), run in this page on the result of the step above.
        </p>
      </div>
    </>
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
      <div className="row gap-1 flex-wrap mb-2">
        {SCENARIOS.map((s) => (
          <button key={s.key} className={s.key === key ? "" : "ghost"} onClick={() => setKey(s.key)}>
            {s.title}
          </button>
        ))}
      </div>
      <p className="mt-0">{scenario.lesson}</p>

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
          <div className="io-label mt-2">
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
          <div className="row gap-1 mt-2">
            <button className="ghost" onClick={() => setI(0)} disabled={i === 0}>
              <Icon name="reset" size={14} /> Reset
            </button>
            <button className="ghost" onClick={() => setI((n) => Math.max(0, n - 1))} disabled={i === 0}>
              ◀ Back
            </button>
            <button onClick={() => setI((n) => Math.min(steps.length - 1, n + 1))} disabled={done}>
              Step ▶
            </button>
            <button className="ghost" onClick={() => (done ? (setI(0), setPlaying(true)) : setPlaying((p) => !p))}>
              <Icon name={playing ? "timer" : "run"} size={14} /> {playing ? "Pause" : "Play"}
            </button>
            <button className="ghost" onClick={() => setI(steps.length - 1)} disabled={done}>
              <Icon name="forward" size={14} /> End
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
      <div className="row gap-1 flex-wrap mb-2">
        {COMBINATORS.map((c) => (
          <button key={c.key} className={c.key === comb ? "" : "ghost"} onClick={() => setComb(c.key)} title={c.note}>
            Promise.{c.key}
          </button>
        ))}
      </div>
      <p className="dim quiz-note mt-0">
        <code>Promise.{comb}</code> — {COMBINATORS.find((c) => c.key === comb)!.note}.
      </p>

      <ScrollX label="Promise timeline" className="card">
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
      </ScrollX>

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
