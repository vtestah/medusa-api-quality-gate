"""Store product category models."""

from pydantic import Field

from quality_gate.models.common import ApiModel, PaginatedEnvelope


class StoreProductCategory(ApiModel):
    """Minimal product category contract."""

    id: str
    handle: str | None = None
    name: str | None = None
    description: str | None = None


class CategoriesResponse(PaginatedEnvelope[StoreProductCategory]):
    """Response contract for GET /store/product-categories."""

    product_categories: list[StoreProductCategory] = Field(default_factory=list)
