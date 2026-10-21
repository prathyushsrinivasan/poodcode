export const SAA_GUIDE = "https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html";
export const SAA_VERIFIED = "2026-10-21";
export const SAA_DOMAINS = {
  security: "Design Secure Architectures",
  resilience: "Design Resilient Architectures",
  performance: "Design High-Performing Architectures",
  cost: "Design Cost-Optimized Architectures",
} as const;
export type SaaDomain = keyof typeof SAA_DOMAINS;
export const SAA_TOPICS = [
  { id: "identity", title: "Identity & security", description: "IAM, cross-account access, encryption, secrets and governance.", source: "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html" },
  { id: "networking", title: "VPC & hybrid networking", description: "Subnets, endpoints, routing, connectivity and network boundaries.", source: "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html" },
  { id: "storage", title: "S3 & file storage", description: "Object protection, storage classes, shared files and transfers.", source: "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html" },
  { id: "compute", title: "Compute & scaling", description: "EC2, load balancing, Auto Scaling, containers and Lambda.", source: "https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html" },
  { id: "relational", title: "Relational databases", description: "RDS, Aurora, replicas, failover and connection management.", source: "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html" },
  { id: "nosql", title: "NoSQL, caching & analytics", description: "DynamoDB access patterns, caches, streams and data queries.", source: "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html" },
  { id: "integration", title: "Messaging & serverless", description: "SQS, SNS, EventBridge, workflows and decoupling.", source: "https://docs.aws.amazon.com/decision-guides/latest/decision-guides/sns-or-sqs-or-eventbridge.html" },
  { id: "edge", title: "DNS & edge delivery", description: "Route 53, CloudFront, Global Accelerator and traffic protection.", source: "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html" },
  { id: "recovery", title: "Resilience & disaster recovery", description: "RPO, RTO, backups, multi-Region designs and recovery strategies.", source: "https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html" },
  { id: "cost", title: "Cost optimization", description: "Purchase models, lifecycle policies, right sizing and data transfer.", source: "https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html" },
] as const;
export type SaaTopic = (typeof SAA_TOPICS)[number]["id"];
export interface SaaQuestion {
  id: string;
  topic: SaaTopic;
  domain: SaaDomain;
  prompt: string;
  correct: number[];
  options: { text: string; explanation: string }[];
  takeaway: string;
}
type Entry = [SaaDomain, string, number[], [string, string][], string];
/** Keep IDs stable: append new entries; never reorder a published topic. */
export function bank(topic: SaaTopic, entries: Entry[]): SaaQuestion[] {
  return entries.map(([domain, prompt, correct, options, takeaway], index) => ({
    id: `saa-${topic}-${String(index + 1).padStart(2, "0")}`, topic, domain, prompt, correct,
    options: options.map(([text, explanation]) => ({ text, explanation })), takeaway,
  }));
}
