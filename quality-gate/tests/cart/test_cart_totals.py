"""Cart total-integrity integration tests against the live runtime.

These run against the live Store API and are guarded by ``runtime_ready`` (via the
``ru_cart`` and ``demo_variant_id`` fixtures) so they skip cleanly when the runtime
is unavailable. They add a line item, then assert the returned cart's totals are
internally consistent (line items vs totals, single currency, non-negative
amounts) using :func:`assert_cart_totals_consistent`. The check is defensive, so it
holds whether or not the Store API includes every computed total on the response.
All assertions use the Pydantic models, never raw dict keys.
"""

import pytest

from quality_gate.clients import StoreCartClient
from quality_gate.models.cart import Cart, assert_cart_totals_consistent


@pytest.mark.cart
def test_cart_with_line_item_has_consistent_totals(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    ru_cart: Cart,
    demo_variant_id: str,
) -> None:
    """Adding a line item yields a cart whose totals reconcile internally."""

    updated = store_cart_client.add_line_item(
        cart_id=ru_cart.id,
        variant_id=demo_variant_id,
        quantity=2,
    )

    # Single currency: the cart exposes exactly one supported currency code.
    assert updated.currency_code in {"rub", "usd"}
    # Internal consistency: line items vs totals + non-negative amounts. Raises a
    # ContractValidationError naming any discrepancy rather than failing silently.
    assert assert_cart_totals_consistent(updated) is updated


@pytest.mark.cart
def test_refetched_cart_totals_stay_consistent(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    ru_cart: Cart,
    demo_variant_id: str,
) -> None:
    """A cart re-read after a mutation still reconciles and keeps its currency."""

    store_cart_client.add_line_item(
        cart_id=ru_cart.id,
        variant_id=demo_variant_id,
        quantity=1,
    )

    fetched = store_cart_client.get_cart(ru_cart.id)

    assert_cart_totals_consistent(fetched)
    assert fetched.currency_code == ru_cart.currency_code
