# N2 reading content

All 238 passages are original practice material: 100 short, 100 medium, 13 paired
AB passages, 12 long arguments, and 13 information-search documents. Together they
provide 388 questions, including 200 medium questions. They ship with the app
and work offline.

`additions/paired.ts`, `additions/long.ts`, and `additions/information.ts` each
append ten passages with explicit IDs: `ab-004`–`ab-013`, `long-003`–`long-012`,
and `information-004`–`information-013`. Paired texts are 270–350 characters each,
long arguments are 900–1,200, and information documents are 600–800. Each new
pair/document has two questions; each long argument has three. Every addition
has a full English translation, exact supporting quotes, and explanations for
all four choices. Legacy passages and question IDs remain unchanged.

Vocabulary opens on hover in passages, questions and choices, without blocking
the reader. Focus or tap also opens it; Arrow Down moves keyboard focus into the
popup, and Escape closes it. Readers can move into the popup to save a word.
Leaving both the word and popup dismisses it. Actual lookups mark unanswered
study results as assisted; timed practice still hides lookups until review.
`additions/vocabulary.ts` supplies additional curated terms; ambiguous 生地 is
explicitly glossed as dough in the bread passage while retaining fabric elsewhere.

The medium library has ten ordered ten-passage practice sets in the existing
中文 reader. The five original entries in `extended.ts` are unchanged, including
all their passage and question IDs. New entries `medium-006`–`medium-100` live in
`medium/set01.ts`–`medium/set10.ts`: the first file completes the first set with
five additions, and each later file supplies ten. `medium/authoring.ts` converts
explicit passage IDs and authored question tuples into the existing schema;
question IDs are always `<passage-id>-q1` and `-q2`. Never insert or renumber
existing entries. Each addition has three paragraphs, 450–550 plain Japanese
characters, two four-choice questions, exact evidence, an English explanation
for every choice, and a complete English translation. Topics span work,
education, technology, daily life, relationships, culture, society and the
environment, with foundation, standard and stretch challenges within N2.

Shared vocabulary includes `medium/vocabulary.ts`; explicit occurrence glosses
cover grammar and inflections with dictionary forms. For example, 生物 is
explicitly read せいぶつ in `medium-068` and なまもの in `medium-096`. The
existing lookup, furigana, saved-word scheduling, bookmark, mistake-review,
translation and timed-mode behavior applies to every addition. No new progress
key or migration is needed: `jlpt-n2-reading-v1` still separates independent,
assisted and timed results by stable question ID.

Short passages live in four authoring files with 25 drafts each. Keep their
order stable: IDs and saved progress are assigned in `index.ts`. Append future
short drafts after the existing four groups instead of inserting into a group.
Extended passages and questions have explicit IDs; never recycle those IDs.

Each question needs one correct choice, three plausible but demonstrably wrong
choices, an English explanation for every choice, and exact plain-text evidence
from its passage. Translations should cover the full text. Passage lengths count
Japanese characters, including punctuation, excluding whitespace and annotation
syntax. AB lengths apply to each text independently.

Vocabulary is provided by curated shared entries in `vocabulary.ts`. Annotate
ambiguous words directly at the occurrence:

```
[生物|なまもの|perishable food]
[生物|せいぶつ|living organisms]
[延期した|えんきした|postponed|延期する]
```

The fourth field is an optional dictionary form; the reading always belongs to
the displayed surface. Explicit annotations override shared vocabulary. Use exact
plain-text quotes for evidence, without annotation syntax. The same renderer also
annotates questions and answer choices.

Run `npm test -- src/lib/dokkai.test.ts` for counts, ordered IDs, strict new-medium
lengths, distinct texts, four-choice questions, exact highlightable evidence,
translations, kana/meaning/lemma validity, vocabulary coverage in passages,
questions and choices, and progress and vocabulary scheduling. A normalized
four-character overlap check rejects substantial shared passage templates
(threshold 35%; a similarity metric cannot by itself judge literary originality).
Then run `npm run build`. Browser checks run with the
mock backend and a local Chromium:

```
npm run dev:mock -- --port 5180
node tools/check_jlpt_reading.mjs --base http://localhost:5180 --chromium PATH
```

The browser checker accepts `--playwright PATH` to a local playwright-core entry,
`--axe PATH` to axe.min.js for accessibility checks, and `--screenshot PATH`.
It verifies the reading formats, all ten medium sets, answer flows, review-only
translations, lookup and saved-word review, persistence across reloads,
bookmarks, filtering by result mode, multi-question timed expiry, and responsive
layouts at 390, 960 and 1440 pixels. With axe, it also checks both themes.

Run `npm run app:build` to rebuild the Windows executable and both installers.
Outputs are under `src-tauri/target/release/poodcode.exe`,
`src-tauri/target/release/bundle/msi/` and
`src-tauri/target/release/bundle/nsis/`; generated binaries are not committed.
