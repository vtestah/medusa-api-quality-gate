# Localization and markets

`Basis` is a fashion-basics storefront with one catalog and two public markets.
Catalog handles stay in English on purpose; the display content is translated by
the Medusa Translation Module.

| Market | Path | Region | Currency | UI language | Shipping |
| --- | --- | --- | --- | --- | --- |
| Russia | `/ru` | `Russia` | `RUB` | Russian chrome | `Курьер`, `ПВЗ`, `Самовывоз` |
| United States | `/us` | `United States` | `USD` | English chrome | `Standard Shipping`, `Express Shipping` |

Keeping handles canonical buys two clean layers: stable English identifiers for
fixtures, URLs, and contracts, and localized product, category, and collection
content for `/ru` and `/us`.

## How the split works

Shell text (nav, hero, footer, account copy) goes through `next-intl`. Catalog
content (products, categories, collections, variants, shipping) is served by the
Medusa Translation Module.

```text
/ru -> region: Russia, currency: RUB, locale: ru-RU
/us -> region: United States, currency: USD, locale: en-US
```

So `region` drives pricing, shipping, and market behavior, while `next-intl`
owns the typed UI dictionaries for the storefront chrome.

Key files:

- `apps/storefront/src/i18n/messages/ru-RU.json`
- `apps/storefront/src/i18n/messages/en-US.json`
- `apps/storefront/src/i18n/request.ts`
- `apps/storefront/src/middleware.ts`

## What renders where

- `/ru` shows Russian nav, hero, footer, and account login copy; `/us` shows English.
- Metadata titles switch too: `Basis | Российский storefront demo` vs `Basis | US storefront demo`.
- `/ru/store` shows Russian product titles, category labels, collection titles, and descriptions.
- `/us/store` shows English catalog content and USD pricing.
