import { useState } from "react";
import type { JudgeReport } from "../types";
import { formatMemory } from "../lib/format";
import { lineDiff } from "../lib/diff";
import { TsErrorLinks } from "./TsErrorLinks";
import { OutputCompare } from "./OutputCompare";
import { Icon } from "./ui/Icon";

function IOBlock({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="io-label">{label}</div>
      <div className="io-block">{value === "" ? "∅ (empty)" : value}</div>
    </div>
  );
}

/** Compact expected-vs-actual diff for a failed case. */
function ExpectedActualDiff({ expected, actual }: { expected: string; actual: string }) {
  const ops = lineDiff(expected, actual);
  const bg = (t: string) =>
    t === "add"
      ? "color-mix(in srgb, var(--bad) 16%, transparent)"
      : t === "del"
      ? "color-mix(in srgb, var(--good) 16%, transparent)"
      : "transparent";
  const sign = (t: string) => (t === "add" ? "+ (yours)" : t === "del" ? "− (expected)" : "  ");
  return (
    <div>
      <div className="io-label">Diff (− expected · + your output)</div>
      <pre className="io-block" style={{ maxHeight: 200, overflow: "auto" }}>
        {ops.map((op, i) => (
          <div key={i} style={{ background: bg(op.type), whiteSpace: "pre-wrap" }}>
            <span className="faint" style={{ userSelect: "none" }}>{sign(op.type)} </span>
            {op.text || " "}
          </div>
        ))}
      </pre>
    </div>
  );
}

export function TestResults({ report }: { report: JudgeReport | null }) {
  const [open, setOpen] = useState<number | null>(0);
  if (!report) {
    return (
      <div className="dim p-3">
        Run or submit your code to see results here.
      </div>
    );
  }

  if (report.status === "not_installed") {
    return (
      <div className="card border-medium">
        <strong>Toolchain not installed.</strong>
        <p className="dim mb-0">
          {report.not_installed_hint}
        </p>
      </div>
    );
  }

  const isError = report.status === "error" && report.results.length === 0;
  if (isError) {
    return (
      <div className="card border-bad">
        <strong className="c-bad">Compilation / build error</strong>
        <pre className="io-block mt-2">
          {report.compile_error || "Unknown error"}
        </pre>
        <TsErrorLinks text={report.compile_error} />
      </div>
    );
  }

  const banner =
    report.status === "accepted"
      ? { text: "Accepted", color: "var(--good)" }
      : report.status === "wrong"
      ? { text: "Wrong Answer", color: "var(--bad)" }
      : report.status === "tle"
      ? { text: "Time Limit Exceeded", color: "var(--medium)" }
      : { text: "Runtime Error", color: "var(--bad)" };

  const verdictLabel: Record<string, string> = {
    pass: "Pass",
    wrong: "Wrong",
    tle: "TLE",
    re: "Runtime error",
    trunc: "Output too long",
  };
  const verdictIcon = (r: { passed: boolean; timed_out: boolean; verdict: string }) =>
    r.passed ? "✅" : r.verdict === "tle" || r.timed_out ? "⏰" : r.verdict === "re" ? "💥" : "❌";

  return (
    <div>
      <div className="row mb-3">
        <span
          style={{ color: banner.color, fontWeight: 700, fontSize: 15 }}
        >
          {banner.text}
        </span>
        <span className="dim">
          {report.passed}/{report.total} passed
        </span>
        <span className="spacer" />
        {report.memory_kb != null && report.memory_kb > 0 && (
          <span className="badge">💾 {formatMemory(report.memory_kb)} peak</span>
        )}
        <span className="badge">⏱ {report.runtime_ms} ms total</span>
      </div>

      {report.results.map((r, i) => (
        <div key={i} className={`result ${r.passed ? "pass" : "fail"}`}>
          <button
            type="button"
            className="result-head"
            aria-expanded={open === i}
            onClick={() => setOpen(open === i ? null : i)}
          >
            <span>{verdictIcon(r)}</span>
            <strong>{r.name}</strong>
            <span className="badge">{r.kind}</span>
            {!r.passed && r.verdict && (
              <span className="badge c-bad border-bad">
                {verdictLabel[r.verdict] ?? r.verdict}
              </span>
            )}
            <span className="spacer" />
            {r.memory_kb != null && r.memory_kb > 0 && (
              <span className="dim">{formatMemory(r.memory_kb)}</span>
            )}
            <span className="dim">{r.runtime_ms} ms</span>
            <Icon name={open === i ? "chevronUp" : "chevronDown"} size={14} />
          </button>
          {open === i && (
            <div className="result-body">
              {r.kind === "hidden" && !r.passed ? (
                <div className="dim">
                  Hidden test — input is not shown. Compare your logic against the
                  expected behavior.
                </div>
              ) : !r.passed && !r.timed_out ? null : (
                <IOBlock label="Input" value={r.input} />
              )}
              {!r.passed && !r.timed_out && r.kind !== "hidden" ? (
                <OutputCompare input={r.input} expected={r.expected} actual={r.actual} />
              ) : (
                <>
                  <IOBlock label="Expected" value={r.expected} />
                  <IOBlock label="Your output" value={r.timed_out ? "(timed out)" : r.actual} />
                  {!r.passed && !r.timed_out && r.expected.trim() !== "" && r.actual !== r.expected && (
                    <ExpectedActualDiff expected={r.expected} actual={r.actual} />
                  )}
                </>
              )}
              {r.stderr.trim() && <IOBlock label="Stderr" value={r.stderr} />}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
