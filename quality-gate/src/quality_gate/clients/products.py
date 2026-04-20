"""Client for Medusa Store products."""

from collections.abc import Mapping
from typing import Any

from requests import Session

from quality_gate.clients.base import StoreApiClient
from quality_gate.config import Settings
from quality_gate.models.products import ProductsResponse


class StoreProductsClient(StoreApiClient):
    """Store API client for product list and lookup flows."""

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def list_products(
        self,
        *,
        handle: str | None = None,
        locale: str | None = None,
        fields: str | None = None,
        extra_params: Mapping[str, Any] | None = None,
    ) -> ProductsResponse:
        params: dict[str, Any] = {}
        if handle:
            params["handle"] = handle
        if fields:
            params["fields"] = fields
        if extra_params:
            params.update(extra_params)

        headers: dict[str, str] = {}
        if locale:
            headers["x-medusa-locale"] = locale

        response = self.get("/store/products", params=params, headers=headers)
        response.raise_for_status()
        return ProductsResponse.model_validate(response.json())
