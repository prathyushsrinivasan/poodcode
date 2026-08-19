import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { Card, CardReview } from "../types";
import { cardId } from "../lib/learnProgress";

/* ------------------------------------------------------------------ helpers */

function shuffle<T>(xs: T[]): T[] {
  const a = [...xs];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function todayStr(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
    d.getDate()
  ).padStart(2, "0")}`;
}

/** The romaji portion of a reading like "へんすう (hensū)" → "hensū"; a
 * katakana loanword reading (e.g. "kōdo") is already romaji. */
function romajiOf(reading: string): string {
  const m = reading.match(/\(([^)]+)\)/);
  return (m ? m[1] : reading).trim();
}

/** Normalize romaji for lenient typed grading: lowercase, fold long-vowel
 * macrons, drop anything that isn't a latin letter. */
function normRomaji(s: string): string {
  return s
    .toLowerCase()
    .replace(/[āáàâ]/g, "a")
    .replace(/[īíìî]/g, "i")
    .replace(/[ūúùû]/g, "u")
    .replace(/[ēéèê]/g, "e")
    .replace(/[ōóòô]/g, "o")
    .replace(/[^a-z]/g, "");
}

/** Pick up to n random items from xs excluding `not`. */
function sample<T>(xs: T[], n: number, not: (x: T) => boolean): T[] {
  return shuffle(xs.filter((x) => !not(x))).slice(0, n);
}

type Mode = "flip" | "choice" | "cloze" | "type";

/** Study variant. "japanese" decks carry a rōmaji reading (Type mode) and
 * example sentences; "vocab" decks (e.g. the Java vocabulary track) instead
 * carry a textbook line, a plain-English line, and a code snippet, so the
 * rōmaji Type mode is dropped and the card back is laid out differently. */
export type StudyVariant = "japanese" | "vocab";

const JP_MODES: { id: Mode; label: string }[] = [
  { id: "flip", label: "🔄 Flip" },
  { id: "choice", label: "🔘 Choice" },
  { id: "cloze", label: "✍️ Cloze" },
  { id: "type", label: "⌨️ Type reading" },
];

const VOCAB_MODES: { id: Mode; label: string }[] = [
  { id: "flip", label: "🔄 Flip" },
  { id: "choice", label: "🔘 Choice" },
  { id: "cloze", label: "✍️ Code cloze" },
];

const GRADES: { q: number; label: string; hint: string; color?: string }[] = [
  { q: 0, label: "Again", hint: "comes back now", color: "var(--bad)" },
  { q: 1, label: "Hard", hint: "sooner" },
  { q: 2, label: "Good", hint: "on schedule" },
  { q: 3, label: "Easy", hint: "much later", color: "var(--good)" },
];

const BLANK = "＿＿＿";

/* --------------------------------------------------------------- component */

/**
 * Spaced-repetition study over a deck of vocabulary cards.
 *
 * State (ease/interval/due) is persisted per card in SQLite via
 * api.gradeCard(), using the same SM-2 engine as the rest of the app. Each
 * session shows only cards that are **due** (or never studied). Grades:
 *   Again → the card is re-queued within the next 20 cards this session AND
 *           scheduled for tomorrow; Hard/Good/Easy push the next review out.
 *
 * Beyond self-graded "Flip", three active-recall modes auto-grade the answer
 * (correct → Good, wrong → Again): multiple Choice, Cloze (fill the blank in
 * the example sentence), and Type (the romaji reading).
 */
export function CardStudy({
  conceptKey,
  cards,
  variant = "japanese",
}: {
  conceptKey: string;
  cards: Card[];
  variant?: StudyVariant;
}) {
  const modes = variant === "vocab" ? VOCAB_MODES : JP_MODES;
  const ids = useMemo(() => cards.map((c) => cardId(conceptKey, c.front)), [cards, conceptKey]);
  const [reviews, setReviews] = useState<Map<string, CardReview>>(new Map());
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<Mode>("flip");
  const [queue, setQueue] = useState<Card[]>([]);
  const [studyingAhead, setStudyingAhead] = useState(false);

  // per-card UI state
  const [revealed, setRevealed] = useState(false); // flip mode
  const [picked, setPicked] = useState<string | null>(null); // choice/cloze
  const [typed, setTyped] = useState("");
  const [answered, setAnswered] = useState(false); // quiz modes

  // session tally
  const [graded, setGraded] = useState(0);
  const [againCount, setAgainCount] = useState(0);

  const build = useCallback(
    async (includeAll = false) => {
      setLoading(true);
      let list: CardReview[] = [];
      try {
        list = await api.cardReviews();
      } catch {
        list = [];
      }
      const m = new Map(list.map((r) => [r.card_id, r]));
      const today = todayStr();
      const pool = cards.filter((c) => {
        const r = m.get(cardId(conceptKey, c.front));
        return includeAll || !r || r.due_date <= today;
      });
      setReviews(m);
      setQueue(shuffle(pool));
      setStudyingAhead(includeAll);
      setGraded(0);
      setAgainCount(0);
      setRevealed(false);
      setPicked(null);
      setTyped("");
      setAnswered(false);
      setLoading(false);
    },
    [cards, conceptKey]
  );

  useEffect(() => {
    build();
  }, [build]);

  const current = queue[0];

  // reset the per-card interaction whenever the card or mode changes
  useEffect(() => {
    setRevealed(false);
    setPicked(null);
    setTyped("");
    setAnswered(false);
  }, [current?.front, mode]);

  const grade = useCallback(
    async (quality: number) => {
      if (!current) return;
      const id = cardId(conceptKey, current.front);
      try {
        const cr = await api.gradeCard(id, quality);
        setReviews((m) => new Map(m).set(id, cr));
      } catch {
        /* keep going even if persistence hiccups */
      }
      setGraded((g) => g + 1);
      const again = quality === 0;
      if (again) setAgainCount((a) => a + 1);
      setQueue((q) => {
        const [cur, ...rest] = q;
        if (!again) return rest;
        if (rest.length === 0) return [cur]; // last one standing — loops
        const span = Math.min(20, rest.length);
        const pos = 1 + Math.floor(Math.random() * span); // 1..span cards ahead
        const arr = [...rest];
        arr.splice(pos, 0, cur);
        return arr;
      });
    },
    [conceptKey, current]
  );

  // Build the question for the current card + mode (stable until either changes)
  const quiz = useMemo(() => {
    if (!current || mode === "flip") return null;
    const others = cards;
    if (mode === "type") {
      return { kind: "type" as const, accepted: normRomaji(romajiOf(current.reading)) };
    }
    if (mode === "cloze" && current.example_ja.includes(current.front)) {
      const distract = sample(others, 3, (c) => c.front === current.front).map((c) => c.front);
      return {
        kind: "cloze" as const,
        prompt: current.example_ja.split(current.front).join(BLANK),
        answer: current.front,
        options: shuffle([current.front, ...distract]),
      };
    }
    // choice (and cloze fallback): random direction
    const jp2en = mode === "cloze" ? true : Math.random() < 0.5;
    const answer = jp2en ? current.meaning : current.front;
    const distract = sample(others, 3, (c) => c.front === current.front).map((c) =>
      jp2en ? c.meaning : c.front
    );
    return {
      kind: "choice" as const,
      jp2en,
      prompt: jp2en ? current.front : current.meaning,
      answer,
      options: shuffle([answer, ...distract]),
    };
  }, [current?.front, mode, cards]);

  function submitTyped() {
    if (!quiz || quiz.kind !== "type") return;
    setAnswered(true);
  }

  const nextDue = useMemo(() => {
    const today = todayStr();
    const future = ids
      .map((id) => reviews.get(id)?.due_date)
      .filter((d): d is string => !!d && d > today)
      .sort();
    return future[0];
  }, [ids, reviews]);

  const knownCount = useMemo(
    () => ids.filter((id) => (reviews.get(id)?.reps ?? 0) > 0).length,
    [ids, reviews]
  );

  if (loading) return <div className="card dim">Loading cards…</div>;

  /* ---- session finished / nothing due -------------------------------- */
  if (!current) {
    return (
      <div className="card" style={{ textAlign: "center", padding: "26px 18px" }}>
        <div style={{ fontSize: 30, marginBottom: 6 }}>{graded > 0 ? "🎉" : "🌸"}</div>
        <h3 style={{ margin: "0 0 4px" }}>
          {graded > 0 ? "Session complete!" : "You're all caught up."}
        </h3>
        <p className="dim" style={{ marginTop: 0 }}>
          {graded > 0 && `${graded} reviewed · ${againCount} need another look · `}
          {knownCount}/{cards.length} cards started
          {nextDue && ` · next due ${nextDue}`}
        </p>
        <div className="row" style={{ justifyContent: "center", gap: 8, flexWrap: "wrap" }}>
          <button onClick={() => build(false)}>Study due</button>
          <button className="ghost" onClick={() => build(true)}>
            Study ahead (all {cards.length})
          </button>
          {knownCount > 0 && (
            <button
              className="ghost"
              onClick={async () => {
                await api.resetCards(ids).catch(() => {});
                build(false);
              }}
            >
              Reset progress
            </button>
          )}
        </div>
      </div>
    );
  }

  const total = graded + queue.length;
  const pct = total > 0 ? Math.round((graded / total) * 100) : 0;

  return (
    <div>
      {/* header: mode switch + progress */}
      <div className="row" style={{ justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
        <div className="row" style={{ gap: 6, flexWrap: "wrap" }}>
          {modes.map((m) => (
            <button
              key={m.id}
              className={mode === m.id ? "" : "ghost"}
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => setMode(m.id)}
            >
              {m.label}
            </button>
          ))}
        </div>
        <div className="dim" style={{ fontSize: 12, alignSelf: "center" }}>
          {queue.length} left{studyingAhead ? " (ahead)" : " due"} · {graded} done
        </div>
      </div>

      <div
        style={{
          height: 5,
          borderRadius: 3,
          background: "var(--bg-elev-2)",
          margin: "8px 0 14px",
          overflow: "hidden",
        }}
      >
        <div style={{ width: `${pct}%`, height: "100%", background: "var(--accent)" }} />
      </div>

      {/* ---- FLIP ------------------------------------------------------- */}
      {mode === "flip" && (
        <>
          <div
            className="card"
            onClick={() => !revealed && setRevealed(true)}
            style={{
              minHeight: 190,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              textAlign: "center",
              cursor: revealed ? "default" : "pointer",
              padding: "24px 20px",
            }}
          >
            <div style={{ fontSize: 40, fontWeight: 600 }}>{current.front}</div>
            {revealed ? (
              <CardBack card={current} variant={variant} />
            ) : (
              <p className="dim" style={{ marginTop: 16, marginBottom: 0, fontSize: 13 }}>
                Tap to reveal
              </p>
            )}
          </div>
          {revealed ? (
            <GradeRow onGrade={grade} />
          ) : (
            <div className="row" style={{ marginTop: 12 }}>
              <button onClick={() => setRevealed(true)}>Show answer</button>
            </div>
          )}
        </>
      )}

      {/* ---- CHOICE / CLOZE -------------------------------------------- */}
      {(mode === "choice" || mode === "cloze") && quiz && quiz.kind === "choice" && (
        <ChoiceQuiz
          promptBig={quiz.jp2en}
          prompt={quiz.prompt}
          options={quiz.options}
          answer={quiz.answer}
          picked={picked}
          answered={answered}
          onPick={(opt) => {
            if (answered) return;
            setPicked(opt);
            setAnswered(true);
          }}
          card={current}
          variant={variant}
          onNext={() => grade(picked === quiz.answer ? 2 : 0)}
        />
      )}
      {mode === "cloze" && quiz && quiz.kind === "cloze" && (
        <ChoiceQuiz
          promptBig={false}
          prompt={quiz.prompt}
          options={quiz.options}
          answer={quiz.answer}
          picked={picked}
          answered={answered}
          onPick={(opt) => {
            if (answered) return;
            setPicked(opt);
            setAnswered(true);
          }}
          card={current}
          variant={variant}
          onNext={() => grade(picked === quiz.answer ? 2 : 0)}
        />
      )}

      {/* ---- TYPE ------------------------------------------------------- */}
      {mode === "type" && quiz && quiz.kind === "type" && (
        <div>
          <div className="card" style={{ textAlign: "center", padding: "24px 18px" }}>
            <div style={{ fontSize: 40, fontWeight: 600 }}>{current.front}</div>
            <p className="dim" style={{ margin: "6px 0 14px", fontSize: 13 }}>
              Type the reading in rōmaji
            </p>
            <input
              autoFocus
              value={typed}
              disabled={answered}
              onChange={(e) => setTyped(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") (answered ? grade(normRomaji(typed) === quiz.accepted ? 2 : 0) : submitTyped());
              }}
              placeholder="e.g. hensuu"
              style={{
                fontSize: 18,
                textAlign: "center",
                padding: "8px 12px",
                width: "100%",
                maxWidth: 320,
                borderRadius: 8,
                border: `1px solid ${
                  answered
                    ? normRomaji(typed) === quiz.accepted
                      ? "var(--good)"
                      : "var(--bad)"
                    : "var(--border)"
                }`,
                background: "var(--bg-elev-2)",
                color: "var(--text)",
              }}
            />
            {answered && (
              <div style={{ marginTop: 12 }}>
                <div
                  style={{
                    color: normRomaji(typed) === quiz.accepted ? "var(--good)" : "var(--bad)",
                    fontWeight: 600,
                  }}
                >
                  {normRomaji(typed) === quiz.accepted ? "Correct!" : "Not quite"}
                </div>
                <CardBack card={current} variant={variant} />
              </div>
            )}
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            {!answered ? (
              <button onClick={submitTyped} disabled={!typed.trim()}>
                Check
              </button>
            ) : (
              <button onClick={() => grade(normRomaji(typed) === quiz.accepted ? 2 : 0)}>
                Next →
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/* --------------------------------------------------------------- subviews */

function CardBack({ card, variant = "japanese" }: { card: Card; variant?: StudyVariant }) {
  if (variant === "vocab") {
    // Java-vocab layout: textbook line, plain-English line, then a code snippet.
    // (meaning = textbook, example_en = plain English, example_ja = code.)
    return (
      <div style={{ marginTop: 14, width: "100%", maxWidth: 560, textAlign: "left" }}>
        <div style={{ fontSize: 12, color: "var(--accent)", marginBottom: 2 }}>Textbook</div>
        <div style={{ fontSize: 16, marginBottom: 12 }}>{card.meaning}</div>
        <div style={{ fontSize: 12, color: "var(--accent)", marginBottom: 2 }}>In plain English</div>
        <div style={{ fontSize: 15, marginBottom: card.example_ja ? 12 : 0 }}>{card.example_en}</div>
        {card.example_ja && (
          <pre
            style={{
              margin: 0,
              padding: "8px 10px",
              borderRadius: 6,
              background: "var(--bg-elev-2)",
              fontSize: 13,
              overflowX: "auto",
            }}
          >
            <code>{card.example_ja}</code>
          </pre>
        )}
      </div>
    );
  }
  return (
    <div style={{ marginTop: 14, width: "100%", maxWidth: 520 }}>
      <div style={{ fontSize: 15, color: "var(--accent)", marginBottom: 4 }}>{card.reading}</div>
      <div style={{ fontSize: 17, marginBottom: 12 }}>{card.meaning}</div>
      <div style={{ borderTop: "1px solid var(--border)", paddingTop: 12, lineHeight: 1.7 }}>
        <div style={{ fontSize: 15 }}>{card.example_ja}</div>
        <div className="dim" style={{ fontStyle: "italic", fontSize: 13 }}>
          {card.example_en}
        </div>
      </div>
    </div>
  );
}

function GradeRow({ onGrade }: { onGrade: (q: number) => void }) {
  return (
    <div className="row" style={{ marginTop: 12, gap: 8, flexWrap: "wrap" }}>
      {GRADES.map((g) => (
        <button
          key={g.q}
          className="ghost"
          style={{ flex: "1 1 0", minWidth: 84, borderColor: g.color, color: g.color }}
          onClick={() => onGrade(g.q)}
          title={`${g.label} — ${g.hint}`}
        >
          <div>{g.label}</div>
          <div className="dim" style={{ fontSize: 11 }}>
            {g.hint}
          </div>
        </button>
      ))}
    </div>
  );
}

function ChoiceQuiz({
  promptBig,
  prompt,
  options,
  answer,
  picked,
  answered,
  onPick,
  onNext,
  card,
  variant = "japanese",
}: {
  promptBig: boolean;
  prompt: string;
  options: string[];
  answer: string;
  picked: string | null;
  answered: boolean;
  onPick: (opt: string) => void;
  onNext: () => void;
  card: Card;
  variant?: StudyVariant;
}) {
  return (
    <div>
      <div className="card" style={{ textAlign: "center", padding: "22px 18px" }}>
        <div style={{ fontSize: promptBig ? 38 : 20, fontWeight: 600, lineHeight: 1.4 }}>
          {prompt}
        </div>
      </div>
      <div className="grid cols-2" style={{ marginTop: 10 }}>
        {options.map((opt) => {
          let border: string | undefined;
          if (answered) {
            if (opt === answer) border = "var(--good)";
            else if (opt === picked) border = "var(--bad)";
          }
          return (
            <button
              key={opt}
              className="ghost"
              style={{ textAlign: "left", borderColor: border, color: border, padding: "10px 12px" }}
              onClick={() => onPick(opt)}
              disabled={answered}
            >
              {opt}
            </button>
          );
        })}
      </div>
      {answered && (
        <>
          <div className="card" style={{ marginTop: 12, textAlign: "center" }}>
            <CardBack card={card} variant={variant} />
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <button onClick={onNext}>Next →</button>
          </div>
        </>
      )}
    </div>
  );
}
