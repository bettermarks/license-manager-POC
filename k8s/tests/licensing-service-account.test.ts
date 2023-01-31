import { Testing } from "cdk8s";
import { LicensingServiceAccount } from "../lib/common/licensing-service-account";

describe("Glu-service-account", () => {
  test("should match with snapshot", () => {
    const app = Testing.app();
    const chart = new LicensingServiceAccount(app, "test-chart", {
      imagePullSecrets: ["ImagePullSecret"],
      namespace: "default"
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
