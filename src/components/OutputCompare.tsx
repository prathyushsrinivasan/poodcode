// The stdin/stdout visualiser (TS_MASTERY_ROADMAP M1-02): the test's stdin
// split into numbered lines, then the expected output and yours side by side,
// the first differing line highlighted with a caret under the first differing
// character, and one sentence saying what the difference is. The comparison
// uses the judge's own normalisation (lib/outputCompare.ts).

import { describeDifference, firstDifference, normalizeOutput, visibleWhitespace } from "../lib/outputCompare";

function Numbered({
  lines,
  mark,
  caret,
  showSpaces,
}: {
  lines: string[];
  mark?: number;
  caret?: number;
  showSpaces?: boolean;
}) {
  return (
    <pre className="io-block output-compare-lines">
      {lines.map((l, i) => (
        <div key={i} className={i + 1 === mark ? "oc-diff" : undefined}>
          <span className="oc-no">{i + 1}</span>
          {(showSpaces ? visibleWhitespace(l) : l) || " "}
          {i + 1 === mark && caret !== undefined && (
            <div className="oc-caret">
              <span className="oc-no" />
              {" ".repeat(Math.max(0, caret - 1))}^
            </div>
          )}
        </div>
      ))}
      {lines.length === 0 && <div className="dim">(nothing)</div>}
    </pre>
  );
}

type CaseResult = {
  name: string;
  input: string;
  expected: string;
  actual: string;
  stderr: string;
  timed_out: boolean;
};

/** The failing cases of a run: the first one visualised in full, a few more
 * summarised. A case named "Hidden test …" never shows its input. */
export function FailingCases({ failing, max = 3 }: { failing: CaseResult[]; max?: number }) {
  return (
    <>
      {failing.slice(0, max).map((r, i) => {
        const hidden = r.name.startsWith("Hidden test");
        if (hidden) {
          return (
            <div key={i} style={{ marginTop: 6, fontSize: 12 }}>
              <div className="dim">{r.name}</div>
              <div style={{ color: "var(--bad)" }}>
                {r.timed_out ? "Timed out." : "Failed."} Its input stays hidden until you pass — think about the
                cases the visible tests do not cover.
              </div>
            </div>
          );
        }
        return (
          <div key={i} style={{ marginTop: 8, fontSize: 12 }}>
            <div className="dim">{r.name}</div>
            {r.timed_out ? (
              <div style={{ color: "var(--bad)" }}>
                Timed out on input <code>{r.input.replace(/\n/g, " ⏎ ") || "(none)"}</code> — look for a loop that
                never ends, or work that grows too fast.
              </div>
            ) : i === 0 ? (
              <OutputCompare input={r.input} expected={r.expected} actual={r.actual} />
            ) : (
              <div style={{ fontFamily: "var(--font-mono)" }}>
                <div>
                  input: <code>{r.input.replace(/\n/g, " ⏎ ") || "(none)"}</code>
                </div>
                <div className="oc-sentence">{describeDifference(firstDifference(r.expected, r.actual))}</div>
              </div>
            )}
            {r.stderr && <pre style={{ margin: "4px 0 0", whiteSpace: "pre-wrap" }}>{r.stderr}</pre>}
          </div>
        );
      })}
    </>
  );
}

export function OutputCompare({
  input,
  expected,
  actual,
}: {
  /** The test's stdin; omitted for a hidden test. */
  input?: string;
  expected: string;
  actual: string;
}) {
  const diff = firstDifference(expected, actual);
  const e = normalizeOutput(expected);
  const a = normalizeOutput(actual);
  const eLines = e === "" ? [] : e.split("\n");
  const aLines = a === "" ? [] : a.split("\n");
  const mark = diff.kind === "same" ? undefined : diff.line;
  const caret = diff.kind === "char" ? diff.column : undefined;
  const spacing = diff.kind === "char" && diff.expected.replace(/\s/g, "") === diff.actual.replace(/\s/g, "");
  return (
    <div className="output-compare">
      {input !== undefined && (
        <div>
          <div className="io-label">stdin — line by line</div>
          <Numbered lines={input === "" ? [] : input.split("\n")} showSpaces={/ $|\t/m.test(input)} />
        </div>
      )}
      <div className="output-compare-cols">
        <div>
          <div className="io-label">Expected</div>
          <Numbered lines={eLines} mark={mark} showSpaces={spacing} />
        </div>
        <div>
          <div className="io-label">Yours</div>
          <Numbered lines={aLines} mark={mark} caret={caret} showSpaces={spacing} />
        </div>
      </div>
      <p className="oc-sentence">{describeDifference(diff)}</p>
    </div>
  );
}
