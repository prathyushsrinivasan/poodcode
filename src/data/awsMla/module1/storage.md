## Start with the prediction, then trace the data

Imagine a retailer predicting whether an order will be returned. At checkout, the system knows the customer, basket and product images. The return outcome arrives weeks later. **A training example is a snapshot of what was knowable at checkout, paired with the eventual outcome.** Copying today's database into a table is not enough: today's product category or customer history may differ from what existed then.

The pipeline has three useful stages: preserve source data, prepare consistent examples, and publish a versioned training dataset. A raw area retains source records so a transformation can be repaired and rerun. A curated area contains validated tables, and a training snapshot fixes the exact inputs used by an experiment. These are logical responsibilities; separate S3 prefixes or buckets can implement them. Record source version, extraction time, schema and transformation version in a manifest. Reproducibility needs those details as well as the model's code.

**Snapshot extraction** captures a database at a point in time. **Change data capture (CDC)** records subsequent inserts, updates and deletes. For a nightly historical dataset, a supported RDS snapshot export avoids running a large analytical query against the live database and writes Parquet to S3. For frequent updates, AWS DMS can perform an initial load and CDC for supported sources. Establish a consistent starting position and reconcile deletes; an append-only copy of updates is not automatically the latest database state. DynamoDB also supports export to S3 using point-in-time recovery, subject to its export prerequisites.

## Choose storage by the operations it must support

An object is fetched through an API by key; a block volume behaves like a disk; a file system provides paths and file operations. These differences explain the service choices better than memorizing names.

| Requirement | Starting choice | Reason and tradeoff |
| --- | --- | --- |
| Durable raw files, images and training snapshots | Amazon S3 | Many independent readers can fetch objects; applications must use supported object access rather than assume arbitrary local disk updates. |
| A disk for one EC2 training machine | Amazon EBS | Suitable for local working data; a volume is tied to an Availability Zone and attachment constraints. |
| Shared Linux files for multiple machines | Amazon EFS | Managed NFS semantics; check throughput and latency against the actual workload. |
| High-throughput parallel training over shared files | Amazon FSx for Lustre | Parallel file access and S3 integration; additional provisioning and cost need justification. |
| Operational relational records with transactions | Amazon RDS or Aurora | SQL relationships and updates; extract an analytical copy when broad training scans would burden production. |
| Operational key-based reads and writes | Amazon DynamoDB | Design around partition keys and access patterns; broad relational joins need another processing layer. |

The same solution can use several services. Orders may originate in RDS, land in S3, and be read through FSx during repeated training. The question is which responsibility each component serves. Storing images as large database blobs merely because orders are relational couples two very different access patterns. A table containing an image's S3 key, checksum, content type, label and source version is usually easier to operate.

Storage selection also includes access and retention. S3 encryption at rest does not grant a role permission to read objects. SSE-KMS access may additionally require key permissions. Lifecycle transitions can reduce long-term cost but an archival class may require restoration before training. Versioning retains earlier objects; Object Lock addresses protected retention when that is required. Apply deletion and access policy to derived datasets as well as originals.

## File format and layout change the amount of work

CSV is convenient for flat interchange, but nested values and ambiguous types need conventions. JSON represents nested events naturally and repeats field names. Parquet and ORC organize values by column and retain schema information, so analytical engines can skip irrelevant columns. Compression reduces bytes; **column projection** reduces which columns are read; **partition pruning** skips whole groups selected by filters. These are different optimizations.

Suppose a table is 600 GB, distributed evenly across 30 dates and 100 equally sized columns. A query needs one date and five columns. An idealized estimate is `600 / 30 × 5 / 100 = 1 GB`. This is reasoning about potential data reduction, not an Athena billing prediction: compression, metadata, row groups, skew and the actual query engine affect real reads. A date predicate must match the partition layout for partition pruning to help.

For daily training, a prefix such as `curated/orders/event_date=2026-10-01/part-000.parquet` is useful. A separate partition for every unique customer can produce many tiny files and expensive metadata work. Compact small objects into sensibly sized files based on measured read parallelism. A `.parquet` filename does not convert JSON content; a writer must serialize the data into that format.

## Worked example: a join that silently changes your dataset

Orders contain `(o1, p7)` and `(o2, p7)`. The product table contains two versions: `(p7, old_category)` and `(p7, new_category)`. Joining only on product ID produces four rows: each order matches both product records. Compression and more memory cannot repair this semantic error.

First declare the intended row grain: one row per order, or perhaps one row per order line. Then validate key uniqueness at that grain. If product history matters, join on product ID **and** the version whose validity interval includes checkout time. If only one current record is intended, construct that table deliberately before joining. Compare row counts, distinct order counts, unmatched keys and label proportions before publishing. Deleting duplicate order IDs afterward can choose the wrong historical values.

For our retailer, preserve raw order events and images in S3, extract a consistent product history, perform a time-aware join, and publish compact date-partitioned Parquet plus an immutable dataset manifest. The decisive checks are the prediction-time boundary and row grain. The storage and format choices make this correct dataset efficient to consume.
