# JLPT implementation checklist

Implement the agreed list in order. Keep the existing section groups and put
specialist drills and filters inside their practice pages. Listening is excluded.
Preserve local changes that predate this work.

- [x] 1. Kana → correct kanji: live Kanji Spelling with explained choices.
- [x] 2. Visually similar kanji drills.
- [x] 3. Same reading, different word: homophone spelling in context.
- [x] 4. Okurigana questions.
- [x] 5. Exam-style reading choices within Kanji Reading.
- [x] 6. Reading error explanations with aligned kana corrections.
- [x] 7. Reading changes in compounds.
- [x] 8. Context-dependent readings.
- [x] 9. More kanji families: 見 and 出; 22 families and 820 words. All 733
  previous word records and answer options are preserved exactly.
- [x] 10. Practise only failed/unfinished skills, or reading/meaning alone.
- [x] 11. Larger context banks.
- [x] 12. Collocation practice.
- [x] 13. Commonly confused words.
- [x] 14. Particle + vocabulary combinations.
- [x] 15. Transitive/intransitive pairs.
- [x] 16. Adverb practice.
- [x] 17. Register and tone.
- [x] 18. Multiple senses in context.
- [x] 19. Repair an incorrect usage.
- [x] 20. Topic-based vocabulary sets.
- [x] 21. A larger grammar bank.
- [x] 22. Searchable grammar reference.
- [x] 23. Formation questions.
- [x] 24. Similar-pattern comparisons.
- [x] 25. Meaning-group practice.
- [x] 26. Minimal-pair examples.
- [x] 27. Sentence correction.
- [x] 28. Register restrictions.
- [x] 29. More realistic passage grammar.
- [x] 30. Broader sentence assembly.
- [x] 31. Find the evidence yourself.
- [x] 32. Main-point questions.
- [x] 33. Reference tracking.
- [x] 34. Argument structure practice.
- [x] 35. Fact versus opinion.
- [x] 36. Answer-strength traps.
- [x] 37. Paragraph summaries.
- [x] 38. Sentence structure breakdowns.
- [x] 39. Visual information retrieval.
- [x] 40. Transfer practice for saved words.
- [x] 41. One JLPT review entry.
- [x] 42. A visible due count.
- [x] 43. A saved-question collection.
- [x] 44. A mistake notebook.
- [x] 45. Review by mistake reason.
- [x] 46. Confident mistakes review.
- [x] 47. Slow-answer review.
- [x] 48. New examples for missed concepts.
- [x] 49. Persistent-trouble sets.
- [x] 50. Concept-level progress.
- [x] 51. Mixed daily practice.
- [x] 52. A short diagnostic.
- [x] 53. Weak-area rounds.
- [x] 54. A configurable N2 written mock.
- [x] 55. Mini mocks.
- [x] 56. Flag for later.
- [x] 57. A mock answer sheet.
- [x] 58. Pacing feedback.
- [x] 59. Fresh-question mocks.
- [x] 60. A useful results breakdown.
- [x] 61. Bring Word Builder closer.
- [x] 62. Expose the full Sentence Order course.
- [x] 63. Expose the affix library.
- [x] 64. Remember practice preferences.
- [x] 65. Small round-size choices.
- [x] 66. One JLPT content search.
- [x] 67. Consistent reading support.
- [x] 68. Consistent session recovery.
- [x] 69. Personal vocabulary lists.
- [x] 70. Progress export/import.

New exercises use the existing guided/timed engine, stable IDs, explanations,
notes and scheduler. Practice options stay collapsed. Structural checks do not
replace native-speaker review of the original Japanese exercise content.

The kanji expansion uses the original pinned CSVs (SHA-256 checked) and JMdict
release. Rebuild with `python tools/build_kanji_words.py --source-dir PATH
--dictionary PATH --preserve-existing` to retain released entries unchanged.
Downloaded sources live outside the repository; dataset licensing is unchanged.

## Validated checkpoint: items 1-40

- 715 tests passed across 65 test files; production build passed.
- Browser checks passed for the original guided flow, all expanded drills, the
  kanji families and skill-only rounds, and the 238-passage reading library.
- New reading activities passed evidence-feedback, independent grading, exact-sense
  word transfer, accessibility and responsive checks.
- New specialist drills, grammar reference, sentence breakdowns and document
  tables stay inside existing practice pages. The four homepage groups remain.
- All 733 existing kanji records and their order were verified unchanged
  against the original JSON entries; 87 entries were appended. Existing study IDs
  and storage keys are retained. Native reader content remains 238 passages and
  388 questions.

| Guided format | Questions |
| --- | ---: |
| Kanji Reading | 64 |
| Kanji Spelling | 36 |
| Vocabulary in Context | 62 |
| Similar Meaning | 20 |
| Correct Usage | 20 |
| Grammar Selection | 50 |
| Sentence Order | 125 |
| Grammar in Passages | 15 |
| Reading Skills (including tables) | 53 |

The complete guided bank has 457 questions including 12 retained foundation
examples outside those main format pools. Word Builder has 820 words in 22
families, and the existing affix course has 300 questions.

## Implementation: items 41-70

- One review entry at `/japanese/n2/review` combines due guided work, native
  course mistakes and saved reading words. Original progress keys remain in use.
  Guided copies of Sentence Order and reading exercises appear once in the queue;
  unresolved native mistakes link back to their original course.
- Saved questions, editable mistake notes, reason filters, confident mistakes,
  slow answers and repeated-trouble sets share this workspace. Confidence and
  timing filters use guided history; old native records contain correctness only.
  New-example rounds use unseen, existing examples of missed guided concepts.
- Daily mixes, a twelve-question diagnostic and weak-concept rounds reuse the
  guided scheduler. Concept progress reports coverage, accuracy and spaced recall.
- Mini mocks and configurable written mocks provide fresh-question selection,
  custom vocabulary/grammar/reading counts, an absolute deadline, persistent
  flags, a jumpable answer sheet, pacing and section results. Mocks use written
  choice/assembly formats and report practice results, not official scaled scores.
  The suggested N2 written mock defaults to 45 questions in 90 minutes and can be
  configured up to 150 questions / 240 minutes. Listening remains excluded.
- Word Builder, the full Sentence Order course and the affix library are linked
  from the existing home/practice pages. The four homepage groups are preserved.
- Practice preferences and small round sizes persist. Unified content search
  covers all six banks plus saved words. Guided and passage practice share
  annotated-reading and translation preferences; timed attempts hide those aids.
  Typed-reading targets stay hidden until checked. Available kana coverage uses
  the existing occurrence annotations, not guessed character readings.
- Native question drafts, frozen rounds, results and deadlines recover after
  navigation/reload. Original course writes have recovery journals. Invalid
  recovery fields are reported and retained; imported exercise snapshots must
  exactly match bundled content.
- Personal vocabulary lists share original schedules and can launch guided,
  Word Builder, affix and saved-word practice. Reading popups and the saved-word
  page can add words directly to lists.
- Scoped JSON export/import covers the six progress stores, notebook, saved
  questions, lists, preferences and recovered sessions. Imports are validated and
  previewed before replacement, preserve unrelated app settings, keep a
  downloadable pre-import backup and attempt rollback on write failure.

Validation commands and coverage are documented in `src/data/n2Study/README.md`.

## Validated checkpoint: items 41-70

- 730 tests passed across 66 test files; production build and typecheck passed.
- Existing guided-flow browser checks passed with the original four home groups.
- Expanded spelling, reading, vocabulary, grammar and reading-skills browser
  checks passed; preference checks now verify remembered filters explicitly.
- Reading activity checks passed for independent grading, evidence feedback,
  exact-sense word transfer, accessibility and responsive layout.
- Workspace browser checks passed for notebook filters, lists, diagnostics,
  mock flags/answer sheet, expiry, recovery without duplicate attempts, native
  affix/kanji/reading drafts, backup validation, failed-import rollback and
  successful import. Axe and mobile-overflow checks passed on these screens.
- Inline-style count remains at the existing baseline of 246. Existing local
  changes and course progress keys were preserved. Exercise banks are unchanged.
