import { useState } from "react";
import { api } from "../api";
import type { ProcOut, Skeleton } from "../types";
import { Markdown, InlineMarkdown } from "./Markdown";
import { CodeEditor } from "./CodeEditor";
import { diffSources } from "../lib/lineDiff";

/**
 * Making the playbook usable.
 *
 * The unit page told you to "copy each of these out by hand once" and then gave
 * you no copy button and nowhere to type. Instruction without affordance is how
 * a good idea becomes a paragraph nobody acts on.
 *
 * Two affordances, and the second is the real one: **retype it from memory**,
 * against the actual compiler, with a line diff against the original when you
 * are done. Copying to the clipboard is for getting a shape into your own file;
 * typing it is what the instruction was actually asking for, and the diff is
 * what tells you whether you had it.
 */

/** Strip the trailing newline the generator adds, so a diff of an exact match is
 * genuinely empty rather than one blank line. */
function norm(code: string): string {
  return code.replace(/\s+$/, "");
}

export function SkeletonBlock({ skeleton }: { skeleton: Skeleton }) {
  const [copied, setCopied] = useState(false);
  const [mode, setMode] = useState<"read" | "type">("read");
  const [typed, setTyped] = useState("");
  const [out, setOut] = useState<ProcOut | null>(null);
  const [running, setRunning] = useState(false);
  const [checked, setChecked] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(skeleton.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* a clipboard the browser refuses is not worth an error dialog */
    }
  };

  const run = async () => {
    setRunning(true);
    setOut(null);
    try {
      // `problemId: null` means no function-harness wrapping: the code is
      // compiled and run exactly as typed, which is what a scratch pad is.
      setOut(await api.runScratch(null, "java", typed, ""));
    } catch (e) {
      setOut({
        stdout: "",
        stderr: String(e),
        exit_code: null,
        timed_out: false,
        runtime_ms: 0,
        memory_kb: null,
        truncated: false,
      });
    } finally {
      setRunning(false);
    }
  };

  // `codeOnly` so a missing comment is not reported as a missing line: the
  // exercise is the code shape, not the prose around it.
  const diff = checked ? diffSources(norm(skeleton.code), norm(typed), { codeOnly: true }) : null;
  const exact = diff !== null && diff.every((l) => l.op === "same");

  return (
    <div style={{ marginBottom: 18 }}>
      <div className="row">
        <strong>{skeleton.name}</strong>
        {skeleton.when && <span className="dim"> — {skeleton.when}</span>}
        <span className="spacer" />
        <button className="ghost" style={{ fontSize: 12, padding: "2px 8px" }} onClick={copy}>
          {copied ? "✓ Copied" : "⧉ Copy"}
        </button>
        <button
          className="ghost"
          style={{ fontSize: 12, padding: "2px 8px" }}
          title="Type it from memory, compile it, then diff it against this"
          onClick={() => {
            setMode((m) => (m === "type" ? "read" : "type"));
            setChecked(false);
          }}
        >
          {mode === "type" ? "Hide the pad" : "⌨️ Type it from memory"}
        </button>
      </div>

      {/* Hidden while you are typing, because a reference you can see is a
          copying exercise rather than a recall one. */}
      {mode === "read" ? (
        <Markdown>{"```java\n" + skeleton.code + "```"}</Markdown>
      ) : (
        <div className="card" style={{ marginTop: 8, padding: 10 }}>
          <p className="faint" style={{ fontSize: 12, marginTop: 0 }}>
            The original is hidden — that is the point. Write it, compile it, then
            check yourself against it.
          </p>
          <div style={{ height: 260, border: "1px solid var(--border)", borderRadius: 6 }}>
            <CodeEditor language="java" value={typed} onChange={setTyped} onRun={run} />
          </div>
          <div className="row" style={{ marginTop: 8, gap: 8 }}>
            <button onClick={run} disabled={running || !typed.trim()}>
              {running ? "Compiling…" : "▶ Compile & run"}
            </button>
            <button className="ghost" onClick={() => setChecked((c) => !c)} disabled={!typed.trim()}>
              {checked ? "Hide the diff" : "Check against the original"}
            </button>
            <span className="spacer" />
            <span className="faint" style={{ fontSize: 12 }}>
              Ctrl+Enter runs
            </span>
          </div>

          {out && (
            <div style={{ marginTop: 10 }}>
              <div className="io-label">
                {out.timed_out
                  ? "Timed out"
                  : out.exit_code === 0
                    ? `Ran in ${out.runtime_ms} ms`
                    : `Exited ${out.exit_code}`}
              </div>
              {out.stdout && (
                <pre className="mono" style={{ margin: "4px 0", fontSize: 12, whiteSpace: "pre-wrap" }}>
                  {out.stdout}
                </pre>
              )}
              {out.stderr && (
                <pre
                  className="mono"
                  style={{ margin: "4px 0", fontSize: 12, color: "var(--bad)", whiteSpace: "pre-wrap" }}
                >
                  {out.stderr}
                </pre>
              )}
            </div>
          )}

          {diff && (
            <div style={{ marginTop: 10 }}>
              <div className="io-label">
                {exact ? "Identical to the original." : "Yours vs the original"}
              </div>
              {!exact && (
                <>
                  <p className="faint" style={{ fontSize: 12, margin: "2px 0 6px" }}>
                    Differences are not failures — a skeleton is a shape, not a
                    string. Read them for the lines you left out, not the names you
                    chose differently.
                  </p>
                  <pre
                    className="mono"
                    style={{
                      margin: 0,
                      fontSize: 12,
                      padding: "8px 10px",
                      borderRadius: 6,
                      background: "var(--bg-elev-2)",
                      overflowX: "auto",
                    }}
                  >
                    {diff.map((l, i) => (
                      <div
                        key={i}
                        style={{
                          color:
                            l.op === "add"
                              ? "var(--good)"
                              : l.op === "del"
                                ? "var(--bad)"
                                : undefined,
                        }}
                      >
                        {l.op === "add" ? "+ " : l.op === "del" ? "− " : "  "}
                        {l.text || " "}
                      </div>
                    ))}
                  </pre>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {skeleton.note && mode === "read" && (
        <p className="faint" style={{ fontSize: 12, marginTop: -6 }}>
          <InlineMarkdown>{skeleton.note}</InlineMarkdown>
        </p>
      )}
    </div>
  );
}
