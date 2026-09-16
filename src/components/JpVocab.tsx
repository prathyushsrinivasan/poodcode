import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { CardReview, JpVocab, JpVocabTag, JpVocabWord } from "../types";
import {
  clozePrompt,
  distractors,
  filterVocab,
  readyWords,
  shuffleWith,
  splitOnTerm,
  stateCounts,
  tagCounts,
  vocabCardId,
  wordState,
  wrapIndex,
  type VocabState,
} from "../lib/jpVocab";
import { acceptsReading, joinReading } from "../lib/romaji";
import { todayISO } from "../lib/srs";

const TAG_STORE_KEY = "poodcode:jp-vocab-tag";
const MODE_STORE_KEY = "poodcode:jp-vocab-mode";

/** How a word is put to you. `flip` and `reverse` you grade yourself; `type`
 * and `cloze` know the answer and grade it for you. */
type VocabMode = "flip" | "reverse" | "type" | "cloze";

const MODES: { id: VocabMode; label: string; ask: string }[] = [
  { id: "flip", label: "🔄 Flip", ask: "Can you read it? Click or press Space to reveal." },
  { id: "reverse", label: "🇬🇧 Reverse", ask: "Say it in Japanese, then reveal." },
  { id: "type", label: "⌨️ Type", ask: "Type the reading — rōmaji or kana." },
  { id: "cloze", label: "✍️ Cloze", ask: "Which word fills the blank?" },
];

function readMode(): VocabMode {
  try {
    const m = localStorage.getItem(MODE_STORE_KEY);
    return MODES.some((x) => x.id === m) ? (m as VocabMode) : "flip";
  } catch {
    return "flip";
  }
}

function writeMode(m: VocabMode) {
  try {
    localStorage.setItem(MODE_STORE_KEY, m);
  } catch {
    /* a remembered mode is a convenience, not state */
  }
}

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

/* --------------------------------------------------------------- reviews */

const GRADES: { q: number; label: string; hint: string; color?: string }[] = [
  { q: 0, label: "Again", hint: "today", color: "var(--bad)" },
  { q: 1, label: "Hard", hint: "sooner" },
  { q: 2, label: "Good", hint: "on schedule" },
  { q: 3, label: "Easy", hint: "much later", color: "var(--good)" },
];

const STATE_LABEL: Record<VocabState, string> = {
  new: "New — never studied",
  due: "Due — ready for review",
  learning: "Learning — scheduled ahead",
};

/** The vocabulary list's slice of the shared `card_reviews` table.
 *
 * Owned by the page rather than by either component below, because the menu
 * shows the counts and the card does the grading — they have to agree without a
 * round trip. Grading a word here is the same `api.gradeCard` (SM-2) the
 * glossary decks use; only the card id differs (`jp-vocab#<word id>`). */
export interface VocabReviews {
  reviews: Map<string, CardReview>;
  today: string;
  grade: (wordId: string, quality: number) => Promise<void>;
  reset: (wordIds: string[]) => Promise<void>;
}

export function useVocabReviews(): VocabReviews {
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  // Pinned for the session: a date that changed mid-session would silently
  // reshuffle what counts as due while the learner is part-way through.
  const [today] = useState(todayISO);

  useEffect(() => {
    api
      .cardReviews()
      .then((list) => setReviews(new Map(list.map((r) => [r.card_id, r]))))
      .catch(() => {
        /* no history yet is the same as no history loaded — everything is new */
      });
  }, []);

  const grade = useCallback(async (wordId: string, quality: number) => {
    const id = vocabCardId(wordId);
    try {
      const cr = await api.gradeCard(id, quality);
      setReviews((m) => new Map(m).set(id, cr));
    } catch {
      /* a dropped grade is not worth interrupting the session over */
    }
  }, []);

  const reset = useCallback(async (wordIds: string[]) => {
    const ids = wordIds.map(vocabCardId);
    try {
      await api.resetCards(ids);
      setReviews((m) => {
        const next = new Map(m);
        for (const id of ids) next.delete(id);
        return next;
      });
    } catch {
      /* leave the counts as they were */
    }
  }, []);

  return { reviews, today, grade, reset };
}

/* ------------------------------------------------------------------- menu */

/**
 * The 日本語 view's first section: the tagged, non-katakana vocabulary
 * (seeds/jp_vocab.json). The menu filters by tag, by free text and by whether a
 * word is ready for review; clicking a word opens it as a flashcard, and
 * prev/next walk the *filtered* list.
 *
 * `openId` / `onOpen` are owned by the page so the open card lives in the URL
 * (?word=<id>) — a card can be linked to, and Back closes it.
 */
export function JpVocabMenu({
  vocab,
  reviews: rev,
  onOpen,
}: {
  vocab: JpVocab;
  reviews: VocabReviews;
  onOpen: (id: string, list: string[]) => void;
}) {
  const { reviews, today } = rev;
  const [tag, setTag] = useState<string>(readTag);
  const [query, setQuery] = useState("");
  const [dueOnly, setDueOnly] = useState(false);
  const counts = useMemo(() => tagCounts(vocab.words), [vocab.words]);
  const states = useMemo(
    () => stateCounts(vocab.words, reviews, today),
    [vocab.words, reviews, today]
  );
  // A tag remembered from an older seed that no longer exists shows everything.
  const activeTag = tag === "all" || vocab.tags.some((t) => t.id === tag) ? tag : "all";
  const matching = useMemo(
    () => filterVocab(vocab.words, activeTag, query),
    [vocab.words, activeTag, query]
  );
  // "Study due" walks what the current filter shows, not the whole list, so
  // narrowing to one tag and studying it is a single click.
  const ready = useMemo(() => readyWords(matching, reviews, today), [matching, reviews, today]);
  const shown = dueOnly ? ready : matching;
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
        <button
          className={dueOnly ? "" : "ghost"}
          onClick={() => setDueOnly((d) => !d)}
          title="New and overdue words — everything you can study right now"
        >
          ⏱ Due <span className="jpv-count">{states.ready}</span>
        </button>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search 漢字, かな, rōmaji or English…"
          aria-label="Search vocabulary"
          style={{ flex: "1 1 220px", minWidth: 0 }}
        />
      </div>

      <div className="row" style={{ gap: 8, flexWrap: "wrap", marginBottom: 10 }}>
        <button onClick={() => onOpen(ready[0].id, ready.map((w) => w.id))} disabled={ready.length === 0}>
          🎴 Study due ({ready.length})
        </button>
        <span className="dim" style={{ fontSize: 12, alignSelf: "center" }}>
          {states.learning} learning · {states.new} new · {states.due} due
        </span>
      </div>

      {shown.length === 0 ? (
        <p className="dim" style={{ margin: "8px 0 0" }}>
          {dueOnly
            ? "Nothing due here — every word in this filter is scheduled for a later day."
            : `No words match${query.trim() ? ` “${query.trim()}”` : ""}.`}
        </p>
      ) : (
        <div className="jpv-grid">
          {shown.map((w) => {
            const state = wordState(reviews.get(vocabCardId(w.id)), today);
            return (
              <button
                key={w.id}
                className="ghost jpv-tile"
                onClick={() => onOpen(w.id, shown.map((s) => s.id))}
                title={`${w.reading} — ${w.meaning}`}
              >
                <span className={`jpv-dot jpv-dot-${state}`} title={STATE_LABEL[state]} />
                <span className="jpv-tile-term" lang="ja">
                  {w.term}
                </span>
                <span className="jpv-tile-reading" lang="ja">
                  {w.reading}
                </span>
                <span className="jpv-tile-meaning">{w.meaning}</span>
                <TagBadge tag={tagById.get(w.tag)} id={w.tag} />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function TagBadge({ tag, id }: { tag?: JpVocabTag; id: string }) {
  return <span className={`badge jpv-tag jpv-tag-${id}`}>{tag?.label ?? id}</span>;
}

/* ------------------------------------------------------------------- card */

/**
 * One word as a study card, in whichever mode is selected: read the kanji
 * (flip), produce the Japanese from the English (reverse), type the reading
 * (type), or put the term back into its own example sentence (cloze).
 *
 * Flip and reverse you grade yourself. Type and cloze know the answer and grade
 * it for you — correct is Good, wrong is Again, the rule `CardStudy` already
 * uses next door. Either way the word is scheduled through the same SM-2 engine
 * and the card advances, so a session is a loop rather than a lookup.
 *
 * Space/Enter reveals, 1–4 grade a revealed self-graded card, ←/→ move through
 * `list`, Esc closes.
 */
export function JpVocabCard({
  vocab,
  id,
  list,
  reviews: rev,
  onNavigate,
  onClose,
}: {
  vocab: JpVocab;
  id: string;
  /** The ids prev/next walk through — the menu's filtered list when opened from it. */
  list: string[];
  reviews: VocabReviews;
  onNavigate: (id: string) => void;
  onClose: () => void;
}) {
  const { reviews, today, grade } = rev;
  const byId = useMemo(() => new Map(vocab.words.map((w) => [w.id, w])), [vocab.words]);
  const word = byId.get(id);
  // Opened from a link, the id may not be in the remembered list; walk everything.
  const ids = list.includes(id) ? list : vocab.words.map((w) => w.id);
  const index = ids.indexOf(id);
  const tag = vocab.tags.find((t) => t.id === word?.tag);
  const [mode, setMode] = useState<VocabMode>(readMode);
  const [revealed, setRevealed] = useState(false);
  const [typed, setTyped] = useState("");
  const [picked, setPicked] = useState<string | null>(null);
  const review = reviews.get(vocabCardId(id));
  const state = wordState(review, today);
  const autoGraded = mode === "type" || mode === "cloze";

  // Fixed for as long as the card is on screen, so a re-render never moves the
  // answer out from under the pointer.
  const options = useMemo(
    () =>
      word ? shuffleWith([word, ...distractors(vocab.words, word.id, 3)]).map((w) => w.term) : [],
    [word, vocab.words]
  );

  const correct =
    mode === "type"
      ? !!word && acceptsReading(typed, joinReading(word.reading, word.romaji))
      : picked === word?.term;

  // A new card — or a new way of being asked — starts unanswered.
  useEffect(() => {
    setRevealed(false);
    setTyped("");
    setPicked(null);
  }, [id, mode]);

  function pickMode(m: VocabMode) {
    setMode(m);
    writeMode(m);
  }

  /** Grade, then move to the next card in the list — the loop a study session
   * is actually made of. On the last card there is nowhere to go, so it just
   * folds shut again. */
  const gradeAndAdvance = useCallback(
    async (quality: number) => {
      await grade(id, quality);
      const next = ids[wrapIndex(index, 1, ids.length)];
      if (next && next !== id) onNavigate(next);
      else setRevealed(false);
    },
    [grade, id, ids, index, onNavigate]
  );

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
      else if (e.key === "ArrowRight") onNavigate(ids[wrapIndex(index, 1, ids.length)]);
      else if (e.key === "ArrowLeft") onNavigate(ids[wrapIndex(index, -1, ids.length)]);
      else if (revealed && !autoGraded && e.key >= "1" && e.key <= "4") {
        e.preventDefault();
        gradeAndAdvance(Number(e.key) - 1);
      } else if (e.key === " " || e.key === "Enter") {
        // A focused control inside the card (Prev, Next, Close) and the Type
        // mode's input keep their own Enter/Space; anywhere else it reveals.
        if ((e.target as HTMLElement | null)?.closest?.(".jpv-card button, .jpv-card input")) return;
        e.preventDefault();
        if (revealed && autoGraded) gradeAndAdvance(correct ? 2 : 0);
        else if (!autoGraded) setRevealed((f) => !f);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [ids, index, revealed, autoGraded, correct, gradeAndAdvance, onNavigate, onClose]);

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
          className="row"
          style={{ gap: 4, flexWrap: "wrap", justifyContent: "center", margin: "10px 0 0" }}
        >
          {MODES.map((m) => (
            <button
              key={m.id}
              className={mode === m.id ? "" : "ghost"}
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => pickMode(m.id)}
            >
              {m.label}
            </button>
          ))}
        </div>

        <div
          className="jpv-face"
          role="button"
          tabIndex={-1}
          onClick={() => !autoGraded && setRevealed((f) => !f)}
          title={autoGraded ? undefined : revealed ? "Click to hide" : "Click to reveal"}
          style={autoGraded ? { cursor: "default" } : undefined}
        >
          {mode === "reverse" ? (
            <>
              <div className="jpv-meaning" style={{ fontSize: 24, marginTop: 6 }}>
                {word.meaning}
              </div>
              {revealed && (
                <>
                  <div className="jpv-term" lang="ja" style={{ fontSize: 44, marginTop: 12 }}>
                    {word.term}
                  </div>
                  <div className="jpv-reading" lang="ja">
                    {word.reading} <span className="dim">· {word.romaji}</span>
                  </div>
                </>
              )}
            </>
          ) : mode === "cloze" ? (
            <p
              lang="ja"
              className="jpv-example-ja"
              style={{ margin: "6px 0 0", fontSize: 19, lineHeight: 1.9 }}
            >
              {clozePrompt(word.example_ja, word.term)}
            </p>
          ) : (
            <>
              <div className="jpv-term" lang="ja">
                {word.term}
              </div>
              {revealed && mode === "flip" && (
                <>
                  <div className="jpv-reading" lang="ja">
                    {word.reading} <span className="dim">· {word.romaji}</span>
                  </div>
                  <div className="jpv-meaning">{word.meaning}</div>
                </>
              )}
            </>
          )}
          {!revealed && (
            <p className="dim" style={{ margin: "14px 0 0", fontSize: 13 }}>
              {MODES.find((m) => m.id === mode)?.ask}
            </p>
          )}
        </div>

        {mode === "type" && (
          <div style={{ textAlign: "center", marginTop: 12 }}>
            <input
              autoFocus
              value={typed}
              disabled={revealed}
              onChange={(e) => setTyped(e.target.value)}
              onKeyDown={(e) => {
                if (e.key !== "Enter") return;
                e.preventDefault();
                if (revealed) gradeAndAdvance(correct ? 2 : 0);
                else if (typed.trim()) setRevealed(true);
              }}
              placeholder="e.g. hairetsu / はいれつ"
              aria-label="Type the reading"
              style={{
                fontSize: 18,
                textAlign: "center",
                padding: "8px 12px",
                width: "100%",
                maxWidth: 320,
                borderRadius: 8,
                border: `1px solid ${
                  revealed ? (correct ? "var(--good)" : "var(--bad)") : "var(--border)"
                }`,
                background: "var(--bg-elev-2)",
                color: "var(--text)",
              }}
            />
          </div>
        )}

        {mode === "cloze" && (
          <div className="grid cols-2" style={{ marginTop: 12 }}>
            {options.map((opt) => {
              let border: string | undefined;
              if (revealed) {
                if (opt === word.term) border = "var(--good)";
                else if (opt === picked) border = "var(--bad)";
              }
              return (
                <button
                  key={opt}
                  className="ghost"
                  lang="ja"
                  style={{ borderColor: border, color: border, padding: "10px 12px" }}
                  disabled={revealed}
                  onClick={() => {
                    setPicked(opt);
                    setRevealed(true);
                  }}
                >
                  {opt}
                </button>
              );
            })}
          </div>
        )}

        {revealed && autoGraded && (
          <div
            style={{
              marginTop: 12,
              textAlign: "center",
              fontWeight: 600,
              color: correct ? "var(--good)" : "var(--bad)",
            }}
          >
            {correct ? "Correct!" : `Not quite — ${mode === "type" ? word.reading : word.term}`}
          </div>
        )}

        {revealed && <CardDetails word={word} />}

        {revealed ? (
          <>
            {autoGraded ? (
              <div className="row" style={{ marginTop: 14 }}>
                <button onClick={() => gradeAndAdvance(correct ? 2 : 0)}>Next →</button>
              </div>
            ) : (
              <div className="row" style={{ marginTop: 14, gap: 8, flexWrap: "wrap" }}>
                {GRADES.map((g) => (
                  <button
                    key={g.q}
                    className="ghost"
                    style={{ flex: "1 1 0", minWidth: 80, borderColor: g.color, color: g.color }}
                    onClick={() => gradeAndAdvance(g.q)}
                    title={`${g.label} — ${g.hint} (press ${g.q + 1})`}
                  >
                    <div>{g.label}</div>
                    <div className="dim" style={{ fontSize: 11 }}>
                      {g.hint}
                    </div>
                  </button>
                ))}
              </div>
            )}
            <p className="dim" style={{ margin: "8px 0 0", fontSize: 12, textAlign: "center" }}>
              <span className={`jpv-dot jpv-dot-${state}`} style={{ position: "static", marginRight: 6 }} />
              {review
                ? `${review.reps} review${review.reps === 1 ? "" : "s"} · next due ${review.due_date}`
                : "Not studied yet — grading schedules it."}
            </p>
          </>
        ) : (
          <div className="row" style={{ justifyContent: "space-between", marginTop: 16, gap: 8 }}>
            <button className="ghost" onClick={() => onNavigate(ids[wrapIndex(index, -1, ids.length)])}>
              ← Prev
            </button>
            {mode === "type" ? (
              <button onClick={() => setRevealed(true)} disabled={!typed.trim()}>
                Check
              </button>
            ) : mode === "cloze" ? (
              <span className="dim" style={{ fontSize: 12, alignSelf: "center" }}>
                Pick an answer
              </span>
            ) : (
              <button onClick={() => setRevealed(true)}>Reveal</button>
            )}
            <button className="ghost" onClick={() => onNavigate(ids[wrapIndex(index, 1, ids.length)])}>
              Next →
            </button>
          </div>
        )}
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
