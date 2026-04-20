"""Smoke tests for Medusa health."""

import pytest
import requests

from quality_gate.clients import HealthClient
from quality_gate.config import Settings


@pytest.mark.smoke
@pytest.mark.contract
def test_health_endpoint_returns_ok(
    runtime_ready: None,
    api_session: requests.Session,
    settings: Settings,
) -> None:
    """Medusa health endpoint should be reachable and contract-valid."""

    client = HealthClient(api_session, settings)
    payload = client.retrieve()

    assert payload.status.lower() == "ok"
