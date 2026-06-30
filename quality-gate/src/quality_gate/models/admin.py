"""Admin API response models."""

from pydantic import Field

from quality_gate.models.common import ApiModel, NonEmptyStr, PaginatedEnvelope


class AdminProduct(ApiModel):
    """Minimal Admin API product contract (extra fields are ignored)."""

    id: NonEmptyStr
    title: NonEmptyStr


class AdminProductsResponse(PaginatedEnvelope[AdminProduct]):
    """Response contract for GET /admin/products."""

    products: list[AdminProduct] = Field(default_factory=list)
