"""Integration tests for adding line items to a cart against the live runtime.

These run against the live Store API and are guarded by ``runtime_ready`` so they
skip cleanly when the runtime is unavailable. They cover the happy path (adding a
line item and re-adding the same variant to confirm aggregation) and negative
paths (a non-existent variant and a pre-flight rejected ``quantity``). The
``variant_id`` always comes from the ``demo_variant_id`` fixture (Demo_Product via
the products client), never a hard-coded id (Req 4.5). All response assertions use
Pydantic models, never raw dict keys (Req 7.1).
"""

import pytest

from quality_gate.clients import StoreCartClient
from quality_gate.errors import ClientValidationError
from quality_gate.models.cart import Cart, LineItem
from quality_gate.models.errors import StoreApiError


def _line_item_for_variant(cart: Cart, variant_id: str) -> LineItem:
    """Return the single line item in ``cart`` referencing ``variant_id``."""

    matching = [item for item in cart.items if item.variant_id == variant_id]
    assert len(matching) == 1, (
        f"expected exactly one line item for variant {variant_id!r}, "
        f"found {len(matching)}"
    )
    return matching[0]


@pytest.mark.cart
def test_add_line_item_records_variant_and_quantity(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    ru_cart: Cart,
    demo_variant_id: str,
) -> None:
    """Adding a line item yields a cart containing that variant at the requested qty.

    The returned :class:`Cart` must contain a :class:`LineItem` referencing the
    requested ``variant_id`` with ``quantity`` equal to what was requested
    (Req 4.1, 4.2).
    """

    requested_quantity = 2
    updated = store_cart_client.add_line_item(
        cart_id=ru_cart.id,
        variant_id=demo_variant_id,
        quantity=requested_quantity,
    )

    assert isinstance(updated, Cart)
    line_item = _line_item_for_variant(updated, demo_variant_id)
    assert line_item.quantity == requested_quantity


@pytest.mark.cart
def test_re_adding_same_variant_aggregates_quantity(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    ru_cart: Cart,
    demo_variant_id: str,
) -> None:
    """Re-adding the same variant keeps one line item and sums the quantities.

    The number of distinct line items for the variant must not increase, and the
    matching :class:`LineItem.quantity` must equal the sum of both additions
    (Req 4.3, 4.4).
    """

    first_quantity = 2
    second_quantity = 3

    after_first = store_cart_client.add_line_item(
        cart_id=ru_cart.id,
        variant_id=demo_variant_id,
        quantity=first_quantity,
    )
    distinct_after_first = len(
        [item for item in after_first.items if item.variant_id == demo_variant_id]
    )

    after_second = store_cart_client.add_line_item(
        cart_id=ru_cart.id,
        variant_id=demo_variant_id,
        quantity=second_quantity,
    )
    distinct_after_second = len(
        [item for item in after_second.items if item.variant_id == demo_variant_id]
    )

    # Re-adding the same variant must not create an additional line item.
    assert distinct_after_second == distinct_after_first
    aggregated = _line_item_for_variant(after_second, demo_variant_id)
    assert aggregated.quantity == first_quantity + second_quantity


@pytest.mark.cart
def test_add_nonexistent_variant_returns_error_and_leaves_cart_unchanged(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    ru_cart: Cart,
    demo_variant_id: str,
) -> None:
    """A non-existent variant yields an error body parsed by StoreApiError.

    The low-level ``add_line_item_response`` returns the raw response without
    validating the body, so the test asserts a non-2xx status, parses the error
    body via :class:`StoreApiError` without raising, and confirms (best-effort)
    the cart composition is unchanged (Req 4.6).
    """

    # Seed the cart with a known-good line item so we have a composition baseline.
    seeded = store_cart_client.add_line_item(
        cart_id=ru_cart.id,
        variant_id=demo_variant_id,
        quantity=1,
    )
    baseline_item_count = len(seeded.items)

    response = store_cart_client.add_line_item_response(
        cart_id=ru_cart.id,
        variant_id="nonexistent_variant_xyz",
        quantity=1,
    )

    assert not 200 <= response.status_code <= 299, (
        f"expected an error status for a non-existent variant, "
        f"got {response.status_code}"
    )

    # The error body must parse into the unified contract model without raising.
    error = StoreApiError.model_validate(response.json())
    assert isinstance(error, StoreApiError)

    # Best-effort: the cart composition is unchanged by the rejected addition.
    current = store_cart_client.get_cart(ru_cart.id)
    assert len(current.items) == baseline_item_count
    assert "nonexistent_variant_xyz" not in {item.variant_id for item in current.items}


@pytest.mark.cart
def test_add_line_item_zero_quantity_rejected_preflight(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    ru_cart: Cart,
    demo_variant_id: str,
) -> None:
    """A ``quantity`` below 1 is rejected pre-flight before any HTTP request.

    ``add_line_item`` raises :class:`ClientValidationError` for ``quantity=0``
    without sending a request, leaving the cart unchanged (Req 4.7).
    """

    with pytest.raises(ClientValidationError):
        store_cart_client.add_line_item(
            cart_id=ru_cart.id,
            variant_id=demo_variant_id,
            quantity=0,
        )
