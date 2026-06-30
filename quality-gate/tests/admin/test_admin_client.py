"""Unit tests for the Admin API client using a mocked HTTP session.

These run without a live runtime: they pin the request shape (endpoint, payload,
authorization header) and the response parsing, complementing the live
integration checks in ``test_admin_api.py``.
"""

from typing import cast
from unittest.mock import MagicMock

import pytest
from requests import Session

from quality_gate.clients import AdminApiClient
from quality_gate.config import Settings

pytestmark = pytest.mark.contract


def _client_with_response(
    method: str,
    *,
    status_code: int,
    json_body: object,
) -> tuple[AdminApiClient, MagicMock]:
    """Build an AdminApiClient backed by a mocked session returning one response."""
    session = MagicMock()
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_body
    getattr(session, method).return_value = response
    client = AdminApiClient(cast("Session", session), Settings())
    return client, session


def test_login_posts_credentials_to_user_emailpass_and_returns_token() -> None:
    client, session = _client_with_response(
        "post", status_code=200, json_body={"token": "jwt-123"}
    )

    token = client.login(email="admin@example.com", password="secret")

    assert token == "jwt-123"
    url, kwargs = session.post.call_args.args[0], session.post.call_args.kwargs
    assert url.endswith("/auth/user/emailpass")
    assert kwargs["json"] == {"email": "admin@example.com", "password": "secret"}


def test_products_without_token_sends_no_authorization_header() -> None:
    client, session = _client_with_response("get", status_code=401, json_body={})

    response = client.request_products(token=None)

    assert response.status_code == 401
    sent_headers = session.get.call_args.kwargs.get("headers") or {}
    assert "Authorization" not in sent_headers


def test_products_with_token_sends_bearer_header_and_parses_contract() -> None:
    client, session = _client_with_response(
        "get",
        status_code=200,
        json_body={"products": [{"id": "prod_1", "title": "Heavy Tee"}], "count": 1},
    )

    listing = client.list_products(token="jwt-123")

    assert listing.count == 1
    assert listing.products[0].id == "prod_1"
    assert listing.products[0].title == "Heavy Tee"
    assert session.get.call_args.kwargs["headers"]["Authorization"] == "Bearer jwt-123"
