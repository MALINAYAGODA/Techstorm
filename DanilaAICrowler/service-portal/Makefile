.PHONY: help
help: ## Cправка
	@awk 'BEGIN {FS = "(.PHONY:)|(##)"} /([a-z\.]+) ## / {printf "  \033[36m%-20s\033[0m %s\n", $$2, $$3}' $(MAKEFILE_LIST)

.PHONY: openapi.build ## OpenAPI: Собрать все определения в единый bundle
openapi.build:
	@npx @redocly/cli bundle api/schema.yaml -o openapi.yaml

.PHONY: openapi.run ## OpenAPI: Собрать все определения в единый bundle и открыть UI в браузере
openapi.run:
	@npx @redocly/cli preview-docs api/schema.yaml

.PHONY: openapi.generate ## OpenAPI: Собрать все определения в единый bundle и сгенерировать код Go-сервера
openapi.generate:
	@echo "Bundling OpenAPI schema..." && \
	npx @redocly/cli bundle api/schema.yaml -o openapi.yaml && \
	echo "Generating server and models code..." && \
	oapi-codegen -config oapi-codegen-config.yaml openapi.yaml && \
	echo "RPC server generated."

.PHONY: lint ## Запустить линтеры на всем проекте
lint:
	@echo "Not implemented"