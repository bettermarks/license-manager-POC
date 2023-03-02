import { Testing } from "cdk8s";
import { IngressNginxChart } from "../lib/charts/ingress-nginx";
import { APP_NODE_POOL_LABELS } from "../lib/constants";

describe("ingress-nginx-chart", () => {
  test("with tls", () => {
    const app = Testing.app();
    const chart = new IngressNginxChart(app, "test-chart", {
      replicas: 1,
      tlsSecret: "loc00-tls-secret",
      namespace: "dummy-namespace",
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
  test("Without tls", () => {
    const app = Testing.app();
    const chart = new IngressNginxChart(app, "test-chart", {
      nodeSelector: APP_NODE_POOL_LABELS,
      namespace: "dummy-namespace",
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
