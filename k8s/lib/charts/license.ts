import { Chart, ChartProps } from "cdk8s";
import { HttpIngressPathType, ImagePullPolicy } from "cdk8s-plus-24";
import {
  EnvFromSource,
  IntOrString,
  KubeIngress,
  Quantity,
  ResourceRequirements,
  KubeRole,
  KubeServiceAccount,
  KubeRoleBinding
} from "../../imports/k8s";
import { Construct } from "constructs";
import { NodeSelector, Segment } from "../types";

import { LicenseService } from "../services/license-service";
import { APPLICATION_CONFIG } from "../config";
import { POSTGRES_IMAGE } from "../constants";
import { LicenseConfigMap } from "../license-configmap";


/**
 * This class is the implementation detail of License deployment.
 */
export type LicenseChartProps = ChartProps & {
  /**
   * Docker image for License
   */
  image: string;
  /**
   * Name of the secret containing Postgres credentials
   *
   * Required keys:
   * - DATABASE_HOST
   * - DATABASE_PORT
   * - DATABASE_USER
   * - DATABASE_PASSWORD
   * - DATABASE_NAME
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
  nodeSelector?: NodeSelector;
  migrationJobResources?: ResourceRequirements;
  loadFixturesJobResources?: ResourceRequirements;
  apiResources?: ResourceRequirements;
  /**
   * API replicas
   * @default 3
  */
  apiReplicas?: number;
  /**
   * Secret names for AWS ECR registry
   * @default []
  */
  imagePullSecrets?: ReadonlyArray<string>;
};

/**
 * Deploys License server.
 */
export class LicenseChart extends Chart {
  constructor(scope: Construct, id: string, props: LicenseChartProps) {
    super(scope, id, props);

    const {
      namespace,
      apiReplicas = 1,
      apiResources,
      applicationSecret,
      image,
      loadFixturesJobResources,
      nodeSelector,
      migrationJobResources,
      postgresSecret,
      segment,
      name,
      imagePullSecrets = []
    } = props;

    const serviceAccount = new KubeServiceAccount(this, `${name}-service-account`, {
      metadata: {
        name: `${name}-service-account`,
        namespace,
      },
      imagePullSecrets: imagePullSecrets?.map((secretRef) => ({ name: secretRef })),
    });

    const role = new KubeRole(this, `${name}-role`, {
      metadata: {
        name: `${name}-role`,
        namespace,
      },
      rules: [
        {
          apiGroups: [""],
          resources: ["pods"],
          verbs: ["get", "list", "watch"],
        },
      ],
    });

    new KubeRoleBinding(this, `${name}-role-binding`, {
      metadata: {
        name: `${name}-role-binding`,
        namespace,
      },
      roleRef: {
        apiGroup: role.apiGroup,
        kind: role.kind,
        name: role.name,
      },
      subjects: [{ kind: serviceAccount.kind, name: serviceAccount.name }],
    });

    const applicationEnv: EnvFromSource[] = [
      {
        configMapRef: {
          name: new LicenseConfigMap(this, `${name}-configmap`, {
            appConfig: APPLICATION_CONFIG[segment],
            name,
            namespace
          }).configMap.name,
        },
      },
      {
        secretRef: {
          name: postgresSecret,
        },
      },
      ...(applicationSecret)
        ? [
          {
            secretRef: {
              name: applicationSecret,
            },
          },
        ]
        : []
    ];

    const apiName = `${name}-api`;
    /**
     * DeploymentID is a unique identifier for each deployment
     */
    const deploymentId = Date.now().toString(16);  // TODO: this should be rethought
    const licenseService = new LicenseService(this, `${apiName}-service`, {
      name: apiName,
      namespace,
      replicas: apiReplicas,
      serviceAccountName: serviceAccount.name,
      nodeSelector: nodeSelector,
      deploymentId: `${apiName}-${deploymentId}`,

      initContainers: [
        {
          name: `${apiName}-wait-for-database`,
          image: POSTGRES_IMAGE,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          command: ["sh", "-c", "until pg_isready --host ${DATABASE_HOST}; do sleep 1; done"],
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
        {
          name: `${apiName}-migration`,
          image,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          command: ["bash", "-c"],
          args: [
            "alembic upgrade head"
          ],
          envFrom: applicationEnv,
          resources: migrationJobResources,
        },
        {
          name: `${apiName}-load-fixtures`,
          image,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          command: ["bash", "-c"],
          args: [
            `echo "TODO: load_initial_products here"`,
          ],
          envFrom: applicationEnv,
          resources: loadFixturesJobResources,
        },
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
            host: "license.bettermarks.loc",
            http: {
              paths: [
                {
                  path: "/",
                  pathType: HttpIngressPathType.PREFIX,
                  backend: {
                    service: {
                      name: licenseService.service!.name,
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
