import { Testing } from "cdk8s";
import { GluLocalChart } from "../lib/glu/glu-local";
import { Segment } from "../lib/types";

describe("glu-local-chart", () => {
  beforeEach(() => {
    jest.useFakeTimers("modern").setSystemTime(new Date("2008-12-01"));
  });
  test("should match with snapshot", () => {
    const app = Testing.app();
    const chart = new GluLocalChart(app, "test-chart", {
      image: "bm-glu",
      segment: Segment.LOC00,
      postgresSecret: "pgChart.secret.name",
      gluApplicationSecret: "loc00-glu-application-secret",
      gluOidcPrivateKeySecret: "loc00-glu-oidc-rsa-private-key",
      serviceAccountName: "glu-service-account",
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
