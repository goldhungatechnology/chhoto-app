PROJECT_NAME ?= chhoto
devup:
	docker compose -p $(PROJECT_NAME)-dev -f ./docker/docker-compose.base.yml -f ./docker/docker-compose.dev.yml up -d

devb:
	docker compose -p $(PROJECT_NAME)-dev -f ./docker/docker-compose.base.yml -f ./docker/docker-compose.dev.yml build

devdown:
	docker compose -p $(PROJECT_NAME)-dev -f ./docker/docker-compose.base.yml -f ./docker/docker-compose.dev.yml down

devdownv:
	docker compose -p $(PROJECT_NAME)-dev -f ./docker/docker-compose.base.yml -f ./docker/docker-compose.dev.yml down -v

stagingup:
	docker compose -p $(PROJECT_NAME)-staging  -f ./docker/docker-compose.staging.yml up -d

stagingb:
	docker compose -p $(PROJECT_NAME)-staging  -f ./docker/docker-compose.staging.yml build

stagingdown:
	docker compose -p $(PROJECT_NAME)-staging  -f ./docker/docker-compose.staging.yml down

stagingdownv:
	docker compose -p $(PROJECT_NAME)-staging  -f ./docker/docker-compose.staging.yml down -v
