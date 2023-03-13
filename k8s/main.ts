import { App } from "cdk8s";
import { IngressNginxChart } from "./lib/charts/ingress-nginx";
import { PostgresChart } from "./lib/charts/postgres";
import { LicensingChart } from "./lib/charts/licensing";
import { Segment } from "./lib/types";
import { DEPLOYMENT_CONFIG } from "./lib/config";
import {
  APP_NODE_POOL_LABELS,
  APPLICATION_SECRET,
  POSTGRES_IMAGE,
  POSTGRES_SECRET,
  REGISTRY_CREDENTIALS,
} from "./lib/constants";
import { Namespace } from "./lib/types";
import { MigrationJobChart } from "./lib/charts/migration-job";
import { LicensingServiceAccount } from "./lib/service-account";

const SEGMENT = (process.env.SEGMENT as Segment) || Segment.LOC00;
const IMAGE_TAG = process.env.IMAGE_TAG || "";
const IMAGE_NAME = "bm-licensing";
const IMAGE_REPO = `676249682729.dkr.ecr.eu-central-1.amazonaws.com/${IMAGE_NAME}`;

const app = new App();

const licensingServiceAccount = new LicensingServiceAccount(app, "licensing-service-account", {
  name: "licensing",
  imagePullSecrets: SEGMENT === Segment.LOC00 ? [] : [REGISTRY_CREDENTIALS],
});

if (SEGMENT === Segment.LOC00) {
  const pgChart = new PostgresChart(app, "postgres", {
    namespace: Namespace.LICENSING,
    image: POSTGRES_IMAGE,
    name: "licensing-db",
  });
  new MigrationJobChart(app, "migration", {
    namespace: Namespace.LICENSING,
    name: "licensing",
    image: IMAGE_NAME,
    segment: SEGMENT,
    postgresSecret: pgChart.secret.name,
    applicationSecret: "loc00-application-secret",
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
  });
  new LicensingChart(app, "licensing", {
    namespace: Namespace.LICENSING,
    name: "licensing",
    image: IMAGE_NAME,
    segment: SEGMENT,
    postgresSecret: pgChart.secret.name,
    applicationSecret: "loc00-application-secret",
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
  });
  new IngressNginxChart(app, "ingress-nginx", {
    namespace: Namespace.LICENSING,
    replicas: 1,
    tlsSecret: "loc00-tls-secret",
  });
} else {
  new MigrationJobChart(app, "migration", {
    namespace: Namespace.LICENSING,
    name: "licensing",
    image: `${IMAGE_REPO}:${IMAGE_TAG}`,
    segment: SEGMENT,
    postgresSecret: POSTGRES_SECRET,
    applicationSecret: APPLICATION_SECRET,
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
    nodeSelector: APP_NODE_POOL_LABELS,
  });
  new LicensingChart(app, "licensing", {
    namespace: Namespace.LICENSING,
    name: "licensing",
    image: `${IMAGE_REPO}:${IMAGE_TAG}`,
    segment: SEGMENT,
    postgresSecret: POSTGRES_SECRET,
    applicationSecret: APPLICATION_SECRET,
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
    nodeSelector: APP_NODE_POOL_LABELS,
    apiResources: DEPLOYMENT_CONFIG[SEGMENT].apiResources,
    apiReplicas: DEPLOYMENT_CONFIG[SEGMENT].apiReplicas,
  });
}

app.synth();
