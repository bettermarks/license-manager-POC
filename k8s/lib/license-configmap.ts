import { ConfigMap } from "cdk8s-plus-24";
import { Construct } from "constructs";
import { ApplicationConfig } from "./types";

export type LicenseConfigMapProps = {
  name: string;
  appConfig: ApplicationConfig;
  namespace?: string;
};

export class LicenseConfigMap extends Construct {
  readonly configMap: ConfigMap;

  constructor(scope: Construct, id: string, props: LicenseConfigMapProps) {
    super(scope, id);
    const { name, namespace, appConfig } = props;

    this.configMap = new ConfigMap(this, `${name}-configmap`, {
      metadata: {
        name: `${name}-configmap`,
        namespace,
      },
    });
    for (const [key, value] of Object.entries(appConfig)) {
      if (Array.isArray(value) || typeof value === "boolean") {
        this.configMap.addData(key, JSON.stringify(value));
      } else {
        this.configMap.addData(key, value);
      }
    }
  }
}