import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { Difficulty, Example, Prerequisite, Problem, TestCase } from "../types";
import { useToast } from "../components/Toast";

function emptyProblem(): Problem {
  return {
    id: 0,
    slug: "",
    title: "",
    difficulty: "Easy",
    description: "",
    constraints: "",
    examples: [],
    editorial: "",
    optimal_time: "",
    optimal_space: "",
    optimal_explanation: "",
    starter_code: {},
    topics: [],
    subtopics: [],
    companies: [],
    patterns: [],
    hints: [],
    prerequisites: [],
    test_cases: [],
    function_spec: null,
    judge_mode: "exact",
    float_tolerance: 0,
    time_limit_ms: 0,
    editorials: [],
    follow_ups: [],
    is_favorite: false,
    solved_status: "unsolved",
    confidence: 0,
    last_solved_at: null,
    time_taken_seconds: 0,
    attempts_count: 0,
    success_count: 0,
    created_at: "",
    updated_at: "",
  };
}

const slugify = (s: string) =>
  s.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");

export default function ProblemForm() {
  const { id } = useParams();
  const editing = id && id !== "new";
  const [p, setP] = useState<Problem>(emptyProblem());
  const [slugTouched, setSlugTouched] = useState(false);
  const nav = useNavigate();
  const toast = useToast();

  useEffect(() => {
    if (editing) {
      api.getProblem(Number(id)).then((prob) => {
        setP(prob);
        setSlugTouched(true);
      });
    }
  }, [editing, id]);

  const set = <K extends keyof Problem>(k: K, v: Problem[K]) => setP((x) => ({ ...x, [k]: v }));
  const csv = (arr: string[]) => arr.join(", ");
  const parseCsv = (s: string) => s.split(",").map((x) => x.trim()).filter(Boolean);

  const updateExample = (i: number, patch: Partial<Example>) =>
    set("examples", p.examples.map((e, j) => (j === i ? { ...e, ...patch } : e)));
  const updateCase = (i: number, patch: Partial<TestCase>) =>
    set("test_cases", p.test_cases.map((c, j) => (j === i ? { ...c, ...patch } : c)));
  const updatePrereq = (i: number, patch: Partial<Prerequisite>) =>
    set("prerequisites", p.prerequisites.map((c, j) => (j === i ? { ...c, ...patch } : c)));

  const save = async () => {
    if (!p.title.trim()) return toast("Title is required");
    const slug = p.slug || slugify(p.title);
    try {
      const newId = await api.saveProblem({ ...p, slug });
      toast(editing ? "Problem updated" : "Problem created");
      nav(`/solve/${newId}`);
    } catch (e) {
      toast(`Save failed: ${e}`);
    }
  };

  return (
    <div className="page">
      <div className="row">
        <h1 className="page-title">{editing ? "Edit Problem" : "New Problem"}</h1>
        <span className="spacer" />
        <button className="ghost" onClick={() => nav(-1)}>Cancel</button>
        <button className="primary" onClick={save}>Save</button>
      </div>

      <div className="card" style={{ marginBottom: 14 }}>
        <div className="io-label">Title</div>
        <input
          style={{ width: "100%" }}
          value={p.title}
          onChange={(e) => {
            set("title", e.target.value);
            if (!slugTouched) set("slug", slugify(e.target.value));
          }}
        />
        <div className="row wrap" style={{ marginTop: 10, gap: 14 }}>
          <div>
            <div className="io-label">Slug (unique)</div>
            <input value={p.slug} onChange={(e) => { setSlugTouched(true); set("slug", e.target.value); }} />
          </div>
          <div>
            <div className="io-label">Difficulty</div>
            <select value={p.difficulty} onChange={(e) => set("difficulty", e.target.value as Difficulty)}>
              <option>Easy</option>
              <option>Medium</option>
              <option>Hard</option>
            </select>
          </div>
        </div>
        <div className="row wrap" style={{ marginTop: 10, gap: 14 }}>
          <div style={{ flex: 1 }}>
            <div className="io-label">Topics (comma separated)</div>
            <input style={{ width: "100%" }} value={csv(p.topics)} onChange={(e) => set("topics", parseCsv(e.target.value))} />
          </div>
          <div style={{ flex: 1 }}>
            <div className="io-label">Subtopics</div>
            <input style={{ width: "100%" }} value={csv(p.subtopics)} onChange={(e) => set("subtopics", parseCsv(e.target.value))} />
          </div>
          <div style={{ flex: 1 }}>
            <div className="io-label">Companies</div>
            <input style={{ width: "100%" }} value={csv(p.companies)} onChange={(e) => set("companies", parseCsv(e.target.value))} />
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 14 }}>
        <div className="io-label">Description (Markdown)</div>
        <textarea rows={7} style={{ width: "100%" }} value={p.description} onChange={(e) => set("description", e.target.value)} />
        <div className="io-label" style={{ marginTop: 10 }}>Constraints (one per line)</div>
        <textarea rows={3} style={{ width: "100%" }} value={p.constraints} onChange={(e) => set("constraints", e.target.value)} />
      </div>

      <div className="card" style={{ marginBottom: 14 }}>
        <div className="row">
          <strong>Examples</strong>
          <span className="spacer" />
          <button onClick={() => set("examples", [...p.examples, { input: "", output: "", explanation: "" }])}>+ Add</button>
        </div>
        {p.examples.map((ex, i) => (
          <div key={i} className="grid cols-3" style={{ marginTop: 10 }}>
            <textarea placeholder="Input" rows={2} value={ex.input} onChange={(e) => updateExample(i, { input: e.target.value })} />
            <textarea placeholder="Output" rows={2} value={ex.output} onChange={(e) => updateExample(i, { output: e.target.value })} />
            <textarea placeholder="Explanation" rows={2} value={ex.explanation} onChange={(e) => updateExample(i, { explanation: e.target.value })} />
          </div>
        ))}
      </div>

      <div className="card" style={{ marginBottom: 14 }}>
        <div className="row">
          <strong>Test cases</strong>
          <span className="spacer" />
          <button
            onClick={() =>
              set("test_cases", [
                ...p.test_cases,
                { id: 0, problem_id: p.id, kind: "hidden", name: `Case ${p.test_cases.length + 1}`, input: "", expected_output: "", ordering: p.test_cases.length },
              ])
            }
          >
            + Add
          </button>
        </div>
        <p className="faint" style={{ fontSize: 12 }}>
          <code>hidden</code> cases are used for Submit; <code>example</code> cases power Run. Programs read stdin and print to stdout.
        </p>
        {p.test_cases.map((c, i) => (
          <div key={i} className="card" style={{ marginTop: 10 }}>
            <div className="row" style={{ marginBottom: 6 }}>
              <select value={c.kind} onChange={(e) => updateCase(i, { kind: e.target.value as TestCase["kind"] })}>
                <option value="hidden">hidden</option>
                <option value="example">example</option>
                <option value="user">user</option>
              </select>
              <input placeholder="Name" value={c.name} onChange={(e) => updateCase(i, { name: e.target.value })} />
              <span className="spacer" />
              <button className="ghost danger" onClick={() => set("test_cases", p.test_cases.filter((_, j) => j !== i))}>Remove</button>
            </div>
            <div className="grid cols-2">
              <div>
                <div className="io-label">Input (stdin)</div>
                <textarea rows={3} style={{ width: "100%" }} value={c.input} onChange={(e) => updateCase(i, { input: e.target.value })} />
              </div>
              <div>
                <div className="io-label">Expected output</div>
                <textarea rows={3} style={{ width: "100%" }} value={c.expected_output} onChange={(e) => updateCase(i, { expected_output: e.target.value })} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginBottom: 14 }}>
        <div className="row">
          <strong>Hints (progressive)</strong>
          <span className="spacer" />
          <button onClick={() => set("hints", [...p.hints, ""])}>+ Add</button>
        </div>
        {p.hints.map((h, i) => (
          <div className="row" key={i} style={{ marginTop: 8 }}>
            <span className="dim mono">{i + 1}</span>
            <input style={{ flex: 1 }} value={h} onChange={(e) => set("hints", p.hints.map((x, j) => (j === i ? e.target.value : x)))} />
            <button className="ghost danger" onClick={() => set("hints", p.hints.filter((_, j) => j !== i))}>×</button>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginBottom: 14 }}>
        <div className="row">
          <strong>Prerequisites</strong>
          <span className="spacer" />
          <button
            onClick={() =>
              set("prerequisites", [
                ...p.prerequisites,
                { key: "", name: "", what: "", deep: "", java: "", how: "" },
              ])
            }
          >
            + Add
          </button>
        </div>
        <p className="faint" style={{ fontSize: 12 }}>
          Concepts the solver should know. <code>What it is</code> is a general explanation;{" "}
          <code>How it helps here</code> is specific to this problem.
        </p>
        {p.prerequisites.map((pr, i) => (
          <div key={i} className="card" style={{ marginTop: 10 }}>
            <div className="row" style={{ marginBottom: 6 }}>
              <input
                placeholder="Name (e.g. Hash Maps)"
                value={pr.name}
                onChange={(e) => updatePrereq(i, { name: e.target.value, key: pr.key || slugify(e.target.value) })}
                style={{ flex: 1 }}
              />
              <input
                placeholder="key"
                value={pr.key}
                onChange={(e) => updatePrereq(i, { key: e.target.value })}
                style={{ width: 140 }}
              />
              <button className="ghost danger" onClick={() => set("prerequisites", p.prerequisites.filter((_, j) => j !== i))}>
                Remove
              </button>
            </div>
            <div className="io-label">What it is (one-line gist)</div>
            <textarea rows={2} style={{ width: "100%" }} value={pr.what} onChange={(e) => updatePrereq(i, { what: e.target.value })} />
            <div className="io-label" style={{ marginTop: 6 }}>Deeper dive (mechanics, complexity, pitfalls)</div>
            <textarea rows={2} style={{ width: "100%" }} value={pr.deep} onChange={(e) => updatePrereq(i, { deep: e.target.value })} />
            <div className="io-label" style={{ marginTop: 6 }}>In Java (classes / idioms)</div>
            <textarea rows={2} style={{ width: "100%" }} value={pr.java} onChange={(e) => updatePrereq(i, { java: e.target.value })} />
            <div className="io-label" style={{ marginTop: 6 }}>How it helps solve this problem</div>
            <textarea rows={2} style={{ width: "100%" }} value={pr.how} onChange={(e) => updatePrereq(i, { how: e.target.value })} />
          </div>
        ))}
      </div>

      <div className="card">
        <div className="io-label">Editorial (Markdown)</div>
        <textarea rows={6} style={{ width: "100%" }} value={p.editorial} onChange={(e) => set("editorial", e.target.value)} />
        <div className="row wrap" style={{ marginTop: 10, gap: 14 }}>
          <div>
            <div className="io-label">Optimal time</div>
            <input value={p.optimal_time} onChange={(e) => set("optimal_time", e.target.value)} placeholder="O(n)" />
          </div>
          <div>
            <div className="io-label">Optimal space</div>
            <input value={p.optimal_space} onChange={(e) => set("optimal_space", e.target.value)} placeholder="O(1)" />
          </div>
          <div style={{ flex: 1 }}>
            <div className="io-label">Why optimal</div>
            <input style={{ width: "100%" }} value={p.optimal_explanation} onChange={(e) => set("optimal_explanation", e.target.value)} />
          </div>
        </div>
      </div>
    </div>
  );
}
