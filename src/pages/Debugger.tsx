import { useEffect, useMemo, useRef, useState } from "react";

// A lightweight algorithm visualizer: step through classic array/pointer
// algorithms over your own numbers, watching pointers move and state change.
// This teaches the *mechanics* that make an algorithm work — the learning goal
// the raw pass/fail judge can't convey.

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

export default function Debugger() {
  const [algo, setAlgo] = useState<AlgoId>("binary");
  const [raw, setRaw] = useState("1 3 5 7 9 11 13");
  const [target, setTarget] = useState(9);
  const [steps, setSteps] = useState<Step[]>([]);
  const [pos, setPos] = useState(0);
  const [playing, setPlaying] = useState(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

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

  // Auto-build when inputs change.
  useEffect(build, [algo, raw, target]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (playing) {
      timer.current = setInterval(() => {
        setPos((p) => {
          if (p >= steps.length - 1) {
            setPlaying(false);
            return p;
          }
          return p + 1;
        });
      }, 900);
    }
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [playing, steps.length]);

  const step = steps[pos];

  return (
    <div className="page page-wide">
      <h1 className="page-title">Visual Debugger</h1>
      <p className="page-sub">Step through array algorithms and watch the pointers move. Great for building intuition.</p>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row wrap" style={{ gap: 16 }}>
          <div>
            <div className="io-label">Algorithm</div>
            <select value={algo} onChange={(e) => setAlgo(e.target.value as AlgoId)}>
              {ALGOS.map((a) => (
                <option key={a.id} value={a.id}>{a.label}</option>
              ))}
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
        <div className="card" style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
            {step.arr.map((v, i) => {
              const hot = step.highlight.includes(i);
              const labels = Object.entries(step.pointers).filter(([, idx]) => idx === i).map(([k]) => k);
              return (
                <div key={i} style={{ textAlign: "center", minWidth: 44 }}>
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
                  <div className="mono" style={{ fontSize: 11, color: "var(--accent)", minHeight: 14 }}>
                    {labels.join(",")}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="io-block" style={{ margin: 0 }}>{step.note}</div>
          <div className="row" style={{ marginTop: 12 }}>
            <button onClick={() => setPos((p) => Math.max(0, p - 1))} disabled={pos === 0}>← Prev</button>
            <button className="primary" onClick={() => setPlaying((v) => !v)}>{playing ? "⏸ Pause" : "▶ Play"}</button>
            <button onClick={() => setPos((p) => Math.min(steps.length - 1, p + 1))} disabled={pos >= steps.length - 1}>Next →</button>
            <button className="ghost" onClick={build}>↺ Restart</button>
            <span className="spacer" />
            <span className="dim mono">step {pos + 1}/{steps.length}</span>
          </div>
        </div>
      )}
    </div>
  );
}
