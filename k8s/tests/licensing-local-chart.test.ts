import { Testing } from "cdk8s";
import { LicensingChart } from "../lib/charts/licensing";
import { Segment } from "../lib/types";

describe("licensing-local-chart", () => {
  beforeEach(() => {
    jest.useFakeTimers("modern").setSystemTime(new Date("2008-12-01"));
  });
  test("should match with snapshot", () => {
    const app = Testing.app();
    const chart = new LicensingChart(app, "test-chart", {
      name: "licensing",
      image: "bm-licensing",
      namespace: "dummy-namespace",
      segment: Segment.LOC00,
      postgresSecret: "pgChart.secret.name",
      applicationSecret: "loc00-licensing-application-secret",
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
