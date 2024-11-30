.PHONY: run
run:
	@docker compose -f docker-compose.tests.yaml build && docker compose -f docker-compose.tests.yaml up
