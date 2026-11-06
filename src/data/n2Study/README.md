# N2 study foundation

Open **Languages → JLPT** for four groups: Kanji & Vocabulary, Grammar,
Reading and Listening. The old `/japanese/n2/library` URL redirects there.
Existing course URLs and progress keys are unchanged. Kanji Spelling covers
spelling, similar characters, homophones and okurigana. Only the five listening
formats remain coming soon. Kanji Reading includes typed/choice practice,
compound sound changes, context-dependent readings and aligned kana feedback.

## Learning experience

- **Practice:** choose a format directly from the four groups. Each guided
  format has one start button, an optional timer and collapsed study tips.
  Vocabulary covers word formation, contextual blanks, paraphrases and usage.
  Reading links open the five passage types directly, with advanced filters
  and additional practice options collapsed. Specialist kanji drills are selected
  in collapsed practice options, without adding homepage sections.
- **Vocabulary depth:** word combinations, confusing words, particles, verb pairs,
  adverbs, register, contextual senses and usage repairs. Optional topic filters
  cover work, education, daily life, society, environment, health, technology and
  relationships.
- **Grammar:** twelve additional patterns, a collapsed searchable reference with
  formation, tone and paired examples, and filters for meaning group and exercise
  (selection, formation, comparison, correction or register). Four multi-paragraph
  texts each have three separately graded blanks.
- **Reading skills:** open a reading library's collapsed options, then Reading
  skill drills. Main points, references, argument roles, facts/opinions, answer
  strength, paragraph summaries and sentence structure have focused practice.
  Clause breakdowns appear after answering. Tables and notices combine schedules,
  prices, capacity, discounts and exceptions; their tables scroll by keyboard or
  touch at narrow widths. Information Retrieval also links directly to this drill.
- **Guided rounds:** a mini lesson before a new format, typed hiragana,
  four-choice questions or keyboard-operable full sentence assembly. Confidence,
  optional hints, reveal, bookmarks, per-option explanations, exact evidence,
  translations and mistake notes. Answers using help are marked assisted.
- **Timed rounds:** a fixed wall-clock deadline, editable answers and question
  navigation. Explanations and hints are unavailable until the round finishes.
  Leaving/reloading does not reset the deadline. Expiry grades saved answers
  and unanswered questions exactly once. These are short practice sets, not
  full-length mock exams or predictors of JLPT scaled scores.
- **Saved rounds:** the home page shows a resume link when a round is active.
  Recaps retain explanations, notes and retries. Historical review, progress
  and plan data remain in storage; their former navigation tabs were removed.

## Content authoring

`schema.ts` owns the content contract. `index.ts` combines the original samples,
the section modules and adapters for the full assembly bank and selected reading
questions. The bank now has 457 questions, including 36 spelling, 64 kanji-reading,
62 context, 20 paraphrase/sense, 20 usage, 50 grammar, 125 assembly, 15 text-grammar
and 53 focused reading-skill questions, plus 12 retained foundation examples.
The separate affix bank still has 300 questions and Word Builder has 820 words.

Author new questions in the relevant module: `spelling.ts`, `readings.ts`,
`vocabulary.ts`, `vocabularyUsage.ts`, `grammar.ts`, `grammarPractice.ts`,
`textGrammar.ts`, `readingSkills.ts` or `informationTables.ts`. `builders.ts`
rotates explained options deterministically. `StudyText.table` supplies accessible
document tables; supporting quotes may occur in prose or in a table cell.

IDs are persistent progress keys. Never renumber/reuse them or silently change
the intended answer of a practiced item. Give a substantially revised question
a new ID. Explicitly list accepted readings. Hiragana typing normalizes Unicode
width and whitespace but never silently accepts romaji, katakana or omitted long
vowels. IME composition does not submit the form.

Every lesson needs a takeaway, three solving steps, a common trap and at least
one translated example. Every question needs a hint, explanation, translation
and a positive `targetSeconds` practice target. Every choice needs an explanation,
including the correct choice. Wrong options can carry an explicit trap label.
Reading evidence must be an exact quote from a supplied text. All text rendering
uses React text nodes. No authored HTML is injected.

Assembly indices are zero-based: `order` is a permutation of `[0,1,2,3]`;
`starIndex` is a slot, not a fragment number. The full order is graded. List other
natural orders in `acceptedOrders`; do not reject valid time/place adjunct swaps
merely because they differ from the displayed teaching order.

Reading and assembly adapters retain the existing source IDs with a study
prefix. They share content, but this foundation's analytics and scheduler are
separate from the original courses. The UI explicitly describes its sample
coverage, rather than implying that legacy progress has been imported.

## State and persistence

`lib/n2Study.ts` is a framework-free state machine. Drafts, confidence, assistance,
results and review scheduling live in a single versioned snapshot. A question's
stable attempt ID is `session-id:question-id`; repeated checks and timeout/reload
effects cannot grade it twice. The round's question IDs stay fixed while review
queues change. Starting another round cannot replace an unfinished session.
Finishing guided practice early keeps tried answers and leaves unseen questions
unattempted. In timed practice, unanswered questions count as missed.

Successful independent recalls advance only when due: 1 day, then 3 days, then
7 days. The third spaced success counts as retained. Later successes continue
at 7 days. An early repeat keeps the existing due date/stage. A wrong, assisted,
revealed or guessed attempt returns to stage 0 with a 1-day interval. Correct
guesses are recorded as correct answers but do not advance retention. Hints
cannot be unmarked. “Mistakes” and “slow” describe the latest attempt; older
attempts remain in recent history. Answering time excludes the initial mini
lesson, guided pauses and time spent reading an already-graded explanation.

`lib/n2StudyStore.ts` serializes SQLite settings writes under `jlpt-n2-study-v1`.
A synchronous WebView-local recovery journal protects the latest revision while
an async database save is pending. A newer journal is recovered on load; an equal
or older journal never replaces the database. Save errors keep changes in memory
and expose a retry. If both storage paths fail, the UI tells the learner to keep
the window open. Invalid JSON and unsupported snapshots fail visibly and are
never replaced with an empty value. Guided rounds reopen paused; timed rounds
retain their original deadline. The store is shared across the new screens in a
single window. Simultaneous editing from multiple desktop windows is not supported.

Recent detailed history is bounded at 3,000 attempts. Lifetime per-question
counters and review schedules persist. Accuracy, activity and streak calculations
use that recent history. Calendar-day planning uses local dates, not UTC date
strings; review intervals use elapsed milliseconds.

## Verification

```powershell
npm test -- src/lib/n2Study.test.ts src/lib/n2StudyStore.test.ts
npm test -- src/lib/n2Expansion.test.ts src/lib/readingCorrection.test.ts src/lib/readingEvidence.test.ts src/lib/readingTransfer.test.ts
npm run typecheck
npm run dev:mock -- --port 5180
node tools/check_n2_study.mjs --playwright PATH/index.mjs --chromium PATH/msedge.exe --axe PATH/axe.min.js --screenshot PATH.png
node tools/check_jlpt_expansion.mjs --base http://localhost:5180 --playwright PATH/index.mjs --chromium PATH/msedge.exe --axe PATH/axe.min.js
node tools/check_reading_activities.mjs --base http://localhost:5180 --playwright PATH/index.mjs --chromium PATH/msedge.exe --axe PATH/axe.min.js
npm run app:build -- --no-bundle
```

Logic tests cover authored content invariants, scheduler boundaries, assistance,
confidence, idempotent grading, immutable rounds, guided pauses, fixed timed
deadlines, malformed state, selection, local dates, serialized writes, failures
and journal recovery. Browser checks exercise real forms, explanations, notes,
bookmarks, reload/pause recovery, timed expiry, assembly, the four-group home,
direct practice links, collapsed reading filters and the legacy library redirect.
They also check WCAG accessibility and overflow at 390/960/1440 pixels in both themes.


## Review workspace and written practice (checklist 41-70)

`lib/jlptWorkspace.ts` adapts the existing native banks into a searchable catalog
and a deduplicated review inventory. It reads native progress without migrating
or adding its counts to guided history. Legacy mistakes without an interval are
immediately actionable; only guided questions and saved reading words have
spaced due dates. Native mistakes stay unresolved until corrected in that course.

Workspace preferences and personal lists are additive fields in the original
version-1 study snapshot. Missing workspace fields get defaults; invalid ones
fail visibly. Question collections and notes use stable, namespaced native IDs;
guided/native copies of the same exercise share the guided collection ID.

Mocks use the guided choice/assembly bank, retain immutable question IDs and an
absolute deadline, and grade once. Diagnostic and weak-area rounds are practice
estimates. Concept progress uses lifetime review totals, even when the bounded
attempt log has rotated old events out.

`useJlptPractice` journals native drafts synchronously by route and query.
`jlptSessionRecovery` validates field types and rejects altered exercise content.
The original native progress hooks retain separate serialized writes and keys;
their newest snapshots stay in recovery journals until SQLite acknowledges them.
The mock backend acknowledges before its debounced localStorage write, so browser
checks explicitly await the mock disk copy before forced reloads.

Backups use `poodcode-jlpt` version 1. Imports reject unknown settings, future study
versions, invalid course records and tampered exercise snapshots before writing.
The import screen previews replacement, requires the guided round to be finished,
saves the previous state locally, and rolls back failed writes. If rollback also
fails, it reports that failure and leaves the pre-import download available.

```sh
node tools/check_jlpt_workspace.mjs --base http://localhost:5180 --playwright PATH/index.mjs --chromium PATH/chrome.exe --axe PATH/axe.min.js --screenshot screenshots
```

The workspace browser check covers notebook/reason/confidence filters, diagnostic
selection, personal lists, search, mock flags and answer sheet, deadline recovery,
idempotent expiry, native affix/kanji/reading drafts, rejected imports, rollback,
round-trip export/import, course links, axe accessibility and mobile overflow.
