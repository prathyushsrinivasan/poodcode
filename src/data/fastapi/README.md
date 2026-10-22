# FastAPI course authoring

`index.ts` adapts 12 fully authored modules to the existing WeeklyCourse reader.
Each Markdown file contains exactly two lessons separated by `<!-- lesson -->`.
Keep the separator outside fenced code. Each module has a project, acceptance
checks and three original explained review questions. The course is bundled for
offline reading; dependency installation, external integrations and cloud labs
need their own runtimes/network access.

Content is code-first and cumulative: a Taskboard API grows through app design,
validation, SQLAlchemy, PostgreSQL, migrations, passwords, JWT authorization,
testing, concurrency, operations, containers and Render deployment. Complete
reference code is in `examples/fastapi-taskboard`. Module 9's outbound HTTP and
background-task examples and module 7's optional admin role are extensions rather
than routes in the core reference. Module 10 explicitly requires an implemented
abuse-control layer or provider policy before public registration.

The audited scope is a beginner-to-intermediate core, not a complete advanced
curriculum. [The audit](../../../FASTAPI_COURSE_AUDIT.md) compares public course
syllabi, records sequencing fixes and specifies the unimplemented advanced
extension. Entry checks link to previous modules without changing saved keys.
The first two worked reveals are assembled from the actual teaching-stage code
so they do not require the final database/auth architecture.

Progress uses existing SQLite chapter completion keys `fastapi-course:wN`, with
manual completion after the project checks. Reading to the end must not
auto-complete these practical builds. Quizzes use the shared course quiz UI;
completion does not claim an automatically verified cloud deployment.

Validation: `npm test -- src/data/fastapi/course.test.ts`, `npm run typecheck`,
`npm run build`, and the reference README's Python test/migration/smoke commands.
Inside the reference virtual environment, run
`python tools/verify_fastapi_course.py --run-checkpoints` from the repository root
to parse all Python fences and execute the cumulative beginner checkpoints.
The CI template in `examples/fastapi-taskboard/ci/fastapi-course.yml`, once
installed as a GitHub workflow, checks PostgreSQL with Python 3.12/3.14.
Keep provider commands and security library examples aligned with
their linked official documentation.
