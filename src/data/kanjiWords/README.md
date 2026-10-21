# Kanji Word Builder

Open **Languages → JLPT N2 courses → Kanji Word Builder**. The initial bank
contains **20 kanji and 733 vocabulary entries**, with **73 multiple-meaning
items**. Different readings of a homograph can be separate entries. A shared
compound appears under every applicable kanji, with one shared progress ID.

The families are 生 学 会 人 心 意 力 行 動 事 物 合 定 成 化 性 表 取 交 分.
Each family currently has 25–63 entries. These productive characters were chosen
for their useful intermediate and advanced compounds, not because the characters
themselves all first appear at N2.

## Practice behavior

1. Show the written word and, for ambiguous readings, a Japanese context cue.
   Type its entire reading in hiragana using a Japanese IME. Romaji and katakana
   are not accepted. Normalization handles Unicode combining marks and spacing,
   while preserving small kana, long vowels and distinctions such as づ/ず.
   Only explicitly reviewed alternate readings are accepted. Enter while an IME
   composition is active does not submit an answer.
2. Reveal the reading result, then continue to an English meaning question.
   One study sense uses radios; multiple distinct senses use checkboxes.
   Synonyms share one option. The exact correct set is required. The cue
   disambiguates the reading; meaning questions cover the listed study senses
   of that reading, beyond the cue sentence alone. Notes and option explanations
   are shown after the meaning attempt, so they cannot spoil that question.

Revealing an answer records an incorrect result for that skill. Reading and
meaning results save independently using the existing SQLite settings API and
the separate `jlpt-kanji-word-practice-v1` key. Both latest results must be
correct for a word to count as complete. Mistake review includes either failed
skill. A correct reading with an unattempted meaning remains unfinished.

The library offers search by written form, aliases, hiragana and English,
estimated-level and progress filters, and an explicit reveal toggle. Practice
up to ten matching words or every matching word in a family. A five-word mixed
round and global mistake review are available. Filters constrain the practice
pool as well as the visible library. Rounds are snapshotted before answering;
correcting one word does not shift or skip the others. Mistakes precede
unfinished words, then completed words. A round recap supports retrying misses.

Submitted results persist across navigation/restart. Unsubmitted text, current
stage and round position do not. Load/save failures have explicit retry controls.
The bank and all grading work offline; external documentation links need internet.

## Content and sources

The reference selection is every whole-word match for the 20 characters from
the N1, N2 and N3 CSV files in
[Open Anki JLPT](https://github.com/jamsinclair/open-anki-jlpt-decks), revision
`1ad66734417aca9dbcca6b2d5ee440cb13ab3ba0`, plus editorial supplements.
The original collection acknowledges chyyran/jlpt-anki-decks and Tanos.
Reference spelling variants are normalized where useful, duplicates are merged,
and expressions with placeholder affixes or unresolved annotations are excluded.
The exact input hashes and excluded source rows are recorded in `manifest.json`.
The bank is a broad starter collection, not an exhaustive dictionary.

**JLPT levels are estimates.** The
[official JLPT FAQ](https://www.jlpt.jp/e/faq/index.html) explains that vocabulary,
kanji and grammar lists are not published for the current test. Reference
classification and editorial study levels are therefore not official assignments;
some familiar core words are included to make the families useful for revision.

The spelling/reading pairs, including accepted alternate readings, were checked
against **JMdict**, copyright James William Breen and the Electronic Dictionary
Research and Development Group, using the English JSON conversion from
[scriptin/jmdict-simplified](https://github.com/scriptin/jmdict-simplified),
release `3.6.2+20261019180022` (dictionary date **2026-10-19**).
JMdict entry IDs are retained for verification. Its glosses are also used during
building to reject distractors with overlapping wording; these full dictionary
glosses are not bundled. Original reference glosses are adapted, and editorial
overrides group synonyms and distinguish selected common senses. The exercises
test those study senses rather than every specialist or historical dictionary
meaning. Distractor explanations identify the alternative Japanese concept.

Data attribution, source links and the complete licenses (readable offline)
appear on each course screen. Reference data
is available under the [MIT license](JLPT-LICENSE.txt), copyright 2020 Jamie
Sinclair. Dictionary-derived data and this adapted vocabulary dataset are made
available under [CC BY-SA 4.0](CC-BY-SA-4.0.txt), with the required attribution
retained. These data notices do not change the license of application code.
See the [EDRDG license statement](https://www.edrdg.org/edrdg/licence.html).

## Rebuilding and maintaining the bank

`editorial.json` contains reviewed meanings, cues, accepted variants,
supplements and the distractor pool. `words.json` is generated; edit the
editorial source and rebuild rather than editing generated rows directly.

1. Download `src/n1.csv`, `src/n2.csv`, and `src/n3.csv` from the pinned reference
   revision into a temporary source directory. The committed manifest records
   SHA-256 hashes; verify them before claiming a reproduction of this bank.
2. Download the English JMdict JSON archive from the pinned release above and
   extract it outside the repository. Do not commit the complete dictionary.
3. Run:

   ```text
   python tools/build_kanji_words.py --source-dir PATH_TO_CSVS --dictionary PATH_TO_JMDICT_JSON
   ```

The build validates the main and reviewed alternative readings, creates stable
IDs from canonical spelling/reading pairs, preserves source levels, produces
deterministic distractors, and writes the manifest. Keep word IDs and option
meanings stable after release, or explicitly migrate affected progress. For a
new reference revision, review changes and update the revision/hash provenance.
Periodically review against updated dictionary releases and rerun the checks;
there is no runtime online dictionary dependency.

Checks:

- `npm test -- src/lib/kanjiWords.test.ts`: content coverage, all readings and
  answer sets, homographs, Unicode grading, progress parsing and round planning.
- `npm run build`: TypeScript and production bundling.
- `npm run dev:mock -- --host 127.0.0.1 --port 5183`, then
  `node tools/check_kanji_words.mjs --playwright PATH_TO_INDEX_MJS --chromium PATH_TO_CHROME`
  exercises the 20 libraries, representative reading/meaning sessions,
  homographs, multiple-answer failures, IME behavior, persistence, shared-word
  progress, review, filtering, save retry and responsive layout.
