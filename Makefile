SHELL := /bin/bash
export

.PHONY: up down logs test seed fmt

up:
	docker compose --env-file .env -f infra/docker-compose.yml up -d --build

down:
	docker compose -f infra/docker-compose.yml down -v

logs:
	docker compose -f infra/docker-compose.yml logs -f --tail=200

test:
	pytest ci/tests -q

seed:
	python scripts/seed_repo.py

fmt:
	ruff check --fix || true
	black . || true
