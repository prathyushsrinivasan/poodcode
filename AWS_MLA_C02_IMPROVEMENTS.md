# AWS MLA-C02 course audit and improvement backlog

Reviewed **2026-10-21**, against source commit **2d76cee**. Scope: the AWS course's published-skill map, all 24 lessons and their questions, learning interface, scheduling, persistence, navigation, integration, tests, and supporting documentation. This is an implementation audit, not an inspection of the learner's private study records or a claim about personal exam readiness.

The course is a working introductory study tool. Its largest remaining gap is **evidence of learning**: mapping a skill to a lesson does not establish that the lesson teaches it deeply, tests it independently, or proves the learner can apply it. Strengthen assessment and progress accuracy before adding more completion indicators.

This document records recommendations. An unchecked item has **not** been implemented by this audit. Keep [the topic roadmap](AWS_MLA_C02_ROADMAP.md) as the exam checklist and this file as the improvement backlog.

## What is implemented

| Area | Verified implementation | Evidence |
| --- | --- | --- |
| Exam map | 4 domains, 12 tasks, 107 unique skill IDs, each assigned to exactly one introductory lesson | `src/data/awsMla/syllabus.ts`; blueprint integrity test |
| Lessons | 24 lessons, two per task; every lesson has a mental model, three rule paragraphs, a trap, recall prompt, design exercise, suggested answer, and references | `src/data/awsMla/lessons.ts` |
| Question bank | 48 fixed original questions: 41 single-answer and 7 select-all; two questions per lesson | Counted from the imported lesson data |
| Sources | 41 distinct documentation URLs attached to lessons; a count of references is not a link-health or factual-accuracy check | Lesson reference arrays |
| Discovery | Sidebar entry, course and lesson commands, breadcrumbs, lesson search, domain and progress filters | `App.tsx`, `Sidebar.tsx`, `CommandPalette.tsx`, `breadcrumb.ts`, `AwsMla.tsx` |
| Daily study | 10/15/25-minute targets; new lessons estimated at 6 minutes, reviews at 3; due reviews precede unseen lessons | `planAwsSession` in `src/lib/awsMla.ts` |
| Sessions | A fixed in-memory queue and next-lesson action prevent the current session from growing indefinitely | `DailySession` in `src/pages/AwsMla.tsx` |
| Practice | Authored option order is shuffled for display; exact select-all grading; one recorded submission per mounted lesson; explanations for every option | `Lesson`, `optionOrder`, `gradeAwsQuestion` |
| Review ladder | Perfect due checks advance through 1, 3, 7, 14, 30 days; misses reset to a 10-minute retry; early passes do not advance the ladder | `recordAwsAttempt` |
| Progress | New, learning, due, and retained states; retained requires three successful spaced checks and a current perfect score | `awsStatus` |
| Local data | Target, per-lesson attempt count/latest score/review state/note, and per-day estimated minutes and distinct lesson IDs are stored through the existing SQLite settings API | `useAwsProgress.ts`; setting key `aws-mla-c02-progress-v1` |
| Recovery | Load errors have Retry; save errors are shown with Retry; writes are serialized within the frontend module | `useAwsProgress.ts` |
| Exam map access | Expandable task list, full roadmap display, Markdown download, official-source links | `CourseHome` |
| Existing quality checks | 12 AWS unit tests cover mapping, grading, interval progression, planning, note preservation, parsing, and local study dates | `src/lib/awsMla.test.ts` |
| Earlier release validation | The preceding implementation/release passed 630 frontend tests, frontend production builds, browser checks, and a Windows build/startup check | Prior work in this session; not all rerun for this documentation audit |

### Domain balance

| Domain | Blueprint weight | Mapped skills | Lessons | Current questions | Share of questions |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1. Data preparation | 28% | 25 | 6 | 12 | 25% |
| 2. Model development | 24% | 27 | 6 | 12 | 25% |
| 3. Deployment and orchestration | 24% | 30 | 6 | 12 | 25% |
| 4. Operations, cost, and security | 24% | 25 | 6 | 12 | 25% |

Equal introductory lesson counts are reasonable. A future mixed assessment should deliberately match the exam weights instead of inheriting this equal question distribution. Do not use the 48-question bank's raw accuracy as an AWS scaled score.

## Findings that should drive the next work

Priorities: **P1** materially affects learning evidence, reliability, or the daily experience; **P2** improves depth, usability, or maintainability; **P3** is useful polish after the fundamentals. No release-blocking P0 failure was established by this review.

| Finding | Evidence and implication | Backlog items |
| --- | --- | --- |
| F01. Skill coverage is assigned, not independently assessed | `AwsQuestion` has no skill IDs. Just two questions set the status of lessons containing 2–7 mapped skills. A correct lesson score cannot identify which of those skills is understood. | Q01–Q03, L01 |
| F02. Repetition can establish familiarity with the same answers | Every review uses the same two stems. All single-answer questions are authored with answer 0; all multi-answer sets begin with the first authored options. Display shuffling works, so this is not an observed answer-position leak. The important weakness is unchanged content. | Q03–Q05 |
| F03. Several distractors test elimination rather than realistic judgment | Examples include model-name length, repository file count, dashboard background, or editor color scheme as alternatives to operational decisions. These are easy warm-ups but weak evidence of exam-level service selection. | Q04, Q06 |
| F04. Help use and independent recall are not distinguished | A learner may reveal notes and the suggested exercise answer before answering. The submitted score advances the same ladder as an unaided check. Recall/design text has no assessment rubric or retained record. | L03–L05, Q02, D02 |
| F05. A due review can disappear from the daily action | Reproduced: choose target 10, fail a new lesson (6 estimated minutes), fail its due retry (3 more), then wait until it is due again. Status is `due`, but `planAwsSession` returns `[]` because only 1 estimated minute remains. Manual lesson browsing still works. | R01, R02 |
| F06. Finishing the target can defer the promised short retry | Planning stops at zero remaining budget. A failed check can become due in 10 minutes while no daily session can start. The learner is told to browse or return, without a direct retry action for the failed lesson. | R01, R05 |
| F07. Save confirmation is optimistic | The note label says “Saved locally” when text equals the in-memory row, before `api.setSetting` resolves. Session completion also says progress is saved. An error is eventually shown, but the success wording is premature. | D01, D03 |
| F08. Important work exists only in component memory | Recall text, design text, quiz selection/feedback, current session queue, and session index are not persisted. Navigating or refreshing can lose this work; completed submissions and saved takeaway notes do persist. | D02, D04 |
| F09. Corrupt-but-plausible progress is accepted | Reproduced: a row with `attempts: 1`, `streak: 999`, `interval: 999`, and a future due time is accepted and labeled retained. A day key `2026-99-99` is also accepted. These are resilience gaps; ordinary course writes do not generate these values. | D05–D07 |
| F10. Runtime curriculum metadata is duplicated | Skill labels live in TypeScript and Markdown; the question counts and timing copy are hard-coded in places; the verification date is global. The parity test catches some drift, but not factual freshness or lesson-level source coverage. | E02, M01–M03 |
| F11. Source availability context is uneven | The production-monitoring lesson already notes Model Monitor's new-customer restriction. The agent lessons use classic-style action groups/aliases without an equivalent distinction, while AWS now documents Agents Classic separately from AgentCore. The Clarify reference also carries an availability restriction. | M01, M02, C14, C18 |
| F12. Regression checks do not continuously cover the shipped feature | AWS is absent from the route arrays in `tools/a11y-check.mjs` and `tools/layout-check.mjs`. The earlier AWS browser harness was a temporary local script, not a committed regression check. | E01, E05–E08 |

## Lesson-by-lesson content improvements

Every existing lesson is listed below. These are proposed additions, not claims that the current lesson is empty or incorrect. Use the skill assignments in `syllabus.ts` to write a detailed taught-and-assessed matrix before expanding content.

| ID | Current lesson / task | Highest-value additions | Evidence of application to add |
| --- | --- | --- | --- |
| C01 | `storage-and-formats` / 1.1 | Service comparison for S3/EBS/EFS/FSx/RDS/DynamoDB; encryption/retention and lifecycle tradeoffs; CSV/JSON/Parquet/ORC examples; snapshots versus change feeds; join multiplicity | Choose storage and format for three workloads, inspect a duplicated join, estimate projected scan bytes |
| C02 | `streams-vectors-features` / 1.1 | Partition/shard capacity, lag/backpressure/replay, ordering/idempotency, Kinesis versus Firehose/Kafka/Flink; vector dimensions/distance/filtering; feature ingestion schemas and event times | Diagnose a hot key from metrics; choose a vector backend under constraints; construct a feature record |
| C03 | `feature-engineering` / 1.2 | Worked scaling/standardization/log/binning examples; point-in-time joins; Glue/EMR/DataBrew/Data Wrangler decision table; event windows and late data | Calculate one transformation, find leakage in a short pipeline, repair a historical feature join |
| C04 | `rag-and-customization-data` / 1.2 | Actual chunk boundaries and overlap examples; text normalization/tokenization/domain augmentation; metadata schemas; embedding compatibility; PII redaction; separate fine-tuning/pretraining/distillation data examples | Compare retrieval on two chunk strategies and validate representative customization JSONL records |
| C05 | `quality-and-labels` / 1.3 | A small DQDL ruleset, schema/range/null/uniqueness checks, imputation examples, annotation agreement/adjudication, semantic prompt-response quality checks | Evaluate a faulty batch, choose quarantine versus remediation, assess ambiguous labels |
| C06 | `bias-and-imbalance` / 1.3 | Confusion matrices, precision/recall/PR-AUC, threshold costs, group-specific rates, sampling/augmentation effects in text and images, limits of fairness metrics | Compute minority recall and subgroup error rates; select an intervention without contaminating holdouts |
| C07 | `choose-a-model` / 2.1 | Concrete baseline algorithms and their assumptions; task/modality/context/license/region constraints; complete specialized-service recognition, including services currently only named in the roadmap | Compare plausible models or APIs on a scored quality/latency/cost/interpretability table |
| C08 | `rag-or-fine-tuning` / 2.1 | A decision tree for prompting, RAG, supervised customization, and combined approaches; semantic versus hybrid search; stale-data and style-failure counterexamples | Defend a choice and explain why each competing approach fails the stated constraints |
| C09 | `training-and-tuning` / 2.2 | Script-mode entry point and job config, input/output channels, objective extraction, log-scale search ranges, epochs/steps/batch calculations, checkpoints and distributed-training overhead | Debug a failed job configuration and choose a bounded tuning strategy using validation results |
| C10 | `fit-prompts-and-retrieval` / 2.2 | Learning curves, convergence diagnostics, regularization/capacity/early-stopping examples, ensemble/routing tradeoffs, forgetting evaluation, a retrieval failure tree | Diagnose plots or traces and propose a controlled next experiment instead of naming a concept |
| C11 | `evaluate-classic-ml` / 2.3 | Numeric precision/recall/F1/MAE/RMSE examples; metric selection under business cost; MLflow run/artifact lineage; feature attributions; divergence/convergence examples | Reproduce a comparison, calculate a metric, distinguish shadow/A-B/offline evidence, inspect a problematic training run |
| C12 | `evaluate-genai` / 2.3 | Tiny BLEU/ROUGE/BERTScore comparison examples, labeled retrieval sets and recall@k, groundedness rubrics, human agreement, judge bias/order effects and calibration | Score a response and retrieved evidence separately, then reconcile human and automated ratings |
| C13 | `inference-and-hosting` / 3.1 | A real-time/async/serverless/batch comparison with current documented constraints; multi-model versus multi-container examples; memory/KV-cache sizing; importing supported external models | Choose among multiple feasible hosting designs using payload size, SLA, cost, and compatibility evidence |
| C14 | `agents-and-rag-serving` / 3.1 | Separate Agents Classic concepts from AgentCore/runtime/tool patterns; actual tool schema/authentication boundaries; MCP/A2A examples where relevant; retrieval filter/rerank configuration; retry semantics | Trace a tool failure, prevent duplicate effects, enforce tenant authorization, select a retrieval configuration |
| C15 | `containers-network-and-scale` / 3.2 | Minimal Dockerfile/health/inference contract; Boto3/CLI deployment flow; IaC dependencies; VPC endpoint/routing diagrams; GPU memory, backlog, warmup, scale-out limits | Read a container/deployment failure and a scaling graph; correct network or IAM configuration |
| C16 | `knowledge-bases-and-agent-state` / 3.2 | Knowledge-base/index schema, document upsert/deletion lifecycle, filter permissions, durable versus session state, concurrency and checkpoint recovery, AgentCore component roles | Recover a partial index refresh and prevent cross-tenant state leakage with an explicit key/access design |
| C17 | `ml-delivery-pipelines` / 3.3 | A versioned pipeline artifact/role diagram, Code* service responsibilities, SageMaker Pipelines versus Step Functions/MWAA, event triggers, approval/quality gates, canary/blue-green rollback examples | Diagnose a failed stage, implement a promotion condition, and rehearse an observable rollback |
| C18 | `genai-delivery-pipelines` / 3.3 | A concrete release manifest; prompt/model/tool/guardrail/index version compatibility; current agent deployment/version concepts; refresh validation and deletion propagation | Reconstruct a known-good release from a manifest and catch a prompt/tool regression before promotion |
| C19 | `production-quality-and-drift` / 4.1 | Worked drift measures, data-quality versus concept/quality drift, ground-truth joins, baselines/thresholds, A/B outcome design, actionable alarms and supported monitoring paths | Interpret a dashboard and delayed labels; decide to investigate, roll back, refresh data, or retrain |
| C20 | `agent-and-fm-observability` / 4.1 | A complete trace with tool/model/retrieval spans, coordination failures, truncated streams, business failures behind HTTP 200, task success and time-to-first-token | Locate the bottleneck/failure from trace evidence and propose bounded recovery |
| C21 | `capacity-and-cost` / 4.2 | More cost-per-result arithmetic; instance/accelerator selection; utilization/headroom; purchasing constraints; Cost Explorer attribution, budget actions and quota limitations | Compare two load tests and cost tables without optimizing away the required SLA |
| C22 | `token-and-agent-economics` / 4.2 | Worked multi-call input/output-token costs, embeddings/reranking/vector storage/refresh costs, caching eligibility, routing/batch/provisioned tradeoffs and quality checks | Calculate total cost per successful task and identify the dominant avoidable work |
| C23 | `iam-network-and-audit` / 4.3 | Actual trust/identity/resource/KMS/endpoint policies, explicit-deny evaluation, subnet/routes/security groups, image scanning findings, CloudTrail/Config/CloudWatch examples | Diagnose a denied encrypted-artifact read and narrow an over-permissive policy without breaking the workflow |
| C24 | `responsible-ai-and-fm-access` / 4.3 | Credential types and lifecycle, applicable guardrail support/limits, prompt-injection threat models, output validation, sensitive-data safeguards and human escalation | Evaluate an attack trace and select enforceable controls at each tool/data boundary |

Do not expand every lesson to the same length. Split overloaded lessons such as C15 into smaller teachable units, while retaining stable progress IDs or providing a migration. Give each subskill an explanation, worked example, and independent check; a mention in a rule paragraph is not sufficient evidence of teaching depth.

## Actionable backlog

### Learning design

| ID | Priority | Improvement | Acceptance condition |
| --- | --- | --- | --- |
| L01 | P1 | Build a skill-to-explanation/example/question/lab matrix; separate introduced, practiced, and independently assessed coverage | All 107 skills have explicit evidence links; uncovered assessment or explanation cells are visible |
| L02 | P1 | Add a short prerequisite path for AWS/IAM/networking, Python/SQL, ML metrics, and embeddings | A learner can diagnose a prerequisite gap and reach the needed mini-lesson without leaving the app |
| L03 | P1 | Record whether notes or suggested answers were used; offer a clearly labeled unaided check | Assisted practice remains useful but cannot silently count as independent assessment |
| L04 | P1 | Give recall and design exercises compact rubrics with key ideas and common omissions | The learner can assess their own answer against criteria rather than one polished example |
| L05 | P2 | Preserve learner explanations and let later reviews ask for recall before showing prior answers | A later check reveals change in understanding without losing the learner's drafts |
| L06 | P2 | Add worked examples followed by faded support and independent variations | Each difficult concept has a demonstrated example and a materially different application |
| L07 | P2 | Add service comparison cards and a searchable acronym/glossary layer | A learner can distinguish close alternatives such as Kinesis/Firehose/Flink or CloudTrail/Config/CloudWatch |
| L08 | P2 | Add local interactive calculations, diagrams, log/policy inspection, and configuration repair | Exercises require manipulating or interpreting evidence, not just choosing a definition |
| L09 | P2 | Add explicit prerequisite metadata rather than relying only on array order | Reordering/splitting content preserves a valid learning path; browsing remains available |
| L10 | P2 | Offer accelerated placement and a focused weak-skill path | Experienced learners can skip demonstrated basics while retaining later independent checkpoints |

### Questions and assessment

| ID | Priority | Improvement | Acceptance condition |
| --- | --- | --- | --- |
| Q01 | P1 | Tag each question with primary and optional secondary skill IDs, difficulty, and decision being tested | Question coverage can be measured per skill without inheriting the parent lesson's whole skill list |
| Q02 | P1 | Store results at question/skill level; maintain separate practice and independent-check evidence | A single incorrect subskill can be scheduled without resetting unrelated demonstrated skills |
| Q03 | P1 | Author independent question families and rotate unseen variants in later checks | Retention requires success on more than the original two stems; exhaustion is explicit |
| Q04 | P1 | Replace absurd distractors with plausible service/configuration tradeoffs and identifiable misconceptions | Every wrong option is a credible choice under some different requirement, and its explanation identifies the failing constraint |
| Q05 | P1 | Reserve a held-out checkpoint bank for transfer testing | Practice cannot reveal the exact questions that determine a readiness checkpoint |
| Q06 | P1 | Add longer operational scenarios with simultaneous cost, latency, security, and maintenance constraints | The learner must choose among feasible alternatives and justify the decisive requirement |
| Q07 | P2 | Broaden select-all practice while keeping exact-match grading and explaining omissions | Practice includes missed-correct-option feedback, not only selected-wrong-option feedback |
| Q08 | P2 | Add confidence and optional answer-time signals to distinguish guesses from fluent decisions | Reports identify confident mistakes and slow correct answers without treating speed as knowledge |
| Q09 | P2 | Add task/domain checkpoints with deliberate sampling and a minimum evidence floor | Coverage and uncertainty are shown alongside accuracy; a small sample cannot imply mastery |
| Q10 | P2 | Add timed mixed practice using a configurable, source-dated exam profile | Standard and beta formats are not conflated; flags, unanswered items, pause rules, and scoring are explicit |
| Q11 | P2 | Add post-session misconception review and spaced retries using a fresh question | A learner sees why they failed and later demonstrates the repair independently |
| Q12 | P2 | Review item quality with an editorial checklist and, if locally available, aggregate personal error patterns | Ambiguous answers, lexical clues, duplicates, and implausible distractors are caught without collecting telemetry |

Suggested initial content target: at least three independent applied checks per skill, plus held-out task checkpoints. This is an authoring target, not an AWS requirement or a guaranteed passing threshold. Prefer fewer carefully reviewed questions to a large templated bank.

### Daily planning and spaced review

| ID | Priority | Improvement | Acceptance condition |
| --- | --- | --- | --- |
| R01 | P1 | Separate new-learning budget from essential short retries; add a direct “Retry this lesson” action | The F05 scenario always offers an actionable retry without requiring the learner to hunt through the library |
| R02 | P1 | Handle unused budget explicitly with a short recall task, a smaller lesson, or a clear completion choice | A 10-minute target after one 6-minute lesson does not leave an unexplained dead end |
| R03 | P1 | Protect a small amount of new learning from an accumulating review backlog | A simulated multi-week plan introduces later domains while still making bounded progress on due work |
| R04 | P1 | Track independent question/skill evidence before advancing retention status | Repeated familiarity with two questions is not sufficient to mark every lesson skill retained |
| R05 | P2 | Show the next due time and optional same-day retry plan on completion | A learner who misses a question knows when and where to return, even after the daily target |
| R06 | P2 | Distinguish estimated effort from actual active study time; do not award time for rapid resubmissions | A seconds-long repeat does not appear as three measured minutes; estimates remain honestly labeled |
| R07 | P2 | Exclude early optional drills from daily target accounting, or give the learner a clear policy choice | Early practice cannot accidentally exhaust the whole day's guided plan |
| R08 | P2 | Use a documented, explainable priority formula with genuine domain interleaving | Show why a lesson is selected; tests cover domain coverage rather than claiming mixing from sort order alone |
| R09 | P2 | Distinguish retention strength from “due” status | A previously well-retained lesson can be due without losing its separate history of demonstrated strength |
| R10 | P2 | Support exam-date planning and a sustainable catch-up schedule | The plan estimates remaining learning/reviews without promising an unsupported readiness date |
| R11 | P2 | Persist/resume a finite session snapshot; revalidate due items on resume | Closing mid-session resumes the appropriate next step without silently expanding the queue |
| R12 | P2 | Define timestamp/calendar behavior across midnight, DST, timezone changes, and system sleep | Due timestamps and local study-day/streak rules remain consistent under tested clock changes |

Current scheduling uses exact elapsed 24-hour days for intervals and local calendar dates for activity. That is a valid starting policy, but it should be documented and tested rather than described as an adaptive memory model.

### Progress, notes, and data reliability

| ID | Priority | Improvement | Acceptance condition |
| --- | --- | --- | --- |
| D01 | P1 | Add explicit saving/saved/failed state and only acknowledge completed writes | “Saved locally” appears after the relevant API write resolves, including at session completion |
| D02 | P1 | Save recall/design drafts and in-progress quiz state separately from graded attempts | Navigate away and restart the app without losing unsubmitted work or granting extra progress |
| D03 | P1 | Flush pending writes on navigation/exit or provide a reliable unsaved-work notice | A delayed or failed write is not hidden by leaving the course |
| D04 | P1 | Persist the session queue/index and submission identity; make attempt recording idempotent across resume | Reloading feedback or double submission cannot record an unintended second graded attempt |
| D05 | P2 | Validate calendar dates, allowed intervals, score states, and consistency between attempts/streak/last score | The F09 malformed fixture is rejected or normalized with a visible recovery explanation |
| D06 | P2 | Preserve recoverable raw data when parsing fails; distinguish invalid data from “new learner” | A corrupt or newer-version snapshot does not silently become a fresh snapshot that can overwrite it |
| D07 | P2 | Add explicit progress migrations and content-version policies | Splitting lessons, replacing questions, changing the syllabus, or restoring old data preserves legitimate history |
| D08 | P2 | Retain an append-only or bounded attempt history including missed question IDs, help use, and versions | Trends and weak-skill analysis can be derived without guessing from only `lastScore` |
| D09 | P2 | Test whole-database backup/restore with AWS settings and add an optional course-only export/import | Restored notes, targets, histories, and due dates match; no cloud account is required |
| D10 | P2 | Handle multiple windows or overlapping hook instances with revisions or atomic updates | A stale whole-progress snapshot cannot overwrite newer study records or notes |
| D11 | P2 | Debounce draft writes, skip unchanged snapshots, and bound long-term history growth | Typing remains responsive and write volume/history size remain predictable |
| D12 | P3 | Add search/export for takeaways and a clear, scoped reset flow with recovery | Learners can reuse notes or reset the course without accidentally resetting other tracks |

Whole-database backup already exists in Settings and should capture this settings-backed progress. The gap is AWS-specific verification and a convenient course-level export, not the absence of any backup capability.

### Interface and accessibility

| ID | Priority | Improvement | Acceptance condition |
| --- | --- | --- | --- |
| U01 | P1 | Move keyboard focus to the new session heading after Continue and announce session position/result | Screen-reader and keyboard users follow the next question without losing context after the old button unmounts |
| U02 | P2 | Show a compact set of skill objectives before the lesson instead of one long subtitle | Overloaded lessons remain scannable at the supported minimum window width and enlarged text |
| U03 | P2 | Keep view/search/domain/progress filters in the URL or persisted navigation state | Back from a lesson returns to the same filtered library or exam-map position |
| U04 | P2 | Add a domain/task learning map with explicit prerequisites and next useful action | The learner can understand the path and jump to a weak skill without memorizing skill IDs |
| U05 | P2 | Offer a focused review layout, collapsible repeated scaffolding, and a useful “already know this” path | A 3-minute review does not require repeatedly traversing the full introductory page |
| U06 | P2 | Search glossary terms, service aliases, references, and the actual course service inventory | Searches for relevant services only named in the roadmap still lead to instruction or clearly labeled coverage gaps |
| U07 | P2 | Add consistent in-page navigation and progress through recall/application/checks | Learners can recover their place in long content while retaining access to explanations |
| U08 | P2 | Verify feedback semantics for disabled fieldsets, disclosures, focus, and select-all controls | Assistive technology can read every explanation and identify selected/correct/missed options |
| U09 | P2 | Explain empty states separately: all mastered, no due work, insufficient remaining budget, filtered-out results, unavailable data | Each state offers the action appropriate to its cause |
| U10 | P3 | Add printable/offline reference sheets and an optional compact review view | Key service distinctions and formulas are available without repeatedly opening external links |

### Engineering and verification

| ID | Priority | Improvement | Acceptance condition |
| --- | --- | --- | --- |
| E01 | P1 | Commit a reproducible AWS browser regression harness using the existing browser-tool conventions | A fresh developer environment can run the course checks without a private temporary script |
| E02 | P2 | Generate the Markdown skill checklist and derived counts from one structured syllabus | Topic labels, counts, weights, and app/download content cannot drift independently |
| E03 | P2 | Split the monolithic page into course home, map, lesson, questions, notes, and session components; centralize derived indexes | Components have clear responsibilities without changing saved IDs or study behavior |
| E04 | P2 | Split lesson authoring by domain/task and validate it with a reusable schema/linter | Invalid mappings, repeated IDs/options, empty explanations, bad answer sets, and missing source metadata fail authoring checks |
| E05 | P1 | Add AWS home/daily/lesson and stateful variants to layout and accessibility coverage | Both themes, high contrast, keyboard use, 960/1180/1440 widths, zoom, and expanded/graded states are exercised |
| E06 | P1 | Add deterministic regression cases for the due-review/budget and malformed-state findings | Tests fail against the identified behavior before the corresponding fix, then pass with a deliberate new policy |
| E07 | P1 | Test the progress hook under delayed/failing writes, rapid edits, unmount/remount, retry, and React Strict Mode | The latest intended state survives and success/error indicators reflect actual persistence |
| E08 | P2 | Test midnight/timezone/sleep behavior, all due/no unseen states, partial session resume, and stale window updates | Planning and recovery policies hold under realistic boundary cases |
| E09 | P2 | Add question-specific factual/editorial review in addition to structural tests | Tests proving answer indices are valid do not stand in for verifying the right answer and distractor explanations |
| E10 | P2 | Verify external-link behavior and roadmap download in the actual Windows WebView2/Tauri app | The data-URL download and external links work under the production CSP and desktop navigation behavior; browser-only success is not enough |

Do not add tests that merely restate UI text or duplicate implementation arithmetic. Test the learner-visible policy and data-loss boundaries. Retain the existing structural tests while broadening their evidence.

### Integration and practical work

| ID | Priority | Improvement | Acceptance condition |
| --- | --- | --- | --- |
| I01 | P2 | Include AWS due work and resume actions on the app-wide Today page and sidebar badges | AWS reviews are discoverable without opening the course; counts use the same scheduling policy |
| I02 | P2 | Include AWS coverage and review health in Insights | Introduced, independently assessed, retained, and due are clearly distinguished |
| I03 | P2 | Make command-palette search include service/skill labels and daily/weak-skill actions | A skill-name query can find its lesson, not just an ID or title match |
| I04 | P1 | Add deterministic offline mini-labs using small data, policies, logs, traces, and deployment manifests | Each task includes a practical exercise with an observable result and an independent check |
| I05 | P2 | Add optional AWS hands-on guides with prerequisites, expected evidence, cost boundaries, and cleanup | No resource is provisioned automatically; completing a lab requires evidence beyond checking a box |
| I06 | P2 | Add a small end-to-end capstone spanning data, training/RAG, deployment, monitoring, security, and rollback | A learner diagnoses and improves a connected system instead of passing only isolated concept checks |

### Source maintenance and documentation

| ID | Priority | Improvement | Acceptance condition |
| --- | --- | --- | --- |
| M01 | P1 | Add per-lesson/source verification dates, supported-access notes, and review ownership | Changes such as Agents Classic/AgentCore and Model Monitor/Clarify access restrictions are explained where relevant |
| M02 | P1 | Distinguish exam-scope recognition from currently available hands-on paths | A service can remain useful exam vocabulary without directing a new customer to an unavailable setup |
| M03 | P2 | Validate meaningful source content and claim support, not merely an `https://docs.aws.amazon.com/` prefix or HTTP success | Redirects to generic pages, removed anchors, and unrelated content are flagged for review |
| M04 | P2 | Review beta/standard exam metadata separately from the lesson content | Exam profiles include code, format, date, and source; no silent switch to another exam version |
| M05 | P2 | Keep this audit and the topic roadmap distinct; mark implemented backlog IDs with evidence | The audit remains actionable and the roadmap remains the learner's topic map |
| M06 | P3 | Establish documentation retirement rules: delete completed one-time prompts, retain live references and authoring contracts | Cleanup does not break imports, tests, guide links, or the next contributor's maintenance information |

## Recommended implementation sequence

1. **Trust and recovery:** D01–D04, R01–R02, E01/E05–E07. Deliver honest save state, surviving drafts/sessions, an actionable retry, and regression coverage.
2. **Assess what was learned:** L01/L03/L04, Q01–Q06, R04, D08. Deliver a skill-level evidence model and a varied applied question bank before changing mastery claims.
3. **Teach the weak spots:** L02/L06–L08, C01–C24, I04. Expand examples and offline practical work using the coverage matrix; prioritize gaps with no direct assessment.
4. **Make daily study sustainable:** R03/R05–R12, U01–U09, I01–I03. Add sensible catch-up, navigation continuity, and app-wide discovery.
5. **Prepare for transfer and the exam:** Q09–Q11, I05–I06, M01–M04. Add held-out checkpoints, source-dated timed practice, and evidence-based practical milestones.
6. **Maintain the course:** D05–D12, E02–E04/E08–E10, M05–M06. Introduce migration and authoring contracts before the bank grows substantially.

These are delivery groups, not reasons to postpone all validation until the end. Each change needs its corresponding regression check and must preserve existing progress or supply a migration.

## What a stronger course should prove

- Every published skill has explicit teaching and independent applied assessment, with gaps visible.
- The learner can transfer a concept to a different scenario, configuration, dataset, or trace.
- Retention reflects fresh independent evidence, while assisted practice is tracked separately.
- Daily work remains short and actionable even with missed reviews and failed checks.
- Drafts, notes, graded attempts, and session position survive the stated save/restart behavior.
- Readiness reports show coverage and evidence limitations, and do not promise a passing score.
- Source and service-availability changes can be reviewed without renumbering stable progress IDs.

## Validation performed for this audit

- Read the course source, all lesson structures/content, scheduler, progress hook, test coverage, styles, navigation, and integration points.
- Counted the imported data: 107 mapped skills, 24 lessons, 48 questions (41 single-answer / 7 multi-answer), 41 distinct lesson reference URLs.
- Reran `npm test -- src/lib/awsMla.test.ts`: **12 tests passed**.
- Executed deterministic temporary fixtures for F05 and F09: a due lesson with an empty budget-limited queue, accepted invalid calendar data, and an inconsistent row classified as retained.
- Inspected save/draft/session behavior in code. Delayed-write, crash, multi-window, screen-reader, and new bank-quality proposals are **not** claimed as end-to-end reproduced defects; they need the checks described above.
- Rechecked AWS's current blueprint weighting and the availability notices cited below. Did not revalidate every claim behind all 41 lesson URLs, run paid AWS labs, or repeat the earlier full release suite for this documentation-only change.

## Markdown cleanup decisions

Reviewed all 16 existing repository Markdown files outside dependencies/build output. File completion alone is not a reason to remove a document that still provides the app's data, an authoring contract, or maintenance rationale.

| File or group | Decision | Reason |
| --- | --- | --- |
| `prompts/jlpt-chuubun.md` | **Delete** | A one-time instruction to reach 100 medium passages. The shipped corpus, tests, authoring guide, and commit `9890921` establish that the requested expansion is complete. Ongoing authoring requirements already live in `src/data/dokkai/README.md`. |
| `AWS_MLA_C02_ROADMAP.md` | **Keep** | Imported as raw content by `AwsMla.tsx`, checked by `awsMla.test.ts`, displayed/downloaded in the app, and still the complete topic checklist. |
| `README.md`, `src/data/dokkai/README.md` | **Keep** | Current setup, architecture, user guidance, and live reading authoring rules. Update the stale prompt link and reading counts in the root README. |
| `NEW_DSA.md` | **Keep** | The 16-section template and remaining topic work still guide active implementation. |
| `TS_MASTERY_ROADMAP.md` | **Keep** | Contains a handoff and explicitly remaining/deferred work, alongside maintenance context. |
| `JAVA_ROADMAP.md`, `TS_ROADMAP.md` | **Keep as reference** | Finished course plans also preserve scope boundaries, prerequisite sequencing, judging/verification rules, and extension decisions. Some historical status wording needs eventual consolidation; they are not disposable one-time prompts. |
| `PROJECTS_ROADMAP.md`, `CALC_ROADMAP.md` | **Keep as reference** | Record project contracts, harness behavior, language/error-format decisions, and maintenance rationale still linked by README and authoring code. |
| `DSA_ROADMAP.md` | **Keep as reference** | Current topic coverage and cross-links to stage authoring remain useful even though the original coverage expansion shipped. |
| `ORDER_SEARCH_ROADMAP.md`, `NUMBERS_BITS_GRIDS_ROADMAP.md`, `TREES_GRAPHS_ROADMAP.md` | **Keep as reference** | Completed expansion records retain concrete depth/verification requirements and stage-specific decisions used in authoring and documentation. |
| `JAPANESE_ROADMAP.md` | **Keep as reference** | Explicitly retained for vocabulary canon, furigana rules, and review-ID migration rationale; those are ongoing maintenance concerns. |
| `UI_ROADMAP.md` | **Keep as reference** | Completed overhaul also records the design system, layout/accessibility contracts, test tooling, and deliberate native-title-bar decision; source comments and tools still reference these decisions. |

The removed prompt remains recoverable from Git history. No learner data, course source, or runtime-imported Markdown is deleted by this cleanup.

## Official references

- [MLA-C02 exam guide](https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/) — published task/skill scope and domain weights; the guide is non-exhaustive.
- [Certification and exam format](https://aws.amazon.com/certification/certified-machine-learning-engineer-associate/) — recheck beta/standard details before building timed profiles or booking.
- [Bedrock agent deployment and Agents Classic availability](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-deploy.html) — current classic-agent access notice and deployment concepts.
- [Model Monitor](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html) — current access notice and monitoring capabilities.
- [Clarify data-bias documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-detect-data-bias.html) — current access notice and bias concepts.
- [Clarify availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-availability-change.html) — evaluate supported alternatives before proposing a hands-on path for new customers.
