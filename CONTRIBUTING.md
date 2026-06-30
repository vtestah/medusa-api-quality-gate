# Contributing

Working notes for hacking on this repo. There are two test layers:

- `quality-gate/`: a Python/pytest API quality gate that runs against the live Medusa Store API and PostgreSQL.
- `e2e/`: Playwright UI end-to-end tests in TypeScript, run against the localized RU/US storefront.

## Prerequisites

- Python 3.11 or 3.12 (CI runs both).
- `pnpm` (the package manager for the whole repo; version is pinned in `package.json`).
- Docker + Docker Compose, needed only for the live runtime (integration tests and E2E).

## Local setup

Create the virtualenv and install the quality gate with dev extras:

```bash
make setup
# equivalent to:
#   pnpm quality-gate:venv
#   pnpm quality-gate:install
```

> The `.venv` console-script shebangs can go stale after the venv is moved or
> recreated. Always invoke Python tools through the interpreter, e.g.
> `.venv/bin/python -m pytest` / `.venv/bin/python -m ruff`, not the
> `.venv/bin/<tool>` wrappers. The `make` targets already do this.

## Lint and type-check

```bash
make lint   # ruff + mypy strict, run from quality-gate/
```

## Tests

The property-based and unit layers run without a runtime; the integration
layers (contract / negative / cart / db / localization) skip automatically when
Medusa or PostgreSQL are unreachable.

```bash
make test          # full pytest suite
make smoke         # fast smoke checks only
```

Run the same gate CI enforces (lint + type-check + tests with coverage):

```bash
make ci
```

Coverage has a floor of `fail_under = 70` (see `quality-gate/pyproject.toml`).

To exercise the integration layers for real, bring the runtime up first:

```bash
make up            # postgres + redis + medusa (+ storefront)
make seed          # seed demo data and sync the publishable key
make test
```

Live tests read configuration from `QUALITY_GATE_*` environment variables
(`medusa_base_url`, `publishable_key`, `db_url`, `admin_email`,
`admin_password`); see `.env.example`.

## UI E2E (Playwright)

Needs the runtime up (`make up` + `make seed`):

```bash
make e2e           # install Playwright + run the RU/US suites
```

Per-market projects (`ru`, `us`) and the storefront base URL come from the
Playwright config; override the host with `STOREFRONT_BASE_URL` if needed.

## CI

- `quality-gate.yml`: the fast gate (ruff + mypy strict + pytest with coverage). It runs on
  pushes and PRs that touch `quality-gate/**`. Keep this one green.
- `integration.yml` brings the runtime up, seeds data, resolves the
  publishable key from the database, then runs the full suite (push, nightly
  schedule, manual dispatch).
- `e2e.yml` runs Playwright RU/US against the live storefront (push, nightly
  schedule, manual dispatch).

JUnit results and coverage are uploaded as build artifacts, and a short test
summary is written to the workflow run summary.

## Branches and pull requests

- The default branch is `main`. Develop on a feature branch and open a PR
  against `main`.
- Run `make ci` locally before pushing; at minimum keep `make lint` clean.
- Keep PRs focused and describe what you changed and how you tested it.
- Don't commit secrets or local environment files (`.env`).
- Dependency updates are proposed automatically by Dependabot (`.github/dependabot.yml`).
