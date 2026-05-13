"""Localization tests for RU Store API responses."""

import re

import pytest

from quality_gate.clients import StoreCategoriesClient, StoreProductsClient
from quality_gate.config import Settings

CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")


def contains_cyrillic(value: str | None) -> bool:
    """Return True when the string contains at least one Cyrillic character."""

    return bool(value and CYRILLIC_RE.search(value))


@pytest.mark.localization
@pytest.mark.contract
def test_store_products_return_russian_copy_for_ru_locale(
    runtime_ready: None,
    store_products_client: StoreProductsClient,
    settings: Settings,
) -> None:
    """Localized product fields should be returned in Russian for ru-RU."""

    payload = store_products_client.list_products(
        handle=settings.demo_product_handle,
        locale=settings.default_locale,
        fields="title,description,handle,material",
    )

    assert payload.products

    product = payload.products[0]
    assert product.handle == settings.demo_product_handle
    assert contains_cyrillic(product.title)
    assert contains_cyrillic(product.description)
    assert contains_cyrillic(product.material)


@pytest.mark.localization
@pytest.mark.contract
def test_store_categories_return_russian_category_name_for_ru_locale(
    runtime_ready: None,
    store_categories_client: StoreCategoriesClient,
    settings: Settings,
) -> None:
    """Localized category fields should be returned in Russian for ru-RU."""

    payload = store_categories_client.list_categories(
        handle=settings.demo_category_handle,
        locale=settings.default_locale,
        fields="name,description,handle",
    )

    assert payload.product_categories

    category = payload.product_categories[0]
    assert category.handle == settings.demo_category_handle
    assert category.name == "Худи"
    assert contains_cyrillic(category.description)
