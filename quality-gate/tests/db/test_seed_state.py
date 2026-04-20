"""Database smoke tests for the seeded Medusa runtime."""

import pytest

from quality_gate.db import PostgresDb


@pytest.mark.db
def test_seeded_medusa_tables_are_queryable(db_connection: PostgresDb) -> None:
    """Expected Medusa seed tables should exist and contain demo data."""

    tables = db_connection.fetch_all(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name IN ('region', 'product', 'product_category')
        ORDER BY table_name
        """
    )

    assert [row["table_name"] for row in tables] == [
        "product",
        "product_category",
        "region",
    ]

    region_count = db_connection.fetch_value("SELECT count(*) FROM region")
    product_count = db_connection.fetch_value("SELECT count(*) FROM product")
    category_count = db_connection.fetch_value(
        "SELECT count(*) FROM product_category"
    )

    assert region_count >= 2
    assert product_count >= 1
    assert category_count >= 1
