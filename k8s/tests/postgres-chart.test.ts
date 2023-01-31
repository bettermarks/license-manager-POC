import { Testing } from "cdk8s";
import { PostgresChart } from "../lib/charts/postgres";

describe("postgres-chart", () => {
  test("should match with snapshot", () => {
    const app = Testing.app();
    const chart = new PostgresChart(app, "test-chart", { image: "postgres:14", name: "licensing-db" });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
