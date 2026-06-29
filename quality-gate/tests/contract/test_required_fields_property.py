"""Property-based checks for the strict required-field contract of Store models.

# Feature: test-coverage-expansion, Property 1: Контракт обязательных полей строго проверяется
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from quality_gate.models.products import StoreProduct
from quality_gate.models.regions import StoreRegion

pytestmark = pytest.mark.contract


# Непустые строки: после strip() гарантированно содержат хотя бы один символ,
# чтобы проходить NonEmptyStr (StringConstraints(min_length=1, strip_whitespace=True)).
_non_empty_text = (
    st.text(min_size=1, max_size=24).map(str.strip).filter(lambda value: len(value) > 0)
)

# currency_code строго rub/usd (CurrencyCode = Literal["rub", "usd"]).
_currency_code = st.sampled_from(["rub", "usd"])

# Скалярные обязательные поля (нет значения по умолчанию): их отсутствие → ValidationError.
_REGION_REQUIRED_SCALARS = ("id", "name", "currency_code")
_PRODUCT_REQUIRED_SCALARS = ("id", "handle", "title")


@st.composite
def _region_payloads(draw: st.DrawFn) -> dict[str, object]:
    """Сгенерировать полностью валидный payload региона."""
    countries = draw(
        st.lists(
            st.fixed_dictionaries({"iso_2": _non_empty_text}),
            max_size=3,
        )
    )
    return {
        "id": draw(_non_empty_text),
        "name": draw(_non_empty_text),
        "currency_code": draw(_currency_code),
        "countries": countries,
    }


@st.composite
def _product_payloads(draw: st.DrawFn) -> dict[str, object]:
    """Сгенерировать полностью валидный payload продукта."""
    variants = draw(
        st.lists(
            st.fixed_dictionaries({"id": _non_empty_text}),
            max_size=3,
        )
    )
    return {
        "id": draw(_non_empty_text),
        "handle": draw(_non_empty_text),
        "title": draw(_non_empty_text),
        "variants": variants,
    }


# Feature: test-coverage-expansion, Property 1: Контракт обязательных полей строго проверяется
@settings(max_examples=100)
@given(payload=_region_payloads(), missing_field=st.sampled_from(_REGION_REQUIRED_SCALARS))
def test_region_rejects_missing_required_scalar(
    payload: dict[str, object], missing_field: str
) -> None:
    """Удаление любого обязательного скалярного поля региона → ValidationError."""
    broken = dict(payload)
    del broken[missing_field]

    with pytest.raises(ValidationError):
        StoreRegion.model_validate(broken)


# Feature: test-coverage-expansion, Property 1: Контракт обязательных полей строго проверяется
@settings(max_examples=100)
@given(payload=_product_payloads(), missing_field=st.sampled_from(_PRODUCT_REQUIRED_SCALARS))
def test_product_rejects_missing_required_scalar(
    payload: dict[str, object], missing_field: str
) -> None:
    """Удаление любого обязательного скалярного поля продукта → ValidationError."""
    broken = dict(payload)
    del broken[missing_field]

    with pytest.raises(ValidationError):
        StoreProduct.model_validate(broken)


# Feature: test-coverage-expansion, Property 1: Контракт обязательных полей строго проверяется
@settings(max_examples=100)
@given(payload=_region_payloads())
def test_valid_region_payload_parses(payload: dict[str, object]) -> None:
    """Полностью валидный payload региона успешно разбирается."""
    region = StoreRegion.model_validate(payload)

    assert region.id == payload["id"]
    assert region.name == payload["name"]
    assert region.currency_code == payload["currency_code"]


# Feature: test-coverage-expansion, Property 1: Контракт обязательных полей строго проверяется
@settings(max_examples=100)
@given(payload=_product_payloads())
def test_valid_product_payload_parses(payload: dict[str, object]) -> None:
    """Полностью валидный payload продукта успешно разбирается."""
    product = StoreProduct.model_validate(payload)

    assert product.id == payload["id"]
    assert product.handle == payload["handle"]
    assert product.title == payload["title"]


# Feature: test-coverage-expansion, Property 1: Контракт обязательных полей строго проверяется
@settings(max_examples=100)
@given(payload=_region_payloads())
def test_region_without_countries_defaults_to_empty_list(payload: dict[str, object]) -> None:
    """Отсутствующий `countries` региона → пустой список."""
    without_countries = dict(payload)
    del without_countries["countries"]

    region = StoreRegion.model_validate(without_countries)

    assert region.countries == []


# Feature: test-coverage-expansion, Property 1: Контракт обязательных полей строго проверяется
@settings(max_examples=100)
@given(payload=_product_payloads())
def test_product_without_variants_defaults_to_empty_list(payload: dict[str, object]) -> None:
    """Отсутствующий `variants` продукта → пустой список."""
    without_variants = dict(payload)
    del without_variants["variants"]

    product = StoreProduct.model_validate(without_variants)

    assert product.variants == []
