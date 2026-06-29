"""Shipping and regional-pricing integration tests for the RU and US markets.

These run against the live Medusa runtime and are guarded by ``runtime_ready`` so
they skip cleanly when the runtime is unavailable. They are parametrized over
``settings.markets`` (Req 5.8): for each market they create a cart in the matching
region, assert the cart's ``currency_code`` matches the configured market currency
(Req 5.3 ru -> rub, Req 5.4 us -> usd), assert the available shipping option names
exactly equal the configured shipping-method set (Req 5.1 RU set, Req 5.2 US set),
and select one available method, confirming it is recorded on the returned cart
(Req 5.5). All assertions use Pydantic models, never raw dict keys (Req 7.1).
"""

import pytest

from quality_gate.clients import StoreCartClient, StoreRegionsClient, StoreShippingClient
from quality_gate.config import Settings


def _resolve_region_id(
    store_regions_client: StoreRegionsClient,
    settings: Settings,
    market_code: str,
) -> str:
    """Resolve a Medusa region id for a market by matching its currency code.

    Looks up the expected currency for ``market_code`` from ``settings.markets``
    and returns the id of the first region whose ``currency_code`` matches. Skips
    the test (rather than failing) when no matching region is seeded.
    """

    expected_currency = settings.markets[market_code].currency_code
    regions = store_regions_client.list_regions().regions
    for region in regions:
        if region.currency_code == expected_currency:
            return region.id
    pytest.skip(
        f"No region found for market {market_code!r} "
        f"(currency {expected_currency!r}) in the live runtime"
    )


@pytest.mark.cart
@pytest.mark.parametrize("market_code", ["ru", "us"])
def test_cart_currency_matches_market(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    store_regions_client: StoreRegionsClient,
    settings: Settings,
    market_code: str,
) -> None:
    """A cart created for a market carries that market's currency code.

    Resolves the region for ``market_code`` by currency, creates a cart, and
    asserts ``cart.currency_code`` equals the configured market currency
    (Req 5.3 ru -> rub, Req 5.4 us -> usd). The strict ``Cart.currency_code``
    literal also guarantees the value is exactly lowercase ``rub``/``usd``.
    """

    market = settings.markets[market_code]
    region_id = _resolve_region_id(store_regions_client, settings, market_code)

    cart = store_cart_client.create_cart(region_id=region_id)

    assert cart.currency_code == market.currency_code


@pytest.mark.cart
@pytest.mark.parametrize("market_code", ["ru", "us"])
def test_shipping_options_match_market_methods(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    store_shipping_client: StoreShippingClient,
    store_regions_client: StoreRegionsClient,
    settings: Settings,
    market_code: str,
) -> None:
    """Available shipping option names equal the market's configured method set.

    For RU the set is exactly {Курьер, ПВЗ, Самовывоз} (Req 5.1); for US it is
    exactly {Standard Shipping, Express Shipping} (Req 5.2). The expected set is
    read from ``settings.markets`` rather than hard-coded (Req 5.8).
    """

    market = settings.markets[market_code]
    region_id = _resolve_region_id(store_regions_client, settings, market_code)

    cart = store_cart_client.create_cart(region_id=region_id)
    options_response = store_shipping_client.list_shipping_options(cart_id=cart.id)

    option_names = {option.name for option in options_response.shipping_options}

    assert option_names == set(market.shipping_methods)


@pytest.mark.cart
@pytest.mark.parametrize("market_code", ["ru", "us"])
def test_selected_shipping_method_recorded_on_cart(
    runtime_ready: None,
    store_cart_client: StoreCartClient,
    store_shipping_client: StoreShippingClient,
    store_regions_client: StoreRegionsClient,
    settings: Settings,
    market_code: str,
) -> None:
    """Selecting an available shipping method records it on the returned cart.

    Lists the options for the market's cart, selects the first available option
    (passing ``available_options`` so the pre-flight check is satisfied), and
    asserts the returned cart records the selected method, matching the chosen
    option id (Req 5.5).
    """

    region_id = _resolve_region_id(store_regions_client, settings, market_code)

    cart = store_cart_client.create_cart(region_id=region_id)
    options_response = store_shipping_client.list_shipping_options(cart_id=cart.id)
    options = options_response.shipping_options

    assert options, f"expected shipping options for market {market_code!r}"

    selected = options[0]
    updated_cart = store_shipping_client.select_shipping_method(
        cart_id=cart.id,
        option_id=selected.id,
        available_options=options,
    )

    assert updated_cart.shipping_methods, "expected a recorded shipping method"
    recorded_option_ids = {
        method.shipping_option_id for method in updated_cart.shipping_methods
    }
    assert selected.id in recorded_option_ids
