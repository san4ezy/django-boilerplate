# Default environment variable
ENV ?= development

# Define path configurations
ENV_DIR := environments/$(ENV)
ENV_FILE := $(ENV_DIR)/app.env
COMPOSE_FILE := $(ENV_DIR)/docker-compose.yml

# Export host UID and GID
export HOST_UID := $(shell id -u)
export HOST_GID := $(shell id -g)

# Include environment variables if app.env exists
-include $(ENV_FILE)
export

# Project identity variables with fallbacks
PROJECT_NAME ?= boilerplate
APP_NAME ?= app
APP_PORT ?= 8000
DB_USER ?= $(POSTGRES_USER)
DB_NAME ?= $(POSTGRES_DB)

# Use bash for subshell commands
SHELL := /bin/bash

.PHONY: help setup keygen build up down restart rebuild logs ps bash \
        migrate makemigrations showmigrations superuser shell collectstatic test \
        startapp makecommand backup restore lint black isort flake8 mypy

.DEFAULT_GOAL := help

# ==============================================================================
# HELP & INITIALIZATION
# ==============================================================================

help: ## Show this interactive help menu
	@echo -e "\033[1;34mAvailable commands:\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup: ## Copy environment files and replace placeholder variables (Usage: make setup ENV=development)
	@echo -e "\033[32m[+] Setting up environment configuration for: $(ENV)...\033[0m"
	@cp $(ENV_DIR)/app.env.example $(ENV_FILE)
	@cp $(ENV_DIR)/docker-compose.yml.example $(COMPOSE_FILE)
	@sed -i 's/<PROJECT_NAME>/$(PROJECT_NAME)/g' $(COMPOSE_FILE)
	@sed -i 's/<APP_NAME>/$(APP_NAME)/g' $(COMPOSE_FILE)
	@sed -i 's/<APP_PORT>/$(APP_PORT)/g' $(COMPOSE_FILE)
	@echo -e "\033[32m[✓] Environment files successfully prepared in $(ENV_DIR)\033[0m"

keygen: ## Generate random secret keys in app.env (Usage: make keygen ENV=development)
	@echo -e "\033[32m[+] Generating secure cryptographic keys for $(ENV_FILE)...\033[0m"
	@PG_PASS=$$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 16); \
	SEC_KEY=$$(openssl rand -base64 36 | tr -dc 'a-zA-Z0-9!@#%^&*()' | head -c 50); \
	JWT_SIG=$$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 64); \
	JWT_ENC=$$(python3 -c "import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"); \
	sed -i "s/<POSTGRES_PASSWORD>/$$PG_PASS/g" $(ENV_FILE); \
	sed -i "s/<SECRET_KEY>/$$SEC_KEY/g" $(ENV_FILE); \
	sed -i "s/<JWT_SIGNING_KEY>/$$JWT_SIG/g" $(ENV_FILE); \
	sed -i "s/<JWT_PAYLOAD_ENCRYPTION_KEY>/$$JWT_ENC/g" $(ENV_FILE)
	@echo -e "\033[32m[✓] Secrets written to $(ENV_FILE)\033[0m"

# ==============================================================================
# DOCKER MANAGEMENT
# ==============================================================================

build: ## Build docker compose services
	docker compose -f $(COMPOSE_FILE) build

up: ## Start services in background
	docker compose -f $(COMPOSE_FILE) up -d

down: ## Stop and remove containers
	docker compose -f $(COMPOSE_FILE) down

restart: ## Restart compose services
	docker compose -f $(COMPOSE_FILE) restart

rebuild: down build up ## Rebuild containers and restart

logs: ## View real-time container logs
	docker compose -f $(COMPOSE_FILE) logs $(APP_NAME) --tail 100 -f

ps: ## List running project containers
	docker compose -f $(COMPOSE_FILE) ps

bash: ## Open interactive bash session inside application container
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) bash

# ==============================================================================
# DJANGO MANAGEMENT COMMANDS
# ==============================================================================

migrate: ## Apply database migrations
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) python manage.py migrate

makemigrations: ## Generate new database migrations
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) python manage.py makemigrations

showmigrations: ## Show status of database migrations
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) python manage.py showmigrations

superuser: ## Create new Django superuser
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) python manage.py createsuperuser

shell: ## Open interactive Django shell (shell_plus)
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) python manage.py shell_plus

collectstatic: ## Collect static files
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) python manage.py collectstatic --noinput

test: ## Execute test suite via pytest
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) pytest

# ==============================================================================
# CODE GENERATORS
# ==============================================================================

startapp: ## Scaffold a new Django application (Usage: make startapp app=blog)
	@if [ -z "$(app)" ]; then echo "Error: Please specify target app name, e.g., 'make startapp app=blog'"; exit 1; fi
	@mkdir -p apps/$(app)
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) python manage.py startapp $(app) apps/$(app)
	@if [ -d "boilerplate/startapp" ]; then cp -r boilerplate/startapp/* apps/$(app)/; fi
	@rm -f apps/$(app)/tests.py
	@echo -e "\033[32m[✓] Scaffolded new app at 'apps/$(app)'\033[0m"

makecommand: ## Scaffold a new management command (Usage: make makecommand app=blog cmd=sync_data)
	@if [ -z "$(app)" ] || [ -z "$(cmd)" ]; then echo "Error: Specify both app and cmd, e.g., 'make makecommand app=blog cmd=sync_data'"; exit 1; fi
	@mkdir -p apps/$(app)/management/commands
	@touch apps/$(app)/management/__init__.py
	@touch apps/$(app)/management/commands/__init__.py
	@cp boilerplate/makecommand/example.py apps/$(app)/management/commands/$(cmd).py
	@echo -e "\033[32m[✓] Created management command 'apps/$(app)/management/commands/$(cmd).py'\033[0m"

# ==============================================================================
# DATABASE BACKUP & RESTORE
# ==============================================================================

backup: ## Dump PostgreSQL database into backups/ directory
	@mkdir -p backups
	@TIMESTAMP=$$(date +%Y%m%d%H%M%S); \
	BACKUP_FILE="backups/$${TIMESTAMP}.db"; \
	echo -e "\033[32m[+] Creating database dump $${BACKUP_FILE}...\033[0m"; \
	docker compose -f $(COMPOSE_FILE) exec -T db pg_dump -U $(DB_USER) $(DB_NAME) > $${BACKUP_FILE}; \
	echo -e "\033[32m[✓] Backup finished: $${BACKUP_FILE}\033[0m"

restore: ## Restore PostgreSQL database from latest dump in backups/
	@LATEST_BACKUP=$$(ls -1t backups/*.db 2>/dev/null | head -n 1); \
	if [ -z "$$LATEST_BACKUP" ]; then echo "Error: No backup files found in backups/"; exit 1; fi; \
	echo -e "\033[33m[!] Restoring database from $${LATEST_BACKUP}...\033[0m"; \
	docker compose -f $(COMPOSE_FILE) exec -T db psql -U $(DB_USER) $(DB_NAME) < $$LATEST_BACKUP; \
	echo -e "\033[32m[✓] Database restored successfully!\033[0m"

# ==============================================================================
# QUALITY ASSURANCE (LINTERS)
# ==============================================================================

lint: black isort flake8 mypy ## Run all code style checkers and linters

black: ## Format code with Black
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) black .

isort: ## Sort module imports with isort
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) isort .

flake8: ## Run Flake8 code linter
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) flake8 .

mypy: ## Check type annotations with mypy
	docker compose -f $(COMPOSE_FILE) exec $(APP_NAME) mypy -p apps