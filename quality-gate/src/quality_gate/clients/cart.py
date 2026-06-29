"""Service Object client for Medusa Store cart flows.

``StoreCartClient`` inherits :class:`StoreApiClient`, so it automatically reuses
the Publishable Key header injection and the shared transport (URL building,
timeout, status helpers). The base URL is read from :class:`Settings` through the
transport layer, never hard-coded.

High-level methods (:meth:`create_cart`, :meth:`get_cart`, :meth:`add_line_item`)
perform pre-flight argument validation before any HTTP request and return strict,
fully validated :class:`Cart` models. They raise :class:`ContractValidationError`
when the status is outside the 2xx range or the body fails Pydantic validation,
never returning a partially populated model. The low-level ``*_response`` methods
return the raw :class:`Response` for negative tests without validating the body.
"""

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError
from requests import Response, Session

from quality_gate.clients.base import StoreApiClient
from quality_gate.config import Settings
from quality_gate.errors import ClientValidationError, ContractValidationError
from quality_gate.models.cart import Cart, CartResponse


def _is_success_status(status_code: int) -> bool:
    """Return ``True`` only for HTTP status codes in the 2xx range."""
    return 200 <= status_code <= 299


class StoreCartClient(StoreApiClient):
    """Store API client for cart creation, lookup, and line-item flows."""

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def create_cart(self, *, region_id: str) -> Cart:
        """Create a cart for ``region_id`` and return the validated :class:`Cart`.

        Pre-flight: a blank or whitespace-only ``region_id`` raises
        :class:`ClientValidationError` before any HTTP request. A non-2xx status or
        a body that fails :class:`Cart` validation raises
        :class:`ContractValidationError` without returning a partial model.
        """
        if not region_id or not region_id.strip():
            raise ClientValidationError("region_id is required")

        response = self.post("/store/carts", json={"region_id": region_id})
        return self._validate_cart(response)

    def create_cart_response(
        self,
        *,
        region_id: str,
        payload: Mapping[str, Any] | None = None,
    ) -> Response:
        """Low-level cart creation for negative tests, returning the raw response.

        When ``payload`` is provided it is used as the JSON body verbatim;
        otherwise the body defaults to ``{"region_id": region_id}``. The response
        body is not validated.
        """
        body: Mapping[str, Any] = payload if payload is not None else {"region_id": region_id}
        return self.post("/store/carts", json=body)

    def get_cart(self, cart_id: str) -> Cart:
        """Fetch a cart by id and return the validated :class:`Cart`.

        A non-2xx status or a body that fails validation raises
        :class:`ContractValidationError` without returning a partial model.
        """
        response = self.get(f"/store/carts/{cart_id}")
        return self._validate_cart(response)

    def add_line_item(self, *, cart_id: str, variant_id: str, quantity: int) -> Cart:
        """Add a line item to a cart and return the validated :class:`Cart`.

        Pre-flight: a ``quantity`` below ``1`` or a non-integer ``quantity``
        (``bool`` is rejected explicitly, since it subclasses ``int``) raises
        :class:`ClientValidationError` before any HTTP request. A non-2xx status or
        a body that fails validation raises :class:`ContractValidationError`
        without returning a partial model.
        """
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ClientValidationError("quantity must be an integer")
        if quantity < 1:
            raise ClientValidationError("quantity must be >= 1")

        response = self.post(
            f"/store/carts/{cart_id}/line-items",
            json={"variant_id": variant_id, "quantity": quantity},
        )
        return self._validate_cart(response)

    def add_line_item_response(
        self,
        *,
        cart_id: str,
        variant_id: str,
        quantity: int,
    ) -> Response:
        """Low-level line-item addition for negative tests, returning the raw response.

        The response body is not validated, so callers can assert on error status
        codes and parse error bodies themselves.
        """
        return self.post(
            f"/store/carts/{cart_id}/line-items",
            json={"variant_id": variant_id, "quantity": quantity},
        )

    @staticmethod
    def _validate_cart(response: Response) -> Cart:
        """Validate a 2xx cart response into a :class:`Cart`, or raise on failure.

        Medusa returns the cart wrapped as ``{"cart": {...}}``; this parses
        :class:`CartResponse` and returns its ``cart``. Any non-2xx status or
        validation failure raises :class:`ContractValidationError` without a
        partial model.
        """
        if not _is_success_status(response.status_code):
            body_preview = response.text[:500].replace("\n", "\\n")
            raise ContractValidationError(
                f"Expected a 2xx status code, but actual is {response.status_code}. "
                f"Response body: {body_preview}"
            )
        try:
            return CartResponse.model_validate(response.json()).cart
        except (ValidationError, ValueError) as exc:
            raise ContractValidationError(
                f"Cart response failed contract validation: {exc}"
            ) from exc
