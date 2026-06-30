# k6 performance checks

Small [k6](https://k6.io/) scripts that exercise the read-only Medusa Store API
endpoints the storefront depends on (`/store/regions`, `/store/products`) plus
`/health`. They are a lightweight performance baseline, not a full load-testing
rig.

- `smoke.js`: 1 VU, a handful of iterations. It confirms the API answers correctly
  and quickly, and fails on any error (`http_req_failed: rate==0`).
- `load.js` ramps to 10 VUs and holds, with error-rate and p95-latency
  thresholds (including tighter per-endpoint budgets).

## Prerequisites

1. A running Medusa runtime with the Store API on `http://localhost:9000`. From the
   repo root:

   ```bash
   make up     # postgres + redis + medusa + storefront
   make seed   # seed demo data and sync the publishable key
   ```

2. [k6 installed](https://grafana.com/docs/k6/latest/set-up/install-k6/) locally
   (`k6 version` to confirm).

3. A Store API publishable key. The `/store/*` endpoints require the
   `x-publishable-api-key` header. After seeding, read the key from PostgreSQL the
   same way CI does:

   ```bash
   export PUBLISHABLE_KEY="$(docker compose exec -T postgres \
     psql -U postgres -d medusa -At \
     -c "select token from api_key where type = 'publishable' limit 1;")"
   ```

## Run

```bash
# Smoke (fast, must be clean)
k6 run -e PUBLISHABLE_KEY="$PUBLISHABLE_KEY" k6/smoke.js

# Load (ramped)
k6 run -e PUBLISHABLE_KEY="$PUBLISHABLE_KEY" k6/load.js
```

Point the scripts at a different host with `BASE_URL`:

```bash
k6 run -e BASE_URL=http://localhost:9000 -e PUBLISHABLE_KEY="$PUBLISHABLE_KEY" k6/smoke.js
```

## Configuration

| Env var           | Default                 | Purpose                         |
| ----------------- | ----------------------- | ------------------------------- |
| `BASE_URL`        | `http://localhost:9000` | Medusa base URL                 |
| `PUBLISHABLE_KEY` | _(empty)_               | Sent as `x-publishable-api-key` |

`/health` needs no key; without a valid `PUBLISHABLE_KEY` the `/store/*` requests
return 4xx and the thresholds fail.

## Thresholds

Both scripts exit non-zero when their thresholds are breached, so they can be wired
into a pipeline later:

- `smoke.js`: `http_req_failed = 0`, `http_req_duration p95 < 500ms`.
- `load.js`: `http_req_failed < 1%`, `http_req_duration p95 < 800ms`, plus
  per-endpoint p95 budgets.

The VU counts, stages, and latency budgets are starting points. Tune them to the
host under test.
