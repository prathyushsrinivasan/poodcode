# AWS SAA-C03 quizzes

100 original scenario questions, organized into ten topics with ten items each.
There are 85 single-answer items (four options) and 15 multiple-answer items
(five options). Every option includes reasoning, and every question includes
a takeaway. The questions practice decisions within the four SAA-C03 domains;
the bank is organized by topic rather than weighted as a full mock exam.
These are original practice items, not reproduced AWS exam questions.

Open **Courses → AWS SAA quizzes** (`/aws-saa`). The section offers topic sets,
ten-question mixed practice, latest-mistake review, and five daily questions.
Multiple-answer questions require the exact correct set; there is no partial
credit. Displayed options are shuffled independently of their authored indices.

Daily sets prioritize prior mistakes, then unseen questions, with five distinct
topics. The IDs are fixed and saved when that day's session opens. Submitted
daily answers survive navigation/restart, and each question counts once for
that day. Separate practice can correct a mistake without changing the earlier
daily score. A new set becomes available on the next local calendar date;
the page checks for rollover every 15 seconds. Daily streaks count completed
sets, regardless of score. Ordinary practice saves submitted results but starts
a new session after navigation. Unsubmitted selections are not persisted.

Progress uses the existing SQLite settings API with its own versioned key,
`aws-saa-c03-quizzes-v1`. There are no AWS credentials, external calls or
subscription requirements to practice. Documentation links require internet.
Load/save failures show retry controls. Progress parsing validates known IDs,
counts and answer selections and recomputes stored daily correctness.

Content was reviewed on 2026-10-21 against the
[official exam guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html)
and linked AWS documentation. Important distinctions include the single-standby
RDS deployment versus readable Multi-AZ DB clusters, zonal NAT design versus
new regional NAT capabilities, current DynamoDB global-table consistency modes,
capacity assurance versus pricing commitments, and at-least-once message
processing versus application-level idempotency. Practice accuracy does not
predict an AWS scaled exam score.

Authoring: append entries within a topic and preserve existing question IDs and
option indices; saved answers use them. Keep four options for a single-answer
item and five or more for a multiple-answer item, with clear scenario constraints,
one best answer set and explanations for every distractor. If changing an
existing answer materially, use a new ID or migrate the saved progress.

Validation:

- `npm test -- src/lib/awsSaa.test.ts`: bank integrity, exact-set grading,
  planning, persistence, daily-score isolation and calendar streaks.
- `npm run build`: TypeScript and production bundling.
- Run `npm run dev:mock -- --host 127.0.0.1 --port 5182`, then
  `node tools/check_aws_saa.mjs --playwright PATH_TO_INDEX_MJS --chromium PATH_TO_CHROME`
  to exercise all 100 answers, feedback, daily resume, mistake correction,
  save retry and responsive layouts using an existing browser installation.
