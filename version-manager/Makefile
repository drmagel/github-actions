SHELL = bash

VERSION = 0.0.1
REGISTRY = local-registry:3000
IMAGEURL = $(REGISTRY)/version-manager:$(VERSION)
CONTAINER_NAME = version-manager

all:
	@echo "Usage: make [build|run|run-sqlite|stop|push|test]"
	@echo "Where:"
	@echo "  build:      build image"
	@echo "  run:        run image locally with PostgreSQL"
	@echo "  run-sqlite: run image locally with SQLite (background)"
	@echo "  stop:       stop running docker container"
	@echo "  push:       push image to registry"
	@echo "  test:       run pytest test suite (starts/stops docker automatically)"

build:
	docker rmi $(IMAGEURL) || true
	docker build -t $(IMAGEURL) image/

run:
	docker run -it --rm -p 8080:8080 -e PYTHONUNBUFFERED=1 $(IMAGEURL)

run-sqlite:
	docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	docker run -d --rm --name $(CONTAINER_NAME) -p 8080:8080 -e USE_POSTGRESQL=false -e PYTHONUNBUFFERED=1 $(IMAGEURL)
	@echo "Container $(CONTAINER_NAME) started. Use 'make stop' to stop it."

stop:
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@echo "Container $(CONTAINER_NAME) stopped."

push:
	docker push $(IMAGEURL)

image: build push

pytest:
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		curl -s http://localhost:8080/health > /dev/null && break || sleep 2; \
	done
	@echo "=== Running pytest test suite ==="
	cd image/src/tests && PYTHONPATH=. pytest -v --tb=short;

pytest-init:
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		curl -s http://localhost:8080/health > /dev/null && break || sleep 2; \
	done
	cd image/src/tests && PYTHONPATH=. pytest -v test_01_setup.py && PYTHONPATH=. pytest -v test_02_images_api.py

pytest-cleanup:
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		curl -s http://localhost:8080/health > /dev/null && break || sleep 2; \
	done
	cd image/src/tests && PYTHONPATH=. pytest -v test_04_cleanup.py


test: stop build run-sqlite pytest
	make stop

re-run: stop build run-sqlite pytest-init

cleanup: pytest-cleanup
	make stop
