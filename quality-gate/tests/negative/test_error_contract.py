"""Data-driven error-contract tests for the Store API.

These run against the live runtime and are guarded by ``runtime_ready`` so they
skip cleanly when it is unavailable. They are parametrized over several
error-producing requests (missing/wrong publishable key, unknown product, unknown
cart) and assert a consistent error contract: the rejection status is in the
expected set, the body is a JSON object, it validates against ``StoreApiError``,
and it carries at least one recognized error field. Bodies are validated through
the model, never raw dict access.
"""

import pytest
import requests

from quality_gate.config import Settings
from quality_gate.models.errors import StoreApiError


def _store_url(settings: Settings, path: str) -> str:
    """Build an absolute Store API URL from ``settings.medusa_base_url``."""

    return f"{settings.medusa_base_url.rstrip('/')}/{path.lstrip('/')}"


def _headers_for_mode(settings: Settings, header_mode: str) -> dict[str, str]:
    """Return request headers for a publishable-key mode (none/wrong/valid)."""

    if header_mode == "none":
        return {}
    if header_mode == "wrong":
        return {"x-publishable-api-key": "pk_wrong"}
    return dict(settings.store_headers)


@pytest.mark.negative
@pytest.mark.contract
@pytest.mark.parametrize(
    ("path", "header_mode", "accepted_status_codes"),
    [
        ("/store/products", "none", {400, 401}),
        ("/store/products", "wrong", {400, 401}),
        ("/store/products/prod_does_not_exist", "valid", {400, 404}),
        ("/store/carts/cart_does_not_exist", "valid", {400, 404}),
    ],
)
def test_error_body_matches_contract(
    runtime_ready: None,
    api_session: requests.Session,
    settings: Settings,
    path: str,
    header_mode: str,
    accepted_status_codes: set[int],
) -> None:
    """Each error-producing request returns a recognized status and a model-valid body."""

    response = api_session.get(
        _store_url(settings, path),
        headers=_headers_for_mode(settings, header_mode),
        timeout=settings.request_timeout_seconds,
    )

    assert response.status_code in accepted_status_codes, (
        f"Expected status in {accepted_status_codes}, but actual is {response.status_code}"
    )

    body = response.json()
    assert isinstance(body, dict), f"expected a JSON object error body, got {type(body)!r}"

    error = StoreApiError.model_validate(body)
    assert error.message is not None or error.type is not None or error.code is not None, (
        "error body carried none of the recognized fields (message/type/code)"
    )
