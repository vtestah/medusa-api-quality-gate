"""Runtime configuration for the Medusa quality gate."""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MarketProfile(BaseModel):
    """Expected currency and shipping methods for a single Medusa market."""

    region_code: str = Field(min_length=1)
    currency_code: str = Field(min_length=1)
    shipping_methods: frozenset[str] = Field(min_length=1)

    model_config = ConfigDict(frozen=True)

    @field_validator("region_code", "currency_code")
    @classmethod
    def _reject_blank_codes(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("market code must not be blank")
        return normalized_value

    @field_validator("shipping_methods")
    @classmethod
    def _reject_blank_shipping_methods(cls, value: frozenset[str]) -> frozenset[str]:
        normalized_methods = frozenset(method.strip() for method in value)
        if not value or any(not method for method in normalized_methods):
            raise ValueError("shipping methods must be non-empty and non-blank")
        return normalized_methods


class Settings(BaseSettings):
    """Centralized env-based settings for the Python QA framework."""

    medusa_base_url: str = Field(
        default="http://localhost:9000",
        alias="QUALITY_GATE_MEDUSA_BASE_URL",
    )
    publishable_key: str = Field(
        default="pk_test",
        alias="QUALITY_GATE_PUBLISHABLE_KEY",
    )
    db_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5433/medusa",
        alias="QUALITY_GATE_DB_URL",
    )
    default_locale: str = Field(
        default="ru-RU",
        alias="QUALITY_GATE_DEFAULT_LOCALE",
    )
    default_region_code: str = Field(
        default="ru",
        alias="QUALITY_GATE_DEFAULT_REGION_CODE",
    )
    demo_product_handle: str = Field(
        default="basis-heavy-tee",
        alias="QUALITY_GATE_DEMO_PRODUCT_HANDLE",
    )
    demo_category_handle: str = Field(
        default="hoodies",
        alias="QUALITY_GATE_DEMO_CATEGORY_HANDLE",
    )
    request_timeout_seconds: float = Field(
        default=10.0,
        alias="QUALITY_GATE_REQUEST_TIMEOUT_SECONDS",
        gt=0,
    )
    ru_currency_code: str = Field(
        default="rub",
        alias="QUALITY_GATE_RU_CURRENCY_CODE",
    )
    ru_shipping_methods: frozenset[str] = Field(
        default=frozenset({"Курьер", "ПВЗ", "Самовывоз"}),
        alias="QUALITY_GATE_RU_SHIPPING_METHODS",
    )
    us_currency_code: str = Field(
        default="usd",
        alias="QUALITY_GATE_US_CURRENCY_CODE",
    )
    us_shipping_methods: frozenset[str] = Field(
        default=frozenset({"Standard Shipping", "Express Shipping"}),
        alias="QUALITY_GATE_US_SHIPPING_METHODS",
    )

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator(
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
    @classmethod
    def _reject_blank_env_values(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("runtime setting must not be blank")
        return normalized_value

    @field_validator("medusa_base_url")
    @classmethod
    def _require_http_base_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("Medusa base URL must start with http:// or https://")
        return value

    @property
    def store_headers(self) -> dict[str, str]:
        """Headers required for Medusa Store API requests."""

        return {"x-publishable-api-key": self.publishable_key}

    @property
    def markets(self) -> dict[str, MarketProfile]:
        """Market profiles keyed by region code (currency + shipping methods)."""

        return {
            "ru": MarketProfile(
                region_code="ru",
                currency_code=self.ru_currency_code,
                shipping_methods=self.ru_shipping_methods,
            ),
            "us": MarketProfile(
                region_code="us",
                currency_code=self.us_currency_code,
                shipping_methods=self.us_shipping_methods,
            ),
        }
