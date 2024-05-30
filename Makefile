run: migrate
	@env $(shell cat local.env) venv/bin/python app/main.py && read

migrate:
	@mkdir -p /var/lib/blamer_bot
	@sqlite3 /var/lib/blamer_bot/file.db "VACUUM;"
	@cd app && ../venv/bin/python -m alembic upgrade head

