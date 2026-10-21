import { bank } from "./schema";

export const relational = bank("relational", [
  ["resilience", "A production RDS for PostgreSQL database must automatically fail over if its Availability Zone becomes unavailable. Read scaling is not a requirement. Which configuration is the simplest fit?", [0], [
    ["An RDS Multi-AZ DB instance deployment with a standby in another AZ.", "RDS maintains a synchronous standby and manages failover for this high-availability configuration."],
    ["One larger Single-AZ DB instance.", "A larger instance remains dependent on one Availability Zone."],
    ["A daily snapshot with no standby.", "Snapshots support restore but cannot provide automatic standby failover."],
    ["An asynchronous read replica with only manual promotion procedures.", "This does not provide the requested managed automatic failover design."],
  ], "Distinguish a Multi-AZ DB instance standby for availability from a read replica for read scaling."],
  ["performance", "An RDS MySQL application has many read-only reports. The primary instance's CPU is saturated by these reads, but write demand is modest. What change most directly scales reads?", [0], [
    ["Create read replicas and route eligible reporting queries to them.", "Read replicas offload read-only queries; the application must use the replica endpoints."],
    ["Send reporting traffic to a Multi-AZ DB instance standby endpoint.", "The standby of a Multi-AZ DB instance deployment cannot serve read queries."],
    ["Increase the backup retention period.", "Longer backup retention does not add read-serving capacity."],
    ["Increase primary storage without adding compute or read-serving replicas.", "Additional allocated storage alone does not offload CPU-intensive reporting queries from the primary."],
  ], "Read replicas generally replicate asynchronously, so route only reads that can tolerate replica lag."],
  ["resilience", "An Aurora cluster has a writer and readers in different AZs. The writer fails. The application should reconnect to the new writer without hard-coded instance addresses. Which endpoint should writes use?", [0], [
    ["The Aurora cluster endpoint with connection retry and DNS refresh handling.", "The cluster endpoint tracks the current primary writer after failover."],
    ["The failed writer's instance endpoint permanently.", "An instance endpoint identifies that instance instead of following the writer role."],
    ["The Aurora reader endpoint for all writes.", "The reader endpoint is intended to distribute read connections, not direct writes."],
    ["A public IP copied from the original database host.", "Hard-coded addresses do not follow managed failover and can change."],
  ], "Use role-appropriate managed endpoints and implement reconnect behavior; an endpoint does not keep a broken connection alive."],
  ["performance", "Thousands of short-lived Lambda invocations connect to RDS. Connection setup and too many simultaneous database connections cause failures. Which service most directly helps?", [0], [
    ["Amazon RDS Proxy.", "RDS Proxy pools database connections and helps applications handle bursts and database failovers."],
    ["A Multi-AZ DB instance standby used as the connection pool.", "A standby provides availability but does not pool client connections or serve application traffic normally."],
    ["Increase Lambda reserved concurrency without changing database access.", "Allowing more simultaneous invocations can increase connection pressure on the database."],
    ["Shorten every function's database connection timeout to one millisecond.", "Failing connections faster does not reduce setup cost or provide reusable pooled sessions."],
  ], "RDS Proxy manages connections; it does not remove the need to size queries, transactions and database compute."],
  ["resilience", "A developer deletes important rows from an RDS database at 14:10. Automated backups were enabled before the incident. The team needs a database representing 14:09. What should it do?", [0], [
    ["Perform point-in-time recovery to a new DB instance at a supported time before the deletion.", "RDS PITR creates a separate instance using backups and transaction logs within the retention window."],
    ["Reboot the current instance to undo committed deletes.", "A reboot does not reverse committed database transactions."],
    ["Fail over to the synchronous standby expecting the rows to remain.", "Committed deletions replicate to the standby; availability replicas are not historical backups."],
    ["Enable backups now and restore to any time in the past.", "Backups cannot reconstruct a period for which recovery data was never retained."],
  ], "Availability replicas also replicate logical mistakes; use historical recovery and plan how to reconcile later legitimate changes."],
  ["performance", "A company migrates a large supported relational database to RDS. The source must remain writable until a short final cutover. Which AWS service supports initial loading followed by ongoing change replication?", [0], [
    ["AWS Database Migration Service with full load and change data capture.", "DMS can copy existing data and replicate supported ongoing changes before cutover."],
    ["A single manual CSV export taken a month before cutover.", "A one-time export omits subsequent source changes."],
    ["DataSync copying the live database's storage files while transactions continue.", "File synchronization alone does not provide a supported transaction-aware full-load and CDC migration."],
    ["S3 Cross-Region Replication alone.", "S3 replication copies objects, not live relational database changes."],
  ], "DMS can reduce migration downtime; validate schema conversion, source prerequisites and replication lag before cutover."],
  ["security", "An RDS database is in private subnets. Only the application tier should connect, and the database must not be publicly reachable. Which TWO settings implement these network boundaries?", [0, 1], [
    ["Disable public accessibility and use an appropriate private DB subnet group.", "This avoids exposing a public database endpoint through public network placement."],
    ["Allow the database port only from the application tier's security group.", "A tier-specific source restricts which application instances can initiate connections."],
    ["Allow the database port from 0.0.0.0/0.", "This is broader than the required application-only boundary."],
    ["Enable database authentication controls but leave network access open to every source.", "Database authentication is useful but does not implement the requested application-tier network restriction."],
    ["Enable encryption at rest and make the database publicly accessible.", "Encryption protects stored data but does not remove the public network path."],
  ], "Use private placement and narrow security group access together; database user permissions remain a separate layer."],
  ["performance", "A reporting service repeatedly runs the same expensive query. Results may be up to five minutes old. Which change reduces database read load with the least query-engine redesign?", [0], [
    ["Cache query results in ElastiCache with an appropriate expiration and invalidation strategy.", "A cache can serve repeated reads without reexecuting the expensive query every time."],
    ["Run every query twice to warm the primary instance.", "Duplicating work adds database load rather than reducing it."],
    ["Increase the number of synchronous standby copies and query them all.", "Standbys in a Multi-AZ DB instance deployment are not readable query targets."],
    ["Turn off SQL indexes so writes finish sooner.", "Removing useful indexes can make these expensive reads slower."],
  ], "Caching is useful when data reuse and permitted staleness justify it; invalidation and expiry are part of the design."],
  ["resilience", "A company needs regional disaster recovery for an Aurora database with a very low recovery point objective and lower cross-Region replication lag than application-managed log shipping. Which feature is designed for this?", [0], [
    ["Aurora Global Database.", "Global Database uses storage-based cross-Region replication for regional reads and disaster recovery."],
    ["Only an additional reader in the same Region.", "A same-Region reader does not provide an independent regional recovery copy."],
    ["A larger connection pool on the original writer.", "Connection pooling does not replicate data to another Region."],
    ["Weekly CSV exports as the only recovery copy.", "Weekly exports leave a much larger potential data-loss window."],
  ], "A global database supports regional recovery, but asynchronous replication can still lose recent writes during an unplanned failover."],
  ["cost", "A development team runs RDS only during working hours. It can tolerate startup time, must preserve its data, and wants to reduce compute charges during nights and weekends. Which action is appropriate?", [0], [
    ["Schedule supported DB instances to stop and start, accounting for automatic restart limits.", "Stopping eligible instances pauses instance-hour charges, while storage and backup charges can remain."],
    ["Delete the database nightly without taking backups.", "Deleting without a recoverable copy violates the data-preservation requirement."],
    ["Assume stopped databases have no charges of any kind.", "Allocated storage and applicable backup charges continue even while compute is stopped."],
    ["Move the database to a larger instance for idle periods.", "Increasing instance size does not reduce idle compute costs."],
  ], "Schedule nonproduction compute where supported; RDS stopped instances automatically restart after the supported maximum stop period."],
]);

export const nosql = bank("nosql", [
  ["performance", "A shopping cart service needs a managed key-value database with predictable low-millisecond access at large scale. Requests retrieve carts by customer ID and do not require relational joins. Which service best fits?", [0], [
    ["Amazon DynamoDB with a key design matching cart access.", "DynamoDB supports managed key-value workloads and scales without managing database servers."],
    ["An S3 Glacier archive restored for every cart request.", "Archive retrieval cannot satisfy interactive low-latency reads."],
    ["A Redshift warehouse queried for every cart update.", "A warehouse is optimized for analytical queries rather than this transactional key-value pattern."],
    ["A single local JSON file on one web instance.", "A local file does not provide the required managed scalable availability."],
  ], "Start database selection with access patterns and consistency needs rather than treating every dataset as relational."],
  ["performance", "A DynamoDB table uses a constant partition key for all new events. One write-heavy partition is throttled while other capacity is unused. Which design change most directly addresses the bottleneck?", [0], [
    ["Use a higher-cardinality partition key or controlled write sharding.", "Distributing writes across keys reduces concentration on one hot logical partition."],
    ["Increase only the number of characters in the sort key.", "A longer sort key does not distribute a constant partition key's traffic."],
    ["Disable all indexes and keep the constant key unchanged.", "Index removal may reduce some write cost but does not fix the concentrated primary access pattern."],
    ["Enable S3 Versioning.", "An S3 feature does not change DynamoDB partition distribution."],
  ], "Good partition-key distribution is essential; sharding also requires a plan for reading and aggregating the shards."],
  ["performance", "An application must read a just-completed DynamoDB write without stale results in the same Region. It reads the base table by primary key. Which option should it use?", [0], [
    ["A strongly consistent GetItem request.", "Strongly consistent reads on a base table reflect prior successful writes in that Region."],
    ["An eventually consistent read from a global secondary index.", "GSIs do not support strongly consistent reads and may lag the base table."],
    ["A cached DAX read with no invalidation plan.", "A cached value can be stale and does not meet the immediate freshness requirement."],
    ["A query of yesterday's S3 export.", "A historical export does not contain the latest write."],
  ], "Strong reads are supported on base tables and local secondary indexes, not global secondary indexes."],
  ["performance", "A DynamoDB application repeatedly reads the same popular catalog items and can tolerate eventual consistency. It needs microsecond-scale cached reads with minimal changes to its DynamoDB access model. Which service fits?", [0], [
    ["DynamoDB Accelerator (DAX).", "DAX is a DynamoDB-compatible managed in-memory cache for suitable read-heavy access patterns."],
    ["DynamoDB auto scaling without adding a cache.", "More table capacity handles additional requests but does not provide DAX's in-memory cached-read latency."],
    ["A new global secondary index containing the same item attributes.", "An index changes access paths but does not add a microsecond-scale in-memory cache."],
    ["A custom ElastiCache layer requiring cache-aside application logic.", "A general cache can help, but DAX is the closer fit for minimal changes to the DynamoDB access model."],
  ], "DAX can accelerate eventually consistent repeated reads; it is not a way to turn cached reads into strong consistency."],
  ["resilience", "A global application needs users in two Regions to read and write local replicas of a DynamoDB dataset. The application can handle the chosen replication mode's consistency behavior. Which feature supplies managed multi-Region replication?", [0], [
    ["DynamoDB global tables.", "Global tables provide managed multi-Region replicas with supported consistency-mode choices."],
    ["A local secondary index.", "An LSI supports an alternative sort key within one table, not regional replication."],
    ["A single-Region DAX cluster.", "A DAX cache does not turn a table into a multi-Region replicated database."],
    ["Scheduled cross-Region table exports used as writable replicas.", "Exports are data copies for restore or analysis, not continuously synchronized multi-active table replicas."],
  ], "Global tables support multi-Region workloads; explicitly choose and validate consistency mode, supported Regions and conflict behavior."],
  ["performance", "A company wants a Lambda function to react to item insertions and updates in a DynamoDB table without polling the whole table. Which integration should it configure?", [0], [
    ["Enable DynamoDB Streams and a Lambda event source mapping.", "Streams capture item-level changes and Lambda can consume them through an event source mapping."],
    ["Run a full Scan every second from Lambda.", "Repeated scans add cost and latency and do not form a precise change stream."],
    ["Export the table to S3 nightly and invoke Lambda only when the export completes.", "A nightly snapshot does not provide near-real-time item-level insert and update notifications."],
    ["Create a global secondary index and treat its entries as an automatically consumed event queue.", "A GSI is a query access path rather than a Lambda event source carrying item change records."],
  ], "Use change streams for event-driven reactions and make consumers idempotent because records may be processed again."],
  ["cost", "A new DynamoDB application has highly unpredictable request rates and frequent idle periods. The team wants request-based billing without maintaining provisioned capacity settings. Which mode is the best starting point?", [0], [
    ["On-demand capacity mode.", "On-demand bills per request and removes the need to configure provisioned read/write capacity."],
    ["A large fixed provisioned capacity selected for worst-case demand.", "Fixed peak capacity can waste money during idle periods."],
    ["Provisioned capacity with fixed manual adjustments before every expected spike.", "Manual provisioning requires predicting demand and maintaining settings the team wants to avoid."],
    ["Provision for the monthly average with no auto scaling or spike handling.", "Average-based fixed capacity can throttle bursts and still charge during idle periods."],
  ], "On-demand suits uncertain demand; compare provisioned capacity and auto scaling when usage becomes steady and predictable."],
  ["performance", "Analysts occasionally run SQL aggregations over partitioned Parquet files already stored in S3. They want no database cluster to administer. Which service best fits?", [0], [
    ["Amazon Athena using the data catalog.", "Athena runs serverless SQL over S3 data; partitioning and columnar formats reduce scanned data."],
    ["A DynamoDB Scan for every SQL join.", "DynamoDB is not a general analytical SQL engine over S3 Parquet files."],
    ["A permanent EC2 database server required for every query.", "A server adds cluster administration that the team wants to avoid."],
    ["An always-running Redshift provisioned cluster loaded with every file before querying.", "A warehouse can support analytics, but it adds provisioned resources and loading work for these occasional direct S3 queries."],
  ], "Athena suits ad hoc S3 analytics; formats, partitions and selected columns strongly influence scan cost."],
  ["performance", "A company needs a managed, continuously ingested event stream that multiple independent consumers can replay within a retention window. Records for each device should preserve order within their partition. Which service fits?", [0], [
    ["Amazon Kinesis Data Streams with a suitable partition key.", "Kinesis retains a replayable stream and orders records within a shard for independent consumers."],
    ["A standard SQS queue shared by all consumers.", "Queue consumers compete for messages; a standard queue is not a retained ordered replay log."],
    ["An SNS standard topic with direct HTTP delivery and no retained stream.", "Push delivery does not provide the requested per-partition ordered log that consumers can replay independently."],
    ["Amazon Data Firehose delivering buffered files to S3 as the only consumer interface.", "Delivery to storage is useful for analytics but does not expose the same retained stream interface for independent live consumers."],
  ], "Use a retained stream for independent replay; distribute partition keys to avoid hot shards."],
  ["resilience", "A checkout must claim an available inventory item and create a separate order item in DynamoDB. Concurrent checkouts must not claim the same stock, and either both changes or neither must commit. Which TWO choices meet these requirements?", [0, 1], [
    ["Include a condition in the inventory update requiring the item to still be available.", "The condition prevents a competing checkout from claiming stock that is no longer available."],
    ["Submit the inventory update and order creation together using TransactWriteItems.", "A transaction atomically commits the two item changes or fails without applying either change."],
    ["Read eventually, then overwrite the item unconditionally.", "Both workers can read the old state and both report successful claims."],
    ["Cache inventory for a day before making the update.", "A stale cache increases the risk of conflicting inventory decisions."],
    ["Enable a second global secondary index and ignore write conditions.", "An index does not enforce atomic claim conditions."],
  ], "Combine conditions with a transaction when both concurrency control and all-or-nothing updates across items are required."],
]);
