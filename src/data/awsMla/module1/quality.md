## Define what one valid record means

Before training, establish a data contract: schema, units, required fields, allowed values, row grain and freshness. “Amount is numeric” does not tell you whether it is dollars or cents. “Customer ID is present” does not establish that the customer exists. A useful quality gate translates each assumption into an observable check and a response when it fails.

| Check | Example failure | Useful response |
| --- | --- | --- |
| Schema and type | A numeric amount arrives as `"unknown"` | Reject or quarantine incompatible rows and alert the producer. |
| Completeness | A required order ID is null | Prevent records without identity from entering a keyed training dataset. |
| Range and units | Age is -5, or cents are mistaken for dollars | Investigate the producer contract before coercing values. |
| Uniqueness at the intended grain | An order event is replayed twice | Deduplicate by the documented business/event key. |
| Referential integrity | An order references a missing product | Resolve extraction timing or quarantine an unmatched relationship. |
| Freshness and volume | A feed stops, or a full day is duplicated | Compare event dates, arrival lag and counts against expectations. |

The response depends on impact. A missing optional display label might be acceptable with a documented default. A missing target label cannot be invented for supervised evaluation. A small batch with invalid IDs can be quarantined; a widespread unit change should block publication of the batch. Retain rejected records and diagnostic reasons so the producer can repair them.

## Read a small data-quality ruleset

AWS Glue Data Quality uses Data Quality Definition Language (DQDL) to express rules. Here is a small example for a table whose declared grain is one row per order:

```text
Rules = [
  IsComplete "order_id",
  IsUnique "order_id",
  ColumnValues "amount" >= 0,
  Completeness "customer_id" >= 0.99
]
```

`IsComplete` requires every order ID to be populated. `IsUnique` checks uniqueness. The range rule rejects a negative amount under this example's business contract. The last rule requires at least 99% customer-ID completeness. On 1,000 rows with 20 missing customer IDs, completeness is `980 / 1000 = 0.98`, so that rule fails. This is a dataset-level rule outcome; identifying individual bad rows and deciding whether to stop the pipeline require explicit handling in the job.

These rules do not cover every failure. A refund dataset may legitimately contain negative amounts. An order-line table can legitimately repeat order IDs and instead needs a composite key. Passing yesterday's rules does not establish that today's schema and business meaning are still correct. Profile distributions, accepted/rejected counts and source freshness as well as evaluating rules.

## Missing values, outliers and duplicates need explanations

Missingness can mean “not measured,” “not applicable,” “not yet arrived” or “a broken source.” Replacing all of these with zero collapses different meanings. Zero purchases is a real behavioral value; unknown purchases are uncertainty. A numeric imputer can use a training-only median and a missingness indicator, but evaluate whether the absence itself changes with deployment. Dropping rows can bias the sample if missingness is concentrated in a particular population.

For training values 10, 20, 30 and missing, the median is 20. Save that fitted parameter and apply it to validation, test and serving. Do not calculate separate holdout medians; that changes the pipeline and uses evaluation information. For a categorical field, an explicit unknown category may be more honest than pretending the most common category is known.

An outlier may be a data error or the valuable rare event the system must detect. A $50,000 purchase deserves investigation, not automatic deletion in a fraud dataset. Compare the source, units and business process; then choose removal, capping, transformation or retention with a documented rationale. Fit any learned capping thresholds only on training data.

Deduplication also needs a semantic key. Two identical purchases by one customer may be real; two deliveries of the same event ID are retries. Deduplicate and group related examples before splitting so a copied event, duplicated document or near-identical image does not appear on both sides of evaluation. Keep an audit trail of which source records were retained.

## Labels and prompt-response pairs require semantic quality

A label is supervision: it tells the model what outcome to learn. Human annotators need a written definition, positive and negative examples, ambiguous cases and an escalation path. For “damaged item,” decide whether cosmetic packaging damage counts. Give several annotators overlapping examples and inspect disagreement. If two reviewers agree on 80 of 100 labels, raw agreement is 80%; that alone does not account for chance or prove that either reviewer is correct. Review ambiguous cases and use adjudication to improve the guideline.

Labels may also be delayed or selectively observed. A transaction not yet confirmed fraudulent is not automatically a legitimate transaction. Define a label maturation window and avoid constructing evaluation before outcomes are sufficiently complete. If only investigated cases get labels, the training set can reflect the investigation policy rather than all customer transactions.

For generative AI, a prompt-response record can satisfy every JSON and schema rule while containing a wrong or unrelated answer. Check instruction relevance, factual grounding, output format, harmful content and sensitive-data exposure. Deterministic validators can check fields and parsable JSON; semantic correctness may require carefully reviewed labels or human assessment. The course's quizzes use authored choice answers so your responses can be graded exactly without asking an AI to judge your writing.

The publication gate should emit a report: input version, rule version, total rows, failures by rule and subgroup, label readiness and output dataset version. Quality is a decision about fitness for a specific task, supported by checks; it is not a claim that every accepted record is perfect.
