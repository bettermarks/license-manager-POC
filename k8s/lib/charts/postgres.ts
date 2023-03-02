import { Chart, ChartProps } from "cdk8s";
import {
  ConfigMap,
  ImagePullPolicy,
  ISecret,
  Secret,
  ServiceType,
} from "cdk8s-plus-24";
import { Construct } from "constructs";
import { IntOrString, KubeDeployment, KubeService } from "../../imports/k8s";

interface PostgresChartProps extends ChartProps {
  image: string;
  name: string;
}

export class PostgresChart extends Chart {
  /**
   * Secret with Postgres credentials
   *
   * keys:
   * - DATABASE_HOST
   * - DATABASE_PORT
   * - DATABASE_USER
   * - DATABASE_PASSWORD
   * - DATABASE_NAME
   * - POSTGRES_PASSWORD
   */
  readonly secret: ISecret;

  constructor(scope: Construct, id: string, props: PostgresChartProps) {
    super(scope, id, props);
    const { name, namespace } = props;
    const pgSecret = new Secret(this, "secret", {
      metadata: {
        name: name,
        namespace,
      },
      stringData: {
        DATABASE_PORT: "5432",
        DATABASE_USER: "postgres",
        DATABASE_PASSWORD: "postgres",
        DATABASE_NAME: "postgres",
        POSTGRES_PASSWORD: "postgres",
        POSTGRES_USER: "postgres",
        POSTGRES_DB: "postgres",
      },
    });

    const configMap = new ConfigMap(this, "initdb", {
      metadata: {
        name: `${name}-init-db-script`,
        namespace,
      },
      data: {}, // TODO: any init command?
    });

    new KubeDeployment(this, "pg-deployment", {
      metadata: {
        name,
        namespace,
        labels: {
          app: name,
        },
      },
      spec: {
        selector: {
          matchLabels: {
            app: name,
          },
        },
        replicas: 1,
        template: {
          metadata: {
            labels: {
              app: name,
            },
          },
          spec: {
            containers: [
              {
                name,
                image: props.image,
                imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
                ports: [{ containerPort: 5432 }],
                envFrom: [
                  {
                    secretRef: { name: pgSecret.name },
                  },
                ],
                readinessProbe: {
                  tcpSocket: {
                    port: IntOrString.fromNumber(5432),
                  },
                  initialDelaySeconds: 10,
                },
                livenessProbe: {
                  tcpSocket: {
                    port: IntOrString.fromNumber(5432),
                  },
                  initialDelaySeconds: 10,
                },
                volumeMounts: [
                  {
                    name: `${configMap.name}-volume`,
                    mountPath: "/docker-entrypoint-initdb.d/",
                  },
                ],
              },
            ],
            volumes: [
              {
                name: `${configMap.name}-volume`,
                configMap: {
                  name: configMap.name,
                },
              },
            ],
          },
        },
      },
    });

    const pgService = new KubeService(this, id, {
      metadata: {
        name,
        namespace,
      },
      spec: {
        type: ServiceType.CLUSTER_IP,
        ports: [
          {
            port: 5432,
          },
        ],
        selector: {
          app: name,
        },
      },
    });

    pgSecret.addStringData("DATABASE_HOST", pgService.name);
    // pgSecret.addStringData("DATABASE_PORT", "5432");
    this.secret = pgSecret;
  }
}
