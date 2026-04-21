# ecom-quality-gate

![Medusa](https://img.shields.io/badge/Medusa-v2.13.6-0A7BFF)
![Next.js](https://img.shields.io/badge/Next.js-15.3.9-000000)
![next-intl](https://img.shields.io/badge/next--intl-4.9.1-0F172A)
![pnpm](https://img.shields.io/badge/pnpm-10.33.0-F69220)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-local_runtime-2496ED)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791)
![Redis](https://img.shields.io/badge/Redis-8-DC382D)

Public portfolio repository for a Senior SDET track focused on API quality gates for a headless commerce stack. The runtime under test is Medusa.js backed by PostgreSQL and Redis. The customer-facing target UI is a Next.js storefront localized as a dual-market demo: Russia first, United States second.

## Architecture

```text
ecom-quality-gate/
├── package.json         # Root scripts for Docker runtime
├── pnpm-workspace.yaml  # Monorepo policy for all JS apps
├── quality-gate/        # Python pytest framework for API quality gates
├── apps/
│   ├── medusa/          # System under test: Medusa backend
│   └── storefront/      # Next.js target UI for future browser automation
├── docker-compose.yml   # postgres + redis + medusa + storefront
└── README.md
```

## Dual-Market Demo

`Basis` is modeled as a fashion-basics storefront with one canonical catalog model and two public markets:

| Market | Path | Region | Currency | UI language | Shipping |
| --- | --- | --- | --- | --- | --- |
| Russia | `/ru` | `Russia` | `RUB` | Russian chrome | `Курьер`, `ПВЗ`, `Самовывоз` |
| United States | `/us` | `United States` | `USD` | English chrome | `Standard Shipping`, `Express Shipping` |

Catalog handles remain canonical in English on purpose, but display content is now served through the Medusa Translation Module. That gives us two clean layers:

- stable English identifiers for fixtures, URLs, and contracts
- localized product/category/collection content for `/ru` and `/us`

## UI Localization Library

Storefront shell localization is powered by `next-intl`, while Medusa Translation Module now owns catalog translations.

```text
/ru -> region: Russia, currency: RUB, locale: ru-RU
/us -> region: United States, currency: USD, locale: en-US
```

This split is deliberate:

- `region` controls pricing, shipping methods, and market behavior
- `next-intl` controls typed UI dictionaries for storefront chrome
- Medusa Translation Module serves translated product, category, collection, variant, and shipping content

Key files:

- `apps/storefront/src/i18n/messages/ru-RU.json`
- `apps/storefront/src/i18n/messages/en-US.json`
- `apps/storefront/src/i18n/request.ts`
- `apps/storefront/src/middleware.ts`

Runtime proof points:

- `/ru` renders Russian nav, hero, footer, and account login copy
- `/us` renders English nav, hero, footer, and account login copy
- metadata titles also switch by locale: `Basis | Российский storefront demo` vs `Basis | US storefront demo`
- `/ru/store` renders Russian product titles, category labels, collection titles, and category descriptions
- `/us/store` renders English catalog content and USD pricing

## Runtime URLs

- Storefront: `http://localhost:8000`
- Russian storefront: `http://localhost:8000/ru`
- US storefront: `http://localhost:8000/us`
- Medusa API: `http://localhost:9000`
- Medusa health: `http://localhost:9000/health`
- Medusa admin: `http://localhost:9000/app`
- PostgreSQL host access: `localhost:5433`

## Python Quality Gate

Python API automation now lives in `quality-gate/` and targets the live Medusa runtime from this repository.

Structure:

```text
quality-gate/
├── pyproject.toml
├── src/quality_gate/
│   ├── clients/   # Health, regions, products, categories
│   ├── models/    # Pydantic contracts
│   ├── db/        # PostgreSQL helpers
│   └── config.py
└── tests/
    ├── smoke/
    ├── localization/
    └── db/
```

Quick commands:

```bash
pnpm quality-gate:venv
```

```bash
pnpm quality-gate:install
```

```bash
pnpm quality-gate:test:smoke
```

```bash
pnpm quality-gate:test:localization
```

## Quick Start

```bash
pnpm docker:up
```

```bash
pnpm docker:seed-demo
```

```bash
curl http://localhost:9000/health
```

```bash
pnpm quality-gate:venv
pnpm quality-gate:install
pnpm quality-gate:doctor
pnpm quality-gate:test:smoke
```

```bash
docker compose exec medusa pnpm exec medusa user -e admin@example.com -p supersecret
```

`pnpm docker:seed-demo` does three things:

- runs the Medusa seed
- syncs the newly generated publishable API key into `.env` and `apps/storefront/.env.local`
- restarts the storefront with the current key

## README-Driven Verification

### HTTP checks

```bash
curl -I http://localhost:8000
curl -I http://localhost:8000/ru
curl -I http://localhost:8000/us
```

Expected behavior:

- `/` redirects to `/ru`
- `/ru` resolves to the RU market
- `/us` resolves to the US market

### Market contract checks

```bash
curl http://localhost:9000/store/regions \
  -H 'x-publishable-api-key: <publishable-key>'
```

Expected backend state:

- exactly two regions: `ru`, `us`
- default store currency: `rub`
- secondary store currency: `usd`
- product catalog count: `6`
- category count: `4`

### Localization checks

```bash
curl 'http://localhost:9000/store/products?handle=basis-heavy-tee&fields=title,description,material' \
  -H 'x-publishable-api-key: <publishable-key>' \
  -H 'x-medusa-locale: ru-RU'
```

Expected RU response:

- `title` is Russian
- `description` is Russian
- `material` is Russian

```bash
curl 'http://localhost:9000/store/product-categories?handle=hoodies&fields=name,description' \
  -H 'x-publishable-api-key: <publishable-key>' \
  -H 'x-medusa-locale: ru-RU'
```

Expected RU response:

- category `name` is `Худи`
- category `description` is Russian

### Shipping checks

RU cart should expose:

- `Курьер`
- `ПВЗ`
- `Самовывоз`

US cart should expose:

- `Standard Shipping`
- `Express Shipping`

## Why This Matters For QA

- Contract tests need a real SUT, not hand-waved mocks.
- State verification becomes possible once the backend and database are reproducible.
- Market routing is a first-class runtime contract, not a cosmetic i18n toggle.
- Region-driven pricing is testable independently from UI rendering.
- Future Python clients can target one canonical API surface at `http://localhost:9000`.

This is the backend analogue of testing a real frontend app with the correct store, router context, and seeded state instead of snapshotting empty shells.

## Package Manager Policy

- Entire repository: `pnpm`
- Reason: officially supported by Medusa, fast enough for monorepo work, and consistent across backend and storefront
- Deliberately not used: mixed `npm` / `bun` policy

## Docker Notes

- The runtime follows the Medusa Docker guide shape with `/server`, `start.sh`, health checks, and Docker-native service discovery.
- The infra baseline intentionally uses latest stable major services: `postgres:18-alpine` and `redis:8-alpine`.
- PostgreSQL 18 uses the recommended volume mount at `/var/lib/postgresql`.
- Host PostgreSQL is exposed on `5433`, not `5432`, to avoid collisions with an already running local database.
- `5173` is intentionally not published to the host anymore; the real admin entrypoint is `http://localhost:9000/app`.
- Storefront now defaults to `ru`, not `gb`.

## Screenshots To Capture For Portfolio

- `RU home`: hero with Russian copy and RUB pricing
- `US store`: category grid with USD pricing
- `Medusa admin`: regions `Russia` and `United States`
- `Checkout shipping`: RU methods vs US methods
- `Database verification`: SQL result for regions, currencies, and product count

## Next Modules

- Expand the Python `quality-gate` package from Store API smoke checks to richer contract coverage
- Add publishable-key edge cases and Store API negative scenarios
- Add DB verification helpers for richer cross-layer assertions
- Add Admin API and auth-heavy flows only after the course reaches those concepts
- Add Playwright UI checks against the localized storefront once the API layer is locked
