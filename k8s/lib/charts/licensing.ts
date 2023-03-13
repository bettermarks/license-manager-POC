import { Chart, ChartProps } from "cdk8s";
import { HttpIngressPathType, ImagePullPolicy } from "cdk8s-plus-24";
import { Construct } from "constructs";
import {
  EnvFromSource,
  IntOrString,
  KubeIngress, ResourceRequirements
} from "../../imports/k8s";

import { APPLICATION_CONFIG } from "../config";
import { LicensingConfigMap } from "../licensing-configmap";
import { LicensingService } from "../services/licensing-service";
import { Namespace, NodeSelector, Segment } from "../types";

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
  serviceAccountName: string;
  segment: Segment;
  name: string;
  nodeSelector?: NodeSelector;
  apiResources?: ResourceRequirements;
  /**
   * API replicas
   * @default 3
   */
  apiReplicas?: number;
};

/**
 * Deploys Licensing server.
 */
export class LicensingChart extends Chart {
  constructor(scope: Construct, id: string, props: LicensingChartProps) {
    super(scope, id, props);

    const {
      namespace = Namespace.LICENSING,
      apiReplicas = 1,
      apiResources,
      applicationSecret,
      image,
      nodeSelector,
      postgresSecret,
      segment,
      serviceAccountName,
      name,
    } = props;

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

    const apiName = `${name}-api`;
    /**
     * DeploymentID is a unique identifier for each deployment
     */
    const deploymentId = Date.now().toString(16); // TODO: this should be rethought
    const licensingService = new LicensingService(this, `${apiName}-service`, {
      name: apiName,
      namespace,
      replicas: apiReplicas,
      serviceAccountName,
      nodeSelector: nodeSelector,
      deploymentId: `${apiName}-${deploymentId}`,

      initContainers: [
      ],
      containers: [
        {
          name: apiName,
          image,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          ports: [
            {
              containerPort: 8000,
            },
          ],
          resources: apiResources,
          envFrom: applicationEnv,
          readinessProbe: {
            httpGet: {
              port: IntOrString.fromNumber(8000),
              path: "/v1/status",
            },
            initialDelaySeconds: 10,
          },
          livenessProbe: {
            httpGet: {
              port: IntOrString.fromNumber(8000),
              path: "/v1/status",
            },
            initialDelaySeconds: 10,
          },
        },
      ],
      servicePort: 80,
      containerPort: 8000,
    });

    if (segment === Segment.LOC00) {
      /**
       * Create ingress
       */
      new KubeIngress(this, `${name}-ingress`, {
        metadata: {
          name: `${name}-ingress`,
        },
        spec: {
          ingressClassName: "nginx",
          rules: [
            {
              http: {
                paths: [
                  {
                    path: "/",
                    pathType: HttpIngressPathType.PREFIX,
                    backend: {
                      service: {
                        name: licensingService.service!.name,
                        port: {
                          number: 80,
                        },
                      },
                    },
                  },
                ],
              },
            },
          ],
        },
      });
    }
  }
}
