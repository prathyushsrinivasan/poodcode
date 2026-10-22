# FastAPI course audit and expansion plan

Reviewed 22 October 2026. Scope: all 12 modules/24 lessons, project briefs,
36 review questions, reference code, the lesson/reference relationship and
verification tooling. External comparisons use the providers' public curricula;
this is not a review of paid lesson content or a claim that every course covers
every topic below.

## Verdict

The course has a coherent **beginner-to-intermediate core** for designing,
persisting, securing, testing and deploying a small API. It does **not yet provide
a complete zero-programming-to-advanced pathway**. A single private-task CRUD app
and a deployed service are useful outcomes, but do not establish competence in
async persistence, distributed jobs, shared state, complex data models or
production performance analysis.

The original entry point assumed basic programming and compressed unfamiliar
Python and HTTP ideas. The advanced end contained several assignments and
one-paragraph mentions without guided implementations. Topic names and a large
final checklist cannot replace runnable examples, failure drills and independent
practice.

The core is now labeled beginner to intermediate, with 40–50 estimated hours.
This is an author estimate, not a measured completion time. Students who have
never programmed need a beginner Python course before this core; programmers
new to Python can use the readiness bridge and repeat its exercises.

## Comparison with published teaching paths

| Primary source | Relevant curriculum evidence | Implication for this course |
|---|---|---|
| [freeCodeCamp: Creating APIs with Python](https://www.freecodecamp.org/news/creating-apis-with-python-free-19-hour-course/) | Separates SQL fundamentals, raw SQL, ORM use, relationships and joins; also includes Git setup and VM deployment | Teach rows/SQL before ORM syntax; increase relationship-query depth. Its older deployment/library commands should not be copied without checking current docs. |
| [Talk Python: Modern APIs](https://training.talkpython.fm/courses/modern-fastapi-apis) | Builds a real external-data API, explores Python features, error handling, caching and deployment | Add a second domain and a cache/failure exercise beyond private-task CRUD. |
| [Talk Python: Full Web Apps](https://training.talkpython.fm/courses/full-html-web-applications-with-fastapi) | Includes an async SQLAlchemy chapter, HTML templates and static content | Async persistence is a substantive gap. HTML rendering is an optional specialization for an API-focused course. |
| [TestDriven.io: TDD with FastAPI and Docker](https://testdriven.io/courses/tdd-fastapi/) | Async PostgreSQL, TDD, coverage, linting, mocking and CI/CD; explicitly expects prior web-development experience | Grow toward those practices after beginner foundations rather than importing its starting difficulty. |
| [TestDriven.io: Celery and FastAPI](https://testdriven.io/courses/fastapi-celery/) | Separate worker processes, retries, scheduling, routing, transaction integration and monitoring | BackgroundTasks plus a queue sketch is an introduction, not durable-job training. |
| [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) and [additional features](https://fastapi.tiangolo.com/advanced/) | Nested models, headers/cookies, forms/files, streaming, WebSockets, async tests and more | Several framework features lack runnable lessons. The documentation also notes that its “advanced” section is not uniformly advanced; advanced competence should be assessed through engineering tasks. |

## Module-by-module ramp review

| Module | Finding | Action/status |
|---|---|---|
| 1: first API | Annotations/classes appeared before a readiness check; HTTP anatomy was assumed; tests directory was missing from setup | Added Python exercises, decorator/resource-lifetime explanations, HTTP/JSON primer, explicit entry/exit checks and tests directory creation. |
| 2: contracts/CRUD | Many ideas arrived together; test reset behavior was assigned without a fixture example; route ordering was missing | Added parameter-source/route-order explanations and a runnable CRUD fixture/test. The stage-specific reference no longer imports final auth/DB modules. |
| 3: architecture/DI | Refactor moved storage without explaining the test update; project requested an injected store that the lesson did not build | Added fixture transition; aligned the build to the dependency override actually demonstrated. |
| 4: SQLite/ORM | ORM syntax preceded SQL; owner seed and test isolation were left implicit; direct handler calls could break after adding injected arguments | Added a runnable SQL bridge, repeatable local seed, early DB fixture and explicit ordinary-helper/session-passing instructions. Joins and multi-table workflows still need expansion. |
| 5: PostgreSQL/Alembic | Docker terminology and Compose file placement were assumed; env.py setup was incomplete for a beginner | Added image/container/volume/network basics, readiness/psql commands and complete env.py. Explained fresh DB migration generation and reseeding after switching databases. |
| 6: passwords | Login example called create_token before module 7 taught it; /auth/me also appeared in the checklist before implementation | Replaced the teaching step with a runnable /auth/login-check returning public user fields; aligned the checklist. |
| 7: JWT/ownership | Good core authorization model, but transition from credential checking and earlier anonymous tests needed explicit edits | Added Token schema, exact route transition and test-update instructions. Role checks remain an optional sketch. |
| 8: testing | Good negative/security testing; main testing chapter came late | Initial tests/fixtures now appear alongside the earlier features. This chapter deepens them. Async DB tests, coverage/lint gates and wider failure testing remain gaps. |
| 9: concurrency | Correct sync/async distinction and outbound-client/lifespan example | Intermediate introduction. No completed AsyncSession conversion or durable worker implementation; uploads/WebSockets remain stretch suggestions. |
| 10: operations | CORS, request IDs and health probes have worked examples; distributed rate limiting is an unscaffolded requirement | Shared limiter remains unimplemented. Logs/probes do not provide a metrics/tracing/load-test module. |
| 11: packaging/CI | Useful runnable packaging and a copyable CI template | Not a full scale/operations module. No measured load experiment, transitive lock exercise or deployment automation implementation. |
| 12: deployment/final | Strong core acceptance checklist and useful recovery prompts | Tests core delivery. Rollback/backup remain practice runbooks; the final project does not exercise advanced feature integration. |

All modules now display an entry check and a link back to the prior module.
Module numbers and completion keys are unchanged, so existing saved progress is
preserved. Completion remains self-reported after the project checklist.

## Coverage: implemented versus introduced versus missing

“Core implementation” means working reference code and relevant tests. “Guided”
means lesson code/lab outside the final reference. “Introduced” means prose,
snippet or stretch assignment; it must not be counted as a completed module.

| Topic | Current coverage | Remaining work |
|---|---|---|
| CRUD, validation, routers, dependencies, settings | Core implementation; early guided checkpoints | Add nested models, enums/UUIDs, more input sources and a domain-error contract. |
| SQL basics, SQLite, transactions | Guided SQL bridge plus core ORM implementation | More independent SQL drills and a multi-write workflow. |
| PostgreSQL and Alembic | Core configuration, migration, smoke script and CI template | Install the template in the learning repository and execute it; broader PostgreSQL integration tests still needed. |
| Relationships, joins, aggregation, N+1 | One user/task relationship; N+1 discussed | Many-to-many schema, joins, aggregates, eager loading and query-count verification. |
| Passwords/JWT/object ownership | Core implementation with failure tests | Add a separate advanced identity/policy path; the current design intentionally has no refresh-token/account-recovery system. |
| Roles/scopes/OIDC/cookie sessions | Optional role snippet and conceptual boundaries | Worked permissions and external identity integration; token lifecycle/revocation and CSRF where applicable. |
| Async external I/O/lifespan | Guided example | Complete the mock-transport exercise and test shutdown/failure behavior. |
| Async SQLAlchemy and async tests | Mentioned only | Async engine/driver/session, cancellation and transaction cleanup, lifespan-aware async tests. |
| Multipart uploads/downloads/streaming | Upload suggested as stretch; no implementation | Bounded file processing, safe metadata, authorization and durable object storage; stream cleanup tests. |
| WebSockets/SSE | WebSocket suggested as stretch; no implementation | Authenticated channels, disconnect cleanup, event delivery and multi-instance design. |
| Durable jobs | BackgroundTasks example and durable-job sketch | Worker/broker setup, retries, idempotency, outbox/transaction boundary, job ownership and monitoring. |
| Caching | No implementation | Cache keys, TTL, invalidation, tenant isolation and outage behavior. |
| Distributed rate limiting | Described and assigned; no implementation | Guided shared counter/atomic operation or a documented provider integration with tests. |
| Observability/performance | Core timing logs and live/ready probes | Metrics, traces, pool budgets, load testing and measured bottleneck analysis. |
| API evolution/webhooks | Expand/backfill/contract discussed; no version/webhook implementation | Compatibility tests, versioning policy and signed/idempotent webhook processing. |
| CI/code quality | Tests, migration/drift checks, smoke configuration | Coverage reports and linting; image/release automation with evidence. |
| Cloud delivery | Guided Render configuration, Docker artifact and smoke script | Learner execution/redeploy verification; no automatic claim of a live deployment. |

## Proposed advanced extension: not yet implemented

Keep modules 1–12 as a usable core. Build these additional modules in dependency
order; do not mark them authored or include them in completion until they have
lessons, runnable references, negative tests and practical review criteria.

| Proposed module | Prerequisites | Build and exit evidence |
|---|---|---|
| 13: richer domain and API contracts | 2, 5, 7, 8 | Projects/memberships/tasks, many-to-many constraints, joins/aggregates, nested models, error handlers, stable pagination and an API compatibility test. Prove outsider access is denied and query count stays bounded. |
| 14: async persistence and async tests | 9, 13 | Convert a vertical slice to AsyncSession with an async driver. Test concurrent independent sessions, rollback/cancellation cleanup and lifespan teardown; retain sync code where justified. |
| 15: uploads, downloads and streaming | 7, 9, 13 | Size-bounded task attachments, authorized download, safe object keys and durable storage adapter. Test oversized content, wrong owner, failed writes and stream cleanup. |
| 16: durable jobs and idempotency | 11, 13, 14 | Queued export with Celery/Redis or equivalent, persisted job status and an outbox/idempotency boundary. Kill a worker, retry and prove no duplicate side effect or cross-user job access. |
| 17: caching and shared abuse controls | 10, 11, 13 | Cache project summaries with tenant-aware keys, TTL/invalidation and a shared limiter. Test concurrent limits, stale data, invalidation and shared-store outages. |
| 18: real-time delivery | 7, 9, 16 | Authenticated progress updates over SSE or WebSockets. Test disconnect/reconnect, authorization and distribution across more than one app instance. |
| 19: identity lifecycle and permission policy | 7, 13 | Worked role/membership policy and an OIDC authorization-code/PKCE integration or provider-backed session path. Explain expiry/revocation; test denied scopes and relevant cookie/CSRF boundaries. |
| 20: performance, observability and final system | 11, 12, 13–19 | Instrument metrics/traces, run a bounded load test and fix one measured bottleneck. Deploy the integrated app with a compatible migration, demonstrate worker recovery, app rollback and scratch-database restore, and defend the tradeoffs. |

Each advanced lesson should follow: guided vertical slice → a smaller change
with hints → independent feature → deliberately broken failure drill → transfer
to a second domain. Repeated private-task CRUD alone does not demonstrate
transfer. Estimate the advanced workload after authoring and running the labs;
do not advertise an untested completion-time guarantee.

Optional tracks include HTML/templates/static files, MongoDB, GraphQL and manual
VM/nginx deployment. They appear in some other learning paths, but the user's
four API/database/security/cloud goals do not require every alternative stack.
Kubernetes and microservices should not become beginner prerequisites.

## Verification and limitations

The updated verifier parses every Python fence and, with `--run-checkpoints`,
executes seven independent temporary-project checks assembled from the lesson
code: first endpoint, CRUD/PATCH, router refactor, dependency overrides, SQL
rollback, credentials before JWTs, and the transition to JWT/owned detail access.
These checks directly target prerequisites and sequencing; they do not claim
that every open-ended lab is automatically verified.

The existing reference API suite tests final behavior separately. Frontend
content checks cover identifiers, quiz answers, stage-specific references,
readiness links and progress namespaces. A copyable PostgreSQL CI template exists,
but Docker/PostgreSQL/cloud execution requires its own runtime and credentials.
Syntax checks, a SQLite test run or writing a workflow do not establish those
external results.
