// Bundle selected worked files so the solutions remain readable offline inside
// the app. Never glob .env, databases, bytecode or local environment directories.
import foundations from "./01-foundations.md?raw";
import contracts from "./02-contracts.md?raw";

const blocks = (content: string) => [...content.matchAll(/^```python\r?\n([\s\S]*?)^```/gm)].map((match) => match[1].trim());
const selectBlock = (content: string, contains: string) => {
  const block = blocks(content).find((source) => source.includes(contains));
  if (!block) throw new Error(`Missing FastAPI teaching block: ${contains}`);
  return block;
};
const file = (path: string, content: string) => `### ${path}\n\n\`\`\`python\n${content}\n\`\`\``;

const sources = import.meta.glob<string>([
  "../../../examples/fastapi-taskboard/app/*.py",
  "../../../examples/fastapi-taskboard/tests/*.py",
  "../../../examples/fastapi-taskboard/scripts/*.py",
  "../../../examples/fastapi-taskboard/migrations/env.py",
  "../../../examples/fastapi-taskboard/migrations/versions/*.py",
  "../../../examples/fastapi-taskboard/requirements*.txt",
  "../../../examples/fastapi-taskboard/Dockerfile",
  "../../../examples/fastapi-taskboard/compose.yaml",
], { eager: true, query: "?raw", import: "default" });

const filesByModule = [
  ["requirements-dev.txt", "app/main.py"],
  ["app/schemas.py", "app/tasks.py"],
  ["app/config.py", "app/db.py", "app/main.py"],
  ["app/db.py", "app/models.py", "app/tasks.py"],
  ["compose.yaml", "migrations/env.py", "migrations/versions/0001_initial.py"],
  ["app/auth.py", "app/schemas.py"],
  ["app/security.py", "app/tasks.py"],
  ["tests/test_api.py"],
  ["app/db.py", "app/main.py"],
  ["app/main.py", "app/config.py"],
  ["Dockerfile", "requirements.txt", "scripts/smoke.py"],
  ["scripts/cloud_smoke.py", "scripts/smoke.py"],
];

export function workedReference(moduleIndex: number): string {
  if (moduleIndex === 0) {
    return file("app/main.py", selectBlock(foundations, '@app.get("/health/live")'));
  }
  if (moduleIndex === 1) {
    return [
      file("app/schemas.py", selectBlock(contracts, "class TaskCreate") + "\n\n" + selectBlock(contracts, "class TaskPatch")),
      file("app/main.py", selectBlock(contracts, "app = FastAPI()") + "\n\nfrom .schemas import TaskPatch\n\n" + selectBlock(contracts, "def list_tasks(")),
    ].join("\n\n");
  }
  return filesByModule[moduleIndex].map((path) => {
    const content = sources[`../../../examples/fastapi-taskboard/${path}`];
    if (content === undefined) throw new Error(`Missing FastAPI worked reference: ${path}`);
    const language = path.endsWith(".py") ? "python" : path.endsWith(".yaml") ? "yaml" : path === "Dockerfile" ? "dockerfile" : "text";
    return `### ${path}\n\n\`\`\`${language}\n${content.trim()}\n\`\`\``;
  }).join("\n\n");
}
