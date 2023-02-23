import { ResourceRequirements } from "../imports/k8s";
/**
 * Stages
 */
export enum Stage {
  LOC = "loc",
  DEV = "dev",
  CI = "ci",
  PRO = "pro",
}

/**
 * Segments
 */
export enum Segment {
  LOC00 = "loc00",
  DEV00 = "dev00",
  CI00 = "ci00",
  CI01 = "ci01",
  PRO00 = "pro00",
}

/**
 * Defines the type defnition of labels in key-value format
 * - Applied to Nodepools when creating K8S cluster
 * - Applied to Deployment definitions at pod spec level when creating a deployment
 */
export type NodeSelector = {
  nodetype: string;
};

export type ApplicationConfig = {
  LOG_HANDLER: string;
  LOG_LEVEL: LogLevel;
  DATABASE_USER: string;
  DATABASE_HOST: string;
  DATABASE_PORT: string;
  DATABASE_NAME: string;
  FORWARDED_ALLOW_IPS: string;
};

/**
 * Deployment configuration
 */
export type DeploymentConfig = {
  /**
   * Migration job resources
   */
  migrationJobResources: ResourceRequirements;
  /**
   * Load fixtures job resources
   */
  loadFixturesJobResources: ResourceRequirements;
  /**
   * API resources
   */
  apiResources: ResourceRequirements;
  /**
   * API replicas
   */
  apiReplicas: number;
};

/**
 * Log level
 */
export enum LogLevel {
  INFO = "INFO",
  WARNING = "WARNING",
  ERROR = "ERROR",
  DEBUG = "DEBUG",
}

/**
 * Namespaces
 */
export enum Namespace {
  DEFAULT = "default",
  LICENSING = "licensing",
}
