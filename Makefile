PYTHON ?= python3
PYTEST ?= pytest
MYPY ?= mypy

# Python implementation
PYTHON_IMPL = $(shell $(PYTHON) -c "import sys; print(sys.implementation.name)")

EXAMPLES = $(sort $(wildcard docs/examples/*.py docs/examples/*/*.py))

.PHONY: all lint init-hooks doc spelling test cov dist devel clean mypy
all: aioredis.egg-info lint doc cov

doc: spelling
	mkdocs build
spelling:
	@echo "Running spelling check"
	$(MAKE) -C docs spelling

mypy:
	$(MYPY)

test:
	$(PYTEST)

cov coverage:
	$(PYTEST) --cov

dist: clean
	$(PYTHON) setup.py sdist bdist_wheel

clean:
	-rm -r docs/build
	-rm -r build dist aioredis.egg-info

init-hooks:
	pip install -U pre-commit
	pre-commit install
	pre-commit install-hooks

lint: init-hooks
	pre-commit run --all-files --show-diff-on-failure

devel: aioredis.egg-info init-hooks
	pip install -U pip
	pip install -U \
		-r tests/requirements.txt \
		-r docs/requirements.txt \
		bumpversion \
		wheel

aioredis.egg-info:
	pip install -Ue .


examples: $(EXAMPLES)

$(EXAMPLES):
	@export REDIS_VERSION="$(redis-cli INFO SERVER | sed -n 2p)"
	$(PYTHON) $@


certificate:
	$(MAKE) -C tests/ssl


ci-test:
	$(PYTEST) --cov --cov-append --cov-report=xml:coverage_redis.xml -m 'not onlycluster'
	$(PYTEST) --cov --cov-append --cov-report=xml:coverage_cluster.xml -m 'not onlynotcluster and not redismod' --redis-url="redis://localhost:16379/0"
