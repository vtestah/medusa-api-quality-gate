"""Read-only PostgreSQL helper for state verification."""

from collections.abc import Sequence
from typing import Any

from psycopg import Connection, connect
from psycopg.rows import dict_row


class PostgresDb:
    """Small read-only helper around psycopg."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._connection: Connection[Any] | None = None

    def connect(self) -> "PostgresDb":
        self._connection = connect(
            conninfo=self._dsn,
            row_factory=dict_row,
            autocommit=True,
        )
        return self

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def fetch_value(
        self,
        query: str,
        params: Sequence[Any] | None = None,
    ) -> Any:
        connection = self._require_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
        if not row:
            return None
        return next(iter(row.values()))

    def fetch_all(
        self,
        query: str,
        params: Sequence[Any] | None = None,
    ) -> list[dict[str, Any]]:
        connection = self._require_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def _require_connection(self) -> Connection[Any]:
        if self._connection is None:
            raise RuntimeError("PostgreSQL connection is not initialized.")
        return self._connection
