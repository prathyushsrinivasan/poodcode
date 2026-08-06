import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import { useStore } from "../store";
import { parseTrace, type TraceStep } from "../lib/trace";

// Visual debugger with two modes:
//  • Algorithms — step through classic array/pointer algorithms over your data.
//  • Trace my code — run YOUR code and visualise the variables it prints via a
//    tiny `#T name=value` protocol (arrays print as [1, 2, 3]). This makes the
//    debugger work on the learner's actual solution, in any language.

interface Step {
  arr: number[];
  pointers: Record<string, number>;
  highlight: number[];
  note: string;
}

type AlgoId = "linear" | "binary" | "twopointer" | "bubble" | "kadane";

const ALGOS: { id: AlgoId; label: string; needsTarget: boolean; needsSorted: boolean }[] = [
  { id: "linear", label: "Linear Search", needsTarget: true, needsSorted: false },
  { id: "binary", label: "Binary Search", needsTarget: true, needsSorted: true },
  { id: "twopointer", label: "Two-Pointer Pair Sum", needsTarget: true, needsSorted: true },
  { id: "bubble", label: "Bubble Sort (one pass)", needsTarget: false, needsSorted: false },
  { id: "kadane", label: "Kadane (max subarray)", needsTarget: false, needsSorted: false },
];

function linear(arr: number[], target: number): Step[] {
  const steps: Step[] = [];
  for (let i = 0; i < arr.length; i++) {
    const found = arr[i] === target;
    steps.push({ arr, pointers: { i }, highlight: found ? [i] : [], note: found ? `Found ${target} at index ${i}.` : `arr[${i}] = ${arr[i]} ≠ ${target}` });
    if (found) break;
  }
  if (!steps.some((s) => s.highlight.length)) steps.push({ arr, pointers: {}, highlight: [], note: `${target} not present.` });
  return steps;
}

function binary(arr: number[], target: number): Step[] {
  const steps: Step[] = [];
  let lo = 0;
  let hi = arr.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const cmp = arr[mid] === target ? "=" : arr[mid] < target ? "<" : ">";
    steps.push({ arr, pointers: { lo, mid, hi }, highlight: [mid], note: `mid=${mid}, arr[mid]=${arr[mid]} ${cmp} ${target}` });
    if (arr[mid] === target) {
      steps.push({ arr, pointers: { mid }, highlight: [mid], note: `Found ${target} at index ${mid}.` });
      return steps;
    }
    if (arr[mid] < target) lo = mid + 1;
    else hi = mid - 1;
  }
  steps.push({ arr, pointers: {}, highlight: [], note: `${target} not present.` });
  return steps;
}

function twoPointer(arr: number[], target: number): Step[] {
  const steps: Step[] = [];
  let l = 0;
  let r = arr.length - 1;
  while (l < r) {
    const sum = arr[l] + arr[r];
    const cmp = sum === target ? "=" : sum < target ? "<" : ">";
    steps.push({ arr, pointers: { l, r }, highlight: [l, r], note: `arr[${l}]+arr[${r}] = ${sum} ${cmp} ${target}` });
    if (sum === target) {
      steps.push({ arr, pointers: { l, r }, highlight: [l, r], note: `Pair found: ${arr[l]} + ${arr[r]} = ${target}.` });
      return steps;
    }
    if (sum < target) l++;
    else r--;
  }
  steps.push({ arr, pointers: {}, highlight: [], note: "No pair sums to the target." });
  return steps;
}

function bubble(arr: number[]): Step[] {
  const a = [...arr];
  const steps: Step[] = [];
  for (let i = 0; i < a.length - 1; i++) {
    const swap = a[i] > a[i + 1];
    steps.push({ arr: [...a], pointers: { j: i }, highlight: [i, i + 1], note: swap ? `${a[i]} > ${a[i + 1]} → swap` : `${a[i]} ≤ ${a[i + 1]} → keep` });
    if (swap) [a[i], a[i + 1]] = [a[i + 1], a[i]];
  }
  steps.push({ arr: [...a], pointers: {}, highlight: [], note: "One pass done — largest element bubbled to the end." });
  return steps;
}

function kadane(arr: number[]): Step[] {
  const steps: Step[] = [];
  let cur = arr[0];
  let best = arr[0];
  steps.push({ arr, pointers: { i: 0 }, highlight: [0], note: `Start: cur=${cur}, best=${best}` });
  for (let i = 1; i < arr.length; i++) {
    cur = Math.max(arr[i], cur + arr[i]);
    best = Math.max(best, cur);
    steps.push({ arr, pointers: { i }, highlight: [i], note: `cur=max(${arr[i]}, prev+${arr[i]})=${cur}, best=${best}` });
  }
  steps.push({ arr, pointers: {}, highlight: [], note: `Maximum subarray sum = ${best}.` });
  return steps;
}

/** Render one array with pointer labels and highlighted cells. */
function ArrayView({ arr, pointers, highlight }: { arr: number[]; pointers: Record<string, number>; highlight: number[] }) {
  return (
    <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
      {arr.map((v, i) => {
        const hot = highlight.includes(i);
        const labels = Object.entries(pointers).filter(([, idx]) => idx === i).map(([k]) => k);
        return (
          <div key={i} style={{ textAlign: "center", minWidth: 40 }}>
            <div
              style={{
                border: `2px solid ${hot ? "var(--accent)" : "var(--border)"}`,
                background: hot ? "color-mix(in srgb, var(--accent) 18%, transparent)" : "var(--bg-elev-1)",
                borderRadius: 8,
                padding: "10px 8px",
                fontWeight: 700,
              }}
            >
              {v}
            </div>
            <div className="faint" style={{ fontSize: 10 }}>{i}</div>
            <div className="mono" style={{ fontSize: 11, color: "var(--accent)", minHeight: 14 }}>{labels.join(",")}</div>
          </div>
        );
      })}
    </div>
  );
}

function StepControls({ pos, total, playing, onPrev, onNext, onPlay, onRestart }: {
  pos: number; total: number; playing: boolean;
  onPrev: () => void; onNext: () => void; onPlay: () => void; onRestart: () => void;
}) {
  return (
    <div className="row" style={{ marginTop: 12 }}>
      <button onClick={onPrev} disabled={pos === 0}>← Prev</button>
      <button className="primary" onClick={onPlay}>{playing ? "⏸ Pause" : "▶ Play"}</button>
      <button onClick={onNext} disabled={pos >= total - 1}>Next →</button>
      <button className="ghost" onClick={onRestart}>↺ Restart</button>
      <span className="spacer" />
      <span className="dim mono">step {pos + 1}/{total}</span>
    </div>
  );
}

function usePlayer(total: number) {
  const [pos, setPos] = useState(0);
  const [playing, setPlaying] = useState(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  useEffect(() => {
    if (playing) {
      timer.current = setInterval(() => {
        setPos((p) => {
          if (p >= total - 1) { setPlaying(false); return p; }
          return p + 1;
        });
      }, 900);
    }
    return () => { if (timer.current) clearInterval(timer.current); };
  }, [playing, total]);
  return { pos, setPos, playing, setPlaying };
}

function AlgoDebugger() {
  const [algo, setAlgo] = useState<AlgoId>("binary");
  const [raw, setRaw] = useState("1 3 5 7 9 11 13");
  const [target, setTarget] = useState(9);
  const [steps, setSteps] = useState<Step[]>([]);
  const { pos, setPos, playing, setPlaying } = usePlayer(steps.length);

  const spec = ALGOS.find((a) => a.id === algo)!;
  const parsed = useMemo(
    () => raw.split(/\s+/).filter(Boolean).map(Number).filter((n) => !Number.isNaN(n)),
    [raw]
  );

  const build = () => {
    let arr = parsed;
    if (spec.needsSorted) arr = [...parsed].sort((a, b) => a - b);
    let s: Step[] = [];
    if (algo === "linear") s = linear(arr, target);
    else if (algo === "binary") s = binary(arr, target);
    else if (algo === "twopointer") s = twoPointer(arr, target);
    else if (algo === "bubble") s = bubble(arr);
    else s = kadane(arr);
    setSteps(s);
    setPos(0);
    setPlaying(false);
  };
  useEffect(build, [algo, raw, target]); // eslint-disable-line react-hooks/exhaustive-deps

  const step = steps[pos];
  return (
    <>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row wrap" style={{ gap: 16 }}>
          <div>
            <div className="io-label">Algorithm</div>
            <select value={algo} onChange={(e) => setAlgo(e.target.value as AlgoId)}>
              {ALGOS.map((a) => (<option key={a.id} value={a.id}>{a.label}</option>))}
            </select>
          </div>
          <div style={{ flex: 1, minWidth: 200 }}>
            <div className="io-label">Array (space-separated)</div>
            <input style={{ width: "100%" }} value={raw} onChange={(e) => setRaw(e.target.value)} />
          </div>
          {spec.needsTarget && (
            <div>
              <div className="io-label">Target</div>
              <input type="number" style={{ width: 90 }} value={target} onChange={(e) => setTarget(Number(e.target.value))} />
            </div>
          )}
        </div>
        {spec.needsSorted && <p className="faint" style={{ fontSize: 12, marginBottom: 0 }}>This algorithm needs a sorted array — the input is sorted automatically.</p>}
      </div>
      {step && (
        <div className="card">
          <ArrayView arr={step.arr} pointers={step.pointers} highlight={step.highlight} />
          <div className="io-block" style={{ margin: 0 }}>{step.note}</div>
          <StepControls pos={pos} total={steps.length} playing={playing}
            onPrev={() => setPos((p) => Math.max(0, p - 1))}
            onNext={() => setPos((p) => Math.min(steps.length - 1, p + 1))}
            onPlay={() => setPlaying((v) => !v)} onRestart={build} />
        </div>
      )}
    </>
  );
}

// ---- Trace-my-code mode ----

const SAMPLES: Record<string, string> = {
  python:
    "# Print lines starting with '#T' to visualise your variables.\n" +
    "# Arrays print as [1, 2, 3]; ints print as-is.\n" +
    "arr = [1, 3, 5, 7, 9, 11]\n" +
    "target = 7\n" +
    "lo, hi = 0, len(arr) - 1\n" +
    "while lo <= hi:\n" +
    "    mid = (lo + hi) // 2\n" +
    "    print('#T arr=%s lo=%d mid=%d hi=%d' % (arr, lo, mid, hi))\n" +
    "    if arr[mid] == target: break\n" +
    "    elif arr[mid] < target: lo = mid + 1\n" +
    "    else: hi = mid - 1\n",
  java:
    "import java.util.*;\n" +
    "public class Main {\n" +
    "    public static void main(String[] a) {\n" +
    "        int[] arr = {1, 3, 5, 7, 9, 11};\n" +
    "        int target = 7, lo = 0, hi = arr.length - 1;\n" +
    "        while (lo <= hi) {\n" +
    "            int mid = (lo + hi) / 2;\n" +
    "            System.out.println(\"#T arr=\" + Arrays.toString(arr) + \" lo=\" + lo + \" mid=\" + mid + \" hi=\" + hi);\n" +
    "            if (arr[mid] == target) break;\n" +
    "            else if (arr[mid] < target) lo = mid + 1;\n" +
    "            else hi = mid - 1;\n" +
    "        }\n" +
    "    }\n" +
    "}\n",
  javascript:
    "const arr = [1, 3, 5, 7, 9, 11];\n" +
    "let target = 7, lo = 0, hi = arr.length - 1;\n" +
    "while (lo <= hi) {\n" +
    "  const mid = (lo + hi) >> 1;\n" +
    "  console.log(`#T arr=[${arr}] lo=${lo} mid=${mid} hi=${hi}`);\n" +
    "  if (arr[mid] === target) break;\n" +
    "  else if (arr[mid] < target) lo = mid + 1;\n" +
    "  else hi = mid - 1;\n" +
    "}\n",
};

function TraceDebugger() {
  const languages = useStore((s) => s.languages);
  const prefs = useStore((s) => s.prefs);
  const [langId, setLangId] = useState(prefs.defaultLanguage);
  const [code, setCode] = useState(SAMPLES[prefs.defaultLanguage] ?? SAMPLES.python);
  const [stdin, setStdin] = useState("");
  const [steps, setSteps] = useState<TraceStep[]>([]);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState("");
  const { pos, setPos, playing, setPlaying } = usePlayer(steps.length);

  const run = async () => {
    setRunning(true);
    setErr("");
    try {
      const out = await api.runScratch(null, langId, code, stdin);
      const s = parseTrace(out.stdout);
      setSteps(s);
      setPos(0);
      setPlaying(false);
      if (out.stderr.trim()) setErr(out.stderr);
      else if (s.length === 0) setErr("No trace found. Print lines like  #T arr=[1,2,3] i=0  from your code.");
    } catch (e) {
      setErr(String(e));
    } finally {
      setRunning(false);
    }
  };

  const step = steps[pos];
  const arrayVars = step ? Object.entries(step.vars).filter(([, v]) => Array.isArray(v)) as [string, number[]][] : [];
  const scalarVars = step ? Object.entries(step.vars).filter(([, v]) => !Array.isArray(v)) : [];
  // Scalar ints become pointers into arrays (index == value).
  const pointers: Record<string, number> = {};
  for (const [k, v] of scalarVars) if (typeof v === "number") pointers[k] = v;

  const loadSample = () => setCode(SAMPLES[langId] ?? SAMPLES.python);

  return (
    <>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row wrap" style={{ gap: 12, marginBottom: 8 }}>
          <select value={langId} onChange={(e) => setLangId(e.target.value)}>
            {languages.map((l) => (
              <option key={l.id} value={l.id}>{l.label}{l.installed ? "" : " · (not installed)"}</option>
            ))}
          </select>
          <button onClick={loadSample}>Load example</button>
          <span className="spacer" />
          <button className="primary" onClick={run} disabled={running}>{running ? "Running…" : "▶ Run & trace"}</button>
        </div>
        <p className="faint" style={{ fontSize: 12, marginTop: 0 }}>
          Add <span className="mono">print</span> lines that start with <span className="mono">#T</span> followed by{" "}
          <span className="mono">name=value</span> pairs (arrays as <span className="mono">[1, 2, 3]</span>). Each printed
          line becomes a step you can scrub through.
        </p>
        <textarea
          style={{ width: "100%", minHeight: "26vh", fontFamily: "var(--font-mono)", fontSize: 13 }}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          spellCheck={false}
        />
        <div className="io-label" style={{ marginTop: 8 }}>Stdin (optional)</div>
        <textarea style={{ width: "100%" }} rows={2} value={stdin} onChange={(e) => setStdin(e.target.value)} />
      </div>

      {err && <div className="io-block" style={{ color: "var(--bad)", marginBottom: 12 }}>{err}</div>}

      {step && (
        <div className="card">
          {arrayVars.length === 0 && <div className="dim" style={{ marginBottom: 8 }}>No arrays in this step — showing scalars only.</div>}
          {arrayVars.map(([name, arr]) => (
            <div key={name} style={{ marginBottom: 8 }}>
              <div className="io-label">{name}</div>
              <ArrayView arr={arr} pointers={pointers} highlight={[]} />
            </div>
          ))}
          {scalarVars.length > 0 && (
            <div className="tag-row" style={{ marginBottom: 8 }}>
              {scalarVars.map(([k, v]) => (
                <span key={k} className="badge mono">{k} = {String(v)}</span>
              ))}
            </div>
          )}
          <div className="io-block" style={{ margin: 0 }}>#T {step.line}</div>
          <StepControls pos={pos} total={steps.length} playing={playing}
            onPrev={() => setPos((p) => Math.max(0, p - 1))}
            onNext={() => setPos((p) => Math.min(steps.length - 1, p + 1))}
            onPlay={() => setPlaying((v) => !v)} onRestart={() => setPos(0)} />
        </div>
      )}
    </>
  );
}

export default function Debugger() {
  const [mode, setMode] = useState<"algorithms" | "trace">("algorithms");
  return (
    <div className="page page-wide">
      <h1 className="page-title">Visual Debugger</h1>
      <p className="page-sub">Watch state change step by step — for built-in algorithms, or your own code.</p>
      <div className="pill-toggle" style={{ marginBottom: 16 }}>
        <span className={`pill ${mode === "algorithms" ? "on" : ""}`} onClick={() => setMode("algorithms")}>Algorithms</span>
        <span className={`pill ${mode === "trace" ? "on" : ""}`} onClick={() => setMode("trace")}>Trace my code</span>
      </div>
      {mode === "algorithms" ? <AlgoDebugger /> : <TraceDebugger />}
    </div>
  );
}
