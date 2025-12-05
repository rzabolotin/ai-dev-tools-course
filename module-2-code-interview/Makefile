.PHONY: backend_tests backend_tests_watch frontend_tests tests

backend_tests:
	docker-compose exec backend pytest -v

backend_tests_watch:
	docker-compose exec backend pytest -v --tb=short -f

frontend_tests:
	docker-compose exec frontend npm run test:run

tests: backend_tests frontend_tests
