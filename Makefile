.PHONY: help install test lint format clean build deploy

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  test       Run tests"
	@echo "  lint       Run linters"
	@echo "  format     Format code"
	@echo "  build      Build Docker images"
	@echo "  run        Run locally"
	@echo "  deploy     Deploy to production"
	@echo "  clean      Clean temporary files"

install:
	pip install -r requirements.txt
	cd backend && pip install -r requirements.txt
	cd frontend && pip install -r requirements.txt

test:
	cd backend && pytest -v --cov=.

lint:
	flake8 backend/
	black --check backend/
	pylint backend/

format:
	black backend/
	isort backend/

run:
	docker-compose up --build

build:
	docker build -t payment-backend ./backend
	docker build -t payment-frontend ./frontend

deploy:
	docker-compose -f docker-compose.prod.yml up -d

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage