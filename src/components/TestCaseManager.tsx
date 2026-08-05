import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { Attempt, Solution, TestCase } from "../types";
import { useToast } from "./Toast";
import { mulberry32, mutateInput, hasMutablePayload, type GenMode } from "../lib/testgen";

interface Props {
  problemId: number;
  cases: TestCase[];
  onChange: (cases: TestCase[]) => void;
}

/** An oracle is a known-correct program used to compute expected outputs for
 * generated inputs: the user's latest accepted submission, or a saved solution. */
interface Oracle {
  id: string;
  label: string;
  language: string;
  code: string;
}

/** Manage user-authored + example test cases, and generate new ones whose
 * expected outputs are computed by running a correct solution (so they're
 * usable for Submit, not just Run). */
export function TestCaseManager({ problemId, cases, onChange }: Props) {
  const toast = useToast();
  const [editing, setEditing] = useState<TestCase | null>(null);
  const [attempts, setAttempts] = useState<Attempt[]>([]);
  const [solutions, setSolutions] = useState<Solution[]>([]);
  const [showGen, setShowGen] = useState(false);
  const [oracleId, setOracleId] = useState<string>("");
  const [count, setCount] = useState(4);
  const [generating, setGenerating] = useState(false);

  const userCases = cases.filter((c) => c.kind !== "hidden");

  useEffect(() => {
    api.listAttempts(problemId).then(setAttempts).catch(() => {});
    api.listSolutions(problemId).then(setSolutions).catch(() => {});
  }, [problemId]);

  // Available oracles: latest accepted attempt + every saved solution with code.
  const oracles = useMemo<Oracle[]>(() => {
    const list: Oracle[] = [];
    const acc = attempts.find((a) => a.status === "accepted" && a.code.trim());
    if (acc) {
      list.push({
        id: "attempt",
        label: `Latest accepted submission (${acc.language})`,
        language: acc.language,
        code: acc.code,
      });
    }
    for (const s of solutions) {
      if (s.code.trim()) {
        list.push({
          id: `sol-${s.id}`,
          label: `Solution: ${s.title} (${s.language})`,
          language: s.language,
          code: s.code,
        });
      }
    }
    return list;
  }, [attempts, solutions]);

  // Templates: existing cases with a non-empty, mutable input to reshape.
  const templates = useMemo(
    () => cases.filter((c) => c.input.trim() && hasMutablePayload(c.input)),
    [cases]
  );

  const canGenerate = oracles.length > 0 && templates.length > 0;
  const activeOracle = oracles.find((o) => o.id === oracleId) ?? oracles[0];

  const blank = (): TestCase => ({
    id: 0,
    problem_id: problemId,
    kind: "user",
    name: `Case ${userCases.length + 1}`,
    input: "",
    expected_output: "",
    ordering: cases.length,
  });

  const save = async (tc: TestCase) => {
    const id = await api.saveTestCase(tc);
    const saved = { ...tc, id };
    const next = tc.id ? cases.map((c) => (c.id === tc.id ? saved : c)) : [...cases, saved];
    onChange(next);
    setEditing(null);
    toast("Test case saved");
  };

  const del = async (tc: TestCase) => {
    await api.deleteTestCase(tc.id);
    onChange(cases.filter((c) => c.id !== tc.id));
  };

  const generate = async () => {
    if (!activeOracle || templates.length === 0) return;
    setGenerating(true);
    // Diversify: mostly perturbations, plus a min and a max boundary case.
    const modes: GenMode[] = [];
    for (let i = 0; i < count; i++) {
      modes.push(i === 0 ? "min" : i === 1 ? "max" : "perturb");
    }
    const rand = mulberry32(Date.now() >>> 0);
    const created: TestCase[] = [];
    let failures = 0;
    try {
      for (let i = 0; i < modes.length; i++) {
        const template = templates[i % templates.length];
        const input = mutateInput(template.input, modes[i], rand);
        let expected = "";
        try {
          const out = await api.runScratch(problemId, activeOracle.language, activeOracle.code, input);
          if (out.timed_out || out.truncated || out.exit_code !== 0) {
            failures++;
            continue;
          }
          expected = out.stdout;
        } catch {
          failures++;
          continue;
        }
        const tc: TestCase = {
          id: 0,
          problem_id: problemId,
          kind: "user",
          name: `Generated ${modes[i]} ${userCases.length + created.length + 1}`,
          input,
          expected_output: expected,
          ordering: cases.length + created.length,
        };
        const savedId = await api.saveTestCase(tc);
        created.push({ ...tc, id: savedId });
      }
      onChange([...cases, ...created]);
      if (created.length > 0) {
        toast(
          `Generated ${created.length} case${created.length === 1 ? "" : "s"}` +
            (failures ? ` (${failures} skipped)` : "")
        );
      } else {
        toast("Couldn't generate cases — the oracle produced no clean output.");
      }
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <div className="row wrap" style={{ marginBottom: 10 }}>
        <button onClick={() => setEditing(blank())}>+ Add case</button>
        <button className={showGen ? "primary" : ""} onClick={() => setShowGen((v) => !v)}>
          ✨ Generate cases
        </button>
      </div>

      {showGen && (
        <div className="card" style={{ marginBottom: 12 }}>
          {!canGenerate ? (
            <div className="dim">
              Generation computes expected outputs by running a known-correct solution against
              reshaped versions of an existing test input.
              {oracles.length === 0 && (
                <div style={{ marginTop: 6 }}>
                  • No oracle yet — <strong>solve this problem</strong> (an accepted submission) or
                  save a solution in the Solutions tab.
                </div>
              )}
              {templates.length === 0 && (
                <div style={{ marginTop: 6 }}>
                  • No usable template input — this problem needs at least one example/test case with
                  numeric input to reshape.
                </div>
              )}
            </div>
          ) : (
            <>
              <div className="row wrap" style={{ gap: 10, marginBottom: 8 }}>
                <label className="dim">
                  Oracle{" "}
                  <select value={activeOracle?.id} onChange={(e) => setOracleId(e.target.value)}>
                    {oracles.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="dim">
                  How many{" "}
                  <input
                    type="number"
                    min={1}
                    max={10}
                    style={{ width: 64 }}
                    value={count}
                    onChange={(e) => setCount(Math.min(10, Math.max(1, Number(e.target.value))))}
                  />
                </label>
                <button className="primary" onClick={generate} disabled={generating}>
                  {generating ? "Generating…" : "Generate"}
                </button>
              </div>
              <p className="faint" style={{ fontSize: 12, margin: 0 }}>
                Inputs are reshaped from your existing cases (counts/dimensions kept valid); expected
                outputs come from running the selected solution. Review generated cases before trusting
                them — they're only as correct as the oracle.
              </p>
            </>
          )}
        </div>
      )}

      {editing && (
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="row" style={{ marginBottom: 8 }}>
            <input
              placeholder="Name"
              value={editing.name}
              onChange={(e) => setEditing({ ...editing, name: e.target.value })}
              style={{ flex: 1 }}
            />
          </div>
          <div className="io-label">Input (stdin)</div>
          <textarea
            rows={4}
            style={{ width: "100%" }}
            value={editing.input}
            onChange={(e) => setEditing({ ...editing, input: e.target.value })}
          />
          <div className="io-label" style={{ marginTop: 8 }}>
            Expected output (optional for “Run”)
          </div>
          <textarea
            rows={3}
            style={{ width: "100%" }}
            value={editing.expected_output}
            onChange={(e) => setEditing({ ...editing, expected_output: e.target.value })}
          />
          <div className="row" style={{ marginTop: 8 }}>
            <button className="primary" onClick={() => save(editing)}>
              Save
            </button>
            <button className="ghost" onClick={() => setEditing(null)}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {userCases.length === 0 && !editing && (
        <div className="dim">No custom test cases yet. Example cases from the statement are used by “Run”.</div>
      )}

      {userCases.map((tc) => (
        <div key={`${tc.kind}-${tc.id}`} className="result">
          <div className="result-head">
            <span className="badge">{tc.kind}</span>
            <strong>{tc.name}</strong>
            <span className="spacer" />
            {tc.kind === "user" && (
              <>
                <button className="ghost" onClick={() => setEditing(tc)}>
                  Edit
                </button>
                <button className="ghost danger" onClick={() => del(tc)}>
                  Delete
                </button>
              </>
            )}
          </div>
          <div className="result-body">
            <div>
              <div className="io-label">Input</div>
              <div className="io-block">{tc.input || "∅"}</div>
            </div>
            {tc.expected_output && (
              <div>
                <div className="io-label">Expected</div>
                <div className="io-block">{tc.expected_output}</div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
