"""Client for Medusa Store regions."""

from requests import Session

from quality_gate.clients.base import StoreApiClient
from quality_gate.config import Settings
from quality_gate.models.regions import RegionsResponse


class StoreRegionsClient(StoreApiClient):
    """Store API client for region endpoints."""

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def list_regions(self) -> RegionsResponse:
        response = self.get("/store/regions")
        response.raise_for_status()
        return RegionsResponse.model_validate(response.json())
