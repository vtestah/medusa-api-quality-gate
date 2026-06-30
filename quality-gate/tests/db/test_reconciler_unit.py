"""Unit tests for the read-only DbReconciler using a mocked PostgresDb.

These run without a live database: they mock :class:`PostgresDb` so the reconciler
methods, their parameter binding, and the ``None`` (absent-row) fallbacks are all
exercised deterministically, complementing the live cross-layer checks in
``test_cart_db_reconciliation.py``.
"""

from typing import cast
from unittest.mock import MagicMock

import pytest

from quality_gate.db.postgres import PostgresDb
from quality_gate.db.reconciler import DbReconciler

pytestmark = pytest.mark.contract


def _reconciler_returning(value: object) -> tuple[DbReconciler, MagicMock]:
    """Build a reconciler whose mocked PostgresDb returns ``value`` for every query."""
    db = MagicMock(spec=PostgresDb)
    db.fetch_value.return_value = value
    return DbReconciler(cast("PostgresDb", db)), db


def test_count_carts_by_id_returns_int_and_binds_param() -> None:
    reconciler, db = _reconciler_returning(1)

    assert reconciler.count_carts_by_id("cart_1") == 1
    query, params = db.fetch_value.call_args.args
    assert "from cart" in query.lower()
    assert params == ("cart_1",)


def test_count_carts_by_id_defaults_to_zero_when_absent() -> None:
    reconciler, _ = _reconciler_returning(None)

    assert reconciler.count_carts_by_id("missing") == 0


def test_count_line_items_returns_int_and_binds_param() -> None:
    reconciler, db = _reconciler_returning(3)

    assert reconciler.count_line_items("cart_1") == 3
    assert db.fetch_value.call_args.args[1] == ("cart_1",)


def test_count_line_items_defaults_to_zero_when_absent() -> None:
    reconciler, _ = _reconciler_returning(None)

    assert reconciler.count_line_items("cart_1") == 0


def test_sum_line_item_quantities_returns_int_and_sums() -> None:
    reconciler, db = _reconciler_returning(5)

    assert reconciler.sum_line_item_quantities("cart_1") == 5
    assert "sum(quantity)" in db.fetch_value.call_args.args[0].lower()


def test_sum_line_item_quantities_defaults_to_zero_when_absent() -> None:
    reconciler, _ = _reconciler_returning(None)

    assert reconciler.sum_line_item_quantities("cart_1") == 0


def test_fetch_cart_region_currency_returns_str() -> None:
    reconciler, db = _reconciler_returning("usd")

    assert reconciler.fetch_cart_region_currency("cart_1") == "usd"
    assert "join region" in db.fetch_value.call_args.args[0].lower()


def test_fetch_cart_region_currency_returns_none_when_absent() -> None:
    reconciler, _ = _reconciler_returning(None)

    assert reconciler.fetch_cart_region_currency("cart_1") is None
