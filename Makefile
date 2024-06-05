ENV_FILE := local.env

run: down rm-volume rebuild
	docker-compose --env-file $(ENV_FILE) up -d --remove-orphans

rebuild:
	docker build -t "blamer_python_deps" -f Dockerfile.python_deps .
	docker build -t "blamer" .

rm-volume:
	rm -rf db-data

down:
	docker-compose down

logs:
	docker logs blamer-bot

run-local:
	env $$(cat local.env | xargs) ./venv/bin/python app/main.py

generate_migration: down rm-volume
	docker-compose --env-file $(ENV_FILE) up -d blamer-db
	sleep 15
	cd app && \
	env $$(cat ../local.env | xargs) \
	env 'DB_HOST=localhost' \
	env 'DB_PORT=25432' \
	../venv/bin/python -m alembic revision --autogenerate -m $(m)

