"""Admin API authentication and authorization checks against the live runtime.

Skipped locally when Medusa is down (via ``runtime_ready``); executed for real in
the integration CI pipeline, which provisions an admin user before the run.
"""

import pytest

from quality_gate.clients import AdminApiClient
from quality_gate.config import Settings

pytestmark = [pytest.mark.admin, pytest.mark.contract]


def test_admin_login_returns_a_bearer_token(
    admin_client: AdminApiClient,
    settings: Settings,
    runtime_ready: None,
) -> None:
    """An admin can exchange email/password for a non-empty bearer token."""
    token = admin_client.login(
        email=settings.admin_email,
        password=settings.admin_password,
    )

    assert token


def test_admin_products_require_authentication(
    admin_client: AdminApiClient,
    runtime_ready: None,
) -> None:
    """The Admin API rejects an unauthenticated products request with 401."""
    response = admin_client.request_products(token=None)

    assert response.status_code == 401


def test_admin_products_listing_matches_contract(
    admin_client: AdminApiClient,
    settings: Settings,
    runtime_ready: None,
) -> None:
    """An authenticated admin reads a contract-valid products listing."""
    token = admin_client.login(
        email=settings.admin_email,
        password=settings.admin_password,
    )

    listing = admin_client.list_products(token=token)

    assert listing.count is None or listing.count >= 0
    for product in listing.products:
        assert product.id
        assert product.title
