"""Shared pytest fixtures for the Medusa quality gate."""

import pytest
import requests

from quality_gate.clients import (
    HealthClient,
    StoreCategoriesClient,
    StoreProductsClient,
    StoreRegionsClient,
)
from quality_gate.config import Settings
from quality_gate.db import PostgresDb


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Centralized runtime settings."""

    return Settings()


@pytest.fixture(scope="session")
def api_session() -> requests.Session:
    """Shared HTTP session for all API clients."""

    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="session")
def store_headers(settings: Settings) -> dict[str, str]:
    """Headers for Medusa Store API requests."""

    return settings.store_headers


@pytest.fixture(scope="module")
def health_client(
    api_session: requests.Session,
    settings: Settings,
) -> HealthClient:
    """Reusable health client for module-level tests."""

    return HealthClient(api_session, settings)


@pytest.fixture(scope="module")
def store_regions_client(
    api_session: requests.Session,
    settings: Settings,
) -> StoreRegionsClient:
    """Reusable store regions client for module-level tests."""

    return StoreRegionsClient(api_session, settings)


@pytest.fixture(scope="module")
def store_products_client(
    api_session: requests.Session,
    settings: Settings,
) -> StoreProductsClient:
    """Reusable store products client for module-level tests."""

    return StoreProductsClient(api_session, settings)


@pytest.fixture(scope="module")
def store_categories_client(
    api_session: requests.Session,
    settings: Settings,
) -> StoreCategoriesClient:
    """Reusable store categories client for module-level tests."""

    return StoreCategoriesClient(api_session, settings)


@pytest.fixture(scope="session")
def runtime_ready(
    api_session: requests.Session,
    settings: Settings,
) -> None:
    """Skip runtime-bound tests when Medusa is unavailable."""

    health_url = f"{settings.medusa_base_url.rstrip('/')}/health"
    try:
        response = api_session.get(
            health_url,
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        pytest.skip(f"Local Medusa runtime unavailable: {exc}")


@pytest.fixture(scope="session")
def db_connection(settings: Settings) -> PostgresDb:
    """Connected PostgreSQL helper for state verification."""

    connection = PostgresDb(settings.db_url)
    try:
        connection.connect()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Local PostgreSQL unavailable: {exc}")

    yield connection
    connection.close()
