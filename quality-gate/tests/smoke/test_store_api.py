"""Smoke tests for the Medusa Store API."""

import pytest
import requests

from quality_gate.clients import StoreProductsClient, StoreRegionsClient
from quality_gate.config import Settings


@pytest.mark.smoke
@pytest.mark.contract
def test_store_regions_return_ru_and_us_markets(
    runtime_ready: None,
    api_session: requests.Session,
    settings: Settings,
) -> None:
    """The seeded demo should expose exactly the RU and US markets."""

    client = StoreRegionsClient(api_session, settings)
    payload = client.list_regions()

    assert len(payload.regions) == 2

    country_codes = {
        country.iso_2
        for region in payload.regions
        for country in region.countries
        if country.iso_2
    }

    assert country_codes == {"ru", "us"}


@pytest.mark.smoke
@pytest.mark.contract
def test_store_products_can_be_filtered_by_demo_handle(
    runtime_ready: None,
    api_session: requests.Session,
    settings: Settings,
) -> None:
    """The seeded demo product should be retrievable by handle."""

    client = StoreProductsClient(api_session, settings)
    payload = client.list_products(
        handle=settings.demo_product_handle,
        fields="title,description,handle,material",
    )

    assert payload.products
    assert payload.count is None or payload.count >= 1
    assert payload.products[0].handle == settings.demo_product_handle
