SHELL := /bin/bash

include .env

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Make venv and install requirements
	@pipenv lock
	@pipenv install --dev
	@pipenv run pre-commit install
	@pre-commit autoupdate

migrate: ## Make and run migrations
	@pipenv run python manage.py makemigrations
	@pipenv run python manage.py migrate
	@pipenv run python manage.py collectstatic --noinput

.PHONY: test
test: ## Run tests
	@pipenv run skjold -v audit Pipfile.lock
	@pipenv run python manage.py test --verbosity=0 --parallel --failfast

.PHONY: bots
bots: ## Launch command for bots
	@pipenv run python manage.py run_pollini
	@pipenv run python manage.py run_marea

.PHONY: run
run: ## Run the Django server
	@pipenv run python manage.py runserver

start: install migrate run ## Install requirements, apply migrations, then start development server

.PHONY: check
check: ## Run checks on the packages
	@pipenv run skjold -v audit Pipfile.lock

.PHONY: update
update: ## For updating repo
	@git pull
	@pipenv run python manage.py migrate
	@pipenv run python manage.py crontab add
	@pipenv run python manage.py crontab add
