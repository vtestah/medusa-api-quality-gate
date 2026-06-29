"""Store region models."""

from pydantic import Field

from quality_gate.models.common import ApiModel, NonEmptyStr, PaginatedEnvelope
from quality_gate.models.contract import CurrencyCode


class StoreCountry(ApiModel):
    """Minimal country representation attached to a region."""

    iso_2: str | None = None
    display_name: str | None = None
    name: str | None = None


class StoreRegion(ApiModel):
    """Minimal region contract used by the Python smoke suite."""

    id: NonEmptyStr
    name: NonEmptyStr
    currency_code: CurrencyCode
    countries: list[StoreCountry] = Field(default_factory=list)


class RegionsResponse(PaginatedEnvelope[StoreRegion]):
    """Response contract for GET /store/regions."""

    regions: list[StoreRegion] = Field(default_factory=list)
