include values.mk

all:
	@echo "Run make [install|uninstall|k3d|vault|cert-manager|arc-controller|arc-runner|application|build|push|build-runner|run]"

uninstall:
	k3d cluster delete --config k3d-config.yaml

k3d:
	k3d cluster create --config k3d-config.yaml

wait:
	@sleep 5

vault:
	helm repo add hashicorp https://helm.releases.hashicorp.com --force-update
	yq -i '(.dependencies[]|select(.name=="vault")|.version)="$(VAULT_VERSION)"|(.dependencies[]|select(.name=="vault-secrets-operator")|.version)="$(VAULT_SECRETS_OPERATOR_VERSION)"' hashicorp-vault/Chart.yaml
	( cd hashicorp-vault && rm -f Chart.lock && helm dependency build )
	helm upgrade -i vault-stack hashicorp-vault \
		--set vault.server.dev.devRootToken=$(VAULT_TOKEN) \
		--set vault.server.ingress.hosts[0].host=$(VAULT_ADDR) \
		--namespace vault --create-namespace --wait

vault-init:
	@curl -X POST \
		-H "X-Vault-Token: $(VAULT_TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"type": "kubernetes"}' \
		-L $(VAULT_ADDR)/v1/sys/auth/kubernetes

	@curl -X POST \
		-H "X-Vault-Token: $(VAULT_TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"kubernetes_host": "https://kubernetes.default.svc:443"}' \
		$(VAULT_ADDR)/v1/auth/kubernetes/config

	@curl -X POST \
		-H "X-Vault-Token: $(VAULT_TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"bound_service_account_names": ["default"],"bound_service_account_namespaces": ["*"],"policies": ["vault-secrets-operator"],"ttl": "1h"}' \
		$(VAULT_ADDR)/v1/auth/kubernetes/role/vso
	
	@curl -X POST \
		-H "X-Vault-Token: $(VAULT_TOKEN)" \
		-d '{ "type":"kv-v2" }' \
		$(VAULT_ADDR)/v1/sys/mounts/k8s-secrets

	@curl -X PUT \
		-H "X-Vault-Token: $(VAULT_TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"policy": "path \"k8s-secrets/data/*\" {\n  capabilities = [\"read\"]\n}\n\npath \"k8s-secrets/metadata/*\" {\n  capabilities = [\"list\"]\n}"}' \
		$(VAULT_ADDR)/v1/sys/policies/acl/vault-secrets-operator

	@curl -X POST \
		--header "X-Vault-Token: $(VAULT_TOKEN)" \
		--header "Content-Type: application/json" \
		--data "{\"data\": {\"github_token\": \"$(GITHUB_TOKEN)\"}}" \
		$(VAULT_ADDR)/v1/k8s-secrets/data/github-actions-token

	@curl -s \
		--header "X-Vault-Token: $(VAULT_TOKEN)" \
		$(VAULT_ADDR)/v1/k8s-secrets/data/github-actions-token | jq

cert-manager:
	helm repo add jetstack https://charts.jetstack.io --force-update
	helm install \
		cert-manager jetstack/cert-manager \
		--version $(CERTIFICATE_MANAGER_VERSION) \
		--set crds.enabled=true \
		--namespace cert-manager --create-namespace --wait

arc-controller: CHART=github-arc-controller
arc-controller:
# gh api /orgs/actions/packages/container/actions-runner-controller-charts%2Fgha-runner-scale-set-controller/versions \
  --jq '.[].metadata.container.tags[]'
# 	helm repo add actions-runner-controller actions-github-asset.github.io
# 	helm repo update
	yq -i '(.dependencies[]|select(.name="gha-runner-scale-set-controller")|.version)="$(ARC_RUNNER_CONTROLLER_VERSION)"' $(CHART)/Chart.yaml
	helm dependencies build $(CHART)
	helm upgrade --install arc-controller $(CHART) \
		--version $(ARC_RUNNER_CONTROLLER_VERSION) \
  	--namespace "arc-systems" --create-namespace --wait

arc-runner: CHART=github-arc-runner/chart
arc-runner:
# gh api '/orgs/actions/packages/container/actions-runner-controller-charts%2Fgha-runner-scale-set/versions' --jq '.[].metadata.container.tags[]'
### Bug in the chart's values.yaml doesn't allow to provide secret name as a parameter, just token as a string.
##+ https://github.com/actions/actions-runner-controller/blob/master/charts/gha-runner-scale-set/values.yaml#L12
	yq -i '(.dependencies[]|select(.name="gha-runner-scale-set")|.version)="$(ARC_RUNNER_SCALE_SET_VERSION)"' $(CHART)/Chart.yaml
	helm dependencies build $(CHART)
	helm upgrade --install arc-runner-arm64-dind $(CHART) \
		-f $(CHART)/values.yaml -f $(CHART)/values-dind.yaml\
		--set gha-runner-scale-set.runnerScaleSetName=arc-runner-arm64-dind \
		--set gha-runner-scale-set.githubConfigSecret.github_token="$(GITHUB_TOKEN)" \
		--namespace dev --create-namespace --wait

	helm upgrade --install arc-runner-arm64-tools $(CHART) \
		-f $(CHART)/values.yaml -f $(CHART)/values-dind.yaml\
		--set gha-runner-scale-set.runnerScaleSetName=arc-runner-arm64-tools \
		--set gha-runner-scale-set.githubConfigSecret.github_token="$(GITHUB_TOKEN)" \
		--namespace dev --create-namespace --wait

application:
	helm upgrade -i testapp myapp/chart \
		--set global.version=green \
		--set global.timeout=5 \
		--namespace dev --create-namespace --wait

install: k3d wait push vault wait vault-init cert-manager arc-controller application arc-runner

build-runner:
	( cd github-arc-runner/image && docker build -t local-registry:3000/arc-runner:built . )

build-applicaiton:
	( cd myapp/image && docker build -t local-registry:3000/myapp:0.0.1 . )

push-runner:
	docker push local-registry:3000/arc-runner:built

push-applicaiton:
	docker push local-registry:3000/myapp:0.0.1

build: build-runner build-applicaiton

push: push-runner push-applicaiton

run:
	docker run --rm -it local-registry:3000/arc-runner:built bash
