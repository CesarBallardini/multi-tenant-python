# Tooling

Linting, type checking, tests organized by kind, and security are wired up from the first
commit, so "it's clean" is what happens by default, not something someone has to remember
to run by hand.

## What's in here

* **[uv](https://docs.astral.sh/uv/)** for dependency and environment management, with separate groups (`dev` vs `deploy`).
* **[ruff](https://docs.astral.sh/ruff/)** as linter and formatter (`ruff.toml`).
* **[pyright](https://microsoft.github.io/pyright/)** + **[pyrefly](https://pyrefly.org/)** as a pair of type checkers, run on purpose (`pyrightconfig.json`, `pyrefly.toml`).
* **[bandit](https://bandit.readthedocs.io/)** (SAST), **[pip-audit](https://pypi.org/project/pip-audit/)** + **[OSV-Scanner](https://google.github.io/osv-scanner/)** (SCA) against `uv.lock` (`bandit.yaml`). OSV-Scanner is a standalone Go binary, not a PyPI package, so it doesn't go through `uv` — locally it just needs to be on `PATH` (`choco install osv-scanner` on Windows), in CI it runs via Google's official reusable workflow (see `security.yml`).
* **[pytest](https://docs.pytest.org/)** with tests split by kind: `unit/`, `integration/`, `acceptance/` (BDD via [pytest-bdd](https://pytest-bdd.readthedocs.io/)), `e2e/`.
* **[pre-commit](https://pre-commit.com/)** hooking lint, format, and lockfile checks before every commit.
* A `Makefile` as the single interface — nobody needs to memorize the exact command for each tool.
* Three independent GitHub Actions workflows in `.github/workflows/`, one per concern, each with its own badge in the [README](../README.md): `check.yml` (lint + format + types), `pytest.yml`, `security.yml`.

## Prerequisites

* [uv](https://docs.astral.sh/uv/) (verified with the latest stable release)
* Python 3.14 (uv installs it automatically if missing, per `.python-version`)
* Git
* [OSV-Scanner](https://google.github.io/osv-scanner/) on `PATH` (only needed for `make security`; on Windows, `choco install osv-scanner`)

## Getting started

Clone it:

```bash
git clone https://github.com/CesarBallardini/multi-tenant-python
cd multi-tenant-python
```

Install dependencies and the pre-commit hooks:

```bash
make install
```

From there, everything goes through the Makefile:

```bash
make                  # no target: lists all available targets
make lint             # ruff check + ruff format --check
make format           # ruff format + ruff check --fix
make types            # pyright + pyrefly
make test             # pytest (unit + integration + acceptance, e2e excluded by default)
make test-bdd         # only the acceptance tests (pytest -m bdd)
make test-integration # only the integration tests (pytest -m integration)
make test-e2e         # pytest -m e2e
make security         # bandit + pip-audit --skip-editable + osv-scanner
make precommit        # run all pre-commit hooks by hand
```

## Updating dependencies

By default, `uv run` and `uv sync` can re-resolve and rewrite `uv.lock` on their own if they detect `pyproject.toml` changed. For any command that's meant to just *run* something (CI, onboarding, any given `make test`), pin the lockfile to exactly what's committed:

```bash
uv sync --frozen              # installs exactly what uv.lock says, resolves nothing
uv run --frozen pytest        # same idea, for any one-off command
```

The local pre-commit hook (`uv lock --check`) already fails if `uv.lock` drifts out of sync with `pyproject.toml` — so a `uv sync`/`uv run` without `--frozen` that accidentally rewrites the lock gets caught before the commit, not in CI.

To update dependencies **on purpose**, the flow is explicit, never implicit:

```bash
uv lock --upgrade-package ruff   # updates just that package to the max pyproject.toml allows
uv lock --upgrade                # updates everything pyproject.toml's constraints allow
```

Both commands rewrite `uv.lock` — review the diff (`git diff uv.lock`) before continuing. After updating, run the full suite before committing:

```bash
uv sync --all-groups   # installs whatever just landed in the updated lock
make lint types test security
```

## Building a wheel

The distribution and the importable package are both `academy` (`[project] name` and `[tool.hatch.build.targets.wheel]` in `pyproject.toml`, with `hatchling` as build backend). To generate the wheel:

```bash
uv build
```

This leaves `dist/academy-0.1.0-py3-none-any.whl` and the matching sdist. To test it installed in another environment:

```bash
uv pip install dist/academy-0.1.0-py3-none-any.whl
python -c "from academy.domain.academics.term import Term; print(Term(2026, 1).label())"
```

The `py.typed` marker that ships in `src/academy/` travels inside the wheel, so any project that installs this package and imports it inherits its type hints instead of its type checker treating it as `Any`.
