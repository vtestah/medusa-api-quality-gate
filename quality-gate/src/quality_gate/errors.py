"""Domain exceptions for the Medusa quality gate framework.

These exceptions give the Service Object clients and contract helpers a small,
distinguishable hierarchy so callers can react to a specific failure mode
(pre-flight argument validation, contract/round-trip mismatch, shipping option
problems) without inspecting message strings.
"""


class QualityGateError(Exception):
    """Base exception for every error raised by the quality gate framework."""


class ClientValidationError(QualityGateError):
    """Pre-flight validation error for client arguments, raised before any HTTP call.

    Raised when a Service Object client detects an invalid argument (for example a
    blank ``region_id`` or a ``quantity`` below ``1``) and rejects the call without
    sending a request, leaving any remote state unchanged.
    """


class ContractValidationError(QualityGateError):
    """Response failed contract or round-trip validation.

    Raised when a Store API response cannot be parsed into its strict Pydantic
    contract model, when the status code is outside the 2xx range on a happy path,
    or when a round-trip check finds diverging fields. No partially populated model
    is returned to the caller.
    """


class ShippingOptionError(QualityGateError):
    """Shipping options are unavailable or an invalid shipping method was selected.

    Raised when shipping options cannot be retrieved (timeout or transport failure)
    or when a requested ``option_id`` is not part of the options available for the
    cart's market. In both cases the cart is left unchanged.
    """
