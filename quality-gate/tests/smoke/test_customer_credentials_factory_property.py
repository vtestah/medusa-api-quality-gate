"""Property-based checks for the customer test-data factory."""

from string import ascii_lowercase, ascii_uppercase, digits

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quality_gate.test_data import (
    CustomerCredentials,
    build_customer_credentials,
)

_PASSWORD_SYMBOLS = "!@#$%&*?"

# Любая строка допустима как prefix: фабрика нормализует её до email-safe
# значения (с fallback на "qa-customer"), поэтому не сужаем входное пространство.
_prefix_strategy = st.text(max_size=40)

# Валидный domain по контракту фабрики: содержит точку, не содержит "@",
# не пустой после strip(). Собираем из меток lowercase-букв, соединённых точкой.
_domain_label = st.text(alphabet=ascii_lowercase, min_size=1, max_size=12)
_domain_strategy = st.builds(
    lambda labels, tld: ".".join((*labels, tld)),
    labels=st.lists(_domain_label, min_size=1, max_size=3),
    tld=st.text(alphabet=ascii_lowercase, min_size=2, max_size=4),
)

# password_length >= 12 по контракту фабрики; верхняя граница держит тест быстрым.
_password_length_strategy = st.integers(min_value=12, max_value=128)


@pytest.mark.smoke
@pytest.mark.bootstrap
@settings(max_examples=100)
@given(
    prefix=_prefix_strategy,
    domain=_domain_strategy,
    password_length=_password_length_strategy,
)
def test_factory_produces_valid_credentials(
    prefix: str,
    domain: str,
    password_length: int,
) -> None:
    """Для валидных параметров фабрика всегда возвращает валидные credentials."""

    credentials = build_customer_credentials(
        prefix=prefix,
        domain=domain,
        password_length=password_length,
    )

    # Возвращается провалидированная Pydantic-модель.
    assert isinstance(credentials, CustomerCredentials)

    # Email имеет форму local-part@domain с точкой в домене.
    local_part, separator, email_domain = credentials.email.partition("@")
    assert separator == "@"
    assert local_part
    assert "." in email_domain
    assert email_domain == domain.strip().lower()

    # Пароль строго заданной длины с обязательными классами символов.
    password = credentials.password
    assert len(password) == password_length
    assert any(char in ascii_lowercase for char in password)
    assert any(char in ascii_uppercase for char in password)
    assert any(char in digits for char in password)
    assert any(char in _PASSWORD_SYMBOLS for char in password)


@pytest.mark.smoke
@pytest.mark.bootstrap
@settings(max_examples=100)
@given(
    prefix=_prefix_strategy,
    domain=_domain_strategy,
    password_length=_password_length_strategy,
)
def test_factory_emails_are_unique_across_consecutive_calls(
    prefix: str,
    domain: str,
    password_length: int,
) -> None:
    """Два последовательных вызова дают различные email (изоляция данных)."""

    first = build_customer_credentials(
        prefix=prefix,
        domain=domain,
        password_length=password_length,
    )
    second = build_customer_credentials(
        prefix=prefix,
        domain=domain,
        password_length=password_length,
    )

    assert first.email != second.email
