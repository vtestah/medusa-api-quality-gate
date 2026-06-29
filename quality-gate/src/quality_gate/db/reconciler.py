"""Read-only cross-layer reconciler comparing Store API state with PostgreSQL.

The reconciler issues only parameterized, read-only ``SELECT`` queries through
:class:`~quality_gate.db.postgres.PostgresDb`; it never performs ``INSERT``,
``UPDATE`` or ``DELETE``.

Table and column names target the **Medusa v2** schema and are centralized in
this module so they are easy to adjust against a real runtime:

- cart table ``cart`` with columns ``id`` and ``region_id``;
- line items table ``cart_line_item`` with column ``cart_id``;
- region table ``region`` with columns ``id`` and ``currency_code``.

``PostgresDb`` runs queries with psycopg3 where sequence params bind to ``%s``
positional placeholders, so every query below uses ``%s`` with a tuple.
"""

from quality_gate.db.postgres import PostgresDb

_COUNT_CARTS_BY_ID = "SELECT count(*) FROM cart WHERE id = %s"
_COUNT_LINE_ITEMS = "SELECT count(*) FROM cart_line_item WHERE cart_id = %s"
_FETCH_CART_REGION_CURRENCY = (
    "SELECT r.currency_code "
    "FROM cart c "
    "JOIN region r ON r.id = c.region_id "
    "WHERE c.id = %s"
)


class DbReconciler:
    """Read-only verification of Store API state against PostgreSQL."""

    def __init__(self, db: PostgresDb) -> None:
        self._db = db

    def count_carts_by_id(self, cart_id: str) -> int:
        """Return the number of cart rows matching ``cart_id`` (expected 0 or 1)."""
        value = self._db.fetch_value(_COUNT_CARTS_BY_ID, (cart_id,))
        return int(value) if value is not None else 0

    def count_line_items(self, cart_id: str) -> int:
        """Return the number of line item rows for the given cart."""
        value = self._db.fetch_value(_COUNT_LINE_ITEMS, (cart_id,))
        return int(value) if value is not None else 0

    def fetch_cart_region_currency(self, cart_id: str) -> str | None:
        """Return the currency code of the cart's region, or ``None`` if absent."""
        value = self._db.fetch_value(_FETCH_CART_REGION_CURRENCY, (cart_id,))
        return str(value) if value is not None else None
