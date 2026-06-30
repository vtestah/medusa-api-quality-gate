# Manual checks

Quick curl checks for when the runtime is up (`make up && make seed`) and you
want to eyeball routing, localization, and shipping by hand. Swap
`<publishable-key>` for the key the seed step prints.

## HTTP routing

```bash
curl -I http://localhost:8000
curl -I http://localhost:8000/ru
curl -I http://localhost:8000/us
```

What you should see:

- `/` redirects to `/ru`
- `/ru` resolves to the RU market
- `/us` resolves to the US market

## Store contract

```bash
curl http://localhost:9000/store/regions \
  -H 'x-publishable-api-key: <publishable-key>'
```

Backend state after a clean seed:

- exactly two regions: `ru`, `us`
- default store currency `rub`, secondary `usd`
- 6 products, 4 categories

## Localization

```bash
curl 'http://localhost:9000/store/products?handle=basis-heavy-tee&fields=title,description,material' \
  -H 'x-publishable-api-key: <publishable-key>' \
  -H 'x-medusa-locale: ru-RU'
```

With `ru-RU`, the `title`, `description`, and `material` come back in Russian.

```bash
curl 'http://localhost:9000/store/product-categories?handle=hoodies&fields=name,description' \
  -H 'x-publishable-api-key: <publishable-key>' \
  -H 'x-medusa-locale: ru-RU'
```

The category `name` is `Худи` and its `description` is Russian.

## Shipping by market

An RU cart should offer `Курьер`, `ПВЗ`, and `Самовывоз`. A US cart should offer
`Standard Shipping` and `Express Shipping`.
