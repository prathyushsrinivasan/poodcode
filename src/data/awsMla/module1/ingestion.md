## Separate the event log, computation and serving

A fraud system receives purchases, calculates a customer's recent spending and retrieves those features during checkout. These are three different operations. A **durable stream** retains events for consumers and replay. A **processor** transforms them, possibly keeping state such as a rolling count. A **serving store** answers requests at the latency the application needs. Combining the names into one box hides where capacity and correctness can fail.

An event should carry an event ID, entity ID, event time, schema version and payload. Event time is when the purchase happened; ingestion time is when the pipeline received it. A delayed mobile device can send an old purchase now. If a feature means “spend during the five minutes before checkout,” arrival time alone gives the wrong result. Decide how late events are handled and how corrected aggregates are published.

| Need | Useful starting point | What still needs design |
| --- | --- | --- |
| Replayable events consumed by custom applications | Kinesis Data Streams | Partitioning, capacity, retention and consumer checkpointing |
| Buffered delivery to destinations such as S3 | Amazon Data Firehose | Buffering latency, transformations, failure destinations and duplicates |
| Existing Kafka ecosystem and client compatibility | Amazon MSK | Topic partitions, broker capacity and consumer groups |
| Stateful windows and event-time computation | Amazon Managed Service for Apache Flink | Watermarks, checkpoints, late-event policy and sink behavior |

Firehose is useful when the requirement is delivery. Kinesis Data Streams is useful when applications need independent access to an event log. Flink computes over a stream; it does not eliminate the need for durable sources and reliable sinks.

## Diagnose bottlenecks before adding capacity

A partition key determines where an event is routed. If almost every event uses `tenant-big`, aggregate stream capacity may look healthy while one key's route is overloaded. Consumers working on other partitions cannot process that hot route for you. Measure producer throttling, per-shard traffic, consumer lag, processing duration and destination throttling separately.

For a **capacity-planning exercise**, assume a partition is allowed 1,000 records/s and 1 MB/s of writes. At 700 records/s of 2 KB each, the rate is approximately 1.4 MB/s: the byte limit is reached before the record limit. These are explicit exercise assumptions, not a claim about every current stream configuration. Consult current Kinesis quotas for the selected capacity mode and shard configuration.

If the workload is evenly distributed and several routes are full, additional appropriate capacity can help. If only one tenant key is hot, consider a more distributed key such as tenant plus device, or controlled key salting. Changing keys changes ordering boundaries: events split across routes do not retain a single total order automatically. If tenant-wide ordering is mandatory, the design must account for that constraint rather than simply randomize keys.

If producers are healthy but consumer lag rises, inspect processing and the sink. A throttled feature-store writer can cause backpressure even when the consumer has spare CPU. Batch where supported, bound retries, and retain failed records with reasons. Scaling the source cannot repair a sink that rejects every record because the schema is invalid.

## Replay, windows and safe retries

Replay is valuable when a transformation is fixed: resume from an earlier position in the retained log and recalculate. It also means the same event may be processed more than once. **Idempotency** makes repeating an operation have the intended single effect. An event-ID-based deduplication policy can prevent a retried $20 purchase from incrementing spending twice. Choose a deduplication retention period consistent with the replay policy; a one-minute cache cannot protect a one-day replay.

A watermark is a processor's estimate of event-time progress. A five-minute window may wait briefly for late events, then emit an aggregate. Later arrivals can update it, go to a side output, or be rejected according to policy. Waiting longer can improve completeness while increasing result latency. Exactly-once guarantees inside a processor do not automatically cover an external API call: the source, checkpointing and sink behavior must support the end-to-end guarantee.

In our fraud example, retain purchases, aggregate by customer with an explicit late-event policy, and publish entity/time/value records. Record the feature definition version so a replay with new code does not silently mix old and new meanings.

## Feature lookup and vector search answer different questions

SageMaker Feature Store's online store is for the latest feature record by entity with low-latency access. Its offline store retains history for training and batch work. A feature group defines features including the record identifier and event-time feature. For example, `customer_id=c17`, `event_time=...`, `spend_5m=120`, `definition_version=v3` represents one computation. Sending data through the store does not automatically make a historical training join correct; select the record available as of each prediction.

A **vector index** instead finds nearby embeddings: “which product descriptions have a similar meaning?” An embedding model maps inputs to a numeric vector. A 1,024-dimensional index cannot accept 768-dimensional vectors without a compatible replacement. Matching dimensions alone is insufficient: vectors from unrelated models can inhabit incompatible spaces even when their lengths match. Use a consistent model and preprocessing path for indexed content and queries.

Choose a backend against retrieval and operational requirements. OpenSearch supports search workloads including vector and lexical retrieval; PostgreSQL with pgvector can combine relational constraints and vector operations; S3 Vectors supplies managed vector storage and queries within its documented capabilities. Verify supported dimensions, similarity metrics, filtering, latency and scale rather than assume feature parity.

The complete fraud design uses a stream for events, a processor for rolling features and an online entity lookup for checkout. A separate product-assistance feature might use vector retrieval. Replacing all of these with a vector database confuses similarity with exact identity and historical aggregation.
