"""Smoke contract tests for Medusa customer registration preflight."""

import logging

import pytest

from quality_gate.clients import StoreAuthClient
from quality_gate.models import AuthErrorResponse


LOGGER = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.contract
def test_customer_registration_requires_password(
    runtime_ready: None,
    store_auth_client: StoreAuthClient,
) -> None:
    """Registration identity creation should reject a payload without password."""

    LOGGER.info("Verify customer registration rejects payload without password")

    response = store_auth_client.request_customer_registration_token(
        email="qa-preflight@example.com",
    )

    LOGGER.info("Customer registration preflight returned status %s", response.status_code)

    assert response.status_code == 401

    payload = AuthErrorResponse.model_validate(response.json())

    assert payload.type == "unauthorized"
    assert "password" in payload.message.lower()
