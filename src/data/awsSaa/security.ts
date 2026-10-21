import { bank } from "./schema";

export const identity = bank("identity", [
  ["security", "An application on EC2 must read objects from one S3 bucket. Security requires automatically rotated credentials and no secrets in the deployment package. Which solution meets these requirements with the least administration?", [0], [
    ["Attach an IAM role through an instance profile with access to the required bucket.", "EC2 supplies and rotates temporary role credentials; the policy can restrict access to that bucket."],
    ["Store an IAM user's access keys in the AMI.", "Long-lived credentials become embedded in every image and need separate rotation."],
    ["Store an IAM user's keys in encrypted Parameter Store values and rotate them with each release.", "Encrypted storage protects the keys, but release-based rotation still requires managing long-lived credentials."],
    ["Add the EC2 instance ID to the bucket policy without assigning an instance role.", "An instance ID is not a credential-bearing IAM principal that can authenticate S3 requests."],
  ], "Give workloads temporary role credentials and only the permissions their operations require."],
  ["security", "A partner in another AWS account must assume a role to read billing exports. The partner serves many customers. Which TWO controls directly address cross-account trust and the confused deputy problem?", [0, 1], [
    ["Trust the partner's intended AWS principal in the role trust policy.", "The trust policy controls which external principal can assume the role."],
    ["Require a unique external ID agreed with the partner in the trust policy.", "The external ID binds the assumption request to the correct customer relationship."],
    ["Email an IAM user's access keys to the partner.", "Static keys bypass the intended role-assumption flow and complicate revocation."],
    ["Require the partner's customers to share the same role session name.", "Session names aid identification but do not bind a request to a unique customer relationship."],
    ["Grant the partner permission to change the role's trust policy.", "The partner should not be able to broaden its own trust relationship."],
  ], "Cross-account role access needs both appropriate trust and caller permissions; external IDs mitigate confused deputy risks."],
  ["security", "A developer has an IAM policy allowing EC2 termination. The account's organizational unit has an SCP explicitly denying ec2:TerminateInstances. The developer tries to terminate an instance. What happens?", [0], [
    ["The request is denied because an explicit deny takes precedence.", "An identity policy cannot override an applicable explicit deny in an SCP."],
    ["The request succeeds because identity policies override organization policies.", "SCPs set permission boundaries for member accounts rather than being overridden by user policies."],
    ["The request succeeds after the developer attaches AdministratorAccess.", "An additional identity-policy allow cannot override an applicable SCP explicit deny."],
    ["The request succeeds if a permissions boundary allows termination.", "A permissions boundary also limits permissions; it cannot override the SCP deny."],
  ], "SCPs limit maximum permissions in member accounts; they do not grant permissions, and explicit denies prevail."],
  ["security", "A workload in account B needs to download an S3 object encrypted with a customer managed KMS key in account A. Its S3 access is already allowed. Which TWO additional permissions are needed for cross-account decryption?", [0, 1], [
    ["Allow the external principal to use the key in account A's KMS key policy.", "The key-owning account must authorize the external account or principal."],
    ["Allow kms:Decrypt on that key in the caller's IAM policy in account B.", "Cross-account KMS use also requires permission on the caller's side."],
    ["Add only s3:GetObject to the KMS key policy.", "S3 object actions do not authorize the separate kms:Decrypt operation."],
    ["Grant kms:Encrypt without kms:Decrypt to the caller.", "Encryption permission does not allow decryption of the downloaded object."],
    ["Allow account B only in the S3 bucket policy and make no KMS policy changes.", "The bucket policy cannot replace the independent key-owner authorization check."],
  ], "S3 authorization and KMS authorization are separate checks; cross-account KMS access requires both sides to allow it."],
  ["security", "An application retrieves a database password at startup. The password must rotate automatically, and application releases must not be required during rotation. What is the most suitable design?", [0], [
    ["Store the password in Secrets Manager with rotation and retrieve it using an application role.", "Secrets Manager supports managed secret retrieval and rotation workflows for supported databases."],
    ["Put the password in source control and encrypt the repository.", "Repository encryption does not provide database credential rotation or runtime access control."],
    ["Hard-code the password in a Lambda environment variable and rotate the deployment monthly.", "This couples secret changes to deployments and does not meet automatic runtime rotation."],
    ["Store a SecureString in Parameter Store and assume encryption automatically rotates the database password.", "Secure storage alone does not configure a rotation workflow that changes the database credential."],
  ], "Use a secret store and temporary workload identity; handle cached connections and refresh behavior during rotation."],
  ["security", "A company wants a centrally managed record of API activity across all Regions and member accounts. Logs must be delivered to a security account. Which solution best meets this requirement?", [0], [
    ["Create a multi-Region organization trail in CloudTrail with a protected central S3 destination.", "Organization trails provide centralized account coverage; a multi-Region trail includes activity across Regions."],
    ["Enable only VPC Flow Logs in the production VPC.", "Flow logs describe network flows rather than IAM and service API calls."],
    ["Use CloudWatch CPU metrics for every instance.", "Resource utilization metrics do not record API identities and actions."],
    ["Enable AWS Config recording only, with no CloudTrail trail.", "Configuration history is useful but does not replace a centralized record of API calls and their identities."],
  ], "CloudTrail answers who called which API; protect its storage and configure relevant data events separately when needed."],
  ["security", "A company must prevent S3 objects from becoming publicly accessible even if a developer accidentally adds a public bucket policy. Which control most directly meets this requirement?", [0], [
    ["Enable all S3 Block Public Access settings at the account level.", "Account-level settings provide a guardrail against public ACLs and policies across the account's buckets."],
    ["Enable S3 Versioning on every bucket.", "Versioning preserves object versions but does not block public authorization."],
    ["Enable default server-side encryption.", "Encryption at rest does not prevent authorized public reads through S3."],
    ["Configure only a private S3 gateway endpoint and leave bucket authorization unchanged.", "An endpoint changes the VPC access path but does not prevent public policies from authorizing other paths."],
  ], "Encryption, durability and access control solve different problems; use Block Public Access to prevent public exposure."],
  ["security", "A company wants to detect buckets that lack required tags and automatically invoke a remediation workflow after a configuration change. Which service should evaluate compliance?", [0], [
    ["AWS Config rules with remediation actions.", "Config records resource configurations and evaluates them against compliance rules."],
    ["Amazon Inspector only.", "Inspector focuses on vulnerability management rather than general resource-tag compliance."],
    ["CloudTrail management-event logging without a configuration evaluation rule.", "Audit logs record changes but do not themselves continuously evaluate the resulting tag compliance."],
    ["Amazon GuardDuty threat detection alone.", "GuardDuty detects suspicious activity rather than evaluating arbitrary required-tag rules."],
  ], "Use Config for resource-state compliance and CloudTrail for the API activity that changed that state."],
  ["security", "A mobile app needs users to sign in through a social identity provider and then obtain temporary, limited AWS credentials for direct S3 uploads. Which combination fits?", [0], [
    ["Federated sign-in with Amazon Cognito and an identity pool mapped to restricted IAM roles.", "Cognito supports user federation and identity pools exchange identities for temporary AWS credentials."],
    ["Embed one IAM user's access keys in the mobile application.", "Anyone extracting the app can reuse the shared long-lived keys."],
    ["Use only a Cognito user pool JWT as the S3 request's AWS signing credentials.", "A user pool token is not an AWS access-key pair; identity federation or an application-mediated flow is needed."],
    ["Create an IAM user with long-lived access keys for every social login.", "This adds credential provisioning and rotation rather than exchanging federated identities for temporary credentials."],
  ], "User authentication and AWS resource authorization are separate steps; identity pools bridge federated identity to IAM roles."],
  ["security", "A private S3 bucket contains paid videos delivered through CloudFront. Viewers should use expiring URLs, and direct anonymous S3 downloads must fail. Which TWO changes meet these requirements?", [0, 1], [
    ["Use CloudFront signed URLs for viewer authorization.", "Signed URLs restrict viewer access and can expire after the purchased access period."],
    ["Use origin access control and a bucket policy restricted to the intended distribution.", "OAC authorizes CloudFront's origin requests without making the bucket public."],
    ["Make the bucket public and hide its URL.", "An undisclosed URL does not prevent direct unauthorized downloads."],
    ["Use S3 website hosting as the origin with OAC.", "OAC is supported for S3 bucket origins, not S3 website endpoints."],
    ["Rely only on S3 default encryption.", "Encryption at rest does not authenticate viewers or restrict direct reads."],
  ], "Protect both boundaries: signed viewer access at CloudFront and restricted origin access at S3."],
]);

export const networking = bank("networking", [
  ["security", "EC2 instances in private IPv4 subnets must download patches from internet repositories. External hosts must not initiate connections to these instances. Which architecture meets the requirement?", [0], [
    ["Route outbound traffic through a public NAT gateway in a public subnet with an internet gateway.", "The NAT gateway permits connections initiated by the private instances and translates return traffic."],
    ["Attach an internet gateway and give every instance a public IPv4 address.", "This exposes direct internet addressing rather than preserving the private-subnet design."],
    ["Route internet traffic to an S3 gateway endpoint.", "An S3 endpoint provides access to S3, not arbitrary patch repositories."],
    ["Use a private NAT gateway with a route to an internet gateway.", "An internet gateway drops traffic routed through a private NAT gateway."],
  ], "For private IPv4 internet egress, use a public NAT gateway with a complete public-subnet route to the internet gateway."],
  ["cost", "A fleet in private subnets transfers large amounts of data to same-Region S3 through a NAT gateway. The company wants to reduce NAT processing charges without opening internet access. What should it add?", [0], [
    ["An S3 gateway VPC endpoint associated with the fleet's route tables.", "S3 gateway endpoints route eligible S3 traffic privately and have no endpoint hourly or data-processing charge."],
    ["A second NAT gateway in the same subnet.", "Additional NAT gateways do not eliminate NAT processing for the S3 traffic."],
    ["A public IP address on each instance.", "Public addressing changes the security design and is unnecessary for private S3 access."],
    ["A Route 53 public hosted zone.", "DNS hosting alone does not change the traffic's network path."],
  ], "Use gateway endpoints for eligible same-Region S3 or DynamoDB access; attach them to the route tables that actually carry the traffic."],
  ["security", "A security team needs to block one abusive IPv4 CIDR for all resources in a subnet. Other approved sources must continue working. Which control supports an explicit subnet-level deny?", [0], [
    ["Add a correctly ordered deny rule to the subnet's network ACL.", "NACLs support allow and deny rules evaluated in order at subnet boundaries."],
    ["Add a deny rule to every security group.", "Security groups support allow rules, not explicit deny rules."],
    ["Create an IAM deny for the CIDR on the EC2 role.", "IAM role policies do not filter arbitrary incoming network packets."],
    ["Disable DNS resolution for the VPC.", "Disabling DNS does not block traffic addressed to an IP."],
  ], "NACLs are stateless subnet filters with explicit deny rules; account for both request and return traffic."],
  ["performance", "Two VPCs are peered: A to B and B to C. An application in A cannot reach a private service in C even after routes are added through B. What is the architectural problem?", [0], [
    ["VPC peering does not provide transitive routing; use direct peering or a transit gateway.", "A peering connection cannot forward traffic through another VPC's peering connection."],
    ["Peering requires every instance to have a public IP address.", "Peering carries private traffic and does not require public instance addresses."],
    ["Peering works only between different AWS accounts.", "VPC peering can connect VPCs within one account or across accounts."],
    ["Source/destination checking on B's ordinary instances must be disabled to make peering transitive.", "Changing an instance setting does not add transitive routing to VPC peering."],
  ], "For a hub connecting many VPCs and on-premises networks, evaluate Transit Gateway rather than assuming peering is transitive."],
  ["security", "A software provider exposes a service behind a Network Load Balancer. Customers need private access from their own VPCs without full network peering or non-overlapping CIDR blocks. What should the provider use?", [0], [
    ["A VPC endpoint service using AWS PrivateLink.", "PrivateLink exposes a specific service through consumer interface endpoints without broad VPC routing."],
    ["A public ALB with an obscure hostname.", "A hidden public hostname does not provide private connectivity."],
    ["A full mesh of VPC peering connections.", "Peering requires non-overlapping CIDRs and grants network connectivity beyond a single endpoint service."],
    ["A shared transit gateway without resolving the overlapping customer CIDRs.", "Transit Gateway connects networks and cannot simply route conflicting customer address spaces as distinct service endpoints."],
  ], "PrivateLink gives private access to a service; peering and Transit Gateway connect networks."],
  ["performance", "A company transfers sustained large datasets from its data center and requires a dedicated private connection to AWS. It also requires encryption in transit regardless of circuit privacy. Which design meets both requirements?", [0], [
    ["AWS Direct Connect with an appropriate VPN overlay or supported MACsec configuration.", "Direct Connect supplies dedicated connectivity; encryption must be supplied explicitly where required."],
    ["Direct Connect alone because every circuit automatically encrypts all traffic.", "A dedicated connection does not by itself guarantee end-to-end encryption."],
    ["An internet gateway attached to the data center.", "An internet gateway is a VPC component, not a dedicated on-premises circuit."],
    ["A Site-to-Site VPN over the public internet as the only connection.", "VPN encryption meets the encryption requirement but does not provide the requested dedicated private circuit."],
  ], "Private connectivity and encryption are separate requirements; validate the encryption scope of the chosen hybrid design."],
  ["resilience", "A team uses zonal public NAT gateways. Private instances run in two Availability Zones and need internet egress during the loss of either zone. Which design avoids a single-zone NAT dependency?", [0], [
    ["Deploy a zonal NAT gateway in each AZ and route each private subnet to its local gateway.", "Each AZ retains its own egress path if the other AZ's gateway becomes unavailable."],
    ["Deploy one zonal NAT gateway and use it from both AZs.", "Both AZs depend on the gateway's single Availability Zone."],
    ["Put two zonal NAT gateways in the first AZ.", "Both gateways remain exposed to the same AZ failure."],
    ["Replace the gateways with one EC2 NAT instance in the first AZ.", "One NAT instance is also a single-zone dependency and requires more administration."],
  ], "For zonal NAT designs, align private-subnet routes with per-AZ gateways; also evaluate current regional NAT capabilities separately."],
  ["security", "An application uses globally routable IPv6 addresses. It must initiate outbound internet connections while blocking internet-initiated IPv6 connections. Which VPC component is designed for this?", [0], [
    ["An egress-only internet gateway with an IPv6 default route.", "An egress-only gateway provides outbound-only IPv6 internet connectivity."],
    ["A normal internet gateway with unrestricted security rules.", "That combination does not enforce outbound-only connectivity."],
    ["A network ACL permitting all IPv6 traffic in both directions.", "Unrestricted stateless rules do not enforce connections initiated only from inside the VPC."],
    ["A security group allowing all IPv6 inbound traffic with no egress rules.", "This reverses the desired access direction rather than allowing outbound connections and their responses."],
  ], "Use an egress-only internet gateway for native outbound-only IPv6 connectivity."],
  ["security", "A web tier and a database tier share a VPC. Only instances assigned to the web tier's security group should reach TCP port 5432 on the database, even as instances scale. What should the database security group allow?", [0], [
    ["Inbound TCP 5432 with the web tier's security group as the source.", "A security group reference follows the authorized tier as its instance addresses change."],
    ["Inbound TCP 5432 from 0.0.0.0/0.", "This permits every IPv4 source allowed by the network path, exceeding the web-tier boundary."],
    ["Inbound TCP 5432 from the current web server's public IP only.", "A fixed public address does not represent all dynamically scaling private web instances."],
    ["No inbound rule because security groups are stateless.", "Security groups are stateful, but an initiating connection still needs an appropriate inbound allow."],
  ], "Reference security groups to express application-tier relationships; stateful return traffic is automatically allowed."],
  ["performance", "On-premises clients must resolve a private hosted zone in Route 53 over an existing VPN. The company does not want to maintain DNS forwarder EC2 instances. Which solution fits?", [0], [
    ["Route 53 Resolver inbound endpoints with conditional forwarding from on-premises DNS.", "Inbound endpoints accept hybrid DNS queries and resolve VPC-associated private zones."],
    ["Route 53 Resolver outbound endpoints only.", "Outbound endpoints forward queries from VPCs to external resolvers, the opposite direction."],
    ["Publish all private records in a public hosted zone.", "This changes the confidentiality and DNS design instead of enabling private hybrid resolution."],
    ["Associate an Elastic IP with the private hosted zone.", "Hosted zones do not accept Elastic IP attachments."],
  ], "Resolver inbound endpoints serve queries coming into AWS; outbound endpoints forward queries leaving AWS."],
]);
