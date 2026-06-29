"""Store customer response models."""

from typing import Any

from pydantic import Field

from quality_gate.models.common import ApiModel


class StoreCustomer(ApiModel):
    """Minimal Store API customer contract for registration checks."""

    id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None
    phone: str | None = None
    addresses: list[dict[str, Any]] = Field(default_factory=list)


class StoreCustomerResponse(ApiModel):
    """Response contract for POST /store/customers."""

    customer: StoreCustomer
