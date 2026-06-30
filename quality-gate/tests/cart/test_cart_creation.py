"""Integration tests for cart creation against the live Medusa runtime.

These run against the live Store API and are guarded by ``runtime_ready`` so they
skip cleanly when the runtime is unavailable. They assert that creating a cart for
a seeded region yields a strictly validated :class:`Cart` with a non-empty ``id``,
``region_id``, and a lowercase ``currency_code`` constrained to ``rub``/``usd``.
All assertions use the Pydantic model, never raw dict keys.
"""

import pytest

from quality_gate.models.cart import Cart


@pytest.mark.cart
def test_create_cart_returns_validated_cart(
    runtime_ready: None,
    ru_cart: Cart,
) -> None:
    """A created RU-market cart is a valid Cart with the expected scalar fields.

    The ``ru_cart`` fixture resolves the RU region id from the regions client and
    creates the cart through ``StoreCartClient.create_cart``, which already raises
    on a non-2xx status or a body that fails validation. Here we confirm the
    returned contract model exposes a non-empty ``id`` and ``region_id`` and a
    ``currency_code`` that is exactly ``rub`` or ``usd``.
    """

    assert isinstance(ru_cart, Cart)
    assert ru_cart.id
    assert ru_cart.region_id
    assert ru_cart.currency_code in {"rub", "usd"}
