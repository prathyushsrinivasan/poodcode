/**
 * Writing or editing a problem (UI_ROADMAP H3).
 *
 * It was one long column of 42 inline-styled inputs, a title check reported
 * in a toast, and plain textareas for Markdown you could not see rendered.
 * Now:
 *   - sections (basics, statement, examples, tests, hints, prerequisites,
 *     editorial) on the reader layout, so the outline rail jumps between them;
 *   - the statement and editorial with a live Markdown preview beside them;
 *   - test cases as a table editor — kind, name, stdin, expected — with
 *     duplicate and reorder;
 *   - every rule in lib/problemForm, its message beside the field, and a
 *     summary in the rail that jumps to each problem;
 *   - leaving with unsaved changes asks first.
 */

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { Difficulty, Example, Prerequisite, Problem, TestCase } from "../types";
import { useToast } from "../components/Toast";
import { Markdown } from "../components/Markdown";
import { ReaderLayout } from "../components/reader/Reader";
import { TrackSkeleton } from "../components/Skeleton";
import { Button, ConfirmDialog, ErrorState, Icon, IconButton, PageHeader, Segmented } from "../components/ui";
import { useCrumb } from "../store";
import { errorsOf, messageFor, moveItem, slugify, validateProblem, type Issue } from "../lib/problemForm";
import { ignore } from "../lib/failures";

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
    checker: "",
    time_limit_ms: 0,
    editorials: [],
    follow_ups: [],
    order: 0,
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

const DIFFICULTIES: Difficulty[] = ["Intro", "Easy", "Medium", "Hard"];
const csv = (arr: string[]) => arr.join(", ");
const parseCsv = (s: string) =>
  s
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);

/** The DOM id of a field, so the issue summary can jump to it. */
const fieldId = (field: string) => `pf-${field.replace(/\./g, "-")}`;

export default function ProblemForm() {
  const { id } = useParams();
  const editing = !!id && id !== "new";
  const [p, setP] = useState<Problem>(emptyProblem);
  const [original, setOriginal] = useState<string>(() => JSON.stringify(emptyProblem()));
  const [loadError, setLoadError] = useState("");
  const [loading, setLoading] = useState(editing);
  const [slugTouched, setSlugTouched] = useState(false);
  const [taken, setTaken] = useState<Map<string, number>>(new Map());
  // Messages appear once a save has been tried, or once a field has been left —
  // not while you are still typing the first letter of a title.
  const [showIssues, setShowIssues] = useState(false);
  const [saving, setSaving] = useState(false);
  const [confirmLeave, setConfirmLeave] = useState(false);
  const nav = useNavigate();
  const toast = useToast();
  useCrumb(editing ? p.title || "Problem" : null, editing ? "Edit problem" : undefined);

  useEffect(() => {
    if (!editing) return;
    setLoading(true);
    api
      .getProblem(Number(id))
      .then((prob) => {
        setP(prob);
        setOriginal(JSON.stringify(prob));
        setSlugTouched(true);
      })
      .catch((e) => setLoadError(String(e)))
      .finally(() => setLoading(false));
  }, [editing, id]);

  // Slugs in use, so a clash is caught here rather than by the database.
  useEffect(() => {
    api
      .listProblems()
      .then((ps) => setTaken(new Map(ps.map((x) => [x.slug, x.id]))))
      .catch(ignore("slug uniqueness is also enforced when saving"));
  }, []);

  const issues = useMemo(() => validateProblem(p, taken), [p, taken]);
  const errors = errorsOf(issues);
  const dirty = JSON.stringify(p) !== original;
  const issue = (field: string) => (showIssues ? messageFor(issues, field) : undefined);

  const set = <K extends keyof Problem>(k: K, v: Problem[K]) => setP((x) => ({ ...x, [k]: v }));
  const updateExample = (i: number, patch: Partial<Example>) =>
    set("examples", p.examples.map((e, j) => (j === i ? { ...e, ...patch } : e)));
  const updateCase = (i: number, patch: Partial<TestCase>) =>
    set("test_cases", p.test_cases.map((c, j) => (j === i ? { ...c, ...patch } : c)));
  const updatePrereq = (i: number, patch: Partial<Prerequisite>) =>
    set("prerequisites", p.prerequisites.map((c, j) => (j === i ? { ...c, ...patch } : c)));

  const jump = (field: string) => {
    // The message sits on the field or, for a list-level issue, its section.
    const el = document.getElementById(fieldId(field)) ?? document.getElementById(fieldId(field.split(".")[0]!));
    el?.scrollIntoView({ behavior: "smooth", block: "center" });
    (el?.querySelector("input, textarea, select") as HTMLElement | null)?.focus({ preventScroll: true });
    if (el && ["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName)) el.focus({ preventScroll: true });
  };

  const save = async () => {
    setShowIssues(true);
    if (errors.length > 0) {
      jump(errors[0]!.field);
      return;
    }
    const slug = p.slug.trim() || slugify(p.title);
    setSaving(true);
    try {
      const newId = await api.saveProblem({
        ...p,
        slug,
        // Case order is their position in the editor.
        test_cases: p.test_cases.map((c, i) => ({ ...c, ordering: i })),
      });
      setOriginal(JSON.stringify(p));
      toast.success(editing ? "Problem updated" : "Problem created");
      nav(`/solve/${newId}`);
    } catch (e) {
      toast.error("Save failed", { detail: String(e) });
    } finally {
      setSaving(false);
    }
  };

  const cancel = () => (dirty ? setConfirmLeave(true) : nav(-1));

  if (loadError) {
    return (
      <div className="page">
        <ErrorState title="That problem could not be loaded." error={loadError} onRetry={() => location.reload()} />
      </div>
    );
  }
  if (loading) return <TrackSkeleton cards={3} />;

  return (
    <div className="page problem-form">
      <ReaderLayout aside={<IssueSummary issues={showIssues ? issues : []} dirty={dirty} onJump={jump} />}>
        <PageHeader
          title={editing ? "Edit problem" : "New problem"}
          subtitle="Programs read stdin and print to stdout. Example cases power Run; hidden cases are for Submit."
        />

        <FormSection title="Basics" icon="document">
          <div className="form-grid">
            <FormField label="Title" id="title" issue={issue("title")} wide>
              <input
                id={fieldId("title")}
                value={p.title}
                onBlur={() => p.title && setShowIssues(true)}
                onChange={(e) => {
                  set("title", e.target.value);
                  if (!slugTouched) set("slug", slugify(e.target.value));
                }}
              />
            </FormField>
            <FormField label="Slug" hint="Unique; used in links and imports." id="slug" issue={issue("slug")}>
              <input
                id={fieldId("slug")}
                className="mono"
                value={p.slug}
                onChange={(e) => {
                  setSlugTouched(true);
                  set("slug", e.target.value);
                }}
              />
            </FormField>
            <FormField label="Difficulty" id="difficulty">
              <Segmented
                label="Difficulty"
                value={p.difficulty}
                onChange={(d) => set("difficulty", d)}
                options={DIFFICULTIES.map((d) => ({ value: d, label: d }))}
              />
            </FormField>
            <FormField label="Topics" hint="Comma separated." id="topics">
              <input id={fieldId("topics")} value={csv(p.topics)} onChange={(e) => set("topics", parseCsv(e.target.value))} />
            </FormField>
            <FormField label="Subtopics" hint="Comma separated." id="subtopics">
              <input id={fieldId("subtopics")} value={csv(p.subtopics)} onChange={(e) => set("subtopics", parseCsv(e.target.value))} />
            </FormField>
            <FormField label="Companies" hint="Comma separated." id="companies">
              <input id={fieldId("companies")} value={csv(p.companies)} onChange={(e) => set("companies", parseCsv(e.target.value))} />
            </FormField>
          </div>
        </FormSection>

        <FormSection title="Statement" icon="learn">
          <MarkdownField
            label="Description"
            id="description"
            value={p.description}
            onChange={(v) => set("description", v)}
            rows={10}
            issue={issue("description")}
          />
          <FormField label="Constraints" hint="One per line." id="constraints" wide>
            <textarea id={fieldId("constraints")} rows={3} value={p.constraints} onChange={(e) => set("constraints", e.target.value)} />
          </FormField>
        </FormSection>

        <FormSection
          title="Examples"
          icon="terminal"
          count={p.examples.length}
          action={
            <Button size="sm" icon="add" onClick={() => set("examples", [...p.examples, { input: "", output: "", explanation: "" }])}>
              Add example
            </Button>
          }
        >
          {p.examples.length === 0 ? (
            <p className="exercise-note">Examples are shown in the statement. They are not judged — add test cases for that.</p>
          ) : (
            <div className="form-table" role="table" aria-label="Examples">
              <div className="form-table-row form-table-head" role="row">
                <span role="columnheader">Input</span>
                <span role="columnheader">Output</span>
                <span role="columnheader">Explanation</span>
                <span role="columnheader" className="sr-only">
                  Actions
                </span>
              </div>
              {p.examples.map((ex, i) => (
                <div key={i} className="form-table-row" role="row" id={fieldId(`examples.${i}`)}>
                  <textarea aria-label={`Example ${i + 1} input`} rows={2} className="mono" value={ex.input} onChange={(e) => updateExample(i, { input: e.target.value })} />
                  <textarea aria-label={`Example ${i + 1} output`} rows={2} className="mono" value={ex.output} onChange={(e) => updateExample(i, { output: e.target.value })} />
                  <textarea aria-label={`Example ${i + 1} explanation`} rows={2} value={ex.explanation} onChange={(e) => updateExample(i, { explanation: e.target.value })} />
                  <IconButton icon="delete" size="sm" label={`Remove example ${i + 1}`} onClick={() => set("examples", p.examples.filter((_, j) => j !== i))} />
                  <RowIssue issue={issue(`examples.${i}`)} />
                </div>
              ))}
            </div>
          )}
        </FormSection>

        <FormSection
          title="Test cases"
          icon="checklist"
          count={p.test_cases.length}
          issue={issue("test_cases")}
          action={
            <Button
              size="sm"
              icon="add"
              onClick={() =>
                set("test_cases", [
                  ...p.test_cases,
                  { id: 0, problem_id: p.id, kind: "hidden", name: `Case ${p.test_cases.length + 1}`, input: "", expected_output: "", ordering: p.test_cases.length },
                ])
              }
            >
              Add case
            </Button>
          }
        >
          <p className="exercise-note">
            <code>example</code> cases power Run and are shown to the solver; <code>hidden</code> cases are only used by
            Submit; <code>user</code> cases are your own scratch inputs.
          </p>
          {p.test_cases.length > 0 && (
            <div className="form-table cases" role="table" aria-label="Test cases">
              <div className="form-table-row form-table-head" role="row">
                <span role="columnheader">Kind</span>
                <span role="columnheader">Name</span>
                <span role="columnheader">Input (stdin)</span>
                <span role="columnheader">Expected output</span>
                <span role="columnheader" className="sr-only">
                  Actions
                </span>
              </div>
              {p.test_cases.map((c, i) => (
                <div key={i} className="form-table-row" role="row" id={fieldId(`test_cases.${i}`)}>
                  <select aria-label={`Case ${i + 1} kind`} value={c.kind} onChange={(e) => updateCase(i, { kind: e.target.value as TestCase["kind"] })}>
                    <option value="example">example</option>
                    <option value="hidden">hidden</option>
                    <option value="user">user</option>
                  </select>
                  <input
                    id={fieldId(`test_cases.${i}.name`)}
                    aria-label={`Case ${i + 1} name`}
                    aria-invalid={!!issue(`test_cases.${i}.name`)}
                    value={c.name}
                    onChange={(e) => updateCase(i, { name: e.target.value })}
                  />
                  <textarea aria-label={`Case ${i + 1} input`} rows={2} className="mono" value={c.input} onChange={(e) => updateCase(i, { input: e.target.value })} />
                  <textarea
                    aria-label={`Case ${i + 1} expected output`}
                    rows={2}
                    className="mono"
                    value={c.expected_output}
                    onChange={(e) => updateCase(i, { expected_output: e.target.value })}
                  />
                  <span className="form-row-actions">
                    <IconButton icon="chevronUp" size="sm" label={`Move case ${i + 1} up`} disabled={i === 0} onClick={() => set("test_cases", moveItem(p.test_cases, i, i - 1))} />
                    <IconButton
                      icon="chevronDown"
                      size="sm"
                      label={`Move case ${i + 1} down`}
                      disabled={i === p.test_cases.length - 1}
                      onClick={() => set("test_cases", moveItem(p.test_cases, i, i + 1))}
                    />
                    <IconButton
                      icon="copy"
                      size="sm"
                      label={`Duplicate case ${i + 1}`}
                      onClick={() => {
                        const copy = { ...c, id: 0, name: `${c.name} (copy)` };
                        set("test_cases", [...p.test_cases.slice(0, i + 1), copy, ...p.test_cases.slice(i + 1)]);
                      }}
                    />
                    <IconButton icon="delete" size="sm" label={`Remove case ${i + 1}`} onClick={() => set("test_cases", p.test_cases.filter((_, j) => j !== i))} />
                  </span>
                  <RowIssue issue={issue(`test_cases.${i}.name`) ?? issue(`test_cases.${i}.expected_output`)} />
                </div>
              ))}
            </div>
          )}
        </FormSection>

        <FormSection
          title="Hints"
          icon="hint"
          count={p.hints.length}
          action={
            <Button size="sm" icon="add" onClick={() => set("hints", [...p.hints, ""])}>
              Add hint
            </Button>
          }
        >
          <p className="exercise-note">Revealed one at a time: a nudge first, the near-answer last.</p>
          <ol className="hint-list">
            {p.hints.map((h, i) => (
              <li key={i} id={fieldId(`hints.${i}`)}>
                <input
                  aria-label={`Hint ${i + 1}`}
                  aria-invalid={!!issue(`hints.${i}`)}
                  value={h}
                  onChange={(e) => set("hints", p.hints.map((x, j) => (j === i ? e.target.value : x)))}
                />
                <IconButton icon="delete" size="sm" label={`Remove hint ${i + 1}`} onClick={() => set("hints", p.hints.filter((_, j) => j !== i))} />
                <RowIssue issue={issue(`hints.${i}`)} />
              </li>
            ))}
          </ol>
        </FormSection>

        <FormSection
          title="Prerequisites"
          icon="layers"
          count={p.prerequisites.length}
          action={
            <Button size="sm" icon="add" onClick={() => set("prerequisites", [...p.prerequisites, { key: "", name: "", what: "", deep: "", java: "", how: "" }])}>
              Add prerequisite
            </Button>
          }
        >
          <p className="exercise-note">
            Concepts the solver should know. <em>What it is</em> is general; <em>how it helps here</em> is about this problem.
          </p>
          {p.prerequisites.map((pr, i) => (
            <div key={i} className="card prereq-card" id={fieldId(`prerequisites.${i}`)}>
              <div className="form-grid">
                <FormField label="Name" id={`prerequisites.${i}.name`} issue={issue(`prerequisites.${i}.name`)} wide>
                  <input
                    id={fieldId(`prerequisites.${i}.name`)}
                    placeholder="Hash Maps"
                    value={pr.name}
                    onChange={(e) => updatePrereq(i, { name: e.target.value, key: pr.key || slugify(e.target.value) })}
                  />
                </FormField>
                <FormField label="Key" id={`prerequisites.${i}.key`} issue={issue(`prerequisites.${i}.key`)}>
                  <input id={fieldId(`prerequisites.${i}.key`)} className="mono" value={pr.key} onChange={(e) => updatePrereq(i, { key: e.target.value })} />
                </FormField>
                <span className="form-card-remove">
                  <Button variant="ghost" size="sm" icon="delete" onClick={() => set("prerequisites", p.prerequisites.filter((_, j) => j !== i))}>
                    Remove
                  </Button>
                </span>
              </div>
              <FormField label="What it is" hint="A one-line gist." id={`prerequisites.${i}.what`} wide>
                <textarea id={fieldId(`prerequisites.${i}.what`)} rows={2} value={pr.what} onChange={(e) => updatePrereq(i, { what: e.target.value })} />
              </FormField>
              <FormField label="Deeper dive" hint="Mechanics, complexity, pitfalls." id={`prerequisites.${i}.deep`} wide>
                <textarea id={fieldId(`prerequisites.${i}.deep`)} rows={2} value={pr.deep} onChange={(e) => updatePrereq(i, { deep: e.target.value })} />
              </FormField>
              <FormField label="In Java" hint="Classes and idioms." id={`prerequisites.${i}.java`} wide>
                <textarea id={fieldId(`prerequisites.${i}.java`)} rows={2} value={pr.java} onChange={(e) => updatePrereq(i, { java: e.target.value })} />
              </FormField>
              <FormField label="How it helps here" id={`prerequisites.${i}.how`} wide>
                <textarea id={fieldId(`prerequisites.${i}.how`)} rows={2} value={pr.how} onChange={(e) => updatePrereq(i, { how: e.target.value })} />
              </FormField>
            </div>
          ))}
        </FormSection>

        <FormSection title="Editorial" icon="notes">
          <MarkdownField label="Editorial" id="editorial" value={p.editorial} onChange={(v) => set("editorial", v)} rows={8} />
          <div className="form-grid">
            <FormField label="Optimal time" id="optimal_time">
              <input id={fieldId("optimal_time")} className="mono" value={p.optimal_time} onChange={(e) => set("optimal_time", e.target.value)} placeholder="O(n)" />
            </FormField>
            <FormField label="Optimal space" id="optimal_space">
              <input id={fieldId("optimal_space")} className="mono" value={p.optimal_space} onChange={(e) => set("optimal_space", e.target.value)} placeholder="O(1)" />
            </FormField>
            <FormField label="Why it is optimal" id="optimal_explanation" wide>
              <input id={fieldId("optimal_explanation")} value={p.optimal_explanation} onChange={(e) => set("optimal_explanation", e.target.value)} />
            </FormField>
          </div>
        </FormSection>

        <div className="form-actions">
          {showIssues && errors.length > 0 && (
            <span className="is-bad form-actions-note" role="alert">
              <Icon name="warning" size={14} /> {errors.length} thing{errors.length === 1 ? "" : "s"} to fix before saving
            </span>
          )}
          {dirty && !(showIssues && errors.length > 0) && <span className="faint form-actions-note">Unsaved changes</span>}
          <span className="spacer" />
          <Button variant="ghost" onClick={cancel}>
            Cancel
          </Button>
          <Button variant="primary" icon="save" onClick={save} loading={saving}>
            {editing ? "Save changes" : "Create problem"}
          </Button>
        </div>
      </ReaderLayout>

      <ConfirmDialog
        open={confirmLeave}
        onClose={() => setConfirmLeave(false)}
        onConfirm={() => {
          setConfirmLeave(false);
          nav(-1);
        }}
        title="Leave without saving?"
        consequence="The changes you made to this problem are not saved anywhere and will be lost."
        confirmLabel="Discard changes"
      />
    </div>
  );
}

function FormSection({
  title,
  icon,
  count,
  action,
  issue,
  children,
}: {
  title: string;
  icon: Parameters<typeof Icon>[0]["name"];
  count?: number;
  action?: ReactNode;
  issue?: Issue;
  children: ReactNode;
}) {
  const id = fieldId(title.toLowerCase().replace(/\s+/g, "_"));
  return (
    <section className="card form-section" data-outline={title} id={id} aria-labelledby={`${id}-h`}>
      <header className="form-section-head">
        <h2 id={`${id}-h`} className="card-title">
          <Icon name={icon} size={16} className="card-title-icon" /> {title}
          {count !== undefined && <span className="tab-count">{count}</span>}
        </h2>
        {action}
      </header>
      {issue && <FieldMessage issue={issue} />}
      {children}
    </section>
  );
}

function FormField({
  label,
  hint,
  id,
  issue,
  wide = false,
  children,
}: {
  label: string;
  hint?: string;
  id: string;
  issue?: Issue;
  wide?: boolean;
  children: ReactNode;
}) {
  return (
    <div className={`form-field ${wide ? "wide" : ""} ${issue?.severity === "error" ? "has-error" : ""}`}>
      <label htmlFor={fieldId(id)} className="form-label">
        {label}
        {hint && <span className="field-hint"> {hint}</span>}
      </label>
      {children}
      {issue && <FieldMessage issue={issue} />}
    </div>
  );
}

function FieldMessage({ issue }: { issue: Issue }) {
  return (
    <span className={`field-error ${issue.severity === "warning" ? "is-warning" : ""}`} role={issue.severity === "error" ? "alert" : undefined}>
      <Icon name={issue.severity === "error" ? "failed" : "warning"} size={12} /> {issue.message}
    </span>
  );
}

function RowIssue({ issue }: { issue?: Issue }) {
  if (!issue) return null;
  return (
    <span className="form-row-issue">
      <FieldMessage issue={issue} />
    </span>
  );
}

/** A Markdown textarea with the rendered result beside it. */
function MarkdownField({
  label,
  id,
  value,
  onChange,
  rows,
  issue,
}: {
  label: string;
  id: string;
  value: string;
  onChange: (v: string) => void;
  rows: number;
  issue?: Issue;
}) {
  const [view, setView] = useState<"split" | "write" | "preview">("split");
  return (
    <div className={`form-field wide md-field ${issue?.severity === "error" ? "has-error" : ""}`}>
      <div className="md-field-head">
        <label htmlFor={fieldId(id)} className="form-label">
          {label} <span className="field-hint">Markdown</span>
        </label>
        <Segmented
          label={`${label} view`}
          value={view}
          onChange={setView}
          options={[
            { value: "write", label: "Write" },
            { value: "split", label: "Split" },
            { value: "preview", label: "Preview" },
          ]}
        />
      </div>
      <div className={`md-field-body is-${view}`}>
        {view !== "preview" && <textarea id={fieldId(id)} rows={rows} value={value} onChange={(e) => onChange(e.target.value)} />}
        {view !== "write" && (
          <div className="md-preview" aria-label={`${label} preview`}>
            {value.trim() ? <Markdown>{value}</Markdown> : <p className="faint">Nothing to preview yet.</p>}
          </div>
        )}
      </div>
      {issue && <FieldMessage issue={issue} />}
    </div>
  );
}

/** The rail: what is left to fix, each a link to its field. */
function IssueSummary({ issues, dirty, onJump }: { issues: Issue[]; dirty: boolean; onJump: (field: string) => void }) {
  const errs = issues.filter((i) => i.severity === "error");
  const warns = issues.filter((i) => i.severity === "warning");
  return (
    <div className={`read-status ${issues.length === 0 ? "" : "has-issues"}`} role="status">
      <div className="read-status-head">
        <Icon name={errs.length ? "warning" : "done"} size={16} className={errs.length ? "is-bad" : "is-good"} />
        <strong>{errs.length ? `${errs.length} to fix` : issues.length ? "Ready, with notes" : dirty ? "Unsaved" : "Nothing to fix"}</strong>
      </div>
      {issues.length > 0 && (
        <ul className="read-steps">
          {[...errs, ...warns].slice(0, 8).map((i, k) => (
            <li key={k} className={i.severity === "error" ? "is-bad" : "is-warn"}>
              <Icon name={i.severity === "error" ? "failed" : "warning"} size={13} />
              <button type="button" className="link-button issue-link" onClick={() => onJump(i.field)}>
                {i.message}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
