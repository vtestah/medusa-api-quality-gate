"""Shared pytest fixtures for the Medusa quality gate."""

from collections.abc import Iterator

import pytest
import requests

from quality_gate.clients import (
    HealthClient,
    StoreAuthClient,
    StoreCartClient,
    StoreCategoriesClient,
    StoreCustomersClient,
    StoreProductsClient,
    StoreRegionsClient,
    StoreShippingClient,
)
from quality_gate.config import Settings
from quality_gate.db import PostgresDb
from quality_gate.db.reconciler import DbReconciler
from quality_gate.models.cart import Cart


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
def store_auth_client(
    api_session: requests.Session,
    settings: Settings,
) -> StoreAuthClient:
    """Reusable storefront auth client for module-level tests."""

    return StoreAuthClient(api_session, settings)


@pytest.fixture(scope="module")
def store_regions_client(
    api_session: requests.Session,
    settings: Settings,
) -> StoreRegionsClient:
    """Reusable store regions client for module-level tests."""

    return StoreRegionsClient(api_session, settings)


@pytest.fixture(scope="module")
def store_customers_client(
    api_session: requests.Session,
    settings: Settings,
) -> StoreCustomersClient:
    """Reusable store customer client for module-level tests."""

    return StoreCustomersClient(api_session, settings)


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


@pytest.fixture(scope="module")
def store_cart_client(
    api_session: requests.Session,
    settings: Settings,
) -> StoreCartClient:
    """Reusable store cart client for module-level tests."""

    return StoreCartClient(api_session, settings)


@pytest.fixture(scope="module")
def store_shipping_client(
    api_session: requests.Session,
    settings: Settings,
) -> StoreShippingClient:
    """Reusable store shipping client for module-level tests."""

    return StoreShippingClient(api_session, settings)


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


def _resolve_region_id(
    store_regions_client: StoreRegionsClient,
    settings: Settings,
    market_code: str,
) -> str:
    """Resolve a Medusa region id for a market by matching its currency code.

    Looks up the expected currency for ``market_code`` from ``settings.markets``
    and returns the id of the first region whose ``currency_code`` matches. Skips
    the test (rather than failing) when no matching region is seeded.
    """

    expected_currency = settings.markets[market_code].currency_code
    regions = store_regions_client.list_regions().regions
    for region in regions:
        if region.currency_code == expected_currency:
            return region.id
    pytest.skip(
        f"No region found for market {market_code!r} "
        f"(currency {expected_currency!r}) in the live runtime"
    )


@pytest.fixture
def demo_variant_id(
    store_products_client: StoreProductsClient,
    settings: Settings,
    runtime_ready: None,
) -> str:
    """Resolve a variant id from the Demo_Product via the Store Products client.

    Fetches the demo product by its configured handle and returns the first
    variant id, so tests never hard-code identifiers (Req 4.5). Skips when the
    product or a variant is not present in the live runtime.
    """

    response = store_products_client.list_products(handle=settings.demo_product_handle)
    if not response.products:
        pytest.skip(
            f"Demo product {settings.demo_product_handle!r} not found in the runtime"
        )
    variants = response.products[0].variants
    if not variants:
        pytest.skip(
            f"Demo product {settings.demo_product_handle!r} has no variants"
        )
    return variants[0].id


@pytest.fixture
def ru_cart(
    store_cart_client: StoreCartClient,
    store_regions_client: StoreRegionsClient,
    settings: Settings,
    runtime_ready: None,
) -> Iterator[Cart]:
    """Provide a freshly created RU-market cart with yield-teardown (Req 3.8, 7.6)."""

    region_id = _resolve_region_id(store_regions_client, settings, "ru")
    cart = store_cart_client.create_cart(region_id=region_id)
    try:
        yield cart
    finally:
        # Best-effort cleanup: the runtime is read-only seeded data and the Store
        # API exposes no cart-delete endpoint, so there is no resource to release
        # here. The try/finally structure is kept so teardown runs even when a
        # test raises (Req 7.6).
        pass


@pytest.fixture
def us_cart(
    store_cart_client: StoreCartClient,
    store_regions_client: StoreRegionsClient,
    settings: Settings,
    runtime_ready: None,
) -> Iterator[Cart]:
    """Provide a freshly created US-market cart with yield-teardown (Req 3.8, 7.6)."""

    region_id = _resolve_region_id(store_regions_client, settings, "us")
    cart = store_cart_client.create_cart(region_id=region_id)
    try:
        yield cart
    finally:
        # Best-effort cleanup: see ``ru_cart`` for rationale. The try/finally is
        # retained so teardown runs even on test failure (Req 7.6).
        pass


@pytest.fixture
def db_reconciler(db_connection: PostgresDb) -> DbReconciler:
    """Read-only cross-layer reconciler over the guarded PostgreSQL connection.

    Built on top of ``db_connection``, which already skips DB-bound tests when
    PostgreSQL is unavailable (Req 6.6).
    """

    return DbReconciler(db_connection)
