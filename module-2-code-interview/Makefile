.PHONY: backend_tests backend_tests_watch frontend_tests tests lint backend_lint frontend_lint format

# Testing
backend_tests:
	docker-compose exec backend pytest -v

backend_tests_watch:
	docker-compose exec backend pytest -v --tb=short -f

frontend_tests:
	docker-compose exec frontend npm run test:run

tests: backend_tests frontend_tests

# Linting
backend_lint:
	@echo "Running flake8..."
	docker-compose exec backend flake8 app/
	@echo "Running black check..."
	docker-compose exec backend black --check app/
	@echo "Running isort check..."
	docker-compose exec backend isort --check-only app/
	@echo "Running mypy..."
	docker-compose exec backend mypy app/

frontend_lint:
	docker-compose exec frontend npm run lint

lint: backend_lint frontend_lint

# Formatting
backend_format:
	docker-compose exec backend black app/
	docker-compose exec backend isort app/

frontend_format:
	docker-compose exec frontend npm run format

format: backend_format frontend_format
