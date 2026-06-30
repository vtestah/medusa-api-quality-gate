# 3. Two test stacks: pytest for API, Playwright for UI

Status: Accepted

## Context

The repository needs both API-level quality gating and UI verification of the
localized storefront. These have different centers of gravity:

- API testing benefits from Python: Pydantic v2 for strict response contracts,
  Hypothesis for property-based invariants, and `psycopg` for read-only PostgreSQL
  reconciliation.
- UI E2E benefits from Playwright, which has native TypeScript support, browser
  automation, per-project configuration, and built-in tracing/screenshots/video.

Forcing both onto a single toolchain would mean giving up the strongest tool for one
of the two jobs.

## Decision

Keep two separate stacks, each owning its layer.

- **Python / pytest** lives in `quality-gate/` and covers Store and Admin API
  contracts, negative input, cart/checkout, localization, cross-layer DB checks, and
  property-based tests. It's validated by `ruff`, `mypy --strict`, and coverage.
- The **Playwright (TypeScript)** suite in `e2e/` drives storefront UI flows with
  the Page Object Model and one project per market (`ru`, `us`).

Each stack has its own dependencies, configuration, and CI workflow
(`quality-gate.yml` / `integration.yml` for Python, `e2e.yml` for Playwright). They
overlap intentionally on the market proof points (currency, shipping methods, and
localization), where the API verifies the contract and the UI verifies what the user
actually sees.

## Consequences

- Each layer uses the most appropriate tool, with clear ownership boundaries between
  API and UI tests.
- The stacks build, run, and scale independently in CI; an API change need not run
  the browser suite and vice versa.
- Two toolchains must be maintained: a Python virtualenv and a pnpm/Node setup.
- Market expectations exist in two places: `Settings.markets` (Python) and the e2e
  market profiles (TypeScript). This duplication is accepted on purpose: each layer
  asserts the same expectations independently, so a regression in one is not masked
  by shared fixtures.
