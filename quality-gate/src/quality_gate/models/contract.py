"""Contract helpers: strict currency alias and round-trip validation.

This module centralises the reusable contract primitives shared by the strict
Store API models. ``CurrencyCode`` constrains a currency field to the exact
lowercase literals the markets support, while :func:`assert_round_trip`
implements the Round_Trip_Check (serialize -> re-parse -> compare fields) and
surfaces diverging fields through :class:`ContractValidationError`.
"""

from typing import Literal, TypeVar

from pydantic import BaseModel

from quality_gate.errors import ContractValidationError

CurrencyCode = Literal["rub", "usd"]
"""Strict currency alias: accepts exactly the lowercase literals ``rub`` or ``usd``."""

ModelT = TypeVar("ModelT", bound=BaseModel)


def _diverging_fields(left: dict[str, object], right: dict[str, object]) -> list[str]:
    """Return the sorted list of field names whose values differ between two dumps."""
    field_names = set(left) | set(right)
    return sorted(name for name in field_names if left.get(name) != right.get(name))


def assert_round_trip(model: ModelT) -> ModelT:
    """Round_Trip_Check: serialize the model, re-parse it, and compare fields.

    The model is dumped to Python objects, validated again through the same model
    type, and the two dumps are compared. When every validated field matches, the
    re-parsed model is returned. When any field diverges, a
    :class:`ContractValidationError` is raised naming the diverging fields, so the
    failure is loud and never silently swallowed.

    Args:
        model: A validated Pydantic model instance to round-trip.

    Returns:
        The re-parsed model instance, equal field-for-field to ``model``.

    Raises:
        ContractValidationError: If the re-parsed model diverges from the original,
            listing the names of the diverging fields.
    """
    original_dump = model.model_dump()
    reparsed = type(model).model_validate(model.model_dump(mode="python"))
    reparsed_dump = reparsed.model_dump()
    if reparsed_dump != original_dump:
        diverging = _diverging_fields(original_dump, reparsed_dump)
        raise ContractValidationError(
            f"Round-trip mismatch for {type(model).__name__}: "
            f"diverging fields {diverging}"
        )
    return reparsed
