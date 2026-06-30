# 2. Test pyramid and skip-vs-fail for runtime-bound tests

Status: Accepted

## Context

The suite mixes two kinds of tests: pure-logic checks that need nothing external,
and integration checks that need a live Medusa runtime and PostgreSQL. We want fast,
reliable feedback on every push, but we also want real integration coverage.

Running everything against a live runtime on every push is slow and brittle, and it
fails the moment the local stack is down — which conflates "infrastructure is
unavailable" with "a check has actually failed". Those two outcomes need to be
distinguishable.

## Decision

Shape the suite as a pyramid and separate infrastructure availability from test
outcome.

- **Base** — property-based (Hypothesis) plus unit/smoke tests. No network, run on
  every push.
- **Middle** — live integration: contract, negative, cart, db, localization, admin.
- **Cap** — Playwright UI E2E over the localized storefront.

Runtime-bound tests depend on guard fixtures: `runtime_ready` probes
`/health` and skips the test when Medusa is unreachable; `db_connection` skips when
PostgreSQL cannot be reached. So locally, with the stack down, the base layer stays
green and the integration layer skips cleanly.

In CI this is deliberately asymmetric: `quality-gate.yml` runs without a runtime
(integration tests skip), while `integration.yml` brings the runtime up so those
same tests must execute for real and are expected not to skip.

## Consequences

- `quality-gate.yml` stays fast and green without Docker; a missing runtime is a
  skip, not a red build.
- Developers can run the base layer locally with zero setup.
- A genuine failure could hide as a skip if a test is run only where the runtime is
  absent. This is mitigated by `integration.yml`, which runs the full suite against a
  live runtime on `main`/`master`, where skips are not expected.
- There is a discipline cost: any new runtime-bound test must depend on the correct
  guard fixture (`runtime_ready` and/or `db_connection`) so it behaves correctly in
  both environments.
