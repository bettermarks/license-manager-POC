SHELL := /bin/bash

.PHONY: k8s_synth
k8s_synth:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run synth)

.PHONY: k8s_install
k8s_install:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm ci)

.PHONY: k8s_test
k8s_test:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run test)

.PHONY: k8s_test_update
k8s_test_update:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run test -- -u)

.PHONY: k8s_pretty
k8s_pretty:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run prettier)

.PHONY: init
init:
	kubectl create namespace licensing || true
	skaffold run --cleanup=false

.PHONY: watch
watch:
	skaffold dev
