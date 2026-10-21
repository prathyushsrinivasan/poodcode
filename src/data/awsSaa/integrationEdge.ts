import { bank } from "./schema";

export const integration = bank("integration", [
  ["resilience", "An order API sends work directly to a fulfillment service. When fulfillment slows down, API requests time out. Orders must be accepted quickly and processed later without losing the backlog. Which change best decouples the services?", [0], [
    ["Place an SQS queue between the API and fulfillment workers.", "A durable queue buffers work and allows consumers to process independently of request arrival."],
    ["Increase only the API timeout to several hours.", "Long waits keep services coupled and consume request resources."],
    ["Retry synchronous fulfillment calls repeatedly before returning the API response.", "Synchronous retries keep API acceptance dependent on the slow fulfillment service."],
    ["Publish only to an SNS HTTP subscription and rely on the consumer's memory as its backlog.", "This does not give the consumer the explicit durable queue and independently drained backlog required here."],
  ], "A queue absorbs bursts and separates availability boundaries; acknowledge requests only after durable acceptance."],
  ["resilience", "An SQS standard-queue worker occasionally receives the same payment request twice. The business must not charge the customer twice. Which application change is required?", [0], [
    ["Make payment processing idempotent using a durable request identifier and atomic deduplication.", "Standard queues provide at-least-once delivery, so consumers must tolerate duplicates safely."],
    ["Assume deleting a message eliminates all possible duplicate deliveries.", "Standard queue delivery can still produce duplicates; deletion is not a business deduplication guarantee."],
    ["Use the receive timestamp as a new payment ID every time.", "A fresh ID makes a duplicate look like a new payment."],
    ["Disable all retries and silently drop failed payments.", "Dropping failures sacrifices successful processing rather than ensuring correctness."],
  ], "Design side effects for idempotency; message transport alone cannot guarantee a business operation happens only once."],
  ["resilience", "A worker usually needs 90 seconds to process an SQS message, but the visibility timeout is 30 seconds. Other workers start processing the same job before the first finishes. Which TWO actions address this?", [0, 1], [
    ["Set the visibility timeout above the expected processing duration.", "Messages remain hidden long enough for normal processing to finish."],
    ["Extend visibility while a long-running job remains in progress.", "ChangeMessageVisibility can prevent premature redelivery when processing time varies."],
    ["Delete the message before starting the job.", "A crash after deletion loses the job instead of allowing retry."],
    ["Increase message retention to fourteen days without changing visibility.", "Retention controls how long messages remain stored, not how long an in-flight message is hidden."],
    ["Increase the number of consumers without changing processing semantics.", "More consumers do not fix visibility expiration and can increase duplicate concurrent work."],
  ], "Visibility timeout is a processing lease; delete only after success and still handle duplicate delivery idempotently."],
  ["resilience", "Some messages repeatedly fail because of invalid data. They should stop blocking ordinary work after a configured number of receives and remain available for investigation. What should the team configure?", [0], [
    ["An SQS dead-letter queue with an appropriate redrive policy.", "The redrive policy moves repeatedly received failed messages to a separate queue."],
    ["A lifecycle rule that deletes the entire source queue hourly.", "Deleting the queue discards valid work and removes evidence needed for investigation."],
    ["Increase the visibility timeout and retry malformed messages indefinitely.", "A longer timeout delays retries but does not isolate poison messages after a bounded number of receives."],
    ["Increase source queue retention and keep every failed message in the source.", "Longer retention preserves messages but does not separate failures from ordinary processing."],
  ], "Use a DLQ for poison-message isolation, monitor it and correct the cause before redriving messages."],
  ["resilience", "Every order event must reach billing, analytics and inventory independently. Each consumer needs its own durable backlog and retry behavior. Which architecture fits?", [0], [
    ["Publish to SNS with a separate SQS subscription for each consumer.", "SNS fans out events while each queue retains its own independent processing backlog."],
    ["Put all three consumers on one SQS queue and expect each message to reach all three.", "Consumers on one queue compete for messages rather than each receiving a copy."],
    ["Subscribe all three services directly to SNS HTTP delivery with no persistent consumer storage.", "Push delivery alone does not provide the required independently managed durable backlog for each service."],
    ["Use three SQS queues but publish each event to only one randomly chosen queue.", "Load distributing an event to one destination does not deliver every event to all three consumers."],
  ], "SNS-to-SQS fanout combines publication to many subscribers with durable per-consumer buffering."],
  ["resilience", "Updates for each customer must be processed in order, while different customers should process concurrently. An SQS-based design is required. Which configuration best fits?", [0], [
    ["Use an SQS FIFO queue with customer ID as MessageGroupId.", "FIFO ordering is maintained within a group, and different groups can process concurrently."],
    ["Use a standard queue and assume global strict order.", "Standard queues offer best-effort ordering rather than strict FIFO order."],
    ["Use one MessageGroupId for every customer to maximize parallelism.", "One group serializes processing across all customers instead of enabling customer-level concurrency."],
    ["Sort only by the time each worker receives the message.", "Receive timestamps cannot reconstruct a strict upstream ordering guarantee."],
  ], "FIFO message groups define ordering boundaries; choose group cardinality to match safe parallelism."],
  ["performance", "A company routes business events from AWS services, custom applications and a SaaS integration. Routing should match event fields without custom polling code. Which service should it use?", [0], [
    ["Amazon EventBridge with event-pattern rules.", "EventBridge supports event buses, integrations and content-based routing to targets."],
    ["A standard SQS queue with custom polling workers that inspect and forward every message.", "This adds polling and routing code that event-pattern rules would manage directly."],
    ["Kinesis Data Streams with custom consumer code implementing every SaaS integration and routing rule.", "A stream can transport events, but this design retains the integration and content-routing code the company wants to avoid."],
    ["An SNS topic with no filter policies and all targets receiving every event.", "Broadcasting every event does not implement the required field-based selection of destinations."],
  ], "EventBridge routes events by content; configure target retries and dead-letter handling for delivery failures."],
  ["resilience", "A checkout workflow calls several services and waits for human approval. It needs persisted execution state, retries and compensating steps for failures. Which managed service best coordinates the workflow?", [0], [
    ["AWS Step Functions Standard workflows.", "Standard workflows support durable orchestration, waits, retries and service integrations."],
    ["One Lambda invocation sleeping until approval arrives days later.", "A single Lambda execution cannot remain running for days and is a poor durable waiting mechanism."],
    ["A chain of direct Lambda invocations with state stored only in the active function's memory.", "In-memory chaining does not provide durable waits and persisted orchestration across failures."],
    ["Independent EventBridge schedules for each step with no shared workflow state.", "Schedules alone do not coordinate conditional transitions, retries and compensating actions as one execution."],
  ], "Use durable orchestration for multi-step work; compensation must be designed for side effects already committed."],
  ["cost", "A worker polls an SQS queue that is often empty. The company wants fewer empty responses without delaying work by a large fixed sleep between requests. Which feature should it enable?", [0], [
    ["SQS long polling.", "Long polling waits for available messages within the request window and reduces empty receives."],
    ["Short polling in a tight loop with no wait.", "Frequent short polls increase empty responses and API usage."],
    ["Disable message retention.", "Removing retention does not implement efficient polling and risks losing work."],
    ["Increase message visibility timeout to reduce empty receives.", "Visibility affects already-received messages, not how a receive request waits for new work."],
  ], "Long polling reduces empty responses; configure client read timeouts longer than the receive wait time."],
  ["security", "A public REST API uses API Gateway and Lambda. Third-party clients need per-client request quotas and throttling, while users still require real authentication. Which TWO controls should be used?", [0, 1], [
    ["Usage plans and API keys for client metering and throttling.", "Usage plans associate API keys with usage limits and throttling targets."],
    ["A supported authorizer or IAM authorization for authentication and access control.", "An authorizer or IAM evaluates caller identity and authorization separately from API-key metering."],
    ["Use API keys as the only user authentication mechanism.", "API keys for usage plans are not a replacement for authentication and authorization."],
    ["Configure only a Cognito authorizer and assume it automatically creates per-client usage-plan quotas.", "An authorizer authenticates callers but does not replace usage-plan configuration for API-key-based metering."],
    ["Disable throttling because Lambda always has unlimited capacity.", "Lambda and downstream systems have limits, and throttling remains useful."],
  ], "API Gateway usage plans meter clients; enforce identity separately and treat quotas as best-effort rather than hard billing caps."],
]);

export const edge = bank("edge", [
  ["performance", "Users worldwide download the same static assets from one regional S3 bucket. The team wants lower download latency and fewer origin requests. Which service should it put in front of S3?", [0], [
    ["Amazon CloudFront with an appropriate cache policy.", "CloudFront serves cacheable objects from edge locations and reduces repeated origin fetches."],
    ["S3 Transfer Acceleration without a CDN.", "Transfer Acceleration optimizes transfer paths but does not provide reusable edge caching of viewer responses."],
    ["Route 53 latency routing with only the original S3 regional endpoint.", "DNS routing to one origin does not create nearby cached copies or reduce repeated origin requests."],
    ["An ALB in the same Region forwarding every asset request to an origin application.", "A regional load balancer does not supply global edge caching for repeated static asset reads."],
  ], "A CDN improves delivery through edge caching; cache keys and object versioning determine correctness and hit rate."],
  ["performance", "A company runs equivalent web deployments in two Regions. DNS should direct users to the healthy Region expected to provide the lowest latency. Which Route 53 routing policy best fits?", [0], [
    ["Latency-based routing with appropriate health evaluation.", "Latency routing chooses among configured Regions based on latency estimates; health evaluation excludes unhealthy targets."],
    ["Simple routing with one fixed target.", "A single fixed target cannot choose between healthy regional deployments by latency."],
    ["Weighted routing with equal weights and no health checks.", "Weights express traffic proportions rather than estimated latency or health."],
    ["Geolocation routing based only on a user's billing address.", "Route 53 geolocation uses request-location information, not billing records, and does not optimize measured latency."],
  ], "Choose latency routing for latency-based regional selection and configure health checks; cached DNS answers still affect failover timing."],
  ["resilience", "A company has a primary web deployment and a standby site. DNS should send traffic to the standby only when the primary fails health checks. Which policy should it use?", [0], [
    ["Route 53 failover routing.", "Failover records implement a primary-secondary DNS design using target health."],
    ["Route 53 weighted routing permanently set to 50/50.", "Equal weighting sends traffic to both sites during healthy operation."],
    ["A single simple record with no health evaluation.", "Without a second target and health evaluation, the record cannot implement automatic failover."],
    ["Latency-based records with both sites serving traffic at all times.", "Active-active latency selection does not enforce the requested primary-only behavior while healthy."],
  ], "DNS failover needs healthy standby capacity and realistic RTO expectations that include DNS caching and client behavior."],
  ["security", "An internet-facing ALB receives SQL injection and cross-site scripting attempts. The team wants managed HTTP request inspection rules without changing application code. Which service should it use?", [0], [
    ["AWS WAF with a web ACL associated with the ALB.", "WAF inspects application-layer requests and can apply managed rules and custom conditions."],
    ["Security group rules matching SQL query text.", "Security groups cannot inspect HTTP payloads for SQL injection patterns."],
    ["Shield Standard alone with no web ACL.", "Baseline DDoS protection is not a replacement for HTTP request rules targeting SQL injection and XSS."],
    ["A network ACL allowing TCP 443 from approved countries.", "NACLs do not perform country-based HTTP content inspection or detect injection payloads."],
  ], "Use WAF for application-layer filtering and retain secure application code; tune rules and monitor false positives."],
  ["security", "A business wants enhanced DDoS protection, access to specialist DDoS response support and eligible DDoS cost protection for supported resources. Which subscription is designed for this?", [0], [
    ["AWS Shield Advanced.", "Shield Advanced adds enhanced protections and eligible support and cost-protection features beyond standard protection."],
    ["Shield Standard alone.", "Standard protection does not include the enhanced subscription features and eligible cost protection requested."],
    ["AWS WAF managed rules without Shield Advanced.", "WAF application filtering alone does not supply Shield Advanced's specialist response and eligible DDoS cost protection."],
    ["A larger DNS TTL as the complete protection strategy.", "Caching behavior alone does not supply enhanced DDoS protection and response capabilities."],
  ], "Shield Standard provides baseline protection; evaluate Shield Advanced against required protections, eligibility and subscription cost."],
  ["performance", "A global UDP application requires two stable anycast IP addresses and health-based routing to regional endpoints through the AWS global network. It does not need HTTP object caching. Which service fits?", [0], [
    ["AWS Global Accelerator.", "Global Accelerator provides static anycast addresses and routes supported TCP/UDP traffic to healthy endpoints."],
    ["CloudFront with an arbitrary UDP cache behavior.", "CloudFront is an HTTP content delivery service, not a generic UDP accelerator."],
    ["S3 Transfer Acceleration for UDP sessions.", "S3 acceleration optimizes supported object transfers rather than arbitrary application sessions."],
    ["Route 53 latency routing directly to changing regional endpoint addresses.", "DNS-based regional selection does not provide the requested pair of static anycast ingress IPs."],
  ], "Use Global Accelerator for global transport ingress and static IPs; use CloudFront for HTTP content delivery and caching."],
  ["cost", "CloudFront forwards a unique tracking query string to the origin and includes it in the cache key, even though the parameter never changes the returned image. Cache hit rate is very low. What should change?", [0], [
    ["Exclude the tracking parameter from the cache key while forwarding it separately only if needed.", "Removing irrelevant key variation allows identical image responses to share cached entries."],
    ["Add every request header and cookie to the cache key.", "More unnecessary variation fragments the cache further."],
    ["Disable edge caching permanently.", "Disabling caching increases origin traffic and gives up the intended savings."],
    ["Increase the origin's compute capacity but keep the unique tracking parameter in every cache key.", "More origin capacity does not remove the cache fragmentation caused by per-request key variation."],
  ], "Include response-changing values in the cache key; avoid caching personalized responses under a shared key."],
  ["security", "A team configures a custom domain on CloudFront and wants an ACM-issued TLS certificate for viewer HTTPS. In which AWS Region must it request or import that certificate for CloudFront?", [0], [
    ["US East (N. Virginia), us-east-1.", "CloudFront requires ACM certificates used for viewer HTTPS to be in us-east-1."],
    ["Only the Region containing the S3 origin.", "The viewer certificate's required Region is independent of the origin's Region."],
    ["Any Region, because CloudFront automatically moves ACM certificates.", "CloudFront does not remove the ACM Region requirement for viewer certificates."],
    ["A separate certificate in every edge location.", "Customers do not provision ACM certificates separately for individual edge locations."],
  ], "CloudFront viewer certificates in ACM belong in us-east-1; origin HTTPS certificates have separate configuration requirements."],
  ["performance", "A team releases a new JavaScript bundle. Cached older files may remain valid for a year, but users must receive the new bundle immediately when the HTML changes. Which release design avoids invalidating every asset?", [0], [
    ["Use content-versioned asset filenames and update the HTML references.", "A new filename creates a new cache key while old versioned assets remain safely cacheable."],
    ["Overwrite the same filename and assume every edge immediately refetches it.", "An unexpired cached response can remain until expiry or invalidation."],
    ["Increase the existing asset's cache lifetime without changing its URL.", "A longer lifetime makes the old cached response persist longer under the same URL."],
    ["Enable S3 Versioning and keep referencing the same unversioned object URL.", "S3 version history does not automatically change the CloudFront cache key used by the viewer URL."],
  ], "Version immutable assets by URL and manage HTML freshness; use invalidation when old URLs must stop serving cached content."],
  ["resilience", "A CloudFront distribution serves read-only assets from an origin group with a primary and secondary S3 origin. The primary returns a configured failover status for a GET request. What behavior should the architect expect?", [0], [
    ["CloudFront can retry that request against the secondary origin according to the origin group's failover settings.", "Origin groups support failover for eligible request methods and configured failure conditions."],
    ["CloudFront synchronously replicates the missing object to the secondary before retrying.", "Origin failover routes requests; it does not replicate origin data."],
    ["Origin groups guarantee failover for every HTTP method including writes.", "Origin failover supports GET, HEAD and OPTIONS rather than arbitrary write methods."],
    ["An origin group automatically creates a second bucket with identical permissions.", "Secondary content, bucket policies and access must be provisioned separately."],
  ], "Configure both origin access and data replication separately; CloudFront origin failover is request routing, not a storage backup."],
]);
