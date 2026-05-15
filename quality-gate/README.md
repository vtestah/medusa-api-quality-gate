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

По умолчанию пакет ориентирован на локальный Docker runtime из этого репозитория:

- Medusa API: `http://localhost:9000`
- PostgreSQL: `postgresql://postgres:postgres@localhost:5433/medusa`
- Locale: `ru-RU`
- Demo product: `basis-heavy-tee`
- Demo category: `hoodies`
