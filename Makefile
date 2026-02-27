.PHONY: api-run api-docker-build tf-init tf-plan tf-apply

api-run:
	cd services/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api-docker-build:
	docker build -t blog-api:local services/api

tf-init:
	cd infra/terraform/envs/dev && terraform init

tf-plan:
	cd infra/terraform/envs/dev && terraform plan

tf-apply:
	cd infra/terraform/envs/dev && terraform apply
