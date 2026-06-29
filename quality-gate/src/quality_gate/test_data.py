"""Factories for isolated test data used by API checks."""

from random import SystemRandom
from secrets import choice
from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL_PREFIX_CHARS = ascii_lowercase + digits + "._-"
_PASSWORD_SYMBOLS = "!@#$%&*?"
_PASSWORD_ALPHABET = ascii_letters + digits + _PASSWORD_SYMBOLS
_RANDOM = SystemRandom()


class CustomerCredentials(BaseModel):
    """Email/password pair ready for a Medusa customer registration payload."""

    email: str = Field(min_length=6)
    password: str = Field(min_length=12)

    model_config = ConfigDict(frozen=True)

    @field_validator("email")
    @classmethod
    def validate_email_shape(cls, value: str) -> str:
        """Keep generated emails shaped like local-part@domain."""

        local_part, separator, domain = value.partition("@")
        if not separator or not local_part or "." not in domain:
            raise ValueError("email must look like local-part@example.test")
        return value


def build_customer_credentials(
    *,
    prefix: str = "qa-customer",
    domain: str = "example.test",
    password_length: int = 20,
) -> CustomerCredentials:
    """Build unique customer credentials for Store API registration scenarios."""

    if password_length < 12:
        raise ValueError("password_length must be at least 12")

    email_prefix = _normalize_email_prefix(prefix)
    email_domain = _normalize_domain(domain)
    unique_suffix = uuid4().hex[:12]
    email = f"{email_prefix}_{unique_suffix}@{email_domain}"

    return CustomerCredentials(
        email=email,
        password=_build_password(length=password_length),
    )


def _normalize_email_prefix(prefix: str) -> str:
    normalized = "".join(
        char if char in _EMAIL_PREFIX_CHARS else "-"
        for char in prefix.strip().lower()
    ).strip(".-_")

    return normalized or "qa-customer"


def _normalize_domain(domain: str) -> str:
    normalized = domain.strip().lower()
    if "@" in normalized or "." not in normalized:
        raise ValueError("domain must look like example.test")
    return normalized


def _build_password(*, length: int) -> str:
    required_chars = [
        choice(ascii_lowercase),
        choice(ascii_uppercase),
        choice(digits),
        choice(_PASSWORD_SYMBOLS),
    ]
    password_chars = required_chars + [
        choice(_PASSWORD_ALPHABET) for _ in range(length - len(required_chars))
    ]
    _RANDOM.shuffle(password_chars)
    return "".join(password_chars)


__all__ = ["CustomerCredentials", "build_customer_credentials"]
