import { Testing } from "cdk8s";
import { LicenseChart } from "../lib/charts/license";
import { Segment } from "../lib/types";

describe("license-local-chart", () => {
  beforeEach(() => {
    jest.useFakeTimers("modern").setSystemTime(new Date("2008-12-01"));
  });
  test("should match with snapshot", () => {
    const app = Testing.app();
    const chart = new LicenseChart(app, "test-chart", {
      name: "license",
      image: "bm-license",
      namespace: "dummy-namespace",
      segment: Segment.LOC00,
      postgresSecret: "pgChart.secret.name",
      applicationSecret: "loc00-license-application-secret",
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
