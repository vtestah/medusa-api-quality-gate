"""Data-driven pagination and filtering tests for GET /store/products.

These run against the live Store API and are guarded by ``runtime_ready`` so they
skip cleanly when the runtime is unavailable. They are parametrized over several
``limit``/``offset`` combinations and assert the documented pagination behaviour:
a page never exceeds its ``limit``, consecutive pages are disjoint, the total
``count`` is independent of page size, and a ``handle`` filter returns only
matching products. All assertions use the Pydantic ``ProductsResponse`` model,
never raw dict keys.
"""

import pytest

from quality_gate.clients import StoreProductsClient
from quality_gate.config import Settings
from quality_gate.models.products import ProductsResponse


@pytest.mark.contract
@pytest.mark.parametrize("limit", [1, 2, 5])
def test_products_listing_respects_limit(
    runtime_ready: None,
    store_products_client: StoreProductsClient,
    limit: int,
) -> None:
    """A listing returns at most ``limit`` products and echoes the applied limit."""

    response = store_products_client.list_products(limit=limit)

    assert isinstance(response, ProductsResponse)
    assert len(response.products) <= limit
    assert response.limit is None or response.limit == limit


@pytest.mark.contract
@pytest.mark.parametrize("offset", [0, 1])
def test_products_pages_do_not_overlap(
    runtime_ready: None,
    store_products_client: StoreProductsClient,
    offset: int,
) -> None:
    """Single-item pages at adjacent offsets never return the same product id."""

    first = store_products_client.list_products(limit=1, offset=offset)
    second = store_products_client.list_products(limit=1, offset=offset + 1)

    first_ids = {product.id for product in first.products}
    second_ids = {product.id for product in second.products}

    # Disjoint when both pages contain items; trivially true if a page is empty.
    assert first_ids.isdisjoint(second_ids)


@pytest.mark.contract
def test_products_total_count_is_stable_across_page_sizes(
    runtime_ready: None,
    store_products_client: StoreProductsClient,
) -> None:
    """The total ``count`` does not depend on the requested page size."""

    small_page = store_products_client.list_products(limit=1)
    large_page = store_products_client.list_products(limit=100)

    if small_page.count is not None and large_page.count is not None:
        assert small_page.count == large_page.count
    assert len(large_page.products) >= len(small_page.products)


@pytest.mark.contract
def test_products_filter_by_handle_returns_only_matching(
    runtime_ready: None,
    store_products_client: StoreProductsClient,
    settings: Settings,
) -> None:
    """Filtering by the demo handle returns only products with that handle."""

    response = store_products_client.list_products(handle=settings.demo_product_handle)

    assert response.products, (
        f"expected at least one product for handle {settings.demo_product_handle!r}"
    )
    assert all(
        product.handle == settings.demo_product_handle for product in response.products
    )
