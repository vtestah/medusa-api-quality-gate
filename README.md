# ecom-quality-gate

![Medusa](https://img.shields.io/badge/Medusa-v2.13.6-0A7BFF)
![pnpm](https://img.shields.io/badge/pnpm-10.33.0-F69220)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-local_runtime-2496ED)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791)
![Redis](https://img.shields.io/badge/Redis-8-DC382D)

Public portfolio repository for a Senior SDET track focused on API quality gates for a headless commerce stack. The runtime under test is Medusa.js backed by PostgreSQL and Redis. The Python test framework will live alongside the application runtime instead of being buried inside it.

## Architecture

```text
ecom-quality-gate/
├── package.json         # Root scripts for Docker runtime
├── pnpm-workspace.yaml  # Monorepo policy for all JS apps
├── apps/
│   └── medusa/          # System under test: Medusa backend
│   └── storefront/      # Next.js target UI for future browser automation
├── docker-compose.yml   # Local runtime: postgres + redis + medusa + storefront
└── README.md
```

## Medusa Runtime Module

This repository now boots a deterministic backend runtime for API testing:

- `postgres` stores commerce state.
- `redis` supports Medusa background/runtime flows.
- `medusa` runs as the backend under test on `http://localhost:9000`.
- `storefront` runs as the customer-facing Next.js target on `http://localhost:8000`.
- `pnpm` is the single JS package manager policy for the repository.
- The Docker layout follows the Medusa guide shape: `start.sh`, `/server`, internal Admin HMR port `5173`, and PostgreSQL SSL explicitly disabled for local Docker.
- The infra baseline intentionally uses latest stable major services: `postgres:18-alpine` and `redis:8-alpine`.

This is the backend analogue of keeping a frontend app behind a stable dev server contract: the Python layer will test a real system, not mocked endpoints.

### Run the stack

```bash
pnpm docker:up
pnpm docker:logs
```

```bash
pnpm docker:logs:storefront
```

### Validate the backend health

```bash
curl http://localhost:9000/health
```

### Seed demo data when needed

```bash
docker compose exec medusa pnpm seed
```

### Create an admin user

```bash
docker compose exec medusa pnpm medusa user -e admin@example.com -p supersecret
```

### Local backend workflow

```bash
cd apps/medusa
pnpm install
pnpm dev
```

### Local storefront workflow

```bash
cd apps/storefront
pnpm dev
```

## Why This Matters For QA

- Contract tests need a real SUT, not hand-waved mocks.
- State verification becomes possible once the backend and database are reproducible.
- Future Python clients can target one canonical base URL: `http://localhost:9000`.
- The Admin app is reachable in Docker without local hacks because Vite HMR is configured for container networking.
- Future browser tests get a real UI target at `http://localhost:8000`, not a mock shell.

## Package Manager Policy

- Entire repository: `pnpm`.
- Reason: it is officially supported by Medusa, fast enough for monorepo work, and keeps backend and future storefront on one package manager.
- Deliberately not used: mixed `npm` / `bun` policy, because it weakens onboarding and portfolio consistency.

## Docker Notes

- The upstream Medusa guide still shows `postgres:15-alpine` and `redis:7-alpine`; this repository keeps the guide's structure but upgrades the service majors to `18` and `8`.
- PostgreSQL 18 changed the recommended Docker data mount layout, so this repository mounts the volume at `/var/lib/postgresql` instead of `/var/lib/postgresql/data`.
- Root `package.json` owns Docker scripts because `docker-compose.yml` lives at repository root, not inside `apps/medusa`.
- `5173` is intentionally not published to the host anymore; the user-facing admin entrypoint is `http://localhost:9000/app`.
- The storefront service uses a separate Dockerfile and a cached `node_modules` volume so `pnpm` stays the single package manager across backend and UI.

## Storefront Module

- Source: official `nextjs-starter-medusa`, normalized to the repo's `pnpm` workspace policy.
- Runtime contract:
  `MEDUSA_BACKEND_URL=http://localhost:9000`
  `NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY=<seeded key>`
  `NEXT_PUBLIC_DEFAULT_REGION=gb`
- The backend seed script creates the publishable API key and demo catalog needed by the storefront.
- The first storefront request intentionally redirects to the region path, so `http://localhost:8000` lands on `http://localhost:8000/gb`.

## Next Modules

- Python `quality-gate` package with `clients`, `models`, `fixtures`, and `tests`.
- Pydantic v2 contract validation for Medusa Store and Admin APIs.
- DB verification helpers for cross-layer assertions.
