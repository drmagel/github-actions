SHELL = bash
REGISTRY = local-registry:3000
VERSION = 0.0.1
IMAGEURL = $(REGISTRY)/myapp:$(VERSION)
TIMEOUT = 60

all:
	@echo "Usage: make [create|run|kill|image|plan|blue|green|delete|helm]"
	@echo "Where:"
	@echo " create:	create image"
	@echo " run:		run image locally"
	@echo " image:		create image and push it to registry"
	@echo " plan:		debug helm chart"
	@echo " blue:	install helm chart - blue version"
	@echo " green:	install helm chart - green version"
	@echo " delete:	delete helm chart"
	@echo " helm:		create image, push it and install helm chart"

image: create push
helm:  create push install

create:
	(	docker rmi $(IMAGEURL); \
		cd image; \
		docker build -t $(IMAGEURL) . \
	)

run:
	docker run -it --rm -p 8080:8080 $(IMAGEURL)

kill:
	docker ps | awk '/myapp:$(VERSION)/{print $$1}' | xargs docker kill

push: 
	docker push $(IMAGEURL)

blue:
	helm upgrade -i -n default \
	  --set global.version=blue \
	  --set global.timeout=$(TIMEOUT) \
		myapp chart

green:
	helm upgrade -i -n default \
	  --set global.version=green \
	  --set global.timeout=$(TIMEOUT) \
		myapp chart

plan:
	helm upgrade -i -n default \
	  --set global.version=$(VERSION) \
		--set global.timeout=$(TIMEOUT) \
		myapp chart --dry-run --debug

template:
	helm template -n default \
	  --set global.version=$(VERSION) \
	  --set global.timeout=$(TIMEOUT) \
		myapp chart --debug

delete:
	helm delete -n default myapp

test:
	@( rm -f out.txt; \
			./client.py  \
	)

version:
	@curl -s http://myapp/api/version