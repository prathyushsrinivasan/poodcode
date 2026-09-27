/**
 * Verdicts, hints and references — the parts of an exercise that report back
 * (UI_ROADMAP C4, G8).
 *
 * Every track drew these by hand: a `div.card` with an inline `borderColor`
 * and an `io-label` coloured to match, and the wording, colours and icons
 * drifted — "Toolchain not available" in Learn, "Runtime not available" in the
 * courses, 🎉 on one pass and ✓ on another, a checkpoint in green in Projects
 * and the same idea in accent in the Backend Lab. One panel now, in four tones,
 * with the icon and the heading in the same place every time.
 */

import { useState, type ReactNode } from "react";
import type { JudgeReport, SqlOut } from "../../types";
import { Icon, type IconName } from "../ui/Icon";
import { Button } from "../ui/Button";
import { Markdown } from "../Markdown";
import { AssertionPanel } from "../AssertionPanel";
import { FailingCases } from "../OutputCompare";
import { TsErrorLinks } from "../TsErrorLinks";
import { ResultGrid, TextGrid, differingRows } from "../SqlGrid";

export type VerdictTone = "good" | "bad" | "warn" | "info";

const TONE_ICON: Record<VerdictTone, IconName> = {
  good: "done",
  bad: "failed",
  warn: "warning",
  info: "info",
};

/** A result, a hint, a checkpoint: a titled panel in one of four tones. */
export function VerdictPanel({
  tone,
  title,
  icon,
  children,
  className = "",
}: {
  tone: VerdictTone;
  title: ReactNode;
  /** Overrides the tone's default icon (a hint uses a bulb, not an ⓘ). */
  icon?: IconName;
  children?: ReactNode;
  className?: string;
}) {
  return (
    <div className={`verdict verdict-${tone} ${className}`.trim()} role={tone === "bad" ? "alert" : undefined}>
      <div className="verdict-title">
        <Icon name={icon ?? TONE_ICON[tone]} size={15} />
        <span>{title}</span>
      </div>
      {children !== undefined && children !== null && children !== false && (
        <div className="verdict-body">{children}</div>
      )}
    </div>
  );
}

/** Raw tool output (a compiler message, a thrown error), preformatted. */
export function ErrorText({ children }: { children: string }) {
  return <pre className="verdict-pre">{children}</pre>;
}

// ---- Hints ----------------------------------------------------------------

/**
 * A hint ladder: nudge → strategy → near-answer, one rung at a time. Falls
 * back to the single legacy `hint` when no ladder is authored.
 */
export function useHintLadder(hints: string[] | undefined, hint: string | undefined) {
  const ladder = hints && hints.length > 0 ? hints : hint ? [hint] : [];
  const [shown, setShown] = useState(0);
  return {
    ladder,
    shown,
    more: shown < ladder.length,
    next: () => setShown((n) => Math.min(ladder.length, n + 1)),
    reset: () => setShown(0),
  };
}

/** The "Hint" / "Next hint (1/3)" button. `data-hint-next` is what the global
 * "reveal the next hint" shortcut clicks. */
export function HintButton({ ladder }: { ladder: ReturnType<typeof useHintLadder> }) {
  if (!ladder.more) return null;
  const n = ladder.ladder.length;
  return (
    <Button variant="ghost" icon="hint" data-hint-next onClick={ladder.next}>
      {ladder.shown === 0 ? (n > 1 ? `Hint (${n})` : "Hint") : `Next hint (${ladder.shown}/${n})`}
    </Button>
  );
}

export function HintPanel({ ladder, title = "Hint" }: { ladder: ReturnType<typeof useHintLadder>; title?: string }) {
  if (ladder.shown === 0) return null;
  const n = ladder.ladder.length;
  return (
    <VerdictPanel tone="info" icon="hint" title={n > 1 ? `Hints (${ladder.shown}/${n})` : title}>
      {ladder.ladder.slice(0, ladder.shown).map((h, i) => (
        <p key={i} className="verdict-para">
          {n > 1 && <strong>{i + 1}. </strong>}
          {h}
        </p>
      ))}
    </VerdictPanel>
  );
}

// ---- References -----------------------------------------------------------

/**
 * A worked solution, hidden behind a button, with a caveat about what to do
 * with it. `note` defaults to the honest one; pass "" to say nothing.
 */
export function ReferenceReveal({
  reference,
  language = "ts",
  revealLabel = "Reveal a reference solution",
  hideLabel = "Hide the reference solution",
  note = "One way to write it — not the only way. Compare it with yours rather than replacing yours with it.",
}: {
  reference: string;
  language?: string;
  revealLabel?: string;
  hideLabel?: string;
  note?: string;
}) {
  const [show, setShow] = useState(false);
  return (
    <div className="exercise-reference">
      <Button variant="ghost" icon={show ? "hide" : "show"} onClick={() => setShow((s) => !s)} aria-expanded={show}>
        {show ? hideLabel : revealLabel}
      </Button>
      {show && <ReferenceCode code={reference} language={language} note={note} />}
    </div>
  );
}

/** The reference itself, once revealed. */
export function ReferenceCode({ code, language, note }: { code: string; language: string; note?: string }) {
  return (
    <div className="exercise-reference-body">
      {note && <p className="exercise-note">{note}</p>}
      <Markdown>{"```" + language + "\n" + code.replace(/\n$/, "") + "\n```"}</Markdown>
    </div>
  );
}

// ---- Judge feedback -------------------------------------------------------

/**
 * What the judge said about a run, in the house wording:
 *   not installed · compile error (with the assertion view for type-graded
 *   exercises) · type-checked · all passed · n/m passed with the failing cases.
 */
export function JudgeFeedback({
  report,
  isSql = false,
  check,
}: {
  report: JudgeReport;
  isSql?: boolean;
  /** A type-graded exercise: its hidden checks and the code judged. */
  check?: { harness: string; code: string };
}) {
  if (report.status === "not_installed") {
    return (
      <VerdictPanel tone="warn" title="Toolchain not available">
        <p className="verdict-para">
          {report.not_installed_hint || "The toolchain for this language isn't installed. See Settings → Toolchains."}
        </p>
      </VerdictPanel>
    );
  }

  if (report.compile_error) {
    return (
      <VerdictPanel tone="bad" title={isSql ? "SQL error — the query would not compile" : "Compile error"}>
        {check && check.harness.trim() !== "" ? (
          <>
            <AssertionPanel harness={check.harness} message={report.compile_error} code={check.code} />
            <details className="verdict-details">
              <summary className="dim quiz-note">The compiler&rsquo;s own words</summary>
              <ErrorText>{report.compile_error}</ErrorText>
            </details>
          </>
        ) : (
          <ErrorText>{report.compile_error}</ErrorText>
        )}
        <TsErrorLinks text={report.compile_error} />
      </VerdictPanel>
    );
  }

  // A type-level exercise has no cases: the backend reports one synthetic
  // `typecheck` result, and a failure has already been rendered above as a
  // compile error. "1/1 tests passed" would be a lie about what happened.
  if (report.results.length === 1 && report.results[0].kind === "typecheck") {
    return (
      <VerdictPanel
        tone="good"
        title={
          check && check.harness.trim() === ""
            ? "It compiles now — the compiler has nothing left to say"
            : "Types check out — every assertion compiled"
        }
      />
    );
  }

  const ok = report.status === "accepted";
  const failing = report.results.filter((r) => !r.passed);

  if (ok) return <VerdictPanel tone="good" title={`All ${report.total} tests passed`} />;

  return (
    <VerdictPanel tone="bad" title={`${report.passed} / ${report.total} tests passed`}>
      {isSql ? (
        failing.slice(0, 2).map((r, i) => (
          <SqlCaseDiff
            key={i}
            name={r.name}
            variation={r.name.includes("changed data")}
            expected={r.expected}
            actual={r.actual}
            stderr={r.stderr}
            timedOut={r.timed_out}
          />
        ))
      ) : (
        <FailingCases failing={failing} />
      )}
    </VerdictPanel>
  );
}

/** "Couldn't run" — the runner itself threw, before any verdict. */
export function RunError({ error }: { error: string }) {
  if (!error) return null;
  return (
    <VerdictPanel tone="bad" title="Couldn’t run">
      <ErrorText>{error}</ErrorText>
    </VerdictPanel>
  );
}

// ---- SQL ------------------------------------------------------------------

/** The result of a scratch "Run query", shown as a table rather than as text. */
export function SqlPreview({ out }: { out: SqlOut }) {
  if (out.error) {
    return (
      <VerdictPanel
        tone="bad"
        title={out.timed_out ? "Query timed out" : out.syntax_error ? "SQL error — the query would not compile" : "SQL error"}
      >
        <ErrorText>{out.error}</ErrorText>
        {out.timed_out && (
          <p className="exercise-note">
            An accidental cross join is the usual cause — check that every table after the first has an{" "}
            <code>ON</code> clause.
          </p>
        )}
      </VerdictPanel>
    );
  }
  return (
    <VerdictPanel
      tone="info"
      icon="database"
      title={`Query result — ${out.row_count} row${out.row_count === 1 ? "" : "s"} in ${out.runtime_ms} ms`}
    >
      {out.grid && <ResultGrid columns={out.grid.columns} rows={out.grid.rows} truncated={out.grid.truncated} />}
      <p className="exercise-note">
        This is just what your SQL returns — press <strong>Check</strong> to compare it against the expected answer.
      </p>
    </VerdictPanel>
  );
}

/** The failing case, as two aligned tables with the differing rows tinted. */
function SqlCaseDiff({
  name,
  variation,
  expected,
  actual,
  stderr,
  timedOut,
}: {
  name: string;
  variation: boolean;
  expected: string;
  actual: string;
  stderr: string;
  timedOut: boolean;
}) {
  const diff = differingRows(expected, actual);
  return (
    <div className="sql-case">
      <div className="exercise-note">
        {name}
        {variation && " — the same schema with the data changed, so a hard-coded answer fails here"}
      </div>
      {stderr ? (
        <pre className="verdict-pre is-bad">
          {timedOut ? "Query timed out. " : ""}
          {stderr}
        </pre>
      ) : (
        <div className="sql-compare">
          <div>
            <div className="io-label is-good">Expected</div>
            <TextGrid text={expected} highlightRows={diff} />
          </div>
          <div>
            <div className="io-label is-bad">Your query returned</div>
            <TextGrid text={actual} highlightRows={diff} />
          </div>
        </div>
      )}
    </div>
  );
}
