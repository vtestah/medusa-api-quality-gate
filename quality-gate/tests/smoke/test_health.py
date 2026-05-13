"""Smoke tests for Medusa health."""

import pytest

from quality_gate.clients import HealthClient


@pytest.mark.smoke
@pytest.mark.contract
def test_health_endpoint_returns_ok(
    runtime_ready: None,
    health_client: HealthClient,
) -> None:
    """Medusa health endpoint should be reachable and contract-valid."""

    payload = health_client.retrieve()

    assert payload.status.lower() == "ok"
