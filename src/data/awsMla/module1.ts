import type { AwsLesson, AwsQuestion, AwsResource, AwsTeaching } from "./syllabus";
import storage from "./module1/storage.md?raw";
import ingestion from "./module1/ingestion.md?raw";
import features from "./module1/features.md?raw";
import documents from "./module1/documents.md?raw";
import quality from "./module1/quality.md?raw";
import bias from "./module1/bias.md?raw";

function teaching(body: string, objectives: string[], minutes = 25): AwsTeaching {
  return {
    minutes, objectives,
    sections: body.trim().split(/^## /m).filter(Boolean).map((part, index) => {
      const newline = part.indexOf("\n");
      return { id: `topic-${index + 1}`, title: part.slice(0, newline).trim(), body: part.slice(newline + 1).trim() };
    }),
  };
}

const doc = (title: string, path: string, focus: string): AwsResource => ({
  title, url: `https://docs.aws.amazon.com/${path}`, kind: "Documentation", focus,
});
const video = (title: string, id: string, focus: string, note?: string): AwsResource => ({
  title, url: `https://www.youtube.com/watch?v=${id}`, kind: "Video", focus, note,
});
function q(id: string, skills: string[], section: string, prompt: string, options: [string, string][], answers: number[]): AwsQuestion {
  return { id: `m1-${id}`, skills, section, prompt, options: options.map(([text, why]) => ({ text, why })), answers };
}

// Stable lesson IDs preserve existing navigation and locally saved notes/history.
// Expanded content is explicit: later domains remain introductory outlines.
export const AWS_MODULE_ONE: Record<string, Pick<AwsLesson, "teaching" | "references" | "questions">> = {
  "storage-and-formats": {
    teaching: teaching(storage, [
      "Trace a prediction back to consistent, versioned source records.",
      "Choose object, block, shared-file and database storage from access requirements.",
      "Estimate column/partition pruning and repair a join at the intended row grain.",
    ]),
    references: [
      video("AWS re:Invent 2024: Dive deep on Amazon S3 (STG302)", "NXehLy7IiPM", "Explore object access, performance and storage design after the storage comparison.", "Recorded in 2024; use the documentation for current options and quotas."),
      doc("RDS snapshot exports", "AmazonRDS/latest/UserGuide/USER_ExportSnapshot.html", "Read how supported snapshots export to S3, and the role and KMS prerequisites."),
      doc("Athena columnar formats", "athena/latest/ug/columnar-storage.html", "Connect column projection and compression to the scan calculation."),
      doc("DynamoDB export to S3", "amazondynamodb/latest/developerguide/S3DataExport.HowItWorks.html", "Compare table export prerequisites with scanning an operational table."),
      doc("FSx for Lustre", "fsx/latest/LustreGuide/what-is.html", "Review parallel shared-file storage and its S3 relationship."),
      doc("S3 Object Lock", "AmazonS3/latest/userguide/object-lock.html", "Distinguish protected retention from ordinary object versioning."),
    ],
    questions: [
      q("storage-snapshot", ["1.1.1"], "topic-1", "A supported RDS database is busy serving checkout requests. A team needs yesterday's consistent snapshot in S3 for nightly analytics, with minimal extra load on the live instance. Which starting approach fits?", [
        ["Run a full-table analytical join on the live instance every hour", "This adds production load and does not use the available point-in-time snapshot."],
        ["Export the supported RDS snapshot to S3", "The export reads the snapshot rather than issuing a full analytical scan against the live instance; validate export permissions and support."],
        ["Use CDC alone without an initial baseline", "Changes alone cannot reconstruct records that existed before capture began."],
        ["Read successive pages from the live database without a consistent snapshot", "Concurrent updates can make pages inconsistent with each other."],
      ], [1]),
      q("storage-files", ["1.1.2"], "topic-2", "A distributed training workload repeatedly reads the same S3-backed data and requires high-throughput parallel POSIX file access. Benchmarking justifies a managed parallel file system. Which option best fits?", [
        ["Use one EBS volume as a general-purpose shared file system across all workers", "EBS is block storage with attachment constraints, rather than the managed parallel file system requested."],
        ["Move the dataset into RDS and query each training minibatch", "This replaces file access with database reads and adds an unsuitable serving path."],
        ["Evaluate FSx for Lustre with S3 integration", "It is built for parallel file workloads; verify throughput, topology and cost for the job."],
        ["Keep the files only on one worker's instance-local disk", "Other workers do not gain a managed shared file system and the working copy is coupled to that worker."],
      ], [2]),
      q("storage-scan", ["1.1.5"], "topic-3", "A 600 GB table is evenly split across 30 date partitions and 100 equally sized columns. A query selects one date and five columns. Ignoring metadata and compression, what idealized amount of column data is needed?", [
        ["1 GB", "600 / 30 gives 20 GB for the date; five of 100 columns gives 1 GB. Real scans depend on layout and the engine."],
        ["20 GB", "This accounts for the date filter but ignores column projection."],
        ["30 GB", "This projects five columns from the whole table but ignores the date partition."],
        ["600 GB", "This assumes neither partition pruning nor column projection works."],
      ], [0]),
      q("storage-join", ["1.1.6"], "topic-4", "Two orders reference product p7. Product history has an old and a new row for p7. Joining on product ID produces four rows, but the target grain is one row per order at checkout. Which repair preserves the intended meaning?", [
        ["Keep any two rows after the join", "Arbitrary truncation can associate an order with the wrong product version."],
        ["Convert the joined result into Parquet", "Changing format preserves the incorrect four-row result."],
        ["Drop the order ID so all four examples appear unique", "Hiding identity makes validation harder and leaves duplicated supervision."],
        ["Join product ID and the product version valid at each order's checkout time", "The temporal condition selects the relevant historical record instead of matching both versions."],
      ], [3]),
      q("storage-images", ["1.1.8"], "topic-2", "Product images change over time and training must be reproducible. Which TWO practices support a reliable multimodal dataset?", [
        ["Keep versioned image objects with checksums and source metadata", "This identifies the exact bytes and provenance used in training."],
        ["Store only a mutable public URL and assume its content stays the same", "The referenced image can change or disappear without a dataset revision."],
        ["Include the image version/key and label relationship in the training manifest", "The manifest ties the asset to the example and preserves reproducibility."],
        ["Remove object versions as soon as model training finishes regardless of retention needs", "Unconditional deletion can prevent reproduction and violate required retention."],
      ], [0, 2]),
      q("storage-retention", ["1.1.2"], "topic-2", "A dataset has mandatory protected retention for seven years but must remain immediately available for monthly retraining. Which design addresses both constraints?", [
        ["Use versioning alone as the protected-retention control", "Version history is useful, but is not the same control as enforced retention."],
        ["Configure the required Object Lock retention and choose a storage class meeting retrieval needs", "Retention protection and access latency are separate requirements; satisfy and validate both."],
        ["Move everything to a restore-required archive and assume immediate reads", "A restore step conflicts with the immediate-read requirement."],
        ["Allow every training role to delete versions to simplify reruns", "Broad deletion rights conflict with protected-retention requirements."],
      ], [1]),
    ],
  },
  "streams-vectors-features": {
    teaching: teaching(ingestion, [
      "Separate transport, stateful processing and low-latency serving.",
      "Diagnose hot keys, lag and backpressure, and design replay-safe operations.",
      "Distinguish historical features, latest-entity lookups and vector similarity search.",
    ]),
    references: [
      video("AWS re:Invent 2023: Serverless data streaming (COM308)", "HjoQllOWRmM", "Follow the Kinesis/Lambda ingestion path and think about retries and consumer throughput.", "Recorded in 2023; current capacity modes and limits are in the documentation."),
      doc("Kinesis quotas and limits", "streams/latest/dev/service-sizes-and-limits.html", "Check current capacity-mode and shard limits before sizing a real stream."),
      doc("Flink application best practices", "managed-flink/latest/java/best-practices.html", "Review operational practices for state, checkpoints and reliable stream applications."),
      doc("SageMaker Feature Store", "sagemaker/latest/dg/feature-store.html", "Compare online latest-record access with offline historical records."),
      doc("Amazon S3 Vectors", "AmazonS3/latest/userguide/s3-vectors.html", "Check supported vector queries, filtering and constraints rather than assuming database parity."),
    ],
    questions: [
      q("ingest-hot-key", ["1.1.3"], "topic-2", "One tenant's partition key receives most writes and throttles while other partitions have spare capacity. Per-tenant total ordering is not required, but per-device ordering is. What should be investigated first?", [
        ["Spread the tenant's events by device while preserving device ordering", "More key diversity can relieve the hot route while retaining the stated ordering boundary."],
        ["Add more readers without changing the write-key distribution", "Readers do not repair a hot write route."],
        ["Increase the downstream database's storage capacity only", "No evidence points to destination storage as the cause of producer throttling."],
        ["Increase stream retention only", "Retention changes replay history, not hot-key write distribution."],
      ], [0]),
      q("ingest-byte-limit", ["1.1.3"], "topic-2", "For this exercise a partition allows 1,000 records/s and 1 MB/s. It receives 700 records/s at 2 KB each, using decimal units. Which conclusion follows?", [
        ["It is below both limits because 700 is less than 1,000", "The record limit is not the only capacity constraint."],
        ["It exceeds the record limit but not the byte limit", "700 is below 1,000 and the data rate is approximately 1.4 MB/s."],
        ["It exceeds the byte limit even though the record rate is below its limit", "700 × 2 KB is 1,400 KB/s, approximately 1.4 MB/s under the stated assumptions."],
        ["Its write capacity doubles if consumers checkpoint more often", "Checkpointing does not double the assumed producer write limits."],
      ], [2]),
      q("ingest-replay", ["1.1.4"], "topic-3", "After a consumer restarts, a $20 purchase event is delivered again. The feature is a running spend total. Which TWO measures support correct replay?", [
        ["Treat every delivery as a new purchase", "At-least-once delivery can repeat one event, inflating the total."],
        ["Keep stable event IDs and a deduplication policy covering the replay horizon", "Identity plus appropriately retained deduplication state allows repeated deliveries to be recognized."],
        ["Discard event times and aggregate only by arrival time", "This changes window semantics and does not identify a duplicate."],
        ["Use an idempotent sink/update strategy consistent with checkpoint recovery", "End-to-end correctness must account for external effects as well as replay positions."],
      ], [1, 3]),
      q("ingest-feature-record", ["1.1.9"], "topic-4", "A fraud API needs latest customer features in milliseconds, while a training job needs historical records as of each checkout. Which design fits?", [
        ["Use only the latest online record to construct every historical training row", "Today's state can include information unavailable at historical checkout."],
        ["Use online lookup for serving and offline history with point-in-time selection for training", "Each path uses the suitable store, and training still explicitly enforces historical availability."],
        ["Issue vector nearest-neighbor queries for exact customer IDs", "Similarity search answers a different question from entity-key lookup."],
        ["Scan the entire offline history for every synchronous checkout request", "A broad historical scan is unsuitable for the stated latency requirement."],
      ], [1]),
      q("ingest-embedding-model", ["1.1.7"], "topic-4", "An index contains 768-dimensional vectors from model A. Model B also produces 768 dimensions. May the application immediately use B for queries against the old index?", [
        ["Yes, identical vector length establishes semantic compatibility", "Dimension agreement is necessary but does not mean the coordinate spaces match."],
        ["Yes, if the nearest-neighbor result has a large score", "A score in an incompatible representation is not evidence of relevance."],
        ["No, every model replacement requires a larger dimension", "Models can share a dimension while having different representations."],
        ["Only if compatibility is established; otherwise regenerate document vectors and use a compatible index", "Query and indexed content must use compatible embedding paths, not merely matching vector lengths."],
      ], [3]),
      q("ingest-service", ["1.1.4"], "topic-1", "A team only needs buffered delivery of incoming events to S3 and accepts delivery latency. It has no custom replay consumer or stateful aggregation. Which managed starting point most directly meets the requirement?", [
        ["Amazon Data Firehose", "Buffered destination delivery is the stated need; still configure errors, duplicates and buffering."],
        ["A Flink application solely to forward unchanged records", "Flink can process streams but adds a computation layer the requirement does not need."],
        ["A custom Kafka cluster with hand-written S3 consumers", "This can work but adds operational work without a stated Kafka or custom-consumer requirement."],
        ["The Feature Store online store alone", "A latest-feature serving store is not the buffered event-delivery service requested."],
      ], [0]),
    ],
  },
  "feature-engineering": {
    teaching: teaching(features, [
      "Select a transformation engine from execution and state requirements.",
      "Calculate scaling and standardization using training-only parameters.",
      "Find preprocessing, entity and prediction-time leakage.",
    ]),
    references: [
      video("AWS re:Invent 2022: Data preparation with SageMaker Data Wrangler", "Slq3i8EeRXI", "See a visual preparation workflow and identify the transformations that need saved parameters.", "Historical interface: current Data Wrangler workflows are documented through SageMaker Canvas."),
      doc("Data Wrangler", "sagemaker/latest/dg/data-wrangler.html", "Read the current entry point and how preparation flows become repeatable jobs."),
      doc("Glue ETL jobs", "glue/latest/dg/etl-jobs-section.html", "Compare managed ETL execution with the other transformation engines."),
      doc("Prepare data with SageMaker Processing", "sagemaker/latest/dg/processing-job.html", "Review managed processing jobs for preparation within ML workflows."),
      { title: "scikit-learn: common pitfalls and recommended practices", url: "https://scikit-learn.org/stable/common_pitfalls.html", kind: "Documentation", focus: "Read inconsistent preprocessing and data leakage, including split-before-fit examples." },
    ],
    questions: [
      q("features-scaling", ["1.2.4"], "topic-2", "A min-max scaler is fit on training values with minimum 10 and maximum 50. Clipping is disabled. What should the saved scaler output for a production value of 70?", [
        ["0.7", "This divides by 100, which is not the fitted min-max formula."],
        ["1.0 after silently updating the training maximum to 70", "Updating parameters during inference changes the learned representation."],
        ["1.5", "(70 - 10) / (50 - 10) = 1.5. Out-of-range production inputs can map outside 0–1."],
        ["0.5", "0.5 would be the transformation of 30 under these parameters."],
      ], [2]),
      q("features-standardize", ["1.2.4"], "topic-2", "Training mean is 40 and standard deviation is 10. What is the standardized value of 60?", [
        ["2", "(60 - 40) / 10 = 2, two training standard deviations above the mean."],
        ["6", "This divides the value by the deviation without subtracting the mean."],
        ["20", "This centers the value but does not scale it."],
        ["0.5", "This is not the result of the stated standardization formula."],
      ], [0]),
      q("features-fit", ["1.2.2", "1.2.4"], "topic-3", "A pipeline computes imputation medians and category vocabularies before splitting into train, validation and test. Which change fixes the leakage?", [
        ["Compute separate fitted preprocessing parameters for every split", "This still lets evaluation data determine its own transformation and differs from deployment."],
        ["Remove test labels but keep the preprocessing order", "Unsupervised fitted preprocessing can leak information without labels."],
        ["Fit preprocessing once per production batch", "This introduces a changing serving representation instead of preserving training parameters."],
        ["Split appropriately, fit on training, and reuse the fitted pipeline for holdouts and serving", "Holdouts remain independent and inference uses the representation the model learned."],
      ], [3]),
      q("features-point-time", ["1.2.2"], "topic-4", "A device event occurred at 09:55 but arrived at 10:10. The training row simulates a prediction made at 10:00. Which rule most honestly reconstructs the deployed system?", [
        ["Include it because event time is before 10:00", "That ignores whether the system could actually access it at prediction time."],
        ["Exclude it from that prediction because it was not available by 10:00", "An honest historical reconstruction accounts for availability as well as event timestamp."],
        ["Include every event from the same calendar day", "Daily membership does not enforce a 10:00 prediction boundary."],
        ["Use today's latest customer feature row", "Latest state can contain future information relative to the historical prediction."],
      ], [1]),
      q("features-engine", ["1.2.1", "1.2.3"], "topic-1", "A pipeline needs five-minute event-time windows, durable processing state, and an explicit late-event policy. Which engine most directly fits?", [
        ["Independent Lambda invocations with only local in-memory counters", "Local invocation memory is not durable shared window state."],
        ["A one-time Glue crawler", "A crawler discovers metadata rather than running stateful event-time computation."],
        ["Amazon Managed Service for Apache Flink", "Flink supports stateful streaming and event-time processing; configure watermarks, checkpoints and sinks."],
        ["A nightly visual profile alone", "A batch profile does not provide the required continuous window computation."],
      ], [2]),
      q("features-split", ["1.2.2"], "topic-3", "A hospital wants to predict outcomes for patients unseen during training. There are multiple visits per patient. Which split best matches this objective?", [
        ["Keep all visits for each patient in one split", "Grouping prevents the same patient's records from crossing the train/evaluation boundary."],
        ["Randomly split individual visits while preserving class balance", "Class balance does not prevent patient-specific information from leaking across splits."],
        ["Oversample patients first and then split visits randomly", "Copied or related examples can appear across the boundary."],
        ["Choose the split with the highest test score after trying many seeds", "Selecting against test scores turns the test set into a tuning signal."],
      ], [0]),
    ],
  },
  "rag-and-customization-data": {
    teaching: teaching(documents, [
      "Preserve meaning while extracting, normalizing and chunking domain documents.",
      "Track embedding compatibility, document versions and enforced access metadata.",
      "Distinguish retrieval corpora, customization examples and held-out evaluations.",
    ]),
    references: [
      { title: "AWS: Advanced parsing, chunking and query reformulation", url: "https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-advanced-parsing-chunking-and-query-reformulation-giving-greater-control-of-accuracy-in-rag-based-applications/", kind: "Article", focus: "Compare parsing and chunking strategies against the return-policy example.", note: "Published July 2024; use current documentation for supported models and configuration." },
      doc("Bedrock knowledge-base chunking", "bedrock/latest/userguide/kb-chunking.html", "Compare fixed-size, semantic, hierarchical and multimodal chunking behavior."),
      doc("Prepare customization data", "bedrock/latest/userguide/model-customization-prepare.html", "Check model-specific dataset formats; the lesson examples are conceptual, not upload schemas."),
      doc("Retrieve from a knowledge base", "bedrock/latest/userguide/kb-test-retrieve.html", "Review retrieval configuration and metadata filters used to narrow authorized results."),
    ],
    questions: [
      q("rag-chunk", ["1.2.6", "1.2.7"], "topic-2", "A policy says opened items are accepted only if defective. Retrieval often returns 'opened items are accepted' without the condition. What is the most targeted first experiment?", [
        ["Increase generation temperature while leaving retrieved evidence unchanged", "Sampling cannot restore the missing condition in the retrieved evidence."],
        ["Preserve the complete rule and exception in a section-aware chunk and measure retrieval", "The failure points to a boundary separating meaning; test a controlled chunking change."],
        ["Remove headings and punctuation from every source", "This removes structure that could preserve the relationship."],
        ["Combine the entire policy library into one chunk", "This dilutes relevance and risks context limits rather than testing the specific failure."],
      ], [1]),
      q("rag-overlap", ["1.2.7"], "topic-2", "In a toy token sequence, chunk one covers tokens 1–100. With chunk size 100 and overlap 20, where does chunk two begin?", [
        ["Token 101", "This creates no overlap."],
        ["Token 21", "This would repeat 80 tokens, not 20."],
        ["Token 121", "This creates a gap rather than an overlap."],
        ["Token 81", "The stride is 100 - 20 = 80; tokens 81–100 occur in both chunks."],
      ], [3]),
      q("rag-compatible", ["1.2.5"], "topic-3", "An assistant changes from 1,024-dimensional document embeddings to a 768-dimensional model for its queries. What must the migration address?", [
        ["Regenerate document vectors with a compatible model path and configure the index accordingly", "The new query representation must match indexed content, including dimension and semantic space."],
        ["Truncate query vectors until requests stop failing", "Arbitrary coordinate manipulation does not establish a meaningful common representation."],
        ["Only increase the chat model's context window", "Context length does not repair incompatible retrieval vectors."],
        ["Pad query vectors with zeros and assume equivalent similarity", "Padding dimensions is not a model compatibility guarantee."],
      ], [0]),
      q("rag-private", ["1.2.7", "1.2.8"], "topic-3", "A multi-tenant assistant indexes private support policies. Which TWO controls belong in the data/retrieval design?", [
        ["Trust the tenant ID typed into the user's prompt", "An untrusted prompt field is not an authorization decision."],
        ["Derive tenant/access filters from trusted identity and enforce them during retrieval", "Unauthorized chunks should not be available to generation."],
        ["Redact unnecessary personal fields before embedding and protect derived artifacts", "Data minimization and access controls must cover vectors and logs too."],
        ["Retrieve every tenant's documents, then ask the model to hide confidential content", "Confidential evidence has already crossed the access boundary."],
      ], [1, 2]),
      q("rag-dataset-purpose", ["1.2.9"], "topic-4", "Which dataset objective is correctly matched to its method?", [
        ["Continued pretraining: a vector index refreshed at each user request", "That describes external retrieval, not training on domain material."],
        ["Supervised fine-tuning: any unlabeled document corpus regardless of task format", "Supervised customization needs examples fitting the model's input/output training contract."],
        ["Distillation: quality-filtered teacher behavior used to train a student", "Distillation transfers behavior; teacher output still needs correctness and quality checks."],
        ["RAG: changing model weights whenever a policy paragraph changes", "RAG updates external evidence rather than requiring a weight update."],
      ], [2]),
      q("rag-normalization", ["1.2.6", "1.2.9"], "topic-1", "A domain corpus contains identifiers such as ZX-41 and policy exceptions using 'not'. Which preprocessing policy is safest to evaluate first?", [
        ["Preserve domain identifiers, negation and structure while removing known extraction noise", "Normalization should preserve task meaning, then be tested on representative retrieval questions."],
        ["Remove every short token, punctuation mark and negative word", "Generic cleanup can destroy identifiers and reverse a statement's meaning."],
        ["Replace all domain terms with one generic token", "This loses distinctions that retrieval and task supervision need."],
        ["Normalize training text differently from query text without measuring compatibility", "Mismatched preprocessing can weaken the shared representation."],
      ], [0]),
    ],
  },
  "quality-and-labels": {
    teaching: teaching(quality, [
      "Turn a data contract into schema, completeness, key and freshness checks.",
      "Evaluate a DQDL rule and choose remediation from the failure's cause.",
      "Check label consistency and distinguish schema validity from semantic quality.",
    ]),
    references: [
      video("AWS Glue Data Quality overview", "pgue7jZrVNU", "See how quality checks fit into a pipeline; compare the workflow with the publication gate."),
      doc("DQDL reference", "glue/latest/dg/dqdl.html", "Read ruleset structure, rule types and dataset-level versus row-level behavior."),
      doc("Get started with Glue Data Quality", "glue/latest/dg/data-quality-getting-started.html", "Inspect a practical ruleset and reference-dataset checks."),
      doc("SageMaker Ground Truth", "sagemaker/latest/dg/sms.html", "Review labeling workflows alongside the lesson's guidelines and adjudication example."),
    ],
    questions: [
      q("quality-rule", ["1.3.1"], "topic-2", "A batch has 1,000 rows and 20 missing customer IDs. Its rule is Completeness customer_id >= 0.99. What is the result?", [
        ["Pass, because only 20 rows are missing", "The rule uses a fraction, not an absolute missing-row allowance."],
        ["Pass, because the schema contains a customer_id column", "Column existence does not establish non-null completeness."],
        ["Fail, because completeness is 0.98", "980 non-missing rows / 1,000 = 0.98, below the 0.99 threshold."],
        ["Fail only if all rows are missing customer IDs", "The stated threshold is stricter than merely having some non-null rows."],
      ], [2]),
      q("quality-grain", ["1.3.1", "1.3.7"], "topic-1", "A table intentionally contains multiple order lines per order. IsUnique order_id fails. What should happen before deleting records?", [
        ["Check the declared row grain and validate the appropriate composite key", "Repeated order IDs can be legitimate when each row is an order line."],
        ["Keep only one arbitrary line per order", "That discards valid products and changes the target dataset."],
        ["Remove the order ID column", "Deleting identity hides the problem instead of expressing the correct contract."],
        ["Convert every order ID to a random value", "Random values break relationships and do not repair the business key."],
      ], [0]),
      q("quality-imputation", ["1.3.7"], "topic-3", "Training values are 10, 20, 30 and missing. The chosen policy is median imputation. What value and deployment policy are appropriate?", [
        ["Zero, because all missing numeric values mean none", "Missing does not necessarily mean a measured zero."],
        ["The separate median of each validation and production batch", "This changes the representation and uses evaluation data to fit preprocessing."],
        ["30, using the maximum to avoid underestimating values", "This is not the selected median-imputation policy."],
        ["20, saved from training and reused on holdouts and serving", "20 is the training median; reusing the fitted parameter preserves the pipeline."],
      ], [3]),
      q("quality-labels", ["1.3.2"], "topic-4", "Reviewers disagree about whether cosmetic packaging damage counts as a damaged product. Which action most directly improves the supervision?", [
        ["Accept whichever reviewer submits first", "Submission speed does not resolve the label definition."],
        ["Clarify guidelines with examples, adjudicate ambiguous cases, and measure agreement", "The inconsistency is in the annotation contract and needs a repeatable resolution process."],
        ["Duplicate every conflicting example to increase dataset size", "More conflicting labels do not make the target definition consistent."],
        ["Tune the model until it memorizes both labels", "Training cannot make contradictory supervision reliable."],
      ], [1]),
      q("quality-semantic", ["1.3.6"], "topic-4", "An instruction dataset parses as JSON and has every required field. Several responses answer a different question. What additional gate is required?", [
        ["Only validate file extensions", "The extension does not assess whether a response follows its prompt."],
        ["Reject every long answer regardless of the request", "Length alone is not evidence of irrelevance or correctness."],
        ["Assess prompt-response relevance, grounding and safety with reviewed criteria", "Schema validity and semantic suitability are independent dimensions of quality."],
        ["Trust every answer generated by a large teacher model", "Teacher outputs can be fluent but unrelated or incorrect."],
      ], [2]),
      q("quality-outlier", ["1.3.7"], "topic-3", "A fraud dataset includes a $50,000 transaction. Which first response best protects dataset usefulness?", [
        ["Investigate source validity and units before choosing retention, transformation or removal", "A rare value may be either an error or exactly the important event the model must learn."],
        ["Delete all values above the mean", "This removes valid variation and is not a reasoned outlier policy."],
        ["Replace the value with the test-set average", "This uses evaluation information and obscures the source issue."],
        ["Relabel it as fraud solely because it is large", "Transaction size alone does not establish the outcome label."],
      ], [0]),
    ],
  },
  "bias-and-imbalance": {
    teaching: teaching(bias, [
      "Calculate precision, recall and error cost from a confusion matrix.",
      "Choose a threshold using validation, realistic prevalence and review capacity.",
      "Separate target imbalance from subgroup bias and avoid contaminated resampling.",
    ]),
    references: [
      video("AWS ML Heroes in 15: Detect bias and explain predictions", "fGCuDspOH7k", "Connect dataset slices and prediction explanations to the subgroup example.", "Historical Clarify demo: the service is now closed to new customers. Study the concepts and current alternatives."),
      doc("Clarify availability and alternatives", "sagemaker/latest/dg/clarify-availability-change.html", "Read the new-customer restriction and the currently documented alternative approaches."),
      doc("Bias metrics before training", "sagemaker/latest/dg/clarify-measure-data-bias.html", "Compare label imbalance and representation metrics with the distinction taught here."),
      { title: "scikit-learn: classification metrics", url: "https://scikit-learn.org/stable/modules/model_evaluation.html", kind: "Documentation", focus: "Check confusion matrices, precision, recall and precision-recall curves against the worked arithmetic." },
    ],
    questions: [
      q("bias-recall", ["1.3.5"], "topic-1", "A model detects 60 of 100 fraudulent transactions and produces 90 false fraud alerts. What are fraud precision and recall?", [
        ["Precision 60%, recall 40%", "This swaps denominators: precision concerns all predicted positives and recall all actual positives."],
        ["Precision 40%, recall 60%", "Precision is 60 / (60 + 90) = 40%; recall is 60 / 100 = 60%."],
        ["Precision 99%, recall 99%", "The majority class can dominate accuracy, not these fraud-specific rates."],
        ["Precision 60%, recall 90%", "False-alert count is not a recall percentage."],
      ], [1]),
      q("bias-cost", ["1.3.5"], "topic-2", "Threshold A has 40 missed frauds and 90 false alerts. Threshold B has 20 missed frauds and 300 false alerts. A miss costs $100 and a false alert $5. Ignoring capacity constraints, which has lower cost?", [
        ["A, because it has fewer false alerts", "Fewer false alerts alone ignores the more expensive missed frauds."],
        ["They have equal cost", "A costs $4,450; B costs $3,500."],
        ["A at $3,500", "$3,500 is B's cost, not A's."],
        ["B at $3,500", "20 × $100 + 300 × $5 = $3,500, below A's $4,450 under these stated assumptions."],
      ], [3]),
      q("bias-resampling", ["1.3.5"], "topic-3", "A team wants to oversample fraud examples and estimate performance at production's 1% prevalence. Which TWO practices preserve an honest evaluation?", [
        ["Split appropriately before resampling, and oversample training only", "This prevents copied minority examples crossing into the holdout."],
        ["Oversample all data before splitting to balance every set", "Copies can cross boundaries and contaminate evaluation."],
        ["Keep independent evaluation representative of operational prevalence", "Precision and alert volume depend on the population being evaluated."],
        ["Choose the threshold repeatedly against final test labels", "That turns final evaluation into tuning."],
      ], [0, 2]),
      q("bias-subgroup", ["1.3.3", "1.3.4"], "topic-4", "Group A has 90 true positives among 100 actual positives; group B has 10 among 20. What does reporting only overall recall conceal?", [
        ["Both groups necessarily have equal false-positive rates", "No false-positive counts are supplied, so that cannot be inferred."],
        ["Group B is performing better because it has fewer errors in absolute count", "Its denominator is smaller; counts alone hide the rate difference."],
        ["Recall is 90% for A and 50% for B despite about 83.3% overall", "100 / 120 is the aggregate; the group denominators reveal the performance gap."],
        ["Removing group identity from the report fixes the underlying bias", "Hiding the measurement does not repair data or model behavior."],
      ], [2]),
      q("bias-augmentation", ["1.3.3", "1.3.4"], "topic-3", "A text dataset is augmented by deleting short words. Positive and negative statements become near-identical after 'not' is removed. Which response fits?", [
        ["Require meaning-preserving augmentation and evaluate it by class and relevant slices", "The transformation can reverse the label's meaning; more examples are not useful if supervision is corrupted."],
        ["Keep the old labels because augmentation always preserves them", "Label preservation must be checked, not assumed."],
        ["Apply the same deletion to the test set and choose the best test score", "This does not repair corrupted meaning and uses the test set for selection."],
        ["Balance the two labels and ignore the changed text", "Equal label counts do not make contradictory examples valid."],
      ], [0]),
      q("bias-threshold", ["1.3.5"], "topic-2", "The lower-cost threshold creates 380 alerts per day, but reviewers can handle only 200. What should guide the final choice?", [
        ["Lowest arithmetic error cost alone, regardless of alert capacity", "A threshold that cannot be operated violates a stated requirement."],
        ["Validate thresholds against both error cost and review capacity, then evaluate the chosen policy on test", "Operational constraints and independent evaluation both belong in the decision."],
        ["Set the threshold using the highest test recall after many experiments", "Repeated selection on test contaminates the final estimate."],
        ["Choose the policy with the highest overall accuracy only", "Accuracy does not encode the rare-event costs or reviewer workload."],
      ], [1]),
    ],
  },
};
