"""Negative input-validation integration tests for the Medusa Store API.

A single file grouped by risk type (negative input validation) per Req 2.8 — no
ad-hoc ``sanity``/``preflight`` directories. Every test runs against the live
Medusa runtime and is guarded by ``runtime_ready`` so it skips cleanly when the
runtime is down. All response/error bodies are parsed through Pydantic models
(``StoreApiError``, ``ProductsResponse``) rather than raw dict access (Req 7.1),
and error responses are validated without suppression.

Covers Req 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8.
"""

from typing import Any

import pytest
import requests

from quality_gate.clients import (
    StoreCartClient,
    StoreProductsClient,
    StoreRegionsClient,
)
from quality_gate.config import Settings
from quality_gate.models.errors import StoreApiError
from quality_gate.models.products import ProductsResponse

# Status codes accepted for unauthenticated / wrong-key Store API requests.
_AUTH_REJECT_STATUS_CODES = {400, 401}


def _store_url(settings: Settings, path: str) -> str:
    """Build an absolute Store API URL from ``settings.medusa_base_url``."""

    return f"{settings.medusa_base_url.rstrip('/')}/{path.lstrip('/')}"


@pytest.mark.contract
def test_missing_publishable_key_is_rejected(
    runtime_ready: None,
    api_session: requests.Session,
    settings: Settings,
) -> None:
    """GET /store/products without the publishable key → status in {400, 401} (Req 2.1).

    The shared ``api_session`` carries only an ``Accept`` header, so issuing the
    request without ``settings.store_headers`` guarantees the
    ``x-publishable-api-key`` header is absent.
    """

    response = api_session.get(
        _store_url(settings, "/store/products"),
        timeout=settings.request_timeout_seconds,
    )

    assert response.status_code in _AUTH_REJECT_STATUS_CODES, (
        f"Expected status in {_AUTH_REJECT_STATUS_CODES}, "
        f"but actual is {response.status_code}"
    )


@pytest.mark.contract
def test_wrong_publishable_key_is_rejected_and_body_parses(
    runtime_ready: None,
    api_session: requests.Session,
    settings: Settings,
) -> None:
    """Wrong publishable key → status in {400, 401} and error body parses (Req 2.2).

    The error body is validated through ``StoreApiError`` without suppression,
    confirming it is a contract-compatible JSON object.
    """

    response = api_session.get(
        _store_url(settings, "/store/products"),
        headers={"x-publishable-api-key": "pk_wrong"},
        timeout=settings.request_timeout_seconds,
    )

    assert response.status_code in _AUTH_REJECT_STATUS_CODES, (
        f"Expected status in {_AUTH_REJECT_STATUS_CODES}, "
        f"but actual is {response.status_code}"
    )

    error = StoreApiError.model_validate(response.json())
    assert isinstance(error, StoreApiError)


@pytest.mark.contract
def test_broken_json_cart_payload_returns_400(
    runtime_ready: None,
    api_session: requests.Session,
    settings: Settings,
) -> None:
    """Syntactically invalid JSON cart payload → 400, error body parses (Req 2.4).

    The raw, malformed body is sent via the session directly (the client always
    serializes valid JSON), so this exercises the server's JSON parser.
    """

    headers: dict[str, str] = {
        **settings.store_headers,
        "Content-Type": "application/json",
    }
    response = api_session.post(
        _store_url(settings, "/store/carts"),
        data="{not json",
        headers=headers,
        timeout=settings.request_timeout_seconds,
    )

    assert response.status_code == 400, (
        f"Expected status 400, but actual is {response.status_code}"
    )

    error = StoreApiError.model_validate(response.json())
    assert isinstance(error, StoreApiError)


@pytest.mark.contract
def test_incomplete_cart_payload_returns_400(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
) -> None:
    """Valid JSON but missing required fields → 400, error body parses (Req 2.5).

    Sends an empty JSON object via the low-level ``create_cart_response`` so the
    body bypasses pre-flight validation and reaches the Store API.
    """

    response = store_cart_client.create_cart_response(region_id="", payload={})

    assert response.status_code == 400, (
        f"Expected status 400, but actual is {response.status_code}"
    )

    error = StoreApiError.model_validate(response.json())
    assert isinstance(error, StoreApiError)


@pytest.mark.contract
def test_zero_quantity_line_item_returns_400(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    store_regions_client: StoreRegionsClient,
    demo_variant_id: str,
) -> None:
    """Line item with ``quantity`` of 0 → 400 via the Store API (Req 2.7).

    ``add_line_item_response`` is used (not ``add_line_item``) because the latter
    rejects ``quantity < 1`` in pre-flight; here we want the server to validate
    the boundary value. A cart is created first with a live region id.
    """

    regions = store_regions_client.list_regions().regions
    if not regions:
        pytest.skip("No regions seeded in the live runtime")

    cart = store_cart_client.create_cart(region_id=regions[0].id)

    response = store_cart_client.add_line_item_response(
        cart_id=cart.id,
        variant_id=demo_variant_id,
        quantity=0,
    )

    assert response.status_code == 400, (
        f"Expected status 400, but actual is {response.status_code}"
    )


@pytest.mark.contract
def test_nonexistent_handle_returns_empty_product_list(
    runtime_ready: None,
    store_products_client: StoreProductsClient,
) -> None:
    """Nonexistent ``handle`` → 200 with an empty ``products`` list (Req 2.3)."""

    response = store_products_client.list_products(handle="does-not-exist-xyz")

    assert isinstance(response, ProductsResponse)
    assert len(response.products) == 0, (
        f"Expected 0 products, but got {len(response.products)}"
    )


@pytest.mark.contract
def test_wrong_locale_does_not_return_5xx(
    runtime_ready: None,
    api_session: requests.Session,
    settings: Settings,
) -> None:
    """Invalid ``x-medusa-locale`` → status not in 5xx, body parses (Req 2.6).

    A direct session GET captures the raw status for the fallback-behavior
    contract. A 2xx body is validated as ``ProductsResponse``; any non-2xx body
    is validated as ``StoreApiError``. Both paths assert via Pydantic models.
    """

    headers: dict[str, str] = {
        **settings.store_headers,
        "x-medusa-locale": "zz-ZZ",
    }
    response = api_session.get(
        _store_url(settings, "/store/products"),
        params={"handle": settings.demo_product_handle},
        headers=headers,
        timeout=settings.request_timeout_seconds,
    )

    assert response.status_code < 500, (
        f"Expected a non-5xx status, but actual is {response.status_code}"
    )

    body: Any = response.json()
    if 200 <= response.status_code <= 299:
        parsed = ProductsResponse.model_validate(body)
        assert isinstance(parsed, ProductsResponse)
    else:
        error = StoreApiError.model_validate(body)
        assert isinstance(error, StoreApiError)
