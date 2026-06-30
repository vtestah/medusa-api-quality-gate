"""Unit tests for cart total-integrity checking (no live runtime).

These build :class:`Cart` instances directly and exercise every branch of
:func:`assert_cart_totals_consistent`: the happy path, single-currency mismatch,
negative amounts, the line-items-vs-totals aggregation, and the defensive skips
when totals or per-line fields are absent.
"""

import pytest

from quality_gate.errors import ContractValidationError
from quality_gate.models.cart import Cart, LineItem, assert_cart_totals_consistent

pytestmark = pytest.mark.cart


def _line_item(
    suffix: str,
    *,
    quantity: int = 1,
    unit_price: int | None = None,
    subtotal: int | None = None,
    total: int | None = None,
) -> LineItem:
    """Build a line item with the supplied (optional) monetary fields."""
    return LineItem(
        id=f"li_{suffix}",
        variant_id=f"variant_{suffix}",
        quantity=quantity,
        unit_price=unit_price,
        subtotal=subtotal,
        total=total,
    )


def _cart(**overrides: object) -> Cart:
    """Build a USD cart, overriding any field via keyword."""
    payload: dict[str, object] = {
        "id": "cart_1",
        "region_id": "region_1",
        "currency_code": "usd",
    }
    payload.update(overrides)
    return Cart.model_validate(payload)


def test_returns_cart_when_fully_consistent() -> None:
    """A cart whose aggregates equal the line sums passes and is returned unchanged."""
    cart = _cart(
        items=[
            _line_item("a", quantity=2, unit_price=500, subtotal=1000, total=1100),
            _line_item("b", quantity=1, unit_price=300, subtotal=300, total=330),
        ],
        item_subtotal=1300,
        item_total=1430,
        tax_total=130,
        shipping_total=0,
        total=1430,
    )

    assert assert_cart_totals_consistent(cart) is cart


def test_line_item_currency_matching_cart_passes() -> None:
    """A line item carrying the same currency as the cart is accepted."""
    cart = _cart(
        items=[
            {"id": "li_a", "variant_id": "variant_a", "quantity": 1, "currency_code": "usd"},
        ],
    )

    assert assert_cart_totals_consistent(cart) is cart


def test_line_item_currency_mismatch_raises() -> None:
    """A line item whose currency differs from the cart is a contract violation."""
    cart = _cart(
        items=[
            {"id": "li_a", "variant_id": "variant_a", "quantity": 1, "currency_code": "eur"},
        ],
    )

    with pytest.raises(ContractValidationError, match="does not match cart currency"):
        assert_cart_totals_consistent(cart)


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    [
        ("unit_price", {"unit_price": -1}),
        ("subtotal", {"subtotal": -1}),
        ("total", {"total": -1}),
    ],
)
def test_negative_line_item_amount_raises(field_name: str, kwargs: dict[str, int]) -> None:
    """A negative line-item monetary field is rejected and named in the error."""
    cart = _cart(items=[_line_item("a", **kwargs)])

    with pytest.raises(ContractValidationError, match=field_name):
        assert_cart_totals_consistent(cart)


def test_negative_cart_total_raises() -> None:
    """A negative cart-level total (here ``tax_total``) is rejected."""
    cart = _cart(tax_total=-5)

    with pytest.raises(ContractValidationError, match="cart tax_total is negative"):
        assert_cart_totals_consistent(cart)


def test_item_subtotal_mismatch_raises() -> None:
    """``item_subtotal`` must equal the sum of line-item subtotals."""
    cart = _cart(
        items=[_line_item("a", subtotal=1000), _line_item("b", subtotal=300)],
        item_subtotal=9999,
    )

    with pytest.raises(ContractValidationError, match="item_subtotal"):
        assert_cart_totals_consistent(cart)


def test_item_total_mismatch_raises() -> None:
    """``item_total`` must equal the sum of line-item totals."""
    cart = _cart(
        items=[_line_item("a", total=1100), _line_item("b", total=330)],
        item_total=9999,
    )

    with pytest.raises(ContractValidationError, match="item_total"):
        assert_cart_totals_consistent(cart)


def test_partial_line_subtotals_skip_aggregation() -> None:
    """Aggregation is skipped (no false failure) when a line lacks ``subtotal``."""
    cart = _cart(
        items=[_line_item("a", subtotal=1000), _line_item("b")],
        item_subtotal=42,
    )

    assert assert_cart_totals_consistent(cart) is cart


def test_negative_discount_total_is_allowed() -> None:
    """``discount_total`` is excluded from the non-negativity check by design."""
    cart = _cart(discount_total=-500, total=500)

    assert assert_cart_totals_consistent(cart) is cart


def test_totals_without_items_are_ignored() -> None:
    """Cart-level totals on an empty cart never trigger the aggregation checks."""
    cart = _cart(item_subtotal=1000, item_total=1000)

    assert assert_cart_totals_consistent(cart) is cart
