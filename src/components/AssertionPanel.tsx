// Which of a type exercise's hidden claims hold, and — for an `Equal` that
// fails — the two types side by side, expanded by the editor's TypeScript
// service (TS_MASTERY_ROADMAP M5-03). See lib/assertions.ts.

import { useEffect, useMemo, useState } from "react";
import { useMonaco } from "@monaco-editor/react";
import {
  assertionFailed,
  failingCheckLines,
  hasOwnCodeErrors,
  parseAssertions,
} from "../lib/assertions";
import { probeSource, probeType } from "../lib/tsAnalysis";

let probeSeq = 0;

export function AssertionPanel({ harness, message, code }: { harness: string; message: string; code: string }) {
  const claims = useMemo(() => parseAssertions(harness), [harness]);
  const failing = useMemo(() => failingCheckLines(message), [message]);
  const own = hasOwnCodeErrors(message);
  const monaco = useMonaco();
  const [expanded, setExpanded] = useState<Record<number, { left: string; right: string }>>({});

  useEffect(() => {
    if (!monaco) return;
    const bad = claims.filter((c) => c.kind === "equal" && assertionFailed(c, failing) && c.left && c.right);
    if (bad.length === 0) return;
    let live = true;
    const uri = monaco.Uri.parse(`file:///assertions/probe-${++probeSeq}.ts`);
    (async () => {
      const names = bad.flatMap((c) => [c.left!, c.right!]);
      const { text, offsets } = probeSource(`${code}\n${harness}`, names);
      const model = monaco.editor.createModel(text, "typescript", uri);
      try {
        const getWorker = await monaco.languages.typescript.getTypeScriptWorker();
        const client = await getWorker(uri);
        const out: Record<number, { left: string; right: string }> = {};
        for (let i = 0; i < bad.length; i++) {
          const show = async (offset: number) => {
            const info = await client.getQuickInfoAtPosition(uri.toString(), offset);
            return probeType((info?.displayParts ?? []).map((p: { text: string }) => p.text).join(""));
          };
          out[bad[i]!.from] = { left: await show(offsets[2 * i]!), right: await show(offsets[2 * i + 1]!) };
        }
        if (live) setExpanded(out);
      } catch {
        /* expansion is a nicety — the ✓/✗ list stands without it */
      } finally {
        model.dispose();
      }
    })();
    return () => {
      live = false;
    };
  }, [monaco, claims, failing, code, harness]);

  if (claims.length === 0) return null;
  const passed = claims.filter((c) => !assertionFailed(c, failing)).length;

  return (
    <div className="assertion-panel">
      <div className="io-label">
        The checks — {passed}/{claims.length} hold
      </div>
      {own && (
        <p className="dim quiz-note" style={{ marginTop: 0 }}>
          Your own code has errors too (the <code>main.ts</code> lines below) — fix those first; the claims depend on it.
        </p>
      )}
      {claims.map((c) => {
        const bad = assertionFailed(c, failing);
        const types = expanded[c.from];
        return (
          <div key={c.from} className={`assertion ${bad ? "bad" : "ok"}`}>
            <div>
              <span aria-hidden>{bad ? "✗" : "✓"}</span>{" "}
              {c.kind === "rejects" ? (
                <>
                  must be <strong>rejected</strong>: <code>{c.text}</code>
                  {c.note && <span className="dim"> — {c.note}</span>}
                  {bad && <div className="dim quiz-note">…but it compiles, so your type lets through something it should not.</div>}
                </>
              ) : (
                <code>{c.text}</code>
              )}
            </div>
            {bad && c.kind === "equal" && (
              <div className="assertion-types">
                <div>
                  <div className="io-label">Your type — {c.left}</div>
                  <code className="playground-type">{types?.left ?? "…"}</code>
                </div>
                <div>
                  <div className="io-label">Expected</div>
                  <code className="playground-type">{types?.right ?? c.right}</code>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
