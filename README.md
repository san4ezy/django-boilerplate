# Modern Django 6.x Boilerplate

A feature-rich, high-performance boilerplate for Django + Django REST Framework projects, built with **Python 3.14+**, **Django 6.x**, **`uv`** dependency management, and fully containerized with **Docker Compose**.

All setup and development tasks are automated using a standard **`Makefile`**.

---

## Tech Stack

* **Python:** 3.14+
* **Framework:** Django 6.x, Django REST Framework
* **Dependency & Environment Management:** `uv` via `pyproject.toml`
* **Containerization:** Docker & Docker Compose (multi-stage build, non-root user, health checks)
* **Database:** PostgreSQL 18.6
* **Task Automation:** `Makefile`
* **Code Quality & Testing:** Pytest, Black, isort, Flake8, mypy, factory-boy

---

## Prerequisites

Before starting, ensure you have the following installed on your system:

* [Docker](https://docs.docker.com/get-docker/) and Docker Compose
* `make` utility (pre-installed on Linux/macOS)
* `git`

---

## Quick Start

Get your project up and running in less than 5 minutes:

### 1. Initialize Environment Configuration
Copy environment templates and replace initial project placeholders:

```bash
make setup ENV=development
```

### 2. Generate Cryptographic Keys

Generate random secure keys (`SECRET_KEY`, `POSTGRES_PASSWORD`, JWT keys) and save them to `environments/development/app.env`:

```bash
make keygen ENV=development
```

### 3. Build & Run Containers

Build Docker images using multi-stage `uv` layers and start containers in background:

```bash
make build
make up
```

### 4. Apply Database Migrations & Create Superuser

```bash
make migrate
make superuser
```

Your Django application is now running at: `http://localhost:8000/admin/`

---

## Available Commands

Run `make` or `make help` to view all available commands in your terminal.

### Environment Setup

* `make setup ENV=<env>` — Prepare environment configuration files (`app.env` and `docker-compose.yml`).
* `make keygen ENV=<env>` — Generate secure random secrets for the specified environment.

### Docker Operations

* `make build` — Build Docker service images.
* `make up` — Start containers in background.
* `make down` — Stop and remove running containers.
* `make restart` — Restart containers.
* `make rebuild` — Full rebuild cycle (down -> build -> up).
* `make logs` — Tail container logs in real time.
* `make ps` — List running project containers.
* `make bash` — Open interactive bash session inside Django container.

### Django Commands

* `make migrate` — Apply database migrations.
* `make makemigrations` — Generate new database migrations.
* `make showmigrations` — List status of all migrations.
* `make superuser` — Create Django superuser interactively.
* `make shell` — Open interactive Django shell (`shell_plus`).
* `make collectstatic` — Collect static files.
* `make test` — Run test suite via `pytest`.

### Code Generators

* `make startapp app=<name>` — Scaffold a new Django app under `apps/<name>` from `boilerplate/startapp/`.
* `make makecommand app=<name> cmd=<command>` — Scaffold a new management command in `apps/<name>/management/commands/<command>.py`.

### Database Backup & Restore

* `make backup` — Dump PostgreSQL database into `backups/` directory.
* `make restore` — Restore database from the latest `.db` dump file in `backups/`.

### Code Quality & Linters

* `make lint` — Run all quality checks (`black`, `isort`, `flake8`, `mypy`).
* `make black` — Auto-format code using Black.
* `make isort` — Sort imports using isort.
* `make flake8` — Run Flake8 linter.
* `make mypy` — Perform static type checking with mypy.

---

## Project Structure

```text
ROOT/
├── apps/                # Application modules (core, users, etc.)
│   ├── core/            # Base abstract models and helpers
│   └── users/           # Custom user model and authentication
├── boilerplate/         # Generator templates
│   ├── startapp/        # Template for new Django apps
│   └── makecommand/     # Template for management commands
├── config/              # Django settings split by environment
│   └── settings/        # base.py, development.py, production.py, staging.py, test.py
├── environments/        # Isolated environment settings
│   ├── development/     # app.env.example, docker-compose.yml.example
│   ├── production/      # app.env.example, docker-compose.yml.example
│   └── staging/         # app.env.example, docker-compose.yml.example
├── Dockerfile           # Python 3.14+ multi-stage Dockerfile with uv
├── Makefile             # Automation Makefile
└── pyproject.toml       # Single config for dependencies (uv) & dev tools
```
