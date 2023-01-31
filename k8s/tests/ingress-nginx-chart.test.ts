import { Testing } from "cdk8s";
import { IngressNginx } from "../lib/common/ingress-nginx";
import { APP_NODE_POOL_LABELS } from "../lib/constants";

describe("ingress-nginx-chart", () => {
  test("with tls", () => {
    const app = Testing.app();
    const chart = new IngressNginx(app, "test-chart", {
      replicas: 1,
      tlsSecret: "loc00-tls-secret",
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
  test("Without tls", () => {
    const app = Testing.app();
    const chart = new IngressNginx(app, "test-chart", {
      nodeSelector: APP_NODE_POOL_LABELS,
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
