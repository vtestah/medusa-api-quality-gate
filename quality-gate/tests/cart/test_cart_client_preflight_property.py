"""Property-based checks for StoreCartClient pre-flight argument validation.

# Feature: test-coverage-expansion, Property 5: Pre-flight валидация клиента отклоняет недопустимые аргументы до HTTP
"""

from unittest.mock import MagicMock

import pytest
import requests
from hypothesis import given, settings
from hypothesis import strategies as st

from quality_gate.clients.cart import StoreCartClient
from quality_gate.config import Settings
from quality_gate.errors import ClientValidationError

pytestmark = [pytest.mark.cart]


def _make_client() -> tuple[StoreCartClient, MagicMock]:
    """Build a StoreCartClient backed by a mock session that forbids HTTP.

    A fresh mock session is created per call so Hypothesis examples never leak
    call state into one another. The session is specced against
    ``requests.Session`` so ``.get``/``.post`` are tracked as mock methods, and
    their side effects raise to prove no network call is ever made.
    """

    mock_session = MagicMock(spec=requests.Session)
    mock_session.get.side_effect = AssertionError("HTTP GET must not be called")
    mock_session.post.side_effect = AssertionError("HTTP POST must not be called")
    client = StoreCartClient(session=mock_session, settings=Settings(_env_file=None))
    return client, mock_session


# Empty string plus strings composed solely of whitespace characters.
blank_region_ids = st.text(alphabet=" \t\n\r\f\v", max_size=6)

# Integers below 1 (zero and negatives), which the client rejects pre-flight.
invalid_quantities = st.integers(max_value=0)


# Feature: test-coverage-expansion, Property 5: Pre-flight валидация клиента отклоняет недопустимые аргументы до HTTP
@settings(max_examples=100)
@given(region_id=blank_region_ids)
def test_create_cart_rejects_blank_region_id_without_http(region_id: str) -> None:
    """Blank/whitespace region_id raises ClientValidationError before any HTTP call.

    Validates: Requirements 3.3, 4.7
    """

    client, mock_session = _make_client()

    with pytest.raises(ClientValidationError):
        client.create_cart(region_id=region_id)

    mock_session.get.assert_not_called()
    mock_session.post.assert_not_called()


# Feature: test-coverage-expansion, Property 5: Pre-flight валидация клиента отклоняет недопустимые аргументы до HTTP
@settings(max_examples=100)
@given(quantity=invalid_quantities)
def test_add_line_item_rejects_non_positive_quantity_without_http(quantity: int) -> None:
    """Quantity below 1 raises ClientValidationError before any HTTP call.

    Validates: Requirements 3.3, 4.7
    """

    client, mock_session = _make_client()

    with pytest.raises(ClientValidationError):
        client.add_line_item(cart_id="cart_1", variant_id="variant_1", quantity=quantity)

    mock_session.get.assert_not_called()
    mock_session.post.assert_not_called()


# Feature: test-coverage-expansion, Property 5: Pre-flight валидация клиента отклоняет недопустимые аргументы до HTTP
@pytest.mark.parametrize("quantity", [True, False])
def test_add_line_item_rejects_bool_quantity_without_http(quantity: bool) -> None:
    """A bool quantity (an int subclass) is rejected pre-flight, with no HTTP call.

    Booleans are the tricky case: ``True`` is ``1`` and ``False`` is ``0`` at the
    int level, so they must be rejected explicitly before any request.

    Validates: Requirements 3.3, 4.7
    """

    client, mock_session = _make_client()

    with pytest.raises(ClientValidationError):
        client.add_line_item(cart_id="cart_1", variant_id="variant_1", quantity=quantity)

    mock_session.get.assert_not_called()
    mock_session.post.assert_not_called()
