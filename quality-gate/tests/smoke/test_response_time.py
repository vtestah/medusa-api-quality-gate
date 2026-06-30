"""Soft-SLA latency smoke checks against the live runtime.

These run against the live Medusa Store API and are guarded by ``runtime_ready``
so they skip cleanly when the runtime is unavailable. Each issues a single read
through a Service Object client and asserts the round-trip stayed under a generous
ceiling via :func:`assert_response_within_sla`. The threshold is intentionally
lenient: the goal is to flag pathological latency, not to benchmark performance.
"""

import pytest

from quality_gate.clients import HealthClient, StoreProductsClient, StoreRegionsClient
from quality_gate.timing import assert_response_within_sla

# Generous soft-SLA ceiling, comfortably below the client request timeout so a
# non-pathological response always passes.
_SOFT_SLA_SECONDS = 8.0


@pytest.mark.smoke
def test_health_responds_within_soft_sla(
    runtime_ready: None,
    health_client: HealthClient,
) -> None:
    """The health endpoint answers well within the soft SLA."""

    response = health_client.get("/health")

    assert response.status_code == 200
    assert_response_within_sla(response, max_seconds=_SOFT_SLA_SECONDS)


@pytest.mark.smoke
def test_store_products_listing_responds_within_soft_sla(
    runtime_ready: None,
    store_products_client: StoreProductsClient,
) -> None:
    """A products listing read stays within the soft SLA.

    Uses the client's low-level ``get`` so the publishable-key header is injected
    while still exposing the raw response for its ``elapsed`` round-trip time.
    """

    response = store_products_client.get("/store/products")

    assert response.status_code == 200
    assert_response_within_sla(response, max_seconds=_SOFT_SLA_SECONDS)


@pytest.mark.smoke
def test_store_regions_listing_responds_within_soft_sla(
    runtime_ready: None,
    store_regions_client: StoreRegionsClient,
) -> None:
    """A regions listing read stays within the soft SLA."""

    response = store_regions_client.get("/store/regions")

    assert response.status_code == 200
    assert_response_within_sla(response, max_seconds=_SOFT_SLA_SECONDS)
