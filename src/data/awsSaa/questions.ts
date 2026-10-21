import { identity, networking } from "./security";
import { storage, compute } from "./storageCompute";
import { relational, nosql } from "./databases";
import { integration, edge } from "./integrationEdge";
import { recovery, cost } from "./recoveryCost";

export const SAA_QUESTIONS = [
  ...identity, ...networking, ...storage, ...compute, ...relational,
  ...nosql, ...integration, ...edge, ...recovery, ...cost,
];
export const SAA_BY_ID = new Map(SAA_QUESTIONS.map((question) => [question.id, question]));
