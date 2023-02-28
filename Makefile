SHELL := /bin/bash

.PHONY: synth
synth:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run synth)

.PHONY: cdk_install
cdk_install:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm ci)

.PHONY: cdk_test
cdk_test:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run test)

.PHONY: cdk_update_snapshots
cdk_update_snapshots:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run test -- -u)

.PHONY: init
init:
	kubectl create namespace licensing || true
	skaffold run --cleanup=false

.PHONY: watch
watch:
	skaffold dev

.PHONY: cdk_pretty
cdk_pretty:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run prettier)