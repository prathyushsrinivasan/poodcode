/**
 * The verdict, pinned under the editor.
 *
 * The results pane was the only place a result appeared, which meant the answer
 * to "did that pass?" was behind whichever tab you happened to be on — and gone
 * the moment you switched to Test Cases or Complexity. This keeps the last
 * verdict, the pass count, the runtime and the memory in view, and offers one
 * click to the first failing case.
 */

import type { JudgeReport } from "../../types";
import { formatMemory } from "../../lib/format";

const VERDICT: Record<JudgeReport["status"], { label: string; tone: string }> = {
  accepted: { label: "Accepted", tone: "good" },
  wrong: { label: "Wrong answer", tone: "bad" },
  error: { label: "Error", tone: "bad" },
  tle: { label: "Time limit exceeded", tone: "warn" },
  not_installed: { label: "Toolchain missing", tone: "warn" },
};

export function VerdictBar({
  report,
  running,
  runCount,
  onJumpToFailure,
}: {
  report: JudgeReport | null;
  running: boolean;
  runCount: number;
  onJumpToFailure: () => void;
}) {
  if (running) {
    return (
      <div className="verdict-bar running" role="status">
        <span className="verdict-dot" aria-hidden />
        Running…
      </div>
    );
  }

  if (!report) {
    return (
      <div className="verdict-bar empty">
        <span className="dim">No run yet — Ctrl+Enter runs the examples.</span>
      </div>
    );
  }

  const v = VERDICT[report.status] ?? { label: report.status, tone: "bad" };
  const firstFail = report.results.findIndex((r) => !r.passed);

  return (
    <div className={`verdict-bar ${v.tone}`} role="status">
      <strong className="verdict-label">{v.label}</strong>
      {report.total > 0 && (
        <span className="verdict-count mono">
          {report.passed}/{report.total} passed
        </span>
      )}
      <span className="spacer" />
      {report.runtime_ms > 0 && <span className="dim mono">{report.runtime_ms} ms</span>}
      {report.memory_kb != null && report.memory_kb > 0 && (
        <span className="dim mono">{formatMemory(report.memory_kb)}</span>
      )}
      <span className="dim">
        {runCount} run{runCount === 1 ? "" : "s"}
      </span>
      {firstFail >= 0 && (
        <button className="ghost verdict-jump" onClick={onJumpToFailure}>
          See case {firstFail + 1} →
        </button>
      )}
    </div>
  );
}
