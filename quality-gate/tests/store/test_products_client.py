"""Unit tests for the Store products client using a mocked HTTP session.

These run without a live runtime: they pin the request shape (endpoint, query
params for pagination/filtering, locale header) and the response parsing,
complementing the live data-driven checks in ``test_products_pagination.py``.
"""

from typing import cast
from unittest.mock import MagicMock

import pytest
from requests import Session

from quality_gate.clients import StoreProductsClient
from quality_gate.config import Settings

pytestmark = pytest.mark.contract


def _client_with_products(json_body: object) -> tuple[StoreProductsClient, MagicMock]:
    """Build a StoreProductsClient backed by a mocked session returning one response."""
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = json_body
    session.get.return_value = response
    client = StoreProductsClient(cast("Session", session), Settings())
    return client, session


def test_list_products_without_params_hits_endpoint_and_parses() -> None:
    client, session = _client_with_products(
        {"products": [{"id": "prod_1", "handle": "tee", "title": "Heavy Tee"}], "count": 1}
    )

    listing = client.list_products()

    assert listing.count == 1
    assert listing.products[0].id == "prod_1"
    url = session.get.call_args.args[0]
    assert url.endswith("/store/products")
    assert session.get.call_args.kwargs["params"] == {}


def test_list_products_forwards_pagination_and_filter_params() -> None:
    client, session = _client_with_products({"products": [], "count": 0})

    client.list_products(handle="tee", limit=2, offset=4, fields="title")

    assert session.get.call_args.kwargs["params"] == {
        "handle": "tee",
        "limit": 2,
        "offset": 4,
        "fields": "title",
    }


def test_list_products_sets_locale_header_and_keeps_publishable_key() -> None:
    client, session = _client_with_products({"products": [], "count": 0})

    client.list_products(locale="ru-RU")

    headers = session.get.call_args.kwargs["headers"]
    assert headers["x-medusa-locale"] == "ru-RU"
    assert "x-publishable-api-key" in headers


def test_list_products_merges_extra_params() -> None:
    client, session = _client_with_products({"products": [], "count": 0})

    client.list_products(extra_params={"category_id": "cat_1"})

    assert session.get.call_args.kwargs["params"]["category_id"] == "cat_1"
