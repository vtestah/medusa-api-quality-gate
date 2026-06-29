"""Property-based checks for StoreShippingClient invalid shipping-method rejection.

# Feature: test-coverage-expansion, Property 6: Недопустимый shipping-метод отклоняется без изменения корзины
"""

from unittest.mock import MagicMock

import pytest
import requests
from hypothesis import given, settings
from hypothesis import strategies as st

from quality_gate.clients.shipping import StoreShippingClient
from quality_gate.config import Settings
from quality_gate.errors import ShippingOptionError
from quality_gate.models.cart import ShippingOption

pytestmark = [pytest.mark.cart]


def _make_client() -> tuple[StoreShippingClient, MagicMock]:
    """Build a StoreShippingClient backed by a mock session that forbids HTTP.

    A fresh mock session is created per call so Hypothesis examples never leak
    call state into one another. The session is specced against
    ``requests.Session`` so ``.get``/``.post`` are tracked as mock methods, and
    their side effects raise to prove no network call is ever made when an invalid
    shipping method is rejected pre-flight.
    """

    mock_session = MagicMock(spec=requests.Session)
    mock_session.get.side_effect = AssertionError("HTTP GET must not be called")
    mock_session.post.side_effect = AssertionError("HTTP POST must not be called")
    client = StoreShippingClient(session=mock_session, settings=Settings(_env_file=None))
    return client, mock_session


# Option ids use letters only; the candidate option_id uses digits only. Two
# non-empty strings drawn from these disjoint alphabets can never be equal, which
# guarantees the generated ``option_id`` is absent from ``available_options``
# without relying on Hypothesis filtering.
_option_ids = st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8)
_option_names = st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=12)
_absent_option_ids = st.text(alphabet="0123456789", min_size=1, max_size=8)


@st.composite
def _shipping_options(draw: st.DrawFn) -> list[ShippingOption]:
    """Generate a list (possibly empty) of valid ShippingOption with letter ids."""

    ids = draw(st.lists(_option_ids, min_size=0, max_size=5, unique=True))
    return [
        ShippingOption(id=opt_id, name=draw(_option_names), amount=draw(st.none() | st.integers()))
        for opt_id in ids
    ]


# Feature: test-coverage-expansion, Property 6: Недопустимый shipping-метод отклоняется без изменения корзины
@settings(max_examples=100)
@given(available_options=_shipping_options(), option_id=_absent_option_ids)
def test_select_shipping_method_rejects_absent_option_without_http(
    available_options: list[ShippingOption], option_id: str
) -> None:
    """An option_id absent from available_options raises before any HTTP call.

    The candidate ``option_id`` is drawn from a digit-only alphabet while the
    available option ids are letter-only, so the candidate is guaranteed absent.
    The call must raise ``ShippingOptionError`` and never touch the network, which
    leaves the cart (and its previously selected method) unchanged.

    Validates: Requirements 5.7
    """

    client, mock_session = _make_client()

    with pytest.raises(ShippingOptionError):
        client.select_shipping_method(
            cart_id="cart_1",
            option_id=option_id,
            available_options=available_options,
        )

    mock_session.get.assert_not_called()
    mock_session.post.assert_not_called()
