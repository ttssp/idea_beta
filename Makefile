.PHONY: bootstrap install-python install-e3 install-node lint-python lint-platform lint-web test-python test-e3 test-web typecheck-web check

bootstrap: install-python install-e3 install-node

install-python:
	python -m pip install -e ".[dev]"

install-e3:
	python -m pip install -r backend/e3/requirements.txt

install-node:
	npm install

lint-python:
	python -m ruff check src/myproj tests

lint-platform:
	python -m ruff check backend/e3 src/policy_control

lint-web:
	npm run lint

test-python:
	python -m pytest tests

test-e3:
	python -m pytest backend/e3/tests

typecheck-web:
	npm run typecheck

test-web:
	npm test -- --run

check: lint-python lint-platform lint-web test-python test-e3 typecheck-web test-web
