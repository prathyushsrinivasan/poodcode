# N2 reading content

All 113 passages are original practice material: 100 short, 5 medium, 3 paired
AB passages, 2 long arguments, and 3 information-search documents. Together they
provide 128 questions. They ship with the app and work offline.

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

Run `npm test -- src/lib/dokkai.test.ts` for corpus, annotation, progress, and
vocabulary-scheduling checks, then `npm run build`. Browser checks run with the
mock backend and a local Chromium:

```
npm run dev:mock -- --port 5180
node tools/check_jlpt_reading.mjs --base http://localhost:5180 --chromium PATH
```

The browser checker accepts `--playwright PATH` to a local playwright-core entry,
`--axe PATH` to axe.min.js for accessibility checks, and `--screenshot PATH`.
It verifies the reading formats, answer flows, lookup and saved-word review,
persistence, bookmarks, filtering, timed expiry, and responsive layouts.
