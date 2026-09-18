# Terms Cheat Sheet

Purpose: a compact review of the software engineering terms that appear while turning an AI/ML idea into a production-style app. Keep each entry short: definition, project example, and one reference for deeper study.

## Backend

### uv

- A Python project/package manager: installs dependencies, creates a lockfile, and runs commands inside the project environment.
- In this project: `backend/pyproject.toml` declares dependencies; `backend/uv.lock` pins versions; `make be-dev` runs `uv run fastapi dev main.py`.
- Production idea: lockfiles reduce "works on my machine" dependency drift.
- Reference: https://docs.astral.sh/uv/

### FastAPI

- A Python web framework for building APIs with validation, automatic docs, and dependency injection.
- In this project: `backend/main.py` creates the app, checks database connectivity on startup, creates tables, and includes `classrooms` and `teachers` routers.
- Useful for AI/ML production because model or workflow logic often needs to be exposed as HTTP APIs.
- Reference: https://fastapi.tiangolo.com/

### REST API

- An API style centered on resources and HTTP methods.
- In this project: `classrooms` and `teachers` are resources; examples include `GET /classrooms/`, `POST /teachers/`, and `PATCH /teachers/{teacher_id}`.
- Quick rule: URLs are nouns/resources; HTTP methods are actions.
- Reference: https://developer.mozilla.org/en-US/docs/Glossary/REST

### Endpoint

- One concrete API address that a client can call.
- Example: `GET /teachers/2` returns the teacher with ID `2`.
- Typical end-to-end path: HTTP request -> router/controller -> schema validation -> repository -> database -> response.
- Reference: https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Client-side_APIs/Introduction

### HTTP Methods

- `GET`: read data without changing state. Example: `GET /classrooms/`.
- `POST`: create a new resource. Example: `POST /teachers/`.
- `PATCH`: update part of a resource. Example: change a classroom `capacity`.
- `PUT`: replace a whole resource.
- `DELETE`: delete a resource. Example: `DELETE /teachers/{teacher_id}`.
- Reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods

### HTTP Status Codes

- `200 OK`: request succeeded.
- `201 Created`: creation succeeded; used by `POST /classrooms/` and `POST /teachers/`.
- `204 No Content`: success with an empty response body; used by `DELETE /teachers/{teacher_id}`.
- `400 Bad Request`: request is syntactically valid but invalid for app logic; example: empty `PATCH` body.
- `404 Not Found`: resource does not exist; example: missing classroom or teacher ID.
- `422 Unprocessable Content`: validation failed; FastAPI/Pydantic returns this for invalid fields such as `capacity <= 0`.
- Reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

### ORM

- Object-Relational Mapping: maps classes/objects in code to tables/rows in a relational database.
- In this project: `Classroom(SQLModel, table=True)` and `Teacher(SQLModel, table=True)` define database tables.
- Note: the project defines ORM models but repositories currently use raw SQL via `text(...)` for CRUD queries.
- Reference: https://sqlmodel.tiangolo.com/

### DTO / Schema

- DTO means Data Transfer Object: a shape used to move data across API or layer boundaries.
- In this project: `ClassroomCreateRequest`, `TeacherUpdateRequest`, and `TeachersResponse` are Pydantic schemas.
- Why it matters: API input/output should be explicit and separate from database internals.
- Reference: https://docs.pydantic.dev/

### Repository

- The layer responsible for talking to storage.
- In this project: `ClassroomRepo` and `TeacherRepo` contain methods such as `list`, `get_by_id`, `create`, `update`, and `delete`.
- Why it matters: routers do not need to know SQL/session details, and database logic is easier to test or change.
- Reference: https://martinfowler.com/eaaCatalog/repository.html

### Handler / Controller / Router

- The API layer that receives HTTP requests, validates input, calls the needed logic, and returns a response.
- In FastAPI this is usually a router plus path operation functions.
- In this project: `backend/routers/classrooms.py` and `backend/routers/teachers.py`.
- Reference: https://fastapi.tiangolo.com/tutorial/bigger-applications/

### Dependency Injection

- A pattern where dependencies are provided from the outside instead of created manually inside each function.
- In this project: `repo: TeacherRepo = Depends(TeacherRepo)` and `Session = Depends(get_session)`.
- Why it matters: tests can override real dependencies, for example replacing PostgreSQL with an in-memory SQLite database.
- Reference: https://fastapi.tiangolo.com/tutorial/dependencies/

### Authentication vs Authorization

- Authentication answers: "Who are you?" Examples: login, token, session.
- Authorization answers: "What are you allowed to do?" Examples: teacher/admin/student permissions.
- Current project status: auth is not implemented yet. A production version should protect write endpoints and define roles.
- Reference: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

## Architecture

### Monolithic Architecture

- One app/repo/deployable contains multiple features in one codebase.
- This project is a small monolith: frontend, backend, database config, and docs live together.
- Good for learning and MVPs because it reduces operational complexity.
- Reference: https://martinfowler.com/bliki/MonolithFirst.html

### Layered Architecture

- Code is separated by responsibility: API layer -> validation/schema layer -> repository/data layer -> database.
- In this project:
  - Routers: `backend/routers/`
  - Schemas/DTOs: `backend/schemas/`
  - Repositories: `backend/repository/`
  - Models: `backend/models/`
- Why it matters: each layer is easier to understand, test, and replace.
- Reference: https://martinfowler.com/eaaCatalog/

### Sync/Async - Architecture Meaning

- Synchronous architecture: caller waits for the result immediately. Example: frontend calls `POST /classrooms/` and waits for the created classroom.
- Asynchronous architecture: caller submits work and processing happens later. Examples: queueing training jobs, document parsing, embedding generation, or email notifications.
- AI/ML production often needs async workflows for long-running tasks.
- Related keywords: queue, worker, background job, event-driven architecture.
- Reference: https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/event-driven

### Sync/Async - Programming Meaning

- Sync code blocks while waiting for I/O.
- Async code uses `async`/`await` so the event loop can do other work while waiting.
- Current project status: route handlers and repositories are sync `def` functions using a sync SQLModel/SQLAlchemy session.
- Important nuance: adding `async def` does not make blocking database code non-blocking unless the database driver/session is async too.
- Reference: https://fastapi.tiangolo.com/async/

## Testing

### Testing

- Code that checks whether the app behaves as expected.
- In this project: `make be-test` runs `uv run pytest`; integration tests live under `backend/tests/intergration/`.
- Production idea: tests let the team change code without guessing whether old flows broke.
- Reference: https://docs.pytest.org/

### Unit Test

- Tests one small function/class in isolation, preferably without real database/network calls.
- Possible future examples: test scheduling logic, permission rules, or ML preprocessing helpers.
- Unit tests are fast and help locate failures precisely.
- Reference: https://martinfowler.com/bliki/UnitTest.html

### Integration Test

- Tests multiple parts working together.
- In this project: `TestClient` calls real FastAPI routers while dependency overrides swap PostgreSQL for an in-memory SQLite test database.
- Examples: `test_create_classroom_returns_created_classroom`, `test_delete_teacher_deletes_teacher`.
- Reference: https://fastapi.tiangolo.com/tutorial/testing/

### V-Model

- A mental model that connects requirements/design/implementation with matching test levels.
- Left side: requirements -> design -> implementation. Right side: unit tests -> integration tests -> acceptance/system tests.
- Project example: requirement "create a teacher" is covered by `test_create_teacher_returns_created_teacher`.
- Reference: https://en.wikipedia.org/wiki/V-model

## Frontend

### Vite

- A fast frontend dev server and build tool.
- In this project: `frontend/package.json` has `dev`, `build`, and `preview` scripts; `vite.config.ts` configures Vite.
- Reference: https://vite.dev/

### React

- A UI library for building interfaces from components.
- In this project: `frontend/src/App.tsx` currently renders `Hello World`.
- Next likely step: React fetches the REST API and renders classroom/teacher lists and forms.
- Reference: https://react.dev/

### shadcn/ui

- A set of copyable React components, commonly used with Tailwind CSS.
- Current project status: shadcn/ui is not installed yet.
- Why it may help later: forms, tables, dialogs, and buttons can be standardized without building every UI primitive from scratch.
- Reference: https://ui.shadcn.com/

### Tailwind CSS

- A utility-first CSS framework: style UI using small classes such as `flex`, `gap-2`, and `text-sm`.
- Current project status: Tailwind is not configured yet.
- Why it may help later: fast, consistent styling, especially if the project adopts shadcn/ui.
- Reference: https://tailwindcss.com/docs

### Figma

- A collaborative design tool used to create wireframes, UI mockups, prototypes, and design systems before implementation.
- In a product workflow: Figma helps align layout, components, spacing, colors, and user flows before React code is written.
- Why it matters: frontend work becomes faster when developers build from clear designs instead of guessing UI details.
- Reference: https://help.figma.com/

### Single Page Application

- A web app that loads one HTML page and updates the UI in the browser as the user navigates.
- In this project: React + Vite is a typical SPA setup; later the app can fetch `/classrooms/` and `/teachers/` without full page reloads.
- Why it matters: SPAs feel interactive, but need careful handling of routing, loading states, errors, and API calls.
- Reference: https://developer.mozilla.org/en-US/docs/Glossary/SPA

### Responsive Design

- Designing UI so it works across screen sizes: desktop, tablet, and mobile.
- Examples: tables may become stacked cards on mobile; forms should keep readable spacing and usable inputs.
- Why it matters: production apps are used on many devices, not only the developer's laptop.
- Reference: https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design

### Landing Website/Page

- A focused page designed to introduce a product, explain value, and guide the user toward one main action.
- Different from an app screen: a landing page sells or explains; an app screen lets users do the actual work.
- For this classroom project: the main app should prioritize managing teachers/classrooms; a landing page is optional.
- Reference: https://www.nngroup.com/articles/landing-pages/

### Design System

- A shared set of UI rules, components, tokens, and patterns: colors, typography, spacing, buttons, forms, tables, dialogs.
- Examples: shadcn/ui components plus Tailwind tokens can become the project's design system.
- Why it matters: teams build faster and avoid inconsistent screens.
- Reference: https://www.figma.com/design-systems/

### JavaScript/TypeScript Runtime

- The environment that executes JavaScript or TypeScript-compiled JavaScript.
- Browser runtime: runs frontend code such as React components.
- Node.js runtime: runs tooling such as Vite, ESLint, TypeScript, and package managers.
- In this project: frontend tooling runs on Node.js; the built app runs in the browser.
- Reference: https://nodejs.org/en/learn/getting-started/introduction-to-nodejs

### JavaScript/TypeScript Package Managers

- npm and Yarn are package managers for JavaScript/TypeScript projects.
- They install dependencies, run scripts, and manage lockfiles.
- In this project: `frontend/package.json` defines dependencies and scripts; `frontend/yarn.lock` pins installed versions; examples are `yarn dev`, `yarn build`, and `yarn lint`.
- Reference: https://yarnpkg.com/getting-started

### Linter

- A tool that catches risky code patterns and style issues.
- In this project: frontend uses ESLint (`yarn lint`); backend uses Ruff (`make be-lint`).
- Examples: unused variables, invalid React hook usage, suspicious Python patterns.
- References: https://eslint.org/docs/latest/ and https://docs.astral.sh/ruff/

### Formatter

- A tool that automatically formats code so the team does not debate whitespace/style.
- In this project: backend uses Ruff format via `make be-fmt`.
- A common frontend option is Prettier, but it is not configured here yet.
- Reference: https://docs.astral.sh/ruff/formatter/

### Axios

### Mock API

### Zustand

### React Router

### Local Storage/Cookie

## Database & Runtime

### PostgreSQL

- A production-grade relational database.
- In this project: `docker-compose.yml` runs `postgres:18-alpine`; backend connects using `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
- Reference: https://www.postgresql.org/docs/

### Docker / Podman Compose

- Compose describes local services in a YAML file.
- In this project: `make start` starts the database container; `make end` stops it and removes the volume.
- Production idea: containerized local services make onboarding and environment setup more predictable.
- Reference: https://docs.docker.com/compose/

### Environment Variables

- Configuration values stored outside source code: database names, passwords, API keys, secrets.
- In this project: `backend/config.py` reads `.env` using `pydantic-settings`.
- Rule of thumb: config that changes by environment should live outside code; secrets should not be committed.
- Reference: https://12factor.net/config

## Production Mindset for AI/ML

- An AI/ML model is not production just because it runs in a notebook. It needs APIs, auth, logging, monitoring, tests, deployment, rollback, and model/data versioning.
- Backend exposes model or workflow capabilities; frontend lets users operate them; database stores state; workers handle long-running jobs.
- Each feature should have an end-to-end path: UI/API contract -> endpoint -> validation -> storage/model call -> tests -> deployment.
- Future sections to add as the project grows: deployment, CI/CD, observability, background jobs, model serving, vector databases, caching, rate limits, and model evaluation.
