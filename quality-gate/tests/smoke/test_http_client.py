"""Smoke checks for shared HTTP client behavior."""

from typing import Any

import pytest
from requests import Response, Session

from quality_gate.clients import StoreCustomersClient
from quality_gate.clients.base import BaseApiClient
from quality_gate.config import Settings

pytestmark = [pytest.mark.smoke, pytest.mark.bootstrap]


class RecordingSession(Session):
    """Minimal session double that records outgoing POST calls."""

    def __init__(self, response: Response) -> None:
        super().__init__()
        self._response = response
        self.post_calls: list[dict[str, Any]] = []

    def post(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response:
        self.post_calls.append(
            {
                "url": url,
                "json": json,
                "params": params,
                "headers": headers,
                "timeout": timeout,
            }
        )
        return self._response


def make_response(
    status_code: int,
    body: str = "{}",
    url: str = "http://localhost:9000/store/customers",
) -> Response:
    """Build a minimal requests response for client helper checks."""

    response = Response()
    response.status_code = status_code
    response._content = body.encode("utf-8")
    response.url = url
    return response


def test_expected_status_code_returns_response_when_status_matches() -> None:
    """The helper should keep the original response available to the caller."""

    response = make_response(401, '{"message":"password is required"}')

    checked_response = BaseApiClient.expect_status_code(
        response,
        expected_status_code=401,
    )

    assert checked_response is response


def test_expected_status_code_failure_message_shows_expected_and_actual() -> None:
    """Mismatch errors should explain the contract failure without extra debugging."""

    response = make_response(401, '{"message":"password is required"}')

    with pytest.raises(
        AssertionError,
        match="Expected status code 201, but actual is 401",
    ):
        BaseApiClient.expect_status_code(
            response,
            expected_status_code=201,
        )


def test_expected_status_code_failure_message_shows_url_and_body() -> None:
    """Failure diagnostics should include the endpoint and response preview."""

    response = make_response(500, '{"message":"database is unavailable"}')

    with pytest.raises(AssertionError) as exc_info:
        BaseApiClient.expect_status_code(
            response,
            expected_status_code=200,
        )

    message = str(exc_info.value)

    assert "URL: http://localhost:9000/store/customers" in message
    assert "database is unavailable" in message


def test_store_customer_client_builds_payload_headers_and_contract() -> None:
    """Customer client should turn method arguments into one Store API request."""

    response = make_response(
        200,
        body=(
            '{"customer":{'
            '"id":"cus_test",'
            '"email":"qa-customer@example.test",'
            '"first_name":"Ada",'
            '"last_name":"Lovelace",'
            '"company_name":null,'
            '"phone":"+15551234567",'
            '"addresses":[]'
            "}}"
        ),
        url="http://medusa.test/store/customers",
    )
    session = RecordingSession(response)
    settings = Settings(
        medusa_base_url="http://medusa.test",
        publishable_key="pk_test_lesson",
        request_timeout_seconds=2.5,
    )
    client = StoreCustomersClient(session=session, settings=settings)

    customer_response = client.register_customer(
        token="jwt-test-token",
        email="qa-customer@example.test",
        first_name="Ada",
        last_name="Lovelace",
        locale="ru-RU",
        extra_payload={"phone": "+15551234567"},
    )

    post_call = session.post_calls[0]

    assert post_call["url"] == "http://medusa.test/store/customers"
    assert post_call["json"] == {
        "email": "qa-customer@example.test",
        "first_name": "Ada",
        "last_name": "Lovelace",
        "phone": "+15551234567",
    }
    assert post_call["headers"] == {
        "x-publishable-api-key": "pk_test_lesson",
        "Authorization": "Bearer jwt-test-token",
        "Content-Type": "application/json",
        "x-medusa-locale": "ru-RU",
    }
    assert post_call["timeout"] == 2.5
    assert customer_response.customer.email == "qa-customer@example.test"
