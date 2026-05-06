# quality-gate

Python-пакет для API automation вокруг локального `Medusa` runtime.

## Что внутри

- `requests.Session` как транспорт
- `Pydantic v2` для контрактной валидации
- `pytest` для smoke, contract, localization и DB checks
- `psycopg` для PostgreSQL state verification

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
