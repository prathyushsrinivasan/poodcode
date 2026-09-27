/**
 * 日本語: the core vocabulary and one review deck (UI_ROADMAP G6, A2).
 *
 * This used to be the top of Learn's 日本語 tab, above the glossary sets — so
 * the thing you do every day (review the deck) sat inside a concept library,
 * and the nav's 日本語 group led only to the bridge. It is a page of its own
 * now, beside the bridge in the nav. The glossary sets stay in Learn, where the
 * other chapters are; this page links to them.
 *
 * The open flashcard lives in the URL (`?word=<id>`) so it can be linked to —
 * the bridge's vocabulary chips do — and Back closes it.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import type { Card, JpVocab } from "../../types";
import { CardStudy } from "../../components/CardStudy";
import { JpVocabCard, JpVocabMenu, useVocabReviews } from "../../components/JpVocab";
import { Section, useCollapse } from "../../components/Collapsible";
import { TrackSkeleton } from "../../components/Skeleton";
import { Badge, ErrorState, Icon, PageHeader } from "../../components/ui";
import { vocabCardId } from "../../lib/jpVocab";
import { joinReading } from "../../lib/romaji";
import { conceptLang, loadVocab, useLearnData } from "./learnData";

export default function JapanesePage() {
  const { concepts } = useLearnData();
  const [vocab, setVocab] = useState<JpVocab | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const [vocabList, setVocabList] = useState<string[]>([]);
  // Review state is shared by the menu (which shows the counts) and the card
  // (which does the grading), so it is owned here rather than by either.
  const vocabReviews = useVocabReviews();
  const [params, setParams] = useSearchParams();
  const openWord = params.get("word");
  const sec = useCollapse("jp-page");

  useEffect(() => {
    setError("");
    loadVocab()
      .then(setVocab)
      .catch((e) => setError(String(e)));
  }, [attempt]);

  const openVocab = (id: string, list: string[]) => {
    setVocabList(list);
    setParams({ word: id });
  };
  const navigateVocab = useCallback((id: string) => setParams({ word: id }, { replace: true }), [setParams]);
  const closeVocab = useCallback(() => {
    const next = new URLSearchParams(params);
    next.delete("word");
    setParams(next, { replace: true });
  }, [params, setParams]);

  const glossarySets = useMemo(() => (concepts ?? []).filter((c) => conceptLang(c) === "japanese"), [concepts]);

  /**
   * One deck for all of 日本語: the vocabulary list plus every glossary set,
   * de-duplicated by card id. The two used to schedule separately, so "what
   * should I review today?" had fourteen answers. Words that exist in both
   * places share one id, which is what makes merging them honest: 配列 is one
   * card in this deck, not one from each source.
   */
  const reviewDeck = useMemo<Card[]>(() => {
    const out: Card[] = [];
    const seen = new Set<string>();
    const push = (card: Card, id: string) => {
      if (seen.has(id)) return;
      seen.add(id);
      out.push(card);
    };
    for (const w of vocab?.words ?? []) {
      const id = vocabCardId(w.id);
      push(
        {
          front: w.term,
          card_id: id,
          reading: joinReading(w.reading, w.romaji),
          meaning: w.meaning,
          example_ja: w.example_ja,
          example_en: w.example_en,
        },
        id
      );
    }
    for (const c of glossarySets) for (const card of c.cards ?? []) push(card, card.card_id || `${c.key}#${card.front}`);
    return out;
  }, [vocab, glossarySets]);

  if (error) {
    return (
      <div className="page">
        <PageHeader title="日本語" />
        <ErrorState title="The vocabulary deck could not be loaded." error={error} onRetry={() => setAttempt((n) => n + 1)} />
      </div>
    );
  }
  if (!vocab) return <TrackSkeleton cards={4} />;

  return (
    <div className="page jp-page">
      <PageHeader
        eyebrow="Languages"
        title="日本語 vocabulary"
        subtitle={
          <>
            {vocab.words.length} core non-katakana words for Java, coding problems and TypeScript. Filter by tag, open a
            word for its reading, meaning and an example sentence — and review everything due in one deck.
          </>
        }
      />

      <ul className="learn-promos">
        <li>
          <Link to="/jp-bridge" className="card learn-promo">
            <Icon name="code" size={20} />
            <span className="learn-promo-text">
              <strong>日本語 → Java — put the vocabulary to work</strong>
              <span>Real coding problems stated in Japanese, solved in Java, plus interview practice.</span>
            </span>
            <Icon name="chevronRight" size={16} />
          </Link>
        </li>
        <li>
          <Link to="/learn?track=japanese" className="card learn-promo">
            <Icon name="learn" size={20} />
            <span className="learn-promo-text">
              <strong>{glossarySets.length} glossary sets in Learn</strong>
              <span>Full glossaries by topic — Java, control flow, errors, Git, the workplace.</span>
            </span>
            <Icon name="chevronRight" size={16} />
          </Link>
        </li>
      </ul>

      {reviewDeck.length > 0 && (
        <Section
          title="Review — まとめて復習"
          outline="Review"
          open={sec.isOpen("review")}
          onToggle={() => sec.toggle("review")}
          meta={<Badge>{reviewDeck.length} cards</Badge>}
        >
          <p className="section-lead">
            The vocabulary list and every glossary set in <strong>one session</strong> — whatever is due today,
            wherever it lives. A word that appears in both is one card here, not two.
          </p>
          <CardStudy conceptKey="jp-review" cards={reviewDeck} variant="japanese" />
        </Section>
      )}

      {vocab.words.length > 0 && (
        <Section
          title="Vocabulary — 語彙"
          outline="Vocabulary"
          open={sec.isOpen("vocab")}
          onToggle={() => sec.toggle("vocab")}
          meta={<Badge>{vocab.words.length} words</Badge>}
        >
          <JpVocabMenu vocab={vocab} reviews={vocabReviews} onOpen={openVocab} />
        </Section>
      )}

      {openWord && (
        <JpVocabCard
          vocab={vocab}
          id={openWord}
          list={vocabList}
          reviews={vocabReviews}
          onNavigate={navigateVocab}
          onClose={closeVocab}
        />
      )}
    </div>
  );
}
