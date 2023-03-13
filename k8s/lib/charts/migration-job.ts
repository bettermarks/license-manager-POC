import { Chart, ChartProps } from "cdk8s";
import { ImagePullPolicy } from "cdk8s-plus-24";
import {
  EnvFromSource,
  Quantity,
  ResourceRequirements,
} from "../../imports/k8s";
import { Construct } from "constructs";

import { NodeSelector, Segment, Namespace } from "../types";
import { POSTGRES_IMAGE } from "../constants";
import { APPLICATION_CONFIG } from "../config";
import { LicensingConfigMap } from "../licensing-configmap";
import { LicensingJob } from "../jobs";


/**
 * This class is the implementation detail of Licensing deployment.
 */
export type LicensingChartProps = ChartProps & {
  /**
   * Docker image for Licensing
   */
  image: string;
  /**
   * Name of the secret containing Postgres credentials
   *
   * Required keys:
   * - DB_HOST
   * - DB_PORT
   * - DB_USER
   * - DB_PASSWORD
   * - DB_NAME
   */
  postgresSecret: string;
  /**
   * Name of the secret containing necessary credentials for running the service.
   *
   * Required keys:
   */
  applicationSecret?: string;
  segment: Segment;
  name: string;
  serviceAccountName: string;
  nodeSelector?: NodeSelector;
  migrationJobResources?: ResourceRequirements;
};

export class MigrationJobChart extends Chart {
  constructor(scope: Construct, id: string, props: LicensingChartProps) {
    super(scope, id, props);

    const {
      namespace = Namespace.LICENSING,
      applicationSecret,
      image,
      nodeSelector,
      migrationJobResources,
      serviceAccountName,
      postgresSecret,
      segment,
      name,
    } = props;

    // Ideally we should not create same config map again
    const applicationEnv: EnvFromSource[] = [
      {
        configMapRef: {
          name: new LicensingConfigMap(this, `${name}-configmap`, {
            appConfig: APPLICATION_CONFIG[segment],
            name,
            namespace,
          }).configMap.name,
        },
      },
      {
        secretRef: {
          name: postgresSecret,
        },
      },
      ...(applicationSecret
        ? [
          {
            secretRef: {
              name: applicationSecret,
            },
          },
        ]
        : []),
    ];
    /**
     * Job for running database migration
     */
    new LicensingJob(this, "migrate", {
      name: `${name}-migration`,
      namespace,
      nodeSelector: nodeSelector,
      serviceAccountName,
      ttlSecondsAfterFinished: 60,
      initContainers: [
        {
          name: "wait-for-database-migration",
          image: POSTGRES_IMAGE,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          command: ["sh", "-c", "until pg_isready --host ${DB_HOST}; do sleep 1; done"],
          envFrom: applicationEnv,
          resources: {
            requests: {
              cpu: Quantity.fromNumber(0.1),
              memory: Quantity.fromString("32Mi"),
            },
            limits: {
              cpu: Quantity.fromNumber(0.2),
              memory: Quantity.fromString("64Mi"),
            },
          },
        },
      ],
      containers: [
        {
          name: "licensing-migration",
          image,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          command: ["bash", "-c"],
          args: ["alembic upgrade head"],
          envFrom: applicationEnv,
          resources: migrationJobResources,
        },
      ],
    });
  }
}