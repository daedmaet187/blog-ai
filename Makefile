.PHONY: api-run api-docker-build tofu-init tofu-plan tofu-apply

api-run:
	cd services/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api-docker-build:
	docker build -t blog-api:local services/api

tofu-init:
	cd infra/terraform/envs/dev && tofu init

tofu-plan:
	cd infra/terraform/envs/dev && tofu plan

tofu-apply:
	cd infra/terraform/envs/dev && tofu apply
