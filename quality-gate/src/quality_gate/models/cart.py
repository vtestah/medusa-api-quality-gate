"""Cart, shipping, and line-item contract models plus a pure aggregation helper.

These strict Pydantic models describe the Store API cart and shipping payloads:
``Cart`` constrains ``currency_code`` to the supported lowercase literals,
``LineItem`` enforces ``quantity >= 1``, and the response wrappers mirror the
Medusa envelope shapes. :func:`aggregate_line_items` is a pure, side-effect-free
function used by the model-based property test (Property 4): it collapses a
sequence of ``(variant_id, quantity)`` additions into exactly one ``LineItem``
per unique ``variant_id`` with the quantities summed.
"""

from collections import OrderedDict
from collections.abc import Sequence

from pydantic import Field

from quality_gate.models.common import ApiModel, NonEmptyStr
from quality_gate.models.contract import CurrencyCode


class LineItem(ApiModel):
    """A cart line item referencing a product variant and its quantity."""

    id: NonEmptyStr
    variant_id: NonEmptyStr
    quantity: int = Field(ge=1)
    title: str | None = None
    unit_price: int | None = None


class ShippingMethod(ApiModel):
    """A shipping method recorded on a cart."""

    id: NonEmptyStr
    name: str | None = None
    shipping_option_id: str | None = None
    amount: int | None = None


class Cart(ApiModel):
    """Cart contract with a strict lowercase ``currency_code`` (rub/usd)."""

    id: NonEmptyStr
    region_id: NonEmptyStr
    currency_code: CurrencyCode
    items: list[LineItem] = Field(default_factory=list)
    shipping_methods: list[ShippingMethod] = Field(default_factory=list)


class CartResponse(ApiModel):
    """Response contract wrapping a single cart (POST/GET /store/carts)."""

    cart: Cart


class ShippingOption(ApiModel):
    """A shipping option available for a cart's market."""

    id: NonEmptyStr
    name: NonEmptyStr
    amount: int | None = None


class ShippingOptionsResponse(ApiModel):
    """Response contract for GET /store/shipping-options."""

    shipping_options: list[ShippingOption] = Field(default_factory=list)


def aggregate_line_items(additions: Sequence[tuple[str, int]]) -> list[LineItem]:
    """Aggregate ``(variant_id, quantity)`` additions into unique line items.

    This is a pure function with no HTTP or external state. It models how a cart
    collapses repeated additions of the same variant: the returned list contains
    exactly one :class:`LineItem` per distinct ``variant_id`` (preserving the order
    of first occurrence), and each line item's ``quantity`` equals the sum of every
    ``quantity`` added for that ``variant_id``. A deterministic ``id`` is derived
    from the ``variant_id`` so the resulting models satisfy the non-empty-id
    contract without requiring server-assigned identifiers.

    Args:
        additions: A sequence of ``(variant_id, quantity)`` pairs, where each
            ``variant_id`` is a non-empty string and each ``quantity`` is ``>= 1``.

    Returns:
        A list of :class:`LineItem`, one per unique ``variant_id``, with quantities
        summed across all additions for that variant.
    """
    totals: OrderedDict[str, int] = OrderedDict()
    for variant_id, quantity in additions:
        totals[variant_id] = totals.get(variant_id, 0) + quantity
    return [
        LineItem(id=f"li_{variant_id}", variant_id=variant_id, quantity=quantity)
        for variant_id, quantity in totals.items()
    ]
