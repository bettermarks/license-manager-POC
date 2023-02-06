import { Quantity } from "../imports/k8s";

import { ApplicationConfig, DeploymentConfig, LogLevel, Segment } from "./types";

/**
 * Information to go in secrets
 * 
 * DB related:
 * - DATABASE_HOST
 * - DATABASE_PORT
 * - DATABASE_USER
 * - DATABASE_PASSWORD
 * - DATABASE_NAME
 *
 * Application related:
 * 
 */

/**
 * Information to go in config map
 */
export const APPLICATION_CONFIG: { [key: string]: ApplicationConfig } = {
  [Segment.LOC00]: {
    LOG_HANDLER: "console",
    LOG_LEVEL: LogLevel.DEBUG,
    DATABASE_USER: "postgres",
    DATABASE_HOST: "localhost",
    DATABASE_PORT: "5432",
    DATABASE_NAME: "licm"
  },
  [Segment.DEV00]: {
    LOG_HANDLER: "console",
    LOG_LEVEL: LogLevel.DEBUG,
    DATABASE_USER: "postgres",
    DATABASE_HOST: "localhost",
    DATABASE_PORT: "5432",
    DATABASE_NAME: "licm"
  },
  [Segment.CI00]: {
    LOG_HANDLER: "console",
    LOG_LEVEL: LogLevel.DEBUG,
    DATABASE_USER: "postgres",
    DATABASE_HOST: "localhost",
    DATABASE_PORT: "5432",
    DATABASE_NAME: "licm"
  },
  [Segment.PRO00]: {
    LOG_HANDLER: "console",
    LOG_LEVEL: LogLevel.DEBUG,
    DATABASE_USER: "postgres",
    DATABASE_HOST: "localhost",
    DATABASE_PORT: "5432",
    DATABASE_NAME: "licm"
  },
};

/**
 * Deployment configuration per segment
 */
export const DEPLOYMENT_CONFIG: {
  [key: string]: DeploymentConfig;
} = {
  [Segment.DEV00]: {
    migrationJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.1),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        cpu: Quantity.fromNumber(1),
        memory: Quantity.fromString("256Mi"),
      },
    },
    loadFixturesJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.1),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        cpu: Quantity.fromNumber(1),
        memory: Quantity.fromString("256Mi"),
      },
    },
    apiResources: {
      requests: {
        cpu: Quantity.fromNumber(0.5),
        memory: Quantity.fromString("512Mi"),
      },
      limits: {
        cpu: Quantity.fromNumber(1),
        memory: Quantity.fromString("1024Mi"),
      },
    },
    apiReplicas: 3,
  },
  [Segment.CI00]: {
    migrationJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.5),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        cpu: Quantity.fromNumber(1),
        memory: Quantity.fromString("256Mi"),
      },
    },
    loadFixturesJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.5),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        cpu: Quantity.fromNumber(1),
        memory: Quantity.fromString("256Mi"),
      },
    },
    apiResources: {
      requests: {
        cpu: Quantity.fromNumber(1),
        memory: Quantity.fromString("512Mi"),
      },
      limits: {
        cpu: Quantity.fromNumber(2),
        memory: Quantity.fromString("1024Mi"),
      },
    },
    apiReplicas: 3,
  },
  [Segment.PRO00]: {
    migrationJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.5),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        cpu: Quantity.fromNumber(1),
        memory: Quantity.fromString("256Mi"),
      },
    },
    loadFixturesJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.5),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        cpu: Quantity.fromNumber(1),
        memory: Quantity.fromString("256Mi"),
      },
    },
    apiResources: {
      requests: {
        cpu: Quantity.fromNumber(1),
        memory: Quantity.fromString("512Mi"),
      },
      limits: {
        cpu: Quantity.fromNumber(2),
        memory: Quantity.fromString("1024Mi"),
      },
    },
    apiReplicas: 3,
  },
};
