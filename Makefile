DEV=docker-compose -f docker-compose.dev.yml -p my-stuff-dev
PROD=docker-compose -f docker-compose.prod.yml -p my-stuff-prod

dev-build:
	$(DEV) build --no-cache

dev-run:
	$(DEV) up --build

dev-start:
	$(DEV) up --build --detach

dev-stop:
	$(DEV) down

dev-restart: dev-stop dev-start

dev-shell:
	$(DEV) exec web bash

dev-psql:
	$(DEV) exec db psql -U my_stuff my_stuff_dev

prod-build:
	$(PROD) build --no-cache

prod-run:
	$(PROD) up --build

prod-start:
	$(PROD) up --build --detach

prod-stop:
	$(PROD) down

prod-restart: prod-stop prod-start

prod-shell:
	$(PROD) exec web bash

prod-psql:
	$(PROD) exec db psql -U my_stuff my_stuff_prod

prod-data-init:
	$(PROD) exec web python manage.py create_db
	$(PROD) exec web python manage.py seed_test_db
