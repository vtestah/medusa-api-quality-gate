"""Property-based checks for the strict CurrencyCode contract alias.

# Feature: test-coverage-expansion, Property 3: currency_code принимается только для rub или usd
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import TypeAdapter, ValidationError

from quality_gate.models.contract import CurrencyCode

pytestmark = pytest.mark.contract

# Focused, pure validator for the CurrencyCode literal alias. Validating through a
# TypeAdapter keeps the property test independent of any surrounding model.
_currency_adapter: TypeAdapter[str] = TypeAdapter(CurrencyCode)

# The only two values the alias accepts (exact lowercase literals).
ACCEPTED_CODES = ("rub", "usd")


# Feature: test-coverage-expansion, Property 3: currency_code принимается только для rub или usd
@settings(max_examples=100)
@given(value=st.text())
def test_currency_code_accepts_iff_rub_or_usd(value: str) -> None:
    """Validation succeeds if and only if the string is exactly "rub" or "usd".

    Validates: Requirements 1.5, 5.3, 5.4
    """

    if value in ACCEPTED_CODES:
        assert _currency_adapter.validate_python(value) == value
    else:
        with pytest.raises(ValidationError):
            _currency_adapter.validate_python(value)


# Feature: test-coverage-expansion, Property 3: currency_code принимается только для rub или usd
@pytest.mark.parametrize("code", ["rub", "usd"])
def test_currency_code_accepts_supported_codes(code: str) -> None:
    """The supported lowercase literals are accepted unchanged.

    Validates: Requirements 1.5, 5.3, 5.4
    """

    assert _currency_adapter.validate_python(code) == code


# Feature: test-coverage-expansion, Property 3: currency_code принимается только для rub или usd
@pytest.mark.parametrize("code", ["RUB", "Rub", "USD", "eur", "", " rub", "rub "])
def test_currency_code_rejects_wrong_case_and_other_values(code: str) -> None:
    """Wrong case, other currencies, and blank values are rejected.

    Validates: Requirements 1.5, 5.3, 5.4
    """

    with pytest.raises(ValidationError):
        _currency_adapter.validate_python(code)
