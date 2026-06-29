"""Smoke checks for environment-driven framework settings."""

import pytest
from pydantic import ValidationError

from quality_gate.config import Settings

pytestmark = [pytest.mark.smoke, pytest.mark.bootstrap]


QUALITY_GATE_ENV_VARS = (
    "QUALITY_GATE_MEDUSA_BASE_URL",
    "QUALITY_GATE_PUBLISHABLE_KEY",
    "QUALITY_GATE_DB_URL",
    "QUALITY_GATE_DEFAULT_LOCALE",
    "QUALITY_GATE_DEFAULT_REGION_CODE",
    "QUALITY_GATE_DEMO_PRODUCT_HANDLE",
    "QUALITY_GATE_DEMO_CATEGORY_HANDLE",
    "QUALITY_GATE_REQUEST_TIMEOUT_SECONDS",
)


def test_settings_defaults_are_local_docker_friendly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Defaults should work for a fresh local checkout without exported env vars."""

    for env_var in QUALITY_GATE_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)

    settings = Settings(_env_file=None)

    assert settings.medusa_base_url == "http://localhost:9000"
    assert settings.db_url == "postgresql://postgres:postgres@localhost:5433/medusa"
    assert settings.default_locale == "ru-RU"
    assert settings.request_timeout_seconds == 10.0


def test_settings_read_quality_gate_environment_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """QUALITY_GATE_* variables should override defaults for runtime-specific runs."""

    monkeypatch.setenv("QUALITY_GATE_MEDUSA_BASE_URL", "http://medusa.local:9000")
    monkeypatch.setenv("QUALITY_GATE_PUBLISHABLE_KEY", "pk_test_lesson_31")
    monkeypatch.setenv("QUALITY_GATE_DEFAULT_LOCALE", "en-US")
    monkeypatch.setenv("QUALITY_GATE_REQUEST_TIMEOUT_SECONDS", "3.5")

    settings = Settings(_env_file=None)

    assert settings.medusa_base_url == "http://medusa.local:9000"
    assert settings.default_locale == "en-US"
    assert settings.request_timeout_seconds == 3.5
    assert settings.store_headers == {"x-publishable-api-key": "pk_test_lesson_31"}


def test_settings_reject_blank_publishable_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A blank Store API key should fail during settings construction."""

    monkeypatch.setenv("QUALITY_GATE_PUBLISHABLE_KEY", "")

    with pytest.raises(ValidationError, match="runtime setting must not be blank"):
        Settings(_env_file=None)


def test_settings_reject_base_url_without_http_scheme(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch the classic requests error before it becomes "No schema supplied"."""

    monkeypatch.setenv("QUALITY_GATE_MEDUSA_BASE_URL", "customers")

    with pytest.raises(ValidationError, match="start with http:// or https://"):
        Settings(_env_file=None)
