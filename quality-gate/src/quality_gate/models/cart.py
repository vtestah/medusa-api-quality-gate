"""Cart, shipping, and line-item contract models plus pure cart helpers.

These strict Pydantic models describe the Store API cart and shipping payloads:
``Cart`` constrains ``currency_code`` to the supported lowercase literals,
``LineItem`` enforces ``quantity >= 1``, and the response wrappers mirror the
Medusa envelope shapes. Monetary amounts are typed as :data:`Money` (integer minor
units, matching how the runtime serializes prices) and every total is optional, so
the models parse cart responses with or without computed totals.

:func:`aggregate_line_items` collapses a sequence of ``(variant_id, quantity)``
additions into one ``LineItem`` per unique ``variant_id``.
:func:`assert_cart_totals_consistent` checks that a cart's totals are internally
consistent (line items vs totals, single currency). Both are pure and
side-effect-free.
"""

from collections import OrderedDict
from collections.abc import Sequence

from pydantic import Field

from quality_gate.errors import ContractValidationError
from quality_gate.models.common import ApiModel, NonEmptyStr
from quality_gate.models.contract import CurrencyCode

Money = int
"""Integer monetary amount in the currency's minor units, as returned by the Store API."""


class LineItem(ApiModel):
    """A cart line item referencing a product variant and its quantity."""

    id: NonEmptyStr
    variant_id: NonEmptyStr
    quantity: int = Field(ge=1)
    title: str | None = None
    unit_price: Money | None = None
    subtotal: Money | None = None
    total: Money | None = None


class ShippingMethod(ApiModel):
    """A shipping method recorded on a cart."""

    id: NonEmptyStr
    name: str | None = None
    shipping_option_id: str | None = None
    amount: Money | None = None


class Cart(ApiModel):
    """Cart contract: strict lowercase ``currency_code`` plus optional money totals."""

    id: NonEmptyStr
    region_id: NonEmptyStr
    currency_code: CurrencyCode
    items: list[LineItem] = Field(default_factory=list)
    shipping_methods: list[ShippingMethod] = Field(default_factory=list)
    item_subtotal: Money | None = None
    item_total: Money | None = None
    subtotal: Money | None = None
    tax_total: Money | None = None
    shipping_total: Money | None = None
    discount_total: Money | None = None
    total: Money | None = None


class CartResponse(ApiModel):
    """Response contract wrapping a single cart (POST/GET /store/carts)."""

    cart: Cart


class ShippingOption(ApiModel):
    """A shipping option available for a cart's market."""

    id: NonEmptyStr
    name: NonEmptyStr
    amount: Money | None = None


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


def assert_cart_totals_consistent(cart: Cart) -> Cart:
    """Assert a cart's monetary totals are internally consistent, then return it.

    Every check is defensive: it runs only when the relevant fields are present, so
    the helper works whether or not the Store API includes computed totals on a
    given response. On any inconsistency it raises :class:`ContractValidationError`
    naming the discrepancy rather than returning silently; on success it returns the
    cart unchanged.

    Verified invariants:

    - **Single currency.** Every line item that carries its own ``currency_code``
      matches the cart's ``currency_code`` (which the model already constrains to
      the supported lowercase literals).
    - **Non-negative amounts.** Present line-item ``unit_price``/``subtotal``/
      ``total`` and present cart ``subtotal``/``item_subtotal``/``item_total``/
      ``tax_total``/``shipping_total``/``total`` are ``>= 0``. ``discount_total`` is
      excluded, since its sign convention varies.
    - **Line items vs totals.** When the cart exposes ``item_subtotal`` and every
      line item exposes ``subtotal``, the cart value equals the sum of the line
      values; likewise for ``item_total`` against the line ``total`` values.
    """
    cart_currency = cart.currency_code

    for item in cart.items:
        item_currency = (item.model_extra or {}).get("currency_code")
        if item_currency is not None and item_currency != cart_currency:
            raise ContractValidationError(
                f"line item {item.id!r} currency {item_currency!r} does not match "
                f"cart currency {cart_currency!r}"
            )
        for field_name, value in (
            ("unit_price", item.unit_price),
            ("subtotal", item.subtotal),
            ("total", item.total),
        ):
            if value is not None and value < 0:
                raise ContractValidationError(
                    f"line item {item.id!r} {field_name} is negative: {value}"
                )

    cart_money_fields = {
        "subtotal": cart.subtotal,
        "item_subtotal": cart.item_subtotal,
        "item_total": cart.item_total,
        "tax_total": cart.tax_total,
        "shipping_total": cart.shipping_total,
        "total": cart.total,
    }
    for field_name, value in cart_money_fields.items():
        if value is not None and value < 0:
            raise ContractValidationError(f"cart {field_name} is negative: {value}")

    expected_item_subtotal = cart.item_subtotal
    if cart.items and expected_item_subtotal is not None:
        line_subtotals = [item.subtotal for item in cart.items if item.subtotal is not None]
        if len(line_subtotals) == len(cart.items) and sum(line_subtotals) != expected_item_subtotal:
            raise ContractValidationError(
                f"cart item_subtotal {expected_item_subtotal} does not equal the sum "
                f"of line-item subtotals {sum(line_subtotals)}"
            )

    expected_item_total = cart.item_total
    if cart.items and expected_item_total is not None:
        line_totals = [item.total for item in cart.items if item.total is not None]
        if len(line_totals) == len(cart.items) and sum(line_totals) != expected_item_total:
            raise ContractValidationError(
                f"cart item_total {expected_item_total} does not equal the sum "
                f"of line-item totals {sum(line_totals)}"
            )

    return cart
