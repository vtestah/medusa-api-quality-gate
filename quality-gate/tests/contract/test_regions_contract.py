"""Contract integration tests for GET /store/regions.

These run against the live Medusa runtime and are guarded by ``runtime_ready``
so they skip cleanly when the runtime is unavailable. They assert that every
region returned by the Store API satisfies the strict Pydantic contract and
survives the Round_Trip_Check, surfacing contract violations loudly rather than
suppressing them (Req 1.1, 1.3, 1.4, 1.6, 1.7, 1.8, 7.1).
"""

import pytest

from quality_gate.clients import StoreRegionsClient
from quality_gate.models.contract import assert_round_trip


@pytest.mark.contract
def test_regions_satisfy_strict_contract_and_round_trip(
    runtime_ready: None,
    store_regions_client: StoreRegionsClient,
) -> None:
    """Every region validates via the strict model and survives round-trip.

    ``list_regions`` parses the response through ``RegionsResponse``; a contract
    violation (missing/typed field or invalid ``currency_code``) would raise a
    ``ValidationError`` here and fail the test rather than being suppressed
    (Req 1.1, 1.3, 1.7). Round-trip checks confirm validated fields are stable
    (Req 1.4, 1.8). All assertions use the Pydantic models, never raw dict keys
    (Req 7.1).
    """

    response = store_regions_client.list_regions()

    assert response.regions, "expected at least one region from the live runtime"

    for region in response.regions:
        # Round_Trip_Check: serialize -> re-parse -> compare validated fields.
        # Raises ContractValidationError naming diverging fields on mismatch.
        reparsed = assert_round_trip(region)

        # Strict scalar fields are non-empty (NonEmptyStr) by contract.
        assert region.id
        assert region.name
        # Literal["rub", "usd"] guarantees the exact lowercase currency.
        assert region.currency_code in {"rub", "usd"}

        # Round-trip preserves the validated key fields.
        assert reparsed.id == region.id
        assert reparsed.name == region.name
        assert reparsed.currency_code == region.currency_code
