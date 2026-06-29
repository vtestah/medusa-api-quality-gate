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
        expected_status_code: int | None = None,
    ) -> Response:
        response = self._session.get(
            self._build_url(path),
            params=params,
            headers=self._merge_headers(headers),
            timeout=self._settings.request_timeout_seconds,
        )
        if expected_status_code is not None:
            return self.expect_status_code(response, expected_status_code)
        return response

    def post(
        self,
        path: str,
        *,
        json: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        expected_status_code: int | None = None,
    ) -> Response:
        response = self._session.post(
            self._build_url(path),
            json=json,
            params=params,
            headers=self._merge_headers(headers),
            timeout=self._settings.request_timeout_seconds,
        )
        if expected_status_code is not None:
            return self.expect_status_code(response, expected_status_code)
        return response

    @staticmethod
    def expect_status_code(
        response: Response,
        expected_status_code: int,
    ) -> Response:
        """Return the response only when the HTTP status matches the contract."""

        if response.status_code == expected_status_code:
            return response

        response_url = response.url or "<unknown url>"
        body_preview = response.text[:500].replace("\n", "\\n")
        raise AssertionError(
            f"Expected status code {expected_status_code}, "
            f"but actual is {response.status_code}. "
            f"URL: {response_url}. "
            f"Response body: {body_preview}"
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
