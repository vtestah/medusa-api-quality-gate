# Test Plan

Working notes on how this repository tests the Medusa-based commerce stack: what
is under test, the layers we test at, where they run, and the gates that have to
stay green. It is a living document — it tracks the suite as it exists, not an
aspirational spec.

## Scope and system under test

The system under test is a real Medusa v2 runtime, not a mock:

- **Store API** and **Admin API** served at `http://localhost:9000`
  (`/health`, `/store/*`, `/admin/*`, admin app at `/app`).
- **PostgreSQL** (host `localhost:5433`, database `medusa`) as the backing store.
- **Redis** as the cache and event bus.
- A **Next.js storefront** at `http://localhost:8000`, localized per market
  (`/ru`, `/us`).

Two public markets drive most of the behavior:

| Market | Prefix | Region currency | UI locale |
| ------ | ------ | --------------- | --------- |
| Russia | `/ru`  | `rub`           | `ru-RU`   |
| US     | `/us`  | `usd`           | `en-US`   |

In scope: Store API response contracts, negative input handling, cart/checkout
and market-driven shipping, localization of catalog content, cross-layer database
state, Admin API authentication/authorization, and storefront UI flows for both
markets.

Out of scope for now: payment capture against real providers, email/notification
delivery, the admin content-authoring UI, and dedicated security testing. Near-term
candidates are listed under [Backlog](#backlog).

## Test layers

The suite is shaped as a pyramid: a wide, fast base that needs no runtime, a live
integration band against the API and database, and a thin UI cap on top. The
rationale for the shape and for skipping (rather than failing) when the runtime is
down is recorded in [`adr/0002-test-pyramid-and-skip-vs-fail.md`](adr/0002-test-pyramid-and-skip-vs-fail.md).

### Property-based and unit (no runtime)

Hypothesis property tests cover pure-logic invariants — Store API contract
parsing, cart aggregation by `variant_id`, cart-client pre-flight, and the
fail-fast `Settings` validation. Unit and bootstrap checks cover the HTTP
transport, configuration, and data factories. This layer runs on every push with
no network access and is the base of the pyramid. Lives in `quality-gate/tests/`
(the `*_property.py` files plus `smoke/`).

### Contract

Strict Pydantic v2 validation of Store API responses (`/store/regions`,
`/store/products`) with round-trip (serialize → deserialize) checks, so a contract
that parses also re-serializes losslessly. Marker: `contract`. Lives in
`quality-gate/tests/contract/`.

### Negative

Store API negative input: missing/invalid authentication, malformed payloads, and
boundary values. Confirms the API rejects bad input with the expected status codes
rather than accepting or 500-ing. Lives in `quality-gate/tests/negative/`.

### Cart and checkout

Cart creation, line items, and market-driven shipping for RU and US. The region is
resolved at runtime by matching the expected currency from `Settings.markets`, so
no region ids are hard-coded. Marker: `cart`. Lives in `quality-gate/tests/cart/`.

### Localization

`x-medusa-locale` contract checks: the same catalog handle returns localized
content for RU versus US (title, description, category name). Marker:
`localization`. Lives in `quality-gate/tests/localization/`.

### Database (cross-layer)

Read-only PostgreSQL reconciliation of API state against database rows via
`psycopg` — seed counts and cart state observed through the API are checked against
the rows behind them. No writes. Marker: `db`, guarded by the `db_connection`
fixture. Lives in `quality-gate/tests/db/`.

### Admin API

Admin authentication and authorization, both against the live runtime and as
mocked unit checks for the client wiring. Marker: `admin`. Lives in
`quality-gate/tests/admin/`.

### UI E2E (Playwright)

TypeScript Playwright suite driving the localized storefront: market routing,
localized chrome, currency, and market shipping. Page Object Model with one
project per market (`ru`, `us`) over the same specs. Lives in `e2e/`
(`smoke.spec.ts`, `localization.spec.ts`, `cart.spec.ts`).

### Performance (k6)

Basic k6 scripts (`k6/smoke.js`, `k6/load.js`) exercise the read-only Store API
endpoints the storefront depends on (`/store/regions`, `/store/products`) plus
`/health`, with error-rate and p95-latency thresholds. Run manually against a live
runtime today; not yet a CI gate. See [`../k6/README.md`](../k6/README.md).

## Environments and test data

- **Local**: `docker compose` brings up postgres + redis + medusa + storefront.
  Use `make up` then `make seed`.
- **CI**: the same compose stack is stood up inside the pipeline (see
  [CI gates](#ci-gates)).
- **Configuration**: Python settings come from `QUALITY_GATE_*` environment
  variables (`medusa_base_url`, `publishable_key`, `db_url`,
  `admin_email`/`admin_password`, market currencies and shipping methods). Defaults
  target the local Docker runtime, so the suite runs with no configuration locally.
- **Test data**: the Medusa seed (`pnpm seed`) creates the canonical catalog — two
  regions (`ru`/`us`), six products, four categories — plus the demo product
  `basis-heavy-tee` and category `hoodies` used as fixtures. Tests resolve ids at
  runtime (region by currency, variant from the demo product) rather than
  hard-coding them.
- **Publishable key**: the Store API requires the `x-publishable-api-key` header.
  It is generated during seed; CI reads it from the `api_key` table in PostgreSQL.
- **Admin user**: `admin@example.com` / `supersecret`, created for the Admin API
  checks.

## CI gates

Three GitHub Actions workflows:

1. **`quality-gate.yml`** — fast, no runtime. Runs on Python 3.11 and 3.12:
   `ruff check`, `mypy --strict`, and `pytest` with coverage. Runtime-bound tests
   skip automatically when Medusa/PostgreSQL are unavailable; the property and unit
   layers run on every push. Coverage floor is enforced (`fail_under = 70`).
2. **`integration.yml`** — brings the runtime up (postgres + redis + medusa), seeds
   demo data, creates the admin user, resolves the publishable key from the
   database, and runs the full pytest suite live. Here the contract / negative /
   cart / db / localization / admin layers execute for real instead of skipping.
3. **`e2e.yml`** — brings up the full runtime including the storefront, restarts it
   with the seeded key, and runs the Playwright RU/US projects.

A change is mergeable when `quality-gate` is green. `integration` and `e2e`
validate live behavior on `main`/`master`.

## Reporting

- **pytest**: terminal coverage with missing lines; optional self-contained HTML
  report (`quality-gate/reports/smoke-report.html`) and Allure results
  (`allure-results/`). `coverage.xml` is uploaded as a CI artifact.
- **Playwright**: HTML report plus trace, screenshot, and video retained on
  failure; uploaded as a CI artifact.
- **k6**: end-of-test summary with threshold results, p95 latency, and error rate.

## Acceptance criteria

- `ruff` and `mypy --strict` clean.
- `pytest` green with coverage ≥ 70%.
- The live integration suite is green against a seeded runtime, with no
  runtime-bound test silently skipping in CI — skips are reserved for genuinely
  unavailable infrastructure (locally), not for masking failures.
- Both Playwright projects (`ru`, `us`) green.
- Contract models validate real Store API responses with no missing required or
  unexpected fields, and round-trip losslessly.
- Each market resolves its region, currency, and shipping methods as configured in
  `Settings.markets` (API) and the e2e market profiles (UI).

## Backlog

Tracks the repository roadmap:

- Schemathesis fuzzing driven by an OpenAPI schema.
- Public Allure report on GitHub Pages.
- Candidates: accessibility checks (axe-core) on the storefront, and promoting the
  k6 checks to a scheduled CI job once latency budgets are tuned to the CI host.
