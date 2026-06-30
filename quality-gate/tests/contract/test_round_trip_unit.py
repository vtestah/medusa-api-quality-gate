"""Focused unit tests hardening the contract round-trip helper.

These complement the property-based round-trip tests by exercising the
divergence helper and the error path directly. They were added to close gaps
surfaced by mutation testing (mutmut): the union-vs-intersection logic in
``_diverging_fields`` and the ``ContractValidationError`` branch in
``assert_round_trip`` were never exercised by the happy-path property tests, so
mutants planted there survived.
"""

import pytest
from pydantic import BaseModel, field_validator

from quality_gate.errors import ContractValidationError
from quality_gate.models.contract import _diverging_fields, assert_round_trip

pytestmark = pytest.mark.contract


def test_diverging_fields_includes_keys_present_on_one_side() -> None:
    """A field present on only one side is reported (set union, not intersection)."""
    assert _diverging_fields({"a": 1, "b": 2}, {"a": 1}) == ["b"]
    assert _diverging_fields({"a": 1}, {"a": 1, "b": 2}) == ["b"]


def test_diverging_fields_reports_differing_shared_values() -> None:
    """Shared keys with differing values are reported; identical dumps report none."""
    assert _diverging_fields({"a": 1, "b": 2}, {"a": 1, "b": 99}) == ["b"]
    assert _diverging_fields({"a": 1, "b": 2}, {"a": 1, "b": 2}) == []


class _NonIdempotentModel(BaseModel):
    """Test-only model whose validator mutates the value on every validation.

    Because validation is not idempotent, re-parsing always diverges from the
    original dump, which deterministically exercises the error path.
    """

    name: str

    @field_validator("name")
    @classmethod
    def _append_marker(cls, value: str) -> str:
        return f"{value}!"


def test_assert_round_trip_raises_and_names_the_diverging_field() -> None:
    """When re-parsing diverges, ContractValidationError names the model and field."""
    model = _NonIdempotentModel(name="a")  # validated once to "a!"

    with pytest.raises(ContractValidationError) as excinfo:
        assert_round_trip(model)

    message = str(excinfo.value)
    assert "_NonIdempotentModel" in message
    assert "name" in message  # kills the `diverging = None` mutant


def test_assert_round_trip_returns_a_reparsed_equal_model() -> None:
    """A clean round-trip returns a distinct but field-equal re-parsed instance."""

    class _StableModel(BaseModel):
        value: int

    original = _StableModel(value=7)
    reparsed = assert_round_trip(original)

    assert reparsed is not original
    assert reparsed.model_dump() == original.model_dump()
