import { useEffect, useMemo, useState } from "react";
import type { JpVocab, JpVocabTag, JpVocabWord } from "../types";
import { filterVocab, splitOnTerm, tagCounts, wrapIndex } from "../lib/jpVocab";

const TAG_STORE_KEY = "poodcode:jp-vocab-tag";

function readTag(): string {
  try {
    return localStorage.getItem(TAG_STORE_KEY) || "all";
  } catch {
    return "all";
  }
}

function writeTag(tag: string) {
  try {
    localStorage.setItem(TAG_STORE_KEY, tag);
  } catch {
    /* a remembered filter is a convenience, not state */
  }
}

/**
 * The 日本語 view's first section: 100 tagged, non-katakana words
 * (seeds/jp_vocab.json). The menu filters by tag and free text; clicking a
 * word opens it as a flashcard, and prev/next walk the *filtered* list.
 *
 * `openId` / `onOpen` are owned by the page so the open card lives in the URL
 * (?word=<id>) — a card can be linked to, and Back closes it.
 */
export function JpVocabMenu({
  vocab,
  onOpen,
}: {
  vocab: JpVocab;
  onOpen: (id: string, list: string[]) => void;
}) {
  const [tag, setTag] = useState<string>(readTag);
  const [query, setQuery] = useState("");
  const counts = useMemo(() => tagCounts(vocab.words), [vocab.words]);
  // A tag remembered from an older seed that no longer exists shows everything.
  const activeTag = tag === "all" || vocab.tags.some((t) => t.id === tag) ? tag : "all";
  const shown = useMemo(
    () => filterVocab(vocab.words, activeTag, query),
    [vocab.words, activeTag, query]
  );
  const tagById = useMemo(() => new Map(vocab.tags.map((t) => [t.id, t])), [vocab.tags]);

  function pick(id: string) {
    setTag(id);
    writeTag(id);
  }

  return (
    <div>
      <div className="row" style={{ gap: 6, flexWrap: "wrap", marginBottom: 10 }}>
        <button className={activeTag === "all" ? "" : "ghost"} onClick={() => pick("all")}>
          All <span className="jpv-count">{counts.all ?? 0}</span>
        </button>
        {vocab.tags.map((t) => (
          <button
            key={t.id}
            className={activeTag === t.id ? "" : "ghost"}
            onClick={() => pick(t.id)}
            title={t.label_ja}
          >
            {t.label} <span className="jpv-count">{counts[t.id] ?? 0}</span>
          </button>
        ))}
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search 漢字, かな, rōmaji or English…"
          aria-label="Search vocabulary"
          style={{ flex: "1 1 220px", minWidth: 0 }}
        />
      </div>

      {shown.length === 0 ? (
        <p className="dim" style={{ margin: "8px 0 0" }}>
          No words match{query.trim() ? ` “${query.trim()}”` : ""}.
        </p>
      ) : (
        <div className="jpv-grid">
          {shown.map((w) => (
            <button
              key={w.id}
              className="ghost jpv-tile"
              onClick={() => onOpen(w.id, shown.map((s) => s.id))}
              title={`${w.reading} — ${w.meaning}`}
            >
              <span className="jpv-tile-term" lang="ja">
                {w.term}
              </span>
              <span className="jpv-tile-reading" lang="ja">
                {w.reading}
              </span>
              <span className="jpv-tile-meaning">{w.meaning}</span>
              <TagBadge tag={tagById.get(w.tag)} id={w.tag} />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function TagBadge({ tag, id }: { tag?: JpVocabTag; id: string }) {
  return <span className={`badge jpv-tag jpv-tag-${id}`}>{tag?.label ?? id}</span>;
}

/**
 * One word as a flashcard. The front is the bare term; flipping reveals the
 * reading, meaning, both descriptions and the example sentence with the term
 * highlighted. Space/Enter flips, ←/→ move through `list`, Esc closes.
 */
export function JpVocabCard({
  vocab,
  id,
  list,
  onNavigate,
  onClose,
}: {
  vocab: JpVocab;
  id: string;
  /** The ids prev/next walk through — the menu's filtered list when opened from it. */
  list: string[];
  onNavigate: (id: string) => void;
  onClose: () => void;
}) {
  const byId = useMemo(() => new Map(vocab.words.map((w) => [w.id, w])), [vocab.words]);
  const word = byId.get(id);
  // Opened from a link, the id may not be in the remembered list; walk everything.
  const ids = list.includes(id) ? list : vocab.words.map((w) => w.id);
  const index = ids.indexOf(id);
  const tag = vocab.tags.find((t) => t.id === word?.tag);
  const [flipped, setFlipped] = useState(false);

  useEffect(() => setFlipped(false), [id]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
      else if (e.key === "ArrowRight") onNavigate(ids[wrapIndex(index, 1, ids.length)]);
      else if (e.key === "ArrowLeft") onNavigate(ids[wrapIndex(index, -1, ids.length)]);
      else if (e.key === " " || e.key === "Enter") {
        // A focused control inside the card (Prev, Next, Close) keeps its own
        // Enter/Space; anywhere else it flips the card.
        if ((e.target as HTMLElement | null)?.closest?.(".jpv-card button")) return;
        e.preventDefault();
        setFlipped((f) => !f);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [ids, index, onNavigate, onClose]);

  if (!word) return null;

  return (
    <div className="welcome-overlay" onClick={onClose}>
      <div
        className="welcome-card jpv-card"
        role="dialog"
        aria-modal="true"
        aria-label={`${word.term} — ${word.meaning}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <TagBadge tag={tag} id={word.tag} />
          <span className="dim" style={{ fontSize: 12 }}>
            {index + 1} / {ids.length}
          </span>
          <button className="ghost" onClick={onClose} aria-label="Close" style={{ padding: "2px 10px" }}>
            ✕
          </button>
        </div>

        <div
          className="jpv-face"
          role="button"
          tabIndex={-1}
          onClick={() => setFlipped((f) => !f)}
          title={flipped ? "Click to hide" : "Click to reveal"}
        >
          <div className="jpv-term" lang="ja">
            {word.term}
          </div>
          {flipped ? (
            <>
              <div className="jpv-reading" lang="ja">
                {word.reading} <span className="dim">· {word.romaji}</span>
              </div>
              <div className="jpv-meaning">{word.meaning}</div>
            </>
          ) : (
            <p className="dim" style={{ margin: "14px 0 0", fontSize: 13 }}>
              Can you read it? Click or press Space to reveal.
            </p>
          )}
        </div>

        {flipped && <CardDetails word={word} />}

        <div className="row" style={{ justifyContent: "space-between", marginTop: 16, gap: 8 }}>
          <button className="ghost" onClick={() => onNavigate(ids[wrapIndex(index, -1, ids.length)])}>
            ← Prev
          </button>
          <button onClick={() => setFlipped((f) => !f)}>{flipped ? "Hide" : "Reveal"}</button>
          <button className="ghost" onClick={() => onNavigate(ids[wrapIndex(index, 1, ids.length)])}>
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}

function CardDetails({ word }: { word: JpVocabWord }) {
  return (
    <div className="jpv-details">
      <div className="jpv-block">
        <div className="io-label">Description</div>
        <p>{word.desc_en}</p>
      </div>
      <div className="jpv-block">
        <div className="io-label" lang="ja">
          説明
        </div>
        <p lang="ja">{word.desc_ja}</p>
      </div>
      <div className="jpv-block jpv-example">
        <div className="io-label" lang="ja">
          例文 · Example
        </div>
        <p lang="ja" className="jpv-example-ja">
          {splitOnTerm(word.example_ja, word.term).map((p, i) =>
            p.hit ? <mark key={i}>{p.text}</mark> : <span key={i}>{p.text}</span>
          )}
        </p>
        <p className="dim jpv-example-en">{word.example_en}</p>
      </div>
    </div>
  );
}
