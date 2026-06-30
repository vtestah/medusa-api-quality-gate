# medusa-api-quality-gate — локальный рантайм и тесты одной командой.
# Всё делегируется уже существующим pnpm-скриптам и docker compose.

SHELL := /bin/bash
VENV := .venv/bin

.PHONY: help up down logs seed setup test smoke lint ci mutation e2e clean

help: ## Список целей
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up: ## Поднять рантайм: Medusa + PostgreSQL + Redis + storefront
	pnpm docker:up

down: ## Остановить рантайм
	pnpm docker:down

logs: ## Логи Medusa
	pnpm docker:logs

seed: ## Засеять демо-данные и синхронизировать publishable key
	pnpm docker:seed-demo

setup: ## Создать venv и поставить quality-gate[dev]
	pnpm quality-gate:venv
	pnpm quality-gate:install

test: ## Прогнать весь pytest-набор quality-gate
	pnpm quality-gate:test

smoke: ## Быстрые smoke-тесты
	pnpm quality-gate:test:smoke

lint: ## ruff + mypy strict (как в CI)
	cd quality-gate && ../$(VENV)/python -m ruff check src tests
	cd quality-gate && ../$(VENV)/python -m mypy

ci: lint ## Локальный CI-гейт: lint + pytest с покрытием (зеркалит quality-gate.yml)
	cd quality-gate && ../$(VENV)/python -m pytest -q --cov-report=xml --junitxml=junit.xml

mutation: ## Mutation testing (mutmut) по доменным моделям
	cd quality-gate && ../$(VENV)/python -m mutmut run --paths-to-mutate src/quality_gate/models/ --runner "../$(VENV)/python -m pytest -x -q" || true
	cd quality-gate && ../$(VENV)/python -m mutmut results

e2e: ## Playwright UI E2E (RU/US storefront); требует поднятый 'make up'
	cd e2e && pnpm install --ignore-workspace && pnpm exec playwright install chromium && pnpm test

clean: ## Убрать локальные кэши тестов
	rm -rf quality-gate/.pytest_cache quality-gate/.mypy_cache quality-gate/.ruff_cache quality-gate/reports
