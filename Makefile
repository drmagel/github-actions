include values.mk

all:
	@echo "Run make [install|uninstall|k3d|vault|cert-manager|actions-controller|actions-runner]"

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
		-d '{"bound_service_account_names": ["default"],"bound_service_account_namespaces": ["vault","actions-runner-system","dev"],"policies": ["vault-secrets-operator"],"ttl": "1h"}' \
		$(VAULT_ADDR)/v1/auth/kubernetes/role/vso
	
	@curl \
    -H "X-Vault-Token: $(VAULT_TOKEN)" \
    -X POST \
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

actions-controller:
	helm repo add actions-runner-controller https://actions-runner-controller.github.io/actions-runner-controller
	yq -i '(.dependencies[]|select(.name="actions-runner-controller")|.version)="$(ACTIONS_RUNNER_CONTROLLER_VERSION)"' github-actions-controller/Chart.yaml
	( cd github-actions-controller && rm -f Chart.lock && helm dependency build )
	helm upgrade --install actions-controller github-actions-controller \
  	--namespace actions-runner-system --create-namespace --wait

actions-runner:
	helm upgrade --install github-actions-runner github-actions-runner/chart \
		--namespace dev --create-namespace --wait

application:
	helm upgrade -i testapp myapp/chart \
		--set global.version=green \
		--set global.timeout=5 \
		--namespace dev --create-namespace --wait

install: k3d wait push vault wait vault-init cert-manager actions-controller application actions-runner

build-runner:
	( cd github-actions-runner/image && docker build -t local-registry:3000/github-actions-runner:built . )

build-applicaiton:
	( cd myapp/image && docker build -t local-registry:3000/myapp:0.0.1 . )

push-runner:
	docker push local-registry:3000/github-actions-runner:built

push-applicaiton:
	docker push local-registry:3000/myapp:0.0.1

build: build-runner build-applicaiton

push: push-runner push-applicaiton

test:
	(cd hashicorp-vault && ls)
