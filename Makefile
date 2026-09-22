.PHONY: start end be-dev be-test be-migrate be-migration be-seed-user be-fmt be-lint

start:
	podman compose up -d

end:
	podman compose down -v

be-dev:
	cd backend && uv run fastapi dev main.py

be-test:
	cd backend && uv run pytest

be-migrate:
	cd backend && PYTHONPATH=.. uv run alembic upgrade head

# Usage: make be-migration m="add foo column"
be-migration:
	cd backend && PYTHONPATH=.. uv run alembic revision --autogenerate -m "$(m)"

# Usage: make be-seed-user u=admin p=secret d="Admin"
be-seed-user:
	cd backend && PYTHONPATH=.. uv run python -m backend.scripts.seed_user --username "$(u)" --password "$(p)" --display-name "$(d)"

be-fmt:
	cd backend && uv run ruff format .

be-lint:
	cd backend && uv run ruff check . --fix