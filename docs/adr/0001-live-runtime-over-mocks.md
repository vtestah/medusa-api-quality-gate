# 1. Test against a live runtime instead of mocks

Status: Accepted

## Context

The quality gate validates a Medusa v2 commerce backend: regions and pricing,
product catalog, carts and market-driven shipping, localized catalog content, and
Admin API access control. Much of this behavior is non-trivial and stateful — it
spans the API, PostgreSQL, and Redis.

Two broad approaches were available:

- Mock or stub the Store/Admin API and assert against canned responses.
- Run the tests against a real Medusa runtime backed by a real database.

Hand-written mocks of a system this rich drift from reality quickly: they encode
assumptions about response shapes, seed data, and status codes that the real
service may not share, and they pass even when the contract has changed. The point
of this repository is to catch exactly those integration problems.

## Decision

Test against a real Medusa runtime brought up with Docker Compose
(postgres + redis + medusa), both locally and in CI.

- Locally, `make up` and `make seed` stand the stack up and seed the canonical
  catalog.
- In CI, `integration.yml` brings the runtime up inside the pipeline, seeds demo
  data, creates the admin user, and resolves the publishable key from the
  `api_key` table before running the full pytest suite. `e2e.yml` does the same and
  adds the storefront for Playwright.
- Pydantic v2 contracts validate the actual Store API responses; cross-layer checks
  read the real PostgreSQL state (read-only) and reconcile it against the API.

## Consequences

- Tests exercise real integration behavior — schema drift, seed assumptions, status
  codes, and DB state are checked against the running system, not a fixture.
- Contracts are validated against payloads the service actually returns.
- The runtime is slower to start and requires Docker, so it is not always available
  locally. Runtime-bound tests are guarded so they skip rather than fail when the
  stack is down; see [ADR 0002](0002-test-pyramid-and-skip-vs-fail.md).
- CI must seed data and resolve the publishable key dynamically; the integration and
  e2e jobs take minutes and run on `main`/`master` rather than on every push.
- To keep fast feedback, pure-logic invariants are still tested without a runtime as
  the base of the pyramid.
