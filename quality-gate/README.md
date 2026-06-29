# quality-gate

Python-пакет для API automation вокруг локального `Medusa` runtime.

## Что внутри

- `requests.Session` как транспорт
- `Pydantic v2` для контрактной валидации
- `pytest` для smoke, contract, localization и DB checks
- `pytest-html` для локального one-file HTML отчета
- `psycopg` для PostgreSQL state verification

## Структура проекта

```text
quality-gate/
├── pyproject.toml          # package metadata, dependencies, pytest config
├── README.md
├── src/
│   └── quality_gate/       # reusable framework code imported by tests
│       ├── clients/        # HTTP clients for Health and Medusa Store API
│       ├── models/         # Pydantic response contracts
│       ├── db/             # read-only PostgreSQL helpers
│       ├── config.py       # env-based Settings
│       ├── bootstrap.py    # local venv/bootstrap diagnostics
│       └── doctor.py       # active Python/runtime snapshot
└── tests/
    ├── smoke/              # fast runtime and bootstrap checks
    ├── localization/       # x-medusa-locale contract checks
    └── db/                 # PostgreSQL state verification
```

Framework code belongs in `src/quality_gate/`; executable checks belong in `tests/`.
One-off learning snippets belong in `notes/lessons/`, not in production test code.

Test directories are named by stable suite/risk type. Current directories are `smoke/`, `localization/`, and `db/`; a category like `contract` can start as a marker and become `contract/` only when it grows into a dedicated suite. Do not create folders for situational labels such as `sanity`, `preflight`, or course IDs; capture those in test names, docstrings, logs, notes, or `-k` filters.

## HTTP client conventions

`StoreApiClient` injects the Medusa Store API `x-publishable-api-key` header from `Settings.store_headers`. Do not add WooCommerce-style OAuth helpers or hardcoded secrets for Store API checks.

Keep transport details in `BaseApiClient`: URL joining, shared session calls, timeout, optional expected status checks, and JSON payload submission. Service clients should pass endpoint paths and payloads into this layer instead of calling `requests.post(...)` directly.

Read the Medusa base URL from `Settings`, not from hardcoded strings in tests. Send JSON payloads through `post(..., json=payload)`, not `data=payload` or manual `json.dumps(...)`.

For endpoints where the expected status is part of the contract, pass `expected_status_code` into the client call:

```python
response = store_auth_client.request_customer_registration_token(
    email="qa-preflight@example.com",
    expected_status_code=401,
)
```

The helper keeps the original `requests.Response` available for JSON parsing and Pydantic validation, but fails fast with expected/actual status details when the API returns the wrong code.

## Быстрый старт

```bash
python3 -m venv .venv
```

```bash
PYTHONPATH=quality-gate/src python3 -m quality_gate.bootstrap
```

```bash
.venv/bin/python -m quality_gate.bootstrap
```

```bash
.venv/bin/python -m pip install -e './quality-gate[dev]'
```

```bash
.venv/bin/python -m quality_gate.doctor
```

```bash
.venv/bin/python -m pytest quality-gate/tests/smoke -q
```

```bash
mkdir -p quality-gate/reports
.venv/bin/python -m pytest quality-gate/tests/smoke \
  --html=quality-gate/reports/smoke-report.html \
  --self-contained-html \
  -q
```

```bash
.venv/bin/python -m pytest quality-gate/tests/localization -q
```

```bash
.venv/bin/python -m pytest quality-gate/tests --alluredir quality-gate/allure-results
```

## Выборочный запуск по маркерам

```bash
.venv/bin/python -m pytest --collect-only quality-gate/tests -m smoke -q
```

```bash
.venv/bin/python -m pytest --collect-only quality-gate/tests -m "smoke and contract" -q
```

```bash
.venv/bin/python -m pytest --collect-only quality-gate/tests -m "smoke or db" -q
```

```bash
.venv/bin/python -m pytest --collect-only quality-gate/tests -m "not db" -q
```

```bash
.venv/bin/python -m pytest --markers quality-gate/tests
```

```bash
.venv/bin/python -m pytest quality-gate/tests/smoke/test_customer_registration_contract.py -q
```

Для точечной проверки customer registration contract используйте путь к файлу или фильтр по имени теста. CLI-логи включены в `pyproject.toml`, поэтому сообщения `LOGGER.info(...)` видны без отдельного `--log-cli-level`.

В этом файле есть два сигнала:

- безопасный preflight: registration endpoint отклоняет payload без `password`;
- happy path response validation: Store API создает customer с уникальным email и возвращает `customer.email`, `customer.id`, пустой `first_name` и не возвращает password.

DB state verification для созданного customer держите в `tests/db/`, когда сценарий дорастет до PostgreSQL-проверки.

```bash
.venv/bin/python -m pytest quality-gate/tests/smoke/test_customer_credentials_factory.py -q
```

Фабрика `build_customer_credentials()` генерирует уникальный `email` и пароль для будущего customer registration happy path. Пароль не логируется; в тестах проверяется только форма данных и готовность к `model_dump()` payload.

```bash
.venv/bin/python -m pytest quality-gate/tests/smoke/test_http_client.py -q
```

Этот bootstrap-check фиксирует, что customer client собирает URL, headers, timeout и request body в одном контракте до живого Medusa runtime.

```bash
env | sort | grep '^QUALITY_GATE_'
```

```bash
.venv/bin/python -m pytest quality-gate/tests/smoke/test_settings.py -q
```

`test_settings.py` фиксирует, что `Settings` читает `QUALITY_GATE_*` переменные окружения, а без них остается совместимым с локальным Docker runtime.
Пустой `QUALITY_GATE_PUBLISHABLE_KEY` и base URL без `http://`/`https://` падают на этапе конфигурации, до HTTP-запроса.

## HTML отчет pytest

Локальный HTML отчет удобен для быстрой демонстрации результата smoke-прогона без чтения полного терминального лога.

```bash
cd ecom-quality-gate
pnpm quality-gate:install
pnpm quality-gate:test:html
```

Отчет создается как один файл:

```text
quality-gate/reports/smoke-report.html
```

Флаг `--self-contained-html` встраивает стили в сам отчет, поэтому файл проще отправить или прикрепить к CI artifact.

## Поддерживаемые переменные окружения

- `QUALITY_GATE_MEDUSA_BASE_URL`
- `QUALITY_GATE_PUBLISHABLE_KEY`
- `QUALITY_GATE_DB_URL`
- `QUALITY_GATE_DEFAULT_LOCALE`
- `QUALITY_GATE_DEFAULT_REGION_CODE`
- `QUALITY_GATE_DEMO_PRODUCT_HANDLE`
- `QUALITY_GATE_DEMO_CATEGORY_HANDLE`
- `QUALITY_GATE_REQUEST_TIMEOUT_SECONDS`

По умолчанию пакет ориентирован на локальный Docker runtime из этого репозитория:

- Medusa API: `http://localhost:9000`
- PostgreSQL: `postgresql://postgres:postgres@localhost:5433/medusa`
- Locale: `ru-RU`
- Demo product: `basis-heavy-tee`
- Demo category: `hoodies`
