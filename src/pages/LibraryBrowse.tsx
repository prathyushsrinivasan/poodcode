/**
 * Browse: the whole problem bank, filterable (UI_ROADMAP H1, H2).
 *
 * A flat table answers "find the one I mean" and never answers "what should I
 * learn next" — that is the curriculum at `/library`. What Browse gains from
 * the curriculum is one column: which unit teaches each problem, so a problem
 * met here has a way back to its technique.
 *
 * H1: saved filter presets (a question you ask every week is one click), a
 * column chooser, and keyboard rows — ↑/↓/PageUp/PageDown/Home/End move, Enter
 * opens. Filters, presets and columns are remembered.
 *
 * H2: all 799 rows used to be in the DOM at once. Rows now arrive a hundred at
 * a time as you scroll, and the count shown is remembered for the session, so
 * coming back from a problem restores both the rows and the scroll position.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { open as openDialog, save as saveDialog } from "@tauri-apps/plugin-dialog";
import { api } from "../api";
import type { CurriculumUnit, Difficulty, Problem, SolvedStatus } from "../types";
import { applyFilter, emptyFilter, type ProblemFilter, type SortKey, type UnitLookup } from "../lib/filters";
import {
  BUILTIN_PRESETS,
  COLUMNS,
  activeFilterCount,
  deletePreset,
  matchesPreset,
  nextRow,
  parseColumns,
  parsePresets,
  savePreset,
  toggleColumn,
  type BrowseState,
  type ColumnKey,
  type Preset,
} from "../lib/browse";
import { hydrate } from "../lib/curriculum";
import { currentMasteryWeek, masteryWeekBySlug } from "../lib/mastery";
import { loadCurriculumSeed } from "../components/CurriculumData";
import { Confidence, DiffBadge } from "../components/common";
import { relativeDate } from "../lib/format";
import { useToast } from "../components/Toast";
import { Badge, Button, Chip, EmptyState, Icon, IconButton, PageHeader } from "../components/ui";
import { loadFailed, saveFailed } from "../lib/failures";

const STATUS_LABEL: Record<SolvedStatus, string> = {
  unsolved: "—",
  attempted: "Attempted",
  solved: "Solved",
};

const FILTER_KEY = "poodcode:browse-filter";
const PRESETS_KEY = "poodcode:browse-presets";
const COLUMNS_KEY = "poodcode:browse-columns";
const PAGE = 100;

/** Rows rendered, remembered for the session so Back restores the same table. */
let renderedRows = PAGE;

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}
function write(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* remembered UI state is a convenience, not a requirement */
  }
}

/** The last filter, or a clean one. Merged onto `emptyFilter` so a stored
 * filter from an older shape cannot leave a field undefined. */
function readFilter(): ProblemFilter {
  try {
    const raw = read(FILTER_KEY);
    return raw ? { ...emptyFilter, ...JSON.parse(raw) } : emptyFilter;
  } catch {
    return emptyFilter;
  }
}

export default function LibraryBrowse() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [topics, setTopics] = useState<string[]>([]);
  const [companies, setCompanies] = useState<string[]>([]);
  const [unitBySlug, setUnitBySlug] = useState<Map<string, CurriculumUnit>>(new Map());
  const [stages, setStages] = useState<{ key: string; title: string; icon: string }[]>([]);
  const [unitList, setUnitList] = useState<{ key: string; title: string; icon: string; stage: string }[]>([]);
  const [mineOnly, setMineOnly] = useState(false);
  // X-25: the TypeScript Mastery week that first curates each problem, and the
  // week the learner is on — "solvable now" is every problem at or before it.
  const [tsWeek, setTsWeek] = useState<Map<string, number>>(new Map());
  const [tsCurrent, setTsCurrent] = useState<number | null>(null);
  const [solvableNow, setSolvableNow] = useState(false);
  const [f, setF] = useState<ProblemFilter>(readFilter);
  const [presets, setPresets] = useState<Preset[]>(() => parsePresets(read(PRESETS_KEY)));
  const [columns, setColumns] = useState<ColumnKey[]>(() => parseColumns(read(COLUMNS_KEY)));
  const [naming, setNaming] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(true);
  const [limit, setLimit] = useState(renderedRows);
  const [activeRow, setActiveRow] = useState(0);
  const tbodyRef = useRef<HTMLTableSectionElement>(null);
  const moreRef = useRef<HTMLDivElement>(null);
  const nav = useNavigate();
  const toast = useToast();

  const load = () => {
    api
      .listProblems()
      .then((ps) => {
        setProblems(ps);
        setLoaded(true);
        // The seed comes from the session cache; only the problems are re-fetched.
        loadCurriculumSeed()
          .then((c) => {
            setUnitBySlug(hydrate(c, ps).unitBySlug);
            setStages((c?.stages ?? []).map((st) => ({ key: st.key, title: st.title, icon: st.icon })));
            setUnitList(
              (c?.stages ?? []).flatMap((st) => st.units.map((u) => ({ key: u.key, title: u.title, icon: u.icon, stage: st.key })))
            );
          })
          .catch(loadFailed("each problem's curriculum unit"));
      })
      .catch(loadFailed("the problem list"));
    Promise.all([api.mastery(), api.masteryProgress()])
      .then(([tracks, rows]) => {
        const ts = tracks.find((t) => t.key === "typescript");
        if (!ts) return;
        setTsWeek(masteryWeekBySlug(ts));
        setTsCurrent(currentMasteryWeek(ts, rows));
      })
      .catch(loadFailed("the TypeScript Mastery weeks"));
    api.distinctTags("topic").then(setTopics).catch(loadFailed("the topic list"));
    api.distinctTags("company").then(setCompanies).catch(loadFailed("the company list"));
  };
  useEffect(load, []);

  useEffect(() => write(FILTER_KEY, JSON.stringify(f)), [f]);
  useEffect(() => write(PRESETS_KEY, JSON.stringify(presets)), [presets]);
  useEffect(() => write(COLUMNS_KEY, JSON.stringify(columns)), [columns]);
  useEffect(() => {
    renderedRows = limit;
  }, [limit]);

  const lookup = useMemo<UnitLookup>(
    () => ({
      unitOf: (slug) => unitBySlug.get(slug)?.key,
      stageOf: (slug) => unitBySlug.get(slug)?.stage,
    }),
    [unitBySlug]
  );

  const filtered = useMemo(() => {
    let base = applyFilter(problems, f, lookup);
    if (mineOnly) base = base.filter((p) => !unitBySlug.has(p.slug));
    if (solvableNow && tsCurrent !== null) base = base.filter((p) => (tsWeek.get(p.slug) ?? Infinity) <= tsCurrent);
    return base;
  }, [problems, f, mineOnly, unitBySlug, lookup, solvableNow, tsWeek, tsCurrent]);

  // A new filter is a new table: start at its top, one page long.
  const filterKey = JSON.stringify([f, mineOnly, solvableNow]);
  const firstFilter = useRef(filterKey);
  useEffect(() => {
    if (firstFilter.current === filterKey) return;
    firstFilter.current = filterKey;
    setLimit(PAGE);
    setActiveRow(0);
  }, [filterKey]);

  const shown = filtered.slice(0, limit);

  // Load the next page as the end of the table comes into view.
  useEffect(() => {
    const el = moreRef.current;
    if (!el || shown.length >= filtered.length) return;
    const obs = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) setLimit((n) => n + PAGE);
    }, { rootMargin: "400px" });
    obs.observe(el);
    return () => obs.disconnect();
  }, [shown.length, filtered.length]);

  // Narrow the unit pills to the chosen stages: 33 pills is a wall, and picking
  // a stage is the natural way to say which third of them you mean.
  const unitPills = useMemo(
    () => (f.stages.length ? unitList.filter((u) => f.stages.includes(u.stage)) : unitList),
    [unitList, f.stages]
  );
  const unplacedCount = useMemo(() => problems.filter((p) => !unitBySlug.has(p.slug)).length, [problems, unitBySlug]);

  const state: BrowseState = { filter: f, mineOnly, solvableNow };
  const nFilters = activeFilterCount(state);
  const allPresets = [...BUILTIN_PRESETS, ...presets];

  const applyState = (s: BrowseState) => {
    setF(s.filter);
    setMineOnly(s.mineOnly);
    setSolvableNow(s.solvableNow);
  };
  const clearFilters = () => applyState({ filter: { ...emptyFilter, sort: f.sort }, mineOnly: false, solvableNow: false });

  const toggleIn = <T,>(arr: T[], v: T): T[] => (arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v]);

  const toggleFav = async (p: Problem) => {
    try {
      await api.setFavorite(p.id, !p.is_favorite);
      setProblems((ps) => ps.map((x) => (x.id === p.id ? { ...x, is_favorite: !x.is_favorite } : x)));
    } catch (e) {
      saveFailed("the favorite")(e);
    }
  };

  const setConf = async (p: Problem, v: number) => {
    try {
      await api.setConfidence(p.id, v);
      setProblems((ps) => ps.map((x) => (x.id === p.id ? { ...x, confidence: v } : x)));
    } catch (e) {
      saveFailed("the confidence rating")(e);
    }
  };

  const doImport = async () => {
    const path = await openDialog({ filters: [{ name: "JSON", extensions: ["json"] }] });
    if (typeof path !== "string") return;
    try {
      const text = await api.readFile(path);
      const n = await api.importProblems(text);
      toast.success(`Imported ${n} problems`);
      load();
    } catch (e) {
      toast.error("Import failed", { detail: String(e) });
    }
  };

  const doExport = async () => {
    const path = await saveDialog({ defaultPath: "poodcode-problems.json", filters: [{ name: "JSON", extensions: ["json"] }] });
    if (!path) return;
    try {
      const json = await api.exportProblems();
      await api.writeFile(path, json);
      toast.success("Exported problem library");
    } catch (e) {
      toast.error("Export failed", { detail: String(e) });
    }
  };

  /** ↑/↓ and friends move between rows; Enter opens. The table holds one tab
   * stop (the active row's title link), so Tab moves past it in one press. */
  const onTableKey = (e: React.KeyboardEvent) => {
    const to = nextRow(e.key, activeRow, filtered.length);
    if (to === null) return;
    e.preventDefault();
    if (to >= limit) setLimit(Math.ceil((to + 1) / PAGE) * PAGE);
    setActiveRow(to);
    requestAnimationFrame(() => {
      const link = tbodyRef.current?.querySelector<HTMLAnchorElement>(`tr[data-row="${to}"] a.row-link`);
      link?.focus();
      link?.closest("tr")?.scrollIntoView({ block: "nearest" });
    });
  };

  const has = (k: ColumnKey) => columns.includes(k);

  return (
    <div className="page page-wide browse">
      <PageHeader
        eyebrow={<Link to="/library">DSA Curriculum</Link>}
        title="Browse problems"
        subtitle={loaded ? `${filtered.length} of ${problems.length} problems` : "Loading the problem bank…"}
        actions={
          <>
            <Button icon="upload" onClick={doImport}>
              Import
            </Button>
            <Button icon="download" onClick={doExport}>
              Export
            </Button>
            <Button variant="primary" icon="add" onClick={() => nav("/problem/new")}>
              New problem
            </Button>
          </>
        }
      />

      {/* ---- Presets ---- */}
      <div className="browse-presets" role="group" aria-label="Saved filters">
        <span className="io-label">Saved filters</span>
        {allPresets.map((p) => (
          <span key={p.id} className="preset">
            <Chip pressed={matchesPreset(p, state)} onClick={() => applyState(p)}>
              {p.name}
            </Chip>
            {!p.builtin && (
              <IconButton
                icon="close"
                size="sm"
                label={`Delete the “${p.name}” preset`}
                onClick={() => setPresets((list) => deletePreset(list, p.id))}
              />
            )}
          </span>
        ))}
        {naming === null ? (
          <Button variant="ghost" size="sm" icon="bookmark" onClick={() => setNaming("")} disabled={nFilters === 0} title={nFilters === 0 ? "Set some filters first" : "Save these filters as a preset"}>
            Save current…
          </Button>
        ) : (
          <form
            className="preset-form"
            onSubmit={(e) => {
              e.preventDefault();
              if (!naming.trim()) return;
              setPresets((list) => savePreset(list, naming, state));
              toast.success(`Saved “${naming.trim()}”`);
              setNaming(null);
            }}
          >
            <input
              autoFocus
              value={naming}
              onChange={(e) => setNaming(e.target.value)}
              onKeyDown={(e) => e.key === "Escape" && setNaming(null)}
              placeholder="Name this filter"
              aria-label="Preset name"
            />
            <Button type="submit" variant="primary" size="sm" disabled={!naming.trim()}>
              Save
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setNaming(null)}>
              Cancel
            </Button>
          </form>
        )}
      </div>

      {/* ---- Filters ---- */}
      <div className="card browse-filters">
        <div className="browse-filter-top">
          <label className="learn-search browse-search">
            <Icon name="search" size={15} />
            <span className="sr-only">Search problems</span>
            <input
              type="search"
              placeholder="Search by title, topic, subtopic, or company…"
              value={f.search}
              onChange={(e) => setF({ ...f, search: e.target.value })}
            />
          </label>
          <label className="history-compare">
            <span className="dim">Sort</span>
            <select value={f.sort} onChange={(e) => setF({ ...f, sort: e.target.value as SortKey })}>
              <option value="difficulty">Difficulty (easy → hard)</option>
              <option value="title">Title</option>
              <option value="recently_added">Recently added</option>
              <option value="recently_solved">Recently solved</option>
              <option value="attempts">Most attempts</option>
              <option value="confidence">Lowest confidence</option>
            </select>
          </label>
          <details className="column-chooser">
            <summary className="btn ghost btn-sm">
              <Icon name="columns" size={14} /> Columns
            </summary>
            <div className="column-menu card" role="group" aria-label="Visible columns">
              {COLUMNS.map((c) => (
                <label key={c.key}>
                  <input type="checkbox" checked={has(c.key)} onChange={() => setColumns((cols) => toggleColumn(cols, c.key))} />
                  {c.label}
                </label>
              ))}
            </div>
          </details>
          <span className="spacer" />
          {nFilters > 0 && (
            <Button variant="ghost" size="sm" icon="close" onClick={clearFilters}>
              Clear {nFilters} filter{nFilters === 1 ? "" : "s"}
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            icon={showFilters ? "chevronUp" : "chevronDown"}
            aria-expanded={showFilters}
            onClick={() => setShowFilters((v) => !v)}
          >
            {showFilters ? "Fewer filters" : "More filters"}
          </Button>
        </div>

        {showFilters && (
          <div className="browse-filter-groups">
            <FilterGroup label="Difficulty">
              {(["Intro", "Easy", "Medium", "Hard"] as Difficulty[]).map((d) => (
                <Chip key={d} pressed={f.difficulties.includes(d)} onClick={() => setF({ ...f, difficulties: toggleIn(f.difficulties, d) })}>
                  {d}
                </Chip>
              ))}
            </FilterGroup>
            <FilterGroup label="Status">
              {(["all", "unsolved", "attempted", "solved"] as const).map((s) => (
                <Chip key={s} pressed={f.status === s} onClick={() => setF({ ...f, status: s })}>
                  {s === "all" ? "All" : s === "unsolved" ? "Unsolved" : STATUS_LABEL[s]}
                </Chip>
              ))}
            </FilterGroup>
            <FilterGroup label="By weakness">
              <Chip icon="star" pressed={f.favoritesOnly} onClick={() => setF({ ...f, favoritesOnly: !f.favoritesOnly })}>
                Favorites
              </Chip>
              <Chip pressed={f.needsReview} onClick={() => setF({ ...f, needsReview: !f.needsReview })}>
                Needs review
              </Chip>
              <Chip pressed={f.weakConfidence} onClick={() => setF({ ...f, weakConfidence: !f.weakConfidence })}>
                Weak confidence
              </Chip>
              <Chip pressed={f.overTime} onClick={() => setF({ ...f, overTime: !f.overTime })} title="Cumulative time spent over 45 minutes">
                Over 45 min
              </Chip>
              <Chip pressed={f.failedTwice} onClick={() => setF({ ...f, failedTwice: !f.failedTwice })} title="Two or more non-accepted attempts">
                Failed ≥ 2
              </Chip>
              <Chip pressed={f.neverOptimal} onClick={() => setF({ ...f, neverOptimal: !f.neverOptimal })} title="Solved, but confidence below 4">
                Never optimal
              </Chip>
              {tsCurrent !== null && tsWeek.size > 0 && (
                <Chip
                  icon="mastery"
                  pressed={solvableNow}
                  onClick={() => setSolvableNow((v) => !v)}
                  title={`Problems the TypeScript Mastery programme curates in weeks 1–${tsCurrent} — everything they need has been taught`}
                >
                  Solvable now (TS week {tsCurrent})
                </Chip>
              )}
              {unplacedCount > 0 && (
                <Chip pressed={mineOnly} onClick={() => setMineOnly((m) => !m)} count={unplacedCount} title="Problems you added or imported — not on the curriculum">
                  Not on the curriculum
                </Chip>
              )}
            </FilterGroup>
            {stages.length > 0 && (
              <>
                <FilterGroup label="Curriculum stage">
                  {stages.map((st) => (
                    <Chip key={st.key} pressed={f.stages.includes(st.key)} onClick={() => setF({ ...f, stages: toggleIn(f.stages, st.key), units: [] })}>
                      {st.title}
                    </Chip>
                  ))}
                </FilterGroup>
                <FilterGroup label={f.stages.length > 0 ? "Unit — narrowed to the stages above" : "Unit"}>
                  {unitPills.map((u) => (
                    <Chip key={u.key} pressed={f.units.includes(u.key)} onClick={() => setF({ ...f, units: toggleIn(f.units, u.key) })}>
                      {u.title}
                    </Chip>
                  ))}
                </FilterGroup>
              </>
            )}
            {topics.length > 0 && (
              <FilterGroup label="Topics">
                {topics.map((t) => (
                  <Chip key={t} pressed={f.topics.includes(t)} onClick={() => setF({ ...f, topics: toggleIn(f.topics, t) })}>
                    {t}
                  </Chip>
                ))}
              </FilterGroup>
            )}
            {companies.length > 0 && (
              <FilterGroup label="Companies">
                {companies.map((c) => (
                  <Chip key={c} pressed={f.companies.includes(c)} onClick={() => setF({ ...f, companies: toggleIn(f.companies, c) })}>
                    {c}
                  </Chip>
                ))}
              </FilterGroup>
            )}
          </div>
        )}
      </div>

      {loaded && filtered.length === 0 ? (
        <EmptyState icon="filter" title="No problems match these filters." action={{ label: "Clear filters", icon: "close", onClick: clearFilters }} />
      ) : (
        <>
          <p className="browse-keys faint">
            Keyboard: Tab into the table, then <kbd className="kbd">↑</kbd> <kbd className="kbd">↓</kbd> to move and{" "}
            <kbd className="kbd">Enter</kbd> to open.
          </p>
          <div className="card table-card">
            <table className="data browse-table" onKeyDown={onTableKey} aria-rowcount={filtered.length + 1}>
              <thead>
                <tr>
                  {has("favorite") && (
                    <th scope="col" className="col-fav">
                      <span className="sr-only">Favorite</span>
                    </th>
                  )}
                  <th scope="col">Title</th>
                  {has("difficulty") && <th scope="col">Difficulty</th>}
                  {has("unit") && <th scope="col">Taught in</th>}
                  {has("topics") && <th scope="col">Topics</th>}
                  {has("status") && <th scope="col">Status</th>}
                  {has("attempts") && (
                    <th scope="col" className="num">
                      Attempts
                    </th>
                  )}
                  {has("confidence") && <th scope="col">Confidence</th>}
                  {has("solved") && <th scope="col">Last solved</th>}
                </tr>
              </thead>
              <tbody ref={tbodyRef}>
                {shown.map((p, i) => {
                  const unit = unitBySlug.get(p.slug);
                  const week = tsWeek.get(p.slug);
                  return (
                    <tr
                      key={p.id}
                      data-row={i}
                      aria-rowindex={i + 2}
                      className={i === activeRow ? "is-active" : undefined}
                      // The row is a mouse target; the title link is the same
                      // destination for the keyboard and for Ctrl-click.
                      onClick={() => nav(`/solve/${p.id}`)}
                    >
                      {has("favorite") && (
                        <td className="col-fav">
                          <IconButton
                            size="sm"
                            icon="star"
                            className={`star ${p.is_favorite ? "on" : ""}`}
                            label={p.is_favorite ? `Unfavorite ${p.title}` : `Favorite ${p.title}`}
                            aria-pressed={p.is_favorite}
                            tabIndex={-1}
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleFav(p);
                            }}
                          />
                        </td>
                      )}
                      <td>
                        <Link
                          to={`/solve/${p.id}`}
                          className="row-link"
                          tabIndex={i === activeRow ? 0 : -1}
                          onFocus={() => setActiveRow(i)}
                          onClick={(e) => e.stopPropagation()}
                        >
                          <strong>{p.title}</strong>
                        </Link>
                      </td>
                      {has("difficulty") && (
                        <td>
                          <DiffBadge d={p.difficulty} />
                        </td>
                      )}
                      {has("unit") && (
                        <td onClick={(e) => e.stopPropagation()}>
                          {unit ? (
                            <Link to={`/library/unit/${unit.key}`} tabIndex={-1}>
                              {unit.title}
                            </Link>
                          ) : (
                            <span className="faint">yours</span>
                          )}
                          {week !== undefined && (
                            <Badge
                              className="browse-week"
                              tone={tsCurrent !== null && week <= tsCurrent ? "good" : "neutral"}
                              icon="mastery"
                              title="The TypeScript Mastery week that first sets this problem"
                            >
                              TS wk {week}
                            </Badge>
                          )}
                        </td>
                      )}
                      {has("topics") && <td className="cell-small dim">{p.topics.slice(0, 3).join(", ")}</td>}
                      {has("status") && (
                        <td>
                          {p.solved_status === "solved" ? (
                            <span className="is-good browse-status">
                              <Icon name="done" size={13} /> Solved
                            </span>
                          ) : (
                            <span className="dim">{STATUS_LABEL[p.solved_status]}</span>
                          )}
                        </td>
                      )}
                      {has("attempts") && <td className="mono num">{p.attempts_count}</td>}
                      {has("confidence") && (
                        <td onClick={(e) => e.stopPropagation()}>
                          <Confidence value={p.confidence} onChange={(v) => setConf(p, v)} />
                        </td>
                      )}
                      {has("solved") && <td className="dim">{relativeDate(p.last_solved_at)}</td>}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {shown.length < filtered.length && (
            <div ref={moreRef} className="browse-more">
              <Button variant="ghost" onClick={() => setLimit((n) => n + PAGE)}>
                Showing {shown.length} of {filtered.length} — show more
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function FilterGroup({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="filter-group" role="group" aria-label={label}>
      <div className="io-label">{label}</div>
      <div className="pill-toggle">{children}</div>
    </div>
  );
}
