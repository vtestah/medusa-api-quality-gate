"""Property-based checks that the contract round-trip preserves validated fields.

# Feature: test-coverage-expansion, Property 2: Контрактный round-trip сохраняет провалидированные поля
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quality_gate.models.cart import Cart
from quality_gate.models.contract import assert_round_trip
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


@st.composite
def _regions(draw: st.DrawFn) -> StoreRegion:
    """Сконструировать валидный экземпляр StoreRegion."""
    countries = draw(
        st.lists(
            st.fixed_dictionaries({"iso_2": _non_empty_text}),
            max_size=3,
        )
    )
    return StoreRegion.model_validate(
        {
            "id": draw(_non_empty_text),
            "name": draw(_non_empty_text),
            "currency_code": draw(_currency_code),
            "countries": countries,
        }
    )


@st.composite
def _products(draw: st.DrawFn) -> StoreProduct:
    """Сконструировать валидный экземпляр StoreProduct."""
    variants = draw(
        st.lists(
            st.fixed_dictionaries({"id": _non_empty_text}),
            max_size=3,
        )
    )
    return StoreProduct.model_validate(
        {
            "id": draw(_non_empty_text),
            "handle": draw(_non_empty_text),
            "title": draw(_non_empty_text),
            "variants": variants,
        }
    )


@st.composite
def _carts(draw: st.DrawFn) -> Cart:
    """Сконструировать валидный экземпляр Cart с несколькими line items."""
    items = draw(
        st.lists(
            st.fixed_dictionaries(
                {
                    "id": _non_empty_text,
                    "variant_id": _non_empty_text,
                    "quantity": st.integers(min_value=1, max_value=1000),
                }
            ),
            max_size=3,
        )
    )
    return Cart.model_validate(
        {
            "id": draw(_non_empty_text),
            "region_id": draw(_non_empty_text),
            "currency_code": draw(_currency_code),
            "items": items,
        }
    )


# Feature: test-coverage-expansion, Property 2: Контрактный round-trip сохраняет провалидированные поля
@settings(max_examples=100)
@given(region=_regions())
def test_region_round_trip_preserves_fields(region: StoreRegion) -> None:
    """Round-trip региона сохраняет все провалидированные поля.

    Validates: Requirements 1.4, 1.8
    """
    reparsed = assert_round_trip(region)

    assert reparsed.model_dump() == region.model_dump()
    assert reparsed.id == region.id
    assert reparsed.name == region.name
    assert reparsed.currency_code == region.currency_code


# Feature: test-coverage-expansion, Property 2: Контрактный round-trip сохраняет провалидированные поля
@settings(max_examples=100)
@given(product=_products())
def test_product_round_trip_preserves_fields(product: StoreProduct) -> None:
    """Round-trip продукта сохраняет все провалидированные поля.

    Validates: Requirements 1.4, 1.8
    """
    reparsed = assert_round_trip(product)

    assert reparsed.model_dump() == product.model_dump()
    assert reparsed.id == product.id
    assert reparsed.handle == product.handle
    assert reparsed.title == product.title


# Feature: test-coverage-expansion, Property 2: Контрактный round-trip сохраняет провалидированные поля
@settings(max_examples=100)
@given(cart=_carts())
def test_cart_round_trip_preserves_fields(cart: Cart) -> None:
    """Round-trip корзины сохраняет все провалидированные поля.

    Validates: Requirements 1.4, 1.8
    """
    reparsed = assert_round_trip(cart)

    assert reparsed.model_dump() == cart.model_dump()
    assert reparsed.id == cart.id
    assert reparsed.region_id == cart.region_id
    assert reparsed.currency_code == cart.currency_code
