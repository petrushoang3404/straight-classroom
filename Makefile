.PHONY: start end be-dev be-test

start:
	podman compose up -d

end:
	podman compose down -v

be-dev:
	cd backend && uv run fastapi dev main.py

be-test:
	cd backend && uv run pytest

be-fmt:
	cd backend && uv run ruff format .

be-lint:
	cd backend && uv run ruff check . --fix