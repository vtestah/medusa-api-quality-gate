# Storefront E2E (Playwright)

UI end-to-end tests for the localized RU/US Medusa storefront, written in
Playwright with TypeScript. Specs run against a running storefront and exercise
the same flows per market through a Page Object Model.

## Layout

- `tests/`: the specs (`smoke`, `localization`, `cart`, `a11y`).
- `src/pages/` holds the Page Object Model (`base`, `home`, `store`, `cart`).
- `src/fixtures.ts`: per-market fixtures that expose the page objects and the
  active `market` profile.
- `src/market.ts` defines the RU/US market profiles (path prefix, locale, currency,
  shipping methods).
- `playwright.config.ts`: projects, reporters and base URL.

## Prerequisites

The tests need a reachable storefront. The base URL defaults to
`http://localhost:8000` and can be overridden with `STOREFRONT_BASE_URL`.

From the repository root the full runtime (PostgreSQL, Redis, Medusa, storefront)
can be started with `make up` and seeded with `make seed`.

## Install and run

```bash
cd e2e
pnpm install --ignore-workspace
pnpm exec playwright install chromium

pnpm test            # all specs, both markets
pnpm run test:ru     # RU project only
pnpm run test:us     # US project only
pnpm run test:smoke  # smoke spec
pnpm run test:a11y   # accessibility spec
```

From the repository root, `make e2e` runs the install, browser download and
test steps in one command (it expects the runtime to be up).

## Projects

Two projects are defined, `ru` and `us`. Both run the same specs; each sets a
`marketCode` that drives the localized URL prefix (`/ru`, `/us`), the expected
currency and the market-specific shipping options. Write a spec once and it runs
against both markets.

## Reports

The configured reporters are `list` (console) and `html`. After a run:

```bash
pnpm run report     # open the HTML report
```

The HTML report is written to `playwright-report/`; traces, screenshots and
video are captured on failure/retry per `playwright.config.ts`. In CI the report
is uploaded as a build artifact.

## Accessibility

`tests/a11y.spec.ts` uses `@axe-core/playwright` to scan the home and catalog
pages for WCAG 2.0/2.1 A and AA issues.

## Scaffolded specs

`tests/cart.spec.ts` and `tests/a11y.spec.ts` are marked `test.fixme`. The cart
flow needs the exact add-to-cart/variant selectors confirmed against the live
DOM, and the accessibility baseline needs to be reviewed against the running
storefront before the zero-violation expectation is enforced. Bring the runtime
up (`make up && make e2e`), confirm the selectors and baseline, then remove the
`fixme` marker.
