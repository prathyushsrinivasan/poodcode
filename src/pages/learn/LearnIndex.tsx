/**
 * The Learn library: every concept in one track, searchable and filterable
 * (UI_ROADMAP G6).
 *
 * The track is in the URL (`/learn?track=sql`), so a link can open the SQL
 * track and Back returns to the one you were on; the last one is remembered
 * for a bare `/learn`. Concept cards are links — they were `div`s with
 * `onClick`, which a keyboard could not reach and Ctrl-click could not open
 * (D3).
 */

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";
import type { Concept } from "../../types";
import { Section, useCollapse } from "../../components/Collapsible";
import { TrackSkeleton } from "../../components/Skeleton";
import { Badge, Button, Chip, EmptyState, ErrorState, Icon, PageHeader, Segmented, Tabs, type IconName } from "../../components/ui";
import {
  TRACKS,
  TRACK_STORE_KEY,
  categoryRank,
  conceptLang,
  langLabel,
  shortCategory,
  useLearnData,
} from "./learnData";

type Progress = "all" | "todo" | "done";

function readStoredTrack(): string {
  try {
    return localStorage.getItem(TRACK_STORE_KEY) || "java";
  } catch {
    return "java";
  }
}

function matches(c: Concept, q: string): boolean {
  if (!q) return true;
  const hay = `${c.name} ${c.what} ${c.category}`.toLowerCase();
  return q
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .every((w) => hay.includes(w));
}

export default function LearnIndex() {
  const { concepts, error, reload, done } = useLearnData();
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [progress, setProgress] = useState<Progress>("all");

  // Only offer tracks that have content.
  const tracks = useMemo(() => {
    const present = new Set((concepts ?? []).map(conceptLang));
    return TRACKS.filter((t) => present.has(t.id));
  }, [concepts]);

  const requested = params.get("track") || readStoredTrack();
  const track = tracks.some((t) => t.id === requested) ? requested : tracks[0]?.id ?? "java";

  useEffect(() => {
    try {
      localStorage.setItem(TRACK_STORE_KEY, track);
    } catch {
      /* the remembered track is a convenience */
    }
  }, [track]);

  const pickTrack = (id: string) => {
    setCategory("");
    setParams({ track: id }, { replace: true });
  };

  // Category sections fold independently per track.
  const cats = useCollapse(`learn-cat:${track}`);

  const inTrack = useMemo(() => (concepts ?? []).filter((c) => conceptLang(c) === track), [concepts, track]);
  const categories = useMemo(
    () => [...new Set(inTrack.map((c) => c.category))].sort((a, b) => categoryRank(a) - categoryRank(b)),
    [inTrack]
  );

  const visible = useMemo(
    () =>
      inTrack.filter(
        (c) =>
          matches(c, query) &&
          (!category || c.category === category) &&
          (progress === "all" || (progress === "done") === done.has(c.key))
      ),
    [inTrack, query, category, progress, done]
  );

  const grouped = useMemo(() => {
    const map = new Map<string, Concept[]>();
    for (const c of visible) {
      if (!map.has(c.category)) map.set(c.category, []);
      map.get(c.category)!.push(c);
    }
    return [...map.entries()].sort((a, b) => categoryRank(a[0]) - categoryRank(b[0]));
  }, [visible]);

  // When a search finds nothing here, say where it would find something.
  const elsewhere = useMemo(() => {
    if (!query || visible.length > 0 || !concepts) return [];
    const counts = new Map<string, number>();
    for (const c of concepts) {
      if (conceptLang(c) !== track && matches(c, query)) counts.set(conceptLang(c), (counts.get(conceptLang(c)) ?? 0) + 1);
    }
    return tracks.filter((t) => counts.has(t.id)).map((t) => ({ ...t, n: counts.get(t.id)! }));
  }, [query, visible.length, concepts, track, tracks]);

  if (error) {
    return (
      <div className="page">
        <PageHeader title="Learn" />
        <ErrorState title="The concept library could not be loaded." error={error} onRetry={reload} />
      </div>
    );
  }
  if (!concepts) return <TrackSkeleton cards={6} />;

  const doneInTrack = inTrack.filter((c) => done.has(c.key)).length;
  const filtered = query !== "" || category !== "" || progress !== "all";
  const clearFilters = () => {
    setQuery("");
    setCategory("");
    setProgress("all");
  };

  return (
    <div className="page learn-page">
      <PageHeader
        title="Learn"
        subtitle={<TrackIntro track={track} count={inTrack.length} />}
        actions={
          <Badge tone={doneInTrack === inTrack.length && inTrack.length > 0 ? "good" : "neutral"} icon="done">
            {doneInTrack}/{inTrack.length} done
          </Badge>
        }
      />

      {tracks.length > 1 && (
        <Tabs
          idBase="learn-track"
          className="learn-tracks"
          active={track}
          onChange={pickTrack}
          tabs={tracks.map((t) => ({
            key: t.id,
            label: t.label,
            count: (concepts ?? []).filter((c) => conceptLang(c) === t.id).length,
          }))}
        />
      )}

      <div id="learn-track-panel" role="tabpanel" aria-labelledby={`learn-track-tab-${track}`} className="learn-panel">
        <TrackPromos track={track} />

        <div className="learn-filters" role="search">
          <label className="learn-search">
            <Icon name="search" size={15} />
            <span className="sr-only">Search {langLabel(track)} concepts</span>
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={`Search ${inTrack.length} ${langLabel(track)} chapters…`}
            />
          </label>
          {categories.length > 1 && (
            <select value={category} onChange={(e) => setCategory(e.target.value)} aria-label="Category">
              <option value="">All categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {shortCategory(c)}
                </option>
              ))}
            </select>
          )}
          <Segmented
            label="Progress"
            value={progress}
            onChange={setProgress}
            options={[
              { value: "all", label: "All" },
              { value: "todo", label: "To do" },
              { value: "done", label: "Done" },
            ]}
          />
          <span className="spacer" />
          {grouped.length > 1 && !filtered && (
            <>
              <Button variant="ghost" size="sm" icon="chevronDown" onClick={() => cats.setAll(grouped.map(([c]) => c), true)}>
                Expand all
              </Button>
              <Button variant="ghost" size="sm" icon="chevronRight" onClick={() => cats.setAll(grouped.map(([c]) => c), false)}>
                Collapse all
              </Button>
            </>
          )}
        </div>

        {filtered && (
          <p className="learn-result-count" role="status">
            {visible.length} of {inTrack.length} chapters
            {visible.length > 0 && (
              <button type="button" className="link-button" onClick={clearFilters}>
                Clear filters
              </button>
            )}
          </p>
        )}

        {visible.length === 0 ? (
          <EmptyState
            icon="search"
            title={query ? `No ${langLabel(track)} chapter matches “${query}”.` : "Nothing matches these filters."}
            action={{ label: "Clear filters", icon: "close", onClick: clearFilters }}
          >
            {elsewhere.length > 0 && (
              <span className="learn-elsewhere">
                In other tracks:{" "}
                {elsewhere.map((t) => (
                  <Chip key={t.id} onClick={() => pickTrack(t.id)} count={t.n}>
                    {t.label}
                  </Chip>
                ))}
              </span>
            )}
          </EmptyState>
        ) : (
          grouped.map(([cat, items]) => {
            const doneN = items.filter((c) => done.has(c.key)).length;
            return (
              <Section
                key={cat}
                title={cat}
                // A search or a filter shows every match, folded or not.
                open={filtered || cats.isOpen(cat)}
                onToggle={() => cats.toggle(cat)}
                meta={
                  <span className={`learn-cat-count ${doneN === items.length ? "is-good" : ""}`}>
                    {doneN}/{items.length} done
                  </span>
                }
              >
                <ul className="concept-grid">
                  {items.map((c) => (
                    <li key={c.key}>
                      <ConceptCard concept={c} done={done.has(c.key)} />
                    </li>
                  ))}
                </ul>
              </Section>
            );
          })
        )}
      </div>
    </div>
  );
}

function ConceptCard({ concept: c, done }: { concept: Concept; done: boolean }) {
  const exs = c.exercises ?? [];
  const drillN = exs.filter((e) => (e.kind || "drill") !== "challenge").length;
  const challengeN = exs.filter((e) => e.kind === "challenge").length;
  const quizN = c.quiz?.length ?? 0;
  return (
    <Link to={`/learn/${c.key}`} className={`card concept-card ${done ? "is-done" : ""}`}>
      <strong className="concept-card-title">
        {done && <Icon name="done" size={14} label="Done" className="is-good" />}
        {c.name}
      </strong>
      <span className="concept-card-what">{c.what}</span>
      <span className="concept-card-badges">
        {c.cards?.length > 0 ? (
          <Badge title="Vocabulary flashcards">{c.cards.length} cards</Badge>
        ) : (
          <>
            {drillN > 0 && <Badge title="Fill-in-the-blank drills">{drillN} drills</Badge>}
            {challengeN > 0 && (
              <Badge tone="accent" icon="trophy" title="Coding challenge">
                challenge
              </Badge>
            )}
          </>
        )}
        {quizN > 0 && (
          <Badge tone="accent" icon="help" title="Multiple-choice self-check quiz">
            {quizN} quiz
          </Badge>
        )}
      </span>
    </Link>
  );
}

/** One line on what the track is and where to start. */
function TrackIntro({ track, count }: { track: string; count: number }): ReactNode {
  switch (track) {
    case "sql":
      return (
        <>
          {count} SQL chapters, from <strong>joins</strong> through aggregation, subqueries, CTEs and window functions —
          every exercise runs real SQL against a real database. Start with <strong>How a Join Actually Works</strong>.
        </>
      );
    case "java_vocab":
      return (
        <>
          {count} Java vocabulary chapters: a textbook definition and a plain-English line for each term, with
          flashcards and a quiz. Start with <strong>Keywords &amp; Syntax</strong>.
        </>
      );
    case "algorithms":
      return (
        <>
          {count} language-agnostic algorithm lessons — the idea, pseudocode, traces and cost — with quizzes and
          practice problems in any language. Start with <strong>What Is an Algorithm?</strong>
        </>
      );
    case "japanese":
      return (
        <>
          {count} Japanese glossary sets for Java and TypeScript. The core vocabulary and its review deck live on the{" "}
          <Link to="/japanese">日本語 page</Link>.
        </>
      );
    case "typescript":
      return (
        <>
          {count} TypeScript chapters, each with the syntax, fill-in-the-blank drills and full problems you run here.
          New to TypeScript? Start with <strong>Language Basics</strong>.
        </>
      );
    default:
      return (
        <>
          {count} {langLabel(track)} chapters, each with the syntax, fill-in-the-blank drills and full problems you run
          here. New to Java? Start with <strong>Foundations</strong>.
        </>
      );
  }
}

/** Where a track continues outside Learn: the course, the programme, the bridge. */
function TrackPromos({ track }: { track: string }) {
  const promos: { to: string; icon: IconName; title: string; body: string }[] =
    track === "typescript"
      ? [
          {
            to: "/course",
            icon: "typescript",
            title: "The 8-month TypeScript course",
            body: "A week-by-week path from your first line to interview-ready. These chapters are its reference.",
          },
          {
            to: "/mastery",
            icon: "mastery",
            title: "6-Month Mastery — these chapters, in order",
            body: "26 weeks, each with curated problems, a build project and an exam that unlocks the next.",
          },
        ]
      : track === "japanese"
        ? [
            {
              to: "/japanese",
              icon: "japanese",
              title: "日本語 vocabulary and review",
              body: "The core word list as flashcards, and one review deck for every set here.",
            },
            {
              to: "/jp-bridge",
              icon: "code",
              title: "日本語 → Java — put the vocabulary to work",
              body: "Real coding problems stated in Japanese, solved in Java, plus interview practice.",
            },
          ]
        : [];
  if (promos.length === 0) return null;
  return (
    <ul className="learn-promos">
      {promos.map((p) => (
        <li key={p.to}>
          <Link to={p.to} className="card learn-promo">
            <Icon name={p.icon} size={20} />
            <span className="learn-promo-text">
              <strong>{p.title}</strong>
              <span>{p.body}</span>
            </span>
            <Icon name="chevronRight" size={16} />
          </Link>
        </li>
      ))}
    </ul>
  );
}
