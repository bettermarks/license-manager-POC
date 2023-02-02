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
import { Namespace, NodeSelector, Segment } from "../types";

import { LicensingService } from "../services/licensing-service";
import { APPLICATION_CONFIG } from "../config";
import { POSTGRES_IMAGE } from "../constants";
import { LicensingConfigMap } from "../licensing-configmap";


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
 * Deploys Licensing server.
 */
export class LicensingChart extends Chart {
  constructor(scope: Construct, id: string, props: LicensingChartProps) {
    super(scope, id, props);

    const {
      namespace = Namespace.DEFAULT,
      apiReplicas = 3,
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
        namespace: props.namespace,
      },
      imagePullSecrets: imagePullSecrets?.map((secretRef) => ({ name: secretRef })),
    });

    const role = new KubeRole(this, `${name}-role`, {
      metadata: {
        name: `${name}-role`,
        namespace: props.namespace,
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
        namespace: props.namespace,
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
          name: new LicensingConfigMap(this, `${name}-configmap`, {
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
      {
        secretRef: {
          name: applicationSecret,
        },
      },
    ];
    /**
     * DeploymentID is a unique identifier for each deployment
     */
    const deploymentId = Date.now().toString(16);  // TODO: this should be rethought
    const licensingService = new LicensingService(this, `${name}-service`, {
      name: name,
      namespace,
      replicas: apiReplicas,
      serviceAccountName: serviceAccount.name,
      nodeSelector: nodeSelector,
      deploymentId: `${name}-${deploymentId}`,

      initContainers: [
        {
          name: `${name}-wait-for-database`,
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
          name: `${name}-migration`,
          image: image,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          command: ["python3.8", "manage.py", "migrate"],
          envFrom: applicationEnv,
          resources: migrationJobResources,
        },
        {
          name: `${name}-load-fixtures`,
          image: image,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          command: ["bash", "-c"],
          args: [
            `python3.8 manage.py loaddata system.yaml && \\
             python3.8 manage.py update_or_create_su --username=$(SUPERUSER_NAME) --email=$(SUPERUSER_EMAIL) --password=$(SUPERUSER_PASSWORD) && \\
             python3.8 manage.py bm_fixtures && \\
             python3.8 manage.py oauth_clients --client_id=bm_edu_$(SEGMENT)\\
                --client_secret=$(OAUTH2_CLIENT_SECRET_EDU)\\
                --name="NSP $(SEGMENT)"\\
                --redirect_uris=$(OAUTH2_REDIRECT_URI_GLU) && \\
             python3.8 manage.py oauth_clients --client_id=bm_edu_$(SEGMENT)_kong\\
                --client_secret=$(OAUTH2_CLIENT_SECRET_KONG)\\
                --name="NSP $(SEGMENT) kong"\\
                --redirect_uris=$(OAUTH2_REDIRECT_URI_KONG)`,
          ],
          envFrom: applicationEnv,
          resources: loadFixturesJobResources,
        },
      ],
      containers: [
        {
          name: name,
          image: image,
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
              path: "/status",
            },
            initialDelaySeconds: 10,
          },
          livenessProbe: {
            httpGet: {
              port: IntOrString.fromNumber(8000),
              path: "/status",
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
