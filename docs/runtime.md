# Runtime and infrastructure

Where things listen, why the ports look the way they do, and the package-manager
rule for the repo.

## URLs

- Storefront: `http://localhost:8000`
- RU storefront: `http://localhost:8000/ru`
- US storefront: `http://localhost:8000/us`
- Medusa API: `http://localhost:9000`
- Medusa health: `http://localhost:9000/health`
- Medusa admin: `http://localhost:9000/app`
- PostgreSQL (host): `localhost:5433`

## Docker notes

- The runtime follows the Medusa Docker guide shape: `/server`, `start.sh`, health checks, and Docker-native service discovery.
- Infra runs current stable majors: `postgres:18-alpine` and `redis:8-alpine`.
- PostgreSQL 18 mounts its data at `/var/lib/postgresql` (the recommended path).
- Host PostgreSQL is on `5433`, not `5432`, so it won't clash with a database you already run locally.
- Port `5173` is no longer published to the host; the admin lives at `http://localhost:9000/app`.
- The storefront defaults to `ru`, not `gb`.

## Package manager

The whole repo uses `pnpm`. Medusa supports it officially, it's quick for
monorepo work, and it keeps the backend and storefront on one tool. No mixed
`npm`/`bun` setup.
