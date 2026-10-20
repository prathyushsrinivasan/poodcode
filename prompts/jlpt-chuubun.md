# Expand JLPT N2 中文 reading practice

Expand the existing **JLPT N2 → 読解 → 中文** section to **at least 100 distinct,
original passages in total**, using the current reading system in
`src/data/dokkai`, `src/pages/JlptReading.tsx`, and `src/pages/reading`.
Implement the work; do not stop at suggestions or a plan.

Before editing, inspect the current content schema, reading renderer, progress
storage, tests, and `src/data/dokkai/README.md`. Reuse the existing study and
timed modes, filters, bookmarks, mistake review, translations, vocabulary
popups, furigana, and saved-word review.

Requirements:

1. Keep the five existing medium passages and all existing passage/question IDs
   stable. Add at least 95 new passages with explicit IDs. Organize new content
   into manageable files and ten-passage sets without creating another reader.
2. Target **450–550 Japanese characters per new passage**, excluding whitespace
   and annotation markup. Write natural, coherent N2 material with multiple
   paragraphs, varied structures, and meaningful examples or contrasts.
3. Cover varied topics: work, education, technology, daily life, relationships,
   culture, society, and the environment. Vary challenge within N2. Avoid
   near-duplicate templates, superficial name changes, and copied exam texts.
4. Give each new passage **2–3 Japanese questions with four choices each**.
   Include main points, reasons, intentions, references, inference, and links
   between paragraphs. Every question must have exactly one defensible answer
   and plausible distractors, without requiring outside knowledge.
5. Provide exact supporting quotes, highlightable in the passage, and clear
   English explanations for the correct answer and every wrong choice. Explain
   traps such as reversed causation, overgeneralization, and confusing an
   example with the author's main claim.
6. Make difficult words and grammar expressions clickable throughout passages,
   questions, and choices, with accurate kana and contextual meanings. Use
   occurrence-specific annotations for ambiguous readings and meanings, and
   include dictionary forms for inflected words where appropriate.
7. Include a complete English translation for each passage, revealed during
   review. Keep the existing separation between independent, assisted, and timed
   results. Ensure expanded content appears in navigation and practice sets.
8. Update corpus checks and documentation for the new counts. Validate lengths,
   unique IDs and texts, four choices, evidence quotes, translations, and
   vocabulary annotations. Run relevant tests, the production build, and browser
   checks of 中文 practice, saving/reloading, timed expiry, and responsive layout.

Complete the full content library and fix validation failures. Then rebuild the
Windows executable and installers, commit and push only the relevant changes to
the existing GitHub branch, preserving unrelated local edits. Report the passage
and question counts, validation results, executable paths, and pushed commit.
