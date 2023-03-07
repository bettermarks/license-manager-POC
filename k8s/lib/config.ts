import { Quantity } from "../imports/k8s";

import {
  ApplicationConfig,
  DeploymentConfig,
  LogLevel,
  Segment,
} from "./types";

/**
 * Information to go in secrets
 *
 * DB related:
 * - DB_HOST
 * - DB_PORT
 * - DB_USER
 * - DB_PASSWORD
 * - DB_NAME
 *
 * Application related:
 * - APM_SECRET_TOKEN
 */

/**
 * Information to go in config map
 */
export const APPLICATION_CONFIG: { [key: string]: ApplicationConfig } = {
  [Segment.LOC00]: {
    SEGMENT: Segment.LOC00,
    LOG_FORMAT: "console",
    LOG_LEVEL: LogLevel.DEBUG,
    APM_URL: "",
    APM_ENABLED: false,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
  },
  [Segment.DEV00]: {
    SEGMENT: Segment.DEV00,
    LOG_FORMAT: "json",
    LOG_LEVEL: LogLevel.DEBUG,
    APM_URL: "https://apm.bettermarks.com",
    APM_ENABLED: true,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
  },
  [Segment.CI00]: {
    SEGMENT: Segment.CI00,
    LOG_FORMAT: "json",
    LOG_LEVEL: LogLevel.DEBUG,
    APM_URL: "https://apm.bettermarks.com",
    APM_ENABLED: true,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
  },
  [Segment.PRO00]: {
    SEGMENT: Segment.PRO00,
    LOG_FORMAT: "json",
    LOG_LEVEL: LogLevel.INFO,
    APM_URL: "https://apm.bettermarks.com",
    APM_ENABLED: true,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
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
