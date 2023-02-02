import { ServiceType } from "cdk8s-plus-24";
import { Construct } from "constructs";
import {
  KubeDeployment,
  KubeService,
  Container,
  IntOrString,
  Volume,
  TopologySpreadConstraint,
} from "../../imports/k8s";
import { NodeSelector } from "../types";

export type LicensingServiceProps = {
  name: string;
  createDeploymentOnly?: boolean;
  replicas: number;
  serviceAccountName: string;
  nodeSelector?: NodeSelector;
  initContainers: Container[];
  containers: Container[];
  volumes?: Volume[];
  servicePort?: number;
  containerPort?: number;
  deploymentId: string;
  namespace: string;
};
export class LicensingService extends Construct {
  readonly service?: KubeService;

  constructor(scope: Construct, id: string, props: LicensingServiceProps) {
    super(scope, id);

    const createDeploymentOnly = !!props.createDeploymentOnly;
    const {
      containerPort,
      containers,
      deploymentId,
      initContainers,
      name,
      namespace,
      nodeSelector,
      replicas,
      serviceAccountName,
      servicePort,
      volumes
    } = props;

    /**
     * Node selector and topology spread constraints
     */
    let topologySpreadConstraints: TopologySpreadConstraint[] = [];
    if (nodeSelector && Object.keys(nodeSelector).length > 0) {
      topologySpreadConstraints = [
        {
          maxSkew: 1,
          topologyKey: Object.keys(nodeSelector).shift()!!,
          whenUnsatisfiable: "DoNotSchedule",
          labelSelector: {
            matchLabels: {
              app: name,
            },
          },
        },
      ];
    }

    new KubeDeployment(this, `${name}-deployment`, {
      metadata: {
        name: `${name}-deployment`,
        namespace: namespace,
      },
      spec: {
        replicas: replicas,
        selector: {
          matchLabels: {
            app: name,
          },
        },
        template: {
          metadata: {
            labels: {
              app: name,
              deploymentId: deploymentId,
            },
          },
          spec: {
            serviceAccountName: serviceAccountName,
            nodeSelector: nodeSelector,
            ...(topologySpreadConstraints.length > 0 && {
              topologySpreadConstraints: topologySpreadConstraints,
            }),
            initContainers: initContainers,
            containers: containers,
            ...(volumes && { volumes: volumes }),
          },
        },
      },
    });

    if (!createDeploymentOnly && servicePort && containerPort) {
      this.service = new KubeService(this, `${name}-service`, {
        metadata: {
          name: `${name}-service`,
          namespace: namespace,
        },
        spec: {
          type: ServiceType.CLUSTER_IP,
          ports: [
            {
              port: servicePort,
              targetPort: IntOrString.fromNumber(containerPort),
            },
          ],
          selector: {
            app: name,
          },
        },
      });
    }
  }
}
