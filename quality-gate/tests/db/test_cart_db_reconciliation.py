"""Cross-layer DB reconciliation integration tests.

These are LIVE tests requiring BOTH the Medusa Store API and PostgreSQL. They
reconcile state observed through the Store API against rows in PostgreSQL using
the read-only :class:`~quality_gate.db.reconciler.DbReconciler`.

Guards (skip, never fail, on missing infrastructure):

- ``ru_cart`` depends on ``runtime_ready`` and skips when Medusa is down.
- ``db_reconciler`` is built on ``db_connection``, which skips when PostgreSQL is
  unavailable.

All reconciliation is read-only: ``DbReconciler`` issues only parameterized
``SELECT`` queries and never modifies data. Divergence fails the test
with explicit expected/actual values. Tests use only Pydantic models and
reconciler methods — no raw SQL.
"""

import pytest

from quality_gate.clients import StoreCartClient
from quality_gate.db.reconciler import DbReconciler
from quality_gate.models.cart import Cart


@pytest.mark.db
def test_created_cart_has_exactly_one_db_row(
    ru_cart: Cart,
    db_reconciler: DbReconciler,
) -> None:
    """A cart created via the Store API maps to exactly one PostgreSQL row."""

    expected_rows = 1
    actual_rows = db_reconciler.count_carts_by_id(ru_cart.id)

    assert actual_rows == expected_rows, (
        f"cart row count mismatch for cart id {ru_cart.id!r}: "
        f"expected {expected_rows}, actual {actual_rows}"
    )


@pytest.mark.db
def test_line_item_count_matches_api_response(
    ru_cart: Cart,
    demo_variant_id: str,
    store_cart_client: StoreCartClient,
    db_reconciler: DbReconciler,
) -> None:
    """DB line-item rows equal the number of items in the API cart response.

    Adds the demo variant twice with distinct quantities. Medusa aggregates repeat
    additions of the same variant into a single line item, so the API response and
    the DB row count must agree on the same total.
    """

    store_cart_client.add_line_item(
        cart_id=ru_cart.id, variant_id=demo_variant_id, quantity=2
    )
    updated_cart = store_cart_client.add_line_item(
        cart_id=ru_cart.id, variant_id=demo_variant_id, quantity=3
    )

    expected_line_items = len(updated_cart.items)
    actual_line_items = db_reconciler.count_line_items(ru_cart.id)

    assert actual_line_items == expected_line_items, (
        f"line item count mismatch for cart id {ru_cart.id!r}: "
        f"expected {expected_line_items} (from API response), "
        f"actual {actual_line_items} (from PostgreSQL)"
    )


@pytest.mark.db
def test_cart_region_currency_matches_api(
    ru_cart: Cart,
    db_reconciler: DbReconciler,
) -> None:
    """The cart region's currency in PostgreSQL matches the API currency_code."""

    expected_currency = ru_cart.currency_code
    actual_currency = db_reconciler.fetch_cart_region_currency(ru_cart.id)

    assert actual_currency == expected_currency, (
        f"region currency mismatch for cart id {ru_cart.id!r}: "
        f"expected {expected_currency!r} (from API), "
        f"actual {actual_currency!r} (from PostgreSQL region join)"
    )
