"""Store product models."""

from pydantic import Field

from quality_gate.models.common import ApiModel, PaginatedEnvelope


class StoreProductVariant(ApiModel):
    """Minimal product variant contract."""

    id: str
    title: str | None = None
    sku: str | None = None
    inventory_quantity: int | None = None


class StoreProduct(ApiModel):
    """Minimal product contract for smoke and localization checks."""

    id: str
    handle: str
    title: str | None = None
    description: str | None = None
    subtitle: str | None = None
    material: str | None = None
    variants: list[StoreProductVariant] = Field(default_factory=list)


class ProductsResponse(PaginatedEnvelope[StoreProduct]):
    """Response contract for GET /store/products."""

    products: list[StoreProduct] = Field(default_factory=list)
