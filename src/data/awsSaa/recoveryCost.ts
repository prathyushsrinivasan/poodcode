import { bank } from "./schema";

export const recovery = bank("recovery", [
  ["resilience", "A business can lose at most 15 minutes of data and must restore service within two hours after a disaster. Which pair of objectives matches these requirements?", [0], [
    ["RPO of 15 minutes and RTO of two hours.", "RPO measures acceptable data loss in time; RTO measures acceptable recovery time."],
    ["RPO of two hours and RTO of 15 minutes.", "This reverses the data-loss and restoration-time requirements."],
    ["Both objectives are two hours.", "A two-hour RPO permits more data loss than the business allows."],
    ["Both objectives are zero because backups exist.", "Backups alone do not imply zero data loss or instantaneous recovery."],
  ], "Translate business requirements into data-loss tolerance (RPO) and restoration-time tolerance (RTO) before selecting a recovery strategy."],
  ["cost", "A noncritical internal application can tolerate a full day of data loss and a day-long recovery. The company wants the lowest ongoing DR infrastructure cost. Which strategy is the best starting point?", [0], [
    ["Backup and restore with tested cross-Region backups and infrastructure automation.", "With loose recovery objectives, stored backups avoid the cost of continuously running a second full deployment."],
    ["Full-size active-active deployments in three Regions.", "This incurs ongoing capacity and operational costs beyond the stated recovery requirements."],
    ["A full-size hot standby processing no production requests.", "Running full idle capacity is unnecessary for a day-long recovery window."],
    ["No backups because the application is noncritical.", "Noncritical does not mean data loss beyond one day is acceptable."],
  ], "Choose the least costly recovery strategy that can demonstrate the required RPO and RTO through testing."],
  ["resilience", "A company continuously replicates its database to a recovery Region but leaves most application servers off. After a disaster it provisions the application tier from templates. Which DR strategy does this describe?", [0], [
    ["Pilot light.", "Pilot light keeps essential core components running and brings up additional infrastructure during recovery."],
    ["Full multi-site active-active.", "Active-active serves production traffic from multiple complete deployments simultaneously."],
    ["Backup and restore only, with no running components.", "The continuously running database core distinguishes pilot light from backup-only recovery."],
    ["A full-capacity hot standby.", "Most application compute is off, so full-capacity standby is not already running."],
  ], "Pilot light trades recovery provisioning time for lower steady-state cost than a fully running standby."],
  ["resilience", "A recovery Region runs a complete functional copy of an application at reduced capacity. During a disaster, the team scales it to production capacity and redirects traffic. Which strategy is this?", [0], [
    ["Warm standby.", "A scaled-down but fully functional deployment is the defining warm-standby pattern."],
    ["Backup and restore with no deployed application.", "The application is already running, unlike a backup-only design."],
    ["Pilot light with only a database running.", "Warm standby includes a functioning application stack rather than only its core components."],
    ["Full-capacity active-active with both Regions serving normal production traffic.", "A reduced-capacity recovery deployment awaiting failover is warm standby rather than active-active."],
  ], "Warm standby reduces restoration steps, but capacity availability, scale-up time and data replication still need testing."],
  ["resilience", "An application runs across three AZs in one Region. A business continuity review now requires survival of a full regional outage. What additional architectural capability is needed?", [0], [
    ["A tested recovery deployment and suitable data copies in another Region.", "A regional failure requires resources outside the affected Region's failure boundary."],
    ["A fourth subnet in one of the existing AZs.", "Additional subnets in the same Region do not provide regional independence."],
    ["Only a larger EC2 instance in the primary Region.", "Instance size does not change its regional failure boundary."],
    ["A lower DNS TTL pointing only to the original regional endpoint.", "Faster DNS expiry cannot create a healthy alternative deployment."],
  ], "Multi-AZ architecture handles zonal failures; regional recovery requires a separate regional data and application strategy."],
  ["security", "A company fears an administrator could delete both production data and ordinary recovery copies. It needs centrally managed backups with retention controls and an isolated account boundary. Which TWO measures best address this?", [0, 1], [
    ["Copy supported backups to a dedicated backup account with tightly restricted access.", "A separate account reduces the blast radius of compromised production administrators."],
    ["Use AWS Backup Vault Lock with an appropriately configured immutable retention policy.", "Vault Lock can enforce backup retention and prevent deletion when its compliance protections are in force."],
    ["Give every production developer full administrator access to the backup account.", "Shared broad access defeats the intended isolation boundary."],
    ["Keep all backup copies on the production instance's root disk.", "The same failure or deletion can destroy both primary data and the backups."],
    ["Remove all retention requirements so cleanup is easier.", "Unrestricted deletion undermines protection against malicious or accidental backup removal."],
  ], "Backup isolation and immutability complement each other; validate lock configuration carefully and test restores."],
  ["resilience", "A team has successful nightly backup jobs but has never restored the application. Management asks whether its four-hour RTO is proven. Which action gives the strongest evidence?", [0], [
    ["Run a timed recovery exercise including data restore, application startup and validation.", "An end-to-end exercise measures whether the actual dependency chain meets the recovery objective."],
    ["Count the number of backup files and assume the RTO is met.", "Backup count does not measure restoration, configuration or application validation time."],
    ["Check only the primary site's CPU utilization.", "Normal production utilization does not demonstrate recovery capability."],
    ["Shorten the written RTO to one hour without architecture changes.", "Changing a document does not improve or demonstrate recovery performance."],
  ], "A backup is useful only if restoration works; include credentials, networking, dependencies and business validation in recovery tests."],
  ["resilience", "An EC2 service writes its only persistent state to instance store. The team plans to stop and start instances during maintenance. Which TWO changes protect data from this lifecycle event?", [0, 1], [
    ["Move required persistent state to storage with the appropriate independent persistence, such as EBS.", "EBS can preserve data across instance stops when configured and retained appropriately."],
    ["Create and test backups independent of the instance host.", "Independent backups protect against host loss and other failures beyond simple instance restart."],
    ["Assume instance store persists through stop and start.", "Instance-store data is lost when the instance stops or terminates."],
    ["Assign a new Elastic IP before stopping the instance.", "Network addresses do not preserve local storage."],
    ["Create an AMI and assume it automatically includes all instance-store data.", "An ordinary EBS-backed AMI does not preserve an instance's transient instance-store volumes."],
  ], "Treat instance store as ephemeral; persistence and recoverability need explicit storage and backup design."],
  ["resilience", "A company uses asynchronous cross-Region replication. During a sudden regional outage, the replica is promoted before the latest writes arrive. What limitation should the recovery plan acknowledge?", [0], [
    ["Some recently acknowledged writes may be lost; RPO depends on replication lag and recovery behavior.", "Asynchronous replication can acknowledge primary writes before the remote copy is durable."],
    ["All acknowledged writes are guaranteed in the remote Region by definition.", "That guarantee does not follow from asynchronous replication."],
    ["DNS failover automatically recreates missing transactions.", "DNS changes route traffic and do not recover unreplicated data."],
    ["A larger replica connection pool guarantees zero RPO.", "Connection pooling does not change the durability timing of cross-Region replication."],
  ], "Do not equate multi-Region replication with zero data loss; measure lag and design around the replication guarantees."],
  ["resilience", "A company uses CloudFormation to reproduce its application stack in a recovery Region. Which statement correctly describes what the templates provide?", [0], [
    ["Repeatable infrastructure provisioning; application data still needs a separate replication or backup plan.", "Infrastructure definitions recreate resources but do not inherently preserve their current business data."],
    ["Automatic continuous replication of every database row.", "CloudFormation is infrastructure as code rather than database replication."],
    ["Guaranteed recovery capacity in every AZ without reservations.", "A valid template does not guarantee underlying service capacity is available."],
    ["Automatic recovery of every secret value from the failed Region.", "Secrets and encryption dependencies must be made available through an explicit recovery design."],
  ], "Infrastructure as code reduces recovery drift; test regional dependencies, quotas, artifacts, keys and data availability separately."],
]);

export const cost = bank("cost", [
  ["cost", "A company has a steady baseline of EC2 usage for the next year but expects to change instance families and Regions. It wants a flexible usage discount and can commit to a consistent hourly spend. Which option best fits?", [0], [
    ["Compute Savings Plans.", "Compute Savings Plans exchange an hourly spend commitment for discounts with broad eligible compute flexibility."],
    ["Spot Instances as a guaranteed uninterrupted baseline.", "Spot capacity may be reclaimed and is not guaranteed uninterrupted capacity."],
    ["On-Demand Capacity Reservations as the discount commitment alone.", "Capacity Reservations assure capacity but do not themselves provide a discounted usage commitment."],
    ["An EC2 Instance Savings Plan for a single instance family in one Region.", "Its family-and-Region scope does not match the requested flexibility across both families and Regions."],
  ], "Savings Plans discount eligible usage through a spend commitment; unused commitment is still charged and does not reserve capacity."],
  ["resilience", "A business must be able to launch a specific EC2 instance type in a particular AZ during a planned event. A discounted bill alone is insufficient. Which option directly reserves the required capacity?", [0], [
    ["An appropriately configured EC2 On-Demand Capacity Reservation.", "A Capacity Reservation holds matching instance capacity in the specified AZ."],
    ["A Compute Savings Plan alone.", "Savings Plans provide billing discounts rather than capacity assurance."],
    ["A regional Reserved Instance discount alone.", "A regional RI does not reserve capacity in one specific AZ."],
    ["A Spot request at a low maximum price.", "Spot depends on spare capacity and cannot guarantee the required launch capacity."],
  ], "Separate capacity assurance from discounts; a matching reservation must cover the instance attributes and AZ required."],
  ["cost", "A company's production fleet is sized for rare peaks. CPU and memory remain low most days. The company wants to reduce spend while maintaining performance. What should it do first?", [0], [
    ["Analyze representative utilization and right-size instances, then validate with load tests.", "Measured sizing can eliminate unused resources while checking that peak performance requirements remain met."],
    ["Buy three-year commitments for all current oversized instances immediately.", "Committing before optimization can lock in unnecessary spending."],
    ["Double every instance size to avoid analysis.", "Larger instances generally increase the underutilization and cost problem."],
    ["Delete production monitoring to reduce CPU usage.", "Removing visibility makes sizing and reliability harder to validate."],
  ], "Optimize demand and resource size before committing to discounted usage; include memory, I/O and peak behavior in the analysis."],
  ["cost", "A company stores large logs in S3. They are read frequently for 30 days, rarely for the next 60 days, and must then be retained cheaply for years. Which feature automates the storage transitions?", [0], [
    ["S3 Lifecycle rules with transitions chosen for access and retention requirements.", "Lifecycle rules automate age-based transitions into appropriate lower-cost storage classes."],
    ["S3 Intelligent-Tiering with no explicit age-based transitions to the required archive class.", "It adapts to actual access rather than implementing the specified fixed-age storage schedule."],
    ["S3 replication that copies every log to another Standard-class bucket but never transitions either copy.", "Creating an additional Standard copy does not implement the requested lower-cost age-based tiering."],
    ["S3 Versioning alone with no noncurrent-version policy.", "Versioning preserves versions but does not automatically optimize their storage class."],
  ], "Lifecycle rules automate known age-based patterns; include minimum storage durations, retrieval costs and noncurrent versions."],
  ["cost", "A company wants to identify which AWS service caused last month's cost increase, group costs by account and inspect usage trends. Which tool best supports this analysis?", [0], [
    ["AWS Cost Explorer.", "Cost Explorer visualizes historical cost and usage and supports filters and groupings."],
    ["AWS Budgets threshold emails without historical cost exploration.", "Alerts can flag spending limits but are not the primary interface for grouping and investigating service trends."],
    ["CloudWatch resource utilization dashboards without billing data.", "Utilization metrics do not by themselves provide service-level billed-cost attribution."],
    ["Trusted Advisor cost recommendations alone.", "Optimization recommendations do not replace detailed historical cost grouping and trend exploration."],
  ], "Use Cost Explorer to investigate trends; use detailed billing exports when deeper line-item analysis is required."],
  ["cost", "A team wants email notifications when forecast monthly AWS spending exceeds a threshold. It does not need automatic workload termination. Which service should it configure?", [0], [
    ["AWS Budgets with forecast-based alerts.", "Budgets can notify subscribers when actual or forecast costs exceed configured thresholds."],
    ["A CloudWatch alarm on estimated charges that checks only current accrued cost.", "An accrued-cost threshold does not implement the requested forecast-based monthly budget alert."],
    ["A Cost Explorer saved report that nobody schedules or monitors.", "An interactive report by itself does not send the requested threshold notifications."],
    ["Cost allocation tags with no budget or alert configuration.", "Tags help attribute costs but do not independently forecast spending and notify subscribers."],
  ], "Budgets provide spending visibility and alerts; an alert alone does not impose a hard spending cap."],
  ["cost", "A private workload in AZ B sends high-volume internet traffic through a zonal NAT gateway in AZ A. The company wants to reduce unnecessary cross-AZ transfer while keeping this zonal NAT design. Which change should it evaluate?", [0], [
    ["Use a NAT gateway in AZ B and route that workload locally, comparing total gateway and transfer costs.", "Local routing removes this cross-AZ NAT path, though the additional gateway has its own charges."],
    ["Add another NAT gateway in AZ A and split requests evenly.", "Traffic from AZ B would still cross zones."],
    ["Purchase a Compute Savings Plan to remove NAT cross-AZ transfer charges.", "Compute usage commitments do not remove networking transfer charges."],
    ["Move traffic through a third AZ first.", "Additional cross-zone paths do not eliminate the original transfer problem."],
  ], "Optimize network paths using total cost and resilience requirements; additional gateways can offset some transfer savings."],
  ["cost", "A business runs SQL analytics on S3 and pays for bytes scanned. Most queries need only a few columns and one day's data. Which TWO changes most directly reduce scan volume?", [0, 1], [
    ["Convert suitable datasets to compressed columnar Parquet.", "Columnar reads and compression reduce the data needed for selected columns."],
    ["Partition data by date and include partition predicates in queries.", "Partition pruning limits reads to the relevant date paths."],
    ["Use SELECT * for every query.", "Selecting all columns prevents column pruning from reducing unnecessary reads."],
    ["Store one uncompressed text file containing all historical data.", "This structure limits pruning and can require scanning much more data."],
    ["Run the same unfiltered SELECT * queries from more concurrent sessions.", "Parallel callers may change throughput but do not reduce the bytes each unpruned query scans."],
  ], "For scan-priced analytics, data layout and query predicates often save more than changing who submits the query."],
  ["cost", "A development account has unattached EBS volumes and obsolete snapshots after experiments end. The team wants to reclaim unnecessary storage costs without losing required recovery points. What should it do?", [0], [
    ["Inventory ownership and retention needs, then delete confirmed unused volumes and obsolete snapshots.", "Removing unneeded billed storage reduces cost while preserving artifacts still required for recovery."],
    ["Stop unrelated EC2 instances and assume all EBS charges disappear.", "EBS storage can remain billable when instances are stopped or volumes are detached."],
    ["Delete every snapshot before checking retention requirements.", "Unreviewed deletion can destroy required recovery history."],
    ["Purchase EC2 Reserved Instances to cover detached EBS storage charges.", "EC2 instance discounts do not eliminate charges for unused EBS volumes and snapshots."],
  ], "Detached resources can still cost money; use ownership and retention policies to make cleanup safe and repeatable."],
  ["cost", "A company serves a popular static website from S3. Most visitors request identical content. Which TWO measures can reduce repeated origin transfers while maintaining responsive delivery?", [0, 1], [
    ["Place CloudFront in front of the S3 origin.", "Edge caching can reduce repeated origin fetches and provides an optimized viewer delivery path."],
    ["Use suitable Cache-Control headers and reusable cache keys for shared assets.", "Correct cache lifetimes and keys increase cache reuse for identical content."],
    ["Include a unique random value in every asset URL.", "A unique URL per request prevents cache reuse."],
    ["Disable caching for all images and scripts.", "Disabling cache forces more origin requests and transfers."],
    ["Enable S3 Transfer Acceleration and assume it provides a reusable viewer response cache.", "Acceleration changes the transfer path but does not replace CloudFront's edge response cache."],
  ], "Cache appropriate shared responses and compare total request and transfer costs; never share personalized content under an unsafe cache key."],
]);
