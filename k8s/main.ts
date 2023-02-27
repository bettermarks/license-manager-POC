import { App } from "cdk8s";
import { IngressNginxChart } from "./lib/charts/ingress-nginx";
import { PostgresChart } from "./lib/charts/postgres";
import { LicenseChart } from "./lib/charts/license";
import { Segment, Namespace } from "./lib/types";
import { DEPLOYMENT_CONFIG } from "./lib/config";
import {
  APP_NODE_POOL_LABELS, 
  APPLICATION_SECRET,
  POSTGRES_IMAGE,
  POSTGRES_SECRET,
  REGISTRY_CREDENTIALS,
} from "./lib/constants";

const SEGMENT = (process.env.SEGMENT as Segment) || Segment.LOC00;
const IMAGE_TAG = process.env.IMAGE_TAG || "";
const IMAGE_NAME = "bm-license";
const IMAGE_REPO = `676249682729.dkr.ecr.eu-central-1.amazonaws.com/${IMAGE_NAME}`;

const app = new App();

if (SEGMENT === Segment.LOC00) {
  const pgChart = new PostgresChart(app, "postgres", { 
    image: POSTGRES_IMAGE, 
    name: "license-db",
    namespace: Namespace.LICENSE,
  });
  new LicenseChart(app, "license", {
    name: "license",
    namespace: Namespace.LICENSE,
    image: IMAGE_NAME,
    segment: SEGMENT,
    postgresSecret: pgChart.secret.name,
    imagePullSecrets: [],
  });
  new IngressNginxChart(app, "ingress-nginx", {
    namespace: Namespace.LICENSE,
    replicaCount: 1,
    tlsSecret: "loc00-tls-secret",
  });
} else {
  new LicenseChart(app, "license", {
    namespace: Namespace.LICENSE,
    name: "license",
    image: `${IMAGE_REPO}:${IMAGE_TAG}`,
    segment: SEGMENT,
    postgresSecret: POSTGRES_SECRET,
    applicationSecret: APPLICATION_SECRET,
    imagePullSecrets: [REGISTRY_CREDENTIALS],
    nodeSelector: APP_NODE_POOL_LABELS,
    migrationJobResources: DEPLOYMENT_CONFIG[SEGMENT].migrationJobResources,
    loadFixturesJobResources: DEPLOYMENT_CONFIG[SEGMENT].loadFixturesJobResources,
    apiResources: DEPLOYMENT_CONFIG[SEGMENT].apiResources,
    apiReplicas: DEPLOYMENT_CONFIG[SEGMENT].apiReplicas,
  });
}

app.synth();
