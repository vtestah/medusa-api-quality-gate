"""Contract integration tests for GET /store/products.

These run against the live Medusa runtime and are guarded by ``runtime_ready``
so they skip cleanly when the runtime is unavailable. They assert that every
product returned by the Store API satisfies the strict Pydantic contract and
survives the Round_Trip_Check, surfacing contract violations loudly rather than
suppressing them (Req 1.2, 1.3, 1.4, 1.6, 1.7, 1.8, 7.1).
"""

import pytest

from quality_gate.clients import StoreProductsClient
from quality_gate.config import Settings
from quality_gate.models.contract import assert_round_trip


@pytest.mark.contract
def test_products_satisfy_strict_contract_and_round_trip(
    runtime_ready: None,
    store_products_client: StoreProductsClient,
    settings: Settings,
) -> None:
    """Every product validates via the strict model and survives round-trip.

    ``list_products`` parses the response through ``ProductsResponse``; a contract
    violation (missing or wrongly typed ``id``/``handle``/``title``) would raise a
    ``ValidationError`` here and fail the test rather than being suppressed
    (Req 1.2, 1.3, 1.7). Round-trip checks confirm validated fields are stable
    (Req 1.4, 1.8). All assertions use the Pydantic models, never raw dict keys
    (Req 7.1).
    """

    response = store_products_client.list_products(
        handle=settings.demo_product_handle,
    )

    assert response.products, (
        f"expected at least one product for handle "
        f"{settings.demo_product_handle!r} from the live runtime"
    )

    for product in response.products:
        # Round_Trip_Check: serialize -> re-parse -> compare validated fields.
        # Raises ContractValidationError naming diverging fields on mismatch.
        reparsed = assert_round_trip(product)

        # Strict scalar fields are non-empty (NonEmptyStr) by contract.
        assert product.id
        assert product.handle
        assert product.title

        # Round-trip preserves the validated key fields.
        assert reparsed.id == product.id
        assert reparsed.handle == product.handle
        assert reparsed.title == product.title
