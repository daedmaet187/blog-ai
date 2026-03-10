.PHONY: api-run api-docker-build api-preflight api-migrate tofu-init tofu-plan tofu-apply tofu-platform-init tofu-platform-plan tofu-platform-apply

api-run:
	cd services/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api-docker-build:
	docker build -t blog-api:local services/api

api-preflight:
	cd services/api && PYTHONPATH=. .venv/bin/python scripts/preflight_prod.py

api-migrate:
	cd services/api && DATABASE_URL=$$DATABASE_URL .venv/bin/alembic upgrade head

tofu-init:
	cd infra/opentofu/envs/dev && tofu init

tofu-plan:
	cd infra/opentofu/envs/dev && tofu plan

tofu-apply:
	cd infra/opentofu/envs/dev && tofu apply

tofu-platform-init:
	cd infra/opentofu/envs/platform-dev && tofu init

tofu-platform-plan:
	cd infra/opentofu/envs/platform-dev && tofu plan

tofu-platform-apply:
	cd infra/opentofu/envs/platform-dev && tofu apply
