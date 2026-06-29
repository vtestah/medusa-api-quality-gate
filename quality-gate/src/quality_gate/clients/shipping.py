"""Service Object client for Medusa Store shipping flows.

``StoreShippingClient`` inherits :class:`StoreApiClient`, so it automatically
reuses the Publishable Key header injection and the shared transport (URL
building, timeout, status helpers). The base URL is read from :class:`Settings`
through the transport layer, never hard-coded.

:meth:`list_shipping_options` retrieves the shipping options available for a cart
and raises :class:`ShippingOptionError` on a transport failure/timeout or a
non-2xx/invalid body, leaving the cart unchanged. :meth:`select_shipping_method`
performs a pre-flight check that the requested ``option_id`` is part of the
``available_options`` before any HTTP request, then applies the method and returns
the fully validated :class:`Cart` with the recorded shipping method.
"""

from collections.abc import Sequence

from pydantic import ValidationError
from requests import RequestException, Response, Session

from quality_gate.clients.base import StoreApiClient
from quality_gate.config import Settings
from quality_gate.errors import ContractValidationError, ShippingOptionError
from quality_gate.models.cart import (
    Cart,
    CartResponse,
    ShippingOption,
    ShippingOptionsResponse,
)


def _is_success_status(status_code: int) -> bool:
    """Return ``True`` only for HTTP status codes in the 2xx range."""
    return 200 <= status_code <= 299


class StoreShippingClient(StoreApiClient):
    """Store API client for listing shipping options and selecting a method."""

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def list_shipping_options(self, *, cart_id: str) -> ShippingOptionsResponse:
        """List shipping options for ``cart_id`` and return the validated response.

        Issues ``GET /store/shipping-options?cart_id={cart_id}``. A transport
        failure or timeout raises :class:`ShippingOptionError` ("shipping options
        unavailable"); this method does not mutate the cart, so the cart is left
        unchanged. A non-2xx status or a body that fails
        :class:`ShippingOptionsResponse` validation also raises
        :class:`ShippingOptionError`.
        """
        try:
            response = self.get(
                "/store/shipping-options",
                params={"cart_id": cart_id},
            )
        except RequestException as exc:
            raise ShippingOptionError(
                f"shipping options unavailable for cart {cart_id}: {exc}"
            ) from exc

        if not _is_success_status(response.status_code):
            body_preview = response.text[:500].replace("\n", "\\n")
            raise ShippingOptionError(
                "shipping options unavailable: expected a 2xx status code, but "
                f"actual is {response.status_code}. Response body: {body_preview}"
            )
        try:
            return ShippingOptionsResponse.model_validate(response.json())
        except (ValidationError, ValueError) as exc:
            raise ShippingOptionError(
                f"shipping options unavailable: response failed validation: {exc}"
            ) from exc

    def select_shipping_method(
        self,
        *,
        cart_id: str,
        option_id: str,
        available_options: Sequence[ShippingOption],
    ) -> Cart:
        """Apply ``option_id`` to a cart and return the validated :class:`Cart`.

        Pre-flight: when ``option_id`` is not among the ids of
        ``available_options``, raises :class:`ShippingOptionError` ("invalid
        shipping method") before any HTTP request, leaving the previously selected
        method unchanged. Otherwise issues
        ``POST /store/carts/{cart_id}/shipping-methods`` with the ``option_id`` body
        and returns the recorded :class:`Cart`. A non-2xx status or a body that
        fails validation raises :class:`ContractValidationError` without returning a
        partial model.
        """
        available_ids = {option.id for option in available_options}
        if option_id not in available_ids:
            raise ShippingOptionError(
                f"invalid shipping method {option_id!r}: not in available options"
            )

        response = self.post(
            f"/store/carts/{cart_id}/shipping-methods",
            json={"option_id": option_id},
        )
        return self._validate_cart(response)

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
