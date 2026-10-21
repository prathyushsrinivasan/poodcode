# AWS MLA-C02 course content

Module 1 (Data Preparation) contains six full lessons, 24 taught sections and
36 original choice questions. Modules 2–4 retain the earlier introductory
outlines and their 36 questions. The app labels this difference explicitly.

The lesson sequence follows a retailer's data through storage and extraction,
streaming ingestion, reusable features, document preparation, quality gates and
bias/imbalance evaluation. Each full lesson includes objectives, worked examples,
comparison tables or calculations, and external resources with a purpose and
historical-demo notes where applicable. All checks use authored answer indices;
there is no written-answer assessment or AI grading.

`module1/*.md` contains the teaching. `module1.ts` assembles its sections,
resources and questions. `lessons.ts` merges that content into the stable lesson
IDs, preserving existing routes and saved history/notes. Previously saved
takeaways remain readable. The older recall/exercise fields are retained in
outline data for compatibility; the interface presents the suggested approach
as a worked example and renders no text-entry exercise.

Every Module 1 question identifies the section to revisit and the skill IDs it
assesses. Together they address the 25 assigned Domain 1 skills. This mapping is
an editorial coverage check, not a claim of certification readiness or independent
mastery. Reviews repeat the same six items and only shuffle display order. Old
progress still describes historical practice, including the earlier question bank.

Full lessons are estimated at 25 minutes including checks; reviews at six.
External resources take additional time. Daily targets are flexible: if the next
lesson is longer than the remaining target, a fresh session offers that one
lesson rather than skipping ahead to shorter outlines. Estimates are recorded
on submission, not measured active reading time. Reading in smaller sittings is
supported, but the current lesson view and unsubmitted selections do not survive
navigation or app restart. You can retry checks directly even after meeting the
daily target; early repeats do not advance the review interval.

Sources were reviewed on 2026-10-21. Current documentation takes precedence over
historical video interfaces and quotas. Clarify's new-customer restriction is
called out in the bias lesson and resource notes. The content and assessment
work offline; external sources require internet. Reading the module requires no
AWS account or paid deployment.

Verification:

- `npm test` checks grading, scheduling, persistence parsing, blueprint parity,
  section references and assessed skill coverage.
- `npm run build` checks types and production bundling.
- Run `npm run dev:mock -- --host 127.0.0.1 --port 5180`, then
  `node tools/check_aws_mla.mjs --playwright PATH_TO_PLAYWRIGHT_INDEX_MJS --chromium PATH_TO_CHROMIUM`
  to check all 24 reading routes, all 36 Module 1 answers, feedback navigation,
  retry behavior, saved progress and responsive layout.
