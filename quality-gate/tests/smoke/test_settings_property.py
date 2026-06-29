"""Property-based checks for fail-fast Settings construction.

# Feature: test-coverage-expansion, Property 7: Settings падает на этапе конфигурации при недопустимых значениях
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from quality_gate.config import Settings

pytestmark = [pytest.mark.smoke, pytest.mark.bootstrap]


# Required QUALITY_GATE_* string fields that reject blank/whitespace values
# during Settings construction (field names; populate_by_name=True is enabled).
BLANK_REJECTING_FIELDS = (
    "medusa_base_url",
    "publishable_key",
    "db_url",
    "default_locale",
    "default_region_code",
    "demo_product_handle",
    "demo_category_handle",
    "ru_currency_code",
    "us_currency_code",
)

# Empty string plus strings composed solely of whitespace characters.
blank_values = st.text(alphabet=" \t\n\r\f\v", max_size=6)

# Non-blank strings that do not carry an http(s):// scheme.
urls_without_scheme = (
    st.text(min_size=1, max_size=40)
    .map(lambda value: value.strip())
    .filter(lambda value: value != "" and not value.startswith(("http://", "https://")))
)


# Feature: test-coverage-expansion, Property 7: Settings падает на этапе конфигурации при недопустимых значениях
@settings(max_examples=100)
@given(field_name=st.sampled_from(BLANK_REJECTING_FIELDS), blank_value=blank_values)
def test_settings_rejects_blank_required_values(field_name: str, blank_value: str) -> None:
    """Any required QUALITY_GATE_* value that is blank/whitespace must fail at construction.

    Validation happens while constructing ``Settings`` (before any HTTP request),
    so ``pydantic.ValidationError`` is raised eagerly.
    """

    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{field_name: blank_value})


# Feature: test-coverage-expansion, Property 7: Settings падает на этапе конфигурации при недопустимых значениях
@settings(max_examples=100)
@given(base_url=urls_without_scheme)
def test_settings_rejects_base_url_without_http_scheme(base_url: str) -> None:
    """Any Medusa base URL without an http(s):// scheme must fail at construction."""

    with pytest.raises(ValidationError):
        Settings(_env_file=None, medusa_base_url=base_url)
