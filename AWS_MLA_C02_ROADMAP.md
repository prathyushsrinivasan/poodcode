# AWS MLA-C02 learning roadmap

Verified against AWS documentation on **2026-10-21**. This checklist maps **all 107 published skills across 12 tasks**. Labels below are concise study labels; use the linked guide for exact AWS wording. AWS describes its outline and service lists as non-exhaustive, so this is coverage of the published blueprint, not a guarantee of every possible exam question.

## Exam baseline

MLA-C02 includes traditional ML, foundation models, RAG, and agents. Domain weights are **28%, 24%, 24%, 24%**. The certification page currently describes an English beta with **85 questions / 170 minutes**; do not confuse this with the guide's standard 65-question format. Recheck the booking page before scheduling. A practice percentage in this app is not an AWS scaled score or a prediction of passing.

- [Official exam guide](https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/)
- [Exam format and beta status](https://aws.amazon.com/certification/certified-machine-learning-engineer-associate/)
- [In-scope services](https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/mla-02-in-scope-services.html)
- [Out-of-scope services](https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/mla-02-out-of-scope-services.html)

## Prerequisites and practical abilities

Be comfortable reading Python, SQL, JSON, IAM policies, logs, and simple container definitions. Explain classification, regression, clustering, embeddings, train/validation/test separation, precision versus recall, latency percentiles, throughput, encryption, and least privilege. Practice choosing a service from business constraints and explaining why competing options fail. AWS targets candidates with about a year of relevant experience; daily quizzes supplement practical work.

## Domain 1 — Data preparation (28%)

[Domain 1 source](https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/machine-learning-engineer-associate-02-domain1.html)

### 1.1 — Collect and store

- [ ] **1.1.1** Extract source data
- [ ] **1.1.2** Choose compliant storage
- [ ] **1.1.3** Debug ingestion bottlenecks
- [ ] **1.1.4** Ingest streaming events
- [ ] **1.1.5** Select serialization formats
- [ ] **1.1.6** Join multiple sources
- [ ] **1.1.7** Configure vector databases
- [ ] **1.1.8** Ingest multimodal assets
- [ ] **1.1.9** Populate Feature Store

### 1.2 — Transform and engineer features

- [ ] **1.2.1** Choose transformation tools
- [ ] **1.2.2** Manage reusable features
- [ ] **1.2.3** Transform streaming events
- [ ] **1.2.4** Engineer numeric features
- [ ] **1.2.5** Generate multimodal embeddings
- [ ] **1.2.6** Preprocess domain text
- [ ] **1.2.7** Prepare RAG documents
- [ ] **1.2.8** Anonymize sensitive data
- [ ] **1.2.9** Prepare customization datasets

### 1.3 — Quality and bias

- [ ] **1.3.1** Validate data quality
- [ ] **1.3.2** Annotate training examples
- [ ] **1.3.3** Mitigate dataset bias
- [ ] **1.3.4** Compare multimodal distributions
- [ ] **1.3.5** Address imbalanced classes
- [ ] **1.3.6** Validate prompt-response integrity
- [ ] **1.3.7** Clean flawed records

## Domain 2 — Model development (24%)

[Domain 2 source](https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/machine-learning-engineer-associate-02-domain2.html)

### 2.1 — Select modeling approaches

- [ ] **2.1.1** Select Bedrock FMs
- [ ] **2.1.2** Choose fine-tuning strategies
- [ ] **2.1.3** Match models to requirements
- [ ] **2.1.4** Compare managed/custom approaches
- [ ] **2.1.5** Choose RAG patterns
- [ ] **2.1.6** Balance training tradeoffs
- [ ] **2.1.7** Balance inference tradeoffs
- [ ] **2.1.8** Apply specialized AI services

### 2.2 — Train and customize

- [ ] **2.2.1** Use algorithms/libraries
- [ ] **2.2.2** Configure script mode
- [ ] **2.2.3** Tune hyperparameters automatically
- [ ] **2.2.4** Accelerate training jobs
- [ ] **2.2.5** Diagnose fit/forgetting
- [ ] **2.2.6** Combine multiple models
- [ ] **2.2.7** Adjust training hyperparameters
- [ ] **2.2.8** Customize prompts/models
- [ ] **2.2.9** Optimize embeddings/retrieval

### 2.3 — Evaluate performance

- [ ] **2.3.1** Reproduce versioned experiments
- [ ] **2.3.2** Establish drift baselines
- [ ] **2.3.3** Compare shadow variants
- [ ] **2.3.4** Explain model predictions
- [ ] **2.3.5** Debug convergence failures
- [ ] **2.3.6** Evaluate ML/GenAI quality
- [ ] **2.3.7** Include human evaluation
- [ ] **2.3.8** Interpret NLP metrics
- [ ] **2.3.9** Assess safety/judge quality
- [ ] **2.3.10** Assess retrieval accuracy

## Domain 3 — Deployment and orchestration (24%)

[Domain 3 source](https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/machine-learning-engineer-associate-02-domain3.html)

### 3.1 — Deployment infrastructure

- [ ] **3.1.1** Select deployment compute
- [ ] **3.1.2** Orchestrate models/containers
- [ ] **3.1.3** Choose inference modes
- [ ] **3.1.4** Compare FM hosting
- [ ] **3.1.5** Import external models
- [ ] **3.1.6** Deploy tool-using agents
- [ ] **3.1.7** Allocate FM resources
- [ ] **3.1.8** Configure RAG retrieval

### 3.2 — Provision resources

- [ ] **3.2.1** Choose capacity commitments
- [ ] **3.2.2** Automate connected infrastructure
- [ ] **3.2.3** Maintain workload containers
- [ ] **3.2.4** Network private endpoints
- [ ] **3.2.5** Deploy through SDKs/CLI
- [ ] **3.2.6** Select scaling signals
- [ ] **3.2.7** Configure knowledge bases
- [ ] **3.2.8** Implement retrieval pipelines
- [ ] **3.2.9** Persist agent state
- [ ] **3.2.10** Scale GPU workloads
- [ ] **3.2.11** Provision agent infrastructure

### 3.3 — Automate delivery

- [ ] **3.3.1** Roll out/roll back
- [ ] **3.3.2** Troubleshoot delivery services
- [ ] **3.3.3** Configure training/inference jobs
- [ ] **3.3.4** Automate pipeline tests
- [ ] **3.3.5** Trigger model retraining
- [ ] **3.3.6** Version registered models
- [ ] **3.3.7** Version managed prompts
- [ ] **3.3.8** Version/deploy agents
- [ ] **3.3.9** Test prompts/models
- [ ] **3.3.10** Automate customized-FM releases
- [ ] **3.3.11** Refresh RAG indexes

## Domain 4 — Operations, cost, and security (24%)

[Domain 4 source](https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/machine-learning-engineer-associate-02-domain4.html)

### 4.1 — Monitor inference

- [ ] **4.1.1** Monitor production quality
- [ ] **4.1.2** Detect workflow failures
- [ ] **4.1.3** Detect distribution changes
- [ ] **4.1.4** Run production A/B tests
- [ ] **4.1.5** Observe agent coordination
- [ ] **4.1.6** Monitor FM quality

### 4.2 — Optimize operations

- [ ] **4.2.1** Choose inference instances
- [ ] **4.2.2** Trace resource problems
- [ ] **4.2.3** Build metric dashboards
- [ ] **4.2.4** Optimize reliable capacity
- [ ] **4.2.5** Budget/control spending
- [ ] **4.2.6** Choose purchasing options
- [ ] **4.2.7** Estimate FM costs
- [ ] **4.2.8** Measure agent consumption
- [ ] **4.2.9** Optimize inference usage
- [ ] **4.2.10** Attribute token/vector costs

### 4.3 — Secure workloads

- [ ] **4.3.1** Scan code/images
- [ ] **4.3.2** Restrict artifact access
- [ ] **4.3.3** Configure IAM identities
- [ ] **4.3.4** Audit compliance/logging
- [ ] **4.3.5** Debug access failures
- [ ] **4.3.6** Isolate workload networks
- [ ] **4.3.7** Mitigate AI threats
- [ ] **4.3.8** Select FM credentials
- [ ] **4.3.9** Apply responsible-AI safeguards

## Service recognition checklist

Know each service's role, nearest alternative, security boundary, and cost driver. Names below follow AWS's in-scope list, grouped compactly; not every service requires equal depth.

| Area | Services/features |
| --- | --- |
| Analytics | Athena, Data Firehose, EMR, Glue, DataBrew, Glue Data Quality, Kinesis, Lake Formation, Managed Service for Apache Flink, OpenSearch, Quick, Redshift |
| Integration | EventBridge, MWAA, SNS, SQS, Step Functions |
| Cost | Billing and Cost Management, Budgets, Cost Explorer |
| Compute/containers | Batch, EC2, Lambda, ECR, ECS, EKS |
| Databases | DocumentDB, DynamoDB, ElastiCache, Neptune, RDS |
| Delivery | CDK, CodeArtifact, CodeBuild, CodeCommit, CodeConnections, CodeDeploy, CodePipeline, X-Ray |
| AI/ML | Bedrock, Bedrock AgentCore, CodeGuru, Comprehend, Comprehend Medical, DevOps Guru, HealthLake, Lex, Personalize, Polly, Rekognition, SageMaker AI, Textract, Transcribe, Translate |
| Governance | Auto Scaling, CloudFormation, CloudTrail, CloudWatch, Compute Optimizer, Config, Organizations, Service Catalog, Systems Manager, Trusted Advisor |
| Media/transfer | Kinesis Video Streams, DataSync |
| Network | API Gateway, CloudFront, Direct Connect, VPC |
| Security | IAM, Inspector, KMS, Macie, Secrets Manager |
| Storage | EBS, EFS, FSx, S3, S3 Glacier, Storage Gateway |

## Daily learning design

The app section lives at **Courses → AWS MLA-C02** (`/aws-mla`). The first implementation groups the blueprint into **24 short lessons**, two per task. Every skill ID maps to one lesson. Each lesson supplies a mental model, practical decision rules, a common trap, a recall prompt, a small design exercise, official references, and two original scenario questions. These are introductory coverage and practice, not an official mock exam or a replacement for labs.

1. Choose a **10, 15, or 25 minute** daily target.
2. Work through due reviews, then new lessons. New lessons follow prerequisite order; reviews mix domains, prioritizing weak, overdue material and exam weight.
3. Attempt the recall prompt before revealing notes. Apply the idea to a small design exercise.
4. Answer scenario questions, including select-all questions. Read the explanation for every option.
5. A perfect first submission schedules the next review after **1, 3, 7, 14, then 30 days**. A miss returns in **10 minutes**. Early repeat passes do not advance the spacing ladder.
6. Progress distinguishes unseen, learning, due, and retained. Retained means three successful spaced checks and a current correct result; opening a lesson earns no mastery.

Daily targets are a planning aid; review estimates are three minutes and new lessons six. A fixed session queue keeps the day's work finite. Progress, notes, target, and study dates persist in the existing local settings database. Repeated practice uses the same small question bank, so retention here is a study signal only.

## Practical milestones beyond the app

- Build a data pipeline: ingest, validate, split without leakage, transform, and publish reusable features.
- Train a baseline: log dataset/code versions, tune, evaluate per class, explain errors, and register an approved model.
- Build a RAG prototype: compare chunks, embedding models, metadata filters, retrieval metrics, and grounded responses.
- Add an agent: isolate sessions, allowlist tools, make side effects idempotent, enforce permissions, and trace failures.
- Practice operations: choose an endpoint, plan scaling and rollback, detect drift, and estimate total cost.
- Practice security: explain role/resource/KMS policy interactions, private connectivity, audit trails, prompt injection, and sensitive data safeguards.

Use a sandbox and remove paid resources after hands-on work. The app's design exercises run offline and do not provision AWS resources.

## Completion and expansion

Blueprint coverage is established when all 107 skill IDs are mapped. Lesson completion, spaced retention, and actual exam readiness are separate milestones. Before booking, close hands-on gaps and use AWS's official practice resources. Expand this starter with additional independent scenarios, executable labs, and full timed practice; keep skill IDs stable and recheck AWS sources when the exam changes.
