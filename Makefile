PROJECT_NAME ?= chhoto
devup:
	docker compose -p $(PROJECT_NAME)-dev -f ./docker/docker-compose.base.yml -f ./docker/docker-compose.dev.yml up -d

devdown:
	docker compose -p $(PROJECT_NAME)-dev -f ./docker/docker-compose.base.yml -f ./docker/docker-compose.dev.yml down
