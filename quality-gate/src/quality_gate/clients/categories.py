"""Client for Medusa Store product categories."""

from collections.abc import Mapping
from typing import Any

from requests import Session

from quality_gate.clients.base import StoreApiClient
from quality_gate.config import Settings
from quality_gate.models.categories import CategoriesResponse


class StoreCategoriesClient(StoreApiClient):
    """Store API client for category list and lookup flows."""

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def list_categories(
        self,
        *,
        handle: str | None = None,
        locale: str | None = None,
        fields: str | None = None,
        extra_params: Mapping[str, Any] | None = None,
    ) -> CategoriesResponse:
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

        response = self.get(
            "/store/product-categories",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return CategoriesResponse.model_validate(response.json())
