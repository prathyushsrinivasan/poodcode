# Japanese Roadmap — expanding the 日本語 track

The plan for growing the **日本語** view of the Learn tab. Today it teaches you to
*recognise* coding vocabulary in Japanese. The goal is to also let you
*read* a real problem statement, *follow* a code review and *answer* an
interview question in Japanese without reaching for a dictionary.

Unlike [`JAVA_ROADMAP.md`](JAVA_ROADMAP.md) and [`TS_ROADMAP.md`](TS_ROADMAP.md),
nothing here is judged by a compiler. The risk is not a wrong expected output but a
wrong reading or an unnatural sentence, and the generator guards are how that risk
gets managed (see [Rules](#rules-that-every-step-keeps)).

**Status legend** — ✅ built and shipping · 🚧 partially built · ⬜ planned.

> **All twelve steps have shipped**, in the order the sequencing notes set out.
>
> This file is kept for the reasoning rather than the plan: why the vocabulary
> list won over the glossary sets, why a single kanji in a verb stem is never
> given furigana, why the review-id migration had to merge rather than rename.
>
> Two things in it are now historical. **"Where it stands"** below describes the
> track as it was *before* this work — where it says 100 words, 292 cards and 12
> bridge problems, the track now has **400 words, 284 cards across 13 sets, and
> 40 bridge problems with 40 interview questions**. And the audit's nine findings
> are the case for the work, not a description of the code: every one of them has
> been addressed.
>
> Step 6's title below still reads "100 to 300" because that is what that step
> was, and it shipped exactly that. The list has since grown past its target in
> two further batches of 50, on the same per-tag floors and the same guards.

---

## Where it stands

Three surfaces, all reference data with no SQLite schema of their own (only
per-card review state lives in `card_reviews`):

| Surface | Content | Authored in | Seed | UI |
|---|---|---|---|---|
| ✅ **Vocabulary** (first section) | 100 non-katakana words — 34 Java, 33 coding problems, 33 TypeScript — each a flashcard with reading, English + Japanese description and an example sentence | `tools/jp_vocab_defs.py` | `seeds/jp_vocab.json` | `src/components/JpVocab.tsx` |
| ✅ **Glossary sets** | 12 sets, 292 cards, studied with SM-2 in four modes (flip, choice, cloze, type the reading) | `tools/japanese_defs.py` | `seeds/concepts.json` | `src/pages/Learn.tsx` + `src/components/CardStudy.tsx` |
| 🚧 **日本語 → Java bridge** | 12 bank problems restated in Japanese (8 Intro, 4 Easy) and 12 interview Q&A | `tools/japanese_bridge.py` | `seeds/jp_bridge.json` | `src/pages/JapaneseBridge.tsx` |

| | |
|---|---|
| Regenerate | `python tools/gen_seed.py` — the vocabulary guards run here |
| Unit tests | `npx vitest run src/lib/jpVocab.test.ts` |
| Rust side | `cd src-tauri && cargo check` — seeds are `include_str!`-embedded |

---

## What an audit of the current content found

1. **The vocabulary is read, not studied.** A word's flashcard flips and pages,
   but nothing is recorded. The glossary sets next door already have SM-2
   scheduling, four study modes and a due count; the vocabulary list has none of
   it.
2. **Two sources for the same word.** 46 of the 100 vocabulary terms also exist
   as glossary cards, each with its own reading, meaning and example — 継承,
   配列, 型推論, 非同期 and 42 more. Nothing checks that the two agree, so an edit
   to one silently diverges from the other.
3. **The glossary sets are katakana-heavy where it teaches least.** 64 of 292
   cards are pure katakana — 14 of 26 in *Java Language*, 11 of 26 in *TS
   Objects & Tooling*, 10 of 22 in *Dev Tools & Git*. A loanword like クラス is
   its own reading; the Type-the-reading mode on it tests rōmaji, not Japanese.
4. **Sentences have no readings.** The headword has its hiragana, but
   `example_ja` and `desc_ja` are plain kanji. A learner who can read 配列 may
   still stall on 与えられます in the same sentence.
5. **No self-checks.** All 12 glossary sets have `quiz: 0`, and a set is marked
   done by scrolling to the bottom.
6. **The bridge stops at Easy.** 12 of the bank's 271 problems are restated, all
   Intro or Easy, while the bank holds 125 Medium and 28 Hard. The interview bank
   is 12 questions, all about a single coding round.
7. **One tag per word.** 計算量 is as much a Java-interview word as a
   coding-problem word, but the filter can only put it in one place.
8. **Hard to find.** The command palette has no Japanese entries, and a card
   can be linked (`/learn?word=keisho`) but nothing links to one — not even the
   bridge's vocabulary chips, which show the same words.
9. **No sound.** Readings are text only; there is no way to hear a word.

---

## Phase 1 — make the vocabulary studyable ✅

Cheap, UI-only, no schema change. The highest value per hour on this page.

### Step 1 — Spaced repetition for vocabulary ✅

**Work.**

1. Grade each word with Again / Hard / Good / Easy after the flip, through the
   existing `api.gradeCard`, keyed `cardId("jp-vocab", word.id)`. The
   `card_reviews` table is keyed by string, so nothing in Rust changes.
2. Add a **Due** filter chip beside the tags, with a count, and a "study due"
   button that opens the first due card and walks only due cards.
3. Show a small state dot on each tile — new, learning, due — so the menu
   doubles as a progress view.

**Payoff.** The 100 words come back on a schedule instead of being read once.

### Step 2 — Study modes ✅

**Work.** Reuse `CardStudy`'s ideas without its deck coupling:

- **Reverse** — English meaning on the front, produce the Japanese.
- **Type the reading** — extract `normRomaji` / `romajiOf` from
  `CardStudy.tsx` into `src/lib` first, so both decks share one grader, and
  accept hiragana input as well as rōmaji.
- **Cloze** — blank the term out of `example_ja`. The generator already
  guarantees the term appears in the sentence, so every word supports it.

### Step 3 — Multiple tags per word ✅

**Work.** `tag: string` → `tags: string[]` in the seed, `models.rs` and
`types.ts`; a filter matches if any tag does; `tagCounts` counts a word once per
tag it carries. Lint: every word has at least one tag, and every tag id is
declared in `JP_VOCAB_TAGS`.

---

## Phase 2 — one source of truth ✅

### Step 4 — Reconcile the 46 overlapping words ✅

**Work.**

1. **First, a guard (one commit, no content change):** in `gen_seed.py`, after
   both files have run, assert that any term present in both `JP_VOCAB` and a
   glossary set has the same reading. Fix whatever it catches.
2. **Then decide the direction.** Recommended: the vocabulary list becomes
   canonical for non-katakana words. A glossary set lists word *ids* for those,
   and `_jp_cards` expands them from `JP_VOCAB`, so the richer vocabulary entry
   (with both descriptions) feeds the set's card study too.
3. Card review ids change for migrated cards (`jp_coding_basics#配列` →
   `jp-vocab#hairetsu`). Carry existing review state across in a one-off
   migration, or accept a reset — decide before merging, not after.

### Step 5 — Separate the loanwords ✅

**Work.** Move the 64 katakana cards into one dedicated set,
**カタカナ Loanwords**, grouped by domain, with the Type-reading mode turned off
for it (its answer would be the rōmaji of the katakana, which is not the skill).
The remaining sets become kanji-first, matching the vocabulary list's rule.

---

## Phase 3 — more words ✅

### Step 6 — Grow the vocabulary from 100 to 300 ✅

Batches of **50 words per commit**, so each batch can be reviewed as a unit.
The `== 100` assertion in `_jpv_build` becomes a per-tag floor.

Proposed new tags and candidate words — every one kanji or kanji + kana, none
katakana:

| Tag | Candidates |
|---|---|
| `java` (+) | 値渡し (あたいわたし), 不変条件 (ふへんじょうけん), 直列化 (ちょくれつか), 遅延評価 (ちえんひょうか) |
| `typescript` (+) | 副作用 (ふくさよう), 純粋関数 (じゅんすいかんすう), 高階関数 (こうかいかんすう), 巻き上げ (まきあげ), 糖衣構文 (とういこうぶん) |
| `problems` (+) | 閉路 (へいろ), 連結成分 (れんけつせいぶん), 位相整列 (いそうせいれつ), 最小全域木 (さいしょうぜんいきぎ), 約数 (やくすう), 最大公約数 (さいだいこうやくすう), 桁あふれ (けたあふれ) |
| `sql` (new) | 結合 (けつごう), 集計 (しゅうけい), 副問い合わせ (ふくといあわせ), 索引 (さくいん) |
| `web` (new) | 認証 (にんしょう), 認可 (にんか), 要求 (ようきゅう), 応答 (おうとう), 永続化 (えいぞくか) |
| `workplace` (new) | 仕様 (しよう), 要件 (ようけん), 見積もり (みつもり), 不具合 (ふぐあい), 差分 (さぶん), 検証 (けんしょう), 設計 (せっけい), 振り返り (ふりかえり) |

Watch for near-collisions with existing entries: a merge conflict is also
競合, which the list already has as part of 競合状態 (race condition).

### Step 7 — Difficulty ✅

**Work.** Add `level: 1 | 2 | 3` (everyday → textbook → specialist) to each
word, a sort and a filter on it, and a lint that each tag has words at every
level. Study sessions default to level 1 first.

---

## Phase 4 — reading support ✅

### Step 8 — Readings for sentences ✅

**Work.**

1. Author `example_ja` with inline ruby markup: `[配列|はいれつ]が[与|あた]えられます。`
2. The generator strips the markup to produce the plain sentence and asserts
   that the plain form still contains the term (the existing guard, unchanged),
   and that every reading is hiragana.
3. The flashcard renders `<ruby>` in JSX, with a toggle to hide the readings
   once you no longer need them. (The Markdown renderer has no `rehype-raw`, so
   ruby must stay out of glossary *tables* — the card view is the place for it.)
4. Do the same for `desc_ja`, lower priority.

### Step 9 — Pronunciation ✅

**Work.** A speaker button on the card using the Web Speech API
(`speechSynthesis`, `lang: "ja-JP"`), reading the headword and then the
sentence. It stays offline — but it depends on a Japanese voice being
installed in the OS, so detect `getVoices()` for `ja` and hide the button with
an explanation when none is present. No bundled audio.

---

## Phase 5 — put it to work ✅

### Step 10 — A deeper bridge ✅

**Work.**

1. 12 → 40 bridge problems, adding Easy and Medium problems stage by stage
   through the DSA Curriculum, so a learner in `heaps` finds a heaps problem in
   Japanese.
2. Assert at generation time that every bridge `slug` exists in the problem bank.
3. When a bridge vocabulary chip's term is in the vocabulary list, link it to
   `/learn?word=<id>`.

### Step 11 — A wider interview bank ✅

**Work.** 12 → 40 questions, tagged by interview stage — 自己紹介, coding round,
設計 (system design), 振り返り (behavioural) — each with a model answer in
Japanese and English and the key terms linked to their cards.

### Step 12 — One review lane and palette entries ✅

**Work.**

1. A single **日本語 review** that pulls due vocabulary cards and due glossary
   cards into one session.
2. Command-palette entries for *Vocabulary*, each glossary set and the bridge,
   using the same builder the weekly courses use.
3. A multiple-choice self-check per glossary set, generated from its cards
   (meaning → term, term → reading), so a set is marked done by passing it
   rather than by scrolling.

---

## Rules that every step keeps

- **No katakana in a vocabulary term.** Katakana inside sentences and
  descriptions is fine.
- **Readings are hiragana**, and the example sentence **contains the term**
  verbatim — both asserted by `_jpv_build`, and both must survive Step 8's ruby
  markup.
- **Polite form (です・ます)** in every sentence — how the words are heard in a
  standup or an interview.
- **One idea per sentence**, using the headword the way a Japanese engineer
  would, not a translation of an English sentence.
- **A native-speaker read-through per batch.** The content is carefully
  authored but not proofread by a native speaker, and the guards catch
  structure, not naturalness. Mark reviewed batches in the defs file so the
  unreviewed remainder stays visible.

## Sequencing notes

- **Phase 1 first** — it is UI-only and makes every later word worth more.
- **Step 4's guard before Step 6** — reconcile the overlap before tripling the
  list, or the drift grows with it.
- **Step 3 before Step 6** — new tags are cheaper to introduce once words can
  carry several.
- **Step 8 before Step 9** — pronunciation reads the same sentences, and ruby
  markup is the natural place to fix a reading the speech engine gets wrong.
- **Schema changes** (`tags[]`, `level`, ruby markup) touch `jp_vocab_defs.py`,
  `models.rs`, `types.ts` and `jpVocab.ts` together — batch Steps 3 and 7 to
  avoid two rounds of seed regeneration.
- Every step regenerates with `python tools/gen_seed.py` and must keep
  `npm test` and `cargo check` green.
