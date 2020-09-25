CONTAINER_IMAGE = vltr/dnsmasq-as-blocker
CURRENT_VERSION = $(shell bump2version --dry-run --list current | grep -v "message=" | grep current_version | cut -d"=" -f2)
VENV_PATH = $(shell pyenv prefix)

current-version:
	@echo $(CURRENT_VERSION)

help:
	@echo "black - formats the source code with black"
	@echo "clean - cleans any unecessary file from the codebase"
	@echo "docker - builds a docker image of this project"
	@echo "docker-push - pushes the docker container"
	@echo "requirements-dev - installs all requirements for development"

.PHONY: help

_create_venv_link:
	@echo "creating symlink (-f) .venv to $(VENV_PATH)"
	@ln -sf $(VENV_PATH) .venv

black:
	@black ./src/ ./tests

cleanpycache:
	find . -type d | grep "__pycache__" | xargs rm -rf

clean: cleanpycache
	rm -rf ./.coverage
	rm -rf ./.pytest_cache
	rm -rf ./.tox
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./htmlcov
	rm -rf ./pip-wheel-metadata
	rm -rf ./src/*.egg-info

pip: _create_venv_link
	@pip install --upgrade pip

piptools: pip
	@test $$(pip freeze | grep pip-tools | wc -l) -ne 1 && pip install pip-tools || pip install --upgrade pip-tools

requirements-dev: piptools
	@pip-compile -U -r requirements-dev.in -o requirements-dev.txt
	@pip-compile -U -r --no-header --no-index requirements.in -o requirements.txt
	@pip-sync requirements-dev.txt requirements.txt

docker-update:
	@docker pull python:3.8-slim

docker: docker-update
	@docker build --rm -t $(CONTAINER_IMAGE):$(CURRENT_VERSION) -f Dockerfile .
	@docker build --rm -t $(CONTAINER_IMAGE):latest -f Dockerfile .

docker-push: docker
	@docker push $(CONTAINER_IMAGE):$(CURRENT_VERSION)
	@docker push $(CONTAINER_IMAGE):latest
