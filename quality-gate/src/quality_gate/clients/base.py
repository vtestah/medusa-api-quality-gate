"""Shared HTTP client primitives."""

from collections.abc import Mapping
from typing import Any
from urllib.parse import urljoin

from requests import Response, Session

from quality_gate.config import Settings


class BaseApiClient:
    """Minimal base client around a shared requests session."""

    def __init__(self, session: Session, settings: Settings) -> None:
        self._session = session
        self._settings = settings

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Response:
        return self._session.get(
            self._build_url(path),
            params=params,
            headers=self._merge_headers(headers),
            timeout=self._settings.request_timeout_seconds,
        )

    def post(
        self,
        path: str,
        *,
        json: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Response:
        return self._session.post(
            self._build_url(path),
            json=json,
            params=params,
            headers=self._merge_headers(headers),
            timeout=self._settings.request_timeout_seconds,
        )

    def _build_url(self, path: str) -> str:
        normalized_base = f"{self._settings.medusa_base_url.rstrip('/')}/"
        normalized_path = path.lstrip("/")
        return urljoin(normalized_base, normalized_path)

    def _merge_headers(
        self,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        merged_headers: dict[str, str] = {}
        if headers:
            merged_headers.update(headers)
        return merged_headers


class StoreApiClient(BaseApiClient):
    """Base client that automatically injects Medusa Store API headers."""

    def _merge_headers(
        self,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        merged_headers = dict(self._settings.store_headers)
        if headers:
            merged_headers.update(headers)
        return merged_headers
