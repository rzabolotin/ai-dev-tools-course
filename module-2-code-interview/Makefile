.PHONY: backend_tests backend_tests_watch

backend_tests:
	docker-compose exec backend pytest -v

backend_tests_watch:
	docker-compose exec backend pytest -v --tb=short -f
