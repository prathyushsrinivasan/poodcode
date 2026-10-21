export const AWS_GUIDE = "https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/";
export const AWS_VERIFIED = "2026-10-21";

export const AWS_DOMAINS = [
  { id: 1, title: "Data preparation", weight: 28 },
  { id: 2, title: "Model development", weight: 24 },
  { id: 3, title: "Deployment & orchestration", weight: 24 },
  { id: 4, title: "Operations, cost & security", weight: 24 },
] as const;

export const AWS_TASKS = [
  { id: "1.1", title: "Collect and store", labels: ["Extract source data", "Choose compliant storage", "Debug ingestion bottlenecks", "Ingest streaming events", "Select serialization formats", "Join multiple sources", "Configure vector databases", "Ingest multimodal assets", "Populate Feature Store"] },
  { id: "1.2", title: "Transform and engineer features", labels: ["Choose transformation tools", "Manage reusable features", "Transform streaming events", "Engineer numeric features", "Generate multimodal embeddings", "Preprocess domain text", "Prepare RAG documents", "Anonymize sensitive data", "Prepare customization datasets"] },
  { id: "1.3", title: "Quality and bias", labels: ["Validate data quality", "Annotate training examples", "Mitigate dataset bias", "Compare multimodal distributions", "Address imbalanced classes", "Validate prompt-response integrity", "Clean flawed records"] },
  { id: "2.1", title: "Select modeling approaches", labels: ["Select Bedrock FMs", "Choose fine-tuning strategies", "Match models to requirements", "Compare managed/custom approaches", "Choose RAG patterns", "Balance training tradeoffs", "Balance inference tradeoffs", "Apply specialized AI services"] },
  { id: "2.2", title: "Train and customize", labels: ["Use algorithms/libraries", "Configure script mode", "Tune hyperparameters automatically", "Accelerate training jobs", "Diagnose fit/forgetting", "Combine multiple models", "Adjust training hyperparameters", "Customize prompts/models", "Optimize embeddings/retrieval"] },
  { id: "2.3", title: "Evaluate performance", labels: ["Reproduce versioned experiments", "Establish drift baselines", "Compare shadow variants", "Explain model predictions", "Debug convergence failures", "Evaluate ML/GenAI quality", "Include human evaluation", "Interpret NLP metrics", "Assess safety/judge quality", "Assess retrieval accuracy"] },
  { id: "3.1", title: "Deployment infrastructure", labels: ["Select deployment compute", "Orchestrate models/containers", "Choose inference modes", "Compare FM hosting", "Import external models", "Deploy tool-using agents", "Allocate FM resources", "Configure RAG retrieval"] },
  { id: "3.2", title: "Provision resources", labels: ["Choose capacity commitments", "Automate connected infrastructure", "Maintain workload containers", "Network private endpoints", "Deploy through SDKs/CLI", "Select scaling signals", "Configure knowledge bases", "Implement retrieval pipelines", "Persist agent state", "Scale GPU workloads", "Provision agent infrastructure"] },
  { id: "3.3", title: "Automate delivery", labels: ["Roll out/roll back", "Troubleshoot delivery services", "Configure training/inference jobs", "Automate pipeline tests", "Trigger model retraining", "Version registered models", "Version managed prompts", "Version/deploy agents", "Test prompts/models", "Automate customized-FM releases", "Refresh RAG indexes"] },
  { id: "4.1", title: "Monitor inference", labels: ["Monitor production quality", "Detect workflow failures", "Detect distribution changes", "Run production A/B tests", "Observe agent coordination", "Monitor FM quality"] },
  { id: "4.2", title: "Optimize operations", labels: ["Choose inference instances", "Trace resource problems", "Build metric dashboards", "Optimize reliable capacity", "Budget/control spending", "Choose purchasing options", "Estimate FM costs", "Measure agent consumption", "Optimize inference usage", "Attribute token/vector costs"] },
  { id: "4.3", title: "Secure workloads", labels: ["Scan code/images", "Restrict artifact access", "Configure IAM identities", "Audit compliance/logging", "Debug access failures", "Isolate workload networks", "Mitigate AI threats", "Select FM credentials", "Apply responsible-AI safeguards"] },
] as const;

export const AWS_SKILLS = AWS_TASKS.flatMap((task) => task.labels.map((title, i) => ({
  id: `${task.id}.${i + 1}`, task: task.id, domain: Number(task.id[0]), title,
})));

export interface AwsQuestion {
  id: string;
  prompt: string;
  options: { text: string; why: string }[];
  answers: number[];
}

export interface AwsLesson {
  id: string;
  task: string;
  title: string;
  skills: string[];
  model: string;
  rules: string[];
  trap: string;
  recall: string;
  exercise: string;
  exerciseAnswer: string;
  references: { title: string; url: string }[];
  questions: AwsQuestion[];
}
