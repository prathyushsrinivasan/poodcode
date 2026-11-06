import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Button, Card, ErrorState, PageHeader, ProgressBar } from "../../components/ui";
import { api } from "../../api";
import { STUDY_QUESTION_MAP } from "../../data/n2Study";
import { MISTAKE_REASONS, beginQuestions, parseStudy, selectRound, startSession, STUDY_KEY, type StudyState } from "../../lib/n2Study";
import { conceptProgress, COURSE_LINKS, filterReview, JLPT_BACKUP_KEYS, JLPT_CATALOG, newExamples, parseJlptBackup, planPractice, reviewInventory, startPlannedPractice, type JlptBackup, type MockConfig, type PracticePlan, type ReviewItem, type WorkspaceFilter } from "../../lib/jlptWorkspace";
import { n2StudyStore, useN2Study, type N2StudyController } from "../../lib/useN2Study";
import { useJlptPreference } from "../../lib/useJlptPractice";
import { StudyStatus, STUDY_ROOT } from "./StudyShared";
import JlptQuestionTools from "../../components/JlptQuestionTools";
import JlptListPicker from "../../components/JlptListPicker";
import { withJlptJournals } from "../../lib/jlptPersistence";
import { flushN2Progress } from "../../lib/useN2Progress";
import { flushKanjiProgress } from "../../lib/useKanjiProgress";
import { flushReadingProgress } from "../../lib/useReadingProgress";

const TABS = ["review", "practice", "progress", "search", "vocabulary", "backup"] as const;
export default function StudyWorkspace() {
  const state = useN2Study();
  const [params, setParams] = useSearchParams();
  const tab = TABS.find((t) => t === params.get("tab")) ?? "review";
  const [settings, setSettings] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState("");
  const [refresh, setRefresh] = useState(0);
  const [now, setNow] = useState(Date.now);
  useEffect(() => { let live = true; setError(""); api.getSettings().then((s) => { if (live) { setSettings(s); setNow(Date.now()); } }).catch((e) => { if (live) setError(String(e)); }); return () => { live = false; }; }, [refresh]);
  useEffect(() => { const timer = window.setInterval(() => setNow(Date.now()), 30_000); return () => window.clearInterval(timer); }, []);
  const inventory = useMemo(() => state.data && settings ? reviewInventory(state.data, withJlptJournals(settings, JLPT_BACKUP_KEYS), now) : [], [state.data, settings, now]);
  return <div className="page n2-page study-page">
    <Link className="ghost-link" to={STUDY_ROOT}>← JLPT</Link>
    <PageHeader title="JLPT review & practice" subtitle="One place for due work, saved questions and your next round." />
    <StudyStatus state={state} />
    <nav className="n2-actions jlpt-workspace-nav" aria-label="JLPT workspace">{TABS.map((t) => <Button key={t} variant={tab === t ? "primary" : "ghost"} aria-current={tab === t ? "page" : undefined} onClick={() => setParams({ tab: t })}>{t === "backup" ? "Export / import" : t[0].toUpperCase() + t.slice(1)}</Button>)}</nav>
    {error && <ErrorState title="Course progress could not be read" error={error} onRetry={() => setRefresh((n) => n + 1)} />}
    {state.data && settings && <>
      {state.data.session && state.data.session.phase !== "summary" && <Card><p>A round is saved: {state.data.session.title}</p><Link className="btn primary" to={`${STUDY_ROOT}/study`}>Continue saved round →</Link></Card>}
      {tab === "review" && <ReviewPanel state={state as N2StudyController} items={inventory} />}
      {tab === "practice" && <PracticePanel state={state as N2StudyController} items={inventory} />}
      {tab === "progress" && <ProgressPanel data={state.data} />}
      {tab === "search" && <SearchPanel state={state as N2StudyController} items={inventory} />}
      {tab === "vocabulary" && <VocabularyPanel state={state as N2StudyController} items={inventory} />}
      {tab === "backup" && <BackupPanel state={state as N2StudyController} onImported={() => setRefresh((n) => n + 1)} />}
    </>}
  </div>;
}

function startReview(state: N2StudyController, ids: string[], title: string, navigate: ReturnType<typeof useNavigate>) {
  if (state.data.session && state.data.session.phase !== "summary") { navigate(`${STUDY_ROOT}/study`); return; }
  state.update((p) => beginQuestions(startSession(p, ids, "learn", title)));
  navigate(`${STUDY_ROOT}/study`);
}
const FILTERS: { id: WorkspaceFilter; label: string }[] = [{ id: "due", label: "Due now" }, { id: "saved", label: "Saved questions" }, { id: "mistakes", label: "Mistake notebook" }, { id: "reason", label: "Mistake reason" }, { id: "confident", label: "Confident mistakes" }, { id: "slow", label: "Slow answers" }, { id: "trouble", label: "Persistent trouble" }];
function ReviewPanel({ state, items }: { state: N2StudyController; items: ReviewItem[] }) {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<WorkspaceFilter>("due");
  const [reason, setReason] = useState("");
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(0);
  const filtered = filterReview(items, filter, reason, query);
  const ids = selectRound(state.data, filtered.flatMap((i) => !i.nativePending && STUDY_QUESTION_MAP.get(i.id) ? [STUDY_QUESTION_MAP.get(i.id)!] : []), state.data.preferences.roundSize);
  const examples = newExamples(state.data, filtered.filter((i) => i.mistakes).map((i) => i.id), state.data.preferences.roundSize);
  const due = items.filter((i) => i.due).length;
  const current = Math.min(page, Math.max(0, Math.ceil(filtered.length / 15) - 1));
  return <>
    <Card><h2>{due} due for review</h2><p>Includes scheduled guided questions, saved reading words and unfinished course mistakes. Legacy mistakes without a schedule remain due until corrected.</p>
      <div className="n2-actions"><Button variant="primary" disabled={!ids.length} onClick={() => startReview(state, ids, "JLPT review", navigate)}>Review {ids.length} guided questions</Button><Link to={`${STUDY_ROOT}/reading/vocabulary`}>Review saved reading words →</Link></div>
    </Card>
    <div className="jlpt-workspace-filters"><label className="study-field">Review collection<select value={filter} onChange={(e) => { setFilter(e.target.value as WorkspaceFilter); setPage(0); }}>{FILTERS.map((f) => <option key={f.id} value={f.id}>{f.label} · {filterReview(items, f.id).length}</option>)}</select></label>
      {filter === "reason" && <label className="study-field">Mistake reason<select aria-label="Mistake reason" value={reason} onChange={(e) => { setReason(e.target.value); setPage(0); }}><option value="">All recorded reasons</option>{MISTAKE_REASONS.map((r) => <option key={r}>{r}</option>)}</select></label>}
      <label className="study-field">Find in collection<input type="search" value={query} onChange={(e) => { setQuery(e.target.value); setPage(0); }} /></label></div>
    {(filter === "slow" || filter === "confident") && <p className="n2-meta">Confidence and answer timing are recorded in guided rounds. Older course records contain correctness only.</p>}
    {filter === "trouble" && <p className="n2-meta">Questions still needing review after at least three misses. Corrected questions leave this set.</p>}
    <p role="status">{filtered.length} items in this collection</p>
    {!!examples.length && <Button onClick={() => startReview(state, examples, "New examples for missed concepts", navigate)}>Try {examples.length} new examples for missed concepts</Button>}
    <div className="study-stack">{filtered.slice(current * 15, current * 15 + 15).map((item) => <Card key={item.id}>
      <p className="n2-meta">{item.source} · {item.concept}{item.mistakes > 0 ? ` · ${item.mistakes} misses` : ""}</p><h3 lang="ja">{item.title}</h3>
      {item.reason && <p><strong>{item.reason}</strong></p>}{item.note && <p>{item.note}</p>}
      <div className="n2-actions">{!item.nativePending && STUDY_QUESTION_MAP.has(item.id) ? <Button onClick={() => startReview(state, [item.id], "Revisit a question", navigate)}>Practice question →</Button> : <Link className="btn" to={item.href}>Open practice →</Link>}</div>
      <JlptQuestionTools id={item.id} review />
    </Card>)}</div>
    {!filtered.length && <Card><p>No items in this collection yet. Your practice results and saved questions will appear here.</p></Card>}
    {filtered.length > 15 && <div className="n2-actions"><Button disabled={!current} onClick={() => setPage(current - 1)}>Previous</Button><span>Page {current + 1}</span><Button disabled={(current + 1) * 15 >= filtered.length} onClick={() => setPage(current + 1)}>Next</Button></div>}
  </>;
}

export function RoundSize({ state }: { state: N2StudyController }) {
  return <label className="study-field">Round size<select aria-label="Round size" value={state.data.preferences.roundSize} onChange={(e) => state.update((p) => ({ ...p, preferences: { ...p.preferences, roundSize: Number(e.target.value) } }))}>{[3, 5, 10, 15, 20].map((n) => <option key={n} value={n}>{n} questions</option>)}</select></label>;
}
function PracticePanel({ state, items }: { state: N2StudyController; items: ReviewItem[] }) {
  const navigate = useNavigate();
  const [kind, setKind] = useState<PracticePlan>("daily");
  const [vocabulary, setVocabulary] = useJlptPreference("mock", "vocabulary", 20);
  const [grammar, setGrammar] = useJlptPreference("mock", "grammar", 15);
  const [reading, setReading] = useJlptPreference("mock", "reading", 10);
  const [minutes, setMinutes] = useJlptPreference("mock", "minutes", 90);
  const [fresh, setFresh] = useJlptPreference("mock", "fresh", true);
  const [seed] = useState(Date.now);
  const mock = kind === "mini" || kind === "written";
  const config: MockConfig = kind === "mini" ? { vocabulary: 4, grammar: 3, reading: 3, minutes: 15, fresh } : { vocabulary, grammar, reading, minutes, fresh };
  const seen = new Set(items.filter((i) => i.attempted).map((i) => i.id));
  const ids = planPractice(state.data, kind, config, seen, seed);
  const requested = config.vocabulary + config.grammar + config.reading;
  const countsValid = [config.vocabulary, config.grammar, config.reading].every((n) => Number.isInteger(n) && n >= 0 && n <= 60) && requested > 0 && requested <= 150 && Number.isInteger(config.minutes) && config.minutes >= 1 && config.minutes <= 240;
  const shortage = mock && ids.length < requested;
  const active = state.data.session && state.data.session.phase !== "summary";
  return <Card>
    <h2>Choose your next round</h2>
    <label className="study-field">Practice type<select value={kind} onChange={(e) => setKind(e.target.value as PracticePlan)}><option value="daily">Mixed daily practice</option><option value="diagnostic">Short diagnostic · 12 questions</option><option value="weak">Weak-area round</option><option value="mini">Mini written mock · 10 questions / 15 minutes</option><option value="written">Configurable N2 written mock</option></select></label>
    <p>{kind === "daily" ? "Mix sections, prioritizing due work and mistakes, then unseen questions." : kind === "diagnostic" ? "Sample all six skill sections. Results suggest where to practice next; a short sample is an estimate." : kind === "weak" ? "Practise concepts below 80% independent accuracy, including new examples of those concepts." : "Vocabulary, grammar and reading in one timed round. Answers stay hidden until submission; flags and an answer sheet help you return to unfinished questions."}</p>
    <details className="jlpt-tips"><summary>Practice options</summary><RoundSize state={state} />
      {mock && <label className="dokkai-check"><input type="checkbox" checked={fresh} onChange={(e) => setFresh(e.target.checked)} />Fresh questions only</label>}
      {kind === "written" && <div className="jlpt-workspace-filters">{([['Vocabulary questions', vocabulary, setVocabulary], ['Grammar questions', grammar, setGrammar], ['Reading questions', reading, setReading], ['Minutes', minutes, setMinutes]] as const).map(([label, value, change]) => <label className="study-field" key={label}>{label}<input type="number" min={label === "Minutes" ? 1 : 0} max={label === "Minutes" ? 240 : 60} value={value} onChange={(e) => change(Number(e.target.value))} /></label>)}</div>}
    </details>
    <p role="status">{ids.length} questions ready{mock ? ` · ${config.minutes} minutes` : ""}</p>
    {shortage && <p role="status">There are too few matching questions for this configuration. Reduce the counts or turn off Fresh questions only.</p>}
    {!countsValid && mock && <p role="alert">Choose 1–150 questions total, up to 60 per section, and 1–240 minutes.</p>}
    {kind === "weak" && !ids.length && <p>Complete a diagnostic or a daily round to identify weak concepts.</p>}
    {mock && <p className="n2-meta">Original written practice with a custom length and budget. This is not an official paper or scaled score; listening is excluded.</p>}
    <Button variant="primary" disabled={!active && (!ids.length || shortage || mock && !countsValid)} onClick={() => { if (!active) state.update((p) => startPlannedPractice(p, ids, kind, config.minutes)); navigate(`${STUDY_ROOT}/study`); }}>{active ? "Continue saved round" : "Start round"} →</Button>
  </Card>;
}
function ProgressPanel({ data }: { data: StudyState }) {
  const concepts = conceptProgress(data);
  return <>
    <Card><h2>Concept-level progress</h2><p>Accuracy counts independent correct answers across all attempts; assisted answers still need review. Retention requires spaced successful reviews. Concepts with little practice need a larger sample.</p></Card>
    <div className="n2-grid">{concepts.map((c) => <Card key={c.id}><h3>{c.title}</h3><p>{c.seen}/{c.total} seen · {c.retained} retained · {c.attempts ? `${Math.round(c.correct / c.attempts * 100)}% independent accuracy (${c.attempts} attempts)` : "No attempts yet"}</p><ProgressBar value={c.retained} max={c.total} label={`${c.title}: retained questions`} /><Link to={`${STUDY_ROOT}/lesson/${c.id}`}>Practice this concept →</Link></Card>)}</div>
  </>;
}
function SearchPanel({ state, items }: { state: N2StudyController; items: ReviewItem[] }) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("");
  const catalog = [...JLPT_CATALOG, ...items.filter((i) => i.source === "Saved word")];
  const matches = query.trim() ? catalog.filter((i) => (!source || i.source === source) && `${i.title} ${i.search} ${i.concept}`.normalize("NFKC").toLowerCase().includes(query.trim().normalize("NFKC").toLowerCase())) : [];
  return <>
    <label className="study-field">Search all JLPT content<input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Japanese, kana, meaning, grammar or topic" /></label>
    <label className="study-field">Content source<select value={source} onChange={(e) => setSource(e.target.value)}><option value="">All sources</option>{[...new Set(catalog.map((i) => i.source))].map((s) => <option key={s}>{s}</option>)}</select></label>
    <p role="status">{query.trim() ? `${matches.length} results · showing up to 50; refine your search to narrow the list.` : `Search ${JLPT_CATALOG.length} exercises across all JLPT courses.`}</p>
    <div className="study-stack">{matches.slice(0, 50).map((i) => <Card key={i.id}><p className="n2-meta">{i.source} · {i.concept}</p><h3 lang="ja">{i.title}</h3><div className="n2-actions">{STUDY_QUESTION_MAP.has(i.id) ? <Button onClick={() => startReview(state, [i.id], "Practice from search", navigate)}>Practice question →</Button> : <Link className="btn" to={i.href}>Open practice →</Link>}<JlptQuestionTools id={i.id} /></div>{i.vocabulary && <AddToList state={state} id={i.alias ?? i.id} />}</Card>)}</div>
    <p className="n2-meta">{items.filter((i) => i.attempted).length} distinct exercises practiced.</p>
    <div className="n2-actions">{COURSE_LINKS.map((l) => <Link key={l.href} to={l.href}>{l.label} →</Link>)}</div>
  </>;
}
function AddToList({ state, id }: { state: N2StudyController; id: string }) {
  return state.data && <JlptListPicker id={id} />;
}
function VocabularyPanel({ state, items }: { state: N2StudyController; items: ReviewItem[] }) {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [selected, setSelected] = useState("");
  const [query, setQuery] = useState("");
  const lists = state.data.workspace.lists;
  const list = lists.find((l) => l.id === selected) ?? lists[0];
  const members = list ? items.filter((i) => list.items.includes(i.id)) : [];
  const candidates = query.trim() ? items.filter((i) => i.vocabulary && `${i.title} ${i.search}`.toLowerCase().includes(query.trim().toLowerCase())).slice(0, 20) : [];
  const ids = selectRound(state.data, members.flatMap((i) => !i.nativePending && STUDY_QUESTION_MAP.get(i.id) ? [STUDY_QUESTION_MAP.get(i.id)!] : []), state.data.preferences.roundSize);
  return <>
    <Card><h2>Personal vocabulary lists</h2><p>Collect words and vocabulary exercises from search or saved reading vocabulary. Lists share existing progress and never create another schedule for the same item.</p>
      <form className="n2-actions" onSubmit={(e) => { e.preventDefault(); if (!name.trim() || lists.length >= 100) return; const id = crypto.randomUUID(); state.update((p) => ({ ...p, workspace: { ...p.workspace, lists: [...p.workspace.lists, { id, name: name.trim(), items: [] }] } })); setSelected(id); setName(""); }}><label className="study-field">New list name<input value={name} maxLength={80} onChange={(e) => setName(e.target.value)} /></label><Button type="submit" disabled={!name.trim() || lists.length >= 100}>Create list</Button></form>
      {!!lists.length && <label className="study-field">Vocabulary list<select value={list?.id ?? ""} onChange={(e) => setSelected(e.target.value)}>{lists.map((l) => <option key={l.id} value={l.id}>{l.name} · {l.items.length} items</option>)}</select></label>}
      {list && <><label className="study-field">Rename list<input value={list.name} maxLength={80} onChange={(e) => { const value = e.target.value; if (value.trim()) state.update((p) => ({ ...p, workspace: { ...p.workspace, lists: p.workspace.lists.map((l) => l.id === list.id ? { ...l, name: value } : l) } })); }} /></label><Button disabled={!ids.length} onClick={() => startReview(state, ids, list.name, navigate)}>Practice {ids.length} guided items</Button></>}
      <div className="n2-actions">{members.some((i) => i.source === "Word Builder") && <Link className="btn" to={`${STUDY_ROOT}/kanji/mixed?ids=${encodeURIComponent(members.filter((i) => i.source === "Word Builder").map((i) => i.id.slice(6)).join(","))}&size=${state.data.preferences.roundSize}`}>Practice Word Builder list →</Link>}
        {members.some((i) => i.source === "Affixes") && <Link className="btn" to={`${STUDY_ROOT}/affixes/mixed?ids=${encodeURIComponent(members.filter((i) => i.source === "Affixes").map((i) => i.id.slice(6)).join(","))}&size=${state.data.preferences.roundSize}`}>Practice affix list →</Link>}
        {members.some((i) => i.source === "Saved word") && <Link className="btn" to={`${STUDY_ROOT}/reading/vocabulary?${new URLSearchParams(members.filter((i) => i.source === "Saved word").map((i) => ["word", i.id.slice(5)]))}`}>Review saved word list →</Link>}</div>
    </Card>
    {list && <><label className="study-field">Find words to add<input type="search" value={query} onChange={(e) => setQuery(e.target.value)} /></label>{candidates.map((i) => <div className="card" key={i.id}><span lang="ja">{i.title}</span> <AddToList state={state} id={i.id} /></div>)}
      <h2>{list.name} · {members.length} available items</h2>{members.map((i) => <Card key={i.id}><h3 lang="ja">{i.title}</h3><p>{i.source}</p><div className="n2-actions"><Link to={i.href}>Open word practice →</Link><Button onClick={() => state.update((p) => ({ ...p, workspace: { ...p.workspace, lists: p.workspace.lists.map((l) => l.id === list.id ? { ...l, items: l.items.filter((id) => id !== i.id) } : l) } }))}>Remove from list</Button></div></Card>)}
      {!members.length && <p>This list is empty. Search for words above to add them.</p>}
      <details><summary>Delete this list</summary><p>Removes the list and its membership; study progress is kept.</p><Button onClick={() => state.update((p) => ({ ...p, workspace: { ...p.workspace, lists: p.workspace.lists.filter((l) => l.id !== list.id) } }))}>Delete {list.name}</Button></details>
    </>}
  </>;
}

function downloadBackup(backup: JlptBackup, filename = "jlpt-progress.json") {
  const url = URL.createObjectURL(new Blob([JSON.stringify(backup, null, 2)], { type: "application/json" }));
  const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; anchor.click(); window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
async function captureBackup(): Promise<JlptBackup> {
  await n2StudyStore.flush();
  await Promise.allSettled([flushN2Progress(), flushKanjiProgress(), flushReadingProgress()]);
  const settings = withJlptJournals(await api.getSettings(), JLPT_BACKUP_KEYS.filter((k) => k !== STUDY_KEY));
  const current = n2StudyStore.getSnapshot();
  if (!current.data) throw new Error("Study progress has not loaded.");
  return { format: "poodcode-jlpt", version: 1, exportedAt: new Date().toISOString(), settings: { ...Object.fromEntries(JLPT_BACKUP_KEYS.filter((k) => settings[k] !== undefined && settings[k] !== "").map((k) => [k, settings[k]])), [STUDY_KEY]: JSON.stringify(current.data) }, recovery: Object.fromEntries(Object.keys(localStorage).filter((k) => k.startsWith("jlpt-session:")).map((k) => [k, localStorage.getItem(k)!])) };
}
function BackupPanel({ state, onImported }: { state: N2StudyController; onImported: () => void }) {
  const [preview, setPreview] = useState<JlptBackup | null>(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  async function run(task: () => Promise<void>) { setBusy(true); setError(""); setStatus(""); try { await task(); } catch (e) { setError(String(e)); } finally { setBusy(false); } }
  return <Card><h2>Export / import JLPT progress</h2><p>Includes all six course stores, saved questions, mistake notes, vocabulary lists, preferences and session recovery. Imports replace only the JLPT data shown below. A copy of the current data is saved before replacement.</p>
    <div className="n2-actions"><Button disabled={busy} onClick={() => void run(async () => { downloadBackup(await captureBackup()); setStatus("JLPT backup downloaded."); })}>Export JLPT progress</Button>
      <Button disabled={busy} onClick={() => void run(async () => { const raw = localStorage.getItem("jlpt-before-import"); if (!raw) throw new Error("No pre-import backup is available."); downloadBackup(parseJlptBackup(raw), "jlpt-before-import.json"); setStatus("Pre-import backup downloaded."); })}>Download pre-import backup</Button></div>
    <label className="study-field">Choose a JLPT backup<input type="file" accept="application/json,.json" disabled={busy} onChange={(e) => { const file = e.target.files?.[0]; setPreview(null); if (file) void run(async () => { if (file.size > 25_000_000) throw new Error("Backup exceeds 25 MB."); setPreview(parseJlptBackup(await file.text())); }); }} /></label>
    {preview && <div className="study-callout"><h3>Ready to import</h3><p>{Object.keys(preview.settings).length} course snapshots · {parseStudy(preview.settings[STUDY_KEY]).attempts.length} guided attempts · {Object.keys(preview.recovery).length} session fields. Missing courses are kept. Existing data in these courses will be replaced.</p>
      <Button disabled={busy || !!state.data.session && state.data.session.phase !== "summary"} onClick={() => void run(async () => {
        const before = await captureBackup();
        localStorage.setItem("jlpt-before-import", JSON.stringify(before));
        const written: string[] = [];
        try {
          for (const [key, value] of Object.entries(preview.settings)) { if (key === STUDY_KEY) continue; written.push(key); await api.setSetting(key, value); }
          for (const key of written) localStorage.removeItem(`${key}-recovery`);
          const imported = parseStudy(preview.settings[STUDY_KEY]);
          if (imported.session?.mode === "learn" && imported.session.phase !== "summary") imported.session.paused = true;
          state.update(() => imported); await n2StudyStore.flush();
          if (n2StudyStore.getSnapshot().saveError) throw new Error(n2StudyStore.getSnapshot().saveError);
          for (const key of Object.keys(localStorage)) if (key.startsWith("jlpt-session:")) localStorage.removeItem(key);
          for (const [key, value] of Object.entries(preview.recovery)) localStorage.setItem(key, value);
          setPreview(null); onImported(); setStatus("JLPT progress imported. Your pre-import backup is available above.");
        } catch (e) {
          const failures: string[] = [];
          for (const key of written) { try { await api.setSetting(key, before.settings[key] ?? ""); } catch { failures.push(key); } }
          state.update(() => parseStudy(before.settings[STUDY_KEY])); await n2StudyStore.flush();
          for (const key of Object.keys(localStorage)) if (key.startsWith("jlpt-session:")) localStorage.removeItem(key);
          for (const [key, value] of Object.entries(before.recovery)) localStorage.setItem(key, value);
          throw new Error(`${String(e)} ${failures.length ? "Some courses could not be restored. Download the pre-import backup and retry." : "Previous progress was restored."}`);
        }
      })}>Replace the listed JLPT progress</Button>
      {state.data.session && state.data.session.phase !== "summary" && <p>Finish the active round before importing.</p>}
    </div>}
    {error && <p role="alert">{error}</p>}{status && <p role="status">{status}</p>}
  </Card>;
}
