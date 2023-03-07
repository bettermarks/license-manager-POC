import { NodeSelector } from "./types";

export const APP_NODE_POOL_LABELS: NodeSelector = {
  nodetype: "application",
};

/**
 * Name of the secret which is used by service chart to look up application secret.
 * This secret is created by AWS Secrets helper in bm-operations project. https://github.com/bettermarks/bm-operations/blob/master/cdk8s/apps/licensing.ts
 */
export const APPLICATION_SECRET = "licensing-secret";
/**
 * Name of the secret which is used by service chart to look up Postgres DB credentials.
 * This secret is created  by AWS Secrets helper in bm-operations project. https://github.com/bettermarks/bm-operations/blob/master/cdk8s/apps/licensing.ts
 */
export const POSTGRES_SECRET = "licensing-postgres-secret";
/**
 * Name of the secret used by Service Account to pull image from AWS ECR registry.
 * This secret is created by AWS Registry Helper Cron. https://github.com/bettermarks/bm-operations/blob/master/cdk8s/apps/licensing.ts
 */
export const REGISTRY_CREDENTIALS = "registry-credentials";
/**
 * Name of the image used for postgres database.
 */
export const POSTGRES_IMAGE = "postgres:14";
