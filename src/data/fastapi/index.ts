import type { CourseWeek, QuizQuestion, WeeklyCourse } from "../../types";
import foundations from "./01-foundations.md?raw";
import contracts from "./02-contracts.md?raw";
import architecture from "./03-architecture.md?raw";
import databases from "./04-databases.md?raw";
import postgres from "./05-postgres.md?raw";
import passwords from "./06-passwords.md?raw";
import authorization from "./07-authorization.md?raw";
import testing from "./08-testing.md?raw";
import concurrency from "./09-concurrency.md?raw";
import operations from "./10-operations.md?raw";
import containers from "./11-containers.md?raw";
import deployment from "./12-deployment.md?raw";
import { workedReference } from "./reference";

type Module = {
  title: string;
  goal: string;
  minutes: number;
  content: string;
  lessons: [string, string];
  build: string;
  checks: string[];
  questions: QuizQuestion[];
};
const q = (question: string, options: string[], answer: number, explanation: string): QuizQuestion =>
  ({ question, options, answer, explanation });

const modules: Module[] = [
  {
    title: "From Python to your first HTTP API", minutes: 240, content: foundations,
    goal: "Create a Python environment, run FastAPI, and test a real endpoint.",
    lessons: ["Python tools you will actually use", "Run, inspect, and test your first endpoint"],
    build: "Build a health API from an empty folder. Add GET /health/live and GET /hello?name=Ada. Write a test for each, deliberately break one, and repair it.",
    checks: ["A fresh virtual environment can install and start the app", "GET /hello?name=Ada returns 200 and a JSON greeting", "The docs and OpenAPI schema contain both routes", "pytest catches a changed greeting"],
    questions: [
      q("An endpoint annotates task_id: int. What happens to GET /tasks/abc?", ["The handler receives the string abc", "FastAPI normally returns 422 before calling the handler", "The database always returns 404"], 1, "FastAPI validates the path value against the annotation. A value that cannot become an integer fails validation."),
      q("Which command starts the app variable inside app/main.py from the project root?", ["uvicorn main.app", "python app", "python -m uvicorn app.main:app --reload"], 2, "The import string is module:attribute. Reload belongs in local development."),
      q("What does an annotation like list[str] do by itself in ordinary Python?", ["Describes the intended type; Python itself does not enforce it", "Rejects every non-string at runtime", "Creates a database table"], 0, "FastAPI and Pydantic inspect annotations and add validation; plain Python annotations are metadata."),
    ],
  },
  {
    title: "Design API contracts and build CRUD", minutes: 240, content: contracts,
    goal: "Implement validated requests, public responses, errors, and partial updates.",
    lessons: ["Routes, request bodies, and response boundaries", "CRUD, PATCH, and useful failure cases"],
    build: "Build an in-memory task API with POST, list, detail, PATCH and DELETE. Use a monotonic counter for IDs; never use len(tasks) + 1. Treat this as a disposable teaching stage before persistence.",
    checks: ["POST returns 201; missing detail returns 404", "Blank and oversized titles return 422", "PATCH with done=false changes true to false without losing the title", "DELETE returns 204 with an empty body", "Restarting loses in-memory tasks, and you can explain why"],
    questions: [
      q("PATCH receives {\"done\": false}. Which update preserves the explicit false?", ["if body.done: task.done = body.done", "Reset every omitted field to its default", "Iterate body.model_dump(exclude_unset=True)"], 2, "exclude_unset distinguishes omission from an explicitly supplied false. Truthiness would drop the requested update."),
      q("Why define TaskRead separately from the database row?", ["To make HTTP slower", "To explicitly control which fields leave the server", "To let clients set owner_id"], 1, "An output contract prevents accidental exposure of internal fields when the database model grows."),
      q("What should a successful 204 deletion response contain?", ["No response body", "A JSON null body", "A copy of the deleted object"], 0, "204 means no content. Return an empty Response rather than a JSON payload."),
    ],
  },
  {
    title: "Structure an app with routers and dependencies", minutes: 180, content: architecture,
    goal: "Separate HTTP, configuration, persistence, and reusable business decisions.",
    lessons: ["Refactor without changing the API", "Dependencies, validated settings, and resource lifetimes"],
    build: "Split your API into an app package. Move task routes into an APIRouter, request models into schemas.py, and settings into config.py. Demonstrate a dependency override with the standalone prefix example; module 4 introduces the request-scoped database session.",
    checks: ["The pre-refactor contract tests still pass", "There is one app entry point and no circular imports", "A dependency override can replace a resource in a test", "Missing or short JWT_SECRET configuration fails validation"],
    questions: [
      q("What does the code after yield in a dependency usually provide?", ["Another HTTP response", "Resource cleanup when the dependency scope ends", "A global singleton per user"], 1, "A yield dependency can scope a session or other resource to a request and close it reliably."),
      q("Where should a database connection string come from in deployment?", ["A secret pasted into a router", "A browser query parameter", "Validated server-side configuration"], 2, "Settings keep environment differences outside business logic and validate configuration before serving requests."),
      q("You are writing a reusable function that computes a price. Should it call Depends(get_db) itself?", ["No; pass ordinary arguments, since FastAPI resolves Depends only in its dependency graph", "Yes; Depends runs automatically in every Python call", "Only if the function name starts with get_"], 0, "Dependency resolution belongs at the FastAPI boundary. Calling a normal function does not resolve a Depends marker."),
    ],
  },
  {
    title: "Persist data with SQLAlchemy and SQLite", minutes: 300, content: databases,
    goal: "Model relationships, scope sessions, and implement durable CRUD with transactions.",
    lessons: ["Tables, relationships, engines, and sessions", "Write and query real data safely"],
    build: "Replace the dictionary with SQLAlchemy 2 models, a SQLite engine and a session dependency. First use create_all only for this local learning stage. Persist tasks across restarts and recover cleanly after a duplicate-user conflict.",
    checks: ["A task survives stopping and restarting the API", "A foreign key associates each task with a user", "One request does not share a global mutable Session with another", "A failed unique constraint is rolled back", "SQL values use bound parameters or ORM expressions"],
    questions: [
      q("What must happen after an IntegrityError before reusing that session?", ["Ignore the exception", "Restart the whole server", "Roll back the failed transaction"], 2, "A failed flush/commit leaves the session transaction needing rollback. A process restart is not transaction handling."),
      q("Which object is normally shared application-wide?", ["A mutable Session used by every request", "The Engine/connection pool", "The currently authenticated User"], 1, "An engine manages connections. Sessions track per-unit-of-work state and should have limited lifetimes."),
      q("Does relationship(back_populates=...) alone prevent an orphan owner_id in SQL?", ["No; the database needs an enforced foreign key", "Yes; it creates every constraint automatically", "Only for strings"], 0, "ORM navigation and database constraints solve different problems. SQLite also needs foreign_keys enabled per connection."),
    ],
  },
  {
    title: "PostgreSQL, migrations, and efficient queries", minutes: 270, content: postgres,
    goal: "Move to PostgreSQL, evolve schemas with Alembic, and bound database work.",
    lessons: ["Run PostgreSQL and migrate deliberately", "Pagination, query plans, and transactional changes"],
    build: "Start PostgreSQL with Compose, point DATABASE_URL at psycopg, and migrate an empty database. Add bounded, ordered pagination and a done filter. Create a reversible description-column migration and inspect its generated SQL before applying it.",
    checks: ["alembic upgrade head works on a fresh database", "alembic check reports no unexpected drift", "A reviewed migration adds a column without losing a seeded row", "Limit 0, limit 101 and offset -1 return 422", "An index and an EXPLAIN plan can be tied to a real query"],
    questions: [
      q("Why is create_all insufficient for deployment schema evolution?", ["It is a password hashing algorithm", "It does not provide reviewed, ordered schema changes to existing tables", "It only works with cloud databases"], 1, "Alembic records an explicit revision history. create_all creates missing tables rather than safely migrating existing ones."),
      q("What makes offset pagination repeatable for an unchanged dataset?", ["An explicit deterministic ORDER BY", "A larger JSON response", "Removing the limit"], 0, "Rows have no guaranteed order without ORDER BY. Concurrent inserts/deletes still motivate keyset pagination."),
      q("Can you apply an autogenerated Alembic migration without reading it?", ["Always; autogenerate proves data preservation", "Only if the file is short", "No; renames and data backfills can require manual changes"], 2, "Autogeneration produces candidate migrations. Review operations, data movement, constraints and compatibility before release."),
    ],
  },
  {
    title: "Passwords and login", minutes: 240, content: passwords,
    goal: "Register users, hash passwords with Argon2, and build a tested login boundary.",
    lessons: ["Store password hashes and expose public users", "Authenticate with explicit failure behavior"],
    build: "Implement registration and a temporary form-based /auth/login-check route. Store only an Argon2 hash. Normalize usernames consistently and handle uniqueness races with a database constraint. Verify credentials and return only the public user; module 7 adds token issuance.",
    checks: ["The stored value differs from the submitted password and verifies correctly", "Neither registration nor /auth/login-check exposes password_hash", "Concurrent duplicate usernames cannot create duplicate rows", "Wrong passwords and unknown usernames receive the same 401 detail", "Credential-check responses carry Cache-Control: no-store"],
    questions: [
      q("Which value should be stored for a password?", ["The plaintext in an encrypted JSON response", "A salted adaptive password hash such as Argon2", "A fast unsalted SHA-256 digest"], 1, "Password hashing deliberately increases the cost of offline guessing. Encryption and fast digests do not provide the same protection."),
      q("Why can a check-then-insert username lookup still race?", ["SQL cannot store strings", "FastAPI disables uniqueness", "Two requests can both observe absence before either commits"], 2, "Enforce uniqueness in the database and handle IntegrityError, even if an earlier lookup improves the user experience."),
      q("OAuth2PasswordRequestForm expects which encoding for login?", ["Form fields named username and password", "A raw SQL query", "Only a JSON array"], 0, "The password form is application/x-www-form-urlencoded and requires python-multipart support. It is separate from JSON registration."),
    ],
  },
  {
    title: "JWTs, ownership, and authorization", minutes: 240, content: authorization,
    goal: "Validate credentials and enforce access on every resource operation.",
    lessons: ["Issue and validate short-lived access tokens", "Prevent cross-user access and add role policies"],
    build: "Implement current_user, then protect every task route. Derive owner_id from the authenticated user. Prove that Bob cannot list, read, patch or delete Alice's tasks. Add an admin-only diagnostic endpoint as a stretch with a server-managed role and positive/negative tests.",
    checks: ["Missing, expired, tampered and wrong-audience tokens return 401", "Disabled users lose access even with an unexpired token", "Clients cannot submit owner_id or elevate roles", "All four cross-user operations are denied", "You can explain authentication, ownership and role checks separately"],
    questions: [
      q("A signed JWT contains a password. Is that password hidden from the bearer?", ["Yes; every JWT is encrypted", "Only over localhost", "No; ordinary signed JWT payloads are readable"], 2, "A signature protects integrity. Keep secrets and sensitive personal data out of token payloads."),
      q("Bob has a valid token and guesses Alice's task ID. What must the database lookup include?", ["Only Task.id", "Task.id and the authenticated owner constraint", "The owner_id Bob supplied in the request"], 1, "Authentication alone does not authorize access to an object. Scope every relevant lookup and list query to the user."),
      q("Where should the accepted JWT algorithm list come from?", ["Server configuration fixed to the intended algorithm", "The token's untrusted alg header", "A request query parameter"], 0, "The verifier controls allowed algorithms, issuer and audience. Attacker-controlled token metadata cannot set verification policy."),
    ],
  },
  {
    title: "Test the API like a backend engineer", minutes: 240, content: testing,
    goal: "Build independent tests for behavior, database isolation, and security regressions.",
    lessons: ["TestClient, fixtures, and dependency overrides", "Write tests that expose real bugs"],
    build: "Write the contract and security test suite before consulting the reference tests. Use an isolated database per test. Make three deliberate mutations: remove owner filtering, ignore done=false, and accept expired tokens. Your tests must fail for each mutation.",
    checks: ["Tests never connect to your live development or cloud database", "The suite can run repeatedly and in a different order", "Ownership, false PATCH, output filtering and token rejection are asserted", "Database overrides are cleared after every test", "A PostgreSQL migration smoke test is separate from fast SQLite tests"],
    questions: [
      q("Why use StaticPool for an in-memory SQLite TestClient fixture?", ["To skip SQL execution", "So request threads share the same in-memory database connection", "To make production PostgreSQL globally mutable"], 1, "An ordinary in-memory SQLite database belongs to a connection. The test fixture shares one connection while isolating different tests with fresh engines."),
      q("Which test best detects broken object authorization?", ["POST returns any 2xx", "The function is named owned_task", "A second user cannot GET, PATCH or DELETE the first user's task"], 2, "Test externally visible security behavior. Naming and implementation shape do not establish isolation."),
      q("Does a passing SQLite suite prove a PostgreSQL migration works?", ["No; run migration and integration checks against PostgreSQL too", "Yes; SQL dialects are identical", "Only when tests run on Windows"], 0, "Types, constraints, transactional DDL and query behavior differ. Keep a real PostgreSQL verification stage."),
    ],
  },
  {
    title: "Concurrency and external services", minutes: 180, content: concurrency,
    goal: "Choose sync versus async deliberately and bound outbound work.",
    lessons: ["Use async I/O without blocking the event loop", "Lifespan, background work, and failure boundaries"],
    build: "In a separate practice branch, add an async external-service adapter using a shared httpx.AsyncClient and an explicit timeout. Test success, timeout and upstream failure without calling the real network. Add a BackgroundTasks notification and explain which work needs a durable queue.",
    checks: ["Sync database routes remain def unless the whole DB stack becomes async", "A shared HTTP client closes during lifespan shutdown", "A timeout maps to a documented API error", "Tests simulate upstream behavior with a mock transport", "A process restart can lose BackgroundTasks work, so critical jobs have a durable design"],
    questions: [
      q("An async def endpoint calls time.sleep(2). What happens?", ["It automatically moves to a worker thread", "The sleep becomes an await", "It blocks the event-loop thread"], 2, "async def does not make blocking libraries nonblocking. Use awaitable I/O or deliberately offload blocking work."),
      q("Which task fits FastAPI BackgroundTasks without extra durability?", ["A best-effort notification that can be lost on restart", "The only record of a payment", "A guaranteed multi-hour export"], 0, "In-process background tasks are useful for noncritical follow-up work. Durable jobs need persistence, retries and worker supervision."),
      q("Why create one outbound AsyncClient during app lifespan?", ["To avoid validating requests", "To reuse pooled connections and close them at shutdown", "To share one mutable database Session across users"], 1, "Connection reuse reduces setup work. The lifecycle should match the resource; do not confuse an HTTP client with a transaction-bound DB session."),
    ],
  },
  {
    title: "Production security and observability", minutes: 180, content: operations,
    goal: "Configure CORS, logs, health checks, abuse controls, and secret handling.",
    lessons: ["Harden the HTTP boundary", "Find failures with logs and health probes"],
    build: "Add an explicit CORS allowlist, request IDs, route-level timing and separate live/ready endpoints. Exercise a browser preflight and a database outage. Design and test login rate limits at a shared gateway or Redis-backed layer before exposing registration to untrusted traffic.",
    checks: ["Disallowed origins do not receive an allow-origin header", "A failing database produces 503 readiness while liveness still works", "Logs omit credentials, request bodies and query strings", "The login abuse control works across more than one worker", "An environment-specific HTTPS and secret rotation plan is written down"],
    questions: [
      q("Does CORS stop a command-line client from calling your API?", ["Yes; it authenticates every caller", "No; it is a browser cross-origin response policy", "Only when a JWT is expired"], 1, "Authentication and authorization must hold for all clients. CORS is an additional browser boundary."),
      q("The database is unavailable but the API process is responsive. Which probe should fail?", ["Readiness", "Only the favicon", "Every liveness check must kill the process immediately"], 0, "Readiness checks whether the service can do useful work. Liveness checks the process itself; unnecessary restarts can amplify an outage."),
      q("What is wrong with a production login limiter stored in a Python dictionary?", ["Dictionary lookup is always O(n)", "It encrypts usernames", "Counters split between processes and vanish on restart"], 2, "Use a shared enforcement layer with bounded keys, expiry and a documented failure policy when multiple instances serve traffic."),
    ],
  },
  {
    title: "Containers and continuous integration", minutes: 210, content: containers,
    goal: "Package the API, run it with PostgreSQL, and automate regression checks.",
    lessons: ["Build a reproducible container", "Run tests and migrations in CI"],
    build: "Build the reference Dockerfile, run migrations as a separate one-off operation and start the container against PostgreSQL. Add the provided CI workflow to your learning repository. Confirm an intentionally failing ownership test blocks the workflow.",
    checks: ["The container listens on 0.0.0.0 and has no reload flag", "The process runs as a non-root user", "Secrets are injected at runtime and excluded from the image", "One migration job runs before serving the new release", "CI passes unit/API tests plus a fresh PostgreSQL migration check"],
    questions: [
      q("Why bind the container server to 0.0.0.0?", ["To disable authorization", "To publish the database password", "To accept traffic on the container network interface"], 2, "Binding only to container-local 127.0.0.1 prevents normal forwarded traffic from reaching the server."),
      q("Where should schema migrations run during a multi-worker deployment?", ["Inside every incoming request", "In one coordinated release operation before the new app serves", "Independently in every worker at import time"], 1, "Coordinating migrations avoids concurrent schema changes. Apply backward-compatible changes when old and new app versions overlap."),
      q("Which file belongs in .dockerignore?", [".env", "app/main.py", "requirements.txt"], 0, "Local secrets and databases must not enter the image build context. Application source and dependency pins are required."),
    ],
  },
  {
    title: "Deploy to the cloud and pass the final build", minutes: 300, content: deployment,
    goal: "Deploy a secure PostgreSQL-backed API and prove it survives a release.",
    lessons: ["Deploy a web service and managed PostgreSQL on Render", "Final practical: rebuild, operate, and defend your design"],
    build: "From an empty repository, rebuild Taskboard using the endpoint contract. Deploy it with managed PostgreSQL and HTTPS, migrate the database once, run the two-user smoke test, redeploy and verify persistence. Record a rollback rehearsal, a restore rehearsal on a scratch database, and a short design explanation.",
    checks: ["A clean checkout installs and passes the local suite", "Public HTTPS endpoints pass registration, login and two-user ownership checks", "A task survives a service redeploy", "A previous app release can be restored without destructive schema changes", "A backup restores into a separate scratch database and the restored row is readable", "You can add a due-date feature with validation, a migration, tests and a release plan"],
    questions: [
      q("Your tasks disappear after cloud redeployment. What should you investigate first?", ["Whether state was stored on ephemeral local disk instead of managed PostgreSQL", "The CSS theme", "Whether response_model is present"], 0, "A durable database lives outside replaceable app instances. Local SQLite is useful for learning but is not this cloud deployment's persistence strategy."),
      q("A release adds a required column to a table containing rows. What is a safer rollout?", ["Drop and recreate the table", "Deploy without considering existing rows", "Expand compatibly, backfill, then enforce the requirement in a later coordinated step"], 2, "Schema compatibility and existing data determine deployment safety. An app image rollback does not undo a destructive migration."),
      q("Which evidence best demonstrates completion of this course?", ["Reading every lesson", "A deployed API, reproducible tests, isolation checks and an operations runbook", "Knowing the definition of ASGI"], 1, "The objective is usable engineering skill. Demonstrate the behavior and recovery procedures, and explain the design decisions."),
    ],
  },
];

const parts = ["Build and design", "Persist and evolve", "Secure and verify", "Operate and deploy"];
const entryChecks = [
  "No FastAPI knowledge required. Complete the Python readiness lab before moving beyond the bridge.",
  "You can run a Python function and test, and identify the method, path, status and JSON body in an HTTP exchange.",
  "Your in-memory CRUD sequence passes, including done=false, invalid input and empty DELETE responses.",
  "You can move a route into a router, resolve a dependency, and explain what a fixture and yield do.",
  "You can read SELECT/INSERT/UPDATE, seed a local owner, and commit or roll back a session without sharing it across requests.",
  "Your users table has a uniqueness constraint, migrations work, and IntegrityError handling rolls back.",
  "Registration hashes passwords and the temporary login-check verifies credentials without issuing a token.",
  "Protected task routes require tokens and enforce ownership; update earlier anonymous-success tests to the new contract.",
  "You can override dependencies in an isolated fixture and assert HTTP success and failure behavior.",
  "You understand identity/ownership, request middleware and the difference between in-process work and shared infrastructure.",
  "Your core API tests and migrations pass, and you can describe which configuration is secret.",
  "Your API is packaged, release checks pass, and you have a plan for login abuse controls, migrations and durable storage.",
];

export const FASTAPI_COURSE: WeeklyCourse = {
  key: "fastapi", title: "FastAPI: build, secure, deploy",
  subtitle: "Beginner to intermediate · 12 practical modules · 24 lessons · 36 explained questions. Plan 40–50 hours to build, secure and deploy one API; advanced specializations remain an extension path.",
  unit_label: "Module", group_label: "Part",
  weeks: modules.map((m, i): CourseWeek => {
    const sections = m.content.trim().split(/\r?\n<!-- lesson -->\r?\n/);
    if (sections.length !== m.lessons.length) throw new Error(`FastAPI module ${i + 1}: lesson sections do not match`);
    const part = i < 3 ? 0 : i < 5 ? 1 : i < 8 ? 2 : 3;
    return {
      number: i + 1, month: part + 1, month_title: parts[part], theme: m.title,
      goal: m.goal, authored: true, est_minutes: m.minutes,
      summary: `**Before you start:** ${entryChecks[i]}${i > 0 ? ` If this is unfamiliar, revisit [module ${i}](#/fastapi-course/${i}).` : ""}\n\n**Build first:** ${m.build}\n\nWork in your own Python project. The complete worked solution and commands live in \`examples/fastapi-taskboard\` in this repository; relevant source files are also included in the reference reveal below. These labs run in your terminal with real FastAPI dependencies. After verifying the project checklist, use **Mark done now** to save your progress.`,
      lessons: m.lessons.map((title, j) => ({
        key: `fastapi-${i + 1}-${j + 1}`, title,
        what: j === 0 ? "Type the worked example, run it, and inspect the result." : "Change the behavior, test a failure, and complete the lab.",
        lesson: sections[j], warmup: [], exercises: [], quiz: [],
      })),
      objectives: [m.goal, "Implement the module project and verify observable behavior"],
      why: "Each module adds a working capability to the same API, so you practice the decisions together.",
      capstone: {
        kind: "brief", title: `Build ${i + 1}: ${m.title}`, brief: m.build,
        rubric: m.checks, exercise: null, stretch: null, example_io: "",
        reference: (i < 2
          ? "These are the runnable source files for this teaching stage, using only ideas introduced so far. Keep the local virtual environment and tests from the lessons.\n\n"
          : "Compare your implementation with the worked solution in `examples/fastapi-taskboard`. Run `python -m pytest -q` there after installing `requirements-dev.txt`. These reference files show the final architecture and can contain ideas introduced later. Module 6 deliberately uses /auth/login-check before module 7 replaces it with /auth/token. Module 9's outbound adapter and the optional admin policy are separate extension labs, not routes in the core reference API.\n\n") + workedReference(i),
      },
      self_check: m.checks, review: m.questions, glossary: [], practice: [],
      cheatsheet: "", milestone: `You verified: ${m.goal}`,
    };
  }),
};
