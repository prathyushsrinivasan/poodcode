# N2 study foundation

Open **Languages → JLPT N2 courses** for the shared study space. The former
course menu is available as **Full course library** at `/japanese/n2/library`.
Existing course URLs and progress keys are unchanged. Listening is excluded.

## Learning experience

- **Today:** due reviews, focused practice, a six-section diagnostic sampler,
  daily answering time, streak and an editable exam countdown.
- **Learn & practice:** six sections, searchable mini lessons, examples,
  solving steps and traps. Vocabulary covers word formation, contextual blanks,
  paraphrases and usage. Reading covers short, medium, paired, long arguments
  and information search. The bank is deliberately small.
- **Guided rounds:** a mini lesson before a new format, typed hiragana,
  four-choice questions or keyboard-operable full sentence assembly. Confidence,
  optional hints, reveal, bookmarks, per-option explanations, exact evidence,
  translations and mistake notes. Answers using help are marked assisted.
- **Timed rounds:** a fixed wall-clock deadline, editable answers and question
  navigation. Explanations and hints are unavailable until the round finishes.
  Leaving/reloading does not reset the deadline. Expiry grades saved answers
  and unanswered questions exactly once. These are short practice sets, not
  full-length mock exams or predictors of JLPT scaled scores.
- **Review:** due questions, latest mistakes/assistance, confident misses,
  slow answers and bookmarks; search includes personal mistake notes.
- **Progress:** independent accuracy, sample coverage, spaced retention,
  average answering time, due counts, seven-day activity and recent history.
- **Plan:** exam date, daily minutes and preferred round size, a proportional
  daily routine and four phases for the final 30 days.

## Content authoring

`schema.ts` owns the content contract. `index.ts` contains the small sample
bank and adapters for selected existing reading/assembly examples. Add authored
lessons and questions there or split them into section files as the bank grows.
The engine and UI do not need to change when content is added.

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
npm run typecheck
npm run dev:mock -- --port 5180
node tools/check_n2_study.mjs --playwright PATH/index.mjs --chromium PATH/msedge.exe --axe PATH/axe.min.js --screenshot PATH.png
npm run app:build -- --no-bundle
```

Logic tests cover authored content invariants, scheduler boundaries, assistance,
confidence, idempotent grading, immutable rounds, guided pauses, fixed timed
deadlines, malformed state, selection, local dates, serialized writes, failures
and journal recovery. Browser checks exercise real forms, explanations, notes,
bookmarks, reload/pause recovery, timed expiry, assembly, queues, plan persistence,
WCAG checks and overflow at 390/960/1440 pixels in both themes.
