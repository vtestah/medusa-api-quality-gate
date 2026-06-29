"""Smoke checks for customer test-data factories."""

from string import ascii_lowercase, ascii_uppercase, digits

import pytest

from quality_gate.test_data import build_customer_credentials


@pytest.mark.smoke
@pytest.mark.bootstrap
def test_customer_credentials_are_unique_and_payload_ready() -> None:
    """Generated credentials should be unique and ready for JSON payloads."""

    first = build_customer_credentials(prefix="TCID29")
    second = build_customer_credentials(prefix="TCID29")

    assert first.email != second.email
    assert first.email.startswith("tcid29_")
    assert first.email.endswith("@example.test")
    assert len(first.password) == 20

    payload = first.model_dump()

    assert payload == {"email": first.email, "password": first.password}
    assert any(char in ascii_lowercase for char in first.password)
    assert any(char in ascii_uppercase for char in first.password)
    assert any(char in digits for char in first.password)
    assert any(char in "!@#$%&*?" for char in first.password)


@pytest.mark.smoke
@pytest.mark.bootstrap
def test_customer_credentials_reject_short_password_length() -> None:
    """Generated passwords should keep a useful minimum length."""

    with pytest.raises(ValueError, match="at least 12"):
        build_customer_credentials(password_length=8)
