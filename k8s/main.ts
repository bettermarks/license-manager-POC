import { App } from "cdk8s";
import { IngressNginx } from "./lib/common/ingress-nginx";
import { PostgresChart } from "./lib/postgres/postgres-chart";
import { LicensingChart } from "./lib/licensing";
import { Segment, Namespace } from "./lib/types";
import { DEPLOYMENT_CONFIG } from "./lib/common/configuration";
import {
  APP_NODE_POOL_LABELS, 
  OIDC_RSA_PRIVATE_KEY,
  POSTGRES_SECRET,
  APPLICATION_SECRET,
  REGISTRY_CREDENTIALS,
} from "./lib/constants";
import { 
  LicensingServiceAccount, 
  LICENSING_SERVICE_ACCOUNT_NAME 
} from "./lib/common/licensing-service-account";

const SEGMENT = (process.env.SEGMENT as Segment) || Segment.LOC00;
const IMAGE_TAG = process.env.IMAGE_TAG || "";
const IMAGE_NAME = "bm-licensing";

const app = new App();

if (SEGMENT === Segment.LOC00) {
  /**
   * Service account
   */
  const licensingServiceAccount = new LicensingServiceAccount(app, LICENSING_SERVICE_ACCOUNT_NAME, {
    namespace: Namespace.DEFAULT,
    imagePullSecrets: [],
  });
  const pgChart = new PostgresChart(app, "licensing-postgres", { image: "postgres:14", name: "licensing-db" });
  new LicensingChart(app, "licensing", {
    namespace: Namespace.DEFAULT,
    image: IMAGE_NAME,
    segment: SEGMENT,
    postgresSecret: pgChart.secret.name,
    applicationSecret: "loc00-glu-application-secret",
    oidcPrivateKeySecret: "loc00-glu-oidc-rsa-private-key",
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
  });
  new IngressNginx(app, "glu-ingress-nginx-controller", {
    namespace: Namespace.DEFAULT,
    replicas: 1,
    tlsSecret: "loc00-tls-secret",
  });
} else {
  const licensingServiceAccount = new LicensingServiceAccount(app, "glu-service-account", {
    namespace: Namespace.LICENSING,
    imagePullSecrets: [REGISTRY_CREDENTIALS],
  });
  new LicensingChart(app, `glu`, {
    namespace: Namespace.LICENSING,
    image: `676249682729.dkr.ecr.eu-central-1.amazonaws.com/${IMAGE_NAME}:${IMAGE_TAG}`,
    postgresSecret: POSTGRES_SECRET,
    applicationSecret: APPLICATION_SECRET,
    oidcPrivateKeySecret: OIDC_RSA_PRIVATE_KEY,
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
    nodeSelector: APP_NODE_POOL_LABELS,
    segment: SEGMENT,
    migrationJobResources: DEPLOYMENT_CONFIG[SEGMENT].migrationJobResources,
    loadFixturesJobResources: DEPLOYMENT_CONFIG[SEGMENT].loadFixturesJobResources,
    apiResources: DEPLOYMENT_CONFIG[SEGMENT].apiResources,
    apiReplicas: DEPLOYMENT_CONFIG[SEGMENT].apiReplicas,
  });
  new IngressNginx(app, "glu-ingress-nginx-controller", {
    namespace: Namespace.LICENSING,
    nodeSelector: APP_NODE_POOL_LABELS,
  });
}

app.synth();
