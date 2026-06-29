"""Smoke contract tests for Medusa customer registration."""

import logging

import pytest

from quality_gate.clients import StoreAuthClient, StoreCustomersClient
from quality_gate.models import AuthErrorResponse
from quality_gate.test_data import build_customer_credentials


LOGGER = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.contract
def test_customer_registration_requires_password(
    runtime_ready: None,
    store_auth_client: StoreAuthClient,
) -> None:
    """Registration identity creation should reject a payload without password."""

    LOGGER.info("Verify customer registration rejects payload without password")

    credentials = build_customer_credentials(prefix="qa-preflight")

    response = store_auth_client.request_customer_registration_token(
        email=credentials.email,
        expected_status_code=401,
    )

    LOGGER.info("Customer registration preflight returned status %s", response.status_code)

    payload = AuthErrorResponse.model_validate(response.json())

    assert payload.type == "unauthorized"
    assert "password" in payload.message.lower()


@pytest.mark.smoke
@pytest.mark.contract
def test_customer_registration_response_matches_payload(
    runtime_ready: None,
    store_auth_client: StoreAuthClient,
    store_customers_client: StoreCustomersClient,
) -> None:
    """Customer registration should return the created customer contract."""

    credentials = build_customer_credentials(prefix="qa-customer")

    LOGGER.info("Request customer registration token for %s", credentials.email)
    token_response = store_auth_client.create_customer_registration_token(
        email=credentials.email,
        password=credentials.password,
    )

    LOGGER.info("Create customer profile for %s", credentials.email)
    customer_response = store_customers_client.register_customer(
        token=token_response.token,
        email=credentials.email,
    )

    customer = customer_response.customer

    assert customer.email == credentials.email, (
        "Create customer API returned wrong email. "
        f"Expected {credentials.email}, got {customer.email}."
    )
    assert customer.first_name in (None, ""), (
        "Create customer API returned first_name even though payload did not set it. "
        f"Actual first_name: {customer.first_name!r}."
    )
    assert customer.id.startswith("cus_")
    assert credentials.password not in customer_response.model_dump_json()
