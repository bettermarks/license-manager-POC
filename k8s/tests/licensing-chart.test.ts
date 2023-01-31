import { Testing } from "cdk8s";
import { GluChart } from "../lib/glu/glu";
import { DEPLOYMENT_CONFIG } from "../lib/common/configuration";
import { Segment } from "../lib/types";
import { APP_NODE_POOL_LABELS } from "../lib/constants";
const segment = Segment.DEV00;
describe("glu-chart", () => {
  beforeEach(() => {
    jest.useFakeTimers("modern").setSystemTime(new Date("2008-12-01"));
  });
  test("should match with snapshot", () => {
    const app = Testing.app();
    const chart = new GluChart(app, "test-chart", {
      image:
        "676249682729.dkr.ecr.eu-central-1.amazonaws.com/bm-glu:e6b588df29edbf984d876e195bdaee5230c5ad92",
      postgresSecret: "postgres-secret",
      gluApplicationSecret: "application-secret",
      serviceAccountName: "glu-service-account",
      gluOidcPrivateKeySecret: "glu-oidc-private-key",
      nodeSelector: APP_NODE_POOL_LABELS,
      segment: segment,
      migrationJobResources: DEPLOYMENT_CONFIG[segment].migrationJobResources,
      loadFixturesJobResources: DEPLOYMENT_CONFIG[segment].loadFixturesJobResources,
      gluApiResources: DEPLOYMENT_CONFIG[segment].apiResources,
      gluBackgroundTaskResources: DEPLOYMENT_CONFIG[segment].gluBackgroundTaskResources,
      gluStaticFilesResources: DEPLOYMENT_CONFIG[segment].gluStaticFilesResources,
      gluApiReplicas: DEPLOYMENT_CONFIG[segment].apiReplicas,
      gluStaticFilesReplicas: DEPLOYMENT_CONFIG[segment].gluStaticFilesReplicas,
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
