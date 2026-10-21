import { bank } from "./schema";

export const storage = bank("storage", [
  ["resilience", "A user accidentally overwrites a critical object in S3. The application needs a simple way to recover earlier contents without restoring an entire bucket backup. Which feature should have been enabled?", [0], [
    ["S3 Versioning.", "Versioning retains earlier object versions that can be retrieved or restored after an overwrite."],
    ["S3 Transfer Acceleration.", "Acceleration changes the upload path and does not preserve previous contents."],
    ["Default SSE-S3 encryption.", "Encryption protects stored contents but does not keep overwritten versions."],
    ["An S3 gateway endpoint.", "An endpoint changes private network access rather than recovery behavior."],
  ], "Enable versioning before accidental overwrites occur; plan lifecycle rules for noncurrent versions as well."],
  ["security", "A regulated company must retain records for seven years. Even the account root user must be unable to delete a protected version before its retention date. Which solution meets this requirement?", [0], [
    ["S3 Object Lock in compliance mode with the required retention period.", "Compliance mode prevents deletion or shortening of protected retention, including by root."],
    ["S3 Object Lock in governance mode with bypass permission for administrators.", "Authorized users can bypass governance retention, violating the stated requirement."],
    ["A lifecycle rule that deletes records after seven years.", "Lifecycle expiration does not prevent users from deleting data earlier."],
    ["S3 Versioning with MFA Delete but no Object Lock retention.", "MFA Delete adds authentication to some delete operations but does not enforce an immutable seven-year retention period."],
  ], "Object Lock compliance mode provides immutable retention for protected object versions; governance mode allows privileged bypass."],
  ["cost", "A company retains large audit files for ten years. Files are rarely read, and restores may take up to 48 hours. Which S3 class generally provides the lowest storage cost for this access pattern?", [0], [
    ["S3 Glacier Deep Archive.", "Deep Archive targets very infrequent long-term access with restore delays compatible with this requirement."],
    ["S3 Standard.", "Standard's immediate access costs more for data rarely retrieved over many years."],
    ["S3 Express One Zone.", "Express targets low-latency access rather than low-cost long-term archives."],
    ["S3 Standard-IA.", "Standard-IA keeps immediate access and typically costs more to store than deep archival storage."],
  ], "Choose archival classes by retrieval time and total cost, including minimum durations and retrieval charges."],
  ["cost", "Millions of large objects have unpredictable access patterns. Objects must remain available with millisecond access, and the team cannot maintain per-object lifecycle decisions. Which solution fits best?", [0], [
    ["S3 Intelligent-Tiering without optional asynchronous archive tiers.", "Automatic access-tier transitions optimize changing usage while the selected tiers retain immediate access."],
    ["Move every object to Glacier Deep Archive after one day.", "Deep Archive requires a restore and cannot meet millisecond access."],
    ["Store everything in S3 One Zone-IA regardless of resilience requirements.", "One Zone-IA neither adapts tiers automatically nor preserves multi-AZ storage resilience."],
    ["Move all objects to Standard-IA after a fixed number of days regardless of actual access.", "A fixed age rule does not adapt to objects that become frequently accessed again or stay frequently accessed."],
  ], "Intelligent-Tiering automates access-based tiering; optional archive tiers change restore behavior, and monitoring charges affect small-object economics."],
  ["performance", "A Linux application runs on EC2 instances in several AZs. All instances need concurrent access to the same files through a POSIX-compatible NFS interface. Which TWO choices provide managed shared access?", [0, 1], [
    ["Amazon EFS Regional mounted by the instances.", "EFS supplies managed shared NFS file storage with Regional multi-AZ availability."],
    ["Configure EFS mount targets and permit NFS access from the application's security group.", "Mount targets and network permissions provide the instances' path to the shared filesystem."],
    ["One ordinary EBS volume attached read-write to every instance across all AZs.", "EBS volumes are AZ-scoped and ordinary volumes do not support this shared cross-AZ attachment pattern."],
    ["An S3 bucket accessed as an unmodified POSIX filesystem.", "S3 is an object API and does not natively provide general POSIX NFS semantics."],
    ["Each instance's local instance store.", "Instance stores are local to individual hosts and do not form a shared filesystem."],
  ], "Match the interface first: EFS for shared Linux NFS files, EBS for block devices, S3 for objects."],
  ["performance", "A Windows workload needs a managed shared filesystem supporting SMB, Windows ACLs and Active Directory integration. Which service best fits?", [0], [
    ["Amazon FSx for Windows File Server.", "FSx for Windows provides managed Windows file shares with SMB and AD integration."],
    ["Amazon EFS.", "EFS primarily exposes NFS rather than a native Windows SMB file server."],
    ["Amazon S3 Glacier Deep Archive.", "An archive object store does not provide interactive SMB shares."],
    ["An EC2 instance store volume.", "Local ephemeral block storage does not supply a managed shared Windows filesystem."],
  ], "Use workload protocol and identity requirements to distinguish EFS from the appropriate FSx filesystem."],
  ["performance", "Remote offices upload multi-gigabyte files over unreliable internet links. Failed uploads should retry only the affected portions. Which TWO S3 capabilities should the application use?", [0, 1], [
    ["Multipart upload.", "Multipart upload splits an object into independently transferable parts."],
    ["Retry failed parts and complete the upload after all parts succeed.", "A failed part can be resent without retransmitting the whole object."],
    ["Enable Transfer Acceleration but continue using one large PUT per file.", "A faster transfer path alone does not provide part-level retry for a failed single PUT."],
    ["Use one large PUT and restart it whenever the connection drops.", "This retransmits already-sent data and fails the efficient-retry requirement."],
    ["Enable S3 Versioning and assume interrupted PUTs resume automatically.", "Versioning preserves completed object versions rather than adding resumable parts to a single PUT."],
  ], "Multipart upload enables parallel transfer and part-level retry; abort incomplete uploads to avoid stranded storage charges."],
  ["performance", "A data center needs to migrate hundreds of terabytes of files to S3 over an existing network connection. The team wants managed scheduling, incremental copying and data-integrity verification. Which service should it use?", [0], [
    ["AWS DataSync.", "DataSync automates network-based transfers, incremental changes and verification for supported storage endpoints."],
    ["AWS DMS as a general-purpose filesystem copier.", "DMS is intended for database migration and replication rather than general file migration."],
    ["AWS Transfer Family used only as an SFTP server, without a source-side scheduled transfer process.", "An SFTP endpoint alone does not supply the requested managed source scan, incremental synchronization and verification workflow."],
    ["A one-time recursive copy script with no incremental comparison or verification.", "A one-off copy does not supply the required recurring, verified incremental transfer management."],
  ], "Choose DataSync for managed online file and object transfers; choose database-specific tooling for databases."],
  ["performance", "An on-premises application must keep using SMB paths while new files are durably stored as S3 objects. Recently used files should be cached locally. Which solution best fits?", [0], [
    ["Amazon S3 File Gateway.", "File Gateway presents file protocols backed by S3 objects and maintains a local cache."],
    ["A tape gateway mounted as an SMB filesystem.", "Tape Gateway exposes virtual tape infrastructure, not ordinary SMB file shares."],
    ["An S3 gateway VPC endpoint installed on the file server.", "A VPC endpoint is not an on-premises protocol adapter or local cache."],
    ["Mount an EFS filesystem over a VPN and use it as the only durable backend.", "EFS provides NFS file storage; this does not preserve SMB access backed by new S3 objects."],
  ], "Storage Gateway bridges existing on-premises storage interfaces to AWS; choose the gateway type matching the application protocol."],
  ["security", "S3 objects encrypted with a customer managed KMS key must replicate automatically to a second Region. Which TWO configurations are necessary for S3 Cross-Region Replication of these objects?", [0, 1], [
    ["Enable versioning on the source and destination buckets.", "S3 replication depends on versioning in both source and destination buckets."],
    ["Configure replication for SSE-KMS objects with a destination-Region key and the required KMS permissions.", "Encrypted-object replication must be explicitly configured and authorized to decrypt and encrypt appropriately."],
    ["Disable all encryption before creating the rule.", "S3 supports replication of SSE-KMS data with the correct configuration."],
    ["Attach both buckets to the same public subnet.", "S3 buckets are not placed in VPC subnets and the buckets are in different Regions."],
    ["Use only an IAM policy allowing s3:ListAllMyBuckets.", "Listing buckets does not authorize object replication or KMS operations."],
  ], "Replication needs versioning and appropriate object/key permissions; use Batch Replication when existing objects must also be copied."],
]);

export const compute = bank("compute", [
  ["resilience", "An ecommerce application must survive the failure of one AZ and automatically replace unhealthy web servers. Which TWO components provide the best foundation?", [0, 1], [
    ["An Application Load Balancer enabled in multiple AZs.", "A multi-AZ load balancer directs requests to healthy targets in available zones."],
    ["An Auto Scaling group spanning multiple AZs with appropriate health checks.", "The group maintains capacity and replaces instances deemed unhealthy."],
    ["One larger EC2 instance in a single AZ.", "Vertical scaling leaves a single-zone failure dependency."],
    ["A single EBS volume holding all application sessions.", "A zonal volume does not supply resilient shared session state."],
    ["An Elastic IP manually moved after every failure.", "Manual address movement does not provide automatic fleet replacement or balancing."],
  ], "Distribute both traffic and capacity across AZs, and externalize state so replacements can serve requests."],
  ["performance", "Several services share one HTTPS entry point. Requests to /orders must reach one target group and /catalog another. Which load balancer feature should the architect use?", [0], [
    ["Application Load Balancer path-based listener rules.", "ALB evaluates HTTP request paths and forwards them to matching target groups."],
    ["Network Load Balancer TCP health checks.", "A TCP health check does not route application requests by HTTP path."],
    ["Route 53 weighted routing based on URL paths.", "DNS resolves hostnames and does not inspect an HTTP URL path."],
    ["A security group rule for each path.", "Security groups filter network traffic rather than application URL paths."],
  ], "Choose ALB for HTTP-aware routing; choose NLB when transport-layer behavior or fixed addresses drive the requirement."],
  ["performance", "A TCP service requires very high throughput and a fixed IP address in each enabled AZ for customer firewall allowlists. Which AWS load balancer best matches the requirements?", [0], [
    ["Network Load Balancer with assigned Elastic IP addresses.", "NLB supports TCP traffic and static addressing, including an Elastic IP per enabled AZ."],
    ["Application Load Balancer with a manually pinned current IP.", "ALB addresses can change; pinning a resolved address is not a supported static-IP design."],
    ["CloudFront using an S3 website origin.", "CloudFront is not a generic TCP load balancer."],
    ["A Route 53 private hosted zone alone.", "A DNS zone does not perform transport-layer traffic balancing or provision service IPs."],
  ], "NLB fits transport-level balancing and fixed per-AZ addresses; still design targets and capacity for failures."],
  ["performance", "A stateless web fleet should maintain average CPU utilization near 50% as traffic rises and falls. The team wants AWS to calculate the required scaling adjustments. Which policy should it select?", [0], [
    ["Target tracking scaling on average CPU utilization.", "Target tracking adjusts capacity to keep the selected metric near its configured target."],
    ["A fixed desired capacity of two instances.", "Fixed capacity does not react to changing traffic."],
    ["A scheduled action once every year.", "A yearly schedule cannot track unpredictable demand during the day."],
    ["A simple scaling policy with manually chosen fixed instance adjustments for each CPU alarm.", "This requires tuning the adjustment sizes rather than letting target tracking calculate capacity to maintain the target."],
  ], "Choose a scaling metric that changes proportionally with load per instance; target tracking manages the adjustments."],
  ["resilience", "A web application stores sessions only in each EC2 instance's memory. Users lose their carts when Auto Scaling replaces instances. Which design most directly resolves the underlying issue?", [0], [
    ["Store session state in a suitable shared store such as DynamoDB or a resilient ElastiCache deployment.", "External state allows any healthy replacement instance to continue a user's session."],
    ["Enable sticky sessions and keep all state only in instance memory.", "Stickiness cannot preserve memory after the selected instance fails or is terminated."],
    ["Disable health checks permanently.", "Retaining unhealthy instances reduces availability and does not make memory durable."],
    ["Increase the deregistration delay and keep all sessions in memory.", "Draining can help in-flight requests finish but does not preserve sessions after the host is gone."],
  ], "Stateless compute is replaceable compute; load-balancer affinity is not durable session storage."],
  ["cost", "A company runs containerized jobs intermittently. It wants to avoid provisioning or patching EC2 worker hosts and pay for the compute resources requested while tasks run. Which option best fits?", [0], [
    ["Amazon ECS tasks on AWS Fargate.", "Fargate runs containers without the team managing underlying EC2 hosts."],
    ["A permanently running, manually patched EC2 cluster.", "This retains host administration and idle capacity costs."],
    ["ECS using the EC2 launch type with a manually maintained worker AMI.", "This still leaves the team responsible for EC2 host provisioning, patching and capacity management."],
    ["An EKS cluster with self-managed EC2 worker nodes.", "Self-managed nodes retain the host-management work the team wants to avoid."],
  ], "Fargate removes host management for supported container workloads; still choose task sizing and service scaling carefully."],
  ["performance", "An image-processing Lambda function should read a file from S3 when an upload occurs. Processing takes less than a minute and demand is sporadic. Which architecture minimizes server management?", [0], [
    ["Configure S3 object-created events to invoke Lambda with an execution role granting needed access.", "Event-driven invocation processes new uploads without polling servers."],
    ["Run a permanent EC2 instance polling S3 every second.", "This adds idle compute, polling and server administration."],
    ["Run a scheduled container that lists every object and discovers new images each minute.", "Polling can work but adds discovery logic and scheduled compute compared with direct upload events."],
    ["Keep a full-size image-processing EC2 fleet running continuously behind an ALB.", "Permanent peak capacity adds management and idle cost for this short, sporadic event workload."],
  ], "Use event-driven compute for short sporadic work; make handlers idempotent because events can be delivered more than once."],
  ["resilience", "A latency-sensitive Lambda API needs predictable startup latency during a planned launch window. Optimizing package size alone has not removed cold-start delays. Which feature directly keeps execution environments initialized?", [0], [
    ["Provisioned concurrency sized for expected traffic.", "Provisioned concurrency preinitializes environments, reducing initialization delays within its configured capacity."],
    ["Reserved concurrency alone.", "Reserved concurrency reserves and caps concurrent executions but does not preinitialize environments."],
    ["EventBridge warm-up invocations sent occasionally to one function environment.", "Occasional invocations do not guarantee enough initialized environments for the expected concurrent launch traffic."],
    ["A longer function timeout.", "A longer allowed runtime does not prevent cold-start initialization."],
  ], "Provisioned concurrency addresses initialization latency; reserved concurrency controls concurrency allocation and limits."],
  ["performance", "An EC2 database requires consistent low-latency block storage and tens of thousands of provisioned IOPS. The data must persist independently of the instance. Which storage type best fits?", [0], [
    ["An appropriately sized EBS io2 volume.", "io2 is persistent block storage designed for demanding workloads with provisioned IOPS."],
    ["Instance store as the only database copy.", "Instance store data can be lost when its instance stops, terminates or the host fails."],
    ["An EBS st1 volume selected for large sequential throughput.", "Throughput Optimized HDD is not designed for consistent high-IOPS random database transactions."],
    ["An EBS sc1 volume selected for maximum random transaction IOPS.", "Cold HDD volumes target low-cost, infrequently accessed throughput workloads rather than high random IOPS."],
  ], "Choose EBS by required IOPS, throughput and latency; persistence still requires a backup and recovery plan."],
  ["cost", "A batch workload can checkpoint and tolerate interruption. Jobs run for hours and can restart on different instances. Which purchasing option usually offers the largest compute discount while matching this tolerance?", [0], [
    ["EC2 Spot Instances with interruption handling and diversified capacity pools.", "Spot offers discounted spare capacity, and checkpointed jobs can recover when that capacity is reclaimed."],
    ["On-Demand Dedicated Hosts for every job.", "Dedicated Hosts are not the economical default for interruption-tolerant generic batch compute."],
    ["A Capacity Reservation used as a discount product by itself.", "Capacity Reservations assure capacity; they do not themselves supply a discounted pricing commitment."],
    ["Always provision the largest available On-Demand instance.", "Oversizing and full On-Demand rates ignore the workload's interruption tolerance."],
  ], "Spot savings require interruption-tolerant architecture, checkpointing and flexible placement rather than assuming capacity is permanent."],
]);
