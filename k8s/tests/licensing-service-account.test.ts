import { Testing } from "cdk8s";
import { LicensingServiceAccount } from "../lib/service-account";

describe("Licensing-service-account", () => {
    test("should match with snapshot", () => {
        const app = Testing.app();
        const chart = new LicensingServiceAccount(app, "test-chart", {
            imagePullSecrets: ["ImagePullSecret"],
            namespace: "dummy-namespace",
            name: "service-account",
        });
        const results = Testing.synth(chart);
        expect(results).toMatchSnapshot();
    });
});
