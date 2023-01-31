# Questions

- README: "wait until the `glu-api-deployment-**\*** pod` is running" -> where is this name defined?
- postgres-chart.ts: What do we need to add to ConfigMap?
- postgres-chart.ts: How to handle secrets (POC!)
- licensing-configmap.ts: Does the naming make sense? ${name}-configmap where name="licensing-config"
- postgres-chart.ts:26 where is the namespace defined? not passed in main.ts:32
- who builds the image / defines the image name