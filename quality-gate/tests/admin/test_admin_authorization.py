"""Access-control checks for the Admin API against the live runtime.

These run against the live Admin API and are guarded by ``runtime_ready`` so they
skip cleanly when the runtime is unavailable. They assert the access-control
behaviour of a protected admin endpoint: a request without credentials, or one
carrying an invalid (non-admin) bearer token, is rejected with 401/403 rather than
returning data. The authenticated happy path is covered separately in
``test_admin_api.py``.
"""

import pytest

from quality_gate.clients import AdminApiClient

# Status codes that represent a rejected (unauthenticated/unauthorized) request.
_REJECT_STATUS_CODES = {401, 403}


@pytest.mark.negative
@pytest.mark.admin
@pytest.mark.parametrize(
    ("scenario", "token"),
    [
        ("missing credentials", None),
        ("malformed bearer token", "not-a-real-jwt"),
        ("invalid bearer token", "eyJhbGciOiJIUzI1NiJ9.invalid.signature"),
    ],
)
def test_admin_products_rejects_unauthorized_access(
    runtime_ready: None,
    admin_client: AdminApiClient,
    scenario: str,
    token: str | None,
) -> None:
    """A protected admin read is rejected without valid admin authorization.

    ``token=None`` sends no ``Authorization`` header; the other cases send a
    bearer token that is not a valid admin session. All must be rejected with a
    401/403 rather than returning a products listing.
    """

    response = admin_client.request_products(token=token)

    assert response.status_code in _REJECT_STATUS_CODES, (
        f"expected {scenario} to be rejected with one of {_REJECT_STATUS_CODES}, "
        f"but actual is {response.status_code}"
    )
